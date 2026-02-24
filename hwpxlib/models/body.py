"""Body models: Section, Paragraph, Run, Table, etc."""
from dataclasses import dataclass, field
from typing import Optional


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
class Section:
    """Section root containing paragraphs and tables."""
    elements: list = field(default_factory=list)  # list of Paragraph or Table-wrapping Paragraph
