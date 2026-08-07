"""Load the K1_BASIS_704D spec — Partner's §704(d) Basis Limitation (preparer-asserted).

Mixed-entity pilot #7 (CC_CODE_CHANGES_PULLIAM_MIXED_PILOT, item 7 — filing
blocker). Ken ratified spec-first on 2026-08-07 (s226 AskUserQuestion): author
this spec, Ken walks it (Gate 1), THEN the app build dispatches.

THE GAP: on a 1065 partnership K-1, `basis_at_risk_limited` is a flag that
changes no number — the full K-1 loss routes to Schedule E page 2 and the only
guard is a warning (rules_schedule_e_p2.d_k1_basis: partner §704(d) basis is
"not built here"). Form 7203 covers the S-corp side (§1366(d)) only. In the
pilot, Schedule E line 41 reads $90,041 instead of $106,270 and federal AGI
$195,006 instead of $211,235; the error flows to Georgia.

THE SHAPE (Ken-ratified recommendation): the preparer ASSERTS the allowed and
suspended amounts; the app routes and carries them but NEVER derives the limit
itself. We cannot see a partner's outside-basis history, so this is
transcribe-and-route: the app checks the arithmetic (allowed + suspended = the
loss; allowed ≤ available basis) and DIAGNOSES an inconsistency rather than
silently recomputing. That stays inside the authoritative-source rule: we
record a preparer's §704(d) determination, we don't invent one.

LAW VERIFIED 2026-08-07 against primary sources (fetched, not memory):
  - §704(d)(1) verbatim: loss allowed "only to the extent of the adjusted basis
    of such partner's interest in the partnership at the end of the partnership
    year in which such loss occurred."
  - §704(d)(2) Carryover — the statute's famously odd "repaid to the
    partnership" phrasing; Reg §1.704-1(d) construes it as carryforward to
    succeeding years to the extent basis is restored above zero.
  - §704(d)(3)(A)/(B): the §702(a)(4) charitable and (a)(6) foreign-tax shares
    count toward the limited loss, EXCEPT the appreciation portion of a
    contribution of appreciated property.
  - Partner's Instructions for Sch K-1 (1065) (2025), verbatim: the four
    limitations apply IN ORDER — basis, at-risk, passive activity, excess
    business loss; disallowed amounts are "suspended and carried forward for
    use in the next tax year in which the partner has adjusted basis"; and
    "It's the partner's responsibility to track" basis — the worksheet is NOT
    attached to the return (⚠ scope finding: unlike Form 7203, #7 needs NO MeF
    document and NO render leg — "rendering and MeF" is satisfied by storing
    and surviving).
  - Reg §1.199A-3(b)(1)(iv)(A): §704(d)-suspended losses arising after 2017
    are taken into account for QBI in the year ALLOWED, FIFO — so the source
    K-1's §199A amount (already reflecting the limitation) must not be
    double-limited by this worksheet.

v1 SCOPE:
  - 1065 partnership K-1s only (S-corp = Form 7203, already built; 1041 out).
  - MATERIALLY PARTICIPATING (nonpassive) losses only — the pilot's case.
    A PASSIVE basis-limited loss keeps the existing SCHEDULE_K1 Decision-4 RED
    (K-1 passive losses are themselves RED-deferred); v1 does not chain
    basis→8582.
  - The preparer's asserted "allowed" figure is AFTER basis and at-risk
    combined (the app's checkbox couples them, and the source return's
    worksheet already ran both). Form 6198 R008 owns the ordering statement.
  - Prior-year suspended amounts join the current-loss input (the instructions'
    worksheet Part II combines current + carryforward columns).

SAFETY GUARD: READY_TO_SEED stays False until Ken's Gate-1 review walk (the
preparer-asserted shape; the arithmetic checks; the no-attachment scope
finding; the QBI no-double-limit rule; the v1 nonpassive-only scope).
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


READY_TO_SEED = True  # FLIPPED 2026-08-07 — Ken approved the Gate-1 walk ("Approve — flip, seed, export").


FORM_JURISDICTION = "FED"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_ENTITY_TYPES = ["1040"]
FORM_STATUS = "draft"


# ═══════════════════════════════════════════════════════════════════════════
# THE MATH (the integrity gate re-types this independently; they share no math).
#
# The app DERIVES NOTHING under §704(d) — every limit figure is preparer-
# asserted. The only computation is the consistency check and the routing cap:
#   available = max(0, beginning_basis + current_additions − distributions)
#     (distributions are taken into account BEFORE the loss limitation —
#      Reg §1.704-1(d)(2) ordering; a distribution in excess of basis is §731
#      gain, out of scope, diagnosed)
#   consistent ⇔ allowed + suspended == current_loss  AND  allowed ≤ available
#   sche_net_limited = max(raw_net, −allowed)   # the k1_sche_net() convention:
#     raw_net = box1 + box2 + box3 (negative); cap once, at the single source
#     of truth, so 8582 gathering / p2 totals / diagnostics all see one number.
# All amounts are positive magnitudes except raw_net / sche_net_limited.
# ═══════════════════════════════════════════════════════════════════════════

from decimal import Decimal  # noqa: E402


def _D(x):
    return Decimal(str(x if x is not None else 0))


def compute_k1_basis_704d(beginning_basis=0, current_additions=0, distributions=0,
                          current_loss=0, allowed_loss=0, suspended_carryforward=0,
                          raw_net=0) -> dict:
    """The preparer-asserted §704(d) worksheet: consistency check + routing cap.
    Never derives the limit — checks the assertion's arithmetic and applies it."""
    available = max(_D(0), _D(beginning_basis) + _D(current_additions) - _D(distributions))
    consistent = (
        _D(allowed_loss) + _D(suspended_carryforward) == _D(current_loss)
        and _D(allowed_loss) <= available
    )
    limited = max(_D(raw_net), -_D(allowed_loss))
    return {"available_basis": available, "consistent": consistent,
            "sche_net_limited": limited}


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY
# ═══════════════════════════════════════════════════════════════════════════

AUTHORITY_TOPICS: list[tuple[str, str]] = [
    ("partner_basis_limitation",
     "Partner's §704(d) outside-basis loss limitation — preparer-asserted allowed/suspended; "
     "ordering basis → §465 → §469 → §461(l); carryforward not attached to the return"),
]

EXISTING_SOURCES_TO_REFERENCE: list[str] = [
    "IRS_2025_1065_K1_INSTR",  # the Partner's Instructions (load_1040_schedule_k1)
    "IRC_465",                 # at-risk (load_1040_schedule_e)
    "IRC_469",                 # passive (load_1040_schedule_e)
    "IRC_199A",                # QBI (load_1040_schedule_k1)
]

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "IRC_704D",
        "source_type": "code_section",  # the VALID SourceType (the older loaders' "statute" is frozen ratchet debt — never copy it)
        "source_rank": "primary_official",
        "jurisdiction_code": "FED",
        "entity_type_code": "1040",
        "tax_year_start": 2025,
        "tax_year_end": 2025,
        "title": "IRC §704(d) — Limitation on allowance of losses (partner's outside basis)",
        "citation": "26 U.S.C. §704(d)(1)-(3)",
        "issuer": "U.S. Congress",
        "official_url": "https://uscode.house.gov/view.xhtml?req=(title:26%20section:704%20edition:prelim)",
        "current_status": "active",
        "is_substantive_authority": True,
        "is_filing_authority": False,
        "trust_score": 10.00,
        "requires_human_review": True,
        "notes": (
            "The substantive limit. (d)(1): distributive share of loss allowed only to the extent of "
            "the adjusted basis of the partner's interest AT THE END of the partnership year. (d)(2) "
            "Carryover: the statute's odd 'repaid to the partnership' phrasing — Reg §1.704-1(d) "
            "construes it as carryforward to succeeding years to the extent basis is restored above "
            "zero. (d)(3): the §702(a)(4) charitable / (a)(6) foreign-tax shares count toward the "
            "limited loss EXCEPT the appreciation portion of contributed appreciated property. "
            "REQUIRES HUMAN REVIEW: (d)(1) verbatim was fetch-verified 2026-08-07; the (d)(2) "
            "sentence was corroborated across two fetches but the full verbatim should be confirmed "
            "at the Gate-1 walk. NOTE the outside-basis ≠ item-L-capital distinction: outside basis "
            "includes the §752 share of liabilities; the K-1 item L capital account does NOT."
        ),
        "topics": ["partner_basis_limitation"],
        "excerpts": [
            {
                "excerpt_label": "§704(d)(1) — loss allowed only to the extent of adjusted basis at year end",
                "location_reference": "26 U.S.C. §704(d)(1)",
                "excerpt_text": (
                    "A partner's distributive share of partnership loss (including capital loss) shall be "
                    "allowed only to the extent of the adjusted basis of such partner's interest in the "
                    "partnership at the end of the partnership year in which such loss occurred."
                ),
                "summary_text": "The limit: current-year loss deductible only up to end-of-year outside basis.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "§704(d)(3)(A)/(B) — charitable + foreign-tax shares; appreciated-property exception",
                "location_reference": "26 U.S.C. §704(d)(3)",
                "excerpt_text": (
                    "(A) In general. In determining the amount of any loss under paragraph (1), there shall "
                    "be taken into account the partner's distributive share of amounts described in "
                    "paragraphs (4) and (6) of section 702(a). (B) Exception. In the case of a charitable "
                    "contribution of property whose fair market value exceeds its adjusted basis, "
                    "subparagraph (A) shall not apply to the extent of the partner's distributive share of "
                    "such excess."
                ),
                "summary_text": (
                    "Charitable contributions and foreign taxes count toward the §704(d)-limited loss, "
                    "EXCEPT the appreciation portion of contributed appreciated property — a nuance the "
                    "preparer's source worksheet owns (the app never allocates it)."
                ),
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "TREAS_REG_1704_1D",
        "source_type": "regulation",
        "source_rank": "primary_official",
        "jurisdiction_code": "FED",
        "entity_type_code": "1040",
        "tax_year_start": 2025,
        "tax_year_end": 2025,
        "title": "Treas. Reg. §1.704-1(d) — Limitation on allowance of losses (carryforward mechanics)",
        "citation": "26 C.F.R. §1.704-1(d)(1)-(2)",
        "issuer": "U.S. Treasury",
        "official_url": "https://www.ecfr.gov/current/title-26/section-1.704-1",
        "current_status": "active",
        "is_substantive_authority": True,
        "is_filing_authority": False,
        "trust_score": 9.90,
        "requires_human_review": True,
        "notes": (
            "The operative carryforward rule: a loss disallowed under §704(d) is allowed at the end of "
            "succeeding partnership years to the extent basis exceeds zero; §1.704-1(d)(2) orders "
            "distributions ahead of the loss limitation (basis is reduced for distributions BEFORE "
            "testing the loss). ⚠ REQUIRES HUMAN REVIEW — NO VERBATIM EXCERPT CAPTURED: eCFR blocked "
            "the 2026-08-07 fetch; this summary is corroborated by the 2025 Partner's Instructions "
            "carryforward language (quoted verbatim on IRS_2025_1065_K1_INSTR). Confirm at the Gate-1 "
            "walk. The app derives nothing from this reg — it is cited for the ordering and the "
            "carryforward construction only."
        ),
        "topics": ["partner_basis_limitation"],
        "excerpts": [],
    },
    {
        "source_code": "TREAS_REG_199A3_PDL",
        "source_type": "regulation",
        "source_rank": "primary_official",
        "jurisdiction_code": "FED",
        "entity_type_code": "1040",
        "tax_year_start": 2025,
        "tax_year_end": 2025,
        "title": "Treas. Reg. §1.199A-3(b)(1)(iv) — Previously disallowed losses (QBI timing)",
        "citation": "26 C.F.R. §1.199A-3(b)(1)(iv)(A)",
        "issuer": "U.S. Treasury",
        "official_url": "https://www.law.cornell.edu/cfr/text/26/1.199A-3",
        "current_status": "active",
        "is_substantive_authority": True,
        "is_filing_authority": False,
        "trust_score": 9.90,
        "requires_human_review": True,
        "notes": (
            "Losses disallowed under §§461(l)/465/469/704(d)/1366(d) arising after 2017 are taken into "
            "account for QBI in the year ALLOWED, FIFO, as a separate trade or business. Consequence "
            "for this spec: the source K-1's §199A amount already reflects the §704(d) limitation "
            "(the pilot's −10,621), so the app must NOT apply this worksheet's cap to QBI a second "
            "time. REQUIRES HUMAN REVIEW: partial verbatim fetch-verified 2026-08-07 via LII; confirm "
            "the subparagraph cite at the Gate-1 walk."
        ),
        "topics": ["partner_basis_limitation"],
        "excerpts": [
            {
                "excerpt_label": "(b)(1)(iv)(A) — pre-2018 suspended losses never enter QBI; post-2017 enter when allowed",
                "location_reference": "26 C.F.R. §1.199A-3(b)(1)(iv)(A)",
                "excerpt_text": (
                    "Losses or deductions that were disallowed, suspended, limited, or carried over from "
                    "taxable years ending before January 1, 2018 … are not taken into account in a "
                    "subsequent taxable year for purposes of computing QBI. [Post-2017 losses disallowed "
                    "under sections 461(l), 465, 469, 704(d), and 1366(d) are taken into account for QBI "
                    "in the year allowed, FIFO, as losses from a separate trade or business.]"
                ),
                "summary_text": (
                    "QBI follows the §704(d) allowance year — the source K-1's §199A figure is already "
                    "limited; never double-limit it here. Bracketed portion is a faithful summary "
                    "pending full verbatim confirmation."
                ),
                "is_key_excerpt": True,
            },
        ],
    },
]

# Today's verbatim fetches land as NEW excerpts on the EXISTING Partner's
# Instructions source (i1065sk1 2025, seeded by load_1040_schedule_k1).
NEW_EXCERPTS_ON_EXISTING: list[tuple[str, dict]] = [
    ("IRS_2025_1065_K1_INSTR", {
        "excerpt_label": "The four loss limitations apply IN ORDER — basis, at-risk, passive, EBL",
        "location_reference": "i1065sk1 (2025), Limitations on Losses, Deductions, and Credits",
        "excerpt_text": (
            "There are potential limitations on partnership losses that you can deduct on your return. "
            "These limitations and the order in which you must apply them are as follows: the basis "
            "limitations, the at-risk limitations, the passive activity limitations, and the excess "
            "business loss limitations."
        ),
        "summary_text": (
            "The stated ORDER: §704(d) basis → §465 at-risk (Form 6198) → §469 passive (Form 8582) → "
            "§461(l) EBL (Form 461). Agrees with FORM_6198 R008."
        ),
        "is_key_excerpt": True,
    }),
    ("IRS_2025_1065_K1_INSTR", {
        "excerpt_label": "Basis-disallowed amounts are suspended and carried forward",
        "location_reference": "i1065sk1 (2025), Basis Limitations",
        "excerpt_text": (
            "A partner's loss and deduction items in excess of basis are suspended and carried forward "
            "for use in the next tax year in which the partner has adjusted basis in their partnership "
            "interest available."
        ),
        "summary_text": (
            "The carryforward: suspended until basis is restored. Indefinite; tracked on the Worksheet "
            "for Adjusting the Basis of a Partner's Interest in the Partnership (Part II columns: "
            "current-year, prior carryforward, total, allowable, suspended)."
        ),
        "is_key_excerpt": True,
    }),
    ("IRS_2025_1065_K1_INSTR", {
        "excerpt_label": "The partner tracks basis — the worksheet is NOT attached to the return",
        "location_reference": "i1065sk1 (2025), Basis Limitations",
        "excerpt_text": (
            "It's the partner's responsibility to track and maintain the information necessary to "
            "figure their adjusted basis in the partnership."
        ),
        "summary_text": (
            "⚠ THE SCOPE FINDING: unlike Form 7203 (S-corp, attached), a partner's basis computation "
            "is the taxpayer's own record — no attachment requirement, so pilot #7 needs NO MeF "
            "document and NO render leg. 'Rendering and MeF' = storing and surviving."
        ),
        "is_key_excerpt": True,
    }),
]

AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    ("IRC_704D", "K1_BASIS_704D", "governs"),
    ("TREAS_REG_1704_1D", "K1_BASIS_704D", "governs"),
    ("TREAS_REG_199A3_PDL", "K1_BASIS_704D", "governs"),
    ("IRS_2025_1065_K1_INSTR", "K1_BASIS_704D", "governs"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM: K1_BASIS_704D
# ═══════════════════════════════════════════════════════════════════════════

N_IDENTITY = {
    "form_number": "K1_BASIS_704D",
    "form_title": "Partner's §704(d) Basis Limitation — preparer-asserted worksheet (TY2025)",
    "notes": (
        "Mixed-entity pilot #7 (filing blocker). NOT an IRS form — the partner-side analogue of "
        "Form 7203 with NO attachment requirement (the partner's own record; no MeF document, no "
        "render leg). The preparer ASSERTS beginning basis, additions, distributions, the current "
        "loss, the allowed loss and the suspended carryforward from the source return's worksheet; "
        "the app routes ONLY the allowed amount into the k1_sche_net() cap (the Form-7203 "
        "precedent: cap once, at the single source of truth), preserves the full K-1 box amounts, "
        "stores the suspended carryforward across reload/roll-forward/import-export, and DIAGNOSES "
        "arithmetic inconsistency without ever deriving the §704(d) limit itself. v1 scope: 1065 "
        "partnership K-1s, materially participating (nonpassive) losses only; the asserted allowed "
        "figure is after basis AND at-risk combined (the checkbox couples them; §469 still applies "
        "downstream). Distinct from item L capital (≠ outside basis — §752 liabilities) and from "
        "the QBI carryforward rules (Reg §1.199A-3(b)(1)(iv): never double-limit)."
    ),
}

N_FACTS: list[dict] = [
    # ── Preparer-asserted inputs (all positive magnitudes) ──
    {"fact_key": "fk1b_beginning_basis", "label": "Outside basis at the beginning of the year (incl. §752 liability share)",
     "data_type": "decimal", "default_value": "0", "sort_order": 1,
     "notes": ("Preparer-asserted from the source return's basis worksheet. Outside basis, NOT the K-1 "
               "item L capital account (item L excludes the §752 liability share).")},
    {"fact_key": "fk1b_current_additions", "label": "Current-year additions (contributions + income/gain items + §752 increases)",
     "data_type": "decimal", "default_value": "0", "sort_order": 2,
     "notes": "Preparer-asserted aggregate. The app never decomposes it."},
    {"fact_key": "fk1b_distributions", "label": "Current-year distributions (+ §752 decreases)",
     "data_type": "decimal", "default_value": "0", "sort_order": 3,
     "notes": ("Preparer-asserted. Taken into account BEFORE the loss limitation (Reg §1.704-1(d)(2)); "
               "a distribution in excess of basis is §731 gain — out of scope, diagnosed (D_K1B_EXCESS_DISTRIB).")},
    {"fact_key": "fk1b_current_loss", "label": "Total current-year loss subject to the limitation (positive magnitude)",
     "data_type": "decimal", "default_value": "0", "sort_order": 4,
     "notes": ("= −(K-1 boxes 1+2+3 net) in v1. Prior-year §704(d)-suspended amounts JOIN this input "
               "(the instructions' worksheet Part II combines current + prior-carryforward columns).")},
    {"fact_key": "fk1b_allowed_loss", "label": "Current-year ALLOWED loss (preparer-asserted, after basis AND at-risk)",
     "data_type": "decimal", "default_value": "0", "sort_order": 5,
     "notes": ("The pilot's $10,621. The preparer's determination from the source worksheet — the app "
               "NEVER derives it. Covers basis + at-risk combined (the basis_at_risk_limited checkbox "
               "couples them); §469 passive still applies downstream.")},
    {"fact_key": "fk1b_suspended_carryforward", "label": "Suspended carryforward (preparer-asserted)",
     "data_type": "decimal", "default_value": "0", "sort_order": 6,
     "notes": ("The pilot's $16,229. Stored on the return; survives reload, roll-forward, import/export. "
               "NOT attached to the return (no MeF, no render).")},
    # ── Outputs ──
    {"fact_key": "fk1b_available_basis", "label": "Available basis check figure = max(0, beginning + additions − distributions)",
     "data_type": "decimal", "sort_order": 30,
     "notes": "OUTPUT (derived check figure only — used by D_K1B_ARITH, never to recompute the allowed loss)."},
    {"fact_key": "fk1b_sche_net_limited", "label": "The limited Schedule E net = max(raw K-1 net, −allowed)",
     "data_type": "decimal", "sort_order": 31,
     "notes": ("OUTPUT. Applied ONCE in k1_sche_net() (the Form-7203 precedent) so 8582 gathering, the "
               "page-2 totals and the diagnostics all see the same limited number.")},
]

N_RULES: list[dict] = [
    {"rule_id": "R-K1B-SCOPE", "title": "Scope — 1065 partnership K-1, nonpassive loss; S-corp = Form 7203", "rule_type": "routing",
     "precedence": 1, "sort_order": 1,
     "formula": ("Applies when: source_type == 1065 AND the K-1's Schedule-E net (boxes 1+2+3) < 0 AND the "
                 "partner materially participates (nonpassive). S-corp K-1 → Form 7203 (§1366(d), built). "
                 "1041 → out of scope. PASSIVE basis-limited loss → keep the SCHEDULE_K1 Decision-4 RED "
                 "(v1 does not chain basis→8582)."),
     "inputs": [], "outputs": [],
     "description": ("§704(d) is the partner-side limit; §1366(d)/Form 7203 is the shareholder-side one "
                     "already implemented. v1 mirrors the pilot: a materially participating partner.")},
    {"rule_id": "R-K1B-ASSERT", "title": "Preparer-asserted allowed/suspended; the app routes, never derives", "rule_type": "calculation",
     "precedence": 2, "sort_order": 2,
     "formula": ("sche_net_limited = max(raw_net, −allowed_loss), applied ONCE in k1_sche_net(). The full "
                 "K-1 box amounts are PRESERVED as entered; only the routed Schedule-E net is capped. "
                 "The app records the preparer's §704(d)/§465 determination — it never computes a limit."),
     "inputs": ["fk1b_allowed_loss"], "outputs": ["fk1b_sche_net_limited"],
     "description": ("§704(d)(1): loss allowed only to the extent of end-of-year outside basis. The app "
                     "cannot see a partner's basis history, so the determination is the preparer's; the "
                     "cap lands beside the existing Form-7203 arm in compute_schedule_k1.k1_sche_net().")},
    {"rule_id": "R-K1B-ARITH", "title": "Arithmetic consistency — diagnose, never recompute", "rule_type": "validation",
     "precedence": 3, "sort_order": 3,
     "formula": ("available = max(0, beginning_basis + additions − distributions)  [distributions before "
                 "the loss test, Reg §1.704-1(d)(2)]. CONSISTENT ⇔ allowed + suspended == current_loss "
                 "AND allowed ≤ available. Inconsistent → D_K1B_ARITH (error); the asserted amounts are "
                 "NEVER silently corrected."),
     "inputs": ["fk1b_beginning_basis", "fk1b_current_additions", "fk1b_distributions",
                "fk1b_current_loss", "fk1b_allowed_loss", "fk1b_suspended_carryforward"],
     "outputs": ["fk1b_available_basis"],
     "description": ("The app's whole derivation surface: two identities that must hold for ANY valid "
                     "§704(d) worksheet. An arithmetically impossible assertion is an ERROR, never "
                     "acknowledgable (house rule, s215).")},
    {"rule_id": "R-K1B-ORDER", "title": "Ordering — basis → §465 → §469 → §461(l)", "rule_type": "routing",
     "precedence": 4, "sort_order": 4,
     "formula": ("The four limitations apply in the instructions' stated order: §704(d) basis, §465 "
                 "at-risk (Form 6198), §469 passive (Form 8582), §461(l) EBL (Form 461). v1: the "
                 "asserted allowed figure is after basis AND at-risk combined; the limited net then "
                 "flows into the existing nonpassive path (no 8582 in scope for a materially "
                 "participating partner)."),
     "inputs": ["fk1b_allowed_loss"], "outputs": [],
     "description": "Agrees with FORM_6198 R008 (basis, then at-risk, then passive). One ordering statement, two specs, no contradiction."},
    {"rule_id": "R-K1B-QBI", "title": "QBI is NOT double-limited — the source §199A amount stands", "rule_type": "routing",
     "precedence": 5, "sort_order": 5,
     "formula": ("Form 8995 line 2 consumes the K-1's §199A QBI amount AS ENTERED (the pilot's −10,621, "
                 "already reflecting the limitation at the source). This worksheet's cap NEVER applies "
                 "to the QBI figure. Suspended-loss QBI timing (year allowed, FIFO) is the preparer's "
                 "source-worksheet responsibility, like the limitation itself."),
     "inputs": [], "outputs": [],
     "description": ("Reg §1.199A-3(b)(1)(iv)(A): post-2017 §704(d)-suspended losses enter QBI in the "
                     "year allowed, FIFO. Keep this worksheet separate from the QBI carryforward rules "
                     "(the item's explicit instruction).")},
    {"rule_id": "R-K1B-CARRY", "title": "The suspended amount is STORED, never attached", "rule_type": "validation",
     "precedence": 6, "sort_order": 6,
     "formula": ("suspended_carryforward persists on the return and survives reload, roll-forward, "
                 "import/export and a compute pass. NO MeF document and NO render leg exist for it — "
                 "the Partner's Instructions impose no attachment requirement ('the partner's "
                 "responsibility to track'). Roll-forward seeds next year's worksheet."),
     "inputs": ["fk1b_suspended_carryforward"], "outputs": [],
     "description": ("The scope finding that removes two legs the Form-7203 precedent would suggest: "
                     "'rendering and MeF' is satisfied by storing and surviving.")},
]

N_LINES: list[dict] = [
    # NOT an IRS form — these are the worksheet's own rows (modeled on the
    # instructions' Worksheet for Adjusting the Basis of a Partner's Interest).
    {"line_number": "W1", "description": "Beginning-of-year outside basis (incl. §752 share)", "line_type": "input"},
    {"line_number": "W2", "description": "Current-year additions (contributions, income items, §752 increases)", "line_type": "input"},
    {"line_number": "W3", "description": "Distributions (+ §752 decreases) — before the loss test", "line_type": "input"},
    {"line_number": "W4", "description": "Available basis = max(0, W1 + W2 − W3) [check figure]", "line_type": "calculated"},
    {"line_number": "W5", "description": "Current-year loss subject to limitation (+ prior suspended)", "line_type": "input"},
    {"line_number": "W6", "description": "Allowed loss (preparer-asserted; ≤ W4; after basis + at-risk)", "line_type": "input"},
    {"line_number": "W7", "description": "Suspended carryforward (preparer-asserted; W5 − W6)", "line_type": "input"},
    {"line_number": "W8", "description": "Limited Schedule E net = max(raw K-1 net, −W6) → page-2 columns", "line_type": "total"},
]

N_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_K1B_ARITH", "title": "Basis worksheet arithmetic is impossible", "severity": "error",
     "condition": "allowed + suspended != current_loss OR allowed > available_basis",
     "message": ("This K-1's basis worksheet does not add up: the allowed loss plus the suspended "
                 "carryforward must equal the total loss, and the allowed loss cannot exceed the "
                 "available basis (beginning basis + additions − distributions). Correct the worksheet "
                 "figures against the source return — the software records your determination and will "
                 "not adjust it."),
     "notes": "R-K1B-ARITH. ERROR, never acknowledgable — an arithmetically impossible value (house rule, s215)."},
    {"diagnostic_id": "D_K1B_EXCESS_DISTRIB", "title": "Distributions exceed basis — possible §731 gain", "severity": "warning",
     "condition": "distributions > beginning_basis + current_additions",
     "message": ("Distributions on this K-1's basis worksheet exceed the basis available (beginning "
                 "basis + current additions). A distribution in excess of basis is generally capital "
                 "gain under §731(a)(1) — not computed by this software. Verify the source return's "
                 "treatment; available basis for the loss test is floored at zero."),
     "notes": "Reg §1.704-1(d)(2) orders distributions ahead of the loss test; §731 gain is out of scope."},
    {"diagnostic_id": "D_K1B_PASSIVE", "title": "Passive basis-limited K-1 — v1 does not chain basis into Form 8582", "severity": "warning",
     "condition": "worksheet present AND NOT materially participating",
     "message": ("This partnership K-1 is basis-limited AND passive. The basis limitation applies "
                 "first, and only the basis-allowed loss enters the Form 8582 passive computation — "
                 "this version does not chain them. K-1 passive losses remain a manual Form 8582 "
                 "entry; verify the ordering by hand."),
     "notes": "R-K1B-SCOPE. Interacts with SCHEDULE_K1 Decision 4 (passive K-1 losses RED-deferred)."},
    {"diagnostic_id": "D_K1B_UNASSERTED", "title": "Marked basis/at-risk limited but no worksheet saved", "severity": "warning",
     "condition": "basis_at_risk_limited AND no saved K1_BASIS_704D worksheet",
     "message": ("This K-1 is marked basis/at-risk limited, but no basis worksheet has been entered — "
                 "the full loss is still flowing to Schedule E. Enter the worksheet (beginning basis, "
                 "additions, distributions, loss, allowed, suspended) from the source return to limit "
                 "the deduction."),
     "notes": ("The existing D_K1_BASIS warning becomes this — a SAVED worksheet clears it (the "
               "Form-7203 confirm precedent: existence is the confirm signal).")},
    {"diagnostic_id": "D_K1B_FULLY_ALLOWED", "title": "Worksheet present but nothing is limited", "severity": "info",
     "condition": "worksheet present AND allowed == current_loss AND suspended == 0",
     "message": ("This K-1's basis worksheet allows the entire loss (nothing suspended). The worksheet "
                 "is consistent; no limitation applies this year."),
     "notes": "Informational — a complete worksheet on an unlimited activity is fine, just visible."},
]

N_SCENARIOS: list[dict] = [
    {"scenario_name": "K1B-T1 — the pilot: 26,850 loss, 10,621 allowed, 16,229 suspended", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"tax_year": 2025, "beginning_basis": 9000, "current_additions": 2000,
                "distributions": 379, "current_loss": 26850, "allowed_loss": 10621,
                "suspended_carryforward": 16229, "raw_net": -26850},
     "expected_outputs": {"fk1b_available_basis": 10621, "fk1b_sche_net_limited": -10621,
                          "consistent": True},
     "notes": ("The pilot's figures (dollar amounts only — basis detail synthetic: 9,000 + 2,000 − 379 "
               "= 10,621 available, allowed exactly exhausts basis). Downstream return-level pins for "
               "the build leg: Schedule E line 41 106,270; Schedule 1 line 5 consumes it; federal AGI "
               "211,235; GA starts from the corrected AGI.")},
    {"scenario_name": "K1B-T2 — zero basis: everything suspended", "scenario_type": "edge", "sort_order": 2,
     "inputs": {"tax_year": 2025, "beginning_basis": 0, "current_additions": 0, "distributions": 0,
                "current_loss": 5000, "allowed_loss": 0, "suspended_carryforward": 5000, "raw_net": -5000},
     "expected_outputs": {"fk1b_available_basis": 0, "fk1b_sche_net_limited": 0, "consistent": True},
     "notes": "No basis → no deduction; the K-1 box amount survives untouched; 5,000 carries."},
    {"scenario_name": "K1B-T3 — basis covers the loss: fully allowed", "scenario_type": "normal", "sort_order": 3,
     "inputs": {"tax_year": 2025, "beginning_basis": 50000, "current_additions": 0, "distributions": 0,
                "current_loss": 8000, "allowed_loss": 8000, "suspended_carryforward": 0, "raw_net": -8000},
     "expected_outputs": {"fk1b_available_basis": 50000, "fk1b_sche_net_limited": -8000,
                          "consistent": True, "D_K1B_FULLY_ALLOWED": True},
     "notes": "Nothing limited; D_K1B_FULLY_ALLOWED (info) confirms the worksheet is live but idle."},
    {"scenario_name": "K1B-T4 — allowed + suspended ≠ loss: the assertion is impossible", "scenario_type": "failure", "sort_order": 4,
     "inputs": {"tax_year": 2025, "beginning_basis": 10000, "current_additions": 0, "distributions": 0,
                "current_loss": 5000, "allowed_loss": 4000, "suspended_carryforward": 500, "raw_net": -5000},
     "expected_outputs": {"consistent": False, "D_K1B_ARITH": True},
     "notes": "4,000 + 500 ≠ 5,000 → ERROR. Never silently corrected, never acknowledgable."},
    {"scenario_name": "K1B-T5 — allowed exceeds available basis: impossible", "scenario_type": "failure", "sort_order": 5,
     "inputs": {"tax_year": 2025, "beginning_basis": 3000, "current_additions": 0, "distributions": 0,
                "current_loss": 5000, "allowed_loss": 4000, "suspended_carryforward": 1000, "raw_net": -5000},
     "expected_outputs": {"fk1b_available_basis": 3000, "consistent": False, "D_K1B_ARITH": True},
     "notes": "allowed 4,000 > available 3,000 → ERROR (the identity §704(d)(1) makes impossible)."},
    {"scenario_name": "K1B-T6 — distributions exceed basis: §731 flag, floor at zero", "scenario_type": "edge", "sort_order": 6,
     "inputs": {"tax_year": 2025, "beginning_basis": 2000, "current_additions": 500, "distributions": 4000,
                "current_loss": 3000, "allowed_loss": 0, "suspended_carryforward": 3000, "raw_net": -3000},
     "expected_outputs": {"fk1b_available_basis": 0, "fk1b_sche_net_limited": 0, "consistent": True,
                          "D_K1B_EXCESS_DISTRIB": True},
     "notes": "4,000 distributed against 2,500 basis → §731 warning; available floored at 0; all suspended."},
    {"scenario_name": "K1B-T7 — QBI is not double-limited", "scenario_type": "normal", "sort_order": 7,
     "inputs": {"tax_year": 2025, "beginning_basis": 9000, "current_additions": 2000, "distributions": 379,
                "current_loss": 26850, "allowed_loss": 10621, "suspended_carryforward": 16229,
                "raw_net": -26850, "section_199a_qbi": -10621},
     "expected_outputs": {"form_8995_line2_component": -10621},
     "notes": ("The K-1's §199A amount (already limited at the source to −10,621) flows to Form 8995 "
               "line 2 AS ENTERED — R-K1B-QBI: the worksheet cap never touches QBI.")},
]

N_RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R-K1B-SCOPE", "IRC_704D", "primary", "§704(d) is the partner-side limit (vs §1366(d)/Form 7203)"),
    ("R-K1B-ASSERT", "IRC_704D", "primary", "§704(d)(1) — loss allowed only to the extent of end-of-year basis"),
    ("R-K1B-ASSERT", "IRS_2025_1065_K1_INSTR", "secondary", "The partner tracks basis; the app records the determination"),
    ("R-K1B-ARITH", "IRC_704D", "primary", "The two identities any valid §704(d) worksheet satisfies"),
    ("R-K1B-ARITH", "TREAS_REG_1704_1D", "secondary", "§1.704-1(d)(2) — distributions before the loss test"),
    ("R-K1B-ORDER", "IRS_2025_1065_K1_INSTR", "primary", "The stated order: basis, at-risk, passive, EBL"),
    ("R-K1B-ORDER", "IRC_465", "secondary", "§465 at-risk is the second layer (Form 6198 R008 agrees)"),
    ("R-K1B-ORDER", "IRC_469", "secondary", "§469 passive is the third layer"),
    ("R-K1B-QBI", "TREAS_REG_199A3_PDL", "primary", "Suspended-loss QBI timing — never double-limit"),
    ("R-K1B-QBI", "IRC_199A", "secondary", "The QBI deduction the timing rule protects"),
    ("R-K1B-CARRY", "TREAS_REG_1704_1D", "primary", "Carryforward to succeeding years until basis is restored"),
    ("R-K1B-CARRY", "IRS_2025_1065_K1_INSTR", "secondary", "No attachment requirement — the partner's own record"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FLOW ASSERTIONS
# ═══════════════════════════════════════════════════════════════════════════

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-1040-K1B-01", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "A saved worksheet caps the K-1's Schedule E net at max(raw, −allowed) — once, in k1_sche_net()",
     "description": ("Validates R-K1B-ASSERT. Bug it catches: the full loss still routing to Schedule E "
                     "with the worksheet saved (the pilot's 90,041-vs-106,270 line 41); or the cap "
                     "applied in one consumer but not another (8582 gathering vs p2 totals vs diagnostics "
                     "disagreeing — the Form-7203 single-source-of-truth convention broken)."),
     "definition": {"kind": "formula_check", "form": "K1_BASIS_704D",
                    "formula": "sche_net_limited = max(raw_net, -allowed_loss)"},
     "sort_order": 1},
    {"assertion_id": "FA-1040-K1B-02", "assertion_type": "reconciliation", "entity_types": ["1040"],
     "title": "The worksheet reconciles: allowed + suspended = loss; allowed ≤ available basis",
     "description": ("Validates R-K1B-ARITH. Bug it catches: an inconsistent assertion passing silently, "
                     "or the app 'helpfully' recomputing an asserted figure."),
     "definition": {"kind": "reconciliation", "form": "K1_BASIS_704D",
                    "formula": ("allowed_loss + suspended_carryforward == current_loss and "
                                "allowed_loss <= max(0, beginning_basis + current_additions - distributions)")},
     "sort_order": 2},
    {"assertion_id": "FA-1040-K1B-03", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "The LIMITED net (not the raw net) reaches Schedule E line 41 → Schedule 1 line 5 → AGI",
     "description": ("Validates the flow target. Bug it catches: the cap applied at the K-1 but the raw "
                     "amount leaking into the line-41 summary or Schedule 1 line 5 (the AGI understatement "
                     "the pilot reported, which also flows to Georgia)."),
     "definition": {"kind": "flow_assertion", "form": "K1_BASIS_704D",
                    "checks": [{"source_line": "W8", "must_write_to": ["SCHEDULE_E.41", "SCH_1.5"]}]},
     "sort_order": 3},
    {"assertion_id": "FA-1040-K1B-04", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "Gates — an impossible worksheet is an ERROR; a flagged-but-unasserted K-1 keeps its warning",
     "description": ("An arithmetic-impossible worksheet (T4/T5) fires D_K1B_ARITH as an error, never "
                     "acknowledgable; basis_at_risk_limited with no worksheet keeps D_K1B_UNASSERTED "
                     "(the D_K1_BASIS successor) so the gap is never silent."),
     "definition": {"kind": "gating_check", "form": "K1_BASIS_704D", "expect": {"red_fires": True},
                    "blockers": ["arith_impossible", "unasserted_limited_flag"]},
     "sort_order": 4},
    {"assertion_id": "FA-1040-K1B-05", "assertion_type": "reconciliation", "entity_types": ["1040"],
     "title": "The suspended carryforward survives — reload, roll-forward, import/export",
     "description": ("Validates R-K1B-CARRY (the pilot's regression target 4). Bug it catches: the "
                     "suspended figure dropped on any persistence path. There is deliberately NO MeF/"
                     "render check here — the worksheet is not attached to the return."),
     "definition": {"kind": "reconciliation", "form": "K1_BASIS_704D",
                    "formula": "suspended_carryforward is preserved across reload/rollforward/import/export"},
     "sort_order": 5},
]


FORMS: list[dict] = [
    {"identity": N_IDENTITY, "facts": N_FACTS, "rules": N_RULES, "lines": N_LINES,
     "diagnostics": N_DIAGNOSTICS, "scenarios": N_SCENARIOS, "rule_links": N_RULE_LINKS},
]


class Command(BaseCommand):
    help = "Load the K1_BASIS_704D spec (partner §704(d) basis limitation). Refuses until READY_TO_SEED=True."

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING("\nLoad K1_BASIS_704D spec (partner §704(d) basis limitation)\n"))
        self._load_topics()
        sources = self._load_sources()
        self._load_new_excerpts_on_existing(sources)
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
                "\nREFUSING TO SEED K1_BASIS_704D: not cleared to seed.\n\n"
                "Gated until Ken's Gate-1 review walk (the preparer-asserted shape; the\n"
                "arithmetic checks; the no-attachment scope finding; the QBI no-double-limit\n"
                "rule; the v1 nonpassive-only scope).\n\n"
                f"READY_TO_SEED = {READY_TO_SEED} (must be True)\n\n"
                f"Currently empty / placeholder:\n  {still_empty}\n"
            )

    def _load_topics(self):
        ct = 0
        for code, name in AUTHORITY_TOPICS:
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
        for code in EXISTING_SOURCES_TO_REFERENCE:
            src = AuthoritySource.objects.filter(source_code=code).first()
            if src:
                sources[code] = src
        self.stdout.write(f"Sources ready: {len(sources)}")
        return sources

    def _load_new_excerpts_on_existing(self, sources):
        for code, exc in NEW_EXCERPTS_ON_EXISTING:
            src = sources.get(code) or AuthoritySource.objects.filter(source_code=code).first()
            if src:
                exc = dict(exc)
                AuthorityExcerpt.objects.update_or_create(
                    authority_source=src, excerpt_label=exc["excerpt_label"], defaults=exc)

    def _upsert_form(self, identity: dict) -> TaxForm:
        form, created = TaxForm.objects.update_or_create(
            form_number=identity["form_number"], jurisdiction=FORM_JURISDICTION,
            tax_year=FORM_TAX_YEAR, version=FORM_VERSION,
            defaults={"form_title": identity["form_title"], "entity_types": FORM_ENTITY_TYPES,
                      "status": FORM_STATUS, "notes": identity["notes"]})
        self.stdout.write(f"{'Created' if created else 'Updated'} {identity['form_number']}")
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
        self.stdout.write(f"  {len(FLOW_ASSERTIONS)} flow assertions")

    def _report_totals(self):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"TaxForms: {TaxForm.objects.count()} | FlowAssertions: {FlowAssertion.objects.count()}")
        form = TaxForm.objects.filter(form_number="K1_BASIS_704D").first()
        if form:
            uncited = [r for r in FormRule.objects.filter(tax_form=form) if not r.authority_links.exists()]
            self.stdout.write("K1_BASIS_704D: all rules cited" if not uncited
                              else self.style.WARNING(f"K1_BASIS_704D uncited rules: {len(uncited)}"))
