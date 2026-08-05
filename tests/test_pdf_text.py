"""Tests for sources.pdf_text — the stdlib best-effort PDF extractor.

The contract under test is narrow and deliberate: get usable text, or return None so the caller
marks the item unscoreable and a human sees it. No database, no network.
"""
import zlib

from sources.pdf_text import extract_text, squash

# Enough alphabetic content to clear MIN_USABLE_ALPHA (200).
_BODY = (b"This revenue procedure provides guidance under section 199A and Form 4797 for "
         b"taxpayers computing the qualified business income deduction and the depreciation "
         b"limitation applicable to passenger automobiles placed in service during the year.")


def _fake_pdf(*text_runs: bytes, compress: bool = True) -> bytes:
    """Build a minimal PDF whose content stream holds the given string literals."""
    content = b" ".join(b"(" + t + b") Tj" for t in text_runs)
    blob = zlib.compress(content) if compress else content
    return (b"%PDF-1.4\n1 0 obj\n<< /Length " + str(len(blob)).encode() +
            b" /Filter /FlateDecode >>\nstream\n" + blob + b"\nendstream\nendobj\n%%EOF")


class TestSquash:
    def test_removes_all_whitespace_and_lowercases(self):
        assert squash("26 C F R  1. 199 A-3") == "26cfr1.199a-3"

    def test_kern_split_and_clean_forms_converge(self):
        """The whole point: the PDF's kerned text and a clean needle must land on one string."""
        assert squash("26 C F R  1. 603 3 - 2") == squash("26CFR1.6033-2")

    def test_preserves_hyphens_and_periods(self):
        """Only whitespace is stripped — '1.199a-3' must stay distinctive."""
        assert squash("1.199A-3") == "1.199a-3"

    def test_handles_none_and_empty(self):
        assert squash(None) == "" and squash("") == ""


class TestExtractText:
    def test_extracts_from_a_flate_stream(self):
        text = extract_text(_fake_pdf(_BODY))
        assert text is not None
        assert "revenue procedure" in text
        assert squash("section 199A") in squash(text)

    def test_extracts_from_an_uncompressed_stream(self):
        text = extract_text(_fake_pdf(_BODY, compress=False))
        assert text is not None and "revenue procedure" in text

    def test_joins_multiple_literals(self):
        text = extract_text(_fake_pdf(_BODY, b"Additional appendix content for the notice."))
        assert "appendix" in text

    def test_octal_escape_decodes_to_section_sign(self):
        text = extract_text(_fake_pdf(b"Amends \\247199A of the Code. " + _BODY))
        assert "§199A" in text

    def test_escaped_parens_survive(self):
        text = extract_text(_fake_pdf(b"Under section 461\\(l\\) limits. " + _BODY))
        assert "461(l)" in text

    def test_respects_max_chars(self):
        text = extract_text(_fake_pdf(_BODY * 50), max_chars=500)
        assert text is not None and len(text) <= 500


class TestUnusableInputReturnsNone:
    """None is a first-class outcome — callers map it to 'unscoreable', not to an error."""

    def test_empty_bytes(self):
        assert extract_text(b"") is None

    def test_garbage_bytes(self):
        assert extract_text(b"\x00\x01\x02 not a pdf at all \xff\xfe") is None

    def test_no_stream_markers(self):
        assert extract_text(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF") is None

    def test_too_little_text_to_be_usable(self):
        """A stream that decodes but yields almost nothing is a failure, not a result."""
        assert extract_text(_fake_pdf(b"Hi")) is None

    def test_undecodable_stream(self):
        body = b"stream\n" + b"\x9c\x00\xff\x11notzlib\x00" + b"\nendstream"
        assert extract_text(b"%PDF-1.4\n" + body) is None
