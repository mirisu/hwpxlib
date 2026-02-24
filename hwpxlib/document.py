"""HwpxDocument - Main API for creating and manipulating HWPX documents."""
from .constants import (
    CHARPR_BODY, CHARPR_BOLD, CHARPR_ITALIC, CHARPR_BOLD_ITALIC,
    CHARPR_H1, CHARPR_H2, CHARPR_H3, CHARPR_H4, CHARPR_H5, CHARPR_H6,
    CHARPR_INLINE_CODE, CHARPR_CODE_BLOCK,
    CHARPR_TABLE_HEADER, CHARPR_TABLE_BODY,
    PARAPR_BODY, PARAPR_H1, PARAPR_H2, PARAPR_H3,
    PARAPR_H4, PARAPR_H5, PARAPR_H6,
    PARAPR_CODE, PARAPR_BULLET, PARAPR_TABLE, PARAPR_ORDERED,
    PARAPR_BULLET_L2, PARAPR_BULLET_L3,
    PARAPR_ORDERED_L2, PARAPR_ORDERED_L3,
    BORDERFILL_TABLE, BORDERFILL_TABLE_HEADER,
    PAGE_WIDTH, MARGIN_LEFT, MARGIN_RIGHT,
)
from .models.body import Paragraph, Run, Table, TableRow, TableCell, Image
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
import os
import struct
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


def _detect_image_size(data: bytes) -> tuple:
    """Detect image dimensions from raw bytes. Returns (width, height) in pixels."""
    # PNG
    if data[:8] == b'\x89PNG\r\n\x1a\n' and len(data) >= 24:
        w, h = struct.unpack('>II', data[16:24])
        return (w, h)
    # JPEG
    if data[:2] == b'\xff\xd8':
        i = 2
        while i < len(data) - 1:
            if data[i] != 0xFF:
                break
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack('>HH', data[i + 5:i + 9])
                return (w, h)
            length = struct.unpack('>H', data[i + 2:i + 4])[0]
            i += 2 + length
    # GIF
    if data[:4] == b'GIF8' and len(data) >= 10:
        w, h = struct.unpack('<HH', data[6:10])
        return (w, h)
    # BMP
    if data[:2] == b'BM' and len(data) >= 26:
        w, h = struct.unpack('<ii', data[18:26])
        return (abs(w), abs(h))
    # Fallback
    return (200, 200)


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
        self._images = []   # list of Image objects for BinData packaging
        self._image_counter = 0
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

    _BULLET_LEVEL_MAP = {0: PARAPR_BULLET, 1: PARAPR_BULLET_L2, 2: PARAPR_BULLET_L3}
    _ORDERED_LEVEL_MAP = {0: PARAPR_ORDERED, 1: PARAPR_ORDERED_L2, 2: PARAPR_ORDERED_L3}

    def add_bullet_list(self, items: list) -> list:
        """Add a bullet list.

        Args:
            items: List of items. Each item can be:
                - str: plain text at level 0
                - list[dict]: formatted segments at level 0
                - (str_or_segments, level): text/segments with nesting level (0-2)
        """
        paragraphs = []
        for item in items:
            level = 0
            content = item
            if isinstance(item, tuple) and len(item) == 2:
                content, level = item
                level = min(max(level, 0), 2)

            para_pr = self._BULLET_LEVEL_MAP.get(level, PARAPR_BULLET)

            if isinstance(content, str):
                run = Run(text=content, char_pr_id_ref=CHARPR_BODY)
                para = Paragraph(runs=[run], para_pr_id_ref=para_pr, style_id_ref=0)
            else:
                run_objects = []
                for seg in content:
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
                para = Paragraph(runs=run_objects, para_pr_id_ref=para_pr, style_id_ref=0)

            self._elements.append(("paragraph", para))
            paragraphs.append(para)
        return paragraphs

    def add_ordered_list(self, items: list) -> list:
        """Add an ordered (numbered) list.

        Args:
            items: List of items. Each item can be:
                - str: plain text at level 0
                - list[dict]: formatted segments at level 0
                - (str_or_segments, level): text/segments with nesting level (0-2)
        """
        paragraphs = []
        for item in items:
            level = 0
            content = item
            if isinstance(item, tuple) and len(item) == 2:
                content, level = item
                level = min(max(level, 0), 2)

            para_pr = self._ORDERED_LEVEL_MAP.get(level, PARAPR_ORDERED)

            if isinstance(content, str):
                run = Run(text=content, char_pr_id_ref=CHARPR_BODY)
                para = Paragraph(runs=[run], para_pr_id_ref=para_pr, style_id_ref=0)
            else:
                run_objects = []
                for seg in content:
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
                para = Paragraph(runs=run_objects, para_pr_id_ref=para_pr, style_id_ref=0)

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

    def add_image(self, image_path: str = "", image_data: bytes = None,
                  width: int = None, height: int = None) -> Image:
        """Add an image.

        Args:
            image_path: Path to image file (png, jpg, etc.)
            image_data: Raw image bytes (alternative to image_path)
            width: Image width in HWPUNIT (default: auto from pixel size)
            height: Image height in HWPUNIT (default: auto from pixel size)

        Returns:
            Image object that was added.
        """
        if image_data is None:
            if not image_path:
                raise ValueError("image_path or image_data is required")
            with open(image_path, 'rb') as f:
                image_data = f.read()

        # Determine media type
        if image_path:
            ext = os.path.splitext(image_path)[1].lower()
        else:
            # Detect from magic bytes
            if image_data[:8] == b'\x89PNG\r\n\x1a\n':
                ext = '.png'
            elif image_data[:2] == b'\xff\xd8':
                ext = '.jpg'
            elif image_data[:4] == b'GIF8':
                ext = '.gif'
            elif image_data[:2] == b'BM':
                ext = '.bmp'
            else:
                ext = '.png'

        mime_map = {
            '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
            '.gif': 'image/gif', '.bmp': 'image/bmp', '.tif': 'image/tiff',
            '.tiff': 'image/tiff',
        }
        media_type = mime_map.get(ext, 'image/png')

        # Auto-detect dimensions from image data if not specified
        if width is None or height is None:
            pw, ph = _detect_image_size(image_data)
            # Convert pixels to HWPUNIT (75 HWPUNIT per pixel is reasonable)
            if width is None:
                width = pw * 75
            if height is None:
                height = ph * 75

        self._image_counter += 1
        item_id = f"image{self._image_counter}"
        filename = f"{item_id}{ext}"

        image = Image(
            binary_item_id=item_id,
            width=width,
            height=height,
            data=image_data,
            media_type=media_type,
        )
        image._filename = filename  # used by packaging
        self._images.append(image)
        self._elements.append(("image", image, PARAPR_BODY, 0))
        return image

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

    def _build_package(self) -> 'HwpxPackage':
        """Build the complete HWPX package with all files."""
        # Build image manifest entries
        image_entries = []
        for img in self._images:
            image_entries.append((img.binary_item_id, img._filename, img.media_type))

        pkg = HwpxPackage()
        pkg.add_file('mimetype', write_mimetype())
        pkg.add_file('version.xml', write_version_xml())
        pkg.add_file('settings.xml', write_settings_xml())
        pkg.add_file('META-INF/container.xml', write_container_xml())
        pkg.add_file('META-INF/manifest.xml', write_manifest_xml())
        pkg.add_file('META-INF/container.rdf', write_container_rdf())
        pkg.add_file('Contents/content.hpf',
                      write_content_hpf(images=image_entries or None))
        pkg.add_file('Contents/header.xml', self._build_header_xml())
        pkg.add_file('Contents/section0.xml', self._build_section_xml())
        pkg.add_file('Preview/PrvText.txt', write_prv_text(self._get_preview_text()))

        # Add image binary data
        for img in self._images:
            pkg.add_file(f'BinData/{img._filename}', img.data)

        return pkg

    def save(self, path: str) -> None:
        """Save the document as a HWPX file."""
        if self._seed is not None:
            set_id_seed(self._seed)
        pkg = self._build_package()
        pkg.save(path)
        if self._seed is not None:
            reset_id_seed()

    def to_bytes(self) -> bytes:
        """Return the document as bytes (for MCP server responses)."""
        if self._seed is not None:
            set_id_seed(self._seed)
        pkg = self._build_package()
        result = pkg.to_bytes()
        if self._seed is not None:
            reset_id_seed()
        return result
