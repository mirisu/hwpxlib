"""MCP server for hwpxlib - pyhwpx-based HWPX document creation tools.

Uses FastMCP (mcp package) with stdio transport.
Run: python mcp_server/server.py
Or register: claude mcp add --transport stdio hwpxlib -- "D:/hwpxlib/venv/Scripts/python.exe" "D:/hwpxlib/mcp_server/server.py"
"""
import os
import sys

# Ensure project root is in path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hwpxlib")


# === Conversion Tools ===

@mcp.tool()
def convert_md_to_hwpx(md_path: str, output_path: str = "") -> str:
    """Markdown 파일을 HWPX(한글) 문서로 변환합니다 (pyhwpx 사용).

    Args:
        md_path: 변환할 .md 파일의 절대 경로
        output_path: 출력 .hwpx 파일 경로 (비우면 .md를 .hwpx로 대체)
    """
    from mcp_server.hwp_engine import HwpEngine

    if not os.path.exists(md_path):
        return f"Error: file not found: {md_path}"

    if not output_path:
        output_path = os.path.splitext(md_path)[0] + ".hwpx"

    try:
        with open(md_path, encoding="utf-8") as f:
            md_text = f.read()
        result = HwpEngine.create_from_md(md_text, output_path)
        return f"변환 완료: {result}"
    except Exception as e:
        return f"변환 실패: {e}"


@mcp.tool()
def convert_all_md(directory: str) -> str:
    """디렉토리 내 모든 .md 파일을 .hwpx로 일괄 변환합니다.

    Args:
        directory: .md 파일이 있는 디렉토리 절대 경로
    """
    import glob as globmod
    from mcp_server.hwp_engine import HwpEngine

    if not os.path.isdir(directory):
        return f"Error: directory not found: {directory}"

    md_files = globmod.glob(os.path.join(directory, "*.md"))
    if not md_files:
        return f"변환할 .md 파일이 없습니다: {directory}"

    results = []
    for md_path in sorted(md_files):
        out_path = os.path.splitext(md_path)[0] + ".hwpx"
        try:
            with open(md_path, encoding="utf-8") as f:
                md_text = f.read()
            HwpEngine.create_from_md(md_text, out_path)
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
    from mcp_server.hwp_engine import HwpEngine

    try:
        result = HwpEngine.create_from_md(md_content, output_path)
        return f"문서 생성 완료: {result}"
    except Exception as e:
        return f"문서 생성 실패: {e}"


@mcp.tool()
def open_in_hwp(file_path: str) -> str:
    """한글에서 파일을 열어 편집 가능 상태로 만듭니다.

    Args:
        file_path: 열 파일의 절대 경로 (.hwp, .hwpx 등)
    """
    from mcp_server.hwp_engine import HwpEngine

    if not os.path.exists(file_path):
        return f"Error: file not found: {file_path}"

    try:
        result = HwpEngine.open_visible(file_path)
        return f"한글에서 열림: {result}"
    except Exception as e:
        return f"열기 실패: {e}"


# === Document Reading Tools ===

@mcp.tool()
def read_hwpx(hwpx_path: str) -> str:
    """HWPX/HWP 문서의 텍스트 내용을 읽어서 반환합니다.

    Args:
        hwpx_path: 읽을 .hwpx/.hwp 파일의 절대 경로
    """
    from mcp_server.hwp_engine import HwpEngine

    if not os.path.exists(hwpx_path):
        return f"Error: file not found: {hwpx_path}"

    try:
        text = HwpEngine.read_document(hwpx_path)
        return text if text.strip() else "(빈 문서)"
    except Exception as e:
        return f"읽기 실패: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
