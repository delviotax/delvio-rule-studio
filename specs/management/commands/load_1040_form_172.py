"""Load the FORM_172 spec — Net Operating Losses (NOLs) for Individuals.

KEN'S RULINGS (2026-08-12 live, s253 — delvio-tax DECISIONS.md "The NOL
rulebook walk"): the s246 authoring brief's four questions, answered:
  1. Scope: BOTH SIDES in v1 — the deduction side (pools → ordered
     absorption → negative Schedule 1 line 8a) AND the generation side
     (Form 172 Part I — computing a new NOL in a loss year). Ken overrode
     the deduction-only recommendation.
  2. Farming carryback: REFUSE BY NAME — a Form 1045 / per-year 1040-X
     paper workflow (the s223 doctrine). No carryback computation.
  3. AMT NOL (ATNOLD): PRESERVE-ONLY — the nol_amt pools roll and print;
     the 6251 interaction stays with the keyed amt_nol aggregate. The
     90%-of-AMTI limitation is a future authored rule.
  4. The 80% base VERBATIM from i172/§172(a)(2) — see THE MATH below; the
     full statutory sentence includes the "over the pre-2018 NOLs carried
     to the year" clause the brief's short form compressed. Surfaced at
     Gate 1 explicitly.

THE GAP (verify-first, s235/s246): /api/forms/lookup/172|NOL|FORM_172|1045
all 404. The app already PRESERVES: CarryforwardAttribute pools
`nol_regular`/`nol_amt` BY LOSS-YEAR VINTAGE (transcribed opening/used/
remaining, per-vintage roll, D_CFWD_001 red "verify by hand", worksheet
print). Schedule 1 line 8a exists on the seeded SCH_1 face as a KEYED
line. Every NOL pool in the shared DB carries a PERMANENT error until
this spec exists — that is the cost of the 404-STOP, working as designed.

LAW VERIFIED 2026-08-12 against primary sources (fetched, not memory):
  - Form 172 (Rev. December 2024), 3 pp. — Part I lines 1-24 (the NOL for
    a loss year; line 24 combines lines 1, 9, 17, and 21-23; "If the
    result is less than zero, enter it here. If the result is zero or
    more, you don't have an NOL"). Part II lines 1-10 (the carryback-year
    absorption schedule, "Start with the earliest carryback year") +
    lines 11-33 (the itemized-deduction adjustment for carryback years).
  - i172 (Rev. December 2024, 7 pp.) — THE SUCCESSOR TO PUB 536 (p536.pdf
    404s; its computation and carryover rules live here). Verbatims
    captured below: the Reminders' two-tier deduction limitation, the
    farming-loss 2-year carryback exception and its waiver election, the
    "Deducting a Carryforward" Schedule-1 destination ("list your NOL
    deduction as a negative figure on Schedule 1 (Form 1040)"), the
    modified-taxable-income definition (How to Figure an NOL Carryover),
    the oldest-first ordering, the excess-business-loss worksheet WITH
    the IRS's own worked example, and the marital/filing-status change
    split rules with i172 Examples 1-2.
  - IRC §172 (uscode.house.gov, prelim) — §172(a)(2) VERBATIM: the
    deduction for years beginning after 2020 is "the sum of— (A) the
    aggregate amount of net operating losses arising in taxable years
    beginning before January 1, 2018, carried to such taxable year, plus
    (B) the lesser of— (i) the aggregate amount of net operating losses
    arising in taxable years beginning after December 31, 2017, carried
    to such taxable year, or (ii) 80 percent of the excess (if any) of—
    (I) taxable income computed without regard to the deductions under
    this section and sections 199A and 250, over (II) the amount
    determined under subparagraph (A)." §172(b)(1)(A)(ii): pre-2018
    losses carry to "each of the 20 taxable years following"; post-2017
    losses carry forward indefinitely. §172(b)(1)(B): the farming 2-year
    carryback. §172(b)(3): the waiver election.

⚠ KNOWN SOURCE ANOMALY, RECORDED NOT SMOOTHED (requires_human_review):
  i172's "NOL Carryover with an Excess Business Loss Worksheet" line 1
  reads "Enter the amount from Form 172, line 33, if less than zero" —
  but Part I's NOL is LINE 24 (line 33 is Part II's itemized-adjustment
  combine, which has no less-than-zero reading). Almost certainly an IRS
  drafting slip for "line 24"; the worksheet's own example is consistent
  with line 24. The spec follows the arithmetic the example demonstrates
  and flags the citation.

v1 SCOPE (every limit is a DECLARED diagnostic, never a silent gap):
  - 1040 individuals only. Estates/trusts (the line-1 variant, Form 1041
    destinations) REFUSE via D_172_ESTATE_TRUST.
  - NO carryback computation of any kind (Ken ruling #2): a farming-loss
    carryback claim refuses by name via D_172_FARM_CARRYBACK; Part II's
    face lines are specced for TRANSCRIPTION/print completeness only.
  - Marital/filing-status changes across NOL years are NOT computed —
    D_172_MARITAL_SPLIT holds with the i172 split rules stated.
  - AMT NOL: preserve-only (Ken ruling #3) — D_172_ATNOLD_HOLD states it.
  - §965 carryback years: the form may not be used (i172 caution) — moot
    under the carryback refusal; recorded in R-172-FARM-CB's notes.

SAFETY GUARD: READY_TO_SEED stays False until Ken's Gate-1 review walk.
"""

from decimal import Decimal

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


# Gate 1 is a human gate; never flip this unattended.
READY_TO_SEED = False


FORM_JURISDICTION = "FED"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_ENTITY_TYPES = ["1040"]
FORM_STATUS = "draft"

# Face line 19: the capital-loss limitation constants — STATUTORY (§1211(b)),
# non-indexed, and PRINTED on the face ("$3,000 (If filing Form 1040, $1,500
# when married filing separately)"). Never inflation-adjust.
CAP_LOSS_LIMIT = Decimal("3000")
CAP_LOSS_LIMIT_MFS = Decimal("1500")

# §172(a)(2)(B)(ii) — statutory, non-indexed.
POST2017_PCT = Decimal("0.80")

# §172(b)(1)(A)(ii)(I) — pre-2018 NOLs expire after 20 carryover years.
PRE2018_CARRYOVER_YEARS = 20

# The vintage boundary, from the statute's own words: "arising in taxable
# years beginning before January 1, 2018" vs "after December 31, 2017".
VINTAGE_BOUNDARY_YEAR = 2018  # vintage_year < 2018 → pre-2018 class


def _D(x):
    return Decimal(str(x if x is not None else 0))


# ═══════════════════════════════════════════════════════════════════════════
# THE MATH — reference implementations. The app's build leg re-types these
# independently; they share no code, so a transcription slip on either side
# shows up as a scenario failure.
#
# PART I (the generation side), straight off the Rev. 12-2024 face:
#   l4  = MAX(0, l2 − l3)              nonbusiness capital-loss excess
#   l5  = MAX(0, l3 − l2)              nonbusiness capital-gain excess
#   l8  = l5 + l7
#   l9  = MAX(0, l6 − l8)              nonbusiness-deduction excess (add-back)
#   l10 = MIN(MAX(0, l8 − l6), l5)     the capped spill of nonbusiness gains
#   l13 = l10 + l12
#   l14 = MAX(0, l11 − l13)            business capital-loss excess
#   l15 = l4 + l14
#   lines 16-21 engage ONLY when line 16 carries a loss or line 17 a §1202
#   exclusion ("If you don't have a loss on that line (and don't have a
#   section 1202 exclusion), skip lines 16 through 21 and enter on line 22
#   the amount from line 15"):
#     l18 = MAX(0, l16 − l17)
#     l19 = MIN(l16, 3000 | 1500 MFS) when l16 > 0 else 0
#     l20 = MAX(0, l18 − l19)
#     l21 = MAX(0, l19 − l18)
#     l22 = MAX(0, l15 − l20)
#   l24 = l1 + l9 + l17 + l21 + l22 + l23   ("Combine lines 1, 9, 17, and
#         21 through 23") — less than zero → that IS the NOL; zero or more
#         → no NOL.
#
# THE DEDUCTION (§172(a)(2) verbatim, two tiers):
#   pre  = Σ remaining pre-2018 vintages carried to the year   (NO 80% cap;
#          they may exceed taxable income — that is how carryovers arise)
#   base = MAX(0, TI_without_NOL_QBI_250 − pre)                ("the excess
#          (if any) of (I) ... over (II)")
#   post_allowed = MIN(Σ remaining post-2017 vintages, 80% × base)
#   deduction    = pre + post_allowed  → a NEGATIVE figure on Sch 1 line 8a
#
# ABSORPTION / CARRYOVER (i172 "How to Figure an NOL Carryover" + §172(b)(2)):
#   vintages absorb OLDEST FIRST against modified taxable income (MTI —
#   taxable income without the NOL being figured or later NOLs, without the
#   capital-loss-in-excess-of-gains deduction, plus any §1202 exclusion,
#   without exemptions, with AGI-derived items refigured; floored at zero).
#   A post-2017 vintage additionally cannot absorb beyond its 80%-capped
#   allowance for the year.
#   ⚠ SYNTHESIS FLAG (requires_human_review — walked at Gate 1): i172 states
#   the MTI absorption rule and the 80% deduction cap in separate places;
#   combining them per vintage (used = MIN(remaining, class allowance
#   remaining, MTI remaining)) follows §172(a)(2) + (b)(2) but is this
#   spec's synthesis, not a single quoted sentence.
# ═══════════════════════════════════════════════════════════════════════════


def compute_172_part_i(
    l1_income_base=0,
    l2_nonbus_cap_losses=0,
    l3_nonbus_cap_gains=0,
    l6_nonbus_deductions=0,
    l7_nonbus_income=0,
    l11_bus_cap_losses=0,
    l12_bus_cap_gains=0,
    l16_schd_combined_loss=0,
    l17_sec1202_exclusion=0,
    l23_prior_nol_deduction=0,
    mfs=False,
) -> dict:
    """Form 172 Part I, lines 1-24, one loss year. Whole-dollar inputs.

    Returns every computed line plus `nol` (POSITIVE pool amount, or 0 when
    line 24 is zero or more — 'you don't have an NOL')."""
    l1 = _D(l1_income_base)
    l2, l3 = _D(l2_nonbus_cap_losses), _D(l3_nonbus_cap_gains)
    l6, l7 = _D(l6_nonbus_deductions), _D(l7_nonbus_income)
    l11, l12 = _D(l11_bus_cap_losses), _D(l12_bus_cap_gains)
    l16, l17 = _D(l16_schd_combined_loss), _D(l17_sec1202_exclusion)
    l23 = _D(l23_prior_nol_deduction)
    Z = Decimal("0")

    l4 = max(Z, l2 - l3)
    l5 = max(Z, l3 - l2)
    l8 = l5 + l7
    l9 = max(Z, l6 - l8)
    l10 = min(max(Z, l8 - l6), l5)
    l13 = l10 + l12
    l14 = max(Z, l11 - l13)
    l15 = l4 + l14

    if l16 == Z and l17 == Z:
        # The face's skip rule: no Schedule D loss and no §1202 exclusion.
        l18 = l19 = l20 = l21 = Z
        l22 = l15
        skipped = True
    else:
        l18 = max(Z, l16 - l17)
        cap = CAP_LOSS_LIMIT_MFS if mfs else CAP_LOSS_LIMIT
        l19 = min(l16, cap) if l16 > Z else Z
        l20 = max(Z, l18 - l19)
        l21 = max(Z, l19 - l18)
        l22 = max(Z, l15 - l20)
        skipped = False

    l24 = l1 + l9 + l17 + l21 + l22 + l23
    return {
        "l4": l4, "l5": l5, "l8": l8, "l9": l9, "l10": l10, "l13": l13,
        "l14": l14, "l15": l15, "l18": l18, "l19": l19, "l20": l20,
        "l21": l21, "l22": l22, "l24": l24, "skipped_16_21": skipped,
        "nol": -l24 if l24 < Z else Z,
    }


def compute_nol_deduction(vintages, ti_without_nol_qbi_250) -> dict:
    """§172(a)(2) — the two-tier NOL deduction for a carryforward year.

    `vintages`: [(loss_year, remaining_amount), ...] — order irrelevant here
    (the split is by class); absorption ordering is handled in
    compute_nol_absorption. Returns the deduction (POSITIVE; Schedule 1
    line 8a prints its negative) and the capped-class detail for the
    80%-limitation statement."""
    ti = _D(ti_without_nol_qbi_250)
    Z = Decimal("0")
    pre = sum((_D(a) for y, a in vintages if int(y) < VINTAGE_BOUNDARY_YEAR), Z)
    post = sum((_D(a) for y, a in vintages if int(y) >= VINTAGE_BOUNDARY_YEAR), Z)
    base = max(Z, ti - pre)                      # "the excess (if any) of (I) over (II)"
    post_cap = (POST2017_PCT * base).quantize(Decimal("1"))
    post_allowed = min(post, post_cap)
    return {
        "pre2018_component": pre,
        "post2017_component": post_allowed,
        "post2017_cap": post_cap,
        "cap_binds": post > post_allowed,
        "deduction": pre + post_allowed,
    }


def compute_nol_absorption(vintages, ti_without_nol_qbi_250, modified_taxable_income) -> list:
    """Per-vintage utilization for the carryforward year, OLDEST FIRST.

    used(vintage) = MIN(remaining, class allowance remaining, MTI remaining).
    Pre-2018 vintages draw on an UNCAPPED allowance; post-2017 vintages draw
    on the 80% cap computed in compute_nol_deduction. MTI is floored at zero
    by its own definition ("Your taxable income as modified cannot be less
    than zero"). Returns [(loss_year, used, remaining_after), ...]."""
    Z = Decimal("0")
    ded = compute_nol_deduction(vintages, ti_without_nol_qbi_250)
    mti_left = max(Z, _D(modified_taxable_income))
    post_allow_left = ded["post2017_component"]
    out = []
    for year, amount in sorted(vintages, key=lambda v: int(v[0])):
        amt = _D(amount)
        if int(year) < VINTAGE_BOUNDARY_YEAR:
            used = min(amt, mti_left)
        else:
            used = min(amt, post_allow_left, mti_left)
            post_allow_left -= used
        mti_left -= used
        out.append((int(year), used, amt - used))
    return out


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY
# ═══════════════════════════════════════════════════════════════════════════

AUTHORITY_TOPICS: list[tuple[str, str]] = [
    ("nol_deduction_and_carryover",
     "§172 net operating losses: Part I generation in a loss year, the two-tier "
     "§172(a)(2) deduction with the 80% limitation, oldest-first absorption and "
     "carryover, the farming-loss carryback exception and waiver, the excess-"
     "business-loss (§461(l)) NOL feed, and the Schedule 1 line 8a destination"),
]

EXISTING_SOURCES_TO_REFERENCE: list[str] = [
    "IRS_2025_SCH1_FORM",   # the line 8a destination on the seeded SCH_1 face
]

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "IRC_172",
        "source_type": "code_section",
        "source_rank": "controlling",
        "jurisdiction_code": "FED",
        "entity_type_code": "1040",
        "tax_year_start": 2025,
        "tax_year_end": 2025,
        "title": "IRC §172 — Net operating loss deduction",
        "citation": "26 U.S.C. §172 (prelim., fetched 2026-08-12)",
        "issuer": "U.S. Congress",
        "official_url": "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section172&num=0&edition=prelim",
        "current_status": "active",
        "is_substantive_authority": True,
        "is_filing_authority": False,
        "trust_score": 10.00,
        "requires_human_review": False,
        "notes": (
            "The operative statute. (a)(2) is the two-tier deduction captured VERBATIM below — note "
            "the full sentence: the 80% applies to the EXCESS of the taxable-income base OVER the "
            "pre-2018 NOLs carried to the year (the pre-2018 class eats the base first). "
            "(b)(1)(A)(ii): pre-2018 losses carry to each of the 20 following years; post-2017 "
            "losses carry forward indefinitely. (b)(1)(B): the 2-year farming carryback (refused in "
            "v1 per Ken ruling #2). (b)(2): the absorption ordering statute behind i172's "
            "oldest-first rule. (b)(3): the carryback waiver election."
        ),
        "topics": ["nol_deduction_and_carryover"],
        "excerpts": [
            {"excerpt_label": "§172(a)(2) — the two-tier deduction, verbatim",
             "excerpt_text": (
                 "in the case of a taxable year beginning after December 31, 2020, the sum of— (A) the "
                 "aggregate amount of net operating losses arising in taxable years beginning before "
                 "January 1, 2018, carried to such taxable year, plus (B) the lesser of— (i) the "
                 "aggregate amount of net operating losses arising in taxable years beginning after "
                 "December 31, 2017, carried to such taxable year, or (ii) 80 percent of the excess "
                 "(if any) of— (I) taxable income computed without regard to the deductions under this "
                 "section and sections 199A and 250, over (II) the amount determined under "
                 "subparagraph (A)."),
             "notes": "Fetched from uscode.house.gov 2026-08-12 (the s232 paraphrase lesson: LII paraphrases are not verbatims)."},
        ],
    },
    {
        "source_code": "IRS_2024_F172_FORM",
        "source_type": "official_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "FED",
        "entity_type_code": "1040",
        "tax_year_start": 2025,
        "tax_year_end": 2025,
        "title": "Form 172 (Rev. December 2024) — Net Operating Losses (NOLs)",
        "citation": "Form 172 (Rev. 12-2024); Cat. No. 16545W; 'For Individuals, Estates, and Trusts'",
        "issuer": "IRS",
        "official_url": "https://www.irs.gov/pub/irs-pdf/f172.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "is_filing_authority": True,
        "trust_score": 10.00,
        "requires_human_review": False,
        "notes": (
            "The face. Part I lines 1-24: every arithmetic step is printed on the line itself "
            "(transcribed into THE MATH above, line by line, 2026-08-12). Line 19 prints the "
            "$3,000/$1,500-MFS capital-loss limitation. Line 24: 'Combine lines 1, 9, 17, and 21 "
            "through 23. If the result is less than zero, enter it here. If the result is zero or "
            "more, you don't have an NOL.' Part II lines 1-10 are the carryback absorption schedule "
            "('Start with the earliest carryback year'); lines 11-33 adjust itemized deductions for "
            "carryback years. Part II is TRANSCRIPTION-ONLY in v1 (Ken ruling #2 refuses carrybacks)."
        ),
        "topics": ["nol_deduction_and_carryover"],
        "excerpts": [
            {"excerpt_label": "Part I line 24 — the NOL determination, verbatim",
             "excerpt_text": (
                 "NOL. Combine lines 1, 9, 17, and 21 through 23. If the result is less than zero, "
                 "enter it here. If the result is zero or more, you don't have an NOL."),
             "notes": "The generation-side terminal line."},
            {"excerpt_label": "Part I line 16 — the skip rule, verbatim",
             "excerpt_text": (
                 "Enter, if any, the combined net short-term and long-term capital loss from your "
                 "Schedule D (Form 1040). ... Enter as a positive number. If you don't have a loss on "
                 "that line (and don't have a section 1202 exclusion), skip lines 16 through 21 and "
                 "enter on line 22 the amount from line 15."),
             "notes": "Lines 16-21 engage only on a Schedule D loss or a §1202 exclusion."},
        ],
    },
    {
        "source_code": "IRS_2024_F172_INSTR",
        "source_type": "official_instructions",
        "source_rank": "primary_official",
        "jurisdiction_code": "FED",
        "entity_type_code": "1040",
        "tax_year_start": 2025,
        "tax_year_end": 2025,
        "title": "Instructions for Form 172 (Rev. December 2024) — the successor to Pub. 536",
        "citation": "Instructions for Form 172 (Rev. 12-2024); Catalog Number 94487B; Dec 23, 2024",
        "issuer": "IRS",
        "official_url": "https://www.irs.gov/pub/irs-pdf/i172.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "is_filing_authority": True,
        "trust_score": 10.00,
        "requires_human_review": True,
        "notes": (
            "Pub 536 is RETIRED (p536.pdf 404s); its rules live here. requires_human_review is set "
            "for ONE anomaly: the 'NOL Carryover with an Excess Business Loss Worksheet' line 1 cites "
            "'Form 172, line 33, if less than zero' — but the NOL is Part I LINE 24 (line 33 is Part "
            "II's itemized-adjustment combine, which has no less-than-zero reading). Almost certainly "
            "a drafting slip for 'line 24'; the worksheet's own example is consistent with line 24. "
            "The spec follows the demonstrated arithmetic and KEEPS the citation flagged rather than "
            "silently correcting the IRS's text."
        ),
        "topics": ["nol_deduction_and_carryover"],
        "excerpts": [
            {"excerpt_label": "Reminders — the deduction limitation, verbatim",
             "excerpt_text": (
                 "NOL deduction limitation. In general, your NOL deduction for tax years beginning "
                 "after December 31, 2020, cannot exceed the sum of: (1) the NOLs carried to the year "
                 "from tax years beginning before January 1, 2018; plus, (2) the lesser of: (a) the "
                 "NOLs carried to the year from tax years beginning after December 31, 2017, or (b) "
                 "80% of the excess (if any) of taxable income computed without regard to deductions "
                 "for NOLs, or Qualified Business Income (QBI), or section 250 deductions, over the "
                 "NOLs carried to the year from tax years beginning before January 1, 2018."),
             "notes": "The instruction-side statement of §172(a)(2); the two agree word for substance."},
            {"excerpt_label": "Farming carryback + the no-carryback rule, verbatim",
             "excerpt_text": (
                 "NOL carryback eliminated. Generally, you can only carry NOLs arising in tax years "
                 "after 2020 to a later year. An exception applies to certain farming losses, which "
                 "may be carried back 2 years. ... Only the farming loss portion of an NOL can be "
                 "carried back 2 years. The 80% limitation rule does not apply to a carryback period "
                 "before 2021."),
             "notes": "The v1 refusal's authority (Ken ruling #2)."},
            {"excerpt_label": "Deducting a Carryforward — the destination, verbatim",
             "excerpt_text": (
                 "If you carry forward your NOL to a tax year after the NOL year, list your NOL "
                 "deduction as a negative figure on Schedule 1 (Form 1040) for the year to which the "
                 "NOL is carried. ... Attach a Form 172 for each NOL to your Form 1040 or Form 1041 "
                 "if it applies."),
             "notes": "Schedule 1 line 8a, as a NEGATIVE figure; one Form 172 per NOL."},
            {"excerpt_label": "Modified taxable income, verbatim (carryover absorption)",
             "excerpt_text": (
                 "Your carryover is the excess of your NOL deduction over your modified taxable "
                 "income for the carryback or carryforward year. If your NOL deduction includes more "
                 "than one NOL, apply the NOLs against your modified taxable income in the same order "
                 "in which you incurred them, starting with the earliest. Modified taxable income. "
                 "Your modified taxable income is your taxable income figured with the following "
                 "changes. 1. You cannot claim an NOL deduction for the NOL carryover you are "
                 "figuring or for any later NOL. 2. You cannot claim a deduction for capital losses "
                 "in excess of your capital gains. Also, you must increase your taxable income by the "
                 "amount of any section 1202 exclusion. 3. You cannot claim a deduction for your "
                 "exemptions ... 4. You must figure any item affected by the amount of your AGI after "
                 "making the changes in (1), (2), and (3) ... Your taxable income as modified cannot "
                 "be less than zero."),
             "notes": "The absorption mechanics; item 4 is the AGI-cascade refigure (the app implements it as a counterfactual compute of its own return)."},
            {"excerpt_label": "The 80% caution + the statement requirement, verbatim",
             "excerpt_text": (
                 "NOLs arising after 2017 and carried forward to a year after 2020 are subject to the "
                 "80%-of-taxable-income limit. The total amount of any NOL deduction for 2021 or "
                 "thereafter that is attributable to NOLs from tax years after 2017 can't exceed 80% "
                 "of taxable income without regard to the NOL deduction or sections 199A or 250. "
                 "Attach a statement to your tax return showing how you figured the 80% limitation, "
                 "if applicable."),
             "notes": "The attach-a-statement duty behind D_172_80PCT_STATEMENT."},
            {"excerpt_label": "Excess business loss — the worksheet example, verbatim",
             "excerpt_text": (
                 "Example. For the current tax year, an unmarried taxpayer operates a Schedule C "
                 "business and incurs a loss of $1 million. The taxpayer completes Form 461 and "
                 "determines that they have incurred an excess business loss of $738,000. The "
                 "taxpayer reports the excess business loss as a positive number on Schedule 1 (Form "
                 "1040 or 1040-SR) – effectively offsetting part of the loss claimed on Schedule C. "
                 "This excess business loss of $738,000 will be treated as an NOL carryover to the "
                 "next tax year."),
             "notes": ("The IRS's own worked example → scenario 172-T9. ⚠ The worksheet's line-1 "
                       "citation ('Form 172, line 33') is the flagged anomaly — see source notes.")},
            {"excerpt_label": "Waiving the carryback period, verbatim",
             "excerpt_text": (
                 "To make this choice, attach a statement to your original return filed by the due "
                 "date (including extensions) for the NOL year. This statement must show that you are "
                 "choosing to waive the carryback period under section 172(b). ... Once you choose to "
                 "waive the carryback period, it is generally irrevocable."),
             "notes": "The waiver election the farming-carryback refusal points the preparer to."},
        ],
    },
]

# Excerpts to attach to sources that already exist in the RS DB.
NEW_EXCERPTS_ON_EXISTING: list[tuple[str, dict]] = [
    ("IRS_2025_SCH1_FORM",
     {"excerpt_label": "Schedule 1 line 8a — the NOL destination",
      "excerpt_text": "Net operating loss",
      "notes": ("The seeded SCH_1 face's line 8a caption. i172: the carryforward deduction is "
                "listed 'as a negative figure' there. FORM_172's R-172-DEST derives it.")}),
]


# ═══════════════════════════════════════════════════════════════════════════
# FACTS
# ═══════════════════════════════════════════════════════════════════════════

FACTS: list[dict] = [
    # ── Part I inputs (the generation side — one Form 172 per loss year) ──
    {"fact_key": "f172_l1_income_base", "label": "Line 1 — AGI minus standard/itemized deductions (individuals)",
     "data_type": "decimal", "sort_order": 1,
     "notes": ("Individuals: AGI − standard or itemized deductions (typically negative in a loss "
               "year). The app derives it from its own computed return (1040 line 11 − line 12); "
               "estates/trusts have a different line-1 recipe and REFUSE in v1 "
               "(D_172_ESTATE_TRUST).")},
    {"fact_key": "f172_l2_nonbus_cap_losses", "label": "Line 2 — Nonbusiness capital losses before limitation (positive)",
     "data_type": "decimal", "default_value": "0", "sort_order": 2,
     "notes": "Excludes §1202 exclusion amounts (i172 line-2 note)."},
    {"fact_key": "f172_l3_nonbus_cap_gains", "label": "Line 3 — Nonbusiness capital gains (without regard to §1202)",
     "data_type": "decimal", "default_value": "0", "sort_order": 3},
    {"fact_key": "f172_l6_nonbus_deductions", "label": "Line 6 — Nonbusiness deductions (positive)",
     "data_type": "decimal", "default_value": "0", "sort_order": 4,
     "notes": ("i172's line-6 list: HSA/Archer deductions, SEP/SIMPLE for the self-employed, IRA "
               "deductions, alimony paid, most itemized deductions (except federally-declared-"
               "disaster casualty/theft and state income tax on trade/business income), and the "
               "STANDARD DEDUCTION. The business-side exclusions (SE health insurance, ½-SE tax, "
               "rental losses, educator expenses ...) are in the same instruction — the "
               "classification is preparer judgment the app can PREFILL from its own return but "
               "never silently own.")},
    {"fact_key": "f172_l7_nonbus_income", "label": "Line 7 — Nonbusiness income other than capital gains",
     "data_type": "decimal", "default_value": "0", "sort_order": 5,
     "notes": ("i172's line-7 list: taxable IRA distributions, pensions, social security benefits, "
               "annuities, dividends, investment interest, nonbusiness pass-through income. Wages, "
               "SE income, UNEMPLOYMENT COMPENSATION and rental income are BUSINESS income and stay "
               "out of line 7.")},
    {"fact_key": "f172_l11_bus_cap_losses", "label": "Line 11 — Business capital losses before limitation (positive)",
     "data_type": "decimal", "default_value": "0", "sort_order": 6},
    {"fact_key": "f172_l12_bus_cap_gains", "label": "Line 12 — Business capital gains (without regard to §1202)",
     "data_type": "decimal", "default_value": "0", "sort_order": 7},
    {"fact_key": "f172_l16_schd_combined_loss", "label": "Line 16 — Combined net ST+LT capital loss from Schedule D (positive)",
     "data_type": "decimal", "default_value": "0", "sort_order": 8,
     "notes": "Zero when Schedule D shows no combined loss; with line 17 also zero, lines 16-21 SKIP."},
    {"fact_key": "f172_l17_sec1202_exclusion", "label": "Line 17 — Section 1202 exclusion (positive)",
     "data_type": "decimal", "default_value": "0", "sort_order": 9},
    {"fact_key": "f172_l19_mfs", "label": "Married filing separately (line 19 uses $1,500)",
     "data_type": "boolean", "default_value": "false", "sort_order": 10,
     "notes": "Derived from the return's filing status; printed on the face at line 19."},
    {"fact_key": "f172_l23_prior_nol_deduction", "label": "Line 23 — NOL deduction for losses from OTHER years (positive)",
     "data_type": "decimal", "default_value": "0", "sort_order": 11,
     "notes": ("The current year's own NOL cannot include prior years' NOL deductions — they add "
               "back here. The app derives it from the Schedule 1 line 8a figure it computed.")},

    # ── Part I computed lines ──
    {"fact_key": "f172_l4_nonbus_cap_loss_excess", "label": "Line 4 — MAX(0, l2 − l3)", "data_type": "decimal", "sort_order": 20},
    {"fact_key": "f172_l5_nonbus_cap_gain_excess", "label": "Line 5 — MAX(0, l3 − l2)", "data_type": "decimal", "sort_order": 21},
    {"fact_key": "f172_l8_nonbus_income_total", "label": "Line 8 — l5 + l7", "data_type": "decimal", "sort_order": 22},
    {"fact_key": "f172_l9_nonbus_ded_excess", "label": "Line 9 — MAX(0, l6 − l8) (add-back)", "data_type": "decimal", "sort_order": 23},
    {"fact_key": "f172_l10_gain_spill", "label": "Line 10 — MIN(MAX(0, l8 − l6), l5)", "data_type": "decimal", "sort_order": 24},
    {"fact_key": "f172_l13_bus_gain_total", "label": "Line 13 — l10 + l12", "data_type": "decimal", "sort_order": 25},
    {"fact_key": "f172_l14_bus_cap_loss_excess", "label": "Line 14 — MAX(0, l11 − l13)", "data_type": "decimal", "sort_order": 26},
    {"fact_key": "f172_l15_cap_loss_total", "label": "Line 15 — l4 + l14", "data_type": "decimal", "sort_order": 27},
    {"fact_key": "f172_l18_loss_after_1202", "label": "Line 18 — MAX(0, l16 − l17)", "data_type": "decimal", "sort_order": 28},
    {"fact_key": "f172_l19_allowed_cap_loss", "label": "Line 19 — MIN(l16, 3000|1500 MFS) when l16 is a loss", "data_type": "decimal", "sort_order": 29},
    {"fact_key": "f172_l20_excess_over_allowed", "label": "Line 20 — MAX(0, l18 − l19)", "data_type": "decimal", "sort_order": 30},
    {"fact_key": "f172_l21_allowed_over_excess", "label": "Line 21 — MAX(0, l19 − l18)", "data_type": "decimal", "sort_order": 31},
    {"fact_key": "f172_l22_net_capital_addback", "label": "Line 22 — MAX(0, l15 − l20)", "data_type": "decimal", "sort_order": 32},
    {"fact_key": "f172_l24_nol_determination", "label": "Line 24 — combine 1, 9, 17, 21-23; < 0 → the NOL",
     "data_type": "decimal", "sort_order": 33,
     "notes": "Negative → its absolute value opens a new NOL vintage pool for THIS loss year."},

    # ── The deduction side (carryforward-year inputs/outputs) ──
    {"fact_key": "f172_vintage_year", "label": "NOL vintage — the loss year the pool arose in",
     "data_type": "integer", "sort_order": 40,
     "notes": ("The app's CarryforwardAttribute pools already store this (s235). vintage_year < "
               "2018 → the uncapped 20-year class; ≥ 2018 → the indefinite 80%-capped class "
               "(§172(a)(2), (b)(1)(A)(ii)).")},
    {"fact_key": "f172_vintage_opening", "label": "NOL vintage — remaining amount carried to this year",
     "data_type": "decimal", "sort_order": 41},
    {"fact_key": "f172_ti_without_nol_qbi_250", "label": "Taxable income computed WITHOUT §172, §199A, §250 deductions",
     "data_type": "decimal", "sort_order": 42,
     "notes": ("The 80% base's first term — §172(a)(2)(B)(ii)(I) verbatim. The app computes it as a "
               "counterfactual of its own return (recompute without the NOL deduction and without "
               "the QBI deduction; §250 is a corporate deduction — structurally zero on a 1040 but "
               "stated for fidelity).")},
    {"fact_key": "f172_pre2018_component", "label": "Deduction component — pre-2018 vintages (uncapped)",
     "data_type": "decimal", "sort_order": 43},
    {"fact_key": "f172_post2017_component", "label": "Deduction component — post-2017 vintages (80%-capped)",
     "data_type": "decimal", "sort_order": 44},
    {"fact_key": "f172_post2017_cap", "label": "The 80% cap — 0.80 × MAX(0, base − pre-2018 component)",
     "data_type": "decimal", "sort_order": 45},
    {"fact_key": "f172_nol_deduction", "label": "The NOL deduction — printed as a NEGATIVE on Schedule 1 line 8a",
     "data_type": "decimal", "sort_order": 46},
    {"fact_key": "f172_modified_taxable_income", "label": "Modified taxable income (absorption base; floored at 0)",
     "data_type": "decimal", "sort_order": 47,
     "notes": ("i172 'How to Figure an NOL Carryover' items 1-4: TI without the NOL being figured "
               "or later NOLs; no capital-losses-in-excess-of-gains deduction; §1202 added back; no "
               "exemptions; AGI-derived items refigured (the counterfactual compute). Cannot be "
               "less than zero.")},
    {"fact_key": "f172_vintage_used", "label": "NOL vintage — amount absorbed this year (oldest first)",
     "data_type": "decimal", "sort_order": 48},
    {"fact_key": "f172_vintage_remaining", "label": "NOL vintage — carryover to the next year",
     "data_type": "decimal", "sort_order": 49},

    # ── Refusal / hold facts ──
    {"fact_key": "f172_farming_carryback_claimed", "label": "A farming-loss 2-year carryback is claimed",
     "data_type": "boolean", "default_value": "false", "sort_order": 60,
     "notes": "Preparer-asserted; triggers the named refusal (Ken ruling #2)."},
    {"fact_key": "f172_ebl_from_461", "label": "Form 461 excess business loss (treated as next year's NOL carryover)",
     "data_type": "decimal", "default_value": "0", "sort_order": 61,
     "notes": ("§461(l): the disallowed excess business loss is an NOL carryover to the FOLLOWING "
               "year — the i172 worksheet adds it to the Part I NOL. The app already stores the "
               "return-level Form 461 aggregates (f461_agg_business_income/deductions).")},
]


# ═══════════════════════════════════════════════════════════════════════════
# RULES
# ═══════════════════════════════════════════════════════════════════════════

RULES: list[dict] = [
    {"rule_id": "R-172-SCOPE", "title": "Scope — 1040 individuals; both sides (generation + deduction); no carrybacks",
     "rule_type": "routing", "precedence": 1, "sort_order": 1,
     "formula": ("Engage the DEDUCTION side whenever nol_regular CarryforwardAttribute pools carry a "
                 "nonzero remaining amount into the year. Engage the GENERATION side (Part I) when "
                 "the computed return's line 1 base is negative OR the preparer opens a Form 172 for "
                 "the loss year. Estates/trusts REFUSE (D_172_ESTATE_TRUST). Carrybacks of every "
                 "kind REFUSE (R-172-FARM-CB). AMT NOL pools are preserve-only (D_172_ATNOLD_HOLD)."),
     "inputs": ["f172_vintage_opening", "f172_l1_income_base"], "outputs": [],
     "description": ("Ken's s253 rulings #1-#3. Both sides in one spec because the generation "
                     "side's line 24 OPENS the vintage pool the deduction side consumes — one "
                     "lifecycle, one form.")},

    {"rule_id": "R-172-P1-BASE", "title": "Part I line 1 — the income base (individuals)",
     "rule_type": "calculation", "precedence": 10, "sort_order": 10,
     "formula": ("l1 = AGI − (standard deduction or itemized deductions) — the face's own words. "
                 "Typically negative in a loss year. The app derives it from its computed 1040 "
                 "(line 11 − line 12); a preparer override rides the normal override lane. "
                 "Estates/trusts (taxable income increased by charitable deduction, income "
                 "distribution deduction, exemption) are OUT OF SCOPE v1."),
     "inputs": [], "outputs": ["f172_l1_income_base"],
     "description": "Form 172 line 1 verbatim."},

    {"rule_id": "R-172-P1-NONBUS", "title": "Part I lines 2-10 — the nonbusiness netting",
     "rule_type": "calculation", "precedence": 11, "sort_order": 11,
     "formula": ("l4 = MAX(0, l2 − l3); l5 = MAX(0, l3 − l2); l8 = l5 + l7; l9 = MAX(0, l6 − l8); "
                 "l10 = MIN(MAX(0, l8 − l6), l5). Line 9 is the ADD-BACK of nonbusiness deductions "
                 "in excess of nonbusiness income; line 10 spills leftover nonbusiness capital "
                 "gains toward the business side, capped at line 5 (the face's 'But don't enter "
                 "more than line 5')."),
     "inputs": ["f172_l2_nonbus_cap_losses", "f172_l3_nonbus_cap_gains",
                "f172_l6_nonbus_deductions", "f172_l7_nonbus_income"],
     "outputs": ["f172_l4_nonbus_cap_loss_excess", "f172_l5_nonbus_cap_gain_excess",
                 "f172_l8_nonbus_income_total", "f172_l9_nonbus_ded_excess", "f172_l10_gain_spill"],
     "description": ("The classification of deductions/income as business vs nonbusiness follows "
                     "i172's line-6/line-7 lists (in the fact notes). The app PREFILLS from its own "
                     "return (standard deduction → l6; interest/dividends/pensions/SS → l7; wages/"
                     "SE/unemployment/rentals stay business) and the preparer confirms — "
                     "classification is judgment, never silently owned.")},

    {"rule_id": "R-172-P1-BUS", "title": "Part I lines 11-15 — the business capital netting",
     "rule_type": "calculation", "precedence": 12, "sort_order": 12,
     "formula": "l13 = l10 + l12; l14 = MAX(0, l11 − l13); l15 = l4 + l14.",
     "inputs": ["f172_l11_bus_cap_losses", "f172_l12_bus_cap_gains", "f172_l10_gain_spill",
                "f172_l4_nonbus_cap_loss_excess"],
     "outputs": ["f172_l13_bus_gain_total", "f172_l14_bus_cap_loss_excess", "f172_l15_cap_loss_total"],
     "description": ("Business capital losses deduct only against business capital gains plus the "
                     "line-10 spill (i172 'Lines 19-22—Capital Loss Limitation', restated at the "
                     "line level by the face itself).")},

    {"rule_id": "R-172-P1-CAPLIM", "title": "Part I lines 16-22 — the Schedule D / §1202 / $3,000 reconciliation",
     "rule_type": "calculation", "precedence": 13, "sort_order": 13,
     "formula": ("SKIP RULE (face line 16): if l16 == 0 AND l17 == 0 → lines 16-21 skip and "
                 "l22 = l15. Otherwise: l18 = MAX(0, l16 − l17); l19 = MIN(l16, 3000 or 1500 MFS) "
                 "when l16 > 0 else 0; l20 = MAX(0, l18 − l19); l21 = MAX(0, l19 − l18); "
                 "l22 = MAX(0, l15 − l20). The $3,000/$1,500 constants are §1211(b), printed on "
                 "the face — NON-indexed."),
     "inputs": ["f172_l16_schd_combined_loss", "f172_l17_sec1202_exclusion", "f172_l19_mfs",
                "f172_l15_cap_loss_total"],
     "outputs": ["f172_l18_loss_after_1202", "f172_l19_allowed_cap_loss",
                 "f172_l20_excess_over_allowed", "f172_l21_allowed_over_excess",
                 "f172_l22_net_capital_addback"],
     "description": "Face lines 16-22 verbatim, including the skip rule."},

    {"rule_id": "R-172-P1-NOL", "title": "Part I lines 23-24 — the NOL determination",
     "rule_type": "calculation", "precedence": 14, "sort_order": 14,
     "formula": ("l24 = l1 + l9 + l17 + l21 + l22 + l23 (the face: 'Combine lines 1, 9, 17, and 21 "
                 "through 23'). l24 < 0 → the NOL is |l24| and OPENS a new nol_regular vintage pool "
                 "for this loss year (plus the Form 461 EBL, if any — R-172-EBL). l24 ≥ 0 → 'you "
                 "don't have an NOL' — no pool, even when line 1 was negative (D_172_NO_NOL_INFO "
                 "explains the add-backs)."),
     "inputs": ["f172_l1_income_base", "f172_l9_nonbus_ded_excess", "f172_l17_sec1202_exclusion",
                "f172_l21_allowed_over_excess", "f172_l22_net_capital_addback",
                "f172_l23_prior_nol_deduction"],
     "outputs": ["f172_l24_nol_determination"],
     "description": "The generation-side terminal: line 24 verbatim."},

    {"rule_id": "R-172-DED-80BASE", "title": "The 80% base — §172(a)(2)(B)(ii) verbatim",
     "rule_type": "calculation", "precedence": 20, "sort_order": 20,
     "formula": ("base = MAX(0, TI_without_NOL_QBI_250 − pre2018_component). '80 percent of the "
                 "excess (if any) of (I) taxable income computed without regard to the deductions "
                 "under this section and sections 199A and 250, over (II) the amount determined "
                 "under subparagraph (A)' — the pre-2018 class EATS THE BASE FIRST; 'excess (if "
                 "any)' floors it at zero. cap = 0.80 × base, whole-dollar."),
     "inputs": ["f172_ti_without_nol_qbi_250", "f172_pre2018_component"],
     "outputs": ["f172_post2017_cap"],
     "description": ("⚠ THE CLAUSE THE SHORT FORM DROPS: the s246 brief compressed the base to '80% "
                     "of TI before NOL/QBI/250'; the statute subtracts the pre-2018 NOLs from that "
                     "base before taking 80%. Both i172 and §172(a)(2) carry it. Walked at Gate 1 "
                     "explicitly (Ken confirmed the verbatim form, ruling #4).")},

    {"rule_id": "R-172-DED-STACK", "title": "The deduction — two tiers, pre-2018 uncapped + post-2017 capped",
     "rule_type": "calculation", "precedence": 21, "sort_order": 21,
     "formula": ("pre = Σ remaining pre-2018 vintages carried to the year (NO cap — the deduction "
                 "may exceed taxable income; that is how carryovers arise). post_allowed = "
                 "MIN(Σ remaining post-2017 vintages, cap from R-172-DED-80BASE). deduction = pre + "
                 "post_allowed → printed as a NEGATIVE figure on Schedule 1 line 8a (R-172-DEST). "
                 "When the cap binds, ATTACH the 80%-limitation statement (D_172_80PCT_STATEMENT)."),
     "inputs": ["f172_vintage_year", "f172_vintage_opening", "f172_post2017_cap"],
     "outputs": ["f172_pre2018_component", "f172_post2017_component", "f172_nol_deduction"],
     "description": "§172(a)(2) verbatim (the excerpt); i172's Reminders restate it identically."},

    {"rule_id": "R-172-CARRYOVER", "title": "Absorption + carryover — oldest first against modified taxable income",
     "rule_type": "calculation", "precedence": 22, "sort_order": 22,
     "formula": ("MTI = MAX(0, taxable income refigured per i172 items 1-4: without the NOL being "
                 "figured or later NOLs; without capital losses in excess of capital gains; plus "
                 "any §1202 exclusion; without exemptions; AGI-derived items refigured — the app "
                 "runs its own return as a counterfactual). Then per vintage OLDEST FIRST: "
                 "used = MIN(remaining, class allowance remaining, MTI remaining); pre-2018 "
                 "vintages draw on an uncapped allowance, post-2017 vintages on the 80% cap. "
                 "remaining' = remaining − used → next year's opening (the pools' engine_computes "
                 "flips; D_CFWD_001 retires for NOL kinds, reconciliation takes over)."),
     "inputs": ["f172_vintage_year", "f172_vintage_opening", "f172_modified_taxable_income",
                "f172_post2017_cap"],
     "outputs": ["f172_vintage_used", "f172_vintage_remaining", "f172_modified_taxable_income"],
     "description": ("⚠ SYNTHESIS FLAG (walked at Gate 1): i172 states the MTI absorption rule and "
                     "the 80% cap separately; the per-vintage MIN() combining them follows "
                     "§172(a)(2)+(b)(2) but is this spec's synthesis, not one quoted sentence. "
                     "requires_human_review rides the i172 source for this and the worksheet "
                     "anomaly.")},

    {"rule_id": "R-172-EXPIRY", "title": "Pre-2018 vintages expire after 20 carryover years",
     "rule_type": "conditional", "precedence": 23, "sort_order": 23,
     "formula": ("A pre-2018 vintage may be carried to 'each of the 20 taxable years following the "
                 "taxable year of the loss' (§172(b)(1)(A)(ii)(I)). current_year − vintage_year > "
                 "20 → the vintage is EXPIRED: it contributes nothing to the deduction and its "
                 "remaining balance closes (D_172_PRE2018_EXPIRED error if still carried; "
                 "D_172_PRE2018_EXPIRING warning in the final year). Post-2017 vintages carry "
                 "forward indefinitely."),
     "inputs": ["f172_vintage_year"], "outputs": [],
     "description": "The 20-year fence the pools have carried untested since s235."},

    {"rule_id": "R-172-FARM-CB", "title": "Farming carryback — REFUSED BY NAME (v1)",
     "rule_type": "routing", "precedence": 30, "sort_order": 30,
     "formula": ("f172_farming_carryback_claimed == true → REFUSE the NOL computation for that "
                 "vintage with the named workflow: the 2-year farming carryback runs through Form "
                 "1045 (within 1 year of the NOL year end) or a per-year Form 1040-X (3-year "
                 "window), attaching Form 172 — a PAPER workflow this app does not compute. The "
                 "waiver election (§172(b)(3); statement attached to the timely original return, "
                 "generally irrevocable) converts the loss to an ordinary carryforward this spec "
                 "handles fully. §965-year interaction (the form may not be used) is recorded and "
                 "moot under the refusal."),
     "inputs": ["f172_farming_carryback_claimed"], "outputs": [],
     "description": "Ken ruling #2 (s253). The s223 doctrine: refusals are the spec."},

    {"rule_id": "R-172-EBL", "title": "Form 461 excess business loss feeds the NOL carryover",
     "rule_type": "calculation", "precedence": 31, "sort_order": 31,
     "formula": ("NOL carryover to next year = |Part I line 24 (if < 0)| + Form 461 excess business "
                 "loss (the i172 worksheet: line 1 the NOL as negative, line 3 the EBL as negative, "
                 "line 4 the combined carryover; carryback-used portion is structurally 0 under the "
                 "no-carryback rule). The EBL joins the SAME loss-year vintage (it 'will be treated "
                 "as an NOL carryover to the next tax year')."),
     "inputs": ["f172_l24_nol_determination", "f172_ebl_from_461"],
     "outputs": [],
     "description": ("The IRS's own worked example is scenario 172-T9. ⚠ The worksheet's 'line 33' "
                     "citation anomaly is flagged on the i172 source — the arithmetic follows the "
                     "example, the citation is not silently corrected.")},

    {"rule_id": "R-172-MARITAL", "title": "Marital / filing-status changes across NOL years — HELD, not computed",
     "rule_type": "conditional", "precedence": 32, "sort_order": 32,
     "formula": ("When the filing status or spouse differs between the loss year and the deduction "
                 "year, the i172 split rules govern (only the loss spouse's NOL deducts; joint-year "
                 "NOLs split by the ratio of separate NOLs — i172 Examples 1-2: $5,000 joint × "
                 "1,800/4,800 = $1,875). v1 does NOT compute the split: D_172_MARITAL_SPLIT holds "
                 "the return with the rules stated; the preparer keys the split pools."),
     "inputs": [], "outputs": [],
     "description": "A declared hold, never a silent wrong split."},

    {"rule_id": "R-172-ATNOLD", "title": "AMT NOL (ATNOLD) — preserve-only (Ken ruling #3)",
     "rule_type": "routing", "precedence": 33, "sort_order": 33,
     "formula": ("nol_amt vintage pools roll and print exactly as today; NO ATNOLD computation (the "
                 "90%-of-AMTI limitation and the Form 6251 line-2f interaction are future authored "
                 "rules). The 6251 amt_nol aggregate stays preparer-keyed. D_172_ATNOLD_HOLD states "
                 "it whenever nol_amt pools are present."),
     "inputs": [], "outputs": [],
     "description": "Ken ruling #3 (s253)."},

    {"rule_id": "R-172-DEST", "title": "Destination — a NEGATIVE figure on Schedule 1 line 8a; one Form 172 per NOL",
     "rule_type": "routing", "precedence": 40, "sort_order": 40,
     "formula": ("The deduction from R-172-DED-STACK prints as a NEGATIVE on Schedule 1 line 8a "
                 "('list your NOL deduction as a negative figure on Schedule 1 (Form 1040)'), "
                 "flowing 8a → Schedule 1 line 9/10 → 1040 line 8 → AGI. Line 8a becomes DERIVED "
                 "(its first deriving writer — the app's 8v/8h single-writer shape; a keyed 8a "
                 "becomes a reconciliation target, the 1099-Q doctrine). Attach a Form 172 per NOL; "
                 "keep records 3 years past the carryover's use or expiry. A zero deduction writes "
                 "NOTHING (never a '-0')."),
     "inputs": ["f172_nol_deduction"], "outputs": [],
     "description": "i172 'Deducting a Carryforward' verbatim (the excerpt)."},
]


RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R-172-SCOPE", "IRS_2024_F172_FORM", "primary", "The form's own population: individuals, estates, trusts (E&T refused v1)"),
    ("R-172-SCOPE", "IRC_172", "secondary", "§172(a) allows the deduction; (b) fixes carryover periods"),
    ("R-172-P1-BASE", "IRS_2024_F172_FORM", "primary", "Line 1 verbatim (AGI − deductions; E&T variant)"),
    ("R-172-P1-NONBUS", "IRS_2024_F172_FORM", "primary", "Lines 2-10 arithmetic printed on the face"),
    ("R-172-P1-NONBUS", "IRS_2024_F172_INSTR", "secondary", "The line-6/line-7 business-vs-nonbusiness lists"),
    ("R-172-P1-BUS", "IRS_2024_F172_FORM", "primary", "Lines 11-15 arithmetic printed on the face"),
    ("R-172-P1-BUS", "IRS_2024_F172_INSTR", "secondary", "'Lines 19-22—Capital Loss Limitation' restates the business-loss cap"),
    ("R-172-P1-CAPLIM", "IRS_2024_F172_FORM", "primary", "Lines 16-22 incl. the skip rule and the printed $3,000/$1,500"),
    ("R-172-P1-NOL", "IRS_2024_F172_FORM", "primary", "Line 24: 'Combine lines 1, 9, 17, and 21 through 23'"),
    ("R-172-P1-NOL", "IRS_2024_F172_INSTR", "secondary", "'How To Figure an NOL' — the disallowed-items list the add-backs implement"),
    ("R-172-DED-80BASE", "IRC_172", "primary", "§172(a)(2)(B)(ii) verbatim — the excess over the pre-2018 amount"),
    ("R-172-DED-80BASE", "IRS_2024_F172_INSTR", "primary", "The Reminders' identical statement"),
    ("R-172-DED-STACK", "IRC_172", "primary", "§172(a)(2) — the two-tier sum"),
    ("R-172-DED-STACK", "IRS_2024_F172_INSTR", "secondary", "The 80% caution + the attach-a-statement duty"),
    ("R-172-CARRYOVER", "IRS_2024_F172_INSTR", "primary", "'How to Figure an NOL Carryover' — MTI + oldest-first, verbatim excerpt"),
    ("R-172-CARRYOVER", "IRC_172", "secondary", "§172(b)(2) — the statutory absorption ordering"),
    ("R-172-EXPIRY", "IRC_172", "primary", "§172(b)(1)(A)(ii)(I) — 20 taxable years for pre-2018 losses"),
    ("R-172-FARM-CB", "IRS_2024_F172_INSTR", "primary", "The farming exception, Form 1045/1040-X windows, the waiver election"),
    ("R-172-FARM-CB", "IRC_172", "secondary", "§172(b)(1)(B) farming carryback; (b)(3) the waiver"),
    ("R-172-EBL", "IRS_2024_F172_INSTR", "primary", "The EBL worksheet + the IRS's own example (excerpted)"),
    ("R-172-MARITAL", "IRS_2024_F172_INSTR", "primary", "Change in Marital/Filing Status — the split rules + Examples 1-2"),
    ("R-172-ATNOLD", "IRC_172", "secondary", "The regular-tax §172 rules this spec covers; ATNOLD (§56(a)(4)/(d)) deliberately unspecced"),
    ("R-172-DEST", "IRS_2024_F172_INSTR", "primary", "'Deducting a Carryforward' — the negative Schedule 1 figure, verbatim"),
    ("R-172-DEST", "IRS_2025_SCH1_FORM", "secondary", "Line 8a 'Net operating loss' on the seeded face"),
]


# ═══════════════════════════════════════════════════════════════════════════
# LINES — Part I verbatim; Part II transcription-only (prefix II-)
# ═══════════════════════════════════════════════════════════════════════════

LINES: list[dict] = [
    {"line_number": "1", "description": "AGI minus standard/itemized deductions (individuals); E&T variant refused v1", "line_type": "calculated"},
    {"line_number": "2", "description": "Nonbusiness capital losses before limitation (positive)", "line_type": "input"},
    {"line_number": "3", "description": "Nonbusiness capital gains (without regard to §1202)", "line_type": "input"},
    {"line_number": "4", "description": "If line 2 > line 3, the difference; else -0-", "line_type": "calculated"},
    {"line_number": "5", "description": "If line 3 > line 2, the difference; else -0-", "line_type": "calculated"},
    {"line_number": "6", "description": "Nonbusiness deductions (positive)", "line_type": "input"},
    {"line_number": "7", "description": "Nonbusiness income other than capital gains", "line_type": "input"},
    {"line_number": "8", "description": "Add lines 5 and 7", "line_type": "subtotal"},
    {"line_number": "9", "description": "If line 6 > line 8, the difference; else -0-", "line_type": "calculated"},
    {"line_number": "10", "description": "If line 8 > line 6, the difference; but not more than line 5", "line_type": "calculated"},
    {"line_number": "11", "description": "Business capital losses before limitation (positive)", "line_type": "input"},
    {"line_number": "12", "description": "Business capital gains (without regard to §1202)", "line_type": "input"},
    {"line_number": "13", "description": "Add lines 10 and 12", "line_type": "subtotal"},
    {"line_number": "14", "description": "Line 11 minus line 13; if zero or less, -0-", "line_type": "calculated"},
    {"line_number": "15", "description": "Add lines 4 and 14", "line_type": "subtotal"},
    {"line_number": "16", "description": "Combined net ST+LT capital loss from Schedule D (positive; skip 16-21 if none and no §1202)", "line_type": "input"},
    {"line_number": "17", "description": "Section 1202 exclusion (positive)", "line_type": "input"},
    {"line_number": "18", "description": "Line 16 minus line 17; if zero or less, -0-", "line_type": "calculated"},
    {"line_number": "19", "description": "Smaller of the line-16 loss or $3,000 ($1,500 MFS)", "line_type": "calculated"},
    {"line_number": "20", "description": "If line 18 > line 19, the difference; else -0-", "line_type": "calculated"},
    {"line_number": "21", "description": "If line 19 > line 18, the difference; else -0-", "line_type": "calculated"},
    {"line_number": "22", "description": "Line 15 minus line 20; if zero or less, -0-", "line_type": "calculated"},
    {"line_number": "23", "description": "NOL deduction for losses from other years (positive)", "line_type": "input"},
    {"line_number": "24", "description": "NOL: combine lines 1, 9, 17, and 21-23; less than zero → the NOL", "line_type": "calculated"},
    # Part II — the carryback absorption schedule. TRANSCRIPTION-ONLY in v1
    # (Ken ruling #2 refuses carryback computation); the lines exist so a
    # filed Form 172's Part II can be carried/printed without inventing them.
    {"line_number": "II-1", "description": "Part II — NOL deduction (positive) [transcription-only v1]", "line_type": "input"},
    {"line_number": "II-2", "description": "Part II — Taxable income before the current-year NOL carryback [transcription-only v1]", "line_type": "input"},
    {"line_number": "II-3", "description": "Part II — Net capital loss deduction [transcription-only v1]", "line_type": "input"},
    {"line_number": "II-4", "description": "Part II — §1202 exclusion [transcription-only v1]", "line_type": "input"},
    {"line_number": "II-5", "description": "Part II — QBI deduction [transcription-only v1]", "line_type": "input"},
    {"line_number": "II-6", "description": "Part II — Adjustment to AGI [transcription-only v1]", "line_type": "input"},
    {"line_number": "II-7", "description": "Part II — Adjustment to itemized deductions (from line II-33) [transcription-only v1]", "line_type": "input"},
    {"line_number": "II-8", "description": "Part II — Estates and trusts exemption amount [transcription-only v1; E&T refused]", "line_type": "input"},
    {"line_number": "II-9", "description": "Part II — Modified taxable income: add lines 2-8; if zero or less, -0- [transcription-only v1]", "line_type": "input"},
    {"line_number": "II-10", "description": "Part II — NOL carryover to the subsequent year (line 1 minus line 9) [transcription-only v1]", "line_type": "input"},
    {"line_number": "II-11-33", "description": "Part II — Adjustment to Itemized Deductions block, lines 11-33 (medical 7.5%, mortgage insurance, charitable, casualty 10%) [transcription-only v1, carried as a unit]", "line_type": "input"},
]


# ═══════════════════════════════════════════════════════════════════════════
# DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════════════════

DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_172_FARM_CARRYBACK", "title": "Farming-loss carryback claimed — not computed here", "severity": "error",
     "condition": "f172_farming_carryback_claimed == true",
     "message": ("A 2-year farming-loss carryback has been claimed. This application does not "
                 "compute carrybacks: the carryback runs through Form 1045 (filed within 1 year "
                 "after the NOL year ends) or a separate Form 1040-X for each carryback year "
                 "(3-year window), attaching Form 172. Alternatively, the carryback may be WAIVED "
                 "by attaching the §172(b) election statement to the timely-filed original return "
                 "(generally irrevocable) — a waived loss carries forward and is computed here in "
                 "full."),
     "notes": "R-172-FARM-CB; Ken ruling #2 (s253). The refusal names the paper workflow — s223."},

    {"diagnostic_id": "D_172_80PCT_STATEMENT", "title": "The 80% limitation applied — attach the computation statement", "severity": "warning",
     "condition": "post2017 pools present AND post2017_component < Σ post2017 remaining (the cap binds)",
     "message": ("Part or all of the post-2017 NOL carryforward was limited to 80% of taxable "
                 "income (computed without the NOL, QBI, or §250 deductions, less pre-2018 NOLs). "
                 "The IRS requires a statement attached to the return showing how the 80% "
                 "limitation was figured. The application prints the limitation worksheet as a "
                 "statement page."),
     "notes": "i172's caution verbatim: 'Attach a statement to your tax return showing how you figured the 80% limitation, if applicable.'"},

    {"diagnostic_id": "D_172_PRE2018_EXPIRING", "title": "A pre-2018 NOL vintage is in its final carryover year", "severity": "warning",
     "condition": "vintage_year < 2018 AND current_year − vintage_year == 20 AND remaining > 0",
     "message": ("A net operating loss that arose before 2018 is in its 20th and final carryover "
                 "year. Any amount not absorbed this year EXPIRES — it cannot be carried to next "
                 "year (§172(b)(1)(A)(ii)(I))."),
     "notes": "R-172-EXPIRY."},

    {"diagnostic_id": "D_172_PRE2018_EXPIRED", "title": "A pre-2018 NOL vintage is past its 20-year carryover period", "severity": "error",
     "condition": "vintage_year < 2018 AND current_year − vintage_year > 20 AND remaining > 0",
     "message": ("A net operating loss vintage from before 2018 is being carried beyond its 20-year "
                 "limit. The vintage contributes nothing to this year's deduction; its remaining "
                 "balance should be closed. Verify the vintage year — if the loss actually arose "
                 "after 2017, it carries indefinitely instead."),
     "notes": "R-172-EXPIRY. The pools have carried this fence untested since s235."},

    {"diagnostic_id": "D_172_MARITAL_SPLIT", "title": "Marital/filing-status change across NOL years — split not computed", "severity": "error",
     "condition": "an NOL pool's loss-year filing facts differ from the deduction year's (preparer-asserted)",
     "message": ("The filing status or spouse changed between the loss year and this year. Only the "
                 "spouse who had the loss may take the NOL deduction; a joint-year NOL must be "
                 "split by the ratio of the spouses' separate NOLs (Form 172 instructions, Change "
                 "in Marital Status / Change in Filing Status). This application does not compute "
                 "the split — figure each spouse's share per the instructions' examples and key the "
                 "split pools."),
     "notes": "R-172-MARITAL; i172 Examples 1-2 ($5,000 × 1,800/4,800 = $1,875)."},

    {"diagnostic_id": "D_172_ATNOLD_HOLD", "title": "AMT NOL pools present — ATNOLD not computed (preserve-only)", "severity": "warning",
     "condition": "nol_amt vintage pools carry a nonzero remaining amount",
     "message": ("AMT net operating loss amounts are being carried on this return. The alternative "
                 "tax NOL deduction (ATNOLD, with its 90%-of-AMTI limitation) is not computed by "
                 "this application — the pools roll forward and print, and any Form 6251 NOL "
                 "adjustment remains the preparer's keyed entry. Verify the AMT NOL by hand if Form "
                 "6251 applies."),
     "notes": "Ken ruling #3 (s253); R-172-ATNOLD."},

    {"diagnostic_id": "D_172_EBL_FEED", "title": "Form 461 excess business loss becomes next year's NOL carryover", "severity": "warning",
     "condition": "f172_ebl_from_461 > 0",
     "message": ("The Form 461 excess business loss disallowed this year is treated as a net "
                 "operating loss carryover to NEXT year. The application adds it to the loss-year "
                 "NOL vintage per the instructions' worksheet; verify the Form 461 amount — the "
                 "combined carryover appears on the NOL worksheet statement."),
     "notes": "R-172-EBL; the i172 worksheet + its example (172-T9)."},

    {"diagnostic_id": "D_172_NO_NOL_INFO", "title": "Negative taxable income but NO NOL — the add-backs consumed it", "severity": "info",
     "condition": "l1 < 0 AND l24 >= 0",
     "message": ("This year's income minus deductions is negative, but the Form 172 computation "
                 "yields NO net operating loss: nonbusiness deductions in excess of nonbusiness "
                 "income, capital-loss limitations, any §1202 exclusion, and prior-year NOL "
                 "deductions are added back (they cannot generate or enlarge an NOL). Nothing "
                 "carries forward from this year."),
     "notes": "R-172-P1-NOL — the answer to 'why is there no NOL when the return shows a loss?'"},

    {"diagnostic_id": "D_172_ESTATE_TRUST", "title": "Estate/trust NOL — out of scope v1", "severity": "error",
     "condition": "the return is a Form 1041 estate/trust with NOL pools or a loss year",
     "message": ("Form 172 for estates and trusts uses a different line-1 base (taxable income "
                 "increased by the charitable deduction, income distribution deduction, and "
                 "exemption) and a Form 1041 destination. This application computes individual "
                 "(Form 1040) NOLs only; prepare the estate/trust NOL by hand."),
     "notes": "R-172-SCOPE. The app is a 1040/1120-S/1065 shop; 1041 is not built."},

    {"diagnostic_id": "D_172_GEN_CLASSIFY", "title": "Verify the business/nonbusiness classification on Part I", "severity": "info",
     "condition": "Part I engaged with prefilled lines 2/3/6/7/11/12",
     "message": ("Form 172 Part I lines 2-12 were prefilled from this return's own items using the "
                 "instructions' business/nonbusiness lists (standard deduction and IRA deductions "
                 "are nonbusiness; wages, self-employment income, unemployment compensation, and "
                 "rental income are business). The classification drives the NOL amount — review "
                 "the split before filing."),
     "notes": "R-172-P1-NONBUS: prefill, never silently own the judgment."},
]


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIOS — hand-computed against the reference implementations above;
# 172-T9 transcribes the IRS's own EBL example.
# ═══════════════════════════════════════════════════════════════════════════

SCENARIOS: list[dict] = [
    {"scenario_name": "172-T1 — textbook sole-proprietor loss year (no capital items)", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"l1_income_base": -57250, "l6_nonbus_deductions": 15750, "l7_nonbus_income": 500},
     "expected_outputs": {"f172_l9_nonbus_ded_excess": 15250, "f172_l24_nol_determination": -42000,
                          "nol_vintage_opened": 42000},
     "notes": ("Wages 8,000 + interest 500 − business loss 50,000 → AGI −41,500; standard deduction "
               "15,750 → line 1 = −57,250. Nonbusiness: std ded 15,750 vs interest 500 → line 9 "
               "add-back 15,250. Line 24 = −57,250 + 15,250 = −42,000 — exactly the business-side "
               "loss net of business income (−50,000 + 8,000), the intuition check.")},

    {"scenario_name": "172-T2 — nonbusiness and business capital netting (lines 2-15) + the $3,000 block + a line-23 add-back", "scenario_type": "normal", "sort_order": 2,
     "inputs": {"l1_income_base": -30000, "l2_nonbus_cap_losses": 1000, "l3_nonbus_cap_gains": 3000,
                "l6_nonbus_deductions": 16000, "l7_nonbus_income": 1500,
                "l11_bus_cap_losses": 4000, "l12_bus_cap_gains": 1000,
                "l16_schd_combined_loss": 1000, "l23_prior_nol_deduction": 500},
     "expected_outputs": {"f172_l4_nonbus_cap_loss_excess": 0, "f172_l5_nonbus_cap_gain_excess": 2000,
                          "f172_l8_nonbus_income_total": 3500, "f172_l9_nonbus_ded_excess": 12500,
                          "f172_l10_gain_spill": 0, "f172_l13_bus_gain_total": 1000,
                          "f172_l14_bus_cap_loss_excess": 3000, "f172_l15_cap_loss_total": 3000,
                          "f172_l18_loss_after_1202": 1000, "f172_l19_allowed_cap_loss": 1000,
                          "f172_l20_excess_over_allowed": 0, "f172_l21_allowed_over_excess": 0,
                          "f172_l22_net_capital_addback": 3000, "f172_l24_nol_determination": -14000},
     "notes": ("Schedule D ties: nonbusiness −1,000+3,000 = +2,000; business −4,000+1,000 = −3,000; "
               "combined −1,000 → line 16 = 1,000. Line 8 (3,500) < line 6 (16,000) → line 10 = 0. "
               "A 500 prior-year NOL deduction adds back on line 23 (a current NOL can never include "
               "other years' NOLs). Line 24 = −30,000 + 12,500 + 3,000 + 500 = −14,000.")},

    {"scenario_name": "172-T3 — the line-10 spill and a §1202 exclusion engage lines 16-21 without a Schedule D loss", "scenario_type": "normal", "sort_order": 3,
     "inputs": {"l1_income_base": -20000, "l2_nonbus_cap_losses": 500, "l3_nonbus_cap_gains": 5000,
                "l6_nonbus_deductions": 2000, "l7_nonbus_income": 1000,
                "l11_bus_cap_losses": 6000, "l12_bus_cap_gains": 2000,
                "l16_schd_combined_loss": 0, "l17_sec1202_exclusion": 800},
     "expected_outputs": {"f172_l5_nonbus_cap_gain_excess": 4500, "f172_l8_nonbus_income_total": 5500,
                          "f172_l9_nonbus_ded_excess": 0, "f172_l10_gain_spill": 3500,
                          "f172_l13_bus_gain_total": 5500, "f172_l14_bus_cap_loss_excess": 500,
                          "f172_l15_cap_loss_total": 500, "f172_l18_loss_after_1202": 0,
                          "f172_l19_allowed_cap_loss": 0, "f172_l20_excess_over_allowed": 0,
                          "f172_l21_allowed_over_excess": 0, "f172_l22_net_capital_addback": 500,
                          "f172_l24_nol_determination": -18700},
     "notes": ("The §1202 exclusion alone defeats the skip rule (face line 16). Line 10 caps at "
               "line 5? No — here MAX(0, 5,500−2,000) = 3,500 < line 5 (4,500), so the spill is "
               "3,500. Line 24 = −20,000 + 0 + 800 + 0 + 500 = −18,700.")},

    {"scenario_name": "172-T4 — negative taxable income but NO NOL (the add-backs consume it)", "scenario_type": "edge", "sort_order": 4,
     "inputs": {"l1_income_base": -3000, "l6_nonbus_deductions": 15750, "l7_nonbus_income": 12000},
     "expected_outputs": {"f172_l9_nonbus_ded_excess": 3750, "f172_l24_nol_determination": 750,
                          "nol_vintage_opened": 0},
     "notes": ("Line 24 = −3,000 + 3,750 = +750 ≥ 0 → 'you don't have an NOL'. D_172_NO_NOL_INFO "
               "explains it. Nothing carries.")},

    {"scenario_name": "172-T5 — pre-2018 vintage: UNCAPPED deduction exceeding taxable income; MTI absorption", "scenario_type": "normal", "sort_order": 5,
     "inputs": {"vintages": [[2016, 40000]], "ti_without_nol_qbi_250": 30000,
                "modified_taxable_income": 30000},
     "expected_outputs": {"f172_pre2018_component": 40000, "f172_post2017_component": 0,
                          "f172_nol_deduction": 40000, "sch1_8a": -40000,
                          "vintage_2016_used": 30000, "vintage_2016_remaining": 10000},
     "notes": ("§172(a)(2)(A): the pre-2018 class enters IN FULL — 40,000 deducted against 30,000 "
               "of income (taxable income goes negative; that is the design). Absorption: MTI "
               "30,000 → used 30,000, carryover 10,000 (i172 'excess of your NOL deduction over "
               "your modified taxable income').")},

    {"scenario_name": "172-T6 — post-2017 vintage: the 80% cap binds; the statement duty fires", "scenario_type": "normal", "sort_order": 6,
     "inputs": {"vintages": [[2021, 90000]], "ti_without_nol_qbi_250": 100000,
                "modified_taxable_income": 100000},
     "expected_outputs": {"f172_pre2018_component": 0, "f172_post2017_cap": 80000,
                          "f172_post2017_component": 80000, "f172_nol_deduction": 80000,
                          "sch1_8a": -80000, "vintage_2021_used": 80000,
                          "vintage_2021_remaining": 10000, "d_172_80pct_statement": "fires"},
     "notes": ("cap = 0.80 × (100,000 − 0) = 80,000 < pool 90,000 → the cap binds. The unused "
               "10,000 carries forward INDEFINITELY. D_172_80PCT_STATEMENT requires the attached "
               "computation.")},

    {"scenario_name": "172-T7 — mixed stack: pre-2018 eats the base BEFORE the 80% computes", "scenario_type": "normal", "sort_order": 7,
     "inputs": {"vintages": [[2017, 30000], [2019, 40000]], "ti_without_nol_qbi_250": 50000,
                "modified_taxable_income": 50000},
     "expected_outputs": {"f172_pre2018_component": 30000, "f172_post2017_cap": 16000,
                          "f172_post2017_component": 16000, "f172_nol_deduction": 46000,
                          "sch1_8a": -46000, "vintage_2017_used": 30000,
                          "vintage_2017_remaining": 0, "vintage_2019_used": 16000,
                          "vintage_2019_remaining": 24000},
     "notes": ("THE CLAUSE THE SHORT FORM DROPS, exercised: base = MAX(0, 50,000 − 30,000) = "
               "20,000 → cap = 16,000. A naive '80% of 50,000 = 40,000' would over-deduct the "
               "2019 vintage by 24,000. Oldest first: 2017 absorbs 30,000, then 2019 its capped "
               "16,000.")},

    {"scenario_name": "172-T8 — farming carryback claimed → REFUSED by name", "scenario_type": "edge", "sort_order": 8,
     "inputs": {"farming_carryback_claimed": True, "vintages": [[2025, 20000]]},
     "expected_outputs": {"refusal": "D_172_FARM_CARRYBACK", "computed_deduction": "none"},
     "notes": ("Ken ruling #2. The refusal names Form 1045 (1-year window) / per-year 1040-X "
               "(3-year window) and the §172(b)(3) waiver alternative. Nothing silently computed.")},

    {"scenario_name": "172-T9 — the IRS's own EBL example: $1M Schedule C loss, $738,000 excess business loss", "scenario_type": "normal", "sort_order": 9,
     "inputs": {"l24_nol": -262000, "ebl_from_461": 738000},
     "expected_outputs": {"nol_carryover_to_next_year": 1000000},
     "notes": ("i172's worked example, verbatim in the excerpt: the $738,000 EBL 'will be treated "
               "as an NOL carryover to the next tax year'; the worksheet combines it with the "
               "Part I NOL (the allowed −262,000) → 1,000,000 carries. ⚠ The worksheet's line-1 "
               "citation reads 'Form 172, line 33' — the flagged anomaly (should be line 24); the "
               "arithmetic follows the IRS's own example.")},

    {"scenario_name": "172-T10 — zero taxable-income base: post-2017 deduction is 0; the pool survives intact", "scenario_type": "edge", "sort_order": 10,
     "inputs": {"vintages": [[2022, 50000]], "ti_without_nol_qbi_250": 0,
                "modified_taxable_income": 0},
     "expected_outputs": {"f172_post2017_cap": 0, "f172_nol_deduction": 0, "sch1_8a": "no entry",
                          "vintage_2022_used": 0, "vintage_2022_remaining": 50000},
     "notes": ("cap = 0.80 × MAX(0, 0) = 0 → nothing deducts; NOTHING prints on 8a (never a "
               "'-0'); the vintage rolls untouched. The no-income year must not burn the pool.")},

    {"scenario_name": "172-T11 — MFS: line 19 caps at $1,500 and changes the NOL", "scenario_type": "normal", "sort_order": 11,
     "inputs": {"l1_income_base": -25000, "l2_nonbus_cap_losses": 2800,
                "l6_nonbus_deductions": 15000, "l16_schd_combined_loss": 2800, "mfs": True},
     "expected_outputs": {"f172_l4_nonbus_cap_loss_excess": 2800, "f172_l9_nonbus_ded_excess": 15000,
                          "f172_l15_cap_loss_total": 2800, "f172_l18_loss_after_1202": 2800,
                          "f172_l19_allowed_cap_loss": 1500, "f172_l20_excess_over_allowed": 1300,
                          "f172_l21_allowed_over_excess": 0, "f172_l22_net_capital_addback": 1500,
                          "f172_l24_nol_determination": -8500},
     "notes": ("MFS: line 19 = MIN(2,800, 1,500) = 1,500 → line 24 = −25,000 + 15,000 + 1,500 = "
               "−8,500. The single/MFJ computation on the same facts gives −7,200 (line 19 = "
               "2,800 → line 22 = 2,800) — the two MUST differ, pinning the printed $1,500.")},
]


# ═══════════════════════════════════════════════════════════════════════════
# FLOW ASSERTIONS
# ═══════════════════════════════════════════════════════════════════════════

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-1040-NOL-01", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "The NOL deduction reaches Schedule 1 line 8a as a NEGATIVE and flows to AGI",
     "description": ("Validates R-172-DEST. Exercises T5: pools 40,000 / TI base 30,000 → 8a = "
                     "−40,000 → Schedule 1 line 9/10 → 1040 line 8 → AGI drops by 40,000. Bug it "
                     "catches: a positive-sign write (which would ADD income), or a deduction that "
                     "never leaves the worksheet."),
     "status": "active"},
    {"assertion_id": "FA-1040-NOL-02", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "The 80% cap binds on post-2017 vintages — and the base subtracts pre-2018 NOLs first",
     "description": ("Validates R-172-DED-80BASE + R-172-DED-STACK. Exercises T6 (cap 80,000 binds "
                     "on a 90,000 pool) AND T7 (base = 50,000 − 30,000 pre-2018 → cap 16,000). Bug "
                     "it catches: computing 80% of the raw base (T7 would over-deduct by 24,000) — "
                     "the clause the brief's short form dropped."),
     "status": "active"},
    {"assertion_id": "FA-1040-NOL-03", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "Pre-2018 vintages deduct UNCAPPED and may exceed taxable income",
     "description": ("Validates R-172-DED-STACK's first tier. Exercises T5: a 40,000 pre-2018 pool "
                     "deducts in full against 30,000 of income. Bug it catches: applying the 80% "
                     "cap to the pre-2018 class (a plausible-looking 'simplification' that "
                     "understates the deduction)."),
     "status": "active"},
    {"assertion_id": "FA-1040-NOL-04", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "Per-vintage utilization writes back oldest-first; next year opens reduced",
     "description": ("Validates R-172-CARRYOVER. Exercises T5/T6/T7's used/remaining columns and "
                     "the proforma roll: vintage 2017 exhausts before vintage 2019 touches its "
                     "cap. Bug it catches: absorbing newest-first (burns indefinite-life post-2017 "
                     "pools while a 20-year pre-2018 pool expires), or utilization never written "
                     "back (the pools double-deduct next year)."),
     "status": "active"},
    {"assertion_id": "FA-1040-NOL-05", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "Part I line 24 < 0 opens a new vintage pool (plus any Form 461 EBL)",
     "description": ("Validates R-172-P1-NOL + R-172-EBL. Exercises T1 (line 24 = −42,000 → a "
                     "42,000 vintage for the loss year) and T9 (the IRS's EBL example: −262,000 + "
                     "738,000 EBL → 1,000,000 carries). Bug it catches: a loss year that computes "
                     "line 24 but never opens the pool — the NOL evaporates at the year boundary."),
     "status": "active"},
]


FORMS: list[dict] = [
    {
        "identity": {
            "form_number": "FORM_172",
            "form_title": "Form 172 — Net Operating Losses (NOLs) (TY2025, individuals)",
            "notes": (
                "Both sides per Ken's s253 rulings: Part I generation (lines 1-24, the face's own "
                "arithmetic) + the §172(a)(2) two-tier deduction with oldest-first MTI absorption. "
                "Carrybacks refused by name (farming → 1045/1040-X paper workflow); ATNOLD "
                "preserve-only; estates/trusts refused. Part II transcription-only. Sources: Form "
                "172 (Rev. 12-2024), i172 (the Pub-536 successor), IRC §172 verbatim "
                "(uscode.house.gov, fetched 2026-08-12)."
            ),
        },
        "facts": FACTS,
        "rules": RULES,
        "rule_links": RULE_LINKS,
        "lines": LINES,
        "diagnostics": DIAGNOSTICS,
        "scenarios": SCENARIOS,
    },
]


class Command(BaseCommand):
    help = "Load the FORM_172 spec (NOLs for individuals — generation + deduction). Gated by READY_TO_SEED."

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad FORM_172 spec (Net Operating Losses — individuals)\n"))
        self._load_topics()
        sources = self._load_sources()
        self._load_new_excerpts_on_existing(sources)
        for spec in FORMS:
            form = self._upsert_form(spec["identity"])
            self._upsert_facts(form, spec["facts"])
            rules = self._upsert_rules(form, spec["rules"])
            self._upsert_authority_links(rules, sources, spec["rule_links"])
            self._upsert_lines(form, spec["lines"])
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
                "\nREFUSING TO SEED FORM_172: not cleared to seed.\n\n"
                "Gated until Ken's Gate-1 review walk. The items to walk:\n"
                "  1. BOTH SIDES are in scope (Ken s253 ruling #1 overrode deduction-only) —\n"
                "     Part I generation opens vintage pools; the deduction consumes them.\n"
                "  2. The 80% base subtracts PRE-2018 NOLs before taking 80% — the clause the\n"
                "     s246 brief's short form dropped (§172(a)(2)(B)(ii) verbatim; scenario T7).\n"
                "  3. The absorption synthesis: per-vintage used = MIN(remaining, class\n"
                "     allowance, MTI remaining) — i172 states the pieces separately; the\n"
                "     combination is this spec's synthesis (requires_human_review).\n"
                "  4. Farming carrybacks REFUSE by name (ruling #2); Part II is\n"
                "     transcription-only; the waiver election is the stated alternative.\n"
                "  5. ATNOLD stays preserve-only (ruling #3) — D_172_ATNOLD_HOLD.\n"
                "  6. The i172 EBL worksheet's 'line 33' citation anomaly is FLAGGED, not\n"
                "     silently corrected (the arithmetic follows the IRS's own example).\n"
                "  7. Marital/filing-status splits are HELD (D_172_MARITAL_SPLIT), never\n"
                "     silently computed.\n\n"
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
            else:
                self.stdout.write(self.style.WARNING(
                    f"  expected existing source {code} not found — its rule links will be skipped"))
        self.stdout.write(f"Sources ready: {len(sources)}")
        return sources

    def _load_new_excerpts_on_existing(self, sources):
        for code, exc in NEW_EXCERPTS_ON_EXISTING:
            src = sources.get(code) or AuthoritySource.objects.filter(source_code=code).first()
            if src:
                exc = dict(exc)
                AuthorityExcerpt.objects.update_or_create(
                    authority_source=src, excerpt_label=exc["excerpt_label"], defaults=exc)
            else:
                self.stdout.write(self.style.WARNING(
                    f"  cannot attach excerpt to missing source {code}"))

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
            rule = rules.get(rule_id)
            source = sources.get(source_code)
            if rule is None or source is None:
                self.stdout.write(self.style.WARNING(
                    f"  skipping link {rule_id} -> {source_code} (missing)"))
                continue
            RuleAuthorityLink.objects.update_or_create(
                form_rule=rule, authority_source=source,
                defaults={"support_level": level, "relevance_note": note})
            ct += 1
        self.stdout.write(f"  {ct} rule-authority links")

    def _upsert_lines(self, form, lines):
        for ln in lines:
            ln = dict(ln)
            FormLine.objects.update_or_create(tax_form=form, line_number=ln.pop("line_number"), defaults=ln)
        self.stdout.write(f"  {len(lines)} lines")

    def _upsert_diagnostics(self, form, diags):
        for d in diags:
            d = dict(d)
            FormDiagnostic.objects.update_or_create(tax_form=form, diagnostic_id=d.pop("diagnostic_id"), defaults=d)
        self.stdout.write(f"  {len(diags)} diagnostics")

    def _upsert_tests(self, form, tests):
        for t in tests:
            t = dict(t)
            TestScenario.objects.update_or_create(tax_form=form, scenario_name=t.pop("scenario_name"), defaults=t)
        self.stdout.write(f"  {len(tests)} scenarios")

    def _upsert_form_links(self, sources):
        form = TaxForm.objects.filter(
            form_number="FORM_172", jurisdiction=FORM_JURISDICTION, tax_year=FORM_TAX_YEAR).first()
        if form is None:
            return
        ct = 0
        for code in ("IRC_172", "IRS_2024_F172_FORM", "IRS_2024_F172_INSTR"):
            src = sources.get(code)
            if src is None:
                continue
            AuthorityFormLink.objects.get_or_create(tax_form=form, authority_source=src)
            ct += 1
        self.stdout.write(f"  {ct} form-authority links")

    def _load_flow_assertions(self):
        for a in FLOW_ASSERTIONS:
            a = dict(a)
            FlowAssertion.objects.update_or_create(assertion_id=a.pop("assertion_id"), defaults=a)
        self.stdout.write(f"Flow assertions: {len(FLOW_ASSERTIONS)}")

    def _report_totals(self):
        self.stdout.write(self.style.SUCCESS("\nFORM_172 seed complete."))
        self.stdout.write(f"TaxForms: {TaxForm.objects.count()} | FlowAssertions: {FlowAssertion.objects.count()}")
        form = TaxForm.objects.filter(form_number="FORM_172").first()
        if form:
            self.stdout.write(
                f"FORM_172: {FormFact.objects.filter(tax_form=form).count()} facts, "
                f"{FormRule.objects.filter(tax_form=form).count()} rules, "
                f"{FormLine.objects.filter(tax_form=form).count()} lines, "
                f"{FormDiagnostic.objects.filter(tax_form=form).count()} diagnostics, "
                f"{TestScenario.objects.filter(tax_form=form).count()} scenarios")
            uncited = [r for r in FormRule.objects.filter(tax_form=form) if not r.authority_links.exists()]
            self.stdout.write("FORM_172: all rules cited" if not uncited
                              else self.style.WARNING(f"FORM_172 uncited rules: {len(uncited)}"))
