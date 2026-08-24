"""Load the Oregon Form OR-20 spec - Corporation Excise Tax Return (TY2025).

WO-W05-CCORP. Oregon's walk closed at campaign **D-25**. ⚠ This is the form that
Wave 5 was reported as having authored and had not: D-29 seeded `OR_AP` and
`OR_ASC_CORP` - Oregon's SHARED SCHEDULES - and `OR_20` itself was never written.

═══════════════════════════════════════════════════════════════════════════
⚠⚠ O1 - THE HIGHEST-DOLLAR CORRECTION OF THE WAVE. OREGON = FEDERAL FOR TY2025.
═══════════════════════════════════════════════════════════════════════════
**ORS 317.010(7), verified verbatim first-hand**, has exactly two prongs:

    (a) On December 31, 2023; or
    (b) If related to the definition of taxable income, as applicable to the tax
        year of the taxpayer.

**Bonus depreciation and § 179 are computed in arriving at taxable income, so they
ride prong (b) - the ROLLING limb - not the fixed 12/31/2023 date.** Therefore for
TY2025:

    § 168(k) bonus CONFORMS at the OBBBA 100% level.
    § 179 conforms at $2,500,000 / $4,000,000.
    THERE IS NO OREGON ADD-BACK.

⚠⚠ The research pass originally read this off prong (a) and put Oregon at
pre-OBBBA - 40% bonus and the old § 179 limits. **A builder applying that would
UNDER-DEPRECIATE a TY2025 OR-20 by up to SIXTY POINTS OF BASIS.** Corrected by
the verification pass; class (a) - right numbers, wrong method.

Four corroborations, the third structurally decisive:
 1. ORS 317.013(1) adopts the IRC "unless modified by other provisions of this
    chapter", and an exhaustive sweep of ORS 314/317/318 found NO operative
    modifier - **ORS 317.312 expressly directs that "no adjustment shall be made
    to federal depreciation expense."**
 2. HB 2092 (2025 R1) would have suspended the rolling reconnect - it DID NOT PASS.
 3. ⭐ **SB 1507 §§ 8-9 (2026) had to CREATE a bonus add-back from TY2026 - pure
    surplusage if the fixed date had already blocked OBBBA.**
 4. The already-VERIFIED holding of `conformity/or_conformity.md` §3 / §12.

**RULED (D-25 O1):** (i) ASSERT it, with a review diagnostic carrying the
reasoning so the next reader cannot "correct" it back; (ii) build the TY2025
engine SWITCH-READY for SB 1507's mandatory TY2026 shadow book; (iii) on the
record, **NO shared "bonus add-back" abstraction with Georgia. DO NOT CLONE THE
GEORGIA ADD-BACK INTO OREGON.** Georgia has one; Oregon does not.

⚠⚠ **OREGON TY2026 IS BLOCKED** pending SB 1507 re-verification - 2026 Or. Laws
ch. 142 § 41 amends ORS 317.010(7) *itself*, so the staleness tripwire fires on
the conformity rule, not merely on a rate.

═══════════════════════════════════════════════════════════════════════════
⚠⚠ THE MINIMUM TAX IS A THREE-LINE INVARIANT, AND CREDITS CANNOT TOUCH IT
═══════════════════════════════════════════════════════════════════════════
Lines **18, 20 and 22** each carry an independent "not less than minimum tax"
clamp ON THE FACE. Instructions, verbatim: *"Minimum tax can't be 'reduced, paid,
or otherwise satisfied through the use of any tax credit' (ORS 317.090)."*
A single clamp at the end is not equivalent - the ordering rule requires the
preparer to reduce how much of a credit they use, which only works if the floor
binds at each step.

⚠ The minimum tax is measured on **Oregon sales of the FILING GROUP**, and
**ONE minimum tax applies per return**, not per affiliate (OAR 150-317-0170(1)(a):
"Only one minimum tax is charged per return, regardless of the number of
corporations in the group that are doing business in Oregon.").

═══════════════════════════════════════════════════════════════════════════
⚠ DEFECT D1 - THE INSTRUCTIONS CONTRADICT THE FACE ON LINE 3
═══════════════════════════════════════════════════════════════════════════
Face: `Income after additions (line 1 plus line 2)`.
OR-20 instructions p.12: *"Line 3. Income after additions (line 1 MINUS line 2)."*
**Three of four sources say PLUS**: the face; the arithmetic (Section A of
OR-ASC-CORP is headed "Additions"); and - decisively - the DOR's own **Form
OR-20-INC instructions p.11**, which for the identically-worded line read
*"line 1 PLUS line 2."* Build the face.

SAFETY GUARD - READY_TO_SEED stays False until Ken's Gate-1 SEED approval.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from sources.models import (
    AuthorityExcerpt, AuthorityFormLink, AuthoritySource, AuthoritySourceTopic,
    AuthorityTopic, RuleAuthorityLink,
)
from specs.models import (
    FlowAssertion, FormDiagnostic, FormFact, FormLine, FormRule, TaxForm, TestScenario,
)

# ═══════════════════════════════════════════════════════════════════════════
# SAFETY GUARD - flip ONLY on Ken's Gate-1 SEED approval, given DIRECTLY.
# D-25 closed the walk (SCOPE). That is not the seed gate.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = True   # ⚠ OPENED 2026-08-23 on Ken's DIRECT Gate-1 SEED approval ("seed it"), given unmediated in session. Pre-flight clean: prod 168 forms, 5 new sources and 1 new topic absent, 7 referenced rows resolve, OR_20_S baseline captured.


FORM_JURISDICTION = "OR"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"
FORM_ENTITY_TYPES = ["1120"]

# ORS 317.061, 2025 Edition: 6.6% of the first $1 million, 7.6% above.
# ⚠ The DOR states the SAME rule as base-plus-excess ("$66,000 plus 7.6% of the
# excess"). They are arithmetically identical - $1,000,000 x 6.6% = $66,000 - and
# the harness proves it rather than assuming it.
OR_EXCISE_BRACKETS: dict[int, tuple] = {
    2025: ((1000000, "0.066"), (None, "0.076")),
}
OR_EXCISE_BASE_AT_1M: dict[int, int] = {2025: 66000}

# ⚠⚠ MINIMUM TAX LADDER - ORS 317.090(2)(a), twelve subparagraphs (A)-(L),
# cross-verified tier for tier against the DOR's Appendix B table.
# Keyed on OREGON SALES OF THE FILING GROUP. (lower_inclusive, upper_inclusive|None, tax)
OR_MINIMUM_TAX_LADDER: dict[int, tuple] = {
    2025: (
        (0, 499999, 150),
        (500000, 999999, 500),
        (1000000, 1999999, 1000),
        (2000000, 2999999, 1500),
        (3000000, 4999999, 2000),
        (5000000, 6999999, 4000),
        (7000000, 9999999, 7500),
        (10000000, 24999999, 15000),
        (25000000, 49999999, 30000),
        (50000000, 74999999, 50000),
        (75000000, 99999999, 75000),
        (100000000, None, 100000),
    ),
}
# ORS 317.090(2)(b): "If a corporation is an S corporation, the minimum tax is $150."
# ⚠ Recorded, NOT used - an S corporation files OR-20-S, not this form.
OR_MINIMUM_TAX_S_CORP: dict[int, int] = {2025: 150}

# ⚠⚠ The three face lines that each clamp at minimum tax. Not one clamp at the end.
OR_MIN_TAX_CLAMPED_LINES: tuple = (18, 20, 22)
OR_MIN_TAX_CREDIT_PROOF = (
    'Instructions, verbatim: Minimum tax can\'t be "reduced, paid, or otherwise satisfied through '
    'the use of any tax credit" (ORS 317.090). And the ordering rule: "If your total standard and '
    'carryforward credits would reduce your tax below the minimum tax, you need to reduce how much '
    'you\'re using on" the schedule - which only works if the floor binds at each step.'
)
# ⚠ Not apportionable for a short tax year (except a change of accounting period).
OR_MIN_TAX_APPORTIONABLE_SHORT_YEAR: dict[int, bool] = {2025: False}
# OAR 150-317-0170(1)(a) - one per RETURN, never per affiliate.
OR_MIN_TAX_ONE_PER_RETURN = True

# ⚠⚠ O1 - THE DEPRECIATION POSITION. An ASSERTED ruling, not an absence.
OR_BONUS_ADDBACK: dict[int, int] = {2025: 0}          # NO add-back
OR_SEC_179_STATE_LIMIT: dict[int, int | None] = {2025: None}      # no state cap
OR_SEC_179_STATE_PHASEOUT: dict[int, int | None] = {2025: None}   # no state phaseout
OR_DEPRECIATION_AUTHORITY = (
    "ORS 317.010(7)(b) - the ROLLING prong, 'if related to the definition of taxable income'. Bonus "
    "and § 179 are computed in arriving at taxable income, so they ride (b), NOT the fixed "
    "12/31/2023 date at (a). Corroborated by ORS 317.312 ('no adjustment shall be made to federal "
    "depreciation expense'), by HB 2092 (2025 R1) FAILING to pass, and structurally by SB 1507 "
    "§§ 8-9 having to CREATE a bonus add-back from TY2026 - pure surplusage if the fixed date had "
    "already blocked OBBBA. Campaign D-25 O1."
)
# ⚠⚠ THE WRONG READING, retained ONLY so the harness can prove what it would cost.
OR_DEPRECIATION_PRONG_A_MISREADING = (
    "Reading ORS 317.010(7)(a)'s fixed 12/31/2023 date onto depreciation puts Oregon at pre-OBBBA - "
    "40% bonus and the old § 179 limits - and UNDER-DEPRECIATES a TY2025 OR-20 by up to SIXTY "
    "POINTS OF BASIS."
)
# ⚠⚠ ON THE RECORD (D-25 O1 iii): Georgia has a bonus add-back; Oregon does not.
OR_SHARES_BONUS_ADDBACK_WITH_GA = False

# SWITCH-READY for SB 1507's mandatory TY2026 shadow book (§ 168(k) as of 12/1/2017).
OR_TY2026_SHADOW_BOOK_BASELINE = "IRC § 168(k) as in effect on 2017-12-01 (SB 1507 § 9)"
OR_SB1507_CITE = "SB 1507 = 2026 Oregon Laws ch. 142, §§ 8-9, 35, 41 and 48(1)"
# ⚠⚠ THE STALENESS TRIPWIRE. § 41 amends ORS 317.010(7) ITSELF.
OR_TY2026_BLOCKED: dict[int, bool] = {2025: False, 2026: True}

# ORS 317.476 - and FOUR ways Oregon is not federal.
OR_NOL_CARRYFORWARD_YEARS: dict[int, int] = {2025: 15}     # NOT indefinite
OR_NOL_80PCT_LIMIT: dict[int, str | None] = {2025: None}   # NO § 172(a)(2) cap
OR_NOL_CARRYBACK_ALLOWED: dict[int, bool] = {2025: False}
OR_NOL_CARRYBACK_EXCEPTION = (
    "ORS 317.346 - crop production, animal production or aquaculture ONLY. Instructions: 'Oregon "
    "doesn't allow net losses to be carried back unless a corporation is engaged in crop "
    "production, animal production, or aquaculture.'"
)
OR_NOL_REIT_EXCLUDED = True     # ORS 317.476(5)

# Apportionment - single sales factor, OR-AP part 1 line 23, four decimals.
OR_APPORTIONMENT_FACTOR = "single sales factor"
OR_APPORTIONMENT_DECIMALS: dict[int, int] = {2025: 4}
OR_IS_JOYCE_STATE = True        # in the statute, not merely the rule
OR_IS_WATERS_EDGE = True        # structurally; no election, no 80/20 rule

# ⚠⚠ THE CODE NAMESPACE. **DO NOT reuse `load_or_pte.py`'s collision constants** -
# those describe the 50-code OR-20-S surface and are stale for this form (campaign
# G3: the like-for-like count corrects to 25, not 12). These are OR-20's own.
OR20_APPENDIX_A_CODE_COUNT: dict[int, int] = {2025: 93}
OR20_CODES_SHARED_WITH_INDIVIDUAL: dict[int, int] = {2025: 39}   # metric B, non-carryforward
OR20_CODES_HAZARDOUS: dict[int, int] = {2025: 25}                # metric A: 23 divergent + 2 near-twins
OR20_CODES_SEMANTICALLY_DIVERGENT: dict[int, int] = {2025: 23}
OR20_NEAR_TWIN_CODES: tuple = (338, 344)
OR20_CODES_IDENTICAL_SAFE: tuple = (122, 123, 187, 188, 336, 341, 342, 384, 385, 807, 810, 890, 901, 908)
# ⚠⚠ AT LEAST NINE of the sixteen "safe" rows FAIL a naive string-equality test,
# because OR-20's Appendix A appends an ORS citation to every credit label that
# Pub. OR-CODES omits. A raw `==` mapper fails on MORE THAN HALF the codes it is
# supposed to wave through.
OR20_SAFE_ROWS_FAILING_STRING_EQUALITY: tuple = (123, 336, 338, 344, 807, 810, 890, 901, 908)
OR20_LABEL_MATCH_RULE = (
    "An EXPLICIT CURATED MAP governs. Normalised matching (ORS cite, case, whitespace, em-dash "
    "suffixes, trailing plural) is a CROSS-CHECK that flags drift - never `==`, and never the "
    "mechanism. Authoring proved normalisation alone insufficient on the brief's own example."
)

# ⚠ TWO DIFFERENT IC-DISC RULES with two different entity tests. The research pass
# bundled them; the verification pass split them.
OR_IC_DISC_RATE: dict[int, str] = {2025: "0.025"}   # ORS 317.283(2)(a) - on total commissions
OR_IC_DISC_RATE_SCOPE = "any domestic international sales corporation formed on or before 2014-01-01"
OR_IC_DISC_MIN_TAX_EXEMPT_SCOPE = (
    "ORS 317.635(2) - an INTEREST CHARGE DISC formed on or before 2014-01-01 is 'exempt from the "
    "tax imposed under ORS 317.090' (the MINIMUM tax). A different rule, a different entity test."
)
# Farm liquidation LTCG: 5%, but delivered as a LINE 11 REDUCTION, not as a rate.
OR_FARM_LTCG_RATE: dict[int, str] = {2025: "0.05"}   # ORS 317.063
OR_FARM_LTCG_DELIVERY = "Schedule OR-FCG-20 adjustment at line 11 - a tax REDUCTION, never a rate"

# Line 1 alternative start points that must be special-cased.
OR_LINE1_START_POINTS: dict[str, str] = {
    "1120": "federal Form 1120 line 28 - taxable income BEFORE NOL and special deductions",
    "1120-C": "ag/hort co-ops begin at federal Form 1120-C LINE 25a, not line 28",
    "1120-IC-DISC": "total commissions received - Schedule B column c lines 1c, 2k and 3g",
    "990-T": "exempt organizations with UBTI; minimum-tax Oregon sales is only gross unrelated "
             "business income apportioned or allocated to Oregon",
    "1120-H": "homeowners associations - gross nonexempt income less directly-related deductions "
              "less the $100 specific deduction; net capital gains included with NO special treatment",
    "1066": "⚠ REMICs file OR-20-INC, NOT this form",
}

# O3 - Portland / Multnomah / Metro: RED-deferred with a NAMED three-form diagnostic.
OR_LOCAL_DEFERRED_FORMS: tuple = ("Portland/Multnomah Combined Business Tax",
                                  "Metro Supportive Housing Services", "Multnomah County Business Income Tax")
# O2 - OR-20-INC is its OWN spec, not a flag on this one.
OR_20_INC_IS_SEPARATE_SPEC = True


def _yk(table: dict, year: int = FORM_TAX_YEAR):
    if year not in table:
        raise CommandError(f"No TY{year} value in {table!r} - re-verify before extending the year.")
    return table[year]


def _or_guard_ty2026(year: int):
    """⚠⚠ THE STALENESS TRIPWIRE. SB 1507 § 41 amends ORS 317.010(7) ITSELF."""
    if _yk(OR_TY2026_BLOCKED, year) if year in OR_TY2026_BLOCKED else year >= 2026:
        raise CommandError(
            f"OREGON TY{year} IS BLOCKED. {OR_SB1507_CITE} amends ORS 317.010(7) itself - the "
            "conformity rule this whole spec rests on - and creates a § 168(k) add-back from "
            "TY2026 against a § 168(k)-as-of-2017-12-01 baseline. Every figure here is stale "
            "until SB 1507 is re-verified. This is a re-authoring event, not a rate roll-forward."
        )


def _or_excise_tax(oregon_taxable_income, year: int = FORM_TAX_YEAR):
    """Line 10 - ORS 317.061, as a BRACKET (the statute's form)."""
    _or_guard_ty2026(year)
    remaining, tax = max(0.0, float(oregon_taxable_income)), 0.0
    for width, rate in _yk(OR_EXCISE_BRACKETS, year):
        if remaining <= 0:
            break
        slice_ = remaining if width is None else min(remaining, width)
        tax += slice_ * float(rate)
        remaining -= slice_
    return tax


def _or_excise_tax_dor_form(oregon_taxable_income, year: int = FORM_TAX_YEAR):
    """The SAME rule as the DOR states it - base-plus-excess. Retained so the harness
    can prove the two formulations agree rather than assuming it.

    Appendix B: "$1 million or less, multiply by 6.6 percent. More than $1 million,
    multiply the amount that's more than $1 million by 7.6 percent, and add $66,000."
    """
    ti = max(0.0, float(oregon_taxable_income))
    if ti <= 1000000:
        return ti * float(_yk(OR_EXCISE_BRACKETS, year)[0][1])
    return (ti - 1000000) * float(_yk(OR_EXCISE_BRACKETS, year)[1][1]) + _yk(OR_EXCISE_BASE_AT_1M, year)


def _or_minimum_tax(oregon_sales_of_filing_group, year: int = FORM_TAX_YEAR):
    """Line 13 - ORS 317.090(2)(a). ⚠ FILING GROUP sales, ONE per return."""
    sales = max(0.0, float(oregon_sales_of_filing_group))
    for lo, hi, tax in _yk(OR_MINIMUM_TAX_LADDER, year):
        if sales >= lo and (hi is None or sales <= hi):
            return float(tax)
    raise CommandError(f"No minimum-tax tier covers Oregon sales of {sales} - the ladder must be "
                       "exhaustive; a gap means a tier was mistranscribed.")


def _or_line3(line1, line2):
    """⚠ DEFECT D1 - the FACE governs: 'Income after additions (line 1 PLUS line 2)'."""
    return float(line1) + float(line2)


def _or_line3_as_instructed(line1, line2):
    """The OR-20 instructions' contrary wording, retained so the harness can prove
    the two differ and that this spec did not ship the defective one."""
    return float(line1) - float(line2)


def _or_line14(calculated_excise_tax, minimum_tax):
    """Line 14 - 'Tax (greater of line 12 or line 13)'."""
    return max(float(calculated_excise_tax), float(minimum_tax))


def _or_apply_credits(tax_before_credits, standard_credits, carryforward_credits, minimum_tax):
    """⚠⚠ Lines 18, 20 and 22 - the minimum tax floor binds at EACH step.

    L18 = L16 - L17, not less than minimum tax
    L20 = L18 - L19, not below minimum tax
    L22 = L20 - L21 (LIFO benefit recapture subtraction)

    A single clamp applied only at the end is NOT equivalent: the DOR's ordering
    rule tells the preparer to reduce how much of a credit they USE, which is only
    meaningful if the floor binds where the credit is applied.
    """
    m = float(minimum_tax)
    l18 = max(m, float(tax_before_credits) - float(standard_credits))
    l20 = max(m, l18 - float(carryforward_credits))
    return {"L18": l18, "L20": l20}


def _or_credits_wasted(tax_before_credits, standard_credits, carryforward_credits, minimum_tax):
    """How much credit the minimum-tax floor absorbs - the number a preparer needs
    in order to apply the DOR's ordering rule and carry the rest forward."""
    unclamped = float(tax_before_credits) - float(standard_credits) - float(carryforward_credits)
    clamped = _or_apply_credits(tax_before_credits, standard_credits,
                                carryforward_credits, minimum_tax)["L20"]
    return max(0.0, clamped - unclamped)


def _or_bonus_addback(federal_bonus_taken, year: int = FORM_TAX_YEAR):
    """⚠⚠ O1 - ZERO for TY2025. An ASSERTED position with a citation, not an absence."""
    _or_guard_ty2026(year)
    return float(_yk(OR_BONUS_ADDBACK, year))


def _or_nol_available(loss_year_amount, loss_year, intervening_net_income, claim_year,
                      year: int = FORM_TAX_YEAR):
    """ORS 317.476(4) - and the subtle one is (4)(b).

    (4)(a) deductible in any of the FIFTEEN succeeding taxable years - NOT indefinite.
    (4)(b) "reduced by the net income (computed without the Oregon net loss deduction)
           of any intervening taxable year or years" - ⚠⚠ WHETHER OR NOT the deduction
           was claimed in those years. A build that tracks only amounts USED will
           OVERSTATE the carryforward.
    (4)(c) the earliest loss is exhausted before a later one may be deducted.
    """
    if claim_year > loss_year + _yk(OR_NOL_CARRYFORWARD_YEARS, year):
        return 0.0
    return max(0.0, float(loss_year_amount) - float(intervening_net_income))


def _or_nol_available_used_only(loss_year_amount, amounts_previously_used):
    """The naive 'track what was used' model - retained so the harness can prove it
    overstates the Oregon carryforward."""
    return max(0.0, float(loss_year_amount) - float(amounts_previously_used))


def _or_consolidated_return_required(in_consolidated_federal: bool, is_unitary: bool,
                                     any_member_oregon_nexus: bool) -> bool:
    """ORS 317.710(5)(a) / Instr. p.4 - ALL THREE conditions, not any."""
    return bool(in_consolidated_federal and is_unitary and any_member_oregon_nexus)


# ⚠⚠ NORMALISATION IS A CROSS-CHECK, NOT THE MECHANISM.
# The brief prescribed "normalised label matching, never ==". Authoring found that
# INSUFFICIENT on the brief's own worked example: strip the ORS citation from
# "Oregon Cultural Trust contribution (ORS 315.675)" and you still have SINGULAR
# against Pub. OR-CODES' PLURAL "Oregon Cultural Trust contributions". Fold the
# plural and some other pair will differ by a comma or an ampersand.
# ⭐ The MO-C lesson applies: an EXPLICIT MAP, never a derived rule. Normalisation
# is retained to CROSS-CHECK a curated map and to flag drift - never to build one.
OR20_LABEL_MATCHING_IS_AUTHORITATIVE = False
OR20_LABEL_MATCHING_NOTE = (
    "Normalised matching is a CROSS-CHECK only. It reconciles the ORS-citation suffix, case, "
    "whitespace, em-dash suffixes and trailing plurals - but authoring proved it still needed a "
    "plural fold to pass the brief's own example, which is evidence that the next pair will break "
    "it differently. The authoritative mechanism is an explicit curated code map."
)


def _or_normalise_code_label(label: str) -> str:
    """Cross-check normaliser. ⚠ NOT the reconciliation mechanism - see the note above.

    Folds: the parenthetical ORS citation, em/en-dash suffixes, case, whitespace,
    and a trailing plural - the last of which authoring had to ADD because the
    brief's prescribed remedy failed on the brief's own worked example.
    """
    import re
    s = re.sub(r"\(ORS[^)]*\)", " ", str(label))
    s = re.sub(r"[—–-].*$", " ", s)          # em/en-dash suffixes
    s = re.sub(r"\s+", " ", s).strip().casefold()
    return re.sub(r"s$", "", s)              # ⚠ trailing plural - see the note


AUTHORITY_TOPICS: list[tuple[str, str]] = [
    # Keep under 255 - the loader guards it (campaign D-17).
    ("or_20_corporation_excise", "Oregon Form OR-20: the 6.6/7.6% excise brackets against a twelve-tier "
     "minimum tax on filing-group sales that credits can never reduce, the rolling-prong depreciation "
     "conformity, and a fifteen-year NOL cut by intervening income."),
]

# ⚠⚠ TWO-WRITERS GUARD (D-31): owned by the seeded `load_or_pte.py`. REFERENCED, never re-declared.
# ⚠ Note what is deliberately NOT reused: that loader's four code-collision constants
# (OR_SEMANTIC_COLLISIONS / OR_LABEL_ONLY_COLLISIONS / OR_COLLIDING_CODES /
# OR_COLLISION_COUNT) describe the 50-code OR-20-S surface and are STALE for OR-20.
EXISTING_SOURCES_TO_REFERENCE: list[str] = [
    "OR_ORS_317_010_CONFORMITY",   # ⚠⚠ the two-prong rule O1 turns on
    "OR_ORS_317_061_090_RATES",    # the excise brackets AND the minimum-tax ladder
    "OR_ORS_317_301_DEPR",         # the ONLY 168(k)/179 disconnect - its window is CLOSED
    "OR_SB1507_2026_CH142",        # ⚠⚠ the TY2026 staleness tripwire
    "OR_2025_SCH_OR_AP",           # apportionment - part 1 line 23 feeds face line 8
    "OR_2025_SCH_ASC_CORP",        # additions/subtractions/credits sections A-D
    "OR_2025_PUB_OR_CODES",        # ⚠ the individual code namespace this form collides with
]

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "OR_2025_FORM_OR20", "source_type": "state_form",
        "source_rank": "primary_official", "jurisdiction_code": "OR",
        "title": "2025 Oregon Form OR-20 - Corporation Excise Tax Return",
        "citation": "Form OR-20 (2025), 150-102-020", "issuer": "Oregon Department of Revenue",
        "official_url": "https://www.oregon.gov/dor/forms/", "current_status": "active",
        "is_substantive_authority": True, "trust_score": 9.5, "topics": ["or_20_corporation_excise"],
        "excerpts": [
            {
                "excerpt_label": "The page-3 spine, lines 1-16 (verbatim)",
                "excerpt_text": (
                    "1 'Taxable income from U.S. corporation income tax return'; 2 'Total additions from "
                    "Schedule OR-ASC-CORP, Section A'; 3 'Income after additions (line 1 plus line 2)'; "
                    "4 'Total subtractions from Schedule OR-ASC-CORP, Section B'; 5 'Income before net "
                    "loss deduction (line 3 minus line 4). If income is derived from sources both in "
                    "Oregon and other states, carry amount from line 5 to Schedule OR-AP, part 2, line 1'; "
                    "6 'Net loss deduction if not apportioned'; 7 'Net capital loss deduction if not "
                    "apportioned'; 8 'Enter the apportionment percentage from Schedule OR-AP, part 1, "
                    "line 23; enter 100.0000 if you don't apportion income'; 9 'Oregon taxable income "
                    "(line 5 minus lines 6 and 7, or Schedule OR-AP, part 2, line 12)'; 10 'Calculated "
                    "excise tax'; 11 'Schedule OR-FCG-20 adjustment'; 12 'Total calculated excise tax "
                    "(line 10 minus line 11)'; 13 'Minimum tax'; 14 'Tax (greater of line 12 or line 13)'; "
                    "15 'Tax adjustments'; 16 'Tax before credits (line 14 plus line 15)'."
                ),
                "summary_text": "⚠ DEFECT D1: the instructions p.12 say 'line 1 MINUS line 2' at line 3. "
                                "The face, the arithmetic, and the DOR's own OR-20-INC instructions for "
                                "the identically-worded line all say PLUS. Three sources to one.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "⚠⚠ The minimum-tax floor clamps at THREE separate lines",
                "excerpt_text": (
                    "18 'Tax after standard credits (line 16 minus line 17, NOT LESS THAN MINIMUM TAX)'; "
                    "20 'Excise tax after standard and carryforward credits (line 18 minus line 19, NOT "
                    "BELOW MINIMUM TAX)'; 22 'Net excise tax (line 20 minus line 21)'. Instructions: "
                    "'Note: Minimum tax can't be \"reduced, paid, or otherwise satisfied through the use "
                    "of any tax credit\" (ORS 317.090).' And the ordering rule from the OR-ASC-CORP "
                    "instructions: 'If your total standard and carryforward credits would reduce your tax "
                    "below the minimum tax, you need to reduce how much you're using on' the schedule. "
                    "Also: 'List credits and codes on the OR-ASC-CORP in the order you want them used.'"
                ),
                "summary_text": "⚠ A single clamp at the end is NOT equivalent - the ordering rule only "
                                "means anything if the floor binds where each credit is applied.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "OR_2025_FORM_OR20_INSTR", "source_type": "state_instructions",
        "source_rank": "primary_official", "jurisdiction_code": "OR",
        "title": "2025 Oregon Form OR-20 Instructions incl. Appendix A (codes) and Appendix B (rates)",
        "citation": "Form OR-20 Instructions (Rev. 10-27-25), 150-102-020-1",
        "issuer": "Oregon Department of Revenue", "official_url": "https://www.oregon.gov/dor/forms/",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.0,
        "topics": ["or_20_corporation_excise"],
        "excerpts": [
            {
                "excerpt_label": "Appendix B - the calculated tax and the full minimum-tax ladder (verbatim)",
                "excerpt_text": (
                    "'Note: Corporation excise tax filers pay the GREATER of calculated tax or minimum "
                    "tax.' 'Calculated tax (ORS 317.061): If Oregon taxable income is $1 million or less, "
                    "multiply Oregon taxable income by 6.6 percent (not below zero). More than $1 million, "
                    "multiply the amount that's more than $1 million by 7.6 percent, and add $66,000.' "
                    "'Minimum tax table - C corporations only', keyed on 'Oregon sales of FILING GROUP': "
                    "under $500,000 -> $150; $500,000-$999,999 -> 500; $1m-$1.999m -> 1,000; $2m-$2.999m "
                    "-> 1,500; $3m-$4.999m -> 2,000; $5m-$6.999m -> 4,000; $7m-$9.999m -> 7,500; "
                    "$10m-$24.999m -> 15,000; $25m-$49.999m -> 30,000; $50m-$74.999m -> 50,000; "
                    "$75m-$99.999m -> 75,000; $100m and above -> 100,000. Line 13: 'Consolidated returns: "
                    "the minimum tax is based on Oregon sales of the affiliated group... ONE MINIMUM TAX "
                    "APPLIES TO THE AFFILIATED GROUP FILING THE CONSOLIDATED RETURN, not to each "
                    "individual affiliate.' 'The minimum tax isn't apportionable for a short tax year "
                    "(except a change of accounting period).'"
                ),
                "summary_text": "✅ Cross-verified tier for tier against ORS 317.090(2)(a)'s twelve "
                                "subparagraphs (A)-(L). Same partition, no gap, no overlap.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "⚠ Line 1's five alternative start points, and the NOL rules",
                "excerpt_text": (
                    "Line 1, verbatim: 'Enter the taxable income reported for federal income tax purposes "
                    "BEFORE net operating loss or special deductions (federal Form 1120, line 28).' "
                    "Alternatives: ag/hort co-ops 'begin the Oregon return with LINE 25a from the federal "
                    "return (not line 28)'; an IC-DISC formed on or before 2014-01-01 enters 'total "
                    "commissions received'; exempt organizations with UBTI attach federal Form 990-T; "
                    "homeowners associations use Form 1120-H with 'gross nonexempt income less "
                    "directly-related deductions, less the specific $100 deduction. However, net capital "
                    "gains are included in the computation and receive no special treatment'; ⚠ REMICs "
                    "file OR-20-INC, not OR-20. NOL, p.14: 'Oregon doesn't allow net losses to be carried "
                    "back UNLESS a corporation is engaged in crop production, animal production, or "
                    "aquaculture. See ORS 317.346.' p.5: 'Don't amend your Oregon return if you amend the "
                    "federal return to carry a net operating loss back to prior years.'"
                ),
                "summary_text": "⚠ Five federal start points, one of which routes the filer to a DIFFERENT "
                                "Oregon form entirely.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "OR_ORS_317_476_NOL", "source_type": "state_statute",
        "source_rank": "controlling", "jurisdiction_code": "OR",
        "title": "ORS 317.476 - Oregon net loss carryforward for corporations",
        "citation": "ORS 317.476(4)-(5) (2025 Edition)", "issuer": "Oregon Legislative Assembly",
        "official_url": "https://www.oregonlegislature.gov/bills_laws/ors/ors317.html",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["or_20_corporation_excise"],
        "excerpts": [{
            "excerpt_label": "⚠⚠ FOUR ways Oregon's NOL is not federal - and (4)(b) is the subtle one",
            "excerpt_text": (
                "(4)(a), verbatim: 'The Oregon net loss in any taxable year shall be allowed as a "
                "deduction in any of the 15 SUCCEEDING TAXABLE YEARS.' (4)(b): 'The amount of the Oregon "
                "net loss deductible in any taxable year shall be the Oregon net loss of a prior year "
                "REDUCED BY THE NET INCOME (computed without the Oregon net loss deduction) OF ANY "
                "INTERVENING TAXABLE YEAR OR YEARS between the year of loss and the succeeding taxable "
                "year in which the deduction is claimed.' (4)(c): 'The Oregon net loss of the earliest "
                "taxable year shall be exhausted before an Oregon net loss from a later year may be "
                "deducted.' (5): no deduction for a business trust qualifying as a REIT under IRC "
                "§§ 856-858. Credit line [Formerly 317.297; 1987 c.293 §45d] - last amended 1987."
            ),
            "summary_text": "⚠⚠ (4)(b) is STRONGER than FIFO ordering: the loss is reduced by intervening "
                            "NET INCOME whether or not the deduction was claimed in those years. A build "
                            "tracking only amounts USED will OVERSTATE the carryforward. And there is NO "
                            "80% limitation anywhere in this section.",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "OR_ORS_317_705_725_CONSOL", "source_type": "state_statute",
        "source_rank": "controlling", "jurisdiction_code": "OR",
        "title": "ORS 317.705-317.725 - consolidated Oregon returns and the unitary test",
        "citation": "ORS 317.705(3)(a), 317.710(5)(a) (2025 Edition)",
        "issuer": "Oregon Legislative Assembly",
        "official_url": "https://www.oregonlegislature.gov/bills_laws/ors/ors317.html",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["or_20_corporation_excise"],
        "excerpts": [{
            "excerpt_label": "The three-condition test and the definition of unitary (verbatim)",
            "excerpt_text": (
                "ORS 317.710(5)(a): 'if two or more corporations subject to taxation under this chapter "
                "are members of the same affiliated group making a consolidated federal return AND are "
                "members of the same unitary group, they shall file a consolidated state return.' "
                "Instructions p.4 state the same as three conditions: 'Included in a consolidated federal "
                "return; Unitary; AND At least one of the affiliated corporations doing business in "
                "Oregon or have Oregon-source income.' 'Unitary business': 'A business that has, directly "
                "or indirectly between members or parts of the enterprise, either a sharing or an exchange "
                "of value shown by: Centralized management or a common executive force; Centralized "
                "administrative services or functions resulting in economies of scale; or Flow of goods, "
                "capital resources, or services showing functional integration.' ⚠ Oregon is WATER'S-EDGE "
                "structurally - no election and no 80/20 rule - and a JOYCE state in the statute, not "
                "merely by rule."
            ),
            "summary_text": "⚠ ALL THREE conditions, not any. And the minimum tax is then measured once, "
                            "on the FILING GROUP's Oregon sales.",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "OR_ORS_317_283_635_DISC", "source_type": "state_statute",
        "source_rank": "controlling", "jurisdiction_code": "OR",
        "title": "ORS 317.283 and 317.635 - the TWO different IC-DISC rules",
        "citation": "ORS 317.283(2)(a); ORS 317.635(2); ORS 317.063 (2025 Edition)",
        "issuer": "Oregon Legislative Assembly",
        "official_url": "https://www.oregonlegislature.gov/bills_laws/ors/ors317.html",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["or_20_corporation_excise"],
        "excerpts": [{
            "excerpt_label": "⚠ Two rules, two entity tests - the research pass bundled them",
            "excerpt_text": (
                "ORS 317.283(2)(a) imposes a 2.5 PERCENT RATE on 'any commission received by the DOMESTIC "
                "INTERNATIONAL SALES CORPORATION' - any DISC formed on or before 2014-01-01. ORS "
                "317.635(2) does something else entirely: 'An INTEREST CHARGE DISC formed on or before "
                "January 1, 2014, is EXEMPT FROM THE TAX IMPOSED UNDER ORS 317.090' - i.e. the MINIMUM "
                "tax, and only for an interest-charge DISC. ⚠ Two form behaviours, two different entity "
                "tests; they must not be bundled. An IC-DISC formed AFTER 2014-01-01 is not exempt, is "
                "disregarded to the extent of related-party transactions, and otherwise files normally. "
                "Its due date is unique: 'due by the 15th day of the month following the due date of the "
                "federal return... NO EXTENSIONS are allowed for IC-DISC returns.' Separately, ORS "
                "317.063(2): 'Notwithstanding ORS 317.061, taxable income that consists of net long-term "
                "capital gain shall be subject to tax under this chapter at a rate of FIVE PERCENT' - "
                "farm liquidation, delivered as a line-11 REDUCTION via Schedule OR-FCG-20, not as a rate."
            ),
            "summary_text": "⚠ A verification-pass correction: the original brief cited '317.283, 317.635' "
                            "jointly for the rate. One is a rate, the other a minimum-tax exemption.",
            "is_key_excerpt": True,
        }],
    },
]

AUTHORITY_FORM_LINKS: list[tuple] = [
    ("OR_2025_FORM_OR20", "OR_20", "governs"),
    ("OR_2025_FORM_OR20_INSTR", "OR_20", "governs"),
    ("OR_ORS_317_476_NOL", "OR_20", "governs"),
    ("OR_ORS_317_705_725_CONSOL", "OR_20", "governs"),
    ("OR_ORS_317_283_635_DISC", "OR_20", "governs"),
    ("OR_ORS_317_010_CONFORMITY", "OR_20", "governs"),
    ("OR_ORS_317_061_090_RATES", "OR_20", "governs"),
    ("OR_ORS_317_301_DEPR", "OR_20", "governs"),
    ("OR_SB1507_2026_CH142", "OR_20", "informs"),
    ("OR_2025_SCH_OR_AP", "OR_20", "governs"),
    ("OR_2025_SCH_ASC_CORP", "OR_20", "governs"),
    ("OR_2025_PUB_OR_CODES", "OR_20", "informs"),
]

F_FACTS: list[dict] = [
    {"fact_key": "federal_return_type", "label": "Federal return type driving the line-1 start point",
     "data_type": "string", "required": True, "sort_order": 1,
     "notes": "⚠ FIVE start points: 1120 line 28 · 1120-C line 25a (co-ops) · 1120-IC-DISC commissions "
              "· 990-T (UBTI) · 1120-H (HOAs). ⚠ A REMIC (Form 1066) files OR-20-INC, NOT this form."},
    {"fact_key": "federal_taxable_income", "label": "L1 Taxable income from the U.S. return",
     "data_type": "decimal", "required": True, "sort_order": 2,
     "notes": "Form 1120 line 28 - BEFORE net operating loss and special deductions."},
    {"fact_key": "total_additions", "label": "L2 Total additions (Schedule OR-ASC-CORP Section A)",
     "data_type": "decimal", "required": False, "sort_order": 3,
     "notes": "⚠ DEFECT D1: the instructions say line 3 = line 1 MINUS line 2. The face, the arithmetic "
              "and the DOR's own OR-20-INC instructions all say PLUS. Build the face."},
    {"fact_key": "total_subtractions", "label": "L4 Total subtractions (Schedule OR-ASC-CORP Section B)",
     "data_type": "decimal", "required": False, "sort_order": 4},
    {"fact_key": "is_apportioning", "label": "Income derived from sources both in and outside Oregon?",
     "data_type": "boolean", "required": False, "sort_order": 5,
     "notes": "If yes, line 5 carries to Schedule OR-AP part 2 line 1 and line 9 comes from OR-AP part 2 "
              "line 12. If no, enter 100.0000 at line 8."},
    {"fact_key": "apportionment_percent", "label": "L8 Apportionment percentage (OR-AP part 1 line 23)",
     "data_type": "decimal", "required": False, "sort_order": 6,
     "notes": "⚠ SINGLE SALES FACTOR, four decimals. Oregon is a JOYCE state - in the statute, not "
              "merely by rule."},
    {"fact_key": "net_loss_deduction", "label": "L6 Net loss deduction if not apportioned",
     "data_type": "decimal", "required": False, "sort_order": 7,
     "notes": "⚠ Face line 6 when Oregon-only; OR-AP part 2 line 10a when apportioning. NEVER BOTH."},
    {"fact_key": "net_capital_loss_deduction", "label": "L7 Net capital loss deduction if not apportioned",
     "data_type": "decimal", "required": False, "sort_order": 8},
    {"fact_key": "oregon_sales_of_filing_group", "label": "Oregon sales OF THE FILING GROUP (minimum tax)",
     "data_type": "decimal", "required": False, "sort_order": 9,
     "notes": "⚠⚠ ORS 317.090(1)(a) defines it, not just the instructions. Branch (B) - a "
              "non-apportioning corporation - is a COUNTERFACTUAL computation ('the total sales in this "
              "state that the taxpayer WOULD HAVE HAD if required to apportion'), and the instructions' "
              "Form 1120 line list is a 'Generally' safe harbour, expressly non-exclusive. ⚠ Excludes "
              "business done with or for members of an agricultural cooperative (ORS 317.090(1)(b))."},
    {"fact_key": "in_consolidated_federal", "label": "Included in a consolidated federal return?",
     "data_type": "boolean", "required": False, "sort_order": 10},
    {"fact_key": "is_unitary_group", "label": "Members of the same unitary group?",
     "data_type": "boolean", "required": False, "sort_order": 11,
     "notes": "Sharing or exchange of value shown by centralized management, centralized administrative "
              "services producing economies of scale, or flow of goods/capital/services showing "
              "functional integration."},
    {"fact_key": "any_member_oregon_nexus", "label": "At least one affiliate doing business in Oregon?",
     "data_type": "boolean", "required": False, "sort_order": 12,
     "notes": "⚠ ALL THREE conditions must hold for a consolidated Oregon return - not any."},
    {"fact_key": "standard_credits", "label": "L17 Total standard credits (OR-ASC-CORP Section C)",
     "data_type": "decimal", "required": False, "sort_order": 13,
     "notes": "⚠⚠ Cannot reduce tax below the minimum tax. List codes in the order you want them used."},
    {"fact_key": "carryforward_credits", "label": "L19 Total carryforward credits (OR-ASC-CORP Section D)",
     "data_type": "decimal", "required": False, "sort_order": 14},
    {"fact_key": "lifo_benefit_recapture", "label": "L21 LIFO benefit recapture subtraction",
     "data_type": "decimal", "required": False, "sort_order": 15},
    {"fact_key": "farm_liquidation_ltcg", "label": "L11 Schedule OR-FCG-20 adjustment (farm liquidation)",
     "data_type": "decimal", "required": False, "sort_order": 16,
     "notes": "⚠ ORS 317.063's 5% is delivered as a line-11 tax REDUCTION, never as a rate. Four "
              "conditions apply, incl. that the buyer is not related under IRC § 267."},
    {"fact_key": "is_ic_disc", "label": "IC-DISC, and formed on or before 2014-01-01?",
     "data_type": "string", "required": False, "sort_order": 17,
     "notes": "⚠ TWO DIFFERENT RULES: ORS 317.283(2)(a) gives a 2.5% RATE to a domestic international "
              "sales corporation; ORS 317.635(2) exempts an INTEREST CHARGE DISC from the MINIMUM tax. "
              "Different entity tests. ⚠ Unique due date and NO extensions."},
    {"fact_key": "federal_bonus_taken", "label": "Federal § 168(k) bonus depreciation taken",
     "data_type": "decimal", "required": False, "sort_order": 18,
     "notes": "⚠⚠ O1: there is NO Oregon add-back for TY2025. Collected so the review diagnostic can "
              "state the position on returns where it matters, NOT because it feeds a computation."},
    {"fact_key": "has_portland_metro_nexus", "label": "Portland / Multnomah / Metro filing obligation?",
     "data_type": "boolean", "required": False, "sort_order": 19,
     "notes": "⚠ O3: RED-deferred in v1 with a named three-form diagnostic."},
    {"fact_key": "estimated_payments", "label": "L23 Estimated payments and refundable credits (Schedule ES line 8)",
     "data_type": "decimal", "required": False, "sort_order": 20},
    {"fact_key": "pte_withholding", "label": "L24 Withholding paid on your behalf by a PTE or on real estate",
     "data_type": "decimal", "required": False, "sort_order": 21},
]

F_RULES: list[dict] = [
    {"rule_id": "R-OR20-L3", "title": "⚠ L3 Income after additions - the FACE governs (defect D1)",
     "rule_type": "calculation", "formula": "L3 = L1 + L2", "inputs": ["federal_taxable_income", "total_additions"],
     "outputs": ["L3"], "sort_order": 1,
     "description": "⚠ DEFECT D1. The face reads 'Income after additions (line 1 PLUS line 2)'; the OR-20 "
                    "instructions p.12 read 'line 1 MINUS line 2'. THREE sources against one: the face; "
                    "the arithmetic (OR-ASC-CORP Section A is headed 'Additions'); and decisively the "
                    "DOR's own Form OR-20-INC instructions p.11, which for the identically-worded line "
                    "read 'line 1 PLUS line 2'. Build the face."},
    {"rule_id": "R-OR20-L10", "title": "L10 Calculated excise tax - 6.6% / 7.6% (ORS 317.061)",
     "rule_type": "calculation", "formula": "6.6% of the first $1,000,000; 7.6% above",
     "inputs": ["federal_taxable_income", "apportionment_percent"], "outputs": ["L10"], "sort_order": 2,
     "description": "ORS 317.061 states it as a BRACKET; the DOR states it as base-plus-excess ($66,000 "
                    "plus 7.6% of the amount over $1 million). They are arithmetically identical - "
                    "$1,000,000 x 6.6% = $66,000 - and the harness PROVES the two formulations agree "
                    "rather than assuming it. ⚠ Two statutory alternates displace this rate: an IC-DISC "
                    "formed on or before 2014-01-01 pays 2.5% on commissions (ORS 317.283(2)(a)), and "
                    "farm-liquidation long-term capital gain is taxed at 5% (ORS 317.063) - but the "
                    "latter arrives as a line-11 REDUCTION, not as a rate."},
    {"rule_id": "R-OR20-L13", "title": "⚠⚠ L13 Minimum tax - twelve tiers on FILING GROUP sales",
     "rule_type": "lookup", "formula": "ladder(Oregon sales of the filing group), ORS 317.090(2)(a)",
     "inputs": ["oregon_sales_of_filing_group"], "outputs": ["L13"], "sort_order": 3,
     "description": "Twelve tiers from $150 (under $500,000) to $100,000 ($100 million and above), "
                    "cross-verified tier for tier against ORS 317.090(2)(a)'s subparagraphs (A)-(L). "
                    "⚠⚠ Measured on the FILING GROUP: 'One minimum tax applies to the affiliated group "
                    "filing the consolidated return, NOT to each individual affiliate' (OAR "
                    "150-317-0170(1)(a)). ⚠ Not apportionable for a short tax year except on a change of "
                    "accounting period. ⚠ 'Oregon sales' is statutorily defined, and for a "
                    "non-apportioning corporation it is a COUNTERFACTUAL - what the taxpayer 'would have "
                    "had' if required to apportion - so the instructions' federal line list is a safe "
                    "harbour, not the rule."},
    {"rule_id": "R-OR20-L14", "title": "L14 Tax - the GREATER of calculated tax or minimum tax",
     "rule_type": "calculation", "formula": "L14 = max(L12, L13)", "inputs": ["L12", "L13"],
     "outputs": ["L14"], "sort_order": 4,
     "description": "Appendix B, verbatim: 'Corporation excise tax filers pay the GREATER of calculated "
                    "tax or minimum tax.' ⚠ A profitable corporation with large Oregon sales can still "
                    "be on the minimum, and a loss corporation is ALWAYS on it - the minimum tax is not "
                    "a small-taxpayer floor, it is a sales-based alternative."},
    {"rule_id": "R-OR20-CREDITFLOOR", "title": "⚠⚠ Credits can NEVER reduce tax below the minimum - at THREE lines",
     "rule_type": "limitation",
     "formula": "L18 = max(minimum, L16 - L17) ; L20 = max(minimum, L18 - L19) ; L22 = L20 - L21",
     "inputs": ["standard_credits", "carryforward_credits", "lifo_benefit_recapture"],
     "outputs": ["L18", "L20", "L22"], "sort_order": 5,
     "description": "⚠⚠ Lines 18, 20 and 22 each carry an independent clamp ON THE FACE. Instructions: "
                    "'Minimum tax can't be \"reduced, paid, or otherwise satisfied through the use of any "
                    "tax credit\" (ORS 317.090).' A single clamp applied only at the end is NOT "
                    "equivalent: the DOR's ordering rule tells the preparer to 'reduce how much you're "
                    "using' of a credit, which is only meaningful if the floor binds where the credit is "
                    "applied. The unused portion is then available to carry forward, so getting this "
                    "wrong destroys credit the taxpayer keeps."},
    {"rule_id": "R-OR20-DEPR", "title": "⚠⚠ O1 - Oregon depreciation IS federal for TY2025. ASSERTED.",
     "rule_type": "calculation", "formula": "bonus add-back = 0 ; no state § 179 limit or phaseout",
     "inputs": ["federal_bonus_taken"], "outputs": ["DEPRECIATION"], "sort_order": 6,
     "description": "⚠⚠ ORS 317.010(7) has two prongs: (a) the fixed 12/31/2023 date, and (b) rolling "
                    "'if related to the definition of taxable income'. Bonus and § 179 are computed in "
                    "arriving at taxable income, so they ride (b). For TY2025: § 168(k) conforms at the "
                    "OBBBA 100% level, § 179 at $2,500,000/$4,000,000, and there is NO ADD-BACK. "
                    "⚠ The research pass read prong (a) and would have UNDER-DEPRECIATED a TY2025 OR-20 "
                    "by up to SIXTY POINTS OF BASIS. Corroborated by ORS 317.312 ('no adjustment shall be "
                    "made to federal depreciation expense'), by HB 2092 (2025 R1) failing to pass, and "
                    "⭐ structurally by SB 1507 §§ 8-9 having to CREATE an add-back from TY2026 - pure "
                    "surplusage if the fixed date had already blocked OBBBA. ⚠⚠ ON THE RECORD: there is "
                    "NO shared bonus-add-back abstraction with Georgia. Georgia has one; Oregon does not. "
                    "DO NOT CLONE."},
    {"rule_id": "R-OR20-NOL", "title": "⚠ NOL - fifteen years, no 80% cap, and reduced by INTERVENING income",
     "rule_type": "limitation",
     "formula": "carryforward = 15 years ; available = loss - intervening net income (claimed or not) ; "
                "earliest loss exhausted first ; no carryback",
     "inputs": ["net_loss_deduction"], "outputs": ["L6"], "sort_order": 7,
     "description": "ORS 317.476(4). FOUR ways Oregon is not federal: (1) FIFTEEN-year carryforward, not "
                    "indefinite; (2) NO 80%-of-taxable-income limitation - § 172(a)(2) has no analogue "
                    "here; (3) ⚠⚠ (4)(b) reduces the loss by intervening-year NET INCOME 'whether or not "
                    "the deduction was claimed', which is STRONGER than FIFO ordering and which a build "
                    "tracking only amounts USED will get wrong by overstating the carryforward; (4) NO "
                    "carryback, except crop production, animal production or aquaculture under ORS "
                    "317.346. ⚠ REITs are excluded entirely by (5). ⚠ Routing: face line 6 when "
                    "Oregon-only, OR-AP part 2 line 10a when apportioning - never both."},
    {"rule_id": "R-OR20-CONSOL", "title": "Consolidated return - ALL THREE conditions",
     "rule_type": "eligibility",
     "formula": "required iff consolidated_federal AND unitary AND any member has Oregon nexus",
     "inputs": ["in_consolidated_federal", "is_unitary_group", "any_member_oregon_nexus"],
     "outputs": ["CONSOLIDATED"], "sort_order": 8,
     "description": "ORS 317.710(5)(a) and Instr. p.4. ⚠ ALL THREE, not any. ⚠ Oregon is WATER'S-EDGE "
                    "structurally - there is no election and no 80/20 rule - and a JOYCE state in the "
                    "statute rather than merely by rule. Insurance affiliates are a MANDATORY exclusion "
                    "with a 100% DRD attached. ⚠ The consolidation determines the minimum tax base: one "
                    "minimum tax for the group, on the group's Oregon sales."},
    {"rule_id": "R-OR20-CODES", "title": "⚠⚠ Code namespace - map by NORMALISED label, never by ==",
     "rule_type": "validation",
     "formula": "93 Appendix A codes; 39 shared with the individual set; 25 hazardous; "
                "normalise before comparing",
     "inputs": [], "outputs": ["CODE_MAPPING"], "sort_order": 9,
     "description": "⚠⚠ OR-20's Appendix A carries 93 codes. 39 of the 67 non-carryforward codes also "
                    "exist in Pub. OR-CODES' individual set; of those, 23 are SEMANTICALLY DIVERGENT and "
                    "2 are near-twins (338, 344) - a hazard surface of 25, roughly double the OR-20-S "
                    "figure of 12. ⚠⚠ AND AT LEAST NINE OF THE SIXTEEN 'SAFE' ROWS FAIL A NAIVE "
                    "STRING-EQUALITY TEST, because OR-20's Appendix A appends an ORS citation to every "
                    "credit label that Pub. OR-CODES omits. A raw `==` mapper fails on MORE THAN HALF the "
                    "codes it is supposed to wave through. Normalise: strip the parenthetical ORS cite, "
                    "case-fold, collapse whitespace and em-dash suffixes. ⚠ Do NOT reuse "
                    "`load_or_pte.py`'s collision constants - they describe the OR-20-S surface."},
    {"rule_id": "R-OR20-TY2026", "title": "⚠⚠ TY2026 is BLOCKED - SB 1507 amends the conformity rule itself",
     "rule_type": "validation", "formula": "refuse any computation for a tax year >= 2026",
     "inputs": [], "outputs": ["STALENESS"], "sort_order": 10,
     "description": "⚠⚠ SB 1507 = 2026 Oregon Laws ch. 142. § 41 amends ORS 317.010(7) ITSELF - the "
                    "conformity rule this entire spec rests on - and §§ 8-9 create a § 168(k) add-back "
                    "from TY2026 measured against a § 168(k)-as-of-2017-12-01 baseline. The TY2025 engine "
                    "is built SWITCH-READY for that mandatory shadow book, but every figure here is "
                    "STALE until SB 1507 is re-verified. This is a RE-AUTHORING event, not a rate "
                    "roll-forward."},
]

F_RULE_LINKS: list[tuple] = [
    ("R-OR20-L3", "OR_2025_FORM_OR20", "governs", "⚠ D1 - the face says PLUS; the instructions say MINUS."),
    ("R-OR20-L3", "OR_2025_FORM_OR20_INSTR", "informs", "⚠ The defective wording, recorded so the "
     "defect is auditable rather than built."),
    ("R-OR20-L10", "OR_ORS_317_061_090_RATES", "governs", "ORS 317.061 - 6.6% / 7.6%, last amended 2013."),
    ("R-OR20-L10", "OR_2025_FORM_OR20_INSTR", "governs", "Appendix B's base-plus-excess statement of the "
     "same rule."),
    ("R-OR20-L10", "OR_ORS_317_283_635_DISC", "informs", "⚠ The two statutory alternates - the IC-DISC "
     "2.5% rate and the farm-liquidation 5%."),
    ("R-OR20-L13", "OR_ORS_317_061_090_RATES", "governs", "ORS 317.090(2)(a) - the twelve tiers, "
     "cross-verified against the printed table."),
    ("R-OR20-L13", "OR_2025_FORM_OR20_INSTR", "governs", "Appendix B's table and the filing-group rule."),
    ("R-OR20-L14", "OR_2025_FORM_OR20", "governs", "'Tax (greater of line 12 or line 13)'."),
    ("R-OR20-CREDITFLOOR", "OR_2025_FORM_OR20", "governs", "⚠⚠ The clamp is printed at lines 18, 20 and 22."),
    ("R-OR20-CREDITFLOOR", "OR_2025_SCH_ASC_CORP", "governs", "The ordering rule - reduce how much of a "
     "credit you use, and carry the rest forward."),
    ("R-OR20-DEPR", "OR_ORS_317_010_CONFORMITY", "governs", "⚠⚠ The two-prong rule. Bonus and § 179 ride "
     "the ROLLING prong (b), not the fixed date at (a)."),
    ("R-OR20-DEPR", "OR_ORS_317_301_DEPR", "governs", "The only § 168(k)/§ 179 disconnect - and its "
     "window is CLOSED."),
    ("R-OR20-DEPR", "OR_SB1507_2026_CH142", "informs", "⭐ Structurally decisive: SB 1507 had to CREATE "
     "an add-back from TY2026, which is surplusage if the fixed date already blocked OBBBA."),
    ("R-OR20-NOL", "OR_ORS_317_476_NOL", "governs", "Fifteen years, no 80% cap, the (4)(b) "
     "intervening-income reduction, and the REIT exclusion."),
    ("R-OR20-NOL", "OR_2025_FORM_OR20_INSTR", "governs", "The carryback prohibition and its ORS 317.346 "
     "agricultural exception."),
    ("R-OR20-CONSOL", "OR_ORS_317_705_725_CONSOL", "governs", "The three-condition test and the unitary "
     "definition."),
    ("R-OR20-CODES", "OR_2025_SCH_ASC_CORP", "governs", "Sections A-D and the code mechanics."),
    ("R-OR20-CODES", "OR_2025_PUB_OR_CODES", "informs", "⚠ The individual namespace this form collides "
     "with - 163 codes parsed positionally."),
    ("R-OR20-TY2026", "OR_SB1507_2026_CH142", "governs", "⚠⚠ § 41 amends ORS 317.010(7) itself."),
    ("R-OR20-TY2026", "OR_ORS_317_010_CONFORMITY", "governs", "The rule being amended."),
    ("R-OR20-L14", "OR_2025_SCH_OR_AP", "informs", "Apportionment feeds line 8 and hence line 9."),
]

F_LINES: list[dict] = [
    {"line_number": "OR20-3", "description": "L3 Income after additions (L1 + L2) - ⚠ defect D1",
     "line_type": "subtotal", "source_rules": ["R-OR20-L3"], "sort_order": 1},
    {"line_number": "OR20-5", "description": "L5 Income before net loss deduction (L3 - L4)",
     "line_type": "subtotal", "source_rules": ["R-OR20-L3"], "sort_order": 2},
    {"line_number": "OR20-8", "description": "L8 Apportionment percentage - single sales factor, 4 dp",
     "line_type": "calculated", "source_rules": ["R-OR20-CONSOL"], "sort_order": 3},
    {"line_number": "OR20-9", "description": "L9 Oregon taxable income",
     "line_type": "subtotal", "source_rules": ["R-OR20-NOL"], "sort_order": 4},
    {"line_number": "OR20-10", "description": "L10 Calculated excise tax (6.6% / 7.6%)",
     "line_type": "calculated", "source_rules": ["R-OR20-L10"], "sort_order": 5},
    {"line_number": "OR20-12", "description": "L12 Total calculated excise tax (L10 - L11)",
     "line_type": "subtotal", "source_rules": ["R-OR20-L10"], "sort_order": 6},
    {"line_number": "OR20-13", "description": "L13 Minimum tax - ⚠ FILING GROUP sales, one per return",
     "line_type": "calculated", "source_rules": ["R-OR20-L13"], "sort_order": 7},
    {"line_number": "OR20-14", "description": "L14 Tax - the GREATER of L12 or L13",
     "line_type": "calculated", "source_rules": ["R-OR20-L14"], "sort_order": 8},
    {"line_number": "OR20-18", "description": "L18 Tax after standard credits - ⚠ clamped at minimum",
     "line_type": "calculated", "source_rules": ["R-OR20-CREDITFLOOR"], "sort_order": 9},
    {"line_number": "OR20-20", "description": "L20 Excise tax after all credits - ⚠ clamped at minimum",
     "line_type": "calculated", "source_rules": ["R-OR20-CREDITFLOOR"], "sort_order": 10},
    {"line_number": "OR20-22", "description": "L22 Net excise tax (L20 - L21 LIFO recapture)",
     "line_type": "subtotal", "source_rules": ["R-OR20-CREDITFLOOR"], "sort_order": 11},
    {"line_number": "OR20-25", "description": "L25 Tax due", "line_type": "calculated",
     "source_rules": ["R-OR20-CREDITFLOOR"], "sort_order": 12},
    {"line_number": "OR20-26", "description": "L26 Overpayment", "line_type": "calculated",
     "source_rules": ["R-OR20-CREDITFLOOR"], "sort_order": 13},
]

F_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_OR20_DEPRECIATION_POSITION", "severity": "info",
     "title": "⚠⚠ Oregon depreciation IS federal for TY2025 - this is asserted, not omitted",
     "condition": "federal_bonus_taken != 0",
     "message": "Delvio applies NO Oregon adjustment to federal depreciation for TY2025: § 168(k) bonus "
                "conforms at the OBBBA 100% level and § 179 at $2,500,000 / $4,000,000, with no "
                "add-back. ⚠ This is an ASSERTED position with a citation, not a gap. ORS 317.010(7) has "
                "two prongs — (a) a fixed 12/31/2023 date and (b) rolling 'if related to the definition "
                "of taxable income' — and bonus and § 179 are computed in arriving at taxable income, so "
                "they ride prong (b). Corroborated by ORS 317.312 ('no adjustment shall be made to "
                "federal depreciation expense'), by HB 2092 (2025 R1) failing to pass, and structurally "
                "by SB 1507 §§ 8-9 having to CREATE an add-back from TY2026 — which would be surplusage "
                "if the fixed date had already blocked OBBBA. ⚠ Reading prong (a) instead would "
                "under-depreciate this return by up to sixty points of basis. ⚠⚠ Oregon does NOT share "
                "Georgia's bonus add-back — do not apply one here.",
     "notes": "⚠⚠ D-25 O1(i): Ken ruled ASSERT with a review diagnostic carrying the reasoning, so the "
              "next reader cannot 'correct' it back to the fixed date."},
    {"diagnostic_id": "D_OR20_TY2026_STALE", "severity": "error",
     "title": "⚠⚠ Oregon TY2026 is BLOCKED - SB 1507 amends the conformity rule itself",
     "condition": "tax_year >= 2026",
     "message": "This spec encodes TY2025 Oregon and must NOT be rolled forward. SB 1507 (2026 Oregon "
                "Laws ch. 142) § 41 amends ORS 317.010(7) ITSELF — the conformity rule every figure here "
                "rests on — and §§ 8-9 create a § 168(k) add-back from TY2026, measured against a "
                "§ 168(k)-as-of-1 December 2017 baseline. The TY2025 engine was deliberately built "
                "SWITCH-READY for that mandatory shadow book rather than re-architected under deadline, "
                "but the switch cannot be thrown until SB 1507 is re-verified. Treat TY2026 as a "
                "RE-AUTHORING event, not a rate roll-forward.",
     "notes": "⚠⚠ The tripwire fires on the conformity rule, not on a rate - which is why it is an error "
              "rather than a warning."},
    {"diagnostic_id": "D_OR20_MIN_TAX_ABSORBS_CREDITS", "severity": "warning",
     "title": "⚠⚠ The minimum tax is absorbing credits - reduce what you use and carry the rest forward",
     "condition": "standard_credits + carryforward_credits > 0 and L20 == L13",
     "message": "Credits have been reduced to the minimum tax floor. Oregon states it plainly: minimum "
                "tax can't be 'reduced, paid, or otherwise satisfied through the use of any tax credit' "
                "(ORS 317.090), and the clamp is printed independently at lines 18, 20 AND 22. ⚠ The "
                "Schedule OR-ASC-CORP ordering rule matters here: 'If your total standard and "
                "carryforward credits would reduce your tax below the minimum tax, you need to reduce "
                "how much you're using' — and you list credits in the order you want them used. Claiming "
                "the full amount of a credit that cannot be absorbed may DESTROY carryforward the "
                "taxpayer would otherwise keep. Review which credits to use and in what order.",
     "notes": "⚠ The failure mode is not a wrong tax - the tax is right either way. It is a destroyed "
              "carryforward, which shows up in a later year and is hard to trace back."},
    {"diagnostic_id": "D_OR20_MIN_TAX_FILING_GROUP", "severity": "warning",
     "title": "⚠ Minimum tax is measured on the FILING GROUP, once per return",
     "condition": "in_consolidated_federal == True",
     "message": "The minimum tax is based on Oregon sales of the affiliated group filing the Oregon "
                "return, and OAR 150-317-0170(1)(a) is explicit: 'Only one minimum tax is charged per "
                "return, regardless of the number of corporations in the group that are doing business "
                "in Oregon.' ⚠ Do not compute a minimum tax per affiliate and add them. ⚠ Note also that "
                "the filing group is NARROWER than the affiliated group — insurance affiliates are a "
                "mandatory exclusion, and Oregon is water's-edge structurally with no election and no "
                "80/20 rule.",
     "notes": "Summing per-affiliate minimums is the natural wrong implementation and can multiply the "
              "figure by the number of members."},
    {"diagnostic_id": "D_OR20_MIN_TAX_SALES_COUNTERFACTUAL", "severity": "warning",
     "title": "⚠ 'Oregon sales' for a non-apportioning corporation is a counterfactual",
     "condition": "is_apportioning != True and oregon_sales_of_filing_group != 0",
     "message": "ORS 317.090(1)(a)(B) defines Oregon sales for a corporation that does not apportion as "
                "'the total sales in this state that the taxpayer WOULD HAVE HAD ... IF the taxpayer were "
                "required to apportion' — a counterfactual computation, not a simple sum of federal "
                "lines. ⚠ The instructions' Form 1120 line list (1c, 5–10) is introduced with "
                "'Generally' and is expressly NON-EXCLUSIVE, so it is a safe harbour rather than the "
                "rule. ⚠ Business done with or for members of an agricultural cooperative is excluded "
                "(ORS 317.090(1)(b)).",
     "notes": "A 'Generally' list read as the definition is how a safe harbour becomes a wrong answer."},
    {"diagnostic_id": "D_OR20_NOL_INTERVENING_INCOME", "severity": "warning",
     "title": "⚠⚠ Oregon reduces a loss by intervening income even in years it was not claimed",
     "condition": "net_loss_deduction != 0",
     "message": "ORS 317.476(4)(b): the deductible Oregon net loss is the prior-year loss 'REDUCED BY THE "
                "NET INCOME (computed without the Oregon net loss deduction) OF ANY INTERVENING TAXABLE "
                "YEAR OR YEARS'. ⚠⚠ That happens WHETHER OR NOT the deduction was claimed in those "
                "years, so a carryforward schedule that tracks only amounts USED will OVERSTATE what "
                "remains. ⚠ Oregon is not federal here in four ways: the carryforward is FIFTEEN years "
                "rather than indefinite; there is NO 80%-of-income limitation; the earliest loss must be "
                "exhausted first; and there is no carryback at all unless the corporation is engaged in "
                "crop production, animal production or aquaculture (ORS 317.346). REITs get no deduction "
                "under this section at all.",
     "notes": "⚠ (4)(b) is stronger than FIFO ordering and is the single most likely thing a shared "
              "multi-state NOL engine will get wrong."},
    {"diagnostic_id": "D_OR20_LINE1_START_POINT", "severity": "warning",
     "title": "⚠ This federal return type does not start at Form 1120 line 28",
     "condition": "federal_return_type not in ('1120', '')",
     "message": "Oregon's line 1 normally takes federal Form 1120 line 28 — taxable income BEFORE net "
                "operating loss and special deductions. ⚠ Five documented exceptions: agricultural and "
                "horticultural co-operatives begin at Form 1120-C LINE 25a; an IC-DISC formed on or "
                "before 1 January 2014 enters total commissions received from Form 1120-IC-DISC Schedule "
                "B; exempt organizations with unrelated business income attach Form 990-T; homeowners' "
                "associations use Form 1120-H (gross nonexempt income less directly-related deductions "
                "less the $100 specific deduction, with net capital gains included and given NO special "
                "treatment); and ⚠⚠ a REMIC files Form OR-20-INC, NOT this form. Confirm the start point "
                "before relying on the computed return.",
     "notes": "One of the five sends the filer to a different Oregon form entirely."},
    {"diagnostic_id": "D_OR20_IC_DISC_TWO_RULES", "severity": "warning",
     "title": "⚠ IC-DISC: the 2.5% rate and the minimum-tax exemption are DIFFERENT rules",
     "condition": "is_ic_disc not in ('', None)",
     "message": "Two provisions are easily conflated and have different entity tests. ORS 317.283(2)(a) "
                "imposes a 2.5 PERCENT RATE on 'any commission received by the domestic international "
                "sales corporation' — any DISC formed on or before 1 January 2014. ORS 317.635(2) instead "
                "EXEMPTS an INTEREST CHARGE DISC formed on or before that date from 'the tax imposed "
                "under ORS 317.090' — the minimum tax. ⚠ A DISC may qualify for one and not the other. "
                "⚠ An IC-DISC formed AFTER 1 January 2014 gets neither, is disregarded to the extent of "
                "related-party transactions, and files normally. ⚠⚠ Its due date is unique — the 15th "
                "day of the month following the federal due date — and NO EXTENSIONS are allowed.",
     "notes": "⚠ The research pass cited the two statutes jointly for the rate; the verification pass "
              "split them. Bundling them gives a DISC an exemption it may not have."},
    {"diagnostic_id": "D_OR20_LOCAL_TAXES_DEFERRED", "severity": "error",
     "title": "⚠ Portland / Multnomah / Metro business taxes are not supported",
     "condition": "has_portland_metro_nexus == True",
     "message": "This return has a Portland, Multnomah County or Metro filing obligation. Those are "
                "separate local returns and are RED-DEFERRED in this version (campaign D-25, O3): the "
                "Portland/Multnomah Combined Business Tax, the Metro Supportive Housing Services tax, and "
                "the Multnomah County Business Income Tax. ⚠ They are NOT computed from the OR-20 and "
                "must be prepared outside Delvio. C-corp local forms are not e-file mandated until "
                "TY2027, so the deferral does not block filing — but the obligation is real and missing "
                "it is the taxpayer's exposure, not ours.",
     "notes": "O3 - RED-deferred with the three forms NAMED, so the refusal tells the preparer exactly "
              "what they still owe."},
    {"diagnostic_id": "D_OR20_CODE_LABEL_MATCHING", "severity": "info",
     "title": "⚠⚠ Oregon's corporate and individual code namespaces overlap and diverge",
     "condition": "True",
     "message": "Form OR-20's Appendix A carries 93 codes. 39 of the 67 non-carryforward codes also exist "
                "in Publication OR-CODES' individual list — and 25 of those are hazardous: 23 mean "
                "DIFFERENT things under the same number, and 2 (338, 344) are near-twins with different "
                "labels for the same statutory item. ⚠⚠ Worse, at least NINE of the sixteen apparently "
                "safe rows FAIL a naive string-equality test, because OR-20's Appendix A appends an ORS "
                "citation to every credit label that Pub. OR-CODES omits. Delvio matches on NORMALISED "
                "labels — parenthetical citation stripped, case folded, whitespace and em-dash suffixes "
                "collapsed — never on raw equality.",
     "notes": "⚠ Do NOT reuse load_or_pte.py's collision constants: they describe the 50-code OR-20-S "
              "surface, where the like-for-like count is 12 rather than 25."},
    {"diagnostic_id": "D_OR20_CONSOLIDATED_ALL_THREE", "severity": "warning",
     "title": "A consolidated Oregon return requires ALL THREE conditions",
     "condition": "in_consolidated_federal == True and (is_unitary_group != True or "
                  "any_member_oregon_nexus != True)",
     "message": "ORS 317.710(5)(a) requires a consolidated Oregon return only when the corporations are "
                "(1) included in a consolidated FEDERAL return, (2) members of the same UNITARY group, "
                "and (3) at least one is doing business in Oregon or has Oregon-source income. ⚠ All "
                "three, not any. Filing a consolidated Oregon return without the unitary relationship — "
                "or filing separately when it exists — changes both the apportionment and the single "
                "group minimum tax.",
     "notes": "Federal consolidation alone is the natural wrong trigger."},
    {"diagnostic_id": "D_OR20_FARM_LTCG_IS_A_REDUCTION", "severity": "info",
     "title": "The farm-liquidation 5% arrives as a line-11 reduction, not as a rate",
     "condition": "farm_liquidation_ltcg != 0",
     "message": "ORS 317.063 taxes qualifying farm-liquidation long-term capital gain at 5 percent "
                "'notwithstanding ORS 317.061' — but Oregon delivers it as a TAX REDUCTION computed on "
                "Schedule OR-FCG-20 and entered at line 11, not by substituting a rate at line 10. "
                "⚠ Four conditions apply, including a 10% ownership interest or § 1231 gain, a farming "
                "entity or farm-use property, a buyer NOT related under IRC § 267, and substantially "
                "complete termination of the interest.",
     "notes": "Substituting the rate at line 10 gives a different — and unfilable — return."},
]

F_SCENARIOS: list[dict] = [
    {"scenario_name": "OR20-A - the two statements of the excise rate agree exactly",
     "scenario_type": "normal", "sort_order": 1,
     "inputs": {"oregon_taxable_income": 1500000},
     "expected_outputs": {"bracket_form": 104000.0, "dor_base_plus_excess": 104000.0},
     "notes": "ORS 317.061 states a bracket (6.6% of the first $1m, 7.6% above); the DOR states "
              "base-plus-excess ($66,000 + 7.6% of the excess). 1,000,000 x 6.6% = 66,000, plus "
              "500,000 x 7.6% = 38,000, giving 104,000 either way. The harness PROVES they agree across "
              "a range rather than assuming it from one figure."},
    {"scenario_name": "OR20-B - at exactly $1,000,000 the base is $66,000",
     "scenario_type": "edge", "sort_order": 2,
     "inputs": {"oregon_taxable_income": 1000000},
     "expected_outputs": {"excise_tax": 66000.0},
     "notes": "The hinge that reconciles the statute's bracket to the DOR's base-plus-excess wording."},
    {"scenario_name": "OR20-C - the minimum-tax ladder at its tier boundaries",
     "scenario_type": "edge", "sort_order": 3,
     "inputs": {"sales": [499999, 500000, 999999, 1000000, 99999999, 100000000]},
     "expected_outputs": {"minimum_tax": [150, 500, 500, 1000, 75000, 100000]},
     "notes": "Twelve tiers, cross-verified against ORS 317.090(2)(a)(A)-(L). The statute expresses the "
              "boundaries as 'less than $500,000' / '$500,000 or more but less than $1 million'; the DOR "
              "as inclusive ranges. Same partition, no gap, no overlap - the harness proves exhaustiveness."},
    {"scenario_name": "OR20-D - a LOSS corporation still owes the minimum tax",
     "scenario_type": "edge", "sort_order": 4,
     "inputs": {"oregon_taxable_income": -400000, "oregon_sales_of_filing_group": 8000000},
     "expected_outputs": {"OR20-10": 0.0, "OR20-13": 7500.0, "OR20-14": 7500.0},
     "notes": "⚠ Calculated tax is zero on a loss, but line 14 takes the GREATER of lines 12 and 13. The "
              "minimum tax is a SALES-based alternative, not a small-taxpayer floor - a large loss-making "
              "corporation can owe $100,000."},
    {"scenario_name": "OR20-E - ⚠⚠ credits cannot reduce tax below the minimum, at three lines",
     "scenario_type": "edge", "sort_order": 5,
     "inputs": {"tax_before_credits": 20000, "standard_credits": 12000, "carryforward_credits": 9000,
                "minimum_tax": 4000},
     "expected_outputs": {"OR20-18": 8000.0, "OR20-20": 4000.0, "credits_absorbed": 5000.0},
     "notes": "⚠⚠ L18 = 20,000 - 12,000 = 8,000 (above the floor). L20 = 8,000 - 9,000 = -1,000, clamped "
              "to 4,000. So 5,000 of credit is absorbed by the floor. ⚠ An unclamped computation would "
              "show -1,000 and the taxpayer would lose the 5,000 of carryforward the ordering rule exists "
              "to preserve. The tax is right either way; the destroyed carryforward is the damage."},
    {"scenario_name": "OR20-F - ⚠ defect D1: plus and minus give different income",
     "scenario_type": "edge", "sort_order": 6,
     "inputs": {"federal_taxable_income": 800000, "total_additions": 150000},
     "expected_outputs": {"line3_face_plus": 950000.0, "line3_instructions_minus": 650000.0},
     "notes": "⚠ A 300,000 swing on this fixture. The face, the arithmetic, and the DOR's own OR-20-INC "
              "instructions for the identically-worded line all say PLUS; only the OR-20 instructions say "
              "MINUS. Three sources to one - build the face."},
    {"scenario_name": "OR20-G - ⚠⚠ O1: TY2025 bonus add-back is ZERO",
     "scenario_type": "edge", "sort_order": 7,
     "inputs": {"federal_bonus_taken": 1000000},
     "expected_outputs": {"oregon_addback": 0.0, "sec_179_state_limit": None},
     "notes": "⚠⚠ ORS 317.010(7)(b) - the ROLLING prong - governs bonus and § 179 because they are "
              "computed in arriving at taxable income. § 168(k) conforms at OBBBA 100%, § 179 at "
              "$2.5m/$4m, and there is NO add-back. Reading prong (a)'s fixed 12/31/2023 date instead "
              "would add back up to 60% of this asset's basis. ⚠ Oregon does NOT share Georgia's "
              "add-back - the harness asserts that on the record."},
    {"scenario_name": "OR20-H - ⚠⚠ TY2026 REFUSES rather than computing",
     "scenario_type": "edge", "sort_order": 8,
     "inputs": {"tax_year": 2026},
     "expected_outputs": {"raises": "CommandError naming SB 1507"},
     "notes": "⚠⚠ SB 1507 § 41 amends ORS 317.010(7) ITSELF, so the staleness tripwire fires on the "
              "conformity rule rather than on a rate. A silent roll-forward would apply TY2025 "
              "depreciation conformity to a year in which Oregon has decoupled."},
    {"scenario_name": "OR20-I - ⚠⚠ NOL: intervening income cuts the loss even in unclaimed years",
     "scenario_type": "edge", "sort_order": 9,
     "inputs": {"loss_year_amount": 500000, "loss_year": 2020, "intervening_net_income": 180000,
                "claim_year": 2025},
     "expected_outputs": {"available_oregon": 320000.0, "available_if_tracking_used_only": 500000.0},
     "notes": "⚠⚠ ORS 317.476(4)(b) reduces the loss by intervening-year NET INCOME whether or not the "
              "deduction was claimed. A schedule tracking only amounts USED reports 500,000 still "
              "available when Oregon allows 320,000 - a 180,000 overstatement that survives until the "
              "Department adjusts it."},
    {"scenario_name": "OR20-J - the fifteen-year carryforward expires; federal would not",
     "scenario_type": "edge", "sort_order": 10,
     "inputs": {"loss_year": 2008, "claim_year": 2025},
     "expected_outputs": {"available": 0.0},
     "notes": "⚠ A 2008 loss expired after 2023. Federal post-TCJA losses carry forward indefinitely and "
              "pre-TCJA ones ran 20 years - Oregon's fifteen is shorter than both, and a shared engine "
              "will keep this loss alive."},
    {"scenario_name": "OR20-K - consolidated filing needs all three conditions",
     "scenario_type": "edge", "sort_order": 11,
     "inputs": {"in_consolidated_federal": True, "is_unitary_group": False,
                "any_member_oregon_nexus": True},
     "expected_outputs": {"consolidated_required": False},
     "notes": "Federal consolidation alone is not enough - the unitary relationship is a separate "
              "statutory test, and filing consolidated without it changes both apportionment and the "
              "single group minimum tax."},
    {"scenario_name": "OR20-L - ⚠⚠ code labels must be matched NORMALISED, never with ==",
     "scenario_type": "edge", "sort_order": 12,
     "inputs": {"corporate_label": "Oregon Cultural Trust contribution (ORS 315.675)",
                "individual_label": "Oregon Cultural Trust contributions"},
     "expected_outputs": {"raw_equality": False, "normalised_equality": True},
     "notes": "⚠⚠ At least NINE of the sixteen 'safe' shared rows fail raw equality, because OR-20's "
              "Appendix A appends an ORS citation that Pub. OR-CODES omits. A raw == mapper rejects more "
              "than half the codes it is supposed to wave through - and then silently treats them as "
              "unmapped."},
]

FORMS: list[dict] = [
    {
        "identity": {
            "form_number": "OR_20",
            "form_title": "Oregon Form OR-20 - Corporation Excise Tax Return (TY2025)",
            "notes": (
                "WO-W05-CCORP; walk closed at campaign D-25. ⚠ This is the Wave-5 form that was reported "
                "as authored and was not - D-29 seeded OR_AP and OR_ASC_CORP, Oregon's SHARED SCHEDULES, "
                "not this return. Oregon's C-corp excise return: federal 1120 line 28 -> OR-ASC-CORP "
                "additions/subtractions -> single-sales-factor apportionment -> the GREATER of a "
                "6.6%/7.6% calculated tax or a twelve-tier minimum tax on FILING-GROUP Oregon sales. "
                "⚠⚠ O1: Oregon depreciation IS federal for TY2025 - bonus and § 179 ride ORS "
                "317.010(7)'s ROLLING prong (b), so § 168(k) conforms at OBBBA 100% and there is NO "
                "add-back; the contrary prong-(a) reading would under-depreciate by up to sixty points "
                "of basis. ⚠⚠ ON THE RECORD: Oregon does NOT share Georgia's bonus add-back. ⚠⚠ The "
                "minimum tax is clamped independently at lines 18, 20 AND 22 and NO credit may reduce it. "
                "⚠ Defect D1: the instructions say line 3 = line 1 minus line 2; the face and two other "
                "sources say plus. ⚠ NOL is fifteen years with no 80% cap and is cut by intervening "
                "income even in unclaimed years. ⚠⚠ TY2026 is BLOCKED - SB 1507 amends the conformity "
                "rule itself."
            ),
        },
        "facts": F_FACTS, "rules": F_RULES, "rule_links": F_RULE_LINKS,
        "lines": F_LINES, "diagnostics": F_DIAGNOSTICS, "scenarios": F_SCENARIOS,
    },
]

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-OR20-MINTAX", "title": "⚠⚠ The minimum tax floor binds at THREE lines, not one",
     "assertion_type": "reconciliation", "entity_types": ["1120"], "status": "draft", "sort_order": 1,
     "description": "⚠⚠ Lines 18, 20 and 22 each carry an independent 'not less than minimum tax' clamp "
                    "on the face, and ORS 317.090 forbids satisfying the minimum with any credit. A "
                    "single clamp at the end produces the same TAX but destroys the carryforward the "
                    "DOR's ordering rule exists to preserve - the preparer is told to reduce how much of "
                    "a credit they use, which is only meaningful if the floor binds where it is applied.",
     "definition": {"rule": "R-OR20-CREDITFLOOR",
                    "check": "L18 >= minimum and L20 >= minimum, clamped independently"}},
    {"assertion_id": "FA-OR20-GREATER", "title": "Line 14 takes the GREATER of calculated and minimum tax",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 2,
     "description": "⚠ The minimum tax is a SALES-based alternative, not a small-taxpayer floor. A "
                    "loss-making corporation with $100 million of Oregon sales owes $100,000, and a "
                    "profitable one can still be on the minimum.",
     "definition": {"rule": "R-OR20-L14", "check": "L14 == max(L12, L13)"}},
    {"assertion_id": "FA-OR20-DEPR", "title": "⚠⚠ Oregon depreciation = federal for TY2025 - ASSERTED",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 3,
     "description": "⚠⚠ Bonus and § 179 ride ORS 317.010(7)'s ROLLING prong (b) because they are computed "
                    "in arriving at taxable income. § 168(k) at OBBBA 100%, § 179 at $2.5m/$4m, NO "
                    "add-back. ⭐ The structurally decisive corroboration is that SB 1507 had to CREATE "
                    "an add-back from TY2026 - surplusage if the fixed date already blocked OBBBA. "
                    "⚠⚠ Oregon does NOT share Georgia's add-back; do not clone it.",
     "definition": {"rule": "R-OR20-DEPR", "check": "bonus add-back == 0; no state 179 limit"}},
    {"assertion_id": "FA-OR20-TY2026", "title": "⚠⚠ TY2026 is a re-authoring event, not a roll-forward",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 4,
     "description": "⚠⚠ SB 1507 § 41 amends ORS 317.010(7) ITSELF, so the staleness tripwire fires on the "
                    "conformity rule rather than on a rate. The engine is built switch-ready for the "
                    "mandatory § 168(k)-as-of-2017-12-01 shadow book, but the switch cannot be thrown "
                    "until SB 1507 is re-verified.",
     "definition": {"rule": "R-OR20-TY2026", "check": "any tax_year >= 2026 raises"}},
    {"assertion_id": "FA-OR20-NOL", "title": "⚠⚠ The Oregon loss is cut by intervening income, claimed or not",
     "assertion_type": "reconciliation", "entity_types": ["1120"], "status": "draft", "sort_order": 5,
     "description": "⚠⚠ ORS 317.476(4)(b) is stronger than FIFO ordering: the loss is reduced by "
                    "intervening-year NET INCOME whether or not the deduction was claimed. A build that "
                    "tracks only amounts USED overstates the carryforward. Fifteen years, no 80% cap, no "
                    "carryback except agriculture, no deduction at all for a REIT.",
     "definition": {"rule": "R-OR20-NOL",
                    "check": "available == loss - intervening net income; 15-year expiry"}},
    {"assertion_id": "FA-OR20-D1", "title": "⚠ Line 3 is built from the FACE, not the instructions",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 6,
     "description": "⚠ The OR-20 instructions say 'line 1 minus line 2' for a line whose own label reads "
                    "'plus', whose inputs are headed 'Additions', and whose sibling form's instructions "
                    "say 'plus'. Three sources to one.",
     "definition": {"rule": "R-OR20-L3", "check": "L3 == L1 + L2"}},
    {"assertion_id": "FA-OR20-CODES", "title": "⚠⚠ Code labels reconcile NORMALISED, never by equality",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 7,
     "description": "⚠⚠ 93 Appendix A codes; 39 shared with the individual namespace; 25 hazardous (23 "
                    "divergent + 2 near-twins). At least NINE of the sixteen 'safe' rows fail raw "
                    "equality because OR-20 appends an ORS citation that Pub. OR-CODES omits. ⚠ Do not "
                    "reuse load_or_pte.py's collision constants - they describe the OR-20-S surface, "
                    "where the like-for-like count is 12 rather than 25.",
     "definition": {"rule": "R-OR20-CODES",
                    "check": "normalised label match; hazardous count == 25"}},
]


class Command(BaseCommand):
    help = ("Load the OR_20 spec (Oregon Corporation Excise Tax Return, TY2025). "
            "Refuses to seed until Ken's Gate-1 SEED approval.")

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad OR_20 spec (Oregon Corporation Excise Tax Return, TY2025)\n"))
        self._load_topics()
        sources = self._load_sources()
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
        """Pinned to the GATE MECHANISM, not the sentinel's value (D-17)."""
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
                "\nREFUSING TO SEED OR_20: not cleared to seed.\n\n"
                "Campaign D-25 closed the Oregon WALK (scope). That is NOT the seed gate. Ken must\n"
                "give the Gate-1 SEED approval DIRECTLY - a relayed approval never opens a human\n"
                "gate.\n\n"
                f"READY_TO_SEED = {READY_TO_SEED} (must be True to proceed)\n\nEmpty:\n  {still_empty}\n"
            )

    def _load_topics(self):
        ct = 0
        for code, name in AUTHORITY_TOPICS:
            if len(name) > 255:
                raise CommandError(f"topic_name for {code!r} is {len(name)} chars - the column is 255 "
                                   "(fails ONLY on the live database; campaign D-17).")
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
        missing = [c for c in EXISTING_SOURCES_TO_REFERENCE
                   if not AuthoritySource.objects.filter(source_code=c).exists()]
        if missing:
            raise CommandError(
                f"Referenced source codes do not resolve: {', '.join(missing)}. A code that does not "
                "resolve becomes a DANGLING REFERENCE - campaign D-25/O4, and D-29 where I made that "
                "mistake myself. Correct the code before seeding."
            )
        for code in EXISTING_SOURCES_TO_REFERENCE:
            sources[code] = AuthoritySource.objects.get(source_code=code)
        self.stdout.write(f"Sources ready: {len(sources)}")
        return sources

    def _upsert_form(self, identity: dict) -> TaxForm:
        form, created = TaxForm.objects.update_or_create(
            form_number=identity["form_number"], jurisdiction=FORM_JURISDICTION,
            tax_year=FORM_TAX_YEAR, version=FORM_VERSION,
            defaults={"form_title": identity["form_title"], "entity_types": FORM_ENTITY_TYPES,
                      "status": FORM_STATUS, "notes": identity["notes"]},
        )
        self.stdout.write(f"{'Created' if created else 'Updated'} {identity['form_number']}")
        return form

    def _upsert_facts(self, form, facts):
        for f in facts:
            f = dict(f)
            FormFact.objects.update_or_create(tax_form=form, fact_key=f.pop("fact_key"), defaults=f)
        self._prune(FormFact.objects.filter(tax_form=form).exclude(
            fact_key__in=[f["fact_key"] for f in facts]), "facts")
        self.stdout.write(f"  {len(facts)} facts")

    def _upsert_rules(self, form, rules_data) -> dict:
        created = {}
        for r in rules_data:
            r = dict(r)
            rule, _ = FormRule.objects.update_or_create(tax_form=form, rule_id=r.pop("rule_id"), defaults=r)
            created[rule.rule_id] = rule
        self._prune(FormRule.objects.filter(tax_form=form).exclude(
            rule_id__in=[r["rule_id"] for r in rules_data]), "rules")
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
        self._prune(FormLine.objects.filter(tax_form=form).exclude(
            line_number__in=[l["line_number"] for l in lines]), "lines")
        self.stdout.write(f"  {len(lines)} lines")

    def _upsert_diagnostics(self, form, diagnostics):
        for d in diagnostics:
            d = dict(d)
            FormDiagnostic.objects.update_or_create(
                tax_form=form, diagnostic_id=d.pop("diagnostic_id"), defaults=d)
        self._prune(FormDiagnostic.objects.filter(tax_form=form).exclude(
            diagnostic_id__in=[d["diagnostic_id"] for d in diagnostics]), "diagnostics")
        self.stdout.write(f"  {len(diagnostics)} diagnostics")

    def _upsert_tests(self, form, scenarios):
        for t in scenarios:
            t = dict(t)
            TestScenario.objects.update_or_create(
                tax_form=form, scenario_name=t.pop("scenario_name"), defaults=t)
        self._prune(TestScenario.objects.filter(tax_form=form).exclude(
            scenario_name__in=[s["scenario_name"] for s in scenarios]), "test scenarios")
        self.stdout.write(f"  {len(scenarios)} test scenarios")

    def _prune(self, qs, label):
        """Delete rows this loader no longer declares (campaign D-16)."""
        n = qs.count()
        if n:
            qs.delete()
            self.stdout.write(self.style.WARNING(f"  pruned {n} stale {label}"))

    def _upsert_form_links(self, sources):
        for sc, fc, lt in AUTHORITY_FORM_LINKS:
            src = sources.get(sc) or AuthoritySource.objects.filter(source_code=sc).first()
            if src:
                AuthorityFormLink.objects.get_or_create(
                    authority_source=src, form_code=fc, link_type=lt, defaults={"note": f"{sc} -> {fc}"})

    def _load_flow_assertions(self):
        for a in FLOW_ASSERTIONS:
            a = dict(a)
            FlowAssertion.objects.update_or_create(assertion_id=a.pop("assertion_id"), defaults=a)
        self.stdout.write(f"  {len(FLOW_ASSERTIONS)} flow assertions")

    def _report_totals(self):
        self.stdout.write("\n" + "=" * 66)
        self.stdout.write("OR_20 loaded (TY2025 ONLY - every figure is TY-keyed).")
        self.stdout.write(f"  OR_20: facts {len(F_FACTS)} / rules {len(F_RULES)} / lines {len(F_LINES)} / "
                          f"diag {len(F_DIAGNOSTICS)} / tests {len(F_SCENARIOS)}")
        self.stdout.write(f"  Flow assertions: {len(FLOW_ASSERTIONS)}")
        self.stdout.write("  !! Oregon depreciation IS federal for TY2025 - asserted, not omitted.")
        self.stdout.write("  !! The minimum tax clamps at lines 18, 20 AND 22; no credit may reduce it.")
        self.stdout.write("  !! TY2026 is BLOCKED - SB 1507 amends ORS 317.010(7) itself.")
        self.stdout.write("=" * 66)
