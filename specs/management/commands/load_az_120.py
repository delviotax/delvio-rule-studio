"""Load the Arizona corporate specs - `AZ_120` and `AZ_120A` (TY2025).

WO-W05-CCORP. Arizona's walk closed at campaign **D-23**.

═══════════════════════════════════════════════════════════════════════════
TWO TOP-LEVEL SPECS, ONE SHARED RULE LIBRARY, NO SHARED FIELD MAP (D-23/A3)
═══════════════════════════════════════════════════════════════════════════
`AZ_120` is Arizona's full corporate return. `AZ_120A` is the SHORT FORM, and
its eligibility is narrow, verbatim: "The only type of corporation that may use
Arizona Form 120A is one that files its return on a separate company (separate
entity) basis and is a 'wholly Arizona corporation.'" Face banner: "IMPORTANT:
Do not use Form 120A to file an Arizona combined or consolidated return. Use
Form 120."

    Form 120A KEEPS  : SCHEDULE A A1-A9 and SCHEDULE B B1-B11 (same labels),
                       both worksheets (relocated to page 4), the 4.9%/$50
                       computation, Form 300 routing.
    Form 120A DROPS  : page-1 questions B, C, D, E, F, and Form 120's
                       Schedules C, D, E and F ENTIRELY.

So the Schedule A/B RULES are shared; the LINE MAPS are not. The same tax
concept sits on Form 120 line 16 and Form 120A line 8; on 120 line 21 and 120A
line 13; on 120 line 29 and 120A line 21.

⚠ NEITHER SHARES A CODE PATH WITH `AZ_120S`. Its
`HAS_MODIFICATION_APPARATUS = False` is pinned, while the corporate constant is
`True`. An S-corp spec cannot be widened into a C-corp spec here.

⚠⚠ A ROUTING TRAP THE FACE DOES NOT MAKE OBVIOUS: being a partner in a
MULTISTATE partnership - or in a partnership with no Arizona business - FORCES
Form 120, even for an otherwise wholly-Arizona separate-company filer. An engine
that keys form choice on multistate-ness alone gets this wrong.

═══════════════════════════════════════════════════════════════════════════
KEN'S RULINGS THIS SPEC IMPLEMENTS (campaign D-23)
═══════════════════════════════════════════════════════════════════════════
A1  The IRC Sec. 965(c) repatriation add-back is BUILT ON BOTH SPECS, on
    A.R.S. Sec. 43-961(5).
    ⚠ THE MIRROR IMAGE OF VIRGINIA AND MARYLAND, and deliberately not decided by
    reflex. There the instruction book claimed MORE than the statute and Ken
    ruled build-to-statute. Here the Form 120 book DIRECTS the add-back while
    the pinpointed statute (Sec. 43-1121(5)) is merely SILENT on Sec. 965(c) -
    24 paragraphs, zero hits for "965" - and a GENERAL provision reaches it:
    Sec. 43-961(5), "Items not deductible in computation of taxable income",
    which AZDOR itself cites for the parallel foreign-dividend expense add-back
    two items down the SAME worksheet. `[UNV-4]` stays carried.
    ⚠ New defect inside it: the Form 120A instruction book OMITS the Sec. 965(c)
    sentence ENTIRELY - zero hits across all 15 pages (defect D14).
A2  STANDING RULE - THE FORM 120A INSTRUCTION BOOK IS A TRANSCRIPTION REFERENCE
    ONLY. `AZ_120A` inherits the FORM 120 instruction book plus the 120A FACE.
    Five verified printed defects in the 120A book (D14-D18); eighteen AZDOR
    printed defects catalogued across the two books overall. This had to be
    settled BEFORE this shared Schedule A/B library was written, or the defects
    propagate into both specs.
W8  Depreciation is v1 DIRECT-ENTRY with hard prompts; the parallel engine is
    v1.1. ⚠ ARIZONA BONUS DEPRECIATION IS 0% FOR EVERY VINTAGE - there is NO
    tier table, and `AZ_165_B1_TIERS` must NOT be ported. So unlike Virginia,
    the divergence lands on EVERY corporate return with a depreciable asset.
W5  The $500 EFT / $1,000 estimates split is TWO constants, and the $500-$999
    band is its own case.
W6  Schedule A line A1 must capture COGS depreciation by DIRECT ENTRY - never a
    line-20 auto-pull.
W9  Form 300 is a direct-entry aggregator; the sixteen credit forms are
    RED-deferred.

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
# GATE 1 CLEARED - flipped 2026-08-23 on Ken's DIRECT seed approval.
#
# Ken, in-session: "approved", in answer to a message naming exactly
# VA_500, AZ_120 and AZ_120A - then re-confirmed for scope after the
# pre-flight finding below, because a bare word across three specs and two
# states is not a gate I should widen by inference.
#
# D-23 approved the walk SCOPE. This is the separate Gate-1 SEED approval.
#
# Pre-flight against PROD before flipping:
#   * every CharField value measured against the REAL model max_length - CLEAN
#   * the state's TY2025 conformity row confirmed PRESENT before the forms
#     (D-8's order, intact)
#   * referenced source codes verified to RESOLVE - no dangling reference
#   * declared source codes checked against every other loader - no two
#     writers of one row
# D-23 approved the walk SCOPE. That is not the seed gate.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = True


FORM_JURISDICTION = "AZ"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"
FORM_ENTITY_TYPES = ["1120"]

# ⚠ A.R.S. Sec. 43-1111 is keyed BY TAXABLE YEAR and lists FIVE tiers. Encode all
# five, not a bare 4.9% - prior Arizona years are in scope for amended-return
# work. Verbatim: "taxes in an amount of the greater of fifty dollars or:
#   1. For taxable years beginning through December 31, 2013, 6.968 per cent...
#   2. ...through December 31, 2014, 6.5 per cent...
#   3. ...through December 31, 2015, 6.0 per cent...
#   4. ...through December 31, 2016, 5.5 per cent...
#   5. For taxable years beginning from and after December 31, 2016, 4.9 per cent"
# ⚠ Vintage-checked: "43-1111" occurs ZERO times in chaptered Laws 2026 Ch. 140 -
# unamended, so the azleg text is current for TY2025.
AZ_RATE_TIERS: list[tuple[int, int, str]] = [
    (0, 2013, "0.06968"),
    (2014, 2014, "0.065"),
    (2015, 2015, "0.060"),
    (2016, 2016, "0.055"),
    (2017, 9999, "0.049"),
]
AZ_MINIMUM_TAX: dict[int, int] = {2025: 50}
AZ_APPORT_DECIMALS: dict[int, int] = {2025: 6}

# W5 - TWO constants, not one threshold. Booklet 120/165ES, verbatim: taxpayers
# anticipating "at least $1,000" must pay by EFT; taxpayers anticipating "more
# than $500 but less than $1,000 are NOT required to make Arizona estimated tax
# payments", but IF they elect to, those payments must also be by EFT.
AZ_ESTIMATES_REQUIRED_AT: dict[int, int] = {2025: 1000}
AZ_EFT_FLOOR: dict[int, int] = {2025: 500}

# ⚠⚠ W8 - ARIZONA BONUS DEPRECIATION IS 0% FOR EVERY VINTAGE. There is NO tier
# table for the corporate return: Form 120 line B1 is ONE SENTENCE with no tiers
# at all. DO NOT PORT `AZ_165_B1_TIERS` from the pass-through side - re-verified
# character-for-character. This constant exists so the zero reads as a verified
# finding rather than an omission.
AZ_BONUS_PCT_ALL_VINTAGES: dict[int, str] = {2025: "0.00"}

# Sec. 168(n) applies from TY2026 onward only - never for TY2025.
AZ_168N_FIRST_YEAR: int = 2026


def _yk(table: dict, year: int = FORM_TAX_YEAR):
    if year not in table:
        raise CommandError(f"No TY{year} value in {table!r} - re-verify before extending the year.")
    return table[year]


def _az_rate(year: int = FORM_TAX_YEAR) -> str:
    """A.R.S. Sec. 43-1111 - the rate for a given taxable year, from the five tiers.

    ⚠ Keyed BY YEAR deliberately (D-23 bless-list R1). A bare 4.9% constant would
    be right for TY2025 and wrong for any amended prior-year return, and Arizona
    stepped the rate down four times between 2013 and 2017.
    """
    for lo, hi, rate in AZ_RATE_TIERS:
        if lo <= year <= hi:
            return rate
    raise CommandError(f"No A.R.S. Sec. 43-1111 tier covers TY{year}.")


def _az_tax(taxable_income, year: int = FORM_TAX_YEAR, group_members: int = 1):
    """Form 120 line 16 / Form 120A line 8.

    Verbatim: "Enter tax: Tax is 4.9 percent of line 15 or fifty dollars ($50),
    whichever is greater." Instruction: "If the result is less than $50, enter
    the minimum tax of $50. Every corporation required to file a return shall
    pay a $50 minimum tax."

    ⚠⚠ ONE MINIMUM PER TAXPAYER, NOT PER MEMBER. Instruction, verbatim:
    "Combined or consolidated returns - a unitary group or an Arizona affiliated
    group is considered a SINGLE TAXPAYER. The minimum tax is imposed on the
    single taxpayer rather than on each corporation within the group."
    A build that applies $50 per member overstates a ten-member group by $450.
    `group_members` is accepted ONLY to make that explicit and is deliberately
    NOT used as a multiplier.
    """
    rate = float(_az_rate(year))
    computed = round(float(taxable_income) * rate, 2)
    minimum = float(_yk(AZ_MINIMUM_TAX, year))
    return max(minimum, computed)


def _az_apportionment_semantics(ratio):
    """Form 120 line 9 - and the distinction an engine will get wrong.

    Instructions, verbatim: "If line 9 is '0.000000', the corporation is
    considered to have NO ARIZONA NEXUS. If line 9 is BLANK or 1.000000, the
    corporation is considered to be 100% Arizona (taxable entirely within
    Arizona)."

    ⚠⚠ A BLANK AND A ZERO MEAN OPPOSITE THINGS. Blank = wholly Arizona, i.e.
    everything is taxed here. Zero = no nexus, i.e. nothing is. Any code path
    that coerces a missing ratio to 0.0 inverts the return completely. Returns
    one of: 'no_nexus', 'wholly_arizona', 'apportioned'.
    """
    if ratio is None:
        return "wholly_arizona"
    r = float(ratio)
    if r == 0.0:
        return "no_nexus"
    if r == 1.0:
        return "wholly_arizona"
    return "apportioned"


def _az_estimates_posture(anticipated_liability, elects_to_pay: bool = False,
                          year: int = FORM_TAX_YEAR):
    """W5 - the $500 / $1,000 split is TWO rules, and the band between them is real.

    Booklet 120/165ES, verbatim: "Taxpayers anticipating a tax liability for the
    current year of at least $1,000 must make Arizona estimated tax payments by
    EFT." And: "Taxpayers that anticipate a tax liability... of more than $500
    but less than $1,000 are NOT required to make Arizona estimated tax
    payments. If the taxpayer elects to make Arizona estimated tax payments, it
    is required to make those payments by EFT."

    ⚠ So in the $500-$999 band payment is OPTIONAL but the METHOD is still
    mandatory. Collapsing this to a single $1,000 threshold loses the rule that
    a voluntary payer must still use EFT.
    """
    amt = float(anticipated_liability or 0)
    required = _yk(AZ_ESTIMATES_REQUIRED_AT, year)
    floor = _yk(AZ_EFT_FLOOR, year)
    if amt >= required:
        return {"payments_required": True, "eft_required": True}
    if amt > floor:
        return {"payments_required": False, "eft_required": bool(elects_to_pay)}
    return {"payments_required": False, "eft_required": False}


def _az_120a_eligible(separate_company: bool, wholly_arizona: bool,
                      partner_in_multistate_or_non_az_partnership: bool = False):
    """Form 120A eligibility, verbatim: "The only type of corporation that may use
    Arizona Form 120A is one that files its return on a separate company
    (separate entity) basis and is a 'wholly Arizona corporation.'"

    ⚠⚠ THE TRAP: being a partner in a MULTISTATE partnership - or in a
    partnership with NO Arizona business - FORCES Form 120, even for an
    otherwise wholly-Arizona separate-company filer. An engine that keys form
    choice on multistate-ness alone gets this wrong, because the corporation
    itself looks wholly Arizona.
    """
    if partner_in_multistate_or_non_az_partnership:
        return False
    return bool(separate_company) and bool(wholly_arizona)


AUTHORITY_TOPICS: list[tuple[str, str]] = [
    # Keep under 255 - the loader guards it (D-17 class).
    ("az_corp_tax", "Arizona Forms 120 and 120A: the A.R.S. Sec. 43-1111 five-tier rate with a $50 minimum "
     "per TAXPAYER, the shared Schedule A/B modification library, the Sec. 965(c) add-back on Sec. 43-961(5), "
     "and zero bonus depreciation for every vintage."),
]

EXISTING_SOURCES_TO_REFERENCE: list[str] = []

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "AZ_2025_FORM_120", "source_type": "state_form", "source_rank": "primary_official",
        "jurisdiction_code": "AZ", "title": "2025 Arizona Form 120 - Arizona Corporation Income Tax Return",
        "citation": "Arizona Form 120 (2025), ADOR 10336", "issuer": "Arizona Department of Revenue",
        "official_url": "https://azdor.gov/forms/corporate-tax-forms",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.5,
        "topics": ["az_corp_tax"],
        "excerpts": [
            {
                "excerpt_label": "The line 1-21 spine, the 4.9%/$50 rule and the ONE-MINIMUM-PER-GROUP rule",
                "excerpt_text": (
                    "1 'Taxable income per included federal return'; 2 'Additions to taxable income from page "
                    "2, Schedule A, line A9'; 3 'Total taxable income: Add lines 1 and 2'; 4 'Subtractions "
                    "from taxable income from page 2, Schedule B, line B11'; 5 'Adjusted income: Subtract "
                    "Line 4 from line 3' then 'Multistate corporations, go to line 6. 100% Arizona "
                    "corporations, check box 5a - Go to line 13.'; 9 'Arizona apportionment ratio from "
                    "Schedule E or Schedule ACA' with 'Be certain to enter the amount in line 9 carried to "
                    "six decimal places.'; 13 'Arizona income before Net Operating Loss (NOL) from line 5 if "
                    "100% Arizona, or line 12 if Multistate corporation'; 14 'Arizona basis NOL carryover'; "
                    "15 'Arizona taxable income: Subtract line 14 from line 13.'; 16 'Enter tax: Tax is 4.9 "
                    "percent of line 15 or fifty dollars ($50), whichever is greater'; 21 'Tax liability: "
                    "Subtract line 19 from line 18.' Instruction to line 16: 'Every corporation required to "
                    "file a return shall pay a $50 minimum tax.' and 'Combined or consolidated returns - a "
                    "unitary group or an Arizona affiliated group is considered a single taxpayer. The "
                    "minimum tax is imposed on the single taxpayer rather than on each corporation within the "
                    "group.'"
                ),
                "summary_text": "Form 120: federal TI + Sch A - Sch B = adjusted income; multistate branch "
                                "through lines 6-12; line 15 Arizona taxable income; line 16 = greater of "
                                "4.9% or $50, ONE minimum per unitary/affiliated GROUP.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "⚠ Line 9 - a BLANK and a ZERO mean opposite things (verbatim)",
                "excerpt_text": (
                    "'If line 9 is \"0.000000\", the corporation is considered to have no Arizona nexus. If "
                    "line 9 is blank or 1.000000, the corporation is considered to be 100% Arizona (taxable "
                    "entirely within Arizona).'"
                ),
                "summary_text": "⚠⚠ Blank = wholly Arizona (everything taxed here). Zero = NO NEXUS (nothing "
                                "taxed here). Coercing a missing ratio to 0.0 inverts the return.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "AZ_2025_FORM_120A", "source_type": "state_form", "source_rank": "primary_official",
        "jurisdiction_code": "AZ", "title": "2025 Arizona Form 120A - Arizona Corporation Income Tax Return "
                                           "(Short Form)",
        "citation": "Arizona Form 120A (2025), ADOR 10949 (25)", "issuer": "Arizona Department of Revenue",
        "official_url": "https://azdor.gov/forms/corporate-tax-forms",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.4,
        "topics": ["az_corp_tax"],
        "excerpts": [{
            "excerpt_label": "⚠ A2 - eligibility, and why this book is transcription-reference ONLY",
            "excerpt_text": (
                "Eligibility, verbatim: 'The only type of corporation that may use Arizona Form 120A is one "
                "that files its return on a separate company (separate entity) basis and is a \"wholly "
                "Arizona corporation.\"' Face banner: 'IMPORTANT: Do not use Form 120A to file an Arizona "
                "combined or consolidated return. Use Form 120.' KEEPS Schedule A A1-A9 and Schedule B "
                "B1-B11 with the same labels, both worksheets relocated to page 4, the 4.9%/$50 computation "
                "and Form 300 routing. DROPS page-1 questions B, C, D, E and F, and Form 120's Schedules C, "
                "D, E and F entirely. ⚠ FIVE VERIFIED PRINTED DEFECTS in its instruction book: D14 the IRC "
                "Sec. 965(c) add-back sentence is MISSING ENTIRELY (zero hits across all 15 pages); D15 the "
                "A8 worksheet total is routed to the wrong line; D16 the A6 worksheet total is mislabelled "
                "'Total Other Additions'; D17 A8-D cites 'Sec. 43-961(5) or Sec. 43-1121(12)' where "
                "paragraph 12 is child-care facility depreciation and is irrelevant (Form 120 cites "
                "Sec. 43-961(5) alone); D18 A8-A cross-refers to the wrong page."
            ),
            "summary_text": "⚠ A2: AZ_120A inherits the FORM 120 instruction book plus the 120A FACE. Its own "
                            "book is a transcription reference only - five verified defects, one of which "
                            "silently drops a required add-back.",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "AZ_ARS_43_1111", "source_type": "state_statute", "source_rank": "primary_official",
        "jurisdiction_code": "AZ", "title": "A.R.S. Sec. 43-1111 - tax imposed on corporations (five tiers)",
        "citation": "A.R.S. Sec. 43-1111", "issuer": "Arizona State Legislature",
        "official_url": "https://www.azleg.gov/ars/43/01111.htm",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["az_corp_tax"],
        "excerpts": [{
            "excerpt_label": "The complete section, verbatim - all five tiers and the $50 floor",
            "excerpt_text": (
                "'There shall be levied, collected and paid for each taxable year upon the entire Arizona "
                "taxable income of every corporation, unless exempt under section 43-1126 or 43-1201 or as "
                "otherwise provided in this title or by law, taxes in an amount of the greater of fifty "
                "dollars or: 1. For taxable years beginning through December 31, 2013, 6.968 per cent of net "
                "income. 2. ...from and after December 31, 2013 through December 31, 2014, 6.5 per cent... "
                "3. ...through December 31, 2015, 6.0 per cent... 4. ...through December 31, 2016, 5.5 per "
                "cent... 5. For taxable years beginning from and after December 31, 2016, 4.9 per cent of "
                "net income.' ⚠ Vintage-checked: '43-1111' occurs ZERO times in the chaptered Laws 2026 "
                "Ch. 140 - unamended. ⚠ The exemption cross-reference is load-bearing: Sec. 43-1126 is the "
                "S-corporation provision and Sec. 43-1201 the exempt-organization list, and NEITHER appears "
                "in Form 120's own instruction book ([UNV-8])."
            ),
            "summary_text": "Five year-keyed tiers, 4.9% from TY2017 on, with a $50 floor that is part of the "
                            "levy itself. Unamended for TY2025.",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "AZ_ARS_43_961", "source_type": "state_statute", "source_rank": "primary_official",
        "jurisdiction_code": "AZ", "title": "A.R.S. Sec. 43-961 - items not deductible in computing taxable income",
        "citation": "A.R.S. Sec. 43-961(5)", "issuer": "Arizona State Legislature",
        "official_url": "https://www.azleg.gov/ars/43/00961.htm",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 10.0,
        "topics": ["az_corp_tax"],
        "excerpts": [{
            "excerpt_label": "⚠ A1 - the general hook that reaches the Sec. 965(c) add-back",
            "excerpt_text": (
                "Sec. 43-961(5), verbatim: 'Any amount, not otherwise provided for by this section, that "
                "would otherwise be allowable as a deduction or an adjustment, which is allocable to one or "
                "more classes of income, whether or not any amount of income of that class or classes is "
                "received or accrued, and that is not required to be included in a person's Arizona adjusted "
                "gross income or Arizona taxable income.' The section is titled 'Items not deductible in "
                "computation of taxable income' and has FIVE paragraphs; Sec. 965 is never mentioned. ⚠ The "
                "Form 120 instruction book directs, at line A4: 'Add back any deduction taken on the federal "
                "tax return pursuant to IRC Sec. 965(c) related to repatriation income.' The paragraph AZDOR "
                "pinpoints there - Sec. 43-1121(5) - names Sec.Sec. 243, 245, 245A and 250(a)(1)(B) and does "
                "NOT name Sec. 965(c): 24 paragraphs, zero hits for '965'. AZDOR itself cites Sec. 43-961(5) "
                "for the parallel foreign-dividend expense add-back at worksheet item A8-D."
            ),
            "summary_text": "⚠ A1: the pinpointed statute is silent on Sec. 965(c) but this general provision "
                            "reaches it, and AZDOR uses the same paragraph for the parallel add-back on the "
                            "same worksheet. Build the add-back on BOTH specs.",
            "is_key_excerpt": True,
        }],
    },
]

AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    ("AZ_2025_FORM_120", "AZ_120", "primary_form"),
    ("AZ_2025_FORM_120A", "AZ_120A", "primary_form"),
    ("AZ_ARS_43_1111", "AZ_120", "statute"),
    ("AZ_ARS_43_1111", "AZ_120A", "statute"),
    ("AZ_ARS_43_961", "AZ_120", "statute"),
    ("AZ_ARS_43_961", "AZ_120A", "statute"),
    # ⚠ A2 - AZ_120A inherits the FORM 120 instruction book, so the 120 source
    # governs it too. Recorded as a link, not left as prose.
    ("AZ_2025_FORM_120", "AZ_120A", "governs"),
]


# ═══════════════════════════════════════════════════════════════════════════
# THE SHARED SCHEDULE A/B RULE LIBRARY (D-23/A3)
# Identical rules on both forms. ⚠ The LINE MAPS are NOT shared - see below.
# ═══════════════════════════════════════════════════════════════════════════
def _shared_schedule_ab_rules(prefix: str) -> list[dict]:
    """Schedule A (additions A1-A9) and Schedule B (subtractions B1-B11).

    ⚠ Form 120A KEEPS these with the SAME LABELS, so the rules are shared and
    parameterised only by rule-id prefix. What is NOT shared is the field map:
    the resulting totals land on different line numbers on each form.
    """
    return [
        {"rule_id": f"{prefix}-SCHA", "title": "Schedule A - additions to taxable income (A1-A9)",
         "rule_type": "calculation",
         "formula": "A9 = A1..A8 summed",
         "inputs": ["sch_a_additions", "federal_965c_deduction"], "outputs": ["A9"], "sort_order": 10,
         "description": "⚠ A1 MUST CAPTURE COGS DEPRECIATION BY DIRECT ENTRY (W6) - never an auto-pull from "
                        "federal line 20. Depreciation embedded in cost of goods sold does not appear on the "
                        "federal depreciation line at all, so an auto-pull silently understates the addition. "
                        "⚠ A4 carries the IRC Sec. 965(c) repatriation add-back on BOTH specs (A1/D-23), on "
                        "A.R.S. Sec. 43-961(5) - the Form 120 book directs it, the pinpointed Sec. 43-1121(5) "
                        "is silent, and the general provision reaches it. ⚠ The FORM 120A INSTRUCTION BOOK "
                        "OMITS THAT SENTENCE ENTIRELY (defect D14) - build it on 120A anyway, from the Form "
                        "120 book, per the A2 standing rule."},
        {"rule_id": f"{prefix}-SCHB", "title": "Schedule B - subtractions from taxable income (B1-B11)",
         "rule_type": "calculation",
         "formula": "B11 = B1..B10 summed",
         "inputs": ["sch_b_subtractions", "az_depreciation_subtraction"], "outputs": ["B11"], "sort_order": 11,
         "description": "⚠⚠ B1 IS ONE SENTENCE WITH NO TIERS. Arizona bonus depreciation is 0% for EVERY "
                        "vintage on the corporate return - there is no five-tier recomputation here and "
                        "`AZ_165_B1_TIERS` from the pass-through side must NOT be ported (re-verified "
                        "character-for-character, D-23 bless-list). Because the bonus is zero in all years, "
                        "the Arizona/federal basis divergence lands on EVERY corporate return with a "
                        "depreciable asset - not on an edge case as in Virginia. v1 is DIRECT-ENTRY with "
                        "hard prompts; the parallel engine is v1.1 (W8). ⚠ IRC Sec. 168(n) applies from "
                        "TY2026 onward ONLY."},
        {"rule_id": f"{prefix}-965C", "title": "The IRC Sec. 965(c) repatriation add-back (A.R.S. Sec. 43-961(5))",
         "rule_type": "validation",
         "formula": "if federal_965c_deduction > 0: include in Schedule A line A4",
         "inputs": ["federal_965c_deduction"], "outputs": [], "sort_order": 12,
         "description": "⚠ A1/D-23, and THE MIRROR IMAGE of Virginia's G1 and Maryland's D3. There an "
                        "instruction book claimed MORE than the statute and Ken ruled build-to-statute. Here "
                        "the Form 120 book DIRECTS the add-back - 'Add back any deduction taken on the "
                        "federal tax return pursuant to IRC Sec. 965(c) related to repatriation income' - "
                        "while the paragraph AZDOR pinpoints (Sec. 43-1121(5)) is merely SILENT on it: 24 "
                        "paragraphs, zero hits for '965', confirmed on azleg AND on chaptered Ch. 140 Sec. "
                        "22. A GENERAL provision reaches it, Sec. 43-961(5), and AZDOR itself cites that same "
                        "paragraph for the parallel foreign-dividend expense add-back two items down the SAME "
                        "worksheet. Build on BOTH specs; carry `[UNV-4]`. ⚠ Rejected explicitly: building it "
                        "on AZ_120 only. That would make the same taxpayer's liability depend on WHICH FORM "
                        "THEY FILE, which Arizona cannot intend, and would hard-code defect D14."},
    ]


def _shared_tax_rules(prefix: str) -> list[dict]:
    """The 4.9% / $50 computation, identical on both forms."""
    return [
        {"rule_id": f"{prefix}-TAX", "title": "Tax - greater of the year's rate or the $50 minimum",
         "rule_type": "calculation",
         "formula": "tax = max(50, round(arizona_taxable_income * rate_for_year, 2))",
         "inputs": ["arizona_taxable_income"], "outputs": ["tax"], "sort_order": 20,
         "description": "A.R.S. Sec. 43-1111 levies 'the greater of fifty dollars or' the year's rate. ⚠ The "
                        "rate is TY-KEYED ACROSS FIVE TIERS (6.968% through TY2013, 6.5% TY2014, 6.0% TY2015, "
                        "5.5% TY2016, 4.9% from TY2017) - a bare 4.9% constant is right for TY2025 and wrong "
                        "for any amended prior-year return. ⚠⚠ ONE MINIMUM PER TAXPAYER, NOT PER MEMBER: "
                        "'a unitary group or an Arizona affiliated group is considered a SINGLE TAXPAYER. The "
                        "minimum tax is imposed on the single taxpayer rather than on each corporation within "
                        "the group.' Applying $50 per member overstates a ten-member group by $450. ⚠ The $50 "
                        "is part of the LEVY, not a floor applied afterwards - it is owed even by a "
                        "corporation with no income."},
    ]


# ── AZ_120: the full return ────────────────────────────────────────────────
AZ120_FACTS: list[dict] = [
    {"fact_key": "federal_taxable_income", "label": "L1 Taxable income per included federal return (1120 L30)",
     "data_type": "decimal", "required": False, "sort_order": 1},
    {"fact_key": "sch_a_additions", "label": "Schedule A additions A1-A8 (total to A9)",
     "data_type": "decimal", "required": False, "sort_order": 2,
     "notes": "⚠ W6: line A1 must capture COGS depreciation by DIRECT ENTRY, never an auto-pull from federal "
              "line 20 - depreciation inside cost of goods sold never appears on that line."},
    {"fact_key": "federal_965c_deduction", "label": "Federal IRC § 965(c) deduction taken (Schedule A line A4)",
     "data_type": "decimal", "required": False, "sort_order": 3,
     "notes": "⚠ A1/D-23: added back on BOTH AZ_120 and AZ_120A on A.R.S. § 43-961(5), even though the Form "
              "120A instruction book omits the sentence entirely (defect D14)."},
    {"fact_key": "sch_b_subtractions", "label": "Schedule B subtractions B1-B10 (total to B11)",
     "data_type": "decimal", "required": False, "sort_order": 4},
    {"fact_key": "az_depreciation_subtraction", "label": "Arizona depreciation subtraction (Sch. B line B1)",
     "data_type": "decimal", "required": False, "sort_order": 5,
     "notes": "⚠⚠ W8: DIRECT-ENTRY in v1. Arizona bonus is 0% for EVERY vintage - B1 is one sentence with no "
              "tiers, and AZ_165_B1_TIERS must NOT be ported. Every corporate return with a depreciable "
              "asset needs this."},
    {"fact_key": "is_multistate", "label": "Multistate corporation? (line 5 branch; 100% AZ checks box 5a)",
     "data_type": "boolean", "required": False, "sort_order": 6},
    {"fact_key": "nonapportionable_income", "label": "L7 Nonapportionable or allocable amounts (Sch. C line C8)",
     "data_type": "decimal", "required": False, "sort_order": 7},
    {"fact_key": "apportionment_ratio", "label": "L9 Arizona apportionment ratio (SIX decimal places)",
     "data_type": "decimal", "required": False, "sort_order": 8,
     "notes": "⚠⚠ BLANK AND ZERO MEAN OPPOSITE THINGS. '0.000000' = NO ARIZONA NEXUS. Blank or '1.000000' = "
              "100% Arizona, taxable entirely here. Coercing a missing ratio to 0.0 inverts the return. Face: "
              "'Be certain to enter the amount in line 9 carried to six decimal places.'"},
    {"fact_key": "other_income_allocated_az", "label": "L11 Other income allocated to Arizona (Sch. D line D6)",
     "data_type": "decimal", "required": False, "sort_order": 9},
    {"fact_key": "az_nol_carryover", "label": "L14 Arizona basis NOL carryover (include computation schedule)",
     "data_type": "decimal", "required": False, "sort_order": 10,
     "notes": "Capped at line 13. Arizona NOLs are CARRYFORWARD-ONLY, 20 years."},
    {"fact_key": "credit_recapture_300", "label": "L17 Tax from recapture of credits (Form 300, Pt 2, L22)",
     "data_type": "decimal", "required": False, "sort_order": 11},
    {"fact_key": "nonrefundable_credits_300", "label": "L19 Nonrefundable credits (Form 300, Pt 2, L40)",
     "data_type": "decimal", "required": False, "sort_order": 12,
     "notes": "⚠ W9: Form 300 is a DIRECT-ENTRY aggregator in v1; the sixteen underlying credit forms are "
              "RED-deferred. Cannot exceed line 18."},
    {"fact_key": "filing_method", "label": "Filing method - separate / combined / consolidated",
     "data_type": "string", "required": False, "sort_order": 13,
     "notes": "⚠ A unitary group or Arizona affiliated group is a SINGLE TAXPAYER for the $50 minimum. The "
              "consolidated election is BINDING and members are jointly and severally liable."},
    {"fact_key": "group_member_count", "label": "Members in the unitary / affiliated group",
     "data_type": "integer", "required": False, "sort_order": 14,
     "notes": "⚠ Recorded so the ONE-minimum-per-taxpayer rule is visible. It is NOT a multiplier for the "
              "$50 - applying it per member overstates a ten-member group by $450."},
    {"fact_key": "anticipated_liability", "label": "Anticipated current-year liability (estimates / EFT test)",
     "data_type": "decimal", "required": False, "sort_order": 15,
     "notes": "⚠ W5: TWO constants. >= $1,000 -> payments REQUIRED, by EFT. $501-$999 -> payments OPTIONAL, "
              "but IF elected they must still be by EFT."},
    {"fact_key": "elects_estimated_payments", "label": "Elects to pay estimates voluntarily ($501-$999 band)?",
     "data_type": "boolean", "required": False, "sort_order": 16},
]

AZ120_LINES: list[dict] = [
    {"line_number": "AZ120-3", "description": "L3 Total taxable income (L1 + L2)", "line_type": "subtotal",
     "source_rules": ["R-AZ120-SCHA"], "sort_order": 1},
    {"line_number": "AZ120-5", "description": "L5 Adjusted income (L3 - L4)", "line_type": "subtotal",
     "source_rules": ["R-AZ120-SCHB"], "sort_order": 2},
    {"line_number": "AZ120-8", "description": "L8 Adjusted business income (L6 - L7), multistate only",
     "line_type": "subtotal", "source_rules": ["R-AZ120-APPORT"], "sort_order": 3},
    {"line_number": "AZ120-9", "description": "L9 Arizona apportionment ratio (six decimals; blank != zero)",
     "line_type": "input", "source_rules": ["R-AZ120-APPORT"], "sort_order": 4},
    {"line_number": "AZ120-12", "description": "L12 Adjusted income attributable to Arizona (L10 + L11)",
     "line_type": "subtotal", "source_rules": ["R-AZ120-APPORT"], "sort_order": 5},
    {"line_number": "AZ120-13", "description": "L13 Arizona income before NOL (L5 if 100% AZ, else L12)",
     "line_type": "subtotal", "source_rules": ["R-AZ120-APPORT"], "sort_order": 6},
    {"line_number": "AZ120-15", "description": "L15 Arizona taxable income (L13 - L14)", "line_type": "subtotal",
     "source_rules": ["R-AZ120-NOL"], "sort_order": 7},
    {"line_number": "AZ120-16", "description": "L16 Tax - greater of the year's rate or $50",
     "line_type": "calculated", "source_rules": ["R-AZ120-TAX"], "sort_order": 8},
    {"line_number": "AZ120-18", "description": "L18 Subtotal (L16 + L17)", "line_type": "subtotal",
     "source_rules": ["R-AZ120-TAX"], "sort_order": 9},
    {"line_number": "AZ120-21", "description": "L21 Tax liability (L18 - L19), cannot be negative",
     "line_type": "calculated", "source_rules": ["R-AZ120-LIAB"], "sort_order": 10},
]

AZ120_EXTRA_RULES: list[dict] = [
    {"rule_id": "R-AZ120-APPORT", "title": "Lines 6-13 - the multistate branch and the line 9 semantics",
     "rule_type": "calculation",
     "formula": ("L8 = L5 - L7 ; L10 = L8 * L9 ; L12 = L10 + L11 ; "
                 "L13 = L5 if not is_multistate else L12"),
     "inputs": ["is_multistate", "nonapportionable_income", "apportionment_ratio",
                "other_income_allocated_az"], "outputs": ["L8", "L12", "L13"], "sort_order": 1,
     "description": "Face: 'Multistate corporations, go to line 6. 100% Arizona corporations, check box 5a - "
                    "Go to line 13.' ⚠⚠ LINE 9's SEMANTICS ARE THE TRAP: '0.000000' means NO ARIZONA NEXUS, "
                    "while BLANK or '1.000000' means 100% Arizona - taxable entirely here. A blank and a "
                    "zero mean OPPOSITE things, and any code path that coerces a missing ratio to 0.0 "
                    "inverts the return completely. Six decimal places, and the face insists on them. ⚠ "
                    "Arizona offers THREE elective apportionment methods and the sales factor MAY REACH 2.0 "
                    "- do NOT clamp it to 1.0. ⚠ The excluded-factor divisor is PRINTED on the Arizona form, "
                    "which cross-ratifies the shape of Virginia's G1 without inheriting its ambiguity."},
    {"rule_id": "R-AZ120-NOL", "title": "L14/L15 - Arizona NOL, carryforward-only, capped at line 13",
     "rule_type": "calculation",
     "formula": "L15 = L13 - min(az_nol_carryover, max(0, L13))",
     "inputs": ["az_nol_carryover"], "outputs": ["L15"], "sort_order": 2,
     "description": "Arizona NOLs are CARRYFORWARD-ONLY with a 20-year period - there is no carryback. The "
                    "deduction is capped at line 13, so it cannot create or deepen a loss. Line 15 is the "
                    "A.R.S. Sec. 43-1101(2) figure the rate applies to."},
    {"rule_id": "R-AZ120-LIAB", "title": "L18-L21 - recapture, credits and the liability floor",
     "rule_type": "calculation",
     "formula": "L18 = L16 + L17 ; L21 = max(0, L18 - min(L19, L18))",
     "inputs": ["credit_recapture_300", "nonrefundable_credits_300"], "outputs": ["L18", "L21"], "sort_order": 3,
     "description": "L19 nonrefundable credits CANNOT EXCEED L18, and L21 CANNOT BE NEGATIVE. ⚠ W9: Form 300 "
                    "is a direct-entry aggregator in v1 and the sixteen underlying credit forms are "
                    "RED-deferred. ⚠ Note the $50 minimum sits INSIDE L16, so credits can reduce the "
                    "liability below $50 - the minimum is on the TAX, not on the amount finally due."},
    {"rule_id": "R-AZ120-EST", "title": "Estimated payments - the $500 / $1,000 split (W5)",
     "rule_type": "validation",
     "formula": ("liability >= 1000 -> payments required AND EFT required ; "
                 "500 < liability < 1000 -> payments optional, EFT required IF elected"),
     "inputs": ["anticipated_liability", "elects_estimated_payments"], "outputs": [], "sort_order": 4,
     "description": "⚠ TWO constants, not one threshold. Booklet 120/165ES: taxpayers anticipating 'at least "
                    "$1,000' must pay 'by EFT'; taxpayers anticipating 'more than $500 but less than $1,000 "
                    "are NOT required to make Arizona estimated tax payments', but 'If the taxpayer elects to "
                    "make Arizona estimated tax payments, it is required to make those payments by EFT'. So "
                    "in the $501-$999 band PAYMENT is optional while the METHOD is mandatory. Collapsing "
                    "this to a single $1,000 threshold loses that rule."},
]

# ── AZ_120A: the short form ────────────────────────────────────────────────
AZ120A_FACTS: list[dict] = [
    {"fact_key": "federal_taxable_income", "label": "Taxable income per federal return (1120 L30)",
     "data_type": "decimal", "required": False, "sort_order": 1},
    {"fact_key": "sch_a_additions", "label": "Schedule A additions A1-A8 (total to A9) - SAME labels as Form 120",
     "data_type": "decimal", "required": False, "sort_order": 2},
    {"fact_key": "federal_965c_deduction", "label": "Federal IRC § 965(c) deduction taken (Schedule A line A4)",
     "data_type": "decimal", "required": False, "sort_order": 3,
     "notes": "⚠⚠ THE FORM 120A INSTRUCTION BOOK OMITS THIS ADD-BACK ENTIRELY (defect D14, zero hits for "
              "'965' across all 15 pages). Built here anyway from the FORM 120 book, per the A2 standing "
              "rule - otherwise the same taxpayer's liability would depend on which form they file."},
    {"fact_key": "sch_b_subtractions", "label": "Schedule B subtractions B1-B10 (total to B11)",
     "data_type": "decimal", "required": False, "sort_order": 4},
    {"fact_key": "az_depreciation_subtraction", "label": "Arizona depreciation subtraction (Sch. B line B1)",
     "data_type": "decimal", "required": False, "sort_order": 5},
    {"fact_key": "separate_company", "label": "Files on a separate company (separate entity) basis?",
     "data_type": "boolean", "required": False, "sort_order": 6,
     "notes": "Not part of a unitary group and not a member of an affiliated group that elected to file an "
              "Arizona consolidated return."},
    {"fact_key": "wholly_arizona", "label": "Is a 'wholly Arizona corporation'?",
     "data_type": "boolean", "required": False, "sort_order": 7},
    {"fact_key": "partner_in_multistate_ptnr", "label": "Partner in a multistate or non-Arizona partnership?",
     "data_type": "boolean", "required": False, "sort_order": 8,
     "notes": "⚠⚠ THE ROUTING TRAP. Being a partner in a MULTISTATE partnership - or in a partnership with "
              "NO Arizona business - FORCES Form 120, even for an otherwise wholly-Arizona separate-company "
              "filer. An engine keying form choice on the corporation's own multistate-ness gets this wrong."},
    {"fact_key": "az_nol_carryover", "label": "Arizona basis NOL carryover", "data_type": "decimal",
     "required": False, "sort_order": 9},
    {"fact_key": "nonrefundable_credits_300", "label": "Nonrefundable credits (Form 300, Part 2, L40)",
     "data_type": "decimal", "required": False, "sort_order": 10},
]

AZ120A_LINES: list[dict] = [
    # ⚠ G4 - DIFFERENT line numbers for the same concepts. Form 120 line 16 is
    # Form 120A line 8; 120 line 21 is 120A line 13; 120 line 29 is 120A line 21.
    {"line_number": "AZ120A-A9", "description": "Schedule A line A9 - total additions",
     "line_type": "subtotal", "source_rules": ["R-AZ120A-SCHA"], "sort_order": 1},
    {"line_number": "AZ120A-B11", "description": "Schedule B line B11 - total subtractions",
     "line_type": "subtotal", "source_rules": ["R-AZ120A-SCHB"], "sort_order": 2},
    {"line_number": "AZ120A-8", "description": "L8 Tax - greater of the year's rate or $50 (Form 120 line 16)",
     "line_type": "calculated", "source_rules": ["R-AZ120A-TAX"], "sort_order": 3},
    {"line_number": "AZ120A-13", "description": "L13 Tax liability (the Form 120 line 21 concept)",
     "line_type": "calculated", "source_rules": ["R-AZ120A-TAX"], "sort_order": 4},
]

AZ120A_EXTRA_RULES: list[dict] = [
    {"rule_id": "R-AZ120A-ELIG", "title": "Form 120A eligibility - and the partnership routing trap",
     "rule_type": "validation",
     "formula": ("eligible = separate_company AND wholly_arizona AND NOT "
                 "partner_in_multistate_or_non_az_partnership"),
     "inputs": ["separate_company", "wholly_arizona", "partner_in_multistate_ptnr"], "outputs": [],
     "sort_order": 1,
     "description": "Verbatim: 'The only type of corporation that may use Arizona Form 120A is one that files "
                    "its return on a separate company (separate entity) basis and is a \"wholly Arizona "
                    "corporation.\"' Face banner: 'IMPORTANT: Do not use Form 120A to file an Arizona "
                    "combined or consolidated return. Use Form 120.' ⚠⚠ THE TRAP: being a partner in a "
                    "MULTISTATE partnership - or in a partnership with NO Arizona business - FORCES Form 120 "
                    "even for an otherwise wholly-Arizona separate-company filer. The corporation itself "
                    "still looks wholly Arizona, so an engine keying form choice on its own multistate-ness "
                    "routes it to the wrong form."},
]


def _az120_rules():
    return (_shared_schedule_ab_rules("R-AZ120") + _shared_tax_rules("R-AZ120") + AZ120_EXTRA_RULES)


def _az120a_rules():
    return (_shared_schedule_ab_rules("R-AZ120A") + _shared_tax_rules("R-AZ120A") + AZ120A_EXTRA_RULES)


AZ120_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_AZ120_LINE9_BLANK_VS_ZERO", "severity": "warning",
     "title": "⚠⚠ Apportionment ratio: a BLANK and a 0.000000 mean opposite things",
     "condition": "is_multistate == True and apportionment_ratio in (None, 0)",
     "message": "Arizona's line 9 carries two meanings that are easy to conflate and produce opposite "
                "returns. Verbatim: 'If line 9 is \"0.000000\", the corporation is considered to have NO "
                "ARIZONA NEXUS. If line 9 is BLANK or 1.000000, the corporation is considered to be 100% "
                "Arizona (taxable entirely within Arizona).' So a zero means nothing is taxed here and a "
                "blank means everything is. Confirm which is intended before filing, and note the ratio must "
                "be carried to SIX decimal places.",
     "notes": "⚠ Any code path coercing a missing ratio to 0.0 inverts the return completely."},
    {"diagnostic_id": "D_AZ120_MIN_TAX_PER_GROUP", "severity": "info",
     "title": "The $50 minimum is per TAXPAYER, not per member",
     "condition": "filing_method in ('combined', 'consolidated')",
     "message": "Arizona's $50 minimum tax applies once to the group, not once per corporation. Verbatim: "
                "'Combined or consolidated returns - a unitary group or an Arizona affiliated group is "
                "considered a single taxpayer. The minimum tax is imposed on the single taxpayer rather than "
                "on each corporation within the group.' Applying it per member would overstate a ten-member "
                "group by $450. Note also that the consolidated election is BINDING, and members are jointly "
                "and severally liable for the tax.",
     "notes": "The $50 is part of the levy in A.R.S. Sec. 43-1111, not a floor applied afterwards."},
    {"diagnostic_id": "D_AZ120_DEPRECIATION_ENTRY", "severity": "warning",
     "title": "⚠ Arizona bonus depreciation is 0% for EVERY vintage - this affects nearly every return",
     "condition": "az_depreciation_subtraction > 0 or sch_a_additions > 0",
     "message": "Arizona allows NO bonus depreciation in any year, so Arizona basis diverges from federal "
                "basis on essentially every corporate return holding a depreciable asset - this is not an "
                "edge case. Schedule B line B1 is a single sentence with NO vintage tiers on the corporate "
                "return. Enter the Arizona depreciation figures directly in this version; the parallel "
                "Arizona depreciation book arrives in a later release. ⚠ Do not carry a tiered "
                "recomputation across from the Arizona pass-through forms - the corporate line has no tiers. "
                "⚠ IRC Section 168(n) applies from tax year 2026 onward only.",
     "notes": "W8. AZ_165_B1_TIERS must NOT be ported; re-verified character-for-character."},
    {"diagnostic_id": "D_AZ120_COGS_DEPRECIATION", "severity": "warning",
     "title": "Schedule A line A1 must include depreciation inside cost of goods sold",
     "condition": "sch_a_additions > 0",
     "message": "The Schedule A line A1 addition must capture ALL federal depreciation, including "
                "depreciation embedded in cost of goods sold. ⚠ COGS depreciation never appears on the "
                "federal depreciation line, so pulling that line automatically silently UNDERSTATES the "
                "Arizona addition. Enter the figure directly from the taxpayer's depreciation schedules.",
     "notes": "W6 - direct entry, never a line-20 auto-pull."},
    {"diagnostic_id": "D_AZ120_965C_ADDBACK", "severity": "info",
     "title": "The IRC § 965(c) add-back rests on § 43-961(5), not the paragraph AZDOR pinpoints",
     "condition": "federal_965c_deduction > 0",
     "message": "Arizona requires the IRC Section 965(c) repatriation deduction to be added back - the Form "
                "120 instruction book directs it at Schedule A line A4. ⚠ Note for the file: the paragraph "
                "the instructions pinpoint, A.R.S. Section 43-1121(5), names Sections 243, 245, 245A and "
                "250(a)(1)(B) and does NOT name Section 965(c). The add-back rests instead on the general "
                "provision A.R.S. Section 43-961(5) (items not deductible), which the Department itself "
                "cites for the parallel foreign-dividend expense add-back on the same worksheet. This "
                "software applies the add-back on BOTH Form 120 and Form 120A.",
     "notes": "A1 / [UNV-4] carried. Ruled by Ken at D-23 - the mirror image of the VA and MD instruction-book "
              "rulings, and deliberately not decided by reflex."},
    {"diagnostic_id": "D_AZ120_CREDITS_DEFERRED", "severity": "warning",
     "title": "Form 300 is a direct-entry aggregator - the sixteen credit forms are not computed",
     "condition": "nonrefundable_credits_300 > 0 or credit_recapture_300 > 0",
     "message": "This version does not compute Arizona's individual credit forms. Enter the totals from Form "
                "300 Part 2 (line 40 for nonrefundable credits, line 22 for recapture); the sixteen "
                "underlying credit forms must be prepared outside this software. Nonrefundable credits "
                "cannot exceed the subtotal on line 18, and the resulting tax liability cannot be negative.",
     "notes": "W9."},
    {"diagnostic_id": "D_AZ120_EFT_BAND", "severity": "info",
     "title": "Between $501 and $999 estimated payments are optional - but EFT is not",
     "condition": "500 < anticipated_liability < 1000",
     "message": "Arizona's estimated-payment rule is two rules. A taxpayer anticipating a liability of at "
                "least $1,000 MUST make estimated payments, and must make them by EFT. A taxpayer "
                "anticipating more than $500 but less than $1,000 is NOT required to make estimated payments "
                "at all - but if it chooses to, it is still required to make those payments by EFT. "
                "Voluntary payment does not mean voluntary method.",
     "notes": "W5 - two constants, and the $500-$999 band is its own case."},
]

AZ120A_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_AZ120A_NOT_ELIGIBLE", "severity": "error",
     "title": "⚠ This corporation may not use Form 120A",
     "condition": "not (separate_company and wholly_arizona) or partner_in_multistate_ptnr",
     "message": "Form 120A may be used ONLY by a corporation that files on a separate company (separate "
                "entity) basis AND is a 'wholly Arizona corporation'. The face states: 'IMPORTANT: Do not "
                "use Form 120A to file an Arizona combined or consolidated return. Use Form 120.' ⚠ AND "
                "NOTE A TRAP THAT IS EASY TO MISS: being a partner in a MULTISTATE partnership, or in a "
                "partnership with no Arizona business, FORCES Form 120 even where the corporation itself is "
                "wholly Arizona and files separately. File Form 120 instead.",
     "notes": "⚠ The routing rule an engine gets wrong if it keys form choice on the corporation's own "
              "multistate-ness alone."},
    {"diagnostic_id": "D_AZ120A_BOOK_IS_REFERENCE", "severity": "info",
     "title": "The Form 120A instruction book is a transcription reference only",
     "condition": "always (informational)",
     "message": "This software builds Form 120A from the FORM 120 instruction book plus the Form 120A form "
                "face. The Form 120A instruction book carries five verified printed defects and is not "
                "relied on for substance: it OMITS the IRC Section 965(c) add-back entirely; it routes the "
                "A8 worksheet total to the wrong line; it mislabels the A6 worksheet total; it cites "
                "'A.R.S. Section 43-1121(12)' at worksheet item A8-D, where paragraph 12 is child-care "
                "facility depreciation and is irrelevant (Form 120 cites Section 43-961(5) alone); and it "
                "cross-refers A8-A to the wrong page. Eighteen printed defects are catalogued across the two "
                "books; this software builds to the corrected values.",
     "notes": "⚠ A2, the standing rule. Settled BEFORE the shared Schedule A/B library was written, so the "
              "defects could not propagate into both specs."},
]

AZ120_SCENARIOS: list[dict] = [
    {"scenario_name": "AZ120-A - wholly Arizona corporation at 4.9%", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"federal_taxable_income": 1000000, "is_multistate": False},
     "expected_outputs": {"AZ120-15": 1000000, "AZ120-16": 49000},
     "notes": "1,000,000 x 4.9% = 49,000, comfortably above the $50 minimum."},
    {"scenario_name": "AZ120-B - the $50 minimum applies to a loss year", "scenario_type": "edge",
     "sort_order": 2,
     "inputs": {"federal_taxable_income": -250000, "is_multistate": False},
     "expected_outputs": {"AZ120-16": 50},
     "notes": "⚠ The $50 is part of the LEVY in A.R.S. Sec. 43-1111 ('the greater of fifty dollars or...'), "
              "not a floor applied afterwards. 'Every corporation required to file a return shall pay a $50 "
              "minimum tax' - including one with no income at all."},
    {"scenario_name": "AZ120-C - one $50 minimum for a ten-member group", "scenario_type": "edge",
     "sort_order": 3,
     "inputs": {"federal_taxable_income": 0, "filing_method": "consolidated", "group_member_count": 10},
     "expected_outputs": {"AZ120-16": 50, "diagnostic": "D_AZ120_MIN_TAX_PER_GROUP"},
     "notes": "⚠⚠ A unitary or affiliated group is a SINGLE TAXPAYER. $50 once, not $500. Applying the "
              "minimum per member would overstate this group by $450."},
    {"scenario_name": "AZ120-D - multistate apportionment to six decimals", "scenario_type": "normal",
     "sort_order": 4,
     "inputs": {"federal_taxable_income": 5000000, "is_multistate": True, "apportionment_ratio": 0.123457},
     "expected_outputs": {"AZ120-13": 617285, "AZ120-16": 30246.97},
     "notes": "5,000,000 x 0.123457 = 617,285; x 4.9% = 30,246.97."},
    {"scenario_name": "AZ120-E - ⚠ ratio 0.000000 means NO NEXUS, not 'wholly Arizona'",
     "scenario_type": "edge", "sort_order": 5,
     "inputs": {"federal_taxable_income": 5000000, "is_multistate": True, "apportionment_ratio": 0.0},
     "expected_outputs": {"semantics": "no_nexus", "diagnostic": "D_AZ120_LINE9_BLANK_VS_ZERO"},
     "notes": "⚠⚠ THE OPPOSITE OF A BLANK. Zero = no Arizona nexus, so nothing is taxed here. A blank or "
              "1.000000 would mean the entire 5,000,000 is Arizona income."},
    {"scenario_name": "AZ120-F - a blank ratio means WHOLLY ARIZONA", "scenario_type": "edge", "sort_order": 6,
     "inputs": {"federal_taxable_income": 5000000, "is_multistate": True, "apportionment_ratio": None},
     "expected_outputs": {"semantics": "wholly_arizona"},
     "notes": "The pair to AZ120-E. Blank and zero must never be normalised to each other."},
    {"scenario_name": "AZ120-G - the $501-$999 estimates band", "scenario_type": "edge", "sort_order": 7,
     "inputs": {"anticipated_liability": 750, "elects_estimated_payments": True},
     "expected_outputs": {"payments_required": False, "eft_required": True,
                          "diagnostic": "D_AZ120_EFT_BAND"},
     "notes": "⚠ W5. Payment is OPTIONAL in this band but the METHOD is mandatory - a voluntary payer must "
              "still use EFT. A single $1,000 threshold loses this."},
    {"scenario_name": "AZ120-H - prior-year rate tiers are TY-keyed", "scenario_type": "edge", "sort_order": 8,
     "inputs": {"tax_year": 2015, "arizona_taxable_income": 1000000},
     "expected_outputs": {"rate": "0.060"},
     "notes": "A.R.S. Sec. 43-1111 steps 6.968 / 6.5 / 6.0 / 5.5 / 4.9 by year. A bare 4.9% constant is "
              "right for TY2025 and wrong for any amended prior-year return."},
]

AZ120A_SCENARIOS: list[dict] = [
    {"scenario_name": "AZ120A-A - eligible wholly-Arizona separate filer", "scenario_type": "normal",
     "sort_order": 1,
     "inputs": {"separate_company": True, "wholly_arizona": True, "federal_taxable_income": 400000},
     "expected_outputs": {"eligible": True, "AZ120A-8": 19600},
     "notes": "400,000 x 4.9% = 19,600. Same computation as Form 120 line 16, different line number."},
    {"scenario_name": "AZ120A-B - ⚠ partner in a multistate partnership FORCES Form 120",
     "scenario_type": "edge", "sort_order": 2,
     "inputs": {"separate_company": True, "wholly_arizona": True, "partner_in_multistate_ptnr": True},
     "expected_outputs": {"eligible": False, "diagnostic": "D_AZ120A_NOT_ELIGIBLE"},
     "notes": "⚠⚠ THE ROUTING TRAP. The corporation itself is separate-company and wholly Arizona, so an "
              "engine keying on its own multistate-ness would wrongly allow the short form."},
    {"scenario_name": "AZ120A-C - a consolidated filer may not use the short form", "scenario_type": "edge",
     "sort_order": 3,
     "inputs": {"separate_company": False, "wholly_arizona": True},
     "expected_outputs": {"eligible": False, "diagnostic": "D_AZ120A_NOT_ELIGIBLE"},
     "notes": "Face banner: 'Do not use Form 120A to file an Arizona combined or consolidated return.'"},
    {"scenario_name": "AZ120A-D - the § 965(c) add-back applies even though the 120A book omits it",
     "scenario_type": "edge", "sort_order": 4,
     "inputs": {"separate_company": True, "wholly_arizona": True, "federal_965c_deduction": 300000},
     "expected_outputs": {"addback_applied": True},
     "notes": "⚠⚠ Defect D14 - the Form 120A instruction book omits the sentence entirely. Built from the "
              "Form 120 book per the A2 standing rule; otherwise the same taxpayer's liability would depend "
              "on which form they file."},
]


FORMS: list[dict] = [
    {
        "identity": {
            "form_number": "AZ_120",
            "form_title": "Arizona Form 120 - Arizona Corporation Income Tax Return (TY2025)",
            "notes": (
                "WO-W05-CCORP; walk closed at campaign D-23. Arizona's full corporate return: federal TI + "
                "Schedule A - Schedule B = adjusted income; multistate branch through lines 6-12; line 15 "
                "Arizona taxable income; line 16 = greater of the year's rate or $50. ⚠ The rate is TY-KEYED "
                "across FIVE tiers (A.R.S. Sec. 43-1111), and ⚠⚠ the $50 minimum is ONE PER TAXPAYER - a "
                "unitary or affiliated group is a single taxpayer. ⚠⚠ Line 9: a BLANK means wholly Arizona "
                "while 0.000000 means NO NEXUS - opposite meanings. ⚠ Bonus depreciation is 0% for EVERY "
                "vintage, so the basis divergence touches nearly every return; AZ_165_B1_TIERS must NOT be "
                "ported. ⚠ Shares a Schedule A/B RULE LIBRARY with AZ_120A but NO field map, and shares no "
                "code path with AZ_120S."
            ),
        },
        "facts": AZ120_FACTS, "rules": _az120_rules(), "lines": AZ120_LINES,
        "diagnostics": AZ120_DIAGNOSTICS, "scenarios": AZ120_SCENARIOS,
        "rule_links": [
            ("R-AZ120-SCHA", "AZ_2025_FORM_120", "primary", "Schedule A A1-A9"),
            ("R-AZ120-SCHB", "AZ_2025_FORM_120", "primary", "Schedule B B1-B11, no vintage tiers"),
            ("R-AZ120-965C", "AZ_ARS_43_961", "primary", "the general hook Sec. 43-961(5)"),
            ("R-AZ120-965C", "AZ_2025_FORM_120", "secondary", "the line A4 instruction directing the add-back"),
            ("R-AZ120-TAX", "AZ_ARS_43_1111", "primary", "the five tiers and the $50 levy"),
            ("R-AZ120-TAX", "AZ_2025_FORM_120", "secondary", "line 16 and the one-minimum-per-group rule"),
            ("R-AZ120-APPORT", "AZ_2025_FORM_120", "primary", "lines 6-13 and the line 9 semantics"),
            ("R-AZ120-NOL", "AZ_2025_FORM_120", "primary", "lines 14-15"),
            ("R-AZ120-LIAB", "AZ_2025_FORM_120", "primary", "lines 18-21"),
            ("R-AZ120-EST", "AZ_2025_FORM_120", "primary", "the estimates/EFT split"),
        ],
    },
    {
        "identity": {
            "form_number": "AZ_120A",
            "form_title": "Arizona Form 120A - Arizona Corporation Income Tax Return, Short Form (TY2025)",
            "notes": (
                "WO-W05-CCORP; walk closed at campaign D-23. The SHORT FORM, usable ONLY by a corporation "
                "filing on a separate company basis that is a 'wholly Arizona corporation'. KEEPS Schedule A "
                "A1-A9 and Schedule B B1-B11 with identical labels, the worksheets (relocated to page 4) and "
                "the 4.9%/$50 computation; DROPS page-1 questions B-F and Form 120's Schedules C, D, E and F "
                "entirely. ⚠⚠ ROUTING TRAP: being a partner in a MULTISTATE partnership, or one with no "
                "Arizona business, FORCES Form 120 even for an otherwise eligible filer. ⚠⚠ A2 STANDING "
                "RULE: the Form 120A instruction book is a TRANSCRIPTION REFERENCE ONLY - five verified "
                "printed defects, including D14 where it OMITS the IRC Sec. 965(c) add-back entirely. This "
                "spec inherits the FORM 120 book plus the 120A FACE."
            ),
        },
        "facts": AZ120A_FACTS, "rules": _az120a_rules(), "lines": AZ120A_LINES,
        "diagnostics": AZ120A_DIAGNOSTICS, "scenarios": AZ120A_SCENARIOS,
        "rule_links": [
            ("R-AZ120A-SCHA", "AZ_2025_FORM_120", "primary", "A2 - the FORM 120 book governs Schedule A"),
            ("R-AZ120A-SCHB", "AZ_2025_FORM_120", "primary", "A2 - the FORM 120 book governs Schedule B"),
            ("R-AZ120A-965C", "AZ_ARS_43_961", "primary", "built despite the 120A book's D14 omission"),
            ("R-AZ120A-TAX", "AZ_ARS_43_1111", "primary", "the same five tiers and $50 levy"),
            ("R-AZ120A-ELIG", "AZ_2025_FORM_120A", "primary", "eligibility + the partnership routing trap"),
        ],
    },
]

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-AZ120-MIN", "title": "The $50 minimum is per TAXPAYER, never per member",
     "assertion_type": "reconciliation", "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 1,
     "description": "A.R.S. Sec. 43-1111 levies 'the greater of fifty dollars or' the year's rate, so the $50 "
                    "is part of the levy and is owed even in a loss year. ⚠ A unitary group or Arizona "
                    "affiliated group is a SINGLE TAXPAYER - one $50, not one per member. Applying it per "
                    "member overstates a ten-member group by $450.",
     "definition": {"rule": "R-AZ120-TAX", "check": "tax == max(50, taxable_income * rate_for_year)"}},
    {"assertion_id": "FA-AZ120-L9", "title": "⚠⚠ A blank apportionment ratio is NOT a zero",
     "assertion_type": "flow_assertion", "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 2,
     "description": "'0.000000' means NO ARIZONA NEXUS; blank or '1.000000' means 100% Arizona, taxable "
                    "entirely here. They are OPPOSITE outcomes and must never be normalised to each other. "
                    "Any code path coercing a missing ratio to 0.0 inverts the return.",
     "definition": {"rule": "R-AZ120-APPORT", "check": "None -> wholly_arizona ; 0.0 -> no_nexus"}},
    {"assertion_id": "FA-AZ120-NOTIERS", "title": "Arizona bonus is 0% every vintage - no tier table exists",
     "assertion_type": "flow_assertion", "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 3,
     "description": "⚠ Schedule B line B1 is ONE SENTENCE with no vintage tiers on the corporate return. "
                    "`AZ_165_B1_TIERS` from the pass-through side must NOT be ported - re-verified "
                    "character-for-character. Because the bonus is zero in ALL years, the divergence touches "
                    "every corporate return with a depreciable asset. Sec. 168(n) is TY2026+ only.",
     "definition": {"rule": "R-AZ120-SCHB", "check": "no vintage tier table exists in this spec"}},
    {"assertion_id": "FA-AZ120-965", "title": "The § 965(c) add-back applies on BOTH forms",
     "assertion_type": "flow_assertion", "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 4,
     "description": "⚠ Built on A.R.S. Sec. 43-961(5), the general 'items not deductible' provision, because "
                    "the paragraph AZDOR pinpoints (Sec. 43-1121(5)) does not name Sec. 965(c) - and AZDOR "
                    "itself cites Sec. 43-961(5) for the parallel add-back on the same worksheet. ⚠ The Form "
                    "120A book omits the sentence entirely (D14); building on 120A only would make liability "
                    "depend on WHICH FORM the taxpayer files.",
     "definition": {"rule": "R-AZ120-965C", "check": "the add-back rule exists on AZ_120 AND AZ_120A"}},
    {"assertion_id": "FA-AZ120A-ROUTE", "title": "A multistate-partnership interest forces Form 120",
     "assertion_type": "flow_assertion", "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 5,
     "description": "⚠⚠ Being a partner in a MULTISTATE partnership - or one with no Arizona business - "
                    "forces Form 120 even for a separate-company, wholly-Arizona corporation. An engine "
                    "keying form choice on the corporation's OWN multistate-ness routes it to the short form "
                    "and gets the return wrong.",
     "definition": {"rule": "R-AZ120A-ELIG", "check": "partner_in_multistate_partnership -> Form 120A refused"}},
]


class Command(BaseCommand):
    help = ("Load the Arizona corporate specs AZ_120 + AZ_120A (TY2025). "
            "Refuses to seed until Ken's Gate-1 SEED approval.")

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad Arizona corporate specs (AZ_120 + AZ_120A, TY2025)\n"))
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
                "\nREFUSING TO SEED the Arizona corporate specs: not cleared to seed.\n\n"
                "Campaign D-23 approved the Arizona walk SCOPE. That is NOT the seed gate.\n"
                "Ken must give the Gate-1 SEED approval DIRECTLY - a relayed approval never\n"
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
        self.stdout.write("Arizona corporate specs loaded (TY2025 ONLY - rate TY-keyed across 5 tiers).")
        for spec in FORMS:
            self.stdout.write(
                f"  {spec['identity']['form_number']}: facts {len(spec['facts'])} / "
                f"rules {len(spec['rules'])} / lines {len(spec['lines'])} / "
                f"diag {len(spec['diagnostics'])} / tests {len(spec['scenarios'])}")
        self.stdout.write(f"  Flow assertions: {len(FLOW_ASSERTIONS)}")
        self.stdout.write("  !! A blank apportionment ratio is NOT a zero - see R-AZ120-APPORT.")
        self.stdout.write("=" * 66)
