"""HwpxDocument - Main API for creating and manipulating HWPX documents."""
from .constants import (
    CHARPR_BODY, CHARPR_BOLD, CHARPR_ITALIC, CHARPR_BOLD_ITALIC,
    CHARPR_H1, CHARPR_H2, CHARPR_H3, CHARPR_H4, CHARPR_H5, CHARPR_H6,
    CHARPR_INLINE_CODE, CHARPR_CODE_BLOCK,
    CHARPR_TABLE_HEADER, CHARPR_TABLE_BODY,
    PARAPR_BODY, PARAPR_H1, PARAPR_H2, PARAPR_H3,
    PARAPR_H4, PARAPR_H5, PARAPR_H6,
    PARAPR_CODE, PARAPR_BULLET, PARAPR_TABLE,
    BORDERFILL_TABLE, BORDERFILL_TABLE_HEADER,
    PAGE_WIDTH, MARGIN_LEFT, MARGIN_RIGHT,
)
from .models.body import Paragraph, Run, Table, TableRow, TableCell
from .template import (
    default_font_faces, default_border_fills,
    default_char_prs, default_para_prs, default_styles,
)
from .xml_writer import (
    write_mimetype, write_version_xml, write_settings_xml,
    write_container_xml, write_manifest_xml, write_container_rdf,
    write_content_hpf, write_prv_text,
    write_header_xml, write_section_xml,
    set_id_seed, reset_id_seed,
)
from .package import HwpxPackage


# Map heading level to (charPr ID, paraPr ID, style ID)
_HEADING_MAP = {
    1: (CHARPR_H1, PARAPR_H1, 1),
    2: (CHARPR_H2, PARAPR_H2, 2),
    3: (CHARPR_H3, PARAPR_H3, 3),
    4: (CHARPR_H4, PARAPR_H4, 4),
    5: (CHARPR_H5, PARAPR_H5, 5),
    6: (CHARPR_H6, PARAPR_H6, 6),
}


class HwpxDocument:
    """High-level API for creating HWPX documents.

    Usage:
        doc = HwpxDocument.new()
        doc.add_heading("제목", level=1)
        doc.add_paragraph("본문 텍스트")
        doc.save("output.hwpx")
    """

    def __init__(self, seed: int = None):
        self._font_faces = default_font_faces()
        self._border_fills = default_border_fills()
        self._char_prs = default_char_prs()
        self._para_prs = default_para_prs()
        self._styles = default_styles()
        self._elements = []  # list of tuples for write_section_xml
        self._seed = seed

    @classmethod
    def new(cls, seed: int = None) -> "HwpxDocument":
        """Create a new empty document.

        Args:
            seed: Optional seed for deterministic element IDs.
                  If None, random IDs are generated (default).
        """
        return cls(seed=seed)

    def builder(self):
        """Return a fluent builder for this document."""
        from .builder import HwpxBuilder
        return HwpxBuilder(self)

    def add_heading(self, text: str, level: int = 1) -> Paragraph:
        """Add a heading paragraph (level 1-6)."""
        level = max(1, min(6, level))
        char_pr_id, para_pr_id, style_id = _HEADING_MAP[level]
        run = Run(text=text, char_pr_id_ref=char_pr_id)
        para = Paragraph(
            runs=[run],
            para_pr_id_ref=para_pr_id,
            style_id_ref=style_id,
        )
        self._elements.append(("paragraph", para))
        return para

    def add_paragraph(self, text: str = "", bold: bool = False,
                      italic: bool = False, runs: list = None) -> Paragraph:
        """Add a body paragraph.

        Args:
            text: Simple text content. Ignored if runs is provided.
            bold: Make entire paragraph bold.
            italic: Make entire paragraph italic.
            runs: List of (text, char_pr_id_ref) tuples for mixed formatting.
        """
        if runs:
            run_objects = [Run(text=t, char_pr_id_ref=c) for t, c in runs]
        elif text:
            if bold and italic:
                cpr = CHARPR_BOLD_ITALIC
            elif bold:
                cpr = CHARPR_BOLD
            elif italic:
                cpr = CHARPR_ITALIC
            else:
                cpr = CHARPR_BODY
            run_objects = [Run(text=text, char_pr_id_ref=cpr)]
        else:
            run_objects = []

        para = Paragraph(
            runs=run_objects,
            para_pr_id_ref=PARAPR_BODY,
            style_id_ref=0,
        )
        self._elements.append(("paragraph", para))
        return para

    def add_mixed_paragraph(self, segments: list) -> Paragraph:
        """Add a paragraph with mixed formatting.

        Args:
            segments: List of dicts with keys:
                - text: str
                - bold: bool (optional)
                - italic: bool (optional)
                - code: bool (optional, for inline code)
        """
        run_objects = []
        for seg in segments:
            text = seg.get("text", "")
            if seg.get("code"):
                cpr = CHARPR_INLINE_CODE
            elif seg.get("bold") and seg.get("italic"):
                cpr = CHARPR_BOLD_ITALIC
            elif seg.get("bold"):
                cpr = CHARPR_BOLD
            elif seg.get("italic"):
                cpr = CHARPR_ITALIC
            else:
                cpr = CHARPR_BODY
            run_objects.append(Run(text=text, char_pr_id_ref=cpr))

        para = Paragraph(
            runs=run_objects,
            para_pr_id_ref=PARAPR_BODY,
            style_id_ref=0,
        )
        self._elements.append(("paragraph", para))
        return para

    def add_table(self, headers: list, rows: list) -> Table:
        """Add a table.

        Args:
            headers: List of header cell strings.
            rows: List of rows, each a list of cell strings.
        """
        col_cnt = len(headers)
        row_cnt = 1 + len(rows)  # header + data rows

        # Calculate column widths (equal distribution)
        usable_width = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT
        col_width = usable_width // col_cnt

        table_rows = []

        # Header row
        header_cells = []
        for ci, h in enumerate(headers):
            cell_para = Paragraph(
                runs=[Run(text=h, char_pr_id_ref=CHARPR_TABLE_HEADER)],
                para_pr_id_ref=PARAPR_TABLE,
                style_id_ref=0,
            )
            header_cells.append(TableCell(
                paragraphs=[cell_para],
                col_addr=ci, row_addr=0,
                width=col_width, height=1000,
                border_fill_id_ref=BORDERFILL_TABLE_HEADER,
                header=1,
            ))
        table_rows.append(TableRow(cells=header_cells))

        # Data rows
        for ri, row_data in enumerate(rows):
            data_cells = []
            for ci, cell_text in enumerate(row_data):
                cell_para = Paragraph(
                    runs=[Run(text=cell_text, char_pr_id_ref=CHARPR_TABLE_BODY)],
                    para_pr_id_ref=PARAPR_TABLE,
                    style_id_ref=0,
                )
                data_cells.append(TableCell(
                    paragraphs=[cell_para],
                    col_addr=ci, row_addr=ri + 1,
                    width=col_width, height=1000,
                    border_fill_id_ref=BORDERFILL_TABLE,
                ))
            # Pad if row has fewer cells than headers
            while len(data_cells) < col_cnt:
                ci = len(data_cells)
                cell_para = Paragraph(
                    runs=[Run(text="", char_pr_id_ref=CHARPR_TABLE_BODY)],
                    para_pr_id_ref=PARAPR_TABLE,
                    style_id_ref=0,
                )
                data_cells.append(TableCell(
                    paragraphs=[cell_para],
                    col_addr=ci, row_addr=ri + 1,
                    width=col_width, height=1000,
                    border_fill_id_ref=BORDERFILL_TABLE,
                ))
            table_rows.append(TableRow(cells=data_cells))

        table = Table(
            rows=table_rows,
            row_cnt=row_cnt,
            col_cnt=col_cnt,
            width=usable_width,
            border_fill_id_ref=BORDERFILL_TABLE,
        )
        self._elements.append(("table", table, PARAPR_BODY, 0))
        return table

    def add_code_block(self, code: str, language: str = "") -> list:
        """Add a code block (one paragraph per line).

        Returns list of Paragraph objects created.
        """
        paragraphs = []
        lines = code.split('\n')
        for line in lines:
            # Use a non-breaking space for empty lines to preserve them
            text = line if line else " "
            run = Run(text=text, char_pr_id_ref=CHARPR_CODE_BLOCK)
            para = Paragraph(
                runs=[run],
                para_pr_id_ref=PARAPR_CODE,
                style_id_ref=0,
            )
            self._elements.append(("paragraph", para))
            paragraphs.append(para)
        return paragraphs

    def add_bullet_list(self, items: list) -> list:
        """Add a bullet list.

        Args:
            items: List of strings or list of segment lists (for mixed formatting).
        """
        paragraphs = []
        for item in items:
            if isinstance(item, str):
                run = Run(text=item, char_pr_id_ref=CHARPR_BODY)
                para = Paragraph(
                    runs=[run],
                    para_pr_id_ref=PARAPR_BULLET,
                    style_id_ref=0,
                )
            else:
                # Mixed formatting: item is list of dicts
                run_objects = []
                for seg in item:
                    text = seg.get("text", "")
                    if seg.get("code"):
                        cpr = CHARPR_INLINE_CODE
                    elif seg.get("bold"):
                        cpr = CHARPR_BOLD
                    elif seg.get("italic"):
                        cpr = CHARPR_ITALIC
                    else:
                        cpr = CHARPR_BODY
                    run_objects.append(Run(text=text, char_pr_id_ref=cpr))
                para = Paragraph(
                    runs=run_objects,
                    para_pr_id_ref=PARAPR_BULLET,
                    style_id_ref=0,
                )
            self._elements.append(("paragraph", para))
            paragraphs.append(para)
        return paragraphs

    def add_horizontal_rule(self) -> Paragraph:
        """Add a horizontal rule (thin line paragraph)."""
        # Use an empty paragraph with a border-bottom style
        run = Run(text="", char_pr_id_ref=CHARPR_BODY)
        para = Paragraph(
            runs=[run],
            para_pr_id_ref=PARAPR_BODY,
            style_id_ref=0,
        )
        self._elements.append(("paragraph", para))
        return para

    def _build_header_xml(self) -> str:
        """Build the header.xml content."""
        return write_header_xml(
            font_faces=self._font_faces,
            border_fills=self._border_fills,
            char_prs=self._char_prs,
            para_prs=self._para_prs,
            styles=self._styles,
        )

    def _build_section_xml(self) -> str:
        """Build the section0.xml content."""
        if not self._elements:
            # Empty document: add one empty paragraph
            para = Paragraph(
                runs=[],
                para_pr_id_ref=PARAPR_BODY,
                style_id_ref=0,
            )
            self._elements.append(("paragraph", para))
        return write_section_xml(self._elements, first_para_idx=0)

    def _get_preview_text(self) -> str:
        """Extract plain text for preview."""
        texts = []
        for elem in self._elements:
            if elem[0] == "paragraph":
                para = elem[1]
                for run in para.runs:
                    if run.text.strip():
                        texts.append(run.text)
            elif elem[0] == "table":
                tbl = elem[1]
                for row in tbl.rows:
                    for cell in row.cells:
                        for p in cell.paragraphs:
                            for r in p.runs:
                                if r.text.strip():
                                    texts.append(r.text)
        return ' '.join(texts)[:200]

    def save(self, path: str) -> None:
        """Save the document as a HWPX file."""
        if self._seed is not None:
            set_id_seed(self._seed)
        pkg = HwpxPackage()

        # Add all required files
        pkg.add_file('mimetype', write_mimetype())
        pkg.add_file('version.xml', write_version_xml())
        pkg.add_file('settings.xml', write_settings_xml())
        pkg.add_file('META-INF/container.xml', write_container_xml())
        pkg.add_file('META-INF/manifest.xml', write_manifest_xml())
        pkg.add_file('META-INF/container.rdf', write_container_rdf())
        pkg.add_file('Contents/content.hpf', write_content_hpf())
        pkg.add_file('Contents/header.xml', self._build_header_xml())
        pkg.add_file('Contents/section0.xml', self._build_section_xml())
        pkg.add_file('Preview/PrvText.txt', write_prv_text(self._get_preview_text()))

        pkg.save(path)
        if self._seed is not None:
            reset_id_seed()

    def to_bytes(self) -> bytes:
        """Return the document as bytes (for MCP server responses)."""
        if self._seed is not None:
            set_id_seed(self._seed)
        pkg = HwpxPackage()
        pkg.add_file('mimetype', write_mimetype())
        pkg.add_file('version.xml', write_version_xml())
        pkg.add_file('settings.xml', write_settings_xml())
        pkg.add_file('META-INF/container.xml', write_container_xml())
        pkg.add_file('META-INF/manifest.xml', write_manifest_xml())
        pkg.add_file('META-INF/container.rdf', write_container_rdf())
        pkg.add_file('Contents/content.hpf', write_content_hpf())
        pkg.add_file('Contents/header.xml', self._build_header_xml())
        pkg.add_file('Contents/section0.xml', self._build_section_xml())
        pkg.add_file('Preview/PrvText.txt', write_prv_text(self._get_preview_text()))
        result = pkg.to_bytes()
        if self._seed is not None:
            reset_id_seed()
        return result
