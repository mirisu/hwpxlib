"""OWPML namespace URIs, unit constants, and default values."""

# === OWPML Namespace URIs ===
NS_HH = "http://www.hancom.co.kr/hwpml/2011/head"
NS_HP = "http://www.hancom.co.kr/hwpml/2011/paragraph"
NS_HS = "http://www.hancom.co.kr/hwpml/2011/section"
NS_HC = "http://www.hancom.co.kr/hwpml/2011/core"
NS_HV = "http://www.hancom.co.kr/hwpml/2011/version"
NS_HA = "http://www.hancom.co.kr/hwpml/2011/app"
NS_OPF = "http://www.idpf.org/2007/opf"
NS_OCF = "urn:oasis:names:tc:opendocument:xmlns:container"
NS_EPB = "http://www.idpf.org/2007/ops"
NS_ODF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
NS_DC = "http://purl.org/dc/elements/1.1/"
NS_MANIFEST = "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"

# Namespace prefix map for XML serialization
NS_MAP = {
    "hh": NS_HH,
    "hp": NS_HP,
    "hs": NS_HS,
    "hc": NS_HC,
    "hv": NS_HV,
    "ha": NS_HA,
    "opf": NS_OPF,
}

# === Unit Conversions ===
# 1 pt = 100 HWPUNIT, 1 inch = 7200 HWPUNIT, 1 mm = 283.46 HWPUNIT
HWPUNIT_PER_PT = 100
HWPUNIT_PER_MM = 283.46
HWPUNIT_PER_INCH = 7200


def pt_to_hwpunit(pt: float) -> int:
    """Convert points to HWPUNIT."""
    return round(pt * HWPUNIT_PER_PT)


def mm_to_hwpunit(mm: float) -> int:
    """Convert millimeters to HWPUNIT."""
    return round(mm * HWPUNIT_PER_MM)


def hwpunit_to_pt(hwpunit: int) -> float:
    """Convert HWPUNIT to points."""
    return hwpunit / HWPUNIT_PER_PT


# === Default Page Size (A4) ===
PAGE_WIDTH = 59530   # 210mm in HWPUNIT
PAGE_HEIGHT = 84190  # 297mm in HWPUNIT

# === Default Margins ===
MARGIN_LEFT = 8504
MARGIN_RIGHT = 8504
MARGIN_TOP = 5668
MARGIN_BOTTOM = 4252
MARGIN_HEADER = 4252
MARGIN_FOOTER = 4252
MARGIN_GUTTER = 0

# === Default Font Sizes (in HWPUNIT) ===
FONT_SIZE_DEFAULT = 1000    # 10pt
FONT_SIZE_H1 = 2200         # 22pt
FONT_SIZE_H2 = 1800         # 18pt
FONT_SIZE_H3 = 1400         # 14pt
FONT_SIZE_H4 = 1200         # 12pt
FONT_SIZE_H5 = 1100         # 11pt
FONT_SIZE_H6 = 1000         # 10pt
FONT_SIZE_CODE = 900         # 9pt
FONT_SIZE_TABLE = 900        # 9pt

# === Colors ===
COLOR_BLACK = "#000000"
COLOR_HEADING = "#323E4F"
COLOR_CODE_TEXT = "#E74C3C"
COLOR_CODE_BG = "#F5F5F5"
COLOR_CODE_BLOCK_TEXT = "#333333"
COLOR_CODE_BLOCK_BG = "#F8F8F8"
COLOR_TABLE_HEADER_TEXT = "#FFFFFF"
COLOR_TABLE_HEADER_BG = "#4472C4"
COLOR_TABLE_ALT_BG = "#D9E2F3"
COLOR_WHITE = "#FFFFFF"
COLOR_HR = "#BFBFBF"

# === Font Names ===
FONT_DEFAULT = "나눔고딕"
FONT_CODE = "나눔고딕코딩"

# === Line Spacing ===
LINE_SPACING_DEFAULT = 160    # 160%
LINE_SPACING_CODE = 130       # 130%
LINE_SPACING_TABLE = 130      # 130%

# === charPr ID Map ===
CHARPR_BODY = 0
CHARPR_BOLD = 1
CHARPR_ITALIC = 2
CHARPR_BOLD_ITALIC = 3
CHARPR_H1 = 4
CHARPR_H2 = 5
CHARPR_H3 = 6
CHARPR_H4 = 7
CHARPR_H5 = 8
CHARPR_H6 = 9
CHARPR_INLINE_CODE = 10
CHARPR_CODE_BLOCK = 11
CHARPR_TABLE_HEADER = 12
CHARPR_TABLE_BODY = 13
CHARPR_LINK = 14
CHARPR_STRIKETHROUGH = 15
CHARPR_SUPERSCRIPT = 16
CHARPR_SUBSCRIPT = 17

# === paraPr ID Map ===
PARAPR_BODY = 0
PARAPR_H1 = 1
PARAPR_H2 = 2
PARAPR_H3 = 3
PARAPR_H4 = 4
PARAPR_H5 = 5
PARAPR_H6 = 6
PARAPR_CODE = 7
PARAPR_BULLET = 8
PARAPR_TABLE = 9
PARAPR_ORDERED = 10
PARAPR_BULLET_L2 = 11
PARAPR_BULLET_L3 = 12
PARAPR_ORDERED_L2 = 13
PARAPR_ORDERED_L3 = 14
PARAPR_HR = 15
PARAPR_BLOCKQUOTE = 16

# === Style ID Map ===
STYLE_BODY = 0
STYLE_H1 = 1
STYLE_H2 = 2
STYLE_H3 = 3
STYLE_H4 = 4
STYLE_H5 = 5
STYLE_H6 = 6

# === borderFill ID Map (1-based, must be sequential and unique) ===
BORDERFILL_NONE = 1         # No border, no fill (page border)
BORDERFILL_DEFAULT = 2      # No border, transparent fill (default for text)
BORDERFILL_TABLE = 3        # Solid border for table cells
BORDERFILL_TABLE_HEADER = 4 # Solid border + blue background
BORDERFILL_CODE_BLOCK = 5   # No border + code block background
BORDERFILL_CODE_INLINE = 6  # No border + inline code background
BORDERFILL_HR = 7           # Bottom border only (horizontal rule)
BORDERFILL_BLOCKQUOTE = 8   # Left border only (blockquote vertical bar)
