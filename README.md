# hwpxlib

Python library for creating HWPX (한글) documents — zero external dependencies.

HWPX는 한컴오피스 한글의 개방형 문서 포맷(OWPML)입니다. hwpxlib은 Python 표준 라이브러리만으로 HWPX 파일을 직접 생성합니다.

## Features

- **Zero-dependency core** — `hwpxlib/` 패키지는 Python 표준 라이브러리만 사용
- **Markdown to HWPX** — 마크다운 파일을 한글 문서로 변환
- **Fluent builder API** — 체이닝 가능한 문서 생성 인터페이스
- **Page setup** — 페이지 크기(A4/Letter/A3), 방향(가로/세로), 마진 설정
- **Style customization** — 글꼴, 크기, 색상, 줄간격 커스터마이징
- **Image embedding** — PNG/JPEG/GIF/BMP 이미지 삽입
- **Nested lists** — 최대 3단계 중첩 불릿/번호 목록
- **Deterministic output** — `seed` 파라미터로 동일한 바이트 출력 보장
- **MCP server** — Claude Code에서 바로 사용 가능한 MCP 도구 제공

## Installation

```bash
pip install hwpxlib
```

또는 소스에서 설치:

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

### Page Setup

```python
from hwpxlib import HwpxDocument, PageSetup

# A4 가로
doc = HwpxDocument.new()
doc.set_page_setup(PageSetup.a4(landscape=True))

# US Letter
doc = HwpxDocument.new()
doc.set_page_setup(PageSetup.letter())

# 커스텀 마진 (HWPUNIT: 1mm ≈ 283)
from hwpxlib.constants import mm_to_hwpunit
doc.set_page_setup(
    margin_left=mm_to_hwpunit(15),
    margin_right=mm_to_hwpunit(15),
)
```

### Style Customization

```python
from hwpxlib import HwpxDocument, StyleConfig

doc = HwpxDocument.new()
doc.set_style(StyleConfig(
    font_body="맑은 고딕",
    font_code="D2Coding",
    font_size_body=1100,          # 11pt (HWPUNIT: 1pt = 100)
    color_heading="#2E74B5",
    color_table_header_bg="#2E74B5",
    line_spacing=180,             # 180%
))
```

### Image Embedding

```python
doc = HwpxDocument.new()
doc.add_heading("이미지 포함 문서", level=1)
doc.add_image("photo.png")
doc.add_image(image_data=raw_bytes, width=15000, height=10000)
doc.save("with_image.hwpx")
```

### Lists (Nested)

```python
doc = HwpxDocument.new()

# 불릿 리스트 (중첩)
doc.add_bullet_list([
    ("항목 A", 0),          # 레벨 0
    ("하위 항목 A-1", 1),   # 레벨 1
    ("더 하위 A-1-a", 2),   # 레벨 2
    ("항목 B", 0),
])

# 번호 리스트
doc.add_ordered_list(["첫째", "둘째", "셋째"])

# 간단한 리스트 (레벨 지정 없이)
doc.add_bullet_list(["항목 1", "항목 2", "항목 3"])
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
| 굵게+기울임 | `***bold italic***` |
| 인라인 코드 | `` `code` `` |
| 코드 블록 | ` ```python ... ``` ` |
| 표 | `\| A \| B \|` 파이프 테이블 |
| 글머리 기호 | `- item` (중첩: 들여쓰기 2칸) |
| 번호 목록 | `1. item` (중첩: 들여쓰기 2칸) |
| 수평선 | `---` |
| 인용 | `> blockquote` |

## API Reference

### HwpxDocument

| 메서드 | 설명 |
|--------|------|
| `HwpxDocument.new(seed=None)` | 새 문서 생성 |
| `.set_page_setup(PageSetup)` | 페이지 크기/방향/마진 설정 |
| `.set_style(StyleConfig)` | 글꼴/크기/색상/줄간격 설정 |
| `.add_heading(text, level)` | 제목 추가 (1~6) |
| `.add_paragraph(text, bold, italic)` | 본문 단락 추가 |
| `.add_mixed_paragraph(segments)` | 혼합 서식 단락 |
| `.add_table(headers, rows)` | 표 추가 |
| `.add_code_block(code, language)` | 코드 블록 추가 |
| `.add_bullet_list(items)` | 불릿 목록 (중첩 지원) |
| `.add_ordered_list(items)` | 번호 목록 (중첩 지원) |
| `.add_image(path/data)` | 이미지 삽입 |
| `.add_horizontal_rule()` | 수평선 추가 |
| `.save(path)` | .hwpx 파일 저장 |
| `.to_bytes()` | 바이트 반환 |

### PageSetup

| 메서드/속성 | 설명 |
|-------------|------|
| `PageSetup.a4(landscape=False)` | A4 (210×297mm) |
| `PageSetup.letter(landscape=False)` | US Letter (216×279mm) |
| `PageSetup.a3(landscape=False)` | A3 (297×420mm) |
| `.usable_width` | 콘텐츠 영역 폭 (마진 제외) |

### StyleConfig

| 속성 | 기본값 | 설명 |
|------|--------|------|
| `font_body` | 나눔고딕 | 본문 글꼴 |
| `font_code` | 나눔고딕코딩 | 코드 글꼴 |
| `font_size_body` | 1000 (10pt) | 본문 크기 |
| `font_size_h1`~`h6` | 2200~1000 | 제목 크기 |
| `color_heading` | #323E4F | 제목 색상 |
| `color_code_text` | #E74C3C | 인라인 코드 색상 |
| `color_table_header_bg` | #4472C4 | 표 헤더 배경색 |
| `line_spacing` | 160 (160%) | 기본 줄간격 |

## Project Structure

```
hwpxlib/
├── hwpxlib/           # Core library (stdlib only)
│   ├── document.py    #   HwpxDocument — main API
│   ├── builder.py     #   HwpxBuilder — fluent API
│   ├── xml_writer.py  #   XML serialization
│   ├── template.py    #   Default styles/fonts
│   ├── style_config.py#   StyleConfig — customization
│   ├── package.py     #   ZIP container
│   ├── constants.py   #   Namespaces, units, IDs
│   └── models/        #   Dataclasses (body, head, meta)
├── converters/        # Markdown → HWPX
│   ├── md_parser.py   #   Regex-based MD parser → AST
│   └── md2hwpx.py     #   AST → HwpxDocument
├── mcp_server/        # MCP server (optional, needs mcp>=1.26.0)
│   └── server.py      #   FastMCP tools
├── tests/             # Tests
├── specs/             # HWPX format specs (11 files)
└── reference/         # Reference HWPX for comparison
```

## MCP Server

Claude Code에서 한글 문서를 직접 생성/읽기할 수 있는 MCP 서버:

```bash
# 등록
claude mcp add --transport stdio hwpxlib -- \
  python mcp_server/server.py
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
- `Contents/section0.xml` — 문서 본문 (문단, 표, 이미지)
- `BinData/` — 삽입된 이미지 파일
- `META-INF/` — 컨테이너 메타데이터
- `Preview/PrvText.txt` — 미리보기 텍스트

## License

MIT
