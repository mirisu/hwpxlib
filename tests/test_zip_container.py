"""Tests for HWPX ZIP container structure.

Spec: specs/01-zip-container.md
"""
import zipfile
from pathlib import Path

import pytest
from tests import NS


REQUIRED_ENTRIES = [
    "mimetype",
    "version.xml",
    "settings.xml",
    "META-INF/container.xml",
    "META-INF/manifest.xml",
    "META-INF/container.rdf",
    "Contents/content.hpf",
    "Contents/header.xml",
    "Contents/section0.xml",
    "Preview/PrvText.txt",
]


class TestZipContainer:
    def test_mimetype_is_first_entry(self, generated_hwpx_path):
        with zipfile.ZipFile(generated_hwpx_path, "r") as zf:
            first = zf.namelist()[0]
            assert first == "mimetype", f"First entry must be 'mimetype', got '{first}'"

    def test_mimetype_is_stored(self, generated_hwpx_path):
        with zipfile.ZipFile(generated_hwpx_path, "r") as zf:
            info = zf.getinfo("mimetype")
            assert info.compress_type == zipfile.ZIP_STORED, \
                "mimetype must use ZIP_STORED (no compression)"

    def test_mimetype_content(self, generated_hwpx_path):
        with zipfile.ZipFile(generated_hwpx_path, "r") as zf:
            content = zf.read("mimetype")
            assert content == b"application/hwp+zip"

    def test_all_required_entries_exist(self, generated_hwpx_path):
        with zipfile.ZipFile(generated_hwpx_path, "r") as zf:
            names = zf.namelist()
            for entry in REQUIRED_ENTRIES:
                assert entry in names, f"Missing required entry: {entry}"

    def test_xml_files_are_deflated(self, generated_hwpx_path):
        with zipfile.ZipFile(generated_hwpx_path, "r") as zf:
            for info in zf.infolist():
                if info.filename == "mimetype":
                    continue
                assert info.compress_type == zipfile.ZIP_DEFLATED, \
                    f"{info.filename} should use ZIP_DEFLATED"

    def test_reference_zip_structure_matches(self, ref_zip_metadata):
        """Verify our required entries match the reference HWPX."""
        for entry in REQUIRED_ENTRIES:
            assert entry in ref_zip_metadata, \
                f"Reference HWPX missing {entry} — check extract_reference.py"
        assert ref_zip_metadata["mimetype"] == "STORED"
