"""Header models: CharPr, ParaPr, Style, FontFace, BorderFill."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FontRef:
    """Font reference for each language."""
    hangul: int = 0
    latin: int = 0
    hanja: int = 0
    japanese: int = 0
    other: int = 0
    symbol: int = 0
    user: int = 0


@dataclass
class CharPr:
    """Character property definition."""
    id: int = 0
    height: int = 1000  # in HWPUNIT (1000 = 10pt)
    text_color: str = "#000000"
    shade_color: str = "none"
    border_fill_id_ref: int = 2
    font_ref: FontRef = field(default_factory=FontRef)
    bold: bool = False
    italic: bool = False
    underline_type: str = "NONE"
    underline_color: str = "#000000"
    strikeout: str = "NONE"
    offset: int = 0  # vertical offset for superscript (>0) / subscript (<0), in %


@dataclass
class ParaPr:
    """Paragraph property definition."""
    id: int = 0
    tab_pr_id_ref: int = 1
    align_horizontal: str = "LEFT"
    heading_type: str = "NONE"
    heading_id_ref: int = 0
    heading_level: int = 0
    keep_with_next: int = 0
    keep_lines: int = 0
    margin_intent: int = 0
    margin_left: int = 0
    margin_right: int = 0
    margin_prev: int = 0
    margin_next: int = 0
    line_spacing_type: str = "PERCENT"
    line_spacing_value: int = 160
    border_fill_id_ref: int = 2


@dataclass
class Style:
    """Named style definition."""
    id: int = 0
    type: str = "PARA"
    name: str = "본문"
    eng_name: str = "Normal"
    para_pr_id_ref: int = 0
    char_pr_id_ref: int = 0
    next_style_id_ref: int = 0
    lang_id: int = 1042


@dataclass
class BorderFill:
    """Border and fill definition."""
    id: int = 1
    left_type: str = "NONE"
    left_width: str = "0.1 mm"
    left_color: str = "#000000"
    right_type: str = "NONE"
    right_width: str = "0.1 mm"
    right_color: str = "#000000"
    top_type: str = "NONE"
    top_width: str = "0.1 mm"
    top_color: str = "#000000"
    bottom_type: str = "NONE"
    bottom_width: str = "0.1 mm"
    bottom_color: str = "#000000"
    fill_color: Optional[str] = None  # None means no fill


@dataclass
class Font:
    """Font definition."""
    id: int = 0
    face: str = "나눔고딕"
    type: str = "TTF"


@dataclass
class FontFace:
    """Font face for a language."""
    lang: str = "HANGUL"
    fonts: list = field(default_factory=list)
