"""Load the TX Franchise (margin) Tax specs — TX_05_158 (+ EZ branch) / TX_05_102 PIR / TX_05_167 OIR.

═══════════════════════════════════════════════════════════════════════════
WHAT THIS IS — a MARGIN tax, **NOT** an income tax
═══════════════════════════════════════════════════════════════════════════
Texas has NO income tax of any kind — no individual income tax (constitutionally
prohibited, Tex. Const. art. VIII §24-a), no corporate income tax, no PTET, no
local income tax, no composite return, no nonresident withholding. What it has is
the **franchise ("margin") tax** under Tex. Tax Code ch. 171: an ENTITY-LEVEL tax
on *margin*, a gross-receipts-derived base with NO relationship to federal taxable
income.

**MOST INCOME-TAX SPEC SHAPES DO NOT APPLY HERE.** There is no federal-AGI or
federal-taxable-income starting point, no addback/subtraction schedule, no K-1
state column, no owner credit, no PTET. Total revenue is assembled from ~30 NAMED
FEDERAL FORM LINES (Items 1-7), not from a federal income figure. Do not port a
GA-600 / SC1065 / AL-20C shape onto this file.

Texas is also the INVERSE of every income-tax state on filing: a Texas *individual*
client generates no Texas filing at all, while a Texas *entity* client generates a
filing (or at minimum an information report) even when it owes nothing and even
when it has zero Texas receipts.

═══════════════════════════════════════════════════════════════════════════
⚠⚠ **THE YEAR MAPPING — READ THIS TWICE. IT IS THE EASIEST THING IN THE WHOLE
CAMPAIGN TO GET BACKWARDS.**
═══════════════════════════════════════════════════════════════════════════
Texas labels reports by **REPORT YEAR = the calendar year the report is DUE**, and
the report is based on the accounting period **ending in the PRIOR calendar year**.

    **Delvio TY2025  ==  the TEXAS 2026 ANNUAL FRANCHISE TAX REPORT, due 05/15/2026.**

    **A document labelled "2025 Texas report" is TY2024 and is the WRONG SOURCE.**

`FORM_TAX_YEAR = 2025` below is **Delvio's** convention (the accounting period
ending in calendar 2025). **Every form, instruction, rate, threshold and figure in
this file is the 2026-REPORT version** — 05-915 **Rev. 4-26/2**, 05-158-A/B
**Rev.8-25/11**, 05-169 **Rev.9-23/9**, 05-102 **Rev.2-24/35**, 05-167 **Rev.2-24/8**.
All annual forms carry the preprinted report year `2026` and due date `05/15/2026`
on the form face — that is the byte-level proof of the right-year documents.

Verbatim, 05-915 (Rev. 4-26/2), *Annual Reports -> Report Year*: "The year in which
the franchise tax report is due. The 2026 annual report is due May 15, 2026." And
*Accounting Period*: "if the 2025 annual franchise tax report had an end date of
12-31-2024, then the begin date on the 2026 annual franchise tax report should be
01-01-2025."

If a future maintainer finds a "2025 Texas report" PDF in a re-verification pass,
that is TY2024 and must be discarded, not used.

═══════════════════════════════════════════════════════════════════════════
v1 SCOPE — proposed (tx_entity_source_brief.md §12; NOT yet walked with Ken)
═══════════════════════════════════════════════════════════════════════════
COMPUTES (v1):
  • **THE FILING-OBLIGATION GATE — five outcomes, evaluated FIRST.** It decides
    whether the software produces anything at all:
      (A) not a taxable entity / no nexus / new veteran-owned  -> NOTHING
      (B) passive entity or qualifying REIT                    -> STUB REPORT
          (passive files NO PIR/OIR; a REIT DOES file one)
      (C) annualized total revenue <= $2,650,000               -> **PIR or OIR ONLY;
          NO FRANCHISE REPORT EXISTS.** Form 05-163 was discontinued — the
          Comptroller's 2026 forms page states outright: "The No Tax Due Report is
          not available for 2026 reports."
      (D) annualized total revenue <= $20,000,000              -> OPTIONAL EZ path
      (E) otherwise                                            -> LONG FORM
    Plus the **$500,000 economic-nexus** test — 34 TAC §3.586, verbatim: nexus
    exists "for each federal income tax accounting period ending in 2019 or later
    ... if during that federal income tax accounting period, it had gross receipts
    from business done in Texas of $500,000 or more." The trigger is the ENTITY'S
    ACCOUNTING PERIOD, not the report due date; nexus BEGIN DATE is the FIRST DAY
    of that period, not the crossing date.
    Both side branches: zero Texas gross receipts (factor 0, still files (D)/(E),
    NOT (C)) and the first-annual zero report.
  • **PIR vs OIR routing** — PIR (05-102) = corporations, LLCs, **LPs**,
    professional associations, financial institutions. OIR (05-167) = GPs, **LLPs**,
    trusts, JVs, business associations, other legal entities. An LLP is NOT an "LP".
    Three carve-outs where NEITHER is filed: **FINAL reports**, passive entities,
    new veteran-owned businesses in the initial five-year period.
  • **Total revenue Items 1-10** from the federal line map (as NAMED FACTS — see W6),
    incl. the Item 3 non-negative rule and the Item 4 -> Item 7 -> Item 9 K-1 rental
    interlock; Item 10 floored at zero.
  • **Annualization** — total revenue / days in period × 365, applied ONLY to the
    threshold and EZ-eligibility tests. "The amount of total revenue used in the tax
    calculations does NOT change as a result of annualizing total revenue."
  • **COGS subtotal Items 11-14** with the 4% cap computed on Item 12 and the sign
    rules on Item 13. (Item 11 itself is DIRECT-ENTRY — see below.)
  • **Compensation Items 15-18** — the **$480,000 per-person cap on Item 15 ONLY**,
    **Item 16 employee benefits UNCAPPED**, uncapped negative NDI.
  • **MARGIN = THE LOWEST OF FOUR (Items 19-23)**, each branch floored at zero
    BEFORE the minimum: 70% of revenue · revenue - COGS · revenue - compensation ·
    **revenue - $1,000,000**. The $1M branch is REAL, is on the form face, and often
    WINS for a small labor-light service entity. The industry shorthand "revenue
    minus the greatest of COGS / compensation / 30% of revenue" silently DROPS it.
  • **Apportionment Items 24-26** — zero rule, both 1.0000 rules, 4-decimal rounding.
  • **Items 27-31, 33-35** — rate selection from the **SIC field with the blank =>
    0.75% default**, Item 33's zero floor, Item 34 identically 0, Item 35 == Item 33.
  • **The EZ path** as an INTERNAL COMPUTATION BRANCH of TX_05_158 (see W2) plus a
    separate 05-169 render target, incl. the total credit/deduction forfeiture, and a
    both-paths comparison surfaced as a RECOMMENDATION, never a silent default.
  • **The <$1,000 no-payment rule** and its tiered-partnership override.

DIRECT-ENTRY (line exists, diagnostic prompts, no computation):
  • **Item 11 Cost of goods sold** — 05-915 says outright this figure "cannot be
    found on a federal income tax report" or on an income statement: "It is a
    calculated amount specific to Texas franchise tax." NEVER derive it from a
    federal COGS figure.
  • Item 12 indirect/administrative overhead BASE (the 4% cap is computed).
  • Items 13 and 17 "Other" (undocumented worker / active duty / aerospace).
  • Item 9 exclusions (closed list, per-category grid, computed subtotal).
  • Items 24 / 25 Texas and everywhere gross receipts (Rule 3.591 sourcing).
  • Item 28 allowable deductions; Item 32 credits (05-181 Item 17).
  • SIC and NAICS codes; PIR sections A/B/C and OIR sections A/B rosters.

RED-DEFERS (R1-R10 — each with its OWN "prepare manually" diagnostic):
  R1 one-time net depreciation catch-up + carryforward   D_TX_DEPR_CATCHUP
  R2 combined groups (05-166 / 05-177)                   D_TX_COMBINED
  R3 tiered partnership election (05-175)                D_TX_TIERED
  R4 credits (05-181 / 05-182 / 05-180 / 05-185)         D_TX_CREDITS
  R5 final reports (05-158-f / 05-169-f)                 D_TX_FINAL
  R6 extensions (05-164 / 05-165)                        D_TX_EXT
  R7 fiduciary / business trusts                         D_TX_TRUST
  R8 §171.106 special apportionment                      D_TX_SPECIAL_APPT
  R9 PEO / management co. / healthcare institution       D_TX_SPECIAL_ENTITY
  R10 amended reports                                    D_TX_AMENDED

EXPLICITLY NOT IN v1: e-file transmission. Texas runs its OWN standalone
Comptroller-approved Franchise Tax Web Service (transmitter registration ->
Comptroller testing -> approval BEFORE public release), separate from IRS MeF, plus
a separate 2D-barcode substitute-forms approval requiring the exact version strings
"TX2026" and "Ver. 17.0".

═══════════════════════════════════════════════════════════════════════════
requires_human_review WALK ITEMS — W1 and W6 FIRST (both LOAD-BEARING)
═══════════════════════════════════════════════════════════════════════════
**W1. THE ASSET-LEVEL BONUS DATE GATE — ESCALATED KEN JUDGEMENT CALL.**
    `GATE1_WALK.md` item 4 / [UNVERIFIED] U1. **DO NOT GUESS AND DO NOT PICK A KEY
    IN A COMPUTED RULE.** Four official sources, three scopes, one silence:
      · STAR memo **202603002M** (3/12/2026, CONTROLLING) — bonus includable for
        assets "placed in service on or after January 19, 2025."
      · Comptroller **news release** (12/1/2025) — assets "acquired after Jan. 19, 2025."
      · **Adopted Rule 3.588** (eff. 6/21/2026) — no ASSET-LEVEL date gate.
      · **Form 05-915 (Rev. 4-26/2)**, the FINAL 2026 instructions published AFTER the
        memo — no asset-level date gate, no dollar limit; ZERO occurrences of
        "January 19"/"Jan. 19"/"19, 2025" in the 33-page booklet.
    **THE REPORT-YEAR GATE IS NOT IN DISPUTE** — all four sources agree the change
    begins with the 2026 franchise tax report. What IS disputed is whether an
    INDIVIDUAL ASSET carries a placed-in-service / acquired date test. Precision
    matters: the rule and the instructions are NOT "silent about timing" (they carry
    a report-year qualifier); they are silent about WHICH ASSETS QUALIFY BY DATE.
    Why it is not academic: federal OBBBA keys 100% bonus to ACQUISITION after
    1/19/2025 with 40% for property acquired earlier — so an asset acquired Dec 2024
    and placed in service Aug 2025 passes the news release's test, FAILS the memo's
    test, and is unaddressed by the rule and the instructions. Common, not edge.
    RECOMMENDATION (brief §9, unchanged): build to PLACED IN SERVICE ON OR AFTER
    1/19/2025, flagged, and email the Comptroller — but record it as a DECISION, not
    a finding. **This file encodes NO date key.** Diagnostic `D_TX_BONUS_DATE_GATE`
    only. Contact: tax policy via STAR / Tax Policy Division.

**W6. FEDERAL-FORM VINTAGE MISMATCH — TREAT AS BLOCKING.**
    [UNVERIFIED] U2. 05-915 (Rev. 4-26/2) states verbatim: "The line items indicated
    in this section refer to specific lines from the **2024** Internal Revenue Service
    (IRS) forms, which are the most current available at the time of publication."
    But the 2026 report is built on an accounting period ending in calendar **2025**,
    i.e. a **2025** federal return. **THE FEDERAL LINE MAP FROM 05-915 IS THEREFORE
    NOT HARD-CODED IN THIS FILE.** The federal handoff is encoded as NAMED FACTS
    (`fed_gross_receipts_or_sales`, `fed_dividends`, ...) with diagnostic
    `D_TX_FED_LINE_MAP` requiring the mapping to be re-verified line-by-line against
    the FINAL 2025 federal forms (1120, 1120S, 1065, 1041, Sch C/E/F, 8825, 4797,
    Sch D) BEFORE the app build. The booklet also warns "federal line numbers are
    subject to change throughout the year," and the statute pins the map to 2006-form
    EQUIVALENTS, so the map is a per-report-year DATA TABLE, not a constant.
    The §4 map is the module's spine; if any line moved, the map ships wrong.

W2. **EZ scoping.** Encoded per the brief's recommendation: **ONE rule spec
    (`TX_05_158`) owning the shared revenue build and BOTH tax paths, with the EZ as
    an internal computation branch and a SEPARATE 05-169 print/e-file render target.**
    10 of the EZ's 17 items are BARE cross-references to the long form (Items 1-8, 10,
    13); Item 9 adds the EZ COGS/compensation bar and Items 11-12 add Rule 3.591
    pointers; Items 11-13 point at 05-158-**B**. Two copies of the ~30-cell federal
    line map plus the 30+-category exclusion list would drift within one year.
    FALLBACK if RS cannot express one-spec-two-render-targets: a thin `TX_05_169`
    that REFERENCES TX_05_158's facts. **What must NOT happen is two independent
    copies of the revenue build.**

W3. **COGS = DIRECT-ENTRY in v1** (Item 11). 05-915: the figure "cannot be found on
    a federal income tax report." Computing it means modelling a 25-item inclusion
    list, a 14-item exclusion list, the §263A/460/471 expense-vs-capitalize election
    and the 4% mixed-service-cost cap — a spec of its own scale. CONFIRM.

W4. **Depreciation catch-up = RED-DEFER** (R1). See the OPEN ITEMS block below.

W5. **Combined groups and tiered partnerships = RED-DEFER both** (R2, R3). Combined
    reporting is verbatim "mandatory" where it applies, so the diagnostic must be
    LOUD — a silent separate-entity report for a unitary group is a WRONG RETURN,
    not an incomplete one. Ask Ken how many TX clients this touches before sizing v2.

W7. **$480,000 proration formula** ([UNVERIFIED] U3). 05-915 says the cap is
    "prorated for the period upon which the tax is based" but gives NO FORMULA
    ("prorat" appears exactly once in the booklet, in that sentence). Days / 365?
    Whole months? The same 365-day convention as revenue annualization? **Do NOT
    assume the annualization convention carries over** — that is exactly the
    plausible guess the Authoritative-Source Rule forbids. Widened by correction C6:
    05-915 states the cross-member cap TWICE with different denominators — "upon
    which the **report** is based" (Combined Group) vs "upon which the **tax** is
    based" (Item 15). Harmless at 12 months; ambiguous for a short period. Pull 34
    TAC §3.589 before coding short periods, or direct-enter the prorated cap.
    This file exposes `comp_cap_proration_factor` as a DIRECT-ENTRY fact defaulting
    to 1.0 and does not invent a proration formula.

W8. **Both-paths recommendation UI.** The EZ taxes apportioned REVENUE, not margin.
    Break-even vs the 0.75% long form is a margin of **44.13%** of revenue
    (0.00331 / 0.0075); vs the 0.375% retail rate it is **88.27%** — and since the
    four-way minimum caps margin at 70% of revenue, **a qualifying retailer or
    wholesaler should NEVER elect the EZ.** The EZ also forfeits ALL credits and
    permanently destroys the current year's temporary-credit-for-BLC portion.
    Confirm Ken wants Delvio to compute both and RECOMMEND rather than default.

W9. **E-file lead time** ([UNVERIFIED] U9, Ken-only). Transmitter registration +
    Comptroller testing must complete BEFORE public release; the 2D-barcode track
    needs the exact strings "TX2026" / "Ver. 17.0". No published calendar exists.
    Start the email (XMLBusiness@cpa.texas.gov) independent of spec work.

═══════════════════════════════════════════════════════════════════════════
OPEN ITEMS — FLAGGED, NEVER GUESSED
═══════════════════════════════════════════════════════════════════════════
**THE ONE-TIME NET DEPRECIATION CATCH-UP IS A RED-DEFER (R1).** Four structural
facts, all CONFIRMED and now double-sourced (05-915 Item 11 AND adopted Rule 3.588
subparagraph (B)):
  1. **It has NO LINE OF ITS OWN.** It is absorbed into **Item 11** and is invisible
     on the filed form — not Item 12, not Item 13, not disclosed on 05-158-A/B,
     05-166, 05-169, 05-181 or any 2026 schedule.
  2. **The zero floor is PER ASSET**, and the per-asset framing is in the ADOPTED
     RULE, not merely in the instructions: "Add together the depreciation adjustment
     for each year to arrive at the net depreciation adjustment for **that qualifying
     asset** ... The net depreciation adjustment cannot be less than zero."
     Negative-net assets floor at zero INDIVIDUALLY and do NOT offset positive-net
     assets. A single entity-level sum with one floor produces a materially smaller
     deduction and is the obvious implementation bug.
  3. **A second, entity-level limiter is CIRCULAR.** The catch-up is admitted only
     "to the extent the adjustment does not take the taxable entity's margin below
     zero" — that is **margin (Item 23)**, not COGS and not apportioned margin. Adding
     catch-up to COGS raises Item 14, lowers Item 20, and can CHANGE WHICH BRANCH IS
     THE MINIMUM. It must be solved as "the largest catch-up such that Item 23 >= 0",
     never as a one-pass subtraction. (Nuance: Item 23's own instruction already
     floors margin at zero, so "does not take margin below zero" must be read against
     the PRE-FLOOR computation or it is vacuous.)
  4. **The carryforward has NO FORM FIELD ANYWHERE.** "Any unused net depreciation
     adjustment may be carried forward to consecutive reports until exhausted" — but
     no 2026 line, schedule or attachment records the balance and no 2027 form
     exists. It is a Delvio-side fact that must survive across report years with no
     external reconciliation point.
Plus: a per-asset, per-year history of (federal depreciation claimed, Texas-COGS
depreciation claimed) from each asset's in-service date through the accounting-year-
end date on the 2025 report — data Delvio does not hold for any client whose prior
preparer was not Delvio. Not amendable ("intended to be prospective"); the only
disposal test is the qualifying-asset gate. ITC-reduced basis governs both.
=> **Diagnostic `D_TX_DEPR_CATCHUP` only. NO COMPUTATION.**

**ALL NINE [UNVERIFIED] ITEMS (tx_entity_source_brief.md §13), carried:**
  U1 **Bonus-depreciation ASSET-LEVEL date gate** — OPEN, correctly escalated.
     Four sources, three scopes. Ken's call (W1). Not resolvable from published
     sources; needs a Comptroller ruling. **LOAD-BEARING.**
  U2 **Federal-form vintage (2024 cited vs 2025 actual)** — OPEN and CONFIRMED REAL;
     the verbatim "2024" sentence is in the FINAL booklet. **LOAD-BEARING / BLOCKING
     (W6).**
  U3 **$480,000 proration formula** — OPEN. 05-915 gives no formula. Widened by C6
     ("report" vs "tax" basis). Needs 34 TAC §3.589. Affects every short period.
  U4 **Net-depreciation-adjustment carryforward has no reporting home** — OPEN but
     narrowed; absence re-confirmed against all 2026 forms and both form indexes.
     Only the 2027 forms can close it.
  U5 **34 TAC §3.589 (Margin: Compensation) not read** — OPEN. Per-person cap
     mechanics across short periods and mid-year hires, officer/director/owner
     definitions and NDI edge cases rest on 05-915's summary alone.
  U6 **34 TAC §3.587 / §3.588 full adopted text** — PARTIALLY RESOLVED (adoption
     preamble read; §179 deletion, §197 pinning and the per-asset catch-up confirmed).
     Section-by-section codified text unread. ⚠ The obvious `txrules.elaws.us` mirror
     serves STALE pre-amendment (2008) §3.588 text that still contains the deleted
     §179 reference — **do not "confirm" against it and reinstate the dead $25,000 cap.**
  U7 **34 TAC §3.591 sourcing detail** — OPEN. Throwback/throwout ABSENCE is
     confirmed; the operative service/intangible/receipt-by-receipt sourcing text was
     read only in 05-915 summary form. Close before Item 24/25 guidance ships.
  U8 **34 TAC §3.581 trust mapping** — OPEN, low urgency (fiduciary is the on-demand
     lane and is RED-deferred, R7).
  U9 **Developer-program calendar** — OPEN, Ken-only, lead-time-bearing (W9).

**ALSO NOT ENCODED AS COMPUTATION, deliberately:** no Texas §179 dollar cap exists
for the 2026 report (adopted Rule 3.588 DELETES the rule's IRC §179 reference, which
was the sole source of the old $25,000 / $200,000 limit). Encode "the federal amount
as claimed" — **NOT** a hardcoded Texas cap and **NOT** a literal "unlimited."

═══════════════════════════════════════════════════════════════════════════
VERIFIED-STRUCTURE PROVENANCE — exact form revisions
(READ from the FINAL 2026-REPORT Texas Comptroller PDFs, downloaded locally by curl
and text-extracted with PyMuPDF — NOT memory, NOT training data, NOT a prior report
year, NOT a commercial publisher summary. WebFetch returns these PDFs as undecoded
binary and cannot be relied on for them. Adversarial verification pass 2026-08-16:
every byte size and /ModDate reproduced EXACTLY; report-year check CLEAN.
Full source brief: delvio-states/research/tx_entity_source_brief.md (VERIFIED);
conformity: delvio-states/conformity/tx_conformity.md (VERIFIED 2026-08-06).)
═══════════════════════════════════════════════════════════════════════════
  05-915   2026 Franchise Tax Report Information and Instructions
           **Rev. 4-26/2** — FINAL, 33 pp., /ModDate 2026-05-06, 1,220,070 bytes
  05-158-A 2026 Texas Franchise Tax 2025 Annual Report, p.1 of 2
           **(Rev.8-25/11)**, Tcode **13250 Annual**, /ModDate 2025-12-02, 313,988 bytes
  05-158-B same PDF, p.2 of 2 — **(Rev.8-25/11)**, Tcode **13251 Annual**
  05-158-f 2026 Texas Franchise Tax 2025 FINAL Report
           **(Rev.8-25/11)**, Tcodes **13270 / 13271 Final**, 303,716 bytes.
           Items 1-35 numbering and labels IDENTICAL to the annual (re-diffed), but
           FOUR real field differences: the FINAL OMITS the PIR/OIR routing question
           (which independently corroborates the no-PIR/OIR-with-a-final-report rule
           from the form face itself), ADDS "Blacken circle to request a Certificate
           of Account Status," carries NO preprinted due date, and uses different
           Tcodes. One line map serves both; the render target differs in 4 places.
  05-169   Texas Franchise Tax 2026 E-Z Computation Annual Report
           **(Rev.9-23/9)**, Tcode **13252 Annual**, /ModDate 2025-12-03, 273,777 bytes
  05-102   2026 Texas Franchise Tax Public Information Report
           **(Rev.2-24/35)**, Tcode **13196 Franchise**, /ModDate 2025-12-02, 395,199 bytes
  05-167   Texas Franchise Tax Ownership Information Report
           **(Rev.2-24/8)**, Tcode **13197**, /ModDate 2025-12-03, 218,773 bytes
  05-166 Affiliate Schedule (report years 2026 and later) · 05-175 Tiered Partnership
  Report · 05-177 Common Owner Information Report · 05-170 Payment · 05-181 Credits
  Summary Schedule (new for 2026, replaces 05-160) · 05-164 Extension Request.
  **05-163 (No Tax Due Report) DOES NOT EXIST FOR 2026** — absent from the 2026 forms
  index and from the 05-915 form list; the forms page says outright: "The No Tax Due
  Report is not available for 2026 reports."
  Statute: Tex. Tax Code §§171.0001(9), 171.0002, 171.002, 171.0003, 171.006,
  171.1011, 171.1012, 171.1013. Rules: 34 TAC §3.586 (nexus, amended 2/10/2021),
  §3.587 (total revenue), §3.588 (COGS, adopted 6/1/2026 eff. **6/21/2026**),
  §3.591 (apportionment). Controlling policy: **STAR 202603002M (3/12/2026)**, which
  "updates and replaces" STAR 202512012M (12/19/2025) — **do not cite the dead memo.**

GAP-CHECK: all TX form codes returned 404 against RS prod (`lookup/<FORM>/export/`),
confirmed 2026-08-15 by [WO-W02-ENT] — TX_05_158, TX_05_169, TX_05_102, TX_05_167
included. NEW forms; no prior RS spec exists.

═══════════════════════════════════════════════════════════════════════════
SAFETY GUARD — **READY_TO_SEED SHIPS False.**
It stays False until Ken approves the review walk (W1-W9) in-session. Until then the
command REFUSES to write to the DB. **DO NOT relax the guard to silence the error.**
W1 (the asset-level bonus date gate) and W6 (the federal-form vintage) are
LOAD-BEARING and W6 is BLOCKING — the §4 federal line map must be re-verified
against the FINAL 2025 federal forms before this spec drives an app build.
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
# SAFETY GUARD — flip ONLY after Ken's in-session review walk (W1-W9 above).
# NOT FLIPPED. W1 is an escalated Ken judgement call and W6 is BLOCKING.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = False


FORM_JURISDICTION = "TX"
# Delvio's convention: TY2025 = the accounting period ending in calendar 2025
# = the TEXAS **2026** ANNUAL REPORT, due 05/15/2026. See the year-mapping block.
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"
TX_REPORT_YEAR = 2026
TX_REPORT_DUE_DATE = "05/15/2026"

# The margin tax reaches most entities REGARDLESS of federal classification —
# "An entity's treatment for federal income tax purposes does not determine its
# responsibility for Texas franchise tax." A federally disregarded single-member LLC
# files its OWN Texas report.
FORM_ENTITY_TYPES = ["1065", "1120S", "1120"]


# ═══════════════════════════════════════════════════════════════════════════
# VERIFIED CONSTANTS — TY-keyed (Delvio TY2025 == the TEXAS 2026 REPORT).
# Every figure below is quoted from the FINAL 2026-report sources; none from memory.
# A NEW TAX YEAR STALENESS-INVALIDATES ALL OF THEM until re-verified.
# ⚠ The threshold and the compensation cap are BIENNIAL under §171.006(b): both are
# fixed for reports originally due on or after Jan. 1, 2026 and before Jan. 1, 2028,
# then re-adjust. Calendar a re-verification for the 2028 report cycle.
# ═══════════════════════════════════════════════════════════════════════════

# "For the 2026 Franchise Tax Report, the no tax due threshold is $2,650,000..."
# (05-915, Important Reminders for 2026). Statutory base $2.47M, §171.002(d)(2),
# biennially adjusted under §171.006(b). Test is "less than OR EQUAL TO".
TX_NO_TAX_DUE_THRESHOLD: dict[int, int] = {2025: 2_650_000}

# "Any entity (including a combined group) that has annualized total revenue of
# $20 million or less is eligible" for the EZ computation. (05-915.)
TX_EZ_REVENUE_CEILING: dict[int, int] = {2025: 20_000_000}

# "The limit on the compensation deduction has been adjusted to $480,000 per person.
# Effective for reports originally due on or after Jan. 1, 2026, and before Jan. 1,
# 2028. Tax Code Section 171.006(b)." (05-915 p.2.)
# ⚠ ITEM 15 ONLY. Item 16 employee benefits are expressly NOT subject to it.
TX_COMP_CAP_PER_PERSON: dict[int, int] = {2025: 480_000}

# Item 22, on the form face: "Revenue less $1 million (Item 10 - $1,000,000)".
# THE FOURTH MARGIN BRANCH. Not indexed; a flat statutory $1,000,000.
TX_MARGIN_1M_DEDUCTION: dict[int, int] = {2025: 1_000_000}

# Rates, unchanged for reports originally due on or after Jan. 1, 2016.
TX_RATE_STANDARD: dict[int, str] = {2025: "0.0075"}            # most entities
TX_RATE_RETAIL_WHOLESALE: dict[int, str] = {2025: "0.00375"}   # qualifying retail/wholesale
TX_RATE_EZ: dict[int, str] = {2025: "0.00331"}                 # EZ, hardcoded on 05-169 Item 15

# 34 TAC §3.586: nexus "for each federal income tax accounting period ending in 2019
# or later ... if during that federal income tax accounting period, it had gross
# receipts from business done in Texas of $500,000 or more."
# ⚠ Keyed to the ENTITY'S ACCOUNTING PERIOD, not the report due date.
TX_ECONOMIC_NEXUS_RECEIPTS: dict[int, int] = {2025: 500_000}

# "an entity that calculates an amount of tax due that is less than $1,000 is not
# required to pay any tax.... The entity, however, must submit all required reports."
# STRICTLY less than. Exactly $1,000 IS payable.
TX_MIN_PAYMENT_FLOOR: dict[int, int] = {2025: 1_000}

# Item 12: "This amount is limited to 4% of total indirect/administrative overhead costs."
TX_OVERHEAD_CAP_PCT: dict[int, str] = {2025: "0.04"}

# Item 19: "Item 10 times 70%. If less than zero, enter zero."
TX_MARGIN_70PCT: dict[int, str] = {2025: "0.70"}

# "divide total revenue by the number of days in the period, multiply the result by 365"
TX_ANNUALIZATION_DAYS: dict[int, int] = {2025: 365}

# Item 26: "round to 4 places past the decimal".
TX_APPORTIONMENT_DECIMALS: int = 4

# 05-102 (PIR) is filed by the ENUMERATED list; 05-167 (OIR) is EVERYTHING ELSE.
# Verbatim 05-915: "Each corporation, limited liability company (LLC), limited
# partnership, professional association and financial institution that has a
# franchise tax responsibility must file a Public Information Report (PIR) to satisfy
# their filing requirements." / "The Ownership Information Report (OIR) is to be filed
# for each taxable entity other than a legally formed corporation, limited liability
# company, limited partnership, professional association or financial institution."
# ⚠ An LLP is NOT an "LP" — LLPs file the OIR.
TX_PIR_LEGAL_FORMS: frozenset = frozenset({
    "corporation", "c_corporation", "s_corporation", "professional_corporation",
    "llc", "single_member_llc", "series_llc",
    "limited_partnership",
    "professional_association",
    "financial_institution", "bank", "state_limited_banking_association", "savings_and_loan",
})
TX_OIR_LEGAL_FORMS: frozenset = frozenset({
    "general_partnership", "llp", "limited_liability_partnership",
    "trust", "business_trust",
    "joint_venture", "business_association", "other_legal_entity",
})

# Filing-gate outcome codes (see _tx_filing_outcome).
TX_OUTCOME_NOTHING = "A_NOTHING"       # not taxable / no nexus / new veteran-owned
TX_OUTCOME_STUB = "B_STUB"             # passive entity or qualifying REIT
TX_OUTCOME_INFO_ONLY = "C_INFO_ONLY"   # <= threshold: PIR/OIR ONLY, NO franchise report
TX_OUTCOME_EZ = "D_EZ"                 # <= $20M and EZ elected
TX_OUTCOME_LONG = "E_LONG"             # long form 05-158-A/B


def _yk(d: dict, year: int):
    """Year-key a constant, falling back to the authored TY2025 (= 2026 report) value."""
    return d.get(year) if d.get(year) is not None else d[2025]


# ═══════════════════════════════════════════════════════════════════════════
# COMPUTATION HELPERS
# Module-level so the throwaway-SQLite harness (scratchpad/validate_tx.py) can drive
# arithmetic oracles against the SAME code the rules describe.
#
# ⚠ NONE of these encodes an asset-level bonus-depreciation date key (W1), and NONE
# hard-codes a federal form line number (W6). Both omissions are deliberate.
# ═══════════════════════════════════════════════════════════════════════════


def _tx_has_nexus(*, organized_in_texas: bool = False, physical_presence_in_texas: bool = False,
                  texas_receipts_this_accounting_period: float = 0.0,
                  has_texas_use_tax_permit: bool = False, year: int = 2025) -> bool:
    """34 TAC §3.586. Organized in TX, or doing business in TX.

    ECONOMIC NEXUS: $500,000+ of Texas gross receipts, no physical presence needed,
    tested on the ENTITY'S FEDERAL INCOME TAX ACCOUNTING PERIOD (ending in 2019 or
    later) — NOT on the report due date. Nexus BEGIN DATE is the FIRST DAY of that
    period, not the day the threshold was crossed (a date fact, not modelled here).
    This is the cheapest filter in the module: it gates out-of-state clients entirely.
    """
    if organized_in_texas or physical_presence_in_texas or has_texas_use_tax_permit:
        return True
    return texas_receipts_this_accounting_period >= _yk(TX_ECONOMIC_NEXUS_RECEIPTS, year)


def _tx_info_report(legal_form: str, *, is_final_report: bool = False,
                    is_passive_entity: bool = False, is_new_veteran_owned: bool = False):
    """PIR (TX_05_102) vs OIR (TX_05_167) — a clean complement, plus THREE carve-outs.

    Carve-outs where NEITHER is filed:
      1. FINAL REPORTS — "A Public Information Report (Form 05-102) or an Ownership
         Information Report (Form 05-167) is NOT required to be filed with the final
         report." (Corroborated from the form face: the FINAL 05-158 OMITS the
         PIR/OIR routing question the annual carries.)
      2. PASSIVE ENTITIES — "A passive entity is not required to file a Public
         Information Report or Ownership Information Report." (A REIT, by contrast,
         DOES file one.)
      3. NEW VETERAN-OWNED BUSINESSES during the initial five-year period.

    Do NOT hardwire "every Texas entity produces a PIR or an OIR."
    """
    if is_final_report or is_passive_entity or is_new_veteran_owned:
        return None
    if legal_form in TX_PIR_LEGAL_FORMS:
        return "TX_05_102"
    return "TX_05_167"


def _tx_annualized_revenue(total_revenue: float, days_in_period: int, year: int = 2025) -> float:
    """05-915: "divide total revenue by the number of days in the period, multiply by 365."

    ⚠ Used ONLY to test the no-tax-due threshold and EZ eligibility.
    "The amount of total revenue used in the tax calculations does NOT change as a
    result of annualizing total revenue."
    """
    if not days_in_period or days_in_period <= 0:
        return float(total_revenue)
    return float(total_revenue) / float(days_in_period) * float(_yk(TX_ANNUALIZATION_DAYS, year))


def _tx_filing_outcome(*, is_taxable_entity: bool = True, has_nexus: bool = True,
                       is_new_veteran_owned: bool = False, is_passive_entity: bool = False,
                       is_qualifying_reit: bool = False, annualized_total_revenue: float = 0.0,
                       ez_elected: bool = False, tiered_partnership_election: bool = False,
                       is_final_report: bool = False, legal_form: str = "llc",
                       year: int = 2025) -> dict:
    """⚠ THE FILING GATE — evaluate FIRST. It decides whether ANYTHING is emitted.

    FIVE distinct outputs. The most common one for a small-firm client base is
    "an information report only, no tax return."

    Returns {outcome, franchise_report, render_target, info_report, reason}.
    """
    threshold = _yk(TX_NO_TAX_DUE_THRESHOLD, year)
    ez_ceiling = _yk(TX_EZ_REVENUE_CEILING, year)

    # STEP 1 — taxable entity? (§171.0002; 05-915 "Entities Subject/Not Subject to Tax")
    # ⚠ Federal disregarded status is IRRELEVANT: "entities that are disregarded for
    # federal income tax purposes are considered separate legal entities for franchise
    # tax reporting purposes." A federally disregarded SMLLC files its OWN report.
    if not is_taxable_entity:
        return {"outcome": TX_OUTCOME_NOTHING, "franchise_report": None, "render_target": None,
                "info_report": None,
                "reason": "Not a taxable entity under Tex. Tax Code §171.0002 (e.g. a sole "
                          "proprietorship other than a single-member LLC, or a general partnership "
                          "whose direct ownership is entirely natural persons and which is not an "
                          "LLP). No franchise report, no PIR, no OIR."}

    # STEP 2 — nexus? (organized in TX, or doing business in TX; $500,000 economic nexus)
    if not has_nexus:
        return {"outcome": TX_OUTCOME_NOTHING, "franchise_report": None, "render_target": None,
                "info_report": None,
                "reason": "No Texas nexus and not organized in Texas (34 TAC §3.586: economic nexus "
                          "requires $500,000+ of Texas gross receipts for a federal income tax "
                          "accounting period ending in 2019 or later). Nothing is filed."}

    # STEP 3 — new veteran-owned business (initial five-year period)
    if is_new_veteran_owned:
        return {"outcome": TX_OUTCOME_NOTHING, "franchise_report": None, "render_target": None,
                "info_report": None,
                "reason": "Qualifying new veteran-owned business: not required to file for the initial "
                          "five-year period, and 'is not required to file a Public Information Report "
                          "(Form 05-102) or Ownership Information Report (Form 05-167) for that same "
                          "period.' Cannot be in a combined group or tiered partnership during it."}

    # STEP 4 — passive entity (§171.0003) or qualifying REIT (§171.0002(c)(4))
    if is_passive_entity or is_qualifying_reit:
        return {"outcome": TX_OUTCOME_STUB,
                "franchise_report": "TX_05_158", "render_target": "05-158 (stub)",
                "info_report": _tx_info_report(legal_form, is_final_report=is_final_report,
                                               is_passive_entity=is_passive_entity),
                "reason": ("Passive entity" if is_passive_entity else "Qualifying REIT") +
                          ": file the stub report — blacken the Passive and/or REIT circle and "
                          "complete 'the Taxpayer Information part of this form only' (accounting "
                          "period dates + signature). No revenue lines. A PASSIVE entity files NO "
                          "PIR/OIR; a REIT DOES."}

    # STEP 5 — annualized total revenue <= the no tax due threshold
    # ⚠ EXCEPTION: an upper/lower tier entity making the tiered partnership election
    # does NOT stop here — the election switches off BOTH no-tax rules.
    if annualized_total_revenue <= threshold and not tiered_partnership_election:
        return {"outcome": TX_OUTCOME_INFO_ONLY, "franchise_report": None, "render_target": None,
                "info_report": _tx_info_report(legal_form, is_final_report=is_final_report),
                "reason": f"Annualized total revenue {annualized_total_revenue:,.0f} is at or below the "
                          f"{threshold:,} no tax due threshold. 05-915 Item 10: 'stop here, you are not "
                          "required to file a franchise tax report. However, you are required to file a "
                          "Public Information Report (Form 05-102) or Ownership Information Report "
                          "(Form 05-167).' Form 05-163 was DISCONTINUED — 'The No Tax Due Report is not "
                          "available for 2026 reports.' There is NO franchise report object to produce."}

    # STEP 6 — EZ elective path
    if annualized_total_revenue <= ez_ceiling and ez_elected:
        return {"outcome": TX_OUTCOME_EZ,
                "franchise_report": "TX_05_158", "render_target": "05-169",
                "info_report": _tx_info_report(legal_form, is_final_report=is_final_report),
                "reason": f"Annualized total revenue {annualized_total_revenue:,.0f} is at or below "
                          f"{ez_ceiling:,} and the EZ computation was ELECTED. Elective, not mandatory. "
                          "Forfeits ALL credits and ALL margin deductions, and permanently destroys the "
                          "current year's temporary-credit-for-business-loss-carryforwards portion."}

    # STEP 7 — long form
    return {"outcome": TX_OUTCOME_LONG,
            "franchise_report": "TX_05_158", "render_target": "05-158-A/B",
            "info_report": _tx_info_report(legal_form, is_final_report=is_final_report),
            "reason": "Long form: 'Any entity (including a combined group) that does not qualify to "
                      "file using the EZ computation or that does not have $2,650,000 or less in "
                      "annualized total revenue should file this report.'"}


def _tx_total_revenue(items_1_to_7: list, exclusions_item_9: float = 0.0) -> dict:
    """Items 8 and 10. Item 8 = sum(Items 1-7). Item 10 = max(0, Item 8 - Item 9).

    ⚠ Item 3 (Interest): "The amount reported must be zero or greater. We do not allow
    a negative amount on Item 3." Items 4, 6 and 7 MAY be negative (form face).
    ⚠ W6: the Items 1-7 inputs are NAMED FACTS, not federal line numbers. 05-915 cites
    2024 federal forms for a report built on a 2025 federal return.
    """
    vals = [float(v) for v in items_1_to_7]
    item8 = sum(vals)
    item10 = max(0.0, item8 - float(exclusions_item_9))
    return {"item8": item8, "item9": float(exclusions_item_9), "item10": item10}


def _tx_cogs(item11_cogs: float, indirect_overhead_base: float, item13_other: float = 0.0,
             year: int = 2025) -> dict:
    """Items 11-14. Item 12 is CAPPED at 4% of total indirect/administrative overhead.

    ⚠ ITEM 11 IS DIRECT-ENTRY AND MUST NEVER BE DERIVED FROM A FEDERAL FIGURE.
    05-915: "Generally COGS for Texas franchise tax reporting purposes will not equal
    the amount used for federal income tax reporting purposes or for financial
    accounting purposes. Typically, this amount CANNOT BE FOUND ON A FEDERAL INCOME
    TAX REPORT or on an income statement. It is a calculated amount specific to Texas
    franchise tax."
    ⚠ Item 11 also silently absorbs the one-time net depreciation catch-up, which has
    no line of its own and is RED-DEFERRED (R1 / D_TX_DEPR_CATCHUP).
    ⚠ Item 13 "Other" is undocumented-worker comp (negative) / active-duty comp /
    aerospace costs (positive) — "These amounts will offset one another. The result can
    be either a negative ... or a positive number." No floor.
    """
    cap_pct = float(_yk(TX_OVERHEAD_CAP_PCT, year))
    item12 = cap_pct * float(indirect_overhead_base)
    item14 = float(item11_cogs) + item12 + float(item13_other)
    return {"item11": float(item11_cogs), "item12": item12,
            "item13": float(item13_other), "item14": item14}


def _tx_compensation(wages_per_person: list, employee_benefits_item16: float = 0.0,
                     item17_other: float = 0.0, cap_proration_factor: float = 1.0,
                     year: int = 2025) -> dict:
    """Items 15-18. ⚠ THE $480,000 CAP APPLIES TO ITEM 15 ONLY.

    Item 15 verbatim: "amounts paid to officers, directors, owners, partners and
    employees for the accounting period, LIMITED TO $480,000 PER PERSON per 12-month
    period, prorated for the period upon which the tax is based."

    Item 16 verbatim: "The deduction for employee benefits is NOT LIMITED TO $480,000
    PER PERSON but is only deductible to the extent deductible for federal income tax
    purposes." — THE SINGLE MOST-OFTEN-MISCODED FACT IN THE COMPENSATION SCHEDULE.

    ⚠ NEGATIVE NDI IS UNCAPPED: "If net distributive income is a negative number, it
    must be included in the computation of compensation as a negative number. There is
    no cap or limitation on 'negative' compensation." min() handles this naturally.

    ⚠ W7 / U3: `cap_proration_factor` is a DIRECT-ENTRY fact defaulting to 1.0. 05-915
    gives NO proration formula ("prorat" appears exactly once, in the Item 15 sentence)
    and states the cross-member denominator TWO different ways ("upon which the REPORT
    is based" vs "upon which the TAX is based"). Do NOT assume the revenue-annualization
    365-day convention carries over. 34 TAC §3.589 is unread (U5).

    ⚠ The cap is PER PERSON ACROSS A WHOLE COMBINED GROUP, not per member — but
    combined groups are RED-DEFERRED (R2).
    """
    cap = float(_yk(TX_COMP_CAP_PER_PERSON, year)) * float(cap_proration_factor)
    item15 = sum(min(float(w), cap) for w in wages_per_person)
    item16 = float(employee_benefits_item16)   # UNCAPPED — do not apply `cap` here.
    item17 = float(item17_other)
    return {"item15": item15, "item16": item16, "item17": item17,
            "item18": item15 + item16 + item17, "cap_applied": cap}


def _tx_margin(total_revenue_item10: float, total_cogs_item14: float,
               total_compensation_item18: float, year: int = 2025) -> dict:
    """⚠⚠ MARGIN = THE LOWEST OF FOUR (Items 19-23), each FLOORED AT ZERO FIRST.

    Item 23 verbatim: "Enter the lowest amount from Items 19, 20, 21, or 22. If the
    amount is less than zero, enter zero."

      Item 19  70% revenue          max(0, I10 x 0.70)
      Item 20  revenue less COGS    max(0, I10 - I14)
      Item 21  revenue less comp    max(0, I10 - I18)
      Item 22  revenue less $1M     max(0, I10 - 1,000,000)   <-- REAL, ON THE FORM FACE

    ⚠ ENCODE THE FOUR-WAY MINIMUM, NOT THE THREE-WAY MAXIMUM. The industry shorthand
    "revenue minus the greatest of COGS / compensation / 30% of revenue" is
    arithmetically equal for branches 19-21 but SILENTLY DROPS ITEM 22 — which is
    frequently the best answer for a small, labor-light service entity with no COGS.
    (Item 22 beats Item 19 whenever revenue < $3,333,333.)

    ⚠ EVERY BRANCH IS AVAILABLE TO EVERY FILER — no election, no eligibility test on
    19, 21 or 22. Only branch 20 is gated: the entity must actually HAVE qualifying
    COGS. A service entity with no COGS computes Item 20 as I10 - 0 = I10, which then
    loses the minimum. (A combined group "may choose only one method ... that applies
    to all members" — RED-deferred, R2.)
    """
    rev = float(total_revenue_item10)
    item19 = max(0.0, rev * float(_yk(TX_MARGIN_70PCT, year)))
    item20 = max(0.0, rev - float(total_cogs_item14))
    item21 = max(0.0, rev - float(total_compensation_item18))
    item22 = max(0.0, rev - float(_yk(TX_MARGIN_1M_DEDUCTION, year)))
    item23 = max(0.0, min(item19, item20, item21, item22))
    branches = {"19_70pct": item19, "20_cogs": item20, "21_comp": item21, "22_million": item22}
    winner = min(branches, key=lambda k: branches[k])
    return {"item19": item19, "item20": item20, "item21": item21, "item22": item22,
            "item23": item23, "winning_branch": winner}


def _tx_apportionment_factor(texas_receipts_item24: float, everywhere_receipts_item25: float) -> float:
    """Item 26, verbatim: "If Texas gross receipts in Item 24 are zero, enter zero. If
    Item 24 and Item 25 are the same and greater than zero, enter 1.0000. If Item 24 is
    more than Item 25 and both are greater than zero, enter 1.0000. Otherwise, divide
    Item 24 by Item 25 and round to 4 places past the decimal."

    SINGLE GROSS RECEIPTS FACTOR — no property factor, no payroll factor. "Gross
    receipts" is broader than "sales". No throwback and no throwout rule exists
    (checked absence, Rule 3.591).
    """
    tx = float(texas_receipts_item24)
    everywhere = float(everywhere_receipts_item25)
    if tx <= 0:
        return 0.0
    if everywhere <= 0:
        return 0.0
    if tx >= everywhere:
        return 1.0
    return round(tx / everywhere, TX_APPORTIONMENT_DECIMALS)


def _tx_rate(sic_code, retail_wholesale_qualified: bool = False, year: int = 2025) -> str:
    """Item 30. ⚠ THE RATE IS DRIVEN BY THE **SIC** FIELD. NAICS IS PURELY INFORMATIONAL.

    Verbatim, 05-915 SIC field instruction: "This field determines the tax rate.
    Completion of the field is OPTIONAL; however, IF LEFT BLANK, THE TAX RATE DEFAULTS
    TO 0.75%." And: "If the SIC code on Form 05-158-A does not fit the definition of
    qualifying retailers and wholesalers ..., the 0.375% tax rate WILL BE DENIED when
    the report is processed."

    Retail = 1987 SIC Manual Division G (+ apparel rental in 5999/7299, Industry Group
    753, tool/party/furniture rental in 7359, heavy construction equipment in 7353,
    Tex. Bus. & Com. Code ch. 92 rental-purchase); wholesale = Division F. ALL THREE
    conditions must hold: (1) retail/wholesale revenue exceeds other-trade revenue;
    (2) except eating and drinking places (Major Group 58), LESS THAN 50% of that
    revenue is from products the entity or its affiliated group produces; (3) the
    entity provides no retail/wholesale utilities (telecom, electricity, gas).
    `retail_wholesale_qualified` is the affirmed three-condition test — direct-entry.
    """
    if sic_code is None or not str(sic_code).strip():
        return _yk(TX_RATE_STANDARD, year)   # ⚠ BLANK SIC => 0.75%, explicitly.
    if retail_wholesale_qualified:
        return _yk(TX_RATE_RETAIL_WHOLESALE, year)
    return _yk(TX_RATE_STANDARD, year)


def _tx_long_form_tax(margin_item23: float, apportionment_factor_item26: float,
                      allowable_deductions_item28: float = 0.0, rate_item30: str = "0.0075",
                      tax_credits_item32: float = 0.0) -> dict:
    """Items 27-35.

      27 apportioned margin      = I23 x I26
      28 allowable deductions    [ENTRY] — solar (§171.107(b)) / clean-coal (§171.108(b)) /
         relocation (§171.109(b), FIRST ANNUAL REPORT ONLY per Rule 3.584(c)(2)). Each
         "may not reduce apportioned margin below zero, and no carryover of unused
         deductions is allowed."
      29 taxable margin          = I27 - I28   (floored at zero by the no-below-zero rule)
      31 tax due                 = I29 x I30   (dollars and cents)
      32 tax credits             [ENTRY] — 05-181 Item 17; "cannot exceed" 05-181 Item 1
      33 tax due before discount = max(0, I31 - I32)   "If less than zero, enter zero."
      34 DISCOUNT                = ALWAYS 0. "Discounts do not apply to reports due
         after Dec. 31, 2009."
      35 TOTAL TAX DUE           = I33 - I34 == I33. "Must equal the amount of tax due
         in Item 33 since discounts do not apply."

    ⚠ NO MINIMUM TAX: "There is no minimum tax requirement under the franchise tax
    provisions." A zero margin produces a zero tax, not a floor amount.
    ⚠ NO ESTIMATED PAYMENTS: "Texas law does not require the filing of estimated tax
    reports or payments." No quarterly obligation, no estimate-based penalty.
    Units: Items 1-29 whole dollars; Items 31-35 dollars and cents; Item 26 a 4-decimal
    factor.
    """
    item27 = float(margin_item23) * float(apportionment_factor_item26)
    item29 = max(0.0, item27 - float(allowable_deductions_item28))
    item31 = item29 * float(rate_item30)
    item33 = max(0.0, item31 - float(tax_credits_item32))
    item34 = 0.0                      # structurally always zero
    item35 = item33 - item34          # identically item33
    return {"item27": item27, "item28": float(allowable_deductions_item28), "item29": item29,
            "item30": str(rate_item30), "item31": item31, "item32": float(tax_credits_item32),
            "item33": item33, "item34": item34, "item35": item35}


def _tx_ez_tax(total_revenue_item10: float, apportionment_factor: float, year: int = 2025) -> dict:
    """Form 05-169 Items 14-17 — the EZ computation branch.

      EZ-14 apportioned revenue     = EZ-10 x EZ-13   (dollars and cents)
      EZ-15 tax due before discount = EZ-14 x 0.00331 (rate hardcoded on the form face)
      EZ-16 discount                = ALWAYS 0
      EZ-17 TOTAL TAX DUE           = EZ-15

    ⚠ THE EZ TAXES APPORTIONED **REVENUE**, NOT MARGIN. "No margin deduction (COGS,
    compensation, 30% of revenue or $1 million) is allowed," and electing entities "are
    not eligible to take any credits or deductions" — the current year's temporary
    credit for business loss carryforwards "may not be used AND MAY NOT BE CARRIED OVER
    to a future period." A genuine trade-off, not a convenience. See _tx_ez_breakeven.

    ⚠ Correction C7: the 05-169 FORM FACE says only "less than" the no-tax-due
    threshold while 05-158-B, 05-915 and the statute say "less than OR EQUAL TO".
    05-915 and the statute govern — a loader must not read the EZ face literally at
    exactly $2,650,000.
    """
    ez14 = float(total_revenue_item10) * float(apportionment_factor)
    ez15 = ez14 * float(_yk(TX_RATE_EZ, year))
    ez16 = 0.0
    return {"ez14": ez14, "ez15": ez15, "ez16": ez16, "ez17": ez15 - ez16}


def _tx_ez_breakeven(long_form_rate: str, year: int = 2025) -> float:
    """The margin-to-revenue ratio at which the EZ ties the long form: EZ rate / long rate.

    vs 0.75%  -> 0.4413... (44.13%). The EZ is cheaper ONLY above that; it is MORE
                 expensive for every COGS-heavy or labor-heavy entity below it — i.e.
                 for exactly the entities that most often reach for it.
    vs 0.375% -> 0.8827... (88.27%). Since the four-way minimum caps margin at 70% of
                 revenue and 70% < 88.27%, **the EZ is NEVER cheaper for a qualifying
                 retailer or wholesaler.** W8: compute both paths and RECOMMEND.
    """
    return float(_yk(TX_RATE_EZ, year)) / float(long_form_rate)


def _tx_payment_required(total_tax_due: float, annualized_total_revenue: float,
                         tiered_partnership_election: bool = False, year: int = 2025) -> bool:
    """⚠ TWO DIFFERENT BRANCHES, DIFFERENT OUTPUTS. Conflating them is the failure mode.

    THRESHOLD BRANCH (§171.002(d)(2)) — tested on ANNUALIZED total revenue BEFORE the
      report is computed; it TERMINATES the computation. No tax, and the franchise
      report is NOT FILED AT ALL (05-163 does not exist for 2026). PIR/OIR still due.

    <$1,000 BRANCH (§171.002(d)(1)) — tested on COMPUTED tax AFTER the whole report is
      computed. No payment, but THE REPORT IS FILED IN FULL showing the computed
      amount, plus the PIR/OIR. "The entity, however, must submit all required reports
      to satisfy its filing requirements." The test is STRICTLY LESS THAN $1,000 —
      exactly $1,000 is payable.

    Sequencing: annualize Item 10 -> if <= threshold and no tiered election, emit
    output (C) and STOP; else compute the full report -> if Item 35 < $1,000 and no
    tiered election, suppress the PAYMENT but emit the complete report + PIR/OIR.

    ⚠ A TIERED-PARTNERSHIP ELECTION DEFEATS BOTH BRANCHES (printed on the face of both
    05-158-B and 05-169): "Both the upper and lower tier entities owe any amount of tax
    that is calculated as due even if the amount is less than $1,000 or annualized
    total revenue after the tiered partnership election is $2,650,000 or less."
    (Tiered partnerships are RED-DEFERRED, R3 — this flag exists so the interaction is
    stated, not so v1 computes it.)
    """
    if tiered_partnership_election:
        return float(total_tax_due) > 0
    if float(annualized_total_revenue) <= float(_yk(TX_NO_TAX_DUE_THRESHOLD, year)):
        return False
    return float(total_tax_due) >= float(_yk(TX_MIN_PAYMENT_FLOOR, year))


def _tx_report_still_required(total_tax_due: float, outcome: str) -> bool:
    """The report is required whenever the gate produced one, even if no payment is due.

    Outputs (B), (D) and (E) all produce a franchise report regardless of tax. Only
    outputs (A) and (C) produce none — and (C) still produces a PIR or OIR.
    """
    return outcome in (TX_OUTCOME_STUB, TX_OUTCOME_EZ, TX_OUTCOME_LONG)


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY TOPICS / SOURCES
# ═══════════════════════════════════════════════════════════════════════════

AUTHORITY_TOPICS: list[tuple[str, str]] = [
    ("tx_margin_tax",
     "Texas franchise (margin) tax, Tax Code ch. 171 — an entity-level tax on margin, NOT an "
     "income tax: the five-outcome filing gate, the $2,650,000 no-tax-due threshold, the "
     "four-way margin minimum, SIC-driven rate selection, and the PIR/OIR split."),
    ("tx_margin_cogs_comp",
     "Texas margin subtractions — COGS (§171.1012, Rule 3.588) and compensation (§171.1013, "
     "Rule 3.589): the from-scratch Texas COGS figure, the 4% overhead cap, and the $480,000 "
     "per-person cap that applies to Item 15 wages only, never to Item 16 benefits."),
    ("tx_info_reports",
     "Texas Public Information Report (05-102) and Ownership Information Report (05-167) — the "
     "enumerated-list/complement split, the three carve-outs, and forfeiture exposure under "
     "§§171.251, 171.252, 171.255 independent of the tax."),
]

# GATED and unseeded in RS prod — a "NOT FOUND" warning from _load_sources() is the
# CORRECT behaviour here, not a bug. Links naming it are skipped; every rule that
# references it also carries a primary link to a source defined in AUTHORITY_SOURCES.
EXISTING_SOURCES_TO_REFERENCE: list[str] = [
    "TX_STAR_202603002M_IRC_CONFORMITY",
]

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "TX_2026_FORM_05_915",
        "source_type": "state_instruction",
        "source_rank": "primary_official",
        "jurisdiction_code": "TX",
        "title": "2026 Texas Franchise Tax Report Information and Instructions (Rev. 4-26/2)",
        "citation": "Texas Comptroller Form 05-915 (Rev. 4-26/2), 2026 report year (= Delvio TY2025)",
        "issuer": "Texas Comptroller of Public Accounts",
        "official_url": "https://comptroller.texas.gov/forms/05-915.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.6,
        "topics": ["tx_margin_tax", "tx_margin_cogs_comp", "tx_info_reports"],
        "excerpts": [
            {
                "excerpt_label": "Report year / accounting period — THE YEAR MAPPING",
                "excerpt_text": (
                    "Report Year: 'The year in which the franchise tax report is due. The 2026 annual "
                    "report is due May 15, 2026.' Accounting Year Begin Date: 'if the 2025 annual "
                    "franchise tax report had an end date of 12-31-2024, then the begin date on the 2026 "
                    "annual franchise tax report should be 01-01-2025.' Accounting Year End Date: 'Enter "
                    "the last accounting period end date for federal income tax purposes in the year "
                    "before the year the report is originally due.' => the 2026 report covers the "
                    "accounting period ENDING IN CALENDAR 2025, which is Delvio TY2025."
                ),
                "summary_text": "Texas reports are labelled by REPORT YEAR = the year the report is due. Delvio TY2025 = the Texas 2026 annual report, due 05/15/2026. A '2025 Texas report' is TY2024.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "No tax due threshold $2,650,000 — PIR/OIR ONLY, no franchise report",
                "excerpt_text": (
                    "Important Reminders for 2026: 'For the 2026 Franchise Tax Report, the no tax due "
                    "threshold is $2,650,000 and entities whose annualized total revenue from their entire "
                    "business is less than or equal to that amount are not required to file a No Tax Due "
                    "Report. Such entities must still file a Public Information Report (Form 05-102) or "
                    "Ownership Information Report (Form 05-167).' Item 10 instruction: 'If the annualized "
                    "total revenue is less than or equal to $2,650,000, and the entity is not an upper or "
                    "lower tier entity making the tiered partnership election, stop here, you are not "
                    "required to file a franchise tax report. However, you are required to file a Public "
                    "Information Report (Form 05-102) or Ownership Information Report (Form 05-167).' "
                    "'The no tax due threshold has been adjusted, as required by Tax Code Section "
                    "171.006(b) and is now $2,650,000 for reports originally due on or after Jan. 1, 2026, "
                    "and before Jan. 1, 2028.'"
                ),
                "summary_text": "Annualized total revenue <= $2,650,000: no tax, NO franchise report at all (05-163 discontinued), but a PIR or OIR is still required. Biennially indexed; fixed through reports due before 1/1/2028.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Items 19-23 — MARGIN IS THE LOWEST OF FOUR",
                "excerpt_text": (
                    "Item 19 '70% revenue (Item 10 x .70)' — 'Item 10 times 70%. If less than zero, enter "
                    "zero.' Item 20 'Revenue less COGS (Item 10 - item 14)'. Item 21 'Revenue less "
                    "compensation (Item 10 - item 18)'. Item 22 'Revenue less $1 million (Item 10 - "
                    "$1,000,000)'. Item 23 MARGIN — 'Enter the lowest amount from Items 19, 20, 21, or 22. "
                    "If the amount is less than zero, enter zero.' Each branch is floored at zero BEFORE "
                    "the minimum is taken. A combined group 'may choose only one method for computing "
                    "margin that applies to all members.'"
                ),
                "summary_text": "Margin = max(0, min(70% of revenue, revenue-COGS, revenue-compensation, revenue-$1,000,000)). The $1M branch is a real fourth option on the form face; the three-way 'greatest of' shorthand drops it.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "SIC field determines the rate; blank defaults to 0.75%",
                "excerpt_text": (
                    "SIC code field: 'This field determines the tax rate. Completion of the field is "
                    "optional; however, if left blank, the tax rate defaults to 0.75%.' 'If the SIC code "
                    "on Form 05-158-A does not fit the definition of qualifying retailers and wholesalers, "
                    "the 0.375% tax rate will be denied when the report is processed.' NAICS code: 'Enter "
                    "the code that is appropriate for the taxable entity or the code that reflects the "
                    "overall business activity of a combined group' — informational only. Rates: 0.75% "
                    "most entities; 0.375% qualifying wholesalers and retailers; 0.331% EZ computation "
                    "(annualized total revenue $20 million or less). Retail = 1987 SIC Manual Division G "
                    "(plus apparel rental in SIC 5999/7299, Industry Group 753, tool/party/furniture "
                    "rental in SIC 7359, heavy construction equipment in SIC 7353, and Tex. Bus. & Com. "
                    "Code ch. 92 rental-purchase agreements); wholesale = Division F. All three conditions "
                    "must hold: retail/wholesale revenue exceeds other-trade revenue; except for eating "
                    "and drinking places (Major Group 58) less than 50% of that revenue is from products "
                    "the entity or its affiliated group produces; and the entity does not provide retail "
                    "or wholesale utilities."
                ),
                "summary_text": "The SIC field drives the rate (blank => 0.75%); NAICS is informational. 0.75% / 0.375% retail-wholesale / 0.331% EZ.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Item 11 COGS is a from-scratch Texas figure",
                "excerpt_text": (
                    "'A taxable entity has eligible COGS ONLY IF the taxable entity sells real or tangible "
                    "personal property in the ordinary course of business OR if the taxable entity has "
                    "qualifying COGS under any one of the exceptions noted in Texas Tax Code Section "
                    "171.1012 or Rule 3.588. Enter ONLY qualifying COGS to compute margin.' 'Generally, a "
                    "taxable entity in the service industry does not have qualifying COGS.' 'Generally "
                    "COGS for Texas franchise tax reporting purposes will not equal the amount used for "
                    "federal income tax reporting purposes or for financial accounting purposes. "
                    "Typically, this amount cannot be found on a federal income tax report or on an income "
                    "statement. It is a calculated amount specific to Texas franchise tax.' Item 12: 'This "
                    "amount is limited to 4% of total indirect/administrative overhead costs.' Item 13: "
                    "'The only allowable amounts are related to undocumented worker compensation, "
                    "compensation of active duty personnel, and aerospace costs. These amounts will offset "
                    "one another. The result can be either a negative or a positive number.'"
                ),
                "summary_text": "Item 11 COGS cannot be found on a federal return — it is a from-scratch Texas computation. Item 12 capped at 4% of indirect/admin overhead; Item 13 is three offsetting components.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Item 15 $480,000 cap vs Item 16 uncapped benefits",
                "excerpt_text": (
                    "Item 15 Wages and cash compensation: 'amounts paid to officers, directors, owners, "
                    "partners and employees for the accounting period, limited to $480,000 per person per "
                    "12-month period, prorated for the period upon which the tax is based.' Includes "
                    "Medicare wages and tips on Form W-2, net distributive income reported to natural "
                    "persons, and stock awards and stock options deducted for federal income tax purposes. "
                    "'If net distributive income is a negative number, it must be included in the "
                    "computation of compensation as a negative number. There is no cap or limitation on "
                    "negative compensation.' Item 16 Employee benefits: 'Enter the cost of benefits "
                    "provided to officers, directors, owners, partners and employees, including workers' "
                    "compensation, health care and retirement benefits. The deduction for employee "
                    "benefits is NOT limited to $480,000 per person but is only deductible to the extent "
                    "deductible for federal income tax purposes.' Item 15 excludes payments on Forms 1099, "
                    "amounts excluded from gross revenue, and the employer's share of employment taxes. "
                    "'The limit on the compensation deduction has been adjusted to $480,000 per person. "
                    "Effective for reports originally due on or after Jan. 1, 2026, and before Jan. 1, "
                    "2028. Tax Code Section 171.006(b).'"
                ),
                "summary_text": "$480,000 per-person cap applies to Item 15 wages ONLY. Item 16 employee benefits are expressly NOT capped. Negative NDI is uncapped.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Federal-form vintage caveat (W6 / U2) — the line map is a data table",
                "excerpt_text": (
                    "Before you begin: 'The line items indicated in this section refer to specific lines "
                    "from the 2024 Internal Revenue Service (IRS) forms, which are the most current "
                    "available at the time of publication. The statute and administrative rules base total "
                    "revenue on specific line items from the 2006 IRS forms and state that in computing "
                    "total revenue for a subsequent report year, total revenue is based on the 2006 "
                    "equivalent line numbers on any subsequent version of that form.' 'The actual line "
                    "numbers in the statute and rules are not updated to reflect subsequent changes in the "
                    "federal form line numbering. Although these instructions are updated annually to "
                    "reflect federal line numbering changes that affect total revenue, be aware that "
                    "federal line numbers are subject to change throughout the year.'"
                ),
                "summary_text": "05-915 cites 2024 federal form line numbers for a 2026 report built on a 2025 federal return. The federal line map is a per-report-year DATA TABLE and must be re-verified against the FINAL 2025 federal forms before the app build.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "No minimum tax / no discount / no estimated payments / <$1,000",
                "excerpt_text": (
                    "'There is no minimum tax requirement under the franchise tax provisions. "
                    "Additionally, an entity that calculates an amount of tax due that is less than $1,000 "
                    "is not required to pay any tax. The entity, however, must submit all required reports "
                    "to satisfy its filing requirements.' Item 34: 'Discounts do not apply to reports due "
                    "after Dec. 31, 2009.' Item 35: 'Must equal the amount of tax due in Item 33 since "
                    "discounts do not apply.' and 'If this amount is less than $1,000, you owe no tax, but "
                    "you must submit this report along with the Public Information Report (Form 05-102) "
                    "and/or the Ownership Information Report (Form 05-167).' 'Texas law does not require "
                    "the filing of estimated tax reports or payments.' Annualization: 'divide total "
                    "revenue by the number of days in the period, multiply the result by 365' — 'The "
                    "amount of total revenue used in the tax calculations does NOT change as a result of "
                    "annualizing total revenue.'"
                ),
                "summary_text": "No minimum tax, no discount (Item 34 always 0), no estimated payments. Tax < $1,000 (STRICTLY) => no payment, but the full report AND the PIR/OIR are still required.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "PIR vs OIR filing requirements and the three carve-outs",
                "excerpt_text": (
                    "Form 05-102: 'Each corporation, limited liability company (LLC), limited partnership, "
                    "professional association and financial institution that has a franchise tax "
                    "responsibility must file a Public Information Report (PIR) to satisfy their filing "
                    "requirements.' Form 05-167: 'The Ownership Information Report (OIR) is to be filed for "
                    "each taxable entity other than a legally formed corporation, limited liability "
                    "company, limited partnership, professional association or financial institution.' "
                    "'Trusts should report their trustee information and not check any box.' Carve-outs: "
                    "final reports — 'A Public Information Report (Form 05-102) or an Ownership "
                    "Information Report (Form 05-167) is not required to be filed with the final report'; "
                    "'A passive entity is not required to file a Public Information Report (Form 05-102) "
                    "or Ownership Information Report (Form 05-167)'; and a new veteran-owned business 'is "
                    "not required to file a Public Information Report (Form 05-102) or Ownership "
                    "Information Report (Form 05-167) for that same period.' A REIT by contrast: 'Each "
                    "REIT or qualified REIT subsidiary must file either a Public Information Report (Form "
                    "05-102) or an Ownership Information Report (Form 05-167).' Forfeiture: 'Even if the "
                    "franchise tax report is filed and all taxes paid, the right to transact business may "
                    "be forfeited for failure to file the completed and signed PIR.'"
                ),
                "summary_text": "PIR = the enumerated list (corp, LLC, LP, professional association, financial institution); OIR = everything else (GP, LLP, trust, JV). Neither is filed with a FINAL report, by a passive entity, or by a new veteran-owned business. A REIT does file one.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Item 11 — the one-time net depreciation catch-up (RED-DEFER R1)",
                "excerpt_text": (
                    "'For the 2026 franchise tax report, a taxable entity with qualifying assets may "
                    "include a one-time net depreciation adjustment for each qualifying asset in its COGS. "
                    "Qualifying assets are those placed in service prior to the accounting year begin date "
                    "on the 2026 report, provided that the assets have not been disposed of prior to this "
                    "date and are associated with and necessary for the production of goods under Texas "
                    "Tax Code Section 171.1012(c)(6). A depreciation adjustment is not allowed for "
                    "recovery claimed under IRC Section 197. For each tax year the qualifying asset was in "
                    "service (through the accounting year end date on the 2025 report), calculate the "
                    "depreciation adjustment. Add together the depreciation adjustment for each year to "
                    "arrive at the net depreciation adjustment for that qualifying asset and include this "
                    "amount in the entity's COGS on its 2026 franchise tax report. The net depreciation "
                    "adjustment cannot be less than zero. After a taxable entity has included all "
                    "qualifying costs in its cost of goods sold, the taxable entity may include the net "
                    "depreciation adjustment to the extent the adjustment does not take the taxable "
                    "entity's margin below zero. Any unused net depreciation adjustment may be carried "
                    "forward to consecutive reports until exhausted.'"
                ),
                "summary_text": "The catch-up has NO LINE OF ITS OWN (it hides inside Item 11), floors at zero PER ASSET, is bounded by a CIRCULAR margin-not-below-zero test, and its carryforward has NO FORM FIELD ANYWHERE. RED-deferred (R1).",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "TX_2026_FORM_05_158",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "TX",
        "title": "Form 05-158-A / 05-158-B — 2026 Texas Franchise Tax Annual Report (long form)",
        "citation": "Texas Comptroller Form 05-158-A/B (Rev.8-25/11), Tcodes 13250/13251 Annual, report year 2026, due 05/15/2026",
        "issuer": "Texas Comptroller of Public Accounts",
        "official_url": "https://comptroller.texas.gov/forms/05-158-a-26.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.6,
        "topics": ["tx_margin_tax", "tx_margin_cogs_comp"],
        "excerpts": [
            {
                "excerpt_label": "05-158-A/B — verbatim item labels 1-35",
                "excerpt_text": (
                    "REVENUE: 1 Gross receipts or sales; 2 Dividends; 3 Interest; 4 Rents (Can be negative "
                    "amount); 5 Royalties; 6 Gains/losses (Can be negative amount); 7 Other income (Can be "
                    "negative amount); 8 Total gross revenue (Add items 1 thru 7); 9 Exclusions from gross "
                    "revenue (See instructions); 10 TOTAL REVENUE (Item 8 minus item 9; if less than zero, "
                    "enter 0). COST OF GOODS SOLD: 11 Cost of goods sold; 12 Indirect or administrative "
                    "overhead costs (Limited to 4%); 13 Other (See instructions); 14 TOTAL COST OF GOODS "
                    "SOLD (Add items 11 thru 13). COMPENSATION: 15 Wages and cash compensation; 16 "
                    "Employee benefits; 17 Other (See instructions); 18 TOTAL COMPENSATION (Add items 15 "
                    "thru 17). MARGIN: 19 70% revenue (Item 10 x .70); 20 Revenue less COGS (Item 10 - "
                    "item 14); 21 Revenue less compensation (Item 10 - item 18); 22 Revenue less $1 "
                    "million (Item 10 - $1,000,000); 23 MARGIN (Enter the lowest of items 19, 20, 21, or "
                    "22; if less than zero, enter 0). APPORTIONMENT: 24 Gross receipts in Texas; 25 Gross "
                    "receipts everywhere; 26 APPORTIONMENT FACTOR (Divide item 24 by item 25, round to 4 "
                    "decimal places). TAXABLE MARGIN: 27 Apportioned margin (Multiply item 23 by item 26); "
                    "28 Allowable deductions (See instructions); 29 TAXABLE MARGIN (Item 27 minus item "
                    "28). TAX DUE: 30 Tax rate; 31 Tax due (Multiply item 29 by the tax rate in item 30); "
                    "32 Tax credits (Item 17 from Form 05-181); 33 Tax due before discount (Item 31 minus "
                    "item 32); 34 Discount; 35 TOTAL TAX DUE (Item 33 minus item 34)."
                ),
                "summary_text": "All 35 long-form item labels, verbatim from the 2026 form face. Items 1-29 whole dollars; Items 31-35 dollars and cents; Item 26 a 4-decimal factor.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Header fields and the PIR/OIR routing question on the form face",
                "excerpt_text": (
                    "Taxpayer number (11-digit; 'If you do not have an assigned number, enter your federal "
                    "employer identification number (FEIN)'); Report year (preprinted 2026); Due date "
                    "(preprinted 05/15/2026); SOS file number or Comptroller file number; Taxpayer name "
                    "and mailing address; Accounting year begin date / end date ('** If not twelve months, "
                    "see instructions for annualized revenue'); NAICS code; SIC code; circles for combined "
                    "report, Total Revenue adjusted for Tiered Partnership Election, PASSIVE and REIT; and "
                    "the routing question 'Is this entity a corporation, limited liability company, "
                    "professional association, limited partnership or financial institution? Yes / No'. "
                    "Footer: 'Do not include payment if item 35 is less than $1,000 or if annualized total "
                    "revenue is less than or equal to the no tax due threshold... If the entity makes a "
                    "tiered partnership election, ANY amount in item 35 is due.' Signature: 'Report may be "
                    "signed by an officer, director or other authorized person. This includes a paid "
                    "preparer authorized to sign the report.'"
                ),
                "summary_text": "The PIR-vs-OIR split is asked on the 05-158-A form face. Blackening the Passive or REIT circle means completing Taxpayer Information only. The FINAL report OMITS this routing question — corroborating the no-PIR/OIR-with-a-final-report rule.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "TX_2026_FORM_05_169_EZ",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "TX",
        "title": "Form 05-169 — Texas Franchise Tax 2026 E-Z Computation Annual Report",
        "citation": "Texas Comptroller Form 05-169 (Rev.9-23/9), Tcode 13252 Annual, report year 2026, due 05/15/2026",
        "issuer": "Texas Comptroller of Public Accounts",
        "official_url": "https://comptroller.texas.gov/forms/05-169-a-26.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["tx_margin_tax"],
        "excerpts": [
            {
                "excerpt_label": "05-169 EZ items 1-17 and the forfeiture of credits and deductions",
                "excerpt_text": (
                    "Items 1-8 carry labels identical to 05-158-A Items 1-8 and are documented in 05-915 "
                    "as BARE cross-references ('See instructions for Item N on Form 05-158-A'). Item 9 "
                    "Exclusions from gross revenue adds EZ-specific text: 'Do not enter COGS or "
                    "compensation amounts as they cannot be deducted if electing to use the EZ "
                    "computation.' Item 10 TOTAL REVENUE (item 8 minus item 9; if less than zero, enter "
                    "0). Items 11-13 cross-reference 05-158-B Items 24-26 (gross receipts in Texas, gross "
                    "receipts everywhere, apportionment factor rounded to 4 decimal places). Item 14 "
                    "Apportioned revenue (Multiply item 10 by item 13) (Dollars and cents). Item 15 Tax "
                    "due before discount (Multiply item 14 by 0.00331) (Dollars and cents). Item 16 "
                    "Discount. Item 17 TOTAL TAX DUE (item 15 minus item 16). Eligibility: 'Any entity "
                    "(including a combined group) that has annualized total revenue of $20 million or less "
                    "is eligible.' Cost: 'Taxable entities that elect this method to file are not eligible "
                    "to take any credits or deductions. When using the EZ computation, the current year's "
                    "portion of the temporary credit for business loss carryforwards may not be used and "
                    "may not be carried over to a future period.' 'No margin deduction (COGS, "
                    "compensation, 30% of revenue or $1 million) is allowed.'"
                ),
                "summary_text": "The EZ taxes apportioned REVENUE at 0.331% with no margin deduction and no credits. 10 of its 17 items are bare cross-references to 05-158 — it has no independent revenue build, which is why it is a computation branch of TX_05_158 plus a separate render target (W2).",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "TX_2026_FORM_05_102_PIR",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "TX",
        "title": "Form 05-102 — 2026 Texas Franchise Tax Public Information Report",
        "citation": "Texas Comptroller Form 05-102 (Rev.2-24/35), Tcode 13196 Franchise, report year 2026, due 5/15/2026",
        "issuer": "Texas Comptroller of Public Accounts",
        "official_url": "https://comptroller.texas.gov/forms/05-102-a-26.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["tx_info_reports"],
        "excerpts": [
            {
                "excerpt_label": "PIR structure and forfeiture exposure",
                "excerpt_text": (
                    "The PIR is filed by each corporation, LLC, limited partnership, professional "
                    "association and financial institution with a franchise tax responsibility. It carries "
                    "the registered agent and registered office, the principal office and principal place "
                    "of business, Section A (officers, directors and managers, with name, title and term "
                    "dates), Section B (entities in which the reporting entity owns a 10% or greater "
                    "interest) and Section C (entities owning a 10% or greater interest in the reporting "
                    "entity), and a signature. Due on the date the franchise tax report is due. 'Even if "
                    "the franchise tax report is filed and all taxes paid, the right to transact business "
                    "may be forfeited for failure to file the completed and signed PIR', with officers and "
                    "directors personally liable for certain debts (Tex. Tax Code §§171.251, 171.252, "
                    "171.255). Forfeiture does not apply to financial institutions (§§171.259, 171.260). A "
                    "separate PIR is filed by each entity that files a separate franchise report OR that "
                    "is part of a combined group, 'unless the entity is not organized in Texas and does "
                    "not have nexus in Texas.'"
                ),
                "summary_text": "PIR sections A/B/C: officers/directors/managers, 10%-owned entities, 10%-owner entities. Signature is a forfeiture-bearing requirement, not a formality — exposure is independent of the tax.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "TX_2026_FORM_05_167_OIR",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "TX",
        "title": "Form 05-167 — Texas Franchise Tax Ownership Information Report (2026)",
        "citation": "Texas Comptroller Form 05-167 (Rev.2-24/8), Tcode 13197, report year 2026, due 5/15/2026",
        "issuer": "Texas Comptroller of Public Accounts",
        "official_url": "https://comptroller.texas.gov/forms/05-167-a-26.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["tx_info_reports"],
        "excerpts": [
            {
                "excerpt_label": "OIR structure — the complement of the PIR list",
                "excerpt_text": (
                    "'The Ownership Information Report (OIR) is to be filed for each taxable entity other "
                    "than a legally formed corporation, limited liability company, limited partnership, "
                    "professional association or financial institution.' So general partnerships that are "
                    "taxable entities, limited liability partnerships (an LLP is not an 'LP'), business "
                    "and other taxable trusts, joint ventures, business associations and other legal "
                    "entities file the OIR. 'Trusts should report their trustee information and not check "
                    "any box.' Section A records general partners, members, managers, trustees and owners; "
                    "Section B records persons or entities owning a 10% or greater interest. Signature "
                    "required. Authority: Tex. Tax Code §171.201(a)(2),(3), §171.202(a)(4), §171.354. "
                    "Partners, members and owners face personal liability for certain debts on forfeiture."
                ),
                "summary_text": "OIR = everything not on the PIR list: GPs, LLPs, trusts, JVs, business associations, other legal entities. Sections A/B carry general partner / member / manager / trustee and >=10% owner rosters.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "TX_TAX_CODE_CH171",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "TX",
        "title": "Tex. Tax Code ch. 171 — Franchise (margin) Tax",
        "citation": "Tex. Tax Code §§171.0001(9), 171.0002, 171.002, 171.0003, 171.006, 171.1011, 171.1012, 171.1013 (2026 report year)",
        "issuer": "Texas Legislature",
        "official_url": "https://statutes.capitol.texas.gov/Docs/TX/htm/TX.171.htm",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.4,
        "topics": ["tx_margin_tax", "tx_margin_cogs_comp"],
        "excerpts": [
            {
                "excerpt_label": "Taxable entities, the no-tax branches, and the biennial indexing hook",
                "excerpt_text": (
                    "§171.0002 subjects corporations, LLCs (including single-member and series LLCs), "
                    "banks, state limited banking associations, S&Ls, S corporations, professional "
                    "corporations, partnerships (general, limited AND limited liability), certain trusts, "
                    "professional associations, business associations, joint ventures and other legal "
                    "entities. §171.0002(b),(c) exclude sole proprietorships (EXCEPT single-member LLCs), "
                    "general partnerships whose direct ownership is composed entirely of natural persons "
                    "(EXCEPT LLPs), Subchapter B exempt entities, certain unincorporated passive entities, "
                    "certain grantor trusts, estates of natural persons and escrows, REMICs and certain "
                    "qualified REITs, ch. 2212 nonprofit self-insurance trusts, IRC §401(a) trusts, IRC "
                    "§501(c)(9) trusts and unincorporated political committees. §171.002(d)(1): no tax is "
                    "owed if the computed amount is less than $1,000. §171.002(d)(2): an entity 'is not "
                    "required to pay any tax and is not considered to owe any tax for a period if the "
                    "amount of the taxable entity's total revenue from its entire business is less than or "
                    "equal to $2.47 million or the amount determined under Section 171.006.' §171.006(b) "
                    "biennially adjusts that base and the compensation cap. §171.0003 defines the passive "
                    "entity 90%-of-federal-gross-income test. §171.1012 governs COGS; §171.1013 "
                    "compensation; §171.1011 total revenue. §171.0001(9) still defines 'Internal Revenue "
                    "Code' as the IRC of 1986 in effect for the federal tax year beginning January 1, 2007."
                ),
                "summary_text": "Statutory basis for the taxable-entity list, the two no-tax branches (<$1,000 and <= the indexed threshold), the passive-entity test, and the 2007-IRC definition that still binds where ch. 171 cites the Code.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "TX_34TAC_3_586_NEXUS",
        "source_type": "state_regulation",
        "source_rank": "controlling",
        "jurisdiction_code": "TX",
        "title": "34 TAC §3.586 — Margin: Nexus ($500,000 economic nexus)",
        "citation": "34 Tex. Admin. Code §3.586 (amended eff. Dec. 29, 2019 and Feb. 10, 2021)",
        "issuer": "Texas Comptroller of Public Accounts",
        "official_url": "https://comptroller.texas.gov/taxes/franchise/",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.3,
        "topics": ["tx_margin_tax"],
        "excerpts": [
            {
                "excerpt_label": "Economic nexus — keyed to the accounting period, not the due date",
                "excerpt_text": (
                    "A foreign taxable entity has nexus 'for each federal income tax accounting period "
                    "ending in 2019 or later ... if during that federal income tax accounting period, it "
                    "had gross receipts from business done in Texas of $500,000 or more, as sourced under "
                    "§3.591(e) and (f).' Gross receipts here means 'all revenue reportable by a taxable "
                    "entity on its federal return, without deduction for the cost of property sold, "
                    "materials used, labor performed, or other costs incurred.' On or after Jan. 1, 2019 a "
                    "foreign entity begins doing business in Texas on the earliest of (A) physical "
                    "presence, (B) obtaining a Texas use tax permit, or (C) the FIRST DAY of the federal "
                    "accounting period ending in 2019 or later in which it reached $500,000."
                ),
                "summary_text": "$500,000 economic nexus, tested on the entity's federal accounting period (ending 2019+), NOT the report due date. Nexus begins on the FIRST DAY of that period, not the crossing date.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "TX_34TAC_3_588_COGS",
        "source_type": "state_regulation",
        "source_rank": "controlling",
        "jurisdiction_code": "TX",
        "title": "34 TAC §3.588 — Margin: Cost of Goods Sold (adopted 6/1/2026, eff. 6/21/2026)",
        "citation": "34 Tex. Admin. Code §3.588, adopted June 1, 2026, effective June 21, 2026 (proposal 51 TexReg 2237, Apr. 3, 2026)",
        "issuer": "Texas Comptroller of Public Accounts",
        "official_url": "https://www.sos.state.tx.us/texreg/archive/June122026/Adopted%20Rules/34.PUBLIC%20FINANCE.html",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.3,
        "topics": ["tx_margin_cogs_comp"],
        "excerpts": [
            {
                "excerpt_label": "§179 reference deleted; per-asset catch-up in the RULE; no asset-level date gate",
                "excerpt_text": (
                    "The adopted amendment DELETES the rule's reference to 'Internal Revenue Code, §179 "
                    "(Election to expense certain depreciable assets)' — the sole source of the old "
                    "$25,000 / $200,000 Texas cap — on the stated ground that 'Chapter 171 does not "
                    "specifically reference §179'. The rule carries the catch-up at subparagraph (B): 'a "
                    "one-time net depreciation adjustment FOR EACH QUALIFYING ASSET' on the 2026 report "
                    "for assets 'placed in service prior to the accounting year begin date on the 2026 "
                    "report'. On bonus: 'beginning with the 2026 franchise tax report, a taxable entity "
                    "may include in its cost of goods sold the bonus depreciation claimed on its federal "
                    "return, to the extent associated with and necessary for the production of the goods' "
                    "— a REPORT-YEAR qualifier with NO ASSET-LEVEL placed-in-service or acquisition date "
                    "gate. §197 recovery remains determined under the 2007 IRC."
                ),
                "summary_text": "Adopted Rule 3.588 deletes the IRC §179 reference (no Texas §179 dollar cap for 2026), puts the PER-ASSET catch-up framing in the rule itself, and states the bonus COGS rule with a report-year qualifier but NO asset-level date gate — the W1 conflict.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "WARNING — the txrules.elaws.us mirror is STALE for §3.588 (correction C4)",
                "excerpt_text": (
                    "As of 2026-08-16 the txrules.elaws.us mirror still serves the PRE-AMENDMENT (eff. "
                    "Jan. 1, 2008) text of §3.588, which RETAINS the very IRC §179 reference the June 2026 "
                    "amendment deletes. Do not use that URL to verify the amended rule: a re-verification "
                    "pass reading it would 'confirm' the wrong text and reinstate the dead $25,000 / "
                    "$200,000 cap. The texreg.sos.state.tx.us/public/readtac$ext.TacPage URL is DEAD "
                    "(returns only a site-redirect notice). The §179-deletion and no-asset-date-gate "
                    "conclusions rest on the Texas Register adoption document, re-fetched and re-confirmed "
                    "2026-08-16."
                ),
                "summary_text": "Source-channel warning: the obvious 34 TAC mirror serves stale pre-2026 §3.588 text. Verify amended sections against the Texas Register adoption document, not the mirror.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "TX_2026_FORMS_INDEX",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "TX",
        "title": "Texas Franchise Tax Report Forms for 2026 (official forms index)",
        "citation": "Texas Comptroller, 2026 franchise tax forms index",
        "issuer": "Texas Comptroller of Public Accounts",
        "official_url": "https://comptroller.texas.gov/taxes/franchise/forms/2026-franchise.php",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.2,
        "topics": ["tx_margin_tax", "tx_info_reports"],
        "excerpts": [
            {
                "excerpt_label": "05-163 No Tax Due Report does not exist for 2026",
                "excerpt_text": (
                    "The 2026 forms page states outright: 'The No Tax Due Report is not available for 2026 "
                    "reports.' Form 05-163 is absent from the 2026 forms index AND from the 05-915 Index "
                    "of Forms; Form 05-160 is likewise absent (replaced by 05-181 Credits Summary "
                    "Schedule). The 2026 family is: 05-158-A/B long form, 05-169 EZ, 05-102 PIR, 05-167 "
                    "OIR, 05-164 extension, 05-165 extension affiliate list, 05-166 affiliate schedule, "
                    "05-170 payment, 05-175 tiered partnership, 05-177 common owner, 05-180 historic "
                    "structure credit, 05-181 credits summary, 05-182 Subchapter T R&D credits, 05-185 "
                    "housing development credit."
                ),
                "summary_text": "There is NO 'no tax due report' object to produce for 2026. A below-threshold entity's only Texas output is a PIR or an OIR.",
                "is_key_excerpt": True,
            },
        ],
    },
]

AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    ("TX_2026_FORM_05_915", "TX_05_158", "governs"),
    ("TX_2026_FORM_05_158", "TX_05_158", "governs"),
    ("TX_2026_FORM_05_169_EZ", "TX_05_158", "governs"),
    ("TX_TAX_CODE_CH171", "TX_05_158", "governs"),
    ("TX_34TAC_3_586_NEXUS", "TX_05_158", "governs"),
    ("TX_34TAC_3_588_COGS", "TX_05_158", "governs"),
    ("TX_2026_FORMS_INDEX", "TX_05_158", "informs"),
    ("TX_2026_FORM_05_915", "TX_05_102", "governs"),
    ("TX_2026_FORM_05_102_PIR", "TX_05_102", "governs"),
    ("TX_TAX_CODE_CH171", "TX_05_102", "governs"),
    ("TX_2026_FORM_05_915", "TX_05_167", "governs"),
    ("TX_2026_FORM_05_167_OIR", "TX_05_167", "governs"),
    ("TX_TAX_CODE_CH171", "TX_05_167", "governs"),
    ("TX_STAR_202603002M_IRC_CONFORMITY", "TX_05_158", "informs"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM 1 of 3 — TX_05_158 (long form 05-158-A/B) with the EZ (05-169) as an
# INTERNAL COMPUTATION BRANCH plus a separate render target. See W2.
# ═══════════════════════════════════════════════════════════════════════════

TX158_FACTS: list[dict] = [
    # ── THE FILING GATE (evaluated FIRST; decides whether anything is emitted) ──
    {"fact_key": "legal_form", "label": "Texas legal form of the entity", "data_type": "choice", "required": True, "sort_order": 1,
     "choices": ["corporation", "c_corporation", "s_corporation", "professional_corporation", "llc",
                 "single_member_llc", "series_llc", "limited_partnership", "professional_association",
                 "financial_institution", "bank", "state_limited_banking_association", "savings_and_loan",
                 "general_partnership", "llp", "trust", "business_trust", "joint_venture",
                 "business_association", "other_legal_entity"],
     "notes": "Drives BOTH taxability (§171.0002) and the PIR-vs-OIR split. ⚠ An LLP is NOT an 'LP' — LLPs file the OIR. This is a TEXAS legal form, NOT the federal filing classification."},
    {"fact_key": "is_taxable_entity", "label": "Is a taxable entity under §171.0002?", "data_type": "boolean", "required": True, "sort_order": 2,
     "notes": "NOT taxable: sole proprietorships (EXCEPT single-member LLCs), general partnerships whose direct ownership is entirely natural persons (EXCEPT LLPs), Subchapter B exempt entities, certain grantor trusts / estates of natural persons / escrows, REMICs and certain qualified REITs, ch. 2212 trusts, IRC §401(a) and §501(c)(9) trusts, unincorporated political committees."},
    {"fact_key": "federally_disregarded_entity", "label": "Disregarded for federal income tax purposes?", "data_type": "boolean", "required": False, "sort_order": 3,
     "notes": "⚠ #1 PRACTICAL TRAP — IRRELEVANT to Texas. 'An entity's treatment for federal income tax purposes does not determine its responsibility for Texas franchise tax.' A federally disregarded SMLLC files its OWN Texas report and its own PIR/OIR."},
    {"fact_key": "organized_in_texas", "label": "Organized/formed in Texas?", "data_type": "boolean", "required": False, "sort_order": 4},
    {"fact_key": "physical_presence_in_texas", "label": "Physical presence in Texas?", "data_type": "boolean", "required": False, "sort_order": 5},
    {"fact_key": "has_texas_use_tax_permit", "label": "Holds a Texas use tax permit?", "data_type": "boolean", "required": False, "sort_order": 6,
     "notes": "One of the three doing-business triggers for a foreign entity on/after 1/1/2019 (34 TAC §3.586)."},
    {"fact_key": "texas_receipts_this_accounting_period", "label": "Texas gross receipts for THIS federal accounting period (economic-nexus test)", "data_type": "decimal", "required": False, "sort_order": 7,
     "notes": "⚠ 34 TAC §3.586: $500,000+ creates nexus 'for each federal income tax accounting period ending in 2019 or later'. Keyed to the ENTITY'S ACCOUNTING PERIOD, not the report due date. Nexus BEGIN DATE = the FIRST DAY of that period, not the crossing date."},
    {"fact_key": "is_new_veteran_owned", "label": "Qualifying new veteran-owned business (initial 5-year period)?", "data_type": "boolean", "required": False, "sort_order": 8,
     "notes": "Formed in TX on/after 1/1/2016 and before 1/1/2020, OR on/after 1/1/2022; 100% owned by honorably discharged veterans; Texas Veterans Commission letter on file. Files NOTHING — no report, no PIR, no OIR. Cannot be in a combined group or tiered partnership during the period."},
    {"fact_key": "is_passive_entity", "label": "Passive entity under §171.0003 (>=90% passive federal gross income)?", "data_type": "boolean", "required": False, "sort_order": 9,
     "notes": "⚠ 'Passive income does not include rent.' Only general/limited/LL partnerships and trusts other than business trusts can qualify — corporations and LLCs NEVER can. A passive entity files the stub report and NO PIR/OIR."},
    {"fact_key": "is_qualifying_reit", "label": "Qualifying REIT or qualified REIT subsidiary (§171.0002(c)(4))?", "data_type": "boolean", "required": False, "sort_order": 10,
     "notes": "Files the stub report AND — unlike a passive entity — 'must file either a Public Information Report (Form 05-102) or an Ownership Information Report (Form 05-167).'"},
    {"fact_key": "is_final_report", "label": "Final report (entity ceased doing business in Texas)?", "data_type": "boolean", "required": False, "sort_order": 11,
     "notes": "RED-DEFER R5. Due 60 days after cessation; NO PIR/OIR is filed with it; different Tcodes (13270/13271); no preprinted due date; adds the Certificate of Account Status circle. Items 1-35 are identical to the annual."},
    {"fact_key": "tiered_partnership_election", "label": "Tiered partnership election made (Form 05-175)?", "data_type": "boolean", "required": False, "sort_order": 12,
     "notes": "RED-DEFER R3. ⚠ The election DEFEATS BOTH no-tax branches — any computed amount is due for both tiers even below $1,000 or below the threshold. Election bar: not allowed if the lower tier, before passing revenue, has $2,650,000 or less annualized revenue OR owes less than $1,000."},
    {"fact_key": "is_combined_group_member", "label": "Member of a unitary affiliated (combined) group?", "data_type": "boolean", "required": False, "sort_order": 13,
     "notes": "RED-DEFER R2. Combined reporting is MANDATORY where it applies — a silent separate-entity report for a unitary group is a WRONG RETURN, not an incomplete one."},
    {"fact_key": "ez_elected", "label": "EZ computation (Form 05-169) elected?", "data_type": "boolean", "required": False, "sort_order": 14,
     "notes": "W2/W8. Elective, not mandatory, and often the WRONG answer: it taxes apportioned REVENUE, forfeits ALL credits and margin deductions, and permanently destroys the current year's temporary-credit-for-BLC portion. Selects the tax path AND the 05-169 render target."},
    {"fact_key": "accounting_year_begin_date", "label": "Accounting year begin date", "data_type": "date", "required": True, "sort_order": 15,
     "notes": "For a calendar-year filer on the 2026 report this is 01-01-2025 (the period ENDING in calendar 2025). See the year-mapping block."},
    {"fact_key": "accounting_year_end_date", "label": "Accounting year end date", "data_type": "date", "required": True, "sort_order": 16,
     "notes": "'the last accounting period end date for federal income tax purposes in the year before the year the report is originally due' — i.e. ending in calendar 2025 for the 2026 report."},
    {"fact_key": "days_in_accounting_period", "label": "Days in the accounting period (for annualization)", "data_type": "integer", "required": False, "sort_order": 17,
     "notes": "Annualization applies only when the period is not 12 months, and ONLY to the threshold and EZ-eligibility tests."},
    {"fact_key": "is_first_annual_report", "label": "First annual report?", "data_type": "boolean", "required": False, "sort_order": 18,
     "notes": "Side branch: if the entity became subject during 2025 with a federal year end BEFORE that date, begin date = end date = the date it became subject, producing a ZERO report — but the PIR/OIR is still required. Also gates the §171.109(b) relocation deduction (first annual report only, Rule 3.584(c)(2))."},

    # ── HEADER / RATE SELECTION ──
    {"fact_key": "taxpayer_number", "label": "Texas taxpayer number (11-digit)", "data_type": "string", "required": False, "sort_order": 20,
     "notes": "'If you do not have an assigned number, enter your federal employer identification number (FEIN).'"},
    {"fact_key": "sos_or_comptroller_file_number", "label": "SOS file number or Comptroller file number", "data_type": "string", "required": False, "sort_order": 21},
    {"fact_key": "naics_code", "label": "NAICS code (INFORMATIONAL ONLY — does not drive the rate)", "data_type": "string", "required": False, "sort_order": 22,
     "notes": "⚠ NAICS does NOT determine the rate. The form carries both fields and only the SIC field is rate-bearing."},
    {"fact_key": "sic_code", "label": "SIC code (1987 SIC Manual) — ⚠ THIS FIELD DETERMINES THE TAX RATE", "data_type": "string", "required": False, "sort_order": 23,
     "notes": "⚠ Verbatim: 'This field determines the tax rate. Completion of the field is optional; however, IF LEFT BLANK, THE TAX RATE DEFAULTS TO 0.75%.' Encode the blank default explicitly — do not treat blank as unknown."},
    {"fact_key": "retail_wholesale_qualified", "label": "All three retail/wholesale rate conditions affirmed?", "data_type": "boolean", "required": False, "sort_order": 24,
     "notes": "Direct-entry affirmation: (1) retail/wholesale revenue exceeds other-trade revenue; (2) except eating and drinking places (SIC Major Group 58), LESS THAN 50% of that revenue is from products the entity or its affiliated group produces; (3) no retail/wholesale utilities (telecom, electricity, gas). A SIC code that does not fit the definition means 'the 0.375% tax rate will be denied when the report is processed.'"},

    # ── REVENUE Items 1-7 (FEDERAL HANDOFF AS NAMED FACTS — W6, NOT line numbers) ──
    {"fact_key": "fed_gross_receipts_or_sales", "label": "Item 1 Gross receipts or sales (from the federal return)", "data_type": "decimal", "required": False, "sort_order": 30,
     "notes": "⚠ W6/U2: the federal SOURCE LINE is deliberately NOT hard-coded. 05-915 (Rev. 4-26/2) cites 2024 IRS form lines for a report built on a 2025 federal return. Re-verify the mapping against the FINAL 2025 federal forms before the app build."},
    {"fact_key": "fed_dividends", "label": "Item 2 Dividends (from the federal return)", "data_type": "decimal", "required": False, "sort_order": 31,
     "notes": "W6 — named fact, not a hard-coded federal line."},
    {"fact_key": "fed_interest", "label": "Item 3 Interest (from the federal return) — MUST BE >= 0", "data_type": "decimal", "required": False, "sort_order": 32,
     "validation_rule": "must be >= 0",
     "notes": "⚠ Verbatim: 'The amount reported must be zero or greater. We do not allow a negative amount on Item 3.' W6 applies to the source line."},
    {"fact_key": "fed_rents", "label": "Item 4 Rents (CAN BE NEGATIVE)", "data_type": "decimal", "required": False, "sort_order": 33,
     "notes": "⚠ Cross-item interlock, verbatim: 'Do not include in Item 4 net rental income (loss) passed through from a partnership or S corporation on IRS Form K-1; report this amount in Item 7. This amount must also be included in Item 9 when subtracting net distributive income...' W6 applies to the source line."},
    {"fact_key": "fed_royalties", "label": "Item 5 Royalties (from the federal return)", "data_type": "decimal", "required": False, "sort_order": 34, "notes": "W6."},
    {"fact_key": "fed_gains_losses", "label": "Item 6 Gains/losses (CAN BE NEGATIVE)", "data_type": "decimal", "required": False, "sort_order": 35,
     "notes": "NEW for 2026 (S.J.R. 18, 89th Leg.): 'Trusts no longer include realized or unrealized capital gains or the sale or transfer of a capital asset in total revenue' — this OVERRIDES the Item 6 pull for a trust filer. W6 applies to the source line."},
    {"fact_key": "fed_other_income", "label": "Item 7 Other income (CAN BE NEGATIVE)", "data_type": "decimal", "required": False, "sort_order": 36,
     "notes": "Carries the K-1 net rental income (loss) redirected out of Item 4, plus tiered-partnership revenue passed UP to an upper tier. W6."},

    # ── Item 9 EXCLUSIONS (closed list; per-category direct entry) ──
    {"fact_key": "excl_bad_debt", "label": "Item 9 exclusion — bad debt expense", "data_type": "decimal", "required": False, "sort_order": 40,
     "notes": "One of only TWO exclusion categories with a federal line map. W6 applies to that mapping."},
    {"fact_key": "excl_sch_c_dividends_received_deduction", "label": "Item 9 exclusion — Schedule C dividends received deduction (1120 filers)", "data_type": "decimal", "required": False, "sort_order": 41,
     "notes": "'to the extent the relating dividend income is included in gross revenue.' The second and last mapped category. W6."},
    {"fact_key": "excl_foreign_dividends_royalties", "label": "Item 9 exclusion — foreign dividends and foreign royalties", "data_type": "decimal", "required": False, "sort_order": 42,
     "notes": "⚠⚠ HARD BLOCK: IRC §78 and §§951-964 amounts are STILL PINNED TO THE 2007 IRC, so GILTI/FDII (OBBBA-renamed NCTI/FDDEI) is INCLUDIBLE in total revenue and is NOT subtractable here — not as a foreign dividend/royalty, not as a §78/§951-964 amount, and not as a Schedule C deduction. The live TY2025 trap for C-corp clients with foreign income. Diagnostic D_TX_GILTI_NOT_EXCLUDABLE."},
    {"fact_key": "excl_net_distributive_income", "label": "Item 9 exclusion — net distributive income from another taxable entity", "data_type": "decimal", "required": False, "sort_order": 43,
     "notes": "'(If this amount is negative, it is included in computing total revenue.)' An entity owning an interest in a PASSIVE entity may not deduct its share unless the income was included in another taxable entity's total revenue. For an upper tier using the tiered partnership election, revenue passed UP cannot be deducted here."},
    {"fact_key": "excl_flow_through_funds", "label": "Item 9 exclusion — flow-through funds mandated by law, fiduciary duty or contract", "data_type": "decimal", "required": False, "sort_order": 44,
     "notes": "Closed sub-list: sales commissions to non-employees; the tax basis of securities underwritten; flow-through payments to subcontractors for design/construction/remodeling/remediation/repair of improvements on real property or location of boundaries."},
    {"fact_key": "excl_other_statutory_categories", "label": "Item 9 exclusion — all other statutory categories (industry 'Other Exclusions')", "data_type": "decimal", "required": False, "sort_order": 45,
     "notes": "⚠ CLOSED LIST: 'Only the following items may be excluded from gross revenue. See Rule 3.587.' ~30 categories incl. legal-services items, tax basis of securities/loans sold, pharmacy cooperative rebates, federal-obligation dividends and interest, PEO client payments, healthcare Medicaid/Medicare/CHIP/TRICARE (healthcare INSTITUTIONS only 50%), management company reimbursements, and — NEW for 2026 — broadband deployment grants incl. reimbursement awards (S.B. 1405), registered securities market operator rebates (S.B. 1058), and Central Texas Water Alliance obligations (S.B. 1194). ⚠ CARES/broadband ASYMMETRY: proceeds are excluded from revenue but the costs and compensation paid WITH them remain includable in COGS and compensation — a deliberate double benefit; do not 'correct' it."},
    {"fact_key": "excl_intercompany_or_tiered_pass", "label": "Item 9 exclusion — intercompany eliminations / lower-tier revenue passed up", "data_type": "decimal", "required": False, "sort_order": 46,
     "notes": "RED-DEFER R2/R3 entry point. Combined groups 'subtract items of revenue received from members of the combined group'; a lower tier entity enters the revenue passed to upper tiers HERE (Item 9), and the upper tier reports it on Item 7."},

    # ── COGS Items 11-13 (DIRECT-ENTRY) ──
    {"fact_key": "cogs_eligibility_affirmed", "label": "Sells real or tangible personal property in the ordinary course (or a §171.1012 / Rule 3.588 exception)?", "data_type": "boolean", "required": False, "sort_order": 50,
     "notes": "⚠ Eligibility GATE, verbatim: 'A taxable entity has eligible COGS ONLY IF...' and 'Generally, a taxable entity in the service industry does not have qualifying COGS.' Ownership required: 'A taxable entity may make a subtraction in relation to the COGS only if that entity OWNS the goods.' Mixed transactions: only the tangible-property costs — 'The labor costs related to the services performed are not eligible COGS.'"},
    {"fact_key": "cogs_item11_qualifying", "label": "Item 11 Cost of goods sold — ⚠ DIRECT-ENTRY, a from-scratch TEXAS figure", "data_type": "decimal", "required": False, "sort_order": 51,
     "notes": "⚠⚠ NEVER DERIVE THIS FROM A FEDERAL COGS FIGURE. 05-915: 'Typically, this amount CANNOT BE FOUND ON A FEDERAL INCOME TAX REPORT or on an income statement. It is a calculated amount specific to Texas franchise tax.' It also silently absorbs the one-time net depreciation catch-up, which has no line of its own (RED-DEFER R1). Includes federal depreciation, §179 expensing, depletion and §197 amortization as claimed, to the extent associated with and necessary for the production of goods."},
    {"fact_key": "cogs_expense_or_capitalize_election", "label": "COGS election (entities subject to IRC §263A, §460 or §471 only)", "data_type": "choice", "required": False, "sort_order": 52,
     "choices": ["expense", "capitalize", "not_applicable"],
     "notes": "'All other taxable entities will expense.' Expensing => no beginning or ending inventory. Capitalizing => beginning inventory allowable costs + costs capitalized during the period − ending inventory allowable costs. 'The election is made by filing the franchise tax report using one method or the other and may not be changed after the due date or the date the report is filed, whichever is later.'"},
    {"fact_key": "indirect_admin_overhead_base", "label": "Item 12 BASE — total indirect/administrative overhead allocable to acquisition or production of goods", "data_type": "decimal", "required": False, "sort_order": 53,
     "notes": "The 4% cap is COMPUTED from this base. Includes all mixed service costs — security, legal, data processing, accounting, personnel operations, general financial planning and management. Anything specifically EXCLUDED from COGS may not be routed through Item 12."},
    {"fact_key": "cogs_item13_other", "label": "Item 13 Other — undocumented worker (negative) / active duty / aerospace", "data_type": "decimal", "required": False, "sort_order": 54,
     "notes": "'The only allowable amounts are related to undocumented worker compensation, compensation of active duty personnel, and aerospace costs. These amounts will offset one another. The result can be either a negative or a positive number.' No floor."},
    {"fact_key": "depr_catchup_manual_item11", "label": "One-time 2026 net depreciation adjustment — ⚠ PREPARED MANUALLY, entered in Item 11", "data_type": "decimal", "required": False, "sort_order": 55,
     "notes": "⚠⚠ RED-DEFER R1 — DELVIO DOES NOT COMPUTE THIS. Per-asset zero floor, a CIRCULAR margin-not-below-zero limiter, a cross-year carryforward with NO FORM FIELD ANYWHERE, and a per-asset per-year federal-vs-Texas depreciation history Delvio does not hold. Enter the manually prepared figure; it is absorbed into Item 11 and is invisible on the filed form."},

    # ── COMPENSATION Items 15-17 ──
    {"fact_key": "comp_wages_person_roster", "label": "Item 15 per-person wage/cash-compensation roster (cap applied PER PERSON)", "data_type": "string", "required": False, "sort_order": 60,
     "notes": "Collection fact: one amount per officer, director, owner, partner and employee. The $480,000 cap is applied to EACH PERSON before summing — an entity-level sum capped once is WRONG. Includes Medicare wages and tips on Form W-2, net distributive income reported to NATURAL PERSONS, and stock awards/options deducted federally."},
    {"fact_key": "comp_wages_uncapped_total", "label": "Item 15 uncapped total (before the per-person $480,000 cap)", "data_type": "decimal", "required": False, "sort_order": 61,
     "notes": "Diagnostic surface only — shows the preparer how much the cap removed."},
    {"fact_key": "comp_persons_over_cap", "label": "Number of persons whose wages exceed the per-person cap", "data_type": "integer", "required": False, "sort_order": 62},
    {"fact_key": "comp_cap_proration_factor", "label": "Per-person cap proration factor for a short period (⚠ W7 — DIRECT-ENTRY, default 1.0)", "data_type": "decimal", "required": False, "sort_order": 63,
     "default_value": "1.0",
     "notes": "⚠ W7/U3: 05-915 says the cap is 'prorated for the period upon which the tax is based' but gives NO FORMULA ('prorat' appears exactly once in the booklet, in that sentence), and states the cross-member denominator two different ways ('upon which the REPORT is based' vs 'upon which the TAX is based'). 34 TAC §3.589 is UNREAD (U5). ⚠ Do NOT assume the revenue-annualization 365-day convention carries over. Direct-enter the factor until §3.589 is pulled."},
    {"fact_key": "comp_negative_ndi", "label": "Negative net distributive income included in Item 15 (UNCAPPED)", "data_type": "decimal", "required": False, "sort_order": 64,
     "notes": "⚠ Verbatim: 'If net distributive income is a negative number, it must be included in the computation of compensation as a negative number. There is no cap or limitation on negative compensation.' NDI formulas: from a 1065 K-1, add boxes 1,2,3,4,5,6a,7,8,9a,10,11 and subtract box 12, the box 13 amounts that represent deductions, and box 21 (foreign taxes). From an 1120S K-1, add boxes 1,2,3,4,5a,6,7,8a,9,10 and subtract box 11, the box 12 amounts that represent deductions, and Code F box 16 (foreign taxes)."},
    {"fact_key": "comp_benefits_item16", "label": "Item 16 Employee benefits — ⚠ NOT SUBJECT TO THE $480,000 CAP", "data_type": "decimal", "required": False, "sort_order": 65,
     "notes": "⚠⚠ THE SINGLE MOST-OFTEN-MISCODED FACT IN THE COMPENSATION SCHEDULE. Verbatim: 'The deduction for employee benefits is NOT limited to $480,000 per person but is only deductible to the extent deductible for federal income tax purposes.' Workers' compensation, health care and retirement benefits."},
    {"fact_key": "comp_item17_other", "label": "Item 17 Other — undocumented worker / active duty / aerospace (against compensation)", "data_type": "decimal", "required": False, "sort_order": 66,
     "notes": "Identical three components to Item 13, applied against compensation rather than COGS."},

    # ── APPORTIONMENT Items 24-25 (DIRECT-ENTRY; the factor is computed) ──
    {"fact_key": "texas_gross_receipts_item24", "label": "Item 24 Gross receipts in Texas", "data_type": "decimal", "required": False, "sort_order": 70,
     "notes": "Rule 3.591 sourcing (U7 — operative text read only in 05-915 summary form): TPP where delivered/shipped to a Texas purchaser; real property in Texas incl. mineral royalties; SERVICES WHERE PERFORMED; rentals of Texas-situated property; patents/copyrights used in Texas; computer software, intangibles and securities to the LEGAL DOMICILE OF THE PAYOR; securities sold through an exchange with an unidentifiable buyer => 8.7% of the revenue is a Texas receipt; internet hosting to the CUSTOMER'S location. Excludes amounts excluded from total revenue, including IRC §78 / §§951-964 income."},
    {"fact_key": "everywhere_gross_receipts_item25", "label": "Item 25 Gross receipts everywhere", "data_type": "decimal", "required": False, "sort_order": 71,
     "notes": "'all revenues reportable by a taxable entity on its federal tax return, without deduction for the COGS or other costs incurred unless otherwise provided for by law.' Net GAINS from capital-asset/investment sales are included; net LOSSES are not. No throwback and no throwout rule exists (checked absence, Rule 3.591)."},

    # ── TAX Items 28 / 32 (DIRECT-ENTRY) ──
    {"fact_key": "allowable_deductions_item28", "label": "Item 28 Allowable deductions (solar / clean coal / relocation)", "data_type": "decimal", "required": False, "sort_order": 80,
     "notes": "EXACTLY THREE: 10% of the amortized cost of a §171.107(b) solar energy device; 10% of the amortized cost of §171.108(b) clean-coal equipment; §171.109(b) relocation costs (FIRST ANNUAL REPORT ONLY, Rule 3.584(c)(2)). Each: 'may not reduce apportioned margin below zero, and no carryover of unused deductions is allowed.' ⚠ NOT available on the EZ path."},
    {"fact_key": "tax_credits_item32", "label": "Item 32 Tax credits (Form 05-181 Item 17)", "data_type": "decimal", "required": False, "sort_order": 81,
     "notes": "RED-DEFER R4. 05-181 Item 17 'cannot exceed the amount in Item 1' (tax due before credits). ⚠ NOT available on the EZ path — electing the EZ forfeits ALL credits and permanently destroys the current year's temporary-credit-for-BLC portion."},
]

TX158_RULES: list[dict] = [
    {"rule_id": "R-TX-NEXUS", "title": "Texas nexus — organized in TX, doing business in TX, or $500,000 economic nexus", "rule_type": "classification",
     "formula": ("has_nexus = organized_in_texas OR physical_presence_in_texas OR has_texas_use_tax_permit "
                 "OR texas_receipts_this_accounting_period >= 500000"),
     "inputs": ["organized_in_texas", "physical_presence_in_texas", "has_texas_use_tax_permit",
                "texas_receipts_this_accounting_period"],
     "outputs": ["has_nexus"], "sort_order": 1,
     "description": "34 TAC §3.586, verbatim: nexus exists 'for each federal income tax accounting period ending in 2019 or later ... if during that federal income tax accounting period, it had gross receipts from business done in Texas of $500,000 or more.' ⚠ The trigger is the ENTITY'S ACCOUNTING PERIOD, not the report due date, and the nexus BEGIN DATE is the FIRST DAY of that period, not the crossing date. This is the cheapest filter in the module — it gates out-of-state clients entirely.",
     "notes": "Threshold is TY-keyed (TX_ECONOMIC_NEXUS_RECEIPTS)."},

    {"rule_id": "R-TX-GATE", "title": "⚠ THE FILING-OBLIGATION GATE — five outcomes, evaluated FIRST", "rule_type": "routing",
     "formula": ("STEP 1 not is_taxable_entity            -> (A) NOTHING ; "
                 "STEP 2 not has_nexus                    -> (A) NOTHING ; "
                 "STEP 3 is_new_veteran_owned             -> (A) NOTHING ; "
                 "STEP 4 is_passive_entity or is_qualifying_reit -> (B) STUB REPORT ; "
                 "STEP 5 annualized_total_revenue <= 2650000 AND not tiered_partnership_election "
                 "-> (C) PIR-OR-OIR ONLY, NO FRANCHISE REPORT ; "
                 "STEP 6 annualized_total_revenue <= 20000000 AND ez_elected -> (D) EZ (render 05-169) ; "
                 "STEP 7 otherwise                        -> (E) LONG FORM (render 05-158-A/B)"),
     "inputs": ["is_taxable_entity", "has_nexus", "is_new_veteran_owned", "is_passive_entity",
                "is_qualifying_reit", "annualized_total_revenue", "ez_elected",
                "tiered_partnership_election", "legal_form"],
     "outputs": ["filing_outcome", "franchise_report", "render_target", "info_report"], "sort_order": 2,
     "description": "THE SINGLE MOST IMPORTANT RULE IN THE MODULE — it decides whether the software produces anything at all, and the most common outcome for a small-firm client base is (C) 'an information report only, no tax return.' ⚠ Outcome (C) verbatim, 05-915 Item 10: 'If the annualized total revenue is less than or equal to $2,650,000, and the entity is not an upper or lower tier entity making the tiered partnership election, stop here, you are not required to file a franchise tax report. However, you are required to file a Public Information Report (Form 05-102) or Ownership Information Report (Form 05-167).' There is NO 'no tax due report' object — Form 05-163 was DISCONTINUED and the Comptroller's 2026 forms page says outright: 'The No Tax Due Report is not available for 2026 reports.'",
     "exceptions": "SIDE BRANCH — ZERO TEXAS GROSS RECEIPTS at any revenue level above the threshold: the apportionment factor is zero so no tax is due, BUT the entity 'must file a Long Form Report (Form 05-158) or, if qualified, the EZ Computation Report (Form 05-169) to report total revenue, Texas gross receipts and gross receipts everywhere,' AND must also file a PIR or OIR. That is outcome (E) or (D) with a zero factor — NOT outcome (C). SIDE BRANCH — FIRST ANNUAL REPORT where the entity became subject during 2025 with a federal year end before that date: begin date = end date = the date it became subject, producing a ZERO report, and the PIR/OIR is still required.",
     "notes": "Step 5's tiered-partnership carve-out is stated so the interaction is correct; tiered partnerships themselves are RED-DEFERRED (R3)."},

    {"rule_id": "R-TX-INFOREPORT", "title": "PIR (05-102) vs OIR (05-167) routing, with the three carve-outs", "rule_type": "routing",
     "formula": ("if is_final_report or is_passive_entity or is_new_veteran_owned: info_report = NONE ; "
                 "elif legal_form in {corporation, s_corp, professional_corporation, llc, single_member_llc, "
                 "series_llc, LIMITED PARTNERSHIP, professional_association, financial_institution, bank, "
                 "state_limited_banking_association, savings_and_loan}: info_report = TX_05_102 (PIR) ; "
                 "else: info_report = TX_05_167 (OIR)   # GP, LLP, trust, JV, business association, other"),
     "inputs": ["legal_form", "is_final_report", "is_passive_entity", "is_new_veteran_owned"],
     "outputs": ["info_report"], "sort_order": 3,
     "description": "A clean complement. PIR verbatim: 'Each corporation, limited liability company (LLC), limited partnership, professional association and financial institution that has a franchise tax responsibility must file a Public Information Report (PIR) to satisfy their filing requirements.' OIR verbatim: 'The Ownership Information Report (OIR) is to be filed for each taxable entity other than a legally formed corporation, limited liability company, limited partnership, professional association or financial institution.' ⚠ An LLP is NOT an 'LP' — an LLP files the OIR. A REIT files one; a PASSIVE entity does not. The question is also asked on the 05-158-A form face, and the FINAL report OMITS it — corroborating carve-out 1 from the form face itself.",
     "exceptions": "THREE carve-outs where NEITHER is filed: (1) FINAL REPORTS — 'A Public Information Report (Form 05-102) or an Ownership Information Report (Form 05-167) is NOT required to be filed with the final report.' (2) PASSIVE ENTITIES. (3) NEW VETERAN-OWNED BUSINESSES during the initial five-year period. Do NOT hardwire 'every Texas entity produces a PIR or an OIR.'",
     "notes": "A separate PIR/OIR is filed by each entity that files a separate franchise report OR that is part of a combined group, 'unless the entity is not organized in Texas and does not have nexus in Texas.'"},

    {"rule_id": "R-TX-STUB", "title": "Passive-entity / REIT stub report (outcome B)", "rule_type": "routing",
     "formula": ("if is_passive_entity or is_qualifying_reit: emit 05-158 (or 05-169) with the Passive "
                 "and/or REIT circle blackened and ONLY the Taxpayer Information part completed "
                 "(accounting period dates + signature). NO revenue lines, NO margin, NO tax. "
                 "info_report = NONE if is_passive_entity else routed normally for a REIT"),
     "inputs": ["is_passive_entity", "is_qualifying_reit", "legal_form"],
     "outputs": ["render_target", "info_report"], "sort_order": 4,
     "description": "05-915 SIC/Passive field instructions: blackening either circle means completing 'the Taxpayer Information part of this form only'. A PASSIVE entity files NO PIR and NO OIR, and an unregistered passive partnership or trust 'is not required to register or file a franchise tax report' at all. A REIT by contrast: 'Each REIT or qualified REIT subsidiary must file either a Public Information Report (Form 05-102) or an Ownership Information Report (Form 05-167).'",
     "notes": "Passive test §171.0003: >=90% of federal gross income from the closed passive list. ⚠ 'Passive income does not include rent.' Corporations and LLCs can NEVER be passive entities. An entity that loses passive status registers via AP-114 / AP-224 / AP-231."},

    {"rule_id": "R-TX-FEDMAP", "title": "⚠ FEDERAL HANDOFF — named facts, NOT hard-coded federal line numbers (W6)", "rule_type": "validation",
     "formula": ("Items 1-7 and the Item 9 bad-debt / Schedule C DRD categories are supplied as NAMED FACTS. "
                 "The federal SOURCE LINE for each is a per-report-year DATA TABLE that MUST be re-verified "
                 "against the FINAL 2025 federal forms (1120, 1120S, 1065, 1041, Sch C/E/F, 8825, 4797, "
                 "Sch D) before the app build. NO federal line number is encoded in this spec."),
     "inputs": ["fed_gross_receipts_or_sales", "fed_dividends", "fed_interest", "fed_rents",
                "fed_royalties", "fed_gains_losses", "fed_other_income", "excl_bad_debt",
                "excl_sch_c_dividends_received_deduction"],
     "outputs": ["federal_map_verification_required"], "sort_order": 5,
     "description": "⚠⚠ BLOCKING (W6 / U2). 05-915 (Rev. 4-26/2) states verbatim: 'The line items indicated in this section refer to specific lines from the 2024 Internal Revenue Service (IRS) forms, which are the most current available at the time of publication' — but the 2026 report is built on an accounting period ending in calendar 2025, i.e. a 2025 federal return. The booklet also warns 'federal line numbers are subject to change throughout the year,' and the statute pins the map to 2006-form EQUIVALENTS. The ~30-cell map is the module's spine; if any line moved, it ships wrong.",
     "exceptions": "Federal-consolidated / disregarded caveat, verbatim: 'If a taxable entity was part of a federal consolidated return or was disregarded for federal tax purposes and is not being treated as disregarded in a combined group report ... report the amounts on Items 1-7 and 9 AS IF THE ENTITY HAD FILED A SEPARATE RETURN for federal income tax purposes.' That is a real preparer WORKPAPER obligation, not a pull. Catch-all: 'For a taxable entity filing a federal tax form other than those mentioned above, enter an amount that is substantially equivalent to the amounts discussed in this section.'",
     "notes": "Deliberately a VALIDATION rule, not a calculation — it asserts the re-verification obligation rather than encoding a mapping that is known to be a report-year behind."},

    {"rule_id": "R-TX-REVENUE", "title": "Total revenue Items 8-10 (Item 10 floored at zero)", "rule_type": "calculation",
     "formula": ("Item8 = Item1 + Item2 + Item3 + Item4 + Item5 + Item6 + Item7 ; "
                 "Item9 = sum of the closed-list exclusion categories ; "
                 "Item10 = max(0, Item8 - Item9)"),
     "inputs": ["fed_gross_receipts_or_sales", "fed_dividends", "fed_interest", "fed_rents",
                "fed_royalties", "fed_gains_losses", "fed_other_income", "excl_bad_debt",
                "excl_sch_c_dividends_received_deduction", "excl_foreign_dividends_royalties",
                "excl_net_distributive_income", "excl_flow_through_funds",
                "excl_other_statutory_categories", "excl_intercompany_or_tiered_pass"],
     "outputs": ["Item8", "Item9", "Item10"], "sort_order": 6,
     "description": "Item 8 'Total gross revenue (Add items 1 thru 7)'; Item 10 'TOTAL REVENUE (Item 8 minus item 9; if less than zero, enter 0)'. ⚠ Item 3 Interest: 'The amount reported must be zero or greater. We do not allow a negative amount on Item 3.' Items 4, 6 and 7 MAY be negative per the form face. ⚠ Item 9 is a CLOSED LIST: 'Only the following items may be excluded from gross revenue.'",
     "exceptions": "⚠ K-1 RENTAL INTERLOCK, verbatim: 'Do not include in Item 4 net rental income (loss) passed through from a partnership or S corporation on IRS Form K-1; report this amount in Item 7. This amount must also be included in Item 9 when subtracting net distributive income from a taxable entity treated as a partnership or as an S corporation for federal tax purposes.' A genuine three-item interlock, not a note. ⚠ GILTI/§78/§§951-964 amounts are INCLUDIBLE in total revenue and are NOT subtractable on Item 9 (the 2007-IRC pin).",
     "notes": "Texas builds total revenue from named federal form lines, NOT from federal taxable income. There is no 'starting point' in the income-tax sense."},

    {"rule_id": "R-TX-ANNUALIZE", "title": "Annualized total revenue — threshold and EZ tests ONLY", "rule_type": "calculation",
     "formula": ("annualized_total_revenue = Item10 / days_in_accounting_period * 365 "
                 "(identity when the period is 365 days)"),
     "inputs": ["Item10", "days_in_accounting_period"], "outputs": ["annualized_total_revenue"], "sort_order": 7,
     "description": "05-915: 'divide total revenue by the number of days in the period, multiply the result by 365.' ⚠ Used ONLY to test the no-tax-due threshold and EZ eligibility — 'The amount of total revenue used in the tax calculations does NOT change as a result of annualizing total revenue.' Feeding annualized revenue into Items 19-22 is a bug.",
     "notes": "The form face flags it: '** If not twelve months, see instructions for annualized revenue'."},

    {"rule_id": "R-TX-COGS", "title": "COGS Items 11-14, with the Item 12 4% cap computed", "rule_type": "calculation",
     "formula": ("Item11 = cogs_item11_qualifying   [DIRECT-ENTRY — never derived] ; "
                 "Item12 = 0.04 * indirect_admin_overhead_base   [CAPPED] ; "
                 "Item13 = cogs_item13_other   [may be negative or positive] ; "
                 "Item14 = Item11 + Item12 + Item13"),
     "inputs": ["cogs_item11_qualifying", "indirect_admin_overhead_base", "cogs_item13_other",
                "cogs_eligibility_affirmed", "cogs_expense_or_capitalize_election"],
     "outputs": ["Item11", "Item12", "Item13", "Item14"], "sort_order": 8,
     "description": "⚠ W3 — ITEM 11 IS DIRECT-ENTRY. 05-915: 'Generally COGS for Texas franchise tax reporting purposes will not equal the amount used for federal income tax reporting purposes or for financial accounting purposes. Typically, this amount CANNOT BE FOUND ON A FEDERAL INCOME TAX REPORT or on an income statement. It is a calculated amount specific to Texas franchise tax.' Item 12 verbatim: 'This amount is limited to 4% of total indirect/administrative overhead costs.' Eligibility gate: only entities that OWN and sell real or tangible personal property in the ordinary course, or qualify under a §171.1012 / Rule 3.588 exception — 'Generally, a taxable entity in the service industry does not have qualifying COGS.'",
     "exceptions": "⚠ THE ONE-TIME NET DEPRECIATION CATCH-UP IS ABSORBED INTO ITEM 11 AND HAS NO LINE OF ITS OWN — it is RED-DEFERRED (R1, D_TX_DEPR_CATCHUP) and is NOT computed here: its zero floor is PER ASSET, its entity-level limiter is CIRCULAR (bounded by margin, which the catch-up itself moves), its carryforward has no form field anywhere, and it needs per-asset per-year federal-vs-Texas depreciation history Delvio does not hold. ⚠ NO ASSET-LEVEL BONUS DATE GATE IS ENCODED — see W1 / D_TX_BONUS_DATE_GATE. ⚠ NO Texas §179 dollar cap exists for the 2026 report (adopted Rule 3.588 deletes the IRC §179 reference); encode 'the federal amount as claimed', not a cap and not a literal 'unlimited'. ⚠ §197 recovery is an INCLUDABLE COGS cost but is determined under the 2007 IRC and is excluded from the catch-up.",
     "notes": "Excluded from COGS (closed list): officers' compensation, non-production rent, selling costs incl. credit card fees, distribution and outbound transportation, advertising, idle facility expense, rehandling, bidding, interest, income taxes, strike expenses (but replacement wages, security and settlement legal fees ARE includable), and federal military-housing facility operating costs."},

    {"rule_id": "R-TX-COMP", "title": "Compensation Items 15-18 — ⚠ $480,000 cap on ITEM 15 ONLY", "rule_type": "calculation",
     "formula": ("Item15 = SUM over each person of min(person_wages, 480000 * comp_cap_proration_factor) "
                 "   # PER PERSON, not an entity-level cap; negative NDI passes through UNCAPPED ; "
                 "Item16 = comp_benefits_item16     # ⚠ NO CAP APPLIED ; "
                 "Item17 = comp_item17_other ; "
                 "Item18 = Item15 + Item16 + Item17"),
     "inputs": ["comp_wages_person_roster", "comp_cap_proration_factor", "comp_negative_ndi",
                "comp_benefits_item16", "comp_item17_other"],
     "outputs": ["Item15", "Item16", "Item17", "Item18"], "sort_order": 9,
     "description": "Item 15 verbatim: 'amounts paid to officers, directors, owners, partners and employees for the accounting period, limited to $480,000 per person per 12-month period, prorated for the period upon which the tax is based.' Item 16 verbatim: 'The deduction for employee benefits is NOT limited to $480,000 per person but is only deductible to the extent deductible for federal income tax purposes.' ⚠⚠ APPLYING THE CAP TO ITEM 16 IS THE SINGLE MOST COMMON MISCODING IN THIS SCHEDULE. ⚠ Negative NDI is uncapped: 'There is no cap or limitation on negative compensation.' Item 15 EXCLUDES payments on Forms 1099, amounts excluded from gross revenue, the employer's share of employment taxes, and amounts paid to an employee whose primary employment is at a federal military-housing facility.",
     "exceptions": "⚠ W7/U3 — the PRORATION FORMULA IS UNKNOWN. 05-915 gives none ('prorat' appears exactly once, in the Item 15 sentence) and states the cross-member denominator two ways: 'upon which the REPORT is based' (Combined Group) vs 'upon which the TAX is based' (Item 15). 34 TAC §3.589 is unread (U5). comp_cap_proration_factor is DIRECT-ENTRY, default 1.0. ⚠ The cap is PER PERSON ACROSS A WHOLE COMBINED GROUP, not per member — but combined groups are RED-DEFERRED (R2). ⚠ PEO / management company regimes rewrite Items 15 and 16 — RED-DEFERRED (R9).",
     "notes": "$480,000 is TY-keyed and BIENNIAL: 'Effective for reports originally due on or after Jan. 1, 2026, and before Jan. 1, 2028. Tax Code Section 171.006(b).'"},

    {"rule_id": "R-TX-MARGIN", "title": "⚠⚠ MARGIN Items 19-23 — THE LOWEST OF FOUR, each floored at zero first", "rule_type": "calculation",
     "formula": ("Item19 = max(0, Item10 * 0.70)          # 70% of revenue ; "
                 "Item20 = max(0, Item10 - Item14)         # revenue less COGS ; "
                 "Item21 = max(0, Item10 - Item18)         # revenue less compensation ; "
                 "Item22 = max(0, Item10 - 1000000)        # revenue less $1 MILLION ; "
                 "Item23 = max(0, MIN(Item19, Item20, Item21, Item22))"),
     "inputs": ["Item10", "Item14", "Item18"], "outputs": ["Item19", "Item20", "Item21", "Item22", "Item23"],
     "sort_order": 10,
     "description": "Item 23 verbatim: 'Enter the lowest amount from Items 19, 20, 21, or 22. If the amount is less than zero, enter zero.' ⚠⚠ ENCODE THE FOUR-WAY MINIMUM, NOT THE THREE-WAY MAXIMUM. The industry shorthand 'revenue minus the greatest of COGS / compensation / 30% of revenue' is arithmetically equal for branches 19-21 but SILENTLY DROPS ITEM 22, the $1,000,000 branch — which is frequently the best answer for a small, labor-light service entity with no COGS. Item 22 beats Item 19 whenever revenue < $3,333,333, and Item 22 is on the 05-158-B form face verbatim as 'Revenue less $1 million (Item 10 - $1,000,000)'. Each branch is separately floored at zero BEFORE the minimum is taken.",
     "exceptions": "⚠ EVERY BRANCH IS AVAILABLE TO EVERY FILER — there is no election and no eligibility test on branches 19, 21 or 22. Only branch 20 is gated: the entity must actually HAVE qualifying COGS (§171.1012 / Rule 3.588). A service entity with no COGS computes Item 20 as Item10 - 0 = Item10, which then loses the minimum. A COMBINED GROUP 'may choose only one method for computing margin that applies to all members' and gets '$1 million for the combined group, not for each member' — RED-DEFERRED (R2). ⚠ NO MARGIN DEDUCTION AT ALL is allowed on the EZ path.",
     "notes": "$1,000,000 is a flat statutory amount, not indexed. Confirmed three ways: the 05-158-B form face, the 05-915 Margin narrative, and the Combined Group section."},

    {"rule_id": "R-TX-APPORT", "title": "Apportionment factor Items 24-26 — single gross receipts factor, 4 decimals", "rule_type": "calculation",
     "formula": ("if Item24 <= 0: Item26 = 0.0000 ; "
                 "elif Item25 <= 0: Item26 = 0.0000 ; "
                 "elif Item24 >= Item25: Item26 = 1.0000 ; "
                 "else: Item26 = round(Item24 / Item25, 4)"),
     "inputs": ["texas_gross_receipts_item24", "everywhere_gross_receipts_item25"],
     "outputs": ["Item26"], "sort_order": 11,
     "description": "Item 26 verbatim: 'If Texas gross receipts in Item 24 are zero, enter zero. If Item 24 and Item 25 are the same and greater than zero, enter 1.0000. If Item 24 is more than Item 25 and both are greater than zero, enter 1.0000. Otherwise, divide Item 24 by Item 25 and round to 4 places past the decimal.' A SINGLE GROSS RECEIPTS factor — no property factor, no payroll factor, so the usual three-factor / single-sales-factor vocabulary does not apply. 'Gross receipts' is a broader base than 'sales'. NO THROWBACK and NO THROWOUT rule exists (a CHECKED ABSENCE in Rule 3.591, not merely 'no rule found').",
     "exceptions": "⚠ SIDE BRANCH — zero Texas receipts produces a zero factor and therefore no tax, but the entity MUST STILL FILE the long form or EZ plus the PIR/OIR. That is outcome (E)/(D), NOT outcome (C). ⚠ §171.106 special apportionment for regulated investment company services and employee retirement plan services is RED-DEFERRED (R8). ⚠ Combined-group apportionment (Texas numerator counts only members organized in TX or with TX nexus; the denominator counts all members; plus the drop-shipment rule) is RED-DEFERRED (R2).",
     "notes": "U7: the operative Rule 3.591(e)-(f) sourcing text was read only in 05-915 summary form. Close before Item 24/25 preparer guidance ships."},

    {"rule_id": "R-TX-RATE", "title": "⚠ Rate selection Item 30 — driven by the SIC field; BLANK DEFAULTS TO 0.75%", "rule_type": "classification",
     "formula": ("if sic_code is blank/empty: Item30 = 0.0075   # ⚠ EXPLICIT BLANK DEFAULT ; "
                 "elif retail_wholesale_qualified: Item30 = 0.00375 ; "
                 "else: Item30 = 0.0075 ; "
                 "EZ path: rate is 0.00331, hardcoded on the 05-169 form face"),
     "inputs": ["sic_code", "retail_wholesale_qualified", "naics_code"],
     "outputs": ["Item30"], "sort_order": 12,
     "description": "⚠ Verbatim: 'This field determines the tax rate. Completion of the field is optional; however, IF LEFT BLANK, THE TAX RATE DEFAULTS TO 0.75%.' ⚠ NAICS IS PURELY INFORMATIONAL — the form carries both fields and only the SIC field is rate-bearing. 'If the SIC code on Form 05-158-A does not fit the definition of qualifying retailers and wholesalers, the 0.375% tax rate WILL BE DENIED when the report is processed.' Retail = 1987 SIC Manual Division G plus apparel rental in SIC 5999/7299, Industry Group 753, tool/party/furniture rental in SIC 7359, heavy construction equipment in SIC 7353, and Tex. Bus. & Com. Code ch. 92 rental-purchase agreements; wholesale = Division F. ALL THREE conditions must hold (retail/wholesale revenue exceeds other trades; except eating and drinking places in Major Group 58, less than 50% from self-produced products; no retail/wholesale utilities).",
     "exceptions": "A COMBINED GROUP 'must look at the total revenue of the group to determine the applicable tax rate' and may exclude a retail/wholesale electric utility member whose activity disqualifies the group if that member's utility revenue is under 5% of group total revenue — RED-DEFERRED (R2).",
     "notes": "Rates unchanged for reports originally due on or after Jan. 1, 2016. TY-keyed."},

    {"rule_id": "R-TX-TAXMARGIN", "title": "Taxable margin Items 27-29", "rule_type": "calculation",
     "formula": ("Item27 = Item23 * Item26 ; "
                 "Item28 = allowable_deductions_item28   [DIRECT-ENTRY; may not reduce Item 27 below zero] ; "
                 "Item29 = max(0, Item27 - Item28)"),
     "inputs": ["Item23", "Item26", "allowable_deductions_item28"], "outputs": ["Item27", "Item29"],
     "sort_order": 13,
     "description": "Item 27 'Apportioned margin (Multiply item 23 by item 26)'; Item 29 'TAXABLE MARGIN (Item 27 minus item 28)'. Item 28 admits EXACTLY THREE deductions: 10% of the amortized cost of a §171.107(b) solar energy device, 10% of the amortized cost of §171.108(b) clean-coal equipment, and §171.109(b) relocation costs (FIRST ANNUAL REPORT ONLY, Rule 3.584(c)(2)). Each 'may not reduce apportioned margin below zero, and no carryover of unused deductions is allowed.'",
     "notes": "Items 1-29 are WHOLE DOLLARS; Items 31-35 are dollars and cents; Item 26 is a 4-decimal factor."},

    {"rule_id": "R-TX-TAXDUE", "title": "Tax due Items 31-35 — no discount, no minimum tax", "rule_type": "calculation",
     "formula": ("Item31 = Item29 * Item30   [dollars and cents] ; "
                 "Item32 = tax_credits_item32   [DIRECT-ENTRY, 05-181 Item 17] ; "
                 "Item33 = max(0, Item31 - Item32) ; "
                 "Item34 = 0   # ALWAYS ; "
                 "Item35 = Item33 - Item34 == Item33"),
     "inputs": ["Item29", "Item30", "tax_credits_item32"],
     "outputs": ["Item31", "Item33", "Item34", "Item35"], "sort_order": 14,
     "description": "Item 33 'If less than zero, enter zero.' Item 34 Discount: 'Discounts do not apply to reports due after Dec. 31, 2009' — structurally ALWAYS ZERO. Item 35: 'Must equal the amount of tax due in Item 33 since discounts do not apply.' ⚠ NO MINIMUM TAX: 'There is no minimum tax requirement under the franchise tax provisions' — a zero margin produces a zero tax, never a floor amount. ⚠ NO ESTIMATED PAYMENTS: 'Texas law does not require the filing of estimated tax reports or payments' — no quarterly obligation and no estimate-based penalty. Item 32 is capped by 05-181's own Item 17 rule ('Amount cannot exceed Item 1').",
     "exceptions": "Credits are RED-DEFERRED (R4) and are entirely FORFEITED on the EZ path.",
     "notes": "There is also no net-worth or capital-stock franchise tax in Texas — that was repealed when the margin tax replaced it in 2008. The margin tax IS the entire entity-level state tax."},

    {"rule_id": "R-TX-NOPAY", "title": "⚠ The <$1,000 no-payment rule vs the threshold branch — DIFFERENT OUTPUTS", "rule_type": "conditional",
     "formula": ("if tiered_partnership_election: payment_required = (Item35 > 0)   # election defeats BOTH ; "
                 "elif annualized_total_revenue <= 2650000: payment_required = False  "
                 "AND NO FRANCHISE REPORT WAS PRODUCED AT ALL (gate outcome C) ; "
                 "else: payment_required = (Item35 >= 1000)   # STRICTLY less than 1000 => no payment, "
                 "but the FULL report and the PIR/OIR are still filed"),
     "inputs": ["Item35", "annualized_total_revenue", "tiered_partnership_election"],
     "outputs": ["payment_required", "report_still_required"], "sort_order": 15,
     "description": "⚠ TWO DIFFERENT BRANCHES OF §171.002(d), BOTH PRODUCING 'NO TAX', BUT PRODUCING DIFFERENT FILINGS — conflating them is the failure mode. THRESHOLD BRANCH §171.002(d)(2): tested on ANNUALIZED total revenue BEFORE the report is computed; it TERMINATES the computation; the franchise report is NOT FILED AT ALL (05-163 does not exist for 2026); PIR/OIR still required; evaluated FIRST, at Item 10. <$1,000 BRANCH §171.002(d)(1): tested on the COMPUTED tax AFTER the whole report is computed; the report is FILED IN FULL showing the computed amount; payment is suppressed; PIR/OIR still required; evaluated LAST, at Item 35. Verbatim: 'an entity that calculates an amount of tax due that is less than $1,000 is not required to pay any tax.... The entity, however, MUST SUBMIT ALL REQUIRED REPORTS to satisfy its filing requirements.' And Item 35: 'If this amount is less than $1,000, you owe no tax, but you must submit this report along with the Public Information Report (Form 05-102) and/or the Ownership Information Report (Form 05-167).' ⚠ THE TEST IS STRICTLY LESS THAN $1,000 — exactly $1,000 IS payable.",
     "exceptions": "⚠ A TIERED-PARTNERSHIP ELECTION DEFEATS BOTH BRANCHES, printed on the face of both 05-158-B and 05-169: 'Both the upper and lower tier entities owe any amount of tax that is calculated as due even if the amount is less than $1,000 or annualized total revenue after the tiered partnership election is $2,650,000 or less.' Tiered partnerships are RED-DEFERRED (R3) — the flag exists so the interaction is STATED, not so v1 computes it. Form 05-158-B footer: 'Do not include payment if item 35 is less than $1,000 or if annualized total revenue is less than or equal to the no tax due threshold... If the entity makes a tiered partnership election, ANY amount in item 35 is due.'",
     "notes": "⚠ Correction C7: the 05-169 form face says only 'less than' the threshold while 05-158-B, 05-915 and the statute say 'less than OR EQUAL TO'. 05-915 and the statute govern — do not read the EZ face literally at exactly $2,650,000."},

    {"rule_id": "R-TX-EZ", "title": "EZ computation branch (05-169 Items 14-17) — apportioned REVENUE x 0.331%", "rule_type": "calculation",
     "formula": ("EZ Items 1-10 are IDENTICAL to long-form Items 1-10 (shared revenue build) ; "
                 "EZ Items 11-13 are IDENTICAL to long-form Items 24-26 (shared apportionment) ; "
                 "EZ14 = Item10 * Item26   [dollars and cents] ; "
                 "EZ15 = EZ14 * 0.00331 ; "
                 "EZ16 = 0   # always ; "
                 "EZ17 = EZ15 - EZ16 == EZ15 ; "
                 "NO margin, NO COGS, NO compensation, NO Item 28 deductions, NO Item 32 credits"),
     "inputs": ["Item10", "Item26", "ez_elected", "annualized_total_revenue"],
     "outputs": ["EZ14", "EZ15", "EZ16", "EZ17"], "sort_order": 16,
     "description": "W2 — encoded as an INTERNAL COMPUTATION BRANCH of TX_05_158 with a separate 05-169 render target, NOT as a second spec. 05-915 documents 13 of 05-169's 17 items by cross-reference to 05-158, TEN OF THEM BARE (Items 1-8, 10, 13); Item 9 adds only the EZ-specific bar 'Do not enter COGS or compensation amounts as they cannot be deducted if electing to use the EZ computation,' and Items 11-12 add 'and Rule 3.591' pointers. Items 11-13 point at 05-158-B. The EZ has NO independent revenue build, so two copies of the ~30-cell federal line map plus the 30+-category exclusion list would drift within one report year. Eligibility: 'Any entity (including a combined group) that has annualized total revenue of $20 million or less is eligible.' Cost: 'Taxable entities that elect this method to file are not eligible to take any credits or deductions. When using the EZ computation, the current year's portion of the temporary credit for business loss carryforwards may not be used AND MAY NOT BE CARRIED OVER to a future period.' 'No margin deduction (COGS, compensation, 30% of revenue or $1 million) is allowed.'",
     "exceptions": "FALLBACK if RS cannot express one-spec-two-render-targets: a thin TX_05_169 spec that REFERENCES TX_05_158's revenue and apportionment facts rather than restating them. ⚠ WHAT MUST NOT HAPPEN IS TWO INDEPENDENT COPIES OF THE REVENUE BUILD. The 05-169 render target carries its own 17-item numbering, its own Tcode (13252) and its own 2D barcode.",
     "notes": "The 0.00331 rate is hardcoded on the 05-169 form face at Item 15. EZ eligibility for a tiered arrangement is tested on the LOWER tier's pre-pass annualized revenue (RED-DEFERRED, R3)."},

    {"rule_id": "R-TX-EZCOMPARE", "title": "Both-paths comparison — RECOMMEND, never silently default (W8)", "rule_type": "classification",
     "formula": ("ez_breakeven_margin_ratio = 0.00331 / long_form_rate ; "
                 "vs 0.0075  -> 0.441333... (44.13% of revenue) ; "
                 "vs 0.00375 -> 0.882666... (88.27% of revenue) ; "
                 "EZ is cheaper ONLY when Item23 / Item10 exceeds that ratio ; "
                 "since the four-way minimum caps margin at 70% of revenue and 70% < 88.27%, "
                 "A QUALIFYING RETAILER OR WHOLESALER SHOULD NEVER ELECT THE EZ"),
     "inputs": ["Item10", "Item23", "Item30", "annualized_total_revenue"],
     "outputs": ["ez_recommended", "ez_breakeven_margin_ratio"], "sort_order": 17,
     "description": "⚠ THE EZ IS A GENUINE TRADE-OFF, NOT A CONVENIENCE — AND IT IS OFTEN THE WRONG ANSWER. It taxes apportioned REVENUE, not margin, so it is MORE EXPENSIVE for every entity whose margin is below ~44.13% of revenue — i.e. for exactly the COGS-heavy or labor-heavy entities that most often reach for it. On top of the arithmetic it forfeits all credits and permanently destroys the current year's temporary-credit-for-business-loss-carryforwards portion. The module should COMPUTE BOTH PATHS AND RECOMMEND, not default to whichever the prior preparer used.",
     "notes": "W8 — confirm with Ken that a recommendation UI (rather than a silent default) is wanted."},

    {"rule_id": "R-TX-DEPRDEFER", "title": "⚠ One-time net depreciation catch-up — NOT COMPUTED (RED-DEFER R1)", "rule_type": "validation",
     "formula": ("NO COMPUTATION. depr_catchup_manual_item11 is a DIRECT-ENTRY figure prepared manually "
                 "and folded into Item 11. Delvio computes neither the per-asset adjustment, nor the "
                 "per-asset zero floor, nor the circular margin limiter, nor the carryforward balance."),
     "inputs": ["depr_catchup_manual_item11"], "outputs": ["depr_catchup_deferred"], "sort_order": 18,
     "description": "Four structural facts, all CONFIRMED and double-sourced (05-915 Item 11 AND adopted Rule 3.588(B)): (1) IT HAS NO LINE OF ITS OWN — absorbed into Item 11, invisible on the filed form, not disclosed on 05-158-A/B, 05-169, 05-166 or 05-181; (2) THE ZERO FLOOR IS PER ASSET — 'the net depreciation adjustment for THAT QUALIFYING ASSET ... cannot be less than zero'; negative-net assets floor at zero individually and do NOT offset positive-net assets, so an entity-level sum with one floor is the obvious implementation bug; (3) THE ENTITY-LEVEL LIMITER IS CIRCULAR — admitted only 'to the extent the adjustment does not take the taxable entity's MARGIN below zero', and adding catch-up to COGS raises Item 14, lowers Item 20, and can change which of the four branches is the minimum, so it must be solved as 'the largest catch-up such that Item 23 >= 0'; (4) THE CARRYFORWARD HAS NO FORM FIELD ANYWHERE — it runs 'to consecutive reports until exhausted' with no 2026 line and no 2027 form in existence (U4).",
     "exceptions": "⚠ W1 — NO ASSET-LEVEL BONUS DATE KEY IS ENCODED ANYWHERE IN THIS SPEC. The REPORT-YEAR gate ('beginning with the 2026 franchise tax report') is NOT in dispute; what is disputed is whether an INDIVIDUAL ASSET carries a placed-in-service or acquisition date test. STAR 202603002M says 'placed in service on or after January 19, 2025'; the Dec. 2025 news release says 'acquired after Jan. 19, 2025'; adopted Rule 3.588 and the FINAL 05-915 impose NO asset-level date gate at all. This is an ESCALATED Ken judgement call (GATE1_WALK item 4) — see D_TX_BONUS_DATE_GATE.",
     "notes": "Also unmodelled and unguessed: §197 recovery is an includable COGS cost but is determined under the 2007 IRC and is EXCLUDED from the catch-up; ITC-reduced basis governs both TX COGS depreciation and the adjustment; the adjustment is prospective only and cannot be claimed by amending prior years."},
]

TX158_RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R-TX-NEXUS", "TX_34TAC_3_586_NEXUS", "primary", "$500,000 economic nexus, keyed to the federal accounting period"),
    ("R-TX-NEXUS", "TX_2026_FORM_05_915", "secondary", "doing-business / organized-in-Texas triggers"),
    ("R-TX-GATE", "TX_2026_FORM_05_915", "primary", "Item 10 stop-here rule and the five filing outcomes, verbatim"),
    ("R-TX-GATE", "TX_TAX_CODE_CH171", "primary", "§171.0002 taxable entities; §171.002(d)(2) threshold; §171.006(b) indexing"),
    ("R-TX-GATE", "TX_2026_FORMS_INDEX", "secondary", "05-163 does not exist for 2026 — no No-Tax-Due-Report object"),
    ("R-TX-INFOREPORT", "TX_2026_FORM_05_915", "primary", "PIR and OIR filing-requirement sentences + the three carve-outs"),
    ("R-TX-INFOREPORT", "TX_2026_FORM_05_158", "secondary", "the routing question on the 05-158-A form face; the FINAL report omits it"),
    ("R-TX-STUB", "TX_2026_FORM_05_915", "primary", "passive/REIT circle: complete Taxpayer Information only"),
    ("R-TX-STUB", "TX_TAX_CODE_CH171", "secondary", "§171.0003 passive entity test; §171.0002(c)(4) qualifying REIT"),
    ("R-TX-FEDMAP", "TX_2026_FORM_05_915", "primary", "the verbatim 2024-federal-forms caveat — W6 / U2"),
    ("R-TX-REVENUE", "TX_2026_FORM_05_158", "primary", "Items 1-10 verbatim labels and the Item 10 zero floor"),
    ("R-TX-REVENUE", "TX_2026_FORM_05_915", "primary", "Item 3 non-negative; the K-1 rental interlock; the closed exclusion list"),
    ("R-TX-REVENUE", "TX_STAR_202603002M_IRC_CONFORMITY", "interpretive", "GILTI / §78 / §§951-964 includible and NOT subtractable (2007-IRC pin)"),
    ("R-TX-ANNUALIZE", "TX_2026_FORM_05_915", "primary", "annualization formula; used only for the threshold and EZ tests"),
    ("R-TX-COGS", "TX_2026_FORM_05_915", "primary", "Item 11 is a from-scratch Texas figure; Item 12 4% cap; Item 13 components"),
    ("R-TX-COGS", "TX_34TAC_3_588_COGS", "primary", "COGS rule as adopted 6/21/2026; IRC §179 reference deleted"),
    ("R-TX-COGS", "TX_TAX_CODE_CH171", "secondary", "§171.1012 includable/excluded cost lists and the ownership requirement"),
    ("R-TX-COGS", "TX_STAR_202603002M_IRC_CONFORMITY", "interpretive", "bonus/§179 flow into COGS with no opt-out (§171.1012(h))"),
    ("R-TX-COMP", "TX_2026_FORM_05_915", "primary", "$480,000 cap on Item 15 ONLY; Item 16 expressly uncapped; uncapped negative NDI"),
    ("R-TX-COMP", "TX_TAX_CODE_CH171", "secondary", "§171.1013 compensation; §171.006(b) biennial cap indexing"),
    ("R-TX-MARGIN", "TX_2026_FORM_05_158", "primary", "Items 19-23 on the form face incl. Item 22 'Revenue less $1 million'"),
    ("R-TX-MARGIN", "TX_2026_FORM_05_915", "primary", "Item 23: 'Enter the lowest amount from Items 19, 20, 21, or 22.'"),
    ("R-TX-APPORT", "TX_2026_FORM_05_915", "primary", "Item 26 zero rule, both 1.0000 rules, 4-decimal rounding"),
    ("R-TX-APPORT", "TX_2026_FORM_05_158", "secondary", "Items 24-26 form-face labels"),
    ("R-TX-RATE", "TX_2026_FORM_05_915", "primary", "SIC determines the rate; blank defaults to 0.75%; NAICS informational"),
    ("R-TX-TAXMARGIN", "TX_2026_FORM_05_158", "primary", "Items 27-29 form-face labels"),
    ("R-TX-TAXMARGIN", "TX_2026_FORM_05_915", "secondary", "the three Item 28 deductions and the no-below-zero / no-carryover rule"),
    ("R-TX-TAXDUE", "TX_2026_FORM_05_158", "primary", "Items 30-35 form-face labels and the footer payment rule"),
    ("R-TX-TAXDUE", "TX_2026_FORM_05_915", "primary", "no minimum tax; no discount after 2009; no estimated payments"),
    ("R-TX-NOPAY", "TX_2026_FORM_05_915", "primary", "Item 35 <$1,000 rule and 'must submit all required reports'"),
    ("R-TX-NOPAY", "TX_TAX_CODE_CH171", "primary", "§171.002(d)(1) and (d)(2) — the two distinct no-tax branches"),
    ("R-TX-EZ", "TX_2026_FORM_05_169_EZ", "primary", "EZ Items 1-17, the 0.00331 form-face rate, credit/deduction forfeiture"),
    ("R-TX-EZ", "TX_2026_FORM_05_915", "secondary", "EZ eligibility at $20M and the cross-reference structure (W2)"),
    ("R-TX-EZCOMPARE", "TX_2026_FORM_05_169_EZ", "primary", "the EZ taxes apportioned revenue, not margin — the break-even arithmetic"),
    ("R-TX-EZCOMPARE", "TX_2026_FORM_05_915", "secondary", "0.75% / 0.375% / 0.331% rate table"),
    ("R-TX-DEPRDEFER", "TX_2026_FORM_05_915", "primary", "Item 11 catch-up: per-asset floor, circular margin limiter, carryforward"),
    ("R-TX-DEPRDEFER", "TX_34TAC_3_588_COGS", "primary", "the per-asset framing is in the ADOPTED RULE, not merely the instructions"),
    ("R-TX-DEPRDEFER", "TX_STAR_202603002M_IRC_CONFORMITY", "interpretive", "W1 — the disputed asset-level placed-in-service date gate"),
]


TX158_LINES: list[dict] = [
    # ── Header (05-158-A; both pages carry taxpayer number / report year / due date) ──
    {"line_number": "HDR-TAXPAYER", "description": "Taxpayer number (11-digit); FEIN if none assigned", "line_type": "input", "source_facts": ["taxpayer_number", "sos_or_comptroller_file_number"], "sort_order": 1,
     "notes": "Report year preprinted 2026; due date preprinted 05/15/2026. ⚠ The 2026 report = Delvio TY2025."},
    {"line_number": "HDR-PERIOD", "description": "Accounting year begin date / end date (** if not twelve months, see annualized revenue)", "line_type": "input", "source_facts": ["accounting_year_begin_date", "accounting_year_end_date", "days_in_accounting_period"], "sort_order": 2},
    {"line_number": "HDR-NAICS", "description": "NAICS code — INFORMATIONAL ONLY, does not drive the rate", "line_type": "input", "source_facts": ["naics_code"], "sort_order": 3},
    {"line_number": "HDR-SIC", "description": "SIC code — ⚠ THIS FIELD DETERMINES THE TAX RATE; blank defaults to 0.75%", "line_type": "input", "source_facts": ["sic_code", "retail_wholesale_qualified"], "sort_order": 4},
    {"line_number": "HDR-PASSIVE", "description": "Passive circle — blacken and complete Taxpayer Information only", "line_type": "input", "source_facts": ["is_passive_entity"], "sort_order": 5},
    {"line_number": "HDR-REIT", "description": "REIT circle — stub report, but a PIR or OIR IS still required", "line_type": "input", "source_facts": ["is_qualifying_reit"], "sort_order": 6},
    {"line_number": "HDR-COMBINED", "description": "Combined report circle — RED-DEFER R2 (combined reporting is MANDATORY where it applies)", "line_type": "input", "source_facts": ["is_combined_group_member"], "sort_order": 7},
    {"line_number": "HDR-TIERED", "description": "Total Revenue adjusted for Tiered Partnership Election circle — RED-DEFER R3", "line_type": "input", "source_facts": ["tiered_partnership_election"], "sort_order": 8},
    {"line_number": "HDR-PIROIR", "description": "'Is this entity a corporation, limited liability company, professional association, limited partnership or financial institution? Yes/No' — the PIR-vs-OIR routing question on the form face", "line_type": "informational", "source_rules": ["R-TX-INFOREPORT"], "sort_order": 9,
     "notes": "⚠ The FINAL report (05-158-f) OMITS this question — corroborating from the form face that no PIR/OIR accompanies a final report."},
    {"line_number": "GATE", "description": "⚠ FILING-OBLIGATION GATE — five outcomes; decides whether anything is emitted at all", "line_type": "informational", "source_rules": ["R-TX-NEXUS", "R-TX-GATE", "R-TX-INFOREPORT", "R-TX-STUB"], "sort_order": 10},

    # ── REVENUE Items 1-10 (shared with the EZ path) ──
    {"line_number": "1", "description": "Gross receipts or sales", "line_type": "input", "source_facts": ["fed_gross_receipts_or_sales"], "sort_order": 11},
    {"line_number": "2", "description": "Dividends", "line_type": "input", "source_facts": ["fed_dividends"], "sort_order": 12},
    {"line_number": "3", "description": "Interest — ⚠ must be zero or greater; negatives are not allowed", "line_type": "input", "source_facts": ["fed_interest"], "sort_order": 13},
    {"line_number": "4", "description": "Rents (Can be negative amount)", "line_type": "input", "source_facts": ["fed_rents"], "sort_order": 14,
     "notes": "⚠ K-1 net rental income (loss) passed through from a partnership or S corp goes to Item 7, NOT here, and must also appear in Item 9."},
    {"line_number": "5", "description": "Royalties", "line_type": "input", "source_facts": ["fed_royalties"], "sort_order": 15},
    {"line_number": "6", "description": "Gains/losses (Can be negative amount)", "line_type": "input", "source_facts": ["fed_gains_losses"], "sort_order": 16},
    {"line_number": "7", "description": "Other income (Can be negative amount)", "line_type": "input", "source_facts": ["fed_other_income"], "sort_order": 17},
    {"line_number": "8", "description": "Total gross revenue (Add items 1 thru 7)", "line_type": "subtotal", "source_rules": ["R-TX-REVENUE"], "sort_order": 18},
    {"line_number": "9", "description": "Exclusions from gross revenue — CLOSED statutory list", "line_type": "input", "source_facts": ["excl_bad_debt", "excl_sch_c_dividends_received_deduction", "excl_foreign_dividends_royalties", "excl_net_distributive_income", "excl_flow_through_funds", "excl_other_statutory_categories", "excl_intercompany_or_tiered_pass"], "sort_order": 19,
     "notes": "⚠ GILTI / §78 / §§951-964 amounts are NOT excludable here (the 2007-IRC pin)."},
    {"line_number": "10", "description": "TOTAL REVENUE (Item 8 minus item 9; if less than zero, enter 0)", "line_type": "subtotal", "source_rules": ["R-TX-REVENUE", "R-TX-ANNUALIZE"], "sort_order": 20,
     "notes": "⚠ THE THRESHOLD BRANCH IS EVALUATED HERE. If annualized Item 10 <= $2,650,000 and there is no tiered-partnership election: 'stop here, you are not required to file a franchise tax report' — emit a PIR or OIR only."},

    # ── COST OF GOODS SOLD Items 11-14 ──
    {"line_number": "11", "description": "Cost of goods sold — ⚠ DIRECT-ENTRY; a from-scratch Texas figure that cannot be found on a federal return", "line_type": "input", "source_facts": ["cogs_item11_qualifying", "cogs_eligibility_affirmed", "cogs_expense_or_capitalize_election", "depr_catchup_manual_item11"], "sort_order": 21,
     "notes": "⚠ Silently absorbs the one-time net depreciation catch-up, which has NO LINE OF ITS OWN and is RED-DEFERRED (R1)."},
    {"line_number": "12", "description": "Indirect or administrative overhead costs (Limited to 4%)", "line_type": "calculated", "calculation": "R-TX-COGS", "source_facts": ["indirect_admin_overhead_base"], "source_rules": ["R-TX-COGS"], "sort_order": 22},
    {"line_number": "13", "description": "Other — undocumented worker (negative) / active duty / aerospace; may be negative or positive", "line_type": "input", "source_facts": ["cogs_item13_other"], "sort_order": 23},
    {"line_number": "14", "description": "TOTAL COST OF GOODS SOLD (Add items 11 thru 13)", "line_type": "subtotal", "source_rules": ["R-TX-COGS"], "sort_order": 24},

    # ── COMPENSATION Items 15-18 ──
    {"line_number": "15", "description": "Wages and cash compensation — ⚠ $480,000 PER PERSON cap applies HERE", "line_type": "calculated", "calculation": "R-TX-COMP", "source_facts": ["comp_wages_person_roster", "comp_cap_proration_factor", "comp_negative_ndi"], "source_rules": ["R-TX-COMP"], "sort_order": 25},
    {"line_number": "16", "description": "Employee benefits — ⚠ NOT subject to the $480,000 cap", "line_type": "input", "source_facts": ["comp_benefits_item16"], "sort_order": 26},
    {"line_number": "17", "description": "Other — undocumented worker / active duty / aerospace (against compensation)", "line_type": "input", "source_facts": ["comp_item17_other"], "sort_order": 27},
    {"line_number": "18", "description": "TOTAL COMPENSATION (Add items 15 thru 17)", "line_type": "subtotal", "source_rules": ["R-TX-COMP"], "sort_order": 28},

    # ── MARGIN Items 19-23 (05-158-B) ──
    {"line_number": "19", "description": "70% revenue (Item 10 x .70) — margin branch 1 of 4, floored at zero", "line_type": "calculated", "calculation": "R-TX-MARGIN", "source_rules": ["R-TX-MARGIN"], "sort_order": 29},
    {"line_number": "20", "description": "Revenue less COGS (Item 10 - item 14) — margin branch 2 of 4, floored at zero", "line_type": "calculated", "calculation": "R-TX-MARGIN", "source_rules": ["R-TX-MARGIN"], "sort_order": 30},
    {"line_number": "21", "description": "Revenue less compensation (Item 10 - item 18) — margin branch 3 of 4, floored at zero", "line_type": "calculated", "calculation": "R-TX-MARGIN", "source_rules": ["R-TX-MARGIN"], "sort_order": 31},
    {"line_number": "22", "description": "Revenue less $1 million (Item 10 - $1,000,000) — ⚠ margin branch 4 of 4; the branch the three-way shorthand DROPS", "line_type": "calculated", "calculation": "R-TX-MARGIN", "source_rules": ["R-TX-MARGIN"], "sort_order": 32},
    {"line_number": "23", "description": "MARGIN (Enter the lowest of items 19, 20, 21, or 22; if less than zero, enter 0)", "line_type": "subtotal", "source_rules": ["R-TX-MARGIN"], "sort_order": 33},

    # ── APPORTIONMENT Items 24-26 ──
    {"line_number": "24", "description": "Gross receipts in Texas (Rule 3.591 sourcing) — DIRECT-ENTRY", "line_type": "input", "source_facts": ["texas_gross_receipts_item24"], "sort_order": 34},
    {"line_number": "25", "description": "Gross receipts everywhere — DIRECT-ENTRY", "line_type": "input", "source_facts": ["everywhere_gross_receipts_item25"], "sort_order": 35},
    {"line_number": "26", "description": "APPORTIONMENT FACTOR (Divide item 24 by item 25, round to 4 decimal places)", "line_type": "calculated", "calculation": "R-TX-APPORT", "source_rules": ["R-TX-APPORT"], "sort_order": 36},

    # ── TAXABLE MARGIN Items 27-29 ──
    {"line_number": "27", "description": "Apportioned margin (Multiply item 23 by item 26)", "line_type": "calculated", "calculation": "R-TX-TAXMARGIN", "source_rules": ["R-TX-TAXMARGIN"], "sort_order": 37},
    {"line_number": "28", "description": "Allowable deductions — solar / clean coal / relocation (first annual report only); DIRECT-ENTRY", "line_type": "input", "source_facts": ["allowable_deductions_item28"], "sort_order": 38},
    {"line_number": "29", "description": "TAXABLE MARGIN (Item 27 minus item 28)", "line_type": "subtotal", "source_rules": ["R-TX-TAXMARGIN"], "sort_order": 39},

    # ── TAX DUE Items 30-35 ──
    {"line_number": "30", "description": "Tax rate — 0.0075 standard / 0.00375 qualifying retail-wholesale; ⚠ SIC-driven, blank => 0.0075", "line_type": "calculated", "calculation": "R-TX-RATE", "source_rules": ["R-TX-RATE"], "sort_order": 40},
    {"line_number": "31", "description": "Tax due (Multiply item 29 by the tax rate in item 30) — dollars and cents", "line_type": "calculated", "calculation": "R-TX-TAXDUE", "source_rules": ["R-TX-TAXDUE"], "sort_order": 41},
    {"line_number": "32", "description": "Tax credits (Item 17 from Form 05-181) — DIRECT-ENTRY, RED-DEFER R4", "line_type": "input", "source_facts": ["tax_credits_item32"], "sort_order": 42},
    {"line_number": "33", "description": "Tax due before discount (Item 31 minus item 32; if less than zero, enter zero)", "line_type": "calculated", "calculation": "R-TX-TAXDUE", "source_rules": ["R-TX-TAXDUE"], "sort_order": 43},
    {"line_number": "34", "description": "Discount — ⚠ STRUCTURALLY ALWAYS ZERO ('Discounts do not apply to reports due after Dec. 31, 2009')", "line_type": "calculated", "calculation": "R-TX-TAXDUE", "source_rules": ["R-TX-TAXDUE"], "sort_order": 44},
    {"line_number": "35", "description": "TOTAL TAX DUE (Item 33 minus item 34) — must equal Item 33", "line_type": "total", "source_rules": ["R-TX-TAXDUE", "R-TX-NOPAY"], "sort_order": 45,
     "notes": "Footer: 'Do not include payment if item 35 is less than $1,000 or if annualized total revenue is less than or equal to the no tax due threshold... If the entity makes a tiered partnership election, ANY amount in item 35 is due.'"},

    # ── EZ RENDER TARGET (05-169). EZ Items 1-10 == long-form Items 1-10;
    #    EZ Items 11-13 == long-form Items 24-26. Only 14-17 diverge. ──
    {"line_number": "EZ-11", "description": "EZ Item 11 Gross receipts in Texas (= long-form Item 24 rules + Rule 3.591)", "line_type": "input", "source_facts": ["texas_gross_receipts_item24"], "sort_order": 50},
    {"line_number": "EZ-12", "description": "EZ Item 12 Gross receipts everywhere (= long-form Item 25 rules + Rule 3.591)", "line_type": "input", "source_facts": ["everywhere_gross_receipts_item25"], "sort_order": 51},
    {"line_number": "EZ-13", "description": "EZ Item 13 Apportionment factor (= long-form Item 26 rules, 4 decimals)", "line_type": "calculated", "calculation": "R-TX-APPORT", "source_rules": ["R-TX-APPORT"], "sort_order": 52},
    {"line_number": "EZ-14", "description": "EZ Item 14 Apportioned revenue (Multiply item 10 by item 13) — dollars and cents", "line_type": "calculated", "calculation": "R-TX-EZ", "source_rules": ["R-TX-EZ"], "sort_order": 53},
    {"line_number": "EZ-15", "description": "EZ Item 15 Tax due before discount (Multiply item 14 by 0.00331) — dollars and cents", "line_type": "calculated", "calculation": "R-TX-EZ", "source_rules": ["R-TX-EZ"], "sort_order": 54},
    {"line_number": "EZ-16", "description": "EZ Item 16 Discount — always zero", "line_type": "calculated", "calculation": "R-TX-EZ", "source_rules": ["R-TX-EZ"], "sort_order": 55},
    {"line_number": "EZ-17", "description": "EZ Item 17 TOTAL TAX DUE (item 15 minus item 16)", "line_type": "total", "source_rules": ["R-TX-EZ", "R-TX-NOPAY"], "sort_order": 56,
     "notes": "⚠ Correction C7: the 05-169 form face says only 'less than' the threshold where 05-158-B, 05-915 and the statute say 'less than OR EQUAL TO'. 05-915 and the statute govern."},
    {"line_number": "EZ-COMPARE", "description": "Both-paths comparison (long form vs EZ) — surfaced as a RECOMMENDATION, never a silent default", "line_type": "informational", "source_rules": ["R-TX-EZCOMPARE"], "sort_order": 57},
]

TX158_DIAGNOSTICS: list[dict] = [
    # ── The year mapping ──
    {"diagnostic_id": "D_TX_YEAR_MAPPING", "title": "⚠ Delvio TY2025 = the TEXAS 2026 report, due 05/15/2026", "severity": "warning",
     "condition": "any Texas franchise report is prepared", "message": "Texas labels reports by REPORT YEAR = the calendar year the report is DUE, based on the accounting period ending in the PRIOR calendar year. Delvio TY2025 produces the TEXAS 2026 ANNUAL REPORT, due 05/15/2026, for an accounting period ENDING IN CALENDAR 2025. A document labelled '2025 Texas report' is TY2024 and is the WRONG source. Verify the preprinted report year on the form face reads 2026.",
     "notes": "The single easiest thing in the campaign to get backwards."},

    # ── Gate outcomes ──
    {"diagnostic_id": "D_TX_NOT_TAXABLE_ENTITY", "title": "Not a taxable entity — NOTHING is filed", "severity": "info",
     "condition": "is_taxable_entity is false", "message": "This entity is not a taxable entity under Tex. Tax Code §171.0002 (e.g. a sole proprietorship other than a single-member LLC, or a general partnership whose direct ownership is entirely natural persons and which is not an LLP). No franchise tax report, no Public Information Report and no Ownership Information Report is due.",
     "notes": "Gate outcome (A). The GP carve-out is narrow: one entity partner, or LLP registration, destroys it."},
    {"diagnostic_id": "D_TX_NO_NEXUS", "title": "No Texas nexus — NOTHING is filed", "severity": "info",
     "condition": "not organized in Texas and no physical presence and Texas receipts < $500,000 for the accounting period", "message": "34 TAC §3.586: economic nexus requires $500,000 or more of Texas gross receipts 'for each federal income tax accounting period ending in 2019 or later'. The test is keyed to the ENTITY'S ACCOUNTING PERIOD, not the report due date, and nexus begins on the FIRST DAY of that period, not the day the threshold was crossed. Below it, and not organized in Texas, nothing is filed at all.",
     "notes": "Gate outcome (A). The cheapest filter in the module."},
    {"diagnostic_id": "D_TX_DISREGARDED_ENTITY", "title": "⚠ Federal disregarded status is IRRELEVANT to Texas", "severity": "warning",
     "condition": "entity is disregarded for federal income tax purposes", "message": "Verbatim 05-915: 'An entity's treatment for federal income tax purposes does not determine its responsibility for Texas franchise tax. Therefore, partnerships, LLCs and other entities that are disregarded for federal income tax purposes are considered separate legal entities for franchise tax reporting purposes.' A federally disregarded single-member LLC files its OWN Texas report AND its own PIR or OIR. This is the #1 practical trap in the Texas module.",
     "notes": "Prevents the most common Texas filing miss for small-firm client bases."},
    {"diagnostic_id": "D_TX_VETERAN_OWNED", "title": "New veteran-owned business — no report and no PIR/OIR", "severity": "info",
     "condition": "qualifying new veteran-owned business within the initial five-year period", "message": "A pre-qualified new veteran-owned business (formed in Texas on/after 1/1/2016 and before 1/1/2020, or on/after 1/1/2022; 100% owned by honorably discharged veterans; Texas Veterans Commission letter on file) files nothing for the initial five-year period: 'A new veteran-owned business is not required to file a Public Information Report (Form 05-102) or Ownership Information Report (Form 05-167) for that same period.' It cannot be in a combined group or a tiered partnership arrangement during the period.",
     "notes": "Gate outcome (A); PIR/OIR carve-out 3."},
    {"diagnostic_id": "D_TX_PASSIVE_REIT_STUB", "title": "Passive entity / REIT — STUB report only", "severity": "warning",
     "condition": "is_passive_entity or is_qualifying_reit", "message": "File Form 05-158 (or 05-169) with the Passive and/or REIT circle blackened and complete 'the Taxpayer Information part of this form only' — accounting period dates and signature. No revenue lines, no margin, no tax. ⚠ A PASSIVE ENTITY FILES NO PIR AND NO OIR. A REIT, by contrast, 'must file either a Public Information Report (Form 05-102) or an Ownership Information Report (Form 05-167).' Passive test (§171.0003): at least 90% of federal gross income from the closed passive list — and 'passive income does not include rent.' Corporations and LLCs can NEVER be passive entities.",
     "notes": "Gate outcome (B); PIR/OIR carve-out 2."},
    {"diagnostic_id": "D_TX_NTD_THRESHOLD_INFO_ONLY", "title": "⚠ At or below $2,650,000 — PIR or OIR ONLY, NO franchise report", "severity": "warning",
     "condition": "annualized total revenue <= $2,650,000 and no tiered partnership election", "message": "Verbatim 05-915 Item 10: 'If the annualized total revenue is less than or equal to $2,650,000, and the entity is not an upper or lower tier entity making the tiered partnership election, STOP HERE, YOU ARE NOT REQUIRED TO FILE A FRANCHISE TAX REPORT. However, you are required to file a Public Information Report (Form 05-102) or Ownership Information Report (Form 05-167).' No long form, no EZ, no no-tax-due report. The correct product output is an INFORMATION REPORT ONLY. Threshold is biennial (§171.006(b)) and is fixed for reports due on/after 1/1/2026 and before 1/1/2028.",
     "notes": "Gate outcome (C) — the most common outcome for a small-firm Texas client base."},
    {"diagnostic_id": "D_TX_NO_TAX_DUE_REPORT_GONE", "title": "⚠ Form 05-163 does not exist for 2026", "severity": "warning",
     "condition": "a 'no tax due report' is expected from prior-year practice", "message": "The Comptroller's 2026 forms page states outright: 'The No Tax Due Report is not available for 2026 reports.' Form 05-163 is absent from both the 2026 forms index and the 05-915 Index of Forms. Do not attempt to produce one, and do not port prior-year logic that emits it. A below-threshold entity's only Texas output is a PIR or an OIR.",
     "notes": "Also gone: 05-160, replaced by 05-181 Credits Summary Schedule."},
    {"diagnostic_id": "D_TX_ZERO_TEXAS_RECEIPTS", "title": "Zero Texas gross receipts — factor 0, but the report is STILL FILED", "severity": "warning",
     "condition": "Item 24 is zero and annualized total revenue exceeds the threshold", "message": "A zero apportionment factor means no tax is due, but the entity 'must file a Long Form Report (Form 05-158) or, if qualified, the EZ Computation Report (Form 05-169) to report total revenue, Texas gross receipts and gross receipts everywhere,' AND 'must also file a Public Information Report (Form 05-102) or an Ownership Information Report (Form 05-167).' ⚠ This is outcome (E) or (D) with a zero factor — it is NOT the below-threshold outcome (C).",
     "notes": "Side branch. Confusing this with outcome (C) suppresses a required franchise report."},
    {"diagnostic_id": "D_TX_FIRST_ANNUAL_ZERO", "title": "First annual report may be a ZERO report — PIR/OIR still required", "severity": "info",
     "condition": "first annual report and the entity became subject during 2025 with an earlier federal year end", "message": "Where an entity became subject during 2025 with a federal year end BEFORE that date, the begin date equals the end date equals the date it became subject, producing a zero report. 'However, entities are still required to file a Public Information Report (Form 05-102) or an Ownership Information Report (Form 05-167).' The first annual report is also the ONLY report on which the §171.109(b) relocation deduction may be claimed (Rule 3.584(c)(2)).",
     "notes": "Side branch."},

    # ── PIR / OIR ──
    {"diagnostic_id": "D_TX_PIROIR_ROUTING", "title": "⚠ PIR vs OIR — an LLP is NOT an 'LP'", "severity": "warning",
     "condition": "an information report is routed", "message": "PIR (05-102) is filed by each CORPORATION, LLC, LIMITED PARTNERSHIP, PROFESSIONAL ASSOCIATION and FINANCIAL INSTITUTION. OIR (05-167) is filed by 'each taxable entity OTHER THAN' those — general partnerships, LIMITED LIABILITY PARTNERSHIPS, trusts, joint ventures, business associations and other legal entities. ⚠ An LLP is not on the PIR list and therefore files the OIR. Trusts 'should report their trustee information and not check any box.'",
     "notes": "The routing question is also asked on the 05-158-A form face."},
    {"diagnostic_id": "D_TX_PIROIR_FORFEITURE", "title": "⚠ PIR/OIR carries forfeiture exposure INDEPENDENT of the tax", "severity": "warning",
     "condition": "a PIR or OIR is required", "message": "Verbatim: 'Even if the franchise tax report is filed and all taxes paid, the right to transact business may be forfeited for failure to file the completed and signed PIR' — with officers and directors (PIR) or partners, members and owners (OIR) PERSONALLY LIABLE for certain debts (Tex. Tax Code §§171.251, 171.252, 171.255). The signature is a forfeiture-bearing requirement, not a formality. Forfeiture does not apply to financial institutions (§§171.259, 171.260). Both reports are due on the date the franchise tax report is due.",
     "notes": "This is why outcome (C) is a real deliverable, not a nicety."},

    # ── W6 — the federal handoff ──
    {"diagnostic_id": "D_TX_FED_LINE_MAP", "title": "⚠⚠ BLOCKING — the federal line map must be re-verified against the 2025 federal forms", "severity": "error",
     "condition": "any Items 1-7 or Item 9 bad-debt / Schedule C DRD amount is sourced from a federal return", "message": "Form 05-915 (Rev. 4-26/2) states verbatim: 'The line items indicated in this section refer to specific lines from the 2024 Internal Revenue Service (IRS) forms, which are the most current available at the time of publication.' But the 2026 Texas report is built on an accounting period ending in calendar 2025 — a 2025 federal return. THIS SPEC DELIBERATELY ENCODES NO FEDERAL LINE NUMBERS. Before the app build, reconcile the ~30-cell map line by line against the FINAL 2025 forms 1120, 1120S, 1065, 1041, Schedules C/E/F, 8825, 4797 and Schedule D. The booklet also warns 'federal line numbers are subject to change throughout the year,' and the statute pins the map to 2006-form EQUIVALENTS, so the map is a per-report-year DATA TABLE that must be re-verified every year.",
     "notes": "W6 / [UNVERIFIED] U2. The §4 map is the module's spine; if any line moved, it ships wrong."},

    # ── Revenue-side traps ──
    {"diagnostic_id": "D_TX_ITEM3_NONNEGATIVE", "title": "Item 3 Interest must be zero or greater", "severity": "error",
     "condition": "Item 3 is negative", "message": "Verbatim: 'The amount reported must be zero or greater. We do not allow a negative amount on Item 3.' Items 4 (Rents), 6 (Gains/losses) and 7 (Other income) MAY be negative per the form face; Item 3 may not.",
     "notes": "Form-face sign rule."},
    {"diagnostic_id": "D_TX_RENTAL_K1_INTERLOCK", "title": "⚠ K-1 net rental income belongs in Item 7, not Item 4 — and also in Item 9", "severity": "warning",
     "condition": "the entity holds a partnership or S corporation K-1 reporting net rental income (loss)", "message": "Verbatim: 'Do not include in Item 4 net rental income (loss) passed through from a partnership or S corporation on IRS Form K-1; report this amount in Item 7. This amount must also be included in Item 9 when subtracting net distributive income from a taxable entity treated as a partnership or as an S corporation for federal tax purposes.' A genuine three-item interlock (4 -> 7 -> 9), not a note.",
     "notes": "Getting this wrong overstates or understates total revenue in two places at once."},
    {"diagnostic_id": "D_TX_GILTI_NOT_EXCLUDABLE", "title": "⚠⚠ GILTI / §78 / §§951-964 amounts are INCLUDIBLE and NOT excludable", "severity": "error",
     "condition": "the entity has foreign income and a foreign-dividend or foreign-royalty exclusion is claimed on Item 9", "message": "Texas §171.1011's references to IRC §78 and §§951-964 are STILL PINNED TO THE 2007 IRC. GILTI and FDII (OBBBA-renamed NCTI and FDDEI) are therefore INCLUDIBLE in total revenue and MAY NOT BE SUBTRACTED — not as foreign dividends or royalties, not as §78 / §§951-964 amounts, and not as Schedule C deductions. They are also excluded from Texas gross receipts and gross receipts everywhere (Item 24: 'income excluded because of IRC Sections 78 or 951-964'). This is the one exclusion an experienced preparer will get wrong, and it is a real TY2025 rule for C-corp clients with foreign income.",
     "notes": "The 2026 IRC reinterpretation moved most amounts to current federal law but expressly NOT where the statute or rule cites the Code."},

    # ── COGS ──
    {"diagnostic_id": "D_TX_COGS_DIRECT_ENTRY", "title": "⚠ Item 11 COGS is a from-scratch Texas figure — never a federal pull", "severity": "warning",
     "condition": "Item 11 is non-zero", "message": "Verbatim 05-915: 'Generally COGS for Texas franchise tax reporting purposes will not equal the amount used for federal income tax reporting purposes or for financial accounting purposes. Typically, this amount CANNOT BE FOUND ON A FEDERAL INCOME TAX REPORT or on an income statement. It is a calculated amount specific to Texas franchise tax.' Delvio v1 does not compute it — build the qualifying-cost schedule manually from the §171.1012 inclusion list and the closed exclusion list (officers' compensation, selling costs, distribution and outbound transportation, advertising, idle facility, rehandling, bidding, interest, income taxes, strike expenses, federal military-housing operating costs).",
     "notes": "W3 direct-entry decision."},
    {"diagnostic_id": "D_TX_COGS_SERVICE_ENTITY", "title": "Service entity claiming COGS — confirm the eligibility gate", "severity": "warning",
     "condition": "Item 11 is non-zero and the entity's activity is service-based, or cogs_eligibility_affirmed is false", "message": "'A taxable entity has eligible COGS ONLY IF the taxable entity sells real or tangible personal property in the ordinary course of business OR if the taxable entity has qualifying COGS under any one of the exceptions noted in Texas Tax Code Section 171.1012 or Rule 3.588.' And: 'Generally, a taxable entity in the service industry does not have qualifying COGS.' The entity must also OWN the goods. For mixed transactions, 'the labor costs related to the services performed are not eligible COGS.' Confirm eligibility before subtracting anything on Item 11. Note that a service entity with no COGS computes Item 20 as Item 10, which then cannot win the four-way minimum.",
     "notes": "Prevents a fabricated COGS branch."},
    {"diagnostic_id": "D_TX_OVERHEAD_4PCT_CAP", "title": "Item 12 is capped at 4% of total indirect/administrative overhead", "severity": "info",
     "condition": "Item 12 is non-zero", "message": "Verbatim: 'This amount is limited to 4% of total indirect/administrative overhead costs.' Includes all mixed service costs — security, legal, data processing, accounting, personnel operations, general financial planning and financial management — that the entity can demonstrate are allocable to the acquisition or production of goods. Anything specifically EXCLUDED from COGS may not be routed through Item 12.",
     "notes": "The base is direct-entry; the cap is computed."},

    # ── Compensation ──
    {"diagnostic_id": "D_TX_COMP_CAP_ITEM15_ONLY", "title": "⚠⚠ The $480,000 cap applies to ITEM 15 ONLY — never to Item 16 benefits", "severity": "warning",
     "condition": "compensation is subtracted", "message": "Item 15 verbatim: wages and cash compensation are 'limited to $480,000 per person per 12-month period, prorated for the period upon which the tax is based.' Item 16 verbatim: 'The deduction for employee benefits is NOT LIMITED TO $480,000 PER PERSON but is only deductible to the extent deductible for federal income tax purposes.' Applying the cap to Item 16 is the single most-often-miscoded fact in this schedule. The cap is also PER PERSON, not per entity — capping an entity-level total once understates the deduction. Negative net distributive income is UNCAPPED: 'There is no cap or limitation on negative compensation.'",
     "notes": "$480,000 is biennial and TY-keyed: effective for reports due on/after 1/1/2026 and before 1/1/2028."},
    {"diagnostic_id": "D_TX_COMP_CAP_PRORATION", "title": "⚠ Short period — the $480,000 proration formula is UNVERIFIED", "severity": "warning",
     "condition": "the accounting period is not twelve months and Item 15 is non-zero", "message": "05-915 says the cap is 'prorated for the period upon which the tax is based' but gives NO FORMULA — the word 'prorat' appears exactly once in the 33-page booklet, in that sentence. It also states the cross-member version two different ways: 'upon which the REPORT is based' (Combined Group) vs 'upon which the TAX is based' (Item 15). 34 TAC §3.589 has not been read. ⚠ DO NOT ASSUME THE REVENUE-ANNUALIZATION 365-DAY CONVENTION CARRIES OVER. Enter the prorated cap factor manually until §3.589 is pulled.",
     "notes": "W7 / [UNVERIFIED] U3, widened by correction C6. Affects every short-period return."},

    # ── Margin ──
    {"diagnostic_id": "D_TX_MARGIN_FOUR_WAY", "title": "⚠ Margin is the LOWEST OF FOUR — the $1 million branch is real", "severity": "info",
     "condition": "margin is computed", "message": "Item 23: 'Enter the lowest amount from Items 19, 20, 21, or 22.' The four branches are 70% of revenue, revenue less COGS, revenue less compensation, and REVENUE LESS $1,000,000 — each floored at zero BEFORE the minimum. The common industry shorthand 'revenue minus the greatest of COGS / compensation / 30% of revenue' is arithmetically equal for the first three but SILENTLY DROPS the $1,000,000 branch, which is frequently the best answer for a small, labor-light service entity with no COGS (it beats the 70% branch whenever revenue is under $3,333,333). Every branch is available to every filer; only the COGS branch requires qualifying COGS.",
     "notes": "Confirmed three ways: the 05-158-B form face, the 05-915 Margin narrative, and the Combined Group section."},

    # ── Rate ──
    {"diagnostic_id": "D_TX_SIC_RATE_DEFAULT", "title": "⚠ SIC blank — the rate DEFAULTS to 0.75%", "severity": "warning",
     "condition": "sic_code is blank", "message": "Verbatim: 'This field determines the tax rate. Completion of the field is optional; however, IF LEFT BLANK, THE TAX RATE DEFAULTS TO 0.75%.' The NAICS field alongside it is INFORMATIONAL ONLY and does not affect the rate. If the entity qualifies as a retailer or wholesaler, the SIC code must be entered to obtain the 0.375% rate.",
     "notes": "Encode the blank default explicitly — do not treat a blank SIC as 'unknown' and stall."},
    {"diagnostic_id": "D_TX_RETAIL_RATE_DENIED", "title": "⚠ Retail/wholesale rate — all three conditions must hold or 0.375% is DENIED", "severity": "warning",
     "condition": "a retail/wholesale SIC code is entered but the three-condition test is not affirmed", "message": "'If the SIC code on Form 05-158-A does not fit the definition of qualifying retailers and wholesalers, the 0.375% tax rate WILL BE DENIED when the report is processed.' All three conditions must hold: (1) total revenue from retail/wholesale activities exceeds total revenue from all other trades; (2) except for eating and drinking places (SIC Major Group 58), LESS THAN 50% of the retail/wholesale revenue comes from products the entity or an affiliated-group member produces; (3) the entity does not provide retail or wholesale utilities, including telecommunications, electricity or gas. Retail = 1987 SIC Manual Division G (plus apparel rental in SIC 5999/7299, Industry Group 753, SIC 7359 tool/party/furniture rental, SIC 7353 heavy construction equipment, and Tex. Bus. & Com. Code ch. 92 rental-purchase); wholesale = Division F.",
     "notes": "Classification is by the 1987 SIC Manual, NOT by NAICS."},

    # ── EZ ──
    {"diagnostic_id": "D_TX_EZ_TRADEOFF", "title": "⚠ The EZ is often the WRONG answer — compute both paths", "severity": "warning",
     "condition": "ez_elected or annualized total revenue <= $20,000,000", "message": "The EZ taxes apportioned REVENUE at 0.331%, not margin. Break-even against the 0.75% long form is a margin of ~44.13% of revenue; the EZ is MORE EXPENSIVE for every entity below that — i.e. for exactly the COGS-heavy and labor-heavy entities that most often reach for it. Against the 0.375% retail/wholesale rate the break-even is ~88.27%, and since the four-way minimum caps margin at 70% of revenue, A QUALIFYING RETAILER OR WHOLESALER SHOULD NEVER ELECT THE EZ. The election also forfeits ALL credits and ALL margin deductions, and the current year's temporary credit for business loss carryforwards 'may not be used AND MAY NOT BE CARRIED OVER to a future period.' Compute both paths and recommend; never default silently.",
     "notes": "W8."},

    # ── Payment interaction ──
    {"diagnostic_id": "D_TX_UNDER_1000_NO_PAYMENT", "title": "Tax under $1,000 — no payment, but the FULL report is still required", "severity": "info",
     "condition": "Item 35 is greater than zero and strictly less than $1,000, with no tiered partnership election", "message": "Verbatim: 'an entity that calculates an amount of tax due that is less than $1,000 is not required to pay any tax.... The entity, however, MUST SUBMIT ALL REQUIRED REPORTS to satisfy its filing requirements.' And Item 35: 'If this amount is less than $1,000, you owe no tax, but you must submit this report along with the Public Information Report (Form 05-102) and/or the Ownership Information Report (Form 05-167).' ⚠ THIS IS NOT THE SAME AS THE THRESHOLD BRANCH: the threshold branch is tested on ANNUALIZED REVENUE BEFORE the computation and produces NO FRANCHISE REPORT AT ALL; this branch is tested on the COMPUTED TAX AFTER the whole report is computed and the report IS FILED IN FULL. The test is STRICTLY less than $1,000 — exactly $1,000 is payable. A tiered partnership election defeats BOTH branches.",
     "notes": "Conflating the two branches is the failure mode the verification passes flagged."},
    {"diagnostic_id": "D_TX_NO_MIN_NO_ESTIMATED", "title": "No minimum tax, no discount, no estimated payments", "severity": "info",
     "condition": "any franchise report is computed", "message": "'There is no minimum tax requirement under the franchise tax provisions' — a zero margin produces a zero tax, never a floor amount. 'Discounts do not apply to reports due after Dec. 31, 2009', so Item 34 is structurally always zero and Item 35 always equals Item 33. 'Texas law does not require the filing of estimated tax reports or payments' — there is no quarterly obligation and no estimate-based penalty. There is also no net-worth or capital-stock franchise tax; Texas repealed that when the margin tax replaced it in 2008.",
     "notes": "Four rules that are easy to state wrongly."},

    # ── Apportionment sourcing ──
    {"diagnostic_id": "D_TX_RECEIPTS_SOURCING", "title": "Items 24/25 are a Rule 3.591 workpaper exercise", "severity": "warning",
     "condition": "Item 24 or Item 25 is entered", "message": "Delvio v1 does not source receipts. Rule 3.591 highlights: tangible personal property where delivered or shipped to a Texas purchaser; real property in Texas including mineral royalties; SERVICES WHERE PERFORMED; rentals of Texas-situated property; patents and copyrights used in Texas; computer software, intangibles and securities sourced to the LEGAL DOMICILE OF THE PAYOR; securities sold through an exchange where the buyer cannot be identified — 8.7% of the revenue is a Texas receipt; membership and enrollment fees by payor domicile; loan-servicing receipts by the location of the secured real property; internet hosting sourced to the CUSTOMER'S location. There is NO throwback and NO throwout rule. Amounts excluded from total revenue (including IRC §78 / §§951-964 income) are excluded from both numerator and denominator.",
     "notes": "[UNVERIFIED] U7 — the operative §3.591(e)-(f) text was read only in 05-915 summary form."},

    # ── W1 — the escalated judgement call ──
    {"diagnostic_id": "D_TX_BONUS_DATE_GATE", "title": "⚠⚠ ESCALATED — the ASSET-LEVEL bonus date gate is an OPEN Ken judgement call", "severity": "error",
     "condition": "federal bonus depreciation is included in Item 11 COGS", "message": "DELVIO DOES NOT PICK A DATE KEY HERE, AND THIS SPEC ENCODES NONE. The REPORT-YEAR gate is NOT in dispute — all four official sources agree the change begins with the 2026 franchise tax report. What IS disputed is whether an INDIVIDUAL ASSET carries a placed-in-service or acquisition date test: STAR memo 202603002M (3/12/2026, controlling) says bonus is includable for assets 'placed in service on or after January 19, 2025'; the Comptroller's 12/1/2025 news release says assets 'acquired after Jan. 19, 2025'; adopted Rule 3.588 (eff. 6/21/2026) imposes NO asset-level date gate; and the FINAL 2026 instructions (05-915 Rev. 4-26/2, published AFTER the memo) contain no asset-level date gate either — zero occurrences of 'January 19', 'Jan. 19' or '19, 2025' in 33 pages. This is not academic: federal OBBBA keys 100% bonus to ACQUISITION after 1/19/2025 with 40% for property acquired earlier, so an asset acquired in Dec 2024 and placed in service in Aug 2025 passes the news release's test, FAILS the memo's test, and is unaddressed by the rule and the instructions. Determine the entity's federal bonus by asset manually and confirm the Texas scope with Ken before relying on any COGS depreciation figure.",
     "notes": "W1 / [UNVERIFIED] U1 / GATE1_WALK.md item 4. Brief's recommendation: build to PLACED IN SERVICE on/after 1/19/2025 per the controlling memo, FLAGGED and recorded as a DECISION not a finding, and email the Comptroller. Cannot be guessed (Authoritative-Source Rule)."},
    {"diagnostic_id": "D_TX_NO_TX_179_CAP", "title": "No Texas §179 dollar cap exists for the 2026 report", "severity": "warning",
     "condition": "a federal §179 election flows into Item 11 COGS", "message": "Adopted Rule 3.588 (eff. 6/21/2026) DELETES the rule's reference to 'Internal Revenue Code, §179 (Election to expense certain depreciable assets)' — the sole source of the old $25,000 / $200,000 Texas cap — because 'Chapter 171 does not specifically reference §179'. Encode THE FEDERAL AMOUNT AS CLAIMED: not a hardcoded Texas cap, and not a literal 'unlimited' (it remains constrained by the federal limit and by §171.1012(c)(6) qualification). ⚠ The obvious txrules.elaws.us mirror still serves the STALE pre-amendment text that retains the deleted §179 reference — verify against the Texas Register adoption document, not the mirror, or a re-verification pass will reinstate the dead $25,000 cap.",
     "notes": "Correction C4 / [UNVERIFIED] U6. For 2025-report years and earlier the old regime still applies to amended reports."},

    # ── E-file ──
    {"diagnostic_id": "D_TX_EFILE_NOT_IN_V1", "title": "Texas e-file is NOT in v1 — Comptroller approval is a hard gate", "severity": "warning",
     "condition": "an electronic Texas franchise filing is attempted", "message": "Texas runs its OWN standalone Franchise Tax Web Service, separate from IRS MeF: the developer must register as a Transmitter, obtain the 2026 Web Services Developer Guide and System Integration Manual, and 'Completed software must be tested and approved by the Comptroller's office before an official public release.' The printable/2D-barcode track is approved SEPARATELY and requires the exact version strings 'TX2026' and 'Ver. 17.0'. v1 produces prepared and printed reports only; below-threshold clients can file their PIR/OIR through the Comptroller's own Webfile in the meantime.",
     "notes": "W9 / [UNVERIFIED] U9 — no published calendar exists. Ken-only, lead-time-bearing. Contact XMLBusiness@cpa.texas.gov."},

    # ══════════════════════════════════════════════════════════════════════
    # RED-DEFERS R1-R10 — each its own "prepare manually" diagnostic
    # ══════════════════════════════════════════════════════════════════════
    {"diagnostic_id": "D_TX_DEPR_CATCHUP", "title": "R1 ⚠ One-time 2026 net depreciation adjustment — PREPARE MANUALLY", "severity": "error",
     "condition": "the entity has qualifying assets placed in service before the 2026 accounting year begin date and not disposed of before that date", "message": "This entity may qualify for the ONE-TIME 2026 Texas net depreciation adjustment. DELVIO DOES NOT COMPUTE IT. Prepare the per-asset federal-versus-Texas depreciation history manually and enter the result inside Item 11 (it has NO LINE OF ITS OWN). Four reasons it cannot be computed responsibly in v1: (1) the zero floor is PER ASSET — 'the net depreciation adjustment for THAT QUALIFYING ASSET ... cannot be less than zero' — so negative-net assets floor individually and do NOT offset positive-net assets; (2) the entity-level limiter is CIRCULAR — admitted only 'to the extent the adjustment does not take the taxable entity's MARGIN below zero', and adding it to COGS raises Item 14, lowers Item 20 and can change which of the four branches is the minimum, so it must be solved as 'the largest catch-up such that Item 23 >= 0'; (3) the carryforward runs 'to consecutive reports until exhausted' but has NO FORM FIELD ANYWHERE on any 2026 form and no 2027 form exists; (4) it needs a per-asset, per-year history of federal versus Texas-COGS depreciation from each asset's in-service date through the accounting-year-end date on the 2025 report — data Delvio does not hold for any client whose prior preparer was not Delvio. Also: no adjustment is allowed for IRC §197 recovery (determined under the 2007 IRC); ITC-reduced basis governs; and the adjustment is prospective only and cannot be claimed by amending prior years.",
     "notes": "R1 / W4. Confirmed and DOUBLE-SOURCED — the per-asset framing is in adopted Rule 3.588(B) itself, not merely in the instructions. The largest single data requirement in the Texas module, and it exists in no other state's spec."},
    {"diagnostic_id": "D_TX_COMBINED", "title": "R2 ⚠ Combined reporting is MANDATORY — prepare the combined report manually", "severity": "error",
     "condition": "the entity is a member of an affiliated group engaged in a unitary business", "message": "COMBINED REPORTING IS MANDATORY for taxable entities that meet the ownership and unitary criteria — a separate-entity report for a unitary group is a WRONG RETURN, not an incomplete one. Delvio v1 prepares separate-entity reports only. Prepare the combined report manually, including Form 05-166 Affiliate Schedule and Form 05-177 Common Owner Information Report. Rules v1 does not model: all members are included even if individually at or below $2,650,000; per-member total revenue is computed as if separate and WITHOUT REGARD to the threshold, then summed, then intercompany revenue is eliminated on Item 9; combined COGS and compensation net out intercompany payments only to the extent the corresponding revenue was subtracted; the $1 million margin deduction is $1,000,000 FOR THE GROUP, not per member; 'A combined group may choose only one method for computing margin that applies to all members'; the compensation cap is per person ACROSS the group; the rate is determined from GROUP total revenue; Texas receipts count only members organized in Texas or with Texas nexus while everywhere-receipts count all members; and the drop-shipment rule sources TPP delivered to a Texas purchaser to Texas even where the selling member lacks nexus. A below-threshold group files no report, Affiliate Schedule or Common Owner Report — but each member organized in Texas or with Texas nexus must still file a PIR or OIR.",
     "notes": "R2 / W5. The diagnostic is deliberately LOUD."},
    {"diagnostic_id": "D_TX_TIERED", "title": "R3 ⚠ Tiered partnership election changes the no-tax rules for BOTH tiers", "severity": "error",
     "condition": "a tiered partnership arrangement with a Form 05-175 election", "message": "Delvio v1 does not model the tiered partnership election. ⚠ THE ELECTION SWITCHES OFF BOTH NO-TAX RULES, printed on the face of both 05-158-B and 05-169: 'Both the upper and lower tier entities owe any amount of tax that is calculated as due even if the amount is less than $1,000 or annualized total revenue after the tiered partnership election is $2,650,000 or less.' Other unmodelled rules: the election is NOT allowed if the lower tier entity, before passing total revenue, has $2,650,000 or less in annualized total revenue OR owes less than $1,000; it is not allowed if the lower tier is in a combined group; revenue passes but MARGIN DEDUCTIONS DO NOT ('COGS, compensation, 30% of revenue or $1 million may not be passed to upper tier entities'); the lower tier reports the passed amount on Item 9 and the upper tier on Item 7; revenue may pass only to upper tier entities subject to Texas franchise tax and only by ownership percentage; both tiers blacken the tiered-partnership circle; all involved entities file a franchise report, a PIR/OIR and Form 05-175; and EZ eligibility for either tier is tested on the LOWER tier's pre-pass annualized revenue.",
     "notes": "R3 / W5."},
    {"diagnostic_id": "D_TX_CREDITS", "title": "R4 Franchise tax credits — prepare Form 05-181 manually", "severity": "error",
     "condition": "the entity claims any Texas franchise tax credit", "message": "Delvio v1 does not compute Texas franchise tax credits. Prepare Form 05-181 Credits Summary Schedule (new for 2026, replacing 05-160) manually and enter its Item 17 on Item 32 — 05-181 caps total credits at its own Item 1 (tax due before credits). Supporting schedules: 05-180 Historic Structure Credit Supplement, 05-182 Subchapter T R&D Activities Credits Schedule (new; the Subchapter M R&D credit was repealed by S.B. 2206, 89th Leg., with carryforwards running to the earlier of expiration or Dec. 31, 2045), and 05-185 Housing Development Credit Supplement. ⚠ Electing the EZ computation FORFEITS ALL CREDITS for the report year and permanently destroys the current year's temporary-credit-for-business-loss-carryforwards portion.",
     "notes": "R4. Correction C5: 05-186 and 05-916 are NOT 2026 franchise forms — four schedules, not six."},
    {"diagnostic_id": "D_TX_FINAL", "title": "R5 Final report — different due date, and NO PIR/OIR", "severity": "error",
     "condition": "the entity ceased doing business in Texas", "message": "Delvio v1 does not prepare Texas final reports. A final report is due 60 DAYS AFTER the entity ceases doing business in Texas, and 'A Public Information Report (Form 05-102) or an Ownership Information Report (Form 05-167) is NOT required to be filed with the final report.' The final form (05-158-f) shares Items 1-35 identically with the annual but differs in four places: it OMITS the PIR/OIR routing question, ADDS a 'Blacken circle to request a Certificate of Account Status' option, carries NO preprinted due date, and uses Tcodes 13270/13271 instead of 13250/13251. An entity at or below the threshold files no final report either, but 'will be asked to check a box to verify that they are under the no tax due threshold when requesting a certificate of account status.'",
     "notes": "R5. The computation is shared; the filing rules and the render target are not."},
    {"diagnostic_id": "D_TX_EXT", "title": "R6 Texas extension — prepare Form 05-164 manually", "severity": "error",
     "condition": "an extension of the Texas franchise tax report is requested", "message": "Delvio v1 does not model the Texas extension. The non-EFT annual extension runs to NOV. 16, 2026 and requires payment of 90% of the current year's tax OR 100% of the prior calendar year's reported tax — the 100% option is unavailable to a first-annual filer or to an entity that was an affiliate on a 2025 combined report. Prepare Form 05-164 (and 05-165 Extension Affiliate List for a combined group) manually. Note: an at-or-below-threshold entity that cannot file its PIR or OIR by May 15 'may request an extension to file its report by filing a ZERO MONEY EXTENSION REQUEST' — the extension mechanism serves information-report-only filers too.",
     "notes": "R6."},
    {"diagnostic_id": "D_TX_TRUST", "title": "R7 Trust taxability is not modelled — confirm manually", "severity": "error",
     "condition": "the client is a trust or estate", "message": "Delvio v1 does not model trust taxability under Tex. Tax Code §171.0002(c) and 34 TAC §3.581. Most fiduciary clients are OUT OF SCOPE for the Texas franchise tax: grantor trusts, estates of natural persons and escrows are excluded, as are trusts qualified under IRC §401(a) or exempt under §501(c)(9); a trust may also separately qualify as a PASSIVE ENTITY. BUSINESS trusts are taxable entities and file the OIR ('Trusts should report their trustee information and not check any box'). NEW for 2026 (S.J.R. 18, 89th Leg.): 'Trusts no longer include realized or unrealized capital gains or the sale or transfer of a capital asset in total revenue' — which overrides the Item 6 pull for a trust filer. Confirm taxable status manually.",
     "notes": "R7 / [UNVERIFIED] U8 — Rule 3.581's operative text is unread. Low urgency: fiduciary is the on-demand lane."},
    {"diagnostic_id": "D_TX_SPECIAL_APPT", "title": "R8 §171.106 special apportionment is not modelled", "severity": "error",
     "condition": "the entity provides regulated investment company services or employee retirement plan services", "message": "Delvio v1 does not model the §171.106 special apportionment regimes for regulated investment company services and employee retirement plan services. Compute the apportionment factor for these receipts manually and enter Items 24 and 25 accordingly.",
     "notes": "R8. A known carve-out, out of scope for a first build."},
    {"diagnostic_id": "D_TX_SPECIAL_ENTITY", "title": "R9 PEO / management company / healthcare regimes are not modelled", "severity": "error",
     "condition": "the entity is a professional employer organization, a client of a PEO or temporary service, a management company, a managed entity, a health care provider or a health care institution", "message": "Delvio v1 does not model these special regimes, each of which rewrites Items 9, 15 and 16. A PEO may include only its OWN employees' wages; a client of a PEO or temporary service (Labor Code §93.001) may include amounts paid to the PEO for covered-employee wages (Item 15) and benefits (Item 16) but NOT the administrative fee, payroll taxes or 1099 amounts — Form 05-176 supplies the client's figures and 'should not be sent to the Comptroller's office but should be kept with the franchise tax report work papers.' A management company may not include amounts reimbursed by a managed entity; the MANAGED entity includes those reimbursements as if paid to its own employees. A health care provider may exclude 100% of Medicaid, Medicare, CHIP, workers' compensation and TRICARE revenue plus actual uncompensated-care cost — but a health care INSTITUTION only 50% (§171.1011(p)(2), cost computed under Rule 3.587(b)(1)). Prepare these manually.",
     "notes": "R9."},
    {"diagnostic_id": "D_TX_AMENDED", "title": "R10 Amended Texas reports are not modelled", "severity": "error",
     "condition": "an amended Texas franchise tax report is required", "message": "Delvio v1 does not prepare amended Texas franchise tax reports; the amendment mechanics were not researched for this spec and are not guessed. Prepare the amended report manually. ⚠ Note one interaction that IS known: the one-time net depreciation adjustment 'is intended to be prospective' and CANNOT be claimed by amending prior years. Note also that for 2025 report years and earlier, both §179 and bonus depreciation are based on the 2007 IRC (§179 capped at $25,000 with a $200,000 phase-out; federal bonus not allowed for Texas COGS) — do not apply the 2026 regime to an amended earlier-year report.",
     "notes": "R10. Explicitly unresearched and correctly deferred rather than guessed."},
]

TX158_SCENARIOS: list[dict] = [
    # ── The five filing outcomes ──
    {"scenario_name": "Gate (A) — general partnership of natural persons is not a taxable entity", "scenario_type": "edge", "sort_order": 1,
     "inputs": {"legal_form": "general_partnership", "is_taxable_entity": False, "organized_in_texas": True},
     "expected_outputs": {"filing_outcome": "A_NOTHING", "franchise_report": None, "info_report": None},
     "notes": "§171.0002(b)(2): a GP whose DIRECT ownership is composed entirely of natural persons with unlimited liability is not a taxable entity. Nothing at all — no report, no PIR, no OIR. One entity partner, or LLP registration, destroys the carve-out."},
    {"scenario_name": "Gate (A) — out-of-state LLC below the $500,000 economic nexus threshold", "scenario_type": "edge", "sort_order": 2,
     "inputs": {"legal_form": "llc", "is_taxable_entity": True, "organized_in_texas": False, "physical_presence_in_texas": False, "texas_receipts_this_accounting_period": 400000},
     "expected_outputs": {"has_nexus": False, "filing_outcome": "A_NOTHING", "info_report": None},
     "notes": "34 TAC §3.586: $400,000 < $500,000 for the accounting period, no physical presence, not organized in Texas -> nothing is filed."},
    {"scenario_name": "Economic nexus at exactly $500,000 — the entity is in", "scenario_type": "edge", "sort_order": 3,
     "inputs": {"legal_form": "llc", "is_taxable_entity": True, "organized_in_texas": False, "texas_receipts_this_accounting_period": 500000, "annualized_total_revenue": 5000000},
     "expected_outputs": {"has_nexus": True, "filing_outcome": "E_LONG", "info_report": "TX_05_102"},
     "notes": "The rule reads '$500,000 or more' — exactly $500,000 creates nexus."},
    {"scenario_name": "Gate (A) — new veteran-owned business files nothing, not even a PIR", "scenario_type": "edge", "sort_order": 4,
     "inputs": {"legal_form": "llc", "is_taxable_entity": True, "organized_in_texas": True, "is_new_veteran_owned": True, "annualized_total_revenue": 8000000},
     "expected_outputs": {"filing_outcome": "A_NOTHING", "franchise_report": None, "info_report": None},
     "notes": "PIR/OIR carve-out 3 — the veteran-owned exemption suppresses the information report too, even at $8M of revenue."},
    {"scenario_name": "Gate (B) — passive limited partnership files a stub and NO PIR/OIR", "scenario_type": "edge", "sort_order": 5,
     "inputs": {"legal_form": "limited_partnership", "is_taxable_entity": True, "organized_in_texas": True, "is_passive_entity": True, "annualized_total_revenue": 9000000},
     "expected_outputs": {"filing_outcome": "B_STUB", "franchise_report": "TX_05_158", "render_target": "05-158 (stub)", "info_report": None},
     "notes": "An LP would normally file the PIR, but PIR/OIR carve-out 2 suppresses it for a passive entity. Complete Taxpayer Information only."},
    {"scenario_name": "Gate (B) — REIT files a stub AND a PIR", "scenario_type": "edge", "sort_order": 6,
     "inputs": {"legal_form": "corporation", "is_taxable_entity": True, "organized_in_texas": True, "is_qualifying_reit": True, "annualized_total_revenue": 40000000},
     "expected_outputs": {"filing_outcome": "B_STUB", "franchise_report": "TX_05_158", "info_report": "TX_05_102"},
     "notes": "⚠ The REIT/passive asymmetry: 'Each REIT or qualified REIT subsidiary must file either a Public Information Report (Form 05-102) or an Ownership Information Report (Form 05-167).'"},
    {"scenario_name": "Gate (C) — at exactly $2,650,000, PIR ONLY and NO franchise report", "scenario_type": "edge", "sort_order": 7,
     "inputs": {"legal_form": "llc", "is_taxable_entity": True, "organized_in_texas": True, "annualized_total_revenue": 2650000},
     "expected_outputs": {"filing_outcome": "C_INFO_ONLY", "franchise_report": None, "render_target": None, "info_report": "TX_05_102"},
     "notes": "The test is 'less than OR EQUAL TO', so exactly $2,650,000 lands in outcome (C). Form 05-163 does not exist for 2026 — the ONLY output is the PIR."},
    {"scenario_name": "Gate (E) — one dollar over the threshold triggers the long form", "scenario_type": "edge", "sort_order": 8,
     "inputs": {"legal_form": "llc", "is_taxable_entity": True, "organized_in_texas": True, "annualized_total_revenue": 2650001},
     "expected_outputs": {"filing_outcome": "E_LONG", "franchise_report": "TX_05_158", "render_target": "05-158-A/B", "info_report": "TX_05_102"},
     "notes": "Boundary pair with the previous scenario."},

    # ── Annualization ──
    {"scenario_name": "Short period annualizes ABOVE the threshold", "scenario_type": "edge", "sort_order": 9,
     "inputs": {"Item10": 1500000, "days_in_accounting_period": 180},
     "expected_outputs": {"annualized_total_revenue": 3041666.67, "filing_outcome": "E_LONG"},
     "notes": "1,500,000 / 180 x 365 = 3,041,666.67 > 2,650,000, so a $1.5M short-period entity DOES file. ⚠ Item 10 itself stays 1,500,000 in the tax computation — 'The amount of total revenue used in the tax calculations does NOT change as a result of annualizing.'"},
    {"scenario_name": "Short period annualizes BELOW the threshold", "scenario_type": "edge", "sort_order": 10,
     "inputs": {"Item10": 1000000, "days_in_accounting_period": 180},
     "expected_outputs": {"annualized_total_revenue": 2027777.78, "filing_outcome": "C_INFO_ONLY", "franchise_report": None},
     "notes": "1,000,000 / 180 x 365 = 2,027,777.78 <= 2,650,000 -> PIR/OIR only."},

    # ── The four-way margin minimum ──
    {"scenario_name": "⚠ Margin — the revenue-less-$1,000,000 branch WINS (service entity)", "scenario_type": "normal", "sort_order": 11,
     "inputs": {"Item10": 3000000, "Item14": 0, "Item18": 400000},
     "expected_outputs": {"Item19": 2100000, "Item20": 3000000, "Item21": 2600000, "Item22": 2000000, "Item23": 2000000, "winning_branch": "22_million"},
     "notes": "THE BRANCH THE THREE-WAY SHORTHAND DROPS. A labor-light service entity with no COGS: 70% = 2,100,000; revenue-COGS = 3,000,000 (loses because COGS is zero); revenue-comp = 2,600,000; revenue-$1M = 2,000,000 WINS. A three-way 'greatest of' implementation would return 2,100,000 and OVERSTATE margin by $100,000."},
    {"scenario_name": "Margin — the COGS branch wins (manufacturer)", "scenario_type": "normal", "sort_order": 12,
     "inputs": {"Item10": 5000000, "Item14": 4200000, "Item18": 500000},
     "expected_outputs": {"Item19": 3500000, "Item20": 800000, "Item21": 4500000, "Item22": 4000000, "Item23": 800000, "winning_branch": "20_cogs"},
     "notes": "5,000,000 - 4,200,000 = 800,000 is the lowest of the four."},
    {"scenario_name": "Margin — the 70% branch wins (large, low-cost entity)", "scenario_type": "normal", "sort_order": 13,
     "inputs": {"Item10": 10000000, "Item14": 1000000, "Item18": 500000},
     "expected_outputs": {"Item19": 7000000, "Item20": 9000000, "Item21": 9500000, "Item22": 9000000, "Item23": 7000000, "winning_branch": "19_70pct"},
     "notes": "Above $3,333,333 of revenue the 70% branch beats the $1M branch, and here it beats both cost branches too."},
    {"scenario_name": "Margin — the compensation branch wins (labor-heavy entity)", "scenario_type": "normal", "sort_order": 14,
     "inputs": {"Item10": 4000000, "Item14": 0, "Item18": 3500000},
     "expected_outputs": {"Item19": 2800000, "Item20": 4000000, "Item21": 500000, "Item22": 3000000, "Item23": 500000, "winning_branch": "21_comp"},
     "notes": "4,000,000 - 3,500,000 = 500,000."},
    {"scenario_name": "Margin — each branch floors at zero BEFORE the minimum", "scenario_type": "edge", "sort_order": 15,
     "inputs": {"Item10": 1000000, "Item14": 1800000, "Item18": 1200000},
     "expected_outputs": {"Item19": 700000, "Item20": 0, "Item21": 0, "Item22": 0, "Item23": 0},
     "notes": "Revenue-COGS and revenue-comp are both negative and floor to zero individually; revenue-$1M is exactly zero. Margin is zero, and — since there is NO MINIMUM TAX — the tax is zero, not a floor amount."},

    # ── Compensation ──
    {"scenario_name": "⚠ $480,000 cap applies PER PERSON on Item 15 but NOT to Item 16 benefits", "scenario_type": "edge", "sort_order": 16,
     "inputs": {"comp_wages_person_roster": [600000, 600000, 600000], "comp_benefits_item16": 200000, "comp_item17_other": 0},
     "expected_outputs": {"Item15": 1440000, "Item16": 200000, "Item17": 0, "Item18": 1640000},
     "notes": "Three officers at $600,000 each: each is capped to $480,000 -> Item 15 = 1,440,000 (not the uncapped 1,800,000, and NOT an entity-level single cap of 480,000). Item 16 benefits pass through UNCAPPED at 200,000. Total compensation 1,640,000."},
    {"scenario_name": "Negative net distributive income is UNCAPPED in Item 15", "scenario_type": "edge", "sort_order": 17,
     "inputs": {"comp_wages_person_roster": [600000, -50000], "comp_benefits_item16": 0},
     "expected_outputs": {"Item15": 430000, "Item18": 430000},
     "notes": "min(600000, 480000) = 480,000; the negative NDI of -50,000 passes through in full — 'There is no cap or limitation on negative compensation.' 480,000 - 50,000 = 430,000."},

    # ── COGS ──
    {"scenario_name": "Item 12 is capped at 4% of the indirect/administrative overhead base", "scenario_type": "normal", "sort_order": 18,
     "inputs": {"cogs_item11_qualifying": 2000000, "indirect_admin_overhead_base": 500000, "cogs_item13_other": 0},
     "expected_outputs": {"Item11": 2000000, "Item12": 20000, "Item13": 0, "Item14": 2020000},
     "notes": "0.04 x 500,000 = 20,000. Item 11 is DIRECT-ENTRY and is never derived from a federal COGS figure."},

    # ── Rate selection ──
    {"scenario_name": "⚠ Blank SIC code defaults the rate to 0.75%", "scenario_type": "edge", "sort_order": 19,
     "inputs": {"sic_code": "", "naics_code": "541211", "retail_wholesale_qualified": False},
     "expected_outputs": {"Item30": "0.0075"},
     "notes": "'Completion of the field is optional; however, if left blank, the tax rate defaults to 0.75%.' The NAICS code alongside it is informational and does not affect the rate."},
    {"scenario_name": "Qualifying retailer with an affirmed SIC gets 0.375%", "scenario_type": "normal", "sort_order": 20,
     "inputs": {"sic_code": "5411", "retail_wholesale_qualified": True},
     "expected_outputs": {"Item30": "0.00375"},
     "notes": "1987 SIC Division G with all three conditions affirmed. Without the affirmation the 0.375% rate 'will be denied when the report is processed.'"},

    # ── Apportionment ──
    {"scenario_name": "Apportionment — 4-decimal rounding, zero rule, and both 1.0000 rules", "scenario_type": "edge", "sort_order": 21,
     "inputs": {"cases": [[750000, 2000000], [0, 2000000], [900000, 900000], [1000000, 900000]]},
     "expected_outputs": {"factors": [0.375, 0.0, 1.0, 1.0]},
     "notes": "750,000/2,000,000 = 0.3750; Texas receipts zero -> 0.0000; equal and > 0 -> 1.0000; Texas MORE than everywhere and both > 0 -> 1.0000."},
    {"scenario_name": "Zero Texas receipts — no tax, but the long form is STILL filed", "scenario_type": "edge", "sort_order": 22,
     "inputs": {"legal_form": "llc", "annualized_total_revenue": 8000000, "Item23": 5600000, "texas_gross_receipts_item24": 0, "everywhere_gross_receipts_item25": 8000000},
     "expected_outputs": {"Item26": 0.0, "Item27": 0.0, "Item35": 0.0, "filing_outcome": "E_LONG", "info_report": "TX_05_102"},
     "notes": "⚠ Outcome (E) with a zero factor, NOT outcome (C). The entity must still report total revenue, Texas receipts and everywhere receipts, plus the PIR."},

    # ── Tax due / payment interaction ──
    {"scenario_name": "Long-form tax — the $1M margin branch carried through to Item 35", "scenario_type": "normal", "sort_order": 23,
     "inputs": {"Item23": 2000000, "Item26": 1.0, "allowable_deductions_item28": 0, "Item30": "0.0075", "tax_credits_item32": 0},
     "expected_outputs": {"Item27": 2000000, "Item29": 2000000, "Item31": 15000, "Item33": 15000, "Item34": 0, "Item35": 15000},
     "notes": "2,000,000 x 0.0075 = 15,000. Item 34 discount is structurally zero and Item 35 equals Item 33."},
    {"scenario_name": "⚠ Tax under $1,000 — no payment, but the report and the PIR are still required", "scenario_type": "edge", "sort_order": 24,
     "inputs": {"Item10": 3000000, "Item14": 0, "Item18": 2900000, "Item26": 1.0, "Item30": "0.0075", "annualized_total_revenue": 3000000, "tiered_partnership_election": False},
     "expected_outputs": {"Item23": 100000, "Item31": 750, "Item35": 750, "payment_required": False, "report_still_required": True, "info_report": "TX_05_102"},
     "notes": "Margin = min(2,100,000; 3,000,000; 100,000; 2,000,000) = 100,000; 100,000 x 0.0075 = 750 < 1,000 -> no payment. ⚠ The FULL report is still filed showing 750, plus the PIR. Contrast with outcome (C), where NO franchise report exists at all."},
    {"scenario_name": "Tax of exactly $1,000 IS payable (strictly-less-than test)", "scenario_type": "edge", "sort_order": 25,
     "inputs": {"Item35": 1000, "annualized_total_revenue": 5000000, "tiered_partnership_election": False},
     "expected_outputs": {"payment_required": True},
     "notes": "'less than $1,000' is STRICT — $1,000.00 exactly must be paid."},
    {"scenario_name": "Tiered partnership election defeats BOTH no-tax branches", "scenario_type": "edge", "sort_order": 26,
     "inputs": {"Item35": 400, "annualized_total_revenue": 2000000, "tiered_partnership_election": True},
     "expected_outputs": {"payment_required": True, "filing_outcome": "E_LONG"},
     "notes": "Printed on both form faces: 'Both the upper and lower tier entities owe any amount of tax that is calculated as due even if the amount is less than $1,000 or annualized total revenue after the tiered partnership election is $2,650,000 or less.' RED-DEFERRED (R3) — modelled here only so the interaction is stated correctly."},

    # ── EZ ──
    {"scenario_name": "Gate (D) — EZ elected at $18,000,000; EZ costs MORE than the long form", "scenario_type": "normal", "sort_order": 27,
     "inputs": {"annualized_total_revenue": 18000000, "ez_elected": True, "Item10": 18000000, "Item26": 0.5, "Item14": 12000000, "Item18": 2000000, "Item30": "0.0075"},
     "expected_outputs": {"filing_outcome": "D_EZ", "render_target": "05-169", "EZ14": 9000000, "EZ15": 29790, "EZ17": 29790, "long_form_Item23": 6000000, "long_form_Item35": 22500, "ez_recommended": False},
     "notes": "EZ: 18,000,000 x 0.5 = 9,000,000 apportioned revenue x 0.00331 = 29,790. Long form: margin = min(12,600,000; 6,000,000; 16,000,000; 17,000,000) = 6,000,000; apportioned 3,000,000 x 0.0075 = 22,500. Margin/revenue = 33.3% < the 44.13% break-even, so THE EZ IS THE MORE EXPENSIVE CHOICE — recommend the long form."},
    {"scenario_name": "EZ is unavailable above $20,000,000 of annualized revenue", "scenario_type": "edge", "sort_order": 28,
     "inputs": {"annualized_total_revenue": 20000001, "ez_elected": True},
     "expected_outputs": {"filing_outcome": "E_LONG", "render_target": "05-158-A/B"},
     "notes": "Eligibility is '$20 million or less' — one dollar over and the election is unavailable regardless of the flag."},
    {"scenario_name": "EZ break-even ratios: 44.13% vs 0.75%, 88.27% vs 0.375%", "scenario_type": "edge", "sort_order": 29,
     "inputs": {"long_form_rates": ["0.0075", "0.00375"]},
     "expected_outputs": {"breakevens": [0.4413333, 0.8826667], "retailer_should_ever_elect_ez": False},
     "notes": "0.00331/0.0075 = 0.441333...; 0.00331/0.00375 = 0.882666.... Since the four-way minimum caps margin at 70% of revenue and 70% < 88.27%, A QUALIFYING RETAILER OR WHOLESALER CAN NEVER BENEFIT FROM THE EZ."},

    # ── PIR/OIR routing ──
    {"scenario_name": "PIR/OIR routing — LP files the PIR, LLP files the OIR", "scenario_type": "edge", "sort_order": 30,
     "inputs": {"cases": ["limited_partnership", "llp", "trust", "general_partnership", "llc", "s_corporation", "joint_venture"]},
     "expected_outputs": {"routes": ["TX_05_102", "TX_05_167", "TX_05_167", "TX_05_167", "TX_05_102", "TX_05_102", "TX_05_167"]},
     "notes": "⚠ An LLP is NOT an 'LP' — the PIR list enumerates 'limited partnership' only. Trusts, GPs and JVs are not on the list, so they file the OIR."},
    {"scenario_name": "No PIR/OIR accompanies a FINAL report", "scenario_type": "edge", "sort_order": 31,
     "inputs": {"legal_form": "llc", "is_final_report": True, "annualized_total_revenue": 9000000},
     "expected_outputs": {"info_report": None},
     "notes": "Carve-out 1: 'A Public Information Report (Form 05-102) or an Ownership Information Report (Form 05-167) is not required to be filed with the final report.' Corroborated from the form face — the FINAL 05-158 omits the routing question the annual carries."},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM 2 of 3 — TX_05_102 Public Information Report (PIR)
# Filed by CORPORATIONS, LLCs, LIMITED PARTNERSHIPS, PROFESSIONAL ASSOCIATIONS and
# FINANCIAL INSTITUTIONS. ⚠ For a large share of Texas clients this is the ONLY
# Texas output — the entity is below the $2,650,000 threshold and files no franchise
# report at all.
# ═══════════════════════════════════════════════════════════════════════════

TX102_FACTS: list[dict] = [
    {"fact_key": "pir_taxpayer_number", "label": "Texas taxpayer number (11-digit)", "data_type": "string", "required": True, "sort_order": 1},
    {"fact_key": "pir_sos_file_number", "label": "SOS file number", "data_type": "string", "required": False, "sort_order": 2},
    {"fact_key": "pir_report_year", "label": "Report year (preprinted 2026 = Delvio TY2025)", "data_type": "integer", "required": True, "sort_order": 3,
     "default_value": "2026",
     "notes": "⚠ The 2026 PIR accompanies the 2026 franchise report and is due 5/15/2026 — Delvio TY2025."},
    {"fact_key": "pir_legal_form", "label": "Legal form (must be on the PIR list)", "data_type": "choice", "required": True, "sort_order": 4,
     "choices": ["corporation", "c_corporation", "s_corporation", "professional_corporation", "llc",
                 "single_member_llc", "series_llc", "limited_partnership", "professional_association",
                 "financial_institution", "bank", "state_limited_banking_association", "savings_and_loan"],
     "notes": "⚠ If the entity is a GP, LLP, trust, JV, business association or other legal entity it files the OIR (TX_05_167), not the PIR."},
    {"fact_key": "pir_registered_agent", "label": "Registered agent name", "data_type": "string", "required": False, "sort_order": 5},
    {"fact_key": "pir_registered_office", "label": "Registered office address", "data_type": "string", "required": False, "sort_order": 6},
    {"fact_key": "pir_principal_office", "label": "Principal office address", "data_type": "string", "required": False, "sort_order": 7},
    {"fact_key": "pir_principal_place_of_business", "label": "Principal place of business", "data_type": "string", "required": False, "sort_order": 8},
    {"fact_key": "pir_section_a_officers_directors", "label": "Section A — officers, directors and managers (name, title, term dates, address)", "data_type": "string", "required": False, "sort_order": 10,
     "notes": "Collection fact (roster). ⚠ The field-level layout of Sections A/B/C was NOT transcribed line by line in the source brief — transcribe it from the FINAL 05-102 (Rev.2-24/35) PDF before the app build. Diagnostic D_PIR_FIELD_MAP."},
    {"fact_key": "pir_section_b_owned_entities", "label": "Section B — entities in which this entity owns a 10% or greater interest", "data_type": "string", "required": False, "sort_order": 11,
     "notes": "Collection fact (roster)."},
    {"fact_key": "pir_section_c_owner_entities", "label": "Section C — entities owning a 10% or greater interest in this entity", "data_type": "string", "required": False, "sort_order": 12,
     "notes": "Collection fact (roster)."},
    {"fact_key": "pir_signed", "label": "Report completed AND signed", "data_type": "boolean", "required": True, "sort_order": 20,
     "notes": "⚠ Forfeiture-bearing. 'the right to transact business may be forfeited for failure to file the COMPLETED AND SIGNED PIR' — even when the franchise tax report is filed and all taxes paid."},
    {"fact_key": "pir_suppressed_reason", "label": "Suppression reason, if no PIR is due (final report / passive / veteran-owned)", "data_type": "choice", "required": False, "sort_order": 21,
     "choices": ["not_suppressed", "final_report", "passive_entity", "new_veteran_owned"],
     "notes": "The three carve-outs where NEITHER a PIR nor an OIR is filed."},
]

TX102_RULES: list[dict] = [
    {"rule_id": "R-TX-PIR-FILE", "title": "Who files the PIR, and the three carve-outs", "rule_type": "routing",
     "formula": ("PIR is due when the entity has a franchise tax responsibility AND legal_form is a "
                 "corporation, LLC, LIMITED PARTNERSHIP, professional association or financial institution "
                 "AND NOT (is_final_report OR is_passive_entity OR is_new_veteran_owned) ; "
                 "otherwise route to TX_05_167 (OIR) or suppress"),
     "inputs": ["pir_legal_form", "pir_suppressed_reason"], "outputs": ["pir_required"], "sort_order": 1,
     "description": "Verbatim: 'Each corporation, limited liability company (LLC), limited partnership, professional association and financial institution that has a franchise tax responsibility must file a Public Information Report (PIR) to satisfy their filing requirements.' ⚠ THE PIR IS DUE EVEN WHEN NO FRANCHISE TAX REPORT IS — an entity at or below the $2,650,000 no-tax-due threshold files NO franchise report but MUST still file this. For a large share of a small-firm Texas client base the PIR is the ONLY Texas deliverable. Due on the date the franchise tax report is due (5/15/2026 for the 2026 report). A separate PIR is filed by each entity that files a separate franchise report OR that is part of a combined group, 'unless the entity is not organized in Texas and does not have nexus in Texas.'",
     "exceptions": "THREE carve-outs where NO PIR (and no OIR) is filed: (1) FINAL REPORTS — 'not required to be filed with the final report' (corroborated from the form face: the FINAL 05-158 omits the routing question); (2) PASSIVE ENTITIES; (3) NEW VETERAN-OWNED BUSINESSES during the initial five-year period. ⚠ A REIT, by contrast, DOES file one.",
     "notes": "⚠ Federal disregarded status is irrelevant — 'if the disregarded entity is organized in Texas or has nexus in Texas, it is required to file a Public Information Report (Form 05-102) or an Ownership Information Report (Form 05-167).'"},
    {"rule_id": "R-TX-PIR-SECT", "title": "PIR Sections A / B / C — officer, director and 10% ownership rosters", "rule_type": "calculation",
     "formula": ("Section A = officers, directors and managers (name, title, term dates, mailing address) ; "
                 "Section B = entities in which the reporting entity owns a 10% or greater interest ; "
                 "Section C = entities owning a 10% or greater interest in the reporting entity ; "
                 "plus registered agent and registered office, principal office and principal place of business"),
     "inputs": ["pir_section_a_officers_directors", "pir_section_b_owned_entities",
                "pir_section_c_owner_entities", "pir_registered_agent", "pir_registered_office",
                "pir_principal_office", "pir_principal_place_of_business"],
     "outputs": ["pir_sections_complete"], "sort_order": 2,
     "description": "DIRECT-ENTRY rosters. The PIR is an information return — there is no computation, but 'completed' is a legal standard here, not a nicety: an incomplete PIR carries the same forfeiture exposure as an unfiled one.",
     "notes": "⚠ The FIELD-LEVEL layout of Sections A/B/C was NOT transcribed line by line in the VERIFIED source brief (which establishes the sections and their content, not each box). Transcribe from the FINAL 05-102 (Rev.2-24/35, Tcode 13196) PDF before the app build — diagnostic D_PIR_FIELD_MAP."},
    {"rule_id": "R-TX-PIR-SIGN", "title": "⚠ Signature is forfeiture-bearing and independent of the tax", "rule_type": "validation",
     "formula": "pir_signed must be TRUE before the report is transmitted or delivered to the client",
     "inputs": ["pir_signed"], "outputs": ["pir_filable"], "sort_order": 3,
     "description": "Verbatim: 'Even if the franchise tax report is filed and all taxes paid, the right to transact business may be forfeited for failure to file the completed and signed PIR' — with officers and directors PERSONALLY LIABLE for certain debts of the entity (Tex. Tax Code §§171.251, 171.252, 171.255). Forfeiture does not apply to financial institutions (§§171.259, 171.260).",
     "notes": "This is why outcome (C) — 'an information report only' — is a real, consequential deliverable."},
]

TX102_RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R-TX-PIR-FILE", "TX_2026_FORM_05_915", "primary", "PIR filing-requirement sentence + the three carve-outs, verbatim"),
    ("R-TX-PIR-FILE", "TX_2026_FORM_05_102_PIR", "primary", "2026 PIR form face (Rev.2-24/35, Tcode 13196)"),
    ("R-TX-PIR-SECT", "TX_2026_FORM_05_102_PIR", "primary", "Sections A/B/C, registered agent/office, principal office"),
    ("R-TX-PIR-SECT", "TX_2026_FORM_05_915", "secondary", "PIR completion instructions"),
    ("R-TX-PIR-SIGN", "TX_TAX_CODE_CH171", "primary", "§§171.251, 171.252, 171.255 forfeiture and personal liability"),
    ("R-TX-PIR-SIGN", "TX_2026_FORM_05_915", "primary", "'completed and signed PIR' forfeiture language, verbatim"),
]

TX102_LINES: list[dict] = [
    {"line_number": "PIR-HDR", "description": "Taxpayer number, SOS file number, report year 2026, due date 5/15/2026, entity name", "line_type": "input", "source_facts": ["pir_taxpayer_number", "pir_sos_file_number", "pir_report_year"], "sort_order": 1},
    {"line_number": "PIR-ROUTE", "description": "⚠ Filing gate — PIR vs OIR vs suppressed (final report / passive / veteran-owned)", "line_type": "informational", "source_rules": ["R-TX-PIR-FILE"], "sort_order": 2},
    {"line_number": "PIR-AGENT", "description": "Registered agent and registered office", "line_type": "input", "source_facts": ["pir_registered_agent", "pir_registered_office"], "sort_order": 3},
    {"line_number": "PIR-OFFICE", "description": "Principal office and principal place of business", "line_type": "input", "source_facts": ["pir_principal_office", "pir_principal_place_of_business"], "sort_order": 4},
    {"line_number": "PIR-SEC-A", "description": "Section A — officers, directors and managers (name, title, term dates, address)", "line_type": "input", "source_facts": ["pir_section_a_officers_directors"], "sort_order": 5},
    {"line_number": "PIR-SEC-B", "description": "Section B — entities in which this entity owns a 10% or greater interest", "line_type": "input", "source_facts": ["pir_section_b_owned_entities"], "sort_order": 6},
    {"line_number": "PIR-SEC-C", "description": "Section C — entities owning a 10% or greater interest in this entity", "line_type": "input", "source_facts": ["pir_section_c_owner_entities"], "sort_order": 7},
    {"line_number": "PIR-SIGN", "description": "⚠ Signature — forfeiture-bearing, independent of the tax", "line_type": "input", "source_facts": ["pir_signed"], "sort_order": 8},
]

TX102_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_PIR_REQUIRED_NO_TAX_REPORT", "title": "⚠ PIR is due even when NO franchise report is", "severity": "warning",
     "condition": "annualized total revenue <= $2,650,000 (gate outcome C)", "message": "An entity at or below the $2,650,000 no tax due threshold files NO franchise tax report at all — Form 05-163 was discontinued and 'The No Tax Due Report is not available for 2026 reports' — but it MUST still file this Public Information Report. For a large share of a small-firm Texas client base the PIR is the ONLY Texas deliverable. It is due on the date the franchise tax report would have been due: 5/15/2026 for the 2026 report (= Delvio TY2025).",
     "notes": "Gate outcome (C). The most commonly missed Texas filing."},
    {"diagnostic_id": "D_PIR_WRONG_REPORT_OIR", "title": "⚠ This entity should file the OIR, not the PIR", "severity": "error",
     "condition": "legal form is a general partnership, LLP, trust, joint venture, business association or other legal entity", "message": "The PIR list is exhaustive: corporations, LLCs, LIMITED PARTNERSHIPS, professional associations and financial institutions. Everything else files the Ownership Information Report (Form 05-167) — including LIMITED LIABILITY PARTNERSHIPS, because an LLP is NOT an 'LP' on the enumerated list. Route this entity to TX_05_167.",
     "notes": "The LP/LLP distinction is the routing trap."},
    {"diagnostic_id": "D_PIR_SUPPRESSED", "title": "No PIR is due — final report, passive entity, or new veteran-owned", "severity": "info",
     "condition": "is_final_report or is_passive_entity or is_new_veteran_owned", "message": "THREE carve-outs suppress the PIR entirely: (1) it 'is not required to be filed with the final report' — corroborated from the form face, since the FINAL 05-158 omits the PIR/OIR routing question the annual carries; (2) 'A passive entity is not required to file a Public Information Report (Form 05-102) or Ownership Information Report (Form 05-167)'; (3) a new veteran-owned business is not required to file one during the initial five-year period. ⚠ A REIT is NOT a carve-out — a REIT DOES file a PIR or OIR.",
     "notes": "Do not hardwire 'every Texas entity produces a PIR or an OIR.'"},
    {"diagnostic_id": "D_PIR_FORFEITURE", "title": "⚠ An unsigned or incomplete PIR risks forfeiture and personal liability", "severity": "error",
     "condition": "the PIR is unsigned or a required section is incomplete", "message": "Verbatim: 'Even if the franchise tax report is filed and all taxes paid, the right to transact business may be forfeited for failure to file the completed and signed PIR.' Officers and directors become PERSONALLY LIABLE for certain debts of the entity (Tex. Tax Code §§171.251, 171.252, 171.255). Forfeiture does not apply to financial institutions (§§171.259, 171.260). 'Completed' is a legal standard, not a formality.",
     "notes": "Exposure is entirely independent of whether any tax is owed."},
    {"diagnostic_id": "D_PIR_FIELD_MAP", "title": "PIR Section A/B/C field layout must be transcribed before the app build", "severity": "warning",
     "condition": "the PIR render target or data-entry screen is built", "message": "The VERIFIED source brief establishes the PIR's SECTIONS and their content (Section A officers/directors/managers; Section B entities 10%-owned by the reporting entity; Section C entities owning 10%+ of it; plus registered agent/office and principal office/place of business) but does NOT transcribe each box line by line. Transcribe the field-level layout from the FINAL Form 05-102 (Rev.2-24/35, Tcode 13196, preprinted 2026 / 5/15/2026) before building the entry screen or the print target. Do not infer field names.",
     "notes": "Authoritative-Source Rule: flagged rather than guessed."},
    {"diagnostic_id": "D_PIR_COMBINED_MEMBER", "title": "Each combined-group member files its own PIR", "severity": "warning",
     "condition": "the entity is a member of a combined group", "message": "'A separate PIR is filed by each entity that files a separate franchise report OR that is part of a combined group, unless the entity is not organized in Texas and does not have nexus in Texas.' Even where the combined group is at or below the threshold and files no report, Affiliate Schedule or Common Owner Report, 'each individual member that is organized in Texas or has nexus in Texas must file a Public Information Report or Ownership Information Report.' Combined reporting itself is RED-DEFERRED (R2).",
     "notes": "The PIR obligation survives the group's below-threshold status."},
]

TX102_SCENARIOS: list[dict] = [
    {"scenario_name": "PIR is the ONLY output for a below-threshold LLC", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"pir_legal_form": "llc", "annualized_total_revenue": 1200000, "pir_signed": True},
     "expected_outputs": {"pir_required": True, "franchise_report": None, "filing_outcome": "C_INFO_ONLY"},
     "notes": "Gate outcome (C): no franchise report exists, and the PIR is the entire Texas deliverable."},
    {"scenario_name": "Limited partnership files the PIR (not the OIR)", "scenario_type": "edge", "sort_order": 2,
     "inputs": {"pir_legal_form": "limited_partnership", "annualized_total_revenue": 9000000, "pir_signed": True},
     "expected_outputs": {"pir_required": True, "info_report": "TX_05_102"},
     "notes": "'limited partnership' is expressly on the PIR list. Contrast an LLP, which is not."},
    {"scenario_name": "Federally disregarded single-member LLC files its OWN PIR", "scenario_type": "edge", "sort_order": 3,
     "inputs": {"pir_legal_form": "single_member_llc", "federally_disregarded_entity": True, "organized_in_texas": True, "annualized_total_revenue": 800000},
     "expected_outputs": {"pir_required": True, "info_report": "TX_05_102", "franchise_report": None},
     "notes": "'if the disregarded entity is organized in Texas or has nexus in Texas, it is required to file a Public Information Report (Form 05-102) or an Ownership Information Report (Form 05-167).' The #1 practical trap."},
    {"scenario_name": "Passive LP — PIR SUPPRESSED", "scenario_type": "edge", "sort_order": 4,
     "inputs": {"pir_legal_form": "limited_partnership", "pir_suppressed_reason": "passive_entity"},
     "expected_outputs": {"pir_required": False, "info_report": None},
     "notes": "Carve-out 2. The entity still files the 05-158 stub, but no information report."},
    {"scenario_name": "Final report — PIR SUPPRESSED", "scenario_type": "edge", "sort_order": 5,
     "inputs": {"pir_legal_form": "corporation", "pir_suppressed_reason": "final_report"},
     "expected_outputs": {"pir_required": False, "info_report": None},
     "notes": "Carve-out 1, corroborated from the form face: the FINAL 05-158 omits the PIR/OIR routing question."},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM 3 of 3 — TX_05_167 Ownership Information Report (OIR)
# Filed by EVERY taxable entity NOT on the PIR list: general partnerships, LLPs,
# trusts, joint ventures, business associations and other legal entities.
# ═══════════════════════════════════════════════════════════════════════════

TX167_FACTS: list[dict] = [
    {"fact_key": "oir_taxpayer_number", "label": "Texas taxpayer number (11-digit)", "data_type": "string", "required": True, "sort_order": 1},
    {"fact_key": "oir_file_number", "label": "SOS file number or Comptroller file number", "data_type": "string", "required": False, "sort_order": 2},
    {"fact_key": "oir_report_year", "label": "Report year (preprinted 2026 = Delvio TY2025)", "data_type": "integer", "required": True, "sort_order": 3,
     "default_value": "2026"},
    {"fact_key": "oir_legal_form", "label": "Legal form (must NOT be on the PIR list)", "data_type": "choice", "required": True, "sort_order": 4,
     "choices": ["general_partnership", "llp", "limited_liability_partnership", "trust", "business_trust",
                 "joint_venture", "business_association", "other_legal_entity"],
     "notes": "⚠ An LLP is NOT an 'LP' — LLPs belong here, not on the PIR."},
    {"fact_key": "oir_is_trust", "label": "Entity is a trust (report trustee information; check NO box)", "data_type": "boolean", "required": False, "sort_order": 5,
     "notes": "Verbatim: 'Trusts should report their trustee information and not check any box.'"},
    {"fact_key": "oir_section_a_owners", "label": "Section A — general partners, members, managers, trustees and owners", "data_type": "string", "required": False, "sort_order": 10,
     "notes": "Collection fact (roster). ⚠ The field-level layout of Sections A/B was NOT transcribed line by line in the source brief — transcribe from the FINAL 05-167 (Rev.2-24/8) PDF before the app build. Diagnostic D_OIR_FIELD_MAP."},
    {"fact_key": "oir_section_b_ten_percent_owners", "label": "Section B — persons or entities owning a 10% or greater interest", "data_type": "string", "required": False, "sort_order": 11,
     "notes": "Collection fact (roster)."},
    {"fact_key": "oir_signed", "label": "Report completed AND signed", "data_type": "boolean", "required": True, "sort_order": 20,
     "notes": "⚠ Forfeiture-bearing, with partners, members and owners personally liable for certain debts."},
    {"fact_key": "oir_suppressed_reason", "label": "Suppression reason, if no OIR is due (final report / passive / veteran-owned)", "data_type": "choice", "required": False, "sort_order": 21,
     "choices": ["not_suppressed", "final_report", "passive_entity", "new_veteran_owned"]},
]

TX167_RULES: list[dict] = [
    {"rule_id": "R-TX-OIR-FILE", "title": "Who files the OIR — the complement of the PIR list", "rule_type": "routing",
     "formula": ("OIR is due when the entity has a franchise tax responsibility AND legal_form is NOT a "
                 "corporation, LLC, limited partnership, professional association or financial institution "
                 "AND NOT (is_final_report OR is_passive_entity OR is_new_veteran_owned)"),
     "inputs": ["oir_legal_form", "oir_suppressed_reason"], "outputs": ["oir_required"], "sort_order": 1,
     "description": "Verbatim: 'The Ownership Information Report (OIR) is to be filed for each taxable entity OTHER THAN a legally formed corporation, limited liability company, limited partnership, professional association or financial institution.' So general partnerships that are taxable entities, LIMITED LIABILITY PARTNERSHIPS (an LLP is not an 'LP'), business and other taxable trusts, joint ventures, business associations and other legal entities file the OIR. ⚠ LIKE THE PIR, IT IS DUE EVEN WHEN NO FRANCHISE TAX REPORT IS — a below-threshold entity files no franchise report but must still file this. Due on the date the franchise tax report is due (5/15/2026 for the 2026 report). Authority: Tex. Tax Code §171.201(a)(2),(3), §171.202(a)(4), §171.354.",
     "exceptions": "THE SAME THREE carve-outs as the PIR: final reports, passive entities, and new veteran-owned businesses during the initial five-year period. ⚠ A REIT DOES file one.",
     "notes": "A general partnership whose direct ownership is entirely natural persons (and which is not an LLP) is not a taxable entity at all and files nothing — the OIR only reaches GPs that ARE taxable entities."},
    {"rule_id": "R-TX-OIR-SECT", "title": "OIR Sections A / B — owner and 10%-interest rosters", "rule_type": "calculation",
     "formula": ("Section A = general partners, members, managers, trustees and owners ; "
                 "Section B = persons or entities owning a 10% or greater interest ; "
                 "if oir_is_trust: report TRUSTEE information and CHECK NO BOX"),
     "inputs": ["oir_section_a_owners", "oir_section_b_ten_percent_owners", "oir_is_trust"],
     "outputs": ["oir_sections_complete"], "sort_order": 2,
     "description": "DIRECT-ENTRY rosters; no computation. ⚠ Trust handling is explicit and easy to miss: 'Trusts should report their trustee information and not check any box.'",
     "notes": "⚠ The FIELD-LEVEL layout of Sections A/B was NOT transcribed line by line in the VERIFIED source brief. Transcribe from the FINAL 05-167 (Rev.2-24/8, Tcode 13197) PDF before the app build — diagnostic D_OIR_FIELD_MAP."},
    {"rule_id": "R-TX-OIR-SIGN", "title": "⚠ Signature is forfeiture-bearing and independent of the tax", "rule_type": "validation",
     "formula": "oir_signed must be TRUE before the report is transmitted or delivered to the client",
     "inputs": ["oir_signed"], "outputs": ["oir_filable"], "sort_order": 3,
     "description": "The OIR carries the same forfeiture exposure as the PIR, independent of the tax: partners, members and owners become personally liable for certain debts of the entity (Tex. Tax Code §§171.251, 171.252, 171.255). Forfeiture does not apply to financial institutions (§§171.259, 171.260) — but financial institutions file the PIR, not the OIR.",
     "notes": "Both information reports must be signed; the signature is not a formality."},
]

TX167_RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R-TX-OIR-FILE", "TX_2026_FORM_05_915", "primary", "OIR filing-requirement sentence, verbatim, plus the three carve-outs"),
    ("R-TX-OIR-FILE", "TX_2026_FORM_05_167_OIR", "primary", "2026 OIR form face (Rev.2-24/8, Tcode 13197)"),
    ("R-TX-OIR-SECT", "TX_2026_FORM_05_167_OIR", "primary", "Sections A/B; 'Trusts should report their trustee information and not check any box'"),
    ("R-TX-OIR-SECT", "TX_2026_FORM_05_915", "secondary", "OIR completion instructions"),
    ("R-TX-OIR-SIGN", "TX_TAX_CODE_CH171", "primary", "§171.201(a)(2),(3), §171.202(a)(4), §171.354; §§171.251/.252/.255 forfeiture"),
    ("R-TX-OIR-SIGN", "TX_2026_FORM_05_915", "secondary", "signature and forfeiture language"),
]

TX167_LINES: list[dict] = [
    {"line_number": "OIR-HDR", "description": "Taxpayer number, file number, report year 2026, due date 5/15/2026, entity name", "line_type": "input", "source_facts": ["oir_taxpayer_number", "oir_file_number", "oir_report_year"], "sort_order": 1},
    {"line_number": "OIR-ROUTE", "description": "⚠ Filing gate — OIR vs PIR vs suppressed (final report / passive / veteran-owned)", "line_type": "informational", "source_rules": ["R-TX-OIR-FILE"], "sort_order": 2},
    {"line_number": "OIR-SEC-A", "description": "Section A — general partners, members, managers, trustees and owners", "line_type": "input", "source_facts": ["oir_section_a_owners", "oir_is_trust"], "sort_order": 3},
    {"line_number": "OIR-SEC-B", "description": "Section B — persons or entities owning a 10% or greater interest", "line_type": "input", "source_facts": ["oir_section_b_ten_percent_owners"], "sort_order": 4},
    {"line_number": "OIR-SIGN", "description": "⚠ Signature — forfeiture-bearing, independent of the tax", "line_type": "input", "source_facts": ["oir_signed"], "sort_order": 5},
]

TX167_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_OIR_REQUIRED_NO_TAX_REPORT", "title": "⚠ OIR is due even when NO franchise report is", "severity": "warning",
     "condition": "annualized total revenue <= $2,650,000 (gate outcome C)", "message": "An entity at or below the $2,650,000 no tax due threshold files NO franchise tax report — Form 05-163 does not exist for 2026 — but MUST still file this Ownership Information Report. Due 5/15/2026 for the 2026 report (= Delvio TY2025). An at-or-below-threshold entity that cannot file the OIR by May 15 'may request an extension to file its report by filing a zero money extension request' (Form 05-164).",
     "notes": "Gate outcome (C)."},
    {"diagnostic_id": "D_OIR_LLP_NOT_LP", "title": "⚠ An LLP files the OIR — it is NOT an 'LP'", "severity": "warning",
     "condition": "legal form is a limited liability partnership", "message": "The PIR list enumerates 'limited partnership' only. A LIMITED LIABILITY PARTNERSHIP is not on that list and therefore files the Ownership Information Report (Form 05-167). Do not route an LLP to the PIR on the strength of the word 'partnership'. (Separately: an LLP is always a taxable entity — the natural-persons general-partnership carve-out expressly excludes LLPs.)",
     "notes": "The single sharpest routing trap in the PIR/OIR split."},
    {"diagnostic_id": "D_OIR_TRUST_NO_BOX", "title": "Trusts report TRUSTEE information and check no box", "severity": "info",
     "condition": "the filing entity is a trust", "message": "Verbatim: 'Trusts should report their trustee information and not check any box.' Note also that most fiduciary clients are out of scope entirely — grantor trusts, estates of natural persons, escrows, IRC §401(a) trusts and §501(c)(9) trusts are not taxable entities, and a trust may separately qualify as a passive entity (which suppresses the OIR). Trust taxability under §171.0002(c) and Rule 3.581 is RED-DEFERRED (R7).",
     "notes": "Rule 3.581's operative text is unread ([UNVERIFIED] U8)."},
    {"diagnostic_id": "D_OIR_SUPPRESSED", "title": "No OIR is due — final report, passive entity, or new veteran-owned", "severity": "info",
     "condition": "is_final_report or is_passive_entity or is_new_veteran_owned", "message": "The same three carve-outs that suppress the PIR suppress the OIR: it 'is not required to be filed with the final report'; 'A passive entity is not required to file a Public Information Report (Form 05-102) or Ownership Information Report (Form 05-167)'; and a new veteran-owned business files neither during the initial five-year period. ⚠ A REIT is NOT a carve-out — a REIT DOES file one.",
     "notes": "Do not hardwire 'every Texas entity produces a PIR or an OIR.'"},
    {"diagnostic_id": "D_OIR_FORFEITURE", "title": "⚠ An unsigned or incomplete OIR risks forfeiture and personal liability", "severity": "error",
     "condition": "the OIR is unsigned or a required section is incomplete", "message": "The OIR carries forfeiture exposure independent of the tax: partners, members and owners become PERSONALLY LIABLE for certain debts of the entity (Tex. Tax Code §§171.251, 171.252, 171.255). Authority for the report itself: §171.201(a)(2),(3), §171.202(a)(4) and §171.354.",
     "notes": "Same standard as the PIR."},
    {"diagnostic_id": "D_OIR_FIELD_MAP", "title": "OIR Section A/B field layout must be transcribed before the app build", "severity": "warning",
     "condition": "the OIR render target or data-entry screen is built", "message": "The VERIFIED source brief establishes the OIR's SECTIONS and their content (Section A general partners, members, managers, trustees and owners; Section B persons or entities owning 10% or more) but does NOT transcribe each box line by line. Transcribe the field-level layout from the FINAL Form 05-167 (Rev.2-24/8, Tcode 13197, preprinted 2026 / 5/15/2026) before building the entry screen or the print target. Do not infer field names.",
     "notes": "Authoritative-Source Rule: flagged rather than guessed."},
]

TX167_SCENARIOS: list[dict] = [
    {"scenario_name": "LLP files the OIR, not the PIR", "scenario_type": "edge", "sort_order": 1,
     "inputs": {"oir_legal_form": "llp", "annualized_total_revenue": 7000000, "oir_signed": True},
     "expected_outputs": {"oir_required": True, "info_report": "TX_05_167"},
     "notes": "⚠ An LLP is not an 'LP' on the enumerated PIR list."},
    {"scenario_name": "Taxable general partnership (one entity partner) files the OIR", "scenario_type": "edge", "sort_order": 2,
     "inputs": {"oir_legal_form": "general_partnership", "annualized_total_revenue": 4000000, "oir_signed": True},
     "expected_outputs": {"oir_required": True, "info_report": "TX_05_167"},
     "notes": "A GP whose direct ownership is entirely natural persons is NOT a taxable entity and files nothing; one entity partner destroys the carve-out and the GP then files the OIR."},
    {"scenario_name": "Business trust — OIR with trustee information, no box checked", "scenario_type": "edge", "sort_order": 3,
     "inputs": {"oir_legal_form": "business_trust", "oir_is_trust": True, "annualized_total_revenue": 3500000},
     "expected_outputs": {"oir_required": True, "trustee_information_reported": True, "box_checked": False},
     "notes": "'Trusts should report their trustee information and not check any box.' Trust taxability itself is RED-DEFERRED (R7)."},
    {"scenario_name": "Below-threshold joint venture — OIR is the ONLY output", "scenario_type": "normal", "sort_order": 4,
     "inputs": {"oir_legal_form": "joint_venture", "annualized_total_revenue": 900000, "oir_signed": True},
     "expected_outputs": {"oir_required": True, "franchise_report": None, "filing_outcome": "C_INFO_ONLY"},
     "notes": "Gate outcome (C): no franchise report exists; the OIR is the entire Texas deliverable."},
    {"scenario_name": "Passive general partnership — OIR SUPPRESSED", "scenario_type": "edge", "sort_order": 5,
     "inputs": {"oir_legal_form": "general_partnership", "oir_suppressed_reason": "passive_entity"},
     "expected_outputs": {"oir_required": False, "info_report": None},
     "notes": "Carve-out 2. The entity still files the 05-158 stub, but no information report."},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORMS registry + flow assertions
# ═══════════════════════════════════════════════════════════════════════════

FORMS: list[dict] = [
    {
        "identity": {"form_number": "TX_05_158",
                     "form_title": "TX 05-158-A/B — Texas Franchise (Margin) Tax Report, 2026 report year (Delvio TY2025)",
                     "entity_types": FORM_ENTITY_TYPES,
                     "notes": "⚠ A MARGIN TAX, NOT AN INCOME TAX — no federal-income starting point, no addback/subtraction schedule, no K-1 state column, no PTET. ⚠ THE YEAR MAPPING: Delvio TY2025 = the TEXAS 2026 ANNUAL REPORT, due 05/15/2026, for an accounting period ending in calendar 2025; a '2025 Texas report' is TY2024. Owns the FIVE-OUTCOME FILING GATE (nothing / passive-REIT stub / PIR-or-OIR only / EZ / long form), the $500,000 economic-nexus test, total revenue Items 1-10 from named federal facts (NOT hard-coded federal line numbers — W6), COGS Items 11-14 with the 4% Item 12 cap, compensation Items 15-18 with the $480,000 per-person cap on ITEM 15 ONLY, the FOUR-WAY margin minimum Items 19-23 including the revenue-less-$1,000,000 branch, apportionment Items 24-26, SIC-driven rate selection (blank => 0.75%), Items 27-35, and the EZ (05-169) as an INTERNAL COMPUTATION BRANCH plus a separate render target (W2). Entity types cover 1065/1120S/1120 because the margin tax reaches most entities regardless of federal classification."},
        "facts": TX158_FACTS, "rules": TX158_RULES, "rule_links": TX158_RULE_LINKS,
        "lines": TX158_LINES, "diagnostics": TX158_DIAGNOSTICS, "scenarios": TX158_SCENARIOS,
    },
    {
        "identity": {"form_number": "TX_05_102",
                     "form_title": "TX 05-102 — Texas Franchise Tax Public Information Report, 2026 report year (Delvio TY2025)",
                     "entity_types": FORM_ENTITY_TYPES,
                     "notes": "PIR, Rev.2-24/35, Tcode 13196, preprinted 2026 / 5/15/2026. Filed by each CORPORATION, LLC, LIMITED PARTNERSHIP, PROFESSIONAL ASSOCIATION and FINANCIAL INSTITUTION with a franchise tax responsibility. ⚠ DUE EVEN WHEN NO FRANCHISE REPORT IS — for a below-threshold entity (gate outcome C) this is the ONLY Texas deliverable, since Form 05-163 does not exist for 2026. Sections A/B/C carry officer/director/manager, 10%-owned-entity and 10%-owner-entity rosters. Signature is forfeiture-bearing (§§171.251/.252/.255) independent of the tax. Suppressed for FINAL reports, passive entities and new veteran-owned businesses; a REIT DOES file one."},
        "facts": TX102_FACTS, "rules": TX102_RULES, "rule_links": TX102_RULE_LINKS,
        "lines": TX102_LINES, "diagnostics": TX102_DIAGNOSTICS, "scenarios": TX102_SCENARIOS,
    },
    {
        "identity": {"form_number": "TX_05_167",
                     "form_title": "TX 05-167 — Texas Franchise Tax Ownership Information Report, 2026 report year (Delvio TY2025)",
                     "entity_types": FORM_ENTITY_TYPES,
                     "notes": "OIR, Rev.2-24/8, Tcode 13197, preprinted 2026 / 5/15/2026. Filed by 'each taxable entity OTHER THAN a legally formed corporation, limited liability company, limited partnership, professional association or financial institution' — general partnerships that are taxable entities, LIMITED LIABILITY PARTNERSHIPS (⚠ an LLP is NOT an 'LP'), trusts, joint ventures, business associations and other legal entities. ⚠ DUE EVEN WHEN NO FRANCHISE REPORT IS. Sections A/B carry general partner/member/manager/trustee and >=10% owner rosters; 'Trusts should report their trustee information and not check any box.' Same three carve-outs as the PIR."},
        "facts": TX167_FACTS, "rules": TX167_RULES, "rule_links": TX167_RULE_LINKS,
        "lines": TX167_LINES, "diagnostics": TX167_DIAGNOSTICS, "scenarios": TX167_SCENARIOS,
    },
]

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-TX-GATE5", "title": "The Texas filing gate produces exactly five outcomes", "assertion_type": "flow_assertion",
     "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 1,
     "description": "Evaluated in order: (A) not a taxable entity / no nexus / new veteran-owned -> NOTHING; (B) passive entity or qualifying REIT -> STUB report; (C) annualized total revenue <= $2,650,000 -> PIR or OIR ONLY, no franchise report; (D) <= $20,000,000 and EZ elected -> EZ (render 05-169); (E) otherwise -> long form (render 05-158-A/B). No sixth outcome exists.",
     "definition": {"rule": "R-TX-GATE", "check": "outcome in {A_NOTHING, B_STUB, C_INFO_ONLY, D_EZ, E_LONG} and the order of evaluation is 1..7"}},
    {"assertion_id": "FA-TX-NTD-NOFORM", "title": "⚠ At or below $2,650,000 NO franchise report is produced — only a PIR or OIR", "assertion_type": "reconciliation",
     "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 2,
     "description": "When annualized total revenue <= $2,650,000 and there is no tiered-partnership election, the engine must emit franchise_report = NONE and info_report = TX_05_102 or TX_05_167. Form 05-163 was discontinued: 'The No Tax Due Report is not available for 2026 reports.' Emitting any franchise report object here is a bug.",
     "definition": {"rule": "R-TX-GATE", "check": "annualized <= 2650000 and not tiered => franchise_report is None and info_report is not None"}},
    {"assertion_id": "FA-TX-MARGIN4", "title": "⚠ Margin = the LOWEST OF FOUR, each floored at zero first", "assertion_type": "reconciliation",
     "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 3,
     "description": "Item 23 = max(0, min(Item19, Item20, Item21, Item22)) where Item19 = max(0, Item10*0.70), Item20 = max(0, Item10-Item14), Item21 = max(0, Item10-Item18), Item22 = max(0, Item10-1,000,000). The three-way 'revenue minus the greatest of COGS/compensation/30% of revenue' shorthand silently drops Item 22 and OVERSTATES margin whenever the $1M branch wins.",
     "definition": {"rule": "R-TX-MARGIN", "check": "Item23 = max(0, min(I19, I20, I21, I22)) with per-branch zero floors applied BEFORE the min"}},
    {"assertion_id": "FA-TX-M1WINS", "title": "The revenue-less-$1,000,000 branch can win and must be reachable", "assertion_type": "reconciliation",
     "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 4,
     "description": "For a labor-light service entity with no qualifying COGS, Item 22 beats Item 19 whenever total revenue is under $3,333,333, and beats Item 21 whenever compensation is under $1,000,000. Example: revenue 3,000,000, COGS 0, compensation 400,000 -> Item23 = 2,000,000 from branch 22.",
     "definition": {"rule": "R-TX-MARGIN", "check": "revenue=3000000, cogs=0, comp=400000 => Item23 == 2000000 and winning_branch == '22_million'"}},
    {"assertion_id": "FA-TX-COMPCAP", "title": "⚠ The $480,000 cap applies PER PERSON to Item 15 and NEVER to Item 16", "assertion_type": "reconciliation",
     "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 5,
     "description": "Item 15 = SUM over persons of min(person_wages, 480,000 x proration); Item 16 employee benefits pass through with NO cap applied. Negative net distributive income is uncapped. Capping an entity-level total once, or capping Item 16, is a bug.",
     "definition": {"rule": "R-TX-COMP", "check": "wages [600000,600000,600000], benefits 200000 => Item15 == 1440000 and Item16 == 200000 and Item18 == 1640000"}},
    {"assertion_id": "FA-TX-SICRATE", "title": "⚠ Rate selection is SIC-driven; a blank SIC defaults to 0.75%", "assertion_type": "reconciliation",
     "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 6,
     "description": "Item 30 = 0.00375 only when a SIC code is present AND the three retail/wholesale conditions are affirmed; otherwise 0.0075. A blank SIC field defaults to 0.75% explicitly — it is not an unknown. NAICS never affects the rate.",
     "definition": {"rule": "R-TX-RATE", "check": "sic blank => 0.0075; sic present and not qualified => 0.0075; sic present and qualified => 0.00375"}},
    {"assertion_id": "FA-TX-COGSDE", "title": "Item 11 COGS is DIRECT-ENTRY and is never derived from a federal figure", "assertion_type": "flow_assertion",
     "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 7,
     "description": "05-915: the Texas COGS figure 'cannot be found on a federal income tax report or on an income statement. It is a calculated amount specific to Texas franchise tax.' No rule in this spec computes Item 11 from any federal COGS, cost-of-sales or depreciation total. Only Item 12 (the 4% overhead cap) is computed within the COGS block.",
     "definition": {"rule": "R-TX-COGS", "check": "Item11 sourced only from cogs_item11_qualifying; Item12 = 0.04 * indirect_admin_overhead_base"}},
    {"assertion_id": "FA-TX-FEDMAP", "title": "⚠ No federal line number is encoded — the map is re-verified before the build", "assertion_type": "flow_assertion",
     "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 8,
     "description": "W6 / U2 — 05-915 (Rev. 4-26/2) cites 2024 federal form lines for a report built on a 2025 federal return. The federal handoff is expressed as named facts (fed_gross_receipts_or_sales, fed_dividends, fed_interest, fed_rents, fed_royalties, fed_gains_losses, fed_other_income, excl_bad_debt, excl_sch_c_dividends_received_deduction) and the mapping is asserted as a verification obligation, never as a constant.",
     "definition": {"rule": "R-TX-FEDMAP", "check": "no rule formula contains a federal form line reference; D_TX_FED_LINE_MAP is severity=error"}},
    {"assertion_id": "FA-TX-APPORT", "title": "Apportionment — zero rule, both 1.0000 rules, 4-decimal rounding", "assertion_type": "reconciliation",
     "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 9,
     "description": "Item 26 = 0 if Item 24 is zero; 1.0000 if Item 24 equals Item 25 and both are > 0; 1.0000 if Item 24 exceeds Item 25 and both are > 0; otherwise round(Item24/Item25, 4). Single gross receipts factor; no throwback, no throwout.",
     "definition": {"rule": "R-TX-APPORT", "check": "(750000,2000000)->0.3750; (0,2000000)->0.0; (900000,900000)->1.0; (1000000,900000)->1.0"}},
    {"assertion_id": "FA-TX-LT1000", "title": "⚠ Tax < $1,000 suppresses PAYMENT only — the report is still filed", "assertion_type": "reconciliation",
     "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 10,
     "description": "The <$1,000 branch (§171.002(d)(1)) is tested on the COMPUTED tax AFTER the full report is computed and suppresses payment only; the full report AND the PIR/OIR are still filed. It is structurally distinct from the threshold branch (§171.002(d)(2)), which is tested on ANNUALIZED REVENUE BEFORE the computation and produces NO franchise report at all. The test is STRICTLY less than $1,000. A tiered-partnership election defeats both.",
     "definition": {"rule": "R-TX-NOPAY", "check": "Item35=750 => payment_required False and report_still_required True; Item35=1000 => payment_required True; tiered => payment_required whenever Item35 > 0"}},
    {"assertion_id": "FA-TX-NODISC", "title": "Item 34 discount is identically zero and Item 35 equals Item 33", "assertion_type": "reconciliation",
     "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 11,
     "description": "'Discounts do not apply to reports due after Dec. 31, 2009.' Item 35 'Must equal the amount of tax due in Item 33 since discounts do not apply.' There is also no minimum tax and no estimated-payment obligation.",
     "definition": {"rule": "R-TX-TAXDUE", "check": "Item34 == 0 and Item35 == Item33 for every input"}},
    {"assertion_id": "FA-TX-EZBRANCH", "title": "The EZ is ONE spec with two render targets, never two revenue builds", "assertion_type": "flow_assertion",
     "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 12,
     "description": "W2 — EZ Items 1-10 ARE long-form Items 1-10 and EZ Items 11-13 ARE long-form Items 24-26; only EZ Items 14-17 diverge (apportioned revenue x 0.00331, discount 0, total). TX_05_158 owns the shared revenue build and both tax paths; ez_elected selects the tax path and the 05-169 render target. No second copy of the federal line map or the exclusion list may exist.",
     "definition": {"rule": "R-TX-EZ", "check": "EZ14 = Item10 * Item26; EZ15 = EZ14 * 0.00331; EZ17 = EZ15; no duplicate Items 1-10 facts"}},
    {"assertion_id": "FA-TX-EZRECO", "title": "Both paths are computed and RECOMMENDED — never silently defaulted", "assertion_type": "reconciliation",
     "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 13,
     "description": "W8 — the EZ break-even margin ratio is 0.00331/rate: 44.13% against the 0.75% long form and 88.27% against the 0.375% retail rate. Since the four-way minimum caps margin at 70% of revenue, a qualifying retailer or wholesaler can never benefit from the EZ.",
     "definition": {"rule": "R-TX-EZCOMPARE", "check": "breakeven(0.0075) ~ 0.441333; breakeven(0.00375) ~ 0.882667 > 0.70"}},
    {"assertion_id": "FA-TX-PIROIR", "title": "PIR/OIR routing is a clean complement with exactly three carve-outs", "assertion_type": "reconciliation",
     "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 14,
     "description": "PIR = corporation, LLC, LIMITED PARTNERSHIP, professional association, financial institution. OIR = everything else (GP, LLP, trust, JV, business association, other legal entity). ⚠ An LLP is NOT an 'LP'. NEITHER is filed with a FINAL report, by a passive entity, or by a new veteran-owned business; a REIT DOES file one.",
     "definition": {"rule": "R-TX-INFOREPORT", "check": "limited_partnership->TX_05_102; llp->TX_05_167; trust->TX_05_167; final/passive/veteran->None; reit->routed normally"}},
    {"assertion_id": "FA-TX-NOTINCOME", "title": "⚠ Texas imports NO federal income-tax starting point of any kind", "assertion_type": "flow_assertion",
     "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 15,
     "description": "The margin tax has no relationship to federal taxable income. Not taken from the federal return: federal taxable income, federal AGI, any federal deduction schedule, any state addback/subtraction schedule. Total revenue is assembled from ~30 NAMED federal form lines (Items 1-7) plus a closed exclusion list. There is no PTET, no owner credit, no K-1 state column and no nonresident withholding, and a Texas resident INDIVIDUAL generates no Texas filing at all.",
     "definition": {"rule": "R-TX-REVENUE", "check": "no fact or rule references federal taxable income, federal AGI, or a state modification schedule"}},
    {"assertion_id": "FA-TX-DEPRDEFER", "title": "⚠ The depreciation catch-up and the bonus date gate are NOT computed", "assertion_type": "flow_assertion",
     "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 16,
     "description": "R1/W4 — no rule computes the one-time net depreciation adjustment (per-asset zero floor, circular margin limiter, carryforward with no form field, missing per-asset history). W1 — no rule encodes an ASSET-LEVEL bonus placed-in-service or acquisition date key; four official sources state three different scopes and it is an escalated Ken judgement call. Both surface as diagnostics only.",
     "definition": {"rule": "R-TX-DEPRDEFER", "check": "no rule formula contains a per-asset depreciation computation or a 1/19/2025 date key; D_TX_DEPR_CATCHUP and D_TX_BONUS_DATE_GATE both present"}},
]


# ═══════════════════════════════════════════════════════════════════════════
# Command
# ═══════════════════════════════════════════════════════════════════════════

class Command(BaseCommand):
    help = (
        "Load the TX Franchise (margin) Tax specs -- TX_05_158 (+ EZ branch), TX_05_102 PIR, "
        "TX_05_167 OIR -- for the TEXAS 2026 REPORT (= Delvio TY2025), due 05/15/2026. "
        "Refuses to seed until Ken sets READY_TO_SEED=True after the in-session review walk (W1-W9). "
        "W1 (the asset-level bonus date gate) is an escalated judgement call and W6 (the federal-form "
        "vintage) is BLOCKING."
    )

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad TX Franchise (margin) Tax specs -- 2026 report year = Delvio TY2025\n"))
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
                "\nREFUSING TO SEED TX FRANCHISE: not cleared to seed.\n\n"
                "Content is authored, but seeding is gated until Ken reviews the packet and\n"
                "flips the sentinel. Two walk items are LOAD-BEARING and must be closed first:\n\n"
                "  W1  THE ASSET-LEVEL BONUS DATE GATE -- an ESCALATED Ken judgement call\n"
                "      (GATE1_WALK.md item 4). Four official sources, three scopes: STAR\n"
                "      202603002M says 'placed in service on or after January 19, 2025'; the\n"
                "      Dec. 2025 news release says 'acquired'; adopted Rule 3.588 and the FINAL\n"
                "      05-915 impose NO asset-level date gate. The REPORT-YEAR gate is not in\n"
                "      dispute. This spec encodes NO date key -- diagnostic only. Cannot be\n"
                "      guessed (Authoritative-Source Rule).\n\n"
                "  W6  FEDERAL-FORM VINTAGE -- BLOCKING. 05-915 (Rev. 4-26/2) cites 2024 federal\n"
                "      form line numbers for a report built on a 2025 federal return. The ~30-cell\n"
                "      federal line map is the module's spine and MUST be re-verified against the\n"
                "      FINAL 2025 forms (1120, 1120S, 1065, 1041, Sch C/E/F, 8825, 4797, Sch D)\n"
                "      before this spec drives an app build. No federal line number is encoded here.\n\n"
                "Also open: W2 EZ scoping, W3 COGS direct-entry, W4 the depreciation-catch-up\n"
                "RED-defer, W5 combined groups / tiered partnerships, W7 the $480,000 proration\n"
                "formula (34 TAC Sec.3.589 unread), W8 the both-paths recommendation, W9 e-file\n"
                "lead time. Nine [UNVERIFIED] items (U1-U9) are carried in the module docstring.\n\n"
                "!! YEAR CHECK before flipping: this spec is the TEXAS 2026 REPORT (due 05/15/2026)\n"
                "  mapped to Delvio TY2025. A '2025 Texas report' is TY2024 and is the WRONG source.\n\n"
                f"READY_TO_SEED = {READY_TO_SEED} (must be True to proceed)\n\n"
                f"Currently empty / placeholder:\n  {still_empty}\n\n"
                "To proceed: review the module-level data lists (and\n"
                "delvio-states/research/tx_entity_source_brief.md + conformity/tx_conformity.md),\n"
                "then set READY_TO_SEED = True. Idempotent via update_or_create.\n"
                "DO NOT relax this guard to silence the error."
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
                # EXPECTED for TX_STAR_202603002M_IRC_CONFORMITY: the Tier-1 conformity
                # batch is GATED and unseeded. Every rule that references it also carries a
                # primary link to a source defined in AUTHORITY_SOURCES, so nothing is orphaned.
                self.stdout.write(self.style.WARNING(
                    f"  existing source {code} NOT FOUND -- links to it will be skipped"))
        self.stdout.write(f"Sources ready: {len(sources)}")
        return sources

    def _upsert_form(self, identity: dict) -> TaxForm:
        form, created = TaxForm.objects.update_or_create(
            form_number=identity["form_number"], jurisdiction=FORM_JURISDICTION,
            tax_year=FORM_TAX_YEAR, version=FORM_VERSION,
            defaults={"form_title": identity["form_title"],
                      "entity_types": identity.get("entity_types", FORM_ENTITY_TYPES),
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
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write("TX Franchise (margin) Tax specs loaded -- TEXAS 2026 REPORT = Delvio TY2025.")
        for spec in FORMS:
            fn = spec["identity"]["form_number"]
            self.stdout.write(
                f"  {fn}: facts {len(spec['facts'])} / rules {len(spec['rules'])} / "
                f"lines {len(spec['lines'])} / diag {len(spec['diagnostics'])} / "
                f"tests {len(spec['scenarios'])} / links {len(spec['rule_links'])}"
            )
        self.stdout.write(f"  Flow assertions: {len(FLOW_ASSERTIONS)}")
        self.stdout.write(f"  Authority sources: {len(AUTHORITY_SOURCES)} "
                          f"(+{len(EXISTING_SOURCES_TO_REFERENCE)} referenced)")
        self.stdout.write("  !! W1 asset-level bonus date gate: OPEN (Ken judgement call, no key encoded).")
        self.stdout.write("  !! W6 federal-form vintage: BLOCKING (no federal line number encoded).")
        self.stdout.write("=" * 70)
