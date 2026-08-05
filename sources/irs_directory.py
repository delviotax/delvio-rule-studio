"""irs_directory — one parser for the two irs.gov file-listing indexes.

`irs-drop` (individual guidance: Rev. Procs, Notices, Rev. Ruls, Announcements) and `irs-dft`
(draft forms/instructions/pubs) are the same Drupal view with a 4-column table:

    Name | Date | Size | Description

Both are the machine-readable surface for content that has no API — govinfo carries no Internal
Revenue Bulletin collection and irs.gov exposes no guidance API, so the listing IS the feed.
`irs-drop` matters most: individual items land here WEEKS before the weekly IRB bundles them,
which is the gap `fetch_irb`'s bulletin-level detection leaves open.

Verified live 2026-08-05 — 50 rows/page, already sorted date-descending, `?page=N` (0-indexed;
irs-drop ran to page 90, irs-dft to page 24, i.e. the indexes are full historical archives, so
default to page 0 only).

⚠ USE THE `/downloads/` PATH. `https://www.irs.gov/pub/irs-drop/` 301-redirects to
`http://www.irs.gov/downloads/irs-drop/` (note: to HTTP). Individual FILE links keep the
`/pub/...` form and are absolute in the href — those are fine to use as-is.

⚠ DESCRIPTIONS ARE NOT A RELIABLE FORMAT. Real irs-drop rows carry 'Rev. Proc.  2026-28' (two
spaces), 'Rev. Proc. 2026-26', 'RR-2026-13', 'N-2026-44'. Derive the designation from the
FILENAME (consistently `rp-`/`n-`/`rr-`/`a-`); treat the description as supplementary text only.
irs-dft descriptions are better structured ('2026 Inst 8615 (PDF)') but heavily space-padded.
"""
from __future__ import annotations

import datetime as _dt
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

BASE = "https://www.irs.gov/downloads"
USER_AGENT = "Mozilla/5.0 (compatible; sherpa-tax-rule-studio change-register; +https://kenlill.com)"

DROP = "irs-drop"
DFT = "irs-dft"

# The verified 4-cell row. DOTALL because cells are separated by long whitespace runs.
INDEX_ROW_RE = re.compile(
    r'<td[^>]*views-field-uri[^>]*>\s*<a href="(?P<url>[^"]+/(?P<filename>[^/"]+))"[^>]*>.*?</a>\s*</td>.*?'
    r'<td[^>]*views-field-field-pup-posted[^>]*>\s*(?P<posted>\d{4}-\d{2}-\d{2})[^<]*</td>.*?'
    r'<td[^>]*views-field-filesize[^>]*>\s*(?P<size>[^<]*?)\s*</td>.*?'
    r'<td[^>]*views-field-name[^>]*>\s*(?P<desc>.*?)\s*</td>',
    re.DOTALL | re.IGNORECASE,
)

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


class IndexLayoutError(RuntimeError):
    """The index parsed to zero rows — the page layout probably changed.

    Raised rather than returning [] on purpose: a silently-empty scrape looks identical to
    "nothing new published," and a detection arm that has quietly stopped detecting is the
    worst failure mode this system has.
    """


@dataclass(frozen=True)
class Row:
    filename: str          # 'rp-26-28.pdf' / 'i8615--dft.pdf'
    url: str               # absolute, as published in the href
    posted_at: _dt.date
    size: str              # '88.05 KB' — display only
    description: str       # whitespace-collapsed


def _clean(html_fragment: str) -> str:
    """Strip tags/entities-lite and collapse the Drupal padding to single spaces."""
    text = _TAG_RE.sub("", html_fragment or "")
    text = text.replace("&amp;", "&").replace("&nbsp;", " ").replace("&#039;", "'")
    return _WS_RE.sub(" ", text).strip()


def parse_index(html: str) -> list[Row]:
    """Parse listing HTML into Rows (page order = newest first). Raises IndexLayoutError on zero."""
    rows: list[Row] = []
    for m in INDEX_ROW_RE.finditer(html or ""):
        try:
            posted = _dt.date.fromisoformat(m.group("posted"))
        except ValueError:
            continue
        rows.append(Row(
            filename=m.group("filename").strip(),
            url=m.group("url").strip(),
            posted_at=posted,
            size=_clean(m.group("size")),
            description=_clean(m.group("desc")),
        ))
    if not rows:
        raise IndexLayoutError(
            "Parsed 0 rows from an irs.gov directory index — the Drupal table layout may have "
            "changed (update INDEX_ROW_RE in sources/irs_directory.py)."
        )
    return rows


def fetch_index(slug: str, page: int = 0) -> str:
    """Fetch one listing page. Isolated so tests monkeypatch here and never hit the network."""
    url = f"{BASE}/{slug}" + (f"?page={page}" if page else "")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 (fixed https host)
        return resp.read().decode("utf-8", errors="replace")


def iter_rows(slug: str, pages: int = 1) -> list[Row]:
    """Fetch and parse `pages` listing pages, de-duplicated by filename, newest first.

    A later page failing does not discard earlier pages — partial coverage beats none, and the
    caller reports what it got. A FIRST-page failure propagates (nothing was collected).
    """
    seen: set[str] = set()
    out: list[Row] = []
    for page in range(max(1, pages)):
        try:
            html = fetch_index(slug, page=page)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
            if page == 0:
                raise
            break
        for row in parse_index(html):
            if row.filename in seen:
                continue
            seen.add(row.filename)
            out.append(row)
    out.sort(key=lambda r: r.posted_at, reverse=True)
    return out


# ── Filename decoding ──────────────────────────────────────────────────────

DROP_KINDS = {"rp": "Rev. Proc.", "n": "Notice", "rr": "Rev. Rul.", "a": "Announcement"}

# rp-26-28.pdf / n-26-39-appendix-2.xlsx / a-26-5.pdf
DROP_FILENAME_RE = re.compile(
    r"^(?P<kind>rp|n|rr|a)-(?P<yy>\d{2})-(?P<num>\d{1,3})(?P<suffix>[-a-z0-9]*)\.(?P<ext>pdf|xlsx?)$",
    re.IGNORECASE,
)

# f1040--dft.pdf / i1040sr--dft.pdf / p17--dft.pdf
DFT_FILENAME_RE = re.compile(r"^(?P<kind>[fip])(?P<stem>[a-z0-9]+)--dft\.(?P<ext>pdf|xlsx?)$", re.IGNORECASE)

# '2026 Inst 1040 (Schedule R)  (PDF)' | '1226 Form 9465 (sp)  (PDF)'
DFT_DESC_RE = re.compile(
    r"^(?P<lead>\d{4})\s+(?P<kind>Form|Inst|Publ?)\s+(?P<form>[^(]+?)"
    r"(?:\s*\((?P<sched>Schedule [^)]+)\))?"
    r"(?:\s*\((?P<sp>sp)\))?\s*\(PDF\)\s*$",
    re.IGNORECASE,
)

DFT_KINDS = {"f": "Form", "i": "Instructions", "p": "Publication"}


def decode_drop(row: Row) -> dict | None:
    """Decode an irs-drop filename into its designation. None if it isn't a guidance file."""
    m = DROP_FILENAME_RE.match(row.filename)
    if not m:
        return None
    kind = m.group("kind").lower()
    year = 2000 + int(m.group("yy"))
    number = int(m.group("num"))
    label = DROP_KINDS[kind]
    designation = f"{label} {year}-{number}"
    suffix = (m.group("suffix") or "").strip("-")
    if suffix:
        designation += f" ({suffix.replace('-', ' ')})"
    return {
        "kind": kind,
        "designation": designation,
        "label": label,
        "year": year,
        "number": number,
        "is_appendix": bool(suffix),
        "ext": m.group("ext").lower(),
    }


def decode_dft(row: Row) -> dict | None:
    """Decode an irs-dft row. Prefers the structured description; falls back to the filename.

    The description is rich enough that no PDF fetch is needed — form number, kind and year come
    straight out of the index, so the perimeter filter on this arm is exact and free.

    `lead` is a tax year when it looks like one (2000-2100), otherwise an MMYY revision stamp
    ('1226' = Dec 2026).
    """
    fm = DFT_FILENAME_RE.match(row.filename)
    kind_letter = (fm.group("kind").lower() if fm else "")

    dm = DFT_DESC_RE.match(row.description or "")
    if not dm:
        if not fm:
            return None
        return {"kind": DFT_KINDS.get(kind_letter, "Form"), "form": fm.group("stem").upper(),
                "schedule": None, "tax_year": None, "revision": None, "is_spanish": False}

    lead = int(dm.group("lead"))
    tax_year = lead if 2000 <= lead <= 2100 else None
    revision = None if tax_year else dm.group("lead")
    kind_word = dm.group("kind").title()
    return {
        "kind": {"Form": "Form", "Inst": "Instructions", "Publ": "Publication",
                 "Pub": "Publication"}.get(kind_word, kind_word),
        "form": (dm.group("form") or "").strip().upper(),
        "schedule": (dm.group("sched") or "").strip() or None,
        "tax_year": tax_year,
        "revision": revision,
        "is_spanish": bool(dm.group("sp")),
    }
