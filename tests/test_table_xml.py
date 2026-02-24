"""Tests for table XML structure.

Spec: specs/10-tables.md
"""
from xml.etree import ElementTree as ET

import pytest
from tests import NS


class TestTableStructure:
    def test_table_exists_in_reference(self, ref_section_tree):
        tables = ref_section_tree.findall(f".//{{{NS['hp']}}}tbl")
        assert len(tables) > 0, "Reference section must have at least one table"

    def test_table_has_required_attrs(self, ref_section_tree):
        tbl = ref_section_tree.find(f".//{{{NS['hp']}}}tbl")
        for attr in ["id", "rowCnt", "colCnt", "cellSpacing", "borderFillIDRef"]:
            assert tbl.get(attr) is not None, f"Table missing attr: {attr}"

    def test_table_has_sz_and_pos(self, ref_section_tree):
        tbl = ref_section_tree.find(f".//{{{NS['hp']}}}tbl")
        sz = tbl.find(f"{{{NS['hp']}}}sz")
        pos = tbl.find(f"{{{NS['hp']}}}pos")
        assert sz is not None, "Table must have hp:sz"
        assert pos is not None, "Table must have hp:pos"

    def test_table_rows_and_cells(self, ref_section_tree):
        tbl = ref_section_tree.find(f".//{{{NS['hp']}}}tbl")
        rows = tbl.findall(f"{{{NS['hp']}}}tr")
        assert len(rows) > 0, "Table must have at least one row"
        first_row = rows[0]
        cells = first_row.findall(f"{{{NS['hp']}}}tc")
        assert len(cells) > 0, "Row must have at least one cell"

    def test_cell_has_sublist(self, ref_section_tree):
        tc = ref_section_tree.find(f".//{{{NS['hp']}}}tc")
        sublist = tc.find(f"{{{NS['hp']}}}subList")
        assert sublist is not None, "Cell must contain hp:subList"
        para = sublist.find(f"{{{NS['hp']}}}p")
        assert para is not None, "subList must contain at least one hp:p"

    def test_cell_has_addr_span_sz(self, ref_section_tree):
        tc = ref_section_tree.find(f".//{{{NS['hp']}}}tc")
        assert tc.find(f"{{{NS['hp']}}}cellAddr") is not None
        assert tc.find(f"{{{NS['hp']}}}cellSpan") is not None
        assert tc.find(f"{{{NS['hp']}}}cellSz") is not None
        assert tc.find(f"{{{NS['hp']}}}cellMargin") is not None


class TestGeneratedTable:
    def test_generated_table_structure(self, generated_hwpx_path):
        import zipfile
        with zipfile.ZipFile(generated_hwpx_path, "r") as zf:
            xml = zf.read("Contents/section0.xml").decode("utf-8")
        root = ET.fromstring(xml)
        tbl = root.find(f".//{{{NS['hp']}}}tbl")
        assert tbl is not None, "Generated section must have a table"

        # Check required attrs
        assert tbl.get("rowCnt") is not None
        assert tbl.get("colCnt") is not None

        # Check rows
        rows = tbl.findall(f"{{{NS['hp']}}}tr")
        assert len(rows) == 3  # 1 header + 2 data rows

        # Check header cell
        first_cell = rows[0].find(f"{{{NS['hp']}}}tc")
        assert first_cell.get("header") == "1"
        assert first_cell.get("borderFillIDRef") == "4"  # table header fill

    def test_generated_table_cell_structure(self, generated_hwpx_path):
        import zipfile
        with zipfile.ZipFile(generated_hwpx_path, "r") as zf:
            xml = zf.read("Contents/section0.xml").decode("utf-8")
        root = ET.fromstring(xml)
        tc = root.find(f".//{{{NS['hp']}}}tc")

        # Must have: subList, cellAddr, cellSpan, cellSz, cellMargin
        assert tc.find(f"{{{NS['hp']}}}subList") is not None
        assert tc.find(f"{{{NS['hp']}}}cellAddr") is not None
        assert tc.find(f"{{{NS['hp']}}}cellSpan") is not None
        assert tc.find(f"{{{NS['hp']}}}cellSz") is not None
        assert tc.find(f"{{{NS['hp']}}}cellMargin") is not None
