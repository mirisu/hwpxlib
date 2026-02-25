"""Default document template with predefined styles.

Creates all the charPr, paraPr, styles, fonts, and borderFills
needed for a standard document based on the reference HWPX structure.
"""
from .constants import (
    CHARPR_BODY, CHARPR_BOLD, CHARPR_ITALIC, CHARPR_BOLD_ITALIC,
    CHARPR_H1, CHARPR_H2, CHARPR_H3, CHARPR_H4, CHARPR_H5, CHARPR_H6,
    CHARPR_INLINE_CODE, CHARPR_CODE_BLOCK,
    CHARPR_TABLE_HEADER, CHARPR_TABLE_BODY, CHARPR_LINK,
    PARAPR_BODY, PARAPR_H1, PARAPR_H2, PARAPR_H3,
    PARAPR_H4, PARAPR_H5, PARAPR_H6, PARAPR_CODE, PARAPR_BULLET,
    PARAPR_TABLE, PARAPR_ORDERED,
    PARAPR_BULLET_L2, PARAPR_BULLET_L3,
    PARAPR_ORDERED_L2, PARAPR_ORDERED_L3,
    BORDERFILL_NONE, BORDERFILL_DEFAULT, BORDERFILL_TABLE,
    BORDERFILL_TABLE_HEADER, BORDERFILL_CODE_BLOCK, BORDERFILL_CODE_INLINE,
)
from .style_config import StyleConfig
from .models.head import CharPr, ParaPr, Style, BorderFill, Font, FontFace, FontRef


def default_font_faces(config: StyleConfig = None) -> list:
    """Create font face definitions for all language groups."""
    cfg = config or StyleConfig()
    langs = ["HANGUL", "LATIN", "HANJA", "JAPANESE", "OTHER", "SYMBOL", "USER"]
    faces = []
    for lang in langs:
        faces.append(FontFace(
            lang=lang,
            fonts=[
                Font(id=0, face=cfg.font_body, type="TTF"),
                Font(id=1, face=cfg.font_code, type="TTF"),
            ]
        ))
    return faces


def default_border_fills(config: StyleConfig = None) -> list:
    """Create border fill definitions."""
    cfg = config or StyleConfig()
    return [
        # id=1: No border, no fill (page border, etc.)
        BorderFill(id=BORDERFILL_NONE, fill_color="none"),
        # id=2: No border, transparent fill (default for text)
        BorderFill(id=BORDERFILL_DEFAULT, fill_color="none"),
        # id=3: Solid border for tables
        BorderFill(
            id=BORDERFILL_TABLE,
            left_type="SOLID", left_width="0.12 mm",
            right_type="SOLID", right_width="0.12 mm",
            top_type="SOLID", top_width="0.12 mm",
            bottom_type="SOLID", bottom_width="0.12 mm",
            fill_color="none",
        ),
        # id=4: Table header (blue background + solid border)
        BorderFill(
            id=BORDERFILL_TABLE_HEADER,
            left_type="SOLID", left_width="0.12 mm",
            right_type="SOLID", right_width="0.12 mm",
            top_type="SOLID", top_width="0.12 mm",
            bottom_type="SOLID", bottom_width="0.12 mm",
            fill_color=cfg.color_table_header_bg,
        ),
        # id=5: Code block background
        BorderFill(
            id=BORDERFILL_CODE_BLOCK,
            left_type="NONE", right_type="NONE",
            top_type="NONE", bottom_type="NONE",
            fill_color=cfg.color_code_block_bg,
        ),
        # id=6: Inline code background
        BorderFill(
            id=BORDERFILL_CODE_INLINE,
            left_type="NONE", right_type="NONE",
            top_type="NONE", bottom_type="NONE",
            fill_color=cfg.color_code_bg,
        ),
    ]


def default_char_prs(config: StyleConfig = None) -> list:
    """Create character property definitions."""
    cfg = config or StyleConfig()
    font_default = FontRef()  # all 0 (body font)
    font_code = FontRef(hangul=1, latin=1, hanja=1, japanese=1,
                         other=1, symbol=1, user=1)  # all 1 (code font)

    return [
        # 0: 본문
        CharPr(id=CHARPR_BODY, height=cfg.font_size_body,
               text_color=cfg.color_body, font_ref=font_default,
               border_fill_id_ref=BORDERFILL_DEFAULT),
        # 1: 볼드
        CharPr(id=CHARPR_BOLD, height=cfg.font_size_body,
               text_color=cfg.color_body, font_ref=font_default,
               bold=True, border_fill_id_ref=BORDERFILL_DEFAULT),
        # 2: 이탤릭
        CharPr(id=CHARPR_ITALIC, height=cfg.font_size_body,
               text_color=cfg.color_body, font_ref=font_default,
               italic=True, border_fill_id_ref=BORDERFILL_DEFAULT),
        # 3: 볼드+이탤릭
        CharPr(id=CHARPR_BOLD_ITALIC, height=cfg.font_size_body,
               text_color=cfg.color_body, font_ref=font_default,
               bold=True, italic=True, border_fill_id_ref=BORDERFILL_DEFAULT),
        # 4: 제목1
        CharPr(id=CHARPR_H1, height=cfg.font_size_h1,
               text_color=cfg.color_heading, font_ref=font_default,
               bold=True, border_fill_id_ref=BORDERFILL_DEFAULT),
        # 5: 제목2
        CharPr(id=CHARPR_H2, height=cfg.font_size_h2,
               text_color=cfg.color_heading, font_ref=font_default,
               bold=True, border_fill_id_ref=BORDERFILL_DEFAULT),
        # 6: 제목3
        CharPr(id=CHARPR_H3, height=cfg.font_size_h3,
               text_color=cfg.color_heading, font_ref=font_default,
               bold=True, border_fill_id_ref=BORDERFILL_DEFAULT),
        # 7: 제목4
        CharPr(id=CHARPR_H4, height=cfg.font_size_h4,
               text_color=cfg.color_heading, font_ref=font_default,
               bold=True, border_fill_id_ref=BORDERFILL_DEFAULT),
        # 8: 제목5
        CharPr(id=CHARPR_H5, height=cfg.font_size_h5,
               text_color=cfg.color_heading, font_ref=font_default,
               bold=True, border_fill_id_ref=BORDERFILL_DEFAULT),
        # 9: 제목6
        CharPr(id=CHARPR_H6, height=cfg.font_size_h6,
               text_color=cfg.color_heading, font_ref=font_default,
               bold=True, border_fill_id_ref=BORDERFILL_DEFAULT),
        # 10: 인라인코드
        CharPr(id=CHARPR_INLINE_CODE, height=cfg.font_size_code,
               text_color=cfg.color_code_text, font_ref=font_code,
               border_fill_id_ref=BORDERFILL_CODE_INLINE),
        # 11: 코드블록
        CharPr(id=CHARPR_CODE_BLOCK, height=cfg.font_size_code,
               text_color=cfg.color_code_block_text, font_ref=font_code,
               border_fill_id_ref=BORDERFILL_DEFAULT),
        # 12: 표 헤더
        CharPr(id=CHARPR_TABLE_HEADER, height=cfg.font_size_table,
               text_color=cfg.color_table_header_text, font_ref=font_default,
               bold=True, border_fill_id_ref=BORDERFILL_DEFAULT),
        # 13: 표 본문
        CharPr(id=CHARPR_TABLE_BODY, height=cfg.font_size_table,
               text_color=cfg.color_body, font_ref=font_default,
               border_fill_id_ref=BORDERFILL_DEFAULT),
        # 14: 하이퍼링크
        CharPr(id=CHARPR_LINK, height=cfg.font_size_body,
               text_color="#0000FF", font_ref=font_default,
               underline_type="BOTTOM", underline_color="#0000FF",
               border_fill_id_ref=BORDERFILL_DEFAULT),
    ]


def default_para_prs(config: StyleConfig = None) -> list:
    """Create paragraph property definitions."""
    cfg = config or StyleConfig()
    ls = cfg.line_spacing
    ls_code = cfg.line_spacing_code
    ls_table = cfg.line_spacing_table

    return [
        # 0: 본문
        ParaPr(id=PARAPR_BODY, margin_next=500,
               line_spacing_value=ls),
        # 1: 제목1
        ParaPr(id=PARAPR_H1, heading_type="OUTLINE", heading_level=0,
               keep_with_next=1, keep_lines=1,
               margin_prev=2400, margin_next=400,
               line_spacing_value=ls),
        # 2: 제목2
        ParaPr(id=PARAPR_H2, heading_type="OUTLINE", heading_level=1,
               keep_with_next=1, keep_lines=1,
               margin_prev=1800, margin_next=400,
               line_spacing_value=ls),
        # 3: 제목3
        ParaPr(id=PARAPR_H3, heading_type="OUTLINE", heading_level=2,
               keep_with_next=1, keep_lines=1,
               margin_prev=1200, margin_next=300,
               line_spacing_value=ls),
        # 4: 제목4
        ParaPr(id=PARAPR_H4, heading_type="OUTLINE", heading_level=3,
               keep_with_next=1, keep_lines=1,
               margin_prev=1000, margin_next=200,
               line_spacing_value=ls),
        # 5: 제목5
        ParaPr(id=PARAPR_H5, heading_type="OUTLINE", heading_level=4,
               keep_with_next=1, keep_lines=1,
               margin_prev=800, margin_next=200,
               line_spacing_value=ls),
        # 6: 제목6
        ParaPr(id=PARAPR_H6, heading_type="OUTLINE", heading_level=5,
               keep_with_next=1, keep_lines=1,
               margin_prev=600, margin_next=200,
               line_spacing_value=ls),
        # 7: 코드블록
        ParaPr(id=PARAPR_CODE, margin_left=400, margin_right=400,
               margin_prev=0, margin_next=0,
               line_spacing_value=ls_code,
               border_fill_id_ref=BORDERFILL_CODE_BLOCK),
        # 8: 불릿
        ParaPr(id=PARAPR_BULLET, heading_type="BULLET", heading_id_ref=1,
               heading_level=0,
               margin_intent=800, margin_left=800,
               margin_next=200,
               line_spacing_value=ls),
        # 9: 표
        ParaPr(id=PARAPR_TABLE, margin_prev=0, margin_next=0,
               line_spacing_value=ls_table,
               align_horizontal="CENTER"),
        # 10: 번호매기기
        ParaPr(id=PARAPR_ORDERED, heading_type="NUMBER", heading_id_ref=1,
               heading_level=0,
               margin_intent=800, margin_left=800,
               margin_next=200,
               line_spacing_value=ls),
        # 11: 불릿 레벨2
        ParaPr(id=PARAPR_BULLET_L2, heading_type="BULLET", heading_id_ref=1,
               heading_level=1,
               margin_intent=800, margin_left=1600,
               margin_next=200,
               line_spacing_value=ls),
        # 12: 불릿 레벨3
        ParaPr(id=PARAPR_BULLET_L3, heading_type="BULLET", heading_id_ref=1,
               heading_level=2,
               margin_intent=800, margin_left=2400,
               margin_next=200,
               line_spacing_value=ls),
        # 13: 번호매기기 레벨2
        ParaPr(id=PARAPR_ORDERED_L2, heading_type="NUMBER", heading_id_ref=1,
               heading_level=1,
               margin_intent=800, margin_left=1600,
               margin_next=200,
               line_spacing_value=ls),
        # 14: 번호매기기 레벨3
        ParaPr(id=PARAPR_ORDERED_L3, heading_type="NUMBER", heading_id_ref=1,
               heading_level=2,
               margin_intent=800, margin_left=2400,
               margin_next=200,
               line_spacing_value=ls),
    ]


def default_styles() -> list:
    """Create style definitions."""
    return [
        Style(id=0, name="본문", eng_name="Normal",
              para_pr_id_ref=PARAPR_BODY, char_pr_id_ref=CHARPR_BODY),
        Style(id=1, name="제목 1", eng_name="Heading 1",
              para_pr_id_ref=PARAPR_H1, char_pr_id_ref=CHARPR_H1),
        Style(id=2, name="제목 2", eng_name="Heading 2",
              para_pr_id_ref=PARAPR_H2, char_pr_id_ref=CHARPR_H2),
        Style(id=3, name="제목 3", eng_name="Heading 3",
              para_pr_id_ref=PARAPR_H3, char_pr_id_ref=CHARPR_H3),
        Style(id=4, name="제목 4", eng_name="Heading 4",
              para_pr_id_ref=PARAPR_H4, char_pr_id_ref=CHARPR_H4),
        Style(id=5, name="제목 5", eng_name="Heading 5",
              para_pr_id_ref=PARAPR_H5, char_pr_id_ref=CHARPR_H5),
        Style(id=6, name="제목 6", eng_name="Heading 6",
              para_pr_id_ref=PARAPR_H6, char_pr_id_ref=CHARPR_H6),
    ]
