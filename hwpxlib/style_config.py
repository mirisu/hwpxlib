"""Style configuration for customizing document appearance."""
from dataclasses import dataclass
from .constants import (
    FONT_DEFAULT, FONT_CODE,
    FONT_SIZE_DEFAULT, FONT_SIZE_H1, FONT_SIZE_H2, FONT_SIZE_H3,
    FONT_SIZE_H4, FONT_SIZE_H5, FONT_SIZE_H6, FONT_SIZE_CODE,
    FONT_SIZE_TABLE,
    COLOR_BLACK, COLOR_HEADING, COLOR_CODE_TEXT, COLOR_CODE_BG,
    COLOR_CODE_BLOCK_TEXT, COLOR_CODE_BLOCK_BG,
    COLOR_TABLE_HEADER_TEXT, COLOR_TABLE_HEADER_BG,
    COLOR_TABLE_ALT_BG, COLOR_WHITE,
    LINE_SPACING_DEFAULT, LINE_SPACING_CODE, LINE_SPACING_TABLE,
)


@dataclass
class StyleConfig:
    """Customizable style settings for a document.

    All font sizes are in HWPUNIT (1pt = 100 HWPUNIT).
    Colors are hex strings (e.g. "#FF0000").
    Line spacing is a percentage (e.g. 160 = 160%).
    """
    # Fonts
    font_body: str = FONT_DEFAULT
    font_code: str = FONT_CODE

    # Font sizes (HWPUNIT: 1000 = 10pt)
    font_size_body: int = FONT_SIZE_DEFAULT
    font_size_h1: int = FONT_SIZE_H1
    font_size_h2: int = FONT_SIZE_H2
    font_size_h3: int = FONT_SIZE_H3
    font_size_h4: int = FONT_SIZE_H4
    font_size_h5: int = FONT_SIZE_H5
    font_size_h6: int = FONT_SIZE_H6
    font_size_code: int = FONT_SIZE_CODE
    font_size_table: int = FONT_SIZE_TABLE

    # Colors
    color_body: str = COLOR_BLACK
    color_heading: str = COLOR_HEADING
    color_code_text: str = COLOR_CODE_TEXT
    color_code_bg: str = COLOR_CODE_BG
    color_code_block_text: str = COLOR_CODE_BLOCK_TEXT
    color_code_block_bg: str = COLOR_CODE_BLOCK_BG
    color_table_header_text: str = COLOR_TABLE_HEADER_TEXT
    color_table_header_bg: str = COLOR_TABLE_HEADER_BG

    # Line spacing (percentage)
    line_spacing: int = LINE_SPACING_DEFAULT
    line_spacing_code: int = LINE_SPACING_CODE
    line_spacing_table: int = LINE_SPACING_TABLE
