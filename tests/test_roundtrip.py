"""End-to-end: MD -> HWPX -> extract XML -> validate structure.

Spec: specs/11-md-conversion.md
"""
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
from tests import NS


SAMPLE_MD = """\
# Test Document

This is a paragraph with **bold** and *italic* text.

## Section Two

| Header A | Header B |
|----------|----------|
| Cell 1   | Cell 2   |

- Bullet one
- Bullet two

```python
print("hello")
```

### Sub Section

Normal paragraph here.
"""


class TestMarkdownRoundtrip:
    @pytest.fixture
    def roundtrip_hwpx(self, tmp_path) -> Path:
        from converters.md2hwpx import convert_md_to_hwpx
        doc = convert_md_to_hwpx(SAMPLE_MD)
        out = tmp_path / "roundtrip.hwpx"
        doc.save(str(out))
        return out

    def test_hwpx_is_valid_zip(self, roundtrip_hwpx):
        assert zipfile.is_zipfile(roundtrip_hwpx)

    def test_has_all_entries(self, roundtrip_hwpx):
        with zipfile.ZipFile(roundtrip_hwpx, "r") as zf:
            names = zf.namelist()
            assert "mimetype" in names
            assert "Contents/header.xml" in names
            assert "Contents/section0.xml" in names

    def test_header_is_valid_xml(self, roundtrip_hwpx):
        with zipfile.ZipFile(roundtrip_hwpx, "r") as zf:
            xml = zf.read("Contents/header.xml").decode("utf-8")
        root = ET.fromstring(xml)
        assert root.tag == f"{{{NS['hh']}}}head"

    def test_section_is_valid_xml(self, roundtrip_hwpx):
        with zipfile.ZipFile(roundtrip_hwpx, "r") as zf:
            xml = zf.read("Contents/section0.xml").decode("utf-8")
        root = ET.fromstring(xml)
        assert root.tag == f"{{{NS['hs']}}}sec"

    def test_section_has_heading(self, roundtrip_hwpx):
        with zipfile.ZipFile(roundtrip_hwpx, "r") as zf:
            xml = zf.read("Contents/section0.xml").decode("utf-8")
        root = ET.fromstring(xml)
        paragraphs = root.findall(f"{{{NS['hp']}}}p")
        # First paragraph should be heading 1
        first_p = paragraphs[0]
        assert first_p.get("styleIDRef") == "1"  # Heading 1 style

    def test_section_has_table(self, roundtrip_hwpx):
        with zipfile.ZipFile(roundtrip_hwpx, "r") as zf:
            xml = zf.read("Contents/section0.xml").decode("utf-8")
        root = ET.fromstring(xml)
        tables = root.findall(f".//{{{NS['hp']}}}tbl")
        assert len(tables) >= 1, "Should have at least one table"

    def test_section_has_bullets(self, roundtrip_hwpx):
        with zipfile.ZipFile(roundtrip_hwpx, "r") as zf:
            xml = zf.read("Contents/section0.xml").decode("utf-8")
        root = ET.fromstring(xml)
        # Bullet paragraphs use paraPrIDRef="8"
        bullet_paras = [p for p in root.findall(f"{{{NS['hp']}}}p")
                        if p.get("paraPrIDRef") == "8"]
        assert len(bullet_paras) >= 2

    def test_section_has_code_block(self, roundtrip_hwpx):
        with zipfile.ZipFile(roundtrip_hwpx, "r") as zf:
            xml = zf.read("Contents/section0.xml").decode("utf-8")
        root = ET.fromstring(xml)
        # Code block paragraphs use paraPrIDRef="7"
        code_paras = [p for p in root.findall(f"{{{NS['hp']}}}p")
                      if p.get("paraPrIDRef") == "7"]
        assert len(code_paras) >= 1

    def test_first_para_has_secpr(self, roundtrip_hwpx):
        with zipfile.ZipFile(roundtrip_hwpx, "r") as zf:
            xml = zf.read("Contents/section0.xml").decode("utf-8")
        root = ET.fromstring(xml)
        first_p = root.find(f"{{{NS['hp']}}}p")
        first_run = first_p.find(f"{{{NS['hp']}}}run")
        sec_pr = first_run.find(f"{{{NS['hp']}}}secPr")
        assert sec_pr is not None

    def test_styles_have_langid_1042(self, roundtrip_hwpx):
        with zipfile.ZipFile(roundtrip_hwpx, "r") as zf:
            xml = zf.read("Contents/header.xml").decode("utf-8")
        root = ET.fromstring(xml)
        styles = root.findall(".//hh:style", NS)
        for st in styles:
            assert st.get("langID") == "1042"
