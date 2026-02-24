#!/usr/bin/env python3
"""CLI entry point: Convert Markdown files to HWPX (한글) documents.

Usage:
    python md2hwpx.py input.md                  # Convert single file
    python md2hwpx.py input.md -o output.hwpx   # Specify output path
    python md2hwpx.py --all                     # Convert all .md in current dir
    python md2hwpx.py --all --dir /path/to/dir  # Convert all .md in specified dir
"""
import argparse
import os
import sys
import glob


def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown files to HWPX (한글) documents"
    )
    parser.add_argument("input", nargs="?", help="Input .md file path")
    parser.add_argument("-o", "--output", help="Output .hwpx file path")
    parser.add_argument("--all", action="store_true",
                        help="Convert all .md files in directory")
    parser.add_argument("--dir", default=".",
                        help="Directory for --all mode (default: current)")

    args = parser.parse_args()

    # Add project root to path
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from converters.md2hwpx import convert_md_file

    if args.all:
        # Convert all .md files in directory
        md_dir = os.path.abspath(args.dir)
        md_files = glob.glob(os.path.join(md_dir, "*.md"))
        if not md_files:
            print(f"No .md files found in {md_dir}")
            return 1

        print(f"Converting {len(md_files)} files in {md_dir}...")
        for md_path in sorted(md_files):
            try:
                result = convert_md_file(md_path)
                basename = os.path.basename(result)
                print(f"  OK: {basename}")
            except Exception as e:
                basename = os.path.basename(md_path)
                print(f"  FAIL: {basename} - {e}")

        print("Done.")
        return 0

    if not args.input:
        parser.print_help()
        return 1

    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print(f"Error: file not found: {input_path}")
        return 1

    output_path = args.output or ""
    try:
        result = convert_md_file(input_path, output_path)
        print(f"Created: {result}")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
