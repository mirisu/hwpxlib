"""Body models: Section, Paragraph, Run, Table, PageSetup, etc."""
from dataclasses import dataclass, field
from typing import Optional

from ..constants import (
    PAGE_WIDTH, PAGE_HEIGHT,
    MARGIN_LEFT, MARGIN_RIGHT, MARGIN_TOP, MARGIN_BOTTOM,
    MARGIN_HEADER, MARGIN_FOOTER, MARGIN_GUTTER,
    mm_to_hwpunit,
)


@dataclass
class Run:
    """Text run within a paragraph."""
    text: str = ""
    char_pr_id_ref: int = 0


@dataclass
class Paragraph:
    """A paragraph (hp:p)."""
    runs: list = field(default_factory=list)  # list of Run
    para_pr_id_ref: int = 0
    style_id_ref: int = 0
    # If this is the first paragraph, it may contain secPr
    has_sec_pr: bool = False


@dataclass
class TableCell:
    """Table cell (hp:tc)."""
    paragraphs: list = field(default_factory=list)  # list of Paragraph
    col_addr: int = 0
    row_addr: int = 0
    col_span: int = 1
    row_span: int = 1
    width: int = 15000
    height: int = 1000
    border_fill_id_ref: int = 3
    header: int = 0


@dataclass
class TableRow:
    """Table row (hp:tr)."""
    cells: list = field(default_factory=list)  # list of TableCell


@dataclass
class Table:
    """Table (hp:tbl)."""
    rows: list = field(default_factory=list)  # list of TableRow
    row_cnt: int = 0
    col_cnt: int = 0
    width: int = 42522  # total table width
    border_fill_id_ref: int = 3
    cell_spacing: int = 0


@dataclass
class Image:
    """Inline image (hp:pic)."""
    binary_item_id: str = ""  # e.g. "image1" — matches opf:item id
    width: int = 15000        # in HWPUNIT
    height: int = 7500        # in HWPUNIT
    data: bytes = field(default=b'', repr=False)  # raw image bytes
    media_type: str = "image/png"  # MIME type


@dataclass
class PageSetup:
    """Page size, margins, and orientation."""
    width: int = PAGE_WIDTH       # 59530 (A4 210mm)
    height: int = PAGE_HEIGHT     # 84190 (A4 297mm)
    margin_left: int = MARGIN_LEFT
    margin_right: int = MARGIN_RIGHT
    margin_top: int = MARGIN_TOP
    margin_bottom: int = MARGIN_BOTTOM
    margin_header: int = MARGIN_HEADER
    margin_footer: int = MARGIN_FOOTER
    margin_gutter: int = MARGIN_GUTTER
    orientation: str = "WIDELY"   # WIDELY = portrait, NARROWLY = landscape

    @classmethod
    def a4(cls, landscape: bool = False) -> "PageSetup":
        """A4 (210 x 297 mm)."""
        if landscape:
            return cls(width=PAGE_HEIGHT, height=PAGE_WIDTH, orientation="NARROWLY")
        return cls()

    @classmethod
    def letter(cls, landscape: bool = False) -> "PageSetup":
        """US Letter (216 x 279 mm)."""
        w, h = mm_to_hwpunit(216), mm_to_hwpunit(279)
        if landscape:
            return cls(width=h, height=w, orientation="NARROWLY")
        return cls(width=w, height=h)

    @classmethod
    def a3(cls, landscape: bool = False) -> "PageSetup":
        """A3 (297 x 420 mm)."""
        w, h = mm_to_hwpunit(297), mm_to_hwpunit(420)
        if landscape:
            return cls(width=h, height=w, orientation="NARROWLY")
        return cls(width=w, height=h)

    @property
    def usable_width(self) -> int:
        """Content area width (page width minus left and right margins)."""
        return self.width - self.margin_left - self.margin_right


@dataclass
class Section:
    """Section root containing paragraphs and tables."""
    elements: list = field(default_factory=list)  # list of Paragraph or Table-wrapping Paragraph
