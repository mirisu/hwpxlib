# Implementation Plan

## Status: 3 of 3 XML quality items resolved | 7 of 7 security items resolved

### Analysis Summary (2026-02-24)

Full comparison of hwpxlib output vs reference HWPX (Colorlight report):
- **header.xml**: 609 lines, byte-perfect match
- **version.xml**: byte-perfect match
- **settings.xml**: byte-perfect match
- **container.xml**: byte-perfect match
- **manifest.xml**: byte-perfect match
- **container.rdf**: byte-perfect match
- **content.hpf**: byte-perfect match
- **Preview/PrvText.txt**: byte-perfect match
- **mimetype**: byte-perfect match
- **section0.xml**: 200 lines, structurally identical; only difference is random IDs in `hp:tbl` and `hp:subList` elements (17 lines)

After normalizing random IDs → **PERFECT MATCH** on section0.xml as well.

---

### P1 — Structural (resolved)

- [x] **Deterministic element IDs**: `xml_writer.py` `_unique_id()` now uses `_IdGenerator` class with optional seed. `HwpxDocument.new(seed=42)` produces identical output on every run. Default (no seed) remains random for uniqueness across documents.

### P2 — Cosmetic / Quality of Life (resolved)

- [x] **Seed-based reproducibility option**: `HwpxDocument(seed=N)` / `HwpxDocument.new(seed=N)` parameter added. Verified: same seed → identical bytes, no seed → different bytes.

- [x] **Cleanup generated test file**: Removed `_gen_header.xml` and `_test_colorlight.hwpx` from project root.

---

## Security Audit (2026-02-24)

### S0 — Critical (resolved)

- [x] **XML Attribute Injection** (`xml_writer.py`): Added `_esc_attr()` function using `xml_escape(str(value), {'"': '&quot;'})`. Applied to all attribute value interpolations in `_write_font_face()`, `_write_border_fill()`, `_write_char_pr()`, `_write_para_pr()`, `_write_style()`. Test: `test_font_face_with_malicious_name`, `test_style_with_malicious_name`.

- [x] **Raw XML Injection** (`xml_writer.py`): Removed `numberings_xml` and `bullets_xml` raw string parameters from `write_header_xml()`. Numberings and bullets are now always generated internally with hardcoded safe values.

### S1 — Important (resolved)

- [x] **ZIP Path Traversal** (`package.py`): `add_file()` now validates paths — rejects `..` traversal, absolute Unix/Windows paths. Uses `posixpath.normpath()` for normalization. Tests: 7 cases (reject `../`, reject absolute, accept valid nested paths).

- [x] **MCP Arbitrary File Execution** (`server.py`): `open_in_hwp()` now validates file extension via `_validate_document_path()` — only `.hwp`, `.hwpx`, `.hwt` are allowed. Rejects `.exe`, `.bat`, `.cmd`, `.py`, etc. Tests: 5 rejection + 2 acceptance cases.

- [x] **MCP Path Validation** (`server.py`): Added `_validate_output_path()` for `convert_md_to_hwpx()` and `create_document_from_md()`. Added input extension check (`.md`, `.txt`) for `convert_md_to_hwpx()`. `read_hwpx()` now validates via `_validate_document_path()`.

### S2 — Defense-in-depth (resolved)

- [x] **Thread-unsafe global state** (`xml_writer.py`): `_IdGenerator` now uses `threading.local()` for per-thread RNG state. Concurrent `save()` calls in different threads each get their own independent ID sequence. Test: `test_thread_isolation` verifies two threads produce deterministic, independent sequences.

- [x] **No XML bomb protection in tests**: Acknowledged as low-risk (tests only parse self-generated XML). No action needed — documented for awareness.

---

## Test Coverage

- **75 total tests** (52 XML quality + 23 security), all passing
- `validate_xml.py`: PASS (header.xml + meta files byte-match reference)
