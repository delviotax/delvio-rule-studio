"""Load the Virginia Form 500 spec — Corporation Income Tax Return (TY2025).

WO-W05-CCORP. Virginia's walk closed at campaign **D-21** (12 items).

═══════════════════════════════════════════════════════════════════════════
WHAT THIS IS
═══════════════════════════════════════════════════════════════════════════
`VA_500` is Virginia's C-corporation return: a FLAT 6% tax on Virginia taxable
income. Federal taxable income (AFTER federal NOL and special deductions) →
Schedule 500ADJ modifications → Schedule 500A apportionment for multistate
filers → 6% → credits → settlement.

⚠ Ken's LOI decision (campaign D-22) declares ONLY `VA_502` + `VA_502PTET` to
Virginia — NOT `VA_500`. **This spec is for print/compute and TY2027 readiness,
not for the coming e-file season.** That is a scope fact, not a defect.

═══════════════════════════════════════════════════════════════════════════
⚠⚠ LINE 11 IS AN OVERWRITE TARGET, NOT A DERIVED LINE (D-21 / V6)
═══════════════════════════════════════════════════════════════════════════
THE SINGLE MOST DANGEROUS THING IN THIS SPEC. Virginia has no general corporate
minimum tax, but FOUR SCC-certified industry regimes each REPLACE the computed
tax on Line 11:

    Telecommunications company        Form 500T     gross receipts x 0.5%
    Noncorporate telecommunications   Form 500T Pt III      same 0.5%
    Electric supplier                 Sch. 500EL    ⚠ SCC-CERTIFIED, no rate
                                                      appears on the form
    Home service contract provider    Form 500HS    provider's fees x 2.25%

Schedule 500EL, verbatim: "Enter this amount on Line 11 of Form 500, and
**replace the amount computed on Form 500**." Form 500HS goes further: "if the
amount on Line 10 is equal to minimum tax, enter this amount on **Line 11 of
Form 500 and enter $0 on Line 10 of Form 500**."

**AN ENGINE THAT MODELS LINE 11 AS DERIVED-ONLY WILL SILENTLY DISCARD THE
MINIMUM TAX AND UNDER-TAX A CERTIFIED FILER ON A RETURN THAT LOOKS PERFECTLY
CLEAN.** The four regimes are RED-deferred in v1, but **the overwrite path must
exist in v1 regardless** — that is exactly what D-21 ruled.

═══════════════════════════════════════════════════════════════════════════
KEN'S RULINGS THIS SPEC IMPLEMENTS (campaign D-21, and D-18/G1)
═══════════════════════════════════════════════════════════════════════════
G1  The Schedule 500A missing-factor divisor is a TRANSCRIPTION from
    Va. Code § 58.1-408 A — weight-sum 4/3/3/2 — NOT an interpretation.
    ⚠ Building to statute knowingly diverges from printed FINAL sources in BOTH
    directions, and Ken accepted that on the record. The Form 502 instruction
    book restates § 58.1-408 A but DROPS the words "plus one".
V2  v1 supports SEPARATE RETURNS ONLY. Combined and consolidated returns are
    refused behind a HARD RED GATE. Virginia's filing-status election is
    effectively permanent once made, so refusing beats computing wrongly.
V3  Depreciation stays v1 DIRECT-ENTRY (engine v1.1). ⚠⚠ The derived
    $1,250,000 / $3,130,000 / $31,300 are NEVER encoded as Virginia constants —
    Virginia publishes no § 179 figure of its own, and inventing one is exactly
    what the campaign's authoritative-source rule forbids.
V4  The residual conformity bucket routes to 500ADJ A2/B2. ⚠ That bucket SHARES
    ONE DOLLAR BOX with the bonus disposed-asset true-up.
V5  The § 58.1-408 B eligible-company NUMERATOR reduction is RED-DEFERRED with a
    prepare-manually diagnostic. Live, money-moving, and with NO line, NO
    checkbox and NO instruction anywhere on any corporate form.
V6  The four minimum-tax overlays are RED-DEFERRED — but see the Line 11
    overwrite warning above, which binds v1 anyway.
W7  The filing-status checkbox is a PREPARER ASSERTION, never derived.
W11 The combined→consolidated change diagnostic follows the STATUTE
    (§ 58.1-442 C), NOT the instruction book, which prints a narrower rule.

═══════════════════════════════════════════════════════════════════════════
⚠ G4 — NEVER CLONE A SIBLING FORM'S LINE NUMBERS (campaign D-18)
═══════════════════════════════════════════════════════════════════════════
Every line here is transcribed from the FORM 500 FACE. Virginia's corporate and
PTE modules use DIFFERENT code numbers for the same concepts, and ⚠ SEVEN code
numbers exist on BOTH forms with DIFFERENT MEANINGS (additions 14, 16, 21;
subtractions 50, 56, 57, 58). A silent port does not 404 — it lands on a real,
wrong code. Worst pair: addition 21 and subtraction 58 each carry
"partnership-level federal adjustment" on ONE form and something unrelated on
the other.

═══════════════════════════════════════════════════════════════════════════
v1 SCOPE
═══════════════════════════════════════════════════════════════════════════
COMPUTES: the Line 1→9 spine, the 6% tax, the Schedule 500A weight-sum
apportionment, and the settlement block (Lines 10–24) INCLUDING the Line 11
overwrite path.
DIRECT-ENTRY: 500ADJ Section A/B totals; depreciation (V3); 500CR credit totals.
RED-DEFERRED: combined/consolidated (V2); the four minimum-tax overlays (V6);
§ 58.1-408 B (V5).

SAFETY GUARD — READY_TO_SEED stays False until Ken's Gate-1 SEED approval.
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
# GATE 1 CLEARED - flipped 2026-08-23 on Ken's DIRECT seed approval.
#
# Ken, in-session: "approved", in answer to a message naming exactly
# VA_500, AZ_120 and AZ_120A - then re-confirmed for scope after the
# pre-flight finding below, because a bare word across three specs and two
# states is not a gate I should widen by inference.
#
# D-21 approved the walk SCOPE. This is the separate Gate-1 SEED approval.
#
# Pre-flight against PROD before flipping:
#   * every CharField value measured against the REAL model max_length - CLEAN
#   * the state's TY2025 conformity row confirmed PRESENT before the forms
#     (D-8's order, intact)
#   * referenced source codes verified to RESOLVE - no dangling reference
#   * declared source codes checked against every other loader - no two
#     writers of one row
# D-21 approved the walk SCOPE (12 items). That is not the seed gate.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = True


FORM_JURISDICTION = "VA"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"
FORM_ENTITY_TYPES = ["1120"]

# Va. Code § 58.1-400 — the flat corporate rate. Line 9: "Income tax [6% of
# Line 7 or 6% of Line 8(a)]".
VA_CORP_RATE: dict[int, str] = {2025: "0.06"}

# Schedule 500A apportionment weights. ⚠ D-18/G1: the divisor is the SUM OF THE
# WEIGHTS of the factors that EXIST, transcribed from Va. Code § 58.1-408 A —
# all three -> 4, sales missing -> 2, property or payroll missing -> 3.
VA_APPORT_WEIGHTS: dict[int, dict] = {2025: {"property": 1, "payroll": 1, "sales": 2}}
VA_APPORT_DECIMALS: dict[int, int] = {2025: 6}

# Savings and Loan bad-debt deduction, percentage-of-income method (§ 58.1-403).
# ⚠ The OTHER methods (percentage-of-loans, experience) do NOT use this line at
# all — they use ADDITION CODE 13 instead.
VA_SL_BAD_DEBT_PCT: dict[int, str] = {2025: "0.40"}

# ⚠⚠ DELIBERATELY ABSENT: Virginia publishes NO § 179 figure of its own. The
# derived $1,250,000 / $3,130,000 / $31,300 must NEVER appear as Virginia
# constants (D-21/V3). This comment exists so their absence reads as a decision
# rather than an oversight, and the harness asserts they are not here.


def _yk(table: dict, year: int = FORM_TAX_YEAR):
    """Year-keyed lookup. A new tax year staleness-invalidates every figure."""
    if year not in table:
        raise CommandError(f"No TY{year} value in {table!r} — re-verify before extending the year.")
    return table[year]


def _va500_apportionment_pct(prop, pay, sales, year: int = FORM_TAX_YEAR):
    """Schedule 500A Section B — the weight-sum divisor.

    ⚠ D-18/G1: this is a TRANSCRIPTION from Va. Code § 58.1-408 A, not an
    interpretation. The statute states both branches outright:

        "...the denominator of which is four; however, where the sales factor
        does not exist, the denominator of the fraction shall be the number of
        existing factors and where the sales factor exists but the payroll
        factor or the property factor does not exist, the denominator of the
        fraction shall be the number of existing factors plus one."

    Applied — the SUM OF THE WEIGHTS of the factors that exist:
        all three exist  -> 4        sales missing    -> 2
        property missing -> 3        payroll missing  -> 3

    ⚠ BUILDING TO STATUTE KNOWINGLY DIVERGES FROM PRINTED FINAL SOURCES IN BOTH
    DIRECTIONS, accepted by Ken on the record:
        sales missing            statute 2 | the 500A face, 502A face, 500A
                                            instructions and 500AC all yield
                                            otherwise -> MORE tax
        payroll/property missing statute 3 | the Form 502 instruction book
                                            prints 2, because it restates
                                            § 58.1-408 A but DROPS the words
                                            "plus one" -> LESS tax
    The instruction book is the DEFECTIVE source. Do NOT reconcile to it.

    Returns None when no factor has a denominator — never a substituted value.
    """
    w = _yk(VA_APPORT_WEIGHTS, year)

    def _f(pair):
        if pair is None:
            return None
        num, den = pair
        if not den:
            return None
        return float(num) / float(den)

    f_prop, f_pay, f_sales = _f(prop), _f(pay), _f(sales)
    divisor = 0
    total = 0.0
    for factor, key in ((f_prop, "property"), (f_pay, "payroll"), (f_sales, "sales")):
        if factor is not None:
            divisor += w[key]
            total += factor * w[key]
    if divisor == 0:
        return None
    return round(total / divisor, _yk(VA_APPORT_DECIMALS, year))


def _va500_line6_sl_bad_debt(line5, method: str, year: int = FORM_TAX_YEAR):
    """Line 6 — Savings and Loan Association's Bad Debt Deduction (§ 58.1-403).

    ⚠ ONLY the percentage-of-income method uses this line: instr. p.11 gives
    Line 5 x 40%. The percentage-of-loans and experience methods do NOT touch
    Line 6 at all — they route through ADDITION CODE 13 on Schedule 500ADJ
    instead. Returning a figure here for those methods would double-count.
    """
    if method != "percentage_of_income":
        return 0.0
    return round(float(line5) * float(_yk(VA_SL_BAD_DEBT_PCT, year)), 2)


def _va500_line11(line9, line10, minimum_tax_override=None):
    """Line 11 — Adjusted corporate tax. ⚠⚠ AN OVERWRITE TARGET, NOT A DERIVED LINE.

    The printed arithmetic is "subtract Line 10 from Line 9". But four
    SCC-certified regimes REPLACE it outright:

        Sch. 500EL: "Enter this amount on Line 11 of Form 500, and REPLACE the
                     amount computed on Form 500."
        Form 500HS: "...enter this amount on Line 11 of Form 500 and enter $0 on
                     Line 10 of Form 500."

    ⚠ A DERIVED-ONLY LINE 11 SILENTLY DISCARDS THE MINIMUM TAX and under-taxes a
    certified filer on a clean-looking return. That is why this function takes an
    override at all, even though v1 RED-defers the four regimes (D-21/V6): the
    PATH must exist now so that enabling a regime later is a data change, not a
    re-architecture.

    Note the Form 500HS behaviour: when the minimum tax wins, Line 10 is ALSO
    zeroed. The caller owns that, because it is a change to a different line.
    """
    if minimum_tax_override is not None:
        return round(float(minimum_tax_override), 2)
    return round(max(0.0, float(line9) - float(line10 or 0)), 2)


AUTHORITY_TOPICS: list[tuple[str, str]] = [
    # ⚠ Keep under 255 — varchar(255), and the guard below enforces it.
    ("va_corp_tax", "Virginia Form 500 C-corporation: the flat 6% tax (Va. Code § 58.1-400), the "
     "Schedule 500ADJ modifications, the § 58.1-408 A weight-sum apportionment divisor, and the four "
     "SCC-certified minimum-tax regimes that OVERWRITE Line 11."),
]

# ⚠ Verified to RESOLVE in prod before seeding. A code that does not resolve is a
# DANGLING REFERENCE — campaign D-25/O4, and D-29 where I made that mistake myself.
#
# ⚠⚠ `VA_CODE_58_1_408` IS OWNED BY `load_va_pte.py`, which is SEEDED AND LIVE, and
# is cited by two live rules (R-VA-502AB on VA_502, R-VAP-502AB on VA_502PTET).
# An earlier version of this loader DECLARED it, so `update_or_create` would have
# silently rewritten its title, citation, trust_score and `source_rank` - the last
# from `controlling` down to `primary_official`. That is not D-29's duplication;
# it is TWO WRITERS OF ONE ROW, the hazard the 2026-07-05 delta audit flagged and
# D-8 exists to prevent. Reference it; never re-declare another loader's source.
EXISTING_SOURCES_TO_REFERENCE: list[str] = [
    "VA_CODE_58_1_408",
]

# Verbatim excerpts this pass derived, attached to the source its OWNER already
# maintains rather than lost or written over. Idempotent on excerpt_label.
EXCERPTS_FOR_EXISTING: list[tuple[str, dict]] = [
    ("VA_CODE_58_1_408", {
        "excerpt_label": "§ 58.1-408 A stated outright (D-18/G1) + the § 58.1-408 B numerator reduction",
        "excerpt_text": (
            "'...shall be apportioned to the Commonwealth by multiplying such income by a fraction, the "
            "numerator of which is the property factor plus the payroll factor, plus twice the sales "
            "factor, and the denominator of which is four; however, where the sales factor does not "
            "exist, the denominator of the fraction shall be the number of existing factors and where the "
            "sales factor exists but the payroll factor or the property factor does not exist, the "
            "denominator of the fraction shall be the number of existing factors plus one.' History ends "
            "2018, cc. 801, 802, 807 - no 2026 amendment. ⚠ § 58.1-408 B additionally grants an ELIGIBLE "
            "COMPANY under § 58.1-405.1 a NUMERATOR REDUCTION, running 'for the taxable year in which it "
            "first becomes eligible and for the six subsequent, consecutive taxable years' - with NO line, "
            "NO checkbox and NO instruction anywhere on any corporate form."
        ),
        "summary_text": "The 4/3/3/2 divisor is transcribed, not interpreted (D-18/G1). § 58.1-408 B is a "
                        "live money-moving numerator reduction with zero form support (D-21/V5).",
        "is_key_excerpt": True,
    }),
]

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "VA_2025_FORM_500", "source_type": "state_form", "source_rank": "primary_official",
        "jurisdiction_code": "VA", "title": "2025 Virginia Form 500 — Corporation Income Tax Return",
        "citation": "Virginia Form 500 (2025)", "issuer": "Virginia Department of Taxation",
        "official_url": "https://www.tax.virginia.gov/forms/search?search=500",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.6,
        "topics": ["va_corp_tax"],
        "excerpts": [
            {
                "excerpt_label": "The Line 1-9 spine and the 6% rate (face, verbatim)",
                "excerpt_text": (
                    "1 'Federal taxable income (from enclosed federal return)'; 2 'Total additions from "
                    "Schedule 500ADJ, Section A, Line 7'; 3 'Total (add Lines 1 and 2)'; 4 'Total "
                    "subtractions from Schedule 500ADJ, Section B, Line 10'; 5 'Balance (subtract Line 4 from "
                    "Line 3)'; 6 'Savings and Loan Association's Bad Debt Deduction (see instructions)'; 7 "
                    "'Virginia taxable income (subtract Line 6 from Line 5)'; 8 'Apportionable Income "
                    "(Schedule 500A Filers) - Complete Lines 8(a) through 8(d).' with 8(a) 'Income subject to "
                    "Virginia tax from Schedule 500A, Section B, Line 3(j)', 8(b) 'Apportionment factor "
                    "percentage from Schedule 500A, Section B, Line 1 or Line 2(f)', 8(c) 'Nonapportionable "
                    "investment function income', 8(d) 'Nonapportionable investment function loss'; and 9 "
                    "'Income tax [6% of Line 7 or 6% of Line 8(a)]'. Instructions p.10 on Line 1: 'Enter "
                    "taxable income after net operating loss deductions and special deductions for dividends "
                    "as it appears on the federal income tax return... Line 1 may not be less than zero except "
                    "to report a net operating loss in the current year.' Line 7: 'Corporations other than "
                    "multistate corporations, skip to Line 9.'"
                ),
                "summary_text": "Form 500: L1 federal TI (after NOL and special deductions) +/- 500ADJ = L5; "
                                "less L6 S&L bad debt = L7; multistate route via L8(a); L9 = 6%.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "⚠ The four minimum-tax boxes that OVERWRITE Line 11 (verbatim)",
                "excerpt_text": (
                    "Page 1 carries four minimum-tax entry boxes: 'Corporate Telecommunications Company - "
                    "Enter amount from Form 500T, Line 7:'; 'Noncorporate Telecommunications Company - Check "
                    "box and enter amount from Form 500T, Line 10:'; 'Electric Supplier Company - Enter amount "
                    "from Sch. 500EL, Line 7 or 14:'; 'Home Service Contract Provider - Enter amount from Form "
                    "500HS, Line 10:'. Schedule 500EL directs: 'Enter this amount on Line 11 of Form 500, and "
                    "REPLACE the amount computed on Form 500.' Form 500HS: 'if the amount on Line 10 is equal "
                    "to minimum tax, enter this amount on Line 11 of Form 500 and enter $0 on Line 10 of Form "
                    "500.' Line 14 carve-out (instr. p.12): 'If filing a combined or consolidated return with "
                    "a home service contract provider or telecommunications company, do not enter refundable "
                    "credits included on Forms 500HS or 500T.'"
                ),
                "summary_text": "⚠ Line 11 is an OVERWRITE target. 500EL says REPLACE the computed amount; "
                                "500HS additionally zeroes Line 10. A derived-only Line 11 silently discards "
                                "the minimum tax.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "VA_CODE_58_1_442", "source_type": "state_statute", "source_rank": "primary_official",
        "jurisdiction_code": "VA", "title": "Va. Code § 58.1-442 — separate, combined and consolidated returns",
        "citation": "Va. Code § 58.1-442 B and C", "issuer": "Virginia General Assembly",
        "official_url": "https://law.lis.virginia.gov/vacode/title58.1/chapter3/section58.1-442/",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["va_corp_tax"],
        "excerpts": [{
            "excerpt_label": "⚠ W11 — the STATUTE is broader than the instruction book",
            "excerpt_text": (
                "§ 58.1-442 C grants the 12-year change 'from separate OR COMBINED to consolidated'. ⚠ The "
                "Form 500 instruction book (p.7) prints the narrower 'from separate to consolidated', omitting "
                "exactly the population that the now-expired § 58.1-442 D used to serve. History of "
                "§ 58.1-442: ...1990, c. 619; 2003, c. 166; 2022, cc. 274, 416, 417; 2023, cc. 520, 521. "
                "(⚠ An earlier reading of this brief printed '2003, c. 376' - that chapter belongs to "
                "§ 58.1-441's history, not this one.) Instructions p.4 confirm: 'Consolidated and combined "
                "returns are supported.'"
            ),
            "summary_text": "⚠ Build the combined->consolidated change diagnostic to the STATUTE, not the "
                            "instruction book, which is narrower and drops a whole population.",
            "is_key_excerpt": True,
        }],
    },
]

AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    ("VA_2025_FORM_500", "VA_500", "primary_form"),
    ("VA_CODE_58_1_408", "VA_500", "statute"),
    ("VA_CODE_58_1_442", "VA_500", "statute"),
]


F_FACTS: list[dict] = [
    {"fact_key": "federal_taxable_income", "label": "L1 Federal taxable income (federal 1120 Line 30)",
     "data_type": "decimal", "required": False, "sort_order": 1,
     "notes": "⚠ AFTER federal NOL deductions AND special deductions for dividends - not before. "
              "Instr. p.10: 'Line 1 may not be less than zero except to report a net operating loss in the "
              "current year.' So a negative IS permitted, but only in that one case."},
    {"fact_key": "adj_section_a_additions", "label": "L2 Total additions (Schedule 500ADJ, Section A, Line 7)",
     "data_type": "decimal", "required": False, "sort_order": 2,
     "notes": "⚠ G4/crosswalk: Virginia's CORPORATE and PTE modules use DIFFERENT code numbers for the same "
              "concepts, and SEVEN codes exist on both with DIFFERENT meanings (additions 14, 16, 21; "
              "subtractions 50, 56, 57, 58). Never port a code number between the modules."},
    {"fact_key": "adj_section_b_subtractions", "label": "L4 Total subtractions (Schedule 500ADJ, Section B, Line 10)",
     "data_type": "decimal", "required": False, "sort_order": 3},
    {"fact_key": "sl_bad_debt_method", "label": "Savings & Loan bad-debt method (§ 58.1-403)",
     "data_type": "string", "required": False, "sort_order": 4,
     "notes": "percentage_of_income | percentage_of_loans | experience. ⚠ ONLY percentage_of_income uses "
              "Line 6 (= Line 5 x 40%). The other two route through ADDITION CODE 13 on Schedule 500ADJ - "
              "entering a Line 6 figure for them would double-count."},
    {"fact_key": "is_multistate", "label": "Multistate corporation (Schedule 500A filer)?",
     "data_type": "boolean", "required": False, "sort_order": 5,
     "notes": "Face: 'Corporations other than multistate corporations, skip to Line 9.' A non-multistate "
              "filer takes L7 straight to the 6%."},
    {"fact_key": "apport_property_va", "label": "Sch. 500A property factor - Virginia numerator",
     "data_type": "decimal", "required": False, "sort_order": 6},
    {"fact_key": "apport_property_total", "label": "Sch. 500A property factor - everywhere denominator",
     "data_type": "decimal", "required": False, "sort_order": 7},
    {"fact_key": "apport_payroll_va", "label": "Sch. 500A payroll factor - Virginia numerator",
     "data_type": "decimal", "required": False, "sort_order": 8},
    {"fact_key": "apport_payroll_total", "label": "Sch. 500A payroll factor - everywhere denominator",
     "data_type": "decimal", "required": False, "sort_order": 9},
    {"fact_key": "apport_sales_va", "label": "Sch. 500A sales factor - Virginia numerator (DOUBLE weighted)",
     "data_type": "decimal", "required": False, "sort_order": 10},
    {"fact_key": "apport_sales_total", "label": "Sch. 500A sales factor - everywhere denominator",
     "data_type": "decimal", "required": False, "sort_order": 11},
    {"fact_key": "nonapport_invest_income", "label": "L8(c) Nonapportionable investment function INCOME",
     "data_type": "decimal", "required": False, "sort_order": 12,
     "notes": "⚠ Allied-Signal constitutional relief. Carries a 'clear and cogent evidence' burden, a "
              "mandatory enclosed statement, and a ONE-WAY RATCHET: once a subtraction is claimed for an "
              "asset, the addition is REQUIRED for any subsequent losses from that asset."},
    {"fact_key": "nonapport_invest_loss", "label": "L8(d) Nonapportionable investment function LOSS",
     "data_type": "decimal", "required": False, "sort_order": 13,
     "notes": "The other half of the one-way ratchet - see L8(c)."},
    {"fact_key": "filing_status", "label": "Filing status - separate / combined / consolidated",
     "data_type": "string", "required": False, "sort_order": 14,
     "notes": "⚠ W7: a PREPARER ASSERTION, never derived. ⚠ V2: v1 supports SEPARATE only and refuses the "
              "other two behind a hard gate - Virginia's election is effectively permanent once made."},
    {"fact_key": "eligible_company_408b", "label": "§ 58.1-408 B eligible company (§ 58.1-405.1)?",
     "data_type": "boolean", "required": False, "sort_order": 15,
     "notes": "⚠ V5 RED-DEFER. Property/payroll acquired 1/1/2018-1/1/2025 in a qualified locality plus ALL "
              "Virginia sales, running the first eligible year plus SIX consecutive years - so a company "
              "first eligible 2019-2024 is STILL INSIDE its window for TY2025. No line, no checkbox, no "
              "instruction anywhere."},
    {"fact_key": "minimum_tax_regime", "label": "SCC-certified minimum-tax regime, if any",
     "data_type": "string", "required": False, "sort_order": 16,
     "notes": "⚠⚠ V6. telecom_500T | noncorp_telecom_500T | electric_500EL | hsc_provider_500HS. All four "
              "RED-deferred in v1, but they OVERWRITE Line 11 - the path must exist."},
    {"fact_key": "minimum_tax_amount", "label": "Minimum tax from Form 500T / Sch. 500EL / Form 500HS",
     "data_type": "decimal", "required": False, "sort_order": 17,
     "notes": "⚠ Sch. 500EL carries NO RATE at all - the SCC certifies the number. 500T is 0.5% of certified "
              "gross receipts; 500HS is 2.25% of collected provider's fees."},
    {"fact_key": "nonrefundable_credits", "label": "L10 Nonrefundable credits (Sch. 500CR, Sec. 2, Pt 1, L1B)",
     "data_type": "decimal", "required": False, "sort_order": 18},
    {"fact_key": "estimated_payments", "label": "L12 2025 estimated payments incl. 2024 overpayment credit",
     "data_type": "decimal", "required": False, "sort_order": 19},
    {"fact_key": "extension_payment", "label": "L13 Extension payment", "data_type": "decimal",
     "required": False, "sort_order": 20},
    {"fact_key": "refundable_credits", "label": "L14 Refundable credits (Sch. 500CR, Sec. 4, Pt 1, L1A)",
     "data_type": "decimal", "required": False, "sort_order": 21,
     "notes": "⚠ Carve-out, instr. p.12: on a combined or consolidated return with a home service contract "
              "provider or telecommunications company, do NOT enter refundable credits already included on "
              "Forms 500HS or 500T. A real double-count guard."},
    {"fact_key": "pte_withholding", "label": "L15 Pass-through entity withholding (Sch. 500ADJ, Section D)",
     "data_type": "decimal", "required": False, "sort_order": 22},
    {"fact_key": "penalty", "label": "L18 Penalty", "data_type": "decimal", "required": False, "sort_order": 23},
    {"fact_key": "interest", "label": "L19 Interest", "data_type": "decimal", "required": False, "sort_order": 24},
    {"fact_key": "form_500c_charge", "label": "L20 Additional charge from Form 500C, Line 17",
     "data_type": "decimal", "required": False, "sort_order": 25},
    {"fact_key": "credit_to_next_year", "label": "L23 Amount credited to 2026 estimated tax",
     "data_type": "decimal", "required": False, "sort_order": 26},
]

F_RULES: list[dict] = [
    {"rule_id": "R-VA500-L5", "title": "L3/L5 - federal TI plus 500ADJ additions less subtractions",
     "rule_type": "calculation",
     "formula": "L3 = federal_taxable_income + adj_section_a_additions ; L5 = L3 - adj_section_b_subtractions",
     "inputs": ["federal_taxable_income", "adj_section_a_additions", "adj_section_b_subtractions"],
     "outputs": ["L3", "L5"], "sort_order": 1,
     "description": "⚠ L1 is federal taxable income AFTER federal NOL and special deductions - the FINAL 2025 "
                    "Form 1120 Line 30, not line 28. Instr. p.10: 'Line 1 may not be less than zero except to "
                    "report a net operating loss in the current year', so a negative is permitted in exactly "
                    "that case and nowhere else."},
    {"rule_id": "R-VA500-L6", "title": "L6 - Savings & Loan bad debt, percentage-of-income ONLY",
     "rule_type": "calculation",
     "formula": "L6 = round(L5 * 0.40, 2) if sl_bad_debt_method == 'percentage_of_income' else 0",
     "inputs": ["sl_bad_debt_method"], "outputs": ["L6"], "sort_order": 2,
     "description": "§ 58.1-403. ⚠ ONLY the percentage-of-income method uses this line (instr. p.11: Line 5 x "
                    "40%). The percentage-of-loans and experience methods do NOT touch Line 6 - they route "
                    "through ADDITION CODE 13 on Schedule 500ADJ. Putting a figure here for those methods "
                    "double-counts the deduction."},
    {"rule_id": "R-VA500-L7", "title": "L7 - Virginia taxable income", "rule_type": "calculation",
     "formula": "L7 = L5 - L6",
     "inputs": [], "outputs": ["L7"], "sort_order": 3,
     "description": "Face: 'This is your Virginia taxable income if the entire business of the corporation is "
                    "transacted or conducted within Virginia. Corporations other than multistate "
                    "corporations, skip to Line 9.'"},
    {"rule_id": "R-VA500-APPORT", "title": "Sch. 500A - the § 58.1-408 A weight-sum divisor",
     "rule_type": "calculation",
     "formula": ("divisor = sum of weights of factors that EXIST (property 1, payroll 1, sales 2) ; "
                 "pct = round(weighted total / divisor, 6)"),
     "inputs": ["apport_property_va", "apport_property_total", "apport_payroll_va", "apport_payroll_total",
                "apport_sales_va", "apport_sales_total"], "outputs": ["L8b"], "sort_order": 4,
     "description": "⚠ D-18/G1 - a TRANSCRIPTION from Va. Code § 58.1-408 A, not an interpretation. The "
                    "statute states both branches outright: denominator four; 'the number of existing "
                    "factors' where the sales factor does not exist; 'the number of existing factors PLUS "
                    "ONE' where sales exists but payroll or property does not. So 4/3/3/2. ⚠ Building to "
                    "statute knowingly diverges from printed FINAL sources BOTH WAYS: the 500A/502A faces, "
                    "the 500A instructions and 500AC do not yield 2 when sales is missing, and the Form 502 "
                    "instruction book prints 2 where the statute requires 3 because it DROPS the words 'plus "
                    "one'. The instruction book is the defective source - do NOT reconcile to it. A missing "
                    "denominator yields NO factor, never a substitute."},
    {"rule_id": "R-VA500-L9", "title": "L9 - income tax at 6%", "rule_type": "calculation",
     "formula": "L9 = round(max(0, (L8a if is_multistate else L7)) * 0.06, 2)",
     "inputs": ["is_multistate"], "outputs": ["L9"], "sort_order": 5,
     "description": "Face: 'Income tax [6% of Line 7 or 6% of Line 8(a)]' - Va. Code § 58.1-400. A "
                    "non-multistate filer uses Line 7; a Schedule 500A filer uses Line 8(a). ⚠ Instr. p.11: "
                    "'Multistate corporations with no Virginia income must enter zeroes in 8(a) and 8(b)' - "
                    "zeroes, not blanks."},
    {"rule_id": "R-VA500-L11", "title": "L11 - Adjusted corporate tax. ⚠⚠ AN OVERWRITE TARGET",
     "rule_type": "calculation",
     "formula": "L11 = minimum_tax_amount if a certified regime applies else max(0, L9 - L10)",
     "inputs": ["nonrefundable_credits", "minimum_tax_regime", "minimum_tax_amount"],
     "outputs": ["L11"], "sort_order": 6,
     "description": "⚠⚠ THE MOST DANGEROUS LINE ON THE FORM. The printed arithmetic is 'subtract Line 10 from "
                    "Line 9', but four SCC-certified regimes REPLACE it. Schedule 500EL, verbatim: 'Enter "
                    "this amount on Line 11 of Form 500, and REPLACE the amount computed on Form 500.' Form "
                    "500HS: 'if the amount on Line 10 is equal to minimum tax, enter this amount on Line 11 "
                    "of Form 500 and enter $0 on Line 10 of Form 500.' AN ENGINE THAT MODELS LINE 11 AS "
                    "DERIVED-ONLY SILENTLY DISCARDS THE MINIMUM TAX and under-taxes a certified filer on a "
                    "return that looks perfectly clean. The four regimes are RED-deferred in v1 (D-21/V6) but "
                    "THE OVERWRITE PATH EXISTS NOW, so enabling one later is a data change, not a "
                    "re-architecture. ⚠ When 500HS wins, Line 10 is ALSO zeroed - a change to a different "
                    "line, owned by the caller."},
    {"rule_id": "R-VA500-L16", "title": "L16 - total payments and credits", "rule_type": "calculation",
     "formula": "L16 = estimated_payments + extension_payment + refundable_credits + pte_withholding",
     "inputs": ["estimated_payments", "extension_payment", "refundable_credits", "pte_withholding"],
     "outputs": ["L16"], "sort_order": 7,
     "description": "Face: 'add Lines 12 through 15'. ⚠ Line 14 carve-out (instr. p.12): on a combined or "
                    "consolidated return with a home service contract provider or telecommunications "
                    "company, do NOT enter refundable credits already included on Forms 500HS or 500T - a "
                    "real double-count guard."},
    {"rule_id": "R-VA500-SETTLE", "title": "L17/L21/L22/L24 - settlement", "rule_type": "calculation",
     "formula": ("L17 = max(0, L11 - L16) ; L21 = L17 + penalty + interest + form_500c_charge ; "
                 "L22 = max(0, L16 - L11) ; L24 = L22 - credit_to_next_year"),
     "inputs": ["penalty", "interest", "form_500c_charge", "credit_to_next_year"],
     "outputs": ["L17", "L21", "L22", "L24"], "sort_order": 8,
     "description": "L17 'if Line 11 is greater than Line 16, subtract Line 16 from Line 11'; L21 'add Lines "
                    "17 through 20'; L22 'if Line 16 is greater than Line 11, subtract Line 11 from Line 16'; "
                    "L24 'subtract Line 23 from Line 22'. L17 and L22 are mutually exclusive by construction. "
                    "⚠ Note the settlement runs off LINE 11, which may have been OVERWRITTEN by a minimum-tax "
                    "regime - so the overwrite propagates all the way to the refund."},
]

F_RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R-VA500-L5", "VA_2025_FORM_500", "primary", "L1-L5 face labels + the L1 instruction"),
    ("R-VA500-L6", "VA_2025_FORM_500", "primary", "L6 and the percentage-of-income method"),
    ("R-VA500-L7", "VA_2025_FORM_500", "primary", "L7 and the multistate skip"),
    ("R-VA500-APPORT", "VA_CODE_58_1_408", "primary", "§ 58.1-408 A - the divisor, stated outright"),
    ("R-VA500-APPORT", "VA_2025_FORM_500", "secondary", "Sch. 500A Section B, L8(b)"),
    ("R-VA500-L9", "VA_2025_FORM_500", "primary", "L9 '6% of Line 7 or 6% of Line 8(a)'"),
    ("R-VA500-L11", "VA_2025_FORM_500", "primary", "the four minimum-tax boxes and the REPLACE instruction"),
    ("R-VA500-L16", "VA_2025_FORM_500", "primary", "L12-L16 and the L14 carve-out"),
    ("R-VA500-SETTLE", "VA_2025_FORM_500", "primary", "L17-L24 face labels"),
]

F_LINES: list[dict] = [
    {"line_number": "VA500-3", "description": "L3 Total (Lines 1 + 2)", "line_type": "subtotal",
     "source_rules": ["R-VA500-L5"], "sort_order": 1},
    {"line_number": "VA500-5", "description": "L5 Balance (Line 3 - Line 4)", "line_type": "subtotal",
     "source_rules": ["R-VA500-L5"], "sort_order": 2},
    {"line_number": "VA500-6", "description": "L6 Savings & Loan bad debt deduction (pct-of-income only)",
     "line_type": "calculated", "source_rules": ["R-VA500-L6"], "sort_order": 3},
    {"line_number": "VA500-7", "description": "L7 Virginia taxable income", "line_type": "subtotal",
     "source_rules": ["R-VA500-L7"], "sort_order": 4},
    {"line_number": "VA500-8b", "description": "L8(b) Apportionment factor percentage (Sch. 500A)",
     "line_type": "calculated", "source_rules": ["R-VA500-APPORT"], "sort_order": 5},
    {"line_number": "VA500-8a", "description": "L8(a) Income subject to Virginia tax (Sch. 500A B L3(j))",
     "line_type": "calculated", "source_rules": ["R-VA500-APPORT"], "sort_order": 6},
    {"line_number": "VA500-9", "description": "L9 Income tax (6%)", "line_type": "calculated",
     "source_rules": ["R-VA500-L9"], "sort_order": 7},
    {"line_number": "VA500-11", "description": "L11 Adjusted corporate tax - OVERWRITE TARGET",
     "line_type": "calculated", "source_rules": ["R-VA500-L11"], "sort_order": 8},
    {"line_number": "VA500-16", "description": "L16 Total payments and credits", "line_type": "subtotal",
     "source_rules": ["R-VA500-L16"], "sort_order": 9},
    {"line_number": "VA500-17", "description": "L17 Tax owed", "line_type": "calculated",
     "source_rules": ["R-VA500-SETTLE"], "sort_order": 10},
    {"line_number": "VA500-21", "description": "L21 Total due", "line_type": "calculated",
     "source_rules": ["R-VA500-SETTLE"], "sort_order": 11},
    {"line_number": "VA500-22", "description": "L22 Overpayment", "line_type": "calculated",
     "source_rules": ["R-VA500-SETTLE"], "sort_order": 12},
    {"line_number": "VA500-24", "description": "L24 Amount to be refunded", "line_type": "calculated",
     "source_rules": ["R-VA500-SETTLE"], "sort_order": 13},
]

F_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_VA500_FILING_STATUS_GATE", "severity": "error",
     "title": "⚠ Combined and consolidated Virginia returns are not supported in v1",
     "condition": "filing_status in ('combined', 'consolidated')",
     "message": "This version computes SEPARATE Virginia corporate returns only. Combined and consolidated "
                "returns are refused rather than computed. Virginia's filing-status election is effectively "
                "PERMANENT once made (Va. Code 58.1-442), so an incorrect consolidated computation is "
                "expensive and hard to unwind for the client. Prepare a combined or consolidated return "
                "outside this software. NOTE the change rule follows the STATUTE, not the instruction book: "
                "Sec. 58.1-442 C grants the 12-year change 'from separate OR COMBINED to consolidated', while "
                "the Form 500 instruction book prints the narrower 'from separate to consolidated' and omits "
                "exactly the population the expired Sec. 58.1-442 D used to serve.",
     "notes": "V2 + W11 (campaign D-21). The filing status itself is a PREPARER ASSERTION, never derived (W7)."},
    {"diagnostic_id": "D_VA500_MIN_TAX_DEFERRED", "severity": "error",
     "title": "⚠⚠ SCC-certified minimum-tax regimes are not computed in v1 - and Line 11 is OVERWRITTEN",
     "condition": "minimum_tax_regime is not None",
     "message": "This return is subject to one of Virginia's four SCC-certified minimum-tax regimes, which "
                "this version does not compute: telecommunications company (Form 500T, 0.5% of certified "
                "gross receipts), noncorporate telecommunications company (Form 500T Part III, same 0.5%), "
                "electric supplier (Schedule 500EL - the SCC certifies the amount and NO RATE appears on the "
                "form), or home service contract provider (Form 500HS, 2.25% of collected provider's fees). "
                "⚠ These do NOT add to the tax - they REPLACE Line 11. Schedule 500EL states: 'Enter this "
                "amount on Line 11 of Form 500, and replace the amount computed on Form 500.' Form 500HS "
                "additionally directs entering $0 on Line 10. Compute the minimum tax on its own form and "
                "enter the result; the software will carry it through Line 11 to the settlement.",
     "notes": "⚠ V6. The regimes are deferred but THE OVERWRITE PATH EXISTS - a derived-only Line 11 would "
              "silently discard the minimum tax and under-tax a certified filer."},
    {"diagnostic_id": "D_VA500_408B_DEFERRED", "severity": "error",
     "title": "⚠ § 58.1-408 B eligible-company numerator reduction is not computed - prepare it manually",
     "condition": "eligible_company_408b == True",
     "message": "Va. Code Sec. 58.1-408 B allows an 'eligible company' under Sec. 58.1-405.1 to REDUCE its "
                "apportionment NUMERATOR - property and payroll acquired between 1/1/2018 and 1/1/2025 in a "
                "qualified locality, plus all Virginia sales. It runs 'for the taxable year in which it first "
                "becomes eligible and for the six subsequent, consecutive taxable years', so a company first "
                "eligible in 2019-2024 is STILL INSIDE its window for TY2025. ⚠ Virginia provides NO line, NO "
                "checkbox and NO instruction for it on any corporate form - the Form 500 book references "
                "Sec. 58.1-405.1 exactly once, unexplained. Eligibility cannot be determined from return "
                "data. Prepare the reduction manually and enter the resulting apportionment factor.",
     "notes": "V5. Live, money-moving, zero form support. Our own brief omitted it until the verification "
              "pass added it - the clearest case of that pass earning its cost on an OMISSION."},
    {"diagnostic_id": "D_VA500_NO_DENOMINATOR", "severity": "error",
     "title": "⚠ No apportionment factor has a denominator - none computed, none substituted",
     "condition": "is_multistate == True and every factor denominator is zero or missing",
     "message": "No Schedule 500A factor has a denominator, so no apportionment percentage can be computed. "
                "This software will NOT substitute a factor and will NOT default to 100%. Supply the "
                "Schedule 500A figures, or use an alternative apportionment method with the Department's "
                "permission.",
     "notes": "Same no-auto-substitute discipline as Maryland D-5 and Oregon."},
    {"diagnostic_id": "D_VA500_DIVISOR_DIVERGES", "severity": "info",
     "title": "A factor is missing - the divisor follows § 58.1-408 A, which diverges from the printed forms",
     "condition": "is_multistate == True and at least one factor has no denominator",
     "message": "One or more apportionment factors have no denominator, so the divisor is the SUM OF THE "
                "WEIGHTS of the factors that do exist (property 1, payroll 1, sales 2): all three present = "
                "4, sales missing = 2, property or payroll missing = 3. ⚠ This is transcribed from Va. Code "
                "Sec. 58.1-408 A, which states both branches outright, and it KNOWINGLY DIVERGES FROM THE "
                "PRINTED FORMS IN BOTH DIRECTIONS. Where the sales factor is missing the statute gives 2 "
                "while the 500A face, 502A face, 500A instructions and 500AC yield otherwise (more tax). "
                "Where payroll or property is missing the statute gives 3 while the Form 502 instruction book "
                "prints 2, because the book restates the statute but DROPS the words 'plus one' (less tax). "
                "The instruction book is the defective source. Do not reconcile this return to it.",
     "notes": "⚠ D-18/G1, ratified by Ken. Recorded on the return so a preparer questioned by the Department "
              "has the citation to hand."},
    {"diagnostic_id": "D_VA500_DEPRECIATION_ENTRY", "severity": "warning",
     "title": "Virginia depreciation is direct-entry in v1 - and Virginia publishes no § 179 figure",
     "condition": "adj_section_a_additions > 0 or adj_section_b_subtractions > 0",
     "message": "Virginia depreciation modifications are entered directly on Schedule 500ADJ in this version; "
                "the parallel Virginia depreciation book arrives in a later release. ⚠ Virginia publishes NO "
                "Section 179 dollar figure of its own. Do not expect this software to display one, and do not "
                "carry a figure across from another state or from a federal worksheet - the amounts sometimes "
                "quoted in this area are DERIVED, not published by Virginia, and this software deliberately "
                "encodes none.",
     "notes": "⚠⚠ V3. The derived $1,250,000 / $3,130,000 / $31,300 are NEVER encoded as Virginia constants. "
              "The harness asserts their absence."},
    {"diagnostic_id": "D_VA500_CONFORMITY_BUCKET", "severity": "info",
     "title": "The residual conformity bucket shares one dollar box with the bonus true-up",
     "condition": "adj_section_a_additions > 0 or adj_section_b_subtractions > 0",
     "message": "Virginia's residual conformity adjustments route to Schedule 500ADJ Section A line 2 and "
                "Section B line 2. ⚠ That bucket SHARES A SINGLE DOLLAR BOX with the bonus-depreciation "
                "disposed-asset true-up, so two conceptually distinct amounts land on one line. Keep the "
                "supporting detail: the return cannot show which component is which, and a later enquiry "
                "will ask.",
     "notes": "V4, the same ruling shape as the PTE side's W2."},
    {"diagnostic_id": "D_VA500_ALLIED_SIGNAL", "severity": "warning",
     "title": "Nonapportionable investment function income carries a one-way ratchet",
     "condition": "nonapport_invest_income > 0 or nonapport_invest_loss > 0",
     "message": "Lines 8(c) and 8(d) are the Allied-Signal constitutional-relief lines. They carry a 'clear "
                "and cogent evidence' burden and require an enclosed statement. ⚠ THE RATCHET IS ONE-WAY: if "
                "a subtraction for nonapportionable investment function income has previously been claimed "
                "for any investment asset, the ADDITION IS REQUIRED for any subsequent losses generated by "
                "those assets. Claiming the benefit in a good year commits the taxpayer to the addition in a "
                "bad one. Cite: Form 500 instructions pp.11-12; Tax Bulletin 93-4 (4/6/93).",
     "notes": "Same doctrine as the PTE side's Schedule 502A Lines 3(b)/3(d), different line numbers - G4."},
    {"diagnostic_id": "D_VA500_SL_METHOD", "severity": "info",
     "title": "Only the percentage-of-income S&L method uses Line 6",
     "condition": "sl_bad_debt_method in ('percentage_of_loans', 'experience')",
     "message": "The Savings and Loan Association bad-debt deduction reaches Form 500 Line 6 ONLY under the "
                "percentage-of-income method (Line 5 x 40%). Under the percentage-of-loans or experience "
                "methods the adjustment is made instead through ADDITION CODE 13 on Schedule 500ADJ, and Line "
                "6 stays empty. Entering an amount on both would double-count the deduction.",
     "notes": "Sec. 58.1-403; instr. p.11."},
    {"diagnostic_id": "D_VA500_CODE_CROSSWALK", "severity": "warning",
     "title": "⚠ Never carry a Schedule 500ADJ code number across from the PTE module",
     "condition": "adj_section_a_additions > 0 or adj_section_b_subtractions > 0",
     "message": "Virginia's corporate Schedule 500ADJ and pass-through Schedule 502ADJ use DIFFERENT code "
                "numbers for the same concepts. ⚠ SEVEN code numbers exist on BOTH forms with DIFFERENT "
                "MEANINGS - additions 14, 16 and 21, and subtractions 50, 56, 57 and 58. A code carried "
                "across does not produce an error: it lands on a real but WRONG code. The worst pair is "
                "addition 21 and subtraction 58, each carrying 'partnership-level federal adjustment' on one "
                "form and something unrelated on the other. Always read the code off the CORPORATE "
                "instructions.",
     "notes": "G4 at the code-table level. Only codes 10, 13 and 99 (Other, both directions) genuinely port."},
]

F_SCENARIOS: list[dict] = [
    {"scenario_name": "VA500-A - wholly-Virginia corporation at 6%", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"federal_taxable_income": 1000000, "is_multistate": False},
     "expected_outputs": {"L3": 1000000, "L5": 1000000, "L7": 1000000, "L9": 60000, "L11": 60000},
     "notes": "The base case. Non-multistate, so Lines 8(a)-(d) are skipped and L9 = 6% of L7."},
    {"scenario_name": "VA500-B - all three apportionment factors present (divisor 4)", "scenario_type": "normal",
     "sort_order": 2,
     "inputs": {"federal_taxable_income": 4000000, "is_multistate": True,
                "apport_property_va": 200000, "apport_property_total": 1000000,
                "apport_payroll_va": 300000, "apport_payroll_total": 1000000,
                "apport_sales_va": 400000, "apport_sales_total": 2000000},
     "expected_outputs": {"L8b": 0.225},
     "notes": "(0.20 + 0.30 + 2 x 0.20) / 4 = 0.225. Sales is double-weighted in BOTH numerator and divisor."},
    {"scenario_name": "VA500-C - sales factor missing, divisor drops to 2 (MORE tax than print)",
     "scenario_type": "edge", "sort_order": 3,
     "inputs": {"is_multistate": True, "apport_property_va": 200000, "apport_property_total": 1000000,
                "apport_payroll_va": 300000, "apport_payroll_total": 1000000,
                "apport_sales_va": 0, "apport_sales_total": 0},
     "expected_outputs": {"L8b": 0.25},
     "notes": "⚠ D-18/G1. (0.20 + 0.30) / 2 = 0.25 per Sec. 58.1-408 A. The 500A face, 502A face, 500A "
              "instructions and 500AC all yield otherwise - the statute produces MORE Virginia tax here, and "
              "Ken ruled build-to-statute."},
    {"scenario_name": "VA500-D - payroll missing, divisor is 3 (the book says 2 - LESS tax)",
     "scenario_type": "edge", "sort_order": 4,
     "inputs": {"is_multistate": True, "apport_property_va": 200000, "apport_property_total": 1000000,
                "apport_payroll_va": 0, "apport_payroll_total": 0,
                "apport_sales_va": 400000, "apport_sales_total": 2000000},
     "expected_outputs": {"L8b": 0.2},
     "notes": "⚠⚠ THE DIVERGENCE THAT MOVES MONEY THE OTHER WAY. (0.20 + 2 x 0.20) / 3 = 0.20. The Form 502 "
              "instruction book would give / 2 = 0.30, because it restates Sec. 58.1-408 A but DROPS 'plus "
              "one'. The statute produces LESS Virginia tax here. Build to the statute; the book is defective."},
    {"scenario_name": "VA500-E - no factor has a denominator", "scenario_type": "edge", "sort_order": 5,
     "inputs": {"is_multistate": True, "apport_property_total": 0, "apport_payroll_total": 0,
                "apport_sales_total": 0},
     "expected_outputs": {"L8b": None, "diagnostic": "D_VA500_NO_DENOMINATOR"},
     "notes": "No factor, no substitute, hard diagnostic."},
    {"scenario_name": "VA500-F - ⚠⚠ a minimum-tax regime OVERWRITES Line 11", "scenario_type": "edge",
     "sort_order": 6,
     "inputs": {"federal_taxable_income": 2000000, "is_multistate": False, "nonrefundable_credits": 15000,
                "minimum_tax_regime": "electric_500EL", "minimum_tax_amount": 250000},
     "expected_outputs": {"L9": 120000, "L11": 250000, "diagnostic": "D_VA500_MIN_TAX_DEFERRED"},
     "notes": "⚠⚠ THE POINT OF THE WHOLE SPEC. Computed tax would be 120,000 less 15,000 credits = 105,000. "
              "Schedule 500EL REPLACES it with the SCC-certified 250,000. A derived-only Line 11 would report "
              "105,000 and UNDER-TAX the filer by 145,000 on a return that looks perfectly clean."},
    {"scenario_name": "VA500-G - settlement runs off the OVERWRITTEN Line 11", "scenario_type": "edge",
     "sort_order": 7,
     "inputs": {"federal_taxable_income": 2000000, "is_multistate": False,
                "minimum_tax_regime": "electric_500EL", "minimum_tax_amount": 250000,
                "estimated_payments": 100000},
     "expected_outputs": {"L11": 250000, "L16": 100000, "L17": 150000},
     "notes": "The overwrite propagates all the way to the amount due: 250,000 - 100,000 = 150,000. Had Line "
              "11 stayed derived, the filer would have been shown a much smaller balance."},
    {"scenario_name": "VA500-H - S&L percentage-of-income method", "scenario_type": "edge", "sort_order": 8,
     "inputs": {"federal_taxable_income": 500000, "is_multistate": False,
                "sl_bad_debt_method": "percentage_of_income"},
     "expected_outputs": {"L5": 500000, "L6": 200000, "L7": 300000, "L9": 18000},
     "notes": "Line 5 x 40% = 200,000 (Sec. 58.1-403). L7 = 300,000 x 6% = 18,000."},
    {"scenario_name": "VA500-I - S&L experience method does NOT touch Line 6", "scenario_type": "edge",
     "sort_order": 9,
     "inputs": {"federal_taxable_income": 500000, "is_multistate": False, "sl_bad_debt_method": "experience"},
     "expected_outputs": {"L6": 0, "L7": 500000, "diagnostic": "D_VA500_SL_METHOD"},
     "notes": "⚠ The experience and percentage-of-loans methods route through ADDITION CODE 13 on Schedule "
              "500ADJ instead. Putting a figure on Line 6 as well would double-count."},
    {"scenario_name": "VA500-J - combined return is refused, not computed", "scenario_type": "edge",
     "sort_order": 10,
     "inputs": {"federal_taxable_income": 3000000, "filing_status": "combined"},
     "expected_outputs": {"diagnostic": "D_VA500_FILING_STATUS_GATE"},
     "notes": "V2 - hard RED gate. Virginia's election is effectively permanent, so refusing beats computing "
              "confidently and wrongly."},
]


FORMS: list[dict] = [
    {
        "identity": {
            "form_number": "VA_500",
            "form_title": "Virginia Form 500 - Corporation Income Tax Return (TY2025)",
            "notes": (
                "WO-W05-CCORP; walk closed at campaign D-21. Virginia's C-corp return: flat 6% "
                "(Va. Code Sec. 58.1-400) on Virginia taxable income. Federal TI (AFTER federal NOL and "
                "special deductions) -> Schedule 500ADJ -> Schedule 500A apportionment for multistate filers "
                "-> 6% -> credits -> settlement. ⚠⚠ LINE 11 IS AN OVERWRITE TARGET: four SCC-certified "
                "minimum-tax regimes REPLACE it (500EL says 'replace the amount computed on Form 500'; 500HS "
                "also zeroes Line 10). The regimes are RED-deferred in v1 but the overwrite path exists, "
                "because a derived-only Line 11 silently discards the minimum tax. ⚠ The Sec. 58.1-408 A "
                "weight-sum divisor (4/3/3/2) is TRANSCRIBED and knowingly diverges from the printed forms in "
                "BOTH directions (D-18/G1). ⚠ v1 is SEPARATE RETURNS ONLY. ⚠ NO Virginia Sec. 179 figure is "
                "encoded - Virginia publishes none. ⚠ Ken's LOI decision (D-22) does NOT declare VA_500 to "
                "Virginia, so this is print/compute and TY2027 readiness, not the coming e-file season."
            ),
        },
        "facts": F_FACTS, "rules": F_RULES, "rule_links": F_RULE_LINKS,
        "lines": F_LINES, "diagnostics": F_DIAGNOSTICS, "scenarios": F_SCENARIOS,
    },
]

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-VA500-SPINE", "title": "The Form 500 spine: L1 -> L5 -> L7 -> L9 at 6%",
     "assertion_type": "reconciliation", "entity_types": ["1120"], "status": "draft", "sort_order": 1,
     "description": "L3 = L1 + L2; L5 = L3 - L4; L7 = L5 - L6; L9 = 6% of L7, or of L8(a) for a Schedule "
                    "500A filer. L1 is federal taxable income AFTER federal NOL and special deductions.",
     "definition": {"rule": "R-VA500-L9", "check": "L9 == round(max(0, L8a if multistate else L7) * 0.06, 2)"}},
    {"assertion_id": "FA-VA500-L11OVR", "title": "⚠⚠ Line 11 is an OVERWRITE target, never derived-only",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 2,
     "description": "When an SCC-certified regime applies, Line 11 takes the minimum tax and REPLACES the "
                    "computed L9-L10. Schedule 500EL: 'Enter this amount on Line 11 of Form 500, and replace "
                    "the amount computed on Form 500.' Form 500HS additionally zeroes Line 10. An engine "
                    "modelling Line 11 as derived-only silently discards the minimum tax and under-taxes a "
                    "certified filer on a clean-looking return.",
     "definition": {"rule": "R-VA500-L11", "check": "regime present -> L11 == minimum_tax_amount, NOT L9 - L10"}},
    {"assertion_id": "FA-VA500-DIV", "title": "The divisor is the weight-sum of EXISTING factors (4/3/3/2)",
     "assertion_type": "reconciliation", "entity_types": ["1120"], "status": "draft", "sort_order": 3,
     "description": "⚠ Transcribed from Va. Code § 58.1-408 A, which states both branches outright. All three "
                    "factors -> 4; sales missing -> 2; property or payroll missing -> 3. Knowingly diverges "
                    "from the printed forms in BOTH directions; the Form 502 instruction book drops the "
                    "statutory words 'plus one'. Build to the statute (D-18/G1).",
     "definition": {"rule": "R-VA500-APPORT", "check": "divisor == sum of weights of factors with a denominator"}},
    {"assertion_id": "FA-VA500-NO179", "title": "NO Virginia § 179 figure is encoded anywhere",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 4,
     "description": "⚠⚠ D-21/V3. Virginia publishes no § 179 dollar figure of its own. The derived "
                    "$1,250,000 / $3,130,000 / $31,300 must NEVER appear as Virginia constants - inventing a "
                    "state figure is exactly what the campaign's authoritative-source rule forbids. Their "
                    "absence is a decision, and the harness asserts it.",
     "definition": {"rule": "R-VA500-L5", "check": "no derived Virginia section 179 dollar constant exists anywhere in this spec"}},
    {"assertion_id": "FA-VA500-SEP", "title": "v1 computes SEPARATE returns only",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 5,
     "description": "Combined and consolidated returns are refused behind a hard gate (V2). The filing status "
                    "is a preparer assertion, never derived (W7). The change-of-basis diagnostic follows "
                    "§ 58.1-442 C, not the narrower instruction book (W11).",
     "definition": {"rule": "R-VA500-L11", "check": "filing_status in (combined, consolidated) -> refuse"}},
]


class Command(BaseCommand):
    help = ("Load the VA_500 spec (Virginia Corporation Income Tax Return, TY2025). "
            "Refuses to seed until Ken's Gate-1 SEED approval.")

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad VA_500 spec (Virginia Corporation Income Tax Return, TY2025)\n"))
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
        """Pinned to the GATE MECHANISM, not the sentinel's current value (D-17)."""
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
                "\nREFUSING TO SEED VA_500: not cleared to seed.\n\n"
                "Campaign D-21 approved the Virginia walk SCOPE (12 items). That is NOT the seed\n"
                "gate. Ken must give the Gate-1 SEED approval DIRECTLY - a relayed approval never\n"
                "opens a human gate.\n\n"
                f"READY_TO_SEED = {READY_TO_SEED} (must be True to proceed)\n\nEmpty:\n  {still_empty}\n"
            )

    def _load_topics(self):
        ct = 0
        for code, name in AUTHORITY_TOPICS:
            if len(name) > 255:
                raise CommandError(f"topic_name for {code!r} is {len(name)} chars - the column is 255 "
                                   "(the class that fails ONLY on the live database, campaign D-17).")
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
        # Contribute this pass's verbatim text to sources ANOTHER loader owns,
        # without rewriting the row itself.
        added = 0
        for code, exc in EXCERPTS_FOR_EXISTING:
            owner = sources.get(code) or AuthoritySource.objects.filter(source_code=code).first()
            if owner:
                _, made = AuthorityExcerpt.objects.update_or_create(
                    authority_source=owner, excerpt_label=exc["excerpt_label"], defaults=dict(exc))
                added += 1 if made else 0
        if added:
            self.stdout.write(f"  {added} excerpt(s) attached to sources owned elsewhere")
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
        self.stdout.write("VA_500 loaded (TY2025 ONLY - every figure is TY-keyed).")
        self.stdout.write(f"  VA_500: facts {len(F_FACTS)} / rules {len(F_RULES)} / lines {len(F_LINES)} / "
                          f"diag {len(F_DIAGNOSTICS)} / tests {len(F_SCENARIOS)}")
        self.stdout.write(f"  Flow assertions: {len(FLOW_ASSERTIONS)}")
        self.stdout.write("  !! Line 11 is an OVERWRITE target - see R-VA500-L11.")
        self.stdout.write("=" * 66)
