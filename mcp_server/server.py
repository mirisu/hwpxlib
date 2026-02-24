"""MCP server for hwpxlib - HWPX document creation tools.

Uses hwpxlib core library (zero external dependencies, cross-platform).
Fallback to pyhwpx COM automation only for open_in_hwp on Windows.

Run: python mcp_server/server.py
Or register: claude mcp add --transport stdio hwpxlib -- python mcp_server/server.py
"""
import os
import sys
import zipfile
import xml.etree.ElementTree as ET

# Allowed file extensions for document operations
_DOCUMENT_EXTENSIONS = {'.hwp', '.hwpx', '.hwt'}
_INPUT_EXTENSIONS = {'.md', '.txt'}


def _validate_document_path(path: str) -> str:
    """Validate that a path points to a HWP/HWPX document file.

    Returns the absolute path if valid, raises ValueError otherwise.
    """
    abspath = os.path.abspath(path)
    ext = os.path.splitext(abspath)[1].lower()
    if ext not in _DOCUMENT_EXTENSIONS:
        raise ValueError(
            f"파일 확장자가 올바르지 않습니다: {ext!r}. "
            f"허용: {', '.join(sorted(_DOCUMENT_EXTENSIONS))}"
        )
    return abspath


def _validate_output_path(path: str) -> str:
    """Validate that an output path has a valid document extension.

    Returns the absolute path if valid, raises ValueError otherwise.
    """
    abspath = os.path.abspath(path)
    ext = os.path.splitext(abspath)[1].lower()
    if ext not in _DOCUMENT_EXTENSIONS:
        raise ValueError(
            f"출력 파일 확장자가 올바르지 않습니다: {ext!r}. "
            f"허용: {', '.join(sorted(_DOCUMENT_EXTENSIONS))}"
        )
    return abspath


# Ensure project root is in path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hwpxlib")


# === Conversion Tools (hwpxlib core — cross-platform) ===

@mcp.tool()
def convert_md_to_hwpx(md_path: str, output_path: str = "") -> str:
    """Markdown 파일을 HWPX(한글) 문서로 변환합니다.

    Args:
        md_path: 변환할 .md 파일의 절대 경로
        output_path: 출력 .hwpx 파일 경로 (비우면 .md를 .hwpx로 대체)
    """
    from converters.md2hwpx import convert_md_file

    md_path = os.path.abspath(md_path)
    if not os.path.exists(md_path):
        return f"Error: file not found: {md_path}"

    ext = os.path.splitext(md_path)[1].lower()
    if ext not in _INPUT_EXTENSIONS:
        return f"Error: 입력 파일이 마크다운이 아닙니다: {ext}"

    if not output_path:
        output_path = os.path.splitext(md_path)[0] + ".hwpx"

    try:
        output_path = _validate_output_path(output_path)
        result = convert_md_file(md_path, output_path)
        return f"변환 완료: {result}"
    except (ValueError, Exception) as e:
        return f"변환 실패: {e}"


@mcp.tool()
def convert_all_md(directory: str) -> str:
    """디렉토리 내 모든 .md 파일을 .hwpx로 일괄 변환합니다.

    Args:
        directory: .md 파일이 있는 디렉토리 절대 경로
    """
    import glob as globmod
    from converters.md2hwpx import convert_md_file

    if not os.path.isdir(directory):
        return f"Error: directory not found: {directory}"

    md_files = globmod.glob(os.path.join(directory, "*.md"))
    if not md_files:
        return f"변환할 .md 파일이 없습니다: {directory}"

    results = []
    for md_path in sorted(md_files):
        out_path = os.path.splitext(md_path)[0] + ".hwpx"
        try:
            convert_md_file(md_path, out_path)
            results.append(f"OK: {os.path.basename(out_path)}")
        except Exception as e:
            results.append(f"FAIL: {os.path.basename(md_path)} - {e}")

    return f"{len(md_files)}개 파일 변환 완료:\n" + "\n".join(results)


# === Document Creation Tools ===

@mcp.tool()
def create_document_from_md(md_content: str, output_path: str) -> str:
    """Markdown 텍스트로 HWPX 문서를 직접 생성합니다.

    Args:
        md_content: Markdown 형식의 텍스트 내용
        output_path: 출력 .hwpx 파일의 절대 경로
    """
    from converters.md2hwpx import convert_md_to_hwpx

    try:
        output_path = _validate_output_path(output_path)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        doc = convert_md_to_hwpx(md_content)
        doc.save(output_path)
        return f"문서 생성 완료: {os.path.abspath(output_path)}"
    except (ValueError, Exception) as e:
        return f"문서 생성 실패: {e}"


@mcp.tool()
def open_in_hwp(file_path: str) -> str:
    """한글에서 파일을 열어 편집 가능 상태로 만듭니다.

    Args:
        file_path: 열 파일의 절대 경로 (.hwp, .hwpx 등)
    """
    if not os.path.exists(file_path):
        return f"Error: file not found: {file_path}"

    try:
        validated_path = _validate_document_path(file_path)
        os.startfile(validated_path)
        return f"한글에서 열림: {validated_path}"
    except (ValueError, Exception) as e:
        return f"열기 실패: {e}"


# === Document Reading Tools ===

def _extract_text_from_hwpx(hwpx_path: str) -> str:
    """Extract plain text from a HWPX file by parsing section XML."""
    ns = {"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}
    texts = []

    with zipfile.ZipFile(hwpx_path, 'r') as zf:
        # Find all section files
        section_files = sorted(
            n for n in zf.namelist()
            if n.startswith("Contents/section") and n.endswith(".xml")
        )
        for section_file in section_files:
            xml_data = zf.read(section_file).decode("utf-8")
            root = ET.fromstring(xml_data)
            for t_elem in root.iter(f"{{{ns['hp']}}}t"):
                if t_elem.text:
                    texts.append(t_elem.text)

    return "\n".join(texts)


@mcp.tool()
def read_hwpx(hwpx_path: str) -> str:
    """HWPX/HWP 문서의 텍스트 내용을 읽어서 반환합니다.

    Args:
        hwpx_path: 읽을 .hwpx/.hwp 파일의 절대 경로
    """
    if not os.path.exists(hwpx_path):
        return f"Error: file not found: {hwpx_path}"

    try:
        validated_path = _validate_document_path(hwpx_path)
        ext = os.path.splitext(validated_path)[1].lower()

        if ext == '.hwpx':
            text = _extract_text_from_hwpx(validated_path)
            return text if text.strip() else "(빈 문서)"
        else:
            # .hwp (binary format) — try pyhwpx if available
            try:
                from mcp_server.hwp_engine import HwpEngine
                text = HwpEngine.read_document(validated_path)
                return text if text.strip() else "(빈 문서)"
            except ImportError:
                return "Error: .hwp 바이너리 형식은 pyhwpx가 필요합니다 (Windows 전용)"
    except (ValueError, Exception) as e:
        return f"읽기 실패: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
