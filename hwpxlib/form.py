"""HwpxForm - Open existing HWPX files, find placeholders, fill and save.

Usage:
    form = HwpxForm.open("양식.hwpx")
    print(form.placeholders)  # ['사업명', '신청기관', ...]
    form.fill({"사업명": "AI 개발", "신청기관": "(주)영준시스템"})
    form.save("결과.hwpx")
"""
import re
import zipfile
import io
from xml.etree import ElementTree as ET


# Namespace map for HWPX XML
_NS = {
    "hp": "http://www.hancom.co.kr/hwpml/2011/paragraph",
    "hs": "http://www.hancom.co.kr/hwpml/2011/section",
    "hc": "http://www.hancom.co.kr/hwpml/2011/core",
    "hh": "http://www.hancom.co.kr/hwpml/2011/head",
}

# Register namespaces to prevent ET from rewriting prefixes
for prefix, uri in _NS.items():
    ET.register_namespace(prefix, uri)
# Additional namespaces that may appear
ET.register_namespace("hv", "http://www.hancom.co.kr/hwpml/2011/version")
ET.register_namespace("ha", "http://www.hancom.co.kr/hwpml/2011/app")
ET.register_namespace("opf", "http://www.idpf.org/2007/opf/")

_PLACEHOLDER_RE = re.compile(r'\{\{([^}]+)\}\}')


class HwpxForm:
    """Read an existing HWPX file, find/replace placeholders, save."""

    def __init__(self):
        self._files = {}       # path -> bytes (non-XML files kept as-is)
        self._xml_files = {}   # path -> ElementTree (parsed XML for modification)
        self._xml_raw = {}     # path -> original bytes (for files we don't parse)
        self._section_paths = []  # ordered list of section XML paths

    @classmethod
    def open(cls, path: str) -> "HwpxForm":
        """Open an existing HWPX file.

        Args:
            path: Path to .hwpx file.

        Returns:
            HwpxForm instance ready for fill() and save().
        """
        form = cls()
        with zipfile.ZipFile(path, 'r') as zf:
            for entry in zf.namelist():
                data = zf.read(entry)
                if entry.startswith('Contents/section') and entry.endswith('.xml'):
                    form._section_paths.append(entry)
                    tree = ET.ElementTree(ET.fromstring(data.decode('utf-8')))
                    form._xml_files[entry] = tree
                elif entry == 'Contents/header.xml':
                    tree = ET.ElementTree(ET.fromstring(data.decode('utf-8')))
                    form._xml_files[entry] = tree
                    form._files[entry] = data
                else:
                    form._files[entry] = data
        form._section_paths.sort()
        return form

    @classmethod
    def from_bytes(cls, data: bytes) -> "HwpxForm":
        """Open an HWPX from bytes."""
        form = cls()
        with zipfile.ZipFile(io.BytesIO(data), 'r') as zf:
            for entry in zf.namelist():
                file_data = zf.read(entry)
                if entry.startswith('Contents/section') and entry.endswith('.xml'):
                    form._section_paths.append(entry)
                    tree = ET.ElementTree(ET.fromstring(file_data.decode('utf-8')))
                    form._xml_files[entry] = tree
                elif entry == 'Contents/header.xml':
                    tree = ET.ElementTree(ET.fromstring(file_data.decode('utf-8')))
                    form._xml_files[entry] = tree
                    form._files[entry] = file_data
                else:
                    form._files[entry] = file_data
        form._section_paths.sort()
        return form

    @property
    def placeholders(self) -> list:
        """Find all {{placeholder}} names in the document.

        Scans all section XML files for {{name}} patterns in text elements.
        Returns sorted list of unique placeholder names.
        """
        found = set()
        for path in self._section_paths:
            tree = self._xml_files[path]
            root = tree.getroot()
            for t_elem in root.iter():
                if t_elem.tag.endswith('}t') or t_elem.tag == 't':
                    if t_elem.text:
                        for m in _PLACEHOLDER_RE.finditer(t_elem.text):
                            found.add(m.group(1))
        return sorted(found)

    def fill(self, data: dict, missing: str = "keep") -> "HwpxForm":
        """Replace {{placeholder}} markers with values from data dict.

        Args:
            data: Dict mapping placeholder names to replacement text.
                  Values can be str (single paragraph) or list[str] (multiple paragraphs).
            missing: What to do with unfilled placeholders:
                     "keep" = leave {{name}} as-is (default)
                     "blank" = replace with empty string
                     "error" = raise KeyError

        Returns:
            self (for chaining).
        """
        for path in self._section_paths:
            tree = self._xml_files[path]
            root = tree.getroot()
            self._fill_element(root, data, missing)
        return self

    def _fill_element(self, root, data: dict, missing: str):
        """Walk XML tree and replace placeholders in hp:t text elements."""
        # Collect all text elements that contain placeholders
        for t_elem in root.iter():
            if not (t_elem.tag.endswith('}t') or t_elem.tag == 't'):
                continue
            if not t_elem.text:
                continue
            if '{{' not in t_elem.text:
                continue

            def _replace_match(m):
                name = m.group(1)
                if name in data:
                    val = data[name]
                    if isinstance(val, list):
                        return '\n'.join(str(v) for v in val)
                    return str(val)
                if missing == "blank":
                    return ""
                if missing == "error":
                    raise KeyError(f"No value for placeholder: {name}")
                return m.group(0)  # keep

            t_elem.text = _PLACEHOLDER_RE.sub(_replace_match, t_elem.text)

    def get_text(self) -> str:
        """Extract all text from the document (for debugging/inspection)."""
        texts = []
        for path in self._section_paths:
            tree = self._xml_files[path]
            root = tree.getroot()
            for t_elem in root.iter():
                if t_elem.tag.endswith('}t') or t_elem.tag == 't':
                    if t_elem.text and t_elem.text.strip():
                        texts.append(t_elem.text.strip())
        return '\n'.join(texts)

    def get_table_text(self, table_index: int = 0, section_index: int = 0) -> list:
        """Extract text from a specific table as 2D list.

        Args:
            table_index: Which table in the section (0-based).
            section_index: Which section (0-based).

        Returns:
            List of rows, each row is a list of cell texts.
        """
        if section_index >= len(self._section_paths):
            return []
        path = self._section_paths[section_index]
        tree = self._xml_files[path]
        root = tree.getroot()

        ns_hp = _NS["hp"]
        tables = root.findall(f'.//{{{ns_hp}}}tbl')
        if table_index >= len(tables):
            return []

        tbl = tables[table_index]
        rows = []
        for tr in tbl.findall(f'{{{ns_hp}}}tr'):
            row = []
            for tc in tr.findall(f'{{{ns_hp}}}tc'):
                cell_texts = []
                for t_elem in tc.iter():
                    if t_elem.tag == f'{{{ns_hp}}}t' and t_elem.text:
                        cell_texts.append(t_elem.text)
                row.append(''.join(cell_texts))
            rows.append(row)
        return rows

    def fill_table_cell(self, table_index: int, row: int, col: int,
                        text: str, section_index: int = 0) -> "HwpxForm":
        """Fill a specific table cell by position.

        Args:
            table_index: Which table (0-based).
            row: Row index (0-based).
            col: Column index (0-based).
            text: Text to put in the cell.
            section_index: Which section (0-based).

        Returns:
            self (for chaining).
        """
        if section_index >= len(self._section_paths):
            raise IndexError(f"Section {section_index} not found")
        path = self._section_paths[section_index]
        tree = self._xml_files[path]
        root = tree.getroot()

        ns_hp = _NS["hp"]
        tables = root.findall(f'.//{{{ns_hp}}}tbl')
        if table_index >= len(tables):
            raise IndexError(f"Table {table_index} not found")

        tbl = tables[table_index]
        trs = tbl.findall(f'{{{ns_hp}}}tr')
        if row >= len(trs):
            raise IndexError(f"Row {row} not found in table {table_index}")

        tcs = trs[row].findall(f'{{{ns_hp}}}tc')
        if col >= len(tcs):
            raise IndexError(f"Col {col} not found in table {table_index} row {row}")

        tc = tcs[col]
        # Find first hp:t in this cell and replace its text
        for t_elem in tc.iter():
            if t_elem.tag == f'{{{ns_hp}}}t':
                t_elem.text = text
                return self

        # No hp:t found — this shouldn't happen in valid HWPX but handle gracefully
        # Find first hp:run and add hp:t
        for run in tc.iter():
            if run.tag == f'{{{ns_hp}}}run':
                t_new = ET.SubElement(run, f'{{{ns_hp}}}t')
                t_new.text = text
                return self

        return self

    def _serialize_xml(self, tree: ET.ElementTree) -> bytes:
        """Serialize ElementTree back to XML bytes."""
        buf = io.BytesIO()
        tree.write(buf, encoding='utf-8', xml_declaration=True)
        return buf.getvalue()

    def save(self, path: str) -> None:
        """Save the filled form as a new HWPX file."""
        with zipfile.ZipFile(path, 'w') as zf:
            # mimetype must be first, STORED
            if 'mimetype' in self._files:
                zf.writestr(
                    zipfile.ZipInfo('mimetype'),
                    self._files['mimetype'],
                    compress_type=zipfile.ZIP_STORED,
                )

            # Write all non-mimetype, non-section, non-header files
            for fpath, content in self._files.items():
                if fpath == 'mimetype':
                    continue
                if fpath in self._xml_files:
                    continue  # will write from parsed XML
                info = zipfile.ZipInfo(fpath)
                info.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(info, content)

            # Write parsed XML files (sections + header)
            for xml_path, tree in self._xml_files.items():
                info = zipfile.ZipInfo(xml_path)
                info.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(info, self._serialize_xml(tree))

    def to_bytes(self) -> bytes:
        """Return the filled form as bytes."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            if 'mimetype' in self._files:
                zf.writestr(
                    zipfile.ZipInfo('mimetype'),
                    self._files['mimetype'],
                    compress_type=zipfile.ZIP_STORED,
                )
            for fpath, content in self._files.items():
                if fpath == 'mimetype':
                    continue
                if fpath in self._xml_files:
                    continue
                info = zipfile.ZipInfo(fpath)
                info.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(info, content)
            for xml_path, tree in self._xml_files.items():
                info = zipfile.ZipInfo(xml_path)
                info.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(info, self._serialize_xml(tree))
        return buf.getvalue()
