"""Load the CO DR 0106 spec — Colorado Partnership and S Corporation Income Tax Return (TY2025).

═══════════════════════════════════════════════════════════════════════════
WHAT THIS IS
═══════════════════════════════════════════════════════════════════════════
Colorado does NOT have a partnership return and an S-corporation return. It has
ONE return — DR 0106 — whose face is identical for both and whose SOURCING RULES
FORK. That is why one RS spec (`CO_DR0106`) serves TWO delvio-tax modules
(1065 and 1120S), and why the fork is modelled as real branches rather than a
shared code path with a comment.

Spec source: `delvio-states/research/co_pte_source_brief.md` — VERIFIED
(adversarial pass 2026-08-16, 9 corrections C1-C9). Its §17 Verification section
SUPERSEDES the body wherever they differ, and this loader follows §17.
Conformity: `delvio-states/conformity/co_conformity.md` (VERIFIED 2026-08-06).

Colorado is rolling-conformity, flat-rate, federal-taxable-income. There is NO
depreciation modification of any kind — that absence is encoded deliberately
(see R-CO-DEPR-NEGATIVE); it is a `rule says no`, not a `no rule found`.

NO prior RS spec exists (lookup/CO_DR0106/export/ -> 404, confirmed 2026-08-16).
NEW form. Form code per campaign D-9 / the `<ST>_<FORM>` namespace.

═══════════════════════════════════════════════════════════════════════════
✅ [UNV-7] RULED BY KEN 2026-08-17 — Gate-1 walk item A1 (was W13)
═══════════════════════════════════════════════════════════════════════════
QUESTION: does Colorado's rolling conformity (§ 39-22-103(5.3), C.R.S.) pick up
RETROACTIVELY-EFFECTIVE federal amendments — specifically OBBBA's retroactive
small-business § 174A R&D expensing election, which changes federal ordinary
income and therefore **DR 0106 line 1**, the first number on the return?

KEN'S RULING: **YES — it does.** § 39-22-103(5.3) takes the IRC "as the same may
become effective at any time or from time to time, for the taxable year," and
the DR 0106 has **no modification line anywhere** to express a divergence. The
form face can therefore only carry the federal figure. **DR 0106 line 1 is a
straight transcription of federal ordinary income as filed. No § 174A adjustment
is computed in either direction** — which is what the draft already built; the
ruling makes that affirmatively correct rather than a deferral.

The reasoning is recorded in rule `R-CO-174A-CONFORM` and in the informational
diagnostic `D_CO106_BLOCK_174A_CONFORMITY` (severity downgraded error -> info;
the diagnostic_id is kept stable so nothing downstream re-keys).

⚠ **[UNV-7] STAYS OPEN as a confirmation item, and is NO LONGER BLOCKING.** The
authority that would confirm the ruling — the published *Anschutz* opinion, the
current 1 CCR 201-2 text showing the repealed rule's date, or CDOR guidance on
§ 174A for TY2025 — is still unpulled. The ruling is Ken's reading of the
rolling-conformity statute, not a published CDOR position. Re-verify before the
module ships. See campaign DECISIONS D-11 A1.

═══════════════════════════════════════════════════════════════════════════
v1 SCOPE — PROPOSED (brief §15; NOT yet walked with Ken)
═══════════════════════════════════════════════════════════════════════════
COMPUTES: Part I (L1-L10) incl. THE SIGN FLIP and BOTH § 179 touchpoints; the
  three-mode state machine (A informational / B composite / C SALT Parity) with
  the mutual-exclusivity block and the mandatory-composite test over the five
  exclusions and the shared carve-out; Part II (L12-L16); Part III (L17-L20);
  Part IV (L21-L35); Part V receipts factor (L1-L15); DR 0106K lines 1-16 both
  columns per module, incl. the per-owner floor at zero; owner-status
  derivation; the due-date calendar; DR 0233 estimated tax; the DR 0106CR
  column arithmetic (L38 = SUM L5..L37) and the Mode-C Column-C-zero rule;
  Boxes B/C balance-sheet transcription; owner-side handoff records.
DIRECT-ENTRY: DR 0106K L9/L10/L11/L13 modification amounts; partnership
  direct-sourced Column B and L4 guaranteed-payment Column B (W1); Part V
  L2-L7 receipts and L10(a)-(e)/L13(a)-(e) allocation detail; DR 0106 L7
  § 280E; all DR 0106CR and DR 0106K credit amounts; L15, L23, L25, L26, L27,
  L30; Boxes D/E/G/H.
RED-DEFER: R1-R16 below — **each gets its own diagnostic; no silent gap.**

RED-DEFERS (R1-R16), each with its own "prepare manually" diagnostic:
  R1  DR 0619 advance-payment reconciliation      D_CO106_R1_DR0619
  R2  DR 1305/E/F/G gross conservation easement   D_CO106_R2_DR1305
  R3  Enterprise Zone / CHIPS (DR 1366, DR 1370)  D_CO106_R3_ENTZONE
  R4  CHFA housing credits                        D_CO106_R4_CHFA
  R5  Contaminated land (DR 0348P/T, DR 0349)     D_CO106_R5_REMEDIATION
  R6  Child care credits (DR 1317)                D_CO106_R6_CHILDCARE
  R7  § 39-22-601.5(3)(e) in-lieu-of amount (L22) D_CO106_R7_INLIEU
  R8  § 39-22-303.6(9) alternative apportionment  D_CO106_R8_ALTAPPORT
  R9  § 39-22-303.7 mutual fund service corp      D_CO106_R9_MUTUALFUND
  R10 DR 1079 real-property withholding           D_CO106_R10_DR1079
  R11 DR 0108 nonresident remittance [UNV-2]      D_CO106_R11_DR0108
  R12 Retroactive PTET elections TY2018-2021      D_CO106_R12_RETRO_ELECTION
  R13 Short-period / fiscal-year estimated sched.  D_CO106_R13_SHORTPERIOD
  R14 PTP composite exemption [UNV-5]             D_CO106_R14_PTP
  R15 Colorado K-1 XLS/XML submitter path         D_CO106_R15_K1_TRANSMITTAL
  R16 Form 8886 / DR 1831 disclosure              D_CO106_R16_REPORTABLE

═══════════════════════════════════════════════════════════════════════════
THE FOUR THINGS MOST LIKELY TO BE BUILT WRONG (all encoded as real branches)
═══════════════════════════════════════════════════════════════════════════
1. ⚠ THE FORK — 16 forks (F1-F16), not 12. The verifier RAISED the count; F13-F16
   all live inside the DR 0106K-I's two halves (pp. 1-9 partnership, pp. 10-18
   S corp). F15 and F16 are SUBSTANTIVE MODIFICATION ITEMS, not wording: an
   S-corp return built from the partnership half silently drops a foreign-tax
   ADDITION and a § 280C SUBTRACTION; a partnership return built from the S-corp
   half silently drops the § 39-22-206 export-taxpayer subtraction.
   FOURTEEN of the sixteen key off the MODULE, and the module fork must key off
   the ATTACHED FEDERAL RETURN (1065 vs 1120-S) — **NEVER off Box A**, which is
   LEGAL form (six of its eight values are silent on 1065-vs-1120S). See W2.
   Every fork is a branch in `_co_fork_*` / `CO_FORKS`, harness-proven to give
   DIFFERENT results for 1065 vs 1120S.

2. ⚠ THE SIGN FLIP — "the single most likely arithmetic bug in this form."
   The DR 0106K carries deductions and subtractions as NEGATIVE ("Enter any
   losses on lines 1, 2, 3, or 8, and any federal deductions on line 12, as
   negative amounts"; "Enter subtractions on line 13 as a negative amount"), but
   DR 0106 lines 6, 7, 8 are entered as POSITIVE and then SUBTRACTED at L9/L10.
   Aggregating K-1 Col. A L12 -> DR 0106 L6 and L13 -> L8 REQUIRES SIGN INVERSION.
   Lines 3 and 4 (from K-1 L10 and L9+L11) are ALREADY POSITIVE and must NOT be
   inverted. Both halves of that rule are pinned by the verifier (§17.1) and both
   are encoded in `_co_part1(..., apply_sign_flip=)`, with a harness oracle that
   proves the un-inverted aggregation yields a different, wrong line 10.

3. ⚠ § 179 HAS TWO TOUCHPOINTS (verifier correction C3, HIGH severity — the
   research pass said "the only § 179 mechanic on the form is the line-2
   disposition aggregation"; that was WRONG and load-bearing):
     (i)  DR 0106 LINE 2 — the § 179-DISPOSITION aggregation: gain/loss on
          property "for which a section 179 deduction has been passed through",
          from the statement attached for Sch. K line 20c (1065) / 17d (1120-S).
     (ii) DR 0106 LINE 6 — the § 179 DEDUCTION ITSELF, which reaches Colorado
          through DR 0106K line 12 (= 1065 K-1 Box 12 + Box 13 / 1120-S K-1
          Box 11 + Box 12; Box 12 / Box 11 IS the § 179 deduction) and therefore
          RIDES THE SIGN FLIP. DR 0106 line 2 lists income lines only and
          deliberately EXCLUDES Sch. K 12/13 (1065) and 11/12 (1120-S).
   Neither is a state modification. This matters precisely because Colorado's
   depreciation story is otherwise "nothing to build" — a missed § 179 path is
   the easiest thing in the spec to omit.

4. ⚠ TWO RATE STATUTES ON ONE FORM. Composite (L13) cites § 39-22-104 — the
   INDIVIDUAL rate ("the highest marginal tax rate in effect under section
   39-22-104", § 39-22-601(5.5)(d)(III)(A) and (2.7)(d)(III)(A)). PTET (L20)
   cites § 39-22-301 — the CORPORATE rate ("the tax rate set forth in section
   39-22-301", § 39-22-344(1)). BOTH read 4.4% for TY2025, so the distinction is
   invisible THIS YEAR. They are encoded as TWO named tax-year-keyed constants
   with SEPARATE authorities and are NOT collapsed. LCS projects 4.33% (TY2027)
   and 4.29% (TY2028) — the constant moves. See W7.

═══════════════════════════════════════════════════════════════════════════
requires_human_review WALK ITEMS — W1-W13 (brief §14 W1-W12 + W13), ALL CLEARED
AT GATE 1 ON 2026-08-17. Retained as the authoring record, not as open items.
═══════════════════════════════════════════════════════════════════════════
W1.  Does v1 COMPUTE partnership direct sourcing, or DIRECT-ENTER Column B?
     Direct sourcing (§ 39-22-109; Rule 39-22-109(3)(a)/(b)/(e)) is the DEFAULT
     for nonresident individual/estate/trust partners, yet ordinary income is
     generally receipts-factor sourced ANYWAY, and a partnership with a C-corp
     partner MUST complete Part V regardless. So a partnership can be running
     both methods at once. PROPOSED: COMPUTE Part V for both modules;
     DIRECT-ENTER the direct-sourced Column B amounts, with the three Rule
     39-22-109(3) tests as help text. **The largest single scope lever on the
     Colorado build.** Read GIL 22-003 before the walk (it is cited BY NAME in
     the DR 0106K-I partnership half; a GIL is non-binding — guidance, not
     authority).
W2.  What drives the 1065/1120-S fork? Box A is LEGAL FORM, not tax
     classification. Key off the ATTACHED FEDERAL RETURN. Hard diagnostic when
     Box A and the federal return are impossibly inconsistent.
W3.  The three-mode machine + mutual exclusivity. Mode A (informational, zero
     tax) is a REAL and common filing, not an edge case. ⚠ C1: the
     mandatory-composite RED must honour the "entity consisting only of already
     excluded owners" carve-out for **S CORPS TOO** (§ 39-22-601(2.7)(d)(VII)(B))
     — the research pass said "no analogue" and was WRONG. Only the PTP
     carve-out is partnership-only.
W4.  Per-owner floor-at-zero vs the aggregate exclusion — build as ONE rule, and
     encode the reconciliations as FLOW ASSERTIONS, not comments.
W5.  Guaranteed payments: IN the entity base (via 1065 Sch. K 4c -> DR 0106 L2),
     OUT of both tax bases and out of K-1 L16. A three-place rule.
W6.  ⚠ DEPRECIATION: encode the ABSENCE. No § 168(k) add-back, no state § 179
     limit, no state basis, no recapture. Build NO nullable "state depreciation
     adjustment" field "for symmetry with GA/TN" — a nullable field a preparer
     can fill is worse than no field. Ken is the depreciation specialist: bless
     the negative explicitly so it is a RULING, not an omission.
W7.  Two rate constants, not one (see #4 above).
W8.  Colorado K-1 transmittal is a SEPARATE submission — MeF-inline, XLS, XML,
     manual, or paper DR 1706 — and explicitly NOT a PDF attachment to the
     return. Depends on [UNV-6].
W9.  Estimated tax: PTE rules != C-corp rules. 70%/100% with the first-year-
     election prior-year block; NO annualized income installment method (the
     Corporate Guide grants it to C corps; DR 0233 denies it to PTEs).
     ⚠ C9: the $5,000 threshold is a live 3-2 SOURCE SPLIT, not an erratum —
     DR 0233 instr. + DR 0106EP + SALT pub say "exceeds"; DR 0106 L31 AND the
     Corporate Income Tax Guide (incorporated by reference by the DR 0106 for
     this exact rule) say ">= / less than $5,000". Exposure is the single point
     net tax == $5,000. ✅ **RULED BY KEN 2026-08-17 (walk item B2): strictly
     greater than $5,000**, on the DR 0233 Part 1 arithmetic and on the
     Corporate Income Tax Guide's incorporation by reference. Recorded as a
     ruling on a source split, NOT as a silent correction of an erratum.
W10. Credit depth. PROPOSED: DIRECT-ENTER all DR 0106CR amounts; COMPUTE only
     the column arithmetic + the L14/L15 cap; RED-defer every sub-schedule.
W11. DR 1079 real-estate withholding on L25 — direct-enter + diagnostic.
W12. DR 0107 is a ONE-TIME filing that PERSISTS across years ("the timely first
     filing of this agreement as applicable to all future filing periods unless
     notified otherwise"). Where does the persistent per-owner flag live? It is a
     CLIENT-RECORD question, not just a form question.
W13. ✅ **RULED 2026-08-17 (walk item A1) — [UNV-7] § 174A / retroactive federal
     amendments under rolling conformity. Colorado DOES pick them up; line 1
     transcribes federal.** See the ruling block above. No longer blocking.

═══════════════════════════════════════════════════════════════════════════
[UNVERIFIED] ITEMS CARRIED FORWARD — all 9 (brief §13, audited §17.3)
═══════════════════════════════════════════════════════════════════════════
[UNV-1] CRS 2025 Title 39 still 404 (re-checked 2026-08-16/17); every statutory
        quotation here is from the OFFICIAL 2024 edition, and all matched on
        re-derivation. Risk LOW. -> W13 context.
[UNV-2] DR 0108 status for TY2025 — CDOR lists only the 2023 form (rev.
        11/17/22), whose own text points at the "Book 106" that no longer
        exists. TY2025 DR 0106/DR 0106K-I/DR 0107 never mention it. -> R11.
[UNV-3] No TY2025 "Individual Partner and Shareholder Instructions for Colorado
        K-1" (only the TY2023 file). OWNER-SIDE HELP TEXT ONLY — not blocking;
        the DR 0106K-I covers every preparer-side rule this spec needs.
[UNV-4] DR 0106K-I errata, both CONFIRMED VERBATIM: (a) S-corp half line 9
        Column A says "line 12 of I R S Form 1065" TWICE -> build to 1120-S
        line 12; (b) partnership half line 10 Column A says "claimed by the
        S corporation" -> build to "the partnership". **Do not "fix" these back.**
[UNV-5] The PTP composite carve-out is in STATUTE ONLY — zero hits for "publicly
        traded" or "7704" anywhere in the DR 0106, DR 0106K-I, DR 0107 or the
        SALT pub. Handle as a USER-ASSERTED exemption flag, never a silent pass.
        -> R14, with the full three-condition § 7704 test (incl. the (a) clause
        the research pass elided — C2).
[UNV-6] Colorado MeF program: schema, business rules, calendar, submission model
        all LOI-gated (DOR_IncomeTaxMeF2D@state.co.us). Longest-lead Ken action.
        -> W8, R15.
[UNV-7] ✅ **RULED 2026-08-17, NO LONGER BLOCKING** — § 174A / retroactive
        federal amendments under rolling conformity. Ken ruled Colorado DOES
        pick them up (walk A1); line 1 transcribes federal as filed. The
        CONFIRMING AUTHORITY is still unpulled (published Anschutz opinion,
        current 1 CCR 201-2, or CDOR § 174A guidance for TY2025), so the item
        stays open as a pre-ship re-verification. -> W13, R-CO-174A-CONFORM,
        D_CO106_BLOCK_174A_CONFORMITY (now severity=info).
[UNV-8] DR 0106 line 22 in-lieu-of amount has NO published computation anywhere
        — the instruction gives filing mechanics only. -> R7.
[UNV-9] Part V line 9 percentage: no stated decimal precision, no rounding rule,
        no zero-"Everywhere"-denominator rule on the face. Small but real — it
        moves every nonresident owner's Column B. -> D_CO106_PARTV_L9_PRECISION.

═══════════════════════════════════════════════════════════════════════════
VERIFIED STRUCTURE (read from the FINAL TY2025 CDOR PDFs by the research pass
2026-08-17 and INDEPENDENTLY RE-PULLED by the adversarial verifier 2026-08-16 —
never memory, never training data):
  DR 0106 rev. 09/19/25 (18 pp.) · DR 0106K rev. 07/18/25 · DR 0106K-I rev.
  09/18/25 (18 pp. — pp. 1-9 partnership, pp. 10-18 S corp; THE fork document)
  · DR 0106CR rev. 10/02/25 · DR 0233 rev. 07/30/25 · DR 0158-N rev. 06/04/25 ·
  DR 0107 rev. 06/05/25 · DR 1706 rev. 06/17/25 · DR 0619 rev. 08/01/25 ·
  DR 0106EP (07/12/24 code on a 2025 form — real) · DR 1705 (05/22/24, same) ·
  Income Tax Topics: SALT Parity Act (Rev. Oct 2025) · Colorado Corporate Income
  Tax Guide (Rev. Mar 2026) · CRS 2024 Title 39 · FINAL 2025 IRS 1065 / 1120-S.
Full source brief: delvio-states/research/co_pte_source_brief.md.

═══════════════════════════════════════════════════════════════════════════
GATE 1 — APPROVED BY KEN 2026-08-17. The walk (dispatch/WAVE3_WALK.md) was taken
in full: A1 ruled (§ 174A, above), B2 ratified (the $5,000 threshold), and the
six scope levers and ~30 ratifications approved as proposed. READY_TO_SEED was
flipped to True on that approval and on nothing else.
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
# GATE 1 CLEARED — flipped 2026-08-17 on Ken's in-session approval.
#
# Both gates that stood between this file and the database are now cleared:
#   (1) Ken's Gate-1 walk over W1-W12 — taken, approved as proposed; and
#   (2) W13 / [UNV-7] — the § 174A rolling-conformity question — RULED
#       (walk item A1: Colorado DOES pick up retroactive federal amendments;
#       DR 0106 line 1 transcribes federal as filed).
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = True


FORM_JURISDICTION = "CO"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"
# ONE form, TWO delvio-tax modules. The face is identical; the sourcing forks.
FORM_ENTITY_TYPES = ["1065", "1120S"]

FORM_CODE = "CO_DR0106"

# Module tokens — the fork key. Derived from the ATTACHED FEDERAL RETURN, never
# from Box A (W2 / §2.2 of the brief).
M_1065 = "1065"
M_1120S = "1120S"
MODULES = (M_1065, M_1120S)


# ═══════════════════════════════════════════════════════════════════════════
# VERIFIED CONSTANTS — tax-year-keyed; every one cited in co_pte_source_brief.md
# ═══════════════════════════════════════════════════════════════════════════

# ⚠ W7 / brief §11 — TWO DIFFERENT RATE STATUTES ON ONE FORM. Equal for TY2025;
# DO NOT COLLAPSE. § 39-22-627 moves them together *today*, but they are separate
# constants with separate authorities, and LCS projects the value moves (4.33%
# TY2027 / 4.29% TY2028).

# DR 0106 line 13 (COMPOSITE). Rate authority: § 39-22-104 — the INDIVIDUAL rate.
# § 39-22-601(5.5)(d)(III)(A) / (2.7)(d)(III)(A), C.R.S., verbatim: "the aggregate
# income derived from sources in the state multiplied by the highest marginal tax
# rate in effect under section 39-22-104".
CO_COMPOSITE_RATE: dict[int, str] = {2025: "0.044"}
CO_COMPOSITE_RATE_AUTHORITY = "C.R.S. § 39-22-104 (individual rate), via § 39-22-601(5.5)(d)(III)(A) and (2.7)(d)(III)(A)"

# DR 0106 line 20 (SALT PARITY / PTET). Rate authority: § 39-22-301 — the
# CORPORATE rate. § 39-22-344(1), C.R.S., verbatim: "an electing pass-through
# entity is subject to a tax in an amount equal to the tax rate set forth in
# section 39-22-301 for the applicable income tax year". § 39-22-301(1)(d)(I)(K):
# "four and forty one-hundredths percent of the Colorado net income".
CO_PTET_RATE: dict[int, str] = {2025: "0.044"}
CO_PTET_RATE_AUTHORITY = "C.R.S. § 39-22-301(1)(d)(I)(K) (corporate rate), via § 39-22-344(1)"

# DR 0106K line 16 uses "4.4% (0.044)" verbatim in all three of its variants.
# It is the rate of whichever regime the entity is in (composite -> composite
# rate; SALT Parity -> PTET rate). Same value TY2025; different authority.

# Due date — 15th day of the FOURTH month (NOT the C corp's fifth).
# § 39-22-608(2)(a), C.R.S.: "Except as provided in subsection (2)(b) ... on or
# before the fifteenth day of the fourth month following the close of the taxable
# year." (2)(b) reaches only C corporations filing under § 39-22-601(2); the PTE
# return is filed under (5.5)(a) / (2.7)(a), so (2)(b) does not reach it.
# Corroborated on the DR 0106 face and by § 39-22-609(1) (payment, same month).
CO_DUE_MONTH: dict[int, int] = {2025: 4}
CO_DUE_DAY: dict[int, int] = {2025: 15}
CO_EXTENSION_MONTHS: dict[int, int] = {2025: 6}     # automatic; NO extension to pay
CO_EXTENSION_VOUCHER = "DR 0158-N"
# Weekend/legal-holiday roll to the next business day — stated on the face.

# Delinquent-payment penalty gate (DR 0106 line 29): "If 90% of the tax is not
# paid by the original due date (without extension)".
CO_EXTENSION_PAY_PCT: dict[int, str] = {2025: "0.90"}
CO_PENALTY_MIN_DOLLARS: dict[int, int] = {2025: 5}
CO_PENALTY_FIRST_MONTH_PCT: dict[int, str] = {2025: "0.05"}
CO_PENALTY_ADDL_MONTH_PCT: dict[int, str] = {2025: "0.005"}
CO_PENALTY_MAX_PCT: dict[int, str] = {2025: "0.12"}

# Estimated tax (DR 0106EP / DR 0233).
# ⚠ W9 / C9 — LIVE 3-2 SOURCE SPLIT, not an erratum. "exceeds": DR 0233 instr.,
# DR 0106EP, SALT Parity pub. ">= / less than $5,000": DR 0106 line 31 AND the
# Colorado Corporate Income Tax Guide (which the DR 0106 EXPRESSLY incorporates
# by reference for this exact rule). Exposure is the single point net tax ==
# $5,000. RULED BY KEN 2026-08-17, walk item B2 (a ruling on a source split, not
# a correction): STRICTLY GREATER THAN $5,000, because DR 0233 Part 1 computes
# "line 1 - $5,000; If line 2 is larger, enter zero and no penalty is due" — the
# form's own arithmetic is the tiebreak, and the Corporate Income Tax Guide is
# the source the DR 0106 expressly incorporates for this rule.
CO_EST_TAX_THRESHOLD: dict[int, int] = {2025: 5000}
CO_EST_THRESHOLD_STRICTLY_GREATER: dict[int, bool] = {2025: True}
CO_EST_REQUIRED_CURRENT_PCT: dict[int, str] = {2025: "0.70"}   # 70% of actual net CO tax
CO_EST_REQUIRED_PRIOR_PCT: dict[int, str] = {2025: "1.00"}     # 100% of preceding year
CO_EST_LARGE_ENTITY_THRESHOLD: dict[int, int] = {2025: 1000000}
CO_EST_LARGE_ENTITY_Q1_PCT: dict[int, str] = {2025: "0.25"}
CO_EST_QUARTER_MONTHS: dict[int, list] = {2025: [4, 6, 9, 12]}  # 15th day of each
# DR 0233 line 18: underpayment x 12% for dates in 2025, 11% for dates in 2026.
CO_EST_INTEREST_RATE: dict[int, str] = {2025: "0.12", 2026: "0.11"}
# ⚠ Colorado law provides NO annualized income installment method for PTEs
# (DR 0233, verbatim). The Corporate Guide DOES grant it to C corps. Genuine
# PTE/C-corp divergence — do not inherit a C-corp estimated-tax module wholesale.
CO_EST_ANNUALIZED_METHOD_AVAILABLE: dict[int, bool] = {2025: False}

# DR 0106CR line 38 = SUM of lines 5 through 37 (verifier addition — NOT 1-37;
# lines 1-4 are recapture and the other-state-tax block).
CO_CR_TOTAL_RANGE: tuple = (5, 37)

# Retroactive SALT Parity election window (TY2018-2021) — CLOSED 2024-06-30.
# § 39-22-343(1)(c)(I), C.R.S.: "must make the election on or after September 1,
# 2023, but before July 1, 2024, in a composite amended tax return".
CO_RETRO_ELECTION_WINDOW_CLOSED = "2024-06-30"


def _yk(d: dict, year: int):
    """Year-keyed lookup with a TY2025 fallback."""
    return d.get(year) if d.get(year) is not None else d[2025]


# ═══════════════════════════════════════════════════════════════════════════
# THE FORK — F1..F16. 16 forks, NOT 12 (verifier 2026-08-16 RAISED the count).
#
# Fourteen of the sixteen change the ARITHMETIC, and the module is determined by
# the ATTACHED FEDERAL RETURN — never by Box A (W2).
#
# F13-F16 were ADDED by the adversarial pass. They all live inside the
# DR 0106K-I's two halves (pp. 1-9 partnership / pp. 10-18 S corp) — the same
# document the research pass correctly called "where the fork actually lives",
# and then partly flattened. F15 and F16 are SUBSTANTIVE MODIFICATION ITEMS, not
# wording variants: an S-corp return built from the partnership half silently
# drops a foreign-tax ADDITION and a Sec. 280C SUBTRACTION; a partnership return
# built from the S-corp half silently drops the Sec. 39-22-206 export-taxpayer
# subtraction.
#
# Every fork below is a real branch. The harness proves each returns DIFFERENT
# values for 1065 vs 1120S.
# ═══════════════════════════════════════════════════════════════════════════

# -- F4: federal Schedule K lines summed into DR 0106 line 2 ----------------
CO_L2_SCHK_LINES: dict[str, list] = {
    M_1065:  ["2", "3c", "4c", "5", "6a", "7", "8", "9a", "10", "11"],
    M_1120S: ["2", "3c", "4", "5a", "6", "7", "8a", "9", "10"],
}

# -- F5: the Sec. 179-disposition statement line (SEC. 179 TOUCHPOINT (i)) ---
CO_179_DISPOSITION_SCHK_LINE: dict[str, str] = {
    M_1065:  "Schedule K line 20c (Form 1065)",
    M_1120S: "Schedule K line 17d (Form 1120-S)",
}

# -- F6: Schedule L depreciable-assets rows for Boxes B and C ---------------
CO_BOXBC_SCHL_LINE: dict[str, str] = {
    M_1065:  "Schedule L line 9b, columns (b) and (d) (Form 1065)",
    M_1120S: "Schedule L line 10b, columns (b) and (d) (Form 1120-S)",
}

# -- DR 0106K Column A federal K-1 BOX maps (brief Sec. 10.2) ---------------
# Schedule K *line* numbers and Schedule K-1 *box* numbers are DIFFERENT
# NAMESPACES. Kept as two separate tables so a transcription cannot cross them.
CO_K1_BOX_MAP: dict[str, dict] = {
    M_1065: {
        "1": ["1"], "2": ["2"], "3": ["3"], "4": ["4c"],
        "5": ["5", "6a"], "6": ["7"], "7": ["8", "9a", "10"], "8": ["11"],
        "12": ["12", "13"],
    },
    M_1120S: {
        "1": ["1"], "2": ["2"], "3": ["3"], "4": None,   # F3 -- N/A for an S corp
        "5": ["4", "5a"], "6": ["6"], "7": ["7", "8a", "9"], "8": ["10"],
        "12": ["11", "12"],
    },
}

# -- SEC. 179 TOUCHPOINT (ii): the Sec. 179 DEDUCTION itself rides K-1 line 12.
# 1065 K-1 Box 12 and 1120-S K-1 Box 11 ARE the Sec. 179 deduction (verified
# against the FINAL 2025 federal forms: 1065 Sch. K line 12 / 1120-S Sch. K line
# 11 = "Section 179 deduction (attach Form 4562)"). K-1 line 12 is entered
# NEGATIVE and is aggregated into DR 0106 line 6 SIGN-INVERTED. DR 0106 line 2
# lists income lines only and deliberately EXCLUDES Sch. K 12/13 (1065) and
# 11/12 (1120-S) -- so without this path the Sec. 179 deduction reaches Colorado
# NOWHERE. (Verifier correction C3, HIGH severity.)
CO_179_DEDUCTION_K1_BOX: dict[str, str] = {
    M_1065:  "Schedule K-1 (Form 1065) Box 12",
    M_1120S: "Schedule K-1 (Form 1120-S) Box 11",
}

# -- F15: DR 0106K line 11 "Other Colorado additions" inventories -----------
_CO_L11_SHARED = [
    "non-Colorado state or local bond interest (excludes bond-premium amortization; reduced by IRC-required allocable deductions)",
    "unauthorized-alien labor service expenses (Sec. 39-22-529, C.R.S.)",
    "discriminatory-club expenses (club licensed under Sec. 44-3-418, C.R.S.)",
    "lower-tier partnership line-11 amounts (tier-chain accumulation)",
]
CO_K1_L11_ITEMS: dict[str, list] = {
    M_1065: list(_CO_L11_SHARED),
    # C7 (HIGH) -- S-CORP ONLY, missed entirely by the research pass:
    M_1120S: list(_CO_L11_SHARED) + [
        "foreign income, war profits, or excess profits taxes paid or accrued to any foreign "
        "country or U.S. possession, deducted by the S corporation on line 12 of IRS Form 1120-S",
    ],
}
# Column B: the unauthorized-alien and discriminatory-club items go in at their
# FULL Column A amount, not an apportioned share. The S-corp foreign-tax item is
# NOT in that full-amount list -- it takes the ordinary "portion attributable to
# Colorado" rule.
CO_K1_L11_FULL_AMOUNT_IN_COL_B = (
    "unauthorized-alien labor service expenses",
    "discriminatory-club expenses",
)

# -- F16: DR 0106K line 13 "Colorado subtractions" inventories --------------
_CO_L13_SHARED = [
    "U.S. government obligation interest",
    "Colorado Marijuana Code IRC Sec. 280E expenditures",
    "Colorado Natural Medicine Code IRC Sec. 280E expenditures",
    "state income tax refunds not previously deducted",
    "lower-tier partnership line-13 amounts (tier-chain accumulation)",
]
CO_K1_L13_ITEMS: dict[str, list] = {
    # PARTNERSHIP ONLY -- Sec. 39-22-206 is BY ITS OWN TERMS a partnership
    # provision ("If a partnership qualifies as an export taxpayer, its partners
    # may exclude..."), verified in CRS 2024. ABSENT from the S-corp half.
    M_1065: list(_CO_L13_SHARED) + [
        "export-taxpayer foreign source income (Sec. 39-22-206, C.R.S.) -- PARTNERSHIP ONLY",
    ],
    # C8 (HIGH) -- S-CORP ONLY, omitted entirely by the research pass. Has its
    # OWN Column B rule: included "to the extent the underlying or related
    # expenses or losses are from business activity in Colorado".
    M_1120S: list(_CO_L13_SHARED) + [
        "wages or salaries paid or incurred but not deductible federally due to IRC Sec. 280C "
        "-- S CORPORATION ONLY (own Column B rule: business activity in Colorado)",
    ],
}
# The state income tax REFUND item splits on DIFFERENT AXES per module -- the
# same axes as the F7 line-9 split.
CO_K1_L13_REFUND_SPLIT_AXIS: dict[str, str] = {
    M_1065:  "C-corporation partner vs non-C-corporation partner",
    M_1120S: "resident shareholder vs nonresident shareholder",
}

# -- F13: DR 0106K line 16 summation WORDING (arithmetically identical) -----
# The loader must not assert one document's wording against the other.
CO_K1_L16_SUM_WORDING: dict[str, str] = {
    M_1065:  "Sum the amounts on lines 1 through 3 and lines 5 through 13",
    M_1120S: "Sum the amounts on lines 1 through 13",
}
# Line 4 is skipped either way: guaranteed payments are excluded for a
# partnership, and line 4 is N/A for an S corp.
CO_K1_L16_LINES: tuple = ("1", "2", "3", "5", "6", "7", "8", "9", "10", "11", "12", "13")

# -- F8: distributive-share ratio for modifications ------------------------
CO_DISTRIBUTIVE_RATIO: dict[str, str] = {
    M_1065:  "the same ratio used to determine the partner's distributive share of partnership "
             "taxable income or loss generally for federal income tax purposes",
    M_1120S: "the manner provided in, and subject to any election made under, section 1377(a) or "
             "1362(e) of the IRC (Sec. 39-22-321(4), C.R.S.)",
}

# -- F9: alternate-apportionment cross-reference inside the Column B rule ---
CO_COLB_APPORTIONMENT_XREF: dict[str, str] = {
    M_1065:  "Sec. 39-22-109 or Sec. 39-22-303.6, C.R.S.",
    M_1120S: "Sec. 39-22-303.6, C.R.S., and, if applicable, Sec. 39-22-303.7, C.R.S. "
             "(mutual fund service corporations -- RED-deferred at R9)",
}

# -- F11: mandatory-composite CARVE-OUTS -----------------------------------
# C1 (HIGH) -- the research pass said the S corp had "no analogue". WRONG.
# Sec. 39-22-601(2.7)(d)(VII) exists and carries TWO carve-outs. Only the PTP
# carve-out is partnership-only. W3's mandatory-composite RED must honour the
# all-owners-excluded carve-out for S CORPS TOO, or it false-positives on any
# S corp whose every nonresident shareholder filed a DR 0107.
CO_COMPOSITE_CARVEOUTS: dict[str, list] = {
    M_1065: [
        "salt_parity_election",         # (5.5)(d)(VII)(A)
        "publicly_traded_partnership",  # (5.5)(d)(VII)(B) -- PARTNERSHIP ONLY; [UNV-5]; R14
        "all_owners_excluded",          # (5.5)(d)(VII)(C)
    ],
    M_1120S: [
        "salt_parity_election",         # (2.7)(d)(VII)(A)
        "all_owners_excluded",          # (2.7)(d)(VII)(B)  <- C1: this EXISTS
    ],
}

# -- F10: composite exclusion for ENTITY owners ----------------------------
# Sec. 39-22-601(5.5)(d)(II)(B) excludes "Any nonresident partner that is a
# corporation or a partnership". The S-corp list at (2.7)(d)(II) has no analogue
# -- an S corp cannot have corporate/partnership shareholders in the first place.
CO_ENTITY_OWNER_EXCLUDED: dict[str, bool] = {M_1065: True, M_1120S: False}

# -- F12: the DR 0106 line 1 instruction erratum ---------------------------
# The instruction names ONLY the 1065 and never names the 1120-S for line 1.
# Build to BOTH: 1120-S Sch. K line 1 is the S-corp source.
CO_L1_INSTRUCTION_NAMES_MODULE: dict[str, bool] = {M_1065: True, M_1120S: False}
CO_L1_SOURCE: dict[str, str] = {
    M_1065:  "Schedule K line 1 (Form 1065) -- Ordinary business income (loss)",
    M_1120S: "Schedule K line 1 (Form 1120-S) -- Ordinary business income (loss)",
}


# ═══════════════════════════════════════════════════════════════════════════
# FORK REGISTRY — the 16 forks, each with its per-module value and authority.
# ═══════════════════════════════════════════════════════════════════════════

CO_FORKS: list[dict] = [
    {"fork_id": "F1", "name": "Sourcing of nonresident-owner income", "arithmetic": True,
     M_1065: "DIRECT SOURCING is the DEFAULT (Sec. 39-22-109); receipts-factor apportionment only AT THE PARTNERSHIP'S ELECTION (Sec. 39-22-203(1)(a))",
     M_1120S: "MANDATORY receipts-factor apportionment (Sec. 39-22-303.6) -- no direct-sourcing option",
     "authority": "DR 0106 pp. 3-4; DR 0106K-I; C.R.S. Secs. 39-22-203(1)(a), 39-22-321"},
    {"fork_id": "F2", "name": "Who gets a Column B on the K-1", "arithmetic": True,
     M_1065: "nonresident individuals/estates/trusts always; nonresident corporations/partnerships ONLY if a SALT Parity election is made -- otherwise Column B is left BLANK for them",
     M_1120S: "EVERY nonresident shareholder",
     "authority": "DR 0106K-I, partnership vs S-corp halves"},
    {"fork_id": "F3", "name": "Guaranteed payments (K-1 line 4)", "arithmetic": True,
     M_1065: "exist; Column B ALWAYS direct-sourced under 1 CCR 201-2, Rule 39-22-109(3)(b)(xii) -- even when the partnership elected formulary apportionment",
     M_1120S: "N/A -- the DR 0106K-I S-corp box map prints 'N/A' against line 4",
     "authority": "DR 0106K-I"},
    {"fork_id": "F4", "name": "Federal Schedule K feed into DR 0106 line 2", "arithmetic": True,
     M_1065: "Sch. K lines 2, 3c, 4c, 5, 6a, 7, 8, 9a, 10, 11",
     M_1120S: "Sch. K lines 2, 3c, 4, 5a, 6, 7, 8a, 9, 10",
     "authority": "DR 0106 line 2 instruction"},
    {"fork_id": "F5", "name": "Sec. 179-disposition statement line", "arithmetic": True,
     M_1065: "Sch. K line 20c", M_1120S: "Sch. K line 17d",
     "authority": "DR 0106 line 2 instruction"},
    {"fork_id": "F6", "name": "Depreciable-assets balance-sheet Boxes B and C", "arithmetic": True,
     M_1065: "Sch. L line 9b, cols (b) and (d)", M_1120S: "Sch. L line 10b, cols (b) and (d)",
     "authority": "DR 0106 Box B/C instruction"},
    {"fork_id": "F7", "name": "State income tax add-back split (K-1 line 9 Col. A)", "arithmetic": True,
     M_1065: "split by PARTNER TYPE: non-C-corp partners get ALL state income taxes regardless of state; C-CORPORATION partners get Colorado-only",
     M_1120S: "split by RESIDENCY: RESIDENT shareholders get all state income taxes; NONRESIDENT shareholders get Colorado-only",
     "authority": "DR 0106K-I, both halves"},
    {"fork_id": "F8", "name": "Distributive-share ratio for modifications", "arithmetic": True,
     M_1065: CO_DISTRIBUTIVE_RATIO[M_1065], M_1120S: CO_DISTRIBUTIVE_RATIO[M_1120S],
     "authority": "DR 0106K-I; C.R.S. Sec. 39-22-321(4)"},
    {"fork_id": "F9", "name": "Alternate apportionment cross-reference in the Column B rule", "arithmetic": True,
     M_1065: CO_COLB_APPORTIONMENT_XREF[M_1065], M_1120S: CO_COLB_APPORTIONMENT_XREF[M_1120S],
     "authority": "DR 0106K-I"},
    {"fork_id": "F10", "name": "Composite-return exclusion for entity owners", "arithmetic": True,
     M_1065: "'Any nonresident partner that is a corporation or a partnership' is excluded",
     M_1120S: "no analogue -- an S corp cannot have corporate/partnership shareholders",
     "authority": "C.R.S. Sec. 39-22-601(5.5)(d)(II)(B) vs (2.7)(d)(II)"},
    {"fork_id": "F11", "name": "Composite requirement carve-outs (CORRECTED C1)", "arithmetic": True,
     M_1065: "SALT Parity election; PUBLICLY TRADED PARTNERSHIP (partnership-only, Sec. 7704 -- three conditions); all-owners-excluded",
     M_1120S: "SALT Parity election; all-owners-excluded (Sec. 39-22-601(2.7)(d)(VII)(B) EXISTS -- 'no analogue' was WRONG). Only the PTP carve-out is missing on the S-corp side",
     "authority": "C.R.S. Sec. 39-22-601(5.5)(d)(VII) AND (2.7)(d)(VII) -- neither is in the DR 0106 instructions ([UNV-5])"},
    {"fork_id": "F12", "name": "DR 0106 line 1 instruction wording (erratum)", "arithmetic": False,
     M_1065: "names IRS Form 1065 explicitly",
     M_1120S: "the instruction NEVER names 1120-S for line 1 -- erratum; build to 1120-S Sch. K line 1 anyway",
     "authority": "DR 0106 line 1 instruction"},
    {"fork_id": "F13", "name": "K-1 line 16 summation wording (added by verifier)", "arithmetic": False,
     M_1065: CO_K1_L16_SUM_WORDING[M_1065], M_1120S: CO_K1_L16_SUM_WORDING[M_1120S],
     "authority": "DR 0106K-I, both halves -- arithmetically identical (L4 is N/A for an S corp)"},
    {"fork_id": "F14", "name": "When K-1 lines 14/15 are MANDATORY (added by verifier)", "arithmetic": True,
     M_1065: "REQUIRED for any partner that is (or is treated as) a C corporation; optional otherwise",
     M_1120S: "NEVER required for any shareholder -- optional only, on request",
     "authority": "DR 0106K-I, both halves"},
    {"fork_id": "F15", "name": "K-1 line 11 'Other Colorado additions' inventory (added by verifier)", "arithmetic": True,
     M_1065: "bond interest / unauthorized alien / discriminatory club / lower-tier (4 items)",
     M_1120S: "the same four PLUS a FOREIGN-TAX ADD-BACK (5 items) -- a real modification item, not a wording variant",
     "authority": "DR 0106K-I, S-corp half"},
    {"fork_id": "F16", "name": "K-1 line 13 'Colorado subtractions' inventory (added by verifier)", "arithmetic": True,
     M_1065: "includes EXPORT-TAXPAYER foreign source income (Sec. 39-22-206 -- a partnership-only statute); refund splits by C-corp vs non-C-corp partner",
     M_1120S: "NO export-taxpayer item; ADDS a Sec. 280C disallowed-wages subtraction with its own Column B rule; refund splits by resident vs nonresident",
     "authority": "DR 0106K-I, both halves; C.R.S. Sec. 39-22-206"},
]

CO_FORKS_TOTAL = 16
# F12 and F13 change the SOURCE TEXT (erratum / wording) but not the arithmetic.
# The other fourteen change what the return computes -- W2's "fourteen of the
# sixteen key off the answer".
CO_FORKS_ARITHMETIC = 14


def co_fork(fork_id: str, module: str) -> str:
    """Return the per-module value of fork F1..F16. Raises on an unknown fork."""
    if module not in MODULES:
        raise ValueError(f"unknown module {module!r} (expected one of {MODULES})")
    for f in CO_FORKS:
        if f["fork_id"] == fork_id:
            return f[module]
    raise ValueError(f"unknown fork {fork_id!r}")


# ═══════════════════════════════════════════════════════════════════════════
# PART I — the entity-wide computation, and THE SIGN FLIP.
#
# Part I lines 1-10 are ENTITY-WIDE: all owners, residents and nonresidents,
# corporate partners included, and (per the DR 0106K-I) a unitary C-corporation
# partner excluded from a SALT Parity election. The Part II and Part III bases
# are SUBSETS built from the K-1s, NOT from line 10. Line 10 feeds ONLY Part V
# line 1.
# ═══════════════════════════════════════════════════════════════════════════

def co_line1(module: str, sch_k: dict) -> float:
    """DR 0106 line 1 -- Ordinary income from federal Schedule K.

    F12: the instruction names only the 1065. Build to BOTH modules anyway.
    Sign rule (verbatim): "Enter income and gains as positive numbers; enter
    losses and deductions as negative numbers."
    """
    if module not in MODULES:
        raise ValueError(f"unknown module {module!r}")
    return float(sch_k.get("1", 0) or 0)


def co_line2(module: str, sch_k: dict, sec179_disposition_gain: float = 0.0) -> float:
    """DR 0106 line 2 -- "Sum of all other income".

    F4  -- the federal Schedule K line set differs per module.
    F5  -- PLUS the SEC. 179 DISPOSITION aggregation (TOUCHPOINT (i)), verbatim:
           "any gain or loss on the sale, exchange, or other disposition of
           property reported on a statement attached for line 20c of Schedule K
           (I R S Form 1065) or line 17d of Schedule K (I R S Form 1120-S) for
           which a section 179 deduction has been passed through to partners or
           shareholders". This item sits OUTSIDE federal Schedule K's numbered
           income lines because it is reported at the OWNER level, so Colorado
           pulls it back in to build an entity-level figure. A spec that omits it
           UNDERSTATES line 2.

    NOTE line 2 lists INCOME lines only. It deliberately EXCLUDES Sch. K 12/13
    (1065) and 11/12 (1120-S) -- i.e. it excludes the Sec. 179 DEDUCTION, which
    arrives instead at line 6 via K-1 line 12 (TOUCHPOINT (ii)).
    """
    lines = CO_L2_SCHK_LINES[module]
    return float(sum(float(sch_k.get(ln, 0) or 0) for ln in lines)) + float(sec179_disposition_gain or 0)


def co_part1(module: str, sch_k: dict, k1_col_a: dict,
             sec179_disposition_gain: float = 0.0, line7_280e: float = 0.0,
             apply_sign_flip: bool = True) -> dict:
    """DR 0106 Part I, lines 1-10 -- and THE SIGN FLIP.

    `k1_col_a` carries the entity-wide aggregate of DR 0106K COLUMN A, using the
    K-1's OWN SIGNS: keys l9, l10, l11 are POSITIVE additions; l12 and l13 are
    NEGATIVE (the K-1 says so verbatim).

    ⚠ THE SIGN FLIP -- "the single most likely arithmetic bug in this form".
      DR 0106K-I, BOTH halves: "Enter any losses on lines 1, 2, 3, or 8, and any
      federal deductions on line 12, as negative amounts" and "Enter subtractions
      on line 13 as a negative amount".
      DR 0106: "Enter the deductions on this line 6 as a positive number" /
      "Enter the subtraction on this line 7 as a positive number" / "Enter the
      deductions on this line 8 as a positive number"; L9 = L6+L7+L8; L10 = L5-L9.

      => Aggregating K-1 Col. A L12 -> DR 0106 L6 and L13 -> L8 REQUIRES SIGN
         INVERSION.
      => Lines 3 and 4 (from K-1 L10 and L9+L11) are ALREADY POSITIVE and must
         NOT be inverted. Both halves of the rule are pinned by the verifier.

    `apply_sign_flip=False` reproduces the BUG, for the harness oracle only.
    """
    if module not in MODULES:
        raise ValueError(f"unknown module {module!r}")

    l1 = co_line1(module, sch_k)
    l2 = co_line2(module, sch_k, sec179_disposition_gain)

    # Lines 3 and 4 -- K-1 Column A ADDITIONS. Already positive. NO INVERSION.
    l3 = float(k1_col_a.get("l10", 0) or 0)                                  # business meals, IRC 274(k)
    l4 = float(k1_col_a.get("l9", 0) or 0) + float(k1_col_a.get("l11", 0) or 0)  # state tax add-back + other CO additions
    l5 = l1 + l2 + l3 + l4

    # Lines 6 and 8 -- K-1 Column A DEDUCTIONS/SUBTRACTIONS. INVERT.
    # Line 6 carries the SEC. 179 DEDUCTION (touchpoint (ii)) inside K-1 line 12.
    raw_l12 = float(k1_col_a.get("l12", 0) or 0)
    raw_l13 = float(k1_col_a.get("l13", 0) or 0)
    l6 = -raw_l12 if apply_sign_flip else raw_l12
    l7 = float(line7_280e or 0)     # entered as a POSITIVE number; excluded from L8
    l8 = -raw_l13 if apply_sign_flip else raw_l13
    l9 = l6 + l7 + l8
    l10 = l5 - l9

    return {"L1": l1, "L2": l2, "L3": l3, "L4": l4, "L5": l5,
            "L6": l6, "L7": l7, "L8": l8, "L9": l9, "L10": l10}


# ═══════════════════════════════════════════════════════════════════════════
# OWNER MODEL + the DR 0106K owner schedule
#
# An owner is a plain dict:
#   residency    : "resident" | "part_year" | "nonresident"
#   owner_kind   : "individual" | "estate" | "trust" | "c_corp" | "partnership"
#   dr0107       : bool  -- timely-filed Nonresident Partner/Shareholder Agreement
#   exempt_112   : bool  -- exempt under Sec. 39-22-112(1), C.R.S.
#   unitary_ccorp: bool  -- C corporation UNITARY with the partnership
#   col_a        : float -- sum of Col. A lines 1-3 + 5-13 (line 4 SKIPPED)
#   col_b        : float -- sum of Col. B lines 1-3 + 5-13 (line 4 SKIPPED)
# ═══════════════════════════════════════════════════════════════════════════

def co_owner_status(owner: dict) -> str:
    """Residency status for K-1 purposes.

    PART-YEAR RESIDENTS ARE TREATED AS RESIDENTS, verbatim from the DR 0106K-I:
    "If a partner was a resident for only part of the tax year, check the box to
    indicate that they were a resident and complete the Colorado K-1 for the
    partner following the instructions for resident partners."
    """
    return "resident" if owner.get("residency") in ("resident", "part_year") else "nonresident"


def co_k1_line9_scope(module: str, owner: dict) -> str:
    """F7 -- the state income tax add-back split on K-1 line 9, COLUMN A.

    PARTNERSHIP: splits by PARTNER TYPE.
      non-C-corp partners  -> ALL deducted state income taxes, REGARDLESS OF STATE
      C-corporation partners -> COLORADO income tax only
    S CORPORATION: splits by RESIDENCY.
      resident shareholders    -> ALL deducted state income taxes
      nonresident shareholders -> COLORADO income tax only

    COLUMN B is Colorado income tax only in BOTH modules.
    The add-back also picks up line 9 of a Colorado K-1 issued to the entity by a
    LOWER-TIER partnership -- a tier-chain accumulation.
    """
    if module == M_1065:
        return "colorado_only" if owner.get("owner_kind") == "c_corp" else "all_states"
    if module == M_1120S:
        return "all_states" if co_owner_status(owner) == "resident" else "colorado_only"
    raise ValueError(f"unknown module {module!r}")


def co_k1_column_b_populated(module: str, owner: dict, salt_parity_election: bool = False) -> bool:
    """F2 -- who gets a Column B at all.

    PARTNERSHIP, verbatim: "If the partnership has not made a SALT Parity Act
    election, leave these lines in Column B blank for all partners that are
    corporations or partnerships."
    S CORP, verbatim: "Complete lines 1 through 13 in Column B for each
    nonresident shareholder."
    """
    if co_owner_status(owner) == "resident":
        return False
    if module == M_1065 and owner.get("owner_kind") in ("c_corp", "partnership"):
        return bool(salt_parity_election)
    return True


def co_k1_lines_14_15_required(module: str, owner: dict) -> bool:
    """F14 (verifier correction C6).

    PARTNERSHIP: "must be completed for any partner that is a C corporation or
    that is treated as a C corporation for Colorado income tax purposes, but is
    not required for any other partner, unless the partner needs the information".
    S CORP: "The completion of lines 14 and 15 is NOT REQUIRED on a Colorado K-1
    prepared for ANY S corporation shareholder, unless the shareholder needs the
    information" -- NEVER mandatory.
    """
    if module == M_1120S:
        return False
    return owner.get("owner_kind") == "c_corp" or bool(owner.get("treated_as_ccorp"))


def co_k1_line16(col_amount: float, rate: str) -> float:
    """DR 0106K line 16 -- the PER-OWNER tax, FLOORED AT ZERO.

    Verbatim: "...multiply the sum by 4.4% (0.044), and enter the result on line
    16. If the sum ... is a negative amount, enter 0 (zero) on line 16."

    Three variants, all floored:
      composite            -> Column B x rate
      SALT Parity resident -> Column A x rate  (incl. a PART-YEAR resident)
      SALT Parity nonres.  -> Column B x rate

    Also: "Do not enter on line 16 any amount that the partnership has not
    remitted to the Department."
    """
    return round(max(0.0, float(col_amount) * float(rate)), 2)


# ═══════════════════════════════════════════════════════════════════════════
# THE THREE-MODE STATE MACHINE (W3)
#
#   MODE A -- NEITHER. Informational-only DR 0106. Parts II and III blank,
#             line 21 = 0. STILL A MANDATORY FILING, and the K-1s are still
#             mandatory. "Every partnership and S corporation must file a
#             DR 0106 for any year it is doing business in Colorado."
#             Mode A is a REAL and COMMON filing, not an edge case -- a spec
#             that treats the DR 0106 as a tax-computing form only will not
#             produce this return.
#   MODE B -- COMPOSITE nonresident return (Part II, lines 12-16). MANDATORY,
#             not elective, when Mode C is not elected and an unexcluded
#             nonresident owner exists.
#   MODE C -- SALT PARITY ACT election (Part III, lines 17-20). ELECTIVE.
#
# MUTUAL EXCLUSIVITY, verbatim from the DR 0106 line 21 instruction: "Part II
# and Part III should not both be completed, as a partnership or S corporation
# may file a composite return (by completing Part II) or make a SALT Parity Act
# election (and complete Part III), but it may not do both."
# Statutory basis: Sec. 39-22-344(5), C.R.S.
# ═══════════════════════════════════════════════════════════════════════════

CO_MODE_A = "A"   # informational only -- no tax
CO_MODE_B = "B"   # composite nonresident return
CO_MODE_C = "C"   # SALT Parity Act (PTET) return


class CoModeConflict(ValueError):
    """Parts II and III both completed -- a hard RED, never a silent precedence."""


def co_mode(salt_parity_election: bool, composite_filed: bool) -> str:
    """Resolve the filing mode. Raises CoModeConflict if both parts are used."""
    if salt_parity_election and composite_filed:
        raise CoModeConflict(
            "DR 0106 Part II and Part III are MUTUALLY EXCLUSIVE (line 21 instruction; "
            "Sec. 39-22-344(5), C.R.S.). An entity may file a composite return OR make a "
            "SALT Parity Act election, but it may not do both."
        )
    if salt_parity_election:
        return CO_MODE_C
    if composite_filed:
        return CO_MODE_B
    return CO_MODE_A


def co_composite_excluded(module: str, owner: dict) -> str:
    """Is this owner EXCLUDED from the mandatory composite return? Returns the
    exclusion reason, or "" if the owner must be included.

    The DR 0106 p. 2 list (four exclusions), verbatim:
      - "Any Colorado resident partner or shareholder, INCLUDING partners and
         shareholders that are residents of Colorado for only part of the tax year"
      - "Any nonresident partner that is a corporation or a partnership"  [F10]
      - "Any nonresident partner or shareholder that is exempt from Colorado
         income tax under section 39-22-112(1), C.R.S."
      - "Any nonresident partner or shareholder that timely files a Nonresident
         Partner or Shareholder Agreement (form DR 0107)"

    PLUS a FIFTH exclusion that is NOT in the general list -- it is in the Part II
    line 12 instruction, and the verifier STRENGTHENED it to statutory footing at
    Sec. 39-22-601(5.5)(d)(III)(A) and (2.7)(d)(III)(A): "If the income computed
    for any nonresident partner is a negative amount, that nonresident partner's
    income is EXCLUDED from the calculation of aggregate income."

    W4: the negative-income exclusion here and the per-owner floor at zero on
    K-1 line 16 are ONE RULE, built together -- that is exactly why the line-13
    reconciliation holds.
    """
    if co_owner_status(owner) == "resident":
        return "resident (incl. part-year)"
    if CO_ENTITY_OWNER_EXCLUDED.get(module) and owner.get("owner_kind") in ("c_corp", "partnership"):
        return "nonresident corporation or partnership (F10)"
    if owner.get("exempt_112"):
        return "exempt under Sec. 39-22-112(1), C.R.S."
    if owner.get("dr0107"):
        return "timely-filed DR 0107 agreement"
    if float(owner.get("col_b", 0) or 0) < 0:
        return "negative Colorado-source income (fifth exclusion)"
    return ""


def co_composite_required(module: str, owners: list, salt_parity_election: bool = False,
                          is_publicly_traded: bool = False) -> bool:
    """Is a composite return MANDATORY?

    Sec. 39-22-601(5.5)(d)(I), C.R.S., verbatim: "every partnership required to
    file a return under subsection (5.5)(a) of this section SHALL ALSO FILE A
    COMPOSITE RETURN and make a composite payment of tax on behalf of all of its
    nonresident partners." Identical language at (2.7)(d)(I) for S corporations.
    It is MANDATORY, not elective.

    Carve-outs (F11). ⚠ C1 (HIGH): the all-owners-excluded carve-out EXISTS FOR
    BOTH MODULES -- Sec. 39-22-601(5.5)(d)(VII)(C) and (2.7)(d)(VII)(B). The
    research pass said the S corp had "no analogue" and was WRONG; without this,
    the mandatory-composite RED false-positives on any S corp whose every
    nonresident shareholder filed a DR 0107.
    Only the PUBLICLY TRADED PARTNERSHIP carve-out is partnership-only, and it is
    STATUTE-ONLY ([UNV-5]) -- user-asserted flag, never a silent pass (R14).
    """
    if salt_parity_election:
        return False   # carve-out (A), BOTH modules
    if is_publicly_traded and "publicly_traded_partnership" in CO_COMPOSITE_CARVEOUTS[module]:
        return False   # PARTNERSHIP ONLY; [UNV-5]; R14
    included = [o for o in owners if not co_composite_excluded(module, o)]
    if not included:
        return False   # all-owners-excluded carve-out -- BOTH modules (C1)
    return True


def co_composite_base(module: str, owners: list) -> float:
    """DR 0106 Part II line 12 -- the composite base.

    Verbatim: "should equal the sum of the amounts on lines 1 through 3 and lines
    5 through 13 in COLUMN B of the Colorado K-1 (DR 0106K) for all nonresident
    partners or shareholders included in this composite return."

    GUARANTEED PAYMENTS (K-1 line 4) ARE EXCLUDED -- the sum skips line 4 -- and
    negative-income owners are excluded ENTIRELY, not netted (W5, W4).
    """
    return float(sum(float(o.get("col_b", 0) or 0)
                     for o in owners if not co_composite_excluded(module, o)))


def co_composite_tax(module: str, owners: list, year: int = FORM_TAX_YEAR) -> float:
    """DR 0106 line 13 = line 12 x the COMPOSITE rate (Sec. 39-22-104 authority)."""
    return round(co_composite_base(module, owners) * float(_yk(CO_COMPOSITE_RATE, year)), 2)


def co_composite_net_tax(tax_l13: float, credits_l14: float, easement_l15: float) -> float:
    """DR 0106 line 16, verbatim: "Net tax, sum of lines 14 and 15, then subtract
    this sum from line 13. The sum of lines 14 and 15 MAY NOT EXCEED the amount
    on line 13." -- i.e. L13 - (L14 + L15), floored at 0 by the cap itself.
    """
    offset = min(float(credits_l14 or 0) + float(easement_l15 or 0), float(tax_l13))
    return round(float(tax_l13) - offset, 2)


def co_ptet_bases(owners: list) -> dict:
    """DR 0106 Part III lines 17 and 18 -- the SALT Parity (PTET) bases.

    Sec. 39-22-344(1), C.R.S.: the tax is the rate "multiplied by the sum of the
    following: (a) Each electing pass-through entity owner's pro rata or
    distributive share of the electing pass-through entity's INCOME ATTRIBUTABLE
    TO THE STATE; and (b) Each RESIDENT electing pass-through entity owner's pro
    rata or distributive share of the electing pass-through entity's INCOME NOT
    ATTRIBUTABLE TO THE STATE."
      resident    -> (a)+(b) = ENTIRE income = COLUMN A  -> line 17
      nonresident -> (a) only               = COLUMN B  -> line 18

    Two exclusions a naive spec will miss:
      - GUARANTEED PAYMENTS (K-1 line 4) -- skipped in both sums (W5);
      - any owner whose NET INCOME IS NEGATIVE -- excluded ENTIRELY, not netted.
    Plus the election's own exclusion: "any partner that is a C corporation that
    is UNITARY with the partnership" is excluded from BOTH the election's reach
    AND the tax base.
    """
    l17 = 0.0
    l18 = 0.0
    for o in owners:
        if o.get("unitary_ccorp"):
            continue                      # excluded from the election AND the base
        if co_owner_status(o) == "resident":
            amt = float(o.get("col_a", 0) or 0)
            if amt > 0:
                l17 += amt
        else:
            amt = float(o.get("col_b", 0) or 0)
            if amt > 0:
                l18 += amt
    l19 = l17 + l18
    return {"L17": round(l17, 2), "L18": round(l18, 2), "L19": round(l19, 2)}


def co_ptet_tax(owners: list, year: int = FORM_TAX_YEAR) -> float:
    """DR 0106 line 20 = line 19 x the PTET rate (Sec. 39-22-301 authority)."""
    return round(co_ptet_bases(owners)["L19"] * float(_yk(CO_PTET_RATE, year)), 2)


def co_rate(kind: str, year: int = FORM_TAX_YEAR) -> str:
    """The TWO rate constants, kept SEPARATE (W7).

    "composite" -> Sec. 39-22-104 (INDIVIDUAL rate), via Sec. 39-22-601(5.5)(d)(III)(A)/(2.7)(d)(III)(A)
    "ptet"      -> Sec. 39-22-301 (CORPORATE rate), via Sec. 39-22-344(1)

    Equal at 0.044 for TY2025. DO NOT COLLAPSE -- separate statutes, separate
    authorities, and LCS projects the values move (4.33% TY2027 / 4.29% TY2028).
    """
    if kind == "composite":
        return _yk(CO_COMPOSITE_RATE, year)
    if kind == "ptet":
        return _yk(CO_PTET_RATE, year)
    raise ValueError(f"unknown rate kind {kind!r} (expected 'composite' or 'ptet')")


# ═══════════════════════════════════════════════════════════════════════════
# PART V — receipts-factor apportionment
# ═══════════════════════════════════════════════════════════════════════════

def co_part_v(l1_modified_fti: float, receipts_co: float, receipts_everywhere: float,
              nonapportionable_total_l10f: float = 0.0,
              allocable_to_co_l13f: float = 0.0,
              all_income_apportionable: bool = False,
              no_out_of_state_activity: bool = False) -> dict:
    """DR 0106 Part V.

      L8  total receipts, each column
      L9  = L8(Colorado) / L8(Everywhere)          -- entered as a PERCENT
      L11 = L1 - L10(f)
      L12 = L9 x L11
      L14 = L12 + L13(f)

    "If a partnership or S corporation has no income from business activity
    outside Colorado, then the partnership or S corporation will source 100% of
    its income to Colorado" (Sec. 39-22-303.6(3)(a)).

    Sec. 39-22-303.6(8) election (the line 15 checkbox): "a taxpayer may elect to
    treat all income as apportionable income ... made by the extended due date of
    the tax return. Once made, the election is IRREVOCABLE for the tax year."
    Its face consequence: "If all income is being treated as apportionable
    income, enter 0 (zero) on lines 10 and 13."

    ⚠ [UNV-9]: the face prints line 9 with a bare "%" box -- NO stated decimal
    precision, NO rounding rule and NO zero-denominator rule. Unresolved; it
    moves every nonresident owner's Column B. Diagnostic D_CO106_PARTV_L9_PRECISION.

    ⚠ Part V line 14 HAS NO DESTINATION ON THE DR 0106 FACE. Nothing on the form
    consumes L12, L13(f) or L14. What Part V actually feeds is the DR 0106K:
    L8 (both columns) -> K-1 line 14, and L10/L13 -> K-1 line 15. A spec that
    wires Part V line 14 into Part II or Part III WILL BE WRONG.
    """
    if all_income_apportionable:
        nonapportionable_total_l10f = 0.0
        allocable_to_co_l13f = 0.0
    if no_out_of_state_activity:
        ratio = 1.0
    elif float(receipts_everywhere or 0) == 0:
        ratio = None                    # [UNV-9] -- undefined; diagnostic, never a silent 0
    else:
        ratio = float(receipts_co) / float(receipts_everywhere)
    l11 = float(l1_modified_fti) - float(nonapportionable_total_l10f or 0)
    l12 = None if ratio is None else round(ratio * l11, 2)
    l14 = None if l12 is None else round(l12 + float(allocable_to_co_l13f or 0), 2)
    return {"L1": float(l1_modified_fti), "L9": ratio, "L10f": float(nonapportionable_total_l10f or 0),
            "L11": round(l11, 2), "L12": l12, "L13f": float(allocable_to_co_l13f or 0), "L14": l14}


def co_sourcing_default(module: str) -> str:
    """F1 -- the load-bearing sourcing fork.

    PARTNERSHIP: DIRECT SOURCING is the DEFAULT. DR 0106 p. 3, verbatim: "the
    Colorado-source income resulting from partnership activity IS GENERALLY
    DETERMINED PURSUANT TO SECTION 39-22-109, C.R.S. (Direct Sourcing), or, AT
    THE PARTNERSHIP'S ELECTION, apportioned and allocated pursuant to section
    39-22-303.6, C.R.S." Line 11 instruction: "If the partnership is using direct
    sourcing, mark the Other box."
    S CORPORATION: MANDATORY receipts factor. "Section 39-22-321(1) and (2),
    C.R.S., requires S corporations to apportion and allocate income pursuant to
    section 39-22-303.6, C.R.S." No direct-sourcing option exists.
    """
    return "direct_sourcing" if module == M_1065 else "receipts_factor"


def co_part_v_required(module: str, owners: list, elected_receipts_factor: bool = False) -> bool:
    """Part V can be MANDATORY even when a partnership direct-sources.

    DR 0106 p. 3, verbatim: "Any partnership that has partners (such a
    C corporations) that are required to apportion and allocate income under
    section 39-22-303.6, C.R.S., MUST COMPLETE PART V ... If a partnership has
    any such partners, it must complete Part V ... REGARDLESS OF WHETHER IT
    ELECTS TO USE DIRECT SOURCING ... and checks the 'other' box on line 11."
    So `line 11 = Other` and a completed Part V can, and sometimes must, coexist.
    """
    if module == M_1120S:
        return True                       # always -- receipts factor is mandatory
    if elected_receipts_factor:
        return True
    return any(o.get("owner_kind") in ("c_corp", "partnership") for o in owners)


# ═══════════════════════════════════════════════════════════════════════════
# PART IV, due dates, penalties, estimated tax
# ═══════════════════════════════════════════════════════════════════════════

def co_part_iv(mode: str, composite_l16: float = 0.0, ptet_l20: float = 0.0,
               in_lieu_l22: float = 0.0, dr0619_repayment_l23: float = 0.0,
               payments_l25: float = 0.0, w2g_l26: float = 0.0, dr0619_credit_l27: float = 0.0,
               penalty_l29: float = 0.0, interest_l30: float = 0.0, est_penalty_l31: float = 0.0,
               credited_forward_l34: float = 0.0) -> dict:
    """DR 0106 Part IV, lines 21-35. Line 21 is the MODE JOIN: "Enter the amount
    from line 16 or line 20, whichever applies." In MODE A, line 21 = 0.
    """
    if mode == CO_MODE_B:
        l21 = round(float(composite_l16 or 0), 2)
    elif mode == CO_MODE_C:
        l21 = round(float(ptet_l20 or 0), 2)
    else:
        l21 = 0.0                                     # MODE A -- informational only
    l24 = round(l21 + float(in_lieu_l22 or 0) + float(dr0619_repayment_l23 or 0), 2)
    l28 = round(float(payments_l25 or 0) + float(w2g_l26 or 0) + float(dr0619_credit_l27 or 0), 2)
    if l24 > l28:
        l32 = round(l24 - l28 + float(penalty_l29 or 0) + float(interest_l30 or 0) + float(est_penalty_l31 or 0), 2)
        return {"L21": l21, "L24": l24, "L28": l28, "L32": l32, "L33": 0.0, "L34": 0.0, "L35": 0.0}
    l33 = round(l28 - l24, 2)
    l34 = round(min(float(credited_forward_l34 or 0), l33), 2)
    return {"L21": l21, "L24": l24, "L28": l28, "L32": 0.0,
            "L33": l33, "L34": l34, "L35": round(l33 - l34, 2)}


def co_due_dates(year: int = FORM_TAX_YEAR) -> dict:
    """The PTE due date -- 15th day of the FOURTH month. NOT the C corp's fifth.

    Sec. 39-22-608(2)(a), C.R.S., verbatim: "EXCEPT AS PROVIDED IN SUBSECTION
    (2)(b) of this section, all returns required by section 39-22-601 must be
    filed ... on or before the FIFTEENTH DAY OF THE FOURTH MONTH following the
    close of the taxable year." (2)(b) reaches only "every C corporation ...
    required by section 39-22-601 (2)". The PTE return is filed under
    Sec. 39-22-601 (5.5)(a) / (2.7)(a) -- so (2)(b) DOES NOT REACH IT.

    The verifier confirmed this against statute rather than assuming it matched
    the C-corp, and found two extra corroborations: Sec. 39-22-609(1) puts
    PAYMENT on the fourth month too, and Sec. 39-22-601(5.5)(f) reads "This
    subsection (5.5) applies to tax years beginning on and after January 1, 2024"
    -- so (5.5) is unambiguously the operative TY2025 subsection.

    Form face: April 15 / automatic six months / October 15 / NO EXTENSION TO PAY
    / weekend-or-holiday rolls to the next business day. Colorado K-1s are due on
    the same date, including extension.
    """
    return {
        "original_month": _yk(CO_DUE_MONTH, year), "original_day": _yk(CO_DUE_DAY, year),
        "calendar_year_original": "April 15",
        "extension_months": _yk(CO_EXTENSION_MONTHS, year), "calendar_year_extended": "October 15",
        "extension_to_pay": False, "extension_voucher": CO_EXTENSION_VOUCHER,
        "weekend_holiday_roll": True,
        "contrast_c_corp": "DR 0112 is the 15th day of the FIFTH month (May 15 / Nov 15 / DR 0158-C)",
    }


def co_delinquency_penalty(additional_tax: float, months_delinquent: int,
                           pct_paid_by_original_due_date: float = 1.0,
                           year: int = FORM_TAX_YEAR) -> float:
    """DR 0106 line 29, verbatim: "If 90% of the tax is not paid by the original
    due date (without extension) ... The penalty is the GREATER OF $5 OR 5% of
    the additional tax due for the FIRST month of delinquency and 0.5% for each
    additional month UP TO A MAXIMUM OF 12%."
    """
    if float(pct_paid_by_original_due_date) >= float(_yk(CO_EXTENSION_PAY_PCT, year)):
        return 0.0
    if months_delinquent <= 0 or float(additional_tax) <= 0:
        return 0.0
    pct = float(_yk(CO_PENALTY_FIRST_MONTH_PCT, year)) + \
        float(_yk(CO_PENALTY_ADDL_MONTH_PCT, year)) * (int(months_delinquent) - 1)
    pct = min(pct, float(_yk(CO_PENALTY_MAX_PCT, year)))
    return round(max(float(_yk(CO_PENALTY_MIN_DOLLARS, year)), float(additional_tax) * pct), 2)


def co_estimated_payments_required(net_tax_liability: float, year: int = FORM_TAX_YEAR) -> bool:
    """DR 0106 p. 3, verbatim: a PTE "must remit quarterly estimated payments if
    its net Colorado tax liability for the year either with a composite
    nonresident return or as a result of a SALT Parity Act Election EXCEEDS
    $5,000."

    ⚠ W9 / C9 -- LIVE 3-2 SOURCE SPLIT, not a one-sided erratum:
      "exceeds"            -> DR 0233 instructions, DR 0106EP, SALT Parity pub
      ">=" / "less than"   -> DR 0106 line 31 AND the Colorado Corporate Income
                              Tax Guide, which the DR 0106 EXPRESSLY incorporates
                              by reference for exactly this rule
    Exposure is the single point net tax == $5,000. Built STRICTLY GREATER THAN,
    because DR 0233 Part 1 computes "line 1 - $5,000; If line 2 is larger, enter
    zero and no penalty is due" -- at exactly $5,000 the Part 1 base is zero
    either way, so the form's own arithmetic is the tiebreak.
    THIS IS A KEN RULING, NOT A SETTLED CORRECTION.
    """
    threshold = _yk(CO_EST_TAX_THRESHOLD, year)
    if _yk(CO_EST_THRESHOLD_STRICTLY_GREATER, year):
        return float(net_tax_liability) > threshold
    return float(net_tax_liability) >= threshold


def co_required_annual_payment(current_year_tax: float, prior_year_tax: float,
                               prior_year_was_12_months: bool = True,
                               filed_prior_co_return: bool = True,
                               prior_3yr_income_1m_or_more: bool = False,
                               making_salt_parity_election: bool = False,
                               elected_salt_parity_prior_year: bool = True,
                               year: int = FORM_TAX_YEAR) -> float:
    """DR 0233 Part 2, verbatim: "The required annual amount to be paid is the
    LESSER OF: 1. 70% of actual net Colorado tax liability, or 2. 100% of
    preceding year's Colorado tax liability only applies if: the preceding year
    was 12-month tax year, and the partnership or S corporation filed a Colorado
    return, and the partnership or S corporation did not have taxable income of
    $1,000,000 or more for any of the three immediately preceding taxable income
    years."

    ⚠ A PTE-SPECIFIC prior-year condition the C-corp rule does NOT have.
    DR 0233 line 6, verbatim: "If you are making a SALT Parity Act election and
    DID NOT file a Colorado return making a SALT Parity Act election for the
    previous year, enter the amount from line 5 here and on line 7" -- i.e. the
    prior-year safe harbor is UNAVAILABLE to a first-year electing entity.

    ⚠ NO ANNUALIZED INCOME INSTALLMENT METHOD for PTEs (DR 0233, verbatim). The
    Corporate Guide Part 9 DOES grant it to C corporations. A genuine PTE/C-corp
    divergence -- do not inherit a C-corp estimated-tax module wholesale.
    """
    current_leg = float(current_year_tax) * float(_yk(CO_EST_REQUIRED_CURRENT_PCT, year))
    prior_available = (prior_year_was_12_months and filed_prior_co_return
                       and not prior_3yr_income_1m_or_more)
    if making_salt_parity_election and not elected_salt_parity_prior_year:
        prior_available = False           # DR 0233 line 6 -- the first-year block
    if not prior_available:
        return round(current_leg, 2)
    prior_leg = float(prior_year_tax) * float(_yk(CO_EST_REQUIRED_PRIOR_PCT, year))
    return round(min(current_leg, prior_leg), 2)


def co_estimated_interest_rate(date_year: int) -> str:
    """DR 0233 line 18, verbatim: "Underpayment on line 15 multiplied by 12% FOR
    DATES IN 2025 or multiplied by 11% FOR DATES IN 2026 multiplied by number of
    days on line 17 divided by 365 (366 for leap year)." Corroborated by the
    Corporate Guide's annual interest-rate table (2025 12%, 2026 11%).
    A split-year penalty computation uses BOTH rates.
    """
    return CO_EST_INTEREST_RATE.get(date_year, CO_EST_INTEREST_RATE[2025])


def co_cr_total(column_amounts: dict) -> float:
    """DR 0106CR line 38, verbatim: "Sum lines 5 through 37 for columns A, B, and
    C" -- NOT 1 through 37. Lines 1-4 are the recapture and other-state-tax block
    and are EXCLUDED from the total. (Verifier addition; absent from the research
    pass.)
    """
    lo, hi = CO_CR_TOTAL_RANGE
    return round(float(sum(float(column_amounts.get(str(n), 0) or 0) for n in range(lo, hi + 1))), 2)


def co_cr_columns(mode: str, column_a: float) -> dict:
    """DR 0106CR column allocation, verbatim: "Unless the partnership or
    S corporation is filing a composite return ..., enter in column B the amount
    from column A and enter 0 (zero) in column C. THIS PROCEDURE APPLIES TO ANY
    PARTNERSHIP OR S CORPORATION THAT IS NOT FILING A COMPOSITE RETURN, INCLUDING
    ANY PARTNERSHIP OR S CORPORATION MAKING AN ELECTION UNDER THE SALT PARITY ACT."

    So in MODE A and MODE C, Column C is ZERO and DR 0106 lines 14/15 are blank.
    Corroborated for Mode C by the SALT Parity pub: "The electing pass-through
    entity may not claim any refundable or nonrefundable credits on its return"
    (Sec. 39-22-344(3), C.R.S.).

    ⚠ The DR 0106CR is a MANDATORY ATTACHMENT on EVERY return -- "Every
    partnership and S corporation must submit a completed form DR 0106CR with its
    return" -- including in Modes A and C.
    """
    if mode == CO_MODE_B:
        return {"A": float(column_a), "B": None, "C": None,
                "note": "composite: Column C carries the credits applied against the composite tax"}
    return {"A": float(column_a), "B": float(column_a), "C": 0.0,
            "note": "not filing composite (Mode A or Mode C): B = A, C = 0"}


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY TOPICS / SOURCES
# ═══════════════════════════════════════════════════════════════════════════

AUTHORITY_TOPICS: list[tuple[str, str]] = [
    ("co_pte_income_tax",
     "Colorado DR 0106: ONE form, the 1065 and 1120S modules, FORKED sourcing rules; three "
     "filing modes (informational / composite / SALT Parity PTET); receipts factor vs "
     "direct sourcing; the DR 0106K owner schedule; two 4.4% rate statutes."),
    ("co_salt_parity_ptet",
     "Colorado SALT Parity Act (Sec. 39-22-340 et seq., C.R.S.): the elective entity-level PTET, "
     "its refundable owner credit, the forced full Sec. 199A add-back on every owner, and "
     "the closed TY2018-2021 retroactive election window."),
    ("co_composite_return",
     "Colorado mandatory composite nonresident return (DR 0106 Part II; Sec. 39-22-601(5.5)(d) "
     "and (2.7)(d), C.R.S.): the five exclusions, the statutory carve-outs, and the per-owner "
     "floor-at-zero reconciliation against DR 0106K line 16."),
]

# Already seeded in RS -- reuse, never re-create. The two CO conformity anchors
# come from the Tier-1 conformity seeding (_state_conformity_tier1.py); the
# federal sources carry the Schedule K / Schedule K-1 handoff this spec depends on.
EXISTING_SOURCES_TO_REFERENCE: list[str] = [
    "CO_CRS_39_22_103",          # Sec. 39-22-103(5.3) ROLLING CONFORMITY (verbatim) + the Title 39 depreciation negative
    "CO_2025_INDIV_TAX_GUIDE",   # Individual Income Tax Guide / Book 104 -- the owner-side add-back stack
    "IRS_2025_1065_INSTR",
    "IRS_2025_1120S_INSTR",
    "IRS_2025_1065_K1_INSTR",
    "IRS_2025_1120S_K1_INSTR",
    "IRS_2025_1120S_SCHL_INSTR",
]

_CO_URL = "https://tax.colorado.gov/sites/tax/files/documents/"
_CRS_URL = "https://leg.colorado.gov/sites/default/files/images/olls/crs2024-title-39.pdf"

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "CO_2025_DR0106",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "CO",
        "title": "2025 Colorado DR 0106 - Partnership and S Corporation Income Tax Return (instructions inline)",
        "citation": "Colorado DR 0106 (09/19/25), 18 pp. (instructions pp. 1-11, form face pp. 12-18)",
        "issuer": "Colorado Department of Revenue",
        "official_url": _CO_URL + "DR0106_2025.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.6,
        "topics": ["co_pte_income_tax", "co_composite_return", "co_salt_parity_ptet"],
        "excerpts": [
            {
                "excerpt_label": "Part I lines 1-11 (verified line map, rev. 09/19/25)",
                "excerpt_text": (
                    "1 Ordinary income from federal Schedule K ('Enter the ordinary income or (loss) from "
                    "line 1 of federal Schedule K (I R S form 1065)' - the instruction names ONLY the 1065; "
                    "for an S corp the source is 1120-S Sch. K line 1). 2 Sum of all other income (1065: Sch. K "
                    "lines 2, 3c, 4c, 5, 6a, 7, 8, 9a, 10 and 11; 1120-S: Sch. K lines 2, 3c, 4, 5a, 6, 7, 8a, 9 "
                    "and 10; PLUS 'any gain or loss on the sale, exchange, or other disposition of property "
                    "reported on a statement attached for line 20c of Schedule K (I R S Form 1065) or line 17d of "
                    "Schedule K (I R S Form 1120-S) for which a section 179 deduction has been passed through to "
                    "partners or shareholders'). 3 Business meals deducted pursuant to section 274(k) (from Col. A "
                    "line 10 of the DR 0106Ks). 4 Other modifications increasing federal income (Col. A lines 9 and "
                    "11 of the DR 0106Ks). 5 Sum of lines 1 through 4. 6 Allowable deductions from federal Schedule "
                    "K (instruction GOVERNS: 'Enter the total federal deductions reported on line 12 of the Colorado "
                    "K-1s (DR 0106K) ... Enter the deductions on this line 6 as a positive number'). 7 Colorado "
                    "Marijuana and Natural Medicine Business Deduction ('Enter the subtraction on this line 7 as a "
                    "positive number'). 8 Other modifications decreasing federal income ('the total subtractions "
                    "reported on line 13 of the Colorado K-1s ... as a positive number'). 9 Sum of lines 6 through 8. "
                    "10 Modified federal taxable income, subtract line 9 from line 5. 11 Apportionment and allocation "
                    "method: Part V / Other (include explanation) / Income is all Colorado Income."
                ),
                "summary_text": "Part I L1-L11. THE SIGN FLIP: K-1 Col.A L12/L13 are NEGATIVE; DR 0106 L6/L7/L8 are POSITIVE and then SUBTRACTED at L9/L10. L3 and L4 are already positive and are NOT inverted.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Part II composite (L12-L16) + the five exclusions",
                "excerpt_text": (
                    "'Every partnership and S corporation that is required to file form DR 0106 that does not make "
                    "an election under the SALT Parity Act must file a composite return (Part II of form DR 0106) and "
                    "make a composite payment of tax on behalf of all of its nonresident partners or shareholders, "
                    "except for the following: Any Colorado resident partner or shareholder, including partners and "
                    "shareholders that are residents of Colorado for only part of the tax year; Any nonresident "
                    "partner that is a corporation or a partnership; Any nonresident partner or shareholder that is "
                    "exempt from Colorado income tax under section 39-22-112(1), C.R.S.; and Any nonresident partner "
                    "or shareholder that timely files a Nonresident Partner or Shareholder Agreement (form DR 0107).' "
                    "PLUS a fifth, from the line 12 instruction: 'Partners or shareholders whose net Colorado-source "
                    "income is negative'. L12 'should equal the sum of the amounts on lines 1 through 3 and lines 5 "
                    "through 13 in column B of the Colorado K-1'. L13 'Tax; 4.4% of the amount on line 12' and 'the "
                    "amount reported on line 13 of form DR 0106 must equal the sum of the amounts reported on line 16 "
                    "of the Colorado K-1s of all nonresident partners or shareholders included in the composite "
                    "return.' L16 'Net tax, sum of lines 14 and 15, then subtract this sum from line 13. The sum of "
                    "lines 14 and 15 may not exceed the amount on line 13.'"
                ),
                "summary_text": "Composite is MANDATORY absent a SALT Parity election; five exclusions incl. negative-income owners; L13 must equal the sum of K-1 L16.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Part III SALT Parity (L17-L20) + Part IV mode join (L21) mutual exclusivity",
                "excerpt_text": (
                    "17 Resident partners' or shareholders' total share of income ('the total of all resident "
                    "partners' or shareholders' income, excluding any resident partner whose net income from the "
                    "partnership is negative ... should equal the sum of the amounts on lines 1 through 3 and lines 5 "
                    "through 13 in column A'). 18 Colorado-source income of nonresident partners or shareholders "
                    "(same sums in column B). 19 Colorado taxable income, sum of lines 17 and 18. 20 Net Tax; 4.4% of "
                    "the amount on line 19. 21 'Enter the amount from line 16 or line 20, whichever applies' - "
                    "'Part II and Part III should not both be completed, as a partnership or S corporation may file a "
                    "composite return (by completing Part II) or make a SALT Parity Act election (and complete Part "
                    "III), but it may not do both.' Reinforced twice more on the face ('Do not complete lines 12-16 "
                    "unless you are filing a composite nonresident return' / 'If you completed lines 12-16, then skip "
                    "Part III') and at Box I ('Complete Part III of this return. Do not complete Part II')."
                ),
                "summary_text": "Part III PTET base = residents' Col.A + nonresidents' Col.B, negative owners excluded entirely; Parts II and III MUTUALLY EXCLUSIVE.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Boxes A-I; Box A is LEGAL FORM, not tax classification",
                "excerpt_text": (
                    "'A. This return is being filed for (mark one): Partnership / S Corporation / LLC / LP / LLP / "
                    "LLLP / Association / Non-Profit'. Instruction: 'Mark the box that represents the TRUE LEGAL FORM "
                    "of the partnership or S corporation filing this return.' Six of the eight options are silent on "
                    "1065-vs-1120S. Reinforced at p. 1: 'any limited liability company classified as a partnership "
                    "for federal income tax purposes' is treated as a partnership - classification follows the FEDERAL "
                    "RETURN. B/C Beginning/Ending depreciable assets from federal return ('net of any accumulated "
                    "depreciation. Refer to line 10b (columns (b) and (d)) of Schedule L of I R S form 1120-S or line "
                    "9b (columns (b) and (d)) of Schedule L of I R S form 1065'). D Business or profession. E Date of "
                    "organization or incorporation. F Final return. G Federal changes in the last four years. "
                    "H Number of partners or shareholders AS OF YEAR END. I SALT Parity Act election ('Mark this box I "
                    "if the partnership or S corporation previously filed an election on form DR 1705 or DR 0106EP')."
                ),
                "summary_text": "Box A is LEGAL form - the module fork must key off the attached federal return (W2). Boxes B/C are a balance-sheet transcription, not a tax computation.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Due date (4th month) + Part V + apportionment fork",
                "excerpt_text": (
                    "'You must file this return and pay any amount owed by the FIFTEENTH DAY OF THE FOURTH MONTH "
                    "after the close of the tax year, which is April 15 for calendar year filers. For filing your "
                    "return there is an AUTOMATIC EXTENSION OF SIX MONTHS, or until October 15 for calendar year "
                    "filers. However, NO EXTENSION IS AVAILABLE FOR PAYMENT. To make an extension payment before "
                    "filing, see form DR 0158-N ... If the due date falls on a weekend or legal holiday, return will "
                    "be due the next business day.' Apportionment: 'For partners who are nonresident individuals, "
                    "nonresident estates, or nonresident trusts, the Colorado-source income resulting from partnership "
                    "activity is generally determined pursuant to section 39-22-109, C.R.S. (Direct Sourcing), or, at "
                    "the partnership's election, apportioned and allocated pursuant to section 39-22-303.6, C.R.S.' vs "
                    "'Section 39-22-321(1) and (2), C.R.S., requires S corporations to apportion and allocate income "
                    "pursuant to section 39-22-303.6, C.R.S.' Part V line 9 = 'Line 8 (Colorado) divided by line 8 "
                    "(Everywhere)' as a percent; line 15 is the Sec. 39-22-303.6(8) all-apportionable election."
                ),
                "summary_text": "PTE due date is the 4th month (April 15 / Oct 15 / DR 0158-N / no extension to pay) - NOT the C corp's 5th. Partnership direct-sourcing default vs S-corp mandatory receipts factor.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "CO_2025_DR0106K_I",
        "source_type": "state_instruction",
        "source_rank": "primary_official",
        "jurisdiction_code": "CO",
        "title": "2025 Colorado DR 0106K-I - Partnership AND S Corporation Instructions for Colorado K-1",
        "citation": "Colorado DR 0106K-I (09/18/25), 18 pp. (pp. 1-9 partnership, pp. 10-18 S corporation)",
        "issuer": "Colorado Department of Revenue",
        "official_url": _CO_URL + "DR0106K-I_2025.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.6,
        "topics": ["co_pte_income_tax", "co_composite_return", "co_salt_parity_ptet"],
        "excerpts": [
            {
                "excerpt_label": "THE FORK DOCUMENT - two instruction sets in one PDF",
                "excerpt_text": (
                    "ONE PDF, 18 pp., rev. DR 0106K-I (09/18/25). pp. 1-9 = 'Partnership Instructions for Colorado "
                    "K-1 (DR 0106K)'; pp. 10-18 = the S corporation instructions. EACH HALF carries its own federal "
                    "K-1 box map, its own Column B rule, its own line-9 split, its own line-11 and line-13 "
                    "inventories, and its own line-16 computation. This is where the two-module fork actually lives. "
                    "The adversarial pass found FOUR FURTHER FORKS inside it (F13-F16) beyond the twelve the research "
                    "pass catalogued - the characteristic failure mode being to FLATTEN THE TWO HALVES INTO ONE."
                ),
                "summary_text": "The DR 0106K-I carries TWO instruction sets. 16 forks total, four of them (F13-F16) living inside this document alone.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "THE SIGN FLIP source - K-1 negatives (both halves, verbatim)",
                "excerpt_text": (
                    "'Enter any losses on lines 1, 2, 3, or 8, and any federal deductions on LINE 12, AS NEGATIVE "
                    "AMOUNTS' and 'Enter subtractions on LINE 13 AS A NEGATIVE AMOUNT'. Both statements appear in "
                    "BOTH halves. Against the DR 0106's 'Enter the deductions on this line 6 as a positive number' / "
                    "'Enter the deductions on this line 8 as a positive number', this means aggregating K-1 Column A "
                    "line 12 into DR 0106 line 6, and line 13 into line 8, REQUIRES A SIGN INVERSION. The K-1 "
                    "ADDITIONS on lines 9, 10 and 11 are already POSITIVE and feed DR 0106 lines 3 and 4 WITHOUT "
                    "inversion."
                ),
                "summary_text": "K-1 L12/L13 negative -> DR 0106 L6/L8 positive (INVERT). K-1 L9/L10/L11 positive -> DR 0106 L3/L4 (DO NOT invert).",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "F7 - the state income tax add-back split (both halves, verbatim)",
                "excerpt_text": (
                    "PARTNERSHIP: 'For all partners that are NOT C CORPORATIONS, enter on line 9 in Column A the "
                    "partner's distributive share of any state income tax that was ... deducted by the partnership on "
                    "line 14 of I R S Form 1065 ... Report on line 9 the partner's distributive share of ALL deducted "
                    "state income taxes, REGARDLESS OF THE STATE to which the income tax was paid or accrued.' / 'For "
                    "all partners that are C CORPORATIONS, enter on line 9 in Column A the partner's distributive "
                    "share of any COLORADO income tax...'. S CORPORATION: 'For all RESIDENT shareholders ... ALL "
                    "deducted state income taxes ... For all NONRESIDENT shareholders ... any COLORADO income tax...'. "
                    "BOTH: Column B is Colorado income tax only; the add-back also picks up line 9 of a Colorado K-1 "
                    "issued to the entity by a LOWER-TIER partnership (tier-chain accumulation)."
                ),
                "summary_text": "F7: partnership splits by PARTNER TYPE (C-corp -> CO only); S corp splits by RESIDENCY (nonresident -> CO only). Column B is CO-only in both.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "F15/F16 - the line 11 and line 13 inventories DIFFER (verifier C7/C8, HIGH)",
                "excerpt_text": (
                    "LINE 11 'Other Colorado additions', BOTH: non-Colorado state or local bond interest ('does not "
                    "include any amortization of the bond premium and is reduced by the amount of the deductions "
                    "required by the Internal Revenue Code to be allocated to the interest income'); unauthorized-alien "
                    "labor expenses (Sec. 39-22-529); discriminatory-club expenses (Sec. 44-3-418); lower-tier line-11 "
                    "amounts. S CORPORATION ONLY, verbatim: 'Any income, war profits, or excess profits taxes paid or "
                    "accrued to any foreign country or to any possession of the United States deducted by the S "
                    "corporation on line 12 of I R S Form 1120-S for the tax year' - NO PARTNERSHIP ANALOGUE. "
                    "LINE 13 'Colorado subtractions', BOTH: U.S. government obligation interest; Colorado Marijuana "
                    "Code Sec. 280E expenditures; Colorado Natural Medicine Code Sec. 280E expenditures; state income "
                    "tax refunds not previously deducted; lower-tier line-13 amounts. PARTNERSHIP ONLY: export-taxpayer "
                    "foreign source income (Sec. 39-22-206). S CORPORATION ONLY: 'Any portion of wages or salaries paid "
                    "or incurred by the S corporation for the tax year, but which are not deductible for federal income "
                    "tax purposes due to SECTION 280C of the Internal Revenue Code' (own Column B rule: 'to the extent "
                    "the underlying or related expenses or losses are from business activity in Colorado')."
                ),
                "summary_text": "F15/F16: the S-corp half adds a FOREIGN-TAX ADDITION and a Sec. 280C SUBTRACTION; the partnership half alone has the Sec. 39-22-206 export-taxpayer subtraction. Substantive modification items, not wording.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "F13/F14 + line 16 per-owner floor + residency tests",
                "excerpt_text": (
                    "LINE 16 SUMMATION WORDING - PARTNERSHIP half, all three variants: 'Sum the amounts on LINES 1 "
                    "THROUGH 3 AND LINES 5 THROUGH 13'; S CORPORATION half, all three variants: 'Sum the amounts on "
                    "LINES 1 THROUGH 13'. Arithmetically identical (line 4 is N/A for an S corp). Composite: '...in "
                    "Column B, multiply the sum by 4.4% (0.044), and enter the result on line 16. IF THE SUM ... IS A "
                    "NEGATIVE AMOUNT, ENTER 0 (ZERO).' SALT Parity resident (INCLUDING A PART-YEAR RESIDENT): same sums "
                    "in Column A x 4.4%, floored at 0. SALT Parity nonresident: Column B x 4.4%, floored at 0. 'Do not "
                    "enter on line 16 any amount that the partnership has not remitted to the Department.' "
                    "LINES 14/15 - PARTNERSHIP: 'must be completed for any partner that is a C corporation or that is "
                    "treated as a C corporation ... but is not required for any other partner'; S CORP: 'The completion "
                    "of lines 14 and 15 is NOT REQUIRED on a Colorado K-1 prepared for ANY S corporation shareholder, "
                    "unless the shareholder needs the information'. RESIDENCY: individual - domiciled in Colorado, or "
                    "maintains a permanent place of abode in Colorado and spends more than six months of the year in "
                    "Colorado; estate - 'administered in Colorado in a proceeding other than an ancillary proceeding'; "
                    "trust - 'administered in Colorado'; C corporation / partnership partner - resident 'if it is "
                    "organized under Colorado law'. PART-YEAR RESIDENTS ARE TREATED AS RESIDENTS."
                ),
                "summary_text": "F13 wording fork; F14 lines 14/15 never mandatory for an S corp; K-1 L16 floored at zero in all three variants; part-year owners treated as residents.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "F2/F3 Column B rules + the two known errata [UNV-4]",
                "excerpt_text": (
                    "F2 - PARTNERSHIP: 'If the partnership has not made a SALT Parity Act election, LEAVE THESE LINES "
                    "IN COLUMN B BLANK for all partners that are corporations or partnerships.' S CORP: 'Complete "
                    "lines 1 through 13 in Column B for EACH nonresident shareholder.' F3 - guaranteed payments, "
                    "partnership line 4 Column B: 'the portion of the nonresident partner's guaranteed payments from "
                    "Column A that is derived from sources within Colorado as determined pursuant to 1 C C R 201-2, "
                    "RULE 39-22-109(3)(b)(xii)' - NO formulary alternative is offered, in contrast to the very next "
                    "paragraph (lines 1-3, 5-8, 12) which explicitly offers 'or, at the partnership's election, "
                    "apportioned or allocated to Colorado pursuant to section 39-22-303.6'. ERRATA, both CONFIRMED "
                    "VERBATIM and NOT to be 'fixed' back: (a) S-corp half line 9 Column A says 'deducted by the S "
                    "corporation on line 12 of I R S FORM 1065' TWICE, while the Column B paragraph below each "
                    "correctly reads 'line 12 of I R S Form 1120-S' - BUILD TO 1120-S LINE 12; (b) partnership half "
                    "line 10 Column A says 'any federal business deduction claimed by the S CORPORATION' - BUILD TO "
                    "'the partnership'. The partnership Column B rule also cites General Information Letter 22-003 by "
                    "name (a GIL is expressly NON-BINDING on the Department - guidance, not authority)."
                ),
                "summary_text": "F2 Column B blank for partnership entity owners absent an election; F3 guaranteed payments ALWAYS direct-sourced; two confirmed instruction errata to build around, not to.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "K-1 transmittal is a SEPARATE submission (W8)",
                "excerpt_text": (
                    "'Do not submit the copies of the Colorado K-1s issued to partners or shareholders (or the DR 1706 "
                    "transmittal form) AS AN ATTACHMENT to a paper income tax return (form DR 0106, OR AS A PDF "
                    "ATTACHMENT TO AN MeF INCOME TAX RETURN), filed for the partnership or S corporation.' Five "
                    "accepted channels: MeF (K-1s carried inside the return submission), XLS upload to Revenue Online, "
                    "XML upload to Revenue Online, manual entry in Revenue Online, or paper with the DR 1706 cover "
                    "sheet. 'The DR 1706 is not needed if you are filing the DR 0106Ks electronically.' Electronic "
                    "submission requires a web-submitter registration with CDOR. Due date: 'Colorado K-1s are due to be "
                    "filed the fifteenth day of the fourth month after the close of the tax year, or after the "
                    "automatic six-month extension, if applicable. Colorado K-1s for calendar year 2025 are due on "
                    "April 15, 2026.' Owners must be furnished their copies on or before the date the K-1s are filed."
                ),
                "summary_text": "Colorado K-1s are transmitted SEPARATELY - never as an attachment to the return, paper or MeF PDF. Five channels; same due date as the return.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "CO_2025_DR0106K",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "CO",
        "title": "2025 Colorado DR 0106K - Colorado K-1 (owner schedule)",
        "citation": "Colorado DR 0106K (07/18/25), 3 pp.",
        "issuer": "Colorado Department of Revenue",
        "official_url": _CO_URL + "DR0106K_2025.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["co_pte_income_tax"],
        "excerpts": [
            {
                "excerpt_label": "DR 0106K face - two columns, six owner-status checkboxes, lines 1-16",
                "excerpt_text": (
                    "Two columns throughout: 'A. Share of Income and Other items' and 'B. Share of Income and Other "
                    "Items Attributable to Colorado'. Owner-status checkboxes (these drive everything): Resident / "
                    "Non-Resident / Composite / DR 0107 / Excluded Nonresident / SALT Parity Election. Lines: "
                    "1 Ordinary business income (loss); 2 Net rental real estate income (loss); 3 Other net rental "
                    "income (loss); 4 Total guaranteed payments; 5 Interest and dividends; 6 Royalties; 7 Net capital "
                    "gain; 8 Other income (loss); 9 State income tax addback; 10 Business meals deducted pursuant to "
                    "section 274(k) of the Internal Revenue Code; 11 Other Colorado additions; 12 Federal deductions; "
                    "13 Colorado subtractions; 14 Partner's share of total receipts from line 8 of the DR 0106, part "
                    "V; 15 Partner's share of non-apportionable income from the DR 0106, part V; 16 Partner's or "
                    "shareholder's share of tax paid with composite return or SALT Parity election (SINGLE COLUMN). "
                    "Credit lines 17-48 (single column, 'Remaining Amount (excluding any credit applied towards "
                    "composite tax)'), including line 25 'SALT Parity credit from lower-tier partnership'."
                ),
                "summary_text": "DR 0106K Col A/B layout, the six status checkboxes, lines 1-16 and the 17-48 credit menu incl. L25 lower-tier SALT Parity pass-through.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "CO_CRS_39_22_601",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "CO",
        "title": "C.R.S. Sec. 39-22-601(2.7) and (5.5) - PTE returns, mandatory composite return, carve-outs",
        "citation": "C.R.S. Sec. 39-22-601(2.7)(d) and (5.5)(d) (CRS 2024, Title 39)",
        "issuer": "Colorado General Assembly, Office of Legislative Legal Services",
        "official_url": _CRS_URL,
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["co_composite_return"],
        "excerpts": [
            {
                "excerpt_label": "Composite return MANDATORY + the composite rate cross-reference",
                "excerpt_text": (
                    "Sec. 39-22-601(5.5)(d)(I): 'Except as otherwise provided in this subsection (5.5)(d), every "
                    "partnership required to file a return under subsection (5.5)(a) of this section SHALL ALSO FILE A "
                    "COMPOSITE RETURN AND MAKE A COMPOSITE PAYMENT OF TAX on behalf of all of its nonresident "
                    "partners.' Identical language at (2.7)(d)(I) for S corporations. (5.5)(d)(III)(A): 'The amount of "
                    "the composite payment is the aggregate income derived from sources in the state multiplied by THE "
                    "HIGHEST MARGINAL TAX RATE IN EFFECT UNDER SECTION 39-22-104.' (identical at (2.7)(d)(III)(A)). "
                    "Same subsection: 'If the income computed for any nonresident partner is a negative amount, that "
                    "nonresident partner's income is EXCLUDED from the calculation of aggregate income' - the fifth "
                    "exclusion is STATUTORY, not merely an instruction. (5.5)(d)(V): the entity 'is entitled to recover "
                    "from each nonresident partner that nonresident partner's share of the composite payment ... "
                    "including any penalty or interest'. (5.5)(f): 'This subsection (5.5) applies to tax years "
                    "beginning on and after January 1, 2024.'"
                ),
                "summary_text": "Composite is MANDATORY; its rate cites Sec. 39-22-104 (the INDIVIDUAL rate); the negative-income exclusion is statutory.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "The carve-outs (5.5)(d)(VII) AND (2.7)(d)(VII) - verifier C1/C2",
                "excerpt_text": (
                    "Sec. 39-22-601(5.5)(d)(VII), verbatim IN FULL: 'This subsection (5.5)(d) does not apply to: (A) A "
                    "partnership that makes the election allowed under subpart 3 of part 3 of this article 22; (B) A "
                    "publicly traded partnership, as defined in section 7704 (b) of the internal revenue code, that "
                    "meets any of the exceptions under section 7704 (c) of the internal revenue code AND IS NOT TREATED "
                    "AS A CORPORATION UNDER SECTION 7704 (a) OF THE INTERNAL REVENUE CODE; and (C) A partnership "
                    "consisting only of partners described in subsection (5.5)(d)(II) of this section.' "
                    "Sec. 39-22-601(2.7)(d)(VII), verbatim: 'This subsection (2.7)(d) does not apply to: (A) An S "
                    "corporation that makes the election allowed under subpart 3 of part 3 of this article 22; or (B) "
                    "AN S CORPORATION CONSISTING ONLY OF SHAREHOLDERS DESCRIBED IN SUBSECTION (2.7)(d)(II) of this "
                    "section.' So the ALL-OWNERS-ALREADY-EXCLUDED carve-out is SHARED BY BOTH MODULES; only the "
                    "publicly-traded-partnership carve-out is partnership-only. NEITHER carve-out appears anywhere in "
                    "the DR 0106 instructions."
                ),
                "summary_text": "C1: the S-corp all-owners-excluded carve-out EXISTS ((2.7)(d)(VII)(B)). C2: the PTP test has THREE conditions incl. 'not treated as a corporation under section 7704(a)'.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "CO_CRS_39_22_344",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "CO",
        "title": "C.R.S. Sec. 39-22-344 - SALT Parity Act imposition, base, and the Sec. 39-22-301 rate cross-reference",
        "citation": "C.R.S. Sec. 39-22-344 (CRS 2024, Title 39)",
        "issuer": "Colorado General Assembly, Office of Legislative Legal Services",
        "official_url": _CRS_URL,
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["co_salt_parity_ptet"],
        "excerpts": [
            {
                "excerpt_label": "PTET imposition, the base, and the CORPORATE rate cross-reference",
                "excerpt_text": (
                    "Sec. 39-22-344(1): 'an electing pass-through entity is subject to a tax in an amount equal to THE "
                    "TAX RATE SET FORTH IN SECTION 39-22-301 for the applicable income tax year' multiplied by the sum "
                    "of: '(a) Each electing pass-through entity owner's pro rata or distributive share of the electing "
                    "pass-through entity's INCOME ATTRIBUTABLE TO THE STATE; and (b) Each RESIDENT electing pass-through "
                    "entity owner's pro rata or distributive share of the electing pass-through entity's INCOME NOT "
                    "ATTRIBUTABLE TO THE STATE.' For a resident, (a)+(b) = entire income = Column A (line 17); for a "
                    "nonresident, (a) only = Column B (line 18). Sec. 39-22-344(2) treats an electing PTE as a "
                    "corporation under Sec. 39-22-606 for estimated-payment purposes. Sec. 39-22-344(3): no credits on "
                    "the electing entity's own return. Sec. 39-22-344(5): 'The provisions of section 39-22-601 (2.7)(d) "
                    "and (5.5)(d) are not applicable to an electing pass-through entity' - the statutory basis for the "
                    "Part II / Part III mutual exclusivity."
                ),
                "summary_text": "PTET rate cites Sec. 39-22-301 (the CORPORATE rate) - a DIFFERENT statute from the composite rate. Base maps exactly onto lines 17/18. Sec. 39-22-344(5) is the mutual-exclusivity basis.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "CO_CRS_39_22_301_RATE",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "CO",
        "title": "C.R.S. Sec. 39-22-301(1)(d)(I)(K) - the CORPORATE rate (4.4%), which the PTET points at",
        "citation": "C.R.S. Sec. 39-22-301(1)(d)(I)(K) (CRS 2024, Title 39)",
        "issuer": "Colorado General Assembly, Office of Legislative Legal Services",
        "official_url": _CRS_URL,
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["co_salt_parity_ptet"],
        "excerpts": [
            {
                "excerpt_label": "The corporate rate, verbatim",
                "excerpt_text": (
                    "Sec. 39-22-301(1)(d)(I)(K), C.R.S., verbatim: 'Except as otherwise provided in section 39-22-627, "
                    "for income tax years commencing on or after January 1, 2022, FOUR AND FORTY ONE-HUNDREDTHS "
                    "PERCENT of the Colorado net income.' This is the rate the SALT Parity Act (Sec. 39-22-344(1)) "
                    "points at for DR 0106 line 20. It is a DIFFERENT statute from Sec. 39-22-104, which the composite "
                    "return points at for line 13. For TY2025 both read 4.4%, so the two lines are numerically "
                    "identical THIS YEAR. Sec. 39-22-627 (the TABOR refund mechanism) moves both together today, but "
                    "they remain separate constants with separate authorities. TY2024 was reduced to 4.25% by a "
                    "ONE-OFF DIRECTIVE at Sec. 39-22-627(1)(c) naming TY2024 specifically; the general mechanism was "
                    "NOT triggered for TY2025 (Legislative Council Staff, September 2025 forecast: the mechanism 'will "
                    "not be triggered in tax years 2025 or 2026', against a Controller-certified $293.3M obligation vs "
                    "the $300M first step). LCS projects 4.33% for TY2027 and 4.29% for TY2028."
                ),
                "summary_text": "Sec. 39-22-301 = 4.4% corporate rate = the PTET rate (line 20). Separate from Sec. 39-22-104 (composite, line 13). Key to the tax year - LCS projects the value moves in TY2027/TY2028.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "CO_CRS_39_22_104_RATE",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "CO",
        "title": "C.R.S. Sec. 39-22-104 - the INDIVIDUAL rate, which the composite return points at",
        "citation": "C.R.S. Sec. 39-22-104 (CRS 2024, Title 39), via Sec. 39-22-601(5.5)(d)(III)(A) / (2.7)(d)(III)(A)",
        "issuer": "Colorado General Assembly, Office of Legislative Legal Services",
        "official_url": _CRS_URL,
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.4,
        "topics": ["co_composite_return"],
        "excerpts": [
            {
                "excerpt_label": "The composite rate cross-reference - the INDIVIDUAL rate statute",
                "excerpt_text": (
                    "The composite payment is measured by 'THE HIGHEST MARGINAL TAX RATE IN EFFECT UNDER SECTION "
                    "39-22-104' (Sec. 39-22-601(5.5)(d)(III)(A), and identically at (2.7)(d)(III)(A) for S "
                    "corporations). Sec. 39-22-104 is the INDIVIDUAL income tax rate statute - NOT Sec. 39-22-301, "
                    "which is what the PTET points at. Colorado's individual rate is FLAT (no brackets): 4.4% for "
                    "TY2025, confirmed on the DR 0106 face at line 13 ('Tax; 4.4% of the amount on line 12') and "
                    "three times in the DR 0106K-I line-16 instruction ('multiply the sum by 4.4% (0.044)'). "
                    "Sec. 39-22-627 lets the executive director temporarily reduce the rate as a TABOR refund "
                    "mechanism, moving BOTH Sec. 39-22-104(1.7) and Sec. 39-22-301(1)(d)(I) together - which is "
                    "exactly why the two must be encoded as two tax-year-keyed constants rather than one."
                ),
                "summary_text": "Sec. 39-22-104 = the individual rate = the COMPOSITE rate (line 13). 4.4% TY2025. Separate authority from the PTET rate.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "CO_CRS_39_22_608_DUE",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "CO",
        "title": "C.R.S. Sec. 39-22-608(2) - return due dates; the PTE is the 4th month, not the C corp's 5th",
        "citation": "C.R.S. Sec. 39-22-608(2) (CRS 2024, Title 39)",
        "issuer": "Colorado General Assembly, Office of Legislative Legal Services",
        "official_url": _CRS_URL,
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["co_pte_income_tax"],
        "excerpts": [
            {
                "excerpt_label": "The due-date split, verbatim",
                "excerpt_text": (
                    "Sec. 39-22-608(2), C.R.S., verbatim: '(a) EXCEPT AS PROVIDED IN SUBSECTION (2)(b) of this "
                    "section, all returns required by section 39-22-601 must be filed ... on or before the FIFTEENTH "
                    "DAY OF THE FOURTH MONTH following the close of the taxable year. (b) For taxable years beginning "
                    "on and after January 1, 2024, EVERY C CORPORATION ... shall file the return required by section "
                    "39-22-601 (2) ... on or before the FIFTEENTH DAY OF THE FIFTH MONTH ...' The partnership / S-corp "
                    "return is filed under Sec. 39-22-601 (5.5)(a) and (2.7)(a), NOT (2) - so (2)(b) DOES NOT REACH "
                    "IT. Two further corroborations: Sec. 39-22-609(1) puts PAYMENT on the fourth month as well, and "
                    "Sec. 39-22-601(5.5)(f) confirms (5.5) is the operative TY2025 subsection. This was verified "
                    "against statute rather than assumed to match the C corporation, whose DR 0112 really is a month "
                    "later on both ends (May 15 / November 15 / DR 0158-C)."
                ),
                "summary_text": "PTE = 15th day of the 4th month (April 15), automatic 6-month extension (Oct 15), no extension to pay. The C corp's 5th-month rule does NOT reach the DR 0106.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "CO_CRS_39_22_343_ELECT",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "CO",
        "title": "C.R.S. Sec. 39-22-343 - the SALT Parity election, its gating condition, and the CLOSED retroactive window",
        "citation": "C.R.S. Sec. 39-22-343 (CRS 2024, Title 39)",
        "issuer": "Colorado General Assembly, Office of Legislative Legal Services",
        "official_url": _CRS_URL,
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["co_salt_parity_ptet"],
        "excerpts": [
            {
                "excerpt_label": "Election mechanics, the Sec. 164 gating condition, and the closed window",
                "excerpt_text": (
                    "Sec. 39-22-343(1)(a)-(b): the election is ELECTIVE, ANNUAL, IRREVOCABLE for the year, and BINDING "
                    "ON ALL OWNERS. Sec. 39-22-343(2), verbatim: 'The election allowed under subsection (1) of this "
                    "section is ONLY ALLOWED IN AN INCOME TAX YEAR WHERE THERE IS A LIMITATION ON THE DEDUCTIONS "
                    "ALLOWED TO INDIVIDUALS UNDER SECTION 164 of the internal revenue code.' - a LIVE CHECK, not a "
                    "constant: if the federal SALT cap ever lapses, the election lapses with it. CDOR treats the "
                    "election as AVAILABLE FOR TY2025 (the TY2025 DR 0106 carries box I, the TY2025 DR 1705 exists and "
                    "says 'irrevocable for tax year 2025', and the SALT Parity publication was reissued October 2025). "
                    "Sec. 39-22-343(1)(c)(I), verbatim: 'For income tax years commencing on or after January 1, 2018, "
                    "but prior to January 1, 2022, the S corporation or partnership MUST MAKE THE ELECTION ON OR AFTER "
                    "SEPTEMBER 1, 2023, BUT BEFORE JULY 1, 2024, in a composite amended tax return for all of the years "
                    "for which the election is made...' The window expired 2024-06-30. NO TY2018-2021 RETROACTIVE PATH "
                    "MAY BE BUILT."
                ),
                "summary_text": "Election is elective/annual/irrevocable/binding; gated on a federal Sec. 164 limitation existing; the TY2018-2021 retroactive window CLOSED 2024-06-30.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "CO_CRS_39_22_347_CREDIT",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "CO",
        "title": "C.R.S. Sec. 39-22-347 - the REFUNDABLE owner credit for PTET paid",
        "citation": "C.R.S. Sec. 39-22-347(2)-(4) (CRS 2024, Title 39)",
        "issuer": "Colorado General Assembly, Office of Legislative Legal Services",
        "official_url": _CRS_URL,
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["co_salt_parity_ptet"],
        "excerpts": [
            {
                "excerpt_label": "The credit is REFUNDABLE, and is conditioned on actual remittance",
                "excerpt_text": (
                    "Sec. 39-22-347(2): 'an electing pass-through entity owner is allowed a credit against the tax "
                    "imposed by this article 22 that is an amount equal to the share of the tax imposed pursuant to "
                    "section 39-22-344 (1) on the electing pass-through entity with respect to the electing "
                    "pass-through entity owner's income'. Sec. 39-22-347(4): 'ANY AMOUNT OF THE CREDIT ALLOWED BY THIS "
                    "SECTION THAT EXCEEDS THE ELECTING PASS-THROUGH ENTITY OWNER'S INCOME TAXES DUE IS REFUNDED to the "
                    "electing pass-through entity owner.' Sec. 39-22-347(3): 'No credit is allowed ... unless the "
                    "electing pass-through entity PAID the tax ... and PROVIDED SUFFICIENT INFORMATION on the electing "
                    "pass-through entity tax return ... to identify that electing pass-through entity owner.' Mirrored "
                    "on the form by the DR 0106K-I: 'Do not enter on line 16 any amount that the partnership has not "
                    "remitted to the Department.' The plumbing: DR 0106 line 20 -> allocated per owner -> DR 0106K "
                    "line 16 -> DR 0104CR PART I (REFUNDABLE CREDITS) LINE 11 -> refunded if it exceeds the owner's "
                    "Colorado tax. NOTE DR 0104CR Part I line 11 is the SAME LINE for the composite payment and the "
                    "PTET credit - the individual return does not distinguish them."
                ),
                "summary_text": "Owner credit is REFUNDABLE (Sec. 39-22-347(4)), lands on DR 0104CR Part I line 11, and is barred unless the entity actually remitted.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "CO_ITT_SALT_PARITY_2025",
        "source_type": "state_instruction",
        "source_rank": "primary_official",
        "jurisdiction_code": "CO",
        "title": "Colorado Income Tax Topics: SALT Parity Act (Revised October 2025)",
        "citation": "CDOR Income Tax Topics: SALT Parity Act, Rev. October 2025, 5 pp.",
        "issuer": "Colorado Department of Revenue",
        "official_url": _CO_URL + "ITT_SALT_Parity_Act_Oct_2025.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.2,
        "topics": ["co_salt_parity_ptet"],
        "excerpts": [
            {
                "excerpt_label": "The forced full Sec. 199A add-back on EVERY owner",
                "excerpt_text": (
                    "'If a partnership or S corporation makes the SALT Parity Act election, ALL of its partners or "
                    "shareholders must add back to federal taxable income on their Colorado return any qualified "
                    "business deduction claimed under section 199A of the Internal Revenue Code on their federal "
                    "return. THE ADDBACK IS REQUIRED FOR THE FULL AMOUNT of the qualified business deduction claimed by "
                    "the electing pass-through entity owner on their federal return.' The DR 0106 p. 2 repeats it. "
                    "Book 104's line-3 instruction: 'You must add back the entire deduction REGARDLESS OF YOUR "
                    "ADJUSTED GROSS INCOME. This addback is NOT LIMITED to the deduction taken with respect to the "
                    "electing partnership.' So BOTH of Colorado's ordinary AGI thresholds ($500,000 / $1,000,000 "
                    "joint) are SWITCHED OFF by the election, for EVERY owner. Landing point: DR 0104 line 3 "
                    "'Qualified Business Income Deduction Addback'. Separately: 'Partners and shareholders must make "
                    "an addition on their Colorado income tax returns for their distributive share of state income "
                    "deducted tax by the partnership or S corporation on its federal return' [sic - word order is the "
                    "DOR's] -> DR 0106K line 9 -> DR 0104 line 2."
                ),
                "summary_text": "The election forces a FULL Sec. 199A add-back on EVERY owner regardless of AGI - an entity-level election that rewrites every owner's individual return.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "No credits on the electing entity's return; tiered partners are INDEPENDENT",
                "excerpt_text": (
                    "'The electing pass-through entity MAY NOT CLAIM ANY REFUNDABLE OR NONREFUNDABLE CREDITS ON ITS "
                    "RETURN.' (corroborated by Sec. 39-22-344(3), C.R.S.) - so in Mode C the DR 0106CR Column C must "
                    "be zero and DR 0106 lines 14 and 15 are blank. TIERED PARTNERS: 'Each tiered partner may make a "
                    "SALT Parity Act election REGARDLESS OF WHETHER an election is made by any lower-tier partnership "
                    "in which the tiered partner is a partner. Any SALT Parity Act election made by a lower-tier "
                    "partnership DOES NOT OBLIGATE any of its tiered partners to make a similar election.' And: 'A "
                    "tiered partner CANNOT CLAIM ANY CREDIT OR SUBTRACTION, or make any other adjustment on its "
                    "return, based on a SALT Parity Act election made by a lower-tier partnership. In particular, an "
                    "electing partnership or S corporation cannot claim any credit for any part of the tax paid by a "
                    "lower-tier partnership that also made a SALT Parity Act election.' The credit PASSES THROUGH the "
                    "tiered partner to its own owners on DR 0106K line 25. Estimated payments: the prior-year safe "
                    "harbor applies 'ONLY IF the entity made a SALT Parity Act election for that preceding tax year'. "
                    "Excluded owner: 'any partner that is a C corporation that is unitary with the partnership'."
                ),
                "summary_text": "Mode C: zero credits on the entity's own return. The election does NOT propagate up or down a tier chain; the credit passes through on DR 0106K line 25.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "CO_2025_DR0233",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "CO",
        "title": "2025 Colorado DR 0233 - Underpayment of Estimated Tax penalty computation for a Partnership and S Corporation",
        "citation": "Colorado DR 0233 (07/30/25), 4 pp.",
        "issuer": "Colorado Department of Revenue",
        "official_url": _CO_URL + "DR0233_2025.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.4,
        "topics": ["co_pte_income_tax"],
        "excerpts": [
            {
                "excerpt_label": "70%/100% test, the first-year block, NO annualized method, split-year interest",
                "excerpt_text": (
                    "Part 1: 'line 1 - $5,000; If line 2 is larger, enter zero and no penalty is due.' Part 2: 'The "
                    "required annual amount to be paid is the LESSER OF: 1. 70% of actual net Colorado tax liability, "
                    "or 2. 100% of preceding year's Colorado tax liability only applies if: the preceding year was "
                    "12-month tax year, and the partnership or S corporation filed a Colorado return, and the "
                    "partnership or S corporation did not have taxable income of $1,000,000 or more for any of the "
                    "three immediately preceding taxable income years.' Line 6: 'If you are making a SALT Parity Act "
                    "election and DID NOT FILE a Colorado return making a SALT Parity Act election for the previous "
                    "year, enter the amount from line 5 here and on line 7' - the prior-year safe harbor is "
                    "UNAVAILABLE to a first-year electing entity. Large entity: 'can base its FIRST QUARTER estimated "
                    "tax payment on 25% of the previous year's tax liability. However, future payments must be based "
                    "on the actual tax liability for the current tax year and any underpayment occurring in the first "
                    "quarter as a result of this estimation must be paid with the second quarterly payment.' Part 3: "
                    "'The dates to be entered on line 10 are the 15th day of the FOURTH, SIXTH, NINTH AND TWELFTH "
                    "MONTH of the taxable year.' Line 18: 'Underpayment on line 15 multiplied by 12% FOR DATES IN 2025 "
                    "or multiplied by 11% FOR DATES IN 2026 multiplied by number of days on line 17 divided by 365 "
                    "(366 for leap year)'. And verbatim: 'COLORADO LAW DOES NOT PROVIDE AN OPTION FOR PARTNERSHIPS OR "
                    "S CORPORATIONS TO COMPUTE THEIR ESTIMATED PAYMENTS USING AN ANNUALIZED INCOME INSTALLMENT METHOD.'"
                ),
                "summary_text": "70%/100% with a first-year-election block; large-entity 25% Q1 rule; four quarterly dates; 12% (2025) / 11% (2026) interest; NO annualized method for PTEs (C corps DO get it).",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "CO_CORP_TAX_GUIDE_2026",
        "source_type": "state_instruction",
        "source_rank": "primary_official",
        "jurisdiction_code": "CO",
        "title": "Colorado Corporate Income Tax Guide (Rev. March 2026) - Part 9 estimated payments, incorporated by reference by the DR 0106",
        "citation": "CDOR Colorado Corporate Income Tax Guide, Rev. March 2026, 47 pp.",
        "issuer": "Colorado Department of Revenue",
        "official_url": _CO_URL + "Corporate_Income_Tax_Guide_Mar_2026_.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.0,
        "topics": ["co_pte_income_tax"],
        "excerpts": [
            {
                "excerpt_label": "The $5,000 threshold - the OTHER side of the W9 3-2 split (verifier C9)",
                "excerpt_text": (
                    "The DR 0106 expressly incorporates this guide by reference for the estimated-payment rules "
                    "('Please see Part 9 of the Colorado Corporate Income Tax Guide'). Part 9 states, verbatim: 'No "
                    "estimated tax penalty is due if a C corporation's net tax liability for the tax year is LESS THAN "
                    "$5,000' - which agrees with the DR 0106's '>= $5,000', NOT with the 'exceeds' wording used by the "
                    "DR 0233 instructions, the DR 0106EP and the SALT Parity publication. This makes the threshold a "
                    "LIVE 3-2 SOURCE SPLIT, not a one-sided erratum. The exposure is a single point - net tax of "
                    "EXACTLY $5,000. Part 9 also grants C CORPORATIONS the annualized installment method ('C "
                    "corporations can use the Annualized Installment' ... Schedule A Part II), which the DR 0233 "
                    "expressly DENIES to partnerships and S corporations - a genuine PTE/C-corp divergence. Its annual "
                    "interest-rate table reads 2022 6%, 2023 8%, 2024 11%, 2025 12%, 2026 11%. Also the source of the "
                    "negative finding that Colorado has NO depreciation modification and NO corporate AMT."
                ),
                "summary_text": "C9: the Corporate Guide sides with the DR 0106's '>= $5,000' against the 'exceeds' sources. 3-2 split -> Ken RULING (W9), not an erratum. Also grants C corps the annualized method PTEs do not get.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "CO_2025_DR0106CR",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "CO",
        "title": "2025 Colorado DR 0106CR - Pass-Through Entity Credit Schedule (mandatory attachment)",
        "citation": "Colorado DR 0106CR (10/02/25), 12 pp.",
        "issuer": "Colorado Department of Revenue",
        "official_url": _CO_URL + "DR0106CR_2025.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.3,
        "topics": ["co_pte_income_tax"],
        "excerpts": [
            {
                "excerpt_label": "Column rule, line 38 range, and the Credit for Tax Paid to Other States",
                "excerpt_text": (
                    "'Every partnership and S corporation must submit a completed form DR 0106CR with its return' - a "
                    "MANDATORY ATTACHMENT even in Modes A and C. Column rule, verbatim: 'Unless the partnership or S "
                    "corporation is filing a composite return ..., enter in column B the amount from column A and enter "
                    "0 (zero) in column C. THIS PROCEDURE APPLIES TO ANY PARTNERSHIP OR S CORPORATION THAT IS NOT "
                    "FILING A COMPOSITE RETURN, INCLUDING ANY PARTNERSHIP OR S CORPORATION MAKING AN ELECTION UNDER THE "
                    "S A L T PARITY ACT.' Line 38, verbatim: 'Sum lines 5 through 37 for columns A, B, and C' - NOT "
                    "1 through 37; lines 1-4 are the recapture and other-state-tax block. Line 38 column C transfers "
                    "to DR 0106 line 14. LINES 2-4, Credit for Tax Paid to Other States, verbatim: 'A partner or "
                    "shareholder who is a Colorado resident individual may claim credit for their share of any net "
                    "income tax imposed upon and paid to another state by the partnership or S corporation. THIS CREDIT "
                    "IS ALLOWED EVEN IF THE IMPOSITION UPON THE PARTNERSHIP OR S CORPORATION WAS AT THE PARTNERSHIP'S "
                    "OR S CORPORATION'S ELECTION.' Filed on a SEPARATE DR 0106CR PER STATE ('Complete lines 2 through 4 "
                    "on a separate DR 0106CR for each state to which tax was paid'). This is the path by which ANOTHER "
                    "STATE'S PTET reaches a Colorado resident owner."
                ),
                "summary_text": "DR 0106CR mandatory on every return; L38 = SUM L5..L37 (not 1-37); not-composite -> B = A and C = 0; lines 2-4 are the multi-state PTET credit path, one DR 0106CR per state.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "CO_2025_DR0107",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "CO",
        "title": "2025 Colorado DR 0107 - Nonresident Partner or Shareholder Agreement",
        "citation": "Colorado DR 0107 (06/05/25), 2 pp.",
        "issuer": "Colorado Department of Revenue",
        "official_url": _CO_URL + "DR0107_2025.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.2,
        "topics": ["co_composite_return"],
        "excerpts": [
            {
                "excerpt_label": "The agreement, and its PERSISTENCE across years (W12)",
                "excerpt_text": (
                    "The owner agrees 'to file a Colorado income tax return and make timely payment of all taxes ... "
                    "with respect to my share of the Colorado income' and 'to be subject to personal jurisdiction in "
                    "the state of Colorado for purposes of the collection of unpaid income tax together with related "
                    "penalties and interest'. Effect: EXCLUDES that owner from the mandatory composite return. It is "
                    "ONE-TIME, NOT ANNUAL - DR 0106K-I, verbatim: 'A form DR 0107 filed with the Department for a "
                    "nonresident partner REMAINS IN EFFECT FOR FUTURE TAX YEARS. The partnership does not need to "
                    "submit a new form DR 0107 for the same nonresident partner each year.' The face itself carries "
                    "both the persistence and its revocation channel: 'I furthermore understand the Department of "
                    "Revenue will consider the timely first filing of this agreement as applicable to all future "
                    "filing periods UNLESS NOTIFIED OTHERWISE.' Delivered by the owner to the entity and submitted BY "
                    "THE ENTITY with the DR 0106. NOT REQUIRED AT ALL if the entity elects SALT Parity. (The face "
                    "still points at 'the instructions ... in the 106 Book' - a booklet that does not exist for "
                    "TY2025; a stale cross-reference on an otherwise current form.)"
                ),
                "summary_text": "DR 0107 excludes an owner from the mandatory composite; it is ONE-TIME and PERSISTS across years, with revocation 'unless notified otherwise' -> a client-record flag, not a form field (W12).",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "CO_GIL_22_003",
        "source_type": "state_instruction",
        "source_rank": "reference_only",
        "jurisdiction_code": "CO",
        "title": "CDOR General Information Letter GIL 22-003 - nonresident partner distributive-share sourcing",
        "citation": "CDOR GIL 22-003 (2022-04-25) - NON-BINDING guidance, cited by name in the DR 0106K-I partnership half",
        "issuer": "Colorado Department of Revenue",
        "official_url": _CO_URL.replace("documents/", "documents/") + "GIL%2022-003.pdf",
        "current_status": "active",
        "is_substantive_authority": False,
        "trust_score": 6.5,
        "topics": ["co_pte_income_tax"],
        "excerpts": [
            {
                "excerpt_label": "Cited BY NAME as authority for the partnership Column B sourcing rule (W1)",
                "excerpt_text": (
                    "The DR 0106K-I partnership half cites this letter by name: 'See Part V of form DR 0106 AND "
                    "GENERAL INFORMATION LETTER 22-003.' It addresses the sourcing of a nonresident partner's "
                    "distributive share under Sec. 39-22-109, C.R.S., and the character rule. It bears directly on W1 "
                    "- whether v1 COMPUTES partnership direct sourcing or DIRECT-ENTERS Column B - which is the "
                    "largest single scope lever on the Colorado build, and it must be read before the walk. A GIL is "
                    "EXPRESSLY NON-BINDING on the Department: cite it as GUIDANCE, NOT AUTHORITY. Surfaced by the "
                    "adversarial verification pass; absent from the research brief entirely."
                ),
                "summary_text": "GIL 22-003 is cited by name in the DR 0106K-I for partnership Column B sourcing. Non-binding guidance. Read before the W1 walk.",
                "is_key_excerpt": False,
            },
        ],
    },
]

AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    ("CO_2025_DR0106", FORM_CODE, "governs"),
    ("CO_2025_DR0106K_I", FORM_CODE, "governs"),
    ("CO_2025_DR0106K", FORM_CODE, "governs"),
    ("CO_2025_DR0106CR", FORM_CODE, "governs"),
    ("CO_2025_DR0233", FORM_CODE, "governs"),
    ("CO_2025_DR0107", FORM_CODE, "governs"),
    ("CO_CRS_39_22_601", FORM_CODE, "governs"),
    ("CO_CRS_39_22_344", FORM_CODE, "governs"),
    ("CO_CRS_39_22_301_RATE", FORM_CODE, "governs"),
    ("CO_CRS_39_22_104_RATE", FORM_CODE, "governs"),
    ("CO_CRS_39_22_608_DUE", FORM_CODE, "governs"),
    ("CO_CRS_39_22_343_ELECT", FORM_CODE, "governs"),
    ("CO_CRS_39_22_347_CREDIT", FORM_CODE, "governs"),
    ("CO_ITT_SALT_PARITY_2025", FORM_CODE, "informs"),
    ("CO_CORP_TAX_GUIDE_2026", FORM_CODE, "informs"),
    ("CO_GIL_22_003", FORM_CODE, "informs"),
    ("CO_CRS_39_22_103", FORM_CODE, "governs"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM — CO_DR0106 : FACTS
# ═══════════════════════════════════════════════════════════════════════════

CO_FACTS: list[dict] = [
    # ---- the module fork + mode machine ----------------------------------
    {"fact_key": "federal_return_type", "label": "Attached federal return (drives the module fork)",
     "data_type": "choice", "required": True, "sort_order": 1, "choices": ["1065", "1120S"],
     "notes": "W2. THE FORK KEY. Derived from the ATTACHED FEDERAL RETURN, never from Box A. "
              "Fourteen of the sixteen forks change the arithmetic based on this value."},
    {"fact_key": "box_a_legal_form", "label": "Box A - legal form (NOT the module fork)",
     "data_type": "choice", "required": True, "sort_order": 2,
     "choices": ["Partnership", "S Corporation", "LLC", "LP", "LLP", "LLLP", "Association", "Non-Profit"],
     "notes": "Box A is LEGAL form, not federal tax classification. An LLC taxed as a partnership marks LLC. "
              "Six of the eight values are silent on 1065-vs-1120S. Never use this to fork."},
    {"fact_key": "salt_parity_election", "label": "Box I - SALT Parity Act election made (Mode C)",
     "data_type": "boolean", "required": False, "sort_order": 3,
     "notes": "Elective, annual, IRREVOCABLE for the year, binding on all owners. Elect via Box I, DR 1705, "
              "or the SALT Parity box on DR 0106EP. Forces Part III; blocks Part II."},
    {"fact_key": "composite_return_filed", "label": "Part II composite nonresident return filed (Mode B)",
     "data_type": "boolean", "required": False, "sort_order": 4,
     "notes": "MANDATORY absent a SALT Parity election when an unexcluded nonresident owner exists."},
    {"fact_key": "is_publicly_traded_partnership", "label": "User-asserted publicly traded partnership (composite carve-out)",
     "data_type": "boolean", "required": False, "sort_order": 5,
     "notes": "[UNV-5] R14. PARTNERSHIP MODULE ONLY. Statute-only carve-out; zero hits for 'publicly traded' or "
              "'7704' anywhere in the DR 0106 kit. User-asserted flag, never a silent pass."},
    {"fact_key": "is_amended_return", "label": "Mark for Amended Return", "data_type": "boolean",
     "required": False, "sort_order": 6,
     "notes": "'Enter all fields even if the value has not changed from the original return. Submit all schedules "
              "and supporting documentation, even if they were submitted with the original return.'"},
    {"fact_key": "listed_reportable_transaction", "label": "Listed or reportable transaction box marked",
     "data_type": "boolean", "required": False, "sort_order": 7,
     "notes": "R16. Attach IRS Form 8886 or DR 1831; C.R.S. Secs. 39-22-651 to 659."},

    # ---- federal Schedule K feed (Part I lines 1-2) -----------------------
    {"fact_key": "fed_schedule_k", "label": "Federal Schedule K line values (keyed by line number, per module)",
     "data_type": "string", "required": True, "sort_order": 10,
     "notes": "F4. 1065: lines 1, 2, 3c, 4c, 5, 6a, 7, 8, 9a, 10, 11. 1120-S: lines 1, 2, 3c, 4, 5a, 6, 7, 8a, 9, 10. "
              "Line 1 feeds DR 0106 L1; the rest feed L2. Sign rule: income/gains positive, losses/deductions negative."},
    {"fact_key": "sec179_disposition_gain", "label": "Sec. 179-disposition gain/loss (Sch. K 20c / 17d statement)",
     "data_type": "decimal", "required": False, "sort_order": 11,
     "notes": "SEC. 179 TOUCHPOINT (i). F5. Gain or loss on disposition of property 'for which a section 179 "
              "deduction has been passed through'. Reported at OWNER level federally, so Colorado pulls it back in. "
              "A spec that omits it UNDERSTATES line 2."},
    {"fact_key": "marijuana_natural_medicine_deduction", "label": "DR 0106 line 7 - Colorado Marijuana / Natural Medicine deduction",
     "data_type": "decimal", "required": False, "sort_order": 12,
     "notes": "Direct-entry. Requires a PRO FORMA 1065/1120-S computed without regard to IRC Sec. 280E; the "
              "deduction is the DIFFERENCE in ordinary business income. Submit both sets of federal forms plus the "
              "MED/NMD license number. Entered as a POSITIVE number."},

    # ---- K-1 Column A aggregates (Part I lines 3, 4, 6, 8) ---------------
    {"fact_key": "k1_col_a_line9_state_tax_addback", "label": "Sum of DR 0106K Column A line 9 (state income tax add-back)",
     "data_type": "decimal", "required": False, "sort_order": 20,
     "notes": "F7 split. POSITIVE on the K-1. Feeds DR 0106 line 4 WITHOUT inversion. Includes tier-chain "
              "accumulation from lower-tier Colorado K-1s."},
    {"fact_key": "k1_col_a_line10_business_meals", "label": "Sum of DR 0106K Column A line 10 (IRC Sec. 274(k) business meals)",
     "data_type": "decimal", "required": False, "sort_order": 21,
     "notes": "POSITIVE on the K-1. Feeds DR 0106 line 3 WITHOUT inversion."},
    {"fact_key": "k1_col_a_line11_other_additions", "label": "Sum of DR 0106K Column A line 11 (other Colorado additions)",
     "data_type": "decimal", "required": False, "sort_order": 22,
     "notes": "F15 - the item inventory FORKS. S corp has a FOREIGN-TAX add-back the partnership does not. "
              "POSITIVE on the K-1. Feeds DR 0106 line 4 WITHOUT inversion."},
    {"fact_key": "k1_col_a_line12_federal_deductions", "label": "Sum of DR 0106K Column A line 12 (federal deductions, NEGATIVE)",
     "data_type": "decimal", "required": False, "sort_order": 23,
     "notes": "THE SIGN FLIP + SEC. 179 TOUCHPOINT (ii). Entered NEGATIVE on the K-1 ('any federal deductions on "
              "line 12, as negative amounts'). = 1065 K-1 Box 12 + Box 13 / 1120-S K-1 Box 11 + Box 12; Box 12 / "
              "Box 11 IS the Sec. 179 deduction. Feeds DR 0106 line 6 SIGN-INVERTED (positive)."},
    {"fact_key": "k1_col_a_line13_co_subtractions", "label": "Sum of DR 0106K Column A line 13 (Colorado subtractions, NEGATIVE)",
     "data_type": "decimal", "required": False, "sort_order": 24,
     "notes": "THE SIGN FLIP. F16 - the item inventory FORKS (partnership-only export-taxpayer; S-corp-only "
              "Sec. 280C wages). Entered NEGATIVE on the K-1. Feeds DR 0106 line 8 SIGN-INVERTED (positive), "
              "EXCLUDING any marijuana/natural-medicine amount already reported on line 7."},

    # ---- owners (the DR 0106K roster) ------------------------------------
    {"fact_key": "owners", "label": "Owner roster (per-owner DR 0106K records)",
     "data_type": "string", "required": True, "sort_order": 30,
     "notes": "Each owner: residency (resident / part_year / nonresident), owner_kind (individual / estate / trust / "
              "c_corp / partnership), dr0107, exempt_112, unitary_ccorp, col_a, col_b. PART-YEAR OWNERS ARE TREATED "
              "AS RESIDENTS. col_a / col_b are the sums of lines 1-3 + 5-13 (LINE 4 SKIPPED - guaranteed payments)."},
    {"fact_key": "num_owners_year_end", "label": "Box H - number of partners or shareholders AS OF YEAR END",
     "data_type": "integer", "required": False, "sort_order": 31,
     "notes": "As of YEAR END, not a weighted count."},
    {"fact_key": "k1_line4_guaranteed_payments_col_b", "label": "DR 0106K line 4 Column B - direct-sourced guaranteed payments",
     "data_type": "decimal", "required": False, "sort_order": 32,
     "notes": "F3. PARTNERSHIP ONLY (N/A for an S corp). ALWAYS direct-sourced under 1 CCR 201-2, Rule "
              "39-22-109(3)(b)(xii) - no formulary alternative is offered, even for a partnership that elected "
              "receipts-factor apportionment. ALWAYS DIRECT-ENTRY (W1). EXCLUDED from every tax base (W5)."},
    {"fact_key": "direct_sourced_col_b_amounts", "label": "Partnership direct-sourced Column B amounts (per owner, direct-entry)",
     "data_type": "string", "required": False, "sort_order": 33,
     "notes": "W1 - the largest scope lever. Direct sourcing under Sec. 39-22-109 is the partnership DEFAULT for "
              "nonresident individual/estate/trust partners. Three Rule 39-22-109(3) tests as help text: real or "
              "tangible property in Colorado; business carried on in Colorado; intangibles employed in a Colorado "
              "business. Applies to NO other partner type."},

    # ---- Part V ----------------------------------------------------------
    {"fact_key": "receipts_colorado", "label": "Part V - total Colorado receipts (lines 2-7, Colorado column)",
     "data_type": "decimal", "required": False, "sort_order": 40,
     "notes": "Categories: tangible personal property; services; sale/rental/lease/license of real property; "
              "rental/lease/license of TPP; sale/rental/lease/license of intangibles; distributive share of "
              "partnership factors. Market-based sourcing, Sec. 39-22-303.6(5)-(6). DIRECT-ENTRY by category."},
    {"fact_key": "receipts_everywhere", "label": "Part V - total receipts everywhere (lines 2-7, Everywhere column)",
     "data_type": "decimal", "required": False, "sort_order": 41,
     "notes": "EXCLUDES foreign-source income modified out on Part I line 8 (face instruction; Sec. 39-22-303.6(4)(b)). "
              "[UNV-9]: a zero denominator has no published rule."},
    {"fact_key": "no_out_of_state_activity", "label": "No income from business activity outside Colorado (100% Colorado)",
     "data_type": "boolean", "required": False, "sort_order": 42,
     "notes": "Sec. 39-22-303.6(3)(a). Short path: source 100% to Colorado."},
    {"fact_key": "all_income_apportionable_election", "label": "Part V line 15 - Sec. 39-22-303.6(8) all-apportionable election",
     "data_type": "boolean", "required": False, "sort_order": 43,
     "notes": "'made by the extended due date of the tax return. Once made, the election is IRREVOCABLE for the tax "
              "year.' Consequence on the face: enter 0 (zero) on lines 10 and 13."},
    {"fact_key": "nonapportionable_allocated_total", "label": "Part V line 10(f) - total income directly allocable to any state",
     "data_type": "decimal", "required": False, "sort_order": 44,
     "notes": "(a) net rents/royalties from real or tangible property; (b) capital gains and losses; (c) interest and "
              "dividends; (d) patents and copyright royalties; (e) other nonapportionable income. DIRECT-ENTRY."},
    {"fact_key": "allocable_to_colorado_total", "label": "Part V line 13(f) - total income directly allocable to Colorado",
     "data_type": "decimal", "required": False, "sort_order": 45,
     "notes": "Same (a)-(e) breakdown. DIRECT-ENTRY."},
    {"fact_key": "apportionment_method", "label": "DR 0106 line 11 - apportionment and allocation method",
     "data_type": "choice", "required": True, "sort_order": 46,
     "choices": ["Part V", "Other", "Income is all Colorado Income"],
     "notes": "F1. A partnership using direct sourcing marks 'Other' - and may STILL be required to complete Part V "
              "if it has any C-corporation or upper-tier-partnership partner."},

    # ---- Part IV payments / credits --------------------------------------
    {"fact_key": "credits_dr0106cr_l38_col_c", "label": "DR 0106 line 14 - credits from DR 0106CR line 38 column C",
     "data_type": "decimal", "required": False, "sort_order": 50,
     "notes": "W10 direct-entry. Composite mode only - 'Do not include any amounts from Column B on this line.' "
              "MUST BE ZERO in Modes A and C. The DR 0106CR is a MANDATORY attachment on EVERY return."},
    {"fact_key": "gross_conservation_easement_credit", "label": "DR 0106 line 15 - Gross Conservation Easement credit (DR 1305G L33)",
     "data_type": "decimal", "required": False, "sort_order": 51, "notes": "R2 RED-defer. Direct-entry."},
    {"fact_key": "in_lieu_of_amount_l22", "label": "DR 0106 line 22 - Sec. 39-22-601.5(3)(e) partnership-audit in-lieu-of amount",
     "data_type": "decimal", "required": False, "sort_order": 52,
     "notes": "R7 / [UNV-8]. NO Colorado form computes it and the instruction gives NO formula - filing mechanics "
              "only (amended return after an IRS partnership audit). Direct-entry with a RED."},
    {"fact_key": "dr0619_repayment_l23", "label": "DR 0106 line 23 - DR 0619 credit repayment (lines 4 and 11)",
     "data_type": "decimal", "required": False, "sort_order": 53, "notes": "R1. NEW for TY2025 - advance-payment clawback."},
    {"fact_key": "estimated_extension_payments_l25", "label": "DR 0106 line 25 - estimated tax, extension payments and credits",
     "data_type": "decimal", "required": False, "sort_order": 54,
     "notes": "2025 estimated payments; 2024 overpayment carried forward; DR 0158-N extension payments; DR 1079 "
              "real-estate withholding (R10 - the DR 1079 must be submitted)."},
    {"fact_key": "lottery_gambling_withholding_l26", "label": "DR 0106 line 26 - withholding from lottery or gambling winnings",
     "data_type": "decimal", "required": False, "sort_order": 55, "notes": "From W-2G; W-2Gs must be submitted."},
    {"fact_key": "dr0619_credit_l27", "label": "DR 0106 line 27 - additional credit from DR 0619 (lines 3 and 10)",
     "data_type": "decimal", "required": False, "sort_order": 56, "notes": "R1."},
    {"fact_key": "interest_l30", "label": "DR 0106 line 30 - interest on unpaid balance", "data_type": "decimal",
     "required": False, "sort_order": 57, "notes": "Accrues from the ORIGINAL due date. Rate per Tax Topics: Penalties and Interest."},
    {"fact_key": "overpayment_credited_forward_l34", "label": "DR 0106 line 34 - overpayment credited to next year's estimated tax",
     "data_type": "decimal", "required": False, "sort_order": 58},
    {"fact_key": "pct_tax_paid_by_original_due_date", "label": "Percentage of tax paid by the ORIGINAL due date (90% penalty gate)",
     "data_type": "decimal", "required": False, "sort_order": 59,
     "notes": "DR 0106 line 29 gate: 'If 90% of the tax is not paid by the original due date (without extension)'. "
              "There is NO extension to pay."},
    {"fact_key": "months_delinquent", "label": "Months of delinquency (line 29 penalty)", "data_type": "integer",
     "required": False, "sort_order": 60},

    # ---- estimated tax (DR 0233) -----------------------------------------
    {"fact_key": "prior_year_co_tax_liability", "label": "Preceding year's Colorado tax liability (DR 0233 line 6)",
     "data_type": "decimal", "required": False, "sort_order": 70},
    {"fact_key": "prior_year_was_12_months", "label": "Preceding year was a 12-month tax year", "data_type": "boolean",
     "required": False, "sort_order": 71},
    {"fact_key": "filed_prior_year_co_return", "label": "Filed a Colorado return for the preceding year", "data_type": "boolean",
     "required": False, "sort_order": 72},
    {"fact_key": "elected_salt_parity_prior_year", "label": "Made a SALT Parity election for the PRECEDING year",
     "data_type": "boolean", "required": False, "sort_order": 73,
     "notes": "DR 0233 line 6 - the prior-year safe harbor is UNAVAILABLE to a first-year electing entity. "
              "A PTE-specific condition the C-corp rule does NOT have."},
    {"fact_key": "prior_3yr_income_1m_or_more", "label": "Taxable income >= $1,000,000 in any of the 3 preceding years",
     "data_type": "boolean", "required": False, "sort_order": 74,
     "notes": "Blocks the 100%-of-prior-year leg; enables the large-entity 25% first-quarter rule."},
    {"fact_key": "estimated_tax_penalty_l31", "label": "DR 0106 line 31 - estimated tax penalty (DR 0233 line 22)",
     "data_type": "decimal", "required": False, "sort_order": 75,
     "notes": "Due only if (a) composite or SALT Parity, (b) net tax liability over $5,000 (W9 ruling), and (c) a "
              "required installment was missed."},

    # ---- balance sheet boxes ---------------------------------------------
    {"fact_key": "depreciable_assets_beginning", "label": "Box B - beginning depreciable assets from the federal return",
     "data_type": "decimal", "required": False, "sort_order": 80,
     "notes": "F6. NET OF ACCUMULATED DEPRECIATION. 1065 Sch. L line 9b col (b) / 1120-S Sch. L line 10b col (b). "
              "A BALANCE-SHEET TRANSCRIPTION, not a tax computation. NOT a depreciation modification."},
    {"fact_key": "depreciable_assets_ending", "label": "Box C - ending depreciable assets from the federal return",
     "data_type": "decimal", "required": False, "sort_order": 81,
     "notes": "F6. NET OF ACCUMULATED DEPRECIATION. 1065 Sch. L line 9b col (d) / 1120-S Sch. L line 10b col (d)."},

    # ---- narrative / blocker ---------------------------------------------
    {"fact_key": "business_or_profession", "label": "Box D - business or profession", "data_type": "string",
     "required": False, "sort_order": 90},
    {"fact_key": "date_of_organization", "label": "Box E - date of organization or incorporation (MM/DD/YY)",
     "data_type": "date", "required": False, "sort_order": 91},
    {"fact_key": "is_final_return", "label": "Box F - final return", "data_type": "boolean", "required": False, "sort_order": 92},
    {"fact_key": "federal_changes_last_four_years", "label": "Box G - federal changes in the last four years",
     "data_type": "boolean", "required": False, "sort_order": 93,
     "notes": "Requires a date and a written explanation on the face. Also a trigger for R7 (line 22)."},
    {"fact_key": "claims_retroactive_sec174a_election", "label": "Return relies on a RETROACTIVE federal amendment (e.g. OBBBA Sec. 174A)",
     "data_type": "boolean", "required": False, "sort_order": 94,
     "notes": "[UNV-7] / W13, RULED BY KEN 2026-08-17 (walk A1): Colorado's rolling conformity DOES reach "
              "retroactively-effective federal amendments, so DR 0106 line 1 transcribes federal ordinary income as "
              "filed and NO Sec. 174A adjustment is computed in either direction. The flag is retained as an "
              "INFORMATIONAL marker only - it drives D_CO106_BLOCK_174A_CONFORMITY (severity=info), which tells the "
              "preparer the position rests on Ken's reading of Sec. 39-22-103(5.3) and not on published CDOR "
              "guidance. It no longer blocks. Re-verify before the module ships."},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM — CO_DR0106 : RULES
# ═══════════════════════════════════════════════════════════════════════════

CO_RULES: list[dict] = [
    # ---- the fork and the mode machine -----------------------------------
    {"rule_id": "R-CO-MODULE-FORK", "title": "Module fork (1065 vs 1120S) keys off the ATTACHED FEDERAL RETURN, never Box A",
     "rule_type": "classification", "sort_order": 1,
     "formula": ("module = federal_return_type  # '1065' or '1120S' ; "
                 "NEVER derive from box_a_legal_form. Box A is LEGAL FORM: an LLC taxed as a partnership marks 'LLC', "
                 "and six of the eight Box A values are silent on 1065-vs-1120S. "
                 "16 forks F1..F16; 14 of them change the arithmetic."),
     "inputs": ["federal_return_type", "box_a_legal_form"], "outputs": ["module"],
     "description": ("W2. THE fork key. DR 0106 p. 1 reinforces it: 'any limited liability company classified as a "
                     "partnership for federal income tax purposes' is treated as a partnership - classification "
                     "follows the FEDERAL RETURN. Hard diagnostic when Box A and the federal return are impossibly "
                     "inconsistent (e.g. Box A = 'S Corporation' with an attached 1065)."),
     "exceptions": "Box A = 'S Corporation' with an attached 1065 (or 'Partnership' with an attached 1120-S) -> D_CO106_BOXA_FORK_CONFLICT."},
    {"rule_id": "R-CO-MODE", "title": "Three-mode state machine (A informational / B composite / C SALT Parity)",
     "rule_type": "routing", "sort_order": 2,
     "formula": ("if salt_parity_election and composite_return_filed: HARD RED (mutually exclusive) ; "
                 "elif salt_parity_election: MODE C -> Part III, line 21 = L20 ; "
                 "elif composite_return_filed: MODE B -> Part II, line 21 = L16 ; "
                 "else: MODE A -> Parts II and III BLANK, line 21 = 0 (informational-only, still a MANDATORY filing)"),
     "inputs": ["salt_parity_election", "composite_return_filed"], "outputs": ["mode", "L21"],
     "description": ("W3. Mutual exclusivity verbatim at line 21 and reinforced twice more on the face and at Box I; "
                     "statutory basis Sec. 39-22-344(5), C.R.S. MODE A IS A REAL AND COMMON FILING - 'Every "
                     "partnership and S corporation must file a DR 0106 for any year it is doing business in "
                     "Colorado.' An entity with only resident owners, or whose nonresident owners all filed DR 0107, "
                     "files a computed line 10, a marked line 11, no Part II, no Part III and ZERO TAX. A spec that "
                     "treats the DR 0106 as a tax-computing form only will not produce this return."),
     "exceptions": "Parts II and III both populated -> D_CO106_MODE_CONFLICT (hard RED, never a silent precedence)."},
    {"rule_id": "R-CO-COMP-REQ", "title": "Mandatory-composite test - five exclusions and the statutory carve-outs",
     "rule_type": "validation", "sort_order": 3,
     "formula": ("required = NOT salt_parity_election "
                 "AND NOT (module == '1065' AND is_publicly_traded_partnership) "
                 "AND any(owner not excluded) ; "
                 "excluded(owner) = resident (incl. PART-YEAR) | (module=='1065' AND owner_kind in "
                 "{c_corp, partnership}) | exempt_112 | dr0107 | col_b < 0"),
     "inputs": ["owners", "salt_parity_election", "is_publicly_traded_partnership", "federal_return_type"],
     "outputs": ["composite_required"],
     "description": ("W3. Composite is MANDATORY, not elective (Sec. 39-22-601(5.5)(d)(I) and (2.7)(d)(I), C.R.S.). "
                     "The fifth (negative-income) exclusion is STATUTORY, not merely an instruction: "
                     "Sec. 39-22-601(5.5)(d)(III)(A) and (2.7)(d)(III)(A). CORRECTION C1 (HIGH): the "
                     "all-owners-already-excluded carve-out EXISTS FOR BOTH MODULES - Sec. 39-22-601(5.5)(d)(VII)(C) "
                     "and (2.7)(d)(VII)(B). Without it this RED false-positives on any S corp whose every nonresident "
                     "shareholder filed a DR 0107. Only the PTP carve-out is partnership-only."),
     "exceptions": "PTP carve-out is [UNV-5] statute-only -> user-asserted flag + R14 RED, never a silent pass."},

    # ---- Part I, the sign flip, and both Sec. 179 touchpoints ------------
    {"rule_id": "R-CO-L1", "title": "DR 0106 line 1 - ordinary income from federal Schedule K (per module)",
     "rule_type": "calculation", "sort_order": 10,
     "formula": "L1 = federal Schedule K line 1 (1065 Sch. K L1 | 1120-S Sch. K L1)",
     "inputs": ["fed_schedule_k", "federal_return_type"], "outputs": ["L1"],
     "description": ("F12 ERRATUM: the DR 0106 line 1 instruction names ONLY the 1065 and never names the 1120-S. "
                     "BUILD TO BOTH. Sign rule verbatim: 'Enter income and gains as positive numbers; enter losses "
                     "and deductions as negative numbers. For paper returns, put negative amounts in parentheses.'")},
    {"rule_id": "R-CO-L2-FED179", "title": "DR 0106 line 2 - other income per module PLUS the Sec. 179-disposition aggregation",
     "rule_type": "calculation", "sort_order": 11,
     "formula": ("1065:  L2 = Sch. K (2 + 3c + 4c + 5 + 6a + 7 + 8 + 9a + 10 + 11) + sec179_disposition_gain ; "
                 "1120S: L2 = Sch. K (2 + 3c + 4  + 5a + 6  + 7 + 8a + 9  + 10) + sec179_disposition_gain ; "
                 "sec179_disposition_gain from the statement attached for Sch. K line 20c (1065) / 17d (1120-S)"),
     "inputs": ["fed_schedule_k", "federal_return_type", "sec179_disposition_gain"], "outputs": ["L2"],
     "description": ("F4 + F5. SEC. 179 TOUCHPOINT (i) of TWO. Verbatim: 'Also include any gain or loss on the sale, "
                     "exchange, or other disposition of property reported on a statement attached for line 20c of "
                     "Schedule K (I R S Form 1065) or line 17d of Schedule K (I R S Form 1120-S) for which a section "
                     "179 deduction has been passed through to partners or shareholders.' A STARTING-POINT "
                     "AGGREGATION rule, not a state modification - the item sits outside federal Schedule K's "
                     "numbered income lines because it is reported at the OWNER level. A SPEC THAT OMITS IT "
                     "UNDERSTATES LINE 2. Note line 2 lists INCOME lines only and deliberately EXCLUDES Sch. K 12/13 "
                     "(1065) and 11/12 (1120-S) - i.e. it excludes the Sec. 179 DEDUCTION, which arrives at line 6."),
     "exceptions": "Guaranteed payments (1065 Sch. K 4c) ARE in line 2 but are OUT of every tax base (W5)."},
    {"rule_id": "R-CO-L3-L4-NOFLIP", "title": "DR 0106 lines 3 and 4 - K-1 Column A ADDITIONS, NOT sign-inverted",
     "rule_type": "calculation", "sort_order": 12,
     "formula": ("L3 = SUM(DR 0106K Col. A line 10)              # IRC Sec. 274(k) business meals ; "
                 "L4 = SUM(DR 0106K Col. A line 9 + line 11)     # state tax add-back + other Colorado additions ; "
                 "NO SIGN INVERSION - these are already POSITIVE on the K-1"),
     "inputs": ["k1_col_a_line9_state_tax_addback", "k1_col_a_line10_business_meals",
                "k1_col_a_line11_other_additions"], "outputs": ["L3", "L4"],
     "description": ("THE OTHER HALF OF THE SIGN FLIP, and the half most likely to be over-applied. The verifier "
                     "confirmed BOTH halves: 'Lines 3 and 4 (from K-1 L10 and L9+L11) are already positive and must "
                     "NOT be inverted.' Inverting these is as wrong as failing to invert lines 6 and 8. "
                     "F15: the line-11 inventory itself FORKS (S corp carries a foreign-tax add-back)."),
     "exceptions": "Line 4 aggregates BOTH line 9 and line 11 of Column A - not line 9 alone."},
    {"rule_id": "R-CO-SIGNFLIP", "title": "THE SIGN FLIP - DR 0106 lines 6 and 8 INVERT the K-1's negatives",
     "rule_type": "calculation", "sort_order": 13,
     "formula": ("L6 = -SUM(DR 0106K Col. A line 12)   # INVERT: K-1 negative -> DR 0106 positive ; "
                 "L7 = marijuana_natural_medicine_deduction  # entered POSITIVE, direct ; "
                 "L8 = -SUM(DR 0106K Col. A line 13)   # INVERT, EXCLUDING any amount already on line 7 ; "
                 "L9 = L6 + L7 + L8 ;  L10 = L5 - L9"),
     "inputs": ["k1_col_a_line12_federal_deductions", "k1_col_a_line13_co_subtractions",
                "marijuana_natural_medicine_deduction"], "outputs": ["L6", "L7", "L8", "L9", "L10"],
     "description": ("THE SINGLE MOST LIKELY ARITHMETIC BUG IN THIS FORM. The DR 0106K carries deductions and "
                     "subtractions as NEGATIVE ('Enter any losses on lines 1, 2, 3, or 8, and any federal deductions "
                     "on line 12, as negative amounts'; 'Enter subtractions on line 13 as a negative amount'), but "
                     "DR 0106 lines 6, 7 and 8 are entered as POSITIVE and then SUBTRACTED at line 9/10 ('Enter the "
                     "deductions on this line 6 as a positive number', etc.). Aggregating K-1 Col. A L12 -> L6 and "
                     "L13 -> L8 REQUIRES A SIGN INVERSION. Getting it wrong moves line 10 by TWICE the deduction "
                     "total, in the wrong direction. "
                     "SEC. 179 TOUCHPOINT (ii) of TWO RIDES THIS RULE: K-1 line 12 = 1065 K-1 Box 12 + Box 13 / "
                     "1120-S K-1 Box 11 + Box 12, and Box 12 / Box 11 IS the Sec. 179 deduction. Since DR 0106 line 2 "
                     "excludes Sch. K 12/13 and 11/12, line 6 is THE ONLY PATH by which the federal Sec. 179 "
                     "deduction reaches Colorado at all (verifier correction C3, HIGH)."),
     "exceptions": ("Line 6's FACE LABEL ('Allowable deductions from federal Schedule K') and its INSTRUCTION ('the "
                    "total federal deductions reported on line 12 of the Colorado K-1s') DISAGREE. THE INSTRUCTION "
                    "GOVERNS - line 6 is a K-1 aggregation, not a direct federal Sch. K read. Line 8 excludes any "
                    "marijuana/natural-medicine subtraction already reported on line 7.")},
    {"rule_id": "R-CO-L5-L10", "title": "DR 0106 lines 5, 9, 10 - subtotals; Part I is ENTITY-WIDE",
     "rule_type": "calculation", "sort_order": 14,
     "formula": "L5 = L1 + L2 + L3 + L4 ; L9 = L6 + L7 + L8 ; L10 = L5 - L9",
     "inputs": [], "outputs": ["L5", "L9", "L10"],
     "description": ("PART I IS ENTITY-WIDE. Lines 1-10 cover ALL owners - residents, nonresidents, corporate "
                     "partners, and a unitary C-corporation partner excluded from a SALT Parity election. The Part II "
                     "and Part III bases are SUBSETS BUILT FROM THE K-1s, NOT from line 10. Line 10 feeds ONLY "
                     "Part V line 1.")},

    # ---- depreciation: the ABSENCE ---------------------------------------
    {"rule_id": "R-CO-DEPR-NEG", "title": "DEPRECIATION - encode the ABSENCE. Build NO modification of any kind.",
     "rule_type": "validation", "sort_order": 15,
     "formula": ("Sec. 168(k) bonus: CONFORMS - no add-back, no recovery schedule, no separate state basis. "
                 "Sec. 179: CONFORMS at the federal limit - NO state dollar limit, NO phaseout, NO pre-OBBBA freeze. "
                 "NO state basis, NO recapture, NO recovery schedule. "
                 "The ONLY two Sec. 179 mechanics are the line-2 disposition aggregation and the K-1-line-12 -> "
                 "line-6 deduction path - NEITHER is a state modification."),
     "inputs": ["depreciable_assets_beginning", "depreciable_assets_ending"], "outputs": [],
     "description": ("W6. This is a `RULE SAYS NO`, not a `no rule found`, established five ways: (1) Colorado's "
                     "rolling conformity (Sec. 39-22-103(5.3)) takes the IRC as amended; (2) a full-text search of "
                     "CRS 2024 Title 39 for 'bonus depreciation', 'section 168', '168(k)' returns ZERO modification "
                     "provisions, and 'section 179' returns exactly 2 hits, both inside CREDIT definitions; (3) both "
                     "current CDOR guides enumerate every addition and subtraction in force without one; (4) zero "
                     "'168'/'bonus' hits anywhere in the TY2025 PTE form kit; (5) THE ModDate ARGUMENT - the DR 0106 "
                     "was re-stamped 2025-10-13 and the DR 0106K-I 2025-09-23, i.e. AFTER OBBBA (2025-07-04) AND "
                     "after Colorado's August 2025 extraordinary session (HB 25B-1001, HB 25B-1002, both approved "
                     "2025-08-28). The DOR had every opportunity to add a depreciation modification line and DID NOT. "
                     "The absence is a CURRENT EDITORIAL DECISION, not a stale form. "
                     "DO NOT port Georgia's or Tennessee's bonus logic. DO NOT build a 'Colorado depreciation basis' "
                     "ledger. DO NOT create a nullable placeholder add-back field 'for symmetry with other states' - "
                     "a nullable field a preparer can fill is WORSE THAN NO FIELD."),
     "exceptions": ("One archaeological exception exists and is OUT OF SCOPE: the pre-1965 higher-Colorado-basis gain "
                    "subtraction (Corporate Guide Part 5). If it ever surfaced it would ride DR 0106K line 13 / "
                    "DR 0106 line 8, NOT a depreciation line.")},
    {"rule_id": "R-CO-BOXBC", "title": "Boxes B and C - depreciable-assets balance-sheet transcription (NOT a computation)",
     "rule_type": "calculation", "sort_order": 16,
     "formula": ("1065:  Box B = Sch. L line 9b col (b) ; Box C = Sch. L line 9b col (d) ; "
                 "1120S: Box B = Sch. L line 10b col (b) ; Box C = Sch. L line 10b col (d) ; "
                 "both NET OF ACCUMULATED DEPRECIATION"),
     "inputs": ["depreciable_assets_beginning", "depreciable_assets_ending", "federal_return_type"],
     "outputs": ["BOX-B", "BOX-C"],
     "description": ("F6. Verbatim: 'Enter the beginning and ending depreciable assets from the federal return NET OF "
                     "ANY ACCUMULATED DEPRECIATION. Refer to line 10b (columns (b) and (d)) of Schedule L of I R S "
                     "form 1120-S or line 9b (columns (b) and (d)) of Schedule L of I R S form 1065.' A pure "
                     "BALANCE-SHEET TRANSCRIPTION. It is one of only two benign 'depreciat*' mentions on the DR 0106 "
                     "and is emphatically NOT a tax computation and NOT a modification.")},

    # ---- Part V ----------------------------------------------------------
    {"rule_id": "R-CO-PARTV", "title": "Part V - receipts-factor apportionment (single factor, market-based)",
     "rule_type": "calculation", "sort_order": 20,
     "formula": ("PV-1 = DR 0106 Part I line 10 ; PV-8 = SUM(PV-2..PV-7) each column ; "
                 "PV-9 = PV-8(Colorado) / PV-8(Everywhere) [as a %] ; "
                 "PV-11 = PV-1 - PV-10(f) ; PV-12 = PV-9 x PV-11 ; PV-14 = PV-12 + PV-13(f) ; "
                 "no_out_of_state_activity -> 100% Colorado ; "
                 "all_income_apportionable_election -> enter 0 on lines 10 and 13"),
     "inputs": ["receipts_colorado", "receipts_everywhere", "no_out_of_state_activity",
                "all_income_apportionable_election", "nonapportionable_allocated_total",
                "allocable_to_colorado_total"],
     "outputs": ["PV-8", "PV-9", "PV-11", "PV-12", "PV-14"],
     "description": ("Sec. 39-22-303.6, C.R.S. Single factor: receipts. Market-based sourcing at "
                     "Sec. 39-22-303.6(5)-(6). NO THROWBACK / THROWOUT (zero hits in CRS Title 39). "
                     "Sec. 39-22-303.6(3)(a): no out-of-state business activity -> source 100% to Colorado. "
                     "Line 15 election, Sec. 39-22-303.6(8): 'a taxpayer may elect to treat all income as "
                     "apportionable income ... made by the extended due date of the tax return. Once made, the "
                     "election is IRREVOCABLE for the tax year.' Face: 'Do Not Include Foreign-source income modified "
                     "out on the DR 0106, Part I, Line 8' (Sec. 39-22-303.6(4)(b))."),
     "exceptions": ("[UNV-9] Line 9 has NO published decimal precision, NO rounding rule and NO zero-denominator "
                    "rule. A zero 'Everywhere' denominator yields an UNDEFINED ratio -> diagnostic, never a silent 0.")},
    {"rule_id": "R-CO-PARTV-FEED", "title": "Part V feeds the DR 0106K, NOT Parts II/III - line 14 has no DR 0106 destination",
     "rule_type": "routing", "sort_order": 21,
     "formula": ("PV-8 (both columns) -> DR 0106K line 14 (Col. A = Everywhere x ratio; Col. B = Colorado x ratio) ; "
                 "PV-10 -> DR 0106K line 15 Col. A ; PV-13 -> DR 0106K line 15 Col. B ; "
                 "NOTHING on the DR 0106 face consumes PV-12, PV-13(f) or PV-14"),
     "inputs": [], "outputs": ["K1-14", "K1-15"],
     "description": ("A SPEC THAT WIRES PART V LINE 14 INTO PART II OR PART III WILL BE WRONG. The apportioned "
                     "Colorado income lands on each nonresident owner's K-1 COLUMN B, and it is the K-1s - not "
                     "Part V - that build the Part II and Part III bases. Confirmed by the verifier: 'Part V line "
                     "14's dead end is real.' F14 governs whether K-1 lines 14/15 must be completed at all."),
     "exceptions": "F14: mandatory only for C-corp partners (1065); NEVER mandatory for any S-corp shareholder."},
    {"rule_id": "R-CO-SOURCING", "title": "F1 - partnership DIRECT SOURCING default vs S-corp MANDATORY receipts factor",
     "rule_type": "classification", "sort_order": 22,
     "formula": ("1065:  default = DIRECT SOURCING (Sec. 39-22-109); receipts factor only AT THE PARTNERSHIP'S "
                 "ELECTION (Sec. 39-22-203(1)(a)); mark line 11 'Other' when direct sourcing ; "
                 "1120S: MANDATORY receipts factor (Sec. 39-22-303.6) - no direct-sourcing option exists ; "
                 "Part V is REQUIRED anyway for a partnership with any C-corp / upper-tier-partnership partner"),
     "inputs": ["federal_return_type", "owners", "apportionment_method"], "outputs": ["sourcing_method"],
     "description": ("W1 - THE LARGEST SINGLE SCOPE LEVER ON THE COLORADO BUILD. Three sub-quirks: (1) A PARTNERSHIP "
                     "CAN BE RUNNING BOTH METHODS AT ONCE - 'The ORDINARY INCOME of a partnership will generally be "
                     "sourced using receipts-factor apportionment EVEN IF the partnership does not elect to apportion "
                     "and allocate all income using this method.' (2) Direct sourcing reaches ONLY nonresident "
                     "individuals, estates and trusts - 'it does not apply to any other types of partners, such as "
                     "partners that are corporations, upper-tier partnerships, or resident individuals' (except that "
                     "under a SALT Parity election it may be used for all nonresident partners included in the "
                     "return). (3) 'If a partnership has any such partners, it must complete Part V ... REGARDLESS OF "
                     "WHETHER IT ELECTS TO USE DIRECT SOURCING ... and checks the \"other\" box on line 11' - so line "
                     "11 = Other and a completed Part V can, and sometimes must, COEXIST. "
                     "CITATION NUANCE: Sec. 39-22-321 as printed is a DEFINITIONS section; the S-corp requirement is "
                     "DEFINITIONAL (no direct-sourcing alternative is defined for an S corp) rather than a "
                     "stand-alone command. Cite the DOR's sentence as the operative statement and Sec. 39-22-321(1)-(2) "
                     "as the underlying text, not the other way round. GIL 22-003 is cited BY NAME by the DR 0106K-I "
                     "for the partnership Column B rule - non-binding guidance; read before the W1 walk."),
     "exceptions": "F3: guaranteed payments (K-1 line 4 Col. B) NEVER leave direct sourcing, under Rule 39-22-109(3)(b)(xii)."},

    # ---- Part II composite -----------------------------------------------
    {"rule_id": "R-CO-COMPOSITE", "title": "Part II - composite base, tax and net tax (L12-L16)",
     "rule_type": "calculation", "sort_order": 30,
     "formula": ("L12 = SUM over INCLUDED nonresident owners of Col. B lines 1-3 + 5-13   [LINE 4 SKIPPED] ; "
                 "L13 = L12 x CO_COMPOSITE_RATE (4.4%) ; "
                 "L16 = L13 - min(L14 + L15, L13)   # 'The sum of lines 14 and 15 may not exceed the amount on line 13'"),
     "inputs": ["owners", "credits_dr0106cr_l38_col_c", "gross_conservation_easement_credit"],
     "outputs": ["L12", "L13", "L16"],
     "description": ("W4/W5. Guaranteed payments are EXCLUDED (line 4 is skipped): 'Do not include guaranteed "
                     "payments from line 4 of the Colorado K-1. Nonresident partners with Colorado-source guaranteed "
                     "payments must file their own Colorado income tax return.' Negative-income owners are excluded "
                     "ENTIRELY, not netted. L14 carries only credits 'allocated to the nonresident partners or "
                     "shareholders included in the composite return and applied toward tax on the composite return', "
                     "and only 'to the extent that the nonresident partner or shareholder could have ... claimed the "
                     "credit on a return they filed'; 'Do not include any amounts from Column B on this line.'"),
     "exceptions": "L15 (gross conservation easement, DR 1305G L33) is separate from the DR 0106CR -> R2 RED-defer."},
    {"rule_id": "R-CO-COMP-RECON", "title": "Composite reconciliation - SUM(K-1 L16) must equal DR 0106 L13",
     "rule_type": "validation", "sort_order": 31,
     "formula": "SUM(DR 0106K line 16 over all owners included in the composite return) == DR 0106 line 13",
     "inputs": ["owners"], "outputs": [],
     "description": ("W4. Verbatim: 'If a composite return is filed, the amount reported on line 13 of form DR 0106 "
                     "MUST EQUAL the sum of the amounts reported on line 16 of the Colorado K-1s (DR 0106K) of all "
                     "nonresident partners or shareholders included in the composite return.' "
                     "THIS IS NOT ARITHMETICALLY AUTOMATIC. Line 12 is an AGGREGATE base taxed ONCE at 4.4%; K-1 line "
                     "16 is computed PER OWNER and FLOORED AT ZERO. The two agree ONLY BECAUSE negative-income owners "
                     "are excluded from line 12 as well. Build the aggregate exclusion and the per-owner floor as ONE "
                     "RULE, and assert the equality as a FLOW ASSERTION, not a comment.")},

    # ---- Part III SALT Parity --------------------------------------------
    {"rule_id": "R-CO-PTET", "title": "Part III - SALT Parity (PTET) bases and tax (L17-L20)",
     "rule_type": "calculation", "sort_order": 40,
     "formula": ("L17 = SUM over RESIDENT owners (incl. PART-YEAR) of Col. A lines 1-3 + 5-13, positive only ; "
                 "L18 = SUM over NONRESIDENT owners of Col. B lines 1-3 + 5-13, positive only ; "
                 "L19 = L17 + L18 ; L20 = L19 x CO_PTET_RATE (4.4%) ; "
                 "EXCLUDE any partner that is a C corporation UNITARY with the partnership"),
     "inputs": ["owners", "salt_parity_election"], "outputs": ["L17", "L18", "L19", "L20"],
     "description": ("The statutory base maps EXACTLY onto lines 17/18 (Sec. 39-22-344(1), C.R.S.): for a RESIDENT, "
                     "(a)+(b) = ENTIRE income = Column A; for a NONRESIDENT, (a) only = Column B. Line 17 is the "
                     "resident's ENTIRE income, NOT just Colorado-source. TWO EXCLUSIONS A NAIVE SPEC WILL MISS: "
                     "guaranteed payments (K-1 line 4, skipped) and ANY OWNER WHOSE NET INCOME IS NEGATIVE - excluded "
                     "ENTIRELY, not netted. Plus the unitary-C-corp-partner exclusion, which removes that partner "
                     "from BOTH the election's reach AND the tax base."),
     "exceptions": ("The election does NOT propagate up or down a tier chain in either direction; a tiered partner "
                    "'cannot claim any credit or subtraction ... based on a SALT Parity Act election made by a "
                    "lower-tier partnership'. The credit passes THROUGH on DR 0106K line 25.")},
    {"rule_id": "R-CO-PTET-NOCR", "title": "Mode C - an electing entity may claim NO credits on its own return",
     "rule_type": "validation", "sort_order": 41,
     "formula": "mode == C  ->  DR 0106CR column C == 0  AND  DR 0106 line 14 == 0  AND  line 15 == 0",
     "inputs": ["salt_parity_election", "credits_dr0106cr_l38_col_c"], "outputs": [],
     "description": ("SALT Parity pub, verbatim: 'The electing pass-through entity may not claim any refundable or "
                     "nonrefundable credits on its return' (corroborated by Sec. 39-22-344(3), C.R.S.). The DR 0106CR "
                     "instruction confirms the mechanism: 'enter in column B the amount from column A and enter 0 "
                     "(zero) in column C. This procedure applies to any partnership or S corporation that is not "
                     "filing a composite return, INCLUDING ANY PARTNERSHIP OR S CORPORATION MAKING AN ELECTION UNDER "
                     "THE S A L T PARITY ACT.' All credits pass through to the owners instead.")},
    {"rule_id": "R-CO-PTET-RECON", "title": "PTET reconciliation - SUM(K-1 L16) must equal DR 0106 L20",
     "rule_type": "validation", "sort_order": 42,
     "formula": "SUM(DR 0106K line 16 over all owners) == DR 0106 line 20",
     "inputs": ["owners"], "outputs": [],
     "description": ("W4. DR 0106K-I: 'The total amounts entered on all Colorado K-1s must equal the total amounts "
                     "tax calculated and paid by the partnership filing the composite return or making the SALT "
                     "parity election.' Same one-rule construction as the composite reconciliation - the per-owner "
                     "floor at zero and the negative-owner exclusion from lines 17/18 are the same rule.")},
    {"rule_id": "R-CO-ELECTION", "title": "SALT Parity election mechanics, gating condition, and the CLOSED retroactive window",
     "rule_type": "conditional", "sort_order": 43,
     "formula": ("ELECTIVE, ANNUAL, IRREVOCABLE for the year, BINDING ON ALL OWNERS ; "
                 "elect via Box I | DR 1705 (any time before filing) | the SALT Parity box on DR 0106EP ; "
                 "gating: allowed ONLY in a year with a federal IRC Sec. 164 deduction LIMITATION ; "
                 "retroactive TY2018-2021: CLOSED 2024-06-30 - NO path may be built"),
     "inputs": ["salt_parity_election"], "outputs": ["mode"],
     "description": ("Sec. 39-22-343, C.R.S. THE GATING CONDITION IS A LIVE CHECK, NOT A CONSTANT: 'The election "
                     "allowed under subsection (1) of this section is only allowed in an income tax year where there "
                     "is a limitation on the deductions allowed to individuals under section 164 of the internal "
                     "revenue code.' CDOR treats the election as AVAILABLE FOR TY2025 (Box I is on the TY2025 form, "
                     "the TY2025 DR 1705 says 'irrevocable for tax year 2025', and the SALT Parity pub was reissued "
                     "October 2025). But if the federal SALT cap ever lapses, the election lapses with it. "
                     "Excluded owner: 'any partner that is a C corporation that is unitary with the partnership'. "
                     "An electing entity is NOT required to collect DR 0107 agreements."),
     "exceptions": "Retroactive TY2018-2021 elections -> R12 hard RED. The window expired 2024-06-30 and cannot reopen."},

    # ---- DR 0106K owner schedule -----------------------------------------
    {"rule_id": "R-CO-K1-COLA", "title": "DR 0106K Column A - the federal K-1 BOX maps (per module)",
     "rule_type": "calculation", "sort_order": 50,
     "formula": ("K-1 L1<-Box 1 | L2<-Box 2 | L3<-Box 3 ; "
                 "1065:  L4<-Box 4c ; L5<-Box 5+6a ; L6<-Box 7 ; L7<-Box 8+9a+10 ; L8<-Box 11 ; L12<-Box 12+13 ; "
                 "1120S: L4 = N/A    ; L5<-Box 4+5a ; L6<-Box 6 ; L7<-Box 7+8a+9 ; L8<-Box 10 ; L12<-Box 11+12"),
     "inputs": ["owners", "federal_return_type"], "outputs": ["K1-1", "K1-2", "K1-3", "K1-4", "K1-5", "K1-6",
                                                             "K1-7", "K1-8", "K1-12"],
     "description": ("F3 (line 4 N/A for an S corp) + the Sec. 179 deduction inside line 12. "
                     "THE K-1 BOX NUMBERS AND THE SCHEDULE K LINE NUMBERS ARE NOT THE SAME NAMESPACE - the DR 0106 "
                     "face pulls Schedule K LINE numbers and the DR 0106K-I pulls Schedule K-1 BOX numbers. For the "
                     "1065 they largely coincide; for the 1120-S they do too; but the mapping MUST be kept as two "
                     "separate tables or a transcription will silently cross them. "
                     "F8: the distributive-share ratio for modifications differs per module."),
     "exceptions": "Losses on lines 1, 2, 3, 8 and all federal deductions on line 12 are entered NEGATIVE."},
    {"rule_id": "R-CO-K1-COLB", "title": "DR 0106K Column B - who gets one, and under which sourcing rule (F1/F2/F9)",
     "rule_type": "classification", "sort_order": 51,
     "formula": ("resident owner -> NO Column B ; "
                 "1065 + owner_kind in {c_corp, partnership} -> Column B BLANK unless a SALT Parity election is made ; "
                 "1065 nonresident individual/estate/trust -> DIRECT SOURCING (default) or elected receipts factor ; "
                 "1120S every nonresident shareholder -> receipts factor, and if applicable Sec. 39-22-303.7"),
     "inputs": ["owners", "federal_return_type", "salt_parity_election"], "outputs": ["K1-colB"],
     "description": ("F2 verbatim - PARTNERSHIP: 'If the partnership has not made a SALT Parity Act election, leave "
                     "these lines in Column B BLANK for all partners that are corporations or partnerships.' S CORP: "
                     "'Complete lines 1 through 13 in Column B for EACH nonresident shareholder.' "
                     "F9 - the cross-reference itself forks: the S-corp Column B rule adds 'and, if applicable "
                     "section 39-22-303.7, C.R.S.' (mutual fund service corporations) -> R9 RED-defer."),
     "exceptions": "F3: line 4 Column B is ALWAYS Rule 39-22-109(3)(b)(xii) direct sourcing, with no formulary alternative."},
    {"rule_id": "R-CO-K1-L9", "title": "F7 - DR 0106K line 9 state income tax add-back, split DIFFERENTLY per module",
     "rule_type": "calculation", "sort_order": 52,
     "formula": ("1065  Col. A: owner_kind == c_corp      -> COLORADO income tax only ; else ALL state income taxes "
                 "REGARDLESS OF STATE (from 1065 page 1 line 14 'Taxes and licenses') ; "
                 "1120S Col. A: residency == resident     -> ALL state income taxes ; nonresident -> COLORADO only "
                 "(from 1120-S page 1 line 12 'Taxes and licenses') ; "
                 "BOTH Col. B: COLORADO income tax only ; "
                 "BOTH: accumulate line 9 of any Colorado K-1 received from a LOWER-TIER partnership"),
     "inputs": ["owners", "federal_return_type"], "outputs": ["K1-9"],
     "description": ("One of the load-bearing forks. THE SPLIT AXIS ITSELF DIFFERS: a partnership splits by PARTNER "
                     "TYPE (C-corp vs not), an S corporation splits by RESIDENCY (resident vs nonresident). Building "
                     "one from the other silently misstates the add-back for whole classes of owner. "
                     "Feeds DR 0106 line 4 (with line 11) and, owner-side, DR 0104 line 2."),
     "exceptions": ("[UNV-4](a) ERRATUM: the S-corp half says 'deducted by the S corporation on line 12 of I R S FORM "
                    "1065' TWICE. The Column B paragraph below each correctly says Form 1120-S. BUILD TO 1120-S "
                    "LINE 12. Do not 'fix' this back.")},
    {"rule_id": "R-CO-K1-L11", "title": "F15 - DR 0106K line 11 'Other Colorado additions'; the S corp has a FIFTH item",
     "rule_type": "calculation", "sort_order": 53,
     "formula": ("BOTH: non-Colorado state/local bond interest + unauthorized-alien labor (Sec. 39-22-529) + "
                 "discriminatory-club expenses (Sec. 44-3-418) + lower-tier line-11 amounts ; "
                 "1120S ONLY, additionally: foreign income/war-profits/excess-profits taxes deducted on 1120-S "
                 "line 12 ; "
                 "Col. B: unauthorized-alien and discriminatory-club go in at the FULL Column A amount (NOT "
                 "apportioned); the S-corp foreign-tax item takes the ordinary 'portion attributable to Colorado' rule"),
     "inputs": ["k1_col_a_line11_other_additions", "federal_return_type"], "outputs": ["K1-11"],
     "description": ("VERIFIER CORRECTION C7, HIGH SEVERITY. The research pass presented four items as shared. The "
                     "S-corp half enumerates a FIFTH - a FOREIGN-TAX ADD-BACK with NO partnership analogue. An S-corp "
                     "return built from the partnership half SILENTLY DROPS A REAL ADDITION. The authorities cited by "
                     "each half differ too: Secs. 39-22-104, 39-22-304, 39-22-322, 39-22-323 (S corp) vs Secs. "
                     "39-22-104, 39-22-202, 39-22-203 (partnership). "
                     "Bond interest 'does not include any amortization of the bond premium and is reduced by the "
                     "amount of the deductions required by the Internal Revenue Code to be allocated to the interest "
                     "income.' Feeds DR 0106 line 4 WITHOUT sign inversion.")},
    {"rule_id": "R-CO-K1-L13", "title": "F16 - DR 0106K line 13 'Colorado subtractions'; TWO different inventories",
     "rule_type": "calculation", "sort_order": 54,
     "formula": ("BOTH: U.S. government obligation interest + Colorado Marijuana Code Sec. 280E + Colorado Natural "
                 "Medicine Code Sec. 280E + state income tax refunds not previously deducted + lower-tier amounts ; "
                 "1065 ONLY: export-taxpayer foreign source income (Sec. 39-22-206) ; "
                 "1120S ONLY: wages/salaries disallowed federally under IRC Sec. 280C (own Column B rule) ; "
                 "refund item splits by C-corp-vs-non-C-corp (1065) or resident-vs-nonresident (1120S) ; "
                 "ENTERED NEGATIVE -> DR 0106 line 8 SIGN-INVERTED"),
     "inputs": ["k1_col_a_line13_co_subtractions", "federal_return_type"], "outputs": ["K1-13"],
     "description": ("VERIFIER CORRECTION C8, HIGH SEVERITY. The research pass merged the two halves into one list "
                     "and omitted an item entirely. Sec. 39-22-206 is BY ITS OWN TERMS a partnership provision ('If a "
                     "PARTNERSHIP qualifies as an export taxpayer, its PARTNERS may exclude...'), verified in CRS "
                     "2024, and is ABSENT from the S-corp half. Conversely the S-corp half carries a Sec. 280C "
                     "disallowed-wages subtraction with its OWN Column B rule ('to the extent the underlying or "
                     "related expenses or losses are from business activity in Colorado'). Each module built from the "
                     "other's list silently drops a real subtraction. "
                     "The refund item's Column B rule is the same in both halves: included 'to the extent the "
                     "underlying or related income is included on lines 1 through 8 in Column A'."),
     "exceptions": "DR 0106 line 8 EXCLUDES any marijuana / natural-medicine subtraction already reported on line 7."},
    {"rule_id": "R-CO-K1-L1415", "title": "F14 - when DR 0106K lines 14 and 15 are MANDATORY",
     "rule_type": "conditional", "sort_order": 55,
     "formula": ("1065:  REQUIRED for any partner that is (or is treated as) a C CORPORATION; optional otherwise ; "
                 "1120S: NEVER REQUIRED for any shareholder - optional only, on request ; "
                 "L14 Col. A = Part V L8 Everywhere x ratio ; Col. B = Part V L8 Colorado x ratio ; "
                 "L15 Col. A = Part V L10 x ratio ; Col. B = Part V L13 x ratio"),
     "inputs": ["owners", "federal_return_type"], "outputs": ["K1-14", "K1-15"],
     "description": ("VERIFIER CORRECTION C6. The research pass stated the partnership rule as if it were shared. "
                     "S corp, verbatim: 'The completion of lines 14 and 15 is NOT REQUIRED on a Colorado K-1 prepared "
                     "for ANY S corporation shareholder, unless the shareholder needs the information.'")},
    {"rule_id": "R-CO-K1-L16", "title": "DR 0106K line 16 - the PER-OWNER tax, FLOORED AT ZERO (three variants)",
     "rule_type": "calculation", "sort_order": 56,
     "formula": ("composite:            L16 = max(0, SUM(Col. B lines 1-3 + 5-13) x 4.4%) ; "
                 "SALT Parity resident: L16 = max(0, SUM(Col. A lines 1-3 + 5-13) x 4.4%)   [incl. PART-YEAR] ; "
                 "SALT Parity nonres.:  L16 = max(0, SUM(Col. B lines 1-3 + 5-13) x 4.4%) ; "
                 "F13 wording: partnership half says 'lines 1 through 3 and lines 5 through 13'; S-corp half says "
                 "'lines 1 through 13' - ARITHMETICALLY IDENTICAL (line 4 is N/A for an S corp)"),
     "inputs": ["owners", "salt_parity_election", "composite_return_filed"], "outputs": ["K1-16"],
     "description": ("W4. THE FLOOR: 'If the sum ... is a negative amount, ENTER 0 (ZERO) on line 16.' This floor and "
                     "the aggregate negative-owner exclusion in Parts II/III are ONE RULE - that is exactly why the "
                     "line-13 and line-20 reconciliations hold. Guaranteed payments (line 4) are skipped in all three "
                     "variants. Also: 'Do not enter on line 16 any amount that the partnership has not remitted to "
                     "the Department.' Statutory cross-references differ by module: composite line 16 cites "
                     "Sec. 39-22-601(5.5)(d)(III) (partnership half) vs (2.7)(d)(III) (S-corp half). "
                     "Owner-side landing point: DR 0104CR PART I (REFUNDABLE CREDITS) LINE 11."),
     "exceptions": "F13: do not assert one half's summation wording against the other document."},
    {"rule_id": "R-CO-OWNER-STAT", "title": "Owner-status derivation - residency tests and the six checkboxes",
     "rule_type": "classification", "sort_order": 57,
     "formula": ("individual: domiciled in Colorado OR (permanent place of abode in Colorado AND more than six "
                 "months of the year in Colorado) ; estate: administered in Colorado in a proceeding other than an "
                 "ancillary proceeding ; trust: administered in Colorado ; C corporation or partnership partner: "
                 "organized under Colorado law ; "
                 "PART-YEAR RESIDENT -> TREATED AS A RESIDENT ; "
                 "checkboxes: Resident / Non-Resident / Composite / DR 0107 / Excluded Nonresident / SALT Parity Election"),
     "inputs": ["owners"], "outputs": ["owner_status"],
     "description": ("The checkboxes drive everything downstream. PART-YEAR IS THE TRAP, verbatim: 'If a partner was "
                     "a resident for only part of the tax year, check the box to indicate that they were a RESIDENT "
                     "and complete the Colorado K-1 for the partner following the instructions for RESIDENT "
                     "partners.' A part-year owner therefore lands in the Part III line 17 (Column A, ENTIRE income) "
                     "base, and is EXCLUDED from the composite return. "
                     "When a SALT Parity election is made, mark the election box on EVERY DR 0106K.")},

    # ---- Part IV, rates, calendar, estimated tax -------------------------
    {"rule_id": "R-CO-PARTIV", "title": "Part IV - amount owed / overpayment (L21-L35)",
     "rule_type": "calculation", "sort_order": 60,
     "formula": ("L21 = L16 (Mode B) | L20 (Mode C) | 0 (Mode A) ; L24 = L21 + L22 + L23 ; "
                 "L28 = L25 + L26 + L27 ; "
                 "if L24 > L28: L32 = L24 - L28 + L29 + L30 + L31 ; "
                 "else: L33 = L28 - L24 ; L35 = L33 - L34"),
     "inputs": ["estimated_extension_payments_l25", "lottery_gambling_withholding_l26", "dr0619_credit_l27",
                "in_lieu_of_amount_l22", "dr0619_repayment_l23", "interest_l30", "estimated_tax_penalty_l31",
                "overpayment_credited_forward_l34"],
     "outputs": ["L21", "L24", "L28", "L32", "L33", "L35"],
     "description": ("Line 21 is the MODE JOIN. Line 22 (R7) is only on an AMENDED return after an IRS partnership "
                     "audit where the partnership elected under Sec. 39-22-601.5(3)(d) to pay in lieu of its direct "
                     "and indirect partners. Line 23 (R1) is NEW FOR TY2025 - the DR 0619 advance-payment clawback. "
                     "Line 30 interest accrues from the ORIGINAL due date, not the extended one.")},
    {"rule_id": "R-CO-RATES", "title": "TWO rate constants with SEPARATE statutory authorities - do not collapse",
     "rule_type": "calculation", "sort_order": 61,
     "formula": ("CO_COMPOSITE_RATE[2025] = 0.044   authority: C.R.S. Sec. 39-22-104 (INDIVIDUAL rate), via "
                 "Sec. 39-22-601(5.5)(d)(III)(A) / (2.7)(d)(III)(A)  -> DR 0106 line 13 ; "
                 "CO_PTET_RATE[2025]      = 0.044   authority: C.R.S. Sec. 39-22-301(1)(d)(I)(K) (CORPORATE rate), "
                 "via Sec. 39-22-344(1)                              -> DR 0106 line 20"),
     "inputs": [], "outputs": ["L13", "L20"],
     "description": ("W7. TWO DIFFERENT RATE STATUTES ON ONE FORM. Numerically identical for TY2025, so the "
                     "distinction is INVISIBLE THIS YEAR - which is precisely why a spec collapses them by accident. "
                     "Sec. 39-22-627 (the TABOR refund mechanism) moves both together TODAY, but they are separate "
                     "constants with separate authorities. TY2024 was reduced to 4.25% by a ONE-OFF DIRECTIVE at "
                     "Sec. 39-22-627(1)(c) naming TY2024 specifically; the general mechanism was NOT triggered for "
                     "TY2025 (LCS September 2025 forecast: 'will not be triggered in tax years 2025 or 2026', against "
                     "a Controller-certified $293.3M obligation vs the $300M first step), and SB25-138, which would "
                     "have made 4.25% permanent from TY2025, was POSTPONED INDEFINITELY 2025-02-27. FORWARD TRAP: the "
                     "same LCS forecast projects 4.33% for TY2027 and 4.29% for TY2028. KEY THE RATE TO THE TAX YEAR."),
     "exceptions": "DR 0106K line 16 uses '4.4% (0.044)' for both regimes - same value, different authority per mode."},
    {"rule_id": "R-CO-DUEDATE", "title": "Due date - 15th day of the FOURTH month; automatic 6-month extension; NO extension to pay",
     "rule_type": "calculation", "sort_order": 62,
     "formula": ("original = 15th day of the 4th month after the close of the tax year (April 15 for calendar year) ; "
                 "extension = AUTOMATIC 6 months (October 15) ; NO extension to pay (voucher DR 0158-N) ; "
                 "weekend or legal holiday -> next business day ; "
                 "Colorado K-1s are due the SAME DATE, including extension"),
     "inputs": [], "outputs": [],
     "description": ("VERIFIED AGAINST STATUTE rather than assumed to match the C corporation. "
                     "Sec. 39-22-608(2)(a): 'EXCEPT AS PROVIDED IN SUBSECTION (2)(b) ... on or before the FIFTEENTH "
                     "DAY OF THE FOURTH MONTH'. (2)(b) reaches only 'every C CORPORATION ... required by section "
                     "39-22-601 (2)'. The PTE return is filed under Sec. 39-22-601 (5.5)(a) / (2.7)(a), so (2)(b) "
                     "DOES NOT REACH IT. Corroborated by the form face, by Sec. 39-22-609(1) (payment, same month), "
                     "and by Sec. 39-22-601(5.5)(f) ('This subsection (5.5) applies to tax years beginning on and "
                     "after January 1, 2024'). "
                     "CONTRAST: the C-corp DR 0112 really IS a month later on both ends - May 15 / November 15 / "
                     "DR 0158-C. Do not inherit that calendar."),
     "exceptions": "DR 0158-N: 'IF NO PAYMENT IS DUE, DO NOT FILE THIS FORM.'"},
    {"rule_id": "R-CO-PENALTY", "title": "DR 0106 line 29 - delinquent-payment penalty, gated on the 90% test",
     "rule_type": "calculation", "sort_order": 63,
     "formula": ("if pct paid by the ORIGINAL due date >= 90%: no penalty ; else "
                 "pct = min(12%, 5% + 0.5% x (months_delinquent - 1)) ; "
                 "penalty = max($5, additional_tax x pct)"),
     "inputs": ["pct_tax_paid_by_original_due_date", "months_delinquent"], "outputs": ["L29"],
     "description": ("Verbatim: 'If 90% of the tax is not paid by the original due date (without extension) ... The "
                     "penalty is the GREATER OF $5 OR 5% of the additional tax due for the first month of delinquency "
                     "and 0.5% for each additional month UP TO A MAXIMUM OF 12%.' Also applies if the balance is "
                     "unpaid at the extension due date.")},
    {"rule_id": "R-CO-EST-TAX", "title": "Estimated tax (DR 0106EP / DR 0233) - PTE rules, NOT C-corp rules",
     "rule_type": "calculation", "sort_order": 64,
     "formula": ("required if net Colorado tax liability > $5,000  [W9 RULING - see below] ; "
                 "required annual amount = LESSER OF 70% of current-year net Colorado tax, or 100% of the preceding "
                 "year's - the 100% leg ONLY IF the preceding year was 12 months AND a Colorado return was filed AND "
                 "taxable income was under $1,000,000 in all three preceding years ; "
                 "AND, if making a SALT Parity election, ONLY IF an election was also made for that preceding year ; "
                 "large entity ($1,000,000+ in any of 3 preceding years): Q1 may use 25% of prior-year tax, but later "
                 "payments must use actual current-year tax and any Q1 underpayment is paid with Q2 ; "
                 "quarters: 15th day of the 4th, 6th, 9th and 12th month ; "
                 "penalty interest: 12% for dates in 2025, 11% for dates in 2026 -> DR 0233 L22 -> DR 0106 L31 ; "
                 "NO ANNUALIZED INCOME INSTALLMENT METHOD"),
     "inputs": ["prior_year_co_tax_liability", "prior_year_was_12_months", "filed_prior_year_co_return",
                "elected_salt_parity_prior_year", "prior_3yr_income_1m_or_more"], "outputs": ["L31"],
     "description": ("W9. TWO GENUINE PTE/C-CORP DIVERGENCES - do NOT inherit a C-corp estimated-tax module "
                     "wholesale: (1) the first-year-election prior-year block (DR 0233 line 6), which the C-corp rule "
                     "does not have; (2) NO annualized income installment method - 'Colorado law does not provide an "
                     "option for partnerships or S corporations to compute their estimated payments using an "
                     "annualized income installment method', while the Corporate Guide Part 9 expressly GRANTS it to "
                     "C corporations. "
                     "THE $5,000 THRESHOLD IS A LIVE 3-2 SOURCE SPLIT (verifier correction C9), NOT AN ERRATUM: "
                     "'exceeds' per the DR 0233 instructions, DR 0106EP and the SALT Parity pub; '>=' / 'less than "
                     "$5,000' per DR 0106 line 31 AND the Corporate Income Tax Guide, which the DR 0106 EXPRESSLY "
                     "INCORPORATES BY REFERENCE for exactly this rule. Exposure is the single point net tax == "
                     "$5,000. Built STRICTLY GREATER THAN, because DR 0233 Part 1 computes 'line 1 - $5,000; If line "
                     "2 is larger, enter zero and no penalty is due' - the form's own arithmetic is the tiebreak. "
                     "RULED BY KEN 2026-08-17 (Gate-1 walk item B2). Recorded AS A RULING ON A SOURCE SPLIT, "
                     "NOT as a correction of an erratum."),
     "exceptions": ("No estimated tax penalty is due 'if the Department determines that the underpayment was due to "
                    "good cause shown by the taxpayer'. Short/fiscal periods -> R13 RED-defer.")},

    # ---- credits, owner-side handoff, transmittal, blocker ---------------
    {"rule_id": "R-CO-CR-COLS", "title": "DR 0106CR column arithmetic - L38 = SUM(L5..L37), and the Column-C rule",
     "rule_type": "calculation", "sort_order": 70,
     "formula": ("L38 = SUM(lines 5 through 37) for EACH of columns A, B, C   # NOT 1..37 ; "
                 "not filing composite (Mode A or Mode C) -> column B = column A and column C = 0 ; "
                 "L38 column C -> DR 0106 line 14, capped so that L14 + L15 <= L13"),
     "inputs": ["credits_dr0106cr_l38_col_c", "salt_parity_election", "composite_return_filed"], "outputs": ["L14"],
     "description": ("W10. VERIFIER ADDITION - line 38 is 'Sum lines 5 through 37 for columns A, B, and C', NOT "
                     "1 through 37: lines 1-4 are the recapture and other-state-tax block and are EXCLUDED from the "
                     "total. The DR 0106CR is a MANDATORY ATTACHMENT ON EVERY RETURN, including Modes A and C. "
                     "ALSO A VERIFIER ADDITION - DR 0106CR LINES 2-4, CREDIT FOR TAX PAID TO OTHER STATES: 'A partner "
                     "or shareholder who is a Colorado resident individual may claim credit for their share of any "
                     "net income tax imposed upon and paid to another state by the partnership or S corporation. THIS "
                     "CREDIT IS ALLOWED EVEN IF THE IMPOSITION UPON THE PARTNERSHIP OR S CORPORATION WAS AT THE "
                     "PARTNERSHIP'S OR S CORPORATION'S ELECTION.' Filed on a SEPARATE DR 0106CR PER STATE. This is "
                     "the path by which ANOTHER STATE'S PTET reaches a Colorado resident owner - a real multi-state "
                     "interaction the campaign will hit repeatedly. Treat as DIRECT-ENTRY with a multi-instance "
                     "schedule in v1."),
     "exceptions": "Every credit sub-schedule is RED-deferred: R2, R3, R4, R5, R6."},
    {"rule_id": "R-CO-OWNER-SIDE", "title": "Owner-side handoff records (DR 0104 / DR 0104CR)",
     "rule_type": "routing", "sort_order": 71,
     "formula": ("DR 0106K L9  -> DR 0104 line 2  'State Income Tax Addback' ; "
                 "election-forced Sec. 199A add-back -> DR 0104 line 3 'Qualified Business Income Deduction Addback' ; "
                 "DR 0106K L10 -> DR 0104 line 5  'Business meals deducted pursuant to section 274(k)' ; "
                 "DR 0106K L16 -> DR 0104CR PART I (REFUNDABLE CREDITS) line 11 ; "
                 "DR 0106K L25 -> the owner's own DR 0104CR / DR 0106K (lower-tier SALT Parity credit)"),
     "inputs": ["owners", "salt_parity_election"], "outputs": [],
     "description": ("The SALT Parity election REACHES BACKWARD INTO EVERY OWNER'S INDIVIDUAL RETURN - a refundable "
                     "credit, a forced FULL Sec. 199A add-back regardless of AGI, and the state-tax add-back. The "
                     "Colorado individual and PTE specs CANNOT be authored independently of each other. "
                     "NOTE DR 0104CR Part I line 11 is the SAME LINE for the composite payment and the PTET credit - "
                     "the individual return does not distinguish them. The credit is REFUNDABLE: 'Any amount of the "
                     "credit ... that exceeds the electing pass-through entity owner's income taxes due is REFUNDED' "
                     "(Sec. 39-22-347(4), C.R.S.). "
                     "Interaction the conformity brief flagged: the DR 0104 line-4 itemized/standard add-back is "
                     "reduced by the line-2 add-back EXCEPT the portion attributable to a partnership/S-corp deduction."),
     "exceptions": "A composite return satisfies the owner's filing requirement only if they have no other Colorado-source income or liability."},
    {"rule_id": "R-CO-K1-TRANSMIT", "title": "Colorado K-1 transmittal is a SEPARATE submission - never an attachment",
     "rule_type": "routing", "sort_order": 72,
     "formula": ("five channels: MeF (K-1s inside the return submission) | XLS upload to Revenue Online | XML upload "
                 "| manual entry in Revenue Online | paper with the DR 1706 cover sheet ; "
                 "NEVER as an attachment to a paper DR 0106, and NEVER as a PDF attachment to an MeF submission ; "
                 "DR 1706 is not needed when filing the DR 0106Ks electronically ; "
                 "due the same date as the return, including extension (April 15, 2026 for calendar-year 2025)"),
     "inputs": [], "outputs": [],
     "description": ("W8. Verbatim: 'Do not submit the copies of the Colorado K-1s issued to partners or shareholders "
                     "(or the DR 1706 transmittal form) AS AN ATTACHMENT to a paper income tax return (form DR 0106, "
                     "OR AS A PDF ATTACHMENT TO AN MeF INCOME TAX RETURN).' Electronic submission requires a "
                     "web-submitter registration with CDOR. Owners must be furnished their copies ON OR BEFORE the "
                     "date the K-1s are filed with the Department. Whether the Colorado MeF DR 0106 schema carries "
                     "the DR 0106K records inline CANNOT BE VERIFIED TODAY - [UNV-6], LOI-gated."),
     "exceptions": ("Mailing-address conflict, recorded so nobody treats it as a transcription slip: the DR 0106K-I "
                    "says Denver, CO 80261-0006; the DR 1706 face says 80261-0005. Resolve with CDOR if v1 ever "
                    "prints the paper path.")},
    {"rule_id": "R-CO-174A-CONFORM", "title": "Retroactive federal amendments ARE picked up under rolling conformity (RULED, [UNV-7])",
     "rule_type": "validation", "sort_order": 99,
     "formula": ("DR 0106 line 1 = federal ordinary income AS FILED. Do NOT compute a Sec. 174A adjustment in "
                 "either direction. Raise D_CO106_BLOCK_174A_CONFORMITY (info) to disclose the basis."),
     "inputs": ["claims_retroactive_sec174a_election"], "outputs": [],
     "description": ("W13 / walk item A1 - RULED BY KEN 2026-08-17. Colorado's conformity is ROLLING "
                     "(Sec. 39-22-103(5.3), C.R.S.: the IRC 'as the same may become effective at any time or from "
                     "time to time, for the taxable year'). THE RULING: that language reaches RETROACTIVELY-EFFECTIVE "
                     "federal amendments, so OBBBA's retroactive small-business Sec. 174A R&D expensing election "
                     "flows through to DR 0106 line 1 exactly as it appears on the federal return. "
                     "THE DECIDING STRUCTURAL FACT: the DR 0106 has NO Colorado modification line anywhere on its "
                     "face. The form is physically incapable of carrying a divergence between Colorado and federal "
                     "ordinary income, so the only position the form can express is the one ruled here. "
                     "WHAT IS STILL OPEN, AND IT IS NOT A COMPUTATION QUESTION: no CDOR source confirms the ruling. "
                     "CDOR's Rule 39-22-103(5.3) - the rule that read conformity as prospective-only - now shows as "
                     "'[Repealed]' with no substantive text retained, and the Colorado Court of Appeals decision said "
                     "to hold the opposite (the Anschutz CARES Act excess-business-loss litigation) is known only "
                     "from SECONDARY REPORTING. The ruling is Ken's reading of the statute. "
                     "WOULD CONFIRM IT: the published Anschutz opinion(s) from coloradojudicial.gov; the current "
                     "1 CCR 201-2 text showing the rule's repeal date; or CDOR guidance on Sec. 174A for TY2025. "
                     "Re-verify before the delvio-tax module ships. [UNV-7] stays open."),
     "exceptions": ("If CDOR later confirms Colorado does NOT pick up retroactive amendments, this form cannot "
                    "express the result and the divergence must be escalated - there is no line to put it on.")},
]

CO_RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R-CO-MODULE-FORK", "CO_2025_DR0106K_I", "primary", "the two instruction halves ARE the fork"),
    ("R-CO-MODULE-FORK", "CO_2025_DR0106", "secondary", "Box A is legal form, not tax classification"),
    ("R-CO-MODE", "CO_2025_DR0106", "primary", "line 21 mutual-exclusivity instruction, verbatim"),
    ("R-CO-MODE", "CO_CRS_39_22_344", "primary", "Sec. 39-22-344(5) statutory basis for mutual exclusivity"),
    ("R-CO-COMP-REQ", "CO_CRS_39_22_601", "primary", "(5.5)(d)(I)/(2.7)(d)(I) mandatory; (VII) carve-outs incl. C1"),
    ("R-CO-COMP-REQ", "CO_2025_DR0106", "secondary", "the four-exclusion list plus the fifth at line 12"),
    ("R-CO-L1", "CO_2025_DR0106", "primary", "line 1 instruction (F12 erratum: names only the 1065)"),
    ("R-CO-L1", "IRS_2025_1065_INSTR", "implementation", "1065 Sch. K line 1 handoff"),
    ("R-CO-L1", "IRS_2025_1120S_INSTR", "implementation", "1120-S Sch. K line 1 handoff"),
    ("R-CO-L2-FED179", "CO_2025_DR0106", "primary", "line 2 instruction incl. the Sec. 179-disposition sentence"),
    ("R-CO-L2-FED179", "IRS_2025_1065_INSTR", "implementation", "1065 Sch. K 2/3c/4c/5/6a/7/8/9a/10/11 + 20c"),
    ("R-CO-L2-FED179", "IRS_2025_1120S_INSTR", "implementation", "1120-S Sch. K 2/3c/4/5a/6/7/8a/9/10 + 17d"),
    ("R-CO-L3-L4-NOFLIP", "CO_2025_DR0106", "primary", "lines 3 and 4 are K-1 Col. A aggregations, already positive"),
    ("R-CO-L3-L4-NOFLIP", "CO_2025_DR0106K_I", "primary", "K-1 additions on lines 9/10/11 are positive"),
    ("R-CO-SIGNFLIP", "CO_2025_DR0106K_I", "primary", "'as negative amounts' / 'line 13 as a negative amount'"),
    ("R-CO-SIGNFLIP", "CO_2025_DR0106", "primary", "'Enter the deductions on this line 6/8 as a positive number'"),
    ("R-CO-SIGNFLIP", "IRS_2025_1065_K1_INSTR", "implementation", "1065 K-1 Box 12 IS the Sec. 179 deduction"),
    ("R-CO-SIGNFLIP", "IRS_2025_1120S_K1_INSTR", "implementation", "1120-S K-1 Box 11 IS the Sec. 179 deduction"),
    ("R-CO-L5-L10", "CO_2025_DR0106", "primary", "L5 = L1..L4; L9 = L6..L8; L10 = L5 - L9; Part I is entity-wide"),
    ("R-CO-DEPR-NEG", "CO_CRS_39_22_103", "primary", "rolling conformity + the Title 39 depreciation negative"),
    ("R-CO-DEPR-NEG", "CO_CORP_TAX_GUIDE_2026", "secondary", "complete addition list contains no depreciation item"),
    ("R-CO-DEPR-NEG", "CO_2025_DR0106", "secondary", "ModDate 2025-10-13, post-OBBBA, still no modification line"),
    ("R-CO-BOXBC", "CO_2025_DR0106", "primary", "Box B/C instruction, net of accumulated depreciation"),
    ("R-CO-BOXBC", "IRS_2025_1120S_SCHL_INSTR", "implementation", "Sch. L line 10b cols (b)/(d); 1065 line 9b"),
    ("R-CO-PARTV", "CO_2025_DR0106", "primary", "Part V face, lines 1-15 incl. the Sec. 39-22-303.6(8) election"),
    ("R-CO-PARTV-FEED", "CO_2025_DR0106K_I", "primary", "Part V L8/L10/L13 -> K-1 lines 14 and 15"),
    ("R-CO-PARTV-FEED", "CO_2025_DR0106", "secondary", "nothing on the face consumes PV L12/L13(f)/L14"),
    ("R-CO-SOURCING", "CO_2025_DR0106", "primary", "pp. 3-4 direct sourcing vs mandatory receipts factor"),
    ("R-CO-SOURCING", "CO_GIL_22_003", "interpretive", "cited by name for partnership Column B sourcing (W1)"),
    ("R-CO-COMPOSITE", "CO_2025_DR0106", "primary", "Part II lines 12-16 verbatim, incl. the L14+L15 cap"),
    ("R-CO-COMPOSITE", "CO_CRS_39_22_601", "primary", "(5.5)(d)(III)(A) base and the Sec. 39-22-104 rate cite"),
    ("R-CO-COMP-RECON", "CO_2025_DR0106", "primary", "line 13 reconciliation instruction, verbatim"),
    ("R-CO-COMP-RECON", "CO_2025_DR0106K_I", "primary", "K-1 line 16 per-owner floor at zero"),
    ("R-CO-PTET", "CO_CRS_39_22_344", "primary", "Sec. 39-22-344(1)(a)/(b) maps exactly onto lines 17/18"),
    ("R-CO-PTET", "CO_2025_DR0106", "primary", "Part III lines 17-20 verbatim"),
    ("R-CO-PTET", "CO_ITT_SALT_PARITY_2025", "secondary", "guaranteed-payment and negative-owner exclusions"),
    ("R-CO-PTET-NOCR", "CO_ITT_SALT_PARITY_2025", "primary", "'may not claim any refundable or nonrefundable credits'"),
    ("R-CO-PTET-NOCR", "CO_2025_DR0106CR", "primary", "not-composite -> column B = column A, column C = 0"),
    ("R-CO-PTET-RECON", "CO_2025_DR0106K_I", "primary", "'must equal the total amounts tax calculated and paid'"),
    ("R-CO-ELECTION", "CO_CRS_39_22_343_ELECT", "primary", "election mechanics, Sec. 164 gate, closed window"),
    ("R-CO-ELECTION", "CO_ITT_SALT_PARITY_2025", "secondary", "unitary-C-corp exclusion; tiered-partner independence"),
    ("R-CO-K1-COLA", "CO_2025_DR0106K_I", "primary", "the two federal K-1 box maps"),
    ("R-CO-K1-COLA", "CO_2025_DR0106K", "secondary", "DR 0106K face lines 1-16"),
    ("R-CO-K1-COLB", "CO_2025_DR0106K_I", "primary", "F2 Column B population rules, both halves"),
    ("R-CO-K1-L9", "CO_2025_DR0106K_I", "primary", "F7 - the two different split axes, verbatim"),
    ("R-CO-K1-L11", "CO_2025_DR0106K_I", "primary", "F15 - the S-corp foreign-tax add-back (C7)"),
    ("R-CO-K1-L13", "CO_2025_DR0106K_I", "primary", "F16 - export-taxpayer vs Sec. 280C wages (C8)"),
    ("R-CO-K1-L1415", "CO_2025_DR0106K_I", "primary", "F14 - never mandatory for an S-corp shareholder (C6)"),
    ("R-CO-K1-L16", "CO_2025_DR0106K_I", "primary", "three variants, all floored at zero; F13 wording"),
    ("R-CO-K1-L16", "CO_CRS_39_22_347_CREDIT", "secondary", "the credit is barred unless actually remitted"),
    ("R-CO-OWNER-STAT", "CO_2025_DR0106K_I", "primary", "residency tests; part-year treated as resident"),
    ("R-CO-OWNER-STAT", "CO_2025_DR0106K", "secondary", "the six owner-status checkboxes"),
    ("R-CO-PARTIV", "CO_2025_DR0106", "primary", "Part IV lines 21-35 verbatim"),
    ("R-CO-RATES", "CO_CRS_39_22_301_RATE", "primary", "PTET rate - the CORPORATE statute (line 20)"),
    ("R-CO-RATES", "CO_CRS_39_22_104_RATE", "primary", "composite rate - the INDIVIDUAL statute (line 13)"),
    ("R-CO-RATES", "CO_2025_DR0106", "secondary", "4.4% printed on the face at lines 13 and 20"),
    ("R-CO-DUEDATE", "CO_CRS_39_22_608_DUE", "primary", "Sec. 39-22-608(2)(a) vs (2)(b), verbatim"),
    ("R-CO-DUEDATE", "CO_2025_DR0106", "secondary", "April 15 / automatic 6 months / no extension to pay"),
    ("R-CO-PENALTY", "CO_2025_DR0106", "primary", "line 29 penalty text, verbatim"),
    ("R-CO-EST-TAX", "CO_2025_DR0233", "primary", "70%/100%, first-year block, no annualized method, interest"),
    ("R-CO-EST-TAX", "CO_CORP_TAX_GUIDE_2026", "secondary", "C9 - the other side of the $5,000 3-2 split"),
    ("R-CO-CR-COLS", "CO_2025_DR0106CR", "primary", "L38 = SUM(L5..L37); the column rule; lines 2-4"),
    ("R-CO-OWNER-SIDE", "CO_CRS_39_22_347_CREDIT", "primary", "refundable credit -> DR 0104CR Part I line 11"),
    ("R-CO-OWNER-SIDE", "CO_ITT_SALT_PARITY_2025", "primary", "forced full Sec. 199A add-back on every owner"),
    ("R-CO-OWNER-SIDE", "CO_2025_INDIV_TAX_GUIDE", "secondary", "the owner-side add-back stack (DR 0104 L2/L3/L5)"),
    ("R-CO-K1-TRANSMIT", "CO_2025_DR0106K_I", "primary", "the five channels and the 'not an attachment' rule"),
    ("R-CO-174A-CONFORM", "CO_CRS_39_22_103", "primary", "Sec. 39-22-103(5.3) rolling conformity - the ruled reach (A1)"),
    # The ruling's own-file link: DR 0106 LINE 1 is the affected line, and the
    # DR 0106 carries NO modification line anywhere to absorb a divergence -- the
    # structural fact the A1 ruling turns on. Kept so the rule still has an
    # authority link when CO_CRS_39_22_103 (a prod-seeded conformity source) is
    # absent, e.g. in a throwaway validation DB.
    ("R-CO-174A-CONFORM", "CO_2025_DR0106", "secondary", "line 1 is the affected line; no modification line exists to carry a divergence"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM — CO_DR0106 : LINES
# Namespaces (line_number cap is 20 chars):
#   "1".."35"        DR 0106 face
#   "PV-*"           Part V (receipts factor)
#   "K1-*"           DR 0106K (the owner schedule)
#   "BOX-*"          the return-level boxes
# ═══════════════════════════════════════════════════════════════════════════

CO_LINES: list[dict] = [
    # ---- Part I ----------------------------------------------------------
    {"line_number": "1", "description": "Ordinary income from federal Schedule K", "line_type": "input",
     "source_facts": ["fed_schedule_k"], "source_rules": ["R-CO-L1"], "sort_order": 1,
     "notes": "F12: the instruction names ONLY the 1065. Build to both modules."},
    {"line_number": "2", "description": "Sum of all other income (incl. the Sec. 179-disposition aggregation)",
     "line_type": "calculated", "calculation": "R-CO-L2-FED179",
     "source_facts": ["fed_schedule_k", "sec179_disposition_gain"], "source_rules": ["R-CO-L2-FED179"], "sort_order": 2,
     "notes": "F4 + F5. SEC. 179 TOUCHPOINT (i). Excludes Sch. K 12/13 (1065) and 11/12 (1120-S)."},
    {"line_number": "3", "description": "Business meals deducted pursuant to section 274(k) of the Internal Revenue Code",
     "line_type": "calculated", "source_facts": ["k1_col_a_line10_business_meals"],
     "source_rules": ["R-CO-L3-L4-NOFLIP"], "sort_order": 3,
     "notes": "K-1 Col. A line 10 aggregation. ALREADY POSITIVE - do NOT invert."},
    {"line_number": "4", "description": "Other modifications increasing federal income", "line_type": "calculated",
     "source_facts": ["k1_col_a_line9_state_tax_addback", "k1_col_a_line11_other_additions"],
     "source_rules": ["R-CO-L3-L4-NOFLIP"], "sort_order": 4,
     "notes": "K-1 Col. A lines 9 AND 11. ALREADY POSITIVE - do NOT invert. F7 and F15 fork the contents."},
    {"line_number": "5", "description": "Sum of lines 1 through 4", "line_type": "subtotal",
     "source_rules": ["R-CO-L5-L10"], "sort_order": 5},
    {"line_number": "6", "description": "Allowable deductions from federal Schedule K (SIGN-INVERTED K-1 line 12)",
     "line_type": "calculated", "calculation": "R-CO-SIGNFLIP",
     "source_facts": ["k1_col_a_line12_federal_deductions"], "source_rules": ["R-CO-SIGNFLIP"], "sort_order": 6,
     "notes": "THE SIGN FLIP + SEC. 179 TOUCHPOINT (ii). Face label and instruction DISAGREE - the INSTRUCTION "
              "GOVERNS: line 6 is a K-1 aggregation, not a direct federal Sch. K read."},
    {"line_number": "7", "description": "Colorado Marijuana and Natural Medicine Business Deduction",
     "line_type": "input", "source_facts": ["marijuana_natural_medicine_deduction"],
     "source_rules": ["R-CO-SIGNFLIP"], "sort_order": 7,
     "notes": "Direct-entry, POSITIVE. Requires a pro forma federal return computed without regard to IRC Sec. 280E."},
    {"line_number": "8", "description": "Other modifications decreasing federal income (SIGN-INVERTED K-1 line 13)",
     "line_type": "calculated", "calculation": "R-CO-SIGNFLIP",
     "source_facts": ["k1_col_a_line13_co_subtractions"], "source_rules": ["R-CO-SIGNFLIP"], "sort_order": 8,
     "notes": "THE SIGN FLIP. EXCLUDES any marijuana/natural-medicine amount already on line 7. F16 forks the contents."},
    {"line_number": "9", "description": "Sum of lines 6 through 8", "line_type": "subtotal",
     "source_rules": ["R-CO-L5-L10"], "sort_order": 9},
    {"line_number": "10", "description": "Modified federal taxable income, subtract line 9 from line 5",
     "line_type": "subtotal", "source_rules": ["R-CO-L5-L10"], "sort_order": 10,
     "destination_form": "CO_DR0106 Part V line 1",
     "notes": "ENTITY-WIDE (all owners). Feeds ONLY Part V line 1 - NOT Part II and NOT Part III."},
    {"line_number": "11", "description": "Apportionment and allocation method (Part V / Other / all Colorado)",
     "line_type": "informational", "source_facts": ["apportionment_method"], "source_rules": ["R-CO-SOURCING"],
     "sort_order": 11, "notes": "F1. A direct-sourcing partnership marks 'Other' - and may still have to complete Part V."},

    # ---- Part II ---------------------------------------------------------
    {"line_number": "12", "description": "Colorado-source income of nonresident partners or shareholders in the composite filing",
     "line_type": "calculated", "source_facts": ["owners"], "source_rules": ["R-CO-COMPOSITE"], "sort_order": 12,
     "notes": "Col. B lines 1-3 + 5-13 over INCLUDED owners. LINE 4 (guaranteed payments) SKIPPED; negative-income owners excluded."},
    {"line_number": "13", "description": "Tax; 4.4% of the amount on line 12", "line_type": "calculated",
     "source_rules": ["R-CO-COMPOSITE", "R-CO-RATES", "R-CO-COMP-RECON"], "sort_order": 13,
     "notes": "COMPOSITE rate - authority C.R.S. Sec. 39-22-104 (INDIVIDUAL rate). Must equal SUM(K-1 line 16)."},
    {"line_number": "14", "description": "Credits from the DR 0106CR line 38 column C", "line_type": "input",
     "source_facts": ["credits_dr0106cr_l38_col_c"], "source_rules": ["R-CO-CR-COLS"], "sort_order": 14,
     "notes": "MUST BE ZERO in Modes A and C. 'Do not include any amounts from Column B on this line.'"},
    {"line_number": "15", "description": "Gross Conservation Easement credit (DR 1305G line 33)", "line_type": "input",
     "source_facts": ["gross_conservation_easement_credit"], "sort_order": 15, "notes": "R2 RED-defer."},
    {"line_number": "16", "description": "Net tax; line 13 less (line 14 + line 15), the sum capped at line 13",
     "line_type": "calculated", "source_rules": ["R-CO-COMPOSITE"], "sort_order": 16},

    # ---- Part III --------------------------------------------------------
    {"line_number": "17", "description": "Resident partners' or shareholders' total share of income (Column A)",
     "line_type": "calculated", "source_facts": ["owners"], "source_rules": ["R-CO-PTET"], "sort_order": 17,
     "notes": "ENTIRE income, not just Colorado-source. Part-year owners count as RESIDENTS. Negative owners excluded entirely."},
    {"line_number": "18", "description": "Colorado-source income of nonresident partners or shareholders (Column B)",
     "line_type": "calculated", "source_facts": ["owners"], "source_rules": ["R-CO-PTET"], "sort_order": 18},
    {"line_number": "19", "description": "Colorado taxable income of partnership or S corporation, sum of lines 17 and 18",
     "line_type": "subtotal", "source_rules": ["R-CO-PTET"], "sort_order": 19},
    {"line_number": "20", "description": "Net Tax; 4.4% of the amount on line 19", "line_type": "calculated",
     "source_rules": ["R-CO-PTET", "R-CO-RATES", "R-CO-PTET-RECON"], "sort_order": 20,
     "notes": "PTET rate - authority C.R.S. Sec. 39-22-301 (CORPORATE rate). A DIFFERENT statute from line 13."},

    # ---- Part IV ---------------------------------------------------------
    {"line_number": "21", "description": "Enter the amount from line 16 or line 20, whichever applies (THE MODE JOIN)",
     "line_type": "calculated", "source_rules": ["R-CO-MODE", "R-CO-PARTIV"], "sort_order": 21,
     "notes": "MODE A -> 0. Parts II and III may never both be completed."},
    {"line_number": "22", "description": "In-lieu-of amount under Sec. 39-22-601.5(3)(e) for a partnership audit adjustment",
     "line_type": "input", "source_facts": ["in_lieu_of_amount_l22"], "sort_order": 22,
     "notes": "R7 / [UNV-8] - NO published computation anywhere. Amended returns only."},
    {"line_number": "23", "description": "Repayment of credit from form DR 0619, lines 4 and 11", "line_type": "input",
     "source_facts": ["dr0619_repayment_l23"], "sort_order": 23, "notes": "R1. NEW for TY2025."},
    {"line_number": "24", "description": "Net Tax, In-Lieu-of Amount, and Required Repayment; sum of lines 21, 22, and 23",
     "line_type": "subtotal", "source_rules": ["R-CO-PARTIV"], "sort_order": 24},
    {"line_number": "25", "description": "Estimated tax, extension payments, and credits", "line_type": "input",
     "source_facts": ["estimated_extension_payments_l25"], "sort_order": 25,
     "notes": "Incl. DR 0158-N extension payments and DR 1079 real-estate withholding (R10)."},
    {"line_number": "26", "description": "Withholding from lottery or gambling winnings", "line_type": "input",
     "source_facts": ["lottery_gambling_withholding_l26"], "sort_order": 26},
    {"line_number": "27", "description": "Additional credit from form DR 0619, lines 3 and 10", "line_type": "input",
     "source_facts": ["dr0619_credit_l27"], "sort_order": 27, "notes": "R1."},
    {"line_number": "28", "description": "Subtotal; sum of lines 25, 26, and 27", "line_type": "subtotal",
     "source_rules": ["R-CO-PARTIV"], "sort_order": 28},
    {"line_number": "29", "description": "Penalty (include on line 32)", "line_type": "calculated",
     "source_facts": ["pct_tax_paid_by_original_due_date", "months_delinquent"],
     "source_rules": ["R-CO-PENALTY"], "sort_order": 29,
     "notes": "Gated on the 90% test. Greater of $5 or 5% first month + 0.5%/month, max 12%."},
    {"line_number": "30", "description": "Interest (include on line 32)", "line_type": "input",
     "source_facts": ["interest_l30"], "sort_order": 30, "notes": "Runs from the ORIGINAL due date."},
    {"line_number": "31", "description": "Estimated Tax Penalty (DR 0233 line 22) (include on line 32)",
     "line_type": "input", "source_facts": ["estimated_tax_penalty_l31"], "source_rules": ["R-CO-EST-TAX"],
     "sort_order": 31, "notes": "W9: the >$5,000 threshold is a Ken ruling on a 3-2 source split."},
    {"line_number": "32", "description": "If line 24 is greater than line 28, enter amount owed", "line_type": "total",
     "source_rules": ["R-CO-PARTIV"], "sort_order": 32},
    {"line_number": "33", "description": "Overpayment, subtract line 24 from line 28", "line_type": "subtotal",
     "source_rules": ["R-CO-PARTIV"], "sort_order": 33},
    {"line_number": "34", "description": "Overpayment to be credited to the next year's estimated tax",
     "line_type": "input", "source_facts": ["overpayment_credited_forward_l34"], "sort_order": 34},
    {"line_number": "35", "description": "Overpayment to be refunded", "line_type": "total",
     "source_rules": ["R-CO-PARTIV"], "sort_order": 35},

    # ---- Part V ----------------------------------------------------------
    {"line_number": "PV-1", "description": "Part V - total modified federal taxable income from Part I line 10",
     "line_type": "calculated", "source_rules": ["R-CO-PARTV"], "sort_order": 40,
     "notes": "The ONLY feed from Part I."},
    {"line_number": "PV-2", "description": "Part V - gross receipts from the sale of tangible personal property (CO / Everywhere)",
     "line_type": "input", "source_facts": ["receipts_colorado", "receipts_everywhere"], "sort_order": 41},
    {"line_number": "PV-3", "description": "Part V - gross receipts from the sale of services", "line_type": "input",
     "source_facts": ["receipts_colorado", "receipts_everywhere"], "sort_order": 42},
    {"line_number": "PV-4", "description": "Part V - gross receipts from the sale, rental, lease, or license of real property",
     "line_type": "input", "source_facts": ["receipts_colorado", "receipts_everywhere"], "sort_order": 43},
    {"line_number": "PV-5", "description": "Part V - gross receipts from the rental, lease, or license of tangible personal property",
     "line_type": "input", "source_facts": ["receipts_colorado", "receipts_everywhere"], "sort_order": 44},
    {"line_number": "PV-6", "description": "Part V - gross receipts from the sale, rental, lease, or license of intangible property",
     "line_type": "input", "source_facts": ["receipts_colorado", "receipts_everywhere"], "sort_order": 45},
    {"line_number": "PV-7", "description": "Part V - distributive share of partnership factors (tiered-entity flow-up)",
     "line_type": "input", "source_facts": ["receipts_colorado", "receipts_everywhere"], "sort_order": 46},
    {"line_number": "PV-8", "description": "Part V - total receipts (lines 2 through 7 in each column)",
     "line_type": "subtotal", "source_rules": ["R-CO-PARTV"], "sort_order": 47,
     "destination_form": "CO_DR0106 K-1 line 14", "notes": "Feeds DR 0106K line 14, both columns (F14 governs when required)."},
    {"line_number": "PV-9", "description": "Part V - line 8 (Colorado) divided by line 8 (Everywhere), as a percent",
     "line_type": "calculated", "source_rules": ["R-CO-PARTV"], "sort_order": 48,
     "notes": "[UNV-9] - NO published decimal precision, rounding rule, or zero-denominator rule."},
    {"line_number": "PV-10a", "description": "Part V line 10(a) - net rents and royalties from real or tangible property",
     "line_type": "input", "source_facts": ["nonapportionable_allocated_total"], "sort_order": 49},
    {"line_number": "PV-10b", "description": "Part V line 10(b) - capital gains and losses", "line_type": "input",
     "source_facts": ["nonapportionable_allocated_total"], "sort_order": 50},
    {"line_number": "PV-10c", "description": "Part V line 10(c) - interest and dividends", "line_type": "input",
     "source_facts": ["nonapportionable_allocated_total"], "sort_order": 51},
    {"line_number": "PV-10d", "description": "Part V line 10(d) - patents and copyright royalties", "line_type": "input",
     "source_facts": ["nonapportionable_allocated_total"], "sort_order": 52},
    {"line_number": "PV-10e", "description": "Part V line 10(e) - other nonapportionable income", "line_type": "input",
     "source_facts": ["nonapportionable_allocated_total"], "sort_order": 53},
    {"line_number": "PV-10f", "description": "Part V line 10(f) - total income directly allocable (a) through (e)",
     "line_type": "subtotal", "source_rules": ["R-CO-PARTV"], "sort_order": 54,
     "destination_form": "CO_DR0106 K-1 line 15 Column A"},
    {"line_number": "PV-11", "description": "Part V - modified federal taxable income subject to apportionment (L1 - L10f)",
     "line_type": "subtotal", "source_rules": ["R-CO-PARTV"], "sort_order": 55},
    {"line_number": "PV-12", "description": "Part V - income apportioned to Colorado (L9 x L11)", "line_type": "calculated",
     "source_rules": ["R-CO-PARTV"], "sort_order": 56, "notes": "NOTHING on the DR 0106 face consumes this."},
    {"line_number": "PV-13a", "description": "Part V line 13(a) - Colorado net rents and royalties from real or tangible property",
     "line_type": "input", "source_facts": ["allocable_to_colorado_total"], "sort_order": 57},
    {"line_number": "PV-13b", "description": "Part V line 13(b) - Colorado capital gains and losses", "line_type": "input",
     "source_facts": ["allocable_to_colorado_total"], "sort_order": 58},
    {"line_number": "PV-13c", "description": "Part V line 13(c) - Colorado interest and dividends", "line_type": "input",
     "source_facts": ["allocable_to_colorado_total"], "sort_order": 59},
    {"line_number": "PV-13d", "description": "Part V line 13(d) - Colorado patents and copyright royalties",
     "line_type": "input", "source_facts": ["allocable_to_colorado_total"], "sort_order": 60},
    {"line_number": "PV-13e", "description": "Part V line 13(e) - other Colorado nonapportionable income",
     "line_type": "input", "source_facts": ["allocable_to_colorado_total"], "sort_order": 61},
    {"line_number": "PV-13f", "description": "Part V line 13(f) - total income directly allocable to Colorado",
     "line_type": "subtotal", "source_rules": ["R-CO-PARTV"], "sort_order": 62,
     "destination_form": "CO_DR0106 K-1 line 15 Column B"},
    {"line_number": "PV-14", "description": "Part V - total income apportioned and allocated to Colorado (L12 + L13f)",
     "line_type": "total", "source_rules": ["R-CO-PARTV", "R-CO-PARTV-FEED"], "sort_order": 63,
     "notes": "DEAD END on the DR 0106 face. Wiring this into Part II or Part III is WRONG."},
    {"line_number": "PV-15", "description": "Part V - Sec. 39-22-303.6(8) election to treat all income as apportionable",
     "line_type": "informational", "source_facts": ["all_income_apportionable_election"],
     "source_rules": ["R-CO-PARTV"], "sort_order": 64,
     "notes": "IRREVOCABLE for the tax year; must be made by the extended due date. Forces 0 on lines 10 and 13."},

    # ---- DR 0106K --------------------------------------------------------
    {"line_number": "K1-1", "description": "DR 0106K line 1 - Ordinary business income (loss)", "line_type": "input",
     "source_rules": ["R-CO-K1-COLA", "R-CO-K1-COLB"], "sort_order": 70, "notes": "Box 1 both modules. Losses NEGATIVE."},
    {"line_number": "K1-2", "description": "DR 0106K line 2 - Net rental real estate income (loss)", "line_type": "input",
     "source_rules": ["R-CO-K1-COLA"], "sort_order": 71},
    {"line_number": "K1-3", "description": "DR 0106K line 3 - Other net rental income (loss)", "line_type": "input",
     "source_rules": ["R-CO-K1-COLA"], "sort_order": 72},
    {"line_number": "K1-4", "description": "DR 0106K line 4 - Total guaranteed payments (1065 Box 4c; N/A for an S corp)",
     "line_type": "input", "source_facts": ["k1_line4_guaranteed_payments_col_b"],
     "source_rules": ["R-CO-K1-COLA"], "sort_order": 73,
     "notes": "F3. ALWAYS Rule 39-22-109(3)(b)(xii) direct sourcing. EXCLUDED from every tax base and from line 16 (W5)."},
    {"line_number": "K1-5", "description": "DR 0106K line 5 - Interest and dividends (1065 Boxes 5+6a / 1120-S Boxes 4+5a)",
     "line_type": "input", "source_rules": ["R-CO-K1-COLA"], "sort_order": 74},
    {"line_number": "K1-6", "description": "DR 0106K line 6 - Royalties (1065 Box 7 / 1120-S Box 6)", "line_type": "input",
     "source_rules": ["R-CO-K1-COLA"], "sort_order": 75},
    {"line_number": "K1-7", "description": "DR 0106K line 7 - Net capital gain (1065 Boxes 8+9a+10 / 1120-S Boxes 7+8a+9)",
     "line_type": "input", "source_rules": ["R-CO-K1-COLA"], "sort_order": 76},
    {"line_number": "K1-8", "description": "DR 0106K line 8 - Other income (loss) (1065 Box 11 / 1120-S Box 10)",
     "line_type": "input", "source_rules": ["R-CO-K1-COLA"], "sort_order": 77},
    {"line_number": "K1-9", "description": "DR 0106K line 9 - State income tax addback (F7 SPLIT)", "line_type": "input",
     "source_facts": ["k1_col_a_line9_state_tax_addback"], "source_rules": ["R-CO-K1-L9"], "sort_order": 78,
     "destination_form": "CO_DR0104 line 2",
     "notes": "1065 splits by PARTNER TYPE; 1120-S splits by RESIDENCY. Col. B is Colorado-only in both."},
    {"line_number": "K1-10", "description": "DR 0106K line 10 - Business meals deducted pursuant to section 274(k)",
     "line_type": "input", "source_facts": ["k1_col_a_line10_business_meals"], "sort_order": 79,
     "destination_form": "CO_DR0104 line 5",
     "notes": "[UNV-4](b) erratum: the partnership half says 'claimed by the S corporation' - build to 'the partnership'."},
    {"line_number": "K1-11", "description": "DR 0106K line 11 - Other Colorado additions (F15 - S corp has a FIFTH item)",
     "line_type": "input", "source_facts": ["k1_col_a_line11_other_additions"], "source_rules": ["R-CO-K1-L11"],
     "sort_order": 80, "notes": "POSITIVE. Unauthorized-alien and discriminatory-club go into Col. B at the FULL Col. A amount."},
    {"line_number": "K1-12", "description": "DR 0106K line 12 - Federal deductions (NEGATIVE; carries the Sec. 179 deduction)",
     "line_type": "input", "source_facts": ["k1_col_a_line12_federal_deductions"], "source_rules": ["R-CO-SIGNFLIP"],
     "sort_order": 81, "destination_form": "CO_DR0106 line 6 (SIGN-INVERTED)",
     "notes": "1065 Boxes 12+13 / 1120-S Boxes 11+12. Box 12 / Box 11 IS the Sec. 179 deduction (TOUCHPOINT ii)."},
    {"line_number": "K1-13", "description": "DR 0106K line 13 - Colorado subtractions (NEGATIVE; F16 forks the inventory)",
     "line_type": "input", "source_facts": ["k1_col_a_line13_co_subtractions"], "source_rules": ["R-CO-K1-L13"],
     "sort_order": 82, "destination_form": "CO_DR0106 line 8 (SIGN-INVERTED)"},
    {"line_number": "K1-14", "description": "DR 0106K line 14 - Partner's share of total receipts from Part V line 8",
     "line_type": "calculated", "source_rules": ["R-CO-PARTV-FEED", "R-CO-K1-L1415"], "sort_order": 83,
     "notes": "F14: required only for C-corp partners (1065); NEVER required for an S-corp shareholder."},
    {"line_number": "K1-15", "description": "DR 0106K line 15 - Partner's share of non-apportionable income from Part V",
     "line_type": "calculated", "source_rules": ["R-CO-PARTV-FEED", "R-CO-K1-L1415"], "sort_order": 84,
     "notes": "Col. A from Part V line 10; Col. B from Part V line 13."},
    {"line_number": "K1-16", "description": "DR 0106K line 16 - share of tax paid with composite return or SALT Parity election",
     "line_type": "calculated", "source_rules": ["R-CO-K1-L16"], "sort_order": 85,
     "destination_form": "CO_DR0104CR Part I line 11",
     "notes": "SINGLE COLUMN. FLOORED AT ZERO per owner. Three variants. Must reconcile to DR 0106 L13 (Mode B) or L20 (Mode C)."},

    # ---- return-level boxes ---------------------------------------------
    {"line_number": "BOX-A", "description": "Box A - legal form (Partnership / S Corporation / LLC / LP / LLP / LLLP / Association / Non-Profit)",
     "line_type": "informational", "source_facts": ["box_a_legal_form"], "source_rules": ["R-CO-MODULE-FORK"],
     "sort_order": 90, "notes": "LEGAL form, NOT tax classification. NEVER the module fork key."},
    {"line_number": "BOX-B", "description": "Box B - beginning depreciable assets from the federal return (net of accumulated depreciation)",
     "line_type": "input", "source_facts": ["depreciable_assets_beginning"], "source_rules": ["R-CO-BOXBC"],
     "sort_order": 91, "notes": "Balance-sheet transcription. NOT a tax computation, NOT a depreciation modification."},
    {"line_number": "BOX-C", "description": "Box C - ending depreciable assets from the federal return (net of accumulated depreciation)",
     "line_type": "input", "source_facts": ["depreciable_assets_ending"], "source_rules": ["R-CO-BOXBC"], "sort_order": 92},
    {"line_number": "BOX-D", "description": "Box D - business or profession", "line_type": "input",
     "source_facts": ["business_or_profession"], "sort_order": 93},
    {"line_number": "BOX-E", "description": "Box E - date of organization or incorporation (MM/DD/YY)", "line_type": "input",
     "source_facts": ["date_of_organization"], "sort_order": 94},
    {"line_number": "BOX-F", "description": "Box F - final return", "line_type": "input",
     "source_facts": ["is_final_return"], "sort_order": 95},
    {"line_number": "BOX-G", "description": "Box G - federal changes in the last four years (date + written explanation)",
     "line_type": "input", "source_facts": ["federal_changes_last_four_years"], "sort_order": 96,
     "notes": "A trigger for R7 (line 22 in-lieu-of amount) when combined with an amended return."},
    {"line_number": "BOX-H", "description": "Box H - number of partners or shareholders AS OF YEAR END", "line_type": "input",
     "source_facts": ["num_owners_year_end"], "sort_order": 97, "notes": "As of YEAR END - not a weighted count."},
    {"line_number": "BOX-I", "description": "Box I - SALT Parity Act election (complete Part III; do NOT complete Part II)",
     "line_type": "informational", "source_facts": ["salt_parity_election"], "source_rules": ["R-CO-MODE", "R-CO-ELECTION"],
     "sort_order": 98, "notes": "Also mark the SALT Parity Election box on EVERY DR 0106K."},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM — CO_DR0106 : DIAGNOSTICS
# The A1 disclosure, the structural hard REDs, and ALL SIXTEEN RED-defers
# (R1-R16), each with its OWN diagnostic. No silent gap.
# ═══════════════════════════════════════════════════════════════════════════

CO_DIAGNOSTICS: list[dict] = [
    # ---- THE A1 RULING'S DISCLOSURE (was the blocker; now informational) ----
    {"diagnostic_id": "D_CO106_BLOCK_174A_CONFORMITY", "severity": "info",
     "title": "Retroactive federal amendments flow through to line 1 (RULED; confirming authority still unpulled)",
     "condition": "claims_retroactive_sec174a_election, or any return relying on a retroactively-effective federal amendment",
     "message": ("This return relies on a retroactively-effective federal amendment (e.g. OBBBA's small-business "
                 "Sec. 174A R&D expensing election), which changes federal ordinary income - DR 0106 LINE 1. "
                 "POSITION TAKEN: Colorado's rolling conformity (Sec. 39-22-103(5.3), C.R.S.) picks it up, so line 1 "
                 "carries the federal figure as filed and no Colorado adjustment is computed in either direction. "
                 "The DR 0106 has no modification line anywhere, so this is the only position the form can express. "
                 "BASIS: a reading of the rolling-conformity statute, ruled 2026-08-17 - NOT published CDOR guidance. "
                 "CDOR's Rule 39-22-103(5.3) now shows as '[Repealed]'; the contrary Court of Appeals holding "
                 "(Anschutz) is known only from secondary reporting. Confirm with CDOR guidance, the published "
                 "Anschutz opinion, or the current 1 CCR 201-2 text before relying on it for a filed return."),
     "notes": "[UNV-7] / W13, RULED 2026-08-17 (walk item A1). Severity downgraded error -> info on the ruling; the "
              "diagnostic_id is DELIBERATELY UNCHANGED so nothing downstream re-keys. [UNV-7] stays open as a "
              "pre-ship confirmation item - the ruling has no published CDOR authority behind it. "
              "Rule R-CO-174A-CONFORM."},

    # ---- structural hard REDs -------------------------------------------
    {"diagnostic_id": "D_CO106_MODE_CONFLICT", "severity": "error",
     "title": "Part II and Part III are MUTUALLY EXCLUSIVE",
     "condition": "any value in Part II (lines 12-16) AND any value in Part III (lines 17-20)",
     "message": ("DR 0106 line 21 instruction, verbatim: 'Part II and Part III should not both be completed, as a "
                 "partnership or S corporation may file a composite return (by completing Part II) or make a SALT "
                 "Parity Act election (and complete Part III), but it may not do both.' Statutory basis: "
                 "Sec. 39-22-344(5), C.R.S. Choose one mode."),
     "notes": "W3. Hard RED - never resolve by silent precedence."},
    {"diagnostic_id": "D_CO106_COMPOSITE_MISSING", "severity": "error",
     "title": "Composite return is MANDATORY - an unexcluded nonresident owner exists",
     "condition": "Mode A selected while at least one nonresident owner is not excluded and no carve-out applies",
     "message": ("A composite return is MANDATORY, not elective (Sec. 39-22-601(5.5)(d)(I) / (2.7)(d)(I), C.R.S.), "
                 "unless a SALT Parity election is made. Exclusions: Colorado residents (INCLUDING part-year); "
                 "nonresident corporations/partnerships (partnership module); owners exempt under Sec. 39-22-112(1); "
                 "owners with a timely DR 0107; and owners whose net Colorado-source income is NEGATIVE. Carve-outs: "
                 "an entity consisting ONLY of already-excluded owners (BOTH modules), and a publicly traded "
                 "partnership (partnership module only)."),
     "notes": "W3 + CORRECTION C1: the all-owners-excluded carve-out applies to S CORPS TOO "
              "(Sec. 39-22-601(2.7)(d)(VII)(B)). Without it this false-positives on any S corp whose nonresident "
              "shareholders all filed a DR 0107."},
    {"diagnostic_id": "D_CO106_BOXA_FORK_CONFLICT", "severity": "error",
     "title": "Box A legal form is impossibly inconsistent with the attached federal return",
     "condition": "box_a_legal_form == 'S Corporation' with an attached 1065, or 'Partnership' with an attached 1120-S",
     "message": ("Box A is the TRUE LEGAL FORM, not the federal tax classification, and it must never drive the "
                 "module fork - but these two values cannot both be right. The spec forks off the ATTACHED FEDERAL "
                 "RETURN (1065 vs 1120-S). Verify which federal return was filed."),
     "notes": "W2. Six of Box A's eight values are silent on 1065-vs-1120S; only these two combinations are impossible."},
    {"diagnostic_id": "D_CO106_SIGNFLIP_REVIEW", "severity": "warning",
     "title": "SIGN FLIP applied - K-1 lines 12/13 inverted into DR 0106 lines 6/8",
     "condition": "any DR 0106K Column A line 12 or line 13 amount is non-zero",
     "message": ("The DR 0106K carries federal deductions (line 12) and Colorado subtractions (line 13) as NEGATIVE; "
                 "DR 0106 lines 6 and 8 take them as POSITIVE and then SUBTRACT at lines 9/10. The sign has been "
                 "INVERTED for lines 6 and 8. Lines 3 and 4 (from K-1 lines 10, 9 and 11) are already positive and "
                 "were NOT inverted. Verify line 10 against the federal return."),
     "notes": "The single most likely arithmetic bug on this form. Getting it wrong moves line 10 by TWICE the "
              "deduction total, in the wrong direction."},
    {"diagnostic_id": "D_CO106_179_TWO_PATHS", "severity": "info",
     "title": "Sec. 179 reaches Colorado by TWO paths - both must be present",
     "condition": "any Sec. 179 deduction or Sec. 179-disposition amount on the federal return",
     "message": ("(i) The Sec. 179-DISPOSITION gain/loss (Sch. K line 20c / 17d statement) is added into DR 0106 "
                 "LINE 2. (ii) The Sec. 179 DEDUCTION ITSELF arrives via DR 0106K line 12 (1065 K-1 Box 12 + Box 13 / "
                 "1120-S K-1 Box 11 + Box 12) and is aggregated into DR 0106 LINE 6, SIGN-INVERTED. DR 0106 line 2 "
                 "lists income lines only and EXCLUDES Sch. K 12/13 and 11/12, so line 6 is the only path for the "
                 "deduction. NEITHER is a Colorado modification - Colorado conforms to Sec. 179 at the federal limit."),
     "notes": "Verifier correction C3 (HIGH). The research pass said there was only ONE Sec. 179 mechanic; a spec "
              "built on that sentence would have had NO path at all for the Sec. 179 deduction."},
    {"diagnostic_id": "D_CO106_NO_DEPR_MOD", "severity": "info",
     "title": "Colorado has NO depreciation modification - this is a rule-says-no",
     "condition": "federal bonus depreciation or Sec. 179 claimed",
     "message": ("Colorado is a rolling-conformity state with NO Sec. 168(k) add-back, NO state Sec. 179 dollar limit "
                 "or phaseout, NO separate state basis, and NO recapture or recovery schedule. Federal depreciation "
                 "flows straight through into DR 0106 line 1. Do NOT port Georgia's or Tennessee's bonus add-back. "
                 "The only two depreciation-adjacent items on the form are Boxes B/C (a balance-sheet transcription) "
                 "and the two Sec. 179 aggregation paths - none of them is a modification."),
     "notes": "W6. Established five ways, including the ModDate argument: the DR 0106 was re-stamped 2025-10-13 and "
              "the DR 0106K-I 2025-09-23, AFTER OBBBA and after the Aug-2025 extraordinary session, and CDOR still "
              "added no depreciation line. The absence is a CURRENT EDITORIAL DECISION."},
    {"diagnostic_id": "D_CO106_MODE_A_INFORMATIONAL", "severity": "info",
     "title": "Mode A - informational-only DR 0106 (zero tax), still a MANDATORY filing",
     "condition": "no SALT Parity election and no composite return required",
     "message": ("'Every partnership and S corporation must file a DR 0106 for any year it is doing business in "
                 "Colorado.' This return has a computed line 10, a marked line 11, no Part II, no Part III and ZERO "
                 "TAX at line 21. THE COLORADO K-1s ARE STILL MANDATORY and must be transmitted separately. The "
                 "DR 0106CR is still a mandatory attachment (Column B = Column A, Column C = 0)."),
     "notes": "W3. Mode A is a real and common filing, not an edge case."},
    {"diagnostic_id": "D_CO106_GUARANTEED_PAYMENTS", "severity": "warning",
     "title": "Guaranteed payments are IN the entity base but OUT of every tax base",
     "condition": "module == 1065 and DR 0106K line 4 is non-zero",
     "message": ("1065 Sch. K line 4c IS included in DR 0106 line 2, but DR 0106K line 4 is SKIPPED by Part II, "
                 "Part III and K-1 line 16 alike. Verbatim: 'Do not include guaranteed payments from line 4 of the "
                 "Colorado K-1. Nonresident partners with Colorado-source guaranteed payments must FILE THEIR OWN "
                 "COLORADO INCOME TAX RETURN to report guaranteed payments and pay any applicable Colorado income "
                 "tax.' Column B for line 4 is ALWAYS direct-sourced under Rule 39-22-109(3)(b)(xii)."),
     "notes": "W5. A three-place rule; getting it wrong overstates every partnership composite/PTET base that has "
              "guaranteed payments."},
    {"diagnostic_id": "D_CO106_PTET_199A_ADDBACK", "severity": "warning",
     "title": "SALT Parity election forces a FULL Sec. 199A add-back on EVERY owner",
     "condition": "salt_parity_election is true",
     "message": ("Every partner or shareholder must add back the ENTIRE federal Sec. 199A qualified business income "
                 "deduction on their Colorado return (DR 0104 line 3), REGARDLESS OF THEIR AGI and NOT LIMITED to the "
                 "deduction attributable to this entity. Colorado's ordinary AGI thresholds ($500,000 / $1,000,000 "
                 "joint) are switched off by the election. Owners also add back their share of state income tax "
                 "deducted by the entity (DR 0106K line 9 -> DR 0104 line 2), and claim the entity tax as a "
                 "REFUNDABLE credit (DR 0106K line 16 -> DR 0104CR Part I line 11)."),
     "notes": "The election reaches BACKWARD into every owner's individual return - the CO individual and PTE specs "
              "cannot be authored independently."},
    {"diagnostic_id": "D_CO106_PARTV_L9_PRECISION", "severity": "warning",
     "title": "Part V line 9 percentage - precision, rounding and zero-denominator rules are UNPUBLISHED",
     "condition": "Part V completed, or Part V line 8 (Everywhere) is zero",
     "message": ("The DR 0106 face prints 'Line 8 (Colorado) divided by line 8 (Everywhere)' with a bare '%' box, "
                 "NO stated decimal places, NO rounding rule and NO rule for a zero 'Everywhere' denominator. This "
                 "moves every nonresident owner's Column B. Verify the ratio manually. Would be settled by the "
                 "DR 0112RF face, the Colorado MeF schema (which will carry a decimal precision), or CDOR guidance."),
     "notes": "[UNV-9]. Unresolved as of 2026-08-16."},
    {"diagnostic_id": "D_CO106_K1_SEPARATE_FILING", "severity": "warning",
     "title": "Colorado K-1s must be transmitted SEPARATELY - never as an attachment",
     "condition": "any DR 0106K is produced",
     "message": ("Verbatim: 'Do not submit the copies of the Colorado K-1s ... (or the DR 1706 transmittal form) as an "
                 "attachment to a paper income tax return (form DR 0106, OR AS A PDF ATTACHMENT TO AN MeF INCOME TAX "
                 "RETURN).' Five accepted channels: MeF (inline in the return submission), XLS upload, XML upload, "
                 "manual entry in Revenue Online, or paper with a DR 1706 cover sheet. Electronic submission requires "
                 "a CDOR web-submitter registration. Due the same date as the return, including extension."),
     "notes": "W8. Depends on [UNV-6] (the Colorado MeF program is LOI-gated and its schema is not publicly readable)."},
    {"diagnostic_id": "D_CO106_DR0107_PERSISTS", "severity": "info",
     "title": "DR 0107 is a ONE-TIME filing that persists across years",
     "condition": "any owner flagged with a DR 0107 agreement",
     "message": ("Verbatim: 'A form DR 0107 filed with the Department for a nonresident partner REMAINS IN EFFECT FOR "
                 "FUTURE TAX YEARS. The partnership does not need to submit a new form DR 0107 for the same "
                 "nonresident partner each year.' The face adds its own revocation channel: 'applicable to all future "
                 "filing periods UNLESS NOTIFIED OTHERWISE.' Software that re-collects it annually generates false "
                 "diagnostics; software that never re-checks it misses revocations. Not required at all if the entity "
                 "elects SALT Parity."),
     "notes": "W12. Where the persistent per-owner flag lives is a CLIENT-RECORD question, not just a form question."},
    {"diagnostic_id": "D_CO106_EST_TAX_THRESHOLD", "severity": "info",
     "title": "Estimated-tax threshold built as STRICTLY GREATER THAN $5,000 (a ruling on a 3-2 source split)",
     "condition": "net Colorado tax liability is at or near $5,000",
     "message": ("Colorado's own sources SPLIT on this threshold. 'Exceeds $5,000': DR 0233 instructions, DR 0106EP, "
                 "SALT Parity publication. '>= $5,000' / 'less than $5,000': DR 0106 line 31 AND the Colorado "
                 "Corporate Income Tax Guide, which the DR 0106 expressly incorporates by reference for this exact "
                 "rule. The exposure is the single point where net tax is EXACTLY $5,000. Built strictly greater "
                 "than, because DR 0233 Part 1 yields a zero base at $5,000 either way. Also note: PTEs get NO "
                 "annualized income installment method, though C corporations do."),
     "notes": "W9 / verifier correction C9. A KEN RULING, not a settled erratum."},

    # ---- the sixteen RED-defers, R1..R16 --------------------------------
    {"diagnostic_id": "D_CO106_R1_DR0619", "severity": "error",
     "title": "R1 - DR 0619 innovative motor vehicle / electric bicycle credits (prepare manually)",
     "condition": "DR 0106 line 23 or line 27 entered",
     "message": ("Form DR 0619 is not prepared by this product. Complete the DR 0619 manually and submit it with the "
                 "return. Lines 3 and 10 carry additional credit to DR 0106 line 27; lines 4 and 11 carry the "
                 "advance-payment repayment to line 23."),
     "notes": "NEW to the DR 0106 for TY2025."},
    {"diagnostic_id": "D_CO106_R2_DR1305", "severity": "error",
     "title": "R2 - Gross conservation easement (DR 1305 / 1305E / 1305F / 1305G) (prepare manually)",
     "condition": "DR 0106 line 15 entered",
     "message": "The gross conservation easement credit schedules are not prepared by this product. Complete the DR 1305 series manually; the DR 1305G line 33 amount is entered on DR 0106 line 15 and the DR 1305G must be submitted with the return.",
     "notes": "Separate from the DR 0106CR."},
    {"diagnostic_id": "D_CO106_R3_ENTZONE", "severity": "error",
     "title": "R3 - Enterprise Zone / CHIPS Zone credits (DR 1366, DR 1370) (prepare manually)",
     "condition": "DR 0106CR line 11 or line 12 is non-zero",
     "message": "The Enterprise Zone (DR 1366) and CHIPS Zone (DR 1370) credit schedules are not prepared by this product. Complete them manually and submit them with the return.",
     "notes": "W10 - credit sub-schedules are all deferred in v1."},
    {"diagnostic_id": "D_CO106_R4_CHFA", "severity": "error",
     "title": "R4 - CHFA housing credits (affordable / transit-oriented / middle-income) (prepare manually)",
     "condition": "DR 0106CR line 13 is non-zero",
     "message": "The CHFA housing credit schedules are not prepared by this product. Complete them manually and submit the certification with the return.",
     "notes": "W10."},
    {"diagnostic_id": "D_CO106_R5_REMEDIATION", "severity": "error",
     "title": "R5 - Remediation of contaminated land (DR 0348P / DR 0348T / DR 0349) (prepare manually)",
     "condition": "DR 0106CR line 8 is non-zero",
     "message": "The contaminated-land remediation credit schedules are not prepared by this product. Complete the DR 0348P / DR 0348T / DR 0349 manually and submit them with the return.",
     "notes": "W10."},
    {"diagnostic_id": "D_CO106_R6_CHILDCARE", "severity": "error",
     "title": "R6 - Child care contribution / investment credits (DR 1317) (prepare manually)",
     "condition": "DR 0106CR lines 5 through 7 are non-zero",
     "message": ("The child care credit schedules are not prepared by this product. Complete the DR 1317 "
                 "certification manually. The child care center / family care home and employer child care "
                 "investment credits also require you to submit a copy of the facility license AND a list of "
                 "depreciable tangible personal property with the return - a SUBSTANTIATION ATTACHMENT, not a "
                 "depreciation modification."),
     "notes": "W10. This is the source of the three benign 'deprecia*' hits on the DR 0106CR (verifier C4)."},
    {"diagnostic_id": "D_CO106_R7_INLIEU", "severity": "error",
     "title": "R7 - Sec. 39-22-601.5(3)(e) partnership-audit in-lieu-of amount (line 22) (prepare manually)",
     "condition": "Box G marked with an amended return, or DR 0106 line 22 entered",
     "message": ("The 'in-lieu-of' amount a partnership pays after an IRS partnership audit, under an election at "
                 "Sec. 39-22-601.5(3)(d), C.R.S., is NOT computed by this product. NO COLORADO FORM COMPUTES IT and "
                 "the DR 0106 instruction gives no formula - only the filing mechanics (it is reported on an AMENDED "
                 "return). Determine the amount under Sec. 39-22-601.5(3)(e) and enter it manually."),
     "notes": "[UNV-8] - confirmed unresolved by the verifier. Must not be silently dropped."},
    {"diagnostic_id": "D_CO106_R8_ALTAPPORT", "severity": "error",
     "title": "R8 - Sec. 39-22-303.6(9) alternative apportionment and industry special rules (prepare manually)",
     "condition": "user elects alternative apportionment or an industry special rule",
     "message": "Alternative apportionment under Sec. 39-22-303.6(9), C.R.S. (available on a preponderance-of-the-evidence showing), and the industry special rules in 1 CCR 201-2, are not computed by this product. Prepare the apportionment manually.",
     "notes": "Out of v1 scope."},
    {"diagnostic_id": "D_CO106_R9_MUTUALFUND", "severity": "error",
     "title": "R9 - Sec. 39-22-303.7 mutual fund service corporation sourcing (prepare manually)",
     "condition": "S corporation Column B sourcing requires Sec. 39-22-303.7",
     "message": "The S-corporation Column B rule reads 'apportioned or allocated to Colorado pursuant to section 39-22-303.6, C.R.S., and, IF APPLICABLE section 39-22-303.7, C.R.S.' Sec. 39-22-303.7 (sourcing of sales of mutual fund service corporations) is not computed by this product. Prepare the sourcing manually.",
     "notes": "F9 - this 'if applicable' clause exists only on the S-corp side."},
    {"diagnostic_id": "D_CO106_R10_DR1079", "severity": "error",
     "title": "R10 - DR 1079 Colorado real-property-transfer withholding (prepare manually)",
     "condition": "DR 0106 line 25 includes a DR 1079 component",
     "message": "Form DR 1079 (Payment of Withholding Tax on Certain Colorado Real Property Interest Transfers) is not prepared by this product. Payments remitted with a DR 1079 for Colorado real estate that closed during the tax year are included in DR 0106 line 25, and THE DR 1079 MUST BE SUBMITTED WITH THE RETURN.",
     "notes": "W11. A payment source with no other presence on the form."},
    {"diagnostic_id": "D_CO106_R11_DR0108", "severity": "error",
     "title": "R11 - DR 0108 nonresident remittance: TY2025 status UNKNOWN",
     "condition": "user asserts a DR 0108 was filed",
     "message": ("Colorado has NOT published a TY2025 DR 0108. The most recent posted version is the 2023 form (rev. "
                 "11/17/22) - and CDOR's own page hyperlinks both its '2023' and '2022' entries to the SAME file - "
                 "whose text refers the reader to 'the Book 106', a booklet that no longer exists for TY2025. The "
                 "TY2025 DR 0106, DR 0106K-I and DR 0107 never mention the DR 0108. CONFIRM THE REMITTANCE ROUTE WITH "
                 "CDOR before relying on it."),
     "notes": "[UNV-2] - confirmed unresolved. Working assumption: retired alongside the Book 106."},
    {"diagnostic_id": "D_CO106_R12_RETRO_ELECTION", "severity": "error",
     "title": "R12 - retroactive SALT Parity elections for TY2018-2021 are CLOSED",
     "condition": "user requests a retroactive SALT Parity Act election for TY2018-2021",
     "message": ("The retroactive SALT Parity Act election window CLOSED JUNE 30, 2024. Sec. 39-22-343(1)(c)(I), "
                 "C.R.S.: the election for tax years commencing on or after January 1, 2018 but prior to January 1, "
                 "2022 'must [have been] made on or after September 1, 2023, but before July 1, 2024, in a composite "
                 "amended tax return'. The CDOR SALT Parity publication repeats it in the past tense. NO RETROACTIVE "
                 "ELECTION CAN BE MADE."),
     "notes": "Confirmed verbatim from statute by the verifier."},
    {"diagnostic_id": "D_CO106_R13_SHORTPERIOD", "severity": "error",
     "title": "R13 - short-period and fiscal-year estimated-payment schedules (prepare manually)",
     "condition": "the tax period is not 12 months",
     "message": "Short-period and fiscal-year adjustments to the DR 0233 estimated-payment schedule (lines 9-11) are not computed by this product. Note that the quarterly due dates are the 15th day of the FOURTH, SIXTH, NINTH and TWELFTH month OF THE TAXABLE YEAR, not fixed calendar dates. Prepare the DR 0233 manually.",
     "notes": "Also note a 12-month preceding year is a precondition of the 100%-of-prior-year safe harbor."},
    {"diagnostic_id": "D_CO106_R14_PTP", "severity": "error",
     "title": "R14 - publicly traded partnership composite exemption (statute-only; verify manually)",
     "condition": "user asserts publicly traded partnership status (PARTNERSHIP module only)",
     "message": ("Sec. 39-22-601(5.5)(d)(VII)(B), C.R.S., excludes from the mandatory composite return 'A publicly "
                 "traded partnership, as defined in section 7704 (b) of the internal revenue code, that meets any of "
                 "the exceptions under section 7704 (c) of the internal revenue code AND IS NOT TREATED AS A "
                 "CORPORATION UNDER SECTION 7704 (a) OF THE INTERNAL REVENUE CODE.' ALL THREE CONDITIONS must hold. "
                 "This carve-out appears NOWHERE in the DR 0106 instructions - zero hits for 'publicly traded' or "
                 "'7704' across the DR 0106, DR 0106K-I, DR 0107 and the SALT Parity publication. Verify the test "
                 "manually and retain support. This carve-out is PARTNERSHIP-ONLY."),
     "notes": ("[UNV-5], quote corrected per C2 (the third condition was elided by the research pass). NOTE the "
               "SIBLING carve-out - 'an entity consisting only of already-excluded owners' - is NOT deferred: it "
               "exists for BOTH modules (Sec. 39-22-601(5.5)(d)(VII)(C) and (2.7)(d)(VII)(B)) and is COMPUTED in the "
               "mandatory-composite test (C1).")},
    {"diagnostic_id": "D_CO106_R15_K1_TRANSMITTAL", "severity": "error",
     "title": "R15 - Colorado K-1 XLS / XML Revenue Online submitter path (submit manually)",
     "condition": "K-1s are to be transmitted outside an MeF submission",
     "message": ("Colorado K-1s must be transmitted SEPARATELY - they may NOT be attached to a paper DR 0106 or "
                 "included as a PDF attachment to an MeF submission. The XLS and XML Revenue Online upload paths (and "
                 "the manual-entry path) are not produced by this product, and they require a CDOR web-submitter "
                 "registration. Use MeF-inline transmission, or file on paper with a DR 1706 cover sheet."),
     "notes": "W8 / [UNV-6]. Whether the Colorado MeF DR 0106 schema carries DR 0106K records inline cannot be "
              "verified until the LOI-gated schema is available."},
    {"diagnostic_id": "D_CO106_R16_REPORTABLE", "severity": "error",
     "title": "R16 - listed or reportable transaction disclosure (Form 8886 / DR 1831) (prepare manually)",
     "condition": "the listed-or-reportable-transaction box is marked",
     "message": "Listed and reportable transaction disclosures are not prepared by this product. Attach IRS Form 8886 or Colorado form DR 1831 as required by Secs. 39-22-651 to 659, C.R.S.",
     "notes": "Return-level box on the DR 0106 face."},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM — CO_DR0106 : TEST SCENARIOS
# ═══════════════════════════════════════════════════════════════════════════

CO_SCENARIOS: list[dict] = [
    {"scenario_name": "THE SIGN FLIP - partnership Part I with negative K-1 deductions", "scenario_type": "normal",
     "sort_order": 1,
     "inputs": {"federal_return_type": "1065",
                "fed_schedule_k": {"1": 500000, "2": 20000, "4c": 60000, "5": 10000},
                "k1_col_a_line9_state_tax_addback": 12000, "k1_col_a_line10_business_meals": 3000,
                "k1_col_a_line11_other_additions": 5000,
                "k1_col_a_line12_federal_deductions": -50000,
                "k1_col_a_line13_co_subtractions": -20000},
     "expected_outputs": {"L1": 500000, "L2": 90000, "L3": 3000, "L4": 17000, "L5": 610000,
                          "L6": 50000, "L8": 20000, "L9": 70000, "L10": 540000},
     "notes": ("L2 = 20000 + 60000 + 10000 = 90000 (1065 set). L3 = K-1 L10 = 3000, NOT inverted. L4 = K-1 L9 + L11 = "
               "12000 + 5000 = 17000, NOT inverted. L5 = 610000. L6 = -(-50000) = 50000 INVERTED. L8 = -(-20000) = "
               "20000 INVERTED. L9 = 70000. L10 = 610000 - 70000 = 540000. "
               "WITHOUT the inversion L6/L8 would be -50000/-20000, L9 = -70000 and L10 = 680000 - WRONG by 140000, "
               "i.e. TWICE the deduction total, in the wrong direction.")},
    {"scenario_name": "SIGN FLIP failure mode - un-inverted aggregation gives the wrong line 10", "scenario_type": "failure",
     "sort_order": 2,
     "inputs": {"federal_return_type": "1065", "fed_schedule_k": {"1": 500000, "2": 20000, "4c": 60000, "5": 10000},
                "k1_col_a_line9_state_tax_addback": 12000, "k1_col_a_line10_business_meals": 3000,
                "k1_col_a_line11_other_additions": 5000, "k1_col_a_line12_federal_deductions": -50000,
                "k1_col_a_line13_co_subtractions": -20000, "apply_sign_flip": False},
     "expected_outputs": {"L6": -50000, "L8": -20000, "L9": -70000, "L10": 680000, "is_wrong": True},
     "notes": "The BUG, recorded deliberately so a regression is recognisable: skipping the inversion overstates "
              "line 10 by 140000 (2 x 70000). The harness asserts the correct and buggy answers DIFFER."},
    {"scenario_name": "Sec. 179 TOUCHPOINT (i) - disposition gain raises line 2", "scenario_type": "edge",
     "sort_order": 3,
     "inputs": {"federal_return_type": "1120S", "fed_schedule_k": {"1": 300000, "2": 15000, "4": 5000},
                "sec179_disposition_gain": 40000},
     "expected_outputs": {"L1": 300000, "L2": 60000},
     "notes": "1120-S set: Sch. K 2 + 4 = 20000, plus the Sec. 179-disposition statement (Sch. K 17d) 40000 = 60000. "
              "Omitting the disposition gain UNDERSTATES line 2 by 40000."},
    {"scenario_name": "Sec. 179 TOUCHPOINT (ii) - the deduction rides K-1 line 12 into line 6", "scenario_type": "edge",
     "sort_order": 4,
     "inputs": {"federal_return_type": "1120S", "fed_schedule_k": {"1": 300000},
                "k1_col_a_line12_federal_deductions": -125000},
     "expected_outputs": {"L2": 0, "L6": 125000, "L10": 175000},
     "notes": ("1120-S K-1 Box 11 IS the Sec. 179 deduction and lands in DR 0106K line 12 (Box 11 + Box 12), entered "
               "NEGATIVE. DR 0106 line 2 EXCLUDES Sch. K 11/12, so line 2 gets nothing. Line 6 = 125000 "
               "(sign-inverted); L10 = 300000 - 125000 = 175000. This is the ONLY path by which the federal Sec. 179 "
               "deduction reaches Colorado - verifier correction C3.")},
    {"scenario_name": "FORK F4 - the same federal Schedule K gives DIFFERENT line 2 per module", "scenario_type": "edge",
     "sort_order": 5,
     "inputs": {"fed_schedule_k": {"1": 100000, "2": 1000, "3c": 2000, "4": 4000, "4c": 8000,
                                   "5": 16000, "5a": 32000, "6": 64000, "6a": 128000}},
     "expected_outputs": {"L2_1065": 155000, "L2_1120S": 103000},
     "notes": ("1065 reads lines 2, 3c, 4c, 5, 6a (+7, 8, 9a, 10, 11) = 1000 + 2000 + 8000 + 16000 + 128000 = 155000. "
               "1120-S reads lines 2, 3c, 4, 5a, 6 (+7, 8a, 9, 10) = 1000 + 2000 + 4000 + 32000 + 64000 = 103000. "
               "A shared code path that ignores the fork silently produces the wrong entity income.")},
    {"scenario_name": "FORK F7 - state tax add-back splits on a DIFFERENT AXIS per module", "scenario_type": "edge",
     "sort_order": 6,
     "inputs": {"owner": {"residency": "nonresident", "owner_kind": "individual"}},
     "expected_outputs": {"scope_1065": "all_states", "scope_1120S": "colorado_only"},
     "notes": ("A NONRESIDENT INDIVIDUAL owner. As a PARTNER (split by partner type, and it is not a C corp) the "
               "Column A add-back is ALL state income taxes regardless of state. As a SHAREHOLDER (split by "
               "residency, and it is a nonresident) it is COLORADO ONLY. Same owner, different answer, because the "
               "SPLIT AXIS ITSELF forks.")},
    {"scenario_name": "FORKS F15/F16 - the modification inventories differ (verifier C7/C8)", "scenario_type": "edge",
     "sort_order": 7, "inputs": {},
     "expected_outputs": {"l11_items_1065": 4, "l11_items_1120S": 5, "l13_has_export_1065": True,
                          "l13_has_export_1120S": False, "l13_has_280c_1120S": True, "l13_has_280c_1065": False},
     "notes": ("Line 11: the S-corp half adds a FOREIGN-TAX add-back with no partnership analogue. Line 13: the "
               "partnership half alone carries the Sec. 39-22-206 export-taxpayer subtraction; the S-corp half alone "
               "carries the IRC Sec. 280C disallowed-wages subtraction. Building either module from the other's list "
               "SILENTLY DROPS A REAL MODIFICATION.")},
    {"scenario_name": "MODE B - composite, with the five exclusions and the per-owner floor", "scenario_type": "normal",
     "sort_order": 8,
     "inputs": {"federal_return_type": "1065", "composite_return_filed": True,
                "owners": [{"residency": "nonresident", "owner_kind": "individual", "col_b": 200000},
                           {"residency": "nonresident", "owner_kind": "individual", "col_b": 100000},
                           {"residency": "resident", "owner_kind": "individual", "col_a": 500000, "col_b": 0},
                           {"residency": "nonresident", "owner_kind": "individual", "dr0107": True, "col_b": 90000},
                           {"residency": "nonresident", "owner_kind": "c_corp", "col_b": 400000},
                           {"residency": "nonresident", "owner_kind": "individual", "col_b": -60000}]},
     "expected_outputs": {"L12": 300000, "L13": 13200, "sum_k1_l16": 13200},
     "notes": ("Included: the two nonresident individuals (200000 + 100000 = 300000). Excluded: the resident; the "
               "DR 0107 filer; the nonresident C corporation (F10); and the NEGATIVE-income owner (the fifth, "
               "statutory exclusion). L13 = 300000 x 4.4% = 13200. Per-owner K-1 L16 = 8800 + 4400 = 13200, and the "
               "negative owner's L16 floors at 0 - THE RECONCILIATION HOLDS ONLY BECAUSE the aggregate exclusion and "
               "the per-owner floor are the same rule (W4).")},
    {"scenario_name": "MODE C - SALT Parity, residents on Column A and nonresidents on Column B", "scenario_type": "normal",
     "sort_order": 9,
     "inputs": {"federal_return_type": "1120S", "salt_parity_election": True,
                "owners": [{"residency": "resident", "owner_kind": "individual", "col_a": 400000, "col_b": 150000},
                           {"residency": "part_year", "owner_kind": "individual", "col_a": 100000, "col_b": 40000},
                           {"residency": "nonresident", "owner_kind": "individual", "col_a": 300000, "col_b": 120000},
                           {"residency": "nonresident", "owner_kind": "individual", "col_a": 50000, "col_b": -25000}]},
     "expected_outputs": {"L17": 500000, "L18": 120000, "L19": 620000, "L20": 27280},
     "notes": ("L17 uses residents' COLUMN A - their ENTIRE income, not just Colorado-source - and the PART-YEAR "
               "owner counts as a RESIDENT: 400000 + 100000 = 500000. L18 uses nonresidents' Column B: 120000; the "
               "negative-Column-B nonresident is EXCLUDED ENTIRELY, not netted. L19 = 620000; L20 = 620000 x 4.4% = "
               "27280.")},
    {"scenario_name": "MODE A - informational-only return, zero tax, still mandatory", "scenario_type": "edge",
     "sort_order": 10,
     "inputs": {"federal_return_type": "1120S", "salt_parity_election": False, "composite_return_filed": False,
                "owners": [{"residency": "resident", "owner_kind": "individual", "col_a": 250000},
                           {"residency": "nonresident", "owner_kind": "individual", "dr0107": True, "col_b": 80000}]},
     "expected_outputs": {"mode": "A", "L21": 0, "composite_required": False},
     "notes": ("Every nonresident shareholder filed a DR 0107, so the all-owners-excluded carve-out at "
               "Sec. 39-22-601(2.7)(d)(VII)(B) applies. CORRECTION C1: the research pass said the S corp had 'no "
               "analogue' to this carve-out, which would have made the mandatory-composite diagnostic FALSE-POSITIVE "
               "on exactly this return. Parts II and III are blank; line 21 = 0; the return and the K-1s are still "
               "MANDATORY.")},
    {"scenario_name": "MODE conflict - Parts II and III both completed is a hard RED", "scenario_type": "failure",
     "sort_order": 11,
     "inputs": {"salt_parity_election": True, "composite_return_filed": True},
     "expected_outputs": {"raises": "CoModeConflict", "diagnostic": "D_CO106_MODE_CONFLICT"},
     "notes": "Sec. 39-22-344(5), C.R.S., and the line 21 instruction. Never resolved by silent precedence."},
    {"scenario_name": "TWO RATE CONSTANTS - equal in TY2025, separate authorities", "scenario_type": "edge",
     "sort_order": 12, "inputs": {"tax_year": 2025},
     "expected_outputs": {"composite_rate": "0.044", "ptet_rate": "0.044", "same_value": True, "same_constant": False},
     "notes": ("Composite (line 13) -> C.R.S. Sec. 39-22-104, the INDIVIDUAL rate. PTET (line 20) -> C.R.S. "
               "Sec. 39-22-301(1)(d)(I)(K), the CORPORATE rate. Numerically identical for TY2025 - which is exactly "
               "why a spec collapses them by accident. LCS projects 4.33% (TY2027) and 4.29% (TY2028).")},
    {"scenario_name": "K-1 line 16 floors at zero per owner", "scenario_type": "edge", "sort_order": 13,
     "inputs": {"col_b_positive": 250000, "col_b_negative": -80000, "rate": "0.044"},
     "expected_outputs": {"l16_positive": 11000, "l16_negative": 0},
     "notes": "'If the sum ... is a negative amount, enter 0 (zero) on line 16.' 250000 x 4.4% = 11000; the negative "
              "owner floors at 0 rather than producing a credit."},
    {"scenario_name": "Part V - no out-of-state activity sources 100% to Colorado", "scenario_type": "edge",
     "sort_order": 14,
     "inputs": {"l1_modified_fti": 800000, "no_out_of_state_activity": True},
     "expected_outputs": {"PV-9": 1.0, "PV-11": 800000, "PV-12": 800000, "PV-14": 800000},
     "notes": "Sec. 39-22-303.6(3)(a). Part V line 14 still has NO destination on the DR 0106 face - it feeds the "
              "DR 0106K (line 8 -> K-1 L14; lines 10/13 -> K-1 L15)."},
    {"scenario_name": "Due date is the FOURTH month, not the C corp's fifth", "scenario_type": "edge",
     "sort_order": 15, "inputs": {"tax_year": 2025},
     "expected_outputs": {"original_month": 4, "original_day": 15, "extension_months": 6,
                          "extension_to_pay": False, "voucher": "DR 0158-N"},
     "notes": "Sec. 39-22-608(2)(a); (2)(b)'s fifth-month rule reaches only C corporations filing under "
              "Sec. 39-22-601(2). April 15 / October 15 / no extension to pay. The DR 0112 is May 15 / November 15."},
    {"scenario_name": "Estimated tax - required annual amount and the first-year-election block", "scenario_type": "edge",
     "sort_order": 16,
     "inputs": {"current_year_tax": 100000, "prior_year_tax": 40000, "making_salt_parity_election": True,
                "elected_salt_parity_prior_year": False},
     "expected_outputs": {"required_with_block": 70000, "required_without_block": 40000, "threshold_met": True},
     "notes": ("Normally the lesser of 70% x 100000 = 70000 and 100% x 40000 = 40000, i.e. 40000. But a FIRST-YEAR "
               "electing entity loses the prior-year leg (DR 0233 line 6), so the required amount is 70000. A "
               "PTE-specific rule the C-corp module does NOT have. Threshold: 100000 > 5000.")},
    {"scenario_name": "Delinquency penalty - greater of $5 or 5% first month, capped at 12%", "scenario_type": "edge",
     "sort_order": 17,
     "inputs": {"additional_tax": 10000, "months_delinquent": 1, "pct_paid_by_original_due_date": 0.5},
     "expected_outputs": {"L29_month1": 500, "L29_month20_capped": 1200, "L29_if_90pct_paid": 0},
     "notes": "Month 1: max(5, 10000 x 5%) = 500. At 20 months the rate would be 5% + 0.5% x 19 = 14.5%, capped at "
              "12% -> 1200. Paying 90% by the ORIGINAL due date suppresses the penalty entirely."},
    {"scenario_name": "Mode C forces DR 0106CR Column C to zero", "scenario_type": "edge", "sort_order": 18,
     "inputs": {"salt_parity_election": True, "column_a": 45000},
     "expected_outputs": {"col_b": 45000, "col_c": 0, "L14": 0, "L15": 0},
     "notes": "'The electing pass-through entity may not claim any refundable or nonrefundable credits on its return' "
              "(Sec. 39-22-344(3), C.R.S.). The DR 0106CR is still a MANDATORY attachment. Same rule applies in Mode A."},
    {"scenario_name": "DR 0106CR line 38 sums lines 5 through 37, not 1 through 37", "scenario_type": "edge",
     "sort_order": 19,
     "inputs": {"line_1": 1000, "line_2": 2000, "line_3": 3000, "line_4": 4000, "line_5": 5000, "line_37": 7000},
     "expected_outputs": {"L38": 12000},
     "notes": "Lines 1-4 (recapture and the other-state-tax block) are EXCLUDED. 5000 + 7000 = 12000, not 22000. "
              "Verifier addition - absent from the research brief."},
    {"scenario_name": "RULED (A1) - a return relying on retroactive Sec. 174A computes, carrying the federal figure",
     "scenario_type": "edge", "sort_order": 20,
     "inputs": {"claims_retroactive_sec174a_election": True, "federal_ordinary_income": 300000},
     "expected_outputs": {"L1": 300000, "sec174a_adjustment": None,
                          "diagnostic": "D_CO106_BLOCK_174A_CONFORMITY", "severity": "info", "computed": True},
     "notes": ("[UNV-7] / W13, RULED BY KEN 2026-08-17 (walk A1). Colorado's rolling conformity picks up "
               "retroactively-effective federal amendments, so line 1 transcribes federal ordinary income AS FILED "
               "and no adjustment is computed in either direction. The DR 0106 has NO modification line to carry a "
               "divergence, which is the structural fact the ruling turns on - the form can express no other answer. "
               "The diagnostic still fires, at INFO, to disclose that the position rests on a statutory reading "
               "rather than published CDOR guidance.")},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORMS registry + FLOW ASSERTIONS
# ═══════════════════════════════════════════════════════════════════════════

FORMS: list[dict] = [
    {
        "identity": {
            "form_number": FORM_CODE,
            "form_title": "CO DR 0106 - Colorado Partnership and S Corporation Income Tax Return (TY2025)",
            "notes": ("ONE form serving TWO delvio-tax modules (1065 and 1120S). The face is identical for both; the "
                      "SOURCING RULES FORK in 16 places (F1-F16), 14 of which change the arithmetic. The module fork "
                      "keys off the ATTACHED FEDERAL RETURN, never Box A. Three filing modes: A informational-only "
                      "(zero tax, still mandatory), B composite nonresident (MANDATORY absent an election), C SALT "
                      "Parity Act PTET - B and C mutually exclusive. Colorado has NO depreciation modification of any "
                      "kind; Sec. 179 reaches the return by TWO aggregation paths, neither a modification. Two "
                      "SEPARATE 4.4% rate statutes. [UNV-7] (Sec. 174A / retroactive federal amendments under "
                      "rolling conformity) RULED BY KEN 2026-08-17: Colorado picks them up, line 1 transcribes "
                      "federal as filed. The confirming CDOR authority is still unpulled - re-verify before ship."),
        },
        "facts": CO_FACTS, "rules": CO_RULES, "rule_links": CO_RULE_LINKS,
        "lines": CO_LINES, "diagnostics": CO_DIAGNOSTICS, "scenarios": CO_SCENARIOS,
    },
]

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-CO-SIGNFLIP", "title": "DR 0106 lines 6/8 INVERT the K-1's negatives; lines 3/4 do NOT",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 1,
     "description": ("L6 = -SUM(DR 0106K Col. A L12) and L8 = -SUM(Col. A L13), because the K-1 carries federal "
                     "deductions and Colorado subtractions as NEGATIVE while DR 0106 lines 6/7/8 are entered POSITIVE "
                     "and subtracted at L9/L10. L3 = SUM(Col. A L10) and L4 = SUM(Col. A L9 + L11) are ALREADY "
                     "POSITIVE and must NOT be inverted. Both halves are load-bearing."),
     "definition": {"rule": "R-CO-SIGNFLIP",
                    "check": "L6 == -sum(k1_colA_L12) and L8 == -sum(k1_colA_L13) and L3 == sum(k1_colA_L10) and L4 == sum(k1_colA_L9 + k1_colA_L11)"},
     "bug_reference": "Aggregating without inversion moves line 10 by 2x the deduction total, in the wrong direction"},
    {"assertion_id": "FA-CO-COMP-RECON", "title": "SUM(DR 0106K line 16) == DR 0106 line 13 (composite)",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 2,
     "description": ("Form-asserted, verbatim: 'the amount reported on line 13 of form DR 0106 must equal the sum of "
                     "the amounts reported on line 16 of the Colorado K-1s of all nonresident partners or "
                     "shareholders included in the composite return.' NOT arithmetically automatic - line 12 is an "
                     "aggregate taxed once, while K-1 line 16 is per-owner and floored at zero. They agree only "
                     "because negative-income owners are excluded from line 12 as well (W4)."),
     "definition": {"rule": "R-CO-COMP-RECON", "check": "sum(K1_L16 over included owners) == DR0106_L13"}},
    {"assertion_id": "FA-CO-PTET-RECON", "title": "SUM(DR 0106K line 16) == DR 0106 line 20 (SALT Parity)",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 3,
     "description": ("DR 0106K-I: 'The total amounts entered on all Colorado K-1s must equal the total amounts tax "
                     "calculated and paid by the partnership filing the composite return or making the SALT parity "
                     "election.' Same one-rule construction as the composite reconciliation."),
     "definition": {"rule": "R-CO-PTET-RECON", "check": "sum(K1_L16 over all owners) == DR0106_L20"}},
    {"assertion_id": "FA-CO-MODE-EXCL", "title": "Parts II and III are mutually exclusive; line 21 takes exactly one",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 4,
     "description": ("Line 21 = L16 (Mode B) XOR L20 (Mode C) XOR 0 (Mode A). Both parts populated is a hard RED "
                     "(Sec. 39-22-344(5), C.R.S.). Mode A is a real, common, zero-tax filing that is still mandatory."),
     "definition": {"rule": "R-CO-MODE", "check": "not (partII_populated and partIII_populated); L21 in {L16, L20, 0}"}},
    {"assertion_id": "FA-CO-179-TWOPATH", "title": "Sec. 179 reaches Colorado by TWO paths, and only these two",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 5,
     "description": ("(i) the DISPOSITION gain from the Sch. K 20c / 17d statement -> DR 0106 line 2; (ii) the "
                     "DEDUCTION itself, inside DR 0106K line 12 (1065 K-1 Box 12 / 1120-S K-1 Box 11) -> DR 0106 "
                     "line 6, SIGN-INVERTED. DR 0106 line 2 excludes Sch. K 12/13 and 11/12, so path (ii) is the only "
                     "route for the deduction. Neither is a Colorado modification."),
     "definition": {"rule": "R-CO-L2-FED179",
                    "check": "L2 includes sec179_disposition_gain AND L6 includes -(k1_colA_L12 sec179 component)"},
     "bug_reference": "Verifier correction C3 - the research pass recognised only path (i), leaving the Sec. 179 deduction with no path at all"},
    {"assertion_id": "FA-CO-NO-DEPR-MOD", "title": "No Colorado depreciation modification exists on any line",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 6,
     "description": ("A rule-says-no. No Sec. 168(k) add-back, no state Sec. 179 limit or phaseout, no separate state "
                     "basis, no recapture, no recovery schedule, and NO nullable placeholder field. The only "
                     "depreciation-adjacent items are Boxes B/C (balance-sheet transcription) and the two Sec. 179 "
                     "aggregation paths."),
     "definition": {"rule": "R-CO-DEPR-NEG", "check": "no depreciation modification line exists on CO_DR0106"}},
    {"assertion_id": "FA-CO-TWO-RATES", "title": "Two rate constants with separate statutory authorities",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 7,
     "description": ("CO_COMPOSITE_RATE (line 13) is authorised by C.R.S. Sec. 39-22-104 (INDIVIDUAL rate); "
                     "CO_PTET_RATE (line 20) by C.R.S. Sec. 39-22-301 (CORPORATE rate). Both 0.044 for TY2025. They "
                     "must remain SEPARATE tax-year-keyed constants - LCS projects 4.33% (TY2027) / 4.29% (TY2028)."),
     "definition": {"rule": "R-CO-RATES",
                    "check": "CO_COMPOSITE_RATE[2025] == CO_PTET_RATE[2025] == '0.044' AND they are distinct constants"}},
    {"assertion_id": "FA-CO-K1L16-FLOOR", "title": "DR 0106K line 16 floors at zero for every owner",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 8,
     "description": ("'If the sum ... is a negative amount, enter 0 (zero) on line 16.' Applies in all three variants "
                     "(composite / SALT Parity resident / SALT Parity nonresident). This floor and the exclusion of "
                     "negative-income owners from lines 12, 17 and 18 are ONE RULE."),
     "definition": {"rule": "R-CO-K1-L16", "check": "K1_L16 == max(0, col_amount * rate) for every owner"}},
    {"assertion_id": "FA-CO-GP-EXCLUDED", "title": "Guaranteed payments: in DR 0106 line 2, out of every tax base",
     "assertion_type": "flow_assertion", "entity_types": ["1065"], "status": "draft", "sort_order": 9,
     "description": ("1065 Sch. K line 4c IS inside DR 0106 line 2, but DR 0106K line 4 is skipped by Part II, "
                     "Part III and K-1 line 16 alike, and the nonresident partner must file their own Colorado return "
                     "for them. A three-place rule (W5). N/A for an S corporation (F3)."),
     "definition": {"rule": "R-CO-COMPOSITE",
                    "check": "L2 includes schK_4c AND L12/L17/L18/K1_L16 all exclude K1 line 4"}},
    {"assertion_id": "FA-CO-PARTV-FEED", "title": "Part V feeds the DR 0106K, not Parts II/III; line 14 is a dead end",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 10,
     "description": ("Part V line 8 (both columns) -> DR 0106K line 14; Part V lines 10 and 13 -> DR 0106K line 15. "
                     "NOTHING on the DR 0106 face consumes Part V line 12, 13(f) or 14. The Part II and Part III "
                     "bases are built from the K-1s, not from Part V. Wiring Part V line 14 into either part is wrong."),
     "definition": {"rule": "R-CO-PARTV-FEED",
                    "check": "PV_L8 -> K1_L14; PV_L10/PV_L13 -> K1_L15; no DR0106 line reads PV_L12/PV_L13f/PV_L14"}},
    {"assertion_id": "FA-CO-MODULE-FORK", "title": "The module fork keys off the federal return, never Box A",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 11,
     "description": ("16 forks (F1-F16); 14 change the arithmetic. Box A is LEGAL FORM - an LLC taxed as a "
                     "partnership marks 'LLC', and six of Box A's eight values are silent on 1065-vs-1120S. "
                     "Reinforced by DR 0106 p. 1: classification follows the federal return."),
     "definition": {"rule": "R-CO-MODULE-FORK", "check": "module derived from federal_return_type, never box_a_legal_form"}},
    {"assertion_id": "FA-CO-CR-COLC-ZERO", "title": "Not filing composite -> DR 0106CR column C is zero",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 12,
     "description": ("In Mode A and Mode C the DR 0106CR carries column B = column A and column C = 0, so DR 0106 "
                     "lines 14 and 15 are blank. For Mode C this is also statutory: an electing entity 'may not claim "
                     "any refundable or nonrefundable credits on its return' (Sec. 39-22-344(3), C.R.S.). The "
                     "DR 0106CR remains a MANDATORY attachment in every mode. Line 38 sums lines 5 through 37 only."),
     "definition": {"rule": "R-CO-CR-COLS",
                    "check": "mode != B -> (colB == colA and colC == 0 and L14 == 0 and L15 == 0); L38 == sum(L5..L37)"}},
]


# ═══════════════════════════════════════════════════════════════════════════
# Command
# ═══════════════════════════════════════════════════════════════════════════

class Command(BaseCommand):
    help = (
        "Load the CO DR 0106 spec (Colorado Partnership and S Corporation Income Tax Return, TY2025). "
        "ONE form, TWO modules (1065 + 1120S), 16 forks. Gate 1 cleared 2026-08-17: the walk (W1-W12) was "
        "approved and the [UNV-7] Sec. 174A rolling-conformity question (W13) was RULED - Colorado picks up "
        "retroactive federal amendments, so line 1 transcribes federal as filed."
    )

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad CO DR 0106 spec (Colorado Partnership and S Corporation Income Tax Return)\n"))
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
                "\nREFUSING TO SEED CO DR 0106: not cleared to seed.\n\n"
                "Gate 1 was CLEARED for this form on 2026-08-17 (Ken's in-session walk,\n"
                "delvio-states/dispatch/WAVE3_WALK.md). Both original gates are satisfied:\n\n"
                "  (1) The Gate-1 walk over W1-W12 - approved as proposed, including W1\n"
                "      (direct-enter Column B), W3 (the three-mode machine), W6 (the\n"
                "      depreciation NEGATIVE blessed as a ruling), W7 (two rate constants),\n"
                "      and W9 / walk item B2 (the >$5,000 threshold, ruled strictly-greater\n"
                "      on the Corporate Income Tax Guide side of a live 3-2 source split).\n\n"
                "  (2) W13 / [UNV-7] - whether Colorado's ROLLING CONFORMITY\n"
                "      (Sec. 39-22-103(5.3), C.R.S.) reaches RETROACTIVELY-EFFECTIVE federal\n"
                "      amendments such as OBBBA's small-business Sec. 174A R&D election.\n"
                "      RULED (walk item A1): it DOES. DR 0106 LINE 1 transcribes federal\n"
                "      ordinary income as filed; no adjustment is computed in either\n"
                "      direction. The deciding fact is structural - this form has NO\n"
                "      modification line anywhere to carry a divergence, so no other\n"
                "      position is expressible on its face. [UNV-7] remains OPEN as a\n"
                "      pre-ship confirmation item (no published CDOR authority backs it).\n\n"
                "So if you are reading this, something ELSE is wrong - most likely a data\n"
                "list was emptied, or READY_TO_SEED was flipped back deliberately.\n\n"
                f"READY_TO_SEED = {READY_TO_SEED} (must be True to proceed)\n\n"
                f"Currently empty / placeholder:\n  {still_empty}\n\n"
                "Do NOT relax this guard to silence the error - fix the cause. The module-\n"
                "level data lists and delvio-states/research/co_pte_source_brief.md (its\n"
                "Sec. 17 Verification section GOVERNS over the body) are the references.\n"
                "Idempotent via update_or_create."
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
                self.stdout.write(self.style.WARNING(
                    f"  existing source {code} NOT FOUND - links to it will be skipped"))
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
        self.stdout.write("CO DR 0106 loaded.")
        self.stdout.write(
            f"  {FORM_CODE}: facts {len(CO_FACTS)} / rules {len(CO_RULES)} / lines {len(CO_LINES)} / "
            f"diag {len(CO_DIAGNOSTICS)} / tests {len(CO_SCENARIOS)} / FA {len(FLOW_ASSERTIONS)} / "
            f"forks {CO_FORKS_TOTAL} ({CO_FORKS_ARITHMETIC} arithmetic)"
        )
        self.stdout.write("=" * 60)
