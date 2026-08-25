"""Load the Louisiana pass-through specs — IT-565 + CIT-620 (TY2025).

Campaign `WO-W06-LA-PILOT` (delvio-states D-14/D-15/D-16). Wave 6, the
PILOT-DEMAND wave: Codex's ten-return TY2025 1065 back-entry pilot needs
Louisiana.

═══════════════════════════════════════════════════════════════════════════
⚠⚠ LOUISIANA BREAKS THE PAIRED-PTE-WAVE TEMPLATE — READ THIS FIRST
═══════════════════════════════════════════════════════════════════════════
There is **NO S-corporation return** and **NO PTE-specific return**. Three
tracks across two forms (verified, statute-grounded — see
delvio-states research/la_pte_source_brief.md §2, VERIFIED 2026-08-22):

  1. NON-ELECTING PARTNERSHIP -> **IT-565**, an INFORMATIONAL return
     (R.S. 47:201; the partnership is not itself taxed), with the composite
     return **EMBEDDED as Schedule 6922** at 3% flat. The standalone
     Form R-6922 was abolished (merged in from TY2021); only the vouchers
     R-6922V / R-6922ES survive.
  2. ELECTING PTE (partnership OR S corp; R.S. 47:287.732.2, Form R-6980)
     -> **CIT-620**, Line O box, **Schedule H-1 at 3% flat**.
  3. NON-ELECTING S CORP -> **CIT-620 computed AS A C CORPORATION** at
     5.5%, with the **Line 1B S-corp exclusion** (ratio of LA-resident-owned
     shares). THE 1120S MODULE'S STATE RETURN IS THE C-CORP RETURN.

Consequence ratified at D-16 A1: **`LA_CIT620` is authored IN FULL here,
including the C-corp computation** — unavoidable, because track 3 IS the
C-corp computation. The future 1120 module REUSES this spec rather than
creating it (the usual order inverts).

⚠ FORM RENAME: CIFT-620 -> **CIT-620** for TY2025 (franchise tax repealed
eff. 1/1/2026, R.S. 47:601; franchise schedules removed from the form).
`LA_CIFT620` would be a stale code. Triple-confirmed by the verification
pass (face, LDR index rows 2021-2024 vs 2025, 404 probes).

═══════════════════════════════════════════════════════════════════════════
v1 SCOPE — D-16 A2: **COMPUTE-AND-REVIEW ONLY**
═══════════════════════════════════════════════════════════════════════════
The composite return is **e-file-only BY STATUTE** (R.S. 47:201.1(F)(4):
"Composite returns shall be filed electronically.") and electing PTEs are
e-file-mandated by rule (LAC 61:I.1001(C)(2)). A paper IT-565 carrying
Schedule 6922 is NOT a legal filing. Until LA MeF access lands (U5), v1
computes everything and produces review copies; every composite/electing
return carries a RED diagnostic naming the mandate. This is exactly what
the back-entry pilot needs.

CONFORMITY IS NOT RE-LITIGATED HERE — `conformity/la_conformity.md`
(VERIFIED 2026-08-22, its §12 governs) is the authority. Headlines that
bear on this spec: rolling conformity, **OBBBA IS in for TY2025**, **NO
federal bonus add-back** (affirmatively established), plus an ELECTIVE
state 100%-expensing regime (R.S. 47:287.744 / 47:297.25, IRC definitions
frozen 1/1/2024, Form R-90158 attachment, out-year add-back on
state-expensed property only). Both 3% rates are statutorily DERIVATIVE of
the individual rate (47:201.1(D)(1); 47:287.732.2(B) -> 47:32) — TY-key
them off one authority chain, two constants.

⚠ TY2026 CLIFF — FOUR acts pivot at 1/1/2026 and are already printed on the
TY2025 forms: Act 6 (franchise repeal), Act 5 (CIT 5.5%), Act 11 (3%),
**Act 382 (S corps become information filers + new Schedules K/L composite;
PTE election barred for S-corp composite filers)**. TY2026 is a
RE-AUTHORING EVENT, not a constant bump. Everything below is TY-keyed.
⚠ VINTAGE TRAP: the CURRENTLY CODIFIED R.S. 47:287.732 is the Act 382
rewrite — the TY2025 S-corp exclusion text is GONE from current law. TY2025
authority is the CIT-620i booklet + the pre-Act-382 text.

SAFETY GUARD — READY_TO_SEED stays False until Ken approves the SEED walk.
D-16 approved the SCOPE (A1/A2/A3 + bless-list); the seed is a separate gate.
"""
from django.core.management.base import BaseCommand, CommandError

from . import _authority_wiring as _wire
from django.db import transaction

from sources.models import (
    AuthorityExcerpt, AuthorityFormLink, AuthoritySource, AuthoritySourceTopic,
    AuthorityTopic, RuleAuthorityLink,
)
from specs.models import (
    FlowAssertion, FormDiagnostic, FormFact, FormLine, FormRule, TaxForm, TestScenario,
)

# FLIPPED 2026-08-22 — Ken APPROVED THE SEED DIRECTLY ("approve the LA seed"),
# in his own words to this session. Campaign D-17.
# ⚠ The gate discipline this wave established and which this flip HONOURS: a
# RELAYED approval would NOT have opened this gate. The delvio-tax session
# staged the question at Ken's instruction; Ken answered here, directly.
# D-16 approved the SCOPE (A1 full CIT-620 incl. the C-corp computation with
# Schedule 6922 inside LA_IT565; A2 compute-and-review-only v1; A3 pro-forma
# direct entry). This is the SEPARATE seed approval.
# ⚠ SEEDING IS NOT BUILDING. The app build stays deferred pending a design
# conversation: Louisiana has no S-corp return, so a non-electing S corp files
# CIT-620 computed AS A C CORPORATION and the 1120S module's state return IS
# the C-corp computation — which inverts the usual module order.
READY_TO_SEED = True

FORM_JURISDICTION = "LA"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"

# ── TY-keyed constants ─────────────────────────────────────────────────────
# Both 3% rates are DERIVATIVE of the individual rate (R.S. 47:32) — they are
# two constants with two authority chains, not one shared number. Do not
# collapse them (the CO R-CO-RATES lesson).
LA_COMPOSITE_RATE: dict[int, str] = {2025: "0.03"}   # R.S. 47:201.1(D)(1) -> 47:32
LA_PTE_ELECT_RATE: dict[int, str] = {2025: "0.03"}   # R.S. 47:287.732.2(B) -> 47:32
LA_CIT_RATE: dict[int, str] = {2025: "0.055"}        # R.S. 47:287.12 (Act 5 of 2024 3ES, flat)
LA_CORP_STD_DEDUCTION: dict[int, int] = {2025: 20000}   # CIT-620 Sch F line 3f
LA_NOL_LIMIT_PCT: dict[int, str] = {2025: "0.72"}       # 72% of LA net income; indefinite carryforward
# Interest — Form R-1111 (1/26), TY-keyed, re-pull annually.
LA_INTEREST_DAILY: dict[int, str] = {2025: "0.00030822", 2026: "0.00028767"}
LA_INTEREST_ANNUAL: dict[int, str] = {2025: "0.1125", 2026: "0.1050"}
# Composite penalties (Schedule 6922 worksheet).
LA_PEN_FILING_PCT_PER_30D: dict[int, str] = {2025: "0.05"}
LA_PEN_PAYMENT_PCT_PER_30D: dict[int, str] = {2025: "0.005"}
LA_PEN_COMBINED_CAP_PCT: dict[int, str] = {2025: "0.25"}
# Election lifecycle (R.S. 47:287.732.2(A)(4)).
LA_ELECTION_TERMINATION_DEADLINE = "November 1 (prospective, following tax year)"
LA_ELECTION_RELECTION_LOCKOUT_YEARS = 5


def _yk(table: dict, year: int):
    if year not in table:
        raise CommandError(
            f"LA spec is TY-keyed and has no entry for {year}. Louisiana's TY2026 cliff "
            "(Acts 5/6/11/382) is a RE-AUTHORING event, not a constant bump — author the "
            "year explicitly rather than extending a TY2025 figure."
        )
    return table[year]


def la_composite_tax(nonresident_partner_share, year: int = FORM_TAX_YEAR) -> float:
    """Schedule 6922 (embedded in IT-565) — composite tax at the individual
    rate on nonresident partners' LA-source distributive shares.
    R.S. 47:201.1(D)(1). ⚠ E-FILE ONLY: R.S. 47:201.1(F)(4)."""
    return float(nonresident_partner_share) * float(_yk(LA_COMPOSITE_RATE, year))


def la_electing_pte_tax(pte_taxable_income, year: int = FORM_TAX_YEAR) -> float:
    """CIT-620 Schedule H-1 — the elective PTE tax. R.S. 47:287.732.2(B) sets
    the rate BY REFERENCE to the individual rate (R.S. 47:32), which is why
    this is a separate constant from the composite rate despite being equal
    for TY2025."""
    return float(pte_taxable_income) * float(_yk(LA_PTE_ELECT_RATE, year))


def la_corporate_tax(la_taxable_income, year: int = FORM_TAX_YEAR) -> float:
    """CIT-620 Schedule H — the flat corporate income tax (R.S. 47:287.12).
    This is the NON-ELECTING S-CORP path too (track 3): an S corporation
    computes as a C corporation and takes the Line 1B exclusion."""
    return float(la_taxable_income) * float(_yk(LA_CIT_RATE, year))


def la_scorp_exclusion(la_net_income, resident_shares, total_shares) -> float:
    """CIT-620 Line 1B — the S-corp exclusion.

    ⚠ THE NUMERATOR IS NOT A SIMPLE RESIDENCY COUNT. It counts shares owned
    by LA residents PLUS shares owned by nonresident individuals **who filed
    a correct Louisiana return and paid the tax** — a fact outside the
    entity's own return (walk W4: per-shareholder resident/compliance flags +
    attachment). The ratio is preparer-supplied; the engine never infers it.
    ⚠ BLOCKED when Line O (the PTE election) is marked — an electing entity
    takes no S-corp exclusion.
    """
    if not total_shares:
        return 0.0
    return float(la_net_income) * (float(resident_shares) / float(total_shares))


def la_nol_utilization(la_net_income, nol_carryforward, year: int = FORM_TAX_YEAR) -> float:
    """CIT-620 Line 1C1 — NOL utilization capped at 72% of LA net income
    (R.S. 47:287.86). Carryforward is INDEFINITE; federal §172 is inoperative
    for Louisiana."""
    return min(float(la_net_income) * float(_yk(LA_NOL_LIMIT_PCT, year)),
               float(nol_carryforward))


def la_corp_standard_deduction(modified_la_net_income_before_3f, year: int = FORM_TAX_YEAR) -> float:
    """CIT-620 Schedule F line 3f — $20,000, floored at zero, capped at the
    income it offsets.
    ⚠ U7 OPEN: whether an ELECTING PTE may take it. The printed test is
    "corporations subject to income tax pursuant to R.S. 47:287.11", and
    47:287.732.2(B) taxes the electing entity at the INDIVIDUAL rate, not
    under §287.11 — which cuts against eligibility — but no instruction
    addresses electing PTEs either way. The diagnostic surfaces it; the
    engine does not decide it."""
    cap = float(_yk(LA_CORP_STD_DEDUCTION, year))
    return max(0.0, min(cap, float(modified_la_net_income_before_3f)))


AUTHORITY_TOPICS: list[tuple[str, str]] = [
    # ⚠ topic_name is varchar(255) — keep it SHORT. The full description lives
    # here in the source, not in the column (the campaign has hit the
    # too-long-for-the-live-column failure before: it passes every local check
    # and fails only against prod).
    # Full scope: IT-565 is the informational partnership return with the
    # composite EMBEDDED as Schedule 6922 at 3%; CIT-620 (renamed from
    # CIFT-620 for TY2025) serves BOTH the elective PTE regime
    # (R.S. 47:287.732.2, Schedule H-1, 3%) AND the non-electing S corporation
    # computed as a C corporation at 5.5% with the Line 1B resident-shareholder
    # exclusion. No S-corp return and no PTE-specific return exist. Rolling
    # conformity; no federal bonus add-back; elective state 100%-expensing
    # regime. Four-act TY2026 cliff.
    ("la_passthrough_pte",
     "Louisiana pass-through returns (IT-565 + CIT-620): composite embedded as "
     "Schedule 6922, the elective PTE regime, and the non-electing S corporation "
     "computed as a C corporation."),
]

EXISTING_SOURCES_TO_REFERENCE: list[str] = []

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "LA_2025_IT565", "source_type": "state_form", "source_rank": "primary_official",
        "jurisdiction_code": "LA", "title": "2025 Louisiana Form IT-565 — Partnership Return of Income + Schedule 6922",
        "citation": "LA Form IT-565 (TY2025), IT-565WEB-BC-1-26 / IT-565i-1-26", "issuer": "Louisiana Department of Revenue",
        "official_url": "https://revenue.louisiana.gov/tax-forms/businesses/",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.5,
        "topics": ["la_passthrough_pte"],
        "excerpts": [{
            "excerpt_label": "IT-565 is INFORMATIONAL; the composite is EMBEDDED as Schedule 6922 and is e-file-only",
            "excerpt_text": (
                "The partnership return is an information return (R.S. 47:201; R.S. 47:103(A)(2)) — the "
                "partnership itself is not subject to the income tax. The nonresident-partner COMPOSITE return "
                "is not a separate form: the standalone Form R-6922 was merged into the IT-565 as SCHEDULE 6922 "
                "beginning TY2021 (only the vouchers R-6922V and R-6922ES survive as standalone forms), and "
                "LDR publishes no paper face for it — vendors render it from the IT-565-SD software-developer "
                "layout. Composite tax = the individual maximum rate (3% for TY2025) on nonresident partners' "
                "Louisiana-source distributive shares (R.S. 47:201.1(D)(1) -> R.S. 47:32). ⚠ R.S. 47:201.1(F)(4), "
                "verbatim: 'Composite returns shall be filed electronically.' A paper IT-565 carrying Schedule "
                "6922 is therefore NOT a legal filing. Partner rosters live in the Schedules A and B Excel "
                "workbook, not the PDF; Schedule B Column O = 3% x Column N per partner. A partnership with "
                "BOTH corporate and non-corporate partners files Schedules D/E/G AND H/I/J — two different "
                "Louisiana net incomes on one return."
            ),
            "summary_text": "IT-565 informational; composite embedded as Schedule 6922 at 3%; e-file mandatory by statute; partner rosters in the A/B xlsx; dual-engine partnerships file both schedule sets.",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "LA_2025_CIT620", "source_type": "state_form", "source_rank": "primary_official",
        "jurisdiction_code": "LA", "title": "2025 Louisiana Form CIT-620 — Corporation Income Tax Return (renamed from CIFT-620)",
        "citation": "LA Form CIT-620 (TY2025, revised 4/10/2026) + CIT-620i", "issuer": "Louisiana Department of Revenue",
        "official_url": "https://revenue.louisiana.gov/tax-forms/businesses/",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.5,
        "topics": ["la_passthrough_pte"],
        "excerpts": [{
            "excerpt_label": "CIT-620 serves THREE tracks; the rename; the S-corp exclusion; the TY2026 cliff",
            "excerpt_text": (
                "⚠ RENAMED for TY2025: CIFT-620 -> CIT-620. The 'F' (franchise) is gone because the corporate "
                "franchise tax is repealed effective January 1, 2026 (R.S. 47:601: 'Repealed... eff. Jan. 1, "
                "2026'); the last franchise period (2025) rode the **2024** CIFT-620, and the TY2025 CIT-620 "
                "carries no franchise schedules. ONE form serves three filers: (a) an ELECTING pass-through "
                "entity — partnership or S corporation — that made the R.S. 47:287.732.2 election on Form "
                "R-6980, which marks Line O and computes on SCHEDULE H-1 at 3%; (b) a NON-ELECTING S "
                "CORPORATION, which computes AS A C CORPORATION at 5.5% on Schedule H and takes the LINE 1B "
                "S-CORP EXCLUSION (the ratio of shares owned by Louisiana residents — plus nonresident "
                "individuals who actually filed and paid Louisiana tax — to total shares); and (c) an ordinary "
                "C corporation. Line 1C1 NOL utilization = 72% x LA net income (indefinite carryforward). "
                "Schedule F line 3f carries the $20,000 corporate standard deduction. ⚠ TY2026: Act 382 of "
                "2025 flips S corporations to INFORMATION filers with new Schedules K/L and a composite, and "
                "bars the PTE election for S-corp composite filers — printed on the TY2025 form."
            ),
            "summary_text": "CIT-620 (renamed, franchise repealed) serves electing PTEs at 3% (Sch H-1), non-electing S corps as C corps at 5.5% with the Line 1B exclusion, and C corps; 72% NOL cap; $20,000 standard deduction; Act 382 TY2026 flip.",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "LA_RS_47_287_732_2", "source_type": "state_statute", "source_rank": "controlling",
        "jurisdiction_code": "LA", "title": "La. R.S. 47:287.732.2 — the elective pass-through entity tax",
        "citation": "La. R.S. 47:287.732.2; R.S. 47:32; LAC 61:I.1001", "issuer": "Louisiana Legislature",
        "official_url": "https://legis.la.gov/legis/Law.aspx?d=1148883",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.6,
        "topics": ["la_passthrough_pte"],
        "excerpts": [{
            "excerpt_label": "Election mechanics, rate-by-reference, termination and the 5-year lockout",
            "excerpt_text": (
                "(A)(1) An electing entity computes its Louisiana income tax 'in the same manner' as a C "
                "corporation. (B) The RATE is set BY REFERENCE to the individual rate at R.S. 47:32 — which is "
                "why the electing-PTE rate and the composite rate, both 3% for TY2025, are two constants with "
                "two authority chains rather than one shared figure. The election is made on Form R-6980, is "
                "submitted BY EMAIL to LDR, and REQUIRES LDR ACCEPTANCE; it is perpetual until terminated on "
                "Form R-6983. (A)(4)(c): termination is PROSPECTIVE and must be filed by NOVEMBER 1 for the "
                "following tax year. (A)(4)(d): a 5-YEAR RE-ELECTION LOCKOUT follows a termination. "
                "LAC 61:I.1001 (adopted rule, LR 50:419) matches R-6980i/R-6983i verbatim and adds C.4.d: "
                "owners of an electing entity submit a PRO-FORMA federal 1040/1041 excluding entity-taxed "
                "items. LAC 61:I.1001(C)(2) makes electing-PTE filing ELECTRONIC. Owner-side relief is an "
                "EXCLUSION (R.S. 47:297.14 for individuals; R.S. 47:300.6/300.7 for estates and trusts) — "
                "CORPORATE owners remain taxable. Composite filing and the election are mutually exclusive."
            ),
            "summary_text": "R-6980 election emailed + LDR acceptance, perpetual; R-6983 termination by Nov 1 prospective + 5-year lockout; rate by reference to R.S. 47:32; owner relief is an EXCLUSION, not a credit; corporate owners still taxable.",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "LA_RS_47_201_1", "source_type": "state_statute", "source_rank": "controlling",
        "jurisdiction_code": "LA", "title": "La. R.S. 47:201 / 47:201.1 — partnership information return and the composite mandate",
        "citation": "La. R.S. 47:201; 47:201.1(A), (D)(1), (F)(4); 47:103(A)(2)", "issuer": "Louisiana Legislature",
        "official_url": "https://legis.la.gov/legis/Law.aspx?d=101460",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.6,
        "topics": ["la_passthrough_pte"],
        "excerpts": [{
            "excerpt_label": "Composite mandate + the statutory e-file requirement (verbatim)",
            "excerpt_text": (
                "R.S. 47:201 makes the partnership return an INFORMATION return (per R.S. 47:103(A)(2)); the "
                "partnership is not subject to the tax. R.S. 47:201.1(A) mandates the composite return for "
                "nonresident partners. (D)(1) sets the composite rate at the individual maximum rate. "
                "⚠ (F)(4), VERBATIM: 'Composite returns shall be filed electronically.' — a STATUTORY e-file "
                "mandate, not a preference, and the reason a v1 without Louisiana MeF output can compute a "
                "composite return but cannot produce a FILABLE one."
            ),
            "summary_text": "Partnership return is informational; composite mandatory for nonresident partners at the individual rate; 'Composite returns shall be filed electronically' (statutory).",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "LA_TY2026_CLIFF", "source_type": "state_statute", "source_rank": "controlling",
        "jurisdiction_code": "LA", "title": "Louisiana TY2026 cliff — Acts 5, 6, 11 (2024 3ES) and Act 382 (2025 RS)",
        "citation": "Acts 5, 6, 11 of the 2024 Third Extraordinary Session; Act 382 of 2025 (enrolled HB 567); RIB 25-032",
        "issuer": "Louisiana Legislature", "official_url": "https://legis.la.gov/legis/BillInfo.aspx?i=250444",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.4,
        "topics": ["la_passthrough_pte"],
        "excerpts": [{
            "excerpt_label": "Four acts pivot at 1/1/2026 — TY2026 is a RE-AUTHORING event",
            "excerpt_text": (
                "Act 6 repeals the corporate FRANCHISE tax effective 1/1/2026 (R.S. 47:601). Act 5 sets the "
                "flat 5.5% corporate income tax. Act 11 carries the 3% individual rate the two PTE rates key "
                "off. ⚠ ACT 382 of 2025 (enrolled HB 567; confirmed by RIB 25-032) flips S CORPORATIONS to "
                "INFORMATION filers for TY2026 with new Schedules K and L plus a composite, ENDS the S-corp "
                "exclusion, and BARS the PTE election for S-corp composite filers. All four are already "
                "PRINTED on the TY2025 forms. ⚠ VINTAGE TRAP: the CURRENTLY CODIFIED R.S. 47:287.732 is the "
                "Act 382 rewrite — the TY2025 S-corp exclusion text no longer appears in current law, so "
                "TY2025 authority is the CIT-620i booklet and the pre-Act-382 text, NOT a fresh statute pull."
            ),
            "summary_text": "Acts 5/6/11 (2024 3ES) + Act 382 (2025) all pivot 1/1/2026; Act 382 ends the S-corp return and the exclusion; current codified 287.732 is already the TY2026 text (vintage trap).",
            "is_key_excerpt": True,
        }],
    },
]

AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    ("LA_2025_IT565", "LA_IT565", "governs"),
    ("LA_RS_47_201_1", "LA_IT565", "governs"),
    ("LA_TY2026_CLIFF", "LA_IT565", "informs"),
    ("LA_2025_CIT620", "LA_CIT620", "governs"),
    ("LA_RS_47_287_732_2", "LA_CIT620", "governs"),
    ("LA_TY2026_CLIFF", "LA_CIT620", "informs"),
]

# ── Shared facts ───────────────────────────────────────────────────────────
_SHARED_FACTS = [
    {"fact_key": "federal_ordinary_income", "label": "Federal ordinary business income (1065 L22 / 1120-S L21)", "data_type": "decimal", "required": False, "sort_order": 1},
    {"fact_key": "la_net_income", "label": "Louisiana net income (after LA modifications and apportionment)", "data_type": "decimal", "required": False, "sort_order": 2},
    {"fact_key": "la_apportionment_ratio", "label": "Louisiana apportionment ratio (single revenue ratio default; R.S. 47:287.95(F))", "data_type": "decimal", "required": False, "sort_order": 3},
    {"fact_key": "state_expensing_election", "label": "La. R.S. 47:287.744 / 47:297.25 elective 100% expensing claimed? (Form R-90158 attachment — RED-deferred, U1)", "data_type": "boolean", "required": False, "sort_order": 4},
    {"fact_key": "is_oil_and_gas", "label": "Oil & gas taxpayer (four-ratio apportionment)? — RED-defer", "data_type": "boolean", "required": False, "sort_order": 5},
    {"fact_key": "separate_accounting", "label": "Separate-accounting method used? — RED-defer", "data_type": "boolean", "required": False, "sort_order": 6},
]

IT565_FACTS = [dict(f) for f in _SHARED_FACTS] + [
    {"fact_key": "composite_filed", "label": "Composite return filed for nonresident partners (Schedule 6922)?", "data_type": "boolean", "required": False, "sort_order": 10},
    {"fact_key": "nonresident_partner_la_share", "label": "Nonresident partners' Louisiana-source distributive shares (Schedule B Column N total — composite base)", "data_type": "decimal", "required": False, "sort_order": 11},
    {"fact_key": "has_corporate_partners", "label": "Partnership has CORPORATE partners? (drives Schedules H/I/J alongside D/E/G — dual engine)", "data_type": "boolean", "required": False, "sort_order": 12},
    {"fact_key": "has_noncorporate_partners", "label": "Partnership has NON-CORPORATE partners? (drives Schedules D/E/G)", "data_type": "boolean", "required": False, "sort_order": 13},
    {"fact_key": "composite_days_late", "label": "Days late (composite interest/penalty worksheet)", "data_type": "decimal", "required": False, "sort_order": 14},
]

CIT620_FACTS = [dict(f) for f in _SHARED_FACTS] + [
    {"fact_key": "pte_election_active", "label": "PTE election active (Line O; R-6980 filed AND accepted by LDR)?", "data_type": "boolean", "required": False, "sort_order": 10},
    {"fact_key": "is_s_corporation", "label": "Federal S corporation (non-electing -> computes as a C corp with the Line 1B exclusion)?", "data_type": "boolean", "required": False, "sort_order": 11},
    {"fact_key": "la_resident_shares", "label": "Shares owned by LA residents + nonresident individuals who FILED AND PAID Louisiana tax (Line 1B numerator — preparer-supplied, attachment required)", "data_type": "decimal", "required": False, "sort_order": 12},
    {"fact_key": "total_shares", "label": "Total shares outstanding (Line 1B denominator)", "data_type": "decimal", "required": False, "sort_order": 13},
    {"fact_key": "nol_carryforward", "label": "Louisiana NOL carryforward available (indefinite; federal §172 inoperative)", "data_type": "decimal", "required": False, "sort_order": 14},
    {"fact_key": "pro_forma_c_corp_income", "label": "Pro-forma Subchapter-C-basis net income (Sch F L1) — DIRECT ENTRY (D-16 A3; the shadow 1120 is not synthesized in v1)", "data_type": "decimal", "required": False, "sort_order": 15},
]

# ── Rules ──────────────────────────────────────────────────────────────────
IT565_RULES = [
    {"rule_id": "R-LAIT565-INFO", "title": "IT-565 is an INFORMATION return — the partnership is not taxed", "rule_type": "constraint",
     "formula": "partnership_income_tax = 0  # R.S. 47:201 / 47:103(A)(2). Tax arises ONLY via Schedule 6922 (composite) or, on election, on the CIT-620.",
     "inputs": ["federal_ordinary_income"], "outputs": ["partnership_income_tax"], "sort_order": 1,
     "description": "R.S. 47:201. The IT-565 itself computes NO entity tax. A spec that treats it as a tax-computing return will not produce the ordinary Louisiana partnership filing."},
    {"rule_id": "R-LAIT565-COMPOSITE", "title": "Schedule 6922 composite tax — 3% of nonresident partners' LA-source shares", "rule_type": "calculation",
     "formula": "composite_tax = nonresident_partner_la_share * 0.03  # per partner: Sch B Col O = Col N x 3%; Sch 6922 L1/L2 are the Col N/O totals",
     "inputs": ["composite_filed", "nonresident_partner_la_share"], "outputs": ["composite_tax"], "sort_order": 2,
     "description": ("R.S. 47:201.1(D)(1) -> R.S. 47:32. The composite is EMBEDDED in the IT-565 as Schedule 6922 "
                     "(the standalone R-6922 was abolished in TY2021); partner rosters live in the Schedules A/B "
                     "Excel workbook. The rate is DERIVATIVE of the individual rate — a separate constant from the "
                     "electing-PTE rate despite being equal for TY2025.")},
    {"rule_id": "R-LAIT565-EFILE", "title": "⚠ The composite return is E-FILE ONLY, by statute", "rule_type": "constraint",
     "formula": "if composite_filed and not efile_available: RED('R.S. 47:201.1(F)(4) — Composite returns shall be filed electronically')",
     "inputs": ["composite_filed"], "outputs": ["efile_required"], "sort_order": 3,
     "description": ("R.S. 47:201.1(F)(4), verbatim: 'Composite returns shall be filed electronically.' A paper "
                     "IT-565 carrying Schedule 6922 is NOT a legal filing. v1 is COMPUTE-AND-REVIEW ONLY (D-16 A2) "
                     "until LA MeF lands — the diagnostic must say so on every composite return.")},
    {"rule_id": "R-LAIT565-DUAL", "title": "Dual-engine partnerships — corporate AND non-corporate partners", "rule_type": "constraint",
     "formula": "if has_corporate_partners and has_noncorporate_partners: require(Schedules D/E/G) and require(Schedules H/I/J)  # TWO Louisiana net incomes on one return",
     "inputs": ["has_corporate_partners", "has_noncorporate_partners"], "outputs": ["required_schedule_sets"], "sort_order": 4,
     "description": ("Walk item W7. A partnership with both partner classes files BOTH schedule sets and reports "
                     "two different Louisiana net incomes on one return. Never force a single-engine assumption.")},
]

CIT620_RULES = [
    {"rule_id": "R-LACIT620-FORK", "title": "THE THREE-TRACK FORK — election, S-corp, or ordinary C corp", "rule_type": "constraint",
     "formula": ("if pte_election_active: track = 'electing_pte' (Schedule H-1, 3%) ; "
                 "elif is_s_corporation: track = 'nonelecting_scorp' (Schedule H, 5.5%, WITH the Line 1B exclusion) ; "
                 "else: track = 'c_corp' (Schedule H, 5.5%, NO exclusion)"),
     "inputs": ["pte_election_active", "is_s_corporation"], "outputs": ["track"], "sort_order": 1,
     "description": ("THE defining Louisiana structure (campaign D-16 A1). One form, three filers. The "
                     "non-electing S-corp path IS the C-corp computation — which is why this spec is authored in "
                     "full now and the future 1120 module reuses it. ⚠ The election and the S-corp exclusion are "
                     "mutually exclusive: an electing entity takes NO Line 1B exclusion.")},
    {"rule_id": "R-LACIT620-ELECT-TAX", "title": "Schedule H-1 — elective PTE tax at 3%", "rule_type": "calculation",
     "formula": "if pte_election_active: pte_tax = pte_taxable_income * 0.03  # R.S. 47:287.732.2(B) -> R.S. 47:32",
     "inputs": ["pte_election_active", "la_net_income"], "outputs": ["pte_tax"], "sort_order": 2,
     "description": ("R.S. 47:287.732.2. The electing entity computes 'in the same manner' as a C corporation but "
                     "at the individual rate. Owner-side relief is an EXCLUSION (47:297.14 individuals; "
                     "47:300.6/300.7 estates and trusts) — CORPORATE owners remain taxable. R-6981 reports each "
                     "owner's share; R-6982 the tax paid.")},
    {"rule_id": "R-LACIT620-SCORP", "title": "Line 1B — the S-corp exclusion (ratio of resident-owned shares)", "rule_type": "calculation",
     "formula": ("if is_s_corporation and not pte_election_active: "
                 "line_1B = line_1A * (la_resident_shares / total_shares) ; else: line_1B = 0"),
     "inputs": ["is_s_corporation", "pte_election_active", "la_resident_shares", "total_shares"], "outputs": ["line_1B"], "sort_order": 3,
     "description": ("⚠ THE NUMERATOR IS NOT A RESIDENCY COUNT. It includes shares held by NONRESIDENT individuals "
                     "who filed a correct Louisiana return AND PAID — a compliance fact outside this return "
                     "(walk W4). Preparer-supplied with an attachment; never inferred. BLOCKED when Line O is "
                     "marked. ⚠ DIES for TY2026 (Act 382).")},
    {"rule_id": "R-LACIT620-CORP-TAX", "title": "Schedule H — flat corporate income tax 5.5%", "rule_type": "calculation",
     "formula": "if not pte_election_active: corp_tax = la_taxable_income * 0.055  # R.S. 47:287.12 (Act 5 of 2024 3ES)",
     "inputs": ["pte_election_active", "la_net_income"], "outputs": ["corp_tax"], "sort_order": 4,
     "description": "Flat rate; no brackets. This path serves BOTH the non-electing S corporation and the ordinary C corporation."},
    {"rule_id": "R-LACIT620-NOL", "title": "Line 1C1 — NOL utilization capped at 72% of LA net income", "rule_type": "calculation",
     "formula": "line_1C1 = min(la_net_income * 0.72, nol_carryforward)  # R.S. 47:287.86; carryforward INDEFINITE",
     "inputs": ["la_net_income", "nol_carryforward"], "outputs": ["line_1C1"], "sort_order": 5,
     "description": "Louisiana's own NOL regime — federal §172 is inoperative. Indefinite carryforward, 72% annual utilization cap."},
    {"rule_id": "R-LACIT620-STD-DED", "title": "Schedule F line 3f — $20,000 corporate standard deduction", "rule_type": "calculation",
     "formula": "line_3f = max(0, min(20000, modified_la_net_income_before_3f))",
     "inputs": ["la_net_income"], "outputs": ["line_3f"], "sort_order": 6,
     "description": ("R.S. 47:287.71(B)(9). ⚠ U7 OPEN: whether an ELECTING PTE may take it. The printed test names "
                     "'corporations subject to income tax pursuant to R.S. 47:287.11', and 47:287.732.2(B) taxes "
                     "the electing entity at the INDIVIDUAL rate rather than under §287.11 — evidence against "
                     "eligibility — but no instruction addresses electing PTEs either way. Surfaced, not decided.")},
    {"rule_id": "R-LACIT620-PROFORMA", "title": "Schedule F L1 — the pro-forma Subchapter-C shadow return (DIRECT ENTRY in v1)", "rule_type": "constraint",
     "formula": "line_F1 = pro_forma_c_corp_income  # preparer-entered; the shadow federal 1120 is NOT synthesized in v1 (D-16 A3)",
     "inputs": ["pro_forma_c_corp_income"], "outputs": ["line_F1"], "sort_order": 7,
     "description": ("CIT-620 Schedule F L1 requires electing partnerships and S corps to compute net income 'on a "
                     "separate Subchapter C corporation basis' — a shadow federal 1120. D-16 A3: v1 takes the "
                     "figure by direct entry with a worksheet-attachment prompt; synthesizing it from 1065/1120-S "
                     "data is a later engine (the VA/MS direct-entry precedent).")},
    {"rule_id": "R-LACIT620-NOBONUS", "title": "Depreciation — NO federal bonus add-back exists in Louisiana", "rule_type": "constraint",
     "formula": "la_bonus_addback = NONE  # rolling conformity; no modification statute. The ONLY depreciation lines are the STATE ELECTION's.",
     "inputs": ["state_expensing_election"], "outputs": [], "sort_order": 8,
     "description": ("`conformity/la_conformity.md` (VERIFIED) establishes this AFFIRMATIVELY: R.S. 47:287.71's "
                     "additions list contains no depreciation item, and all four TY2025 booklets grep clean. A "
                     "commercial-publisher claim to the contrary was refuted against primary sources. What DOES "
                     "exist is the ELECTIVE state 100%-expensing regime (47:287.744 / 47:297.25) with IRC "
                     "definitions frozen 1/1/2024 and an out-year add-back on STATE-EXPENSED property only "
                     "(47:287.744(C)(3)) — Form R-90158, which has NO published PDF (U1) and is therefore "
                     "RED-DEFERRED. ⚠ Never code a Georgia-shaped bonus add-back for Louisiana.")},
    {"rule_id": "R-LACIT620-ELECT", "title": "Election lifecycle — acceptance, perpetuity, Nov-1 termination, 5-year lockout", "rule_type": "constraint",
     "formula": ("election_active requires: R-6980 filed AND LDR acceptance received ; perpetual until R-6983 ; "
                 "R-6983 due NOVEMBER 1 (prospective, next tax year) ; then 5-YEAR re-election lockout"),
     "inputs": ["pte_election_active"], "outputs": ["election_status"], "sort_order": 9,
     "description": ("R.S. 47:287.732.2(A)(4)(c)-(d); LAC 61:I.1001. Walk item W6: election status is CLIENT-RECORD "
                     "data (with the acceptance-letter date), not a return field — nothing on the return reveals "
                     "it, and the election is emailed to LDR outside the return. Composite filing and the "
                     "election are MUTUALLY EXCLUSIVE.")},
]

IT565_RULE_LINKS = [
    ("R-LAIT565-INFO", "LA_RS_47_201_1", "primary", "R.S. 47:201 information return"),
    ("R-LAIT565-COMPOSITE", "LA_RS_47_201_1", "primary", "R.S. 47:201.1(D)(1) composite rate"),
    ("R-LAIT565-COMPOSITE", "LA_2025_IT565", "secondary", "Schedule 6922 / Sch B Col O"),
    ("R-LAIT565-EFILE", "LA_RS_47_201_1", "primary", "R.S. 47:201.1(F)(4) verbatim"),
    ("R-LAIT565-DUAL", "LA_2025_IT565", "primary", "Schedules D/E/G vs H/I/J"),
]

CIT620_RULE_LINKS = [
    ("R-LACIT620-FORK", "LA_2025_CIT620", "primary", "three tracks on one form"),
    ("R-LACIT620-ELECT-TAX", "LA_RS_47_287_732_2", "primary", "R.S. 47:287.732.2(B) rate by reference"),
    ("R-LACIT620-SCORP", "LA_2025_CIT620", "primary", "Line 1B exclusion ratio"),
    ("R-LACIT620-CORP-TAX", "LA_2025_CIT620", "primary", "Schedule H 5.5%"),
    ("R-LACIT620-NOL", "LA_2025_CIT620", "primary", "Line 1C1 72% cap"),
    ("R-LACIT620-STD-DED", "LA_2025_CIT620", "primary", "Schedule F line 3f"),
    ("R-LACIT620-PROFORMA", "LA_2025_CIT620", "primary", "Schedule F L1 pro-forma C basis"),
    ("R-LACIT620-ELECT", "LA_RS_47_287_732_2", "primary", "R-6980/R-6983 lifecycle"),
]

IT565_LINES = [
    {"line_number": "IT565-SCH6922-L1", "description": "Schedule 6922 Line 1 — nonresident partners' LA-source shares (Sch B Column N total)", "line_type": "calculated", "source_rules": ["R-LAIT565-COMPOSITE"], "sort_order": 1},
    {"line_number": "IT565-SCH6922-L2", "description": "Schedule 6922 Line 2 — composite tax (Sch B Column O total = 3% x Column N per partner)", "line_type": "calculated", "source_rules": ["R-LAIT565-COMPOSITE"], "sort_order": 2},
    {"line_number": "IT565-SCH6922-L23", "description": "Schedule 6922 Line 23 — total composite balance due/overpayment (after credits, interest and penalties)", "line_type": "total", "source_rules": ["R-LAIT565-COMPOSITE"], "sort_order": 3},
    {"line_number": "IT565-SCHG-L23", "description": "Schedule G Line 23 — Louisiana net income (ties to Schedule D Line 4; RED on mismatch)", "line_type": "calculated", "source_rules": ["R-LAIT565-INFO"], "sort_order": 4},
]

CIT620_LINES = [
    {"line_number": "CIT620-1A", "description": "Line 1A — Louisiana net income (from Schedule D Line 31)", "line_type": "calculated", "source_rules": ["R-LACIT620-FORK"], "sort_order": 1},
    {"line_number": "CIT620-1B", "description": "Line 1B — S-corp exclusion (1A x resident-share ratio; zero when Line O is marked)", "line_type": "calculated", "source_rules": ["R-LACIT620-SCORP"], "sort_order": 2},
    {"line_number": "CIT620-1C1", "description": "Line 1C1 — NOL utilization (72% of LA net income, indefinite carryforward)", "line_type": "calculated", "source_rules": ["R-LACIT620-NOL"], "sort_order": 3},
    {"line_number": "CIT620-1D", "description": "Line 1D — Louisiana taxable income (1A − 1B − 1C1)", "line_type": "calculated", "source_rules": ["R-LACIT620-FORK"], "sort_order": 4},
    {"line_number": "CIT620-1E", "description": "Line 1E — tax (from Schedule H at 5.5%, or Schedule H-1 at 3% when Line O is marked)", "line_type": "calculated", "source_rules": ["R-LACIT620-ELECT-TAX", "R-LACIT620-CORP-TAX"], "sort_order": 5},
    {"line_number": "CIT620-SCHF-L3F", "description": "Schedule F Line 3f — $20,000 corporate standard deduction (U7: electing-PTE eligibility open)", "line_type": "calculated", "source_rules": ["R-LACIT620-STD-DED"], "sort_order": 6},
]

IT565_DIAG = [
    {"diagnostic_id": "D_LAIT565_EFILE_MANDATE", "severity": "error",
     "title": "⚠ Composite returns are E-FILE ONLY by statute — a paper filing is not valid",
     "condition": "composite_filed",
     "message": ("R.S. 47:201.1(F)(4), verbatim: 'Composite returns shall be filed electronically.' A paper IT-565 "
                 "carrying Schedule 6922 is NOT a legal filing. Delvio v1 is COMPUTE-AND-REVIEW ONLY for Louisiana "
                 "(campaign D-16 A2) — the figures here are correct and reviewable, but the return must be "
                 "transmitted through an LDR-approved e-file channel. Prepare the electronic filing separately."),
     "notes": "D-16 A2. Clears when LA MeF output lands (U5)."},
    {"diagnostic_id": "D_LAIT565_INFORMATIONAL", "severity": "info",
     "title": "IT-565 is an INFORMATION return — no entity-level tax",
     "condition": "always",
     "message": ("R.S. 47:201 / 47:103(A)(2): the partnership is not subject to Louisiana income tax and the IT-565 "
                 "computes none. Louisiana tax arises only via Schedule 6922 (the embedded composite for "
                 "nonresident partners) or, on a R-6980 election, on the CIT-620 instead."),
     "notes": "Structural."},
    {"diagnostic_id": "D_LAIT565_DUAL_ENGINE", "severity": "warning",
     "title": "Dual-engine partnership — both schedule sets are required",
     "condition": "has_corporate_partners and has_noncorporate_partners",
     "message": ("This partnership has BOTH corporate and non-corporate partners, so it files Schedules D/E/G AND "
                 "Schedules H/I/J and reports TWO different Louisiana net incomes on one return (walk W7). Verify "
                 "both schedule sets are complete — the engine does not assume a single method."),
     "notes": "W7."},
    {"diagnostic_id": "D_LAIT565_NO_BONUS_ADDBACK", "severity": "info",
     "title": "Louisiana has NO federal bonus depreciation add-back",
     "condition": "federal_bonus_depreciation > 0",
     "message": ("Louisiana conforms by rolling reference and its addition statute (R.S. 47:287.71) contains no "
                 "depreciation item — there is NO bonus add-back to make (established affirmatively in "
                 "conformity/la_conformity.md; a commercial-publisher claim to the contrary was refuted). Do not "
                 "look for an add-back line. What DOES exist is the ELECTIVE state 100%-expensing regime "
                 "(R.S. 47:287.744 / 47:297.25) — separate, opt-in, and RED-deferred pending Form R-90158 (U1)."),
     "notes": "conformity §3."},
    {"diagnostic_id": "D_LAIT565_R90158_DEFER", "severity": "error",
     "title": "State expensing election claimed — Form R-90158 is RED-DEFERRED (no published form exists)",
     "condition": "state_expensing_election",
     "message": ("The La. R.S. 47:297.25 / 47:287.744 elective 100%-expensing regime requires Form R-90158 "
                 "(Bonus Depreciation Schedule) as an attachment. ⚠ R-90158 has NO PUBLISHED PDF ANYWHERE as of "
                 "2026-08-22 — both LDR forms indexes, LDR site search and a web-wide sweep returned nothing, "
                 "though it is named as required in five TY2025 booklets and RIB 25-012. Prepare the election and "
                 "its schedule MANUALLY and re-check the LDR index before filing (U1)."),
     "notes": "U1 — firm RED-defer, re-check before the app build."},
]

CIT620_DIAG = [
    {"diagnostic_id": "D_LACIT620_TRACK", "severity": "info",
     "title": "CIT-620 serves three tracks — confirm which one this return is",
     "condition": "always",
     "message": ("Louisiana has no S-corporation return and no PTE-specific return. This form serves (a) an "
                 "ELECTING pass-through entity (Line O marked; Schedule H-1 at 3%), (b) a NON-ELECTING S "
                 "corporation computing AS A C CORPORATION at 5.5% with the Line 1B exclusion, and (c) an ordinary "
                 "C corporation. The track drives the rate, the exclusion and the owner-side treatment — verify it "
                 "before relying on any figure."),
     "notes": "D-16 A1."},
    {"diagnostic_id": "D_LACIT620_ELECT_EFILE", "severity": "error",
     "title": "⚠ Electing-PTE returns are e-file mandated (LAC 61:I.1001(C)(2))",
     "condition": "pte_election_active",
     "message": ("LAC 61:I.1001(C)(2) requires electronic filing for electing pass-through entities. Delvio v1 is "
                 "COMPUTE-AND-REVIEW ONLY for Louisiana (D-16 A2) — transmit through an LDR-approved e-file "
                 "channel. Required companions: R-6981 (each owner's share) and R-6982 (tax paid), plus the "
                 "owners' pro-forma federal 1040/1041 excluding entity-taxed items (LAC 61:I.1001 C.4.d)."),
     "notes": "D-16 A2."},
    {"diagnostic_id": "D_LACIT620_ELECTION_STATUS", "severity": "warning",
     "title": "Election status is client-record data — R-6980 requires LDR ACCEPTANCE",
     "condition": "pte_election_active",
     "message": ("The R.S. 47:287.732.2 election is made on Form R-6980, submitted BY EMAIL to LDR, and is not "
                 "effective until LDR ACCEPTS it; nothing on this return reveals its status. It is perpetual until "
                 "terminated on Form R-6983, which must be filed by NOVEMBER 1 to take effect PROSPECTIVELY for "
                 "the following year, and a 5-YEAR RE-ELECTION LOCKOUT follows. Record the acceptance-letter date "
                 "on the client record (walk W6). Composite filing and the election are MUTUALLY EXCLUSIVE."),
     "notes": "W6."},
    {"diagnostic_id": "D_LACIT620_SCORP_EXCL_INPUTS", "severity": "warning",
     "title": "Line 1B numerator includes nonresidents who FILED AND PAID — attachment required",
     "condition": "is_s_corporation and not pte_election_active",
     "message": ("The Line 1B exclusion ratio's numerator is NOT a simple residency count: it includes shares held "
                 "by NONRESIDENT individuals who filed a correct Louisiana return AND PAID the tax — a compliance "
                 "fact outside this entity's return (walk W4). The engine never infers it. Supply the ratio with "
                 "the supporting per-shareholder schedule attached. ⚠ This exclusion DIES for TY2026 (Act 382)."),
     "notes": "W4."},
    {"diagnostic_id": "D_LACIT620_STD_DED_U7", "severity": "warning",
     "title": "U7 OPEN — may an ELECTING PTE take the $20,000 standard deduction?",
     "condition": "pte_election_active and la_net_income > 0",
     "message": ("Schedule F line 3f's printed test is 'corporations subject to income tax pursuant to "
                 "R.S. 47:287.11'. An electing PTE is taxed under R.S. 47:287.732.2(B) at the INDIVIDUAL rate, "
                 "not under §287.11 — which cuts AGAINST eligibility — but no LDR instruction addresses electing "
                 "PTEs either way, and the TY2026 S-corp denial is rationalized on exactly that ground. Unresolved "
                 "([UNVERIFIED] U7): decide it on the return and document the position."),
     "notes": "U7."},
    {"diagnostic_id": "D_LACIT620_PROFORMA", "severity": "warning",
     "title": "Schedule F Line 1 requires a pro-forma Subchapter-C computation — direct entry in v1",
     "condition": "pte_election_active or is_s_corporation",
     "message": ("CIT-620 Schedule F Line 1 requires net income computed 'on a separate Subchapter C corporation "
                 "basis' — effectively a shadow federal 1120. Delvio v1 takes this figure by DIRECT ENTRY "
                 "(campaign D-16 A3); it does not synthesize the shadow return from 1065/1120-S data. Prepare the "
                 "pro-forma computation and attach the worksheet."),
     "notes": "D-16 A3 / W3."},
    {"diagnostic_id": "D_LACIT620_TY2026_CLIFF", "severity": "info",
     "title": "⚠ TY2026 re-authoring event — four acts pivot at 1/1/2026",
     "condition": "always",
     "message": ("Already printed on the TY2025 form: Act 6 repeals the corporate FRANCHISE tax (which is why this "
                 "form is CIT-620, not CIFT-620); Acts 5 and 11 set the 5.5% and 3% rates; and ACT 382 flips S "
                 "CORPORATIONS to INFORMATION filers for TY2026 with new Schedules K/L and a composite, ENDS the "
                 "Line 1B exclusion, and BARS the PTE election for S-corp composite filers. TY2026 is a "
                 "re-authoring event, not a constant bump. ⚠ Vintage trap: the currently codified "
                 "R.S. 47:287.732 is ALREADY the Act 382 rewrite — TY2025 authority is the CIT-620i booklet."),
     "notes": "W5 / conformity §10."},
    {"diagnostic_id": "D_LACIT620_NO_BONUS_ADDBACK", "severity": "info",
     "title": "Louisiana has NO federal bonus depreciation add-back",
     "condition": "federal_bonus_depreciation > 0",
     "message": ("Rolling conformity with no depreciation item in R.S. 47:287.71 — there is no add-back to make. "
                 "The ELECTIVE state 100%-expensing regime (R.S. 47:287.744) is separate and opt-in, with IRC "
                 "definitions frozen 1/1/2024 and an out-year add-back on STATE-EXPENSED property only; it "
                 "requires Form R-90158, which is unpublished (U1) and therefore RED-deferred."),
     "notes": "conformity §3."},
    {"diagnostic_id": "D_LACIT620_OILGAS_DEFER", "severity": "error",
     "title": "Oil & gas four-ratio apportionment — prepare manually (RED-defer)",
     "condition": "is_oil_and_gas",
     "message": ("Louisiana's default is a SINGLE revenue ratio (R.S. 47:287.95(F)) with MARKET-BASED sourcing "
                 "(R.S. 47:287.95(L): services sourced to the delivery location; individuals by billing address; "
                 "intangibles by use). The oil-and-gas four-ratio variant is not modelled in v1 — prepare "
                 "Schedule B Lines 2-4 / Schedule C manually."),
     "notes": "RED-defer."},
    {"diagnostic_id": "D_LACIT620_SEPACCT_DEFER", "severity": "error",
     "title": "Separate-accounting method — prepare manually (RED-defer)",
     "condition": "separate_accounting",
     "message": "Separate-accounting returns follow a different Schedule D/G chain and are not modelled in v1.",
     "notes": "RED-defer."},
]

IT565_SCEN = [
    {"scenario_name": "IT565-A — composite tax at 3% (Schedule 6922)", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"composite_filed": True, "nonresident_partner_la_share": 500000},
     "expected_outputs": {"composite_tax": 15000},
     "notes": "500,000 LA-source nonresident shares x 3% = 15,000. Per partner: Sch B Col O = Col N x 3%; Sch 6922 L1/L2 are the column totals."},
    {"scenario_name": "IT565-B — the partnership itself is NOT taxed", "scenario_type": "edge", "sort_order": 2,
     "inputs": {"federal_ordinary_income": 900000, "composite_filed": False},
     "expected_outputs": {"partnership_income_tax": 0},
     "notes": "R.S. 47:201 — an information return. A non-electing partnership with only resident partners computes NO Louisiana tax on the IT-565."},
    {"scenario_name": "IT565-C — composite triggers the statutory e-file mandate", "scenario_type": "edge", "sort_order": 3,
     "inputs": {"composite_filed": True, "nonresident_partner_la_share": 100000},
     "expected_outputs": {"composite_tax": 3000, "efile_required": True, "diagnostic": "D_LAIT565_EFILE_MANDATE"},
     "notes": "R.S. 47:201.1(F)(4) — paper is not a legal filing. v1 computes and reviews; transmission is out of scope (D-16 A2)."},
    {"scenario_name": "IT565-D — dual-engine partnership needs BOTH schedule sets", "scenario_type": "edge", "sort_order": 4,
     "inputs": {"has_corporate_partners": True, "has_noncorporate_partners": True},
     "expected_outputs": {"required_schedule_sets": ["D/E/G", "H/I/J"], "diagnostic": "D_LAIT565_DUAL_ENGINE"},
     "notes": "W7 — two Louisiana net incomes on one return."},
]

CIT620_SCEN = [
    {"scenario_name": "CIT620-A — ELECTING PTE at 3% (Schedule H-1)", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"pte_election_active": True, "is_s_corporation": True, "la_net_income": 1000000},
     "expected_outputs": {"track": "electing_pte", "pte_tax": 30000, "line_1B": 0},
     "notes": "1,000,000 x 3% = 30,000 (R.S. 47:287.732.2(B) -> 47:32). ⚠ An electing entity takes NO Line 1B S-corp exclusion — the two are mutually exclusive."},
    {"scenario_name": "CIT620-B — NON-ELECTING S CORP computes as a C CORP at 5.5% with the Line 1B exclusion", "scenario_type": "normal", "sort_order": 2,
     "inputs": {"pte_election_active": False, "is_s_corporation": True, "la_net_income": 1000000,
                "la_resident_shares": 600, "total_shares": 1000},
     "expected_outputs": {"track": "nonelecting_scorp", "line_1B": 600000, "corp_tax_on_400000": 22000},
     "notes": ("THE TRACK-3 PIN. 1B = 1,000,000 x (600/1,000) = 600,000; taxable 400,000 x 5.5% = 22,000. The "
               "1120S module's Louisiana return IS the C-corp computation — this is why LA_CIT620 is authored in "
               "full (D-16 A1). ⚠ The numerator also counts nonresidents who filed AND paid (W4).")},
    {"scenario_name": "CIT620-C — ordinary C corporation, no exclusion", "scenario_type": "normal", "sort_order": 3,
     "inputs": {"pte_election_active": False, "is_s_corporation": False, "la_net_income": 1000000},
     "expected_outputs": {"track": "c_corp", "line_1B": 0, "corp_tax": 55000},
     "notes": "1,000,000 x 5.5% = 55,000. No S-corp exclusion for a C corporation."},
    {"scenario_name": "CIT620-D — NOL utilization capped at 72%", "scenario_type": "edge", "sort_order": 4,
     "inputs": {"la_net_income": 1000000, "nol_carryforward": 900000},
     "expected_outputs": {"line_1C1": 720000},
     "notes": "min(72% x 1,000,000 = 720,000 ; carryforward 900,000) = 720,000. The unused 180,000 carries forward INDEFINITELY (federal §172 inoperative)."},
    {"scenario_name": "CIT620-E — NOL smaller than the cap", "scenario_type": "edge", "sort_order": 5,
     "inputs": {"la_net_income": 1000000, "nol_carryforward": 500000},
     "expected_outputs": {"line_1C1": 500000},
     "notes": "The cap does not create deduction — min(720,000 ; 500,000) = 500,000."},
    {"scenario_name": "CIT620-F — $20,000 standard deduction floors and caps", "scenario_type": "edge", "sort_order": 6,
     "inputs": {"modified_la_net_income_before_3f": 12000},
     "expected_outputs": {"line_3f": 12000},
     "notes": "min(20,000 ; 12,000) = 12,000, floored at 0. ⚠ U7: electing-PTE eligibility is unresolved."},
    {"scenario_name": "CIT620-G — the two 3% rates are SEPARATE constants", "scenario_type": "edge", "sort_order": 7,
     "inputs": {"composite_rate_source": "R.S. 47:201.1(D)(1)", "pte_rate_source": "R.S. 47:287.732.2(B)"},
     "expected_outputs": {"same_value": True, "same_constant": False},
     "notes": ("Both resolve to the individual rate (R.S. 47:32) and both are 3% for TY2025 — which is exactly why "
               "a spec collapses them by accident. Two authority chains, two constants. The CO R-CO-RATES lesson.")},
    {"scenario_name": "CIT620-H — no bonus add-back exists", "scenario_type": "edge", "sort_order": 8,
     "inputs": {"federal_bonus_depreciation": 400000},
     "expected_outputs": {"la_bonus_addback": None, "diagnostic": "D_LACIT620_NO_BONUS_ADDBACK"},
     "notes": "Rolling conformity, no depreciation item in R.S. 47:287.71. Never code a GA-shaped add-back for Louisiana."},
]

FORMS: list[dict] = [
    {"identity": {"form_number": "LA_IT565", "entity_types": ["1065"],
                  "form_title": "Louisiana Form IT-565 — Partnership Return of Income (TY2025), incl. Schedule 6922 composite",
                  "notes": ("WO-W06-LA-PILOT (campaign D-14/D-15/D-16). INFORMATION return (R.S. 47:201) — the "
                            "partnership is not taxed. The nonresident composite is EMBEDDED as Schedule 6922 at "
                            "3% (standalone R-6922 abolished TY2021) and is E-FILE ONLY by statute "
                            "(R.S. 47:201.1(F)(4)). Partner rosters live in the Schedules A/B Excel workbook. "
                            "Dual-engine partnerships (corporate + non-corporate partners) file BOTH D/E/G and "
                            "H/I/J. v1 = compute-and-review only (D-16 A2).")},
     "facts": IT565_FACTS, "rules": IT565_RULES, "rule_links": IT565_RULE_LINKS,
     "lines": IT565_LINES, "diagnostics": IT565_DIAG, "scenarios": IT565_SCEN},
    {"identity": {"form_number": "LA_CIT620", "entity_types": ["1120S", "1120"],
                  "form_title": "Louisiana Form CIT-620 — Corporation Income Tax Return (TY2025; renamed from CIFT-620)",
                  "notes": ("WO-W06-LA-PILOT (campaign D-14/D-15/D-16 A1 — authored IN FULL, C-corp computation "
                            "included). ONE form, THREE tracks: electing PTE (Line O, Schedule H-1, 3%); "
                            "NON-ELECTING S CORP computed AS A C CORPORATION at 5.5% with the Line 1B "
                            "resident-share exclusion; ordinary C corporation. The 1120S module's Louisiana "
                            "return IS the C-corp computation, so the future 1120 module REUSES this spec. "
                            "Renamed CIFT-620 -> CIT-620 (franchise repealed eff. 1/1/2026). 72% NOL cap, "
                            "indefinite carryforward; $20,000 standard deduction (U7 open for electing PTEs); "
                            "pro-forma Subchapter-C figure is DIRECT ENTRY (D-16 A3). NO federal bonus add-back. "
                            "⚠ TY2026 = re-authoring event (Act 382).")},
     "facts": CIT620_FACTS, "rules": CIT620_RULES, "rule_links": CIT620_RULE_LINKS,
     "lines": CIT620_LINES, "diagnostics": CIT620_DIAG, "scenarios": CIT620_SCEN},
]

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-LAIT565-COMPOSITE", "title": "Schedule 6922 composite tax = 3% of nonresident LA-source shares",
     "assertion_type": "reconciliation", "entity_types": ["1065"], "status": "draft", "sort_order": 1,
     "description": ("Sch 6922 L2 = Sch B Column O total, and Column O = Column N x 3% per partner, so L2 = L1 x 3%. "
                     "The per-partner computation and the total must agree."),
     "definition": {"rule": "R-LAIT565-COMPOSITE", "check": "sch6922_L2 = sch6922_L1 * 0.03 = sum(per_partner_col_O)"}},
    {"assertion_id": "FA-LAIT565-NOTAX", "title": "The IT-565 computes NO entity-level tax",
     "assertion_type": "invariant", "entity_types": ["1065"], "status": "draft", "sort_order": 2,
     "description": "R.S. 47:201 — an information return. Any nonzero entity income tax on an IT-565 is a defect.",
     "definition": {"rule": "R-LAIT565-INFO", "check": "partnership_income_tax == 0"}},
    {"assertion_id": "FA-LACIT620-XOR", "title": "The PTE election and the S-corp exclusion are mutually exclusive",
     "assertion_type": "invariant", "entity_types": ["1120S", "1120"], "status": "draft", "sort_order": 3,
     "description": "An electing entity (Line O) takes NO Line 1B exclusion, and the rate forks with it (3% vs 5.5%).",
     "definition": {"rule": "R-LACIT620-FORK", "check": "pte_election_active implies line_1B == 0 and rate == 0.03"}},
    {"assertion_id": "FA-LACIT620-TAXABLE", "title": "Line 1D = 1A − 1B − 1C1, and 1E applies the track's rate",
     "assertion_type": "reconciliation", "entity_types": ["1120S", "1120"], "status": "draft", "sort_order": 4,
     "description": "The Louisiana taxable-income chain and the rate fork, in one assertion.",
     "definition": {"rule": "R-LACIT620-CORP-TAX", "check": "line_1D = line_1A - line_1B - line_1C1 ; line_1E = line_1D * (0.03 if electing else 0.055)"}},
    {"assertion_id": "FA-LACIT620-NOL-CAP", "title": "NOL utilization never exceeds 72% of Louisiana net income",
     "assertion_type": "invariant", "entity_types": ["1120S", "1120"], "status": "draft", "sort_order": 5,
     "description": "R.S. 47:287.86. The cap binds even when a larger carryforward exists; the remainder carries forward indefinitely.",
     "definition": {"rule": "R-LACIT620-NOL", "check": "line_1C1 <= la_net_income * 0.72"}},
]


class Command(BaseCommand):
    help = ("Load the Louisiana pass-through specs (IT-565 + CIT-620, TY2025). "
            "Refuses to seed until READY_TO_SEED=True (Gate-1 SEED approval).")

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad Louisiana pass-through specs (IT-565 + CIT-620)\n"))
        self._load_topics()
        sources = self._load_sources()
        for spec in FORMS:
            form = self._upsert_form(spec["identity"])
            self._upsert_facts(form, spec["facts"])
            rules = self._upsert_rules(form, spec["rules"])
            self._upsert_links(rules, sources, spec["rule_links"])
            self._upsert_lines(form, spec["lines"])
            self._upsert_diag(form, spec["diagnostics"])
            self._upsert_tests(form, spec["scenarios"])
        self._upsert_form_links(sources)
        self._load_fa()
        self._report()

    def _guard(self):
        empty = []
        for spec in FORMS:
            fn = spec["identity"]["form_number"]
            for key in ("facts", "rules", "lines", "diagnostics", "scenarios", "rule_links"):
                if not spec[key]:
                    empty.append(f"{fn}.{key}")
        if not FLOW_ASSERTIONS:
            empty.append("FLOW_ASSERTIONS")
        # Louisiana-specific refusals — the traps that would ship a wrong return.
        for spec in FORMS:
            for r in spec["rules"]:
                f = (r.get("formula") or "").lower()
                if "bonus" in f and "addback" in f and "none" not in f:
                    empty.append(f"{spec['identity']['form_number']}: a bonus ADD-BACK was invented "
                                 "(Louisiana has none — see R-LACIT620-NOBONUS)")
        if not READY_TO_SEED or empty:
            still = "\n  ".join(f"- {n}" for n in empty) or "(all populated)"
            raise CommandError(
                "\nREFUSING TO SEED the Louisiana specs: not cleared.\n\n"
                "Campaign D-16 approved the SCOPE (A1 full CIT-620 incl. the C-corp computation with\n"
                "Schedule 6922 inside LA_IT565; A2 compute-and-review-only v1; A3 pro-forma direct entry).\n"
                "The SEED approval is a SEPARATE Gate-1 step and has not been given.\n\n"
                f"READY_TO_SEED = {READY_TO_SEED}\n\nEmpty / refused:\n  {still}\n"
            )

    def _load_topics(self):
        ct = 0
        for code, name in AUTHORITY_TOPICS:
            _, created = AuthorityTopic.objects.update_or_create(topic_code=code, defaults={"topic_name": name})
            ct += 1 if created else 0
        self.stdout.write(f"Topics: {ct} new")

    def _load_sources(self) -> dict:
        sources: dict = {}
        for sd in AUTHORITY_SOURCES:
            sd = dict(sd)
            exc = sd.pop("excerpts", [])
            tcs = sd.pop("topics", [])
            src, _ = AuthoritySource.objects.update_or_create(source_code=sd["source_code"], defaults=sd)
            sources[src.source_code] = src
            for e in exc:
                e = dict(e)
                AuthorityExcerpt.objects.update_or_create(
                    authority_source=src, excerpt_label=e["excerpt_label"], defaults=e)
            for tc in tcs:
                t = AuthorityTopic.objects.filter(topic_code=tc).first()
                if t:
                    AuthoritySourceTopic.objects.get_or_create(authority_source=src, authority_topic=t)
        # ⚠ D-42: these two lists existed and were NEVER READ. One module DECLARES a
        #   source, every other REFERENCES it (D-29) — that only works if both halves run.
        _wire.resolve_references(EXISTING_SOURCES_TO_REFERENCE, sources, self.stdout.write)
        self.stdout.write(f"Sources ready: {len(sources)}")
        return sources

    def _upsert_form(self, identity: dict) -> TaxForm:
        form, created = TaxForm.objects.update_or_create(
            form_number=identity["form_number"], jurisdiction=FORM_JURISDICTION,
            tax_year=FORM_TAX_YEAR, version=FORM_VERSION,
            defaults={"form_title": identity["form_title"], "entity_types": identity["entity_types"],
                      "status": FORM_STATUS, "notes": identity["notes"]},
        )
        self.stdout.write(f"{'Created' if created else 'Updated'} {identity['form_number']} {identity['entity_types']}")
        return form

    # NOTE: every upsert below PRUNES rows this loader no longer declares.
    # Added campaign-wide 2026-08-22 after the NC reseed shipped a repealed
    # pre-2023 fact and scenario alongside their replacements — renaming a
    # name-keyed row creates a duplicate and leaves the original live.
    def _prune(self, qs, label):
        n = qs.count()
        if n:
            qs.delete()
            self.stdout.write(self.style.WARNING(f"  pruned {n} stale {label}"))

    def _upsert_facts(self, form, facts):
        keys = {f["fact_key"] for f in facts}
        for f in facts:
            f = dict(f)
            FormFact.objects.update_or_create(tax_form=form, fact_key=f.pop("fact_key"), defaults=f)
        self._prune(FormFact.objects.filter(tax_form=form).exclude(fact_key__in=keys), "facts")
        self.stdout.write(f"  {len(facts)} facts")

    def _upsert_rules(self, form, rules_data) -> dict:
        created = {}
        ids = {r["rule_id"] for r in rules_data}
        for r in rules_data:
            r = dict(r)
            rule, _ = FormRule.objects.update_or_create(tax_form=form, rule_id=r.pop("rule_id"), defaults=r)
            created[rule.rule_id] = rule
        self._prune(FormRule.objects.filter(tax_form=form).exclude(rule_id__in=ids), "rules")
        self.stdout.write(f"  {len(created)} rules")
        return created

    def _upsert_links(self, rules, sources, rule_links):
        ct = 0
        for rid, sc, lvl, note in rule_links:
            rule, src = rules.get(rid), sources.get(sc)
            if rule and src:
                RuleAuthorityLink.objects.get_or_create(
                    form_rule=rule, authority_source=src,
                    defaults={"support_level": lvl, "relevance_note": note})
                ct += 1
        self.stdout.write(f"  {ct} authority links")

    def _upsert_lines(self, form, lines):
        nums = {ln["line_number"] for ln in lines}
        for ln in lines:
            ln = dict(ln)
            FormLine.objects.update_or_create(tax_form=form, line_number=ln.pop("line_number"), defaults=ln)
        self._prune(FormLine.objects.filter(tax_form=form).exclude(line_number__in=nums), "lines")
        self.stdout.write(f"  {len(lines)} lines")

    def _upsert_diag(self, form, diags):
        ids = {d["diagnostic_id"] for d in diags}
        for d in diags:
            d = dict(d)
            FormDiagnostic.objects.update_or_create(
                tax_form=form, diagnostic_id=d.pop("diagnostic_id"), defaults=d)
        self._prune(FormDiagnostic.objects.filter(tax_form=form).exclude(diagnostic_id__in=ids), "diagnostics")
        self.stdout.write(f"  {len(diags)} diagnostics")

    def _upsert_tests(self, form, scenarios):
        names = {t["scenario_name"] for t in scenarios}
        for t in scenarios:
            t = dict(t)
            TestScenario.objects.update_or_create(
                tax_form=form, scenario_name=t.pop("scenario_name"), defaults=t)
        self._prune(TestScenario.objects.filter(tax_form=form).exclude(scenario_name__in=names), "test scenarios")
        self.stdout.write(f"  {len(scenarios)} test scenarios")

    def _upsert_form_links(self, sources):
        for sc, fc, lt in AUTHORITY_FORM_LINKS:
            src = sources.get(sc) or AuthoritySource.objects.filter(source_code=sc).first()
            if src:
                AuthorityFormLink.objects.get_or_create(
                    authority_source=src, form_code=fc, link_type=lt, defaults={"note": f"{sc} -> {fc}"})

    def _load_fa(self):
        for a in FLOW_ASSERTIONS:
            a = dict(a)
            FlowAssertion.objects.update_or_create(assertion_id=a.pop("assertion_id"), defaults=a)
        self.stdout.write(f"  {len(FLOW_ASSERTIONS)} flow assertions")

    def _report(self):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("Louisiana pass-through specs loaded.")
        for spec in FORMS:
            i = spec["identity"]
            self.stdout.write(
                f"  {i['form_number']}: facts {len(spec['facts'])} / rules {len(spec['rules'])} / "
                f"lines {len(spec['lines'])} / diag {len(spec['diagnostics'])} / tests {len(spec['scenarios'])}")
        self.stdout.write(f"  flow assertions: {len(FLOW_ASSERTIONS)}")
        self.stdout.write("=" * 60)
