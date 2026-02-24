"""Security-focused tests for hwpxlib.

Covers:
- XML attribute injection prevention
- ZIP path traversal prevention
- Thread-safe ID generation
- MCP server input validation
"""
import threading
import xml.etree.ElementTree as ET

import pytest

from hwpxlib.xml_writer import (
    _esc, _esc_attr, _write_font_face, _write_style,
    set_id_seed, reset_id_seed, _unique_id,
)
from hwpxlib.package import HwpxPackage
from hwpxlib.models.head import Font, FontFace, Style


class TestXmlEscaping:
    """Verify XML escaping prevents injection."""

    def test_esc_handles_basic_entities(self):
        assert _esc('<script>') == '&lt;script&gt;'
        assert _esc('a & b') == 'a &amp; b'

    def test_esc_attr_escapes_double_quotes(self):
        result = _esc_attr('value" evil="injected')
        assert '"' not in result or '&quot;' in result
        assert '&quot;' in result

    def test_esc_attr_escapes_angle_brackets(self):
        result = _esc_attr('<evil>')
        assert '&lt;' in result
        assert '&gt;' in result

    def test_esc_attr_escapes_ampersand(self):
        result = _esc_attr('a&b')
        assert '&amp;' in result

    def test_font_face_with_malicious_name(self):
        """Font name containing " should not break XML attribute boundary."""
        evil_font = Font(id=0, face='Evil" onload="alert(1)', type="TTF")
        ff = FontFace(lang="HANGUL", fonts=[evil_font])
        xml = _write_font_face(ff)
        # Should produce valid XML (no unescaped quotes in attributes)
        assert '&quot;' in xml
        # Verify it parses as valid XML
        wrapped = f'<root xmlns:hh="http://test">{xml}</root>'
        tree = ET.fromstring(wrapped)
        font_el = tree.find('.//{http://test}font')
        assert font_el is not None
        # The face attribute should contain the original text (decoded)
        assert 'Evil" onload="alert(1)' == font_el.get('face')

    def test_style_with_malicious_name(self):
        """Style name containing " should not break XML attribute boundary."""
        s = Style(
            id=99, type="PARA", name='Evil" extra="x',
            eng_name='Bad" attr="y', para_pr_id_ref=0,
            char_pr_id_ref=0, next_style_id_ref=0, lang_id="1042",
        )
        xml = _write_style(s)
        assert '&quot;' in xml
        wrapped = f'<root xmlns:hh="http://test">{xml}</root>'
        tree = ET.fromstring(wrapped)
        style_el = tree.find('.//{http://test}style')
        assert style_el.get('name') == 'Evil" extra="x'


class TestZipPathTraversal:
    """Verify ZIP path traversal prevention."""

    def test_reject_dotdot_path(self):
        pkg = HwpxPackage()
        with pytest.raises(ValueError, match="traversal"):
            pkg.add_file("../../etc/passwd", b"evil")

    def test_reject_dotdot_in_middle(self):
        pkg = HwpxPackage()
        with pytest.raises(ValueError, match="traversal"):
            pkg.add_file("Contents/../../../evil.txt", b"evil")

    def test_reject_absolute_unix_path(self):
        pkg = HwpxPackage()
        with pytest.raises(ValueError, match="Absolute"):
            pkg.add_file("/etc/passwd", b"evil")

    def test_reject_absolute_windows_path(self):
        pkg = HwpxPackage()
        with pytest.raises(ValueError, match="Absolute"):
            pkg.add_file("C:\\Windows\\evil.dll", b"evil")

    def test_accept_valid_nested_path(self):
        pkg = HwpxPackage()
        pkg.add_file("Contents/section0.xml", b"<valid/>")
        assert "Contents/section0.xml" in pkg._files

    def test_accept_mimetype(self):
        pkg = HwpxPackage()
        pkg.add_file("mimetype", b"application/hwp+zip")
        assert "mimetype" in pkg._files

    def test_accept_meta_inf_path(self):
        pkg = HwpxPackage()
        pkg.add_file("META-INF/container.xml", b"<xml/>")
        assert "META-INF/container.xml" in pkg._files


class TestThreadSafeIdGeneration:
    """Verify ID generation is thread-safe."""

    def test_deterministic_seed_produces_same_ids(self):
        set_id_seed(42)
        ids_a = [_unique_id() for _ in range(10)]
        set_id_seed(42)
        ids_b = [_unique_id() for _ in range(10)]
        reset_id_seed()
        assert ids_a == ids_b

    def test_different_seeds_produce_different_ids(self):
        set_id_seed(42)
        ids_a = [_unique_id() for _ in range(10)]
        set_id_seed(99)
        ids_b = [_unique_id() for _ in range(10)]
        reset_id_seed()
        assert ids_a != ids_b

    def test_thread_isolation(self):
        """IDs generated in one thread should not affect another thread's sequence."""
        results = {}

        def generate_ids(thread_name, seed):
            set_id_seed(seed)
            results[thread_name] = [_unique_id() for _ in range(5)]
            reset_id_seed()

        t1 = threading.Thread(target=generate_ids, args=("t1", 42))
        t2 = threading.Thread(target=generate_ids, args=("t2", 99))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Each thread should get its own sequence
        assert results["t1"] != results["t2"]

        # Verify sequences are deterministic by re-running with same seeds
        set_id_seed(42)
        expected_t1 = [_unique_id() for _ in range(5)]
        reset_id_seed()
        set_id_seed(99)
        expected_t2 = [_unique_id() for _ in range(5)]
        reset_id_seed()

        assert results["t1"] == expected_t1
        assert results["t2"] == expected_t2


class TestMcpInputValidation:
    """Verify MCP server input validation functions."""

    def test_validate_document_path_accepts_hwpx(self):
        from mcp_server.server import _validate_document_path
        # Should not raise for valid extensions
        result = _validate_document_path("test.hwpx")
        assert result.endswith(".hwpx")

    def test_validate_document_path_accepts_hwp(self):
        from mcp_server.server import _validate_document_path
        result = _validate_document_path("test.hwp")
        assert result.endswith(".hwp")

    def test_validate_document_path_rejects_exe(self):
        from mcp_server.server import _validate_document_path
        with pytest.raises(ValueError, match="확장자"):
            _validate_document_path("evil.exe")

    def test_validate_document_path_rejects_bat(self):
        from mcp_server.server import _validate_document_path
        with pytest.raises(ValueError, match="확장자"):
            _validate_document_path("evil.bat")

    def test_validate_document_path_rejects_cmd(self):
        from mcp_server.server import _validate_document_path
        with pytest.raises(ValueError, match="확장자"):
            _validate_document_path("script.cmd")

    def test_validate_document_path_rejects_py(self):
        from mcp_server.server import _validate_document_path
        with pytest.raises(ValueError, match="확장자"):
            _validate_document_path("script.py")

    def test_validate_output_path_rejects_non_document(self):
        from mcp_server.server import _validate_output_path
        with pytest.raises(ValueError, match="확장자"):
            _validate_output_path("output.txt")
