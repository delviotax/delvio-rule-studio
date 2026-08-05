"""Load the Form 6765 spec — Credit for Increasing Research Activities (§41).

GREENFIELD authoring 2026-08-04 (WO-14; the delvio-tax CC batch-005 #2 trigger:
packet 227's real 6765 — ASC, QREs $53,704, credit $4,243 → Schedule K — blocked
in the entity lane on the RS 404). Ken's go the same day ("run the form 6765 rule
studio spec"); Gate-1 scope walk = DECISIONS D-16.

Sources verified VERBATIM this date (f6765_source_brief.md):
  * f6765.pdf — Rev. December 2024 face (4 pp, fetched irs.gov 2026-08-04): every
    line number and rate below is read off this face (Section A 1-13, Section B
    14-26, Section C 27-32, Section D 33a-36, Section E 37-41, Section F 42-48,
    Section G 49-56).
  * i6765.pdf — Rev. December 2025 instructions (12 pp), header verbatim: "For
    use with the January 2025 revision of Form 6765". ⚠ REVISION-LABEL MISMATCH:
    irs.gov serves a face stamped Rev. 12-2024; every instruction line reference
    matches that face as extracted, so they are treated as the same structural
    revision. Re-check when IRS posts a face stamped January 2025.
  * i1120ssk.pdf — Shareholder's Instructions for Schedule K-1 (1120-S): box 13
    "Code M. Credit for increasing research activities. Report this amount on
    Section C, line 29, of Form 6765" (verbatim — the destination code).

KEN RULINGS (2026-08-04, Gate-1 scope walk, DECISIONS D-16):
  1. Line 6 fixed-base percentage = PREPARER-ENTERED (16% cap enforced; the
     §41(c)(3)(B) start-up phase-in is not computed).
  2. §280C no-election deduction reduction = DIAGNOSTIC-ONLY
     (D_6765_280C_DEDUCTION) — the engine never silently mutates a book number.
  3. Section D payroll election = DEFERRED v1 (D_6765_PAYROLL_HOLD when 33a).
  4. Item B controlled group = HOLD (D_6765_CTRL_GROUP_HOLD).

SEASON-KEYED STALENESS: Section G is OPTIONAL for tax years beginning BEFORE
2026 (i6765 "What's New" verbatim) and REQUIRED (subject to guidelines) after
2025 — D_6765_G_TY2026 flags the boundary; the v1 spec must grow Section G
facts/lines before a TY2026 season.

[UNVERIFIED] The 1065 K-1 box 15 research-credit code letter was not re-pulled
this session (the 1120-S box 13 code M IS verbatim-verified). Re-pull i1065sk1
at the app build if a partnership packet needs the destination letter.
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

READY_TO_SEED = False  # Gate 1: Ken's scope rulings are in (D-16); the SEED
# approval ("Approve — flip, seed, export") has not been given yet.

FORM_JURISDICTION = "FED"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1  # New form — lookup/6765/export/ was 404 (2026-08-04).
# The credit exists on every lane Sherpa carries; the immediate consumer is the
# 1120-S entity lane (packet 227). Destination differs by entity (R-6765-DEST).
FORM_ENTITY_TYPES = ["1120S", "1065", "1040", "1120"]
FORM_STATUS = "draft"

# Year-keyed constants (Rev. 12-2024 face; re-verify each season):
RATE_REGULAR = "0.20"          # line 13 (no §280C election)
RATE_REGULAR_280C = "0.158"    # line 13 (§280C elected)
RATE_ASC = "0.14"              # line 24 (prior-3-year QREs in all 3 years)
RATE_ASC_FIRSTYEAR = "0.06"    # line 24 (no QREs in any 1 of the prior 3)
RATE_ASC_280C = "0.79"         # line 26 multiplier (§280C elected)
FBP_CAP = "0.16"               # line 6 "but not more than 16%"
ASC_PRIOR_DIVISOR = "6.0"      # line 22 "Divide line 21 by 6.0"
PAYROLL_ELECTION_CAP = 500000  # line 34 (documented only — Section D deferred)


# ═══════════════════════════════════════════════════════════════════════════
# PURE MATH HELPERS — the validate harness calls these directly
# ═══════════════════════════════════════════════════════════════════════════

def qre_total(wages, supplies, computer_lease, contract_applicable,
              basic_research_applicable):
    """Section F: line 47 = 45 + 46; line 48 = 42 + 43 + 44 + 47."""
    line47 = contract_applicable + basic_research_applicable
    return wages + supplies + computer_lease + line47


def regular_credit(energy_consortia, basic_payments, basic_base, qres,
                   fixed_base_pct, avg_gross_receipts, elect_280c):
    """Section A lines 1-13 (Rev. 12-2024 face verbatim).

    fixed_base_pct is a DECIMAL fraction (0.05 = 5%), preparer-entered,
    capped at 0.16 (Ken D-16 #1).
    """
    line4 = max(0.0, basic_payments - basic_base)
    line6 = min(fixed_base_pct, 0.16)
    line8 = avg_gross_receipts * line6
    line9 = max(0.0, qres - line8)
    line10 = qres * 0.50
    line11 = min(line9, line10)
    line12 = energy_consortia + line4 + line11
    rate = 0.158 if elect_280c else 0.20
    return round(line12 * rate)


def asc_credit(energy_consortia, basic_payments, basic_base, qres,
               prior3_total, had_qres_all_prior3, elect_280c):
    """Section B lines 14-26 (Rev. 12-2024 face verbatim).

    had_qres_all_prior3 False ⇒ lines 22-23 skipped, line 24 = 6% × line 20
    (face: "If you had no QREs in any 1 of those years, skip lines 22 and 23").
    """
    line17 = max(0.0, basic_payments - basic_base)
    line18 = energy_consortia + line17
    line19 = line18 * 0.20
    if had_qres_all_prior3:
        line22 = prior3_total / 6.0
        line23 = max(0.0, qres - line22)
        line24 = line23 * 0.14
    else:
        line24 = qres * 0.06
    line25 = line19 + line24
    line26 = line25 * 0.79 if elect_280c else line25
    return round(line26)


def section_c_credit(section_ab_credit, overlap_8932, passthrough_in):
    """Section C: line 28 = (13|26) − 27 floor 0; line 30 = 28 + 29."""
    line28 = max(0.0, section_ab_credit - overlap_8932)
    return round(line28 + passthrough_in)


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY
# ═══════════════════════════════════════════════════════════════════════════

AUTHORITY_TOPICS: list[tuple[str, str]] = [
    ("6765", "Form 6765 — Credit for Increasing Research Activities (§41)"),
    ("research_credit", "§41 research credit — regular/ASC methods, §280C reduced-credit election, QRE definitions"),
]

EXISTING_SOURCES_TO_REFERENCE: list[str] = []

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "IRC_41",
        "source_type": "statute", "source_rank": "primary_official", "jurisdiction_code": "FED",
        "title": "IRC §41 — Credit for Increasing Research Activities",
        "citation": "26 U.S.C. §41", "issuer": "U.S. Congress",
        "official_url": "https://uscode.house.gov/view.xhtml?req=(title:26%20section:41%20edition:prelim)",
        "current_status": "active", "is_substantive_authority": True, "is_filing_authority": False,
        "trust_score": 10.0, "requires_human_review": True,
        "notes": "§41(a) 20% incremental credit over the base amount + 20% basic-research + energy-"
                 "consortium amounts; §41(c)(4) alternative simplified credit (14% of QREs over 50% of "
                 "the prior-3-year average; 6% when no QREs in any of those years); §41(c)(3)(C) 16% "
                 "fixed-base-percentage cap; §41(b)(3) contract research applicable percentages "
                 "(65%/75%/100%); §41(d) 4-part qualified-research test.",
        "topics": ["research_credit"],
        "excerpts": [
            {"excerpt_label": "§41(c)(4) — the ASC mechanics",
             "location_reference": "§41(c)(4)(A)-(B)",
             "excerpt_text": (
                 "At the election of the taxpayer, the credit determined under subsection (a)(1) shall "
                 "be equal to 14 percent of so much of the qualified research expenses for the taxable "
                 "year as exceeds 50 percent of the average qualified research expenses for the 3 "
                 "taxable years preceding the taxable year for which the credit is being determined. "
                 "In the case of a taxpayer who has no qualified research expenses in any one of the 3 "
                 "taxable years preceding the taxable year for which the credit is being determined, "
                 "the amount determined under subparagraph (A) shall be equal to 6 percent of the "
                 "qualified research expenses for the taxable year."),
             "summary_text": "ASC = 14% × (QRE − 50% of prior-3-yr average); 6% × QRE when any prior year had none. The face's ÷6.0 IS the 50%-of-3-year-average in one step.",
             "is_key_excerpt": True},
        ],
    },
    {
        "source_code": "IRC_280C_41",
        "source_type": "statute", "source_rank": "primary_official", "jurisdiction_code": "FED",
        "title": "IRC §280C(c) — research credit: deduction reduction / reduced-credit election",
        "citation": "26 U.S.C. §280C(c)", "issuer": "U.S. Congress",
        "official_url": "https://uscode.house.gov/view.xhtml?req=(title:26%20section:280C%20edition:prelim)",
        "current_status": "active", "is_substantive_authority": True, "is_filing_authority": False,
        "trust_score": 10.0, "requires_human_review": True,
        "notes": "No double benefit: absent the reduced-credit election, the §174A deduction (OBBBA "
                 "P.L. 119-21, TYs beginning after 12/31/2024) is reduced by the credit. Elected: the "
                 "credit itself is reduced (face: 15.8% regular rate / ×79% ASC — the 21% corporate "
                 "rate complement). Election on the original timely filed return only (Item A). "
                 "Ken ruling D-16 #2: diagnostic-only in the engine.",
        "topics": ["research_credit"],
        "excerpts": [],
    },
    {
        "source_code": "IRS_2024_6765_FORM",
        "source_type": "form", "source_rank": "primary_official", "jurisdiction_code": "FED",
        "title": "Form 6765 (Rev. December 2024) — Credit for Increasing Research Activities",
        "citation": "Form 6765 (Rev. 12-2024)", "issuer": "IRS",
        "official_url": "https://www.irs.gov/pub/irs-pdf/f6765.pdf",
        "current_status": "active", "is_substantive_authority": False, "is_filing_authority": True,
        "trust_score": 9.5, "requires_human_review": False,
        "notes": "Fetched + extracted line-by-line 2026-08-04. Every rate and line reference in this "
                 "spec is read off this face. ⚠ the Dec-2025 instructions self-describe as 'for use "
                 "with the January 2025 revision' — label mismatch flagged; line references verified "
                 "to match this face.",
        "topics": ["6765"],
        "excerpts": [
            {"excerpt_label": "Line 24 (ASC rate switch, verbatim)",
             "location_reference": "Form 6765 (Rev. 12-2024) lines 21-24",
             "excerpt_text": (
                 "21 Enter your total QREs for the prior 3 tax years. If you had no QREs in any 1 of "
                 "those years, skip lines 22 and 23. 22 Divide line 21 by 6.0. 23 Subtract line 22 "
                 "from line 20. If zero or less, enter -0-. 24 Multiply line 23 by 14% (0.14). If you "
                 "skipped lines 22 and 23, multiply line 20 by 6% (0.06)."),
             "summary_text": "ASC chain: L22 = prior-3 ÷ 6.0; L23 = QRE − L22 floor 0; L24 = 14% (or 6% first-year path).",
             "is_key_excerpt": True},
            {"excerpt_label": "Line 26 / line 13 (§280C arithmetic, verbatim)",
             "location_reference": "Form 6765 (Rev. 12-2024) lines 13, 26",
             "excerpt_text": (
                 "13 If you elect to reduce the credit under section 280C, then multiply line 12 by "
                 "15.8% (0.158). If not, multiply line 12 by 20% (0.20) and see instructions for the "
                 "statement that must be attached. … 26 If you elect to reduce the credit under "
                 "section 280C, then multiply line 25 by 79% (0.79). If not, enter the amount from "
                 "line 25 and see the line 13 instructions for the statement that must be attached."),
             "summary_text": "§280C elected: 15.8% regular / ×0.79 ASC. Not elected: full rate + a required statement.",
             "is_key_excerpt": True},
            {"excerpt_label": "Section C routing (verbatim)",
             "location_reference": "Form 6765 (Rev. 12-2024) line 30",
             "excerpt_text": (
                 "Partnerships and S corporations not electing the payroll tax credit, stop here and "
                 "report this amount on Schedule K. Partnerships and S corporations electing the "
                 "payroll tax credit, complete Section D and report on Schedule K the amount on this "
                 "line reduced by the amount on line 36. Eligible small businesses, stop here and "
                 "report the credit on Form 3800, Part III, line 4i. Filers other than eligible small "
                 "businesses, stop here and report the credit on Form 3800, Part III, line 1c."),
             "summary_text": "S corps/partnerships: line 30 → Schedule K (less line 36 if payroll-electing); ESB → 3800 III 4i; others → 3800 III 1c.",
             "is_key_excerpt": True},
            {"excerpt_label": "Section F line 48 (verbatim)",
             "location_reference": "Form 6765 (Rev. 12-2024) lines 42-48",
             "excerpt_text": (
                 "42 Total wages for qualified services for all business components (do not include "
                 "any wages used in figuring the work opportunity credit). 43 Total costs of supplies. "
                 "44 Total rental or lease cost of computers. 45 Total applicable amount of contract "
                 "research (do not include basic research payments). 46 Enter the applicable amount of "
                 "all basic research payments. 47 Add line 45 and line 46. 48 Add lines 42, 43, 44, "
                 "and 47, then enter line 48 on either line 5 or line 20, whichever is appropriate."),
             "summary_text": "QRE summary: 48 = 42+43+44+(45+46) → feeds line 5 (regular) or 20 (ASC).",
             "is_key_excerpt": True},
        ],
    },
    {
        "source_code": "IRS_2025_6765_INSTR",
        "source_type": "official_instruction", "source_rank": "primary_official", "jurisdiction_code": "FED",
        "title": "Instructions for Form 6765 (Rev. December 2025)",
        "citation": "i6765 (Rev. 12-2025)", "issuer": "IRS",
        "official_url": "https://www.irs.gov/pub/irs-pdf/i6765.pdf",
        "current_status": "active", "is_substantive_authority": True, "is_filing_authority": True,
        "trust_score": 9.5, "requires_human_review": False,
        "notes": "Fetched 2026-08-04 (12 pp). Self-describes as for the January 2025 face revision — "
                 "flagged; line references match the Rev. 12-2024 face in hand. Carries the OBBBA "
                 "§174A What's-New, the Section G optionality window, the ASC election/revocation "
                 "mechanics, and the §280C statement requirement.",
        "topics": ["6765", "research_credit"],
        "excerpts": [
            {"excerpt_label": "What's New — Section G optional before 2026 (verbatim)",
             "location_reference": "i6765 (12-2025), What's New",
             "excerpt_text": (
                 "For tax years beginning before 2026, Section G will be optional for all filers. … "
                 "For tax years beginning after 2025, Section G will be required, subject to the "
                 "guidelines in Section G—Business Component Information."),
             "summary_text": "TY2025: Section G optional for ALL. TY2026+: required — the spec's staleness boundary.",
             "is_key_excerpt": True},
            {"excerpt_label": "ASC election mechanics (verbatim)",
             "location_reference": "i6765 (12-2025), Specific Instructions",
             "excerpt_text": (
                 "Once elected, the ASC applies to the current tax year and all later years. A current "
                 "tax year's ASC election may not be revoked. You may revoke the election for a later "
                 "tax year by completing Section A relating to the regular credit and attaching the "
                 "Form 6765 to your timely filed (including extensions) original return for the year "
                 "to which the revocation applies. See Regulations section 1.41-9(b)(3)."),
             "summary_text": "ASC: elect by completing Section B on a timely ORIGINAL return; revoke later years via Section A. Reg. §1.41-9(b)(3).",
             "is_key_excerpt": True},
            {"excerpt_label": "Line 13 — no-election deduction reduction (verbatim)",
             "location_reference": "i6765 (12-2025), Line 13",
             "excerpt_text": (
                 "If you don't elect the reduced credit, you must reduce your domestic research or "
                 "experimental expenditures under section 174A otherwise taken into account as a "
                 "deduction or charged to a capital account by the amount of the research credit."),
             "summary_text": "§280C not elected ⇒ the §174A deduction shrinks by the credit (diagnostic-only per Ken D-16 #2).",
             "is_key_excerpt": True},
            {"excerpt_label": "Section E required when QREs reported (verbatim)",
             "location_reference": "i6765 (12-2025), Reminders",
             "excerpt_text": (
                 "If you have reported Qualified Research Expenses (QREs) on line 48, you must "
                 "complete Section E."),
             "summary_text": "Line 48 > 0 ⇒ Section E (lines 37-41) is mandatory.",
             "is_key_excerpt": True},
        ],
    },
    {
        "source_code": "IRS_I1120SSK_13M",
        "source_type": "official_instruction", "source_rank": "primary_official", "jurisdiction_code": "FED",
        "title": "Shareholder's Instructions for Schedule K-1 (Form 1120-S) — box 13 code M",
        "citation": "i1120ssk (2025)", "issuer": "IRS",
        "official_url": "https://www.irs.gov/pub/irs-pdf/i1120ssk.pdf",
        "current_status": "active", "is_substantive_authority": False, "is_filing_authority": True,
        "trust_score": 9.5, "requires_human_review": False,
        "notes": "Fetched 2026-08-04. The 1120-S destination code for the entity's research credit.",
        "topics": ["6765"],
        "excerpts": [
            {"excerpt_label": "Box 13 code M (verbatim)",
             "location_reference": "i1120ssk, box 13 codes",
             "excerpt_text": (
                 "Code M. Credit for increasing research activities. Report this amount on Section C, "
                 "line 29, of Form 6765, Credit for Increasing Research Activities, or Form 3800 (see "
                 "Tip, earlier)."),
             "summary_text": "1120-S K-1 box 13 code M = the research credit; the recipient reports it on their own 6765 line 29.",
             "is_key_excerpt": True},
        ],
    },
]

AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    ("IRS_2024_6765_FORM", "6765", "governs"),
    ("IRS_2025_6765_INSTR", "6765", "governs"),
    ("IRC_41", "6765", "governs"),
    ("IRC_280C_41", "6765", "informs"),
    ("IRS_I1120SSK_13M", "6765", "informs"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM SPEC
# ═══════════════════════════════════════════════════════════════════════════

P_IDENTITY = {
    "form_number": "6765",
    "form_title": "Form 6765 — Credit for Increasing Research Activities",
    "notes": ("§41 credit, TY2025 (Rev. 12-2024 face). v1 boundaries (Ken D-16, 2026-08-04): "
              "line 6 fixed-base % = preparer-entered (16% cap enforced; no start-up phase-in "
              "compute); §280C no-election deduction reduction = diagnostic-only; Section D "
              "payroll election = deferred (HOLD on 33a); Item B controlled group = HOLD. "
              "Section G = optional TY2025, informational only — REQUIRED for TYs beginning "
              "after 2025 (spec staleness boundary, D_6765_G_TY2026)."),
}

P_FACTS: list[dict] = [
    # Header elections
    {"fact_key": "f6765_elect_280c", "label": "Item A — electing the reduced credit under §280C?",
     "data_type": "boolean", "required": True, "sort_order": 1,
     "notes": "Made on the ORIGINAL timely filed return (incl. extensions) only. Yes → line 13 at "
              "15.8% / line 26 × 79%. No → full rate + required statement + the §174A deduction "
              "reduction (diagnostic-only, Ken D-16 #2)."},
    {"fact_key": "f6765_controlled_group", "label": "Item B — member of a controlled group or business under common control?",
     "data_type": "boolean", "default_value": "false", "sort_order": 2,
     "notes": "Yes → HOLD (D_6765_CTRL_GROUP_HOLD): the group computes as a single taxpayer and "
              "member shares ride a required attachment — out of v1 scope (Ken D-16 #4)."},
    {"fact_key": "f6765_method_asc", "label": "Method — completing Section B (ASC)? (No = Section A regular credit)",
     "data_type": "boolean", "required": True, "sort_order": 3,
     "notes": "The ASC election is MADE by completing Section B on a timely original return; it "
              "applies to the current year and all later years (irrevocable currently; revoke later "
              "years via Section A — Reg. §1.41-9(b)(3))."},
    # Shared credit-base inputs (Section A lines 1-3 = Section B lines 14-16)
    {"fact_key": "f6765_energy_consortia", "label": "Line 1/14 — amounts paid to energy consortia",
     "data_type": "decimal", "default_value": "0", "sort_order": 10},
    {"fact_key": "f6765_basic_research_payments", "label": "Line 2/15 — basic research payments to qualified organizations",
     "data_type": "decimal", "default_value": "0", "sort_order": 11,
     "notes": "Corporations (other than S corps, personal holding companies, and service organizations) only — see §41(e)."},
    {"fact_key": "f6765_basic_research_base", "label": "Line 3/16 — qualified organization base period amount",
     "data_type": "decimal", "default_value": "0", "sort_order": 12},
    # Section A (regular credit)
    {"fact_key": "f6765_fixed_base_pct", "label": "Line 6 — fixed-base percentage (DECIMAL fraction; max 0.16) — PREPARER-ENTERED",
     "data_type": "decimal", "sort_order": 20,
     "notes": "Ken D-16 #1: entered from the prior-year 6765/workpapers; the §41(c)(3)(B) start-up "
              "phase-in is not computed. The spec enforces the §41(c)(3)(C) 16% cap."},
    {"fact_key": "f6765_avg_gross_receipts", "label": "Line 7 — average annual gross receipts (4 prior tax years)",
     "data_type": "decimal", "sort_order": 21,
     "notes": "Annualize short years; new taxpayers see the i6765 line-7 rules (prorations on "
              "S-election/termination years)."},
    # Section B (ASC)
    {"fact_key": "f6765_prior3_qres_total", "label": "Line 21 — TOTAL QREs for the prior 3 tax years",
     "data_type": "decimal", "default_value": "0", "sort_order": 30,
     "notes": "The face divides by 6.0 (= 50% of the 3-year average in one step, §41(c)(4))."},
    {"fact_key": "f6765_had_qres_all_prior3", "label": "Had QREs in EACH of the prior 3 tax years?",
     "data_type": "boolean", "sort_order": 31,
     "notes": "No → skip lines 22-23; line 24 = 6% × line 20 (face verbatim). Required when Section B "
              "is completed."},
    # Section C
    {"fact_key": "f6765_8932_overlap", "label": "Line 27 — Form 8932 credit portion attributable to the same wages",
     "data_type": "decimal", "default_value": "0", "sort_order": 40},
    {"fact_key": "f6765_passthrough_credit", "label": "Line 29 — research credit from partnerships, S corporations, estates, trusts",
     "data_type": "decimal", "default_value": "0", "sort_order": 41,
     "notes": "K-1 (1120-S) box 13 code M (i1120ssk verbatim); [UNVERIFIED] the 1065 box-15 letter — re-pull i1065sk1 at the app build."},
    # Section D (deferred)
    {"fact_key": "f6765_payroll_election", "label": "Line 33a — qualified small business electing the payroll tax credit?",
     "data_type": "boolean", "default_value": "false", "sort_order": 50,
     "notes": "DEFERRED v1 (Ken D-16 #3): checking this raises D_6765_PAYROLL_HOLD. $500,000 line-34 "
              "cap and the Form 8974 interplay are documented, not computed."},
    # Section E
    {"fact_key": "f6765_business_component_count", "label": "Line 37 — number of business components generating the QREs",
     "data_type": "integer", "sort_order": 60,
     "notes": "Section E is REQUIRED whenever line 48 reports QREs (i6765 Reminders verbatim)."},
    {"fact_key": "f6765_officer_wages_in_qres", "label": "Line 38 — officers' wages included in line 42",
     "data_type": "decimal", "default_value": "0", "sort_order": 61},
    {"fact_key": "f6765_acquired_disposed", "label": "Line 39 — acquired or disposed of a major portion of a trade/business this year?",
     "data_type": "boolean", "default_value": "false", "sort_order": 62},
    {"fact_key": "f6765_new_categories", "label": "Line 40 — any new categories of expenses in current-year QREs?",
     "data_type": "boolean", "default_value": "false", "sort_order": 63},
    {"fact_key": "f6765_asc730", "label": "Line 41 — QREs determined under the ASC 730 Directive?",
     "data_type": "boolean", "default_value": "false", "sort_order": 64,
     "notes": "≥$10M assets + GAAP certified audited financials only."},
    {"fact_key": "f6765_asc730_amount", "label": "Line 41 — Appendix C line 19 amount (if ASC 730 Yes)",
     "data_type": "decimal", "default_value": "0", "sort_order": 65},
    # Section F (the QRE summary — feeds line 5 / line 20)
    {"fact_key": "f6765_qre_wages", "label": "Line 42 — total wages for qualified services",
     "data_type": "decimal", "default_value": "0", "sort_order": 70,
     "notes": "EXCLUDES wages used for the work opportunity credit (face verbatim)."},
    {"fact_key": "f6765_qre_supplies", "label": "Line 43 — total costs of supplies",
     "data_type": "decimal", "default_value": "0", "sort_order": 71},
    {"fact_key": "f6765_qre_computer_lease", "label": "Line 44 — total rental or lease cost of computers",
     "data_type": "decimal", "default_value": "0", "sort_order": 72},
    {"fact_key": "f6765_qre_contract_research", "label": "Line 45 — total APPLICABLE amount of contract research",
     "data_type": "decimal", "default_value": "0", "sort_order": 73,
     "notes": "Enter the amount AFTER the §41(b)(3) applicable percentage (generally 65%; 75% "
              "qualified research consortia; 100% certain small-business/university/federal-lab "
              "payments). D_6765_CONTRACT_65 reminds. Excludes basic research payments."},
    {"fact_key": "f6765_qre_basic_research_applicable", "label": "Line 46 — applicable amount of all basic research payments",
     "data_type": "decimal", "default_value": "0", "sort_order": 74},
]

P_RULES: list[dict] = [
    {"rule_id": "R-6765-METHOD", "title": "Method selection — Section A (regular) vs Section B (ASC)",
     "rule_type": "classification", "precedence": 1, "sort_order": 1,
     "formula": ("f6765_method_asc → complete Section B only (skip A); else Section A only (skip B). "
                 "Amounts in BOTH sections = error (D_6765_BOTH_METHODS)."),
     "inputs": ["f6765_method_asc"], "outputs": [],
     "description": ("Face verbatim: 'Skip this section and go to Section B if you are electing or "
                     "previously elected (and are not revoking) the alternative simplified credit.' "
                     "The ASC election is made by completing Section B on a timely ORIGINAL return; "
                     "current-year ASC may not be revoked; later-year revocation = complete Section A "
                     "(Reg. §1.41-9(b)(3))."),
    },
    {"rule_id": "R-6765-QRESUM", "title": "Section F — QRE summary (lines 42-48 → 5/20)",
     "rule_type": "calculation", "precedence": 2, "sort_order": 2,
     "formula": "L47 = L45 + L46; L48 = L42 + L43 + L44 + L47; L5 (regular) or L20 (ASC) = L48.",
     "inputs": ["f6765_qre_wages", "f6765_qre_supplies", "f6765_qre_computer_lease",
                "f6765_qre_contract_research", "f6765_qre_basic_research_applicable"],
     "outputs": [],
     "description": ("Face verbatim. Line 45 carries the amount AFTER the §41(b)(3) applicable "
                     "percentage (65%/75%/100%) — preparer-applied, D_6765_CONTRACT_65 reminds. "
                     "Line 48 > 0 makes Section E mandatory (R-6765-SECTE)."),
    },
    {"rule_id": "R-6765-REG", "title": "Section A — regular credit (lines 1-13)",
     "rule_type": "calculation", "precedence": 3, "sort_order": 3,
     "formula": ("L4 = max(0, L2 − L3); L6 = min(fixed_base_pct, 0.16); L8 = L7 × L6; "
                 "L9 = max(0, L5 − L8); L10 = L5 × 0.50; L11 = min(L9, L10); L12 = L1 + L4 + L11; "
                 "L13 = L12 × (0.158 if §280C elected else 0.20)."),
     "inputs": ["f6765_energy_consortia", "f6765_basic_research_payments", "f6765_basic_research_base",
                "f6765_fixed_base_pct", "f6765_avg_gross_receipts", "f6765_elect_280c"],
     "outputs": [],
     "description": ("Face verbatim, lines 1-13. The line-10 50%-of-QREs limit is §41(c)(2) (base "
                     "amount ≥ 50% of QREs, expressed on the face as the smaller-of). Fixed-base % "
                     "preparer-entered per Ken D-16 #1; the 16% cap is §41(c)(3)(C)."),
    },
    {"rule_id": "R-6765-ASC", "title": "Section B — alternative simplified credit (lines 14-26)",
     "rule_type": "calculation", "precedence": 4, "sort_order": 4,
     "formula": ("L17 = max(0, L15 − L16); L18 = L14 + L17; L19 = L18 × 0.20; "
                 "if had QREs in all prior 3 years: L22 = L21 ÷ 6.0; L23 = max(0, L20 − L22); "
                 "L24 = L23 × 0.14; else (skip 22-23): L24 = L20 × 0.06; "
                 "L25 = L19 + L24; L26 = L25 × 0.79 if §280C elected else L25."),
     "inputs": ["f6765_energy_consortia", "f6765_basic_research_payments", "f6765_basic_research_base",
                "f6765_prior3_qres_total", "f6765_had_qres_all_prior3", "f6765_elect_280c"],
     "outputs": [],
     "description": ("Face verbatim, lines 14-26; §41(c)(4) verbatim in the IRC_41 excerpt (÷6.0 IS "
                     "the 50%-of-3-year-average in one step). The 6% path engages when the taxpayer "
                     "had NO QREs in ANY ONE of the prior 3 years."),
    },
    {"rule_id": "R-6765-280C", "title": "§280C — reduced-credit election / deduction reduction (diagnostic-only v1)",
     "rule_type": "validation", "precedence": 5, "sort_order": 5,
     "formula": ("Item A elected → the 15.8%/×0.79 arithmetic in R-6765-REG/ASC. NOT elected → the "
                 "§174A research deduction must be reduced by the credit AND a statement attached — "
                 "VERIFIED BY DIAGNOSTIC (D_6765_280C_DEDUCTION), never auto-adjusted."),
     "inputs": ["f6765_elect_280c"], "outputs": [],
     "description": ("i6765 line-13 verbatim (the §174A-era text, OBBBA P.L. 119-21). Ken D-16 #2: "
                     "the preparer enters the already-reduced deduction; the engine flags, never "
                     "silently mutates a book number (the 8941 D_8941_004 precedent — on an 1120-S "
                     "this touches page 1, M-1, and AAA)."),
    },
    {"rule_id": "R-6765-DEST", "title": "Section C — current-year credit and entity routing (lines 27-30)",
     "rule_type": "routing", "precedence": 6, "sort_order": 6,
     "formula": ("L28 = max(0, (L13 or L26) − L27); L30 = L28 + L29. "
                 "1120-S/1065 (no payroll election): STOP — L30 → Schedule K "
                 "(1120-S: Schedule K line 13g other credits, K-1 box 13 CODE M; 1065: Schedule K "
                 "line 15, K-1 box 15 [UNVERIFIED letter]). ESB → Form 3800 Part III 4i; "
                 "others → 3800 Part III 1c. Estates/trusts: L31/L32 — OUT OF v1 (D_6765_TRUST_HOLD)."),
     "inputs": ["f6765_8932_overlap", "f6765_passthrough_credit", "f6765_payroll_election"],
     "outputs": [],
     "description": ("Face Section-C routing text verbatim (the IRS_2024_6765_FORM excerpt). The "
                     "1120-S destination code M is i1120ssk-verbatim. ⚠ APP NOTE: delvio-tax's K13g "
                     "is currently written by Form 8941 — the app build must COMPOSE 8941 + 6765 "
                     "into the Schedule K other-credits family, not stomp."),
    },
    {"rule_id": "R-6765-SECTE", "title": "Section E — required when line 48 reports QREs",
     "rule_type": "validation", "precedence": 7, "sort_order": 7,
     "formula": "L48 > 0 → lines 37-41 must be answered (D_6765_SECTION_E).",
     "inputs": ["f6765_business_component_count", "f6765_officer_wages_in_qres",
                "f6765_acquired_disposed", "f6765_new_categories", "f6765_asc730"],
     "outputs": [],
     "description": "i6765 Reminders verbatim: 'If you have reported Qualified Research Expenses (QREs) on line 48, you must complete Section E.'",
    },
]

P_LINES: list[dict] = [
    {"line_number": "A", "description": "Item A — electing the reduced credit under §280C? (original timely filed return only)", "line_type": "input", "source_facts": ["f6765_elect_280c"], "source_rules": ["R-6765-280C"]},
    {"line_number": "B", "description": "Item B — controlled group / common control? Yes → required statement (v1 HOLD)", "line_type": "input", "source_facts": ["f6765_controlled_group"]},
    # Section A
    {"line_number": "1", "description": "Energy consortia amounts", "line_type": "input", "source_facts": ["f6765_energy_consortia"]},
    {"line_number": "2", "description": "Basic research payments to qualified organizations", "line_type": "input", "source_facts": ["f6765_basic_research_payments"]},
    {"line_number": "3", "description": "Qualified organization base period amount", "line_type": "input", "source_facts": ["f6765_basic_research_base"]},
    {"line_number": "4", "description": "Line 2 − line 3 (floor 0)", "line_type": "calculated", "source_rules": ["R-6765-REG"]},
    {"line_number": "5", "description": "Total QREs — from line 48 (complete Section F first)", "line_type": "calculated", "source_rules": ["R-6765-QRESUM"]},
    {"line_number": "6", "description": "Fixed-base percentage (max 16%) — preparer-entered (Ken D-16 #1)", "line_type": "input", "source_facts": ["f6765_fixed_base_pct"], "source_rules": ["R-6765-REG"]},
    {"line_number": "7", "description": "Average annual gross receipts (prior 4 years)", "line_type": "input", "source_facts": ["f6765_avg_gross_receipts"]},
    {"line_number": "8", "description": "Line 7 × line 6", "line_type": "calculated", "source_rules": ["R-6765-REG"]},
    {"line_number": "9", "description": "Line 5 − line 8 (floor 0)", "line_type": "calculated", "source_rules": ["R-6765-REG"]},
    {"line_number": "10", "description": "Line 5 × 50%", "line_type": "calculated", "source_rules": ["R-6765-REG"]},
    {"line_number": "11", "description": "Smaller of line 9 or line 10", "line_type": "calculated", "source_rules": ["R-6765-REG"]},
    {"line_number": "12", "description": "Add lines 1, 4, and 11", "line_type": "subtotal", "source_rules": ["R-6765-REG"]},
    {"line_number": "13", "description": "Line 12 × 15.8% (§280C elected) or × 20% (+ required statement)", "line_type": "total", "source_rules": ["R-6765-REG", "R-6765-280C"]},
    # Section B
    {"line_number": "14", "description": "Energy consortia amounts (ASC)", "line_type": "input", "source_facts": ["f6765_energy_consortia"]},
    {"line_number": "15", "description": "Basic research payments (ASC)", "line_type": "input", "source_facts": ["f6765_basic_research_payments"]},
    {"line_number": "16", "description": "Qualified organization base period amount (ASC)", "line_type": "input", "source_facts": ["f6765_basic_research_base"]},
    {"line_number": "17", "description": "Line 15 − line 16 (floor 0)", "line_type": "calculated", "source_rules": ["R-6765-ASC"]},
    {"line_number": "18", "description": "Add lines 14 and 17", "line_type": "calculated", "source_rules": ["R-6765-ASC"]},
    {"line_number": "19", "description": "Line 18 × 20%", "line_type": "calculated", "source_rules": ["R-6765-ASC"]},
    {"line_number": "20", "description": "Total QREs — from line 48 (complete Section F first)", "line_type": "calculated", "source_rules": ["R-6765-QRESUM"]},
    {"line_number": "21", "description": "Total QREs for the prior 3 tax years (skip 22-23 if any year had none)", "line_type": "input", "source_facts": ["f6765_prior3_qres_total", "f6765_had_qres_all_prior3"]},
    {"line_number": "22", "description": "Line 21 ÷ 6.0", "line_type": "calculated", "source_rules": ["R-6765-ASC"]},
    {"line_number": "23", "description": "Line 20 − line 22 (floor 0)", "line_type": "calculated", "source_rules": ["R-6765-ASC"]},
    {"line_number": "24", "description": "Line 23 × 14% — or line 20 × 6% if lines 22-23 were skipped", "line_type": "calculated", "source_rules": ["R-6765-ASC"]},
    {"line_number": "25", "description": "Add lines 19 and 24", "line_type": "subtotal", "source_rules": ["R-6765-ASC"]},
    {"line_number": "26", "description": "Line 25 × 79% (§280C elected) or line 25 (+ required statement)", "line_type": "total", "source_rules": ["R-6765-ASC", "R-6765-280C"]},
    # Section C
    {"line_number": "27", "description": "Form 8932 credit portion on the same wages", "line_type": "input", "source_facts": ["f6765_8932_overlap"]},
    {"line_number": "28", "description": "(Line 13 or 26) − line 27 (floor 0)", "line_type": "calculated", "source_rules": ["R-6765-DEST"]},
    {"line_number": "29", "description": "Research credit from partnerships, S corporations, estates, trusts (1120-S K-1 box 13 code M)", "line_type": "input", "source_facts": ["f6765_passthrough_credit"]},
    {"line_number": "30", "description": "Add lines 28 and 29. Partnerships/S corps (no payroll election): STOP → Schedule K (1120-S 13g code M / 1065 15). ESB → 3800 III 4i; others → 3800 III 1c", "line_type": "total", "source_rules": ["R-6765-DEST"], "destination_form": "1120-S Schedule K line 13g (K-1 box 13 code M) / 1065 Schedule K line 15 / Form 3800 Part III 4i or 1c"},
    {"line_number": "31", "description": "Amount allocated to estate/trust beneficiaries — OUT OF v1 (D_6765_TRUST_HOLD)", "line_type": "informational"},
    {"line_number": "32", "description": "Estates/trusts: line 30 − line 31 → Form 3800 — OUT OF v1", "line_type": "informational"},
    # Section D (deferred)
    {"line_number": "33a", "description": "QSB payroll tax election checkbox — DEFERRED v1 (D_6765_PAYROLL_HOLD)", "line_type": "input", "source_facts": ["f6765_payroll_election"]},
    {"line_number": "34", "description": "Portion elected as payroll tax credit (≤ $500,000) — deferred", "line_type": "informational"},
    {"line_number": "36", "description": "Smaller of line 28 or 34 → Form 8974; Schedule K carries line 30 − line 36 — deferred", "line_type": "informational"},
    # Section E
    {"line_number": "37", "description": "Number of business components generating the QREs", "line_type": "input", "source_facts": ["f6765_business_component_count"], "source_rules": ["R-6765-SECTE"]},
    {"line_number": "38", "description": "Officers' wages included in line 42", "line_type": "input", "source_facts": ["f6765_officer_wages_in_qres"]},
    {"line_number": "39", "description": "Acquired/disposed of a major portion of a trade or business?", "line_type": "input", "source_facts": ["f6765_acquired_disposed"]},
    {"line_number": "40", "description": "New categories of expenses in current-year QREs?", "line_type": "input", "source_facts": ["f6765_new_categories"]},
    {"line_number": "41", "description": "ASC 730 Directive (≥$10M assets, GAAP audited) + Appendix C line 19 amount", "line_type": "input", "source_facts": ["f6765_asc730", "f6765_asc730_amount"]},
    # Section F
    {"line_number": "42", "description": "Total wages for qualified services (excl. WOTC wages)", "line_type": "input", "source_facts": ["f6765_qre_wages"]},
    {"line_number": "43", "description": "Total costs of supplies", "line_type": "input", "source_facts": ["f6765_qre_supplies"]},
    {"line_number": "44", "description": "Total rental or lease cost of computers", "line_type": "input", "source_facts": ["f6765_qre_computer_lease"]},
    {"line_number": "45", "description": "Total APPLICABLE contract research (§41(b)(3) 65%/75%/100% already applied)", "line_type": "input", "source_facts": ["f6765_qre_contract_research"]},
    {"line_number": "46", "description": "Applicable amount of basic research payments", "line_type": "input", "source_facts": ["f6765_qre_basic_research_applicable"]},
    {"line_number": "47", "description": "Add lines 45 and 46", "line_type": "subtotal", "source_rules": ["R-6765-QRESUM"]},
    {"line_number": "48", "description": "Add lines 42, 43, 44, and 47 → line 5 or line 20", "line_type": "total", "source_rules": ["R-6765-QRESUM"]},
    # Section G (optional TY2025)
    {"line_number": "49-56", "description": "Section G — business component detail (49a-f identity/type, 50-56 per-component QREs). OPTIONAL for TYs beginning before 2026; REQUIRED after 2025 — out of v1 scope (D_6765_G_TY2026)", "line_type": "informational"},
]

P_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_6765_BOTH_METHODS", "title": "Section A and Section B both carry amounts", "severity": "error",
     "condition": "Section A lines (5-13) nonzero AND Section B lines (20-26) nonzero",
     "message": "Form 6765 computes ONE method: the regular credit (Section A) or the ASC (Section B) — the face says to skip the other. Clear the section that does not apply."},
    {"diagnostic_id": "D_6765_CTRL_GROUP_HOLD", "title": "Controlled group — v1 HOLD", "severity": "error",
     "condition": "f6765_controlled_group == true",
     "message": "Item B is Yes: the research credit is computed at the GROUP level (single-taxpayer rule) with member shares on a required attachment — not modeled in v1 (Ken D-16 #4). Hold the return; compute the member share outside and escalate."},
    {"diagnostic_id": "D_6765_PAYROLL_HOLD", "title": "Payroll tax election — Section D deferred", "severity": "error",
     "condition": "f6765_payroll_election == true",
     "message": "Box 33a is checked: the qualified-small-business payroll tax election (Section D, $500,000 cap, Form 8974) is deferred in v1 (Ken D-16 #3). Hold the return until the Section D unit is built."},
    {"diagnostic_id": "D_6765_TRUST_HOLD", "title": "Estate/trust beneficiary allocation — out of v1", "severity": "error",
     "condition": "filer is an estate or trust AND line 30 > 0",
     "message": "Line 31 (allocation to beneficiaries) is not modeled in v1 — hold estate/trust 6765 returns."},
    {"diagnostic_id": "D_6765_280C_DEDUCTION", "title": "§280C not elected — reduce the §174A deduction + attach the statement", "severity": "warning",
     "condition": "credit (line 13/26) > 0 AND f6765_elect_280c == false",
     "message": "The reduced credit was NOT elected: the §174A research deduction must be REDUCED by the credit and the required statement attached (i6765 line 13). Confirm the research expense entered is already net of the credit — the engine never adjusts it automatically (Ken D-16 #2). On an 1120-S this moves page 1, M-1, and AAA."},
    {"diagnostic_id": "D_6765_SECTION_E", "title": "Section E incomplete with QREs on line 48", "severity": "warning",
     "condition": "line 48 > 0 AND f6765_business_component_count blank",
     "message": "Line 48 reports QREs — Section E (lines 37-41) is mandatory (i6765 Reminders). Enter the business-component count, officers' wages included, and the three Yes/No answers."},
    {"diagnostic_id": "D_6765_FBP_RANGE", "title": "Fixed-base percentage out of range", "severity": "error",
     "condition": "Section A completed AND (f6765_fixed_base_pct <= 0 OR f6765_fixed_base_pct > 0.16)",
     "message": "Line 6 must be a decimal fraction above zero and not more than 16% (0.16) — §41(c)(3)(C). Enter it from the prior-year Form 6765 or the fixed-base workpapers."},
    {"diagnostic_id": "D_6765_ASC_PRIOR_MISMATCH", "title": "ASC prior-year facts inconsistent", "severity": "warning",
     "condition": "f6765_had_qres_all_prior3 == true AND f6765_prior3_qres_total == 0",
     "message": "'Had QREs in each of the prior 3 years' is Yes but line 21 is zero — either enter the prior-3-year QRE total or answer No (which switches line 24 to the 6% first-year path)."},
    {"diagnostic_id": "D_6765_CONTRACT_65", "title": "Line 45 is the post-§41(b)(3) applicable amount", "severity": "info",
     "condition": "f6765_qre_contract_research > 0",
     "message": "Line 45 must already reflect the §41(b)(3) applicable percentage — generally 65% of contract research (75% qualified research consortia; 100% certain small-business/university/federal-lab payments). Enter the applicable amount, not the gross contract cost."},
    {"diagnostic_id": "D_6765_G_TY2026", "title": "Section G becomes required after 2025", "severity": "info",
     "condition": "tax year begins after 2025-12-31",
     "message": "Section G (business component detail) is REQUIRED for tax years beginning after 2025 (i6765 What's New) and is not modeled in this spec version — the 6765 spec must be re-authored before a TY2026 season."},
]

P_SCENARIOS: list[dict] = [
    {"scenario_name": "F6765-T1 — packet 227 shape: ASC, no §280C (INFERRED priors)",
     "scenario_type": "normal", "sort_order": 1,
     "inputs": {"method_asc": True, "elect_280c": False, "qre_wages": 53704,
                "prior3_qres_total": 140382, "had_qres_all_prior3": True,
                "energy_consortia": 0, "basic_research_payments": 0,
                "8932_overlap": 0, "passthrough_credit": 0},
     "expected_outputs": {"line20": 53704, "line22": 23397, "line23": 30307,
                          "line24": 4243, "line25": 4243, "line26": 4243,
                          "line28": 4243, "line30": 4243,
                          "destination": "1120-S Schedule K (K-1 box 13 code M)"},
     "notes": ("Production packet 227 (GOLD FUSION PROMOTIONS LLC): QREs 53,704 → credit 4,243. "
               "⚠ line 21 = 140,382 is INFERRED from the credit (4,243 ÷ 0.14 = 30,307 = L23 ⇒ "
               "L22 = 23,397 ⇒ L21 = 140,382); the REAL prior-year QREs come off the packet's "
               "printed Section B at authoring. The Section F split (all-wages here) is likewise "
               "shape-only. 14% × 30,307 = 4,242.98 → 4,243 whole-dollar.")},
    {"scenario_name": "F6765-T2 — ASC first-year 6% path (no QREs in one of the prior 3)",
     "scenario_type": "normal", "sort_order": 2,
     "inputs": {"method_asc": True, "elect_280c": False, "qre_wages": 53704,
                "had_qres_all_prior3": False, "prior3_qres_total": 0},
     "expected_outputs": {"line24": 3222, "line26": 3222},
     "notes": "Face verbatim: lines 22-23 skipped; 6% × 53,704 = 3,222.24 → 3,222."},
    {"scenario_name": "F6765-T3 — regular credit with the §280C 15.8% rate",
     "scenario_type": "normal", "sort_order": 3,
     "inputs": {"method_asc": False, "elect_280c": True, "qre_total": 250000,
                "fixed_base_pct": 0.05, "avg_gross_receipts": 2000000,
                "energy_consortia": 0, "basic_research_payments": 0},
     "expected_outputs": {"line8": 100000, "line9": 150000, "line10": 125000,
                          "line11": 125000, "line12": 125000, "line13": 19750},
     "notes": "L8 = 2,000,000 × 5% = 100,000; L9 = 150,000; the L10 50% limit binds (125,000); L13 = 125,000 × 0.158 = 19,750."},
    {"scenario_name": "F6765-T4 — ASC with the §280C ×79% reduction",
     "scenario_type": "normal", "sort_order": 4,
     "inputs": {"method_asc": True, "elect_280c": True, "qre_wages": 53704,
                "prior3_qres_total": 140382, "had_qres_all_prior3": True},
     "expected_outputs": {"line25": 4243, "line26": 3352},
     "notes": "4,243 × 0.79 = 3,351.97 → 3,352. D_6765_280C_DEDUCTION does NOT fire (elected)."},
    {"scenario_name": "F6765-T5 — 8932 overlap and pass-through credits compose in Section C",
     "scenario_type": "edge", "sort_order": 5,
     "inputs": {"method_asc": True, "elect_280c": False, "qre_wages": 53704,
                "prior3_qres_total": 140382, "had_qres_all_prior3": True,
                "8932_overlap": 500, "passthrough_credit": 1000},
     "expected_outputs": {"line26": 4243, "line28": 3743, "line30": 4743},
     "notes": "L28 = 4,243 − 500 = 3,743; L30 = 3,743 + 1,000 = 4,743 → Schedule K."},
    {"scenario_name": "F6765-T6 — fixed-base cap and the 50%-of-QREs limit",
     "scenario_type": "edge", "sort_order": 6,
     "inputs": {"method_asc": False, "elect_280c": False, "qre_total": 100000,
                "fixed_base_pct": 0.03, "avg_gross_receipts": 200000},
     "expected_outputs": {"line8": 6000, "line9": 94000, "line10": 50000,
                          "line11": 50000, "line13": 10000},
     "notes": ("The §41(c)(2) floor as the face expresses it: L11 = min(94,000, 50,000) = 50,000; "
               "L13 = 50,000 × 20% = 10,000. A pct keyed above 0.16 caps to 16% (D_6765_FBP_RANGE "
               "errors the entry)."),
    },
]

P_RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R-6765-METHOD", "IRS_2024_6765_FORM", "primary", "Section A/B skip text verbatim"),
    ("R-6765-METHOD", "IRS_2025_6765_INSTR", "secondary", "ASC election/revocation mechanics; Reg. §1.41-9(b)(3)"),
    ("R-6765-QRESUM", "IRS_2024_6765_FORM", "primary", "Lines 42-48 verbatim (the Section F excerpt)"),
    ("R-6765-QRESUM", "IRC_41", "secondary", "§41(b) QRE definitions; §41(b)(3) contract-research applicable percentage"),
    ("R-6765-REG", "IRS_2024_6765_FORM", "primary", "Lines 1-13; the 16% cap and 15.8%/20% rates on the face"),
    ("R-6765-REG", "IRC_41", "secondary", "§41(a), §41(c)(2) 50% base floor, §41(c)(3)(C) 16% cap"),
    ("R-6765-ASC", "IRS_2024_6765_FORM", "primary", "Lines 14-26 verbatim (the line-24 rate-switch excerpt)"),
    ("R-6765-ASC", "IRC_41", "primary", "§41(c)(4) verbatim excerpt — 14%/6% and the 50%-of-average base"),
    ("R-6765-280C", "IRS_2025_6765_INSTR", "primary", "Line 13 §174A deduction-reduction text verbatim"),
    ("R-6765-280C", "IRC_280C_41", "secondary", "§280C(c) no-double-benefit / reduced-credit election"),
    ("R-6765-DEST", "IRS_2024_6765_FORM", "primary", "Section C routing text verbatim"),
    ("R-6765-DEST", "IRS_I1120SSK_13M", "secondary", "K-1 box 13 code M verbatim (the 1120-S destination)"),
    ("R-6765-SECTE", "IRS_2025_6765_INSTR", "primary", "Reminders: Section E required when line 48 carries QREs"),
]

FLOW_ASSERTIONS: list[dict] = [
    # DRAFT until the delvio-tax 6765 unit lands (the app build is Gate-2-gated;
    # flip to active with that build, the 8941 precedent).
    {"assertion_id": "FA-6765-01", "assertion_type": "reconciliation",
     "entity_types": ["1120S", "1065", "1040", "1120"], "status": "draft",
     "title": "Credit chains: ASC L22=L21/6; L23=max(0,L20−L22); L24=14%/6% switch; L26=×0.79 iff 280C. Regular L11=min(L9, L5×50%); L13=15.8%/20%.",
     "description": ("Validates R-6765-REG/ASC/280C. Bugs it catches: dividing by 3 instead of 6 "
                     "(averaging without the 50%), applying 14% on the first-year path, taking 79% "
                     "without the Item A election, missing the L10 50% limit."),
     "definition": {"kind": "reconciliation", "form": "6765",
                    "formula": ("ASC: L22=L21/6.0; L23=max(0,L20-L22); L24=(L23*0.14 if all-3-prior "
                                "else L20*0.06); L25=L19+L24; L26=L25*(0.79 if 280c else 1). "
                                "REG: L11=min(max(0,L5-L7*min(FBP,0.16)), L5*0.5); L12=L1+L4+L11; "
                                "L13=L12*(0.158 if 280c else 0.20)")},
     "sort_order": 1},
    {"assertion_id": "FA-6765-02", "assertion_type": "flow_assertion",
     "entity_types": ["1120S"], "status": "draft",
     "title": "1120-S: line 30 → Schedule K other credits (13g family) → K-1 box 13 code M (Σ owners == entity)",
     "description": ("Validates R-6765-DEST on the S-corp lane. Bug it catches: the credit reaching "
                     "Form 3800 at entity level, stomping the 8941-written K13g instead of composing, "
                     "or the K-1 code-M split not reconciling to the entity total."),
     "definition": {"kind": "flow_assertion", "form": "6765",
                    "checks": [{"source_line": "30", "must_write_to": ["SCH_K_1120S.13g"],
                                "note": "COMPOSE with Form 8941's 13g write — never stomp"}]},
     "sort_order": 2},
]


class Command(BaseCommand):
    help = "Load the Form 6765 spec (§41 credit for increasing research activities)."

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING("\nLoad Form 6765 spec (§41 research credit)\n"))
        self._load_topics()
        sources = self._load_sources()
        form = self._upsert_form(P_IDENTITY)
        self._upsert_facts(form, P_FACTS)
        rules = self._upsert_rules(form, P_RULES)
        self._upsert_authority_links(rules, sources, P_RULE_LINKS)
        self._upsert_lines(form, P_LINES)
        self._upsert_diagnostics(form, P_DIAGNOSTICS)
        self._upsert_tests(form, P_SCENARIOS)
        self._upsert_form_links(sources)
        self._load_flow_assertions()
        self._report_totals()

    def _guard_against_hollow_seed(self):
        empty = [name for name, block in [
            ("P_FACTS", P_FACTS), ("P_RULES", P_RULES), ("P_LINES", P_LINES),
            ("P_DIAGNOSTICS", P_DIAGNOSTICS), ("P_SCENARIOS", P_SCENARIOS),
            ("P_RULE_LINKS", P_RULE_LINKS), ("FLOW_ASSERTIONS", FLOW_ASSERTIONS),
        ] if not block]
        if not READY_TO_SEED or empty:
            still_empty = "\n  ".join(f"- {n}" for n in empty) or "(all populated)"
            raise CommandError(
                f"\nREFUSING TO SEED Form 6765.\nREADY_TO_SEED = {READY_TO_SEED}\n"
                f"Empty blocks:\n  {still_empty}\n")

    def _load_topics(self):
        for code, name in AUTHORITY_TOPICS:
            AuthorityTopic.objects.update_or_create(topic_code=code, defaults={"topic_name": name})
        self.stdout.write(f"Topics: {len(AUTHORITY_TOPICS)} in batch")

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

    def _upsert_form(self, identity: dict) -> TaxForm:
        form, created = TaxForm.objects.update_or_create(
            form_number=identity["form_number"], jurisdiction=FORM_JURISDICTION,
            tax_year=FORM_TAX_YEAR, version=FORM_VERSION,
            defaults={"form_title": identity["form_title"], "entity_types": FORM_ENTITY_TYPES,
                      "status": FORM_STATUS, "notes": identity["notes"]})
        self.stdout.write(f"{'Created' if created else 'Updated'} Form {identity['form_number']}")
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
        self.stdout.write(f"  {len(FLOW_ASSERTIONS)} flow assertions (draft until the app unit lands)")

    def _report_totals(self):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"TaxForms: {TaxForm.objects.count()} | FlowAssertions: {FlowAssertion.objects.count()}")
        form = TaxForm.objects.filter(form_number="6765").order_by("-version").first()
        if form:
            uncited = [r for r in FormRule.objects.filter(tax_form=form) if not r.authority_links.exists()]
            self.stdout.write("Form 6765: all rules cited" if not uncited
                              else f"⚠ UNCITED RULES: {[r.rule_id for r in uncited]}")
