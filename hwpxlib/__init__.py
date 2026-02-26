"""hwpxlib - Python HWPX (한글) document library."""

__version__ = "0.1.0"

from .document import HwpxDocument
from .models.body import PageSetup, HeaderFooter, Footnote, Endnote
from .style_config import StyleConfig
from .form import HwpxForm
