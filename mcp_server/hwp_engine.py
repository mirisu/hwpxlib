"""pyhwpx-based document generation engine.

Converts Markdown AST (from md_parser) to native HWP documents
using pyhwpx COM automation. Provides singleton HWP instance management.
"""
import os
import atexit

from converters.md_parser import (
    parse_markdown, Heading, ParagraphNode, TableNode,
    CodeBlock, BulletList, HorizontalRule, BlockQuote,
)

# Font/size constants
HEADING_SIZES = {1: 22, 2: 16, 3: 13, 4: 11, 5: 10, 6: 10}
BODY_SIZE = 10
CODE_SIZE = 9
DEFAULT_FONT = "맑은 고딕"
CODE_FONT = "D2Coding"


class HwpEngine:
    """Singleton pyhwpx wrapper for MD-to-HWP conversion."""

    _hwp = None

    @classmethod
    def get_hwp(cls):
        """Get or create the HWP COM instance (lazy singleton)."""
        if cls._hwp is None:
            cls._hwp = cls._create_hwp()
        else:
            try:
                _ = cls._hwp.Version  # health check
            except Exception:
                cls._hwp = cls._create_hwp()
        return cls._hwp

    @classmethod
    def _create_hwp(cls):
        from pyhwpx import Hwp
        hwp = Hwp(visible=True)
        # Minimize window to keep out of the way
        try:
            import win32gui, win32con
            def _find_hwp(hwnd, results):
                title = win32gui.GetWindowText(hwnd)
                if 'Hwp' in title or '한글' in title or 'HWP' in title:
                    results.append(hwnd)
                return True
            wins = []
            win32gui.EnumWindows(_find_hwp, wins)
            for w in wins:
                win32gui.ShowWindow(w, win32con.SW_MINIMIZE)
        except Exception:
            pass
        return hwp

    @classmethod
    def cleanup(cls):
        """Release HWP COM object."""
        if cls._hwp is not None:
            try:
                cls._hwp.quit()
            except Exception:
                pass
            cls._hwp = None

    @classmethod
    def create_from_md(cls, md_text: str, output_path: str) -> str:
        """Convert markdown text to a HWP/HWPX document.

        Returns the absolute path of the saved file.
        """
        ast = parse_markdown(md_text)
        hwp = cls.get_hwp()
        hwp.clear(option=1)

        for node in ast:
            _dispatch(hwp, node)

        out = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        fmt = "HWPX" if out.lower().endswith(".hwpx") else "HWP"
        hwp.save_as(out, format=fmt)
        return out

    @classmethod
    def read_document(cls, path: str) -> str:
        """Extract plain text from a HWP/HWPX file."""
        hwp = cls.get_hwp()
        hwp.clear(option=1)  # discard current doc to avoid save prompt
        hwp.Open(os.path.abspath(path))
        hwp.Run("SelectAll")
        text = hwp.get_text_file(format="UNICODE", option="saveblock:true")
        hwp.clear(option=1)
        return text

    @classmethod
    def open_visible(cls, path: str) -> str:
        """Open file in HWP for interactive editing (launches HWP window)."""
        abspath = os.path.abspath(path)
        os.startfile(abspath)
        return abspath


# ── AST dispatch ──────────────────────────────────────────────

def _dispatch(hwp, node):
    handler = {
        Heading: _heading,
        ParagraphNode: _paragraph,
        TableNode: _table,
        CodeBlock: _code_block,
        BulletList: _bullet_list,
        HorizontalRule: _horizontal_rule,
        BlockQuote: _blockquote,
    }.get(type(node))
    if handler:
        handler(hwp, node)


# ── helpers ───────────────────────────────────────────────────

def _reset_font(hwp):
    """Reset to default body text formatting."""
    hwp.set_font(
        FaceName=DEFAULT_FONT, Height=BODY_SIZE,
        Bold=False, Italic=False, TextColor=0,
        UnderlineType=0, StrikeOutType=False,
    )


def _apply_segment_font(hwp, seg):
    """Set font matching a TextSegment's flags."""
    if seg.code:
        hwp.set_font(FaceName=CODE_FONT, Height=BODY_SIZE,
                      Bold=False, Italic=False, TextColor=0)
    else:
        hwp.set_font(FaceName=DEFAULT_FONT, Height=BODY_SIZE,
                      Bold=seg.bold, Italic=seg.italic, TextColor=0)


def _insert_segments(hwp, segments):
    """Insert a list of TextSegments with per-segment formatting."""
    for seg in segments:
        if not seg.text:
            continue
        _apply_segment_font(hwp, seg)
        hwp.insert_text(seg.text)


# ── node handlers ─────────────────────────────────────────────

def _heading(hwp, node):
    size = HEADING_SIZES.get(node.level, BODY_SIZE)
    # H1: dark navy, others: black
    color = hwp.rgb_color(0, 0, 128) if node.level == 1 else 0
    hwp.set_font(FaceName=DEFAULT_FONT, Height=size,
                  Bold=True, Italic=False, TextColor=color)
    hwp.insert_text(node.text)
    _reset_font(hwp)
    hwp.BreakPara()


def _paragraph(hwp, node):
    _insert_segments(hwp, node.segments)
    _reset_font(hwp)
    hwp.BreakPara()


def _table(hwp, node):
    if not node.headers:
        return

    num_cols = len(node.headers)
    num_rows = 1 + len(node.rows)

    hwp.create_table(rows=num_rows, cols=num_cols, header=True)

    # Build flat (text, is_header) list for all cells
    cells = [(h, True) for h in node.headers]
    for row in node.rows:
        padded = (row + [''] * num_cols)[:num_cols]
        cells.extend((c, False) for c in padded)

    for i, (text, is_header) in enumerate(cells):
        hwp.set_font(FaceName=DEFAULT_FONT, Height=BODY_SIZE,
                      Bold=is_header, Italic=False, TextColor=0)
        if text:
            hwp.insert_text(str(text))
        if i < len(cells) - 1:
            hwp.Run("TableRightCell")

    # Exit table → document level
    _reset_font(hwp)
    hwp.Run("MoveDocEnd")
    hwp.BreakPara()


def _code_block(hwp, node):
    hwp.set_font(FaceName=CODE_FONT, Height=CODE_SIZE,
                  Bold=False, Italic=False, TextColor=0)
    lines = node.code.split('\n')
    for i, line in enumerate(lines):
        if line:
            hwp.insert_text(line)
        if i < len(lines) - 1:
            hwp.BreakPara()
            # Re-apply code font for new paragraph
            hwp.set_font(FaceName=CODE_FONT, Height=CODE_SIZE,
                          Bold=False, Italic=False, TextColor=0)
    _reset_font(hwp)
    hwp.BreakPara()


def _bullet_list(hwp, node):
    for item_segments in node.items:
        _reset_font(hwp)
        hwp.insert_text("\u2022 ")  # bullet character
        _insert_segments(hwp, item_segments)
        _reset_font(hwp)
        hwp.BreakPara()


def _horizontal_rule(hwp, _node):
    gray = hwp.rgb_color(180, 180, 180)
    hwp.set_font(FaceName=DEFAULT_FONT, Height=BODY_SIZE,
                  Bold=False, Italic=False, TextColor=gray)
    hwp.insert_text("\u2501" * 50)  # ━ heavy horizontal
    _reset_font(hwp)
    hwp.BreakPara()


def _blockquote(hwp, node):
    gray = hwp.rgb_color(100, 100, 100)
    hwp.set_font(FaceName=DEFAULT_FONT, Height=BODY_SIZE,
                  Bold=False, Italic=True, TextColor=gray)
    hwp.insert_text("\u2502 ")  # │ vertical bar prefix
    for seg in node.segments:
        if not seg.text:
            continue
        hwp.set_font(FaceName=DEFAULT_FONT, Height=BODY_SIZE,
                      Bold=seg.bold, Italic=True, TextColor=gray)
        hwp.insert_text(seg.text)
    _reset_font(hwp)
    hwp.BreakPara()


# Cleanup HWP process on interpreter exit
atexit.register(HwpEngine.cleanup)
