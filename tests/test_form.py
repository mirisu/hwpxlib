"""Tests for HwpxForm - HWPX template reading and form filling."""
import zipfile
from xml.etree import ElementTree as ET

import pytest

from hwpxlib.document import HwpxDocument
from hwpxlib.form import HwpxForm


def _make_template(tmp_path, seed=42):
    """Create a test template HWPX with {{placeholder}} markers."""
    doc = HwpxDocument.new(seed=seed)
    doc.add_heading("사업계획서", level=1)
    doc.add_table(
        headers=["항목", "내용"],
        rows=[
            ["사업명", "{{사업명}}"],
            ["신청기관", "{{신청기관}}"],
            ["대표자", "{{대표자}}"],
        ],
    )
    doc.add_heading("1. 사업 개요", level=2)
    doc.add_paragraph("{{사업개요}}")
    doc.add_heading("2. 추진 계획", level=2)
    doc.add_paragraph("{{추진계획}}")
    path = tmp_path / "template.hwpx"
    doc.save(str(path))
    return str(path)


class TestFormOpen:
    def test_open_reads_sections(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        assert len(form._section_paths) >= 1
        assert "Contents/section0.xml" in form._section_paths

    def test_open_reads_header(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        assert "Contents/header.xml" in form._xml_files

    def test_from_bytes(self, tmp_path):
        tpl = _make_template(tmp_path)
        with open(tpl, 'rb') as f:
            data = f.read()
        form = HwpxForm.from_bytes(data)
        assert len(form._section_paths) >= 1


class TestPlaceholders:
    def test_find_placeholders(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        phs = form.placeholders
        assert "사업명" in phs
        assert "신청기관" in phs
        assert "대표자" in phs
        assert "사업개요" in phs
        assert "추진계획" in phs

    def test_placeholder_count(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        assert len(form.placeholders) == 5


class TestFill:
    def test_fill_replaces_text(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        form.fill({
            "사업명": "AI 기반 LED 제어 시스템",
            "신청기관": "(주)영준시스템",
            "대표자": "홍길동",
            "사업개요": "본 사업은 AI를 활용합니다.",
            "추진계획": "1단계: 설계\n2단계: 개발",
        })
        text = form.get_text()
        assert "AI 기반 LED 제어 시스템" in text
        assert "(주)영준시스템" in text
        assert "홍길동" in text
        assert "{{사업명}}" not in text

    def test_fill_partial_keeps_unfilled(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        form.fill({"사업명": "테스트 사업"})
        text = form.get_text()
        assert "테스트 사업" in text
        assert "{{신청기관}}" in text  # unfilled = kept

    def test_fill_partial_blank(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        form.fill({"사업명": "테스트"}, missing="blank")
        text = form.get_text()
        assert "테스트" in text
        assert "{{신청기관}}" not in text

    def test_fill_missing_error(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        with pytest.raises(KeyError):
            form.fill({"사업명": "테스트"}, missing="error")

    def test_fill_chaining(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        result = form.fill({"사업명": "체이닝 테스트"})
        assert result is form


class TestFillTableCell:
    def test_get_table_text(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        rows = form.get_table_text(table_index=0)
        assert len(rows) == 4  # header + 3 data rows
        assert rows[0][0] == "항목"
        assert rows[1][1] == "{{사업명}}"

    def test_fill_by_cell_position(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        form.fill_table_cell(table_index=0, row=1, col=1, text="직접 입력한 사업명")
        rows = form.get_table_text(table_index=0)
        assert rows[1][1] == "직접 입력한 사업명"

    def test_fill_cell_invalid_index(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        with pytest.raises(IndexError):
            form.fill_table_cell(table_index=99, row=0, col=0, text="x")


class TestSave:
    def test_save_creates_valid_hwpx(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        form.fill({"사업명": "저장 테스트", "신청기관": "테스트기관",
                    "대표자": "김철수", "사업개요": "개요입니다",
                    "추진계획": "계획입니다"})
        out = tmp_path / "filled.hwpx"
        form.save(str(out))

        # Verify it's a valid HWPX ZIP
        assert out.exists()
        with zipfile.ZipFile(str(out)) as zf:
            names = zf.namelist()
            assert "mimetype" in names
            assert "Contents/section0.xml" in names
            assert "Contents/header.xml" in names

            # Verify filled content
            section = zf.read("Contents/section0.xml").decode("utf-8")
            assert "저장 테스트" in section
            assert "테스트기관" in section
            assert "{{사업명}}" not in section

    def test_save_mimetype_is_first_and_stored(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        out = tmp_path / "check_mime.hwpx"
        form.save(str(out))

        with zipfile.ZipFile(str(out)) as zf:
            assert zf.namelist()[0] == "mimetype"
            info = zf.getinfo("mimetype")
            assert info.compress_type == zipfile.ZIP_STORED

    def test_to_bytes(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        form.fill({"사업명": "바이트 테스트"})
        data = form.to_bytes()
        assert len(data) > 0

        # Re-open from bytes and verify
        form2 = HwpxForm.from_bytes(data)
        text = form2.get_text()
        assert "바이트 테스트" in text

    def test_roundtrip_preserves_structure(self, tmp_path):
        """Open → fill → save → reopen should preserve all non-text structure."""
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        form.fill({"사업명": "라운드트립"})
        out = tmp_path / "rt.hwpx"
        form.save(str(out))

        form2 = HwpxForm.open(str(out))
        # Should still have table structure
        rows = form2.get_table_text(table_index=0)
        assert len(rows) == 4
        assert rows[1][1] == "라운드트립"
        # Unfilled placeholders should survive
        assert "{{신청기관}}" in rows[2][1]


class TestFillByLabel:
    def test_fill_by_label_basic(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        form.fill_by_label("사업명", "라벨로 찾은 사업")
        rows = form.get_table_text(table_index=0)
        assert rows[1][1] == "라벨로 찾은 사업"

    def test_fill_by_label_contains(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        # "신청기관" is a label cell; "contains" match should find it
        form.fill_by_label("신청", "(주)테스트")
        rows = form.get_table_text(table_index=0)
        assert rows[2][1] == "(주)테스트"

    def test_fill_by_label_exact(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        form.fill_by_label("대표자", "김영희", match="exact")
        rows = form.get_table_text(table_index=0)
        assert rows[3][1] == "김영희"

    def test_fill_by_label_not_found(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        with pytest.raises(KeyError):
            form.fill_by_label("존재하지않는라벨", "값")

    def test_fill_by_label_chaining(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        result = form.fill_by_label("사업명", "체이닝")
        assert result is form


class TestGetFields:
    def test_get_fields_returns_list(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        fields = form.get_fields()
        assert isinstance(fields, list)
        assert len(fields) > 0

    def test_get_fields_has_label_keys(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        fields = form.get_fields()
        for f in fields:
            assert 'label' in f
            assert 'value' in f
            assert 'table' in f
            assert 'row' in f

    def test_get_fields_finds_table_labels(self, tmp_path):
        tpl = _make_template(tmp_path)
        form = HwpxForm.open(tpl)
        fields = form.get_fields()
        labels = [f['label'] for f in fields]
        assert "항목" in labels
