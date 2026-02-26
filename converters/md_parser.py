"""Markdown parser - regex-based, zero external dependencies.

Parses Markdown into an intermediate AST (Abstract Syntax Tree).
Supports: headings, bold, italic, inline code, tables, fenced code blocks,
bullet lists, horizontal rules, blockquotes, and regular paragraphs.
"""
import re
from dataclasses import dataclass, field
from typing import Union


# === AST Node Types ===

@dataclass
class TextSegment:
    """A segment of text with formatting."""
    text: str = ""
    bold: bool = False
    italic: bool = False
    code: bool = False
    strikethrough: bool = False
    link: str = ""  # URL if this is a hyperlink


@dataclass
class Heading:
    """ATX heading (# to ######)."""
    level: int = 1
    text: str = ""
    segments: list = field(default_factory=list)  # list of TextSegment


@dataclass
class ParagraphNode:
    """A paragraph with mixed formatting."""
    segments: list = field(default_factory=list)  # list of TextSegment


@dataclass
class TableNode:
    """GFM table."""
    headers: list = field(default_factory=list)   # list of str
    rows: list = field(default_factory=list)       # list of list of str


@dataclass
class CodeBlock:
    """Fenced code block."""
    code: str = ""
    language: str = ""


@dataclass
class BulletList:
    """Bullet list."""
    items: list = field(default_factory=list)  # list of (segments, level) tuples


@dataclass
class OrderedList:
    """Ordered (numbered) list."""
    items: list = field(default_factory=list)  # list of (segments, level) tuples


@dataclass
class HorizontalRule:
    """Horizontal rule (---, ***, ___)."""
    pass


@dataclass
class BlockQuote:
    """Block quote."""
    segments: list = field(default_factory=list)  # list of TextSegment


# Type alias for AST nodes
ASTNode = Union[Heading, ParagraphNode, TableNode, CodeBlock,
                BulletList, OrderedList, HorizontalRule, BlockQuote]


# === Inline Formatting Parser ===

def parse_inline(text: str) -> list:
    """Parse inline formatting (bold, italic, code) into TextSegments.

    Handles: ***bold italic***, **bold**, *italic*, `code`
    """
    segments = []
    # Pattern: link > code > strikethrough > bold_italic > bold > italic > plain
    pattern = re.compile(
        r'\[([^\]]+)\]\(([^)]+)\)'         # [text](url)  groups 1,2
        r'|`([^`]+)`'                       # inline code  group 3
        r'|~~(.+?)~~'                       # strikethrough group 4
        r'|\*\*\*(.+?)\*\*\*'             # bold+italic  group 5
        r'|\*\*(.+?)\*\*'                 # bold         group 6
        r'|\*(.+?)\*'                      # italic       group 7
        r'|([^`*~\[]+|[~](?!~))'          # plain text   group 8
    )

    for m in pattern.finditer(text):
        if m.group(1) is not None:
            segments.append(TextSegment(text=m.group(1), link=m.group(2)))
        elif m.group(3) is not None:
            segments.append(TextSegment(text=m.group(3), code=True))
        elif m.group(4) is not None:
            segments.append(TextSegment(text=m.group(4), strikethrough=True))
        elif m.group(5) is not None:
            segments.append(TextSegment(text=m.group(5), bold=True, italic=True))
        elif m.group(6) is not None:
            segments.append(TextSegment(text=m.group(6), bold=True))
        elif m.group(7) is not None:
            segments.append(TextSegment(text=m.group(7), italic=True))
        elif m.group(8) is not None:
            segments.append(TextSegment(text=m.group(8)))

    return segments if segments else [TextSegment(text=text)]


# === Block-Level Parser ===

# Regex patterns for block elements
RE_HEADING = re.compile(r'^(#{1,6})\s+(.+?)(?:\s+#+)?$')
RE_HR = re.compile(r'^(?:---+|\*\*\*+|___+)\s*$')
RE_FENCE_START = re.compile(r'^```(\w*)\s*$')
RE_FENCE_END = re.compile(r'^```\s*$')
RE_BULLET = re.compile(r'^(\s*)[-*+]\s+(.+)$')
RE_TABLE_ROW = re.compile(r'^\|(.+)\|\s*$')
RE_TABLE_SEP = re.compile(r'^\|[\s:]*[-]+[\s:]*')
RE_ORDERED = re.compile(r'^(\s*)\d+[.)]\s+(.+)$')
RE_BLOCKQUOTE = re.compile(r'^>\s*(.*)')


def parse_markdown(text: str) -> list:
    """Parse Markdown text into a list of AST nodes.

    Args:
        text: Raw Markdown string.

    Returns:
        List of ASTNode objects.
    """
    lines = text.split('\n')
    ast = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip completely empty lines
        if not line.strip():
            i += 1
            continue

        # --- Fenced code block ---
        m = RE_FENCE_START.match(line)
        if m:
            language = m.group(1)
            code_lines = []
            i += 1
            while i < len(lines) and not RE_FENCE_END.match(lines[i]):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            ast.append(CodeBlock(code='\n'.join(code_lines), language=language))
            continue

        # --- Horizontal rule ---
        if RE_HR.match(line):
            ast.append(HorizontalRule())
            i += 1
            continue

        # --- Heading ---
        m = RE_HEADING.match(line)
        if m:
            level = len(m.group(1))
            heading_text = m.group(2).strip()
            segments = parse_inline(heading_text)
            ast.append(Heading(level=level, text=heading_text, segments=segments))
            i += 1
            continue

        # --- Table ---
        m = RE_TABLE_ROW.match(line)
        if m:
            # Parse header row
            header_cells = [c.strip() for c in m.group(1).split('|')]
            i += 1
            # Skip separator row
            if i < len(lines) and RE_TABLE_SEP.match(lines[i]):
                i += 1
            # Parse data rows
            data_rows = []
            while i < len(lines):
                rm = RE_TABLE_ROW.match(lines[i])
                if rm:
                    row_cells = [c.strip() for c in rm.group(1).split('|')]
                    data_rows.append(row_cells)
                    i += 1
                else:
                    break
            ast.append(TableNode(headers=header_cells, rows=data_rows))
            continue

        # --- Bullet list ---
        m = RE_BULLET.match(line)
        if m:
            items = []
            while i < len(lines):
                bm = RE_BULLET.match(lines[i])
                if bm:
                    indent = len(bm.group(1))
                    level = min(indent // 2, 2)
                    item_text = bm.group(2)
                    items.append((parse_inline(item_text), level))
                    i += 1
                elif lines[i].strip() == '':
                    break
                else:
                    break
            ast.append(BulletList(items=items))
            continue

        # --- Ordered list ---
        m = RE_ORDERED.match(line)
        if m:
            items = []
            while i < len(lines):
                om = RE_ORDERED.match(lines[i])
                if om:
                    indent = len(om.group(1))
                    level = min(indent // 2, 2)
                    item_text = om.group(2)
                    items.append((parse_inline(item_text), level))
                    i += 1
                elif lines[i].strip() == '':
                    break
                else:
                    break
            ast.append(OrderedList(items=items))
            continue

        # --- Block quote ---
        m = RE_BLOCKQUOTE.match(line)
        if m:
            quote_lines = []
            while i < len(lines):
                qm = RE_BLOCKQUOTE.match(lines[i])
                if qm:
                    quote_lines.append(qm.group(1))
                    i += 1
                elif lines[i].strip() == '':
                    break
                else:
                    break
            quote_text = ' '.join(quote_lines)
            ast.append(BlockQuote(segments=parse_inline(quote_text)))
            continue

        # --- Regular paragraph ---
        # Collect contiguous non-blank, non-special lines
        para_lines = []
        while i < len(lines):
            if not lines[i].strip():
                break
            # Check if next line is a block element
            if (RE_HEADING.match(lines[i]) or
                RE_HR.match(lines[i]) or
                RE_FENCE_START.match(lines[i]) or
                RE_BULLET.match(lines[i]) or
                RE_ORDERED.match(lines[i]) or
                RE_TABLE_ROW.match(lines[i]) or
                RE_BLOCKQUOTE.match(lines[i])):
                if para_lines:  # already have content, stop here
                    break
            para_lines.append(lines[i])
            i += 1

        if para_lines:
            para_text = ' '.join(para_lines)
            ast.append(ParagraphNode(segments=parse_inline(para_text)))

    return ast
