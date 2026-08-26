"""Load the NC pass-through entity specs — D-403 (Partnership) + CD-401S (S-Corp) + NC Taxed PTE (TY2025).
WO-13, the NC + AL pass-through batch (NC half). Completes the adjacent-state pass-through track.

═══════════════════════════════════════════════════════════════════════════
WHAT THIS IS
═══════════════════════════════════════════════════════════════════════════
Two NC pass-through returns in one loader (mirrors load_sc_passthrough.py):
  • NC_D403 — NC Partnership Income Tax Return (federal 1065 start).
  • NC_CD401S — NC S-Corporation Tax Return (federal 1120-S start) — and CD-401S DOES compute the
    NC FRANCHISE TAX on the S-corp (net-worth base, same as CD-405).
THE HEADLINE: the NC Taxed PTE election (S.L. 2021-180). Unlike AL's 5%/credit design, NC's is at the
INDIVIDUAL RATE (4.25% for 2025) and the owner-side is a DEDUCTION — the electing owner removes their
share of the Taxed-PTE income from NC AGI (via NC-PE), NOT a credit. Reuses the NC D-400/CD-405
depreciation work (85% bonus add-back + §179 $25k/$200k) and the CD-405 franchise mechanic.

Greenfield: no NC_D403 / NC_CD401S at the 2026-07-05 gap-check.

═══════════════════════════════════════════════════════════════════════════
v1 SCOPE — LOCKED (Ken's Gate-1 walk 2026-07-05; DECISIONS D-15). See nc_al_passthrough_source_brief.md.
═══════════════════════════════════════════════════════════════════════════
COMPUTES (Q1 full + Q2 owner side): the Taxed-PTE tax (4.25%) with the owner DEDUCTION; NC nonresident
withholding (4.25%); the CD-401S franchise tax (net worth); the 85% bonus / §179 $25k/$200k add-back;
single sales factor (4 dec).

requires_human_review WALK ITEMS (W1-W3):
W1. [CORRECTED 2026-08-22, D-16/NC-1 -- the original base was STALE PRE-2023 LAW] NC Taxed PTE = 4.25%
    (individual rate) on the NC-ATTRIBUTABLE shares of owners NOT classified as corporations/partnerships.
    G.S. 105-154.1(b)(1)b / 105-131.1A(b)(1)b's resident non-NC-share component was REPEALED effective
    TY2023+ ("(Repealed effective for taxable years beginning on or after January 1, 2023)"). Owner side =
    DEDUCTION (D-400 Schedule S Line 38a for individuals; NC-PE Part B Line 38a for PTE owners), NOT a credit.
W2. [CORRECTED 2026-08-22, D-16/NC-2 -- the original cloned the CD-405 C-CORP mechanic] CD-401S franchise:
    "$200 for the first one million dollars" + $1.50/$1,000 (.0015) of the base OVER $1,000,000; $200 minimum;
    $150,000 holding-company cap. (2025 CD-401S Sch A Line 2 verbatim: "If Line 1 <= $1,000,000, the minimum
    tax due of $200 is applicable. If Line 1 > $1,000,000, multiply the amount over $1,000,000 by .0015 and
    add $200.") D-403 partnerships pay NO franchise.
W3. Depreciation decouple (85% bonus add-back + §179 $25k/$200k) + single sales factor (4 dec); conformity
    Jan 1 2023 (OBBBA not adopted). CONFIRM.

[UNVERIFIED] CLEARED 2026-08-22: the 2025 PDFs now text-extract; every line number verified against the
FINAL TY2025 NCDOR PDFs (delvio-states research/alnc_ty2025_repull_report.md). That re-pull also found the
TWO COMPUTATIONAL defects corrected in this revision (NC-1 Taxed-PTE base, NC-2 franchise mechanic) plus five
secondary corrections (NC-3..NC-7), all applied here per Ken's Gate-1 approval (campaign D-16, 2026-08-22).
NC rate/§179 stay year-keyed. Re-verify at TY2026.

SAFETY GUARD — READY_TO_SEED stays False until Ken approves the review walk (W1-W3).
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

# FLIPPED 2026-07-05 — Ken APPROVED ("Approve — flip, seed, export"): W1 Taxed PTE 4.25% +
# owner DEDUCTION, W2 CD-401S NC franchise, W3 depreciation (85%/§179 $25k/$200k) + apportionment.
# Validated (scratchpad/validate_nc_al_pt.py, 47/0). Line-number [UNVERIFIED] noted for re-pull.
READY_TO_SEED = True

FORM_JURISDICTION = "NC"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"

# Verified constants (nc_al_passthrough_source_brief.md; 2025 NCDOR sources)
NC_PTET_RATE = "0.0425"            # Taxed PTE = individual rate (2025); §105-153.7 / S.L. 2021-180
NC_NRW_RATE = "0.0425"            # nonresident owner withholding = individual rate
NC_179_LIMIT = 25000              # G.S. §105-130.5B
NC_179_PHASEOUT = 200000
ADDBACK_PCT = "0.85"              # 85% bonus / §179-excess add-back
FRANCHISE_RATE = "0.0015"        # $1.50 per $1,000 of net worth OVER $1,000,000 (CD-401S Sch A L2)
FRANCHISE_FIRST_TIER = 1000000
FRANCHISE_FIRST_TIER_TAX = 200    # [D-16/NC-2] "$200 for the first one million dollars" -- NOT the CD-405
                                  # C-corp "$500 first-$1M cap" mechanic the first pass cloned
FRANCHISE_MIN = 200
FRANCHISE_HOLDING_CAP = 150000


def _nc_franchise(net_worth, is_holding=False) -> float:
    """NC S-corp franchise tax (CD-401S Sch A Line 2; base from Sch C Line 9).

    [D-16/NC-2] TY2025 CD-401S verbatim: "If Line 1 <= $1,000,000, the minimum
    tax due of $200 is applicable. If Line 1 > $1,000,000, multiply the amount
    over $1,000,000 by .0015 and add $200." NOT the CD-405 C-corp mechanic
    ($500 first-$1M cap) the first pass cloned. $2,000,000 net worth = $1,700.
    """
    nw = float(net_worth)
    fr = float(FRANCHISE_FIRST_TIER_TAX)
    if nw > FRANCHISE_FIRST_TIER:
        fr += (nw - FRANCHISE_FIRST_TIER) * float(FRANCHISE_RATE)
    fr = max(float(FRANCHISE_MIN), fr)
    if is_holding:
        fr = min(fr, float(FRANCHISE_HOLDING_CAP))
    return fr


def _nc_addback(bonus, s179) -> float:
    """NC 85% bonus + 85% of §179 over the NC $25,000 limit (recover 20%/yr over 5 yrs)."""
    return float(ADDBACK_PCT) * float(bonus) + float(ADDBACK_PCT) * max(0.0, float(s179) - NC_179_LIMIT)


def _nc_taxed_pte(nc_attributable_share_eligible) -> float:
    """NC Taxed PTE tax = 4.25% of the NC-ATTRIBUTABLE shares of eligible owners.

    [D-16/NC-1] Eligible = owners NOT classified as corporations/partnerships;
    residents count only to the extent NC-attributable. The resident-entire-share
    component was REPEALED effective TY2023+ (G.S. 105-154.1(b)(1)b /
    105-131.1A(b)(1)b). D-403 Part 4 Sec. E L24-25; CD-401S Sch B L17-19.
    """
    return float(nc_attributable_share_eligible) * float(NC_PTET_RATE)


AUTHORITY_TOPICS: list[tuple[str, str]] = [
    ("nc_passthrough_ptet", "NC pass-through returns (D-403 partnership / CD-401S S-corp) + the Taxed PTE "
     "election (S.L. 2021-180): 4.25% entity tax at the individual rate, owner-side DEDUCTION via NC-PE, "
     "85% bonus/§179 $25k/$200k decouple, CD-401S net-worth franchise."),
]

EXISTING_SOURCES_TO_REFERENCE: list[str] = [    "NC_GS_105_CORP",  # ownership -> load_nc_cd405.py (A3/D-42, 2026-08-25)
]

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "NC_2025_PTE_RETURNS", "source_type": "state_form", "source_rank": "primary_official",
        "jurisdiction_code": "NC", "title": "2025 NC D-403 (Partnership) + CD-401S (S-Corporation) Returns",
        "citation": "NC Form D-403 / CD-401S (2025)", "issuer": "North Carolina Department of Revenue",
        "official_url": "https://www.ncdor.gov/",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.4, "topics": ["nc_passthrough_ptet"],
        "excerpts": [{
            "excerpt_label": "D-403 / CD-401S structure + franchise + NR withholding (2025 substance)",
            "excerpt_text": (
                "D-403 (partnership) starts from federal Form 1065; CD-401S (S-corp) from federal 1120-S; NC "
                "adjustments flow to owners via NC-PE. 85% bonus depreciation add-back (recover 20%/yr over 5 "
                "years from 2026); NC §179 $25,000/$200,000 (add-back = (federal − NC) × 85%). Single sales "
                "factor, four decimals (§105-130.4). CD-401S computes the NC FRANCHISE TAX on the S-corp "
                "(base on Sch C, TAX on Sch A Line 2): $200 for the first $1,000,000 + $1.50 per $1,000 (.0015) of "
                "the excess, minimum $200, holding-company cap $150,000 [D-16/NC-2]. D-403 partnerships pay NO "
                "franchise. The entity pays NC tax on each nonresident owner's NC-source share at the individual "
                "rate (4.25% for 2025); relief: D-403 via Form NC-NPA (entity-type partners only), CD-401S via "
                "Form NC-NA + composite [D-16/NC-5]. Each owner receives an NC K-1. Due 15th day of 4th month "
                "(April 15, 2026)."
            ),
            "summary_text": "D-403 from 1065, CD-401S from 1120-S; 85% bonus/§179 $25k/$200k; single sales factor 4 dec; CD-401S franchise (net worth, $500 cap/$200 min); NR withholding 4.25%.",
            "is_key_excerpt": True,
        }],
    },
    {
        "source_code": "NC_SL_2021_180", "source_type": "statute", "source_rank": "controlling",
        "jurisdiction_code": "NC", "title": "NC Taxed Pass-Through Entity election (S.L. 2021-180)",
        "citation": "N.C. Gen. Stat. §105-131.7 (Taxed S Corp); §105-154(c) (Taxed Partnership); §105-153.7(a)", "issuer": "North Carolina General Assembly",
        "official_url": "https://www.ncleg.gov/",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.3, "topics": ["nc_passthrough_ptet"],
        "excerpts": [{
            "excerpt_label": "Taxed PTE — 4.25% + owner DEDUCTION [base CORRECTED for TY2023+, D-16/NC-1]",
            "excerpt_text": (
                "The Taxed PTE tax is 'imposed at the individual income tax rate for the applicable taxable "
                "year' (4.25% for 2025). ⚠ BASE, TY2023 AND LATER: the NC-attributable shares of owners not "
                "classified as corporations or partnerships. G.S. 105-154.1(b)(1)b and 105-131.1A(b)(1)b — the "
                "resident owner's share 'not attributable to the State' — carry '(Repealed effective for "
                "taxable years beginning on or after January 1, 2023)' verbatim; the Important-Notice base "
                "language quoted by the first pass ('Each resident Owner's share ... not attributable to North "
                "Carolina') is SUPERSEDED for TY2023+. 2025 D-403A: entity-level tax 'on the aggregate amount "
                "of income attributable to North Carolina for all partners except partners classified as "
                "corporations or partnerships' (D-403 Part 4 Sec. E L24-25; CD-401S Sch B L17-19). Owner side: "
                "the owner DEDUCTS — individuals at D-400 Schedule S Line 38a ('Taxed Pass-Through Entity "
                "Income – N.C. Sourced'); PTE owners at NC-PE Part B Line 38a; L38b serves entity-level tax "
                "paid to ANOTHER state; NOT a credit, and the entity must not report the owner's share of NC "
                "entity-level tax on NC K-1 Line 9. Election on the timely-filed D-403/CD-401S, annual, and "
                "'may not make or revoke the election after the return is filed' (G.S. 105-131.1A(a)). A "
                "nonresident owner of a Taxed PTE need not file if the PTE share is the only NC income."
            ),
            "summary_text": "Taxed PTE 4.25%; base (TY2023+) = NC-attributable shares of non-corp/non-partnership owners (resident non-NC component REPEALED); owner DEDUCTS at D-400 Sch S L38a; election locked once the original return is filed.",
            "is_key_excerpt": True,
        }],
    },
]

# Added 2026-08-25 (campaign D-42) so the D-29 ownership remedy is
# available here. Empty: adding it changes nothing until an entry lands.
NEW_EXCERPTS_ON_EXISTING: list[tuple[str, dict]] = [    # Re-homed 2026-08-25 (campaign A3/D-42): NC_GS_105_CORP is DECLARED by load_nc_cd405.py.
    # This spec still contributes these excerpts; it no longer rewrites the row.
    ("NC_GS_105_CORP", {
                "excerpt_label": "Bonus/§179 add-back + franchise + single sales factor (re-declared, as CD-405)",
                "excerpt_text": (
                    "§105-130.5B (corporate) and §105-153.6 (AGI-side — the pass-through/individual authority, where "
                    "the $25,000/$200,000 figures are codified): 85% bonus/§179 add-back (20%/yr recovery). §105-122: "
                    "franchise tax on net worth ($1.50/$1,000, first $1M cap $500, $200 minimum, holding cap "
                    "$150,000; net-worth-only base per S.L. 2021-180; TY2025 CD-401S mechanic: $200 for the first $1M "
                    "+ .0015 x the excess, $200 minimum [D-16/NC-2]). §105-130.4: "
                    "single sales factor, market-based sourcing, four decimals. Conformity: IRC as of January 1, "
                    "2023 (OBBBA not adopted)."
                ),
                "summary_text": "§105-130.5B/§105-153.6 85% add-back + §179 $25k/$200k; §105-122 net-worth franchise ($200 first $1M + .0015 excess); §105-130.4 single sales factor; conformity Jan 1 2023.",
                "is_key_excerpt": True,
            }),
]

AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    ("NC_2025_PTE_RETURNS", "NC_D403", "governs"), ("NC_SL_2021_180", "NC_D403", "governs"),
    ("NC_GS_105_CORP", "NC_D403", "governs"),
    ("NC_2025_PTE_RETURNS", "NC_CD401S", "governs"), ("NC_SL_2021_180", "NC_CD401S", "governs"),
    ("NC_GS_105_CORP", "NC_CD401S", "governs"),
]

# ─────────────────────────── shared fact set (per form) ───────────────────────────
_PT_FACTS = [
    {"fact_key": "federal_income", "label": "Federal ordinary income (D-403: Form 1065 / CD-401S: Form 1120-S)", "data_type": "decimal", "required": False, "sort_order": 1},
    {"fact_key": "federal_bonus_depreciation", "label": "Federal §168(k) bonus depreciation (NC 85% add-back)", "data_type": "decimal", "required": False, "sort_order": 2},
    {"fact_key": "federal_section_179", "label": "Federal §179 deduction (for the NC $25k/$200k delta)", "data_type": "decimal", "required": False, "sort_order": 3},
    {"fact_key": "nc_bonus_recovery", "label": "NC bonus/§179 recovery — 20%/yr installments (NC-PE subtraction)", "data_type": "decimal", "required": False, "sort_order": 4},
    {"fact_key": "is_multistate", "label": "Multistate entity (apportion)? — if no, NC ratio = 100%", "data_type": "boolean", "required": False, "sort_order": 5},
    {"fact_key": "sales_nc", "label": "Sales within NC (single sales factor numerator)", "data_type": "decimal", "required": False, "sort_order": 6},
    {"fact_key": "sales_everywhere", "label": "Sales everywhere (denominator)", "data_type": "decimal", "required": False, "sort_order": 7},
    {"fact_key": "is_taxed_pte", "label": "Taxed PTE election made? (annual, on the timely-filed return)", "data_type": "boolean", "required": False, "sort_order": 8},
    {"fact_key": "nc_attributable_share_eligible", "label": "Taxed-PTE base — NC-ATTRIBUTABLE distributive shares of owners NOT classified as corporations/partnerships (residents only to the extent NC-attributable; post-2022 base, D-16/NC-1)", "data_type": "decimal", "required": False, "sort_order": 9},
    {"fact_key": "nonresident_nc_source_share", "label": "Nonresident owners' NC-source share (Taxed-PTE base + NR withholding base)", "data_type": "decimal", "required": False, "sort_order": 10},
    {"fact_key": "nrw_exempt", "label": "Nonresident withholding relieved? (D-403: Form NC-NPA, corp/partnership/trust/estate/tax-exempt partners ONLY; CD-401S: Form NC-NA + composite)", "data_type": "boolean", "required": False, "sort_order": 11},
]

_ADJ_RULE = {
    "rule_id": None, "title": "NC adjustments — 85% bonus + §179 excess add-back / recovery (NC-PE)", "rule_type": "calculation",
    "formula": "nc_additions = 0.85 * federal_bonus_depreciation + 0.85 * max(0, federal_section_179 - 25000) ; nc_subtractions = nc_bonus_recovery",
    "inputs": ["federal_bonus_depreciation", "federal_section_179", "nc_bonus_recovery"], "outputs": ["nc_additions", "nc_subtractions"], "sort_order": 1,
    "description": "W3. G.S. §105-130.5B — add back 85% of federal bonus + 85% of §179 over NC's $25,000 limit; recover 20%/yr over 5 years. Adjustments flow to owners via NC-PE.",
}
_APPORT_RULE = {
    "rule_id": None, "title": "Single sales factor apportionment (4 decimals)", "rule_type": "calculation",
    "formula": "nc_ratio = 1.0 if not is_multistate else round(sales_nc / sales_everywhere, 4)",
    "inputs": ["is_multistate", "sales_nc", "sales_everywhere"], "outputs": ["nc_ratio"], "sort_order": 2,
    "description": "W3. §105-130.4 single sales factor, market-based sourcing, four decimals.",
}
_PTET_RULE = {
    "rule_id": None, "title": "NC Taxed PTE tax — 4.25% of NC-attributable eligible-owner shares (owner DEDUCTION)", "rule_type": "calculation",
    "formula": ("if is_taxed_pte: taxed_pte_base = nc_attributable_share_eligible  # NC-attributable shares of "
                "owners NOT classified as corporations/partnerships; residents only to the extent NC-attributable ; "
                "taxed_pte_tax = taxed_pte_base * 0.0425 ; owner_side = individual owners DEDUCT via D-400 Schedule S "
                "Line 38a (Taxed PTE Income - N.C. Sourced); PTE owners via NC-PE Part B Line 38a"),
    "inputs": ["is_taxed_pte", "nc_attributable_share_eligible"], "outputs": ["taxed_pte_tax"], "sort_order": 3,
    "description": ("W1 [CORRECTED D-16/NC-1]. S.L. 2021-180 as amended. Taxed PTE tax = 4.25% (the individual rate) "
                    "on the NC-ATTRIBUTABLE distributive shares of owners not classified as corporations/partnerships "
                    "(D-403A: 'the aggregate amount of income attributable to North Carolina for all partners except "
                    "partners classified as corporations or partnerships'; D-403 Part 4 Sec. E L24-25; CD-401S Sch B "
                    "L17-19). The resident non-NC-share component was REPEALED eff. TY2023+ (G.S. 105-154.1(b)(1)b / "
                    "105-131.1A(b)(1)b). Corp/partnership owners of a Taxed Partnership remain under the NR payment "
                    "regime unless NC-NPA. OWNER SIDE is a DEDUCTION, not a credit: individuals at D-400 Sch S L38a "
                    "(L38b is for entity-level tax paid to ANOTHER state); the entity must NOT report the owner's "
                    "share of NC entity-level tax on NC K-1 Line 9. Election cannot be made or revoked after the "
                    "original return is filed (G.S. 105-131.1A(a); D-403A)."),
}
_NRW_RULE = {
    "rule_id": None, "title": "NC nonresident owner withholding — 4.25%", "rule_type": "calculation",
    "formula": "if not is_taxed_pte and not nrw_exempt: nonresident_withholding = nonresident_nc_source_share * 0.0425",
    "inputs": ["is_taxed_pte", "nrw_exempt", "nonresident_nc_source_share"], "outputs": ["nonresident_withholding"], "sort_order": 4,
    "description": ("W1 [CORRECTED D-16/NC-5]. The entity pays NC tax on each nonresident owner's NC-source share "
                    "at the individual rate (4.25% for 2025). Relief forks by form: D-403 partnerships use Form "
                    "NC-NPA -- and ONLY partners classified as corporation/partnership/trust/estate/tax-exempt are "
                    "eligible (NR individuals cannot opt out); CD-401S S-corps file Form NC-NA per nonresident "
                    "shareholder plus the composite mechanism (Sch B Lines 16/18/19). A Taxed-PTE election "
                    "substitutes the entity tax for this."),
}


def _mk_rules(prefix, include_franchise=False):
    rules = []
    for base, suffix in ((_ADJ_RULE, "ADJ"), (_APPORT_RULE, "APPORT"), (_PTET_RULE, "PTET"), (_NRW_RULE, "NRW")):
        r = dict(base)
        r["rule_id"] = f"{prefix}-{suffix}"
        rules.append(r)
    if include_franchise:
        rules.append({
            "rule_id": f"{prefix}-FRANCH", "title": "NC franchise tax — net worth (CD-401S Schedule C)", "rule_type": "calculation",
            "formula": ("franchise_tax = 200 if net_worth <= 1000000 else 200 + (net_worth - 1000000) * 0.0015 ; "
                        "if is_holding_company: franchise_tax = min(franchise_tax, 150000)"),
            "inputs": ["net_worth", "is_holding_company"], "outputs": ["franchise_tax"], "sort_order": 5,
            "description": ("W2 [CORRECTED D-16/NC-2]. §105-122 (as amended by S.L. 2021-180). CD-401S Sch A Line 2, "
                            "verbatim: 'If Line 1 <= $1,000,000, the minimum tax due of $200 is applicable. If Line 1 "
                            "> $1,000,000, multiply the amount over $1,000,000 by .0015 and add $200.' I.e. $200 for "
                            "the first $1M + $1.50/$1,000 of the excess; $200 minimum; holding-company cap $150,000. "
                            "NOT the CD-405 C-corp $500-first-$1M-cap mechanic. Net-worth BASE computes on Sch C "
                            "(L9); the TAX computes on Sch A. (D-403 partnerships pay no franchise.)"),
        })
    return rules


def _mk_links(prefix, include_franchise=False):
    links = [
        (f"{prefix}-ADJ", "NC_GS_105_CORP", "primary", "§105-130.5B 85% add-back + §179 $25k/$200k"),
        (f"{prefix}-APPORT", "NC_GS_105_CORP", "primary", "§105-130.4 single sales factor"),
        (f"{prefix}-PTET", "NC_SL_2021_180", "primary", "Taxed PTE 4.25% + owner deduction"),
        (f"{prefix}-PTET", "NC_2025_PTE_RETURNS", "secondary", "election on the return"),
        (f"{prefix}-NRW", "NC_2025_PTE_RETURNS", "primary", "nonresident withholding 4.25%"),
    ]
    if include_franchise:
        links.append((f"{prefix}-FRANCH", "NC_GS_105_CORP", "primary", "§105-122 net-worth franchise"))
    return links


# ── NC_D403 (partnership) ──
D403_FACTS = [dict(f) for f in _PT_FACTS]
D403_RULES = _mk_rules("R-NCD403")
D403_LINKS = _mk_links("R-NCD403")
D403_LINES = [
    {"line_number": "D403-PTET", "description": "D-403 Taxed PTE tax (× 4.25%) — Part 1 Line 11; Part 4 Sec. E Lines 24–27 [NC-6]", "line_type": "calculated", "source_rules": ["R-NCD403-PTET"], "sort_order": 1},
    {"line_number": "D403-NRW", "description": "D-403 nonresident partner withholding (× 4.25%) — Part 4 Sec. C Lines 17–20 [NC-6]", "line_type": "calculated", "source_rules": ["R-NCD403-NRW"], "sort_order": 2},
    {"line_number": "D403-APPT", "description": "D-403 apportionment ratio (single sales, 4 dec) — Part 2 Line 9 [NC-6]", "line_type": "calculated", "source_rules": ["R-NCD403-APPORT"], "sort_order": 3},
]
D403_DIAG = [
    {"diagnostic_id": "D_NCD403_PTET", "title": "NC Taxed PTE — 4.25%, owner DEDUCTS (not a credit)", "severity": "info",
     "condition": "is_taxed_pte",
     "message": "A Taxed Partnership pays NC tax at the individual rate (4.25% for 2025) on the NC-ATTRIBUTABLE distributive shares of partners NOT classified as corporations or partnerships (the resident non-NC-share component was REPEALED eff. TY2023+ — G.S. 105-154.1(b)(1)b). Corp/partnership partners remain under the NR payment regime unless NC-NPA. Each eligible partner then DEDUCTS their NC-sourced share on D-400 Schedule S Line 38a (PTE owners: NC-PE Part B Line 38a) — a DEDUCTION, not a credit (contrast Alabama); do NOT report the partner's share of entity-level tax on NC K-1 Line 9. Election is annual on the timely-filed D-403 and cannot be made or revoked after the original return is filed.",
     "notes": "W1."},
    {"diagnostic_id": "D_NCD403_BONUS", "title": "NC 85% bonus depreciation add-back", "severity": "info",
     "condition": "federal_bonus_depreciation > 0",
     "message": "NC did not adopt §168(k) for 2025. Add back 85% of federal bonus depreciation; recover in five equal installments (20%/yr) from 2026 (G.S. §105-130.5B). Flows to partners via NC-PE.",
     "notes": "W3."},
    {"diagnostic_id": "D_NCD403_179", "title": "NC §179 limit $25,000 / $200,000", "severity": "warning",
     "condition": "federal_section_179 > 25000",
     "message": "NC §179 limits are $25,000 / $200,000. Add back 85% of the federal §179 over the NC limit; recover 20%/yr. Flows to partners via NC-PE.",
     "notes": "W3."},
    {"diagnostic_id": "D_NCD403_NRW", "title": "NC nonresident partner withholding — 4.25%", "severity": "info",
     "condition": "nonresident_nc_source_share > 0 and not is_taxed_pte",
     "message": "The partnership pays NC tax on each nonresident partner's NC-source share at 4.25% (2025). Form NC-NPA relief is available ONLY for partners classified as corporation/partnership/trust/estate/tax-exempt — nonresident INDIVIDUALS cannot opt out [D-16/NC-5]. A Taxed-PTE election substitutes the entity tax for this withholding.",
     "notes": "W1."},
]
D403_SCEN = [
    {"scenario_name": "D403-A — Taxed PTE 4.25% (post-2022 base)", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"is_taxed_pte": True, "nc_attributable_share_eligible": 700000},
     "expected_outputs": {"taxed_pte_tax": 29750}, "notes": "[D-16/NC-1] 700,000 NC-attributable (eligible owners only; residents to the extent NC-attributable; corp/partnership owners excluded) x 4.25% = 29,750. Individual owners deduct at D-400 Sch S L38a."},
    {"scenario_name": "D403-B — nonresident withholding (no election)", "scenario_type": "normal", "sort_order": 2,
     "inputs": {"is_taxed_pte": False, "nonresident_nc_source_share": 200000},
     "expected_outputs": {"nonresident_withholding": 8500}, "notes": "200,000 NC-source x 4.25% = 8,500 (no NC-NPA)."},
    {"scenario_name": "D403-C — 85% bonus add-back", "scenario_type": "edge", "sort_order": 3,
     "inputs": {"federal_bonus_depreciation": 80000},
     "expected_outputs": {"nc_additions": 68000}, "notes": "85% of 80,000 = 68,000 add-back (flows via NC-PE)."},
    {"scenario_name": "D403-D — multistate single sales factor", "scenario_type": "edge", "sort_order": 4,
     "inputs": {"is_multistate": True, "sales_nc": 250000, "sales_everywhere": 1000000},
     "expected_outputs": {"nc_ratio": 0.25}, "notes": "Ratio 250,000/1,000,000 = 0.2500."},
]

# ── NC_CD401S (S-corp) ──
CD401S_FACTS = [dict(f) for f in _PT_FACTS] + [
    {"fact_key": "net_worth", "label": "Net worth — total assets (before accumulated depreciation) less liabilities (franchise base, Sch C)", "data_type": "decimal", "required": False, "sort_order": 12},
    {"fact_key": "is_holding_company", "label": "Qualified holding company? (franchise cap $150,000)", "data_type": "boolean", "required": False, "sort_order": 13},
]
CD401S_RULES = _mk_rules("R-NCCD401S", include_franchise=True)
CD401S_LINKS = _mk_links("R-NCCD401S", include_franchise=True)
CD401S_LINES = [
    {"line_number": "CD401-PTET", "description": "CD-401S Taxed PTE tax (× 4.25%) — Sch B Lines 17–19 [NC-6]", "line_type": "calculated", "source_rules": ["R-NCCD401S-PTET"], "sort_order": 1},
    {"line_number": "CD401-FRAN", "description": "CD-401S franchise tax — Sch A Lines 1–2 (net worth from Sch C Line 9) [NC-6]", "line_type": "calculated", "source_rules": ["R-NCCD401S-FRANCH"], "sort_order": 2},
    {"line_number": "CD401-NRW", "description": "CD-401S nonresident shareholder withholding/composite — Sch B Lines 16, 18–19 [NC-6]", "line_type": "calculated", "source_rules": ["R-NCCD401S-NRW"], "sort_order": 3},
]
CD401S_DIAG = [
    {"diagnostic_id": "D_NCCD401S_PTET", "title": "NC Taxed S Corporation — 4.25%, owner DEDUCTS", "severity": "info",
     "condition": "is_taxed_pte",
     "message": "A Taxed S Corporation pays NC tax at 4.25% (2025) on the NC-ATTRIBUTABLE shares of its shareholders (CD-401S Sch B Lines 17–19: apportioned + allocated NC income; the resident non-NC-share component was REPEALED eff. TY2023+ — G.S. 105-131.1A(b)(1)b). Each shareholder DEDUCTS their NC-sourced share at D-400 Schedule S Line 38a, not a credit. Annual election on the timely-filed CD-401S; cannot be made or revoked after the original return is filed.",
     "notes": "W1."},
    {"diagnostic_id": "D_NCCD401S_FRANCH", "title": "NC franchise tax applies to S-corps (CD-401S)", "severity": "warning",
     "condition": "net_worth > 0",
     "message": "NC imposes the franchise tax on S-corporations via CD-401S (net-worth base on Sch C; TAX on Sch A Line 2): $200 for the first $1,000,000 of the base + $1.50 per $1,000 (.0015) of the excess; minimum $200; holding-company cap $150,000. [CORRECTED D-16/NC-2 — not the CD-405 C-corp $500-cap mechanic.] This is in addition to the income pass-through — S-corps are NOT exempt from the NC franchise tax.",
     "notes": "W2."},
    {"diagnostic_id": "D_NCCD401S_BONUS", "title": "NC 85% bonus depreciation add-back", "severity": "info",
     "condition": "federal_bonus_depreciation > 0",
     "message": "NC did not adopt §168(k) for 2025 — add back 85% of federal bonus depreciation, recover 20%/yr from 2026 (G.S. §105-130.5B). Flows to shareholders via NC-PE.",
     "notes": "W3."},
    {"diagnostic_id": "D_NCCD401S_179", "title": "NC §179 limit $25,000 / $200,000", "severity": "warning",
     "condition": "federal_section_179 > 25000",
     "message": "NC §179 limits are $25,000/$200,000. Add back 85% of the federal §179 over the NC limit; recover 20%/yr. Flows to shareholders via NC-PE.",
     "notes": "W3."},
]
CD401S_SCEN = [
    {"scenario_name": "CD401S-A — Taxed PTE 4.25% (post-2022 base)", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"is_taxed_pte": True, "nc_attributable_share_eligible": 500000},
     "expected_outputs": {"taxed_pte_tax": 21250}, "notes": "[D-16/NC-1] 500,000 NC apportioned+allocated (CD-401S Sch B L17+L18) x 4.25% = 21,250."},
    {"scenario_name": "CD401S-B — franchise tax over $1M", "scenario_type": "edge", "sort_order": 2,
     "inputs": {"net_worth": 2000000},
     "expected_outputs": {"franchise_tax": 1700}, "notes": "[CORRECTED D-16/NC-2] $200 (first $1M) + 1,000,000 × .0015 = $1,700 — NOT the $2,000 the CD-405-clone mechanic gave."},
    {"scenario_name": "CD401S-C — franchise minimum ($200)", "scenario_type": "edge", "sort_order": 3,
     "inputs": {"net_worth": 100000},
     "expected_outputs": {"franchise_tax": 200}, "notes": "Base <= $1,000,000 -> flat $200 (CD-401S Sch A L2)."},
    {"scenario_name": "CD401S-D — nonresident withholding 4.25%", "scenario_type": "normal", "sort_order": 4,
     "inputs": {"is_taxed_pte": False, "nonresident_nc_source_share": 100000},
     "expected_outputs": {"nonresident_withholding": 4250}, "notes": "100,000 x 4.25% = 4,250."},
]

FORMS: list[dict] = [
    {"identity": {"form_number": "NC_D403", "entity_types": ["1065"],
                  "form_title": "North Carolina Form D-403 — Partnership Income Tax Return (TY2025)",
                  "notes": "WO-13 (DECISIONS D-15); CORRECTED per campaign D-16 (2026-08-22). NC partnership: federal 1065 start + 85% bonus/§179 $25k/$200k add-back (NC-PE) + single sales factor (4 dec); the NC Taxed PTE election (4.25% on the NC-ATTRIBUTABLE shares of non-corp/non-partnership owners — post-2022 base; owner-side DEDUCTION at D-400 Sch S L38a, NOT a credit); nonresident partner withholding 4.25% (NC-NPA relief limited to entity-type partners). No franchise (partnerships). Conformity Jan 1 2023."},
     "facts": D403_FACTS, "rules": D403_RULES, "rule_links": D403_LINKS, "lines": D403_LINES, "diagnostics": D403_DIAG, "scenarios": D403_SCEN},
    {"identity": {"form_number": "NC_CD401S", "entity_types": ["1120S"],
                  "form_title": "North Carolina Form CD-401S — S Corporation Tax Return (TY2025)",
                  "notes": "WO-13 (DECISIONS D-15); CORRECTED per campaign D-16 (2026-08-22). NC S-corp: federal 1120-S start + 85% bonus/§179 add-back + single sales factor; the NC Taxed PTE election (4.25% on Sch B L17+L18 NC apportioned+allocated — post-2022 base; owner DEDUCTION at D-400 Sch S L38a); the NC FRANCHISE TAX on the S-corp ($200 first $1M + .0015 × excess, $200 min, $150k holding cap — NOT the CD-405 mechanic; S-corps are NOT franchise-exempt); nonresident shareholder relief via Form NC-NA + composite. Conformity Jan 1 2023."},
     "facts": CD401S_FACTS, "rules": CD401S_RULES, "rule_links": CD401S_LINKS, "lines": CD401S_LINES, "diagnostics": CD401S_DIAG, "scenarios": CD401S_SCEN},
]

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-NCD403-PTET", "title": "NC Taxed PTE tax = 4.25% of the electing base", "assertion_type": "reconciliation",
     "entity_types": ["1065"], "status": "draft", "sort_order": 1,
     "description": "[D-16/NC-1] Taxed PTE tax = NC-attributable shares of eligible (non-corp/non-partnership) owners × 4.25%; individual owners deduct at D-400 Sch S L38a.",
     "definition": {"rule": "R-NCD403-PTET", "check": "taxed_pte_tax = nc_attributable_share_eligible * 0.0425"}},
    {"assertion_id": "FA-NCCD401S-FRAN", "title": "NC franchise applies to the S-corp (CD-401S)", "assertion_type": "reconciliation",
     "entity_types": ["1120S"], "status": "draft", "sort_order": 2,
     "description": "[D-16/NC-2] CD-401S franchise = $200 for the first $1M of net worth + .0015 × the excess; $200 minimum; $150k holding cap.",
     "definition": {"rule": "R-NCCD401S-FRANCH", "check": "franchise = 200 if nw <= 1000000 else 200 + (nw - 1000000) * 0.0015"}},
]


class Command(BaseCommand):
    help = "Load the NC pass-through specs (D-403 + CD-401S + Taxed PTE, TY2025). Refuses to seed until READY_TO_SEED=True (W1-W3)."

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard()
        self.stdout.write(self.style.MIGRATE_HEADING("\nLoad NC pass-through specs (D-403 + CD-401S + Taxed PTE)\n"))
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
        if not READY_TO_SEED or empty:
            still = "\n  ".join(f"- {n}" for n in empty) or "(all populated)"
            raise CommandError(
                "\nREFUSING TO SEED NC pass-through: not cleared.\n\n"
                "Gated until Ken reviews (W1 Taxed PTE 4.25% + owner deduction; W2 CD-401S franchise;\n"
                f"W3 depreciation) and flips the sentinel.\n\nREADY_TO_SEED = {READY_TO_SEED}\n\nEmpty:\n  {still}\n"
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
                AuthorityExcerpt.objects.update_or_create(authority_source=src, excerpt_label=e["excerpt_label"], defaults=e)
            for tc in tcs:
                t = AuthorityTopic.objects.filter(topic_code=tc).first()
                if t:
                    AuthoritySourceTopic.objects.get_or_create(authority_source=src, authority_topic=t)
        # ⚠ D-42: these two lists existed and were NEVER READ. One module DECLARES a
        #   source, every other REFERENCES it (D-29) — that only works if both halves run.
        _wire.resolve_references(EXISTING_SOURCES_TO_REFERENCE, sources, self.stdout.write)
        _wire.apply_new_excerpts(NEW_EXCERPTS_ON_EXISTING, sources, self.stdout.write)
        self.stdout.write(f"Sources ready: {len(sources)}")
        return sources

    def _upsert_form(self, identity: dict) -> TaxForm:
        form, created = TaxForm.objects.update_or_create(
            form_number=identity["form_number"], jurisdiction=FORM_JURISDICTION, tax_year=FORM_TAX_YEAR, version=FORM_VERSION,
            defaults={"form_title": identity["form_title"], "entity_types": identity["entity_types"], "status": FORM_STATUS, "notes": identity["notes"]},
        )
        self.stdout.write(f"{'Created' if created else 'Updated'} {identity['form_number']} {identity['entity_types']}")
        return form

    def _upsert_facts(self, form, facts):
        keys = {f["fact_key"] for f in facts}
        for f in facts:
            f = dict(f)
            FormFact.objects.update_or_create(tax_form=form, fact_key=f.pop("fact_key"), defaults=f)
        self._prune(FormFact.objects.filter(tax_form=form).exclude(fact_key__in=keys), "facts")
        self.stdout.write(f"  {len(facts)} facts")

    def _upsert_rules(self, form, rules_data) -> dict:
        created = {}
        for r in rules_data:
            r = dict(r)
            rule, _ = FormRule.objects.update_or_create(tax_form=form, rule_id=r.pop("rule_id"), defaults=r)
            created[rule.rule_id] = rule
        self.stdout.write(f"  {len(created)} rules")
        return created

    def _upsert_links(self, rules, sources, rule_links):
        ct = 0
        for rid, sc, lvl, note in rule_links:
            rule, src = rules.get(rid), sources.get(sc)
            if rule and src:
                RuleAuthorityLink.objects.get_or_create(form_rule=rule, authority_source=src, defaults={"support_level": lvl, "relevance_note": note})
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
            FormDiagnostic.objects.update_or_create(tax_form=form, diagnostic_id=d.pop("diagnostic_id"), defaults=d)
        self._prune(FormDiagnostic.objects.filter(tax_form=form).exclude(diagnostic_id__in=ids), "diagnostics")
        self.stdout.write(f"  {len(diags)} diagnostics")

    def _upsert_tests(self, form, scenarios):
        names = {t["scenario_name"] for t in scenarios}
        for t in scenarios:
            t = dict(t)
            TestScenario.objects.update_or_create(tax_form=form, scenario_name=t.pop("scenario_name"), defaults=t)
        self._prune(TestScenario.objects.filter(tax_form=form).exclude(scenario_name__in=names), "test scenarios")
        self.stdout.write(f"  {len(scenarios)} test scenarios")

    def _prune(self, qs, label):
        """Delete rows this loader no longer declares.

        [ADDED 2026-08-22, campaign D-16] Every upsert here keys on a NAME
        (fact_key / line_number / diagnostic_id / scenario_name) with
        update_or_create, so RENAMING a row created a second row and left the
        original live. Found while applying the NC-1/NC-2 corrections: the
        repealed pre-2023 `resident_owner_share` fact and the stale
        `D403-A`/`CD401S-A` scenarios (carrying the superseded base) survived
        the reseed alongside their replacements — a spec export shipping BOTH
        the corrected and the repealed rule. Mirrors the delvio-tax
        seed_ga700 stale-line prune.
        """
        n = qs.count()
        if n:
            qs.delete()
            self.stdout.write(self.style.WARNING(f"  pruned {n} stale {label}"))

    def _upsert_form_links(self, sources):
        for sc, fc, lt in AUTHORITY_FORM_LINKS:
            src = sources.get(sc) or AuthoritySource.objects.filter(source_code=sc).first()
            if src:
                AuthorityFormLink.objects.get_or_create(authority_source=src, form_code=fc, link_type=lt, defaults={"note": f"{sc} -> {fc}"})

    def _load_fa(self):
        for a in FLOW_ASSERTIONS:
            a = dict(a)
            FlowAssertion.objects.update_or_create(assertion_id=a.pop("assertion_id"), defaults=a)
        self.stdout.write(f"  {len(FLOW_ASSERTIONS)} flow assertions")

    def _report(self):
        self.stdout.write("\n" + "=" * 60)
        for spec in FORMS:
            fn = spec["identity"]["form_number"]
            self.stdout.write(f"  {fn}: facts {len(spec['facts'])} / rules {len(spec['rules'])} / lines {len(spec['lines'])} / diag {len(spec['diagnostics'])} / tests {len(spec['scenarios'])}")
        self.stdout.write(f"  flow assertions: {len(FLOW_ASSERTIONS)}")
        self.stdout.write("=" * 60)
