"""Load the MD_510 + MD_511 specs — Maryland Pass-Through Entity returns (TY2025).

═══════════════════════════════════════════════════════════════════════════
WHAT THIS IS
═══════════════════════════════════════════════════════════════════════════
Maryland does NOT have a partnership return and an S-corp return. It has
**two mutually exclusive returns split on an election**, each of which serves
partnerships, S corporations, LLCs and business trusts alike:

  • Form 510 — NON-ELECTING PTE. Mandatory nonresident tax only:
    6.50% + 2.25% on nonresident individual/fiduciary members' Maryland shares,
    8.25% on nonresident ENTITY members' shares. Resident members untaxed.
  • Form 511 — ELECTING PTE ("Electing PTE tax", Maryland's PTET). 8.75% on ALL
    individual/fiduciary members (resident AND nonresident), 8.25% on ALL entity
    members (resident AND nonresident).

TWO FORM CODES IN ONE LOADER (campaign D-9 namespacing): MD_510, MD_511. They
are authored as **two genuinely separate specs**, not one spec with a branch
flag — they have different bases, different rate structures, different member
classification maps, different DCF worksheets, different payment blocks and
different owner-side consequences.

Spec source: delvio-states/research/md_pte_source_brief.md — **VERIFIED
(adversarial pass 2026-08-17)**; its §15 Verification supersedes the body.
Conformity: delvio-states/conformity/md_conformity.md (VERIFIED 2026-08-06).

═══════════════════════════════════════════════════════════════════════════
THE FOUR THINGS MOST LIKELY TO BE BUILT WRONG
═══════════════════════════════════════════════════════════════════════════
1. **THE ELECTION IS NOT DERIVABLE FROM THE RETURN.** Box A / Box B is checked
   on the FIRST filing of the tax year — Form 510/511D (estimated) or Form
   510/511E (extension) — months before the return exists. It is IRREVOCABLE
   and may not be changed on an amended return. TWO DEEMING DEFAULTS: first
   filing with NEITHER box → deemed Form 510 (non-electing), irrevocably;
   first filing with BOTH boxes checked in error → deemed Form 511 (electing),
   irrevocably. If no D or E was filed, the year-end return ITSELF is the
   election. **Nothing on the return's own data reveals which applies** — so
   the spec takes it as a REQUIRED input and raises an ERROR diagnostic when it
   cannot be determined. It NEVER infers the election from computed values.
2. **THE SAME MEMBER LANDS IN DIFFERENT BOXES.** A Maryland-RESIDENT ENTITY
   member sits on Form 510 line 1d ("Others") and is UNTAXED; on Form 511 it
   sits on line 1c ("Nonresident **and resident** entities") and is taxed at
   8.25%. Same member, same PTE, different box, different tax. Fiduciaries sit
   inside the INDIVIDUAL legs (1a/1b), never the entity legs.
3. **THE TWO DCF WORKSHEETS DIFFER.** Worksheet 9A (Form 510) multiplies
   distributable cash flow by the NONRESIDENT OWNERSHIP PERCENTAGE (lines J/K);
   Worksheet 11A (Form 511) has NO ownership step. And the lesser-of on 510 L15
   / 511 L12 is **CONDITIONAL on the worksheet checkbox** — an unconditional
   MIN() zeroes the tax whenever the line is left blank.
4. **THE OWNER SIDE IS TWO LEGS.** Credit (§10-701.1) PLUS a mandatory income
   ADD-BACK — and the add-back attaches to Schedule K-1 Section D lines **2 and
   4 ONLY** (the 511 legs). It does **NOT** attach to D1 (the 510 nonresident
   tax), because §10-102.1(c)(1) already treats that as the member's own tax
   paid on their behalf. Credit-without-add-back overstates owner relief by the
   full PTET; adding back D1 double-taxes every nonresident partner.

═══════════════════════════════════════════════════════════════════════════
⚠ APPORTIONMENT — MARYLAND HAS **NO** INSIGNIFICANT-DENOMINATOR RULE
═══════════════════════════════════════════════════════════════════════════
The wave premise that Maryland carries a Florida-style rule dropping or
reweighting a factor whose denominator is "zero or determined to be
insignificant" is **FALSE**. That rule is **Fla. Stat. §220.15(1)**. The
verification pass searched Forms 510/511/510C/510-511D/510-511E, Schedule K-1,
Form 500DM, both PTE booklets, the Corporate Booklet, Tax-General §§10-102.1,
10-105, 10-106.1, 10-210.1, 10-306, 10-310, 10-401, 10-402, 10-701.1, COMAR
03.04.03.08/.09/.10 and Administrative Release 43 — **zero hits**, re-tested
against the synonyms "de minimis", "omit", "eliminat", "disregard", "not
material", "nominal" and "zero".

Maryland's ACTUAL convention is the OPPOSITE: a zero factor is **floored at
.000001**, not eliminated — `(If factor is zero, enter .000001)` on the Form
510 and Form 511 faces at line 3b and Schedule A line 4 (a FORM-FACE rule; it
appears in neither booklet). COMAR 03.04.03.08 B(5) additionally requires a
factor to be computed even on a loss return. And **only the Comptroller may
alter a formula** — §10-402(e) ("the Comptroller may alter ... the weight of
any factor"), §10-401(2) ("the method that the Comptroller requires"), and the
booklets' Alternative Apportionment instruction. **The software must NEVER
auto-drop, auto-reweight or auto-substitute a factor.** (W9.)

═══════════════════════════════════════════════════════════════════════════
v1 SCOPE — COMPUTES / DIRECT-ENTRY / RED-DEFER (brief §11; FOR KEN'S WALK)
═══════════════════════════════════════════════════════════════════════════
COMPUTES (v1):
  • The ELECTION STATE MACHINE — Box A/B carried from the first 510/511D or
    510/511E; both deeming defaults; the year-end-return-as-election path; the
    irrevocability lock; a hard block on filing the contradicting year-end
    form; the amended-return bar. Year-keyed (the "first filing wins" rule is
    suspended for TY2026 only).
  • The MEMBER-CLASSIFICATION MATRIX, keyed on (form, member kind, residency),
    with the resident-entity divergence.
  • MD_510: L2 federal base → L3a/L3b allocation → L4 → L5–L13 nonresident tax
    (6.50% + 2.25% + 8.25%) → worksheet 9A → conditional L15 → L16a–16h →
    L17–L22.
  • MD_511: L2 federal base + SALT add-back → L3a/L3b (EVERY multistate PTE) →
    L4 → L5a/5b/5c → L6–L10 (8.75% / 8.25%) → worksheet 11A → conditional L12 →
    L13a–13f → L14–L19.
  • Schedule A apportionment factor to SIX decimals; the .000001 zero floor.
  • Schedule B per-member shares off **line 2, not line 4**.
  • Schedule K-1 (510/511) Section D legs (D1 vs D2/D4) and Section H column 2
    = column 1 × the Maryland apportionment factor.
  • The PTET rate as a YEAR-KEYED DERIVATION with both statutory inputs cited
    (§10-105(a) top marginal 6.50% + §10-106.1 lowest county 2.25% = 8.75%;
    §10-105(b) 8.25%) and a staleness assertion — never a hardcoded 0.0875.

DIRECT-ENTRY (line exists; each with a diagnostic prompt):
  • Schedule A numerators/denominators (1a–1g, 2a–2f, 3a–3b, both columns).
  • Line 3a separate-accounting amount (S corps only if nonunitary).
  • Ownership percentages (510 L5/L10 — "If 100%, leave blank"; 511 L5a/L5b —
    "expressed as a decimal. If 100%, enter 9999"). The two conventions DIFFER.
  • Both DCF worksheets' inputs B–E and G–H.
  • Schedule B per-member rows; K-1 Sections B, C, E, F, G; Section H column 1.
  • MW506NRS payments; Form 500UP interest/penalty.
  • Page-3 questions 1–8 including Q8 (INFORMATIONAL ONLY).
  • Code numbers 704 / 705 / 301 (no published master list — U12).
  • The NAICS 31–33 manufacturing-entity attribute (no form line captures it).

RED-DEFER — each gets its OWN "prepare manually" diagnostic, no silent gap:
  R1 Form 510C composite · R2 Special Apportionment Formula · R3 Alternative
  Apportionment Formula · R4 Form 500CR / 502S business credits · R5 One
  Maryland Economic Development Tax Credit · R6 Form 500 for an S corp with
  federal corporate-level tax (1120-S L23a/23b) · R7 Form 500UP · R8 Form
  MW506NRS · R9 the entity's own Form 500DM · R10 the §10-210.1 manufacturing
  carve-out · R11 tiered-PTE credit chains beyond one level · R12 publicly
  traded partnerships (code 704) · R13 investment partnerships (code 705) ·
  R14 Form EL102B (composite extension) · R15 §501 PTE with federal taxable
  income.

═══════════════════════════════════════════════════════════════════════════
requires_human_review WALK ITEMS (Ken's Gate-1 walk, before seeding)
⚠ W3 IS WITHDRAWN — DO NOT RE-RAISE IT. See the note after W11.
═══════════════════════════════════════════════════════════════════════════
W1. THE ELECTION IS SET BY A FORM FILED MONTHS EARLIER, IS IRREVOCABLE, AND
    HAS TWO DEEMING DEFAULTS. Nothing on the year-end return reveals it.
    Ken's call: WHERE the election state lives (return-level flag vs
    client-level attribute vs a first-filing record). Encoded here as a
    REQUIRED fact plus an ERROR diagnostic when undetermined.
W2. THE §10-210.1 MANUFACTURING CARVE-OUT HAS NO PRINTED FORM LINE ANYWHERE.
    NAICS **2012 Edition** Sectors **31/32/33**, refiners excluded, property
    placed in service **on or after 1/1/2019** → both the §168(k) and the §179
    add-backs switch OFF. Zero occurrences across every TY2025 PTE document.
    Built here as a spec-level entity attribute, RED-deferred (R10), and
    EXPLICITLY DISCONNECTED from page-3 question 8. R10's diagnostic wording
    is the only place the carve-out lives in the product — it needs Ken's
    words, not developer prose. It does NOT reach §10-210.1(b)(5) heavy-duty
    SUVs.
W4. OWNER SIDE IS TWO LEGS AND ONLY THE 511 LEGS CARRY THE ADD-BACK — K-1
    Section D lines 2 and 4 only, NEVER D1. Emitted here as a typed
    modification so the 1040/1120/1041 modules cannot drop it. Ken to decide
    whether this wave or the owner-side wave owns the consuming end.
W5. THE DCF CAP IS A CONDITIONAL LESSER-OF AND THE TWO WORKSHEETS DIFFER
    (9A scales by nonresident ownership %; 11A does not).
    ⚠ W5(a) — the brief transcribes worksheet line F verbatim as `Total. (Add
    lines B through E.)` on BOTH worksheets, which omits line A (the income
    base) from the total. Encoded EXACTLY as the brief states it, behind the
    constant MD_DCF_F_INCLUDES_LINE_A = False. **Do not "fix" this by
    inference** — confirm against the printed worksheet at the walk and flip
    the one constant if Ken rules otherwise.
    ⚠ W5(b) — md_conformity.md §4's "Cannot be elected on an amended return"
    is UNSUPPORTED in every TY2025 source (U7). NOT encoded. Ken to rule.
W6. THE RESIDENT ENTITY MEMBER MOVES BOXES between the two forms (510 line 1d
    untaxed → 511 line 1c taxed at 8.25%). Fiduciaries sit in the INDIVIDUAL
    legs. Encoded as one classification matrix keyed on (form, member kind,
    residency), with a cross-foot assertion against Schedule B Parts I–IV.
W7. K-1 SECTION H IS A MANDATORY REPORTING OBLIGATION WITH NO TAX LINE. New
    for TY2025, on both forms, feeding members' Forms 502CG/504CG. Column 2 =
    column 1 × the Schedule A factor. Row 3 is resident-members-only. ⚠ The
    instruction misprints IRC §408/§408A as "§458/§458A" — encoded against the
    statute and TB 58, erratum recorded. Confirm a mandatory-but-untaxed
    schedule gets the same completeness treatment as a tax line.
W8. FORM 510C PRINTS ONE AGGREGATE 8.75% MULTIPLICATION (line 11), not a
    per-member loop — correcting md_conformity.md §4's framing (same rate,
    different arithmetic). RED-deferred (R1); the corrected arithmetic is
    recorded so a later build does not clone a per-member design. TB 6 is
    TY2023-keyed and must be re-pulled before the composite is built.
W9. APPORTIONMENT: NEVER AUTO-REWEIGHT. Maryland has no insignificant-
    denominator rule (U11 — a thorough negative, re-tested with synonyms). It
    has the opposite: a zero factor is entered as .000001, and a factor must be
    computed even on a loss return. Altering a formula is the COMPTROLLER's
    act. Ken to bless the negative as a RULING, not a finding.
W10. AN S CORP WITH FEDERAL CORPORATE-LEVEL TAX FILES TWO MARYLAND RETURNS —
    Form 500 (line 1 = total taxable income, box "Other" = "1120S") AND Form
    510/511. Trigger: 1120-S line 23a/23b. The booklets say "also file Form
    510" and are SILENT on the 511 case. RED-deferred (R6); ask Ken whether the
    product should surface the 511-plus-500 combination the booklets omit.
W11. FOUR+TWO COMPTROLLER ERRATA TO RECORD RATHER THAN "FIX" — build to the
    FORM FACES in every case:
    (a) Booklet 510's `1b or 1d` line-5–19 gate vs the face's `1b or 1c` (U4);
    (b) both booklets' amended-payment line pointers (16b/13d) vs the faces
        (16g/13e) (U5);
    (c) K-1 Section D line 4's `Form 511, Line 13C` cross-reference, which
        should be Form 510 lines 16d/16e (U3);
    (d) Form 500DM's three citations to a NONEXISTENT "Technical Bulletin No.
        38" — the document is Administrative Release No. 38 (U10);
    (e) Form 511's line-17 NOTE points members at "the composite return"
        although Booklet 511 bars an Electing PTE from filing Form 510C;
    (f) Form 511's line-4 NOTE says `Investment partnerships see Specific
        Instructions` but Booklet 511 has no such instruction and never
        mentions code 705.

⚠⚠ **W3 IS WITHDRAWN — DO NOT RE-RAISE IT.** The research pass alleged that
Form 511 line 4 apportions a RESIDENT member's base while §10-102.1(a)(8)(i)
says it should not. **That was a FALSE CONFLICT.** The (i)/(ii) resident-vs-
nonresident split it quoted is the **2025 BRFA (2025 Md. Laws Ch. 604)**
amendment, which mgaleg serves as CURRENT code. That amendment **never applied
to TY2025**, and the **2026 BRFA (2026 Md. Laws Ch. 6 §4) postponed it to
TY2027**. The operative TY2025 definition (SB 787 of 2021) is quoted verbatim
in **Technical Bulletin No. 6 §I.A/§I.B** and is Maryland-source **for all
members**, with `Multistate electing PTEs must apportion their income.` The
Comptroller's **Tax Alert eff. 4/13/2026** closes it: TY2026 (and TY2025) tax
electing PTEs on `resident and nonresident shares attributable to Maryland
only, as it was in tax year 2025`. **Form 511 and the TY2025 statute AGREE.
Build the form exactly as printed — no ruling needed, no diagnostic.**
Standing lesson kept in its place: mgaleg `enactments=false` serves CURRENT
code, so every statute cite here carries its VINTAGE (chapter law + effective
tax year). The base DOES move for **TY2027** — MD_511 lines 2–4 are a dated
future re-spec (D_MD511_TY2027_BASE_CHANGE).

═══════════════════════════════════════════════════════════════════════════
OPEN `[UNVERIFIED]` ITEMS — carried, never guessed (brief §12 / §15.5)
═══════════════════════════════════════════════════════════════════════════
U1.  Maryland MeF **business**-track LOI deadline, ATS window, schemas and
     business rules — SES-gated, genuinely unfetchable. **Ken-only; the
     campaign's long pole for Maryland.** Request SES access for the BUSINESS
     track before build work is scheduled.
U3.  K-1 Section D line 4's cross-reference to `Form 511, Line 13C` reads as an
     erratum; build to Form 510 lines 16d/16e. Recorded, not "fixed".
U4.  Booklet 510 `1b or 1d` vs the Form 510 face `1b or 1c` for the lines-5–19
     gate. The face is internally consistent; the booklet is not. Face governs.
U5.  Both booklets point the amended-return payment at the wrong line (16b /
     13d). The faces and per-line instructions say 16g / 13e. Faces govern.
U6.  LARGELY RESOLVED — the electing-leg exemption of REIT / IRC §408(e) /
     §501 members rests on **TB 6 §II.A** (which excludes them from the
     definition of *member* generally) plus **TG §10-104**, not on
     §10-102.1(f), which is scoped to the non-electing leg. Residual: TB 6 is
     TY2023-keyed and §10-104 was not read. Excluded from lines 1c/5b here;
     **re-verify §10-104 before seeding.**
U7.  Whether the DCF limitation may be elected on an amended return. The
     negative is STRONG: nothing in the FINAL TY2025 forms, either booklet,
     §10-102.1(d)(3) or TB 6 bars it. md_conformity.md §4's claim is
     unsupported. **NOT encoded.** Ken to rule (W5(b)).
U8.  What Form 510/511 page-3 question 8 now does. COMAR 03.04.03.10 F(2)'s
     ">25 employees" report expired for tax years beginning on/after 1/1/2011,
     and since TY2022 every multistate business uses a single receipts factor.
     Treated as informational direct-entry. **Never wired to the §10-210.1
     depreciation carve-out.**
U9.  NOL carryback period: §10-210.1(b)(2) says 5 years; Form 500DM says 2
     years (farming only). Both re-confirmed verbatim. Low PTE impact (the PTE
     computes nothing on 500DM), high member impact.
U10. "Technical Bulletin No. 38" does not exist and is cited three times on the
     FINAL TY2025 Form 500DM. The document is Administrative Release No. 38.
     Recorded so nobody "corrects" the spec back to TB 38.
U12. No published master list of Form 510/511 CODE NUMBERS. Only 704 (PTP),
     705 (investment partnership) and 301 (500UP annualization) exist in the
     whole TY2025 corpus. The spec offers those three plus free entry.

RESOLVED, recorded so they are not re-opened:
U2.  ✅ WITHDRAWN — the Form 511 resident-member "conflict" was false (see W3
     above). **Do not encode a ruling for it.**
U11. ✅ CONFIRMED NEGATIVE — no insignificant-denominator rule exists in
     Maryland. That rule is Florida's (Fla. Stat. §220.15(1)).

═══════════════════════════════════════════════════════════════════════════
VERIFIED STRUCTURE + CONSTANTS — every line number and verbatim label below
was read out of the FINAL TY2025 Comptroller of Maryland PDFs (PyMuPDF text
extraction, independently re-downloaded and re-extracted on the adversarial
verification pass 2026-08-17): Form 510 (COM/RAD-069 07/25, ModDate
2026-03-18) · Form 511 (COM/RAD-069 07/25, ModDate 2026-02-20) · Schedule K-1
(510/511) (COM/RAD-045 11/25) · 2025 PTE Booklets 510 and 511 · Form 510/511D
(COM/RAD-073 08/25) · Form 510/511E (COM/RAD-008 06/25) · Form 510C
(COM/RAD-071 09/25) · Form 500DM (COM/RAD-24 10/25) · Tax-General §§10-102.1,
10-105, 10-106.1, 10-210.1, 10-401, 10-402, 10-701.1 · COMAR 03.04.03.08/.09/
.10 · Administrative Release 43 · Technical Bulletin No. 6 · Tax Alert eff.
4/13/2026 · FINAL 2025 IRS Forms 1065 and 1120-S. NOT from memory.
⚠ Forms 510 and 511 carry the SAME revision code `COM/RAD-069 07/25` at
different URLs and are DIFFERENT returns — never key on COM/RAD-069 as a
unique document identifier.
Full source brief: delvio-states/research/md_pte_source_brief.md
═══════════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════
GATE 1 — APPROVED BY KEN 2026-08-17 (delvio-states/dispatch/WAVE3_WALK.md).
The walk (W1, W2, W4–W11) was taken and approved as proposed — all of Maryland's
items fell in Group D (ratifications) and Group E (routing), with no blocking
ruling required. W9 in particular stands as authored: **never auto-reweight an
insignificant apportionment denominator** — Maryland has no such rule, that is
Florida's, and both the code and the harness guard it. READY_TO_SEED was flipped
on that approval and nothing else.
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
# GATE 1 CLEARED — flipped 2026-08-17 on Ken's in-session review walk. The ten
# walk items (W1, W2, W4-W11) were blessed as authored. The nine [UNVERIFIED]
# items (U1, U3, U4, U5, U7, U8, U9, U10, U12) stay OPEN as pre-ship
# re-verification work — they were never seeding blockers.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = True


FORM_JURISDICTION = "MD"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"
FORM_ENTITY_TYPES = ["1065", "1120S"]

FORM_510 = "MD_510"
FORM_511 = "MD_511"


# ═══════════════════════════════════════════════════════════════════════════
# VERIFIED CONSTANTS — year-keyed, each cited; never memory, never literals
# where the source expresses a derivation.
# ═══════════════════════════════════════════════════════════════════════════

# --- The PTET rate INPUTS (the rate itself is DERIVED; see _md_ptet_*_rate) ---
# Md. Code, Tax-General §10-105(a) top marginal individual rate. TY2025 = 6.50%
# (new top bracket, Budget Reconciliation and Financing Act of 2025, HB 352,
# 2025 Md. Laws Ch. 604, for tax years beginning after 12/31/2024).
MD_TOP_MARGINAL_INDIVIDUAL_RATE: dict[int, str] = {2025: "0.0650"}
# §10-106.1(b): "the lowest county income tax rate set by any Maryland county"
# = 2.25% for TY2025 (Worcester County; all 24 rates verified in md_conformity.md §12).
MD_LOWEST_COUNTY_RATE: dict[int, str] = {2025: "0.0225"}
# §10-105(b): "The State income tax rate for a corporation is 8.25%".
MD_CORPORATE_RATE: dict[int, str] = {2025: "0.0825"}
# The tax year the rate inputs were verified for. Any other year is STALE.
MD_RATE_VERIFIED_TAX_YEAR = 2025

# --- Apportionment (Schedule A) ---
MD_APPORT_DECIMALS: dict[int, int] = {2025: 6}          # booklet Instruction 2
MD_APPORT_ZERO_FLOOR: dict[int, str] = {2025: "0.000001"}  # FORM FACE ONLY: "(If factor is zero, enter .000001)"
# TY2025: single receipts factor for tax years beginning after 12/31/2021.
MD_SINGLE_RECEIPTS_FACTOR: dict[int, bool] = {2025: True}
# ⚠ THE LOAD-BEARING NEGATIVE. Maryland has NO rule dropping or reweighting a
# factor whose denominator is zero or "insignificant". That rule is Florida's
# (Fla. Stat. §220.15(1)). Verified absent across statute, COMAR, AR 43 and
# every TY2025 booklet, re-tested with synonyms. NEVER flip this to True.
MD_INSIGNIFICANT_DENOMINATOR_RULE: dict[int, bool] = {2025: False}
# Only the Comptroller may alter a formula (§10-402(e); §10-401(2)).
MD_FORMULA_ALTERATION_ACTORS: tuple[str, ...] = ("comptroller",)

# --- Election state machine ---
# The election must be made "with the first filing of the tax year".
# ⚠ YEAR-KEYED: for TY2026 ONLY the Comptroller "will ignore any election or
# nonelection made with the first quarter estimated payment, and will, instead,
# honor the election or nonelection made with the next filing or payment for
# tax year 2026 made after April 15, 2026" (Tax Alert eff. 4/13/2026).
MD_FIRST_FILING_WINS: dict[int, bool] = {2025: True, 2026: False}
MD_ELECTION_IRREVOCABLE: dict[int, bool] = {2025: True}
MD_ELECTION_FIRST_FILING_FORMS: tuple[str, ...] = ("510_511D", "510_511E")

# --- Distributable cash flow (worksheets 9A / 11A) ---
# 9A scales distributable cash flow by the nonresident ownership percentage
# (lines J/K). 11A does NOT. Cloning one into the other over-caps or under-caps
# every DCF return.
MD_DCF_9A_HAS_OWNERSHIP_STEP: dict[int, bool] = {2025: True}
MD_DCF_11A_HAS_OWNERSHIP_STEP: dict[int, bool] = {2025: False}
# ⚠ W5(a). The brief transcribes worksheet line F verbatim as
# "Total. (Add lines B through E.)" on BOTH worksheets — line A (the income
# base) is NOT in the total. Encoded exactly as the brief states it. Flip only
# on Ken's ruling against the printed worksheet; do NOT "fix" by inference.
MD_DCF_F_INCLUDES_LINE_A: dict[int, bool] = {2025: False}
# The lesser-of is CONDITIONAL on the worksheet checkbox, never unconditional.
MD_DCF_LESSER_OF_IS_CONDITIONAL: dict[int, bool] = {2025: True}
# U7: NOT encoded — no TY2025 source bars electing the DCF cap on an amended
# return. md_conformity.md §4's claim is unsupported. Ken to rule (W5(b)).
MD_DCF_AMENDED_RETURN_BAR_SOURCED: dict[int, bool] = {2025: False}

# --- Ownership-percentage entry conventions (they DIFFER between the forms) ---
# Form 510 L5/L10 : "If 100%, leave blank" (and L6/L11 then take line 4 whole).
# Form 511 L5a/L5b: "expressed as a decimal. If 100%, enter 9999" — no blank
#                    convention, and the form face carries no 100% instruction.
MD_511_FULL_OWNERSHIP_SENTINEL = 9999

# --- Maryland §179 / decoupling figures the PTE passes through but never computes ---
# §10-210.1(b)(3)(i): no increase above $25,000 / $200,000 after 12/31/2002.
# NOT the federal OBBBA $2,500,000/$4,000,000, and NOT Georgia's.
MD_179_LIMIT: dict[int, int] = {2025: 25000}
MD_179_PHASEOUT: dict[int, int] = {2025: 200000}
# The PTE makes NO adjustment on its own Form 510/511; it attaches Form 500DM
# and passes each member's share through Schedule K-1 Section I with the codes.
MD_PTE_COMPUTES_500DM: dict[int, bool] = {2025: False}

# --- Manufacturing carve-out (§10-210.1) — statute only, NO printed form line ---
MD_MFG_NAICS_EDITION = "2012"
MD_MFG_NAICS_SECTORS: tuple[str, ...] = ("31", "32", "33")
MD_MFG_PLACED_IN_SERVICE_ON_OR_AFTER = "2019-01-01"
# ⚠ The page-3 Q8 "multistate manufacturing corporation with more than 25
# employees" is the APPORTIONMENT rule (COMAR 03.04.03.10; NAICS 1997 Edition,
# Sectors 11/31/32/33, extra exclusions, expired >25-employee report). It is a
# DIFFERENT RULE. Never wire Q8 to the depreciation carve-out.
MD_Q8_IS_DEPRECIATION_CARVEOUT = False

# --- Estimated tax / extension / interest (510/511D, 510/511E) ---
MD_ESTIMATED_THRESHOLD: dict[int, int] = {2025: 1000}
MD_ESTIMATED_SAFE_HARBOR: dict[int, tuple[float, float]] = {2025: (0.90, 1.10)}
MD_ESTIMATED_MONTHS_SCORP: dict[int, tuple[int, ...]] = {2025: (4, 6, 9, 12)}
MD_ESTIMATED_MONTHS_OTHER: dict[int, tuple[int, ...]] = {2025: (4, 6, 9, 13)}
MD_SHORT_PERIOD_NO_ESTIMATE_MONTHS: dict[int, int] = {2025: 4}
MD_EXTENSION_MONTHS: dict[int, dict] = {2025: {"1120S": 7, "other": 6}}
MD_RETURN_DUE_MONTH: dict[int, int] = {2025: 4}   # 15th day of the 4th month
MD_INTEREST_ANNUAL_PCT: dict[int, str] = {2025: "10.8133"}
MD_INTEREST_MONTHLY_PCT: dict[int, str] = {2025: "0.9011"}

# --- Code numbers: the ONLY three that exist anywhere in the TY2025 corpus (U12) ---
MD_KNOWN_CODE_NUMBERS: dict[str, str] = {
    "704": "Publicly traded pass-through entity (§10-102.1(j)) — Form 510 only",
    "705": "Investment partnership (Booklet 510 Instruction 9 NOTE 2) — Form 510 only",
    "301": "Form 500UP annualization (S corporations may NOT use annualization)",
}

# --- Composite (Form 510C) ---
MD_510C_ALLOWED: dict[str, bool] = {FORM_510: True, FORM_511: False}


def _yk(d: dict, year: int = FORM_TAX_YEAR):
    """Year-keyed lookup with a TY2025 fallback."""
    return d.get(year) if d.get(year) is not None else d[FORM_TAX_YEAR]


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS — the arithmetic the harness drives as oracles.
# ═══════════════════════════════════════════════════════════════════════════

# --- Rate derivation (§10-102.1(d)(1) and (d)(2), same construction) ---

def _md_ptet_individual_rate(year: int = FORM_TAX_YEAR) -> float:
    """§10-102.1(d)(2)(i): §10-106.1 lowest county rate + §10-105(a) top marginal.

    DERIVED, not a literal. TY2025: 0.0225 + 0.0650 = 0.0875. Any change to
    §10-105(a)'s top bracket or to the lowest county rate moves the PTET
    automatically, with no PTE legislation — it moved 8.00% -> 8.75% for TY2025
    exactly this way.
    """
    return round(
        float(_yk(MD_TOP_MARGINAL_INDIVIDUAL_RATE, year))
        + float(_yk(MD_LOWEST_COUNTY_RATE, year)),
        6,
    )


def _md_ptet_entity_rate(year: int = FORM_TAX_YEAR) -> float:
    """§10-102.1(d)(2)(ii) -> §10-105(b) corporate rate. TY2025 = 0.0825."""
    return round(float(_yk(MD_CORPORATE_RATE, year)), 6)


def _md_rate_inputs_are_stale(year: int) -> bool:
    """Staleness assertion — the rate inputs are verified for ONE tax year only."""
    return year != MD_RATE_VERIFIED_TAX_YEAR


# --- The election state machine (W1) ---

def _md_election(
    first_filing_kind=None,
    box_a=None,
    box_b=None,
    year_end_form=None,
    year: int = FORM_TAX_YEAR,
) -> dict:
    """Resolve which year-end return the PTE MUST file.

    ⚠ This is NOT derivable from the year-end return's own data. It is state
    carried across filings inside a tax year, set months earlier on Form
    510/511D or Form 510/511E. The function therefore REQUIRES the recorded
    first-filing facts and returns form=None ("undetermined") rather than
    guessing.

    first_filing_kind: '510_511D' | '510_511E' | 'year_end_return' | None
    Returns {'form', 'irrevocable', 'basis', 'deemed'}.
    """
    irrevocable = bool(_yk(MD_ELECTION_IRREVOCABLE, year))

    if first_filing_kind in MD_ELECTION_FIRST_FILING_FORMS:
        a, b = bool(box_a), bool(box_b)
        if a and b:
            # "If ... both boxes are checked in error, the Comptroller will deem
            # you have elected to pay tax at the entity level ... irrevocable."
            return {"form": FORM_511, "irrevocable": irrevocable, "deemed": True,
                    "basis": "both boxes checked in error -> DEEMED electing (Form 511)"}
        if a:
            return {"form": FORM_511, "irrevocable": irrevocable, "deemed": False,
                    "basis": "Box A checked on the first filing -> Form 511"}
        if b:
            return {"form": FORM_510, "irrevocable": irrevocable, "deemed": False,
                    "basis": "Box B checked on the first filing -> Form 510"}
        # "If this is your first filing and neither box is checked, the
        # Comptroller will deem you to have chosen to pay tax only on behalf of
        # nonresident members, and that decision will be irrevocable."
        return {"form": FORM_510, "irrevocable": irrevocable, "deemed": True,
                "basis": "neither box checked on the first filing -> DEEMED non-electing (Form 510)"}

    if first_filing_kind == "year_end_return":
        # "If you did not file Form 510/511D or Form 510/511E, filing Form 511
        # is an irrevocable election ..." / Booklet 510 Instruction 1: "filing
        # Form 510 will be deemed to be an irrevocable decision to pay tax only
        # on behalf of nonresident members."
        if year_end_form in (FORM_510, FORM_511):
            return {"form": year_end_form, "irrevocable": irrevocable, "deemed": True,
                    "basis": f"no 510/511D or 510/511E filed - filing {year_end_form} IS the irrevocable election"}
        return {"form": None, "irrevocable": irrevocable, "deemed": False,
                "basis": "no first filing on record and no year-end form chosen - UNDETERMINED"}

    return {"form": None, "irrevocable": irrevocable, "deemed": False,
            "basis": "the tax year's first filing is not on record - UNDETERMINED (never inferred)"}


def _md_election_conflict(recorded_form, filing_form) -> bool:
    """True when the year-end return being prepared contradicts the recorded,
    irrevocable election. This is a HARD BLOCK, not a warning — the error
    cannot be cured on an amended return."""
    return bool(recorded_form) and bool(filing_form) and recorded_form != filing_form


def _md_amended_may_change_election(year: int = FORM_TAX_YEAR) -> bool:
    """Booklet 510 Instruction 8: 'A PTE may not file an amended return to
    change the PTE's election or non-election for the tax year.' Corroborated
    by TB 6: 'A nonelection may not be changed to an election on an amended
    return.' Always False."""
    return False


def _md_first_filing_wins(year: int = FORM_TAX_YEAR) -> bool:
    """Year-keyed: True for TY2025; suspended for TY2026 by the Comptroller's
    Tax Alert eff. 4/13/2026 (Q1 estimated payment election is ignored)."""
    return bool(_yk(MD_FIRST_FILING_WINS, year))


# --- The member-classification matrix (W6) ---

def _md_member_box(form_number: str, member_kind: str, is_resident: bool,
                   is_exempt: bool = False) -> dict:
    """Which line 1a-1d the member lands on, and whether it is taxed.

    ⚠ THE SAME MEMBER LANDS IN DIFFERENT BOXES ON THE TWO FORMS.
    A Maryland-RESIDENT ENTITY member: Form 510 line 1d ('Others') UNTAXED;
    Form 511 line 1c ('Nonresident AND resident entities') taxed at 8.25%.
    Fiduciaries sit inside the INDIVIDUAL legs (1a/1b), never the entity legs
    ('the term individual includes fiduciaries, unless specifically excepted').

    member_kind: 'individual' | 'fiduciary' | 'entity'
    is_exempt: REIT (§856), IRC §408(e) or §501 member (TB 6 §II.A + TG
               §10-104; U6 residual — re-verify §10-104 before seeding).
    """
    individual_kinds = ("individual", "fiduciary")
    if is_exempt:
        # Both booklets route tax-exempt members to 'Others' (line 1d), which
        # nothing multiplies.
        return {"line": "1d", "taxed": False, "rate_key": None,
                "why": "REIT / IRC 408(e) / 501 exempt member -> line 1d 'Others', untaxed"}

    if form_number == FORM_510:
        if member_kind in individual_kinds:
            if is_resident:
                return {"line": "1a", "taxed": False, "rate_key": None,
                        "why": "resident individual/fiduciary -> line 1a, NOT taxed on a non-electing return"}
            return {"line": "1b", "taxed": True, "rate_key": "individual_nonresident",
                    "why": "nonresident individual/fiduciary -> line 1b -> L5/L6 -> 6.50% (L7) + 2.25% (L8)"}
        # entity member
        if is_resident:
            return {"line": "1d", "taxed": False, "rate_key": None,
                    "why": "RESIDENT ENTITY -> line 1d 'Others', UNTAXED (booklet 510: 'Include in Others, resident entities')"}
        return {"line": "1c", "taxed": True, "rate_key": "entity",
                "why": "nonresident entity -> line 1c -> L10/L11 -> 8.25% (L12)"}

    if form_number == FORM_511:
        if member_kind in individual_kinds:
            line = "1a" if is_resident else "1b"
            return {"line": line, "taxed": True, "rate_key": "individual_ptet",
                    "why": "ALL individual/fiduciary members -> line 5a -> 8.75% (L7), resident included"}
        # entity member — resident AND nonresident both land on 1c
        return {"line": "1c", "taxed": True, "rate_key": "entity",
                "why": "line 1c is 'Nonresident AND resident entities' -> line 5b -> 8.25% (L9)"}

    raise ValueError(f"unknown form_number {form_number!r}")


def _md_member_tax(form_number: str, member_kind: str, is_resident: bool,
                   maryland_share: float, is_exempt: bool = False,
                   year: int = FORM_TAX_YEAR) -> float:
    """Tax on ONE member's Maryland-allocable share, per form.

    The oracle for 'the same member produces different tax on 510 vs 511'.
    """
    box = _md_member_box(form_number, member_kind, is_resident, is_exempt)
    if not box["taxed"]:
        return 0.0
    if box["rate_key"] == "individual_nonresident":
        # Form 510 applies TWO multipliers to the same base and adds (L7 + L8).
        # Mathematically identical to 8.75% but it rounds at a different point;
        # follow each form's own line structure - do NOT collapse them.
        r_state = float(_yk(MD_TOP_MARGINAL_INDIVIDUAL_RATE, year))
        r_special = float(_yk(MD_LOWEST_COUNTY_RATE, year))
        return round(maryland_share * r_state, 2) + round(maryland_share * r_special, 2)
    if box["rate_key"] == "individual_ptet":
        # Form 511 applies ONE 8.75% multiplier (L7).
        return round(maryland_share * _md_ptet_individual_rate(year), 2)
    return round(maryland_share * _md_ptet_entity_rate(year), 2)


# --- Ownership percentage entry conventions (they differ between the forms) ---

def _md_ownership_pct(form_number: str, raw) -> float:
    """Normalise the ownership percentage per EACH FORM'S OWN convention.

    Form 510 L5/L10 : 'If 100%, leave blank' -> blank means 1.0.
    Form 511 L5a/L5b: 'expressed as a decimal. If 100%, enter 9999' -> there is
                      NO blank convention on the 511, and the form face carries
                      no 100% instruction at all.
    A shared component that normalises '100%' one way mis-enters one of the two
    returns (verification finding §15.4 item 3).
    """
    if form_number == FORM_510:
        if raw in (None, "", "blank"):
            return 1.0
        return float(raw)
    if form_number == FORM_511:
        if raw in (None, ""):
            raise ValueError("Form 511 L5a/L5b has no blank convention - enter a decimal, or 9999 for 100%")
        if float(raw) == float(MD_511_FULL_OWNERSHIP_SENTINEL):
            return 1.0
        return float(raw)
    raise ValueError(f"unknown form_number {form_number!r}")


# --- Apportionment (Schedule A) — W9 ---

def _md_apportionment_factor(numerator, denominator, year: int = FORM_TAX_YEAR) -> float:
    """Column 3 = Column 1 / Column 2, rounded to SIX places.

    ⚠ A ZERO FACTOR IS FLOORED AT .000001 — never dropped, never reweighted.
    Form 510/511 line 3b and Schedule A line 4: '(If factor is zero, enter
    .000001)'. COMAR 03.04.03.08 B(5) additionally requires a factor to be
    computed even on a loss return.
    """
    dec = _yk(MD_APPORT_DECIMALS, year)
    floor = float(_yk(MD_APPORT_ZERO_FLOOR, year))
    if not denominator:
        return floor
    factor = round(float(numerator) / float(denominator), dec)
    if factor == 0.0:
        return floor
    return factor


def _md_final_apportionment_factor(receipts_factor, property_factor=None,
                                   payroll_factor=None, special_or_alternative=None,
                                   year: int = FORM_TAX_YEAR):
    """Schedule A line 4 -> Form 510/511 line 3b.

    ⚠⚠ THE LOAD-BEARING NEGATIVE. For TY2025 Maryland uses a SINGLE RECEIPTS
    FACTOR. Property and payroll are developed only for taxpayers with income
    from the sale of intangibles or on a special/alternative formula — they
    NEVER reweight the receipts factor, and a zero or "insignificant"
    property/payroll denominator changes NOTHING. There is no
    insignificant-denominator rule in Maryland; that rule is Fla. Stat.
    §220.15(1). Altering a formula is the COMPTROLLER's act (§10-402(e);
    §10-401(2)) — a special or alternative factor is ENTERED by the preparer
    after the Comptroller's acceptance and merely disclosed by the checkbox.
    """
    if MD_INSIGNIFICANT_DENOMINATOR_RULE.get(year, False):  # pragma: no cover - must stay False
        raise AssertionError(
            "Maryland has NO insignificant-denominator rule. That is Fla. Stat. "
            "§220.15(1). Never reweight, drop or substitute a factor."
        )
    if special_or_alternative is not None:
        # Disclosed on the Schedule A line-4 checkbox; the software does not
        # compute it and must not derive it (R2 / R3).
        return float(special_or_alternative)
    if not _yk(MD_SINGLE_RECEIPTS_FACTOR, year):  # pragma: no cover
        raise AssertionError("TY2025 is single-receipts-factor; a multi-factor year needs a new spec")
    return float(receipts_factor)


def _md_may_alter_formula(actor: str) -> bool:
    """§10-402(e) / §10-401(2): only the Comptroller may alter a formula.
    Never the preparer, and never the software."""
    return actor.strip().lower() in MD_FORMULA_ALTERATION_ACTORS


# --- Form 510 tax computation (lines 5-15) ---

def _md_510_tax(line4, pct_individual_nr=None, pct_entity_nr=None,
                year: int = FORM_TAX_YEAR) -> dict:
    """Form 510 lines 5-13. Percentages follow the 510 'blank = 100%' convention."""
    p_ind = _md_ownership_pct(FORM_510, pct_individual_nr)
    p_ent = _md_ownership_pct(FORM_510, pct_entity_nr)
    r_state = float(_yk(MD_TOP_MARGINAL_INDIVIDUAL_RATE, year))
    r_special = float(_yk(MD_LOWEST_COUNTY_RATE, year))
    r_entity = _md_ptet_entity_rate(year)

    l6 = round(float(line4) * p_ind, 2)
    l7 = round(l6 * r_state, 2)          # "Multiply line 6 by 6.50%."
    l8 = round(l6 * r_special, 2)        # "Multiply line 6 by 2.25%."
    l9 = round(l7 + l8, 2)
    l11 = round(float(line4) * p_ent, 2)
    l12 = round(l11 * r_entity, 2)       # "Multiply line 11 by 8.25%."
    l13 = round(l9 + l12, 2)
    return {"L5": p_ind, "L6": l6, "L7": l7, "L8": l8, "L9": l9,
            "L10": p_ent, "L11": l11, "L12": l12, "L13": l13}


# --- Form 511 tax computation (lines 5a-10) ---

def _md_511_tax(line4, pct_individual=None, pct_entity=None,
                year: int = FORM_TAX_YEAR) -> dict:
    """Form 511 lines 5a-10. Percentages follow the 511 '9999 = 100%' convention."""
    p_ind = _md_ownership_pct(FORM_511, pct_individual)
    p_ent = _md_ownership_pct(FORM_511, pct_entity)
    r_ind = _md_ptet_individual_rate(year)
    r_ent = _md_ptet_entity_rate(year)

    l5c = round(p_ind + p_ent, 6)
    l6 = round(float(line4) * p_ind, 2)
    l7 = round(l6 * r_ind, 2)            # "Multiply line 6 by 8.75%."
    l8 = round(float(line4) * p_ent, 2)
    l9 = round(l8 * r_ent, 2)            # "Multiply line 8 by 8.25%."
    l10 = round(l7 + l9, 2)
    return {"L5a": p_ind, "L5b": p_ent, "L5c": l5c, "L6": l6, "L7": l7,
            "L8": l8, "L9": l9, "L10": l10}


# --- The two distributable-cash-flow worksheets (they DIFFER) — W5 ---

def _md_dcf_9a(line_a, b=0.0, c=0.0, d=0.0, e=0.0, g=0.0, h=0.0,
               nonresident_pct=0.0, prior_nonresident_tax_paid=0.0,
               year: int = FORM_TAX_YEAR) -> dict:
    """Form 510 worksheet 9A -> Form 510 line 14.

    A income (Form 510 line 2) · B cash-method restatement · C non-includable
    cash receipts · D depreciation/amortization/depletion add-back · E decrease
    in liability reserve · F 'Total. (Add lines B through E.)' · G non-deductible
    cash expenditures · H increase in liability reserve · I 'Total distributable
    cash flow. (Add lines G and H, and subtract the total from line F.)' ·
    ⚠ J 'Total percentage of ownership ... by nonresident. (Enter the sum of the
    percentages from Form 510, lines 5 and 10.)' · K 'Distributable cash flow.
    (Multiply line I by line J.)' · L nonresident tax previously paid ·
    M 'Distributable cash flow limitation. (Subtract line L from line K. If less
    than 0, enter 0.)'

    ⚠ W5(a): F omits line A per the brief's verbatim transcription. Gated by
    MD_DCF_F_INCLUDES_LINE_A so one constant flips it if Ken rules otherwise.
    """
    f = b + c + d + e
    if _yk(MD_DCF_F_INCLUDES_LINE_A, year):
        f += float(line_a)
    i = f - (g + h)
    j = float(nonresident_pct)
    k = round(i * j, 2)                                  # THE OWNERSHIP STEP — 9A ONLY
    m = max(0.0, round(k - float(prior_nonresident_tax_paid), 2))
    return {"A": float(line_a), "F": round(f, 2), "I": round(i, 2), "J": j,
            "K": k, "L": float(prior_nonresident_tax_paid), "M": m}


def _md_dcf_11a(line_a, b=0.0, c=0.0, d=0.0, e=0.0, g=0.0, h=0.0,
                members_tax_previously_paid=0.0, year: int = FORM_TAX_YEAR) -> dict:
    """Form 511 worksheet 11A -> Form 511 line 11.

    A 'Pass-through entity's taxable income (Form 511, line 2)' · B-E identical
    concepts · F 'Total. (Add lines B through E.)' · G, H identical ·
    I 'Distributable cash flow. (Add lines G and H, and subtract the total from
    line F.)' · J 'Members' tax previously paid.' · K 'Distributable cash flow
    limitation. (Subtract line J from line I. If less than 0, enter 0.)'

    ⚠ NO OWNERSHIP-PERCENTAGE STEP. 11A runs A-K; 9A runs A-M.
    """
    f = b + c + d + e
    if _yk(MD_DCF_F_INCLUDES_LINE_A, year):
        f += float(line_a)
    i = f - (g + h)
    k = max(0.0, round(i - float(members_tax_previously_paid), 2))
    return {"A": float(line_a), "F": round(f, 2), "I": round(i, 2),
            "J": float(members_tax_previously_paid), "K": k}


def _md_tax_due_after_dcf(total_tax, dcf_limitation=None, dcf_worksheet_used=False,
                          year: int = FORM_TAX_YEAR) -> float:
    """Form 510 line 15 / Form 511 line 12 — a CONDITIONAL lesser-of.

    Booklet 510 line 15, verbatim: 'If the distributable cash flow limitation is
    not used, enter the amount shown on Line 13. If the distributable cash flow
    method is used, enter the lesser of Line 13 or Line 14.' Identical
    construction at Form 511 line 12.

    ⚠ Building this as an unconditional MIN() ZEROES THE TAX whenever the
    worksheet line is left blank. That is a real bug, not a rounding nit.
    """
    if not dcf_worksheet_used or dcf_limitation is None:
        return round(float(total_tax), 2)
    if not _yk(MD_DCF_LESSER_OF_IS_CONDITIONAL, year):  # pragma: no cover
        raise AssertionError("the DCF lesser-of is conditional on the checkbox in every TY2025 source")
    return round(min(float(total_tax), float(dcf_limitation)), 2)


# --- The owner side: credit PLUS add-back, D2/D4 only — W4 ---

def _md_owner_side(k1_d1=0.0, k1_d2=0.0, k1_d4=0.0) -> dict:
    """Schedule K-1 (510/511) Section D -> the member's own return.

    D1 'Nonresident tax paid on member's behalf by this PTE (Form 510)'
    D2 'Pass-through entity election tax paid on member's ... share by this PTE (Form 511)'
    D3 RESERVED (dead — Comptroller v. FC-GEN Operations Investments LLC)
    D4 'Pass-through entity election tax paid ... by OTHER PTEs (Form 511)'
    D5 Total (Add lines 1 through 4).

    CREDIT (§10-701.1) = D1 + D2 + D4, routed to Form 502CR Part CC line 9
    (individuals) / 500CR (corporations) / 504 (fiduciaries) / 505 line 45 for
    510 credits / Form 510 lines 16c-16f / Form 511 line 13c (PTE members).

    ⚠ ADD-BACK = D2 + D4 ONLY. Form face, Section D line 5: 'Members with
    entries on Lines 2 and 4 are required to addback the amount of the credit
    total on Line 2 and 4 on their respective returns.' D1 carries NO such
    sentence — under §10-102.1(c)(1) the non-electing tax is already treated as
    the member's own tax paid on their behalf, not an entity-level deduction.
    ADDING BACK D1 DOUBLE-TAXES EVERY NONRESIDENT PARTNER; omitting the D2/D4
    add-back overstates owner relief by the full PTET.

    ⚠ The PTE must NOT pre-load the add-back into K-1 Section B: 'For electing
    PTEs, do not include in additions the member's addback of the electing PTE
    credit. The electing PTE credit is added back on the member's return.'
    """
    d1, d2, d4 = float(k1_d1), float(k1_d2), float(k1_d4)
    return {
        "D5_credit_total": round(d1 + d2 + d4, 2),
        "addback": round(d2 + d4, 2),
        "addback_sources": ["D2", "D4"],
        "d1_in_addback": False,
        "section_b_preloaded": False,
        "individual_addback_route": "Form 502 Other Additions code 'r'",
        "corporate_addback_route": "§10-306(b)(6) -> §10-205(m)",
    }


# --- K-1 Section H (mandatory reporting, no tax line) — W7 ---

def _md_k1_section_h_column2(column1_federal_gain, apportionment_factor) -> float:
    """'To determine the Maryland net capital gain in Column 2, multiply the
    federal amount in Column 1 by the PTE's Maryland apportionment factor.'

    A SECOND consumer of the Schedule A factor. The PTE computes NO capital-gain
    surtax at entity level (TB 58) but MUST report — a mandatory schedule with
    no tax line is exactly what gets dropped.
    """
    return round(float(column1_federal_gain) * float(apportionment_factor), 2)


# --- Schedule B (per-member roster) ---

def _md_schedule_b_share_base(line2, line4) -> float:
    """⚠ Schedule B reports the per-member share as 'a portion of the amount on
    line 2, page 1' — LINE 2, NOT LINE 4. The tax lines run off the apportioned
    line 4; Schedule B does not. Do not wire Schedule B off line 4."""
    return float(line2)


# --- S-corp dual filing trigger (R6 / W10) ---

def _md_scorp_also_files_form_500(f1120s_line_23a=0.0, f1120s_line_23b=0.0) -> bool:
    """'S corporations subject to federal corporation income tax, such as for
    excess net passive income or built-in gains, also are subject to Maryland
    corporation income tax.' Trigger verified on the FINAL 2025 IRS Form 1120-S:
    line 23a 'Excess net passive income or LIFO recapture tax' / line 23b 'Tax
    from Schedule D (Form 1120-S)'. TWO Maryland returns, not one.
    ⚠ The booklets say 'also file Form 510' and are SILENT on the 511 case (W10).
    """
    return (float(f1120s_line_23a or 0) > 0) or (float(f1120s_line_23b or 0) > 0)


# ═══════════════════════════════════════════════════════════════════════════
# SHARED COMPONENTS — Schedule A is byte-identical on the two forms (verified
# by diff; only header/form-number differ). Generated from one table so the
# two specs cannot drift apart.
# ═══════════════════════════════════════════════════════════════════════════

SCHEDULE_A_INPUT_ROWS: list[tuple[str, str, str]] = [
    ("1a", "Gross receipts or sales less returns and allowances", "receipts"),
    ("1b", "Dividends", "receipts"),
    ("1c", "Interest", "receipts"),
    ("1d", "Gross rents", "receipts"),
    ("1e", "Gross royalties", "receipts"),
    ("1f", "Capital gain net income", "receipts"),
    ("1g", "Other income (Attach schedule.)", "receipts"),
    ("2a", "Inventory", "property"),
    ("2b", "Machinery and equipment", "property"),
    ("2c", "Buildings", "property"),
    ("2d", "Land", "property"),
    ("2e", "Other tangible assets (Attach schedule.)", "property"),
    ("2f", "Rent expense capitalized (multiply by eight)", "property"),
    ("3a", "Compensation of officers", "payroll"),
    ("3b", "Other salaries and wages", "payroll"),
]

SCHEDULE_A_TOTAL_ROWS: list[tuple[str, str]] = [
    ("1h", "Total receipts (Add lines 1(a) through 1(g), for Columns 1 and 2.) "
           "Report this factor on line 4 unless you use a special apportionment formula "
           "or alternative apportionment formula."),
    ("2g", "Total property (Add lines 2a through 2f, for Columns 1 and 2)"),
    ("3c", "Total payroll (Add lines 3a and 3b, for Columns 1 and 2.)"),
]


def _schedule_a_facts(sort_base: int) -> list[dict]:
    """Column 1 (TOTALS WITHIN MARYLAND) and Column 2 (WITHIN AND WITHOUT) for
    every Schedule A input row — all DIRECT-ENTRY in v1."""
    facts: list[dict] = []
    for i, (code, label, group) in enumerate(SCHEDULE_A_INPUT_ROWS):
        facts.append({
            "fact_key": f"scha_{code}_md", "label": f"Schedule A {code} — {label} (Column 1, within Maryland)",
            "data_type": "decimal", "required": False, "sort_order": sort_base + (i * 2),
            "notes": f"{group} factor numerator. Direct-entry; must reconcile to the federal return's own categories.",
        })
        facts.append({
            "fact_key": f"scha_{code}_everywhere", "label": f"Schedule A {code} — {label} (Column 2, within and without)",
            "data_type": "decimal", "required": False, "sort_order": sort_base + (i * 2) + 1,
            "notes": f"{group} factor denominator. Direct-entry.",
        })
    facts.append({
        "fact_key": "scha_special_or_alternative_checked",
        "label": "Schedule A line 4 — special / alternative apportionment formula used? (disclosure checkbox)",
        "data_type": "boolean", "required": False, "sort_order": sort_base + 90,
        "notes": "A DISCLOSURE of a formula already accepted by the Comptroller — not a self-election. RED-defer R2/R3.",
    })
    facts.append({
        "fact_key": "scha_accepted_alternative_factor",
        "label": "Schedule A line 4 — Comptroller-accepted special/alternative factor (direct-entry)",
        "data_type": "decimal", "required": False, "sort_order": sort_base + 91,
        "notes": "Entered by the preparer; the software never derives one (§10-402(e); §10-401(2)).",
    })
    return facts


def _schedule_a_lines(sort_base: int, apport_rule: str) -> list[dict]:
    lines: list[dict] = []
    n = 0
    for code, label, _group in SCHEDULE_A_INPUT_ROWS:
        lines.append({
            "line_number": f"SchA-{code}", "description": label, "line_type": "input",
            "source_facts": [f"scha_{code}_md", f"scha_{code}_everywhere"],
            "sort_order": sort_base + n,
        })
        n += 1
    for code, label in SCHEDULE_A_TOTAL_ROWS:
        lines.append({
            "line_number": f"SchA-{code}", "description": label, "line_type": "subtotal",
            "source_rules": [apport_rule], "sort_order": sort_base + n,
        })
        n += 1
    lines.append({
        "line_number": "SchA-4",
        "description": ("Maryland apportionment factor — Enter amount from Line 1 Column 3. If an alternative "
                        "apportionment formula or a special apportionment formula is used, enter the alternative "
                        "or special apportionment factor here. (If factor is zero, enter .000001 on line 3b, page 1.) "
                        "Check here if special apportionment or alternative apportionment formula is used."),
        "line_type": "calculated", "calculation": apport_rule, "source_rules": [apport_rule],
        "sort_order": sort_base + n,
        "notes": ("Column 3 = Column 1 / Column 2 rounded to SIX places. TY2025 = single receipts factor. "
                  "NEVER drop or reweight a factor — Maryland has no insignificant-denominator rule (W9)."),
    })
    return lines


PAGE3_LINES: list[dict] = [
    {"line_number": "p3-Q7", "description": "Is this entity a multistate corporation that is a member of a unitary group?",
     "line_type": "input", "source_facts": ["p3_q7_unitary_group_member"], "sort_order": 900},
    {"line_number": "p3-Q8", "description": ("Is this entity a multistate manufacturing corporation with more than 25 employees? "
                                             "⚠ INFORMATIONAL ONLY — this is the COMAR 03.04.03.10 apportionment rule "
                                             "(NAICS 1997 Edition, Sectors 11/31/32/33), NOT the §10-210.1 depreciation "
                                             "carve-out (NAICS 2012 Edition, Sectors 31/32/33). Never wire the two together."),
     "line_type": "input", "source_facts": ["p3_q8_multistate_mfg_corp_25_employees"], "sort_order": 901},
    {"line_number": "p3-codes", "description": "CODE NUMBERS (3 digits per line) — only 704, 705 and 301 exist in the TY2025 corpus (U12)",
     "line_type": "input", "source_facts": ["p3_code_numbers"], "sort_order": 902},
]


def _page3_facts(sort_base: int) -> list[dict]:
    return [
        {"fact_key": "p3_q7_unitary_group_member", "label": "Page 3 Q7 — multistate corporation that is a member of a unitary group?",
         "data_type": "boolean", "required": False, "sort_order": sort_base},
        {"fact_key": "p3_q8_multistate_mfg_corp_25_employees",
         "label": "Page 3 Q8 — multistate manufacturing corporation with more than 25 employees? (INFORMATIONAL)",
         "data_type": "boolean", "required": False, "sort_order": sort_base + 1,
         "notes": "U8: no current published use. NEVER wired to the §10-210.1 depreciation carve-out (W2)."},
        {"fact_key": "p3_code_numbers", "label": "Page 3 CODE NUMBERS (704 PTP / 705 investment partnership / 301 500UP annualization)",
         "data_type": "string", "required": False, "sort_order": sort_base + 2,
         "notes": "U12 — no published master list; these three are the only codes anywhere in the TY2025 PTE corpus."},
        {"fact_key": "naics_31_33_manufacturing_entity",
         "label": "§10-210.1 manufacturing entity? (NAICS 2012 Edition Sectors 31/32/33, refiners excluded)",
         "data_type": "boolean", "required": False, "sort_order": sort_base + 3,
         "notes": ("W2 / R10. A SPEC-LEVEL ENTITY ATTRIBUTE — no Maryland form line captures it, so there is no "
                   "printed cross-check. Switches OFF the §168(k) and §179 add-backs for property placed in service "
                   "on or after 1/1/2019. Does NOT reach §10-210.1(b)(5) heavy-duty SUVs. Disconnected from p3-Q8."),
         },
    ]


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY TOPICS / SOURCES
# ═══════════════════════════════════════════════════════════════════════════

# ⚠ topic_name is capped at 255 in Postgres — keep every entry short.
AUTHORITY_TOPICS: list[tuple[str, str]] = [
    ("md_pte_election", "Maryland's mutually exclusive PTE returns — Form 510 (non-electing) vs Form 511 (electing). "
     "The election is made on the tax year's first filing, is irrevocable, has two deeming defaults, and is not "
     "derivable from the return's own data."),
    ("md_ptet_rate", "Maryland PTET rate as a statutory derivation: §10-106.1 lowest county rate (2.25%) + §10-105(a) "
     "top marginal (6.50%) = 8.75% for individuals/fiduciaries; §10-105(b) 8.25% for entity members."),
    ("md_pte_apportionment", "Maryland PTE single receipts factor, six decimals, the .000001 zero-factor floor, and "
     "the absence of any insignificant-denominator rule — only the Comptroller may alter a formula."),
    ("md_pte_owner_side", "Maryland PTE owner side: the §10-701.1 credit PLUS the mandatory income add-back attaching "
     "to Schedule K-1 (510/511) Section D lines 2 and 4 only, never line 1."),
]

# The MD conformity anchor already seeded by the Tier-1 conformity wave.
# MD_TG_10_108 is Maryland's conformity/automatic-decoupling statute (the anchor);
# MD_TG_10_210_1 backs the §179 freeze and the manufacturing carve-out (R10/W2).
EXISTING_SOURCES_TO_REFERENCE: list[str] = [
    "MD_TG_10_108",
    "MD_TG_10_210_1",
]

AUTHORITY_SOURCES: list[dict] = [
    {
        "source_code": "MD_2025_FORM_510",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "MD",
        "title": "2025 Form 510 — Maryland Pass-Through Entity Income Tax Return (non-electing)",
        "citation": "Maryland Form 510 (2025), COM/RAD-069 07/25 — FINAL TY2025 (PDF ModDate 2026-03-18)",
        "issuer": "Comptroller of Maryland",
        "official_url": "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/forms/2025/510.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.6,
        "topics": ["md_pte_election", "md_ptet_rate", "md_pte_apportionment"],
        "excerpts": [
            {
                "excerpt_label": "Form 510 page-1 face — the STOP instruction (election)",
                "excerpt_text": (
                    "Complete this form if the pass-through entity (\"PTE\") is paying tax only on behalf of "
                    "nonresident members and not electing to remit tax on all members' shares of income. If the PTE "
                    "made an irrevocable election on Form 510/511D or 510/511E to remit tax with respect to all "
                    "members' shares, STOP. You must file Form 511. — Also on the face: 'You may also use this form "
                    "to request a refund of estimated payment(s) for tax paid on resident members' shares of income "
                    "if the PTE has decided not to make the entity election.'"
                ),
                "summary_text": "Form 510 is the NON-ELECTING return; a Box-A filer must STOP and file Form 511. A Box-B filer recovers resident-leg estimates on the 510.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Form 510 verified line map (pages 1-2)",
                "excerpt_text": (
                    "1a Individual (including fiduciary) residents of Maryland; 1b Individual (including fiduciary) "
                    "nonresidents; 1c Nonresident entities; 1d Others; 1e Total. 2 Total distributive or pro rata "
                    "share of income per federal return (Form 1065 or 1120S). 3a Non-Maryland income (separate "
                    "accounting); 3b Maryland apportionment factor from computation worksheet on Page 4 (If factor is "
                    "zero, enter .000001). 4 Distributive or pro rata share of income allocable to Maryland. NOTE: "
                    "Complete lines 5 through 19 if there is an entry on line 1b or line 1c. 5 Percentage of "
                    "ownership by individual nonresident members (If 100%, leave blank); 6 = L4 x L5; 7 Nonresident "
                    "individual tax (Multiply line 6 by 6.50%.); 8 Special nonresident tax (Multiply line 6 by "
                    "2.25%.); 9 = L7+L8; 10 Percentage of ownership by nonresident entities; 11 = L4 x L10; 12 "
                    "Nonresident entity tax (Multiply line 11 by 8.25%.); 13 = L9+L12; 14 Distributable cash flow "
                    "limitation from worksheet (If worksheet used, check here); 15 Nonresident tax due (Enter the "
                    "lesser of line 13 or line 14.); 16a-16g payments -> 16h total; 17 balance due; 18 overpayment; "
                    "18a prior overpayment; 19 interest/penalty (Form 500UP); 20 total nonresident balance due (Add "
                    "lines 15, 18a, and 19. Subtract line 16h.); 21 applied to next year; 22 TO BE REFUNDED; 23a-d "
                    "direct deposit."
                ),
                "summary_text": "Form 510: nonresident-only tax at 6.50% + 2.25% (individuals/fiduciaries) and 8.25% (nonresident entities); seven payment lines 16a-16g.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Form 510 worksheet 9A — DCF WITH the ownership step",
                "excerpt_text": (
                    "A Total distributive or pro rata share of income (Form 510, line 2); B cash-method restatement; "
                    "C non-includable cash receipts; D depreciation/amortization/depletion add-back; E decrease in "
                    "liability reserve; F Total. (Add lines B through E.); G non-deductible cash expenditures; H "
                    "increase in liability reserve; I Total distributable cash flow. (Add lines G and H, and subtract "
                    "the total from line F.); J Total percentage of ownership (or profit/loss sharing if applicable) "
                    "by nonresident. (Enter the sum of the percentages from Form 510, lines 5 and 10.); K "
                    "Distributable cash flow. (Multiply line I by line J.); L nonresident tax previously paid; M "
                    "Distributable cash flow limitation. (Subtract line L from line K. If less than 0, enter 0.)"
                ),
                "summary_text": "Worksheet 9A runs A-M and SCALES distributable cash flow by the nonresident ownership percentage (J/K) — worksheet 11A does not.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Form 510 page 3 — Additional Information Required",
                "excerpt_text": (
                    "1 principal Maryland place of business; 2 address of tax records; 3 telephone; 4 State of "
                    "organization or incorporation; 5 unreported IRS adjustments Y/N + tax years; 6 employer "
                    "withholding filed Y/N; 7 Is this entity a multistate corporation that is a member of a unitary "
                    "group?; 8 Is this entity a multistate manufacturing corporation with more than 25 employees?; "
                    "plus two CODE NUMBERS (3 digits per line) blocks. Page 3 is IDENTICAL on Form 511."
                ),
                "summary_text": "Page-3 Q8 is the COMAR 03.04.03.10 apportionment rule, not the §10-210.1 depreciation carve-out; no published code-number legend (U12).",
                "is_key_excerpt": False,
            },
        ],
    },
    {
        "source_code": "MD_2025_FORM_511",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "MD",
        "title": "2025 Form 511 — Maryland Pass-Through Entity Election Income Tax Return",
        "citation": "Maryland Form 511 (2025), COM/RAD-069 07/25 — FINAL TY2025 (PDF ModDate 2026-02-20)",
        "issuer": "Comptroller of Maryland",
        "official_url": "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/forms/2025/511.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.6,
        "topics": ["md_pte_election", "md_ptet_rate", "md_pte_apportionment"],
        "excerpts": [
            {
                "excerpt_label": "Form 511 verified line map (pages 1-2)",
                "excerpt_text": (
                    "1a Individual (including fiduciary) residents of Maryland; 1b Individual (including fiduciary) "
                    "nonresidents; 1c Nonresident AND RESIDENT entities; 1d Others (see instructions); 1e Total. 2 "
                    "Pass-through entity taxable income. ALLOCATION OF INCOME: Multistate pass-through entities must "
                    "complete Line 3a. or 3b. (no 'with nonresident members' qualifier). 3b (If factor is zero, enter "
                    ".000001). 4 Pass-through entity taxable income allocable to Maryland. NOTE: Complete lines 5a. "
                    "through 19 only if there is an entry on line 1a. through line 1d. 5a Percentage of ownership by "
                    "individual members shown on lines 1a and 1b; 5b Percentage of ownership by entity members shown "
                    "on line 1c; 5c Add Lines 5a and 5b; 6 = L4 x L5a; 7 Total Individual members' pass-through "
                    "entity election tax (Multiply line 6 by 8.75%.); 8 = L4 x L5b; 9 Entity members' pass-through "
                    "entity election tax (Multiply line 8 by 8.25%.); 10 = L7+L9; 11 Distributable cash flow "
                    "limitation from worksheet (If worksheet used, check here); 12 Pass-through entity election tax "
                    "due (Enter the lesser of line 10 or line 11.); 13a-13e payments -> 13f total; 14 balance due; 15 "
                    "overpayment; 15a prior overpayment; 16 interest/penalty; 17 Total balance due (Add lines 12, 15a "
                    "and 16. Subtract line 13f.); 18 applied to next year; 19 TO BE REFUNDED; 20a-d direct deposit. "
                    "There is NO '510C Filed' checkbox on Form 511."
                ),
                "summary_text": "Form 511 taxes ALL members: 8.75% individuals/fiduciaries (one multiplier), 8.25% entity members incl. RESIDENT entities on line 1c; five payment lines 13a-13e.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Form 511 face — this form is for electing PTEs",
                "excerpt_text": (
                    "This Form is used by PTEs that elect to remit tax on all members' shares of income. — Both the "
                    "510/511D and 510/511E carry: 'MANDATORY: You must select either Box A or Box B. The choice you "
                    "make on your first filing of the tax year is irrevocable for the tax year.'"
                ),
                "summary_text": "Form 511 is the ELECTING return; the election is made and locked on the first filing of the tax year.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Form 511 worksheet 11A — DCF WITHOUT the ownership step",
                "excerpt_text": (
                    "A Pass-through entity's taxable income (Form 511, line 2); B-E identical concepts to worksheet "
                    "9A; F Total. (Add lines B through E.); G non-deductible cash expenditures; H increase in "
                    "liability reserve; I Distributable cash flow. (Add lines G and H, and subtract the total from "
                    "line F.); J Members' tax previously paid. (Enter all members' estimated tax paid with Forms "
                    "510/511D or 510/511E); K Distributable cash flow limitation. (Subtract line J from line I. If "
                    "less than 0, enter 0.) — NO ownership-percentage step. 11A runs A-K; 9A runs A-M."
                ),
                "summary_text": "Worksheet 11A has NO ownership multiplier. Cloning 9A into 11A (or the reverse) over-caps or under-caps every DCF return.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Form 511 face errata — the two dangling cross-references (W11 e, f)",
                "excerpt_text": (
                    "(e) The NOTE under line 17 reads 'The total tax paid on line 12 is to be reported either on the "
                    "composite return or on the returns of members' — but PTE Booklet 511 states 'An Electing PTE is "
                    "not permitted to file a composite Maryland income tax return Form 510C', and there is no '510C "
                    "Filed' box on the 511. (f) The line-4 NOTE says '(Investment partnerships see Specific "
                    "Instructions)' but Booklet 511 contains no investment-partnership instruction and never mentions "
                    "code 705 — the rule exists only in Booklet 510 Instruction 9 and TB 6 §II.B."
                ),
                "summary_text": "Two Form 511 face errata recorded so nobody 'fixes' them back: the composite cross-reference and the missing investment-partnership instruction.",
                "is_key_excerpt": False,
            },
        ],
    },
    {
        "source_code": "MD_2025_PTE_BOOKLET_510",
        "source_type": "state_instruction",
        "source_rank": "primary_official",
        "jurisdiction_code": "MD",
        "title": "2025 Maryland PTE Booklet 510 — instructions for Form 510",
        "citation": "2025 Maryland Pass-Through Entity Booklet 510 — FINAL TY2025 (PDF ModDate 2026-02-17)",
        "issuer": "Comptroller of Maryland",
        "official_url": "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/pte-booklet-510.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.4,
        "topics": ["md_pte_election", "md_ptet_rate", "md_pte_apportionment"],
        "excerpts": [
            {
                "excerpt_label": "Booklet 510 Instruction 1 + 8 — the mirror election statement and the amended bar",
                "excerpt_text": (
                    "An entity may file Form 510 as its year-end return only if it did not elect to pay tax at the "
                    "entity level with respect to all members' shares on its first filing of the tax year (Form "
                    "510/511D or Form 510/511E). An entity that made such an election must file Form 511 as its "
                    "year-end return. If the year-end return is the entity's first filing of the tax year, filing "
                    "Form 510 will be deemed to be an irrevocable decision to pay tax only on behalf of nonresident "
                    "members. — Instruction 8: A PTE may not file an amended return to change the PTE's election or "
                    "non-election for the tax year."
                ),
                "summary_text": "Filing Form 510 as a first filing IS an irrevocable non-election; no amended return may change the election either way.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Booklet 510 Taxability — the nonresident rates and the nonresident-entity definition",
                "excerpt_text": (
                    "If there are nonresident members, the pass-through entity nonresident tax applies and must be "
                    "paid by the PTE on behalf of these members. PTEs must pay a tax consisting of 6.50%, in addition "
                    "to a special nonresident tax of 2.25%, of the nonresident individual and nonresident fiduciary "
                    "members' distributive or pro rata shares of income allocable to Maryland. PTEs also are required "
                    "to pay a tax at the rate of 8.25% of income allocable to Maryland on behalf of all members who "
                    "are nonresident entities. A nonresident entity is an entity that is not formed under the laws of "
                    "Maryland; and is not qualified by, or registered with, the Department of Assessments and "
                    "Taxation to do business in Maryland. Note: the term individual includes fiduciaries."
                ),
                "summary_text": "6.50% + 2.25% on nonresident individuals AND fiduciaries; 8.25% on nonresident entities; fiduciaries live in the individual legs.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Booklet 510 Line 1 + line 15 — the resident entity, and the CONDITIONAL lesser-of",
                "excerpt_text": (
                    "Line 1: Include in \"Others\", resident entities and entities that are tax-exempt under IRC "
                    "Sections 408(e) or 501. — Line 15 - Nonresident tax due: If the distributable cash flow "
                    "limitation is not used, enter the amount shown on Line 13. If the distributable cash flow method "
                    "is used, enter the lesser of Line 13 or Line 14. — Also: Election of the distributable cash flow "
                    "limitation will not reduce the tax liability of the members. If the distributable cash flow "
                    "limitation is not used, do not complete this line."
                ),
                "summary_text": "Resident entities go to line 1d 'Others' (untaxed) on the 510; the L15 lesser-of applies ONLY when the DCF worksheet is used.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Booklet 510 Instruction 9 NOTE 2 — investment partnerships (code 705)",
                "excerpt_text": (
                    "If the PTE is a partnership whose activities and assets are limited to investment in stocks, "
                    "bonds, futures, options or debt obligations other than debt instruments directly secured by real "
                    "or tangible personal property, it is not subject to the nonresident tax merely because the "
                    "investment decisions, trading orders, research and the like are conducted by a general partner "
                    "from a Maryland location. Enter code number \"705\" on one of the lines marked \"code number\" on "
                    "page 3 of Form 510. Partnerships, however, such as brokerage firms that deal with the general "
                    "public, are not exempt if the business is conducted within Maryland and should complete lines 5-19."
                ),
                "summary_text": "Investment-partnership relief (code 705) exists only in Booklet 510; brokerage firms dealing with the public are NOT exempt.",
                "is_key_excerpt": False,
            },
            {
                "excerpt_label": "Booklet 510 apportionment + Schedule B (Instructions 2, 3)",
                "excerpt_text": (
                    "For tax years beginning after December 31, 2021, multistate businesses using the apportionment "
                    "method of allocation generally are required to use a single receipts factor. Each factor is "
                    "calculated to six decimal places. Partnerships may use separate accounting or the apportionment "
                    "method of allocation. S corporations must use the apportionment method unless the activity in "
                    "Maryland is nonunitary. — Schedule B: the per-member share of income is a portion of the amount "
                    "on line 2, page 1. — ERRATUM (U4): 'Do not complete lines 5 through 19: 1. Unless the PTE has "
                    "members that are nonresidents of Maryland (there is an entry on 1b or 1d)' contradicts the form "
                    "face's '1b or 1c'; the face governs."
                ),
                "summary_text": "Single receipts factor, six decimals, entity-type gate on separate accounting; Schedule B runs off LINE 2, not line 4; the booklet's 1b-or-1d gate is an erratum.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MD_2025_PTE_BOOKLET_511",
        "source_type": "state_instruction",
        "source_rank": "primary_official",
        "jurisdiction_code": "MD",
        "title": "2025 Maryland PTE Booklet 511 — instructions for Form 511 (Electing PTE)",
        "citation": "2025 Maryland Pass-Through Entity Booklet 511 — FINAL TY2025 (PDF ModDate 2026-02-17)",
        "issuer": "Comptroller of Maryland",
        "official_url": "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/pte-booklet-511.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.4,
        "topics": ["md_pte_election", "md_ptet_rate", "md_pte_owner_side"],
        "excerpts": [
            {
                "excerpt_label": "Booklet 511 FILING FORM 511 — the election and its irrevocability",
                "excerpt_text": (
                    "You must file Form 511 if you checked the box electing to be taxed at the entity level on Form "
                    "510/511D ... and/or Form 510/511E ... If you did not check the box on Form 510/511D or Form "
                    "510/511E, you did not make the election, and you must file Form 510. If you did not file Form "
                    "510/511D or Form 510/511E, filing Form 511 is an irrevocable election to be taxed at the entity "
                    "level for tax year 2025. You may not change this election on an amended return."
                ),
                "summary_text": "The box on the first filing decides the year-end return; with no D or E filed, filing the 511 IS the irrevocable election.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Booklet 511 Line 2 — the electing base and the SALT add-back",
                "excerpt_text": (
                    "Enter the Electing PTE's taxable income under the federal Internal Revenue Code, calculated "
                    "without regard to any deduction for taxes based on net income that are imposed by any state or "
                    "political subdivision of a state, that is derived from or reasonably attributable to the trade or "
                    "business of the pass-through entity ... the net amount of income/loss for the PTE, less interest "
                    "from federal obligations plus the amount attributable to taxes based on net income imposed by a "
                    "state or any political subdivision of a state. The amount attributable to taxes based on net "
                    "income does not include taxes with a basis other than net income, such as a gross receipts tax "
                    "or a commercial activity tax. Partnership: net of federal Form 1065 Schedule K lines 1 through "
                    "11 plus taxes based on net income included on federal Form 1065 Line 14. S corporation: net of "
                    "federal Form 1120S Schedule K lines 1 through 10 plus Form 1120S Line 12."
                ),
                "summary_text": "Form 511 line 2 = federal Sch. K income block + the SALT add-back (1065 L14 / 1120-S L12) − federal-obligation interest.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Booklet 511 — the prior-year-refund adjustment (multi-year state)",
                "excerpt_text": (
                    "In calculating PTE taxable income, the disregarded deduction is adjusted for income on the "
                    "federal return attributable to a refund of overpayment of the previous year's estimated taxes. "
                    "Worked example: Year 1 SALT payments $10,000, federal income $75,000 -> MD PTE taxable income "
                    "$85,000; MD liability $6,800; refund $3,200. Year 2 SALT payments $10,000, federal income "
                    "$78,200 of which $3,200 is the Year-1 refund -> the electing PTE should adjust the disregarded "
                    "deduction to $6,800, bringing PTE taxable income to $85,000. The add-back is the tax actually "
                    "BORNE, not the cash paid."
                ),
                "summary_text": "The 511 line-2 SALT add-back is net of the prior-year Maryland refund — multi-year state, not a single-year computation.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Booklet 511 — rates, exempt members, and the composite bar",
                "excerpt_text": (
                    "The tax is the top marginal state tax of 6.50% plus the lowest local income tax rate of 2.25% of "
                    "individual member's distributive or pro rata share of income. For entity members the tax is "
                    "8.25%. — The Electing PTE tax does not apply to a member that is a Real Estate Investment Trust "
                    "(REIT) or to a member that is tax-exempt under IRC Sections 408(e) or 501, unless the tax-exempt "
                    "member is subject to the federal income tax on its federal return on that share of Electing PTE "
                    "income. — An Electing PTE is not permitted to file a composite Maryland income tax return Form "
                    "510C. — Line 1: 1c counts the number of nonresident AND RESIDENT entities; Include in \"Others\" "
                    "entities that are tax-exempt under IRC Sections 408(e) or 501 (resident entities are dropped)."
                ),
                "summary_text": "8.75%/8.25% confirmed in narrative; REIT/§408(e)/§501 members excluded (U6 footing = TB 6 §II.A + TG §10-104); an Electing PTE may NOT file Form 510C; resident entities move to line 1c.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "Booklet 511 L5a/L5b — the 100% convention that differs from the 510",
                "excerpt_text": (
                    "Lines 5a and 5b: the percentage of ownership expressed as a decimal. If 100%, enter 9999. "
                    "(Form 510 lines 5 and 10 instead say 'If 100%, leave blank', and the 510's lines 6/11 then take "
                    "the amount from line 4 whole. The Form 511 face carries no 100% instruction at all.)"
                ),
                "summary_text": "511: 100% is entered as 9999. 510: 100% is left blank. A shared normaliser mis-enters one of the two returns.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MD_2025_SCH_K1_510_511",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "MD",
        "title": "2025 Maryland Schedule K-1 (510/511) with instructions",
        "citation": "Maryland Schedule K-1 (510/511) (2025), COM/RAD-045 11/25 — FINAL TY2025 (PDF ModDate 2026-04-09)",
        "issuer": "Comptroller of Maryland",
        "official_url": "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/forms/2025/510k-1.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["md_pte_owner_side", "md_pte_apportionment"],
        "excerpts": [
            {
                "excerpt_label": "K-1 Section D — the whole owner-side story, and where the add-back attaches",
                "excerpt_text": (
                    "D1 Nonresident tax paid on member's behalf by this PTE (Form 510). D2 Pass-through entity "
                    "election tax paid on member's distributive or pro rata share of income by this PTE (Form 511). "
                    "D3 RESERVED — 'Due to the decision by the Supreme Court of Maryland in Comptroller of Maryland v. "
                    "FC-GEN Operations Investments LLC ... the amount reported on this line in previous years is no "
                    "longer passed through to a PTE's members.' D4 Pass-through entity election tax paid ... by other "
                    "PTEs (Form 511). D5 Total (Add Lines 1 through 4.) — 'Note: Members with entries on Lines 2 and "
                    "4 are required to addback the amount of the credit total on Line 2 and 4 on their respective "
                    "returns.' The D2 and D4 instructions add: 'The amount of credit listed here must be taken as an "
                    "addition modification on Form 500, 504 (Instruction 9), 502, or 505.' D1 carries NO such sentence."
                ),
                "summary_text": "Credit = D1+D2+D4. ADD-BACK = D2+D4 ONLY. D1 is never added back (§10-102.1(c)(1)); adding it back double-taxes every nonresident partner.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "K-1 Section B instruction — where the add-back does NOT go",
                "excerpt_text": (
                    "For electing PTEs, do not include in additions the member's addback of the electing PTE credit. "
                    "The electing PTE credit is added back on the member's return."
                ),
                "summary_text": "The PTE must NOT pre-load the electing-PTE add-back into K-1 Section B additions.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "K-1 Section H — mandatory capital-gain reporting with NO tax line (W7)",
                "excerpt_text": (
                    "New for TY2025. Columns: (1) Federal Net Capital Gain (All Members); (2) Maryland Net Capital "
                    "Gain (Nonresident Members Only); (3) Non-Maryland Net Capital Gain (Nonresident Members Only). "
                    "Seven rows: 1 net capital gain per federal Schedule K-1; 2 primary residence (exclude sales "
                    "totaling $1,500,000 or more); 3 tax-advantaged retirement plan assets (FOR RESIDENT MEMBERS "
                    "ONLY — column 2 blocked out); 4 cattle/horses/breeding livestock; 5 conservation/agricultural/"
                    "forest preservation easement land; 6 §179 trade-or-business property; 7 nonprofit affordable "
                    "housing. 'To determine the Maryland net capital gain in Column 2, multiply the federal amount in "
                    "Column 1 by the PTE's Maryland apportionment factor.' 'MEMBERS: include the amounts from Section "
                    "H on Maryland Form 502CG or Form 504CG.' ⚠ The Section H line-3 instruction misprints IRC §408 / "
                    "§408A as '§458 / §458A' — encode against the statute and TB 58; the erratum is recorded, not fixed."
                ),
                "summary_text": "Section H is mandatory on both forms, computes column 2 from the apportionment factor, and carries no entity-level tax line — exactly what gets dropped.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "K-1 Section I + D5 routing, and the U3 erratum",
                "excerpt_text": (
                    "Section I: the member's share of the PTE's 500DM addition/subtraction modifications with the "
                    "code legend (1 Depreciation deductions (e, l, or j); 2 NOL deductions (f, m, or k); 3 Original "
                    "Issue Discounts (de); 4 Discharge of Business Indebtedness (cd); 5 Expensing Domestic R&E (da); "
                    "6 Business ATI Calculation (db); 7 IRC 168(n) Depreciation (dc)) — 'This amount should be "
                    "included in Column 3 of the Member's Form 500DM.' D5 routing: 'Corporate Members filing Form "
                    "500: ... List credit on Form 500CR. Resident individual members filing Form 502: list credit on "
                    "Form 502CR, Part CC, lines 6 and/or 9. ... Form 505: line 45 for credits from Form 510 and for "
                    "Electing PTEs, list credit on Form 502CR, Part CC, line 9. Form 510, line 16c, 16d, 16e, and "
                    "16f. Form 511, line 13c.' ⚠ U3: the D4 instruction's cross-reference to 'Form 511, Line 13C' is "
                    "an erratum for a 510 filer — build to Form 510 lines 16d/16e."
                ),
                "summary_text": "Section I carries the 500DM codes to the member's own 500DM line 9; the D4 'Form 511 Line 13C' pointer is a recorded erratum.",
                "is_key_excerpt": False,
            },
        ],
    },
    {
        "source_code": "MD_2025_FORM_510_511D",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "MD",
        "title": "2025 Form 510/511D — Declaration of Estimated Pass-Through Entity Income Tax",
        "citation": "Maryland Form 510/511D (2025), COM/RAD-073 08/25 — FINAL TY2025 (PDF ModDate 2026-02-12)",
        "issuer": "Comptroller of Maryland",
        "official_url": "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/forms/2025/510-511D.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.4,
        "topics": ["md_pte_election", "md_ptet_rate"],
        "excerpts": [
            {
                "excerpt_label": "510/511D — the Box A / Box B election and the estimated-tax worksheet",
                "excerpt_text": (
                    "MANDATORY: You must select either Box A or Box B. The choice you make on your first filing of "
                    "the tax year is irrevocable for the tax year; the same box must be checked with all subsequent "
                    "filings. Worksheet: L2 6.50% of line 1 + L3 2.25% of line 1 (nonresident individuals); L5 8.25% "
                    "(nonresident entities); L7 6.50% of line 6 + L8 2.25% of line 6 (RESIDENT individuals); L10 "
                    "8.25% (resident entities); L11 = Add lines 2, 3, 5, 7, 8, and 10; L12 = Line 11 divided by four. "
                    "A Box-B (non-electing) filer leaves lines 6-10 blank. Estimated tax is required when the tax is "
                    "expected to exceed $1,000; safe harbour is 90% of the current year or 110% of the prior year; "
                    "installments are due the 15th day of the 4th, 6th, 9th and 12th months for S corporations and "
                    "the 4th, 6th, 9th and 13th for partnerships, LLCs and business trusts."
                ),
                "summary_text": "One worksheet serves both election branches; $1,000 threshold, 90%/110% safe harbour, and two DIFFERENT installment calendars by entity type.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MD_2025_FORM_510_511E",
        "source_type": "state_form",
        "source_rank": "primary_official",
        "jurisdiction_code": "MD",
        "title": "2025 Form 510/511E — Application for Extension to File Pass-Through Entity Income Tax Return",
        "citation": "Maryland Form 510/511E (2025), COM/RAD-008 06/25 — FINAL TY2025; served at .../2025/511e.pdf, NOT 510-511e.pdf",
        "issuer": "Comptroller of Maryland",
        "official_url": "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/forms/2025/511e.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.4,
        "topics": ["md_pte_election"],
        "excerpts": [
            {
                "excerpt_label": "510/511E — THE FULLEST STATEMENT OF THE ELECTION, INCLUDING BOTH DEEMING DEFAULTS",
                "excerpt_text": (
                    "Irrevocable Election Checkboxes: For tax years beginning after December 31, 2022, the election "
                    "must be made, if at all, with the first filing of the tax year. Entities must check either Box A "
                    "to indicate they are electing to pay tax at the entity level with respect to all members' shares "
                    "or Box B to indicate they are paying tax only on behalf of nonresident members. An entity that "
                    "checks Box A must file Form 511 as the year-end return. An entity that checks Box B must file "
                    "Form 510 as the year-end return. Unless this extension is the first filing made for this tax "
                    "year, the same box that was checked on previous filings must be checked for this extension. IF "
                    "THIS IS YOUR FIRST FILING AND NEITHER BOX IS CHECKED, THE COMPTROLLER WILL DEEM YOU TO HAVE "
                    "CHOSEN TO PAY TAX ONLY ON BEHALF OF NONRESIDENT MEMBERS, AND THAT DECISION WILL BE IRREVOCABLE. "
                    "IF THIS IS YOUR FIRST FILING AND BOTH BOXES ARE CHECKED IN ERROR, THE COMPTROLLER WILL DEEM YOU "
                    "HAVE ELECTED TO PAY TAX AT THE ENTITY LEVEL WITH RESPECT TO ALL MEMBERS' SHARES, AND THAT "
                    "DECISION WILL BE IRREVOCABLE."
                ),
                "summary_text": "Both deeming defaults, verbatim: neither box -> Form 510; both boxes -> Form 511; each irrevocable.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "510/511E — extension conditions and the zero-tax first-filing trap",
                "excerpt_text": (
                    "An extension is granted only if (1) it is filed by the original due date, (2) An application for "
                    "extension of time has been filed with the IRS, and (3) Full payment of any balance due is "
                    "submitted with the application. It is granted for seven months for S corporations and six months "
                    "for other PTEs. 'IF NO TAX IS DUE WITH THIS EXTENSION, DO NOT MAIL THIS PAPER FORM UNLESS IT IS "
                    "THE FIRST FILING OF THE ENTITY.' Composite Return filers use Form EL102B instead."
                ),
                "summary_text": "Three grant conditions; 7 months S corp / 6 months other; a first-year entity must still file the paper form at zero tax because the election box must be set.",
                "is_key_excerpt": False,
            },
        ],
    },
    {
        "source_code": "MD_TG_10_102_1",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "MD",
        "title": "Md. Code, Tax-General §10-102.1 — Tax on pass-through entities",
        "citation": "Md. Code Ann., Tax-General §10-102.1(a)(2)-(a)(8), (b)(2), (c)(1)/(c)(3), (d)(1)-(d)(3), (f), (j). VINTAGE: TY2025 text = SB 787 of 2021",
        "issuer": "Maryland General Assembly",
        "official_url": "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-102.1&enactments=false",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["md_pte_election", "md_ptet_rate"],
        "excerpts": [
            {
                "excerpt_label": "§10-102.1(b)(2) — the elect-or-not construction, with NO mechanism",
                "excerpt_text": (
                    "Each pass-through entity: (i) shall pay the tax imposed under paragraph (1) of this subsection "
                    "with respect to the distributive shares or pro rata shares of the nonresident and nonresident "
                    "entity members of the pass-through entity; or (ii) may elect to pay the tax imposed under "
                    "paragraph (1) of this subsection with respect to the distributive shares or pro rata shares of "
                    "ALL members of the pass-through entity. — The statute prescribes NO election mechanism, NO "
                    "deadline and NO irrevocability. All of that is administrative and lives only on the Form "
                    "510/511D and 510/511E instructions."
                ),
                "summary_text": "The statute creates the two legs but not the election machinery — the mechanism, deadline and irrevocability are wholly administrative.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "§10-102.1(c) — TWO LEGALLY DIFFERENT TAXES, not two rates of one tax",
                "excerpt_text": (
                    "(c)(1): a non-electing PTE's tax 'shall be treated as a tax imposed on the nonresident or "
                    "nonresident entity members that is paid on behalf of the nonresidents ... by the pass-through "
                    "entity'. (c)(3): an electing PTE's tax 'shall be treated as a tax imposed on the pass-through "
                    "entity itself'. — This distinction is WHY the owner-side add-back attaches to K-1 Section D "
                    "lines 2 and 4 (the electing legs) and never to line 1."
                ),
                "summary_text": "The 510 tax is the member's own tax paid on their behalf; the 511 tax is the entity's own tax. That is the statutory basis for the D2/D4-only add-back.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "§10-102.1(d)(2) — the rate DERIVATION, and (d)(3) the DCF cap",
                "excerpt_text": (
                    "(d)(2): '(i) a rate equal to the sum of the rate of the tax imposed under § 10-106.1 of this "
                    "subtitle and the top marginal State tax rate for individuals under § 10-105(a) of this subtitle "
                    "applied to the sum of each individual member's distributive share or pro rata share of the "
                    "pass-through entity's taxable income; and (ii) the rate of the tax for a corporation under § "
                    "10-105(b) of this subtitle applied to the sum of each entity member's ... share'. (d)(1) is "
                    "word-for-word the same construction for the non-electing leg on 'nonresident taxable income'. "
                    "(d)(3): the tax 'may not exceed ... the sum of all of the [nonresident and nonresident entity / "
                    "all] members' shares of the pass-through entity's distributable cash flow'."
                ),
                "summary_text": "The PTET rate is a DERIVED constant (2.25% + 6.50% = 8.75%; corporate 8.25%) that moves automatically with the top bracket or the lowest county rate; (d)(3) is the DCF cap.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "§10-102.1(a)(8) TY2025 vintage, and the exemptions at (f)/(j)",
                "excerpt_text": (
                    "TY2025 definition (SB 787 of 2021, quoted verbatim in Technical Bulletin No. 6 §I.A): "
                    "\"Pass-through entity's taxable income\" means the portion of a pass-through entity's income "
                    "under the federal Internal Revenue Code, calculated without regard to any deduction for taxes "
                    "based on net income that are imposed by any state or political subdivision of a state, that is "
                    "derived from or reasonably attributable to the trade or business of the pass-through entity in "
                    "this State. ⚠ The (i)/(ii) resident-vs-nonresident split now served by mgaleg is the 2025 BRFA "
                    "(Ch. 604) amendment, postponed to TY2027 by the 2026 BRFA — it does NOT apply to TY2025. "
                    "(f)(1)/(f)(2): the non-electing leg does not apply to a resident PTE member, a §856 REIT, or a "
                    "§501 organization. (j): nor to a publicly traded PTE filing the annual >$500 information return."
                ),
                "summary_text": "One Maryland-source base for ALL members in TY2025; the resident/nonresident split is a TY2027 change. Exemptions at (f) are scoped to the non-electing leg (U6).",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MD_TG_10_105_106_1",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "MD",
        "title": "Md. Code, Tax-General §10-105 and §10-106.1 — the two PTET rate inputs",
        "citation": "Md. Code Ann., Tax-General §10-105(a) (top marginal 6.50%, BRFA 2025 Ch. 604), §10-105(b) (corporate 8.25%), §10-106.1(b) (lowest county rate 2.25%)",
        "issuer": "Maryland General Assembly",
        "official_url": "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-106.1&enactments=false",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["md_ptet_rate"],
        "excerpts": [
            {
                "excerpt_label": "The two rate inputs, verbatim",
                "excerpt_text": (
                    "§10-106.1(b): 'The rate of the tax imposed under this section shall be equal to the lowest county "
                    "income tax rate set by any Maryland county in accordance with § 10-106 of this subtitle.' For "
                    "TY2025 that is 2.25% (Worcester County; all 24 rates verified in md_conformity.md §12). "
                    "§10-105(a): the top marginal individual rate for TY2025 is 6.50% ('6.50% of Maryland taxable "
                    "income in excess of $1,000,000'), a NEW bracket added by the Budget Reconciliation and Financing "
                    "Act of 2025 (HB 352, Ch. 604) for tax years beginning after 12/31/2024. §10-105(b): 'The State "
                    "income tax rate for a corporation is 8.25% of Maryland taxable income.' 6.50% + 2.25% = 8.75%."
                ),
                "summary_text": "2.25% + 6.50% = 8.75% for individual/fiduciary members; 8.25% for entity members. The BRFA's new top bracket moved the PTET from 8.00% automatically.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MD_TG_10_701_1",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "MD",
        "title": "Md. Code, Tax-General §10-701.1 — Credit for tax paid by a pass-through entity",
        "citation": "Md. Code Ann., Tax-General §10-701.1; read with §10-306(b)(6) -> §10-205(m) for corporate members",
        "issuer": "Maryland General Assembly",
        "official_url": "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-701.1&enactments=false",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["md_pte_owner_side"],
        "excerpts": [
            {
                "excerpt_label": "§10-701.1 — the credit leg (leg 1 of 2)",
                "excerpt_text": (
                    "A member of a pass-through entity may claim a credit against the income tax for a taxable year "
                    "in the amount of tax paid by a pass-through entity under § 10-102.1 of this title that is "
                    "attributable to the member's share of the pass-through entity's taxable income, as defined in § "
                    "10-102.1(a)(8) of this title. — Routed by K-1 Section D line 5 to Form 502CR Part CC line 9 "
                    "(individuals), Form 500CR (corporations), Form 504 (fiduciaries), Form 505 line 45 (510 "
                    "credits), and Form 510 lines 16c-16f / Form 511 line 13c (PTE members). ⚠ The statute grants a "
                    "CREDIT only — the mandatory income ADD-BACK is a separate obligation on the K-1 form face."
                ),
                "summary_text": "The statutory credit. Implementing only the credit silently overstates owner relief by the full PTET — the classic Maryland PTET bug.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MD_TG_10_402_401",
        "source_type": "state_statute",
        "source_rank": "controlling",
        "jurisdiction_code": "MD",
        "title": "Md. Code, Tax-General §10-402 and §10-401 — apportionment and nonresident allocation",
        "citation": "Md. Code Ann., Tax-General §10-402(d)(2)(v) (single sales factor after 12/31/2021), §10-402(e) (Comptroller may alter), §10-401(1)-(2)",
        "issuer": "Maryland General Assembly",
        "official_url": "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-402&enactments=false",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.5,
        "topics": ["md_pte_apportionment"],
        "excerpts": [
            {
                "excerpt_label": "§10-402(e) / §10-401(2) — ONLY THE COMPTROLLER MAY ALTER A FORMULA",
                "excerpt_text": (
                    "§10-402(e): 'To reflect clearly the income allocable to Maryland, THE COMPTROLLER MAY ALTER, if "
                    "circumstances warrant, the methods under subsections (c) and (d) of this section, including: (1) "
                    "the use of the separate accounting method; (2) the use of the 3-factor double weighted sales "
                    "factor formula method or the single sales factor formula method; (3) THE WEIGHT OF ANY FACTOR in "
                    "the 3-factor formula; (4) the valuation of rented property ...; and (5) the determination of the "
                    "extent to which tangible personal property is located in the State.' §10-401(2): allocation by "
                    "'separate accounting, if the Comptroller allows; or ... the method that the Comptroller "
                    "requires'. ⚠ NEGATIVE FINDING: the word 'insignificant' appears NOWHERE in §10-402, §10-401, "
                    "COMAR 03.04.03.08/.09/.10, Administrative Release 43, the Corporate Booklet or either PTE "
                    "Booklet — re-tested with 'de minimis', 'omit', 'eliminat', 'disregard', 'not material', "
                    "'nominal' and 'zero'. Maryland has NO insignificant-denominator rule; that is Fla. Stat. §220.15(1)."
                ),
                "summary_text": "Altering a formula is the Comptroller's act, never the preparer's or the software's — and Maryland has no insignificant-denominator reweighting rule at all.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MD_COMAR_03_04_03_08",
        "source_type": "state_regulation",
        "source_rank": "primary_official",
        "jurisdiction_code": "MD",
        "title": "COMAR 03.04.03.08 — Apportionment of Income (with .10, manufacturing single sales factor)",
        "citation": "COMAR 03.04.03.08 B(2), B(5), C(3)-(7), D; COMAR 03.04.03.10 B(1), D(1), F(2)",
        "issuer": "Comptroller of the Treasury",
        "official_url": "https://regs.maryland.gov/us/md/exec/comar/03.04.03.08",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.2,
        "topics": ["md_pte_apportionment"],
        "excerpts": [
            {
                "excerpt_label": "COMAR .08 B(5) — a factor must exist even on a loss return",
                "excerpt_text": (
                    "If a return is filed by a corporation operating within and outside the State which reflects a "
                    "loss with no income to be apportioned, an apportionment factor shall be calculated for the "
                    "filing to be considered complete. — B(2): 'Each factor shall be separately determined and the "
                    "number of factors used shall be averaged to arrive at the final apportionment factor.' For "
                    "TY2025 the general formula is a SINGLE receipts factor, so there is nothing to average; B(2) can "
                    "only bite inside a multi-factor SPECIAL formula (airline; the worldwide-HQ election)."
                ),
                "summary_text": "A factor is always computed — never dropped. The only averaging concept applies inside multi-factor special formulas, not the general single-receipts formula.",
                "is_key_excerpt": True,
            },
            {
                "excerpt_label": "COMAR .10 — the OTHER manufacturing rule (page-3 Q8), not the carve-out",
                "excerpt_text": (
                    "COMAR 03.04.03.10 B(1)/B(2): 'manufacturing corporation' under the NAICS 1997 EDITION, sector "
                    "11, 31, 32, or 33, excluding refiners, 'An affiliated or commonly controlled corporation that "
                    "engages in activities on behalf of a manufacturing corporation' and 'An affiliated or "
                    "unaffiliated service provider'. D(1): the two >50% tests. F(2): the >25-employee report applies "
                    "only 'For each taxable year beginning after December 31, 2005, but before January 1, 2011' — "
                    "EXPIRED. ⚠ Contrast §10-210.1(a)(4): NAICS 2012 EDITION, Sectors 31/32/33, no employee test, "
                    "'manufacturing ENTITY'. Two different rules; never conflate them."
                ),
                "summary_text": "Page-3 Q8's terminology ('manufacturing corporation', '>25 employees') is COMAR .10's, not §10-210.1's. Different NAICS edition, different sectors, expired report (U8).",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MD_TB_6_PTE",
        "source_type": "state_conformity_notice",
        "source_rank": "primary_official",
        "jurisdiction_code": "MD",
        "title": "Technical Bulletin No. 6 — Taxation of Pass-Through Entities",
        "citation": "Comptroller of Maryland, Technical Bulletin No. 6, issued 12/27/2023, §§I.A-I.C, II.A-II.B. ⚠ TY2023-KEYED — its composite rate is stale for TY2025",
        "issuer": "Comptroller of Maryland",
        "official_url": "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/legal-publications/technical-bulletins/tb-it6.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.0,
        "topics": ["md_pte_election", "md_pte_owner_side"],
        "excerpts": [
            {
                "excerpt_label": "TB 6 §I.A/§I.B — THE TY2025 INCOME BASE (the source that withdrew U2/W3)",
                "excerpt_text": (
                    "TB 6 quotes the operative TY2025 §10-102.1(a)(8) text (SB 787 of 2021): PTE taxable income is "
                    "'the portion of a pass-through entity's income under the federal Internal Revenue Code, "
                    "calculated without regard to any deduction for taxes based on net income that are imposed by any "
                    "state or political subdivision of a state, that is derived from or reasonably attributable to "
                    "the trade or business of the pass-through entity in this State' — ONE Maryland-source rule for "
                    "ALL members — followed by 'Multistate electing PTEs must apportion their income.' §II.A: 'The "
                    "term \"member\" does not include a Real Estate Investment Trust as defined by § 856 ..., an "
                    "organization exempt under the Internal Revenue Code (including IRA's, Keoghs, pension and "
                    "profit-sharing plans ...), or any other tax-exempt entity listed in TG § 10-104.' Also: 'A "
                    "nonelection may not be changed to an election on an amended return.' TB 6 is SILENT on whether "
                    "the DCF limitation may be elected on an amended return (U7)."
                ),
                "summary_text": "TB 6 settles the TY2025 base (Maryland-source for all members, apportioned) and supplies the U6 footing for excluding REIT/§408(e)/§501 members. It says nothing barring a DCF election on an amended return.",
                "is_key_excerpt": True,
            },
        ],
    },
    {
        "source_code": "MD_COMP_ALERT_PTE_TY2026",
        "source_type": "state_conformity_notice",
        "source_rank": "primary_official",
        "jurisdiction_code": "MD",
        "title": "Tax Alert — Changes to Tax Year 2026 Pass-Through Entity Estimated Payments",
        "citation": "Comptroller of Maryland, Tax Alert effective 4/13/2026 (PDF ModDate 2026-04-20) — the vintage authority for the TY2025 base and the TY2027 postponement",
        "issuer": "Comptroller of Maryland",
        "official_url": "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/legal-publications/alerts/tax-alert-changes-to-tax-year-2026-pass-through-entity-estimated-payments.pdf",
        "current_status": "active",
        "is_substantive_authority": True,
        "trust_score": 9.3,
        "topics": ["md_pte_election"],
        "excerpts": [
            {
                "excerpt_label": "Tax Alert 4/13/2026 — TY2025 base confirmed, TY2027 change calendared, TY2026 timing relief",
                "excerpt_text": (
                    "'The Budget Reconciliation and Financing Act of 2026 ... postponed any alterations of the "
                    "calculation of a PTE's taxable income to tax year 2027. ... For tax year 2026, the tax on "
                    "electing PTEs will be imposed on resident and nonresident shares attributable to Maryland only, "
                    "AS IT WAS IN TAX YEAR 2025.' Also: for TY2026 only, the Comptroller 'will ignore any election or "
                    "nonelection made with the first quarter estimated payment, and will, instead, honor the election "
                    "or nonelection made with the next filing or payment for tax year 2026 made after April 15, "
                    "2026'. And: 'any overpayment made by the PTE is refunded to the PTE, and is not distributable to "
                    "the members' (corroborating the K-1 D3 RESERVED / FC-GEN outcome)."
                ),
                "summary_text": "Confirms the TY2025 base, dates the TY2027 re-spec of MD_511 lines 2-4, and suspends the 'first filing wins' rule for TY2026 only — which is why the election machine is year-keyed.",
                "is_key_excerpt": True,
            },
        ],
    },
]

AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    ("MD_2025_FORM_510", FORM_510, "governs"),
    ("MD_2025_PTE_BOOKLET_510", FORM_510, "governs"),
    ("MD_2025_FORM_511", FORM_511, "governs"),
    ("MD_2025_PTE_BOOKLET_511", FORM_511, "governs"),
    ("MD_2025_SCH_K1_510_511", FORM_510, "informs"),
    ("MD_2025_SCH_K1_510_511", FORM_511, "informs"),
    ("MD_2025_FORM_510_511D", FORM_510, "governs"),
    ("MD_2025_FORM_510_511D", FORM_511, "governs"),
    ("MD_2025_FORM_510_511E", FORM_510, "governs"),
    ("MD_2025_FORM_510_511E", FORM_511, "governs"),
    ("MD_TG_10_102_1", FORM_510, "governs"),
    ("MD_TG_10_102_1", FORM_511, "governs"),
    ("MD_TG_10_105_106_1", FORM_510, "governs"),
    ("MD_TG_10_105_106_1", FORM_511, "governs"),
    ("MD_TG_10_701_1", FORM_510, "informs"),
    ("MD_TG_10_701_1", FORM_511, "informs"),
    ("MD_TG_10_402_401", FORM_510, "governs"),
    ("MD_TG_10_402_401", FORM_511, "governs"),
    ("MD_COMAR_03_04_03_08", FORM_510, "informs"),
    ("MD_COMAR_03_04_03_08", FORM_511, "informs"),
    ("MD_TB_6_PTE", FORM_510, "informs"),
    ("MD_TB_6_PTE", FORM_511, "informs"),
    ("MD_COMP_ALERT_PTE_TY2026", FORM_511, "informs"),
]


# ═══════════════════════════════════════════════════════════════════════════
# SHARED FACTS — the election state (identical inputs on both forms, because
# the election is a TAX-YEAR fact, not a return fact).
# ═══════════════════════════════════════════════════════════════════════════

def _election_facts() -> list[dict]:
    return [
        {"fact_key": "election_first_filing_kind",
         "label": "First filing of the tax year (the filing that SET the election)",
         "data_type": "choice", "required": True, "sort_order": 1,
         "choices": ["510_511D", "510_511E", "year_end_return", "unknown"],
         "notes": ("W1. The election is made with the FIRST filing of the tax year and is IRREVOCABLE. "
                   "'unknown' is a legitimate value and MUST raise the undetermined diagnostic — the spec "
                   "never infers the election from the return's own computed values.")},
        {"fact_key": "election_box_a_checked",
         "label": "Box A checked on the first filing (elect to pay tax on ALL members' shares)?",
         "data_type": "boolean", "required": True, "sort_order": 2,
         "notes": "Box A -> Form 511. Both boxes checked in error -> DEEMED Form 511, irrevocably."},
        {"fact_key": "election_box_b_checked",
         "label": "Box B checked on the first filing (pay tax only on behalf of nonresident members)?",
         "data_type": "boolean", "required": True, "sort_order": 3,
         "notes": "Box B -> Form 510. NEITHER box checked on a first filing -> DEEMED Form 510, irrevocably."},
        {"fact_key": "election_recorded_form",
         "label": "Recorded year-end return required by the election (MD_510 / MD_511 / undetermined)",
         "data_type": "choice", "required": True, "sort_order": 4,
         "choices": [FORM_510, FORM_511, "undetermined"],
         "notes": ("W1 — Ken's call on WHERE this state lives (return-level flag vs client-level attribute vs a "
                   "first-filing record). Carried across filings inside the tax year and locked.")},
        {"fact_key": "is_amended_return", "label": "Amended return?", "data_type": "boolean",
         "required": False, "sort_order": 5,
         "notes": "'A PTE may not file an amended return to change the PTE's election or non-election for the tax year.'"},
        {"fact_key": "entity_type_checkbox", "label": "TYPE OF ENTITY (page 1 checkbox)",
         "data_type": "choice", "required": True, "sort_order": 6,
         "choices": ["s_corporation", "partnership", "limited_liability_company", "business_trust"],
         "notes": "Drives the Schedule A method gate (S corps must apportion unless nonunitary), the installment calendar and the extension length."},
        {"fact_key": "is_first_filing_of_entity", "label": "First filing of the entity (page 1 checkbox)",
         "data_type": "boolean", "required": False, "sort_order": 7},
        {"fact_key": "is_inactive_entity", "label": "Inactive entity (page 1 checkbox)", "data_type": "boolean",
         "required": False, "sort_order": 8},
        {"fact_key": "is_final_return", "label": "Final Return (page 1 checkbox)", "data_type": "boolean",
         "required": False, "sort_order": 9},
        {"fact_key": "is_multistate", "label": "Multistate pass-through entity?", "data_type": "boolean",
         "required": True, "sort_order": 10,
         "notes": "Gates the ALLOCATION OF INCOME block. The gate DIFFERS between the forms — see each form's ALLOC rule."},
        {"fact_key": "allocation_method", "label": "Allocation method (separate accounting L3a vs apportionment L3b)",
         "data_type": "choice", "required": False, "sort_order": 11,
         "choices": ["separate_accounting", "apportionment"],
         "notes": "'Partnerships may use separate accounting or the apportionment method. S corporations must use the apportionment method unless the activity in Maryland is nonunitary.'"},
        {"fact_key": "f1120s_line_23a", "label": "Federal Form 1120-S line 23a (excess net passive income / LIFO recapture tax)",
         "data_type": "decimal", "required": False, "sort_order": 12,
         "notes": "R6 / W10 trigger — an S corp with federal corporate-level tax files Form 500 IN ADDITION to Form 510/511."},
        {"fact_key": "f1120s_line_23b", "label": "Federal Form 1120-S line 23b (tax from Schedule D)",
         "data_type": "decimal", "required": False, "sort_order": 13,
         "notes": "R6 / W10 trigger."},
    ]


def _k1_facts(sort_base: int, form_number: str) -> list[dict]:
    """Schedule K-1 (510/511) emitter inputs shared by both forms."""
    facts = [
        {"fact_key": "k1_section_b_additions", "label": "K-1 Section B additions (lines 1-5, direct-entry)",
         "data_type": "decimal", "required": False, "sort_order": sort_base,
         "notes": "⚠ For electing PTEs, do NOT include the member's addback of the electing PTE credit here."},
        {"fact_key": "k1_section_c_subtractions", "label": "K-1 Section C subtractions (lines 1-5, direct-entry)",
         "data_type": "decimal", "required": False, "sort_order": sort_base + 1},
        {"fact_key": "k1_section_e_credits_present", "label": "K-1 Section E credits used (lines 1-28; 13 and 23 print RESERVED)?",
         "data_type": "boolean", "required": False, "sort_order": sort_base + 2,
         "notes": "R4 RED-defer: 26 NAMED credits across lines 1-28. Triggers the conditional e-file mandate."},
        {"fact_key": "k1_one_maryland_used", "label": "K-1 One Maryland Economic Development blocks used (lines 29a-32 / 33a-39)?",
         "data_type": "boolean", "required": False, "sort_order": sort_base + 3, "notes": "R5 RED-defer."},
        {"fact_key": "k1_section_f_mw506nrs", "label": "K-1 Section F — member's share of MW506NRS withholding",
         "data_type": "decimal", "required": False, "sort_order": sort_base + 4, "notes": "R8 RED-defer."},
        {"fact_key": "k1_section_h_col1_rows", "label": "K-1 Section H column 1 — federal net capital gain, rows 1-7 (direct-entry)",
         "data_type": "string", "required": False, "sort_order": sort_base + 5,
         "notes": ("W7. Column 2 is COMPUTED (column 1 x the apportionment factor). Row 3 is resident-members-only "
                   "(column 2 blocked out). Row sources: federal Sch. K-1, 8949, 6252, 4797, 8824.")},
        {"fact_key": "k1_section_i_500dm_shares", "label": "K-1 Section I — member's share of the PTE's 500DM modifications with codes",
         "data_type": "string", "required": False, "sort_order": sort_base + 6,
         "notes": "R9. The PTE computes NOTHING on 500DM; it attaches the form and passes each member's share through with the codes."},
        {"fact_key": "upstream_pte_k1_count", "label": "Number of upstream PTE Schedule K-1 (510/511) forms received",
         "data_type": "integer", "required": False, "sort_order": sort_base + 7,
         "notes": "R11 RED-defer: more than one level of tiered-PTE credit chain is not computed in v1."},
    ]
    return facts


# ═══════════════════════════════════════════════════════════════════════════
# FORM MD_510 — Pass-Through Entity Income Tax Return (NON-ELECTING)
# ═══════════════════════════════════════════════════════════════════════════

MD510_FACTS: list[dict] = _election_facts() + [
    # --- Member counts, lines 1a-1e ---
    {"fact_key": "count_1a_resident_individuals", "label": "1a — Individual (including fiduciary) residents of Maryland (count)",
     "data_type": "integer", "required": False, "sort_order": 20,
     "notes": "Counted but NOT taxed on Form 510."},
    {"fact_key": "count_1b_nonresident_individuals", "label": "1b — Individual (including fiduciary) nonresidents (count)",
     "data_type": "integer", "required": False, "sort_order": 21,
     "notes": "Fiduciaries live HERE, in the individual leg — never in the entity leg."},
    {"fact_key": "count_1c_nonresident_entities", "label": "1c — Nonresident entities (count)",
     "data_type": "integer", "required": False, "sort_order": 22,
     "notes": "⚠ On Form 511 this box reads 'Nonresident AND RESIDENT entities'. On the 510 it is nonresident only."},
    {"fact_key": "count_1d_others", "label": "1d — Others (resident entities + IRC §408(e)/§501 exempt entities) (count)",
     "data_type": "integer", "required": False, "sort_order": 23,
     "notes": "⚠ W6. A RESIDENT ENTITY member sits here on the 510 and is UNTAXED. On the 511 it moves to 1c and is taxed at 8.25%."},
    # --- Income, lines 2-4 ---
    {"fact_key": "fed_1065_sch_k_lines_1_11", "label": "Federal Form 1065 Schedule K lines 1-11, net (partnerships)",
     "data_type": "decimal", "required": False, "sort_order": 30,
     "notes": "Verified on the FINAL 2025 IRS Form 1065: L11 = 'Other income (loss)', L12 = 'Section 179 deduction' (correctly outside the range)."},
    {"fact_key": "fed_1120s_sch_k_lines_1_10", "label": "Federal Form 1120-S Schedule K lines 1-10, net (S corporations)",
     "data_type": "decimal", "required": False, "sort_order": 31,
     "notes": "Verified on the FINAL 2025 IRS Form 1120-S: L10 = 'Other income (loss)', L11 = 'Section 179 deduction'."},
    {"fact_key": "federal_obligations_interest", "label": "Interest from federal obligations (subtracted from the line 2 base)",
     "data_type": "decimal", "required": False, "sort_order": 32,
     "notes": "Booklet 510 line 2: 'the net amount of income/loss for the PTE, LESS interest from federal obligations'."},
    {"fact_key": "non_maryland_income_sep_acct", "label": "3a — Non-Maryland income (entities using separate accounting)",
     "data_type": "decimal", "required": False, "sort_order": 33},
    # --- Ownership percentages, lines 5 / 10 ---
    {"fact_key": "pct_nonresident_individuals_l5", "label": "5 — Percentage of ownership by individual nonresident members (BLANK = 100%)",
     "data_type": "decimal", "required": False, "sort_order": 40,
     "notes": "⚠ FORM 510 CONVENTION: 'If 100%, leave blank and enter the amount from line 4 on line 6.' The 511 uses 9999 instead."},
    {"fact_key": "pct_nonresident_entities_l10", "label": "10 — Percentage of ownership by nonresident entities (BLANK = 100%)",
     "data_type": "decimal", "required": False, "sort_order": 41,
     "notes": "Profit/loss percentage may be used instead, which the software cannot derive — direct-entry."},
    # --- DCF worksheet 9A ---
    {"fact_key": "dcf_worksheet_used", "label": "14 — Distributable cash flow limitation worksheet used? (checkbox)",
     "data_type": "boolean", "required": False, "sort_order": 50,
     "notes": "⚠ W5. The L15 lesser-of applies ONLY when this is checked. Unconditional MIN() zeroes the tax when L14 is blank."},
    {"fact_key": "dcf_b_cash_method_restatement", "label": "Worksheet 9A B — cash-method restatement", "data_type": "decimal", "required": False, "sort_order": 51},
    {"fact_key": "dcf_c_non_includable_receipts", "label": "Worksheet 9A C — non-includable cash receipts (capital contributions, loan proceeds)", "data_type": "decimal", "required": False, "sort_order": 52},
    {"fact_key": "dcf_d_depreciation_addback", "label": "Worksheet 9A D — depreciation/amortization/depletion add-back", "data_type": "decimal", "required": False, "sort_order": 53},
    {"fact_key": "dcf_e_liability_reserve_decrease", "label": "Worksheet 9A E — decrease in liability reserve", "data_type": "decimal", "required": False, "sort_order": 54},
    {"fact_key": "dcf_g_non_deductible_expenditures", "label": "Worksheet 9A G — non-deductible cash expenditures (excluding member distributions)", "data_type": "decimal", "required": False, "sort_order": 55},
    {"fact_key": "dcf_h_liability_reserve_increase", "label": "Worksheet 9A H — increase in liability reserve", "data_type": "decimal", "required": False, "sort_order": 56},
    {"fact_key": "dcf_l_nonresident_tax_prev_paid", "label": "Worksheet 9A L — nonresident tax previously paid with 510/511D or 510/511E", "data_type": "decimal", "required": False, "sort_order": 57},
    # --- Payments 16a-16g ---
    {"fact_key": "pay_16a_estimated", "label": "16a — Estimated PTE nonresident tax paid with Form 510/511D (and prior year overpayment)", "data_type": "decimal", "required": False, "sort_order": 60},
    {"fact_key": "pay_16b_extension", "label": "16b — PTE nonresident tax paid with an extension request (Form 510/511E)", "data_type": "decimal", "required": False, "sort_order": 61},
    {"fact_key": "pay_16c_credit_from_other_pte", "label": "16c — Credit for nonresident tax paid on behalf of the PTE by another PTE", "data_type": "decimal", "required": False, "sort_order": 62},
    {"fact_key": "pay_16d_credit_nonres_shares", "label": "16d — Credit for entity-level tax paid by another PTE on this entity's NONRESIDENT shares", "data_type": "decimal", "required": False, "sort_order": 63,
     "notes": "U3: the K-1 D4 instruction misdirects this to 'Form 511, Line 13C'. Build to 16d/16e."},
    {"fact_key": "pay_16e_credit_res_shares", "label": "16e — Credit for entity-level tax paid by another PTE on this entity's RESIDENT shares", "data_type": "decimal", "required": False, "sort_order": 64},
    {"fact_key": "pay_16f_mw506nrs", "label": "16f — Payment made with Form MW506NRS", "data_type": "decimal", "required": False, "sort_order": 65, "notes": "R8 RED-defer."},
    {"fact_key": "pay_16g_amended_prior_payments", "label": "16g — If amending, total payments made with original plus additional tax paid after", "data_type": "decimal", "required": False, "sort_order": 66,
     "notes": "U5: Booklet 510 Instruction 8 wrongly points at line 16b (the extension line). The face governs — 16g."},
    {"fact_key": "prior_overpayment_18a", "label": "18a — If amending, prior overpayment (total all refunds previously issued)", "data_type": "decimal", "required": False, "sort_order": 67},
    {"fact_key": "interest_penalty_500up_19", "label": "19 — Interest and/or penalty from Form 500UP or late payment interest", "data_type": "decimal", "required": False, "sort_order": 68, "notes": "R7 RED-defer."},
    {"fact_key": "overpayment_applied_next_year", "label": "21 — Overpayment applied to next year's estimated tax", "data_type": "decimal", "required": False, "sort_order": 69},
    # --- Composite / defer triggers ---
    {"fact_key": "box_510c_filed", "label": "510C Filed (page 1 checkbox — Form 510 only)", "data_type": "boolean", "required": False, "sort_order": 70,
     "notes": "R1 RED-defer. ⚠ There is NO 510C Filed box on Form 511 — an Electing PTE may not file a composite."},
    {"fact_key": "is_publicly_traded_pte", "label": "Publicly traded pass-through entity (§10-102.1(j))?", "data_type": "boolean", "required": False, "sort_order": 71, "notes": "R12 — enter code 704; a PTP should NOT file Form 511."},
    {"fact_key": "is_investment_partnership", "label": "Investment partnership (Booklet 510 Instruction 9 NOTE 2)?", "data_type": "boolean", "required": False, "sort_order": 72, "notes": "R13 — enter code 705. Brokerage firms dealing with the general public are NOT exempt."},
    {"fact_key": "is_501_pte_with_fti", "label": "IRC §501-exempt PTE with federal taxable income (26 CFR §301.7701-3(c)(1)(v)(A))?", "data_type": "boolean", "required": False, "sort_order": 73, "notes": "R15 — must still file Form 510 or Form 511."},
    {"fact_key": "has_decoupling_modification", "label": "Any Maryland decoupling modification present (Form 500DM must be attached)?", "data_type": "boolean", "required": False, "sort_order": 74, "notes": "R9 — the PTE computes nothing but MUST attach 500DM and pass shares through K-1 Section I."},
] + _schedule_a_facts(300) + _page3_facts(400) + _k1_facts(500, FORM_510)

MD510_RULES: list[dict] = [
    {"rule_id": "R-MD510-ELECT", "title": "Election state machine — Form 510 is legal ONLY for a non-electing PTE",
     "rule_type": "routing", "sort_order": 1,
     "formula": ("election = f(election_first_filing_kind, election_box_a_checked, election_box_b_checked) ; "
                 "510_511D|510_511E: A&B -> MD_511 (DEEMED) ; A -> MD_511 ; B -> MD_510 ; neither -> MD_510 (DEEMED) ; "
                 "year_end_return: filing MD_510 IS the irrevocable non-election ; "
                 "unknown -> UNDETERMINED (ERROR diagnostic, never inferred) ; "
                 "if election_recorded_form == MD_511 -> HARD BLOCK: STOP, file Form 511 ; "
                 "is_amended_return cannot change the election"),
     "inputs": ["election_first_filing_kind", "election_box_a_checked", "election_box_b_checked",
                "election_recorded_form", "is_amended_return"],
     "outputs": ["required_year_end_form"],
     "description": ("W1 — THE DEFINING STRUCTURAL FACT. 510 and 511 are mutually exclusive and the choice was made "
                     "months earlier on Form 510/511D or 510/511E. Nothing on the year-end return's own data reveals "
                     "it, so the spec REQUIRES the recorded election and refuses to guess. Irrevocable; not curable "
                     "on an amended return. Year-keyed: 'first filing wins' is suspended for TY2026 only."),
     "exceptions": "TY2026 only — the Comptroller ignores an election made with the Q1 estimated payment (Tax Alert eff. 4/13/2026)."},
    {"rule_id": "R-MD510-MEMBER", "title": "Member classification into lines 1a-1e (nonresidents only are taxed)",
     "rule_type": "classification", "sort_order": 2,
     "formula": ("resident individual/fiduciary -> 1a (UNTAXED) ; nonresident individual/fiduciary -> 1b (6.50% + 2.25%) ; "
                 "nonresident entity -> 1c (8.25%) ; RESIDENT ENTITY -> 1d 'Others' (UNTAXED) ; "
                 "REIT / IRC 408(e) / 501 exempt -> 1d (UNTAXED) ; 1e = 1a + 1b + 1c + 1d"),
     "inputs": ["count_1a_resident_individuals", "count_1b_nonresident_individuals",
                "count_1c_nonresident_entities", "count_1d_others"],
     "outputs": ["1a", "1b", "1c", "1d", "1e"],
     "description": ("W6. Fiduciaries sit inside the INDIVIDUAL legs ('the term individual includes fiduciaries'). "
                     "⚠ THE RESIDENT ENTITY MEMBER: line 1d here and untaxed; line 1c on Form 511 and taxed at 8.25%. "
                     "Cross-foot Schedule B Parts I+II to 1a+1b and Parts III+IV to 1c/1d."),
     "notes": "U6: REIT/§408(e)/§501 exclusion rests on TB 6 §II.A + TG §10-104 — re-verify §10-104 before seeding."},
    {"rule_id": "R-MD510-L2", "title": "Line 2 — total distributive or pro rata share of income per the federal return",
     "rule_type": "calculation", "sort_order": 3,
     "formula": ("partnership: L2 = net(1065 Sch. K lines 1-11) - federal_obligations_interest ; "
                 "S corporation: L2 = net(1120S Sch. K lines 1-10) - federal_obligations_interest ; "
                 "unistate entities, and multistate entities with no nonresident members, also enter this amount on line 4"),
     "inputs": ["fed_1065_sch_k_lines_1_11", "fed_1120s_sch_k_lines_1_10", "federal_obligations_interest", "entity_type_checkbox"],
     "outputs": ["2"],
     "description": ("⚠ The NON-ELECTING base. Unlike Form 511 line 2 there is NO SALT add-back here — that is the "
                     "single largest base difference between the two returns.")},
    {"rule_id": "R-MD510-ALLOC", "title": "Lines 3a/3b -> line 4 — allocation gated on multistate AND nonresident members",
     "rule_type": "conditional", "sort_order": 4,
     "formula": ("if not is_multistate or no nonresident members: L4 = L2 ; "
                 "elif allocation_method == separate_accounting: L4 = L2 - L3a ; "
                 "else: L4 = L2 x L3b   [L3b = Schedule A line 4; if the factor is zero, enter .000001]"),
     "inputs": ["is_multistate", "allocation_method", "non_maryland_income_sep_acct", "entity_type_checkbox"],
     "outputs": ["3a", "3b", "4"],
     "description": ("⚠ THE GATE DIFFERS FROM THE 511. Form 510: 'To be completed by multistate PTEs WITH NONRESIDENT "
                     "MEMBERS - unistate entities, and multistate entities with no nonresidents, go to line 4.' Form "
                     "511 has no such qualifier — EVERY multistate 511 allocates. Method gate: partnerships may use "
                     "separate accounting; S corporations must apportion unless the Maryland activity is nonunitary.")},
    {"rule_id": "R-MD510-APPORT", "title": "Schedule A — single receipts factor, six decimals, .000001 floor, NEVER reweighted",
     "rule_type": "calculation", "sort_order": 5,
     "formula": ("column 3 = column 1 / column 2 rounded to SIX places ; SchA-4 = receipts factor (SchA-1h col 3) "
                 "unless a Comptroller-accepted special/alternative factor is entered ; "
                 "if factor == 0: enter .000001 on line 3b ; "
                 "property and payroll factors are developed only for intangible-sale income or a special formula and "
                 "NEVER reweight the receipts factor"),
     "inputs": ["scha_1a_md", "scha_1a_everywhere", "scha_special_or_alternative_checked", "scha_accepted_alternative_factor"],
     "outputs": ["SchA-1h", "SchA-2g", "SchA-3c", "SchA-4", "3b"],
     "description": ("⚠⚠ W9 / U11. MARYLAND HAS NO INSIGNIFICANT-DENOMINATOR RULE — that rule is Fla. Stat. "
                     "§220.15(1). Maryland's convention is the OPPOSITE: a zero factor is FLOORED at .000001 (form "
                     "face only; it is in neither booklet), and COMAR 03.04.03.08 B(5) requires a factor even on a "
                     "loss return. Only the Comptroller may alter a formula (§10-402(e); §10-401(2)). The software "
                     "must NEVER auto-drop, auto-reweight or auto-substitute a factor."),
     "exceptions": "Special (rental/leasing, financial institutions, transportation, worldwide-HQ) and Alternative formulas are RED-deferred (R2/R3) — the preparer enters the accepted factor."},
    {"rule_id": "R-MD510-GATE", "title": "Completion gate — lines 5 through 19 only if line 1b or line 1c has an entry",
     "rule_type": "conditional", "sort_order": 6,
     "formula": "complete_lines_5_to_19 = (count_1b_nonresident_individuals > 0) or (count_1c_nonresident_entities > 0)",
     "inputs": ["count_1b_nonresident_individuals", "count_1c_nonresident_entities"],
     "outputs": ["gate_5_19"],
     "description": ("Form face, verbatim: 'Complete lines 5 through 19 if there is an entry on line 1b or line 1c. "
                     "Tax is calculated only for nonresident individual or nonresident entity members.' "
                     "⚠ U4 / W11(a): Booklet 510 says '1b or 1d' instead — but 1d is 'Others' (resident and exempt "
                     "entities), which nothing taxes. THE FORM FACE IS INTERNALLY CONSISTENT AND THE BOOKLET IS NOT. "
                     "Build to the face; the erratum is recorded, not fixed."),
     "exceptions": "Investment partnerships (code 705) are not subject to the nonresident tax merely because trading is directed from Maryland — R13."},
    {"rule_id": "R-MD510-NRTAX", "title": "Lines 5-13 — the mandatory nonresident tax (6.50% + 2.25%, and 8.25%)",
     "rule_type": "calculation", "sort_order": 7,
     "formula": ("L5 = pct by individual nonresidents (BLANK = 100%) ; L6 = L4 x L5 ; "
                 "L7 = L6 x 6.50%  [§10-105(a) top marginal] ; L8 = L6 x 2.25%  [§10-106.1 lowest county] ; L9 = L7 + L8 ; "
                 "L10 = pct by nonresident entities (BLANK = 100%) ; L11 = L4 x L10 ; L12 = L11 x 8.25%  [§10-105(b)] ; "
                 "L13 = L9 + L12"),
     "inputs": ["4", "pct_nonresident_individuals_l5", "pct_nonresident_entities_l10"],
     "outputs": ["5", "6", "7", "8", "9", "10", "11", "12", "13"],
     "description": ("⚠ THE 510 APPLIES TWO MULTIPLIERS TO THE SAME BASE AND ADDS (L7 + L8); the 511 applies ONE "
                     "8.75% multiplier. Mathematically identical, but they round at different points and both forms "
                     "print whole-dollar boxes. Follow each form's own line structure — do NOT collapse L7+L8 into a "
                     "single 8.75% line."),
     "notes": "Rates are DERIVED, year-keyed constants with both statutory inputs cited — never a hardcoded 0.0875/0.0650."},
    {"rule_id": "R-MD510-DCF9A", "title": "Worksheet 9A — distributable cash flow SCALED by nonresident ownership %",
     "rule_type": "calculation", "sort_order": 8,
     "formula": ("F = B + C + D + E ; I = F - (G + H) ; J = L5 + L10 (nonresident ownership %) ; "
                 "K = I x J   [THE OWNERSHIP STEP — 9A ONLY] ; M = max(0, K - L) -> Form 510 line 14"),
     "inputs": ["dcf_b_cash_method_restatement", "dcf_c_non_includable_receipts", "dcf_d_depreciation_addback",
                "dcf_e_liability_reserve_decrease", "dcf_g_non_deductible_expenditures",
                "dcf_h_liability_reserve_increase", "dcf_l_nonresident_tax_prev_paid"],
     "outputs": ["W9A-F", "W9A-I", "W9A-J", "W9A-K", "W9A-M", "14"],
     "description": ("W5. Worksheet 9A runs A-M and MULTIPLIES distributable cash flow by the nonresident ownership "
                     "percentage; worksheet 11A runs A-K with NO ownership step. Cloning one into the other "
                     "over-caps or under-caps every DCF return. Statutory cap: §10-102.1(d)(3)."),
     "notes": ("⚠ W5(a): line F is encoded verbatim as 'Add lines B through E', which omits line A. Gated by "
               "MD_DCF_F_INCLUDES_LINE_A = False — confirm against the printed worksheet at the walk. "
               "⚠ W5(b)/U7: the 'cannot be elected on an amended return' claim is UNSUPPORTED and is NOT encoded.")},
    {"rule_id": "R-MD510-L15", "title": "Line 15 — CONDITIONAL lesser-of, gated on the worksheet checkbox",
     "rule_type": "conditional", "sort_order": 9,
     "formula": "L15 = L13 if not dcf_worksheet_used else min(L13, L14)",
     "inputs": ["13", "14", "dcf_worksheet_used"], "outputs": ["15"],
     "description": ("⚠ Booklet 510, verbatim: 'If the distributable cash flow limitation is not used, enter the "
                     "amount shown on Line 13. If the distributable cash flow method is used, enter the lesser of "
                     "Line 13 or Line 14.' AN UNCONDITIONAL MIN() ZEROES THE TAX whenever line 14 is blank. "
                     "'Election of the distributable cash flow limitation will not reduce the tax liability of the members.'")},
    {"rule_id": "R-MD510-PAY", "title": "Lines 16a-16h — payments and credits (SEVEN lines, incl. the 16d/16e split)",
     "rule_type": "calculation", "sort_order": 10,
     "formula": "L16h = 16a + 16b + 16c + 16d + 16e + 16f + 16g",
     "inputs": ["pay_16a_estimated", "pay_16b_extension", "pay_16c_credit_from_other_pte", "pay_16d_credit_nonres_shares",
                "pay_16e_credit_res_shares", "pay_16f_mw506nrs", "pay_16g_amended_prior_payments"],
     "outputs": ["16h"],
     "description": ("⚠ The 510 has SEVEN payment lines to the 511's five, and splits the upstream entity-level "
                     "credit into 16d (this entity's NONRESIDENT shares) and 16e (its RESIDENT shares). "
                     "U3: the K-1 Section D4 instruction misdirects a 510 filer to 'Form 511, Line 13C' — build to "
                     "16d/16e. Also available here: a Box-B filer's refund of resident-leg estimates paid on the "
                     "510/511D worksheet lines 6-10.")},
    {"rule_id": "R-MD510-SETTLE", "title": "Lines 17-22 — balance due, overpayment, refund",
     "rule_type": "calculation", "sort_order": 11,
     "formula": ("L17 = max(0, L15 - L16h) ; L18 = max(0, L16h - L15) ; "
                 "L20 = L15 + L18a + L19 - L16h ; "
                 "L21 <= (L18 - L18a - L19) ; L22 = L18 - (L19 + L21)  [if amending: L18 - L18a - L19]"),
     "inputs": ["15", "16h", "prior_overpayment_18a", "interest_penalty_500up_19", "overpayment_applied_next_year"],
     "outputs": ["17", "18", "18a", "19", "20", "21", "22"],
     "description": "U5/W11(b): the amended-return payment line is 16g, not the booklet's 16b. Faces govern.",
     "notes": "Overpayments are refunded to the PTE, not distributed to members (Comptroller v. FC-GEN; K-1 D3 RESERVED)."},
    {"rule_id": "R-MD510-SCHB", "title": "Schedule B Parts I-IV — per-member roster, shares off LINE 2",
     "rule_type": "calculation", "sort_order": 12,
     "formula": ("Part I individuals (SSN order) + Part II fiduciaries (FEIN order) + Part III PTE members "
                 "(INCLUDING S CORPORATIONS) + Part IV corporation members (EXCLUDING S CORPORATIONS) ; "
                 "per-member income share = a portion of LINE 2, page 1 (NOT line 4) ; "
                 "cross-foot Parts I+II to 1a+1b, Parts III+IV to 1c/1d"),
     "inputs": ["2", "count_1a_resident_individuals", "count_1b_nonresident_individuals",
                "count_1c_nonresident_entities", "count_1d_others"],
     "outputs": ["SchB"],
     "description": ("⚠ Schedule B reports the FEDERAL/ENTITY-LEVEL share while the tax lines run off the APPORTIONED "
                     "line 4. Do not wire Schedule B off line 4. Printed in the margin of every part: 'You must file "
                     "Form 510 electronically to pass on business tax credits from Form 500CR and/or Form 502S to "
                     "your members' — a conditional e-file mandate on the form face.")},
    {"rule_id": "R-MD510-K1D", "title": "Schedule K-1 Section D — the 510 leg is D1: CREDIT ONLY, NO ADD-BACK",
     "rule_type": "calculation", "sort_order": 13,
     "formula": ("K-1 D1 = member's share of Form 510 line 15 ; D5 = D1 + D2 + D4 ; "
                 "addback = D2 + D4 ONLY  ->  for a pure 510 filer the add-back is ZERO"),
     "inputs": ["15"], "outputs": ["K1-D1", "K1-D5"],
     "description": ("⚠ W4. D1 carries NO add-back sentence. Under §10-102.1(c)(1) the non-electing tax is already "
                     "treated as a tax imposed on the members and paid on their behalf — it is not an entity-level "
                     "deduction. A SPEC THAT ADDS BACK D1 DOUBLE-TAXES EVERY NONRESIDENT PARTNER. "
                     "D3 is RESERVED (Comptroller v. FC-GEN Operations Investments LLC)."),
     "notes": "Credit route: Form 505 line 45 for 510 credits; Form 500CR (corporations); Form 504 (fiduciaries); Form 510 lines 16c-16f (PTE members)."},
    {"rule_id": "R-MD510-K1H", "title": "Schedule K-1 Section H — capital-gain reporting, column 2 = column 1 x the factor",
     "rule_type": "calculation", "sort_order": 14,
     "formula": ("H column 2 (Maryland net capital gain, NONRESIDENT MEMBERS ONLY) = column 1 x Schedule A line 4 ; "
                 "row 3 (tax-advantaged retirement plan assets) is RESIDENT MEMBERS ONLY — column 2 blocked out ; "
                 "the PTE computes NO capital-gain surtax at entity level"),
     "inputs": ["k1_section_h_col1_rows", "SchA-4"], "outputs": ["K1-H"],
     "description": ("W7. New for TY2025, mandatory on both forms, feeding members' Forms 502CG/504CG — a reporting "
                     "obligation with NO tax line on either return face, which is exactly what gets dropped. A "
                     "SECOND consumer of the apportionment factor. ⚠ The instruction misprints IRC §408/§408A as "
                     "'§458/§458A'; encode against the statute and TB 58, and do not 'fix' the erratum back.")},
    {"rule_id": "R-MD510-RATES", "title": "The nonresident-tax rates are a YEAR-KEYED DERIVATION, not literals",
     "rule_type": "validation", "sort_order": 15,
     "formula": ("individual leg = §10-105(a) top marginal (0.0650) applied at L7 + §10-106.1 lowest county (0.0225) "
                 "applied at L8 ; entity leg = §10-105(b) (0.0825) at L12 ; "
                 "STALENESS: the inputs are verified for TY2025 only — any other tax year invalidates them"),
     "inputs": [], "outputs": ["rate_individual_state", "rate_special_nonresident", "rate_entity"],
     "description": ("§10-102.1(d)(1) uses the same construction as (d)(2). Any change to §10-105(a)'s top bracket or "
                     "to the lowest county rate moves the tax automatically with no PTE legislation — it moved for "
                     "TY2025 exactly this way (the BRFA of 2025's new 6.50% bracket). Encode as a derivation with "
                     "both inputs cited and a staleness assertion.")},
]

MD510_RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R-MD510-ELECT", "MD_2025_FORM_510_511E", "primary", "both deeming defaults + irrevocability, verbatim"),
    ("R-MD510-ELECT", "MD_2025_FORM_510", "primary", "page-1 STOP instruction"),
    ("R-MD510-ELECT", "MD_2025_PTE_BOOKLET_510", "primary", "Instruction 1 mirror + Instruction 8 amended bar"),
    ("R-MD510-ELECT", "MD_TG_10_102_1", "secondary", "(b)(2) creates the two legs but no election mechanism"),
    ("R-MD510-ELECT", "MD_COMP_ALERT_PTE_TY2026", "secondary", "TY2026 suspension of 'first filing wins' — why the machine is year-keyed"),
    ("R-MD510-MEMBER", "MD_2025_FORM_510", "primary", "lines 1a-1e verbatim; 1c is nonresident entities only"),
    ("R-MD510-MEMBER", "MD_2025_PTE_BOOKLET_510", "primary", "'Include in Others, resident entities and 408(e)/501 entities'"),
    ("R-MD510-MEMBER", "MD_TB_6_PTE", "secondary", "§II.A exempt-member definition (U6 footing)"),
    ("R-MD510-L2", "MD_2025_PTE_BOOKLET_510", "primary", "line 2 = net 1065 Sch. K 1-11 / 1120S Sch. K 1-10 less federal-obligation interest"),
    ("R-MD510-ALLOC", "MD_2025_FORM_510", "primary", "ALLOCATION OF INCOME header gate, verbatim"),
    ("R-MD510-ALLOC", "MD_2025_PTE_BOOKLET_510", "secondary", "separate accounting vs apportionment, by entity type"),
    ("R-MD510-APPORT", "MD_2025_FORM_510", "primary", "'(If factor is zero, enter .000001)' — FORM FACE ONLY"),
    ("R-MD510-APPORT", "MD_TG_10_402_401", "primary", "§10-402(e): only the Comptroller may alter a formula; no insignificance rule"),
    ("R-MD510-APPORT", "MD_COMAR_03_04_03_08", "secondary", "B(5) a factor is computed even on a loss return"),
    ("R-MD510-GATE", "MD_2025_FORM_510", "primary", "face: 'if there is an entry on line 1b or line 1c'"),
    ("R-MD510-GATE", "MD_2025_PTE_BOOKLET_510", "secondary", "U4 erratum: the booklet says 1b or 1d"),
    ("R-MD510-NRTAX", "MD_2025_FORM_510", "primary", "L7 6.50%, L8 2.25%, L12 8.25% on the form face"),
    ("R-MD510-NRTAX", "MD_2025_PTE_BOOKLET_510", "secondary", "Taxability narrative + nonresident-entity definition"),
    ("R-MD510-DCF9A", "MD_2025_FORM_510", "primary", "worksheet 9A lines A-M incl. the J/K ownership step"),
    ("R-MD510-DCF9A", "MD_TG_10_102_1", "secondary", "(d)(3) statutory distributable-cash-flow cap"),
    ("R-MD510-L15", "MD_2025_PTE_BOOKLET_510", "primary", "line 15 conditional lesser-of, verbatim"),
    ("R-MD510-PAY", "MD_2025_FORM_510", "primary", "16a-16g verbatim incl. the 16d/16e nonresident-vs-resident split"),
    ("R-MD510-SETTLE", "MD_2025_FORM_510", "primary", "lines 17-22 arithmetic off the form face"),
    ("R-MD510-SCHB", "MD_2025_PTE_BOOKLET_510", "primary", "'a portion of the amount on line 2, page 1'"),
    ("R-MD510-K1D", "MD_2025_SCH_K1_510_511", "primary", "Section D — D1 carries no add-back sentence"),
    ("R-MD510-K1D", "MD_TG_10_102_1", "primary", "(c)(1) the non-electing tax is the members' own tax"),
    ("R-MD510-K1D", "MD_TG_10_701_1", "secondary", "the member credit"),
    ("R-MD510-K1H", "MD_2025_SCH_K1_510_511", "primary", "Section H columns and the apportionment-factor rule"),
    ("R-MD510-RATES", "MD_TG_10_105_106_1", "primary", "the two rate inputs, verbatim"),
    ("R-MD510-RATES", "MD_TG_10_102_1", "primary", "(d)(1)/(d)(2) the derivation construction"),
]

MD510_LINES: list[dict] = [
    {"line_number": "1a", "description": "Individual (including fiduciary) residents of Maryland", "line_type": "input",
     "source_facts": ["count_1a_resident_individuals"], "sort_order": 1, "notes": "Counted, NOT taxed on Form 510."},
    {"line_number": "1b", "description": "Individual (including fiduciary) nonresidents", "line_type": "input",
     "source_facts": ["count_1b_nonresident_individuals"], "sort_order": 2},
    {"line_number": "1c", "description": "Nonresident entities", "line_type": "input",
     "source_facts": ["count_1c_nonresident_entities"], "sort_order": 3,
     "notes": "⚠ Form 511's 1c reads 'Nonresident AND RESIDENT entities'. Different scope, different tax."},
    {"line_number": "1d", "description": "Others (resident entities + IRC §408(e)/§501 exempt entities) — UNTAXED", "line_type": "input",
     "source_facts": ["count_1d_others"], "sort_order": 4,
     "notes": "⚠ W6: the resident entity member lives here on the 510 and moves to line 1c on the 511."},
    {"line_number": "1e", "description": "Total", "line_type": "subtotal", "source_rules": ["R-MD510-MEMBER"], "sort_order": 5},
    {"line_number": "2", "description": ("Total distributive or pro rata share of income per federal return (Form 1065 or 1120S) — "
                                         "Unistate entities or multistate entities with no nonresident members also enter this amount on line 4."),
     "line_type": "calculated", "calculation": "R-MD510-L2", "source_rules": ["R-MD510-L2"], "sort_order": 6},
    {"line_number": "3a", "description": "Non-Maryland income (for entities using separate accounting). Subtract this amount from line 2 and enter the difference on line 4.",
     "line_type": "input", "source_facts": ["non_maryland_income_sep_acct"], "sort_order": 7},
    {"line_number": "3b", "description": ("Maryland apportionment factor from computation worksheet on Page 4 (for entities using the "
                                          "apportionment method). Multiply line 2 by this factor and enter the result on line 4. "
                                          "(If factor is zero, enter .000001)"),
     "line_type": "calculated", "calculation": "R-MD510-APPORT", "source_rules": ["R-MD510-APPORT"], "sort_order": 8},
    {"line_number": "4", "description": "Distributive or pro rata share of income allocable to Maryland", "line_type": "subtotal",
     "source_rules": ["R-MD510-ALLOC"], "sort_order": 9},
    {"line_number": "5", "description": ("Percentage of ownership by individual nonresident members shown on line 1b (or profit/loss "
                                         "percentage, if applicable). If 100%, leave blank and enter the amount from line 4 on line 6."),
     "line_type": "input", "source_facts": ["pct_nonresident_individuals_l5"], "sort_order": 10},
    {"line_number": "6", "description": "Distributive or pro rata share of income for nonresident individual members (Multiply line 4 by the percentage on line 5.)",
     "line_type": "calculated", "source_rules": ["R-MD510-NRTAX"], "sort_order": 11},
    {"line_number": "7", "description": "Nonresident individual tax (Multiply line 6 by 6.50%.)", "line_type": "calculated",
     "source_rules": ["R-MD510-NRTAX"], "sort_order": 12, "notes": "§10-105(a) top marginal individual rate — DERIVED constant."},
    {"line_number": "8", "description": "Special nonresident tax (Multiply line 6 by 2.25%.)", "line_type": "calculated",
     "source_rules": ["R-MD510-NRTAX"], "sort_order": 13, "notes": "§10-106.1 — the lowest county income tax rate set by any Maryland county."},
    {"line_number": "9", "description": "Total Maryland tax on individual members (Add lines 7 and 8.)", "line_type": "subtotal",
     "source_rules": ["R-MD510-NRTAX"], "sort_order": 14},
    {"line_number": "10", "description": "Percentage of ownership by nonresident entities shown on line 1c (or profit/loss percentage, if applicable). If 100%, leave blank.",
     "line_type": "input", "source_facts": ["pct_nonresident_entities_l10"], "sort_order": 15},
    {"line_number": "11", "description": "Distributive or pro rata share of income for nonresident entity members (Multiply line 4 by percentage on line 10.)",
     "line_type": "calculated", "source_rules": ["R-MD510-NRTAX"], "sort_order": 16},
    {"line_number": "12", "description": "Nonresident entity tax (Multiply line 11 by 8.25%.)", "line_type": "calculated",
     "source_rules": ["R-MD510-NRTAX"], "sort_order": 17},
    {"line_number": "13", "description": "Total nonresident tax (Add lines 9 and 12.)", "line_type": "subtotal",
     "source_rules": ["R-MD510-NRTAX"], "sort_order": 18},
    {"line_number": "14", "description": "Distributable cash flow limitation from worksheet. See instructions. If worksheet used, check here",
     "line_type": "calculated", "calculation": "R-MD510-DCF9A", "source_rules": ["R-MD510-DCF9A"], "sort_order": 19},
    {"line_number": "15", "description": "Nonresident tax due (Enter the lesser of line 13 or line 14.) — CONDITIONAL on the worksheet checkbox",
     "line_type": "calculated", "calculation": "R-MD510-L15", "source_rules": ["R-MD510-L15"], "sort_order": 20,
     "notes": "⚠ If the DCF limitation is not used, enter line 13. An unconditional MIN() zeroes the tax."},
    {"line_number": "16a", "description": "Estimated PTE nonresident tax paid with Form 510/511D (and prior year overpayment)",
     "line_type": "input", "source_facts": ["pay_16a_estimated"], "sort_order": 21},
    {"line_number": "16b", "description": "PTE nonresident tax paid with an extension request (Form 510/511E)",
     "line_type": "input", "source_facts": ["pay_16b_extension"], "sort_order": 22},
    {"line_number": "16c", "description": "Credit for nonresident tax paid on behalf of the PTE by another PTE (Attach Schedule K-1 (510/511))",
     "line_type": "input", "source_facts": ["pay_16c_credit_from_other_pte"], "sort_order": 23},
    {"line_number": "16d", "description": "Credit for entity-level tax paid by another PTE with regard to this entity's NONRESIDENT shares",
     "line_type": "input", "source_facts": ["pay_16d_credit_nonres_shares"], "sort_order": 24,
     "notes": "U3: the K-1 D4 instruction's 'Form 511, Line 13C' pointer is an erratum — build here."},
    {"line_number": "16e", "description": "Credit for entity-level tax paid by another PTE with regard to this entity's RESIDENT shares",
     "line_type": "input", "source_facts": ["pay_16e_credit_res_shares"], "sort_order": 25,
     "notes": "⚠ This resident/nonresident credit split has NO counterpart on Form 511 (one line, 13c)."},
    {"line_number": "16f", "description": "Payment made with Form MW506NRS (nonresident real-property withholding)",
     "line_type": "input", "source_facts": ["pay_16f_mw506nrs"], "sort_order": 26},
    {"line_number": "16g", "description": "If amending, total payments made with original plus additional tax paid after original was filed.",
     "line_type": "input", "source_facts": ["pay_16g_amended_prior_payments"], "sort_order": 27,
     "notes": "U5: the booklet wrongly points at 16b. The face governs."},
    {"line_number": "16h", "description": "Total payments and credits (Add lines 16a through 16g.)", "line_type": "subtotal",
     "source_rules": ["R-MD510-PAY"], "sort_order": 28},
    {"line_number": "17", "description": "Balance of tax due (If line 15 exceeds line 16h, enter the difference.)",
     "line_type": "calculated", "source_rules": ["R-MD510-SETTLE"], "sort_order": 29},
    {"line_number": "18", "description": "Overpayment (If line 16h exceeds line 15, enter the difference.)",
     "line_type": "calculated", "source_rules": ["R-MD510-SETTLE"], "sort_order": 30},
    {"line_number": "18a", "description": "If amending, prior overpayment. (Total all refunds previously issued.)",
     "line_type": "input", "source_facts": ["prior_overpayment_18a"], "sort_order": 31},
    {"line_number": "19", "description": "Interest and/or penalty from Form 500UP or late payment interest — TOTAL",
     "line_type": "input", "source_facts": ["interest_penalty_500up_19"], "sort_order": 32, "notes": "R7 RED-defer."},
    {"line_number": "20", "description": "Total nonresident balance due (Add lines 15, 18a, and 19. Subtract line 16h.) Pay in full with this return.",
     "line_type": "total", "source_rules": ["R-MD510-SETTLE"], "sort_order": 33},
    {"line_number": "21", "description": "Amount of overpayment to be applied to estimated tax for next year (not to exceed the net of lines 18 minus 18a and 19).",
     "line_type": "calculated", "source_facts": ["overpayment_applied_next_year"], "source_rules": ["R-MD510-SETTLE"], "sort_order": 34},
    {"line_number": "22", "description": "Amount of overpayment TO BE REFUNDED. (Add lines 19 and 21, and subtract the total from line 18.)",
     "line_type": "total", "source_rules": ["R-MD510-SETTLE"], "sort_order": 35},
    {"line_number": "23a", "description": "Direct deposit — type of account / routing number (9 digits) / account number / name on the account",
     "line_type": "input", "sort_order": 36},
    # --- Worksheet 9A ---
    {"line_number": "W9A-A", "description": "Worksheet 9A A — Total distributive or pro rata share of income (Form 510, line 2)",
     "line_type": "informational", "source_rules": ["R-MD510-DCF9A"], "sort_order": 700},
    {"line_number": "W9A-B", "description": "Worksheet 9A B — cash-method restatement", "line_type": "input",
     "source_facts": ["dcf_b_cash_method_restatement"], "sort_order": 701},
    {"line_number": "W9A-C", "description": "Worksheet 9A C — non-includable cash receipts (capital contributions, loan proceeds)",
     "line_type": "input", "source_facts": ["dcf_c_non_includable_receipts"], "sort_order": 702},
    {"line_number": "W9A-D", "description": "Worksheet 9A D — depreciation/amortization/depletion add-back", "line_type": "input",
     "source_facts": ["dcf_d_depreciation_addback"], "sort_order": 703},
    {"line_number": "W9A-E", "description": "Worksheet 9A E — decrease in liability reserve", "line_type": "input",
     "source_facts": ["dcf_e_liability_reserve_decrease"], "sort_order": 704},
    {"line_number": "W9A-F", "description": "Worksheet 9A F — Total. (Add lines B through E.)", "line_type": "subtotal",
     "source_rules": ["R-MD510-DCF9A"], "sort_order": 705,
     "notes": "⚠ W5(a): transcribed verbatim as B through E — line A is not in the total. Confirm at the walk."},
    {"line_number": "W9A-G", "description": "Worksheet 9A G — non-deductible cash expenditures (excluding member distributions)",
     "line_type": "input", "source_facts": ["dcf_g_non_deductible_expenditures"], "sort_order": 706},
    {"line_number": "W9A-H", "description": "Worksheet 9A H — increase in liability reserve", "line_type": "input",
     "source_facts": ["dcf_h_liability_reserve_increase"], "sort_order": 707},
    {"line_number": "W9A-I", "description": "Worksheet 9A I — Total distributable cash flow. (Add lines G and H, and subtract the total from line F.)",
     "line_type": "subtotal", "source_rules": ["R-MD510-DCF9A"], "sort_order": 708},
    {"line_number": "W9A-J", "description": ("Worksheet 9A J — Total percentage of ownership (or profit/loss sharing if applicable) by "
                                             "nonresident. (Enter the sum of the percentages from Form 510, lines 5 and 10.)"),
     "line_type": "calculated", "source_rules": ["R-MD510-DCF9A"], "sort_order": 709,
     "notes": "⚠ THE OWNERSHIP STEP — worksheet 11A has no equivalent."},
    {"line_number": "W9A-K", "description": "Worksheet 9A K — Distributable cash flow. (Multiply line I by line J.)",
     "line_type": "calculated", "source_rules": ["R-MD510-DCF9A"], "sort_order": 710},
    {"line_number": "W9A-L", "description": "Worksheet 9A L — nonresident tax previously paid with 510/511D or 510/511E",
     "line_type": "input", "source_facts": ["dcf_l_nonresident_tax_prev_paid"], "sort_order": 711},
    {"line_number": "W9A-M", "description": "Worksheet 9A M — Distributable cash flow limitation. (Subtract line L from line K. If less than 0, enter 0.)",
     "line_type": "total", "source_rules": ["R-MD510-DCF9A"], "sort_order": 712},
] + _schedule_a_lines(600, "R-MD510-APPORT") + PAGE3_LINES + [
    {"line_number": "SchB", "description": ("Schedule B Parts I-IV — Individual / Fiduciary / Pass-Through Entity (INCLUDING S "
                                            "CORPORATIONS) / Corporation (EXCLUDING S CORPORATIONS) members. Per-member income share "
                                            "is a portion of LINE 2, page 1 — NOT line 4."),
     "line_type": "informational", "source_rules": ["R-MD510-SCHB"], "sort_order": 950},
    {"line_number": "K1-D1", "description": "Schedule K-1 Section D line 1 — Nonresident tax paid on member's behalf by this PTE (Form 510). CREDIT ONLY; NEVER added back.",
     "line_type": "calculated", "source_rules": ["R-MD510-K1D"], "sort_order": 960},
    {"line_number": "K1-H", "description": "Schedule K-1 Section H — capital-gain reporting; column 2 = column 1 x the Maryland apportionment factor",
     "line_type": "calculated", "source_rules": ["R-MD510-K1H"], "sort_order": 961},
]

MD510_DIAGNOSTICS: list[dict] = [
    # ---- The election state machine (W1) ----
    {"diagnostic_id": "D_MD510_ELECTION_UNDETERMINED", "severity": "error",
     "title": "The 510-vs-511 election cannot be determined — it is NOT on this return",
     "condition": "election_first_filing_kind = 'unknown', or election_recorded_form = 'undetermined'",
     "message": ("Maryland's Form 510 and Form 511 are MUTUALLY EXCLUSIVE and the choice was made on the FIRST filing "
                 "of the tax year (Form 510/511D or Form 510/511E), months before this return. Nothing on the "
                 "year-end return's own data reveals which applies. Retrieve the first filing and record which box "
                 "was checked: Box A (pay tax on ALL members' shares) requires Form 511; Box B (pay only on behalf of "
                 "nonresident members) requires Form 510. If no 510/511D or 510/511E was filed, the year-end return "
                 "you file IS the irrevocable election. Do not proceed on an assumption — filing the wrong return is "
                 "an IRREVOCABLE error that an amended return cannot cure."),
     "notes": "W1. The spec never infers the election from computed values."},
    {"diagnostic_id": "D_MD510_WRONG_FORM_FILE_511", "severity": "error",
     "title": "STOP — the recorded election requires Form 511, not Form 510",
     "condition": "election_recorded_form = MD_511 while Form 510 is being prepared",
     "message": ("Form 510 page 1, verbatim: 'If the PTE made an irrevocable election on Form 510/511D or 510/511E to "
                 "remit tax with respect to all members' shares, STOP. You must file Form 511.' The election is "
                 "irrevocable for the tax year and may not be changed on an amended return."),
     "notes": "W1 hard block."},
    {"diagnostic_id": "D_MD510_DEEMED_NEITHER_BOX", "severity": "warning",
     "title": "DEEMED non-election — neither box was checked on the first filing",
     "condition": "first filing was a 510/511D or 510/511E with neither Box A nor Box B checked",
     "message": ("Form 510/511E instructions, verbatim: 'If this is your first filing and neither box is checked, the "
                 "Comptroller will deem you to have chosen to pay tax only on behalf of nonresident members, and that "
                 "decision will be irrevocable.' Form 510 is therefore the required year-end return. Confirm with the "
                 "client that entity-level election was not intended — it cannot be recovered this tax year."),
     "notes": "W1 deeming default #1."},
    {"diagnostic_id": "D_MD510_DEEMED_BOTH_BOXES", "severity": "error",
     "title": "DEEMED election — both boxes were checked, so Form 511 is required",
     "condition": "first filing had BOTH Box A and Box B checked",
     "message": ("Form 510/511E instructions, verbatim: 'If this is your first filing and both boxes are checked in "
                 "error, the Comptroller will deem you have elected to pay tax at the entity level with respect to "
                 "all members' shares, and that decision will be irrevocable.' Prepare Form 511, not Form 510. "
                 "(The 510/511D states the same default without the 'first filing' qualifier — a drafting "
                 "difference, not a substantive one.)"),
     "notes": "W1 deeming default #2."},
    {"diagnostic_id": "D_MD510_AMENDED_ELECTION_BAR", "severity": "error",
     "title": "An amended return may not change the election or non-election",
     "condition": "is_amended_return and the amended return would change the recorded election",
     "message": ("Booklet 510 Instruction 8: 'A PTE may not file an amended return to change the PTE's election or "
                 "non-election for the tax year.' Corroborated by Technical Bulletin 6: 'A nonelection may not be "
                 "changed to an election on an amended return.' Amend the figures, not the election."),
     "notes": "W1."},
    # ---- Member classification (W6) ----
    {"diagnostic_id": "D_MD510_RESIDENT_ENTITY_1D", "severity": "info",
     "title": "A RESIDENT entity member goes to line 1d 'Others' and is NOT taxed on Form 510",
     "condition": "a member is an entity formed under, or registered with SDAT to do business in, Maryland",
     "message": ("Booklet 510 line 1: 'Include in \"Others\", resident entities and entities that are tax-exempt under "
                 "IRC Sections 408(e) or 501.' Line 1d is not multiplied by anything. ⚠ THE SAME MEMBER ON FORM 511 "
                 "lands on line 1c ('Nonresident and resident entities') and is taxed at 8.25%. Same member, same "
                 "PTE, different box, different tax — do not carry a 510 classification onto a 511."),
     "notes": "W6."},
    {"diagnostic_id": "D_MD510_FIDUCIARY_IN_IND_LEG", "severity": "info",
     "title": "Fiduciary members belong in the INDIVIDUAL legs (1a/1b), never the entity legs",
     "condition": "the PTE has fiduciary (trust/estate) members",
     "message": ("Lines 1a and 1b read 'Individual (including fiduciary)', and both booklets state 'In these "
                 "instructions, the term individual includes fiduciaries, unless specifically excepted.' A "
                 "nonresident fiduciary is taxed at 6.50% + 2.25% on the 510, not at the 8.25% entity rate. Note also "
                 "that fiduciary members may NOT be included in a Form 510C composite return."),
     "notes": "W6."},
    {"diagnostic_id": "D_MD510_EXEMPT_MEMBER_U6", "severity": "warning",
     "title": "REIT / IRC §408(e) / §501 member excluded — re-verify TG §10-104 before relying on this",
     "condition": "a member is a REIT (§856), an IRA/Keogh/pension plan (§408(e)) or a §501 organization",
     "message": ("Technical Bulletin 6 §II.A excludes these from the definition of 'member' generally, plus 'any other "
                 "tax-exempt entity listed in TG § 10-104'. ⚠ OPEN ITEM U6: §10-102.1(f) by its own words is scoped "
                 "to the NON-ELECTING leg only, TB 6 is TY2023-keyed, and TG §10-104 has not been read. The exclusion "
                 "is applied here on TB 6's footing; re-verify §10-104 before seeding."),
     "notes": "U6 residual."},
    # ---- Apportionment (W9 / U11) ----
    {"diagnostic_id": "D_MD510_APPORT_ZERO_FLOOR", "severity": "info",
     "title": "A zero apportionment factor is entered as .000001 — never dropped",
     "condition": "the computed Schedule A factor rounds to zero, or the receipts denominator is zero",
     "message": ("Form 510 line 3b and Schedule A line 4, verbatim: '(If factor is zero, enter .000001)'. COMAR "
                 "03.04.03.08 B(5) additionally requires an apportionment factor to be calculated even on a loss "
                 "return 'for the filing to be considered complete'. Note this convention appears ONLY on the form "
                 "faces — it is in neither PTE booklet nor the Corporate Booklet."),
     "notes": "W9."},
    {"diagnostic_id": "D_MD510_NO_FACTOR_REWEIGHT", "severity": "error",
     "title": "Maryland has NO insignificant-denominator rule — never reweight or drop a factor",
     "condition": "any attempt to eliminate, reweight or substitute an apportionment factor",
     "message": ("Maryland has NO rule dropping or reweighting a factor whose denominator is zero or 'insignificant'. "
                 "That rule is Fla. Stat. §220.15(1) and it does NOT apply here — verified absent across Tax-General "
                 "§§10-401/10-402, COMAR 03.04.03.08/.09/.10, Administrative Release 43, the Corporate Booklet and "
                 "both PTE Booklets. Maryland's convention is the opposite: a zero factor is floored at .000001. "
                 "Altering a formula — including 'the weight of any factor' — is reserved to THE COMPTROLLER "
                 "(§10-402(e); §10-401(2)). Neither the preparer nor this software may do it."),
     "notes": "W9 / U11. The load-bearing negative."},
    # ---- DCF (W5) ----
    {"diagnostic_id": "D_MD510_DCF_CONDITIONAL", "severity": "warning",
     "title": "Line 15 is a CONDITIONAL lesser-of — not an unconditional MIN()",
     "condition": "line 14 is blank or the distributable-cash-flow worksheet checkbox is unchecked",
     "message": ("Booklet 510, verbatim: 'If the distributable cash flow limitation is not used, enter the amount "
                 "shown on Line 13. If the distributable cash flow method is used, enter the lesser of Line 13 or "
                 "Line 14.' Line 15 therefore equals line 13 unless the worksheet is used. Also: 'Election of the "
                 "distributable cash flow limitation will not reduce the tax liability of the members.'"),
     "notes": "W5."},
    {"diagnostic_id": "D_MD510_DCF_OWNERSHIP_STEP", "severity": "info",
     "title": "Worksheet 9A scales distributable cash flow by the NONRESIDENT ownership percentage",
     "condition": "the distributable-cash-flow worksheet is used on Form 510",
     "message": ("Worksheet 9A line J = the sum of the percentages from Form 510 lines 5 and 10; line K = line I x "
                 "line J. ⚠ Form 511's worksheet 11A has NO ownership step — its line I is the whole distributable "
                 "cash flow. Do not clone one worksheet into the other; it over-caps or under-caps every DCF return."),
     "notes": "W5."},
    {"diagnostic_id": "D_MD510_DCF_AMENDED_U7", "severity": "info",
     "title": "No source bars electing the DCF limitation on an amended return (U7)",
     "condition": "the DCF limitation is elected on an amended return",
     "message": ("md_conformity.md §4 asserts the DCF cap 'cannot be elected on an amended return'. NO such statement "
                 "appears in the FINAL TY2025 Booklets 510 or 511, on either form face, in §10-102.1(d)(3), or in "
                 "Technical Bulletin 6 — whose only amended-return sentence is the ELECTION bar. The claim is "
                 "unsupported and is NOT encoded as a rule. Ken to rule before this is enforced."),
     "notes": "U7 / W5(b)."},
    # ---- Errata (W11) ----
    {"diagnostic_id": "D_MD510_GATE_ERRATUM_U4", "severity": "info",
     "title": "Booklet erratum — the lines-5-19 gate is '1b or 1c' on the face, not '1b or 1d'",
     "condition": "reconciling the completion gate against Booklet 510",
     "message": ("Form face: 'Complete lines 5 through 19 if there is an entry on line 1b or line 1c.' Booklet 510: "
                 "'Do not complete lines 5 through 19: 1. Unless the PTE has members that are nonresidents of "
                 "Maryland (there is an entry on 1b or 1d)'. Line 1c is nonresident entities; line 1d is 'Others', "
                 "which the same booklet says holds RESIDENT and exempt entities. The face is internally consistent "
                 "and the booklet is not — build to the face. Recorded so nobody 'fixes' it back."),
     "notes": "U4 / W11(a)."},
    {"diagnostic_id": "D_MD510_AMEND_LINE_ERRATUM_U5", "severity": "info",
     "title": "Booklet erratum — amended payments go on line 16g, not line 16b",
     "condition": "is_amended_return",
     "message": ("Booklet 510 Instruction 8 says to 'include the amount paid on line 16b of Form 510'. Line 16b is the "
                 "EXTENSION payment line; the amended-return line is 16g. The form face and the per-line instructions "
                 "both say 16g. Build to the face."),
     "notes": "U5 / W11(b)."},
    {"diagnostic_id": "D_MD510_K1_D4_ERRATUM_U3", "severity": "info",
     "title": "K-1 erratum — a 510 filer's received entity-level credit goes on lines 16d/16e",
     "condition": "an upstream PTE's Schedule K-1 (510/511) Section D line 4 is present",
     "message": ("The K-1 Section D line 4 instruction says the amount is 'the member's distributive or pro rata share "
                 "from Form 511, Line 13C'. But Form 511 line 13c is credit received by a 511 FILER, and this entity "
                 "is filing a 510 — it reports the received credit on Form 510 lines 16d (nonresident shares) and 16e "
                 "(resident shares). Reads as an erratum; build to 16d/16e."),
     "notes": "U3 / W11(c)."},
    {"diagnostic_id": "D_MD510_TB38_ERRATUM_U10", "severity": "info",
     "title": "Form 500DM cites a nonexistent 'Technical Bulletin No. 38'",
     "condition": "following Form 500DM's cross-references",
     "message": ("Form 500DM cites 'Technical Bulletin No. 38' three times — on the form face, under Additional "
                 "Information, and at line 8. NO such document exists. The document is ADMINISTRATIVE RELEASE No. 38, "
                 "'Decoupling from Federal Income Tax Laws'. Recorded so nobody 'corrects' the spec back to TB 38."),
     "notes": "U10 / W11(d)."},
    # ---- Informational / structural ----
    {"diagnostic_id": "D_MD510_SCHB_OFF_LINE2", "severity": "warning",
     "title": "Schedule B per-member shares run off LINE 2, not line 4",
     "condition": "Schedule B Parts I-IV are populated",
     "message": ("Both booklets: the per-member share of income is 'a portion of the amount on line 2, page 1.' "
                 "Schedule B therefore reports the FEDERAL/ENTITY-LEVEL share while the tax lines run off the "
                 "APPORTIONED line 4. Do not wire Schedule B off line 4."),
     "notes": "Structural trap."},
    {"diagnostic_id": "D_MD510_EFILE_MANDATE", "severity": "warning",
     "title": "Conditional e-file mandate — credits from Form 500CR or 502S force electronic filing",
     "condition": "k1_section_e_credits_present or a Form 500CR / 502S credit is passed through",
     "message": ("Printed in the margin of every Schedule B page: 'You must file Form 510 electronically to pass on "
                 "business tax credits from Form 500CR and/or Form 502S to your members.' The mandate is conditional "
                 "on credits, not on size. Form 500CRW is the hardship waiver. ⚠ Maryland approval is PER FORM on the "
                 "BUSINESS MeF track and the software must prevent e-filing any form Maryland has not approved (U1)."),
     "notes": "U1."},
    {"diagnostic_id": "D_MD510_Q8_NOT_MFG_CARVEOUT", "severity": "info",
     "title": "Page-3 Q8 is the APPORTIONMENT manufacturing rule — NOT the depreciation carve-out",
     "condition": "page-3 question 8 is answered",
     "message": ("'Is this entity a multistate manufacturing corporation with more than 25 employees?' is COMAR "
                 "03.04.03.10 language — NAICS 1997 Edition, sectors 11/31/32/33, with extra exclusions for "
                 "affiliated corporations and service providers, and a >25-employee report that EXPIRED for tax years "
                 "beginning on or after 1/1/2011. The §10-210.1 depreciation carve-out is a DIFFERENT rule: NAICS "
                 "2012 Edition, Sectors 31/32/33, 'manufacturing entity', no employee test. NEVER wire question 8 to "
                 "the depreciation carve-out. Treated as informational direct-entry (U8)."),
     "notes": "U8 / W2."},
    {"diagnostic_id": "D_MD510_CODE_NUMBERS_U12", "severity": "info",
     "title": "Only three Form 510/511 code numbers exist in the TY2025 corpus",
     "condition": "a page-3 CODE NUMBER is entered",
     "message": ("The form prints two three-digit code blocks with no legend, and no published master list exists. "
                 "The only codes appearing anywhere in the TY2025 PTE sources are 704 (publicly traded pass-through "
                 "entity), 705 (investment partnership — Booklet 510 only) and 301 (Form 500UP annualization; S "
                 "corporations may NOT use the annualization method). Anything else is free entry, unverified."),
     "notes": "U12."},
    {"diagnostic_id": "D_MD510_RESIDENT_ESTIMATE_REFUND", "severity": "info",
     "title": "A Box-B filer recovers resident-leg estimated payments on this return",
     "condition": "resident-leg estimates were paid on the 510/511D worksheet (lines 6-10) but Box B was checked",
     "message": ("Form 510 page-1 face: 'You may also use this form to request a refund of estimated payment(s) for "
                 "tax paid on resident members' shares of income if the PTE has decided not to make the entity "
                 "election.' The 510/511D worksheet computes BOTH election branches (lines 1-5 nonresident, lines "
                 "6-10 resident), so a Box-B filer who completed lines 6-10 has an overpayment to recover through "
                 "line 16a into line 18. Note the overpayment is refunded to the PTE, not to the members."),
     "notes": "Verification finding §15.4 item 4."},
    {"diagnostic_id": "D_MD510_K1H_NO_TAX_LINE", "severity": "warning",
     "title": "Schedule K-1 Section H is mandatory for TY2025 and has NO tax line on this return",
     "condition": "the PTE has capital gain income allocable to any member",
     "message": ("New for TY2025: 'the PTE must provide additional information on capital gain income passed through "
                 "to members.' The PTE computes NO capital-gain surtax at entity level (TB 58) but MUST report all "
                 "seven Section H rows so members can complete Form 502CG or 504CG. Column 2 = column 1 x the "
                 "Maryland apportionment factor; row 3 is resident-members-only. Nothing on either return face "
                 "references Section H — a mandatory schedule with no tax line is exactly what gets dropped."),
     "notes": "W7."},
    {"diagnostic_id": "D_MD510_K1H_408_ERRATUM", "severity": "info",
     "title": "K-1 erratum — '§458 / §458A' should read IRC §408 / §408A",
     "condition": "reading the Schedule K-1 Section H line 3 instruction",
     "message": ("The K-1 Section H line-3 instruction cites 'an individual retirement account or individual "
                 "retirement annuity under IRC § 458, a Roth individual retirement account under IRC § 458A'. The "
                 "correct citations are IRC §408 and §408A, as Technical Bulletin 58 has them — the same misprint the "
                 "conformity brief found on Form 502CG line 3. Encode against the statute and TB 58; the erratum is "
                 "recorded so a future reader does not 'fix' it back."),
     "notes": "W7."},
    # ---- RED-DEFERS R1-R15 ----
    {"diagnostic_id": "D_MD510_R1_COMPOSITE_510C", "severity": "error",
     "title": "R1 — Form 510C composite return is not prepared by this product",
     "condition": "box_510c_filed, or more than one nonresident individual member elects into a composite",
     "message": ("Maryland Form 510C is not prepared in v1. Complete Form 510 first, then prepare Form 510C manually. "
                 "Gates: an Electing PTE (Form 511) may NOT file Form 510C; a single-member PTE may not file one; a "
                 "composite may not be filed if only one member elects in; nonresident FIDUCIARY, ENTITY and RESIDENT "
                 "members may not participate; for TY2025 a nonresident individual who received Maryland-taxable "
                 "distributed net capital gain may not participate; a member must be subject to Maryland tax SOLELY "
                 "from this PTE. Only the depreciation and 2-year-NOL decoupling modifications may flow through "
                 "(line 7). ⚠ The 510C prints ONE aggregate 8.75% multiplication at line 11 — not a per-member loop."),
     "notes": "R1 / W8. Re-pull TB 6 (TY2023-keyed) before the composite is ever built."},
    {"diagnostic_id": "D_MD510_R2_SPECIAL_APPORT", "severity": "error",
     "title": "R2 — Special Apportionment Formula is not computed",
     "condition": "the entity is a rental/leasing company, financial institution, transportation company or worldwide headquartered company",
     "message": ("Rental/leasing companies, financial institutions, transportation companies and worldwide "
                 "headquartered companies must use a Special Apportionment Formula (rental/leasing: equally weighted "
                 "receipts and property with intangible receipts excluded; financial institutions: COMAR 03.04.08.03; "
                 "trucking: miles in State / miles everywhere; railroad: track miles; shipping: days in ports and "
                 "waterways; airline: equally weighted property, payroll and sales; worldwide HQ: AR 43). This "
                 "product does not compute one. Enter the factor on Schedule A line 4 and check the disclosure box."),
     "notes": "R2."},
    {"diagnostic_id": "D_MD510_R3_ALTERNATIVE_APPORT", "severity": "error",
     "title": "R3 — an Alternative Apportionment Formula requires the Comptroller's prior acceptance",
     "condition": "scha_special_or_alternative_checked with an entity-supplied factor",
     "message": ("An Alternative Apportionment Formula requires the Comptroller's prior acceptance (Tax-General "
                 "§10-402(e); §10-401(2) for nonresident allocation). This product does not compute one and will "
                 "never derive one. Enter the accepted factor on Schedule A line 4, check the disclosure box, and "
                 "retain the Comptroller's acceptance. The Schedule A checkbox is a DISCLOSURE of a formula already "
                 "accepted — not a self-election."),
     "notes": "R3 / W9."},
    {"diagnostic_id": "D_MD510_R4_500CR_502S", "severity": "error",
     "title": "R4 — Form 500CR business credits and Form 502S are not computed",
     "condition": "k1_section_e_credits_present",
     "message": ("Schedule K-1 Section E carries 26 NAMED credits across lines 1-28 (lines 13 and 23 print RESERVED). "
                 "Form 500CR business credits and the Form 502S Maryland Historic Revitalization Tax Credit are not "
                 "computed in v1 — prepare them manually. ⚠ Passing any of these credits to members REQUIRES "
                 "electronic filing of the return (Form 500CRW is the hardship waiver)."),
     "notes": "R4."},
    {"diagnostic_id": "D_MD510_R5_ONE_MARYLAND", "severity": "error",
     "title": "R5 — the One Maryland Economic Development Tax Credit is not computed",
     "condition": "k1_one_maryland_used",
     "message": ("The One Maryland Economic Development Tax Credit occupies its own Schedule K-1 blocks (lines 29a-32 "
                 "and 33a-39, two vintages) and its own Form 500CR Parts P-I / P-II regime. Not computed in v1 — "
                 "prepare Form 500CR manually."),
     "notes": "R5."},
    {"diagnostic_id": "D_MD510_R6_SCORP_FORM_500", "severity": "error",
     "title": "R6 — this S corporation owes Maryland corporation income tax: file Form 500 as well",
     "condition": "entity_type_checkbox = s_corporation and (f1120s_line_23a > 0 or f1120s_line_23b > 0)",
     "message": ("'S corporations subject to federal corporation income tax, such as for excess net passive income or "
                 "built-in gains, also are subject to Maryland corporation income tax.' File Form 500 — enter the "
                 "corporation name, FEIN and tax year; enter the total taxable income on line 1; check the box "
                 "labeled 'Other' and enter '1120S'; report additions and subtractions to the extent applicable — IN "
                 "ADDITION to Form 510. Form 500 is not computed in v1. ⚠ The booklets address only the 510 case and "
                 "are silent on an ELECTING S corp (Form 500 + Form 511) — treat that combination as a diagnostic, "
                 "not a settled rule (W10)."),
     "notes": "R6 / W10. Trigger verified on the FINAL 2025 IRS Form 1120-S lines 23a/23b."},
    {"diagnostic_id": "D_MD510_R7_FORM_500UP", "severity": "error",
     "title": "R7 — Form 500UP underpayment interest and penalty is not computed",
     "condition": "interest_penalty_500up_19 entered, or estimates fall short of the 90%/110% safe harbour",
     "message": ("Estimated tax is required when the tax is expected to exceed $1,000; the safe harbour is 90% of the "
                 "current year or 110% of the prior year. Installments are due the 15th day of the 4th, 6th, 9th and "
                 "12th months for S corporations and the 4th, 6th, 9th and 13th months for partnerships, LLCs and "
                 "business trusts. Form 500UP is not computed in v1. ⚠ 'S corporations may not use the annualization "
                 "method on Form 500UP'; partnerships and LLCs that annualize must enter code number 301. Interest "
                 "runs at 10.8133% annually / 0.9011% per month before 1/1/2027."),
     "notes": "R7."},
    {"diagnostic_id": "D_MD510_R8_MW506NRS", "severity": "error",
     "title": "R8 — Form MW506NRS nonresident real-property withholding is not computed",
     "condition": "pay_16f_mw506nrs entered or k1_section_f_mw506nrs used",
     "message": ("Form MW506NRS (withholding on the nonresident sale of Maryland real property) is not prepared in "
                 "v1. Enter the payment on line 16f and flow each member's share through Schedule K-1 Section F. The "
                 "return must carry the federal return, the HUD-1 and the MW506NRS as attachments."),
     "notes": "R8."},
    {"diagnostic_id": "D_MD510_R9_FORM_500DM", "severity": "error",
     "title": "R9 — Form 500DM must be ATTACHED, but the PTE computes no adjustment on this return",
     "condition": "has_decoupling_modification",
     "message": ("Form 500DM instructions, verbatim: 'If the entity is a PTE ... no adjustment is made on the PTE's "
                 "Maryland income tax return (Form 510 or 511). However, Form 500DM must be submitted with Form 510 "
                 "or 511 and the PTE must provide each partner, shareholder or member a statement showing their share "
                 "of each decoupling modification with the appropriate code(s).' This is a PRO FORMA FEDERAL RETURN "
                 "regime, not a percentage add-back — prepare the pro forma manually and pass each member's share "
                 "through Schedule K-1 Section I with the codes. Maryland §179 is frozen at $25,000 / $200,000 — NOT "
                 "the federal OBBBA $2,500,000 / $4,000,000 and NOT Georgia's."),
     "notes": "R9."},
    {"diagnostic_id": "D_MD510_R10_MFG_CARVEOUT", "severity": "error",
     "title": "R10 — the §10-210.1 manufacturing carve-out has NO Maryland form line anywhere",
     "condition": "naics_31_33_manufacturing_entity is set AND any asset was placed in service on or after 1/1/2019",
     "message": ("Tax-General §10-210.1(b)(1)(ii) and (b)(3)(ii): the §168(k) bonus and §179 add-backs 'do not apply "
                 "to property placed in service by a manufacturing entity on or after January 1, 2019.' "
                 "§10-210.1(a)(4): a 'manufacturing entity' is primarily engaged in activities that, under the NAICS "
                 "United States Manual 2012 EDITION, fall in SECTOR 31, 32 or 33, excluding a refiner as defined in "
                 "Business Regulation §10-101. §10-310 extends this to corporations. ⚠ THIS CARVE-OUT APPEARS ON NO "
                 "TY2025 MARYLAND PTE FORM OR INSTRUCTION — it must be built from the statute alone and there is NO "
                 "printed cross-check. It is NOT the page-3 question 8 rule. And it does NOT reach §10-210.1(b)(5) "
                 "heavy-duty SUVs, which remain subject to the §280F limits for all taxpayers including manufacturing "
                 "entities. Not applied in v1 — flag for review."),
     "notes": "R10 / W2. ⚠ This wording is the ONLY place the carve-out lives in the product — it must be Ken-approved, not developer prose."},
    {"diagnostic_id": "D_MD510_R11_TIERED_PTE", "severity": "error",
     "title": "R11 — tiered-PTE credit chains beyond one level are not computed",
     "condition": "upstream_pte_k1_count > 1",
     "message": ("More than one upstream Maryland Schedule K-1 (510/511) is present. Credit chains through more than "
                 "one level of pass-through entity (Form 510 lines 16c/16d/16e, Form 511 line 13c, K-1 Section D line "
                 "4) are not computed in v1 — verify each level manually."),
     "notes": "R11."},
    {"diagnostic_id": "D_MD510_R12_PTP_CODE_704", "severity": "error",
     "title": "R12 — publicly traded pass-through entity (§10-102.1(j))",
     "condition": "is_publicly_traded_pte",
     "message": ("A publicly traded pass-through entity that files the annual information return for members "
                 "receiving more than $500 is exempt from the nonresident tax under §10-102.1(j) and 'should not file "
                 "Form 511'. Enter code number 704 on page 3 of Form 510. The exemption is not applied automatically "
                 "in v1 — verify the information-return condition first."),
     "notes": "R12."},
    {"diagnostic_id": "D_MD510_R13_INVEST_PTNSHP_705", "severity": "error",
     "title": "R13 — investment partnership relief (code 705) is not applied automatically",
     "condition": "is_investment_partnership",
     "message": ("A partnership whose activities and assets are limited to investment in stocks, bonds, futures, "
                 "options or debt obligations (other than debt instruments directly secured by real or tangible "
                 "personal property) is not subject to the nonresident tax merely because investment decisions, "
                 "trading orders and research are conducted by a general partner from a Maryland location. Enter code "
                 "number 705 on page 3. ⚠ Verify against Technical Bulletin 6 §II.B before suppressing the "
                 "nonresident tax — 'brokerage firms that deal with the general public are not exempt if the business "
                 "is conducted within Maryland and should complete lines 5-19.' Note the rule exists only in Booklet "
                 "510; Booklet 511 never mentions code 705 (W11(f))."),
     "notes": "R13."},
    {"diagnostic_id": "D_MD510_R14_EL102B", "severity": "error",
     "title": "R14 — a composite filer's extension uses Form EL102B, not Form 510/511E",
     "condition": "box_510c_filed and an extension is required",
     "message": ("'IMPORTANT: Composite Return filers use Form EL102B (See instructions).' Form EL102B is not "
                 "prepared in v1."),
     "notes": "R14."},
    {"diagnostic_id": "D_MD510_R15_501_PTE_FTI", "severity": "error",
     "title": "R15 — a §501-exempt PTE with federal taxable income must still file",
     "condition": "is_501_pte_with_fti",
     "message": ("'A PTE that qualifies for a IRC § 501 exemption and is treated as an association under 26 CFR § "
                 "301.7701-3(c)(1)(v)(A) and which has federal taxable income must file Form 510 or Form 511.' The "
                 "unrelated-business-income computation is not handled in v1 — prepare manually."),
     "notes": "R15."},
]

MD510_SCENARIOS: list[dict] = [
    {"scenario_name": "510 election — Box B on the 510/511D requires Form 510", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"election_first_filing_kind": "510_511D", "election_box_a_checked": False, "election_box_b_checked": True},
     "expected_outputs": {"required_year_end_form": FORM_510, "irrevocable": True, "deemed": False},
     "notes": "Box B = pay tax only on behalf of nonresident members -> Form 510 as the year-end return."},
    {"scenario_name": "510 deeming default — neither box checked on the first filing", "scenario_type": "edge", "sort_order": 2,
     "inputs": {"election_first_filing_kind": "510_511E", "election_box_a_checked": False, "election_box_b_checked": False},
     "expected_outputs": {"required_year_end_form": FORM_510, "irrevocable": True, "deemed": True},
     "notes": "'the Comptroller will deem you to have chosen to pay tax only on behalf of nonresident members, and that decision will be irrevocable.'"},
    {"scenario_name": "510 election undetermined — first filing not on record", "scenario_type": "failure", "sort_order": 3,
     "inputs": {"election_first_filing_kind": "unknown", "election_box_a_checked": None, "election_box_b_checked": None},
     "expected_outputs": {"required_year_end_form": None, "diagnostic": "D_MD510_ELECTION_UNDETERMINED"},
     "notes": "Nothing on the return reveals the election. The spec returns UNDETERMINED and raises an error — it never infers."},
    {"scenario_name": "510 nonresident tax — 6.50% + 2.25% and 8.25%", "scenario_type": "normal", "sort_order": 4,
     "inputs": {"4": 1000000, "pct_nonresident_individuals_l5": 0.40, "pct_nonresident_entities_l10": 0.25},
     "expected_outputs": {"6": 400000.0, "7": 26000.0, "8": 9000.0, "9": 35000.0,
                          "11": 250000.0, "12": 20625.0, "13": 55625.0},
     "notes": "L6 = 1,000,000 x .40 = 400,000; L7 = 400,000 x .065 = 26,000; L8 = 400,000 x .0225 = 9,000; L9 = 35,000. L11 = 250,000; L12 = 250,000 x .0825 = 20,625; L13 = 55,625."},
    {"scenario_name": "510 blank percentage means 100% of line 4", "scenario_type": "edge", "sort_order": 5,
     "inputs": {"4": 500000, "pct_nonresident_individuals_l5": None, "pct_nonresident_entities_l10": 0},
     "expected_outputs": {"6": 500000.0, "7": 32500.0, "8": 11250.0, "9": 43750.0, "13": 43750.0},
     "notes": "'If 100%, leave blank and enter the amount from line 4 on line 6.' 500,000 x 8.75% in total = 43,750, reached as 32,500 + 11,250."},
    {"scenario_name": "510 resident entity member is UNTAXED (line 1d)", "scenario_type": "edge", "sort_order": 6,
     "inputs": {"member_kind": "entity", "is_resident": True, "maryland_share": 100000},
     "expected_outputs": {"line": "1d", "taxed": False, "tax": 0.0},
     "notes": "W6. THE SAME MEMBER on Form 511 lands on line 1c and pays 8,250. Same member, different box, different tax."},
    {"scenario_name": "510 worksheet 9A scales DCF by nonresident ownership", "scenario_type": "normal", "sort_order": 7,
     "inputs": {"dcf_b_cash_method_restatement": 400000, "dcf_c_non_includable_receipts": 100000,
                "dcf_d_depreciation_addback": 150000, "dcf_e_liability_reserve_decrease": 50000,
                "dcf_g_non_deductible_expenditures": 200000, "dcf_h_liability_reserve_increase": 0,
                "nonresident_pct": 0.65, "dcf_l_nonresident_tax_prev_paid": 10000},
     "expected_outputs": {"W9A-F": 700000.0, "W9A-I": 500000.0, "W9A-K": 325000.0, "W9A-M": 315000.0},
     "notes": "F = 400k+100k+150k+50k = 700,000 (verbatim 'Add lines B through E' — W5(a)); I = 700,000 − 200,000 = 500,000; K = 500,000 × .65 = 325,000; M = 325,000 − 10,000 = 315,000."},
    {"scenario_name": "510 line 15 is line 13 when the DCF box is unchecked", "scenario_type": "failure", "sort_order": 8,
     "inputs": {"13": 55625, "14": None, "dcf_worksheet_used": False},
     "expected_outputs": {"15": 55625.0},
     "notes": "⚠ An unconditional MIN(L13, L14) would produce 0 here and zero out the tax. The lesser-of is CONDITIONAL on the checkbox."},
    {"scenario_name": "510 zero apportionment factor floors at .000001", "scenario_type": "edge", "sort_order": 9,
     "inputs": {"scha_1a_md": 0, "scha_1a_everywhere": 5000000},
     "expected_outputs": {"3b": 0.000001},
     "notes": "'(If factor is zero, enter .000001)'. NEVER dropped, NEVER reweighted — Maryland has no insignificant-denominator rule."},
    {"scenario_name": "510 payments roll-up across all seven lines", "scenario_type": "normal", "sort_order": 10,
     "inputs": {"pay_16a_estimated": 30000, "pay_16b_extension": 5000, "pay_16c_credit_from_other_pte": 2000,
                "pay_16d_credit_nonres_shares": 1500, "pay_16e_credit_res_shares": 500,
                "pay_16f_mw506nrs": 0, "pay_16g_amended_prior_payments": 0, "15": 55625},
     "expected_outputs": {"16h": 39000.0, "17": 16625.0, "18": 0.0},
     "notes": "16h = 30,000+5,000+2,000+1,500+500 = 39,000; L15 55,625 − 39,000 = 16,625 balance due. Seven payment lines vs the 511's five."},
    {"scenario_name": "510 K-1 Section D — credit with NO add-back", "scenario_type": "edge", "sort_order": 11,
     "inputs": {"k1_d1": 12000, "k1_d2": 0, "k1_d4": 0},
     "expected_outputs": {"D5_credit_total": 12000.0, "addback": 0.0},
     "notes": "W4. D1 is a pure 510 leg — credit only. Adding back D1 would double-tax every nonresident partner (§10-102.1(c)(1))."},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM MD_511 — Pass-Through Entity ELECTION Income Tax Return (ELECTING PTE)
# ═══════════════════════════════════════════════════════════════════════════

MD511_FACTS: list[dict] = _election_facts() + [
    # --- Member counts, lines 1a-1e (⚠ 1c and 1d have DIFFERENT scope than the 510) ---
    {"fact_key": "count_1a_resident_individuals", "label": "1a — Individual (including fiduciary) residents of Maryland (count)",
     "data_type": "integer", "required": False, "sort_order": 20,
     "notes": "⚠ TAXED at 8.75% on Form 511 — the same member is untaxed on Form 510."},
    {"fact_key": "count_1b_nonresident_individuals", "label": "1b — Individual (including fiduciary) nonresidents (count)",
     "data_type": "integer", "required": False, "sort_order": 21,
     "notes": "Taxed at 8.75% via line 5a, together with 1a. Fiduciaries belong here, not in the entity leg."},
    {"fact_key": "count_1c_nonres_and_res_entities", "label": "1c — Nonresident AND RESIDENT entities (count)",
     "data_type": "integer", "required": False, "sort_order": 22,
     "notes": "⚠ W6. Form 510's 1c is NONRESIDENT entities only. On the 511 a RESIDENT entity moves here and is taxed at 8.25%."},
    {"fact_key": "count_1d_others", "label": "1d — Others (IRC §408(e)/§501 exempt entities; see instructions) (count)",
     "data_type": "integer", "required": False, "sort_order": 23,
     "notes": "⚠ Booklet 511 conspicuously DROPS resident entities from 'Others' — only tax-exempt entities remain here."},
    # --- Income, lines 2-4 (the SALT add-back is the 511's base difference) ---
    {"fact_key": "fed_1065_sch_k_lines_1_11", "label": "Federal Form 1065 Schedule K lines 1-11, net (partnerships)",
     "data_type": "decimal", "required": False, "sort_order": 30},
    {"fact_key": "fed_1120s_sch_k_lines_1_10", "label": "Federal Form 1120-S Schedule K lines 1-10, net (S corporations)",
     "data_type": "decimal", "required": False, "sort_order": 31},
    {"fact_key": "federal_obligations_interest", "label": "Interest from federal obligations (subtracted from the line 2 base)",
     "data_type": "decimal", "required": False, "sort_order": 32},
    {"fact_key": "salt_deduction_1065_l14_or_1120s_l12", "label": "Federal deduction for taxes based on net income (1065 page-1 line 14 / 1120-S page-1 line 12)",
     "data_type": "decimal", "required": False, "sort_order": 33,
     "notes": ("'Taxes and licenses' on the FINAL 2025 IRS forms. ⚠ Only taxes BASED ON NET INCOME — 'does not include "
               "taxes with a basis other than net income, such as a gross receipts tax or a commercial activity tax'.")},
    {"fact_key": "prior_year_md_refund_in_federal_income", "label": "Prior-year Maryland PTE refund included in this year's federal income",
     "data_type": "decimal", "required": False, "sort_order": 34,
     "notes": ("⚠ MULTI-YEAR STATE. 'the disregarded deduction is adjusted for income on the federal return "
               "attributable to a refund of overpayment of the previous year's estimated taxes.' The add-back is the "
               "tax actually BORNE, not the cash paid.")},
    {"fact_key": "non_maryland_income_sep_acct", "label": "3a — Non-Maryland income (entities using separate accounting)",
     "data_type": "decimal", "required": False, "sort_order": 35},
    # --- Ownership percentages, lines 5a / 5b (⚠ 9999 convention) ---
    {"fact_key": "pct_individual_members_l5a", "label": "5a — Percentage of ownership by individual members on lines 1a AND 1b (decimal; 100% = 9999)",
     "data_type": "decimal", "required": False, "sort_order": 40,
     "notes": "⚠ FORM 511 CONVENTION: 'expressed as a decimal. If 100%, enter 9999.' There is NO blank convention here — the 510 uses blank."},
    {"fact_key": "pct_entity_members_l5b", "label": "5b — Percentage of ownership by entity members on line 1c (decimal; 100% = 9999)",
     "data_type": "decimal", "required": False, "sort_order": 41,
     "notes": "Covers RESIDENT and nonresident entity members alike."},
    # --- DCF worksheet 11A (NO ownership step) ---
    {"fact_key": "dcf_worksheet_used", "label": "11 — Distributable cash flow limitation worksheet used? (checkbox)",
     "data_type": "boolean", "required": False, "sort_order": 50,
     "notes": "⚠ W5. The L12 lesser-of applies ONLY when this is checked."},
    {"fact_key": "dcf_b_cash_method_restatement", "label": "Worksheet 11A B — cash-method restatement", "data_type": "decimal", "required": False, "sort_order": 51},
    {"fact_key": "dcf_c_non_includable_receipts", "label": "Worksheet 11A C — non-includable cash receipts", "data_type": "decimal", "required": False, "sort_order": 52},
    {"fact_key": "dcf_d_depreciation_addback", "label": "Worksheet 11A D — depreciation/amortization/depletion add-back", "data_type": "decimal", "required": False, "sort_order": 53},
    {"fact_key": "dcf_e_liability_reserve_decrease", "label": "Worksheet 11A E — decrease in liability reserve", "data_type": "decimal", "required": False, "sort_order": 54},
    {"fact_key": "dcf_g_non_deductible_expenditures", "label": "Worksheet 11A G — non-deductible cash expenditures", "data_type": "decimal", "required": False, "sort_order": 55},
    {"fact_key": "dcf_h_liability_reserve_increase", "label": "Worksheet 11A H — increase in liability reserve", "data_type": "decimal", "required": False, "sort_order": 56},
    {"fact_key": "dcf_j_members_tax_previously_paid", "label": "Worksheet 11A J — ALL MEMBERS' estimated tax paid with Forms 510/511D or 510/511E",
     "data_type": "decimal", "required": False, "sort_order": 57,
     "notes": "⚠ Worksheet 11A has NO ownership-percentage step — its J is members' tax previously paid, where 9A's J is the ownership percentage."},
    # --- Payments 13a-13e (FIVE lines, not seven) ---
    {"fact_key": "pay_13a_estimated", "label": "13a — Estimated tax paid with Form 510/511D (and prior year overpayment)", "data_type": "decimal", "required": False, "sort_order": 60},
    {"fact_key": "pay_13b_extension", "label": "13b — Tax paid with an extension request on Form 510/511E", "data_type": "decimal", "required": False, "sort_order": 61},
    {"fact_key": "pay_13c_credit_from_other_pte", "label": "13c — Credit for tax paid by another pass-through entity (Attach Maryland Schedule K-1 (510/511))",
     "data_type": "decimal", "required": False, "sort_order": 62,
     "notes": "⚠ ONE line here; Form 510 splits the same concept across 16c, 16d (nonresident shares) and 16e (resident shares)."},
    {"fact_key": "pay_13d_mw506nrs", "label": "13d — Payment made with Form MW506NRS", "data_type": "decimal", "required": False, "sort_order": 63, "notes": "R8 RED-defer."},
    {"fact_key": "pay_13e_amended_prior_payments", "label": "13e — If amending, total payments made with original plus additional tax paid after", "data_type": "decimal", "required": False, "sort_order": 64,
     "notes": "U5: Booklet 511 Instruction 8 wrongly points at line 13d (the MW506NRS line). The face governs — 13e."},
    {"fact_key": "prior_overpayment_15a", "label": "15a — If amending, prior overpayment (total all refunds previously issued)", "data_type": "decimal", "required": False, "sort_order": 65},
    {"fact_key": "interest_penalty_500up_16", "label": "16 — Interest and/or penalty from Form 500UP or late payment interest", "data_type": "decimal", "required": False, "sort_order": 66, "notes": "R7 RED-defer."},
    {"fact_key": "overpayment_applied_next_year", "label": "18 — Overpayment applied to next year's estimated tax", "data_type": "decimal", "required": False, "sort_order": 67},
    # --- Defer triggers ---
    {"fact_key": "composite_510c_attempted", "label": "Composite Form 510C attempted? (⚠ BARRED for an Electing PTE)", "data_type": "boolean", "required": False, "sort_order": 70,
     "notes": "There is NO '510C Filed' checkbox on Form 511. The line-17 NOTE nonetheless mentions 'the composite return' — erratum W11(e)."},
    {"fact_key": "is_publicly_traded_pte", "label": "Publicly traded pass-through entity (§10-102.1(j))?", "data_type": "boolean", "required": False, "sort_order": 71,
     "notes": "R12 — a PTP 'should not file Form 511'."},
    {"fact_key": "is_investment_partnership", "label": "Investment partnership? (⚠ Booklet 511 has NO such instruction — W11(f))", "data_type": "boolean", "required": False, "sort_order": 72},
    {"fact_key": "is_501_pte_with_fti", "label": "IRC §501-exempt PTE with federal taxable income?", "data_type": "boolean", "required": False, "sort_order": 73, "notes": "R15."},
    {"fact_key": "has_decoupling_modification", "label": "Any Maryland decoupling modification present (Form 500DM must be attached)?", "data_type": "boolean", "required": False, "sort_order": 74, "notes": "R9."},
] + _schedule_a_facts(300) + _page3_facts(400) + _k1_facts(500, FORM_511)

MD511_RULES: list[dict] = [
    {"rule_id": "R-MD511-ELECT", "title": "Election state machine — Form 511 is legal ONLY for an electing PTE",
     "rule_type": "routing", "sort_order": 1,
     "formula": ("election = f(election_first_filing_kind, election_box_a_checked, election_box_b_checked) ; "
                 "510_511D|510_511E: A&B -> MD_511 (DEEMED) ; A -> MD_511 ; B -> MD_510 ; neither -> MD_510 (DEEMED) ; "
                 "year_end_return: filing MD_511 IS the irrevocable election ; "
                 "unknown -> UNDETERMINED (ERROR diagnostic, never inferred) ; "
                 "if election_recorded_form == MD_510 -> HARD BLOCK: file Form 510 ; "
                 "is_amended_return cannot change the election"),
     "inputs": ["election_first_filing_kind", "election_box_a_checked", "election_box_b_checked",
                "election_recorded_form", "is_amended_return"],
     "outputs": ["required_year_end_form"],
     "description": ("W1. Identical machine to the 510's, with the mirror outcome. Booklet 511: 'If you did not file "
                     "Form 510/511D or Form 510/511E, filing Form 511 is an irrevocable election to be taxed at the "
                     "entity level for tax year 2025. You may not change this election on an amended return.' "
                     "Year-keyed: 'first filing wins' is suspended for TY2026 only."),
     "exceptions": "TY2026 only — the Comptroller ignores an election made with the Q1 estimated payment."},
    {"rule_id": "R-MD511-MEMBER", "title": "Member classification into lines 1a-1e — ALL members are taxed",
     "rule_type": "classification", "sort_order": 2,
     "formula": ("resident individual/fiduciary -> 1a (TAXED 8.75%) ; nonresident individual/fiduciary -> 1b (TAXED 8.75%) ; "
                 "nonresident entity -> 1c (8.25%) ; RESIDENT ENTITY -> 1c (8.25%) ; "
                 "REIT / IRC 408(e) / 501 exempt -> 1d 'Others' (UNTAXED) ; 1e = 1a + 1b + 1c + 1d"),
     "inputs": ["count_1a_resident_individuals", "count_1b_nonresident_individuals",
                "count_1c_nonres_and_res_entities", "count_1d_others"],
     "outputs": ["1a", "1b", "1c", "1d", "1e"],
     "description": ("⚠ W6 — THE SINGLE MOST CONSEQUENTIAL LINE-FOR-LINE DIFFERENCE. Form 511 line 1c reads "
                     "'Nonresident AND RESIDENT entities' where the 510's reads 'Nonresident entities'. Booklet 511 "
                     "drops resident entities from 'Others' and counts them at 1c. The same resident entity member "
                     "that is UNTAXED on a 510 pays 8.25% on a 511. Fiduciaries remain inside the individual legs."),
     "notes": "U6: REIT/§408(e)/§501 exclusion for the ELECTING leg rests on TB 6 §II.A + TG §10-104, not §10-102.1(f) — re-verify §10-104 before seeding."},
    {"rule_id": "R-MD511-L2", "title": "Line 2 — pass-through entity taxable income (federal base PLUS the SALT add-back)",
     "rule_type": "calculation", "sort_order": 3,
     "formula": ("partnership: L2 = net(1065 Sch. K lines 1-11) - federal_obligations_interest "
                 "+ salt_deduction(1065 page-1 line 14) ; "
                 "S corporation: L2 = net(1120S Sch. K lines 1-10) - federal_obligations_interest "
                 "+ salt_deduction(1120S page-1 line 12) ; "
                 "the disregarded deduction is ADJUSTED for prior-year Maryland refund income included this year "
                 "(add back the tax actually BORNE, not the cash paid)"),
     "inputs": ["fed_1065_sch_k_lines_1_11", "fed_1120s_sch_k_lines_1_10", "federal_obligations_interest",
                "salt_deduction_1065_l14_or_1120s_l12", "prior_year_md_refund_in_federal_income", "entity_type_checkbox"],
     "outputs": ["2"],
     "description": ("⚠ THE ELECTING BASE — §10-102.1(a)(8) as it stood for TY2025 (SB 787 of 2021, quoted verbatim in "
                     "TB 6 §I.A): income under the federal IRC 'calculated without regard to any deduction for taxes "
                     "based on net income that are imposed by any state or political subdivision of a state, that is "
                     "derived from or reasonably attributable to the trade or business of the pass-through entity in "
                     "this State.' The add-back covers only taxes BASED ON NET INCOME — not gross receipts or "
                     "commercial activity taxes. ⚠ MULTI-YEAR STATE: the prior-year Maryland refund adjustment cannot "
                     "be derived from a single year's federal return."),
     "notes": ("⚠ TY2027: the base changes to 'residents everywhere + nonresidents Maryland' (2025 Md. Laws Ch. 604 as "
               "postponed by 2026 Md. Laws Ch. 6 §4). For TY2025 the printed form and the statute AGREE — build as "
               "printed. (Former walk item W3 WITHDRAWN as a false conflict; do not re-raise it.)")},
    {"rule_id": "R-MD511-ALLOC", "title": "Lines 3a/3b -> line 4 — EVERY multistate PTE allocates",
     "rule_type": "conditional", "sort_order": 4,
     "formula": ("if not is_multistate: L4 = L2 ; "
                 "elif allocation_method == separate_accounting: L4 = L2 - L3a ; "
                 "else: L4 = L2 x L3b   [if the factor is zero, enter .000001]"),
     "inputs": ["is_multistate", "allocation_method", "non_maryland_income_sep_acct", "entity_type_checkbox"],
     "outputs": ["3a", "3b", "4"],
     "description": ("⚠ THE GATE DIFFERS FROM THE 510. Form 511: 'Multistate pass-through entities must complete Line "
                     "3a. or 3b. Unistate entities go to line 4.' — NO 'with nonresident members' qualifier, so every "
                     "multistate 511 allocates. The apportioned line 4 applies to RESIDENT and NONRESIDENT members "
                     "alike for TY2025; TB 6 §I.B: 'Multistate electing PTEs must apportion their income.'")},
    {"rule_id": "R-MD511-APPORT", "title": "Schedule A — single receipts factor, six decimals, .000001 floor, NEVER reweighted",
     "rule_type": "calculation", "sort_order": 5,
     "formula": ("column 3 = column 1 / column 2 rounded to SIX places ; SchA-4 = receipts factor unless a "
                 "Comptroller-accepted special/alternative factor is entered ; if factor == 0: enter .000001 on line 3b ; "
                 "property and payroll factors NEVER reweight the receipts factor"),
     "inputs": ["scha_1a_md", "scha_1a_everywhere", "scha_special_or_alternative_checked", "scha_accepted_alternative_factor"],
     "outputs": ["SchA-1h", "SchA-2g", "SchA-3c", "SchA-4", "3b"],
     "description": ("⚠⚠ W9 / U11. MARYLAND HAS NO INSIGNIFICANT-DENOMINATOR RULE — that is Fla. Stat. §220.15(1). "
                     "A zero factor is FLOORED at .000001 (form face only). COMAR 03.04.03.08 B(5) requires a factor "
                     "even on a loss return. Only the Comptroller may alter a formula (§10-402(e); §10-401(2)). "
                     "The software must NEVER auto-drop, auto-reweight or auto-substitute a factor."),
     "exceptions": "Special and Alternative formulas are RED-deferred (R2/R3)."},
    {"rule_id": "R-MD511-GATE", "title": "Completion gate — lines 5a through 19 only if line 1a THROUGH 1d has an entry",
     "rule_type": "conditional", "sort_order": 6,
     "formula": "complete_lines_5a_to_19 = any entry on lines 1a, 1b, 1c or 1d",
     "inputs": ["count_1a_resident_individuals", "count_1b_nonresident_individuals",
                "count_1c_nonres_and_res_entities", "count_1d_others"],
     "outputs": ["gate_5a_19"],
     "description": ("Form 511 face: 'Complete lines 5a. through 19 only if there is an entry on line 1a. through line "
                     "1d.' ⚠ Broader than the 510's gate, which fires only on 1b or 1c — because the electing tax "
                     "reaches ALL members, resident included."),
     "notes": "⚠ The line-4 NOTE says '(Investment partnerships see Specific Instructions)' but Booklet 511 has NO such instruction and never mentions code 705 — erratum W11(f)."},
    {"rule_id": "R-MD511-PCT", "title": "Lines 5a/5b/5c — ownership percentages, with the 9999 = 100% convention",
     "rule_type": "calculation", "sort_order": 7,
     "formula": ("L5a = pct by individual members on lines 1a AND 1b (decimal; 9999 means 100%) ; "
                 "L5b = pct by entity members on line 1c (decimal; 9999 means 100%) ; L5c = L5a + L5b"),
     "inputs": ["pct_individual_members_l5a", "pct_entity_members_l5b"], "outputs": ["5a", "5b", "5c"],
     "description": ("⚠ THE TWO FORMS USE DIFFERENT 100% CONVENTIONS. Booklet 511: 'expressed as a decimal. If 100%, "
                     "enter 9999' — and the Form 511 face carries no 100% instruction at all. Booklet 510 instead "
                     "says 'If 100%, leave blank'. A shared normaliser that handles 100% one way MIS-ENTERS one of "
                     "the two returns."),
     "notes": "The form permits profit/loss percentages instead of ownership percentages, which the software cannot derive — direct-entry."},
    {"rule_id": "R-MD511-TAX", "title": "Lines 6-10 — the Electing PTE tax (8.75% and 8.25%)",
     "rule_type": "calculation", "sort_order": 8,
     "formula": ("L6 = L4 x L5a ; L7 = L6 x 8.75%   [ONE multiplier: §10-106.1 2.25% + §10-105(a) 6.50%] ; "
                 "L8 = L4 x L5b ; L9 = L8 x 8.25%   [§10-105(b)] ; L10 = L7 + L9"),
     "inputs": ["4", "5a", "5b"], "outputs": ["6", "7", "8", "9", "10"],
     "description": ("⚠ THE 511 APPLIES ONE 8.75% MULTIPLIER where the 510 applies 6.50% and 2.25% separately and "
                     "adds. Mathematically identical, different rounding points. Both forms print whole-dollar boxes "
                     "— follow each form's own line structure. The 8.75% covers RESIDENT individual and fiduciary "
                     "members too; the 8.25% covers RESIDENT entity members too."),
     "notes": "Rates are DERIVED, year-keyed constants with both statutory inputs cited — never a hardcoded 0.0875."},
    {"rule_id": "R-MD511-DCF11A", "title": "Worksheet 11A — distributable cash flow with NO ownership step",
     "rule_type": "calculation", "sort_order": 9,
     "formula": ("F = B + C + D + E ; I = F - (G + H) ; "
                 "J = all members' tax previously paid with 510/511D or 510/511E ; "
                 "K = max(0, I - J) -> Form 511 line 11    [NO ownership multiplier anywhere in 11A]"),
     "inputs": ["dcf_b_cash_method_restatement", "dcf_c_non_includable_receipts", "dcf_d_depreciation_addback",
                "dcf_e_liability_reserve_decrease", "dcf_g_non_deductible_expenditures",
                "dcf_h_liability_reserve_increase", "dcf_j_members_tax_previously_paid"],
     "outputs": ["W11A-F", "W11A-I", "W11A-J", "W11A-K", "11"],
     "description": ("W5. Worksheet 11A runs A-K; worksheet 9A runs A-M and multiplies line I by the nonresident "
                     "ownership percentage. 11A's line I IS the whole distributable cash flow, and its line J is "
                     "members' tax previously paid — the slot 9A uses for the ownership percentage. Cloning one into "
                     "the other over-caps or under-caps every DCF return. Statutory cap: §10-102.1(d)(3)."),
     "notes": ("⚠ W5(a): line F encoded verbatim as 'Add lines B through E', which omits line A. Gated by "
               "MD_DCF_F_INCLUDES_LINE_A = False. ⚠ W5(b)/U7: the amended-return bar is UNSUPPORTED and NOT encoded.")},
    {"rule_id": "R-MD511-L12", "title": "Line 12 — CONDITIONAL lesser-of, gated on the worksheet checkbox",
     "rule_type": "conditional", "sort_order": 10,
     "formula": "L12 = L10 if not dcf_worksheet_used else min(L10, L11)",
     "inputs": ["10", "11", "dcf_worksheet_used"], "outputs": ["12"],
     "description": ("Identical construction to Form 510 line 15: if the distributable cash flow limitation is not "
                     "used, enter line 10; if it is used, enter the lesser of line 10 or line 11. AN UNCONDITIONAL "
                     "MIN() ZEROES THE TAX whenever line 11 is blank. 'Election of the distributable cash flow "
                     "limitation will not reduce the tax liability of the members.'")},
    {"rule_id": "R-MD511-PAY", "title": "Lines 13a-13f — payments and credits (FIVE lines, one upstream-credit line)",
     "rule_type": "calculation", "sort_order": 11,
     "formula": "L13f = 13a + 13b + 13c + 13d + 13e",
     "inputs": ["pay_13a_estimated", "pay_13b_extension", "pay_13c_credit_from_other_pte",
                "pay_13d_mw506nrs", "pay_13e_amended_prior_payments"],
     "outputs": ["13f"],
     "description": ("⚠ FIVE payment lines to the 510's seven. Line 13c is a single 'credit for tax paid by another "
                     "pass-through entity' line — the 510 splits the same concept into 16c, 16d (nonresident shares) "
                     "and 16e (resident shares). U5: the booklet's '13d' pointer for amended payments is an erratum; "
                     "the face says 13e.")},
    {"rule_id": "R-MD511-SETTLE", "title": "Lines 14-19 — balance due, overpayment, refund",
     "rule_type": "calculation", "sort_order": 12,
     "formula": ("L14 = max(0, L12 - L13f) ; L15 = max(0, L13f - L12) ; "
                 "L17 = L12 + L15a + L16 - L13f ; L18 <= (L15 - L15a - L16) ; "
                 "L19 = L15 - (L16 + L18)  [if amending: L15 - L15a - L16]"),
     "inputs": ["12", "13f", "prior_overpayment_15a", "interest_penalty_500up_16", "overpayment_applied_next_year"],
     "outputs": ["14", "15", "15a", "16", "17", "18", "19"],
     "description": "Overpayments are refunded to the PTE, not distributed to members (Comptroller v. FC-GEN; K-1 Section D line 3 is RESERVED)."},
    {"rule_id": "R-MD511-SCHB", "title": "Schedule B Parts I-IV — per-member roster, shares off LINE 2",
     "rule_type": "calculation", "sort_order": 13,
     "formula": ("Parts I-IV identical to the 510's (only the printed form number differs) ; "
                 "per-member income share = a portion of LINE 2, page 1 (NOT line 4) ; "
                 "cross-foot Parts I+II to 1a+1b and Parts III+IV to 1c/1d"),
     "inputs": ["2", "count_1a_resident_individuals", "count_1b_nonresident_individuals",
                "count_1c_nonres_and_res_entities", "count_1d_others"],
     "outputs": ["SchB"],
     "description": ("A byte-level diff of pages 5-8 of the two forms returned only header and form-number "
                     "differences. ⚠ The per-member share is a portion of LINE 2 while the tax lines run off the "
                     "APPORTIONED line 4 — do not wire Schedule B off line 4. Margin note: 'You must file Form 511 "
                     "electronically to pass on business tax credits from Form 500CR and/or Form 502S to your members.'")},
    {"rule_id": "R-MD511-K1D", "title": "Schedule K-1 Section D — the 511 legs are D2/D4: CREDIT **AND** ADD-BACK",
     "rule_type": "calculation", "sort_order": 14,
     "formula": ("K-1 D2 = member's share of Form 511 line 12 ; D4 = entity-level tax paid by OTHER PTEs ; "
                 "D5 = D1 + D2 + D4  [the CREDIT] ; "
                 "MANDATORY ADD-BACK = D2 + D4 ONLY — never D1 ; "
                 "the add-back must NOT be pre-loaded into K-1 Section B additions"),
     "inputs": ["12"], "outputs": ["K1-D2", "K1-D4", "K1-D5", "K1-addback"],
     "description": ("⚠ W4 — THE OWNER SIDE IS TWO LEGS. Leg 1, the credit (§10-701.1), routes to Form 502CR Part CC "
                     "line 9 (individuals), Form 500CR (corporations), Form 504 (fiduciaries) and Form 511 line 13c "
                     "(PTE members). Leg 2, the add-back, is on the K-1 form face: 'Members with entries on Lines 2 "
                     "and 4 are required to addback the amount of the credit total on Line 2 and 4 on their "
                     "respective returns' — Form 502 Other Additions code 'r' for individuals; §10-306(b)(6) -> "
                     "§10-205(m) for corporate members; Form 504 line 1 for trusts. IMPLEMENTING ONLY THE CREDIT "
                     "OVERSTATES OWNER RELIEF BY THE FULL PTET — the classic Maryland PTET bug. And the add-back "
                     "NEVER attaches to D1. Emit it as a TYPED MODIFICATION so the 1040/1120/1041 modules cannot "
                     "drop it."),
     "notes": "K-1 Section B instruction: 'For electing PTEs, do not include in additions the member's addback of the electing PTE credit.'"},
    {"rule_id": "R-MD511-K1H", "title": "Schedule K-1 Section H — capital-gain reporting, column 2 = column 1 x the factor",
     "rule_type": "calculation", "sort_order": 15,
     "formula": ("H column 2 (Maryland net capital gain, NONRESIDENT MEMBERS ONLY) = column 1 x Schedule A line 4 ; "
                 "row 3 is RESIDENT MEMBERS ONLY — column 2 blocked out ; no entity-level surtax is computed"),
     "inputs": ["k1_section_h_col1_rows", "SchA-4"], "outputs": ["K1-H"],
     "description": ("W7. Mandatory for TY2025 on both forms, feeding members' Forms 502CG/504CG, with NO tax line on "
                     "either return face. A SECOND consumer of the apportionment factor. ⚠ Encode against IRC §408 / "
                     "§408A and TB 58 — the instruction's '§458 / §458A' is a misprint, recorded not fixed.")},
    {"rule_id": "R-MD511-RATES", "title": "The Electing PTE rates are a YEAR-KEYED DERIVATION, not literals",
     "rule_type": "validation", "sort_order": 16,
     "formula": ("individual/fiduciary rate = §10-106.1 lowest county (0.0225) + §10-105(a) top marginal (0.0650) "
                 "= 0.0875 at L7 ; entity rate = §10-105(b) = 0.0825 at L9 ; "
                 "STALENESS: the inputs are verified for TY2025 only — any other tax year invalidates them"),
     "inputs": [], "outputs": ["rate_individual_ptet", "rate_entity"],
     "description": ("§10-102.1(d)(2)(i): 'a rate equal to the sum of the rate of the tax imposed under § 10-106.1 ... "
                     "and the top marginal State tax rate for individuals under § 10-105(a)'. The rate MOVED from "
                     "8.00% to 8.75% for TY2025 with no PTE legislation, purely because the BRFA of 2025 added a "
                     "6.50% top bracket. Encode as a derivation with both inputs cited and a staleness assertion — "
                     "NOT as a hardcoded 0.0875.")},
]

MD511_RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R-MD511-ELECT", "MD_2025_FORM_510_511E", "primary", "both deeming defaults + irrevocability, verbatim"),
    ("R-MD511-ELECT", "MD_2025_PTE_BOOKLET_511", "primary", "FILING FORM 511 instruction, verbatim"),
    ("R-MD511-ELECT", "MD_2025_FORM_511", "secondary", "face: 'used by PTEs that elect to remit tax on all members' shares'"),
    ("R-MD511-ELECT", "MD_COMP_ALERT_PTE_TY2026", "secondary", "TY2026 suspension of 'first filing wins'"),
    ("R-MD511-MEMBER", "MD_2025_FORM_511", "primary", "line 1c = 'Nonresident and resident entities'"),
    ("R-MD511-MEMBER", "MD_2025_PTE_BOOKLET_511", "primary", "1c counts nonresident AND resident entities; 'Others' drops resident entities"),
    ("R-MD511-MEMBER", "MD_TB_6_PTE", "secondary", "§II.A exempt-member definition (U6 footing)"),
    ("R-MD511-L2", "MD_2025_PTE_BOOKLET_511", "primary", "line 2 base + SALT add-back + the prior-year-refund worked example"),
    ("R-MD511-L2", "MD_TG_10_102_1", "primary", "(a)(8) TY2025 vintage definition"),
    ("R-MD511-L2", "MD_TB_6_PTE", "primary", "§I.A quotes the operative TY2025 text; §I.B requires apportionment"),
    ("R-MD511-L2", "MD_COMP_ALERT_PTE_TY2026", "secondary", "TY2027 postponement — the dated future re-spec"),
    ("R-MD511-ALLOC", "MD_2025_FORM_511", "primary", "ALLOCATION OF INCOME header — every multistate PTE allocates"),
    ("R-MD511-ALLOC", "MD_TB_6_PTE", "secondary", "'Multistate electing PTEs must apportion their income.'"),
    ("R-MD511-APPORT", "MD_2025_FORM_511", "primary", "'(If factor is zero, enter .000001)' — FORM FACE ONLY"),
    ("R-MD511-APPORT", "MD_TG_10_402_401", "primary", "§10-402(e): only the Comptroller may alter a formula; no insignificance rule"),
    ("R-MD511-APPORT", "MD_COMAR_03_04_03_08", "secondary", "B(5) a factor is computed even on a loss return"),
    ("R-MD511-GATE", "MD_2025_FORM_511", "primary", "face NOTE: 'only if there is an entry on line 1a. through line 1d.'"),
    ("R-MD511-PCT", "MD_2025_PTE_BOOKLET_511", "primary", "'expressed as a decimal. If 100%, enter 9999'"),
    ("R-MD511-TAX", "MD_2025_FORM_511", "primary", "L7 8.75% and L9 8.25% on the form face"),
    ("R-MD511-TAX", "MD_2025_PTE_BOOKLET_511", "secondary", "narrative: 6.50% + 2.25% for individuals, 8.25% for entities"),
    ("R-MD511-DCF11A", "MD_2025_FORM_511", "primary", "worksheet 11A lines A-K with NO ownership step"),
    ("R-MD511-DCF11A", "MD_TG_10_102_1", "secondary", "(d)(3) statutory distributable-cash-flow cap"),
    ("R-MD511-L12", "MD_2025_PTE_BOOKLET_511", "primary", "line 12 conditional lesser-of"),
    ("R-MD511-PAY", "MD_2025_FORM_511", "primary", "13a-13e verbatim; one upstream-credit line"),
    ("R-MD511-SETTLE", "MD_2025_FORM_511", "primary", "lines 14-19 arithmetic off the form face"),
    ("R-MD511-SCHB", "MD_2025_PTE_BOOKLET_511", "primary", "'a portion of the amount on line 2, page 1'"),
    ("R-MD511-K1D", "MD_2025_SCH_K1_510_511", "primary", "Section D line 5 add-back note; D2/D4 instructions"),
    ("R-MD511-K1D", "MD_TG_10_701_1", "primary", "the §10-701.1 credit leg"),
    ("R-MD511-K1D", "MD_TG_10_102_1", "secondary", "(c)(3) the electing tax is imposed on the entity itself"),
    ("R-MD511-K1H", "MD_2025_SCH_K1_510_511", "primary", "Section H columns and the apportionment-factor rule"),
    ("R-MD511-RATES", "MD_TG_10_105_106_1", "primary", "the two rate inputs, verbatim"),
    ("R-MD511-RATES", "MD_TG_10_102_1", "primary", "(d)(2) the derivation construction"),
]

MD511_LINES: list[dict] = [
    {"line_number": "1a", "description": "Individual (including fiduciary) residents of Maryland — TAXED at 8.75% on Form 511",
     "line_type": "input", "source_facts": ["count_1a_resident_individuals"], "sort_order": 1,
     "notes": "⚠ The same member is UNTAXED on Form 510."},
    {"line_number": "1b", "description": "Individual (including fiduciary) nonresidents", "line_type": "input",
     "source_facts": ["count_1b_nonresident_individuals"], "sort_order": 2},
    {"line_number": "1c", "description": "Nonresident AND RESIDENT entities — taxed at 8.25%", "line_type": "input",
     "source_facts": ["count_1c_nonres_and_res_entities"], "sort_order": 3,
     "notes": "⚠ W6. Form 510's 1c is nonresident entities only; a resident entity sits at the 510's 1d and is untaxed."},
    {"line_number": "1d", "description": "Others (see instructions) — IRC §408(e)/§501 exempt entities; resident entities are NOT here",
     "line_type": "input", "source_facts": ["count_1d_others"], "sort_order": 4},
    {"line_number": "1e", "description": "Total", "line_type": "subtotal", "source_rules": ["R-MD511-MEMBER"], "sort_order": 5},
    {"line_number": "2", "description": "Pass-through entity taxable income (See instructions). Unistate entities also enter this amount on line 4.",
     "line_type": "calculated", "calculation": "R-MD511-L2", "source_rules": ["R-MD511-L2"], "sort_order": 6,
     "notes": "Federal Sch. K income block LESS federal-obligation interest PLUS the SALT add-back, net of the prior-year Maryland refund."},
    {"line_number": "3a", "description": "Non-Maryland income (for entities using separate accounting). Subtract this amount from line 2 and enter the difference on line 4.",
     "line_type": "input", "source_facts": ["non_maryland_income_sep_acct"], "sort_order": 7},
    {"line_number": "3b", "description": "Maryland apportionment factor from computation worksheet on Page 4 (If factor is zero, enter .000001)",
     "line_type": "calculated", "calculation": "R-MD511-APPORT", "source_rules": ["R-MD511-APPORT"], "sort_order": 8},
    {"line_number": "4", "description": "Pass-through entity taxable income allocable to Maryland (header: Entity Tax Calculation)",
     "line_type": "subtotal", "source_rules": ["R-MD511-ALLOC"], "sort_order": 9,
     "notes": "For TY2025 this base is Maryland-source for ALL members, resident included — statute and form AGREE (former W3 withdrawn)."},
    {"line_number": "5a", "description": "Percentage of ownership by individual members shown on lines 1a and 1b (decimal; If 100%, enter 9999)",
     "line_type": "input", "source_facts": ["pct_individual_members_l5a"], "sort_order": 10,
     "notes": "⚠ The 510 instead says 'If 100%, leave blank'."},
    {"line_number": "5b", "description": "Percentage of ownership by entity members shown on line 1c (decimal; If 100%, enter 9999)",
     "line_type": "input", "source_facts": ["pct_entity_members_l5b"], "sort_order": 11},
    {"line_number": "5c", "description": "Add Lines 5a and 5b", "line_type": "subtotal", "source_rules": ["R-MD511-PCT"], "sort_order": 12},
    {"line_number": "6", "description": "Pass-through entity taxable income for individual members (Multiply line 4 by the percentage on line 5a.)",
     "line_type": "calculated", "source_rules": ["R-MD511-TAX"], "sort_order": 13},
    {"line_number": "7", "description": "Total Individual members' pass-through entity election tax (Multiply line 6 by 8.75%.)",
     "line_type": "calculated", "source_rules": ["R-MD511-TAX"], "sort_order": 14,
     "notes": "ONE multiplier here; the 510 applies 6.50% (L7) and 2.25% (L8) separately and adds."},
    {"line_number": "8", "description": "Pass-through entity taxable income for entity members (Multiply line 4 by percentage on line 5b.)",
     "line_type": "calculated", "source_rules": ["R-MD511-TAX"], "sort_order": 15},
    {"line_number": "9", "description": "Entity members' pass-through entity election tax (Multiply line 8 by 8.25%.)",
     "line_type": "calculated", "source_rules": ["R-MD511-TAX"], "sort_order": 16},
    {"line_number": "10", "description": "Total pass-through entity election tax (Add lines 7 and 9.)", "line_type": "subtotal",
     "source_rules": ["R-MD511-TAX"], "sort_order": 17},
    {"line_number": "11", "description": "Distributable cash flow limitation from worksheet. See instructions. If worksheet used, check here",
     "line_type": "calculated", "calculation": "R-MD511-DCF11A", "source_rules": ["R-MD511-DCF11A"], "sort_order": 18},
    {"line_number": "12", "description": "Pass-through entity election tax due (Enter the lesser of line 10 or line 11.) — CONDITIONAL on the checkbox",
     "line_type": "calculated", "calculation": "R-MD511-L12", "source_rules": ["R-MD511-L12"], "sort_order": 19,
     "notes": "⚠ If the DCF limitation is not used, enter line 10. An unconditional MIN() zeroes the tax."},
    {"line_number": "13a", "description": "Estimated tax paid with Form 510/511D (and prior year overpayment)", "line_type": "input",
     "source_facts": ["pay_13a_estimated"], "sort_order": 20},
    {"line_number": "13b", "description": "Tax paid with an extension request on Form 510/511E", "line_type": "input",
     "source_facts": ["pay_13b_extension"], "sort_order": 21},
    {"line_number": "13c", "description": "Credit for tax paid by another pass-through entity (Attach Maryland Schedule K-1 (510/511).)",
     "line_type": "input", "source_facts": ["pay_13c_credit_from_other_pte"], "sort_order": 22,
     "notes": "⚠ ONE line, where the 510 splits it into 16c / 16d / 16e."},
    {"line_number": "13d", "description": "Payment made with Form MW506NRS", "line_type": "input",
     "source_facts": ["pay_13d_mw506nrs"], "sort_order": 23},
    {"line_number": "13e", "description": "If amending, total payments made with original plus additional tax paid after original was filed.",
     "line_type": "input", "source_facts": ["pay_13e_amended_prior_payments"], "sort_order": 24,
     "notes": "U5: Booklet 511 wrongly points at 13d. The face governs."},
    {"line_number": "13f", "description": "Total payments and credits (Add lines 13a through 13e.)", "line_type": "subtotal",
     "source_rules": ["R-MD511-PAY"], "sort_order": 25},
    {"line_number": "14", "description": "Balance of tax due (If line 12 exceeds line 13f, enter the difference.)",
     "line_type": "calculated", "source_rules": ["R-MD511-SETTLE"], "sort_order": 26},
    {"line_number": "15", "description": "Overpayment (If line 13f exceeds line 12, enter the difference.)",
     "line_type": "calculated", "source_rules": ["R-MD511-SETTLE"], "sort_order": 27},
    {"line_number": "15a", "description": "If amending, prior overpayment (Total all refunds previously issued.)",
     "line_type": "input", "source_facts": ["prior_overpayment_15a"], "sort_order": 28},
    {"line_number": "16", "description": "Interest and/or penalty from Form 500UP or late payment interest",
     "line_type": "input", "source_facts": ["interest_penalty_500up_16"], "sort_order": 29, "notes": "R7 RED-defer."},
    {"line_number": "17", "description": "Total balance due (Add lines 12, 15a and 16. Subtract line 13f.)",
     "line_type": "total", "source_rules": ["R-MD511-SETTLE"], "sort_order": 30,
     "notes": "⚠ The NOTE printed under this line mentions 'the composite return', which Booklet 511 BARS for an Electing PTE — erratum W11(e)."},
    {"line_number": "18", "description": "Amount of overpayment to be applied to estimated tax for next year (not to exceed the net of lines 15 minus 15a and 16.)",
     "line_type": "calculated", "source_facts": ["overpayment_applied_next_year"], "source_rules": ["R-MD511-SETTLE"], "sort_order": 31},
    {"line_number": "19", "description": "Amount of overpayment TO BE REFUNDED (Add lines 16 and 18, and subtract the total from line 15.)",
     "line_type": "total", "source_rules": ["R-MD511-SETTLE"], "sort_order": 32},
    {"line_number": "20a", "description": "Direct deposit — type of account / routing number (9 digits) / account number / name on the account",
     "line_type": "input", "sort_order": 33},
    # --- Worksheet 11A ---
    {"line_number": "W11A-A", "description": "Worksheet 11A A — Pass-through entity's taxable income (Form 511, line 2)",
     "line_type": "informational", "source_rules": ["R-MD511-DCF11A"], "sort_order": 700},
    {"line_number": "W11A-B", "description": "Worksheet 11A B — cash-method restatement", "line_type": "input",
     "source_facts": ["dcf_b_cash_method_restatement"], "sort_order": 701},
    {"line_number": "W11A-C", "description": "Worksheet 11A C — non-includable cash receipts", "line_type": "input",
     "source_facts": ["dcf_c_non_includable_receipts"], "sort_order": 702},
    {"line_number": "W11A-D", "description": "Worksheet 11A D — depreciation/amortization/depletion add-back", "line_type": "input",
     "source_facts": ["dcf_d_depreciation_addback"], "sort_order": 703},
    {"line_number": "W11A-E", "description": "Worksheet 11A E — decrease in liability reserve", "line_type": "input",
     "source_facts": ["dcf_e_liability_reserve_decrease"], "sort_order": 704},
    {"line_number": "W11A-F", "description": "Worksheet 11A F — Total. (Add lines B through E.)", "line_type": "subtotal",
     "source_rules": ["R-MD511-DCF11A"], "sort_order": 705,
     "notes": "⚠ W5(a): transcribed verbatim as B through E — line A is not in the total. Confirm at the walk."},
    {"line_number": "W11A-G", "description": "Worksheet 11A G — non-deductible cash expenditures", "line_type": "input",
     "source_facts": ["dcf_g_non_deductible_expenditures"], "sort_order": 706},
    {"line_number": "W11A-H", "description": "Worksheet 11A H — increase in liability reserve", "line_type": "input",
     "source_facts": ["dcf_h_liability_reserve_increase"], "sort_order": 707},
    {"line_number": "W11A-I", "description": "Worksheet 11A I — Distributable cash flow. (Add lines G and H, and subtract the total from line F.)",
     "line_type": "subtotal", "source_rules": ["R-MD511-DCF11A"], "sort_order": 708,
     "notes": "⚠ NO ownership multiplier follows — this IS the distributable cash flow. Worksheet 9A instead multiplies by lines 5 + 10."},
    {"line_number": "W11A-J", "description": "Worksheet 11A J — Members' tax previously paid. (All members' estimated tax paid with Forms 510/511D or 510/511E)",
     "line_type": "input", "source_facts": ["dcf_j_members_tax_previously_paid"], "sort_order": 709,
     "notes": "⚠ 9A's line J is the OWNERSHIP PERCENTAGE; 11A's line J is tax previously paid. Same letter, different meaning."},
    {"line_number": "W11A-K", "description": "Worksheet 11A K — Distributable cash flow limitation. (Subtract line J from line I. If less than 0, enter 0.)",
     "line_type": "total", "source_rules": ["R-MD511-DCF11A"], "sort_order": 710},
] + _schedule_a_lines(600, "R-MD511-APPORT") + PAGE3_LINES + [
    {"line_number": "SchB", "description": ("Schedule B Parts I-IV — identical to Form 510's apart from the printed form number. "
                                            "Per-member income share is a portion of LINE 2, page 1 — NOT line 4."),
     "line_type": "informational", "source_rules": ["R-MD511-SCHB"], "sort_order": 950},
    {"line_number": "K1-D2", "description": "Schedule K-1 Section D line 2 — Electing PTE tax paid by THIS PTE. CREDIT **AND** MANDATORY ADD-BACK.",
     "line_type": "calculated", "source_rules": ["R-MD511-K1D"], "sort_order": 960},
    {"line_number": "K1-D4", "description": "Schedule K-1 Section D line 4 — Electing PTE tax paid by OTHER PTEs. CREDIT **AND** MANDATORY ADD-BACK.",
     "line_type": "calculated", "source_rules": ["R-MD511-K1D"], "sort_order": 961},
    {"line_number": "K1-addback", "description": "Typed member add-back modification = K-1 Section D lines 2 + 4 ONLY (never line 1)",
     "line_type": "calculated", "source_rules": ["R-MD511-K1D"], "sort_order": 962,
     "notes": "Form 502 Other Additions code 'r' (individuals); §10-306(b)(6) -> §10-205(m) (corporations); Form 504 line 1 (trusts)."},
    {"line_number": "K1-H", "description": "Schedule K-1 Section H — capital-gain reporting; column 2 = column 1 x the Maryland apportionment factor",
     "line_type": "calculated", "source_rules": ["R-MD511-K1H"], "sort_order": 963},
]

MD511_DIAGNOSTICS: list[dict] = [
    # ---- The election state machine (W1) ----
    {"diagnostic_id": "D_MD511_ELECTION_UNDETERMINED", "severity": "error",
     "title": "The 510-vs-511 election cannot be determined — it is NOT on this return",
     "condition": "election_first_filing_kind = 'unknown', or election_recorded_form = 'undetermined'",
     "message": ("Maryland's Form 510 and Form 511 are MUTUALLY EXCLUSIVE and the choice was made on the FIRST filing "
                 "of the tax year (Form 510/511D or Form 510/511E), months before this return. Nothing on the "
                 "year-end return's own data reveals which applies. Retrieve the first filing and record which box "
                 "was checked: Box A requires Form 511; Box B requires Form 510. If no 510/511D or 510/511E was "
                 "filed, filing Form 511 IS an irrevocable election to be taxed at the entity level. Do not proceed "
                 "on an assumption — the error cannot be cured on an amended return."),
     "notes": "W1. The spec never infers the election from computed values."},
    {"diagnostic_id": "D_MD511_WRONG_FORM_FILE_510", "severity": "error",
     "title": "The recorded election is Box B — file Form 510, not Form 511",
     "condition": "election_recorded_form = MD_510 while Form 511 is being prepared",
     "message": ("Booklet 511: 'If you did not check the box on Form 510/511D or Form 510/511E, you did not make the "
                 "election, and you must file Form 510.' Filing Form 511 without the election taxes resident members "
                 "who are not subject to the tax. The election is irrevocable for the tax year."),
     "notes": "W1 hard block."},
    {"diagnostic_id": "D_MD511_DEEMED_BOTH_BOXES", "severity": "warning",
     "title": "DEEMED election — both boxes were checked in error, so Form 511 is required",
     "condition": "first filing had BOTH Box A and Box B checked",
     "message": ("Form 510/511E instructions, verbatim: 'If this is your first filing and both boxes are checked in "
                 "error, the Comptroller will deem you have elected to pay tax at the entity level with respect to "
                 "all members' shares, and that decision will be irrevocable.' Form 511 is the required year-end "
                 "return, and every member — resident included — is inside the tax. Confirm the client understands "
                 "the consequence; it cannot be undone this tax year."),
     "notes": "W1 deeming default #2."},
    {"diagnostic_id": "D_MD511_YEAR_END_IS_ELECTION", "severity": "warning",
     "title": "No 510/511D or 510/511E was filed — filing this return IS the irrevocable election",
     "condition": "election_first_filing_kind = 'year_end_return'",
     "message": ("Booklet 511: 'If you did not file Form 510/511D or Form 510/511E, filing Form 511 is an irrevocable "
                 "election to be taxed at the entity level for tax year 2025. You may not change this election on an "
                 "amended return.' Confirm the entity-level election is intended before transmitting — the mirror "
                 "rule applies to Form 510 (Booklet 510 Instruction 1: filing the 510 'will be deemed to be an "
                 "irrevocable decision to pay tax only on behalf of nonresident members')."),
     "notes": "W1."},
    {"diagnostic_id": "D_MD511_AMENDED_ELECTION_BAR", "severity": "error",
     "title": "An amended return may not change the election or non-election",
     "condition": "is_amended_return and the amended return would change the recorded election",
     "message": ("Booklet 510 Instruction 8: 'A PTE may not file an amended return to change the PTE's election or "
                 "non-election for the tax year.' Technical Bulletin 6: 'A nonelection may not be changed to an "
                 "election on an amended return.' Amend the figures, not the election."),
     "notes": "W1."},
    # ---- Member classification (W6) ----
    {"diagnostic_id": "D_MD511_RESIDENT_ENTITY_1C", "severity": "warning",
     "title": "A RESIDENT entity member moves to line 1c on Form 511 and IS taxed at 8.25%",
     "condition": "a member is an entity formed under, or registered with SDAT to do business in, Maryland",
     "message": ("⚠ THE SAME MEMBER LANDS IN A DIFFERENT BOX. Form 511 line 1c reads 'Nonresident AND RESIDENT "
                 "entities' and feeds line 5b at 8.25%; Form 510 line 1c is nonresident entities only, and a resident "
                 "entity there sits in line 1d 'Others' and is UNTAXED. Booklet 511 confirms it by omission — its "
                 "'Others' instruction covers only IRC §408(e)/§501 entities, dropping the resident entities the "
                 "Booklet 510 version includes. Do not carry a Form 510 member classification onto a Form 511."),
     "notes": "W6 — the most consequential line-for-line difference between the two returns."},
    {"diagnostic_id": "D_MD511_RESIDENT_INDIVIDUAL_TAXED", "severity": "info",
     "title": "Resident individual and fiduciary members ARE inside the Form 511 tax",
     "condition": "count_1a_resident_individuals > 0",
     "message": ("Line 5a is 'Percentage of ownership by individual members shown on lines 1a AND 1b' — resident and "
                 "nonresident alike — taxed at 8.75% on line 7. On Form 510 the same resident member is counted at "
                 "line 1a and taxed at nothing. For TY2025 the apportioned line-4 base applies to resident and "
                 "nonresident members alike; the statute and the form AGREE (TB 6 §I.A/§I.B; Tax Alert eff. "
                 "4/13/2026). Build the form exactly as printed."),
     "notes": "Former walk item W3 WITHDRAWN as a false conflict — do not re-raise it."},
    {"diagnostic_id": "D_MD511_FIDUCIARY_IN_IND_LEG", "severity": "info",
     "title": "Fiduciary members belong in the INDIVIDUAL legs (1a/1b), never the entity legs",
     "condition": "the PTE has fiduciary (trust/estate) members",
     "message": ("Lines 1a and 1b read 'Individual (including fiduciary)', and both booklets state 'the term "
                 "individual includes fiduciaries, unless specifically excepted.' A fiduciary member is taxed at "
                 "8.75% through line 5a, not at the 8.25% entity rate through line 5b."),
     "notes": "W6."},
    {"diagnostic_id": "D_MD511_EXEMPT_MEMBER_U6", "severity": "warning",
     "title": "REIT / IRC §408(e) / §501 member excluded — the ELECTING-leg footing is TB 6, not §10-102.1(f)",
     "condition": "a member is a REIT (§856), an IRA/Keogh/pension plan (§408(e)) or a §501 organization",
     "message": ("Booklet 511: 'The Electing PTE tax does not apply to a member that is a Real Estate Investment "
                 "Trust (REIT) or to a member that is tax-exempt under IRC Sections 408(e) or 501, unless the "
                 "tax-exempt member is subject to the federal income tax on its federal return on that share of "
                 "Electing PTE income.' ⚠ OPEN ITEM U6: §10-102.1(f) is scoped by its own words to the NON-ELECTING "
                 "leg, and §408(e) appears nowhere in §10-102.1. The footing is Technical Bulletin 6 §II.A (which "
                 "excludes them from the definition of 'member') plus TG §10-104. TB 6 is TY2023-keyed and §10-104 "
                 "has not been read — re-verify before seeding."),
     "notes": "U6 residual."},
    # ---- Base (line 2) ----
    {"diagnostic_id": "D_MD511_SALT_ADDBACK_REQUIRED", "severity": "warning",
     "title": "Line 2 requires the SALT add-back — the 511 base is NOT the 510 base",
     "condition": "line 2 is computed from the federal return",
     "message": ("Form 511 line 2 = the net of federal Form 1065 Schedule K lines 1-11 (or Form 1120-S Schedule K "
                 "lines 1-10), LESS interest from federal obligations, PLUS the federal deduction attributable to "
                 "taxes based on net income — 'including but not limited to' Form 1065 page-1 line 14 / Form 1120-S "
                 "page-1 line 12 ('Taxes and licenses'). Taxes with a basis other than net income (gross receipts, "
                 "commercial activity) are NOT added back. Form 510 line 2 has NO such add-back."),
     "notes": "Federal line numbers verified on the FINAL 2025 IRS forms."},
    {"diagnostic_id": "D_MD511_PRIOR_REFUND_ADJUST", "severity": "warning",
     "title": "The SALT add-back is net of the prior-year Maryland refund — this is MULTI-YEAR state",
     "condition": "prior_year_md_refund_in_federal_income > 0",
     "message": ("Booklet 511: 'In calculating PTE taxable income, the disregarded deduction is adjusted for income "
                 "on the federal return attributable to a refund of overpayment of the previous year's estimated "
                 "taxes.' Worked example: Year 1 SALT $10,000 on federal income $75,000 gives Maryland PTE taxable "
                 "income $85,000, liability $6,800 and a $3,200 refund. In Year 2, with SALT $10,000 and federal "
                 "income $78,200 (including the $3,200 refund), the disregarded deduction is adjusted to $6,800, "
                 "returning PTE taxable income to $85,000. THE ADD-BACK IS THE TAX ACTUALLY BORNE, NOT THE CASH "
                 "PAID. Nothing on the federal return produces this figure."),
     "notes": "Multi-year state; the federal handoff is lossy here."},
    {"diagnostic_id": "D_MD511_TY2027_BASE_CHANGE", "severity": "info",
     "title": "CALENDARED — the Form 511 base changes for TY2027, not for TY2025 or TY2026",
     "condition": "preparing a Form 511 for a tax year after 2026",
     "message": ("The Budget Reconciliation and Financing Act of 2025 (2025 Md. Laws Ch. 604) rewrote "
                 "§10-102.1(a)(8) to split the base — residents' income from everywhere, nonresidents' Maryland "
                 "income — and the 2026 BRFA (2026 Md. Laws Ch. 6 §4) POSTPONED it to TY2027. For TY2025 and TY2026 "
                 "the tax is imposed on 'resident and nonresident shares attributable to Maryland only, as it was in "
                 "tax year 2025' (Tax Alert eff. 4/13/2026). MD_511 lines 2-4 are a dated future re-spec, and the "
                 "2026 BRFA also promises electing PTEs options for calculating the tax for TY2027. ⚠ mgaleg serves "
                 "CURRENT code — every Maryland statute cite must carry its chapter law and effective tax year."),
     "notes": "The standing statute-vintage convention that replaced the withdrawn W3."},
    # ---- Apportionment (W9 / U11) ----
    {"diagnostic_id": "D_MD511_APPORT_ZERO_FLOOR", "severity": "info",
     "title": "A zero apportionment factor is entered as .000001 — never dropped",
     "condition": "the computed Schedule A factor rounds to zero, or the receipts denominator is zero",
     "message": ("Form 511 line 3b and Schedule A line 4, verbatim: '(If factor is zero, enter .000001)'. COMAR "
                 "03.04.03.08 B(5) requires an apportionment factor even on a loss return 'for the filing to be "
                 "considered complete'. The convention appears ONLY on the form faces — it is in neither booklet."),
     "notes": "W9."},
    {"diagnostic_id": "D_MD511_NO_FACTOR_REWEIGHT", "severity": "error",
     "title": "Maryland has NO insignificant-denominator rule — never reweight or drop a factor",
     "condition": "any attempt to eliminate, reweight or substitute an apportionment factor",
     "message": ("Maryland has NO rule dropping or reweighting a factor whose denominator is zero or 'insignificant'. "
                 "That rule is Fla. Stat. §220.15(1) and it does NOT apply here — verified absent across Tax-General "
                 "§§10-401/10-402, COMAR 03.04.03.08/.09/.10, Administrative Release 43, the Corporate Booklet and "
                 "both PTE Booklets, and re-tested against 'de minimis', 'omit', 'eliminat', 'disregard', 'not "
                 "material' and 'nominal'. Maryland's convention is the opposite: a zero factor is floored at "
                 ".000001. Altering a formula — including 'the weight of any factor' — is reserved to THE COMPTROLLER "
                 "(§10-402(e); §10-401(2)). Neither the preparer nor this software may do it."),
     "notes": "W9 / U11. The load-bearing negative."},
    # ---- DCF (W5) ----
    {"diagnostic_id": "D_MD511_DCF_CONDITIONAL", "severity": "warning",
     "title": "Line 12 is a CONDITIONAL lesser-of — not an unconditional MIN()",
     "condition": "line 11 is blank or the distributable-cash-flow worksheet checkbox is unchecked",
     "message": ("If the distributable cash flow limitation is not used, enter the amount shown on line 10; if it is "
                 "used, enter the lesser of line 10 or line 11. AN UNCONDITIONAL MIN() ZEROES THE TAX whenever line "
                 "11 is blank. Also: 'Election of the distributable cash flow limitation will not reduce the tax "
                 "liability of the members.'"),
     "notes": "W5."},
    {"diagnostic_id": "D_MD511_DCF_NO_OWNERSHIP_STEP", "severity": "info",
     "title": "Worksheet 11A has NO ownership-percentage step — do not clone worksheet 9A",
     "condition": "the distributable-cash-flow worksheet is used on Form 511",
     "message": ("Worksheet 11A runs A-K: line I IS the distributable cash flow, and line J is ALL MEMBERS' tax "
                 "previously paid with Forms 510/511D or 510/511E. Form 510's worksheet 9A runs A-M and multiplies "
                 "line I by line J, where J is the sum of the nonresident ownership percentages from Form 510 lines 5 "
                 "and 10. THE LETTER J MEANS DIFFERENT THINGS ON THE TWO WORKSHEETS. Cloning one into the other "
                 "over-caps or under-caps every DCF return."),
     "notes": "W5."},
    {"diagnostic_id": "D_MD511_DCF_AMENDED_U7", "severity": "info",
     "title": "No source bars electing the DCF limitation on an amended return (U7)",
     "condition": "the DCF limitation is elected on an amended return",
     "message": ("md_conformity.md §4 asserts the DCF cap 'cannot be elected on an amended return'. NO such statement "
                 "appears in the FINAL TY2025 Booklets 510 or 511, on either form face, in §10-102.1(d)(3), or in "
                 "Technical Bulletin 6 — whose only amended-return sentence is the ELECTION bar. The claim is "
                 "unsupported and is NOT encoded as a rule. Ken to rule before this is enforced."),
     "notes": "U7 / W5(b)."},
    # ---- Owner side (W4) ----
    {"diagnostic_id": "D_MD511_ADDBACK_D2_D4_ONLY", "severity": "error",
     "title": "The member add-back attaches to K-1 Section D lines 2 and 4 ONLY — never line 1",
     "condition": "Schedule K-1 Section D line 2 or line 4 has an amount",
     "message": ("⚠ THE OWNER SIDE IS TWO LEGS AND BOTH ARE REQUIRED. Leg 1 — the §10-701.1 CREDIT, routed by K-1 "
                 "Section D line 5 to Form 502CR Part CC line 9 (individuals), Form 500CR (corporations), Form 504 "
                 "(fiduciaries) and Form 511 line 13c (PTE members). Leg 2 — the MANDATORY ADD-BACK, on the K-1 form "
                 "face: 'Members with entries on Lines 2 and 4 are required to addback the amount of the credit total "
                 "on Line 2 and 4 on their respective returns.' Individuals use Form 502 Other Additions code 'r'; "
                 "corporate members via §10-306(b)(6) -> §10-205(m); trusts add D2 + D4 to federal taxable income on "
                 "Form 504 line 1. IMPLEMENTING ONLY THE CREDIT OVERSTATES OWNER RELIEF BY THE FULL PTET. And the "
                 "add-back NEVER attaches to line D1 — under §10-102.1(c)(1) the non-electing tax is already the "
                 "member's own tax paid on their behalf, so adding back D1 double-taxes every nonresident partner."),
     "notes": "W4. The classic Maryland PTET bug, in both directions."},
    {"diagnostic_id": "D_MD511_ADDBACK_NOT_IN_SEC_B", "severity": "warning",
     "title": "Do NOT pre-load the electing-PTE add-back into K-1 Section B additions",
     "condition": "k1_section_b_additions is populated on an electing PTE's K-1",
     "message": ("K-1 Section B instruction, verbatim: 'For electing PTEs, do not include in additions the member's "
                 "addback of the electing PTE credit. The electing PTE credit is added back on the member's return.' "
                 "The add-back is the MEMBER's obligation, emitted as a typed modification on the K-1 — not an "
                 "entity-level Section B addition. Pre-loading it double-counts."),
     "notes": "W4."},
    # ---- Composite bar + errata ----
    {"diagnostic_id": "D_MD511_NO_COMPOSITE_510C", "severity": "error",
     "title": "An Electing PTE may NOT file Form 510C — and the form face contradicts itself here",
     "condition": "composite_510c_attempted",
     "message": ("Booklet 511: 'An Electing PTE is not permitted to file a composite Maryland income tax return Form "
                 "510C.' There is no '510C Filed' checkbox on Form 511. ⚠ ERRATUM: the NOTE printed under Form 511 "
                 "line 17 nonetheless says 'The total tax paid on line 12 is to be reported either on the composite "
                 "return or on the returns of members.' THE FORM CONTRADICTS ITSELF. Build to the booklet's bar and "
                 "to the absent checkbox; the erratum is recorded, not fixed."),
     "notes": "W11(e) / R1."},
    {"diagnostic_id": "D_MD511_INVEST_PTNSHP_ERRATUM", "severity": "info",
     "title": "Form 511's line-4 investment-partnership cross-reference points nowhere",
     "condition": "is_investment_partnership on a Form 511",
     "message": ("The Form 511 line-4 NOTE says '(Investment partnerships see Specific Instructions)', but PTE "
                 "Booklet 511 contains NO investment-partnership instruction and never mentions code 705 — the rule "
                 "exists only in Booklet 510 Instruction 9 NOTE 2 and Technical Bulletin 6 §II.B. A 511 filer "
                 "following the form face has nowhere to go. Do not infer 510-style relief onto the electing tax; "
                 "escalate instead."),
     "notes": "W11(f)."},
    {"diagnostic_id": "D_MD511_AMEND_LINE_ERRATUM_U5", "severity": "info",
     "title": "Booklet erratum — amended payments go on line 13e, not line 13d",
     "condition": "is_amended_return",
     "message": ("Booklet 511 Instruction 8 says to 'include the amount paid on line 13d of Form 511'. Line 13d is the "
                 "MW506NRS line; the amended-return line is 13e. The form face and the per-line instructions both say "
                 "13e. Build to the face."),
     "notes": "U5 / W11(b)."},
    {"diagnostic_id": "D_MD511_TB38_ERRATUM_U10", "severity": "info",
     "title": "Form 500DM cites a nonexistent 'Technical Bulletin No. 38'",
     "condition": "following Form 500DM's cross-references",
     "message": ("Form 500DM cites 'Technical Bulletin No. 38' three times — on the form face, under Additional "
                 "Information, and at line 8. NO such document exists. The document is ADMINISTRATIVE RELEASE No. 38, "
                 "'Decoupling from Federal Income Tax Laws'. Recorded so nobody 'corrects' the spec back to TB 38."),
     "notes": "U10 / W11(d)."},
    # ---- Structural / informational ----
    {"diagnostic_id": "D_MD511_PCT_9999_CONVENTION", "severity": "info",
     "title": "On Form 511, 100% ownership is entered as 9999 — NOT left blank",
     "condition": "line 5a or 5b represents 100% ownership",
     "message": ("Booklet 511 lines 5a/5b: the percentage is 'expressed as a decimal. If 100%, enter 9999.' The Form "
                 "511 face carries no 100% instruction at all. ⚠ Form 510 lines 5 and 10 use the OPPOSITE convention "
                 "— 'If 100%, leave blank and enter the amount from line 4 on line 6.' A shared component that "
                 "normalises 100% one way will mis-enter one of the two returns."),
     "notes": "Verification finding §15.4 item 3."},
    {"diagnostic_id": "D_MD511_SCHB_OFF_LINE2", "severity": "warning",
     "title": "Schedule B per-member shares run off LINE 2, not line 4",
     "condition": "Schedule B Parts I-IV are populated",
     "message": ("Both booklets: the per-member share of income is 'a portion of the amount on line 2, page 1.' "
                 "Schedule B therefore reports the FEDERAL/ENTITY-LEVEL share while the tax lines run off the "
                 "APPORTIONED line 4. Do not wire Schedule B off line 4."),
     "notes": "Structural trap."},
    {"diagnostic_id": "D_MD511_EFILE_MANDATE", "severity": "warning",
     "title": "Conditional e-file mandate — credits from Form 500CR or 502S force electronic filing",
     "condition": "k1_section_e_credits_present or a Form 500CR / 502S credit is passed through",
     "message": ("Printed in the margin of every Schedule B page: 'You must file Form 511 electronically to pass on "
                 "business tax credits from Form 500CR and/or Form 502S to your members.' The mandate is conditional "
                 "on credits, not on size. Form 500CRW is the hardship waiver. ⚠ Maryland approval is PER FORM on the "
                 "BUSINESS MeF track and the software must prevent e-filing any form Maryland has not approved (U1)."),
     "notes": "U1."},
    {"diagnostic_id": "D_MD511_Q8_NOT_MFG_CARVEOUT", "severity": "info",
     "title": "Page-3 Q8 is the APPORTIONMENT manufacturing rule — NOT the depreciation carve-out",
     "condition": "page-3 question 8 is answered",
     "message": ("'Is this entity a multistate manufacturing corporation with more than 25 employees?' is COMAR "
                 "03.04.03.10 language — NAICS 1997 Edition, sectors 11/31/32/33, extra exclusions for affiliated "
                 "corporations and service providers, and a >25-employee report that EXPIRED for tax years beginning "
                 "on or after 1/1/2011. The §10-210.1 depreciation carve-out is a DIFFERENT rule: NAICS 2012 Edition, "
                 "Sectors 31/32/33, 'manufacturing entity', no employee test. NEVER wire question 8 to the "
                 "depreciation carve-out. Informational direct-entry only (U8)."),
     "notes": "U8 / W2."},
    {"diagnostic_id": "D_MD511_CODE_NUMBERS_U12", "severity": "info",
     "title": "Only three Form 510/511 code numbers exist in the TY2025 corpus",
     "condition": "a page-3 CODE NUMBER is entered",
     "message": ("The form prints two three-digit code blocks with no legend, and no published master list exists. "
                 "The only codes appearing anywhere in the TY2025 PTE sources are 704 (publicly traded pass-through "
                 "entity), 705 (investment partnership — Booklet 510 only) and 301 (Form 500UP annualization). "
                 "Anything else is free entry, unverified."),
     "notes": "U12."},
    {"diagnostic_id": "D_MD511_K1H_NO_TAX_LINE", "severity": "warning",
     "title": "Schedule K-1 Section H is mandatory for TY2025 and has NO tax line on this return",
     "condition": "the PTE has capital gain income allocable to any member",
     "message": ("New for TY2025: 'the PTE must provide additional information on capital gain income passed through "
                 "to members.' The PTE computes NO capital-gain surtax at entity level (TB 58 — the PTET rate is "
                 "statutory and excludes the 2%) but MUST report all seven Section H rows so members can complete "
                 "Form 502CG or 504CG, and should advise members to make additional estimated payments. Column 2 = "
                 "column 1 x the Maryland apportionment factor; row 3 is resident-members-only. Nothing on either "
                 "return face references Section H."),
     "notes": "W7."},
    {"diagnostic_id": "D_MD511_K1H_408_ERRATUM", "severity": "info",
     "title": "K-1 erratum — '§458 / §458A' should read IRC §408 / §408A",
     "condition": "reading the Schedule K-1 Section H line 3 instruction",
     "message": ("The K-1 Section H line-3 instruction cites 'IRC § 458' and 'IRC § 458A'. The correct citations are "
                 "IRC §408 and §408A, as Technical Bulletin 58 has them — the same misprint the conformity brief "
                 "found on Form 502CG line 3. Encode against the statute and TB 58; recorded so a future reader does "
                 "not 'fix' it back."),
     "notes": "W7."},
    # ---- RED-DEFERS that apply on the 511 ----
    {"diagnostic_id": "D_MD511_R2_SPECIAL_APPORT", "severity": "error",
     "title": "R2 — Special Apportionment Formula is not computed",
     "condition": "the entity is a rental/leasing company, financial institution, transportation company or worldwide headquartered company",
     "message": ("Rental/leasing companies, financial institutions, transportation companies and worldwide "
                 "headquartered companies must use a Special Apportionment Formula unless the Comptroller has "
                 "accepted an Alternative Apportionment Formula. This product does not compute one. Enter the factor "
                 "on Schedule A line 4 and check the disclosure box."),
     "notes": "R2."},
    {"diagnostic_id": "D_MD511_R3_ALTERNATIVE_APPORT", "severity": "error",
     "title": "R3 — an Alternative Apportionment Formula requires the Comptroller's prior acceptance",
     "condition": "scha_special_or_alternative_checked with an entity-supplied factor",
     "message": ("An Alternative Apportionment Formula requires the Comptroller's prior acceptance (Tax-General "
                 "§10-402(e); §10-401(2)). This product does not compute one and will never derive one. Enter the "
                 "accepted factor on Schedule A line 4, check the disclosure box, and retain the acceptance. The "
                 "checkbox is a DISCLOSURE of a formula already accepted — not a self-election."),
     "notes": "R3 / W9."},
    {"diagnostic_id": "D_MD511_R4_500CR_502S", "severity": "error",
     "title": "R4 — Form 500CR business credits and Form 502S are not computed",
     "condition": "k1_section_e_credits_present",
     "message": ("Schedule K-1 Section E carries 26 NAMED credits across lines 1-28 (lines 13 and 23 print RESERVED). "
                 "Form 500CR and the Form 502S Maryland Historic Revitalization Tax Credit are not computed in v1 — "
                 "prepare them manually. ⚠ Passing any of these credits to members REQUIRES electronic filing."),
     "notes": "R4."},
    {"diagnostic_id": "D_MD511_R5_ONE_MARYLAND", "severity": "error",
     "title": "R5 — the One Maryland Economic Development Tax Credit is not computed",
     "condition": "k1_one_maryland_used",
     "message": ("The One Maryland Economic Development Tax Credit occupies its own Schedule K-1 blocks (lines "
                 "29a-32 and 33a-39, two vintages) and its own Form 500CR Parts P-I / P-II regime. Not computed in "
                 "v1 — prepare Form 500CR manually."),
     "notes": "R5."},
    {"diagnostic_id": "D_MD511_R6_SCORP_FORM_500", "severity": "error",
     "title": "R6 — this S corporation owes Maryland corporation income tax: Form 500 as well",
     "condition": "entity_type_checkbox = s_corporation and (f1120s_line_23a > 0 or f1120s_line_23b > 0)",
     "message": ("An S corporation subject to federal corporation income tax (excess net passive income, built-in "
                 "gains) is also subject to Maryland corporation income tax and must file Form 500 — total taxable "
                 "income on line 1, box 'Other' checked with '1120S' entered. Form 500 is not computed in v1. ⚠ THE "
                 "BOOKLETS ADDRESS ONLY THE FORM 510 CASE and are silent on an ELECTING S corp filing Form 500 plus "
                 "Form 511. Treat that combination as a diagnostic, not a settled rule, and escalate (W10)."),
     "notes": "R6 / W10."},
    {"diagnostic_id": "D_MD511_R7_FORM_500UP", "severity": "error",
     "title": "R7 — Form 500UP underpayment interest and penalty is not computed",
     "condition": "interest_penalty_500up_16 entered, or estimates fall short of the 90%/110% safe harbour",
     "message": ("Estimated tax is required when the tax is expected to exceed $1,000; the safe harbour is 90% of the "
                 "current year or 110% of the prior year. Installments: the 15th day of the 4th, 6th, 9th and 12th "
                 "months for S corporations; the 4th, 6th, 9th and 13th for partnerships, LLCs and business trusts. "
                 "A short period under 4 months owes no estimated tax and files no 510/511D. Form 500UP is not "
                 "computed in v1. 'S corporations may not use the annualization method on Form 500UP'; annualizing "
                 "partnerships and LLCs enter code 301. Interest runs at 10.8133% annually / 0.9011% per month."),
     "notes": "R7."},
    {"diagnostic_id": "D_MD511_R8_MW506NRS", "severity": "error",
     "title": "R8 — Form MW506NRS nonresident real-property withholding is not computed",
     "condition": "pay_13d_mw506nrs entered or k1_section_f_mw506nrs used",
     "message": ("Form MW506NRS (withholding on the nonresident sale of Maryland real property) is not prepared in "
                 "v1. Enter the payment on line 13d and flow each member's share through Schedule K-1 Section F. The "
                 "return must carry the federal return, the HUD-1 and the MW506NRS as attachments."),
     "notes": "R8."},
    {"diagnostic_id": "D_MD511_R9_FORM_500DM", "severity": "error",
     "title": "R9 — Form 500DM must be ATTACHED, but the PTE computes no adjustment on this return",
     "condition": "has_decoupling_modification",
     "message": ("Form 500DM instructions: 'If the entity is a PTE ... no adjustment is made on the PTE's Maryland "
                 "income tax return (Form 510 or 511). However, Form 500DM must be submitted with Form 510 or 511 and "
                 "the PTE must provide each partner, shareholder or member a statement showing their share of each "
                 "decoupling modification with the appropriate code(s).' This is a PRO FORMA FEDERAL RETURN regime, "
                 "not a percentage add-back. Maryland §179 is frozen at $25,000 / $200,000 — NOT the federal OBBBA "
                 "$2,500,000 / $4,000,000 and NOT Georgia's. Pass each member's share through Schedule K-1 Section I "
                 "with the codes; the member reports it on their own Form 500DM line 9."),
     "notes": "R9."},
    {"diagnostic_id": "D_MD511_R10_MFG_CARVEOUT", "severity": "error",
     "title": "R10 — the §10-210.1 manufacturing carve-out has NO Maryland form line anywhere",
     "condition": "naics_31_33_manufacturing_entity is set AND any asset was placed in service on or after 1/1/2019",
     "message": ("Tax-General §10-210.1(b)(1)(ii) and (b)(3)(ii): the §168(k) bonus and §179 add-backs 'do not apply "
                 "to property placed in service by a manufacturing entity on or after January 1, 2019.' "
                 "§10-210.1(a)(4): a 'manufacturing entity' is primarily engaged in activities that, under the NAICS "
                 "United States Manual 2012 EDITION, fall in SECTOR 31, 32 or 33, excluding a refiner as defined in "
                 "Business Regulation §10-101. §10-310 extends this to corporations. ⚠ THIS CARVE-OUT APPEARS ON NO "
                 "TY2025 MARYLAND PTE FORM OR INSTRUCTION — it must be built from the statute alone and there is NO "
                 "printed cross-check anywhere in this module. It is NOT the page-3 question 8 rule. And it does NOT "
                 "reach §10-210.1(b)(5) heavy-duty SUVs, which remain subject to the §280F limits for all taxpayers "
                 "including manufacturing entities. Not applied in v1 — flag for review."),
     "notes": "R10 / W2. ⚠ This wording is the ONLY place the carve-out lives in the product — Ken-approved wording required."},
    {"diagnostic_id": "D_MD511_R11_TIERED_PTE", "severity": "error",
     "title": "R11 — tiered-PTE credit chains beyond one level are not computed",
     "condition": "upstream_pte_k1_count > 1",
     "message": ("More than one upstream Maryland Schedule K-1 (510/511) is present. Credit chains through more than "
                 "one level of pass-through entity (Form 511 line 13c, K-1 Section D line 4) are not computed in v1 "
                 "— verify each level manually, and remember the D2/D4 add-back travels with every level."),
     "notes": "R11."},
    {"diagnostic_id": "D_MD511_R12_PTP_SHOULD_NOT_FILE", "severity": "error",
     "title": "R12 — a publicly traded pass-through entity should NOT file Form 511",
     "condition": "is_publicly_traded_pte",
     "message": ("A publicly traded pass-through entity that files the annual information return for members "
                 "receiving more than $500 is outside the tax under §10-102.1(j), and the booklets state it 'should "
                 "not file Form 511'. Enter code number 704 on Form 510 instead. Verify the information-return "
                 "condition before relying on the exemption."),
     "notes": "R12."},
    {"diagnostic_id": "D_MD511_R15_501_PTE_FTI", "severity": "error",
     "title": "R15 — a §501-exempt PTE with federal taxable income must still file",
     "condition": "is_501_pte_with_fti",
     "message": ("'A PTE that qualifies for a IRC § 501 exemption and is treated as an association under 26 CFR § "
                 "301.7701-3(c)(1)(v)(A) and which has federal taxable income must file Form 510 or Form 511.' The "
                 "unrelated-business-income computation is not handled in v1 — prepare manually."),
     "notes": "R15."},
]

MD511_SCENARIOS: list[dict] = [
    {"scenario_name": "511 election — Box A on the 510/511D requires Form 511", "scenario_type": "normal", "sort_order": 1,
     "inputs": {"election_first_filing_kind": "510_511D", "election_box_a_checked": True, "election_box_b_checked": False},
     "expected_outputs": {"required_year_end_form": FORM_511, "irrevocable": True, "deemed": False},
     "notes": "Box A = elect to pay tax at the entity level on ALL members' shares -> Form 511 as the year-end return."},
    {"scenario_name": "511 deeming default — BOTH boxes checked in error", "scenario_type": "edge", "sort_order": 2,
     "inputs": {"election_first_filing_kind": "510_511E", "election_box_a_checked": True, "election_box_b_checked": True},
     "expected_outputs": {"required_year_end_form": FORM_511, "irrevocable": True, "deemed": True},
     "notes": "'the Comptroller will deem you have elected to pay tax at the entity level ... and that decision will be irrevocable.'"},
    {"scenario_name": "511 year-end return IS the election when no D or E was filed", "scenario_type": "edge", "sort_order": 3,
     "inputs": {"election_first_filing_kind": "year_end_return", "year_end_form": FORM_511},
     "expected_outputs": {"required_year_end_form": FORM_511, "irrevocable": True, "deemed": True},
     "notes": "'filing Form 511 is an irrevocable election to be taxed at the entity level for tax year 2025.'"},
    {"scenario_name": "511 electing tax — 8.75% individuals and 8.25% entities", "scenario_type": "normal", "sort_order": 4,
     "inputs": {"4": 1000000, "pct_individual_members_l5a": 0.70, "pct_entity_members_l5b": 0.30},
     "expected_outputs": {"5c": 1.0, "6": 700000.0, "7": 61250.0, "8": 300000.0, "9": 24750.0, "10": 86000.0},
     "notes": "L6 = 700,000; L7 = 700,000 x .0875 = 61,250 (ONE multiplier). L8 = 300,000; L9 = 300,000 x .0825 = 24,750. L10 = 86,000."},
    {"scenario_name": "511 the 9999 sentinel means 100% ownership", "scenario_type": "edge", "sort_order": 5,
     "inputs": {"4": 400000, "pct_individual_members_l5a": 9999, "pct_entity_members_l5b": 0},
     "expected_outputs": {"5a": 1.0, "6": 400000.0, "7": 35000.0, "10": 35000.0},
     "notes": "'expressed as a decimal. If 100%, enter 9999.' ⚠ Form 510 uses BLANK for 100% — the conventions differ."},
    {"scenario_name": "511 resident entity member IS taxed at 8.25% (line 1c)", "scenario_type": "edge", "sort_order": 6,
     "inputs": {"member_kind": "entity", "is_resident": True, "maryland_share": 100000},
     "expected_outputs": {"line": "1c", "taxed": True, "tax": 8250.0},
     "notes": "⚠ W6. THE SAME MEMBER on Form 510 sits at line 1d 'Others' and pays 0. Same member, different box, different tax."},
    {"scenario_name": "511 resident individual member IS taxed at 8.75% (line 1a)", "scenario_type": "edge", "sort_order": 7,
     "inputs": {"member_kind": "individual", "is_resident": True, "maryland_share": 200000},
     "expected_outputs": {"line": "1a", "taxed": True, "tax": 17500.0},
     "notes": "On Form 510 the same resident individual is counted at 1a and taxed at 0. TY2025 base is Maryland-source for all members."},
    {"scenario_name": "511 worksheet 11A has NO ownership multiplier", "scenario_type": "normal", "sort_order": 8,
     "inputs": {"dcf_b_cash_method_restatement": 400000, "dcf_c_non_includable_receipts": 100000,
                "dcf_d_depreciation_addback": 150000, "dcf_e_liability_reserve_decrease": 50000,
                "dcf_g_non_deductible_expenditures": 200000, "dcf_h_liability_reserve_increase": 0,
                "dcf_j_members_tax_previously_paid": 10000},
     "expected_outputs": {"W11A-F": 700000.0, "W11A-I": 500000.0, "W11A-K": 490000.0},
     "notes": "F = 700,000; I = 500,000; K = 500,000 − 10,000 = 490,000. ⚠ Worksheet 9A on the SAME inputs at 65% nonresident ownership gives 315,000 — the worksheets are not interchangeable."},
    {"scenario_name": "511 line 12 is line 10 when the DCF box is unchecked", "scenario_type": "failure", "sort_order": 9,
     "inputs": {"10": 86000, "11": None, "dcf_worksheet_used": False},
     "expected_outputs": {"12": 86000.0},
     "notes": "⚠ An unconditional MIN(L10, L11) would produce 0 here and zero out the tax. The lesser-of is CONDITIONAL on the checkbox."},
    {"scenario_name": "511 owner side — credit AND add-back, D2/D4 only", "scenario_type": "edge", "sort_order": 10,
     "inputs": {"k1_d1": 0, "k1_d2": 61250, "k1_d4": 5000},
     "expected_outputs": {"D5_credit_total": 66250.0, "addback": 66250.0, "d1_in_addback": False},
     "notes": "W4. Both legs required. With a D1 of 12,000 added to the same K-1 the credit becomes 78,250 but the ADD-BACK stays 66,250 — D1 is never added back."},
    {"scenario_name": "511 add-back excludes D1 even when all three are present", "scenario_type": "failure", "sort_order": 11,
     "inputs": {"k1_d1": 12000, "k1_d2": 61250, "k1_d4": 5000},
     "expected_outputs": {"D5_credit_total": 78250.0, "addback": 66250.0},
     "notes": "⚠ Adding back D1 would produce 78,250 and double-tax the nonresident member (§10-102.1(c)(1)). The add-back attaches to D2 and D4 ONLY."},
    {"scenario_name": "511 zero apportionment factor floors at .000001", "scenario_type": "edge", "sort_order": 12,
     "inputs": {"scha_1a_md": 0, "scha_1a_everywhere": 8000000},
     "expected_outputs": {"3b": 0.000001},
     "notes": "'(If factor is zero, enter .000001)'. NEVER dropped, NEVER reweighted — Maryland has no insignificant-denominator rule (that is Florida's)."},
    {"scenario_name": "511 line 2 SALT add-back net of the prior-year refund", "scenario_type": "normal", "sort_order": 13,
     "inputs": {"fed_1065_sch_k_lines_1_11": 78200, "salt_deduction_1065_l14_or_1120s_l12": 10000,
                "prior_year_md_refund_in_federal_income": 3200, "federal_obligations_interest": 0},
     "expected_outputs": {"2": 85000.0},
     "notes": "Booklet 511 worked example: the disregarded deduction is adjusted from 10,000 to 6,800 (the tax actually BORNE), so 78,200 + 6,800 = 85,000 — not 88,200."},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORMS registry + cross-form flow assertions
# ═══════════════════════════════════════════════════════════════════════════

FORMS: list[dict] = [
    {
        "identity": {
            "form_number": FORM_510,
            "form_title": "MD Form 510 — Maryland Pass-Through Entity Income Tax Return (non-electing, TY2025)",
            "notes": ("The NON-ELECTING Maryland PTE return. Mutually exclusive with MD_511: the choice was made on "
                      "the first filing of the tax year (Form 510/511D or 510/511E), is irrevocable, has two deeming "
                      "defaults, and is NOT derivable from this return's own data. Taxes ONLY nonresident individual "
                      "and fiduciary members (6.50% + 2.25%) and nonresident ENTITY members (8.25%); resident members "
                      "and resident entities are untaxed. Worksheet 9A scales distributable cash flow by the "
                      "nonresident ownership percentage; the line-15 lesser-of is conditional on the checkbox. K-1 "
                      "Section D line 1 is a credit with NO add-back."),
        },
        "facts": MD510_FACTS, "rules": MD510_RULES, "rule_links": MD510_RULE_LINKS,
        "lines": MD510_LINES, "diagnostics": MD510_DIAGNOSTICS, "scenarios": MD510_SCENARIOS,
    },
    {
        "identity": {
            "form_number": FORM_511,
            "form_title": "MD Form 511 — Maryland Pass-Through Entity Election Income Tax Return (electing PTE, TY2025)",
            "notes": ("The ELECTING Maryland PTE return (Maryland's PTET). Mutually exclusive with MD_510. Taxes ALL "
                      "members: 8.75% on individual and fiduciary members (resident AND nonresident) and 8.25% on "
                      "entity members (resident AND nonresident — line 1c reads 'Nonresident and resident entities'). "
                      "Line 2 adds back the federal deduction for taxes based on net income, net of the prior-year "
                      "Maryland refund (multi-year state). Worksheet 11A has NO ownership step. K-1 Section D lines 2 "
                      "and 4 carry a credit AND a mandatory member add-back. An Electing PTE may not file Form 510C. "
                      "⚠ TY2027 re-spec calendared for lines 2-4."),
        },
        "facts": MD511_FACTS, "rules": MD511_RULES, "rule_links": MD511_RULE_LINKS,
        "lines": MD511_LINES, "diagnostics": MD511_DIAGNOSTICS, "scenarios": MD511_SCENARIOS,
    },
]

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-MD-ELECT-XOR", "title": "MD_510 and MD_511 are mutually exclusive for a tax year",
     "assertion_type": "flow_assertion", "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 1,
     "description": ("Exactly one of Form 510 and Form 511 may be filed as the year-end return for a tax year. The "
                     "choice is set on the first filing (Form 510/511D or 510/511E), is irrevocable, and may not be "
                     "changed on an amended return. Filing the form that contradicts the recorded election is a hard "
                     "block, not a warning."),
     "definition": {"rules": ["R-MD510-ELECT", "R-MD511-ELECT"],
                    "check": "exactly_one_of(MD_510, MD_511) per (entity, tax_year); filing_form == recorded_election"}},
    {"assertion_id": "FA-MD-ELECT-DEEM", "title": "Both deeming defaults resolve to the correct form",
     "assertion_type": "flow_assertion", "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 2,
     "description": ("First filing with NEITHER box checked -> deemed Form 510, irrevocably. First filing with BOTH "
                     "boxes checked in error -> deemed Form 511, irrevocably. If no 510/511D or 510/511E was filed, "
                     "the year-end return itself IS the election."),
     "definition": {"rules": ["R-MD510-ELECT", "R-MD511-ELECT"],
                    "check": "neither_box -> MD_510 ; both_boxes -> MD_511 ; year_end_return -> that form, all irrevocable"}},
    {"assertion_id": "FA-MD-ELECT-INPUT", "title": "The election is a required INPUT, never inferred from return data",
     "assertion_type": "flow_assertion", "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 3,
     "description": ("Nothing on either year-end return's own data reveals which election applies. The spec takes the "
                     "recorded first-filing facts as required inputs and raises an ERROR diagnostic when they are "
                     "unknown; it must never derive the election from computed values such as which members are "
                     "present or which lines are populated."),
     "definition": {"rules": ["R-MD510-ELECT", "R-MD511-ELECT"],
                    "check": "election_first_filing_kind='unknown' -> form is None AND an error diagnostic fires"}},
    {"assertion_id": "FA-MD-MEMBER-BOX", "title": "The same member lands in different boxes on the two forms",
     "assertion_type": "reconciliation", "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 4,
     "description": ("A Maryland-RESIDENT ENTITY member sits on Form 510 line 1d ('Others') and is untaxed; on Form "
                     "511 it sits on line 1c ('Nonresident and resident entities') and is taxed at 8.25%. A resident "
                     "individual/fiduciary is untaxed on the 510 and taxed at 8.75% on the 511. Fiduciaries are "
                     "always inside the individual legs (1a/1b)."),
     "definition": {"rules": ["R-MD510-MEMBER", "R-MD511-MEMBER"],
                    "check": "tax(MD_510, entity, resident) == 0 AND tax(MD_511, entity, resident) == share * 0.0825"}},
    {"assertion_id": "FA-MD-SCHB-CROSS", "title": "Schedule B Parts I-IV cross-foot to lines 1a-1d, off LINE 2",
     "assertion_type": "reconciliation", "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 5,
     "description": ("Schedule B Parts I + II reconcile to lines 1a + 1b and Parts III + IV to lines 1c / 1d, on both "
                     "forms. The per-member income share is a portion of LINE 2, page 1 — not the apportioned line 4."),
     "definition": {"rules": ["R-MD510-SCHB", "R-MD511-SCHB"],
                    "check": "sum(SchB parts) == line 1e ; per-member share base == line 2"}},
    {"assertion_id": "FA-MD-DCF-SPLIT", "title": "The two DCF worksheets are NOT interchangeable",
     "assertion_type": "reconciliation", "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 6,
     "description": ("Worksheet 9A (Form 510) runs A-M and multiplies distributable cash flow by the nonresident "
                     "ownership percentage (lines J/K). Worksheet 11A (Form 511) runs A-K with no ownership step — "
                     "its line J is members' tax previously paid. On identical B-H inputs the two worksheets must "
                     "produce different limitations whenever nonresident ownership is below 100%."),
     "definition": {"rules": ["R-MD510-DCF9A", "R-MD511-DCF11A"],
                    "check": "9A.K == 9A.I * ownership_pct ; 11A has no ownership factor ; 9A.M != 11A.K when pct < 1"}},
    {"assertion_id": "FA-MD-DCF-COND", "title": "The DCF lesser-of is conditional on the worksheet checkbox",
     "assertion_type": "reconciliation", "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 7,
     "description": ("Form 510 line 15 = line 13, and Form 511 line 12 = line 10, unless the distributable-cash-flow "
                     "worksheet is used, in which case the lesser of the two applies. An unconditional MIN() would "
                     "zero the tax whenever the worksheet line is blank."),
     "definition": {"rules": ["R-MD510-L15", "R-MD511-L12"],
                    "check": "not dcf_used -> due == total_tax (NOT min(total_tax, None or 0))"}},
    {"assertion_id": "FA-MD-RATE-DERIV", "title": "The PTET rate is derived from two statutes, not hardcoded",
     "assertion_type": "table_invariant", "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 8,
     "description": ("§10-106.1 lowest county rate (0.0225) + §10-105(a) top marginal individual rate (0.0650) = "
                     "0.0875 for individual and fiduciary members; §10-105(b) = 0.0825 for entity members. Both "
                     "inputs are year-keyed and carry a staleness assertion — the rate moved 8.00% -> 8.75% for "
                     "TY2025 purely because the BRFA of 2025 added a 6.50% bracket."),
     "definition": {"rules": ["R-MD510-RATES", "R-MD511-RATES"],
                    "check": "ptet_individual_rate(2025) == lowest_county + top_marginal == 0.0875 ; entity == 0.0825"}},
    {"assertion_id": "FA-MD-OWNER-2LEG", "title": "Owner side is credit PLUS add-back — both legs required",
     "assertion_type": "flow_assertion", "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 9,
     "description": ("The §10-701.1 credit (K-1 Section D line 5 -> Form 502CR Part CC line 9 / 500CR / 504 / 505 "
                     "line 45) must be accompanied by the mandatory income add-back for K-1 Section D lines 2 and 4. "
                     "Emitting the credit without the add-back overstates owner relief by the full PTET. The add-back "
                     "must be a typed modification the 1040/1120/1041 modules consume, not prose, and must not be "
                     "pre-loaded into K-1 Section B."),
     "definition": {"rules": ["R-MD511-K1D"], "check": "addback == D2 + D4 whenever credit includes D2 or D4"}},
    {"assertion_id": "FA-MD-D1-NO-ADDBK", "title": "K-1 Section D line 1 is NEVER added back",
     "assertion_type": "reconciliation", "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 10,
     "description": ("D1 is the non-electing Form 510 nonresident tax, which §10-102.1(c)(1) already treats as a tax "
                     "imposed on the members and paid on their behalf. It carries no add-back sentence on the form or "
                     "in the instructions. Adding back D1 double-taxes every nonresident partner."),
     "definition": {"rules": ["R-MD510-K1D", "R-MD511-K1D"], "check": "addback excludes D1 for every combination of D1/D2/D4"}},
    {"assertion_id": "FA-MD-APPORT-FLOOR", "title": "A zero apportionment factor is entered as .000001",
     "assertion_type": "table_invariant", "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 11,
     "description": ("Form 510/511 line 3b and Schedule A line 4: '(If factor is zero, enter .000001)'. A factor is "
                     "computed to six decimal places and must exist even on a loss return (COMAR 03.04.03.08 B(5)). "
                     "The convention is on the form faces only — it is in neither booklet."),
     "definition": {"rules": ["R-MD510-APPORT", "R-MD511-APPORT"],
                    "check": "factor == 0 or denominator == 0 -> 0.000001 ; never None, never dropped"}},
    {"assertion_id": "FA-MD-NO-REWEIGHT", "title": "NO insignificant-denominator reweighting exists in Maryland",
     "assertion_type": "table_invariant", "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 12,
     "description": ("Maryland has no rule dropping or reweighting a factor whose denominator is zero or "
                     "'insignificant' — that rule is Fla. Stat. §220.15(1) and must never leak in. The final factor "
                     "for TY2025 is the receipts factor alone, unchanged by a zero property or payroll denominator, "
                     "and only the Comptroller may alter a formula (§10-402(e); §10-401(2))."),
     "bug_reference": "Wave premise error — a Florida rule asserted of Maryland; disproved exhaustively on verification 2026-08-17",
     "definition": {"rules": ["R-MD510-APPORT", "R-MD511-APPORT"],
                    "check": "final_factor(receipts, property=0, payroll=0) == final_factor(receipts) ; no reweight function exists"}},
    {"assertion_id": "FA-MD-K1H-FACTOR", "title": "K-1 Section H column 2 = column 1 x the Maryland apportionment factor",
     "assertion_type": "reconciliation", "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 13,
     "description": ("Section H is mandatory for TY2025 on both forms and has no tax line on either return. Column 2 "
                     "is the second consumer of the Schedule A factor; row 3 is resident-members-only. The PTE "
                     "computes no capital-gain surtax at entity level."),
     "definition": {"rules": ["R-MD510-K1H", "R-MD511-K1H"], "check": "H.col2 == H.col1 * SchA-4"}},
    {"assertion_id": "FA-MD-511-BASE", "title": "Form 511 line 2 carries the SALT add-back; Form 510 line 2 does not",
     "assertion_type": "reconciliation", "entity_types": FORM_ENTITY_TYPES, "status": "draft", "sort_order": 14,
     "description": ("Form 511 line 2 = federal Sch. K income block − federal-obligation interest + the deduction for "
                     "taxes based on net income (1065 page-1 line 14 / 1120-S page-1 line 12), adjusted for "
                     "prior-year Maryland refund income. Form 510 line 2 has no add-back. Nothing on the federal "
                     "return produces the adjusted figure — the handoff is lossy here."),
     "definition": {"rules": ["R-MD510-L2", "R-MD511-L2"],
                    "check": "MD_511.L2 - MD_510.L2 == salt_addback_net_of_prior_year_refund"}},
]


# ═══════════════════════════════════════════════════════════════════════════
# Command
# ═══════════════════════════════════════════════════════════════════════════

class Command(BaseCommand):
    help = (
        "Load the MD_510 + MD_511 specs (Maryland Pass-Through Entity returns, TY2025). "
        "Refuses to seed until Ken sets READY_TO_SEED=True after the in-session Gate-1 walk "
        "(W1, W2, W4-W11; W3 is WITHDRAWN)."
    )

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad MD_510 + MD_511 specs (Maryland Pass-Through Entity returns, TY2025)\n"))
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
                "\nREFUSING TO SEED MD_510 / MD_511: not cleared to seed.\n\n"
                "Content is authored, but seeding is gated until Ken reviews the packet and\n"
                "flips the sentinel. Walk items W1 (the election state machine and where its\n"
                "state lives), W2 (the manufacturing carve-out with no printed form line —\n"
                "R10's wording must be Ken's), W4 (the two-leg owner side, D2/D4 only), W5\n"
                "(the two DCF worksheets, the conditional lesser-of, the line-F transcription\n"
                "and the unsupported amended-return bar), W6 (the resident entity member\n"
                "moving boxes), W7 (K-1 Section H), W8 (Form 510C's aggregate 8.75%), W9\n"
                "(never auto-reweight an apportionment factor), W10 (S corp files Form 500 as\n"
                "well) and W11 (six recorded Comptroller errata) are unblessed.\n"
                "⚠ W3 is WITHDRAWN as a false conflict — do NOT re-raise it.\n"
                "Nine [UNVERIFIED] items remain open: U1, U3, U4, U5, U7, U8, U9, U10, U12.\n\n"
                f"READY_TO_SEED = {READY_TO_SEED} (must be True to proceed)\n\n"
                f"Currently empty / placeholder:\n  {still_empty}\n\n"
                "To proceed: review the module-level data lists (and md_pte_source_brief.md),\n"
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
        self.stdout.write("MD PTE loaded (MD_510 + MD_511).")
        for spec in FORMS:
            fn = spec["identity"]["form_number"]
            self.stdout.write(
                f"  {fn}: facts {len(spec['facts'])} / rules {len(spec['rules'])} / lines {len(spec['lines'])} / "
                f"diag {len(spec['diagnostics'])} / tests {len(spec['scenarios'])}"
            )
        self.stdout.write(f"  flow assertions: {len(FLOW_ASSERTIONS)}")
        self.stdout.write("=" * 60)
