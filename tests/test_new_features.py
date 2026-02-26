"""Tests for ordered lists, nested lists, page setup, style customization, and images."""
import os
import struct
import zipfile
from io import BytesIO
from xml.etree import ElementTree as ET

import pytest

from hwpxlib.document import HwpxDocument
from hwpxlib.models.body import PageSetup
from hwpxlib.style_config import StyleConfig
from hwpxlib.constants import (
    PARAPR_BULLET, PARAPR_ORDERED,
    PARAPR_BULLET_L2, PARAPR_BULLET_L3,
    PARAPR_ORDERED_L2, PARAPR_ORDERED_L3,
    mm_to_hwpunit, PAGE_WIDTH, PAGE_HEIGHT,
)
from converters.md_parser import parse_markdown, BulletList, OrderedList


# === Markdown Parser: Ordered Lists ===

class TestOrderedListParser:

    def test_parse_simple_ordered_list(self):
        md = "1. First\n2. Second\n3. Third"
        ast = parse_markdown(md)
        assert len(ast) == 1
        assert isinstance(ast[0], OrderedList)
        assert len(ast[0].items) == 3

    def test_ordered_list_item_text(self):
        md = "1. Alpha\n2. Beta"
        ast = parse_markdown(md)
        segments, level = ast[0].items[0]
        assert segments[0].text == "Alpha"
        assert level == 0

    def test_ordered_list_with_formatting(self):
        md = "1. **Bold** item\n2. Normal item"
        ast = parse_markdown(md)
        segments, level = ast[0].items[0]
        assert any(s.bold for s in segments)

    def test_ordered_list_dot_and_paren(self):
        md = "1) First\n2) Second"
        ast = parse_markdown(md)
        assert isinstance(ast[0], OrderedList)
        assert len(ast[0].items) == 2


# === Markdown Parser: Nested Lists ===

class TestNestedListParser:

    def test_nested_bullet_levels(self):
        md = "- Level 0\n  - Level 1\n    - Level 2"
        ast = parse_markdown(md)
        assert isinstance(ast[0], BulletList)
        items = ast[0].items
        assert items[0][1] == 0
        assert items[1][1] == 1
        assert items[2][1] == 2

    def test_nested_ordered_levels(self):
        md = "1. Level 0\n  1. Level 1\n    1. Level 2"
        ast = parse_markdown(md)
        assert isinstance(ast[0], OrderedList)
        items = ast[0].items
        assert items[0][1] == 0
        assert items[1][1] == 1
        assert items[2][1] == 2

    def test_max_level_capped_at_2(self):
        md = "- L0\n        - Deep indent"
        ast = parse_markdown(md)
        _, level = ast[0].items[1]
        assert level == 2  # capped

    def test_mixed_levels_in_bullet(self):
        md = "- A\n  - A1\n  - A2\n- B"
        ast = parse_markdown(md)
        items = ast[0].items
        assert len(items) == 4
        assert items[0][1] == 0
        assert items[1][1] == 1
        assert items[2][1] == 1
        assert items[3][1] == 0


# === Document API: Ordered List ===

class TestOrderedListDocument:

    def test_add_ordered_list_creates_elements(self):
        doc = HwpxDocument.new()
        doc.add_ordered_list(["A", "B", "C"])
        assert len(doc._elements) == 3
        for elem in doc._elements:
            assert elem[0] == "paragraph"
            assert elem[1].para_pr_id_ref == PARAPR_ORDERED

    def test_add_ordered_list_with_level(self):
        doc = HwpxDocument.new()
        doc.add_ordered_list([("L0", 0), ("L1", 1), ("L2", 2)])
        assert doc._elements[0][1].para_pr_id_ref == PARAPR_ORDERED
        assert doc._elements[1][1].para_pr_id_ref == PARAPR_ORDERED_L2
        assert doc._elements[2][1].para_pr_id_ref == PARAPR_ORDERED_L3


# === Document API: Nested Bullet List ===

class TestNestedBulletDocument:

    def test_nested_bullet_parapr_ids(self):
        doc = HwpxDocument.new()
        doc.add_bullet_list([("A", 0), ("B", 1), ("C", 2)])
        assert doc._elements[0][1].para_pr_id_ref == PARAPR_BULLET
        assert doc._elements[1][1].para_pr_id_ref == PARAPR_BULLET_L2
        assert doc._elements[2][1].para_pr_id_ref == PARAPR_BULLET_L3

    def test_backward_compat_no_level(self):
        """Plain strings should still work (level 0)."""
        doc = HwpxDocument.new()
        doc.add_bullet_list(["A", "B"])
        for elem in doc._elements:
            assert elem[1].para_pr_id_ref == PARAPR_BULLET


# === Page Setup ===

class TestPageSetup:

    def test_a4_defaults(self):
        ps = PageSetup.a4()
        assert ps.width == PAGE_WIDTH
        assert ps.height == PAGE_HEIGHT
        assert ps.orientation == "WIDELY"

    def test_a4_landscape(self):
        ps = PageSetup.a4(landscape=True)
        assert ps.width == PAGE_HEIGHT
        assert ps.height == PAGE_WIDTH
        assert ps.orientation == "NARROWLY"

    def test_letter_size(self):
        ps = PageSetup.letter()
        assert ps.width == mm_to_hwpunit(216)
        assert ps.height == mm_to_hwpunit(279)

    def test_a3_size(self):
        ps = PageSetup.a3()
        assert ps.width == mm_to_hwpunit(297)
        assert ps.height == mm_to_hwpunit(420)

    def test_usable_width(self):
        ps = PageSetup()
        expected = ps.width - ps.margin_left - ps.margin_right
        assert ps.usable_width == expected

    def test_set_page_setup_on_document(self):
        doc = HwpxDocument.new()
        doc.set_page_setup(PageSetup.letter())
        assert doc.page_setup.width == mm_to_hwpunit(216)

    def test_set_page_setup_kwargs(self):
        doc = HwpxDocument.new()
        doc.set_page_setup(margin_left=5000, margin_right=5000)
        assert doc.page_setup.margin_left == 5000
        assert doc.page_setup.margin_right == 5000

    def test_page_setup_in_output_xml(self, tmp_path):
        doc = HwpxDocument.new(seed=1)
        doc.set_page_setup(PageSetup.a4(landscape=True))
        doc.add_paragraph("Test")
        out = tmp_path / "landscape.hwpx"
        doc.save(str(out))

        with zipfile.ZipFile(str(out)) as zf:
            section = zf.read("Contents/section0.xml").decode("utf-8")
        assert 'landscape="NARROWLY"' in section
        assert f'width="{PAGE_HEIGHT}"' in section

    def test_table_width_uses_page_setup(self):
        doc = HwpxDocument.new()
        doc.set_page_setup(PageSetup.letter())
        doc.add_table(["A", "B"], [["1", "2"]])
        tbl = doc._elements[0][1]
        expected_width = doc.page_setup.usable_width
        assert tbl.width == expected_width


# === Style Customization ===

class TestStyleConfig:

    def test_default_style_config(self):
        cfg = StyleConfig()
        assert cfg.font_body == "나눔고딕"
        assert cfg.font_code == "나눔고딕코딩"
        assert cfg.font_size_body == 1000
        assert cfg.line_spacing == 160

    def test_custom_style_config(self):
        cfg = StyleConfig(font_body="맑은 고딕", font_size_body=1100)
        assert cfg.font_body == "맑은 고딕"
        assert cfg.font_size_body == 1100

    def test_set_style_changes_fonts(self, tmp_path):
        doc = HwpxDocument.new(seed=1)
        doc.set_style(font_body="맑은 고딕", font_code="D2Coding")
        doc.add_paragraph("Test")
        out = tmp_path / "custom_font.hwpx"
        doc.save(str(out))

        with zipfile.ZipFile(str(out)) as zf:
            header = zf.read("Contents/header.xml").decode("utf-8")
        assert '맑은 고딕' in header
        assert 'D2Coding' in header

    def test_set_style_changes_colors(self, tmp_path):
        doc = HwpxDocument.new(seed=1)
        doc.set_style(color_heading="#FF0000")
        doc.add_heading("Red Heading", level=1)
        out = tmp_path / "custom_color.hwpx"
        doc.save(str(out))

        with zipfile.ZipFile(str(out)) as zf:
            header = zf.read("Contents/header.xml").decode("utf-8")
        assert '#FF0000' in header

    def test_set_style_with_config_object(self):
        doc = HwpxDocument.new()
        cfg = StyleConfig(font_body="Arial", line_spacing=200)
        doc.set_style(cfg)
        # Verify fonts were rebuilt
        assert doc._font_faces[0].fonts[0].face == "Arial"

    def test_set_style_chaining(self):
        doc = HwpxDocument.new()
        result = doc.set_style(font_body="맑은 고딕")
        assert result is doc  # returns self


# === Image Support ===

class TestImageSupport:

    @staticmethod
    def _make_png(width=10, height=10):
        """Create a minimal valid PNG."""
        import zlib
        signature = b'\x89PNG\r\n\x1a\n'
        # IHDR
        ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
        ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xFFFFFFFF
        ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
        # IDAT (minimal)
        raw = b'\x00' * (width * 3 + 1) * height
        compressed = zlib.compress(raw)
        idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xFFFFFFFF
        idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
        # IEND
        iend_crc = zlib.crc32(b'IEND') & 0xFFFFFFFF
        iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
        return signature + ihdr + idat + iend

    def test_add_image_from_bytes(self):
        doc = HwpxDocument.new()
        png = self._make_png(100, 50)
        img = doc.add_image(image_data=png)
        assert img.binary_item_id == "image1"
        assert img.media_type == "image/png"
        assert img.width == 100 * 75   # pixels * 75 HWPUNIT
        assert img.height == 50 * 75

    def test_add_image_custom_size(self):
        doc = HwpxDocument.new()
        png = self._make_png()
        img = doc.add_image(image_data=png, width=20000, height=10000)
        assert img.width == 20000
        assert img.height == 10000

    def test_image_in_output_zip(self, tmp_path):
        doc = HwpxDocument.new(seed=1)
        png = self._make_png(10, 10)
        doc.add_image(image_data=png)
        out = tmp_path / "with_image.hwpx"
        doc.save(str(out))

        with zipfile.ZipFile(str(out)) as zf:
            names = zf.namelist()
            assert any("BinData/" in n for n in names)
            # content.hpf should reference the image
            hpf = zf.read("Contents/content.hpf").decode("utf-8")
            assert "image1" in hpf
            assert 'isEmbeded="1"' in hpf

    def test_image_in_section_xml(self, tmp_path):
        doc = HwpxDocument.new(seed=1)
        png = self._make_png(10, 10)
        doc.add_image(image_data=png)
        out = tmp_path / "img_section.hwpx"
        doc.save(str(out))

        with zipfile.ZipFile(str(out)) as zf:
            section = zf.read("Contents/section0.xml").decode("utf-8")
        assert "hp:pic" in section
        assert "image1" in section


# === End-to-End: MD with nested lists ===

class TestMdConversionNewFeatures:

    def test_md_ordered_list_roundtrip(self, tmp_path):
        from converters.md2hwpx import convert_md_to_hwpx
        md = "1. First\n2. Second\n3. Third"
        doc = convert_md_to_hwpx(md)
        out = tmp_path / "ordered.hwpx"
        doc.save(str(out))
        assert out.exists()
        assert out.stat().st_size > 0

    def test_md_nested_bullet_roundtrip(self, tmp_path):
        from converters.md2hwpx import convert_md_to_hwpx
        md = "- A\n  - A1\n    - A1a\n- B"
        doc = convert_md_to_hwpx(md)
        out = tmp_path / "nested.hwpx"
        doc.save(str(out))

        with zipfile.ZipFile(str(out)) as zf:
            section = zf.read("Contents/section0.xml").decode("utf-8")
        # Should have different paraPrIDRef values for different levels
        assert f'paraPrIDRef="{PARAPR_BULLET}"' in section
        assert f'paraPrIDRef="{PARAPR_BULLET_L2}"' in section
        assert f'paraPrIDRef="{PARAPR_BULLET_L3}"' in section


# === Header/Footer Support ===

class TestHeaderFooter:

    def test_set_header_text(self):
        doc = HwpxDocument.new()
        result = doc.set_header("Test Header")
        assert result is doc  # chaining
        assert doc._header is not None
        assert doc._header.paragraphs[0].runs[0].text == "Test Header"
        assert doc._header.apply_page_type == "BOTH"

    def test_set_footer_text(self):
        doc = HwpxDocument.new()
        doc.set_footer("Page Footer", apply_page_type="ODD")
        assert doc._footer is not None
        assert doc._footer.paragraphs[0].runs[0].text == "Page Footer"
        assert doc._footer.apply_page_type == "ODD"

    def test_header_in_section_xml(self, tmp_path):
        doc = HwpxDocument.new(seed=42)
        doc.set_header("Report Header")
        doc.add_paragraph("Body text")
        out = tmp_path / "header.hwpx"
        doc.save(str(out))

        with zipfile.ZipFile(str(out)) as zf:
            section = zf.read("Contents/section0.xml").decode("utf-8")
        assert "hp:header" in section
        assert "Report Header" in section
        assert 'applyPageType="BOTH"' in section

    def test_footer_in_section_xml(self, tmp_path):
        doc = HwpxDocument.new(seed=42)
        doc.set_footer("Page Footer")
        doc.add_paragraph("Body text")
        out = tmp_path / "footer.hwpx"
        doc.save(str(out))

        with zipfile.ZipFile(str(out)) as zf:
            section = zf.read("Contents/section0.xml").decode("utf-8")
        assert "hp:footer" in section
        assert "Page Footer" in section

    def test_both_header_and_footer(self, tmp_path):
        doc = HwpxDocument.new(seed=42)
        doc.set_header("Header")
        doc.set_footer("Footer")
        doc.add_paragraph("Body")
        out = tmp_path / "both.hwpx"
        doc.save(str(out))

        with zipfile.ZipFile(str(out)) as zf:
            section = zf.read("Contents/section0.xml").decode("utf-8")
        assert "hp:header" in section
        assert "hp:footer" in section
        assert "Header" in section
        assert "Footer" in section

    def test_header_has_sublist_structure(self, tmp_path):
        doc = HwpxDocument.new(seed=42)
        doc.set_header("Test")
        doc.add_paragraph("Body")
        out = tmp_path / "hf_struct.hwpx"
        doc.save(str(out))

        with zipfile.ZipFile(str(out)) as zf:
            section = zf.read("Contents/section0.xml").decode("utf-8")
        tree = ET.fromstring(section)
        ns = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}
        headers = tree.findall(".//hp:header", ns)
        assert len(headers) == 1
        sublists = headers[0].findall("hp:subList", ns)
        assert len(sublists) == 1
        paras = sublists[0].findall("hp:p", ns)
        assert len(paras) >= 1

    def test_header_footer_chaining(self):
        doc = HwpxDocument.new()
        result = doc.set_header("H").set_footer("F")
        assert result is doc


# === TOC Support ===

class TestTOC:

    def test_toc_generates_entries(self):
        doc = HwpxDocument.new()
        doc.add_heading("Chapter 1", level=1)
        doc.add_paragraph("Some text")
        doc.add_heading("Section 1.1", level=2)
        doc.add_paragraph("More text")
        doc.add_heading("Chapter 2", level=1)

        entries = doc.add_toc(title="Contents")
        # Should find 3 headings (Chapter 1, Section 1.1, Chapter 2)
        # Note: "Contents" heading itself is not included because it's added
        # after scanning existing headings
        assert len(entries) == 3

    def test_toc_indentation(self):
        doc = HwpxDocument.new()
        doc.add_heading("H1", level=1)
        doc.add_heading("H2", level=2)
        doc.add_heading("H3", level=3)
        entries = doc.add_toc(title="")

        texts = [e.runs[0].text for e in entries]
        assert texts[0] == "H1"       # no indent for level 1
        assert texts[1] == "  H2"     # 2-space indent for level 2
        assert texts[2] == "    H3"   # 4-space indent for level 3

    def test_toc_in_output_xml(self, tmp_path):
        doc = HwpxDocument.new(seed=42)
        doc.add_heading("Introduction", level=1)
        doc.add_heading("Methods", level=1)
        doc.add_toc(title="TOC")
        out = tmp_path / "toc.hwpx"
        doc.save(str(out))

        with zipfile.ZipFile(str(out)) as zf:
            section = zf.read("Contents/section0.xml").decode("utf-8")
        assert "Introduction" in section
        assert "Methods" in section
        assert "TOC" in section

    def test_no_header_footer_by_default(self, tmp_path):
        doc = HwpxDocument.new(seed=42)
        doc.add_paragraph("Body only")
        out = tmp_path / "no_hf.hwpx"
        doc.save(str(out))

        with zipfile.ZipFile(str(out)) as zf:
            section = zf.read("Contents/section0.xml").decode("utf-8")
        assert "hp:header" not in section
        assert "hp:footer" not in section


class TestBlockQuote:
    def test_blockquote_plain_text(self):
        doc = HwpxDocument.new(seed=42)
        para = doc.add_blockquote("This is a quote")
        assert para.runs[0].text == "This is a quote"
        assert para.para_pr_id_ref == 16  # PARAPR_BLOCKQUOTE

    def test_blockquote_with_formatting(self):
        doc = HwpxDocument.new(seed=42)
        segments = [
            {"text": "Bold quote", "bold": True},
            {"text": " continues", "italic": False},
        ]
        para = doc.add_blockquote(segments=segments)
        assert len(para.runs) == 2
        assert para.runs[0].char_pr_id_ref == 1  # CHARPR_BOLD
        assert para.para_pr_id_ref == 16  # PARAPR_BLOCKQUOTE

    def test_blockquote_in_output_xml(self, tmp_path):
        doc = HwpxDocument.new(seed=42)
        doc.add_blockquote("Quoted text")
        out = tmp_path / "bq.hwpx"
        doc.save(str(out))

        with zipfile.ZipFile(str(out)) as zf:
            section = zf.read("Contents/section0.xml").decode("utf-8")
        assert "Quoted text" in section
        # paraPrIDRef="16" in the output
        assert 'paraPrIDRef="16"' in section

    def test_blockquote_borderfill_in_header(self, tmp_path):
        doc = HwpxDocument.new(seed=42)
        doc.add_blockquote("Test")
        out = tmp_path / "bq_hdr.hwpx"
        doc.save(str(out))

        with zipfile.ZipFile(str(out)) as zf:
            header = zf.read("Contents/header.xml").decode("utf-8")
        # borderFill id=8 should exist with left border
        root = ET.fromstring(header)
        ns = {"hh": "http://www.hancom.co.kr/hwpml/2011/head"}
        bfs = root.findall(".//hh:borderFill", ns)
        bf_ids = [bf.get("id") for bf in bfs]
        assert "8" in bf_ids

    def test_blockquote_no_curly_quotes(self):
        """Blockquote should NOT wrap text in curly quotes anymore."""
        doc = HwpxDocument.new(seed=42)
        para = doc.add_blockquote("Simple quote")
        text = para.runs[0].text
        assert "\u201C" not in text
        assert "\u201D" not in text

    def test_md_blockquote_conversion(self):
        """Markdown blockquote should use add_blockquote, not italic paragraph."""
        from converters.md_parser import parse_markdown
        from converters.md2hwpx import convert_md_to_hwpx

        md = "> This is a blockquote"
        doc = convert_md_to_hwpx(md)
        # Find blockquote paragraph
        found = False
        for elem in doc._elements:
            if elem[0] == "paragraph":
                para = elem[1]
                if para.para_pr_id_ref == 16:  # PARAPR_BLOCKQUOTE
                    found = True
                    assert para.runs[0].text == "This is a blockquote"
                    break
        assert found, "Expected a blockquote paragraph with PARAPR_BLOCKQUOTE"


class TestStrikethrough:
    def test_strikethrough_in_mixed_paragraph(self):
        doc = HwpxDocument.new(seed=42)
        segments = [
            {"text": "normal "},
            {"text": "deleted", "strikethrough": True},
            {"text": " text"},
        ]
        para = doc.add_mixed_paragraph(segments)
        assert para.runs[1].char_pr_id_ref == 15  # CHARPR_STRIKETHROUGH

    def test_strikethrough_in_output_xml(self, tmp_path):
        doc = HwpxDocument.new(seed=42)
        doc.add_mixed_paragraph([{"text": "strike", "strikethrough": True}])
        out = tmp_path / "strike.hwpx"
        doc.save(str(out))

        with zipfile.ZipFile(str(out)) as zf:
            header = zf.read("Contents/header.xml").decode("utf-8")
        # charPr id=15 should have strikeout shape="SOLID"
        root = ET.fromstring(header)
        ns = {"hh": "http://www.hancom.co.kr/hwpml/2011/head"}
        cps = root.findall(".//hh:charPr", ns)
        cp15 = [cp for cp in cps if cp.get("id") == "15"][0]
        strike = cp15.find("hh:strikeout", ns)
        assert strike is not None
        assert strike.get("shape") == "SOLID"

    def test_md_strikethrough_parsing(self):
        from converters.md_parser import parse_inline
        segs = parse_inline("hello ~~deleted~~ world")
        assert len(segs) == 3
        assert segs[1].strikethrough is True
        assert segs[1].text == "deleted"

    def test_md_strikethrough_conversion(self):
        from converters.md2hwpx import convert_md_to_hwpx
        doc = convert_md_to_hwpx("This has ~~deleted~~ text")
        found = False
        for elem in doc._elements:
            if elem[0] == "paragraph":
                for run in elem[1].runs:
                    if run.char_pr_id_ref == 15:
                        found = True
                        break
        assert found, "Expected strikethrough charPr in output"


class TestPageBreak:
    def test_page_break_paragraph(self):
        doc = HwpxDocument.new(seed=42)
        para = doc.add_page_break()
        assert para.page_break is True

    def test_page_break_in_xml(self, tmp_path):
        doc = HwpxDocument.new(seed=42)
        doc.add_paragraph("Page 1 content")
        doc.add_page_break()
        doc.add_paragraph("Page 2 content")
        out = tmp_path / "pb.hwpx"
        doc.save(str(out))

        with zipfile.ZipFile(str(out)) as zf:
            section = zf.read("Contents/section0.xml").decode("utf-8")
        assert 'pageBreak="1"' in section
        assert "Page 1 content" in section
        assert "Page 2 content" in section

    def test_normal_paragraph_no_page_break(self, tmp_path):
        doc = HwpxDocument.new(seed=42)
        doc.add_paragraph("Normal text")
        out = tmp_path / "no_pb.hwpx"
        doc.save(str(out))

        with zipfile.ZipFile(str(out)) as zf:
            section = zf.read("Contents/section0.xml").decode("utf-8")
        # All normal paragraphs should have pageBreak="0"
        assert 'pageBreak="1"' not in section


class TestSuperSubscript:
    def test_superscript_charpr(self):
        doc = HwpxDocument.new(seed=42)
        segs = [{"text": "H"}, {"text": "2", "superscript": True}, {"text": "O"}]
        para = doc.add_mixed_paragraph(segs)
        assert para.runs[1].char_pr_id_ref == 16  # CHARPR_SUPERSCRIPT

    def test_subscript_charpr(self):
        doc = HwpxDocument.new(seed=42)
        segs = [{"text": "H"}, {"text": "2", "subscript": True}, {"text": "O"}]
        para = doc.add_mixed_paragraph(segs)
        assert para.runs[1].char_pr_id_ref == 17  # CHARPR_SUBSCRIPT

    def test_superscript_offset_in_xml(self, tmp_path):
        doc = HwpxDocument.new(seed=42)
        doc.add_mixed_paragraph([{"text": "x", "superscript": True}])
        out = tmp_path / "sup.hwpx"
        doc.save(str(out))

        with zipfile.ZipFile(str(out)) as zf:
            header = zf.read("Contents/header.xml").decode("utf-8")
        root = ET.fromstring(header)
        ns = {"hh": "http://www.hancom.co.kr/hwpml/2011/head"}
        cps = root.findall(".//hh:charPr", ns)
        cp16 = [cp for cp in cps if cp.get("id") == "16"][0]
        offset = cp16.find("hh:offset", ns)
        assert offset is not None
        assert offset.get("hangul") == "50"

    def test_subscript_offset_in_xml(self, tmp_path):
        doc = HwpxDocument.new(seed=42)
        doc.add_mixed_paragraph([{"text": "x", "subscript": True}])
        out = tmp_path / "sub.hwpx"
        doc.save(str(out))

        with zipfile.ZipFile(str(out)) as zf:
            header = zf.read("Contents/header.xml").decode("utf-8")
        root = ET.fromstring(header)
        ns = {"hh": "http://www.hancom.co.kr/hwpml/2011/head"}
        cps = root.findall(".//hh:charPr", ns)
        cp17 = [cp for cp in cps if cp.get("id") == "17"][0]
        offset = cp17.find("hh:offset", ns)
        assert offset is not None
        assert offset.get("hangul") == "-50"
