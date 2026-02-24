"""Standalone XML diff tool: compare hwpxlib output against reference XML.

Usage:
    python tests/validate_xml.py [--verbose]

Exit code 0 = all match, 1 = differences found.
This script serves as a backpressure gate for the Ralph build loop.
"""
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

REFERENCE_DIR = PROJECT_ROOT / "reference" / "extracted" / "colorlight"


def normalize_xml(xml_str: str) -> ET.Element:
    """Parse XML and return normalized ElementTree."""
    return ET.fromstring(xml_str)


def compare_elements(ref: ET.Element, gen: ET.Element, path: str = "") -> list:
    """Recursively compare two XML elements, returning list of differences."""
    diffs = []
    current = f"{path}/{ref.tag}" if path else ref.tag

    # Compare tag
    if ref.tag != gen.tag:
        diffs.append(f"TAG MISMATCH at {current}: ref={ref.tag} gen={gen.tag}")
        return diffs

    # Compare attributes
    ref_attrs = dict(ref.attrib)
    gen_attrs = dict(gen.attrib)

    # Skip 'id' attributes that are random IDs (like subList id, tbl id)
    skip_attrs = set()
    if ref.tag.endswith("}tbl") or ref.tag.endswith("}subList"):
        skip_attrs.add("id")

    for key in sorted(set(ref_attrs.keys()) | set(gen_attrs.keys())):
        if key in skip_attrs:
            continue
        ref_val = ref_attrs.get(key)
        gen_val = gen_attrs.get(key)
        if ref_val != gen_val:
            diffs.append(f"ATTR {current}@{key}: ref={ref_val!r} gen={gen_val!r}")

    # Compare text
    ref_text = (ref.text or "").strip()
    gen_text = (gen.text or "").strip()
    if ref_text != gen_text:
        diffs.append(f"TEXT {current}: ref={ref_text!r} gen={gen_text!r}")

    # Compare children count
    ref_children = list(ref)
    gen_children = list(gen)
    if len(ref_children) != len(gen_children):
        diffs.append(
            f"CHILDREN COUNT {current}: ref={len(ref_children)} gen={len(gen_children)}"
        )
        # Compare as many as possible
        for i, (rc, gc) in enumerate(zip(ref_children, gen_children)):
            diffs.extend(compare_elements(rc, gc, f"{current}[{i}]"))
    else:
        for i, (rc, gc) in enumerate(zip(ref_children, gen_children)):
            diffs.extend(compare_elements(rc, gc, f"{current}[{i}]"))

    return diffs


def validate_header():
    """Compare generated header.xml against reference."""
    from hwpxlib.template import (
        default_font_faces, default_border_fills,
        default_char_prs, default_para_prs, default_styles,
    )
    from hwpxlib.xml_writer import write_header_xml

    gen_xml = write_header_xml(
        font_faces=default_font_faces(),
        border_fills=default_border_fills(),
        char_prs=default_char_prs(),
        para_prs=default_para_prs(),
        styles=default_styles(),
    )
    ref_xml = (REFERENCE_DIR / "Contents" / "header.xml").read_text(encoding="utf-8")

    ref_tree = normalize_xml(ref_xml)
    gen_tree = normalize_xml(gen_xml)

    return compare_elements(ref_tree, gen_tree)


def validate_meta():
    """Compare generated meta files against reference."""
    from hwpxlib.xml_writer import write_version_xml, write_settings_xml

    diffs = []

    # version.xml
    gen = write_version_xml()
    ref = (REFERENCE_DIR / "version.xml").read_text(encoding="utf-8")
    ref_tree = normalize_xml(ref)
    gen_tree = normalize_xml(gen)
    diffs.extend(compare_elements(ref_tree, gen_tree))

    # settings.xml
    gen = write_settings_xml()
    ref = (REFERENCE_DIR / "settings.xml").read_text(encoding="utf-8")
    ref_tree = normalize_xml(ref)
    gen_tree = normalize_xml(gen)
    diffs.extend(compare_elements(ref_tree, gen_tree))

    return diffs


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    all_diffs = []

    print("=== Validating header.xml ===")
    header_diffs = validate_header()
    all_diffs.extend(header_diffs)
    if header_diffs:
        print(f"  {len(header_diffs)} difference(s) found")
        if verbose:
            for d in header_diffs:
                print(f"    {d}")
    else:
        print("  PASS")

    print("\n=== Validating meta files ===")
    meta_diffs = validate_meta()
    all_diffs.extend(meta_diffs)
    if meta_diffs:
        print(f"  {len(meta_diffs)} difference(s) found")
        if verbose:
            for d in meta_diffs:
                print(f"    {d}")
    else:
        print("  PASS")

    print(f"\n{'='*40}")
    if all_diffs:
        print(f"FAIL: {len(all_diffs)} total difference(s)")
        sys.exit(1)
    else:
        print("ALL PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
