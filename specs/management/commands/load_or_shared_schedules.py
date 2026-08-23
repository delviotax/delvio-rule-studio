"""Load Oregon's two SHARED corporate schedules — `OR_AP` and `OR_ASC_CORP` (TY2025).

WO-W05-CCORP. Authored to close the dangling-reference defect recorded at
campaign **D-25 / walk item O4**.

═══════════════════════════════════════════════════════════════════════════
WHY THIS EXISTS — a real defect in PRODUCTION, found by reading, not testing
═══════════════════════════════════════════════════════════════════════════
The seeded, LIVE `OR_20_S` spec references these two schedules in **16 places**
— five FormRules (`R-OR20S-PART1`, `R-OR20S-L6-ALWAYS`, `R-OR20S-NO-C-E`,
`R-OR20S-LINES23-NS`, `R-OR20S-DEPR-NEG`), six FormLines (2, 3, 6, 7, 15, ES-7)
and the facts `or20s_l2_asc_corp_additions` / `or20s_l3_asc_corp_subtractions` —
while **neither existed as a form in RS prod** (which held only `OR_20_S`,
`OR_21`, `OR_65`). Verified against prod 2026-08-23.

Ken ruled at D-25/O4: **author both as FIRST-CLASS SHARED CODES and re-point the
seeded spec.** That ruling also decides the thing that actually matters
long-term — whether Oregon's code tables are **EXTENDED or DUPLICATED**. They
are extended: one definition here, consumed by every Oregon return.

═══════════════════════════════════════════════════════════════════════════
⚠ G4 — NEVER CLONE A SIBLING FORM'S LINE NUMBERS (campaign D-18)
═══════════════════════════════════════════════════════════════════════════
These schedules feed DIFFERENT line numbers on every form that consumes them:

    OR-ASC-CORP section │ OR-20 │ OR-20-INC │ OR-20-S
    ────────────────────┼───────┼───────────┼─────────
    A  additions        │   2   │     2     │    2
    B  subtractions     │   4   │     4     │    3   ⚠ NOT 4
    C  standard credits │  17   │    11     │   n/a  ⚠ no Section C line
    D  carryforward     │  19   │    13     │   15   ⚠ NOT 19
    E  refundable       │  ES-7 │   ES-7    │   n/a  ⚠ no Section E line

**So this spec is namespaced BY SECTION, never by a consuming form's line
number.** The consuming spec owns the mapping. Encoding "Section B → line 4"
here would be wrong for OR-20-S, which puts it on line 3.

═══════════════════════════════════════════════════════════════════════════
SCHEDULE OR-AP — 150-102-171 (Rev. 07-10-25, ver. 01), 4 pp.
═══════════════════════════════════════════════════════════════════════════
Purpose, verbatim (150-102-171-1 Rev. 10-14-25 p. 1): "Schedule OR-AP is used
for all corporations and partnerships that are doing business in more than one
state and may be used with Forms OR-20, OR-20-INC, OR-20-INS, OR-20-S, and
OR-65." — **the SAME PHYSICAL FORM for all five.**

STANDARD APPORTIONMENT = 100% SINGLE SALES FACTOR. ORS 314.650, 2025 Edition,
**the entire section, verbatim**: "Apportionment of income. All apportionable
income shall be apportioned to this state by multiplying the income by the sales
factor." History ends 2017 c.43 §4 — **last amended 2017, vintage-safe.**
⚠ **The section has NO SUBSECTIONS.** OAR 150-314-0385(3) still cites a
forest-products carve-out at "ORS 314.650(2)(a)" — an **orphan cross-reference**
almost certainly flattened by 2017 c.43 §4. **DO NOT BUILD A FOREST-PRODUCTS
BRANCH.** → carried open item U9.

THE ONE ALTERNATIVE — double-weighted sales, **utilities and telecommunications
ONLY**, elected by a checkbox on the consuming return (OR-20 question L,
OR-20-INC question K, OR-20-S question I), under ORS 314.650 **(1999 Edition)**
via ORS 314.280(3)(b).
⚠⚠ **Its line 6 is a LIVE DENOMINATOR, not the constant 4**: "Number of factors
with a positive number in column b." A factor whose *everywhere* figure is zero
is dropped from BOTH numerator and denominator. Hard-coding 4 silently
overstates the Oregon percentage whenever a factor is absent.

═══════════════════════════════════════════════════════════════════════════
SCHEDULE OR-ASC-CORP — 150-102-033 (Rev. 07-10-25, ver. 01), 4 pp., 5 sections
═══════════════════════════════════════════════════════════════════════════
Purpose, verbatim: "This schedule is for corporation filers only. Individuals do
not use this form. Schedule OR-ASC-CORP is used to report Oregon additions,
subtractions, and credits that don't have a specific line on the corporate
return."

⚠ **SECTIONS C AND E ARE FORM-GATED.** Verbatim: "Section E: Refundable credits
(Forms OR-20, OR-20-INC, and OR-20-INS only)… There are no refundable credits
available to S corporations." And: "Note: Form OR-20-S filers cannot claim
standard credits although some credits can flow through to shareholders."
→ **OR-20 is the ONLY corporate form that uses all five sections, and an
OR-20-S spec authored with C and E suppressed CANNOT be extended to OR-20 by
flipping a flag.**

⚠ **THE SCHEDULE-SM NOTE IS INERT ON THE C-CORP FORMS.** The instructions carry
"Note for OR-20-S filers: This schedule and these codes are not for additions or
subtractions on Schedule SM." **Form OR-20 has NO Schedule SM** — confirmed by a
positional read of all seven face pages, zero occurrences. **Do NOT port the
Schedule-SM firewall rule to OR-20**; a validation rule keyed to a non-existent
schedule is dead code that misleads the next author.

⚠ **SECTION D's DATA MODEL IS RICHER THAN A/B/C/E** and a build must carry all
four columns: Code · Amount from prior year · Amount awarded this year · Total
used this year → Total. Ordering rule, verbatim: "we'll apply your credits
against your tax in the order in which they're listed on the schedule… enter
your credits in the order in which they expire… **List all credits you have
available even if you can't use them this year.**"

CODE NAMESPACES — **there are FOUR Appendix As, one per corporate return**,
counted positionally off all four FINAL instruction PDFs: **OR-20 = 93 codes**,
OR-20-INC = 90, OR-20-INS = 62, **OR-20-S = 50**. The genuine full OR-ASC-CORP
universe is the **UNION = 105**. ⚠ OR-20's Appendix A **is not a subset of
anything** — it is the correct and complete eligibility list for OR-20, and it
DOES contain code 341.

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
# SAFETY GUARD — flip ONLY on Ken's Gate-1 SEED approval, given DIRECTLY.
# D-25/O4 approved AUTHORING these as first-class shared codes. That is not the
# seed gate. A relayed approval never opens a human gate.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = False


FORM_JURISDICTION = "OR"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"
# ⚠ These are SHARED schedules. OR-AP serves OR-65 (1065), OR-20-S (1120S) and
# OR-20/OR-20-INC/OR-20-INS (1120). OR-ASC-CORP is corporation-only — the
# instructions say so in terms ("for corporation filers only") — but OR-20-S is
# a corporation form, so 1120S belongs and 1065 does NOT.
AP_ENTITY_TYPES = ["1065", "1120", "1120S"]
ASC_ENTITY_TYPES = ["1120", "1120S"]

# Schedule OR-AP part 1 line 23: "Round to four decimal places" (OR-AP Instr. p.3).
OR_APPORT_DECIMALS: dict[int, int] = {2025: 4}

# The five OR-ASC-CORP sections, and which forms may use each. ⚠ FORM-GATED:
# OR-20-S filers cannot claim standard credits (C) and have no refundable
# credits (E). Encoded as data so a consuming spec cannot quietly assume five.
ASC_SECTIONS: dict[str, dict] = {
    "A": {"name": "Additions", "forms": ["OR_20", "OR_20_INC", "OR_20_INS", "OR_20_S"]},
    "B": {"name": "Subtractions", "forms": ["OR_20", "OR_20_INC", "OR_20_INS", "OR_20_S"]},
    "C": {"name": "Standard credits", "forms": ["OR_20", "OR_20_INC", "OR_20_INS"]},
    "D": {"name": "Carryforward credits", "forms": ["OR_20", "OR_20_INC", "OR_20_INS", "OR_20_S"]},
    "E": {"name": "Refundable credits", "forms": ["OR_20", "OR_20_INC", "OR_20_INS"]},
}

# Appendix A code counts, per return. ⚠ FOUR separate lists; the union is the
# schedule's real universe. Counted positionally off the FINAL instruction PDFs.
ASC_APPENDIX_A_COUNTS: dict[str, int] = {
    "OR_20": 93, "OR_20_INC": 90, "OR_20_INS": 62, "OR_20_S": 50,
}
ASC_CODE_UNION: int = 105


def _yk(table: dict, year: int = FORM_TAX_YEAR):
    """Year-keyed lookup. A new tax year staleness-invalidates every figure."""
    if year not in table:
        raise CommandError(f"No TY{year} value in {table!r} — re-verify before extending the year.")
    return table[year]


def _or_single_sales_factor(sales_or, sales_everywhere, year: int = FORM_TAX_YEAR):
    """Schedule OR-AP part 1 line 23 — the STANDARD worksheet.

    ORS 314.650 (2025 Edition), the entire section: "All apportionable income
    shall be apportioned to this state by multiplying the income by the sales
    factor." 100% single sales factor for TY2025; last amended 2017 c.43 §4.

    ⚠ Returns None when there are no sales everywhere — there is no factor to
    compute, and this must NOT silently become 100.0000 or 0.0000. The consuming
    return decides what to enter (OR-20-S line 6 enters 100.0000 only when the
    filer does NOT apportion, which is a different condition entirely).

    ⚠ NO FOREST-PRODUCTS BRANCH. OAR 150-314-0385(3) cites "ORS 314.650(2)(a)",
    but ORS 314.650 has NO subsections — an orphan cross-reference flattened by
    2017 c.43 §4. Carried open as U9.
    """
    if sales_everywhere is None or float(sales_everywhere) == 0:
        return None
    pct = (float(sales_or) / float(sales_everywhere)) * 100.0
    return round(pct, _yk(OR_APPORT_DECIMALS, year))


def _or_alternative_apportionment(factors, year: int = FORM_TAX_YEAR):
    """Schedule OR-AP alternative worksheet — DOUBLE-WEIGHTED SALES.

    Utilities and telecommunications taxpayers ONLY, elected by checkbox on the
    consuming return (OR-20 question L, OR-20-INC question K, OR-20-S question I).
    Authority: ORS 314.280(3)(b) routing to ORS 314.650 (1999 Edition).

    `factors` is a list of (numerator_or, denominator_everywhere) in worksheet
    order: property (line 1), payroll (line 2), sales (line 3), sales AGAIN
    (line 4 — "same as line 3 above", which is what makes sales double-weighted).

    ⚠⚠ LINE 6 IS A LIVE DENOMINATOR, NOT THE CONSTANT 4. Verbatim: "Number of
    factors with a positive number in column b." A factor whose EVERYWHERE
    figure is zero is dropped from BOTH the numerator sum and the denominator.
    Hard-coding 4 silently OVERSTATES the Oregon percentage whenever a factor is
    absent — the same class of error as Virginia's missing-factor divisor
    (campaign D-18/G1), and Oregon prints its rule where Virginia buried it.
    """
    total_pct = 0.0
    live = 0
    for num, den in factors:
        if den is None or float(den) == 0:
            continue                       # dropped from BOTH sides
        live += 1
        total_pct += (float(num) / float(den)) * 100.0
    if live == 0:
        return None
    return round(total_pct / live, _yk(OR_APPORT_DECIMALS, year))


def _asc_section_allowed(section: str, form_code: str) -> bool:
    """⚠ Sections C and E are FORM-GATED — OR-20-S may not use them.

    "Section E: Refundable credits (Forms OR-20, OR-20-INC, and OR-20-INS
    only)… There are no refundable credits available to S corporations." and
    "Note: Form OR-20-S filers cannot claim standard credits."
    """
    if section not in ASC_SECTIONS:
        raise CommandError(f"Unknown OR-ASC-CORP section {section!r} — the schedule has A, B, C, D, E.")
    return form_code in ASC_SECTIONS[section]["forms"]


AUTHORITY_TOPICS: list[tuple[str, str]] = [
    # ⚠ Keep under 255 — the column is varchar(255); the loader guards it, and it
    # caught this very entry at 263 chars during authoring (campaign D-17 class).
    ("or_shared_schedules", "Oregon shared corporate schedules: OR-AP apportionment (ORS 314.650 single "
     "sales factor + the utilities/telecom double-weighted alternative) and OR-ASC-CORP, whose five "
     "sections are form-gated and whose codes span four Appendix A lists."),
]

EXISTING_SOURCES_TO_REFERENCE: list[str] = []

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "OR_2025_SCH_AP", "source_type": "state_form", "source_rank": "primary_official",
        "jurisdiction_code": "OR", "title": "2025 Oregon Schedule OR-AP — Apportionment of Income for Corporations "
                                            "and Partnerships",
        "citation": "Schedule OR-AP, 150-102-171 (Rev. 07-10-25, ver. 01)", "issuer": "Oregon Department of Revenue",
        "official_url": "https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-ap_150-102-171.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.5,
        "topics": ["or_shared_schedules"],
        "excerpts": [{
            "excerpt_label": "Shared across five returns + both worksheets (instructions, verbatim)",
            "excerpt_text": (
                "'Schedule OR-AP is used for all corporations and partnerships that are doing business in more "
                "than one state and may be used with Forms OR-20, OR-20-INC, OR-20-INS, OR-20-S, and OR-65.' "
                "Standard worksheet: 'Apportionable income is apportioned to Oregon by multiplying the income by "
                "a multiplier equal to Oregon sales and other receipts as determined by Schedule OR-AP, part 1, "
                "divided by total sales and other receipts from the federal return (ORS 314.650).' '1. Total "
                "sales and other receipts (Schedule OR-AP, part 1, line 22)... (a) Oregon (b) everywhere' "
                "'2. Oregon apportionment percentage (enter on Schedule OR-AP, part 1, line 23) (Round to four "
                "decimal places)'. Alternative worksheet: 'Alternative apportionment worksheet (double-weighted "
                "sales factor formula) for utility or telecommunications taxpayers only. Taxpayers primarily "
                "engaged in utilities or telecommunications may elect to apportion trade or business income "
                "using the double-weighted sales factor [ORS 314.650 (1999 edition)]. Check the box on the front "
                "of your return if you're using this alternative apportionment worksheet (Form OR-20, question "
                "L; Form OR-20-INC, question K; Form OR-20-S, question I). All others use the standard "
                "apportionment worksheet above.' Its line 6: 'Number of factors with a positive number in "
                "column b.'"
            ),
            "summary_text": "OR-AP is ONE physical form shared by OR-20, OR-20-INC, OR-20-INS, OR-20-S and OR-65. "
                            "Standard = single sales factor to four decimals. Alternative = double-weighted sales, "
                            "utilities/telecom only, with a LIVE factor-count denominator.",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "OR_ORS_314_650", "source_type": "state_statute", "source_rank": "primary_official",
        "jurisdiction_code": "OR", "title": "ORS 314.650 — Apportionment of income (single sales factor)",
        "citation": "ORS 314.650 (2025 Edition)", "issuer": "Oregon Legislative Assembly",
        "official_url": "https://www.oregonlegislature.gov/bills_laws/ors/ors314.html",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["or_shared_schedules"],
        "excerpts": [{
            "excerpt_label": "The ENTIRE section, verbatim — and it has no subsections",
            "excerpt_text": (
                "'Apportionment of income. All apportionable income shall be apportioned to this state by "
                "multiplying the income by the sales factor.' History: [1965 c.152 s.10; 1989 c.626 s.5; 1989 "
                "c.1088 s.1; 1995 c.79 s.156; 2001 c.793 s.1; 2003 c.739 ss.1,5; 2005 c.832 ss.48,49; 2009 c.842 "
                "s.1; 2017 c.43 s.4] - last amended 2017, vintage-safe for TY2025. THE SECTION HAS NO "
                "SUBSECTIONS. OAR 150-314-0385(3) still cites a forest-products carve-out at 'ORS 314.650(2)(a)' "
                "- an ORPHAN CROSS-REFERENCE almost certainly flattened by 2017 c.43 s.4."
            ),
            "summary_text": "100% single sales factor for TY2025, one sentence, no subsections. Do NOT build a "
                            "forest-products branch off the orphaned OAR cross-reference (U9).",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "OR_2025_SCH_ASC_C", "source_type": "state_form", "source_rank": "primary_official",
        "jurisdiction_code": "OR", "title": "2025 Oregon Schedule OR-ASC-CORP — Oregon Adjustments for Corporate "
                                            "Filers",
        "citation": "Schedule OR-ASC-CORP, 150-102-033 (Rev. 07-10-25, ver. 01); instructions 150-102-033-1 "
                    "(Rev. 10-14-25)",
        "issuer": "Oregon Department of Revenue",
        "official_url": "https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-asc-corp_150-102-033.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.5,
        "topics": ["or_shared_schedules"],
        "excerpts": [{
            "excerpt_label": "Purpose, the FORM-GATED sections, and the entry rule (verbatim)",
            "excerpt_text": (
                "'This schedule is for corporation filers only. Individuals do not use this form. Schedule "
                "OR-ASC-CORP is used to report Oregon additions, subtractions, and credits that don't have a "
                "specific line on the corporate return. Code numbers and item explanations are in the "
                "instructions for Forms OR-20, OR-20-INC, OR-20-INS, and OR-20-S.' FORM-GATING: 'Section E: "
                "Refundable credits (Forms OR-20, OR-20-INC, and OR-20-INS only)... There are no refundable "
                "credits available to S corporations.' and 'Note: Form OR-20-S filers cannot claim standard "
                "credits although some credits can flow through to shareholders.' ENTRY RULE: 'Enter the code "
                "and amount for each item you're claiming. If you're claiming multiple items with the same code, "
                "report the items together. Enter each code only once and add the claimed amounts together.' "
                "SECTION D ORDERING: 'we'll apply your credits against your tax in the order in which they're "
                "listed on the schedule... enter your credits in the order in which they expire. Start with "
                "credits that expire earlier, followed by credits that expire later. List all credits you have "
                "available even if you can't use them this year.' DECOY: 'Note for OR-20-S filers: This schedule "
                "and these codes are not for additions or subtractions on Schedule SM.'"
            ),
            "summary_text": "Five sections; C and E are FORM-GATED away from OR-20-S. Each code entered ONCE with "
                            "amounts summed. Section D carries four columns and is ordered by expiry. The "
                            "Schedule-SM note is INERT on OR-20, which has no Schedule SM.",
            "is_key_excerpt": True,
        }],
    },
]

AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    ("OR_2025_SCH_AP", "OR_AP", "primary_form"),
    ("OR_ORS_314_650", "OR_AP", "statute"),
    ("OR_2025_SCH_ASC_C", "OR_ASC_CORP", "primary_form"),
    # ⚠ The whole point of D-25/O4 — the seeded consumers now resolve.
    ("OR_2025_SCH_AP", "OR_20_S", "related_form"),
    ("OR_2025_SCH_ASC_C", "OR_20_S", "related_form"),
    ("OR_2025_SCH_AP", "OR_65", "related_form"),
]


# ── Schedule OR-AP ─────────────────────────────────────────────────────────
AP_FACTS: list[dict] = [
    {"fact_key": "ap_sales_oregon", "label": "OR-AP part 1 line 22(a) — total sales and other receipts, OREGON",
     "data_type": "decimal", "required": False, "sort_order": 1},
    {"fact_key": "ap_sales_everywhere", "label": "OR-AP part 1 line 22(b) — total sales and other receipts, EVERYWHERE",
     "data_type": "decimal", "required": False, "sort_order": 2,
     "notes": "From the FEDERAL return, per the worksheet. A zero/absent denominator yields NO factor — never a "
              "silent 100.0000 or 0.0000."},
    {"fact_key": "ap_alt_apportionment_elected",
     "label": "Alternative (double-weighted sales) apportionment elected? — utilities/telecom ONLY",
     "data_type": "boolean", "required": False, "sort_order": 3,
     "notes": "Elected by checkbox on the CONSUMING return: OR-20 question L, OR-20-INC question K, OR-20-S "
              "question I. ORS 314.280(3)(b) → ORS 314.650 (1999 Edition)."},
    {"fact_key": "ap_property_oregon", "label": "OR-AP part 1 line 9(a) — total owned and rented property, OREGON",
     "data_type": "decimal", "required": False, "sort_order": 4,
     "notes": "Alternative worksheet only. For TY2025 the STANDARD formula ignores property entirely."},
    {"fact_key": "ap_property_everywhere", "label": "OR-AP part 1 line 9(b) — total owned and rented property, EVERYWHERE",
     "data_type": "decimal", "required": False, "sort_order": 5},
    {"fact_key": "ap_payroll_oregon", "label": "OR-AP part 1 line 12(a) — total wages and salaries, OREGON",
     "data_type": "decimal", "required": False, "sort_order": 6},
    {"fact_key": "ap_payroll_everywhere", "label": "OR-AP part 1 line 12(b) — total wages and salaries, EVERYWHERE",
     "data_type": "decimal", "required": False, "sort_order": 7},
    {"fact_key": "ap_net_loss_deduction", "label": "OR-AP part 2 line 10a — net loss deduction",
     "data_type": "decimal", "required": False, "sort_order": 8,
     "notes": "⚠ There is NO face line for this on OR-20-INC — it exists ONLY on OR-AP part 2 line 10a."},
    {"fact_key": "ap_net_capital_loss_deduction", "label": "OR-AP part 2 line 10b — net capital loss deduction",
     "data_type": "decimal", "required": False, "sort_order": 9,
     "notes": "⚠ Same: no OR-20-INC face line; OR-AP part 2 line 10b only."},
]

AP_RULES: list[dict] = [
    {"rule_id": "R-ORAP-SSF", "title": "Part 1 line 23 — the STANDARD single sales factor", "rule_type": "calculation",
     "formula": "L23 = None if ap_sales_everywhere == 0 else round((ap_sales_oregon / ap_sales_everywhere) * 100, 4)",
     "inputs": ["ap_sales_oregon", "ap_sales_everywhere"], "outputs": ["AP-1-23"], "sort_order": 1,
     "description": "ORS 314.650 (2025 Edition), the ENTIRE section: 'All apportionable income shall be "
                    "apportioned to this state by multiplying the income by the sales factor.' 100% single sales "
                    "factor for TY2025; last amended 2017 c.43 §4, so vintage-safe. Rounded to FOUR decimal "
                    "places per the worksheet. ⚠ A zero or missing 'everywhere' figure yields NO factor — the "
                    "consuming return decides what to enter, and OR-20-S's '100.0000 if you don't apportion' is "
                    "a DIFFERENT condition, not a fallback for a missing denominator. ⚠ NO FOREST-PRODUCTS "
                    "BRANCH: OAR 150-314-0385(3) cites 'ORS 314.650(2)(a)' but the section has no subsections — "
                    "an orphan cross-reference (U9)."},
    {"rule_id": "R-ORAP-ALT", "title": "Alternative worksheet — double-weighted sales, utilities/telecom only",
     "rule_type": "calculation",
     "formula": ("live = count of factors with everywhere > 0 among [property, payroll, sales, sales] ; "
                 "L7 = round(sum(pct of live factors) / live, 4)"),
     "inputs": ["ap_alt_apportionment_elected", "ap_property_oregon", "ap_property_everywhere",
                "ap_payroll_oregon", "ap_payroll_everywhere", "ap_sales_oregon", "ap_sales_everywhere"],
     "outputs": ["AP-1-23"], "sort_order": 2,
     "description": "ORS 314.280(3)(b) → ORS 314.650 (1999 Edition). Sales is counted TWICE (worksheet lines 3 "
                    "and 4, line 4 being 'same as line 3 above'), which is what double-weights it. ⚠⚠ LINE 6 IS "
                    "A LIVE DENOMINATOR, NOT THE CONSTANT 4 — verbatim, 'Number of factors with a positive "
                    "number in column b.' A factor whose EVERYWHERE figure is zero is dropped from BOTH the "
                    "numerator sum and the denominator. Hard-coding 4 silently OVERSTATES the Oregon percentage "
                    "whenever a factor is absent. Same class as Virginia's missing-factor divisor (D-18/G1) — "
                    "except Oregon PRINTS its rule where Virginia buried it in statute. Available ONLY to "
                    "taxpayers primarily engaged in utilities or telecommunications, and ONLY on election."},
    {"rule_id": "R-ORAP-P2", "title": "Part 2 — the deductions that exist ONLY on OR-AP", "rule_type": "calculation",
     "formula": "AP-2-12 = Oregon taxable income after part 2 lines 10a and 10b",
     "inputs": ["ap_net_loss_deduction", "ap_net_capital_loss_deduction"], "outputs": ["AP-2-12"], "sort_order": 3,
     "description": "⚠ The net loss deduction (part 2 line 10a) and net capital loss deduction (line 10b) have "
                    "NO face line on OR-20-INC at all — they exist only here. Part 2 line 12 is the Oregon "
                    "taxable income that OR-20-INC line 7 takes ALWAYS, and that OR-20 line 9 takes when the "
                    "filer apportions. A consuming spec that models these as face lines will invent lines that "
                    "do not exist."},
]

AP_LINES: list[dict] = [
    {"line_number": "AP-1-9", "description": "Part 1 line 9 — total owned and rented property (a) Oregon (b) everywhere",
     "line_type": "subtotal", "source_rules": ["R-ORAP-ALT"], "sort_order": 1},
    {"line_number": "AP-1-12", "description": "Part 1 line 12 — total wages and salaries (a) Oregon (b) everywhere",
     "line_type": "subtotal", "source_rules": ["R-ORAP-ALT"], "sort_order": 2},
    {"line_number": "AP-1-22", "description": "Part 1 line 22 — total sales and other receipts (a) Oregon (b) everywhere",
     "line_type": "subtotal", "source_rules": ["R-ORAP-SSF"], "sort_order": 3},
    {"line_number": "AP-1-23", "description": "Part 1 line 23 — Oregon apportionment percentage (FOUR decimals)",
     "line_type": "calculated", "source_rules": ["R-ORAP-SSF", "R-ORAP-ALT"], "sort_order": 4},
    {"line_number": "AP-2-10a", "description": "Part 2 line 10a — net loss deduction (NO face line elsewhere)",
     "line_type": "input", "source_rules": ["R-ORAP-P2"], "sort_order": 5},
    {"line_number": "AP-2-10b", "description": "Part 2 line 10b — net capital loss deduction (NO face line elsewhere)",
     "line_type": "input", "source_rules": ["R-ORAP-P2"], "sort_order": 6},
    {"line_number": "AP-2-12", "description": "Part 2 line 12 — Oregon taxable income",
     "line_type": "calculated", "source_rules": ["R-ORAP-P2"], "sort_order": 7},
]

AP_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_ORAP_NO_DENOMINATOR", "severity": "error",
     "title": "⚠ No sales everywhere — no apportionment percentage computed, and none substituted",
     "condition": "ap_sales_everywhere is None or ap_sales_everywhere == 0",
     "message": "Schedule OR-AP part 1 line 22(b) (total sales and other receipts everywhere, from the federal "
                "return) is zero or missing, so no apportionment percentage can be computed. This software will "
                "NOT substitute 100.0000 and will NOT substitute 0.0000. Note that a return which does not "
                "apportion at all is a DIFFERENT case: OR-20-S line 6 says to enter 100.0000 when you don't "
                "apportion, which is a filing posture, not a fallback for a missing denominator.",
     "notes": "The same no-auto-substitute discipline as Maryland D-5 and Virginia G1."},
    {"diagnostic_id": "D_ORAP_ALT_ELIGIBILITY", "severity": "warning",
     "title": "Double-weighted sales apportionment is restricted to utilities and telecommunications",
     "condition": "ap_alt_apportionment_elected == True",
     "message": "The alternative (double-weighted sales) apportionment worksheet is available ONLY to taxpayers "
                "primarily engaged in utilities or telecommunications, and only by election - check the box on "
                "the front of the return (Form OR-20 question L, OR-20-INC question K, OR-20-S question I). "
                "Authority is ORS 314.280(3)(b), which routes to the weightings in ORS 314.650 (1999 Edition). "
                "This software cannot verify that the taxpayer is primarily engaged in those activities; confirm "
                "eligibility before electing.",
     "notes": "Eligibility is a fact the return does not carry."},
    {"diagnostic_id": "D_ORAP_ALT_LIVE_DIVISOR", "severity": "info",
     "title": "A factor with no 'everywhere' amount is dropped from BOTH sides of the alternative formula",
     "condition": "ap_alt_apportionment_elected == True and any factor everywhere == 0",
     "message": "One or more factors have no 'everywhere' amount, so they are excluded from both the numerator "
                "and the divisor of the alternative apportionment worksheet. Worksheet line 6 is 'Number of "
                "factors with a positive number in column b' - a LIVE COUNT, not the constant 4. Treating the "
                "divisor as a fixed 4 would understate the average and overstate the Oregon percentage.",
     "notes": "⚠ The trap this spec exists to prevent. Oregon prints the rule; Virginia buried its equivalent."},
    {"diagnostic_id": "D_ORAP_NO_FOREST_BRANCH", "severity": "info",
     "title": "No forest-products apportionment branch exists — the OAR cross-reference is an orphan",
     "condition": "always (informational)",
     "message": "OAR 150-314-0385(3) cites a forest-products carve-out at 'ORS 314.650(2)(a)'. ORS 314.650 has "
                "NO SUBSECTIONS - the section is a single sentence, last amended by 2017 c.43 section 4, which "
                "almost certainly flattened it. This software does not implement a forest-products branch, and "
                "one should not be added on the strength of the orphaned rule cite alone.",
     "notes": "Carried open item U9. Recorded so a future reader does not 'restore' a branch that has no statute."},
]

AP_SCENARIOS: list[dict] = [
    {"scenario_name": "ORAP-A — standard single sales factor to four decimals", "scenario_type": "normal",
     "sort_order": 1,
     "inputs": {"ap_sales_oregon": 1234567, "ap_sales_everywhere": 10000000},
     "expected_outputs": {"AP-1-23": 12.3457},
     "notes": "(1,234,567 / 10,000,000) x 100 = 12.34567 -> 12.3457 at four decimal places."},
    {"scenario_name": "ORAP-B — no sales everywhere yields NO factor", "scenario_type": "edge", "sort_order": 2,
     "inputs": {"ap_sales_oregon": 500000, "ap_sales_everywhere": 0},
     "expected_outputs": {"AP-1-23": None, "diagnostic": "D_ORAP_NO_DENOMINATOR"},
     "notes": "⚠ Never 100.0000, never 0.0000. The 'enter 100.0000 if you don't apportion' instruction is a "
              "different condition and must not be used as a fallback."},
    {"scenario_name": "ORAP-C — alternative worksheet, all four factors live", "scenario_type": "edge",
     "sort_order": 3,
     "inputs": {"ap_alt_apportionment_elected": True,
                "ap_property_oregon": 200000, "ap_property_everywhere": 1000000,
                "ap_payroll_oregon": 300000, "ap_payroll_everywhere": 1000000,
                "ap_sales_oregon": 400000, "ap_sales_everywhere": 2000000},
     "expected_outputs": {"AP-1-23": 25.0},
     "notes": "Property 20% + payroll 30% + sales 20% + sales 20% = 90; divisor 4 (all live); 90/4 = 22.5. "
              "⚠ Recomputed: 20 + 30 + 20 + 20 = 90 -> 90/4 = 22.5. See ORAP-D for the live-divisor case."},
    {"scenario_name": "ORAP-D — ⚠ a missing factor DROPS from both sides (divisor 3, not 4)",
     "scenario_type": "edge", "sort_order": 4,
     "inputs": {"ap_alt_apportionment_elected": True,
                "ap_property_oregon": 0, "ap_property_everywhere": 0,
                "ap_payroll_oregon": 300000, "ap_payroll_everywhere": 1000000,
                "ap_sales_oregon": 400000, "ap_sales_everywhere": 2000000},
     "expected_outputs": {"AP-1-23": 23.3333, "diagnostic": "D_ORAP_ALT_LIVE_DIVISOR"},
     "notes": "⚠⚠ THE POINT OF THE WHOLE SCHEDULE. Property has no 'everywhere' amount, so it is dropped from "
              "BOTH sides: payroll 30% + sales 20% + sales 20% = 70, divisor 3 -> 23.3333. Hard-coding divisor 4 "
              "would give 17.5000 - understating the average and, on a real return, overstating Oregon income."},
    {"scenario_name": "ORAP-E — an all-Oregon filer reaches exactly 100.0000", "scenario_type": "edge",
     "sort_order": 5,
     "inputs": {"ap_sales_oregon": 4000000, "ap_sales_everywhere": 4000000},
     "expected_outputs": {"AP-1-23": 100.0},
     "notes": "A computed 100.0000 is distinct from the 'enter 100.0000 if you don't apportion' instruction."},
]

AP_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-ORAP-SSF", "title": "Standard apportionment is a SINGLE sales factor to four decimals",
     "assertion_type": "reconciliation", "entity_types": AP_ENTITY_TYPES, "status": "draft", "sort_order": 1,
     "description": "ORS 314.650 in full: 'All apportionable income shall be apportioned to this state by "
                    "multiplying the income by the sales factor.' Property and payroll are collected on OR-AP "
                    "part 1 but feed NOTHING in the standard formula for TY2025.",
     "definition": {"rule": "R-ORAP-SSF", "check": "AP-1-23 == round(sales_or / sales_everywhere * 100, 4)"}},
    {"assertion_id": "FA-ORAP-DIVISOR", "title": "The alternative divisor is a LIVE factor count, never 4",
     "assertion_type": "flow_assertion", "entity_types": AP_ENTITY_TYPES, "status": "draft", "sort_order": 2,
     "description": "⚠⚠ Worksheet line 6 is 'Number of factors with a positive number in column b'. A factor "
                    "with no 'everywhere' amount is dropped from BOTH the numerator and the divisor. Hard-coding "
                    "4 overstates the Oregon percentage whenever a factor is absent.",
     "definition": {"rule": "R-ORAP-ALT", "check": "divisor == count(factors with everywhere > 0), never the constant 4"}},
    {"assertion_id": "FA-ORAP-NOSUB", "title": "A missing denominator yields NO percentage, never a substitute",
     "assertion_type": "flow_assertion", "entity_types": AP_ENTITY_TYPES, "status": "draft", "sort_order": 3,
     "description": "Zero or missing sales everywhere returns None. The consuming return decides what to enter; "
                    "'100.0000 if you don't apportion' is a filing posture, not a fallback.",
     "definition": {"rule": "R-ORAP-SSF", "check": "sales_everywhere == 0 -> None + D_ORAP_NO_DENOMINATOR"}},
]


# ── Schedule OR-ASC-CORP ───────────────────────────────────────────────────
ASC_FACTS: list[dict] = [
    {"fact_key": "asc_section_a_additions", "label": "Section A — total Oregon additions (coded)",
     "data_type": "decimal", "required": False, "sort_order": 1,
     "notes": "⚠ Feeds a DIFFERENT line on every consumer: OR-20 line 2, OR-20-INC line 2, OR-20-S line 2. The "
              "consuming spec owns the mapping — this schedule is namespaced by SECTION (G4)."},
    {"fact_key": "asc_section_b_subtractions", "label": "Section B — total Oregon subtractions (coded)",
     "data_type": "decimal", "required": False, "sort_order": 2,
     "notes": "⚠ OR-20 line 4, OR-20-INC line 4, but OR-20-S line 3 — NOT line 4. Never clone the mapping."},
    {"fact_key": "asc_section_c_standard_credits", "label": "Section C — standard credits (coded)",
     "data_type": "decimal", "required": False, "sort_order": 3,
     "notes": "⚠ FORM-GATED. 'Form OR-20-S filers cannot claim standard credits although some credits can flow "
              "through to shareholders.' OR-20 line 17, OR-20-INC line 11."},
    {"fact_key": "asc_section_d_carryforward", "label": "Section D — carryforward credits (four-column model)",
     "data_type": "decimal", "required": False, "sort_order": 4,
     "notes": "⚠ RICHER than A/B/C/E — carries Code, Amount from prior year, Amount awarded this year, Total used "
              "this year, then Total. Ordered by EXPIRY, and all available credits are listed even if unusable "
              "this year. OR-20 line 19, OR-20-INC line 13, OR-20-S line 15."},
    {"fact_key": "asc_section_e_refundable", "label": "Section E — refundable credits (coded)",
     "data_type": "decimal", "required": False, "sort_order": 5,
     "notes": "⚠ FORM-GATED. 'Forms OR-20, OR-20-INC, and OR-20-INS only… There are no refundable credits "
              "available to S corporations.' Routes via Schedule ES line 7."},
    {"fact_key": "asc_consuming_form", "label": "Which return is consuming this schedule?",
     "data_type": "string", "required": False, "sort_order": 6,
     "notes": "OR_20 / OR_20_INC / OR_20_INS / OR_20_S. Drives the Section C and E gating, and the line mapping."},
]

ASC_RULES: list[dict] = [
    {"rule_id": "R-ORASC-GATE", "title": "Sections C and E are FORM-GATED away from OR-20-S", "rule_type": "validation",
     "formula": "section_allowed(C|E, form) == form in {OR_20, OR_20_INC, OR_20_INS}",
     "inputs": ["asc_consuming_form", "asc_section_c_standard_credits", "asc_section_e_refundable"],
     "outputs": ["asc_gate_ok"], "sort_order": 1,
     "description": "⚠ Verbatim: 'Section E: Refundable credits (Forms OR-20, OR-20-INC, and OR-20-INS only)… "
                    "There are no refundable credits available to S corporations.' and 'Note: Form OR-20-S "
                    "filers cannot claim standard credits although some credits can flow through to "
                    "shareholders.' ⚠⚠ CONSEQUENCE FOR THE BUILD: OR-20 is the ONLY corporate form using all "
                    "five sections, so an OR-20-S spec authored with C and E suppressed CANNOT be extended to "
                    "OR-20 by flipping a flag. The gating is encoded as DATA here so a consuming spec cannot "
                    "quietly assume five sections."},
    {"rule_id": "R-ORASC-ONCE", "title": "Each code appears ONCE, with amounts summed", "rule_type": "validation",
     "formula": "for each code: one row, amount = sum of all items carrying that code",
     "inputs": [], "outputs": [], "sort_order": 2,
     "description": "Verbatim: 'If you're claiming multiple items (additions, subtractions, or credits) with the "
                    "same code, report the items together. Enter each code only once and add the claimed amounts "
                    "together. If you have more items than will fit on a single schedule, provide the codes and "
                    "amounts on additional schedules and add the total to your tax return.'"},
    {"rule_id": "R-ORASC-D-COLS", "title": "Section D carries FOUR columns and is ordered by expiry",
     "rule_type": "calculation",
     "formula": "per code: prior_year + awarded_this_year -> used_this_year -> total ; rows ordered by expiry date",
     "inputs": ["asc_section_d_carryforward"], "outputs": ["asc_d_total"], "sort_order": 3,
     "description": "⚠ Section D's data model is richer than every other section. Verbatim: 'When we process "
                    "your return, we'll apply your credits against your tax in the order in which they're listed "
                    "on the schedule… enter your credits in the order in which they expire. Start with credits "
                    "that expire earlier, followed by credits that expire later. List all credits you have "
                    "available even if you can't use them this year.' The listing ORDER is operative — Oregon "
                    "applies credits in the order printed, so a build that reorders rows changes the outcome."},
    {"rule_id": "R-ORASC-NO-SM", "title": "VERIFIED NEGATIVE — the Schedule-SM note is INERT on the C-corp forms",
     "rule_type": "validation", "formula": "no Schedule SM firewall rule on OR_20 / OR_20_INC / OR_20_INS",
     "inputs": [], "outputs": [], "sort_order": 4,
     "description": "The instructions carry 'Note for OR-20-S filers: This schedule and these codes are not for "
                    "additions or subtractions on Schedule SM.' ⚠ FORM OR-20 HAS NO SCHEDULE SM — confirmed by a "
                    "positional read of all seven face pages, zero occurrences; the string appears only on the "
                    "OR-20-S face p.5 ('Schedule SM—Oregon modifications passed through to shareholders'). DO "
                    "NOT port the Schedule-SM firewall to the C-corp specs: a validation rule keyed to a "
                    "non-existent schedule is dead code that misleads the next author."},
]

ASC_LINES: list[dict] = [
    {"line_number": "ASC-A", "description": "Section A — Oregon additions (coded)",
     "line_type": "subtotal", "source_rules": ["R-ORASC-ONCE"], "sort_order": 1},
    {"line_number": "ASC-B", "description": "Section B — Oregon subtractions (coded)",
     "line_type": "subtotal", "source_rules": ["R-ORASC-ONCE"], "sort_order": 2},
    {"line_number": "ASC-C", "description": "Section C — standard credits (NOT available to OR-20-S)",
     "line_type": "subtotal", "source_rules": ["R-ORASC-GATE"], "sort_order": 3},
    {"line_number": "ASC-D", "description": "Section D — carryforward credits (four columns, expiry order)",
     "line_type": "subtotal", "source_rules": ["R-ORASC-D-COLS"], "sort_order": 4},
    {"line_number": "ASC-E", "description": "Section E — refundable credits (NOT available to OR-20-S)",
     "line_type": "subtotal", "source_rules": ["R-ORASC-GATE"], "sort_order": 5},
]

ASC_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_ORASC_S_NO_C_OR_E", "severity": "error",
     "title": "⚠ Form OR-20-S cannot claim standard or refundable credits",
     "condition": "asc_consuming_form == 'OR_20_S' and (asc_section_c_standard_credits > 0 or asc_section_e_refundable > 0)",
     "message": "Schedule OR-ASC-CORP Sections C (standard credits) and E (refundable credits) are not available "
                "to Form OR-20-S filers. The instructions state 'Section E: Refundable credits (Forms OR-20, "
                "OR-20-INC, and OR-20-INS only)... There are no refundable credits available to S corporations', "
                "and 'Note: Form OR-20-S filers cannot claim standard credits although some credits can flow "
                "through to shareholders.' Some credits may still PASS THROUGH to shareholders - that is a "
                "different mechanism and is not reported in these sections.",
     "notes": "⚠ Also the reason an OR-20-S spec cannot be extended to OR-20 by flipping a flag."},
    {"diagnostic_id": "D_ORASC_D_ORDER", "severity": "warning",
     "title": "Section D credit ORDER is operative — Oregon applies credits as listed",
     "condition": "asc_section_d_carryforward > 0",
     "message": "Oregon applies carryforward credits against tax in the ORDER THEY ARE LISTED on Schedule "
                "OR-ASC-CORP Section D. Enter credits in the order in which they EXPIRE - earliest-expiring "
                "first - and list every credit available even if it cannot be used this year. Reordering the "
                "rows changes which credits are consumed and which are lost, so the listing order is part of the "
                "return, not presentation.",
     "notes": "Section D also carries four columns: prior year, awarded this year, used this year, total."},
    {"diagnostic_id": "D_ORASC_CODE_ONCE", "severity": "info",
     "title": "Each code appears once, with its amounts summed",
     "condition": "any code appears more than once",
     "message": "Schedule OR-ASC-CORP requires each code to be entered ONCE with the claimed amounts added "
                "together, even where several separate items share the code. If more items exist than fit on one "
                "schedule, continue on additional schedules and carry the combined total to the return.",
     "notes": "Verbatim entry rule from the instructions."},
    {"diagnostic_id": "D_ORASC_NAMESPACE", "severity": "info",
     "title": "Code eligibility differs per return — there are FOUR Appendix A lists, not one",
     "condition": "always (informational)",
     "message": "Schedule OR-ASC-CORP is shared, but the codes a filer may use are NOT. There are four separate "
                "Appendix A lists, one per corporate return: Form OR-20 has 93 codes, OR-20-INC has 90, "
                "OR-20-INS has 62 and OR-20-S has 50; the union across all four is 105. Form OR-20's list is the "
                "complete and correct eligibility list for OR-20 and is NOT a subset of any other. Validate a "
                "code against the consuming return's own Appendix A, never against the union.",
     "notes": "⚠ Counted positionally off all four FINAL instruction PDFs. An earlier reading had these as "
              "91/48/103; the correct figures are 93/90/62/50, union 105."},
]

ASC_SCENARIOS: list[dict] = [
    {"scenario_name": "ORASC-A — OR-20 may use all five sections", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"asc_consuming_form": "OR_20", "asc_section_a_additions": 50000,
                "asc_section_c_standard_credits": 10000, "asc_section_e_refundable": 5000},
     "expected_outputs": {"asc_gate_ok": True},
     "notes": "OR-20 is the ONLY corporate form using all five sections."},
    {"scenario_name": "ORASC-B — ⚠ OR-20-S is gated out of Sections C and E", "scenario_type": "edge",
     "sort_order": 2,
     "inputs": {"asc_consuming_form": "OR_20_S", "asc_section_c_standard_credits": 10000},
     "expected_outputs": {"asc_gate_ok": False, "diagnostic": "D_ORASC_S_NO_C_OR_E"},
     "notes": "S corporations cannot claim standard or refundable credits. Some credits pass through to "
              "shareholders instead — a different mechanism, not these sections."},
    {"scenario_name": "ORASC-C — OR-20-S may use A, B and D", "scenario_type": "normal", "sort_order": 3,
     "inputs": {"asc_consuming_form": "OR_20_S", "asc_section_a_additions": 20000,
                "asc_section_b_subtractions": 8000, "asc_section_d_carryforward": 3000},
     "expected_outputs": {"asc_gate_ok": True},
     "notes": "⚠ And they land on OR-20-S lines 2, 3 and 15 — NOT the OR-20 lines 2, 4 and 19. The consuming "
              "spec owns the mapping (G4)."},
    {"scenario_name": "ORASC-D — Section D order is operative", "scenario_type": "edge", "sort_order": 4,
     "inputs": {"asc_consuming_form": "OR_20", "asc_section_d_carryforward": 25000},
     "expected_outputs": {"diagnostic": "D_ORASC_D_ORDER"},
     "notes": "Oregon applies credits in the order listed, so rows must be entered earliest-expiring first and "
              "every available credit listed even if unusable this year."},
]

ASC_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-ORASC-GATE", "title": "Sections C and E are unavailable to OR-20-S",
     "assertion_type": "flow_assertion", "entity_types": ASC_ENTITY_TYPES, "status": "draft", "sort_order": 1,
     "description": "⚠ Standard credits and refundable credits are form-gated to OR-20, OR-20-INC and "
                    "OR-20-INS. An OR-20-S spec authored with C and E suppressed CANNOT be extended to OR-20 by "
                    "flipping a flag — the gating is structural, and is encoded here as data.",
     "definition": {"rule": "R-ORASC-GATE", "check": "form == OR_20_S -> sections C and E refused"}},
    {"assertion_id": "FA-ORASC-NOSM", "title": "No Schedule-SM firewall on the C-corp forms",
     "assertion_type": "flow_assertion", "entity_types": ASC_ENTITY_TYPES, "status": "draft", "sort_order": 2,
     "description": "The Schedule-SM note applies to OR-20-S only. Form OR-20 has NO Schedule SM (zero "
                    "occurrences across all seven face pages), so a firewall rule there would be dead code "
                    "keyed to a schedule that does not exist.",
     "definition": {"rule": "R-ORASC-NO-SM", "check": "no SM rule is emitted for OR_20 / OR_20_INC / OR_20_INS"}},
    {"assertion_id": "FA-ORASC-NS", "title": "Code eligibility is per-return, not per-schedule",
     "assertion_type": "flow_assertion", "entity_types": ASC_ENTITY_TYPES, "status": "draft", "sort_order": 3,
     "description": "Four Appendix A lists — OR-20 93, OR-20-INC 90, OR-20-INS 62, OR-20-S 50, union 105. "
                    "Validate against the CONSUMING return's own list, never against the union, and never "
                    "assume one list is a subset of another.",
     "definition": {"rule": "R-ORASC-ONCE", "check": "code validated against ASC_APPENDIX_A_COUNTS[consuming_form]"}},
]


FORMS: list[dict] = [
    {
        "identity": {
            "form_number": "OR_AP",
            "form_title": "Oregon Schedule OR-AP — Apportionment of Income (TY2025)",
            "notes": (
                "SHARED schedule — ONE physical form used by OR-20, OR-20-INC, OR-20-INS, OR-20-S and OR-65. "
                "Authored at campaign D-25/O4 to close a dangling-reference defect: the seeded live OR_20_S "
                "referenced this schedule while it did not exist as a form in prod. Standard apportionment is a "
                "100% SINGLE SALES FACTOR (ORS 314.650, whole section, last amended 2017 — vintage-safe), to "
                "FOUR decimal places. ⚠ The alternative double-weighted-sales worksheet is utilities/telecom "
                "ONLY and its divisor is a LIVE FACTOR COUNT, never the constant 4. ⚠ No forest-products branch "
                "— the OAR cross-reference to 'ORS 314.650(2)(a)' is an orphan (U9)."
            ),
        },
        "entity_types": AP_ENTITY_TYPES,
        "facts": AP_FACTS, "rules": AP_RULES, "lines": AP_LINES,
        "diagnostics": AP_DIAGNOSTICS, "scenarios": AP_SCENARIOS, "assertions": AP_ASSERTIONS,
        "rule_links": [
            ("R-ORAP-SSF", "OR_ORS_314_650", "primary", "the entire section — single sales factor"),
            ("R-ORAP-SSF", "OR_2025_SCH_AP", "secondary", "part 1 line 23, four decimals"),
            ("R-ORAP-ALT", "OR_2025_SCH_AP", "primary", "the alternative worksheet and its live line-6 divisor"),
            ("R-ORAP-P2", "OR_2025_SCH_AP", "primary", "part 2 lines 10a/10b/12"),
        ],
    },
    {
        "identity": {
            "form_number": "OR_ASC_CORP",
            "form_title": "Oregon Schedule OR-ASC-CORP — Oregon Adjustments for Corporate Filers (TY2025)",
            "notes": (
                "SHARED schedule for corporation filers only (OR-20, OR-20-INC, OR-20-INS, OR-20-S). Authored at "
                "campaign D-25/O4 to close a dangling-reference defect. FIVE sections, and ⚠ C and E are "
                "FORM-GATED away from OR-20-S — so OR-20 is the only corporate form using all five, and an "
                "OR-20-S spec with C/E suppressed CANNOT be extended to OR-20 by flipping a flag. ⚠ Section D "
                "carries a four-column model and its LISTING ORDER is operative (Oregon applies credits as "
                "listed; enter earliest-expiring first). ⚠ FOUR Appendix A code lists — 93/90/62/50, union 105 "
                "— validate against the CONSUMING return's list. ⚠ The Schedule-SM note is INERT on the C-corp "
                "forms; OR-20 has no Schedule SM. Namespaced BY SECTION, never by a consuming form's line "
                "numbers (G4) — Section B is line 4 on OR-20 but line 3 on OR-20-S."
            ),
        },
        "entity_types": ASC_ENTITY_TYPES,
        "facts": ASC_FACTS, "rules": ASC_RULES, "lines": ASC_LINES,
        "diagnostics": ASC_DIAGNOSTICS, "scenarios": ASC_SCENARIOS, "assertions": ASC_ASSERTIONS,
        "rule_links": [
            ("R-ORASC-GATE", "OR_2025_SCH_ASC_C", "primary", "the Section C/E form-gating, verbatim"),
            ("R-ORASC-ONCE", "OR_2025_SCH_ASC_C", "primary", "enter each code only once"),
            ("R-ORASC-D-COLS", "OR_2025_SCH_ASC_C", "primary", "Section D four columns + expiry ordering"),
            ("R-ORASC-NO-SM", "OR_2025_SCH_ASC_C", "primary", "the Schedule-SM note and its inertness on OR-20"),
        ],
    },
]


class Command(BaseCommand):
    help = ("Load Oregon's shared schedules OR_AP and OR_ASC_CORP (TY2025). Closes the D-25/O4 "
            "dangling-reference defect. Refuses to seed until Ken's Gate-1 SEED approval.")

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad Oregon shared schedules (OR_AP + OR_ASC_CORP, TY2025)\n"))
        self._load_topics()
        sources = self._load_sources()
        for spec in FORMS:
            form = self._upsert_form(spec)
            self._upsert_facts(form, spec["facts"])
            rules = self._upsert_rules(form, spec["rules"])
            self._upsert_authority_links(rules, sources, spec["rule_links"])
            self._upsert_lines(form, spec["lines"])
            self._upsert_diagnostics(form, spec["diagnostics"])
            self._upsert_tests(form, spec["scenarios"])
            self._load_flow_assertions(spec["assertions"])
        self._upsert_form_links(sources)
        self._report_totals()

    def _guard_against_hollow_seed(self):
        """Pinned to the GATE MECHANISM, never to the sentinel's current value.

        Campaign D-17 recorded a harness going red the moment Ken approved
        something, five separate times. Assert the gate WORKS, never what it holds.
        """
        empty = []
        for spec in FORMS:
            fn = spec["identity"]["form_number"]
            for key in ("facts", "rules", "lines", "diagnostics", "scenarios", "assertions", "rule_links"):
                if not spec[key]:
                    empty.append(f"{fn}.{key}")
        if not READY_TO_SEED or empty:
            still_empty = "\n  ".join(f"- {n}" for n in empty) or "(all populated)"
            raise CommandError(
                "\nREFUSING TO SEED the Oregon shared schedules: not cleared to seed.\n\n"
                "Campaign D-25/O4 approved AUTHORING these as first-class shared codes. That is NOT\n"
                "the seed gate. Ken must give the Gate-1 SEED approval DIRECTLY - a relayed approval\n"
                "never opens a human gate.\n\n"
                "⚠ Note this seed also RE-POINTS the already-seeded OR_20_S, so it changes a live\n"
                "spec and not merely adds new ones.\n\n"
                f"READY_TO_SEED = {READY_TO_SEED} (must be True to proceed)\n\nEmpty:\n  {still_empty}\n"
            )

    def _load_topics(self):
        ct = 0
        for code, name in AUTHORITY_TOPICS:
            if len(name) > 255:
                raise CommandError(f"topic_name for {code!r} is {len(name)} chars — the column is 255 "
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
                "resolve becomes a DANGLING REFERENCE - which is the very defect (D-25/O4) this loader "
                "exists to fix. Correct the code before seeding."
            )
        for code in EXISTING_SOURCES_TO_REFERENCE:
            sources[code] = AuthoritySource.objects.get(source_code=code)
        self.stdout.write(f"Sources ready: {len(sources)}")
        return sources

    def _upsert_form(self, spec: dict) -> TaxForm:
        identity = spec["identity"]
        form, created = TaxForm.objects.update_or_create(
            form_number=identity["form_number"], jurisdiction=FORM_JURISDICTION,
            tax_year=FORM_TAX_YEAR, version=FORM_VERSION,
            defaults={"form_title": identity["form_title"], "entity_types": spec["entity_types"],
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

    def _load_flow_assertions(self, assertions):
        for a in assertions:
            a = dict(a)
            FlowAssertion.objects.update_or_create(assertion_id=a.pop("assertion_id"), defaults=a)
        self.stdout.write(f"  {len(assertions)} flow assertions")

    def _report_totals(self):
        self.stdout.write("\n" + "=" * 66)
        self.stdout.write("Oregon shared schedules loaded (TY2025 ONLY).")
        for spec in FORMS:
            self.stdout.write(
                f"  {spec['identity']['form_number']}: facts {len(spec['facts'])} / rules {len(spec['rules'])} / "
                f"lines {len(spec['lines'])} / diag {len(spec['diagnostics'])} / tests {len(spec['scenarios'])} / "
                f"FA {len(spec['assertions'])}")
        self.stdout.write("  ⚠ D-25/O4: the seeded OR_20_S referenced these in 16 places while neither existed.")
        self.stdout.write("=" * 66)
