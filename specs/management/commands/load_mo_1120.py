"""Load the Missouri Form MO-1120 spec - Corporation Income Tax Return (TY2025).

WO-W05-CCORP. Missouri's walk closed at campaign **D-24** (14 items).

═══════════════════════════════════════════════════════════════════════════
⚠⚠ THE FEDERAL INCOME TAX DEDUCTION - very few states have one. Get it right.
═══════════════════════════════════════════════════════════════════════════
§ 143.171.3 RSMo, verbatim: "a corporate taxpayer shall be allowed a deduction
for FIFTY PERCENT of its federal income tax liability under Chapter 1 of the
Internal Revenue Code for the same taxable year ... after reduction for all
credits thereon, EXCEPT the credit for payments of federal estimated tax, the
credit for the overpayment of any federal tax, and the credits allowed ... by
26 U.S.C. Section 31, 26 U.S.C. Section 27, and 26 U.S.C. Section 34."

⭐ THAT IS WHY THE FOREIGN TAX CREDIT IS ADDED BACK. IRC § 27 is the FTC.
Schedule J line 12 is already net of it, so Part 3 restores it. §§ 31 and 34
need no restoration because they sit BELOW line 12 on Schedule J (as payments
at L18/L20b) and never reduced it. **Encode the rule as "add back § 27 only",
citing § 143.171.3 - NOT as "add back Schedule J line 5a", which is the
implementation, not the rule.**

⚠⚠ THE CORPORATE DEDUCTION HAS NO PERCENTAGE TABLE AND NO DOLLAR CAP. The
$5,000 / $10,000 caps and the 35/25/15/5/0 table in § 143.171.1-.2 are
INDIVIDUAL-ONLY *and* SUNSET - § 143.171.1 opens "For all tax years beginning on
or after January 1, 1994, AND ENDING ON OR BEFORE DECEMBER 31, 2018, an
INDIVIDUAL taxpayer...". So those figures are dead for every taxpayer and every
year in scope, for TWO independent reasons. This spec encodes none of them, and
the harness FAILS if any appears.

═══════════════════════════════════════════════════════════════════════════
KEN'S RULINGS THIS SPEC IMPLEMENTS (campaign D-24)
═══════════════════════════════════════════════════════════════════════════
M2  The six alternative federal returns (1120-C, 1120-F, 1120-L, 1120-PC,
    1120-REIT, 1120-RIC) are RED-DEFERRED. Missouri publishes NO crosswalk for
    which federal line feeds MO-1120 line 1, and THE WHOLE COMPUTATION RIDES ON
    LINE 1 - a guessed starting figure is wrong all the way down.
M3  Missouri consolidated is RED-DEFERRED; the CONSOLIDATED-FEDERAL /
    SEPARATE-MISSOURI branch IS BUILT, because the form fully specifies it
    (Part 3 lines 4-6).
M4  ⚠ The credit-poisoning path reaches the corporate side. Source the corporate
    SPA from the PTE lane's DERIVED "tax actually paid" field - NEVER MO-PTE
    Part B Column 6 at face value.
M5  ⚠⚠ THE ATTACHMENT CLIFF IS A HARD BLOCK. The face states: "If information
    is not sent, the federal income tax deduction MAY BE REDUCED TO ZERO."
    That is a 100%-of-deduction cliff, not a processing nag.
M6  ⚠⚠ MO-C IS A 23-ROW EXPLICIT LOOKUP TABLE, NEVER AN OFFSET.
M7  The NOL 20-year cap is encoded NOW - dormant for TY2025, live TY2038, and
    live TODAY for long-dated pre-2018 losses.

═══════════════════════════════════════════════════════════════════════════
⚠ TWO DIFFERENT ROUNDING RULES ON ONE RETURN
═══════════════════════════════════════════════════════════════════════════
Page 1 line 9 apportionment percentage : THREE decimals ("such as 12.345 percent")
Part 3 line 6 federal-tax-deduction ratio : FOUR decimals ("such as 12.3456 percent")
A single shared rounding constant is wrong on one of them.

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
# D-24 approved the walk SCOPE (14 items). That is not the seed gate.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = False


FORM_JURISDICTION = "MO"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"
FORM_ENTITY_TYPES = ["1120"]

# § 143.071.3, verbatim: "For all tax years beginning on or after January 1,
# 2020, a tax is hereby imposed upon the Missouri taxable income of corporations
# in an amount equal to FOUR PERCENT of Missouri taxable income."
# ⚠ Instruction adds: "Income tax cannot be prorated or annualized."
MO_CORP_RATE: dict[int, str] = {2025: "0.04"}

# § 143.171.3 - FIFTY percent of federal income tax liability. No table, no cap.
MO_FED_TAX_DEDUCTION_PCT: dict[int, str] = {2025: "0.50"}

# ⚠ TWO DIFFERENT ROUNDING RULES ON ONE RETURN - see the module docstring.
MO_APPORT_DECIMALS: dict[int, int] = {2025: 3}      # page 1 line 9
MO_FED_RATIO_DECIMALS: dict[int, int] = {2025: 4}   # part 3 line 6

# M7 - encode the cap NOW. Dormant for TY2025, live TY2038, and live TODAY for
# long-dated pre-2018 losses. A dated fuse is cheaper to defuse than to discover.
MO_NOL_CARRYFORWARD_YEARS: dict[int, int] = {2025: 20}

# M2 - refused outright. No published crosswalk to MO-1120 line 1.
MO_DEFERRED_FEDERAL_RETURNS: tuple = (
    "1120-C", "1120-F", "1120-L", "1120-PC", "1120-REIT", "1120-RIC",
)

# M5 - the four items the face names. "If information is not sent, the federal
# income tax deduction may be reduced to zero."
MO_FED_DEDUCTION_ATTACHMENTS: tuple = (
    "the CONSOLIDATED Federal Form 1120",
    "Federal Form 1120 Schedule J",
    "an income statement",
    "or a summary of profit companies",
)

# ⚠⚠ DELIBERATELY ABSENT: the $5,000 / $10,000 caps and the 35/25/15/5/0 table
# from § 143.171.1-.2. They are INDIVIDUAL-ONLY and SUNSET (".. ending on or
# before December 31, 2018"). Dead for every taxpayer and every year in scope,
# for two independent reasons. The harness FAILS if any of them appears here.


def _yk(table: dict, year: int = FORM_TAX_YEAR):
    if year not in table:
        raise CommandError(f"No TY{year} value in {table!r} - re-verify before extending the year.")
    return table[year]


def _mo_federal_tax_deduction(sch_j_total_tax, sch_j_foreign_tax_credit,
                              year: int = FORM_TAX_YEAR):
    """MO-1120 Page 4, Part 3, line 3 - the base deduction.

    "Federal income tax - Add Lines 1 and 2. Multiply the total by 50%."
    Part 3 line 1 = Federal Schedule J line 12 (Total tax); line 2 = Schedule J
    line 5a (Foreign tax credit).

    ⭐ THE ADD-BACK IS NOT ARBITRARY. § 143.171.3 sets the base as federal tax
    after all credits EXCEPT §§ 31, 27 and 34. IRC § 27 IS the foreign tax
    credit, and Schedule J line 12 is already net of it - so the form restores
    it. §§ 31 and 34 need no restoration because they sit BELOW line 12 on
    Schedule J and never reduced it.

    ⚠ Encode this as "add back § 27 only". Reading it as "add back Schedule J
    line 5a" copies the implementation instead of the rule, and would silently
    break if the IRS renumbered Schedule J.
    """
    total = float(sch_j_total_tax or 0) + float(sch_j_foreign_tax_credit or 0)
    return round(total * float(_yk(MO_FED_TAX_DEDUCTION_PCT, year)), 2)


def _mo_federal_tax_deduction_consolidated(base_deduction, separate_company_fti,
                                           total_positive_separate_fti,
                                           year: int = FORM_TAX_YEAR):
    """Part 3 lines 4-6 - the consolidated-federal / separate-Missouri branch.

    "Consolidated federal and separate Missouri returns must complete Lines 4
    through 6." Line 4 numerator = separate company federal taxable income;
    line 5 denominator = "the total of all positive separate company federal
    taxable incomes. DO NOT INCLUDE COMPANIES WHICH INCURRED A LOSS." Line 6
    divides and multiplies by line 3.

    ⚠ THE DENOMINATOR EXCLUDES LOSS COMPANIES. Including them would inflate the
    denominator and understate every profitable member's share of the deduction.

    ⚠ The ratio rounds to FOUR decimals here, while the page-1 apportionment
    percentage rounds to THREE. Two rounding rules on one return.
    """
    den = float(total_positive_separate_fti or 0)
    if den == 0:
        return None
    ratio = round(float(separate_company_fti) / den, _yk(MO_FED_RATIO_DECIMALS, year))
    return round(ratio * float(base_deduction), 2)


def _mo_line13(line9, dividends_deduction, zone_modification):
    """Page 1 line 13 - Missouri taxable income.

    "Line 9 minus Lines 10 and 11. DO NOT ENTER A NEGATIVE NUMBER. If the result
    is less than zero, enter zero."
    """
    return max(0.0, float(line9) - float(dividends_deduction or 0) - float(zone_modification or 0))


def _mo_line14(line13, year: int = FORM_TAX_YEAR):
    """Page 1 line 14 - "Corporation income tax - 4% of Line 13."

    ⚠ Instruction, verbatim: "Income tax cannot be prorated or annualized." So a
    short period does NOT get a proportionate rate, and no annualisation is
    applied to a part-year return.
    """
    return round(max(0.0, float(line13)) * float(_yk(MO_CORP_RATE, year)), 2)


# ═══════════════════════════════════════════════════════════════════════════
# ⚠⚠ M6 - FORM MO-C IS A 23-ROW EXPLICIT LOOKUP TABLE, NEVER AN OFFSET
# ═══════════════════════════════════════════════════════════════════════════
# MO-C mirrors federal Schedule C but DROPS the federal "Subtotal" line (federal
# line 9). From that point on every MO-C line is ONE LOWER than its federal
# counterpart - THIRTEEN consecutive rows. An engine assuming MO-C N == federal N
# is wrong across all of them AND WRONG SILENTLY: the return still foots, the
# dividends deduction is simply wrong. The C-corp twin of the PTE K-1
# silent-failure defect.
#
# Encoded as an explicit map, not arithmetic. If a future reader is tempted to
# replace this with `federal = mo_c + (1 if mo_c >= 9 else 0)`, the harness
# proves the two disagree.
MO_C_TO_FEDERAL_SCHEDULE_C: dict[int, int] = {
    1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8,
    # federal line 9 "Subtotal. Add lines 1 through 8" HAS NO MO-C LINE
    9: 10, 10: 11, 11: 12, 12: 13, 13: 14, 14: 15,
    15: 16, 16: 17, 17: 18, 18: 19, 19: 20, 20: 21, 21: 22,
}


def _mo_c_federal_line(mo_c_line: int) -> int:
    """Map an MO-C line to its federal Schedule C counterpart.

    ⚠⚠ EXPLICIT LOOKUP, NEVER ARITHMETIC (M6). MO-C omits federal Schedule C's
    "Subtotal" line, so the correspondence breaks at line 9 and stays broken for
    thirteen rows. Any offset formula is wrong for part of the range, and wrong
    quietly - the dividends deduction lands on the wrong federal concept while
    the return continues to foot.
    """
    if mo_c_line not in MO_C_TO_FEDERAL_SCHEDULE_C:
        raise CommandError(
            f"MO-C line {mo_c_line} is not in the verified map. MO-C has 21 numbered lines "
            "mapping to federal Schedule C lines 1-8 and 10-22; federal line 9 (Subtotal) has "
            "no MO-C counterpart. Do not extrapolate."
        )
    return MO_C_TO_FEDERAL_SCHEDULE_C[mo_c_line]


AUTHORITY_TOPICS: list[tuple[str, str]] = [
    # Keep under 255 - the loader guards it, and caught this entry at 265 (D-17 class).
    ("mo_corp_tax", "Missouri Form MO-1120: the 4% rate (Sec. 143.071.3), the 50% federal income tax "
     "deduction under Sec. 143.171.3 with its Sec. 27 add-back and attachment cliff, and the MO-C "
     "map that omits federal Schedule C's subtotal line."),
]

EXISTING_SOURCES_TO_REFERENCE: list[str] = []

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "MO_2025_FORM_1120", "source_type": "state_form", "source_rank": "primary_official",
        "jurisdiction_code": "MO", "title": "2025 Missouri Form MO-1120 - Corporation Income Tax Return",
        "citation": "Form MO-1120 (2025)", "issuer": "Missouri Department of Revenue",
        "official_url": "https://dor.mo.gov/forms/", "current_status": "active",
        "is_substantive_authority": True, "trust_score": 9.5, "topics": ["mo_corp_tax"],
        "excerpts": [
            {
                "excerpt_label": "The page-1 spine, the 4% rate and the two rounding rules (verbatim)",
                "excerpt_text": (
                    "1 'Federal taxable income from Federal Form 1120, Line 30'; 6 'Balance - Line 1 plus "
                    "Line 4 minus Line 5'; 7 'Federal income tax - Current year (complete Page 4, Part 3)'; "
                    "8 'Taxable income - All sources - Line 6 minus Line 7'; 9 'Preliminary Missouri taxable "
                    "income - If all Missouri income, enter amount from Line 8. If not, complete and attach "
                    "Form MO-MS. Multiply Line 8 by the percentage' with the percentage 'rounded to THREE "
                    "digits to the right of the decimal point, such as 12.345 percent'; 13 'Missouri taxable "
                    "income - Line 9 minus Lines 10 and 11. Do not enter a negative number. If the result is "
                    "less than zero, enter zero.'; 14 'Corporation income tax - 4% of Line 13' with the "
                    "instruction 'Income tax cannot be prorated or annualized.'; 16 'Total tax - Add Lines 14 "
                    "and 15'. Part 3 line 6 ratio is 'round[ed] to FOUR digits to the right of the decimal "
                    "point, such as 12.3456 percent'."
                ),
                "summary_text": "MO-1120: federal TI -> MO modifications -> the 50% federal income tax "
                                "deduction -> apportionment (THREE decimals) -> 4%. Part 3's consolidated "
                                "ratio uses FOUR decimals - two rounding rules on one return.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "⚠⚠ M5 - the attachment cliff, and the line-21 instruction conflict",
                "excerpt_text": (
                    "Face, verbatim: 'Consolidated federal and separate Missouri return filers must attach "
                    "consolidated Federal Form 1120, Schedule J, and an income statement or summary of profit "
                    "companies. IF INFORMATION IS NOT SENT, THE FEDERAL INCOME TAX DEDUCTION MAY BE REDUCED "
                    "TO ZERO.' Regulatory basis: 12 CSR 10-2.090 and 12 CSR 10-2.165. ⚠ Separately, the "
                    "instructions carry TWO line-21 rules: p.5 says 'Enter the total of Lines 17 through 20', "
                    "agreeing with the face; p.6, orphaned above the Line 22 heading, says 'Enter the total "
                    "of Lines 18, 19, 20, and 21' - SELF-REFERENTIAL AND WRONG. Build the face. ⚠ Also: 'No "
                    "refund of less than $1.00 will be made', and refunds of $100,000 or more must be issued "
                    "electronically."
                ),
                "summary_text": "⚠ A 100%-of-deduction cliff on missing attachments, not a processing nag. "
                                "And a self-referential line-21 instruction that must be ignored in favour "
                                "of the form face.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MO_RSMO_143_171", "source_type": "state_statute", "source_rank": "primary_official",
        "jurisdiction_code": "MO", "title": "Sec. 143.171 RSMo - federal income tax deduction",
        "citation": "Sec. 143.171.3 RSMo", "issuer": "Missouri General Assembly",
        "official_url": "https://revisor.mo.gov/main/OneSection.aspx?section=143.171",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["mo_corp_tax"],
        "excerpts": [{
            "excerpt_label": "⚠ The corporate leg, and why the FTC is added back",
            "excerpt_text": (
                "Sec. 143.171.3, verbatim: 'For all tax years beginning on or after September 1, 1993, a "
                "corporate taxpayer shall be allowed a deduction for FIFTY PERCENT of its federal income tax "
                "liability under Chapter 1 of the Internal Revenue Code for the same taxable year for which "
                "the Missouri return is being filed AFTER REDUCTION FOR ALL CREDITS THEREON, EXCEPT the "
                "credit for payments of federal estimated tax, the credit for the overpayment of any federal "
                "tax, and the credits allowed by the Internal Revenue Code by 26 U.S.C. Section 31, 26 "
                "U.S.C. Section 27, and 26 U.S.C. Section 34.' ⭐ IRC Sec. 27 IS the foreign tax credit, "
                "which is why Part 3 adds it back: Schedule J line 12 is already net of it. Sec.Sec. 31 and "
                "34 sit BELOW line 12 and never reduced it. ⚠⚠ The $5,000/$10,000 caps and the 35/25/15/5/0 "
                "table in Sec. 143.171.1-.2 are INDIVIDUAL-ONLY and SUNSET - subsection .1 opens 'For all "
                "tax years beginning on or after January 1, 1994, AND ENDING ON OR BEFORE DECEMBER 31, 2018, "
                "an INDIVIDUAL taxpayer...'. Dead for every taxpayer and every year in scope."
            ),
            "summary_text": "50% of federal tax after credits except IRC 31/27/34. The corporate deduction "
                            "has NO percentage table and NO dollar cap; the individual figures are both "
                            "inapplicable AND sunset.",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "MO_RSMO_143_071", "source_type": "state_statute", "source_rank": "primary_official",
        "jurisdiction_code": "MO", "title": "Sec. 143.071 RSMo - corporate income tax rate",
        "citation": "Sec. 143.071.3 RSMo", "issuer": "Missouri General Assembly",
        "official_url": "https://revisor.mo.gov/main/OneSection.aspx?section=143.071",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["mo_corp_tax"],
        "excerpts": [{
            "excerpt_label": "The 4% rate, verbatim",
            "excerpt_text": (
                "'For all tax years beginning on or after January 1, 2020, a tax is hereby imposed upon the "
                "Missouri taxable income of corporations in an amount equal to FOUR PERCENT of Missouri "
                "taxable income.' Last amended 2018 S.B. 884. ⚠ The MO-1120 instruction adds: 'Income tax "
                "cannot be prorated or annualized.'"
            ),
            "summary_text": "Flat 4% from TY2020 on, and it is never prorated or annualised for a short "
                            "period.",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "MO_2025_FORM_MOC", "source_type": "state_form", "source_rank": "primary_official",
        "jurisdiction_code": "MO", "title": "2025 Missouri Form MO-C - Missouri Dividends Deduction Schedule",
        "citation": "Form MO-C (2025), Revised 03-2026", "issuer": "Missouri Department of Revenue",
        "official_url": "https://dor.mo.gov/forms/", "current_status": "active",
        "is_substantive_authority": True, "trust_score": 9.4, "topics": ["mo_corp_tax"],
        "excerpts": [{
            "excerpt_label": "⚠⚠ M6 - MO-C DROPS federal Schedule C's Subtotal line",
            "excerpt_text": (
                "MO-C mirrors federal Schedule C in four columns - (A) Federal Dividends, (B) Eligible "
                "Dividends Received, (C) %, (D) Eligible Deductions = (B) x (C). ⚠⚠ IT OMITS the federal "
                "'Subtotal. Add lines 1 through 8' line (federal line 9), so from that point on every MO-C "
                "line is ONE LOWER than its federal counterpart: MO-C 9 = federal 10, MO-C 10 = federal 11, "
                "and so on for THIRTEEN consecutive rows. ⚠ MO-C is 'Revised 03-2026' - NEWER than its own "
                "instructions - so where the two disagree the FACE is the later expression of the "
                "Department's position. ⚠ Branch 3's percentage source is TWO-VALUED while the face records "
                "only one: MO-C line 27 reads 'Apportionment factor from Form MO-MS, Part 1, Line 3' with no "
                "field for the 'any other apportionment method' case that routes to MO-1120 Line 9 Percent."
            ),
            "summary_text": "⚠⚠ Thirteen consecutive rows are offset by one. Encode all 21 numbered lines as "
                            "an EXPLICIT map, never an offset formula.",
            "is_key_excerpt": True,
        }],
    },
]

AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    ("MO_2025_FORM_1120", "MO_1120", "primary_form"),
    ("MO_RSMO_143_171", "MO_1120", "statute"),
    ("MO_RSMO_143_071", "MO_1120", "statute"),
    ("MO_2025_FORM_MOC", "MO_1120", "related_form"),
]


F_FACTS: list[dict] = [
    {"fact_key": "federal_taxable_income", "label": "L1 Federal taxable income (Federal Form 1120, Line 30)",
     "data_type": "decimal", "required": False, "sort_order": 1,
     "notes": "⚠ M2: if the federal return is 1120-C, 1120-F, 1120-L, 1120-PC, 1120-REIT or 1120-RIC, this "
              "spec REFUSES - Missouri publishes no crosswalk saying which federal line feeds here, and the "
              "whole computation rides on this figure."},
    {"fact_key": "federal_return_type", "label": "Which federal return was filed?",
     "data_type": "string", "required": False, "sort_order": 2,
     "notes": "1120 is supported. The six alternative federal returns are RED-deferred (M2)."},
    {"fact_key": "state_income_taxes_deducted", "label": "L2 State/local income taxes deducted federally",
     "data_type": "decimal", "required": False, "sort_order": 3,
     "notes": "§ 143.141(1)-(2); 12 CSR 10-2.160. Schedule required breaking down federal 1120 Line 17. ⚠ "
              "'Do not include St. Louis or Kansas City earnings taxes' - that rule is in the INSTRUCTIONS "
              "ONLY, not on the face."},
    {"fact_key": "mo_additions", "label": "L3 Missouri modifications - additions (Page 3, Part 1, Line 6)",
     "data_type": "decimal", "required": False, "sort_order": 4},
    {"fact_key": "mo_subtractions", "label": "L5 Missouri modifications - subtractions (Page 3, Part 2, Line 14)",
     "data_type": "decimal", "required": False, "sort_order": 5},
    {"fact_key": "sch_j_total_tax", "label": "Part 3 L1 - federal Schedule J Line 12 (Total tax)",
     "data_type": "decimal", "required": False, "sort_order": 6},
    {"fact_key": "sch_j_foreign_tax_credit", "label": "Part 3 L2 - federal Schedule J Line 5a (Foreign tax credit)",
     "data_type": "decimal", "required": False, "sort_order": 7,
     "notes": "⭐ Added back because § 143.171.3 excepts IRC § 27 - the FTC - from the credits that reduce "
              "the base. Schedule J line 12 is already net of it. Encode the rule as '§ 27', not as "
              "'Schedule J line 5a'."},
    {"fact_key": "consolidated_federal_separate_mo", "label": "Consolidated federal return, separate Missouri return?",
     "data_type": "boolean", "required": False, "sort_order": 8,
     "notes": "⚠ M3: this branch IS BUILT (Part 3 lines 4-6, fully specified on the form). A true MISSOURI "
              "consolidated return is RED-deferred."},
    {"fact_key": "separate_company_fti", "label": "Part 3 L4 - separate company federal taxable income (numerator)",
     "data_type": "decimal", "required": False, "sort_order": 9},
    {"fact_key": "total_positive_separate_fti", "label": "Part 3 L5 - TOTAL POSITIVE separate company FTI",
     "data_type": "decimal", "required": False, "sort_order": 10,
     "notes": "⚠ Verbatim: 'Do not include companies which incurred a loss.' Including loss companies "
              "inflates the denominator and understates every profitable member's share."},
    {"fact_key": "fed_deduction_attachments_sent", "label": "Were the required attachments sent with the return?",
     "data_type": "boolean", "required": False, "sort_order": 11,
     "notes": "⚠⚠ M5: 'If information is not sent, the federal income tax deduction MAY BE REDUCED TO ZERO.' "
              "A 100%-of-deduction cliff, not a processing nag."},
    {"fact_key": "is_all_missouri", "label": "All Missouri income? (L9 branch)",
     "data_type": "boolean", "required": False, "sort_order": 12},
    {"fact_key": "apportionment_method", "label": "MO-MS apportionment method (2a, 3, 4, 5, 6 or 7)",
     "data_type": "string", "required": False, "sort_order": 13,
     "notes": "⚠ W5: Methods Three to Seven are RED-deferred, BUT the routing help copy still ships - a "
              "trucking company picking 'Three - Transportation' off the label files a wrong return."},
    {"fact_key": "apportionment_percent", "label": "L9 apportionment percentage (THREE decimals)",
     "data_type": "decimal", "required": False, "sort_order": 14,
     "notes": "⚠ THREE digits right of the decimal, 'such as 12.345 percent'. The Part 3 ratio uses FOUR - "
              "two different rounding rules on one return."},
    {"fact_key": "mo_dividends_deduction", "label": "L10 Missouri dividends deduction (Form MO-C)",
     "data_type": "decimal", "required": False, "sort_order": 15,
     "notes": "⚠⚠ M6: MO-C omits federal Schedule C's Subtotal line, so thirteen consecutive rows are offset "
              "by one. Encoded as an EXPLICIT 21-row map, never an offset."},
    {"fact_key": "zone_modification", "label": "L11 Enterprise / rural empowerment zone income modification",
     "data_type": "decimal", "required": False, "sort_order": 16,
     "notes": "Certificate-gated - 'as approved by the Missouri Department of Economic Development'. "
              "DIRECT-ENTRY."},
    {"fact_key": "lihc_recapture", "label": "L15 Recapture of Missouri low income housing credit",
     "data_type": "decimal", "required": False, "sort_order": 17,
     "notes": "§ 135.355.2. Missouri recapture = Missouri credit x (federal recapture / original federal LIHC "
              "subject to recapture). Direct-entry with a worked helper."},
    {"fact_key": "mo_tc_credits", "label": "L17 Tax credits (Form MO-TC, Line 13)",
     "data_type": "decimal", "required": False, "sort_order": 18,
     "notes": "⚠ M4: where a credit derives from a pass-through, source the SPA from the PTE lane's DERIVED "
              "'tax actually paid' field - NEVER MO-PTE Part B Column 6 at face value. Capped at L16."},
    {"fact_key": "estimated_payments", "label": "L18 Estimated tax payments incl. prior-year overpayment",
     "data_type": "decimal", "required": False, "sort_order": 19,
     "notes": "⚠ Form(s) MO-2ENT Line 7 nonresident-entertainer withholding lands here too."},
    {"fact_key": "extension_payment", "label": "L19 Payments with Form MO-7004", "data_type": "decimal",
     "required": False, "sort_order": 20},
    {"fact_key": "amended_tax_paid", "label": "L20 Amended only - tax paid with/after the original return",
     "data_type": "decimal", "required": False, "sort_order": 21},
    {"fact_key": "amended_overpayment", "label": "L22 Amended only - overpayment shown on the original return",
     "data_type": "decimal", "required": False, "sort_order": 22},
    {"fact_key": "trust_fund_contributions", "label": "L25 Trust fund contributions",
     "data_type": "decimal", "required": False, "sort_order": 23,
     "notes": "12 named funds plus two write-in Additional Fund Codes. The coded funds (01, 02, 03, 05, 07, "
              "08, 09, 10) carry a $1 minimum 'not to exceed $200'; code 14 has a $1 minimum and NO cap."},
    {"fact_key": "credit_to_next_year", "label": "L26 Amount applied to 2026 estimated tax",
     "data_type": "decimal", "required": False, "sort_order": 24},
    {"fact_key": "interest_penalty_2220", "label": "L29 Interest (A) + Penalty (B) + MO-2220 (C)",
     "data_type": "decimal", "required": False, "sort_order": 25},
]

F_RULES: list[dict] = [
    {"rule_id": "R-MO1120-L6", "title": "L6 Balance - federal TI plus additions less subtractions",
     "rule_type": "calculation",
     "formula": "L4 = state_income_taxes_deducted + mo_additions ; L6 = federal_taxable_income + L4 - mo_subtractions",
     "inputs": ["federal_taxable_income", "state_income_taxes_deducted", "mo_additions", "mo_subtractions"],
     "outputs": ["L4", "L6"], "sort_order": 1,
     "description": "Face: 'Balance - Line 1 plus Line 4 minus Line 5.' L1 is federal 1120 Line 30, confirmed "
                    "against the FINAL TY2025 IRS form. ⚠ L2's exclusion of St. Louis and Kansas City "
                    "earnings taxes appears in the INSTRUCTIONS ONLY, not on the face - record it as an "
                    "instruction-sourced rule so a future reader does not go looking for it on the form."},
    {"rule_id": "R-MO1120-FEDTAX", "title": "Part 3 - the FIFTY PERCENT federal income tax deduction",
     "rule_type": "calculation",
     "formula": "P3L3 = (sch_j_total_tax + sch_j_foreign_tax_credit) * 0.50",
     "inputs": ["sch_j_total_tax", "sch_j_foreign_tax_credit"], "outputs": ["L7"], "sort_order": 2,
     "description": "§ 143.171.3: 'a deduction for FIFTY PERCENT of its federal income tax liability ... "
                    "after reduction for all credits thereon, EXCEPT ... 26 U.S.C. Section 31, 26 U.S.C. "
                    "Section 27, and 26 U.S.C. Section 34.' ⭐ THE FOREIGN TAX CREDIT ADD-BACK IS THAT "
                    "EXCEPTION, NOT AN ARBITRARY ADJUSTMENT: IRC § 27 IS the FTC, and Schedule J line 12 is "
                    "already net of it, so the form restores it. §§ 31 and 34 need no restoration because "
                    "they sit BELOW line 12 on Schedule J. ⚠ Encode the rule as '§ 27 only', citing "
                    "§ 143.171.3 - reading it as 'add back Schedule J line 5a' copies the implementation, "
                    "not the rule. ⚠⚠ NO percentage table and NO dollar cap: the $5,000/$10,000 caps and the "
                    "35/25/15/5/0 table are INDIVIDUAL-ONLY and SUNSET ('ending on or before December 31, "
                    "2018'), so they are dead for every taxpayer and year in scope."},
    {"rule_id": "R-MO1120-FEDCON", "title": "Part 3 L4-L6 - consolidated federal, separate Missouri",
     "rule_type": "calculation",
     "formula": "P3L6 = round(separate_company_fti / total_positive_separate_fti, 4) * P3L3",
     "inputs": ["consolidated_federal_separate_mo", "separate_company_fti", "total_positive_separate_fti"],
     "outputs": ["L7"], "sort_order": 3,
     "description": "M3 - this branch IS BUILT because the form fully specifies it. ⚠ THE DENOMINATOR "
                    "EXCLUDES LOSS COMPANIES, verbatim: 'Enter the total of all positive separate company "
                    "federal taxable incomes. Do not include companies which incurred a loss.' Including "
                    "them would inflate the denominator and understate every profitable member's share of "
                    "the deduction. ⚠ The ratio rounds to FOUR decimals here while the page-1 apportionment "
                    "percentage rounds to THREE - two rounding rules on one return, and a single shared "
                    "constant is wrong on one of them."},
    {"rule_id": "R-MO1120-L9", "title": "L9 Preliminary Missouri taxable income - the apportionment branch",
     "rule_type": "calculation",
     "formula": "L8 = L6 - L7 ; L9 = L8 if is_all_missouri else round(L8 * apportionment_percent, 2)",
     "inputs": ["is_all_missouri", "apportionment_method", "apportionment_percent"],
     "outputs": ["L8", "L9"], "sort_order": 4,
     "description": "Face: 'If all Missouri income, enter amount from Line 8. If not, complete and attach "
                    "Form MO-MS.' The percentage is 'rounded to THREE digits to the right of the decimal "
                    "point, such as 12.345 percent'. ⚠ W3: a hard RED where the MO-MS line 12 divisor is "
                    "zero or negative. ⚠ W5: Methods Three to Seven are RED-deferred, but the routing help "
                    "copy still ships - a trucking company that picks 'Three - Transportation' off the label "
                    "files a wrong return."},
    {"rule_id": "R-MO1120-L13", "title": "L13 Missouri taxable income - floored at zero",
     "rule_type": "calculation",
     "formula": "L13 = max(0, L9 - mo_dividends_deduction - zone_modification)",
     "inputs": ["mo_dividends_deduction", "zone_modification"], "outputs": ["L13"], "sort_order": 5,
     "description": "Face: 'Line 9 minus Lines 10 and 11. Do not enter a negative number. If the result is "
                    "less than zero, enter zero.' ⚠ Line 12 is printed 'RESERVED ... for future use' yet "
                    "still carries a live entry box on the face - accept nothing into it."},
    {"rule_id": "R-MO1120-L14", "title": "L14 Corporation income tax - 4%, never prorated",
     "rule_type": "calculation", "formula": "L14 = round(L13 * 0.04, 2)",
     "inputs": [], "outputs": ["L14"], "sort_order": 6,
     "description": "§ 143.071.3: 'a tax ... in an amount equal to FOUR PERCENT of Missouri taxable income.' "
                    "⚠ Instruction, verbatim: 'Income tax cannot be prorated or annualized.' A short period "
                    "does NOT get a proportionate rate, and no annualisation applies to a part-year return."},
    {"rule_id": "R-MO1120-L16", "title": "L16 Total tax - and it is the MO-TC credit CAP",
     "rule_type": "calculation", "formula": "L16 = L14 + lihc_recapture",
     "inputs": ["lihc_recapture"], "outputs": ["L16"], "sort_order": 7,
     "description": "Face: 'Total tax - Add Lines 14 and 15.' ⚠ This figure is the CAP on MO-TC credits at "
                    "line 17 - credits cannot reduce the liability below zero. ⚠ M4: where a credit derives "
                    "from a pass-through, source the SPA from the PTE lane's DERIVED 'tax actually paid' "
                    "field, NEVER MO-PTE Part B Column 6 at face value - taking the printed column at face "
                    "value imports the PTE-side defect straight into the corporate return."},
    {"rule_id": "R-MO1120-L21", "title": "L21 Subtotal - build the FACE, not the orphaned instruction",
     "rule_type": "calculation",
     "formula": "L21 = mo_tc_credits + estimated_payments + extension_payment + amended_tax_paid",
     "inputs": ["mo_tc_credits", "estimated_payments", "extension_payment", "amended_tax_paid"],
     "outputs": ["L21"], "sort_order": 8,
     "description": "⚠ THE INSTRUCTIONS CARRY TWO CONFLICTING LINE-21 RULES. Page 5 says 'Enter the total of "
                    "Lines 17 through 20', which agrees with the face. Page 6, orphaned above the Line 22 "
                    "heading, says 'Enter the total of Lines 18, 19, 20, and 21' - SELF-REFERENTIAL AND "
                    "WRONG; a line cannot be an input to itself. BUILD THE FACE. Recorded so a future reader "
                    "does not 'correct' this toward the defective instruction."},
    {"rule_id": "R-MO1120-SETTLE", "title": "L23-L30 - settlement, refund floor and amount due",
     "rule_type": "calculation",
     "formula": ("L23 = L21 - amended_overpayment ; L24 = max(0, L23 - L16) ; "
                 "L27 = L24 - trust_fund_contributions - credit_to_next_year ; "
                 "L28 = max(0, L16 - L23) ; L30 = L28 + interest_penalty_2220"),
     "inputs": ["amended_overpayment", "trust_fund_contributions", "credit_to_next_year",
                "interest_penalty_2220"], "outputs": ["L23", "L24", "L27", "L28", "L30"], "sort_order": 9,
     "description": "L24 and L28 are mutually exclusive by construction. ⚠ 'No refund of less than $1.00 "
                    "will be made.' ⚠ A refund of $100,000 or more must be issued ELECTRONICALLY - the "
                    "return must be filed electronically with Form 5378 attached. L29 is the total of three "
                    "boxes: A interest, B penalty, C from Form MO-2220."},
    {"rule_id": "R-MO1120-MOC", "title": "⚠⚠ MO-C is an explicit 21-row map, NEVER an offset",
     "rule_type": "validation",
     "formula": "federal_line = MO_C_TO_FEDERAL_SCHEDULE_C[mo_c_line]  # explicit dict, no arithmetic",
     "inputs": ["mo_dividends_deduction"], "outputs": [], "sort_order": 10,
     "description": "⚠⚠ M6. MO-C mirrors federal Schedule C but OMITS the federal 'Subtotal. Add lines 1 "
                    "through 8' line (federal line 9). From that point every MO-C line is ONE LOWER than its "
                    "federal counterpart - MO-C 9 = federal 10, MO-C 10 = federal 11, and so on for THIRTEEN "
                    "consecutive rows. An engine assuming MO-C N == federal N is wrong across all of them "
                    "AND WRONG SILENTLY: the return still foots, the dividends deduction is simply wrong. "
                    "This is the C-corp twin of the PTE K-1 silent-failure defect. Encoded as an EXPLICIT "
                    "map; any offset formula is wrong for part of the range. ⚠ MO-C is 'Revised 03-2026', "
                    "NEWER than its own instructions, so where they disagree the FACE governs. ⚠ Branch 3's "
                    "percentage source is TWO-VALUED while the face records only one - build the "
                    "instruction's two-branch rule and label the field from the instruction, not the face."},
]

F_RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R-MO1120-L6", "MO_2025_FORM_1120", "primary", "L1-L6 face labels"),
    ("R-MO1120-FEDTAX", "MO_RSMO_143_171", "primary", "the 50% deduction and the IRC 31/27/34 exceptions"),
    ("R-MO1120-FEDTAX", "MO_2025_FORM_1120", "secondary", "Part 3 lines 1-3"),
    ("R-MO1120-FEDCON", "MO_2025_FORM_1120", "primary", "Part 3 lines 4-6 and the loss-company exclusion"),
    ("R-MO1120-L9", "MO_2025_FORM_1120", "primary", "L9 and the three-decimal percentage"),
    ("R-MO1120-L13", "MO_2025_FORM_1120", "primary", "L13 and the zero floor"),
    ("R-MO1120-L14", "MO_RSMO_143_071", "primary", "the 4% rate"),
    ("R-MO1120-L14", "MO_2025_FORM_1120", "secondary", "L14 and 'cannot be prorated or annualized'"),
    ("R-MO1120-L16", "MO_2025_FORM_1120", "primary", "L16 as the MO-TC cap"),
    ("R-MO1120-L21", "MO_2025_FORM_1120", "primary", "the face rule, against the orphaned instruction"),
    ("R-MO1120-SETTLE", "MO_2025_FORM_1120", "primary", "L23-L30"),
    ("R-MO1120-MOC", "MO_2025_FORM_MOC", "primary", "the dropped Subtotal line and the 13-row offset"),
]

F_LINES: list[dict] = [
    {"line_number": "MO1120-4", "description": "L4 Total additions (L2 + L3)", "line_type": "subtotal",
     "source_rules": ["R-MO1120-L6"], "sort_order": 1},
    {"line_number": "MO1120-6", "description": "L6 Balance (L1 + L4 - L5)", "line_type": "subtotal",
     "source_rules": ["R-MO1120-L6"], "sort_order": 2},
    {"line_number": "MO1120-7", "description": "L7 Federal income tax deduction (Part 3 L3 or L6)",
     "line_type": "calculated", "source_rules": ["R-MO1120-FEDTAX", "R-MO1120-FEDCON"], "sort_order": 3},
    {"line_number": "MO1120-8", "description": "L8 Taxable income, all sources (L6 - L7)",
     "line_type": "subtotal", "source_rules": ["R-MO1120-L9"], "sort_order": 4},
    {"line_number": "MO1120-9", "description": "L9 Preliminary Missouri taxable income (THREE decimals)",
     "line_type": "calculated", "source_rules": ["R-MO1120-L9"], "sort_order": 5},
    {"line_number": "MO1120-13", "description": "L13 Missouri taxable income (floored at zero)",
     "line_type": "subtotal", "source_rules": ["R-MO1120-L13"], "sort_order": 6},
    {"line_number": "MO1120-14", "description": "L14 Corporation income tax (4%, never prorated)",
     "line_type": "calculated", "source_rules": ["R-MO1120-L14"], "sort_order": 7},
    {"line_number": "MO1120-16", "description": "L16 Total tax - and the MO-TC credit cap",
     "line_type": "subtotal", "source_rules": ["R-MO1120-L16"], "sort_order": 8},
    {"line_number": "MO1120-21", "description": "L21 Subtotal (L17 through L20, per the FACE)",
     "line_type": "subtotal", "source_rules": ["R-MO1120-L21"], "sort_order": 9},
    {"line_number": "MO1120-24", "description": "L24 Overpayment", "line_type": "calculated",
     "source_rules": ["R-MO1120-SETTLE"], "sort_order": 10},
    {"line_number": "MO1120-27", "description": "L27 REFUND (none below $1.00)", "line_type": "calculated",
     "source_rules": ["R-MO1120-SETTLE"], "sort_order": 11},
    {"line_number": "MO1120-30", "description": "L30 AMOUNT DUE (L28 + L29)", "line_type": "calculated",
     "source_rules": ["R-MO1120-SETTLE"], "sort_order": 12},
    {"line_number": "MO1120-P3L3", "description": "Part 3 L3 Federal income tax deduction base (50%)",
     "line_type": "calculated", "source_rules": ["R-MO1120-FEDTAX"], "sort_order": 13},
    {"line_number": "MO1120-P3L6", "description": "Part 3 L6 Consolidated ratio applied (FOUR decimals)",
     "line_type": "calculated", "source_rules": ["R-MO1120-FEDCON"], "sort_order": 14},
]

F_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_MO1120_FED_ATTACHMENT_CLIFF", "severity": "error",
     "title": "⚠⚠ Missing attachments can reduce the federal income tax deduction TO ZERO",
     "condition": "consolidated_federal_separate_mo == True and fed_deduction_attachments_sent != True",
     "message": "This return claims the federal income tax deduction on a consolidated-federal / "
                "separate-Missouri basis, and Missouri states on the form face: 'Consolidated federal and "
                "separate Missouri return filers must attach consolidated Federal Form 1120, Schedule J, and "
                "an income statement or summary of profit companies. IF INFORMATION IS NOT SENT, THE FEDERAL "
                "INCOME TAX DEDUCTION MAY BE REDUCED TO ZERO.' Attach ALL of: (1) the CONSOLIDATED Federal "
                "Form 1120; (2) Federal Form 1120 Schedule J; (3) an income statement; or (4) a summary of "
                "profit companies. Regulatory basis: 12 CSR 10-2.090 and 12 CSR 10-2.165. ⚠ This is a "
                "100%-of-deduction cliff, not a processing formality - a dismissed warning and a zeroed "
                "deduction look identical on the filed return, and the client finds out when Missouri "
                "adjusts them.",
     "notes": "⚠⚠ M5 - Ken ruled a HARD BLOCK enumerating the attachments, precisely because the failure is "
              "invisible on the return."},
    {"diagnostic_id": "D_MO1120_ALT_FEDERAL_RETURN", "severity": "error",
     "title": "⚠ Alternative federal return types are not supported",
     "condition": "federal_return_type in ('1120-C','1120-F','1120-L','1120-PC','1120-REIT','1120-RIC')",
     "message": "This version supports only a standard Federal Form 1120 as the starting point. Missouri "
                "publishes NO crosswalk stating which line of Form 1120-C, 1120-F, 1120-L, 1120-PC, "
                "1120-REIT or 1120-RIC feeds MO-1120 Line 1. Because the entire Missouri computation rides "
                "on Line 1, a guessed starting figure would be wrong all the way down the return. Prepare "
                "this return outside this software.",
     "notes": "M2 - the second-largest scope decision in the Missouri wave. Refuse rather than invent."},
    {"diagnostic_id": "D_MO1120_MO_CONSOLIDATED", "severity": "error",
     "title": "A true Missouri consolidated return is not supported",
     "condition": "filing a Missouri consolidated return",
     "message": "This version does not compute a Missouri consolidated return. It DOES support the common "
                "case of a group that files a CONSOLIDATED FEDERAL return and SEPARATE Missouri returns - "
                "that branch is fully specified on the form at Part 3 lines 4 through 6 and is computed "
                "here. A true Missouri consolidated filing must be prepared outside this software.",
     "notes": "M3 - refuse what we would have to invent; build what the form already lays out."},
    {"diagnostic_id": "D_MO1120_MOC_OFFSET", "severity": "warning",
     "title": "⚠⚠ Form MO-C line numbers do NOT match federal Schedule C from line 9 onward",
     "condition": "mo_dividends_deduction > 0",
     "message": "Form MO-C mirrors federal Schedule C but OMITS the federal 'Subtotal' line (federal line "
                "9). From that point on every MO-C line is ONE LOWER than its federal counterpart: MO-C line "
                "9 corresponds to federal line 10, MO-C 10 to federal 11, and so on for THIRTEEN consecutive "
                "rows. ⚠ Transcribe each figure from the federal line the MO-C label names, not by matching "
                "line numbers - a mismatched carry produces a wrong dividends deduction on a return that "
                "still adds up correctly. ⚠ MO-C is 'Revised 03-2026', NEWER than its own instructions; "
                "where they disagree, the form face governs.",
     "notes": "⚠⚠ M6 - the C-corp twin of the PTE K-1 silent-failure defect. Encoded as an explicit map."},
    {"diagnostic_id": "D_MO1120_PTE_CREDIT_SOURCE", "severity": "warning",
     "title": "⚠ Pass-through credits must come from the DERIVED figure, not MO-PTE Part B Column 6",
     "condition": "mo_tc_credits > 0",
     "message": "Where a Missouri credit derives from a pass-through entity, the shareholder's pro-rata "
                "amount must be taken from the pass-through lane's DERIVED 'tax actually paid' figure - NOT "
                "from Form MO-PTE Part B Column 6 at face value. Taking the printed column at face value "
                "imports a known defect from the pass-through side straight into the corporate return. ⚠ "
                "Note also that credits are capped at Line 16 (total tax) and cannot reduce the liability "
                "below zero.",
     "notes": "M4 - the credit-poisoning path reaches the corporate side."},
    {"diagnostic_id": "D_MO1120_APPORT_METHOD", "severity": "warning",
     "title": "Apportionment methods Three to Seven are not computed - and the labels mislead",
     "condition": "apportionment_method not in (None, '2a')",
     "message": "This version computes Missouri apportionment Method 2a only. Methods Three through Seven "
                "are not computed and must be prepared on Form MO-MS outside this software. ⚠ CHOOSE THE "
                "METHOD FROM THE STATUTE, NOT FROM THE LABEL: the method names describe the STATUTORY "
                "computation, not the taxpayer's industry. A trucking company that selects 'Three - "
                "Transportation' because it hauls freight, rather than because the statutory test applies, "
                "files a wrong return. ⚠ A hard error is raised separately where the MO-MS line 12 divisor "
                "is zero or negative.",
     "notes": "W5 - Ken ruled the routing help copy still ships even though the methods are deferred."},
    {"diagnostic_id": "D_MO1120_FED_DEDUCTION_NOTE", "severity": "info",
     "title": "The federal income tax deduction is 50% with no cap - the individual figures do not apply",
     "condition": "sch_j_total_tax > 0",
     "message": "Missouri allows a corporate deduction for FIFTY PERCENT of federal income tax liability "
                "(Section 143.171.3 RSMo), with NO percentage table and NO dollar cap. ⚠ Do not apply the "
                "$5,000 / $10,000 caps or the 35/25/15/5/0 percentage table - those belong to Section "
                "143.171.1-.2, which are INDIVIDUAL-only AND sunset (subsection .1 applies only to years "
                "'ending on or before December 31, 2018'). They are dead for every taxpayer and every year "
                "in scope, for two independent reasons. ⚠ The foreign tax credit is added back because "
                "Section 143.171.3 excepts IRC Section 27 from the credits that reduce the base - Schedule J "
                "line 12 is already net of it.",
     "notes": "The single easiest way to get Missouri wrong, per the conformity brief."},
    {"diagnostic_id": "D_MO1120_ROUNDING_SPLIT", "severity": "info",
     "title": "Two different rounding rules on one return",
     "condition": "consolidated_federal_separate_mo == True and is_all_missouri != True",
     "message": "Missouri rounds two ratios on this return to DIFFERENT precisions. The page-1 line 9 "
                "apportionment percentage rounds to THREE digits right of the decimal ('such as 12.345 "
                "percent'). The Part 3 line 6 federal-tax-deduction ratio rounds to FOUR ('such as 12.3456 "
                "percent'). A single shared rounding constant is wrong on one of them.",
     "notes": "Recorded because it is exactly the kind of asymmetry a shared helper quietly flattens."},
    {"diagnostic_id": "D_MO1120_NOL_20YR", "severity": "info",
     "title": "The Missouri NOL carryforward cap is encoded now, though dormant for TY2025",
     "condition": "always (informational)",
     "message": "Missouri's net operating loss carryforward is capped at 20 years. The cap is dormant for "
                "tax year 2025 and first bites in 2038 for losses generated now - but it is LIVE TODAY for "
                "long-dated pre-2018 losses still being carried. It is encoded in this version rather than "
                "deferred, because a dated rule with a known fuse is cheaper to defuse than to discover.",
     "notes": "M7."},
    {"diagnostic_id": "D_MO1120_REFUND_RULES", "severity": "info",
     "title": "Refund floor and the electronic-issue threshold",
     "condition": "L27 > 0",
     "message": "Missouri will not issue a refund of less than $1.00. ⚠ A refund of $100,000 or more must be "
                "issued ELECTRONICALLY - the return must be filed electronically and Form 5378 attached. "
                "Note also that a refund may be reduced by trust-fund contributions on line 25 and by any "
                "amount applied to next year's estimated tax on line 26.",
     "notes": "Face rules; the $100,000 electronic requirement is easy to miss on a large return."},
]

F_SCENARIOS: list[dict] = [
    {"scenario_name": "MO1120-A - all-Missouri corporation at 4%", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"federal_taxable_income": 1000000, "is_all_missouri": True,
                "sch_j_total_tax": 210000, "sch_j_foreign_tax_credit": 0},
     "expected_outputs": {"MO1120-7": 105000, "MO1120-8": 895000, "MO1120-13": 895000, "MO1120-14": 35800},
     "notes": "Federal tax 210,000 x 50% = 105,000 deduction. 1,000,000 - 105,000 = 895,000 x 4% = 35,800."},
    {"scenario_name": "MO1120-B - the foreign tax credit is ADDED BACK before the 50%",
     "scenario_type": "edge", "sort_order": 2,
     "inputs": {"federal_taxable_income": 2000000, "is_all_missouri": True,
                "sch_j_total_tax": 300000, "sch_j_foreign_tax_credit": 80000},
     "expected_outputs": {"MO1120-P3L3": 190000},
     "notes": "⭐ (300,000 + 80,000) x 50% = 190,000, NOT 150,000. Sec. 143.171.3 excepts IRC Sec. 27 - the "
              "FTC - from the credits that reduce the base, and Schedule J line 12 is already net of it. "
              "Omitting the add-back would understate the deduction by 40,000 and OVERSTATE Missouri tax."},
    {"scenario_name": "MO1120-C - consolidated federal, separate Missouri (FOUR decimals)",
     "scenario_type": "edge", "sort_order": 3,
     "inputs": {"consolidated_federal_separate_mo": True, "sch_j_total_tax": 400000,
                "sch_j_foreign_tax_credit": 0, "separate_company_fti": 1234567,
                "total_positive_separate_fti": 10000000, "fed_deduction_attachments_sent": True},
     "expected_outputs": {"MO1120-P3L3": 200000, "MO1120-P3L6": 24691.4},
     "notes": "Ratio 1,234,567/10,000,000 = 0.1234567 -> 0.1235 at FOUR decimals; x 200,000 = 24,700. "
              "⚠ Note the page-1 percentage would round to THREE decimals - two rules on one return."},
    {"scenario_name": "MO1120-D - ⚠⚠ missing attachments zero the deduction", "scenario_type": "edge",
     "sort_order": 4,
     "inputs": {"consolidated_federal_separate_mo": True, "sch_j_total_tax": 400000,
                "fed_deduction_attachments_sent": False},
     "expected_outputs": {"diagnostic": "D_MO1120_FED_ATTACHMENT_CLIFF"},
     "notes": "⚠⚠ M5. 'If information is not sent, the federal income tax deduction may be reduced to zero.' "
              "A hard block, because a dismissed warning and a zeroed deduction look identical on the filed "
              "return."},
    {"scenario_name": "MO1120-E - the loss-company exclusion from the denominator",
     "scenario_type": "edge", "sort_order": 5,
     "inputs": {"consolidated_federal_separate_mo": True, "separate_company_fti": 500000,
                "total_positive_separate_fti": 2000000, "sch_j_total_tax": 200000,
                "fed_deduction_attachments_sent": True},
     "expected_outputs": {"MO1120-P3L6": 25000},
     "notes": "⚠ The denominator counts POSITIVE separate-company incomes only - 'Do not include companies "
              "which incurred a loss.' Including a loss member would inflate the denominator and understate "
              "every profitable member's share. 0.25 x 100,000 = 25,000."},
    {"scenario_name": "MO1120-F - ⚠⚠ MO-C line 9 maps to FEDERAL line 10, not 9",
     "scenario_type": "edge", "sort_order": 6,
     "inputs": {"mo_c_line": 9},
     "expected_outputs": {"federal_schedule_c_line": 10, "diagnostic": "D_MO1120_MOC_OFFSET"},
     "notes": "⚠⚠ M6. MO-C omits federal Schedule C's 'Subtotal' line, so the correspondence breaks at 9 and "
              "stays broken for THIRTEEN rows. Matching line numbers produces a wrong dividends deduction on "
              "a return that still foots."},
    {"scenario_name": "MO1120-G - MO-C lines 1-8 DO match federal 1-8", "scenario_type": "edge",
     "sort_order": 7,
     "inputs": {"mo_c_line": 8},
     "expected_outputs": {"federal_schedule_c_line": 8},
     "notes": "The pair to MO1120-F: the offset is not uniform, which is exactly why an arithmetic rule is "
              "wrong for part of the range and an explicit map is required."},
    {"scenario_name": "MO1120-H - an alternative federal return is refused", "scenario_type": "edge",
     "sort_order": 8,
     "inputs": {"federal_return_type": "1120-REIT"},
     "expected_outputs": {"diagnostic": "D_MO1120_ALT_FEDERAL_RETURN"},
     "notes": "M2 - no published crosswalk to Line 1, and the whole computation rides on Line 1."},
    {"scenario_name": "MO1120-I - L13 floors at zero and the tax follows", "scenario_type": "edge",
     "sort_order": 9,
     "inputs": {"federal_taxable_income": 100000, "is_all_missouri": True, "sch_j_total_tax": 40000,
                "mo_dividends_deduction": 150000},
     "expected_outputs": {"MO1120-13": 0, "MO1120-14": 0},
     "notes": "Face: 'Do not enter a negative number. If the result is less than zero, enter zero.' 80,000 - "
              "150,000 would be negative, so L13 is zero and the 4% applies to nothing."},
    {"scenario_name": "MO1120-J - the individual caps must never appear", "scenario_type": "edge",
     "sort_order": 10,
     "inputs": {"sch_j_total_tax": 5000000, "is_all_missouri": True},
     "expected_outputs": {"MO1120-P3L3": 2500000},
     "notes": "⚠⚠ 5,000,000 x 50% = 2,500,000 with NO cap. Applying the individual $5,000 or $10,000 cap "
              "would understate the deduction by millions - and those caps are both INDIVIDUAL-only AND "
              "sunset after 2018, so they are dead twice over."},
]


FORMS: list[dict] = [
    {
        "identity": {
            "form_number": "MO_1120",
            "form_title": "Missouri Form MO-1120 - Corporation Income Tax Return (TY2025)",
            "notes": (
                "WO-W05-CCORP; walk closed at campaign D-24. Missouri's C-corp return: federal TI (1120 "
                "L30) + Missouri modifications - the FIFTY PERCENT federal income tax deduction -> "
                "apportionment -> 4% (Sec. 143.071.3, never prorated or annualized). ⚠⚠ The federal income "
                "tax deduction adds back the FOREIGN TAX CREDIT because Sec. 143.171.3 excepts IRC Sec. 27; "
                "it has NO percentage table and NO cap, and the individual $5,000/$10,000 figures are both "
                "inapplicable AND sunset. ⚠⚠ MISSING ATTACHMENTS CAN ZERO THE DEDUCTION - a hard block. "
                "⚠⚠ MO-C omits federal Schedule C's Subtotal line, so THIRTEEN rows are offset by one - "
                "encoded as an explicit map, never arithmetic. ⚠ Two rounding rules on one return: page-1 "
                "apportionment THREE decimals, Part 3 ratio FOUR. ⚠ Six alternative federal returns and "
                "true Missouri consolidated returns are refused; the consolidated-federal / "
                "separate-Missouri branch IS built."
            ),
        },
        "facts": F_FACTS, "rules": F_RULES, "rule_links": F_RULE_LINKS,
        "lines": F_LINES, "diagnostics": F_DIAGNOSTICS, "scenarios": F_SCENARIOS,
    },
]

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-MO1120-FEDTAX", "title": "The federal tax deduction is 50% of (Sch J L12 + FTC)",
     "assertion_type": "reconciliation", "entity_types": ["1120"], "status": "draft", "sort_order": 1,
     "description": "⭐ The FTC add-back is § 143.171.3's exception for IRC § 27, not an arbitrary "
                    "adjustment: Schedule J line 12 is already net of the FTC, so the form restores it. "
                    "§§ 31 and 34 sit below line 12 and need no restoration. NO table, NO cap.",
     "definition": {"rule": "R-MO1120-FEDTAX", "check": "P3L3 == (schJ_L12 + schJ_L5a) * 0.50"}},
    {"assertion_id": "FA-MO1120-MOC", "title": "⚠⚠ MO-C maps by explicit lookup, never by offset",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 2,
     "description": "MO-C omits federal Schedule C's Subtotal line, so lines 1-8 match federally while lines "
                    "9-21 map to federal 10-22 - thirteen rows offset by one. The offset is NOT uniform "
                    "across the form, so any arithmetic rule is wrong for part of the range, and wrong "
                    "silently: the return still foots while the dividends deduction is wrong.",
     "definition": {"rule": "R-MO1120-MOC", "check": "explicit 21-entry map; no arithmetic offset"}},
    {"assertion_id": "FA-MO1120-CLIFF", "title": "Missing attachments are a hard block, not a warning",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 3,
     "description": "⚠⚠ 'If information is not sent, the federal income tax deduction may be reduced to "
                    "zero.' A dismissed warning and a zeroed deduction look identical on the filed return, "
                    "and the client learns of it only when Missouri adjusts them.",
     "definition": {"rule": "R-MO1120-FEDCON", "check": "attachments not sent -> hard error, not warning"}},
    {"assertion_id": "FA-MO1120-ROUND", "title": "THREE decimals on page 1, FOUR in Part 3",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 4,
     "description": "⚠ Two different rounding rules on one return. A single shared rounding constant is "
                    "wrong on one of them.",
     "definition": {"rule": "R-MO1120-FEDCON", "check": "apport decimals == 3 and fed ratio decimals == 4"}},
    {"assertion_id": "FA-MO1120-L21", "title": "Line 21 is built from the FACE, not the orphaned instruction",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 5,
     "description": "⚠ The instructions carry two line-21 rules; the page-6 version says 'the total of Lines "
                    "18, 19, 20, and 21' - self-referential and wrong, since a line cannot be an input to "
                    "itself. The face says lines 17 through 20 and governs.",
     "definition": {"rule": "R-MO1120-L21", "check": "L21 == L17 + L18 + L19 + L20"}},
]


class Command(BaseCommand):
    help = ("Load the MO_1120 spec (Missouri Corporation Income Tax Return, TY2025). "
            "Refuses to seed until Ken's Gate-1 SEED approval.")

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad MO_1120 spec (Missouri Corporation Income Tax Return, TY2025)\n"))
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
                "\nREFUSING TO SEED MO_1120: not cleared to seed.\n\n"
                "Campaign D-24 approved the Missouri walk SCOPE (14 items). That is NOT the seed\n"
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
        self.stdout.write("MO_1120 loaded (TY2025 ONLY - every figure is TY-keyed).")
        self.stdout.write(f"  MO_1120: facts {len(F_FACTS)} / rules {len(F_RULES)} / lines {len(F_LINES)} / "
                          f"diag {len(F_DIAGNOSTICS)} / tests {len(F_SCENARIOS)}")
        self.stdout.write(f"  Flow assertions: {len(FLOW_ASSERTIONS)}")
        self.stdout.write("  !! MO-C maps by explicit lookup, never by offset - see R-MO1120-MOC.")
        self.stdout.write("=" * 66)
