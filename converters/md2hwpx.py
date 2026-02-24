"""MD to HWPX conversion engine.

Parses Markdown using md_parser, then builds a HwpxDocument using the library API.
"""
from .md_parser import (
    parse_markdown, Heading, ParagraphNode, TableNode,
    CodeBlock, BulletList, OrderedList, HorizontalRule, BlockQuote,
    TextSegment,
)
from hwpxlib.document import HwpxDocument
from hwpxlib.constants import (
    CHARPR_BODY, CHARPR_BOLD, CHARPR_ITALIC, CHARPR_BOLD_ITALIC,
    CHARPR_INLINE_CODE,
)


def _segments_to_format_list(segments: list) -> list:
    """Convert TextSegments to the format expected by add_mixed_paragraph."""
    return [
        {
            "text": seg.text,
            "bold": seg.bold,
            "italic": seg.italic,
            "code": seg.code,
        }
        for seg in segments
    ]


def _segments_to_plain(segments: list) -> str:
    """Convert TextSegments to plain text."""
    return ''.join(seg.text for seg in segments)


def _has_formatting(segments: list) -> bool:
    """Check if segments have any formatting beyond plain text."""
    return any(seg.bold or seg.italic or seg.code for seg in segments)


def convert_md_to_hwpx(md_text: str) -> HwpxDocument:
    """Convert Markdown text to an HwpxDocument.

    Args:
        md_text: Raw Markdown string.

    Returns:
        HwpxDocument ready to save.
    """
    ast = parse_markdown(md_text)
    doc = HwpxDocument.new()

    for node in ast:
        if isinstance(node, Heading):
            doc.add_heading(node.text, level=node.level)

        elif isinstance(node, ParagraphNode):
            if _has_formatting(node.segments):
                doc.add_mixed_paragraph(_segments_to_format_list(node.segments))
            else:
                doc.add_paragraph(_segments_to_plain(node.segments))

        elif isinstance(node, TableNode):
            doc.add_table(
                headers=node.headers,
                rows=node.rows,
            )

        elif isinstance(node, CodeBlock):
            doc.add_code_block(node.code, language=node.language)

        elif isinstance(node, BulletList):
            items = []
            for item_segments in node.items:
                if _has_formatting(item_segments):
                    items.append(_segments_to_format_list(item_segments))
                else:
                    items.append(_segments_to_plain(item_segments))
            doc.add_bullet_list(items)

        elif isinstance(node, OrderedList):
            items = []
            for item_segments in node.items:
                if _has_formatting(item_segments):
                    items.append(_segments_to_format_list(item_segments))
                else:
                    items.append(_segments_to_plain(item_segments))
            doc.add_ordered_list(items)

        elif isinstance(node, HorizontalRule):
            doc.add_horizontal_rule()

        elif isinstance(node, BlockQuote):
            # Render blockquotes as italic paragraphs with indent
            if _has_formatting(node.segments):
                fmt = _segments_to_format_list(node.segments)
                # Add quote marker
                fmt.insert(0, {"text": "\u201C ", "italic": True})
                fmt.append({"text": " \u201D", "italic": True})
                doc.add_mixed_paragraph(fmt)
            else:
                text = _segments_to_plain(node.segments)
                doc.add_paragraph(f"\u201C{text}\u201D", italic=True)

    return doc


def convert_md_file(input_path: str, output_path: str = "") -> str:
    """Convert a Markdown file to HWPX.

    Args:
        input_path: Path to the .md file.
        output_path: Path for the .hwpx output. If empty, replaces .md with .hwpx.

    Returns:
        Path to the created .hwpx file.
    """
    if not output_path:
        if input_path.lower().endswith('.md'):
            output_path = input_path[:-3] + '.hwpx'
        else:
            output_path = input_path + '.hwpx'

    with open(input_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    doc = convert_md_to_hwpx(md_text)
    doc.save(output_path)
    return output_path
