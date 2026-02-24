"""XML serialization for HWPX document components.

Uses string-based XML generation to ensure exact namespace prefix control,
which is critical for HWPX compatibility with Hancom Office.
"""
import random
from xml.sax.saxutils import escape as xml_escape

from .constants import (
    NS_HH, NS_HP, NS_HS, NS_HC, NS_HV, NS_HA,
    PAGE_WIDTH, PAGE_HEIGHT,
    MARGIN_LEFT, MARGIN_RIGHT, MARGIN_TOP, MARGIN_BOTTOM,
    MARGIN_HEADER, MARGIN_FOOTER,
)
from .models.head import CharPr, ParaPr, Style, BorderFill, Font, FontFace
from .models.body import Paragraph, Run, Table, TableRow, TableCell


def _esc(text: str) -> str:
    """Escape XML special characters."""
    return xml_escape(text)


# =============================================================================
# META FILES
# =============================================================================

def write_mimetype() -> bytes:
    return b"application/hwp+zip"


def write_version_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<hv:HCFVersion xmlns:hv="{NS_HV}" tagetApplication="WORDPROCESSOR"'
        ' major="5" minor="1" micro="1" buildNumber="0" os="1"'
        ' xmlVersion="1.5" application="Hancom Office Hangul"'
        ' appVersion="12.0.0.1"/>\n'
    )


def write_settings_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<ha:HWPApplicationSetting xmlns:ha="{NS_HA}"'
        ' xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0">\n'
        '  <ha:CaretPosition listIDRef="0" paraIDRef="0" pos="0"/>\n'
        '  <config:config-item-set name="PrintInfo">\n'
        '    <config:config-item name="PrintAutoFootNote" type="boolean">false</config:config-item>\n'
        '    <config:config-item name="PrintAutoHeadNote" type="boolean">false</config:config-item>\n'
        '    <config:config-item name="PrintCropMark" type="short">0</config:config-item>\n'
        '    <config:config-item name="BinderHoleType" type="short">0</config:config-item>\n'
        '    <config:config-item name="ZoomX" type="short">100</config:config-item>\n'
        '    <config:config-item name="ZoomY" type="short">100</config:config-item>\n'
        '  </config:config-item-set>\n'
        '</ha:HWPApplicationSetting>\n'
    )


def write_container_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<ocf:container xmlns:ocf="urn:oasis:names:tc:opendocument:xmlns:container"'
        ' xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf">\n'
        '  <ocf:rootfiles>\n'
        '    <ocf:rootfile full-path="Contents/content.hpf"'
        ' media-type="application/hwpml-package+xml"/>\n'
        '    <ocf:rootfile full-path="Preview/PrvText.txt"'
        ' media-type="text/plain"/>\n'
        '    <ocf:rootfile full-path="META-INF/container.rdf"'
        ' media-type="application/rdf+xml"/>\n'
        '  </ocf:rootfiles>\n'
        '</ocf:container>\n'
    )


def write_manifest_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<odf:manifest xmlns:odf="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"/>\n'
    )


def write_container_rdf() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n'
        '  <rdf:Description rdf:about="">\n'
        '    <ns0:hasPart xmlns:ns0="http://www.hancom.co.kr/hwpml/2016/meta/pkg#"'
        ' rdf:resource="Contents/header.xml"/>\n'
        '  </rdf:Description>\n'
        '  <rdf:Description rdf:about="Contents/header.xml">\n'
        '    <rdf:type rdf:resource="http://www.hancom.co.kr/hwpml/2016/meta/pkg#HeaderFile"/>\n'
        '  </rdf:Description>\n'
        '  <rdf:Description rdf:about="">\n'
        '    <ns0:hasPart xmlns:ns0="http://www.hancom.co.kr/hwpml/2016/meta/pkg#"'
        ' rdf:resource="Contents/section0.xml"/>\n'
        '  </rdf:Description>\n'
        '  <rdf:Description rdf:about="Contents/section0.xml">\n'
        '    <rdf:type rdf:resource="http://www.hancom.co.kr/hwpml/2016/meta/pkg#SectionFile"/>\n'
        '  </rdf:Description>\n'
        '  <rdf:Description rdf:about="">\n'
        '    <rdf:type rdf:resource="http://www.hancom.co.kr/hwpml/2016/meta/pkg#Document"/>\n'
        '  </rdf:Description>\n'
        '</rdf:RDF>\n'
    )


def write_content_hpf() -> str:
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<opf:package xmlns:opf="http://www.idpf.org/2007/opf/"'
        ' version="" unique-identifier="" id="">\n'
        '  <opf:metadata>\n'
        '    <opf:title></opf:title>\n'
        '    <opf:language>ko</opf:language>\n'
        '    <opf:meta name="creator" content="text"></opf:meta>\n'
        '    <opf:meta name="subject" content="text"/>\n'
        '    <opf:meta name="description" content="text"/>\n'
        '    <opf:meta name="keyword" content="text"/>\n'
        '  </opf:metadata>\n'
        '  <opf:manifest>\n'
        '    <opf:item id="header" href="Contents/header.xml"'
        ' media-type="application/xml"/>\n'
        '    <opf:item id="section0" href="Contents/section0.xml"'
        ' media-type="application/xml"/>\n'
        '    <opf:item id="settings" href="settings.xml"'
        ' media-type="application/xml"/>\n'
        '  </opf:manifest>\n'
        '  <opf:spine>\n'
        '    <opf:itemref idref="header" linear="yes"/>\n'
        '    <opf:itemref idref="section0" linear="yes"/>\n'
        '  </opf:spine>\n'
        '</opf:package>\n'
    )


def write_prv_text(text: str = "") -> str:
    """Preview text (first ~200 chars of document)."""
    return text[:200] if text else " "


# =============================================================================
# HEADER.XML
# =============================================================================

def _write_font_face(ff: FontFace) -> str:
    """Write a single fontface element."""
    lines = [f'      <hh:fontface lang="{ff.lang}" fontCnt="{len(ff.fonts)}">']
    for font in ff.fonts:
        lines.append(
            f'        <hh:font id="{font.id}" face="{_esc(font.face)}"'
            f' type="{font.type}" isEmbedded="0" />'
        )
    lines.append('      </hh:fontface>')
    return '\n'.join(lines)


def _write_border_fill(bf: BorderFill) -> str:
    """Write a single borderFill element."""
    lines = [
        f'      <hh:borderFill id="{bf.id}" threeD="0" shadow="0"'
        f' centerLine="NONE" breakCellSeparateLine="0">',
        '        <hh:slash type="NONE" Crooked="0" isCounter="0" />',
        '        <hh:backSlash type="NONE" Crooked="0" isCounter="0" />',
        f'        <hh:leftBorder type="{bf.left_type}" width="{bf.left_width}"'
        f' color="{bf.left_color}" />',
        f'        <hh:rightBorder type="{bf.right_type}" width="{bf.right_width}"'
        f' color="{bf.right_color}" />',
        f'        <hh:topBorder type="{bf.top_type}" width="{bf.top_width}"'
        f' color="{bf.top_color}" />',
        f'        <hh:bottomBorder type="{bf.bottom_type}" width="{bf.bottom_width}"'
        f' color="{bf.bottom_color}" />',
        '        <hh:diagonal type="SOLID" width="0.1 mm" color="#000000" />',
    ]
    if bf.fill_color and bf.fill_color != "none":
        lines.append('        <hc:fillBrush>')
        lines.append(
            f'          <hc:winBrush faceColor="{bf.fill_color}"'
            f' hatchColor="#000000" alpha="0" />'
        )
        lines.append('        </hc:fillBrush>')
    else:
        lines.append('        <hc:fillBrush>')
        lines.append(
            '          <hc:winBrush faceColor="none"'
            ' hatchColor="#000000" alpha="0" />'
        )
        lines.append('        </hc:fillBrush>')
    lines.append('      </hh:borderFill>')
    return '\n'.join(lines)


def _write_char_pr(cp: CharPr) -> str:
    """Write a single charPr element."""
    fr = cp.font_ref
    lines = [
        f'      <hh:charPr id="{cp.id}" height="{cp.height}"'
        f' textColor="{cp.text_color}" shadeColor="{cp.shade_color}"'
        f' useFontSpace="0" useKerning="0" symMark="NONE"'
        f' borderFillIDRef="{cp.border_fill_id_ref}">',
        f'        <hh:fontRef hangul="{fr.hangul}" latin="{fr.latin}"'
        f' hanja="{fr.hanja}" japanese="{fr.japanese}" other="{fr.other}"'
        f' symbol="{fr.symbol}" user="{fr.user}" />',
        '        <hh:ratio hangul="100" latin="100" hanja="100"'
        ' japanese="100" other="100" symbol="100" user="100" />',
        '        <hh:spacing hangul="0" latin="0" hanja="0"'
        ' japanese="0" other="0" symbol="0" user="0" />',
        '        <hh:relSz hangul="100" latin="100" hanja="100"'
        ' japanese="100" other="100" symbol="100" user="100" />',
        '        <hh:offset hangul="0" latin="0" hanja="0"'
        ' japanese="0" other="0" symbol="0" user="0" />',
    ]
    if cp.bold:
        lines.append('        <hh:bold />')
    if cp.italic:
        lines.append('        <hh:italic />')
    lines.append(
        f'        <hh:underline type="{cp.underline_type}" shape="SOLID"'
        f' color="{cp.underline_color}" />'
    )
    lines.append(f'        <hh:strikeout shape="{cp.strikeout}" color="#000000" />')
    lines.append('        <hh:outline type="NONE" />')
    lines.append('        <hh:shadow type="NONE" color="#C0C0C0" offsetX="5" offsetY="5" />')
    lines.append('      </hh:charPr>')
    return '\n'.join(lines)


def _write_para_pr(pp: ParaPr) -> str:
    """Write a single paraPr element."""
    lines = [
        f'      <hh:paraPr id="{pp.id}" tabPrIDRef="{pp.tab_pr_id_ref}"'
        f' condense="0" fontLineHeight="0" snapToGrid="1"'
        f' suppressLineNumbers="0" checked="0">',
        f'        <hh:align horizontal="{pp.align_horizontal}" vertical="BASELINE" />',
        f'        <hh:heading type="{pp.heading_type}" idRef="{pp.heading_id_ref}"'
        f' level="{pp.heading_level}" />',
        f'        <hh:breakSetting breakLatinWord="KEEP_WORD"'
        f' breakNonLatinWord="BREAK_WORD" widowOrphan="0"'
        f' keepWithNext="{pp.keep_with_next}" keepLines="{pp.keep_lines}"'
        f' pageBreakBefore="0" lineWrap="BREAK" />',
        '        <hh:autoSpacing eAsianEng="0" eAsianNum="0" />',
        '        <hp:switch>',
        '          <hp:case hp:required-namespace='
        '"http://www.hancom.co.kr/hwpml/2016/HwpUnitChar">',
        '            <hh:margin>',
        f'              <hc:intent value="{pp.margin_intent}" unit="HWPUNIT" />',
        f'              <hc:left value="{pp.margin_left}" unit="HWPUNIT" />',
        f'              <hc:right value="{pp.margin_right}" unit="HWPUNIT" />',
        f'              <hc:prev value="{pp.margin_prev}" unit="HWPUNIT" />',
        f'              <hc:next value="{pp.margin_next}" unit="HWPUNIT" />',
        '            </hh:margin>',
        f'            <hh:lineSpacing type="{pp.line_spacing_type}"'
        f' value="{pp.line_spacing_value}" unit="HWPUNIT" />',
        '          </hp:case>',
        '          <hp:default>',
        '            <hh:margin>',
        f'              <hc:intent value="{pp.margin_intent}" unit="HWPUNIT" />',
        f'              <hc:left value="{pp.margin_left}" unit="HWPUNIT" />',
        f'              <hc:right value="{pp.margin_right}" unit="HWPUNIT" />',
        f'              <hc:prev value="{pp.margin_prev}" unit="HWPUNIT" />',
        f'              <hc:next value="{pp.margin_next}" unit="HWPUNIT" />',
        '            </hh:margin>',
        f'            <hh:lineSpacing type="{pp.line_spacing_type}"'
        f' value="{pp.line_spacing_value}" unit="HWPUNIT" />',
        '          </hp:default>',
        '        </hp:switch>',
        f'        <hh:border borderFillIDRef="{pp.border_fill_id_ref}"'
        f' offsetLeft="400" offsetRight="400" offsetTop="100"'
        f' offsetBottom="100" connect="0" ignoreMargin="0" />',
        '      </hh:paraPr>',
    ]
    return '\n'.join(lines)


def _write_style(s: Style) -> str:
    """Write a single style element."""
    return (
        f'      <hh:style id="{s.id}" type="{s.type}"'
        f' name="{_esc(s.name)}" engName="{_esc(s.eng_name)}"'
        f' paraPrIDRef="{s.para_pr_id_ref}"'
        f' charPrIDRef="{s.char_pr_id_ref}"'
        f' nextStyleIDRef="{s.next_style_id_ref}"'
        f' langID="{s.lang_id}" lockForm="0" />'
    )


def write_header_xml(
    font_faces: list,
    border_fills: list,
    char_prs: list,
    para_prs: list,
    styles: list,
    numberings_xml: str = "",
    bullets_xml: str = "",
) -> str:
    """Generate the complete header.xml content."""
    lines = [
        f'<hh:head xmlns:hc="{NS_HC}" xmlns:hh="{NS_HH}"'
        f' xmlns:hp="{NS_HP}" version="1.5" secCnt="1">',
        '  <hh:beginNum page="1" footnote="1" endnote="1" pic="1"'
        ' tbl="1" equation="1" />',
        '  <hh:refList>',
    ]

    # Font faces
    lines.append(f'    <hh:fontfaces itemCnt="{len(font_faces)}">')
    for ff in font_faces:
        lines.append(_write_font_face(ff))
    lines.append('    </hh:fontfaces>')

    # Border fills
    lines.append(f'    <hh:borderFills itemCnt="{len(border_fills)}">')
    for bf in border_fills:
        lines.append(_write_border_fill(bf))
    lines.append('    </hh:borderFills>')

    # Char properties
    lines.append(f'    <hh:charProperties itemCnt="{len(char_prs)}">')
    for cp in char_prs:
        lines.append(_write_char_pr(cp))
    lines.append('    </hh:charProperties>')

    # Para properties
    lines.append(f'    <hh:paraProperties itemCnt="{len(para_prs)}">')
    for pp in para_prs:
        lines.append(_write_para_pr(pp))
    lines.append('    </hh:paraProperties>')

    # Tab properties
    lines.append('    <hh:tabProperties itemCnt="2">')
    lines.append('      <hh:tabPr id="0" autoTabLeft="0" autoTabRight="0" />')
    lines.append('      <hh:tabPr id="1" autoTabLeft="1" autoTabRight="0" />')
    lines.append('    </hh:tabProperties>')

    # Numberings
    if numberings_xml:
        lines.append(numberings_xml)
    else:
        lines.append('    <hh:numberings itemCnt="1">')
        lines.append('      <hh:numbering id="1" start="0">')
        for lvl in range(1, 11):
            lines.append(
                f'        <hh:paraHead start="1" level="{lvl}" align="LEFT"'
                f' useInstWidth="1" autoIndent="0" widthAdjust="0"'
                f' textOffsetType="PERCENT" textOffset="35"'
                f' numFormat="DIGIT" charPrIDRef="1" checkable="0" />'
            )
        lines.append('      </hh:numbering>')
        lines.append('    </hh:numberings>')

    # Bullets
    if bullets_xml:
        lines.append(bullets_xml)
    else:
        lines.append('    <hh:bullets itemCnt="1">')
        lines.append(
            '      <hh:bullet id="1" char="&#x25CF;"'
            ' checkedChar="&#x25CF;">'
        )
        for lvl in range(1, 11):
            lines.append(
                f'        <hh:paraHead start="1" level="{lvl}" align="LEFT"'
                f' useInstWidth="1" autoIndent="1" widthAdjust="0"'
                f' textOffsetType="PERCENT" textOffset="50"'
                f' numFormat="BULLET" charPrIDRef="0" checkable="0" />'
            )
        lines.append('      </hh:bullet>')
        lines.append('    </hh:bullets>')

    lines.append('  </hh:refList>')

    # Styles
    lines.append(f'  <hh:styles itemCnt="{len(styles)}">')
    for s in styles:
        lines.append(_write_style(s))
    lines.append('  </hh:styles>')

    lines.append('</hh:head>')
    return '\n'.join(lines)


# =============================================================================
# SECTION0.XML (body content)
# =============================================================================

def _unique_id() -> int:
    """Generate a unique-ish ID for HWPX elements."""
    return random.randint(100000000, 999999999)


def write_sec_pr() -> str:
    """Write section properties (page setup) - goes in first paragraph's first run."""
    return (
        f'<hp:secPr xmlns:hp="{NS_HP}" id=""'
        ' textDirection="HORIZONTAL" spaceColumns="1134"'
        ' tabStop="8000" tabStopVal="4000" tabStopUnit="HWPUNIT"'
        ' outlineShapeIDRef="1" memoShapeIDRef="1"'
        ' textVerticalWidthHead="0" masterPageCnt="0">\n'
        '        <hp:grid lineGrid="0" charGrid="0" wonggojiFormat="0" />\n'
        '        <hp:startNum pageStartsOn="BOTH" page="0" pic="0"'
        ' tbl="0" equation="0" />\n'
        '        <hp:visibility hideFirstHeader="0" hideFirstFooter="0"'
        ' hideFirstMasterPage="0" border="SHOW_ALL" fill="SHOW_ALL"'
        ' hideFirstPageNum="0" hideFirstEmptyLine="0" showLineNumber="0" />\n'
        '        <hp:lineNumberShape restartType="0" countBy="0"'
        ' distance="0" startNumber="0" />\n'
        f'        <hp:pagePr landscape="WIDELY" width="{PAGE_WIDTH}"'
        f' height="{PAGE_HEIGHT}" gutterType="LEFT_ONLY">\n'
        f'          <hp:margin header="{MARGIN_HEADER}" footer="{MARGIN_FOOTER}"'
        f' gutter="0" left="{MARGIN_LEFT}" right="{MARGIN_RIGHT}"'
        f' top="{MARGIN_TOP}" bottom="{MARGIN_BOTTOM}" />\n'
        '        </hp:pagePr>\n'
        '        <hp:footNotePr>\n'
        '          <hp:autoNumFormat type="DIGIT" userChar=""'
        ' prefixChar="" suffixChar="" supscript="1" />\n'
        '          <hp:noteLine length="-1" type="SOLID"'
        ' width="0.25 mm" color="#000000" />\n'
        '          <hp:noteSpacing betweenNotes="283"'
        ' belowLine="0" aboveLine="1000" />\n'
        '          <hp:numbering type="CONTINUOUS" newNum="1" />\n'
        '          <hp:placement place="EACH_COLUMN" beneathText="0" />\n'
        '        </hp:footNotePr>\n'
        '        <hp:endNotePr>\n'
        '          <hp:autoNumFormat type="ROMAN_SMALL" userChar=""'
        ' prefixChar="" suffixChar="" supscript="1" />\n'
        '          <hp:noteLine length="-1" type="SOLID"'
        ' width="0.25 mm" color="#000000" />\n'
        '          <hp:noteSpacing betweenNotes="0"'
        ' belowLine="0" aboveLine="1000" />\n'
        '          <hp:numbering type="CONTINUOUS" newNum="1" />\n'
        '          <hp:placement place="END_OF_DOCUMENT" beneathText="0" />\n'
        '        </hp:endNotePr>\n'
        '        <hp:pageBorderFill type="BOTH" borderFillIDRef="1"'
        ' textBorder="PAPER" headerInside="0" footerInside="0"'
        ' fillArea="PAPER">\n'
        '          <hp:offset left="1417" right="1417"'
        ' top="1417" bottom="1417" />\n'
        '        </hp:pageBorderFill>\n'
        '        <hp:pageBorderFill type="EVEN" borderFillIDRef="1"'
        ' textBorder="PAPER" headerInside="0" footerInside="0"'
        ' fillArea="PAPER">\n'
        '          <hp:offset left="1417" right="1417"'
        ' top="1417" bottom="1417" />\n'
        '        </hp:pageBorderFill>\n'
        '        <hp:pageBorderFill type="ODD" borderFillIDRef="1"'
        ' textBorder="PAPER" headerInside="0" footerInside="0"'
        ' fillArea="PAPER">\n'
        '          <hp:offset left="1417" right="1417"'
        ' top="1417" bottom="1417" />\n'
        '        </hp:pageBorderFill>\n'
        '      </hp:secPr>'
    )


def _write_run(run: Run) -> str:
    """Write a single run element."""
    return (
        f'<hp:run charPrIDRef="{run.char_pr_id_ref}">'
        f'<hp:t>{_esc(run.text)}</hp:t></hp:run>'
    )


def write_paragraph(para: Paragraph, is_first: bool = False) -> str:
    """Write a paragraph element."""
    parts = [
        f'<hp:p paraPrIDRef="{para.para_pr_id_ref}"'
        f' styleIDRef="{para.style_id_ref}"'
        f' pageBreak="0" columnBreak="0" merged="0">'
    ]

    for i, run in enumerate(para.runs):
        run_start = f'<hp:run charPrIDRef="{run.char_pr_id_ref}">'
        inner = ""
        # First paragraph, first run gets secPr and colPr
        if is_first and i == 0:
            inner += write_sec_pr()
            inner += (
                '\n      <hp:ctrl xmlns:hp="'
                + NS_HP + '">\n'
                '        <hp:colPr id="" type="NEWSPAPER" layout="LEFT"'
                ' colCount="1" sameSz="1" sameGap="0" />\n'
                '      </hp:ctrl>\n    '
            )
        inner += f'<hp:t>{_esc(run.text)}</hp:t>'
        parts.append(run_start + inner + '</hp:run>')

    # Empty paragraph (no runs) - still valid
    if not para.runs:
        if is_first:
            run_start = '<hp:run charPrIDRef="0">'
            inner = write_sec_pr()
            inner += (
                '\n      <hp:ctrl xmlns:hp="'
                + NS_HP + '">\n'
                '        <hp:colPr id="" type="NEWSPAPER" layout="LEFT"'
                ' colCount="1" sameSz="1" sameGap="0" />\n'
                '      </hp:ctrl>\n    '
            )
            parts.append(run_start + inner + '</hp:run>')

    parts.append('</hp:p>')
    return ''.join(parts)


def write_table_paragraph(table: Table, para_pr_id_ref: int = 0,
                          style_id_ref: int = 0) -> str:
    """Write a table wrapped in a paragraph."""
    tbl_id = _unique_id()
    total_width = table.width

    parts = [
        f'<hp:p paraPrIDRef="{para_pr_id_ref}"'
        f' styleIDRef="{style_id_ref}"'
        ' pageBreak="0" columnBreak="0" merged="0">',
        f'<hp:run charPrIDRef="0">',
        f'<hp:tbl id="{tbl_id}" zOrder="0" numberingType="TABLE"'
        f' textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES"'
        f' lock="0" dropcapstyle="None" pageBreak="CELL"'
        f' repeatHeader="1" rowCnt="{table.row_cnt}"'
        f' colCnt="{table.col_cnt}" cellSpacing="{table.cell_spacing}"'
        f' borderFillIDRef="{table.border_fill_id_ref}" noAdjust="0">',
        f'<hp:sz width="{total_width}" widthRelTo="ABSOLUTE"'
        f' height="5000" heightRelTo="ABSOLUTE" protect="0"/>',
        '<hp:pos treatAsChar="0" affectLSpacing="0" flowWithText="1"'
        ' allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA"'
        ' horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT"'
        ' vertOffset="0" horzOffset="0"/>',
        '<hp:outMargin left="0" right="0" top="0" bottom="1417"/>',
        '<hp:inMargin left="510" right="510" top="141" bottom="141"/>',
    ]

    for row in table.rows:
        parts.append('<hp:tr>')
        for cell in row.cells:
            sub_id = _unique_id()
            parts.append(
                f'<hp:tc name="" header="{cell.header}" hasMargin="0"'
                f' protect="0" editable="0" dirty="0"'
                f' borderFillIDRef="{cell.border_fill_id_ref}">'
            )
            parts.append(
                f'<hp:subList id="{sub_id}" textDirection="HORIZONTAL"'
                f' lineWrap="BREAK" vertAlign="TOP" linkListIDRef="0"'
                f' linkListNextIDRef="0" textWidth="0" textHeight="0"'
                f' hasTextRef="0" hasNumRef="0">'
            )
            for p in cell.paragraphs:
                parts.append(write_paragraph(p, is_first=False))
            parts.append('</hp:subList>')
            parts.append(
                f'<hp:cellAddr colAddr="{cell.col_addr}"'
                f' rowAddr="{cell.row_addr}"/>'
            )
            parts.append(
                f'<hp:cellSpan colSpan="{cell.col_span}"'
                f' rowSpan="{cell.row_span}"/>'
            )
            parts.append(
                f'<hp:cellSz width="{cell.width}"'
                f' height="{cell.height}"/>'
            )
            parts.append(
                '<hp:cellMargin left="510" right="510"'
                ' top="141" bottom="141"/>'
            )
            parts.append('</hp:tc>')
        parts.append('</hp:tr>')

    parts.append('</hp:tbl>')
    parts.append('</hp:run>')
    parts.append('</hp:p>')
    return ''.join(parts)


def write_section_xml(elements: list, first_para_idx: int = 0) -> str:
    """Generate the complete section0.xml content.

    elements: list of tuples:
        ("paragraph", Paragraph)
        ("table", Table, para_pr_id_ref, style_id_ref)
    """
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        f'<hs:sec xmlns:hp="{NS_HP}" xmlns:hs="{NS_HS}"'
        f' xmlns:hc="{NS_HC}">',
    ]

    for i, elem in enumerate(elements):
        is_first = (i == first_para_idx)
        if elem[0] == "paragraph":
            lines.append(write_paragraph(elem[1], is_first=is_first))
        elif elem[0] == "table":
            # Table gets its own paragraph wrapper
            tbl = elem[1]
            ppr = elem[2] if len(elem) > 2 else 0
            sidr = elem[3] if len(elem) > 3 else 0
            if is_first:
                # Need a first paragraph with secPr before the table
                empty_para = Paragraph(runs=[], para_pr_id_ref=0, style_id_ref=0)
                lines.append(write_paragraph(empty_para, is_first=True))
                lines.append(write_table_paragraph(tbl, ppr, sidr))
            else:
                lines.append(write_table_paragraph(tbl, ppr, sidr))

    lines.append('</hs:sec>')
    return '\n'.join(lines)
