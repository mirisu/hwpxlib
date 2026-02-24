# hwpxlib

Python library for creating HWPX (한글) documents — zero external dependencies.

HWPX는 한컴오피스 한글의 개방형 문서 포맷(OWPML)입니다. hwpxlib은 Python 표준 라이브러리만으로 HWPX 파일을 직접 생성합니다.

## Features

- **Zero-dependency core** — `hwpxlib/` 패키지는 Python 표준 라이브러리만 사용
- **Markdown to HWPX** — 마크다운 파일을 한글 문서로 변환
- **Fluent builder API** — 체이닝 가능한 문서 생성 인터페이스
- **Deterministic output** — `seed` 파라미터로 동일한 바이트 출력 보장
- **MCP server** — Claude Code에서 바로 사용 가능한 MCP 도구 제공
- **Comprehensive tests** — 75개 테스트 (XML 구조 + 보안)

## Installation

```bash
git clone https://github.com/mirisu/hwpxlib.git
cd hwpxlib
pip install -e .
```

MCP 서버를 사용하려면:

```bash
pip install -e ".[mcp]"
```

## Quick Start

### Python API

```python
from hwpxlib import HwpxDocument

doc = HwpxDocument.new()
doc.add_heading("보고서 제목", level=1)
doc.add_paragraph("본문 텍스트입니다.")
doc.add_table(
    headers=["항목", "설명"],
    rows=[["A", "첫 번째"], ["B", "두 번째"]],
)
doc.save("output.hwpx")
```

### Fluent Builder

```python
from hwpxlib import HwpxDocument

(HwpxDocument.new()
    .builder()
    .heading("제목", level=1)
    .paragraph("본문")
    .paragraph("굵은 텍스트", bold=True)
    .code_block("print('hello')", language="python")
    .bullet_list(["항목 1", "항목 2", "항목 3"])
    .table(
        headers=["이름", "값"],
        rows=[["A", "1"], ["B", "2"]],
    )
    .save("output.hwpx"))
```

### Markdown 변환

```python
from converters.md2hwpx import convert_md_file

convert_md_file("input.md", "output.hwpx")
```

### CLI

```bash
# 단일 파일 변환
python md2hwpx.py input.md

# 출력 경로 지정
python md2hwpx.py input.md -o output.hwpx

# 디렉토리 내 모든 .md 파일 일괄 변환
python md2hwpx.py --all --dir /path/to/markdown
```

## Supported Markdown Elements

| 요소 | 문법 |
|------|------|
| 제목 (H1~H6) | `# Heading` ~ `###### Heading` |
| 굵게 | `**bold**` |
| 기울임 | `*italic*` |
| 인라인 코드 | `` `code` `` |
| 코드 블록 | ` ```python ... ``` ` |
| 표 | `\| A \| B \|` 파이프 테이블 |
| 글머리 기호 | `- item` 또는 `* item` |
| 수평선 | `---` |
| 인용 | `> blockquote` |

## Project Structure

```
hwpxlib/
├── hwpxlib/           # Core library (stdlib only)
│   ├── document.py    #   HwpxDocument — main API
│   ├── builder.py     #   HwpxBuilder — fluent API
│   ├── xml_writer.py  #   XML serialization
│   ├── template.py    #   Default styles/fonts
│   ├── package.py     #   ZIP container
│   ├── constants.py   #   Namespaces, units, IDs
│   └── models/        #   Dataclasses (body, head, meta)
├── converters/        # Markdown → HWPX
│   ├── md_parser.py   #   Regex-based MD parser → AST
│   └── md2hwpx.py     #   AST → HwpxDocument
├── mcp_server/        # MCP server (optional, needs mcp>=1.26.0)
│   ├── server.py      #   FastMCP tools
│   └── hwp_engine.py  #   pyhwpx COM engine
├── tests/             # 75 tests
├── specs/             # HWPX format specs (11 files)
└── reference/         # Reference HWPX for comparison
```

## MCP Server

Claude Code에서 한글 문서를 직접 생성/읽기할 수 있는 MCP 서버:

```bash
# 등록
claude mcp add --transport stdio hwpxlib -- \
  "D:/hwpxlib/venv/Scripts/python.exe" "D:/hwpxlib/mcp_server/server.py"
```

제공 도구:

| 도구 | 설명 |
|------|------|
| `convert_md_to_hwpx` | .md 파일 → .hwpx 변환 |
| `convert_all_md` | 디렉토리 내 .md 일괄 변환 |
| `create_document_from_md` | 마크다운 텍스트로 직접 생성 |
| `open_in_hwp` | 한글에서 파일 열기 |
| `read_hwpx` | HWPX 문서 텍스트 추출 |

## Deterministic Output

테스트나 CI에서 동일한 출력이 필요하면 `seed`를 지정:

```python
doc = HwpxDocument.new(seed=42)
# ... 동일한 내용 → 항상 동일한 바이트
doc.save("output.hwpx")
```

## Tests

```bash
# 전체 테스트 실행
python -m pytest tests/ -v

# XML 참조 비교 검증
python tests/validate_xml.py
```

## HWPX Format

HWPX는 ZIP 기반 개방형 문서 포맷입니다:

- `mimetype` — `application/hwp+zip` (비압축, 첫 번째 엔트리)
- `Contents/header.xml` — 글꼴, 스타일, 문자/문단 속성
- `Contents/section0.xml` — 문서 본문 (문단, 표, 텍스트)
- `META-INF/` — 컨테이너 메타데이터
- `Preview/PrvText.txt` — 미리보기 텍스트

## License

MIT
