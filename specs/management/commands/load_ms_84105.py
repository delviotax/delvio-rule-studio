"""Load the MS Form 84-105 spec — Mississippi Pass-Through Entity Tax Return (TY2025).

═══════════════════════════════════════════════════════════════════════════
WHAT THIS IS
═══════════════════════════════════════════════════════════════════════════
Mississippi does NOT have a partnership return and an S-corporation return.
It has ONE return — Form 84-105 — whose entity type is a radio pair in the
header (Partnership/LLC/LLP (Federal 1065)  |  S Corporation (Federal 1120-S)).
Both modules feed the same Form 84-122 income engine and the same 84-131 /
84-132 owner schedules.

⚠ BUT THE TOP THIRD OF THE RETURN — LINES 1 THROUGH 4 — IS AN
S-CORPORATION-ONLY FRANCHISE-TAX BLOCK. See "THE MODULE FORK" below.

Spec source: delvio-states/research/ms_pte_source_brief.md (VERIFIED, adversarial
pass 2026-08-16; its §17 Verification section SUPERSEDES the body and carries six
corrections + one form omission). Conformity spine:
delvio-states/conformity/ms_conformity.md (VERIFIED, adversarial pass 2026-08-06;
its §12 governs).

Gap check: lookup/MS_84_105/export/ -> 404. No load_ms_* loader existed in RS.
NEW form. Code MS_84_105 per the <ST>_<FORM> namespace (campaign D-9).

═══════════════════════════════════════════════════════════════════════════
⚠ THE MODULE FORK — stated once, encoded as a real branch (brief §2.1)
═══════════════════════════════════════════════════════════════════════════
                            | Partnership/LLC/LLP (1065) | S corporation (1120-S)
  Franchise tax L1-L4 / 84-110 | NOT APPLICABLE (blank)   | APPLIES, $25 minimum
  Income tax L5-L8            | composite or EPTE only   | composite or EPTE only
                              |                          | (+ the §2.4 84-380 failure)
  ⚠ L9 TOTAL                  | = L8                     | = L4 + L8
  Underestimate form (L15)    | COMPOSITE partnership ->  | Form 83-305 L19, BOTH modes
    ⚠ keyed on MODE x ENTITY  |   Form 80-320 L11 (80%)  |   (90%)
                              | ELECTING-PTE partnership |
                              |   -> Form 83-305 L19 (90%)|
  Backstop withholding        | 5% of net gain/profit,    | 5% (highest marginal rate)
                              |   Form 84-387             |   for a missing Form 84-380
  K-1 boxes 4a/4b/4c          | guaranteed payments used  | "partnerships only" — n/a

DOR states the L9 fork verbatim (84-100 Rev. 01/26 p.17): "S corporations, enter
the amount from line 4; composite and electing pass-through entity S corporations,
enter the amounts from line 4 plus line 8; and composite and electing pass-through
entity partnerships, enter the amount from line 8."

⚠ The $25 franchise MINIMUM makes the partnership failure mode SILENT AND NON-ZERO:
the smallest possible partnership would file a $25 tax it does not owe. L1-L4 are
therefore HARD-GATED on the entity-type radio, not merely "left blank".

Two documented exceptions (brief §2.1): (1) a partnership/LLC that elected federal
CORPORATE treatment is not an 84-105 filer at all -> Form 83-105 (RED, R15);
(2) an exempt organization with UBTI files 84-105, leaves L1-L4 blank, and enters
Form 990-T UBTI on 84-122 line 1.

═══════════════════════════════════════════════════════════════════════════
⚠ DEPRECIATION — THE LINE NUMBERS ARE 84-122 L8 AND L15, NOT L6 AND L13
═══════════════════════════════════════════════════════════════════════════
Verified by positional (x,y) read of the FINAL TY2025 Form 84-122 face
(84-122-25-8-1/2-000 (Rev. 10/25), ModDate 2025-10-08), and re-confirmed on the
adversarial pass (brief §17.1):

  84-122 L6  = "Interest on obligations of other states or political subdivisions
                (net of expenses)"                          <- MUNICIPAL BOND INTEREST
  84-122 L13 = "Income (loss) from partnership, S corporation or trust"
                                                            <- FLOW-THROUGH INCOME
  84-122 L8  = "Federal special depreciation allowance"      <- THE ADD-BACK  (+)
  84-122 L15 = "Additional depreciation due to a difference in the depreciable
                base for federal and state purposes (attach schedule)"
                                                            <- MS-BASIS RECOVERY (-)

L6/L13 are the Form 83-122 (CORPORATE) line numbers. Coding them here would report
the federal special depreciation allowance as MUNICIPAL-BOND INTEREST and the state
basis recovery as LOWER-TIER FLOW-THROUGH INCOME — silently, in the wrong box, on
every Mississippi PTE return carrying bonus depreciation, and L13 would additionally
corrupt the L24 re-insertion of already-sourced flow-through income.
DOR states the pairing itself (84-122 L8 instruction): "Any additional depreciation
expense, for purposes of this state, due to the basis adjustment not being made is
reported on line 15 of this form."

GENERAL RULE — MS runs its OWN permanent 100% bonus, independent of IRC §168(k)
(§27-7-17(1)(f)(ii)2, property placed in service after 12/31/2022, "notwithstanding
any changes to federal law related to cost recovery"); qualified property / QIP
definitions FROZEN at 1/1/2021; elective and IRREVOCABLE; combined methods capped at
100% of cost (§27-7-17(1)(f)(ii)6). DO NOT CODE A FEDERAL BONUS ADD-BACK BY REFLEX.

⚠ THE NARROW EXCEPTION — AVIATION. §27-7-17(1)(f)(i): "In the case of new or used
aircraft, equipment, engines, or other parts and tools used for aviation, allowance
for bonus depreciation CONFORMS WITH THE FEDERAL BONUS DEPRECIATION RATES..." So for
TY2025 an aviation asset acquired in 2024 and placed in service in 2025 follows the
FEDERAL 40%, while a non-aviation asset placed in service the same year gets MS 100%.
Two assets, same year, same taxpayer, different regimes. NO aviation line, checkbox
or word exists on Form 84-122 or in the FINAL TY2025 84-100 booklet (searched: zero
hits) — the branch is statutory only and needs an app-level flag (W4).

L8/L15 are NOT a same-year wash: L15 recurs every year until the asset is fully
recovered, because Mississippi never reduces the asset's basis. A separate
Mississippi depreciation ledger per asset, for the life of the asset, is implied by
the "second Form 4562 labeled Mississippi" mechanic. v1 DIRECT-ENTERS L8 and L15
(W3); the MS-basis engine is v1.1 (R7).

═══════════════════════════════════════════════════════════════════════════
⚠ THE COMPOSITE-RATE CONFLICT IS THREE-SIDED AND UNRESOLVED — NO SIDE IS PICKED
═══════════════════════════════════════════════════════════════════════════
  A. DOR, twice, TY2025-keyed: 0% first $5,000 / 4% next $5,000 / 5% over $10,000
     (84-100 p.7 Tax Rates; 84-105 L6 instruction).
  B. Statutory: composite members are nonresident INDIVIDUALS; §27-7-5(1)(b) reduces
     the rate for individuals only -> 0% first $10,000 / 4.4% above. DOR's own
     composite text: income "computed in the same manner as in a separate individual
     filing".
  C. Official 35 Miss. Admin. Code Title 35 Pt.III (SOS capture, ModDate 2026-05-26):
     the regulation PACKAGES the $5,000/10% deduction WITH the individual rate (the
     nonresident-individual-return route) and the "regular corporate rate" WITH NO
     deduction (the corporate-return route, S corps only; no corporate-rate
     alternative is offered for partnerships at all). The TY2025 forms take one half
     of EACH — 84-122 L30 gives the deduction AND 84-105 L6 taxes at 0/4/5.

DOR's own plumbing splits the modules (composite S corps -> corporate Form 83-305;
composite partnerships -> individual Form 80-320), so the rate question is live in
DOR's own machinery.

**THIS SPEC ENCODES A DIAGNOSTIC AND NO COMPUTED COMPOSITE RATE.**
`_ms_composite_tax()` returns None by design. The ELECTING-PTE rate (0/4/5) IS
settled and IS computed. Composite L6 is direct-entry behind D_MS84105_COMPOSITE_RATE
until Ken rules (W1/U1). Do not "fix" this by choosing.

═══════════════════════════════════════════════════════════════════════════
v1 SCOPE — PROPOSED, NOT YET WALKED (brief §15). READY_TO_SEED ships False.
═══════════════════════════════════════════════════════════════════════════
COMPUTES: 84-105 L1-L4 (S corps only, TY-keyed franchise rate + $25 min +
  $100,000 exemption, L4 = MAX(0, L2-L3)); Form 84-110 L8/L12/L13/L15/L16/L18
  (capital base, property+gross-receipts ratio, assessed-value FLOOR, short-period
  proration, round-up to next $1,000); 84-105 L5-L8 (EPTE rate 0/4/5, §27-7-5(4)
  fiscal-year proration as a general mechanism, L8 = MAX(0, L6-L7)); 84-105 L9-L22
  incl. the L9 ENTITY FORK, the L12 lower-tier PTET credit, and the L20 ASYMMETRY
  (L13 - L9 - L15, late-payment items NOT netted); Form 84-122 full engine (L4, L10,
  L17, L18, L20, L22 with the 100%-Mississippi short path, L28 PER THE FACE
  "22 through 26 MINUS 27", and both terminal blocks L29-L32 composite / L33-L35
  EPTE with their zero floors); Form 84-125 Part I (incl. 1e rental x 8) and Part II
  lines 4 / 5a-5g / 6a-6e; the sales-factor numerator rules incl. THROWBACK and the
  U.S. Government ORIGIN rule; Form 84-155 NOL (B-D=E, 2 back / 20 forward);
  Form 84-131 (owner grid, Column D = 84-105 L8 x ownership%); Form 84-132 Part V;
  Form 84-161 (L5 = MIN(L3D, L4), L6 excess); Form 84-401 grid -> L3 / L7;
  Form 84-115 MS8453-PTE Part I lines 1-7 tie-outs; filing modes incl. the
  inactive-S-corp $25 mode and the exempt-org-with-UBTI mode; estimates thresholds.
DIRECT-ENTRY: every 84-122 modification amount (L1,2,3,5,6,7,**8**,9,11,12,13,14,
  **15**,16,26,27); 84-110 balance-sheet inputs + county assessed-value grid;
  84-125 Part I raw column A/B amounts; 84-150 rows 1a-1i; 84-132 Boxes 2-14 incl.
  Box 13 MS §179; 84-401 credit rows; 84-105 L10, L11, L15-L18, L21/L22; 84-115
  identity/signature blocks; 84-155 prior-year rows; 84-381 field capture.
RED-DEFER (R1-R17, each with its OWN diagnostic — no silent gap): direct accounting /
  84-124; 84-125 line 7 special formula; pipelines; financial institutions;
  pharmaceutical five-factor; fee-in-lieu; the MS-basis depreciation engine; aviation
  assets; the S-corp 84-380 failure charge; the 84-387 5% backstop; the 83-305 AND
  80-320 underestimate computations (BRANCHED — different safe harbours); composite +
  EPTE both checked; per-credit computation for all 60 84-401 codes; 84-122 L27 MDA
  exemption; federal corporate election -> wrong form; combined/consolidated
  reporting; Form 84-381 preparation.

═══════════════════════════════════════════════════════════════════════════
requires_human_review WALK ITEMS (Ken, before seeding) — brief §14
═══════════════════════════════════════════════════════════════════════════
W1.  ⚠ THE COMPOSITE RATE (U1). Three-sided, unresolved. Spec computes NOTHING.
     Recommendation: ship DOR's 0/4/5 as a single-point-of-change flagged constant
     with a review diagnostic on every composite return, and open a DOR ticket.
     Record as a RULING, not a finding.
W2.  ⚠ THE FRANCHISE-TAX FORK. Hard-gate L1-L4 on entity type; diagnostic if a
     partnership return carries any value in 1-4. Confirm the page-2 Part I line 4
     "elected corporate treatment" RED and the exempt-org-UBTI blank-1-4 mode.
W3.  ⚠ DEPRECIATION SCOPE: v1 direct-entry of 84-122 L8/L15 vs a full MS-basis
     engine (second "Mississippi" Form 4562, recurring L15, irrevocable election,
     100%-of-cost cap, aviation branch). Ken is the depreciation specialist — the
     single largest scope lever on this form.
W4.  ⚠ THE AVIATION BRANCH. No form field exists. Confirm an app-level asset flag
     (ms_aviation_asset) driving the FEDERAL rate is acceptable ahead of a DOR answer.
W5.  ⚠ THROWBACK + which apportionment formulas ship in v1. Bless the P.L. 86-272
     reading (a MS manufacturer protected in the destination state throws back).
W6.  ⚠ COMPOSITE + ELECTING PTE ON ONE RETURN (U2). Recommend mutually exclusive in
     v1 with a RED if both are checked; confirm with DOR.
W7.  ⚠ BLESS THE FIVE DOR ERRATA (E1-E5) — build to the FORM FACE. Plus the two new
     verification-pass corrections (underestimate-form fork; 80% vs 90%).
W8.  ⚠ TWO ARITHMETIC ASSUMPTIONS READ OFF THE FORM: (a) franchise =
     MAX(25, 0.75 x CEIL(MAX(0, capital - 100,000) / 1,000)) with the 84-110 L18
     round-up applied first — the interaction with the statutory "or fraction
     thereof" is untested; (b) 84-110 L6/L7 sign convention (U16).
W9.  ⚠ THE PTET ELECTION IS BINDING FOR ALL LATER YEARS, is made on a SEPARATE form
     (84-381), CANNOT be made retroactively by amending, and requires a governance
     vote. Client-advice exposure. Decide: hard confirmation before the EPTE box,
     an 84-381 attachment check, a standing per-client persistence flag, and whether
     the product prepares 84-381 at all.
W10. ⚠ THE MISSISSIPPI §179 AMOUNT (U13). 84-132 Box 13 needs an MS-specific figure;
     no MS line computes it and no instruction derives it. v1 direct-entry.
W11. ⚠ ARE 84-131 / 84-132 IN v1? They are the PTET's whole delivery mechanism and
     the 100-K-1 e-file mandate makes K-1 production the practical filing gate.

═══════════════════════════════════════════════════════════════════════════
[UNVERIFIED] / OPEN ITEMS — 17 raised, 4 closed on the adversarial pass, 13 LIVE.
Every live one must be re-pulled or ruled. NEVER guessed here.
═══════════════════════════════════════════════════════════════════════════
U1.  ⚠ The composite-return rate — three positions, none dispositive. (-> W1)
U2.  Whether one return may be BOTH composite and electing PTE, and what goes on
     84-105 L5 if it is. Both boxes sit under CHECK ALL THAT APPLY. (-> W6, R12)
U3.  The Fee-In-Lieu checkbox on 84-105 L2 — printed on the FINAL face, ZERO hits in
     both FINAL TY2025 booklets. Statutory basis §27-13-5(3)(a). (-> R6)
U4.  No financial-institution apportionment formula exists anywhere in the official
     Title 35 Part III (123 pp.), yet Form 84-125 line 6 lists them. (-> R4)
U5.  Pipelines — Form 84-125 line 6 = (property+payroll+SALES)/3; official §402.07 =
     (property+payroll+TRAFFIC MILES)/3. Different formulas. (-> R3)
U6.  The five-factor major-medical/pharmaceutical variant is cited by Form 84-125 to
     the 84-100 booklet, which contains ZERO occurrences of "pharmaceutical"; the
     rule exists only in the 83-100 corporate booklet. (-> R5)
U7.  84-122 line 30 has no printed formula. Booklet: "$5,000 or 10% of the composite
     NET INCOME, whichever is less". Regulation: "10% of ADJUSTED GROSS INCOME".
     DIFFERENT BASES. Bound up with U1.
U8.  Whether the composite and electing-PTE NOL pools are distinct (84-122 L31 vs
     L34, both from Form 84-155 line 2; L31 instruction says "separate company
     composite" NOL). Whether one entity can carry two pools is unstated.
U9.  Whether the MS NOL is applied pre- or post-apportionment. The form's arithmetic
     says post (L31/L34 sit after L28); no DOR statement found. Ken should BLESS
     rather than the spec assuming.
U13. How the "Mississippi Section 179 deduction" on 84-132 Box 13 is computed. MS
     apportionment and MS basis both differ from federal, so it is NOT
     federal x ownership%. (-> W10)
U14. The R&E election's landing line — the 84-122 L8 instruction says L8; the L16
     instruction says L16. Net effect coherent, routing is not.
U15. The S-corp nonresident-agreement failure amount (§2.4). L5 carries "the income
     on which payment of tax is required", but L6 then applies 0/4/5 while the
     statutory charge is a FLAT 5% of that income. On a share under $10,000 the two
     differ. (-> R9)
U16. Form 84-110 sign convention on L6 (Less treasury stock) and L7 (holding-company
     exclusion) inside "add line 1 through line 7". Assumed SUBTRACTIVE. (-> W8)
U17. ⚠ PARTIALLY RESOLVED. The DOR APPROVED PAPER-FORM PROVIDER program IS published
     (per-vendor x per-form matrix, 16 forms incl. 84-115, approval dates Nov 2025 -
     Feb 2026). The MeF/e-file handbook, the Letter of Intent, and the ATS/test
     window remain UNPUBLISHED. Ken-only, lead-time-bearing:
     efile@dor.ms.gov / (601) 923-7700.
CLOSED on the adversarial pass: U10 (Form 80-320 retrieved — produced the 80%
correction), U11 (Form 83-305 face transcribed), U12 (Form 84-150 was /Rotate 90,
not scrambled; column map confirmed from the face).

═══════════════════════════════════════════════════════════════════════════
DOR ERRATA — BUILD TO THE FORM FACE (brief §12; all five re-verified)
═══════════════════════════════════════════════════════════════════════════
E1. 84-132 Box 1 instruction cites 1120-S p.1 L21 / 1065 p.1 L22 — BOTH are
    "Total deductions" on the FINAL 2025 IRS forms. Build to 1120-S L22 / 1065 L23
    (the 84-122 L1 FACE cite, which is correct).
E2. 84-105 L7 instruction says "Form 83-401" — face says Form 84-401. 83-401 is the
    corporate series. Build to 84-401.
E3. 84-105 L19 instruction says "if line 10 is larger than line 13" — face says
    line 9. L10 is prior-year overpayment; the comparison is meaningless. Use L9.
E4. 84-122 L28 instruction says "sum lines 22 through 27" — face says "add line 22
    through line 26 MINUS line 27". L27 is an exemption. Build to the face.
E5. 84-122 L1 instruction says "before net operating loss and special deductions" —
    Form 1120 line 28 boilerplate. Build to the face.

═══════════════════════════════════════════════════════════════════════════
VERIFIED STRUCTURE + CONSTANTS — every line number and verbatim label read
POSITIONALLY off the FINAL TY2025 MS DOR PDFs (all ModDate 2025-10-08; booklets
2026-01-14), then independently re-derived on the adversarial pass 2026-08-16.
NOT memory, NOT training data, NOT another state's brief. NEVER CLONE GA.
Full source brief: delvio-states/research/ms_pte_source_brief.md
═══════════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════
SAFETY GUARD — READY_TO_SEED stays False until Ken approves the review walk
(W1-W11 above, and the 13 live open items) in-session. Until then the command
refuses to write to the DB. DO NOT relax the guard to silence the error.
═══════════════════════════════════════════════════════════════════════════
"""
from decimal import ROUND_CEILING, Decimal

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
# SAFETY GUARD — flip ONLY after Ken's in-session review walk (W1-W11 above).
# NOT FLIPPED. Mississippi has 13 live open items, the composite rate is an
# unresolved three-way conflict that this spec deliberately does not decide,
# and the v1 COMPUTES/DIRECT-ENTRY/RED-DEFER boundary has not been walked.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = False


FORM_JURISDICTION = "MS"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"
FORM_ENTITY_TYPES = ["1065", "1120S"]


# ═══════════════════════════════════════════════════════════════════════════
# VERIFIED CONSTANTS — TY-keyed; cited in ms_pte_source_brief.md; never memory
# ═══════════════════════════════════════════════════════════════════════════

# Franchise tax rate per $1,000 of capital in excess of $100,000 (84-100 p.3 ladder;
# §27-13-5(1)(a)(ix)-(xi)). SB 2858 (2016) phase-out. NO clause exists for 2028+:
# the tax is REPEALED effective January 1, 2028. MUST be a TY-keyed table with a
# sunset, NEVER a constant.
MS_FRANCHISE_RATE_PER_1000: dict[int, str | None] = {
    2020: "2.00", 2021: "1.75", 2022: "1.50", 2023: "1.25", 2024: "1.00",
    2025: "0.75", 2026: "0.50", 2027: "0.25", 2028: None,  # repealed 1/1/2028
}
MS_FRANCHISE_MINIMUM = 25                 # §27-13-5(1)(b) — "in no case ... less than $25"
MS_FRANCHISE_EXEMPT_CAPITAL = 100_000     # rate applies to capital IN EXCESS OF $100,000
MS_FRANCHISE_REPEAL_TAX_YEAR = 2028

# Income tax — the NON-INDIVIDUAL schedule. §27-7-5(1)(a) levies 0/4/5 on "every
# resident individual, corporation, association, trust or estate"; §27-7-5(1)(b)
# then reduces the rate FOR INDIVIDUALS ONLY. A partnership/S corp is not an
# individual, so an ELECTING PTE sits on the unreduced 0/4/5. SETTLED.
# (bracket_top, rate)
MS_ENTITY_RATES: dict[int, list] = {2025: [(5_000, "0.00"), (10_000, "0.04"), (None, "0.05")]}

# ⚠ POSITION B ONLY — the INDIVIDUAL schedule, recorded for the W1 conflict record.
# NEVER applied by this spec to an 84-105 line. §27-7-5(1)(b)(ii)2.
MS_INDIVIDUAL_RATES_REFERENCE_ONLY: dict[int, list] = {2025: [(10_000, "0.00"), (None, "0.044")]}

# ⚠ W1/U1 — THE COMPOSITE RATE IS UNRESOLVED. No schedule is selected here.
MS_COMPOSITE_RATE_RESOLVED = False
MS_COMPOSITE_RATE_POSITIONS: list[dict] = [
    {"position": "A", "schedule": "0% / 4% / 5% (entity schedule)",
     "authority": "MS DOR, 84-100 (Rev. 01/26) p.7 Tax Rates AND the 84-105 L6 instruction, both TY2025-keyed",
     "note": "What the ADMINISTERING authority prescribes, and what a product must match to clear MS's approval gate."},
    {"position": "B", "schedule": "0% first $10,000 / 4.4% above (individual schedule)",
     "authority": "Miss. Code Ann. §27-7-5(1)(b) + §27-7-5(3); composite members are nonresident INDIVIDUALS",
     "note": "DOR's own composite text: income 'computed in the same manner as in a separate individual filing'."},
    {"position": "C", "schedule": "TWO PACKAGED ROUTES, and they differ between the modules",
     "authority": "35 Miss. Admin. Code Title 35 Pt.III §112.03 (S corps) and the partnership Composite Returns chapter",
     "note": "Regulation pairs the $5,000/10% deduction WITH the individual rate, and the corporate rate WITH NO "
             "deduction (S corps only; NO corporate-rate alternative is offered for partnerships). The TY2025 forms "
             "take one half of EACH."},
]

# §27-7-5(4) fiscal-year proration (restated on the 84-105 L6 instruction): compute
# the full-year tax at the BEGINNING-year rates and at the ENDING-year rates, weight
# each by months in that calendar year, and add. A no-op for an electing PTE in
# TY2025 (0/4/5 did not change 2025->2026) but LIVE on the franchise side (0.75->0.50)
# and live for composite if W1 resolves to the individual schedule (4.4%->4.0%).
# Encode as a general mechanism keyed to a rate table, NOT as dead code.
MS_FISCAL_YEAR_PRORATION_STATUTE = "Miss. Code Ann. §27-7-5(4)"

# Flat 5% charges — NOT the 0/4/5 schedule. Two different, unrelated backstops.
MS_NR_AGREEMENT_FAILURE_RATE = "0.05"   # S corp, missing Form 84-380 (§27-7-5 highest marginal rate)
MS_PARTNERSHIP_BACKSTOP_RATE = "0.05"   # partnership, Form 84-387 withholding of net gain/profit

# Estimates (84-100 pp.6, 21-22; DOR EPTE FAQ).
MS_ESTIMATE_THRESHOLD = 200             # annual income tax liability IN EXCESS OF $200
MS_LARGE_ENTITY_THRESHOLD = 1_000_000   # MS taxable income >= $1M in any of 3 preceding years
MS_UNDERESTIMATE_PENALTY_RATE = "0.10"  # Form 83-305 L11 only
MS_UNDERESTIMATE_INTEREST_MONTHLY = "0.005"  # 1/2 of 1% per month, BOTH forms

# ⚠ [CORRECTED — verification pass] SAFE HARBOUR FORKS ON MODE x ENTITY, NOT ENTITY.
MS_SAFE_HARBOUR: dict[str, dict] = {
    "83-305": {"form": "83-305", "feed_line": "19", "current_year_pct": "0.90",
               "instalments": "15th of the 4th / 6th / 9th / 12th month",
               "has_10pct_penalty": True, "interest_monthly": "0.005",
               "reached_by": "S corporations (composite OR electing PTE) AND electing-PTE partnerships"},
    "80-320": {"form": "80-320", "feed_line": "11", "current_year_pct": "0.80",
               "instalments": "Apr. 15, 2025 / June 15, 2025 / Sept. 15, 2025 / Jan. 15, 2026 (CALENDAR-keyed)",
               "has_10pct_penalty": False, "interest_monthly": "0.005",
               "reached_by": "COMPOSITE PARTNERSHIPS ONLY (printed on the 84-105 L15 face)"},
}

# Composite deduction in lieu of exemptions -> 84-122 L30. ⚠ U7: the BASE is
# contested (booklet "composite NET INCOME" vs regulation "ADJUSTED GROSS INCOME")
# and the form face gives NO formula and NO cap — the line is "(attach schedule)".
MS_COMPOSITE_DEDUCTION_CAP = 5_000
MS_COMPOSITE_DEDUCTION_PCT = "0.10"
MS_COMPOSITE_DEDUCTION_BASE_RESOLVED = False

# NOL — Mississippi does NOT conform to federal NOL rules (§27-7-17).
MS_NOL_CARRYBACK_YEARS = 2
MS_NOL_CARRYFORWARD_YEARS = 20

# Depreciation. MS's OWN permanent 100% bonus for property placed in service AFTER
# this date (§27-7-17(1)(f)(ii)2); §168(k)/§168(e)(6) definitions FROZEN at 1/1/2021.
MS_OWN_BONUS_PIS_AFTER = "2022-12-31"
MS_OWN_BONUS_RATE = "1.00"
MS_BONUS_DEFINITION_FREEZE_DATE = "2021-01-01"
MS_DEPRECIATION_COMBINED_CAP_PCT = "1.00"   # §27-7-17(1)(f)(ii)6 — cannot exceed 100% of cost
# ⚠ AVIATION: §27-7-17(1)(f)(i) — conforms to the FEDERAL bonus rate. OBBBA TY2025:
# 100% if acquired AND placed in service after 1/19/2025; 40% otherwise.
MS_AVIATION_FOLLOWS_FEDERAL = True
FED_OBBBA_FULL_BONUS_ON_OR_AFTER = "2025-01-20"
FED_OBBBA_PRIOR_BONUS_RATE = "0.40"
FED_OBBBA_FULL_BONUS_RATE = "1.00"
# §179 — ROLLING (§27-7-17(1)(f)(ii)3, "in effect for that year"). MS publishes NO
# §179 dollar figure of its own. ENCODE AS "= federal for the tax year", never a constant.
MS_179_FOLLOWS_FEDERAL_FOR_YEAR = True
MS_179_FEDERAL_TY2025_REFERENCE = {"limit": 2_500_000, "phaseout": 4_000_000, "suv_sublimit": 31_300}

# ⚠ THE FOUR 84-122 LINES THIS SPEC EXISTS TO KEEP STRAIGHT. Positional read of the
# FINAL TY2025 84-122 face. DO NOT EDIT WITHOUT RE-READING THE FORM FACE.
MS_84122_DEPRECIATION_ADDBACK_LINE = "122-L8"
MS_84122_DEPRECIATION_RECOVERY_LINE = "122-L15"
MS_84122_MUNI_BOND_INTEREST_LINE = "122-L6"     # NOT depreciation — the trap
MS_84122_FLOWTHROUGH_INCOME_LINE = "122-L13"    # NOT depreciation — the trap

# Apportionment.
MS_RENTAL_PROPERTY_MULTIPLIER = 8   # 84-125 L1e; §402.09(1)(f) "eight times the net annual rental rate"
MS_APPORTIONMENT_DECIMALS = 4
MS_HAS_THROWBACK = True             # ⚠ 35 Miss. Admin. Code Pt.III §402.09(3)(b)(ii) and (vii)
MS_US_GOVT_SALES_ORIGIN_SOURCED = True   # §402.09(3)(c) — throwback in the OTHER direction

# Filing / e-file / penalties.
MS_DUE_DATE_RULE = "15th day of the 3rd month after the close of the accounting year"
MS_EFILE_K1_MANDATE_THRESHOLD = 100
MS_EFILE_ASSET_MANDATE_THRESHOLD = 250_000
MS_LATE_FILING_MIN_INCOME_TAX_PENALTY = 100
MS_INCOMPLETE_RETURN_PENALTY = 25
MS_INCOMPLETE_RETURN_PENALTY_MAX = 500

# Owner-side PTET credit landing lines (all verified off Form 80-161 / 84-161 faces).
# ⚠ A FIDUCIARY CANNOT ELECT BUT CAN RECEIVE — Form 81-110 line 8.
MS_PTET_OWNER_CREDIT_LANDING: dict[str, str] = {
    "individual_resident": "Form 80-105, page 1, line 26 (PAYMENTS block)",
    "individual_nonresident_or_part_year": "Form 80-205, page 1, line 28",
    "fiduciary": "Form 81-110, page 1, line 8  (cannot elect; CAN receive)",
    "business_pte": "Form 84-105, page 1, line 12",
    "business_corporation": "Form 83-105, page 1, line 12",
}
MS_PTET_ELECTION_FORM = "84-381"
MS_PTET_ELECTION_IS_BINDING_FORWARD = True
MS_PTET_ELECTION_BY_AMENDMENT = False   # "cannot be amended to make a pass-through entity election"
MS_PTET_VOTE_THRESHOLD_PCT = "0.50"     # greater than fifty percent of voting control
MS_PTET_FIDUCIARIES_MAY_ELECT = False


def _yk(d: dict, year: int):
    """Year-keyed lookup with a TY2025 fallback (matches the house helper)."""
    return d.get(year) if d.get(year) is not None else d[2025]


# ═══════════════════════════════════════════════════════════════════════════
# ARITHMETIC HELPERS — the oracles the validation harness exercises
# ═══════════════════════════════════════════════════════════════════════════

def _ms_franchise_tax(taxable_capital, tax_year: int = 2025) -> Decimal:
    """84-105 L2. MAX($25, rate x CEIL(MAX(0, capital - $100,000) / $1,000)).

    W8(a): the round-up-to-next-$1,000 already applied at 84-110 L18 and the
    statutory 'per $1,000, or fraction thereof' both point the same way; the
    CEIL here is the 'or fraction thereof'. Ken to bless.
    Repealed for tax years beginning on/after 1/1/2028 — no rate clause exists.
    """
    rate = MS_FRANCHISE_RATE_PER_1000.get(tax_year, "MISSING")
    if rate == "MISSING":
        raise ValueError(f"MS franchise rate not on the TY-keyed ladder for {tax_year}")
    if rate is None or tax_year >= MS_FRANCHISE_REPEAL_TAX_YEAR:
        return Decimal("0")     # repealed effective January 1, 2028
    excess = max(Decimal("0"), Decimal(str(taxable_capital)) - Decimal(MS_FRANCHISE_EXEMPT_CAPITAL))
    units = (excess / Decimal("1000")).to_integral_value(rounding=ROUND_CEILING)
    return max(Decimal(MS_FRANCHISE_MINIMUM), Decimal(rate) * units)


def _ms_entity_income_tax(taxable_income, tax_year: int = 2025) -> Decimal:
    """84-105 L6 for an ELECTING PTE — the SETTLED 0% / 4% / 5% schedule."""
    ti = max(Decimal("0"), Decimal(str(taxable_income)))
    tax, prior = Decimal("0"), Decimal("0")
    for top, rate in _yk(MS_ENTITY_RATES, tax_year):
        ceiling = ti if top is None else min(ti, Decimal(top))
        if ceiling > prior:
            tax += (ceiling - prior) * Decimal(rate)
        prior = ceiling
        if top is not None and ti <= Decimal(top):
            break
    return tax


def _ms_composite_tax(taxable_income, tax_year: int = 2025):
    """⚠ W1 / U1 — RETURNS None BY DESIGN. THREE-SIDED, UNRESOLVED, KEN'S CALL.

    DOR says 0/4/5 twice (TY2025-keyed); §27-7-5(1)(b) reduces the rate for
    individuals only and composite members ARE individuals; the official
    regulation packages the individual rate with the $5,000/10% deduction and the
    corporate rate with no deduction, and offers NO corporate-rate route for
    partnerships at all. The TY2025 forms take one half of each.
    v1 DIRECT-ENTERS 84-105 L6 for composite behind D_MS84105_COMPOSITE_RATE.
    DO NOT MAKE THIS FUNCTION RETURN A NUMBER WITHOUT A KEN RULING.
    """
    return None


def _ms_l9_total(entity_type: str, net_franchise_tax_l4, net_income_tax_l8) -> Decimal:
    """⚠ THE MODULE FORK. 84-105 L9 = L4 + L8 for an S corp; = L8 for a partnership.

    84-100 (Rev. 01/26) p.17, verbatim: 'S corporations, enter the amount from
    line 4; composite and electing pass-through entity S corporations, enter the
    amounts from line 4 plus line 8; and composite and electing pass-through
    entity partnerships, enter the amount from line 8.'
    """
    l4 = Decimal(str(net_franchise_tax_l4 or 0))
    l8 = Decimal(str(net_income_tax_l8 or 0))
    if entity_type == "1120S":
        return l4 + l8
    if entity_type == "1065":
        return l8       # franchise block is NOT APPLICABLE — hard-gated, never merely blank
    raise ValueError(f"MS_84_105 serves 1065 and 1120S only; got {entity_type!r}")


def _ms_franchise_block_applies(entity_type: str, *, elected_federal_corporate: bool = False,
                                is_exempt_org_with_ubti: bool = False) -> bool:
    """W2 hard gate on 84-105 L1-L4 (and Form 84-110)."""
    if elected_federal_corporate:
        return False    # not an 84-105 filer at all -> Form 83-105 (R15)
    if is_exempt_org_with_ubti:
        return False    # 'not subject to the franchise tax levy ... leave lines 1 through 4 blank'
    return entity_type == "1120S"


def _ms_safe_harbour(entity_type: str, filing_mode: str) -> dict:
    """⚠ [CORRECTED — verification pass] KEYED ON MODE x ENTITY, NOT ENTITY ALONE.

    Composite PARTNERSHIP  -> Form 80-320 L11: 80% current-year test, CALENDAR
                              quarters, interest only, NO 10% penalty component.
    Everything else        -> Form 83-305 L19: 90% current-year test, 4th/6th/9th/
                              12th-month instalments, 10% penalty + 1/2%/month.
    (84-105 face prints '(composite partnerships only)' against Form 80-320; the
    DOR EPTE FAQ 3/4/2024 puts partnerships AND S corporations on Form 83-305.)
    """
    if entity_type == "1065" and filing_mode == "composite":
        return dict(MS_SAFE_HARBOUR["80-320"])
    return dict(MS_SAFE_HARBOUR["83-305"])


def _ms_depreciation_lines(federal_special_allowance, ms_additional_depreciation) -> dict:
    """⚠ THE WHOLE POINT OF THIS SPEC. Returns the 84-122 lines the two amounts land on.

    L8  (+) federal §168(k) special depreciation allowance -> REMOVED from the MS base
    L15 (-) the extra MS depreciation that exists because Mississippi never reduced
            the asset's basis by the federal allowance -> MS keeps an UNREDUCED basis

    NOT L6 (municipal-bond interest). NOT L13 (flow-through income). Those are the
    Form 83-122 CORPORATE line numbers and putting these amounts there would be a
    silent wrong-box error on every MS PTE return carrying bonus depreciation.

    NOT a same-year wash: L15 recurs every year until the asset is fully recovered.
    """
    return {
        MS_84122_DEPRECIATION_ADDBACK_LINE: Decimal(str(federal_special_allowance or 0)),
        MS_84122_DEPRECIATION_RECOVERY_LINE: Decimal(str(ms_additional_depreciation or 0)),
    }


def _ms_bonus_rate(*, is_aviation_asset: bool,
                   acquired_on_or_after_2025_01_20: bool = True,
                   placed_in_service_on_or_after_2025_01_20: bool = True,
                   placed_in_service_after_2022_12_31: bool = True) -> str:
    """MS's own 100% bonus, WITH the statutory aviation branch (§27-7-17(1)(f)(i)).

    Aviation assets follow the FEDERAL rate — the one place OBBBA §168(k) reaches
    Mississippi cost recovery. Everything else gets MS's own permanent 100% for
    property placed in service after 12/31/2022, notwithstanding federal changes.
    """
    if is_aviation_asset and MS_AVIATION_FOLLOWS_FEDERAL:
        if acquired_on_or_after_2025_01_20 and placed_in_service_on_or_after_2025_01_20:
            return FED_OBBBA_FULL_BONUS_RATE
        return FED_OBBBA_PRIOR_BONUS_RATE
    return MS_OWN_BONUS_RATE if placed_in_service_after_2022_12_31 else "0.00"


def _ms_l20_overpayment(total_payments_l13, total_tax_l9, underestimate_l15) -> Decimal:
    """⚠ 84-105 L20 ASYMMETRY, encoded as WRITTEN, not as L13 - L19.

    Face: 'if line 13 is larger than line 9 plus line 15, subtract line 9 and line
    15 from line 13'. The underestimate interest/penalty (L15) IS netted against the
    refund; the LATE-PAYMENT items (L16-L18) are NOT.
    """
    l13 = Decimal(str(total_payments_l13 or 0))
    l9 = Decimal(str(total_tax_l9 or 0))
    l15 = Decimal(str(underestimate_l15 or 0))
    return max(Decimal("0"), l13 - l9 - l15) if l13 > (l9 + l15) else Decimal("0")


def _ms_84161_credit(total_pte_tax_paid_l3d, owner_total_tax_l4) -> dict:
    """Forms 84-161 / 80-161: L5 = MIN(L3D, L4); L6 = L3D - L5 (excess).

    Excess is CARRIED FORWARD AS AN OVERPAYMENT OR REFUNDED AT THE OWNER'S ELECTION
    (§27-7-26(1)(c), now statutory). The credit lands in the PAYMENTS block, never
    in the credits block, at EVERY level.
    """
    l3d = Decimal(str(total_pte_tax_paid_l3d or 0))
    l4 = Decimal(str(owner_total_tax_l4 or 0))
    l5 = min(l3d, l4)
    return {"L5_allowed": l5, "L6_excess": l3d - l5}


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY TOPICS / SOURCES
# ═══════════════════════════════════════════════════════════════════════════

AUTHORITY_TOPICS: list[tuple[str, str]] = [
    ("ms_pass_through_entity", "Mississippi Form 84-105: ONE return serving the 1065 and 1120S modules, with an "
     "S-corp-only franchise block (L1-L4), the 84-122 income engine, composite vs electing-PTE terminal blocks, "
     "and the 84-131/84-132 owner delivery of the PTET credit."),
    ("ms_franchise_tax", "Mississippi franchise tax on CAPITAL (§27-13-1 et seq.): TY-keyed rate ladder ($0.75 per "
     "$1,000 over $100,000 for TY2025), $25 minimum, its own property-and-receipts apportionment, an assessed-value "
     "floor, and repeal on January 1, 2028."),
    ("ms_apportionment_throwback", "Mississippi apportionment: industry-keyed formulas on Form 84-125 Part II, the "
     "x8 rental-property capitalization, and the SALES-FACTOR THROWBACK plus U.S. Government origin rule in "
     "35 Miss. Admin. Code Title 35 Part III §402.09."),
]

# The MS conformity anchor is already seeded by _state_conformity_tier1.py — the
# JurisdictionConformitySource row for MS TY2025 points at MS_CODE_27_7_17. Reference
# it; never redefine it here (this loader must not overwrite the conformity spine).
EXISTING_SOURCES_TO_REFERENCE: list[str] = [
    "MS_CODE_27_7_17",        # ⚠ THE MS CONFORMITY ANCHOR — own 100% bonus, aviation, §179 rolling, 1/1/2021 freeze
    "MS_2025_84_100_INSTR",   # FINAL TY2025 PTE booklet — the 0/4/5 rate, binding election, MS §179 K-1 box
    "MS_2025_83_100_INSTR",   # corporate booklet — ONLY for the five-factor pharmaceutical rule absent from 84-100
]

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "MS_2025_FORM_84_105",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "MS",
        "title": "2025 Mississippi Form 84-105 — Pass-Through Entity Tax Return",
        "citation": "Form 84-105-25-8-1..4-000 (Rev. 10/25), FINAL TY2025, ModDate 2025-10-08",
        "issuer": "Mississippi Department of Revenue",
        "official_url": "https://www.dor.ms.gov/sites/default/files/tax-forms/business/84105258.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["ms_pass_through_entity", "ms_franchise_tax"],
        "excerpts": [
            {
                "excerpt_label": "84-105 face — the three blocks and the module fork (verbatim, positional read)",
                "excerpt_text": (
                    "Header entity-type radio: 'Partnership / LLC / LLP (Federal 1065)' | 'S Corporation "
                    "(Federal 1120-S)'. CHECK ALL THAT APPLY: Electing Pass-Through Entity / Composite Return / "
                    "Amended Return / Final Return. CHECK ONE: 100% Mississippi / Multistate Apportioning / "
                    "Multistate Direct Accounting. || S CORPORATION FRANCHISE TAX: 1 Taxable capital (from Form "
                    "84-110, line 18); 2 Franchise tax (minimum tax $25) [with a Fee-In-Lieu checkbox]; 3 Franchise "
                    "tax credit (from Form 84-401, line 1); 4 Net franchise tax due (line 2 minus line 3). || "
                    "COMPOSITE / ELECTING PASS-THROUGH ENTITY INCOME TAX: 5 Mississippi net taxable income (from "
                    "Form 84-122, line 32 (composite) or line 35 (electing pass-through entity)); 6 Income tax; "
                    "7 Income tax credits (from Form 84-401, line 3); 8 Net income tax due (line 6 minus line 7). || "
                    "PAYMENTS AND TAX DUE: 9 Total franchise tax (S corporations only) and/or income tax (composite "
                    "or electing pass-through entity), (line 4 plus line 8); 10 Overpayments from prior year; "
                    "11 Estimated tax payments and payment with extension; 12 Credit for tax paid on an electing "
                    "Pass-Through Entity Tax Return (from Form (84-161, line 3D; must attach K-1(s) received from "
                    "electing pass-through entities); 13 Total payments (line 10 plus line 11 and line 12); 14 Net "
                    "total franchise tax and/or income tax (line 9 minus line 13); 15 Interest and penalty on "
                    "underestimated income tax payments (from Form 83-305, line 19 or Form 80-320, line 11 "
                    "(composite partnerships only), see instructions)); 16 Late payment interest; 17 Late payment "
                    "penalty; 18 Late filing penalty (minimum income tax penalty $100); 19 Total balance due (if "
                    "line 9 is larger than line 13, add line 14 through line 18); 20 Total overpayment (if line 13 "
                    "is larger than line 9 plus line 15, subtract line 9 and line 15 from line 13); 21 Overpayment "
                    "credited to next year (from line 20); 22 Overpayment to be refunded (line 20 minus line 21). || "
                    "Face notice: 'If issuing 100 or more K-1s, this return must be filed electronically.'"
                ),
                "summary_text": "84-105 face, 22 lines in three blocks. L1-L4 are S-CORP-ONLY franchise; L9 = L4+L8 "
                                "for S corps and = L8 for partnerships; L20 nets only L9 and L15, not L16-L18.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "84-100 p.17 L9 instruction — the module fork, verbatim",
                "excerpt_text": (
                    "Line 9: ... S corporations, enter the amount from line 4; composite and electing pass-through "
                    "entity S corporations, enter the amounts from line 4 plus line 8; and composite and electing "
                    "pass-through entity partnerships, enter the amount from line 8. || Line 2: Enter the amount of "
                    "franchise tax due. For tax year 2025, the franchise tax rate is $0.75 per $1,000 of capital in "
                    "excess of $100,000 (minimum tax of $25). || Line 4 / Line 8: If line 3 [7] equals or exceeds "
                    "the amount shown on line 2 [6], enter a zero. || Line 5: Mississippi net taxable income is only "
                    "entered on this line if the taxpayer is filing a composite or electing pass-through entity "
                    "return or is required to make a payment of tax because it failed to obtain an agreement from a "
                    "non-resident shareholder ... || Line 6: Composite or electing pass-through entities, enter the "
                    "amount of income tax due. For tax year 2025, the income tax rates are: 0% on the first $5,000 "
                    "of taxable income; 4% on the next $5,000 of taxable income; and 5% on taxable income in excess "
                    "of $10,000."
                ),
                "summary_text": "DOR states the L9 entity fork verbatim; TY2025 franchise $0.75/$1,000 over $100,000 "
                                "min $25; TY2025 income rate 0/4/5 keyed to the tax year.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Errata E2 / E3 — build to the FORM FACE",
                "excerpt_text": (
                    "E2: the L7 INSTRUCTION says 'Enter the total amount of credit claimed from Form 83-401, line 3' "
                    "while the FACE says 'Income tax credits (from Form 84-401, line 3)'. 83-401 is the CORPORATE "
                    "series — build to Form 84-401. || E3: the L19 INSTRUCTION says 'if line 10 is larger than line "
                    "13' while the FACE says 'if line 9 is larger than line 13'. L10 is prior-year overpayment and "
                    "the instruction's comparison is arithmetically meaningless — build to line 9."
                ),
                "summary_text": "Two of the five DOR errata live on the 84-105: the L7 credit-form cite and the L19 "
                                "balance-due trigger. Build to the face. (W7)",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MS_2025_FORM_84_122",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "MS",
        "title": "2025 Mississippi Form 84-122 — Net Taxable Income Schedule (the income engine)",
        "citation": "Form 84-122-25-8-1/2-000 (Rev. 10/25), FINAL TY2025, ModDate 2025-10-08",
        "issuer": "Mississippi Department of Revenue",
        "official_url": "https://www.dor.ms.gov/sites/default/files/tax-forms/business/84122258.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["ms_pass_through_entity"],
        "excerpts": [
            {
                "excerpt_label": "⚠ THE DEPRECIATION LINES — L8 and L15, verbatim off the FINAL face",
                "excerpt_text": (
                    "Line 6: 'Interest on obligations of other states or political subdivisions (net of expenses)' "
                    "— MUNICIPAL BOND INTEREST, NOT depreciation. || Line 13: 'Income (loss) from partnership, "
                    "S corporation or trust' — FLOW-THROUGH INCOME REMOVAL, NOT depreciation. || Line 8: 'Federal "
                    "special depreciation allowance' — THE ADD-BACK. || Line 15: 'Additional depreciation due to a "
                    "difference in the depreciable base for federal and state purposes (attach schedule)' — the "
                    "unreduced-Mississippi-basis RECOVERY. || L8 instruction: 'Federal Form 4562 must be completed "
                    "twice and attached immediately after Form 84-122. The first submission reflects the deductions "
                    "taken for federal income tax purposes. The second submission should be labeled \"Mississippi\" "
                    "at the top of the form ... Expenditures for business assets placed in service after December "
                    "31, 2022, are eligible for 100% bonus depreciation. Any difference between the two submissions "
                    "resulting from the special depreciation allowance is reported as an increase on this line. Any "
                    "additional depreciation expense, for purposes of this state, due to the basis adjustment not "
                    "being made is reported on LINE 15 of this form.' || L15 instruction: 'When a special "
                    "depreciation allowance is taken for federal tax purposes, the depreciable base must be reduced "
                    "by the amount of the allowance. Enter the additional depreciation expense for purposes of this "
                    "state due to the basis adjustment not being made for state purposes.' || Two election "
                    "checkboxes at the TOP of page 1: 'R&D Expense Election' and 'Bonus Depreciation Election'."
                ),
                "summary_text": "⚠ 84-122 L8 = federal special depreciation add-back; L15 = the MS unreduced-basis "
                                "recovery. L6 is muni-bond interest and L13 is flow-through income — those are the "
                                "83-122 CORPORATE numbers and coding them here is a silent wrong-box error.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "84-122 face — 35 lines, five blocks (verbatim labels)",
                "excerpt_text": (
                    "FEDERAL TAXABLE INCOME 1-4: 1 Ordinary business income (loss) (from federal Form 1120S, page 1, "
                    "line 22 or federal Form 1065, page 1, line 23. If multistate direct accounting, enter zero and "
                    "skip to line 25); 2 Total federal Schedule K income (1120S p.3 Sch K lines 2-10 / 1065 p.5 Sch "
                    "K lines 2-11); 3 Total federal Schedule K deductions (1120S lines 11-12e / 1065 lines 12-13e); "
                    "4 Total federal business income (loss) (line 1 plus line 2 minus line 3). || STATE ADDITIONS "
                    "5-10: 5 State, local or foreign government taxes based on income; 6 Interest on obligations of "
                    "other states; 7 Depletion expense in excess of cost; 8 Federal special depreciation allowance; "
                    "9 Other additions required by law; 10 Total additions. || STATE DEDUCTIONS 11-17: 11 Interest "
                    "on obligations of the United States; 12 Wages reduced for federal employment tax credits; "
                    "13 Income (loss) from partnership, S corporation or trust; 14 Income (loss) from construction "
                    "contracting or production of natural mineral resource products; 15 Additional depreciation due "
                    "to a difference in the depreciable base; 16 Other deductions; 17 Total deductions. || "
                    "APPORTIONMENT/ALLOCATION 18-28: 18 Adjusted federal income (line 4 plus line 10 minus line 17); "
                    "19 Adjustment for nonbusiness income (84-150 col E line 2); 20 Apportionable business income "
                    "(18-19); 21 Apportionment ratio (84-125 Part II); 22 Mississippi apportioned income (if 100% "
                    "Mississippi, enter line 18, otherwise multiply line 20 by line 21); 23 Nonbusiness income "
                    "allocated to Mississippi (84-150 col F line 2); 24 Mississippi income from partnership, S corp "
                    "or trust; 25 Mississippi income from construction contracting or mineral production (84-124); "
                    "26 Other adjustments required by law; 27 Income exemption; 28 Total income apportioned and "
                    "directly allocated to Mississippi (ADD LINE 22 THROUGH LINE 26 MINUS LINE 27). || COMPOSITE "
                    "29-32: 29 Mississippi composite net income (from Form 84-131 line 4a); 30 Composite return "
                    "filing adjustment (attach schedule); 31 Less Mississippi composite net operating loss deduction "
                    "(84-155 line 2); 32 Mississippi composite net taxable income (29 minus 30 and 31; If negative, "
                    "enter zero on Form 84-105, line 5). || ELECTING PTE 33-35: 33 Total Mississippi net income "
                    "(from line 28); 34 Less Mississippi electing pass-through entity net operating loss deduction "
                    "(84-155 line 2); 35 Mississippi net taxable income (33 minus 34; If negative, enter zero)."
                ),
                "summary_text": "The engine: federal start (L1-L4), additions (L5-L10), deductions (L11-L17), "
                                "apportionment (L18-L28), then TWO terminal blocks — composite L29-L32 and electing "
                                "PTE L33-L35 — each with a zero floor onto 84-105 L5.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Errata E1 / E4 / E5, and the L2 capital-loss limiter",
                "excerpt_text": (
                    "E4: the L28 INSTRUCTION says 'sum lines 22 through 27'; the FACE says 'add line 22 through line "
                    "26 minus line 27'. L27 is an EXEMPTION, so the face is arithmetically right — build to the "
                    "face. || E5: the L1 INSTRUCTION says 'taxable income (loss) (before net operating loss and "
                    "special deductions)' — that is Form 1120 line 28 boilerplate; the FACE cites 1120-S line 22 / "
                    "1065 line 23 and is correct. || E1: the 84-132 Box 1 instruction cites '1120S page 1 line 21' "
                    "and '1065 page 1 line 22' — BOTH are 'Total deductions' on the FINAL 2025 IRS forms. Build "
                    "84-132 Box 1 to the SAME federal lines as 84-122 line 1. || L2 limiter, instruction only: "
                    "'Long term and short-term capital losses are included only to the extent of current year "
                    "capital gains.' || L13 and L14 are REMOVAL lines: flow-through income comes back, already "
                    "sourced, at L24; direct-accounting lines of business come back at L25."
                ),
                "summary_text": "Three of the five DOR errata live on the 84-122. Plus the instruction-only "
                                "capital-loss limiter at L2 and the L13/L14 removal-and-reinsertion architecture.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MS_2025_FORM_84_110",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "MS",
        "title": "2025 Mississippi Form 84-110 — S-Corporation Franchise Tax Schedule (capital base)",
        "citation": "Form 84-110-25-8-1-000 (Rev. 10/25), FINAL TY2025, ModDate 2025-10-08",
        "issuer": "Mississippi Department of Revenue",
        "official_url": "https://www.dor.ms.gov/sites/default/files/tax-forms/business/84110258.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["ms_franchise_tax"],
        "excerpts": [
            {
                "excerpt_label": "84-110 face — capital base, its OWN apportionment, the assessed-value floor",
                "excerpt_text": (
                    "CAPITAL BASE: 1 Capital stock; 2 Paid in capital; 3 Surplus and retained earnings; 4 Loans from "
                    "shareholders or affiliates; 5 Deferred taxes, contingent liabilities, all true reserves and "
                    "other elements; 6 Less treasury stock; 7 Holding company exclusion; 8 Total capital base (add "
                    "line 1 through line 7). || APPORTIONMENT RATIO (A MISSISSIPPI / B EVERYWHERE): 9 Real and "
                    "tangible personal property owned at year end (net book value); 10 Gross receipts; 11 Total "
                    "(line 9 plus line 10); 12 Mississippi ratio (line 11A divided by line 11B); 13 Taxable capital "
                    "apportioned to Mississippi (line 8 multiplied by line 12. If 100% Mississippi enter amount from "
                    "line 8). || TAXABLE CAPITAL: 14 Total assessed value of Mississippi property; 15 Taxable "
                    "capital (ENTER THE LARGER OF LINE 13 OR LINE 14); 16 Prorate (except for initial return; if "
                    "period is less than twelve months, multiply line 15 by the number of months covered by the "
                    "return and divide by twelve); 17 Capital exemption; 18 Final taxable capital (line 15 or line "
                    "16 minus line 17; ROUND AMOUNT UP TO THE NEXT HIGHEST $1,000 and enter amount on Form 84-105, "
                    "line 1. If negative, enter zero on Form 84-105, line 1)."
                ),
                "summary_text": "The franchise capital base and a SECOND, different apportionment engine (property + "
                                "gross receipts), an assessed-value FLOOR from the prior year's county ad valorem "
                                "roll, and a round-up to the next $1,000 before the rate applies. ⚠ U16: L6/L7 sign "
                                "convention inside 'add line 1 through line 7' is not stated — assumed subtractive.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MS_2025_FORM_84_125",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "MS",
        "title": "2025 Mississippi Form 84-125 — Business Income Apportionment Schedule",
        "citation": "Form 84-125-25-8-1-000 (Rev. 10/25), FINAL TY2025, ModDate 2025-10-08",
        "issuer": "Mississippi Department of Revenue",
        "official_url": "https://www.dor.ms.gov/sites/default/files/tax-forms/business/84125258.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["ms_apportionment_throwback"],
        "excerpts": [
            {
                "excerpt_label": "84-125 Part I + Part II — the four industry-keyed formulas (CHECK ONE)",
                "excerpt_text": (
                    "Part I (columns A Total Mississippi / B Total Everywhere / C Mississippi Ratio, four decimal "
                    "places): 1a Beginning of taxable year; 1b End of taxable year; 1c Total; 1d Average net book "
                    "value of assets (divide line 1c by two); 1e RENTAL PROPERTY (ENTER ANNUAL RENTAL PROPERTY "
                    "MULTIPLIED BY EIGHT); 1f Total (1d plus 1e); 1g Mississippi property factor; 2 Payroll factor; "
                    "3 Sales factor. || Part II APPLICATION OF APPORTIONMENT FACTORS (CHECK ONE): line 4 "
                    "'Retailing, renting, servicing, merchandising or wholesaling' = SINGLE SALES FACTOR; lines "
                    "5a-5g 'Manufacturers that sell principally at retail' = 5g Weighted average (divide line 5f by "
                    "two), i.e. ((property + payroll)/2 + sales)/2; lines 6a-6e 'Financial institutions, pipelines "
                    "or manufacturers that sell principally at wholesale (for major medical or pharmaceutical "
                    "suppliers, see instructions Form 84-100)' = 6e Average (divide line 6d by three); line 7 "
                    "'Airlines, motor carriers, express companies, telephone and telegraph companies' = Special "
                    "formula required (attach schedule). Each of 4, 5g, 6e and 7 carries '(enter ratio on Form "
                    "84-122, line 21)'."
                ),
                "summary_text": "Four boxes: single sales factor; manufacturer-retail weighted average; "
                                "equal-weighted three-factor; special formula. Rental property capitalized at 8x.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MS_ADMIN_CODE_35_PT3",
        "source_type": "state_regulation",
        "source_rank": "controlling",
        "jurisdiction_code": "MS",
        "title": "35 Miss. Admin. Code Title 35, Part III — Income and Franchise Tax (official SOS capture)",
        "citation": "35 Miss. Admin. Code Pt. III §§202.06, 402.01-402.10, §112.03 and the Composite Returns chapter; "
                    "official Mississippi Secretary of State ACCode capture, 123 pp., ModDate 2026-05-26",
        "issuer": "Mississippi Secretary of State (official Administrative Code)",
        "official_url": "https://www.sos.ms.gov/adminsearch/ACCode/00000158c.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.6,
        "topics": ["ms_apportionment_throwback", "ms_pass_through_entity"],
        "excerpts": [
            {
                "excerpt_label": "⚠ §402.09(3)(b) — THE THROWBACK RULE, verbatim from the OFFICIAL text",
                "excerpt_text": (
                    "SALES OF TANGIBLE PERSONAL PROPERTY ARE IN THIS STATE. Gross receipts from sales of tangible "
                    "personal property (except sale to the United States Government) are in this state: i. If the "
                    "property is delivered or shipped to a purchase, within this state regardless of the f. o. b. "
                    "point or other conditions of sale, or ii. IF THE PROPERTY IS SHIPPED FROM AN OFFICE, STORE, "
                    "WAREHOUSE, FACTORY, OR OTHER PLACE OF STORAGE IN THIS STATE AND THE TAXPAYER IS NOT TAXABLE IN "
                    "THE STATE OF THE PURCHASER. iii. Property shall be deemed to be delivered or shipped to a "
                    "purchaser within this state if the recipient is located in this state, even though the property "
                    "is ordered from outside this state. iv. Property is delivered or shipped to a purchaser within "
                    "the state if the shipment terminates in this state, even though the property is subsequently "
                    "transferred by the purchaser to another state. v. The term 'purchaser within this state' shall "
                    "include the ultimate recipient of the property ... vi. When the property being shipped by a "
                    "seller from the state of origin to a consignee in another state is diverted while en route to a "
                    "purchaser in this state, the sales are in this state. vii. IF THE TAXPAYER IS NOT TAXABLE IN "
                    "THE STATE OF THE PURCHASER, THE SALE IS ATTRIBUTED TO THIS STATE IF THE PROPERTY IS SHIPPED "
                    "FROM AN OFFICE, STORE, WAREHOUSE, FACTORY, OR OTHER PLACE OF STORAGE IN THIS STATE. viii. If a "
                    "taxpayer, whose salesman operates from an office located in this state, makes a sale to a "
                    "purchaser in another state in which the taxpayer is not taxable, and the property shipped "
                    "directly by a third party to the purchaser: if the taxpayer is taxable in the state from which "
                    "the third party ships the property, then the sale is in such state; if the taxpayer is not "
                    "taxable in the state from which the property is shipped, then the sale is in this state. || "
                    "§402.09(3)(c): Gross receipts from the sales of tangible personal property to the United States "
                    "Government are in this state IF THE PROPERTY IS SHIPPED FROM AN OFFICE, STORE, WAREHOUSE, "
                    "FACTORY, OR OTHER PLACE OF STORAGE IN THIS STATE. || §202.06: 'Jurisdiction to tax is not "
                    "present when the state is prohibited from imposing the tax by reason of the provisions of "
                    "Public Law 86-272.'"
                ),
                "summary_text": "⚠ MISSISSIPPI HAS A THROWBACK RULE, and P.L. 86-272 protection in the destination "
                                "state triggers it. U.S. Government sales are ORIGIN-sourced unconditionally.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "⚠ §112.03 + Composite Returns — POSITION C in the composite-rate conflict",
                "excerpt_text": (
                    "S corporations, §112.03: 'If a composite return is filed, the S corporation return is completed "
                    "like any other S corporation return, but an additional schedule is attached ... The S "
                    "corporation then pays the tax on this income AT THE REGULAR CORPORATE RATE. If the S "
                    "corporation wants a deduction for the individual's personal exemptions and standard deductions, "
                    "then instead of paying tax on the corporate return, the composite return income is reported on "
                    "ONE NONRESIDENT INDIVIDUAL RETURN under the S corporations name and identification number. On "
                    "this return, the corporation is allowed to deduct 10% of the adjusted gross income of the "
                    "nonresident individuals reported on this return up to a maximum of $5,000 per composite "
                    "return.' || Partnerships, Composite Returns chapter paragraphs 3-4: '...The partnership then "
                    "files a NONRESIDENT INDIVIDUAL RETURN under the partnership name and identification number in "
                    "which it includes the composite income. The partnership is allowed to deduct 10% of adjusted "
                    "gross income not to exceed $5,000 per composite return...' — NO CORPORATE-RATE ALTERNATIVE IS "
                    "OFFERED FOR PARTNERSHIPS AT ALL (confirmed by full enumeration of all 18 'composite' hits in "
                    "the 123-page official text). || §402.07 PIPELINES: 'the numerator of which is the property "
                    "factor plus the payroll factor ... plus the TRAFFIC MILES FACTOR, and the denominator ... three "
                    "(3)' — DIFFERENT from Form 84-125 line 6. || Full-text search: NO financial-institution "
                    "apportionment formula exists anywhere in Part III."
                ),
                "summary_text": "⚠ The regulation makes the $5,000/10% deduction and the INDIVIDUAL rate one package, "
                                "and the corporate rate with NO deduction a different package. The TY2025 forms take "
                                "one half of each. Also: the pipeline formula diverges and no FI formula exists.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MS_CODE_27_13_5",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "MS",
        "title": "Miss. Code Ann. §27-13-5 — Corporation franchise tax rate ladder, $25 minimum, 2028 repeal",
        "citation": "Miss. Code Ann. §27-13-5(1)(a)(ix)-(xi), (1)(b), (3)(a), (4); §27-13-7; SB 2858 (2016 Reg. Sess.)",
        "issuer": "Mississippi Legislature",
        "official_url": "https://codes.findlaw.com/ms/title-27-taxation-and-finance/ms-code-sect-27-13-5/",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.2,
        "topics": ["ms_franchise_tax"],
        "excerpts": [
            {
                "excerpt_label": "TY-keyed franchise ladder + minimum + repeal",
                "excerpt_text": (
                    "§27-13-5(1)(a)(ix): 'For tax years beginning on or after January 1, 2025, but before January 1, "
                    "2026, SEVENTY-FIVE CENTS (75c) for each One Thousand Dollars ($1,000.00), or fraction thereof, "
                    "IN EXCESS OF One Hundred Thousand Dollars ($100,000.00), of the value of the capital used, "
                    "invested or employed...' (x) 2026 = 50c; (xi) 2027 = 25c, 'but before January 1, 2028'; NO "
                    "CLAUSE EXISTS FOR 2028 OR LATER. || §27-13-5(1)(b): 'In no case shall the franchise tax due for "
                    "the accounting period be less than Twenty-five Dollars ($25.00).' || DOR phase-out table "
                    "(84-100 p.3): 2020 $2.00 / 2021 $1.75 / 2022 $1.50 / 2023 $1.25 / 2024 $1.00 / 2025 $0.75 / "
                    "2026 $0.50 / 2027 $0.25 / 2028 Franchise tax REPEALED effective January 1, 2028. || The levy "
                    "reaches 'every corporation, association or joint-stock company OR PARTNERSHIP TREATED AS A "
                    "CORPORATION UNDER THE INCOME TAX LAWS OR REGULATIONS' — the one crack in 'partnerships never "
                    "pay franchise tax'. || Fee-in-lieu projects (§27-13-5(3)(a)) are exempt from the ordinary levy "
                    "and get a SINGLE-SALES-FACTOR franchise apportionment instead."
                ),
                "summary_text": "TY2025 = $0.75 per $1,000 over $100,000, $25 floor, repealed 1/1/2028. Rate MUST be "
                                "a TY-keyed table with a sunset, never a constant.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MS_CODE_27_7_26_PTET",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "MS",
        "title": "Miss. Code Ann. §27-7-26 — the elective entity-level pass-through entity tax (PTET)",
        "citation": "Miss. Code Ann. §27-7-26(1)(b), (1)(c), current codified text; enacted as HB 1691 §1 (2022 Reg. Sess.)",
        "issuer": "Mississippi Legislature",
        "official_url": "https://billstatus.ls.state.ms.us/documents/2022/html/HB/1600-1699/HB1691SG.htm",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.3,
        "topics": ["ms_pass_through_entity"],
        "excerpts": [
            {
                "excerpt_label": "⚠ BINDING FOREVER, and the owner side is a CREDIT — income REPORTED, not excluded",
                "excerpt_text": (
                    "§27-7-26(1)(b): the entity 'shall submit the appropriate form to the department at any time "
                    "during the tax year for which the entity elects to be taxed as an electing pass-through entity, "
                    "or by the due date of the return for that tax year, or by the date such return is filed, "
                    "whichever is latest.' 'The election shall be binding for the taxable year and ALL SUBSEQUENT "
                    "TAXABLE YEARS unless the election is revoked by the electing PTE.' || §27-7-26(1)(c) CURRENT "
                    "CODIFIED TEXT (the 2022 enrolled 'shall not be liable' clause is GONE): 'Each owner, member, "
                    "partner or shareholder of an electing pass-through entity SHALL REPORT his or her pro rata or "
                    "distributive share of the income of the electing pass-through entity, AND SUCH SHARE SHALL BE "
                    "USED IN COMPUTING THE TAXPAYER'S GROSS INCOME TAX LIABILITY. Each owner ... SHALL BE ALLOWED A "
                    "CREDIT against the taxes imposed under this chapter in an amount equal to his or her pro rata "
                    "or distributive share of tax paid by the electing pass-through entity ... In the event an "
                    "owner's ... aggregate credits shall exceed his or her income tax liability, such excess shall "
                    "be CARRIED FORWARD AS AN OVERPAYMENT OR REFUNDED AT THE ELECTION OF SUCH PERSON.' || HB 1691 "
                    "§1(2): 'The adjusted basis of the owners, members or partners ... shall be calculated WITHOUT "
                    "REGARD to the election under this section.'"
                ),
                "summary_text": "PTET election is binding for the year and every later year until revoked. Owner "
                                "REPORTS the income and takes a CREDIT (in the PAYMENTS block); excess is refundable "
                                "or carried forward at the owner's election. Basis computed as if no election.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MS_2025_FORM_84_381",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "MS",
        "title": "2025 Mississippi Form 84-381 — Pass-Through Entity Election Form (election / revocation)",
        "citation": "Form 84-381-25-8-1-000 (Rev. 10/25), FINAL TY2025, ModDate 2025-10-08",
        "issuer": "Mississippi Department of Revenue",
        "official_url": "https://www.dor.ms.gov/sites/default/files/tax-forms/business/84381258.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["ms_pass_through_entity"],
        "excerpts": [
            {
                "excerpt_label": "84-381 printed INSTRUCTIONS block + the vote attestation, verbatim",
                "excerpt_text": (
                    "'Complete this form to make an election to pay taxes at the entity level (\"Electing PTE\") or "
                    "to revoke a previous election made. THE \"ELECTING PTE\" STATUS SHALL BE VALID FOR THE CURRENT "
                    "TAXABLE YEAR AND EACH TAXABLE YEAR THEREAFTER UNTIL THE ELECTION IS REVOKED. Elections and "
                    "revocations must be made by the due date or the extended due date of the Pass-Through Entity "
                    "Tax Return of the taxable year, or by the date such return is filed, whichever is latest ... "
                    "The effective date of the election or revocation must be provided on this form. Prior to "
                    "submitting this form, a vote by or written consent of the members of the governing body of the "
                    "entity, as well as, a vote by or written consent of the owners, members, partners or "
                    "shareholders holding GREATER THAN FIFTY PERCENT (50%) of the voting control of the entity must "
                    "be obtained in order to be taxed as an electing PTE.' || Face fields: CHECK ONE: Electing PTE | "
                    "Removing PTE; Effective date (mm dd yyyy); Total Number of Owners/Partners; RESPONSIBLE PARTY "
                    "block; the vote-threshold attestation checkbox; officer signature + paid-preparer block. || DOR "
                    "EPTE FAQs (3/4/2024): 'ONCE THE PASS-THROUGH ENTITY RETURN IS FILED, IT CANNOT BE AMENDED TO "
                    "MAKE A PASS-THROUGH ENTITY ELECTION.' 'Annual filings of the election form are not required.' "
                    "'Fiduciaries are not eligible for this election.' 'A partnership, S Corporation or other "
                    "similar pass-through entity that owns an electing pass-through entity IS NOT REQUIRED TO MAKE "
                    "AN ELECTION to be able to claim or utilize the credit for taxes paid on the Electing "
                    "Pass-Through Entity Return.'"
                ),
                "summary_text": "⚠ W9. Separate form, not a return checkbox. Binding for the year and every later "
                                "year. Cannot be made retroactively by amending. Requires a >50% governance vote. "
                                "Fiduciaries cannot elect. Tiering works without an upper-tier election.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MS_2025_FORM_84_161",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "MS",
        "title": "2025 Mississippi Forms 84-161 / 80-161 — Tax Credit For Income Tax Paid By Electing PTE",
        "citation": "Form 84-161-25-8-1/2-000 (Rev. 10/25) and Form 80-161-25-8-1/2-000 (Rev. 09/25), FINAL TY2025",
        "issuer": "Mississippi Department of Revenue",
        "official_url": "https://www.dor.ms.gov/sites/default/files/tax-forms/business/84161258.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["ms_pass_through_entity"],
        "excerpts": [
            {
                "excerpt_label": "⚠ Owner-side landing lines — including a filer type that CANNOT elect",
                "excerpt_text": (
                    "Form 80-161 line 3D, verbatim off the face: 'Total Mississippi taxable income (line 1C plus "
                    "line 2C) and amount of taxes paid on pass-through entity returns (line 1D plus line 2D). "
                    "Include amount from line 3D on Form 80-105, page 1, line 26 or From 80-205, page 1, line 28; or "
                    "FORM 81-110, PAGE 1, LINE 8' (the 'From 80-205' typo is on the face). || Form 84-161 line 3D "
                    "-> 'Form 83-105, page 1, line 12 or Form 84-105, page 1, line 12'. || BOTH forms: L4 = the "
                    "owner's total Mississippi income tax due; L5 = 'the lesser of line 3D or line 4'; L6 = 'Excess "
                    "credit for tax paid on an electing Pass-Through Entity Return (line 3D minus line 5)'. || "
                    "⚠ A FIDUCIARY CANNOT MAKE THE ELECTION BUT CAN RECEIVE THE CREDIT — Form 81-110 line 8. || "
                    "Attachment gate on both faces: 'The Mississippi K-1(s) you received from electing pass-through "
                    "entities must be attached to the return.'"
                ),
                "summary_text": "The PTET credit lands in the PAYMENTS block at every level: 80-105 L26, 80-205 L28, "
                                "81-110 L8 (fiduciary — cannot elect, CAN receive), 84-105 L12, 83-105 L12. "
                                "L5 = MIN(L3D, L4); L6 = the excess.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MS_2025_FORM_83305_80320",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "MS",
        "title": "2025 Mississippi Forms 83-305 and 80-320 — the two underestimate worksheets",
        "citation": "Form 83-305-25-8-1-000 (Rev. 10/25) Underestimate of Corporate Income Tax Worksheet; "
                    "Form 80-320-25-8-1/2/3-000 (Rev. 09/25) Individual Income Tax Interest and Penalty Worksheet",
        "issuer": "Mississippi Department of Revenue",
        "official_url": "https://www.dor.ms.gov/sites/default/files/tax-forms/business/83305258.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["ms_pass_through_entity"],
        "excerpts": [
            {
                "excerpt_label": "⚠ [CORRECTED — verification pass] TWO DIFFERENT SAFE HARBOURS, keyed MODE x ENTITY",
                "excerpt_text": (
                    "Form 83-305 (reached by S CORPORATIONS in either mode AND by ELECTING-PTE PARTNERSHIPS): L1 "
                    "'Current year income tax due (from Form 83-105, line 8 (corporations) or Form 84-105, line 8 "
                    "(composite S corporations and electing pass-through entities))'; L2 'NINETY (90%) of current "
                    "year income tax due (multiply line 1 by 90%)'; L4 lesser of L2 or L3 (except for large "
                    "corporations); L5 'divide line 4 by four'; Part II columns '15th of 4th Month / 6th / 9th / "
                    "12th Month'; L11 'multiply line 10 by 10%'; L15 interest '5/10 of 1% per month'; L19 -> Form "
                    "84-105, page 1, line 15. Face checkboxes: 'Annualized Income Method' and 'Amended'. || "
                    "Form 80-320 (reached ONLY by a COMPOSITE PARTNERSHIP — the 84-105 face prints '(composite "
                    "partnerships only)'): L2 'MULTIPLY THE AMOUNT ON LINE 1 BY 80% and enter the result'; L3 '2024 "
                    "Mississippi income tax liability'; L5 'Enter 1/4th (.25) of line 4'; columns 'Apr. 15, 2025 / "
                    "June 15, 2025 / Sept. 15, 2025 / Jan. 15, 2026' (CALENDAR-keyed); L9/L10 interest only, '1/2% "
                    "per month' — NO 10% PENALTY COMPONENT; L11 -> 84-105 line 15. || DOR EPTE FAQ (3/4/2024): "
                    "'Underestimate interest and penalty for PARTNERSHIPS and S corporations or other similar "
                    "pass-through entities should be calculated using Form 83-305.'"
                ),
                "summary_text": "⚠ A composite partnership computes on an 80% current-year safe harbour, on CALENDAR "
                                "quarters, with NO 10% penalty — three differences from every other filer on this "
                                "form. Do NOT code one underestimate routine.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MS_2025_FORM_84_115",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "MS",
        "title": "2025 Mississippi Form 84-115 (MS8453-PTE) — PTE Declaration for Electronic Filing",
        "citation": "Form 84-115 MS8453-PTE (Rev. 10/25), FINAL TY2025, ModDate 2025-10-08, 1 p.",
        "issuer": "Mississippi Department of Revenue",
        "official_url": "https://www.dor.ms.gov/sites/default/files/tax-forms/business/84115258.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["ms_pass_through_entity"],
        "excerpts": [
            {
                "excerpt_label": "⚠ [ADDED — verification pass] Part I: seven computed tie-outs against Form 84-105",
                "excerpt_text": (
                    "1 'Mississippi taxable income (Form 84-105, line 5)'; 2 'Total income tax (Form 84-105, line "
                    "6)'; 3 'Total credits and payments (Form 84-105, line 7 and line 13)'; 4 'Amount you owe (Form "
                    "84-105, line 19)'; 5 'Overpayment (Form 84-105, line 20)'; 6 'Refund (Form 84-105, line 22)'; "
                    "7 'Amount of payment remitted electronically'. || Face: 'DO NOT MAIL THIS DOCUMENT TO THE "
                    "DEPARTMENT OF REVENUE' / 'This declaration is to be maintained by the ERO and provided to DOR "
                    "on request.' Part II Declaration of Officer; Part III ERO / Paid Preparer declarations "
                    "referencing IRS Pub. 3112 and Pub. 4163 (the MeF piggyback made explicit on a form face). || "
                    "It appears as its OWN COLUMN on the DOR's TY2025 approved-provider matrix, so a vendor's "
                    "product is approved for it SEPARATELY — it is not optional."
                ),
                "summary_text": "The MS e-file signature declaration the research pass missed entirely. Seven "
                                "computed tie-out lines against 84-105, print-and-retain, separately approval-gated.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MS_2025_FORM_84_131_132",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "MS",
        "title": "2025 Mississippi Forms 84-131 (Schedule K) and 84-132 (Mississippi Schedule K-1)",
        "citation": "Form 84-131-25-8-1/2-000 (Rev. 10/25) and Form 84-132-25-8-1-000 (Rev 10/25), FINAL TY2025",
        "issuer": "Mississippi Department of Revenue",
        "official_url": "https://www.dor.ms.gov/sites/default/files/tax-forms/business/84131258.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["ms_pass_through_entity"],
        "excerpts": [
            {
                "excerpt_label": "84-131 owner grid and 84-132 Part V — how the PTET credit reaches owners",
                "excerpt_text": (
                    "84-131: Column A name/FEIN-SSN/state of residence; Column B OWNERSHIP % TO THE FOURTH DECIMAL "
                    "PLACE with a per-owner COMPOSITE checkbox; Column C a Mississippi taxable income (loss) / b "
                    "credit code / c credit amount; Column D 'TAX PAID BY ELECTING PASS-THROUGH ENTITY'. Totals L2 + "
                    "L3 -> L4 (Column B 'must total 100%'; Column C line 4a -> 84-122 line 29 for composite) and L5 "
                    "'Total tax paid by electing pass-through entity (column D, line 2 plus line 3)'. || 84-100 "
                    "p.23: 'The amount of tax credit paid is equal to the partner's pro rata or distributive share "
                    "of the tax paid ON FORM 84-105, LINE 8 by the electing PTE for the corresponding taxable "
                    "year.' || 84-132: Part V 'If the election was made to be taxed as an electing pass-through "
                    "entity, enter the amount of tax paid by the electing pass-through entity on the partner's share "
                    "of income'; Part IV Mississippi tax credits from Form 84-401; Box G 'Check box if 5% of the net "
                    "gain / profit was remitted as an estimated tax payment for the partner on Form 84-387'; Box 12 "
                    "charitable contributions 'limited to 20% of the entity's current year taxable income', no "
                    "carryover; Box 13 'Enter the owner's share of MISSISSIPPI Section 179 deduction'; Boxes "
                    "4a/4b/4c guaranteed payments 'Applicable to partnerships only'; line J stock-ownership % for "
                    "S corps instead of profit/loss/capital."
                ),
                "summary_text": "84-131 Column D = 84-105 L8 x ownership%; 84-132 Part V delivers it per owner. "
                                "Composite base comes off 84-131 line 4a (only owners with the COMPOSITE box "
                                "checked), which is why the composite base is SMALLER than the EPTE base (= L28).",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MS_2025_PTE_APPROVED_PROVIDERS",
        "source_type": "state_vendor_guide",
        "source_rank": "implementation_official",
        "jurisdiction_code": "MS",
        "title": "MS DOR — Approved Paper Form Providers, Pass Through Entity Tax Returns, Tax Year 2025",
        "citation": "2025PTEApprovedProvidersRev2.4.26.pdf, Last Updated 2/4/2026, ModDate 2026-02-12",
        "issuer": "Mississippi Department of Revenue",
        "official_url": "https://www.dor.ms.gov/sites/default/files/business/2025PTEApprovedProvidersRev2.4.26.pdf",
        "current_status": "active",
        "is_filing_authority": True,
        "trust_score": 9.0,
        "topics": ["ms_pass_through_entity"],
        "excerpts": [
            {
                "excerpt_label": "⚠ U17 — the approval gate, its 16 forms, and its lead time",
                "excerpt_text": (
                    "A per-vendor x per-form MATRIX: 26 named vendors (CCH, Thomson Reuters, Drake, Corptax, Intuit "
                    "Lacerte, Intuit ProSeries Business, Bloomberg STF, TaxWise, TaxAct, TaxSlayer, ATX, CrossLink, "
                    "...) x 16 forms: 84-105, 84-110, 84-115, 84-122, 84-124, 84-125, 84-131, 84-132, 84-150, "
                    "84-155, 84-161, 84-300, 84-380, 84-381, 84-387, 84-401. Every cell is an APPROVAL DATE, PER "
                    "FORM. Legend: 'Form is not supported by provider' / '** Dates indicate the approval date **' / "
                    "'Blanks indicate form has not been submitted for review'. TY2025 approval dates run 2025-11-07 "
                    "through 2026-02-04, clustering in December 2025. Partial approval is normal and visible. || "
                    "STILL OPEN: this is the PAPER-FORM program. The MeF/e-file handbook, the Letter of Intent, and "
                    "the ATS/test window remain UNPUBLISHED. Mississippi piggybacks federal MeF for 1120/1065 and "
                    "'requires all participants to be accepted into the Federal program'. Corporate/PTE returns "
                    "CANNOT be filed through TAP, though Form 84-381 alone CAN. Contact: efile@dor.ms.gov / "
                    "(601) 923-7700."
                ),
                "summary_text": "⚠ Ken-only, lead-time-bearing. Forms are submitted for review from ~November and "
                                "approved on a rolling per-form basis into February. 84-115 has its own column.",
                "is_key_excerpt": True,
            },
        ],
    },
]

AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    ("MS_2025_FORM_84_105", "MS_84_105", "governs"),
    ("MS_2025_FORM_84_122", "MS_84_105", "governs"),
    ("MS_2025_FORM_84_110", "MS_84_105", "governs"),
    ("MS_2025_FORM_84_125", "MS_84_105", "governs"),
    ("MS_2025_FORM_84_381", "MS_84_105", "governs"),
    ("MS_2025_FORM_84_161", "MS_84_105", "governs"),
    ("MS_2025_FORM_84_115", "MS_84_105", "governs"),
    ("MS_2025_FORM_84_131_132", "MS_84_105", "governs"),
    ("MS_2025_FORM_83305_80320", "MS_84_105", "informs"),
    ("MS_ADMIN_CODE_35_PT3", "MS_84_105", "governs"),
    ("MS_CODE_27_13_5", "MS_84_105", "governs"),
    ("MS_CODE_27_7_26_PTET", "MS_84_105", "governs"),
    ("MS_CODE_27_7_17", "MS_84_105", "governs"),
    ("MS_2025_84_100_INSTR", "MS_84_105", "governs"),
    ("MS_2025_PTE_APPROVED_PROVIDERS", "MS_84_105", "informs"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM — MS 84-105 (ONE form, TWO modules)
# ═══════════════════════════════════════════════════════════════════════════

MS84105_FACTS: list[dict] = [
    # ── the two orthogonal branches in the header ──
    {"fact_key": "entity_type", "label": "Entity type (header radio)", "data_type": "choice", "required": True,
     "sort_order": 1, "choices": ["1065", "1120S"],
     "notes": "⚠ THE MODULE FORK. 1065 = Partnership/LLC/LLP; 1120S = S Corporation. Drives the L1-L4 franchise "
              "hard gate, the L9 total, the underestimate form, the backstop-withholding regime, and the K-1 "
              "guaranteed-payment boxes."},
    {"fact_key": "filing_mode", "label": "Taxing mode (CHECK ALL THAT APPLY group)", "data_type": "choice",
     "required": True, "sort_order": 2, "choices": ["informational", "composite", "electing_pte"],
     "notes": "If neither Electing PTE nor Composite is checked the return is INFORMATIONAL — the entity computes "
              "and distributes on 84-131/84-132 and pays no MS income tax. ⚠ U2/W6: the form permits BOTH; v1 "
              "treats them as mutually exclusive with a RED."},
    {"fact_key": "both_composite_and_epte_checked", "label": "Both Composite AND Electing PTE checked? (U2)",
     "data_type": "boolean", "required": False, "sort_order": 3,
     "notes": "84-105 L5 says 'line 32 (composite) OR line 35' with no rule for both. RED-defer R12."},
    {"fact_key": "apportionment_mode", "label": "Apportionment mode (CHECK ONE group)", "data_type": "choice",
     "required": True, "sort_order": 4,
     "choices": ["100_percent_mississippi", "multistate_apportioning", "multistate_direct_accounting"],
     "notes": "100% MS -> 84-122 complete L18 then skip to L22 (= L18). Apportioning -> L19-L21 + Form 84-125. "
              "Direct accounting -> 84-122 L1 = zero, skip to L25, income off Form 84-124 (RED-defer R1)."},
    {"fact_key": "is_amended_return", "label": "Amended return", "data_type": "boolean", "required": False, "sort_order": 5},
    {"fact_key": "is_final_return", "label": "Final return", "data_type": "boolean", "required": False, "sort_order": 6},
    {"fact_key": "tax_year_beginning", "label": "Tax year beginning (mm dd yyyy)", "data_type": "date", "required": False, "sort_order": 7,
     "notes": "A fiscal-year return is a first-class case — §27-7-5(4) proration, and the FRANCHISE rate changes "
              "every year ($0.75 -> $0.50 for 2026)."},
    {"fact_key": "tax_year_ending", "label": "Tax year ending (mm dd yyyy)", "data_type": "date", "required": False, "sort_order": 8},
    {"fact_key": "total_mississippi_k1s", "label": "Total number of Mississippi K-1s", "data_type": "integer",
     "required": False, "sort_order": 9,
     "notes": "Face: 'If issuing 100 or more K-1s, this return must be filed electronically.'"},
    {"fact_key": "total_assets", "label": "Total assets (e-file mandate test, $250,000)", "data_type": "decimal",
     "required": False, "sort_order": 10},
    # ── the filer-shape exceptions ──
    {"fact_key": "elected_federal_corporate_treatment", "label": "Page 2 Part I line 4 — federal election to file as a corporation?",
     "data_type": "boolean", "required": False, "sort_order": 11,
     "notes": "⚠ 'Yes' means the entity is NOT an 84-105 filer at all — it files Form 83-105. RED STOP (R15), "
              "NOT a franchise-tax switch."},
    {"fact_key": "is_exempt_org_with_ubti", "label": "Exempt organization with UBTI (Form 990-T)", "data_type": "boolean",
     "required": False, "sort_order": 12,
     "notes": "Files 84-105, NOT subject to the franchise levy, leaves L1-L4 blank, enters 990-T UBTI on 84-122 L1."},
    {"fact_key": "is_inactive_s_corp", "label": "Inactive S corporation (still must file)", "data_type": "boolean",
     "required": False, "sort_order": 13,
     "notes": "A real filing mode: an inactive S corp files an 84-105 with $25 franchise minimum due, until "
              "dissolved or withdrawn through the Secretary of State."},
    {"fact_key": "fee_in_lieu_checked", "label": "Fee-In-Lieu checkbox (84-105 line 2)", "data_type": "boolean",
     "required": False, "sort_order": 14,
     "notes": "⚠ U3 / R6. Printed on the FINAL face; ZERO hits in both FINAL TY2025 booklets. §27-13-5(3)(a). "
              "Must exist and must SUPPRESS the L2 computation."},
    # ── franchise (84-110) inputs ──
    {"fact_key": "capital_stock", "label": "84-110 L1 Capital stock", "data_type": "decimal", "required": False, "sort_order": 20},
    {"fact_key": "paid_in_capital", "label": "84-110 L2 Paid in capital", "data_type": "decimal", "required": False, "sort_order": 21},
    {"fact_key": "surplus_and_retained_earnings", "label": "84-110 L3 Surplus and retained earnings", "data_type": "decimal", "required": False, "sort_order": 22},
    {"fact_key": "loans_from_shareholders_affiliates", "label": "84-110 L4 Loans from shareholders or affiliates", "data_type": "decimal", "required": False, "sort_order": 23},
    {"fact_key": "deferred_taxes_reserves_other", "label": "84-110 L5 Deferred taxes, contingent liabilities, true reserves", "data_type": "decimal", "required": False, "sort_order": 24},
    {"fact_key": "less_treasury_stock", "label": "84-110 L6 Less treasury stock (U16 — assumed SUBTRACTIVE)", "data_type": "decimal", "required": False, "sort_order": 25},
    {"fact_key": "holding_company_exclusion", "label": "84-110 L7 Holding company exclusion (U16 — assumed SUBTRACTIVE)", "data_type": "decimal", "required": False, "sort_order": 26},
    {"fact_key": "franchise_property_ms", "label": "84-110 L9A MS real and tangible personal property (NBV)", "data_type": "decimal", "required": False, "sort_order": 27},
    {"fact_key": "franchise_property_everywhere", "label": "84-110 L9B Everywhere property (NBV)", "data_type": "decimal", "required": False, "sort_order": 28},
    {"fact_key": "franchise_receipts_ms", "label": "84-110 L10A Mississippi gross receipts", "data_type": "decimal", "required": False, "sort_order": 29},
    {"fact_key": "franchise_receipts_everywhere", "label": "84-110 L10B Everywhere gross receipts", "data_type": "decimal", "required": False, "sort_order": 30},
    {"fact_key": "assessed_value_ms_property", "label": "84-110 L14 Total assessed value of MS property (PRIOR-YEAR county ad valorem)", "data_type": "decimal", "required": False, "sort_order": 31,
     "notes": "The L15 GREATER-OF floor. Lives in no federal return and no income schedule (§§27-13-9, 27-13-13)."},
    {"fact_key": "months_covered_by_return", "label": "84-110 L16 Months covered (short-period proration; NOT on an initial return)", "data_type": "integer", "required": False, "sort_order": 32},
    {"fact_key": "is_initial_return", "label": "Initial return (no 84-110 L16 proration)", "data_type": "boolean", "required": False, "sort_order": 33},
    {"fact_key": "capital_exemption", "label": "84-110 L17 Capital exemption", "data_type": "decimal", "required": False, "sort_order": 34},
    {"fact_key": "franchise_tax_credit_84401", "label": "84-105 L3 Franchise tax credit (Form 84-401, line 1)", "data_type": "decimal", "required": False, "sort_order": 35},
    # ── 84-122 engine inputs (DIRECT-ENTRY per W3/§15) ──
    {"fact_key": "federal_ordinary_business_income", "label": "84-122 L1 Ordinary business income (1120-S p1 L22 / 1065 p1 L23)", "data_type": "decimal", "required": False, "sort_order": 40,
     "notes": "E1/E5 — the FACE cite is correct; the 84-132 Box 1 instruction is off by one (both cited lines are "
              "'Total deductions' on the FINAL 2025 IRS forms). Build Box 1 to the SAME lines as this."},
    {"fact_key": "federal_schedule_k_income", "label": "84-122 L2 Total federal Schedule K income", "data_type": "decimal", "required": False, "sort_order": 41,
     "notes": "1120-S p3 Sch K lines 2-10 / 1065 p5 Sch K lines 2-11. ⚠ Instruction-only limiter: capital losses "
              "are included only to the extent of current-year capital gains. MS taxes capital gain as ORDINARY."},
    {"fact_key": "federal_schedule_k_deductions", "label": "84-122 L3 Total federal Schedule K deductions", "data_type": "decimal", "required": False, "sort_order": 42},
    {"fact_key": "add_income_taxes_deducted", "label": "84-122 L5 State/local/foreign taxes based on income", "data_type": "decimal", "required": False, "sort_order": 43},
    {"fact_key": "add_other_state_muni_interest", "label": "84-122 L6 Interest on obligations of OTHER states (MUNICIPAL BOND INTEREST)", "data_type": "decimal", "required": False, "sort_order": 44,
     "notes": "⚠ NOT DEPRECIATION. This is the line the campaign framing wrongly named as the bonus add-back."},
    {"fact_key": "add_excess_depletion", "label": "84-122 L7 Depletion expense in excess of cost", "data_type": "decimal", "required": False, "sort_order": 45},
    {"fact_key": "add_federal_special_depreciation", "label": "84-122 L8 FEDERAL SPECIAL DEPRECIATION ALLOWANCE (the add-back)", "data_type": "decimal", "required": False, "sort_order": 46,
     "notes": "⚠ THE ADD-BACK LINE, verified positionally off the FINAL 84-122 face. Federal Form 4562 filed TWICE, "
              "the second labeled 'Mississippi'. Also the landing line for the MS bonus and R&E elections."},
    {"fact_key": "add_other_additions", "label": "84-122 L9 Other additions required by law", "data_type": "decimal", "required": False, "sort_order": 47,
     "notes": "Occupants: charitable contribution carryovers; unrecognized installment-sale gains; related-member "
              "intangible/interest expense add-back; the extraterritorial income exclusion (attach Form 8873)."},
    {"fact_key": "ded_us_obligations_interest", "label": "84-122 L11 Interest on obligations of the United States", "data_type": "decimal", "required": False, "sort_order": 48},
    {"fact_key": "ded_wages_federal_employment_credits", "label": "84-122 L12 Wages reduced for federal employment tax credits", "data_type": "decimal", "required": False, "sort_order": 49},
    {"fact_key": "ded_flowthrough_income_removed", "label": "84-122 L13 Income (loss) from partnership, S corp or trust (REMOVAL)", "data_type": "decimal", "required": False, "sort_order": 50,
     "notes": "⚠ NOT DEPRECIATION. A REMOVAL line — the income is re-inserted, already sourced, at L24. This is "
              "the line the campaign framing wrongly named as the MS-basis recovery."},
    {"fact_key": "ded_construction_mineral_removed", "label": "84-122 L14 Construction/mineral income (REMOVAL, re-enters at L25)", "data_type": "decimal", "required": False, "sort_order": 51},
    {"fact_key": "ded_additional_ms_depreciation", "label": "84-122 L15 ADDITIONAL DEPRECIATION from the unreduced MS basis (the recovery)", "data_type": "decimal", "required": False, "sort_order": 52,
     "notes": "⚠ THE RECOVERY LINE. RECURS EVERY YEAR until the asset is fully recovered — NOT a same-year wash "
              "with L8. Requires a separate MS depreciation ledger per asset (R7 / W3)."},
    {"fact_key": "ded_other_deductions", "label": "84-122 L16 Other deductions (also the R&E election's second landing line, U14)", "data_type": "decimal", "required": False, "sort_order": 53},
    {"fact_key": "nonbusiness_income_everywhere", "label": "84-122 L19 Nonbusiness income net of expenses (84-150 col E line 2)", "data_type": "decimal", "required": False, "sort_order": 54},
    {"fact_key": "nonbusiness_income_ms", "label": "84-122 L23 Nonbusiness income allocated to MS (84-150 col F line 2)", "data_type": "decimal", "required": False, "sort_order": 55},
    {"fact_key": "ms_flowthrough_income_reinserted", "label": "84-122 L24 MS income from partnership, S corp or trust (already sourced)", "data_type": "decimal", "required": False, "sort_order": 56},
    {"fact_key": "ms_direct_accounting_income", "label": "84-122 L25 MS income from 84-124 (p2 L31 or p3 L46)", "data_type": "decimal", "required": False, "sort_order": 57},
    {"fact_key": "other_adjustments_required_by_law", "label": "84-122 L26 Other adjustments required by law", "data_type": "decimal", "required": False, "sort_order": 58},
    {"fact_key": "income_exemption_mda", "label": "84-122 L27 Income exemption (MDA certification required)", "data_type": "decimal", "required": False, "sort_order": 59,
     "notes": "RED-defer R14 — requires an MDA certification and the completed application as attachments."},
    {"fact_key": "composite_net_income_84131_l4a", "label": "84-122 L29 Composite net income (Form 84-131 line 4a)", "data_type": "decimal", "required": False, "sort_order": 60,
     "notes": "⚠ ONLY owners whose COMPOSITE box is checked in 84-131 Column B. This is why the composite base is "
              "SMALLER than the electing-PTE base (L33 = L28 in full)."},
    {"fact_key": "composite_filing_adjustment_l30", "label": "84-122 L30 Composite return filing adjustment (attach schedule)", "data_type": "decimal", "required": False, "sort_order": 61,
     "notes": "⚠ U7. Booklet: '$5,000 or 10% of the composite NET INCOME, whichever is less'. Regulation: '10% of "
              "ADJUSTED GROSS INCOME'. DIFFERENT BASES; the face gives no formula and no cap."},
    {"fact_key": "ms_nol_deduction_84155_l2", "label": "84-155 line 2 MS NOL used this year (-> 84-122 L31 or L34)", "data_type": "decimal", "required": False, "sort_order": 62,
     "notes": "⚠ U8: whether the composite and EPTE pools are distinct is unstated. ⚠ U9: pre- vs post-apportionment "
              "is unstated; the form's arithmetic says POST — Ken should bless."},
    {"fact_key": "nol_forgo_carryback_election", "label": "84-155 State election to forgo carryback (IRREVOCABLE)", "data_type": "boolean", "required": False, "sort_order": 63},
    # ── apportionment (84-125) inputs ──
    {"fact_key": "apportionment_category", "label": "84-125 Part II category (CHECK ONE)", "data_type": "choice", "required": False, "sort_order": 70,
     "choices": ["sales_retail_line4", "manufacturers_retail_line5", "manufacturers_wholesale_fi_pipeline_line6", "special_formula_line7"],
     "notes": "⚠ R3 pipelines (U5 — reg says traffic miles), R4 financial institutions (U4 — no reg formula "
              "exists), R5 pharmaceutical five-factor (U6 — rule is only in the 83-100 booklet), R2 line 7."},
    {"fact_key": "property_boy_ms", "label": "84-125 L1a MS property, beginning of year", "data_type": "decimal", "required": False, "sort_order": 71},
    {"fact_key": "property_eoy_ms", "label": "84-125 L1b MS property, end of year", "data_type": "decimal", "required": False, "sort_order": 72},
    {"fact_key": "property_boy_everywhere", "label": "84-125 L1a Everywhere property, beginning of year", "data_type": "decimal", "required": False, "sort_order": 73},
    {"fact_key": "property_eoy_everywhere", "label": "84-125 L1b Everywhere property, end of year", "data_type": "decimal", "required": False, "sort_order": 74},
    {"fact_key": "annual_rent_ms", "label": "84-125 L1e MS annual rental property (capitalized x8)", "data_type": "decimal", "required": False, "sort_order": 75,
     "notes": "§402.09(1)(f) net annual rental rate LESS subrents — ⚠ (1)(g): subrents are NOT deducted when they "
              "constitute business income. Leasehold improvements and transportation equipment are EXCLUDED."},
    {"fact_key": "annual_rent_everywhere", "label": "84-125 L1e Everywhere annual rental property (capitalized x8)", "data_type": "decimal", "required": False, "sort_order": 76},
    {"fact_key": "payroll_ms", "label": "84-125 L2A Mississippi payroll", "data_type": "decimal", "required": False, "sort_order": 77},
    {"fact_key": "payroll_everywhere", "label": "84-125 L2B Everywhere payroll", "data_type": "decimal", "required": False, "sort_order": 78},
    {"fact_key": "sales_destination_into_ms", "label": "84-125 L3A component — destination sales INTO Mississippi", "data_type": "decimal", "required": False, "sort_order": 79},
    {"fact_key": "sales_thrown_back_to_ms", "label": "84-125 L3A component — THROWBACK sales shipped FROM a MS location", "data_type": "decimal", "required": False, "sort_order": 80,
     "notes": "⚠ §402.09(3)(b)(ii) and (vii): shipped from a MS location into a state where the taxpayer is NOT "
              "TAXABLE — including a state where it is protected by P.L. 86-272 (§202.06). A first-class input, "
              "never preparer memory."},
    {"fact_key": "sales_dropship_thrown_back", "label": "84-125 L3A component — drop-shipment throwback (§402.09(3)(b)(viii))", "data_type": "decimal", "required": False, "sort_order": 81},
    {"fact_key": "sales_us_government_from_ms", "label": "84-125 L3A component — ALL U.S. Government sales shipped from a MS location", "data_type": "decimal", "required": False, "sort_order": 82,
     "notes": "§402.09(3)(c) — ORIGIN-sourced unconditionally (throwback in the other direction). Subcontractor "
              "sales to a prime contractor are NOT sales to the U.S. Government."},
    {"fact_key": "sales_everywhere", "label": "84-125 L3B Everywhere sales", "data_type": "decimal", "required": False, "sort_order": 83,
     "notes": "'Sales' is broad: business interest and dividends IN; capital-asset sales at GAIN ONLY, not gross "
              "proceeds; excise/sales taxes included if passed on to the buyer."},
    # ── payments / tax due ──
    {"fact_key": "income_tax_credits_84401", "label": "84-105 L7 Income tax credits (Form 84-401, line 3 — NOT 83-401, E2)", "data_type": "decimal", "required": False, "sort_order": 90},
    {"fact_key": "prior_year_overpayment", "label": "84-105 L10 Overpayments from prior year", "data_type": "decimal", "required": False, "sort_order": 91},
    {"fact_key": "estimated_and_extension_payments", "label": "84-105 L11 Estimated tax payments and payment with extension", "data_type": "decimal", "required": False, "sort_order": 92},
    {"fact_key": "lower_tier_ptet_credit_84161_l3d", "label": "84-105 L12 Credit for tax paid on an electing PTE return (84-161 line 3D)", "data_type": "decimal", "required": False, "sort_order": 93,
     "notes": "⚠ THE TIERING LINE. An upper-tier PTE claims a lower tier's entity-level tax HERE, in PAYMENTS, and "
              "need NOT elect itself. MS puts the PTET credit in payments, never in credits, at every level. "
              "Attachment gate: must attach the K-1(s) received."},
    {"fact_key": "underestimate_interest_penalty_l15", "label": "84-105 L15 Underestimate interest and penalty (83-305 L19 or 80-320 L11)", "data_type": "decimal", "required": False, "sort_order": 94,
     "notes": "⚠ MODE x ENTITY: composite PARTNERSHIP -> 80-320 L11 (80%, calendar quarters, NO 10% penalty); "
              "everything else -> 83-305 L19 (90%, 4th/6th/9th/12th month, 10% + 1/2%/month). RED-defer R11a/R11b."},
    {"fact_key": "late_payment_interest", "label": "84-105 L16 Late payment interest (1/2 of 1% per month)", "data_type": "decimal", "required": False, "sort_order": 95},
    {"fact_key": "late_payment_penalty", "label": "84-105 L17 Late payment penalty (1/2% per month, max 25%)", "data_type": "decimal", "required": False, "sort_order": 96},
    {"fact_key": "late_filing_penalty", "label": "84-105 L18 Late filing penalty (5%/month, max 25%, MINIMUM $100 income tax)", "data_type": "decimal", "required": False, "sort_order": 97},
    {"fact_key": "overpayment_credited_next_year", "label": "84-105 L21 Overpayment credited to next year", "data_type": "decimal", "required": False, "sort_order": 98},
    # ── PTET election / owner side ──
    {"fact_key": "ptet_election_84381_on_file", "label": "Form 84-381 election on file (and attached to the return)", "data_type": "boolean", "required": False, "sort_order": 100,
     "notes": "⚠ W9. Separate form, BINDING for the year and every later year until a 'Removing PTE' 84-381 is "
              "filed, CANNOT be made retroactively by amending, requires a >50% governance vote. Fiduciaries "
              "cannot elect. Can be filed through TAP even though the return cannot."},
    {"fact_key": "ptet_election_effective_date", "label": "Form 84-381 effective date of election or revocation", "data_type": "date", "required": False, "sort_order": 101},
    {"fact_key": "ptet_vote_attestation", "label": "Form 84-381 vote-threshold attestation checkbox (>50% of voting control)", "data_type": "boolean", "required": False, "sort_order": 102},
    {"fact_key": "owner_ptet_tax_paid_l3d", "label": "84-161/80-161 L3D total tax paid on electing PTE returns", "data_type": "decimal", "required": False, "sort_order": 103},
    {"fact_key": "owner_total_ms_tax_l4", "label": "84-161/80-161 L4 owner's total Mississippi income tax due", "data_type": "decimal", "required": False, "sort_order": 104},
    {"fact_key": "owner_type_for_credit_landing", "label": "Owner type (drives the PTET credit landing line)", "data_type": "choice", "required": False, "sort_order": 105,
     "choices": ["individual_resident", "individual_nonresident_or_part_year", "fiduciary", "business_pte", "business_corporation"],
     "notes": "⚠ 'fiduciary' CANNOT ELECT but CAN RECEIVE — Form 81-110 page 1 line 8."},
    # ── depreciation flags (app-level; no form field exists) ──
    {"fact_key": "ms_bonus_depreciation_election", "label": "84-122 top-of-page 'Bonus Depreciation Election' checkbox (IRREVOCABLE)", "data_type": "boolean", "required": False, "sort_order": 110},
    {"fact_key": "ms_rd_expense_election", "label": "84-122 top-of-page 'R&D Expense Election' checkbox (IRREVOCABLE)", "data_type": "boolean", "required": False, "sort_order": 111,
     "notes": "⚠ U14: the L8 instruction routes it to L8, the L16 instruction routes it to L16. Net effect coherent, "
              "routing is not."},
    {"fact_key": "ms_aviation_asset", "label": "APP-LEVEL FLAG — aviation asset (follows the FEDERAL bonus rate)",
     "data_type": "boolean", "required": False, "sort_order": 112,
     "notes": "⚠ W4. §27-7-17(1)(f)(i). NO aviation line, checkbox or word exists on Form 84-122 or in the FINAL "
              "TY2025 84-100 booklet — the branch is statutory only and the form gives the preparer nowhere to "
              "signal it. Do NOT invent a form field."},
    {"fact_key": "federal_4562_shows_special_allowance", "label": "Federal Form 4562 shows a special depreciation allowance",
     "data_type": "boolean", "required": False, "sort_order": 113,
     "notes": "Hard RED trigger when 84-122 L8 is blank (W3)."},
    {"fact_key": "ms_section_179_deduction", "label": "84-132 Box 13 MISSISSIPPI §179 deduction (direct-entry, W10/U13)",
     "data_type": "decimal", "required": False, "sort_order": 114,
     "notes": "MS conforms to §179 rolling ('in effect for that year'), but no MS form line computes it and no "
              "instruction derives it. MS apportionment and MS basis differ, so it is NOT federal x ownership%."},
    # ── nonresident / withholding ──
    {"fact_key": "nonresident_owners_present", "label": "Nonresident owners present", "data_type": "boolean", "required": False, "sort_order": 120},
    {"fact_key": "form_84380_agreements_on_file", "label": "S corp: Form 84-380 agreement on file from EVERY nonresident shareholder",
     "data_type": "boolean", "required": False, "sort_order": 121,
     "notes": "Retained by the S corporation, NOT filed with the return. On failure the corporation owes a FLAT 5% "
              "of that shareholder's MS income (RED-defer R9; ⚠ U15 — L6 would apply 0/4/5 instead)."},
    {"fact_key": "form_84387_backstop_remitted", "label": "Partnership: 5% of net gain/profit remitted on Form 84-387",
     "data_type": "boolean", "required": False, "sort_order": 122,
     "notes": "Withhold from MISSISSIPPI SOURCE INCOME ONLY. Partners claim it as ESTIMATED TAX; refundable if "
              "their liability is less. Surfaced on 84-132 Box G. RED-defer R10."},
    {"fact_key": "partnership_net_gain_or_profit", "label": "Form 84-387 L1 total partnership net gain or profit", "data_type": "decimal", "required": False, "sort_order": 123},
]

MS84105_RULES: list[dict] = [
    {"rule_id": "R-MS-ENTITY-GATE", "title": "⚠ Entity-type hard gate on the franchise block (84-105 L1-L4 / Form 84-110)",
     "rule_type": "routing", "sort_order": 1,
     "formula": ("franchise_block_applies = (entity_type == '1120S') "
                 "AND NOT elected_federal_corporate_treatment AND NOT is_exempt_org_with_ubti ; "
                 "if entity_type == '1065': L1..L4 are NOT APPLICABLE — hard-gated, never merely blank"),
     "inputs": ["entity_type", "elected_federal_corporate_treatment", "is_exempt_org_with_ubti"],
     "outputs": ["franchise_block_applies"],
     "description": "W2. The block header is literally 'S CORPORATION FRANCHISE TAX'. The $25 MINIMUM makes the "
                    "partnership failure mode SILENT AND NON-ZERO — the smallest possible partnership would file a "
                    "$25 tax it does not owe. Two exceptions: a partnership/LLC that elected federal corporate "
                    "treatment is not an 84-105 filer at all (-> Form 83-105, R15); an exempt org with UBTI files "
                    "84-105 and leaves L1-L4 blank.",
     "exceptions": "§27-13-5(1)(a) reaches a 'partnership treated as a corporation under the income tax laws or "
                   "regulations' — but that entity files Form 83-105, not 84-105."},
    {"rule_id": "R-MS-FRAN-CAPITAL", "title": "Form 84-110 — capital base, its own apportionment, assessed-value floor",
     "rule_type": "calculation", "sort_order": 2,
     "formula": ("L8 = L1 + L2 + L3 + L4 + L5 - L6 - L7   [U16: L6/L7 assumed SUBTRACTIVE inside 'add 1 through 7'] ; "
                 "L11A = L9A + L10A ; L11B = L9B + L10B ; L12 = L11A / L11B  [PROPERTY + GROSS RECEIPTS — a SECOND, "
                 "different apportionment engine from the income formula] ; "
                 "L13 = L8 if 100% Mississippi else L8 * L12 ; "
                 "L15 = MAX(L13, L14)   [prior-year county ad valorem assessed-value FLOOR] ; "
                 "L16 = L15 * months / 12  (short period ONLY, and NOT on an initial return) ; "
                 "L18 = MAX(0, ROUND_UP_TO_NEXT_1000((L16 or L15) - L17))  ->  84-105 L1"),
     "inputs": ["capital_stock", "paid_in_capital", "surplus_and_retained_earnings", "loans_from_shareholders_affiliates",
                "deferred_taxes_reserves_other", "less_treasury_stock", "holding_company_exclusion",
                "franchise_property_ms", "franchise_property_everywhere", "franchise_receipts_ms",
                "franchise_receipts_everywhere", "assessed_value_ms_property", "months_covered_by_return",
                "is_initial_return", "capital_exemption"],
     "outputs": ["110-L8", "110-L12", "110-L13", "110-L15", "110-L16", "110-L18", "1"],
     "description": "W8(b)/U16. Nothing on the FEDERAL return produces this base — capital comes off the balance "
                    "sheet and the floor off a prior-year county ad valorem assessment. Flow-through look-through: "
                    "the property and receipts of flow-through entities must be included in a multistate corporate "
                    "partner's capital-base ratio."},
    {"rule_id": "R-MS-FRANCHISE", "title": "84-105 L2-L4 — TY-keyed franchise tax, $25 minimum, repealed 1/1/2028",
     "rule_type": "calculation", "sort_order": 3,
     "formula": ("L2 = MAX(25, rate_for_tax_year * CEIL(MAX(0, L1 - 100000) / 1000)) ; "
                 "TY2025 rate = $0.75 per $1,000 ; ladder 2024 $1.00 / 2025 $0.75 / 2026 $0.50 / 2027 $0.25 / "
                 "2028 REPEALED (no statutory clause exists) ; "
                 "if fee_in_lieu_checked: SUPPRESS the L2 computation (R6) ; "
                 "L4 = MAX(0, L2 - L3)"),
     "inputs": ["1", "franchise_tax_credit_84401", "fee_in_lieu_checked", "tax_year_beginning"],
     "outputs": ["2", "4"],
     "description": "W8(a). §27-13-5(1)(a)(ix) + (1)(b). The rate MUST be a TY-keyed table with a sunset, never a "
                    "constant — and because the franchise rate changes EVERY year, the §27-7-5(4) fiscal-year "
                    "problem is live here with a different answer from the income side. L4 instruction: 'If line 3 "
                    "equals or exceeds the amount shown on line 2, enter a zero.'"},
    {"rule_id": "R-MS-ENGINE-122", "title": "Form 84-122 — the income engine (L4, L10, L17, L18, L20, L22, L28)",
     "rule_type": "calculation", "sort_order": 4,
     "formula": ("L4 = L1 + L2 - L3 ; L10 = L5 + L6 + L7 + L8 + L9 ; L17 = L11 + L12 + L13 + L14 + L15 + L16 ; "
                 "L18 = L4 + L10 - L17 ; L20 = L18 - L19 ; "
                 "L22 = L18 if apportionment_mode == '100_percent_mississippi' else L20 * L21 ; "
                 "L28 = (L22 + L23 + L24 + L25 + L26) - L27   ⚠ PER THE FACE (E4: the instruction's 'sum lines 22 "
                 "through 27' is wrong — L27 is an EXEMPTION)"),
     "inputs": ["federal_ordinary_business_income", "federal_schedule_k_income", "federal_schedule_k_deductions",
                "add_income_taxes_deducted", "add_other_state_muni_interest", "add_excess_depletion",
                "add_federal_special_depreciation", "add_other_additions", "ded_us_obligations_interest",
                "ded_wages_federal_employment_credits", "ded_flowthrough_income_removed",
                "ded_construction_mineral_removed", "ded_additional_ms_depreciation", "ded_other_deductions",
                "nonbusiness_income_everywhere", "nonbusiness_income_ms", "ms_flowthrough_income_reinserted",
                "ms_direct_accounting_income", "other_adjustments_required_by_law", "income_exemption_mda",
                "apportionment_mode"],
     "outputs": ["122-L4", "122-L10", "122-L17", "122-L18", "122-L20", "122-L22", "122-L28"],
     "description": "E4/E5 — build to the FACE throughout. L13 and L14 are REMOVAL lines, not benefits: lower-tier "
                    "flow-through income is stripped out of the apportionable base and re-inserted ALREADY SOURCED "
                    "at L24; direct-accounting lines of business re-enter at L25 off Form 84-124. '100% Mississippi' "
                    "takes the short path: complete L18, skip to L22 = L18."},
    {"rule_id": "R-MS-DEPR", "title": "⚠ DEPRECIATION — add-back on 84-122 L8, MS-basis recovery on 84-122 L15",
     "rule_type": "calculation", "sort_order": 5,
     "formula": ("122-L8  (+) = the federal §168(k) special depreciation allowance, REMOVED from the MS base ; "
                 "122-L15 (-) = the extra MS depreciation that exists because Mississippi NEVER reduced the asset's "
                 "basis by the federal allowance (MS keeps an UNREDUCED basis) ; "
                 "⚠ NOT 122-L6 (municipal-bond interest) and NOT 122-L13 (flow-through income) — those are the "
                 "Form 83-122 CORPORATE line numbers ; "
                 "MS own bonus = 100% for property placed in service after 12/31/2022, elective + IRREVOCABLE, "
                 "§168(k)/§168(e)(6) definitions FROZEN at 1/1/2021, combined methods capped at 100% of cost"),
     "inputs": ["add_federal_special_depreciation", "ded_additional_ms_depreciation",
                "ms_bonus_depreciation_election", "ms_rd_expense_election", "federal_4562_shows_special_allowance"],
     "outputs": ["122-L8", "122-L15"],
     "description": "⚠ THE REASON THIS SPEC EXISTS. Verified positionally off the FINAL TY2025 84-122 face and "
                    "confirmed by DOR's own L8 instruction ('...is reported on line 15 of this form'). Putting the "
                    "federal special depreciation allowance on L6 would report it as MUNICIPAL-BOND INTEREST and "
                    "the recovery on L13 would corrupt the L24 re-insertion of already-sourced flow-through income "
                    "— both silently. NOT a same-year wash: L15 recurs every year until the asset is fully "
                    "recovered, so the app needs a separate MS depreciation ledger per asset (R7, v1.1).",
     "exceptions": "AVIATION — see R-MS-DEPR-AVIATN. §179 — see R-MS-179 (rolling, = federal for the tax year). "
                   "U14: the R&E election's landing line is routed to L8 by one instruction and to L16 by another."},
    {"rule_id": "R-MS-DEPR-AVIATN", "title": "⚠ THE AVIATION EXCEPTION — aviation assets follow the FEDERAL bonus rate",
     "rule_type": "conditional", "sort_order": 6,
     "formula": ("if ms_aviation_asset: rate = FEDERAL bonus rate under OBBBA "
                 "(100% if acquired AND placed in service on/after 2025-01-20, else 40%) ; "
                 "else: rate = MS's own 100% (property placed in service after 2022-12-31)"),
     "inputs": ["ms_aviation_asset"], "outputs": ["ms_bonus_rate"],
     "description": "W4 / R8. §27-7-17(1)(f)(i): 'In the case of new or used aircraft, equipment, engines, or other "
                    "parts and tools used for aviation, allowance for bonus depreciation CONFORMS WITH THE FEDERAL "
                    "BONUS DEPRECIATION RATES...' The ONE place OBBBA §168(k) reaches Mississippi cost recovery. "
                    "Two assets, same year, same taxpayer, different regimes. ⚠ No aviation line, checkbox or word "
                    "exists on Form 84-122 or anywhere in the FINAL TY2025 84-100 booklet (searched: zero hits) — "
                    "the branch is statutory only. Carry an APP-LEVEL flag; do NOT invent a form field."},
    {"rule_id": "R-MS-179", "title": "§179 — ROLLING conformity, = federal for the tax year (never a constant)",
     "rule_type": "calculation", "sort_order": 7,
     "formula": "MS §179 limit/phaseout = the federal §179 figures IN EFFECT FOR THAT TAX YEAR (TY2025: $2,500,000 "
                "limit / $4,000,000 phaseout / $31,300 SUV sub-limit) ; 84-132 Box 13 = the MISSISSIPPI §179 amount, "
                "DIRECT-ENTRY (W10/U13)",
     "inputs": ["ms_section_179_deduction"], "outputs": ["132-B13"],
     "description": "§27-7-17(1)(f)(ii)3: \"Mississippi's treatment of the deduction shall conform to the provisions "
                    "of 26 USCS Section 179 IN EFFECT FOR THAT YEAR.\" Mississippi publishes NO §179 dollar figure "
                    "of its own. ⚠ U13: no MS form line computes the Mississippi §179 amount and no instruction "
                    "derives it, yet 84-132 Box 13 requires one — and MS apportionment and MS basis both differ "
                    "from federal, so it is NOT federal x ownership%. ⚠ Georgia's figures are irrelevant here: MS "
                    "reaches the same numbers by a ROLLING statutory adoption. NEVER CLONE GA."},
    {"rule_id": "R-MS-APPORT", "title": "Form 84-125 — the industry-keyed apportionment formulas (ratio -> 84-122 L21)",
     "rule_type": "calculation", "sort_order": 8,
     "formula": ("L1f = ((L1a + L1b) / 2) + (annual_rent * 8) ; L1g = L1fA / L1fB ; L2 = payrollA / payrollB ; "
                 "L3 = salesA / salesB   [four decimal places] ; "
                 "line 4  (retail/rent/service/merchandise/wholesale) = L3                       SINGLE SALES ; "
                 "line 5g (manufacturers selling principally at RETAIL)   = ((L1g + L2)/2 + L3)/2 ; "
                 "line 6e (manufacturers WHOLESALE, financial institutions, pipelines) = (L1g + L2 + L3)/3 ; "
                 "line 7  (airlines, motor carriers, express, telephone/telegraph) = SPECIAL FORMULA (RED, R2)"),
     "inputs": ["apportionment_category", "property_boy_ms", "property_eoy_ms", "property_boy_everywhere",
                "property_eoy_everywhere", "annual_rent_ms", "annual_rent_everywhere", "payroll_ms",
                "payroll_everywhere", "sales_everywhere"],
     "outputs": ["125-L1g", "125-L2", "125-L3", "125-L4", "125-L5g", "125-L6e", "122-L21"],
     "description": "Property factor: average of beginning- and end-of-year NBV PLUS rented property capitalized at "
                    "EIGHT TIMES the net annual rental rate. Transportation equipment is EXCLUDED COMPLETELY; "
                    "leasehold improvements are treated as owned and their NBV is EXCLUDED; subrents are deducted "
                    "EXCEPT where they constitute business income. ⚠ Three divergences flagged, none resolved: "
                    "pipelines (U5/R3 — the regulation uses TRAFFIC MILES, not sales), financial institutions "
                    "(U4/R4 — no formula exists in the official 123-page Part III), and the five-factor "
                    "pharmaceutical variant (U6/R5 — the form cites a booklet that does not contain the rule)."},
    {"rule_id": "R-MS-THROWBACK", "title": "⚠ The Mississippi sales-factor numerator — DESTINATION plus THROWBACK",
     "rule_type": "calculation", "sort_order": 9,
     "formula": ("MS sales numerator = destination sales delivered/shipped to a purchaser in MS "
                 "+ sales shipped FROM a MS office/store/warehouse/factory where the taxpayer is NOT TAXABLE in the "
                 "purchaser's state   [THROWBACK, §402.09(3)(b)(ii) and (vii)] "
                 "+ drop-shipment throwbacks   [(viii)] "
                 "+ ALL sales to the U.S. Government shipped from a MS location   [ORIGIN-sourced, §402.09(3)(c)]"),
     "inputs": ["sales_destination_into_ms", "sales_thrown_back_to_ms", "sales_dropship_thrown_back",
                "sales_us_government_from_ms"],
     "outputs": ["125-L3"],
     "description": "W5. Verified from the OFFICIAL Mississippi Secretary of State Administrative Code capture (not "
                    "a mirror). ⚠ §202.06: 'Jurisdiction to tax is not present when the state is prohibited from "
                    "imposing the tax by reason of the provisions of Public Law 86-272' — SO A MISSISSIPPI "
                    "MANUFACTURER PROTECTED BY P.L. 86-272 IN THE DESTINATION STATE THROWS THE SALE BACK TO "
                    "MISSISSIPPI. Voluntary filing, or a minimum tax/qualification fee without actual business "
                    "activity, does NOT make the taxpayer taxable there. Also: diverted shipments and ultimate "
                    "recipients are MS sales; capital-asset receipts enter at GAIN ONLY, not gross proceeds; "
                    "business interest and dividends are IN the sales factor.",
     "exceptions": "Total-assignment rule: if the entity is not taxable in ANY other state, its TOTAL net income is "
                   "assigned to Mississippi."},
    {"rule_id": "R-MS-TERMINAL", "title": "Form 84-122 terminal blocks — composite L29-L32 vs electing PTE L33-L35",
     "rule_type": "calculation", "sort_order": 10,
     "formula": ("COMPOSITE:     L32 = L29 - L30 - L31 ; if negative, enter ZERO on 84-105 L5 ; "
                 "               L29 comes off Form 84-131 line 4a — ONLY owners with the COMPOSITE box checked ; "
                 "               L30 is a deduction the EPTE does NOT get ($5,000 or 10%, whichever is less — but "
                 "               ⚠ U7, the BASE is contested and the face gives no formula and no cap) ; "
                 "ELECTING PTE:  L33 = L28 IN FULL (every owner, resident and nonresident) ; "
                 "               L35 = L33 - L34 ; if negative, enter ZERO on 84-105 L5"),
     "inputs": ["filing_mode", "composite_net_income_84131_l4a", "composite_filing_adjustment_l30",
                "ms_nol_deduction_84155_l2", "122-L28"],
     "outputs": ["122-L32", "122-L35", "5"],
     "description": "⚠ THE STRUCTURAL DIFFERENCE BETWEEN THE TWO MODES IS THE BASE, AND IT IS LARGE. The electing "
                    "PTE is taxed on ALL Mississippi income; the composite base covers only the qualified "
                    "nonresident owners who elected in. ⚠ U8: the NOL is deducted per mode (L31 vs L34) from the "
                    "SAME Form 84-155 line 2, and the L31 instruction calls it a 'separate company composite' NOL — "
                    "whether one entity can hold two pools is unstated. ⚠ U9: pre- vs post-apportionment is "
                    "unstated; the form's arithmetic says POST and Ken should BLESS rather than the spec assuming."},
    {"rule_id": "R-MS-NOL", "title": "Form 84-155 — the Mississippi NOL (2 back / 20 forward, NOT the federal period)",
     "rule_type": "calculation", "sort_order": 11,
     "formula": ("columns A NOL Year End / B NOL Amount / C Income Year NOL Applied / D Amount Used / E NOL Balance, "
                 "with B - D = E ; NOLs entered as POSITIVE numbers; the CURRENT-year NOL is NOT entered in A-E ; "
                 "L2 (used in current year) -> 84-122 L31 (composite) or L34 (electing PTE) ; "
                 "carryback 2 / carryforward 20 ; a short year counts as a year"),
     "inputs": ["ms_nol_deduction_84155_l2", "nol_forgo_carryback_election"], "outputs": ["155-L2"],
     "description": "'Mississippi does not conform to federal net operating loss rules.' The face carries a 'State "
                    "election to forgo carryback and to carryforward the current year NOL' checkbox and the booklet "
                    "says 'Once this election is made, IT CANNOT BE CHANGED.' 'Form 84-155 must be completed and "
                    "attached or an NOL deduction will not be allowed.'"},
    {"rule_id": "R-MS-INCOME-TAX", "title": "84-105 L6-L8 — the ELECTING-PTE rate (0% / 4% / 5%) and net income tax",
     "rule_type": "calculation", "sort_order": 12,
     "formula": ("ELECTING PTE (SETTLED): L6 = 0% on the first $5,000 + 4% on the next $5,000 + 5% on taxable "
                 "income in excess of $10,000, applied to L5 ; "
                 "COMPOSITE: ⚠ NO RATE IS COMPUTED — see R-MS-COMP-RATE ; "
                 "L8 = MAX(0, L6 - L7)"),
     "inputs": ["5", "income_tax_credits_84401", "filing_mode"], "outputs": ["6", "8"],
     "description": "§27-7-5(1)(a) levies 0/4/5 on 'every resident individual, corporation, association, trust or "
                    "estate'; §27-7-5(1)(b) then reduces the rate FOR INDIVIDUALS ONLY. A partnership or S "
                    "corporation is not an individual, so an electing PTE sits on the unreduced 0/4/5 — DOR and "
                    "statute agree and this half is SETTLED. L8 instruction: 'If line 7 equals or exceeds the amount "
                    "shown on line 6, enter a zero.' Both 84-122 terminal lines floor at zero onto L5."},
    {"rule_id": "R-MS-COMP-RATE", "title": "⚠ THE COMPOSITE RATE — THREE-SIDED, UNRESOLVED, NO SIDE PICKED",
     "rule_type": "validation", "sort_order": 13,
     "formula": ("COMPOSITE L6 IS NOT COMPUTED IN THIS SPEC. Three positions, none dispositive: "
                 "A = 0%/4%/5% (MS DOR, twice, TY2025-keyed) ; "
                 "B = 0% first $10,000 / 4.4% above (§27-7-5(1)(b) — composite members ARE individuals) ; "
                 "C = the official regulation's TWO PACKAGED ROUTES — the individual rate WITH the $5,000/10% "
                 "deduction, or the corporate rate WITH NO deduction (S corps only; no corporate-rate route is "
                 "offered for partnerships at all). The TY2025 forms take one half of EACH. "
                 "-> RAISE D_MS84105_COMPOSITE_RATE and DIRECT-ENTER L6 until Ken rules."),
     "inputs": ["filing_mode", "entity_type", "5"], "outputs": ["6"],
     "description": "W1 / U1 — the #1 walk item and the only place where DOR, the statute and the official "
                    "regulation all say different things. DOR's own plumbing splits the modules (composite S corps "
                    "-> corporate Form 83-305; composite partnerships -> individual Form 80-320), so the rate "
                    "question is live in DOR's own machinery. Recommendation for the walk: ship DOR's 0/4/5 as a "
                    "SINGLE-POINT-OF-CHANGE flagged constant with a review diagnostic on every composite return, "
                    "and open a DOR ticket before the module ships — recorded as a RULING, not a finding. "
                    "DO NOT RESOLVE THIS BY CHOOSING.",
     "exceptions": "Bound up with U7: the regulation makes the $5,000/10% deduction and the individual rate a "
                   "PACKAGE, and words the deduction base differently ('adjusted gross income') from the booklet "
                   "('composite net income')."},
    {"rule_id": "R-MS-FISCAL-PROR", "title": "§27-7-5(4) fiscal-year proration — a general mechanism, not dead code",
     "rule_type": "calculation", "sort_order": 14,
     "formula": ("tax = (full-year tax at the BEGINNING calendar year's rates * months in that year / total months) "
                 "+ (full-year tax at the ENDING calendar year's rates * months in that year / total months)"),
     "inputs": ["tax_year_beginning", "tax_year_ending", "5"], "outputs": ["6", "2"],
     "description": "Printed verbatim on the 84-105 L6 instruction. A NO-OP for an electing PTE in TY2025 (0/4/5 did "
                    "not change between 2025 and 2026) — but LIVE on the FRANCHISE side, where the rate changes "
                    "every single year ($0.75 -> $0.50), and live for composite if W1 resolves to the individual "
                    "schedule (4.4% -> 4.0%). Encode keyed to a rate TABLE, never as dead code."},
    {"rule_id": "R-MS-FORK-L9", "title": "⚠ THE MODULE FORK — 84-105 L9 = L4 + L8 (S corp) vs = L8 (partnership)",
     "rule_type": "conditional", "sort_order": 15,
     "formula": "L9 = (L4 + L8) if entity_type == '1120S' else L8",
     "inputs": ["entity_type", "4", "8"], "outputs": ["9"],
     "description": "84-100 (Rev. 01/26) p.17, verbatim: 'S corporations, enter the amount from line 4; composite "
                    "and electing pass-through entity S corporations, enter the amounts from line 4 plus line 8; "
                    "and composite and electing pass-through entity partnerships, enter the amount from line 8.' "
                    "The single most consequential branch on the form: a partnership return that lands a franchise "
                    "tax on L2 is a WRONG RETURN, and the $25 minimum makes the failure silent and non-zero."},
    {"rule_id": "R-MS-PAYMENTS", "title": "84-105 L13-L22 — payments, balance due, and the L20 ASYMMETRY",
     "rule_type": "calculation", "sort_order": 16,
     "formula": ("L13 = L10 + L11 + L12 ; L14 = L9 - L13 ; "
                 "L19 (if L9 > L13) = L14 + L15 + L16 + L17 + L18   ⚠ per the FACE — E3, the instruction's 'line 10' "
                 "is meaningless ; "
                 "L20 (if L13 > L9 + L15) = L13 - L9 - L15   ⚠ ASYMMETRY: the underestimate interest/penalty IS "
                 "netted against the refund but the LATE-PAYMENT items L16-L18 are NOT ; "
                 "L22 = L20 - L21"),
     "inputs": ["prior_year_overpayment", "estimated_and_extension_payments", "lower_tier_ptet_credit_84161_l3d",
                "underestimate_interest_penalty_l15", "late_payment_interest", "late_payment_penalty",
                "late_filing_penalty", "overpayment_credited_next_year", "9"],
     "outputs": ["13", "14", "19", "20", "22"],
     "description": "⚠ Encode L20 AS WRITTEN, not as L13 - L19. ⚠ L12 is the TIERING LINE and is easy to miss: an "
                    "upper-tier PTE that owns a lower-tier electing PTE claims the lower tier's entity-level tax "
                    "HERE, in the PAYMENTS block, via Form 84-161 line 3D — and does NOT have to elect itself. "
                    "Mississippi puts the PTET credit in payments, never in credits, at every level."},
    {"rule_id": "R-MS-PTET-ELECT", "title": "⚠ Form 84-381 — the PTET election is BINDING FOR ALL LATER YEARS",
     "rule_type": "validation", "sort_order": 17,
     "formula": ("election is made on FORM 84-381, not by checking a box on the return ; "
                 "valid for the current taxable year AND EACH TAXABLE YEAR THEREAFTER until revoked on a "
                 "'Removing PTE' 84-381 ; annual re-filing is NOT required ; "
                 "CANNOT be made retroactively by amending a filed return ; "
                 "requires a governance vote (>50% of voting control, plus the governing body) ; "
                 "FIDUCIARIES ARE NOT ELIGIBLE TO ELECT (but CAN receive the credit) ; "
                 "a copy of Form 84-381 and every Form 84-132 must be attached to the 84-105"),
     "inputs": ["ptet_election_84381_on_file", "ptet_election_effective_date", "ptet_vote_attestation", "filing_mode"],
     "outputs": ["election_status"],
     "description": "W9 — CLIENT-ADVICE EXPOSURE, not just a spec question. Confirmed at four independent levels: "
                    "HB 1691 §1(1)(b) (2022), the current codified §27-7-26(1)(b), the TY2025 84-100 booklet p.22, "
                    "and the printed instructions on the election form's own face. DOR EPTE FAQs (3/4/2024): 'Once "
                    "the Pass-Through Entity Return is filed, it cannot be amended to make a pass-through entity "
                    "election.' The product needs a hard confirmation before the EPTE box can be checked, an 84-381 "
                    "attachment check, and a STANDING PER-CLIENT FLAG that the election persists into every later "
                    "year. Form 84-381 alone CAN be filed through TAP even though the return cannot."},
    {"rule_id": "R-MS-PTET-CREDIT", "title": "The owner-side PTET credit — REPORTED income, credit in the PAYMENTS block",
     "rule_type": "calculation", "sort_order": 18,
     "formula": ("84-131 Column D per owner = 84-105 L8 x that owner's ownership % (four decimals; Column B must "
                 "total 100%) ; 84-132 Part V delivers it ; "
                 "owner files 84-161 (business) or 80-161 (individual/fiduciary): "
                 "L5 = MIN(L3D, L4) ; L6 = L3D - L5 (excess) ; "
                 "L3D lands on: 80-105 L26 (resident individual) / 80-205 L28 (nonresident or part-year) / "
                 "81-110 L8 (FIDUCIARY — cannot elect, CAN receive) / 84-105 L12 / 83-105 L12"),
     "inputs": ["owner_ptet_tax_paid_l3d", "owner_total_ms_tax_l4", "owner_type_for_credit_landing", "8"],
     "outputs": ["131-L4a", "131-L5", "132-PtV", "161-L3D", "161-L5", "161-L6"],
     "description": "W11. §27-7-26(1)(c) current codified text: the owner 'SHALL REPORT' the share and it 'shall be "
                    "used in computing the taxpayer's gross income tax liability', then takes a CREDIT — MS "
                    "REPORTS AND CREDITS, NEVER EXCLUDES. Excess is carried forward as an overpayment OR REFUNDED "
                    "AT THE OWNER'S ELECTION (now statutory, not just FAQ). Owner BASIS is computed as if no "
                    "election were made. A nonresident whose only MS income is from the electing PTE need not file "
                    "a MS nonresident return. Limitations on the OTHER credits apply at the owner level."},
    {"rule_id": "R-MS-ESTIMATES", "title": "⚠ Estimates and underestimate — the safe harbour forks on MODE x ENTITY",
     "rule_type": "routing", "sort_order": 19,
     "formula": ("estimates required if annual income tax liability EXCEEDS $200 ; "
                 "COMPOSITE PARTNERSHIP -> Form 80-320 L11: 80% current-year test, CALENDAR instalments "
                 "(Apr 15 / Jun 15 / Sep 15 / Jan 15), interest only at 1/2%/month, NO 10% PENALTY ; "
                 "EVERYTHING ELSE (S corps in either mode, electing-PTE partnerships) -> Form 83-305 L19: "
                 "90% current-year test, instalments on the 15th of the 4th/6th/9th/12th month, "
                 "10% penalty PLUS 1/2 of 1% per month ; "
                 "large-entity bar: MS taxable income >= $1,000,000 in any of the three preceding years"),
     "inputs": ["entity_type", "filing_mode", "8"], "outputs": ["15"],
     "description": "⚠ [CORRECTED — verification pass] The research pass stated a flat 90% and calendar-agnostic "
                    "dates for BOTH modules; both faces were retrieved and they disagree. A composite partnership's "
                    "underestimate exposure is computed on an 80% safe harbour, on calendar quarters, with no 10% "
                    "penalty — THREE differences from every other filer on this form. DO NOT CODE ONE UNDERESTIMATE "
                    "ROUTINE. Authority for the exceptions: 35 Miss. Admin. Code Pt.III Subpt.11 Ch.21 §101, with "
                    "'the entity may not use more than one exception'. RED-defer R11a/R11b."},
    {"rule_id": "R-MS-WITHHOLD", "title": "⚠ Nonresident backstops — 84-380 (S corp) vs 84-387 (partnership)",
     "rule_type": "conditional", "sort_order": 20,
     "formula": ("S CORP: every nonresident shareholder executes Form 84-380, RETAINED by the corporation and NOT "
                 "FILED. On failure the corporation owes a FLAT 5% (the highest marginal rate under §27-7-5) x that "
                 "shareholder's pro-rata MS income, reported through 84-105 L5 ; "
                 "PARTNERSHIP: no agreement regime — the partnership and general partners are JOINTLY AND SEVERALLY "
                 "liable UNLESS the partnership withholds 5% of the net gain or profit and remits it on Form "
                 "84-387, from MISSISSIPPI SOURCE INCOME ONLY ; partners claim it as ESTIMATED TAX and it is "
                 "REFUNDABLE if their liability is lower ; surfaced on 84-132 Box G"),
     "inputs": ["entity_type", "nonresident_owners_present", "form_84380_agreements_on_file",
                "form_84387_backstop_remitted", "partnership_net_gain_or_profit"],
     "outputs": ["5", "387-L2"],
     "description": "Two different, unrelated 5% backstops on the same form, one per module. ⚠ U15/R9: L5 is "
                    "instructed to carry 'the income on which payment of tax is required', but L6 then applies the "
                    "0/4/5 schedule while the statutory charge is a FLAT 5% of that income — on a shareholder share "
                    "under $10,000 the two differ, and DOR does not say which governs. RED-defer. Do NOT confuse "
                    "either with the separate 5% a NONRESIDENT SELLER remits on MS real property over $100,000."},
    {"rule_id": "R-MS-CREDITS", "title": "Form 84-401 — the credit summary grid (Part I -> L3, Part II -> L7)",
     "rule_type": "calculation", "sort_order": 21,
     "formula": "per credit row: (B + C + D - E - F) = G ; Part I total -> 84-105 L3 (franchise) ; "
                "Part II total -> 84-105 L7 (income)  ⚠ PER THE FACE — E2, the instruction's 'Form 83-401' is the "
                "CORPORATE series",
     "inputs": ["franchise_tax_credit_84401", "income_tax_credits_84401"], "outputs": ["3", "7"],
     "description": "RED-defer R13: 60 credit codes, amounts direct-entry, NO per-credit computation and NO caps "
                    "enforced in v1 (including the 50%-of-liability Jobs Tax Credit cap and the MDA-certification "
                    "credits). DOR EPTE FAQ: incentive credits are NOT tax payments, and if claimed at entity level "
                    "they CANNOT also flow through — 'The incentive credits can only be taken on one return.'"},
    {"rule_id": "R-MS-84115", "title": "Form 84-115 (MS8453-PTE) Part I — seven computed tie-outs against 84-105",
     "rule_type": "calculation", "sort_order": 22,
     "formula": ("115-L1 = 84-105 L5 ; 115-L2 = 84-105 L6 ; 115-L3 = 84-105 L7 + L13 ; 115-L4 = 84-105 L19 ; "
                 "115-L5 = 84-105 L20 ; 115-L6 = 84-105 L22 ; 115-L7 = amount of payment remitted electronically"),
     "inputs": ["5", "6", "7", "13", "19", "20", "22"], "outputs": ["115-L1", "115-L7"],
     "description": "⚠ [ADDED — verification pass] The form the research pass missed entirely. The Mississippi "
                    "e-file signature declaration, the state analogue of federal Form 8453. NOT optional: it "
                    "carries its OWN COLUMN on the DOR's TY2025 approved-provider matrix, so a vendor's product is "
                    "approved for it separately. Face: 'DO NOT MAIL THIS DOCUMENT TO THE DEPARTMENT OF REVENUE' / "
                    "'This declaration is to be maintained by the ERO and provided to DOR on request.'"},
]

MS84105_RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R-MS-ENTITY-GATE", "MS_2025_FORM_84_105", "primary", "block header 'S CORPORATION FRANCHISE TAX'; page 2 Part I line 4"),
    ("R-MS-ENTITY-GATE", "MS_CODE_27_13_5", "secondary", "§27-13-5(1)(a) 'partnership treated as a corporation'"),
    ("R-MS-FRAN-CAPITAL", "MS_2025_FORM_84_110", "primary", "84-110 L1-L18 face, verbatim"),
    ("R-MS-FRANCHISE", "MS_CODE_27_13_5", "primary", "TY2025 75c ladder, $25 minimum, no 2028 clause"),
    ("R-MS-FRANCHISE", "MS_2025_FORM_84_105", "secondary", "L2 instruction, TY2025-keyed; the Fee-In-Lieu checkbox"),
    ("R-MS-ENGINE-122", "MS_2025_FORM_84_122", "primary", "84-122 face, 35 lines; L28 per the face (E4)"),
    ("R-MS-DEPR", "MS_2025_FORM_84_122", "primary", "⚠ L8 add-back / L15 recovery, positional read of the FINAL face"),
    ("R-MS-DEPR", "MS_CODE_27_7_17", "primary", "§27-7-17(1)(f)(ii)2 MS's own 100% bonus; 1/1/2021 freeze; 100% cap"),
    ("R-MS-DEPR", "MS_2025_84_100_INSTR", "secondary", "dual-Form-4562 mechanic; 'reported on line 15 of this form'"),
    ("R-MS-DEPR-AVIATN", "MS_CODE_27_7_17", "primary", "§27-7-17(1)(f)(i) aviation conforms to FEDERAL bonus rates"),
    ("R-MS-179", "MS_CODE_27_7_17", "primary", "§27-7-17(1)(f)(ii)3 §179 'in effect for that year' (ROLLING)"),
    ("R-MS-179", "MS_2025_84_100_INSTR", "secondary", "84-132 Box 13 'Mississippi Section 179 deduction' (U13)"),
    ("R-MS-APPORT", "MS_2025_FORM_84_125", "primary", "Part I factors + Part II four formulas; 1e rental x 8"),
    ("R-MS-APPORT", "MS_ADMIN_CODE_35_PT3", "primary", "§§402.01-402.09; the pipeline and FI divergences"),
    ("R-MS-APPORT", "MS_2025_83_100_INSTR", "interpretive", "the five-factor pharmaceutical rule, absent from 84-100 (U6)"),
    ("R-MS-THROWBACK", "MS_ADMIN_CODE_35_PT3", "primary", "⚠ §402.09(3)(b)(ii)/(vii)/(viii), (3)(c), §202.06 P.L. 86-272"),
    ("R-MS-TERMINAL", "MS_2025_FORM_84_122", "primary", "L29-L32 composite / L33-L35 EPTE, both zero floors"),
    ("R-MS-TERMINAL", "MS_2025_FORM_84_131_132", "secondary", "84-131 line 4a — only owners with COMPOSITE checked"),
    ("R-MS-NOL", "MS_2025_84_100_INSTR", "primary", "MS NOL 2 back / 20 forward; irrevocable forgo-carryback election"),
    ("R-MS-INCOME-TAX", "MS_2025_84_100_INSTR", "primary", "84-100 p.7 Tax Rates + the 84-105 L6 instruction (0/4/5)"),
    ("R-MS-INCOME-TAX", "MS_2025_FORM_84_105", "secondary", "L6-L8 face labels; L8 zero floor"),
    ("R-MS-COMP-RATE", "MS_ADMIN_CODE_35_PT3", "primary", "⚠ POSITION C — §112.03 and the partnership Composite chapter"),
    ("R-MS-COMP-RATE", "MS_2025_84_100_INSTR", "secondary", "POSITION A — DOR's 0/4/5, stated twice, TY2025-keyed"),
    ("R-MS-FISCAL-PROR", "MS_2025_84_100_INSTR", "primary", "§27-7-5(4) restated verbatim on the 84-105 L6 instruction"),
    ("R-MS-FORK-L9", "MS_2025_FORM_84_105", "primary", "⚠ L9 face label 'line 4 plus line 8'"),
    ("R-MS-FORK-L9", "MS_2025_84_100_INSTR", "primary", "⚠ the L9 instruction states the entity fork verbatim"),
    ("R-MS-PAYMENTS", "MS_2025_FORM_84_105", "primary", "L13-L22 face; the L20 asymmetry; E3 build-to-face"),
    ("R-MS-PTET-ELECT", "MS_2025_FORM_84_381", "primary", "the form's own printed instructions; vote attestation"),
    ("R-MS-PTET-ELECT", "MS_CODE_27_7_26_PTET", "primary", "§27-7-26(1)(b) binding for all subsequent taxable years"),
    ("R-MS-PTET-CREDIT", "MS_CODE_27_7_26_PTET", "primary", "§27-7-26(1)(c) report + credit; excess refundable"),
    ("R-MS-PTET-CREDIT", "MS_2025_FORM_84_161", "primary", "L3D landing lines incl. 81-110 L8; L5/L6 arithmetic"),
    ("R-MS-PTET-CREDIT", "MS_2025_FORM_84_131_132", "secondary", "84-131 Column D = 84-105 L8 x ownership%; 84-132 Part V"),
    ("R-MS-ESTIMATES", "MS_2025_FORM_83305_80320", "primary", "⚠ the 90% vs 80% safe-harbour fork, both faces"),
    ("R-MS-ESTIMATES", "MS_2025_FORM_84_105", "secondary", "L15 face: '(composite partnerships only)'"),
    ("R-MS-WITHHOLD", "MS_2025_84_100_INSTR", "primary", "84-380 retained agreement (pp.5-6); 84-387 5% backstop (p.6)"),
    ("R-MS-CREDITS", "MS_2025_FORM_84_105", "primary", "L3 / L7 face cite Form 84-401 (E2 — not 83-401)"),
    ("R-MS-84115", "MS_2025_FORM_84_115", "primary", "Part I lines 1-7 tie-outs, verbatim"),
    ("R-MS-84115", "MS_2025_PTE_APPROVED_PROVIDERS", "implementation", "84-115 has its own approval column (U17)"),
]

MS84105_LINES: list[dict] = [
    # ── 84-105 face: S CORPORATION FRANCHISE TAX (S corps only) ──
    {"line_number": "1", "description": "Taxable capital (from Form 84-110, line 18) — S CORPORATIONS ONLY", "line_type": "calculated",
     "source_rules": ["R-MS-FRAN-CAPITAL", "R-MS-ENTITY-GATE"], "sort_order": 1,
     "notes": "⚠ HARD-GATED on the entity-type radio. A partnership return must never carry a value here."},
    {"line_number": "2", "description": "Franchise tax (minimum tax $25) — with the Fee-In-Lieu checkbox", "line_type": "calculated",
     "source_rules": ["R-MS-FRANCHISE"], "sort_order": 2,
     "notes": "TY2025 $0.75 per $1,000 of capital in excess of $100,000. Fee-In-Lieu SUPPRESSES this computation (R6)."},
    {"line_number": "3", "description": "Franchise tax credit (from Form 84-401, line 1)", "line_type": "input",
     "source_facts": ["franchise_tax_credit_84401"], "sort_order": 3},
    {"line_number": "4", "description": "Net franchise tax due (line 2 minus line 3) — MAX(0, L2 - L3)", "line_type": "calculated",
     "source_rules": ["R-MS-FRANCHISE"], "sort_order": 4},
    # ── COMPOSITE / ELECTING PASS-THROUGH ENTITY INCOME TAX ──
    {"line_number": "5", "description": "Mississippi net taxable income (84-122 line 32 composite OR line 35 electing PTE)",
     "line_type": "calculated", "source_rules": ["R-MS-TERMINAL", "R-MS-WITHHOLD"], "sort_order": 5,
     "notes": "⚠ A THIRD trigger that is neither mode: an S corp that failed to obtain a Form 84-380 agreement "
              "enters here the income on which payment of tax is required (U15)."},
    {"line_number": "6", "description": "Income tax — EPTE 0/4/5 computed; COMPOSITE rate UNRESOLVED (W1, direct-entry)",
     "line_type": "calculated", "source_rules": ["R-MS-INCOME-TAX", "R-MS-COMP-RATE", "R-MS-FISCAL-PROR"], "sort_order": 6,
     "notes": "⚠ The form face carries NO rate — it lives only in the instruction and is tax-year-keyed."},
    {"line_number": "7", "description": "Income tax credits (from Form 84-401, line 3) — E2: NOT Form 83-401",
     "line_type": "input", "source_facts": ["income_tax_credits_84401"], "sort_order": 7},
    {"line_number": "8", "description": "Net income tax due (line 6 minus line 7) — MAX(0, L6 - L7)", "line_type": "calculated",
     "source_rules": ["R-MS-INCOME-TAX"], "sort_order": 8,
     "notes": "Also the base for 84-131 Column D (per-owner PTET credit) and Form 83-305 line 1."},
    # ── PAYMENTS AND TAX DUE ──
    {"line_number": "9", "description": "⚠ THE FORK — total franchise and/or income tax: L4 + L8 (S corp) vs L8 (partnership)",
     "line_type": "subtotal", "source_rules": ["R-MS-FORK-L9"], "sort_order": 9},
    {"line_number": "10", "description": "Overpayments from prior year", "line_type": "input",
     "source_facts": ["prior_year_overpayment"], "sort_order": 10},
    {"line_number": "11", "description": "Estimated tax payments and payment with extension", "line_type": "input",
     "source_facts": ["estimated_and_extension_payments"], "sort_order": 11},
    {"line_number": "12", "description": "⚠ TIERING — credit for tax paid on an electing PTE return (84-161 line 3D)",
     "line_type": "input", "source_facts": ["lower_tier_ptet_credit_84161_l3d"], "sort_order": 12,
     "notes": "The upper tier need NOT elect itself. Must attach the K-1(s) received. PTET credit sits in PAYMENTS."},
    {"line_number": "13", "description": "Total payments (line 10 plus line 11 and line 12)", "line_type": "subtotal",
     "source_rules": ["R-MS-PAYMENTS"], "sort_order": 13},
    {"line_number": "14", "description": "Net total franchise tax and/or income tax (line 9 minus line 13)",
     "line_type": "subtotal", "source_rules": ["R-MS-PAYMENTS"], "sort_order": 14},
    {"line_number": "15", "description": "Underestimate interest and penalty (83-305 L19 OR 80-320 L11, composite partnerships only)",
     "line_type": "input", "source_facts": ["underestimate_interest_penalty_l15"], "sort_order": 15,
     "notes": "⚠ MODE x ENTITY fork, and the two forms do NOT compute the same safe harbour (90% vs 80%)."},
    {"line_number": "16", "description": "Late payment interest (1/2 of 1% per month)", "line_type": "input",
     "source_facts": ["late_payment_interest"], "sort_order": 16},
    {"line_number": "17", "description": "Late payment penalty (1/2% per month, max 25%)", "line_type": "input",
     "source_facts": ["late_payment_penalty"], "sort_order": 17},
    {"line_number": "18", "description": "Late filing penalty (minimum income tax penalty $100)", "line_type": "input",
     "source_facts": ["late_filing_penalty"], "sort_order": 18},
    {"line_number": "19", "description": "Total balance due (if line 9 > line 13, add line 14 through line 18) — E3",
     "line_type": "total", "source_rules": ["R-MS-PAYMENTS"], "sort_order": 19},
    {"line_number": "20", "description": "⚠ ASYMMETRY — total overpayment: L13 - L9 - L15 (L16-L18 NOT netted)",
     "line_type": "total", "source_rules": ["R-MS-PAYMENTS"], "sort_order": 20},
    {"line_number": "21", "description": "Overpayment credited to next year (from line 20)", "line_type": "input",
     "source_facts": ["overpayment_credited_next_year"], "sort_order": 21},
    {"line_number": "22", "description": "Overpayment to be refunded (line 20 minus line 21)", "line_type": "total",
     "source_rules": ["R-MS-PAYMENTS"], "sort_order": 22},
    # ── Form 84-110 (franchise capital) ──
    {"line_number": "110-L8", "description": "84-110 L8 Total capital base (add line 1 through line 7; U16 sign convention)",
     "line_type": "subtotal", "source_rules": ["R-MS-FRAN-CAPITAL"], "sort_order": 30},
    {"line_number": "110-L12", "description": "84-110 L12 Mississippi ratio — PROPERTY + GROSS RECEIPTS (a second engine)",
     "line_type": "calculated", "source_rules": ["R-MS-FRAN-CAPITAL"], "sort_order": 31},
    {"line_number": "110-L13", "description": "84-110 L13 Taxable capital apportioned to Mississippi (L8 x L12)",
     "line_type": "calculated", "source_rules": ["R-MS-FRAN-CAPITAL"], "sort_order": 32},
    {"line_number": "110-L15", "description": "84-110 L15 Taxable capital — GREATER OF L13 or L14 (assessed-value floor)",
     "line_type": "calculated", "source_rules": ["R-MS-FRAN-CAPITAL"], "sort_order": 33},
    {"line_number": "110-L18", "description": "84-110 L18 Final taxable capital, ROUNDED UP to the next $1,000 -> 84-105 L1",
     "line_type": "total", "source_rules": ["R-MS-FRAN-CAPITAL"], "destination_form": "MS_84_105 line 1", "sort_order": 34},
    # ── Form 84-122 (the engine) — the four lines that must not be confused ──
    {"line_number": "122-L6", "description": "84-122 L6 Interest on obligations of OTHER states — MUNICIPAL BOND INTEREST",
     "line_type": "input", "source_facts": ["add_other_state_muni_interest"], "sort_order": 40,
     "notes": "⚠ NOT DEPRECIATION. Recorded explicitly so no future pass re-routes the bonus add-back here."},
    {"line_number": "122-L8", "description": "84-122 L8 FEDERAL SPECIAL DEPRECIATION ALLOWANCE — THE ADD-BACK (+)",
     "line_type": "input", "source_facts": ["add_federal_special_depreciation"], "source_rules": ["R-MS-DEPR"], "sort_order": 41,
     "notes": "⚠ Verified positionally off the FINAL TY2025 84-122 face. Also the landing line for the MS bonus "
              "election and (per the L8 instruction) the R&E election."},
    {"line_number": "122-L13", "description": "84-122 L13 Income (loss) from partnership, S corp or trust — FLOW-THROUGH REMOVAL",
     "line_type": "input", "source_facts": ["ded_flowthrough_income_removed"], "sort_order": 42,
     "notes": "⚠ NOT DEPRECIATION. Re-inserted, already sourced, at L24."},
    {"line_number": "122-L15", "description": "84-122 L15 ADDITIONAL DEPRECIATION from the unreduced MS basis — THE RECOVERY (-)",
     "line_type": "input", "source_facts": ["ded_additional_ms_depreciation"], "source_rules": ["R-MS-DEPR"], "sort_order": 43,
     "notes": "⚠ RECURS EVERY YEAR until the asset is fully recovered. Not a same-year wash with L8."},
    {"line_number": "122-L18", "description": "84-122 L18 Adjusted federal income (line 4 plus line 10 minus line 17)",
     "line_type": "subtotal", "source_rules": ["R-MS-ENGINE-122"], "sort_order": 44},
    {"line_number": "122-L21", "description": "84-122 L21 Apportionment ratio (from Form 84-125 Part II, category box mirrored)",
     "line_type": "calculated", "source_rules": ["R-MS-APPORT"], "sort_order": 45},
    {"line_number": "122-L22", "description": "84-122 L22 MS apportioned income (= L18 if 100% Mississippi, else L20 x L21)",
     "line_type": "calculated", "source_rules": ["R-MS-ENGINE-122"], "sort_order": 46},
    {"line_number": "122-L28", "description": "84-122 L28 Total MS income — ADD L22 THROUGH L26 MINUS L27 (per the FACE, E4)",
     "line_type": "subtotal", "source_rules": ["R-MS-ENGINE-122"], "sort_order": 47},
    {"line_number": "122-L30", "description": "84-122 L30 Composite return filing adjustment ($5,000 / 10% — BASE CONTESTED, U7)",
     "line_type": "input", "source_facts": ["composite_filing_adjustment_l30"], "sort_order": 48},
    {"line_number": "122-L32", "description": "84-122 L32 Composite net taxable income (L29 - L30 - L31; zero floor) -> 84-105 L5",
     "line_type": "total", "source_rules": ["R-MS-TERMINAL"], "destination_form": "MS_84_105 line 5", "sort_order": 49},
    {"line_number": "122-L35", "description": "84-122 L35 Electing PTE net taxable income (L33 - L34; zero floor) -> 84-105 L5",
     "line_type": "total", "source_rules": ["R-MS-TERMINAL"], "destination_form": "MS_84_105 line 5", "sort_order": 50,
     "notes": "⚠ L33 = L28 IN FULL — the EPTE is taxed on ALL Mississippi income, every owner, resident and not."},
    # ── Form 84-125 (apportionment) ──
    {"line_number": "125-L1e", "description": "84-125 L1e Rental property — annual rental property MULTIPLIED BY EIGHT",
     "line_type": "calculated", "source_rules": ["R-MS-APPORT"], "sort_order": 60},
    {"line_number": "125-L3", "description": "84-125 L3 Sales factor — destination + THROWBACK + drop-ship + U.S. Gov origin",
     "line_type": "calculated", "source_rules": ["R-MS-THROWBACK"], "sort_order": 61},
    {"line_number": "125-L4", "description": "84-125 L4 SINGLE SALES FACTOR (retailing, renting, servicing, merchandising, wholesaling)",
     "line_type": "calculated", "source_rules": ["R-MS-APPORT"], "sort_order": 62},
    {"line_number": "125-L5g", "description": "84-125 L5g Weighted average — manufacturers selling principally at RETAIL",
     "line_type": "calculated", "source_rules": ["R-MS-APPORT"], "sort_order": 63},
    {"line_number": "125-L6e", "description": "84-125 L6e Equal-weighted three-factor — wholesale mfrs, FI, pipelines",
     "line_type": "calculated", "source_rules": ["R-MS-APPORT"], "sort_order": 64,
     "notes": "⚠ U4 financial institutions (no reg formula exists) and U5 pipelines (reg uses TRAFFIC MILES) both "
              "sit on this line and are RED-deferred (R3/R4)."},
    {"line_number": "125-L7", "description": "84-125 L7 Special formula required — airlines, motor carriers, express, telephone/telegraph",
     "line_type": "informational", "sort_order": 65, "notes": "RED-defer R2 — attach schedule, prepare manually."},
    # ── owner delivery + companions ──
    {"line_number": "131-L4a", "description": "84-131 Column C line 4a Composite net income -> 84-122 L29 (COMPOSITE owners only)",
     "line_type": "subtotal", "source_rules": ["R-MS-PTET-CREDIT"], "destination_form": "84-122 line 29", "sort_order": 70},
    {"line_number": "131-L5", "description": "84-131 Column D line 5 Total tax paid by electing PTE (= 84-105 L8 allocated)",
     "line_type": "subtotal", "source_rules": ["R-MS-PTET-CREDIT"], "sort_order": 71},
    {"line_number": "132-PtV", "description": "84-132 Part V — tax paid by the electing PTE on this owner's share",
     "line_type": "calculated", "source_rules": ["R-MS-PTET-CREDIT"], "sort_order": 72},
    {"line_number": "132-B13", "description": "84-132 Box 13 MISSISSIPPI §179 deduction (direct-entry — W10/U13)",
     "line_type": "input", "source_facts": ["ms_section_179_deduction"], "source_rules": ["R-MS-179"], "sort_order": 73},
    {"line_number": "155-L2", "description": "84-155 L2 MS NOL used in the current year -> 84-122 L31 (composite) or L34 (EPTE)",
     "line_type": "calculated", "source_rules": ["R-MS-NOL"], "sort_order": 74},
    {"line_number": "161-L3D", "description": "84-161/80-161 L3D total tax paid on electing PTE returns -> the PAYMENTS block",
     "line_type": "subtotal", "source_rules": ["R-MS-PTET-CREDIT"], "sort_order": 75,
     "notes": "Lands on 80-105 L26 / 80-205 L28 / 81-110 L8 (fiduciary) / 84-105 L12 / 83-105 L12."},
    {"line_number": "161-L5", "description": "84-161/80-161 L5 Credit allowed — the LESSER of line 3D or line 4",
     "line_type": "calculated", "source_rules": ["R-MS-PTET-CREDIT"], "sort_order": 76},
    {"line_number": "161-L6", "description": "84-161/80-161 L6 EXCESS credit (L3D - L5) — refunded or carried forward at the OWNER's election",
     "line_type": "calculated", "source_rules": ["R-MS-PTET-CREDIT"], "sort_order": 77},
    {"line_number": "115-L1", "description": "84-115 (MS8453-PTE) Part I L1 — Mississippi taxable income (84-105 line 5)",
     "line_type": "calculated", "source_rules": ["R-MS-84115"], "sort_order": 80},
    {"line_number": "115-L4", "description": "84-115 Part I L4 — Amount you owe (84-105 line 19)",
     "line_type": "calculated", "source_rules": ["R-MS-84115"], "sort_order": 81},
    {"line_number": "115-L6", "description": "84-115 Part I L6 — Refund (84-105 line 22); print and retain, NEVER mailed",
     "line_type": "calculated", "source_rules": ["R-MS-84115"], "sort_order": 82},
    {"line_number": "387-L2", "description": "84-387 L2 — 5% of net gain or profit remitted by the partnership (backstop)",
     "line_type": "calculated", "source_rules": ["R-MS-WITHHOLD"], "sort_order": 83,
     "notes": "Partners claim it as ESTIMATED TAX; refundable. Surfaced on 84-132 Box G. RED-defer R10."},
]

MS84105_DIAGNOSTICS: list[dict] = [
    # ═══ WALK ITEMS / structural reviews ═══
    {"diagnostic_id": "D_MS84105_COMPOSITE_RATE", "severity": "warning",
     "title": "⚠ Composite rate is UNRESOLVED — three-sided conflict, no rate is computed (W1/U1)",
     "condition": "filing_mode == 'composite'",
     "message": "Mississippi's composite rate is genuinely contested and this product does NOT choose. (A) MS DOR "
                "prescribes 0% / 4% / 5%, twice, TY2025-keyed. (B) Miss. Code Ann. §27-7-5(1)(b) reduces the rate "
                "for INDIVIDUALS only and composite members are nonresident individuals — 0% / 4.4%. (C) The "
                "official 35 Miss. Admin. Code Title 35 Part III packages the $5,000/10% deduction WITH the "
                "individual rate and the corporate rate WITH NO deduction, and offers no corporate-rate route for "
                "partnerships at all — while the TY2025 forms take one half of each. Enter Form 84-105 line 6 "
                "manually and open a DOR ticket before filing.",
     "notes": "W1 is the #1 walk item. Recommendation for the walk: ship DOR's 0/4/5 as a SINGLE-POINT-OF-CHANGE "
              "flagged constant. DO NOT RESOLVE THIS BY CHOOSING inside the loader."},
    {"diagnostic_id": "D_MS84105_FRANCHISE_FORK", "severity": "error",
     "title": "⚠ Franchise tax (lines 1-4) is S-CORPORATION ONLY — a partnership must not carry a value here",
     "condition": "entity_type == '1065' AND any of lines 1-4 is non-zero",
     "message": "Form 84-105 lines 1 through 4 are the S CORPORATION FRANCHISE TAX block. Partnerships, LLCs and "
                "LLPs are not subject to the Mississippi franchise tax and must leave lines 1-4 blank. Because the "
                "franchise tax carries a $25 MINIMUM, a partnership return that lands here files a non-zero tax it "
                "does not owe — silently. Clear lines 1-4 and Form 84-110.",
     "notes": "W2. Hard gate, not a soft prompt."},
    {"diagnostic_id": "D_MS84105_DEPR_L8_L15", "severity": "warning",
     "title": "⚠ Depreciation belongs on 84-122 LINE 8 (add-back) and LINE 15 (MS-basis recovery)",
     "condition": "federal_4562_shows_special_allowance AND 84-122 line 8 is blank",
     "message": "Federal Form 4562 shows a special depreciation allowance but Form 84-122 line 8 is blank. The "
                "federal special depreciation allowance is added back on LINE 8; the additional Mississippi "
                "depreciation arising because Mississippi never reduced the asset's basis is deducted on LINE 15. "
                "Line 6 is municipal-bond interest and line 13 is flow-through income — neither is a depreciation "
                "line. Federal Form 4562 must be completed twice, the second copy labeled 'Mississippi'.",
     "notes": "⚠ THE ERROR THIS SPEC EXISTS TO PREVENT. Verified positionally off the FINAL TY2025 84-122 face and "
              "confirmed by DOR's own line 8 instruction. W3."},
    {"diagnostic_id": "D_MS84105_DEPR_RECURRING", "severity": "info",
     "title": "Mississippi keeps an UNREDUCED basis — line 15 recurs every year, it is not a same-year wash",
     "condition": "any asset with a federal special depreciation allowance exists",
     "message": "Because Mississippi does not reduce an asset's depreciable base by the federal special "
                "depreciation allowance, the extra Mississippi depreciation on Form 84-122 line 15 RECURS EVERY "
                "YEAR until the asset is fully recovered. Maintain the separate 'Mississippi' Form 4562 ledger for "
                "the life of every affected asset. A spec treating lines 8 and 15 as a same-year wash is wrong from "
                "year two onward.",
     "notes": "W3 / R7."},
    {"diagnostic_id": "D_MS84105_PTET_BINDING", "severity": "warning",
     "title": "⚠ The Mississippi PTET election BINDS EVERY LATER YEAR and cannot be made by amending",
     "condition": "filing_mode == 'electing_pte'",
     "message": "The electing-PTE status is valid for the current taxable year AND EACH TAXABLE YEAR THEREAFTER "
                "until it is affirmatively revoked on a 'Removing PTE' Form 84-381 — annual re-filing is not "
                "required and the election does not lapse. It is made on Form 84-381, not by checking a box on this "
                "return, and once the return is filed IT CANNOT BE AMENDED TO MAKE THE ELECTION. It requires a vote "
                "or written consent of owners holding greater than 50% of voting control (and of the governing body "
                "where one exists). Fiduciaries are not eligible to elect. Confirm with the client before checking "
                "the Electing Pass-Through Entity box.",
     "notes": "W9 — client-advice exposure, confirmed at four independent authority levels."},
    {"diagnostic_id": "D_MS84105_THROWBACK", "severity": "warning",
     "title": "⚠ Mississippi HAS a sales-factor throwback rule — P.L. 86-272 protection triggers it",
     "condition": "multistate apportioning AND sales shipped from a Mississippi location",
     "message": "Sales shipped from a Mississippi office, store, warehouse, factory or other place of storage into a "
                "state where the entity is NOT TAXABLE are thrown back into the Mississippi sales numerator "
                "(35 Miss. Admin. Code Pt. III §402.09(3)(b)(ii) and (vii)). 'Not taxable' includes a state where "
                "the entity is protected by Public Law 86-272 (§202.06). Drop shipments follow (viii). ALL sales to "
                "the United States Government shipped from a Mississippi location are Mississippi sales "
                "unconditionally (§402.09(3)(c)). The rule appears on no form and in no booklet.",
     "notes": "W5. Verified from the OFFICIAL Mississippi SOS Administrative Code capture, not a mirror."},
    {"diagnostic_id": "D_MS84105_FRANCHISE_ARITH", "severity": "info",
     "title": "Franchise arithmetic and the 84-110 sign convention are read off the form, not stated by DOR (W8)",
     "condition": "franchise block applies",
     "message": "Two assumptions to confirm: (a) franchise tax = MAX($25, rate x CEIL(MAX(0, capital - $100,000) / "
                "$1,000)), with the Form 84-110 line 18 round-up to the next $1,000 applied first — the interaction "
                "of that round-up with the statutory 'or fraction thereof' is untested; (b) Form 84-110 lines 6 "
                "(less treasury stock) and 7 (holding company exclusion) are treated as SUBTRACTIVE inside 'add "
                "line 1 through line 7'. Both silently change every small and every multistate S-corp return.",
     "notes": "W8 / U16."},
    {"diagnostic_id": "D_MS84105_ERRATA", "severity": "info",
     "title": "Five DOR form-vs-instruction errata — this product builds to the FORM FACE (W7)",
     "condition": "always (informational)",
     "message": "E1 the 84-132 Box 1 instruction cites federal lines that are 'Total deductions' on the FINAL 2025 "
                "IRS forms (build to 1120-S line 22 / 1065 line 23, as the 84-122 line 1 FACE does); E2 the 84-105 "
                "line 7 instruction cites Form 83-401 (the corporate series) where the face cites Form 84-401; "
                "E3 the line 19 instruction says 'if line 10 is larger than line 13' where the face says line 9; "
                "E4 the 84-122 line 28 instruction says 'sum lines 22 through 27' where the face says 'add line 22 "
                "through line 26 minus line 27'; E5 the 84-122 line 1 instruction carries Form 1120 line 28 "
                "boilerplate. All five build to the face.",
     "notes": "W7. Recorded so a future pass does not 'fix' them back into the error."},
    {"diagnostic_id": "D_MS84105_L20_ASYMMETRY", "severity": "info",
     "title": "Line 20 overpayment nets only lines 9 and 15 — late-payment items are NOT netted",
     "condition": "line 13 > line 9 plus line 15",
     "message": "Form 84-105 line 20 is computed as written on the face: 'if line 13 is larger than line 9 plus line "
                "15, subtract line 9 and line 15 from line 13'. The underestimate interest and penalty (line 15) is "
                "netted against the refund; the late-payment interest, late-payment penalty and late-filing penalty "
                "(lines 16-18) are NOT. Do not compute line 20 as line 13 minus line 19.",
     "notes": "Face-verified asymmetry."},
    {"diagnostic_id": "D_MS84105_84115_TIEOUT", "severity": "info",
     "title": "Form 84-115 (MS8453-PTE) is required, separately approval-gated, and never mailed",
     "condition": "return is filed electronically",
     "message": "Form 84-115, the Mississippi Pass-Through Entity Declaration for Electronic Filing, carries seven "
                "computed tie-outs against this return (lines 5, 6, 7+13, 19, 20, 22) plus the amount remitted "
                "electronically. It is retained by the ERO and provided to DOR on request — 'DO NOT MAIL THIS "
                "DOCUMENT TO THE DEPARTMENT OF REVENUE'. It appears as its own column on the DOR approved-provider "
                "matrix, so it is approval-gated separately from the return.",
     "notes": "⚠ [ADDED — verification pass] The research pass missed this form entirely."},
    {"diagnostic_id": "D_MS84105_EFILE_MANDATE", "severity": "warning",
     "title": "Mississippi e-file mandate — 100+ K-1s or $250,000 in assets",
     "condition": "total_mississippi_k1s >= 100 OR total_assets >= 250000",
     "message": "Mississippi mandates electronic filing for all corporations, S corporations and partnerships with "
                "assets of $250,000 or more and/or returns with 100 or more K-1s. Penalty $25 for the first "
                "instance and $500 for each additional. Corporate and pass-through returns cannot be filed through "
                "TAP — they go through an authorized software provider, with a complete copy of the federal return "
                "submitted electronically.",
     "notes": "§27-3-83; Title 35 Part I Chapter 4. Face notice on the 84-105."},
    {"diagnostic_id": "D_MS84105_FISCAL_YEAR", "severity": "info",
     "title": "Fiscal-year proration (§27-7-5(4)) — and the FRANCHISE rate changes every year",
     "condition": "the accounting period is not a calendar year",
     "message": "For a fiscal year spanning two calendar years with different rates, compute the full-year tax under "
                "each calendar year's rates and weight each by the months falling in that year. For an electing PTE "
                "in TY2025 this is a no-op (0/4/5 did not change between 2025 and 2026), but the FRANCHISE rate "
                "steps down every single year ($0.75 for 2025, $0.50 for 2026), so the same proration is live on "
                "the franchise side with a different answer.",
     "notes": "Printed verbatim on the 84-105 L6 instruction."},
    {"diagnostic_id": "D_MS84105_INACTIVE_SCORP", "severity": "info",
     "title": "An inactive S corporation still files — and still owes the $25 franchise minimum",
     "condition": "entity_type == '1120S' AND is_inactive_s_corp",
     "message": "Every S corporation domesticated or qualified to do business in Mississippi must file a return even "
                "if inactive, and remains subject to the filing requirement until it is officially dissolved or "
                "withdrawn through the Office of the Mississippi Secretary of State. The $25 franchise minimum "
                "applies. This is a real filing mode, not an edge case.",
     "notes": "84-100 p.3."},
    {"diagnostic_id": "D_MS84105_EXEMPT_UBTI", "severity": "info",
     "title": "Exempt organization with UBTI — file 84-105, leave lines 1-4 blank",
     "condition": "is_exempt_org_with_ubti",
     "message": "An exempt organization with unrelated business taxable income files Form 84-105, is NOT subject to "
                "the franchise tax levy, and should leave lines 1 through 4 blank. Enter the federal Form 990-T "
                "UBTI on Form 84-122 line 1. This is a third filer shape inside the same form.",
     "notes": "84-100 p.10. A second exception to the franchise gate."},
    {"diagnostic_id": "D_MS84105_CAPLOSS_LIMIT", "severity": "info",
     "title": "84-122 line 2 capital-loss limiter exists only in the instruction",
     "condition": "Schedule K carries capital losses",
     "message": "Long-term and short-term capital losses are included on Form 84-122 line 2 only to the extent of "
                "current-year capital gains. This entity-level netting rule has no federal analogue on Schedule K, "
                "and it interacts with the Mississippi rule that capital GAIN is taxed as ORDINARY INCOME.",
     "notes": "84-100 p.18; 84-132 Box 9b instruction."},
    {"diagnostic_id": "D_MS84105_NOL_OPEN", "severity": "warning",
     "title": "MS NOL — two open questions DOR does not answer (U8, U9)",
     "condition": "ms_nol_deduction_84155_l2 is non-zero",
     "message": "Mississippi does not conform to federal NOL rules: 2-year carryback, 20-year carryforward, and a "
                "short year counts as a year. Two points are unresolved: (U8) Form 84-122 lines 31 and 34 both draw "
                "from Form 84-155 line 2 while the line 31 instruction calls it a 'separate company composite' NOL "
                "— whether one entity can hold two distinct pools, and how a mode change between years is handled, "
                "is unstated; (U9) whether the NOL is applied pre- or post-apportionment is unstated, and this "
                "product follows the form's arithmetic (POST). Form 84-155 must be attached or the deduction is "
                "not allowed; the forgo-carryback election is irrevocable.",
     "notes": "U8/U9 — Ken should bless the post-apportionment reading rather than the spec assuming it."},
    {"diagnostic_id": "D_MS84105_MS179", "severity": "warning",
     "title": "Mississippi §179 on 84-132 Box 13 is not derived by any Mississippi form (W10/U13)",
     "condition": "federal Form 4562 shows a §179 deduction AND 84-132 Box 13 is blank",
     "message": "Mississippi conforms to IRC §179 'in effect for that year' (TY2025: $2,500,000 limit, $4,000,000 "
                "phaseout, $31,300 SUV sub-limit) and requires the owner's share of the MISSISSIPPI §179 deduction "
                "on Form 84-132 Box 13 — but no Mississippi form line computes that amount and no instruction "
                "derives it. Because Mississippi apportionment and Mississippi basis both differ from federal, it "
                "is NOT the federal amount times ownership percentage. Enter Box 13 manually and attach the federal "
                "Form 4562.",
     "notes": "W10 / U13. Never hardcode the §179 figures — they are the federal ones for the tax year."},
    {"diagnostic_id": "D_MS84105_RE_ELECTION", "severity": "info",
     "title": "The R&E election's landing line is routed two different ways by DOR (U14)",
     "condition": "ms_rd_expense_election",
     "message": "The Form 84-122 line 8 instruction says the specified research or experimental expensing election "
                "amount goes on line 8; the line 16 instruction says it goes on line 16. The net effect (add back "
                "on 8, deduct on 15/16) is coherent but the routing is not. Both the R&D Expense Election and the "
                "Bonus Depreciation Election are elective and IRREVOCABLE unless the commissioner allows a change, "
                "and the combined depreciation methods cannot exceed 100% of the cost of the property.",
     "notes": "U14. §27-7-17(1)(f)(ii)1, 4 and 6."},
    {"diagnostic_id": "D_MS84105_L30_BASE", "severity": "warning",
     "title": "84-122 line 30 has no printed formula and the deduction BASE is contested (U7)",
     "condition": "filing_mode == 'composite'",
     "message": "The composite return filing adjustment on Form 84-122 line 30 is '(attach schedule)' — the form "
                "face gives no formula and no cap. The booklet supplies '$5,000.00 or 10% of the composite NET "
                "INCOME, whichever is less'; the official regulation words it as '10% of ADJUSTED GROSS INCOME' up "
                "to $5,000 per composite return. Different bases. Compute the schedule manually and note which base "
                "you used. Bound up with the composite-rate conflict.",
     "notes": "U7, bound to U1/W1."},
    # ═══ RED-DEFERS R1-R17 — each its own 'prepare manually' diagnostic, no silent gap ═══
    {"diagnostic_id": "D_MS84105_R1_DIRECT_ACCT", "severity": "error",
     "title": "R1 — Multistate direct accounting / Form 84-124 is not prepared (MANDATORY for two groups)",
     "condition": "apportionment_mode == 'multistate_direct_accounting' OR 84-122 line 14 or line 25 is non-zero",
     "message": "Mississippi REQUIRES direct (separate) accounting for producers of mineral or natural resource "
                "products and for construction contractors — it is not optional for those groups. Form 84-124 is "
                "not prepared by this product. Compute it manually and enter page 2 line 31 and/or page 3 line 46 "
                "on Form 84-122, line 25. Note that Form 84-122 line 1 is entered as zero in this mode.",
     "notes": "RED-defer R1."},
    {"diagnostic_id": "D_MS84105_R2_SPECIAL_FORMULA", "severity": "error",
     "title": "R2 — Form 84-125 line 7 special apportionment formula is not computed",
     "condition": "apportionment_category == 'special_formula_line7' OR matching NAICS",
     "message": "Airlines, motor carriers, express companies, and telephone and telegraph companies require a "
                "special apportionment formula, attached as a schedule, with the resulting ratio entered on Form "
                "84-122 line 21. This product does not compute it — prepare the schedule manually.",
     "notes": "RED-defer R2."},
    {"diagnostic_id": "D_MS84105_R3_PIPELINE", "severity": "error",
     "title": "R3 — Pipeline apportionment: the form and the regulation prescribe DIFFERENT formulas (U5)",
     "condition": "pipeline NAICS or user selection",
     "message": "Form 84-125 line 6 places pipelines on (property + payroll + SALES) / 3. The official 35 Miss. "
                "Admin. Code Pt. III §402.07 places them on (property + payroll + TRAFFIC MILES) / 3, with traffic "
                "miles defined as the movement of one barrel of oil, one gallon of gasoline, or one thousand cubic "
                "feet of gas for one mile, and a capacity-mileage fallback. These are not the same formula and DOR "
                "has not reconciled them. Prepare the apportionment manually pending a DOR ruling.",
     "notes": "RED-defer R3 / U5. Do NOT silently code the form's version as 'the pipeline rule'."},
    {"diagnostic_id": "D_MS84105_R4_FIN_INST", "severity": "error",
     "title": "R4 — No financial-institution apportionment formula exists in the regulation (U4)",
     "condition": "financial-institution NAICS or user selection",
     "message": "Form 84-125 line 6 groups financial institutions with pipelines and wholesale manufacturers on the "
                "equal-weighted three-factor formula, but the official 35 Miss. Admin. Code Title 35 Part III (123 "
                "pages) contains no financial-institution apportionment provision at all. Prepare the apportionment "
                "manually and obtain DOR confirmation.",
     "notes": "RED-defer R4 / U4."},
    {"diagnostic_id": "D_MS84105_R5_PHARMA", "severity": "error",
     "title": "R5 — The five-factor major medical / pharmaceutical formula is not computed (U6)",
     "condition": "user selects the pharmaceutical distribution variant",
     "message": "For a certain major medical or pharmaceutical supplier of a Mississippi distribution facility the "
                "apportionment percentage is payroll counted twice plus property counted twice plus sales counted "
                "once, divided by five. Form 84-125 points to the Form 84-100 booklet for this rule, but the FINAL "
                "TY2025 84-100 contains zero occurrences of 'pharmaceutical' — the rule is printed only in the "
                "83-100 corporate booklet. Prepare manually and confirm with DOR that the 83-100 text governs "
                "pass-through entities.",
     "notes": "RED-defer R5 / U6."},
    {"diagnostic_id": "D_MS84105_R6_FEE_IN_LIEU", "severity": "error",
     "title": "R6 — Fee-in-lieu franchise treatment is not computed; the line 2 computation is SUPPRESSED (U3)",
     "condition": "fee_in_lieu_checked",
     "message": "The Fee-In-Lieu checkbox is printed on the Form 84-105 line 2 face, but 'fee-in-lieu' appears zero "
                "times in the FINAL TY2025 PTE booklet and zero times in the corporate booklet. Under Miss. Code "
                "Ann. §27-13-5(3)(a) fee-in-lieu projects are exempt from the ordinary franchise levy and receive a "
                "SINGLE-SALES-FACTOR franchise apportionment instead of the property-and-receipts formula. The line "
                "2 computation is suppressed — enter the fee-in-lieu amount manually.",
     "notes": "RED-defer R6 / U3."},
    {"diagnostic_id": "D_MS84105_R7_MS_BASIS_ENGINE", "severity": "error",
     "title": "R7 — The Mississippi-basis depreciation engine is not built in v1 (W3)",
     "condition": "any asset with a federal special depreciation allowance exists, every year until recovered",
     "message": "Mississippi requires federal Form 4562 to be completed TWICE, the second copy labeled "
                "'Mississippi', computing depreciation under Mississippi statutes in effect in the year the assets "
                "were placed in service and on a basis that was never reduced by the federal special depreciation "
                "allowance. This product does not maintain the Mississippi asset ledger. Prepare the second Form "
                "4562 manually and enter the resulting amounts on Form 84-122 line 8 (add-back) and line 15 "
                "(recovery) — every year until each asset is fully recovered.",
     "notes": "RED-defer R7 / W3. v1.1 scope."},
    {"diagnostic_id": "D_MS84105_R8_AVIATION", "severity": "error",
     "title": "R8 — Aviation assets follow the FEDERAL bonus rate, and no form field exists to signal it (W4)",
     "condition": "ms_aviation_asset flag set",
     "message": "Miss. Code Ann. §27-7-17(1)(f)(i): for new or used aircraft, equipment, engines, or other parts "
                "and tools used for aviation, Mississippi bonus depreciation CONFORMS WITH THE FEDERAL RATES. Under "
                "OBBBA that is 100% for property acquired AND placed in service after January 19, 2025, and 40% "
                "otherwise — so an aviation asset acquired in 2024 and placed in service in 2025 gets 40% while a "
                "non-aviation asset placed in service the same year gets Mississippi's own 100%. No aviation line, "
                "checkbox or word appears on Form 84-122 or anywhere in the TY2025 booklet. Compute the aviation "
                "assets manually.",
     "notes": "RED-defer R8 / W4. The one place OBBBA §168(k) reaches Mississippi cost recovery."},
    {"diagnostic_id": "D_MS84105_R9_NR_AGREEMENT", "severity": "error",
     "title": "R9 — S corporation: missing Form 84-380 nonresident agreement triggers a flat 5% charge (U15)",
     "condition": "entity_type == '1120S' AND nonresident shareholders exist without a Form 84-380 on file",
     "message": "Mississippi requires a signed Form 84-380 from every nonresident shareholder, agreeing to file and "
                "pay Mississippi tax and to submit to Mississippi jurisdiction. The form is retained by the S "
                "corporation as part of its permanent tax files and is NOT sent with the return. Absent it — or on "
                "a shareholder's failure to file and pay — the corporation owes a FLAT 5% (the highest marginal "
                "rate under §27-7-5) of that shareholder's pro-rata Mississippi income, reported through line 5. "
                "Note that line 6 would otherwise apply the 0/4/5 schedule, which differs from a flat 5% on a share "
                "under $10,000, and DOR does not say which governs. Compute manually.",
     "notes": "RED-defer R9 / U15."},
    {"diagnostic_id": "D_MS84105_R10_84387", "severity": "error",
     "title": "R10 — Partnership 5% backstop withholding on Form 84-387 is not prepared",
     "condition": "entity_type == '1065' AND nonresident partners exist AND no Form 84-387 remittance",
     "message": "If individual partners fail to report and pay, the partnership and its general partners are "
                "JOINTLY AND SEVERALLY liable — unless the partnership withholds 5% of its net gain or profit and "
                "remits it on Form 84-387. Withhold from MISSISSIPPI SOURCE INCOME ONLY. Partners claim the amount "
                "as ESTIMATED TAX on their individual returns and it is refundable if their liability is lower; the "
                "partnership must furnish Form 84-387 to each partner and check Form 84-132 Box G with the amount "
                "remitted. This product does not prepare Form 84-387.",
     "notes": "RED-defer R10. Do NOT confuse with the separate 5% a nonresident SELLER remits on Mississippi real "
              "property with gross proceeds over $100,000."},
    {"diagnostic_id": "D_MS84105_R11A_83305", "severity": "error",
     "title": "R11a — Form 83-305 underestimate (90% safe harbour) is not computed",
     "condition": "line 8 exceeds $200 and estimates are short, and the filer is NOT a composite partnership",
     "message": "S corporations in either mode, and electing-PTE partnerships, compute underestimate interest and "
                "penalty on Form 83-305: 90% of the current-year income tax due, or the prior-year liability, "
                "whichever is less (subject to the $1,000,000 large-entity bar); instalments on the 15th day of the "
                "4th, 6th, 9th and 12th months; a 10% penalty PLUS interest of 5/10 of 1% per month. Enter Form "
                "83-305 line 19 on Form 84-105 line 15 manually.",
     "notes": "RED-defer R11a. §17.5 recommendation: R11 must BRANCH — see R11b."},
    {"diagnostic_id": "D_MS84105_R11B_80320", "severity": "error",
     "title": "R11b — COMPOSITE PARTNERSHIP underestimate uses Form 80-320: 80%, calendar quarters, NO 10% penalty",
     "condition": "entity_type == '1065' AND filing_mode == 'composite' AND estimates are short",
     "message": "A composite PARTNERSHIP is the only filer that reaches Form 80-320, and it computes differently in "
                "three ways: the current-year safe harbour is 80% (not 90%); the instalment dates are CALENDAR-keyed "
                "(April 15, June 15, September 15, January 15); and there is NO 10% penalty component — interest "
                "only, at 1/2% per month. Enter Form 80-320 line 11 on Form 84-105 line 15 manually. Do not reuse "
                "the Form 83-305 computation.",
     "notes": "RED-defer R11b. ⚠ [CORRECTED — verification pass] The research pass had a flat 90% for both modules."},
    {"diagnostic_id": "D_MS84105_R12_BOTH_MODES", "severity": "error",
     "title": "R12 — Composite AND Electing PTE both checked: no DOR rule exists for line 5 (U2/W6)",
     "condition": "both_composite_and_epte_checked",
     "message": "Both boxes sit under CHECK ALL THAT APPLY, so the form permits both, and Form 84-122 carries two "
                "separate terminal blocks (lines 29-32 composite and lines 33-35 electing PTE). But Form 84-105 "
                "line 5 reads 'from Form 84-122, line 32 (composite) OR line 35 (electing pass-through entity)' "
                "with no rule for what goes on line 5 if both are checked, and no DOR guidance exists. This product "
                "treats the two modes as MUTUALLY EXCLUSIVE — select one, or prepare the return manually.",
     "notes": "RED-defer R12 / U2 / W6."},
    {"diagnostic_id": "D_MS84105_R13_CREDITS", "severity": "error",
     "title": "R13 — Form 84-401 credit amounts are direct-entry; no per-credit computation or cap is enforced",
     "condition": "any Form 84-401 credit row is entered",
     "message": "Form 84-401 carries 60 credit codes. This product computes the grid arithmetic ((B + C + D - E - F) "
                "= G) and carries Part I to Form 84-105 line 3 and Part II to line 7, but it does NOT compute any "
                "individual credit and does NOT enforce any cap — including the 50%-of-liability Jobs Tax Credit "
                "cap, Form 83-450, and the MDA-certification credits. Verify each credit and its limitation "
                "manually. Note that incentive credits are NOT tax payments, and a credit claimed at entity level "
                "cannot also flow through to owners — it can be taken on one return only.",
     "notes": "RED-defer R13, sharpened by the DOR EPTE FAQ."},
    {"diagnostic_id": "D_MS84105_R14_EXEMPTION", "severity": "error",
     "title": "R14 — 84-122 line 27 income exemption requires an MDA certification and is not computed",
     "condition": "income_exemption_mda is non-zero",
     "message": "Form 84-122 line 27 requires a schedule showing the calculation, a copy of the certification from "
                "the Mississippi Development Authority, and the completed application. This product does not "
                "compute the exemption — prepare it manually and attach the certification. Note that line 27 is "
                "SUBTRACTED at line 28 (the form face governs; the instruction's 'sum lines 22 through 27' is "
                "wrong).",
     "notes": "RED-defer R14, tied to erratum E4."},
    {"diagnostic_id": "D_MS84105_R15_CORP_ELECTION", "severity": "error",
     "title": "R15 — Federal corporate election: file Mississippi Form 83-105, NOT Form 84-105",
     "condition": "elected_federal_corporate_treatment (page 2 Part I line 4 = Yes)",
     "message": "A partnership or LLC that has made a federal election to be treated as a corporation files as a "
                "corporation for Mississippi income AND franchise tax purposes. It is not a Form 84-105 filer at "
                "all — prepare Mississippi Form 83-105, Corporate Income and Franchise Tax Return. This is a WRONG-"
                "FORM stop, not a franchise-tax switch.",
     "notes": "RED-defer R15. 84-100 p.4; §27-13-5(1)(a) reaches such an entity for franchise tax."},
    {"diagnostic_id": "D_MS84105_R16_COMBINED", "severity": "error",
     "title": "R16 — Combined / consolidated reporting is out of scope (and never allowed for franchise tax)",
     "condition": "combined or consolidated reporting is elected",
     "message": "Mississippi authorizes combined reporting for INCOME TAX ONLY — 'Mississippi law does NOT authorize "
                "combined reporting for franchise tax; therefore, separate returns are required of all "
                "corporations.' The reporting corporation files Form 83-310, in the corporate series. This product "
                "does not prepare combined returns.",
     "notes": "RED-defer R16."},
    {"diagnostic_id": "D_MS84105_R17_84381_MISSING", "severity": "error",
     "title": "R17 — Electing PTE box checked but no Form 84-381 election is on file",
     "condition": "filing_mode == 'electing_pte' AND NOT ptet_election_84381_on_file",
     "message": "The pass-through entity election MUST be made by filing Form 84-381 — it cannot be made by "
                "checking the box on this return, and once this return is filed it CANNOT be amended to make the "
                "election. A copy of Form 84-381 must be attached to the return, together with a Mississippi "
                "Schedule K-1 (Form 84-132) for each owner. File Form 84-381 (paper or through TAP) before filing "
                "this return.",
     "notes": "RED-defer R17 / W9. Form 84-381 CAN be filed through TAP even though the return cannot."},
]

MS84105_SCENARIOS: list[dict] = [
    {"scenario_name": "⚠ THE FORK — S corporation, electing PTE, franchise plus income tax", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"entity_type": "1120S", "filing_mode": "electing_pte", "tax_year_beginning": "2025-01-01",
                "taxable_capital_84110_l18": 2_100_000, "franchise_tax_credit_84401": 0,
                "ms_net_taxable_income_l5": 500_000, "income_tax_credits_84401": 0},
     "expected_outputs": {"2": 1500, "4": 1500, "6": 24700, "8": 24700, "9": 26200},
     "notes": "L2 = MAX(25, 0.75 x CEIL((2,100,000 - 100,000)/1,000)) = 0.75 x 2,000 = 1,500. L4 = 1,500. "
              "L6 = 0% x 5,000 + 4% x 5,000 + 5% x 490,000 = 0 + 200 + 24,500 = 24,700. L8 = 24,700. "
              "⚠ L9 = L4 + L8 = 1,500 + 24,700 = 26,200 (S CORPORATION)."},
    {"scenario_name": "⚠ THE FORK — identical partnership: franchise block NOT APPLICABLE, L9 = L8", "scenario_type": "normal", "sort_order": 2,
     "inputs": {"entity_type": "1065", "filing_mode": "electing_pte", "tax_year_beginning": "2025-01-01",
                "ms_net_taxable_income_l5": 500_000, "income_tax_credits_84401": 0},
     "expected_outputs": {"1": None, "2": None, "3": None, "4": None, "6": 24700, "8": 24700, "9": 24700},
     "notes": "Same income, same year, DIFFERENT return. Lines 1-4 are hard-gated off — there is no $25 minimum for "
              "a partnership. ⚠ L9 = L8 = 24,700, NOT 26,200. A partnership that lands a franchise tax on L2 files "
              "a wrong return, and the $25 minimum makes that failure silent and non-zero."},
    {"scenario_name": "Franchise minimum — inactive S corporation with $60,000 of capital", "scenario_type": "edge", "sort_order": 3,
     "inputs": {"entity_type": "1120S", "filing_mode": "informational", "is_inactive_s_corp": True,
                "taxable_capital_84110_l18": 60_000, "tax_year_beginning": "2025-01-01"},
     "expected_outputs": {"2": 25, "4": 25, "9": 25},
     "notes": "Capital is BELOW the $100,000 exemption, so the rate produces zero and the $25 statutory MINIMUM "
              "applies (§27-13-5(1)(b)). An inactive S corp still files. This is the exact figure a partnership "
              "would wrongly owe if the L1-L4 gate failed."},
    {"scenario_name": "Franchise fraction-of-$1,000 rounding at $100,500 of capital", "scenario_type": "edge", "sort_order": 4,
     "inputs": {"entity_type": "1120S", "taxable_capital_84110_l18": 100_500, "tax_year_beginning": "2025-01-01"},
     "expected_outputs": {"2": 25},
     "notes": "Excess = 500; 'or fraction thereof' -> CEIL(500/1,000) = 1 unit; 0.75 x 1 = $0.75, which the $25 "
              "minimum overrides. W8(a): the interaction of the 84-110 L18 round-up with the statutory 'or fraction "
              "thereof' is untested and Ken should bless it."},
    {"scenario_name": "⚠ DEPRECIATION — add-back on 84-122 L8, MS recovery on L15, and NOT on L6/L13", "scenario_type": "edge", "sort_order": 5,
     "inputs": {"entity_type": "1065", "federal_4562_shows_special_allowance": True,
                "add_federal_special_depreciation": 400_000, "ded_additional_ms_depreciation": 57_143,
                "add_other_state_muni_interest": 0, "ded_flowthrough_income_removed": 0},
     "expected_outputs": {"122-L8": 400000, "122-L15": 57143, "122-L6": 0, "122-L13": 0},
     "notes": "⚠ THE ASSERTION THIS SPEC EXISTS FOR. The $400,000 federal special depreciation allowance is added "
              "back on LINE 8 and the extra Mississippi depreciation from the unreduced basis is deducted on LINE "
              "15. Line 6 (municipal-bond interest) and line 13 (flow-through income) MUST stay zero — those are "
              "the Form 83-122 CORPORATE line numbers. The L15 amount recurs every year until the asset is fully "
              "recovered; it is not a same-year wash."},
    {"scenario_name": "⚠ AVIATION — two assets, same year, same taxpayer, different bonus regimes", "scenario_type": "edge", "sort_order": 6,
     "inputs": {"asset_a": {"ms_aviation_asset": False, "placed_in_service": "2025-06-01"},
                "asset_b": {"ms_aviation_asset": True, "acquired": "2024-11-01", "placed_in_service": "2025-06-01"}},
     "expected_outputs": {"asset_a_bonus_rate": "1.00", "asset_b_bonus_rate": "0.40"},
     "notes": "Asset A takes Mississippi's OWN permanent 100% bonus (§27-7-17(1)(f)(ii)2, property placed in "
              "service after 12/31/2022). Asset B is an aviation asset, so it CONFORMS TO THE FEDERAL RATE "
              "(§27-7-17(1)(f)(i)) — acquired before 1/20/2025, so 40% under OBBBA. No form field signals this; "
              "the app-level ms_aviation_asset flag drives it (W4/R8)."},
    {"scenario_name": "⚠ SAFE HARBOUR — composite partnership 80% vs everyone else 90%", "scenario_type": "edge", "sort_order": 7,
     "inputs": {"case_a": {"entity_type": "1065", "filing_mode": "composite", "current_year_tax": 100_000},
                "case_b": {"entity_type": "1065", "filing_mode": "electing_pte", "current_year_tax": 100_000},
                "case_c": {"entity_type": "1120S", "filing_mode": "composite", "current_year_tax": 100_000}},
     "expected_outputs": {"case_a": {"form": "80-320", "pct": "0.80", "test": 80000, "has_10pct_penalty": False},
                          "case_b": {"form": "83-305", "pct": "0.90", "test": 90000, "has_10pct_penalty": True},
                          "case_c": {"form": "83-305", "pct": "0.90", "test": 90000, "has_10pct_penalty": True}},
     "notes": "⚠ [CORRECTED — verification pass] The fork is MODE x ENTITY, not entity alone. ONLY a composite "
              "PARTNERSHIP reaches Form 80-320, and it computes on 80%, on CALENDAR quarters, with NO 10% penalty. "
              "An electing-PTE partnership is on Form 83-305 at 90% like every S corp. Three silent per-return "
              "differences. Do not code one underestimate routine."},
    {"scenario_name": "⚠ COMPOSITE RATE — no rate is computed, a diagnostic is raised", "scenario_type": "failure", "sort_order": 8,
     "inputs": {"entity_type": "1065", "filing_mode": "composite", "ms_net_taxable_income_l5": 300_000},
     "expected_outputs": {"6": None, "diagnostic": "D_MS84105_COMPOSITE_RATE", "positions_recorded": 3},
     "notes": "⚠ W1/U1. Three positions, none dispositive: DOR's 0/4/5 (stated twice, TY2025-keyed); the statutory "
              "0/4.4% (composite members are individuals and §27-7-5(1)(b) reduces the rate for individuals only); "
              "and the official regulation's two packaged routes, which pair the individual rate with the "
              "$5,000/10% deduction and the corporate rate with no deduction — while the TY2025 forms take one half "
              "of each. THE SPEC DOES NOT CHOOSE. Line 6 is direct-entry until Ken rules."},
    {"scenario_name": "⚠ L20 ASYMMETRY — late-payment items are not netted against the refund", "scenario_type": "edge", "sort_order": 9,
     "inputs": {"9": 20_000, "13": 30_000, "15": 1_200, "16": 400, "17": 300, "18": 500},
     "expected_outputs": {"20": 8800},
     "notes": "L20 = L13 - L9 - L15 = 30,000 - 20,000 - 1,200 = 8,800. The underestimate interest and penalty IS "
              "netted; the late-payment interest (400), late-payment penalty (300) and late-filing penalty (500) "
              "are NOT. Computing L20 as L13 - L19 would give 7,600 and be wrong."},
    {"scenario_name": "Owner-side PTET credit — allowed portion and refundable excess", "scenario_type": "normal", "sort_order": 10,
     "inputs": {"owner_ptet_tax_paid_l3d": 18_000, "owner_total_ms_tax_l4": 12_500,
                "owner_type_for_credit_landing": "individual_resident"},
     "expected_outputs": {"161-L5": 12500, "161-L6": 5500, "lands_on": "Form 80-105, page 1, line 26 (PAYMENTS block)"},
     "notes": "L5 = MIN(18,000, 12,500) = 12,500. L6 excess = 5,500, carried forward as an overpayment OR REFUNDED "
              "AT THE OWNER'S ELECTION (§27-7-26(1)(c), now statutory). The owner REPORTS the income and takes the "
              "credit in the PAYMENTS block — Mississippi reports and credits, never excludes."},
    {"scenario_name": "Fiduciary receives the PTET credit even though it cannot elect", "scenario_type": "edge", "sort_order": 11,
     "inputs": {"owner_type_for_credit_landing": "fiduciary", "owner_ptet_tax_paid_l3d": 4_000, "owner_total_ms_tax_l4": 9_000},
     "expected_outputs": {"161-L5": 4000, "161-L6": 0, "lands_on": "Form 81-110, page 1, line 8  (cannot elect; CAN receive)"},
     "notes": "⚠ Fiduciaries are NOT eligible to make the pass-through entity election (84-100 p.22; DOR EPTE FAQ) "
              "— yet Form 80-161 line 3D routes the credit to Form 81-110 page 1 line 8. Cannot elect, can receive; "
              "confirmed on both legs."},
    {"scenario_name": "100% Mississippi short path through Form 84-122", "scenario_type": "normal", "sort_order": 12,
     "inputs": {"apportionment_mode": "100_percent_mississippi", "122-L18": 750_000, "122-L27": 0,
                "ms_flowthrough_income_reinserted": 0, "nonbusiness_income_ms": 0, "other_adjustments_required_by_law": 0},
     "expected_outputs": {"122-L22": 750000, "122-L28": 750000},
     "notes": "Face note above L18: 'If 100% Mississippi, complete line 18 then skip to page 2, line 22.' L22 = L18 "
              "directly — lines 19-21 and Form 84-125 are not used. L28 = (22 + 23 + 24 + 25 + 26) - 27 per the "
              "FACE (E4)."},
    {"scenario_name": "⚠ THROWBACK — a P.L. 86-272-protected shipment returns to the MS numerator", "scenario_type": "edge", "sort_order": 13,
     "inputs": {"sales_destination_into_ms": 2_000_000, "sales_thrown_back_to_ms": 3_000_000,
                "sales_dropship_thrown_back": 250_000, "sales_us_government_from_ms": 750_000,
                "sales_everywhere": 20_000_000},
     "expected_outputs": {"ms_sales_numerator": 6000000, "125-L3": "0.3000"},
     "notes": "Numerator = 2,000,000 destination + 3,000,000 thrown back (shipped from a MS location into states "
              "where the entity is not taxable, INCLUDING P.L. 86-272-protected states per §202.06) + 250,000 "
              "drop-shipment throwback + 750,000 U.S. Government sales shipped from a MS location (origin-sourced "
              "unconditionally) = 6,000,000 / 20,000,000 = 0.3000. Without throwback the ratio would be 0.1000 — "
              "the single largest sourcing consequence in the state."},
    {"scenario_name": "Composite base is SMALLER than the electing-PTE base", "scenario_type": "edge", "sort_order": 14,
     "inputs": {"122-L28": 1_000_000, "composite_net_income_84131_l4a": 350_000,
                "composite_filing_adjustment_l30": 5_000, "ms_nol_deduction_84155_l2": 0},
     "expected_outputs": {"122-L32": 345000, "122-L35": 1000000},
     "notes": "Electing PTE: L33 = L28 IN FULL = 1,000,000 -> L35 = 1,000,000 (every owner, resident and "
              "nonresident). Composite: L29 = 350,000 off Form 84-131 line 4a — ONLY the owners whose COMPOSITE box "
              "is checked — less the L30 adjustment = 345,000. The two modes are not two rates on one base; they "
              "are two different bases."},
    {"scenario_name": "Form 84-115 (MS8453-PTE) Part I tie-outs", "scenario_type": "normal", "sort_order": 15,
     "inputs": {"5": 500_000, "6": 24_700, "7": 1_000, "13": 20_000, "19": 5_700, "20": 0, "22": 0},
     "expected_outputs": {"115-L1": 500000, "115-L2": 24700, "115-L3": 21000, "115-L4": 5700, "115-L6": 0},
     "notes": "115-L3 = 84-105 L7 + L13 = 1,000 + 20,000 = 21,000. ⚠ [ADDED — verification pass] The form the "
              "research pass missed entirely; it carries its own column on the DOR approved-provider matrix, so it "
              "is separately approval-gated. Print and retain — never mailed."},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORMS registry + flow assertions
# ═══════════════════════════════════════════════════════════════════════════

FORMS: list[dict] = [
    {
        "identity": {
            "form_number": "MS_84_105",
            "form_title": "MS Form 84-105 — Mississippi Pass-Through Entity Tax Return (TY2025)",
            "notes": "ONE form serving BOTH the 1065 and 1120S modules. ⚠ Lines 1-4 are an S-CORPORATION-ONLY "
                     "franchise block, hard-gated on the entity-type radio — L9 = L4 + L8 for an S corp and = L8 "
                     "for a partnership, and the $25 franchise minimum makes a mis-gated partnership return "
                     "silently non-zero. ⚠ Depreciation lives on Form 84-122 LINE 8 (federal special allowance "
                     "add-back) and LINE 15 (unreduced-Mississippi-basis recovery) — NOT lines 6/13, which are "
                     "municipal-bond interest and flow-through income and are the Form 83-122 CORPORATE numbers. "
                     "⚠ The composite rate is a genuine three-way conflict between DOR, the statute and the "
                     "official Administrative Code; this spec raises a diagnostic and computes NO composite rate. "
                     "Companions in v1 scope: 84-110, 84-122, 84-125, 84-131, 84-132, 84-150, 84-155, 84-161, "
                     "84-401, 84-115 (MS8453-PTE) and 84-381 field capture. NEVER CLONE GA — Mississippi has no "
                     "general conformity statute, runs its own permanent 100% bonus with an aviation exception, "
                     "and has a live franchise tax that dies on 1/1/2028.",
        },
        "facts": MS84105_FACTS, "rules": MS84105_RULES, "rule_links": MS84105_RULE_LINKS,
        "lines": MS84105_LINES, "diagnostics": MS84105_DIAGNOSTICS, "scenarios": MS84105_SCENARIOS,
    },
]

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-MS-L9-FORK", "title": "⚠ 84-105 L9 = L4 + L8 for an S corp, = L8 for a partnership",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 1,
     "description": "The module fork. 84-100 p.17: 'S corporations, enter the amount from line 4; composite and "
                    "electing pass-through entity S corporations, enter the amounts from line 4 plus line 8; and "
                    "composite and electing pass-through entity partnerships, enter the amount from line 8.'",
     "definition": {"rule": "R-MS-FORK-L9",
                    "check": "L9 == (L4 + L8) if entity_type == '1120S' else L8"}},
    {"assertion_id": "FA-MS-FRAN-GATE", "title": "⚠ A partnership return carries NOTHING on 84-105 lines 1-4",
     "assertion_type": "flow_assertion", "entity_types": ["1065"], "status": "draft", "sort_order": 2,
     "description": "Lines 1-4 are the S CORPORATION FRANCHISE TAX block. The $25 minimum makes a mis-gated "
                    "partnership return silently non-zero, so the gate is hard, not a preparer convention.",
     "definition": {"rule": "R-MS-ENTITY-GATE",
                    "check": "entity_type == '1065' implies L1 == L2 == L3 == L4 == None"}},
    {"assertion_id": "FA-MS-DEPR-L8L15", "title": "⚠ Depreciation lands on 84-122 L8 (add-back) and L15 (recovery)",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 3,
     "description": "The federal special depreciation allowance is added back on 84-122 line 8; the additional "
                    "Mississippi depreciation from the unreduced state basis is deducted on line 15. DOR's own line "
                    "8 instruction states the pairing.",
     "definition": {"rule": "R-MS-DEPR",
                    "check": "depreciation_lines.keys() == {'122-L8', '122-L15'}"}},
    {"assertion_id": "FA-MS-DEPR-NOT-L613", "title": "⚠ Depreciation NEVER lands on 84-122 L6 or L13",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 4,
     "bug_reference": "Campaign framing asserted 84-122 L6/L13 — those are the Form 83-122 CORPORATE lines; coding "
                      "them would book bonus depreciation as municipal-bond interest on every MS PTE return",
     "description": "84-122 line 6 is 'Interest on obligations of other states or political subdivisions' and line "
                    "13 is 'Income (loss) from partnership, S corporation or trust'. Neither is a depreciation "
                    "line. Line 13 in particular would corrupt the line 24 re-insertion of already-sourced "
                    "flow-through income.",
     "definition": {"rule": "R-MS-DEPR",
                    "check": "'122-L6' not in depreciation_lines and '122-L13' not in depreciation_lines"}},
    {"assertion_id": "FA-MS-FRAN-MIN", "title": "Franchise tax is never below the $25 statutory minimum",
     "assertion_type": "table_invariant", "entity_types": ["1120S"], "status": "draft", "sort_order": 5,
     "description": "§27-13-5(1)(b): 'In no case shall the franchise tax due for the accounting period be less than "
                    "Twenty-five Dollars ($25.00).' Rate is TY-keyed ($0.75 per $1,000 over $100,000 for TY2025) "
                    "and the levy is REPEALED effective January 1, 2028.",
     "definition": {"rule": "R-MS-FRANCHISE",
                    "check": "tax_year < 2028 implies L2 >= 25; tax_year >= 2028 implies L2 == 0"}},
    {"assertion_id": "FA-MS-SAFE-HARBOUR", "title": "⚠ Safe harbour is keyed on MODE x ENTITY: 80% vs 90%",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 6,
     "bug_reference": "Research pass stated a flat 90% for both modules; Form 80-320 line 2 says 80%",
     "description": "A composite PARTNERSHIP alone reaches Form 80-320: 80% current-year test, calendar-keyed "
                    "instalments, interest only with no 10% penalty. Everything else is on Form 83-305 at 90% with "
                    "a 10% penalty plus 1/2 of 1% per month.",
     "definition": {"rule": "R-MS-ESTIMATES",
                    "check": "(entity_type=='1065' and mode=='composite') implies form=='80-320' and pct=='0.80'; "
                             "else form=='83-305' and pct=='0.90'"}},
    {"assertion_id": "FA-MS-COMP-RATE", "title": "⚠ NO composite rate is computed — three positions, unresolved",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 7,
     "description": "W1/U1. The spec deliberately declines to choose between DOR's 0/4/5, the statutory 0/4.4%, and "
                    "the official regulation's two packaged routes. Composite line 6 is direct-entry behind "
                    "D_MS84105_COMPOSITE_RATE until Ken rules.",
     "definition": {"rule": "R-MS-COMP-RATE",
                    "check": "composite_tax is None and len(MS_COMPOSITE_RATE_POSITIONS) == 3 and "
                             "MS_COMPOSITE_RATE_RESOLVED is False"}},
    {"assertion_id": "FA-MS-L20-ASYM", "title": "84-105 L20 nets only L9 and L15, never L16-L18",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 8,
     "description": "Face: 'if line 13 is larger than line 9 plus line 15, subtract line 9 and line 15 from line "
                    "13'. The late-payment items are excluded from the netting. Encode as written, not as L13-L19.",
     "definition": {"rule": "R-MS-PAYMENTS", "check": "L20 == max(0, L13 - L9 - L15)"}},
    {"assertion_id": "FA-MS-PTET-CREDIT", "title": "PTET credit is a PAYMENT at every level; excess is refundable",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 9,
     "description": "84-131 Column D = 84-105 L8 x ownership%; 84-132 Part V delivers it; the owner's 84-161/80-161 "
                    "L5 = MIN(L3D, L4) and L6 = the excess, refunded or carried forward AT THE OWNER'S ELECTION. "
                    "Landing lines: 80-105 L26, 80-205 L28, 81-110 L8 (fiduciary — cannot elect, CAN receive), "
                    "84-105 L12, 83-105 L12 — all inside PAYMENTS blocks, never credits blocks.",
     "definition": {"rule": "R-MS-PTET-CREDIT",
                    "check": "L5 == min(L3D, L4) and L6 == L3D - L5 and landing_block == 'payments'"}},
    {"assertion_id": "FA-MS-THROWBACK", "title": "⚠ MS sales numerator includes throwback and U.S. Government origin",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 10,
     "description": "Numerator = destination sales into MS + sales shipped from a MS location where the taxpayer is "
                    "not taxable in the purchaser's state (P.L. 86-272 protection counts) + drop-shipment "
                    "throwbacks + ALL U.S. Government sales shipped from a MS location.",
     "definition": {"rule": "R-MS-THROWBACK",
                    "check": "numerator == destination + throwback + dropship_throwback + us_govt_from_ms"}},
    {"assertion_id": "FA-MS-84115-TIE", "title": "Form 84-115 Part I ties out to 84-105 L5/L6/L7+L13/L19/L20/L22",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 11,
     "description": "The MS8453-PTE e-file declaration's seven Part I lines are computed tie-outs against this "
                    "return. Separately approval-gated on the DOR provider matrix.",
     "definition": {"rule": "R-MS-84115",
                    "check": "115_L1==L5 and 115_L2==L6 and 115_L3==L7+L13 and 115_L4==L19 and 115_L5==L20 and 115_L6==L22"}},
]


# ═══════════════════════════════════════════════════════════════════════════
# Command
# ═══════════════════════════════════════════════════════════════════════════

class Command(BaseCommand):
    help = (
        "Load the MS Form 84-105 spec (Mississippi Pass-Through Entity Tax Return, TY2025). "
        "ONE form, TWO modules (1065 + 1120S), with an S-corporation-only franchise block. "
        "Refuses to seed until Ken sets READY_TO_SEED=True after the in-session review walk (W1-W11)."
    )

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad MS Form 84-105 spec (Mississippi Pass-Through Entity Tax Return)\n"))
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
        # The composite rate must NOT be silently resolved inside the loader.
        if MS_COMPOSITE_RATE_RESOLVED:
            empty.append("MS_COMPOSITE_RATE_RESOLVED was flipped without a Ken ruling (W1/U1)")
        if not READY_TO_SEED or empty:
            still_empty = "\n  ".join(f"- {n}" for n in empty) or "(all populated)"
            raise CommandError(
                "\nREFUSING TO SEED MS 84-105: not cleared to seed.\n\n"
                "Content is authored, but seeding is gated until Ken reviews the packet and\n"
                "flips the sentinel. The walk items:\n"
                "  W1  the COMPOSITE RATE — three-sided and unresolved; this spec computes NO\n"
                "      composite rate and must not be made to pick a side without a ruling\n"
                "  W2  the FRANCHISE FORK — lines 1-4 hard-gated to 1120S ($25 min makes a\n"
                "      mis-gated partnership return silently non-zero)\n"
                "  W3  DEPRECIATION scope — direct-entry 84-122 L8/L15 vs an MS-basis engine\n"
                "  W4  the AVIATION branch (no form field exists; app-level flag proposed)\n"
                "  W5  THROWBACK + which apportionment formulas ship in v1\n"
                "  W6  composite + electing PTE on one return (U2)\n"
                "  W7  bless the five DOR errata E1-E5 (build to the form face)\n"
                "  W8  the two arithmetic assumptions read off the form (franchise CEIL; 84-110\n"
                "      L6/L7 sign convention)\n"
                "  W9  the PTET election BINDS EVERY LATER YEAR and cannot be made by amending\n"
                "  W10 the Mississippi §179 amount on 84-132 Box 13 (U13)\n"
                "  W11 are Forms 84-131 / 84-132 in v1?\n"
                "Plus 13 live [UNVERIFIED] items (U1-U9, U13-U16, U17 partial) — see the module\n"
                "docstring and delvio-states/research/ms_pte_source_brief.md §13.\n\n"
                f"READY_TO_SEED = {READY_TO_SEED} (must be True to proceed)\n\n"
                f"Currently empty / placeholder:\n  {still_empty}\n\n"
                "To proceed: review the module-level data lists (and ms_pte_source_brief.md),\n"
                "then set READY_TO_SEED = True. Idempotent via update_or_create."
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
                self.stdout.write(self.style.WARNING(f"  existing source {code} NOT FOUND — links to it will be skipped"))
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
        self.stdout.write("MS Form 84-105 loaded.")
        self.stdout.write(
            f"  MS_84_105: facts {len(MS84105_FACTS)} / rules {len(MS84105_RULES)} / lines {len(MS84105_LINES)} / "
            f"diag {len(MS84105_DIAGNOSTICS)} / tests {len(MS84105_SCENARIOS)} / FA {len(FLOW_ASSERTIONS)}"
        )
        self.stdout.write("  entity_types: 1065 + 1120S (ONE form, TWO modules); franchise block gated to 1120S")
        self.stdout.write("  !! depreciation: add-back 84-122 L8 / recovery 84-122 L15 (NOT L6 / L13)")
        self.stdout.write("  !! composite rate: UNRESOLVED - no rate computed (W1/U1)")
        self.stdout.write("=" * 60)
