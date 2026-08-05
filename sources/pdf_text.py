"""pdf_text — best-effort text extraction from IRS guidance PDFs. NOT a PDF parser.

This module exists for exactly one job: pull enough readable text out of an irs-drop PDF
(rp-26-28.pdf, n-26-44.pdf, ...) to run keyword/citation matching in `sources.relevance`.
It is deliberately crude, and its failure mode is deliberately loud-by-omission:

    extract_text() returns None when it cannot get usable text, and every caller must treat
    None as "unscoreable" — which `relevance.score()` maps to a MID-band score that surfaces
    the item to a human. Never to silence. A guidance item we could not read is exactly the
    item a person needs to look at.

Why stdlib (zlib + re) instead of pypdf/pdfminer: the repo has no PDF dependency
(`requirements.txt` is Django + DRF + psycopg + gunicorn + whitenoise + dj-database-url +
dotenv), and adding one buys a Render build cost and a supply-chain surface for a task that
is "find whether the string 1.199A-3 appears." Verified 2026-08-05 against the real
rp-26-28.pdf: FlateDecode streams decompress with zlib and the CFR header line is recoverable.

⚠ Text arrives KERN-SPLIT. PDF text operators emit runs like `26 C F R 1. 603 3 - 2`, so
matching MUST run on `squash()`-ed strings (lowercased, all whitespace removed) on BOTH sides.
Matching raw extracted text against a clean needle will silently miss.
"""
import re
import urllib.error
import urllib.request
import zlib

USER_AGENT = "Mozilla/5.0 (compatible; sherpa-tax-rule-studio change-register; +https://kenlill.com)"

MAX_PDF_BYTES = 8 * 1024 * 1024   # refuse anything larger; guidance PDFs are ~50-500 KB
DEFAULT_MAX_CHARS = 20_000        # plenty for a header + first pages; keeps scoring cheap
MIN_USABLE_ALPHA = 200            # below this we didn't really extract anything

_STREAM_RE = re.compile(rb"stream\r?\n(.*?)\r?\nendstream", re.DOTALL)
# A PDF string literal: (...) honouring backslash escapes. Does not handle nested unescaped
# parens (legal if balanced) — acceptable for best-effort.
_LITERAL_RE = re.compile(rb"\((?:\\.|[^\\()])*\)", re.DOTALL)
_OCTAL_RE = re.compile(rb"\\([0-7]{1,3})")

_SIMPLE_ESCAPES = {
    b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"\b", b"f": b"\f",
    b"(": b"(", b")": b")", b"\\": b"\\",
}


def squash(s: str) -> str:
    """Lowercase and remove ALL whitespace.

    The kern-split defence. `squash("26 C F R 1. 199 A-3")` == `squash("26 CFR 1.199A-3")`,
    so a needle and a haystack that differ only in PDF kerning still match.
    """
    return re.sub(r"\s+", "", s or "").lower()


def _unescape(raw: bytes) -> bytes:
    """Resolve PDF string escapes: octal (\\247 -> §), simple (\\n), and line continuations."""
    out = _OCTAL_RE.sub(lambda m: bytes([int(m.group(1), 8) & 0xFF]), raw)
    # Line continuation: a backslash immediately before a newline means "no character here".
    out = re.sub(rb"\\\r?\n", b"", out)

    def _simple(m):
        return _SIMPLE_ESCAPES.get(m.group(1), m.group(1))

    return re.sub(rb"\\(.)", _simple, out, flags=re.DOTALL)


def _decode_stream(blob: bytes) -> bytes | None:
    """FlateDecode if we can; fall back to raw. Returns None for streams we can't use."""
    try:
        return zlib.decompress(blob)
    except zlib.error:
        pass
    # Some producers leave a stray leading byte or use a raw deflate stream.
    for wbits in (-15, 47):
        try:
            return zlib.decompress(blob, wbits)
        except zlib.error:
            continue
    # Uncompressed content streams exist; only accept if it looks like text operators.
    return blob if b"Tj" in blob or b"TJ" in blob else None


def extract_text(pdf_bytes: bytes, max_chars: int = DEFAULT_MAX_CHARS) -> str | None:
    """Return best-effort text, or None if nothing usable came out.

    None is a first-class outcome, not an error — see the module docstring.
    """
    if not pdf_bytes:
        return None

    chunks: list[str] = []
    total = 0
    for m in _STREAM_RE.finditer(pdf_bytes):
        decoded = _decode_stream(m.group(1))
        if not decoded:
            continue
        for lit in _LITERAL_RE.finditer(decoded):
            body = lit.group(0)[1:-1]          # strip the surrounding parens
            if not body:
                continue
            # Latin-1: PDF simple fonts use WinAnsi/StandardEncoding, close enough that §
            # and the digits/letters we match on survive.
            text = _unescape(body).decode("latin-1", errors="replace")
            chunks.append(text)
            total += len(text)
            if total >= max_chars:
                break
        if total >= max_chars:
            break

    if not chunks:
        return None
    joined = " ".join(chunks)[:max_chars]
    if sum(c.isalpha() for c in joined) < MIN_USABLE_ALPHA:
        return None
    return joined


def fetch_pdf(url: str, max_bytes: int = MAX_PDF_BYTES) -> bytes | None:
    """Download a PDF, refusing oversized ones. Isolated so tests never hit the network.

    Returns None on any HTTP/size failure — callers treat that as unscoreable, same as
    unparseable text. A fetch failure must never abort an arm's whole run.
    """
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/pdf"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 (fixed https host)
            declared = resp.headers.get("Content-Length")
            if declared and declared.isdigit() and int(declared) > max_bytes:
                return None
            return resp.read(max_bytes)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None


def text_for_url(url: str, max_chars: int = DEFAULT_MAX_CHARS) -> str | None:
    """fetch + extract in one call. None on any failure (unscoreable)."""
    blob = fetch_pdf(url)
    return extract_text(blob, max_chars=max_chars) if blob else None
