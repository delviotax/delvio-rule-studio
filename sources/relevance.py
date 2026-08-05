"""relevance — does a detected change touch OUR perimeter, and how much?

The signal-to-noise layer for the detection arms. `irs-drop` posts ~8 guidance items/month and
`irs-dft` ~6 draft forms/day; most touch forms we don't file. This module scores each item so
`change_digest` can rank, without ever deciding what gets recorded.

TWO INVARIANTS — both load-bearing, do not "optimize" either away:

  1. THE SCORE ORDERS; IT NEVER GATES. Every parsed item becomes a DETECTED row regardless of
     score. Callers may use the score to rank and to set a DISPLAY threshold; they must not use
     it to skip creation. A change suppressed at write time is invisible forever, which is the
     exact silent error `tts-tax-status/CHANGE_REGISTER.md` forbids — "AI/automation may DETECT
     and TRIAGE; it must NEVER implement" cuts both ways: it may not un-detect either.
     (`fetch_irs_drafts` is the one allowed exception, and only because its filter is an EXACT
     structured form-number match, not a fuzzy text score. It logs what it dropped.)

  2. UNSCOREABLE FAILS TOWARD THE HUMAN. Text we couldn't read scores UNSCOREABLE_SCORE (mid-band)
     with an explicit signal, never 0. An item we could not parse is precisely the item a person
     should look at.

The perimeter is INHERITED, not hardcoded: form tokens come from `specs.TaxForm` and
`AuthorityFormLink`, section tokens from `AuthoritySource`. Author a new form in Rule Studio and
the scorer starts recognising it. Only the keyword and hard-negative lists are curated here.

⚠ All matching runs on `pdf_text.squash()`-ed strings — lowercased, whitespace removed — because
IRS PDF text arrives kern-split (`26 C F R 1. 603 3 - 2`). Needles are squashed too. Note squash
strips WHITESPACE ONLY: hyphens and periods survive, so `1.199a-3` stays distinctive.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from sources.pdf_text import squash

# ── Weights ────────────────────────────────────────────────────────────────
W_FORM = 40          # exact form-number hit on a form we actually spec
W_IRC = 30           # IRC section we cite as an authority
W_CFR = 25           # 26 CFR section matching an authority citation
W_KEYWORD = 15       # curated perimeter topic keyword
W_ENTITY = 10        # perimeter entity family (1040/1120-S/1065/1041)
W_JURISDICTION = 10  # perimeter jurisdiction named
W_HARD_NEGATIVE = -60

UNSCOREABLE_SCORE = 50   # mid-band: "a human must look at this"
SCORE_MIN, SCORE_MAX = 0, 100

# Default display threshold for the digest's above-the-line section. A DISPLAY knob only.
DEFAULT_DIGEST_THRESHOLD = 25

# ── Curated vocabulary ─────────────────────────────────────────────────────
# Topics that matter to the forms we file. Kept short and high-precision; the form/section
# tokens carry most of the weight and come from the database.
PERIMETER_KEYWORDS = (
    "inflation adjustment", "inflation adjusted", "standard deduction", "standard mileage",
    "optional standard mileage", "tax rate table", "tax rate schedule",
    "qualified business income", "section 199A", "bonus depreciation", "section 179",
    "depreciation limitation", "luxury automobile", "passenger automobile",
    "SALT cap", "state and local tax deduction", "senior deduction",
    "qualified tips", "qualified overtime", "car loan interest",
    "excess business loss", "section 461(l)", "net operating loss",
    "earned income credit", "child tax credit", "premium tax credit",
    "self-employment tax", "limited partner", "retirement plan limit",
    "underpayment rate", "overpayment rate", "automatic change", "accounting method",
    "OBBBA", "One Big Beautiful Bill",
)

# Entity families we file. Weak signal on their own — a document mentioning "Form 1065"
# without a specific provision is still worth a nudge.
PERIMETER_ENTITIES = ("1040", "1120-S", "1120S", "1065", "1041")

# Jurisdictions in the perimeter. NOTE: the 2026-08-05 "federal only" decision governs which
# detection ARMS get built (no state page-diff arm yet) — it does not mean the scorer should be
# blind to a federal document that names Georgia. GA/SC/AL/NC stay recognised here.
PERIMETER_JURISDICTIONS = ("FED", "US", "GA", "SC", "AL", "NC")

# Strong "this is not us" markers. Only ever applied when NOTHING positive fired — see score().
HARD_NEGATIVE_FORMS = ("990", "706", "709", "5500", "8038", "720", "940", "941",
                       "1120-POL", "4461", "8971", "2438", "1075", "5227", "8038-G")
HARD_NEGATIVE_KEYWORDS = (
    "exempt organization", "tax-exempt organization", "estate tax return", "generation-skipping",
    "gift tax", "excise tax", "tax-exempt bond", "employee plans determination",
    "private foundation", "unrelated business income", "political organization",
)

# ── Token extraction ───────────────────────────────────────────────────────
_IRC_FROM_CODE_RE = re.compile(r"^IRC[_-]?(\d+[A-Za-z]?(?:\(\w+\))?)$", re.IGNORECASE)
_IRC_FROM_CITATION_RE = re.compile(r"(?:§+\s*|26\s*U\.?S\.?C\.?\s*§?\s*|section\s+)(\d+[A-Za-z]?)", re.IGNORECASE)
_CFR_FROM_CITATION_RE = re.compile(r"26\s*CFR\s*(\d+\.[\w.-]+)", re.IGNORECASE)


def normalize_jurisdiction(code: str | None) -> str:
    """Canonicalise the FED/US split.

    `AuthoritySource` seeds federal rows as 'FED' (see sources/federal_data/irc_sections.py)
    while `ChangeRegisterItem.jurisdiction_code` defaults to 'US' and all three original arms
    hardcode 'US'. Both mean the same thing. Canonical = 'US'; 'FED' is the alias. Without this,
    any future join on jurisdiction silently misses half the rows.
    """
    if not code:
        return ""
    up = code.strip().upper()
    return "US" if up in {"FED", "FEDERAL", "US"} else up


def _form_needles(form_code: str) -> list[str]:
    """Squashed needles for a form number, with enough context to avoid bare-number collisions.

    A bare '4797' would match a page number or a dollar amount. Requiring 'form4797' /
    'schedule4797' costs a little recall and buys a lot of precision.
    """
    raw = (form_code or "").strip()
    if not raw:
        return []
    low = raw.lower()
    variants = {low, low.replace("-", ""), low.replace(" ", "")}
    out: set[str] = set()
    for v in variants:
        if v.startswith("sch"):                       # 'Schedule D' / 'SCH_D' / 'schd'
            tail = v.replace("schedule", "").replace("sch_", "").replace("sch", "").strip("_-")
            if tail:
                out.add(squash(f"schedule{tail}"))
                out.add(squash(f"sch{tail}"))
        else:
            out.add(squash(f"form{v}"))
            out.add(squash(f"forms{v}"))
            out.add(squash(f"instructionsforform{v}"))
    return sorted(n for n in out if n)


def _irc_needles(section: str) -> list[str]:
    s = (section or "").strip().lower()
    if not s:
        return []
    return [squash(f"§{s}"), squash(f"section{s}"), squash(f"irc{s}")]


@dataclass
class PerimeterIndex:
    """Everything the scorer matches against, built once per arm run."""

    form_needles: dict[str, list[str]] = field(default_factory=dict)   # form_code -> needles
    irc_needles: dict[str, list[str]] = field(default_factory=dict)    # '199A' -> needles
    cfr_sections: set[str] = field(default_factory=set)                # '1.199a-3' (squashed)
    keyword_needles: dict[str, str] = field(default_factory=dict)      # keyword -> squashed
    entity_needles: dict[str, list[str]] = field(default_factory=dict)
    jurisdictions: set[str] = field(default_factory=set)
    hard_negative_forms: dict[str, list[str]] = field(default_factory=dict)
    hard_negative_keywords: dict[str, str] = field(default_factory=dict)

    @property
    def is_empty(self) -> bool:
        """True when the DB carried no forms/authorities — scoring would be meaningless."""
        return not self.form_needles and not self.irc_needles and not self.cfr_sections


def build_perimeter_index(*, include_db: bool = True) -> PerimeterIndex:
    """Assemble the index from the curated lists plus (optionally) the Rule Studio tables.

    `include_db=False` yields a keyword/entity-only index — used by unit tests that must not
    touch the database, and as the graceful degradation path if the tables are empty.
    """
    idx = PerimeterIndex(
        keyword_needles={k: squash(k) for k in PERIMETER_KEYWORDS},
        entity_needles={e: _form_needles(e) for e in PERIMETER_ENTITIES},
        jurisdictions={normalize_jurisdiction(j) for j in PERIMETER_JURISDICTIONS},
        hard_negative_forms={f: _form_needles(f) for f in HARD_NEGATIVE_FORMS},
        hard_negative_keywords={k: squash(k) for k in HARD_NEGATIVE_KEYWORDS},
    )
    if not include_db:
        return idx

    # Imported lazily so the module is importable (and testable) without Django app loading.
    from sources.models import AuthorityFormLink, AuthoritySource
    from specs.models import TaxForm

    form_codes: set[str] = set()
    form_codes.update(TaxForm.objects.values_list("form_number", flat=True))
    form_codes.update(AuthorityFormLink.objects.values_list("form_code", flat=True))
    for code in form_codes:
        needles = _form_needles(code)
        if needles:
            idx.form_needles[code] = needles

    for source_code, citation in AuthoritySource.objects.values_list("source_code", "citation"):
        m = _IRC_FROM_CODE_RE.match(source_code or "")
        if m:
            sec = m.group(1)
            idx.irc_needles.setdefault(sec, _irc_needles(sec))
        if citation:
            for sec in _IRC_FROM_CITATION_RE.findall(citation):
                idx.irc_needles.setdefault(sec, _irc_needles(sec))
            for cfr in _CFR_FROM_CITATION_RE.findall(citation):
                idx.cfr_sections.add(squash(cfr))

    return idx


def _sig(kind: str, value: str, via: str, weight: int) -> dict:
    return {"kind": kind, "value": value, "via": via, "weight": weight}


def score(
    text: str | None,
    *,
    index: PerimeterIndex,
    forms: tuple | list = (),
    sections: tuple | list = (),
    cfr: tuple | list = (),
    jurisdiction: str | None = None,
) -> tuple[int, list[dict]]:
    """Score an item 0-100 and return the signals that produced it.

    `text` is free prose (title + description + extracted PDF text). `forms` / `sections` / `cfr`
    are STRUCTURED hints an arm already parsed — e.g. `fetch_ecfr_title26` passes the section
    identifier directly rather than hoping to find it in prose.

    Returns (score, signals). `text=None` (unreadable PDF) yields UNSCOREABLE_SCORE — never 0 —
    unless structured hints alone already produce a match.
    """
    signals: list[dict] = []
    hay = squash(text) if text else ""

    # ── Structured hints (exact, no text needed) ───────────────────────────
    for f in forms:
        if f and f in index.form_needles:
            signals.append(_sig("form", str(f), "structured", W_FORM))
    for s in sections:
        if s and s in index.irc_needles:
            signals.append(_sig("irc", str(s), "structured", W_IRC))
    for c in cfr:
        if c and squash(str(c)) in index.cfr_sections:
            signals.append(_sig("cfr", str(c), "structured", W_CFR))

    juris = normalize_jurisdiction(jurisdiction)
    if juris and juris in index.jurisdictions:
        signals.append(_sig("jurisdiction", juris, "structured", W_JURISDICTION))

    # ── Text matching ──────────────────────────────────────────────────────
    if hay:
        for code, needles in index.form_needles.items():
            if any(n in hay for n in needles):
                signals.append(_sig("form", code, "text", W_FORM))
        for sec, needles in index.irc_needles.items():
            if any(n in hay for n in needles):
                signals.append(_sig("irc", sec, "text", W_IRC))
        for cfr_sec in index.cfr_sections:
            if cfr_sec in hay:
                signals.append(_sig("cfr", cfr_sec, "text", W_CFR))
        for kw, needle in index.keyword_needles.items():
            if needle in hay:
                signals.append(_sig("keyword", kw, "text", W_KEYWORD))
        for ent, needles in index.entity_needles.items():
            if any(n in hay for n in needles):
                signals.append(_sig("entity", ent, "text", W_ENTITY))

    # De-duplicate: structured and text can both fire on the same token; count it once,
    # keeping the structured attribution (it's the stronger evidence).
    deduped: dict[tuple, dict] = {}
    for s in signals:
        key = (s["kind"], str(s["value"]).lower())
        if key not in deduped or s["via"] == "structured":
            deduped[key] = s
    signals = list(deduped.values())

    has_positive_anchor = any(s["kind"] in {"form", "irc", "cfr"} for s in signals)

    # ── Hard negatives — only when nothing positive anchored ───────────────
    if hay and not has_positive_anchor:
        neg: list[dict] = []
        for code, needles in index.hard_negative_forms.items():
            if any(n in hay for n in needles):
                neg.append(_sig("out_of_perimeter_form", code, "text", W_HARD_NEGATIVE))
        for kw, needle in index.hard_negative_keywords.items():
            if needle in hay:
                neg.append(_sig("out_of_perimeter_topic", kw, "text", W_HARD_NEGATIVE))
        if neg:
            # One penalty, however many markers fired — the point is "this is elsewhere",
            # not a pile-on that buries a weak-but-real signal.
            signals.append(neg[0])

    # ── Unscoreable ────────────────────────────────────────────────────────
    if not hay and not signals:
        return UNSCOREABLE_SCORE, [
            _sig("unscoreable", "no readable text", "extractor", 0),
        ]

    total = sum(s["weight"] for s in signals)
    return max(SCORE_MIN, min(SCORE_MAX, total)), signals


def score_summary(signals: list[dict], limit: int = 4) -> str:
    """Compact one-line rendering for the digest: '[form 4797] [§1231] [keyword: section 179]'."""
    parts = []
    for s in signals[:limit]:
        kind, value = s.get("kind"), s.get("value")
        if kind == "irc":
            parts.append(f"[§{value}]")
        elif kind == "cfr":
            parts.append(f"[26 CFR {value}]")
        elif kind in {"out_of_perimeter_form", "out_of_perimeter_topic"}:
            parts.append(f"[NOT-US: {value}]")
        elif kind == "unscoreable":
            parts.append("[UNSCOREABLE]")
        else:
            parts.append(f"[{kind} {value}]")
    if len(signals) > limit:
        parts.append(f"(+{len(signals) - limit})")
    return " ".join(parts)
