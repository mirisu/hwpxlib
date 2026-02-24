"""Chaining builder API for HwpxDocument.

Usage:
    doc = HwpxDocument.new()
    (doc.builder()
        .heading("제목", level=1)
        .paragraph("본문")
        .table([["A","B"],["1","2"]])
        .save("output.hwpx"))
"""


class HwpxBuilder:
    """Fluent builder for HwpxDocument."""

    def __init__(self, document):
        self._doc = document

    def heading(self, text: str, level: int = 1) -> "HwpxBuilder":
        self._doc.add_heading(text, level=level)
        return self

    def paragraph(self, text: str = "", bold: bool = False,
                  italic: bool = False) -> "HwpxBuilder":
        self._doc.add_paragraph(text, bold=bold, italic=italic)
        return self

    def mixed_paragraph(self, segments: list) -> "HwpxBuilder":
        self._doc.add_mixed_paragraph(segments)
        return self

    def table(self, headers: list, rows: list) -> "HwpxBuilder":
        self._doc.add_table(headers, rows)
        return self

    def code_block(self, code: str, language: str = "") -> "HwpxBuilder":
        self._doc.add_code_block(code, language=language)
        return self

    def bullet_list(self, items: list) -> "HwpxBuilder":
        self._doc.add_bullet_list(items)
        return self

    def horizontal_rule(self) -> "HwpxBuilder":
        self._doc.add_horizontal_rule()
        return self

    def save(self, path: str) -> None:
        self._doc.save(path)
