"""Load the Mississippi Form 83-105 spec - Corporate Income and Franchise Tax Return (TY2025).

WO-W05-CCORP. Mississippi's walk closed at campaign **D-26** (16 items).

═══════════════════════════════════════════════════════════════════════════
⚠⚠ TWO TAXES ON ONE RETURN, AND NEITHER GATES THE OTHER
═══════════════════════════════════════════════════════════════════════════
On the PTE 84-105 the franchise block is hard-gated - the header literally reads
`S CORPORATION FRANCHISE TAX` and line 9 forks by entity type. On the 83-105
the header is the unqualified `FRANCHISE TAX (ROUND TO THE NEAREST DOLLAR)` and
line 9 is `line 4 plus line 8` with NO fork. Booklet p.7, verbatim: "Form 83-110
must be completed by ALL corporations." Booklet p.3: a corporation must file
"even if the corporation is inactive or not otherwise engaged in business."

**The only way out of the franchise block is an EXEMPTION, never an entity type.**
Four exemption routes: exempt organizations with UBTI (leave lines 1-4 blank),
fee-in-lieu projects, Growth and Prosperity areas, and the undefined capital
exemption at 83-110 L17. Three of the four are RED-deferred - see W5/U1/U3/U4.

═══════════════════════════════════════════════════════════════════════════
⚠⚠ S1 - THE $25 FRANCHISE MINIMUM vs THE LINE-4 ZERO FLOOR
═══════════════════════════════════════════════════════════════════════════
**This is NOT the Virginia (D-21) or Maryland (D-20) shape, and Ken did not
decide it by reflex.** There, an instruction book contradicted the statute and
was demonstrably DEFECTIVE. Here **both texts are the Department's own**:

  § 27-13-5(1)(b), verbatim: "In no case shall the franchise tax due for the
  accounting period be less than Twenty-five Dollars ($25.00)."

  83-100 p.16, the DOR's own L4 instruction, verbatim: "Enter the net franchise
  tax due (line 2 minus line 3). IF LINE 3 EQUAL OR EXCEEDS THE AMOUNT SHOWN ON
  LINE 2, ENTER A ZERO."

**RULED (D-26 S1): ship the DOR zero floor**, as a flagged SINGLE-POINT-OF-CHANGE
constant, plus a DOR ticket. **Why the Department wins here and the statute won
in VA/MD:** this is statute-versus-OPERATIONAL-INSTRUCTION, not
statute-versus-error - and DOR runs the approval process this software must pass.
⚠ **It bites every Mississippi bank** (the Bank Share credit is a franchise
credit). One constant changes when the ticket comes back: MS_FRANCHISE_NET_FLOOR.

═══════════════════════════════════════════════════════════════════════════
⚠⚠ S4 - THE RATE LADDER IS KEYED BY TAXPAYER TYPE FROM THE START
═══════════════════════════════════════════════════════════════════════════
A verification-pass finding. § 27-7-5(1)(a) applies the 0/4/5 schedule to "every
resident individual, CORPORATION, association, trust or estate". HB 1 (2025 Reg.
Sess., the "Build Up Mississippi Act") added stepped reductions at
§ 27-7-5(1)(b)(ii) - 3.75% for 2027, 3.5% for 2028, 3.25% for 2029, 3% for 2030
and after - **expressly limited to "all taxable income of INDIVIDUALS in excess
of Ten Thousand Dollars"**. The corporate schedule is the unreduced one and is
NOT on a phase-down ladder.

**So the two schedules diverge on a published timetable from TY2027.** A single
year-keyed table would leak the individual phase-down into corporate returns that
year and go wrong SILENTLY. Encoded keyed NOW, while TY2025 does not yet need it.
The harness PROVES the divergence at TY2027 rather than asserting it.

═══════════════════════════════════════════════════════════════════════════
KEN'S OTHER RULINGS THIS SPEC IMPLEMENTS (campaign D-26)
═══════════════════════════════════════════════════════════════════════════
S2  Underestimate interest is **HALF of one percent per month**, built to the
    FORM FACE. Three DOR sources disagree: the regulation (T35 P3 Subpart 11
    Ch.21 § 101(1)) says "one percent (1%) per month"; booklet p.19 says "1/2 of
    1% per month"; Form 83-305 L15 says "5/10 of 1% per month". Two against one,
    and the face governs. **Ruling, not finding.**
S3  NOL is **TWO periods back, TWENTY forward**, built to statute + booklet.
    ⚠ T35 P3 Subpart 02 Ch.06 § 100 STILL reads "the next five succeeding years"
    - stale text predating the 2001 amendment. Do NOT build to it.

**Scope levers, each NAMING what it refuses:** W2 combined filing -> DETECT and
RED-defer · W3 Form 83-391 (insurance) -> out of scope with a filer-type RED stop
· W4 Form 83-124 (direct accounting) -> RED-defer · W13 Form 83-450 -> out.
⚠ W16: the combined universes are **DISJOINT** - Forms 83-391 and 83-105 cannot
mix - so the detection diagnostic is a PREREQUISITE to any future combined
coding, not an optional extra.

SAFETY GUARD - READY_TO_SEED stays False until Ken's Gate-1 SEED approval.
"""
import math

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
# D-26 approved the walk SCOPE (16 items). That is not the seed gate.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = True   # ⚠ OPENED 2026-08-23 on Ken's DIRECT Gate-1 SEED approval ("seed all three"), given unmediated in session. Pre-flight clean: prod 164 forms, no two-writers hazard, all references resolve.


FORM_JURISDICTION = "MS"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"
FORM_ENTITY_TYPES = ["1120"]

# ───────────────────────────────────────────────────────────────────────────
# FRANCHISE TAX - the phase-out ladder, from the CORPORATE booklet p.3
# (SB 2858, 2016 Reg. Sess.; §§ 27-13-1, 27-13-5, 27-13-7, 27-13-67).
# ⚠ TY2025 = $0.75 is confirmed on THREE independent corporate DOR statements:
# the ladder (p.3), the TAX RATES block (p.5) and the L2 instruction (p.16).
# None => the levy is repealed for that year, not "zero rate". They differ:
# a repealed levy means lines 1-4 do not exist; a zero rate means they compute
# to nothing and the $25 minimum would still bite.
# ───────────────────────────────────────────────────────────────────────────
MS_FRANCHISE_RATE_PER_1000: dict[int, str | None] = {
    2020: "2.00", 2021: "1.75", 2022: "1.50", 2023: "1.25", 2024: "1.00",
    2025: "0.75", 2026: "0.50", 2027: "0.25",
    2028: None,   # "Franchise tax repealed effective January 1, 2028"
}

# 83-100 p.5, verbatim: "$0.75 per $1,000 of capital, OR FRACTIONAL PART THEREOF,
# ... in excess of $100,000 (minimum tax of $25)".
MS_FRANCHISE_CAPITAL_EXEMPTION: dict[int, int] = {2025: 100000}
MS_FRANCHISE_UNIT: dict[int, int] = {2025: 1000}

# ⚠⚠ S1 - THE SINGLE POINT OF CHANGE. Ken ruled the DOR zero floor ships.
# § 27-13-5(1)(b) says the franchise tax due may never be under $25; the DOR's
# own L4 instruction says credits may drive it to zero. Both are DOR text.
# When the DOR ticket comes back, ONE of these two constants changes and nothing
# else in this spec moves.
MS_FRANCHISE_LINE2_MINIMUM: dict[int, int] = {2025: 25}   # printed ON the face at L2
MS_FRANCHISE_NET_FLOOR: dict[int, int] = {2025: 0}        # ⚠ D-26 S1 - DOR L4 instruction
MS_FRANCHISE_NET_FLOOR_BASIS = (
    "83-100 p.16 L4 instruction (DOR operational text). ⚠ § 27-13-5(1)(b) reads the other way "
    "($25 statutory minimum on tax DUE). Ken ruled the Department's operational instruction ships "
    "because DOR runs the approval this software must pass - campaign D-26 S1 - with a DOR ticket "
    "queued. Change THIS constant to 25 if the Department answers for the statute."
)

# ───────────────────────────────────────────────────────────────────────────
# ⚠⚠ S4 - INCOME TAX RATE LADDER, KEYED BY TAXPAYER TYPE **AND** YEAR.
# Each entry: (bracket_width_or_None_for_remainder, rate).
# The corporate ladder is the UNREDUCED § 27-7-5(1)(a) schedule and does not
# move. The individual ladder carries HB 1 (2025)'s § 27-7-5(1)(b)(ii) steps.
# They are equal through TY2026 and DIVERGE from TY2027 - which is precisely
# why a single shared table would fail silently that year.
# ───────────────────────────────────────────────────────────────────────────
MS_RATE_LADDER: dict[str, dict[int, tuple]] = {
    "corporation": {
        2025: ((5000, "0.00"), (5000, "0.04"), (None, "0.05")),
        2026: ((5000, "0.00"), (5000, "0.04"), (None, "0.05")),
        2027: ((5000, "0.00"), (5000, "0.04"), (None, "0.05")),
        2028: ((5000, "0.00"), (5000, "0.04"), (None, "0.05")),
        2029: ((5000, "0.00"), (5000, "0.04"), (None, "0.05")),
        2030: ((5000, "0.00"), (5000, "0.04"), (None, "0.05")),
    },
    # ⚠ NOT used by this form. Present so that the corporate ladder can never be
    # "helpfully" merged with it, and so the harness can PROVE the divergence.
    "individual": {
        2025: ((5000, "0.00"), (5000, "0.04"), (None, "0.05")),
        2026: ((5000, "0.00"), (5000, "0.04"), (None, "0.05")),
        2027: ((5000, "0.00"), (5000, "0.04"), (None, "0.0375")),
        2028: ((5000, "0.00"), (5000, "0.04"), (None, "0.035")),
        2029: ((5000, "0.00"), (5000, "0.04"), (None, "0.0325")),
        2030: ((5000, "0.00"), (5000, "0.04"), (None, "0.03")),
    },
}

# S3 - § 27-7-17(1)(l): two back, twenty forward, for losses after 12/31/2001.
# ⚠⚠ DELIBERATELY ABSENT: the "next five succeeding years" of T35 P3 Subpart 02
# Ch.06 § 100. That regulation predates the 2001 amendment and the same chapter's
# § 102 then cites § 27-7-17(1)(l). The harness FAILS if a 5 appears here.
MS_NOL_CARRYBACK_YEARS: dict[int, int] = {2025: 2}
MS_NOL_CARRYFORWARD_YEARS: dict[int, int] = {2025: 20}

# S2 - built to the FORM FACE (83-305 L15), against the regulation's 1%.
MS_UNDERESTIMATE_INTEREST_MONTHLY: dict[int, str] = {2025: "0.005"}
MS_LATE_PAYMENT_INTEREST_MONTHLY: dict[int, str] = {2025: "0.005"}
MS_LATE_PAYMENT_PENALTY_MONTHLY: dict[int, str] = {2025: "0.005"}
MS_LATE_PAYMENT_PENALTY_CAP: dict[int, str] = {2025: "0.25"}
MS_LATE_FILING_MINIMUM_PENALTY: dict[int, int] = {2025: 100}

# Booklet p.16: "If the current Mississippi income tax liability (LINE 8) is $200
# or less, then estimated income tax payments were not required."
# ⚠ Keyed to LINE 8 - the income tax - never to line 9. The franchise tax never
# triggers estimates.
MS_ESTIMATE_THRESHOLD_LINE8: dict[int, int] = {2025: 200}

# W14 - the corporate-only charitable divergence on 83-122 L7.
MS_CHARITABLE_LIMIT_PCT: dict[int, str] = {2025: "0.20"}
MS_CHARITABLE_CARRYOVER_ALLOWED: dict[int, bool] = {2025: False}

# 83-125 Part I header, verbatim: "ROUND TO FOUR DECIMAL PLACES".
MS_APPORTIONMENT_DECIMALS: dict[int, int] = {2025: 4}

# Scope levers - each names what it refuses (D-26).
MS_DEFERRED_FORMS: tuple = (
    "83-391",   # W3 - insurance company return. OUT of scope, filer-type RED stop.
    "83-124",   # W4 - direct accounting. RED-defer.
    "83-450",   # W13 - out.
)

# ⚠⚠ W16 - the combined universes are DISJOINT. 83-391 filers and 83-105 filers
# CANNOT appear in one combined return. Detection is a PREREQUISITE to any future
# combined coding, not an optional extra.
MS_COMBINED_UNIVERSES_DISJOINT = True


def _yk(table: dict, year: int = FORM_TAX_YEAR):
    if year not in table:
        raise CommandError(f"No TY{year} value in {table!r} - re-verify before extending the year.")
    return table[year]


def _ms_franchise_line2(taxable_capital, year: int = FORM_TAX_YEAR):
    """83-105 L2 `Franchise tax (minimum tax $25)`.

    83-100 p.5, verbatim: "$0.75 per $1,000 of capital, OR FRACTIONAL PART THEREOF,
    of capital surplus, undivided profits and true reserves employed in Mississippi
    in excess of $100,000 (minimum tax of $25)."

    ⚠ "or fractional part thereof" means each PART of a $1,000 unit counts as a
    whole unit - so the unit count is a CEILING, not a truncation. Truncating
    understates the tax on every base that is not an exact multiple of $1,000,
    which is almost all of them.
    """
    rate = _yk(MS_FRANCHISE_RATE_PER_1000, year)
    if rate is None:
        raise CommandError(
            f"The Mississippi franchise tax is REPEALED for TY{year} (SB 2858; effective "
            "January 1, 2028). Lines 1-4 do not exist for that year - this is not a zero rate, "
            "and a zero rate would still carry the $25 minimum."
        )
    exemption = _yk(MS_FRANCHISE_CAPITAL_EXEMPTION, year)
    unit = _yk(MS_FRANCHISE_UNIT, year)
    minimum = _yk(MS_FRANCHISE_LINE2_MINIMUM, year)
    excess = max(0, float(taxable_capital) - exemption)
    units = math.ceil(excess / unit)          # ⚠ "or fractional part thereof"
    computed = units * float(rate)
    return max(float(minimum), computed)


def _ms_franchise_line4(line2, franchise_credits, year: int = FORM_TAX_YEAR):
    """83-105 L4 `Net franchise tax due (line 2 minus line 3)`.

    ⚠⚠ D-26 S1. The DOR L4 instruction governs: "If line 3 equal or exceeds the
    amount shown on line 2, enter a zero." The competing statutory reading
    (§ 27-13-5(1)(b), a $25 floor on tax DUE) would return the minimum instead.
    """
    floor = _yk(MS_FRANCHISE_NET_FLOOR, year)
    return max(float(floor), float(line2) - float(franchise_credits))


def _ms_franchise_line4_statutory_reading(line2, franchise_credits, year: int = FORM_TAX_YEAR):
    """The reading Ken did NOT ship - retained so the harness can prove the two differ.

    § 27-13-5(1)(b): "In no case shall the franchise tax due for the accounting
    period be less than Twenty-five Dollars ($25.00)."
    """
    minimum = _yk(MS_FRANCHISE_LINE2_MINIMUM, year)
    return max(float(minimum), float(line2) - float(franchise_credits))


def _ms_income_tax(taxable_income, year: int = FORM_TAX_YEAR, taxpayer_type: str = "corporation"):
    """83-105 L6 `Income tax`, from the ladder keyed by TAXPAYER TYPE and year (S4).

    83-100 p.16 L6, verbatim: "The rates of tax are: 0% on the first $5,000, 4% on
    the next $5,000 of taxable income; and 5% on taxable income in excess of
    $10,000."
    """
    if taxpayer_type not in MS_RATE_LADDER:
        raise CommandError(
            f"Unknown taxpayer_type {taxpayer_type!r}. The ladder is keyed by taxpayer type "
            "because HB 1 (2025) phases the individual top rate from TY2027 while leaving the "
            "corporate schedule unreduced - campaign D-26 S4."
        )
    ladder = _yk(MS_RATE_LADDER[taxpayer_type], year)
    remaining, tax = max(0.0, float(taxable_income)), 0.0
    for width, rate in ladder:
        if remaining <= 0:
            break
        slice_ = remaining if width is None else min(remaining, width)
        tax += slice_ * float(rate)
        remaining -= slice_
    return tax


def _ms_income_tax_fiscal_blend(taxable_income, months_in_earlier_year, months_in_fiscal_year,
                                earlier_year, later_year, taxpayer_type: str = "corporation"):
    """§ 27-7-5(4) (a)-(e), printed VERBATIM on the corporate L6 instruction.

    (a) compute the full-year tax at the EARLIER calendar year's rates;
    (b) compute the full-year tax at the LATER calendar year's rates;
    (c)/(d) apply the months ratios; (e) add.

    ⚠ For TY2025 this is the IDENTITY on the income tax - the corporate 0/4/5
    schedule has not moved between CY2024, CY2025 and CY2026. It is encoded as a
    real blend anyway: it is one legislative session away from being live, and a
    hard-coded 0/4/5 would fail silently the moment it is not.

    ⚠ This is NOT the franchise proration. That is a different mechanism entirely
    - Form 83-110 line 16, a months-covered/twelve proration of the CAPITAL BASE,
    not a rate blend.
    """
    if months_in_fiscal_year <= 0:
        raise CommandError("months_in_fiscal_year must be positive.")
    tax_a = _ms_income_tax(taxable_income, earlier_year, taxpayer_type)
    tax_b = _ms_income_tax(taxable_income, later_year, taxpayer_type)
    months_later = months_in_fiscal_year - months_in_earlier_year
    return (tax_a * (months_in_earlier_year / months_in_fiscal_year)
            + tax_b * (months_later / months_in_fiscal_year))


def _ms_line19_balance_due(line9, line13, line14, line15, line16, line17, line18):
    """L19 `Total balance due (if line 9 is larger than line 13, add line 14 through line 18)`."""
    if float(line9) <= float(line13):
        return 0.0
    return sum(float(x) for x in (line14, line15, line16, line17, line18))


def _ms_line20_overpayment(line9, line13, line15):
    """L20 `Total overpayment (if line 13 is larger than line 9 plus line 15, subtract line 9
    and line 15 from line 13)`.

    ⚠⚠ THE ASYMMETRY IS NOT A TYPO AND MUST NOT BE "SYMMETRISED". L19 tests
    `line 9 > line 13`; L20 tests `line 13 > line 9 + line 15` and subtracts BOTH.
    So underestimate interest/penalty (L15) nets against an overpayment, while the
    late-payment items (L16-L18) do not. The PTE verification pass confirmed the
    identical asymmetry on the 84-105. Build the two lines exactly as printed.
    """
    if float(line13) <= float(line9) + float(line15):
        return 0.0
    return float(line13) - float(line9) - float(line15)


def _ms_underestimate_interest(underpayment, months, year: int = FORM_TAX_YEAR):
    """83-305 L15 - S2. The FORM FACE rate, half of one percent per month."""
    return float(underpayment) * float(_yk(MS_UNDERESTIMATE_INTEREST_MONTHLY, year)) * months


def _ms_nol_expiry_year(loss_year: int, year: int = FORM_TAX_YEAR) -> int:
    """S3 - twenty periods forward. § 27-7-17(1)(l); booklet pp.9 and 19.

    ⚠ "A short taxable year counts as a taxable year" - so the caller must pass
    PERIODS, not calendar years, where they differ.
    """
    return loss_year + _yk(MS_NOL_CARRYFORWARD_YEARS, year)


AUTHORITY_TOPICS: list[tuple[str, str]] = [
    # Keep under 255 - the loader guards it (campaign D-17, which has bitten this
    # campaign three times in one session on topic_name alone).
    ("ms_corp_franchise_income", "Mississippi Form 83-105: the ungated franchise levy on ALL "
     "corporations, the $0.75/$1,000 TY2025 rate on its phase-out ladder, the $25 minimum against "
     "the DOR line-4 zero floor, and the 0/4/5 income ladder keyed by taxpayer type."),
]

# ⚠⚠ TWO-WRITERS GUARD (D-31): these are OWNED by the seeded MS PTE loaders.
# This spec REFERENCES them and never re-declares them. Re-declaring would make
# this loader a second writer of a row another loader owns.
EXISTING_SOURCES_TO_REFERENCE: list[str] = [
    "MS_CODE_27_13_5",              # the franchise levy, minimum and exemptions
    "MS_ADMIN_CODE_35_PT3",         # Title 35 - apportionment, throwback, the stale NOL chapter
    "MS_2025_FORM_84_161",          # the PTET credit that lands on 83-105 L12
    "MS_2025_FORM_83305_80320",     # estimated tax / underestimate interest
]

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "MS_2025_FORM_83_105", "source_type": "state_form",
        "source_rank": "primary_official", "jurisdiction_code": "MS",
        "title": "2025 Mississippi Form 83-105 - Corporate Income and Franchise Tax Return",
        "citation": "Form 83-105 (2025)", "issuer": "Mississippi Department of Revenue",
        "official_url": "https://www.dor.ms.gov/business/corporate-income-tax",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.5,
        "topics": ["ms_corp_franchise_income"],
        "excerpts": [
            {
                "excerpt_label": "⚠⚠ The franchise block is UNGATED, and line 9 has no fork (verbatim)",
                "excerpt_text": (
                    "Block header: 'FRANCHISE TAX (ROUND TO THE NEAREST DOLLAR)' - unqualified, where the "
                    "PTE 84-105 reads 'S CORPORATION FRANCHISE TAX'. L1 'Taxable capital (from Form 83-110, "
                    "line 18)'; L2 'Franchise tax (minimum tax $25)'; L3 'Franchise tax credit (from Form "
                    "83-401, line 1)'; L4 'Net franchise tax due (line 2 minus line 3)'. L5 'Mississippi net "
                    "taxable income (from Form 83-122, line 30 or Form 83-310, line 5, column C)'; L6 "
                    "'Income tax'; L7 'Income tax credits'; L8 'Net income tax due (line 6 minus line 7)'; "
                    "L9 'Total franchise and income tax (line 4 plus line 8)' - NO entity-type fork. "
                    "Header 'CHECK ALL THAT APPLY': Amended Return / Final Return / Non Profit. 'CHECK ONE': "
                    "100% Mississippi / Multistate Apportioning / Multistate Direct Accounting."
                ),
                "summary_text": "Both taxes always apply on the 83-105; the only way out of the franchise "
                                "block is an exemption, never an entity type. The Non Profit box replaces "
                                "the PTE form's election/composite pair - a C corp cannot elect PTE status.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "⚠⚠ The L19/L20 asymmetry - printed, deliberate, not to be symmetrised",
                "excerpt_text": (
                    "L19 'Total balance due (if line 9 is larger than line 13, add line 14 through line "
                    "18)'. L20 'Total overpayment (if line 13 is larger than line 9 PLUS LINE 15, subtract "
                    "line 9 AND LINE 15 from line 13)'. So underestimate interest and penalty (L15) net "
                    "against an overpayment while the late-payment items (L16 late payment interest, L17 "
                    "late payment penalty, L18 late filing penalty, minimum income tax penalty $100) do "
                    "not. L12 'Credit for tax paid on an electing Pass-Through Entity Tax Return (from Form "
                    "84-161, line 3D; must attach K-1(s))' - the ONLY place the PTET touches a C "
                    "corporation, and it is a payment credit, never an income exclusion."
                ),
                "summary_text": "⚠ The PTE verification pass confirmed the identical asymmetry on the "
                                "84-105. Build both lines exactly as printed.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "⚠ The Fee-In-Lieu checkbox that appears in NO instruction",
                "excerpt_text": (
                    "An unlabelled-in-instructions 'Fee-In-Lieu' checkbox is printed at x~331.2, y~314.7, "
                    "immediately left of the line-2 amount box. Full-text search of all 24 pages of the "
                    "83-100 booklet (whitespace-normalised) returns ZERO hits for 'fee-in-lieu' or 'fee in "
                    "lieu' - absence independently re-proved on the verification pass. The form face gives "
                    "no computation. § 27-13-5(3)(a) is an EXEMPTION, not an apportionment rule: 'A "
                    "corporation that has negotiated a fee-in-lieu as defined in Section 57-75-5 shall not "
                    "be subject to the tax levied by this section on such project; however, the fee-in-lieu "
                    "payment shall be otherwise treated in the same manner as the payment of franchise "
                    "taxes.' The single-sales-factor override is at § 27-13-5(3)(b)(iv). What remains "
                    "unstated anywhere is HOW the project is carved out of the 83-110 capital base."
                ),
                "summary_text": "U1, narrowed but not closed: the statutory mechanic is established, the "
                                "carve-out arithmetic is not. RED-defer with the verbatim absence note.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        # ⚠ source_type corrected 2026-08-25 (campaign D-41, Ken: "correct and reseed"). Was "state_instructions" (plural),
        #   which is NOT a SourceType member; Django does not enforce choices on update_or_create.
        "source_code": "MS_2025_BOOKLET_83_100", "source_type": "state_instruction",
        "source_rank": "primary_official", "jurisdiction_code": "MS",
        "title": "2025 Mississippi Form 83-100 - Corporate Income and Franchise Tax Instructions",
        "citation": "Form 83-100 (2025)", "issuer": "Mississippi Department of Revenue",
        "official_url": "https://www.dor.ms.gov/business/corporate-income-tax",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.0,
        "topics": ["ms_corp_franchise_income"],
        "excerpts": [
            {
                "excerpt_label": "⚠⚠ S1 - the L4 zero floor, in the Department's own words",
                "excerpt_text": (
                    "p.16, L4, verbatim: 'Enter the net franchise tax due (line 2 minus line 3). IF LINE 3 "
                    "EQUAL OR EXCEEDS THE AMOUNT SHOWN ON LINE 2, ENTER A ZERO.' p.16, L2: 'For tax year "
                    "2025, the franchise tax rate is $0.75 per $1,000 of capital in excess of $100,000 "
                    "(minimum tax of $25).' p.5, TAX RATES: 'Franchise Tax: $0.75 per $1,000 of capital, or "
                    "fractional part thereof, of capital surplus, undivided profits and true reserves "
                    "employed in Mississippi in excess of $100,000 (minimum tax of $25).' p.17, L8: 'If "
                    "line 7 equals or exceeds the amount shown on line 6, enter a zero.' "
                    "⚠ This collides head-on with § 27-13-5(1)(b): 'In no case shall the franchise tax due "
                    "for the accounting period be less than Twenty-five Dollars ($25.00).' BOTH texts are "
                    "the Department's own - this is statute-versus-operational-instruction, NOT "
                    "statute-versus-error."
                ),
                "summary_text": "⚠⚠ D-26 S1: ship the zero floor as a flagged single-point-of-change "
                                "constant + a DOR ticket, because DOR runs the approval the software must "
                                "pass. It bites every Mississippi bank.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "The 0/4/5 ladder and the § 27-7-5(4) proration, printed in full",
                "excerpt_text": (
                    "p.5 TAX RATES: 'Income Tax: 0% on the first $5,000 of taxable income and 4% on the "
                    "next $5,000 of taxable income and 5% on all taxable income in excess of $10,000.' "
                    "p.16 L6 repeats it and then prints § 27-7-5(4) verbatim: '(a) Computing for the full "
                    "fiscal year the amount of tax that would be due under the rates in effect for the "
                    "calendar year in which the fiscal year begins; and (b) ... in which the fiscal year "
                    "ends; and (c) Applying to the tax computed under paragraph (a) the ratio which the "
                    "number of months falling within the earlier calendar year bears to the total number of "
                    "months in the fiscal year; and (d) ... the later calendar year ...; and (e) Adding to "
                    "the tax determined under paragraph (c) the tax determined under paragraph (d).'"
                ),
                "summary_text": "The proration is a real months-ratio rate blend. Dormant on the income tax "
                                "for TY2025 (the corporate schedule has not moved) - encoded anyway.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "⚠⚠ S3 - NOL two back / twenty forward, and the stale five-year regulation",
                "excerpt_text": (
                    "p.9 and p.19, verbatim: 'For any taxable year ending after December 31, 2001, the "
                    "period for net operating loss carrybacks and net operating loss carryovers is TWO "
                    "PERIODS BACK AND TWENTY PERIODS FORWARD. This is NOT in accordance with federal "
                    "carryback and carryover provisions... A short taxable year counts as a taxable year. A "
                    "taxpayer may elect to forgo the carryback on Form 83-155. ONCE THIS ELECTION IS MADE, "
                    "IT CANNOT BE CHANGED. Form 83-155 must be completed and attached or an NOL deduction "
                    "will not be allowed.' p.19: the election is made 'ON THE ORIGINAL RETURN FILING'. p.6: "
                    "'Form 83-155 must be filed with an amended return in order to claim a net operating "
                    "loss deduction.' 83-122 L28 instruction, p.18: 'Mississippi does not conform to "
                    "federal net operating loss rules.' ⚠ Title 35 Part III Subpart 02 Ch.06 § 100 STILL "
                    "reads 'the next FIVE succeeding years' - text predating the 2001 amendment; the same "
                    "chapter's § 102 then cites § 27-7-17(1)(l). Build to statute + booklet."
                ),
                "summary_text": "⚠⚠ D-26 S3. Also corporate-only: T35 § 101 excludes regulated investment "
                                "companies and life/mutual insurers other than marine from the carryover.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "⚠ ALL corporations file, and all complete Form 83-110",
                "excerpt_text": (
                    "p.7, verbatim: 'Form 83-110 must be completed by all corporations to indicate the "
                    "amount of capital of the corporation.' And: 'The section of Form 83-110 concerning the "
                    "assessed values of all real and personal property in Mississippi must be completed by "
                    "all corporations.' p.3, WHO MUST FILE: 'Every corporation domesticated or qualified to "
                    "do business in Mississippi must file a return EVEN IF THE CORPORATION IS INACTIVE OR "
                    "NOT OTHERWISE ENGAGED IN BUSINESS. Such corporation will remain subject to the filing "
                    "requirements until it is officially dissolved or withdrawn through the Office of the "
                    "Mississippi Secretary of State.' p.10: 'Exempt corporate organizations file Form "
                    "83-105 and any necessary supplemental schedules. THESE ORGANIZATIONS ARE NOT SUBJECT "
                    "TO THE FRANCHISE TAX LEVY AND SHOULD LEAVE LINES 1 THROUGH 4 BLANK.' p.16: 'If the "
                    "current Mississippi income tax liability (line 8) is $200 or less, then estimated "
                    "income tax payments were not required.'"
                ),
                "summary_text": "The franchise levy is ungated. Exemption, not entity type, is the only way "
                                "out - and the exempt-organization route says BLANK, not zero.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MS_CODE_27_7_5_HB1_2025", "source_type": "state_statute",
        "source_rank": "primary_official", "jurisdiction_code": "MS",
        "title": "Miss. Code Ann. § 27-7-5 as amended by HB 1 (2025 Reg. Sess.) - the rate schedule",
        "citation": "Miss. Code Ann. § 27-7-5(1)(a), (1)(b)(ii), (4)",
        "issuer": "Mississippi Legislature", "official_url": "https://billstatus.ls.state.ms.us/",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["ms_corp_franchise_income"],
        "excerpts": [{
            "excerpt_label": "⚠⚠ S4 - the corporate and individual schedules DIVERGE from TY2027",
            "excerpt_text": (
                "§ 27-7-5(1)(a) imposes the schedule 'upon the entire net income of every resident "
                "individual, CORPORATION, association, trust or estate' - the corporate schedule is the "
                "UNREDUCED 0/4/5. HB 1 (2025 Reg. Sess.), the 'Build Up Mississippi Act', added stepped "
                "reductions at § 27-7-5(1)(b)(ii) - 3.75% for 2027, 3.5% for 2028, 3.25% for 2029, 3% for "
                "2030 and after - expressly limited to 'all taxable income of INDIVIDUALS in excess of Ten "
                "Thousand Dollars ($10,000.00)'. § 27-7-5(4), the fiscal-year proration, is retained. "
                "⚠ The research pass's FindLaw codification was stamped 'Current as of January 01, 2025' "
                "and predated the session; the verification pass read HB 1 in its as-sent-to-Governor text "
                "and confirmed all three points."
            ),
            "summary_text": "⚠⚠ Because the two schedules now diverge on a PUBLISHED timetable, the rate "
                            "table must be keyed by taxpayer type as well as year. A single year-keyed "
                            "table leaks the individual phase-down into corporate returns from TY2027.",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "MS_CODE_27_7_17_NOL", "source_type": "state_statute",
        "source_rank": "primary_official", "jurisdiction_code": "MS",
        "title": "Miss. Code Ann. § 27-7-17(1)(l) - net operating loss carryback and carryover",
        "citation": "Miss. Code Ann. § 27-7-17(1)(l)", "issuer": "Mississippi Legislature",
        "official_url": "https://law.justia.com/codes/mississippi/title-27/chapter-7/",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["ms_corp_franchise_income"],
        "excerpts": [{
            "excerpt_label": "S3 - two back, twenty forward, and the irrevocable election",
            "excerpt_text": (
                "Carryback to 'each of the two (2) taxable years preceding' and carryover to 'each of the "
                "twenty (20) taxable years following', with an election to 'relinquish the entire carryback "
                "period', for losses arising after 12/31/2001. The booklet adds the ordering rule: a NOL is "
                "carried 'to each of the two (2) taxable years preceding the year of the NOL, STARTING WITH "
                "THE EARLIEST, and then to each of the twenty (20) tax years following the year of the NOL, "
                "until the NOL is exhausted or the carry forward period expires.'"
            ),
            "summary_text": "The statute and both booklets agree on 2/20. Only the stale 1990s regulation "
                            "says five, and its own sibling section cites this statute.",
            "is_key_excerpt": True,
        }],
    },
]

AUTHORITY_FORM_LINKS: list[tuple] = [
    ("MS_2025_FORM_83_105", "MS_83105", "governs"),
    ("MS_2025_BOOKLET_83_100", "MS_83105", "governs"),
    ("MS_CODE_27_7_5_HB1_2025", "MS_83105", "governs"),
    ("MS_CODE_27_7_17_NOL", "MS_83105", "governs"),
    ("MS_CODE_27_13_5", "MS_83105", "governs"),
    ("MS_ADMIN_CODE_35_PT3", "MS_83105", "informs"),
    ("MS_2025_FORM_84_161", "MS_83105", "informs"),
    ("MS_2025_FORM_83305_80320", "MS_83105", "informs"),
]

F_FACTS: list[dict] = [
    {"fact_key": "filer_type", "label": "Filer type (corporation / exempt organization with UBTI / insurance)",
     "data_type": "string", "required": True, "sort_order": 1,
     "notes": "⚠ W3: an insurance company files Form 83-391, NOT the 83-105. Filer-type RED stop."},
    {"fact_key": "is_non_profit", "label": "Header 'Non Profit' box - exempt organization with UBTI",
     "data_type": "boolean", "required": False, "sort_order": 2,
     "notes": "Booklet p.10: these organizations 'are not subject to the franchise tax levy and should "
              "leave lines 1 through 4 BLANK.' ⚠ Blank, not zero - a printed zero asserts a computation."},
    {"fact_key": "filing_mode", "label": "'CHECK ONE' - 100% Mississippi / Multistate Apportioning / "
                                        "Multistate Direct Accounting",
     "data_type": "string", "required": True, "sort_order": 3,
     "notes": "⚠ W4: direct accounting routes to Form 83-124, which is RED-deferred."},
    {"fact_key": "is_combined_return", "label": "Combined income tax return (FEIN of reporting corporation)",
     "data_type": "boolean", "required": False, "sort_order": 4,
     "notes": "⚠⚠ W2/W16: DETECT and RED-defer. The combined universes are DISJOINT - 83-391 and 83-105 "
              "filers cannot mix - so detection is a PREREQUISITE to any future combined coding."},
    {"fact_key": "combined_reporting_fein", "label": "FEIN of the reporting corporation (combined)",
     "data_type": "string", "required": False, "sort_order": 5},
    {"fact_key": "taxable_capital", "label": "L1 Taxable capital (Form 83-110, line 18)",
     "data_type": "decimal", "required": False, "sort_order": 6,
     "notes": "Form 83-110 must be completed by ALL corporations (booklet p.7)."},
    {"fact_key": "fee_in_lieu_checked", "label": "L2 'Fee-In-Lieu' checkbox",
     "data_type": "boolean", "required": False, "sort_order": 7,
     "notes": "⚠ U1/W5: this checkbox appears NOWHERE in the 24-page booklet. § 27-13-5(3)(a) exempts the "
              "project from the levy and § 27-13-5(3)(b)(iv) allows a single sales factor, but HOW the "
              "project is carved out of the 83-110 capital base is unstated on any DOR form. RED-defer."},
    {"fact_key": "franchise_credits", "label": "L3 Franchise tax credit (Form 83-401, line 1)",
     "data_type": "decimal", "required": False, "sort_order": 8,
     "notes": "⚠⚠ S1: the Bank Share credit lands here, which is why the L4 floor question bites every "
              "Mississippi bank."},
    {"fact_key": "capital_exemption_83110_l17", "label": "83-110 L17 capital exemption (undefined on the form)",
     "data_type": "decimal", "required": False, "sort_order": 9,
     "notes": "⚠ U3/U4/W5: the Growth and Prosperity route (§ 27-13-5(4)) and an undefined capital "
              "exemption both land here. Direct-entry + RED carrying the verbatim absence note."},
    {"fact_key": "loan_recharacterisation_83110_l4", "label": "83-110 L4 loan recharacterisation",
     "data_type": "decimal", "required": False, "sort_order": 10,
     "notes": "⚠ W15 (verification-pass find): a regulation the research pass missed governs this line. "
              "Direct-entry + RED when non-zero."},
    {"fact_key": "ms_net_taxable_income", "label": "L5 Mississippi net taxable income (83-122 L30 / 83-310 L5C)",
     "data_type": "decimal", "required": False, "sort_order": 11},
    {"fact_key": "income_tax_credits", "label": "L7 Income tax credits (83-401 L3 / 83-310 L5B)",
     "data_type": "decimal", "required": False, "sort_order": 12,
     "notes": "⚠ W9: the L24 credit-addback loop is direct-entry WITH SOLVER ASSIST, never silent."},
    {"fact_key": "taxpayer_type", "label": "Taxpayer type driving the rate ladder",
     "data_type": "string", "required": False, "sort_order": 13,
     "notes": "⚠⚠ S4: always 'corporation' on this form. Present because the ladder MUST be keyed - HB 1 "
              "phases the individual top rate from TY2027 and a shared table would leak it here."},
    {"fact_key": "fiscal_year_months_earlier", "label": "§ 27-7-5(4) months falling in the earlier calendar year",
     "data_type": "integer", "required": False, "sort_order": 14},
    {"fact_key": "fiscal_year_months_total", "label": "§ 27-7-5(4) total months in the fiscal year",
     "data_type": "integer", "required": False, "sort_order": 15},
    {"fact_key": "prior_year_overpayment", "label": "L10 Overpayments from prior year",
     "data_type": "decimal", "required": False, "sort_order": 16},
    {"fact_key": "estimated_and_extension_payments", "label": "L11 Estimated tax payments and payment with extension",
     "data_type": "decimal", "required": False, "sort_order": 17},
    {"fact_key": "pte_credit_84161", "label": "L12 Credit for tax paid on an electing PTE return (84-161 L3D)",
     "data_type": "decimal", "required": False, "sort_order": 18,
     "notes": "⚠ The ONLY place the PTET touches a C corporation, and it is a PAYMENT CREDIT, never an "
              "income exclusion. A C corp cannot make the § 84-381 election but CAN receive the credit. "
              "K-1(s) must be attached."},
    {"fact_key": "underestimate_interest_83305", "label": "L15 Interest and penalty on underestimated income tax (83-305 L19)",
     "data_type": "decimal", "required": False, "sort_order": 19,
     "notes": "⚠ S2: half of one percent per month, built to the FORM FACE. ⚠ Keyed to LINE 8 - the income "
              "tax - never line 9. The franchise tax never triggers estimates."},
    {"fact_key": "late_payment_interest", "label": "L16 Late payment interest",
     "data_type": "decimal", "required": False, "sort_order": 20},
    {"fact_key": "late_payment_penalty", "label": "L17 Late payment penalty",
     "data_type": "decimal", "required": False, "sort_order": 21,
     "notes": "½% per month, not to exceed 25% in the aggregate."},
    {"fact_key": "late_filing_penalty", "label": "L18 Late filing penalty (minimum income tax penalty $100)",
     "data_type": "decimal", "required": False, "sort_order": 22},
    {"fact_key": "overpayment_to_next_year", "label": "L21 Overpayment credited to next year",
     "data_type": "decimal", "required": False, "sort_order": 23},
    {"fact_key": "nol_forgo_carryback_elected", "label": "83-155 'State election to forgo carryback'",
     "data_type": "boolean", "required": False, "sort_order": 24,
     "notes": "⚠ Made ON THE ORIGINAL RETURN, and 'once this election is made, it cannot be changed.'"},
    {"fact_key": "nol_available", "label": "83-155 Part I L1 Available NOL",
     "data_type": "decimal", "required": False, "sort_order": 25},
    {"fact_key": "aviation_asset_regime", "label": "⚠ W10 aviation dual-regime flag - PER ASSET",
     "data_type": "string", "required": False, "sort_order": 26,
     "notes": "⚠ W10: the aviation exception is a PER-ASSET election, not a return-level one. Carries real "
              "client-advice exposure and the same trap as PTE W4."},
    {"fact_key": "industry_apportionment_type", "label": "⚠ W6 special-industry apportionment type",
     "data_type": "string", "required": False, "sort_order": 27,
     "notes": "⚠ W6: three industry divergences are RED-deferred; boxes 1-3 compute as printed."},
]

F_RULES: list[dict] = [
    {"rule_id": "R-MS83105-L2", "title": "L2 Franchise tax - $0.75/$1,000 above $100,000, minimum $25",
     "rule_type": "calculation",
     "formula": "L2 = max(25, ceil(max(0, taxable_capital - 100000) / 1000) * 0.75)",
     "inputs": ["taxable_capital"], "outputs": ["L2"], "sort_order": 1,
     "description": "83-100 p.5: '$0.75 per $1,000 of capital, OR FRACTIONAL PART THEREOF ... in excess of "
                    "$100,000 (minimum tax of $25).' ⚠ 'or fractional part thereof' makes the unit count a "
                    "CEILING - truncating understates the tax on every base that is not an exact multiple "
                    "of $1,000. TY2025 = $0.75 confirmed on three independent corporate DOR statements; the "
                    "rate is on a phase-out ladder ($1.00 -> 0.75 -> 0.50 -> 0.25 -> repealed 1 Jan 2028)."},
    {"rule_id": "R-MS83105-L4", "title": "⚠⚠ L4 Net franchise tax - the DOR ZERO FLOOR (D-26 S1)",
     "rule_type": "calculation", "formula": "L4 = max(MS_FRANCHISE_NET_FLOOR, L2 - franchise_credits)",
     "inputs": ["L2", "franchise_credits"], "outputs": ["L4"], "sort_order": 2,
     "description": "⚠⚠ Two DOR texts, both the Department's own. § 27-13-5(1)(b): 'In no case shall the "
                    "franchise tax due for the accounting period be less than Twenty-five Dollars.' The "
                    "83-100 p.16 L4 instruction: 'If line 3 equal or exceeds the amount shown on line 2, "
                    "enter a zero.' Ken ruled (D-26 S1) the Department's operational instruction ships, "
                    "because DOR runs the approval this software must pass - the opposite of the VA/MD "
                    "answer, and deliberately so: there the booklet was DEFECTIVE, here it is merely "
                    "operational. Shipped as a single-point-of-change constant with a DOR ticket queued. "
                    "⚠ Bites every Mississippi bank, via the Bank Share franchise credit."},
    {"rule_id": "R-MS83105-L6", "title": "⚠ L6 Income tax - the 0/4/5 ladder KEYED BY TAXPAYER TYPE",
     "rule_type": "calculation",
     "formula": "L6 = ladder(taxpayer_type, year)(ms_net_taxable_income); corporate = 0% first 5,000 / "
                "4% next 5,000 / 5% above 10,000",
     "inputs": ["ms_net_taxable_income", "taxpayer_type"], "outputs": ["L6"], "sort_order": 3,
     "description": "⚠⚠ D-26 S4. § 27-7-5(1)(a) names 'corporation' and the corporate schedule is the "
                    "UNREDUCED one. HB 1 (2025)'s reductions at § 27-7-5(1)(b)(ii) are expressly limited to "
                    "INDIVIDUALS and step 3.75/3.5/3.25/3% from TY2027. The two schedules therefore diverge "
                    "on a published timetable, and a single year-keyed table would leak the individual "
                    "phase-down into corporate returns from TY2027 - silently. Keyed NOW, while TY2025 does "
                    "not yet need it."},
    {"rule_id": "R-MS83105-PRORATE", "title": "§ 27-7-5(4) fiscal-year rate blend, (a) through (e)",
     "rule_type": "calculation",
     "formula": "tax = tax_at_earlier_rates * (months_earlier/months_total) + "
                "tax_at_later_rates * (months_later/months_total)",
     "inputs": ["ms_net_taxable_income", "fiscal_year_months_earlier", "fiscal_year_months_total"],
     "outputs": ["L6"], "sort_order": 4,
     "description": "Printed VERBATIM on the corporate L6 instruction and matching § 27-7-5(4)(a)-(e) "
                    "word for word. ⚠ For TY2025 this is the IDENTITY on the income tax - the corporate "
                    "0/4/5 schedule has not moved between CY2024, CY2025 and CY2026. Encoded as a real "
                    "blend anyway: it is one legislative session from being live and a hard-coded 0/4/5 "
                    "would fail silently. ⚠ This is NOT the franchise proration, which is a different "
                    "mechanism entirely - 83-110 line 16, a months/twelve proration of the CAPITAL BASE."},
    {"rule_id": "R-MS83105-L9", "title": "L9 Total franchise and income tax - NO entity-type fork",
     "rule_type": "calculation", "formula": "L9 = L4 + L8", "inputs": ["L4", "L8"], "outputs": ["L9"],
     "sort_order": 5,
     "description": "⚠ The structural delta from the PTE 84-105, where L9 forks by entity type. Here the "
                    "face reads 'Total franchise and income tax (line 4 plus line 8)' with no fork, and the "
                    "booklet agrees. Both taxes always apply; the only way out of the franchise block is an "
                    "exemption. L8 carries its own zero floor: 'If line 7 equals or exceeds the amount "
                    "shown on line 6, enter a zero.'"},
    {"rule_id": "R-MS83105-SETTLE", "title": "⚠⚠ L19/L20 - the printed asymmetry, NOT to be symmetrised",
     "rule_type": "calculation",
     "formula": "L19 = (L9 > L13) ? sum(L14..L18) : 0 ; L20 = (L13 > L9 + L15) ? L13 - L9 - L15 : 0",
     "inputs": ["L9", "L13", "L15"], "outputs": ["L19", "L20"], "sort_order": 6,
     "description": "⚠⚠ L19 tests 'line 9 is larger than line 13'; L20 tests 'line 13 is larger than line 9 "
                    "PLUS LINE 15' and subtracts BOTH. So underestimate interest/penalty nets against an "
                    "overpayment while the late-payment items (L16-L18) do not. The PTE verification pass "
                    "confirmed the identical asymmetry on the 84-105 - it is deliberate, not a typo. Build "
                    "the two lines exactly as printed; do not 'symmetrise' them."},
    {"rule_id": "R-MS83105-NOL", "title": "⚠ NOL two periods back, twenty forward (D-26 S3)",
     "rule_type": "calculation", "formula": "carryback = 2 periods (earliest first); carryforward = 20 periods",
     "inputs": ["nol_available", "nol_forgo_carryback_elected"], "outputs": ["NOL_USED"], "sort_order": 7,
     "description": "§ 27-7-17(1)(l) and both booklets: 'two periods back and twenty periods forward. This "
                    "is NOT in accordance with federal carryback and carryover provisions.' ⚠ A SHORT "
                    "TAXABLE YEAR COUNTS AS A TAXABLE YEAR - so the ledger counts periods, not calendar "
                    "years. ⚠⚠ The stale Title 35 Part III Subpart 02 Ch.06 § 100 still reads 'the next "
                    "five succeeding years'; it predates the 2001 amendment and its own sibling § 102 cites "
                    "§ 27-7-17(1)(l). Do NOT build to it. ⚠ The forgo election is made on the ORIGINAL "
                    "return and 'cannot be changed'; a carryback requires an AMENDED return."},
    {"rule_id": "R-MS83105-UNDEREST", "title": "⚠ Underestimate interest is HALF of one percent (D-26 S2)",
     "rule_type": "calculation", "formula": "interest = underpayment * 0.005 * months",
     "inputs": ["underestimate_interest_83305"], "outputs": ["L15"], "sort_order": 8,
     "description": "⚠ Three DOR sources, two rates. T35 P3 Subpart 11 Ch.21 § 101(1): 'interest of one "
                    "percent (1%) per month'. 83-100 p.19: '1/2 of 1% per month'. Form 83-305 L15: '5/10 of "
                    "1% per month'. Ken ruled the FORM FACE (D-26 S2). ⚠ Estimates are keyed to LINE 8 - "
                    "the income tax - not line 9: 'If the current Mississippi income tax liability (line 8) "
                    "is $200 or less, then estimated income tax payments were not required.' The franchise "
                    "tax never triggers estimates."},
    {"rule_id": "R-MS83105-CHARITABLE", "title": "W14 - the 20% Mississippi charitable limit, no carryover",
     "rule_type": "limitation", "formula": "deduction = min(contributions, 0.20 * base); carryover = none",
     "inputs": ["ms_net_taxable_income"], "outputs": ["83122_L7"], "sort_order": 9,
     "description": "A corporate-only divergence from federal on 83-122 L7: a 20% Mississippi limit with NO "
                    "carryover, against the federal 10% limit WITH carryover. ⚠ The interaction between a "
                    "federal carryover arriving in a Mississippi year that allows none is not spelled out "
                    "in the booklet - the arithmetic is encoded here and flagged for confirmation."},
]

F_RULE_LINKS: list[tuple] = [
    ("R-MS83105-L2", "MS_2025_BOOKLET_83_100", "governs", "p.5 TAX RATES and p.16 L2 - the rate, the "
     "$100,000 exemption, 'or fractional part thereof', and the $25 minimum."),
    ("R-MS83105-L2", "MS_CODE_27_13_5", "governs", "The franchise levy, the ladder at "
     "§ 27-13-5(1)(a)(ix)-(xi), and the exemption routes at (3)(a) and (4)."),
    ("R-MS83105-L4", "MS_2025_BOOKLET_83_100", "governs", "⚠⚠ D-26 S1 - the L4 zero floor, in the "
     "Department's own operational instruction. This is the text Ken ruled ships."),
    ("R-MS83105-L4", "MS_CODE_27_13_5", "informs", "⚠ § 27-13-5(1)(b) reads the OTHER way - a $25 floor on "
     "tax due. Recorded as the competing authority, not as the shipped rule, with a DOR ticket queued."),
    ("R-MS83105-L6", "MS_CODE_27_7_5_HB1_2025", "governs", "⚠⚠ S4 - § 27-7-5(1)(a) names 'corporation' and "
     "HB 1's reductions are limited to individuals. This is why the ladder is keyed by taxpayer type."),
    ("R-MS83105-L6", "MS_2025_BOOKLET_83_100", "governs", "p.5 and p.16 - the 0/4/5 ladder, twice."),
    ("R-MS83105-PRORATE", "MS_CODE_27_7_5_HB1_2025", "governs", "§ 27-7-5(4)(a)-(e), retained by HB 1 and "
     "printed verbatim on the corporate L6 instruction."),
    ("R-MS83105-L9", "MS_2025_FORM_83_105", "governs", "The face: 'Total franchise and income tax (line 4 "
     "plus line 8)' - no entity-type fork, unlike the PTE 84-105."),
    ("R-MS83105-SETTLE", "MS_2025_FORM_83_105", "governs", "⚠⚠ The printed L19/L20 asymmetry, confirmed "
     "identical on the 84-105 by the PTE verification pass."),
    ("R-MS83105-NOL", "MS_CODE_27_7_17_NOL", "governs", "Two back, twenty forward, with the irrevocable "
     "election to relinquish the carryback."),
    ("R-MS83105-NOL", "MS_ADMIN_CODE_35_PT3", "informs", "⚠ Ch.06 § 100's 'five succeeding years' is STALE "
     "and must not be built; § 101 carries the corporate carve-out (regulated investment companies and "
     "life/mutual insurers other than marine) that the booklets never mention."),
    ("R-MS83105-UNDEREST", "MS_2025_FORM_83305_80320", "governs", "⚠ S2 - Form 83-305 L15 is the form face: "
     "'5/10 of 1% per month'. The regulation's 1% is not built."),
    ("R-MS83105-CHARITABLE", "MS_2025_BOOKLET_83_100", "governs", "W14 - the 20% limit with no carryover, "
     "on 83-122 L7."),
]

F_LINES: list[dict] = [
    {"line_number": "MS83105-2", "description": "L2 Franchise tax (minimum tax $25)",
     "line_type": "calculated", "source_rules": ["R-MS83105-L2"], "sort_order": 1},
    {"line_number": "MS83105-4", "description": "L4 Net franchise tax due - ⚠ DOR zero floor (D-26 S1)",
     "line_type": "calculated", "source_rules": ["R-MS83105-L4"], "sort_order": 2},
    {"line_number": "MS83105-6", "description": "L6 Income tax (0/4/5, keyed by taxpayer type)",
     "line_type": "calculated", "source_rules": ["R-MS83105-L6", "R-MS83105-PRORATE"], "sort_order": 3},
    {"line_number": "MS83105-8", "description": "L8 Net income tax due (L6 - L7, floored at zero)",
     "line_type": "subtotal", "source_rules": ["R-MS83105-L9"], "sort_order": 4},
    {"line_number": "MS83105-9", "description": "L9 Total franchise and income tax (L4 + L8) - no fork",
     "line_type": "subtotal", "source_rules": ["R-MS83105-L9"], "sort_order": 5},
    {"line_number": "MS83105-13", "description": "L13 Total payments (L10 + L11 + L12)",
     "line_type": "subtotal", "source_rules": ["R-MS83105-SETTLE"], "sort_order": 6},
    {"line_number": "MS83105-14", "description": "L14 Net total franchise tax and/or income tax (L9 - L13)",
     "line_type": "calculated", "source_rules": ["R-MS83105-SETTLE"], "sort_order": 7},
    {"line_number": "MS83105-19", "description": "L19 Total balance due - ⚠ asymmetric with L20",
     "line_type": "calculated", "source_rules": ["R-MS83105-SETTLE"], "sort_order": 8},
    {"line_number": "MS83105-20", "description": "L20 Total overpayment - ⚠ nets L15 only, never L16-L18",
     "line_type": "calculated", "source_rules": ["R-MS83105-SETTLE"], "sort_order": 9},
    {"line_number": "MS83105-22", "description": "L22 Overpayment to be refunded (L20 - L21)",
     "line_type": "calculated", "source_rules": ["R-MS83105-SETTLE"], "sort_order": 10},
]

F_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_MS83105_INSURANCE_FILER", "severity": "error",
     "title": "⚠ An insurance company does not file Form 83-105",
     "condition": "filer_type == 'insurance'",
     "message": "Mississippi insurance companies file Form 83-391, not Form 83-105. Form 83-391 is OUT OF "
                "SCOPE for this version (campaign D-26, W3) - this is a filer-type stop, not a warning. "
                "⚠⚠ And the two universes are DISJOINT: an 83-391 filer and an 83-105 filer cannot appear "
                "in one combined return (W16). Prepare this return outside Delvio, or wait for 83-391 "
                "support.",
     "notes": "W3 - out of scope, naming exactly what it refuses."},
    {"diagnostic_id": "D_MS83105_COMBINED_RETURN", "severity": "error",
     "title": "⚠⚠ Combined Mississippi returns are detected but not computed",
     "condition": "is_combined_return == True",
     "message": "This return is marked as a combined income tax return (the unnumbered header line above "
                "line 5 carries the reporting corporation's FEIN). Combined filing is RED-DEFERRED in this "
                "version (campaign D-26, W2). ⚠⚠ Detection is a PREREQUISITE, not a courtesy: the combined "
                "universes are DISJOINT - Forms 83-391 and 83-105 cannot mix (W16) - so any future combined "
                "coding must start from a reliable detection of which universe the group is in. Do not file "
                "a combined Mississippi return from this version.",
     "notes": "⚠ W2 + W16. Ken ruled DETECT and RED-defer, with the disjointness recorded as the reason "
              "detection cannot be skipped."},
    {"diagnostic_id": "D_MS83105_DIRECT_ACCOUNTING", "severity": "error",
     "title": "⚠ Multistate direct accounting (Form 83-124) is not supported",
     "condition": "filing_mode == 'Multistate Direct Accounting'",
     "message": "The header 'CHECK ONE' group selects direct accounting, which routes to Form 83-124. That "
                "form is RED-DEFERRED in this version (campaign D-26, W4). The apportioning and 100%-"
                "Mississippi modes are supported. ⚠ Direct accounting is not a presentation choice - it "
                "changes which income is Mississippi income, so it cannot be approximated by apportioning.",
     "notes": "W4 - RED-defer, naming what it refuses."},
    {"diagnostic_id": "D_MS83105_FEE_IN_LIEU", "severity": "error",
     "title": "⚠ Fee-in-lieu: the statute exempts the project, but no source states the capital carve-out",
     "condition": "fee_in_lieu_checked == True",
     "message": "The line-2 'Fee-In-Lieu' checkbox is ticked. ⚠ THIS CHECKBOX APPEARS NOWHERE IN THE "
                "24-PAGE 83-100 BOOKLET - a full-text search of all 24 pages returns zero hits for "
                "'fee-in-lieu' or 'fee in lieu', and the form face gives no computation. What IS "
                "established: § 27-13-5(3)(a) provides that a corporation with a negotiated fee-in-lieu "
                "'shall not be subject to the tax levied by this section on such project; however, the "
                "fee-in-lieu payment shall be otherwise treated in the same manner as the payment of "
                "franchise taxes', and § 27-13-5(3)(b)(iv) permits a single sales apportionment factor. "
                "What is NOT established anywhere is HOW the project is carved out of the Form 83-110 "
                "capital base. Compute the franchise tax outside Delvio and enter it directly.",
     "notes": "⚠ U1 (narrowed, not closed) / W5 - direct-entry + RED carrying the verbatim absence note."},
    {"diagnostic_id": "D_MS83105_CAPITAL_EXEMPTION_UNDEFINED", "severity": "error",
     "title": "⚠ The 83-110 line-17 capital exemption has no published computation",
     "condition": "capital_exemption_83110_l17 != 0",
     "message": "Form 83-110 line 17 carries a capital exemption that the DOR booklet never defines. Two "
                "routes are known to land here - the Growth and Prosperity (GAP) area exemption at "
                "§ 27-13-5(4) (booklet p.15) and an undefined capital exemption - but neither carries a "
                "published computation. This figure is DIRECT-ENTRY and this return cannot be filed from "
                "Delvio until the exemption is substantiated outside it.",
     "notes": "U3/U4/W5 - direct-entry + RED carrying the verbatim absence note."},
    {"diagnostic_id": "D_MS83105_83110_L4_LOAN", "severity": "error",
     "title": "⚠ Form 83-110 line 4 loan recharacterisation is direct-entry",
     "condition": "loan_recharacterisation_83110_l4 != 0",
     "message": "Form 83-110 line 4 recharacterises certain loans into the capital base under a regulation "
                "the original research pass missed and the verification pass recovered (campaign D-26, "
                "W15). The amount is DIRECT-ENTRY in this version. Verify it against the regulation before "
                "filing - a wrong figure here moves the capital base and therefore the franchise tax.",
     "notes": "W15 - a verification-pass find. Direct-entry + RED when non-zero."},
    {"diagnostic_id": "D_MS83105_FRANCHISE_FLOOR_BITES", "severity": "warning",
     "title": "⚠⚠ Franchise credits drove line 4 to zero - and the statute reads $25",
     "condition": "franchise_credits >= L2 and L4 == 0",
     "message": "Franchise tax credits equal or exceed the line-2 franchise tax, so line 4 is zero. That "
                "follows the Department's own line-4 instruction: 'If line 3 equal or exceeds the amount "
                "shown on line 2, enter a zero.' ⚠ But § 27-13-5(1)(b) reads the other way: 'In no case "
                "shall the franchise tax due for the accounting period be less than Twenty-five Dollars "
                "($25.00).' Both texts are the Department's. Ken ruled the operational instruction ships "
                "(campaign D-26, S1) and a DOR ticket is queued to resolve it. The difference on this "
                "return is $25. ⚠ This most often arises on a Mississippi bank claiming the Bank Share "
                "credit.",
     "notes": "⚠⚠ S1 - the flag half of 'ship it flagged'. The constant MS_FRANCHISE_NET_FLOOR is the "
              "single point of change when the Department answers."},
    {"diagnostic_id": "D_MS83105_NONPROFIT_FRANCHISE_BLANK", "severity": "warning",
     "title": "Exempt organizations leave lines 1-4 BLANK, not zero",
     "condition": "is_non_profit == True and (taxable_capital != 0 or L2 != 0)",
     "message": "The 'Non Profit' box is ticked. Booklet p.10, verbatim: 'Exempt corporate organizations "
                "file Form 83-105 and any necessary supplemental schedules. These organizations are not "
                "subject to the franchise tax levy and should LEAVE LINES 1 THROUGH 4 BLANK.' ⚠ Blank is "
                "not zero - a printed zero asserts that a computation was performed and returned nothing, "
                "which is not what the Department asked for.",
     "notes": "Exemption route 1 of 4. The only one with a clean published rule."},
    {"diagnostic_id": "D_MS83105_INDUSTRY_APPORTIONMENT", "severity": "error",
     "title": "⚠ Special-industry apportionment is not computed",
     "condition": "industry_apportionment_type not in ('', None, 'general')",
     "message": "Mississippi's apportionment regulations diverge for three special industries. Those "
                "divergences are RED-DEFERRED in this version (campaign D-26, W6); apportionment boxes 1-3 "
                "compute as printed for general taxpayers only. Compute the special-industry factor outside "
                "Delvio and enter it directly.",
     "notes": "W6 - RED-defer, boxes 1-3 as printed."},
    {"diagnostic_id": "D_MS83105_CREDIT_ADDBACK_LOOP", "severity": "warning",
     "title": "⚠ The credit add-back is circular - solver assist, never silent",
     "condition": "income_tax_credits != 0",
     "message": "Certain Mississippi credits are added back in computing the income they offset, which makes "
                "the credit and the tax mutually dependent. Ken ruled this DIRECT-ENTRY WITH SOLVER ASSIST "
                "and NEVER SILENT (campaign D-26, W9): Delvio may propose an iterated figure, but it must "
                "show that it iterated and what it converged to. Review the proposed amount before filing.",
     "notes": "W9 - 'direct-entry with solver assist, never silent' is the ruling; silence is the failure "
              "mode being guarded against."},
    {"diagnostic_id": "D_MS83105_AVIATION_PER_ASSET", "severity": "warning",
     "title": "⚠ The aviation depreciation regime is a PER-ASSET election",
     "condition": "aviation_asset_regime not in ('', None)",
     "message": "Mississippi's aviation exception to its own 100% bonus regime is elected PER ASSET, not "
                "per return (campaign D-26, W10 - the same trap as PTE W4). A return-level flag will "
                "silently apply one regime to a mixed fleet. ⚠ This carries real client-advice exposure: "
                "the wrong regime on one aircraft changes depreciation for its whole life, not just this "
                "year. Confirm the regime asset by asset.",
     "notes": "W10 - an app-design problem Ken flagged as carrying client-advice exposure."},
    {"diagnostic_id": "D_MS83105_NOL_ELECTION_IRREVOCABLE", "severity": "warning",
     "title": "⚠ The forgo-carryback election is made on the ORIGINAL return and cannot be changed",
     "condition": "nol_forgo_carryback_elected == True",
     "message": "The 83-155 header election to forgo the NOL carryback is being made. Booklet p.19: the "
                "election is available only 'on the original return filing', and p.9: 'ONCE THIS ELECTION "
                "IS MADE, IT CANNOT BE CHANGED.' ⚠ Mississippi's period is two years back and twenty "
                "forward - NOT the federal treatment - so forgoing the carryback gives up two real years of "
                "recovery. Confirm with the client before filing.",
     "notes": "S3 - the irrevocability is the part clients are surprised by."},
    {"diagnostic_id": "D_MS83105_ESTIMATES_KEYED_TO_L8", "severity": "info",
     "title": "Estimates are keyed to line 8 - the income tax - never to line 9",
     "condition": "ms_net_taxable_income != 0",
     "message": "Booklet p.16: 'If the current Mississippi income tax liability (line 8) is $200 or less, "
                "then estimated income tax payments were not required.' ⚠ The threshold reads LINE 8, the "
                "net income tax - not line 9, the combined franchise-and-income total. The franchise tax "
                "never triggers estimated payments, so a corporation with a large franchise tax and a small "
                "income tax owes no estimates.",
     "notes": "A quiet trap: line 9 is the number that looks like 'the tax', and it is the wrong one here."},
]

F_SCENARIOS: list[dict] = [
    {"scenario_name": "MS83105-A - franchise tax at $0.75 per $1,000 above the $100,000 exemption",
     "scenario_type": "normal", "sort_order": 1,
     "inputs": {"taxable_capital": 5100000, "franchise_credits": 0},
     "expected_outputs": {"MS83105-2": 3750.0, "MS83105-4": 3750.0},
     "notes": "(5,100,000 - 100,000) / 1,000 = 5,000 units x $0.75 = $3,750."},
    {"scenario_name": "MS83105-B - 'or fractional part thereof' rounds the unit count UP",
     "scenario_type": "edge", "sort_order": 2,
     "inputs": {"taxable_capital": 1000500, "franchise_credits": 0},
     "expected_outputs": {"MS83105-2": 675.75},
     "notes": "⚠ (1,000,500 - 100,000) = 900,500 -> 901 units (NOT 900.5) x $0.75 = $675.75. Truncating "
              "gives $675.375 and understates the tax on every base that is not an exact multiple of "
              "$1,000 - which is almost all of them."},
    {"scenario_name": "MS83105-C - the $25 minimum bites at line 2",
     "scenario_type": "edge", "sort_order": 3,
     "inputs": {"taxable_capital": 110000, "franchise_credits": 0},
     "expected_outputs": {"MS83105-2": 25.0},
     "notes": "(110,000 - 100,000) = 10,000 -> 10 units x $0.75 = $7.50, raised to the printed $25 minimum."},
    {"scenario_name": "MS83105-D - ⚠⚠ S1: credits drive line 4 to ZERO, and the statute would say $25",
     "scenario_type": "edge", "sort_order": 4,
     "inputs": {"taxable_capital": 5100000, "franchise_credits": 4000},
     "expected_outputs": {"MS83105-4": 0.0},
     "notes": "⚠⚠ THE RULING THAT MOVES A NUMBER. Credits (4,000) exceed the line-2 tax (3,750), so the "
              "DOR's own L4 instruction says enter zero. The competing statutory reading, § 27-13-5(1)(b), "
              "would return $25. The harness computes BOTH and asserts they differ - the point of D-26 S1 "
              "is that Ken chose between two live DOR texts, not that one was wrong. Bites every "
              "Mississippi bank via the Bank Share credit."},
    {"scenario_name": "MS83105-E - the 0/4/5 ladder, and a flat 5% is provably wrong",
     "scenario_type": "normal", "sort_order": 5,
     "inputs": {"ms_net_taxable_income": 250000, "taxpayer_type": "corporation"},
     "expected_outputs": {"MS83105-6": 12200.0},
     "notes": "0% x 5,000 + 4% x 5,000 + 5% x 240,000 = 0 + 200 + 12,000 = 12,200. A flat 5% would give "
              "12,500 - the two brackets below 10,000 are worth exactly $300 to every Mississippi "
              "corporation, every year."},
    {"scenario_name": "MS83105-F - ⚠⚠ S4: corporate and individual ladders DIVERGE at TY2027",
     "scenario_type": "edge", "sort_order": 6,
     "inputs": {"ms_net_taxable_income": 250000, "tax_year": 2027},
     "expected_outputs": {"corporate_2027": 12200.0, "individual_2027": 9200.0},
     "notes": "⚠⚠ THE WHOLE POINT OF KEYING THE LADDER. At TY2027 the corporate schedule is still 0/4/5 "
              "(§ 27-7-5(1)(a)) while HB 1's § 27-7-5(1)(b)(ii) drops the individual top rate to 3.75% - "
              "0 + 200 + 3.75% x 240,000 = 9,200. A single year-keyed table would hand this corporation "
              "the individual answer and understate its tax by 3,000, silently, in a year nobody will be "
              "re-reading this spec."},
    {"scenario_name": "MS83105-G - L9 has no entity-type fork",
     "scenario_type": "normal", "sort_order": 7,
     "inputs": {"taxable_capital": 5100000, "franchise_credits": 0, "ms_net_taxable_income": 250000},
     "expected_outputs": {"MS83105-9": 15950.0},
     "notes": "3,750 franchise + 12,200 income = 15,950. On the PTE 84-105 an entity-type fork could drop "
              "the franchise leg entirely; here it never can."},
    {"scenario_name": "MS83105-H - ⚠⚠ the L19/L20 asymmetry, and symmetrising changes the refund",
     "scenario_type": "edge", "sort_order": 8,
     "inputs": {"L9": 10000, "L13": 12000, "L15": 300, "L16": 100, "L17": 100, "L18": 100},
     "expected_outputs": {"MS83105-19": 0.0, "MS83105-20": 1700.0},
     "notes": "⚠⚠ L20 = 12,000 - 10,000 - 300 = 1,700. It nets the underestimate item (L15) but NOT the "
              "late-payment items (L16-L18). A 'symmetrised' L20 that also netted L16-L18 would return "
              "1,400 and short the client $300 on the refund. The PTE verification pass confirmed the same "
              "asymmetry on the 84-105 - it is printed, deliberate, and must be built as printed."},
    {"scenario_name": "MS83105-I - ⚠ S3: NOL expiry at twenty periods, not the stale five",
     "scenario_type": "edge", "sort_order": 9,
     "inputs": {"loss_year": 2020},
     "expected_outputs": {"expiry_year": 2040},
     "notes": "⚠ § 27-7-17(1)(l) and both booklets: twenty periods forward. The stale Title 35 Ch.06 § 100 "
              "would expire this loss in 2025 - THIS year - and silently disallow a deduction the taxpayer "
              "is entitled to for another fifteen years. The harness proves the two answers differ."},
    {"scenario_name": "MS83105-J - ⚠ S2: underestimate interest at ½%, not the regulation's 1%",
     "scenario_type": "edge", "sort_order": 10,
     "inputs": {"underpayment": 40000, "months": 6},
     "expected_outputs": {"interest_half_pct": 1200.0, "interest_one_pct": 2400.0},
     "notes": "⚠ 40,000 x 0.5% x 6 = 1,200 on the form face; the regulation's 1% would give 2,400 - exactly "
              "double, on every underpaid Mississippi corporate return. Two DOR sources say ½% (booklet "
              "p.19 and Form 83-305 L15) against one that says 1%. Ken ruled the face (D-26 S2)."},
    {"scenario_name": "MS83105-K - § 27-7-5(4) blend is the IDENTITY for a TY2025 fiscal year",
     "scenario_type": "edge", "sort_order": 11,
     "inputs": {"ms_net_taxable_income": 250000, "fiscal_year_months_earlier": 6,
                "fiscal_year_months_total": 12, "earlier_year": 2025, "later_year": 2026},
     "expected_outputs": {"blended": 12200.0},
     "notes": "The corporate schedule has not moved between CY2025 and CY2026, so (a) and (b) produce the "
              "same number and the blend is the identity. Encoded as a REAL blend anyway - it is one "
              "session away from being live, and the harness proves it is a genuine blend by running it "
              "across the TY2026/TY2027 individual boundary where the rates do differ."},
]

FORMS: list[dict] = [
    {
        "identity": {
            "form_number": "MS_83105",
            "form_title": "Mississippi Form 83-105 - Corporate Income and Franchise Tax Return (TY2025)",
            "notes": (
                "WO-W05-CCORP; walk closed at campaign D-26 (16 items). Mississippi's C-corp return runs "
                "TWO taxes and neither gates the other: the franchise levy (L1-L4) applies to ALL "
                "corporations - the block header is unqualified and L9 has no entity-type fork, unlike the "
                "PTE 84-105 - and the income tax (L5-L8) runs the unreduced 0/4/5 ladder. ⚠⚠ D-26 S1: the "
                "$25 statutory franchise minimum and the DOR's own line-4 zero floor CONFLICT, both texts "
                "are the Department's, and Ken ruled the operational instruction ships as a flagged "
                "single-point-of-change constant with a DOR ticket - the opposite of the VA/MD answer and "
                "deliberately so. ⚠⚠ D-26 S4: the rate ladder is keyed by TAXPAYER TYPE from the start, "
                "because HB 1 (2025) phases the individual top rate from TY2027 while leaving the "
                "corporate schedule alone. ⚠ The L19/L20 asymmetry is printed and must not be "
                "symmetrised. ⚠ NOL is 2 back / 20 forward per statute and booklet, never the stale "
                "five-year regulation. Combined filing, Form 83-391 (insurance), Form 83-124 (direct "
                "accounting) and Form 83-450 are refused, each naming what it refuses."
            ),
        },
        "facts": F_FACTS, "rules": F_RULES, "rule_links": F_RULE_LINKS,
        "lines": F_LINES, "diagnostics": F_DIAGNOSTICS, "scenarios": F_SCENARIOS,
    },
]

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-MS83105-UNGATE", "title": "The franchise levy is ungated - L9 never forks",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 1,
     "description": "⚠ The PTE 84-105 gates its franchise block to S corporations and forks L9 by entity "
                    "type. The 83-105 does neither: the header is the unqualified 'FRANCHISE TAX' and L9 "
                    "is 'line 4 plus line 8'. Booklet p.7: 'Form 83-110 must be completed by ALL "
                    "corporations.' The only way out is an EXEMPTION, never an entity type - and three of "
                    "the four exemption routes are RED-deferred because none carries a published "
                    "computation.",
     "definition": {"rule": "R-MS83105-L9", "check": "L9 == L4 + L8 unconditionally"}},
    {"assertion_id": "FA-MS83105-FLOOR", "title": "⚠⚠ The L4 floor is a single point of change (D-26 S1)",
     "assertion_type": "reconciliation", "entity_types": ["1120"], "status": "draft", "sort_order": 2,
     "description": "⚠⚠ § 27-13-5(1)(b) sets a $25 minimum on franchise tax DUE; the DOR's own L4 "
                    "instruction permits credits to reach zero. BOTH are Department text - this is "
                    "statute-versus-operational-instruction, not statute-versus-error, which is why the "
                    "answer differs from Virginia (D-21) and Maryland (D-20). Ken ruled the Department's "
                    "reading ships because DOR runs the approval this software must pass. ONE constant, "
                    "MS_FRANCHISE_NET_FLOOR, changes when the DOR ticket returns.",
     "definition": {"rule": "R-MS83105-L4", "check": "L4 == max(MS_FRANCHISE_NET_FLOOR, L2 - L3)"}},
    {"assertion_id": "FA-MS83105-LADDER",
     "title": "⚠⚠ The rate ladder is keyed by TAXPAYER TYPE, not by year alone (D-26 S4)",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 3,
     "description": "⚠⚠ § 27-7-5(1)(a) names 'corporation' and its schedule is unreduced. HB 1 (2025)'s "
                    "§ 27-7-5(1)(b)(ii) steps the INDIVIDUAL top rate to 3.75/3.5/3.25/3% from TY2027. A "
                    "single year-keyed table leaks the individual phase-down into corporate returns in a "
                    "year nobody will be re-reading this spec. Keyed NOW, while TY2025 does not need it.",
     "definition": {"rule": "R-MS83105-L6",
                    "check": "ladder(corporation, 2027) != ladder(individual, 2027)"}},
    {"assertion_id": "FA-MS83105-ASYMM",
     "title": "⚠⚠ L19 and L20 are asymmetric as printed and must not be reconciled",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 4,
     "description": "⚠⚠ L19 tests line 9 > line 13; L20 tests line 13 > line 9 + line 15 and subtracts "
                    "both. Underestimate interest nets against an overpayment; late-payment items do not. "
                    "Confirmed identical on the 84-105 by the PTE verification pass. A developer who "
                    "'fixes' this shorts the client the late-payment amounts on every overpaid return.",
     "definition": {"rule": "R-MS83105-SETTLE",
                    "check": "L20 subtracts L15 only; L16-L18 are never netted"}},
    {"assertion_id": "FA-MS83105-NOL",
     "title": "⚠ NOL is two back / twenty forward - never the stale five-year regulation",
     "assertion_type": "reconciliation", "entity_types": ["1120"], "status": "draft", "sort_order": 5,
     "description": "⚠ Title 35 Part III Subpart 02 Ch.06 § 100 still reads 'the next five succeeding "
                    "years'. That text predates the 2001 amendment, and the same chapter's § 102 cites "
                    "§ 27-7-17(1)(l), which says two and twenty - as do both booklets. Building the "
                    "regulation would expire a 2020 loss in 2025 and silently disallow fifteen more years "
                    "of a deduction the taxpayer is entitled to. ⚠ A short taxable year counts as a "
                    "taxable year, so the ledger counts PERIODS, not calendar years.",
     "definition": {"rule": "R-MS83105-NOL", "check": "carryback == 2 and carryforward == 20"}},
    {"assertion_id": "FA-MS83105-COMBINE",
     "title": "⚠⚠ Detection of combined filing is a prerequisite, not a courtesy",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 6,
     "description": "⚠⚠ W16: the combined universes are DISJOINT - Forms 83-391 and 83-105 filers cannot "
                    "appear in one combined return. That is why Ken ruled DETECT-and-defer rather than "
                    "simply defer: any future combined coding has to begin by establishing which universe "
                    "the group is in, and a version that cannot detect combined filing at all cannot be "
                    "extended safely.",
     "definition": {"rule": "R-MS83105-L9",
                    "check": "is_combined_return -> hard error; universes never mixed"}},
]


class Command(BaseCommand):
    help = ("Load the MS_83105 spec (Mississippi Corporate Income and Franchise Tax Return, TY2025). "
            "Refuses to seed until Ken's Gate-1 SEED approval.")

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad MS_83105 spec (Mississippi Corporate Income and Franchise Tax Return, TY2025)\n"))
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
                "\nREFUSING TO SEED MS_83105: not cleared to seed.\n\n"
                "Campaign D-26 approved the Mississippi walk SCOPE (16 items). That is NOT the seed\n"
                "gate. Ken must give the Gate-1 SEED approval DIRECTLY - a relayed approval never\n"
                "opens a human gate.\n\n"
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
        self.stdout.write("MS_83105 loaded (TY2025 ONLY - every figure is TY-keyed).")
        self.stdout.write(f"  MS_83105: facts {len(F_FACTS)} / rules {len(F_RULES)} / lines {len(F_LINES)} / "
                          f"diag {len(F_DIAGNOSTICS)} / tests {len(F_SCENARIOS)}")
        self.stdout.write(f"  Flow assertions: {len(FLOW_ASSERTIONS)}")
        self.stdout.write("  !! L4 floor ships the DOR zero (D-26 S1) - MS_FRANCHISE_NET_FLOOR is the")
        self.stdout.write("     single point of change when the DOR ticket returns.")
        self.stdout.write("  !! The rate ladder is keyed by TAXPAYER TYPE (D-26 S4) - never merge it.")
        self.stdout.write("=" * 66)
