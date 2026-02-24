"""Shared fixtures for hwpxlib tests.

Loads reference XML from extracted HWPX files and generates
hwpxlib output for comparison.
"""
import os
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

# Ensure hwpxlib is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

REFERENCE_DIR = Path(__file__).parent.parent / "reference" / "extracted" / "colorlight"
PATENT_DIR = Path(__file__).parent.parent / "reference" / "extracted" / "patent"


@pytest.fixture
def ref_header_xml() -> str:
    """Return the reference header.xml content as string."""
    path = REFERENCE_DIR / "Contents" / "header.xml"
    return path.read_text(encoding="utf-8")


@pytest.fixture
def ref_section_xml() -> str:
    """Return the reference section0.xml content as string."""
    path = REFERENCE_DIR / "Contents" / "section0.xml"
    return path.read_text(encoding="utf-8")


@pytest.fixture
def ref_version_xml() -> str:
    path = REFERENCE_DIR / "version.xml"
    return path.read_text(encoding="utf-8")


@pytest.fixture
def ref_settings_xml() -> str:
    path = REFERENCE_DIR / "settings.xml"
    return path.read_text(encoding="utf-8")


@pytest.fixture
def ref_zip_metadata() -> dict:
    """Return ZIP metadata as dict of {filename: compress_method}."""
    path = REFERENCE_DIR / "_zip_metadata.txt"
    result = {}
    for line in path.read_text(encoding="utf-8").strip().split("\n"):
        parts = line.split("\t")
        result[parts[0]] = parts[1]
    return result


@pytest.fixture
def ref_header_tree(ref_header_xml) -> ET.Element:
    """Parse reference header.xml into ElementTree."""
    return ET.fromstring(ref_header_xml)


@pytest.fixture
def ref_section_tree(ref_section_xml) -> ET.Element:
    """Parse reference section0.xml (first 2000 chars) into ElementTree."""
    return ET.fromstring(ref_section_xml)


@pytest.fixture
def generated_hwpx_path(tmp_path) -> Path:
    """Generate a test HWPX file using hwpxlib and return its path."""
    from hwpxlib.document import HwpxDocument

    doc = HwpxDocument.new()
    doc.add_heading("Test Document", level=1)
    doc.add_paragraph("This is a test paragraph.")
    doc.add_paragraph("Bold text", bold=True)
    doc.add_table(["Col A", "Col B"], [["1", "2"], ["3", "4"]])
    doc.add_code_block("print('hello')", language="python")
    doc.add_bullet_list(["Item 1", "Item 2"])

    out = tmp_path / "test_output.hwpx"
    doc.save(str(out))
    return out


@pytest.fixture
def generated_header_xml() -> str:
    """Generate header.xml from hwpxlib defaults."""
    from hwpxlib.template import (
        default_font_faces, default_border_fills,
        default_char_prs, default_para_prs, default_styles,
    )
    from hwpxlib.xml_writer import write_header_xml

    return write_header_xml(
        font_faces=default_font_faces(),
        border_fills=default_border_fills(),
        char_prs=default_char_prs(),
        para_prs=default_para_prs(),
        styles=default_styles(),
    )


@pytest.fixture
def generated_header_tree(generated_header_xml) -> ET.Element:
    """Parse generated header.xml into ElementTree."""
    return ET.fromstring(generated_header_xml)


