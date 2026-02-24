"""Extract XML files from reference HWPX documents for comparison testing.

Usage:
    python reference/extract_reference.py

Extracts all XML/text files from the two reference HWPX files into
reference/extracted/colorlight/ and reference/extracted/patent/.
"""
import os
import sys
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

REFERENCES = {
    "colorlight": Path(r"D:/(주)영준시스템/디아이디특허/Colorlight_5A-75B_오픈소스_활용_보고서.hwpx"),
    "patent": Path(r"D:/(주)영준시스템/디아이디특허/특허_10-2674320_요약본.hwpx"),
}

OUTPUT_BASE = SCRIPT_DIR / "extracted"


def extract_hwpx(name: str, hwpx_path: Path):
    """Extract all entries from an HWPX (ZIP) file."""
    out_dir = OUTPUT_BASE / name
    out_dir.mkdir(parents=True, exist_ok=True)

    if not hwpx_path.exists():
        print(f"[SKIP] {hwpx_path} not found")
        return

    with zipfile.ZipFile(hwpx_path, "r") as zf:
        for entry in zf.namelist():
            data = zf.read(entry)
            dest = out_dir / entry
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            print(f"  {entry} ({len(data)} bytes)")

        # Also write ZIP entry metadata
        meta_lines = []
        for info in zf.infolist():
            compress = "STORED" if info.compress_type == zipfile.ZIP_STORED else "DEFLATED"
            meta_lines.append(
                f"{info.filename}\t{compress}\t{info.file_size}\t{info.compress_size}"
            )
        meta_path = out_dir / "_zip_metadata.txt"
        meta_path.write_text("\n".join(meta_lines), encoding="utf-8")
        print(f"  _zip_metadata.txt (metadata)")


def main():
    for name, path in REFERENCES.items():
        print(f"\n=== Extracting {name}: {path} ===")
        extract_hwpx(name, path)

    print("\nDone. Reference XML files are in reference/extracted/")


if __name__ == "__main__":
    main()
