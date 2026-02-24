"""ZIP/OPC container management for HWPX files.

HWPX is a ZIP-based format. The 'mimetype' file MUST be the first entry
and stored uncompressed (no DEFLATE). All other XML files use DEFLATED compression.
"""
import posixpath
import zipfile
import io


class HwpxPackage:
    """Manages the ZIP container for a HWPX document."""

    def __init__(self):
        self._files: dict[str, bytes] = {}

    def add_file(self, path: str, content: bytes | str):
        """Add a file to the package.

        Raises ValueError if the path contains traversal sequences or is absolute.
        """
        # Reject absolute paths and path traversal
        if posixpath.isabs(path) or path.startswith('/') or path.startswith('\\'):
            raise ValueError(f"Absolute paths not allowed in ZIP entries: {path!r}")
        # Normalize and check for .. traversal
        normalized = posixpath.normpath(path)
        if normalized.startswith('..') or '/../' in normalized or normalized == '..':
            raise ValueError(f"Path traversal not allowed in ZIP entries: {path!r}")
        # Also reject Windows absolute paths (e.g., C:\...)
        if len(path) >= 2 and path[1] == ':':
            raise ValueError(f"Absolute paths not allowed in ZIP entries: {path!r}")

        if isinstance(content, str):
            content = content.encode('utf-8')
        self._files[path] = content

    def save(self, output_path: str):
        """Save the HWPX package as a ZIP file."""
        with zipfile.ZipFile(output_path, 'w') as zf:
            # mimetype MUST be first entry, STORED (not compressed)
            if 'mimetype' in self._files:
                zf.writestr(
                    zipfile.ZipInfo('mimetype'),
                    self._files['mimetype'],
                    compress_type=zipfile.ZIP_STORED,
                )

            # All other files use DEFLATED compression
            for path, content in self._files.items():
                if path == 'mimetype':
                    continue
                info = zipfile.ZipInfo(path)
                info.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(info, content)

    def to_bytes(self) -> bytes:
        """Return the HWPX package as bytes."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            if 'mimetype' in self._files:
                zf.writestr(
                    zipfile.ZipInfo('mimetype'),
                    self._files['mimetype'],
                    compress_type=zipfile.ZIP_STORED,
                )
            for path, content in self._files.items():
                if path == 'mimetype':
                    continue
                info = zipfile.ZipInfo(path)
                info.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(info, content)
        return buf.getvalue()
