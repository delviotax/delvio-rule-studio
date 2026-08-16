"""Load the TN_FAE170 spec — Tennessee Franchise & Excise Tax Return (TY2025).

═══════════════════════════════════════════════════════════════════════════
WHAT THIS IS
═══════════════════════════════════════════════════════════════════════════
Tennessee has NO partnership return, NO S-corp return and NO C-corp return.
It has ONE return — **FAE170** — carrying TWO separately-computed taxes that
share no base:

    FRANCHISE (Schedule A)                 EXCISE (Schedule B)
     F1 net worth ─┐                        J1/J2/J3/J4 ─→ Sch. J L1
     Sch. G L15 ───┴→ MAX(A1, A2)                        ↓ 27 modifications
        × 0.25% ("25c per $100 or major                  ↓ Sch. J L39
         fraction thereof"), minimum $100 → A3     × 6.5% → B5 (+B6) → B7
                          └────────→ C8 = A3 + B7 ←────────┘

**THE DEFINING STRUCTURAL FACT** — the net-earnings starting point branches on
federal classification through FOUR entry schedules and then converges:

    1065  → Schedule J1 (L11) ─┐
    1040  → Schedule J2 (L9)  ─┤
    1120S → Schedule J3 (L7)  ─┼→ Schedule J, Line 1 → ... → L39 → Sch. B L4
    1120  → Schedule J4 (L11) ─┘

Sch. J Line 1 instruction, verbatim: `Enter the applicable amount from line 11,
9, 7, or 11 of Schedule J1, J2, J3, or J4, respectively.`

That is why ONE RS spec serves THREE delvio-tax modules — FORM_ENTITY_TYPES =
["1065", "1120S", "1120"]. The **J2 path additionally reaches an individual-owned
single-member LLC** (a 1040 client's SMLLC is an FAE170 taxpayer in its own
right — conformity §5, walk item W10). "1040" is deliberately NOT in
FORM_ENTITY_TYPES: FAE170 is never filed *by* a 1040; it is filed by the LLC.
The trigger placement is W10, an open question for Ken.

Tennessee is an **entity-only** state: no individual income tax (Hall repealed
for periods beginning on/after 1/1/2021), no fiduciary return, **no PTET and
structurally no room for one** (there is no owner-level tax to credit). The
imposition test is **limited liability, not federal classification**.

**NOT A CLONE OF ANY EXISTING SPEC.** Different base (net worth + net earnings,
not income), different filers (LLCs/LPs taxed as entities), rolling conformity
frozen at TCJA §168(k), §179 conforming at full OBBBA figures, no PTET table,
no owner credit, no K-1 state column.

NO prior RS spec exists (lookup/TN_FAE170/export/ → 404, confirmed 2026-08-15).
NEW form. Code namespaced `<ST>_<FORM>` per campaign D-9.

═══════════════════════════════════════════════════════════════════════════
v1 SCOPE — PROPOSED (source brief §13; NOT yet walked with Ken)
═══════════════════════════════════════════════════════════════════════════
COMPUTES (v1):
  • Schedule A — L3 = **MAX(L1, L2) × 0.25%** with `major fraction thereof`
    rounding and the **$100 minimum**; short-period proration floored at $100;
    NO proration for 52/53-week filers. (Never `L1 × 0.0025` — the greater-of
    is live even though Schedule G is opt-in.)
  • Schedule B — L5 = L4 × 6.5%, zero if L4 is a loss; L7 = L5 + L6.
  • Schedule C — L8..L16, the credit cap (L9 ≤ L8) **with the Green Energy
    exception**, L10 floored at zero, refund/credit-forward split.
  • **Schedules J1, J2, J3, J4** — all four entry points, every add/subtract
    line, each wired to its verified federal source. Includes the J1/J3 §179
    pro-forma disposition entry points and the **J4 contribution /
    capital-loss timing reversals** (L5/L6/L8/L9).
  • **Schedule J** — the full modification engine: L15, L30 (**excluding
    L28b**), L31; the **$50,000 PRE-apportionment standard deduction** (L32);
    L33 optional addback; L34; L36 = L34 × L35; **L37 nonbusiness
    POST-apportionment**; **L38 NOL LAST**; L39.
  • Schedule M spillover deduction; Schedule K's four reversals; Schedule U
    (15-year, oldest-first).
  • Schedule N — **single sales factor, ONE line**, one ratio to BOTH F1 L4
    and J L35.
  • Schedule F1 — one-way affiliate-indebtedness add-back, **$2B manufacturer
    cap**.
  • Schedule E estimates ($5,000-both-years test, standard-method installments),
    the FAE173 extension test, Schedule T Part 1, Schedule H.
  • The inactive-entity **page-1-only** filing mode and the **P.L. 86-272
    franchise-only** mode (checkbox c).

DIRECT-ENTRY (line exists; each carries a diagnostic prompt):
  • Every Schedule J modification AMOUNT (L2–L14, L16–L29) — the engine computes
    the subtotals and the flow; the preparer supplies each modification.
    **Including L3, L16, L17** per W3 (no TN-basis depreciation engine in v1).
  • Schedule F1 GAAP balance-sheet inputs; Schedule A **Line 2** (Sch. G total,
    so the greater-of is live); Schedule D Lines 1–4 and 6–9; Schedule V /
    Schedule PLCF carryover tables; Schedule M detail rows; Schedule I roster;
    Schedule N numerator/denominator; Schedule C L12–L15; Schedule U rows.

RED-DEFERS (each gets its OWN diagnostic — no silent gap; house rule):
  R1 Schedule G property-measure election · R2 Schedule F2 consolidated net
  worth · R3 Schedule N1 (three-factor / Telecom Qualified Member) · R4
  Schedules O/P/R · R5 **FAE174** (financial institutions, captive REITs —
  a HARD STOP, not a note) · R6 Schedule X · R7 Schedule QP · R8 Schedule BP ·
  R9 Schedule T Part 2 recapture · R10 certified distribution sales additional
  excise tax · R11 annualized income installment method · R12 FAE183 exemption
  applications · R13 **the OBBBA post-2022 bonus differential** · R14 Form IE ·
  R15 Tennessee business tax (BUS 428 — informational only).

═══════════════════════════════════════════════════════════════════════════
requires_human_review WALK ITEMS (source brief §12) — W1/W2 FIRST because they
are the two that change numbers on ORDINARY returns.
═══════════════════════════════════════════════════════════════════════════
W1. **BONUS KEYED TO *ACQUIRED* OR *PLACED IN SERVICE*? — ESCALATED, KEN'S CALL.**
    The DOR contradicts itself inside one manual: p. 225 table caption `Asset
    Acquired Between:` vs p. 267 `qualified property placed in service in 2025`.
    Diverges for an asset acquired 2024 / placed in service 2025 (60% vs 40%)
    AND decides which of the two regimes an asset falls into. Already
    `delvio-states/GATE1_WALK.md` item 3. Brief's recommendation: build to
    PLACED IN SERVICE, flag, confirm with DOR — **record as a RULING, not a
    finding.** ⚠ NO COMPUTED RULE IN THIS SPEC PICKS A KEY. `_tn_tcja_bonus_pct`
    takes a caller-supplied year and refuses to derive it. Diagnostic
    D_TN170_BONUS_KEY_W1.
W2. **WHICH SCHEDULE J LINES CARRY THE POST-2022 OBBBA DIFFERENTIAL (U1)?**
    Form face + instructions scope L3/L16/L17 verbatim to `assets purchased on
    or before December 31, 2022`; manual p. 223 says do not adjust those lines
    for post-2022 assets *unless federal law is amended to diverge*; the OBBBA
    chapter (pp. 267–268) mandates Schedule J adjustments for exactly that
    divergence **without naming a line**. The DOR re-stamped the form
    2025-12-31 — after OBBBA and after the manual — and still did not
    reconcile it. Working assumption: **L3/L16/L17 carry BOTH regimes** (there
    is no other line). v1 RED-DEFERS the differential (R13) rather than
    guessing. Diagnostic D_TN170_OBBBA_BONUS_DIFF.
W3. **TN depreciation basis engine in v1, or direct-entry L3/L16/L17?** A full
    engine means two simultaneous regimes, a separate TN asset ledger, and
    disposition true-ups on L17. Brief: v1 direct-entry with a hard diagnostic
    when Form 4562 Line 14 or Line 25 is non-zero and Sch. J L3 is blank; v1.1
    the engine. Largest single scope lever; Ken is the depreciation specialist.
W4. **Schedule G in or out of v1?** Opt-in, rare, annual TNTAP-submitted
    election carrying a constitutional waiver, narrative guidance in a
    superseded manual. Brief: RED-defer Schedule G but **build Sch. A L3 as a
    live MAX(L1, L2)** with L2 direct-entry. ⚠ The old "Schedule G is not in
    the MeF accepted-forms list" rationale was REFUTED (verification C1) — the
    decision stands, the justification changed. D_TN170_SCHED_G says nothing
    about MeF.
W5. **Schedule F2 / consolidated net worth in v1?** Requires the Consolidated
    Net Worth Election, a pro forma consolidated GAAP balance sheet, and
    Schedules 170NC/170NC1/170SF. Brief: RED-defer.
W6. **Schedule N1 (three-factor election + Telecom Qualified Member)?** N1
    produces TWO ratios (franchise via L14, excise via L13) and carries the
    zero-denominator elimination rule; the election also requires proving a
    *higher* ratio, i.e. computing both formulas. Brief: RED-defer N1/O/P/R;
    compute Schedule N single sales factor only.
W7. **Which credits does v1 compute?** Brief: compute Schedule T Part 1
    (1% or the approved enhanced rate × purchase price; least of L5/L7/L10),
    direct-enter Sch. D L1–4 and L6–9, RED-defer T Part 2 / X / QP / BP.
    Preserve the Green Energy exception to the Sch. C L8 cap.
W8. **Confirm the $100-minimum-vs-credits reading (U8) and the `major fraction
    thereof` rounding.** Sch. C L9 is capped only at `cannot exceed Schedule C,
    Line 8` and L10 floors at zero — so on the form's arithmetic a large credit
    reduces net tax below the $100 franchise minimum. NO DOR statement exists
    either way. Both are one-line spec constants that silently change every
    small return. Ken must bless or overrule, not the spec assume.
W9. **Franchise-tax proration on initial and short-period returns.** Prorate
    from `Date Tennessee operations began` / formation, floor at $100, NO
    proration for 52/53-week filers, NEVER prorate excise. Confirm the
    day-count convention (the manual's own annualization example uses 365.25).
W10. **The SMLLC (Schedule J2) path is an INDIVIDUAL-module obligation living
    in an entity form.** A 1040 client with a Tennessee SMLLC owes an FAE170
    that no 1040 workflow will surface. Decide where the trigger lives — a
    client-exposure question, not only a spec question.

Carried `[UNVERIFIED]` / open items (source brief §11): **U1** OBBBA line
assignment (=W2) · **U2** acquired-vs-placed-in-service (=W1, ESCALATED) ·
**U3** short periods beginning in 2025 and ending before 12/31/2025 fall in the
11×/13 statutory row but the TY2025 Schedule N has one line and cannot express
it · **U4** the Sch. J L13 instruction's `Sch. J, Line 27a` cross-reference is
an ERRATUM — there is no L27a; build to **L28a** (resolved, recorded so nobody
"fixes" it back) · **U5** certified distribution sales additional excise tax has
no schedule in the kit and no formula in the instructions · **U6** Schedules X,
QP, BP line maps not transcribed · **U7** TN MeF schema and business rules not
obtained (gated behind DOR software-vendor registration — a lead-time-bearing
KEN action: a sales-tax account, then software.registration@tn.gov, then
efile.questions@tn.gov) · **U8** whether credits may reduce net tax below the
$100 franchise minimum (=W8) · **U9** whether the TN MeF FAE170 schema carries
Schedule G detail lines 1–15 or only the Sch. A L2 total (folds into U7; does
not affect v1). Also: the FAE183 PDF has not been reissued since **2023-02-01**
and therefore predates PC 950 (2024) and PC 455 (2025) — the exemption module
must not assume it reflects 2025 law.

═══════════════════════════════════════════════════════════════════════════
VERIFIED STRUCTURE + CONSTANTS — provenance
═══════════════════════════════════════════════════════════════════════════
Every line number and verbatim label below was read out of the FINAL TY2025 DOR
PDFs, then INDEPENDENTLY RE-DERIVED by an adversarial verification pass
(2026-08-16). **No line number in the brief was wrong.** Exact documents:

  • **Form FAE170 (2025)** — `FAE170_2025.pdf`, rev. `RV-R0011001 (9/25)`,
    /ModDate 2025-12-31, 10 pp. (md5 476a5392db72c1dc466d446835540f4e, byte-
    identical across both passes). ⚠ Its embedded PDF *title* metadata reads
    `...January 1, 2024 and after` — STALE metadata carried from the prior year.
    The FORM FACE (`2025 Franchise and Excise Tax Return`) and the revision code
    govern. Do not treat the metadata as a form-year signal.
  • **2025 FAE170 Instructions** — `fae170instructions2025.pdf`, /ModDate
    2025-12-31, 15 pp.
  • **Franchise & Excise Tax Manual, December 2025** — 563 pp., /ModDate
    2025-12-21 (imposition p. 17–18; exemptions/FAE183 pp. 26–28; FI test p. 55;
    due dates/extension/proration pp. 89–92; estimates pp. 108–110; Sch. G
    election p. 198; bonus depreciation pp. 222–225; standard deduction +
    optional addback pp. 257–258; **OBBBA chapter pp. 267–272**; NOL p. 298).
  • **Franchise & Excise Tax Manual, December 2023** — 621 pp., /ModDate
    2023-12-08. REQUIRED for Schedule G: the Dec 2025 manual removed all
    Schedule G guidance. Load-bearing only for sub-rent and finance-vs-operating
    -lease rules (the 8/3/2/1 multipliers are printed on the CURRENT form face —
    verification C3).
  • **Schedule G — Determination of Real and Tangible Property**,
    `RV-F700012 (12/24)` and **Schedule G Minimum Property Measure Election**,
    also `RV-F700012 (12/24)`. ⚠ **Both documents carry the SAME revision code
    at different URLs — never key on `RV-F700012` as a unique document id.**
  • **Schedule PL / PLCF**, `RV-F700009 (9/25)` — carryforward-ONLY on the
    TY2025 form (credit expired for tax years ending on/after 12/31/2025;
    25-year carryforward).
  • **FAE173** `RV-R0011401 (12/25)` · **FAE172 (2025)** · **FAE183** (current
    file, not reissued since 2023-02-01).
  • **Tenn. Code Ann.** §§ 67-4-2004, -2006, -2007, -2008, -2009, -2012, -2023,
    -2103, -2104, -2105(a), -2106, -2107, -2108, -2109(m), -2111, **-2119**
    ($100 min), **-2121** ($2B manufacturer cap), **-2123** (annual
    minimum-measure election). Session laws: **PC 377 (2023)** (Tennessee Works
    Tax Act), **PC 950 (2024)** (property-measure repeal + election),
    **PC 343 (2025)** (optional deduction addback), **PC 455 (2025)**,
    2002 Pub. Ch. 856 (6.5% rate).
  • **FINAL 2025 IRS forms** — 1065, 1120-S, 1120, 1120-REIT, 990-T, 4562,
    8990 (Rev. 12-2025), 1040 Sch. C, 1040 Sch. F — every federal line number
    TN's instructions cite was re-read off the IRS PDF, not taken on trust.

Full source brief: `delvio-states/research/tn_entity_source_brief.md` (VERIFIED,
adversarial pass 2026-08-16 — its §15 Verification governs where it differs from
the body). Conformity: `delvio-states/conformity/tn_conformity.md` (VERIFIED
2026-08-06; its §12 governs).

═══════════════════════════════════════════════════════════════════════════
SAFETY GUARD — READY_TO_SEED stays False until Ken approves the review walk
(W1–W10) in-session. Until then the command refuses to write to the DB.
DO NOT relax the guard to silence the error. DO NOT COMMIT. DO NOT SEED.
═══════════════════════════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════════════════════════
# SAFETY GUARD — flip ONLY after Ken's in-session review walk (W1-W10 above).
# W1 (bonus keying) is an ESCALATED judgement call recorded in
# delvio-states/GATE1_WALK.md item 3 — it must be RULED, not assumed, before
# this sentinel moves.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = False


FORM_JURISDICTION = "TN"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"
# ONE return serves THREE federal entity types. The J2 path additionally reaches
# an individual-owned SMLLC, but the filer is the LLC, never the 1040 — see W10.
FORM_ENTITY_TYPES = ["1065", "1120S", "1120"]


# ═══════════════════════════════════════════════════════════════════════════
# VERIFIED CONSTANTS (year-keyed; every one cited in tn_entity_source_brief.md
# and/or tn_conformity.md; NEVER from memory).
# A NEW TAX YEAR STALENESS-INVALIDATES ALL OF THESE until re-verified.
# ═══════════════════════════════════════════════════════════════════════════

# Excise tax rate — Sch. B L5 `Excise tax (6.5% of Line 4)`.
# Tenn. Code Ann. § 67-4-2007; rate set by 2002 Tenn. Pub. Ch. 856.
TN_EXCISE_RATE: dict[int, str] = {2025: "0.065"}

# Franchise tax — Sch. A L3 `25c per $100 or major fraction thereof`.
# Tenn. Code Ann. §§ 67-4-2104, -2105(a).
TN_FRANCHISE_PER_HUNDRED: dict[int, str] = {2025: "0.25"}   # dollars per $100 unit
TN_FRANCHISE_RATE: dict[int, str] = {2025: "0.0025"}        # equivalent ad-valorem rate
TN_FRANCHISE_MINIMUM: dict[int, int] = {2025: 100}          # § 67-4-2119
TN_MANUFACTURER_BASE_CAP: dict[int, int] = {2025: 2_000_000_000}   # § 67-4-2121

# Excise tax standard deduction — Sch. J L32, PRE-apportionment, lesser of L31 or
# this figure, cannot create/increase a loss, no carryforward, ONE per return.
# Effective for tax years ending on/after 12/31/2024 → applies for TY2025.
TN_EXCISE_STANDARD_DEDUCTION: dict[int, int] = {2025: 50_000}

# Tennessee loss carryover — Schedules K and U. Computed SEPARATELY from federal.
TN_NOL_CARRYFORWARD_YEARS: dict[int, int] = {2025: 15}
TN_CREDIT_CARRYFORWARD_YEARS: dict[int, int] = {2025: 25}   # Schedule V (industrial machinery / job credits)

# GILTI / § 951A — full amount deducted on Sch. J L27, 5% added back on L12, so a
# NET 5% is taxed; the § 250 deduction is NOT allowed.
# Tenn. Code Ann. §§ 67-4-2006(b)(1)(P), (b)(2)(T).
TN_GILTI_ADDBACK_PCT: dict[int, str] = {2025: "0.05"}

# Sch. J L19 — the FORM LABEL OMITS THE PERCENTAGE; the instruction says
# `Enter 75% of donations...`. §§ 67-4-2006(b)(2)(M) and (P). Certification required.
TN_SCHOOL_DONATION_PCT: dict[int, str] = {2025: "0.75"}

# § 179 — TN CONFORMS at full OBBBA figures via rolling conformity (manual p. 270).
# No state limit, no add-back. Contrast §168(k) below: the two OBBBA depreciation
# provisions split in OPPOSITE directions.
TN_179_LIMIT: dict[int, int] = {2025: 2_500_000}
TN_179_PHASEOUT: dict[int, int] = {2025: 4_000_000}

# § 168(k) bonus — TN is frozen at the TCJA version (PC 377 (2023);
# Tenn. Code Ann. § 67-4-2006(a)(12)) and will REMAIN so unless conforming state
# legislation is enacted. OBBBA 100% bonus is NOT available in Tennessee.
# Table is the manual p. 225 phase-down, printed under the caption
# `Asset Acquired Between:` — while manual p. 267 keys the same 40/20/0 to
# property `placed in service`. ⚠ W1/U2: THE KEY IS UNRESOLVED AND IS KEN'S CALL.
# The PERCENTAGES are verified; only the keying is open.
TN_TCJA_BONUS_PHASEDOWN: dict[int, list] = {2025: [
    (2017, 2022, "1.00"),   # 9/28/2017-12/31/2022 (pre-2023 regime: bonus FULLY DISALLOWED for TN)
    (2023, 2023, "0.80"),
    (2024, 2024, "0.60"),
    (2025, 2025, "0.40"),   # TY2025 TN percentage
    (2026, 2026, "0.20"),
    (2027, 9999, "0.00"),
]}
# The regime boundary: assets purchased ON OR BEFORE this date get FULL bonus
# disallowance (Sch. J L3/L16/L17); assets after it follow the TCJA table above.
TN_BONUS_REGIME_A_LAST_DATE: dict[int, str] = {2025: "2022-12-31"}

# Schedule G rental multipliers — PRINTED ON THE CURRENT FORM FACE
# (`RV-F700012 (12/24)`, x8/x3/x2/x1 against Lines 11-14). Verification C3
# downgraded the superseded Dec 2023 manual to corroborating.
# ⚠ DIFFERENT from Schedule N1, where ALL rents use x8, and Sch. G is GAAP net
# book value while N1 is original tax-basis cost. Do NOT share a property model.
TN_SCHED_G_RENT_MULTIPLES: dict[int, dict] = {2025: {
    "real_property": 8,                 # L11
    "mfg_machinery_equipment": 3,       # L12
    "furniture_office_equipment": 2,    # L13
    "delivery_mobile_equipment": 1,     # L14
}}

# Sch. G L7b / Sch. N1 L8 — exempt finished-goods inventory in excess of this
# amount. Tenn. Code Ann. § 67-4-2108(a)(6)(B).
TN_EXEMPT_FINISHED_GOODS_THRESHOLD: dict[int, int] = {2025: 30_000_000}

# Estimated payments (manual pp. 108-110). Required only when combined franchise
# and excise liability AFTER CREDITS is at/above this figure for BOTH the prior
# and the current tax year. A short PRIOR period is annualized for the test; the
# current year is not.
TN_ESTIMATE_THRESHOLD: dict[int, int] = {2025: 5_000}
TN_ESTIMATE_PRIOR_PCT: dict[int, str] = {2025: "0.25"}          # 25% of prior-year total liability
TN_ESTIMATE_CURRENT_PCT: dict[int, str] = {2025: "0.20"}        # 25% of 80% = 20% of projected current
TN_ESTIMATE_IMMEDIATE_FUNDS: dict[int, int] = {2025: 2_500}     # >= this must be remitted in immediately available funds
# Due: 15th day of the 4th, 6th and 9th month of the current taxable year, and
# the 1st month of the SUBSEQUENT taxable year.
TN_ESTIMATE_DUE_MONTHS: dict[int, list] = {2025: [4, 6, 9, "1-next"]}

# Extension — FAE173, SEVEN months. Payment by the ORIGINAL due date must equal
# the LESSER of 90% of the current year's liability or 100% of the prior year's
# (annualized if the prior year was short). If the prior year's liability was
# ZERO the required extension payment is $100. Automatic if payments suffice.
TN_EXTENSION_MONTHS: dict[int, int] = {2025: 7}
TN_EXTENSION_CURRENT_PCT: dict[int, str] = {2025: "0.90"}
TN_EXTENSION_PRIOR_PCT: dict[int, str] = {2025: "1.00"}
TN_EXTENSION_PRIOR_ZERO_PAYMENT: dict[int, int] = {2025: 100}

# Schedule T Part 1 — industrial machinery / R&D equipment credit.
# Generally 1%; enhanced by approved capital investment (§ 67-4-2009(3)(I)).
TN_IM_CREDIT_BASE_RATE: dict[int, str] = {2025: "0.01"}
TN_IM_CREDIT_ENHANCED: dict[int, list] = {2025: [
    (100_000_000, "0.03"), (250_000_000, "0.05"), (500_000_000, "0.07"), (1_000_000_000, "0.10"),
]}
TN_IM_CREDIT_LIMIT_PCT: dict[int, str] = {2025: "0.50"}   # Sch. T L7 = 50% of pre-credit liability

# Nexus — bright-line presence (Revenue Modernization Act). TN receipts > the
# LESSER of $500,000 or 25% of total; TN property > the lesser of $50,000 or 25%;
# TN compensation > the lesser of $50,000 or 25%. Physical presence not required.
# A TN-DOMESTIC entity is ALWAYS subject and owes the $100 minimum regardless.
TN_NEXUS_RECEIPTS: dict[int, int] = {2025: 500_000}
TN_NEXUS_PROPERTY: dict[int, int] = {2025: 50_000}
TN_NEXUS_COMPENSATION: dict[int, int] = {2025: 50_000}
TN_NEXUS_PERCENTAGE: dict[int, str] = {2025: "0.25"}

# Nonbusiness earnings — default expense assumptions where not substantiated
# (Tenn. Comp. R. & Regs. 1320-06-01-.23(3)).
TN_NONBUSINESS_RENTAL_EXPENSE_PCT: dict[int, str] = {2025: "0.50"}
TN_NONBUSINESS_OTHER_EXPENSE_PCT: dict[int, str] = {2025: "0.05"}

# Penalties — delinquency 5% per 30-day period, max 25%, minimum $15
# (§ 67-1-804); estimated-payment penalty 2%/month to 24%; negligence 10%;
# intangible-expense nondisclosure the GREATER of $10,000 or 50% of the
# adjustment; FAE183 late filing $200 per occurrence (does NOT forfeit the
# exemption); a refund of $200+ on an amended return needs a Report of Debts.
TN_PENALTY_DELINQUENCY_PCT: dict[int, str] = {2025: "0.05"}
TN_PENALTY_DELINQUENCY_MAX: dict[int, str] = {2025: "0.25"}
TN_PENALTY_DELINQUENCY_MIN: dict[int, int] = {2025: 15}
TN_PENALTY_ESTIMATE_PCT: dict[int, str] = {2025: "0.02"}
TN_PENALTY_ESTIMATE_MAX: dict[int, str] = {2025: "0.24"}
TN_PENALTY_NEGLIGENCE_PCT: dict[int, str] = {2025: "0.10"}
TN_PENALTY_INTANGIBLE_FLOOR: dict[int, int] = {2025: 10_000}
TN_PENALTY_INTANGIBLE_PCT: dict[int, str] = {2025: "0.50"}
TN_PENALTY_FAE183_LATE: dict[int, int] = {2025: 200}

# Filing scope — 17 exemptions at Tenn. Code Ann. § 67-4-2008; exactly TEN of
# them require FAE183 for the initial and each subsequent period (counted off the
# manual's own asterisks, pp. 26-27). PC 455 (2025) agricultural-cooperative
# subsidiaries are NOT an 18th exemption — they are not taxpayers at all.
TN_EXEMPTION_COUNT: dict[int, int] = {2025: 17}
TN_EXEMPTIONS_REQUIRING_FAE183: dict[int, list] = {2025: [
    "venture_capital_fund",
    "farming_or_personal_residence",
    "affiliate_receivables",
    "lihtc_affordable_housing",
    "obligated_member_entity",
    "asset_backed_securities",
    "family_owned_noncorporate_entity",
    "diversified_investing_fund",
    "armed_forces_facility_entity",
    "low_income_historic_structure",
]}

# Due date: 15th day of the 4th month following the period end shown on the
# CORRESPONDING FEDERAL RETURN. The TN period MUST coincide with the federal one.
TN_DUE_MONTHS_AFTER_PERIOD_END: dict[int, int] = {2025: 4}
TN_DUE_DAY: dict[int, int] = {2025: 15}
TN_EFILE_PERFECTION_DAYS: dict[int, int] = {2025: 10}


def _yk(d: dict, year: int):
    """Year-keyed constant lookup, falling back to the authored year."""
    return d.get(year) if d.get(year) is not None else d[2025]


def _f(x) -> float:
    return float(x or 0)


# ═══════════════════════════════════════════════════════════════════════════
# PURE HELPERS — the arithmetic the harness proves. No DB, no Django.
# ═══════════════════════════════════════════════════════════════════════════

def _tn_hundreds_major_fraction(base) -> int:
    """$100 units for Sch. A L3, with `or major fraction thereof` rounding.

    Verbatim: `Franchise tax (25c per $100 or major fraction thereof on the
    greater of Lines 1 or 2; minimum $100)`. A remainder exceeding $50 is a
    MAJOR fraction and rounds the base UP to the next $100. This is a real
    rounding rule, not decoration (W8 — Ken to bless the >50 vs >=50 reading).
    """
    b = max(0.0, _f(base))
    units = int(b // 100)
    if (b - units * 100) > 50:
        units += 1
    return units


def _tn_franchise_tax(f1_net_worth, schedule_g_l15=0.0, year=2025,
                      proration=1.0, is_5253_week_filer=False):
    """Schedule A. Returns (base_used, tax).

    L1 = Sch. F1 L5 or Sch. F2 L3 · L2 = Sch. G L15 (opt-in ONLY; blank
    otherwise) · **L3 = MAX(L1, L2) rounded to $100 units x $0.25, floored at
    the $100 minimum**.

    ⚠ THE GREATER-OF IS LIVE. Schedule G is opt-in and RED-deferred in v1 (W4),
    but L2 is direct-entry so the arithmetic is right the day Schedule G lands.
    NEVER collapse this to `L1 * 0.0025`.

    Proration: franchise tax MAY be prorated on short-period/initial returns but
    NEVER below the $100 minimum, and NOT AT ALL for 52/53-week filers (W9).
    Excise tax is never prorated.
    """
    base = max(_f(f1_net_worth), _f(schedule_g_l15))
    tax = _tn_hundreds_major_fraction(base) * float(_yk(TN_FRANCHISE_PER_HUNDRED, year))
    if not is_5253_week_filer:
        tax = tax * _f(proration)
    return base, max(tax, float(_yk(TN_FRANCHISE_MINIMUM, year)))


def _tn_f1_net_worth(net_worth, affiliate_indebtedness, ratio,
                     is_manufacturer=False, year=2025):
    """Schedule F1 — Non-Consolidated Net Worth (the DEFAULT path).

    L1 net worth (total assets less total liabilities, **GAAP basis**, or the
    taxpayer's federal tax accounting method if it does not keep GAAP books) ·
    L2 indebtedness to or guaranteed by a parent/affiliate — a ONE-WAY
    thin-capitalization add-back (§ 67-4-2107(b)): `This amount cannot be a
    deduction.` · L3 = L1 + L2 · L4 apportionment ratio · L5 = L3 x L4,
    capped at $2 BILLION for a manufacturer (§ 67-4-2121) → Sch. A L1.

    ⚠ This is the data-capture surface the 1065/1120S/1120 modules do not
    otherwise have. Net worth comes off a GAAP BALANCE SHEET. NOTHING on
    Schedules J1-J4 feeds it — the federal handoff is one-directional and lossy
    and covers only the EXCISE half of FAE170.
    """
    l3 = _f(net_worth) + max(0.0, _f(affiliate_indebtedness))
    l5 = l3 * _f(ratio)
    if is_manufacturer:
        l5 = min(l5, float(_yk(TN_MANUFACTURER_BASE_CAP, year)))
    return l5


def _tn_excise_tax(sch_j_l39, year=2025):
    """Schedule B L5 — `Excise tax (6.5% of Line 4)`; `If Line 4 is a loss,
    enter zero.` The $100 minimum FRANCHISE tax is still due on a loss year."""
    return max(0.0, _f(sch_j_l39)) * float(_yk(TN_EXCISE_RATE, year))


# ── The four Schedule J entry points ───────────────────────────────────────
# Sch. J L1 instruction, verbatim: `Enter the applicable amount from line 11, 9,
# 7, or 11 of Schedule J1, J2, J3, or J4, respectively.`

def _tn_j1_total(l1_ordinary_1065_l23, l2_allocated_income, l3_reit_loss,
                 l5_allocated_expense, l6_self_employment, l7_qualified_plan,
                 l8_reit_gain, l9_loss_asset_sold_12mo):
    """Schedule J1 — Entities Treated as Partnerships (federal 1065).
    Returns (L4 additions, L10 deductions, L11 total → Sch. J L1).

    L1 = 1065 Line 23 `Ordinary business income (loss)` · L2 = Sch. K Lines 2-11
    (EXCLUDE L11 §743(b) code F; INCLUDE §179-disposition gain at box 20 code L)
    · L3 REIT loss/expense · **L4 = L1+L2+L3** · L5 = Sch. K Lines 12 and 13a-e
    (EXCLUDE L13 §743(b) code V; EXCLUDE qualified-plan contributions, which go
    to L7; INCLUDE §179-disposition loss at box 20 code L) · **L6 self-employment
    earnings** · **L7 qualified pension / all IRC 401 plans** · L8 REIT gain ·
    L9 12-month distribution loss · **L10 = L5..L9** · **L11 = L4 - L10**.

    ⚠ **L6 AND L7 ARE THE CLONE TRAP.** They exist ONLY here (and L6's analogue
    at J2 L8). Schedule J3 has NEITHER — see `_tn_j3_total`.
    ⚠ L6/L7 are loss-limited (`This deduction cannot create or increase a loss
    carryover`) and are BOTH REVERSED on Schedule K Line 3.
    ⚠ L6 is taken NET of pass-through expense deducted elsewhere on the return,
    `such as IRC Section 179 expenses **and contributions deducted on Line 5**`.
    ⚠ §179 PRO-FORMA RULE (L2 and L5): the disposition gain/loss is computed at
    the ENTITY level and `any Section 179 expense limits that would have been
    imposed for federal income tax purposes at the partner level should be
    disregarded` — an entity-level recomputation with NO federal analogue.
    """
    l4 = _f(l1_ordinary_1065_l23) + _f(l2_allocated_income) + _f(l3_reit_loss)
    l10 = (_f(l5_allocated_expense) + _f(l6_self_employment) + _f(l7_qualified_plan)
           + _f(l8_reit_gain) + _f(l9_loss_asset_sold_12mo))
    return l4, l10, l4 - l10


def _tn_j2_total(l1_sch_c_l31, l2_sch_d, l3_sch_e, l4_sch_f_l34,
                 l5_form_4797, l6_other, l8_self_employment):
    """Schedule J2 — Single Member LLC Filing as an Individual (federal 1040).
    Returns (L7 additions, L9 total → Sch. J L1).

    **L7 = L1..L6 · L9 = L7 - L8.**

    ⚠ THE `no individual income tax != no individual filing` TRAP. Tennessee has
    no individual income tax, but a single-member LLC owned by a NATURAL PERSON
    is an FAE170 taxpayer in its own right. Disregarded entities are NOT
    disregarded for F&E — except an SMLLC whose single member is a CORPORATION
    (§§ 67-4-2007(d), 67-4-2106(c)) and an SMLLC wholly owned by a PENSION TRUST.
    Where this trigger lives relative to the 1040 module is walk item **W10**.

    ⚠ VERIFICATION C5 — THE FORM FACE AND THE INSTRUCTIONS DO NOT READ ALIKE.
    The PRINTED FORM carries NO federal line numbers at all: L1-L5 read verbatim
    `Business Income or loss from federal Form 1040, Schedule C` / `Schedule D` /
    `Schedule E` / `Schedule F` / `Business Income or loss from federal Form
    4797`. The federal line numbers exist ONLY in the instructions, and only for
    two of them: L1 → Sch. C **Line 31**; L4 → Sch. F **Line 34**. Sch. D,
    Sch. E and Form 4797 are given NO line number by EITHER document. A UI built
    from instruction text alone will not match the printed form.
    L2 is entered as a NEGATIVE if it is a loss. L6 is free-form
    `Other: federal Form ___, Schedule ___`.
    L8 (self-employment earnings paid to the single member) carries the SAME
    loss limit and the SAME Schedule K Line 3 add-back as J1 L6.
    """
    l7 = (_f(l1_sch_c_l31) + _f(l2_sch_d) + _f(l3_sch_e) + _f(l4_sch_f_l34)
          + _f(l5_form_4797) + _f(l6_other))
    return l7, l7 - _f(l8_self_employment)


def _tn_j3_total(l1_ordinary_1120s_l22, l2_s_status_income,
                 l4_s_status_expense, l5_loss_asset_sold_12mo):
    """Schedule J3 — Entities Treated as Subchapter S Corporations (federal 1120S).
    Returns (L3 additions, L6 deductions, L7 total → Sch. J L1).

    L1 = 1120-S Line 22 `Ordinary business income (loss)` · L2 = Sch. K Lines
    2-10 `Income items to extent includable in federal income were it not for
    "S" status election` (§179-disposition gain at box 17 code K, same
    entity-level pro-forma rule, shareholder-level §179 limits disregarded) ·
    **L3 = L1+L2** · L4 = Sch. K Lines 11-12e · L5 12-month distribution loss ·
    **L6 = L4+L5** · **L7 = L3 - L6**.

    ══════════════════════════════════════════════════════════════════════════
    ⚠⚠ **THE CLONE TRAP — READ THIS BEFORE TOUCHING THIS FUNCTION.**
    **J3 HAS ONLY TWO DEDUCTION LINES: L4 AND L5.**
    **J3 HAS NO SELF-EMPLOYMENT DEDUCTION AND NO QUALIFIED-PLAN DEDUCTION.**
    J1 gets L6 (self-employment) and L7 (pension) OUT of its base; an S corp
    gets NOTHING equivalent, because a shareholder's wages are already inside
    1120-S Line 22. Tennessee therefore taxes the S corp on essentially its
    full federal K-1 economics.

    This is the SINGLE LARGEST entity-choice-driven difference in the Tennessee
    excise base, and the easiest thing in this spec to get wrong. CLONING J1
    INTO J3 OVERSTATES THE S-CORP DEDUCTION and understates tax at 6.5% of the
    SE + pension figures. Confirmed on the form face AND in the line-by-line
    instructions by the adversarial pass (verification item 3).

    The signature of this function deliberately has NO se/pension parameters so
    the mistake cannot be made silently. Diagnostic: D_TN170_J3_NO_SE_PENSION.
    ══════════════════════════════════════════════════════════════════════════
    """
    l3 = _f(l1_ordinary_1120s_l22) + _f(l2_s_status_income)
    l6 = _f(l4_s_status_expense) + _f(l5_loss_asset_sold_12mo)
    return l3, l6, l3 - l6


def _tn_j4_total(l1_1120_l28, l2a_reit_l21, l2b_reit_dividends_l22b, l3_ubti_990t_l5,
                 l4_other, l5_contribution_carryover_used, l6_capital_gains_offset,
                 l8_contributions_excess, l9_current_capital_loss):
    """Schedule J4 — Entities Treated as Corporations and Other Entities (1120).
    Returns (L2c, L7 additions, L10 deductions, L11 total → Sch. J L1).

    L1 = 1120 Line 28 `Taxable income before net operating loss deduction and
    special deductions` · L2a/L2b/L2c the REIT block (1120-REIT L21 / L22b;
    **L2c = L2a - L2b**) · L3 = 990-T Line 5 UBTI · L4 free-form other ·
    **L7 = L1+L2c+L3+L4+L5+L6** · **L10 = L8+L9** · **L11 = L7 - L10**.

    ⚠ **LINES 5/6/8/9 ARE A FULL CONTRIBUTIONS-AND-CAPITAL-LOSS TIMING
    DECOUPLING** — a SECOND Tennessee-basis ledger, entirely distinct from the
    depreciation one:
      L5 `Contribution carryover from prior period(s)` — `must be added back to
         net income when used for federal tax purposes`
      L6 `Capital gains offset by capital loss carryover or carryback` — `must
         be added to net income when offset against capital gains`
      L8 `Contributions in excess of amount allowed by federal government` —
         `may be deducted, in full, in the year in which the contributions were
         made`
      L9 `Portion of current year's capital loss not included in federal taxable
         income` — `may be deducted, in full, in the year the loss was incurred`
    Tennessee allows charitable contributions and capital losses IN FULL IN THE
    YEAR INCURRED and therefore REVERSES every federal carryover/carryback when
    the federal return uses it. The app must carry a SEPARATE TENNESSEE
    contribution and capital-loss HISTORY per C-corp.

    ⚠ J4 IS ALSO THE NONPROFIT PATH: a 501(c) with unrelated business taxable
    income files FAE170 with Form 990-T Line 5 on J4 Line 3.
    ⚠ TN is a SEPARATE-ENTITY state: a member of a federal consolidated group
    must build a PRO FORMA Form 1120 (and may use the Excise Tax Interest
    Expense Worksheet for its share of the group's interest deduction).
    """
    l2c = _f(l2a_reit_l21) - _f(l2b_reit_dividends_l22b)
    l7 = (_f(l1_1120_l28) + l2c + _f(l3_ubti_990t_l5) + _f(l4_other)
          + _f(l5_contribution_carryover_used) + _f(l6_capital_gains_offset))
    l10 = _f(l8_contributions_excess) + _f(l9_current_capital_loss)
    return l2c, l7, l10, l7 - l10


def _tn_schedule_j(l1_from_entry_point, additions_l2_l14, deductions_l16_l29_excl_28b,
                   l33_optional_addback, l35_ratio, l37_nonbusiness_tn, l38_nol,
                   year=2025):
    """Schedule J L31-L39 — **THE ORDERING IS LOAD-BEARING.**

    ══════════════════════════════════════════════════════════════════════════
    ⚠⚠ **APPORTION-FIRST IS WRONG.** Confirmed by the adversarial pass
    (verification item 4) against the form face p. 5 and instructions pp. 9-10.
    The three steps happen at three DIFFERENT points in the flow:

      1. **$50,000 standard deduction — PRE-APPORTIONMENT** (L32, applied inside
         L34, before the ratio is ever touched).
      2. **Nonbusiness allocation — POST-APPORTIONMENT** (L37, added after L36;
         allocated, not apportioned, and taxed at the full 6.5%).
      3. **NOL — LAST** (L38, subtracted after both).

    Any spec that apportions first will be wrong on every multistate return.
    ══════════════════════════════════════════════════════════════════════════

    L15 = additions L2-L14 · **L30 = deductions L16-L29 EXCLUDING L28b**
    (`Line 28b is informational only`) ·
    **L31** `Total business income (loss) (add Lines 1 and 15, subtract Line 30;
    if loss, enter on Schedule K, Line 1)` ·
    **L32** `Excise tax standard deduction (enter the lesser of Line 31 or
    $50,000; if negative, enter zero)` — cannot create/increase a loss, no
    carryforward, ONE per return; the unused portion spills to Schedule M L10 ·
    **L33** optional deduction addback (PC 343 (2025), § 67-4-2006(c)(10)) —
    taxpayer-elective and may be `made, adjusted, or removed at the taxpayer's
    discretion for any tax year on any timely filed original or amended return` ·
    **L34 = L31 - L32 + L33** · L35 ratio · **L36 = L34 x L35** ·
    **L37** nonbusiness earnings directly allocated to TN (Sch. M L11) ·
    **L38** loss carryover from Schedule U (15-year, oldest first, computed
    SEPARATELY from federal) · **L39 = L36 + L37 - L38** → Sch. B L4.
    """
    l31 = _f(l1_from_entry_point) + _f(additions_l2_l14) - _f(deductions_l16_l29_excl_28b)
    l32 = max(0.0, min(l31, float(_yk(TN_EXCISE_STANDARD_DEDUCTION, year))))
    l34 = l31 - l32 + _f(l33_optional_addback)
    l36 = l34 * _f(l35_ratio)
    l39 = l36 + _f(l37_nonbusiness_tn) - _f(l38_nol)
    return {"L31": l31, "L32": l32, "L34": l34, "L36": l36,
            "L37": _f(l37_nonbusiness_tn), "L38": _f(l38_nol), "L39": l39}


def _tn_schedule_m_spillover(m_l9_net_nonbusiness, j_l32_standard_deduction, year=2025):
    """Schedule M L10, verbatim: `Excise tax standard deduction (Enter $50,000
    less amount reported on Schedule J, Line 32; cannot exceed Line 9)`.

    The UNUSED standard deduction offsets directly-allocated nonbusiness
    earnings. Capped at the lesser of Sch. M L9 or $50,000. NEVER negative.
    Returns (L10, L11) where L11 = L9 - L10 → Sch. J L37.

    Default expense assumptions where not substantiated (Tenn. Comp. R. & Regs.
    1320-06-01-.23(3)): 50% of nonbusiness RENTAL earnings, 5% of OTHER
    nonbusiness earnings. The manual notes income meeting the statutory
    nonbusiness definition is uncommon.
    """
    l9 = _f(m_l9_net_nonbusiness)
    l10 = max(0.0, min(float(_yk(TN_EXCISE_STANDARD_DEDUCTION, year)) - _f(j_l32_standard_deduction), l9))
    return l10, l9 - l10


def _tn_schedule_k_loss_carryover(j_l31, j_l18_dividends, j_l22_nonbusiness,
                                  j_l33_optional_addback, j1_l6_l7_or_j2_l8, ratio):
    """Schedule K — Determination of Loss Carryover Available.

    ⚠ **THE NOL IS NOT SIMPLY SCHEDULE J LINE 31.** Schedule K REVERSES FOUR
    specific deductions before apportioning:
      L1 net loss from Sch. J L31 ·
      L2 `Amounts reported on Schedule J, Lines 18, 22, and 33` (80%-owned
         dividends, nonbusiness earnings, the optional addback) ·
      L3 `Amounts reported on Schedule J1, Lines 6 and 7, or Schedule J2,
         Line 8` (the SE / qualified-plan deductions) ·
      L4 `Reduced loss (add Lines 1 through 3; **if net amount is positive,
         enter zero**)` · L5 ratio · **L6 = L4 x L5**.

    Manual p. 298: `These reversals (add-backs) should never turn an apportioned
    business loss ... into income.` Discharge-of-indebtedness reduction under
    § 67-4-2006(c)(8) applies to the carryover for bankruptcy discharges on or
    after 10/1/2013.
    """
    l4 = (_f(j_l31) + _f(j_l18_dividends) + _f(j_l22_nonbusiness)
          + _f(j_l33_optional_addback) + _f(j1_l6_l7_or_j2_l8))
    if l4 > 0:
        l4 = 0.0
    return l4, l4 * _f(ratio)


def _tn_sales_factor(tn_receipts, everywhere_receipts):
    """Schedule N — Apportionment, Standard.

    ⚠ **THE ENTIRE SCHEDULE IS ONE LINE on the TY2025 form**: `1. Sales factor
    (business gross receipts) (Enter franchise tax apportionment ratio on
    Schedule F1, Line 4. Enter excise tax apportionment ratio on Schedule J,
    Line 35.)` — columns `In Tennessee` | `Total Everywhere` | `Ratio %`.

    There is **NO property line, NO payroll line, and NO 11x/13 divisor anywhere
    on the TY2025 form**. The 11x/13 formula lives on the TY2024 form; a fiscal
    filer ending 6/30/2025 began 7/1/2024 and files TY2024, so it is not a
    TY2025 form-year concern. (⚠ U3: a SHORT period beginning on/after 1/1/2025
    and ending before 12/31/2025 statutorily falls in the 11x/13 row that this
    form cannot express — unresolved DOR edge case, D_TN170_SHORT_PERIOD_APPT.)

    **ONE RATIO SERVES BOTH TAXES** — the same percentage goes to F1 L4
    (franchise) and J L35 (excise). Contrast Schedule N1, which produces TWO
    different ratios (franchise via L14, excise via L13) — RED-deferred (W6).

    No throwback and no throwout. Destination sourcing for TPP; market-based
    sourcing for other-than-TPP (RMA 2015, periods beginning on/after 7/1/2016).
    A zero everywhere-denominator falls back to the form's `or 100%`.
    """
    everywhere = _f(everywhere_receipts)
    if everywhere <= 0:
        return 1.0
    return _f(tn_receipts) / everywhere


def _tn_credit_allowed(total_credits_sch_d_l10, sch_c_l8, green_energy_credit=0.0):
    """Schedule C L9 — `Total credit from Schedule D, Line 10 (cannot exceed
    Schedule C, Line 8)`.

    ⚠ THE CAP HAS EXACTLY ONE HOLE. Sch. D L10 instruction: `Total credits may
    not exceed the amount on Schedule C, Line 8, **unless claiming a Green
    Energy Credit** under the provisions of Tenn. Code Ann. § 67-4-2109(m).`
    Encoded as: non-green credits capped at L8; the Green Energy Credit rides
    on top uncapped. ⚠ That split is the SPEC'S READING of a terse sentence —
    the DOR does not spell out the mechanics. Flag with W8.
    """
    green = _f(green_energy_credit)
    non_green = max(0.0, _f(total_credits_sch_d_l10) - green)
    return min(non_green, max(0.0, _f(sch_c_l8))) + green


def _tn_schedule_c(sch_a_l3_franchise, sch_b_l7_excise, total_credits,
                   total_payments, penalty_and_interest=0.0, green_energy_credit=0.0):
    """Schedule C — Total Tax Due or Overpayment. Returns a dict L8..L16.

    L8 = L3 + L7 · L9 credits (capped, green-energy exception) · **L10 = L8 - L9,
    floored at zero** (`if Line 9 exceeds Line 8, enter zero here`) ·
    L11 payments (Sch. E L7) · L12-L15 penalty and interest ·
    L16 = L10 + L12 + L13 + L14 + L15 - L11, then the election boxes
    `A. Credit to next year's tax` / `B. Refund`.

    ⚠ **U8 / W8 — UNRESOLVED AND LEFT AS THE FORM'S ARITHMETIC.** Because L9 is
    capped only at `cannot exceed Schedule C, Line 8` and L10 floors at ZERO, a
    large credit reduces net tax to zero — **the $100 franchise minimum
    included**. No DOR statement was found either way. The spec follows the
    form's arithmetic; **Ken must bless this rather than the spec assuming it.**
    Diagnostic: D_TN170_MIN_TAX_VS_CREDITS.
    """
    l8 = _f(sch_a_l3_franchise) + _f(sch_b_l7_excise)
    l9 = _tn_credit_allowed(total_credits, l8, green_energy_credit)
    l10 = max(0.0, l8 - l9)
    l16 = l10 + _f(penalty_and_interest) - _f(total_payments)
    return {"L8": l8, "L9": l9, "L10": l10, "L11": _f(total_payments), "L16": l16,
            "refund": max(0.0, -l16), "amount_due": max(0.0, l16)}


def _tn_schedule_t_part1(purchase_price, rate, schedule_v_carryover,
                         sch_a_l3, sch_b_l5, sch_d_l1_l4_and_l7, year=2025):
    """Schedule T Part 1 — Industrial Machinery / R&D Equipment Credit.

    L1 purchase price · L2 `Percentage allowed (generally 1%*)` · L3 = L1 x L2 ·
    L4 carryover from Schedule V · L5 = L3 + L4 · **L6 = `franchise and excise
    tax liability before any credits (add Schedule A, Line 3 and Schedule B,
    Line 5)`** · **L7 = 50% of L6** · L8 = L6 · L9 = Sch. D Lines 1-4 and
    Line 7 · L10 = L8 - L9 · **L11 = the SMALLEST of L5, L7, L10** → Sch. D L5.

    Enhanced rates by approved capital investment (§ 67-4-2009(3)(I)):
    $100M → 3%, $250M → 5%, $500M → 7%, $1B → 10%. Carryforward 25 years
    (Schedule V — printed with 18 rows against a 25-year carryforward; a
    data-capture note, not a defect). Part 2 recapture is RED-deferred (R9).

    ⚠ Note L6 uses Sch. B **Line 5**, not Line 7 — recapture is excluded.
    """
    l3 = _f(purchase_price) * float(rate if rate is not None else _yk(TN_IM_CREDIT_BASE_RATE, year))
    l5 = l3 + _f(schedule_v_carryover)
    l6 = _f(sch_a_l3) + _f(sch_b_l5)
    l7 = l6 * float(_yk(TN_IM_CREDIT_LIMIT_PCT, year))
    l10 = l6 - _f(sch_d_l1_l4_and_l7)
    return min(l5, l7, l10)


def _tn_schedule_g_total(owned_subtotal_l10, rent_real, rent_mfg_machinery,
                         rent_furniture_office, rent_delivery_mobile, year=2025):
    """Schedule G L15 — the property measure (**opt-in only**) → Sch. A L2.

    Owned property (L1-L9 → L10 subtotal) is at **GAAP net book value, cost less
    accumulated depreciation, in Tennessee**; L10 = `add Lines 1 through 7a,
    subtract Lines 7b through 9`. Rented property L11-L14 = net annual rental x
    the statutory multiple, **printed on the current form face**:
      L11 real property **x8** · L12 machinery and equipment used in
      manufacturing and processing **x3** · L13 furniture, office machinery and
      equipment **x2** · L14 delivery or mobile equipment **x1**.
    **L15 = add Lines 10 through 14.**

    Net annual rental = gross annual rent PAID less gross rent RECEIVED for
    sub-rental, **floored at zero** (never negative); sub-rental requires the
    same property and the same rights. Rents are ANNUALIZED for short periods
    before the multiple is applied. Finance leases → owned asset at net book
    value; operating leases → rent x multiple.

    ⚠ **RED-DEFERRED IN v1 (R1/W4).** PC 950 (2024) eliminated the property
    measure as a MANDATORY base for periods ending on/after 1/1/2024; it
    survives ONLY as an ANNUAL OPT-IN election under § 67-4-2123, valid only
    where ALL THREE hold: the net-worth base is LOWER than the § 67-4-2108
    minimum base; the election RESULTS IN A HIGHER TAX; and the taxpayer WAIVES
    any claim that the minimum base is unconstitutional for failing the internal
    consistency test. The election form carries a SEPARATE SECOND SIGNATURE
    BLOCK for that waiver and is submitted through TNTAP, not with the return.
    Purpose: let taxpayers with large F&E credit carryforwards generate enough
    liability to use them.
    This helper exists so Sch. A L3's greater-of is arithmetically right the day
    Schedule G lands; v1 takes L15 as DIRECT ENTRY on Sch. A L2.
    """
    m = _yk(TN_SCHED_G_RENT_MULTIPLES, year)
    return (_f(owned_subtotal_l10)
            + max(0.0, _f(rent_real)) * m["real_property"]
            + max(0.0, _f(rent_mfg_machinery)) * m["mfg_machinery_equipment"]
            + max(0.0, _f(rent_furniture_office)) * m["furniture_office_equipment"]
            + max(0.0, _f(rent_delivery_mobile)) * m["delivery_mobile_equipment"])


def _tn_tcja_bonus_pct(key_year, year=2025):
    """Tennessee's FROZEN TCJA §168(k) applicable percentage for `key_year`.

    ══════════════════════════════════════════════════════════════════════════
    ⚠⚠ **W1 / U2 — THIS HELPER DOES NOT AND WILL NOT PICK THE KEY.**
    The DOR contradicts itself INSIDE ONE MANUAL:
      • p. 225 phase-down table caption: `Asset Acquired Between:`
      • p. 224 narrative: `assets **acquired** ... before January 1, 2023`
      • p. 267 narrative: `the 40%, 20%, and 0% applicable percentages will
        apply for excise tax purposes to qualified property **placed in
        service** in 2025, 2026, and 2027 and after`
      • the form face and instructions say `purchased`
    Worse, p. 267 keys the FEDERAL OBBBA rule to property `acquired` after
    January 19, 2025 while keying TENNESSEE's 40/20/0 to property `placed in
    service` — BOTH KEYS INSIDE A SINGLE SENTENCE.

    These diverge for an asset ACQUIRED IN 2024 AND PLACED IN SERVICE IN 2025
    (60% vs 40%), which is a common pattern and not an edge case, and the keying
    ALSO decides which of the two regimes an asset falls into.

    **THIS CHANGES NUMBERS ON REAL RETURNS.** It is ESCALATED to Ken as
    GATE1_WALK.md item 3 and walk item W1 here. The CALLER must supply
    `key_year` from the date field Ken's ruling names. Nothing in this spec
    derives `key_year` on its own, and no computed FormRule calls this helper.
    The PERCENTAGES below are verified; only the KEY is open.
    ══════════════════════════════════════════════════════════════════════════

    ⚠ Also note the OBBBA consequences that are NOT open:
      • OBBBA 100% bonus is **NOT available in Tennessee for TY2025**. A TY2025
        asset generating 100% federally against TN's 40% produces a 60-POINT
        ADD-BACK plus ongoing MACRS recovery of the differential.
      • **§168(n) qualified production property gets ZERO TN bonus** — `Because
        IRC § 168(n) does not exist in the TCJA version of IRC § 168, this OBBBA
        provision is not applicable for Tennessee excise tax purposes` —
        depreciate as MACRS nonresidential real property.
      • §179 CONFORMS at the full OBBBA $2.5M/$4M. The two OBBBA depreciation
        provisions split in OPPOSITE directions.
    """
    if key_year is None:
        return None
    for lo, hi, pct in _yk(TN_TCJA_BONUS_PHASEDOWN, year):
        if lo <= int(key_year) <= hi:
            return float(pct)
    return None


def _tn_estimate_required(prior_year_liability_after_credits,
                          current_year_liability_after_credits, year=2025):
    """Estimated payments are required when the combined franchise and excise
    liability AFTER CREDITS is `$5,000 or more for BOTH the prior tax year and
    the current tax year`. A short PRIOR period is ANNUALIZED for the test; the
    current year is NOT. (Manual p. 108.)"""
    t = float(_yk(TN_ESTIMATE_THRESHOLD, year))
    return _f(prior_year_liability_after_credits) >= t and _f(current_year_liability_after_credits) >= t


def _tn_installment_standard(prior_year_liability, projected_current_liability, year=2025):
    """Standard-method installment (manual p. 109) — each installment is the
    LESSER of `25% of the prior year's total liability (annualized if the tax
    period was less than 12 months)` or `25% of 80% of the projected current
    year's liability`. The annualized income installment method (checkbox f) is
    RED-deferred (R11)."""
    return min(_f(prior_year_liability) * float(_yk(TN_ESTIMATE_PRIOR_PCT, year)),
               _f(projected_current_liability) * float(_yk(TN_ESTIMATE_CURRENT_PCT, year)))


def _tn_extension_payment_required(current_year_liability, prior_year_liability, year=2025):
    """FAE173 — seven months. Granted provided that BY THE ORIGINAL DUE DATE the
    taxpayer has requested the extension and remitted the LESSER of 90% of the
    current year's liability or 100% of the prior year's (annualized if the
    prior year was short). **`If the taxpayer had a zero tax liability for the
    prior tax year, then the required extension payment is $100.`**

    If sufficient payments are already in, the extension is AUTOMATIC and no
    form is required. `The filing extension is not a payment extension` —
    interest runs from the ORIGINAL due date. Missing the payment threshold or
    the extended due date VOIDS the extension retroactively.
    """
    if _f(prior_year_liability) <= 0:
        return float(_yk(TN_EXTENSION_PRIOR_ZERO_PAYMENT, year))
    return min(_f(current_year_liability) * float(_yk(TN_EXTENSION_CURRENT_PCT, year)),
               _f(prior_year_liability) * float(_yk(TN_EXTENSION_PRIOR_PCT, year)))


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY TOPICS / SOURCES
# ═══════════════════════════════════════════════════════════════════════════

AUTHORITY_TOPICS: list[tuple[str, str]] = [
    ("tn_franchise_excise",
     "Tennessee franchise & excise tax (FAE170): ONE return, TWO taxes -- 0.25% franchise on net "
     "worth (minimum $100) and 6.5% excise on Schedule J net earnings, with four entity-branching "
     "entry schedules J1/J2/J3/J4 converging on a single Schedule J."),
    ("tn_bonus_depreciation",
     "Tennessee IRC 168(k) decoupling: bonus FULLY disallowed for assets purchased on or before "
     "12/31/2022; TCJA percentages permanently frozen for later assets; OBBBA 100% bonus NOT "
     "available for TY2025 while 179 conforms at $2.5M/$4M."),
    ("tn_property_measure",
     "Tennessee franchise tax property measure (Schedule G): repealed as a MANDATORY base by Public "
     "Chapter 950 (2024), surviving only as an ANNUAL OPT-IN election under Tenn. Code Ann. "
     "67-4-2123 with a constitutional-waiver signature."),
]

# ⚠ TN_TCA_67_4_2004_IRC_DEF is the Tier-1 conformity ANCHOR authored in
# `_state_conformity_tier1.py`. It is currently GATED and UNSEEDED, so this
# loader WILL print `existing source TN_TCA_67_4_2004_IRC_DEF NOT FOUND -- links
# to it will be skipped` until the Tier-1 conformity batch seeds.
# **THAT WARNING IS EXPECTED AND CORRECT.** Do not "fix" it by re-authoring the
# source here — one truth per fact; the conformity anchor has exactly one home.
EXISTING_SOURCES_TO_REFERENCE: list[str] = [
    "TN_TCA_67_4_2004_IRC_DEF",   # rolling IRC conformity + the TCJA 168(k) lock (Tier-1 anchor)
    "IRS_2025_1065_INSTR",        # Sch. J1 L1 = 1065 Line 23; Sch. K Lines 2-11 / 12-13a-e
    "IRS_2025_1120S_INSTR_FULL",  # Sch. J3 L1 = 1120-S Line 22; Sch. K Lines 2-10 / 11-12e
    "IRS_2025_4562_INSTR",        # federal bonus at Form 4562 Part II L14 and Part V L25
]

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "TN_2025_FAE170_FORM",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "TN",
        "title": "2025 Tennessee Form FAE170 — Franchise and Excise Tax Return",
        "citation": "Form FAE170 (2025), rev. RV-R0011001 (9/25), 10 pp., /ModDate 2025-12-31 (md5 476a5392db72c1dc466d446835540f4e)",
        "issuer": "Tennessee Department of Revenue",
        "official_url": "https://www.tn.gov/content/dam/tn/revenue/documents/forms/fae/FAE170_2025.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.6,
        "topics": ["tn_franchise_excise", "tn_bonus_depreciation"],
        "excerpts": [
            {
                "excerpt_label": "Schedules A/B/C face (verbatim) — the two taxes and the total",
                "excerpt_text": (
                    "SCHEDULE A: 1 'Total net worth Schedule F1, Line 5 or Schedule F2, Line 3'; 2 "
                    "'Taxpayer electing to calculate franchise tax based on property measure - enter total "
                    "from Schedule G Line 15. All other taxpayers - leave blank'; 3 'Franchise tax (25c per "
                    "$100 or major fraction thereof on the greater of Lines 1 or 2; minimum $100)'. "
                    "SCHEDULE B: 4 'Income subject to excise tax from Schedule J, Line 39'; 5 'Excise tax "
                    "(6.5% of Line 4)' [instruction: 'If Line 4 is a loss, enter zero.']; 6 'Recapture of "
                    "tax credit (Schedule T, Line 13) and additional excise tax on certified distribution "
                    "sales'; 7 'Total excise tax due (add Lines 5 and 6)'. SCHEDULE C: 8 'Total franchise "
                    "and excise taxes (add Lines 3 and 7)'; 9 'Total credit from Schedule D, Line 10 "
                    "(cannot exceed Schedule C, Line 8)'; 10 'Net tax (subtract Line 9 from Line 8; if Line "
                    "9 exceeds Line 8, enter zero here)'; 11 'Total payments from Schedule E, Line 7'; "
                    "12-15 penalty and interest; 16 'Total amount due (overpaid) (add Lines 10, 12, 13, 14, "
                    "and 15, subtract Line 11)' with election boxes A credit-forward / B refund."
                ),
                "summary_text": "Sch. A L3 = MAX(L1,L2) x 25c/$100 major-fraction, $100 min. Sch. B L5 = 6.5% of Sch. J L39, zero on a loss. Sch. C L8 = A3+B7; L9 credits capped at L8; L10 floored at zero.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Schedule J1 vs J3 — THE CLONE TRAP (verbatim deduction lines)",
                "excerpt_text": (
                    "SCHEDULE J1 (partnerships, federal 1065) deductions: 5 'Expense items specifically "
                    "allocated to partners not deducted elsewhere'; 6 'Amount subject to self-employment "
                    "taxes distributable or paid to each partner or member net of any pass-through expense "
                    "deducted elsewhere on this return (if negative, enter zero) (include on Schedule K, "
                    "Line 3)'; 7 'Amount of contribution to qualified pension or benefit plans of any "
                    "partner or member, including all IRC 401 plans (include on Schedule K, Line 3)'; 8 REIT "
                    "gain; 9 12-month distribution loss; 10 total; 11 'Total (subtract Line 10 from Line 4; "
                    "enter here and on Schedule J, Line 1)'. SCHEDULE J3 (S corps, federal 1120S) "
                    "deductions -- THE COMPLETE LIST: 4 'Expense items to extent includable in federal "
                    "expenses were it not for \"S\" status election'; 5 'Any loss on the sale of an asset "
                    "sold within 12 months after the date of distribution'; 6 'Total deductions (add Lines 4 "
                    "and 5)'; 7 'Total (subtract Line 6 from Line 3; enter here and on Schedule J, Line 1)'. "
                    "J3 HAS NO SELF-EMPLOYMENT LINE AND NO QUALIFIED-PLAN LINE."
                ),
                "summary_text": "J1 carries L6 (self-employment) and L7 (qualified pension); J3 has NEITHER -- its only deductions are L4 and L5. Cloning J1 into J3 overstates the S-corp deduction.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Schedule J L31-L39 — the ordering (verbatim)",
                "excerpt_text": (
                    "31 'Total business income (loss) (add Lines 1 and 15, subtract Line 30; if loss, enter "
                    "on Schedule K, Line 1)'; 32 'Excise tax standard deduction (enter the lesser of Line 31 "
                    "or $50,000; if negative, enter zero)'; 33 'Excise tax optional deduction addback (see "
                    "instructions; attach schedule)'; 34 'Adjusted total business income (loss) (subtract "
                    "Line 32 from 31, add Line 33)'; 35 'Excise tax apportionment ratio (Schedules N, N1, O, "
                    "P, or R if applicable or 100%)'; 36 'Apportioned business income (loss) (multiply Line "
                    "34 by Line 35)'; 37 'Nonbusiness earnings directly allocated to Tennessee (from "
                    "Schedule M, Line 11)'; 38 'Loss carryover from prior years (from Schedule U)'; 39 "
                    "'Subject to excise tax (add Line 36 and 37, subtract Line 38; enter here and on "
                    "Schedule B, Line 4)'. Line 30: 'Total deductions (add Lines 16 through 29, excluding "
                    "28b)'. Line 28b is informational only."
                ),
                "summary_text": "$50,000 standard deduction is PRE-apportionment (L32, inside L34); nonbusiness allocation is POST-apportionment (L37); NOL is LAST (L38). Apportion-first is wrong.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Schedule J4 Lines 5/6/8/9 — the contributions and capital-loss decoupling",
                "excerpt_text": (
                    "5 'Contribution carryover from prior period(s)' -- instruction: contribution carryovers "
                    "'must be added back to net income when used for federal tax purposes'. 6 'Capital gains "
                    "offset by capital loss carryover or carryback' -- 'must be added to net income when "
                    "offset against capital gains'. 8 'Contributions in excess of amount allowed by federal "
                    "government' -- 'may be deducted, in full, in the year in which the contributions were "
                    "made'. 9 \"Portion of current year's capital loss not included in federal taxable "
                    "income\" -- 'may be deducted, in full, in the year the loss was incurred'. "
                    "Also J4: 1 = federal Form 1120 Line 28; 2a/2b/2c the 1120-REIT block (Lines 21 / 22b); "
                    "3 = Form 990-T Line 5 unrelated business taxable income."
                ),
                "summary_text": "TN allows contributions and capital losses IN FULL in the year incurred and reverses every federal carryover/carryback -- a separate TN contribution and capital-loss history per C-corp.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Schedule N — single sales factor, ONE line on the TY2025 form",
                "excerpt_text": (
                    "'1. Sales factor (business gross receipts) (Enter franchise tax apportionment ratio on "
                    "Schedule F1, Line 4. Enter excise tax apportionment ratio on Schedule J, Line 35.)' -- "
                    "columns 'In Tennessee' | 'Total Everywhere' | 'Ratio %'. There is NO property line, NO "
                    "payroll line and NO 11x/13 divisor anywhere on the TY2025 form; the 11x/13 formula "
                    "lives on the TY2024 form. Schedule N1 (elective three-factor / Telecom Qualified "
                    "Member) separately prints 'c. Franchise Ratio' and 'd. Excise Ratio' columns and "
                    "produces TWO different ratios (franchise via L14, excise via L13)."
                ),
                "summary_text": "TY2025 Schedule N is a single sales factor on one line; the same ratio serves BOTH the franchise (F1 L4) and excise (J L35) taxes.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Return-level checkboxes (a)-(i) — branching",
                "excerpt_text": (
                    "a) Amended return; b) Final return; c) Public Law 86-272 applied to excise tax; "
                    "d) Taxpayer has made an election to calculate net worth per Tenn. Code Ann. "
                    "67-4-2103(g)-(i); e) filed the prescribed form to revoke its election; f) Annualized "
                    "income installment method for quarterly estimates election; g) Taxpayer has filed for "
                    "federal extension; h) Three-factor apportionment election; i) Telecom Qualified Member. "
                    "Plus 'Date Tennessee operations began'."
                ),
                "summary_text": "Nine checkboxes drive branching; (c) P.L. 86-272 kills excise only and still requires the franchise schedules; (d)/(e) consolidated net worth; (h)/(i) route to Schedule N1.",
                "is_key_excerpt": False,
            },
        ],
    },
    {
        "source_code": "TN_2025_FAE170_INSTR",
        "source_type": "state_instruction",
        "source_rank": "primary_official",
        "jurisdiction_code": "TN",
        "title": "2025 Instructions for Tennessee Franchise and Excise Tax Return (FAE170)",
        "citation": "2025 FAE170 Instructions, 15 pp., /ModDate 2025-12-31",
        "issuer": "Tennessee Department of Revenue",
        "official_url": "https://www.tn.gov/content/dam/tn/revenue/documents/forms/fae/fae170instructions2025.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["tn_franchise_excise", "tn_bonus_depreciation", "tn_property_measure"],
        "excerpts": [
            {
                "excerpt_label": "Schedule J Line 1 — the four entry points (verbatim)",
                "excerpt_text": (
                    "'Enter the applicable amount from line 11, 9, 7, or 11 of Schedule J1, J2, J3, or J4, "
                    "respectively.' J1 totals at Line 11 (partnerships, federal Form 1065 Line 23); J2 at "
                    "Line 9 (single member LLC filing as an individual, federal Form 1040 Schedules C/D/E/F "
                    "and Form 4797); J3 at Line 7 (S corporations, federal Form 1120S Line 22); J4 at Line "
                    "11 (corporations and other entities, federal Form 1120 Line 28). The mapping closes."
                ),
                "summary_text": "One Schedule J serves four entity-branching entry schedules; J1 L11, J2 L9, J3 L7, J4 L11 all feed Schedule J Line 1.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Schedule A Lines 2-3 — the elective property measure and the greater-of",
                "excerpt_text": (
                    "Line 2: 'This line is no longer mandatory. Taxpayers who elect to calculate franchise "
                    "tax based on the property measure: enter total from Schedule G, Line 15. If not elected "
                    "leave this line blank.' Line 3: 'Multiply the greater of Line 1 or 2 by $0.25 per $100 "
                    "or major fraction thereof. The minimum tax is $100. Franchise tax may be prorated on "
                    "short period returns, but not below the $100 minimum... The franchise tax may not be "
                    "prorated on returns filed by 52/53 week filers.' Head of Schedule A: 'Round to the "
                    "nearest dollar'."
                ),
                "summary_text": "Sch. A L3 is a LIVE greater-of even though Schedule G is opt-in; $100 minimum survives proration; no proration at all for 52/53-week filers.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Schedule J1 §179 pro-forma disposition rule (verbatim)",
                "excerpt_text": (
                    "'The gain included on Sch. J1, Line 2 should be computed on a pro forma basis at the "
                    "partnership level and any Section 179 expense limits that would have been imposed for "
                    "federal income tax purposes at the partner level should be disregarded.' Identical "
                    "language on Line 5 for losses, and on Schedule J3 Lines 2 and 4 at the S-corp level. "
                    "The disposition is reported federally at Form 1065 Sch. K box 20 code L or Form 1120S "
                    "Sch. K box 17 code K, not on Form 4797. Schedule J1 Line 6 is taken net of pass-through "
                    "expense deducted elsewhere on the return, 'such as IRC Section 179 expenses and "
                    "contributions deducted on Line 5'. Lines 6 and 7: 'This deduction cannot create or "
                    "increase a loss carryover.'"
                ),
                "summary_text": "J1/J3 §179 disposition gain/loss is recomputed PRO FORMA at the entity level with partner/shareholder §179 limits disregarded -- no federal analogue.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Schedule J deduction detail — L19 75%, L28a/28b, L30 exclusion",
                "excerpt_text": (
                    "Line 19 (form label omits the percentage): 'Enter 75% of donations' to qualified public "
                    "school support groups and nonprofit organizations (67-4-2006(b)(2)(M) and (P)); "
                    "certification form required. Line 28a 'Business interest expense currently deductible' "
                    "= pro forma Form 8990 Lines 1 and 4 plus 2018/2019 carryforwards, plus a partner's "
                    "share of excess business interest from Form 8990 Sch. A Line 43 column (c) where the "
                    "partnership does not file F&E, EXCLUDING disqualified interest disallowed on Form 8926 "
                    "under pre-TCJA 163(j). Line 28b 'Business interest expense carryforward available for "
                    "future tax years' -- 'Line 28b is informational only.' Line 30: 'Add Lines 16 through "
                    "29, excluding Line 28b.' Line 20: 'Do not deduct Paid Family and Medical Leave for "
                    "which a credit was claimed on Schedule PL of this return.'"
                ),
                "summary_text": "L19 is 75% of donations though the label omits it; L28b is informational and EXCLUDED from the L30 total; L28a is the business-interest deduction (not L27a -- see the erratum).",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Line 13 cross-reference ERRATUM (U4)",
                "excerpt_text": (
                    "The Schedule J Line 13 instruction closes: 'Note: the business interest expense "
                    "deduction for excise tax purposes is reported on Sch. J, Line 27a.' THERE IS NO LINE "
                    "27a ON THE FORM. Line 27 is IRC 951A global intangible low-taxed income; the "
                    "business-interest deduction is Line 28a on both the form face and the Line 28a "
                    "instruction. Stale cross-reference -- BUILD TO 28a."
                ),
                "summary_text": "U4 erratum: the L13 instruction points at a nonexistent 'Line 27a'; the business-interest deduction is L28a. Recorded so a future reader does not 'fix' it back.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Filing modes — inactive entity and P.L. 86-272",
                "excerpt_text": (
                    "'A taxable entity that is incorporated, domesticated, qualified or otherwise registered "
                    "to do business in Tennessee that was inactive in Tennessee for the entire taxable "
                    "period and owes only the minimum tax may file only page one of this return and omit the "
                    "remaining pages.' Checkbox (c): 'Check this box to claim the protections afforded by "
                    "P.L. 86-272 and file only the franchise tax schedules.' Checkbox (h) requires BOTH 'The "
                    "election must result in a higher apportionment ratio for the tax year' AND 'The "
                    "taxpayer must have net earnings, rather than a net loss, for the tax year.' Due date: "
                    "the 15th day of the 4th month following the period end date as shown on the "
                    "corresponding federal income tax return filed; 'The tax period covered must coincide "
                    "with the federal income tax return.' Electronic filing and payment is required unless a "
                    "hardship exemption has been received."
                ),
                "summary_text": "Two real filing modes: inactive-entity page-1-only ($100 minimum), and P.L. 86-272 franchise-schedules-only. E-file is mandatory absent hardship.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "TN_FE_MANUAL_DEC2025",
        "source_type": "state_instruction",
        "source_rank": "primary_official",
        "jurisdiction_code": "TN",
        "title": "Tennessee Franchise and Excise Tax Manual (December 2025)",
        "citation": "TN DOR Franchise & Excise Tax Manual, published December 2025, 563 pp., /ModDate 2025-12-21",
        "issuer": "Tennessee Department of Revenue",
        "official_url": "https://www.tn.gov/content/dam/tn/revenue/documents/tax_manuals/december-2025/Frachise-Excise-Tax-Manual.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.4,
        "topics": ["tn_franchise_excise", "tn_bonus_depreciation", "tn_property_measure"],
        "excerpts": [
            {
                "excerpt_label": "OBBBA chapter pp. 267-268 — bonus, §168(n), §179 (verbatim)",
                "excerpt_text": (
                    "'To the extent that bonus depreciation allowable under the OBBBA is deducted for "
                    "federal income tax purposes in excess of the amount allowable for the tax year pursuant "
                    "to the TCJA, the excess bonus depreciation cannot be deducted for excise tax purposes; "
                    "this portion of the property's basis must be depreciated for Tennessee excise tax "
                    "purposes in accordance with the federal MACRS depreciation provisions, and the taxpayer "
                    "must make appropriate bonus depreciation addback and deduction adjustments on Schedule "
                    "J of the excise tax return accordingly.' On qualified production property: 'Because IRC "
                    "168(n) does not exist in the TCJA version of IRC 168, this OBBBA provision is not "
                    "applicable for Tennessee excise tax purposes' -- depreciate as MACRS nonresidential "
                    "real property. On 179 (p. 270): 'Tennessee conforms to IRC 179 via the state's general "
                    "rolling conformity with the Internal Revenue Code, as amended' -- $2,500,000 limit / "
                    "$4,000,000 phaseout, indexed, for tax years beginning after 12/31/2024."
                ),
                "summary_text": "OBBBA 100% bonus is NOT available in TN for TY2025 (60-point add-back plus MACRS recovery of the differential); §168(n) gets zero TN bonus; §179 conforms at $2.5M/$4M.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "The two bonus regimes and the TCJA phase-down table (pp. 223-225)",
                "excerpt_text": (
                    "p. 223: 'For assets purchased on or before December 31, 2022, bonus depreciation "
                    "deductions continue to be disallowed for excise tax purposes.' p. 224: 'Tennessee "
                    "decoupled from federal bonus depreciation for assets acquired on or after July 15, "
                    "2002, and before January 1, 2023.' Federal bonus is found at Form 4562 Part II Line 14 "
                    "and Part V Line 25. p. 224 standing reminder: 'for assets purchased on or after January "
                    "1, 2023, Tennessee remains coupled with the federal bonus depreciation provisions under "
                    "IRC 168, as amended by the ... TCJA. If the federal bonus depreciation provisions are "
                    "amended by subsequent enactment of federal legislation, Tennessee will nevertheless "
                    "remain coupled with the TCJA bonus depreciation provisions unless conforming state "
                    "legislation is enacted.' p. 225 phase-down table, caption 'Asset Acquired Between:' -- "
                    "9/28/2017-12/31/2022 100%; 1/1/2023-12/31/2023 80%; 1/1/2024-12/31/2024 60%; "
                    "1/1/2025-12/31/2025 40%; 1/1/2026-12/31/2026 20%; 1/1/2027 and after 0%."
                ),
                "summary_text": "Two simultaneous regimes: pre-2023 assets get FULL bonus disallowance forever; post-2022 assets follow the frozen TCJA percentages (40% for 2025).",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "⚠ U1 / W2 — the unreconciled Schedule J line assignment (p. 223)",
                "excerpt_text": (
                    "p. 223: 'Taxpayers should not make any adjustments on Schedule J, Lines 3, 16, or 17, "
                    "as a result of federal bonus depreciation deductions taken on depreciable property "
                    "purchased on or after January 1, 2023 (unless the federal bonus depreciation provisions "
                    "are amended by subsequent enactment of federal legislation, resulting in federal bonus "
                    "depreciation applicable percentages that differ from those applied by Tennessee for any "
                    "of the years indicated on the following page).' 'The following page' is the 2023-2027 "
                    "phase-down table, and OBBBA produces a federal percentage that differs from Tennessee's "
                    "for exactly those years -- so OBBBA IS that subsequent enactment. But pp. 267-268 "
                    "mandate Schedule J adjustments WITHOUT NAMING A LINE, and the DOR did not update the "
                    "Line 3/16/17 wording on a form re-stamped 2025-12-31. UNRECONCILED."
                ),
                "summary_text": "U1/W2: the p. 223 parenthetical arguably switches L3/16/17 back on for post-2022 assets, but the DOR never said so on the form. Working assumption: L3/16/17 carry both regimes; v1 RED-defers.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "⚠ U2 / W1 — acquired vs placed-in-service, contradicted in one manual",
                "excerpt_text": (
                    "p. 225 table caption: 'Asset Acquired Between:'. p. 224 narrative: assets 'acquired'. "
                    "p. 267 narrative: 'the 40%, 20%, and 0% applicable percentages will apply for excise "
                    "tax purposes to qualified property placed in service in 2025, 2026, and 2027 and "
                    "after'. The form face and instructions say 'purchased'. p. 267 further describes the "
                    "FEDERAL OBBBA rule as 100% for property 'acquired' after January 19, 2025 while keying "
                    "TENNESSEE's 40/20/0 to property 'placed in service' -- both keys inside a single "
                    "sentence. These diverge for an asset acquired in 2024 and placed in service in 2025 "
                    "(60% vs 40%), and the keying also decides which regime an asset falls into."
                ),
                "summary_text": "U2/W1 ESCALATED: the DOR states BOTH keys. This changes numbers on real returns. GATE1_WALK item 3 -- Ken's ruling required; the spec picks nothing.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Imposition test, exemptions, FI test, nexus",
                "excerpt_text": (
                    "p. 17: 'Franchise and excise tax is imposed on entities that operate in Tennessee and "
                    "offer their owners limited liability protection.' Not subject: sole proprietorships and "
                    "general partnerships, 'because they do not provide their owners limited liability "
                    "protection'. p. 26: 'There are 17 types of exemptions available to entities that would "
                    "otherwise be subject to franchise and excise tax ... If a taxpayer fails to meet the "
                    "requirements for the exemption at any time during the taxable period, the taxpayer "
                    "loses the exemption for the entire taxable period.' Exactly TEN are starred as "
                    "requiring FAE183. p. 27: FAE183 is 'due on or before the 15th day of the fourth month "
                    "following the close of the entity's taxable period', a seven-month extension is "
                    "granted, and 'While failure to timely file the form will not preclude the entity from "
                    "qualifying for the exemption, the Department may assess the entity a penalty of $200, "
                    "per occurrence, for late filing.' p. 55: 'If more than 50% of an entity's gross "
                    "receipts are from carrying on the \"business of a financial institution,\" franchise "
                    "and excise tax Form FAE174 should be completed instead of Form FAE170.'"
                ),
                "summary_text": "Limited liability, not federal classification, is the imposition test. 17 exemptions, 10 needing annual FAE183. >50% financial-institution receipts => FAE174 INSTEAD OF FAE170.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Schedule K reversals, standard deduction, estimates, extension",
                "excerpt_text": (
                    "p. 298 (Schedule K): 'These reversals (add-backs) should never turn an apportioned "
                    "business loss ... into income.' Schedule K reverses Schedule J Lines 18, 22 and 33 and "
                    "Schedule J1 Lines 6 and 7 or Schedule J2 Line 8. Tennessee loss carryover is computed "
                    "separately from federal and carries forward 15 years, oldest first. pp. 257-258: the "
                    "$50,000 excise tax standard deduction applies pre-apportionment, cannot create or "
                    "increase a loss, cannot be carried forward, one per return; the Public Chapter 343 "
                    "(2025) optional deduction addback under 67-4-2006(c)(10) may be 'made, adjusted, or "
                    "removed at the taxpayer's discretion for any tax year on any timely filed original or "
                    "amended return'. p. 108: estimates required when combined liability after credits is "
                    "$5,000 or more for BOTH the prior and current tax year. p. 109: each installment is the "
                    "lesser of 25% of the prior year's total liability or 25% of 80% of the projected "
                    "current year's liability. Extension: lesser of 90% current / 100% prior, and 'If the "
                    "taxpayer had a zero tax liability for the prior tax year, then the required extension "
                    "payment is $100.'"
                ),
                "summary_text": "Schedule K's four reversals never create income; 15-year TN NOL; $50k standard deduction pre-apportionment; $5,000-both-years estimate test; $100 extension payment when the prior year was zero.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Schedule G election purpose and manufacturer cap (p. 198, p. 155)",
                "excerpt_text": (
                    "p. 198: Public Chapter 950 (2024) eliminated the property measure as a mandatory "
                    "alternative base for tax years ending on or after 1/1/2024; it survives as an annual "
                    "opt-in election, and the taxpayer 'will file Schedule G with its tax return' (Schedule "
                    "G and the election form are both 'available in TNTAP'). Purpose: let taxpayers with "
                    "large F&E credit carryforwards generate enough liability to use them. Manufacturer cap: "
                    "'Tenn. Code Ann. 67-4-2121 limits the franchise tax base of any manufacturer to $2 "
                    "billion'. Minimum tax $100 per year (67-4-2119), owed by any registered entity "
                    "including an inactive one and one whose charter has been revoked but not dissolved."
                ),
                "summary_text": "Schedule G survives only as an opt-in election; $2B manufacturer base cap; the $100 minimum franchise tax is owed even by inactive and charter-revoked entities.",
                "is_key_excerpt": False,
            },
        ],
    },
    {
        "source_code": "TN_FE_MANUAL_DEC2023",
        "source_type": "state_instruction",
        "source_rank": "primary_official",
        "jurisdiction_code": "TN",
        "title": "Tennessee Franchise and Excise Tax Manual (December 2023) — retained for Schedule G",
        "citation": "TN DOR Franchise & Excise Tax Manual, December 2023, 621 pp., /ModDate 2023-12-08",
        "issuer": "Tennessee Department of Revenue",
        "official_url": "https://www.tn.gov/content/dam/tn/revenue/documents/tax_manuals/december-2023/Franchise-Excise-Tax-Manual.pdf",
        "current_status": "superseded",
        "is_substantive_authority": True,
        "trust_score": 8.0,
        "topics": ["tn_property_measure"],
        "excerpts": [
            {
                "excerpt_label": "Schedule G sub-rent and lease rules (the only load-bearing use)",
                "excerpt_text": (
                    "pp. 223-224: the rental multiples are applied line by line -- 'multiplying the net "
                    "annual rental by 8 ... reported on Schedule G, Line 11', and correspondingly x3 (L12), "
                    "x2 (L13), x1 (L14). Net annual rental = gross annual rent paid less gross rent received "
                    "for sub-rental, floored at zero (never negative); sub-rental requires the same property "
                    "and the same rights. Rents are annualized for short periods before the multiple is "
                    "applied. p. 240: finance leases are treated as an owned asset at net book value while "
                    "operating leases are rent x multiple -- and Schedule N1 uses a multiple of 8 for ALL "
                    "rents, unlike Schedule G's 8/3/2/1. The December 2025 manual states it 'has been "
                    "updated to remove all guidance pertaining to the franchise tax Schedule G minimum "
                    "measure' and points to Chapter 10 of this December 2023 edition."
                ),
                "summary_text": "SUPERSEDED except for Schedule G: sub-rent netting (floored at zero), short-period annualization, and finance-vs-operating lease treatment. The 8/3/2/1 multiples themselves are on the CURRENT form face.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "TN_SCHED_G_PROPERTY",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "TN",
        "title": "Tennessee Schedule G — Determination of Real and Tangible Property",
        "citation": "Schedule G, rev. RV-F700012 (12/24) [⚠ the ELECTION form shares this same revision code at a different URL — never key on RV-F700012 as a unique document id]",
        "issuer": "Tennessee Department of Revenue",
        "official_url": "https://www.tn.gov/content/dam/tn/revenue/documents/forms/fae/RV-F700012.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.2,
        "topics": ["tn_property_measure"],
        "excerpts": [
            {
                "excerpt_label": "Schedule G line map and the 8/3/2/1 multipliers (printed on the form face)",
                "excerpt_text": (
                    "Book Value of Property Owned -- cost less accumulated depreciation, In Tennessee, GAAP "
                    "basis: 1 Land; 2 Buildings, leaseholds, and improvements; 3 Machinery, equipment, "
                    "furniture, and fixtures; 4 Automobiles and trucks; 5 Prepaid supplies and other "
                    "tangible personal property; 6 Ownership share of real and tangible property of a "
                    "partnership that does not file a return; 7a Inventories and work in progress; 7b Exempt "
                    "finished goods inventory in excess of $30 million; 8 Certified pollution control "
                    "equipment; 9 Exempt required capital investments; 10 'Subtotal (add Lines 1 through 7a, "
                    "subtract Lines 7b through 9)'. Rental Value Of Property Used But Not Owned: 11 Real "
                    "property x8; 12 Machinery and equipment used in manufacturing and processing x3; 13 "
                    "Furniture, office machinery, and equipment x2; 14 Delivery or mobile equipment x1; 15 "
                    "'Tennessee total (add Lines 10 through 14; enter here and on Schedule A, Line 2)'."
                ),
                "summary_text": "Sch. G L15 -> Sch. A L2. The x8/x3/x2/x1 multipliers are PRINTED ON THE CURRENT FORM FACE, so they do not rest on the superseded 2023 manual.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "TN_SCHED_G_ELECTION",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "TN",
        "title": "Tennessee Schedule G Minimum Property Measure Election (Franchise Tax)",
        "citation": "Schedule G Minimum Property Measure Election, rev. RV-F700012 (12/24) [same revision code as the property schedule — different document]",
        "issuer": "Tennessee Department of Revenue",
        "official_url": "https://www.tn.gov/content/dam/tn/revenue/documents/forms/fae/Schedule%20G.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.2,
        "topics": ["tn_property_measure"],
        "excerpts": [
            {
                "excerpt_label": "The three § 67-4-2123 conditions and the constitutional waiver (verbatim)",
                "excerpt_text": (
                    "'If a taxpayer's net worth tax base under Tenn. Code Ann. 67-4-2106 and -2107 for a "
                    "given tax period results in a lower tax base than the minimum property measure tax base "
                    "... then the taxpayer may elect to use the minimum property measure tax base ... "
                    "provided, however, the election must result in a higher tax levied for the tax period, "
                    "and the taxpayer waives any claim that the minimum tax base under Tenn. Code Ann. "
                    "67-4-2108 is unconstitutional by failing the internal consistency test.' The form "
                    "carries a SEPARATE SECOND SIGNATURE BLOCK for the constitutional waiver. 'This is an "
                    "annual election. An election form is required for each tax year the taxpayer makes the "
                    "election.' 'Please submit this election form online using Tennessee Taxpayer Access "
                    "Point (TNTAP)... Only if you cannot e-file in TNTAP, mail completed form...'"
                ),
                "summary_text": "Three cumulative conditions plus a signed constitutional waiver, elected ANNUALLY and submitted through TNTAP separately from the return.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "TN_TCA_67_4_2006",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "TN",
        "title": "Tenn. Code Ann. § 67-4-2006 — Net earnings; Tennessee additions and deductions",
        "citation": "Tenn. Code Ann. § 67-4-2006(a), (a)(10)-(a)(12), (b), (b)(1)(P), (b)(2)(M)/(N)/(P)/(T), (c)(8), (c)(10) (2025)",
        "issuer": "Tennessee General Assembly",
        "official_url": "https://www.tn.gov/content/dam/tn/revenue/documents/tax_manuals/december-2025/Frachise-Excise-Tax-Manual.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.3,
        "topics": ["tn_franchise_excise", "tn_bonus_depreciation"],
        "excerpts": [
            {
                "excerpt_label": "The statutory decouplings behind Schedule J",
                "excerpt_text": (
                    "67-4-2006(a) defines net earnings as federal taxable income before the net operating "
                    "loss deduction and special deductions, with the (b) adjustments. (a)(10) decouples from "
                    "TCJA IRC 163(j) -- TN conforms to the PRE-TCJA 163(j), so most taxpayers fully expense "
                    "business interest (Sch. J L13 add-back / L28a deduction). (a)(11) allows full IRC 174 "
                    "expensing for tax years beginning on/after 1/1/2022 (Sch. J L14 / L29). (a)(12) locks "
                    "IRC 168(k) to the TCJA version (Public Chapter 377 (2023)). (b)(1)(P) and (b)(2)(T) "
                    "produce the 5% NCTI/GILTI result: the full amount is deducted on Sch. J L27 and 5% is "
                    "added back on L12, with the IRC 250 deduction NOT allowed. (b)(2)(M) and (P) give the "
                    "75% qualified-school-donation deduction (L19). (c)(8) reduces the loss carryover for "
                    "discharge of indebtedness. (c)(10), added by Public Chapter 343 (2025), is the "
                    "taxpayer-elective optional deduction addback (L33)."
                ),
                "summary_text": "One statute drives most of Schedule J: pre-TCJA §163(j), full §174 expensing, the TCJA §168(k) lock, net 5% GILTI with no §250, the 75% school donation, and the PC 343 optional addback.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "TN_TCA_67_4_2123",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "TN",
        "title": "Tenn. Code Ann. § 67-4-2123 — Annual election of minimum tax base pursuant to § 67-4-2108",
        "citation": "Tenn. Code Ann. § 67-4-2123, added by Public Chapter 950 (2024), effective 5/10/2024",
        "issuer": "Tennessee General Assembly",
        "official_url": "https://law.justia.com/codes/tennessee/title-67/chapter-4/part-21/section-67-4-2123/",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.0,
        "topics": ["tn_property_measure"],
        "excerpts": [
            {
                "excerpt_label": "Property measure repealed as a mandatory base, retained as an election",
                "excerpt_text": (
                    "Public Chapter 950 (2024), signed 5/10/2024, eliminated the property measure (the "
                    "'minimum measure', historically the greater-of alternative base computed on Schedule G) "
                    "effective for tax years ending on or after January 1, 2024, leaving franchise tax based "
                    "on net worth (Schedule F) only. Section 67-4-2123 then permits an ANNUAL election to "
                    "use the minimum property measure base, conditioned on all three of: a LOWER net-worth "
                    "base than the 67-4-2108 minimum base; an election that RESULTS IN A HIGHER TAX; and a "
                    "WAIVER of any internal-consistency constitutional claim. The associated refund window "
                    "(May 15, 2024 - November 30, 2024) is CLOSED and historical only."
                ),
                "summary_text": "PC 950 (2024) killed the mandatory property measure; § 67-4-2123 keeps it alive as a conditional annual election. Sch. A Line 3's greater-of therefore stays live.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "TN_2025_SCHED_PL",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "TN",
        "title": "Tennessee Schedule PL / PLCF — Employer Credit for Paid Family and Medical Leave",
        "citation": "Schedule PL / PLCF, rev. RV-F700009 (9/25), /ModDate 2026-03-02",
        "issuer": "Tennessee Department of Revenue",
        "official_url": "https://www.tn.gov/content/dam/tn/revenue/documents/forms/fae/RV-F700009.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.0,
        "topics": ["tn_franchise_excise"],
        "excerpts": [
            {
                "excerpt_label": "Carryforward-only on the TY2025 form",
                "excerpt_text": (
                    "Schedule PL Line 1 is 'Credit available from prior year(s) (from Schedule PLCF)' -- "
                    "there is NO current-year credit line. Instructions: 'This tax credit has expired for "
                    "tax years ending on or after December 31, 2025 ... However, unused tax credits that "
                    "have been established for tax years ending on or after December 31, 2023, but before "
                    "December 31, 2025, may be carried forward up to 25 years.' Schedule PL Line 7 feeds "
                    "Schedule D Line 9. Schedule J Line 20 instruction: 'Do not deduct Paid Family and "
                    "Medical Leave for which a credit was claimed on Schedule PL of this return.'"
                ),
                "summary_text": "Schedule PL appears on the TY2025 form only because of its 25-year carryforward, NOT because of short 2025 periods -- which resolved half of the earlier open item.",
                "is_key_excerpt": True,
            },
        ],
    },
]

AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    ("TN_2025_FAE170_FORM", "TN_FAE170", "governs"),
    ("TN_2025_FAE170_INSTR", "TN_FAE170", "governs"),
    ("TN_FE_MANUAL_DEC2025", "TN_FAE170", "governs"),
    ("TN_FE_MANUAL_DEC2023", "TN_FAE170", "informs"),
    ("TN_SCHED_G_PROPERTY", "TN_FAE170", "informs"),
    ("TN_SCHED_G_ELECTION", "TN_FAE170", "informs"),
    ("TN_TCA_67_4_2006", "TN_FAE170", "governs"),
    ("TN_TCA_67_4_2123", "TN_FAE170", "governs"),
    ("TN_2025_SCHED_PL", "TN_FAE170", "informs"),
    ("TN_TCA_67_4_2004_IRC_DEF", "TN_FAE170", "governs"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM — TN_FAE170
#
# LINE NUMBERING: FAE170 reuses numbers across schedules (Sch. J1 L1, Sch. J
# L1, Sch. F1 L1 ... all exist), so every FormLine is namespaced
# `<schedule>-<line>` — "A-3", "J1-11", "J-28a", "F1-5". FormLine is
# unique_together on (tax_form, line_number) and the raw numbers WOULD COLLIDE.
# The face's own continuous 1-16 numbering across Schedules A/B/C is preserved
# inside the namespace: A-1..A-3, B-4..B-7, C-8..C-16.
# ═══════════════════════════════════════════════════════════════════════════

# ── Schedule J modification lines — VERBATIM form-face labels ──────────────
# 27 NUMBERED modification lines (2-14 = 13 additions; 16-29 = 14 deductions)
# but 28 ENTRY FIELDS, because Line 28 splits into 28a/28b.
# Tuple: (line_suffix, fact_key, verbatim_label, instruction_note)

J_ADDITIONS: list[tuple[str, str, str, str]] = [
    ("2", "j_l2_intangible_expense_affiliate",
     "Intangible expenses paid, accrued, or incurred to an affiliated business entity or entities deducted for federal income tax purposes",
     "Definitions at Tenn. Code Ann. 67-4-2004(1) and (24). Pairs with the L23 deduction, which is ALLOWED ONLY IF Form IE is attached. Nondisclosure penalty: the GREATER of $10,000 or 50% of the adjustment. RED-defer R14."),
    ("3", "j_l3_bonus_depr_disallowed",
     "Any depreciation under the provisions of IRC Section 168 not permitted for excise tax purposes due to Tennessee decoupling from federal bonus depreciation for assets purchased on or before December 31, 2022",
     "Federal bonus is at Form 4562 Part II Line 14 and Part V Line 25. DIRECT-ENTRY in v1 (W3). The form face scopes this line to PRE-2023 assets; whether it also carries the post-2022 OBBBA differential is U1/W2 -- RED-deferred (R13), never silently computed."),
    ("4", "j_l4_gain_asset_sold_12mo",
     "Gain on the sale of an asset sold within 12 months after the date of distribution to a nontaxable entity",
     "Reported by the DISTRIBUTING entity. 'Failure to report this gain may result in a 50% negligence penalty.' Mirrors the L9 deduction on J1 and the L5 deduction on J3."),
    ("5", "j_l5_tn_excise_tax_expense",
     "Tennessee excise tax expense (to the extent reported for federal income tax purposes)",
     "MAY BE NEGATIVE -- an over-accrual reversal reduces the add-back."),
    ("6", "j_l6_gross_premiums_tax",
     "Gross premiums tax deducted in determining federal income and used as an excise tax credit",
     "Paired with Schedule D Line 1. The taxpayer MAY ELECT TO FOREGO the credit, in which case this add-back is not made. Excludes the 0.4% TOSHA surcharge."),
    ("7", "j_l7_muni_interest_income",
     "Interest income on obligations of states and their political subdivisions, less allowable amortization",
     "'all tax-exempt interest as shown on the books', net of interest disallowed under 26 U.S.C. 265 and 291."),
    ("8", "j_l8_depletion_not_cost_based",
     "Depletion not based on actual recovery of cost",
     "Percentage depletion."),
    ("9", "j_l9_donated_property_fmv_excess",
     "Excess fair market value over book value of property donated",
     ""),
    ("10", "j_l10_excess_rent_affiliate",
     "Excess rent to/from an affiliate",
     "'Reasonable rent means rent that does not exceed 2% per month of the appraised value for property tax purposes.' The RECIPIENT affiliate may enter a NEGATIVE."),
    ("11", "j_l11_pte_loss_received",
     "Net loss or expense received from a pass-through entity subject to the excise tax (attach schedule)",
     "Prevents duplicate recognition -- made ONLY IF the K-1 issuer itself files F&E. NOT made if the issuer is exempt under Tenn. Code Ann. 67-4-2008. Mirror of the L25 deduction."),
    ("12", "j_l12_gilti_5pct_addback",
     "An amount equal to five percent of IRC Section 951A global intangible low-taxed income deducted on Line 27",
     "5% of GILTI computed BEFORE any IRC 250 deduction. Paired with L27, so a NET 5% of GILTI is taxed and the 250 deduction is NOT allowed. Tenn. Code Ann. 67-4-2006(b)(1)(P), (b)(2)(T). OBBBA 951A changes apply for tax years beginning after 12/31/2025 -- NOT TY2025."),
    ("13", "j_l13_business_interest_addback",
     "Business interest expense deducted in arriving at the amount reported on Sch. J, Line 1. Only complete if federal Form 8990 was filed.",
     "Excludes amounts already on L11. U4 ERRATUM: this instruction closes by pointing at 'Sch. J, Line 27a', which DOES NOT EXIST -- Line 27 is GILTI and the deduction is Line 28a. BUILD TO 28a. Recorded so nobody 'fixes' it back."),
    ("14", "j_l14_section_174_rd_addback",
     "Research and experimental expenditures deducted under IRC Section 174 in arriving at the amount reported on Sch. J, Line 1",
     "Paired with the L29 deduction. TN has allowed full 174 expensing since 1/1/2022 (Tenn. Code Ann. 67-4-2006(a)(11)), so the pair nets to full expensing."),
]

J_DEDUCTIONS: list[tuple[str, str, str, str]] = [
    ("16", "j_l16_bonus_depr_permitted",
     "Any depreciation under the provisions of IRC Section 168 permitted for excise tax purposes due to Tennessee decoupling from federal bonus depreciation for assets purchased on or before December 31, 2022",
     "The depreciation TN DOES permit on the Tennessee basis (federal method and life, MACRS, minus the bonus). DIRECT-ENTRY in v1 (W3). Same U1/W2 scope question as L3."),
    ("17", "j_l17_basis_difference_gain_loss",
     "Any excess gain (or loss) from the basis adjustment resulting from Tennessee decoupling from federal bonus depreciation for assets purchased on or before December 31, 2022 (or other federal/state basis difference - see instructions)",
     "BROADER THAN BONUS: 'This line may also be used to deduct excess gain or loss due to other federal/state basis differences that Tennessee has recognized.' The disposition true-up. DIRECT-ENTRY in v1 (W3)."),
    ("18", "j_l18_dividends_80pct_owned",
     "Dividends received from corporations at least 80% owned",
     "DIRECT ownership of at least 80% of stock. REVERSED on Schedule K Line 2 in the loss-carryover computation."),
    ("19", "j_l19_school_donations_75pct",
     "Donations to qualified public school support groups and nonprofit organizations",
     "THE FORM LABEL OMITS THE PERCENTAGE -- the instruction says 'Enter 75% of donations' (Tenn. Code Ann. 67-4-2006(b)(2)(M) and (P)). A certification form is required."),
    ("20", "j_l20_expense_with_federal_credit",
     "Any expense other than income taxes not deducted in determining federal taxable income for which a credit against the federal income tax was allowed",
     "'Do not deduct Paid Family and Medical Leave for which a credit was claimed on Schedule PL of this return.'"),
    ("21", "j_l21_safe_harbor_lease_adj",
     "Adjustments related to the safe harbor lease election (see instructions)",
     "Tenn. Code Ann. 67-4-2006(b)(1)(G), (b)(2)(G)-(H); ERTA 1981. 'If the net adjustment is an increase in taxable income, enter a negative number.'"),
    ("22", "j_l22_nonbusiness_earnings",
     "Nonbusiness earnings (from Schedule M, Line 8)",
     "Removes nonbusiness earnings from the APPORTIONED base; the Tennessee-allocated portion re-enters POST-apportionment at Line 37 (Schedule M Line 11). REVERSED on Schedule K Line 2."),
    ("23", "j_l23_intangible_expense_form_ie",
     "Intangible expenses paid, accrued, or incurred to an affiliated entity or entities (from Form IE, Line 4)",
     "ALLOWED ONLY IF Line 2 is completed AND Form IE is attached -- otherwise the deduction is DISALLOWED and the greater-of-$10,000-or-50% penalty applies. RED-defer R14."),
    ("24", "j_l24_intangible_income_affiliate",
     "Intangible income from an affiliated business entity or entities if the corresponding intangible expenses have not been deducted by the affiliate(s) under Tenn. Code Ann. Section 67-4-2006(b)(2)(N)",
     ""),
    ("25", "j_l25_pte_gain_received",
     "Net gain or income received from a pass-through entity subject to the excise tax (attach schedule)",
     "Mirror of the L11 addition -- same 'issuer must itself file F&E' condition."),
    ("26", "j_l26_government_grants",
     "Deductible Grants from governmental units",
     "Grants swept into federal taxable income as a result of the TCJA."),
    ("27", "j_l27_gilti_full",
     "IRC Section 951A global intangible low-taxed income",
     "The FULL GILTI amount BEFORE IRC 250. Paired with the 5% add-back on L12, so a net 5% is taxed and the 250 deduction is NOT allowed."),
    ("28a", "j_l28a_business_interest_deductible",
     "Business interest expense currently deductible. See instructions",
     "Pro forma Form 8990 LINES 1 AND 4 plus 2018/2019 carryforwards; PLUS a partner's share of excess business interest from Form 8990 Sch. A Line 43 column (c) where the partnership does not file F&E; EXCLUDING disqualified interest disallowed on Form 8926 under PRE-TCJA 163(j). TN conforms to the pre-TCJA 163(j) (Tenn. Code Ann. 67-4-2006(a)(10)), so most taxpayers fully expense business interest. THIS IS THE LINE THE L13 INSTRUCTION MISCALLS '27a'."),
    ("28b", "j_l28b_business_interest_carryforward",
     "Business interest expense carryforward available for future tax years",
     "INFORMATIONAL ONLY -- EXCLUDED from the Line 30 total ('Add Lines 16 through 29, excluding Line 28b'). A spec that sums 16..29 inclusive will overstate the deduction."),
    ("29", "j_l29_section_174_rd_deductible",
     "Research and experimental expenditures currently deductible",
     "'the amount ... allowed by Section 174 ... immediately before enactment of the TCJA' -- i.e. FULL EXPENSING, for tax years beginning on or after 1/1/2022. Paired with the L14 add-back."),
]


TN170_FACTS: list[dict] = [
    # ── Identity, period, and the branching switches ───────────────────────
    {"fact_key": "federal_entity_type", "label": "Federal classification (selects the Schedule J entry point)",
     "data_type": "choice", "required": True, "sort_order": 1,
     "choices": ["1065", "1120S", "1120", "1040_smllc"],
     "notes": "1065 -> Schedule J1 (L11); 1040_smllc -> J2 (L9); 1120S -> J3 (L7); 1120 -> J4 (L11). "
              "The IMPOSITION test is LIMITED LIABILITY, not this election -- see is_limited_liability_entity. "
              "Federal classification is honored for COMPUTING net earnings; EXEMPTION eligibility follows "
              "state-law organizational form (one exception: the asset-backed securitization exemption DOES look to federal classification)."},
    {"fact_key": "tax_period_begin", "label": "Tax period begin date", "data_type": "date", "required": True, "sort_order": 2,
     "notes": "The TN period MUST coincide with the corresponding federal return's period."},
    {"fact_key": "tax_period_end", "label": "Tax period end date", "data_type": "date", "required": True, "sort_order": 3,
     "notes": "Drives the due date (15th day of the 4th month following) AND the apportionment form-year selection, which keys on period END."},
    {"fact_key": "is_short_period", "label": "Short period return?", "data_type": "boolean", "required": False, "sort_order": 4,
     "notes": "U3: a short period BEGINNING on/after 1/1/2025 and ENDING before 12/31/2025 statutorily falls in the 11x/13 apportionment row that the TY2025 Schedule N cannot express. Unresolved DOR edge case."},
    {"fact_key": "is_5253_week_filer", "label": "52/53-week filer?", "data_type": "boolean", "required": False, "sort_order": 5,
     "notes": "Franchise tax may NOT be prorated for 52/53-week filers. They conform to the nearest calendar year end (12/28 and 1/2 both -> April 15)."},
    {"fact_key": "date_tn_operations_began", "label": "Date Tennessee operations began (form face)", "data_type": "date", "required": False, "sort_order": 6},
    {"fact_key": "is_limited_liability_entity", "label": "Does the entity offer its owners limited liability?", "data_type": "boolean", "required": True, "sort_order": 7,
     "notes": "THE IMPOSITION TEST. Sole proprietorships and general partnerships are NOT subject (no limited liability). Disregarded entities ARE subject, except an SMLLC whose single member is a CORPORATION and an SMLLC wholly owned by a PENSION TRUST."},
    {"fact_key": "is_tennessee_domestic", "label": "Tennessee-domestic entity?", "data_type": "boolean", "required": False, "sort_order": 8,
     "notes": "A TN-domestic entity is ALWAYS subject and owes the $100 minimum franchise tax even with zero TN property, payroll and sales."},
    {"fact_key": "is_inactive_entity", "label": "Inactive in Tennessee for the entire taxable period?", "data_type": "boolean", "required": False, "sort_order": 9,
     "notes": "Page-1-only filing mode: registered but inactive, owes only the $100 minimum, 'may file only page one of this return and omit the remaining pages'."},
    {"fact_key": "is_manufacturer", "label": "Manufacturer (for the $2 billion franchise base cap)?", "data_type": "boolean", "required": False, "sort_order": 10,
     "notes": "Tenn. Code Ann. 67-4-2121 caps the franchise tax base of any manufacturer at $2,000,000,000 (instruction on F1 L5 and F2 L3)."},
    {"fact_key": "is_financial_institution", "label": "More than 50% of gross receipts from the business of a financial institution?",
     "data_type": "boolean", "required": False, "sort_order": 11,
     "notes": "HARD STOP: 'Form FAE174 should be completed instead of Form FAE170.' A STANDALONE-ENTITY test, not a group-only rule. Also captive REITs."},
    {"fact_key": "exemption_claimed", "label": "Section 67-4-2008 exemption claimed (one of 17)", "data_type": "string", "required": False, "sort_order": 12,
     "notes": "10 of the 17 require FAE183 for the initial and each subsequent period. Losing the requirements AT ANY POINT during the period forfeits the exemption for the ENTIRE period. Late FAE183 does NOT forfeit -- $200 per occurrence only."},
    # Return-level checkboxes (a)-(i)
    {"fact_key": "is_amended_return", "label": "Checkbox (a) Amended return", "data_type": "boolean", "required": False, "sort_order": 20},
    {"fact_key": "is_final_return", "label": "Checkbox (b) Final return", "data_type": "boolean", "required": False, "sort_order": 21},
    {"fact_key": "pl_86_272_claimed", "label": "Checkbox (c) Public Law 86-272 applied to excise tax", "data_type": "boolean", "required": False, "sort_order": 22,
     "notes": "P.L. 86-272 kills the EXCISE tax only. The taxpayer still files FAE170 and completes the FRANCHISE tax schedules."},
    {"fact_key": "consolidated_nw_election", "label": "Checkbox (d) Consolidated net worth election (67-4-2103(g)-(i))", "data_type": "boolean", "required": False, "sort_order": 23,
     "notes": "Binding FIVE years. Routes to Schedule F2 -- RED-deferred (R2/W5)."},
    {"fact_key": "consolidated_nw_revocation", "label": "Checkbox (e) Filed the prescribed form to revoke the election", "data_type": "boolean", "required": False, "sort_order": 24},
    {"fact_key": "annualized_installment_election", "label": "Checkbox (f) Annualized income installment method election", "data_type": "boolean", "required": False, "sort_order": 25,
     "notes": "Annual election, ORIGINAL return only. RED-deferred (R11)."},
    {"fact_key": "federal_extension_filed", "label": "Checkbox (g) Taxpayer has filed for federal extension (Form 7004)", "data_type": "boolean", "required": False, "sort_order": 26},
    {"fact_key": "three_factor_election", "label": "Checkbox (h) Three-factor apportionment election", "data_type": "boolean", "required": False, "sort_order": 27,
     "notes": "Requires BOTH a HIGHER resulting ratio AND net earnings rather than a net loss. Routes to Schedule N1 -- RED-deferred (R3/W6)."},
    {"fact_key": "telecom_qualified_member", "label": "Checkbox (i) Telecom Qualified Member (67-4-2012(j))", "data_type": "boolean", "required": False, "sort_order": 28,
     "notes": "MANDATORY three-factor under 67-4-2012(a)(7), not elective. Class includes telecommunications, mobile telecom, internet access, VIDEO PROGRAMMING and DIRECT-TO-HOME SATELLITE TV service. Routes to Schedule N1 -- RED-deferred (R3)."},
    {"fact_key": "property_measure_election", "label": "Schedule G minimum property measure election made (67-4-2123)?", "data_type": "boolean", "required": False, "sort_order": 29,
     "notes": "ANNUAL election submitted through TNTAP with a separate constitutional-waiver signature. RED-deferred (R1/W4) -- but Sch. A Line 2 is direct-entry so the greater-of stays live."},

    # ── Schedule J1 — partnerships (federal 1065) ──────────────────────────
    {"fact_key": "j1_l1_ordinary_income_1065_l23", "label": "J1 L1 Ordinary income or loss (federal Form 1065, Line 23)", "data_type": "decimal", "required": False, "sort_order": 100,
     "notes": "Verified against FINAL 2025 Form 1065: 'Ordinary business income (loss). Subtract line 22 from line 8.'"},
    {"fact_key": "j1_l2_allocated_income", "label": "J1 L2 Income items specifically allocated to partners, incl. guaranteed payments", "data_type": "decimal", "required": False, "sort_order": 101,
     "notes": "Form 1065 Sch. K Lines 2-11. EXCLUDE Sch. K L11 IRC 743(b) adjustments (code F). INCLUDE 179-property disposition gain at Sch. K box 20 code L, computed PRO FORMA at the partnership level with partner-level 179 limits DISREGARDED."},
    {"fact_key": "j1_l3_reit_loss_distributed", "label": "J1 L3 Any net loss or expense distributed to a publicly traded REIT", "data_type": "decimal", "required": False, "sort_order": 102},
    {"fact_key": "j1_l5_allocated_expense", "label": "J1 L5 Expense items specifically allocated to partners not deducted elsewhere", "data_type": "decimal", "required": False, "sort_order": 103,
     "notes": "Form 1065 Sch. K Lines 12 and 13a-e. EXCLUDE Sch. K L13 IRC 743(b) (code V). EXCLUDE qualified-plan contributions (they go to L7). INCLUDE 179-disposition LOSS at box 20 code L, same pro-forma rule."},
    {"fact_key": "j1_l6_self_employment", "label": "J1 L6 Amount subject to self-employment taxes distributable or paid to each partner or member", "data_type": "decimal", "required": False, "sort_order": 104,
     "notes": "CLONE TRAP: EXISTS ONLY ON J1 (and as J2 L8). Taken NET of pass-through expense deducted elsewhere on the return, 'such as IRC Section 179 expenses AND CONTRIBUTIONS DEDUCTED ON LINE 5'. If negative, enter zero. Cannot create or increase a loss carryover. ADDED BACK on Schedule K Line 3."},
    {"fact_key": "j1_l7_qualified_plan", "label": "J1 L7 Contribution to qualified pension or benefit plans, including all IRC 401 plans", "data_type": "decimal", "required": False, "sort_order": 105,
     "notes": "CLONE TRAP: EXISTS ONLY ON J1. Cannot create or increase a loss carryover. ADDED BACK on Schedule K Line 3."},
    {"fact_key": "j1_l8_reit_gain_distributed", "label": "J1 L8 Any net gain or income distributed to a publicly traded REIT", "data_type": "decimal", "required": False, "sort_order": 106},
    {"fact_key": "j1_l9_loss_asset_sold_12mo", "label": "J1 L9 Loss on the sale of an asset sold within 12 months after the date of distribution", "data_type": "decimal", "required": False, "sort_order": 107},

    # ── Schedule J2 — individual-owned SMLLC (federal 1040) ────────────────
    {"fact_key": "j2_l1_schedule_c", "label": "J2 L1 Business income or loss from federal Form 1040, Schedule C", "data_type": "decimal", "required": False, "sort_order": 120,
     "notes": "The FORM FACE carries NO federal line number (verification C5). The INSTRUCTION says Schedule C Line 31 -- verified on the FINAL 2025 Sch. C: 'Net profit or (loss). Subtract line 30 from line 29.'"},
    {"fact_key": "j2_l2_schedule_d", "label": "J2 L2 Business income or loss from federal Form 1040, Schedule D", "data_type": "decimal", "required": False, "sort_order": 121,
     "notes": "Capital gain (loss) attributable to the LLC. NO federal line number is given by EITHER the form or the instructions. 'If it is a loss, enter as a negative.'"},
    {"fact_key": "j2_l3_schedule_e", "label": "J2 L3 Business income or loss from federal Form 1040, Schedule E", "data_type": "decimal", "required": False, "sort_order": 122,
     "notes": "NO federal line number given by either document."},
    {"fact_key": "j2_l4_schedule_f", "label": "J2 L4 Business income or loss from federal Form 1040, Schedule F", "data_type": "decimal", "required": False, "sort_order": 123,
     "notes": "Instruction says Schedule F Line 34 -- verified on the FINAL 2025 Sch. F: 'Net farm profit or (loss). Subtract line 33 from line 9.' The form face carries no line number."},
    {"fact_key": "j2_l5_form_4797", "label": "J2 L5 Business income or loss from federal Form 4797", "data_type": "decimal", "required": False, "sort_order": 124,
     "notes": "Gain (loss) attributable to ASSETS USED BY THE LLC. NO federal line number given by either document."},
    {"fact_key": "j2_l6_other", "label": "J2 L6 Other: federal Form ___, Schedule ___", "data_type": "decimal", "required": False, "sort_order": 125},
    {"fact_key": "j2_l8_self_employment", "label": "J2 L8 Amount subject to self-employment taxes distributable or paid to the single member", "data_type": "decimal", "required": False, "sort_order": 126,
     "notes": "Same loss limit and same Schedule K Line 3 add-back as J1 L6. J3 has NO equivalent."},

    # ── Schedule J3 — S corporations (federal 1120S) ───────────────────────
    {"fact_key": "j3_l1_ordinary_income_1120s_l22", "label": "J3 L1 Ordinary income or loss (federal Form 1120S, Line 22)", "data_type": "decimal", "required": False, "sort_order": 140,
     "notes": "Verified against FINAL 2025 Form 1120-S: 'Ordinary business income (loss). Subtract line 21 from line 6.'"},
    {"fact_key": "j3_l2_s_status_income", "label": "J3 L2 Income items to extent includable in federal income were it not for 'S' status election", "data_type": "decimal", "required": False, "sort_order": 141,
     "notes": "Form 1120S Sch. K Lines 2-10. 179-disposition gain at Sch. K box 17 code K, computed PRO FORMA at the S-corp level with SHAREHOLDER-level 179 limits DISREGARDED."},
    {"fact_key": "j3_l4_s_status_expense", "label": "J3 L4 Expense items to extent includable in federal expenses were it not for 'S' status election", "data_type": "decimal", "required": False, "sort_order": 142,
     "notes": "Form 1120S Sch. K Lines 11-12e. 179-disposition loss, same pro-forma rule."},
    {"fact_key": "j3_l5_loss_asset_sold_12mo", "label": "J3 L5 Loss on the sale of an asset sold within 12 months after the date of distribution", "data_type": "decimal", "required": False, "sort_order": 143,
     "notes": "⚠ J3 HAS EXACTLY TWO DEDUCTION LINES -- L4 AND THIS ONE. NO self-employment line, NO qualified-plan line. Do NOT add fields for them."},

    # ── Schedule J4 — corporations and other entities (federal 1120) ───────
    {"fact_key": "j4_l1_taxable_income_1120_l28", "label": "J4 L1 Taxable income before NOL and special deductions (federal Form 1120, Line 28)", "data_type": "decimal", "required": False, "sort_order": 160,
     "notes": "Verified against FINAL 2025 Form 1120 Line 28. A member of a federal CONSOLIDATED group must build a PRO FORMA 1120 -- TN is a separate-entity state."},
    {"fact_key": "j4_l2a_reit_taxable_income", "label": "J4 L2a REIT taxable income before NOL and special deductions (federal Form 1120-REIT, Line 21)", "data_type": "decimal", "required": False, "sort_order": 161},
    {"fact_key": "j4_l2b_reit_dividends_paid", "label": "J4 L2b REIT deduction for dividends paid (federal Form 1120-REIT, Line 22b)", "data_type": "decimal", "required": False, "sort_order": 162,
     "notes": "Verified: 'Total deduction for dividends paid (Schedule A, line 7).'"},
    {"fact_key": "j4_l3_ubti_990t", "label": "J4 L3 Unrelated business taxable income (federal Form 990-T, Line 5)", "data_type": "decimal", "required": False, "sort_order": 163,
     "notes": "THE NONPROFIT PATH. A not-for-profit is not generally subject, but IS subject to excise tax on UBTI and to franchise tax on the net worth attributable to those unrelated activities."},
    {"fact_key": "j4_l4_other_federal_income", "label": "J4 L4 Other: federal Form ___", "data_type": "decimal", "required": False, "sort_order": 164},
    {"fact_key": "j4_l5_contribution_carryover_used", "label": "J4 L5 Contribution carryover from prior period(s)", "data_type": "decimal", "required": False, "sort_order": 165,
     "notes": "TIMING DECOUPLING: 'must be added back to net income when used for federal tax purposes.' Requires a SEPARATE TENNESSEE contribution history per C-corp."},
    {"fact_key": "j4_l6_capital_gains_offset", "label": "J4 L6 Capital gains offset by capital loss carryover or carryback", "data_type": "decimal", "required": False, "sort_order": 166,
     "notes": "TIMING DECOUPLING: 'must be added to net income when offset against capital gains.' Requires a SEPARATE TENNESSEE capital-loss history per C-corp."},
    {"fact_key": "j4_l8_contributions_excess", "label": "J4 L8 Contributions in excess of amount allowed by federal government", "data_type": "decimal", "required": False, "sort_order": 167,
     "notes": "TN allows contributions 'in full, in the year in which the contributions were made' -- the other half of the L5 decoupling."},
    {"fact_key": "j4_l9_current_capital_loss", "label": "J4 L9 Portion of current year's capital loss not included in federal taxable income", "data_type": "decimal", "required": False, "sort_order": 168,
     "notes": "TN allows capital losses 'in full, in the year the loss was incurred' -- the other half of the L6 decoupling."},

    # ── Schedule J computation block, apportionment, and the other schedules ──
    {"fact_key": "j_l35_apportionment_ratio", "label": "Sch. J L35 Excise tax apportionment ratio (Schedules N, N1, O, P, or R, or 100%)", "data_type": "decimal", "required": False, "sort_order": 220,
     "notes": "On Schedule N the SAME ratio also goes to Schedule F1 Line 4 (franchise). Schedule N1 is the exception -- it produces two DIFFERENT ratios (RED-deferred)."},
    {"fact_key": "sales_factor_tn_receipts", "label": "Schedule N — business gross receipts In Tennessee", "data_type": "decimal", "required": False, "sort_order": 221},
    {"fact_key": "sales_factor_everywhere", "label": "Schedule N — business gross receipts Total Everywhere", "data_type": "decimal", "required": False, "sort_order": 222,
     "notes": "No throwback, no throwout. Destination sourcing for TPP; market-based sourcing for other-than-TPP. Investment interest income is excluded from BOTH numerator and denominator."},
    {"fact_key": "m_l9_net_nonbusiness_earnings", "label": "Schedule M L9 — net nonbusiness earnings after expenses", "data_type": "decimal", "required": False, "sort_order": 230,
     "notes": "Default expense assumptions if not substantiated: 50% of nonbusiness RENTAL earnings, 5% of OTHER nonbusiness earnings (Tenn. Comp. R. & Regs. 1320-06-01-.23(3))."},
    {"fact_key": "u_loss_carryover_available", "label": "Schedule U — Tennessee loss carryover available (15-year, oldest first)", "data_type": "decimal", "required": False, "sort_order": 240,
     "notes": "'Tennessee loss carryover is computed separately from federal loss carryover.' Schedule U prints 15 rows against the 15-year carryforward. Applied POST-apportionment at Sch. J L38."},
    {"fact_key": "f1_l1_net_worth", "label": "Schedule F1 L1 Net worth (total assets less total liabilities), GAAP basis", "data_type": "decimal", "required": False, "sort_order": 250,
     "notes": "GAAP, or the taxpayer's federal tax accounting method if it does not keep GAAP books and that method fairly reflects activity. NOTHING on Schedules J1-J4 feeds this."},
    {"fact_key": "f1_l2_affiliate_indebtedness", "label": "Schedule F1 L2 Indebtedness to or guaranteed by parent or affiliated corporation", "data_type": "decimal", "required": False, "sort_order": 251,
     "notes": "ONE-WAY thin-capitalization add-back (67-4-2107(b), Rule 1320-06-01-.15): 'This amount cannot be a deduction.'"},
    {"fact_key": "f1_l4_franchise_ratio", "label": "Schedule F1 L4 Franchise tax apportionment ratio", "data_type": "decimal", "required": False, "sort_order": 252},
    {"fact_key": "a_l2_schedule_g_total", "label": "Schedule A L2 — Schedule G Line 15 total (property measure; blank unless elected)", "data_type": "decimal", "required": False, "sort_order": 260,
     "notes": "DIRECT ENTRY so that Sch. A Line 3's greater-of is arithmetically live the day Schedule G lands. Schedule G itself is RED-deferred (R1/W4)."},
    {"fact_key": "franchise_proration_factor", "label": "Franchise tax proration factor (short/initial period; 1.0 = none)", "data_type": "decimal", "required": False, "sort_order": 261,
     "notes": "W9. Prorate from formation or the date TN operations began, whichever is first, for TN-formed entities; from the date operations began for foreign entities. NEVER below $100. NOT AT ALL for 52/53-week filers. EXCISE tax is NEVER prorated. Day-count convention: the manual's annualization example uses 365.25 -- confirm with Ken."},
    {"fact_key": "b_l6_recapture_and_cds", "label": "Schedule B L6 Recapture of tax credit (Sch. T L13) and additional excise tax on certified distribution sales", "data_type": "decimal", "required": False, "sort_order": 270,
     "notes": "Both components RED-deferred (R9 Schedule T Part 2 recapture; R10 certified distribution sales -- U5: the kit contains NO schedule computing it and the instruction gives NO formula)."},
    # Credits — Schedule D
    {"fact_key": "d_l1_gross_premiums_credit", "label": "Schedule D L1 Gross Premiums Tax Credit", "data_type": "decimal", "required": False, "sort_order": 280,
     "notes": "Paired with the Sch. J L6 add-back; may be FOREGONE. Excludes the 0.4% TOSHA surcharge."},
    {"fact_key": "d_l2_green_energy_credit", "label": "Schedule D L2 Green Energy Tax Credit (business plans filed before 7/1/2015)", "data_type": "decimal", "required": False, "sort_order": 281,
     "notes": "Tenn. Code Ann. 67-4-2109(m) — THE ONE CREDIT EXEMPT FROM THE SCHEDULE C LINE 8 CAP."},
    {"fact_key": "d_l3_brownfield_credit", "label": "Schedule D L3 Brownfield Property Credits", "data_type": "decimal", "required": False, "sort_order": 282, "notes": "Schedule BP + DOR approval letter. RED-deferred (R8)."},
    {"fact_key": "d_l4_broadband_carryover", "label": "Schedule D L4 Broadband Internet Access Tax Credit carryover", "data_type": "decimal", "required": False, "sort_order": 283, "notes": "Repealed 7/1/2019 — carryover only."},
    {"fact_key": "d_l6_job_tax_credit", "label": "Schedule D L6 Job Tax Credit (Schedule X, Line 46)", "data_type": "decimal", "required": False, "sort_order": 284, "notes": "RED-deferred (R6). U6: Schedule X line map not transcribed."},
    {"fact_key": "d_l7_addl_job_tax_credit", "label": "Schedule D L7 Additional Annual Job Tax Credit (Schedule X, Line 38)", "data_type": "decimal", "required": False, "sort_order": 285, "notes": "RED-deferred (R6)."},
    {"fact_key": "d_l8_qualified_production_credit", "label": "Schedule D L8 Qualified Production Credit (Schedule QP, Line 12)", "data_type": "decimal", "required": False, "sort_order": 286, "notes": "RED-deferred (R7)."},
    {"fact_key": "d_l9_paid_family_leave_credit", "label": "Schedule D L9 Employer Credit for Paid Family and Medical Leave (Schedule PL, Line 7)", "data_type": "decimal", "required": False, "sort_order": 287,
     "notes": "CARRYFORWARD-ONLY on the TY2025 form — the credit expired for tax years ending on/after 12/31/2025; established credits carry forward 25 years."},
    # Schedule T Part 1
    {"fact_key": "t_l1_machinery_purchase_price", "label": "Schedule T L1 Industrial machinery / R&D equipment purchase price", "data_type": "decimal", "required": False, "sort_order": 290},
    {"fact_key": "t_l2_credit_percentage", "label": "Schedule T L2 Percentage allowed (generally 1%)", "data_type": "decimal", "required": False, "sort_order": 291,
     "notes": "Enhanced by approved capital investment (67-4-2009(3)(I)): $100M -> 3%, $250M -> 5%, $500M -> 7%, $1B -> 10%."},
    {"fact_key": "v_credit_carryover", "label": "Schedule V — industrial machinery credit carryover (25-year)", "data_type": "decimal", "required": False, "sort_order": 292,
     "notes": "Data-capture note: Schedule V is PRINTED WITH 18 ROWS against a 25-year carryforward. Not a defect, but the capture surface must not be sized off the printed rows."},
    # Payments, penalties, prior-year figures
    {"fact_key": "e_l1_prior_year_overpayment", "label": "Schedule E L1 Overpayment from previous year", "data_type": "decimal", "required": False, "sort_order": 300},
    {"fact_key": "e_estimated_payments", "label": "Schedule E L2b-L5b Estimated payments made", "data_type": "decimal", "required": False, "sort_order": 301},
    {"fact_key": "e_l6_extension_payment", "label": "Schedule E L6 Extension payment", "data_type": "decimal", "required": False, "sort_order": 302},
    {"fact_key": "c_l12_l15_penalty_interest", "label": "Schedule C L12-L15 Penalty and interest (incl. estimated-payment penalty and interest)", "data_type": "decimal", "required": False, "sort_order": 303,
     "notes": "Delinquency 5% per 30-day period, max 25%, minimum $15 (67-1-804). Estimated-payment penalty 2%/month to 24%. Interest per 67-1-801."},
    {"fact_key": "prior_year_total_liability", "label": "Prior year total franchise & excise liability after credits", "data_type": "decimal", "required": False, "sort_order": 304,
     "notes": "Drives BOTH the $5,000 estimate test (annualized if the prior period was short) and the 100%-of-prior extension leg. If ZERO, the required extension payment is $100."},
    {"fact_key": "projected_current_liability", "label": "Projected current year franchise & excise liability after credits", "data_type": "decimal", "required": False, "sort_order": 305},
    {"fact_key": "h_l1_gross_receipts", "label": "Schedule H L1 Gross receipts or sales per federal income tax return", "data_type": "decimal", "required": False, "sort_order": 310,
     "notes": "Form 1120/1120S/1065 Line 1a, or Schedule C Line 1 on Form 1040. INFORMATIONAL — feeds nothing on the return; a reporting/nexus datapoint."},
    {"fact_key": "federal_4562_bonus_total", "label": "Federal bonus depreciation (Form 4562 Part II Line 14 + Part V Line 25)", "data_type": "decimal", "required": False, "sort_order": 320,
     "notes": "GATE for the W3 diagnostic: if this is non-zero and Sch. J L3 is blank, the preparer has almost certainly missed the Tennessee bonus add-back. v1 does NOT compute the TN basis."},
    {"fact_key": "has_post_2022_obbba_differential", "label": "Any post-2022 asset where federal OBBBA bonus exceeds the TN TCJA-allowable amount?", "data_type": "boolean", "required": False, "sort_order": 321,
     "notes": "R13 / U1 / W2 trigger. RED until the DOR ruling lands — the spec must not pick a Schedule J line for the differential."},
]


TN170_RULES: list[dict] = [
    # ── Filing scope and routing ───────────────────────────────────────────
    {"rule_id": "R-TN-FILING", "title": "Who files FAE170 — the LIMITED-LIABILITY imposition test", "rule_type": "routing",
     "formula": ("subject = is_limited_liability_entity ; "
                 "NOT subject: sole proprietorships, general partnerships (no limited liability) ; "
                 "disregarded entities ARE subject EXCEPT an SMLLC whose single member is a CORPORATION "
                 "or which is wholly owned by a PENSION TRUST ; "
                 "not-for-profits are subject ONLY on UBTI (990-T L5 -> J4 L3) and the net worth attributable to it ; "
                 "if is_financial_institution: FILE FAE174 INSTEAD OF FAE170 (hard stop) ; "
                 "if exemption_claimed in the 10 starred exemptions: FAE183 required annually"),
     "inputs": ["is_limited_liability_entity", "federal_entity_type", "is_financial_institution",
                "exemption_claimed", "is_tennessee_domestic"],
     "outputs": ["files_fae170", "files_fae174", "fae183_required"], "sort_order": 1,
     "description": "THE STRUCTURAL DIFFERENCE FROM AN INCOME-TAX STATE. The test is whether the entity confers "
                    "limited liability on its owners, NOT how it is classified federally. LLCs, LPs, LLPs, S corps, "
                    "business trusts and individual-owned SMLLCs are all FAE170 taxpayers in their own right. There is "
                    "no owner-level credit and no pass-through of the tax, because there is no owner-level tax. "
                    "17 exemptions at 67-4-2008; 10 require FAE183 (RED-deferred R12). PC 455 (2025) agricultural-"
                    "cooperative subsidiaries are NOT an 18th exemption — they are not taxpayers at all. "
                    "Exemption eligibility follows STATE-LAW organizational form, not the federal election (one "
                    "exception: asset-backed securitization DOES look to federal classification).",
     "notes": "Nexus bright-line: TN receipts > lesser of $500,000 or 25%; TN property > lesser of $50,000 or 25%; "
              "TN compensation > lesser of $50,000 or 25%. A TN-domestic entity is ALWAYS subject and owes the $100 minimum."},
    {"rule_id": "R-TN-MODES", "title": "Filing modes — inactive page-1-only and P.L. 86-272 franchise-only", "rule_type": "conditional",
     "formula": ("if is_inactive_entity and only the minimum tax is owed: file PAGE ONE ONLY, franchise = $100, "
                 "omit the remaining pages ; "
                 "if pl_86_272_claimed (checkbox c): EXCISE tax not imposed, but the taxpayer STILL FILES FAE170 "
                 "and completes the FRANCHISE tax schedules"),
     "inputs": ["is_inactive_entity", "pl_86_272_claimed"], "outputs": ["filing_mode"], "sort_order": 2,
     "description": "Two real filing modes verbatim on the instructions. P.L. 86-272 protects against the EXCISE tax "
                    "ONLY — it never removes the franchise obligation, and the $100 minimum still applies.",
     "notes": "An inactive-but-registered entity, and one whose charter has been revoked but not dissolved, still owes the $100 minimum."},

    # ── The four Schedule J entry points ───────────────────────────────────
    {"rule_id": "R-TN-J1", "title": "Schedule J1 — partnerships (federal 1065) → Sch. J Line 1", "rule_type": "calculation",
     "formula": ("J1_L4 = J1_L1 + J1_L2 + J1_L3 ; "
                 "J1_L10 = J1_L5 + J1_L6 + J1_L7 + J1_L8 + J1_L9 ; "
                 "J1_L11 = J1_L4 - J1_L10  -> Schedule J, Line 1"),
     "inputs": ["j1_l1_ordinary_income_1065_l23", "j1_l2_allocated_income", "j1_l3_reit_loss_distributed",
                "j1_l5_allocated_expense", "j1_l6_self_employment", "j1_l7_qualified_plan",
                "j1_l8_reit_gain_distributed", "j1_l9_loss_asset_sold_12mo"],
     "outputs": ["J1-4", "J1-10", "J1-11"], "sort_order": 10,
     "description": "L1 = federal Form 1065 Line 23. L2 = Sch. K Lines 2-11 (exclude L11 §743(b) code F; include the "
                    "§179-disposition gain at box 20 code L). L5 = Sch. K Lines 12 and 13a-e (exclude L13 §743(b) code V; "
                    "exclude qualified-plan contributions, which go to L7). **L6 (self-employment) and L7 (qualified "
                    "pension) EXIST ONLY HERE** — see R-TN-J3. Both are loss-limited and both are reversed on Schedule K "
                    "Line 3. L6 is net of pass-through expense deducted elsewhere, such as §179 expense AND CONTRIBUTIONS "
                    "DEDUCTED ON LINE 5.",
     "notes": "§179 PRO-FORMA: the disposition gain/loss on L2 and L5 is recomputed at the PARTNERSHIP level with "
              "partner-level §179 limits DISREGARDED — an entity-level recomputation with no federal analogue."},
    {"rule_id": "R-TN-J2", "title": "Schedule J2 — individual-owned SMLLC (federal 1040) → Sch. J Line 1", "rule_type": "calculation",
     "formula": ("J2_L7 = J2_L1 + J2_L2 + J2_L3 + J2_L4 + J2_L5 + J2_L6 ; "
                 "J2_L9 = J2_L7 - J2_L8  -> Schedule J, Line 1"),
     "inputs": ["j2_l1_schedule_c", "j2_l2_schedule_d", "j2_l3_schedule_e", "j2_l4_schedule_f",
                "j2_l5_form_4797", "j2_l6_other", "j2_l8_self_employment"],
     "outputs": ["J2-7", "J2-9"], "sort_order": 11,
     "description": "THE 'no individual income tax != no individual filing' TRAP. Tennessee has no individual income "
                    "tax, yet an SMLLC owned by a natural person is an FAE170 taxpayer in its own right. ⚠ The FORM FACE "
                    "carries NO federal line numbers (verification C5); only the instructions give Sch. C L31 and Sch. F "
                    "L34, and Sch. D / Sch. E / Form 4797 get NO line number from either document. L2 is entered as a "
                    "NEGATIVE if it is a loss. L8 carries the same loss limit and the same Schedule K Line 3 add-back as J1 L6.",
     "notes": "W10 — where the trigger lives relative to the 1040 module is a CLIENT-EXPOSURE question, not just a spec question. "
              "A 1040 client with a TN SMLLC owes an FAE170 that no 1040 workflow will surface."},
    {"rule_id": "R-TN-J3", "title": "Schedule J3 — S corporations (1120S) → Sch. J L1 — NO SE / NO PENSION", "rule_type": "calculation",
     "formula": ("J3_L3 = J3_L1 + J3_L2 ; "
                 "J3_L6 = J3_L4 + J3_L5           <-- THE COMPLETE DEDUCTION LIST ; "
                 "J3_L7 = J3_L3 - J3_L6  -> Schedule J, Line 1 ; "
                 "**NO self-employment deduction. NO qualified-plan deduction. J1 L6/L7 have NO J3 ANALOGUE.**"),
     "inputs": ["j3_l1_ordinary_income_1120s_l22", "j3_l2_s_status_income",
                "j3_l4_s_status_expense", "j3_l5_loss_asset_sold_12mo"],
     "outputs": ["J3-3", "J3-6", "J3-7"], "sort_order": 12,
     "description": "⚠⚠ THE CLONE TRAP. J3's ONLY deductions are L4 (pass-through expense items) and L5 (12-month "
                    "distribution loss). A partnership gets J1 L6 (self-employment) and L7 (qualified pension) OUT of its "
                    "base; an S corp gets NOTHING equivalent, because shareholder wages are already inside 1120-S Line 22. "
                    "Tennessee therefore taxes the S corp on essentially its full federal K-1 economics. THIS IS THE SINGLE "
                    "LARGEST entity-choice-driven difference in the TN excise base, and cloning J1 into J3 OVERSTATES the "
                    "S-corp deduction — understating tax at 6.5% of the SE + pension figures. Confirmed on the form face AND "
                    "in the line-by-line instructions by the adversarial pass.",
     "exceptions": "There is NO exception. Do not add a self-employment or qualified-plan line to J3 under any circumstance.",
     "notes": "Diagnostic D_TN170_J3_NO_SE_PENSION fires if a J3 return carries an SE or pension figure. "
              "§179 disposition gain at Sch. K box 17 code K, pro forma at the S-corp level, shareholder-level limits disregarded."},
    {"rule_id": "R-TN-J4", "title": "Schedule J4 — corporations and other entities (1120) → Sch. J Line 1", "rule_type": "calculation",
     "formula": ("J4_L2c = J4_L2a - J4_L2b ; "
                 "J4_L7  = J4_L1 + J4_L2c + J4_L3 + J4_L4 + J4_L5 + J4_L6 ; "
                 "J4_L10 = J4_L8 + J4_L9 ; "
                 "J4_L11 = J4_L7 - J4_L10  -> Schedule J, Line 1"),
     "inputs": ["j4_l1_taxable_income_1120_l28", "j4_l2a_reit_taxable_income", "j4_l2b_reit_dividends_paid",
                "j4_l3_ubti_990t", "j4_l4_other_federal_income", "j4_l5_contribution_carryover_used",
                "j4_l6_capital_gains_offset", "j4_l8_contributions_excess", "j4_l9_current_capital_loss"],
     "outputs": ["J4-2c", "J4-7", "J4-10", "J4-11"], "sort_order": 13,
     "description": "⚠ LINES 5/6/8/9 ARE A FULL CONTRIBUTIONS-AND-CAPITAL-LOSS TIMING DECOUPLING — a SECOND "
                    "Tennessee-basis ledger, distinct from the depreciation one. Tennessee allows charitable "
                    "contributions and capital losses IN FULL IN THE YEAR INCURRED (L8, L9) and therefore REVERSES every "
                    "federal carryover/carryback when the federal return uses it (L5, L6). The app must carry a SEPARATE "
                    "TENNESSEE contribution and capital-loss HISTORY per C-corp. J4 is also the NONPROFIT path (990-T "
                    "Line 5 on L3) and the REIT path (1120-REIT Lines 21 / 22b).",
     "notes": "TN is a SEPARATE-ENTITY state: a member of a federal consolidated group must build a PRO FORMA Form 1120, "
              "optionally using the Excise Tax Interest Expense Worksheet for its share of the group's interest deduction."},
    {"rule_id": "R-TN-J-ENTRY", "title": "Schedule J Line 1 — the four entry points converge", "rule_type": "routing",
     "formula": ("J_L1 = {1065: J1_L11, 1040_smllc: J2_L9, 1120S: J3_L7, 1120: J4_L11}[federal_entity_type] ; "
                 "instruction verbatim: 'Enter the applicable amount from line 11, 9, 7, or 11 of Schedule J1, J2, J3, or J4, respectively.'"),
     "inputs": ["federal_entity_type"], "outputs": ["J-1"], "sort_order": 14,
     "description": "THE DEFINING STRUCTURAL FACT. Tennessee has ONE return whose net-earnings starting point branches "
                    "on federal classification and then converges on a SINGLE Schedule J. This is why one RS spec covers "
                    "three delvio-tax modules. Note the totals sit on DIFFERENT line numbers per schedule — 11, 9, 7, 11 — "
                    "which is exactly the order the instruction recites.",
     "notes": "Only ONE entry schedule is completed per return."},

    # ── Schedule J — modifications and the ordering ────────────────────────
    {"rule_id": "R-TN-J-SUBTOT", "title": "Schedule J subtotals L15 and L30 (L28b EXCLUDED)", "rule_type": "calculation",
     "formula": ("J_L15 = sum(J_L2 .. J_L14)                          [13 addition lines] ; "
                 "J_L30 = sum(J_L16 .. J_L29) EXCLUDING J_L28b        [14 deduction lines, 15 fields] ; "
                 "verbatim: 'Total deductions (add Lines 16 through 29, excluding 28b)'"),
     "inputs": [f[1] for f in J_ADDITIONS] + [f[1] for f in J_DEDUCTIONS],
     "outputs": ["J-15", "J-30"], "sort_order": 20,
     "description": "27 NUMBERED modification lines (2-14 = 13 additions; 16-29 = 14 deductions) but 28 ENTRY FIELDS, "
                    "because Line 28 splits into 28a/28b. ⚠ **L28b IS INFORMATIONAL ONLY AND IS EXCLUDED FROM L30** — a "
                    "spec that sums 16..29 inclusive overstates the deduction. Every modification AMOUNT is DIRECT-ENTRY "
                    "in v1; the engine owns the subtotals and the flow. Several lines may legitimately be NEGATIVE: L5 "
                    "(excise-tax over-accrual reversal), L10 (the recipient affiliate), L17 (basis difference), and L21 "
                    "(safe harbor lease — 'If the net adjustment is an increase in taxable income, enter a negative number').",
     "notes": "GILTI pairing: L27 deducts the FULL §951A amount and L12 adds back 5%, so a NET 5% is taxed and the §250 "
              "deduction is NOT allowed. §174 pairing: L14 adds back, L29 deducts in full. Business interest: L13 adds "
              "back, L28a deducts (NOT 'L27a' — U4 erratum)."},
    {"rule_id": "R-TN-J-ORDER", "title": "Schedule J L31-L39 — $50k PRE-apportionment, nonbusiness POST, NOL LAST", "rule_type": "calculation",
     "formula": ("J_L31 = J_L1 + J_L15 - J_L30 ; "
                 "J_L32 = max(0, min(J_L31, 50000))            <-- **PRE-APPORTIONMENT** ; "
                 "J_L34 = J_L31 - J_L32 + J_L33 ; "
                 "J_L36 = J_L34 * J_L35                        <-- apportionment happens HERE ; "
                 "J_L37 = Schedule M L11                       <-- **POST-APPORTIONMENT**, allocated, taxed at full 6.5% ; "
                 "J_L38 = Schedule U carryover                 <-- **LAST** ; "
                 "J_L39 = J_L36 + J_L37 - J_L38  -> Schedule B, Line 4"),
     "inputs": ["j_l33_optional_addback", "j_l35_apportionment_ratio", "m_l9_net_nonbusiness_earnings",
                "u_loss_carryover_available"],
     "outputs": ["J-31", "J-32", "J-34", "J-36", "J-37", "J-38", "J-39"], "sort_order": 21,
     "description": "⚠⚠ **APPORTION-FIRST IS WRONG** — confirmed by the adversarial pass against the form face p. 5 and "
                    "instructions pp. 9-10. The $50,000 standard deduction sits INSIDE L34 and is therefore applied to "
                    "100% of business income BEFORE the ratio; the nonbusiness allocation is added AFTER the ratio; and "
                    "the NOL comes off last. On a 30% apportionment ratio the two orderings differ by $50,000 x (1 - "
                    "0.30) = $35,000 of base, i.e. $2,275 of tax. The standard deduction cannot create or increase a "
                    "loss, cannot be carried forward, and is ONE PER RETURN; its unused portion spills to Schedule M L10.",
     "exceptions": "L33 (PC 343 (2025), §67-4-2006(c)(10)) is TAXPAYER-ELECTIVE and discretionary — it may be made, "
                   "adjusted, or removed on any timely filed original or amended return. It is never engine-imposed.",
     "notes": "L35 comes from Schedule N (computed), or N1/O/P/R (all RED-deferred), or 100%."},
    {"rule_id": "R-TN-SCHM", "title": "Schedule M — nonbusiness earnings and the spillover standard deduction", "rule_type": "calculation",
     "formula": ("M_L8 -> Schedule J L22 (removes nonbusiness earnings from the apportioned base) ; "
                 "M_L10 = max(0, min(50000 - J_L32, M_L9))   'cannot exceed Line 9', never negative ; "
                 "M_L11 = M_L9 - M_L10 -> Schedule J L37"),
     "inputs": ["m_l9_net_nonbusiness_earnings"], "outputs": ["M-8", "M-10", "M-11"], "sort_order": 22,
     "description": "Nonbusiness earnings are ALLOCATED, not apportioned, and are taxed at the full 6.5%. The UNUSED "
                    "portion of the $50,000 standard deduction offsets them here. Default expense assumptions where not "
                    "substantiated: 50% of nonbusiness RENTAL earnings, 5% of OTHER nonbusiness earnings (Tenn. Comp. R. "
                    "& Regs. 1320-06-01-.23(3)). The manual notes income meeting the statutory nonbusiness definition is uncommon.",
     "notes": "Sch. M detail rows are DIRECT-ENTRY with the 50%/5% defaults offered."},
    {"rule_id": "R-TN-SCHK", "title": "Schedule K — loss carryover available (FOUR reversals, never creates income)", "rule_type": "calculation",
     "formula": ("K_L1 = net loss from Schedule J L31 ; "
                 "K_L2 = Schedule J Lines 18 + 22 + 33 ; "
                 "K_L3 = Schedule J1 Lines 6 and 7, OR Schedule J2 Line 8 ; "
                 "K_L4 = K_L1 + K_L2 + K_L3 ; **if the net amount is POSITIVE, enter ZERO** ; "
                 "K_L6 = K_L4 * K_L5 (apportionment ratio)"),
     "inputs": ["j_l18_dividends_80pct_owned", "j_l22_nonbusiness_earnings", "j_l33_optional_addback",
                "j1_l6_self_employment", "j1_l7_qualified_plan", "j2_l8_self_employment"],
     "outputs": ["K-4", "K-6"], "sort_order": 23,
     "description": "⚠ THE NOL IS NOT SIMPLY SCHEDULE J LINE 31. Four specific deductions are REVERSED before "
                    "apportioning: 80%-owned dividends (J L18), nonbusiness earnings (J L22), the optional addback "
                    "(J L33), and the SE/qualified-plan deductions (J1 L6+L7 or J2 L8). Manual p. 298: 'These reversals "
                    "(add-backs) should never turn an apportioned business loss ... into income' — hence the "
                    "positive-to-zero floor on L4. Note J3 and J4 contribute NOTHING to K L3: they have no SE or pension line.",
     "notes": "Discharge-of-indebtedness reduction under §67-4-2006(c)(8) applies to the carryover for bankruptcy discharges on/after 10/1/2013."},
    {"rule_id": "R-TN-SCHU", "title": "Schedule U — 15-year Tennessee loss carryover, oldest first", "rule_type": "calculation",
     "formula": "J_L38 = sum of available Schedule U carryovers, consumed OLDEST FIRST, 15-year expiry",
     "inputs": ["u_loss_carryover_available"], "outputs": ["J-38"], "sort_order": 24,
     "description": "'Tennessee loss carryover is computed separately from federal loss carryover.' 15-year "
                    "carryforward, oldest first, applied POST-apportionment at Schedule J Line 38. Prior-year loss rows "
                    "are DIRECT-ENTRY in v1.",
     "notes": "Contrast Schedule V, where industrial-machinery and several job credits carry forward 25 years."},

    # ── Apportionment ──────────────────────────────────────────────────────
    {"rule_id": "R-TN-SCHN", "title": "Schedule N — single sales factor, ONE ratio to BOTH taxes", "rule_type": "calculation",
     "formula": ("ratio = sales_factor_tn_receipts / sales_factor_everywhere  (or 100% if the denominator is zero) ; "
                 "the SAME ratio -> Schedule F1 Line 4 (FRANCHISE) and Schedule J Line 35 (EXCISE)"),
     "inputs": ["sales_factor_tn_receipts", "sales_factor_everywhere"],
     "outputs": ["N-1", "F1-4", "J-35"], "sort_order": 30,
     "description": "⚠ The ENTIRE TY2025 Schedule N is ONE LINE. There is NO property line, NO payroll line and NO "
                    "11x/13 divisor anywhere on the TY2025 form — that formula lives on the TY2024 form, which a fiscal "
                    "filer ending 6/30/2025 (period beginning 7/1/2024) actually files. Selection of the apportionment "
                    "row keys on period END date; 52/53-week filers conform to the nearest calendar year end. NO "
                    "THROWBACK and NO THROWOUT. Destination sourcing for TPP; market-based sourcing for other-than-TPP.",
     "exceptions": "Carve-outs keep their prescribed formulas and are ALL RED-deferred in v1: common carriers (Sch. O), "
                   "air carriers (P), air express carriers (R), the elective/mandatory three-factor family (N1), "
                   "financial institutions and FI unitary groups and captive REITs (FAE174). A captive REIT keeps "
                   "three-factor for EXCISE but single sales factor for FRANCHISE — so the two ratios can differ for one taxpayer.",
     "notes": "U3: a SHORT period beginning on/after 1/1/2025 and ending before 12/31/2025 statutorily falls in the "
              "11x/13 row that this one-line schedule cannot express. Unresolved DOR edge case."},

    # ── Franchise tax ──────────────────────────────────────────────────────
    {"rule_id": "R-TN-F1", "title": "Schedule F1 — non-consolidated net worth (GAAP) → Sch. A Line 1", "rule_type": "calculation",
     "formula": ("F1_L3 = F1_L1 + F1_L2   (L2 is a ONE-WAY add-back: 'This amount cannot be a deduction') ; "
                 "F1_L5 = F1_L3 * F1_L4 ; if is_manufacturer: F1_L5 = min(F1_L5, 2000000000) ; "
                 "F1_L5 -> Schedule A, Line 1"),
     "inputs": ["f1_l1_net_worth", "f1_l2_affiliate_indebtedness", "f1_l4_franchise_ratio", "is_manufacturer"],
     "outputs": ["F1-3", "F1-5", "A-1"], "sort_order": 40,
     "description": "⚠ THE DATA-CAPTURE SURFACE THE 1065/1120S/1120 MODULES DO NOT OTHERWISE HAVE. Net worth is total "
                    "assets less total liabilities on a GAAP BALANCE SHEET (or the taxpayer's federal tax accounting "
                    "method if it does not keep GAAP books and that method fairly reflects activity). NOTHING on "
                    "Schedules J1-J4 feeds it. The federal handoff is one-directional and LOSSY: any 'import the federal "
                    "return and TN computes' design covers only the EXCISE half of FAE170. L2 is the thin-capitalization "
                    "add-back under §67-4-2107(b) / Rule 1320-06-01-.15. The $2 BILLION manufacturer cap is §67-4-2121.",
     "notes": "Schedule F2 (consolidated net worth) is RED-deferred (R2/W5) — it needs the Consolidated Net Worth "
              "Election, a pro forma consolidated GAAP balance sheet, and Schedules 170NC/170NC1/170SF (NOT N/N1/O/P/R). "
              "The election is binding FIVE years; exiting members compute on F1."},
    {"rule_id": "R-TN-A-FRANCH", "title": "Schedule A Line 3 — MAX(L1, L2) x 0.25%, $100 minimum", "rule_type": "calculation",
     "formula": ("base  = MAX(A_L1, A_L2)                                <-- **LIVE GREATER-OF** ; "
                 "units = floor(base/100) + (1 if base%100 > 50 else 0)   <-- 'or major fraction thereof' ; "
                 "tax   = units * $0.25 ; "
                 "if not is_5253_week_filer: tax = tax * franchise_proration_factor ; "
                 "A_L3  = max(tax, $100)                                  <-- minimum SURVIVES proration ; "
                 "**NEVER A_L1 * 0.0025**"),
     "inputs": ["a_l2_schedule_g_total", "franchise_proration_factor", "is_5253_week_filer"],
     "outputs": ["A-3"], "sort_order": 41,
     "description": "Verbatim: 'Franchise tax (25c per $100 or major fraction thereof on the greater of Lines 1 or 2; "
                    "minimum $100)'. ⚠ THE GREATER-OF IS LIVE even though Schedule G is opt-in and RED-deferred (W4): "
                    "Line 2 is direct-entry precisely so the arithmetic is right the day Schedule G lands. Do NOT "
                    "collapse Line 3 to a flat rate on Line 1. 'Round to the nearest dollar' heads Schedule A. Franchise "
                    "tax MAY be prorated on short-period and initial returns but NEVER below $100, and NOT AT ALL for "
                    "52/53-week filers. EXCISE tax is NEVER prorated.",
     "notes": "W8 — both the '>50 is a major fraction' rounding and the $100 floor are read off the form's arithmetic, "
              "not from an explicit DOR statement. They silently change every small return. Ken to bless. "
              "The $100 minimum is owed by ANY registered entity, including an inactive one and one whose charter has "
              "been revoked but not dissolved (§67-4-2119)."},

    # ── Excise tax and the total ───────────────────────────────────────────
    {"rule_id": "R-TN-B-EXCISE", "title": "Schedule B — excise tax at 6.5% of Schedule J Line 39", "rule_type": "calculation",
     "formula": ("B_L4 = Schedule J, Line 39 ; "
                 "B_L5 = max(0, B_L4) * 6.5%    ('If Line 4 is a loss, enter zero.') ; "
                 "B_L7 = B_L5 + B_L6"),
     "inputs": ["b_l6_recapture_and_cds"], "outputs": ["B-4", "B-5", "B-7"], "sort_order": 50,
     "description": "6.5% per Tenn. Code Ann. §67-4-2007 (rate set by 2002 Tenn. Pub. Ch. 856). ⚠ A LOSS YEAR PRODUCES "
                    "ZERO EXCISE TAX BUT THE $100 MINIMUM FRANCHISE TAX IS STILL DUE — the two taxes share no base and "
                    "neither floors the other.",
     "notes": "L6 carries BOTH Schedule T Line 13 recapture (R9) and the additional excise tax on certified distribution "
              "sales (R10 / U5 — the kit contains no schedule computing it and the instruction gives no formula). Both RED-deferred."},
    {"rule_id": "R-TN-C-TOTAL", "title": "Schedule C — total tax, the credit cap, and the Green Energy exception", "rule_type": "calculation",
     "formula": ("C_L8  = A_L3 + B_L7 ; "
                 "C_L9  = min(non_green_credits, C_L8) + green_energy_credit   <-- ONE HOLE IN THE CAP ; "
                 "C_L10 = max(0, C_L8 - C_L9) ; "
                 "C_L16 = C_L10 + C_L12 + C_L13 + C_L14 + C_L15 - C_L11 ; "
                 "C_L16 < 0 -> overpayment: election box A (credit to next year) or B (refund)"),
     "inputs": ["d_l1_gross_premiums_credit", "d_l2_green_energy_credit", "d_l3_brownfield_credit",
                "d_l4_broadband_carryover", "d_l6_job_tax_credit", "d_l7_addl_job_tax_credit",
                "d_l8_qualified_production_credit", "d_l9_paid_family_leave_credit",
                "c_l12_l15_penalty_interest", "e_l1_prior_year_overpayment", "e_estimated_payments",
                "e_l6_extension_payment"],
     "outputs": ["C-8", "C-9", "C-10", "C-11", "C-16"], "sort_order": 51,
     "description": "The credit cap has EXACTLY ONE HOLE: 'Total credits may not exceed the amount on Schedule C, Line "
                    "8, UNLESS claiming a Green Energy Credit under the provisions of Tenn. Code Ann. §67-4-2109(m).' "
                    "Encoded as non-green credits capped at L8 with the Green Energy Credit riding on top uncapped — "
                    "⚠ that split is the SPEC'S READING of a terse sentence, not DOR mechanics.",
     "exceptions": "⚠ U8 / W8 — because L9 is capped only at L8 and L10 floors at ZERO, a large credit reduces net tax "
                   "to zero, THE $100 FRANCHISE MINIMUM INCLUDED. No DOR statement exists either way. The spec follows "
                   "the form's arithmetic; KEN MUST BLESS THIS rather than the spec assuming it.",
     "notes": "A refund of $200 or more requested on an amended return requires a Report of Debts form."},
    {"rule_id": "R-TN-SCHT1", "title": "Schedule T Part 1 — industrial machinery / R&D credit (least of L5, L7, L10)", "rule_type": "calculation",
     "formula": ("T_L3  = T_L1 * T_L2  (generally 1%; enhanced 3/5/7/10% by approved capital investment) ; "
                 "T_L5  = T_L3 + T_L4 (Schedule V carryover) ; "
                 "T_L6  = Schedule A Line 3 + Schedule B **Line 5**  (pre-credit liability; NOT Line 7) ; "
                 "T_L7  = 50% of T_L6 ; T_L8 = T_L6 ; T_L9 = Schedule D Lines 1-4 and Line 7 ; T_L10 = T_L8 - T_L9 ; "
                 "T_L11 = min(T_L5, T_L7, T_L10) -> Schedule D, Line 5"),
     "inputs": ["t_l1_machinery_purchase_price", "t_l2_credit_percentage", "v_credit_carryover"],
     "outputs": ["T-11", "D-5"], "sort_order": 52,
     "description": "The one credit v1 COMPUTES (W7). Enhanced rates by approved capital investment (§67-4-2009(3)(I)): "
                    "$100M -> 3%, $250M -> 5%, $500M -> 7%, $1B -> 10%. Carryforward 25 years on Schedule V. Note the "
                    "credit ORDERING: L9 subtracts Schedule D Lines 1-4 and Line 7, so this credit sits behind them.",
     "notes": "Part 2 (recapture on sale or removal from Tennessee before the end of the federal useful life, L12 "
              "reducing the Schedule V carryover and L13 feeding Schedule B Line 6) is RED-deferred (R9)."},

    # ── Estimates, extension, informational ────────────────────────────────
    {"rule_id": "R-TN-ESTIM", "title": "Schedule E — the $5,000-BOTH-YEARS test and standard-method installments", "rule_type": "calculation",
     "formula": ("required = (prior_year_total_liability >= 5000) AND (projected_current_liability >= 5000) ; "
                 "  [a SHORT PRIOR period is ANNUALIZED for the test; the current year is NOT] ; "
                 "installment = min(25% * prior_year_total_liability, 25% * 80% * projected_current_liability) ; "
                 "due: the 15th day of the 4th, 6th and 9th month of the current taxable year, and the 1st month "
                 "of the SUBSEQUENT taxable year ; "
                 "E_L7 = E_L1 + installments paid + E_L6 -> Schedule C, Line 11"),
     "inputs": ["prior_year_total_liability", "projected_current_liability", "e_l1_prior_year_overpayment",
                "e_estimated_payments", "e_l6_extension_payment", "is_short_period"],
     "outputs": ["E-7", "C-11"], "sort_order": 60,
     "description": "BOTH years must clear $5,000 AFTER CREDITS — a single big year does not trigger estimates. "
                    "Any taxpayer owing $2,500 or more on a quarterly estimated payment must remit in IMMEDIATELY "
                    "AVAILABLE FUNDS. Estimated-payment penalty is 2% per month to a 24% maximum.",
     "notes": "The ANNUALIZED INCOME INSTALLMENT METHOD (checkbox f) is RED-deferred (R11): annual election, original "
              "return only, franchise and excise components computed separately, the excise component per IRC §6655(e)(2)."},
    {"rule_id": "R-TN-EXTEND", "title": "FAE173 — seven-month extension, lesser of 90% current / 100% prior, $100 floor case", "rule_type": "validation",
     "formula": ("required_payment = $100 if prior_year_total_liability == 0 "
                 "else min(90% * current_liability, 100% * prior_year_total_liability) ; "
                 "  [prior year ANNUALIZED if it was short] ; "
                 "granted if the request AND the payment are in by the ORIGINAL due date ; "
                 "AUTOMATIC (no form) if payments already suffice ; extension = SEVEN months"),
     "inputs": ["prior_year_total_liability", "projected_current_liability", "federal_extension_filed"],
     "outputs": ["extension_granted", "extension_payment_required"], "sort_order": 61,
     "description": "'The filing extension is not a payment extension' — interest runs from the ORIGINAL due date. "
                    "Missing the payment threshold or the extended due date VOIDS the extension retroactively. Return due "
                    "date: the 15th day of the 4th month following the period end shown on the CORRESPONDING FEDERAL "
                    "RETURN; the TN period must coincide with the federal one. 52/53-week filers use the month CLOSEST to "
                    "the year end (12/28 and 1/2 both -> April 15). Electronic perfection period: 10 calendar days after a rejection.",
     "notes": "E-file is MANDATORY unless a hardship exemption has been received (no computer, no internet, or religious objection)."},
    {"rule_id": "R-TN-SCHH", "title": "Schedule H — gross receipts (informational)", "rule_type": "calculation",
     "formula": "H_L1 = federal Form 1120 / 1120S / 1065 Line 1a, or Form 1040 Schedule C Line 1",
     "inputs": ["h_l1_gross_receipts"], "outputs": ["H-1"], "sort_order": 62,
     "description": "Feeds NOTHING on the return — a reporting and nexus datapoint only.",
     "notes": "Do not wire Schedule H into any computation."},

    # ── Depreciation regimes (structure encoded; the KEY is deliberately absent) ──
    {"rule_id": "R-TN-DEPR-REGIME", "title": "The two §168(k) regimes — structure only; NO key, NO computed differential", "rule_type": "classification",
     "formula": ("REGIME A — assets purchased ON OR BEFORE 12/31/2022: federal bonus FULLY DISALLOWED. "
                 "Add back on Sch. J L3; deduct the TN-basis depreciation actually permitted on L16; "
                 "disposition true-up on L17. Does NOT expire — runs out asset by asset. ; "
                 "REGIME B — assets purchased ON OR AFTER 1/1/2023: TN remains coupled to the TCJA §168(k), "
                 "PERMANENTLY FROZEN: 80% (2023) / 60% (2024) / **40% (2025)** / 20% (2026) / 0% (2027+). ; "
                 "⚠ **NO RULE HERE DERIVES THE YEAR-KEY (acquired vs placed in service) — W1/U2, KEN'S CALL.** ; "
                 "⚠ **NO RULE HERE COMPUTES THE OBBBA DIFFERENTIAL — W2/U1, RED-DEFERRED (R13).** ; "
                 "§179: CONFORMS at the full OBBBA $2,500,000 / $4,000,000, indexed. NO state limit, NO add-back."),
     "inputs": ["federal_4562_bonus_total", "has_post_2022_obbba_differential"],
     "outputs": ["depreciation_regime"], "sort_order": 70,
     "description": "Two SIMULTANEOUS regimes, each generating disposition true-ups, and the app must carry a SEPARATE "
                    "TENNESSEE ASSET BASIS. v1 does NOT build the engine (W3): Schedule J Lines 3, 16 and 17 are "
                    "DIRECT-ENTRY, with a hard diagnostic when Form 4562 Part II Line 14 or Part V Line 25 is non-zero "
                    "and Line 3 is blank. ⚠ The two OBBBA depreciation provisions split in OPPOSITE directions: §179 "
                    "CONFORMS, §168(k) does NOT. §168(n) qualified production property gets ZERO Tennessee bonus and is "
                    "depreciated as MACRS nonresidential real property. OBBBA 100% bonus is NOT available in Tennessee "
                    "for TY2025 — a TY2025 asset can generate a 60-POINT add-back plus ongoing MACRS recovery of the "
                    "differential.",
     "exceptions": "⚠⚠ THE KEY IS UNRESOLVED. Manual p. 225 captions the phase-down table 'Asset Acquired Between:' "
                   "while p. 267 keys the same 40/20/0 to property 'placed in service'; the form and instructions say "
                   "'purchased'; and p. 267 uses BOTH keys in one sentence (federal 'acquired' after 1/19/2025 vs "
                   "Tennessee 'placed in service' in 2025). These diverge for an asset acquired 2024 / placed in service "
                   "2025 — 60% vs 40% — and the key also decides which regime an asset falls into. THIS CHANGES NUMBERS "
                   "ON REAL RETURNS. Escalated as GATE1_WALK item 3 and walk item W1. The helper `_tn_tcja_bonus_pct` "
                   "takes a caller-supplied year and refuses to derive one.",
     "notes": "W2/U1: which Schedule J lines carry the post-2022 OBBBA differential is unreconciled by the DOR. Working "
              "assumption is L3/L16/L17 for both regimes (there is no other line), but v1 RED-DEFERS the differential "
              "rather than guessing. Federal bonus is located at Form 4562 Part II Line 14 and Part V Line 25."},
]

TN170_RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R-TN-FILING", "TN_FE_MANUAL_DEC2025", "primary", "imposition test p. 17; 17 exemptions and the 10 FAE183 stars pp. 26-28; FI >50% test p. 55"),
    ("R-TN-FILING", "TN_TCA_67_4_2004_IRC_DEF", "secondary", "'person or taxpayer' at (36); general partnership at (19); not-for-profit at (32)"),
    ("R-TN-MODES", "TN_2025_FAE170_INSTR", "primary", "inactive page-1-only mode and the P.L. 86-272 franchise-only mode, verbatim"),
    ("R-TN-J1", "TN_2025_FAE170_FORM", "primary", "Schedule J1 line map and the L6/L7 deduction lines, form face"),
    ("R-TN-J1", "TN_2025_FAE170_INSTR", "primary", "Sch. K line ranges, the §743(b) exclusions, and the §179 pro-forma rule"),
    ("R-TN-J1", "IRS_2025_1065_INSTR", "secondary", "federal Form 1065 Line 23 and Sch. K Lines 2-11 / 12-13a-e verified on the FINAL 2025 form"),
    ("R-TN-J2", "TN_2025_FAE170_FORM", "primary", "Schedule J2 face labels carry NO federal line numbers (verification C5)"),
    ("R-TN-J2", "TN_2025_FAE170_INSTR", "primary", "Sch. C L31 and Sch. F L34 appear only in the instructions"),
    ("R-TN-J3", "TN_2025_FAE170_FORM", "primary", "THE CLONE TRAP — J3's complete deduction list is L4 and L5, form face"),
    ("R-TN-J3", "TN_2025_FAE170_INSTR", "primary", "line-by-line instructions confirm J3 has no SE and no qualified-plan line"),
    ("R-TN-J3", "IRS_2025_1120S_INSTR_FULL", "secondary", "federal Form 1120-S Line 22 and Sch. K Lines 2-10 / 11-12e verified on the FINAL 2025 form"),
    ("R-TN-J4", "TN_2025_FAE170_FORM", "primary", "Schedule J4 line map incl. the REIT block and the L5/L6/L8/L9 decoupling"),
    ("R-TN-J4", "TN_2025_FAE170_INSTR", "primary", "the contributions and capital-loss timing rules, verbatim"),
    ("R-TN-J-ENTRY", "TN_2025_FAE170_INSTR", "primary", "'Enter the applicable amount from line 11, 9, 7, or 11 ... respectively'"),
    ("R-TN-J-SUBTOT", "TN_2025_FAE170_FORM", "primary", "L15 and L30 subtotals; 'excluding 28b' on the form face"),
    ("R-TN-J-SUBTOT", "TN_TCA_67_4_2006", "primary", "the statutory decouplings behind the modification lines"),
    ("R-TN-J-SUBTOT", "TN_2025_FAE170_INSTR", "secondary", "per-line instruction detail incl. the L19 75% and the L13/L28a erratum"),
    ("R-TN-J-ORDER", "TN_2025_FAE170_FORM", "primary", "L31-L39 as printed — the $50k inside L34, L37 after L36, L38 last"),
    ("R-TN-J-ORDER", "TN_FE_MANUAL_DEC2025", "primary", "standard deduction and PC 343 optional addback, pp. 257-258"),
    ("R-TN-SCHM", "TN_2025_FAE170_FORM", "primary", "Schedule M L8/L10/L11 and the spillover cap, form face"),
    ("R-TN-SCHK", "TN_FE_MANUAL_DEC2025", "primary", "p. 298 — the reversals never turn an apportioned loss into income"),
    ("R-TN-SCHK", "TN_2025_FAE170_FORM", "secondary", "Schedule K L1-L6 as printed"),
    ("R-TN-SCHU", "TN_FE_MANUAL_DEC2025", "primary", "15-year TN loss carryover computed separately from federal"),
    ("R-TN-SCHN", "TN_2025_FAE170_FORM", "primary", "Schedule N is ONE line; the same ratio to F1 L4 and J L35"),
    ("R-TN-SCHN", "TN_FE_MANUAL_DEC2025", "secondary", "PC 377 (2023) phase-in keyed to period END; no throwback; market sourcing"),
    ("R-TN-F1", "TN_2025_FAE170_INSTR", "primary", "GAAP basis, the one-way L2 add-back, and the $2B manufacturer cap"),
    ("R-TN-F1", "TN_FE_MANUAL_DEC2025", "secondary", "§67-4-2121 manufacturer cap; §67-4-2107(b) thin capitalization"),
    ("R-TN-A-FRANCH", "TN_2025_FAE170_FORM", "primary", "'25c per $100 or major fraction thereof on the greater of Lines 1 or 2; minimum $100'"),
    ("R-TN-A-FRANCH", "TN_2025_FAE170_INSTR", "primary", "proration allowed but not below $100; none for 52/53-week filers"),
    ("R-TN-A-FRANCH", "TN_TCA_67_4_2123", "secondary", "the property measure survives as an election, so the greater-of stays live"),
    ("R-TN-B-EXCISE", "TN_2025_FAE170_FORM", "primary", "'Excise tax (6.5% of Line 4)'; 'If Line 4 is a loss, enter zero.'"),
    ("R-TN-B-EXCISE", "TN_TCA_67_4_2006", "secondary", "net earnings definition under §67-4-2006(a)"),
    ("R-TN-C-TOTAL", "TN_2025_FAE170_FORM", "primary", "Schedule C L8-L16 and the L9 cap as printed"),
    ("R-TN-C-TOTAL", "TN_2025_FAE170_INSTR", "primary", "the Green Energy exception to the Schedule C Line 8 cap"),
    ("R-TN-SCHT1", "TN_2025_FAE170_FORM", "primary", "Schedule T Part 1 L1-L11 as printed"),
    ("R-TN-SCHT1", "TN_FE_MANUAL_DEC2025", "secondary", "enhanced rates §67-4-2009(3)(I); 25-year Schedule V carryforward"),
    ("R-TN-ESTIM", "TN_FE_MANUAL_DEC2025", "primary", "pp. 108-110 — the $5,000-both-years test and the standard method"),
    ("R-TN-EXTEND", "TN_FE_MANUAL_DEC2025", "primary", "pp. 89-92 — 90%/100%, the $100 prior-zero rule, seven months"),
    ("R-TN-EXTEND", "TN_2025_FAE170_INSTR", "secondary", "due date tied to the corresponding federal return's period end"),
    ("R-TN-SCHH", "TN_2025_FAE170_INSTR", "primary", "Schedule H Line 1 federal source; informational only"),
    ("R-TN-DEPR-REGIME", "TN_FE_MANUAL_DEC2025", "primary", "pp. 222-225 the two regimes and the phase-down table; pp. 267-270 the OBBBA chapter"),
    ("R-TN-DEPR-REGIME", "TN_TCA_67_4_2006", "primary", "§67-4-2006(a)(12) — the TCJA §168(k) lock (PC 377 (2023))"),
    ("R-TN-DEPR-REGIME", "TN_TCA_67_4_2004_IRC_DEF", "secondary", "rolling IRC conformity that OBBBA §179 rides in on"),
    ("R-TN-DEPR-REGIME", "IRS_2025_4562_INSTR", "secondary", "federal bonus at Form 4562 Part II Line 14 and Part V Line 25"),
    ("R-TN-MODES", "TN_FE_MANUAL_DEC2025", "secondary", "the $100 minimum is owed by inactive and charter-revoked entities"),
    ("R-TN-SCHM", "TN_FE_MANUAL_DEC2025", "secondary", "the 50%/5% default nonbusiness expense assumptions"),
]


# ── The line map ───────────────────────────────────────────────────────────
# Namespaced `<schedule>-<line>`; sort_order is assigned by position below.

TN170_LINES: list[dict] = [
    # Schedule A — Computation of Franchise Tax
    {"line_number": "A-1", "description": "Total net worth Schedule F1, Line 5 or Schedule F2, Line 3",
     "line_type": "calculated", "source_rules": ["R-TN-F1"], "source_facts": []},
    {"line_number": "A-2", "description": "Taxpayer electing to calculate franchise tax based on property measure - enter total from Schedule G Line 15. All other taxpayers - leave blank",
     "line_type": "input", "source_facts": ["a_l2_schedule_g_total"],
     "notes": "DIRECT-ENTRY so the Line 3 greater-of stays live. Schedule G itself is RED-deferred (R1/W4)."},
    {"line_number": "A-3", "description": "Franchise tax (25c per $100 or major fraction thereof on the greater of Lines 1 or 2; minimum $100)",
     "line_type": "calculated", "calculation": "R-TN-A-FRANCH", "source_rules": ["R-TN-A-FRANCH"],
     "notes": "LIVE MAX(L1, L2). Never L1 x 0.0025."},
    # Schedule B — Computation of Excise Tax
    {"line_number": "B-4", "description": "Income subject to excise tax from Schedule J, Line 39",
     "line_type": "calculated", "source_rules": ["R-TN-J-ORDER"]},
    {"line_number": "B-5", "description": "Excise tax (6.5% of Line 4) — if Line 4 is a loss, enter zero",
     "line_type": "calculated", "calculation": "R-TN-B-EXCISE", "source_rules": ["R-TN-B-EXCISE"]},
    {"line_number": "B-6", "description": "Recapture of tax credit (Schedule T, Line 13) and additional excise tax on certified distribution sales",
     "line_type": "input", "source_facts": ["b_l6_recapture_and_cds"], "notes": "Both components RED-deferred (R9, R10/U5)."},
    {"line_number": "B-7", "description": "Total excise tax due (add Lines 5 and 6)", "line_type": "subtotal", "source_rules": ["R-TN-B-EXCISE"]},
    # Schedule C — Total Tax Due or Overpayment
    {"line_number": "C-8", "description": "Total franchise and excise taxes (add Lines 3 and 7)", "line_type": "subtotal", "source_rules": ["R-TN-C-TOTAL"]},
    {"line_number": "C-9", "description": "Total credit from Schedule D, Line 10 (cannot exceed Schedule C, Line 8)",
     "line_type": "calculated", "source_rules": ["R-TN-C-TOTAL"], "notes": "One hole in the cap: the Green Energy Credit (§67-4-2109(m))."},
    {"line_number": "C-10", "description": "Net tax (subtract Line 9 from Line 8; if Line 9 exceeds Line 8, enter zero here)",
     "line_type": "calculated", "source_rules": ["R-TN-C-TOTAL"], "notes": "U8/W8 — floors at zero, so credits can drive net tax below the $100 franchise minimum."},
    {"line_number": "C-11", "description": "Total payments from Schedule E, Line 7", "line_type": "calculated", "source_rules": ["R-TN-ESTIM"]},
    {"line_number": "C-12", "description": "Penalty", "line_type": "input", "source_facts": ["c_l12_l15_penalty_interest"]},
    {"line_number": "C-13", "description": "Interest", "line_type": "input", "source_facts": ["c_l12_l15_penalty_interest"]},
    {"line_number": "C-14", "description": "Penalty on estimated payments", "line_type": "input", "source_facts": ["c_l12_l15_penalty_interest"]},
    {"line_number": "C-15", "description": "Interest on estimated payments", "line_type": "input", "source_facts": ["c_l12_l15_penalty_interest"]},
    {"line_number": "C-16", "description": "Total amount due (overpaid) (add Lines 10, 12, 13, 14, and 15, subtract Line 11); election A credit to next year / B refund",
     "line_type": "total", "source_rules": ["R-TN-C-TOTAL"]},
    # Schedule J1 — partnerships
    {"line_number": "J1-1", "description": "Ordinary income or loss (federal Form 1065, Line 23)", "line_type": "input", "source_facts": ["j1_l1_ordinary_income_1065_l23"]},
    {"line_number": "J1-2", "description": "Income items specifically allocated to partners, including guaranteed payments to partners", "line_type": "input", "source_facts": ["j1_l2_allocated_income"]},
    {"line_number": "J1-3", "description": "Any net loss or expense distributed to a publicly traded REIT", "line_type": "input", "source_facts": ["j1_l3_reit_loss_distributed"]},
    {"line_number": "J1-4", "description": "Total additions (add Lines 1 through 3)", "line_type": "subtotal", "source_rules": ["R-TN-J1"]},
    {"line_number": "J1-5", "description": "Expense items specifically allocated to partners not deducted elsewhere", "line_type": "input", "source_facts": ["j1_l5_allocated_expense"]},
    {"line_number": "J1-6", "description": "Amount subject to self-employment taxes distributable or paid to each partner or member net of any pass-through expense deducted elsewhere on this return (if negative, enter zero) (include on Schedule K, Line 3)",
     "line_type": "input", "source_facts": ["j1_l6_self_employment"], "notes": "CLONE TRAP — exists ONLY on J1 (and as J2 L8). J3 has no equivalent."},
    {"line_number": "J1-7", "description": "Amount of contribution to qualified pension or benefit plans of any partner or member, including all IRC 401 plans (include on Schedule K, Line 3)",
     "line_type": "input", "source_facts": ["j1_l7_qualified_plan"], "notes": "CLONE TRAP — exists ONLY on J1. J3 has no equivalent."},
    {"line_number": "J1-8", "description": "Any net gain or income distributed to a publicly traded REIT", "line_type": "input", "source_facts": ["j1_l8_reit_gain_distributed"]},
    {"line_number": "J1-9", "description": "Any loss on the sale of an asset sold within 12 months after the date of distribution", "line_type": "input", "source_facts": ["j1_l9_loss_asset_sold_12mo"]},
    {"line_number": "J1-10", "description": "Total deductions (add Lines 5 through 9)", "line_type": "subtotal", "source_rules": ["R-TN-J1"]},
    {"line_number": "J1-11", "description": "Total (subtract Line 10 from Line 4; enter here and on Schedule J, Line 1)", "line_type": "total", "source_rules": ["R-TN-J1"], "destination_form": "TN_FAE170 Schedule J Line 1"},
    # Schedule J2 — individual-owned SMLLC
    {"line_number": "J2-1", "description": "Business Income or loss from federal Form 1040, Schedule C", "line_type": "input", "source_facts": ["j2_l1_schedule_c"], "notes": "Instruction (not the form face) says Line 31."},
    {"line_number": "J2-2", "description": "Business Income or loss from federal Form 1040, Schedule D", "line_type": "input", "source_facts": ["j2_l2_schedule_d"], "notes": "If it is a loss, enter as a negative. No federal line number given by either document."},
    {"line_number": "J2-3", "description": "Business Income or loss from federal Form 1040, Schedule E", "line_type": "input", "source_facts": ["j2_l3_schedule_e"]},
    {"line_number": "J2-4", "description": "Business Income or loss from federal Form 1040, Schedule F", "line_type": "input", "source_facts": ["j2_l4_schedule_f"], "notes": "Instruction (not the form face) says Line 34."},
    {"line_number": "J2-5", "description": "Business Income or loss from federal Form 4797", "line_type": "input", "source_facts": ["j2_l5_form_4797"]},
    {"line_number": "J2-6", "description": "Other: federal Form ___, Schedule ___", "line_type": "input", "source_facts": ["j2_l6_other"]},
    {"line_number": "J2-7", "description": "Total additions (add Lines 1 through 6)", "line_type": "subtotal", "source_rules": ["R-TN-J2"]},
    {"line_number": "J2-8", "description": "Amount subject to self-employment taxes distributable or paid to the single member", "line_type": "input", "source_facts": ["j2_l8_self_employment"]},
    {"line_number": "J2-9", "description": "Total (subtract Line 8 from Line 7; enter here and on Schedule J, Line 1)", "line_type": "total", "source_rules": ["R-TN-J2"], "destination_form": "TN_FAE170 Schedule J Line 1"},
    # Schedule J3 — S corporations
    {"line_number": "J3-1", "description": "Ordinary income or loss (federal Form 1120S, Line 22)", "line_type": "input", "source_facts": ["j3_l1_ordinary_income_1120s_l22"]},
    {"line_number": "J3-2", "description": "Income items to extent includable in federal income were it not for 'S' status election", "line_type": "input", "source_facts": ["j3_l2_s_status_income"]},
    {"line_number": "J3-3", "description": "Total additions (add Lines 1 and 2)", "line_type": "subtotal", "source_rules": ["R-TN-J3"]},
    {"line_number": "J3-4", "description": "Expense items to extent includable in federal expenses were it not for 'S' status election", "line_type": "input", "source_facts": ["j3_l4_s_status_expense"]},
    {"line_number": "J3-5", "description": "Any loss on the sale of an asset sold within 12 months after the date of distribution", "line_type": "input", "source_facts": ["j3_l5_loss_asset_sold_12mo"],
     "notes": "⚠ J3's deduction list ENDS HERE. There is NO self-employment line and NO qualified-plan line — J1 L6/L7 have no J3 analogue."},
    {"line_number": "J3-6", "description": "Total deductions (add Lines 4 and 5)", "line_type": "subtotal", "source_rules": ["R-TN-J3"]},
    {"line_number": "J3-7", "description": "Total (subtract Line 6 from Line 3; enter here and on Schedule J, Line 1)", "line_type": "total", "source_rules": ["R-TN-J3"], "destination_form": "TN_FAE170 Schedule J Line 1"},
    # Schedule J4 — corporations and other entities
    {"line_number": "J4-1", "description": "Taxable income or loss before net operating loss deduction and special deductions (federal Form 1120, Line 28)", "line_type": "input", "source_facts": ["j4_l1_taxable_income_1120_l28"]},
    {"line_number": "J4-2a", "description": "REIT taxable income before net operating loss deduction and special deductions (federal Form 1120-REIT, Line 21)", "line_type": "input", "source_facts": ["j4_l2a_reit_taxable_income"]},
    {"line_number": "J4-2b", "description": "REIT deduction for dividends paid (federal Form 1120-REIT, Line 22b)", "line_type": "input", "source_facts": ["j4_l2b_reit_dividends_paid"]},
    {"line_number": "J4-2c", "description": "REIT taxable income after dividends paid deduction (subtract Line 2b from Line 2a)", "line_type": "subtotal", "source_rules": ["R-TN-J4"]},
    {"line_number": "J4-3", "description": "Unrelated business taxable income (federal Form 990-T, Line 5)", "line_type": "input", "source_facts": ["j4_l3_ubti_990t"], "notes": "The nonprofit path."},
    {"line_number": "J4-4", "description": "Other: federal Form ___", "line_type": "input", "source_facts": ["j4_l4_other_federal_income"]},
    {"line_number": "J4-5", "description": "Contribution carryover from prior period(s)", "line_type": "input", "source_facts": ["j4_l5_contribution_carryover_used"], "notes": "TIMING DECOUPLING — added back when used federally."},
    {"line_number": "J4-6", "description": "Capital gains offset by capital loss carryover or carryback", "line_type": "input", "source_facts": ["j4_l6_capital_gains_offset"], "notes": "TIMING DECOUPLING — added back when offset federally."},
    {"line_number": "J4-7", "description": "Total additions (add Lines 1 through 6)", "line_type": "subtotal", "source_rules": ["R-TN-J4"]},
    {"line_number": "J4-8", "description": "Contributions in excess of amount allowed by federal government", "line_type": "input", "source_facts": ["j4_l8_contributions_excess"], "notes": "Deducted IN FULL in the year made."},
    {"line_number": "J4-9", "description": "Portion of current year's capital loss not included in federal taxable income", "line_type": "input", "source_facts": ["j4_l9_current_capital_loss"], "notes": "Deducted IN FULL in the year incurred."},
    {"line_number": "J4-10", "description": "Total deductions (add Lines 8 and 9)", "line_type": "subtotal", "source_rules": ["R-TN-J4"]},
    {"line_number": "J4-11", "description": "Total (subtract Line 10 from Line 7; enter here and on Schedule J, Line 1)", "line_type": "total", "source_rules": ["R-TN-J4"], "destination_form": "TN_FAE170 Schedule J Line 1"},
    # Schedule J — Line 1 (the convergence)
    {"line_number": "J-1", "description": "Enter the applicable amount from line 11, 9, 7, or 11 of Schedule J1, J2, J3, or J4, respectively",
     "line_type": "calculated", "calculation": "R-TN-J-ENTRY", "source_rules": ["R-TN-J-ENTRY"],
     "notes": "THE CONVERGENCE. Only one entry schedule is completed per return."},
]

# Schedule J modification lines, generated from the verbatim tables above.
TN170_LINES += [
    {"line_number": f"J-{suffix}", "description": label, "line_type": "input",
     "source_facts": [fact], "notes": note}
    for suffix, fact, label, note in J_ADDITIONS
]
TN170_LINES.append(
    {"line_number": "J-15", "description": "Total additions (add Lines 2 through 14)",
     "line_type": "subtotal", "source_rules": ["R-TN-J-SUBTOT"]}
)
TN170_LINES += [
    {"line_number": f"J-{suffix}", "description": label, "line_type": "input",
     "source_facts": [fact], "notes": note}
    for suffix, fact, label, note in J_DEDUCTIONS
]
TN170_LINES += [
    {"line_number": "J-30", "description": "Total deductions (add Lines 16 through 29, excluding 28b)",
     "line_type": "subtotal", "source_rules": ["R-TN-J-SUBTOT"],
     "notes": "⚠ Line 28b is informational only and is EXCLUDED. Summing 16..29 inclusive overstates the deduction."},
    {"line_number": "J-31", "description": "Total business income (loss) (add Lines 1 and 15, subtract Line 30; if loss, enter on Schedule K, Line 1)",
     "line_type": "subtotal", "source_rules": ["R-TN-J-ORDER"]},
    {"line_number": "J-32", "description": "Excise tax standard deduction (enter the lesser of Line 31 or $50,000; if negative, enter zero)",
     "line_type": "calculated", "source_rules": ["R-TN-J-ORDER"],
     "notes": "PRE-APPORTIONMENT. Cannot create or increase a loss; no carryforward; ONE per return; unused portion spills to Schedule M Line 10."},
    {"line_number": "J-33", "description": "Excise tax optional deduction addback (see instructions; attach schedule)",
     "line_type": "input", "source_facts": ["j_l33_optional_addback"],
     "notes": "PC 343 (2025), §67-4-2006(c)(10). TAXPAYER-ELECTIVE — may be made, adjusted or removed at the taxpayer's discretion on any timely filed original or amended return. Never engine-imposed. Reversed on Schedule K Line 2."},
    {"line_number": "J-34", "description": "Adjusted total business income (loss) (subtract Line 32 from 31, add Line 33)",
     "line_type": "subtotal", "source_rules": ["R-TN-J-ORDER"]},
    {"line_number": "J-35", "description": "Excise tax apportionment ratio (Schedules N, N1, O, P, or R if applicable or 100%)",
     "line_type": "calculated", "source_rules": ["R-TN-SCHN"], "source_facts": ["j_l35_apportionment_ratio"]},
    {"line_number": "J-36", "description": "Apportioned business income (loss) (multiply Line 34 by Line 35)",
     "line_type": "calculated", "source_rules": ["R-TN-J-ORDER"]},
    {"line_number": "J-37", "description": "Nonbusiness earnings directly allocated to Tennessee (from Schedule M, Line 11)",
     "line_type": "calculated", "source_rules": ["R-TN-SCHM"],
     "notes": "POST-APPORTIONMENT — allocated, not apportioned, and taxed at the full 6.5%."},
    {"line_number": "J-38", "description": "Loss carryover from prior years (from Schedule U)",
     "line_type": "calculated", "source_rules": ["R-TN-SCHU"], "notes": "LAST. 15-year, oldest first, computed separately from federal."},
    {"line_number": "J-39", "description": "Subject to excise tax (add Line 36 and 37, subtract Line 38; enter here and on Schedule B, Line 4)",
     "line_type": "total", "source_rules": ["R-TN-J-ORDER"], "destination_form": "TN_FAE170 Schedule B Line 4"},
    # Schedule F1
    {"line_number": "F1-1", "description": "Net worth (total assets less total liabilities)", "line_type": "input", "source_facts": ["f1_l1_net_worth"], "notes": "GAAP basis."},
    {"line_number": "F1-2", "description": "Indebtedness to or guaranteed by parent or affiliated corporation (cannot be a deduction)", "line_type": "input", "source_facts": ["f1_l2_affiliate_indebtedness"]},
    {"line_number": "F1-3", "description": "Total (add Lines 1 and 2)", "line_type": "subtotal", "source_rules": ["R-TN-F1"]},
    {"line_number": "F1-4", "description": "Franchise tax apportionment ratio (Schedules N, N1, O, P, or R if applicable or 100%)", "line_type": "calculated", "source_rules": ["R-TN-SCHN"], "source_facts": ["f1_l4_franchise_ratio"]},
    {"line_number": "F1-5", "description": "Total (multiply Line 3 by Line 4; enter here and on Schedule A, Line 1)", "line_type": "total", "source_rules": ["R-TN-F1"], "notes": "Manufacturer base capped at $2,000,000,000 (§67-4-2121)."},
    # Schedule N
    {"line_number": "N-1", "description": "Sales factor (business gross receipts) (Enter franchise tax apportionment ratio on Schedule F1, Line 4. Enter excise tax apportionment ratio on Schedule J, Line 35.)",
     "line_type": "calculated", "calculation": "R-TN-SCHN", "source_rules": ["R-TN-SCHN"],
     "source_facts": ["sales_factor_tn_receipts", "sales_factor_everywhere"],
     "notes": "THE ENTIRE SCHEDULE. No property line, no payroll line, no 11x/13 divisor on the TY2025 form."},
    # Schedule M
    {"line_number": "M-8", "description": "Nonbusiness earnings (enter here and on Schedule J, Line 22)", "line_type": "calculated", "source_rules": ["R-TN-SCHM"]},
    {"line_number": "M-9", "description": "Net nonbusiness earnings after expenses", "line_type": "input", "source_facts": ["m_l9_net_nonbusiness_earnings"]},
    {"line_number": "M-10", "description": "Excise tax standard deduction (Enter $50,000 less amount reported on Schedule J, Line 32; cannot exceed Line 9)", "line_type": "calculated", "source_rules": ["R-TN-SCHM"]},
    {"line_number": "M-11", "description": "Nonbusiness earnings directly allocated to Tennessee (enter here and on Schedule J, Line 37)", "line_type": "total", "source_rules": ["R-TN-SCHM"]},
    # Schedule K
    {"line_number": "K-1", "description": "Net loss from Schedule J, Line 31", "line_type": "calculated", "source_rules": ["R-TN-SCHK"]},
    {"line_number": "K-2", "description": "Amounts reported on Schedule J, Lines 18, 22, and 33", "line_type": "calculated", "source_rules": ["R-TN-SCHK"]},
    {"line_number": "K-3", "description": "Amounts reported on Schedule J1, Lines 6 and 7, or Schedule J2, Line 8", "line_type": "calculated", "source_rules": ["R-TN-SCHK"],
     "notes": "J3 and J4 contribute NOTHING here — they have no self-employment or qualified-plan line."},
    {"line_number": "K-4", "description": "Reduced loss (add Lines 1 through 3; if net amount is positive, enter zero)", "line_type": "subtotal", "source_rules": ["R-TN-SCHK"]},
    {"line_number": "K-5", "description": "Apportionment ratio", "line_type": "calculated", "source_rules": ["R-TN-SCHN"]},
    {"line_number": "K-6", "description": "Current year loss carryover available (multiply Line 4 by Line 5)", "line_type": "total", "source_rules": ["R-TN-SCHK"]},
    # Schedules T / D / E / H
    {"line_number": "T-11", "description": "Industrial machinery credit — enter the smaller value of Lines 5, 7, or 10 here, and on Schedule D, Line 5",
     "line_type": "calculated", "calculation": "R-TN-SCHT1", "source_rules": ["R-TN-SCHT1"]},
    {"line_number": "D-5", "description": "Industrial Machinery and Research and Development Tax Credit from Schedule T, Line 11", "line_type": "calculated", "source_rules": ["R-TN-SCHT1"]},
    {"line_number": "D-10", "description": "Total credit (add Lines 1 through 9; enter here and on Schedule C, Line 9)", "line_type": "subtotal", "source_rules": ["R-TN-C-TOTAL"]},
    {"line_number": "E-7", "description": "Total payments (add Lines 1 through 6; enter here and on Schedule C, Line 11)", "line_type": "subtotal", "source_rules": ["R-TN-ESTIM"]},
    {"line_number": "H-1", "description": "Gross receipts or sales per federal income tax return", "line_type": "informational", "source_facts": ["h_l1_gross_receipts"], "source_rules": ["R-TN-SCHH"],
     "notes": "Feeds nothing on the return — a reporting/nexus datapoint."},
]

for _i, _ln in enumerate(TN170_LINES, start=1):
    _ln.setdefault("notes", "")
    _ln.setdefault("source_facts", [])
    _ln.setdefault("source_rules", [])
    _ln["sort_order"] = _i


# ── Diagnostics ────────────────────────────────────────────────────────────
# HOUSE RULE: **EVERY RED-DEFER GETS ITS OWN DIAGNOSTIC — NO SILENT GAP.**
# R1..R15 below are the fifteen defers from the source brief §13, one for one.
# Severity: "error" where the return will be WRONG or INCOMPLETE without manual
# work; "warning" where a human must confirm an unresolved reading; "info" for
# notices that do not change this return's numbers.

TN170_DIAGNOSTICS: list[dict] = [
    # ═══ THE STRUCTURAL TRAPS ═══
    {"diagnostic_id": "D_TN170_J3_NO_SE_PENSION", "severity": "error",
     "title": "Schedule J3 has NO self-employment and NO qualified-plan deduction",
     "condition": "federal_entity_type == '1120S' AND (a self-employment figure OR a qualified pension/IRC 401 figure has been carried onto Schedule J3)",
     "message": "Schedule J3's ONLY deductions are Line 4 (expense items includable but for the 'S' election) and Line 5 "
                "(loss on an asset sold within 12 months of distribution). Tennessee gives an S corporation NO equivalent "
                "of Schedule J1 Line 6 (self-employment earnings) or Line 7 (qualified pension / IRC 401 contributions), "
                "because shareholder wages are already inside federal Form 1120-S Line 22. Remove the figure — carrying "
                "it here OVERSTATES the deduction and UNDERSTATES Tennessee excise tax by 6.5% of the amount.",
     "notes": "THE CLONE TRAP. Verified on the form face AND the line-by-line instructions by the adversarial pass. "
              "This is the single largest entity-choice-driven difference in the TN excise base."},
    {"diagnostic_id": "D_TN170_J_ORDERING", "severity": "info",
     "title": "Schedule J ordering: $50,000 pre-apportionment, nonbusiness post, NOL last",
     "condition": "Schedule J Line 35 apportionment ratio < 100%",
     "message": "The $50,000 excise tax standard deduction is applied BEFORE apportionment (Line 32, inside Line 34); "
                "nonbusiness earnings allocated to Tennessee are added AFTER apportionment (Line 37); and the Tennessee "
                "loss carryover is subtracted LAST (Line 38). Apportioning first and then deducting $50,000 produces a "
                "different — and wrong — answer on every multistate return.",
     "notes": "Confirmed against the form face p. 5 and instructions pp. 9-10. At a 30% ratio the two orderings differ by $35,000 of base."},
    {"diagnostic_id": "D_TN170_FRANCHISE_GREATER", "severity": "info",
     "title": "Schedule A Line 3 is a live greater-of, not a flat rate on net worth",
     "condition": "Schedule A Line 2 has a value",
     "message": "Franchise tax is 25c per $100 (or major fraction thereof) on the GREATER of Line 1 (net worth) or Line 2 "
                "(the Schedule G property measure), with a $100 minimum. Line 2 is populated, so the property measure may "
                "be producing the tax. Verify the Schedule G election is properly on file.",
     "notes": "W4 — Schedule G is RED-deferred but the greater-of is built so the arithmetic is right when it lands."},
    {"diagnostic_id": "D_TN170_SMLLC_J2_TRIGGER", "severity": "warning",
     "title": "A single-member LLC owned by an individual is itself an FAE170 taxpayer",
     "condition": "federal_entity_type == '1040_smllc'",
     "message": "Tennessee has no individual income tax, but a single-member LLC owned by a natural person is a franchise "
                "and excise taxpayer in its own right and computes net earnings on Schedule J2 from Form 1040 Schedules C, "
                "D, E and F and Form 4797. Disregarded entities are NOT disregarded for F&E — the only exceptions are an "
                "SMLLC whose single member is a CORPORATION and an SMLLC wholly owned by a PENSION TRUST.",
     "notes": "W10 — a client-exposure question. A 1040 workflow will not surface this filing on its own."},
    {"diagnostic_id": "D_TN170_NET_WORTH_CAPTURE", "severity": "warning",
     "title": "Franchise tax needs GAAP balance-sheet data the federal return does not supply",
     "condition": "Schedule F1 Line 1 is blank and the entity is not filing the inactive page-1-only return",
     "message": "Net worth (total assets less total liabilities, GAAP basis) comes off a balance sheet, not off the "
                "federal income return. Nothing on Schedules J1-J4 feeds Schedule F1. Importing the federal return covers "
                "only the EXCISE half of FAE170 — the franchise half must be captured separately.",
     "notes": "The handoff is one-directional and lossy."},
    {"diagnostic_id": "D_TN170_LOSS_MIN_TAX", "severity": "info",
     "title": "A loss year still owes the $100 minimum franchise tax",
     "condition": "Schedule J Line 39 <= 0",
     "message": "Excise tax is zero when Schedule J Line 39 is a loss, but the $100 minimum franchise tax (Tenn. Code Ann. "
                "§67-4-2119) is still due. The two taxes share no base and neither floors the other.",
     "notes": "Also owed by an inactive entity and by one whose charter has been revoked but not dissolved."},

    # ═══ OPEN ITEMS — FLAGGED, NEVER GUESSED ═══
    {"diagnostic_id": "D_TN170_BONUS_KEY_W1", "severity": "warning",
     "title": "OPEN (W1): bonus keyed to ACQUISITION or PLACED-IN-SERVICE date — Ken's ruling required",
     "condition": "any asset whose acquisition year and placed-in-service year differ, in a return using Schedule J Lines 3, 16 or 17",
     "message": "The Tennessee DOR contradicts itself: the phase-down table (manual p. 225) is captioned 'Asset Acquired "
                "Between:' while the OBBBA chapter (p. 267) keys the same 40%/20%/0% to property 'placed in service'; the "
                "form and instructions say 'purchased'. For an asset ACQUIRED IN 2024 AND PLACED IN SERVICE IN 2025 the "
                "two readings give 60% and 40%, and the key also decides which of the two decoupling regimes the asset "
                "falls into. This product does not choose. Determine the applicable percentage manually and enter Lines 3, "
                "16 and 17 directly until the ruling is recorded.",
     "notes": "ESCALATED — delvio-states/GATE1_WALK.md item 3 and walk item W1. Brief's recommendation: build to "
              "PLACED IN SERVICE, flag, confirm with the DOR, and record it as a RULING not a finding. "
              "THIS CHANGES NUMBERS ON REAL RETURNS."},
    {"diagnostic_id": "D_TN170_OBBBA_BONUS_DIFF", "severity": "error",
     "title": "RED-DEFER R13 (W2/U1): the post-2022 OBBBA bonus differential — prepare manually",
     "condition": "has_post_2022_obbba_differential is true, i.e. federal OBBBA bonus exceeds the Tennessee TCJA-allowable amount for an asset purchased on or after 1/1/2023",
     "message": "Tennessee is frozen at the TCJA version of IRC §168(k) — 40% for 2025 — so OBBBA's 100% bonus is not "
                "available, and §168(n) qualified production property gets no Tennessee bonus at all. The excess must be "
                "added back and then recovered as MACRS on a separate Tennessee basis. HOWEVER, the Department has not "
                "said which Schedule J line carries that differential: the form and instructions scope Lines 3, 16 and 17 "
                "to assets purchased on or before December 31, 2022, while the OBBBA chapter mandates Schedule J "
                "adjustments without naming a line. This product does not prepare the differential. Compute it manually "
                "and enter the amounts directly.",
     "notes": "W2/U1. Working assumption for a future build: Lines 3/16/17 carry BOTH regimes (there is no other line). "
              "This is the one RED-defer that gates ORDINARY returns rather than rare taxpayers. Open a DOR ticket."},
    {"diagnostic_id": "D_TN170_DEPR_DIRECT_ENTRY", "severity": "error",
     "title": "Federal bonus depreciation present but Schedule J Line 3 is blank (W3)",
     "condition": "federal_4562_bonus_total (Form 4562 Part II Line 14 + Part V Line 25) is non-zero AND Schedule J Line 3 is blank",
     "message": "Federal bonus depreciation was claimed but no Tennessee add-back is on Schedule J Line 3. Tennessee "
                "disallows bonus entirely for assets purchased on or before December 31, 2022, and allows only the frozen "
                "TCJA percentage for later assets. This product does not compute the Tennessee depreciation basis in v1 — "
                "enter Lines 3, 16 and 17 directly from a manually maintained Tennessee asset ledger.",
     "notes": "W3 — the largest single scope lever. v1.1 is the TN-basis engine. Ken is the depreciation specialist."},
    {"diagnostic_id": "D_TN170_MIN_TAX_VS_CREDITS", "severity": "warning",
     "title": "OPEN (W8/U8): credits reducing net tax below the $100 franchise minimum",
     "condition": "Schedule C Line 9 credits >= Schedule C Line 8, producing a Line 10 of zero",
     "message": "Schedule C Line 9 is capped only at 'cannot exceed Schedule C, Line 8' and Line 10 floors at zero, so on "
                "the form's own arithmetic a large credit reduces net tax to zero — the $100 minimum franchise tax "
                "included. No Department statement was found either way. This product follows the form's arithmetic. "
                "Confirm the treatment before filing.",
     "notes": "W8 — must be Ken's ruling, not the spec's assumption. Same walk item covers the 'major fraction thereof' "
              "rounding (a remainder over $50 rounds the base up to the next $100)."},
    {"diagnostic_id": "D_TN170_SHORT_PERIOD_APPT", "severity": "warning",
     "title": "OPEN (U3): short 2025 period vs the one-line TY2025 Schedule N",
     "condition": "is_short_period AND tax_period_begin >= 2025-01-01 AND tax_period_end < 2025-12-31",
     "message": "By statute a period ending before December 31, 2025 falls in the (property + payroll + 11x sales) / 13 "
                "apportionment row, but the TY2025 Schedule N carries a single sales-factor line and cannot express that "
                "formula. The Department has published no guidance on which form-year such a short period files. Confirm "
                "with the Department before filing.",
     "notes": "U3. The Schedule PL half of this item is RESOLVED — Schedule PL is carryforward-only on the TY2025 form "
              "because of its 25-year carryforward, not because of short periods."},
    {"diagnostic_id": "D_TN170_L13_L28A_ERRATUM", "severity": "info",
     "title": "Instruction erratum (U4): business interest is deducted on Line 28a, not 'Line 27a'",
     "condition": "Schedule J Line 13 is completed (federal Form 8990 was filed)",
     "message": "The Schedule J Line 13 instruction closes by saying the business interest expense deduction is reported "
                "on 'Sch. J, Line 27a'. There is no Line 27a on the form — Line 27 is IRC §951A GILTI, and the business "
                "interest deduction is Line 28a on both the form face and the Line 28a instruction. This product builds "
                "to Line 28a.",
     "notes": "U4 — resolved as an erratum. Recorded so a future reader does not 'fix' it back to 27a."},

    # ═══ RED-DEFERS R1..R15 — one diagnostic each, no silent gap ═══
    {"diagnostic_id": "D_TN170_SCHED_G", "severity": "error",
     "title": "RED-DEFER R1: Schedule G property-measure election — prepare manually",
     "condition": "Schedule A Line 2 has a value, OR the taxpayer indicates the Tenn. Code Ann. §67-4-2123 election",
     "message": "Tennessee Schedule G is not prepared by this product. The annual Schedule G Minimum Property Measure "
                "Election (Tenn. Code Ann. §67-4-2123) must be submitted separately through TNTAP, including the "
                "constitutional-waiver signature. Compute Schedule G manually and enter the Line 15 total on Schedule A, "
                "Line 2 — Schedule A Line 3's greater-of will then compute correctly.",
     "notes": "⚠ W4 / verification C1: this text deliberately says NOTHING about the MeF accepted-forms list. The old "
              "'Schedule G is not e-fileable' rationale was an argument from silence and was REFUTED — Schedule A Line 2 "
              "carries the Schedule G total onto the FAE170, which IS accepted through MeF. The DEFER decision is "
              "unchanged (opt-in rarity, the annual TNTAP election, the constitutional waiver, superseded guidance); only "
              "its justification changed. U9 (whether the MeF schema carries Sch. G detail lines) does not affect v1."},
    {"diagnostic_id": "D_TN170_SCHED_F2", "severity": "error",
     "title": "RED-DEFER R2: Schedule F2 consolidated net worth — prepare manually",
     "condition": "checkbox (d) consolidated net worth election OR checkbox (e) revocation is set",
     "message": "Consolidated net worth (Schedule F2) is not prepared by this product. It requires the Consolidated Net "
                "Worth Election Registration Application, a pro forma consolidated GAAP balance sheet with intercompany "
                "transactions and holdings in non-domestic persons eliminated (§67-4-2106(b)), and an apportionment ratio "
                "from Schedule 170NC, 170NC1 or 170SF — not from Schedules N/N1/O/P/R. Prepare the group computation "
                "manually.",
     "notes": "W5. The election is binding FIVE years; exiting members compute on Schedule F1 (§67-4-2103(d))."},
    {"diagnostic_id": "D_TN170_SCHED_N1", "severity": "error",
     "title": "RED-DEFER R3: Schedule N1 three-factor / Telecom Qualified Member — prepare manually",
     "condition": "checkbox (h) three-factor election OR checkbox (i) Telecom Qualified Member is set",
     "message": "Schedule N1 is not prepared by this product. It produces TWO different ratios — franchise via Line 14 "
                "(net of exempt inventory) and excise via Line 13 (gross) — carries the zero-denominator factor "
                "elimination rule, and uses original tax-basis cost with a x8 multiple on ALL rents. The elective version "
                "also requires proving a HIGHER resulting ratio AND net earnings rather than a net loss, which means "
                "computing both formulas. Prepare Schedule N1 manually.",
     "notes": "W6. Telecom Qualified Member (§67-4-2012(j), computed under (a)(7)) is MANDATORY, not elective, and covers "
              "telecommunications, mobile telecom, internet access, video programming and direct-to-home satellite TV."},
    {"diagnostic_id": "D_TN170_SCHED_OPR", "severity": "error",
     "title": "RED-DEFER R4: Schedules O / P / R industry apportionment — prepare manually",
     "condition": "the taxpayer is a common carrier, air carrier, or air express carrier",
     "message": "Schedule O (common carriers — railroads, motor carriers, pipelines, barges), Schedule P (air carriers) "
                "and Schedule R (air express carriers) are not prepared by this product. Each is a two-factor formula "
                "with its own divisor and the zero-denominator elimination rule. Prepare the applicable schedule manually "
                "and enter the resulting ratio.",
     "notes": "W6. Common carriers: Tenn. Code Ann. §67-4-2013."},
    {"diagnostic_id": "D_TN170_FAE174", "severity": "error",
     "title": "RED-DEFER R5: file FAE174, not FAE170 — HARD STOP",
     "condition": "more than 50% of the entity's gross receipts are from carrying on the business of a financial institution, or the entity is a captive REIT",
     "message": "File FAE174, not FAE170. The Department states it directly: 'If more than 50% of an entity's gross "
                "receipts are from carrying on the \"business of a financial institution,\" franchise and excise tax Form "
                "FAE174 should be completed instead of Form FAE170.' This is a standalone-entity test, not a group-only "
                "rule. Financial institution unitary groups and captive REIT affiliated groups are the only "
                "combined/consolidated F&E filers; everyone else files separate-entity.",
     "notes": "R5 is correctly a HARD STOP rather than a review note, given the verbatim 'instead of'. FAE174 filers are "
              "separately required to file electronically."},
    {"diagnostic_id": "D_TN170_SCHED_X", "severity": "error",
     "title": "RED-DEFER R6: Schedule X job tax credits — prepare manually",
     "condition": "Schedule D Line 6 or Line 7 is non-zero",
     "message": "The Job Tax Credit (Schedule D Line 6, from Schedule X Line 46) and the Additional Annual Job Tax Credit "
                "(Schedule D Line 7, from Schedule X Line 38) are not computed by this product. Prepare Schedule X "
                "manually and enter the credit amounts.",
     "notes": "U6 — the Schedule X line map has not been transcribed; only its feed lines are verified. "
              "Note Schedule D Line 7 also feeds the Schedule T Line 9 credit-ordering subtraction."},
    {"diagnostic_id": "D_TN170_SCHED_QP", "severity": "error",
     "title": "RED-DEFER R7: Schedule QP qualified production credit — prepare manually",
     "condition": "Schedule D Line 8 is non-zero",
     "message": "The Qualified Production Credit (Schedule D Line 8, from Schedule QP Line 12) is not computed by this "
                "product. Prepare Schedule QP manually and enter the credit amount.",
     "notes": "U6 — Schedule QP line map not transcribed."},
    {"diagnostic_id": "D_TN170_SCHED_BP", "severity": "error",
     "title": "RED-DEFER R8: Schedule BP brownfield credits — prepare manually",
     "condition": "Schedule D Line 3 is non-zero",
     "message": "Brownfield Property Credits (Schedule D Line 3) are not computed by this product. Prepare Schedule BP "
                "manually; a Department approval letter must accompany the claim.",
     "notes": "U6 — Schedule BP line map not transcribed."},
    {"diagnostic_id": "D_TN170_SCHED_T_RECAP", "severity": "error",
     "title": "RED-DEFER R9: Schedule T Part 2 recapture — prepare manually",
     "condition": "industrial machinery was sold, or removed from Tennessee, before the end of its federal useful life",
     "message": "Recapture of the industrial machinery credit (Schedule T Part 2) is not computed by this product. "
                "Compute it manually: Line 12 reduces the Schedule V carryover and Line 13 is reported on Schedule B, "
                "Line 6. Schedule T Part 1 (the current-year credit) IS computed.",
     "notes": "W7."},
    {"diagnostic_id": "D_TN170_CERT_DIST_SALES", "severity": "error",
     "title": "RED-DEFER R10: certified distribution sales additional excise tax — prepare manually",
     "condition": "a Tenn. Code Ann. §67-4-2023 election is indicated, OR Schedule B Line 6 is entered without a Schedule T Line 13 amount",
     "message": "The additional excise tax on certified distribution sales (§67-4-2023, reported within Schedule B "
                "Line 6) is not computed by this product. The FAE170 kit contains no schedule computing it and the Line 6 "
                "instruction gives no formula. Compute it manually. Note the TY2025 gate change: for tax years ending on "
                "or after December 31, 2025 the sales-factor threshold drops to 7.5% AND more than 50% of the taxpayer's "
                "Tennessee sales must be certified distribution sales.",
     "notes": "U5 — genuinely unresolved: no schedule, no formula. Must not be silently dropped."},
    {"diagnostic_id": "D_TN170_ANNUALIZED_EST", "severity": "error",
     "title": "RED-DEFER R11: annualized income installment method — prepare manually",
     "condition": "checkbox (f) annualized income installment method election is set",
     "message": "The annualized income installment method is not computed by this product. It is an annual election "
                "available on an ORIGINAL return only; the franchise and excise components are computed separately, with "
                "the excise component under IRC §6655(e)(2) and the franchise component at the lesser of 25% of the prior "
                "year's franchise tax (annualized if short) or 25% of 80% of the current year's. Complete the worksheet "
                "manually and enter Line 23 on Schedule E Lines 2(a)-5(a). The STANDARD method IS computed.",
     "notes": "W7 / brief §9.2."},
    {"diagnostic_id": "D_TN170_FAE183", "severity": "warning",
     "title": "RED-DEFER R12: FAE183 exemption application / annual renewal — file separately",
     "condition": "the entity claims one of the 10 exemptions that require FAE183",
     "message": "Ten of the seventeen §67-4-2008 exemptions require Form FAE183 for the initial period AND each "
                "subsequent period: venture capital funds; farming or holding a personal residence; entities acquiring "
                "affiliate receivables; LIHTC affordable housing; obligated member entities; asset-backed securitization; "
                "family-owned noncorporate entities (FONCE); diversified investing funds; armed-forces facility entities; "
                "and qualified low-income community historic structure owners or lessees. FAE183 is due the 15th day of "
                "the 4th month after the period closes, with a seven-month extension available. Late filing does NOT "
                "forfeit the exemption but carries a $200 per-occurrence penalty. This product does not prepare FAE183.",
     "notes": "Failing the requirements at ANY point during the period forfeits the exemption for the ENTIRE period. Six "
              "exemptions require Audit Division evaluation. ⚠ The FAE183 PDF has not been reissued since 2023-02-01 and "
              "therefore predates PC 950 (2024) and PC 455 (2025) — do not assume it reflects 2025 law."},
    {"diagnostic_id": "D_TN170_FORM_IE", "severity": "error",
     "title": "RED-DEFER R14: Form IE intangible expense disclosure — required or the deduction is lost",
     "condition": "Schedule J Line 2 or Line 23 is non-zero",
     "message": "Form IE (Intangible Expense Disclosure) is not prepared by this product and MUST be attached. The "
                "Schedule J Line 23 deduction is allowed only if Line 2 is completed AND Form IE is attached; omitting it "
                "disallows the deduction and triggers a penalty of the GREATER of $10,000 or 50% of the adjustment. "
                "Prepare Form IE manually.",
     "notes": "Definitions at Tenn. Code Ann. §67-4-2004(1) and (24); §67-4-2006(b)(2)(N)."},
    {"diagnostic_id": "D_TN170_BUS_428", "severity": "info",
     "title": "RED-DEFER R15: Tennessee business tax (BUS 428) is a separate obligation — out of scope",
     "condition": "the entity has $100,000 or more of gross sales in a Tennessee county or municipality",
     "message": "Tennessee's county/city business tax is a separate gross-receipts privilege tax and is NOT part of "
                "franchise and excise tax. Form BUS 428 is filed PER LOCATION, due the 15th day of the 4th month after "
                "fiscal year end, with classification set by each location's dominant business activity. The threshold is "
                "$100,000 of gross sales per jurisdiction; a minimal activity license covers over $3,000 and under "
                "$100,000. Business tax returns must be filed electronically through TNTAP — there is no third-party "
                "e-file path — so this product cannot prepare or transmit them.",
     "notes": "Conformity §9 scope call: keep OUT of the F&E spec. Informational notice only; never a wave item."},

    # ═══ MODE AND ROUTING NOTICES ═══
    {"diagnostic_id": "D_TN170_PL86272", "severity": "info",
     "title": "P.L. 86-272 removes the excise tax only — the franchise schedules are still required",
     "condition": "checkbox (c) Public Law 86-272 applied to excise tax is set",
     "message": "Checking box (c) claims P.L. 86-272 protection against the EXCISE tax only. The taxpayer still files "
                "FAE170 and completes the FRANCHISE tax schedules, and the $100 minimum franchise tax still applies.",
     "notes": "Verbatim from the instructions."},
    {"diagnostic_id": "D_TN170_INACTIVE_MIN", "severity": "info",
     "title": "Inactive entity — page-one-only filing mode",
     "condition": "is_inactive_entity AND only the minimum tax is owed",
     "message": "An entity registered in Tennessee that was inactive for the entire taxable period and owes only the "
                "minimum tax may file page one of this return only and omit the remaining pages. The $100 minimum "
                "franchise tax is still due — including where the charter has been revoked but not dissolved.",
     "notes": "A real filing mode, verbatim from the instructions p. 2."},
    {"diagnostic_id": "D_TN170_NO_PTET_NO_1040", "severity": "info",
     "title": "Tennessee has no PTET, no individual return, and no owner-level credit",
     "condition": "a preparer looks for a Tennessee PTET election, composite return, or owner credit",
     "message": "Tennessee has no pass-through entity tax and structurally cannot use one — there is no owner-level "
                "Tennessee income tax to credit against, because the Hall income tax was repealed for tax periods "
                "beginning on or after January 1, 2021. There is no individual return, no fiduciary return (except that a "
                "BUSINESS TRUST is an F&E taxpayer), no composite return, and no nonresident withholding. Tennessee "
                "reaches pass-through income by taxing the ENTITY directly. Owner-side treatment: none — no credit, "
                "deduction, exclusion, or K-1 pass-through of the tax.",
     "notes": "Prevents a wave's shared scaffolding from assuming a PTET table, an owner credit, or a K-1 state column."},
    {"diagnostic_id": "D_TN170_MFG_CAP", "severity": "info",
     "title": "Manufacturer franchise base capped at $2 billion",
     "condition": "is_manufacturer AND Schedule F1 Line 3 x Line 4 exceeds $2,000,000,000",
     "message": "Tenn. Code Ann. §67-4-2121 limits the franchise tax base of any manufacturer to $2,000,000,000 of "
                "apportioned net worth. The cap is applied at Schedule F1 Line 5 (or Schedule F2 Line 3).",
     "notes": ""},
    {"diagnostic_id": "D_TN170_PRORATION", "severity": "warning",
     "title": "Franchise proration: floored at $100, and never for 52/53-week filers (W9)",
     "condition": "is_short_period OR this is an initial return OR is_5253_week_filer",
     "message": "Franchise tax may be prorated on short-period and initial returns — from the date of formation or the "
                "date Tennessee operations began, whichever is first, for Tennessee-formed entities, and from the date "
                "operations began for foreign entities — but NEVER below the $100 minimum, and NOT AT ALL on returns "
                "filed by 52/53-week filers. Excise tax is NEVER prorated. The Department's Short Period Return "
                "Worksheets are retained by the taxpayer, not filed.",
     "notes": "W9 — confirm the day-count convention with Ken; the manual's own annualization example uses 365.25."},
]


# ── Test scenarios (arithmetic oracles; the harness re-proves each) ─────────

TN170_SCENARIOS: list[dict] = [
    {"scenario_name": "Franchise tax — net worth only, no Schedule G election", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"f1_l1_net_worth": 4000000, "f1_l2_affiliate_indebtedness": 0, "f1_l4_franchise_ratio": 1.0, "a_l2_schedule_g_total": 0},
     "expected_outputs": {"A-1": 4000000, "A-3": 10000.0},
     "notes": "4,000,000 / 100 = 40,000 units x $0.25 = $10,000 (= 0.25%). Line 2 blank, so the greater-of picks Line 1."},
    {"scenario_name": "Franchise tax — Schedule G property measure WINS the greater-of", "scenario_type": "edge", "sort_order": 2,
     "inputs": {"f1_l1_net_worth": 300000, "f1_l4_franchise_ratio": 1.0, "a_l2_schedule_g_total": 1200000},
     "expected_outputs": {"A-1": 300000, "A-2": 1200000, "A-3": 3000.0},
     "notes": "MAX(300,000, 1,200,000) = 1,200,000 -> 12,000 units x $0.25 = $3,000. A spec that used Line 1 would compute $750 — a 4x understatement. THE GREATER-OF IS LIVE."},
    {"scenario_name": "Franchise tax — $100 minimum floor", "scenario_type": "edge", "sort_order": 3,
     "inputs": {"f1_l1_net_worth": 12000, "f1_l4_franchise_ratio": 1.0},
     "expected_outputs": {"A-3": 100.0},
     "notes": "12,000 -> 120 units x $0.25 = $30, floored to the $100 minimum (§67-4-2119)."},
    {"scenario_name": "Franchise tax — 'major fraction thereof' rounding", "scenario_type": "edge", "sort_order": 4,
     "inputs": {"f1_l1_net_worth": 1000051, "f1_l4_franchise_ratio": 1.0},
     "expected_outputs": {"A-3": 2500.25},
     "notes": "1,000,051 = 10,000 units remainder 51. A remainder OVER $50 is a major fraction and rounds up -> 10,001 units x $0.25 = $2,500.25. At 1,000,050 the remainder is exactly 50, which does NOT round up -> $2,500.00. (W8: Ken to bless the >50 vs >=50 reading.)"},
    {"scenario_name": "Franchise tax — manufacturer $2 billion base cap", "scenario_type": "edge", "sort_order": 5,
     "inputs": {"f1_l1_net_worth": 5000000000, "f1_l4_franchise_ratio": 1.0, "is_manufacturer": True},
     "expected_outputs": {"F1-5": 2000000000, "A-3": 5000000.0},
     "notes": "§67-4-2121 caps the base at $2B -> 20,000,000 units x $0.25 = $5,000,000. Uncapped it would be $12,500,000."},
    {"scenario_name": "Franchise proration — short period, floored at $100", "scenario_type": "edge", "sort_order": 6,
     "inputs": {"f1_l1_net_worth": 30000, "f1_l4_franchise_ratio": 1.0, "franchise_proration_factor": 0.5, "is_short_period": True},
     "expected_outputs": {"A-3": 100.0},
     "notes": "30,000 -> 300 units x $0.25 = $75; x 0.5 proration = $37.50; floored to $100. At 200,000 net worth: $500 x 0.5 = $250, above the floor. A 52/53-week filer gets NO proration at all (W9)."},
    {"scenario_name": "Excise tax — 6.5% of Schedule J Line 39", "scenario_type": "normal", "sort_order": 10,
     "inputs": {"j_l39_subject_to_excise": 800000},
     "expected_outputs": {"B-5": 52000.0},
     "notes": "800,000 x 6.5% = $52,000 (Tenn. Code Ann. §67-4-2007)."},
    {"scenario_name": "Excise zero on a loss — but the $100 franchise minimum still due", "scenario_type": "edge", "sort_order": 11,
     "inputs": {"j_l39_subject_to_excise": -250000, "f1_l1_net_worth": 12000, "f1_l4_franchise_ratio": 1.0},
     "expected_outputs": {"B-5": 0.0, "A-3": 100.0, "C-8": 100.0},
     "notes": "'If Line 4 is a loss, enter zero.' The two taxes share no base — the franchise minimum is unaffected by an excise loss."},
    {"scenario_name": "THE CLONE TRAP — J1 vs J3 on identical economics", "scenario_type": "edge", "sort_order": 12,
     "inputs": {"j1_l1_ordinary_income_1065_l23": 500000, "j1_l2_allocated_income": 100000, "j1_l5_allocated_expense": 40000,
                "j1_l6_self_employment": 150000, "j1_l7_qualified_plan": 25000,
                "j3_l1_ordinary_income_1120s_l22": 500000, "j3_l2_s_status_income": 100000, "j3_l4_s_status_expense": 40000},
     "expected_outputs": {"J1-4": 600000, "J1-10": 215000, "J1-11": 385000, "J3-3": 600000, "J3-6": 40000, "J3-7": 560000},
     "notes": "Same economics, DIFFERENT Tennessee base. J1 = 600,000 - 215,000 = 385,000. J3 = 600,000 - 40,000 = 560,000. "
              "The 175,000 gap is EXACTLY J1 L6 + L7 (150,000 + 25,000), which J3 has no line for. At 6.5% that is "
              "$11,375 of excise tax. Cloning J1 into J3 would produce 385,000 and understate the tax by that amount."},
    {"scenario_name": "ORDERING — $50k pre-apportionment vs the WRONG apportion-first path", "scenario_type": "edge", "sort_order": 13,
     "inputs": {"j_l31_total_business_income": 1000000, "j_l35_apportionment_ratio": 0.30,
                "j_l37_nonbusiness_tn": 0, "u_loss_carryover_available": 0},
     "expected_outputs": {"J-32": 50000, "J-34": 950000, "J-36": 285000.0, "J-39": 285000.0, "B-5": 18525.0},
     "notes": "CORRECT: 1,000,000 - 50,000 = 950,000; x 0.30 = 285,000; x 6.5% = $18,525. "
              "WRONG (apportion first): 1,000,000 x 0.30 = 300,000 - 50,000 = 250,000; x 6.5% = $16,250. "
              "The $2,275 gap is 50,000 x (1 - 0.30) x 6.5%. Apportion-first is wrong."},
    {"scenario_name": "ORDERING — nonbusiness POST-apportionment, NOL LAST", "scenario_type": "edge", "sort_order": 14,
     "inputs": {"j_l31_total_business_income": 400000, "j_l35_apportionment_ratio": 0.50,
                "j_l37_nonbusiness_tn": 60000, "u_loss_carryover_available": 90000},
     "expected_outputs": {"J-32": 50000, "J-34": 350000, "J-36": 175000.0, "J-39": 145000.0, "B-5": 9425.0},
     "notes": "400,000 - 50,000 = 350,000; x 0.50 = 175,000; + 60,000 nonbusiness (allocated, NOT apportioned) = 235,000; "
              "- 90,000 NOL = 145,000; x 6.5% = $9,425. Apportioning the nonbusiness earnings would give 205,000 -> $7,475."},
    {"scenario_name": "Schedule J standard deduction floors at zero on a small base", "scenario_type": "edge", "sort_order": 15,
     "inputs": {"j_l31_total_business_income": -80000, "j_l35_apportionment_ratio": 1.0},
     "expected_outputs": {"J-32": 0.0, "J-34": -80000.0, "J-39": -80000.0, "B-5": 0.0},
     "notes": "'enter the lesser of Line 31 or $50,000; if negative, enter zero' — the standard deduction cannot create or increase a loss."},
    {"scenario_name": "Schedule J Line 30 EXCLUDES Line 28b", "scenario_type": "edge", "sort_order": 16,
     "inputs": {"j_l28a_business_interest_deductible": 120000, "j_l28b_business_interest_carryforward": 400000,
                "j_l27_gilti_full": 0, "j_l16_bonus_depr_permitted": 30000},
     "expected_outputs": {"J-30": 150000.0},
     "notes": "L30 = 30,000 + 120,000 = 150,000. Including the informational L28b carryforward would give 550,000 and overstate the deduction by 400,000 ($26,000 of tax)."},
    {"scenario_name": "Schedule N — one ratio serves BOTH taxes", "scenario_type": "normal", "sort_order": 20,
     "inputs": {"sales_factor_tn_receipts": 2000000, "sales_factor_everywhere": 8000000},
     "expected_outputs": {"N-1": 0.25, "F1-4": 0.25, "J-35": 0.25},
     "notes": "Single sales factor, ONE line on the TY2025 form; the same 25% goes to Schedule F1 Line 4 (franchise) and Schedule J Line 35 (excise). No property, no payroll, no 11x/13."},
    {"scenario_name": "Schedule M — spillover standard deduction, capped at Line 9", "scenario_type": "edge", "sort_order": 21,
     "inputs": {"j_l31_total_business_income": 20000, "m_l9_net_nonbusiness_earnings": 75000},
     "expected_outputs": {"J-32": 20000, "M-10": 30000.0, "M-11": 45000.0},
     "notes": "J L32 used only 20,000 of the $50,000; M L10 = min(50,000 - 20,000, 75,000) = 30,000; M L11 = 45,000 -> J L37. Never negative, never above Line 9."},
    {"scenario_name": "Schedule K — the four reversals, apportioned", "scenario_type": "edge", "sort_order": 22,
     "inputs": {"j_l31_total_business_income": -100000, "j_l18_dividends_80pct_owned": 15000,
                "j_l22_nonbusiness_earnings": 10000, "j_l33_optional_addback": 0,
                "j1_l6_self_employment": 45000, "j1_l7_qualified_plan": 15000, "j_l35_apportionment_ratio": 0.40},
     "expected_outputs": {"K-4": -15000.0, "K-6": -6000.0},
     "notes": "-100,000 + (15,000 + 10,000 + 0) + (45,000 + 15,000) = -15,000; x 0.40 = -6,000. Using L31 alone would carry -40,000 — nearly 7x too much loss."},
    {"scenario_name": "Schedule K — reversals cannot turn a loss into income", "scenario_type": "edge", "sort_order": 23,
     "inputs": {"j_l31_total_business_income": -30000, "j_l18_dividends_80pct_owned": 50000,
                "j_l22_nonbusiness_earnings": 0, "j_l33_optional_addback": 0,
                "j1_l6_self_employment": 0, "j1_l7_qualified_plan": 0, "j_l35_apportionment_ratio": 1.0},
     "expected_outputs": {"K-4": 0.0, "K-6": 0.0},
     "notes": "-30,000 + 50,000 = +20,000 -> 'if net amount is positive, enter zero'. Manual p. 298: the reversals 'should never turn an apportioned business loss ... into income'."},
    {"scenario_name": "Schedule J4 — the contributions and capital-loss timing decoupling", "scenario_type": "edge", "sort_order": 24,
     "inputs": {"j4_l1_taxable_income_1120_l28": 500000, "j4_l5_contribution_carryover_used": 40000,
                "j4_l6_capital_gains_offset": 25000, "j4_l8_contributions_excess": 70000,
                "j4_l9_current_capital_loss": 30000},
     "expected_outputs": {"J4-7": 565000.0, "J4-10": 100000.0, "J4-11": 465000.0},
     "notes": "Additions 500,000 + 40,000 + 25,000 = 565,000 (federal carryovers USED are added back); deductions 70,000 + 30,000 = 100,000 (TN allows both IN FULL in the year incurred); total 465,000. Requires a separate Tennessee contribution and capital-loss history."},
    {"scenario_name": "Schedule J2 — individual-owned SMLLC path", "scenario_type": "normal", "sort_order": 25,
     "inputs": {"j2_l1_schedule_c": 120000, "j2_l2_schedule_d": -15000, "j2_l3_schedule_e": 30000,
                "j2_l4_schedule_f": 0, "j2_l5_form_4797": 5000, "j2_l6_other": 0, "j2_l8_self_employment": 90000},
     "expected_outputs": {"J2-7": 140000.0, "J2-9": 50000.0},
     "notes": "140,000 additions less the 90,000 self-employment deduction = 50,000 -> Schedule J Line 1. Schedule D is entered as a NEGATIVE when it is a loss."},
    {"scenario_name": "Schedule C — credit cap with the Green Energy exception", "scenario_type": "edge", "sort_order": 30,
     "inputs": {"a_l3_franchise": 10000, "b_l7_excise": 52000, "non_green_credits": 70000, "d_l2_green_energy_credit": 5000},
     "expected_outputs": {"C-8": 62000.0, "C-9": 67000.0, "C-10": 0.0},
     "notes": "Non-green credits capped at L8 (70,000 -> 62,000) PLUS the uncapped Green Energy Credit (5,000) = 67,000; L10 floors at zero. ⚠ U8/W8: this drives net tax below the $100 franchise minimum on the form's own arithmetic."},
    {"scenario_name": "Schedule T Part 1 — least of Lines 5, 7, 10", "scenario_type": "edge", "sort_order": 31,
     "inputs": {"t_l1_machinery_purchase_price": 3000000, "t_l2_credit_percentage": 0.01, "v_credit_carryover": 10000,
                "a_l3_franchise": 10000, "b_l5_excise": 52000, "sch_d_l1_l4_and_l7": 5000},
     "expected_outputs": {"T-11": 31000.0},
     "notes": "L3 = 30,000; L5 = 40,000; L6 = 10,000 + 52,000 = 62,000; L7 = 31,000; L10 = 62,000 - 5,000 = 57,000; L11 = min(40,000, 31,000, 57,000) = 31,000 — the 50% limitation binds."},
    {"scenario_name": "Estimates — the $5,000-BOTH-years test and the standard installment", "scenario_type": "edge", "sort_order": 40,
     "inputs": {"prior_year_total_liability": 6000, "projected_current_liability": 8000},
     "expected_outputs": {"estimates_required": True, "installment": 1500.0},
     "notes": "Both years clear $5,000, so estimates are required. Installment = min(25% x 6,000 = 1,500; 25% x 80% x 8,000 = 1,600) = 1,500. With prior 4,000 / current 20,000 estimates are NOT required — a single big year does not trigger them."},
    {"scenario_name": "Extension — $100 when the prior year's liability was zero", "scenario_type": "edge", "sort_order": 41,
     "inputs": {"prior_year_total_liability": 0, "projected_current_liability": 20000},
     "expected_outputs": {"extension_payment_required": 100.0},
     "notes": "'If the taxpayer had a zero tax liability for the prior tax year, then the required extension payment is $100.' With prior 15,000 / current 20,000 it is min(90% x 20,000 = 18,000; 100% x 15,000 = 15,000) = 15,000."},
    {"scenario_name": "Schedule G — the 8/3/2/1 rent multiples", "scenario_type": "edge", "sort_order": 50,
     "inputs": {"g_owned_subtotal_l10": 500000, "g_rent_real": 100000, "g_rent_mfg_machinery": 50000,
                "g_rent_furniture_office": 20000, "g_rent_delivery_mobile": 10000},
     "expected_outputs": {"G-15": 1500000.0},
     "notes": "500,000 + (100,000 x 8) + (50,000 x 3) + (20,000 x 2) + (10,000 x 1) = 1,500,000 -> Schedule A Line 2. "
              "Multipliers printed on the current form face. ⚠ Schedule N1 uses x8 for ALL rents and original tax-basis cost — do not share a property model."},
    {"scenario_name": "TCJA bonus percentage — 40% for a 2025-keyed asset (key is W1, not the spec's)", "scenario_type": "edge", "sort_order": 51,
     "inputs": {"key_year": 2025},
     "expected_outputs": {"tn_bonus_pct": 0.40},
     "notes": "TN's frozen TCJA percentage: 2023 80% / 2024 60% / 2025 40% / 2026 20% / 2027+ 0%. ⚠ W1/U2 — WHICH DATE "
              "produces key_year (acquisition or placed-in-service) is Ken's ruling; the spec supplies the percentage, "
              "never the key. An asset acquired 2024 / placed in service 2025 is 60% or 40% depending on that ruling."},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORMS registry + flow assertions
# ═══════════════════════════════════════════════════════════════════════════

FORMS: list[dict] = [
    {
        "identity": {
            "form_number": "TN_FAE170",
            "form_title": "TN Form FAE170 — Tennessee Franchise and Excise Tax Return (TY2025)",
            "notes": (
                "FIRST Tennessee spec. ONE return, TWO separately-computed taxes sharing no base: a 0.25% "
                "franchise tax on the GREATER of net worth (Schedule F1) or the elective Schedule G property "
                "measure, minimum $100; and a 6.5% excise tax on Schedule J net earnings. FOUR entity-branching "
                "entry schedules — J1 (federal 1065, L11), J2 (individual-owned SMLLC, L9), J3 (1120S, L7), J4 "
                "(1120, L11) — converge on a single Schedule J. THREE delvio-tax modules therefore share one "
                "spec. THE CLONE TRAP: J3 has NO self-employment and NO qualified-plan deduction while J1 has "
                "both. ORDERING: the $50,000 standard deduction is PRE-apportionment, the nonbusiness allocation "
                "POST-apportionment, and the NOL LAST. Not a clone of any income-tax state: different base, "
                "different filers (limited liability is the imposition test, not federal classification), "
                "rolling conformity frozen at TCJA §168(k), no PTET, no individual return."
            ),
        },
        "facts": TN170_FACTS,
        "rules": TN170_RULES,
        "rule_links": TN170_RULE_LINKS,
        "lines": TN170_LINES,
        "diagnostics": TN170_DIAGNOSTICS,
        "scenarios": TN170_SCENARIOS,
    },
]

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-TN-J-ENTRY", "title": "Schedule J Line 1 = J1 L11 / J2 L9 / J3 L7 / J4 L11",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S", "1120"], "status": "draft", "sort_order": 1,
     "description": "The four entity-branching entry schedules converge on Schedule J Line 1, and the totals sit on "
                    "DIFFERENT line numbers per schedule: 'Enter the applicable amount from line 11, 9, 7, or 11 of "
                    "Schedule J1, J2, J3, or J4, respectively.' Exactly ONE entry schedule is completed per return.",
     "definition": {"rule": "R-TN-J-ENTRY",
                    "check": "J_L1 == {1065: J1_L11, 1040_smllc: J2_L9, 1120S: J3_L7, 1120: J4_L11}[federal_entity_type]"}},
    {"assertion_id": "FA-TN-J1J3", "title": "J3 has NO self-employment and NO qualified-plan deduction",
     "assertion_type": "flow_assertion", "entity_types": ["1120S"], "status": "draft", "sort_order": 2,
     "description": "THE CLONE TRAP. Schedule J3's deductions are exactly Lines 4 and 5. Schedule J1 Lines 6 "
                    "(self-employment) and 7 (qualified pension) have NO J3 analogue, because an S corporation's "
                    "shareholder wages are already inside federal Form 1120-S Line 22. On identical economics the J3 base "
                    "EXCEEDS the J1 base by exactly J1 L6 + L7, and cloning J1 into J3 understates Tennessee excise tax "
                    "by 6.5% of that amount.",
     "bug_reference": "Pre-emptive: cloning J1 into J3 would overstate the S-corp deduction on every TN 1120S return.",
     "definition": {"rule": "R-TN-J3",
                    "check": "J3_L6 == J3_L4 + J3_L5 ; no self-employment or qualified-plan term exists on Schedule J3"}},
    {"assertion_id": "FA-TN-ORDER", "title": "$50k PRE-apportionment, nonbusiness POST, NOL LAST",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S", "1120"], "status": "draft", "sort_order": 3,
     "description": "Schedule J sequencing is load-bearing: L32 (the $50,000 standard deduction) is applied inside L34, "
                    "BEFORE the ratio; L37 (nonbusiness earnings allocated to Tennessee) is added AFTER L36; L38 (the "
                    "Tennessee NOL) is subtracted LAST. Apportion-first produces a different and wrong answer on every "
                    "multistate return.",
     "definition": {"rule": "R-TN-J-ORDER",
                    "check": "L39 == (L31 - min(max(L31,0),50000) + L33) * L35 + L37 - L38 ; and L39 != (L31*L35) - 50000 + L37 - L38 whenever L35 < 1"}},
    {"assertion_id": "FA-TN-FRANCH-MAX", "title": "Schedule A Line 3 is a live MAX(L1, L2), never a flat rate",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S", "1120"], "status": "draft", "sort_order": 4,
     "description": "Franchise tax is 25c per $100 (or major fraction thereof) on the GREATER of net worth (Line 1) or "
                    "the Schedule G property measure (Line 2). Schedule G is opt-in and RED-deferred, but Line 2 is "
                    "direct-entry so the greater-of stays arithmetically live.",
     "definition": {"rule": "R-TN-A-FRANCH", "check": "A_L3 base == max(A_L1, A_L2) ; NOT A_L1 * 0.0025"}},
    {"assertion_id": "FA-TN-MIN100", "title": "$100 minimum franchise tax survives proration and an excise loss",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S", "1120"], "status": "draft", "sort_order": 5,
     "description": "Tenn. Code Ann. §67-4-2119. The $100 minimum is owed by any registered entity — including an "
                    "inactive one and one whose charter has been revoked but not dissolved — survives short-period "
                    "proration, and is unaffected by a Schedule J loss that zeroes the excise tax.",
     "definition": {"rule": "R-TN-A-FRANCH", "check": "A_L3 >= 100 for every filer, before Schedule C credits"}},
    {"assertion_id": "FA-TN-EXCISE", "title": "Excise = 6.5% of Schedule J L39, floored at zero",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S", "1120"], "status": "draft", "sort_order": 6,
     "description": "Schedule B Line 5 = 6.5% of Schedule J Line 39; 'If Line 4 is a loss, enter zero.' The franchise "
                    "and excise taxes share no base — a loss year still owes the $100 minimum.",
     "definition": {"rule": "R-TN-B-EXCISE", "check": "B_L5 == max(0, J_L39) * 0.065 ; B_L7 == B_L5 + B_L6"}},
    {"assertion_id": "FA-TN-SCHN-ONE", "title": "One Schedule N ratio serves BOTH the franchise and excise taxes",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S", "1120"], "status": "draft", "sort_order": 7,
     "description": "The TY2025 Schedule N is a single sales-factor line whose ratio goes to BOTH Schedule F1 Line 4 "
                    "(franchise) and Schedule J Line 35 (excise). No property line, no payroll line, no 11x/13 divisor. "
                    "Schedule N1 is the exception — it produces two different ratios — and is RED-deferred.",
     "definition": {"rule": "R-TN-SCHN", "check": "F1_L4 == J_L35 == N_L1 whenever Schedule N is the apportionment source"}},
    {"assertion_id": "FA-TN-J30-28B", "title": "Schedule J Line 30 EXCLUDES Line 28b",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S", "1120"], "status": "draft", "sort_order": 8,
     "description": "'Total deductions (add Lines 16 through 29, excluding 28b)' — Line 28b (business interest expense "
                    "carryforward available for future tax years) is INFORMATIONAL ONLY. A spec that sums 16..29 "
                    "inclusive overstates the deduction by the entire carryforward.",
     "definition": {"rule": "R-TN-J-SUBTOT", "check": "J_L30 == sum(J_L16..J_L29) - J_L28b"}},
    {"assertion_id": "FA-TN-SCHK-REV", "title": "Schedule K reverses four deductions and never creates income",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S", "1120"], "status": "draft", "sort_order": 9,
     "description": "The Tennessee loss carryover is NOT Schedule J Line 31. Schedule K reverses J L18 (80%-owned "
                    "dividends), J L22 (nonbusiness earnings), J L33 (the optional addback), and J1 L6+L7 or J2 L8 (the "
                    "SE / qualified-plan deductions) before apportioning, and L4 floors at zero so the reversals can "
                    "never turn an apportioned loss into income.",
     "definition": {"rule": "R-TN-SCHK", "check": "K_L4 == min(0, J_L31 + J_L18 + J_L22 + J_L33 + (J1_L6 + J1_L7 or J2_L8)) ; K_L6 == K_L4 * ratio"}},
    {"assertion_id": "FA-TN-J4-BASIS", "title": "J4 L5/L6/L8/L9 require a separate TN contribution and capital-loss ledger",
     "assertion_type": "flow_assertion", "entity_types": ["1120"], "status": "draft", "sort_order": 10,
     "description": "Tennessee allows charitable contributions and capital losses IN FULL in the year incurred (J4 L8, "
                    "L9) and reverses every federal carryover/carryback when the federal return uses it (J4 L5, L6). The "
                    "app must therefore carry a Tennessee contribution and capital-loss HISTORY per C-corp — a second "
                    "state-basis ledger entirely distinct from the depreciation one.",
     "definition": {"rule": "R-TN-J4", "check": "J4_L7 includes L5 + L6 additions ; J4_L10 == L8 + L9 ; TN history maintained separately from federal"}},
    {"assertion_id": "FA-TN-NO-PTET", "title": "No PTET, no individual return, no owner-level credit",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S", "1120"], "status": "draft", "sort_order": 11,
     "description": "Tennessee has no pass-through entity tax and structurally cannot use one — the Hall income tax was "
                    "repealed for periods beginning on or after 1/1/2021, so there is no owner-level tax to credit "
                    "against. No composite return, no nonresident withholding, no K-1 state tax column. Tennessee "
                    "reaches pass-through income by taxing the ENTITY directly.",
     "definition": {"rule": "R-TN-FILING", "check": "no PTET election, no owner credit, and no K-1 state column exists for TN"}},
    {"assertion_id": "FA-TN-DEPR-OPEN", "title": "No computed rule picks the bonus key or the OBBBA differential line",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S", "1120"], "status": "draft", "sort_order": 12,
     "description": "W1/U2 (acquired vs placed-in-service keying) and W2/U1 (which Schedule J line carries the post-2022 "
                    "OBBBA differential) are both unresolved by the Department. This spec encodes the VERIFIED "
                    "percentages and the two-regime structure but NEVER derives the key and NEVER computes the "
                    "differential — Schedule J Lines 3, 16 and 17 are direct-entry, and D_TN170_BONUS_KEY_W1 / "
                    "D_TN170_OBBBA_BONUS_DIFF fire instead.",
     "definition": {"rule": "R-TN-DEPR-REGIME",
                    "check": "_tn_tcja_bonus_pct requires a caller-supplied key_year ; no calculation rule outputs a TN bonus differential"}},
]


# ═══════════════════════════════════════════════════════════════════════════
# Command
# ═══════════════════════════════════════════════════════════════════════════

class Command(BaseCommand):
    help = (
        "Load the TN_FAE170 spec (Tennessee Franchise & Excise Tax Return, TY2025). "
        "Refuses to seed until Ken sets READY_TO_SEED=True after the in-session review walk (W1-W10)."
    )

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad TN_FAE170 spec (Tennessee Franchise & Excise Tax Return)\n"))
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
                "\nREFUSING TO SEED TN_FAE170: not cleared to seed.\n\n"
                "Content is authored, but seeding is gated until Ken walks the packet and\n"
                "flips the sentinel. The two items that change numbers on ORDINARY returns\n"
                "come first:\n\n"
                "  W1  bonus keyed to ACQUIRED or PLACED IN SERVICE? (ESCALATED —\n"
                "      GATE1_WALK.md item 3; the DOR states both inside one manual)\n"
                "  W2  which Schedule J line carries the post-2022 OBBBA differential?\n"
                "  W3  TN depreciation basis engine in v1, or direct-entry L3/L16/L17?\n"
                "  W4  Schedule G in or out (the greater-of is built either way)\n"
                "  W5  Schedule F2 consolidated net worth\n"
                "  W6  Schedule N1 / O / P / R\n"
                "  W7  which credits v1 computes\n"
                "  W8  credits below the $100 minimum, and the 'major fraction' rounding\n"
                "  W9  franchise proration day-count convention\n"
                "  W10 where the SMLLC (Schedule J2) trigger lives\n\n"
                f"READY_TO_SEED = {READY_TO_SEED} (must be True to proceed)\n\n"
                f"Currently empty / placeholder:\n  {still_empty}\n\n"
                "To proceed: review the module-level data lists (and\n"
                "delvio-states/research/tn_entity_source_brief.md), then set\n"
                "READY_TO_SEED = True. Idempotent via update_or_create."
            )

    def _load_topics(self):
        ct = 0
        for code, name in AUTHORITY_TOPICS:
            _, created = AuthorityTopic.objects.update_or_create(topic_code=code, defaults={"topic_name": name})
            if created:
                ct += 1
        self.stdout.write(f"Topics: {ct} new ({len(AUTHORITY_TOPICS)} in batch)")

    def _load_sources(self) -> dict:
        sources: dict = {}
        for src_data in AUTHORITY_SOURCES:
            src_data = dict(src_data)
            excerpts_data = src_data.pop("excerpts", [])
            topic_codes = src_data.pop("topics", [])
            source, _ = AuthoritySource.objects.update_or_create(
                source_code=src_data["source_code"], defaults=src_data,
            )
            sources[source.source_code] = source
            for exc in excerpts_data:
                exc = dict(exc)
                AuthorityExcerpt.objects.update_or_create(
                    authority_source=source, excerpt_label=exc["excerpt_label"], defaults=exc,
                )
            for tc in topic_codes:
                topic = AuthorityTopic.objects.filter(topic_code=tc).first()
                if topic:
                    AuthoritySourceTopic.objects.get_or_create(authority_source=source, authority_topic=topic)
        for code in EXISTING_SOURCES_TO_REFERENCE:
            src = AuthoritySource.objects.filter(source_code=code).first()
            if src:
                sources[code] = src
            else:
                # EXPECTED for TN_TCA_67_4_2004_IRC_DEF until the Tier-1 conformity
                # batch seeds. Do NOT re-author the source here — one truth per fact.
                self.stdout.write(self.style.WARNING(
                    f"  existing source {code} NOT FOUND — links to it will be skipped"))
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
                    defaults={"support_level": level, "relevance_note": note},
                )
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
                    defaults={"note": f"{source_code} -> {form_code}"},
                )

    def _load_flow_assertions(self):
        for a in FLOW_ASSERTIONS:
            a = dict(a)
            FlowAssertion.objects.update_or_create(assertion_id=a.pop("assertion_id"), defaults=a)
        self.stdout.write(f"  {len(FLOW_ASSERTIONS)} flow assertions")

    def _report_totals(self):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("TN_FAE170 loaded.")
        self.stdout.write(
            f"  TN_FAE170: facts {len(TN170_FACTS)} / rules {len(TN170_RULES)} / lines {len(TN170_LINES)} / "
            f"diag {len(TN170_DIAGNOSTICS)} / tests {len(TN170_SCENARIOS)} / FA {len(FLOW_ASSERTIONS)}"
        )
        self.stdout.write("  Serves 1065 + 1120S + 1120 from ONE spec (plus the J2 individual-owned SMLLC path).")
        self.stdout.write("=" * 60)
