"""Load the Alabama Form 40NR spec - Individual Nonresident Income Tax Return (TY2025).

Campaign `delvio-states`. Research closed and adversarially verified (U1-U9);
**Gate-1 walk closed at campaign D-32**, all four source conflicts ruled.

⚠ This form JUMPED the declared wave order (PTE -> C-corp -> individual -> fiduciary)
on Ken's ruling, because a production packet was blocked on it.

═══════════════════════════════════════════════════════════════════════════
⚠⚠ THE ONE THAT MOVES MONEY SILENTLY - RETIREMENT IS NOT A SOURCING QUESTION
═══════════════════════════════════════════════════════════════════════════
Booklet p.11, Line 3 Pensions and Annuities, verbatim:

  "Pension and annuity payments received by a nonresident are NOT SUBJECT TO
   ALABAMA TAX. However, pension and annuity payments you received in 2025 THAT
   WOULD BE TAXABLE TO A RESIDENT OF ALABAMA must be included in the total
   adjusted gross income from all sources in order to compute the ratio of
   Alabama adjusted gross income to total adjusted gross income from all sources"

**Geography is irrelevant.** Column C is ALWAYS ZERO for pensions - r. 810-3-14-.05
enumerates a nonresident's Alabama gross income exhaustively and pensions appear
nowhere in it. But **column B carries the distribution anyway**, precisely so it
enlarges the line-10 denominator and SHRINKS every prorated deduction.

⚠⚠ So retirement income a nonresident will never pay one dollar of Alabama tax on
still CUTS their Alabama deductions. Drop it from column B and line 10 comes out
TOO HIGH, every prorated figure comes out TOO LARGE, and Alabama tax is
UNDERSTATED - while the return foots perfectly either way. **Schedule RS Part I
exempts by PLAN TYPE, not location** (§ 414(j) is defined BENEFIT; an IRA is not
on the list). The test scenarios encode a real filed return in BOTH positions so
the harness PROVES the whole cascade moves, not merely line 10.

═══════════════════════════════════════════════════════════════════════════
KEN'S RULINGS THIS SPEC IMPLEMENTS (campaign D-32)
═══════════════════════════════════════════════════════════════════════════
A1  ⚠⚠ The MFS-on-Alabama / joint-on-federal federal tax deduction: **BUILD THE
    FORM** (Part IV's two multiplications), and DIAGNOSE the divergence from
    r. 810-3-15-.21(3)(e)(2)(i)'s single fraction.
    **This is deliberately NOT the Virginia answer (D-21).** There the booklet was
    demonstrably DEFECTIVE - it restated the statute and dropped "plus one". Here
    the form is NOT defective: the two methods are ALGEBRAICALLY IDENTICAL whenever
    the taxpayer's federal AGI equals their Alabama all-source adjusted total
    income, and diverge only as column B departs from federal AGI - in BOTH
    directions. And Part IV lines 3/5/6/7 are PRINTED, so the regulation's single
    fraction yields a return where line 7 != line 5 x line 6.
    ⭐ *A regulation outranks a form on authority; it does not outrank it on what
    the form must show.*
A2  The $6,000 age-65 retirement exclusion: **ENCODE IT, PER TAXPAYER**, from the
    Schedule RS face. `$6,000` appears NOWHERE in the 40NR booklet, TY2025 or
    TY2024 - but nothing contradicts the face, so the silence is an OMISSION, not
    a conflict.
A3  The line-10 ZERO FLOOR for an Alabama loss: **ENCODE IT**, recording that it
    rests on ONE authority. The face is silent in both editions and the regulation
    is silent; only the booklet carries it. Omitting it yields a NEGATIVE
    percentage propagating into five prorated figures.
A4  Casualty and theft losses: **ALABAMA-ONLY, NOT PRORATED** - closed on evidence
    rather than adjudicated. The booklet's line-21 instruction scopes proration to
    "lines 1 through 20", putting 24a-c outside it by construction.

═══════════════════════════════════════════════════════════════════════════
⚠⚠ U9 - THE DOR'S PRINTED STANDARD-DEDUCTION CHART IS DEFECTIVE
═══════════════════════════════════════════════════════════════════════════
The MFJ column's third band is PRINTED as `$25,500 - $26,999`. That overlaps bands
1 and 2 and runs backwards, making an AGI of ~$25,700 an AMBIGUOUS lookup ($8,500
or $8,150) on an ordinary figure.

⚠ **The other DOR income-tax booklets CANNOT settle it** - Form 40, Form 40A and
40NR for BOTH TY2024 and TY2025 reprint the identical defect from one shared piece
of artwork (PDF metadata proves it).

✅ **What settles it is the DOR's WITHHOLDING TAX TABLES booklet** - a different,
independently typeset first-party publication that states the rule TWICE: as a
formula ("$8,500 less $175 for each $500 increment or part thereof of GI above
$25,999") and as the same 21-band schedule reading **$26,500 - $26,999 -> $8,150**.
The printed `$25,500` duplicates the STATUTORY phase-down threshold
(Ala. Code § 40-18-15(b)) into the row-3 lower-bound cell.

**This spec encodes $26,500, records that the published chart is defective, and the
harness PROVES the corrected reading is the one that makes the ladder uniform.**

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
# D-32 closed the walk (SCOPE). That is not the seed gate.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = True   # ⚠ OPENED 2026-08-23 on Ken's DIRECT Gate-1 SEED approval ("seed it"), given unmediated in session. Pre-flight clean: prod 167 forms, 7 new sources and 1 new topic all absent, 4 referenced rows resolve.


FORM_JURISDICTION = "AL"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"
FORM_ENTITY_TYPES = ["1040"]

FILING_STATUSES = ("single", "mfj", "mfs", "hof")

# Face lines 1-4. ⚠ Prorated by line 10 at line 15 (r. 810-3-15-.21(3)(e)(1)).
AL_PERSONAL_EXEMPTION: dict[int, dict[str, int]] = {
    2025: {"single": 1500, "mfj": 3000, "mfs": 1500, "hof": 3000},
}

# ───────────────────────────────────────────────────────────────────────────
# ⚠⚠ THE STANDARD DEDUCTION CHART - EXPLICIT BANDS, keyed on COL. B LINE 12.
# Each entry: (lower_inclusive, upper_inclusive_or_None, deduction).
# ⚠ The MFJ row-3 lower bound is 26500, NOT the 25500 the DOR chart PRINTS.
# See the module docstring; the correction is sourced to the DOR Withholding Tax
# Tables booklet, an independently typeset first-party publication.
# ⚠ Encoded EXPLICITLY rather than generated. The campaign's MO-C lesson is that a
# formula which happens to fit is not the same as the published table - but here
# the harness ALSO proves the explicit table matches a uniform ladder, because
# that uniformity is part of the evidence that 26500 is the right reading.
# ───────────────────────────────────────────────────────────────────────────
def _bands(first_hi: int, step: int, first_amt: int, decrement: int,
           floor_lo: int, floor_amt: int) -> tuple:
    out = [(0, first_hi, first_amt)]
    lo, amt = first_hi + 1, first_amt - decrement
    while lo < floor_lo:
        out.append((lo, lo + step - 1, amt))
        lo, amt = lo + step, amt - decrement
    out.append((floor_lo, None, floor_amt))
    return tuple(out)


AL_STANDARD_DEDUCTION: dict[int, dict[str, tuple]] = {
    2025: {
        # MFJ  : $0-25,999 -> 8,500 ; -175 per $500 band ; floor 35,500+ -> 5,000
        "mfj": _bands(25999, 500, 8500, 175, 35500, 5000),
        # MFS  : $0-12,999 -> 4,250 ; -88 per $250 band ; floor 17,750+ -> 2,500
        "mfs": _bands(12999, 250, 4250, 88, 17750, 2500),
        # HOF  : $0-25,999 -> 5,200 ; -135 per $500 band ; floor 35,500+ -> 2,500
        "hof": _bands(25999, 500, 5200, 135, 35500, 2500),
        # Single: $0-25,999 -> 3,000 ; -25 per $500 band ; floor 35,500+ -> 2,500
        "single": _bands(25999, 500, 3000, 25, 35500, 2500),
    },
}

# ⚠⚠ The reading the DOR chart PRINTS for MFJ band 3 - retained ONLY so the harness
# can prove it is ambiguous and that this spec did not ship it.
AL_MFJ_BAND3_AS_PRINTED = (25500, 26999, 8150)
AL_MFJ_BAND3_AS_ENCODED = (26500, 26999, 8150)
AL_U9_DEFECT_NOTE = (
    "The DOR's printed income-tax chart gives MFJ band 3 as $25,500-$26,999, which overlaps bands 1 "
    "and 2 and runs backwards. Form 40, Form 40A and 40NR for BOTH TY2024 and TY2025 reprint the "
    "identical defect from one shared piece of artwork. Resolved to $26,500 against the DOR "
    "WITHHOLDING TAX TABLES booklet (whbooklet_0126.pdf), independently typeset, which states the "
    "rule both as a formula and as the same 21-band schedule. The printed 25,500 duplicates the "
    "statutory phase-down threshold at Ala. Code § 40-18-15(b) into the row-3 lower-bound cell."
)

# Dependent exemption chart - ALSO keyed on col. B line 12. Independently confirmed
# in the DOR Withholding booklet p.7.
AL_DEPENDENT_EXEMPTION: dict[int, tuple] = {
    2025: ((0, 50000, 1000), (50001, 100000, 500), (100001, None, 300)),
}

# ───────────────────────────────────────────────────────────────────────────
# ⚠⚠ THE TAX TABLE - TWO columns, and HEAD OF FAMILY IS IN THE *SINGLE* COLUMN.
# Booklet pp.21-26, resolved POSITIONALLY:
#   col 1 header: "Single ✱ Married filing separately ✱ Head of family"
#   col 2 header: "Married filing jointly"
# ⚠ HOF takes the MFJ-sized $3,000 personal exemption and its OWN standard-deduction
# table, but the SINGLE rate brackets. Confirmed against the DOR Withholding booklet
# p.7, which brackets "'0', 'S', 'H' or 'MS'" together and "'M'" separately.
# ───────────────────────────────────────────────────────────────────────────
AL_TAX_BRACKETS: dict[int, dict[str, tuple]] = {
    2025: {
        "single_mfs_hof": ((500, "0.02"), (2500, "0.04"), (None, "0.05")),
        "mfj": ((1000, "0.02"), (5000, "0.04"), (None, "0.05")),
    },
}
AL_TAX_COLUMN: dict[str, str] = {
    "single": "single_mfs_hof",
    "mfs": "single_mfs_hof",
    "hof": "single_mfs_hof",   # ⚠⚠ NOT "mfj" - the trap this constant exists to prevent
    "mfj": "mfj",
}
AL_TAX_TABLE_BAND: dict[int, int] = {2025: 100}       # $100 bands ABOVE the floor rows
# ⚠⚠ THE TABLE IS NOT UNIFORMLY BANDED. Below $100 it carries TWO $50-wide rows,
# and those two round DOWN where the rest of the table rounds half-up.
# Established by harvesting all 1,006 published rows: Alabama rounds half-up on
# 1,910 of 1,914 exact-half cases; the ONLY exceptions are these two, in BOTH
# columns - [0,50) raw 0.50 -> 0 and [50,100) raw 1.50 -> 1. They are therefore
# encoded AS PRINTED rather than computed. CORRECTED 2026-08-24 on Ken's ruling.
# ⚠ Same shape as the SC tax-table band error: a table whose row width is not
# uniform across its range. The floor, the ceiling and every width change need
# their own fixture - the interior gets tested and the boundaries do not.
AL_TAX_TABLE_FLOOR_BAND: dict[int, int] = {2025: 50}       # $50-wide rows below $100
AL_TAX_TABLE_FLOOR_CEILING: dict[int, int] = {2025: 100}   # where the $100 bands begin
AL_TAX_TABLE_FLOOR_ROWS: dict[int, dict[int, int]] = {     # AS PRINTED, both columns
    2025: {0: 0, 50: 1},
}
AL_TAX_TABLE_CEILING: dict[int, int] = {2025: 100000}
# Over $100,000 the table is replaced by a printed worksheet:
# taxable - 100,000.00 -> x .05 -> + constant.
# ⚠ Both constants sit ~$2 below the exact bracket computation ($4,960 / $4,920)
# because they carry the table's own mid-band convention. USE THE PUBLISHED
# CONSTANTS, never a derived formula.
AL_OVER_100K_CONSTANT: dict[int, dict[str, str]] = {
    2025: {"single_mfs_hof": "4958.00", "mfj": "4918.00"},
}
AL_OVER_100K_RATE: dict[int, str] = {2025: "0.05"}

# ⚠⚠ ALABAMA MULTIPLIES BY THE **ROUNDED** LINE-10 PERCENTAGE, NOT FULL PRECISION.
# Line 10 prints two decimal places as a percentage, and that printed figure is what
# every proration uses. Established from a real filed return: 17,138/39,693 =
# 43.17638%, printed as 43.18%. Schedule A line 21 of 21,559 gives 9,308 at full
# precision and 9,309 at the printed percentage - and the filed figure is 9,309.
# ⚠ A $1 divergence on every itemizing nonresident return, and it compounds across
# the five prorated figures. Not stated anywhere; established by reconstruction.
AL_LINE10_DECIMALS: dict[int, int] = {2025: 2}      # decimal places as a PERCENTAGE

# ⚠⚠ A3 - the line-10 zero floor. SINGLE AUTHORITY: the booklet only.
AL_LINE10_LOSS_FLOOR: dict[int, str] = {2025: "0.00"}
AL_LINE10_CAP: dict[int, str] = {2025: "1.00"}
AL_LINE10_FLOOR_AUTHORITY = (
    "⚠ ONE AUTHORITY ONLY (campaign D-32 A3). Booklet, verbatim: 'If the amount in Column C is a "
    "loss (less than 0) enter 0% on line 10.' The form face carries 'not over 100%' but NO loss "
    "rule at all, in BOTH the print and interactive editions, and r. 810-3-15-.21 states only the "
    "bare division. Ken ruled it ships anyway because the alternative - a negative percentage "
    "propagating into five prorated figures - is arithmetically indefensible."
)

# Schedule A floors. ⚠⚠ THREE FLOORS, TWO DIFFERENT COLUMNS, ON ONE SCHEDULE.
AL_MEDICAL_FLOOR_PCT: dict[int, str] = {2025: "0.04"}       # of line 12 COL. B
AL_CASUALTY_FLOOR_PCT: dict[int, str] = {2025: "0.10"}      # of line 12 COL. C
AL_JOB_EXPENSE_FLOOR_PCT: dict[int, str] = {2025: "0.02"}   # of line 12 COL. C
AL_CASUALTY_PER_EVENT_FLOOR: dict[int, int] = {2025: 100}   # ⚠ INSTRUCTION-ONLY
# Schedule A lines 1-20 are prorated (booklet line-21 instruction); 24c and 29 are
# NOT (A4). ⚠ Line 20's miscellaneous deductions are exempt from the 2% limit.
AL_SCHED_A_PRORATED_LINES: tuple = (4, 9, 14, 18, 19, 20)
AL_SCHED_A_UNPRORATED_LINES: tuple = (24, 29)

# NEW for TY2025 - the Qualified Vehicle Loan Interest Worksheet.
AL_VEHICLE_LOAN_CAP: dict[int, int] = {2025: 10000}
AL_VEHICLE_LOAN_PHASEOUT_START: dict[int, dict[str, int]] = {
    2025: {"single": 100000, "mfs": 100000, "hof": 100000, "mfj": 200000},
}
AL_VEHICLE_LOAN_PHASEOUT_STEP: dict[int, int] = {2025: 1000}
AL_VEHICLE_LOAN_PHASEOUT_PER_STEP: dict[int, int] = {2025: 200}

# ⚠⚠ A2 - the $6,000 age-65 retirement exclusion, PER TAXPAYER.
AL_RETIREMENT_EXCLUSION: dict[int, int] = {2025: 6000}
AL_RETIREMENT_EXCLUSION_AGE: dict[int, int] = {2025: 65}
AL_RETIREMENT_EXCLUSION_AUTHORITY = (
    "⚠ Schedule RS face ONLY (campaign D-32 A2). Part II line 10 / Part III line 10: 'Is the "
    "primary taxpayer 65 or older and receives taxable retirement? ... If Yes, EACH TAXPAYER is "
    "eligible up to $6,000 not to exceed the Retirement Income Taxable to Alabama on line 9.' "
    "The figure $6,000 appears NOWHERE in the 40NR booklet, TY2025 or TY2024 - but nothing "
    "contradicts the face, so the silence is an OMISSION, not a conflict. Encoded PER TAXPAYER "
    "because the face gives primary and spouse separate lines. NOT new for TY2025 - the TY2024 "
    "Schedule RS carries it verbatim."
)

# ⚠⚠ Schedule RS Part I exempts by PLAN TYPE, not by location.
AL_RETIREMENT_EXEMPT_PLAN_TYPES: tuple = (
    "State of Alabama Teachers' Retirement",
    "State of Alabama Employees' Retirement",
    "State of Alabama Judicial Retirement",
    "United States Civil Service Retirement",
    "Retirement systems created by the Federal Social Security Acts",
    "Railroad retirement benefits under the Federal Railroad Retirement Acts of 1935 and 1937",
    "Military Retirement Pay",
    "TVA Pension System Benefits",
    "U.S. Foreign Service Retirement and Disability Fund Annuities",
    "U.S. Government Retirement Fund Benefits",
    "Any Defined Benefit Retirement Plan in accordance with IRC 414(j)",
)
# ⚠⚠ NOT a plan type, and NOT a valid exemption reason. Geography is irrelevant.
AL_RETIREMENT_INVALID_EXEMPT_REASONS: tuple = ("out-of-state", "OS", "non-Alabama source", "nonresident")

# ⚠⚠ Part II line 8 sums DIFFERENT LINE SETS per column. Face, verbatim:
# "Add lines 1 through 7, Column B, and lines 1, 3 through 7, Column C."
AL_PART2_SUM_COL_B: tuple = (1, 2, 3, 4, 5, 6, 7)
AL_PART2_SUM_COL_C: tuple = (1, 3, 4, 5, 6, 7)      # ⚠ line 2 OMITTED

# ⚠⚠ THE FEDERAL LINE REFERENCES, re-verified against the FINAL TY2025 IRS forms.
# Alabama disclaims them ("may have changed"); U5 proved they are CORRECT for
# TY2025, INCLUDING the two places Alabama deliberately omits Form 1040-NR.
AL_FIT_WORKSHEET_FEDERAL_LINES: dict[str, dict] = {
    "tax":        {"line": "1040 L22", "forms": ("1040", "1040-SR", "1040-NR"),
                   "label": "Subtract line 21 from line 18. If zero or less, enter -0-"},
    "niit":       {"line": "8960 L17", "forms": ("8960",),
                   "label": "Net investment income tax for individuals"},
    "eic":        {"line": "1040 L27a", "forms": ("1040", "1040-SR"),
                   "label": "Earned income credit (EIC)"},
    "actc":       {"line": "1040 L28", "forms": ("1040", "1040-SR", "1040-NR"),
                   "label": "Additional child tax credit (ACTC) from Schedule 8812"},
    "aoc":        {"line": "1040 L29", "forms": ("1040", "1040-SR"),
                   "label": "American opportunity credit from Form 8863, line 8"},
    "adoption":   {"line": "1040 L30", "forms": ("1040", "1040-SR", "1040-NR"),
                   "label": "Refundable adoption credit from Form 8839, line 13"},
    "form_2439":  {"line": "Sch 3 Part II L13a", "forms": ("1040", "1040-SR", "1040-NR"),
                   "label": "Form 2439"},
}
# ⚠⚠ THE BUILD TRAP. On the 2025 Form 1040-NR, line 29 is NOT the American
# Opportunity Credit and there is no line 27a at all. Alabama's per-form
# qualifications are precise, and a loader that treats the three 1040 variants as
# interchangeable pulls a Form 1040-C payment into the EIC/AOC slot.
AL_1040NR_LINE29_IS = "Credit for amount paid with Form 1040-C"
AL_1040NR_HAS_EIC_LINE = False


def _yk(table: dict, year: int = FORM_TAX_YEAR):
    if year not in table:
        raise CommandError(f"No TY{year} value in {table!r} - re-verify before extending the year. "
                           "⚠ A new tax year staleness-invalidates every figure in this spec.")
    return table[year]


def _al_line10(col_c, col_b, year: int = FORM_TAX_YEAR):
    """Page 1 line 10 - the Alabama percentage. THREE branches, one source each.

    Face: 'Divide line 9, col. C, by line 9, col. B (not over 100%)'.
    Booklet: 'If the amount in Column C is larger than the amount in Column B, you
    should enter 100% on line 10. If the amount in Column C is a loss (less than 0)
    enter 0% on line 10.'

    ⚠⚠ Struck on LINE 9, never line 12. r. 810-3-15-.21(3)(e): 'Alimony paid and
    adoption expenses are not considered in the computation ... the amounts are not
    subtracted from either the numerator or the denominator of the fraction.'
    """
    c, b = float(col_c), float(col_b)
    if c < 0:
        return float(_yk(AL_LINE10_LOSS_FLOOR, year))     # ⚠ A3 - booklet only
    if b <= 0:
        return float(_yk(AL_LINE10_LOSS_FLOOR, year))
    return min(float(_yk(AL_LINE10_CAP, year)), c / b)


def _al_round_line10(pct, year: int = FORM_TAX_YEAR):
    """Round line 10 to the printed precision. ⚠ THE PRINTED FIGURE IS WHAT MULTIPLIES."""
    places = _yk(AL_LINE10_DECIMALS, year)
    return round(float(pct) * 100.0, places) / 100.0


def _al_prorate(amount, line10_pct, year: int = FORM_TAX_YEAR):
    """Apply the Alabama percentage AS PRINTED, then round to whole dollars.

    ⚠ Using the full-precision ratio instead is off by a dollar on real returns -
    proved against a filed return in the test scenarios.
    """
    return math.floor(float(amount) * _al_round_line10(line10_pct, year) + 0.5)


def _al_line10_without_floor(col_c, col_b):
    """The unfloored division - retained ONLY so the harness can prove the floor matters."""
    b = float(col_b)
    if b == 0:
        raise CommandError("division by zero")
    return min(1.0, float(col_c) / b)


def _al_standard_deduction(filing_status: str, col_b_line12, year: int = FORM_TAX_YEAR):
    """Booklet p.9 chart. ⚠ Keyed on COLUMN B line 12 - ALL-SOURCES AGI.

    ⚠⚠ The chart amount is then PRORATED by line 10 (booklet: 'The Standard
    Deduction must be prorated by the percentage on page 1, line 10.'), so the
    all-source figure sizes it and the Alabama percentage shrinks it. Two different
    figures doing two different jobs.
    """
    if filing_status not in FILING_STATUSES:
        raise CommandError(f"Unknown filing status {filing_status!r}.")
    agi = float(col_b_line12)
    for lo, hi, amt in _yk(AL_STANDARD_DEDUCTION, year)[filing_status]:
        if agi >= lo and (hi is None or agi <= hi):
            return float(amt)
    raise CommandError(f"No standard-deduction band covers {agi} for {filing_status} - the chart "
                       "must be exhaustive; a gap means a band was mistranscribed.")


def _al_dependent_exemption(col_b_line12, dependents: int, year: int = FORM_TAX_YEAR):
    """Page 2 Part V. ⚠ Also keyed on COLUMN B line 12, then prorated by line 10."""
    agi = float(col_b_line12)
    for lo, hi, amt in _yk(AL_DEPENDENT_EXEMPTION, year):
        if agi >= lo and (hi is None or agi <= hi):
            return float(amt) * int(dependents)
    raise CommandError(f"No dependent-exemption band covers {agi}.")


def _al_tax(taxable_income, filing_status: str, year: int = FORM_TAX_YEAR):
    """Page 1 line 19, from the booklet's tax table (pp.21-26).

    ⚠⚠ HEAD OF FAMILY IS IN THE *SINGLE* COLUMN, not the MFJ column. It takes the
    MFJ-sized $3,000 personal exemption and its own standard-deduction table, but
    the single rate brackets.

    The printed table is banded in $100 increments and computes at the BAND
    MIDPOINT - which is why the printed figures are not what a naive
    exact-income computation gives. Above $100,000 the table is replaced by a
    printed worksheet whose constants are used as published.
    """
    if filing_status not in AL_TAX_COLUMN:
        raise CommandError(f"Unknown filing status {filing_status!r}.")
    col = AL_TAX_COLUMN[filing_status]
    ti = max(0.0, float(taxable_income))
    ceiling = _yk(AL_TAX_TABLE_CEILING, year)
    if ti >= ceiling:
        const = float(_yk(AL_OVER_100K_CONSTANT, year)[col])
        return (ti - ceiling) * float(_yk(AL_OVER_100K_RATE, year)) + const
    # ⚠ THE FLOOR ROWS ARE $50-WIDE AND PRINT 0 / 1 - see AL_TAX_TABLE_FLOOR_ROWS.
    # They are read straight off the table; computing them gives 1 and 2 instead.
    floor_ceiling = _yk(AL_TAX_TABLE_FLOOR_CEILING, year)
    if ti < floor_ceiling:
        fband = _yk(AL_TAX_TABLE_FLOOR_BAND, year)
        row = int(math.floor(ti / fband) * fband)
        rows = _yk(AL_TAX_TABLE_FLOOR_ROWS, year)
        if row not in rows:
            raise CommandError(
                f"AL tax table floor row {row!r} is not encoded for {year}; "
                f"known rows {sorted(rows)}. Refusing to compute it."
            )
        return float(rows[row])
    band = _yk(AL_TAX_TABLE_BAND, year)
    midpoint = (math.floor(ti / band) * band) + band / 2.0
    remaining, tax = midpoint, 0.0
    for width, rate in _yk(AL_TAX_BRACKETS, year)[col]:
        if remaining <= 0:
            break
        slice_ = remaining if width is None else min(remaining, width)
        tax += slice_ * float(rate)
        remaining -= slice_
    return math.floor(tax + 0.5)          # the table prints whole dollars


def _al_part2_line8(amounts_by_line: dict, column: str):
    """Page 2 Part II line 8 - the asymmetric summation.

    Face, verbatim: 'Add lines 1 through 7, Column B, and lines 1, 3 through 7,
    Column C.' ⚠⚠ COLUMN C OMITS LINE 2 (penalty on early withdrawal of savings),
    and the booklet agrees: 'Enter this amount on line 2, COLUMN B ONLY.'

    Summing the same seven lines in both columns is wrong, and wrong QUIETLY: the
    totals look plausible while line 10 shifts and every proration shifts with it.
    """
    lines = AL_PART2_SUM_COL_B if column == "B" else AL_PART2_SUM_COL_C
    return sum(float(amounts_by_line.get(n, 0)) for n in lines)


def _al_fit_worksheet(tax_1040_l22, niit_8960_l17, eic, actc, aoc, adoption, form_2439):
    """Booklet p.27 / packet p.40 - the Federal Income Tax Deduction Worksheet.

    L3 = L1 + L2 (tax + NIIT); L5 = the five refundable credits;
    L6 = L3 - L5, 'If amount is negative enter zero'.

    ⚠ The base is tax AFTER nonrefundable credits but BEFORE other taxes - 1040
    line 23 (self-employment tax etc.) is deliberately OUTSIDE it.
    """
    base = float(tax_1040_l22) + float(niit_8960_l17)
    credits = sum(float(x) for x in (eic, actc, aoc, adoption, form_2439))
    return max(0.0, base - credits)


def _al_part4_line7_form(fit_liability, taxpayer_federal_agi, spouse_federal_agi,
                         line10_pct, mfs_on_alabama_joint_on_federal: bool):
    """⚠⚠ A1 AS RULED - Part IV line 7, BUILT TO THE FORM.

    Face line 7, verbatim: 'If you completed lines 1-3 above, multiply line 5 by
    percentage on line 6. Otherwise, multiply line 4 by percentage on line 6.'
    Gate: 'If you are filing separately on your Alabama return and jointly on your
    Federal return, complete all lines below. Otherwise, omit lines 1 through 3.'

    So in the MFS-on-Alabama case the deduction is reduced FIRST by the taxpayer's
    share of joint federal AGI (line 3), THEN by the Alabama percentage (line 6).
    """
    fit = float(fit_liability)
    if mfs_on_alabama_joint_on_federal:
        joint = float(taxpayer_federal_agi) + float(spouse_federal_agi)
        if joint <= 0:
            raise CommandError("joint federal AGI must be positive for the Part IV lines 1-3 branch")
        fit = fit * (float(taxpayer_federal_agi) / joint)
    return fit * float(line10_pct)


def _al_part4_line7_regulation(fit_liability, spouse_federal_agi,
                               taxpayer_all_source_line9, taxpayer_alabama_line9):
    """The method Ken did NOT ship - retained so the harness can prove the divergence.

    r. 810-3-15-.21(3)(e)(2)(i): '... the Alabama percentage of adjusted total income
    IS NOT USED to prorate the federal income tax deduction. (I) The taxpayer's
    Alabama adjusted total income is divided by the sum of the spouse's federal
    adjusted gross income and the taxpayer's adjusted total income from all sources.
    (II) The percentage computed in subparagraph (I) is then applied to the amount
    of the federal income tax liability ...'

    ⚠⚠ Algebraically IDENTICAL to the form whenever the taxpayer's federal AGI
    equals their Alabama all-source adjusted total income. The two diverge exactly
    to the extent column B departs from federal AGI - and column B is NOT federal
    AGI (r. 810-3-15-.21(2): what 'would be included in gross income if received by
    a resident of the State of Alabama').
    """
    denom = float(spouse_federal_agi) + float(taxpayer_all_source_line9)
    if denom <= 0:
        raise CommandError("the regulation's denominator must be positive")
    return float(fit_liability) * (float(taxpayer_alabama_line9) / denom)


def _al_schedule_a(prorated_subtotal, line10_pct, casualty_loss, casualty_agi_col_c,
                   job_expenses, job_agi_col_c, year: int = FORM_TAX_YEAR):
    """Schedule A (Form 40NR) lines 21-30. ⚠⚠ THE PRORATION LIVES ON THE SCHEDULE.

    L21 'Total itemized deductions to be prorated. (Add lines 4, 9, 14, 18, 19, and 20.)'
    L22 'Enter percentage (%) from Form 40NR, page 1, line 10.'
    L23 'Multiply line 21 by the percentage on line 22.'
    L24a-c Alabama casualty and theft - floor 10% of line 12 COLUMN C
    L25-29 Alabama job-related expenses - floor 2% of line 12 COLUMN C
    L30 'Add the amounts on lines 23, 24c, and 29.' -> page 1 line 13, box 13a

    ⚠⚠ A4 (D-32): 24c and 29 enter UNPRORATED. The booklet's line-21 instruction
    scopes the proration explicitly - 'The amounts shown in LINES 1 THROUGH 20
    should be the amounts for the entire period that the return covers' - so 24a-c
    are outside it by construction, and reg (3)(d) agrees.
    """
    # ⚠ Whole dollars throughout - the floors are rounded before subtraction, and the
    # proration uses the PRINTED line-10 percentage (see _al_prorate).
    l23 = float(_al_prorate(prorated_subtotal, line10_pct, year))
    l24b = math.floor(float(casualty_agi_col_c) * float(_yk(AL_CASUALTY_FLOOR_PCT, year)) + 0.5)
    l24c = max(0.0, math.floor(float(casualty_loss) + 0.5) - l24b)
    l28 = math.floor(float(job_agi_col_c) * float(_yk(AL_JOB_EXPENSE_FLOOR_PCT, year)) + 0.5)
    l29 = max(0.0, math.floor(float(job_expenses) + 0.5) - l28)
    return {"L23": l23, "L24b": l24b, "L24c": l24c, "L28": l28, "L29": l29,
            "L30": l23 + l24c + l29}


def _al_medical_floor(medical_expenses, line12_col_b, year: int = FORM_TAX_YEAR):
    """Schedule A lines 1-4. ⚠⚠ THE MEDICAL FLOOR READS COLUMN B - all sources.

    L2 'Enter amount from Form 40NR, line 12, col. B'; L3 'Multiply the amount on
    line 2 by 4% (.04)'. The casualty and job-expense floors read COLUMN C. Three
    floors, two different columns, on one schedule - encoding them as one AGI is a
    silent error.
    """
    # ⚠ The FLOOR is rounded to whole dollars before subtraction. Established from a
    # filed return: 4% x 39,693 = 1,587.72, and the filed line reads 12,751 - 1,588
    # = 11,163. Carrying the floor to cents gives 11,163.28 and prints a different
    # whole-dollar figure on some returns.
    floor = math.floor(float(line12_col_b) * float(_yk(AL_MEDICAL_FLOOR_PCT, year)) + 0.5)
    return max(0.0, math.floor(float(medical_expenses) + 0.5) - floor)


def _al_vehicle_loan_interest(interest_paid, line12_col_b, filing_status: str,
                              year: int = FORM_TAX_YEAR):
    """NEW for TY2025 - the Qualified Vehicle Loan Interest Worksheet.

    L2 'Enter the smaller of the amount on line 1 or $10,000'
    L3 'Enter the amount from Form 40NR, line 12, Col. B'      <- ⚠ ALL SOURCES
    L4 'Enter $100,000 ($200,000 if married filing jointly)'
    L6 'Divide line 5 by $1,000. If the resulting number isn't a whole number,
        INCREASE THE RESULT TO THE NEXT HIGHER WHOLE NUMBER.'  <- ⚠ always UP
    L7 'Multiply line 6 by $200'      L8 = L2 - L7, floored at zero

    ⚠ The phase-out is measured on WORLDWIDE AGI even though only Alabama income is
    taxed, and line 6 rounds UP always - so any excess at all costs a full $200.
    """
    l2 = min(float(interest_paid), float(_yk(AL_VEHICLE_LOAN_CAP, year)))
    start = _yk(AL_VEHICLE_LOAN_PHASEOUT_START, year)[filing_status]
    l5 = float(line12_col_b) - float(start)
    if l5 <= 0:
        return l2
    steps = math.ceil(l5 / _yk(AL_VEHICLE_LOAN_PHASEOUT_STEP, year))    # ⚠ always UP
    l7 = steps * _yk(AL_VEHICLE_LOAN_PHASEOUT_PER_STEP, year)
    return max(0.0, l2 - l7)


def _al_retirement_columns(gross_distribution, taxable_to_an_alabama_resident: bool):
    """⚠⚠ THE CATEGORICAL RULE. Returns (column_B, column_C).

    Column C is ALWAYS ZERO - r. 810-3-14-.05 enumerates a nonresident's Alabama
    gross income exhaustively and pensions appear nowhere in it. Column B carries
    the distribution iff a RESIDENT would be taxed on it (r. 810-3-15-.21(2)).

    ⚠⚠ Geography plays no part. A distribution is not excluded from column B for
    being 'out of state'; it is excluded only if its PLAN TYPE is on Schedule RS
    Part I's exempt list.
    """
    return (float(gross_distribution) if taxable_to_an_alabama_resident else 0.0), 0.0


def _al_retirement_column_b(legs, year: int = FORM_TAX_YEAR):
    """⚠⚠ Column B, NET of the Schedule RS line-10 exclusion, PER TAXPAYER.

    `legs` = [(gross, exempt_by_plan_type, age), ...] — one entry per taxpayer.

    ⚠ Two INDEPENDENT mechanisms reach the same destination and a joint return can
    need one for each spouse:
      * PLAN TYPE (Part I exempt list, § 414(j) defined benefit) removes the
        distribution from column B entirely.
      * AGE 65+ (Part II/III line 10) excludes up to $6,000 of what remains.
    Modelling them with one return-level flag forces both spouses to the same answer,
    which is how AL40NR-H came to assert a figure it could not have computed.
    """
    total = 0.0
    for gross, exempt, age in legs:
        col_b, _ = _al_retirement_columns(gross, not exempt)
        total += max(0.0, col_b - _al_retirement_exclusion(col_b, age, year))
    return total


def _al_retirement_exclusion(taxable_retirement_to_alabama, age, year: int = FORM_TAX_YEAR):
    """⚠ A2 - Schedule RS Part II/III line 10, PER TAXPAYER."""
    if int(age) < _yk(AL_RETIREMENT_EXCLUSION_AGE, year):
        return 0.0
    return min(float(_yk(AL_RETIREMENT_EXCLUSION, year)), max(0.0, float(taxable_retirement_to_alabama)))


AUTHORITY_TOPICS: list[tuple[str, str]] = [
    # Keep under 255 - the loader guards it (campaign D-17).
    ("al_40nr_nonresident", "Alabama Form 40NR: the three-column structure, the line-10 allocation "
     "percentage and the five figures it prorates, the categorical nonresident retirement rule, and "
     "the defective published standard-deduction chart."),
]

# ⚠⚠ TWO-WRITERS GUARD (D-31): these rows are OWNED by the seeded AL loaders.
# This spec REFERENCES them and never re-declares them.
EXISTING_SOURCES_TO_REFERENCE: list[str] = [
    "AL_CODE_40_18_15",          # § 40-18-15 - deductions, incl. the standard-deduction subsection
    "AL_CODE_40_18_5",           # § 40-18-5 - the 2/4/5% individual rate schedule
    "AL_2025_FORM_40",           # the RESIDENT return - the sibling this form must not be cloned from
    "AL_2025_FORM_40_BOOKLET",   # ⚠ carries the IDENTICAL defective chart - evidence for U9
]

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "AL_2025_FORM_40NR", "source_type": "state_form",
        "source_rank": "primary_official", "jurisdiction_code": "AL",
        "title": "2025 Alabama Form 40NR - Individual Income Tax Return, Nonresidents Only",
        "citation": "Alabama Form 40NR (2025), 25f40nr.pdf / 25f40nrblk.pdf",
        "issuer": "Alabama Department of Revenue",
        "official_url": "https://www.revenue.alabama.gov/individual-corporate/individual-income-tax/",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.5,
        "topics": ["al_40nr_nonresident"],
        "excerpts": [
            {
                "excerpt_label": "The page-1 spine, and why line 10 reads line 9 (verbatim)",
                "excerpt_text": (
                    "L5 'Wages, salaries, tips, etc. (From Schedule W-2, line 18, columns G, H, and I.)'; "
                    "L7 'Total income. Add amounts in col. B then add amounts in col. C, lines 5 and 6'; "
                    "L9 'Adjusted total income. Subtract line 8 from line 7'; L10 'Alabama percentage of "
                    "adjusted total income. Divide line 9, col. C, by line 9, col. B (not over 100%)'; "
                    "L11 'Other Adjustments (from page 2, Part III, line 4 and line 6)'; L12 'Adjusted "
                    "Gross Income. Subtract line 11 from line 9'; L15 'Personal exemption (multiply line 1, "
                    "2, 3, or 4 by percentage on line 10)'; L18 'Taxable income. Subtract line 17 from line "
                    "12, column C'. Columns: 'A - Alabama Tax Withheld', 'B - All Sources', 'C - Alabama "
                    "Income'. Face banner: 'You Must Attach a Complete copy of Federal Return, if claiming "
                    "a deduction on line 14.'"
                ),
                "summary_text": "⚠⚠ Line 10 is struck on LINE 9, not line 12 - alimony paid and adoption "
                                "expenses (line 11) are subtracted AFTER the percentage. The ordering is "
                                "load-bearing and the regulation states it explicitly.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "⚠⚠ Part II line 8 sums DIFFERENT LINE SETS per column",
                "excerpt_text": (
                    "Page 2, Part II line 8, verbatim: 'Add lines 1 through 7, Column B, and lines 1, 3 "
                    "through 7, Column C.' COLUMN C OMITS LINE 2 - the penalty on early withdrawal of "
                    "savings. The booklet agrees: 'Enter this amount on line 2, COLUMN B ONLY. (Be sure to "
                    "include the interest income on Part I, line 1, column B.)' ⚠ Part IV line 7: 'If you "
                    "completed lines 1-3 above, multiply line 5 by percentage on line 6. Otherwise, "
                    "multiply line 4 by percentage on line 6', gated by 'If you are filing separately on "
                    "your Alabama return and jointly on your Federal return, complete all lines below.'"
                ),
                "summary_text": "A build that sums the same seven lines in both columns is wrong QUIETLY - "
                                "the totals look plausible while line 10 shifts and every proration with it.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "⚠⚠ Schedule A - the proration is ON the schedule, and three floors read TWO columns",
                "excerpt_text": (
                    "Schedule A (Form 40NR), scanline *2500074N*: L2 'Enter amount from Form 40NR, line 12, "
                    "col. B'; L3 'Multiply the amount on line 2 by 4% (.04)'; L21 'Total itemized "
                    "deductions to be prorated. (Add lines 4, 9, 14, 18, 19, and 20.)'; L22 'Enter "
                    "percentage (%) from Form 40NR, page 1, line 10.'; L23 'Multiply line 21 by the "
                    "percentage on line 22.'; L24b 'Enter 10% of your Adjusted Gross Income (Form 40NR, "
                    "line 12, column C)'; L28 'Multiply the amount on Form 40NR, line 12, column C by 2% "
                    "(.02)'; sidebar at lines 25-29: 'You may ONLY deduct expenses associated with your "
                    "Alabama income.'; L30 'Add the amounts on lines 23, 24c, and 29 ... enter on Form "
                    "40NR, page 1, line 13 and check 13a, Itemized Deductions.'"
                ),
                "summary_text": "⚠⚠ MEDICAL floors on COLUMN B; CASUALTY and JOB EXPENSES floor on COLUMN "
                                "C. Encoding the three as one AGI is a silent error.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        # ⚠ source_type corrected 2026-08-25 (campaign D-41, Ken: "correct and reseed"). Was "state_instructions" (plural),
        #   which is NOT a SourceType member; Django does not enforce choices on update_or_create.
        "source_code": "AL_2025_BOOKLET_40NR", "source_type": "state_instruction",
        "source_rank": "primary_official", "jurisdiction_code": "AL",
        "title": "2025 Alabama Form 40NR Booklet - Instructions, Tax Tables, Charts, Worksheets",
        "citation": "Alabama Form 40NR Booklet (2025), 25f40nrbk.pdf (29 pp., Dec 2025)",
        "issuer": "Alabama Department of Revenue",
        "official_url": "https://www.revenue.alabama.gov/individual-corporate/individual-income-tax/",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.0,
        "topics": ["al_40nr_nonresident"],
        "excerpts": [
            {
                "excerpt_label": "⚠⚠ RETIREMENT IS NOT A SOURCING QUESTION (verbatim, p.11)",
                "excerpt_text": (
                    "'Pension and annuity payments received by a nonresident are NOT SUBJECT TO ALABAMA "
                    "TAX. However, pension and annuity payments you received in 2025 THAT WOULD BE TAXABLE "
                    "TO A RESIDENT OF ALABAMA must be included in the total adjusted gross income from all "
                    "sources in order to compute the ratio of Alabama adjusted gross income to total "
                    "adjusted gross income from all sources'. The same categorical treatment at Line 2 "
                    "Alimony Received: 'Alimony and separate maintenance payments received by a nonresident "
                    "of Alabama in 2025 are not taxable for Alabama purposes. However, any amounts you "
                    "received in 2025 must be included in the total adjusted gross income from all sources "
                    "... The amount received should be listed in COLUMN B ONLY.' The exempt list is by PLAN "
                    "TYPE: Alabama Teachers'/Employees'/Judicial Retirement, US Civil Service Retirement, "
                    "Social Security systems, Railroad Retirement, Military Retirement Pay, TVA Pension, US "
                    "Foreign Service, US Government Retirement, and 'Any Defined Benefit Retirement Plan in "
                    "accordance with IRC 414(j)'."
                ),
                "summary_text": "⚠⚠ Column C is ALWAYS zero for pensions; column B carries them anyway, so "
                                "untaxed retirement income still SHRINKS every prorated deduction. § 414(j) "
                                "is defined BENEFIT - an IRA is not on the list.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "⚠ A3 - the line-10 zero floor, and A4 - the line-21 proration scope",
                "excerpt_text": (
                    "Line 10, verbatim: 'If the amount in Column C is larger than the amount in Column B, "
                    "you should enter 100% on line 10. IF THE AMOUNT IN COLUMN C IS A LOSS (LESS THAN 0) "
                    "ENTER 0% ON LINE 10.' ⚠ The form face carries 'not over 100%' but NO loss rule, in "
                    "either edition, and r. 810-3-15-.21 is silent - one authority only. Line 21, verbatim: "
                    "'The amounts shown in LINES 1 THROUGH 20 should be the amounts for the entire period "
                    "that the return covers. In most cases, these amounts will be the same as shown on your "
                    "Federal return. Follow the instructions on lines 21 through 23 to determine the "
                    "portion of these expenses that apply to your Alabama income.' Lines 24a-c: 'A "
                    "nonresident of Alabama may deduct only those losses where the property was located in "
                    "Alabama at the time of loss', and 'the amount of EACH separate casualty or theft loss "
                    "is more than $100, and the total amount of ALL Alabama losses during the year is more "
                    "than 10% of your adjusted gross income on Form 40NR, page 1, line 12, column C.' "
                    "Also: 'The Standard Deduction must be prorated by the percentage on page 1, line 10.'"
                ),
                "summary_text": "⚠ A4 closed on evidence: line 21 scopes proration to lines 1-20, so 24a-c "
                                "sit outside it by construction. ⚠ The $100-per-event casualty floor is "
                                "INSTRUCTION-ONLY - it is not on the form face.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "⚠⚠ The DEFECTIVE standard-deduction chart, and the tax-table columns",
                "excerpt_text": (
                    "p.9 chart, both keyed on 'Adjusted Gross Income (Col. B, Line 12)'. MFJ: $0-$25,999 -> "
                    "$8,500; $26,000-$26,499 -> $8,325; ⚠⚠ PRINTED AS '$25,500 - $26,999' -> $8,150 (which "
                    "overlaps bands 1 and 2 and runs backwards); floor $35,500+ -> $5,000. MFS steps in "
                    "$250 bands from $12,999 with -$88; HOF -$135 and Single -$25 in $500 bands, both from "
                    "$25,999, both flooring at $2,500. Dependent exemption: 0-50,000 -> $1,000; "
                    "50,001-100,000 -> $500; over 100,000 -> $300. Tax table pp.21-26, resolved "
                    "positionally: column 1 heads 'Single ✱ Married filing separately ✱ Head of family', "
                    "column 2 heads 'Married filing jointly'. Over $100,000 a worksheet replaces the table: "
                    "taxable - 100,000.00, x .05, + 4,958.00 (col 1) or + 4,918.00 (MFJ)."
                ),
                "summary_text": "⚠⚠ HEAD OF FAMILY SITS IN THE SINGLE COLUMN - $3,000 personal exemption "
                                "like MFJ, its own standard-deduction table, but the single rate brackets.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "AL_2025_SCHEDULE_RS", "source_type": "state_form",
        "source_rank": "primary_official", "jurisdiction_code": "AL",
        "title": "2025 Alabama Schedule RS (Form 40 or Form 40NR) - Retirement Schedule",
        "citation": "Alabama Schedule RS (2025), 25schrsblk.pdf",
        "issuer": "Alabama Department of Revenue",
        "official_url": "https://www.revenue.alabama.gov/individual-corporate/individual-income-tax/",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.0,
        "topics": ["al_40nr_nonresident"],
        "excerpts": [{
            "excerpt_label": "⚠⚠ Part IV routes to COLUMN B, and Part I exempts by PLAN TYPE",
            "excerpt_text": (
                "Part I 'Retirement Distribution(s) Exempt from Alabama Income' - columns A-I: FEIN, IRA, "
                "Distribution Code(s), Account Number, Gross Distribution, State Code, State ID, Alabama "
                "Withheld, REASON EXEMPT. Part II/III 'Fully or Partially Taxable Retirement "
                "Distributions', column I 'Taxable to Alabama'. Part II line 10 / Part III line 10, "
                "verbatim: 'RETIREMENT EXCLUSION. Is the primary taxpayer 65 or older and receives taxable "
                "retirement? ... If Yes, EACH TAXPAYER is eligible up to $6,000 not to exceed the "
                "Retirement Income Taxable to Alabama on line 9.' Part IV line 3, verbatim: 'Total Alabama "
                "Taxable Retirement Distribution. Add lines 1 and 2. Enter the amount here and on Form 40, "
                "Page 2, Part 1, Line 4 or FORM 40NR, PAGE 2, PART 1, LINE 3, COLUMN B'."
            ),
            "summary_text": "⚠⚠ Part IV's routing to COLUMN B is not a drafting slip - it is the "
                            "categorical rule expressed on the form. Column C is never populated from "
                            "Schedule RS. ⚠ $6,000 appears NOWHERE in the 40NR booklet, either year.",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "AL_ADMIN_810_3_14_05", "source_type": "state_regulation",
        "source_rank": "controlling", "jurisdiction_code": "AL",
        "title": "Ala. Admin. Code r. 810-3-14-.05 - Gross Income Of Nonresidents",
        "citation": "Ala. Admin. Code r. 810-3-14-.05 (auth. Code of Ala. 1975, § 40-18-14)",
        "issuer": "Alabama Department of Revenue",
        "official_url": "https://admincode.legislature.state.al.us/api/rule/810-3-14-.05",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["al_40nr_nonresident"],
        "excerpts": [{
            "excerpt_label": "⚠⚠ The EXHAUSTIVE list of a nonresident's Alabama gross income",
            "excerpt_text": (
                "(1)(a) 'The gross income of a nonresident includes compensation for personal services ONLY "
                "TO THE EXTENT THAT THE SERVICES WERE RENDERED IN THIS STATE.' (2)(a) 'Gross income of a "
                "nonresident includes income from real and/or tangible personal property located within "
                "Alabama, or intangible personal property with a business situs in Alabama.' (3)(a) the "
                "deemed distributive share of an ELECTING Alabama S corporation, Alabama-attributable only; "
                "(3)(c) 'Gross income of a nonresident DOES NOT INCLUDE actual distributions from S "
                "corporations which have not elected to be Alabama S corporations, nor does it include "
                "deemed distributive shares of income (or losses) of such corporations.' (4) a "
                "partnership's Alabama-attributable distributive share plus guaranteed payments; (5) "
                "estate/trust income attributable to Alabama."
            ),
            "summary_text": "⚠⚠ PENSIONS AND ANNUITIES APPEAR NOWHERE IN THIS LIST. That is why column C "
                            "is always zero for retirement income - it is not a sourcing rule, it is an "
                            "absence from the definition of Alabama gross income.",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "AL_ADMIN_810_3_15_21", "source_type": "state_regulation",
        "source_rank": "controlling", "jurisdiction_code": "AL",
        "title": "Ala. Admin. Code r. 810-3-15-.21 - Deductions For Nonresidents",
        "citation": "Ala. Admin. Code r. 810-3-15-.21 (auth. §§ 40-2A-7(a)(5), 40-18-15)",
        "issuer": "Alabama Department of Revenue",
        "official_url": "https://admincode.legislature.state.al.us/api/rule/810-3-15-.21",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["al_40nr_nonresident"],
        "excerpts": [
            {
                "excerpt_label": "⚠⚠ COLUMN B IS DEFINED HERE, and it is NOT federal AGI",
                "excerpt_text": (
                    "(2), verbatim: 'The phrase \"adjusted gross income from all sources\" is comprised of "
                    "income which would be included in gross income IF RECEIVED BY A RESIDENT OF THE STATE "
                    "OF ALABAMA in accordance with § 40-18-14, Code of Ala. 1975, less the deductions "
                    "described in § 40-18-14.2.' (3)(e), verbatim: 'Nonresidents must divide the amount of "
                    "their Alabama adjusted total income by the amount of their adjusted total income from "
                    "all sources ... ALIMONY PAID AND ADOPTION EXPENSES ARE NOT CONSIDERED IN THE "
                    "COMPUTATION of the Alabama percentage of adjusted total income - the amounts are not "
                    "subtracted from either the numerator or the denominator of the fraction.' (3)(e)(1) "
                    "prorates the personal and dependent exemptions; (3)(e)(3) the optional standard "
                    "deduction; (3)(e)(4) itemized deductions item by item."
                ),
                "summary_text": "⚠⚠ Column B is what a RESIDENT would include, not federal AGI. That single "
                                "fact drives both the retirement rule and the A1 divergence.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "⚠ A1 - the regulation's MFS method, which is NOT what ships",
                "excerpt_text": (
                    "(3)(e)(2)(i), verbatim: 'If the taxpayer is filing separately on the Alabama return, "
                    "but jointly on the federal return, an intermediate computation is performed before the "
                    "federal income tax deduction is prorated, and THE ALABAMA PERCENTAGE OF ADJUSTED TOTAL "
                    "INCOME IS NOT USED to prorate the federal income tax deduction. (I) The taxpayer's "
                    "Alabama adjusted total income is divided by the sum of the spouse's federal adjusted "
                    "gross income and the taxpayer's adjusted total income from all sources. (II) The "
                    "percentage computed in subparagraph (I) is then applied to the amount of the federal "
                    "income tax liability as shown on the current federal income tax return.' ⚠ (3)(d) "
                    "limits casualty losses to Alabama-located property with the limits applied to Alabama "
                    "AGI, while (3)(e)(4)(iii) lists casualty among the prorated deductions - the specific "
                    "provision governs (campaign D-32 A4)."
                ),
                "summary_text": "⚠⚠ Ken ruled BUILD THE FORM (D-32 A1). The methods coincide whenever "
                                "federal AGI equals Alabama all-source income and diverge only as they "
                                "differ - and Part IV's printed lines must foot.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        # ⚠ source_type corrected 2026-08-25 (campaign D-41, Ken: "correct and reseed"). Was "state_instructions" (plural),
        #   which is NOT a SourceType member; Django does not enforce choices on update_or_create.
        "source_code": "AL_2026_WH_TAX_TABLES", "source_type": "state_instruction",
        "source_rank": "primary_official", "jurisdiction_code": "AL",
        "title": "Alabama Withholding Tax Tables and Instructions for Employers (Jan 2026)",
        "citation": "whbooklet_0126.pdf, pp. 7 and 9", "issuer": "Alabama Department of Revenue",
        "official_url": "https://www.revenue.alabama.gov/wp-content/uploads/2026/01/whbooklet_0126.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.0,
        "topics": ["al_40nr_nonresident"],
        "excerpts": [{
            "excerpt_label": "⚠⚠ THE SOURCE THAT RESOLVES THE DEFECTIVE CHART (U9)",
            "excerpt_text": (
                "p.7, as a FORMULA, verbatim: 'Employee claims \"Married Filing Jointly (M)\" exemption: "
                "- GI of $25,999 or less deduct $8,500 - GI greater than $25,999 but less than $35,500 "
                "deduct $8,500 LESS $175 FOR EACH $500 INCREMENT OR PART THEREOF OF GI ABOVE $25,999 - GI "
                "of $35,500 or more deduct $5,000.' Parallel formulas give Single -$25, MFS -$88 per $250 "
                "increment above $12,999, and Head of Family -$135. p.9, as the SAME 21-band schedule, MFJ "
                "band 3 reads '$ 26,500 - $ 26,999   $ 8,150'. Dependents, p.7: '$1,000 if gross income "
                "less than or equal to $50,000 - $500 if gross income greater than $50,000 but less than or "
                "equal to $100,000 - $300 if gross income greater than $100,000.'"
            ),
            "summary_text": "⚠⚠ An INDEPENDENTLY TYPESET first-party DOR publication that states the rule "
                            "TWICE. The income-tax booklets cannot settle the defect - Form 40, 40A and "
                            "40NR across TWO tax years reprint it from one shared piece of artwork.",
            "is_key_excerpt": True,
        }],
    },
    {
        # ⚠ source_type corrected 2026-08-25 (campaign D-41, Ken: "correct and reseed"). Was "federal_form",
        #   which is NOT a SourceType member; Django does not enforce choices on update_or_create.
        "source_code": "AL_40NR_IRS_2025_HANDOFF", "source_type": "official_form",
        "source_rank": "primary_official", "jurisdiction_code": "US",
        "title": "FINAL TY2025 IRS Forms 1040, 1040-NR, Schedule 3 and 8960 - the 40NR federal handoff",
        "citation": "2025 Form 1040 / 1040-NR / Schedule 3 / Form 8960",
        "issuer": "Internal Revenue Service", "official_url": "https://www.irs.gov/pub/irs-pdf/f1040.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["al_40nr_nonresident"],
        "excerpts": [{
            "excerpt_label": "⚠⚠ THE 1040-NR TRAP - line 29 is NOT the American Opportunity Credit",
            "excerpt_text": (
                "Alabama disclaims its own federal line references: 'The Federal line references were "
                "correct at the time these forms and instructions were printed. However, there may have "
                "been changes to Federal forms after our print deadline...' ALL SEVEN WERE RE-VERIFIED "
                "AGAINST THE FINAL TY2025 FORMS AND ARE CORRECT: 1040 and 1040-NR line 22 both read "
                "'Subtract line 21 from line 18. If zero or less, enter -0-'; 8960 line 17 'Net investment "
                "income tax for individuals'; 1040 line 27a 'Earned income credit (EIC)'; line 28 "
                "'Additional child tax credit (ACTC) from Schedule 8812'; line 29 'American opportunity "
                "credit from Form 8863, line 8'; line 30 'Refundable adoption credit from Form 8839, line "
                "13'; Schedule 3 Part II line 13a 'Form 2439'. ⚠⚠ BUT on the 2025 Form 1040-NR, LINE 29 IS "
                "'Credit for amount paid with Form 1040-C' AND THERE IS NO LINE 27a AT ALL. Alabama "
                "correctly cites 1040/1040-SR only for the EIC and AOC lines - the omission is precision, "
                "not oversight."
            ),
            "summary_text": "⚠⚠ A loader that treats the three 1040 variants as interchangeable pulls a "
                            "Form 1040-C payment into the EIC/AOC slot and silently understates the "
                            "federal-tax deduction base.",
            "is_key_excerpt": True,
        }],
    },
]

AUTHORITY_FORM_LINKS: list[tuple] = [
    ("AL_2025_FORM_40NR", "AL_FORM_40NR", "governs"),
    ("AL_2025_BOOKLET_40NR", "AL_FORM_40NR", "governs"),
    ("AL_2025_SCHEDULE_RS", "AL_FORM_40NR", "governs"),
    ("AL_ADMIN_810_3_14_05", "AL_FORM_40NR", "governs"),
    ("AL_ADMIN_810_3_15_21", "AL_FORM_40NR", "governs"),
    ("AL_2026_WH_TAX_TABLES", "AL_FORM_40NR", "governs"),
    ("AL_40NR_IRS_2025_HANDOFF", "AL_FORM_40NR", "informs"),
    ("AL_CODE_40_18_15", "AL_FORM_40NR", "governs"),
    ("AL_CODE_40_18_5", "AL_FORM_40NR", "governs"),
    ("AL_2025_FORM_40_BOOKLET", "AL_FORM_40NR", "informs"),
    ("AL_2025_FORM_40", "AL_FORM_40NR", "informs"),
]

F_FACTS: list[dict] = [
    {"fact_key": "filing_status", "label": "Filing status (single / mfj / mfs / hof)",
     "data_type": "string", "required": True, "sort_order": 1,
     "notes": "⚠⚠ Head of Family takes the MFJ-sized $3,000 personal exemption and its OWN "
              "standard-deduction table, but the SINGLE rate brackets. Three different groupings of "
              "the same four statuses on one return."},
    {"fact_key": "is_nonresident_alien", "label": "Filing status 3 'NRA' box - nonresident alien",
     "data_type": "boolean", "required": False, "sort_order": 2,
     "notes": "⚠ Booklet: a nonresident alien's federal-tax deduction uses the ratio of Alabama source "
              "income to income from sources WITHIN THE UNITED STATES - a different denominator. "
              "Nothing on the face says the ratio changes."},
    {"fact_key": "mfs_on_alabama_joint_on_federal", "label": "Filing separately on Alabama, jointly on federal?",
     "data_type": "boolean", "required": False, "sort_order": 3,
     "notes": "⚠⚠ A1: gates Part IV lines 1-3. Ken ruled BUILD THE FORM (two multiplications), with a "
              "diagnostic where it diverges from r. 810-3-15-.21(3)(e)(2)(i)'s single fraction."},
    {"fact_key": "wages_all_sources", "label": "L5 col. B Wages (Schedule W-2 line 18 column H)",
     "data_type": "decimal", "required": False, "sort_order": 4,
     "notes": "⚠ Booklet: 'State of Alabama employees will find that the amount taxable for state "
              "purposes is, in most cases, MORE than the amount taxable for federal purposes' - AL "
              "Retirement System contributions are federally deferred but not state-deferred."},
    {"fact_key": "wages_alabama", "label": "L5 col. C Wages (Schedule W-2 line 18 column I)",
     "data_type": "decimal", "required": False, "sort_order": 5},
    {"fact_key": "other_income_all_sources", "label": "L6 col. B Other income (page 2 Part I line 9)",
     "data_type": "decimal", "required": False, "sort_order": 6},
    {"fact_key": "other_income_alabama", "label": "L6 col. C Other income (page 2 Part I line 9)",
     "data_type": "decimal", "required": False, "sort_order": 7},
    {"fact_key": "retirement_distributions", "label": "Schedule RS gross retirement distributions",
     "data_type": "decimal", "required": False, "sort_order": 8,
     "notes": "⚠⚠ Column C is ALWAYS ZERO. Column B carries the distribution iff a RESIDENT would be "
              "taxed on it. Geography is irrelevant - Part I exempts by PLAN TYPE."},
    {"fact_key": "retirement_exempt_by_plan_type", "label": "Is the plan on Schedule RS Part I's exempt list?",
     "data_type": "boolean", "required": False, "sort_order": 9,
     "notes": "⚠⚠ The list reaches DEFINED BENEFIT plans under IRC § 414(j). An IRA or 401(k) is "
              "defined CONTRIBUTION and is NOT on it. 'Out of state' is not a reason."},
    # ⚠⚠ PER-TAXPAYER retirement, added 2026-08-25 (Ken: "wire the exclusion in properly").
    #    The return-level pair above cannot express a joint return where the two spouses'
    #    plans differ - which is the ACTUAL shape of the case that exposed this: one
    #    spouse's IRAs are NOT exempt-listed and are zeroed by their own age exclusion,
    #    while the other's RSA pension is exempt-listed and never enters either column.
    #    A single boolean forces both to the same answer.
    {"fact_key": "primary_retirement_distributions", "label": "Primary's gross retirement distributions (Sch RS Part II)",
     "data_type": "decimal", "required": False, "sort_order": 8.1,
     "notes": "Schedule RS Part II line 9. Falls back to retirement_distributions when the return-level "
              "shorthand is used (single filer, or both spouses' plans treated alike)."},
    {"fact_key": "primary_retirement_exempt_by_plan_type", "label": "Primary's plan on Part I's exempt list?",
     "data_type": "boolean", "required": False, "sort_order": 8.2},
    {"fact_key": "spouse_retirement_distributions", "label": "Spouse's gross retirement distributions (Sch RS Part III)",
     "data_type": "decimal", "required": False, "sort_order": 8.3},
    {"fact_key": "spouse_retirement_exempt_by_plan_type", "label": "Spouse's plan on Part I's exempt list?",
     "data_type": "boolean", "required": False, "sort_order": 8.4},
    {"fact_key": "primary_age", "label": "Primary taxpayer's age (Schedule RS line 10 gate)",
     "data_type": "integer", "required": False, "sort_order": 10},
    {"fact_key": "spouse_age", "label": "Spouse's age (Schedule RS Part III line 10 gate)",
     "data_type": "integer", "required": False, "sort_order": 11,
     "notes": "⚠ A2: the $6,000 exclusion is PER TAXPAYER - primary and spouse have separate lines."},
    {"fact_key": "adjustments_part2", "label": "L8 Adjustments to income (page 2 Part II line 8)",
     "data_type": "decimal", "required": False, "sort_order": 12,
     "notes": "⚠⚠ Column C OMITS line 2 (penalty on early withdrawal of savings). The face and the "
              "booklet agree; summing the same seven lines in both columns is wrong QUIETLY."},
    {"fact_key": "early_withdrawal_penalty", "label": "Part II line 2 Penalty on early withdrawal of savings",
     "data_type": "decimal", "required": False, "sort_order": 13,
     "notes": "⚠ 'Enter this amount on line 2, COLUMN B ONLY.' ⚠ 'Penalties on early withdrawal from "
              "RETIREMENT PLANS are not deductible.'"},
    {"fact_key": "other_adjustments_part3", "label": "L11 Other adjustments - alimony paid, adoption expenses",
     "data_type": "decimal", "required": False, "sort_order": 14,
     "notes": "⚠⚠ Subtracted AFTER line 10 is struck. The regulation is explicit that these are in "
              "neither the numerator nor the denominator of the percentage."},
    {"fact_key": "itemize", "label": "L13 box - itemized (13a) or standard (13b)?",
     "data_type": "boolean", "required": False, "sort_order": 15,
     "notes": "⚠ MFS lock: 'both spouses must claim the same deduction unless the spouses have lived "
              "apart for the entire year.'"},
    {"fact_key": "schedule_a_prorated_subtotal", "label": "Schedule A L21 Total itemized deductions to be prorated",
     "data_type": "decimal", "required": False, "sort_order": 16,
     "notes": "Sum of Schedule A lines 4, 9, 14, 18, 19 and 20 - the lines the booklet's line-21 "
              "instruction scopes the proration to."},
    {"fact_key": "medical_expenses", "label": "Schedule A L1 Medical and dental expenses",
     "data_type": "decimal", "required": False, "sort_order": 17,
     "notes": "⚠⚠ Floored at 4% of line 12 COLUMN B - all sources. The casualty and job-expense floors "
              "read COLUMN C."},
    {"fact_key": "casualty_loss", "label": "Schedule A L24a Alabama casualty and theft loss",
     "data_type": "decimal", "required": False, "sort_order": 18,
     "notes": "⚠ A4: Alabama-located property only, NOT prorated. Floor 10% of line 12 col. C, plus an "
              "INSTRUCTION-ONLY $100-per-event floor that is not on the form face."},
    {"fact_key": "job_related_expenses", "label": "Schedule A L25-27 Alabama job-related expenses",
     "data_type": "decimal", "required": False, "sort_order": 19,
     "notes": "⚠ 'You may ONLY deduct expenses associated with your Alabama income.' Floor 2% of line "
              "12 col. C. ⚠ Schedule A line 20's miscellaneous deductions are EXEMPT from the 2% limit."},
    {"fact_key": "vehicle_loan_interest", "label": "Schedule A L11a/11b Qualified vehicle loan interest",
     "data_type": "decimal", "required": False, "sort_order": 20,
     "notes": "⚠ NEW for TY2025. Capped at $10,000, phased out on line 12 COLUMN B from $100,000 "
              "($200,000 MFJ), and line 6 of the worksheet rounds UP always."},
    {"fact_key": "fed_tax_1040_l22", "label": "FIT worksheet L1 - tax from 2025 Form 1040/1040-SR/1040-NR line 22",
     "data_type": "decimal", "required": False, "sort_order": 21,
     "notes": "⚠ Tax AFTER nonrefundable credits but BEFORE other taxes - 1040 line 23 (SE tax) is "
              "deliberately OUTSIDE the base."},
    {"fact_key": "niit_8960_l17", "label": "FIT worksheet L2 - Net Investment Income Tax (Form 8960 line 17)",
     "data_type": "decimal", "required": False, "sort_order": 22},
    {"fact_key": "federal_refundable_credits", "label": "FIT worksheet L4a-4e - the five refundable credits",
     "data_type": "decimal", "required": False, "sort_order": 23,
     "notes": "⚠⚠ EIC (1040 L27a) · ACTC (L28) · AOC (L29) · refundable adoption (L30) · Form 2439 "
              "(Sch 3 Part II L13a). ⚠ On Form 1040-NR line 29 is 'Credit for amount paid with Form "
              "1040-C' and there is NO line 27a - Alabama's per-form qualifications are precise."},
    {"fact_key": "taxpayer_federal_agi", "label": "Part IV L2 - your federal adjusted gross income",
     "data_type": "decimal", "required": False, "sort_order": 24},
    {"fact_key": "joint_federal_agi", "label": "Part IV L1 - your JOINT federal adjusted gross income",
     "data_type": "decimal", "required": False, "sort_order": 25},
    {"fact_key": "dependents", "label": "Part V L1 - total dependents (Schedule DS line 1b)",
     "data_type": "integer", "required": False, "sort_order": 26,
     "notes": "⚠ Alabama's definition is NARROWER than federal: over 50% support AND an enumerated "
              "relationship. 'You cannot claim a foster child, friend, cousin, yourself, or your "
              "spouse as a dependent under Alabama law' - a foster child IS a federal dependent."},
    {"fact_key": "alabama_withholding", "label": "L21 Alabama income tax withheld (col. A line 5)",
     "data_type": "decimal", "required": False, "sort_order": 27},
    {"fact_key": "pte_credit_schedule_cp", "label": "L23 Composite tax payments / Electing PTE credit (Schedule CP)",
     "data_type": "decimal", "required": False, "sort_order": 28},
    {"fact_key": "state_of_residence", "label": "Part VI L1 - state of legal residence in 2025",
     "data_type": "string", "required": False, "sort_order": 29},
]

F_RULES: list[dict] = [
    {"rule_id": "R-AL40NR-L10", "title": "⚠⚠ L10 the Alabama percentage - THREE branches, struck on line 9",
     "rule_type": "calculation",
     "formula": "L10 = 0% if colC < 0 ; else min(100%, line9_colC / line9_colB)",
     "inputs": ["wages_alabama", "other_income_alabama", "adjustments_part2"],
     "outputs": ["L10"], "sort_order": 1,
     "description": "Face: 'Divide line 9, col. C, by line 9, col. B (not over 100%)'. Booklet adds the "
                    "100% case AND the loss case: 'If the amount in Column C is a loss (less than 0) enter "
                    "0% on line 10.' ⚠⚠ A3 (D-32): the zero floor has ONE authority - the face is silent in "
                    "both editions and r. 810-3-15-.21 is silent. Ken ruled it ships anyway because a "
                    "negative percentage propagating into five prorated figures is arithmetically "
                    "indefensible. ⚠⚠ Struck on LINE 9, never line 12: the regulation states that alimony "
                    "paid and adoption expenses are in neither the numerator nor the denominator."},
    {"rule_id": "R-AL40NR-PRORATE", "title": "L10 prorates FIVE figures, and one is invisible on the face",
     "rule_type": "calculation",
     "formula": "personal_exemption, dependent_exemption, federal_tax_deduction, standard_deduction "
                "and itemized_deductions are each multiplied by L10",
     "inputs": ["L10"], "outputs": ["L13", "L14", "L15", "L16"], "sort_order": 2,
     "description": "r. 810-3-15-.21(3)(e) is the authority: (e)(1) personal and dependent exemptions, "
                    "(e)(2) the federal income tax deduction, (e)(3) the optional standard deduction, "
                    "(e)(4) itemized deductions. ⚠ The STANDARD DEDUCTION proration appears NOWHERE on the "
                    "form face - only in the booklet ('The Standard Deduction must be prorated by the "
                    "percentage on page 1, line 10') and the regulation. ⚠ Itemized deductions are prorated "
                    "ON SCHEDULE A ITSELF at lines 21-23, not at line 13."},
    {"rule_id": "R-AL40NR-STDDED", "title": "⚠⚠ Standard deduction chart - keyed on COL. B, and the DOR chart is DEFECTIVE",
     "rule_type": "lookup",
     "formula": "band lookup on line 12 COLUMN B by filing status, then multiplied by L10",
     "inputs": ["filing_status", "L12_col_B"], "outputs": ["L13b"], "sort_order": 3,
     "description": "⚠⚠ The DOR's printed chart gives MFJ band 3 as $25,500-$26,999, which OVERLAPS bands "
                    "1 and 2 and RUNS BACKWARDS - an AGI of ~$25,700 matches two bands and returns either "
                    "$8,500 or $8,150. Form 40, Form 40A and 40NR for BOTH TY2024 and TY2025 reprint the "
                    "identical defect from one shared piece of artwork, so the sibling booklets cannot "
                    "settle it. Resolved to $26,500 against the DOR WITHHOLDING TAX TABLES booklet - "
                    "independently typeset - which states the rule as a formula AND as the same 21-band "
                    "schedule. The printed 25,500 duplicates the statutory phase-down threshold "
                    "(§ 40-18-15(b)) into the row-3 cell. ⚠ Keyed on ALL-SOURCES AGI, then prorated by the "
                    "Alabama percentage: two different figures doing two different jobs."},
    {"rule_id": "R-AL40NR-TAX", "title": "⚠⚠ L19 Tax - TWO columns, and Head of Family is in the SINGLE column",
     "rule_type": "lookup",
     "formula": "band midpoint -> 2/4/5% brackets; single_mfs_hof = 500/2,500/over 3,000 ; "
                "mfj = 1,000/5,000/over 6,000 ; over $100,000 use the printed worksheet constants",
     "inputs": ["L18", "filing_status"], "outputs": ["L19"], "sort_order": 4,
     "description": "⚠⚠ Booklet pp.21-26, resolved POSITIONALLY: column 1 heads 'Single ✱ Married filing "
                    "separately ✱ Head of family'; column 2 heads 'Married filing jointly'. Head of Family "
                    "takes the MFJ-sized $3,000 personal exemption and its OWN standard-deduction table but "
                    "the SINGLE rate brackets - three different groupings of the same four statuses on one "
                    "return. Confirmed against the DOR Withholding booklet, which brackets \"'0', 'S', 'H' "
                    "or 'MS'\" together. ⚠ The printed table computes at the BAND MIDPOINT in $100 bands, "
                    "which is why exact-income arithmetic does not reproduce it. ⚠ Above $100,000 the "
                    "published worksheet constants (+4,958.00 / +4,918.00) are used AS PUBLISHED - both sit "
                    "~$2 below the exact bracket computation because they carry the table's own convention."},
    {"rule_id": "R-AL40NR-RETIRE", "title": "⚠⚠ Retirement is CATEGORICAL - column B only, never column C",
     "rule_type": "calculation",
     "formula": ("col_C = 0 always ; per taxpayer: col_B_share = (gross iff taxable to an Alabama "
                 "RESIDENT) MINUS that taxpayer's Schedule RS line-10 exclusion (RS_P2L10 / RS_P3L10, "
                 "floored at 0) ; col_B = primary share + spouse share"),
     "inputs": ["primary_retirement_distributions", "primary_retirement_exempt_by_plan_type",
                "spouse_retirement_distributions", "spouse_retirement_exempt_by_plan_type",
                "retirement_distributions", "retirement_exempt_by_plan_type",
                "RS_P2L10", "RS_P3L10"],
     "outputs": ["P1L3_colB"], "sort_order": 5,
     "description": "⚠⚠ THE SILENT FAILURE ON THIS FORM. Booklet p.11: 'Pension and annuity payments "
                    "received by a nonresident are not subject to Alabama tax. However, pension and annuity "
                    "payments you received in 2025 THAT WOULD BE TAXABLE TO A RESIDENT OF ALABAMA must be "
                    "included in the total adjusted gross income from all sources in order to compute the "
                    "ratio.' r. 810-3-14-.05 enumerates a nonresident's Alabama gross income exhaustively "
                    "and pensions appear NOWHERE in it, so column C is always zero; r. 810-3-15-.21(2) "
                    "defines column B as what a RESIDENT would include, so column B carries it. ⚠⚠ Untaxed "
                    "retirement income therefore SHRINKS every prorated deduction. Drop it from column B "
                    "and line 10 comes out too high, every prorated figure too large, and Alabama tax is "
                    "UNDERSTATED - while the return foots perfectly. ⚠ Schedule RS Part I exempts by PLAN "
                    "TYPE (§ 414(j) is defined BENEFIT), never by location. Schedule RS Part IV line 3 "
                    "routes to 'Form 40NR, page 2, Part 1, Line 3, COLUMN B' - the rule on the form. "
                    "⚠⚠ AMENDED 2026-08-25: Part IV line 3 is fed by Part II/III line 11, which is "
                    "line 9 MINUS line 10 - so column B is NET of the $6,000 age-65 exclusion "
                    "(R-AL40NR-RSEXCL). Until this amendment the two rules named the same form chain "
                    "and did not meet: RSEXCL's outputs fed nothing, so a 65+ taxpayer's column B was "
                    "overstated and the allocation percentage with it. ⭐ PER TAXPAYER on both legs - "
                    "the exemption is by plan type, the exclusion is by age, and a joint return can "
                    "need one for each spouse."},
    {"rule_id": "R-AL40NR-RSEXCL", "title": "A2 - the $6,000 age-65 retirement exclusion, PER TAXPAYER",
     "rule_type": "limitation",
     "formula": "per taxpayer aged 65+: min($6,000, that taxpayer's Alabama-taxable retirement)",
     "inputs": ["primary_age", "spouse_age",
                "primary_retirement_distributions", "primary_retirement_exempt_by_plan_type",
                "spouse_retirement_distributions", "spouse_retirement_exempt_by_plan_type"],
     "outputs": ["RS_P2L10", "RS_P3L10"], "sort_order": 6,
     "description": "⚠ Campaign D-32 A2. Schedule RS Part II line 10 / Part III line 10: 'each taxpayer is "
                    "eligible up to $6,000 not to exceed the Retirement Income Taxable to Alabama on line "
                    "9.' ⚠⚠ The figure $6,000 appears NOWHERE in the 40NR booklet, TY2025 or TY2024 - the "
                    "schedule face is the only source. Ken ruled the booklet's silence is an OMISSION, not "
                    "a conflict, since nothing contradicts the face. PER TAXPAYER because the face gives "
                    "primary and spouse separate lines. ⚠ NOT new for TY2025 - the TY2024 Schedule RS "
                    "carries it verbatim (an adversarial-pass correction)."},
    {"rule_id": "R-AL40NR-PART2", "title": "⚠⚠ Part II line 8 sums DIFFERENT LINE SETS per column",
     "rule_type": "calculation",
     "formula": "col B = sum(lines 1-7) ; col C = sum(lines 1, 3-7)   [line 2 OMITTED from col C]",
     "inputs": ["early_withdrawal_penalty"], "outputs": ["L8"], "sort_order": 7,
     "description": "Face, verbatim: 'Add lines 1 through 7, Column B, and lines 1, 3 through 7, Column C.' "
                    "The booklet corroborates: the early-withdrawal penalty goes 'on line 2, COLUMN B "
                    "ONLY.' ⚠ A build that sums the same seven lines in both columns is wrong QUIETLY - the "
                    "totals look plausible while line 10 shifts and every proration shifts with it. "
                    "⚠ Column-C limits differ per line: IRA/Keogh/SEP is limited to contributions from "
                    "Alabama-source income; moving expenses require the new job location to be IN Alabama; "
                    "and self-employed health insurance uses ITS OWN ratio (Alabama SE income / total SE "
                    "income), not line 10."},
    {"rule_id": "R-AL40NR-SCHEDA", "title": "⚠⚠ Schedule A - proration on the schedule, THREE floors on TWO columns",
     "rule_type": "calculation",
     "formula": "L23 = L21 x L10 ; L24c and L29 enter UNPRORATED ; L30 = L23 + L24c + L29",
     "inputs": ["schedule_a_prorated_subtotal", "casualty_loss", "job_related_expenses"],
     "outputs": ["L13a"], "sort_order": 8,
     "description": "⚠⚠ The itemized proration lives ON Schedule A at lines 21-23, not at page-1 line 13. "
                    "⚠⚠ THREE FLOORS READ TWO DIFFERENT COLUMNS: medical 4% of line 12 COL. B; casualty 10% "
                    "of line 12 COL. C; job expenses 2% of line 12 COL. C. Encoding them as one AGI is a "
                    "silent error. ⚠ A4 (D-32): 24c and 29 are NOT prorated - the booklet's line-21 "
                    "instruction scopes the proration to 'LINES 1 THROUGH 20', putting 24a-c outside it by "
                    "construction, and reg (3)(d) agrees. ⚠ An INSTRUCTION-ONLY $100-per-event casualty "
                    "floor exists that is not on the form face. ⚠ Schedule A line 20's miscellaneous "
                    "deductions are EXEMPT from the 2% limit that applies to the others."},
    {"rule_id": "R-AL40NR-FITDED", "title": "⚠⚠ A1 - the federal income tax deduction, BUILT TO THE FORM",
     "rule_type": "calculation",
     "formula": "worksheet L6 = max(0, 1040_L22 + 8960_L17 - five refundable credits) ; "
                "Part IV L7 = (MFS-on-AL ? L6 x (own federal AGI / joint federal AGI) : L6) x L10",
     "inputs": ["fed_tax_1040_l22", "niit_8960_l17", "federal_refundable_credits",
                "taxpayer_federal_agi", "joint_federal_agi", "mfs_on_alabama_joint_on_federal"],
     "outputs": ["L14"], "sort_order": 9,
     "description": "⚠⚠ Campaign D-32 A1: BUILD THE FORM, diagnose the divergence. The regulation, "
                    "r. 810-3-15-.21(3)(e)(2)(i), says the Alabama percentage 'is not used' in the MFS case "
                    "and gives ONE fraction instead. ⚠ The two are ALGEBRAICALLY IDENTICAL whenever the "
                    "taxpayer's federal AGI equals their Alabama all-source adjusted total income, and "
                    "diverge only as column B departs from federal AGI - in BOTH directions. ⚠⚠ Part IV's "
                    "lines 3/5/6/7 are PRINTED, so the regulation's single fraction would produce a return "
                    "where line 7 != line 5 x line 6. A regulation outranks a form on authority; it does "
                    "not outrank it on what the form must show. ⚠ NONRESIDENT ALIEN: the booklet gives a "
                    "DIFFERENT denominator - income from sources within the United States - and nothing on "
                    "the face says so."},
    {"rule_id": "R-AL40NR-FEDLINES", "title": "⚠⚠ The seven federal line references - and the 1040-NR trap",
     "rule_type": "validation",
     "formula": "1040 L22 tax + 8960 L17 NIIT - (L27a EIC + L28 ACTC + L29 AOC + L30 adoption + "
                "Sch3 II L13a Form 2439), floored at zero",
     "inputs": ["fed_tax_1040_l22", "niit_8960_l17", "federal_refundable_credits"],
     "outputs": ["FIT_L6"], "sort_order": 10,
     "description": "Alabama disclaims its own federal line references. ⚠ ALL SEVEN WERE RE-VERIFIED "
                    "AGAINST THE FINAL TY2025 IRS FORMS AND ARE CORRECT - including the two places Alabama "
                    "deliberately omits Form 1040-NR. ⚠⚠ THE TRAP: on the 2025 Form 1040-NR, line 29 is "
                    "'Credit for amount paid with Form 1040-C', NOT the American Opportunity Credit, and "
                    "there is NO line 27a (EIC) at all. Alabama cites 1040/1040-SR only for those two - the "
                    "omission is precision, not oversight. A loader treating the three variants as "
                    "interchangeable pulls a Form 1040-C payment into the EIC/AOC slot and silently "
                    "UNDERSTATES the deduction base."},
    {"rule_id": "R-AL40NR-VEHICLE", "title": "NEW TY2025 - qualified vehicle loan interest, phased on COLUMN B",
     "rule_type": "limitation",
     "formula": "min(interest, $10,000) - 200 x ceil(max(0, L12_colB - threshold) / 1,000)",
     "inputs": ["vehicle_loan_interest"], "outputs": ["SchA_L11c"], "sort_order": 11,
     "description": "⚠ New for TY2025 - the phrase appears nowhere in the TY2024 booklet. Worksheet L3 "
                    "reads 'Form 40NR, line 12, Col. B', so the phase-out is measured on WORLDWIDE AGI even "
                    "though only Alabama income is taxed - the same column-B asymmetry as the dollar charts "
                    "and the medical floor. ⚠ L6: 'If the resulting number isn't a whole number, INCREASE "
                    "THE RESULT TO THE NEXT HIGHER WHOLE NUMBER. (For example, increase 1.5 to 2, and "
                    "increase 0.05 to 1.)' - so any excess at all costs a full $200."},
    {"rule_id": "R-AL40NR-DEPEND", "title": "Dependent exemption - chart on COL. B, and a NARROWER definition",
     "rule_type": "lookup",
     "formula": "chart(L12 col B) x dependents, then x L10 (Part V lines 2-4)",
     "inputs": ["dependents"], "outputs": ["L16"], "sort_order": 12,
     "description": "Chart: 0-50,000 -> $1,000; 50,001-100,000 -> $500; over 100,000 -> $300, keyed on "
                    "column B line 12 and independently confirmed in the DOR Withholding booklet. ⚠ "
                    "Alabama's dependent definition is NARROWER than federal: over 50% support AND an "
                    "enumerated relationship. 'You cannot claim a foster child, friend, cousin, yourself, "
                    "or your spouse as a dependent under Alabama law' - a foster child IS a federal "
                    "dependent and is NOT an Alabama one. ⚠ MFS: 'you must consider only the amounts you "
                    "separately furnished out of your income.'"},
]

F_RULE_LINKS: list[tuple] = [
    ("R-AL40NR-L10", "AL_2025_FORM_40NR", "governs", "The face's division and the 'not over 100%' cap."),
    ("R-AL40NR-L10", "AL_2025_BOOKLET_40NR", "governs", "⚠ A3 - the ONLY source for the zero floor on a "
     "loss. Recorded as the single authority it is."),
    ("R-AL40NR-L10", "AL_ADMIN_810_3_15_21", "governs", "(3)(e) - the ratio, and that alimony paid and "
     "adoption expenses are in neither the numerator nor the denominator."),
    ("R-AL40NR-PRORATE", "AL_ADMIN_810_3_15_21", "governs", "(3)(e)(1)-(4) - the five prorated figures, "
     "including the standard deduction, which the form face never mentions."),
    ("R-AL40NR-STDDED", "AL_2026_WH_TAX_TABLES", "governs", "⚠⚠ The independently typeset source that "
     "resolves the defective chart - it states the rule as a formula AND as the same 21-band schedule."),
    ("R-AL40NR-STDDED", "AL_2025_BOOKLET_40NR", "informs", "⚠ The chart AS PRINTED, defect included. "
     "Recorded so the defect is auditable, not so it is built."),
    ("R-AL40NR-STDDED", "AL_2025_FORM_40_BOOKLET", "informs", "⚠ The RESIDENT booklet reprints the "
     "IDENTICAL defect from the same artwork - which is why the sibling forms cannot settle it."),
    ("R-AL40NR-STDDED", "AL_CODE_40_18_15", "governs", "§ 40-18-15(b) - the statutory phase-down whose "
     "$25,500 threshold was duplicated into the row-3 cell."),
    ("R-AL40NR-TAX", "AL_2025_BOOKLET_40NR", "governs", "⚠ The tax table pp.21-26, resolved positionally: "
     "Head of Family sits in the SINGLE column."),
    ("R-AL40NR-TAX", "AL_CODE_40_18_5", "governs", "The 2/4/5% rate schedule."),
    ("R-AL40NR-TAX", "AL_2026_WH_TAX_TABLES", "informs", "⚠ Confirms the bracket grouping independently - "
     "it brackets \"'0', 'S', 'H' or 'MS'\" together and \"'M'\" separately."),
    ("R-AL40NR-RETIRE", "AL_2025_BOOKLET_40NR", "governs", "⚠⚠ p.11 - the categorical rule, verbatim."),
    ("R-AL40NR-RETIRE", "AL_ADMIN_810_3_14_05", "governs", "⚠⚠ The exhaustive list of a nonresident's "
     "Alabama gross income. Pensions appear nowhere in it - hence column C is always zero."),
    ("R-AL40NR-RETIRE", "AL_ADMIN_810_3_15_21", "governs", "(2) - column B is what a RESIDENT would "
     "include, which is why the distribution belongs there."),
    ("R-AL40NR-RETIRE", "AL_2025_SCHEDULE_RS", "governs", "Part IV line 3 routes to column B; Part I "
     "exempts by plan type."),
    ("R-AL40NR-RSEXCL", "AL_2025_SCHEDULE_RS", "governs", "⚠ A2 - the ONLY source for the $6,000 figure, "
     "in either tax year."),
    ("R-AL40NR-PART2", "AL_2025_FORM_40NR", "governs", "The asymmetric summation, printed on the face."),
    ("R-AL40NR-PART2", "AL_2025_BOOKLET_40NR", "governs", "'Enter this amount on line 2, Column B only.'"),
    ("R-AL40NR-SCHEDA", "AL_2025_FORM_40NR", "governs", "Schedule A lines 21-23 and the three floors."),
    ("R-AL40NR-SCHEDA", "AL_2025_BOOKLET_40NR", "governs", "⚠ A4 - the line-21 instruction scopes the "
     "proration to lines 1 through 20, and the $100-per-event casualty floor."),
    ("R-AL40NR-SCHEDA", "AL_ADMIN_810_3_15_21", "informs", "⚠ (3)(d) agrees; (3)(e)(4)(iii)'s general "
     "list sits crosswise and is governed by the specific provision."),
    ("R-AL40NR-FITDED", "AL_2025_FORM_40NR", "governs", "⚠⚠ A1 as ruled - Part IV as printed."),
    ("R-AL40NR-FITDED", "AL_ADMIN_810_3_15_21", "informs", "⚠ (3)(e)(2)(i)'s single fraction - the "
     "competing method, recorded because it is the authority, not because it is what ships."),
    ("R-AL40NR-FITDED", "AL_2025_BOOKLET_40NR", "governs", "The worksheet, and the nonresident-alien "
     "denominator the face never mentions."),
    ("R-AL40NR-FEDLINES", "AL_40NR_IRS_2025_HANDOFF", "governs", "⚠⚠ All seven verified against the FINAL "
     "TY2025 forms - and the 1040-NR line-29 trap."),
    ("R-AL40NR-VEHICLE", "AL_2025_BOOKLET_40NR", "governs", "The worksheet, incl. the always-up rounding."),
    ("R-AL40NR-DEPEND", "AL_2025_BOOKLET_40NR", "governs", "The chart and the narrower dependent definition."),
    ("R-AL40NR-DEPEND", "AL_2026_WH_TAX_TABLES", "informs", "Independently confirms 1,000 / 500 / 300."),
]

F_LINES: list[dict] = [
    {"line_number": "AL40NR-9B", "description": "L9 col. B Adjusted total income - all sources",
     "line_type": "subtotal", "source_rules": ["R-AL40NR-PART2"], "sort_order": 1},
    {"line_number": "AL40NR-9C", "description": "L9 col. C Adjusted total income - Alabama",
     "line_type": "subtotal", "source_rules": ["R-AL40NR-PART2"], "sort_order": 2},
    {"line_number": "AL40NR-10", "description": "L10 Alabama percentage - ⚠ three branches, struck on line 9",
     "line_type": "calculated", "source_rules": ["R-AL40NR-L10"], "sort_order": 3},
    {"line_number": "AL40NR-12B", "description": "L12 col. B Adjusted Gross Income - ⚠ the chart key",
     "line_type": "subtotal", "source_rules": ["R-AL40NR-PRORATE"], "sort_order": 4},
    {"line_number": "AL40NR-12C", "description": "L12 col. C Adjusted Gross Income - Alabama",
     "line_type": "subtotal", "source_rules": ["R-AL40NR-PRORATE"], "sort_order": 5},
    {"line_number": "AL40NR-13", "description": "L13 Itemized (13a) or Standard (13b) deduction, prorated",
     "line_type": "calculated", "source_rules": ["R-AL40NR-STDDED", "R-AL40NR-SCHEDA"], "sort_order": 6},
    {"line_number": "AL40NR-14", "description": "L14 Federal income tax deduction (Part IV line 7)",
     "line_type": "calculated", "source_rules": ["R-AL40NR-FITDED"], "sort_order": 7},
    {"line_number": "AL40NR-15", "description": "L15 Personal exemption x L10",
     "line_type": "calculated", "source_rules": ["R-AL40NR-PRORATE"], "sort_order": 8},
    {"line_number": "AL40NR-16", "description": "L16 Dependent exemption (Part V line 4)",
     "line_type": "calculated", "source_rules": ["R-AL40NR-DEPEND"], "sort_order": 9},
    {"line_number": "AL40NR-17", "description": "L17 Total deductions (L13 + L14 + L15 + L16)",
     "line_type": "subtotal", "source_rules": ["R-AL40NR-PRORATE"], "sort_order": 10},
    {"line_number": "AL40NR-18", "description": "L18 Taxable income (L12 col. C - L17)",
     "line_type": "subtotal", "source_rules": ["R-AL40NR-TAX"], "sort_order": 11},
    {"line_number": "AL40NR-19", "description": "L19 Tax - ⚠ HOF is in the SINGLE column",
     "line_type": "calculated", "source_rules": ["R-AL40NR-TAX"], "sort_order": 12},
    {"line_number": "AL40NR-SCHA-30", "description": "Schedule A L30 -> page 1 line 13, box 13a",
     "line_type": "calculated", "source_rules": ["R-AL40NR-SCHEDA"], "sort_order": 13},
    {"line_number": "AL40NR-RS-P4L3", "description": "Schedule RS Part IV L3 -> page 2 Part I L3 COLUMN B",
     "line_type": "calculated", "source_rules": ["R-AL40NR-RETIRE", "R-AL40NR-RSEXCL"], "sort_order": 14},
]

F_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_AL40NR_RETIREMENT_NOT_IN_COLB", "severity": "error",
     "title": "⚠⚠ Retirement excluded as 'out of state' - Alabama does not use that test",
     "condition": "retirement_distributions != 0 and retirement_exempt_by_plan_type != True and "
                  "retirement_in_column_b == 0",
     "message": "A retirement distribution has been excluded from column B. ⚠⚠ ALABAMA HAS NO SOURCING "
                "TEST FOR RETIREMENT INCOME. Column C is always zero for pensions and annuities - Ala. "
                "Admin. Code r. 810-3-14-.05 enumerates a nonresident's Alabama gross income exhaustively "
                "and pensions appear nowhere in it. But the booklet requires the distribution in COLUMN B "
                "anyway if it 'would be taxable to a resident of Alabama', precisely so it enlarges the "
                "line-10 denominator. ⚠ Schedule RS Part I exempts by PLAN TYPE, not location: Alabama "
                "Teachers'/Employees'/Judicial Retirement, US Civil Service, Social Security, Railroad "
                "Retirement, Military Retirement, TVA, US Foreign Service, US Government Retirement, and "
                "defined BENEFIT plans under IRC § 414(j). An IRA or 401(k) is defined CONTRIBUTION and is "
                "NOT on that list. ⚠⚠ Leaving it out raises the Alabama percentage, inflates EVERY prorated "
                "deduction, and UNDERSTATES the tax - and the return foots either way, so nothing on its "
                "face will show you.",
     "notes": "⚠⚠ The single most consequential diagnostic on this form. A real filed return was found "
              "with exactly this defect, exempting three distributions with reason 'OS'."},
    {"diagnostic_id": "D_AL40NR_RETIREMENT_PLAN_TYPE", "severity": "warning",
     "title": "⚠ Confirm the PLAN TYPE before exempting a distribution",
     "condition": "retirement_exempt_by_plan_type == True",
     "message": "This distribution is being treated as exempt from Alabama income. Confirm it is exempt by "
                "PLAN TYPE, not by where it was paid from. The exempt list is closed: Alabama "
                "Teachers'/Employees'/Judicial Retirement · United States Civil Service Retirement · "
                "Social Security systems · Railroad Retirement (1935 and 1937 Acts) · Military Retirement "
                "Pay · TVA Pension · U.S. Foreign Service Retirement and Disability Fund Annuities · U.S. "
                "Government Retirement Fund Benefits · any DEFINED BENEFIT plan under IRC § 414(j). "
                "⚠ § 414(j) is defined BENEFIT - an IRA, 401(k) or other defined-CONTRIBUTION plan does not "
                "qualify however it is labelled on the 1099-R.",
     "notes": "The exempt list looks like it might include ordinary retirement accounts. It does not."},
    {"diagnostic_id": "D_AL40NR_LINE10_LOSS", "severity": "warning",
     "title": "Alabama income is a loss - line 10 is floored at 0%",
     "condition": "line9_col_c < 0",
     "message": "Column C on line 9 is negative, so line 10 is entered as 0% per the booklet: 'If the "
                "amount in Column C is a loss (less than 0) enter 0% on line 10.' ⚠ This rule has ONE "
                "authority - the form face carries only 'not over 100%' and the regulation states just the "
                "bare division. It is encoded because the alternative is a negative percentage flowing "
                "into the personal exemption, the dependent exemption, the federal-tax deduction and the "
                "standard or itemized deduction. ⚠ A loss on line 12 column C may also be an Alabama NOL - "
                "check the amended box and attach Form NOL-85 and/or NOL-85A.",
     "notes": "⚠ Campaign D-32 A3 - encoded with its single authority recorded."},
    {"diagnostic_id": "D_AL40NR_MFS_FIT_DIVERGENCE", "severity": "warning",
     "title": "⚠ Separate on Alabama, joint on federal - the form and the regulation differ here",
     "condition": "mfs_on_alabama_joint_on_federal == True and abs(taxpayer_federal_agi - line9_col_b) > 0",
     "message": "This return is separate on Alabama and joint on federal, and the taxpayer's federal AGI "
                "differs from their Alabama all-source adjusted total income. Delvio computes Part IV as "
                "PRINTED (line 5 × line 6). ⚠ Ala. Admin. Code r. 810-3-15-.21(3)(e)(2)(i) prescribes a "
                "different method - one fraction, the taxpayer's Alabama adjusted total income ÷ (spouse's "
                "federal AGI + taxpayer's all-source adjusted total income) - and states the Alabama "
                "percentage 'is not used'. The two are identical when federal AGI equals Alabama all-source "
                "income and diverge as they differ, IN BOTH DIRECTIONS. Ken ruled the form governs "
                "(campaign D-32 A1) because Part IV's lines are printed and must foot. Review the "
                "difference before filing.",
     "notes": "⚠⚠ A1 - the 'diagnose' half of 'build the form, diagnose the divergence'."},
    {"diagnostic_id": "D_AL40NR_NRA_DENOMINATOR", "severity": "error",
     "title": "⚠ Nonresident alien - the federal-tax deduction uses a DIFFERENT denominator",
     "condition": "is_nonresident_alien == True",
     "message": "The 'NRA' box is checked at filing status 3. Booklet, verbatim: 'If you are a nonresident "
                "alien with income earned in Alabama, the deduction for Federal Income Tax should be "
                "computed by applying the ratio of Alabama source income to total income received from "
                "sources WITHIN THE UNITED STATES. In other words, in the case of a nonresident alien, "
                "total income from all sources does not include foreign source income that is not required "
                "to be reported for Federal Income Tax purposes.' ⚠ NOTHING ON THE FORM FACE SAYS THE RATIO "
                "CHANGES - the face carries only the NRA checkbox. Compute the federal-tax deduction "
                "outside Delvio for this return and enter it directly at line 14.",
     "notes": "An instruction-only rule with a checkbox on the face and no computation behind it."},
    {"diagnostic_id": "D_AL40NR_STD_DEDUCTION_CHART_DEFECT", "severity": "info",
     "title": "⚠ The DOR's published standard-deduction chart is defective in the MFJ column",
     "condition": "itemize != True and filing_status == 'mfj' and 25500 <= L12_col_B <= 26999",
     "message": "Alabama's printed chart gives the third married-filing-jointly band as '$25,500 – "
                "$26,999', which overlaps the two bands above it and runs backwards - so an all-source AGI "
                "in this range appears to match two bands at once and returns either $8,500 or $8,150. "
                "⚠ Form 40, Form 40A and Form 40NR for BOTH TY2024 and TY2025 reprint the identical defect "
                "from one shared piece of artwork, so the sibling booklets cannot settle it. Delvio uses "
                "$26,500 as the band's lower bound, resolved against the Department's WITHHOLDING TAX "
                "TABLES booklet - independently typeset - which states the rule both as a formula ('$8,500 "
                "less $175 for each $500 increment or part thereof of GI above $25,999') and as the same "
                "21-band schedule reading '$26,500 – $26,999'. The printed $25,500 duplicates the statutory "
                "phase-down threshold at Ala. Code § 40-18-15(b) into that cell.",
     "notes": "⚠⚠ U9. Recorded on the return so the preparer can see WHY Delvio's figure may differ from a "
              "hand lookup off the printed chart."},
    {"diagnostic_id": "D_AL40NR_HOF_TAX_COLUMN", "severity": "info",
     "title": "Head of Family uses the SINGLE tax column, not the married one",
     "condition": "filing_status == 'hof'",
     "message": "Head of Family takes the $3,000 personal exemption (like married filing jointly) and its "
                "own standard-deduction table - but the tax comes from the SINGLE column of Alabama's tax "
                "table, which heads 'Single ✱ Married filing separately ✱ Head of family'. ⚠ Three "
                "different groupings of the same four filing statuses appear on one return. Confirmed "
                "independently in the Department's withholding formula, which brackets '0', 'S', 'H' and "
                "'MS' together and 'M' separately.",
     "notes": "The natural wrong assumption is that the $3,000 exemption implies the married brackets."},
    {"diagnostic_id": "D_AL40NR_SCHEDA_TWO_COLUMNS", "severity": "info",
     "title": "⚠ Schedule A's three floors read TWO different columns",
     "condition": "itemize == True",
     "message": "On Schedule A the medical floor reads 'Form 40NR, line 12, col. B' (all sources) at 4%, "
                "while the casualty floor (10%) and the job-expense floor (2%) both read 'Form 40NR, line "
                "12, column C' (Alabama). ⚠ Encoding all three against one AGI is a silent error - the "
                "return still foots. ⚠ Note also that the itemized proration happens ON this schedule at "
                "lines 21–23, not at page-1 line 13, and that lines 24c (Alabama casualty) and 29 (Alabama "
                "job expenses) enter UNPRORATED because they are already Alabama-only.",
     "notes": "⚠ A4 - the line-21 instruction scopes proration to lines 1 through 20."},
    {"diagnostic_id": "D_AL40NR_CASUALTY_PER_EVENT", "severity": "warning",
     "title": "⚠ The $100-per-event casualty floor is instruction-only",
     "condition": "casualty_loss != 0",
     "message": "Alabama allows a nonbusiness casualty or theft loss only to the extent that 'the amount of "
                "EACH separate casualty or theft loss is more than $100, AND the total amount of ALL "
                "Alabama losses during the year is more than 10% of your adjusted gross income on Form "
                "40NR, page 1, line 12, column C.' ⚠ The $100-per-event floor appears in the instructions "
                "only - it is NOT on the form face, which shows just the 10% computation at line 24b. "
                "⚠ Only losses on property located in Alabama at the time of loss qualify, and the loss "
                "may be claimed only in the year it occurred or the theft was discovered.",
     "notes": "A per-event floor is easy to miss when the form face shows only the aggregate one."},
    {"diagnostic_id": "D_AL40NR_PART2_COLC_OMITS_L2", "severity": "info",
     "title": "Part II column C omits line 2 by design",
     "condition": "early_withdrawal_penalty != 0",
     "message": "The penalty on early withdrawal of savings is entered in COLUMN B ONLY. The face states "
                "the asymmetry directly: 'Add lines 1 through 7, Column B, and lines 1, 3 through 7, Column "
                "C', and the booklet confirms it. ⚠ Do not mirror the entry into column C - it would raise "
                "the Alabama percentage and inflate every prorated deduction. ⚠ Note separately that "
                "penalties on early withdrawal from RETIREMENT plans are not deductible at all.",
     "notes": "The asymmetry is printed and deliberate."},
    {"diagnostic_id": "D_AL40NR_FEDERAL_1040NR_LINES", "severity": "warning",
     "title": "⚠⚠ Form 1040-NR numbers its credit lines differently",
     "condition": "federal_return_type == '1040-NR'",
     "message": "The federal return is a Form 1040-NR. ⚠⚠ Alabama's Federal Income Tax Deduction Worksheet "
                "cites line 27a for the Earned Income Credit and line 29 for the American Opportunity "
                "Credit ON FORM 1040 AND 1040-SR ONLY - and that omission is precision, not oversight. On "
                "the 2025 Form 1040-NR there is NO line 27a at all, and LINE 29 IS 'Credit for amount paid "
                "with Form 1040-C'. Pulling line 29 from a 1040-NR into the American Opportunity Credit "
                "slot subtracts a payment that is not a refundable credit and UNDERSTATES the federal tax "
                "deduction base. Lines 22, 28 and 30 and Schedule 3 Part II line 13a are the same on both "
                "returns.",
     "notes": "⚠⚠ Found by U5's re-verification against the FINAL TY2025 IRS forms."},
    {"diagnostic_id": "D_AL40NR_STD_DED_PRORATED", "severity": "info",
     "title": "The standard deduction is prorated - and the form face never says so",
     "condition": "itemize != True",
     "message": "Alabama's standard deduction is looked up on ALL-SOURCES AGI (line 12, column B) and then "
                "PRORATED by the Alabama percentage on line 10. ⚠ The form face says only to enter the "
                "chart amount - the proration appears solely in the booklet ('The Standard Deduction must "
                "be prorated by the percentage on page 1, line 10') and in Ala. Admin. Code "
                "r. 810-3-15-.21(3)(e)(3). Two different figures doing two different jobs: worldwide income "
                "sizes the deduction, Alabama's share shrinks it.",
     "notes": "One of the five prorated figures, and the only one with no trace on the form face."},
    {"diagnostic_id": "D_AL40NR_DEPENDENT_NARROWER", "severity": "warning",
     "title": "⚠ Alabama's dependent definition is narrower than federal",
     "condition": "dependents != 0",
     "message": "An Alabama dependent must have received OVER 50% of their support from the taxpayer AND be "
                "related in an enumerated way. ⚠ 'You cannot claim a foster child, friend, cousin, "
                "yourself, or your spouse as a dependent under Alabama law' - a foster child IS a federal "
                "dependent and is NOT an Alabama one, so the federal count cannot simply be carried over. "
                "⚠ If married filing separately, 'you must consider only the amounts you separately "
                "furnished out of your income.' ⚠ The exemption amount itself is keyed to ALL-SOURCES AGI "
                "(line 12 column B) and is then prorated by line 10.",
     "notes": "Carrying the federal dependent count over is the natural error."},
    {"diagnostic_id": "D_AL40NR_VEHICLE_LOAN_ROUNDING", "severity": "info",
     "title": "The vehicle-loan phase-out rounds UP, and measures worldwide AGI",
     "condition": "vehicle_loan_interest != 0",
     "message": "New for TY2025. The deduction is capped at $10,000 and phased out above $100,000 of "
                "adjusted gross income ($200,000 if married filing jointly) — ⚠ measured on line 12 COLUMN "
                "B, worldwide, even though only Alabama income is taxed. ⚠ The worksheet divides the excess "
                "by $1,000 and instructs: 'If the resulting number isn't a whole number, INCREASE THE "
                "RESULT TO THE NEXT HIGHER WHOLE NUMBER (for example, increase 1.5 to 2, and increase 0.05 "
                "to 1)', then multiplies by $200. So being $1 over a threshold costs a full $200.",
     "notes": "New for TY2025 - absent from the entire TY2024 booklet."},
    {"diagnostic_id": "D_AL40NR_ATTACH_FEDERAL_RETURN", "severity": "error",
     "title": "A complete federal return must be attached to claim the line-14 deduction",
     "condition": "L14 != 0 and federal_return_attached != True",
     "message": "Face banner, verbatim: 'You Must Attach a Complete copy of Federal Return, if claiming a "
                "deduction on line 14.' The federal income tax deduction is usually the largest single "
                "deduction on an Alabama nonresident return, so an unattached federal return risks the "
                "Department disallowing it outright.",
     "notes": "Printed on the face as a banner, not buried in the instructions."},
]

F_SCENARIOS: list[dict] = [
    # ── The tax function, pinned against THREE independently known figures ──
    {"scenario_name": "AL40NR-A0 — ⚠ the tax table's FLOOR: $0-49 prints ZERO, not one", "scenario_type": "edge", "sort_order": 0,
     "inputs": {"L18": 25, "filing_status": "single"},
     "expected_outputs": {"L19": 0},
     "notes": "⚠⚠ THE BOUNDARY THE OLD SPEC GOT WRONG. Alabama's table is NOT uniformly $100-banded: below $100 it carries two $50-wide rows, printing 0 for [0,50) and 1 for [50,100). The superseded uniform-$100 model put taxable income 25 in the [0,100) band, took midpoint 50, computed 50 x 2% = 1.00 and returned 1 - a dollar of tax Alabama does not charge. ⚠ The $50-99 range agreed BY LUCK (both give 1), so only $0-49 was ever wrong, and no fixture touched it. ⭐ Established by harvesting all 1,006 printed rows: half-up holds for 1,910 of 1,914 exact-half cases and these two floor rows are the only exceptions, in both columns. ⭐ THE GENERAL LESSON: the interior of a table gets tested and its BOUNDARIES do not - the floor, the ceiling, every row-width change and every handoff to a worksheet each need their own fixture. Same class as the SC tax-table band error and the Form 40 $100,000 handoff gap."},
    {"scenario_name": "AL40NR-A - the tax table reproduces its own printed figures",
     "scenario_type": "normal", "sort_order": 1,
     "inputs": {"taxable_income": 23050, "band": "23,000-23,100"},
     "expected_outputs": {"single_mfs_hof": 1113, "mfj": 1073},
     "notes": "The printed table shows 1,113 and 1,073 for the 23,000-23,100 band. The table computes at "
              "the BAND MIDPOINT (23,050), which is why exact-income arithmetic does not reproduce it: "
              "single = 2%x500 + 4%x2,500 + 5%x20,050 = 1,112.50 -> 1,113."},
    {"scenario_name": "AL40NR-B - ⚠ Head of Family takes the SINGLE column, not the married one",
     "scenario_type": "edge", "sort_order": 2,
     "inputs": {"taxable_income": 23050},
     "expected_outputs": {"hof": 1113, "single": 1113, "mfj": 1073},
     "notes": "⚠ HOF equals SINGLE and differs from MFJ by 40 on this fixture. HOF takes the MFJ-sized "
              "$3,000 personal exemption and its own standard-deduction table, so the natural assumption "
              "is that it takes the married brackets too. It does not."},
    {"scenario_name": "AL40NR-C - over $100,000 uses the published worksheet constants",
     "scenario_type": "edge", "sort_order": 3,
     "inputs": {"taxable_income": 150000},
     "expected_outputs": {"single_mfs_hof": 7458.0, "mfj": 7418.0},
     "notes": "(150,000 - 100,000) x .05 = 2,500, plus the published constants 4,958.00 / 4,918.00. "
              "⚠ Both constants sit ~$2 below an exact bracket computation because they carry the table's "
              "own mid-band convention - use them AS PUBLISHED, never a derived formula."},

    # ── U9, the defective chart ──
    {"scenario_name": "AL40NR-D - ⚠⚠ U9: the printed chart is ambiguous, the encoded one is not",
     "scenario_type": "edge", "sort_order": 4,
     "inputs": {"filing_status": "mfj", "L12_col_B": 25700},
     "expected_outputs": {"standard_deduction": 8500.0},
     "notes": "⚠⚠ An AGI of 25,700 falls in MFJ band 1 ($0-$25,999 -> $8,500). Under the chart AS PRINTED "
              "it ALSO falls in the defective band 3 ($25,500-$26,999 -> $8,150) - two answers for one "
              "ordinary figure. Encoding $26,500 as band 3's lower bound removes the overlap; the harness "
              "proves the encoded bands are contiguous and non-overlapping across all four statuses, and "
              "that the corrected reading is the one making the MFJ ladder step uniformly by $175."},

    # ── The line-10 branches ──
    {"scenario_name": "AL40NR-E - ⚠ A3: an Alabama loss floors line 10 at 0%",
     "scenario_type": "edge", "sort_order": 5,
     "inputs": {"line9_col_c": -8000, "line9_col_b": 60000},
     "expected_outputs": {"L10": 0.0, "L10_without_the_floor": -0.1333},
     "notes": "⚠ Without the booklet's floor the percentage is NEGATIVE, and it then multiplies the "
              "personal exemption, the dependent exemption, the federal-tax deduction and the standard or "
              "itemized deduction - turning four deductions into additions. The harness proves the "
              "unfloored value is negative rather than merely asserting the floor exists."},
    {"scenario_name": "AL40NR-F - line 10 caps at 100% when Alabama exceeds all-sources",
     "scenario_type": "edge", "sort_order": 6,
     "inputs": {"line9_col_c": 70000, "line9_col_b": 60000},
     "expected_outputs": {"L10": 1.0},
     "notes": "Face: 'not over 100%'. Booklet: 'If the amount in Column C is larger than the amount in "
              "Column B, you should enter 100%.' Both sources agree here - unlike the loss case."},

    # ── The real filed return, in BOTH positions ──
    {"scenario_name": "AL40NR-G - a real filed return, reconstructed and footing to the filed tax",
     "scenario_type": "normal", "sort_order": 7,
     "inputs": {"filing_status": "mfj", "wages_all_sources": 14380, "wages_alabama": 14380,
                "other_income_all_sources": 32131, "other_income_alabama": 9576,
                "adjustments_part2": 6818, "schedule_a_prorated_subtotal": 21559,
                "fed_tax_1040_l22": 3894, "niit_8960_l17": 0, "federal_refundable_credits": 0,
                "dependents": 0, "itemize": True},
     "expected_outputs": {"AL40NR-9B": 39693, "AL40NR-9C": 17138, "AL40NR-10": 0.4318,
                          "AL40NR-SCHA-30": 9309, "AL40NR-14": 1681, "AL40NR-15": 1295,
                          "AL40NR-17": 12285, "AL40NR-18": 4853, "AL40NR-19": 174},
     "notes": "A production return, de-identified (figures only). Every line reconciles: 17,138/39,693 = "
              "43.17638%, PRINTED as 43.18%; 21,559 x 43.18% = 9,309; 3,894 x 43.18% = 1,681; "
              "3,000 x 43.18% = 1,295; total deductions 12,285; 17,138 - 12,285 = 4,853; and the tax "
              "table returns 174 at the 4,800-4,900 band midpoint. ⚠⚠ THIS FIXTURE ESTABLISHED THE "
              "ROUNDING RULE: at FULL precision Schedule A gives 9,308, not the filed 9,309 - so Alabama "
              "multiplies by the PRINTED two-decimal percentage. Stated nowhere; recovered by "
              "reconstruction, and pinned here so it cannot be lost."},
    {"scenario_name": "AL40NR-H - ⚠⚠ the SAME return, retirement in column B PER THE EXEMPT LIST",
     "scenario_type": "edge", "sort_order": 8,
     "inputs": {"same_as": "AL40NR-G",
                "primary_age": 82, "spouse_age": 78,
                "primary_retirement_distributions": 3181,
                "primary_retirement_exempt_by_plan_type": False,
                "spouse_retirement_distributions": 13033,
                "spouse_retirement_exempt_by_plan_type": True},
     "expected_outputs": {"AL40NR-9B": 39693, "AL40NR-10": 0.4318, "AL40NR-SCHA-30": 9309,
                          "AL40NR-14": 1681, "AL40NR-15": 1295, "AL40NR-17": 12285,
                          "AL40NR-18": 4853, "AL40NR-19": 174,
                          "RS_P2L10": 3181, "RS_P3L10": 0},
     "notes": "⚠⚠ RE-BASED 2026-08-25 on Ken's direct word (\"wire the exclusion in properly\"). Column B 42,874 -> 39,693, the PRINTED percentage 39.97% -> 43.18%, tax 210 -> 174 - which is AL40NR-G, the return AS FILED. THE FILED RETURN WAS CORRECT AND THE EXPOSURE IS ZERO. ⭐⭐ TWO INDEPENDENT MECHANISMS, ONE FOR EACH SPOUSE, AND THAT IS THE WHOLE POINT: the primary's 3,181 is two ordinary IRAs - defined CONTRIBUTION, so NOT on Part I's exempt list - and is zeroed by his own Part II line-10 age-65 exclusion (min(6,000, 3,181) = 3,181). The spouse's 13,033 is a Retirement Systems of Alabama pension - named on the exempt list AND a 414(j) defined-benefit plan - so it never enters either column at all. Her own exclusion would have covered only 6,000 of it, so PLAN TYPE is doing that work, not age. ⚠⚠ WHY THIS FIXTURE WAS UNABLE TO FIRE THE RULE IT IS ABOUT: it previously supplied NO AGE and a single return-level retirement_exempt_by_plan_type=True, and R-AL40NR-RSEXCL's outputs fed nothing - so the exclusion could not move column B however the scenario was written. A missing input, an unreachable branch and a rule whose output nothing consumed are ONE defect seen three ways. ⭐ THE D-36 SECOND SHAPE: the fixture sweep asks whether a value discriminates; it cannot see an input REQUIRED TO REACH the rule that is absent entirely. ⚠ Superseded readings, kept so nobody re-derives them: 30.65%/tax 343 (added all three distributions) and 39.97%/tax 210 (correct on plan type, blind to age). Paired with AL40NR-H2, which is this same return at age 64 and DOES come out at 39.97%/210 - so the two now discriminate."},

    {"scenario_name": "AL40NR-H2 - ⭐ the SAME return at 64: the age exclusion is what moves it",
     "scenario_type": "edge", "sort_order": 8.5,
     "inputs": {"same_as": "AL40NR-G",
                "primary_age": 64, "spouse_age": 78,
                "primary_retirement_distributions": 3181,
                "primary_retirement_exempt_by_plan_type": False,
                "spouse_retirement_distributions": 13033,
                "spouse_retirement_exempt_by_plan_type": True},
     "expected_outputs": {"AL40NR-9B": 42874, "AL40NR-10": 0.3997, "AL40NR-SCHA-30": 8617,
                          "AL40NR-14": 1556, "AL40NR-15": 1199, "AL40NR-17": 11372,
                          "AL40NR-18": 5766, "AL40NR-19": 210,
                          "RS_P2L10": 0, "RS_P3L10": 0},
     "notes": "⭐⭐ THE DISCRIMINATING HALF. Identical to AL40NR-H in every input but ONE - the "
              "primary is 64, not 82 - and the answer moves by 3,181 of column B, 3.21 percentage points, "
              "and $36 of tax. ⚠ A fixture that cannot fail is not a test (campaign D-36): AL40NR-H "
              "asserted 39.97% for two days while carrying no age at all, so nothing about it could have "
              "detected that the age-65 exclusion was never reaching column B. This pair can. ⚠ Note "
              "the spouse leg is IDENTICAL in both and contributes zero either way - plan-type exemption "
              "is age-blind, which is exactly why one mechanism cannot stand in for the other."},

    {"scenario_name": "AL40NR-I - ⚠ A1: form and regulation AGREE when federal AGI = Alabama all-source",
     "scenario_type": "edge", "sort_order": 9,
     "inputs": {"fit_liability": 30000, "taxpayer_federal_agi": 100000, "spouse_federal_agi": 100000,
                "taxpayer_all_source_line9": 100000, "taxpayer_alabama_line9": 40000},
     "expected_outputs": {"form_method": 6000.0, "regulation_method": 6000.0},
     "notes": "⚠ The two methods are ALGEBRAICALLY IDENTICAL here. form = FIT x (T_fed/(T_fed+S_fed)) x "
              "(T_AL/T_all); reg = FIT x T_AL/(S_fed+T_all). Substituting T_fed = T_all cancels T_all. "
              "This is why the divergence had to be quantified before the walk could be put properly."},
    {"scenario_name": "AL40NR-J - ⚠ A1: they diverge exactly as column B departs from federal AGI",
     "scenario_type": "edge", "sort_order": 10,
     "inputs": {"fit_liability": 30000, "taxpayer_federal_agi": 100000, "spouse_federal_agi": 100000,
                "taxpayer_all_source_line9": 80000, "taxpayer_alabama_line9": 40000},
     "expected_outputs": {"form_method": 7500.0, "regulation_method": 6666.67},
     "notes": "⚠ 20,000 of US Treasury interest sits in federal AGI but NOT in Alabama's column B "
              "(r. 810-3-15-.21(2): column B is what a RESIDENT would include). The form gives 833 MORE "
              "deduction - less Alabama tax. Reverse the gap (an Alabama Retirement System employee, whose "
              "column B EXCEEDS federal AGI) and the form gives LESS deduction. Ken ruled the form governs "
              "because Part IV's lines are printed and must foot."},

    # ── Schedule A's two columns ──
    {"scenario_name": "AL40NR-K - ⚠⚠ Schedule A's three floors read TWO different columns",
     "scenario_type": "edge", "sort_order": 11,
     "inputs": {"medical_expenses": 12751, "L12_col_B": 39693, "casualty_loss": 5000,
                "job_related_expenses": 3000, "L12_col_C": 17138},
     "expected_outputs": {"medical_after_floor": 11163, "casualty_floor": 1714,
                          "job_floor": 343},
     "notes": "⚠⚠ Medical floors at 4% of COLUMN B (39,693 -> 1,588); casualty at 10% of COLUMN C "
              "(17,138 -> 1,714); job expenses at 2% of COLUMN C (17,138 -> 343). ⚠ The floors are ROUNDED to "
              "whole dollars before subtraction - the filed return proves it. Using column C for the "
              "medical floor would give a floor of 686 instead of 1,588 and overstate the deduction by "
              "902 - and the return would still foot."},

    # ── The vehicle loan worksheet ──
    {"scenario_name": "AL40NR-L - the vehicle-loan phase-out rounds UP, always",
     "scenario_type": "edge", "sort_order": 12,
     "inputs": {"vehicle_loan_interest": 4000, "L12_col_B": 200050, "filing_status": "mfj"},
     "expected_outputs": {"deduction": 3800.0},
     "notes": "⚠ Excess = 50, which is 0.05 of a $1,000 step - and the worksheet says 'increase 0.05 to 1'. "
              "So $50 over the threshold costs a full $200. Truncating instead would cost nothing and "
              "overstate the deduction."},

    # ── A2 ──
    {"scenario_name": "AL40NR-M - ⚠ A2: the $6,000 exclusion is PER TAXPAYER",
     "scenario_type": "edge", "sort_order": 13,
     "inputs": {"primary_age": 67, "spouse_age": 66, "primary_taxable_retirement": 9000,
                "spouse_taxable_retirement": 4000},
     "expected_outputs": {"primary_exclusion": 6000.0, "spouse_exclusion": 4000.0,
                          "total": 10000.0, "if_read_per_return": 6000.0},
     "notes": "⚠ Each taxpayer is capped separately at $6,000 AND at their own Alabama-taxable retirement - "
              "so the spouse's exclusion is limited to 4,000 by their own income, not by the $6,000 cap. "
              "A per-RETURN reading would allow only 6,000 total and overstate the tax. The figure appears "
              "nowhere in the booklet, either tax year; the Schedule RS face is the only source."},

    # ── Part II asymmetry ──
    {"scenario_name": "AL40NR-N - ⚠ Part II column C omits line 2",
     "scenario_type": "edge", "sort_order": 14,
     "inputs": {"part2_line1": 5000, "part2_line2": 900, "part2_line4": 1200},
     "expected_outputs": {"col_B_total": 7100.0, "col_C_total": 6200.0},
     "notes": "⚠ The early-withdrawal penalty (line 2) is column B only. Mirroring it into column C would "
              "raise line 10 and inflate every prorated deduction. The face states the asymmetry and the "
              "booklet confirms it - it is deliberate, not a typo."},

    # ── The FIT worksheet floor ──
    {"scenario_name": "AL40NR-O - the federal-tax worksheet floors at zero",
     "scenario_type": "edge", "sort_order": 15,
     "inputs": {"fed_tax_1040_l22": 2000, "niit_8960_l17": 0, "eic": 3500, "actc": 1000,
                "aoc": 0, "adoption": 0, "form_2439": 0},
     "expected_outputs": {"worksheet_L6": 0.0},
     "notes": "L6: 'Subtract line 5 from line 3. If amount is negative enter zero.' Refundable credits of "
              "4,500 against 2,000 of tax give -2,500, floored to zero - never a negative deduction."},
]

FORMS: list[dict] = [
    {
        "identity": {
            "form_number": "AL_FORM_40NR",
            "form_title": "Alabama Form 40NR - Individual Income Tax Return, Nonresidents Only (TY2025)",
            "notes": (
                "Campaign `delvio-states`; Gate-1 walk closed at campaign D-32 (four source conflicts "
                "ruled). Alabama's nonresident individual return: three columns (A withheld / B all "
                "sources / C Alabama), an allocation percentage at line 10 that prorates FIVE figures, and "
                "a tax table with only TWO columns. ⚠⚠ THE BIG ONE: retirement income is CATEGORICAL, not "
                "sourced - column C is always zero for pensions, but column B carries any distribution a "
                "RESIDENT would be taxed on, so untaxed retirement income still shrinks every prorated "
                "deduction. Schedule RS Part I exempts by PLAN TYPE (§ 414(j) is defined BENEFIT), never "
                "by location. ⚠⚠ The DOR's published standard-deduction chart is DEFECTIVE in the MFJ "
                "column and the sibling booklets reprint the same defect; it is resolved against the "
                "Department's independently typeset withholding booklet. ⚠ HEAD OF FAMILY sits in the "
                "SINGLE tax column despite taking the MFJ-sized exemption. ⚠ Schedule A prorates ITSELF at "
                "lines 21-23 and carries THREE floors reading TWO different columns. ⚠ On Form 1040-NR "
                "line 29 is not the American Opportunity Credit and there is no EIC line at all."
            ),
        },
        "facts": F_FACTS, "rules": F_RULES, "rule_links": F_RULE_LINKS,
        "lines": F_LINES, "diagnostics": F_DIAGNOSTICS, "scenarios": F_SCENARIOS,
    },
]

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-AL40NR-RETIRE", "title": "⚠⚠ Retirement: column B carries it, column C never does",
     "assertion_type": "reconciliation", "entity_types": ["1040"], "status": "draft", "sort_order": 1,
     "description": "⚠⚠ Alabama has NO sourcing test for retirement income. r. 810-3-14-.05 enumerates a "
                    "nonresident's Alabama gross income exhaustively and pensions appear nowhere in it, so "
                    "column C is always zero; r. 810-3-15-.21(2) defines column B as what a RESIDENT would "
                    "include, so the distribution belongs there. The consequence is that income Alabama "
                    "never taxes still SHRINKS every prorated deduction - and the return foots either way, "
                    "so nothing on its face reveals the error.",
     "definition": {"rule": "R-AL40NR-RETIRE",
                    "check": "col_C == 0 always; col_B == gross iff taxable to an AL resident"}},
    {"assertion_id": "FA-AL40NR-L10", "title": "⚠ Line 10 has three branches and is struck on line 9",
     "assertion_type": "flow_assertion", "entity_types": ["1040"], "status": "draft", "sort_order": 2,
     "description": "⚠ Ordinary = C ÷ B; capped at 100% (face + booklet); floored at 0% on a loss "
                    "(BOOKLET ONLY - campaign D-32 A3). ⚠⚠ Struck on LINE 9, never line 12: the regulation "
                    "states that alimony paid and adoption expenses sit in neither the numerator nor the "
                    "denominator, which is exactly why line 11 is subtracted afterwards.",
     "definition": {"rule": "R-AL40NR-L10",
                    "check": "colC<0 -> 0%; else min(100%, line9_colC/line9_colB)"}},
    {"assertion_id": "FA-AL40NR-CHART", "title": "⚠⚠ The encoded chart bands are contiguous and non-overlapping",
     "assertion_type": "reconciliation", "entity_types": ["1040"], "status": "draft", "sort_order": 3,
     "description": "⚠⚠ The DOR's published chart is DEFECTIVE: MFJ band 3 prints as $25,500-$26,999, "
                    "overlapping bands 1 and 2 and running backwards, so an ordinary AGI near $25,700 has "
                    "two answers. Form 40, 40A and 40NR across TWO tax years reprint it from one shared "
                    "piece of artwork. Resolved to $26,500 against the Department's independently typeset "
                    "withholding booklet, which states the rule as a formula AND as the same schedule.",
     "definition": {"rule": "R-AL40NR-STDDED",
                    "check": "bands contiguous, non-overlapping, exhaustive, for all four statuses"}},
    {"assertion_id": "FA-AL40NR-HOF", "title": "⚠ Head of Family: MFJ exemption, SINGLE tax column",
     "assertion_type": "flow_assertion", "entity_types": ["1040"], "status": "draft", "sort_order": 4,
     "description": "⚠ Three different groupings of the same four filing statuses on one return: HOF takes "
                    "the $3,000 personal exemption (with MFJ), its own standard-deduction table (alone), "
                    "and the single rate brackets (with Single and MFS). Confirmed independently by the "
                    "Department's withholding formula.",
     "definition": {"rule": "R-AL40NR-TAX", "check": "tax(hof) == tax(single) != tax(mfj)"}},
    {"assertion_id": "FA-AL40NR-SCHEDA", "title": "⚠⚠ Schedule A: three floors, two columns, and it prorates itself",
     "assertion_type": "reconciliation", "entity_types": ["1040"], "status": "draft", "sort_order": 5,
     "description": "⚠⚠ Medical floors on COLUMN B (4%); casualty (10%) and job expenses (2%) floor on "
                    "COLUMN C. The itemized proration happens at lines 21-23 ON the schedule, and lines "
                    "24c and 29 enter UNPRORATED because they are already Alabama-only - the booklet's "
                    "line-21 instruction scopes proration to 'lines 1 through 20' (campaign D-32 A4).",
     "definition": {"rule": "R-AL40NR-SCHEDA",
                    "check": "L30 == L21*L10 + L24c + L29; medical floor reads col B"}},
    {"assertion_id": "FA-AL40NR-FITDED", "title": "⚠ A1: the form's arithmetic ships; the regulation's is diagnosed",
     "assertion_type": "flow_assertion", "entity_types": ["1040"], "status": "draft", "sort_order": 6,
     "description": "⚠ The two methods coincide whenever the taxpayer's federal AGI equals their Alabama "
                    "all-source adjusted total income and diverge only as column B departs from federal "
                    "AGI - in BOTH directions. Part IV's lines 3/5/6/7 are PRINTED, so the regulation's "
                    "single fraction would produce a return where line 7 != line 5 x line 6. ⭐ A "
                    "regulation outranks a form on authority; it does not outrank it on what the form "
                    "must show.",
     "definition": {"rule": "R-AL40NR-FITDED",
                    "check": "form method ships; divergence raises a diagnostic"}},
    {"assertion_id": "FA-AL40NR-FEDNR", "title": "⚠⚠ The three 1040 variants are NOT interchangeable",
     "assertion_type": "flow_assertion", "entity_types": ["1040"], "status": "draft", "sort_order": 7,
     "description": "⚠⚠ On the 2025 Form 1040-NR, line 29 is 'Credit for amount paid with Form 1040-C', "
                    "not the American Opportunity Credit, and there is NO line 27a (EIC) at all. Alabama "
                    "cites 1040/1040-SR only for those two lines - the omission is precision, not "
                    "oversight, and a loader that ignores it subtracts a payment as though it were a "
                    "refundable credit.",
     "definition": {"rule": "R-AL40NR-FEDLINES",
                    "check": "EIC and AOC sourced from 1040/1040-SR only"}},
]


class Command(BaseCommand):
    help = ("Load the AL_FORM_40NR spec (Alabama Individual Nonresident Return, TY2025). "
            "Refuses to seed until Ken's Gate-1 SEED approval.")

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad AL_FORM_40NR spec (Alabama Individual Nonresident Return, TY2025)\n"))
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
                "\nREFUSING TO SEED AL_FORM_40NR: not cleared to seed.\n\n"
                "Campaign D-32 closed the Gate-1 WALK (scope). That is NOT the seed gate. Ken must\n"
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
        self.stdout.write("AL_FORM_40NR loaded (TY2025 ONLY - every figure is TY-keyed).")
        self.stdout.write(f"  AL_FORM_40NR: facts {len(F_FACTS)} / rules {len(F_RULES)} / "
                          f"lines {len(F_LINES)} / diag {len(F_DIAGNOSTICS)} / tests {len(F_SCENARIOS)}")
        self.stdout.write(f"  Flow assertions: {len(FLOW_ASSERTIONS)}")
        self.stdout.write("  !! Retirement is CATEGORICAL - column B carries it, column C never does.")
        self.stdout.write("  !! The DOR standard-deduction chart is DEFECTIVE; MFJ band 3 encodes 26,500.")
        self.stdout.write("  !! Head of Family sits in the SINGLE tax column.")
        self.stdout.write("=" * 66)
