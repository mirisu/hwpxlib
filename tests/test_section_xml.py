"""Tests for section0.xml structure.

Spec: specs/08-section-structure.md, specs/09-paragraph-runs.md
"""
from xml.etree import ElementTree as ET

import pytest
from tests import NS


class TestSectionRoot:
    """Spec: specs/08-section-structure.md"""

    def test_root_tag_is_hs_sec(self, ref_section_tree):
        expected_tag = f"{{{NS['hs']}}}sec"
        assert ref_section_tree.tag == expected_tag

    def test_generated_root_tag(self, generated_hwpx_path):
        import zipfile
        with zipfile.ZipFile(generated_hwpx_path, "r") as zf:
            xml = zf.read("Contents/section0.xml").decode("utf-8")
        root = ET.fromstring(xml)
        expected_tag = f"{{{NS['hs']}}}sec"
        assert root.tag == expected_tag

    def test_section_has_namespaces(self, generated_hwpx_path):
        import zipfile
        with zipfile.ZipFile(generated_hwpx_path, "r") as zf:
            xml = zf.read("Contents/section0.xml").decode("utf-8")
        # Check all three required namespace declarations
        assert 'xmlns:hp=' in xml
        assert 'xmlns:hs=' in xml
        assert 'xmlns:hc=' in xml


class TestSecPr:
    """First paragraph must contain secPr."""

    def test_first_para_has_secpr(self, ref_section_tree):
        first_p = ref_section_tree.find(f"{{{NS['hp']}}}p")
        assert first_p is not None, "No paragraphs in section"
        first_run = first_p.find(f"{{{NS['hp']}}}run")
        assert first_run is not None, "No run in first paragraph"
        sec_pr = first_run.find(f"{{{NS['hp']}}}secPr")
        assert sec_pr is not None, "First run must contain secPr"

    def test_generated_first_para_has_secpr(self, generated_hwpx_path):
        import zipfile
        with zipfile.ZipFile(generated_hwpx_path, "r") as zf:
            xml = zf.read("Contents/section0.xml").decode("utf-8")
        root = ET.fromstring(xml)
        first_p = root.find(f"{{{NS['hp']}}}p")
        first_run = first_p.find(f"{{{NS['hp']}}}run")
        sec_pr = first_run.find(f"{{{NS['hp']}}}secPr")
        assert sec_pr is not None, "Generated first run must contain secPr"

    def test_secpr_page_dimensions(self, ref_section_tree):
        sec_pr = ref_section_tree.find(f".//{{{NS['hp']}}}secPr")
        page_pr = sec_pr.find(f"{{{NS['hp']}}}pagePr")
        assert page_pr.get("width") == "59530"
        assert page_pr.get("height") == "84190"
        assert page_pr.get("landscape") == "WIDELY"

    def test_generated_page_dimensions(self, generated_hwpx_path):
        import zipfile
        with zipfile.ZipFile(generated_hwpx_path, "r") as zf:
            xml = zf.read("Contents/section0.xml").decode("utf-8")
        root = ET.fromstring(xml)
        sec_pr = root.find(f".//{{{NS['hp']}}}secPr")
        page_pr = sec_pr.find(f"{{{NS['hp']}}}pagePr")
        assert page_pr.get("width") == "59530"
        assert page_pr.get("height") == "84190"


class TestColPr:
    """First paragraph must contain colPr after secPr."""

    def test_first_para_has_colpr(self, ref_section_tree):
        first_p = ref_section_tree.find(f"{{{NS['hp']}}}p")
        first_run = first_p.find(f"{{{NS['hp']}}}run")
        ctrl = first_run.find(f"{{{NS['hp']}}}ctrl")
        assert ctrl is not None, "First run must contain ctrl"
        col_pr = ctrl.find(f"{{{NS['hp']}}}colPr")
        assert col_pr is not None, "ctrl must contain colPr"

    def test_generated_first_para_has_colpr(self, generated_hwpx_path):
        import zipfile
        with zipfile.ZipFile(generated_hwpx_path, "r") as zf:
            xml = zf.read("Contents/section0.xml").decode("utf-8")
        root = ET.fromstring(xml)
        first_p = root.find(f"{{{NS['hp']}}}p")
        first_run = first_p.find(f"{{{NS['hp']}}}run")
        ctrl = first_run.find(f"{{{NS['hp']}}}ctrl")
        assert ctrl is not None
        col_pr = ctrl.find(f"{{{NS['hp']}}}colPr")
        assert col_pr is not None


class TestParagraphRuns:
    """Spec: specs/09-paragraph-runs.md"""

    def test_paragraph_has_required_attrs(self, ref_section_tree):
        paragraphs = ref_section_tree.findall(f"{{{NS['hp']}}}p")
        for p in paragraphs[:5]:
            assert p.get("paraPrIDRef") is not None
            assert p.get("styleIDRef") is not None
            assert p.get("pageBreak") is not None
            assert p.get("columnBreak") is not None
            assert p.get("merged") is not None

    def test_run_has_charpr_ref(self, ref_section_tree):
        runs = ref_section_tree.findall(f".//{{{NS['hp']}}}run")
        for run in runs[:10]:
            assert run.get("charPrIDRef") is not None
