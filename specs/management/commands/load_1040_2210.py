"""Load the FORM_2210 spec — Underpayment of Estimated Tax (§6654), FULL build.

Phase 2, sixth common form. Ken's 2 scope decisions (2026-06-15): FULL (Part I +
Regular quarterly method + Schedule AI annualized); prior-year inputs as preparer
facts. The §6654 penalty → 1040 line 38.

Part I — required annual payment = min(90% current tax, 100%/110% prior tax); no
penalty if (current tax − withholding) < $1,000. Regular Method — per-period
required installment (l9/4 or the Schedule AI amount) vs payments; every payment
(a dated estimate, or a legacy quarter bucket dated on its due date) applies to
the EARLIEST underpaid installment, and each underpaid amount accrues from its
installment due date to the date it is cured, capped at 4/15/2026, at the §6621
rate (flat 7% through 4/15/2026 — i2210 2025 Penalty Worksheet, all four rate
periods × 0.07; RATE AMENDMENT 2026-07-26). Schedule AI — annualized
installments (factors 4/2.4/1.5/1, applicable % 22.5/45/67.5/90, smaller-of the
regular installment).

LAW VERIFIED 2026-06-15 (brief tts-tax-app server/specs/_2210_source_brief.md):
  $1,000 de-minimis; 90% / 100% / 110% (110% when prior AGI > $150,000 [$75,000
  MFS]); four periods due 4/15, 6/15, 9/15/2025, 1/15/2026. RATE RE-VERIFIED
  2026-07-26 (QA Batch-001 item 10): the 2025 i2210 Penalty Worksheet applies
  × 0.07 in ALL FOUR rate periods (Rate Period 4 = 1/1/2026-4/15/2026, one 7%
  period; Table 2 days 365/304/212/90) — the original "6% Q2 2026" figure was
  an assumption made before the worksheet published, and understated penalties.

DATED AMENDMENT 2026-07-01 (Ken scope option 1 — build as designed,
tts-tax-app server/specs/2210_dated_penalty_design.md): the penalty formula now
accrues each underpayment to the DATE CURED (earliest-first application per the
i2210 Penalty Worksheet — "the number of days it remains unpaid (from the
installment due date to the date paid, or April 15, 2026)", excerpt
IRS_2025_F2210_INSTR already on this form) instead of always charging the fixed
due-date→4/15/2026 day count. With payments on the due dates the unified
algorithm reproduces the prior numbers exactly (P-T1..T6 unchanged); dated
payments add the effect (P-T7/P-T8). Withholding stays ¼-spread ON the due dates
(§6654(g) default; the actual-date withholding election remains deferred).

FACE RENUMBER + RECONCILIATION AMENDMENT 2026-07-27 (QA Batch-001 item 10, second
half — Ken scoped "panel + Part III grid" in-session):

  (1) PART III LINE NUMBERS WERE FROM A SUPERSEDED FORM. This spec carried
      line "18" = "required installment per period" and line "25" =
      "underpayment per period". On the 2025 Form 2210 face those are wrong:
      Part III Section A runs lines 10-18 — line 10 IS the required
      installment, line 17 IS the underpayment, and line 18 is the
      OVERPAYMENT. There is no line 25 in Part III at all (25 is a Schedule
      AI line). The 18/25 numbering belongs to the pre-renumber Form 2210,
      whose Part IV Section A ran 18-25. Transcribed 2026-07-27 from
      resources/irs_forms/2025/f2210.pdf and cross-checked against that
      PDF's own AcroForm widget grid (page 2 carries exactly nine 4-column
      rows + the single line-19 box, and the already-correct line-19 mapping
      anchors the sequence). Line "25" is RETIRED here, not left orphaned —
      a superseded line out-authored under a new number would leave both in
      the exported spec (the s122 ID-G lesson).

  (2) The full Part III Section A column mechanics are now specced (lines
      10-18, four columns) so a FILED 2210 is complete, and so the app's
      reconciliation panel and the printed face read the same numbers.

  (3) DOCUMENTED SOURCE OVERRIDE (R-2210-SRC). A preparer may record a
      controlling source figure (e.g. the prior software's penalty) WITHOUT
      destroying the computed one. Per MeF business rule F2210-006-01 the
      2210's TotalPenaltyAmt must EQUAL the return's EsPenaltyAmt, so the
      override drives line 19 and 1040 line 38 together — it never splits
      them. D_2210_TIE catches the older workaround (overriding 1040 line 38
      directly), which does split them.

  NOTE on filing: a transmitted 2210 must carry a Part II box A-E
  (F2210-002-02) — boxes A/B/D/E are NOT modeled, which is why this app
  transmits no IRS2210 today. That is a modeling limitation, not a rule that
  the form is never filed; the face itself says "You must file Form 2210"
  whenever a Part II box applies.

v1 NOTE (requires_human_review): Schedule AI takes the per-period annualized TAX as
a preparer input (t2210_ai_tax_q*) — the full per-period QDCGT/AMT bracket
computation is deferred. Withholding is spread evenly (no actual-date election —
Part II box D, unmodeled).

SAFETY GUARD: READY_TO_SEED stays False until Ken's review walk (the safe-harbor +
the regular-method penalty rate periods + Schedule AI + the §6621 rates).
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from sources.models import (
    AuthorityExcerpt,
    AuthorityFormLink,
    AuthoritySource,
    AuthoritySourceTopic,
    AuthorityTopic,
    RuleAuthorityLink,
)
from specs.models import (
    FlowAssertion,
    FormDiagnostic,
    FormFact,
    FormLine,
    FormRule,
    TaxForm,
    TestScenario,
)


READY_TO_SEED = True  # FLIPPED 2026-06-15 — Ken approved the review walk ("Approved — seed it, include render").
# 2026-07-01: the dated-accrual amendment rides the same approval — Ken chose scope
# option 1 ("build as designed") for the federal-payment-dates unit in-session.


FORM_JURISDICTION = "FED"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_ENTITY_TYPES = ["1040"]
FORM_STATUS = "draft"

# ── §6654 / §6621 constants (verified) ──
DE_MINIMIS = 1000
PCT_CURRENT = 0.90                 # 90% of current-year tax
HIGH_INCOME_AGI = 150000           # $75,000 if MFS
HIGH_INCOME_AGI_MFS = 75000
PCT_PRIOR_HIGH = 1.10              # 110% prior when high-income
PCT_PRIOR_NORMAL = 1.00
# §6621 underpayment rate for the 2025 penalty period (to 4/15/2026).
# VERIFIED 2026-07-26 against the OFFICIAL 2025 Instructions for Form 2210
# Penalty Worksheet (QA Batch-001 item 10): × 0.07 in ALL FOUR rate periods —
# Rate Period 4 is "January 1, 2026–April 15, 2026" as ONE 7% period (Table 2
# day counts 365/304/212/90 confirm). The prior 6% stub for 4/1-4/15/2026 was
# an unpublished-Q2-rate assumption and UNDERSTATED the penalty by 15 days ×
# 1% — the $1-3 TaxWise deltas the QA reports flagged. The two-rate machinery
# below is retained for years where the window does straddle a rate change.
RATE_7 = 0.07                      # all rate periods through 4/15/2026
RATE_6 = 0.07                      # unused in TY2025 (R7_END = CAP_DATE)
DAYS_7 = [365, 304, 212, 90]       # days at 7% from each due date to 4/15/2026
DAYS_6 = [0, 0, 0, 0]              # no second-rate stub in TY2025 (i2210)
# Schedule AI:
AI_FACTOR = [4.0, 2.4, 1.5, 1.0]
AI_PCT = [0.225, 0.45, 0.675, 0.90]


from datetime import date  # noqa: E402
from decimal import ROUND_HALF_UP, Decimal  # noqa: E402

# Dated accrual (2026-07-01 amendment): the four installment due dates, the
# 7%→6% rate boundary, and the accrual cap. DAYS_7/DAYS_6 above are the
# derived due-date→cap day counts (days_at_rates(due, CAP) reproduces them —
# the integrity gate pins that equivalence).
DUE_DATES = [date(2025, 4, 15), date(2025, 6, 15), date(2025, 9, 15), date(2026, 1, 15)]
R7_END = date(2026, 4, 15)         # last calendar day at 7% = the cap (i2210 2025)
CAP_DATE = date(2026, 4, 15)       # accrual stops here (i2210: "or April 15, 2026")


def _D(x):
    return Decimal(str(x if x is not None else 0))


def _r0(x):
    return int(_D(x).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def penalty_factor(i) -> Decimal:
    """The composite §6621 factor for period i (underpayment outstanding to 4/15/2026)."""
    return (Decimal(DAYS_7[i]) / Decimal("365") * _D(RATE_7)
            + Decimal(DAYS_6[i]) / Decimal("365") * _D(RATE_6))


# ── Pure functions (mirror the RS loader; the integrity gate re-types) ──


def required_annual_payment(current_tax, other_taxes, refundable_credits, withholding,
                            prior_year_tax, prior_year_agi, filing_status, prior_full_year=True) -> dict:
    """Part I. Returns l4/l5/l7/l8/l9 + whether a penalty can apply."""
    l4 = _D(current_tax) + _D(other_taxes) - _D(refundable_credits)
    l5 = _D(_r0(l4 * _D(PCT_CURRENT)))
    l7 = l4 - _D(withholding)
    fs = (filing_status or "single").lower()
    agi_thr = HIGH_INCOME_AGI_MFS if fs == "mfs" else HIGH_INCOME_AGI
    pct = PCT_PRIOR_HIGH if _D(prior_year_agi) > agi_thr else PCT_PRIOR_NORMAL
    # No prior-year safe harbor if the prior year wasn't a full 12-month year with tax.
    l8 = _D(_r0(_D(prior_year_tax) * _D(pct))) if (prior_full_year and _D(prior_year_tax) > 0) else None
    l9 = l5 if l8 is None else min(l5, l8)
    return {"l4": l4, "l5": l5, "l7": l7, "l8": (l8 if l8 is not None else _D(0)),
            "l9": l9, "penalty_possible": l7 >= DE_MINIMIS}


def regular_installments(l9) -> list[Decimal]:
    """The 25% method — four equal required installments."""
    q = _D(l9) / Decimal("4")
    return [q, q, q, q]


def ai_installments(ai_tax, reg_installments) -> list[Decimal]:
    """Schedule AI — annualized installment per period = annualized_tax × applicable% −
    prior required installments; line 27 = the smaller of that or the regular installment."""
    out = []
    prior = Decimal("0")
    for i in range(4):
        annualized = max(Decimal("0"), _D(ai_tax[i]) * _D(AI_PCT[i]) - prior)
        req = min(annualized, _D(reg_installments[i]))
        out.append(req)
        prior += req
    return out


def _as_date(d) -> date:
    """Scenario JSON carries ISO strings; the pure functions accept both."""
    if isinstance(d, date):
        return d
    return date.fromisoformat(str(d))


def days_at_rates(due: date, end: date) -> tuple[int, int]:
    """Chargeable days for an underpayment due `due` and cured `end` (already
    capped at CAP_DATE by the caller): (days at 7%, days at 6%). Simple date
    subtraction — the convention that makes days_at_rates(due, CAP_DATE)
    reproduce DAYS_7[i]/DAYS_6[i] exactly."""
    if end <= due:
        return 0, 0
    d7 = max(0, (min(end, R7_END) - due).days)
    d6 = max(0, (min(end, CAP_DATE) - max(due, R7_END)).days)
    return d7, d6


def _chunk_penalty(due: date, cure: date, amount: Decimal) -> Decimal:
    d7, d6 = days_at_rates(due, min(cure, CAP_DATE))
    return amount * (Decimal(d7) / Decimal("365") * _D(RATE_7)
                     + Decimal(d6) / Decimal("365") * _D(RATE_6))


def regular_penalty(installments, withholding, est_payments, payments_dated=None) -> dict:
    """The §6621 penalty, unified dated algorithm (i2210 Penalty Worksheet):
    withholding is treated as paid ¼ ON each due date (§6654(g) default);
    every payment — a dated (date, amount) pair, or a legacy quarter bucket
    dated on its due date — applies to the EARLIEST still-underpaid
    installment; each underpaid amount accrues from its installment due date
    to the date it is cured, capped at 4/15/2026 (flat 7% through 4/15/2026 —
    i2210 2025). A payment on or before the due date cures with zero
    chargeable days. With payments exactly on the due dates this reproduces
    the prior fixed-day formula (P-T1..T6 pin that equivalence).

    Returns the FACE per-column underpayments (Part III Section A: payments
    netted per column by date window — (a) ≤4/15, (b) 4/16–6/15, (c)
    6/16–9/15, (d) 9/16–1/15 — with an overpayment carry-forward; identical
    to the pre-amendment quarterly model when payments sit on the due dates)
    + the total penalty (the Penalty Worksheet's earliest-first, date-cured
    allocation — the two are the form's own split)."""
    if payments_dated:
        payments = [(_as_date(d), _D(a)) for d, a in payments_dated]
    else:
        payments = [(DUE_DATES[i], _D(est_payments[i])) for i in range(4)]
    wh_q = _D(withholding) / Decimal("4")

    # FACE: per-column window netting + overpayment carry-forward.
    window_paid = [Decimal("0")] * 4
    for paid_on, amount in payments:
        for i in range(4):
            if paid_on <= DUE_DATES[i]:
                window_paid[i] += _D(amount)
                break  # a payment after 1/15 belongs to no column
    underpayments, overpay = [], Decimal("0")
    for i in range(4):
        avail = wh_q + window_paid[i] + overpay
        req = _D(installments[i])
        if avail >= req:
            underpayments.append(Decimal("0"))
            overpay = avail - req
        else:
            underpayments.append(req - avail)
            overpay = Decimal("0")

    # PENALTY: earliest-first, date-cured accrual.
    events = sorted(
        [(DUE_DATES[i], wh_q) for i in range(4) if wh_q > 0] + payments,
        key=lambda e: e[0],
    )
    remaining = [_D(x) for x in installments]
    penalty = Decimal("0")
    for paid_on, amount in events:
        amount = _D(amount)
        for i in range(4):
            if amount <= 0:
                break
            if remaining[i] <= 0:
                continue
            applied = min(amount, remaining[i])
            remaining[i] -= applied
            amount -= applied
            penalty += _chunk_penalty(DUE_DATES[i], paid_on, applied)
    for i in range(4):
        if remaining[i] > 0:
            penalty += _chunk_penalty(DUE_DATES[i], CAP_DATE, remaining[i])
    return {"underpayments": underpayments, "penalty": _D(_r0(penalty))}


def column_payments(withholding, est_payments, payments_dated=None) -> list[Decimal]:
    """Line 11 per column — withholding spread ¼ on each due date (§6654(g)
    default) plus the payments falling in each column's date window:
    (a) on or before 4/15, (b) 4/16-6/15, (c) 6/16-9/15, (d) 9/16-1/15.
    A payment after 1/15/2026 belongs to no column."""
    if payments_dated:
        pays = [(_as_date(d), _D(a)) for d, a in payments_dated]
    else:
        pays = [(DUE_DATES[i], _D(est_payments[i])) for i in range(4)]
    wh_q = _D(withholding) / Decimal("4")
    out = [wh_q for _ in range(4)]
    for paid_on, amount in pays:
        for i in range(4):
            if paid_on <= DUE_DATES[i]:
                out[i] += _D(amount)
                break
    return out


def face_columns(installments, withholding, est_payments, payments_dated=None) -> list[dict]:
    """Part III Section A, lines 10-18, transcribed from the 2025 face
    (2026-07-27). Returns one dict per column (a)-(d).

    The mechanic that matters: line 14 carries the PREVIOUS column's unpaid
    amount (line 16 + line 17), and line 15 subtracts it from this column's
    available payments BEFORE they count toward this column's own installment.
    So a late catch-up payment cures the earlier shortfall first and leaves the
    current period underpaid — the same earliest-first principle the Section B
    penalty worksheet uses.

    This REPLACES the earlier overpayment-carry-only allocation, which agreed
    with the face whenever payments sat on the due dates but credited a late
    catch-up to the wrong column. Section A drives the printed face and the
    reconciliation display only; the PENALTY is unaffected (it comes from the
    Section B worksheet in regular_penalty)."""
    paid = column_payments(withholding, est_payments, payments_dated)
    cols: list[dict] = []
    l16_prev = l17_prev = l18_prev = Decimal("0")
    for i in range(4):
        l10 = _D(installments[i])
        l11 = paid[i]
        l12 = l18_prev
        l13 = l11 + l12
        l14 = l16_prev + l17_prev
        # "For column (a) only, enter the amount from line 11."
        l15 = l11 if i == 0 else max(Decimal("0"), l13 - l14)
        l16 = (l14 - l13) if l15 == 0 else Decimal("0")
        l17 = (l10 - l15) if l10 >= l15 else Decimal("0")
        l18 = (l15 - l10) if l15 > l10 else Decimal("0")
        cols.append({"10": l10, "11": l11, "12": l12, "13": l13, "14": l14,
                     "15": l15, "16": l16, "17": l17, "18": l18})
        l16_prev, l17_prev, l18_prev = l16, l17, l18
    return cols


def compute_2210(current_tax=0, other_taxes=0, refundable_credits=0, withholding=0,
                 prior_year_tax=0, prior_year_agi=0, filing_status="single", prior_full_year=True,
                 est_payments=(0, 0, 0, 0), use_annualized=False, ai_tax=(0, 0, 0, 0),
                 payments_dated=None) -> dict:
    """The full §6654 chain. Returns l9 (required annual payment) + the penalty → 1040 line 38.
    `payments_dated` — [(date|ISO string, amount), ...] — REPLACES the quarter
    buckets when present (the tts FederalEstimatedPayment rows)."""
    p1 = required_annual_payment(current_tax, other_taxes, refundable_credits, withholding,
                                 prior_year_tax, prior_year_agi, filing_status, prior_full_year)
    if not p1["penalty_possible"]:
        return {"l8": p1["l8"], "l9": p1["l9"], "penalty": Decimal("0"), "no_penalty": True,
                "columns": []}
    reg = regular_installments(p1["l9"])
    installments = ai_installments(ai_tax, reg) if use_annualized else reg
    pen = regular_penalty(installments, withholding, est_payments, payments_dated)
    cols = face_columns(installments, withholding, est_payments, payments_dated)
    return {"l8": p1["l8"], "l9": p1["l9"], "penalty": pen["penalty"],
            "underpayments": [c["17"] for c in cols], "columns": cols,
            "no_penalty": pen["penalty"] <= 0}


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY
# ═══════════════════════════════════════════════════════════════════════════

AUTHORITY_TOPICS: list[tuple[str, str]] = [
    ("estimated_tax_penalty", "Underpayment of estimated tax (§6654) — the required annual payment safe harbors + the §6621 penalty; Form 2210 → 1040 line 38"),
]

EXISTING_SOURCES_TO_REFERENCE: list[str] = [
    "IRS_2025_1040_FORM",
    "IRS_2025_1040_INSTR",
    "IRC_6654",  # ownership -> load_1040_spine.py (A3/D-42, 2026-08-25)
]

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "IRS_2025_F2210_INSTR",
        "source_type": "official_instructions",
        "source_rank": "primary_official",
        "jurisdiction_code": "FED",
        "entity_type_code": "1040",
        "tax_year_start": 2025,
        "tax_year_end": 2025,
        "title": "2025 Instructions for Form 2210 — Underpayment of Estimated Tax",
        "citation": "Instructions for Form 2210 (2025), Parts I-IV + Schedule AI",
        "issuer": "IRS",
        "official_url": "https://www.irs.gov/instructions/i2210",
        "current_status": "active",
        "is_substantive_authority": False,
        "is_filing_authority": True,
        "trust_score": 9.50,
        "requires_human_review": True,
        "notes": "Part I safe harbors ($1,000 / 90% / 100% / 110% over $150k AGI), the Regular Method penalty (§6621 flat 7% through 4/15/2026 per the 2025 Penalty Worksheet — corrected 2026-07-26), and Schedule AI (factors 4/2.4/1.5/1, % 22.5/45/67.5/90). REQUIRES HUMAN REVIEW: Schedule AI takes the per-period annualized TAX as a preparer input (the full per-period bracket/QDCGT computation is deferred); withholding spread evenly; Part II waiver + farmers/fishermen out of v1.",
        "topics": ["estimated_tax_penalty"],
        "excerpts": [
            {
                "excerpt_label": "Part I — the required annual payment + the $1,000 de-minimis",
                "location_reference": "i2210 (2025), Part I lines 4-9",
                "excerpt_text": (
                    "Line 4 is your current-year tax. Line 5 is 90% of line 4. Line 6 is your withholding. If "
                    "line 4 minus line 6 (line 7) is less than $1,000, you don't owe a penalty. Line 8 is your "
                    "prior-year tax, multiplied by 110% if your prior-year AGI was more than $150,000 ($75,000 "
                    "if married filing separately). Line 9, the required annual payment, is the smaller of line "
                    "5 or line 8."
                ),
                "summary_text": "Required annual payment = min(90% current, 100%/110% prior); no penalty if current tax − withholding < $1,000.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "The Regular Method penalty + the §6621 rate",
                "location_reference": "i2210 (2025), Part III + the Penalty Worksheet (pp. 5-6) + Table 2",
                "excerpt_text": (
                    "Penalty Worksheet rate periods and factors (each line: Underpayment on line 1a × Number "
                    "of days ÷ 365 × 0.07): Rate Period 1: April 16, 2025–June 30, 2025 (× 0.07); Rate Period "
                    "2: July 1, 2025–September 30, 2025 (× 0.07); Rate Period 3: October 1, 2025–December 31, "
                    "2025 (× 0.07); Rate Period 4: January 1, 2026–April 15, 2026 (× 0.07). Table 2 (Chart of "
                    "Total Days): column (a) 04/15/25: 76/92/92/105 = 365; (b) 06/15/25: 15/92/92/105 = 304; "
                    "(c) 09/15/25: 15/92/105 = 212; (d) 01/15/26: 90."
                ),
                "summary_text": "Penalty = underpayment × days/365 × 0.07 — a FLAT 7% across all four rate periods through 4/15/2026 (the prior '6% for 4/1-4/15/2026' excerpt was a pre-publication assumption, corrected 2026-07-26).",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Schedule AI — the annualized income method",
                "location_reference": "i2210 (2025), Schedule AI",
                "excerpt_text": (
                    "Annualize your income for each period by multiplying by 4 (Jan 1-Mar 31), 2.4 (Jan 1-May "
                    "31), 1.5 (Jan 1-Aug 31), and 1 (Jan 1-Dec 31). Figure the tax on each annualized amount and "
                    "multiply by the applicable percentage: 22.5%, 45%, 67.5%, and 90%. The required "
                    "installment is the smaller of this annualized installment or the regular method installment."
                ),
                "summary_text": "AI installment = annualized tax × (22.5/45/67.5/90)% − prior installments; the required installment is the smaller of the AI or regular amount.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        # ADDED 2026-07-27. The filing/transmission authority for the 2210 —
        # read from the IRS business-rule file the app already holds
        # (delvio-tax docs/mef/schemas/2025v5.3/1040_Business_Rules_2025v5.3.csv),
        # NOT from recollection. F2210-006-01 is what makes the documented
        # source override drive line 19 and 1040 line 38 together.
        "source_code": "IRS_2025_1040_MEF_BR",
        "source_type": "mef_business_rule",
        "source_rank": "primary_official",
        "jurisdiction_code": "FED",
        "entity_type_code": "1040",
        "tax_year_start": 2025,
        "tax_year_end": 2025,
        "title": "MeF Business Rules for Form 1040 — TY2025v5.3 (Form 2210 rules)",
        "citation": "IRS Modernized e-File Business Rules, 1040 Business Rules 2025v5.3, rules F2210-002-02 / F2210-003 / F2210-004 / F2210-006-01",
        "issuer": "IRS",
        "official_url": "https://www.irs.gov/e-file-providers/modernized-e-file-mef-schemas-and-business-rules",
        "current_status": "active",
        "is_substantive_authority": False,
        "is_filing_authority": True,
        "trust_score": 10.00,
        "requires_human_review": False,
        "notes": (
            "Transmission-side rules, all Active/Reject in TY2025v5.3. F2210-002-02 is why a "
            "2210 can only be TRANSMITTED with a Part II box A-E checked — and, read the other "
            "way, why the form IS filed whenever one applies. This app models only box C and "
            "refuses at extract (Schedule AI is not computed), so no IRS2210 is transmitted "
            "today; boxes A/B/D/E are unmodeled. Box D (withholding credited on the dates "
            "actually withheld) is a penalty-REDUCING election the app does not offer — the "
            "compute uses the §6654(g) even-spread default."
        ),
        "topics": ["estimated_tax_penalty"],
        "excerpts": [
            {
                "excerpt_label": "F2210-006-01 — the 2210 penalty must equal the return's penalty",
                "location_reference": "1040 Business Rules 2025v5.3, rule F2210-006-01 (Data Mismatch, Reject, Active)",
                "excerpt_text": (
                    "Form 2210, 'TotalPenaltyAmt' must be equal to 'EsPenaltyAmt' in the return."
                ),
                "summary_text": (
                    "The 2210's own penalty (line 19) must tie to the 1040's estimated-tax "
                    "penalty (line 38). A documented source override must therefore move BOTH; "
                    "overriding line 38 alone splits them (D_2210_TIE)."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "F2210-002-02 — a transmitted 2210 needs a Part II box",
                "location_reference": "1040 Business Rules 2025v5.3, rule F2210-002-02 (Incorrect Data, Reject, Active)",
                "excerpt_text": (
                    "On Form 2210, Part II, one of more of the following checkboxes must be "
                    "checked: (Line A 'WaiverOfEntirePenaltyInd' or Line B "
                    "'WaiverOfPartOfPenaltyInd' or Line C 'AnnualizedIncomeMethodInd' or Line D "
                    "'ActuallyWithheldInd' or Line E 'JointReturnInd')."
                ),
                "summary_text": (
                    "Quoted verbatim including the IRS source's own 'one of more' typo. A 2210 "
                    "carrying no Part II box rejects; the form IS transmitted when a box applies. "
                    "Related: F2210-003 / F2210-004 require a [WaiverExplanationStatement] "
                    "attached whenever box A or box B is checked."
                ),
                "is_key_excerpt": True,
            },
        ],
    },
]

NEW_EXCERPTS_ON_EXISTING: list[tuple[str, dict]] = [    # Re-homed 2026-08-25 (campaign A3/D-42): IRC_6654 is DECLARED by load_1040_spine.py.
    # This spec still contributes these excerpts; it no longer rewrites the row.
    ("IRC_6654", {
                    "excerpt_label": "§6654(d) the required annual payment",
                    "location_reference": "26 U.S.C. §6654(d)(1)",
                    "excerpt_text": (
                        "The required annual payment is the lesser of 90 percent of the tax shown on the return for "
                        "the taxable year, or 100 percent of the tax shown on the return for the preceding taxable "
                        "year (110 percent if the adjusted gross income exceeded $150,000)."
                    ),
                    "summary_text": "Required annual payment = lesser of 90% current or 100%/110% prior.",
                    "is_key_excerpt": True,
                }),
]

AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    ("IRS_2025_F2210_INSTR", "FORM_2210", "governs"),
    ("IRC_6654", "FORM_2210", "governs"),
    ("IRS_2025_1040_MEF_BR", "FORM_2210", "governs"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM: FORM_2210
# ═══════════════════════════════════════════════════════════════════════════

P_IDENTITY = {
    "form_number": "FORM_2210",
    "form_title": "Form 2210 Underpayment of Estimated Tax (§6654) (TY2025)",
    "notes": (
        "Ken's 2 scope decisions 2026-06-15 (FULL build). A return-level FormDefinition "
        "on the 1040 (no sub-model). Part I: required annual payment = min(90% current "
        "tax, 100%/110% prior) — no penalty if current tax − withholding < $1,000. "
        "Regular Method: per-period required installment (line 9 / 4 or the Schedule AI "
        "amount) vs payments (withholding spread 1/4 + the estimated payments); the "
        "penalty on each underpayment accrues to 4/15/2026 at the §6621 rate (FLAT 7% "
        "through 4/15/2026 — i2210 2025 Penalty Worksheet; rate corrected 2026-07-26) "
        "→ 1040 line 38. Schedule AI: annualized "
        "installments (factors 4/2.4/1.5/1, % 22.5/45/67.5/90, smaller-of the regular). "
        "v1: Schedule AI takes the per-period annualized TAX as a preparer input "
        "(requires_human_review); withholding spread evenly; Part II waiver deferred."
    ),
}

P_FACTS: list[dict] = [
    # ── Part I preparer inputs ──
    {"fact_key": "t2210_prior_year_tax", "label": "Prior-year (2024) total tax",
     "data_type": "decimal", "default_value": "0", "sort_order": 1, "notes": "Line 8 — the 100%/110% safe harbor."},
    {"fact_key": "t2210_prior_year_agi", "label": "Prior-year (2024) AGI",
     "data_type": "decimal", "default_value": "0", "sort_order": 2, "notes": "> $150k ($75k MFS) → 110%."},
    {"fact_key": "t2210_prior_full_year", "label": "Prior year was a full 12-month year with a tax liability?",
     "data_type": "boolean", "default_value": "true", "sort_order": 3, "notes": "No → the 100% safe harbor is unavailable."},
    # ── Schedule AI ──
    {"fact_key": "t2210_use_annualized", "label": "Use the annualized income method (Schedule AI)?",
     "data_type": "boolean", "default_value": "false", "sort_order": 4, "notes": "Uneven income."},
    {"fact_key": "t2210_payments_dated", "label": "Dated federal estimated payments entered?",
     "data_type": "boolean", "default_value": "false", "sort_order": 9,
     "notes": ("Marker: dated (amount, date_paid) payment rows exist (tts FederalEstimatedPayment). When "
               "present they REPLACE the flat quarter buckets; each payment applies earliest-first and "
               "stops that underpayment's accrual on its date (R-2210-REG). §6654-creditable kinds only: "
               "estimate + prior_year_applied (the 1040 line-26 set; an overpayment applied is treated as "
               "paid 4/15 — the i2210 convention; extension/other rows are recorded, never credited). A "
               "dated total that differs from the flat line-26 buckets fires D_2210_DATED.")},
    {"fact_key": "t2210_ai_tax_q1", "label": "Schedule AI — annualized tax, period 1 (Jan-Mar)",
     "data_type": "decimal", "default_value": "0", "sort_order": 5, "notes": "Preparer-computed (v1)."},
    {"fact_key": "t2210_ai_tax_q2", "label": "Schedule AI — annualized tax, period 2 (Jan-May)",
     "data_type": "decimal", "default_value": "0", "sort_order": 6, "notes": "Preparer-computed (v1)."},
    {"fact_key": "t2210_ai_tax_q3", "label": "Schedule AI — annualized tax, period 3 (Jan-Aug)",
     "data_type": "decimal", "default_value": "0", "sort_order": 7, "notes": "Preparer-computed (v1)."},
    {"fact_key": "t2210_ai_tax_q4", "label": "Schedule AI — annualized tax, period 4 (Jan-Dec)",
     "data_type": "decimal", "default_value": "0", "sort_order": 8, "notes": "Preparer-computed (v1)."},
    # ── Documented source override (ADDED 2026-07-27, R-2210-SRC) ──
    {"fact_key": "t2210_penalty_source_amount", "label": "Documented source penalty (controlling amount)",
     "data_type": "decimal", "sort_order": 10,
     "notes": ("Preparer input. A penalty figure from a controlling outside source (e.g. the prior "
               "software, or an IRS notice) that the preparer is using INSTEAD of the computed "
               "amount. It does NOT erase the computed penalty — both are retained and shown side "
               "by side. Per F2210-006-01 it drives BOTH 2210 line 19 and 1040 line 38, so the "
               "return stays internally consistent. Blank = use the computed penalty.")},
    {"fact_key": "t2210_penalty_source_label", "label": "Source of the documented penalty",
     "data_type": "text", "sort_order": 11,
     "notes": "Preparer input. Where the controlling figure came from — required when an amount is entered."},
    {"fact_key": "t2210_penalty_source_note", "label": "Why the source amount controls",
     "data_type": "text", "sort_order": 12,
     "notes": ("Preparer input. The reason the computed figure was not used. This is the audit "
               "record a reviewer reads a year later — required when an amount is entered.")},
    # ── Outputs ──
    {"fact_key": "t2210_line8", "label": "Prior-year safe harbor (line 8)",
     "data_type": "decimal", "sort_order": 29,
     "notes": ("OUTPUT. prior_tax × 100% or 110%. ADDED 2026-07-27: line 8 is one of the two "
               "candidates line 9 takes the smaller of, and it was neither stored nor printed — "
               "the printed face showed line 9 as 'the smaller of line 5 or line 8' with line 8 "
               "BLANK. Zero means the prior-year harbor is unavailable (no prior tax, or the "
               "prior year was not a full 12-month year), not that it computed to zero.")},
    {"fact_key": "t2210_line9", "label": "Required annual payment (line 9)",
     "data_type": "decimal", "sort_order": 30, "notes": "OUTPUT. min(90% current, 100/110% prior)."},
    {"fact_key": "t2210_penalty", "label": "Estimated tax penalty → 1040 line 38",
     "data_type": "decimal", "sort_order": 31, "notes": "OUTPUT. §6621 on the underpayments."},
]

P_RULES: list[dict] = [
    {"rule_id": "R-2210-RAP", "title": "Part I — required annual payment + the $1,000 de-minimis", "rule_type": "calculation",
     "precedence": 1, "sort_order": 1,
     "formula": ("l4 = current_tax + other_taxes − refundable_credits; l5 = round(0.90 × l4); l7 = l4 − "
                 "withholding; if l7 < $1,000 → no penalty. l8 = round(prior_tax × (1.10 if prior_AGI > "
                 "$150k [$75k MFS] else 1.00)) [only if prior was a full year]; l9 = min(l5, l8)."),
     "inputs": ["t2210_prior_year_tax", "t2210_prior_year_agi", "t2210_prior_full_year"],
     "outputs": ["t2210_line9"],
     "description": "§6654(d). The safe harbors."},
    {"rule_id": "R-2210-REG", "title": "Regular Method — dated underpayment accrual + §6621 penalty", "rule_type": "calculation",
     "precedence": 2, "sort_order": 2,
     "formula": ("required installment = l9/4 (or the Schedule AI amount); withholding is treated as paid "
                 "1/4 ON each due date (§6654(g) default); every payment — a dated estimate, or a legacy "
                 "quarter bucket dated on its due date — applies to the EARLIEST still-underpaid "
                 "installment; each underpaid amount accrues from its installment due date to the date it "
                 "is cured, capped at 4/15/2026: penalty += amount × days/365 × 7% — the 2025 i2210 "
                 "Penalty Worksheet applies × 0.07 in ALL FOUR rate periods (Rate Period 4 = 1/1/2026-"
                 "4/15/2026, one 7% period; corrected 2026-07-26 from the pre-publication 6% Q2 stub); "
                 "→ 1040 line 38. Due dates 4/15/2025, 6/15/2025, 9/15/2025, 1/15/2026. With payments "
                 "on the due dates this equals the fixed-day formula (DAYS = [365,304,212,90])."),
     "inputs": ["t2210_use_annualized", "t2210_payments_dated"], "outputs": ["t2210_penalty"],
     "description": ("The §6621 penalty accrues per day from the installment due date to the date paid "
                     "(i2210 Penalty Worksheet, earliest-first; flat 7% through 4/15/2026).")},
    {"rule_id": "R-2210-AI", "title": "Schedule AI — annualized installments", "rule_type": "calculation",
     "precedence": 3, "sort_order": 3,
     "formula": ("annualized installment[i] = max(0, ai_tax[i] × AI_PCT[i] − Σ prior); AI_PCT = "
                 "[22.5,45,67.5,90]%; the required installment = min(annualized, the regular l9/4). The "
                 "annualized tax per period is a preparer input in v1."),
     "inputs": ["t2210_ai_tax_q1", "t2210_ai_tax_q2", "t2210_ai_tax_q3", "t2210_ai_tax_q4"], "outputs": [],
     "description": "Schedule AI factors 4/2.4/1.5/1; applicable % 22.5/45/67.5/90."},
    # ADDED 2026-07-27 — QA Batch-001 item 10.
    {"rule_id": "R-2210-FACE", "title": "Part III Section A — the four-column underpayment worksheet", "rule_type": "calculation",
     "precedence": 4, "sort_order": 4,
     "formula": ("Per column i in (a) 4/15/25, (b) 6/15/25, (c) 9/15/25, (d) 1/15/26: "
                 "l10 = 25% of line 9 (or Schedule AI line 27 when box C applies); "
                 "l11 = withholding/4 (§6654(g) even spread) + estimated payments made in that "
                 "column's date window ((a) on or before 4/15; (b) 4/16-6/15; (c) 6/16-9/15; "
                 "(d) 9/16-1/15; a payment after 1/15 belongs to no column); "
                 "l12 = l18 of the previous column; l13 = l11 + l12; "
                 "l14 = l16 + l17 of the previous column; "
                 "l15 = max(0, l13 − l14) — for column (a), l15 = l11; "
                 "l16 = (l14 − l13) if l15 == 0 else 0; "
                 "l17 (UNDERPAYMENT) = l10 − l15 when l10 ≥ l15, else 0; "
                 "l18 (OVERPAYMENT) = l15 − l10 when l15 > l10, else 0."),
     "inputs": ["t2210_line9", "t2210_use_annualized"], "outputs": [],
     "description": ("The face's own per-column allocation, which is SEPARATE from the Section B "
                     "penalty worksheet: Section A nets payments by column date window with an "
                     "overpayment carry-forward, while the penalty applies every payment to the "
                     "earliest still-underpaid installment (R-2210-REG). With payments sitting on "
                     "the due dates the two agree. Specced 2026-07-27 — previously the app stored "
                     "only the first installment and the SUM of the underpayments, so no "
                     "per-period figure was recoverable for review.")},
    {"rule_id": "R-2210-SRC", "title": "Documented source override — retain the computed penalty", "rule_type": "calculation",
     "precedence": 5, "sort_order": 5,
     "formula": ("If t2210_penalty_source_amount is entered: the RETURN uses it for BOTH Form 2210 "
                 "line 19 and Form 1040 line 38 (never one without the other — F2210-006-01 "
                 "requires TotalPenaltyAmt == EsPenaltyAmt), while the computed §6654 penalty and "
                 "the whole Part I / Part III derivation are RETAINED and displayed alongside it. "
                 "Blank ⇒ the computed penalty controls. The source label and the reason are "
                 "required whenever an amount is entered — an undocumented override is the thing "
                 "this rule exists to prevent."),
     "inputs": ["t2210_penalty_source_amount", "t2210_penalty_source_label", "t2210_penalty_source_note"],
     "outputs": ["t2210_penalty"],
     "description": ("§6654 does not authorize a preparer to substitute a figure — this rule is a "
                     "RECORD-KEEPING mechanism, not a tax-law position. It exists because "
                     "preparers reconciling against prior software were otherwise overriding 1040 "
                     "line 38 directly, which erased the computed penalty and split it from the "
                     "2210's own line 19.")},
]

# TRANSCRIBED 2026-07-27 from the 2025 Form 2210 face
# (resources/irs_forms/2025/f2210.pdf), cross-checked against that PDF's own
# AcroForm widget grid. Part I = lines 1-9; Part III Section A = lines 10-18
# in FOUR columns (a) 4/15/25 (b) 6/15/25 (c) 9/15/25 (d) 1/15/26; Section B =
# line 19. Per-column values carry an (a)-(d) suffix.
P_LINES: list[dict] = [
    # ── Part I — Required Annual Payment ──
    {"line_number": "1", "description": "Line 1 — 2025 tax after credits (1040 line 22)", "line_type": "calculated"},
    {"line_number": "2", "description": "Line 2 — other taxes (SE tax, Additional Medicare, NIIT)", "line_type": "calculated"},
    {"line_number": "3", "description": "Line 3 — other payments and refundable credits (shown in parentheses on the face)", "line_type": "calculated"},
    {"line_number": "4", "description": "Line 4 — current year tax (combine lines 1, 2, and 3)", "line_type": "calculated"},
    {"line_number": "5", "description": "Line 5 — 90% of line 4", "line_type": "calculated"},
    {"line_number": "6", "description": "Line 6 — withholding taxes", "line_type": "input"},
    {"line_number": "7", "description": "Line 7 — line 4 − line 6 (< $1,000 → no penalty)", "line_type": "calculated"},
    {"line_number": "8", "description": "Line 8 — maximum required annual payment based on prior year's tax (× 110% if high-income)", "line_type": "calculated"},
    {"line_number": "9", "description": "Line 9 — required annual payment (smaller of 5 or 8)", "line_type": "calculated"},
    # ── Part III Section A — Figure Your Underpayment (4 columns) ──
    # RENUMBERED 2026-07-27: the required installment is line 10 (was
    # mis-specced as "18") and the underpayment is line 17 (was "25").
    {"line_number": "10", "description": "Line 10 — required installments per column (25% of line 9, or Schedule AI line 27)", "line_type": "calculated"},
    {"line_number": "11", "description": "Line 11 — estimated tax paid and tax withheld, per column", "line_type": "calculated"},
    {"line_number": "12", "description": "Line 12 — amount from line 18 of the previous column (overpayment carried forward)", "line_type": "calculated"},
    {"line_number": "13", "description": "Line 13 — add lines 11 and 12", "line_type": "calculated"},
    {"line_number": "14", "description": "Line 14 — add the amounts on lines 16 and 17 of the previous column", "line_type": "calculated"},
    {"line_number": "15", "description": "Line 15 — line 13 − line 14 (zero or less → -0-; column (a) = line 11)", "line_type": "calculated"},
    {"line_number": "16", "description": "Line 16 — if line 15 is zero, line 14 − line 13; otherwise -0-", "line_type": "calculated"},
    {"line_number": "17", "description": "Line 17 — UNDERPAYMENT per column (line 10 − line 15 when line 10 ≥ line 15)", "line_type": "calculated"},
    {"line_number": "18", "description": "Line 18 — OVERPAYMENT per column (line 15 − line 10 when line 15 > line 10); carries to line 12 of the next column", "line_type": "calculated"},
    {"line_number": "ai27", "description": "Schedule AI line 27 — annualized required installment → Part III line 10", "line_type": "calculated"},
    # ── Part III Section B — the penalty ──
    {"line_number": "19", "description": "Line 19 — the penalty → 1040 line 38 (Worksheet for Part III Section B)", "line_type": "total"},
    {"line_number": "1040_38", "description": "Estimated tax penalty → Form 1040 line 38", "line_type": "total"},
]

# RETIRED 2026-07-27 — line numbers this spec previously authored that do NOT
# exist on the 2025 face. Deleted on load rather than left orphaned: an
# out-authored replacement leaves BOTH rows in the exported spec, which is how
# two contradictory versions survived undetected for six weeks in the ID-G
# scenarios (s122). "18" is NOT retired — it still exists, but it now means
# OVERPAYMENT, so its description is simply corrected above.
RETIRED_LINES: list[str] = ["25"]

P_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_2210_NO_PENALTY", "title": "No estimated tax penalty (safe harbor met)", "severity": "info",
     "condition": "line 7 < $1,000, or payments >= required annual payment",
     "message": ("No §6654 penalty applies — either the balance after withholding is under $1,000, or the "
                 "withholding plus timely estimated payments met the required annual payment (90% of this "
                 "year's tax, or 100%/110% of last year's)."),
     "notes": "§6654 the safe harbors."},
    {"diagnostic_id": "D_2210_PRIOR_YEAR", "title": "Prior-year tax not entered — safe harbor untested", "severity": "warning",
     "condition": "a penalty is computed but prior-year tax is blank",
     "message": ("A penalty is computed but the prior-year tax is blank, so the 100%/110% prior-year safe "
                 "harbor can't be tested — the 90%-of-current path may overstate the required payment. Enter "
                 "the 2024 total tax (and AGI) to use the prior-year safe harbor."),
     "notes": "No silent gap — the prior-year safe harbor is often the lower number."},
    {"diagnostic_id": "D_2210_110", "title": "High income — the 110% prior-year safe harbor applies", "severity": "info",
     "condition": "prior-year AGI > $150,000 ($75,000 MFS)",
     "message": ("Prior-year AGI exceeds $150,000 ($75,000 if married filing separately), so the prior-year "
                 "safe harbor is 110% of the 2024 tax (not 100%)."),
     "notes": "§6654(d)(1)(C)."},
    {"diagnostic_id": "D_2210_AI", "title": "Schedule AI used — verify the per-period tax", "severity": "info",
     "condition": "the annualized income method is used",
     "message": ("The annualized income method (Schedule AI) is used. In this version the per-period annualized "
                 "tax is entered by the preparer — verify each period's tax (including any QDCGT / AMT) before "
                 "relying on the installment amounts."),
     "notes": "v1 simplification (requires_human_review)."},
    {"diagnostic_id": "D_2210_DATED", "title": "Dated payments don't reconcile with 1040 line 26", "severity": "warning",
     "condition": ("dated FederalEstimatedPayment rows exist AND their §6654-creditable total (estimate + "
                   "prior_year_applied) != the flat est_payment_q1..q4 + PY-applied total that feeds 1040 "
                   "line 26"),
     "message": ("Dated federal estimated payments are entered, but their total (estimates + prior-year "
                 "overpayment applied) does not equal the flat quarterly amounts on 1040 line 26. The Form "
                 "2210 penalty uses the DATED payments; line 26 uses the flat amounts — reconcile them so "
                 "the return's payments and the penalty computation tell the same story."),
     "notes": ("No silent gap: line 26 stays on the flat quarter buckets (spine R-PAY-04, out of this "
               "unit's scope); the penalty uses the dated rows when present. A divergence is preparer "
               "error, not a computable choice.")},
    {"diagnostic_id": "D_2210_TY2026", "title": "TY2026 — re-verify the §6621 rates", "severity": "warning",
     "condition": "tax_year == 2026 AND a penalty is computed",
     "message": ("This 2026 return uses the 2025-period §6621 rate (flat 7% to 4/15/2026), which is INTERIM "
                 "for a 2026 penalty period — re-verify the quarterly underpayment rates from the 2026 Form "
                 "2210 Penalty Worksheet when it publishes (~Jan 2027)."),
     "notes": "Re-pin the 2026 rates from the published worksheet, never from an assumed rate ruling (the 2026-07-26 lesson)."},
    # ADDED 2026-07-27 — QA Batch-001 item 10.
    {"diagnostic_id": "D_2210_SRC", "title": "A documented source penalty is controlling", "severity": "warning",
     "condition": "t2210_penalty_source_amount is entered",
     "message": ("This return reports a documented source penalty instead of the computed §6654 "
                 "amount. The computed penalty and the full Part I / Part III derivation are "
                 "retained on the Form 2210 tab — compare them before filing, and make sure the "
                 "recorded source and reason still hold."),
     "notes": ("WARNING, not error: the override is a deliberate, documented preparer act. It is "
               "never silent, though — it appears on every diagnostics run so a reviewer cannot "
               "miss that the filed penalty is not the computed one. Severity is EFFECT-SCALED: "
               "fires only when the source amount actually DIFFERS from the computed penalty "
               "(recording a source figure that agrees with the computation is corroboration, "
               "not a divergence, and stays silent)."),
     },
    {"diagnostic_id": "D_2210_TIE", "title": "1040 line 38 was overridden away from the Form 2210 penalty", "severity": "warning",
     "condition": ("Form 1040 line 38 carries a direct preparer override AND it does not equal the "
                   "Form 2210 line 19 penalty (and no documented source override is recorded)"),
     "message": ("Form 1040 line 38 has been overridden by hand and no longer matches the Form 2210 "
                 "penalty on line 19. MeF business rule F2210-006-01 requires the 2210's penalty to "
                 "equal the return's estimated-tax penalty, so this return would be rejected if a "
                 "Form 2210 is ever transmitted with it — and the printed packet already "
                 "contradicts itself. Use the documented source penalty on the Form 2210 tab "
                 "instead: it moves both numbers together and records where the figure came from."),
     "notes": ("Catches the pre-2026-07-27 workaround. F2210-006-01 (1040 Business Rules "
               "2025v5.3, Data Mismatch / Reject / Active). WARNING rather than error because this "
               "app transmits no IRS2210 today (only Part II box C is modeled, and it refuses at "
               "extract) — so the reject is latent, not immediate. It becomes an ERROR the day any "
               "Part II box is modelable. FLAGGED FOR RATIFICATION."),
     },
]

P_SCENARIOS: list[dict] = [
    {"scenario_name": "P-T1 — under $1,000 balance → no penalty", "scenario_type": "edge_case", "sort_order": 1,
     "inputs": {"tax_year": 2025, "current_tax": 10000, "withholding": 9500},
     "expected_outputs": {"t2210_penalty": 0},
     "notes": "line 7 = 10,000 − 9,500 = 500 < 1,000 → no penalty."},
    {"scenario_name": "P-T2 — prior-year safe harbor met → no penalty", "scenario_type": "edge_case", "sort_order": 2,
     "inputs": {"tax_year": 2025, "current_tax": 30000, "withholding": 20000, "prior_year_tax": 18000,
                "prior_year_agi": 100000, "est_payments": [0, 0, 0, 0]},
     "expected_outputs": {"t2210_line9": 18000, "t2210_penalty": 0},
     "notes": "l5 = 27,000; l8 = 18,000 (100%); l9 = 18,000; withholding 20,000 ≥ 18,000 → no penalty."},
    {"scenario_name": "P-T3 — full underpayment (no estimates) → penalty", "scenario_type": "normal", "sort_order": 3,
     "inputs": {"tax_year": 2025, "current_tax": 12000, "withholding": 0, "prior_year_tax": 10000,
                "prior_year_agi": 100000, "est_payments": [0, 0, 0, 0]},
     "expected_outputs": {"t2210_line9": 10000, "t2210_penalty": 466},
     "notes": "l5 = 10,800; l8 = 10,000; l9 = 10,000; each installment 2,500 underpaid → 2,500 × (0.070000 + 0.058301 + 0.040658 + 0.017260) = 466 (flat 7% per i2210 2025; was 461 under the retired 6% stub)."},
    {"scenario_name": "P-T4 — 110% high-income safe harbor", "scenario_type": "edge_case", "sort_order": 4,
     "inputs": {"tax_year": 2025, "current_tax": 50000, "withholding": 30000, "prior_year_tax": 40000,
                "prior_year_agi": 200000, "est_payments": [0, 0, 0, 0]},
     "expected_outputs": {"t2210_line9": 44000},
     "notes": "l5 = 45,000; l8 = 40,000 × 1.10 = 44,000; l9 = min = 44,000."},
    {"scenario_name": "P-T5 — estimated payments cure the underpayment", "scenario_type": "edge_case", "sort_order": 5,
     "inputs": {"tax_year": 2025, "current_tax": 12000, "withholding": 0, "prior_year_tax": 10000,
                "prior_year_agi": 100000, "est_payments": [2500, 2500, 2500, 2500]},
     "expected_outputs": {"t2210_penalty": 0},
     "notes": "l9 = 10,000; each installment 2,500 fully paid each period → no underpayment → no penalty."},
    {"scenario_name": "P-T6 — partial estimates → reduced penalty", "scenario_type": "edge_case", "sort_order": 6,
     "inputs": {"tax_year": 2025, "current_tax": 12000, "withholding": 0, "prior_year_tax": 10000,
                "prior_year_agi": 100000, "est_payments": [2500, 2500, 0, 0]},
     "expected_outputs": {"t2210_penalty": 145},
     "notes": "periods 1-2 paid; periods 3-4 underpaid 2,500 each → 2,500 × (0.040658 + 0.017260) = 145 (flat 7%; was 143 under the retired 6% stub)."},
    {"scenario_name": "P-T7 — dated mid-year lump cures earliest-first", "scenario_type": "edge_case", "sort_order": 7,
     "inputs": {"tax_year": 2025, "current_tax": 12000, "withholding": 0, "prior_year_tax": 10000,
                "prior_year_agi": 100000, "payments_dated": [["2025-08-01", 5000]]},
     "expected_outputs": {"t2210_line9": 10000, "t2210_penalty": 219},
     "notes": ("HAND-COMPUTED: installments 2,500 due 4/15/6/15/9/15/25+1/15/26. The 8/1/2025 lump cures "
               "installment 1 after 108 days (2,500×108/365×7% = 51.78) and installment 2 after 47 days "
               "(22.53); installments 3-4 stay unpaid to the cap at flat 7% (101.64 + 43.15). Total "
               "219.10 → 219 (was 217 under the retired 6% stub). "
               "The OLD fixed-day formula could not credit the mid-year cure.")},
    {"scenario_name": "P-T8 — Q4 estimate paid 10 days late", "scenario_type": "edge_case", "sort_order": 8,
     "inputs": {"tax_year": 2025, "current_tax": 12000, "withholding": 0, "prior_year_tax": 10000,
                "prior_year_agi": 100000,
                "payments_dated": [["2025-04-15", 2500], ["2025-06-15", 2500], ["2025-09-15", 2500],
                                    ["2026-01-25", 2500]]},
     "expected_outputs": {"t2210_line9": 10000, "t2210_penalty": 5},
     "notes": ("HAND-COMPUTED: installments 1-3 cured on their due dates (0 days). Installment 4 (due "
               "1/15/2026) cured 1/25/2026 → 10 days @ 7%: 2,500×10/365×7% = 4.79 → 5. The OLD flat "
               "q4 bucket assumed on-time payment → 0 (the understatement this amendment fixes).")},
    {"scenario_name": "P-G1 — no penalty diagnostic", "scenario_type": "diagnostic", "sort_order": 9,
     "inputs": {"tax_year": 2025, "current_tax": 10000, "withholding": 9500},
     "expected_outputs": {"D_2210_NO_PENALTY": True},
     "notes": "line 7 < 1,000 → D_2210_NO_PENALTY."},
    # ── ADDED 2026-07-27 (QA Batch-001 item 10). Fact patterns taken from two
    # real reconciliations against the prior software; no client identifiers —
    # this spec is publicly reachable on the deployed Rule Studio.
    {"scenario_name": "P-T9 — per-column breakdown; 110% harbor computed but not controlling",
     "scenario_type": "normal", "sort_order": 11,
     "inputs": {"tax_year": 2025, "current_tax": 26485, "withholding": 17633, "prior_year_tax": 24975,
                "prior_year_agi": 187696, "filing_status": "mfj", "est_payments": [0, 0, 0, 0]},
     "expected_outputs": {"t2210_line8": 27473, "t2210_line9": 23837, "t2210_penalty": 289,
                          "line_10": [5959.25, 5959.25, 5959.25, 5959.25],
                          "line_17": [1551, 3102, 4653, 5959.25]},
     "notes": ("Pins the FULL per-column derivation, not just the total. l5 = 90% × 26,485 = "
               "23,837; l8 = 24,975 × 1.10 = 27,473 (prior AGI 187,696 > $150,000); l9 = the "
               "SMALLER = 23,837, so the 110% harbor is computed and LOSES — the complement of "
               "P-T4, where it wins. Installments 5,959.25; withholding spreads 4,408.25 per "
               "column, leaving 1,551 short each period.\n\n"
               "NOTE the shape of line 17: it is the RUNNING OUTSTANDING balance, not each "
               "period's own shortfall — 1,551 / 3,102 / 4,653 / 5,959.25, with line 16 holding "
               "the 244.75 that column (d) cannot absorb (16 + 17 = 6,204 = 4 × 1,551, the true "
               "total). That is what line 14 does: each column's payments cover the previous "
               "column's unpaid balance before counting toward this installment. The penalty is "
               "IDENTICAL either way, because charging the running balance over each interval and "
               "charging each period's shortfall from its own due date are the same integral: "
               "1,551×61 + 3,102×92 + 4,653×122 + 6,204×90 = 1,506,021 = 1,551 × 971 amount-days; "
               "× 0.07/365 = 288.83 → 289. Matches the prior software to the dollar under the "
               "flat-7% rate; the retired 6% stub gave 286.")},
    {"scenario_name": "P-T10 — no prior-year facts: the 90% path controls",
     "scenario_type": "normal", "sort_order": 12,
     "inputs": {"tax_year": 2025, "current_tax": 18698, "withholding": 12759, "est_payments": [0, 0, 0, 0]},
     "expected_outputs": {"t2210_line8": 0, "t2210_line9": 16828, "t2210_penalty": 189,
                          "line_17": [1017.25, 2034.50, 3051.75, 4069.00]},
     "notes": ("Prior-year tax blank ⇒ line 8 is UNAVAILABLE (0, not 'computed to zero') and line "
               "9 falls back to the 90% path: 90% × 18,698 = 16,828. Installments 4,207 vs "
               "withholding 3,189.75 per column → 1,017.25 short each period, shown on line 17 as "
               "the running balance 1,017.25 / 2,034.50 / 3,051.75 / 4,069.00 (line 16 is zero "
               "throughout here). 1,017.25 × 971 amount-days × 0.07/365 = 189. Pairs with P-T11: "
               "same return, prior-year facts entered, penalty $0. D_2210_PRIOR_YEAR fires here — "
               "the $189 swing is exactly why that warning exists.")},
    {"scenario_name": "P-T11 — the same return with prior-year facts: harbor met, no penalty",
     "scenario_type": "edge_case", "sort_order": 13,
     "inputs": {"tax_year": 2025, "current_tax": 18698, "withholding": 12759, "prior_year_tax": 11463,
                "prior_year_agi": 129374, "est_payments": [0, 0, 0, 0]},
     "expected_outputs": {"t2210_line8": 11463, "t2210_line9": 11463, "t2210_penalty": 0,
                          "line_17": [0, 0, 0, 0]},
     "notes": ("The safe-harbor swing, and the reason the reconciliation panel exists. Identical "
               "to P-T10 except the prior-year facts: line 8 = 11,463 (AGI 129,374 ≤ $150,000, so "
               "100%), which is SMALLER than the 16,828 90% figure, so line 9 = 11,463. "
               "Installments 2,865.75 are fully covered by 3,189.75 of withholding per column → "
               "no underpayment → penalty 0. A $189 difference driven entirely by one input, with "
               "nothing on screen previously explaining it.")},
    {"scenario_name": "P-G3 — a documented source penalty differs from the computed one",
     "scenario_type": "diagnostic", "sort_order": 14,
     "inputs": {"tax_year": 2025, "current_tax": 18698, "withholding": 12759, "est_payments": [0, 0, 0, 0],
                "penalty_source_amount": 195, "penalty_source_label": "prior software",
                "penalty_source_note": "reconciling the filed return"},
     "expected_outputs": {"D_2210_SRC": True},
     "notes": ("Computed 189 vs a documented source 195 → D_2210_SRC (warning). The return files "
               "195 on BOTH 2210 line 19 and 1040 line 38 (F2210-006-01), while the computed 189 "
               "and its derivation stay visible. A source amount EQUAL to the computed penalty is "
               "corroboration and must NOT fire — the negative control in the harness.")},
    {"scenario_name": "P-G2 — dated payments diverge from line 26", "scenario_type": "diagnostic", "sort_order": 10,
     "inputs": {"tax_year": 2025, "current_tax": 12000, "withholding": 0, "prior_year_tax": 10000,
                "prior_year_agi": 100000, "est_payments": [0, 0, 0, 0],
                "payments_dated": [["2025-04-15", 2500]]},
     "expected_outputs": {"D_2210_DATED": True},
     "notes": ("Dated creditable total 2,500 != the flat line-26 buckets (0) → D_2210_DATED. The penalty "
               "itself uses the dated rows.")},
]

P_RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R-2210-RAP", "IRC_6654", "primary", "§6654(d) the required annual payment"),
    ("R-2210-RAP", "IRS_2025_F2210_INSTR", "secondary", "Part I lines 4-9"),
    ("R-2210-REG", "IRS_2025_F2210_INSTR", "primary", "Part III + the penalty worksheet (§6621)"),
    ("R-2210-REG", "IRC_6654", "secondary", "§6654(a) the addition to tax"),
    ("R-2210-AI", "IRS_2025_F2210_INSTR", "primary", "Schedule AI the annualized method"),
    ("R-2210-FACE", "IRS_2025_F2210_INSTR", "primary", "Part III Section A lines 10-18, the four payment-due-date columns"),
    ("R-2210-SRC", "IRS_2025_1040_MEF_BR", "primary", "F2210-006-01 — TotalPenaltyAmt must equal EsPenaltyAmt"),
    ("R-2210-SRC", "IRS_2025_F2210_INSTR", "secondary", "Line 19 is the amount included on 1040 line 38"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FLOW ASSERTIONS
# ═══════════════════════════════════════════════════════════════════════════

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-1040-2210-01", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "Part I required annual payment + the $1,000 de-minimis",
     "description": "Validates R-2210-RAP. Bug it catches: the 90%/100%/110% wrong, the $1,000 de-minimis not stopping, or the smaller-of not applied.",
     "definition": {"kind": "formula_check", "form": "FORM_2210",
                    "formula": "l9 = min(0.90×current, prior×(1.10 if AGI>150k else 1.0)); l7<1000 → no penalty"},
     "sort_order": 1},
    {"assertion_id": "FA-1040-2210-02", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "Regular Method — the §6621 penalty (flat 7% to 4/15/2026, dated accrual)",
     "description": "Validates R-2210-REG. Bug it catches: the wrong rate (incl. the retired 6% Q2-2026 stub — the 2025 i2210 Penalty Worksheet is ×0.07 in all four rate periods), or accrual not stopping at min(date cured, 4/15/2026).",
     "definition": {"kind": "formula_check", "form": "FORM_2210",
                    "formula": "penalty = Σ chunks: amount × days/365 × 0.07; days run from the installment due date to min(date cured, 2026-04-15); with due-date payments this equals Σ underpayment_i × (DAYS[i]/365 × 0.07), DAYS = [365,304,212,90]"},
     "sort_order": 2},
    {"assertion_id": "FA-1040-2210-03", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "Face columns net by date window; the penalty applies payments earliest-first",
     "description": "Validates R-2210-REG. Bug it catches: withholding not spread on the due dates, the face-column window netting or overpayment carry-forward missing, or penalty payments not applied to the earliest underpaid installment.",
     "definition": {"kind": "formula_check", "form": "FORM_2210",
                    "formula": "FACE column underpayment_i = max(0, installment_i − (withholding/4 + payments in the column's date window + prior-column overpayment)); the PENALTY worksheet separately applies every payment to the EARLIEST still-underpaid installment in date order"},
     "sort_order": 3},
    {"assertion_id": "FA-1040-2210-04", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "The penalty → 1040 line 38",
     "description": "Validates the flow target. Bug it catches: the §6654 penalty not landing on Form 1040 line 38.",
     "definition": {"kind": "flow_assertion", "form": "FORM_2210",
                    "checks": [{"source_line": "19", "must_write_to": ["1040.38"]}]},
     "sort_order": 4},
    {"assertion_id": "FA-1040-2210-05", "assertion_type": "reconciliation", "entity_types": ["1040"],
     "title": "Schedule AI — the annualized installment (smaller-of) + the applicable %",
     "description": "Validates R-2210-AI. Bug it catches: the wrong applicable % (22.5/45/67.5/90), or the smaller-of-regular not applied.",
     "definition": {"kind": "reconciliation", "form": "FORM_2210",
                    "formula": "ai_installment_i = min(max(0, ai_tax_i × pct_i − prior), l9/4); pct = [22.5,45,67.5,90]%"},
     "sort_order": 5},
    {"assertion_id": "FA-1040-2210-06", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "Gates — de-minimis + prior-year safe harbor produce zero penalty",
     "description": "A balance under $1,000, or payments meeting the required annual payment, computes zero penalty (D_2210_NO_PENALTY).",
     "definition": {"kind": "gating_check", "form": "FORM_2210", "expect": {"red_fires": True},
                    "blockers": ["de_minimis", "safe_harbor"]},
     "sort_order": 6},
    {"assertion_id": "FA-1040-2210-07", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "Dated payments stop accrual on the date paid (earliest-first)",
     "description": ("Validates the 2026-07-01 dated amendment to R-2210-REG. Bug it catches: a dated "
                     "payment not curing the earliest underpayment, accrual continuing past the payment "
                     "date, or a late payment silently treated as on time (P-T7 lump=219, P-T8 late Q4=5, "
                     "P-T6 due-date buckets unchanged=145 — flat-7% pins, 2026-07-26)."),
     "definition": {"kind": "formula_check", "form": "FORM_2210",
                    "formula": "for each dated payment: apply to the earliest still-underpaid installment; chunk penalty = amount × days(due → min(paid, 2026-04-15)) / 365 × 0.07; paid ≤ due → 0 days"},
     "sort_order": 7},
    # ADDED 2026-07-27 — QA Batch-001 item 10.
    {"assertion_id": "FA-1040-2210-08", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "Part III Section A carries the 2025 face line numbers (10-18), not the superseded ones",
     "description": ("Validates R-2210-FACE. Bug it catches: the required installment stored as "
                     "line 18 (which on the 2025 face is the OVERPAYMENT) or the underpayment "
                     "stored as line 25 (which does not exist in Part III) — the pre-2026-07-27 "
                     "numbering, inherited from the form's pre-renumber Part IV. Also catches a "
                     "per-column value collapsing to a single figure: line 10 and line 17 each "
                     "carry FOUR column amounts, and the app previously kept only "
                     "installments[0] and the SUM of the underpayments."),
     "definition": {"kind": "formula_check", "form": "FORM_2210",
                    "formula": ("line 10 = required installment per column; line 17 = underpayment "
                                "per column; line 18 = overpayment per column, carried to line 12 "
                                "of the next column; each is a 4-vector over columns (a)-(d)")},
     "sort_order": 8},
    {"assertion_id": "FA-1040-2210-09", "assertion_type": "reconciliation", "entity_types": ["1040"],
     "title": "The 2210 penalty ties to 1040 line 38 (F2210-006-01), override or not",
     "description": ("Validates R-2210-SRC. Bug it catches: a documented source override moving "
                     "1040 line 38 without moving 2210 line 19 (or the reverse), which would "
                     "reject under F2210-006-01 if a 2210 is ever transmitted; or an override "
                     "DESTROYING the computed penalty instead of sitting alongside it."),
     "definition": {"kind": "reconciliation", "form": "FORM_2210",
                    "formula": ("line 19 == 1040 line 38 always; when "
                                "t2210_penalty_source_amount is entered both equal it and the "
                                "computed §6654 penalty remains retrievable; when blank both "
                                "equal the computed penalty")},
     "sort_order": 9},
]


FORMS: list[dict] = [
    {"identity": P_IDENTITY, "facts": P_FACTS, "rules": P_RULES, "lines": P_LINES,
     "diagnostics": P_DIAGNOSTICS, "scenarios": P_SCENARIOS, "rule_links": P_RULE_LINKS},
]


class Command(BaseCommand):
    help = "Load the FORM_2210 spec (Underpayment of Estimated Tax). Refuses until READY_TO_SEED=True."

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING("\nLoad FORM_2210 spec (Underpayment of Estimated Tax)\n"))
        self._load_topics()
        sources = self._load_sources()
        self._load_new_excerpts_on_existing(sources)
        for spec in FORMS:
            form = self._upsert_form(spec["identity"])
            self._upsert_facts(form, spec["facts"])
            rules = self._upsert_rules(form, spec["rules"])
            self._upsert_authority_links(rules, sources, spec["rule_links"])
            self._upsert_lines(form, spec["lines"])
            self._retire_superseded_lines(form)
            self._upsert_diagnostics(form, spec["diagnostics"])
            self._upsert_tests(form, spec["scenarios"])
        self._upsert_form_links(sources)
        self._load_flow_assertions()
        self._report_totals()

    def _guard_against_hollow_seed(self):
        empty = []
        for spec in FORMS:
            fn = spec["identity"]["form_number"]
            for key in ("facts", "rules", "lines", "diagnostics", "scenarios", "rule_links"):
                if not spec[key]:
                    empty.append(f"{fn}.{key}")
        if not FLOW_ASSERTIONS:
            empty.append("FLOW_ASSERTIONS")
        if not READY_TO_SEED or empty:
            still_empty = "\n  ".join(f"- {n}" for n in empty) or "(all populated)"
            raise CommandError(
                "\nREFUSING TO SEED FORM_2210: not cleared to seed.\n\n"
                "Gated until Ken's review walk (the safe-harbor + the regular-method penalty\n"
                "rate periods + Schedule AI + the §6621 rates).\n\n"
                f"READY_TO_SEED = {READY_TO_SEED} (must be True)\n\n"
                f"Currently empty / placeholder:\n  {still_empty}\n"
            )

    def _load_topics(self):
        ct = 0
        for code, name in AUTHORITY_TOPICS:
            _, created = AuthorityTopic.objects.update_or_create(topic_code=code, defaults={"topic_name": name})
            ct += 1 if created else 0
        self.stdout.write(f"Topics: {ct} new ({len(AUTHORITY_TOPICS)} in batch)")

    def _load_sources(self) -> dict:
        sources: dict = {}
        for src_data in AUTHORITY_SOURCES:
            src_data = dict(src_data)
            excerpts_data = src_data.pop("excerpts", [])
            topic_codes = src_data.pop("topics", [])
            source, _ = AuthoritySource.objects.update_or_create(
                source_code=src_data["source_code"], defaults=src_data)
            sources[source.source_code] = source
            for exc in excerpts_data:
                exc = dict(exc)
                AuthorityExcerpt.objects.update_or_create(
                    authority_source=source, excerpt_label=exc["excerpt_label"], defaults=exc)
            for tc in topic_codes:
                topic = AuthorityTopic.objects.filter(topic_code=tc).first()
                if topic:
                    AuthoritySourceTopic.objects.get_or_create(authority_source=source, authority_topic=topic)
        for code in EXISTING_SOURCES_TO_REFERENCE:
            src = AuthoritySource.objects.filter(source_code=code).first()
            if src:
                sources[code] = src
        self.stdout.write(f"Sources ready: {len(sources)}")
        return sources

    def _load_new_excerpts_on_existing(self, sources):
        for code, exc in NEW_EXCERPTS_ON_EXISTING:
            src = sources.get(code) or AuthoritySource.objects.filter(source_code=code).first()
            if src:
                exc = dict(exc)
                AuthorityExcerpt.objects.update_or_create(
                    authority_source=src, excerpt_label=exc["excerpt_label"], defaults=exc)

    def _upsert_form(self, identity: dict) -> TaxForm:
        form, created = TaxForm.objects.update_or_create(
            form_number=identity["form_number"], jurisdiction=FORM_JURISDICTION,
            tax_year=FORM_TAX_YEAR, version=FORM_VERSION,
            defaults={"form_title": identity["form_title"], "entity_types": FORM_ENTITY_TYPES,
                      "status": FORM_STATUS, "notes": identity["notes"]})
        self.stdout.write(f"{'Created' if created else 'Updated'} {identity['form_number']}")
        return form

    def _upsert_facts(self, form, facts):
        for f in facts:
            f = dict(f)
            FormFact.objects.update_or_create(tax_form=form, fact_key=f.pop("fact_key"), defaults=f)
        self.stdout.write(f"  {len(facts)} facts")

    def _upsert_rules(self, form, rules_data) -> dict:
        created = {}
        for r in rules_data:
            r = dict(r)
            rule, _ = FormRule.objects.update_or_create(tax_form=form, rule_id=r.pop("rule_id"), defaults=r)
            created[rule.rule_id] = rule
        self.stdout.write(f"  {len(created)} rules")
        return created

    def _upsert_authority_links(self, rules, sources, rule_links):
        ct = 0
        for rule_id, source_code, level, note in rule_links:
            rule, source = rules.get(rule_id), sources.get(source_code)
            if rule and source:
                RuleAuthorityLink.objects.get_or_create(
                    form_rule=rule, authority_source=source,
                    defaults={"support_level": level, "relevance_note": note})
                ct += 1
        self.stdout.write(f"  {ct} authority links")

    def _upsert_lines(self, form, lines):
        for ln in lines:
            ln = dict(ln)
            FormLine.objects.update_or_create(tax_form=form, line_number=ln.pop("line_number"), defaults=ln)
        self.stdout.write(f"  {len(lines)} lines")

    def _retire_superseded_lines(self, form):
        """DELETE line numbers this spec used to author that don't exist on the
        2025 face (RETIRED_LINES). Upserting the corrected set is not enough —
        the old row would survive in the export alongside the new one, which is
        exactly how two contradictory versions of a thing stay invisible for
        weeks (s122). Idempotent: nothing to delete on a re-run."""
        if not RETIRED_LINES:
            return
        gone, _ = FormLine.objects.filter(
            tax_form=form, line_number__in=RETIRED_LINES).delete()
        if gone:
            self.stdout.write(self.style.WARNING(
                f"  retired {gone} superseded line(s): {', '.join(RETIRED_LINES)}"))
        else:
            self.stdout.write(f"  retired lines: none present ({', '.join(RETIRED_LINES)})")

    def _upsert_diagnostics(self, form, diagnostics):
        for d in diagnostics:
            d = dict(d)
            FormDiagnostic.objects.update_or_create(tax_form=form, diagnostic_id=d.pop("diagnostic_id"), defaults=d)
        self.stdout.write(f"  {len(diagnostics)} diagnostics")

    def _upsert_tests(self, form, scenarios):
        for t in scenarios:
            t = dict(t)
            TestScenario.objects.update_or_create(tax_form=form, scenario_name=t.pop("scenario_name"), defaults=t)
        self.stdout.write(f"  {len(scenarios)} test scenarios")

    def _upsert_form_links(self, sources):
        for source_code, form_code, link_type in AUTHORITY_FORM_LINKS:
            source = sources.get(source_code) or AuthoritySource.objects.filter(source_code=source_code).first()
            if source:
                AuthorityFormLink.objects.get_or_create(
                    authority_source=source, form_code=form_code, link_type=link_type,
                    defaults={"note": f"{source_code} -> {form_code}"})

    def _load_flow_assertions(self):
        for a in FLOW_ASSERTIONS:
            a = dict(a)
            FlowAssertion.objects.update_or_create(assertion_id=a.pop("assertion_id"), defaults=a)
        self.stdout.write(f"  {len(FLOW_ASSERTIONS)} flow assertions")

    def _report_totals(self):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"TaxForms: {TaxForm.objects.count()} | FlowAssertions: {FlowAssertion.objects.count()}")
        form = TaxForm.objects.filter(form_number="FORM_2210").first()
        if form:
            uncited = [r for r in FormRule.objects.filter(tax_form=form) if not r.authority_links.exists()]
            self.stdout.write("FORM_2210: all rules cited" if not uncited
                              else self.style.WARNING(f"FORM_2210 uncited rules: {len(uncited)}"))
