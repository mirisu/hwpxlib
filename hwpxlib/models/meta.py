"""Meta file models: version, settings, content.hpf, container files."""
from dataclasses import dataclass


@dataclass
class DocumentMeta:
    """Document metadata."""
    title: str = ""
    language: str = "ko"
    creator: str = ""
    subject: str = ""
    description: str = ""
