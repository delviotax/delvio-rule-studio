"""Load the VA PTE specs — Virginia Form 502 + Form 502PTET (TY2025), ONE loader, TWO form codes.

═══════════════════════════════════════════════════════════════════════════
WHAT THIS IS
═══════════════════════════════════════════════════════════════════════════
Virginia does NOT have a partnership return and an S-corporation return. It has
ONE pass-through entity return — **Form 502** — filed by both, and one elective
alternative — **Form 502PTET** — filed INSTEAD OF Form 502. So two RS form codes
(`VA_502`, `VA_502PTET`, campaign D-9) serve BOTH the 1065 and the 1120S modules:
`entity_types = ["1065", "1120S"]` on each.

    1065  ─┐                                    ┌─ VA_502     (default; withholding return)
           ├→ Form 502 Page 1 (identical) ──────┤
    1120S ─┘                                    └─ VA_502PTET (5.75% elective entity tax)
                                                     ↓
                                        Schedule VK-1 per owner (identical both paths)

Page 1 (Lines 1–20) is line-for-line IDENTICAL on the two forms — only the
adjustment schedule name changes (Schedule 502ADJ → Schedule PTET ADJ). The forms
diverge completely on Page 2 (withholding reconciliation vs. 5.75% entity tax), on
the penalty regime (Article 9 vs. Article 14 CORPORATE), and — the trap — on the
**base**: Form 502 Line 1 is income ONLY, while Form 502PTET **Section I Line 1**
(page 2) is income NET OF DEDUCTIONS with §179 and charitable contributions
re-limited to the federal C-corporation limits. Cloning 502 into 502PTET gets this
wrong. See `_va_502_line1` vs `_va_ptet_section_i_line1`.

Spec source: `delvio-states/research/va_pte_source_brief.md` — **VERIFIED**
(adversarial pass 2026-08-16); its §16 Verification section SUPERSEDES the body and
its corrections C1–C7 are folded in here. Conformity posture:
`delvio-states/conformity/va_conformity.md` (VERIFIED 2026-08-06), §12 governs.

Gap check: `lookup/VA_502/export/` → 404. NEW forms. First Virginia spec in RS.

═══════════════════════════════════════════════════════════════════════════
THE SIX MODULE BRANCH POINTS (brief §2.1) — encoded as real distinctions
═══════════════════════════════════════════════════════════════════════════
The branch is NOT in the computation. Lines 1–20 are literally the same lines for
both modules. It lives in six places, all carried by `_va_module_branch()`:

  1. Entity Type code (face, required) — partnership PG/PL/LL/LP/NZ/OB · S corp **SC**
  2. Owner-count source (face Line a) — 1065 Page 1 item I (number of Schedules K-1)
     · 1120-S Page 1 item I (number of shareholders during any part of the year).
     SAME LETTER, DIFFERENT MEANING — both verified on the FINAL 2025 IRS forms.
  3. Participation-% source (VK-1 Line d) — 1065 K-1 item J ENDING PROFIT %
     · 1120-S K-1 item **G**, taken AS PRINTED (`Current year allocation percentage`;
     do NOT "correct" it to a stock ratio computed from item H — C7).
  4. Participation Type code (VK-1 Line c) — GPT/LPT/LLM/OTR · S corp **SHR**
  5. Required federal enclosure — `Form 1065 with Schedule K` · `Form 1120-S with
     Schedule K` (no federal K-1; no K-2/K-3).
  6. Bank Franchise Tax — an **S-CORP-ONLY** consequence: Schedule 502ADJ Code 99
     addition / Code 99 subtraction → owner deduction **Code 112**.

Plus one 502PTET-only S-corp divergence: an electing S corporation may compute
Virginia taxable income AS IF ALL OWNERS WERE NONRESIDENTS and report entirely in
Column A. No partnership analogue, and **no checkbox exists** (U9).

═══════════════════════════════════════════════════════════════════════════
v1 SCOPE — PROPOSED (brief §14; Ken's Gate-1 walk pending)
═══════════════════════════════════════════════════════════════════════════
COMPUTES:
  • Page 1 Lines 1–20 both forms — the printed 12-line Line-1 worksheet with the DOR
    `Caution` surfaced (W9); L13 = ΣL8..L12; L18 = ΣL14..L17; the wholly-Virginia
    short path (L4/L5 blank, L6 = L1, L7 = 100%).
  • Schedule 502A Section B ÷4 double-weighted sales, incl. the missing-factor
    denominator reduction; Section C Lines 1–4 incl. the commercial-domicile branch
    and the three feeds to Form 502 Lines 4/5/6. **NOTE C5: Schedule 502A Section C
    is NOT a renumbering of Schedule 500A — 500A has no Section C and applies the
    percentage on the schedule; 502A has NO percentage-application line at all.**
  • Schedule 502ADJ / PTET ADJ Sections A/B (10 addition codes, 20 subtraction codes
    — C3) and the ENUMERATED Section C Part II / Part IV totals (never a range).
  • Schedule VK-1 fan-out + the cross-form assertion set (§6.1).
  • Form 502 Page 2 — the ENTIRE withholding return: 5% per nonresident owner with
    day-count proration and per-owner zero floor, the Extension Penalty Worksheet,
    the $1,200 late-filing penalty, and Line 10's FOUR-BRANCH conditional verbatim.
  • Form 502PTET Page 2 — Section I two-column build with the PER-COLUMN zero floor,
    5.75% on Line 7a, Line 7 = 7a + 7b, Sections III/IV/V, Form 500C, the corporate
    penalty regime, and the $1,000 estimate threshold.
  • Both due-date clocks and the never-extends payment rule.
  • Filing-mode gates: 502/502PTET mutual exclusivity, the PTET 6-month HARD BAR,
    Form 765 barred for electing PTEs, single-member-LLC and investment-PTE "no
    filing required", the 13-criterion 502EZ eligibility CHECK.

DIRECT-ENTRY (line exists; each with a diagnostic prompt):
  • Lines 8, 9, 14, 15 — the four conformity lines (W5).
  • Every 502ADJ / PTET ADJ / SVK-1 coded modification AMOUNT (engine supplies the
    code table, citation, owner-side translation and subtotal).
  • Lines 10, 11, 16 — with Line 10's explicit "NOT the same as 502ADJ C-I-1" warning.
  • Schedule 502A factor numerators/denominators and the Section B Line 1 single
    factor for any of the eight enumerated method boxes.
  • Form 502PTET Line 7(b) — pre-filled 5% × nonresident corporate share, flagged (W4).
  • All credit amounts except PTET ADJ C-III-10 (computed from Line 7a).
  • Interest lines; the owner roster.

RED-DEFER — R1..R16, EACH WITH ITS OWN DIAGNOSTIC (no silent gap):
  R1  Form 502EZ (eForms short form)          R9   Form TCA credit allocation
  R2  the Virginia depreciation shadow book   R10  tiered-PTE withholding
  R3  §174A retroactive / catch-up            R11  entity-level R&D on 502PTET (U10)
  R4  Schedule 502A Section A boxes 1–8       R12  undue-hardship waiver requests
  R5  502A Section C 3(b)/3(d) Allied-Signal  R13  Bank Franchise Tax S corporations
  R6  Form 502FED-1 / 502FED-2 (1065 ONLY)    R14  alternative apportionment method
  R7  Schedule 500AB                          R15  Form 500HS
  R8  Form 765 composite                      R16  Schedule VK-1 Consolidated

═══════════════════════════════════════════════════════════════════════════
requires_human_review WALK ITEMS — W1..W11 (brief §13, as amended by §16.5)
═══════════════════════════════════════════════════════════════════════════
W1.  ONE SPEC OR TWO. Recommendation taken: **two form codes sharing a Page-1 rule
     block** (campaign D-9 already names VA_502 / VA_502PTET). CONFIRM.
W2.  ⚠ RE-WORDED per correction C1. The ruling Ken is asked to bless is NOT "H.R.1
     goes on Line 9." It is: **route the RESIDUAL CONFORMITY BUCKET to Lines 9(2) /
     15(2), of which H.R.1 is one component.** The `Conformity Update for 2025`
     section lists the H.R.1 trio AND the §163(j) 20% change AND six continuing
     deconformities (bonus, 2008/09 NOL carryback, AHYDO, COD income, CARES-Act
     items, COVID small-business expenses). The word **"other"** in Line 9(2) is what
     excludes bonus depreciation, which Lines 8 and 9(1) already carry by name.
     Lines 8/14 are textually scoped to bonus 2001–2025 and nothing else. No 502ADJ
     code covers it; no DOR worksheet exists ("enclose a schedule and explanation").
     `requires_human_review` on every return where the bucket is non-zero. Open: U1.
W3.  ⚠ **VIRGINIA PUBLISHES NO §179 DOLLAR FIGURE — none is seeded here.**
     `VA_179_PUBLISHED[2025] is None`. The $1,250,000 / $3,130,000 / $31,300 figures
     are DERIVED from Rev. Proc. 2024-40 §3.25 through TB 26-1's "as if the 2025
     H.R. 1 changes had not been enacted", and are carried in a separately named
     constant that says so. The federal OBBBA $2,500,000 / $4,000,000 must NEVER be
     used for Virginia. Ken is the depreciation specialist — his call. Open: U2.
W4.  The **5%** on Form 502PTET Line 7(b) is carried over from a DIFFERENT FORM. The
     entire 14-page 502PTET package states no rate (boundary-anchored regex confirms
     zero standalone "5%", zero "five percent"). Statutory anchor is solid:
     § 58.1-486.2 B.1. Direct-entry with the computed value pre-filled + review flag.
     THIS ONE MOVES MONEY. Open: U3.
W5.  Virginia depreciation shadow book in v1 or v1.1. Taken: **v1 direct-entry Lines
     8/9/14/15 with a hard RED when federal bonus or H.R.1 expensing is present and
     the Virginia line is blank; v1.1 the Virginia-basis engine.** CONFIRM.
W6.  Compute the withholding leg (it is why Form 502 exists), RED-defer only the
     tiered-PTE case (R10). CONFIRM.
W7.  ✅ EFFECTIVELY DECIDED by the verification pass. `Va. Code § 58.1-392 E` —
     "Waivers shall be granted only if the Tax Commissioner finds that the requirement
     creates an unreasonable burden" — and § 58.1-390.3 A.2 makes Form 502PTET a
     § 58.1-392 return. So the package's "Waivers… will not be granted" is an
     ADMINISTRATIVE POSTURE, not a legal impossibility. Build e-file-only as POLICY;
     **never** a diagnostic asserting a waiver cannot exist (R12 states it positively).
W8.  Credit allocation arithmetic computed, credit AMOUNTS direct-entry; preserve the
     TWO allocation classes as data (16 pro-rata; **5** may be allocated "as the
     owners may mutually agree"). CONFIRM.
W9.  The Form 502 Line 1 build is a Virginia-only summation with an explicit DOR
     warning against naïvely summing Schedule K. Built as a REAL VISIBLE 12-line
     worksheet with the `Caution` as help copy, plus a required preparer affirmation
     fact (`l1_no_double_count_confirmed`). CONFIRM.
W10. ✅ EFFECTIVELY DECIDED. `Va. Code § 58.1-392 A` puts Form 502 / 502PTET on the
     **15th day of the 4th month** (April 15). Form 760 / 770 are on **May 1**. BOTH
     ARE TRUE AT ONCE. The string "May 1" appears ZERO times in the 29-page 502 book
     and ZERO times in the 14-page PTET package. A single "Virginia due date"
     constant is wrong on one side or the other. Bless explicitly.
W11. Form 502FED-1 / 502FED-2 (partnership-only) RED-deferred (R6). CONFIRM.

═══════════════════════════════════════════════════════════════════════════
[UNVERIFIED] / OPEN ITEMS CARRIED FORWARD — U1..U15 (brief §12)
═══════════════════════════════════════════════════════════════════════════
U1.  Whether Lines 9(2)/15(2) genuinely carry the H.R.1 conformity adjustment, and
     whether a DOR worksheet exists. NARROWED (C1) to a residual bucket. Two new
     corroborations: the corporate Form 500 book routes identically at Schedule
     500ADJ Section A Line 2, and TB 26-1 calls it a "fixed date conformity
     addition/subtraction". TB 26-1's promised web guidance page DOES NOT EXIST.
U2.  Virginia's own §179 limit / phase-out. Confirmed absent from THREE instruction
     books (502, 502PTET, corporate 500). No figure seeded. See W3.
U3.  The rate and base for Form 502PTET Line 7(b). See W4.
U4.  The repealed PTET sunset is STILL PRINTED — **six times** (C2) — in a package the
     DOR RE-ISSUED on 2026-08-10, five and a half months after the repeal; and the
     Form 502 instruction book contradicts itself between p.1 and p.3.
     `Va. Code § 58.1-390.3` contains NO expiration date. **BUILD TO THE STATUTE.**
     No sunset is encoded; a diagnostic explains the dead form text instead.
U5.  Whether an estimated or extension payment is LEGALLY sufficient to make the PTET
     election. The statute names only the timely filed return; the payment-as-election
     acts rest on DOR Guidelines / TB 22-6 / TB 23-3, neither obtained. It matters —
     it is exactly what rescues a filer past the 6-month bar.
U6.  How 502PTET Section I Lines 2 and 4 derive the ELIGIBLE-OWNER share of Page 1
     Lines 13 and 18. Page 1 is expressly whole-entity; no line, ratio or worksheet is
     provided. Working assumption: eligible owners' aggregate participation %.
U7.  Schedule 502ADJ Section D Line 5's label is TRUNCATED on the FINAL form face
     (reproduced byte-for-byte). Arithmetic forced by Line 6's mirror.
U8.  (a) Schedule PTET ADJ Part II has no readable label in the FINAL PDF.
     (b) The VK-1 Consolidated field list says "nonrefundable credits from Part IV" —
     but Part IV is the REFUNDABLE total. DOR erratum.
U9.  The 502PTET S-corp "treat all owners as nonresidents" option has NO CHECKBOX, no
     statutory cite, no stated scope. Detectable only by an empty Column B.
U10. Form 502PTET Line 10 names the Research and Development Tax Credit, but 10b and
     10c are both printed `Reserved for future use`. → R11.
U11. Whether a 502PTET e-file hardship waiver is genuinely unavailable. STRENGTHENED
     by § 58.1-392 E → decided as policy, not invariant. See W7.
U12. Form 502FED-1 / 502FED-2 line maps NOT obtained. Blocks nothing (R6 defers them).
U13. Tax-exempt interest section-name mismatch for the 1120-S module: VA says "the
     'Other' section", but 1120-S Line 16a sits under `Items Affecting Shareholder
     Basis`. Cosmetic — same figure. Recorded so nobody "fixes" the mapping.
U14. Virginia MeF schema and business rules NOT obtained — behind the software-provider
     Letter of Intent gate (per-product LOI to vendors@tax.virginia.gov; TY2025 LOI was
     due Nov 3 2025, ATS accepted by Jan 30 2026; the TY2026 analogue ≈ Nov 3 2026).
     **This is the single thing that would settle U1, U3, U6, U8 and U15 at once, and it
     is a lead-time-bearing Ken action.**
U15. The Form 502 instructions CONTRADICT THEMSELVES on when Schedule VK-1 Consolidated
     is required (instr. p.19 universal vs. p.20 waived-paper-filers-only). Working
     assumption: specific governs — a waived-paper artifact only (R16). Do NOT build a
     rule requiring a Consolidated on every e-filed return.

═══════════════════════════════════════════════════════════════════════════
VERIFIED STRUCTURE (read 2026-08-16/17 from the FINAL TY2025 Virginia DOR PDFs, the
FINAL 2025 IRS forms and law.lis.virginia.gov — NEVER memory. Form 502 Rev. 07/26 ·
Sch 502A Rev. 07/26 · Sch 502ADJ Rev. 07/26 · Sch VK-1 Rev. 07/26 · Form 502W
Rev. 07/26 · 2025 Form 502 Instructions Rev. 4/2026 · 2025 Form 502PTET Instruction
Package **Rev. 08/26, RE-ISSUED 2026-08-10** · Tax Bulletin 26-1 · Va. Code
§§ 58.1-301, -332, -390.1, -390.3, -391, -392, -408, -486.1, -486.2, 55.1-1200.)
═══════════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════
SAFETY GUARD — READY_TO_SEED ships False and STAYS False until Ken approves the
Gate-1 walk (W1–W11) in-session. Until then the command refuses to write to the DB.
DO NOT relax the guard to silence the error. DO NOT COMMIT. DO NOT SEED.
═══════════════════════════════════════════════════════════════════════════
"""
import math

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
# SAFETY GUARD — flip ONLY after Ken's in-session Gate-1 walk (W1-W11 above).
# NOT YET WALKED. NOT APPROVED. Ships False by design.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = False


FORM_JURISDICTION = "VA"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"

# BOTH forms serve BOTH modules — S corporations are pass-through entities for
# Virginia purposes and there is no Virginia 1120-S analogue (brief §2).
FORM_ENTITY_TYPES = ["1065", "1120S"]


# ═══════════════════════════════════════════════════════════════════════════
# VERIFIED CONSTANTS — year-keyed. Every figure cited in va_pte_source_brief.md.
# ═══════════════════════════════════════════════════════════════════════════

# PTET rate — Va. Code § 58.1-390.3 B, verbatim "A tax at the rate of 5.75 percent".
VA_PTET_RATE: dict[int, str] = {2025: "0.0575"}

# Nonresident withholding rate — Va. Code § 58.1-486.2 B.1, verbatim "five percent
# of the nonresident owner's share of income from Virginia sources".
VA_NR_WITHHOLDING_RATE: dict[int, str] = {2025: "0.05"}

# ── TWO DUE-DATE CLOCKS (W10). BOTH ARE TRUE AT ONCE. ──────────────────────
# Entities: Va. Code § 58.1-392 A — "the fifteenth day of the fourth month".
VA_ENTITY_DUE_MONTH: dict[int, int] = {2025: 4}
VA_ENTITY_DUE_DAY: dict[int, int] = {2025: 15}
# Individuals (Form 760) and fiduciaries (Form 770): MAY 1. NOT the entity date.
VA_INDIVIDUAL_DUE_MONTH_DAY: dict[int, tuple] = {2025: (5, 1)}
# Automatic extension: 6 months, OR 30 days after the federal extended due date,
# WHICHEVER IS LATER. The extension NEVER extends the payment date.
VA_EXTENSION_MONTHS: dict[int, int] = {2025: 6}
VA_EXTENSION_FED_PLUS_DAYS: dict[int, int] = {2025: 30}
VA_PAYMENT_DATE_EXTENDS: dict[int, bool] = {2025: False}

# ── Apportionment (Va. Code § 58.1-408; Schedule 502A Section B Line 2) ────
# Three-factor, DOUBLE-WEIGHTED SALES, divided by 4. NOT single sales factor.
VA_APPORT_WEIGHTS: dict[int, dict] = {2025: {"property": 1, "payroll": 1, "sales": 2}}
VA_APPORT_DIVISOR: dict[int, int] = {2025: 4}
VA_RENT_MULTIPLIER: dict[int, int] = {2025: 8}          # rented property at 8x annual rent
VA_APPORT_DECIMALS: dict[int, int] = {2025: 6}
VA_MARKET_SOURCING_GENERAL: dict[int, bool] = {2025: False}   # COST OF PERFORMANCE for non-TPP
VA_THROWBACK_RULE: dict[int, bool] = {2025: False}            # zero occurrences in the sources

# ── §179: VIRGINIA PUBLISHES NO FIGURE. (W3 / U2) ─────────────────────────
# This is the whole point: `None` is the Virginia value. Do NOT seed a number here.
VA_179_PUBLISHED: dict[int, None] = {2025: None}
# DERIVED ONLY — Rev. Proc. 2024-40 §3.25 applied through TB 26-1's "as if the 2025
# H.R. 1 changes had not been enacted". NOT a Virginia source. Configurable, with a
# Virginia-source TODO that must be closed before this is relied on.
VA_179_DERIVED_NOT_VA_SOURCED: dict[int, dict] = {
    2025: {
        "limit": 1250000,
        "phaseout": 3130000,
        "suv_sublimit": 31300,
        "provenance": "DERIVED from Rev. Proc. 2024-40 s.3.25 — NOT a Virginia source (U2/W3)",
    }
}
# NEVER USE THESE FOR VIRGINIA. Kept only so the harness can prove they are absent.
FEDERAL_OBBBA_179_DO_NOT_USE: dict[int, dict] = {2025: {"limit": 2500000, "phaseout": 4000000}}

# ── Conformity (conformity brief §2; TB 26-1; Va. Code § 58.1-301) ─────────
VA_CONFORMITY_TYPE: dict[int, str] = {2025: "static"}
VA_CONFORMITY_DATE: dict[int, str] = {2025: "2025-12-31"}
VA_OBBBA_IN: dict[int, bool] = {2025: True}             # fixed date POST-DATES 7/4/2025
VA_BONUS_CONFORMS: dict[int, bool] = {2025: False}      # never has, does not now
VA_BONUS_VINTAGE_WINDOW: dict[int, tuple] = {2025: (2001, 2025)}
# The Line 9(2)/15(2) bucket is WIDER THAN H.R.1 (correction C1). Membership list:
VA_CONFORMITY_BUCKET_MEMBERS: tuple = (
    "IRC 168(n) qualified production property (H.R.1)",
    "IRC 174A domestic R&E expensing incl. retroactive/catch-up (H.R.1)",
    "IRC 179 expensing-limit increases (H.R.1)",
    "applicable high yield discount obligations (AHYDO)",
    "cancellation of debt income on certain business debts",
    "five-year carryback of 2008/2009 NOLs",
    "certain business provisions of the federal CARES Act",
    "business expenses through COVID small-business assistance pre-TY2021",
)
# Bonus depreciation is EXCLUDED from the bucket — Lines 8 and 9(1) carry it by name,
# and Line 9(2) says "any OTHER conformity additions". That word is the whole mechanism.
VA_BUCKET_EXCLUDES_BONUS: dict[int, bool] = {2025: True}
# §163(j): Virginia conforms to the federal limitation; the Virginia SUBTRACTION for
# federally disallowed business interest drops 50% (TY2024) -> 20% (TY2025+).
VA_BUSINESS_INTEREST_PCT: dict[int, str] = {2025: "0.20", 2024: "0.50"}

# ── Form 502 Page 2 — withholding penalties and thresholds ────────────────
VA_WH_SAFE_HARBOR: dict[int, dict] = {2025: {"current_year_pct": 0.90, "prior_year_pct": 1.00}}
VA_WH_EXT_PENALTY_PCT_PER_MONTH: dict[int, float] = {2025: 0.02}
VA_WH_EXT_PENALTY_CAP: dict[int, float] = {2025: 0.12}
VA_WH_EXT_PENALTY_MONTH_DAYS: dict[int, int] = {2025: 30}   # count in 30-day increments, round UP
VA_WH_LATE_PAYMENT_PCT: dict[int, float] = {2025: 0.30}     # Page 2 Line 6 = 30% of Line 4
VA_502_LATE_FILING_FLAT: dict[int, int] = {2025: 1200}      # Page 2 Line 9 — flat $1,200
VA_502_LATE_PAY_MONTHLY: dict[int, float] = {2025: 0.06}
VA_502_LATE_PAY_MAX: dict[int, float] = {2025: 0.30}
# Assessed by the Department, NEVER computed by the software (informational only).
VA_502_ASSESSED_INCOME_PENALTY_PCT: dict[int, float] = {2025: 0.06}

# ── Form 502PTET — CORPORATE penalty regime (Article 14), NOT the Form 502 one ──
VA_PTET_ESTIMATE_THRESHOLD: dict[int, int] = {2025: 1000}
VA_PTET_ESTIMATE_INSTALLMENTS: dict[int, int] = {2025: 4}
VA_PTET_ESTIMATE_PCT: dict[int, float] = {2025: 0.25}
VA_PTET_ESTIMATE_DATES_CY: dict[int, tuple] = {2025: ("04-15", "06-15", "09-15", "12-15")}
VA_PTET_ESTIMATE_MONTHS_FY: dict[int, tuple] = {2025: (4, 6, 9, 12)}
VA_PTET_EXT_PENALTY_PCT_PER_MONTH: dict[int, float] = {2025: 0.02}
VA_PTET_LATE_PAY_MONTHLY: dict[int, float] = {2025: 0.06}
VA_PTET_LATE_PAY_MAX: dict[int, float] = {2025: 0.30}
VA_PTET_LATE_FILE_PCT: dict[int, float] = {2025: 0.30}
# "In no case will the penalty for failure to file timely be less than $100, and this
# minimum $100 penalty applies WHETHER OR NOT TAX IS DUE."
VA_PTET_LATE_FILE_MINIMUM: dict[int, int] = {2025: 100}
VA_PTET_90PCT_EXT_THRESHOLD: dict[int, float] = {2025: 0.90}
# Form 500C Part II exception percentages.
VA_500C_EX1_PCTS: dict[int, tuple] = {2025: (0.25, 0.50, 0.75, 1.00)}
VA_500C_EX2_PCTS: dict[int, tuple] = {2025: (0.25, 0.50, 0.75, 1.00)}
VA_500C_EX3_PCTS: dict[int, tuple] = {2025: (0.225, 0.45, 0.675, 0.90)}
VA_500C_90PCT: dict[int, float] = {2025: 0.90}
VA_500C_QUARTER_PCT: dict[int, float] = {2025: 0.25}

# Interest and bad-payment charge (both regimes).
VA_INTEREST_BASIS: dict[int, str] = {2025: "IRC 6621 + 2%"}
VA_BAD_PAYMENT_PENALTY: dict[int, int] = {2025: 35}

# ── PTET permanence — U4. The STATUTE has NO expiration date. ─────────────
# The re-issued Rev. 08/26 package still prints the repealed sunset SIX times. Dead text.
VA_PTET_SUNSET_YEAR: dict[int, None] = {2025: None}
VA_PTET_SUNSET_IN_FORM_TEXT_IS_DEAD: dict[int, bool] = {2025: True}
VA_PTET_STALE_SUNSET_RECITALS: dict[int, int] = {2025: 6}
VA_PTET_ELECTION_BINDING: dict[int, bool] = {2025: True}
VA_PTET_OWNER_CREDIT_REFUNDABLE: dict[int, bool] = {2025: True}
# Three election acts per the DOR; the STATUTE names only the third (U5).
VA_PTET_ELECTION_ACTS: tuple = ("estimated_payment", "extension_payment", "timely_filed_return")
VA_PTET_ELECTION_ACTS_IN_STATUTE: tuple = ("timely_filed_return",)
VA_PTET_HARD_BAR_MONTHS: dict[int, int] = {2025: 6}

# ── E-file posture (W7 / U11): POLICY, never a legal invariant ────────────
VA_502_EFILE_MANDATORY: dict[int, bool] = {2025: True}
VA_502_EFILE_WAIVER_AVAILABLE: dict[int, bool] = {2025: True}
VA_PTET_EFILE_MANDATORY: dict[int, bool] = {2025: True}
VA_PTET_EFILE_WAIVER_POLICY_DEFAULT: dict[int, bool] = {2025: False}
# Va. Code § 58.1-392 E expressly contemplates waivers, and Form 502PTET IS a
# § 58.1-392 return. So a waiver is legally POSSIBLE even though the DOR says it will
# not grant one. NEVER write a diagnostic asserting a waiver cannot exist.
VA_PTET_EFILE_WAIVER_LEGALLY_POSSIBLE: dict[int, bool] = {2025: True}

# ── Schedule 502ADJ code tables — COUNTS CORRECTED per C3 (10 / 20) ───────
VA_ADJ_ADDITION_CODES: tuple = (10, 13, 14, 15, 16, 18, 21, 22, 23, 99)
VA_ADJ_SUBTRACTION_CODES: tuple = (10, 11, 12, 13, 14, 16, 17, 20, 21, 22, 43, 48, 49, 50, 51, 52, 56, 57, 58, 99)
# "PTE reports it under one code; the OWNER deducts it under a DIFFERENT code."
VA_OWNER_CODE_TRANSLATIONS: dict = {
    "sub_43": "owner deduction Code 107 (Virginia Public School Construction Grants)",
    "sub_48": "owner deduction Code 108 (Tobacco Quota Buyout)",
    "sub_56": "owner deduction Code 116 (business interest, 20% of s.163(j)-disallowed)",
    "add_22": "owner NEGATIVE deduction (business interest recapture)",
    "code_99_bank_franchise": "owner deduction Code 112, Schedule ADJ Line 8a (S corp only)",
}

# ── Schedule 502ADJ / PTET ADJ Section C — ENUMERATED totals, never a range ──
# Part I has 27 numbered slots with NINE Reserved (C4): 9, 10, 11, 16, 18, 19, 20, 22, 24.
VA_CREDIT_PART1_RESERVED: tuple = (9, 10, 11, 16, 18, 19, 20, 22, 24)
VA_CREDIT_PART2_SUMMANDS: tuple = (1, 2, 3, 4, 5, 6, 7, 8, 12, 13, 14, 15, 17, 21, 23, 25, 26, 27)
VA_CREDIT_PART3_SLOTS: tuple = (1, 7, 9)                 # refundable, on Schedule 502ADJ
VA_CREDIT_PART4_SUMMANDS_502: tuple = (1, 7, 9)          # Schedule 502ADJ Part IV
VA_CREDIT_PART4_SUMMANDS_PTET: tuple = (1, 7, 9, 10)     # Schedule PTET ADJ gains Line 10
# The 5 credits that may be allocated "as the owners may mutually agree" (all others pro rata).
VA_CREDITS_FREE_ALLOCATION: tuple = (5, 12, 13, 14, 27)
VA_CREDITS_PRO_RATA_COUNT: dict[int, int] = {2025: 16}
VA_PTE_COMPUTES_CARRYOVERS: dict[int, bool] = {2025: False}

# ── Code tables carried as data (verbatim from the instructions) ──────────
VA_ENTITY_TYPE_CODES_PARTNERSHIP: tuple = ("PG", "PL", "LL", "LP", "NZ", "OB")
VA_ENTITY_TYPE_CODE_SCORP: str = "SC"
VA_PARTICIPATION_CODES_PARTNERSHIP: tuple = ("GPT", "LPT", "LLM", "OTR")
VA_PARTICIPATION_CODE_SCORP: str = "SHR"
VA_OWNER_ENTITY_TYPE_CODES: tuple = ("RES", "NON", "PG", "PL", "LL", "LP", "SC", "CC", "TE", "NZ", "OB")
# ENTITY-level withholding exemption codes (Form 502 Line d) — a SUBSET of the owner codes.
VA_ENTITY_EXEMPTION_CODES: tuple = ("03", "04", "06", "07")
# OWNER-level withholding exemption codes (VK-1 Line f) — a SUPERSET.
VA_OWNER_EXEMPTION_CODES: tuple = ("01", "02", "03", "04", "05", "06", "07")
VA_AMENDED_REASON_CODES: tuple = ("02", "03", "04", "05", "10", "11", "30")
VA_APPORT_METHOD_BOXES: tuple = (1, 2, 3, 4, 5, 6, 7, 8, 9)   # box 9 = the default ÷4 formula

# 502EZ eligibility gate (R1) — all 13 criteria must be met.
VA_502EZ_MAX_OWNERS: dict[int, int] = {2025: 10}
VA_502EZ_MAX_TAXABLE_INCOME: dict[int, int] = {2025: 40000}
VA_502EZ_MAX_MODIFICATIONS: dict[int, int] = {2025: 1000}

# Cross-form structural invariants (brief §6.1).
VA_VK1_MIRROR_LINES: tuple = (1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 13, 18)
VA_VK1_PER_OWNER_LINES: tuple = (7,)        # Line 7 is the SAME for every owner, never summed
VA_VK1_PARTICIPATION_TOTAL: str = "100.00"

# Days in the withholding proration year.
VA_WH_PRORATION_DAYS: dict[int, int] = {2025: 365}


def _yk(d: dict, year: int = FORM_TAX_YEAR):
    """Year-keyed constant lookup, defaulting to the authored year."""
    return d.get(year) if d.get(year) is not None or year in d else d[FORM_TAX_YEAR]


# ===========================================================================
# HELPERS - the arithmetic, exposed so scratchpad/validate_va.py can oracle it.
# Every one is transcribed from the brief, never from memory.
# ===========================================================================

def _va_module_branch(module: str) -> dict:
    """The SIX places where the 1065 and 1120S modules diverge (brief Sec.2.1).

    Form 502 Lines 1-20 are literally the same lines for both. The branch is here.
    """
    if module not in ("1065", "1120S"):
        raise ValueError(f"module must be '1065' or '1120S', got {module!r}")
    if module == "1120S":
        return {
            "entity_type_codes": (VA_ENTITY_TYPE_CODE_SCORP,),
            "owner_count_source": "federal Form 1120-S, Page 1, item I (number of SHAREHOLDERS during any part of the year)",
            "participation_pct_source": "federal Schedule K-1 (1120-S), item G, AS PRINTED ('Current year allocation percentage') - do NOT recompute from item H",
            "participation_type_codes": (VA_PARTICIPATION_CODE_SCORP,),
            "federal_enclosure": "Form 1120-S with Schedule K (no federal K-1; no K-2/K-3)",
            "bank_franchise_branch": True,
            "scorp_all_nonresident_option_502ptet": True,
            "form_502fed1_path": False,
        }
    return {
        "entity_type_codes": VA_ENTITY_TYPE_CODES_PARTNERSHIP,
        "owner_count_source": "federal Form 1065, Page 1, item I (number of Schedules K-1 filed)",
        "participation_pct_source": "federal Schedule K-1 (1065), item J, ENDING PROFIT percentage",
        "participation_type_codes": VA_PARTICIPATION_CODES_PARTNERSHIP,
        "federal_enclosure": "Form 1065 with Schedule K (no federal K-1; no K-2/K-3)",
        "bank_franchise_branch": False,
        "scorp_all_nonresident_option_502ptet": False,
        "form_502fed1_path": True,
    }


# The 12-line Line-1 worksheet printed in the instructions (p.10). Worksheet line 12
# is the Virginia total - "there is not a total on Schedule K of federal Form 1065
# or Form 1120-S".
VA_L1_WORKSHEET_KEYS: tuple = (
    "wk_ordinary_income", "wk_rental_real_estate", "wk_other_rental", "wk_interest",
    "wk_dividends", "wk_royalty", "wk_other_portfolio", "wk_st_capital_gain",
    "wk_lt_capital_gain", "wk_1231_gain", "wk_other_income",
)


def _va_502_line1(worksheet: dict) -> float:
    """Form 502 Line 1 'Total taxable income amounts' - INCOME ONLY.

    Line 2 (deductions) does NOT reduce it. Line 1 - not L1 - L2 - is what flows to
    Schedule 502A Section C Line 1 and drives apportionment. Lines 2 and 3 are
    informational carriers to VK-1 for the owner's own return.

    The DOR Caution: Schedule K has NO total, entries may OVERLAP (a yearly amount and
    a through-a-date amount in a federal mid-year-change year), and the correct figure
    is "not necessarily the sum of all entries in the 'Income' section". The engine
    sums the eleven YEARLY category totals the preparer affirms; it must never scrape
    Schedule K unattended. This is the single most under-appreciated line on the form.
    """
    return float(sum(float(worksheet.get(k, 0) or 0) for k in VA_L1_WORKSHEET_KEYS))


def _va_page1_line13(l8, l9, l10, l11, l12) -> float:
    """Line 13 Total additions. 'Add Lines 8 through 12.'"""
    return float(l8 or 0) + float(l9 or 0) + float(l10 or 0) + float(l11 or 0) + float(l12 or 0)


def _va_page1_line18(l14, l15, l16, l17) -> float:
    """Line 18 Total subtractions. 'Add Lines 14 through 17.'"""
    return float(l14 or 0) + float(l15 or 0) + float(l16 or 0) + float(l17 or 0)


def _va_conformity_line(item: str) -> str:
    """Which Form 502 line carries a given conformity adjustment (W2 / U1 / C1).

    Lines 8 / 14 are textually scoped to 'the special bonus depreciation deduction for
    federal purposes in any taxable year from 2001 through 2025' AND NOTHING ELSE.
    Line 9 / 15 sub-item (1) is the DISPOSED-ASSET true-up on a bonus asset - "the
    difference in the federal and Virginia basis of the asset when sold".
    Line 9 / 15 sub-item (2) is a RESIDUAL CONFORMITY BUCKET - "any OTHER conformity
    additions listed in the Conformity Update for 2025 above". The word "other" is
    what excludes bonus depreciation. The bucket is WIDER THAN H.R.1: it also carries
    AHYDO, COD income, the 2008/09 NOL carryback and the CARES-Act items. It is NOT
    an "H.R.1 line" (correction C1) - do not describe it as one, in code or in copy.
    """
    if item == "bonus_depreciation_recompute":
        return "8/14"
    if item == "bonus_disposed_asset_trueup":
        return "9(1)/15(1)"
    if item in VA_CONFORMITY_BUCKET_MEMBERS:
        return "9(2)/15(2)"
    return "UNKNOWN"


def _va_conformity_bucket_is_wider_than_hr1() -> bool:
    """True: the Line 9(2)/15(2) bucket carries more than the three H.R.1 items."""
    hr1 = [m for m in VA_CONFORMITY_BUCKET_MEMBERS if "H.R.1" in m]
    return len(VA_CONFORMITY_BUCKET_MEMBERS) > len(hr1) > 0


def _va_179_limits(year: int = FORM_TAX_YEAR) -> dict:
    """Virginia's Sec.179 figures. `virginia_published` IS None - that is the finding.

    Confirmed absent by exhaustion from THREE instruction books (Form 502, the 502PTET
    package, the corporate Form 500 book), TB 26-1 and the 2026 Legislative Summary.
    The derived figures come from Rev. Proc. 2024-40 s.3.25 applied through TB 26-1's
    "as if the 2025 H.R. 1 changes had not been enacted" - an INFERENCE, not a Virginia
    number. The federal OBBBA 2,500,000 / 4,000,000 must NEVER be used for Virginia.
    """
    return {
        "virginia_published": _yk(VA_179_PUBLISHED, year),
        "derived_not_va_sourced": _yk(VA_179_DERIVED_NOT_VA_SOURCED, year),
        "federal_obbba_do_not_use": _yk(FEDERAL_OBBBA_179_DO_NOT_USE, year),
    }


def _va_apportionment_pct(prop, pay, sales, year: int = FORM_TAX_YEAR):
    """Schedule 502A Section B Line 2 - three factors, DOUBLE-WEIGHTED SALES, /4.

    Each argument is a (numerator, denominator) pair; a zero/None denominator means
    the factor DOES NOT EXIST.
        2(d) = 2(c) x 2
        2(e) = 2(a) + 2(b) + 2(d)
        2(f) = 2(e) / 4, "reduced by the number of factors, if any, having no denominator"

    RECONCILIATION NOTE (not in the brief; recorded here so it is auditable). The form
    FACE says "divide Line 2e by 4, reduced by the number of factors having no
    denominator"; the INSTRUCTION says the denominator "must be the number of existing
    factors". Those readings agree only if the sales factor is counted at its DOUBLE
    weight. The divisor implemented is therefore the SUM OF THE WEIGHTS of the factors
    that exist (property 1 + payroll 1 + sales 2 = 4):
        all three exist  -> 4        sales missing    -> 2
        property missing -> 3        payroll missing  -> 3
    Returns None when no factor has a denominator.
    """
    w = _yk(VA_APPORT_WEIGHTS, year)

    def _f(pair):
        if pair is None:
            return None
        num, den = pair
        if not den:
            return None
        return float(num) / float(den)

    f_prop, f_pay, f_sales = _f(prop), _f(pay), _f(sales)
    divisor = 0
    total = 0.0
    if f_prop is not None:
        divisor += w["property"]
        total += f_prop * w["property"]
    if f_pay is not None:
        divisor += w["payroll"]
        total += f_pay * w["payroll"]
    if f_sales is not None:
        divisor += w["sales"]
        total += f_sales * w["sales"]
    if divisor == 0:
        return None
    return round(total / divisor, _yk(VA_APPORT_DECIMALS, year))


def _va_property_factor(begin_va, end_va, begin_ew, end_ew, rent_va=0, rent_ew=0,
                        year: int = FORM_TAX_YEAR):
    """Property at ORIGINAL COST plus additions and improvements, averaged beginning
    and ending; RENTED property at 8 TIMES the annual rental rate
    (Va. Code ss.58.1-409 to -411)."""
    m = _yk(VA_RENT_MULTIPLIER, year)
    num = (float(begin_va) + float(end_va)) / 2.0 + m * float(rent_va)
    den = (float(begin_ew) + float(end_ew)) / 2.0 + m * float(rent_ew)
    return num, den


def _va_502a_section_c(l1, dividends_received, nonapport_income, nonapport_loss,
                       commercial_domicile_in_va: bool) -> dict:
    """Schedule 502A Section C - allocable vs. apportionable income.

    C5: Section C is NOT a renumbering of Schedule 500A. Schedule 500A has NO Section C
    (its income build lives in Section B Line 3(a)-3(j)) and it APPLIES THE PERCENTAGE
    ON THE SCHEDULE. Schedule 502A Section C stops at Lines 1-4 and pushes three figures
    out to Form 502 Lines 4, 5 and 6; there is NO line on Schedule 502A that multiplies
    income by the apportionment percentage. A loader that clones 500A Section B Line 3
    into the PTE spec invents lines that do not exist.

    Lines 3(b)/3(d) are the Allied-Signal constitutional-relief lines, carrying a clear-
    and-cogent-evidence burden and a one-way ratchet on later losses -> R5.
    """
    l1 = float(l1 or 0)
    if commercial_domicile_in_va:
        l2 = float(dividends_received or 0)          # -> Form 502 Line 4
        l3e = 0.0                                    # -> Form 502 Line 5
        l4 = l1 - l2                                 # -> Form 502 Line 6
    else:
        l2 = 0.0
        l3c = float(dividends_received or 0) + float(nonapport_income or 0)
        l3e = l3c - float(nonapport_loss or 0)       # -> Form 502 Line 5
        l4 = l1 - l3e                                # -> Form 502 Line 6
    return {"502_L4": round(l2, 2), "502_L5": round(l3e, 2), "502_L6": round(l4, 2)}


def _va_wholly_virginia_shortpath(l1) -> dict:
    """Instruction, Lines 4-7: if the PTE conducted its business entirely within
    Virginia, "leave Lines 4 and 5 blank, repeat the amount from Line 1 on Line 6, and
    enter '100%' on Line 7" - a real short path that skips Schedule 502A entirely."""
    return {"502_L4": None, "502_L5": None, "502_L6": float(l1 or 0), "502_L7": 1.00}


# ---------------------------------------------------------------------------
# Form 502 Page 2 - the nonresident withholding return
# ---------------------------------------------------------------------------

def _va_wh_owner_tax(va_source_share, is_nonresident: bool = True, exemption_code=None,
                     credits_passed_through=0.0, days_nonresident=None,
                     days_in_year=None, year: int = FORM_TAX_YEAR) -> float:
    """5% of a nonresident owner's share of Virginia-source taxable income.

    Va. Code s.58.1-486.2 B.1, verbatim: "five percent of the nonresident owner's share
    of income from Virginia sources". Part-year owners: "the income allocated to such
    owner must be prorated by the number of days of residence outside of Virginia".
    Credits that pass through may be applied, "but the tax liability of any nonresident
    owner may not be reduced to less than zero" - the floor is PER OWNER, applied
    before the entity total is struck.
    """
    if not is_nonresident or exemption_code:
        return 0.0
    days_in_year = int(days_in_year or _yk(VA_WH_PRORATION_DAYS, year))
    share = float(va_source_share or 0)
    if days_nonresident is not None and int(days_nonresident) < days_in_year:
        share = share * (float(days_nonresident) / float(days_in_year))
    tax = share * float(_yk(VA_NR_WITHHOLDING_RATE, year))
    return round(max(0.0, tax - float(credits_passed_through or 0)), 2)


def _va_wh_line1(owners: list, year: int = FORM_TAX_YEAR) -> float:
    """Page 2 Section 1 Line 1 - total withholding due, summed AFTER the per-owner floor."""
    return round(sum(_va_wh_owner_tax(year=year, **o) for o in owners), 2)


def _va_wh_safe_harbor(current_year_liability, prior_year_liability,
                       prior_year_was_full_12_months: bool,
                       prior_year_had_liability: bool, year: int = FORM_TAX_YEAR) -> float:
    """"the payment must be equal to the LESSER of: 90% of the withholding tax liability
    that was reported for the current taxable year or 100% of the withholding tax
    liability reported for the previous taxable year, PROVIDED that the return for the
    previous year covered a 12-month period and reflected a withholding tax liability."
    If either proviso fails there is no prior-year leg and 90% of current stands."""
    sh = _yk(VA_WH_SAFE_HARBOR, year)
    current_leg = float(current_year_liability or 0) * sh["current_year_pct"]
    if prior_year_was_full_12_months and prior_year_had_liability:
        prior_leg = float(prior_year_liability or 0) * sh["prior_year_pct"]
        return round(min(current_leg, prior_leg), 2)
    return round(current_leg, 2)


def _va_wh_ext_penalty_applies(l1, l4) -> bool:
    """ONE test, stated two ways by the DOR - encode ONCE, never both.
    Face: "may apply to returns filed within extension period if 90% of Line 1 is not
    paid timely". Instruction: "may apply if the balance due on Line 4 is more than 10%
    of Line 1". paid >= 90% <=> balance <= 10%."""
    return float(l4 or 0) > 0.10 * float(l1 or 0)


def _va_wh_ext_penalty(l4, days_late, year: int = FORM_TAX_YEAR) -> float:
    """Extension Penalty Worksheet (Instr. p.14), verbatim structure.
    A = tax due after timely payments (the Line 4 balance)
    C = number of months from the due date through the date filed, "count in 30-DAY
        INCREMENTS and ROUND UP to the next full month"
    D = C x 2%, "Do not exceed 12%"
    E = A x D
    """
    if float(l4 or 0) <= 0 or int(days_late or 0) <= 0:
        return 0.0
    step = _yk(VA_WH_EXT_PENALTY_MONTH_DAYS, year)
    months = math.ceil(float(days_late) / float(step))
    pct = min(months * _yk(VA_WH_EXT_PENALTY_PCT_PER_MONTH, year),
              _yk(VA_WH_EXT_PENALTY_CAP, year))
    return round(float(l4) * pct, 2)


def _va_wh_line6(l4, filed_more_than_6_months_late: bool, year: int = FORM_TAX_YEAR) -> float:
    """Page 2 Line 6 late payment penalty: "Enter 30% of the amount on Line 4"."""
    if not filed_more_than_6_months_late:
        return 0.0
    return round(float(l4 or 0) * _yk(VA_WH_LATE_PAYMENT_PCT, year), 2)


def _va_wh_line9(filed_more_than_6_months_late: bool,
                 filed_more_than_30_days_after_fed_ext: bool,
                 year: int = FORM_TAX_YEAR) -> float:
    """Page 2 Section 3 Line 9 - flat $1,200 late-filing penalty."""
    if filed_more_than_6_months_late or filed_more_than_30_days_after_fed_ext:
        return float(_yk(VA_502_LATE_FILING_FLAT, year))
    return 0.0


def _va_wh_penalties_mutually_exclusive(l5, l6) -> bool:
    """"The extension penalty does not apply in cases where the return is subject to the
    late filing penalty." Lines 5 and 6 can never both be non-zero."""
    return not (float(l5 or 0) > 0 and float(l6 or 0) > 0)


def _va_wh_line10(l3, l6, l7, l8, l9):
    """Page 2 Section 4 Line 10 - a FOUR-BRANCH CONDITIONAL, not a subtraction.
    The single most error-prone line on the form; transcribed exactly.

    "Net overpayment. If Line 8 or Line 9 exceeds Line 3, go to Line 13 below to compute
    the total payment due. Compare Line 6 and Line 9. If Line 6 is greater than Line 9,
    subtract Line 8 from Line 3. If Line 9 is greater than Line 6, subtract Line 7 plus
    Line 9 from Line 3. Otherwise, enter overpayment amount from Line 3."

    Returns None for branch 1 (the "go to Line 13" exit) - NOT zero.
    """
    l3, l6, l7, l8, l9 = (float(x or 0) for x in (l3, l6, l7, l8, l9))
    if l8 > l3 or l9 > l3:
        return None                      # branch 1 - go to Line 13
    if l6 > l9:
        return round(l3 - l8, 2)         # branch 2
    if l9 > l6:
        return round(l3 - (l7 + l9), 2)  # branch 3
    return round(l3, 2)                  # branch 4 - "otherwise"


def _va_wh_line13(l3, l4, l5, l8, l9) -> float:
    """Line 13 "Balance of tax due plus extension penalty, if applicable. If there is an
    amount due on Line 4, enter Line 4 plus Line 5. If there is an overpayment on Line 3
    and Line 8 or Line 9 is greater than Line 3, enter Line 5 minus Line 3."
    """
    l3, l4, l5, l8, l9 = (float(x or 0) for x in (l3, l4, l5, l8, l9))
    if l4 > 0:
        return round(l4 + l5, 2)
    if l3 > 0 and (l8 > l3 or l9 > l3):
        return round(l5 - l3, 2)
    return 0.0


def _va_wh_line15(l6, l9) -> float:
    """Line 15 Late filing penalty: "Enter the GREATER of Line 6 or Line 9"."""
    return round(max(float(l6 or 0), float(l9 or 0)), 2)


def _va_wh_line16(l13, l14, l15) -> float:
    """Line 16 Total payment due. "Add Line 13, Line 14, and Line 15."""
    return round(float(l13 or 0) + float(l14 or 0) + float(l15 or 0), 2)


def _va_wh_line20_21(l16, l17, l12=0.0) -> dict:
    """Section 6. Line 20 Amount Due = L16 - L17 where L16 exceeds L17. Line 21 Refund =
    L17 - L16 where L16 is less than L17, and "If there is an amount on Line 12, add
    Line 12 and Line 17." L17 is the Motion Picture Production Tax Credit refunded
    directly to the PTE - the only credit the PTE itself can monetise."""
    l16, l17, l12 = float(l16 or 0), float(l17 or 0), float(l12 or 0)
    if l16 > l17:
        return {"L20_amount_due": round(l16 - l17, 2), "L21_refund": 0.0}
    return {"L20_amount_due": 0.0, "L21_refund": round((l17 - l16) + l12, 2)}


# ---------------------------------------------------------------------------
# Form 502PTET - the elective entity-level tax
# ---------------------------------------------------------------------------

def _va_ptet_section_i_line1(income_total, deductions_total,
                             sec179_as_filed=0.0, sec179_ccorp_limit=0.0,
                             charitable_as_filed=0.0, charitable_ccorp_limit=0.0,
                             eligible_owner_pct=1.0) -> float:
    """Form 502PTET Section I Line 1 - THE BASE DIVERGENCE. Read before cloning Form 502.

    Verbatim: "unlike the computation of the nonresident withholding tax on Form 502,
    separately stated items of deduction ARE included when calculating each eligible
    owner's share of the PTE's taxable income on this form. For the purposes of the
    PTET, any separately stated item of deduction that is subject to a federal
    limitation, such as the deduction for charitable contributions and the Section 179
    deduction, is limited to what is allowed under federal law for a C CORPORATION."

    So Form 502 Line 1 (income only) != 502PTET Section I Line 1 (income NET of
    deductions, with s.179 and charitable RE-LIMITED at the C-corp level). That is an
    entity-level C-corporation pro-forma recomputation with no federal analogue - the
    software must build it. It is the easiest thing to get wrong by cloning.

    NOTE: the Sec.179 limit used HERE is the FEDERAL C-corp limit, for the BASE. The
    VIRGINIA Sec.179 deconformity then adjusts it downstream on Lines 9/15. TWO Sec.179
    rules, in sequence, on one return.
    """
    other_deductions = (float(deductions_total or 0) - float(sec179_as_filed or 0)
                        - float(charitable_as_filed or 0))
    allowed = (other_deductions
               + min(float(sec179_as_filed or 0), float(sec179_ccorp_limit or 0))
               + min(float(charitable_as_filed or 0), float(charitable_ccorp_limit or 0)))
    return round((float(income_total or 0) - allowed) * float(eligible_owner_pct), 2)


def _va_ptet_section_i_column(l1, l2_additions, l4_subtractions) -> dict:
    """Section I, ONE COLUMN (A Nonresident Owners / B Resident Owners).
    L3 = L1 + L2 ; L5 = L3 - L4, "If Line 4 is greater than Line 3, enter zero."
    THE ZERO FLOOR IS PER COLUMN - a resident-column loss CANNOT offset nonresident-
    column income. Encode two independent floors, not one.

    U6: Lines 2 and 4 want the ELIGIBLE-OWNER portion of Page 1 Lines 13 and 18, but
    Page 1 is expressly whole-entity and no line, ratio or worksheet is provided for
    the narrowing. Working assumption: the eligible owners' aggregate participation %.
    """
    l3 = float(l1 or 0) + float(l2_additions or 0)
    l5 = max(0.0, l3 - float(l4_subtractions or 0))
    return {"L3": round(l3, 2), "L5": round(l5, 2)}


def _va_ptet_line6(l5_col_a, l5_col_b) -> float:
    """Line 6 "Total Virginia taxable income: Add Line 5, Columns A and B (if negative,
    enter zero)." The SECOND floor."""
    return round(max(0.0, float(l5_col_a or 0) + float(l5_col_b or 0)), 2)


def _va_ptet_line7a(l6, year: int = FORM_TAX_YEAR) -> float:
    """Line 7a "Pass-Through Entity Tax: Multiply Line 6 by 5.75%".
    This - NOT Line 7 - is "the amount of PTE elective tax credit that will be passed
    through to an electing PTE's eligible individual and fiduciary owners"."""
    return round(float(l6 or 0) * float(_yk(VA_PTET_RATE, year)), 2)


def _va_ptet_line7b(nonresident_corporate_va_source_share, year: int = FORM_TAX_YEAR) -> float:
    """Line 7b "Withholding tax due for nonresident corporate owners."

    *** W4 / U3 - THIS RATE IS AN INFERENCE FROM A DIFFERENT FORM. ***
    The entire 14-page 502PTET package states NO rate and NO base (boundary-anchored
    search: zero standalone "5%", zero "five percent"; the only percentages printed are
    100, 2, 22.50, 25, 30, 45, 5.75, 50, 6, 67.50, 75, 90). The 5% is carried over from
    Va. Code s.58.1-486.2 and the Form 502 instructions on the reasoning that it is the
    same statutory obligation, differently housed. Defensible - but it determines a real
    payment, so v1 PRE-FILLS this and leaves it EDITABLE with a review flag.
    """
    return round(float(nonresident_corporate_va_source_share or 0)
                 * float(_yk(VA_NR_WITHHOLDING_RATE, year)), 2)


def _va_ptet_line7(l7a, l7b) -> float:
    """Line 7 = 7a + 7b. An entity tax with a withholding leg bolted onto it."""
    return round(float(l7a or 0) + float(l7b or 0), 2)


def _va_ptet_credit_to_owners(l7a) -> float:
    """Schedule PTET ADJ Section C Part III Line 10 = Form 502PTET Section II Line 7a =
    the sum of VK-1 Part III Line 10 across owners. KEYED TO 7a, NOT 7 - the corporate
    withholding leg is EXCLUDED from the credit. The owner-side credit is REFUNDABLE
    (s.58.1-390.3 E: "such excess shall be treated as an overpayment and refundable")."""
    return round(float(l7a or 0), 2)


def _va_ptet_estimates_required(expected_ptet, year: int = FORM_TAX_YEAR) -> bool:
    """Estimates required if the PTET "can reasonably be expected to exceed $1,000"."""
    return float(expected_ptet or 0) > _yk(VA_PTET_ESTIMATE_THRESHOLD, year)


def _va_ptet_installment(expected_ptet, year: int = FORM_TAX_YEAR) -> float:
    """Four 25% installments: Apr 15 / Jun 15 / Sep 15 / Dec 15 for calendar filers; the
    15th day of the 4th / 6th / 9th / 12th month FOLLOWING THE BEGINNING of a fiscal year."""
    return round(float(expected_ptet or 0) * _yk(VA_PTET_ESTIMATE_PCT, year), 2)


def _va_ptet_late_filing_penalty(tax_due, is_late: bool = True,
                                 year: int = FORM_TAX_YEAR) -> float:
    """s.58.1-455 late filing: 30% of tax due, and "In no case will the penalty for
    failure to file timely be less than $100, and this minimum $100 penalty applies
    WHETHER OR NOT TAX IS DUE." A zero-tax late PTET return still owes $100.
    Note also: "The late payment penalty does not apply to the extent that the taxpayer
    is already subject to the late filing penalty."
    """
    if not is_late:
        return 0.0
    return round(max(float(tax_due or 0) * _yk(VA_PTET_LATE_FILE_PCT, year),
                     float(_yk(VA_PTET_LATE_FILE_MINIMUM, year))), 2)


def _va_ptet_election_permitted(months_after_original_due,
                                made_estimated_or_extension_payment: bool,
                                year: int = FORM_TAX_YEAR) -> bool:
    """THE HARD BAR - a VALIDATION rule, not a penalty; the return is REFUSED.
    "A PTE that fails to file more than 6 months after the original due date, or more
    than 30 days after the federal extended due date WILL NOT BE PERMITTED TO FILE Form
    502PTET unless it has made corresponding estimated payments or an extension payment
    for the taxable year."
    U5: whether a payment is LEGALLY sufficient to elect is unsettled - s.58.1-390.3 A.2
    names only the timely filed return, and the payment-as-election acts rest on DOR
    Guidelines / TB 22-6 / TB 23-3, which were not obtained. This follows the DOR's
    stated administration and carries a review flag."""
    if float(months_after_original_due or 0) <= _yk(VA_PTET_HARD_BAR_MONTHS, year):
        return True
    return bool(made_estimated_or_extension_payment)


def _va_ptet_sunset_year(year: int = FORM_TAX_YEAR):
    """U4 - BUILD TO THE STATUTE. Va. Code s.58.1-390.3 contains NO expiration date at
    all (history 2022, cc. 690, 689; 2023, cc. 686, 687; 2025, c. 725; 2026, c. 7).
    The re-issued Rev. 08/26 package still recites the repealed "before January 1, 2027"
    sunset SIX times, and the Form 502 instruction book contradicts itself between p.1
    ("becomes permanent and does not expire after Taxable Year 2026") and p.3. Returns
    None: NO SUNSET IS ENCODED. A diagnostic explains the dead form text instead."""
    return _yk(VA_PTET_SUNSET_YEAR, year)


def _va_ptet_may_file_765() -> bool:
    """"An electing PTE is NOT permitted to file Form 765." Mutually exclusive."""
    return False


# ---------------------------------------------------------------------------
# Due dates - TWO CLOCKS (W10). Both true at once.
# ---------------------------------------------------------------------------

def _va_due_month_day(return_kind: str, year: int = FORM_TAX_YEAR):
    """Entities are on the 15th day of the 4th month (Va. Code s.58.1-392 A, verbatim:
    "shall make a return... on or before the fifteenth day of the fourth month following
    the close of its taxable year"). Individuals (760/760PY/763) and fiduciaries (770)
    are on MAY 1. The string "May 1" appears ZERO times in the 29-page Form 502 book and
    ZERO times in the 14-page PTET package."""
    if return_kind in ("VA_502", "VA_502PTET"):
        return (_yk(VA_ENTITY_DUE_MONTH, year), _yk(VA_ENTITY_DUE_DAY, year))
    if return_kind in ("VA_760", "VA_760PY", "VA_763", "VA_770"):
        return _yk(VA_INDIVIDUAL_DUE_MONTH_DAY, year)
    raise ValueError(f"unknown return kind {return_kind!r}")


def _va_due_dates_conflated(kind_a: str, kind_b: str, year: int = FORM_TAX_YEAR) -> bool:
    """True when the SAME due date has been applied to an entity return and an
    individual/fiduciary return - the single-constant mistake W10 exists to prevent."""
    return _va_due_month_day(kind_a, year) == _va_due_month_day(kind_b, year)


def _va_payment_due_extends(year: int = FORM_TAX_YEAR) -> bool:
    """NEVER. Confirmed three ways: the Form 502 instructions, the 502PTET package, and
    Va. Code s.58.1-486.2 D.2 - "An extension of time for filing the return... shall not
    extend the time for paying the amount of withholding tax due." Form 502W
    operationally: "the withholding tax payment is due on April 15, 2026"."""
    return _yk(VA_PAYMENT_DATE_EXTENDS, year)


# ---------------------------------------------------------------------------
# Credits, filing gates, and the cross-form assertion set
# ---------------------------------------------------------------------------

def _va_credit_part2_total(part1_entered: dict) -> float:
    """Section C Part II Line 1, verbatim: "Add Part I, Lines 1-8, 12-15, 17, 21, 23, and
    25 through 27." The skipped numbers are exactly the NINE Reserved slots
    (9, 10, 11, 16, 18, 19, 20, 22, 24 - correction C4). ENUMERATE, never a range."""
    return round(sum(float(part1_entered.get(n, 0) or 0) for n in VA_CREDIT_PART2_SUMMANDS), 2)


def _va_credit_part4_total(part3_entered: dict, is_ptet: bool = False) -> float:
    """Part IV Line 1. Schedule 502ADJ: "Add Part III, Lines 1, 7, and 9."
    Schedule PTET ADJ: "Add Part III, Lines 1, 7, 9, AND 10."
    Schedule VK-1 carries the Line 10 slot on BOTH paths and its Part IV total ALWAYS
    includes Line 10 - so a naive `sum(VK-1 Part IV) == 502ADJ Part IV` assertion breaks
    the moment Line 10 is non-zero. Build the assertion PER LINE, not on the totals."""
    summands = VA_CREDIT_PART4_SUMMANDS_PTET if is_ptet else VA_CREDIT_PART4_SUMMANDS_502
    return round(sum(float(part3_entered.get(n, 0) or 0) for n in summands), 2)


def _va_credit_allocation_class(credit_slot: int) -> str:
    """Two classes. FIVE credits - Vehicle Emissions Testing Equipment (5), Historic
    Rehabilitation (12), Land Preservation (13), Qualified Equity and Subordinated Debt
    Investments (14), Virginia Housing Opportunity (27) - may be allocated "in
    proportion... OR AS THE OWNERS MAY MUTUALLY AGREE, or as provided in the partnership
    agreement". All others are strictly pro rata. Preserve as DATA, not one rule.
    Also: "Pass-through entities do not use or compute credit carryovers", and where a
    credit is limited "the limitation applies to the TOTAL credit of the PTE (the
    aggregate of the owners' shares), not to each owner's share separately"."""
    return "mutual_agreement_allowed" if credit_slot in VA_CREDITS_FREE_ALLOCATION else "pro_rata_required"


def _va_502ez_eligible(all_business_in_va: bool, all_income_va_source: bool,
                       commercial_domicile_va: bool, owner_count: int,
                       files_form_500: bool, files_schedule_502a: bool,
                       is_500hs_provider: bool, passes_schedule_cr_credits: bool,
                       has_conformity_modifications: bool, total_taxable_income: float,
                       total_modifications: float, amending_for_fed_adjustment: bool,
                       electing_ptet: bool, year: int = FORM_TAX_YEAR) -> bool:
    """R1 - the 13-criterion Form 502EZ gate; the PTE "must meet ALL of the criteria".
    THE CONFORMITY-MODIFICATION EXCLUSION IS DECISIVE FOR TY2025: any PTE with a bonus
    depreciation or residual-conformity-bucket adjustment is out of 502EZ BY DEFINITION.
    502EZ is eForms-only (browser), not an MeF form - deferred either way."""
    return bool(
        all_business_in_va and all_income_va_source and commercial_domicile_va
        and int(owner_count) <= _yk(VA_502EZ_MAX_OWNERS, year)
        and not files_form_500 and not files_schedule_502a and not is_500hs_provider
        and not passes_schedule_cr_credits and not has_conformity_modifications
        and 0 <= float(total_taxable_income) <= _yk(VA_502EZ_MAX_TAXABLE_INCOME, year)
        and float(total_modifications) < _yk(VA_502EZ_MAX_MODIFICATIONS, year)
        and not amending_for_fed_adjustment and not electing_ptet
    )


def _va_files_form_502(is_single_member_disregarded_llc: bool = False,
                       is_investment_only_pte: bool = False,
                       does_business_in_va: bool = True,
                       has_va_source_income: bool = True) -> bool:
    """Filing determinations that are RULES SAYING NO, not gaps.
    Single-member LLCs disregarded federally are disregarded for Virginia too - "The
    disregarded entity is not required to file Form 502." This is the OPPOSITE of
    Tennessee's Schedule J2 trap; do NOT port that pattern here.
    Investment-only PTEs "established solely to invest in intangible personal property...
    and that have no employees and no real or tangible property are not considered to be
    carrying on a trade or business" and are likewise not required to file.
    There are also NO consolidated or multilevel PTE returns - every PTE files its own."""
    if is_single_member_disregarded_llc or is_investment_only_pte:
        return False
    return bool(does_business_in_va or has_va_source_income)


def _va_502_and_ptet_mutually_exclusive() -> bool:
    """"Pass-through entities opting to make the election must electronically submit Form
    502PTET INSTEAD OF Form 502." If either has already been filed for the taxable year, any
    subsequent return must be marked amended - Reason Code 05 for a Form 502PTET amended return.
    An electing PTE also may not file Form 765. Always True: the two filings are exclusive."""
    return True


def _va_withhold_for_owner_pte(notified_will_not_file_va_return: bool) -> bool:
    """R10 - the anti-cascade rule. "As a general rule, a PTE should not withhold tax on
    behalf of another PTE"... but "If a PTE is notified by a nonresident owner PTE that
    the nonresident owner PTE is not going to file a Virginia PTE return, then the PTE IS
    required to withhold on the nonresident owner PTE."
    And the trap: "PTE withholding is not 'generation skipping'" - an erroneously
    withheld amount is TRAPPED, recoverable only by the WITHHOLDING PTE filing an amended
    Form 502, and NEVER claimable by the recipient PTE on its own Form 502."""
    return bool(notified_will_not_file_va_return)


def _va_vk1_crossform_checks(form502_lines: dict, vk1_rows: list) -> dict:
    """Brief Sec.6.1 - "The entries on each line of the Schedules VK-1 for all owners of
    the PTE should equal the corresponding entry on Form 502 and Schedule 502ADJ, EXCEPT
    FOR LINE 7. The entry on Line 7 will be the same for all owners of the entity and the
    same as Line 7 of Form 502." Returns a dict of check-name -> bool."""
    out = {}
    for n in VA_VK1_MIRROR_LINES:
        total = round(sum(float(r.get(n, 0) or 0) for r in vk1_rows), 2)
        out[f"sum_vk1_L{n}_eq_502_L{n}"] = abs(total - float(form502_lines.get(n, 0) or 0)) < 0.005
    l7 = form502_lines.get(7)
    out["vk1_L7_same_for_every_owner"] = all(
        abs(float(r.get(7, 0) or 0) - float(l7 or 0)) < 0.000005 for r in vk1_rows)
    pct = round(sum(float(r.get("d", 0) or 0) for r in vk1_rows), 2)
    out["sum_vk1_Ld_eq_100pct"] = abs(pct - 100.00) < 0.005
    withheld = round(sum(float(r.get("e", 0) or 0) for r in vk1_rows), 2)
    out["sum_vk1_Le_eq_502_Lc"] = abs(withheld - float(form502_lines.get("c", 0) or 0)) < 0.005
    return out


# ===========================================================================
# AUTHORITY TOPICS / SOURCES
# ===========================================================================

AUTHORITY_TOPICS: list[tuple[str, str]] = [
    ("va_pte_return", "Virginia Form 502 pass-through entity return of income and return of "
     "nonresident withholding tax: ONE return filed by partnerships and S corporations alike, "
     "Page 1 income/modification/credit build, Page 2 the 5% nonresident withholding return."),
    ("va_ptet", "Virginia Form 502PTET elective pass-through entity tax: 5.75% on eligible owners' "
     "shares, annually elective, binding on all eligible owners, refundable owner credit; filed "
     "INSTEAD OF Form 502. Made permanent in 2026 - the statute carries no sunset."),
    ("va_pte_apportionment", "Virginia PTE allocation and apportionment: Schedule 502A, three "
     "factors with double-weighted sales divided by four, cost-of-performance sourcing for non-TPP "
     "sales, nine mutually exclusive method boxes."),
    ("va_conformity_adjustment", "Virginia fixed-date (12/31/2025) conformity adjustments on the PTE "
     "forms: bonus depreciation on Lines 8/14, the disposed-asset true-up on Lines 9(1)/15(1), and "
     "the residual conformity bucket on Lines 9(2)/15(2)."),
]

# ALREADY SEEDED by the Tier-1 conformity batch (_state_conformity_tier1.py). These should
# RESOLVE - no "NOT FOUND" warning is expected. They anchor every conformity-side rule here
# to the same rows the conformity brief established, rather than re-authoring the posture.
EXISTING_SOURCES_TO_REFERENCE: list[str] = [
    "VA_CODE_58_1_301",   # fixed IRC date 12/31/2025; the 13 statutory exceptions
    "VA_TB_26_1",         # the operative DOR guidance: OBBBA IN, three carve-outs, the mechanic
]

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "VA_2025_FORM_502",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "VA",
        "title": "2025 Virginia Form 502 - Pass-Through Entity Return of Income and Return of Nonresident Withholding Tax",
        "citation": "Va. Form 502 (2025), 2601015-W Rev. 07/26 (PDF ModDate 2026-07-07)",
        "issuer": "Virginia Department of Taxation",
        "official_url": "https://www.tax.virginia.gov/sites/default/files/taxforms/corporation-and-pass-through-entity-tax/2025/502-2025.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.6,
        "topics": ["va_pte_return", "va_conformity_adjustment"],
        "excerpts": [
            {
                "excerpt_label": "Form 502 Page 1 face (2025) - verbatim line map, Lines a-d and 1-20",
                "excerpt_text": (
                    "Number and Types of Owners: a Total number of owners (include individuals and any "
                    "other entity types); b Total number of nonresident owners; c Total amount withheld "
                    "for nonresident owners (total of Line e from all Schedules VK-1); d If the entity is "
                    "exempt from withholding, enter the exemption code. Distributive or Pro Rata Income "
                    "and Deductions: 1 Total taxable income amounts; 2 Total deductions; 3 Tax-exempt "
                    "interest income. Allocation and Apportionment: 4 Income allocated to Virginia from "
                    "Schedule 502A, Section C, Line 2; 5 Income allocated outside of Virginia from "
                    "Schedule 502A, Section C, Line 3(e); 6 Apportionable income from Schedule 502A, "
                    "Section C, Line 4; 7 Virginia apportionment percentage from Schedule 502A, Section "
                    "B, percent from Line 1 or Line 2(f) or 100%. Virginia Additions: 8 Conformity - "
                    "depreciation; 9 Conformity - other; 10 Net income tax or other tax used as a "
                    "deduction in determining taxable income; 11 Interest on municipal or state "
                    "obligations other than from Virginia; 12 Total additions from enclosed Schedule "
                    "502ADJ, Section A, Line 5; 13 Total additions. Add Lines 8 through 12. Virginia "
                    "Subtractions: 14 Conformity - depreciation; 15 Conformity - other; 16 Income from "
                    "obligations of the United States; 17 Total subtractions from enclosed Schedule "
                    "502ADJ, Section B, Line 5; 18 Total subtractions. Add Lines 14 through 17. Virginia "
                    "Tax Credits Passed Through to Owners: 19 Total nonrefundable credits from enclosed "
                    "Schedule 502ADJ, Section C, Part II, Line 1; 20 Total refundable credits from "
                    "enclosed Schedule 502ADJ, Section C, Part IV, Line 1."
                ),
                "summary_text": (
                    "Form 502 Page 1: owner counts (a-d), income build (1-3), allocation and "
                    "apportionment (4-7), additions (8-13), subtractions (14-18), credits passed through "
                    "(19-20). THERE IS NO TAX COMPUTATION ON PAGE 1 - the PTE is not a taxpayer."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Form 502 Page 2 face (2025) - the nonresident withholding return, Sections 1-6",
                "excerpt_text": (
                    "Section 1: 1 Total withholding tax due for nonresident owners; 2 Total withholding "
                    "tax paid (Entity's own payments only); 3 Overpayment. If Line 2 is greater than Line "
                    "1, subtract Line 1 from Line 2; 4 Withholding tax due. If Line 2 is less than Line 1, "
                    "subtract Line 2 from Line 1. Section 2: 5 Extension penalty (may apply to returns "
                    "filed within extension period if 90% of Line 1 is not paid timely); 6 Late payment "
                    "penalty on tax due... Enter 30% of the amount on Line 4; 7 Interest; 8 Penalty and "
                    "interest charges due. Add Line 5 or Line 6 (whichever applies) to Line 7. Section 3: "
                    "9 If Form 502 is being filed more than 6 months after the original due date, or more "
                    "than 30 days after the federal extended due date, enter $1,200. Section 4: 10 Net "
                    "overpayment [four-branch conditional]; 11 Amount of withholding overpayment to be "
                    "credited to 2026; 12 Amount of withholding overpayment to be refunded. Section 5: 13 "
                    "Balance of tax due plus extension penalty, if applicable; 14 Interest charges on "
                    "withholding tax from Line 7; 15 Late filing penalty. Enter the greater of Line 6 or "
                    "Line 9; 16 Total payment due. Add Line 13, Line 14, and Line 15. Section 6: 17 Motion "
                    "Picture Production Tax Credit to be refunded directly to PTE; 18 Reserved for future "
                    "use; 19 Reserved for future use; 20 Amount Due; 21 Amount of Refund."
                ),
                "summary_text": (
                    "Form 502 Page 2 is a SECOND return - the nonresident withholding tax return. Line 10 "
                    "is a four-branch conditional; Line 15 takes the GREATER of Line 6 or Line 9; the "
                    "$1,200 late-filing penalty is flat."
                ),
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "VA_2025_FORM_502_INSTR",
        "source_type": "state_instruction",
        "source_rank": "primary_official",
        "jurisdiction_code": "VA",
        "title": "Instructions for Preparing 2025 Virginia Form 502 - Pass-Through Entity Return of Income",
        "citation": "Va. 2025 Form 502 Instructions, 6201028 Rev. 4/2026, 29 pp. (PDF ModDate 2026-04-01)",
        "issuer": "Virginia Department of Taxation",
        "official_url": "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2025-502-instructions.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["va_pte_return", "va_conformity_adjustment", "va_pte_apportionment"],
        "excerpts": [
            {
                "excerpt_label": "Conformity Update for 2025 + Line 9(2) / Line 15(2) routing (instr. p.12-13)",
                "excerpt_text": (
                    "[HEADING] Conformity Update for 2025 - '...replaced Virginia's suspended rolling "
                    "conformity to the IRC with a fixed conformity date of December 31, 2025... the 2026 "
                    "General Assembly legislation reduces the related Virginia subtraction for the "
                    "business interest disallowed on the federal return to 20% for Taxable Year 2025. Also "
                    "note that Virginia deconforms from certain business related provisions of 2025 H.R. "
                    "1, specifically: the immediate expensing of qualified production property, the "
                    "immediate expensing of domestic research and experimental expenditures (including "
                    "retroactive and catchup provisions), and the increases to the expensing limits of "
                    "certain depreciable assets.' THE SECTION CONTINUES: 'Virginia will continue to "
                    "deconform from the following: bonus depreciation...; the five-year carryback of "
                    "certain federal net operating loss (NOL) deductions generated in the 2008 or 2009 "
                    "taxable years; the federal income treatment of applicable high yield discount "
                    "obligations; and the federal income tax treatment of cancellation of debt income "
                    "realized in connection with certain business debts. In addition, Virginia will "
                    "continue to deconform from certain business provisions of the federal CARES Act, and "
                    "deduction of business expenses through certain COVID-related small business "
                    "assistance programs prior to Taxable Year 2021.' [LINE 9 SUB-ITEM (2)] 'Conformity "
                    "Additions. If you are required to make any other conformity additions listed in the "
                    "Conformity Update for 2025 above, enter the total amount of such additions. Also, "
                    "enclose a schedule and explanation of such additions.' [LINE 15 SUB-ITEM (2)] "
                    "'Conformity Subtractions. If you are required to make any conformity subtractions "
                    "listed in the Conformity Update for 2025 above, enter the total amount of such "
                    "subtractions on this line. Also, enclose a schedule and explanation.'"
                ),
                "summary_text": (
                    "Line 9(2) / 15(2) is a RESIDUAL CONFORMITY BUCKET, wider than H.R.1 - it carries the "
                    "H.R.1 trio PLUS AHYDO, COD income, the 2008/09 NOL carryback and the CARES-Act items. "
                    "The word 'other' is what excludes bonus depreciation, which Lines 8 and 9(1) already "
                    "carry by name. No DOR worksheet exists: 'enclose a schedule and explanation'. W2/U1."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Line 8 / Line 14 - bonus depreciation recompute, textually scoped 2001-2025",
                "excerpt_text": (
                    "'Enter the amount that should be added to federal taxable income based upon the "
                    "recomputation of allowable depreciation. If depreciation was included in the "
                    "computation of your federal taxable income and one or more of the depreciable assets "
                    "received the special bonus depreciation deduction for federal purposes in any taxable "
                    "year from 2001 through 2025, then depreciation must be recomputed for Virginia "
                    "purposes as if such assets did not receive the special bonus depreciation "
                    "deduction... If the total 2025 Virginia depreciation is less than 2025 federal "
                    "depreciation, then the difference must be recognized as an addition.' [LINE 9(1) "
                    "DISPOSED ASSET] 'The adjustment will be the difference in the federal and Virginia "
                    "basis of the asset when sold.'"
                ),
                "summary_text": (
                    "Lines 8/14 are BONUS-ONLY, scoped to vintages 2001-2025. Line 9(1)/15(1) is the "
                    "disposed-asset true-up measured as the federal-vs-Virginia basis difference. Both "
                    "require a multi-year Virginia depreciation shadow book -> R2."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "The six module branch points - entity/participation codes, owner counts, enclosures, bank franchise",
                "excerpt_text": (
                    "[ENTITY TYPE, face, required] PG General Partnership, PL Limited Partnership, LL "
                    "Limited Liability Company, LP Limited Liability Partnership, NZ Nonprofit "
                    "Organization, OB Other; SC S Corporation. [LINE a] partnership: 'the number of "
                    "Schedules K-1 filed with the PTE's federal return (see federal Form 1065, Page 1, "
                    "Line I)'; S corp: 'the number of shareholders who were shareholders during any part "
                    "of the taxable year (see federal Form 1120-S, Page 1, Line I)'. [VK-1 LINE d] "
                    "partnership: 'the ending percentage for the partner's profit share as shown on the "
                    "Schedule K-1, under Line J'; S corp: 'the owner's percentage of stock ownership for "
                    "the taxable year, as shown on the owner's federal Schedule K-1 (Form 1120-S), Line "
                    "G'. [VK-1 LINE c] GPT General Partner, LPT Limited Partner, LLM LLC/LLP Member, OTR "
                    "Other; SHR S Corporation Shareholder. [ENCLOSURE] Form 1065 with Schedule K / Form "
                    "1120-S with Schedule K - 'Do not include federal Schedule K-1 because it is not "
                    "required. Do not submit Schedules K-2 and K-3'. [BANK FRANCHISE] 'the S corporation "
                    "will provide the shareholders with the pertinent information concerning their "
                    "allocable share of the income or gain, losses, or deductions or the value of any "
                    "distributions' -> Schedule 502ADJ Code 99 -> owner deduction Code 112."
                ),
                "summary_text": (
                    "The 1065/1120S branch lives in six places, none of them in the computation: entity "
                    "type code, owner-count source, participation-% source, participation type code, "
                    "federal enclosure, and the S-corp-only bank franchise consequence."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Nonresident withholding - 5%, exceptions, safe harbor, the anti-cascade rule (instr. p.4)",
                "excerpt_text": (
                    "'Every PTE that does business in the Commonwealth and has taxable income derived from "
                    "Virginia sources must withhold and pay Virginia income tax on behalf of each of its "
                    "nonresident owners, unless the entity or the owner meets an exception... The tax is "
                    "equal to 5% of the share of taxable income from Virginia sources that is allocable to "
                    "each nonresident owner. In determining the amount of tax, the entity may apply any "
                    "tax credits that pass through to nonresident owners, but the tax liability of any "
                    "nonresident owner may not be reduced to less than zero.' 'If an owner was a "
                    "nonresident owner for only a portion of the taxable year, the income allocated to "
                    "such owner must be prorated by the number of days of residence outside of Virginia.' "
                    "[SAFE HARBOR] 'the lesser of: 90% of the withholding tax liability that was reported "
                    "for the current taxable year or 100% of the withholding tax liability reported for "
                    "the previous taxable year, provided that the return for the previous year covered a "
                    "12-month period and reflected a withholding tax liability.' [ANTI-CASCADE] 'PTE "
                    "withholding is not \"generation skipping\" and does not pass through an intermediate "
                    "PTE to owners that are more than one level of ownership away.' [DUE DATE] 'Payment of "
                    "the withholding tax is due by the original due date for filing Form 502 (i.e., April "
                    "15 for a calendar year return). The automatic 6-month filing extension for Form 502 "
                    "does not apply to the withholding tax payment.'"
                ),
                "summary_text": (
                    "5% of each nonresident owner's Virginia-source share, day-count prorated for "
                    "part-year, credits applied but floored at zero PER OWNER; 90%/100% safe harbor; the "
                    "payment date NEVER extends; withholding is not generation-skipping."
                ),
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "VA_2025_SCH_502A",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "VA",
        "title": "2025 Virginia Schedule 502A - Multistate Pass-Through Entity Allocation and Apportionment",
        "citation": "Va. Schedule 502A (2025), 2601014-W Rev. 07/26 (PDF ModDate 2026-07-23)",
        "issuer": "Virginia Department of Taxation",
        "official_url": "https://www.tax.virginia.gov/sites/default/files/taxforms/corporation-and-pass-through-entity-tax/2025/502a-2025.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["va_pte_apportionment"],
        "excerpts": [
            {
                "excerpt_label": "Section B Line 2 - the divide-by-four double-weighted sales formula (verbatim)",
                "excerpt_text": (
                    "2(a) Property Factor; 2(b) Payroll Factor; 2(c) Sales Factor; 2(d) Double-Weighted "
                    "Sales Factor Apportionment: Multiply the sales factor from Line 2(c) by 2; 2(e) Sum "
                    "of Percentages. Add Lines 2(a), 2(b), and 2(d); 2(f) Multi-Factor Percentage "
                    "(Double-Weighted Sales): Divide Line 2e by 4, reduced by the number of factors, if "
                    "any, having no denominator. [INSTRUCTION] 'Multistate companies are generally "
                    "required to use a three-factor formula of property, payroll and double-weighted "
                    "sales. The sum of the property factor, payroll factor and twice the sales factor is "
                    "divided by 4 to arrive at the final apportionment factor.' 'However, if the sales "
                    "factor does not exist, the denominator of the fraction must be the number of existing "
                    "factors. If the sales factor exists, but the payroll factor or the property factor "
                    "does not exist, the denominator of the fraction must be the number of existing "
                    "factors.'"
                ),
                "summary_text": (
                    "Virginia PTEs are NOT on single sales factor. Three factors, sales weighted twice, "
                    "divided by four, with the divisor reduced when a factor has no denominator."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Section C - allocable and apportionable income, Lines 1-4 (no percentage-application line)",
                "excerpt_text": (
                    "1 Total of taxable income amounts from Form 502, Line 1; 2 If commercial domicile is "
                    "in Virginia, enter dividends received here and on Form 502, Line 4; 3(a) If "
                    "commercial domicile is not in Virginia: Enter dividends received; 3(b) Enter "
                    "nonapportionable investment function income; 3(c) Add Lines 3(a) and 3(b); 3(d) Enter "
                    "nonapportionable investment function loss; 3(e) Allocable Income - Subtract Line 3(d) "
                    "from Line 3(c). Enter the amount here and on Form 502, Line 5; 4 Apportionable Income "
                    "- If domiciled in Virginia, subtract Line 2 from Line 1. If not domiciled in "
                    "Virginia, subtract Line 3(e) from Line 1. Enter on Form 502, Line 6."
                ),
                "summary_text": (
                    "Section C stops at allocable/apportionable income and pushes three figures to Form "
                    "502 Lines 4/5/6. Schedule 500A has NO Section C and applies the percentage on the "
                    "schedule itself - do not clone 500A Section B Line 3 into the PTE spec (C5)."
                ),
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "VA_2025_SCH_502ADJ",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "VA",
        "title": "2025 Virginia Schedule 502ADJ - Pass-Through Entity Modifications and Credits",
        "citation": "Va. Schedule 502ADJ (2025), 2601020-W Rev. 07/26 (PDF ModDate 2026-07-02); overflow on Schedule 502ADJS, 2601026-W Rev. 07/26",
        "issuer": "Virginia Department of Taxation",
        "official_url": "https://www.tax.virginia.gov/sites/default/files/taxforms/corporation-and-pass-through-entity-tax/2025/502adj-2025.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["va_pte_return"],
        "excerpts": [
            {
                "excerpt_label": "Section C Parts II and IV - the ENUMERATED credit totals (never a range)",
                "excerpt_text": (
                    "[PART II, Line 1, verbatim] 'Add Part I, Lines 1-8, 12-15, 17, 21, 23, and 25 through "
                    "27. Enter on Form 502, Page 1, Line 19.' [PART IV, Line 1, verbatim] 'Add Part III, "
                    "Lines 1, 7, and 9. Enter on Form 502, Page 1, Line 20.' Part I carries 27 numbered "
                    "slots of which NINE are Reserved for Future Use - slots 9, 10, 11, 16, 18, 19, 20, 22 "
                    "and 24. Part III carries 9 slots: 1 Agricultural Best Management Practices, 2-6 "
                    "Reserved, 7 Motion Picture Production, 8 Reserved, 9 Conservation Tillage and "
                    "Precision Agriculture Equipment. Schedule PTET ADJ Part III gains a Line 10 "
                    "'Pass-Through Entity Elective Tax Payment Credit' and its Part IV reads 'Add Part "
                    "III, Lines 1, 7, 9, and 10.'"
                ),
                "summary_text": (
                    "The credit totals are ENUMERATED lists that skip exactly the nine Reserved slots. "
                    "Schedule VK-1 carries the Part III Line 10 slot on BOTH paths, so a totals-level "
                    "VK-1-vs-502ADJ assertion breaks the moment Line 10 is non-zero - assert per line."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Addition and subtraction code tables (10 additions / 20 subtractions) and the owner-side translations",
                "excerpt_text": (
                    "ADDITION CODES: 10 interest on federally exempt U.S. obligations; 13 bad debt "
                    "deduction (savings and loan); 14 unrelated business taxable income (IRC 512); 15 "
                    "royalty addback (enclose Schedule 500AB); 16 interest addback (enclose Schedule "
                    "500AB); 18 dealer disposition of property; 21 Food Donation Tax Credit addback; 22 "
                    "Addition Related to the Business Interest Deduction; 23 partnership-level federal "
                    "adjustments (enclose Form 502FED-1); 99 Other. SUBTRACTION CODES: 10, 11, 12 "
                    "(subpart F / GILTI), 13 foreign source income, 14 dividends from 50%-owned "
                    "corporations, 16, 17, 20 Virginia obligations, 21 WOTC wages, 22 related-member "
                    "offset, 43, 48, 49, 50, 51, 52, 56 Business Interest Deduction (20% of s.163(j) "
                    "disallowed), 57, 58, 99 Other. OWNER-SIDE TRANSLATIONS: 'The Virginia Public School "
                    "Construction Grants Program, Fund (Code 43), the Tobacco Quota Buyout Program (Code "
                    "48), and the business interest (Code 56) deductions must be claimed as deductions on "
                    "the shareholder's individual income tax return' - as Codes 107, 108 and 116 "
                    "respectively; bank-franchise Code 99 becomes owner deduction Code 112."
                ),
                "summary_text": (
                    "TEN addition codes and TWENTY subtraction codes (correction C3 - not 22/19). Five "
                    "codes are 'PTE reports it under one code, the owner deducts it under a DIFFERENT "
                    "code' - 43->107, 48->108, 56->116, 22->negative deduction, 99->112."
                ),
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "VA_2025_SCH_VK1",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "VA",
        "title": "2025 Virginia Schedule VK-1 - Owner's Share of Income and Virginia Modifications and Credits",
        "citation": "Va. Schedule VK-1 (2025), 2601024-W Rev. 07/26 (PDF ModDate 2026-07-20); overflow on Schedule SVK-1, 2601055-W Rev. 07/26",
        "issuer": "Virginia Department of Taxation",
        "official_url": "https://www.tax.virginia.gov/sites/default/files/taxforms/corporation-and-pass-through-entity-tax/2025/502-vk-1-2025.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["va_pte_return", "va_ptet"],
        "excerpts": [
            {
                "excerpt_label": "VK-1 mirrors Form 502 line-for-line, EXCEPT Line 7 (instr. p.21, verbatim)",
                "excerpt_text": (
                    "'These items on Schedule VK-1 correspond to related items with the same line numbers "
                    "on Lines 1-11 of Form 502 and to certain lines of Sections A, B, and C of Schedule "
                    "502ADJ... The entries on each line of the Schedules VK-1 for all owners of the PTE "
                    "should equal the corresponding entry on Form 502 and Schedule 502ADJ, except for Line "
                    "7. The entry on Line 7 will be the same for all owners of the entity and the same as "
                    "Line 7 of Form 502 (the PTE's Virginia apportionment percentage).' 'The participation "
                    "percentages as shown on Schedules VK-1 for all owners of the PTE should equal 100%.' "
                    "[LINES a-f] a Date owner acquired interest; b Owner's entity type (code); c Owner's "
                    "participation type (code); d Owner's participation percentage; e Amount withheld by "
                    "PTE for the owner; f If owner or entity is exempt from withholding, enter an "
                    "exemption code."
                ),
                "summary_text": (
                    "The cross-form assertion set: sum(VK-1 Ln) = Form 502 Ln for n in 1-6, 8-11, 13, 18; "
                    "VK-1 L7 = Form 502 L7 for EVERY owner (never summed); sum(VK-1 Le) = Form 502 Lc; "
                    "sum(VK-1 Ld) = 100.00%."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Grantor-trust rule and the PTET credit no-reallocation bar (verbatim)",
                "excerpt_text": (
                    "'For grantor trusts where no Form 770 is being filed, enter \"RES\" if the owner will "
                    "file an individual Form 760 or Form 760PY resident return and \"NON\" if the owner "
                    "will file an individual Form 763 return... For all other grantor trusts, enter \"TE.\" "
                    "The PTET credit can only be claimed by direct owners of the PTE. A PTET credit that "
                    "is allocated to an estate or trust cannot subsequently be allocated to the "
                    "beneficiaries.' [OWNER EXEMPTION CODE 03] 'Individual owner is included in a "
                    "composite return, or the owner is eligible to claim the PTET Credit reported on Sch. "
                    "VK-1, Line 10.'"
                ),
                "summary_text": (
                    "Owner entity type must match the return the owner actually files; grantor trusts map "
                    "to RES/NON/TE. A PTET credit landing on an estate or trust STOPS there. Owner "
                    "exemption code 03 does double duty - composite AND eligible PTET owner."
                ),
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "VA_2025_FORM_502PTET_PKG",
        "source_type": "state_instruction",
        "source_rank": "primary_official",
        "jurisdiction_code": "VA",
        "title": "2025 Virginia Form 502PTET Instruction Package - Form 502PTET, Schedule PTET ADJ, Form 500C",
        "citation": "Va. 2025 Form 502PTET Instruction Package, 2601209 Rev. 08/26, 14 pp. - RE-ISSUED 2026-08-10 (ModDate D:20260810090247); contains 2601207-W, 2601208-W, 2601007-W",
        "issuer": "Virginia Department of Taxation",
        "official_url": "https://www.tax.virginia.gov/sites/default/files/taxforms/corporation-and-pass-through-entity-tax/2025/502ptet-instruction-package-2025.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.4,
        "topics": ["va_ptet"],
        "excerpts": [
            {
                "excerpt_label": "Form 502PTET Page 2 face - Sections I-V, verbatim line map",
                "excerpt_text": (
                    "SECTION I - Income Attributable to Eligible Owners, Column A Nonresident Owners / "
                    "Column B Resident Owners: 1 Owners' shares of taxable income; 2 Owners' shares of "
                    "Virginia additions; 3 Add Lines 1 and 2; 4 Owners' shares of Virginia subtractions; 5 "
                    "Virginia taxable income. Subtract Line 4 from Line 3 ('If Line 4 is greater than Line "
                    "3, enter zero'). SECTION II: 6 Total Virginia taxable income: Add Line 5, Columns A "
                    "and B (if negative, enter zero); 7a Pass-Through Entity Tax: Multiply Line 6 by "
                    "5.75%; 7b Withholding tax due for nonresident corporate owners; 7 Add amounts on "
                    "Lines 7a and 7b. SECTION III: 8 Estimated tax paid including any overpayment carried "
                    "over; 9 Extension payment, withholding paid prior to return filing, and other "
                    "payments; 10a Motion Picture Production Tax Credit; 10b Reserved for future use; 10c "
                    "Other (Reserved); 10 Add 10a, 10b, 10c; 11 Total payments and credits. Add Lines "
                    "8-10. SECTION IV: 12 Tax owed; 13 Overpayment amount; 14 Amount of Line 13 credited "
                    "to next year's estimated tax; 15 Net overpayment amount; 16 Addition to tax (Form "
                    "500C included); 17 Penalty; 18 Interest; 19 Total additional charges. Add Lines "
                    "16-18. SECTION V: 20 Amount owed; 21 Amount of refund."
                ),
                "summary_text": (
                    "Section I is a two-column build with a PER-COLUMN zero floor at Line 5 and a second "
                    "floor at Line 6. Line 7a (not Line 7) is the credit passed through to eligible owners."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Section I Line 1 - THE BASE DIVERGENCE from Form 502 (verbatim)",
                "excerpt_text": (
                    "'Compute the eligible owners' shares of taxable income, including amounts from the "
                    "\"Income\" and \"Deductions\" sections of the PTE's Schedule K... However, unlike the "
                    "computation of the nonresident withholding tax on Form 502, separately stated items "
                    "of deduction ARE included when calculating each eligible owner's share of the PTE's "
                    "taxable income on this form. For the purposes of the PTET, any separately stated item "
                    "of deduction that is subject to a federal limitation, such as the deduction for "
                    "charitable contributions and the Section 179 deduction, is limited to what is allowed "
                    "under federal law for a C corporation.' [PAGE 1 NOTE] 'Note: Lines 1-20 are based on "
                    "the entire pass-through entity. See the Form 502 Instructions for guidance.'"
                ),
                "summary_text": (
                    "Form 502 Line 1 is income ONLY; 502PTET Section I Line 1 is income NET of deductions "
                    "with s.179 and charitable re-limited to the federal C-corporation limits. Two "
                    "different bases on two forms with identical Page-1 numbering. Requires an "
                    "entity-level C-corp pro-forma recomputation with no federal analogue."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Election mechanics, binding effect, the 6-month hard bar, and the corporate penalty regime",
                "excerpt_text": (
                    "[ELECTION] 'Making an estimated payment of PTET for the taxable year, Making an "
                    "extension payment of PTET for the taxable year, Filing Form 502PTET on or before the "
                    "extended due date for the taxable year.' [BINDING] 'Once Form 502PTET is filed, the "
                    "election is binding for that taxable year... the election is binding on all the "
                    "eligible owners once the election is made. Eligible owners do not have the option to "
                    "opt out of an entity's election with the Department.' [HARD BAR] 'A PTE that fails to "
                    "file more than 6 months after the original due date, or more than 30 days after the "
                    "federal extended due date will not be permitted to file Form 502PTET unless it has "
                    "made corresponding estimated payments or an extension payment for the taxable year.' "
                    "[ESTIMATES] required if PTET 'can reasonably be expected to exceed $1,000'; four 25% "
                    "installments. [PENALTIES] Article 14 (s.58.1-450 et seq.) CORPORATE penalties, "
                    "'instead of the penalties in Article 9'; extension penalty 2%/month; late payment "
                    "6%/month max 30%; late filing 30% of tax due and 'In no case will the penalty for "
                    "failure to file timely be less than $100, and this minimum $100 penalty applies "
                    "whether or not tax is due.' [E-FILE] 'Paper submissions will not be accepted. Waivers "
                    "of the electronic filing requirement will not be granted.'"
                ),
                "summary_text": (
                    "The PTET runs on the CORPORATE penalty regime - a single PTE penalty engine will be "
                    "wrong on one of the two paths. The 6-month bar is a validation rule that REFUSES the "
                    "return. The e-file 'no waiver' line is administrative posture, not law (see s.58.1-392 E)."
                ),
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "U4 - the REPEALED sunset still printed six times in the RE-ISSUED Rev. 08/26 package",
                "excerpt_text": (
                    "The package re-issued 2026-08-10 still recites the sunset repealed by 2026 Acts of "
                    "Assembly c. 7 SIX times: 'Virginia established a new elective pass-through entity "
                    "(PTE) tax for Taxable Years 2021-2026'; 'For taxable years beginning on and after "
                    "January 1, 2021, but before January 1, 2027, a pass-through entity may make an annual "
                    "election'; 'An eligible owner may claim a corresponding refundable individual and "
                    "fiduciary income tax credit for Taxable Years 2021 through 2026'; '...in order to "
                    "make the PTET election for Taxable Years 2021-2026 was removed'; 'A PTE may make an "
                    "annual election on its timely filed Form 502PTET for taxable years beginning on or "
                    "after January 1, 2022, but before January 1, 2027'; and the definition of "
                    "'Pass-through entity elective tax'. THE STATUTE GOVERNS: Va. Code s.58.1-390.3 "
                    "contains no expiration date at all."
                ),
                "summary_text": (
                    "This is no longer 'a document that predates the law'; it is 'a document the DOR "
                    "revisited and did not fix'. Build to the statute. No sunset is encoded."
                ),
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "VA_CODE_58_1_390_3",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "VA",
        "title": "Va. Code 58.1-390.3 - Elective income tax on pass-through entities",
        "citation": "Va. Code s.58.1-390.3 (history 2022, cc. 690, 689; 2023, cc. 686, 687; 2025, c. 725; 2026, c. 7) - NO EXPIRATION DATE",
        "issuer": "Virginia General Assembly (Code of Virginia via LIS)",
        "official_url": "https://law.lis.virginia.gov/vacode/title58.1/chapter3/section58.1-390.3/",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.8,
        "topics": ["va_ptet"],
        "excerpts": [
            {
                "excerpt_label": "s.58.1-390.3 B, C, D, E, F - rate, nonresident limit, SALT add-back, refundable credit, corporate collection",
                "excerpt_text": (
                    "[B] 'A tax at the rate of 5.75 percent is hereby annually imposed on the Virginia "
                    "taxable income, as calculated pursuant to s.58.1-391 but taking into account only the "
                    "pro rata or distributive share of each item of income, gain, loss, or deduction "
                    "attributable to eligible owners, for each taxable year of every pass-through entity "
                    "that makes the election provided under subsection A.' [C] 'the pro rata or "
                    "distributive share of the Virginia taxable income of each nonresident eligible owner "
                    "shall be limited to income that is attributable to Virginia sources.' [D] '...provided "
                    "that a pass-through entity's taxable income shall be adjusted to eliminate any "
                    "federal deduction for state and local income taxes.' [E] 'Such credit shall be in an "
                    "amount equal to such person's pro rata share of the tax paid under this section... If "
                    "the amount of the credit... exceeds such person's tax liability... such excess shall "
                    "be treated as an overpayment and refundable pursuant to s.58.1-499.' [F] 'the "
                    "Department shall assess and collect tax, interest, and penalties as if such tax is a "
                    "corporate income tax imposed pursuant to the provisions of Article 10.'"
                ),
                "summary_text": (
                    "5.75% on eligible owners' shares only; SALT deduction eliminated from the base; the "
                    "owner credit is REFUNDABLE and lives in s.58.1-390.3 E (NOT s.58.1-332, which is the "
                    "separate out-of-state PTET credit at C.2); collected as a corporate income tax."
                ),
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "VA_CODE_58_1_486_2",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "VA",
        "title": "Va. Code 58.1-486.2 - Withholding tax on Virginia source income of nonresident owners",
        "citation": "Va. Code s.58.1-486.2 (subsections B.1 rate, C.4 four-or-fewer dwelling units, D.2 extension does not extend payment)",
        "issuer": "Virginia General Assembly (Code of Virginia via LIS)",
        "official_url": "https://law.lis.virginia.gov/vacode/title58.1/chapter3/section58.1-486.2/",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.8,
        "topics": ["va_pte_return"],
        "excerpts": [
            {
                "excerpt_label": "s.58.1-486.2 B.1 / C.4 / D.2 - the 5% rate, the live 55.1-1200 cite, and the payment date",
                "excerpt_text": (
                    "[B.1] 'The amount of withholding tax payable by any pass-through entity under this "
                    "article shall be equal to five percent of the nonresident owner's share of income "
                    "from Virginia sources...' [C.4] 'For the purposes of this subdivision, the term "
                    "\"person\" shall mean the same as that term is defined in s.55.1-1200.' - the LIVE "
                    "cite for the four-or-fewer-dwelling-units exception; the Form 502 instructions still "
                    "print the repealed s.55-248.4, recodified to Title 55.1 in 2019. [D.2] 'An extension "
                    "of time for filing the return... shall not extend the time for paying the amount of "
                    "withholding tax due.'"
                ),
                "summary_text": (
                    "The statutory anchor for the 5% rate - and the source relied on for Form 502PTET Line "
                    "7(b), which the PTET package never states (W4/U3). Encode s.55.1-1200, not the "
                    "instruction's dead cite."
                ),
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "VA_CODE_58_1_392",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "VA",
        "title": "Va. Code 58.1-392 - Pass-through entity returns; due date and electronic filing",
        "citation": "Va. Code s.58.1-392 (subsection A due date; subsection E electronic filing waivers)",
        "issuer": "Virginia General Assembly (Code of Virginia via LIS)",
        "official_url": "https://law.lis.virginia.gov/vacode/title58.1/chapter3/section58.1-392/",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.8,
        "topics": ["va_pte_return", "va_ptet"],
        "excerpts": [
            {
                "excerpt_label": "s.58.1-392 A and E - the statutory April 15 clock (W10) and the waiver machinery (W7)",
                "excerpt_text": (
                    "[A] 'shall make a return... on or before the fifteenth day of the fourth month "
                    "following the close of its taxable year.' This is the STATUTORY basis for the entity "
                    "clock and is stronger than the instruction text; Virginia's famous MAY 1 date belongs "
                    "to Form 760 and Form 770 only, and 'May 1' appears zero times in the 29-page Form 502 "
                    "book and zero times in the 14-page PTET package. [E] 'Pass-through entities may be "
                    "required to file the return using an electronic medium prescribed by the Tax "
                    "Commissioner... Waivers shall be granted only if the Tax Commissioner finds that the "
                    "requirement creates an unreasonable burden on the pass-through entity. All requests "
                    "for waivers must be submitted to the Tax Commissioner in writing.' Because "
                    "s.58.1-390.3 A.2 makes the PTET election one made 'on its timely filed return "
                    "pursuant to s.58.1-392', Form 502PTET IS a s.58.1-392 return and this waiver "
                    "machinery reaches it."
                ),
                "summary_text": (
                    "Settles W10 (two clocks provably coexist) and W7 (a 502PTET e-file waiver is legally "
                    "POSSIBLE - the package's 'will not be granted' is administrative posture)."
                ),
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "VA_CODE_58_1_408",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "VA",
        "title": "Va. Code 58.1-408 - What income apportioned and how (three factors, double-weighted sales)",
        "citation": "Va. Code s.58.1-408; applied to PTEs by the Form 502 instructions and ss.58.1-405 through 58.1-422.5",
        "issuer": "Virginia General Assembly (Code of Virginia via LIS)",
        "official_url": "https://law.lis.virginia.gov/vacode/title58.1/chapter3/section58.1-408/",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.8,
        "topics": ["va_pte_apportionment"],
        "excerpts": [
            {
                "excerpt_label": "s.58.1-408 - the statutory divide-by-four formula, and the PTE cross-reference",
                "excerpt_text": (
                    "'shall be apportioned to the Commonwealth by multiplying such income by a fraction, "
                    "the numerator of which is the property factor plus the payroll factor, plus twice the "
                    "sales factor, and the denominator of which is four.' [FORM 502 INSTRUCTIONS, p.5] 'If "
                    "a PTE conducts its business in Virginia and elsewhere in a manner such that its "
                    "income would be subject to a tax on net income in Virginia and at least one other "
                    "state, the entity must allocate and apportion its income in the same manner that is "
                    "provided in Virginia law for corporations. This applies to all types of pass-through "
                    "entities (partnerships, LLPs, LLCs, and S corporations).' Non-TPP sales are sourced "
                    "by COST OF PERFORMANCE (s.58.1-416 A), not market; market-based sourcing exists only "
                    "for the two VEDP hybrid carve-outs (ss.58.1-422.4, -422.5) and debt buyers "
                    "(s.58.1-416 B). No throwback or throwout rule appears anywhere in the sources."
                ),
                "summary_text": (
                    "The PTE apportionment rule does NOT differ from the corporate rule - statute and form "
                    "agree, and the 2026 General Assembly made no apportionment change at all."
                ),
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "VA_CODE_58_1_390_1",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "VA",
        "title": "Va. Code 58.1-390.1 - Definitions (eligible owner, owner, pass-through entity)",
        "citation": "Va. Code s.58.1-390.1",
        "issuer": "Virginia General Assembly (Code of Virginia via LIS)",
        "official_url": "https://law.lis.virginia.gov/vacode/title58.1/chapter3/section58.1-390.1/",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.8,
        "topics": ["va_ptet"],
        "excerpts": [
            {
                "excerpt_label": "Eligible owner vs. who may elect - two different questions",
                "excerpt_text": (
                    "[s.58.1-390.1] '\"Eligible owner\" means a DIRECT owner of a pass-through entity who "
                    "is a natural person subject to the tax imposed by Article 2 (s.58.1-320 et seq.) or "
                    "an estate or trust subject to the tax imposed by Article 6 (s.58.1-360 et seq.).' "
                    "[FORM 502 INSTRUCTIONS p.3] 'Beginning with Taxable Year 2023, the requirement that a "
                    "PTE must be 100% owned by natural persons or persons eligible to be shareholders of "
                    "an S corporation in order to make the PTET election... was removed... All PTEs can "
                    "make the PTE election, but only owners meeting the eligible owner requirement are "
                    "eligible to claim the refundable PTET credits.'"
                ),
                "summary_text": (
                    "The ENTITY gate is open - any PTE may elect. The BASE is narrowed to eligible owners' "
                    "shares, and ineligible owners get nothing. Three owner classes must be tracked."
                ),
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "VA_2025_FORM_502W",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "VA",
        "title": "2025 Virginia Form 502W - Pass-Through Entity Withholding Tax Payment Voucher",
        "citation": "Va. Form 502W (2025), 2601021-W Rev. 07/26 (PDF ModDate 2026-07-23)",
        "issuer": "Virginia Department of Taxation",
        "official_url": "https://www.tax.virginia.gov/sites/default/files/taxforms/corporation-and-pass-through-entity-tax/2025/502w-2025.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.2,
        "topics": ["va_pte_return"],
        "excerpts": [
            {
                "excerpt_label": "Form 502W - the operational confirmation of the April 15 withholding payment date",
                "excerpt_text": (
                    "'For calendar year filers, the withholding tax payment is due on April 15, 2026.' The "
                    "5% withholding rate is restated on the voucher. Weekend/holiday rollover applies: "
                    "'When the last day... falls on a Saturday, Sunday, or legal holiday, you may file and "
                    "make payment without penalty or interest on the next succeeding business day.'"
                ),
                "summary_text": "Operational confirmation of the entity clock and the never-extending payment date.",
                "is_key_excerpt": False,
            },
        ],
    },
    {
        "source_code": "RP_2024_40_VA_179_DERIVED_ONLY",
        "source_type": "official_revenue_procedure",
        "source_rank": "reference_only",
        "jurisdiction_code": "VA",
        "title": "Rev. Proc. 2024-40 s.3.25 - pre-OBBBA indexed IRC 179 amounts, used ONLY as a DERIVED Virginia figure",
        "citation": "Rev. Proc. 2024-40 s.3.25 - NOT A VIRGINIA SOURCE. Attribution to Virginia is an inference from TB 26-1's 'as if the 2025 H.R. 1 changes had not been enacted'.",
        "issuer": "Internal Revenue Service (cited here as a DERIVED figure only)",
        "official_url": "https://www.irs.gov/pub/irs-drop/rp-24-40.pdf",
        "current_status": "active",
        "is_substantive_authority": False,
        "requires_human_review": True,
        "trust_score": 6.0,
        "topics": ["va_conformity_adjustment"],
        "excerpts": [
            {
                "excerpt_label": "W3/U2 - the DERIVED Sec.179 figures, and the Virginia-source TODO that must close",
                "excerpt_text": (
                    "[Rev. Proc. 2024-40 s.3.25, verbatim] 'the aggregate cost of any s.179 property that "
                    "a taxpayer elects to treat as an expense cannot exceed $1,250,000 and... the cost of "
                    "any sport utility vehicle... cannot exceed $31,300. ... the $1,250,000 limitation... "
                    "is reduced (but not below zero) by the amount by which the cost of s.179 property "
                    "placed in service during the 2025 taxable year exceeds $3,130,000.' *** VIRGINIA HAS "
                    "PUBLISHED NO SEC.179 DOLLAR LIMIT AND NO PHASE-OUT THRESHOLD OF ITS OWN - confirmed "
                    "by exhaustion from the 2025 Form 502 instruction book (one structural mention of "
                    "'179', no figure), the 2025 Form 502PTET package (same), the corporate 2025 Form 500 "
                    "instruction book (ZERO occurrences of '179', '174', '168(n)'), TB 26-1 and the 2026 "
                    "Legislative Summary. *** The federal OBBBA $2,500,000 / $4,000,000 figures must NEVER "
                    "be used for Virginia. Encode as a configurable derived constant with a "
                    "Virginia-source TODO, never as a Virginia-published constant."
                ),
                "summary_text": (
                    "Virginia publishes NO Sec.179 figure. The 1,250,000 / 3,130,000 / 31,300 amounts are "
                    "DERIVED, not Virginia-sourced. W3 is Ken's call; nothing Virginia-labelled is seeded."
                ),
                "is_key_excerpt": True,
            },
        ],
    },
]

AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    ("VA_2025_FORM_502", "VA_502", "governs"),
    ("VA_2025_FORM_502_INSTR", "VA_502", "governs"),
    ("VA_2025_SCH_502A", "VA_502", "governs"),
    ("VA_2025_SCH_502ADJ", "VA_502", "governs"),
    ("VA_2025_SCH_VK1", "VA_502", "governs"),
    ("VA_2025_FORM_502W", "VA_502", "informs"),
    ("VA_CODE_58_1_392", "VA_502", "governs"),
    ("VA_CODE_58_1_408", "VA_502", "governs"),
    ("VA_CODE_58_1_486_2", "VA_502", "governs"),
    ("VA_CODE_58_1_301", "VA_502", "governs"),
    ("VA_TB_26_1", "VA_502", "informs"),
    ("RP_2024_40_VA_179_DERIVED_ONLY", "VA_502", "informs"),
    ("VA_2025_FORM_502PTET_PKG", "VA_502PTET", "governs"),
    ("VA_2025_FORM_502_INSTR", "VA_502PTET", "informs"),
    ("VA_2025_SCH_502A", "VA_502PTET", "governs"),
    ("VA_2025_SCH_VK1", "VA_502PTET", "governs"),
    ("VA_CODE_58_1_390_1", "VA_502PTET", "governs"),
    ("VA_CODE_58_1_390_3", "VA_502PTET", "governs"),
    ("VA_CODE_58_1_392", "VA_502PTET", "governs"),
    ("VA_CODE_58_1_486_2", "VA_502PTET", "informs"),
    ("VA_CODE_58_1_301", "VA_502PTET", "governs"),
    ("VA_TB_26_1", "VA_502PTET", "informs"),
    ("RP_2024_40_VA_179_DERIVED_ONLY", "VA_502PTET", "informs"),
]


# ===========================================================================
# THE SHARED PAGE-1 BLOCK
# Form 502 and Form 502PTET carry Lines 1-20 IDENTICALLY. Only the adjustment
# schedule name changes. Built once here so the two specs cannot drift apart.
# ===========================================================================

def _page1_facts() -> list[dict]:
    """Facts for Page 1 Lines a-d and 1-20, identical on both forms."""
    facts: list[dict] = [
        {"fact_key": "entity_module", "label": "Federal module (1065 partnership or 1120S S corporation)",
         "data_type": "choice", "required": True, "sort_order": 1, "choices": ["1065", "1120S"],
         "notes": "Drives all SIX branch points (brief Sec.2.1). Lines 1-20 are identical either way."},
        {"fact_key": "entity_type_code", "label": "Entity Type code (face; 'A proper entry in this field is required')",
         "data_type": "choice", "required": True, "sort_order": 2,
         "choices": list(VA_ENTITY_TYPE_CODES_PARTNERSHIP) + [VA_ENTITY_TYPE_CODE_SCORP],
         "notes": "BRANCH 1. SC is the only valid code for the 1120S module."},
        {"fact_key": "federal_enclosure_kind", "label": "Required federal enclosure",
         "data_type": "choice", "required": True, "sort_order": 3,
         "choices": ["1065_with_schedule_k", "1120S_with_schedule_k"],
         "notes": "BRANCH 5. No federal Schedule K-1; do not submit Schedules K-2 or K-3."},
        {"fact_key": "subject_to_bank_franchise_tax", "label": "Subject to Bank Franchise Tax (checkbox)",
         "data_type": "boolean", "required": False, "sort_order": 4,
         "notes": "BRANCH 6 - an S-CORP-ONLY consequence -> Schedule 502ADJ Code 99 -> owner Code 112. R13."},
        {"fact_key": "amended_reason_code", "label": "Amended return reason code",
         "data_type": "choice", "required": False, "sort_order": 5, "choices": list(VA_AMENDED_REASON_CODES),
         "notes": "02 partnership-level federal adjustment (R6); 05 PTET amended return."},
        {"fact_key": "fiscal_or_short_year", "label": "Fiscal or short year filer", "data_type": "boolean",
         "required": False, "sort_order": 6},
        {"fact_key": "is_single_member_disregarded_llc", "label": "Single-member LLC disregarded federally",
         "data_type": "boolean", "required": False, "sort_order": 7,
         "notes": "RULE SAYS NO: 'The disregarded entity is not required to file Form 502.' Opposite of TN's J2 trap."},
        {"fact_key": "is_investment_only_pte", "label": "PTE established solely to invest in intangible personal property",
         "data_type": "boolean", "required": False, "sort_order": 8,
         "notes": "No employees, no real or tangible property -> not carrying on a trade or business -> no Form 502."},
        # Lines a-d
        {"fact_key": "owner_count_total", "label": "Line a - total number of owners (all types)",
         "data_type": "integer", "required": True, "sort_order": 10,
         "notes": "BRANCH 2. 1065: Form 1065 Page 1 item I. 1120S: Form 1120-S Page 1 item I (shareholders during ANY part of the year)."},
        {"fact_key": "owner_count_nonresident", "label": "Line b - total number of nonresident owners",
         "data_type": "integer", "required": False, "sort_order": 11},
        {"fact_key": "entity_withholding_exemption_code", "label": "Line d - entity withholding exemption code",
         "data_type": "choice", "required": False, "sort_order": 12, "choices": list(VA_ENTITY_EXEMPTION_CODES),
         "notes": "ALL-OR-NOTHING entity flag. Partial exemptions belong on VK-1 Line f, NOT here."},
        # Line 1 worksheet (W9) - a real, visible 12-line worksheet
        {"fact_key": "wk_ordinary_income", "label": "L1 wks 1 - Ordinary income (loss) from trade or business",
         "data_type": "decimal", "required": False, "sort_order": 20},
        {"fact_key": "wk_rental_real_estate", "label": "L1 wks 2 - Net income (loss) from rental real estate",
         "data_type": "decimal", "required": False, "sort_order": 21},
        {"fact_key": "wk_other_rental", "label": "L1 wks 3 - Net income (loss) from other rental activity",
         "data_type": "decimal", "required": False, "sort_order": 22},
        {"fact_key": "wk_interest", "label": "L1 wks 4 - Interest income", "data_type": "decimal",
         "required": False, "sort_order": 23},
        {"fact_key": "wk_dividends", "label": "L1 wks 5 - Dividend income", "data_type": "decimal",
         "required": False, "sort_order": 24},
        {"fact_key": "wk_royalty", "label": "L1 wks 6 - Royalty income", "data_type": "decimal",
         "required": False, "sort_order": 25},
        {"fact_key": "wk_other_portfolio", "label": "L1 wks 7 - Other portfolio income", "data_type": "decimal",
         "required": False, "sort_order": 26},
        {"fact_key": "wk_st_capital_gain", "label": "L1 wks 8 - Net short-term capital gain (loss)",
         "data_type": "decimal", "required": False, "sort_order": 27},
        {"fact_key": "wk_lt_capital_gain", "label": "L1 wks 9 - Net long-term capital gain (loss)",
         "data_type": "decimal", "required": False, "sort_order": 28},
        {"fact_key": "wk_1231_gain", "label": "L1 wks 10 - Net IRC 1231 gain (loss)", "data_type": "decimal",
         "required": False, "sort_order": 29},
        {"fact_key": "wk_other_income", "label": "L1 wks 11 - Other taxable income (loss)", "data_type": "decimal",
         "required": False, "sort_order": 30},
        {"fact_key": "l1_no_double_count_confirmed",
         "label": "Preparer affirms each income category is the YEARLY total, not double counted",
         "data_type": "boolean", "required": True, "sort_order": 31,
         "notes": "W9. The DOR Caution: Schedule K entries may OVERLAP in a federal mid-year-change year. "
                  "The engine must never scrape Schedule K unattended."},
        {"fact_key": "total_deductions", "label": "Line 2 - Total deductions (Schedule K 'Deductions' section)",
         "data_type": "decimal", "required": False, "sort_order": 32,
         "notes": "DOES NOT REDUCE LINE 1. Informational carrier to VK-1 - but it IS in the 502PTET base."},
        {"fact_key": "tax_exempt_interest", "label": "Line 3 - Tax-exempt interest income", "data_type": "decimal",
         "required": False, "sort_order": 33,
         "notes": "1065 Sch K L18a; 1120-S Sch K L16a (under 'Items Affecting Shareholder Basis', not 'Other' - U13)."},
        # Apportionment inputs
        {"fact_key": "wholly_within_virginia", "label": "PTE conducted business ENTIRELY within Virginia",
         "data_type": "boolean", "required": False, "sort_order": 40,
         "notes": "Short path: leave L4/L5 blank, repeat L1 on L6, enter 100% on L7 - skips Schedule 502A."},
        {"fact_key": "apportionment_method_box", "label": "Schedule 502A Section A method box (1-9)",
         "data_type": "integer", "required": False, "sort_order": 41,
         "notes": "Box 9 (multi-factor double-weighted sales) is the default and the only one computed in v1. Boxes 1-8 -> R4."},
        {"fact_key": "commercial_domicile_in_va", "label": "Commercial domicile is in Virginia",
         "data_type": "boolean", "required": False, "sort_order": 42},
        {"fact_key": "dividends_received", "label": "Schedule 502A Section C - dividends received",
         "data_type": "decimal", "required": False, "sort_order": 43},
        {"fact_key": "nonapport_investment_income", "label": "502A C 3(b) - nonapportionable investment function income",
         "data_type": "decimal", "required": False, "sort_order": 44,
         "notes": "Allied-Signal relief; clear and cogent evidence required -> R5."},
        {"fact_key": "nonapport_investment_loss", "label": "502A C 3(d) - nonapportionable investment function loss",
         "data_type": "decimal", "required": False, "sort_order": 45,
         "notes": "One-way ratchet: a prior subtraction creates a permanent obligation to add back later losses. R5."},
        {"fact_key": "property_factor_va_begin", "label": "502A B 2(a) - Virginia property, beginning (original cost)",
         "data_type": "decimal", "required": False, "sort_order": 46},
        {"fact_key": "property_factor_va_end", "label": "502A B 2(a) - Virginia property, ending (original cost)",
         "data_type": "decimal", "required": False, "sort_order": 47},
        {"fact_key": "property_factor_ew_begin", "label": "502A B 2(a) - everywhere property, beginning",
         "data_type": "decimal", "required": False, "sort_order": 48},
        {"fact_key": "property_factor_ew_end", "label": "502A B 2(a) - everywhere property, ending",
         "data_type": "decimal", "required": False, "sort_order": 49},
        {"fact_key": "property_rent_va", "label": "502A B 2(a) - Virginia annual rental rate (entered at 8x)",
         "data_type": "decimal", "required": False, "sort_order": 50},
        {"fact_key": "property_rent_ew", "label": "502A B 2(a) - everywhere annual rental rate (entered at 8x)",
         "data_type": "decimal", "required": False, "sort_order": 51},
        {"fact_key": "payroll_factor_va", "label": "502A B 2(b) - Virginia payroll", "data_type": "decimal",
         "required": False, "sort_order": 52},
        {"fact_key": "payroll_factor_ew", "label": "502A B 2(b) - everywhere payroll", "data_type": "decimal",
         "required": False, "sort_order": 53},
        {"fact_key": "sales_factor_va", "label": "502A B 2(c) - Virginia sales (destination TPP; COST OF PERFORMANCE non-TPP)",
         "data_type": "decimal", "required": False, "sort_order": 54,
         "notes": "'Sales' excludes dividends; on intangibles only the NET GAIN, per transaction."},
        {"fact_key": "sales_factor_ew", "label": "502A B 2(c) - everywhere sales", "data_type": "decimal",
         "required": False, "sort_order": 55},
        {"fact_key": "single_factor_percentage", "label": "502A B Line 1 - single-factor percentage (method boxes 1-8)",
         "data_type": "decimal", "required": False, "sort_order": 56,
         "notes": "DIRECT-ENTRY. Built live so the arithmetic is right the day a non-default method lands (R4)."},
        # Conformity lines - DIRECT-ENTRY (W5)
        {"fact_key": "conformity_depreciation_addition", "label": "Line 8 - Conformity, depreciation (bonus recompute addition)",
         "data_type": "decimal", "required": False, "sort_order": 60,
         "notes": "BONUS ONLY, vintages 2001-2025. Direct-entry in v1 (W5); Virginia basis book is R2."},
        {"fact_key": "conformity_disposed_asset_addition", "label": "Line 9(1) - Conformity, other: Disposed Asset addition",
         "data_type": "decimal", "required": False, "sort_order": 61,
         "notes": "The federal-vs-Virginia BASIS DIFFERENCE on a disposed bonus asset."},
        {"fact_key": "conformity_bucket_addition", "label": "Line 9(2) - Conformity Additions (residual bucket)",
         "data_type": "decimal", "required": False, "sort_order": 62,
         "notes": "W2/U1. WIDER THAN H.R.1 - also AHYDO, COD income, 2008/09 NOL carryback, CARES items. "
                  "Enclose a schedule and explanation; there is no DOR worksheet."},
        {"fact_key": "income_tax_addback", "label": "Line 10 - Net income tax or other tax used as a deduction",
         "data_type": "decimal", "required": False, "sort_order": 63,
         "notes": "Includes franchise/excise taxes measured by net income. NOT the same as Schedule 502ADJ Section C Part I Line 1."},
        {"fact_key": "muni_interest_other_states", "label": "Line 11 - Interest on non-Virginia municipal or state obligations",
         "data_type": "decimal", "required": False, "sort_order": 64},
        {"fact_key": "adj_additions_total", "label": "Line 12 - Total additions from the adjustment schedule, Section A Line 5",
         "data_type": "decimal", "required": False, "sort_order": 65},
        {"fact_key": "conformity_depreciation_subtraction", "label": "Line 14 - Conformity, depreciation (subtraction)",
         "data_type": "decimal", "required": False, "sort_order": 66},
        {"fact_key": "conformity_disposed_asset_subtraction", "label": "Line 15(1) - Conformity, other: Disposed Asset subtraction",
         "data_type": "decimal", "required": False, "sort_order": 67},
        {"fact_key": "conformity_bucket_subtraction", "label": "Line 15(2) - Conformity Subtractions (residual bucket)",
         "data_type": "decimal", "required": False, "sort_order": 68,
         "notes": "Note the asymmetry: Line 15(2) omits the word 'other' that Line 9(2) carries."},
        {"fact_key": "us_obligations_income", "label": "Line 16 - Income from obligations of the United States",
         "data_type": "decimal", "required": False, "sort_order": 69,
         "notes": "Interest, dividends AND gain. Excludes interest on federal refunds and equipment purchase contracts."},
        {"fact_key": "adj_subtractions_total", "label": "Line 17 - Total subtractions from the adjustment schedule, Section B Line 5",
         "data_type": "decimal", "required": False, "sort_order": 70},
        {"fact_key": "nonrefundable_credits_total", "label": "Line 19 - Total nonrefundable credits (Section C Part II Line 1)",
         "data_type": "decimal", "required": False, "sort_order": 71},
        {"fact_key": "refundable_credits_total", "label": "Line 20 - Total refundable credits (Section C Part IV Line 1)",
         "data_type": "decimal", "required": False, "sort_order": 72},
        # Depreciation / conformity triggers that drive the RED-defers
        {"fact_key": "has_federal_bonus_depreciation", "label": "Federal bonus depreciation present (any vintage 2001-2025)",
         "data_type": "boolean", "required": False, "sort_order": 80, "notes": "Triggers R2."},
        {"fact_key": "has_168n_or_174a_or_179_excess", "label": "Federal 168(n) / 174A / s.179 above the Virginia figure present",
         "data_type": "boolean", "required": False, "sort_order": 81, "notes": "Triggers R2 and the W2 bucket prompt."},
        {"fact_key": "has_174a_catchup", "label": "Federal 174A retroactive or catch-up deduction present",
         "data_type": "boolean", "required": False, "sort_order": 82, "notes": "Triggers R3 - no Virginia counterpart exists."},
        {"fact_key": "sec179_claimed_federal", "label": "Federal IRC 179 expense claimed", "data_type": "decimal",
         "required": False, "sort_order": 83,
         "notes": "W3: Virginia publishes NO s.179 figure. Compared against the DERIVED constant only, with a review flag."},
        # Owner roster
        {"fact_key": "owner_roster", "label": "Owner roster (entity type, participation type/%, residency, exemption code)",
         "data_type": "string", "required": True, "sort_order": 90,
         "notes": "BRANCHES 3 and 4. Participation % source differs by module; grantor trusts map RES/NON/TE."},
    ]
    return facts


def _page1_lines(adj_schedule: str, form_code: str) -> list[dict]:
    """Page 1 Lines a-d and 1-20. IDENTICAL on both forms except the schedule name."""
    return [
        {"line_number": "a", "description": "Total number of owners (include individuals and any other entity types)",
         "line_type": "input", "source_facts": ["owner_count_total"], "sort_order": 1,
         "notes": "BRANCH 2 - 1065 Page 1 item I vs 1120-S Page 1 item I. Same letter, different meaning."},
        {"line_number": "b", "description": "Total number of nonresident owners", "line_type": "input",
         "source_facts": ["owner_count_nonresident"], "sort_order": 2},
        {"line_number": "c", "description": "Total amount withheld for nonresident owners (total of Line e from all Schedules VK-1)",
         "line_type": "calculated", "source_rules": [f"{form_code}-VK1"], "sort_order": 3},
        {"line_number": "d", "description": "If the entity is exempt from withholding, enter the exemption code",
         "line_type": "input", "source_facts": ["entity_withholding_exemption_code"], "sort_order": 4,
         "notes": "ALL-OR-NOTHING. A PTE with both individual and corporate owners should NOT flag exempt here."},
        {"line_number": "1", "description": "Total taxable income amounts (12-line worksheet; INCOME ONLY - Line 2 does not reduce it)",
         "line_type": "calculated", "source_rules": [f"{form_code}-L1"], "sort_order": 11},
        {"line_number": "2", "description": "Total deductions (Schedule K 'Deductions' section; charitable, IRC 179, other)",
         "line_type": "input", "source_facts": ["total_deductions"], "sort_order": 12},
        {"line_number": "3", "description": "Tax-exempt interest income", "line_type": "input",
         "source_facts": ["tax_exempt_interest"], "sort_order": 13},
        {"line_number": "4", "description": f"Income allocated to Virginia from Schedule 502A, Section C, Line 2",
         "line_type": "calculated", "source_rules": [f"{form_code}-502AC"], "sort_order": 14},
        {"line_number": "5", "description": "Income allocated outside of Virginia from Schedule 502A, Section C, Line 3(e)",
         "line_type": "calculated", "source_rules": [f"{form_code}-502AC"], "sort_order": 15},
        {"line_number": "6", "description": "Apportionable income from Schedule 502A, Section C, Line 4",
         "line_type": "calculated", "source_rules": [f"{form_code}-502AC"], "sort_order": 16},
        {"line_number": "7", "description": "Virginia apportionment percentage from Schedule 502A, Section B, Line 1 or Line 2(f) or 100%",
         "line_type": "calculated", "source_rules": [f"{form_code}-502AB"], "sort_order": 17},
        {"line_number": "8", "description": "Conformity - depreciation (bonus recompute addition; vintages 2001-2025 ONLY)",
         "line_type": "input", "source_facts": ["conformity_depreciation_addition"], "sort_order": 18},
        {"line_number": "9", "description": "Conformity - other: (1) Disposed Asset and (2) Conformity Additions (residual bucket)",
         "line_type": "input",
         "source_facts": ["conformity_disposed_asset_addition", "conformity_bucket_addition"], "sort_order": 19,
         "notes": "ONE undifferentiated dollar box carrying two sub-items. The engine can compute the "
                  "components but the FORM cannot report them separately - a real diagnostics limitation."},
        {"line_number": "10", "description": "Net income tax or other tax used as a deduction in determining taxable income",
         "line_type": "input", "source_facts": ["income_tax_addback"], "sort_order": 20,
         "notes": "'defined differently and is not necessarily the same amount' as Schedule 502ADJ Section C Part I Line 1."},
        {"line_number": "11", "description": "Interest on municipal or state obligations other than from Virginia",
         "line_type": "input", "source_facts": ["muni_interest_other_states"], "sort_order": 21},
        {"line_number": "12", "description": f"Total additions from enclosed {adj_schedule}, Section A, Line 5",
         "line_type": "input", "source_facts": ["adj_additions_total"], "sort_order": 22},
        {"line_number": "13", "description": "Total additions. Add Lines 8 through 12.", "line_type": "subtotal",
         "source_rules": [f"{form_code}-ADD"], "sort_order": 23},
        {"line_number": "14", "description": "Conformity - depreciation (subtraction)", "line_type": "input",
         "source_facts": ["conformity_depreciation_subtraction"], "sort_order": 24},
        {"line_number": "15", "description": "Conformity - other: (1) Disposed Asset and (2) Conformity Subtractions",
         "line_type": "input",
         "source_facts": ["conformity_disposed_asset_subtraction", "conformity_bucket_subtraction"], "sort_order": 25},
        {"line_number": "16", "description": "Income from obligations of the United States (interest, dividends and gain)",
         "line_type": "input", "source_facts": ["us_obligations_income"], "sort_order": 26},
        {"line_number": "17", "description": f"Total subtractions from enclosed {adj_schedule}, Section B, Line 5",
         "line_type": "input", "source_facts": ["adj_subtractions_total"], "sort_order": 27},
        {"line_number": "18", "description": "Total subtractions. Add Lines 14 through 17.", "line_type": "subtotal",
         "source_rules": [f"{form_code}-SUB"], "sort_order": 28},
        {"line_number": "19", "description": f"Total nonrefundable credits from enclosed {adj_schedule}, Section C, Part II, Line 1",
         "line_type": "calculated", "source_rules": [f"{form_code}-CRED"], "sort_order": 29},
        {"line_number": "20", "description": f"Total refundable credits from enclosed {adj_schedule}, Section C, Part IV, Line 1",
         "line_type": "calculated", "source_rules": [f"{form_code}-CRED"], "sort_order": 30},
        # Schedule 502A (shared, identical on both paths)
        {"line_number": "502A-B1", "description": "Schedule 502A Section B Line 1 - single factor percentage (method boxes 1-8)",
         "line_type": "input", "source_facts": ["single_factor_percentage"], "sort_order": 40},
        {"line_number": "502A-B2a", "description": "Property Factor (original cost; rented property at 8x annual rent; begin/end average)",
         "line_type": "calculated", "source_rules": [f"{form_code}-502AB"], "sort_order": 41},
        {"line_number": "502A-B2b", "description": "Payroll Factor", "line_type": "calculated",
         "source_rules": [f"{form_code}-502AB"], "sort_order": 42},
        {"line_number": "502A-B2c", "description": "Sales Factor (destination TPP; COST OF PERFORMANCE for non-TPP)",
         "line_type": "calculated", "source_rules": [f"{form_code}-502AB"], "sort_order": 43},
        {"line_number": "502A-B2d", "description": "Double-Weighted Sales Factor: Multiply the sales factor from Line 2(c) by 2",
         "line_type": "calculated", "source_rules": [f"{form_code}-502AB"], "sort_order": 44},
        {"line_number": "502A-B2e", "description": "Sum of Percentages. Add Lines 2(a), 2(b), and 2(d).",
         "line_type": "subtotal", "source_rules": [f"{form_code}-502AB"], "sort_order": 45},
        {"line_number": "502A-B2f", "description": "Multi-Factor Percentage: Divide Line 2e by 4, reduced by the number of factors having no denominator",
         "line_type": "calculated", "source_rules": [f"{form_code}-502AB"], "sort_order": 46},
        {"line_number": "502A-C1", "description": "Total of taxable income amounts from Form 502, Line 1",
         "line_type": "calculated", "source_rules": [f"{form_code}-502AC"], "sort_order": 47},
        {"line_number": "502A-C2", "description": "If commercial domicile is in Virginia, enter dividends received here and on Line 4",
         "line_type": "calculated", "source_rules": [f"{form_code}-502AC"], "sort_order": 48},
        {"line_number": "502A-C3a", "description": "If commercial domicile is not in Virginia: dividends received",
         "line_type": "input", "source_facts": ["dividends_received"], "sort_order": 49},
        {"line_number": "502A-C3b", "description": "Nonapportionable investment function income (Allied-Signal) - R5",
         "line_type": "input", "source_facts": ["nonapport_investment_income"], "sort_order": 50},
        {"line_number": "502A-C3c", "description": "Add Lines 3(a) and 3(b)", "line_type": "subtotal",
         "source_rules": [f"{form_code}-502AC"], "sort_order": 51},
        {"line_number": "502A-C3d", "description": "Nonapportionable investment function loss (Allied-Signal) - R5",
         "line_type": "input", "source_facts": ["nonapport_investment_loss"], "sort_order": 52},
        {"line_number": "502A-C3e", "description": "Allocable Income - Subtract Line 3(d) from Line 3(c). Enter here and on Line 5.",
         "line_type": "calculated", "source_rules": [f"{form_code}-502AC"], "sort_order": 53},
        {"line_number": "502A-C4", "description": "Apportionable Income - domiciled in VA: L1 - L2; not domiciled: L1 - L3(e). Enter on Line 6.",
         "line_type": "calculated", "source_rules": [f"{form_code}-502AC"], "sort_order": 54},
        # Adjustment schedule totals + VK-1 (shared shape)
        {"line_number": "ADJ-A5", "description": f"{adj_schedule} Section A Line 5 - Total Additions. Add Lines 1-4 (502ADJS overflow rolls up here).",
         "line_type": "input", "source_facts": ["adj_additions_total"], "sort_order": 60},
        {"line_number": "ADJ-B5", "description": f"{adj_schedule} Section B Line 5 - Total Subtractions. Add Lines 1-4.",
         "line_type": "input", "source_facts": ["adj_subtractions_total"], "sort_order": 61},
        {"line_number": "ADJ-C-II-1", "description": "Section C Part II Line 1 - Add Part I, Lines 1-8, 12-15, 17, 21, 23, and 25 through 27",
         "line_type": "calculated", "source_rules": [f"{form_code}-CRED"], "sort_order": 62,
         "notes": "ENUMERATED. The skipped numbers are exactly the nine Reserved slots."},
        {"line_number": "VK1-d", "description": "VK-1 Line d - owner's participation percentage (must total 100.00%)",
         "line_type": "calculated", "source_rules": [f"{form_code}-VK1"], "sort_order": 65,
         "notes": "BRANCH 3 - 1065 K-1 item J ENDING PROFIT %; 1120-S K-1 item G AS PRINTED."},
        {"line_number": "VK1-e", "description": "VK-1 Line e - amount withheld by PTE for the owner (sums to Form 502 Line c)",
         "line_type": "calculated", "source_rules": [f"{form_code}-VK1"], "sort_order": 66},
        {"line_number": "VK1-f", "description": "VK-1 Line f - owner withholding exemption code (superset of the entity codes)",
         "line_type": "input", "source_facts": ["owner_roster"], "sort_order": 67,
         "notes": "Code 03 does double duty: on a composite return OR an eligible PTET owner."},
        {"line_number": "VK1-7", "description": "VK-1 Line 7 - the PTE apportionment percentage, SAME for every owner (never summed)",
         "line_type": "calculated", "source_rules": [f"{form_code}-VK1"], "sort_order": 68},
        {"line_number": "VK1-PIII-10", "description": "VK-1 Part III Line 10 - Pass-Through Entity Elective Tax Payment Credit",
         "line_type": "calculated", "source_rules": [f"{form_code}-VK1"], "sort_order": 69,
         "notes": "Printed on the NON-PTET VK-1 too, and VK-1 Part IV ALWAYS includes it while Schedule "
                  "502ADJ Part IV does not. Assert PER LINE, never on the totals."},
    ]


def _page1_rules(prefix: str, adj_schedule: str) -> list[dict]:
    """The shared Page-1 rule block, instantiated once per form code."""
    return [
        {"rule_id": f"{prefix}-MODULE", "title": "Module branch: 1065 vs 1120S - the six divergences", "rule_type": "classification",
         "formula": ("entity_module=1120S -> entity_type_code=SC ; owner count from Form 1120-S Page 1 item I ; "
                     "participation % from K-1 (1120-S) item G AS PRINTED ; participation type=SHR ; "
                     "enclose Form 1120-S with Schedule K ; bank-franchise branch AVAILABLE. "
                     "entity_module=1065 -> entity_type_code in {PG,PL,LL,LP,NZ,OB} ; owner count from Form 1065 "
                     "Page 1 item I ; participation % from K-1 (1065) item J ENDING PROFIT % ; participation type "
                     "in {GPT,LPT,LLM,OTR} ; enclose Form 1065 with Schedule K ; Form 502FED-1 path EXISTS."),
         "inputs": ["entity_module", "entity_type_code", "federal_enclosure_kind", "subject_to_bank_franchise_tax"],
         "outputs": ["entity_type_code", "owner_count_total", "VK1-d", "VK1-c"], "sort_order": 1,
         "description": ("Lines 1-20 are IDENTICAL for both modules - the branch is entirely in these six places "
                         "(brief Sec.2.1). Signature authority also differs: an officer of the S corporation, a "
                         "general partner, or an authorized LLC member.")},
        {"rule_id": f"{prefix}-L1", "title": "Line 1 - the 12-line income worksheet (INCOME ONLY)", "rule_type": "calculation",
         "formula": ("L1 = wk_ordinary_income + wk_rental_real_estate + wk_other_rental + wk_interest + wk_dividends "
                     "+ wk_royalty + wk_other_portfolio + wk_st_capital_gain + wk_lt_capital_gain + wk_1231_gain "
                     "+ wk_other_income ; L1 is NOT reduced by L2 ; L1 -> Schedule 502A Section C Line 1"),
         "inputs": list(VA_L1_WORKSHEET_KEYS) + ["l1_no_double_count_confirmed"], "outputs": ["1"], "sort_order": 2,
         "description": ("W9. Schedule K carries NO total and entries may OVERLAP in a federal mid-year-change "
                         "year - 'For each category of income, include only the yearly total in the Virginia "
                         "computation; do not omit, duplicate, or count any amounts twice.' The engine sums the "
                         "eleven affirmed yearly totals; it never scrapes Schedule K unattended.")},
        {"rule_id": f"{prefix}-ADD", "title": "Line 13 - Total additions. Add Lines 8 through 12.", "rule_type": "calculation",
         "formula": "L13 = L8 + L9 + L10 + L11 + L12",
         "inputs": ["conformity_depreciation_addition", "conformity_disposed_asset_addition",
                    "conformity_bucket_addition", "income_tax_addback", "muni_interest_other_states",
                    "adj_additions_total"], "outputs": ["13"], "sort_order": 3,
         "description": ("Line 9 is ONE dollar box carrying two sub-items (disposed-asset true-up + the residual "
                         "conformity bucket). Modifications are allocated among owners in proportion to ownership, "
                         "then FILTERED BY OWNER TYPE - each owner may only claim the modifications allowed on the "
                         "owner's own Virginia return.")},
        {"rule_id": f"{prefix}-SUB", "title": "Line 18 - Total subtractions. Add Lines 14 through 17.", "rule_type": "calculation",
         "formula": "L18 = L14 + L15 + L16 + L17",
         "inputs": ["conformity_depreciation_subtraction", "conformity_disposed_asset_subtraction",
                    "conformity_bucket_subtraction", "us_obligations_income", "adj_subtractions_total"],
         "outputs": ["18"], "sort_order": 4,
         "description": "Lines 14/15 are the exact mirrors of Lines 8/9 in the subtraction direction."},
        {"rule_id": f"{prefix}-CONFORM", "title": "Conformity routing: Lines 8/14, 9(1)/15(1), 9(2)/15(2)", "rule_type": "routing",
         "formula": ("bonus depreciation recompute -> Lines 8 / 14 (scoped 'any taxable year from 2001 through 2025') ; "
                     "disposed bonus asset true-up -> Lines 9(1) / 15(1) (federal basis minus Virginia basis) ; "
                     "EVERY OTHER conformity item in the 'Conformity Update for 2025' list -> Lines 9(2) / 15(2), "
                     "a RESIDUAL BUCKET wider than H.R.1: 168(n), 174A, 179 expensing limits, AHYDO, COD income, "
                     "the 2008/09 five-year NOL carryback, CARES-Act items, COVID small-business expenses. "
                     "No Schedule 502ADJ code covers it; no DOR worksheet exists - enclose a schedule."),
         "inputs": ["conformity_bucket_addition", "conformity_bucket_subtraction", "has_168n_or_174a_or_179_excess"],
         "outputs": ["8", "9", "14", "15"], "sort_order": 5,
         "description": ("W2 / U1, as NARROWED by verification correction C1. The word 'OTHER' in Line 9(2) is the "
                         "mechanism that excludes bonus depreciation - Lines 8 and 9(1) already carry it by name. "
                         "Do NOT call this an 'H.R.1 line'. Every return with a non-zero bucket amount gets a "
                         "requires_human_review flag. The corporate Form 500 book routes identically at Schedule "
                         "500ADJ Section A Line 2 - this is a DOR-wide pattern, not a one-off reading.")},
        {"rule_id": f"{prefix}-179", "title": "IRC 179: Virginia publishes NO dollar figure", "rule_type": "validation",
         "formula": ("VA_179_PUBLISHED[2025] = None  (NOTHING IS SEEDED) ; "
                     "derived-only reference = 1,250,000 limit / 3,130,000 phase-out / 31,300 SUV cap "
                     "[Rev. Proc. 2024-40 s.3.25 - NOT a Virginia source] ; "
                     "federal OBBBA 2,500,000 / 4,000,000 -> NEVER USE FOR VIRGINIA ; "
                     "if sec179_claimed_federal > derived limit -> requires_human_review diagnostic"),
         "inputs": ["sec179_claimed_federal"], "outputs": [], "sort_order": 6,
         "description": ("W3 / U2. Confirmed absent by exhaustion from THREE Virginia instruction books, TB 26-1 "
                         "and the 2026 Legislative Summary. The Virginia amount is recovered through a TIMING "
                         "mechanism (fixed-date conformity addition now, subtraction later), not a permanent "
                         "disallowance. Encode the ABSENCE plus a diagnostic - never a Virginia-labelled constant.")},
        {"rule_id": f"{prefix}-502AB", "title": "Schedule 502A Section B - apportionment percentage (Line 7)", "rule_type": "calculation",
         "formula": ("if wholly_within_virginia: L4/L5 blank, L6 = L1, L7 = 100% (Schedule 502A skipped entirely) ; "
                     "else if method box in 1..8: L7 = Schedule 502A Section B Line 1 (single factor, direct-entry) ; "
                     "else box 9: 2(a)=property, 2(b)=payroll, 2(c)=sales, 2(d)=2(c)x2, 2(e)=2(a)+2(b)+2(d), "
                     "2(f)=2(e) / (sum of the WEIGHTS of the factors that exist: property 1 + payroll 1 + sales 2) ; "
                     "property numerator/denominator = begin/end average at ORIGINAL COST + 8 x annual rent"),
         "inputs": ["wholly_within_virginia", "apportionment_method_box", "single_factor_percentage",
                    "property_factor_va_begin", "property_factor_va_end", "property_factor_ew_begin",
                    "property_factor_ew_end", "property_rent_va", "property_rent_ew", "payroll_factor_va",
                    "payroll_factor_ew", "sales_factor_va", "sales_factor_ew"],
         "outputs": ["7", "502A-B2a", "502A-B2b", "502A-B2c", "502A-B2d", "502A-B2e", "502A-B2f"], "sort_order": 7,
         "description": ("The PTE apportionment rule does NOT differ from the corporate rule - Sections A and B are "
                         "the same nine method boxes and the same divide-by-four computation. Virginia is NOT a "
                         "single sales factor state for PTEs. Non-TPP sales are COST OF PERFORMANCE, not market; "
                         "market sourcing exists only for the two VEDP carve-outs and debt buyers. No throwback or "
                         "throwout rule exists. DIVISOR NOTE: the face's '4 reduced by the number of factors having "
                         "no denominator' and the instruction's 'the number of existing factors' agree only when "
                         "sales is counted at its DOUBLE weight - hence the weight-sum divisor.")},
        {"rule_id": f"{prefix}-502AC", "title": "Schedule 502A Section C - allocable and apportionable income (Lines 4/5/6)", "rule_type": "calculation",
         "formula": ("C1 = Form 502 Line 1 ; "
                     "if commercial_domicile_in_va: C2 = dividends_received -> Line 4 ; C3(e) = 0 -> Line 5 ; "
                     "C4 = C1 - C2 -> Line 6 ; "
                     "else: C3(c) = dividends_received + nonapport_investment_income ; "
                     "C3(e) = C3(c) - nonapport_investment_loss -> Line 5 ; C4 = C1 - C3(e) -> Line 6"),
         "inputs": ["commercial_domicile_in_va", "dividends_received", "nonapport_investment_income",
                    "nonapport_investment_loss"],
         "outputs": ["4", "5", "6", "502A-C1", "502A-C2", "502A-C3c", "502A-C3e", "502A-C4"], "sort_order": 8,
         "description": ("C5: Schedule 500A has NO Section C and applies the percentage on the schedule itself. "
                         "Schedule 502A Section C stops at Lines 1-4 and pushes three figures to Form 502 Lines "
                         "4/5/6 - there is NO percentage-application line on Schedule 502A. A loader that clones "
                         "500A Section B Line 3 invents lines that do not exist. Lines 3(b)/3(d) are Allied-Signal "
                         "relief lines carrying a clear-and-cogent-evidence burden and a one-way ratchet -> R5.")},
        {"rule_id": f"{prefix}-CRED", "title": "Credit totals (Lines 19/20) and the two allocation classes", "rule_type": "calculation",
         "formula": (f"{adj_schedule} Section C Part II Line 1 = Add Part I Lines 1-8, 12-15, 17, 21, 23, 25-27 "
                     "(ENUMERATED - the nine Reserved slots 9,10,11,16,18,19,20,22,24 are skipped) -> Line 19 ; "
                     "Part IV Line 1 = Add Part III Lines 1, 7, 9" +
                     (", and 10 -> Line 20" if adj_schedule.endswith("PTET ADJ") else " -> Line 20") + " ; "
                     "allocation: slots {5,12,13,14,27} may be allocated pro rata OR as the owners mutually agree; "
                     "all other credits are strictly pro rata"),
         "inputs": ["nonrefundable_credits_total", "refundable_credits_total"],
         "outputs": ["19", "20", "ADJ-C-II-1"], "sort_order": 9,
         "description": ("'Pass-through entities do not use or compute credit carryovers.' Where a credit is "
                         "limited, 'the limitation applies to the TOTAL credit of the PTE (the aggregate of the "
                         "owners' shares), not to each owner's share separately.' Credit AMOUNTS are direct-entry; "
                         "the engine computes the allocation arithmetic and the enumerated totals (W8). Form TCA "
                         "and Schedule 500AB are deferred (R9, R7).")},
        {"rule_id": f"{prefix}-VK1", "title": "Schedule VK-1 fan-out and the cross-form assertion set", "rule_type": "calculation",
         "formula": ("for n in {1,2,3,4,5,6,8,9,10,11,13,18}: sum(VK-1 Ln over all owners) = Form Ln ; "
                     "VK-1 L7 = Form L7 for EVERY owner (never summed) ; "
                     "sum(VK-1 Le) = Form Line c ; sum(VK-1 Ld) = 100.00% ; "
                     "VK-1 carries four inline coded rows 12a-12d (L13 = L8..L11 + 12a-12d) and 17a-17d "
                     "(L18 = L14..L16 + 17a-17d), overflowing to Schedule SVK-1"),
         "inputs": ["owner_roster"], "outputs": ["c", "VK1-d", "VK1-e", "VK1-7", "VK1-PIII-10"], "sort_order": 10,
         "description": ("Grantor trusts: enter RES if the owner will file Form 760/760PY, NON if Form 763, TE "
                         "otherwise. 'The PTET credit can only be claimed by direct owners... A PTET credit that is "
                         "allocated to an estate or trust cannot subsequently be allocated to the beneficiaries.' "
                         "Fiscal-year rule: calendar-year owners of a fiscal-year PTE report in the year the PTE's "
                         "fiscal year ENDS.")},
        {"rule_id": f"{prefix}-DUE", "title": "Due dates - TWO CLOCKS, both true at once", "rule_type": "validation",
         "formula": ("Form 502 / Form 502PTET: the 15th day of the 4th month after year end (April 15 for "
                     "calendar filers) - Va. Code s.58.1-392 A ; "
                     "automatic extension = 6 months, OR 30 days after the federal extended due date, WHICHEVER IS "
                     "LATER ; THE PAYMENT DATE NEVER EXTENDS (withholding or PTET) ; "
                     "Form 760 / Form 760PY / Form 763 / Form 770: MAY 1 ; "
                     "weekend/holiday rollover to the next succeeding business day"),
         "inputs": ["fiscal_or_short_year"], "outputs": [], "sort_order": 11,
         "description": ("W10. A single 'Virginia due date' constant is wrong on one side or the other. 'May 1' "
                         "appears ZERO times in the 29-page Form 502 book and ZERO times in the 14-page PTET "
                         "package. Confirmed three ways that the payment date never extends, including "
                         "Va. Code s.58.1-486.2 D.2.")},
        {"rule_id": f"{prefix}-GATES", "title": "Filing-mode gates and 'rule says no' determinations", "rule_type": "routing",
         "formula": ("single-member LLC disregarded federally -> NOT required to file Form 502 ; "
                     "investment-only PTE (no employees, no real or tangible property) -> NOT required to file ; "
                     "NO consolidated or multilevel PTE returns - every PTE files its own ; "
                     "Form 502 and Form 502PTET are MUTUALLY EXCLUSIVE (502PTET is filed INSTEAD OF 502); a second "
                     "return for the year must be marked amended with Reason Code 05 ; "
                     "an electing PTET entity may NOT file Form 765"),
         "inputs": ["is_single_member_disregarded_llc", "is_investment_only_pte"], "outputs": [], "sort_order": 12,
         "description": ("These are affirmative rules, not gaps. The single-member-LLC rule is the OPPOSITE of "
                         "Tennessee's Schedule J2 trap - do not port that pattern here.")},
    ]


def _page1_rule_links(prefix: str) -> list[tuple[str, str, str, str]]:
    """Authority links for the shared Page-1 rule block. Every rule gets >= 1."""
    return [
        (f"{prefix}-MODULE", "VA_2025_FORM_502_INSTR", "primary", "the six module branch points, verbatim code tables"),
        (f"{prefix}-MODULE", "VA_2025_FORM_502", "secondary", "Entity Type field on the form face"),
        (f"{prefix}-L1", "VA_2025_FORM_502_INSTR", "primary", "the printed 12-line Line 1 worksheet and the DOR Caution"),
        (f"{prefix}-L1", "VA_2025_FORM_502", "secondary", "Line 1 face label 'Total taxable income amounts'"),
        (f"{prefix}-ADD", "VA_2025_FORM_502", "primary", "Line 13 'Add Lines 8 through 12'"),
        (f"{prefix}-SUB", "VA_2025_FORM_502", "primary", "Line 18 'Add Lines 14 through 17'"),
        (f"{prefix}-CONFORM", "VA_2025_FORM_502_INSTR", "primary", "Conformity Update for 2025 + Lines 9(2)/15(2) sub-items"),
        (f"{prefix}-CONFORM", "VA_TB_26_1", "secondary", "the fixed date conformity addition/subtraction mechanic"),
        (f"{prefix}-CONFORM", "VA_CODE_58_1_301", "secondary", "the 13 statutory exceptions incl. 168(n), 174A, 179"),
        (f"{prefix}-179", "RP_2024_40_VA_179_DERIVED_ONLY", "interpretive", "DERIVED figures only - Virginia publishes none"),
        (f"{prefix}-179", "VA_TB_26_1", "primary", "'as if the 2025 H.R. 1 changes had not been enacted'"),
        (f"{prefix}-502AB", "VA_2025_SCH_502A", "primary", "Section B Line 2(a)-(f) verbatim"),
        (f"{prefix}-502AB", "VA_CODE_58_1_408", "primary", "the statutory divide-by-four formula"),
        (f"{prefix}-502AC", "VA_2025_SCH_502A", "primary", "Section C Lines 1-4 verbatim"),
        (f"{prefix}-CRED", "VA_2025_SCH_502ADJ", "primary", "the enumerated Part II / Part IV totals"),
        (f"{prefix}-CRED", "VA_2025_FORM_502_INSTR", "secondary", "the two credit allocation classes; no PTE carryovers"),
        (f"{prefix}-VK1", "VA_2025_SCH_VK1", "primary", "VK-1 mirrors Form 502 except Line 7"),
        (f"{prefix}-DUE", "VA_CODE_58_1_392", "primary", "s.58.1-392 A - the fifteenth day of the fourth month"),
        (f"{prefix}-DUE", "VA_CODE_58_1_486_2", "secondary", "s.58.1-486.2 D.2 - extension does not extend payment"),
        (f"{prefix}-GATES", "VA_2025_FORM_502_INSTR", "primary", "single-member LLC / investment PTE / no consolidated returns"),
    ]


def _page1_diagnostics(prefix: str) -> list[dict]:
    """Diagnostics attached to the shared Page-1 block, instantiated per form."""
    return [
        {"diagnostic_id": f"{prefix}_W2_CONFORMITY_BUCKET", "severity": "warning",
         "title": "Conformity bucket (Lines 9(2)/15(2)) used - requires human review",
         "condition": "conformity_bucket_addition != 0 or conformity_bucket_subtraction != 0",
         "message": ("This amount is routed to Line 9(2) (addition) or Line 15(2) (subtraction) - the residual "
                     "conformity bucket for items in the 'Conformity Update for 2025' list other than bonus "
                     "depreciation. The bucket is WIDER than the 2025 H.R. 1 items: it also carries applicable "
                     "high yield discount obligations, cancellation of debt income, the 2008/2009 five-year NOL "
                     "carryback and the CARES Act items. Virginia publishes NO worksheet - enclose a schedule and "
                     "explanation with the return. Verify the routing before filing."),
         "notes": "W2 / U1, as narrowed by verification correction C1. The Department never says 'H.R.1 goes on "
                  "Line 9' in those words, and its promised web guidance page does not exist."},
        {"diagnostic_id": f"{prefix}_W3_NO_VA_179_FIGURE", "severity": "warning",
         "title": "Virginia publishes no IRC 179 dollar limit - figure is DERIVED",
         "condition": "sec179_claimed_federal > 0",
         "message": ("Virginia deconforms from the 2025 H.R. 1 increases to the IRC Section 179 expensing limits "
                     "but has published NO dollar limit and NO phase-out threshold of its own. The comparison "
                     "figures used here ($1,250,000 limit / $3,130,000 phase-out / $31,300 SUV cap) are DERIVED "
                     "from Rev. Proc. 2024-40 section 3.25 by applying Tax Bulletin 26-1's instruction to compute "
                     "'as if the 2025 H.R. 1 changes had not been enacted'. They are not Virginia numbers. Do NOT "
                     "use the federal $2,500,000 / $4,000,000 amounts for Virginia. Verify before filing."),
         "notes": "W3 / U2. Nothing Virginia-labelled is seeded; VA_179_PUBLISHED[2025] is None by design."},
        {"diagnostic_id": f"{prefix}_R2_VA_DEPRECIATION_BOOK", "severity": "error",
         "title": "Virginia depreciation shadow book not maintained - prepare the adjustment manually",
         "condition": "has_federal_bonus_depreciation or has_168n_or_174a_or_179_excess",
         "message": ("Virginia requires depreciation, amortization and carryforwards to be recomputed as if bonus "
                     "depreciation and the 2025 H.R. 1 expensing provisions had not been enacted, on separate "
                     "Virginia records (Tax Bulletin 26-1). This product does not maintain the per-asset Virginia "
                     "basis book. Compute the Virginia adjustment manually and enter it on Line 8 or Line 9 "
                     "(addition) or Line 14 or Line 15 (subtraction), and enclose a schedule and explanation."),
         "notes": "R2 / W5. The Virginia-basis engine is v1.1. Line 9(1) is literally 'the difference in the "
                  "federal and Virginia basis of the asset when sold'."},
        {"diagnostic_id": f"{prefix}_R3_174A_CATCHUP", "severity": "error",
         "title": "IRC 174A retroactive/catch-up deduction - no Virginia counterpart",
         "condition": "has_174a_catchup",
         "message": ("Virginia deconforms from the retroactive and catch-up provisions of IRC Section 174A. There "
                     "is no Virginia counterpart to the federal catch-up deduction; a Virginia conformity addition "
                     "is required. Prepare manually."),
         "notes": "R3. The nastiest piece of the Virginia depreciation layer - federal catch-up deductions have no "
                  "Virginia analogue at all."},
        {"diagnostic_id": f"{prefix}_L1_CAUTION_NO_K_SUM", "severity": "warning",
         "title": "Line 1 must be built, not imported from Schedule K",
         "condition": "line 1 worksheet completed",
         "message": ("The Schedule K of federal Forms 1065 and 1120-S does not include a total taxable income "
                     "amount, and the correct amount for Line 1 is not necessarily the sum of all entries in the "
                     "'Income' section. Schedule K may have entries that overlap for a category of income (for "
                     "instance a yearly amount and an amount through a certain date because of a midyear federal "
                     "law change). For each category, include only the YEARLY total; do not omit, duplicate, or "
                     "count any amount twice."),
         "notes": "W9. Verbatim DOR Caution surfaced as help copy."},
        {"diagnostic_id": f"{prefix}_L1_NOT_REDUCED_BY_L2", "severity": "info",
         "title": "Line 2 deductions do NOT reduce Line 1",
         "condition": "total_deductions != 0",
         "message": ("Line 1 is income only. Line 2 (deductions) and Line 3 (tax-exempt interest) are "
                     "informational carriers to Schedule VK-1 for each owner's own return; they do not reduce Line "
                     "1. Line 1 - not Line 1 minus Line 2 - is what flows to Schedule 502A Section C Line 1 and "
                     "drives apportionment. Note that the Form 502PTET base is DIFFERENT: deductions ARE included "
                     "there, with Section 179 and charitable contributions re-limited at the C-corporation level."),
         "notes": "The clone trap between the two forms."},
        {"diagnostic_id": f"{prefix}_L10_NOT_ADJ_C_I_1", "severity": "info",
         "title": "Line 10 is not the same amount as Schedule ADJ Section C Part I Line 1",
         "condition": "income_tax_addback != 0",
         "message": ("Line 10 covers net income taxes AND other taxes - including franchise and excise taxes - "
                     "that are based on, measured by, or computed with reference to net income, imposed by any "
                     "taxing jurisdiction, to the extent deducted federally. The Department states this item 'may "
                     "be related to the income tax paid on Schedule 502ADJ, Section C, Part I, Line 1, but is "
                     "defined differently and is not necessarily the same amount.' Do not wire the two together."),
         "notes": "The DOR says so explicitly; a natural but wrong optimisation."},
        {"diagnostic_id": f"{prefix}_MOD_FILTER_BY_OWNER", "severity": "info",
         "title": "Modifications are allocated, then filtered by owner type",
         "condition": "any Virginia modification present",
         "message": ("Virginia modifications are allocated among owners in proportion to ownership or as provided "
                     "in the entity agreement, but 'each owner may only claim the modifications allowed on the "
                     "owner's Virginia income tax return' - an individual owner reports only modifications "
                     "applicable to individual income tax and a corporate owner only those applicable to corporate "
                     "income tax. The PTE-level total and the sum of the VK-1s agree in AMOUNT but can diverge in "
                     "USABILITY."),
         "notes": "Stated verbatim twice in the instructions."},
        {"diagnostic_id": f"{prefix}_OWNER_CODE_TRANSLATION", "severity": "info",
         "title": "Five modification codes translate to DIFFERENT codes on the owner's return",
         "condition": "adj code 22, 43, 48, 56 or 99 (bank franchise) present",
         "message": ("Subtraction Code 43 becomes owner deduction Code 107; Code 48 becomes Code 108; Code 56 "
                     "(business interest) becomes Code 116; addition Code 22 becomes a negative deduction; and the "
                     "bank-franchise Code 99 items become owner deduction Code 112 on Schedule ADJ Line 8a. A spec "
                     "that treats VK-1 subtraction codes as directly consumable by the individual module will be "
                     "wrong on all five."),
         "notes": "One of the easiest cross-module errors to ship."},
        {"diagnostic_id": f"{prefix}_CODE22_MULTIYEAR", "severity": "warning",
         "title": "Business interest addition (Code 22) requires a multi-year Virginia history",
         "condition": "adj addition code 22 or subtraction code 56 present",
         "message": ("For TY2025 the Virginia business interest deduction is 20% of federally disallowed business "
                     "interest (it was 50% in TY2024). If a Virginia Business Interest Deduction was claimed in "
                     "prior years and the federal carryover is now utilised, an addition equal to the prior "
                     "Virginia deduction is required - applied IN THE SAME PROPORTION as the federal carryover "
                     "actually used. This needs a Virginia business-interest-deduction history per entity, tracked "
                     "separately from the federal Section 163(j) carryforward. Enclose federal Form 8990."),
         "notes": "A mid-season change enacted 2026-02-20 and retroactive to TY2025."},
        {"diagnostic_id": f"{prefix}_R4_APPORT_METHOD_BOX", "severity": "error",
         "title": "Non-default apportionment method (Schedule 502A Section A boxes 1-8) - prepare manually",
         "condition": "apportionment_method_box in 1..8",
         "message": ("This product computes only the default multi-factor formula with double-weighted sales (box "
                     "9). Motor carrier, financial corporation, construction completed-contract, railway, retail, "
                     "debt buyer, manufacturer's modified method and enterprise data center apportionment are not "
                     "computed - enter the single-factor percentage on Schedule 502A Section B Line 1 directly. "
                     "NOTE for the manufacturer's modified method: it carries a 3-year lock and annual wage and "
                     "employment certification, and if the 90% base-year employment level is not maintained the "
                     "RECAPTURE FALLS ON THE OWNERS, not the entity - the PTE must provide owners with corrected "
                     "income amounts and the owners pay the difference plus interest."),
         "notes": "R4. The owner-level recapture is a genuine PTE-vs-corporate divergence in consequence."},
        {"diagnostic_id": f"{prefix}_R5_ALLIED_SIGNAL", "severity": "error",
         "title": "Nonapportionable investment function income/loss (502A C 3(b)/3(d)) - prepare manually",
         "condition": "nonapport_investment_income != 0 or nonapport_investment_loss != 0",
         "message": ("Excluding nonapportionable investment function income requires proof BY CLEAR AND COGENT "
                     "EVIDENCE that the investment was completely separate from operations and located outside "
                     "Virginia, an enclosed statement of the nature and basis of the adjustment, and consistent "
                     "treatment in other states (Tax Bulletin 93-4 / PD 93-93B). A subtraction also creates a "
                     "PERMANENT obligation to add back later losses generated by the same assets. Prepare "
                     "manually."),
         "notes": "R5. The one-way ratchet is a multi-year tracking obligation."},
        {"diagnostic_id": f"{prefix}_R7_SCHEDULE_500AB", "severity": "error",
         "title": "Schedule 500AB intangible/interest add-back - prepare manually",
         "condition": "adj addition code 15 or 16, or subtraction code 22, non-zero",
         "message": ("Royalty and interest add-backs for intangible expenses (Codes 15 and 16) and the "
                     "related-member offset (subtraction Code 22) require an enclosed Schedule 500AB, which is not "
                     "prepared by this product."),
         "notes": "R7."},
        {"diagnostic_id": f"{prefix}_R9_FORM_TCA", "severity": "error",
         "title": "Form TCA credit allocation - filed outside the return",
         "condition": "any credit requiring certification is present",
         "message": ("Certain Virginia credits must be allocated to owners on Form TCA (previously named Form "
                     "PTE), filed with the Tax Credit Unit within 30 days of certification of the credit and at "
                     "least 90 days before the participants file their income tax returns. Form TCA is not "
                     "prepared by this product. Form TCA cannot be used to allocate PTET credits - the PTET credit "
                     "is allocated on Schedule PTET ADJ Section C Part III Line 10 and flows to Schedule VK-1 Part "
                     "III Line 10. If certification arrives late, either pay at least 90% of the withholding and "
                     "file on extension, or file on time without the credit and amend."),
         "notes": "R9. Correction C6 - the TCA/PTET tension is reconciled by the DOR itself, not a contradiction."},
        {"diagnostic_id": f"{prefix}_R12_WAIVER_REQUESTS", "severity": "warning",
         "title": "Waiver requests are made outside the return",
         "condition": "exemption code 06 entered, or an e-filing waiver is indicated",
         "message": ("The undue-hardship waiver of the WITHHOLDING obligation is requested by letter to the Tax "
                     "Commissioner describing the facts and circumstances; note that the withholding tax liability "
                     "itself is not part of the cost of compliance and inability to pay is not a basis for "
                     "exemption. The E-FILING waiver is requested on the Department's Electronic Filing Waiver "
                     "Request form. Neither is prepared by this product. Virginia Code Section 58.1-392 E "
                     "expressly provides that waivers of the pass-through entity electronic filing requirement "
                     "SHALL be granted where the Tax Commissioner finds an unreasonable burden - so a waiver is "
                     "legally available even where Departmental guidance states it will not be granted."),
         "notes": "R12, stated POSITIVELY per verification Sec.16.5 and W7. Never assert a waiver cannot exist."},
        {"diagnostic_id": f"{prefix}_R13_BANK_FRANCHISE", "severity": "error",
         "title": "Bank Franchise Tax S corporation - Code 99 amounts prepared manually",
         "condition": "subject_to_bank_franchise_tax and entity_module == '1120S'",
         "message": ("An S corporation subject to the Virginia Bank Franchise Tax must report its income and gain "
                     "and its losses, deductions and distributions as 'Other' modifications (Code 99) on the "
                     "adjustment schedule, to be claimed by shareholders as a negative deduction under Code 112 on "
                     "Line 8a of the shareholder's Schedule ADJ, using the worksheet in the individual income tax "
                     "instructions. Prepare the Code 99 amounts manually."),
         "notes": "R13 - branch 6, an S-corp-only consequence. There is no partnership analogue."},
        {"diagnostic_id": f"{prefix}_R14_ALT_APPORTIONMENT", "severity": "error",
         "title": "Alternative method of allocation and apportionment requires advance permission",
         "condition": "user indicates an alternative apportionment method",
         "message": ("Permission to use an alternative method of allocation and apportionment must be obtained "
                     "from the Department in advance and 'will be granted only in extraordinary circumstances' "
                     "(Va. Code Section 58.1-421; 23 VAC 10-120-130). Not prepared by this product."),
         "notes": "R14."},
        {"diagnostic_id": f"{prefix}_R15_FORM_500HS", "severity": "error",
         "title": "Noncorporate home service contract provider - Form 500HS required",
         "condition": "entity indicates home-service-contract status",
         "message": ("This PTE must file Form 500 and Form 500HS in addition to or instead of the standard "
                     "pass-through entity return. Neither is prepared by this product."),
         "notes": "R15."},
        {"diagnostic_id": f"{prefix}_W10_TWO_DUE_CLOCKS", "severity": "info",
         "title": "Virginia has TWO due-date clocks - do not conflate them",
         "condition": "due date computed",
         "message": ("Form 502 and Form 502PTET are due on the 15th day of the 4th month after the close of the "
                     "taxable year (April 15 for calendar-year filers) under Virginia Code Section 58.1-392 A. "
                     "Virginia's May 1 due date applies to Form 760 / 760PY / 763 and Form 770 ONLY. Both are true "
                     "at once. The automatic extension is 6 months, or 30 days after the federal extended due "
                     "date, whichever is later - and it NEVER extends the payment date for withholding or PTET."),
         "notes": "W10, settled by s.58.1-392 A. A single Virginia due-date constant is wrong on one side."},
        {"diagnostic_id": f"{prefix}_NO_FILING_REQUIRED", "severity": "info",
         "title": "Single-member LLC or investment-only PTE - no Form 502 required",
         "condition": "is_single_member_disregarded_llc or is_investment_only_pte",
         "message": ("A single-member LLC disregarded for federal income tax purposes is treated the same way for "
                     "Virginia purposes and 'is not required to file Form 502'. Pass-through entities established "
                     "solely to invest in intangible personal property, with no employees and no real or tangible "
                     "property, are not carrying on a trade or business and are likewise not required to file. "
                     "There are also no consolidated or multilevel Virginia PTE returns - every PTE files its own."),
         "notes": "Affirmative rules, not gaps. The OPPOSITE of Tennessee's Schedule J2 trap."},
    ]


# ===========================================================================
# FORM VA_502 - Page 2 is a SECOND return: the nonresident withholding return
# ===========================================================================

VA502_FACTS: list[dict] = _page1_facts() + [
    {"fact_key": "nonresident_va_source_income", "label": "P2 L1 - nonresident owners' aggregate Virginia-source taxable income",
     "data_type": "decimal", "required": False, "sort_order": 100,
     "notes": "Per owner in the roster; the 5% and the zero floor are applied PER OWNER, then summed."},
    {"fact_key": "withholding_credits_passed_through", "label": "Credits passed through to nonresident owners (applied against withholding)",
     "data_type": "decimal", "required": False, "sort_order": 101,
     "notes": "'may not be reduced to less than zero' - the floor is PER OWNER."},
    {"fact_key": "owner_days_nonresident", "label": "Days of residence outside Virginia (part-year owners)",
     "data_type": "integer", "required": False, "sort_order": 102,
     "notes": "Day-count proration of the allocated income."},
    {"fact_key": "withholding_paid_by_entity", "label": "P2 L2 - withholding tax paid (ENTITY'S OWN PAYMENTS ONLY)",
     "data_type": "decimal", "required": False, "sort_order": 103,
     "notes": "Do NOT include amounts withheld by another PTE in which this PTE is a nonresident owner."},
    {"fact_key": "prior_year_wh_liability", "label": "Prior-year withholding tax liability (safe harbor)",
     "data_type": "decimal", "required": False, "sort_order": 104},
    {"fact_key": "prior_year_full_12_months", "label": "Prior-year return covered a full 12-month period",
     "data_type": "boolean", "required": False, "sort_order": 105},
    {"fact_key": "prior_year_had_wh_liability", "label": "Prior-year return reflected a withholding tax liability",
     "data_type": "boolean", "required": False, "sort_order": 106},
    {"fact_key": "days_late", "label": "Days from the original due date through the filing date",
     "data_type": "integer", "required": False, "sort_order": 107,
     "notes": "Extension Penalty Worksheet line C counts in 30-day increments, ROUNDED UP."},
    {"fact_key": "filed_more_than_6_months_late", "label": "Form 502 filed more than 6 months after the original due date",
     "data_type": "boolean", "required": False, "sort_order": 108},
    {"fact_key": "filed_more_than_30d_after_fed_ext", "label": "Filed more than 30 days after the federal extended due date",
     "data_type": "boolean", "required": False, "sort_order": 109},
    {"fact_key": "wh_interest_charge", "label": "P2 L7 - interest on withholding tax (IRC 6621 + 2%)",
     "data_type": "decimal", "required": False, "sort_order": 110},
    {"fact_key": "overpayment_credited_next_year", "label": "P2 L11 - withholding overpayment credited to 2026",
     "data_type": "decimal", "required": False, "sort_order": 111},
    {"fact_key": "overpayment_refunded", "label": "P2 L12 - withholding overpayment refunded",
     "data_type": "decimal", "required": False, "sort_order": 112,
     "notes": "'The total of Lines 11 and 12 cannot exceed the amount on Line 10.'"},
    {"fact_key": "motion_picture_credit_refund", "label": "P2 L17 - Motion Picture Production Tax Credit refunded directly to the PTE",
     "data_type": "decimal", "required": False, "sort_order": 113,
     "notes": "The only credit the PTE itself can monetise."},
    {"fact_key": "unified_nonresident_765_filed", "label": "Unified nonresident return (Form 765) filed",
     "data_type": "boolean", "required": False, "sort_order": 114, "notes": "Triggers R8; suppress withholding for owners flagged code 03."},
    {"fact_key": "has_nonresident_owner_pte", "label": "A nonresident owner is itself a pass-through entity",
     "data_type": "boolean", "required": False, "sort_order": 115, "notes": "Triggers R10 - the anti-cascade case."},
    {"fact_key": "owner_pte_notified_will_not_file", "label": "That owner PTE notified it will NOT file a Virginia return",
     "data_type": "boolean", "required": False, "sort_order": 116,
     "notes": "The ONLY circumstance in which withholding on an owner PTE is required."},
    {"fact_key": "has_502fed1_trigger", "label": "Partnership-level federal adjustment (Reason Code 02, or codes 23/58)",
     "data_type": "boolean", "required": False, "sort_order": 117, "notes": "Triggers R6 - 1065 module only."},
    {"fact_key": "has_efiling_waiver", "label": "PTE has been granted a waiver from the electronic filing mandate",
     "data_type": "boolean", "required": False, "sort_order": 118, "notes": "The only path on which VK-1 Consolidated exists (R16)."},
]

VA502_RULES: list[dict] = _page1_rules("R-VA", "Schedule 502ADJ") + [
    {"rule_id": "R-VA-WH-OWNER", "title": "P2 L1 - 5% withholding, per owner, floored at zero", "rule_type": "calculation",
     "formula": ("for each nonresident owner without an exemption code: "
                 "share = owner's Virginia-source taxable income share (INCLUDING additions and subtractions) ; "
                 "if part-year: share = share x (days of residence outside Virginia / 365) ; "
                 "tax = max(0, share x 5% - credits passed through to that owner) ; "
                 "P2 Line 1 = sum(tax) over owners. "
                 "Categorically out: publicly traded partnerships and DISREGARDED ENTITIES. "
                 "Owner exceptions 01-07 suppress withholding for that owner."),
     "inputs": ["owner_roster", "nonresident_va_source_income", "withholding_credits_passed_through",
                "owner_days_nonresident"], "outputs": ["P2-1", "c", "VK1-e"], "sort_order": 20,
     "description": ("W6 - computed, because it is the reason Form 502 exists and there is no manual fallback that "
                     "produces a filable return. THE ZERO FLOOR IS PER OWNER, applied before the entity total is "
                     "struck. Va. Code s.58.1-486.2 B.1 supplies the 5%. The tiered-PTE case is RED-deferred (R10).")},
    {"rule_id": "R-VA-WH-RECON", "title": "P2 Section 1 Lines 2-4 - withholding payment reconciliation", "rule_type": "calculation",
     "formula": ("L2 = the entity's OWN payments only ; "
                 "L3 = L2 - L1 if L2 > L1 (overpayment) ; L4 = L1 - L2 if L2 < L1 (tax due)"),
     "inputs": ["withholding_paid_by_entity"], "outputs": ["P2-2", "P2-3", "P2-4"], "sort_order": 21,
     "description": ("'Only amounts paid directly to the Department by the PTE filing Form 502 should be recorded "
                     "on Line 2.' Amounts withheld by ANOTHER PTE in which this PTE is a nonresident owner are "
                     "excluded - the generation-skipping bar, seen from the receiving side. If another PTE has "
                     "withheld erroneously, contact that PTE and request reimbursement.")},
    {"rule_id": "R-VA-WH-SAFE", "title": "Withholding safe harbor - lesser of 90% current / 100% prior", "rule_type": "validation",
     "formula": ("required payment = lesser of (0.90 x current-year withholding liability) and "
                 "(1.00 x prior-year withholding liability), PROVIDED the prior-year return covered a 12-month "
                 "period AND reflected a withholding tax liability; otherwise only the 90% leg applies"),
     "inputs": ["prior_year_wh_liability", "prior_year_full_12_months", "prior_year_had_wh_liability"],
     "outputs": [], "sort_order": 22,
     "description": "Both provisos must hold before the prior-year leg is available."},
    {"rule_id": "R-VA-WH-PEN", "title": "P2 Section 2/3 - extension penalty, late payment, late filing", "rule_type": "calculation",
     "formula": ("extension penalty applies iff L4 > 10% of L1 (identically: less than 90% of L1 paid timely) - "
                 "ONE test, encode once ; worksheet: months = ceil(days_late / 30), pct = min(months x 2%, 12%), "
                 "L5 = L4 x pct ; "
                 "L6 = 30% of L4 if filed more than 6 months after the original due date ; "
                 "L5 and L6 are MUTUALLY EXCLUSIVE ; "
                 "L9 = $1,200 flat if filed more than 6 months late OR more than 30 days after the federal "
                 "extended due date ; L8 = (L5 or L6, whichever applies) + L7 ; L7 interest at IRC 6621 + 2%"),
     "inputs": ["days_late", "filed_more_than_6_months_late", "filed_more_than_30d_after_fed_ext", "wh_interest_charge"],
     "outputs": ["P2-5", "P2-6", "P2-7", "P2-8", "P2-9"], "sort_order": 23,
     "description": ("The face states the threshold as '90% of Line 1 not paid timely' and the instruction as "
                     "'balance due on Line 4 more than 10% of Line 1'. Same test from opposite sides - implement "
                     "one. 'The extension penalty does not apply in cases where the return is subject to the late "
                     "filing penalty.' Separately, the Department may assess a penalty of 6% of the Virginia "
                     "taxable income owners derive from the entity - NOT return-computable; informational only.")},
    {"rule_id": "R-VA-WH-L10", "title": "P2 Line 10 - the FOUR-BRANCH net overpayment conditional", "rule_type": "conditional",
     "formula": ("if L8 > L3 or L9 > L3: go to Line 13 (no Line 10 amount) ; "
                 "elif L6 > L9: L10 = L3 - L8 ; "
                 "elif L9 > L6: L10 = L3 - (L7 + L9) ; "
                 "else: L10 = L3 ; "
                 "and L11 + L12 <= L10"),
     "inputs": ["overpayment_credited_next_year", "overpayment_refunded"],
     "outputs": ["P2-10", "P2-11", "P2-12"], "sort_order": 24,
     "description": ("Transcribed exactly - this is a four-branch conditional, NOT a subtraction, and it is the "
                     "single most error-prone line on the form. Branch 1 is an EXIT to Line 13, not a zero. "
                     "Section 4 also states the governing principle: any overpayment on Line 3 must be offset "
                     "against the penalty and interest charges in Sections 2 and 3.")},
    {"rule_id": "R-VA-WH-SETTLE", "title": "P2 Sections 5/6 - Lines 13-16, 17, 20/21", "rule_type": "calculation",
     "formula": ("L13 = L4 + L5 if there is an amount due on L4; else if L3 > 0 and (L8 > L3 or L9 > L3): L13 = L5 - L3 ; "
                 "L14 = L7 ; L15 = GREATER of L6 or L9 ; L16 = L13 + L14 + L15 ; "
                 "L20 = L16 - L17 when L16 > L17 ; L21 = (L17 - L16) + L12 when L16 < L17"),
     "inputs": ["motion_picture_credit_refund", "wh_interest_charge"],
     "outputs": ["P2-13", "P2-14", "P2-15", "P2-16", "P2-17", "P2-20", "P2-21"], "sort_order": 25,
     "description": ("Lines 18 and 19 are printed 'Reserved for future use'. Line 17 is the Motion Picture "
                     "Production Tax Credit refunded directly to the PTE.")},
    {"rule_id": "R-VA-ADJ-D", "title": "Schedule 502ADJ Section D - amended-return withholding true-up", "rule_type": "calculation",
     "formula": ("D1 = amount paid with the original return + additional tax paid after it was filed ; "
                 "D2 = D1 + Form 502 Section 1 Line 2 ; D3 = overpayment on the original return or as previously "
                 "adjusted ; D4 = D2 - D3 ; "
                 "D5 = Form 502 Section 1 Line 1 - D4 when D4 is less (ADDITIONAL TAX DUE) ; "
                 "D6 = D4 - Form 502 Section 1 Line 1 when Line 1 is less (AMOUNT OVERPAID)"),
     "inputs": [], "outputs": ["ADJ-D1", "ADJ-D2", "ADJ-D3", "ADJ-D4", "ADJ-D5", "ADJ-D6"], "sort_order": 26,
     "description": ("U7: Line 5's label is TRUNCATED on the FINAL Rev. 07/26 form face - the trailing 'from "
                     "Section 1, Line 1 of Form 502. This is the Additional Tax Due' clause is absent where Line "
                     "6's symmetric clause is present. Treated as a form-face typographical defect; the arithmetic "
                     "is forced by Line 6's mirror. Amended-return doctrine: 'complete Form 502 using the "
                     "corrected figures, as if it were the original return' - Section D does the reconciliation.")},
    {"rule_id": "R-VA-502EZ", "title": "Form 502EZ eligibility CHECK (the form itself is deferred)", "rule_type": "validation",
     "formula": ("eligible iff ALL of: 100% of business in Virginia; 100% of income from Virginia sources; "
                 "commercial domicile in Virginia; not more than 10 owners; not required to file Form 500; not "
                 "filing Schedule 502A; not a noncorporate home service contract provider filing 500HS; passes no "
                 "Schedule CR credits; NO conformity modifications or adjustments to pass to owners; total taxable "
                 "income >= $0 and <= $40,000; total additions and subtractions < $1,000; not amending for a "
                 "partnership-level federal adjustment; not electing to pay at the entity level"),
     "inputs": ["owner_count_total", "wholly_within_virginia"], "outputs": [], "sort_order": 27,
     "description": ("R1. The conformity-modification exclusion is DECISIVE for TY2025 - any PTE with a bonus "
                     "depreciation or residual-bucket adjustment is out of 502EZ by definition. 502EZ is "
                     "eForms-only (browser), not MeF, so it is deferred either way; the check exists so the "
                     "product can tell a qualifying PTE that a free filing route exists.")},
]

VA502_RULE_LINKS: list[tuple[str, str, str, str]] = _page1_rule_links("R-VA") + [
    ("R-VA-WH-OWNER", "VA_CODE_58_1_486_2", "primary", "s.58.1-486.2 B.1 - five percent, verbatim"),
    ("R-VA-WH-OWNER", "VA_2025_FORM_502_INSTR", "primary", "exceptions, day-count proration, per-owner zero floor"),
    ("R-VA-WH-RECON", "VA_2025_FORM_502", "primary", "Page 2 Section 1 Lines 1-4 face labels"),
    ("R-VA-WH-RECON", "VA_2025_FORM_502W", "secondary", "the April 15 withholding payment date"),
    ("R-VA-WH-SAFE", "VA_2025_FORM_502_INSTR", "primary", "lesser of 90% current / 100% prior, with both provisos"),
    ("R-VA-WH-SAFE", "VA_CODE_58_1_486_2", "secondary", "the statutory 90%/100% test"),
    ("R-VA-WH-PEN", "VA_2025_FORM_502_INSTR", "primary", "Extension Penalty Worksheet p.14; the 10%/90% threshold"),
    ("R-VA-WH-PEN", "VA_2025_FORM_502", "primary", "Page 2 Lines 5-9 face labels incl. the $1,200 flat penalty"),
    ("R-VA-WH-L10", "VA_2025_FORM_502", "primary", "Line 10's four-branch conditional, verbatim"),
    ("R-VA-WH-SETTLE", "VA_2025_FORM_502", "primary", "Page 2 Lines 13-21 face labels"),
    ("R-VA-ADJ-D", "VA_2025_SCH_502ADJ", "primary", "Section D Lines 1-6; U7 truncation on Line 5"),
    ("R-VA-502EZ", "VA_2025_FORM_502_INSTR", "primary", "the 13-criterion 502EZ eligibility gate"),
]

VA502_LINES: list[dict] = _page1_lines("Schedule 502ADJ", "R-VA") + [
    {"line_number": "P2-1", "description": "Total withholding tax due for nonresident owners (5% per owner, floored at zero)",
     "line_type": "calculated", "source_rules": ["R-VA-WH-OWNER"], "sort_order": 100},
    {"line_number": "P2-2", "description": "Total withholding tax paid (Entity's own payments ONLY)",
     "line_type": "input", "source_facts": ["withholding_paid_by_entity"], "sort_order": 101},
    {"line_number": "P2-3", "description": "Overpayment. If Line 2 is greater than Line 1, subtract Line 1 from Line 2.",
     "line_type": "calculated", "source_rules": ["R-VA-WH-RECON"], "sort_order": 102},
    {"line_number": "P2-4", "description": "Withholding tax due. If Line 2 is less than Line 1, subtract Line 2 from Line 1.",
     "line_type": "calculated", "source_rules": ["R-VA-WH-RECON"], "sort_order": 103},
    {"line_number": "P2-5", "description": "Extension penalty (applies if less than 90% of Line 1 paid timely; 2% per 30-day month, cap 12%)",
     "line_type": "calculated", "source_rules": ["R-VA-WH-PEN"], "sort_order": 104},
    {"line_number": "P2-6", "description": "Late payment penalty on tax due - enter 30% of the amount on Line 4",
     "line_type": "calculated", "source_rules": ["R-VA-WH-PEN"], "sort_order": 105},
    {"line_number": "P2-7", "description": "Interest (IRC 6621 plus 2%)", "line_type": "input",
     "source_facts": ["wh_interest_charge"], "sort_order": 106},
    {"line_number": "P2-8", "description": "Penalty and interest charges due. Add Line 5 or Line 6 (whichever applies) to Line 7.",
     "line_type": "subtotal", "source_rules": ["R-VA-WH-PEN"], "sort_order": 107},
    {"line_number": "P2-9", "description": "Late filing penalty - $1,200 if filed more than 6 months late or 30 days after the federal extension",
     "line_type": "calculated", "source_rules": ["R-VA-WH-PEN"], "sort_order": 108},
    {"line_number": "P2-10", "description": "Net overpayment - FOUR-BRANCH conditional; branch 1 exits to Line 13",
     "line_type": "calculated", "source_rules": ["R-VA-WH-L10"], "sort_order": 109},
    {"line_number": "P2-11", "description": "Amount of withholding overpayment to be credited to 2026",
     "line_type": "input", "source_facts": ["overpayment_credited_next_year"], "sort_order": 110},
    {"line_number": "P2-12", "description": "Amount of withholding overpayment to be refunded (L11 + L12 cannot exceed L10)",
     "line_type": "input", "source_facts": ["overpayment_refunded"], "sort_order": 111},
    {"line_number": "P2-13", "description": "Balance of tax due plus extension penalty, if applicable",
     "line_type": "calculated", "source_rules": ["R-VA-WH-SETTLE"], "sort_order": 112},
    {"line_number": "P2-14", "description": "Interest charges on withholding tax from Line 7",
     "line_type": "calculated", "source_rules": ["R-VA-WH-SETTLE"], "sort_order": 113},
    {"line_number": "P2-15", "description": "Late filing penalty. Enter the GREATER of Line 6 or Line 9.",
     "line_type": "calculated", "source_rules": ["R-VA-WH-SETTLE"], "sort_order": 114},
    {"line_number": "P2-16", "description": "Total payment due. Add Line 13, Line 14, and Line 15.",
     "line_type": "subtotal", "source_rules": ["R-VA-WH-SETTLE"], "sort_order": 115},
    {"line_number": "P2-17", "description": "Motion Picture Production Tax Credit to be refunded directly to the PTE",
     "line_type": "input", "source_facts": ["motion_picture_credit_refund"], "sort_order": 116},
    {"line_number": "P2-18", "description": "Reserved for future use", "line_type": "informational", "sort_order": 117},
    {"line_number": "P2-19", "description": "Reserved for future use", "line_type": "informational", "sort_order": 118},
    {"line_number": "P2-20", "description": "Amount Due (Line 16 less Line 17 where Line 16 exceeds Line 17)",
     "line_type": "total", "source_rules": ["R-VA-WH-SETTLE"], "sort_order": 119},
    {"line_number": "P2-21", "description": "Amount of Refund (Line 17 less Line 16; add Line 12 if there is an amount on Line 12)",
     "line_type": "total", "source_rules": ["R-VA-WH-SETTLE"], "sort_order": 120},
    {"line_number": "ADJ-D1", "description": "502ADJ Section D Line 1 - amount paid with the original return plus additional tax paid",
     "line_type": "input", "sort_order": 130},
    {"line_number": "ADJ-D2", "description": "502ADJ Section D Line 2 - add Line 1 and Form 502 Section 1 Line 2",
     "line_type": "subtotal", "source_rules": ["R-VA-ADJ-D"], "sort_order": 131},
    {"line_number": "ADJ-D3", "description": "502ADJ Section D Line 3 - overpayment on the original return or as previously adjusted",
     "line_type": "input", "sort_order": 132},
    {"line_number": "ADJ-D4", "description": "502ADJ Section D Line 4 - subtract Line 3 from Line 2",
     "line_type": "calculated", "source_rules": ["R-VA-ADJ-D"], "sort_order": 133},
    {"line_number": "ADJ-D5", "description": "502ADJ Section D Line 5 - additional tax due (label TRUNCATED on the form face; U7)",
     "line_type": "calculated", "source_rules": ["R-VA-ADJ-D"], "sort_order": 134},
    {"line_number": "ADJ-D6", "description": "502ADJ Section D Line 6 - amount overpaid",
     "line_type": "calculated", "source_rules": ["R-VA-ADJ-D"], "sort_order": 135},
    {"line_number": "ADJ-C-IV-1", "description": "502ADJ Section C Part IV Line 1 - Add Part III, Lines 1, 7, and 9 (NO Line 10)",
     "line_type": "calculated", "source_rules": ["R-VA-CRED"], "sort_order": 136,
     "notes": "Schedule PTET ADJ adds Line 10 here; Schedule VK-1 Part IV always includes it on BOTH paths."},
]

VA502_DIAGNOSTICS: list[dict] = _page1_diagnostics("D_VA502") + [
    {"diagnostic_id": "D_VA502_R1_502EZ_AVAILABLE", "severity": "info",
     "title": "This PTE may qualify for the free Form 502EZ",
     "condition": "all 13 Form 502EZ eligibility criteria met",
     "message": ("This pass-through entity appears to meet all of the Form 502EZ criteria and may qualify to file "
                 "the free Form 502EZ through Virginia's eForms system. This product prepares the full Form 502, "
                 "which is also accepted. Note that a TY2025 PTE with ANY conformity modification is ineligible "
                 "for Form 502EZ by definition."),
     "notes": "R1 - INFO, not RED. 502EZ is eForms-only (browser), not an MeF form."},
    {"diagnostic_id": "D_VA502_R6_FORM_502FED1", "severity": "error",
     "title": "Partnership-level federal adjustment - Form 502FED-1 / 502FED-2 prepared manually",
     "condition": "has_502fed1_trigger and entity_module == '1065'",
     "message": ("Virginia requires partnership-level federal adjustments to be reported on Form 502FED-1 no later "
                 "than 90 days after the final determination date. The partnership may instead elect to pay the "
                 "resulting Virginia tax at the entity level by submitting Form 502FED-2 within 90 days, with the "
                 "payment due within 1 year of the final determination date. Neither form is prepared by this "
                 "product. Pair with Amended Reason Code 02 and Schedule 502ADJ codes 23 / 58. Separately, ANY "
                 "change in the federal return requires notifying the Department and issuing an amended Schedule "
                 "VK-1 to each owner within 1 year of the final determination date."),
     "notes": "R6 / W11 / U12 - the 1065 module ONLY; there is no S-corp counterpart."},
    {"diagnostic_id": "D_VA502_R8_FORM_765", "severity": "error",
     "title": "Form 765 unified nonresident return - prepared and filed separately",
     "condition": "unified_nonresident_765_filed",
     "message": ("Form 765 is a separate return prepared and filed independently of Form 502; it is not prepared "
                 "by this product. Form 765 may not be filed unless the entity has also filed its Form 502. "
                 "Enclose a completed Schedule 502A with Form 765. DO NOT submit Form 765 with Form 502 - mail it "
                 "to the address on Form 765. Withholding is suppressed for owners flagged with exemption code 03. "
                 "A qualified nonresident owner is an INDIVIDUAL, nonresident, DIRECT owner only. Partial "
                 "composites are permitted provided the PTE pays withholding for the owners not included. An "
                 "electing PTET entity may not file Form 765 at all."),
     "notes": "R8."},
    {"diagnostic_id": "D_VA502_R10_TIERED_PTE_WH", "severity": "error",
     "title": "Nonresident owner is itself a PTE - withholding is NOT generation-skipping",
     "condition": "has_nonresident_owner_pte",
     "message": ("As a general rule a PTE should NOT withhold tax on behalf of a nonresident owner that is itself "
                 "a pass-through entity. Withholding is required ONLY if that owner PTE has notified you that it "
                 "will not file a Virginia PTE return. If withholding is made in error the recipient PTE CANNOT "
                 "claim credit for it on its own Form 502 - Virginia PTE withholding is not 'generation skipping' "
                 "and does not pass through an intermediate PTE to owners more than one level away. The only "
                 "recovery is an amended Form 502 by the withholding PTE. This case is not computed by this "
                 "product - determine it manually."),
     "notes": "R10 / W6. The trapped-withholding consequence makes this a hard block, not a warning."},
    {"diagnostic_id": "D_VA502_R16_VK1_CONSOLIDATED", "severity": "error",
     "title": "Schedule VK-1 Consolidated - not produced by this product",
     "condition": "has_efiling_waiver and owner_count_total >= 10",
     "message": ("Paper filers with 10 or more owners must use the Schedule VK-1 Consolidated Excel template, "
                 "which is not produced by this product. The template is for PTEs that have been granted a waiver "
                 "from the electronic filing mandate. The PTE still sends each owner their own Schedule VK-1 and "
                 "sends the Department only the summary - and to avoid disclosing confidential taxpayer "
                 "information the PTE must NOT send the summary to its owners."),
     "notes": "R16 / U15. The instructions contradict themselves on when a Consolidated is required (p.19 reads "
              "universal, p.20 scopes it to waived paper filers). The specific governs. Do NOT build a rule "
              "requiring a Consolidated on every e-filed return."},
    {"diagnostic_id": "D_VA502_LINE_D_ALL_OR_NOTHING", "severity": "warning",
     "title": "Line d is an all-or-nothing entity exemption flag",
     "condition": "entity_withholding_exemption_code set and the PTE has both individual and non-individual owners",
     "message": ("PTEs that have both individual and corporate and/or other entity members may be exempt from "
                 "paying the withholding tax for the individual members but will still be required to pay it on "
                 "behalf of the corporate and/or other entity members. In that case the PTE should NOT indicate "
                 "that it is exempt on Line d. Record the partial exemption on each affected owner's Schedule VK-1 "
                 "Line f instead."),
     "notes": "A real validation rule. The entity codes (03, 04, 06, 07) are a SUBSET of the owner codes (01-07)."},
    {"diagnostic_id": "D_VA502_L2_ENTITY_PAYMENTS_ONLY", "severity": "warning",
     "title": "Page 2 Line 2 is the entity's own payments only",
     "condition": "withholding_paid_by_entity != 0",
     "message": ("Do not enter any amount that was withheld by another PTE in which this PTE is a nonresident "
                 "owner and was issued a Schedule VK-1 reflecting that withholding. Only amounts paid directly to "
                 "the Department by the PTE filing this Form 502 belong on Line 2. If another PTE has withheld "
                 "erroneously on this PTE, contact that PTE and request reimbursement."),
     "notes": "The generation-skipping bar seen from the receiving side."},
    {"diagnostic_id": "D_VA502_EXT_PEN_ONE_TEST", "severity": "info",
     "title": "Extension penalty threshold is one test stated two ways",
     "condition": "extension penalty evaluated",
     "message": ("The form face states the extension penalty applies if 90% of Line 1 is not paid timely; the "
                 "instruction states it may apply if the balance due on Line 4 is more than 10% of Line 1. These "
                 "are the same test from opposite sides and are implemented once. The extension penalty and the "
                 "late payment penalty on Line 6 are mutually exclusive - the extension penalty does not apply "
                 "where the return is subject to the late filing penalty."),
     "notes": "Encode once; do not implement both."},
    {"diagnostic_id": "D_VA502_WH_PAYMENT_NEVER_EXTENDS", "severity": "warning",
     "title": "The withholding payment date never extends",
     "condition": "extension used and withholding tax due",
     "message": ("Payment of the withholding tax is due by the ORIGINAL due date for filing Form 502 (April 15 for "
                 "a calendar-year return). The automatic 6-month filing extension does not apply to the "
                 "withholding tax payment. Pay via Form 502W or ACH credit. To avoid the extension penalty, pay "
                 "the lesser of 90% of the current-year withholding liability or 100% of the prior year's, "
                 "provided the prior year covered 12 months and reflected a liability."),
     "notes": "Confirmed three ways, including Va. Code s.58.1-486.2 D.2."},
    {"diagnostic_id": "D_VA502_U7_ADJ_D5_TRUNCATED", "severity": "info",
     "title": "Schedule 502ADJ Section D Line 5 label is truncated on the form face",
     "condition": "amended return with Schedule 502ADJ Section D completed",
     "message": ("The FINAL Rev. 07/26 form face prints Line 5 as 'If Line 4 above is less than Section 1, Line 1 "
                 "of Form 502, subtract Line 4 above' and then breaks to a dot leader; the trailing clause is "
                 "missing where Line 6's symmetric clause is complete. This is treated as a form-face "
                 "typographical defect: the arithmetic (Section 1 Line 1 minus Section D Line 4 = additional tax "
                 "due) is forced by Line 6's mirror. Verify against the rendered form before filing."),
     "notes": "U7 - reproduced byte-for-byte on an independent extraction; not an extraction artifact."},
    {"diagnostic_id": "D_VA502_MUTEX_WITH_PTET", "severity": "error",
     "title": "Form 502 and Form 502PTET are mutually exclusive",
     "condition": "a Form 502PTET has already been filed for this taxable year",
     "message": ("Pass-through entities opting to make the elective entity-level tax election must electronically "
                 "submit Form 502PTET INSTEAD OF Form 502. If a pass-through entity return (Form 502 or Form "
                 "502PTET) has already been filed for the taxable year, any subsequent return must be marked as "
                 "amended - use Reason Code 05 for a Form 502PTET amended return."),
     "notes": "Filing-mode gate."},
]

VA502_SCENARIOS: list[dict] = [
    {"scenario_name": "Partnership, wholly Virginia, no withholding due", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"entity_module": "1065", "entity_type_code": "PL", "wholly_within_virginia": True,
                "wk_ordinary_income": 400000, "wk_interest": 25000, "total_deductions": 60000,
                "l1_no_double_count_confirmed": True, "owner_count_total": 3, "owner_count_nonresident": 0},
     "expected_outputs": {"1": 425000, "6": 425000, "7": 1.00, "P2-1": 0},
     "notes": "L1 = 400,000 + 25,000 = 425,000 (deductions do NOT reduce it). Wholly-Virginia short path: "
              "Lines 4 and 5 blank, Line 6 = Line 1, Line 7 = 100%, Schedule 502A skipped. No nonresident "
              "owners, so Page 2 Line 1 is zero."},
    {"scenario_name": "S corporation module - the six branch points", "scenario_type": "normal", "sort_order": 2,
     "inputs": {"entity_module": "1120S", "entity_type_code": "SC", "federal_enclosure_kind": "1120S_with_schedule_k",
                "owner_count_total": 4, "l1_no_double_count_confirmed": True, "wk_ordinary_income": 300000},
     "expected_outputs": {"entity_type_code": "SC", "1": 300000},
     "notes": "SC is the only valid entity type code for the 1120S module; owner count comes off Form 1120-S "
              "Page 1 item I (shareholders during ANY part of the year); VK-1 participation type is SHR and the "
              "percentage comes off Schedule K-1 (1120-S) item G AS PRINTED; enclosure is Form 1120-S with "
              "Schedule K; the bank-franchise branch is available. Lines 1-20 are otherwise identical."},
    {"scenario_name": "Apportionment - three factors, double-weighted sales, divide by four", "scenario_type": "normal", "sort_order": 3,
     "inputs": {"property_factor_va_begin": 200000, "property_factor_va_end": 200000,
                "property_factor_ew_begin": 1000000, "property_factor_ew_end": 1000000,
                "payroll_factor_va": 300000, "payroll_factor_ew": 1000000,
                "sales_factor_va": 400000, "sales_factor_ew": 2000000, "apportionment_method_box": 9},
     "expected_outputs": {"502A-B2c": 0.20, "502A-B2d": 0.40, "502A-B2e": 0.90, "502A-B2f": 0.225, "7": 0.225},
     "notes": "2(a) = 200,000/1,000,000 = 0.20; 2(b) = 300,000/1,000,000 = 0.30; 2(c) = 400,000/2,000,000 = 0.20; "
              "2(d) = 0.20 x 2 = 0.40; 2(e) = 0.20 + 0.30 + 0.40 = 0.90; 2(f) = 0.90 / 4 = 0.225. Virginia is "
              "NOT a single sales factor state for PTEs."},
    {"scenario_name": "Apportionment - sales factor does not exist (divisor drops to 2)", "scenario_type": "edge", "sort_order": 4,
     "inputs": {"property_factor_va_begin": 200000, "property_factor_va_end": 200000,
                "property_factor_ew_begin": 1000000, "property_factor_ew_end": 1000000,
                "payroll_factor_va": 300000, "payroll_factor_ew": 1000000,
                "sales_factor_va": 0, "sales_factor_ew": 0, "apportionment_method_box": 9},
     "expected_outputs": {"502A-B2e": 0.50, "502A-B2f": 0.25},
     "notes": "With no sales denominator, 2(e) = 0.20 + 0.30 = 0.50 and the divisor drops by the sales factor's "
              "DOUBLE weight to 2, giving 0.25. Dividing by 3 (counting sales as one factor) would give 0.166667 "
              "and is wrong; the instruction's 'the number of existing factors' reconciles with the face only on "
              "the weight-sum reading."},
    {"scenario_name": "Section C - commercial domicile outside Virginia", "scenario_type": "normal", "sort_order": 5,
     "inputs": {"commercial_domicile_in_va": False, "dividends_received": 50000,
                "nonapport_investment_income": 30000, "nonapport_investment_loss": 10000,
                "wk_ordinary_income": 1000000, "l1_no_double_count_confirmed": True},
     "expected_outputs": {"4": 0.0, "5": 70000.0, "6": 930000.0},
     "notes": "3(c) = 50,000 + 30,000 = 80,000; 3(e) = 80,000 - 10,000 = 70,000 -> Line 5; Line 6 = 1,000,000 - "
              "70,000 = 930,000. Line 4 is zero because Section C Line 2 applies only where the commercial "
              "domicile IS in Virginia. Lines 3(b)/3(d) trigger the Allied-Signal RED (R5)."},
    {"scenario_name": "Withholding - 5% with part-year proration and a per-owner floor", "scenario_type": "edge", "sort_order": 6,
     "inputs": {"owner_count_nonresident": 3, "nonresident_va_source_income": 200000,
                "owner_days_nonresident": 146, "withholding_credits_passed_through": 12000},
     "expected_outputs": {"owner_full_year": 10000.0, "owner_part_year": 4000.0, "owner_over_credited": 0.0},
     "notes": "Full-year nonresident: 200,000 x 5% = 10,000. Part-year (146 days outside Virginia): 200,000 x "
              "146/365 = 80,000, x 5% = 4,000. An owner with 12,000 of pass-through credits against a 10,000 "
              "withholding liability floors at ZERO, not negative 2,000 - and the floor is applied per owner "
              "BEFORE the Page 2 Line 1 total is struck."},
    {"scenario_name": "Extension penalty worksheet - 30-day months rounded up, capped at 12%", "scenario_type": "edge", "sort_order": 7,
     "inputs": {"nonresident_va_source_income": 200000, "withholding_paid_by_entity": 0, "days_late": 45},
     "expected_outputs": {"P2-1": 10000.0, "P2-4": 10000.0, "P2-5": 400.0},
     "notes": "Line 1 = 10,000; nothing paid, so Line 4 = 10,000 and the balance exceeds 10% of Line 1 - the "
              "extension penalty applies. 45 days = ceil(45/30) = 2 months; 2 x 2% = 4%; 10,000 x 4% = 400. At "
              "200 days the 7 months would be 14%, capped at 12% = 1,200."},
    {"scenario_name": "Page 2 Line 10 - the four branches", "scenario_type": "edge", "sort_order": 8,
     "inputs": {"L3": 5000, "L6": 0, "L7": 100, "L8": 100, "L9": 0},
     "expected_outputs": {"branch4_L10": 5000.0, "branch2_L10": 4900.0, "branch3_L10": 3700.0, "branch1_L10": None},
     "notes": "Branch 4 (L6 == L9): L10 = L3 = 5,000. Branch 2 (L6 > L9, e.g. L6 = 1,200 and L9 = 0): L10 = "
              "5,000 - 100 = 4,900. Branch 3 (L9 > L6, e.g. L9 = 1,200): L10 = 5,000 - (100 + 1,200) = 3,700. "
              "Branch 1 (L8 or L9 exceeds L3): NO Line 10 amount - go to Line 13."},
    {"scenario_name": "Safe harbor - both provisos must hold", "scenario_type": "edge", "sort_order": 9,
     "inputs": {"current_year_liability": 20000, "prior_year_wh_liability": 15000,
                "prior_year_full_12_months": True, "prior_year_had_wh_liability": True},
     "expected_outputs": {"required_payment": 15000.0, "required_if_prior_year_short": 18000.0},
     "notes": "Lesser of 90% x 20,000 = 18,000 and 100% x 15,000 = 15,000 -> 15,000. If the prior year did not "
              "cover 12 months or reflected no liability, the prior-year leg is unavailable and 18,000 stands."},
]


# ===========================================================================
# FORM VA_502PTET - the 5.75% elective entity-level tax
# Page 1 is the SHARED block; Page 2 is an entirely different return.
# ===========================================================================

VAPTET_FACTS: list[dict] = _page1_facts() + [
    {"fact_key": "ptet_election_certified", "label": "Election checkbox certified on Page 1",
     "data_type": "boolean", "required": True, "sort_order": 100,
     "notes": "'If this box is not checked, the election will be invalid.'"},
    {"fact_key": "ptet_election_act", "label": "Act by which the election was made", "data_type": "choice",
     "required": False, "sort_order": 101, "choices": list(VA_PTET_ELECTION_ACTS),
     "notes": "U5 - the STATUTE names only the timely filed return; the payment acts are DOR administration."},
    {"fact_key": "no_va_business_or_source_income", "label": "Electing PTE does not conduct business in Virginia or have Virginia source income",
     "data_type": "boolean", "required": False, "sort_order": 102,
     "notes": "A real filing mode - electing to pay on behalf of Virginia RESIDENT owners only."},
    {"fact_key": "owners_eligible_nonresident", "label": "Line a - eligible individual and fiduciary NONRESIDENT owners",
     "data_type": "integer", "required": False, "sort_order": 103},
    {"fact_key": "owners_eligible_resident", "label": "Line b - eligible individual and fiduciary RESIDENT owners",
     "data_type": "integer", "required": False, "sort_order": 104},
    {"fact_key": "owners_ineligible", "label": "Line c - ineligible owners (corporate and other entity owners)",
     "data_type": "integer", "required": False, "sort_order": 105,
     "notes": "Any PTE may ELECT; only eligible owners may claim the credit. Two different questions."},
    {"fact_key": "owners_nonres_corporate_withholding", "label": "Line d - nonresident corporate owners requiring withholding",
     "data_type": "integer", "required": False, "sort_order": 106},
    {"fact_key": "eligible_owner_pct", "label": "Eligible owners' aggregate participation percentage",
     "data_type": "decimal", "required": False, "sort_order": 107,
     "notes": "U6 - the working assumption for narrowing Page 1 Lines 13/18 to Section I Lines 2/4."},
    {"fact_key": "sec179_as_filed", "label": "IRC 179 deduction as claimed on Schedule K", "data_type": "decimal",
     "required": False, "sort_order": 108},
    {"fact_key": "sec179_ccorp_limit", "label": "IRC 179 amount allowed to a federal C CORPORATION (PTET base limit)",
     "data_type": "decimal", "required": False, "sort_order": 109,
     "notes": "The FEDERAL C-corp limit for the BASE - distinct from the Virginia deconformity on Lines 9/15."},
    {"fact_key": "charitable_as_filed", "label": "Charitable contributions as claimed on Schedule K",
     "data_type": "decimal", "required": False, "sort_order": 110},
    {"fact_key": "charitable_ccorp_limit", "label": "Charitable contributions allowed to a federal C CORPORATION",
     "data_type": "decimal", "required": False, "sort_order": 111},
    {"fact_key": "scorp_all_nonresident_election", "label": "Electing S corporation computes as if ALL owners were nonresidents",
     "data_type": "boolean", "required": False, "sort_order": 112,
     "notes": "U9 - S-corp only; NO CHECKBOX exists on the face; detectable only by an empty Column B."},
    {"fact_key": "eligible_additions_col_a", "label": "Section I Line 2 Column A - nonresident eligible owners' share of additions",
     "data_type": "decimal", "required": False, "sort_order": 113},
    {"fact_key": "eligible_additions_col_b", "label": "Section I Line 2 Column B - resident eligible owners' share of additions",
     "data_type": "decimal", "required": False, "sort_order": 114},
    {"fact_key": "eligible_subtractions_col_a", "label": "Section I Line 4 Column A - nonresident eligible owners' share of subtractions",
     "data_type": "decimal", "required": False, "sort_order": 115},
    {"fact_key": "eligible_subtractions_col_b", "label": "Section I Line 4 Column B - resident eligible owners' share of subtractions",
     "data_type": "decimal", "required": False, "sort_order": 116},
    {"fact_key": "nonres_corporate_va_source_share", "label": "Nonresident corporate owners' share of Virginia-source taxable income",
     "data_type": "decimal", "required": False, "sort_order": 117,
     "notes": "W4/U3 - the base for Line 7(b). The package states neither rate nor base."},
    {"fact_key": "ptet_line7b_override", "label": "Line 7(b) withholding tax due for nonresident corporate owners (editable)",
     "data_type": "decimal", "required": False, "sort_order": 118,
     "notes": "Pre-filled at 5% of the share, EDITABLE, and flagged for review. This one moves money."},
    {"fact_key": "ptet_estimated_paid", "label": "Section III Line 8 - estimated tax paid plus prior-year carryover",
     "data_type": "decimal", "required": False, "sort_order": 119},
    {"fact_key": "ptet_extension_and_other_payments", "label": "Section III Line 9 - extension payment, pre-filing withholding, other payments",
     "data_type": "decimal", "required": False, "sort_order": 120,
     "notes": "Includes nonresident withholding paid for INELIGIBLE owners, and withholding paid for eligible "
              "owners BEFORE the PTET election was made - recovered here, not refunded separately."},
    {"fact_key": "ptet_motion_picture_credit", "label": "Section III Line 10a - Motion Picture Production Tax Credit",
     "data_type": "decimal", "required": False, "sort_order": 121},
    {"fact_key": "ptet_credited_next_year", "label": "Section IV Line 14 - overpayment credited to next year's estimated tax",
     "data_type": "decimal", "required": False, "sort_order": 122},
    {"fact_key": "ptet_form_500c_included", "label": "Section IV Line 16 - Form 500C included in the electronic submission",
     "data_type": "boolean", "required": False, "sort_order": 123},
    {"fact_key": "ptet_penalty", "label": "Section IV Line 17 - penalty", "data_type": "decimal",
     "required": False, "sort_order": 124},
    {"fact_key": "ptet_interest", "label": "Section IV Line 18 - interest (IRC 6621 + 2%)", "data_type": "decimal",
     "required": False, "sort_order": 125},
    {"fact_key": "months_after_original_due_date", "label": "Months elapsed after the original due date at filing",
     "data_type": "integer", "required": False, "sort_order": 126, "notes": "Drives the 6-month HARD BAR."},
    {"fact_key": "made_estimated_or_extension_payment", "label": "Corresponding estimated or extension payment was made",
     "data_type": "boolean", "required": False, "sort_order": 127,
     "notes": "The ONLY thing that rescues a filer past the 6-month bar."},
    {"fact_key": "expected_ptet_liability", "label": "PTET reasonably expected for the year (estimate threshold test)",
     "data_type": "decimal", "required": False, "sort_order": 128},
    {"fact_key": "wants_entity_level_rd_credit", "label": "PTE intends to claim the refundable Research and Development Tax Credit directly",
     "data_type": "boolean", "required": False, "sort_order": 129, "notes": "Triggers R11 - the face cannot carry it."},
]

VAPTET_RULES: list[dict] = _page1_rules("R-VAP", "Schedule PTET ADJ") + [
    {"rule_id": "R-VAP-ELECTION", "title": "The election: who may make it, how, binding effect, and the hard bar", "rule_type": "validation",
     "formula": ("ANY PTE may elect; only ELIGIBLE OWNERS (direct owners who are natural persons taxed under "
                 "Article 2, or estates or trusts taxed under Article 6) may claim the credit ; "
                 "election acts: an estimated payment, an extension payment, or filing Form 502PTET on or before "
                 "the extended due date ; the Page 1 certification checkbox MUST be checked or the election is "
                 "INVALID ; once filed the election is BINDING for the year and binding on ALL eligible owners - "
                 "they cannot opt out ; "
                 "HARD BAR: filed more than 6 months after the original due date, or more than 30 days after the "
                 "federal extended due date -> NOT PERMITTED to file Form 502PTET unless corresponding estimated "
                 "or extension payments were made ; an electing PTE may NOT file Form 765"),
     "inputs": ["ptet_election_certified", "ptet_election_act", "months_after_original_due_date",
                "made_estimated_or_extension_payment"], "outputs": [], "sort_order": 20,
     "description": ("The entity gate is open and the BASE is narrowed - not the other way round. The hard bar is "
                     "a VALIDATION rule, not a penalty: the return is refused. U5 - the statute names only the "
                     "timely filed return, so the payment-as-election route carries a review flag.")},
    {"rule_id": "R-VAP-BASE", "title": "Section I Line 1 - the base DIVERGES from Form 502 Line 1", "rule_type": "calculation",
     "formula": ("Section I Line 1 = (Schedule K income - allowed deductions) x eligible owners' share, where "
                 "allowed deductions = other deductions + min(IRC 179 as filed, the federal C-CORPORATION limit) "
                 "+ min(charitable as filed, the federal C-CORPORATION limit) ; "
                 "CONTRAST: Form 502 Line 1 = income ONLY, never reduced by Line 2"),
     "inputs": ["total_deductions", "sec179_as_filed", "sec179_ccorp_limit", "charitable_as_filed",
                "charitable_ccorp_limit", "eligible_owner_pct"], "outputs": ["I-1A", "I-1B"], "sort_order": 21,
     "description": ("THE CLONE TRAP. Two different bases on two forms with identical Page-1 line numbering. The "
                     "PTET base needs an entity-level C-corporation pro-forma recomputation of Section 179 and "
                     "charitable contributions, replacing the partner/shareholder-level federal limits - no "
                     "federal analogue exists. And note the sequencing: this is the FEDERAL C-corp limit for the "
                     "BASE, while the VIRGINIA Section 179 deconformity then adjusts it on Lines 9/15. Two "
                     "Section 179 rules, in sequence, on one return. Statutory base per s.58.1-390.3 B and D, "
                     "including the elimination of any federal deduction for state and local income taxes.")},
    {"rule_id": "R-VAP-SEC-I", "title": "Section I Lines 2-5 - two columns, PER-COLUMN zero floor", "rule_type": "calculation",
     "formula": ("Column A nonresident eligible owners, Column B resident eligible owners ; "
                 "L3 = L1 + L2 ; L5 = max(0, L3 - L4) IN EACH COLUMN INDEPENDENTLY ; "
                 "nonresident columns are limited to income attributable to Virginia sources (s.58.1-390.3 C) ; "
                 "an electing S CORPORATION may compute as if all owners were nonresidents and report entirely "
                 "in Column A"),
     "inputs": ["eligible_additions_col_a", "eligible_additions_col_b", "eligible_subtractions_col_a",
                "eligible_subtractions_col_b", "scorp_all_nonresident_election"],
     "outputs": ["I-2A", "I-2B", "I-3A", "I-3B", "I-4A", "I-4B", "I-5A", "I-5B"], "sort_order": 22,
     "description": ("TWO INDEPENDENT FLOORS, not one - a resident-column loss cannot offset nonresident-column "
                     "income. U6: Lines 2 and 4 want the ELIGIBLE-OWNER portion of Page 1 Lines 13 and 18, but "
                     "Page 1 is expressly whole-entity and the DOR provides no line, ratio or worksheet for the "
                     "narrowing. U9: the S-corp all-nonresident option has no checkbox on the face.")},
    {"rule_id": "R-VAP-TAX", "title": "Section II - Line 6, the 5.75% on Line 7a, and Line 7", "rule_type": "calculation",
     "formula": ("L6 = max(0, Section I L5 Column A + Section I L5 Column B) - the SECOND floor ; "
                 "L7a = L6 x 5.75% ; L7 = L7a + L7b"),
     "inputs": [], "outputs": ["II-6", "II-7a", "II-7"], "sort_order": 23,
     "description": ("Va. Code s.58.1-390.3 B, verbatim: 'A tax at the rate of 5.75 percent is hereby annually "
                     "imposed'. Line 7a - NOT Line 7 - is the amount of elective tax credit passed through to "
                     "eligible individual and fiduciary owners.")},
    {"rule_id": "R-VAP-WHCORP", "title": "Line 7(b) - withholding for nonresident CORPORATE owners", "rule_type": "calculation",
     "formula": ("L7b = 5% x nonresident corporate owners' share of Virginia-source taxable income "
                 "[PRE-FILLED, EDITABLE, review-flagged] ; L7 = L7a + L7b"),
     "inputs": ["nonres_corporate_va_source_share", "ptet_line7b_override", "owners_nonres_corporate_withholding"],
     "outputs": ["II-7b"], "sort_order": 24,
     "description": ("W4 / U3 - THE RATE IS AN INFERENCE FROM A DIFFERENT FORM. The 14-page 502PTET package "
                     "contains no withholding rate and no computation; a boundary-anchored search returns zero "
                     "standalone '5%' and zero 'five percent'. The 5% is carried over from Va. Code s.58.1-486.2 "
                     "and the Form 502 instructions on the basis that it is the same statutory obligation, "
                     "differently housed. The PTET module is therefore NOT purely a 5.75% entity tax - it carries "
                     "a withholding leg. Withholding survives ONLY for nonresident corporate owners: the PTE does "
                     "not withhold for eligible nonresident owners for whom it files Form 502PTET.")},
    {"rule_id": "R-VAP-PAY", "title": "Section III Lines 8-11 - payments and credits", "rule_type": "calculation",
     "formula": ("L10 = L10a + L10b + L10c ; L11 = L8 + L9 + L10 ; "
                 "L9 includes nonresident withholding payments made for INELIGIBLE owners, and withholding paid "
                 "for eligible owners BEFORE the PTET election was made"),
     "inputs": ["ptet_estimated_paid", "ptet_extension_and_other_payments", "ptet_motion_picture_credit"],
     "outputs": ["III-10", "III-11"], "sort_order": 25,
     "description": ("Pre-election withholding is recovered on Line 9, not refunded separately. Lines 10b and 10c "
                     "are both printed 'Reserved for future use' - see R11.")},
    {"rule_id": "R-VAP-SETTLE", "title": "Sections IV and V - tax owed, overpayment, charges, refund", "rule_type": "calculation",
     "formula": ("L12 = L7 - L11 when L7 > L11 ; L13 = L11 - L7 when L11 > L7 ; L15 = L13 - L14 ; "
                 "L19 = L16 + L17 + L18 ; "
                 "L20 = L12 + L19 if tax is owed on L12, OR L19 - L15 if L15 is less than L19 ; "
                 "L21 = L15 - L19 where there is a net overpayment on L15"),
     "inputs": ["ptet_credited_next_year", "ptet_penalty", "ptet_interest", "ptet_form_500c_included"],
     "outputs": ["IV-12", "IV-13", "IV-14", "IV-15", "IV-19", "V-20", "V-21"], "sort_order": 26,
     "description": "Line 16 is the Form 500C addition to tax; the checkbox indicates Form 500C is in the e-file submission."},
    {"rule_id": "R-VAP-EST", "title": "Estimated payments - the $1,000 threshold and four 25% instalments", "rule_type": "validation",
     "formula": ("required if the PTET can reasonably be expected to exceed $1,000 ; four instalments of 25% ; "
                 "calendar-year: April 15 / June 15 / September 15 / December 15 ; "
                 "fiscal-year: the 15th day of the 4th, 6th, 9th and 12th month FOLLOWING THE BEGINNING of the "
                 "fiscal year ; computed 'based upon the rules set forth under Virginia law for the corporate "
                 "income tax'"),
     "inputs": ["expected_ptet_liability"], "outputs": [], "sort_order": 27,
     "description": "An estimated payment is also one of the three acts that MAKES the election, and the thing "
                    "that rescues a filer past the 6-month bar (U5)."},
    {"rule_id": "R-VAP-500C", "title": "Form 500C - underpayment of estimated tax by electing PTEs", "rule_type": "calculation",
     "formula": ("Part I: L1 income tax reduced by allowable nonrefundable and refundable credits; L2 = 90% of "
                 "L1; L3 = 25% of L2 per column; L4-L7 payments; L8 underpayment ; "
                 "Part II exceptions: Ex.1 prior year's tax (25/50/75/100%), Ex.2 prior year's income at current "
                 "year's rates (25/50/75/100%), Ex.3 annualized income (22.50/45/67.50/90%) ; "
                 "Part III L13-L17 charge at IRC 6621 + 2% -> Form 502PTET Section IV Line 16"),
     "inputs": ["ptet_form_500c_included"], "outputs": ["IV-16"], "sort_order": 28,
     "description": ("Va. Code s.58.1-504. Form 500C is titled '2025 Underpayment of Virginia Estimated Tax by "
                     "Corporations AND ELECTING PASS-THROUGH ENTITIES' - the corporate form does the job because "
                     "s.58.1-390.3 F directs the Department to assess and collect 'as if such tax is a corporate "
                     "income tax'. If an amended return is filed there is NO adjustment allowed to the addition "
                     "to tax previously computed and paid.")},
    {"rule_id": "R-VAP-PEN", "title": "PTET penalties - the CORPORATE regime (Article 14), not the Form 502 regime", "rule_type": "calculation",
     "formula": ("extension penalty 2% per month if less than 90% is paid by the ORIGINAL due date ; "
                 "late payment penalty 6% per month, maximum 30% ; "
                 "late filing penalty 30% of tax due, with a $100 MINIMUM that applies WHETHER OR NOT TAX IS DUE ; "
                 "the late payment penalty does not apply to the extent the late filing penalty applies ; "
                 "interest at IRC 6621 + 2% from the ORIGINAL due date until paid ; "
                 "returned check or EFT nonpayment $35"),
     "inputs": ["ptet_penalty"], "outputs": ["IV-17"], "sort_order": 29,
     "description": ("Penalties run under Article 14 (s.58.1-450 et seq.) 'instead of the penalties in Article 9' "
                     "- so a single PTE penalty engine WILL be wrong on one of the two paths. Compare the Form "
                     "502 regime: 6%/month capped 30%, a FLAT $1,200 late filing penalty, and a "
                     "non-return-computable 6%-of-owners'-income assessed penalty. A fraudulent return is a "
                     "Class 6 felony (ss.58.1-451, -452).")},
    {"rule_id": "R-VAP-CREDIT", "title": "The PTET credit chain - Line 7a to PTET ADJ C-III-10 to VK-1 Part III Line 10", "rule_type": "calculation",
     "formula": ("Schedule PTET ADJ Section C Part III Line 10 = Form 502PTET Section II Line 7a ; "
                 "that amount = the sum of VK-1 Part III Line 10 across owners ; "
                 "Schedule PTET ADJ Part IV Line 1 = Add Part III Lines 1, 7, 9 AND 10 ; "
                 "the owner-side credit is REFUNDABLE (s.58.1-390.3 E)"),
     "inputs": [], "outputs": ["III-10", "V-21", "VK1-PIII-10"], "sort_order": 30,
     "description": ("KEYED TO 7a, NOT 7 - the corporate withholding leg is excluded from the credit. The owner "
                     "must add back any deduction for state and local income taxes paid by the PTE. A PTET credit "
                     "allocated to an estate or trust CANNOT be re-allocated to beneficiaries. Form 502PTET and "
                     "all required schedules must be completed and filed BEFORE the Department will allow eligible "
                     "owners to claim the credit - a hard sequencing dependency on every owner's Form 760. Note "
                     "also that s.58.1-332 C.2 is a DIFFERENT credit (the out-of-state PTET credit), not this one.")},
    {"rule_id": "R-VAP-SUNSET", "title": "NO SUNSET - build to the statute, not the form text", "rule_type": "validation",
     "formula": ("VA_PTET_SUNSET_YEAR[2025] = None ; the PTET election and the associated credits are PERMANENT ; "
                 "do NOT encode 'before January 1, 2027' or 'Taxable Years 2021-2026' anywhere"),
     "inputs": [], "outputs": [], "sort_order": 31,
     "description": ("U4. Va. Code s.58.1-390.3 as it stands contains no expiration date at all. The 2026 "
                     "Amendments to the 2025 Appropriation Act (HB 29, c. 7, thirteenth enactment clause) "
                     "permanently extended both the election and the associated credits, and also the out-of-state "
                     "credit that would have expired 1/1/2026. The Rev. 08/26 package - RE-ISSUED on 2026-08-10, "
                     "five and a half months AFTER the repeal - still recites the sunset SIX times, and the Form "
                     "502 instruction book contradicts itself between page 1 and page 3. Dead text.")},
]

VAPTET_RULE_LINKS: list[tuple[str, str, str, str]] = _page1_rule_links("R-VAP") + [
    ("R-VAP-ELECTION", "VA_2025_FORM_502PTET_PKG", "primary", "election acts, certification checkbox, binding effect, hard bar"),
    ("R-VAP-ELECTION", "VA_CODE_58_1_390_1", "primary", "eligible owner definition - direct natural persons, estates, trusts"),
    ("R-VAP-ELECTION", "VA_CODE_58_1_390_3", "secondary", "s.58.1-390.3 A.2 - election on the timely filed return (U5)"),
    ("R-VAP-BASE", "VA_2025_FORM_502PTET_PKG", "primary", "Section I Line 1 - deductions included, C-corp re-limits"),
    ("R-VAP-BASE", "VA_CODE_58_1_390_3", "primary", "s.58.1-390.3 B and D - the statutory base and the SALT add-back"),
    ("R-VAP-SEC-I", "VA_2025_FORM_502PTET_PKG", "primary", "two columns, per-column zero floor, S-corp option"),
    ("R-VAP-SEC-I", "VA_CODE_58_1_390_3", "secondary", "s.58.1-390.3 C - nonresident shares limited to Virginia sources"),
    ("R-VAP-TAX", "VA_CODE_58_1_390_3", "primary", "s.58.1-390.3 B - 5.75 percent, verbatim"),
    ("R-VAP-TAX", "VA_2025_FORM_502PTET_PKG", "primary", "Section II Lines 6, 7a, 7 face labels"),
    ("R-VAP-WHCORP", "VA_CODE_58_1_486_2", "primary", "s.58.1-486.2 B.1 - the 5% relied on for Line 7(b)"),
    ("R-VAP-WHCORP", "VA_2025_FORM_502PTET_PKG", "secondary", "Line 7(b) exists but states no rate or base (U3)"),
    ("R-VAP-PAY", "VA_2025_FORM_502PTET_PKG", "primary", "Section III Lines 8-11 incl. pre-election withholding"),
    ("R-VAP-SETTLE", "VA_2025_FORM_502PTET_PKG", "primary", "Sections IV and V face labels"),
    ("R-VAP-EST", "VA_2025_FORM_502PTET_PKG", "primary", "the $1,000 threshold and the four instalment dates"),
    ("R-VAP-500C", "VA_2025_FORM_502PTET_PKG", "primary", "Form 500C Parts I-III inside the package"),
    ("R-VAP-500C", "VA_CODE_58_1_390_3", "secondary", "s.58.1-390.3 F - collected as a corporate income tax"),
    ("R-VAP-PEN", "VA_2025_FORM_502PTET_PKG", "primary", "Article 14 corporate penalties incl. the $100 minimum"),
    ("R-VAP-CREDIT", "VA_CODE_58_1_390_3", "primary", "s.58.1-390.3 E - the REFUNDABLE owner credit"),
    ("R-VAP-CREDIT", "VA_2025_SCH_VK1", "secondary", "VK-1 Part III Line 10 and the no-reallocation bar"),
    ("R-VAP-SUNSET", "VA_CODE_58_1_390_3", "primary", "the statute carries no expiration date"),
    ("R-VAP-SUNSET", "VA_2025_FORM_502PTET_PKG", "interpretive", "the re-issued package still prints the repealed sunset six times"),
]

VAPTET_LINES: list[dict] = _page1_lines("Schedule PTET ADJ", "R-VAP") + [
    {"line_number": "I-1A", "description": "Section I Line 1 Col A - nonresident eligible owners' shares of taxable income (deductions INCLUDED)",
     "line_type": "calculated", "source_rules": ["R-VAP-BASE"], "sort_order": 100},
    {"line_number": "I-1B", "description": "Section I Line 1 Col B - resident eligible owners' shares of taxable income",
     "line_type": "calculated", "source_rules": ["R-VAP-BASE"], "sort_order": 101},
    {"line_number": "I-2A", "description": "Section I Line 2 Col A - owners' shares of Virginia additions (from Page 1 Line 13)",
     "line_type": "input", "source_facts": ["eligible_additions_col_a"], "sort_order": 102},
    {"line_number": "I-2B", "description": "Section I Line 2 Col B - owners' shares of Virginia additions",
     "line_type": "input", "source_facts": ["eligible_additions_col_b"], "sort_order": 103},
    {"line_number": "I-3A", "description": "Section I Line 3 Col A - Add Lines 1 and 2", "line_type": "subtotal",
     "source_rules": ["R-VAP-SEC-I"], "sort_order": 104},
    {"line_number": "I-3B", "description": "Section I Line 3 Col B - Add Lines 1 and 2", "line_type": "subtotal",
     "source_rules": ["R-VAP-SEC-I"], "sort_order": 105},
    {"line_number": "I-4A", "description": "Section I Line 4 Col A - owners' shares of Virginia subtractions (from Page 1 Line 18)",
     "line_type": "input", "source_facts": ["eligible_subtractions_col_a"], "sort_order": 106},
    {"line_number": "I-4B", "description": "Section I Line 4 Col B - owners' shares of Virginia subtractions",
     "line_type": "input", "source_facts": ["eligible_subtractions_col_b"], "sort_order": 107},
    {"line_number": "I-5A", "description": "Section I Line 5 Col A - Virginia taxable income; if Line 4 exceeds Line 3, enter ZERO",
     "line_type": "calculated", "source_rules": ["R-VAP-SEC-I"], "sort_order": 108,
     "notes": "PER-COLUMN floor. A resident-column loss cannot offset nonresident-column income."},
    {"line_number": "I-5B", "description": "Section I Line 5 Col B - Virginia taxable income; if Line 4 exceeds Line 3, enter ZERO",
     "line_type": "calculated", "source_rules": ["R-VAP-SEC-I"], "sort_order": 109},
    {"line_number": "II-6", "description": "Total Virginia taxable income: Add Line 5, Columns A and B (if negative, enter zero)",
     "line_type": "subtotal", "source_rules": ["R-VAP-TAX"], "sort_order": 110},
    {"line_number": "II-7a", "description": "Pass-Through Entity Tax: Multiply Line 6 by 5.75% (this is the credit passed to owners)",
     "line_type": "calculated", "source_rules": ["R-VAP-TAX"], "sort_order": 111},
    {"line_number": "II-7b", "description": "Withholding tax due for nonresident corporate owners (5% - INFERRED, W4/U3)",
     "line_type": "input", "source_facts": ["ptet_line7b_override"], "sort_order": 112},
    {"line_number": "II-7", "description": "Add amounts on Lines 7a and 7b and enter the total here",
     "line_type": "total", "source_rules": ["R-VAP-TAX"], "sort_order": 113},
    {"line_number": "III-8", "description": "Estimated tax paid including any overpayment carried over from the prior year",
     "line_type": "input", "source_facts": ["ptet_estimated_paid"], "sort_order": 114},
    {"line_number": "III-9", "description": "Extension payment, withholding paid prior to return filing, and other payments",
     "line_type": "input", "source_facts": ["ptet_extension_and_other_payments"], "sort_order": 115},
    {"line_number": "III-10a", "description": "Motion Picture Production Tax Credit", "line_type": "input",
     "source_facts": ["ptet_motion_picture_credit"], "sort_order": 116},
    {"line_number": "III-10b", "description": "Reserved for future use", "line_type": "informational", "sort_order": 117},
    {"line_number": "III-10c", "description": "Other - printed 'Reserved' (the instruction names an R&D credit the face cannot carry; U10)",
     "line_type": "informational", "sort_order": 118},
    {"line_number": "III-10", "description": "Add amounts on Lines 10a, 10b, and 10c", "line_type": "subtotal",
     "source_rules": ["R-VAP-PAY"], "sort_order": 119},
    {"line_number": "III-11", "description": "Total payments and credits. Add Lines 8-10.", "line_type": "subtotal",
     "source_rules": ["R-VAP-PAY"], "sort_order": 120},
    {"line_number": "IV-12", "description": "Tax owed: if Line 7 is greater than Line 11, enter the difference",
     "line_type": "calculated", "source_rules": ["R-VAP-SETTLE"], "sort_order": 121},
    {"line_number": "IV-13", "description": "Overpayment amount: if Line 11 is greater than Line 7, enter the difference",
     "line_type": "calculated", "source_rules": ["R-VAP-SETTLE"], "sort_order": 122},
    {"line_number": "IV-14", "description": "Amount of Line 13 credited to next year's estimated tax",
     "line_type": "input", "source_facts": ["ptet_credited_next_year"], "sort_order": 123},
    {"line_number": "IV-15", "description": "Net overpayment amount: Subtract Line 14 from Line 13",
     "line_type": "calculated", "source_rules": ["R-VAP-SETTLE"], "sort_order": 124},
    {"line_number": "IV-16", "description": "Addition to tax - check to indicate Form 500C is included in the electronic submission",
     "line_type": "calculated", "source_rules": ["R-VAP-500C"], "sort_order": 125},
    {"line_number": "IV-17", "description": "Penalty (Article 14 CORPORATE regime)", "line_type": "input",
     "source_facts": ["ptet_penalty"], "sort_order": 126},
    {"line_number": "IV-18", "description": "Interest (IRC 6621 plus 2% from the original due date)",
     "line_type": "input", "source_facts": ["ptet_interest"], "sort_order": 127},
    {"line_number": "IV-19", "description": "Total additional charges, penalties, and interest. Add Lines 16-18.",
     "line_type": "subtotal", "source_rules": ["R-VAP-SETTLE"], "sort_order": 128},
    {"line_number": "V-20", "description": "Amount owed (Lines 12 + 19, or Line 19 less Line 15)",
     "line_type": "total", "source_rules": ["R-VAP-SETTLE"], "sort_order": 129},
    {"line_number": "V-21", "description": "Amount of refund (Line 15 less Line 19)", "line_type": "total",
     "source_rules": ["R-VAP-SETTLE"], "sort_order": 130},
    {"line_number": "PTETADJ-C-III-10", "description": "Schedule PTET ADJ Section C Part III Line 10 = Form 502PTET Line 7a",
     "line_type": "calculated", "source_rules": ["R-VAP-CREDIT"], "sort_order": 131,
     "notes": "'This amount should equal the sum of the corresponding credit amounts reported on the "
              "participants' Schedules VK-1.' Keyed to 7a, NOT 7."},
    {"line_number": "PTETADJ-C-IV-1", "description": "Schedule PTET ADJ Part IV Line 1 - Add Part III, Lines 1, 7, 9, AND 10",
     "line_type": "calculated", "source_rules": ["R-VAP-CREDIT"], "sort_order": 132},
    {"line_number": "500C-P3-17", "description": "Form 500C Part III Line 17 - addition to tax -> Form 502PTET Section IV Line 16",
     "line_type": "calculated", "source_rules": ["R-VAP-500C"], "sort_order": 133},
]

VAPTET_DIAGNOSTICS: list[dict] = _page1_diagnostics("D_VAPTET") + [
    {"diagnostic_id": "D_VAPTET_BASE_DIVERGES", "severity": "warning",
     "title": "The 502PTET base is NOT the Form 502 base",
     "condition": "Section I Line 1 computed",
     "message": ("Unlike the nonresident withholding computation on Form 502, separately stated items of "
                 "DEDUCTION ARE INCLUDED when computing each eligible owner's share of taxable income on Form "
                 "502PTET, and any separately stated deduction subject to a federal limitation - notably "
                 "charitable contributions and the Section 179 deduction - is limited to what is allowed under "
                 "federal law for a C CORPORATION. This requires an entity-level C-corporation pro-forma "
                 "recomputation with no federal analogue. Do not carry Form 502 Line 1 across."),
     "notes": "The single easiest thing to get wrong by cloning Form 502 into Form 502PTET."},
    {"diagnostic_id": "D_VAPTET_TWO_179_RULES", "severity": "info",
     "title": "Two Section 179 rules apply in sequence on this return",
     "condition": "sec179_as_filed != 0",
     "message": ("The Section 179 amount in the PTET BASE is limited to the FEDERAL C-corporation limit "
                 "(Section I Line 1). Separately, Virginia's deconformity from the 2025 H.R. 1 increases to the "
                 "Section 179 expensing limits is then adjusted on Lines 9 and 15. These are two different rules "
                 "applied in sequence - do not collapse them."),
     "notes": "A sequencing trap unique to the PTET path."},
    {"diagnostic_id": "D_VAPTET_PER_COLUMN_FLOOR", "severity": "info",
     "title": "The Section I zero floor is PER COLUMN",
     "condition": "Section I Line 5 computed in either column",
     "message": ("Line 5 is floored at zero in EACH column independently ('If Line 4 is greater than Line 3, enter "
                 "zero'), and Line 6 is floored again after adding the two columns. A loss in the resident-owner "
                 "column therefore cannot offset income in the nonresident-owner column."),
     "notes": "Encode two independent floors, not one."},
    {"diagnostic_id": "D_VAPTET_U6_ELIGIBLE_SHARE", "severity": "warning",
     "title": "Section I Lines 2 and 4 narrow whole-entity totals with no prescribed method",
     "condition": "eligible_additions_col_a/b or eligible_subtractions_col_a/b entered",
     "message": ("Page 1 Lines 13 and 18 are expressly whole-entity ('Lines 1-20 are based on the entire "
                 "pass-through entity'), but Section I Lines 2 and 4 require the portion attributable to ELIGIBLE "
                 "OWNERS. Virginia provides no line, worksheet or ratio for this narrowing. This product allocates "
                 "by the eligible owners' aggregate participation percentage, per the general "
                 "modification-allocation rule. Verify before filing."),
     "notes": "U6 - re-read in full during verification; the package genuinely provides nothing."},
    {"diagnostic_id": "D_VAPTET_W4_LINE7B_RATE", "severity": "warning",
     "title": "Line 7(b) rate is inferred from Form 502 - verify before filing",
     "condition": "owners_nonres_corporate_withholding > 0 or nonres_corporate_va_source_share != 0",
     "message": ("The Form 502PTET instruction package states no rate and no base for Line 7(b) - the entire "
                 "14-page package contains no withholding rate or computation. This product pre-fills 5% of the "
                 "nonresident corporate owners' share of Virginia-source taxable income, carried over from "
                 "Virginia Code Section 58.1-486.2 and the Form 502 instructions on the basis that it is the same "
                 "statutory withholding obligation. The figure is editable. Confirm with the Department - this "
                 "line determines a real payment."),
     "notes": "W4 / U3 - one of the two money-moving open items."},
    {"diagnostic_id": "D_VAPTET_U4_STALE_SUNSET", "severity": "info",
     "title": "The printed PTET sunset is repealed - this product builds to the statute",
     "condition": "always, on the PTET path",
     "message": ("The 2025 Form 502PTET instruction package - re-issued 10 August 2026 - still recites a sunset "
                 "for 'taxable years... before January 1, 2027' and 'Taxable Years 2021-2026' in six places, and "
                 "the Form 502 instruction book contradicts itself between page 1 and page 3. That language is "
                 "DEAD. The 2026 Amendments to the 2025 Appropriation Act permanently extended the election and "
                 "the associated credits, and Virginia Code Section 58.1-390.3 as it stands contains no "
                 "expiration date at all. No sunset is applied by this product."),
     "notes": "U4 - build to the statute; a diagnostic, never an encoded sunset."},
    {"diagnostic_id": "D_VAPTET_HARD_BAR", "severity": "error",
     "title": "Form 502PTET may not be filed - the 6-month bar applies",
     "condition": "months_after_original_due_date > 6 and not made_estimated_or_extension_payment",
     "message": ("A pass-through entity that fails to file more than 6 months after the original due date, or "
                 "more than 30 days after the federal extended due date, WILL NOT BE PERMITTED to file Form "
                 "502PTET unless it made corresponding estimated payments or an extension payment for the taxable "
                 "year. This is a filing bar, not a penalty - the return is refused. File Form 502 instead. Note "
                 "that whether a payment is legally sufficient to MAKE the election is not settled by statute; "
                 "Virginia Code Section 58.1-390.3 A.2 names only the timely filed return."),
     "notes": "U5. The payment-as-election route rests on DOR Guidelines / TB 22-6 / TB 23-3, none obtained."},
    {"diagnostic_id": "D_VAPTET_ELECTION_BINDING", "severity": "info",
     "title": "The election is binding on all eligible owners",
     "condition": "ptet_election_certified",
     "message": ("Once Form 502PTET is filed the election is binding for that taxable year. The electing PTE must "
                 "obtain consent from its eligible owners, but the election is binding on ALL eligible owners once "
                 "made - eligible owners do not have the option to opt out with the Department. If the "
                 "certification checkbox on Page 1 is not checked the election is INVALID. An electing PTE may not "
                 "file Form 765, and Form 502PTET is filed INSTEAD OF Form 502."),
     "notes": "Election mechanics, verbatim."},
    {"diagnostic_id": "D_VAPTET_INELIGIBLE_OWNERS", "severity": "info",
     "title": "Any PTE may elect - but only eligible owners get the credit",
     "condition": "owners_ineligible > 0",
     "message": ("Since Taxable Year 2023 all pass-through entities may make the PTET election, but only owners "
                 "meeting the eligible owner requirement - DIRECT owners who are natural persons taxed under "
                 "Article 2, or estates or trusts taxed under Article 6 - may claim the refundable credit. "
                 "Corporate and other entity owners are ineligible: no PTET on their shares, and no credit. Track "
                 "the three owner classes separately on Page 1 Lines a through d."),
     "notes": "Entity gate open; base narrowed. Two different questions."},
    {"diagnostic_id": "D_VAPTET_U9_SCORP_ALL_NONRES", "severity": "warning",
     "title": "S corporation all-nonresident computation has no checkbox on the form",
     "condition": "scorp_all_nonresident_election and entity_module == '1120S'",
     "message": ("An electing S corporation with both nonresident and resident eligible owners may compute its "
                 "Virginia taxable income as if all of its owners were nonresidents and report the whole "
                 "computation in the nonresident owner column. There is no partnership analogue. No checkbox for "
                 "this option exists on the form face - the Department can detect it only from an empty Column B - "
                 "and neither its legal character (revocable? binding? annual?) nor its scope is stated anywhere. "
                 "Verify before filing."),
     "notes": "U9 - confirmed during verification that there is no checkbox; the option exists only in prose."},
    {"diagnostic_id": "D_VAPTET_R11_ENTITY_RD_CREDIT", "severity": "error",
     "title": "Entity-level Research and Development Tax Credit has no line on the form",
     "condition": "wants_entity_level_rd_credit",
     "message": ("The Form 502PTET instructions state that the PTE may directly claim the refundable Motion "
                 "Picture Production Tax Credit AND the Research and Development Tax Credit - but Lines 10(b) and "
                 "10(c) of the form are both printed 'Reserved for future use'. The instruction names a credit the "
                 "face cannot carry. Contact the Department before filing."),
     "notes": "R11 / U10 - confirmed on the FINAL face and in the line instructions."},
    {"diagnostic_id": "D_VAPTET_PRE_ELECTION_WH", "severity": "info",
     "title": "Pre-election withholding is recovered on Section III Line 9",
     "condition": "ptet_extension_and_other_payments != 0",
     "message": ("Line 9 may include nonresident withholding payments made for INELIGIBLE owners such as "
                 "nonresident corporate owners, and - importantly - withholding payments made for ELIGIBLE owners "
                 "BEFORE the PTE made the PTET election. Report those on this line; they are not refunded "
                 "separately. If composite payments were made before the election, the PTE can file an original or "
                 "amended Form 765 showing a ZERO tax liability to obtain a refund, or contact Customer Service to "
                 "request a transfer of the payments."),
     "notes": "A real recovery path that is easy to miss."},
    {"diagnostic_id": "D_VAPTET_CREDIT_KEYED_TO_7A", "severity": "warning",
     "title": "The PTET credit is keyed to Line 7a, not Line 7",
     "condition": "II-7b != 0",
     "message": ("Schedule PTET ADJ Section C Part III Line 10 equals Form 502PTET Section II Line 7a and must "
                 "equal the sum of the credit amounts on the participants' Schedules VK-1. The nonresident "
                 "corporate withholding on Line 7(b) is EXCLUDED from the credit even though it is included in the "
                 "Line 7 total. Form 502PTET and all required schedules must be completed and filed before the "
                 "Department will allow eligible owners to claim the credit on their own returns."),
     "notes": "A hard sequencing dependency between the entity return and every owner's Form 760."},
    {"diagnostic_id": "D_VAPTET_CORPORATE_PENALTIES", "severity": "info",
     "title": "PTET penalties are CORPORATE - a Form 502 penalty engine will be wrong here",
     "condition": "return filed late or underpaid",
     "message": ("Form 502PTET penalties run under Article 14 (Virginia Code Section 58.1-450 et seq.), the "
                 "corporate regime, instead of the Article 9 pass-through penalties: extension penalty 2% per "
                 "month where less than 90% is paid by the original due date; late payment 6% per month capped at "
                 "30%; late filing 30% of tax due with a $100 MINIMUM THAT APPLIES WHETHER OR NOT TAX IS DUE. The "
                 "late payment penalty does not apply to the extent the late filing penalty applies. Interest runs "
                 "at IRC Section 6621 plus 2% from the original due date. Contrast Form 502, whose late filing "
                 "penalty is a flat $1,200."),
     "notes": "A single PTE penalty engine will be wrong on one of the two paths."},
    {"diagnostic_id": "D_VAPTET_U8_PTETADJ_PART2", "severity": "info",
     "title": "Schedule PTET ADJ Part II has no readable label on the final form",
     "condition": "Schedule PTET ADJ Section C Part II completed",
     "message": ("The Part II row on the FINAL Schedule PTET ADJ extracts as blank where Schedule 502ADJ prints "
                 "its enumerated formula. This product presumes Part II is identical to Schedule 502ADJ Part II - "
                 "'Add Part I, Lines 1-8, 12-15, 17, 21, 23, and 25 through 27' - with the Form 502PTET Page 1 "
                 "Line 19 reference substituted, which matches Line 19's own label. PRESUMED, NOT READ. Verify "
                 "against the rendered form. Note also that the DOR prints the Section C heading with a typo "
                 "('Virgnia Tax Credits') on both pages - do not transcribe it."),
     "notes": "U8(a) - reproduced independently during verification."},
    {"diagnostic_id": "D_VAPTET_EFILE_ONLY_POLICY", "severity": "warning",
     "title": "Form 502PTET is e-file only as a POLICY default",
     "condition": "paper filing indicated",
     "message": ("Form 502PTET and all associated schedules must be filed through the Federal/State e-File "
                 "program or the Department's Online Services for Businesses, and the instruction package states "
                 "that paper submissions will not be accepted and waivers will not be granted. However, Virginia "
                 "Code Section 58.1-392 E provides that waivers of the pass-through entity electronic filing "
                 "requirement SHALL be granted where the Tax Commissioner finds an unreasonable burden, and "
                 "Section 58.1-390.3 A.2 makes Form 502PTET a Section 58.1-392 return - so the waiver machinery "
                 "reaches it. The Department's own Electronic Filing Requirements page lists Form 502PTET and "
                 "PTET-PMT under a page-level hardship waiver with no carve-out. Treat e-file-only as policy, not "
                 "as a legal impossibility."),
     "notes": "W7 / U11, stated per the verification pass. Also: the federal return must be a LINKED return on "
              "this path - 'Do not attach PDFs to the Form 502PTET submission' - which is stricter than Form 502."},
]

VAPTET_SCENARIOS: list[dict] = [
    {"scenario_name": "PTET base diverges from Form 502 Line 1", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"wk_ordinary_income": 1000000, "l1_no_double_count_confirmed": True, "total_deductions": 150000,
                "sec179_as_filed": 100000, "sec179_ccorp_limit": 60000,
                "charitable_as_filed": 50000, "charitable_ccorp_limit": 30000, "eligible_owner_pct": 1.0},
     "expected_outputs": {"form502_L1": 1000000.0, "ptet_section_I_L1": 910000.0},
     "notes": "Form 502 Line 1 = 1,000,000 (income only). PTET Section I Line 1: allowed deductions = other "
              "(150,000 - 100,000 - 50,000 = 0) + min(100,000, 60,000) + min(50,000, 30,000) = 90,000; base = "
              "1,000,000 - 90,000 = 910,000. Same facts, two different bases."},
    {"scenario_name": "5.75% tax with a per-column floor blocking offset", "scenario_type": "edge", "sort_order": 2,
     "inputs": {"col_a_L1": 500000, "eligible_additions_col_a": 20000, "eligible_subtractions_col_a": 0,
                "col_b_L1": -100000, "eligible_additions_col_b": 0, "eligible_subtractions_col_b": 50000},
     "expected_outputs": {"I-5A": 520000.0, "I-5B": 0.0, "II-6": 520000.0, "II-7a": 29900.0},
     "notes": "Column A: 500,000 + 20,000 = 520,000, no subtractions, Line 5A = 520,000. Column B: -100,000 + 0 = "
              "-100,000, less 50,000 = -150,000, floored to ZERO. Line 6 = 520,000 (the resident loss does NOT "
              "reduce it). Line 7a = 520,000 x 5.75% = 29,900."},
    {"scenario_name": "Line 7 = 7a plus the corporate withholding leg", "scenario_type": "normal", "sort_order": 3,
     "inputs": {"II-6": 520000, "nonres_corporate_va_source_share": 200000,
                "owners_nonres_corporate_withholding": 2},
     "expected_outputs": {"II-7a": 29900.0, "II-7b": 10000.0, "II-7": 39900.0, "credit_to_owners": 29900.0},
     "notes": "Line 7a = 29,900; Line 7b = 200,000 x 5% = 10,000 (W4 - the 5% is inferred from Form 502 / "
              "s.58.1-486.2; the PTET package states no rate). Line 7 = 39,900. But the credit passed to owners "
              "is keyed to 7a = 29,900, NOT 39,900."},
    {"scenario_name": "Late filing penalty applies with a $100 minimum on zero tax", "scenario_type": "edge", "sort_order": 4,
     "inputs": {"tax_due": 0, "is_late": True},
     "expected_outputs": {"late_filing_penalty": 100.0, "penalty_on_10000_tax": 3000.0},
     "notes": "30% of zero is zero, but 'In no case will the penalty for failure to file timely be less than "
              "$100, and this minimum $100 penalty applies whether or not tax is due.' On 10,000 of tax the "
              "penalty is 3,000. Contrast Form 502's flat $1,200 late-filing penalty."},
    {"scenario_name": "Estimated payments - the $1,000 threshold and 25% instalments", "scenario_type": "normal", "sort_order": 5,
     "inputs": {"expected_ptet_liability": 40000},
     "expected_outputs": {"estimates_required": True, "installment": 10000.0, "not_required_at_1000": False},
     "notes": "40,000 exceeds $1,000, so estimates are required: four instalments of 25% = 10,000 each, due "
              "April 15 / June 15 / September 15 / December 15 for a calendar-year filer. At exactly $1,000 the "
              "test fails - the threshold is 'reasonably expected to EXCEED $1,000'."},
    {"scenario_name": "The 6-month hard bar and its only escape", "scenario_type": "failure", "sort_order": 6,
     "inputs": {"months_after_original_due_date": 8, "made_estimated_or_extension_payment": False},
     "expected_outputs": {"election_permitted": False, "permitted_if_payment_made": True},
     "notes": "Filed 8 months after the original due date with no estimated or extension payment - Form 502PTET "
              "may not be filed at all; file Form 502 instead. Had an estimated or extension payment been made, "
              "the election survives. This is a validation rule, not a penalty."},
    {"scenario_name": "No sunset - the statute governs the re-issued form text", "scenario_type": "edge", "sort_order": 7,
     "inputs": {"tax_year": 2025},
     "expected_outputs": {"sunset_year": None, "stale_recitals_in_package": 6},
     "notes": "Va. Code s.58.1-390.3 carries no expiration date; the Rev. 08/26 package re-issued 2026-08-10 "
              "still recites the repealed sunset six times. Build to the statute - no sunset is encoded."},
    {"scenario_name": "Two due-date clocks coexist", "scenario_type": "edge", "sort_order": 8,
     "inputs": {"tax_year": 2025},
     "expected_outputs": {"VA_502": [4, 15], "VA_502PTET": [4, 15], "VA_760": [5, 1], "VA_770": [5, 1]},
     "notes": "Entity returns are on the 15th day of the 4th month (Va. Code s.58.1-392 A); Form 760 and Form 770 "
              "are on May 1. A single Virginia due-date constant is wrong on one side or the other. Neither "
              "extension extends the PAYMENT date."},
]


# ===========================================================================
# FORMS registry + flow assertions
# ===========================================================================

FORMS: list[dict] = [
    {
        "identity": {
            "form_number": "VA_502",
            "form_title": "VA Form 502 - Virginia Pass-Through Entity Return of Income and Return of Nonresident Withholding Tax (TY2025)",
            "entity_types": FORM_ENTITY_TYPES,
            "notes": (
                "TWO RETURNS IN ONE DOCUMENT: an INFORMATION return of income (Page 1) and a TAX return for "
                "nonresident withholding (Page 2). Virginia has no separate partnership and S-corporation "
                "returns - Form 502 is filed by both, so entity_types covers 1065 AND 1120S and the module "
                "branch lives in six places only (entity type code, owner-count source, participation-% "
                "source, participation type code, federal enclosure, and the S-corp-only bank franchise "
                "consequence). PAGE 1 COMPUTES NO TAX - the PTE is not a taxpayer; the build ends at Line 20. "
                "LINE 1 IS INCOME ONLY and is NOT reduced by Line 2 - it is what flows to Schedule 502A "
                "Section C Line 1 and drives apportionment. Apportionment is THREE FACTORS WITH DOUBLE-WEIGHTED "
                "SALES DIVIDED BY FOUR, not single sales factor, and non-TPP sales are sourced by COST OF "
                "PERFORMANCE. Conformity routing: bonus depreciation on Lines 8/14, the disposed-asset true-up "
                "on Lines 9(1)/15(1), and a RESIDUAL CONFORMITY BUCKET WIDER THAN H.R.1 on Lines 9(2)/15(2). "
                "VIRGINIA PUBLISHES NO SECTION 179 DOLLAR FIGURE - none is seeded. Page 2 carries the 5% "
                "nonresident withholding return with a PER-OWNER zero floor, the Extension Penalty Worksheet, "
                "a flat $1,200 late-filing penalty, and Line 10's FOUR-BRANCH conditional. Mutually exclusive "
                "with Form 502PTET."
            ),
        },
        "facts": VA502_FACTS, "rules": VA502_RULES, "rule_links": VA502_RULE_LINKS,
        "lines": VA502_LINES, "diagnostics": VA502_DIAGNOSTICS, "scenarios": VA502_SCENARIOS,
    },
    {
        "identity": {
            "form_number": "VA_502PTET",
            "form_title": "VA Form 502PTET - Virginia Pass-Through Entity Elective Income Tax Return (TY2025)",
            "entity_types": FORM_ENTITY_TYPES,
            "notes": (
                "Filed INSTEAD OF Form 502 by an electing PTE; the two are mutually exclusive and a second "
                "return for the year must be amended with Reason Code 05. Serves BOTH modules. PAGE 1 LINES "
                "1-20 ARE IDENTICAL TO FORM 502 (only 'Schedule PTET ADJ' replaces 'Schedule 502ADJ') and are "
                "whole-entity; the eligible-owner narrowing happens on Page 2. *** THE BASE DIVERGES: Form 502 "
                "Line 1 is income only, but Form 502PTET SECTION I LINE 1 is income NET OF DEDUCTIONS with "
                "Section 179 and charitable contributions RE-LIMITED to the federal C-CORPORATION limits - an "
                "entity-level pro-forma recomputation with no federal analogue. *** Section I is a two-column "
                "build (nonresident / resident eligible owners) with a PER-COLUMN zero floor at Line 5 and a "
                "second floor at Line 6; Line 7a = Line 6 x 5.75%; Line 7 = 7a + 7b, where 7b is a "
                "nonresident-CORPORATE withholding leg whose 5% rate the package never states (W4/U3). The "
                "credit passed to owners is keyed to LINE 7a, NOT Line 7, is REFUNDABLE, and cannot be "
                "re-allocated by an estate or trust to its beneficiaries. Penalties run under the CORPORATE "
                "Article 14 regime, with a $100 minimum late-filing penalty that applies whether or not tax is "
                "due. Estimates required above $1,000. A 6-MONTH HARD BAR REFUSES the return unless estimated "
                "or extension payments were made. NO SUNSET IS ENCODED - the statute has none, and the "
                "re-issued Rev. 08/26 package's six sunset recitals are dead text."
            ),
        },
        "facts": VAPTET_FACTS, "rules": VAPTET_RULES, "rule_links": VAPTET_RULE_LINKS,
        "lines": VAPTET_LINES, "diagnostics": VAPTET_DIAGNOSTICS, "scenarios": VAPTET_SCENARIOS,
    },
]

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-VA-MODULE-BR", "title": "One form, two modules - the branch is in six places only",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 1,
     "description": ("Form 502 Lines 1-20 are identical for a partnership and an S corporation. The module branch "
                     "is confined to: the entity type code (SC for 1120S), the owner-count source (1065 Page 1 "
                     "item I vs 1120-S Page 1 item I), the participation-percentage source (1065 K-1 item J ending "
                     "profit % vs 1120-S K-1 item G as printed), the participation type code (SHR for 1120S), the "
                     "required federal enclosure, and the S-corp-only bank franchise consequence."),
     "definition": {"rule": "R-VA-MODULE", "check": "branch(1065) != branch(1120S) in exactly 6 named fields"}},
    {"assertion_id": "FA-VA-BASE-SPLIT", "title": "Form 502 Line 1 != Form 502PTET Section I Line 1",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 2,
     "description": ("Form 502 Line 1 is income only and is never reduced by Line 2 deductions. Form 502PTET "
                     "Section I Line 1 INCLUDES deductions, with IRC 179 and charitable contributions re-limited "
                     "to the amounts allowed to a federal C corporation. Given the same Schedule K, the two "
                     "figures must differ whenever deductions are non-zero."),
     "definition": {"rule": "R-VAP-BASE",
                    "check": "ptet_section_I_L1 = (income - allowed_deductions) x eligible_pct != form502_L1"}},
    {"assertion_id": "FA-VA-VK1-SUM", "title": "Sum of VK-1 lines equals the corresponding Form 502 line",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 3,
     "description": ("For n in {1,2,3,4,5,6,8,9,10,11,13,18} the sum of Schedule VK-1 Line n over all owners "
                     "equals Form 502 Line n. Also: the sum of VK-1 Line e equals Form 502 Line c, and the sum of "
                     "VK-1 Line d equals 100.00%."),
     "definition": {"rule": "R-VA-VK1", "check": "sum(VK1[n]) == Form502[n] for n in mirror_lines"}},
    {"assertion_id": "FA-VA-VK1-L7", "title": "VK-1 Line 7 is the same for every owner and is never summed",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 4,
     "description": ("Line 7 is the PTE's Virginia apportionment percentage. Every owner's Schedule VK-1 carries "
                     "the SAME Line 7 value, equal to Form 502 Line 7. Summing it across owners is always wrong."),
     "definition": {"rule": "R-VA-VK1", "check": "all(VK1[i].L7 == Form502.L7) and never sum(VK1.L7)"}},
    {"assertion_id": "FA-VA-VK1-PIII10", "title": "VK-1 Part IV includes Line 10 on BOTH paths; 502ADJ Part IV does not",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 5,
     "description": ("Schedule VK-1 carries the Part III Line 10 PTET credit slot and totals Part IV as 'Lines 1, "
                     "7, 9, and 10' on the NON-PTET path too, while Schedule 502ADJ Part IV is 'Lines 1, 7, and "
                     "9'. A totals-level equality assertion breaks the moment Line 10 is non-zero - assert per "
                     "line, never on the totals."),
     "definition": {"check": "sum(VK1.PartIV) != 502ADJ.PartIV when VK1.PartIII.L10 != 0"}},
    {"assertion_id": "FA-VA-WH-5PCT", "title": "Withholding is 5% per nonresident owner, floored at zero PER OWNER",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 6,
     "description": ("Form 502 Page 2 Line 1 = sum over nonresident owners of max(0, 5% x the owner's "
                     "Virginia-source share, day-count prorated for part-year owners, less credits passed through "
                     "to that owner). The zero floor is applied per owner BEFORE the total is struck, so an "
                     "over-credited owner can never reduce another owner's withholding."),
     "definition": {"rule": "R-VA-WH-OWNER",
                    "check": "P2L1 == sum(max(0, share*0.05 - credits) per nonresident owner)"}},
    {"assertion_id": "FA-VA-PTET-CREDIT", "title": "PTET ADJ C-III-10 = Form 502PTET Line 7a = sum of VK-1 Part III Line 10",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 7,
     "description": ("The elective tax credit passed through to eligible owners is keyed to Section II LINE 7a, "
                     "not Line 7 - the nonresident corporate withholding leg on Line 7(b) is excluded. The "
                     "owner-side credit is refundable under Va. Code s.58.1-390.3 E."),
     "definition": {"rule": "R-VAP-CREDIT", "check": "PTETADJ_C_III_10 == PTET_L7a == sum(VK1.PartIII.L10)"}},
    {"assertion_id": "FA-VA-PTET-FLOOR", "title": "The Section I zero floor is per column, then again at Line 6",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 8,
     "description": ("Line 5 is floored at zero in Column A and Column B independently, and Line 6 is floored "
                     "again after summing. A resident-column loss can never offset nonresident-column income."),
     "definition": {"rule": "R-VAP-SEC-I", "check": "L5col = max(0, L3col - L4col) per column; L6 = max(0, L5A + L5B)"}},
    {"assertion_id": "FA-VA-APPORT-DIV4", "title": "Apportionment is three factors, sales doubled, divided by four",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 9,
     "description": ("2(d) = 2(c) x 2; 2(e) = 2(a) + 2(b) + 2(d); 2(f) = 2(e) divided by four, reduced when a "
                     "factor has no denominator - the divisor being the sum of the weights of the factors that "
                     "exist (property 1, payroll 1, sales 2). Virginia is NOT a single sales factor state for "
                     "PTEs, and the PTE rule does not differ from the corporate rule."),
     "definition": {"rule": "R-VA-502AB", "check": "L7 == (P + Y + 2S) / weight_sum_of_existing_factors"}},
    {"assertion_id": "FA-VA-502A-NO-PCT", "title": "Schedule 502A Section C has NO percentage-application line",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 10,
     "description": ("Section C stops at allocable and apportionable income (Lines 1-4) and pushes three figures "
                     "to Form 502 Lines 4, 5 and 6. Schedule 500A has no Section C at all and applies the "
                     "percentage on the schedule itself. Cloning 500A Section B Line 3 into the PTE spec invents "
                     "lines that do not exist."),
     "definition": {"rule": "R-VA-502AC", "check": "no line on 502A multiplies income by the apportionment percentage"}},
    {"assertion_id": "FA-VA-CONFORM-BKT", "title": "Conformity routing - bonus to 8/14, the residual bucket to 9(2)/15(2)",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 11,
     "description": ("Lines 8/14 are textually scoped to bonus depreciation vintages 2001-2025 and nothing else. "
                     "Lines 9(1)/15(1) carry the disposed-asset basis true-up. Lines 9(2)/15(2) are a RESIDUAL "
                     "conformity bucket WIDER THAN H.R.1 - the word 'other' is what excludes bonus. The bucket "
                     "must never be labelled an 'H.R.1 line'."),
     "definition": {"rule": "R-VA-CONFORM",
                    "check": "line('bonus')=='8/14'; line('174A')=='9(2)/15(2)'; bucket_members > hr1_members"}},
    {"assertion_id": "FA-VA-179-NONE", "title": "No Virginia Section 179 figure is seeded",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 12,
     "description": ("Virginia has published no IRC 179 dollar limit and no phase-out threshold. The loader seeds "
                     "None as the Virginia value; the 1,250,000 / 3,130,000 / 31,300 figures live in a separately "
                     "named DERIVED constant citing Rev. Proc. 2024-40 s.3.25, and the federal OBBBA 2,500,000 / "
                     "4,000,000 amounts must never be used for Virginia."),
     "definition": {"rule": "R-VA-179",
                    "check": "VA_179_PUBLISHED[2025] is None and derived != federal_obbba"}},
    {"assertion_id": "FA-VA-DUE-CLOCKS", "title": "Two Virginia due-date clocks coexist",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 13,
     "description": ("Form 502 and Form 502PTET are due on the 15th day of the 4th month (Va. Code s.58.1-392 A); "
                     "Form 760 / 760PY / 763 / 770 are due May 1. Both are true for TY2025. The extension never "
                     "extends the payment date for withholding or PTET."),
     "definition": {"rule": "R-VA-DUE",
                    "check": "due('VA_502')==(4,15) and due('VA_760')==(5,1) and not payment_extends"}},
    {"assertion_id": "FA-VA-MUTEX-502", "title": "Form 502 and Form 502PTET are mutually exclusive filings",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 14,
     "description": ("An electing PTE submits Form 502PTET INSTEAD OF Form 502. If either has been filed for the "
                     "year, a subsequent return must be marked amended - Reason Code 05 for a Form 502PTET amended "
                     "return. An electing PTE also may not file Form 765."),
     "definition": {"rule": "R-VA-GATES", "check": "exactly one of {VA_502, VA_502PTET} per entity per tax year"}},
    {"assertion_id": "FA-VA-NO-SUNSET", "title": "The PTET carries no sunset - the statute governs the form text",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 15,
     "description": ("Va. Code s.58.1-390.3 contains no expiration date. The Rev. 08/26 package, re-issued "
                     "2026-08-10, still recites the repealed 'before January 1, 2027' sunset six times, and the "
                     "Form 502 instruction book contradicts itself between page 1 and page 3. No sunset is "
                     "encoded; a diagnostic explains the dead form text."),
     "definition": {"rule": "R-VAP-SUNSET", "check": "VA_PTET_SUNSET_YEAR[2025] is None"}},
]


# ===========================================================================
# Command
# ===========================================================================

class Command(BaseCommand):
    help = (
        "Load the VA PTE specs (VA_502 + VA_502PTET, Virginia pass-through entity returns, TY2025). "
        "ONE loader, TWO form codes, BOTH serving the 1065 and 1120S modules. Refuses to seed until "
        "Ken sets READY_TO_SEED=True after the Gate-1 review walk (W1-W11)."
    )

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad VA PTE specs (VA_502 + VA_502PTET, Virginia pass-through entity returns)\n"))
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
                "\nREFUSING TO SEED VA PTE SPECS: not cleared to seed.\n\n"
                "Content is authored, but seeding is gated until Ken walks the packet\n"
                "and flips the sentinel:\n"
                "  W1  one spec or two - taken as TWO form codes sharing a Page-1 rule block\n"
                "  W2  *** the residual conformity bucket routes to Lines 9(2)/15(2), of which\n"
                "         H.R.1 is ONE COMPONENT - not an 'H.R.1 line' (correction C1)\n"
                "  W3  *** VIRGINIA PUBLISHES NO SECTION 179 FIGURE - none is seeded; the\n"
                "         1,250,000/3,130,000/31,300 amounts are DERIVED, not Virginia numbers\n"
                "  W4  *** the 5% on Form 502PTET Line 7(b) is inferred from a DIFFERENT FORM\n"
                "         and it moves money\n"
                "  W5  Virginia depreciation shadow book: v1 direct-entry Lines 8/9/14/15\n"
                "  W6  compute the withholding leg; RED-defer only the tiered-PTE case\n"
                "  W7  PTET e-file waiver = POLICY default, never a legal invariant (s.58.1-392 E)\n"
                "  W8  credit allocation computed; credit amounts direct-entry; two classes kept\n"
                "  W9  the Form 502 Line 1 build is a real visible worksheet with the DOR Caution\n"
                "  W10 the TWO due-date clocks provably coexist (entity 4th month; 760/770 May 1)\n"
                "  W11 Form 502FED-1 / 502FED-2 deferred (1065 module only)\n\n"
                f"READY_TO_SEED = {READY_TO_SEED} (must be True to proceed)\n\n"
                f"Currently empty / placeholder:\n  {still_empty}\n\n"
                "To proceed: review the module-level data lists (and\n"
                "delvio-states/research/va_pte_source_brief.md, whose Sec.16 Verification\n"
                "section governs), then set READY_TO_SEED = True. Idempotent via\n"
                "update_or_create.\n"
                "NOTE: TY2025 ONLY. Every figure is TY-keyed; a new tax year\n"
                "staleness-invalidates the brief until re-verified."
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
                # The VA Tier-1 conformity rows ARE seeded in prod, so this should not fire
                # there. It WILL fire on a throwaway SQLite harness DB, which is expected.
                self.stdout.write(self.style.WARNING(
                    f"  existing source {code} NOT FOUND - links to it will be skipped "
                    "(expected only on a fresh/throwaway DB; VA Tier-1 conformity is seeded in prod)"))
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
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("VA PTE specs loaded (TY2025 ONLY - every figure is TY-keyed).")
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
        self.stdout.write("=" * 60)
