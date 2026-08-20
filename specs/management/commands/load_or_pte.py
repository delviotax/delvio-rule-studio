"""Load the Oregon PTE specs — Form OR-65, Form OR-20-S and Form OR-21 (TY2025).

═══════════════════════════════════════════════════════════════════════════
WHAT THIS IS
═══════════════════════════════════════════════════════════════════════════
Oregon needs THREE pass-through specs, not two:

  OR_65     Form OR-65,   Oregon Partnership Income Return          (1065)
  OR_20_S   Form OR-20-S, Oregon S Corporation Tax Return           (1120S)
  OR_21     Form OR-21,   Oregon Pass-through Entity Elective Tax   (1065 + 1120S)

`OR_21` IS ITS OWN SPEC (campaign D-12, Group B). Its base is built ENTIRELY
from federal Schedule K with ZERO inputs from OR-65 or OR-20-S — verified by
two independent workstreams with zero exceptions, and the strings "OR-65" and
"OR-20-S" do not occur anywhere in 150-107-114-1. It has its own statutory due
date (the ORS ch. 316 date, via 2021 Or. Laws ch. 589 §3(8) → ORS 314.385(1)(a)),
its own calendar-year-only rule, its own apportionment schedule (OR-21-AP,
sales-factor-only), its own member directory, its own K-1, its own estimated-tax
regime and its own penalty set. Folding it in would couple three unrelated
release cadences.

Spec source: `delvio-states/research/or_pte_source_brief.md` — VERIFIED
(adversarial pass 2026-08-19, 26 corrections). ⚠ ITS §18 VERIFICATION SECTION
GOVERNS OVER THE BODY and this loader follows §18 everywhere they differ.
Conformity: `delvio-states/conformity/or_conformity.md` (VERIFIED 2026-08-06);
its §12 governs over its body.

NO prior RS spec exists — `lookup/OR_65/`, `/OR_20_S/`, `/OR_21/` (plus the
alternate spellings `OR_20S`, `OR21` and the legacy bare `65`) all returned 404
on 2026-08-17. All three are greenfield; `<ST>_<FORM>` per campaign D-9.

═══════════════════════════════════════════════════════════════════════════
⚠⚠ C1 — THE MOST IMPORTANT BUILD INSTRUCTION IN THE WAVE (campaign D-12)
    OREGON RUNS TWO MODIFICATION-CODE NAMESPACES AND ONE ENGAGEMENT TOUCHES BOTH
═══════════════════════════════════════════════════════════════════════════
TWELVE code numbers collide between the individual set (Publication OR-CODES,
150-101-432 Rev. 10-07-25) and the corporate set (Schedule OR-ASC-CORP):

  TEN true semantic collisions — same number, DIFFERENT item:
      118 · 132 · 150 · 151 · 158 · 159 · 352 · 356 · 358 · 361
  TWO same-item / different-label near-collisions (fatal to a string-equality
  reconciliation, safe in substance):
      338 · 344

Code **158** is the exemplar: on Schedule OR-ASC-CORP it is
*Gain or loss on disposition of depreciable property* — a DEPRECIATION-BASIS
item. In Publication OR-CODES it is
*Interest and dividends on government bonds of other states* — a
MUNICIPAL-INTEREST item. **A namespace mix-up posts a depreciation-basis
difference onto a municipal-interest line, and the return still foots.**

⚠ **158's semantic twin in the individual set is 154**, not 158
(`154 - Gain or loss on sale of depreciable property with different basis for
Oregon`). So the SAME economic item carries DIFFERENT numbers while the SAME
number carries different items. **A label-driven mapper survives the crossing;
a number-driven mapper fails silently.** Every lookup helper below is
label-capable and namespace-mandatory; `or_code()` REFUSES a bare integer with
no namespace.

⚠⚠ **WHERE THE NAMESPACES MEET: the Schedule OR-K-1 OVERFLOW ATTACHMENT.**
OR-K-1's face is code-free, but lines 15 `Other additions (include schedule)`
and 18 `Other subtractions (include schedule)` are both printed
*(include schedule)*, and Schedule OR-K-1 Instructions 150-101-002-1
(Rev. 09-03-25) p. 2 requires that attachment to carry **Publication OR-CODES —
i.e. INDIVIDUAL — codes**: *"Include the code for each item from Publication
OR-CODES"* / *"Use the appropriate code for each item as shown on an attachment
to Schedule OR-K-1 or as listed in Publication OR-CODES."*
**Schedule OR-K-1 is issued by BOTH entity forms.** So an S corporation running
CORPORATE codes on OR-20-S lines 2/3 must simultaneously emit INDIVIDUAL codes
on the OR-K-1 attachment it hands each shareholder. **Both namespaces are live
inside one OR-20-S engagement and the DOR has published no firewall there.**

⚠⚠ **THE DECOY — DO NOT LET IT TALK YOU OUT OF THE GUARD.** Two DOR notes read:
  Sch. OR-ASC-CORP Instr. 150-102-033-1 p. 1: "Note for OR-20-S filers: This
    schedule and these codes are not for additions or subtractions on Schedule SM."
  OR-20-S Instr. 150-102-025-1 p. 12: "Note: Don't use Schedule OR-ASC-CORP
    codes for Schedule SM additions and subtractions."
Both are TRUE and both are IRRELEVANT: they police **Schedule SM**, which is a
code-free named-line schedule that nobody claimed carries codes. **A verification
pass was fooled by exactly this, refuted the crossing point, and then RETRACTED
the refutation.** The retraction is the operative finding (brief §18.3(c)).
**Namespace the lookup; do not police Schedule SM.**

⚠ **THREE tables, not two** — additions and subtractions × 2 namespaces, PLUS
`OR_ASC_CORP_CREDIT_CODES` (Section D, an unrelated 8xx/999 series). Line 15 is
a CREDIT line and is NOT part of the collision hazard (brief §18.3(g)); the
collision analysis governs **OR-20-S lines 2 and 3 only**.

⚠ **The corporate table is seeded from the FULL OR-ASC-CORP universe, not from
Appendix A.** Appendix A is the S-corp SUBSET. Worked proof: code **341**
(*Income on a composite return*) is directed by Pub. OR-OC to Schedule
OR-ASC-CORP Section B for corporate composite owners, yet appears NOWHERE in
Appendix A. An `appendix_a` eligibility flag rides on top; seeding Appendix A as
if it were the whole corporate table would fail a legitimate corporate composite
subtraction.

═══════════════════════════════════════════════════════════════════════════
⚠⚠ STATUTORY STALENESS TRIPWIRE — SB 1507 INVALIDATES §7.2 BY STATUTE FOR TY2026
═══════════════════════════════════════════════════════════════════════════
Oregon's conformity is a **HYBRID and must not be flattened**:
  prong (b) ROLLING — "if related to the definition of taxable income, as
      applicable to the tax year of the taxpayer"  → every income-measurement
      provision, so OBBBA flows into TY2025 automatically: 100% bonus, $2.5M/$4M
      §179, NO add-back, NO state basis for TY2025 acquisitions.
  prong (a)/(c) FIXED at **December 31, 2023** for TY2025 — an ENUMERATED list
      at ORS 314.011(2)(c), all of it administrative or mechanical
      (ORS 314.302 installment interest, 314.385 due dates, 314.402, 314.410,
      314.412, 314.525, 314.767(7) the §1375(d) waiver, 314.771 LIFO, 314.772).

**Enrolled SB 1507 = 2026 Oregon Laws ch. 142 §35 changes ORS 314.011(2)(b)(A)
and (2)(c) from December 31, 2023 to December 31, 2025; §41 does the same to
ORS 317.010(7).** §48(1) verbatim: *"…the amendments to statutes by sections 16
to 47 of this 2026 Act apply to transactions or activities occurring on or after
January 1, 2026, in tax years beginning on or after January 1, 2026."*
**§35 is in range ⇒ TY2025 STAYS at 12/31/2023 and TY2026 MOVES.**
Every frozen-side figure in this spec is TY2025-ONLY. `OR_CONFORMITY_FIXED_DATE`
is tax-year-keyed and `or_conformity_fixed_date()` REFUSES an unkeyed year, so
TY2026 cannot silently inherit TY2025 conformity. Diagnostic
`D_OR_TY2026_CONFORMITY_STALE` carries the tripwire.
SB 1507 also decouples Oregon from §168(k) for property placed in service in tax
years beginning on/after 1/1/2026 (measured against §168(k) as in effect
12/1/2017) — a TY2026 dual-basis regime that a TY2025 spec MUST NOT model.
⚠ Residual: whether SB 1507 §48(2)-(3)'s retroactivity machinery reaches a
TY2025 return is UNSETTLED (§18.11 item 4).
⚠ Near-miss on the record: **HB 2092 (2025 R1)** would have disconnected Oregon
from the rolling prong for exactly TY2025. It DIED in Senate Finance and Revenue.
The rolling conclusion is right, but it was one committee vote from void.

═══════════════════════════════════════════════════════════════════════════
THE OTHER D-12 RULINGS THAT BIND THIS FILE
═══════════════════════════════════════════════════════════════════════════
D-12 W2 · "THE PRINTED FACE GOVERNS; INSTRUCTION CONFLICTS ARE LOGGED" —
  ratified as a standing Oregon authoring convention. SIX instruction defects
  were found in FINAL TY2025 booklets (see OR_INSTRUCTION_DEFECTS).
  ⚠ **COROLLARY: Form OR-21 HAS NO PUBLISHED FACE AT ALL**, so for OR-21 the
  rule CANNOT apply. Every OR-21 line number rests on "Worksheet OR-21" inside
  150-107-114-1 p. 10, stamped *"This worksheet is for informational purposes
  only. Do not file this worksheet."* That provenance is encoded explicitly on
  every OR-21 line (`notes` carry OR21_PROVENANCE) and in fact
  `or21_line_provenance`, rule R-OR21-PROVENANCE and diagnostic
  D_OR21_NO_PUBLISHED_FACE. It is an enumeration result, not a failed URL
  guess: the DOR FormsPubs SharePoint list was re-queried (1,712 items,
  __next = null) and 150-107-114 / -112 / -111 / -110 appear ZERO times in any
  year, while 150-107-113 (Schedule OR-21-K-1) appears as a real face in
  2022-2025. AcroForm widget counts: 0/0/0/0 vs 23 on the OR-21-K-1 face.

D-12 W3 · **Schedule OR-AP part 2: ONE FILED INSTANCE plus a SEPARATE
  OFF-SCHEDULE owner-source computation.** ⚠ The earlier "must be run twice"
  mandate was **DISPROVEN on verification** — the DOR's owner-level use is
  PERMISSIVE (*"Most pass-through entities (PTEs) don't complete Schedule OR-AP,
  part 2. However, they MAY use it to determine the Oregon-source distributive
  income for their owners."*). **DO NOT PRINT TWO PART 2s.** The two evaluations
  differ in three ways (line-1 input, line 10 suppressed, line-12 destination)
  and that substance survives — as an ENGINEERING INFERENCE, now labelled one.

D-12 · **The PTE-E election is ANNUAL and REVOCABLE — NOT binding on future
  years.** This was the Mississippi question in Wave 3 and Oregon answers it the
  OPPOSITE way; do not carry the Mississippi assumption over. Owner side is
  **credit AND add-back**: refundable code **900** — ⚠ **NOT prorated for
  nonresidents** (Pub. OR-CODES marks 895/896/897/898/901 `PR`; 900 is plain `X`
  on OR-40, OR-40-N and OR-40-P) — plus addition code **167**, plus a later
  subtraction code **387**. Rate **9% / 9.9%** with a $250,000 breakpoint.

D-12 W6 · **PENALTY POSTURE IS OPPOSITE BETWEEN THE TWO ENTITY RETURNS.**
  OR-65: *"Don't submit a penalty payment with the return. Penalty payments are
  only required if the department assesses a penalty."* and the face has NO
  penalty or interest line at all. OR-20-S: SELF-ASSESSES at lines 22/23/24.
  OR-21: a THIRD, narrower set (5% + interest only; no 20%, no 100%).
  **Encoded as three separate models. Do not unify.**

D-12 W8 · **Portland / Multnomah / Metro: RED-DEFER for v1 with an explicit
  diagnostic.** It is a **Group E routing item with NO DECISION TAKEN** — four
  separate returns, a separate agency (City of Portland Revenue Division), a
  separate MeF program. **Neither silently included nor silently excluded: it is
  named** (D_OR_R2_PORTLAND_METRO). ⚠ Two corrections carried:
   (a) **LIC-2.05's preparer prong covers PERSONAL returns ONLY.** The four
       business returns are bound by the BUSINESS prong, whose trigger is the
       TAXPAYER's own federal e-file duty (26 CFR 301.6011-3(a) partnerships;
       26 CFR 301.6037-2(a) S corps — 301.6011-5 is the Form 1120 rule and does
       NOT reach 1120-S). LIC-2.05 has no numeric threshold of its own.
   (b) **METBIT-65/-20S start at Part II line 4 and pull Schedule K at line 6.**
       On the METBIT forms **line 7 is `Non-business income or loss subtraction`.**
       Reusing the P-2025/SC-2025 map (line 7 / line 10) writes ordinary income
       into the wrong field **and the return still foots.** See OR_METBIT_LINE_MAP.

D-12 · **RED-DEFER what is genuinely blocked, each with its own diagnostic and
  no silent gap:** the **OR-21 MeF schema family** (U1/U19/U23) and the
  **OR-21-MD denominator** (U5), both awaiting the DOR developers' handbook —
  a Ken-only request that is DECIDED (D-12 A5) but NOT YET SENT.

D-12 · **U5 is PROVEN IMPOSSIBLE with any NEGATIVE member share.** Worked
  counterexample: members at +$100,000 / +$100,000 / -$50,000 → OR-21 line 22 =
  $150,000, line 23 = $13,500, but OR-21-MD Part B lines 4 and 5 each total
  **$18,000** — 33.3% over, i.e. $18,000 of refundable member credit against
  $13,500 of entity tax. A ZERO share is harmless; only a NEGATIVE share breaks
  it (the original "zero-or-loss" framing was too broad).
  ⚠ **The brief's proposed fix (positive-share denominator) reasons from the
  mandatory tie-out Caution, NOT from a cited rule.** So this file encodes the
  IMPOSSIBILITY and the DIAGNOSTIC, and `or21_md_allocation()` returns the
  candidate figures under BOTH readings while refusing to label either as DOR
  guidance. `R-OR21-MD-TIEOUT` says so in terms.

═══════════════════════════════════════════════════════════════════════════
THE SIX THINGS MOST LIKELY TO BE BUILT WRONG (all encoded as real branches)
═══════════════════════════════════════════════════════════════════════════
1. ⚠ THE CODE-NAMESPACE CROSSING — C1 above. `or_code()` refuses a namespace-free
   lookup; `or_assert_namespace()` refuses a cross-use; the harness proves both.
2. ⚠ **OR-65's two gates are DIFFERENT BOOLEANS.** FILING is required if
   `2A OR 2B`. The $150 is owed only if `1A AND (2A OR 2B)`. A partnership with
   Oregon resident partners but no Oregon business activity FILES AND OWES
   NOTHING. Collapsing them bills $150 to every out-of-state partnership with
   one Oregon partner.
3. ⚠ **OR-20-S line 6 is completed EVEN WHEN THE TAX IS ZERO.** The face tells a
   no-BIG/no-ENPI filer to enter the apportionment percentage on line 6 and then
   zeroes on 7/8/10 — because line 6 is the number every NONRESIDENT SHAREHOLDER
   needs. A build that short-circuits to $150 silently drops it. **The single
   most likely OR-20-S bug** (brief §2.2).
4. ⚠ **THE OR-65 PRORATION TABLE IS A PUBLISHED 12-ROW ROUNDED TABLE, NOT A
   FORMULA.** Every half-dollar rounds UP: 1→$13, 3→$38, 5→$63, 7→$88, 9→$113,
   11→$138. A `round()` implementation using banker's rounding gives $12/$62/
   $112/$138 and is **wrong on five of the twelve rows**. Seeded as a literal
   table. ⚠ And the switch is checkbox **(e) `Accounting period change`**, NOT
   the `Short-year return` box — two different boxes on the same page.
   ⚠ OR-20-S states the SAME rule as a bare FORMULA (`$150 x months / 12`). Two
   different authorities; **do not share one proration routine** (D-12 W6).
5. ⚠ **THE ZERO SIDE OF THE OR-20-S MINIMUM TAX IS NOT IN ORS 317.090.**
   317.090(2)(b) supplies only the $150. The ZERO follows from the PREDICATE of
   317.090(2) (*"for the privilege of carrying on or doing business by it within
   this state"*) read with **ORS 318.020(1)** and **ORS 318.031**. Cite
   318.020/318.031 for the zero, keyed to the `Income tax` checkbox.
6. ⚠ **OR-21 LINE 21 DRAWS FROM LINE 17, NOT LINE 19.** The DOR instruction says
   "line 19" TWICE in one paragraph; line 19 is a four-decimal PERCENTAGE and
   line 21 is a dollar field feeding `line 22 = line 20 + line 21`. Building the
   DOR's literal text puts a percentage into a dollar field. The first sentence
   of the same paragraph says "line 17" and that is the only arithmetic that
   closes. Two occurrences of the same wrong pointer is the signature of a stale
   renumbering, which RAISES confidence in the correction.

═══════════════════════════════════════════════════════════════════════════
VERIFIED-NEGATIVE INVENTORY — encode the ABSENCE deliberately (pinned in the
harness so a later contributor cannot quietly add a field "for symmetry")
═══════════════════════════════════════════════════════════════════════════
N1  NO TY2025 §168(k) bonus add-back and NO state §179 cap or phaseout anywhere
    in the Oregon PTE set. ORS 317.301 is the ONLY §168(k)/§179 disconnect in
    Oregon law and its window is CLOSED — applicability note 2011 c.7 §31:
    *"ORS 316.739 and 317.301 apply to tax years beginning on or after
    January 1, 2009, and before January 1, 2011."* Its only TY2025 relevance is
    subsection (4), the UNWIND of a 2009/2010 addition. Pub. OR-17 (Rev.
    01-29-26) p. 91: *"As of the date this publication was last revised, Oregon
    had not disconnected from any new federal depreciation expense provisions
    for this tax year."*
N2  NO Schedule I total line and NO flow from Schedule I to OR-65 line 3 or to
    any other OR-65 line. Schedule I does not foot. A build that ties Schedule I
    to the tax computation has misread the form.
N3  NO Schedule OR-ASC-CORP **Section C** (standard credits) line and NO
    **Section E** (refundable credits) line on Form OR-20-S. Confirmed three
    ways: the ASC-CORP face routes C7 and E5 to OR-20/OR-20-INC/OR-20-INS ONLY;
    the instructions say *"Form OR-20-S filers cannot claim standard credits"*
    and *"There are no refundable credits available to S corporations"*; and
    OR-20-S Schedule ES line 7 is printed **`7. Reserved`**. ⚠ A shared
    corporate-series component mapping `ASC-CORP E5 → Schedule ES line 7` writes
    a refundable credit into a RESERVED box and the arithmetic still foots.
N4  NO GILTI computation on Form OR-20-S — a bare informational checkbox with no
    line, no add-back, no subtraction and no Appendix A code. DO NOT INVENT ONE.
    (SB 1510 (2026) replaces GILTI with NCTI under IRC §951A — TY2026, not TY2025.)
N5  NO estimated payments on Form OR-65, no OR-65 analogue to Form OR-37, no
    underpayment interest and no Schedule ES. Form OR-65-V carries only TWO
    payment types — there is no `Estimated payment` box.
N6  NO apportionment percentage field anywhere on the Form OR-65 face. It exists
    only on Schedule OR-AP part 1 line 23 and lands on each Schedule OR-K-1
    Part III header.
N7  NO property factor and NO payroll factor on Schedule OR-21-AP, and therefore
    NO double-weighted-sales alternative for a PTE-E filer — even though the
    OR-21 line 19 instruction routes financial institutions and public utilities
    to ORS 314.280. There is no OR-21 artifact to do it on (U13 → RED-DEFER).
N8  NO C-corporation twelve-tier minimum-tax table on Form OR-20-S. S corps get
    the flat $150 under ORS 317.090(2)(b). The table reappears only on Schedule
    OR-OC-2, per corporate composite owner, keyed to THAT OWNER's share of
    Oregon sales.
N9  NO "authorize your preparer" checkbox on Form OR-65 (OR-20-S has one).
    NO Oregon-partnership-representative designation field on Form OR-65 —
    *"Don't use Form OR-65 to designate an Oregon partnership representative."*
N10 NO corporate analogue to refundable code 900. The PTE-E credit is delivered
    exclusively to INDIVIDUAL members.
N11 Question K (`total Oregon sales`) feeds NOTHING on Form OR-20-S. Do not wire
    it into a minimum-tax lookup on the S-corp form.
N12 NO §199A, NO §179 line and NO separately-stated deduction of any kind in the
    Form OR-21 base — Pub. OR-21-EST p. 1 says so expressly. The base is GROSS.

═══════════════════════════════════════════════════════════════════════════
VERIFIED STRUCTURE — the FINAL TY2025 Oregon DOR PDFs, read positionally by the
research pass 2026-08-17 and INDEPENDENTLY RE-DERIVED by the adversarial pass
2026-08-19 (45 DOR PDFs re-checked; page counts and /ModDate all match):
  Form OR-65 150-101-065 Rev. 05-29-25 ver. 01 (3 pp.) — COMPLETE positional
    re-derive, ALL 3 PAGES, 0 errors, after a real cross-state contamination
    incident and a quarantine-and-rebuild. VERDICT: INTACT.
  Form OR-65 Instr. 150-101-065-1 Rev. 10-16-25 (4 pp.)
  Form OR-20-S 150-102-025 Rev. 07-10-25 ver. 01 (8 pp.) — COMPLETE positional
    re-derive, ALL 8 PAGES, 0 errors. VERDICT: INTACT.
  Form OR-20-S Instr. 150-102-025-1 Rev. 10-14-25 (16 pp.)
  Form OR-21 Instr. 150-107-114-1 Rev. 04-01-26 ver. 01 (10 pp.) — carries
    Worksheet OR-21 p. 10; ⚠ NO FORM FACE EXISTS
  Sch. OR-21-MD Instr. 150-107-112-1 · OR-21-AP Instr. 150-107-111-1 ·
    OR-21-MD-PT Instr. 150-107-110-1 (all Rev. 10-16-25; no faces)
  Sch. OR-21-K-1 150-107-113 Rev. 07-24-25 ver. 01 — the ONLY published PTE-E face
  Pub. OR-21-EST 150-107-115 ⚠ Rev. 10-16-24 — the OLDEST revision in the set
  Sch. OR-AP 150-102-171 Rev. 07-10-25 ver. 01 + Instr. -171-1 Rev. 10-14-25
  Sch. OR-ASC-CORP 150-102-033 Rev. 07-10-25 ver. 01 + Instr. -033-1 Rev. 10-14-25
  Sch. OR-K-1 150-101-002 Rev. 09-03-25 ver. 01 + Instr. -002-1 Rev. 09-03-25
  Pub. OR-CODES 150-101-432 Rev. 10-07-25 (5 pp.) — full positional sweep
  Sch. OR-DEPR 150-101-025 Rev. 09-03-25 · Form OR-19 150-101-182 Rev. 06-03-25 ·
    Form OR-19-AF 150-101-175 ⚠ Rev. 09-04-24 · Form OR-OC 150-101-154
    Rev. 07-21-25 · Pub. OR-OC 150-101-155 Rev. 02-04-26 ·
    Form OR-24 150-101-734 ⚠ Rev. 08-18-23 · Form OR-PCR 150-101-184
  ORS 2025 EDITION chapters 314 / 316 / 317 / 318 (⚠ pull with `curl --compressed`;
    a plain fetch silently truncates ORS 314.011-314.037)
  2021 Or. Laws ch. 589 (as amended 2022 c.82 §3) · 2026 Or. Laws ch. 142 (SB 1507)
  OAR 150-316-0155 · FINAL 2025 IRS 1065 / 1120-S / Sch. D (1120-S) / 8824
Full brief: delvio-states/research/or_pte_source_brief.md.

═══════════════════════════════════════════════════════════════════════════
⚠⚠ GATE 1 — SEED APPROVAL GRANTED BY KEN 2026-08-19 (campaign D-12). READY_TO_SEED = True.
D-12 approved the WAVE SCOPE (three Oregon specs, the code-namespace ruling, the
OR-AP part 2 reversal, the penalty split, the Portland deferral). It did NOT
approve seeding these specs, and TWO items remain BLOCKED on sources only the
Oregon DOR can supply — the OR-21 MeF schema family (U1/U19/U23) and the
OR-21-MD denominator (U5). D-12 A5 DECIDED to request the DOR developers'
handbook, draft forms and test scenarios; that request is a Ken-only external
action and HAS NOT BEEN SENT. Until it lands, `OR_21`'s line numbers rest on a
"do not file" worksheet and its owner-credit allocation is provably unclosable
whenever any member has a loss share.
Also open before seeding: **U24 — 2025 Or. Laws ch. 36 §3 amends ORS 314.772**
(the only load-bearing ORS section in the brief with a 2025-session amendment)
and its applicability date was never run down. **Pull it before OR-20-S line 15
ships.**
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
# THE SEED SENTINEL. Do NOT flip this to silence an error.
#
# It is False because Gate 1 has NOT been taken for the Oregon specs. See the
# banner above: D-12 approved the wave SHAPE, not the seed; the OR-21 MeF schema
# family (U1/U19/U23) and the OR-21-MD denominator (U5) are BLOCKED on the DOR
# developers' handbook, which is a decided-but-unsent Ken-only action (D-12 A5);
# and U24 (2025 Or. Laws ch. 36 §3, amending ORS 314.772) is unpulled.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = True   # Gate-1 SEED APPROVAL granted by Ken 2026-08-19 (campaign D-12)


FORM_JURISDICTION = "OR"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"

FORM_CODE_OR65 = "OR_65"
FORM_CODE_OR20S = "OR_20_S"
FORM_CODE_OR21 = "OR_21"
FORM_CODES = (FORM_CODE_OR65, FORM_CODE_OR20S, FORM_CODE_OR21)

# Module tokens. Derived from the ATTACHED FEDERAL RETURN. Form OR-65 serves the
# 1065 module only and Form OR-20-S the 1120S module only -- Oregon does not put
# S corporations on OR-65 at all (the `Type of entity` box has four values and no
# S-corp option). Form OR-21 serves BOTH and forks at line 9.
M_1065 = "1065"
M_1120S = "1120S"
MODULES = (M_1065, M_1120S)


def _yk(d: dict, year: int):
    """Tax-year-keyed lookup. Raises rather than silently defaulting.

    Every figure in this spec is TY2025-keyed and SB 1507 moves Oregon's
    conformity date for TY2026 (see the banner). A silent fallback would let a
    TY2026 engagement inherit TY2025 law, which is exactly the failure this
    campaign's staleness rule exists to prevent.
    """
    if year not in d:
        raise KeyError(
            f"No TY{year} value seeded. Oregon figures are tax-year-keyed and a new "
            f"tax year staleness-invalidates them (SB 1507 = 2026 Or. Laws ch. 142 "
            f"moves the conformity date to 12/31/2025 effective TY2026). Seeded years: "
            f"{sorted(d)}"
        )
    return d[year]


# ═══════════════════════════════════════════════════════════════════════════
# CONFORMITY -- THE HYBRID, AND THE TY2026 STALENESS TRIPWIRE
#
# ⚠ DO NOT FLATTEN. Oregon is NOT "static 12/31/2023" and NOT "rolling". It is
# BOTH, split by subject matter, and the split is identical across all three
# chapters that touch a PTE return (ORS 314.011(2)(b), 316.012, 317.010(7)).
#
# ⚠ DO NOT ENCODE THE DOR ONE-LINER. The OR-20-S booklet says "Oregon is tied to
# the federal definition of taxable income as of December 31, 2023" -- which
# or_conformity.md §2 flags as STATED BACKWARDS and which was verified
# byte-for-byte across all three corporate instruction sets. The statute says the
# opposite: the taxable-income definition is the ROLLING prong.
# ═══════════════════════════════════════════════════════════════════════════

# The FIXED-date prong. TY2025 = 12/31/2023. TY2026 = 12/31/2025 by SB 1507 §35.
OR_CONFORMITY_FIXED_DATE: dict[int, str] = {2025: "2023-12-31", 2026: "2025-12-31"}
OR_CONFORMITY_TYPE = "partial"          # matches the seeded JurisdictionConformitySource row (D-10)
OR_CONFORMITY_ROLLING_PRONG = (
    "ROLLING PRONG. ORS 314.011(2)(b)(B) / ORS 317.010(7)(b) - 'If related to the definition of taxable "
    "income, as applicable to the tax year of the taxpayer.' EVERY income-measurement "
    "provision rides this prong, so OBBBA flows into TY2025 automatically."
)
OR_CONFORMITY_FIXED_PRONG = (
    "FIXED PRONG, 12/31/2023 for TY2025. ORS 314.011(2)(c) - an ENUMERATED list, not a category judgment: ORS 314.105, "
    "314.256, 314.260(1)(b), 314.302, 314.306, 314.330, 314.360, 314.362, 314.385, "
    "314.402, 314.410, 314.412, 314.525, 314.767(7), 314.771 and 314.772, plus 'other "
    "provisions of this chapter, except those described in paragraph (b)'."
)
# ⚠ Build to the ENUMERATION, not to 'similar administrative provisions'. In
# particular Oregon's CORPORATE NOL rules live in ORS 317.476/317.479, NOT in
# chapter 314, so the chapter-314 freeze list does not reach them.
OR_CONFORMITY_FROZEN_SECTIONS_ON_PTE: dict[str, str] = {
    "ORS 314.302": "OR-20-S line 13 - installment-obligation interest",
    "ORS 314.306": "Schedule I / Schedule SM 'other' - discharge of indebtedness (IRC 108)",
    "ORS 314.385": "all three due dates",
    "ORS 314.402": "understatement penalty",
    "ORS 314.410": "deficiency limitation period / amended-return window",
    "ORS 314.412": "refund limitation period / amended-return window",
    "ORS 314.525": "OR-20-S line 24 / Form OR-37 estimated-tax underpayment",
    "ORS 314.767(7)": "OR-20-S line 1b - the IRC 1375(d) ENPI WAIVER mechanic only",
    "ORS 314.771": "OR-20-S line 17 - IRC 1363(d) LIFO recapture",
    "ORS 314.772": "Schedule OR-K-1 line 19 - business credits allowable to SHAREHOLDERS",
}
# ⚠ EVERY frozen provision above is ADMINISTRATIVE or MECHANICAL. None of them
# moves an income figure on a TY2025 Oregon PTE return. That is the practical
# answer to "which side of the line."
#
# ⚠ THE ONE GENUINELY FUZZY EDGE: IRC 1375 is SPLIT ACROSS BOTH PRONGS BY
# SUBSECTION. ORS 314.767(6) incorporates the 1375 provisions that relate to the
# MEASUREMENT of excess net passive income (arguably rolling, prong (b)); ORS
# 314.767(7) -- the 1375(d) waiver -- is expressly frozen by (c). OBBBA did not
# amend 1375, so the distinction is INERT for TY2025. Recorded (U12) so a TY2026
# pass does not have to rediscover it.
OR_CONFORMITY_1375_SPLIT = (
    "ORS 314.767(6) = measurement of excess net passive income (rolling prong); "
    "ORS 314.767(7) = the IRC 1375(d) waiver (frozen 12/31/2023). Oregon has split "
    "one IRC section across both prongs BY SUBSECTION. Inert for TY2025 - OBBBA did "
    "not amend IRC 1375. U12."
)

# ⚠ THE TRIPWIRE ITSELF.
OR_SB1507_CITE = "Enrolled SB 1507 = 2026 Oregon Laws ch. 142, secs. 35, 41 and 48(1)"
OR_SB1507_APPLICABILITY = (
    "sec. 48(1), verbatim: 'Except as provided in subsections (2) and (3) of this "
    "section, the amendments to statutes by sections 16 to 47 of this 2026 Act apply to "
    "transactions or activities occurring on or after January 1, 2026, in tax years "
    "beginning on or after January 1, 2026.' Section 35 is inside that range, so "
    "TY2025 STAYS at 12/31/2023 and TY2026 MOVES to 12/31/2025."
)
OR_TY2026_STALENESS: dict[int, bool] = {2025: False, 2026: True}


def or_conformity_fixed_date(year: int = FORM_TAX_YEAR) -> str:
    """The FIXED-prong IRC date for a tax year. Refuses an unkeyed year."""
    return _yk(OR_CONFORMITY_FIXED_DATE, year)


def or_conformity_is_stale_for(year: int) -> bool:
    """True when `year` is past the TY2025 keying of every figure in this spec.

    ⚠ This is a STATUTORY tripwire, not a housekeeping nicety: SB 1507 sec. 35
    moves ORS 314.011(2)(b)(A) and (2)(c) from 12/31/2023 to 12/31/2025 and
    decouples Oregon from IRC 168(k) for property placed in service in tax years
    beginning on or after 1/1/2026. A TY2026 Oregon PTE spec must model a full
    dual-basis regime. A TY2025 one MUST NOT.
    """
    return year > FORM_TAX_YEAR


# ═══════════════════════════════════════════════════════════════════════════
# ⚠⚠ C1 -- THE THREE NAMESPACED CODE TABLES
#
# THREE tables, not two: additions and subtractions x 2 namespaces, PLUS the
# OR-ASC-CORP Section D CREDIT series (8xx / 999), which is an entirely separate
# numbering space with no overlap at all.
#
# Rows carry a LABEL because a label-driven mapper survives the 158/154 crossing
# and a number-driven one fails silently. Prefer `or_code_by_label`.
# ═══════════════════════════════════════════════════════════════════════════

NS_INDIVIDUAL = "individual"        # Publication OR-CODES, 150-101-432 Rev. 10-07-25
NS_CORPORATE = "corporate"          # Schedule OR-ASC-CORP, 150-102-033 (FULL universe)
NS_CORP_CREDIT = "corporate_credit"  # Schedule OR-ASC-CORP Section D, 8xx / 999
NAMESPACES = (NS_INDIVIDUAL, NS_CORPORATE, NS_CORP_CREDIT)

K_ADDITION = "addition"
K_SUBTRACTION = "subtraction"
K_CREDIT = "credit"


class OregonCodeNamespaceError(ValueError):
    """Raised when a modification code is used without, or across, a namespace.

    This is deliberately a HARD failure. Twelve Oregon code numbers collide and
    the worst of them -- 158 -- silently posts a depreciation-basis difference
    onto a municipal-interest line while the return still foots. A soft warning
    would be indistinguishable from a correct return.
    """


# ---------------------------------------------------------------------------
# INDIVIDUAL namespace -- Publication OR-CODES 150-101-432 (Rev. 10-07-25),
# "Effective for tax year 2025". Full positional sweep, all 5 pages.
# Used by: Form OR-65 Schedule I; Schedule OR-K-1 and ITS OVERFLOW ATTACHMENT
# (even when the issuing PTE is an S corporation); every individual owner's
# Schedule OR-ASC / OR-ASC-NP.
# `forms` records the individual returns each code is available on; `prorated`
# records Pub. OR-CODES' own `PR` legend.
# ---------------------------------------------------------------------------
OR_CODES_INDIVIDUAL: list[dict] = [
    # ---- Additions (Schedule OR-ASC Section A / OR-ASC-NP Section B) -------
    {"code": 118, "kind": K_ADDITION, "label": "Oregon deferral of reinvested capital gain",
     "collides": True, "note": "⚠ collides with corporate 118 (deferred gain from out-of-state disposition of property)"},
    {"code": 132, "kind": K_ADDITION, "label": "Accumulation distribution from certain domestic trusts",
     "collides": True, "note": "⚠ collides with corporate 132 (charitable donations not allowed for Oregon)"},
    {"code": 150, "kind": K_ADDITION, "label": "Basis of business assets transferred into Oregon",
     "collides": True, "note": "⚠ collides with corporate 150 (interest income excluded from the federal return)"},
    {"code": 151, "kind": K_ADDITION, "label": "Depletion in excess of property basis",
     "collides": True, "note": "⚠ collides with corporate 151 (Oregon excise tax and other tax)"},
    {"code": 152, "kind": K_ADDITION, "label": "Depreciation difference for Oregon",
     "collides": False, "note": "INDIVIDUAL ONLY - verified ABSENT from OR-20-S Appendix A"},
    {"code": 153, "kind": K_ADDITION, "label": "Federal depreciation disconnect",
     "collides": False, "note": "INDIVIDUAL ONLY - verified ABSENT from OR-20-S Appendix A"},
    {"code": 154, "kind": K_ADDITION,
     "label": "Gain or loss on sale of depreciable property with different basis for Oregon",
     "collides": False,
     "note": ("⚠⚠ THE SEMANTIC TWIN OF CORPORATE 158. The same economic item is 158 corporate and "
              "154 individual, while 158 INDIVIDUAL is an unrelated municipal-interest item. This "
              "is what makes the hazard SILENT: a label-driven mapper survives, a number-driven "
              "mapper posts to the wrong line and the return still foots.")},
    {"code": 158, "kind": K_ADDITION, "label": "Interest and dividends on government bonds of other states",
     "collides": True,
     "note": ("⚠⚠ THE EXEMPLAR COLLISION. Corporate 158 is 'Gain or loss on disposition of "
              "depreciable property' - a DEPRECIATION-BASIS item. This is a MUNICIPAL-INTEREST "
              "item. Mixing them posts a depreciation-basis difference onto a municipal-interest "
              "line. Its corporate-side twin is 154, above.")},
    {"code": 159, "kind": K_ADDITION, "label": "Federal subtraction for retirement savings rollover from IDA",
     "collides": True, "note": "⚠ collides with corporate 159 (income from sources outside U.S.)"},
    {"code": 167, "kind": K_ADDITION, "label": "PTE-E tax deducted on entity-level federal return",
     "collides": False,
     "note": ("SAFE SHARED - identical in both namespaces. Pub. OR-CODES p. 2, available on OR-40, "
              "OR-40-N and OR-40-P. This is leg 1 of the three-leg PTE-E owner treatment; the "
              "electing PTE reports it on Schedule OR-21-K-1 line 2, and a TIERED member (a "
              "partnership that is itself a member of another electing PTE) reports it on OR-65 "
              "Schedule I."), "forms": ["OR-40", "OR-40-N", "OR-40-P"]},
    {"code": 187, "kind": K_ADDITION, "label": "CPAR addition",
     "collides": False,
     "note": ("SAFE SHARED - identical in both namespaces. Pub. OR-OC p. 8: 'Use these codes, even "
              "if another code is assigned for the specific type of increased or decreased income.'")},
    # ---- Subtractions (Schedule OR-ASC Section C / OR-ASC-NP Section D) ----
    {"code": 336, "kind": K_SUBTRACTION,
     "label": "Film production labor rebate-Greenlight Oregon Labor Rebate Fund",
     "collides": False,
     "note": ("SAFE SHARED in SUBSTANCE, but ⚠ the LABEL DIFFERS from corporate 336 ('Film "
              "production labor rebate'). Three of the eight 'safe' shared codes (336, 338, 344) "
              "fail a naive string-equality reconciliation.")},
    {"code": 338, "kind": K_SUBTRACTION, "label": "Manufactured dwelling park capital gain exclusion",
     "collides": True,
     "note": ("NEAR-COLLISION - SAME statutory item, DIFFERENT label (corporate: 'Sale of "
              "manufactured dwelling park'). Counted in the 12.")},
    {"code": 341, "kind": K_SUBTRACTION, "label": "Income on a composite return",
     "collides": False,
     "note": ("SAFE SHARED. ⚠ Pub. OR-CODES lists 341 for OR-40-N and OR-40-P ONLY - correctly, "
              "since composite joiners are nonresidents. Its corporate twin is directed by Pub. "
              "OR-OC to Schedule OR-ASC-CORP Section B and is ABSENT FROM APPENDIX A - the proof "
              "that Appendix A is an S-corp SUBSET of the OR-ASC-CORP universe."),
     "forms": ["OR-40-N", "OR-40-P"]},
    {"code": 344, "kind": K_SUBTRACTION, "label": "Manufactured dwelling park closure payments to tenants",
     "collides": True,
     "note": ("NEAR-COLLISION - SAME statutory item, DIFFERENT label (corporate: 'Manufactured "
              "dwelling park tenant payments'). Counted in the 12.")},
    {"code": 352, "kind": K_SUBTRACTION, "label": "DISC dividend payments",
     "collides": True,
     "note": "⚠ collides with corporate 352 (deferred gain from out-of-state disposition of property)"},
    {"code": 354, "kind": K_SUBTRACTION, "label": "Depreciation difference for Oregon",
     "collides": False, "note": "INDIVIDUAL ONLY - verified ABSENT from OR-20-S Appendix A"},
    {"code": 356, "kind": K_SUBTRACTION, "label": "Passive activity losses",
     "collides": True,
     "note": "⚠ collides with corporate 356 (gain or loss on sale of depreciable property)"},
    {"code": 358, "kind": K_SUBTRACTION, "label": "Basis of business assets transferred into Oregon",
     "collides": True, "note": "⚠ collides with corporate 358 (losses from outside U.S.)"},
    {"code": 359, "kind": K_SUBTRACTION, "label": "Marijuana business expenses",
     "collides": False,
     "note": ("INDIVIDUAL number for the ORS 317.363 IRC 280E modification. ⚠ The CORPORATE number "
              "for the SAME item is 375 - marijuana does NOT share a code across the namespaces, "
              "though psilocybin (385) does. A floor rule applies with no corporate analogue: the "
              "deduction 'can't be used to create a net operating loss. It can only reduce your "
              "Oregon source income to zero.'")},
    {"code": 361, "kind": K_SUBTRACTION,
     "label": "First-time home buyer savings account contributions and earnings",
     "collides": True,
     "note": ("⚠ collides with corporate 361 (interest on obligations from the federal return and "
              "its instrumentalities - INCOME FILERS ONLY)")},
    {"code": 384, "kind": K_SUBTRACTION, "label": "CPAR subtraction",
     "collides": False, "note": "SAFE SHARED - identical in both namespaces."},
    {"code": 385, "kind": K_SUBTRACTION, "label": "Psilocybin business expenses",
     "collides": False,
     "note": ("SAFE SHARED - identical in both namespaces. ⚠ Psilocybin happens to share 385 "
              "across both sets; marijuana does NOT (359 individual vs 375 corporate).")},
    {"code": 387, "kind": K_SUBTRACTION, "label": "PTE-E tax refund included on entity-level federal return",
     "collides": False,
     "note": ("SAFE SHARED - identical in both namespaces. Leg 3 of the three-leg PTE-E owner "
              "treatment: a member who reported the 167 addition in a prior year and reports a "
              "refund of that tax federally this year subtracts it here.")},
]

# Refundable credit -- Schedule OR-ASC Section F / OR-ASC-NP Section I.
# Kept OUT of the modification tables on purpose: it is a CREDIT, a different
# vocabulary, and folding it in would repeat the line-15 error the verification
# pass corrected on the corporate side.
OR_CODES_INDIVIDUAL_REFUNDABLE: list[dict] = [
    {"code": 900, "kind": K_CREDIT, "label": "Pass-through entity elective taxes paid",
     "prorated": False,
     "note": ("⚠⚠ NOT PRORATED FOR NONRESIDENTS OR PART-YEAR RESIDENTS. Pub. OR-CODES p. 5 marks "
              "several refundable credits 'PR' (must be prorated) - 895, 896, 897, 898, 901 - but "
              "900 is plain 'X' on OR-40, OR-40-N AND OR-40-P. A NONRESIDENT MEMBER GETS THE FULL "
              "CREDIT. Applying the generic nonresident proration to code 900 UNDERSTATES every "
              "nonresident member's refund. Leg 2 of the three-leg owner treatment. ⚠ There is NO "
              "corporate analogue - the PTE-E credit is delivered exclusively to INDIVIDUAL "
              "members (verified negative N10)."),
     "forms": ["OR-40", "OR-40-N", "OR-40-P"]},
]

# ---------------------------------------------------------------------------
# CORPORATE namespace -- Schedule OR-ASC-CORP, seeded from the FULL OR-ASC-CORP
# universe (⚠ NOT from Appendix A, which is the S-corp SUBSET). `appendix_a`
# is the OR-20-S eligibility filter that rides on top.
# `income_filers_only` carries the DOR's own checkbox-driven eligibility rule --
# codes 361 and 364 are available only when the page-1 `Income tax` box is
# checked, never on an excise return. That is exactly the kind of rule a generic
# code-list seeding pass drops on the floor.
# Used by: Form OR-20-S LINES 2 AND 3 ONLY.
# ---------------------------------------------------------------------------
OR_ASC_CORP_CODES: list[dict] = [
    # ---- Section A: Additions ---------------------------------------------
    {"code": 118, "kind": K_ADDITION, "label": "Deferred gain from out-of-state disposition of property",
     "statute": "ORS 317.327", "appendix_a": True, "collides": True},
    {"code": 132, "kind": K_ADDITION, "label": "Charitable donations not allowed for Oregon",
     "statute": "ORS 317.491", "appendix_a": True, "collides": True},
    {"code": 150, "kind": K_ADDITION,
     "label": "Interest income excluded from the federal return (state, municipal, and other interest income)",
     "statute": "ORS 317.309", "appendix_a": True, "collides": True},
    {"code": 151, "kind": K_ADDITION, "label": "Oregon excise tax and other tax",
     "statute": "ORS 317.314", "appendix_a": True, "collides": True,
     "note": ("⚠ Carries the ONLY mention of the Portland-metro local taxes anywhere in the Oregon "
              "corporate instructions, and it runs the OTHER way: 'the Oregon minimum tax and local "
              "taxes, such as the Multnomah County Business Income tax, ARE DEDUCTIBLE, and aren't "
              "required to be added back' (ORS 317.314). ORS 317.314(1) adds back taxes on or "
              "measured by net income imposed by a foreign country, this state or any state; (2) "
              "SUBTRACTS taxes and license fees imposed by counties, cities and other political "
              "subdivisions. Instruction and statute agree; the direction is correct as printed.")},
    {"code": 158, "kind": K_ADDITION, "label": "Gain or loss on disposition of depreciable property",
     "statute": "ORS 317.356", "appendix_a": True, "collides": True,
     "note": ("⚠⚠ THE EXEMPLAR COLLISION. Individual 158 is 'Interest and dividends on government "
              "bonds of other states'. The individual number for THIS item is 154.")},
    {"code": 159, "kind": K_ADDITION, "label": "Income from sources outside U.S.",
     "statute": "ORS 317.625; IRC secs. 861-864, 862", "appendix_a": True, "collides": True},
    {"code": 167, "kind": K_ADDITION, "label": "PTE-E tax deducted on entity-level federal return",
     "statute": "Form OR-21 Instructions / Publication OR-17", "appendix_a": True, "collides": False,
     "note": ("SAFE SHARED. ⚠ This is the TIERED case only - this S corporation is a member of a "
              "DIFFERENT electing PTE. The electing entity's OWN PTE-E addition goes on Schedule SM "
              "line 3 as a named 'other addition', NOT here. TWO different schedules for two "
              "different PTE-E addition scenarios on the same form.")},
    {"code": 174, "kind": K_ADDITION, "label": "Depreciation differences",
     "statute": "ORS 317.301", "appendix_a": True, "collides": False,
     "note": ("CORPORATE ONLY - verified ABSENT from Pub. OR-CODES. ⚠ For TY2025 this line stays "
              "EMPTY for new assets: ORS 317.301's window is CLOSED (2011 c.7 sec. 31: tax years "
              "beginning on or after 1/1/2009 and before 1/1/2011). The only TY2025 population is "
              "legacy - 2009/2010 assets still unwinding, property transferred into Oregon, "
              "pre-1985 credit-basis differences and unaligned 1981-1985 ACRS assets.")},
    {"code": 187, "kind": K_ADDITION, "label": "CPAR addition",
     "statute": "ORS 314.733", "appendix_a": True, "collides": False, "note": "SAFE SHARED."},
    {"code": 199, "kind": K_ADDITION, "label": "Uncategorized addition (must include explanation)",
     "statute": None, "appendix_a": True, "collides": False, "note": "CORPORATE ONLY."},
    # ---- Section B: Subtractions ------------------------------------------
    {"code": 336, "kind": K_SUBTRACTION, "label": "Film production labor rebate",
     "statute": "ORS 317.394", "appendix_a": True, "collides": False,
     "note": "SAFE SHARED in substance; ⚠ the individual LABEL differs (adds '-Greenlight Oregon Labor Rebate Fund')."},
    {"code": 338, "kind": K_SUBTRACTION, "label": "Sale of manufactured dwelling park",
     "statute": "note following ORS 317.401", "appendix_a": True, "collides": True,
     "note": "NEAR-COLLISION - same item, different label."},
    {"code": 341, "kind": K_SUBTRACTION, "label": "Income on a composite return",
     "statute": "ORS 314.778", "appendix_a": False, "collides": False,
     "note": ("⚠⚠ THE PROOF THAT APPENDIX A IS A SUBSET. Pub. OR-OC directs a CORPORATE composite "
              "owner to subtract its 'Share of Oregon-source distributive income' on Schedule "
              "OR-ASC-CORP Section B using code 341 - yet 341 APPEARS NOWHERE IN APPENDIX A "
              "(re-checked positionally 2026-08-19). Seeding Appendix A as the whole corporate "
              "table would fail a legitimate corporate composite subtraction. `appendix_a` is "
              "False so the OR-20-S eligibility filter still excludes it from an OR-20-S return.")},
    {"code": 344, "kind": K_SUBTRACTION, "label": "Manufactured dwelling park tenant payments",
     "statute": "ORS 317.092; ORS 90.505-90.840", "appendix_a": True, "collides": True,
     "note": "NEAR-COLLISION - same item, different label."},
    {"code": 352, "kind": K_SUBTRACTION, "label": "Deferred gain from out-of-state disposition of property",
     "statute": "ORS 317.327", "appendix_a": True, "collides": True},
    {"code": 353, "kind": K_SUBTRACTION, "label": "Depreciation differences",
     "statute": "ORS 317.301", "appendix_a": True, "collides": False,
     "note": "CORPORATE ONLY - verified ABSENT from Pub. OR-CODES. Same closed-window caveat as 174."},
    {"code": 356, "kind": K_SUBTRACTION, "label": "Gain or loss on sale of depreciable property",
     "statute": "ORS 317.356; OAR 150-317-0420", "appendix_a": True, "collides": True},
    {"code": 358, "kind": K_SUBTRACTION, "label": "Losses from outside U.S.",
     "statute": "ORS 317.625", "appendix_a": True, "collides": True},
    {"code": 361, "kind": K_SUBTRACTION,
     "label": "Interest on obligations from the federal return and its instrumentalities (income filers only)",
     "statute": None, "appendix_a": True, "collides": True, "income_filers_only": True,
     "note": "⚠ Available ONLY when the page-1 `Income tax` box is checked. A checkbox-driven code-eligibility rule."},
    {"code": 364, "kind": K_SUBTRACTION, "label": "State of Oregon interest income (income filers only)",
     "statute": None, "appendix_a": True, "collides": False, "income_filers_only": True,
     "note": "CORPORATE ONLY - verified ABSENT from Pub. OR-CODES. ⚠ Income filers only."},
    {"code": 375, "kind": K_SUBTRACTION, "label": "Marijuana business expenses",
     "statute": "ORS 317.363", "appendix_a": True, "collides": False,
     "note": ("CORPORATE ONLY - verified ABSENT from Pub. OR-CODES. ⚠ The INDIVIDUAL number for the "
              "same item is 359. Marijuana does NOT share a code across the namespaces.")},
    {"code": 384, "kind": K_SUBTRACTION, "label": "CPAR subtraction",
     "statute": "ORS 314.733", "appendix_a": True, "collides": False, "note": "SAFE SHARED."},
    {"code": 385, "kind": K_SUBTRACTION, "label": "Psilocybin business expenses",
     "statute": "ORS 317.363", "appendix_a": True, "collides": False, "note": "SAFE SHARED."},
    {"code": 387, "kind": K_SUBTRACTION, "label": "PTE-E tax refund included on entity-level federal return",
     "statute": "ORS 305.100", "appendix_a": True, "collides": False, "note": "SAFE SHARED."},
    {"code": 399, "kind": K_SUBTRACTION, "label": "Uncategorized subtraction (must include explanation)",
     "statute": None, "appendix_a": True, "collides": False, "note": "CORPORATE ONLY."},
]

# ---------------------------------------------------------------------------
# THE THIRD TABLE -- Schedule OR-ASC-CORP Section D carryforward credits, the
# 8xx / 999 series. ⚠ NOT part of the collision hazard: it shares no number with
# the 1xx/3xx modification codes. Line 15 was WRONGLY included in the earlier
# "corporate table only" rule; the verification pass removed it (brief §18.3(g)).
#
# ⚠ THE DOR'S OWN GATE RIDES ON THIS TABLE, verbatim from the OR-20-S
# instructions: "These credits can apply to tax on recognized built-in gains
# only." An OR-20-S with no recognized built-in gains may not populate line 15
# at all. Appendix A also prints "Standard credits: None" for the S corp.
# ---------------------------------------------------------------------------
OR_ASC_CORP_CREDIT_CODES: list[dict] = [
    {"code": 835, "label": "Agricultural workforce housing", "statute": "ORS 315.164"},
    {"code": 839, "label": "Business energy", "statute": "ORS 315.354"},
    {"code": 841, "label": "Child Care Fund contributions", "statute": "ORS 315.213"},
    {"code": 843, "label": "Crop donation", "statute": "ORS 315.156",
     "note": "⚠ The credit percentage is raised to 25% for tax years beginning on or after 1/1/2025 (HB 2087, 2025) - the ONLY TY2025 computation change in the OR-20-S 'What's new' block."},
    {"code": 846, "label": "Employer-provided dependent care assistance", "statute": "ORS 315.204"},
    {"code": 847, "label": "Employer scholarship", "statute": "ORS 315.237"},
    {"code": 848, "label": "Lender's credit: energy conservation", "statute": "ORS 317.112"},
    {"code": 849, "label": "Energy conservation projects", "statute": "ORS 315.331"},
    {"code": 850, "label": "Fish screening devices", "statute": "ORS 315.138"},
    {"code": 852, "label": "Individual Development Account (IDA) donation", "statute": "ORS 315.271"},
    {"code": 853, "label": "Long-term enterprise zone facilities", "statute": "ORS 317.124"},
    {"code": 854, "label": "Oregon affordable housing lender's credit", "statute": "ORS 317.097",
     "note": "⚠ HB 2087 / HB 3589 (2025) changes are TY2026 - do NOT encode them into a TY2025 spec."},
    {"code": 855, "label": "Oregon Low-Income Community Jobs Initiative", "statute": "ORS 315.533"},
    {"code": 856, "label": "Oregon production investment fund (auction)", "statute": "ORS 315.514"},
    {"code": 860, "label": "Renewable energy resource equipment manufacturing facility", "statute": "ORS 315.341"},
    {"code": 863, "label": "Transportation projects", "statute": "ORS 315.336"},
    {"code": 864, "label": "University venture fund", "statute": "ORS 315.640"},
    {"code": 866, "label": "Weatherization lender's credit", "statute": "ORS 317.111"},
    {"code": 868, "label": "Rural technology workforce development", "statute": "ORS 315.523"},
    {"code": 869, "label": "Bovine manure", "statute": "ORS 315.176"},
    {"code": 871, "label": "Opportunity Grant Fund (auction)", "statute": "ORS 315.643"},
    {"code": 872, "label": "Short line railroad rehabilitation", "statute": "ORS 315.593"},
    {"code": 873, "label": "Forest Conservation Tax Credit (FCTC)", "statute": "ORS 315.124"},
    {"code": 874, "label": "Research and development for semiconductor companies (non-refundable)",
     "statute": "ORS 315.518 to 315.522",
     "note": "HB 2095 (2025) deleted the reference to the alternative incremental credit at IRC 41(c)(4) - a federal cross-reference cleanup, not a TY2025 computation change."},
    {"code": 875, "label": "Publicly supported housing sale", "statute": "ORS 315.283"},
    {"code": 999, "label": "Uncategorized carryforward credit (must include explanation)", "statute": None},
]

OR_ASC_CORP_CREDIT_GATE = (
    "THE DOR'S OWN GATE, verbatim: 'These credits can apply to tax on recognized built-in gains "
    "only.' - so an OR-20-S with no recognized built-in gains may not populate line 15 at all. "
    "OR-20-S Instructions, verbatim: 'Only credits carried forward from C corporation years are "
    "allowed on the S corporation return.' / 'No credits are allowed to offset the tax on excess "
    "net passive income or minimum tax, unless specified by statute. Credit carryforwards are only "
    "allowed to offset the tax on built-in gains [ORS 314.766(5)].' Appendix A prints 'Standard "
    "credits: None'."
)

# ---------------------------------------------------------------------------
# THE COLLISION LEDGER. Derived, not asserted -- `or_code_collisions()` recomputes
# it from the two tables so the count is auditable and cannot drift.
# ---------------------------------------------------------------------------
# Same number, DIFFERENT item. TEN.
OR_SEMANTIC_COLLISIONS = (118, 132, 150, 151, 158, 159, 352, 356, 358, 361)
# Same item, DIFFERENT label. TWO. Safe in substance, fatal to a string-equality test.
OR_LABEL_ONLY_COLLISIONS = (338, 344)
# 10 + 2 = 12 shared numbers whose labels are not identical.
OR_COLLIDING_CODES = OR_SEMANTIC_COLLISIONS + OR_LABEL_ONLY_COLLISIONS
OR_COLLISION_COUNT = 12
# Identical in BOTH sets -- safe to share. ⚠ 336's LABELS differ even so, so
# THREE of the eight safe shared codes (336, 338, 344) fail naive string equality.
OR_SAFE_SHARED_CODES = (167, 187, 336, 384, 385, 387)
# ⚠ 341 is shared and SAFE, and it does NOT change the count of 12: the 12 counts
# shared numbers with NON-IDENTICAL labels, and 341's labels agree. It is listed
# separately because it only becomes shared once the corporate table is seeded
# from the FULL OR-ASC-CORP universe rather than from Appendix A.
OR_SAFE_SHARED_BEYOND_APPENDIX_A = (341,)
# The seven verified `(not used)` markers -- absences, re-verified positionally.
OR_CODES_INDIVIDUAL_ONLY = (152, 153, 354)      # confirmed ABSENT from Appendix A
OR_CODES_CORPORATE_ONLY = (174, 353, 364, 375)  # confirmed ABSENT from Pub. OR-CODES

# WHICH CONTEXT MAY DRAW FROM WHICH TABLE. This is the whole of C1 in one dict.
OR_CONTEXT_NAMESPACE: dict[str, str] = {
    "OR65_SCHEDULE_I": NS_INDIVIDUAL,
    "OR_K1_LINES_14_18": NS_INDIVIDUAL,
    # ⚠⚠ THE CROSSING POINT. Individual codes even when the issuing PTE is an S
    # corporation filing OR-20-S with corporate codes on its own lines 2/3.
    "OR_K1_OVERFLOW_ATTACHMENT": NS_INDIVIDUAL,
    "OWNER_SCHEDULE_OR_ASC": NS_INDIVIDUAL,
    "OWNER_SCHEDULE_OR_ASC_NP": NS_INDIVIDUAL,
    "OR20S_LINE_2": NS_CORPORATE,
    "OR20S_LINE_3": NS_CORPORATE,
    "OR20S_LINE_15": NS_CORP_CREDIT,   # a CREDIT line - NOT part of the collision hazard
    "CORPORATE_COMPOSITE_OWNER_ASC_CORP_B": NS_CORPORATE,
}

# Schedule SM is NOT in that map, on purpose, and that is the point of the decoy.
OR_SCHEDULE_SM_IS_CODE_FREE = True
OR_SCHEDULE_SM_DECOY_NOTE = (
    "⚠⚠ THE DECOY. Two FINAL TY2025 DOR notes firewall Schedule SM - Sch. OR-ASC-CORP Instr. "
    "150-102-033-1 p. 1 ('Note for OR-20-S filers: This schedule and these codes are not for "
    "additions or subtractions on Schedule SM.') and OR-20-S Instr. 150-102-025-1 p. 12 ('Note: "
    "Don't use Schedule OR-ASC-CORP codes for Schedule SM additions and subtractions.'). BOTH ARE "
    "TRUE AND BOTH ARE IRRELEVANT: Schedule SM is a code-free, fixed-named-line schedule and "
    "nobody claimed it carries codes. They police Schedule SM and say NOTHING about the place the "
    "namespaces genuinely meet - the Schedule OR-K-1 overflow attachment. A verification pass was "
    "fooled by exactly this, refuted the crossing point, and RETRACTED the refutation. Do not let "
    "these two notes talk you out of the guard."
)


# ═══════════════════════════════════════════════════════════════════════════
# C1 -- THE LOOKUP HELPERS AND THE HARD CROSS-USE GUARD
# ═══════════════════════════════════════════════════════════════════════════

_OR_TABLES: dict[str, list] = {
    NS_INDIVIDUAL: OR_CODES_INDIVIDUAL,
    NS_CORPORATE: OR_ASC_CORP_CODES,
    NS_CORP_CREDIT: OR_ASC_CORP_CREDIT_CODES,
}


def or_code(namespace: str, code: int, kind: str | None = None) -> dict:
    """Resolve a modification/credit code WITHIN a named namespace.

    ⚠ There is no namespace default and there never will be. Twelve Oregon code
    numbers collide; the worst of them (158) posts a depreciation-basis
    difference onto a municipal-interest line while the return still foots.
    Passing `None` raises.
    """
    if namespace not in _OR_TABLES:
        raise OregonCodeNamespaceError(
            f"Oregon modification codes are NAMESPACED and a bare code number is meaningless. "
            f"Got namespace={namespace!r}; expected one of {NAMESPACES}. "
            f"Twelve numbers collide between the individual (Publication OR-CODES) and corporate "
            f"(Schedule OR-ASC-CORP) sets: {OR_COLLIDING_CODES}."
        )
    rows = [r for r in _OR_TABLES[namespace] if r["code"] == code and (kind is None or r["kind"] == kind)]
    if not rows:
        raise KeyError(f"code {code} (kind={kind}) is not in the {namespace} table")
    if len(rows) > 1:
        raise KeyError(f"code {code} is ambiguous in {namespace} without a `kind`")
    return rows[0]


def or_code_by_label(namespace: str, label: str, kind: str | None = None) -> dict:
    """Resolve by LABEL. ⚠ THE PREFERRED MAPPER.

    A label-driven mapper survives the 158/154 crossing; a number-driven one
    fails silently. Matching is case-insensitive and whitespace-normalised
    because three of the eight 'safe' shared codes (336, 338, 344) carry
    different label STRINGS for the same statutory item across the namespaces.
    """
    if namespace not in _OR_TABLES:
        raise OregonCodeNamespaceError(
            f"or_code_by_label requires a namespace; got {namespace!r}. Expected {NAMESPACES}."
        )
    want = " ".join(label.lower().split())
    rows = [r for r in _OR_TABLES[namespace]
            if " ".join(r["label"].lower().split()) == want and (kind is None or r["kind"] == kind)]
    if not rows:
        raise KeyError(f"label {label!r} (kind={kind}) is not in the {namespace} table")
    return rows[0]


def or_assert_namespace(context: str, namespace: str) -> str:
    """⚠ THE HARD CROSS-USE GUARD. Raises on any cross-namespace use.

    `context` is a place on a return, not a form: OR-20-S runs CORPORATE codes on
    its own lines 2 and 3 and simultaneously emits INDIVIDUAL codes on the
    Schedule OR-K-1 overflow attachment it hands each shareholder. Both
    namespaces are live inside ONE engagement, so the guard keys off the
    context, never off the form.
    """
    if context not in OR_CONTEXT_NAMESPACE:
        raise OregonCodeNamespaceError(
            f"unknown code context {context!r}; known contexts: {sorted(OR_CONTEXT_NAMESPACE)}"
        )
    expected = OR_CONTEXT_NAMESPACE[context]
    if namespace != expected:
        raise OregonCodeNamespaceError(
            f"CROSS-NAMESPACE USE REFUSED: context {context!r} takes {expected!r} codes, got "
            f"{namespace!r}. Twelve numbers collide ({OR_COLLIDING_CODES}); code 158 alone means "
            f"'gain or loss on disposition of depreciable property' (corporate) vs 'interest and "
            f"dividends on government bonds of other states' (individual), and mixing them posts a "
            f"depreciation-basis difference onto a municipal-interest line WITHOUT breaking the "
            f"return's arithmetic. The two DOR 'don't use these codes on Schedule SM' notes do NOT "
            f"cover this - they police Schedule SM, not the Schedule OR-K-1 overflow attachment."
        )
    return expected


def or_resolve_in_context(context: str, namespace: str, *, code: int | None = None,
                          label: str | None = None, kind: str | None = None) -> dict:
    """Namespace-checked resolution. The only sanctioned entry point for the app."""
    or_assert_namespace(context, namespace)
    if label is not None:
        return or_code_by_label(namespace, label, kind)
    if code is None:
        raise OregonCodeNamespaceError("supply either `label` (preferred) or `code`")
    return or_code(namespace, code, kind)


def or_code_collisions() -> dict:
    """Recompute the collision ledger from the two tables. Derived, not asserted."""
    ind = {(r["code"], r["kind"]): r["label"] for r in OR_CODES_INDIVIDUAL}
    corp = {(r["code"], r["kind"]): r["label"] for r in OR_ASC_CORP_CODES}
    shared = sorted({c for c, _ in ind} & {c for c, _ in corp})
    semantic, label_only, identical = [], [], []
    for c in shared:
        i_rows = {k: v for k, v in ind.items() if k[0] == c}
        c_rows = {k: v for k, v in corp.items() if k[0] == c}
        for key, i_label in i_rows.items():
            if key not in c_rows:
                continue
            c_label = c_rows[key]
            if i_label == c_label:
                identical.append(c)
            elif c in OR_LABEL_ONLY_COLLISIONS or c in OR_SAFE_SHARED_CODES \
                    or c in OR_SAFE_SHARED_BEYOND_APPENDIX_A:
                label_only.append(c)
            else:
                semantic.append(c)
    return {
        "shared": shared,
        "semantic_collisions": sorted(set(semantic)),
        "label_only_or_safe_shared": sorted(set(label_only)),
        "identical_labels": sorted(set(identical)),
    }


def or_code_is_ambiguous_without_namespace(code: int) -> bool:
    """True for any of the twelve numbers that cannot be resolved without a namespace."""
    return code in OR_COLLIDING_CODES


def or_appendix_a_codes() -> list[int]:
    """The OR-20-S ELIGIBILITY FILTER over the full OR-ASC-CORP universe."""
    return sorted(r["code"] for r in OR_ASC_CORP_CODES if r.get("appendix_a", True))


def or_corporate_code_allowed_on_or20s(code: int, tax_basis: str) -> bool:
    """OR-20-S line 2/3 eligibility: Appendix A membership AND the income-filer gate."""
    rows = [r for r in OR_ASC_CORP_CODES if r["code"] == code]
    if not rows:
        return False
    row = rows[0]
    if not row.get("appendix_a", True):
        return False
    if row.get("income_filers_only") and tax_basis != "income":
        return False
    return True


# ═══════════════════════════════════════════════════════════════════════════
# THE SIX FINAL-BOOKLET INSTRUCTION DEFECTS (D-12 W2: the printed face governs;
# instruction conflicts are LOGGED, never silently corrected)
# ═══════════════════════════════════════════════════════════════════════════
OR_INSTRUCTION_DEFECTS: list[dict] = [
    {"id": "OR-DEF-1", "form": FORM_CODE_OR20S, "where": "Question J (Instr. p. 8)",
     "printed": "Enter ordinary business income or loss from federal Form 1120-S, line 21.",
     "correct": "2025 Form 1120-S line 22 (line 21 is 'Total deductions. Add lines 7 through 20').",
     "resolution": "BUILD TO THE LABEL, not the DOR pointer.",
     "note": ("⚠ STALE BY THREE FORM YEARS, not two. The Form 7205 line was inserted for TY2023, "
              "not TY2024: ordinary business income sat at line 21 on the 2021 and 2022 forms and "
              "at line 22 on the 2023, 2024 and 2025 forms. Question J read 'line 21' in the TY2022 "
              "booklet (Rev. 10-28-22) where it was CORRECT, and unchanged in TY2023 (Rev. "
              "07-19-24), TY2024 (Rev. 10-14-24) and TY2025 (Rev. 10-14-25). The TY2023 booklet was "
              "re-revised in July 2024 and still not fixed. CONSEQUENCE: TY2023 and TY2024 Oregon "
              "builds carried the same defect. ✅ The IRS's own cross-reference settles it without "
              "line-counting - 2025 Schedule K line 1 reads '(page 1, line 22)' on the 1120-S and "
              "'(page 1, line 23)' on the 1065. The SAME BOOKLET three paragraphs later correctly "
              "uses 2025 numbering for line 1(b) ('Worksheet for line 23a'), so the booklet is "
              "internally inconsistent. U3.")},
    {"id": "OR-DEF-2", "form": FORM_CODE_OR20S, "where": "Schedule ES total (Instr. p. 11)",
     "printed": "Total. On line 7, enter the total of lines 1 through 6, then carry total to Form OR-20-S, line 19.",
     "correct": "The face prints '7. Reserved' and '8. Total prepayments (carry to line 19 above)'.",
     "resolution": "THE FACE WINS: total on LINE 8.",
     "note": ("⚠ 'Schedule ES line 7 = Reserved' is a live landmine. On Form OR-20 and OR-20-INC "
              "that same line carries REFUNDABLE credits. A shared corporate-series component "
              "mapping 'ASC-CORP E5 -> Schedule ES line 7' writes a refundable credit into a dead "
              "box on the S-corp return AND THE ARITHMETIC STILL FOOTS. U4.")},
    {"id": "OR-DEF-3", "form": FORM_CODE_OR20S, "where": "Line 4 arithmetic (Instr. p. 10)",
     "printed": "line 1 plus line 2, minus line 3",
     "correct": "The face prints 'line 1c plus line 2, minus line 3'; 1c is the total of 1a + 1b.",
     "resolution": "THE FACE WINS.", "note": "Third loose pointer in one booklet."},
    {"id": "OR-DEF-4", "form": FORM_CODE_OR20S, "where": "Form OR-24 DOR number (Instr. p. 7)",
     "printed": "150-800-734",
     "correct": "150-101-734 - per the form face and the DOR forms index.",
     "resolution": "Use 150-101-734.", "note": "A typo in the FINAL booklet."},
    {"id": "OR-DEF-5", "form": FORM_CODE_OR21, "where": "Line 21 (Instr. p. 4)",
     "printed": ("Enter the total of the non-apportionable income from line 17 that is allocated to "
                 "Oregon. If the PTE does all of its business activity in Oregon, enter the amount "
                 "from line 19. If the PTE must apportion its income, see 'Allocable income' in "
                 "Schedule OR-21-AP Instructions to determine whether the amount on line 19 "
                 "includes income that is allocated to Oregon."),
     "correct": "Both 'line 19' references resolve to LINE 17.",
     "resolution": "BUILD TO LINE 17. Do NOT seed the DOR's literal text.",
     "note": ("⚠ Line 19 is a four-decimal PERCENTAGE; line 21 is a dollar field feeding "
              "'line 22 = line 20 + line 21'. The DOR's literal text puts a percentage into a "
              "dollar field. The defect occurs TWICE in one paragraph while the paragraph's own "
              "opening sentence says 'line 17' - the signature of a stale renumbering, which "
              "RAISES confidence in the correction. Only line 17 closes: a wholly-in-Oregon PTE has "
              "L19 = 100.0000, L20 = L18, L21 = L17, so L22 = L18 + L17 = L16. U2.")},
    {"id": "OR-DEF-6", "form": FORM_CODE_OR21, "where": "Paper filing (Instr. p. 5 vs the DOR PTE-E program page)",
     "printed": "File Form OR-21 by mail only if you requested a paper return because you don't have internet access.",
     "correct": ("The DOR PTE-E Tax program page says the opposite: 'Paper returns will not be "
                 "accepted' and 'We will not be releasing the OR-21 in paper form.'"),
     "resolution": "WORKING POSITION: treat a paper Form OR-21 as UNAVAILABLE; route the no-internet case to the DOR exception mailbox.",
     "note": ("⚠⚠ THE COROLLARY BITES HERE. The 'printed face governs' rule CANNOT resolve this "
              "one, because FORM OR-21 HAS NO FACE. Both sources re-fetched 2026-08-19; they cannot "
              "both be operative. U23 - RED-DEFERred pending the DOR developers' handbook.")},
]

# ⚠ THE PROVENANCE STAMP that rides on every OR-21 line. The 'face governs' rule
# has no subject on this form.
OR21_PROVENANCE = (
    "⚠ PROVENANCE: read off WORKSHEET OR-21 inside 2025 Form OR-21 Instructions 150-107-114-1 "
    "(Rev. 04-01-26 ver. 01) p. 10, stamped verbatim 'This worksheet is for informational purposes "
    "only. Do not file this worksheet.' THE DOR HAS NEVER PUBLISHED A FORM OR-21 FACE, IN ANY YEAR "
    "- established by enumeration (FormsPubs SharePoint list, 1,712 items, __next = null; "
    "150-107-114/-112/-111/-110 appear zero times in any year while 150-107-113 appears as a real "
    "face in 2022-2025; AcroForm widget counts 0/0/0/0 vs 23 on the OR-21-K-1 face). Whether these "
    "worksheet line numbers are the MeF schema's line numbers is an INFERENCE (U1). The campaign's "
    "'printed face governs' convention (D-12 W2) CANNOT apply to this form."
)


def or21_line_provenance() -> str:
    """The single sanctioned statement of Form OR-21's line-number provenance."""
    return OR21_PROVENANCE


# ═══════════════════════════════════════════════════════════════════════════
# FORM OR-65 -- constants and computation
# Form OR-65 is an INFORMATION RETURN with a flat $150 bolted on. There is no
# income line, no apportionment line and no taxable-income line anywhere on it.
# ORS 314.712(1): 'a partnership as such is not subject to the tax imposed by
# ORS chapter 316, 317 or 318.'
# ═══════════════════════════════════════════════════════════════════════════

OR65_MINIMUM_TAX: dict[int, int] = {2025: 150}          # ORS 314.725
OR65_FTF_PER_PARTNER_PER_MONTH: dict[int, int] = {2025: 50}   # ORS 314.724(3)
OR65_FTF_MAX_MONTHS: dict[int, int] = {2025: 5}
OR65_LATE_PAY_PENALTY_PCT: dict[int, str] = {2025: "0.05"}
OR65_K1_SUMMARY_THRESHOLD: dict[int, int] = {2025: 11}  # >= 11 partners => summary
OR65_ESTIMATES_REQUIRED: dict[int, bool] = {2025: False}
# ⚠ D-12 W6 -- OR-65 does NOT self-assess. The face has NO penalty or interest
# line at all (its tax block is 3A-3D) and the instructions say, verbatim:
# 'Don't submit a penalty payment with the return. Penalty payments are only
# required if the department assesses a penalty.' The OPPOSITE of OR-20-S.
OR65_SELF_ASSESSES_PENALTY: dict[int, bool] = {2025: False}

# ⚠ THE PUBLISHED 12-ROW PRORATION TABLE. NOT round(150 * n / 12).
# Every half-dollar rounds UP. Banker's rounding gives $12/$62/$112/$138 and is
# WRONG ON FIVE OF THE TWELVE ROWS. Seeded literally.
OR65_PRORATION_TABLE: dict[int, dict[int, int]] = {
    2025: {1: 13, 2: 25, 3: 38, 4: 50, 5: 63, 6: 75,
           7: 88, 8: 100, 9: 113, 10: 125, 11: 138, 12: 150},
}
# ⚠ The switch is checkbox (e) `Accounting period change`, NOT `Short-year return`.
OR65_PRORATION_TRIGGER = "checkbox (e) Accounting period change"
OR65_PRORATION_EXCLUSION = (
    "Instr. p. 2, verbatim: 'Important: This chart doesn't apply to other short tax year returns, "
    "such as initial returns or final returns. The tax is $150 in those cases.'"
)


def or65_must_file(q2a_oregon_source_income: bool, q2b_oregon_resident_partners: bool) -> bool:
    """FILING gate. ORS 314.724(1). Instr.: 'If you answered "Yes" to 2A or 2B (or both), you must file.'"""
    return bool(q2a_oregon_source_income or q2b_oregon_resident_partners)


def or65_owes_minimum_tax(q1a_doing_business: bool, q2a_oregon_source_income: bool,
                          q2b_oregon_resident_partners: bool) -> bool:
    """TAX gate -- a DIFFERENT boolean from the filing gate.

    ⚠ Face, line 3A verbatim: 'Did you answer yes to question 1 and question 2A
    and/or 2B? If yes, enter $150; if no, enter 0.'
    A partnership with Oregon RESIDENT PARTNERS but NO Oregon business activity
    FILES AND OWES NOTHING. Collapsing the two gates bills $150 to every
    out-of-state partnership that happens to have one Oregon partner.
    Corroborated by Instr. p. 1: 'If the partnership is registered to do business
    in Oregon, but didn't have any business activity, it's not subject to the
    minimum tax.'
    """
    return bool(q1a_doing_business and (q2a_oregon_source_income or q2b_oregon_resident_partners))


def or65_line_3a(q1a: bool, q2a: bool, q2b: bool, *, accounting_period_change: bool = False,
                 months_in_short_period: int | None = None, year: int = FORM_TAX_YEAR) -> int:
    """Form OR-65 line 3A. The ENTIRE tax computation on the form."""
    if not or65_owes_minimum_tax(q1a, q2a, q2b):
        return 0
    if not accounting_period_change:
        return _yk(OR65_MINIMUM_TAX, year)
    table = _yk(OR65_PRORATION_TABLE, year)
    if months_in_short_period not in table:
        raise ValueError(
            f"months_in_short_period must be 1-12 when checkbox (e) is set; got "
            f"{months_in_short_period!r}. The DOR publishes an ENUMERATED 12-row chart, not a "
            f"formula - do not extrapolate."
        )
    return table[months_in_short_period]


def or65_line_3(l3a: int, l3b_payments: float) -> dict:
    """Lines 3C (tax due) and 3D (refund). Mutually exclusive by construction."""
    l3c = max(0.0, float(l3a) - float(l3b_payments))
    l3d = max(0.0, float(l3b_payments) - float(l3a))
    return {"L3A": float(l3a), "L3B": float(l3b_payments), "L3C": l3c, "L3D": l3d}


def or65_failure_to_file_penalty(partners_at_any_time: int, months_late: int,
                                 year: int = FORM_TAX_YEAR) -> float:
    """ORS 314.724(3). $50 x partners x months, capped at FIVE months.

    ⚠ The statutory measure is 'the number of persons who were partners in the
    partnership DURING ANY PART OF the taxable year' - a HIGHER count than
    year-end partners, and higher than the line 4D K-1 count in a year with
    mid-year departures.
    ⚠ AND IT IS NOT PUT ON THE RETURN: 'Don't submit a penalty payment with the
    return.' This function exists to ESTIMATE exposure for the preparer, never to
    populate a line - Form OR-65 has no penalty line to populate.
    """
    capped = min(int(months_late), _yk(OR65_FTF_MAX_MONTHS, year))
    return float(_yk(OR65_FTF_PER_PARTNER_PER_MONTH, year) * int(partners_at_any_time) * max(0, capped))


def or65_k1_delivery(partner_count: int, year: int = FORM_TAX_YEAR) -> str:
    """>= 11 partners => a summary; <= 10 => attach the federal K-1s.

    The OR-65 instructions state BOTH halves ('fewer than 11 partners' / 'more
    than 10 partners'); the parallel OR-20-S rule states only the second half.
    SAME threshold, different phrasing - a shared component must not infer a
    different rule from the missing clause.
    """
    return "summary" if int(partner_count) >= _yk(OR65_K1_SUMMARY_THRESHOLD, year) else "attach_k1s"


# ═══════════════════════════════════════════════════════════════════════════
# FORM OR-20-S -- constants and computation
# ═══════════════════════════════════════════════════════════════════════════

TAX_BASIS_EXCISE = "excise"     # ORS ch. 317 - doing business in Oregon
TAX_BASIS_INCOME = "income"     # ORS ch. 318 - Oregon-source income, NOT doing business
TAX_BASES = (TAX_BASIS_EXCISE, TAX_BASIS_INCOME)

# ORS 317.061: 6.6% of the first $1,000,000, 7.6% above.
OR20S_RATE_LOW: dict[int, str] = {2025: "0.066"}
OR20S_RATE_HIGH: dict[int, str] = {2025: "0.076"}
OR20S_RATE_BREAKPOINT: dict[int, int] = {2025: 1_000_000}
OR20S_RATE_BASE_CONSTANT: dict[int, int] = {2025: 66_000}   # = 6.6% x $1,000,000

# ⚠ THE $150 AND THE ZERO HAVE DIFFERENT AUTHORITIES (verified negative #5).
OR20S_MINIMUM_TAX: dict[int, dict[str, int]] = {2025: {TAX_BASIS_EXCISE: 150, TAX_BASIS_INCOME: 0}}
OR20S_MIN_TAX_AUTHORITY_150 = "ORS 317.090(2)(b) - 'If a corporation is an S corporation, the minimum tax is $150.'"
OR20S_MIN_TAX_AUTHORITY_ZERO = (
    "⚠ NOT ORS 317.090. The zero follows from the PREDICATE of ORS 317.090(2) - 'Each corporation "
    "... filing a return under ORS 317.710 shall pay annually to the state, FOR THE PRIVILEGE OF "
    "CARRYING ON OR DOING BUSINESS BY IT WITHIN THIS STATE, a minimum tax as follows:' - which by "
    "its terms cannot reach a filer that is NOT doing business here. That filer is taxed instead "
    "under ORS 318.020(1), and ORS 318.031 pulls chapter 317 into chapter 318 only 'allowance "
    "being made for the difference in imposition of the taxes.' Cite 318.020 / 318.031 for the "
    "zero, keyed to the `Income tax` checkbox."
)
OR20S_MIN_TAX_NOT_APPORTIONABLE = (
    "ORS 317.090(3): the minimum tax 'is not apportionable (except in the case of a change of "
    "accounting periods), is payable in full for any part of the year during which a corporation "
    "is subject to tax and may not be reduced, paid or otherwise satisfied through the use of any "
    "tax credit.'"
)
# ⚠ A PRECISION POINT THE DOR'S OWN 'What's new' BLURS. HB 2339 (2025) lets the
# agricultural overtime credit offset ORS 317.090(2)(a) minimum tax - the
# TWELVE-TIER C-CORPORATION table. Subsection (2)(b), the flat $150 S-corp
# minimum, is NOT inside that exception. The credit does NOT offset an S corp's
# $150. (It does exist for individual owners as refundable code 901.)
OR20S_AG_OVERTIME_CREDIT_REACHES = "ORS 317.090(2)(a) only - NOT (2)(b), so it does not offset the S corp's $150"

# ⚠ OR-20-S states proration as a bare FORMULA where OR-65 publishes a TABLE.
# D-12 W6: seed both as authored; DO NOT UNIFY.
OR20S_PRORATION_IS_FORMULA: dict[int, bool] = {2025: True}
OR20S_PRORATION_FORMULA = "$150 minimum tax x total months in the short period / 12"
OR20S_ROUNDING = "whole dollars, round-half-up ('$4,681.55 becomes $4,682; and $8,775.22 becomes $8,775')"

# ⚠ D-12 W6 -- OR-20-S SELF-ASSESSES on the face at lines 22/23/24. THE OPPOSITE
# OF OR-65. A shared 'Oregon penalty engine' across the two forms is impossible.
OR20S_SELF_ASSESSES_PENALTY: dict[int, bool] = {2025: True}
OR20S_PENALTY_FAILURE_TO_PAY_PCT: dict[int, str] = {2025: "0.05"}
OR20S_PENALTY_FAILURE_TO_FILE_PCT: dict[int, str] = {2025: "0.20"}   # if > 3 months late
OR20S_PENALTY_FAILURE_TO_FILE_MONTHS: dict[int, int] = {2025: 3}
OR20S_PENALTY_THREE_YEAR_PCT: dict[int, str] = {2025: "1.00"}        # 3 consecutive years
OR20S_EXTENSION_PAY_PCT: dict[int, str] = {2025: "0.90"}
# The 5% waiver test is a FIVE-WAY CONJUNCTION whose last two conditions are
# NOT KNOWABLE AT PREPARATION TIME. That is why D-12 W6 lands on direct-entry
# with a computed suggestion rather than an authoritative computation.
OR20S_FTP_EXCEPTION_CONDITIONS = (
    "valid federal or Oregon extension",
    "at least 90 percent of tax after credits paid by the ORIGINAL due date",
    "return filed within the extension period",
    "balance of tax paid when the return is filed",
    "interest on the balance paid when the return is filed or within 30 days of the bill",
)

# Interest is DAILY and the rate changes at the CALENDAR-YEAR boundary, so a
# balance paid late across 12/31/2025 needs a TWO-SEGMENT computation. The Form
# OR-21 underpayment worksheet models exactly this as a `Rate change` event on
# 01/01/2026 - evidence the DOR expects segmentation, not a blended rate.
OR_INTEREST_ANNUAL: dict[int, str] = {2024: "0.08", 2025: "0.09", 2026: "0.08"}
OR_INTEREST_DAILY: dict[int, str] = {2024: "0.000219", 2025: "0.000247", 2026: "0.000219"}
OR_INTEREST_DELINQUENCY_BUMP = "one-third of 1 percent per month (4 percent yearly) after 60 days unpaid"
# ⚠ NOTATION TRAP, same agency, same season: the OR-20-S table prints 0.0247% and
# 0.0219% (PERCENTS) while the OR-21 underpayment worksheet prints 0.000247 and
# 0.000219 (DECIMALS). Same numbers, two notations.

OR20S_EST_TAX_THRESHOLD: dict[int, int] = {2025: 500}
OR20S_EST_INCLUDES_MINIMUM_TAX: dict[int, bool] = {2025: True}
OR20S_HIGH_INCOME_THRESHOLD: dict[int, int] = {2025: 1_000_000}
OR20S_HIGH_INCOME_LOOKBACK_YEARS: dict[int, int] = {2025: 3}
OR20S_EST_QUARTER_MONTH_DAY: dict[int, list] = {2025: [(4, 15), (6, 15), (9, 15), (12, 15)]}
OR20S_SCHEDULE_ES_TOTAL_LINE = "8"       # THE FACE. The instructions say 7; line 7 is `Reserved`.
OR20S_SCHEDULE_ES_RESERVED_LINE = "7"
OR20S_K1_SUMMARY_THRESHOLD: dict[int, int] = {2025: 11}
OR20S_LIFO_INSTALLMENTS_TOTAL: dict[int, int] = {2025: 4}
OR20S_LIFO_INSTALLMENTS_ON_OR20S: dict[int, int] = {2025: 3}
OR20S_NOL_CARRYFORWARD_YEARS: dict[int, int] = {2025: 15}
OR20S_NOL_CARRYBACK_ALLOWED: dict[int, bool] = {2025: False}   # except ORS 317.346 farm
OR20S_AMENDED_NOTIFY_DAYS: dict[int, int] = {2025: 90}          # ORS 314.380


def or20s_minimum_tax(tax_basis: str, year: int = FORM_TAX_YEAR) -> int:
    """Line 11. $150 for an EXCISE filer; 0 for an INCOME filer.

    The excise/income checkbox is a REQUIRED, MUTUALLY EXCLUSIVE header field
    ('One box must be checked') and it is the highest-leverage single field on
    the form: it alone decides whether line 11 is $150 or 0 AND whether the
    credit floor is the minimum tax or zero.
    """
    if tax_basis not in TAX_BASES:
        raise ValueError(f"tax_basis must be one of {TAX_BASES}; got {tax_basis!r}. One box must be checked.")
    return _yk(OR20S_MINIMUM_TAX, year)[tax_basis]


def or20s_calculated_tax(oregon_taxable_income: float, year: int = FORM_TAX_YEAR) -> float:
    """Line 8. ORS 317.061 -- 6.6% of the first $1M, 7.6% above.

    ⚠ Transcribe the floor as printed: 'Enter 0 if the result is negative or
    zero' appears only on the <=$1M branch. A negative line 7 in the >$1M branch
    is impossible by construction, so the asymmetry is harmless.
    ⚠ 'Don't enter minimum tax on this line.'
    """
    bp = _yk(OR20S_RATE_BREAKPOINT, year)
    ti = float(oregon_taxable_income)
    if ti <= bp:
        return max(0.0, ti * float(_yk(OR20S_RATE_LOW, year)))
    return float(_yk(OR20S_RATE_BASE_CONSTANT, year)) + (ti - bp) * float(_yk(OR20S_RATE_HIGH, year))


def or20s_credit_floor(tax_basis: str, year: int = FORM_TAX_YEAR) -> int:
    """Same form, TWO different credit floors, chosen by the page-1 checkbox.

    OR-ASC-CORP Instr. p. 2: excise filers' credits 'can't reduce your excise tax
    below minimum tax'; income filers 'don't have a minimum tax ... can't reduce
    your income tax below zero.'
    """
    return or20s_minimum_tax(tax_basis, year)


def or20s_part1(sch_d_part3_line18: float = 0.0, enpi_worksheet: float = 0.0,
                additions_asc_corp_a: float = 0.0, subtractions_asc_corp_b: float = 0.0,
                prior_c_corp_nol: float = 0.0, apportionment_pct: float = 100.0,
                or_ap_part2_line12: float | None = None) -> dict:
    """Lines 1a-1c, 2, 3, 4, 6 and 7.

    ⚠ Line 1a takes federal 1120-S Schedule D Part III LINE 18 (`Net recognized
    built-in gain`) - the INCOME BASE, not line 23 (the federal 21% TAX). A build
    that grabs line 23 imports the federal tax as if it were Oregon income.
    Negative line 18 => enter $0.
    ⚠ Lines 2 and 3 are SCOPE-LIMITED: 'only if apply to amounts included in line
    1'. They are NOT the entity's Oregon modifications - those live on Schedule
    SM and pass through to shareholders. The two systems are DISJOINT and use
    DIFFERENT CODE VOCABULARIES.
    ⚠ Line 7 has TWO MUTUALLY EXCLUSIVE derivations: the Oregon-only path is
    `line 4 minus line 5` on the face; the multistate path imports Schedule OR-AP
    part 2 line 12 wholesale. A build must not do both.
    ⚠ LINE 6 IS COMPLETED EVEN WHEN THE TAX IS ZERO (the single most likely
    OR-20-S bug). It is the number every nonresident shareholder needs.
    """
    l1a = max(0.0, float(sch_d_part3_line18))
    l1b = float(enpi_worksheet)
    l1c = l1a + l1b
    l2 = float(additions_asc_corp_a)
    l3 = float(subtractions_asc_corp_b)
    l4 = l1c + l2 - l3
    l5 = float(prior_c_corp_nol)
    l6 = float(apportionment_pct)
    if or_ap_part2_line12 is not None:
        l7 = float(or_ap_part2_line12)
        path = "or_ap_part2"
    else:
        l7 = l4 - l5
        path = "oregon_only"
    return {"L1a": l1a, "L1b": l1b, "L1c": l1c, "L2": l2, "L3": l3, "L4": l4,
            "L5": l5, "L6": l6, "L7": l7, "line7_path": path}


def or20s_tax_block(l7_oregon_taxable_income: float, tax_basis: str,
                    fcg20_adjustment: float = 0.0, year: int = FORM_TAX_YEAR) -> dict:
    """Lines 8-12. Line 12 = greater of calculated tax and minimum tax."""
    l8 = or20s_calculated_tax(l7_oregon_taxable_income, year)
    l9 = float(fcg20_adjustment)
    l10 = l8 - l9
    l11 = float(or20s_minimum_tax(tax_basis, year))
    l12 = max(l10, l11)
    return {"L8": l8, "L9": l9, "L10": l10, "L11": l11, "L12": l12}


def or20s_net_tax(l12: float, installment_interest_l13: float = 0.0,
                  carryforward_credits_l15: float = 0.0, lifo_recapture_l17: float = 0.0,
                  tax_basis: str = TAX_BASIS_EXCISE, year: int = FORM_TAX_YEAR) -> dict:
    """Lines 13-18, with the credit floor enforced.

    ⚠ FOUR CONSTRAINTS ON LINE 15, ALL SIMULTANEOUS:
      (i)   the credit must be a CARRYFORWARD FROM A C-CORPORATION YEAR;
      (ii)  it may offset ONLY the BUILT-IN-GAINS portion of the tax - not the
            excess-net-passive portion and not the minimum tax [ORS 314.766(5)];
      (iii) the total may not drop excise tax below $150 (or income tax below 0);
      (iv)  credits apply IN THE ORDER THE PREPARER LISTS THEM.
    ⚠ CONSTRAINT (ii) HAS NO FIELD ON THE FORM. Line 1c FUSES built-in gains and
    excess net passive income into one number and line 14 is a single tax figure,
    so there is nowhere on Form OR-20-S to show that only the BIG slice was
    offset. A real modelling gap - hence D_OR20S_L15_BIG_ONLY_NO_FIELD.
    ⚠ LINE 17 (LIFO) sits BELOW the line-12 minimum comparison AND BELOW the
    line-15 credit subtraction, so LIFO recapture STACKS ON TOP of the $150 and
    CANNOT be absorbed by credits. And it is one-third of the deferred TAX, not
    of the income - a TAX amount in a TAX column despite the word 'addition'.
    """
    l13 = float(installment_interest_l13)
    l14 = float(l12) + l13
    floor = float(or20s_credit_floor(tax_basis, year))
    requested = float(carryforward_credits_l15)
    l15 = min(requested, max(0.0, l14 - floor))
    l16 = l14 - l15
    l17 = float(lifo_recapture_l17)
    l18 = l16 + l17
    return {"L13": l13, "L14": l14, "L15": l15, "L15_requested": requested,
            "L15_limited_by_floor": l15 < requested, "L16": l16, "L17": l17, "L18": l18,
            "credit_floor": floor}


def or20s_estimated_required(net_tax_liability: float, high_income_taxpayer: bool = False,
                             year: int = FORM_TAX_YEAR) -> bool:
    """Line 24 / Form OR-37 gate. '$500 or more in tax. THIS INCLUDES OREGON MINIMUM TAX.'

    ⚠ An S corp with no built-in gains owes exactly $150 and is BELOW the
    threshold - BUT a 'high-income taxpayer' is still on the hook. The definition
    looks at FEDERAL taxable income before NOL and capital-loss carryovers of
    $1,000,000 or more IN ANY ONE OF THE LAST THREE YEARS, not including the
    current year. ⚠ THAT LOOKBACK CANNOT BE COMPUTED FROM THE CURRENT RETURN -
    it is persistent client state or direct entry (D-12 W10).
    """
    if high_income_taxpayer:
        return True
    return float(net_tax_liability) >= _yk(OR20S_EST_TAX_THRESHOLD, year)


def or_daily_interest(year: int) -> str:
    """The DAILY interest rate for a calendar year. Segmented, never blended."""
    return _yk(OR_INTEREST_DAILY, year)


def or_interest_segments(unpaid_tax: float, segments: list) -> dict:
    """Segmented daily interest. `segments` = [(calendar_year, days), ...].

    ⚠ The rate changes at the CALENDAR-YEAR boundary. The DOR's own OR-21
    underpayment worksheet carries `01/01/2026  Rate change` as a first-class
    EVENT LINE, which is the evidence that segmentation - not a blended annual
    rate - is what Oregon expects.
    """
    total = 0.0
    detail = []
    for cal_year, days in segments:
        rate = float(or_daily_interest(cal_year))
        amt = float(unpaid_tax) * rate * int(days)
        detail.append({"year": cal_year, "days": int(days), "daily_rate": rate, "interest": amt})
        total += amt
    return {"total": total, "segments": detail}


# ═══════════════════════════════════════════════════════════════════════════
# FORM OR-21 -- THE PTE-E ELECTIVE TAX. ITS OWN SPEC (campaign D-12 Group B).
#
# ⚠ EVERY CONSTANT AND LINE NUMBER BELOW CARRIES OR21_PROVENANCE: there is no
# published Form OR-21 face, so the 'printed face governs' rule has no subject.
# ═══════════════════════════════════════════════════════════════════════════

# 2021 Or. Laws ch. 589 §3(6): 9% of the first $250,000 'or fraction thereof',
# 9.9% above. ⚠ THE 9% FIRST TIER IS BELOW OREGON'S 9.9% INDIVIDUAL TOP RATE -
# a genuine rate BENEFIT, not a rate-match PTET. The PTE-E can be advantageous
# even ignoring the federal SALT-cap workaround.
OR21_RATE_LOW: dict[int, str] = {2025: "0.09"}
OR21_RATE_HIGH: dict[int, str] = {2025: "0.099"}
OR21_RATE_BREAKPOINT: dict[int, int] = {2025: 250_000}
OR21_RATE_SHORTCUT_CONSTANT: dict[int, int] = {2025: 22_500}   # = 9% x $250,000

OR21_ELECTION_IS_ANNUAL: dict[int, bool] = {2025: True}
OR21_ELECTION_BINDS_FUTURE_YEARS: dict[int, bool] = {2025: False}
OR21_ELECTION_REVOCABLE: dict[int, bool] = {2025: True}
OR21_ELECTION_RETROACTIVE: dict[int, bool] = {2025: False}
OR21_CALENDAR_YEAR_ONLY: dict[int, bool] = {2025: True}
OR21_AVAILABILITY_FIRST_TY: dict[int, int] = {2025: 2022}
OR21_AVAILABILITY_LAST_TY: dict[int, int] = {2025: 2027}   # per the Rev. 04-01-26 instructions (SB 1510)
OR21_ELECTION_NOTE = (
    "2021 Or. Laws ch. 589 §3(2), verbatim: 'The election shall be made ANNUALLY on or before the "
    "due date, including extensions ... The election MAY NOT BE MADE RETROACTIVELY. The members of "
    "a pass-through entity may REVOKE an election under this section for a tax year only on or "
    "before the due date of the pass-through entity's return for that tax year, and only if the "
    "revocation is agreed to by all members who are members at the time of the revocation.' "
    "⚠ NOT BINDING ON FUTURE YEARS. This was the Mississippi question in Wave 3 and OREGON ANSWERS "
    "IT THE OPPOSITE WAY - do not carry the Mississippi assumption over. Vintage: ch. 589 §3 was "
    "amended by 2022 c.82 §3 and the applicability note (2022 c.82 §16(2) as amended by 2024 c.52 "
    "§5(2)) puts TY2025 in scope, so the quoted text IS the TY2025 text."
)
# ⚠ U22 -- A STATUTE-vs-INSTRUCTIONS DIVERGENCE ON THE REVOCATION DEADLINE.
# ch. 589 §3(2) grants revocation 'only on or before THE DUE DATE' with NO
# extension language, in pointed contrast to the ELECTION sentence in the SAME
# subsection ('including extensions'). The DOR instructions add 'including
# extension' to the revocation rule anyway. BUILD TO THE INSTRUCTIONS AND
# DIAGNOSE: an invalid revocation leaves an election IN FORCE, which changes the
# tax.
OR21_REVOCATION_EXTENSION_PER_DOR: dict[int, bool] = {2025: True}
OR21_REVOCATION_EXTENSION_PER_STATUTE: dict[int, bool] = {2025: False}

# ⚠ THE CONTINGENT SUNSET. ch. 589 §§11-13: the PTE-E self-destructs on the date
# IRC 164(b)(6) is repealed. OBBBA RAISED the SALT cap rather than repealing it,
# so the PTE-E is in force for TY2025. A standing staleness trigger.
OR21_SUNSET_TRIGGER = "2021 Or. Laws ch. 589 §§11-13 - repeal becomes operative on the date IRC 164(b)(6) is repealed"

OR21_EST_THRESHOLD: dict[int, int] = {2025: 1_000}
OR21_EST_CURRENT_YEAR_PCT: dict[int, str] = {2025: "0.90"}
OR21_EST_PRIOR_YEAR_PCT: dict[int, str] = {2025: "1.00"}
# ⚠ Safe harbour requires the PTE to have MADE THE ELECTION for the prior year:
# 'To use safe harbor for 2025, the PTE must have made the election for 2024.'
OR21_EST_SAFE_HARBOR_REQUIRES_PRIOR_ELECTION: dict[int, bool] = {2025: True}
# ⚠ THREE DIFFERENT QUARTERLY CALENDARS COEXIST IN THE OREGON PTE SPACE.
# OR-21 Q2 is JUNE 16 (June 15, 2025 was a Sunday) and Q4 is JANUARY 15 - the
# INDIVIDUAL date, NOT the corporate December 15.
OR21_EST_DUE_DATES: dict[int, list] = {2025: ["2025-04-15", "2025-06-16", "2025-09-15", "2026-01-15"]}
OR21_EST_DUE_DATES_NEXT_YEAR: dict[int, list] = {2026: ["2026-04-15", "2026-06-15", "2026-09-15", "2027-01-15"]}
OR21_EST_FISCAL_USES_CALENDAR_DATES: dict[int, bool] = {2025: True}

OR21_ANNUALIZATION_PERIOD_END_MONTHS: dict[int, list] = {2025: [3, 5, 8, 12]}
OR21_ANNUALIZATION_MULTIPLIERS: dict[int, list] = {2025: ["4", "2.4", "1.5", "1"]}
OR21_ANNUALIZATION_PERCENTAGES: dict[int, list] = {2025: ["0.225", "0.45", "0.675", "0.9"]}

OR21_PENALTY_FAILURE_TO_PAY_PCT: dict[int, str] = {2025: "0.05"}
# ⚠ NO 20% failure-to-file penalty and NO 100% three-year penalty on Form OR-21,
# unlike Form OR-20-S. A THIRD penalty posture. Do not share the corporate engine.
OR21_HAS_FAILURE_TO_FILE_PENALTY: dict[int, bool] = {2025: False}
OR21_HAS_THREE_YEAR_PENALTY: dict[int, bool] = {2025: False}
OR21_PENALTY_ROUNDING = "round the line-27 TOTAL to the nearest $1, AFTER summing penalty and interest - not component-wise"

# THE FEDERAL SOURCE MAP -- ✅ every reference verified positionally against the
# FINAL 2025 IRS Forms 1065 and 1120-S by TWO independent workstreams, 0 errors.
# ⚠ 'Not one line from OR-65 or OR-20-S' was verified with ZERO EXCEPTIONS: the
# strings 'OR-65' and 'OR-20-S' do not occur anywhere in 150-107-114-1.
OR21_SCHED_K_MAP: dict[str, dict] = {
    M_1065: {
        "6": ["1"], "7": ["2"], "8": ["3c"], "9": ["4c"], "10": ["5"],
        "11": ["6a"], "12": ["7"], "13": ["8", "9a"], "14": ["10"], "15": ["11"],
    },
    M_1120S: {
        # ⚠ THE ONLY MODULE FORK IN THE OR-21 BASE. 'If the PTE is a partnership,
        # enter the total guaranteed payments from federal Schedule K, line 4c;
        # OTHERWISE, ENTER 0.'
        "6": ["1"], "7": ["2"], "8": ["3c"], "9": None, "10": ["4"],
        "11": ["5a"], "12": ["6"], "13": ["7", "8a"], "14": ["9"], "15": ["10"],
    },
}
# ⚠ EXCLUDED BY DESIGN, and the exclusions are load-bearing:
#  - 1065 lines 9b/9c and 1120-S lines 8b/8c (collectibles 28% gain and
#    unrecaptured 1250 gain) are CHARACTERISATION SUB-LINES of 9a/8a and would
#    DOUBLE-COUNT at OR-21 line 13.
#  - EVERYTHING from the Deductions block down: 1065 line 12 / 1120-S line 11
#    (IRC 179), charitable contributions, investment interest, 59(e)(2), other
#    deductions, self-employment, credits. Pub. OR-21-EST p. 1, verbatim:
#    'Separately stated deductions, such as the expense deduction allowed under
#    Section 179 ... or the IRC Section 170 deduction for charitable
#    contributions are not included in the calculation of estimated tax.'
#    THE PTE-E BASE IS GROSS.
OR21_SCHED_K_EXCLUDED: dict[str, list] = {
    M_1065: ["9b", "9c", "12 (IRC 179)", "13 (charitable etc.)", "everything below the Deductions block"],
    M_1120S: ["8b", "8c", "11 (IRC 179)", "12 (charitable etc.)", "everything below the Deductions block"],
}
OR21_DISTRIBUTIVE_PROCEEDS_DEFINITION = (
    "2021 Or. Laws ch. 589 §2(1), verbatim: '\"Distributive proceeds\" means the net income, "
    "dividends, royalties, interest, rents, guaranteed payments and gains of a pass-through entity, "
    "derived from or connected with sources within this state.'"
)


def or21_module_line9(module: str) -> list | None:
    """⚠ The ONLY module fork in the Form OR-21 base."""
    if module not in MODULES:
        raise ValueError(f"module must be one of {MODULES}; got {module!r}")
    return OR21_SCHED_K_MAP[module]["9"]


def or21_part_c(module: str, sch_k: dict, non_apportionable_l17: float = 0.0,
                apportionment_pct_l19: float = 100.0,
                oregon_allocated_l21: float | None = None) -> dict:
    """Form OR-21 Part C, lines 6-22. THE ENTIRE PTE-E BASE.

    ⚠ Built ENTIRELY from federal Schedule K. NOT ONE LINE comes from Form OR-65
    or Form OR-20-S. Line 13 is the only COMPOSED line (short-term + long-term
    capital gain) and it deliberately excludes the characterisation sub-lines.

    ⚠ LINE 21 DRAWS FROM LINE 17, NOT LINE 19 (OR-DEF-5 / U2). When the PTE does
    all of its business activity in Oregon, line 21 = line 17, which gives
    L22 = L20 + L21 = L18 + L17 = L16. That is the only arithmetic that closes.
    Building the DOR's literal 'enter the amount from line 19' puts a four-decimal
    PERCENTAGE into a dollar field.
    """
    if module not in MODULES:
        raise ValueError(f"module must be one of {MODULES}; got {module!r}")
    fed = OR21_SCHED_K_MAP[module]
    lines: dict[str, float] = {}
    for or_line in ("6", "7", "8", "9", "10", "11", "12", "13", "14", "15"):
        srcs = fed[or_line]
        lines[f"L{or_line}"] = 0.0 if srcs is None else float(sum(float(sch_k.get(s, 0.0)) for s in srcs))
    l16 = sum(lines[f"L{n}"] for n in ("6", "7", "8", "9", "10", "11", "12", "13", "14", "15"))
    l17 = float(non_apportionable_l17)
    l18 = l16 - l17
    l19 = float(apportionment_pct_l19)
    l20 = l18 * (l19 / 100.0)
    # ⚠ OR-DEF-5 / U2: line 21 comes from LINE 17, never from line 19.
    l21 = l17 if oregon_allocated_l21 is None else float(oregon_allocated_l21)
    l22 = l20 + l21
    lines.update({"L16": l16, "L17": l17, "L18": l18, "L19": l19, "L20": l20,
                  "L21": l21, "L22": l22, "L21_source": "L17 (U2 - the DOR text says L19 and is wrong)"})
    return lines


def or21_tax(l22_distributive_proceeds: float, year: int = FORM_TAX_YEAR) -> float:
    """Line 23, CLOSED FORM. `min(L22, 250000) x 0.09 + max(0, L22 - 250000) x 0.099`.

    Validated against the DOR's own six-step worksheet by `or21_tax_worksheet`.
    Arithmetically CONTINUOUS at the breakpoint: both branches give $22,500 at
    exactly $250,000.
    """
    bp = float(_yk(OR21_RATE_BREAKPOINT, year))
    l22 = float(l22_distributive_proceeds)
    if l22 <= 0:
        return 0.0
    return min(l22, bp) * float(_yk(OR21_RATE_LOW, year)) + \
        max(0.0, l22 - bp) * float(_yk(OR21_RATE_HIGH, year))


def or21_tax_worksheet(l22_distributive_proceeds: float, year: int = FORM_TAX_YEAR) -> dict:
    """The DOR's own six-step PTE-E tax worksheet, seeded for AUDITABILITY.

    ⚠ Line e is a BRANCH, not a formula, and $22,500 is a HARD-CODED SHORTCUT
    CONSTANT (= 9% x $250,000). At exactly $250,000, line c = 0 and line d = 0, so
    line e takes the FIRST branch and computes 250,000 x 9% = $22,500 - identical
    to the `otherwise` constant, so the branch is SAFE AT THE BOUNDARY and only
    matters BELOW $250,000.
    The DOR's two worked examples must reproduce exactly: $425,000 -> $39,825 and
    $180,000 -> $16,200.
    """
    a = float(l22_distributive_proceeds)
    b = float(_yk(OR21_RATE_BREAKPOINT, year))
    c = max(0.0, a - b)
    d = c * float(_yk(OR21_RATE_HIGH, year))
    e = a * float(_yk(OR21_RATE_LOW, year)) if d == 0 else float(_yk(OR21_RATE_SHORTCUT_CONSTANT, year))
    f = d + e
    return {"a": a, "b": b, "c": c, "d": d, "e": e, "f": f}


def or21_stop_do_not_file(l22_distributive_proceeds: float) -> bool:
    """⚠ THE HARD STOP. Instr. p. 4, line 22, verbatim:

    'If line 22 is zero or a loss (negative number), STOP. Do not file Form
    OR-21. Instead, go to the PTE's account on Revenue Online and request a
    refund of all estimated PTE-E tax payments made for this tax year.'

    This must produce a CLIENT INSTRUCTION, not a return. There is a parallel
    'request for refund without election' path with the same shape.
    """
    return float(l22_distributive_proceeds) <= 0


def or21_document_state(election: bool, revocation: bool, amended: bool,
                        upper_tier_passthrough: bool) -> str:
    """Form OR-21 has FOUR distinct document states, and one of them is easy to miss.

    - `election`         : the ordinary electing return.
    - `revocation`       : 'complete this form as if you are making the election,
                           EXCEPT enter 0 for all numeric fields on lines 6
                           through 23' + the Revocation box. A FILED OR-21 WITH A
                           ZEROED BODY.
    - `amended`          : Box 3; refile with all schedules 'as it should have
                           been filed', PLUS an amended Schedule OR-21-K-1 to
                           EVERY member. ⚠ 'Member listed by mistake ... list the
                           member on the amended schedule as well, but enter
                           zeroes for all of that member's amounts' - a ZEROED
                           GHOST MEMBER ROW that must persist rather than be
                           deleted.
    - `upper_tier_only`  : ⚠⚠ A NON-ELECTING UPPER-TIER PTE MUST STILL FILE A
                           PARTIAL FORM OR-21 - Parts A, B (box 5 only) and F,
                           with 0 on lines 6 through 33, plus Schedule
                           OR-21-MD-PT plus an OR-21-K-1 to every member.
                           'If the PTE is not making its own election to pay
                           PTE-E tax, do not check any other boxes.'
    """
    flags = [election, revocation, amended, upper_tier_passthrough]
    if sum(1 for f in (election, revocation) if f) > 1:
        raise ValueError("Election and Revocation are mutually exclusive on Form OR-21")
    if revocation:
        return "revocation"
    if election and amended:
        return "amended_election"
    if election:
        return "election"
    if upper_tier_passthrough:
        return "upper_tier_only"
    if not any(flags):
        raise ValueError("no Form OR-21 document state selected")
    return "amended"


def or21_regular_installment(current_year_tax_l23: float, prior_year_tax_l23: float | None,
                             year: int = FORM_TAX_YEAR) -> dict:
    """The regular installment worksheet (Form OR-21 Instr. p. 6).

    ⚠ The $1,000 test is on the CURRENT-YEAR tax at worksheet line 1 and it turns
    underpayment interest off ENTIRELY. Pub. OR-21-EST applies the same test at
    ITS line 2 - same substance, different numbering between two DOR
    publications. PREFER the Form OR-21 instructions (Rev. 04-01-26) over
    Pub. OR-21-EST (Rev. 10-16-24) on every point of conflict (U6).
    ⚠ Prior-year safe harbour requires an ELECTION to have been made for 2024.
    ⚠ 'Underpayment interest may be charged even if the return shows an
    overpayment if estimated payments were late or too small.'
    """
    l1 = float(current_year_tax_l23)
    if l1 < _yk(OR21_EST_THRESHOLD, year):
        return {"L1": l1, "below_threshold": True, "L2": None, "L3": None, "L4": 0.0, "L5": 0.0}
    l2 = l1 * float(_yk(OR21_EST_CURRENT_YEAR_PCT, year))
    l3 = None if prior_year_tax_l23 is None else \
        float(prior_year_tax_l23) * float(_yk(OR21_EST_PRIOR_YEAR_PCT, year))
    l4 = l2 if l3 is None else min(l2, l3)
    return {"L1": l1, "below_threshold": False, "L2": l2, "L3": l3, "L4": l4, "L5": l4 / 4.0}


def or21_annualized_installment(period_index: int, period_proceeds: float,
                                prior_period_installments: float = 0.0,
                                regular_installment: float = 0.0,
                                prior_excess: float = 0.0, year: int = FORM_TAX_YEAR) -> dict:
    """The annualized installment worksheet, columns A-D.

    Period ends 3/31, 5/31, 8/31, 12/31 => 3, 5, 8, 12 months, multipliers
    4 / 2.4 / 1.5 / 1, cumulative percentages 22.5% / 45% / 67.5% / 90% (the 90%
    safe harbour spread evenly).
    ⚠ Line 4: 'If the annualized amount on line 3 is less than $250,000, multiply
    line 3 times 9 percent (0.09). Otherwise, use the instructions for Form OR-21,
    line 23 as a guide' - i.e. the same two-tier rate.
    ⚠ Box 1D must tie to Form OR-21 line 22.
    """
    if period_index not in (0, 1, 2, 3):
        raise ValueError("period_index must be 0..3 (columns A-D)")
    mult = float(_yk(OR21_ANNUALIZATION_MULTIPLIERS, year)[period_index])
    pct = float(_yk(OR21_ANNUALIZATION_PERCENTAGES, year)[period_index])
    l1 = float(period_proceeds)
    l3 = l1 * mult
    l4 = or21_tax(l3, year)
    l6 = l4 * pct
    l7 = float(prior_period_installments)
    l8 = max(0.0, l6 - l7)
    l9 = float(regular_installment)
    l10 = float(prior_excess)
    l11 = l9 + l10
    l12 = max(0.0, l11 - l8)
    l13 = min(l8, l11)
    return {"multiplier": mult, "percentage": pct, "L1": l1, "L3": l3, "L4": l4,
            "L6": l6, "L7": l7, "L8": l8, "L9": l9, "L10": l10, "L11": l11,
            "L12": l12, "L13": l13}


def or21_late_penalty_interest(unpaid_tax: float, days_late: int,
                               interest_calendar_year: int = 2026,
                               year: int = FORM_TAX_YEAR) -> dict:
    """Line 27. 5% failure-to-pay + DAILY interest, TOTAL rounded to the nearest $1.

    ⚠ NO 20% failure-to-file and NO 100% three-year penalty on Form OR-21.
    ⚠ Day count runs from the day AFTER the due date THROUGH the payment date
    inclusive. The DOR's Example 3 pins it: April 16, 2026 to July 29, 2026 =
    105 days at 0.0219%, on $4,825 unpaid, giving $241.25 penalty + $110.95
    interest = $352.20, entered as $352.
    """
    penalty = float(unpaid_tax) * float(_yk(OR21_PENALTY_FAILURE_TO_PAY_PCT, year))
    interest = float(unpaid_tax) * float(or_daily_interest(interest_calendar_year)) * int(days_late)
    total = penalty + interest
    return {"penalty": penalty, "interest": interest, "total": total,
            "line_27": int(total + 0.5)}


def or21_md_allocation(member_shares: list, total_addition: float, tax_l23: float,
                       line_22: float) -> dict:
    """Schedule OR-21-MD Part A columns s and t, and Part B lines 3/4/5.

    THE RULE AS THE DOR WROTE IT, verbatim: 'FOR EACH MEMBER WITH A POSITIVE
    SHARE of distributive proceeds in column r, divide the member's share by the
    total distributive proceeds FROM FORM OR-21, LINE 22. Multiply this
    percentage by the total addition amount.' Column t uses the same percentage
    against Form OR-21 line 23.

    ⚠⚠ U5 -- PROVEN IMPOSSIBLE WITH ANY NEGATIVE MEMBER SHARE.
    Part B line 4 must equal the total addition and line 5 must equal line 23, on
    pain of 'the schedule is not complete'. With A = the addition and T = the
    tax, the schedule computes line 4 = A * Sum(positive r) / L22 and
    line 5 = T * Sum(positive r) / L22. BOTH tie-outs hold IF AND ONLY IF
    Sum(positive column-r shares) == Form OR-21 line 22 - a necessary AND
    sufficient condition. Line 22 is built entirely from entity-level federal
    Schedule K aggregates with NO positive-share filter, so it cannot equal that
    sum except by coincidence.
    Worked counterexample: +100,000 / +100,000 / -50,000 -> L22 = 150,000,
    L23 = 13,500, but lines 4 and 5 each total 18,000 - 33.3% over, i.e. $18,000
    of refundable member credit against $13,500 of entity tax.
    ⚠ REFINEMENT: a ZERO share is HARMLESS (it contributes 0 to both sides).
    ONLY A NEGATIVE SHARE BREAKS IT.
    ⚠⚠ THE FIX IS NOT DOR GUIDANCE. The 'use the positive-share sum as the
    denominator' reading reasons from the mandatory tie-out Caution, NOT from any
    cited rule, and all six PTE-E documents plus ch. 589 were swept with no
    escape hatch found (the 'enter zeroes' rule is scoped to the amended-return
    'member listed by mistake' case only; §3(5) STRENGTHENS the contradiction).
    So this function returns BOTH readings and labels NEITHER as authority.
    RED-DEFER: D_OR21_R15_MD_DENOMINATOR.
    """
    shares = [float(s) for s in member_shares]
    positive = [s for s in shares if s > 0]
    sum_positive = sum(positive)
    has_negative = any(s < 0 for s in shares)
    l22 = float(line_22)

    def _alloc(denominator: float) -> dict:
        if denominator == 0:
            return {"pct": [], "col_s": [], "col_t": [], "line_4": 0.0, "line_5": 0.0}
        pct = [(s / denominator if s > 0 else 0.0) for s in shares]
        col_s = [p * float(total_addition) for p in pct]
        col_t = [p * float(tax_l23) for p in pct]
        return {"pct": pct, "col_s": col_s, "col_t": col_t,
                "line_4": sum(col_s), "line_5": sum(col_t)}

    as_written = _alloc(l22)                 # the DOR's literal denominator
    positive_denom = _alloc(sum_positive)    # the CANDIDATE fix -- NOT DOR guidance
    ties_out = abs(sum_positive - l22) < 0.005
    return {
        "line_3": sum(shares),
        "sum_positive_shares": sum_positive,
        "line_22": l22,
        "has_negative_share": has_negative,
        "tie_out_possible": ties_out,
        "as_written_line22_denominator": as_written,
        "candidate_positive_share_denominator": positive_denom,
        "candidate_is_dor_guidance": False,
        "u5_note": (
            "U5. Both Part B tie-outs hold IF AND ONLY IF sum(positive column-r shares) == Form "
            "OR-21 line 22. A zero share is harmless; ONLY a negative share breaks it. The "
            "positive-share denominator is a CANDIDATE reasoned from the mandatory tie-out "
            "Caution, NOT cited DOR guidance - do not present it as such. Settle by an OAR under "
            "2021 Or. Laws ch. 589 §5(3), DOR guidance, or the MeF validation rules."
        ),
    }


def or21_k1_lines(md_col_r: float, md_col_s: float, md_col_t: float,
                  mdpt_col_l: float = 0.0, mdpt_col_m: float = 0.0,
                  mdpt_col_n: float = 0.0) -> dict:
    """Schedule OR-21-K-1 lines 1-3. EACH LINE IS A SUM ACROSS TWO SCHEDULES.

    ⚠ Line 1 is reported to the member FOR INFORMATION ONLY - 'It is not reported
    on your federal or Oregon personal income tax return.'
    ⚠ Line 2 -> Schedule OR-ASC Section A / OR-ASC-NP Section B, ADDITION CODE 167.
    ⚠ Line 3 -> Schedule OR-ASC Section F / OR-ASC-NP Section I, REFUNDABLE CREDIT
      CODE 900, and 900 IS NOT PRORATED for nonresidents or part-year residents.
      'Do not include penalty, interest on unpaid tax, or interest on an
      underpayment of estimated tax.'
    ⚠ An electing PTE issues TWO Oregon K-1s per owner (OR-K-1 AND OR-21-K-1) and
      NEITHER is filed with any return.
    """
    return {"L1": float(md_col_r) + float(mdpt_col_l),
            "L2": float(md_col_s) + float(mdpt_col_m),
            "L3": float(md_col_t) + float(mdpt_col_n),
            "L2_owner_destination": "Schedule OR-ASC Section A / OR-ASC-NP Section B, addition code 167",
            "L3_owner_destination": "Schedule OR-ASC Section F / OR-ASC-NP Section I, refundable credit code 900"}


def or21_owner_legs() -> list[dict]:
    """THREE owner-side legs, not one. Encoded so none is quietly dropped."""
    return [
        {"leg": "addition", "namespace": NS_INDIVIDUAL, "code": 167,
         "label": "PTE-E tax deducted on entity-level federal return",
         "when": "the year the electing PTE deducts the tax federally"},
        {"leg": "refundable_credit", "namespace": NS_INDIVIDUAL, "code": 900,
         "label": "Pass-through entity elective taxes paid", "prorated_for_nonresidents": False,
         "when": "the year of the election"},
        {"leg": "subtraction", "namespace": NS_INDIVIDUAL, "code": 387,
         "label": "PTE-E tax refund included on entity-level federal return",
         "when": "a LATER year, when a refund of the previously-added tax is reported federally"},
    ]


# ═══════════════════════════════════════════════════════════════════════════
# SCHEDULE OR-AP -- apportionment for BOTH entity forms (never for OR-21)
# ═══════════════════════════════════════════════════════════════════════════

# ⚠ Oregon is SINGLE SALES FACTOR (ORS 314.650, complete: 'All apportionable
# income shall be apportioned to this state by multiplying the income by the
# sales factor') - and Schedule OR-AP part 1 STILL collects a property factor and
# a payroll factor across two full pages, with the instruction 'Note: Please
# complete all sections of Schedule OR-AP, part 1.'
# THE STATUTORY REASON: ORS 314.655(1) and ORS 314.660(1) BOTH OPEN verbatim
# 'For purposes of ORS 317.391, the property factor is ...' / '... the payroll
# factor is ...' - the factors survive in Oregon statute ONLY for the Oregon
# Investment Advantage, plus insurers and utility/telecom electors. The valuation
# rules the DOR restates ARE ORS 314.655(2)-(3), i.e. the ORS 317.391 rules -
# the same 317.391 that reappears at OR-AP part 2 line 10b.
# So the lines are NOT vestigial: live for OIA claimants, insurers and
# utility/telecom electors, DEAD for everyone else. D-12 W5: required
# direct-entry data with no downstream computation for a standard filer.
OR_AP_COLLECTS_PROPERTY_PAYROLL: dict[int, bool] = {2025: True}
OR_AP_PROPERTY_PAYROLL_AUTHORITY = "ORS 314.655(1) and ORS 314.660(1), both opening 'For purposes of ORS 317.391'"
OR_AP_ROUNDING_DECIMALS: dict[int, int] = {2025: 4}
# ⚠ THE LAYOUT DIFFERS BY SECTION. Property and payroll use an a/b suffix pair on
# every line (1a/1b ... 12a/12b) on two separate pages. SALES uses BARE line
# numbers 13-21 for OREGON ONLY, with a single 22b for Everywhere. THERE IS NO
# 13b-21b. A model assuming uniform a/b pairing invents NINE FIELDS THAT DO NOT
# EXIST.
OR_AP_SALES_LINES_OREGON_ONLY = ("13", "14", "15", "16", "17", "18", "19", "20", "21")
OR_AP_HAS_NO_B_SIDE_FOR_SALES: dict[int, bool] = {2025: True}
# The alternative (double-weighted sales) worksheet -- utility/telecom electors
# only, via OR-20-S Question I. ⚠ Cited to `ORS 314.650 (1999 EDITION)`, a
# deliberately FROZEN prior edition; the current 314.650 is single-sales-factor.
# Do NOT read the current statute and conclude the worksheet is obsolete.
OR_AP_ALT_WORKSHEET_AUTHORITY = "ORS 314.650 (1999 edition), preserved by express reference"
OR_AP_ALT_SALES_COUNTED_TWICE: dict[int, bool] = {2025: True}


def or_ap_line23_standard(oregon_sales: float, everywhere_sales: float,
                          year: int = FORM_TAX_YEAR) -> float | None:
    """Standard apportionment worksheet -> part 1 line 23. Four decimal places.

    Returns None for a zero denominator rather than a silent 0.0.
    """
    if float(everywhere_sales) == 0:
        return None
    pct = float(oregon_sales) / float(everywhere_sales) * 100.0
    return round(pct, _yk(OR_AP_ROUNDING_DECIMALS, year))


def or_ap_line23_alternative(factors: list, year: int = FORM_TAX_YEAR) -> float | None:
    """Double-weighted sales worksheet. `factors` = [(oregon, everywhere), ...] in
    worksheet order: property (L1), payroll (L2), sales (L3), SALES AGAIN (L4).

    ⚠ THREE THINGS A NAIVE IMPLEMENTATION GETS WRONG:
      1. The sales factor is entered TWICE (lines 3 and 4) - THAT is the
         double-weighting.
      2. The divisor at line 6 is THE NUMBER OF FACTORS WITH A POSITIVE COLUMN-(b)
         DENOMINATOR, not a constant 4. A taxpayer with no payroll anywhere
         divides by 3. A full-factor taxpayer divides by 4 (sales appears twice).
      3. Available only to taxpayers 'primarily engaged in utilities or
         telecommunications' - an UNDEFINED threshold. RED-DEFER.
    """
    if len(factors) != 4:
        raise ValueError("the alternative worksheet has FOUR factor rows (sales appears twice)")
    total_pct, positive = 0.0, 0
    for oregon, everywhere in factors:
        if float(everywhere) > 0:
            positive += 1
            total_pct += float(oregon) / float(everywhere) * 100.0
    if positive == 0:
        return None
    return round(total_pct / positive, _yk(OR_AP_ROUNDING_DECIMALS, year))


# ⚠⚠ D-12 W3 -- ONE FILED INSTANCE, plus a SEPARATE OFF-SCHEDULE owner-source
# computation. The 'must be run twice' mandate was DISPROVEN on verification.
OR_AP_PART2_PURPOSE_ENTITY = "entity_level"
OR_AP_PART2_PURPOSE_OWNER = "owner_source"
OR_AP_PART2_FILED_INSTANCES: dict[int, int] = {2025: 1}
OR_AP_PART2_OWNER_RUN_IS_FILED: dict[int, bool] = {2025: False}
OR_AP_PART2_PERMISSIVE_QUOTE = (
    "Sch. OR-AP Instr. p. 2, verbatim: 'Note: This part of the schedule is used for computation of "
    "entity level Oregon taxable income for Form OR-20, OR-20-INC, OR-20-INS, and OR-20-S filers. "
    "MOST PASS-THROUGH ENTITIES (PTEs) DON'T COMPLETE SCHEDULE OR-AP, PART 2. HOWEVER, THEY MAY USE "
    "IT to determine the Oregon-source distributive income for their owners.' PERMISSIVE. The "
    "mandatory duty is to REPORT each nonresident owner's Oregon-source income, not to file a "
    "second part 2, and the face directs a single filing."
)
OR_AP_PART2_L4_IS_INFERENCE = (
    "⚠ Part 2 lines 4, 5, 6 and 9 have NO published line instruction, and line 4 has NO printed "
    "formula. `L4 = L1 - L2 - L3` is INFERRED from the 'Subtract:' labels on the face. Cite it as "
    "an inference, never as a quotation."
)


def or_ap_part2(income_l1: float, nonapportionable_l2: float = 0.0,
                prior_installment_gains_l3: float = 0.0, apportionment_pct_l5: float = 100.0,
                nonapportionable_to_oregon_l7: float = 0.0,
                installment_gains_to_oregon_l8: float = 0.0,
                prior_net_loss_l10a: float = 0.0, net_capital_loss_l10b: float = 0.0,
                purpose: str = OR_AP_PART2_PURPOSE_ENTITY) -> dict:
    """Schedule OR-AP part 2, lines 1-12.

    ⚠ THE ONLY DIFFERENCE BETWEEN THE TWO EVALUATIONS IS THREE THINGS:
      line-1 INPUT   -- entity: OR-20-S line 4. owner: 'ONLY the modified
                        distributive income for the entity' (ORS 314.775), i.e.
                        federal distributive income +/- Schedule I / Schedule SM.
      line 10        -- entity: USED. owner: SUPPRESSED, verbatim 'Do not use
                        line 10 when computing Oregon-source distributive income
                        for nonresident owners of PTEs.'
      line-12 OUTPUT -- entity: -> OR-20-S line 7. owner: -> each Schedule OR-K-1
                        column (b), plus the Oregon-source portion of any
                        guaranteed payments and the taxable portion of
                        distributions.
    ⚠ ONLY THE ENTITY RUN IS FILED (D-12 W3). Printing two part 2s would put an
    UNFILED computation on the return.
    ⚠ The entity run happens ONLY if the S corp has federal taxable income,
    built-in gains or excess net passive income; otherwise line 7 is -0- and part
    2 is not run for entity purposes at all.
    """
    if purpose not in (OR_AP_PART2_PURPOSE_ENTITY, OR_AP_PART2_PURPOSE_OWNER):
        raise ValueError(f"purpose must be entity_level or owner_source; got {purpose!r}")
    l1 = float(income_l1)
    l2 = float(nonapportionable_l2)
    l3 = float(prior_installment_gains_l3)
    l4 = l1 - l2 - l3              # ⚠ INFERRED - see OR_AP_PART2_L4_IS_INFERENCE
    l5 = float(apportionment_pct_l5)
    l6 = l4 * (l5 / 100.0)
    l7 = float(nonapportionable_to_oregon_l7)
    l8 = float(installment_gains_to_oregon_l8)
    l9 = l6 + l7 + l8
    if purpose == OR_AP_PART2_PURPOSE_OWNER:
        l10a = l10b = 0.0          # ⚠ SUPPRESSED for the owner-source run
    else:
        l10a, l10b = float(prior_net_loss_l10a), float(net_capital_loss_l10b)
    l11 = l10a + l10b
    l12 = l9 - l11
    return {"purpose": purpose, "filed": purpose == OR_AP_PART2_PURPOSE_ENTITY,
            "L1": l1, "L2": l2, "L3": l3, "L4": l4, "L5": l5, "L6": l6, "L7": l7,
            "L8": l8, "L9": l9, "L10a": l10a, "L10b": l10b, "L11": l11, "L12": l12,
            "L12_destination": ("OR-20-S line 7" if purpose == OR_AP_PART2_PURPOSE_ENTITY
                                else "each Schedule OR-K-1 column (b), plus Oregon-source guaranteed "
                                     "payments and the taxable portion of distributions")}


def or_guaranteed_payment_ordering() -> str:
    """✅ U9 CLOSED. OAR 150-316-0155 pulled in full; the ordering IS explicit.

    Verbatim: '(1) Guaranteed payments paid to nonresident partners ... are
    treated as a distributive share of partnership income for Oregon tax
    purposes. In order to determine the income attributable to Oregon sources,
    each nonresident partner's ENTIRE distributive share, INCLUDING the
    guaranteed payments, IS THEN SUBJECT TO the allocation and apportionment
    provisions of ORS 314.605 to 314.675. (2) The inclusion of guaranteed
    payments into a nonresident partner's share of apportionable income is
    IRRESPECTIVE OF that partner's percentage interest in the profit or loss of
    the partnership.' (REV 29-2017 - last amended 2017, valid for TY2025.)

    ⚠ APPORTION-THEN-ATTRIBUTE. The DOR's own paraphrase in the OR-19
    instructions and Pub. OR-OC - 'attributed DIRECTLY to the owner receiving the
    payment' - is LOOSER THAN THE RULE and, read alone, invites a spec author to
    SKIP APPORTIONMENT ENTIRELY. BUILD TO THE RULE TEXT.
    """
    return "apportion_then_attribute"


# ═══════════════════════════════════════════════════════════════════════════
# SCHEDULE OR-K-1 -- the owner schedule for BOTH entity modules
# ═══════════════════════════════════════════════════════════════════════════

# ONE schedule serves PARTNERS, SHAREHOLDERS and BENEFICIARIES. The four
# member-type checkboxes include `Beneficiary` (Form OR-41 fiduciary).
OR_K1_MEMBER_TYPES = ("general_partner_or_llc_member_manager", "limited_partner_or_other_llc_member",
                      "shareholder", "beneficiary")
# The four MUTUALLY EXCLUSIVE owner-status checkboxes.
OR_K1_OWNER_STATUS = ("form_or_oc", "form_or_19", "form_or_19_af", "not_required")
# ⚠ Line 4 `Guaranteed payments to partners` is DEAD for an S corporation and the
# face indicates no suppression - the app must suppress it BY MODULE.
OR_K1_LINE4_LIVE: dict[str, bool] = {M_1065: True, M_1120S: False}
# ⚠ Lines 8 and 9 are SEPARATE here (short-term / long-term) where Form OR-21
# line 13 FUSES them. Three different orderings of the same federal data across
# three Oregon artifacts.
OR_K1_SPLITS_CAPITAL_GAIN: dict[int, bool] = {2025: True}
# ⚠ Lines 12-13 are 'Adjustments', a THIRD category distinct from Oregon
# additions (14-15) and Oregon subtractions (16-18). IRC 179 rides line 12 as an
# ADJUSTMENT, not a modification - consistent with Oregon conforming to 179.
OR_K1_ADJUSTMENT_LINES = ("12", "13")
OR_K1_ADDITION_LINES = ("14", "15")
OR_K1_SUBTRACTION_LINES = ("16", "17", "18")
OR_K1_OVERFLOW_LINES = ("15", "18")   # both printed `(include schedule)`
OR_K1_CREDIT_LINE = "19"
OR_K1_PAYMENT_LINES = ("20", "21")


def or_k1_column_fill(is_oregon_resident: bool) -> dict:
    """⚠⚠ TWO COMPLETELY DIFFERENT FILL PATTERNS ON ONE SCHEDULE, selected by the
    `Oregon resident?` radio. A build that populates both columns uniformly
    produces a WRONG RESIDENT K-1.

    Residents, verbatim: 'Complete lines 1-18 of the federal column (a) and lines
    19 and 20, column (b). DON'T USE LINES 1-18 OF THE OREGON COLUMN (b) FOR
    OREGON RESIDENTS.'
    Nonresidents, verbatim: 'Complete both the federal column (a) and the Oregon
    column (b) ... multiply the apportionment percentage by the owner's pro rata
    share of each item in the federal column.'
    ⚠ Line 21 (composite tax paid) is mentioned for NEITHER residency in that
    paragraph, because a RESIDENT CANNOT JOIN A COMPOSITE RETURN: 'For
    nonresidents who elected to be included in a composite filing only.'
    """
    if is_oregon_resident:
        return {"column_a_lines": [str(n) for n in range(1, 19)],
                "column_b_lines": ["19", "20"],
                "column_b_is_apportioned": False}
    return {"column_a_lines": [str(n) for n in range(1, 19)],
            "column_b_lines": [str(n) for n in range(1, 22)],
            "column_b_is_apportioned": True}


def or_k1_pte_e_suppression(pte_e_election: bool) -> dict:
    """⚠ SUPPRESSION LOGIC, NOT JUST POPULATION LOGIC.

    OR-K-1 Instr., verbatim: 'Lines 14 through 18. Enter the owner's pro rata
    share for each addition and subtraction as a positive amount. DON'T INCLUDE
    THE PTE-E ADDITION IF THE PTE MADE THE ELECTION to pay PTE-E tax.' and
    'Line 19 ... DON'T INCLUDE THE PTE-E TAX CREDIT IF THE PTE ELECTED to pay the
    PTE-E tax.'
    When the election is made the PTE-E items ride EXCLUSIVELY on Schedule
    OR-21-K-1. Both instructions say each schedule is NOT a substitute for the
    other, so an electing PTE issues TWO Oregon K-1s per owner.
    """
    return {"suppress_pte_e_addition_lines_14_18": bool(pte_e_election),
            "suppress_pte_e_credit_line_19": bool(pte_e_election),
            "issue_or_21_k1": bool(pte_e_election)}


def or_k1_overflow_namespace() -> str:
    """⚠⚠ THE CROSSING POINT, stated once, in one place.

    OR-K-1 lines 15 and 18 are printed `(include schedule)` and Schedule OR-K-1
    Instructions 150-101-002-1 (Rev. 09-03-25) p. 2 requires that attachment to
    carry PUBLICATION OR-CODES - i.e. INDIVIDUAL - codes, verbatim: 'Include the
    code for each item from Publication OR-CODES' and 'Use the appropriate code
    for each item as shown on an attachment to Schedule OR-K-1 or as listed in
    Publication OR-CODES.'
    SCHEDULE OR-K-1 IS ISSUED BY BOTH ENTITY FORMS, so an S corporation running
    CORPORATE codes on OR-20-S lines 2/3 must simultaneously emit INDIVIDUAL
    codes here. The DOR has published NO firewall at this point - the two
    'Schedule SM' notes are a decoy (OR_SCHEDULE_SM_DECOY_NOTE).
    """
    return or_assert_namespace("OR_K1_OVERFLOW_ATTACHMENT", NS_INDIVIDUAL)


# ⚠ THE COMPUTATION ORDER FOR THE WHOLE ENGAGEMENT, from the OR-K-1 instructions:
# 'If the entity is making the election to pay tax at the entity level for
# calendar year 2025, COMPLETE FORM OR-21 AND ASSOCIATED SCHEDULES FIRST.'
OR_ENGAGEMENT_ORDER = (
    "Form OR-65 / Form OR-20-S", "Form OR-21 (+ OR-21-MD / -AP / -MD-PT)",
    "Schedule OR-21-K-1", "Schedule OR-K-1 (PTE-E items SUPPRESSED)",
    "Form OR-19 / Form OR-OC",
)
# ⚠ U17 -- A GENUINE CIRCULAR REFERENCE. OR-K-1 says do OR-21 first; OR-21-MD
# column r sources member shares from 'Schedule OR-K-1, Part III, lines 1 through
# 11, Oregon column'; and OR-21-MD itself says 'Complete Form OR-21 before
# completing this schedule.' Resolvable in practice (the OR-K-1 INCOME lines are
# computable before the PTE-E items are known; only the PTE-E addition/credit
# SUPPRESSION depends on OR-21) but THE DOR NEVER SAYS SO. Low risk, high
# annoyance for a dependency-ordered engine.
OR_U17_CIRCULARITY = (
    "Schedule OR-K-1 <-> Schedule OR-21-MD. Practical resolution: compute OR-K-1 lines 1-11 first, "
    "then Form OR-21 and its schedules, then apply the OR-K-1 PTE-E suppression. NOT stated by the DOR."
)


# ═══════════════════════════════════════════════════════════════════════════
# DUE DATES -- THREE FORMS, THREE STATUTORY RULES, FIVE ACTUAL DATES
#
# ⚠ A MISSED PTE-E DUE DATE IS IRRECOVERABLE: 'The election may not be made
# retroactively.'
# ⚠ THERE IS NO ORS CHAPTER 316 DUE-DATE SECTION AT ALL. ORS 316.457 is
# 'Department may require...'. Form OR-21's April 15 arrives ONLY by the chain
# 2021 Or. Laws ch. 589 §3(8) -> ORS 314.385(1)(a) -> IRC §6072(a). DO NOT read
# it as 'Oregon statute says April 15.'
# ⚠ OREGON'S CORPORATE RETURNS ARE DUE ONE MONTH LATER THAN THE FEDERAL RETURN
# (ORS 314.385(1)(b), restated at (1)(d) for the no-federal-return case).
# ═══════════════════════════════════════════════════════════════════════════
OR_DUE_DATES: dict[int, dict] = {
    2025: {
        "OR_19": {"due": "2026-03-02", "extended": None,
                  "rule": "last day of the 2nd month after the entity's year end (Feb 28, 2026 is a Saturday)",
                  "derived": False},
        FORM_CODE_OR65: {"due": "2026-03-16", "extended": "2026-09-15",
                         "rule": "ORS 314.724(1) - the federal partnership date (March 15, 2026 is a Sunday)",
                         "derived": False,
                         "note": "The extension is SELF-DECLARING - checkbox (f) plus the extended date typed on the face. NO REQUEST IS FILED WITH ANYONE."},
        FORM_CODE_OR20S: {"due": "2026-04-15", "extended": "2026-10-15",
                          "rule": "ORS 314.385(1)(b) - the 15th day of the month FOLLOWING the federal due date",
                          "derived": True,
                          "note": ("⚠ THE RULE IS CONFIRMED; THE DATE IS DERIVED. The string 'April 15, 2026' "
                                   "appears NOWHERE in the OR-20-S instructions as a return due date (its two "
                                   "occurrences are a 2030 credit sunset and the estimated-payment calendar). "
                                   "Derivation: federal 1120-S 3/15/26 (Sun) -> 3/16/26 -> +1 month, 15th = "
                                   "4/15/26. The EXTENDED date is derived the same way (federal extended "
                                   "9/15/26 -> Oregon 10/15/26). U18.")},
        FORM_CODE_OR21: {"due": "2026-04-15", "extended": "2026-09-15",
                         "rule": "2021 Or. Laws ch. 589 §3(8) -> ORS 314.385(1)(a) -> IRC 6072(a) - the ORS ch. 316 date",
                         "derived": False, "extended_unresolved": True,
                         "note": ("⚠⚠ THE EXTENDED DATE IS NEVER STATED (U7). 'Oregon will honor the same "
                                  "extension request' as the federal 1065/1120-S extension, which runs to "
                                  "September 15, 2026 - but six months from Oregon's OWN April 15 gives "
                                  "October 15, 2026, which is exactly the construction Pub. OR-OC uses "
                                  "EXPLICITLY for the composite return. The DOR's Example 3 (a July 29 filing) "
                                  "does not discriminate. DEFAULT TO THE EARLIER DATE (September 15) AND "
                                  "DIAGNOSE - a missed filing deadline here is irrecoverable. Payment is due "
                                  "4/15/2026 regardless of any extension to file.")},
        "OR_OC": {"due": "2026-04-15", "extended": "2026-10-15",
                  "rule": "the tax year and due date of the MAJORITY OF THE ELECTING OWNERS", "derived": False},
    },
}


def or_due_date(form_code: str, year: int = FORM_TAX_YEAR) -> dict:
    """The due-date record for a form. Refuses an unkeyed tax year."""
    table = _yk(OR_DUE_DATES, year)
    if form_code not in table:
        raise KeyError(f"no Oregon due date seeded for {form_code!r}; known: {sorted(table)}")
    return table[form_code]


# ⚠ FIVE DISTINCT DUE DATES AND NINE DISTINCT DESTINATIONS IN ONE ENGAGEMENT.
# ⚠ A RECURRING DOR RULE ACROSS EVERY FORM: NEVER SEND A VOUCHER WITH A RETURN.
# Stated on the OR-65 face, the OR-20-S face, OR-20-S Instr. p. 6, the OR-21
# instructions and Pub. OR-OC. A build that always attaches a voucher is WRONG ON
# ALL FIVE FORMS.
OR_VOUCHER_NEVER_WITH_RETURN: dict[int, bool] = {2025: True}
OR_VOUCHERS: dict[str, dict] = {
    "OR-65-V": {"number": "150-101-066", "types": ["Original return or extension", "Amended return"],
                "mail_to": "PO Box 14950",
                "note": "⚠ TWO types only - there is NO `Estimated payment` box, consistent with 'Estimated payments are not required' for Form OR-65."},
    "OR-20-V": {"number": "150-102-172",
                "types": ["Original return or extension", "Estimated payment", "Amended return"],
                "mail_to": "PO Box 14950"},
    "OR-21-V": {"number": "150-107-172",
                "types": ["Original return or extension", "Estimated payment", "Amended return"],
                "mail_to": "PO Box 14950",
                "note": "⚠ Published as a year-agnostic 'General' item - a gap-check filtered on Year eq '2025' will wrongly report it MISSING. Union Year=2025 with Year=General."},
    "OR-19-V": {"number": "150-101-185", "types": [], "mail_to": "PO Box 14950"},
    "OR-OC-V": {"number": "150-101-150", "types": ["Original return"], "mail_to": "PO Box 14950"},
}
OR_RETURN_MAILBOXES: dict[str, str] = {
    FORM_CODE_OR65: "PO Box 14555, Salem OR 97309-0940 (ONE address regardless of refund or balance due)",
    FORM_CODE_OR20S + "_tax_due": "PO Box 14790, Salem OR 97309-0470",
    FORM_CODE_OR20S + "_refund": "PO Box 14777, Salem OR 97309-0960",
    FORM_CODE_OR21: "PO Box 14380, Salem OR 97309-5075 (paper by REQUEST ONLY - and see U23)",
    "OR_19": "PO Box 14950, Salem OR 97309-0950",
    "OR_OC_with_payment": "PO Box 14555, Salem OR 97309-0940 (⚠ THE SAME BOX AS FORM OR-65 - the address alone does not identify the return)",
    "OR_OC_without_payment": "PO Box 14700, Salem OR 97309-0930",
    "OR_OC_TR": "PO Box 14999, Salem OR 97309-0990",
}


# ═══════════════════════════════════════════════════════════════════════════
# NONRESIDENT OWNERS -- withholding, affidavit, composite. Context for the two
# entity specs; the forms themselves are outside the three specs authored here.
# ═══════════════════════════════════════════════════════════════════════════
OR19_WITHHOLDING_RATE_INDIVIDUAL: dict[int, str] = {2025: "0.099"}   # ORS 316.037 top marginal
OR19_WITHHOLDING_RATE_CORP_LOW: dict[int, str] = {2025: "0.066"}
OR19_WITHHOLDING_RATE_CORP_HIGH: dict[int, str] = {2025: "0.076"}
OR19_DE_MINIMIS: dict[int, int] = {2025: 1_000}
OR19_DE_MINIMIS_AUTHORITY = (
    "ORS 314.784(1)(a), verbatim, `[2005 c.387 §4]` - unamended since 2005: 'The nonresident owner "
    "has a share of distributive income that is less than $1,000 for the tax year of the "
    "pass-through entity.' PER OWNER, per the PTE's tax year, on the DISTRIBUTIVE SHARE (not the "
    "distribution), STRICTLY LESS THAN. ⚠ U15: the statute says 'distributive income'; the "
    "instructions narrow it to 'OREGON-SOURCE distributive income'. The DOR reading is narrower "
    "and taxpayer-favourable and is consistent with ORS 314.781(2)'s own measure. BUILD TO THE "
    "INSTRUCTIONS."
)
# ⚠ THE GROSS-UP RULE: 'Tax payments are required on the nonresident owner's
# ENTIRE share of Oregon-source income, NOT JUST THE AMOUNT EXCEEDING $1,000.'
OR19_GROSS_UP: dict[int, bool] = {2025: True}
# ⚠ THE PTE-E ELECTION TURNS WITHHOLDING OFF -- WITH A CARVE-OUT that is exactly
# the OR-20-S line 1a/1b population: 'Withholding may be required for other types
# of taxes not included on the PTE elective tax return, such as BUILT-IN GAINS OR
# EXCESS NET PASSIVE INCOME TAX.'
OR19_PTE_E_SUPPRESSES_WITHHOLDING: dict[int, bool] = {2025: True}
OR19_PTE_E_CARVE_OUT = "built-in gains and excess net passive income tax still require withholding"
OR19_AFFIDAVIT_RESUBMIT_TRIGGER_PCT: dict[int, int] = {2025: 10}
OR19_AFFIDAVIT_IS_PERSISTENT: dict[int, bool] = {2025: True}
OR_OC_KICKER_PCT: dict[int, str] = {2025: "0.09863"}
OR_OC_CPAR_RATE_INDIVIDUAL: dict[int, str] = {2025: "0.099"}
OR_OC_CPAR_RATE_CORPORATE: dict[int, str] = {2025: "0.076"}


def or19_withholding_rate(owner_kind: str, oregon_source_income: float,
                          year: int = FORM_TAX_YEAR) -> float:
    """ORS 314.781(2)-(3). Individuals at the top marginal rate; corporations at
    the ORS 317.061 / 318.020 rates."""
    if owner_kind == "individual":
        return float(oregon_source_income) * float(_yk(OR19_WITHHOLDING_RATE_INDIVIDUAL, year))
    if owner_kind == "c_corp":
        bp = _yk(OR20S_RATE_BREAKPOINT, year)
        inc = float(oregon_source_income)
        if inc <= bp:
            return inc * float(_yk(OR19_WITHHOLDING_RATE_CORP_LOW, year))
        return float(_yk(OR20S_RATE_BASE_CONSTANT, year)) + \
            (inc - bp) * float(_yk(OR19_WITHHOLDING_RATE_CORP_HIGH, year))
    raise ValueError(f"owner_kind must be 'individual' or 'c_corp'; got {owner_kind!r}")


def or19_withholding_required(pte_e_election: bool, oregon_source_share: float,
                              affidavit_on_file: bool, joins_composite: bool,
                              owner_makes_own_estimates: bool,
                              has_big_or_enpi: bool = False,
                              year: int = FORM_TAX_YEAR) -> bool:
    """The four statutory exceptions plus the PTE-E carve-out."""
    if pte_e_election and not has_big_or_enpi:
        return False
    if float(oregon_source_share) < _yk(OR19_DE_MINIMIS, year):
        return False
    if affidavit_on_file or joins_composite or owner_makes_own_estimates:
        return False
    return True


# ═══════════════════════════════════════════════════════════════════════════
# ⚠⚠ THE LOCAL LAYER -- PORTLAND / MULTNOMAH / METRO. RED-DEFER FOR v1 (D-12 W8),
# NAMED EXPLICITLY. A GROUP E ROUTING ITEM WITH NO DECISION TAKEN.
#
# Neither silently included nor silently excluded. Four separate returns, a
# SEPARATE AGENCY (City of Portland Revenue Division - 'we are a separate
# government agency from the Oregon Department of Revenue'), a SEPARATE MeF
# PROGRAM with its own ATS, its own FTA-SES schemas and its own vendor list
# (~13 competitors already approved for TY2025). NOTHING ROUTES THROUGH OREGON DOR.
# ═══════════════════════════════════════════════════════════════════════════
OR_LOCAL_IN_V1_SCOPE: dict[int, bool] = {2025: False}
OR_LOCAL_DECISION_STATUS = "GROUP E ROUTING ITEM - NO DECISION TAKEN (campaign D-12). RED-DEFER for v1."
OR_LOCAL_RETURNS: dict[str, dict] = {
    "P-2025": {"module": M_1065, "covers": "City of Portland Business License Tax + Multnomah County BIT (combined)",
               "form_rev": "01/21/2026", "instr_rev": "12/15/2025"},
    "SC-2025": {"module": M_1120S, "covers": "City + County (combined)",
                "form_rev": "01/21/2026", "instr_rev": "12/15/2025"},
    "METBIT-65": {"module": M_1065, "covers": "Metro Supportive Housing Services BIT - A SEPARATE RETURN",
                  "instr_rev": "12/15/2025"},
    "METBIT-20S": {"module": M_1120S, "covers": "Metro SHS BIT - A SEPARATE RETURN",
                   "instr_rev": "07/31/2026"},
}
# ⚠⚠ BUILD-CORRUPTING IF REUSED. THE METBIT FORMS ARE NOT A RENUMBERED COPY OF
# P/SC. On METBIT-65 and METBIT-20S, PART II LINE 7 IS
# `Non-business income or loss subtraction`. A spec reusing the P/SC map writes
# ORDINARY INCOME INTO THE NON-BUSINESS-INCOME SUBTRACTION AND THE RETURN STILL
# FOOTS.
OR_METBIT_LINE_MAP: dict[str, dict] = {
    "P-2025": {"starting_line": "Part II line 7", "label": "Ordinary net income or (loss)",
               "schedule_k_pull_line": "line 10", "federal_source": "Form 1065 (2025) line 23"},
    "SC-2025": {"starting_line": "Part II line 7", "label": "Ordinary net income or (loss)",
                "schedule_k_pull_line": "line 10", "federal_source": "Form 1120-S (2025) line 22"},
    "METBIT-65": {"starting_line": "Part II line 4", "label": "Ordinary income or (loss) from Form 1065",
                  "schedule_k_pull_line": "line 6", "federal_source": "Form 1065 (2025) line 23",
                  "line_7_is": "Non-business income or loss subtraction"},
    "METBIT-20S": {"starting_line": "Part II line 4", "label": "Ordinary income or (loss) from Form 1120-S",
                   "schedule_k_pull_line": "line 6", "federal_source": "Form 1120-S (2025) line 22",
                   "line_7_is": "Non-business income or loss subtraction"},
}
# ⚠ THE PRONG CORRECTION. LIC-2.05 (adopted 2024-04-16) has TWO prongs and only
# the SECOND reaches the four PTE returns.
OR_LIC_205_PREPARER_PRONG_SCOPE = "PERSONAL income tax returns ONLY (Form SP / MC-40 / MC-40-NP / MET-40 / MET-40-NP)"
OR_LIC_205_BUSINESS_PRONG_TRIGGER = (
    "'All businesses required to electronically file their federal tax return are required to "
    "electronically file their business license tax and/or business income tax returns.' THE "
    "TRIGGER IS A PROPERTY OF THE TAXPAYER, NOT THE PREPARER. Federal predicate: 26 CFR "
    "301.6011-3(a) for partnerships (>=10 returns in aggregate for the calendar year, OR more than "
    "100 partners) and 26 CFR 301.6037-2(a) for S corporations (>=10 returns in aggregate). ⚠ 26 "
    "CFR 301.6011-5 is the FORM 1120 rule and does NOT reach 1120-S. LIC-2.05 contains NO NUMERIC "
    "THRESHOLD OF ITS OWN - both prongs incorporate federal law by reference. Because the count "
    "AGGREGATES W-2s, 1099s, employment and excise returns, nearly every real PTE client is "
    "caught, so the force of the scope call is UNCHANGED; only its mechanism changes."
)
OR_LOCAL_EFILE_MANDATORY_FROM: dict[str, int] = {
    "P-2025": 2025, "SC-2025": 2025, "METBIT-65": 2025, "METBIT-20S": 2025,
}
# TY2025 local rates -- recorded so the deferral diagnostic can be specific.
OR_LOCAL_RATES: dict[int, dict] = {
    2025: {
        "portland_business_license": {"rate": "0.026", "minimum": 100, "exempt_under_gross_receipts": 50_000},
        "multnomah_county_bit": {"rate": "0.020", "minimum": 100, "exempt_under_gross_receipts": 100_000},
        "metro_shs_bit": {"rate": "0.010", "minimum": 100, "applies_over_gross_receipts": 5_000_000},
    },
}
# ⚠ TWO DIFFERENT 75% RULES, NOT ONE, on three computations.
OR_LOCAL_NOL_CAP_PCT: dict[int, str] = {2025: "0.75"}
OR_LOCAL_NOL_CAP_APPLIES_ON = ("City line 29", "County line 19", "METBIT line 12")
OR_LOCAL_OWNER_COMP_CAP_PCT: dict[int, str] = {2025: "0.75"}
OR_LOCAL_OWNER_COMP_DOLLAR_CAP: dict[int, dict] = {2025: {"city": 160_500, "county": 158_500}}
OR_LOCAL_OWNER_COMP_NOTE = (
    "⚠ The owner's compensation deduction is ITSELF capped at 75% of net business income, "
    "INDEPENDENTLY of the NOL cap: 'A deduction of up to 75% of the net business income (line 13) "
    "is allowed for GPs but cannot exceed $158,500 for the County per GP listed on line 9.' The "
    "per-owner DOLLAR cap is a CEILING ON AN ALREADY-LIMITED FIGURE - applying only the dollar cap "
    "OVER-DEDUCTS. Does not apply to the Metro return."
)
OR_LOCAL_EXEMPTION_CODE_COUNT: dict[int, int] = {2025: 12}   # 1, 2, 3, 6-13, 99 -- code 4 removed for TY2025
OR_LOCAL_FORWARD_ONLY = (
    "⚠ NOT TY2025: the City gross-receipts exemption rises to $75,000 (TY2026) and $100,000 "
    "(TY2027) per PCC 7.02.400 as amended by Ordinance 192163, effective May 8, 2026."
)


def or_local_line_map(local_form: str) -> dict:
    """⚠ REFUSES to hand back a P/SC map for a METBIT form. See OR_METBIT_LINE_MAP."""
    if local_form not in OR_METBIT_LINE_MAP:
        raise KeyError(f"unknown local return {local_form!r}; known: {sorted(OR_METBIT_LINE_MAP)}")
    return OR_METBIT_LINE_MAP[local_form]


# Transit self-employment -- DOR-administered, triggered by OR-65 lines 7B/7D.
OR_TRANSIT_RATES: dict[int, dict] = {
    2025: {"OR-TM": {"rate": "0.008237", "form": "150-555-001", "threshold_net_se_earnings": 400},
           "OR-LTD": {"rate": "0.0080", "form": "150-560-001", "threshold_net_se_earnings": 400}},
}
# ⚠ 7A and 7C (EMPLOYEES) have NO return consequence for the partnership -
# employer transit payroll tax is a payroll-side obligation. ONLY 7B and 7D
# (PARTNERS' self-employment) produce a return. A diagnostic that fires on 7A/7C
# is WRONG.
OR65_TRANSIT_RETURN_TRIGGER_LINES = ("7B", "7D")
OR65_TRANSIT_NO_RETURN_LINES = ("7A", "7C")


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY TOPICS
# ⚠ topic_name is a CharField(255). Wave-3 harnesses caught four values over the
# cap that were INVISIBLE IN SQLITE and would have been Postgres DataErrors in
# prod. These are deliberately short; validate_or.py measures them against the
# LIVE model _meta rather than a hardcoded number.
# ═══════════════════════════════════════════════════════════════════════════
AUTHORITY_TOPICS: list[tuple[str, str]] = [
    ("or_pte_entity_returns",
     "Oregon Form OR-65 and Form OR-20-S: the $150 minimum tax, the excise/income split, "
     "Schedule I vs Schedule SM, and the opposite penalty postures."),
    ("or_pte_e_elective_tax",
     "Oregon Form OR-21 PTE-E elective tax: annual revocable election, 9%/9.9% rate, "
     "OR-21-MD/-AP/-MD-PT, and the three owner legs (167 / 900 / 387)."),
    ("or_modification_code_namespaces",
     "Oregon's TWO disjoint modification code sets: Publication OR-CODES (individual) vs "
     "Schedule OR-ASC-CORP (corporate). Twelve numbers collide."),
    ("or_conformity_hybrid",
     "Oregon's hybrid IRC conformity: rolling for the definition of taxable income, "
     "fixed 12/31/2023 for the ORS 314.011(2)(c) enumeration (TY2025)."),
    ("or_apportionment",
     "Schedule OR-AP (single sales factor, with vestigial property/payroll) and Schedule "
     "OR-21-AP (sales factor only)."),
    ("or_nonresident_owners",
     "Oregon nonresident owner paths: Form OR-19 withholding, Form OR-19-AF affidavit, "
     "Form OR-OC composite, and the $1,000 de-minimis."),
    ("or_local_portland_metro",
     "The Portland / Multnomah / Metro business income taxes - a separate agency, a separate "
     "MeF program, four separate PTE returns."),
]

# ⚠ ALREADY SEEDED IN RS -- REUSE, NEVER RE-CREATE (campaign D-10). Oregon's
# JurisdictionConformitySource row is live with conformity_type = 'partial', so
# these anchors resolve immediately in prod. They WILL warn on a throwaway
# SQLite harness DB, which is expected and is asserted for in validate_or.py.
EXISTING_SOURCES_TO_REFERENCE: list[str] = [
    "OR_ORS_317_010_CONFORMITY",   # the corporate-excise conformity statute
    "OR_2025_PUB_OR17",            # THE DOR authority for Oregon's TY2025 posture
    "OR_ORS_317_301_DEPR",         # the ONLY 168(k)/179 disconnect - and its window is CLOSED
]

AUTHORITY_SOURCES: list[dict] = [
    # ---------------------------------------------------------------- statute
    {
        "source_code": "OR_ORS_314_011_CONFORMITY",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("ORS 314.011(2)(b)-(c) (2025 Edition) - the conformity statute that GOVERNS the "
                  "entire Oregon PTE module (partnerships, S corporations, apportionment and the "
                  "PTE-E tax), and the enumerated list of FROZEN sections"),
        "citation": "ORS 314.011(2)(b)-(c), ORS 2025 Edition (amendment credit ends 2024 c.75 s.18)",
        "issuer": "Oregon Legislative Assembly",
        "official_url": "https://www.oregonlegislature.gov/bills_laws/ors/ors314.html",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.9,
        "topics": ["or_conformity_hybrid"],
        "notes": ("EXTENDS or_conformity.md, which verified ORS 316.012 and 317.010(7) but did NOT "
                  "reach ORS 314.011. ⚠ Retrieve the chapter page with `curl --compressed` - a "
                  "plain fetch is SILENTLY TRUNCATED and drops the body of ORS 314.011-314.037."),
        "excerpts": [
            {"excerpt_label": "ORS 314.011(2)(b) - the two prongs, verbatim",
             "location_reference": "ORS ch. 314, 2025 Edition",
             "excerpt_text": ("Except where the Legislative Assembly has provided otherwise, a reference to the "
                              "laws of the United States or to the Internal Revenue Code refers to the laws of "
                              "the United States or to the Internal Revenue Code as they are amended and in "
                              "effect: (A) On December 31, 2023; or (B) If related to the definition of taxable "
                              "income, as applicable to the tax year of the taxpayer."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ DO NOT FLATTEN. Prong (B) is ROLLING and it swallows every "
                              "income-measurement provision, so OBBBA flows into TY2025 automatically - "
                              "100% bonus, $2.5M/$4M IRC 179, NO add-back. The DOR one-liner in the OR-20-S "
                              "booklet states this BACKWARDS.")},
            {"excerpt_label": "ORS 314.011(2)(c) - the ENUMERATED frozen sections, verbatim",
             "location_reference": "ORS ch. 314, 2025 Edition",
             "excerpt_text": ("(c) With respect to ORS 314.105, 314.256 (relating to proxy tax on lobbying "
                              "expenditures), 314.260 (1)(b), 314.302, 314.306, 314.330, 314.360, 314.362, "
                              "314.385, 314.402, 314.410, 314.412, 314.525, 314.767 (7), 314.771 and 314.772 "
                              "and other provisions of this chapter, except those described in paragraph (b) "
                              "of this subsection, any reference to the laws of the United States or to the "
                              "Internal Revenue Code means the laws of the United States relating to income "
                              "taxes or the Internal Revenue Code as they are amended on or before December "
                              "31, 2023, even when the amendments take effect or become operative after that "
                              "date, except where the Legislative Assembly has specifically provided otherwise."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("BUILD TO THE ENUMERATION, NOT TO A CATEGORY JUDGMENT. Every frozen provision "
                              "here is ADMINISTRATIVE or MECHANICAL; none moves an income figure on a TY2025 "
                              "Oregon PTE return. Note Oregon's CORPORATE NOL rules live in ORS 317.476/479, "
                              "NOT in chapter 314, so this freeze list does not reach them.")},
        ],
    },
    {
        "source_code": "OR_SB1507_2026_CH142",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "OR",
        "tax_year_start": 2026,
        "title": ("Enrolled SB 1507 = 2026 Oregon Laws ch. 142, secs. 35, 41 and 48 - moves Oregon's "
                  "fixed IRC conformity date to 12/31/2025 and decouples from IRC 168(k), BOTH "
                  "EFFECTIVE TY2026. ⚠ THE STALENESS TRIPWIRE FOR THIS ENTIRE SPEC."),
        "citation": "2026 Or. Laws ch. 142 secs. 35, 41, 48(1) (SB 1507; Senate 2026-02-16, House 2026-02-25)",
        "issuer": "Oregon Legislative Assembly",
        "official_url": "https://olis.oregonlegislature.gov/",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.7,
        "topics": ["or_conformity_hybrid"],
        "notes": ("⚠⚠ EVERY FIGURE IN THIS SPEC IS TY2025-KEYED AND SB 1507 INVALIDATES THE FROZEN "
                  "SIDE BY STATUTE FOR TY2026. A TY2026 Oregon PTE spec must model a full dual-basis "
                  "depreciation regime; a TY2025 one must NOT. Residual [UNVERIFIED]: whether sec. "
                  "48(2)-(3)'s retroactivity machinery reaches a TY2025 return is NOT SETTLED - "
                  "settle by the LRO paper 'An Analysis of Changes in Federal Tax Laws for the Year "
                  "2025' (OLIS 2026R1 doc 312823)."),
        "excerpts": [
            {"excerpt_label": "SB 1507 sec. 48(1) applicability, verbatim",
             "excerpt_text": ("Except as provided in subsections (2) and (3) of this section, the amendments "
                              "to statutes by sections 16 to 47 of this 2026 Act apply to transactions or "
                              "activities occurring on or after January 1, 2026, in tax years beginning on or "
                              "after January 1, 2026."),
             "is_key_excerpt": True, "effective_year_start": 2026,
             "summary_text": ("Section 35 is INSIDE that range, so TY2025 STAYS at 12/31/2023 and TY2026 "
                              "MOVES to 12/31/2025.")},
        ],
    },
    {
        "source_code": "OR_2021_CH589_PTE_E",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "OR",
        "tax_year_start": 2022, "tax_year_end": 2027,
        "title": ("2021 Oregon Laws ch. 589 (as amended by 2022 c.82 s.3) - the entire PTE-E tax, "
                  "compiled as notes following ORS 314.140"),
        "citation": "2021 Or. Laws ch. 589 secs. 1-6 and 10-13, ORS 2025 Edition, notes following ORS 314.140 [2021 c.589 s.3; 2022 c.82 s.3]",
        "issuer": "Oregon Legislative Assembly",
        "official_url": "https://www.oregonlegislature.gov/bills_laws/ors/ors314.html",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.9,
        "topics": ["or_pte_e_elective_tax"],
        "notes": ("Vintage chain, run and confirmed: ch. 589 sec. 3 was amended by 2022 c.82 sec. 3, and "
                  "the applicability note (2022 c.82 sec. 16(2) as amended by 2024 c.52 sec. 5(2)) puts "
                  "TY2025 in scope, so the quoted text IS the TY2025 text. ⚠ VINTAGE-CHECK NOTE, the "
                  "REVERSE of the usual trap: the ORS 2025 Edition note at ch. 589 sec. 10 still shows "
                  "the PRE-SB-1510 window ('before January 1, 2026') while the DOR's Rev. 04-01-26 "
                  "instructions show 'before January 1, 2028'. TY2025 falls inside BOTH, so there is no "
                  "TY2025 conflict - recorded so a later pass does not read the stale note and wrongly "
                  "conclude the PTE-E expired."),
        "excerpts": [
            {"excerpt_label": "sec. 3(8) - THE SEPARATE-RETURN PROOF, verbatim",
             "excerpt_text": ("Pass-through entities that have made an election under this section shall file "
                              "an entity tax return. The return shall be accompanied by payment and shall be "
                              "due on the date applicable to returns due under ORS chapter 316, as provided "
                              "in ORS 314.385."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("Quoted character for character and re-verified. This is why OR_21 is its own "
                              "spec: a separate return on the ORS ch. 316 (April 15) date while OR-65 is due "
                              "March 16 and OR-20-S April 15 by a completely different route.")},
            {"excerpt_label": "sec. 3(2) - ANNUAL, REVOCABLE, NOT RETROACTIVE, verbatim",
             "excerpt_text": ("The election shall be made annually on or before the due date, including "
                              "extensions, of the pass-through entity's return, in the form and manner "
                              "prescribed by the Department of Revenue. The election may not be made "
                              "retroactively. The members of a pass-through entity may revoke an election "
                              "under this section for a tax year only on or before the due date of the "
                              "pass-through entity's return for that tax year, and only if the revocation is "
                              "agreed to by all members who are members at the time of the revocation."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ NOT BINDING ON FUTURE YEARS - the opposite of Mississippi's. ⚠ U22: the "
                              "REVOCATION sentence has NO extension language while the ELECTION sentence in "
                              "the same subsection says 'including extensions'. The DOR instructions add "
                              "'including extension' to the revocation rule anyway. Build to the "
                              "instructions and diagnose.")},
            {"excerpt_label": "sec. 3(6) - the two-tier rate, verbatim",
             "excerpt_text": ("The rate of the tax imposed by and computed under this section is: (a) Nine "
                              "percent of the first $250,000, or fraction thereof, of the sum of distributive "
                              "proceeds; and (b) Nine and nine-tenths percent of any amount of distributive "
                              "proceeds in excess of $250,000."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ The 9% first tier is BELOW Oregon's 9.9% individual top rate - a genuine "
                              "rate BENEFIT, not a rate-match PTET. Continuous at the breakpoint: both "
                              "branches give $22,500 at exactly $250,000.")},
        ],
    },
    {
        "source_code": "OR_ORS_314_385_DUE",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": "ORS 314.385(1)(a)-(d) (2025 Edition) - ONE section, TWO different due-date rules",
        "citation": "ORS 314.385(1), ORS 2025 Edition (last amended 2016 c.33 s.17a)",
        "issuer": "Oregon Legislative Assembly",
        "official_url": "https://www.oregonlegislature.gov/bills_laws/ors/ors314.html",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.9,
        "topics": ["or_pte_entity_returns", "or_pte_e_elective_tax"],
        "notes": ("⚠ THERE IS NO ORS CHAPTER 316 DUE-DATE SECTION AT ALL (ORS 316.457 is 'Department "
                  "may require...'). Form OR-21's April 15 arrives ONLY via ch. 589 sec. 3(8) -> "
                  "314.385(1)(a) -> IRC 6072(a). Do not read it as 'Oregon statute says April 15.' "
                  "Subsection (1)(d) governs the no-federal-return case and restates the one-month "
                  "corporate shift."),
        "excerpts": [
            {"excerpt_label": "ORS 314.385(1)(a)-(b) - the ch. 316 rule and the ONE-MONTH corporate shift",
             "excerpt_text": ("(a) For purposes of ORS chapter 316, returns shall be filed with the "
                              "Department of Revenue on or before the due date of the corresponding federal "
                              "return for the tax year as prescribed under the Internal Revenue Code and the "
                              "regulations adopted pursuant thereto. (b) For purposes of ORS chapters 317 and "
                              "318, returns shall be filed with the department on or before the 15th day of "
                              "the month following the due date of the corresponding federal return for the "
                              "tax year, as prescribed under the Internal Revenue Code and the regulations "
                              "adopted pursuant thereto."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": "Oregon's corporate returns are due ONE MONTH LATER than the federal return."},
        ],
    },
    {
        "source_code": "OR_ORS_314_724_725_PTNSHP",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("ORS 314.712(1), 314.724 and 314.725 (2025 Edition) - partnerships are not subject "
                  "to tax; the filing trigger; the ENTIRE $150 privilege tax; the failure-to-file penalty"),
        "citation": "ORS 314.712(1) [2019 c.132 s.7]; ORS 314.724(1),(3); ORS 314.725 [2009 c.745 s.3], ORS 2025 Edition",
        "issuer": "Oregon Legislative Assembly",
        "official_url": "https://www.oregonlegislature.gov/bills_laws/ors/ors314.html",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.9,
        "topics": ["or_pte_entity_returns"],
        "excerpts": [
            {"excerpt_label": "ORS 314.725 - the whole of Oregon's partnership entity-level tax, verbatim",
             "excerpt_text": ("Each partnership transacting business in this state shall, for the privilege of "
                              "carrying on or doing business by it within this state, include with the filing "
                              "of the return required under ORS 314.724 payment of a minimum tax of $150."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025},
            {"excerpt_label": "ORS 314.724(3) - the failure-to-file penalty measure, verbatim",
             "excerpt_text": ("The amount of the penalty imposed under subsection (2) of this section shall be "
                              "determined by the department by rule. However, the amount of the penalty "
                              "imposed for each month may not exceed the product of $50 multiplied by the "
                              "number of persons who were partners in the partnership during any part of the "
                              "taxable year, and the total amount of the penalty may not exceed five times "
                              "the monthly penalty."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ 'persons who were partners DURING ANY PART OF the taxable year' is a HIGHER "
                              "count than year-end partners and higher than the line 4D K-1 count in a year "
                              "with mid-year departures. And the DOR bills it - the return must NOT carry it.")},
        ],
    },
    {
        "source_code": "OR_ORS_317_061_090_RATES",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": "ORS 317.061 (corporate rates) and ORS 317.090 (minimum tax), 2025 Edition",
        "citation": "ORS 317.061 [2013 s.s. c.5 s.1 - unamended since 2013]; ORS 317.090(1)(a),(2),(3), ORS 2025 Edition",
        "issuer": "Oregon Legislative Assembly",
        "official_url": "https://www.oregonlegislature.gov/bills_laws/ors/ors317.html",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.9,
        "topics": ["or_pte_entity_returns"],
        "excerpts": [
            {"excerpt_label": "ORS 317.061 - the rate, verbatim",
             "excerpt_text": ("The rate of the tax imposed by and computed under this chapter is: (1) Six and "
                              "six-tenths percent of the first $1 million of taxable income, or fraction "
                              "thereof; and (2) Seven and six-tenths percent of any amount of taxable income "
                              "in excess of $1 million."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025},
            {"excerpt_label": "ORS 317.090(2)(b) and (3) - the $150, and the credit bar",
             "excerpt_text": ("(2)(b) If a corporation is an S corporation, the minimum tax is $150. ... (3) "
                              "The minimum tax is not apportionable (except in the case of a change of "
                              "accounting periods), is payable in full for any part of the year during which "
                              "a corporation is subject to tax and may not be reduced, paid or otherwise "
                              "satisfied through the use of any tax credit."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ 317.090 SUPPLIES THE $150 BUT NEVER STATES THE ZERO. The zero follows from "
                              "the PREDICATE of (2) ('for the privilege of carrying on or doing business by "
                              "it within this state') read with ORS 318.020(1) and ORS 318.031. ⚠ The "
                              "TWELVE-TIER table at (2)(a) is a C-CORPORATION table and does NOT apply to "
                              "Form OR-20-S; it reappears only on Schedule OR-OC-2 per corporate composite "
                              "owner.")},
        ],
    },
    {
        "source_code": "OR_ORS_318_020_031_INCOME",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("ORS 318.020 and ORS 318.031 (2025 Edition) - THE AUTHORITY FOR THE ZERO MINIMUM TAX "
                  "on an Oregon INCOME-tax filer, keyed to the OR-20-S `Income tax` checkbox"),
        "citation": "ORS 318.020(1); ORS 318.031, ORS 2025 Edition",
        "issuer": "Oregon Legislative Assembly",
        "official_url": "https://www.oregonlegislature.gov/bills_laws/ors/ors318.html",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.8,
        "topics": ["or_pte_entity_returns"],
        "notes": ("⚠ Added by the verification pass. As originally written the brief's ONLY authority for "
                  "the zero was the DOR sentence 'There is no minimum tax for a corporate income tax "
                  "filer.' ORS 317.090(2)(b) gives only the $150."),
        "excerpts": [
            {"excerpt_label": "ORS 318.020(1), verbatim",
             "excerpt_text": ("a tax at the rate provided in ORS 317.061 upon its Oregon taxable income "
                              "derived from sources within this state, other than income for which the "
                              "corporation is subject to the tax imposed by ORS chapter 317"),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": "ORS 318.031 pulls chapter 317 into chapter 318 only 'allowance being made for the difference in imposition of the taxes.'"},
        ],
    },
    {
        "source_code": "OR_ORS_314_762_772_SCORP",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("ORS 314.762, 314.763(4)-(5), 314.766, 314.767, 314.771 and 314.772 (2025 Edition) - "
                  "built-in gains, excess net passive income, the NOL and credit constraints, LIFO "
                  "recapture, and the credits that belong to the SHAREHOLDERS"),
        "citation": "ORS 314.762(2)(c)-(d), 314.763(4)-(5) [Formerly 314.734], 314.766(1)-(5), 314.767(1)-(7), 314.771, 314.772(1), ORS 2025 Edition",
        "issuer": "Oregon Legislative Assembly",
        "official_url": "https://www.oregonlegislature.gov/bills_laws/ors/ors314.html",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.7,
        "topics": ["or_pte_entity_returns", "or_conformity_hybrid"],
        "notes": ("⚠⚠ U24 - PULL BEFORE OR-20-S LINE 15 SHIPS. ORS 314.772 carries the credit line "
                  "'[Formerly 314.752; 2022 c.34 s.11; 2022 c.115 s.15; 2023 c.298 s.11; 2023 c.490 s.23; "
                  "2025 c.36 s.3]'. IT IS THE ONLY LOAD-BEARING ORS SECTION IN THIS BRIEF WITH A "
                  "2025-SESSION AMENDMENT and its applicability date was never run down. ⚠ Also note the "
                  "brief correctly handled two RENUMBERED sections: 314.734 -> 314.763 and 314.732 -> "
                  "314.762, and read the DOR's stale cross-reference 'ORS 314.734(4) and (5)' as pointing "
                  "at ORS 314.763(4) AND (5)."),
        "excerpts": [
            {"excerpt_label": "ORS 314.772(1) - credits go to the SHAREHOLDERS, verbatim",
             "excerpt_text": ("Except as provided in ORS 314.766 (5)(b), the tax credits allowed or allowable "
                              "to a C corporation for purposes of ORS chapter 317 or 318 shall not be allowed "
                              "to an S corporation. The business tax credits allowed or allowable for "
                              "purposes of ORS chapter 316 shall be allowed or are allowable to the "
                              "shareholders of the S corporation."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ CORRECTED destination. This lands on SCHEDULE OR-K-1 LINE 19, NOT on "
                              "OR-20-S line 15. Line 15 is the narrow CARRYFORWARD-credit total, usable "
                              "against built-in-gains tax only.")},
            {"excerpt_label": "ORS 314.766(4)-(5) - the NOL and credit constraints on built-in gains",
             "excerpt_text": ("(4) Notwithstanding ORS 314.762 (2)(c), any net operating loss carryforward "
                              "arising in a taxable year for which the corporation was a C corporation shall "
                              "be allowed for purposes of the tax imposed under this section as a deduction "
                              "against the net recognized built-in gain of the S corporation for the taxable "
                              "year. For purposes of determining the amount of any such loss which may be "
                              "carried to any of the 15 subsequent taxable years, the amount of the net "
                              "recognized built-in gain shall be treated as taxable income. (5)(a) Except for "
                              "estimated and other advance tax payments and except as provided under "
                              "paragraph (b) of this subsection, no credits shall be allowed against the tax "
                              "imposed under this section."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("With ORS 314.762(2)(d) ('no carryforward, and no carryback, shall arise at the "
                              "corporate level for a taxable year for which a corporation is an S "
                              "corporation'), AN S CORPORATION CANNOT GENERATE A NEW OREGON NOL AT ALL. Line "
                              "5 can only ever draw down a pre-existing C-corp balance.")},
        ],
    },
    {
        "source_code": "OR_ORS_314_781_784_WH",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": "ORS 314.778, 314.781 and 314.784 (2025 Edition) - composite election, nonresident withholding, and the $1,000 de-minimis",
        "citation": "ORS 314.778(1)(a),(3); 314.781(2),(3),(6); 314.784(1)(a) [2005 c.387 s.4], ORS 2025 Edition",
        "issuer": "Oregon Legislative Assembly",
        "official_url": "https://www.oregonlegislature.gov/bills_laws/ors/ors314.html",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.8,
        "topics": ["or_nonresident_owners"],
        "excerpts": [
            {"excerpt_label": "ORS 314.784(1)(a) - the de-minimis, verbatim",
             "excerpt_text": ("The nonresident owner has a share of distributive income that is less than "
                              "$1,000 for the tax year of the pass-through entity;"),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("PER OWNER, per the PTE's tax year, on the DISTRIBUTIVE SHARE (not the "
                              "distribution), STRICTLY LESS THAN. ⚠ U15 - the instructions narrow it to "
                              "OREGON-SOURCE; build to the instructions. ⚠ And the GROSS-UP rule bites: once "
                              "over $1,000, payments are due on the ENTIRE share, not just the excess.")},
        ],
    },
    {
        "source_code": "OR_OAR_150_316_0155_GP",
        "source_type": "state_regulation", "source_rank": "primary_official", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": "OAR 150-316-0155, Nonresident Partners: Guaranteed Payments - THE ORDERING, explicit",
        "citation": "OAR 150-316-0155 (REV 29-2017; renumbered from 150-316.124(2) by REV 62-2016; last amended 2017)",
        "issuer": "Oregon Department of Revenue / Oregon Secretary of State OARD",
        "official_url": "https://secure.sos.state.or.us/oard/",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.5,
        "topics": ["or_apportionment", "or_nonresident_owners"],
        "notes": ("✅ CLOSES U9. ⚠ The DOR's OWN PARAPHRASE in the OR-19 instructions and Pub. OR-OC - "
                  "'attributed DIRECTLY to the owner receiving the payment' - is LOOSER THAN THE RULE and, "
                  "read alone, invites a spec author to SKIP APPORTIONMENT ENTIRELY. BUILD TO THE RULE TEXT."),
        "excerpts": [
            {"excerpt_label": "OAR 150-316-0155(1)-(2), verbatim",
             "excerpt_text": ("(1) Guaranteed payments paid to nonresident partners of a partnership that has "
                              "business activity in the state of Oregon are treated as a distributive share "
                              "of partnership income for Oregon tax purposes. In order to determine the "
                              "income attributable to Oregon sources, each nonresident partner's entire "
                              "distributive share, including the guaranteed payments, is then subject to the "
                              "allocation and apportionment provisions of ORS 314.605 to 314.675. (2) The "
                              "inclusion of guaranteed payments into a nonresident partner's share of "
                              "apportionable income is irrespective of that partner's percentage interest in "
                              "the profit or loss of the partnership."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": "APPORTION-THEN-ATTRIBUTE."},
        ],
    },
    # ---------------------------------------------------------------- DOR forms
    {
        "source_code": "OR_2025_FORM_OR65",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025, "entity_type_code": "1065",
        "title": "2025 Form OR-65, Oregon Partnership Income Return, 150-101-065",
        "citation": "Or. Form OR-65 (2025), 150-101-065 Rev. 05-29-25 ver. 01 (PDF ModDate 2026-03-16, 3 pp.)",
        "issuer": "Oregon Department of Revenue",
        "official_url": "https://www.oregon.gov/dor/forms/FormsPubs/form-or-65_101-065_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "is_filing_authority": True,
        "trust_score": 9.8, "topics": ["or_pte_entity_returns", "or_modification_code_namespaces"],
        "notes": ("COMPLETE POSITIONAL RE-DERIVE OF ALL 3 PAGES by the adversarial pass after a real "
                  "cross-state contamination incident and a quarantine-and-rebuild. VERDICT: INTACT - "
                  "every line number, letter and label matches the source; no gaps, no duplications, no "
                  "dropped lines; 0 errors. Sub-lettering checked by X-COORDINATE, not reading order: "
                  "bare N is the NAME field (x~36-42), Na is the CODE box (x~366-371), Nb is the AMOUNT "
                  "box (x~416-421). ⚠ Title discrepancy: the DOR forms-index Title reads 'Oregon "
                  "Partnership RETURN OF INCOME' every year 2017-2025 while the FACE reads 'Oregon "
                  "Partnership INCOME RETURN'. THE FACE WINS. (The parallel claim about Form OR-65-V was "
                  "FALSE and is struck - the voucher is fully self-consistent.)"),
        "excerpts": [
            {"excerpt_label": "Line 3A - the ENTIRE tax computation, verbatim",
             "location_reference": "150-101-065 p. 1",
             "excerpt_text": ("3. Partnership minimum tax. A. Tax liability. Did you answer yes to question 1 "
                              "and question 2A and/or 2B? If yes, enter $150; if no, enter 0 (see "
                              "instructions). B. Payments. Enter prepayments already made. C. Tax due. If "
                              "line 3A is more than line 3B, you have tax to pay. Line 3A minus line 3B. D. "
                              "Refund. If line 3B is more than line 3A, you have a refund. Line 3B minus "
                              "line 3A."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ The TAX gate is `1A AND (2A OR 2B)`; the FILING gate is `2A OR 2B`. TWO "
                              "DIFFERENT BOOLEANS on the same page.")},
            {"excerpt_label": "Schedule I header and the 8/8a/8b transcription trap",
             "location_reference": "150-101-065 p. 3",
             "excerpt_text": ("Schedule I-Oregon modifications to federal partnership income and credits "
                              "passed through to partners. List the name, numeric code, and amount for each "
                              "addition, subtraction, and credit (see instructions). Include schedules to "
                              "explain and compute the modifications and credits."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("Each row is bare N (NAME) + Na (CODE) + Nb (AMOUNT): 8/8a/8b, 9/9a/9b, "
                              "10/10a/10b, 11/11a/11b for additions; 12-15 subtractions; 16-19 credits. "
                              "FOUR ROWS PER SECTION. ⚠ NO TOTAL LINE ON ANY SECTION and NOTHING flows to "
                              "line 3 or anywhere else.")},
        ],
    },
    {
        "source_code": "OR_2025_FORM_OR65_INSTR",
        "source_type": "state_instruction", "source_rank": "implementation_official", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025, "entity_type_code": "1065",
        "title": "2025 Form OR-65 Instructions, 150-101-065-1",
        "citation": "Or. Form OR-65 Instructions (2025), 150-101-065-1 Rev. 10-16-25 (PDF ModDate 2026-02-18, 4 pp.)",
        "issuer": "Oregon Department of Revenue",
        "official_url": "https://www.oregon.gov/dor/forms/FormsPubs/form-or-65_101-065-1_2025.pdf",
        "current_status": "active", "is_filing_authority": True, "trust_score": 9.4,
        "topics": ["or_pte_entity_returns"],
        "notes": "⚠ FILE-NAMING TRAP: no `-instructions` segment in the URL. Pattern-guessing 404s here.",
        "excerpts": [
            {"excerpt_label": "The PENALTY POSTURE - verbatim, and it is the OPPOSITE of OR-20-S",
             "location_reference": "150-101-065-1 p. 1",
             "excerpt_text": ("Partnership failure-to-file penalty. We may assess a penalty if a partnership "
                              "doesn't file a return or fails to provide information to us as required by "
                              "law. The penalty is $50 per month per partner for each month the return is "
                              "late or incomplete, up to a maximum of five months. Don't submit a penalty "
                              "payment with the return. Penalty payments are only required if the department "
                              "assesses a penalty."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("D-12 W6. Form OR-65 has NO penalty or interest line at all (its tax block is "
                              "3A-3D); Form OR-20-S self-assesses at lines 22-24. A shared 'Oregon penalty "
                              "engine' across the two forms is IMPOSSIBLE.")},
            {"excerpt_label": "The proration chart intro and its EXCLUSION, verbatim",
             "location_reference": "150-101-065-1 p. 2",
             "excerpt_text": ("Enter $150 on line 3A unless the partnership is filing a return for a change "
                              "in accounting periods. If the 'Accounting period change' box is checked, use "
                              "this chart to determine the correct tax. ... Important: This chart doesn't "
                              "apply to other short tax year returns, such as initial returns or final "
                              "returns. The tax is $150 in those cases."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ The switch is checkbox (e) `Accounting period change`, NOT the "
                              "`Short-year return` box. And the twelve values are PUBLISHED AND ROUNDED - "
                              "13/25/38/50/63/75/88/100/113/125/138/150 - not round(150*n/12).")},
            {"excerpt_label": "Schedule I code source - THE INDIVIDUAL NAMESPACE, verbatim",
             "location_reference": "150-101-065-1 p. 2",
             "excerpt_text": ("Enter the name, numeric code, and amount for each modification or credit. "
                              "Include schedules to list additional modifications and credits or to explain "
                              "the modifications. Modification and credit codes can be found in Publication "
                              "OR-CODES and Publication OR-17, which are available on our website."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": "Form OR-65 uses the INDIVIDUAL code set. Form OR-20-S uses the CORPORATE one. C1."},
        ],
    },
    {
        "source_code": "OR_2025_FORM_OR20S",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025, "entity_type_code": "1120S",
        "title": "2025 Form OR-20-S, Oregon S Corporation Tax Return, 150-102-025",
        "citation": "Or. Form OR-20-S (2025), 150-102-025 Rev. 07-10-25 ver. 01 (PDF ModDate 2026-03-27, 8 pp.)",
        "issuer": "Oregon Department of Revenue",
        "official_url": "https://www.oregon.gov/dor/forms/FormsPubs/form-or-20-s_102-025_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "is_filing_authority": True,
        "trust_score": 9.8, "topics": ["or_pte_entity_returns", "or_modification_code_namespaces"],
        "notes": ("COMPLETE POSITIONAL RE-DERIVE OF ALL 8 PAGES. VERDICT: INTACT, ZERO ERRORS. Four "
                  "surprising claims were singled out for attack and ALL FOUR SURVIVED: (a) Schedule SM's "
                  "`K-1 line` companion fields exist on lines 1, 2, 5, 6, 7 and are ABSENT on 3 and 8; "
                  "(b) `7. Reserved` on Schedule ES is real AND the instruction conflict is real; (c) "
                  "Question I is printed TWICE in the text layer (a PDF artifact, ONE checkbox); (d) "
                  "Question J carries no line number on the face - the stale `line 21` pointer lives only "
                  "in the instructions. ⚠ FOUR SPELLINGS of this form's name are in circulation across DOR "
                  "artifacts, including the assembly list's wrong 'Oregon S Corporation INCOME Tax "
                  "Return'. USE THE FACE: 'Oregon S Corporation Tax Return'."),
        "excerpts": [
            {"excerpt_label": "The printed SKIP RULE above line 1 - why line 6 survives a zero-tax return",
             "location_reference": "150-102-025 p. 3",
             "excerpt_text": ("S corporations without built-in gains or excess net passive income, fill in "
                              "your apportionment percentage on line 6 then enter -0- on lines 7, 8, and 10 "
                              "and go to line 11."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠⚠ THE SINGLE MOST LIKELY OR-20-S BUG. Line 6 is completed EVEN AT ZERO TAX, "
                              "because it is the number every NONRESIDENT SHAREHOLDER needs to compute "
                              "their Oregon-source share. A build that short-circuits to $150 silently "
                              "drops it.")},
            {"excerpt_label": "Schedule ES lines 7 and 8 as PRINTED ON THE FACE",
             "location_reference": "150-102-025 p. 7",
             "excerpt_text": "7. Reserved ... 8. Total prepayments (carry to line 19 above)",
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("THE FACE WINS over the instruction's 'On line 7, enter the total of lines 1 "
                              "through 6'. ⚠ On Form OR-20 and OR-20-INC that same line 7 carries REFUNDABLE "
                              "credits - a shared component mapping ASC-CORP E5 -> Schedule ES line 7 writes "
                              "into a dead box AND THE ARITHMETIC STILL FOOTS.")},
        ],
    },
    {
        "source_code": "OR_2025_FORM_OR20S_INSTR",
        "source_type": "state_instruction", "source_rank": "implementation_official", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025, "entity_type_code": "1120S",
        "title": "2025 Form OR-20-S Instructions, 150-102-025-1 (incl. Appendix A codes and Appendix B rates)",
        "citation": "Or. Form OR-20-S Instructions (2025), 150-102-025-1 Rev. 10-14-25 (PDF ModDate 2026-03-25, 16 pp.)",
        "issuer": "Oregon Department of Revenue",
        "official_url": "https://www.oregon.gov/dor/forms/FormsPubs/form-OR-20-S-instructions_102-025-1_2025.pdf",
        "current_status": "active", "is_filing_authority": True, "trust_score": 9.2,
        "topics": ["or_pte_entity_returns", "or_modification_code_namespaces"],
        "notes": ("⚠ FOUR OF THE SIX FINAL-BOOKLET INSTRUCTION DEFECTS LIVE HERE (OR-DEF-1 through "
                  "OR-DEF-4). D-12 W2: the printed FACE governs and the conflict is LOGGED. ⚠ Appendix A "
                  "is the S-CORP SUBSET of the OR-ASC-CORP code universe, not the whole of it - code 341 "
                  "proves it."),
        "excerpts": [
            {"excerpt_label": "Question J - THE STALE FEDERAL POINTER, verbatim as printed",
             "location_reference": "150-102-025-1 p. 8",
             "excerpt_text": "Question J. Enter ordinary business income or loss from federal Form 1120-S, line 21.",
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("❌ STALE. 2025 Form 1120-S line 21 is 'Total deductions'; ordinary business "
                              "income is LINE 22. Stale since TY2023 (not TY2024) - three seasons across "
                              "four booklet revisions, including a July-2024 re-revision of the TY2023 "
                              "booklet that did not fix it. BUILD TO THE LABEL. U3.")},
            {"excerpt_label": "The Schedule SM firewall note - ⚠ ONE HALF OF THE DECOY",
             "location_reference": "150-102-025-1 p. 12",
             "excerpt_text": "Note: Don't use Schedule OR-ASC-CORP codes for Schedule SM additions and subtractions.",
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("TRUE AND IRRELEVANT. Schedule SM is a code-free named-line schedule; nobody "
                              "claimed it carries codes. This note polices Schedule SM and says NOTHING "
                              "about the Schedule OR-K-1 overflow attachment, where the namespaces "
                              "genuinely meet. A verification pass was fooled by exactly this and "
                              "RETRACTED its refutation.")},
        ],
    },
    {
        "source_code": "OR_2025_FORM_OR21_INSTR",
        "source_type": "state_instruction", "source_rank": "primary_official", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("2025 Form OR-21 Instructions, 150-107-114-1 - CONTAINS WORKSHEET OR-21, THE ONLY "
                  "PUBLISHED LINE LAYOUT FOR FORM OR-21 IN EXISTENCE"),
        "citation": "Or. Form OR-21 Instructions (2025), 150-107-114-1 Rev. 04-01-26 ver. 01 (PDF ModDate 2026-04-01, 10 pp.)",
        "issuer": "Oregon Department of Revenue",
        "official_url": "https://www.oregon.gov/dor/forms/FormsPubs/form-or-21-instr_107-114-1_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "is_filing_authority": True,
        "trust_score": 8.8, "topics": ["or_pte_e_elective_tax"],
        "notes": ("⚠⚠ RANKED primary_official DESPITE BEING AN INSTRUCTION BOOKLET, because THERE IS NO "
                  "FORM OR-21 FACE TO OUTRANK IT. Every OR-21 line number in this spec comes from "
                  "Worksheet OR-21 p. 10, stamped 'Do not file this worksheet.' Whether those line "
                  "numbers are the MeF schema's is an INFERENCE (U1). ⚠ Carries a banner: 'General "
                  "information on page 1 of these instructions was updated on April 1, 2026, to reflect "
                  "the passage of SB 1510 during the 2026 legislative session.' It is FIVE AND A HALF "
                  "MONTHS newer than every OR-21 schedule instruction and EIGHTEEN MONTHS newer than "
                  "Pub. OR-21-EST - PREFER IT on every point of conflict (U6)."),
        "excerpts": [
            {"excerpt_label": "The worksheet stamp, verbatim",
             "location_reference": "150-107-114-1 p. 10",
             "excerpt_text": ("Complete this worksheet to prepare to file Form OR-21. To complete your "
                              "filing, go to Revenue Online at www.oregon.gov/dor. This worksheet is for "
                              "informational purposes only. Do not file this worksheet."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025},
            {"excerpt_label": "Line 21 - OR-DEF-5, the self-contradicting instruction, verbatim as printed",
             "location_reference": "150-107-114-1 p. 4",
             "excerpt_text": ("Line 21. Enter the total of the non-apportionable income from line 17 that is "
                              "allocated to Oregon. If the PTE does all of its business activity in Oregon, "
                              "enter the amount from line 19. If the PTE must apportion its income, see "
                              "'Allocable income' in Schedule OR-21-AP Instructions to determine whether the "
                              "amount on line 19 includes income that is allocated to Oregon."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("BOTH 'line 19' references are WRONG and both resolve to LINE 17. Line 19 is a "
                              "four-decimal PERCENTAGE. BUILD TO LINE 17 - the only arithmetic that closes. "
                              "DO NOT SEED THE DOR'S LITERAL TEXT. U2.")},
            {"excerpt_label": "The zero-or-loss HARD STOP, verbatim",
             "location_reference": "150-107-114-1 p. 4",
             "excerpt_text": ("If line 22 is zero or a loss (negative number), STOP. Do not file Form OR-21. "
                              "Instead, go to the PTE's account on Revenue Online and request a refund of "
                              "all estimated PTE-E tax payments made for this tax year."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": "Must produce a CLIENT INSTRUCTION, not a return."},
        ],
    },
    {
        "source_code": "OR_2025_SCH_OR21_MD_INSTR",
        "source_type": "state_instruction", "source_rank": "primary_official", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": "2025 Schedule OR-21-MD Instructions (incl. Worksheet OR-21-MD), 150-107-112-1 - the member directory",
        "citation": "Or. Schedule OR-21-MD Instructions (2025), 150-107-112-1 Rev. 10-16-25 (PDF ModDate 2026-02-17, 3 pp.)",
        "issuer": "Oregon Department of Revenue",
        "official_url": "https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-21-md-instr_107-112-1_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 8.8,
        "topics": ["or_pte_e_elective_tax"],
        "notes": "⚠ NO FORM FACE PUBLISHED. Columns are lettered r, s, t (and l, m, n on OR-21-MD-PT). Two members per page.",
        "excerpts": [
            {"excerpt_label": "Column s - the allocation rule that CANNOT TIE OUT with a loss member, verbatim",
             "location_reference": "150-107-112-1 p. 1",
             "excerpt_text": ("For each member with a positive share of distributive proceeds in column r, "
                              "divide the member's share by the total distributive proceeds from Form OR-21, "
                              "line 22. Multiply this percentage by the total addition amount. Enter the "
                              "result in column s."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠⚠ U5, PROVEN. Both Part B tie-outs hold IF AND ONLY IF sum(positive column-r "
                              "shares) == Form OR-21 line 22, and line 22 is built from entity-level federal "
                              "Schedule K aggregates with NO positive-share filter. A ZERO share is "
                              "harmless; ONLY A NEGATIVE SHARE BREAKS IT.")},
            {"excerpt_label": "Part B tie-outs and the mandatory Caution, verbatim",
             "location_reference": "150-107-112-1 pp. 1-2",
             "excerpt_text": ("Line 4: ... The total should equal the amount of taxes paid to the State of "
                              "Oregon that were deducted on a federal return filed by the entity. Line 5: ... "
                              "The total should equal the amount of PTE-E tax on Form OR-21, line 23. "
                              "Caution: If any of the total amounts do not match the amounts from Form OR-21 "
                              "or the applicable federal return, the schedule is not complete. Make any "
                              "necessary corrections before filing Form OR-21."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ The Caution's wording is GENERIC and does NOT textually exclude line 3, so "
                              "'line 3 is untied' is an INFERENCE. Note the direction of the risk: if line 3 "
                              "= line 22 IS required, U5's contradiction gets SHARPER, not weaker.")},
        ],
    },
    {
        "source_code": "OR_2025_SCH_OR21_AP_INSTR",
        "source_type": "state_instruction", "source_rank": "primary_official", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": "2025 Schedule OR-21-AP Instructions (incl. Worksheet OR-21-AP), 150-107-111-1 - PTE-E apportionment",
        "citation": "Or. Schedule OR-21-AP Instructions (2025), 150-107-111-1 Rev. 10-16-25 (PDF ModDate 2026-02-17, 3 pp.)",
        "issuer": "Oregon Department of Revenue",
        "official_url": "https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-21-ap-instr_107-111-1_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 8.8,
        "topics": ["or_pte_e_elective_tax", "or_apportionment"],
        "notes": ("⚠⚠ SALES-FACTOR-ONLY - NO property factor, NO payroll factor, and therefore NO "
                  "double-weighted-sales alternative, even though the OR-21 line 19 instruction routes "
                  "financial institutions and public utilities to ORS 314.280. There is no OR-21 artifact "
                  "to do that on (U13 -> RED-DEFER). ⚠ DO NOT ASSUME A LINE-FOR-LINE MAPPING TO SCHEDULE "
                  "OR-AP: the sequence matches but OR-21-AP line 2 carries an EXPLICIT exclusion that "
                  "OR-AP line 14 leaves implicit."),
    },
    {
        "source_code": "OR_2025_SCH_OR21_MDPT_INSTR",
        "source_type": "state_instruction", "source_rank": "primary_official", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": "2025 Schedule OR-21-MD-PT Instructions (incl. worksheet), 150-107-110-1 - upper-tier pass-through",
        "citation": "Or. Schedule OR-21-MD-PT Instructions (2025), 150-107-110-1 Rev. 10-16-25 (PDF ModDate 2026-02-17, 2 pp.)",
        "issuer": "Oregon Department of Revenue",
        "official_url": "https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-21-md-pt_107-110-1_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 8.8,
        "topics": ["or_pte_e_elective_tax"],
        "notes": ("⚠ 'The addition and credit reported to the upper-tier PTE by the electing lower-tier "
                  "entity CAN'T BE CLAIMED ON AN ENTITY-LEVEL RETURN and must be passed through to the "
                  "upper-tier PTE's members.' A SEPARATE schedule per electing lower-tier entity. ⚠ The "
                  "three total lines at the bottom are explicitly 'For preparer use only ... not part of "
                  "the schedule' - validations, not fields. Delvio should still compute and enforce them."),
    },
    {
        "source_code": "OR_2025_SCH_OR21_K1",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": "2025 Schedule OR-21-K-1, Distributive Share of Proceeds, Addition, and Credit, 150-107-113",
        "citation": "Or. Schedule OR-21-K-1 (2025), 150-107-113 Rev. 07-24-25 ver. 01 (PDF ModDate 2026-03-16, 1 p., scanline 22322501010000)",
        "issuer": "Oregon Department of Revenue",
        "official_url": "https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-21-k-1_107-113_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "is_filing_authority": True,
        "trust_score": 9.6, "topics": ["or_pte_e_elective_tax"],
        "notes": ("THE ONLY PUBLISHED PTE-E FORM FACE - and its existence is what proves the FormsPubs "
                  "enumeration is not blind to PTE-E artifacts (23 AcroForm widgets here vs 0/0/0/0 across "
                  "the four instruction PDFs). ⚠ NOT a substitute for Schedule OR-K-1, and vice versa: an "
                  "electing PTE issues TWO Oregon K-1s per owner and NEITHER is filed."),
    },
    {
        "source_code": "OR_2025_PUB_OR_CODES",
        "source_type": "state_instruction", "source_rank": "primary_official", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": "2025 Publication OR-CODES, 150-101-432 - THE INDIVIDUAL MODIFICATION AND CREDIT CODE SET",
        "citation": "Or. Publication OR-CODES (2025), 150-101-432 Rev. 10-07-25 (PDF ModDate 2026-02-18, 5 pp.), 'Effective for tax year 2025'",
        "issuer": "Oregon Department of Revenue",
        "official_url": "https://www.oregon.gov/dor/forms/FormsPubs/Publication_OR-CODES_101-432_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.7,
        "topics": ["or_modification_code_namespaces"],
        "notes": ("⚠⚠ EXTRACTION TRAP, and it cost the verification pass time: PUBLICATION OR-CODES PRINTS "
                  "ITS CODE COLUMN ON THE RIGHT. Naive text-order extraction pairs each label with the "
                  "NEXT row's code and SILENTLY YIELDS WRONG CODES. EXTRACT IT POSITIONALLY. Full "
                  "positional sweep of all 5 pages by the adversarial pass; every row and every "
                  "'(not used)' marker re-verified. ⚠ The 'PR' legend marks credits that must be prorated "
                  "- 895, 896, 897, 898, 901 carry it; CODE 900 DOES NOT."),
        "excerpts": [
            {"excerpt_label": "Code 158 (individual) vs code 154 - THE EXEMPLAR COLLISION AND ITS TWIN",
             "location_reference": "150-101-432 pp. 1-2",
             "excerpt_text": ("154 - Gain or loss on sale of depreciable property with different basis for "
                              "Oregon. ... 158 - Interest and dividends on government bonds of other states."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠⚠ CORPORATE 158 is 'Gain or loss on disposition of depreciable property'. The "
                              "SAME economic item is 158 corporate / 154 individual, while 158 INDIVIDUAL is "
                              "an unrelated municipal-interest item. A LABEL-DRIVEN MAPPER SURVIVES; A "
                              "NUMBER-DRIVEN ONE POSTS A DEPRECIATION-BASIS DIFFERENCE TO A "
                              "MUNICIPAL-INTEREST LINE AND THE RETURN STILL FOOTS.")},
            {"excerpt_label": "The three PTE-E owner legs, verbatim locations",
             "location_reference": "150-101-432 pp. 2, 3, 5",
             "excerpt_text": ("Additions-Schedule OR-ASC, Section A or OR-ASC-NP, Section B: PTE-E tax "
                              "deducted on entity-level federal return ... 167. Subtractions: PTE-E tax "
                              "refund included on entity-level federal return ... 387. Refundable "
                              "credits-Schedule OR-ASC, Section F or OR-ASC-NP, Section I: Pass-through "
                              "entity elective taxes paid ... 900."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": "THREE legs: addition 167, refundable credit 900 (NOT PRORATED), later subtraction 387."},
        ],
    },
    {
        "source_code": "OR_2025_SCH_ASC_CORP",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025, "entity_type_code": "1120S",
        "title": "2025 Schedule OR-ASC-CORP, Oregon Adjustments for Corporation Returns, 150-102-033 (+ Instructions -033-1)",
        "citation": "Or. Schedule OR-ASC-CORP (2025), 150-102-033 Rev. 07-10-25 ver. 01 (4 pp.); Instructions 150-102-033-1 Rev. 10-14-25",
        "issuer": "Oregon Department of Revenue",
        "official_url": "https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-asc-corp_102-033_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.6,
        "topics": ["or_modification_code_namespaces"],
        "notes": ("THE CORPORATE NAMESPACE. Five sections: A additions (A1-A20, total A21 -> OR-20-S line "
                  "2); B subtractions (B1-B20, total B21 -> OR-20-S line 3); C standard credits (total C7 "
                  "-> ⚠ NOT OR-20-S); D carryforward credits (5 groups of 4 fields, D1-D20, total D21 -> "
                  "OR-20-S line 15); E refundable credits (total E5 -> ⚠ NOT OR-20-S). ⚠ ONLY 'Total used "
                  "this year' foots to D21 - a build that sums the wrong column overstates the credit by "
                  "the FULL CARRYFORWARD BALANCE. ⚠ 'Enter each code only once and add the claimed amounts "
                  "together.' ⚠ Section D's face numbering is UNRELIABLE - transcribe as five groups of "
                  "four, D1-D20."),
        "excerpts": [
            {"excerpt_label": "The Schedule SM firewall note - ⚠ THE OTHER HALF OF THE DECOY",
             "location_reference": "150-102-033-1 p. 1",
             "excerpt_text": ("Note for OR-20-S filers: This schedule and these codes are not for additions "
                              "or subtractions on Schedule SM."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("TRUE AND IRRELEVANT - see OR_2025_FORM_OR20S_INSTR. Namespace the lookup; do "
                              "not police Schedule SM.")},
            {"excerpt_label": "The credit FLOOR, which forks on the page-1 checkbox, verbatim",
             "location_reference": "150-102-033-1 p. 2",
             "excerpt_text": ("Forms OR-20, OR-20-INS, and OR-20-S (excise tax) filers: Total standard and "
                              "carryforward credits used can't reduce your excise tax below minimum tax. ... "
                              "Form OR-20-INC and OR-20-S (income tax) filers: You don't have a minimum tax. "
                              "Total standard and carryforward credits used can't reduce your income tax "
                              "below zero."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": "SAME FORM, TWO FLOORS, chosen by the excise/income checkbox."},
        ],
    },
    {
        "source_code": "OR_2025_SCH_OR_K1",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": "2025 Schedule OR-K-1, Distributive Share of Income, Deductions, Credits, etc., 150-101-002 (+ Instructions -002-1)",
        "citation": "Or. Schedule OR-K-1 (2025), 150-101-002 Rev. 09-03-25 ver. 01 (1 p., scanline 17612501010000); Instructions 150-101-002-1 Rev. 09-03-25 (2 pp.)",
        "issuer": "Oregon Department of Revenue",
        "official_url": "https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-k-1_101-002_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.6,
        "topics": ["or_pte_entity_returns", "or_modification_code_namespaces"],
        "notes": ("Positional re-derive of all 21 lines and both instruction passages, 0 errors. ONE "
                  "schedule serves PARTNERS, SHAREHOLDERS and BENEFICIARIES. ⚠ THE APPORTIONMENT "
                  "PERCENTAGE LANDS HERE, inside Part III as a column header - it has no home on the "
                  "Form OR-65 face at all."),
        "excerpts": [
            {"excerpt_label": "⚠⚠ THE CROSSING POINT - the overflow attachment carries INDIVIDUAL codes, verbatim",
             "location_reference": "150-101-002-1 p. 2",
             "excerpt_text": ("For other income, adjustments, additions, subtractions, and credits, attach a "
                              "separate schedule listing each item. Include the code for each item from "
                              "Publication OR-CODES. You can use Schedule OR-ASC for resident owners or "
                              "Schedule OR-ASC-NP for nonresident or part-year resident owners to list the "
                              "codes and amounts. ... Report the Oregon additions, subtractions, and credits "
                              "from lines 14 through 19 on Schedule OR-ASC. Use the appropriate code for "
                              "each item as shown on an attachment to Schedule OR-K-1 or as listed in "
                              "Publication OR-CODES."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠⚠ THE LOAD-BEARING PARAGRAPH FOR C1. Schedule OR-K-1 is issued by BOTH entity "
                              "forms, so an S corporation running CORPORATE codes on OR-20-S lines 2/3 must "
                              "simultaneously emit INDIVIDUAL codes here. This claim was REFUTED by an "
                              "earlier verification attempt and the REFUTATION WAS RETRACTED - the two DOR "
                              "'Schedule SM' notes are a decoy.")},
            {"excerpt_label": "The asymmetric two-column rule, verbatim",
             "location_reference": "150-101-002-1 p. 1",
             "excerpt_text": ("For Oregon residents-Complete lines 1-18 of the federal column (a) and lines "
                              "19 and 20, column (b). Don't use lines 1-18 of the Oregon column (b) for "
                              "Oregon residents. For nonresidents-Complete both the federal column (a) and "
                              "the Oregon column (b). The amounts in the federal column (a) are reported as "
                              "if the owner were a full-year Oregon resident. The amounts in the Oregon "
                              "column (b) are the Oregon source portion of the item allocated or apportioned "
                              "to Oregon."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": "TWO COMPLETELY DIFFERENT FILL PATTERNS on one schedule, selected by the residency radio."},
        ],
    },
    {
        "source_code": "OR_2025_SCH_OR_AP",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": "2025 Schedule OR-AP, Apportionment of Income for Corporations and Partnerships, 150-102-171 (+ Instructions -171-1)",
        "citation": "Or. Schedule OR-AP (2025), 150-102-171 Rev. 07-10-25 ver. 01 (4 pp.); Instructions 150-102-171-1 Rev. 10-14-25",
        "issuer": "Oregon Department of Revenue",
        "official_url": "https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-ap_102-171_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.4,
        "topics": ["or_apportionment"],
        "notes": ("ONE schedule serves FIVE parent forms including both Oregon PTE returns - and is NOT "
                  "used with Form OR-21, which has its own OR-21-AP with a different line structure. DO "
                  "NOT REUSE ONE APPORTIONMENT MODEL ACROSS THEM."),
        "excerpts": [
            {"excerpt_label": "The part-2 PTE caveat - PERMISSIVE, not mandatory, verbatim",
             "location_reference": "150-102-171-1 p. 2",
             "excerpt_text": ("Note: This part of the schedule is used for computation of entity level Oregon "
                              "taxable income for Form OR-20, OR-20-INC, OR-20-INS, and OR-20-S filers. Most "
                              "pass-through entities (PTEs) don't complete Schedule OR-AP, part 2. However, "
                              "they may use it to determine the Oregon-source distributive income for their "
                              "owners."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("D-12 W3. The 'must be run twice' mandate is DISPROVEN. ONE FILED INSTANCE plus "
                              "a SEPARATE OFF-SCHEDULE owner-source computation - printing two part 2s would "
                              "put an UNFILED computation on the return.")},
        ],
    },
    {
        "source_code": "OR_2025_PUB_OR21_EST",
        "source_type": "state_instruction", "source_rank": "implementation_official", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": "Publication OR-21-EST, Oregon PTE-E Tax Estimated Payment Instructions, 150-107-115",
        "citation": "Or. Publication OR-21-EST, 150-107-115 ⚠ Rev. 10-16-24 (PDF ModDate 2026-02-09, 3 pp.)",
        "issuer": "Oregon Department of Revenue",
        "official_url": "https://www.oregon.gov/dor/forms/FormsPubs/pub%20or-21-est-107-115_2025.pdf",
        "current_status": "active", "trust_score": 7.5, "topics": ["or_pte_e_elective_tax"],
        "notes": ("⚠ THE WEAKEST LINK IN THE PTE-E CHAIN (U6). Rev. 10-16-24 - EIGHTEEN MONTHS older than "
                  "the Form OR-21 instructions and PRE-OBBBA, PRE-SB-1510. Observed divergence: the $1,000 "
                  "test sits at worksheet LINE 2 here and at worksheet LINE 1 in the Form OR-21 "
                  "instructions. SAME SUBSTANCE, DIFFERENT NUMBERING. PREFER THE FORM OR-21 INSTRUCTIONS "
                  "(Rev. 04-01-26) ON EVERY POINT OF CONFLICT. ⚠ Filename contains SPACES - another "
                  "pattern-guessing trap."),
    },
    {
        "source_code": "OR_DOR_PTE_E_PROGRAM_PAGE",
        "source_type": "state_efile_spec", "source_rank": "implementation_official", "jurisdiction_code": "OR",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": "Oregon DOR Pass-through Entity Elective Tax program page - the e-file requirement and the PAPER CONTRADICTION",
        "citation": "oregon.gov/dor/programs/businesses/pages/pass-through-entity-elective-tax.aspx (re-fetched 2026-08-19, HTTP 200)",
        "issuer": "Oregon Department of Revenue",
        "official_url": "https://www.oregon.gov/dor/programs/businesses/pages/pass-through-entity-elective-tax.aspx",
        "current_status": "active", "trust_score": 8.5, "topics": ["or_pte_e_elective_tax"],
        "notes": ("LARGELY RESOLVES U19: an approved software vendor MAY file the RETURN, so the 'PTE-E "
                  "vendor category is payments only' reading is REFUTED and the corporate e-file page's "
                  "five-program list is INCOMPLETE, not prohibitive. ⚠ STILL OPEN: the MeF SUBMISSION TYPE "
                  "and SCHEMA FAMILY for OR-21, obtainable ONLY from the LOI-gated Oregon MeF Handbook. "
                  "ONE EMAIL ANSWERS IT; NO PUBLIC PAGE WILL. ⚠ AND IT CREATES U23 - it contradicts the "
                  "FINAL instruction booklet on whether a paper Form OR-21 exists at all."),
        "excerpts": [
            {"excerpt_label": "The paper contradiction - OR-DEF-6 / U23, verbatim",
             "excerpt_text": ("Returns can only be filed electronically either through Revenue Online or an "
                              "approved software vendor. Your software vendor must be approved by the "
                              "department for electronic filing... If your software vendor does not support "
                              "Form OR-21, you will have to file through Revenue Online. Paper returns will "
                              "not be accepted. ... The OR-21 will be required to be electronically filed or "
                              "filed through our Revenue Online portal. We will not be releasing the OR-21 "
                              "in paper form."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ The FINAL instruction booklet says the opposite ('File Form OR-21 by mail "
                              "only if you requested a paper return'). THE 'FACE BEATS INSTRUCTIONS' RULE "
                              "CANNOT RESOLVE IT, BECAUSE FORM OR-21 HAS NO FACE. Working position: treat "
                              "paper OR-21 as UNAVAILABLE.")},
        ],
    },
    {
        "source_code": "OR_PORTLAND_LIC_2_05",
        "source_type": "state_regulation", "source_rank": "primary_official", "jurisdiction_code": "OR",
        "tax_year_start": 2025,
        "title": ("City of Portland policy LIC-2.05, Requirement to File Returns Electronically (adopted "
                  "2024-04-16) - TWO PRONGS, and only the SECOND reaches a PTE return"),
        "citation": "Portland LIC-2.05; federal predicate 26 CFR 301.6011-3(a) and 301.6037-2(a)",
        "issuer": "City of Portland Revenue Division",
        "official_url": "https://www.portland.gov/policies/licensing-and-income-taxes/administration/lic-205-requirement-file-returns-electronically",
        "current_status": "active", "trust_score": 8.8, "topics": ["or_local_portland_metro"],
        "notes": ("⚠ CORRECTED ON VERIFICATION. Prong 1 ('All paid tax preparers filing PERSONAL INCOME TAX "
                  "RETURNS...') reaches ONLY the SP / MC-40 / MC-40-NP / MET-40 / MET-40-NP family, so it "
                  "does NOT reach Form P, SC, METBIT-65 or METBIT-20S. Those four are bound by the BUSINESS "
                  "prong, whose trigger is the TAXPAYER's own federal e-file duty. LIC-2.05 has NO numeric "
                  "threshold of its own. ⚠ 26 CFR 301.6011-5 is the Form 1120 rule and does NOT reach "
                  "1120-S. Because the 10-return count aggregates W-2s and 1099s, nearly every real PTE "
                  "client is caught - THE FORCE OF THE SCOPE CALL IS UNCHANGED, only its mechanism."),
    },
    {
        "source_code": "OR_IRS_2025_1065_1120S",
        "source_type": "official_form", "source_rank": "primary_official", "jurisdiction_code": "FED",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": "FINAL 2025 IRS Form 1065 and Form 1120-S (+ Schedule D (1120-S)) - the federal handoff for all three Oregon specs",
        "citation": "IRS Form 1065 (2025) ModDate 2026-01-08; Form 1120-S (2025) ModDate 2026-01-08; Schedule D (Form 1120-S) ModDate 2025-12-30",
        "issuer": "Internal Revenue Service",
        "official_url": "https://www.irs.gov/pub/irs-pdf/f1120s.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.9,
        "topics": ["or_pte_e_elective_tax", "or_pte_entity_returns"],
        "notes": ("✅ ALL VERIFIED. Two independent workstreams re-derived every Form OR-21 Schedule K "
                  "mapping against freshly downloaded 2025 forms: 0 ERRORS across 20 references. ✅ The "
                  "IRS's own cross-reference settles the Oregon Question J defect without line-counting: "
                  "2025 Schedule K line 1 reads '(page 1, line 22)' on the 1120-S and '(page 1, line 23)' "
                  "on the 1065. ⚠ Schedule D (1120-S) Part III LINE 18 is 'Net recognized built-in gain' - "
                  "the INCOME BASE; line 23 is the federal 21% TAX. A build that grabs line 23 imports the "
                  "federal tax as if it were Oregon income."),
    },
]

# ⚠ AUTHORITY -> FORM links. `form_code` is CharField(50); the three Oregon codes
# fit easily.
AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    ("OR_2025_FORM_OR65", FORM_CODE_OR65, "governs"),
    ("OR_2025_FORM_OR65_INSTR", FORM_CODE_OR65, "governs"),
    ("OR_ORS_314_724_725_PTNSHP", FORM_CODE_OR65, "governs"),
    ("OR_2025_PUB_OR_CODES", FORM_CODE_OR65, "governs"),
    ("OR_2025_SCH_OR_K1", FORM_CODE_OR65, "informs"),
    ("OR_2025_SCH_OR_AP", FORM_CODE_OR65, "informs"),
    ("OR_ORS_314_385_DUE", FORM_CODE_OR65, "governs"),
    ("OR_ORS_314_011_CONFORMITY", FORM_CODE_OR65, "governs"),
    ("OR_SB1507_2026_CH142", FORM_CODE_OR65, "informs"),
    ("OR_ORS_317_010_CONFORMITY", FORM_CODE_OR20S, "governs"),
    ("OR_2025_FORM_OR20S", FORM_CODE_OR20S, "governs"),
    ("OR_2025_FORM_OR20S_INSTR", FORM_CODE_OR20S, "governs"),
    ("OR_ORS_317_061_090_RATES", FORM_CODE_OR20S, "governs"),
    ("OR_ORS_318_020_031_INCOME", FORM_CODE_OR20S, "governs"),
    ("OR_ORS_314_762_772_SCORP", FORM_CODE_OR20S, "governs"),
    ("OR_2025_SCH_ASC_CORP", FORM_CODE_OR20S, "governs"),
    ("OR_2025_SCH_OR_AP", FORM_CODE_OR20S, "governs"),
    ("OR_2025_SCH_OR_K1", FORM_CODE_OR20S, "informs"),
    ("OR_IRS_2025_1065_1120S", FORM_CODE_OR20S, "mapping_only"),
    ("OR_SB1507_2026_CH142", FORM_CODE_OR20S, "informs"),
    ("OR_2021_CH589_PTE_E", FORM_CODE_OR21, "governs"),
    ("OR_2025_FORM_OR21_INSTR", FORM_CODE_OR21, "governs"),
    ("OR_2025_SCH_OR21_MD_INSTR", FORM_CODE_OR21, "governs"),
    ("OR_2025_SCH_OR21_AP_INSTR", FORM_CODE_OR21, "governs"),
    ("OR_2025_SCH_OR21_MDPT_INSTR", FORM_CODE_OR21, "governs"),
    ("OR_2025_SCH_OR21_K1", FORM_CODE_OR21, "governs"),
    ("OR_2025_PUB_OR21_EST", FORM_CODE_OR21, "informs"),
    ("OR_2025_PUB_OR_CODES", FORM_CODE_OR21, "informs"),
    ("OR_IRS_2025_1065_1120S", FORM_CODE_OR21, "mapping_only"),
    ("OR_DOR_PTE_E_PROGRAM_PAGE", FORM_CODE_OR21, "informs"),
    ("OR_ORS_314_385_DUE", FORM_CODE_OR21, "governs"),
    ("OR_PORTLAND_LIC_2_05", FORM_CODE_OR65, "informs"),
    ("OR_PORTLAND_LIC_2_05", FORM_CODE_OR20S, "informs"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM OR_65 -- FACTS
# ═══════════════════════════════════════════════════════════════════════════
OR65_FACTS: list[dict] = [
    {"fact_key": "or65_amended_return", "label": "Amended return", "data_type": "boolean",
     "sort_order": 1, "notes": "Header checkbox. Oregon has NO separate amended partnership form."},
    {"fact_key": "or65_short_year_return", "label": "Short-year return", "data_type": "boolean",
     "sort_order": 2,
     "notes": ("⚠ NOT the proration switch. This box and checkbox (e) `Accounting period change` are "
               "two DIFFERENT boxes on the same page; keying off the wrong one mis-states the "
               "minimum tax on every short-year return, IN BOTH DIRECTIONS.")},
    {"fact_key": "or65_entity_type", "label": "Type of entity", "data_type": "choice",
     "choices": ["Partnership", "Limited partnership", "Limited liability company",
                 "Limited liability partnership"],
     "required": True, "sort_order": 3,
     "notes": ("Four boxes. ⚠ NO abbreviation-code scheme and NO S-corp option - Oregon does not put "
               "S corporations on Form OR-65 at all.")},
    {"fact_key": "or65_box_a_final_return", "label": "(a) Final return", "data_type": "boolean", "sort_order": 4,
     "notes": ("⚠ Triggers a HARD ATTACHMENT REQUIREMENT with NO FORM AND NO TEMPLATE: 'a schedule "
               "showing to whom all assets and liabilities were distributed, and each asset's "
               "adjusted basis, fair market value, and sales price.'")},
    {"fact_key": "or65_box_b_initial_return", "label": "(b) Initial return", "data_type": "boolean", "sort_order": 5},
    {"fact_key": "or65_box_c_amended_fed_audit", "label": "(c) Amended due to federal audit or adjustments",
     "data_type": "boolean", "sort_order": 6},
    {"fact_key": "or65_box_d_name_change", "label": "(d) Name change", "data_type": "boolean", "sort_order": 7,
     "notes": "⚠ Carries an instruction obligation with NO FIELD ON THE FACE - the prior name goes in an attachment."},
    {"fact_key": "or65_box_e_accounting_period_change", "label": "(e) Accounting period change",
     "data_type": "boolean", "sort_order": 8,
     "notes": "⚠⚠ THIS is the proration switch for the 12-row published table, not the `Short-year return` box."},
    {"fact_key": "or65_box_f_extension_filed", "label": "(f) Extension filed", "data_type": "boolean", "sort_order": 9,
     "notes": ("⚠ The ONLY extension mechanism on Form OR-65, and it is SELF-DECLARING - no request is "
               "filed with anyone. The preparer types the extended due date onto the face.")},
    {"fact_key": "or65_extension_due_date", "label": "(f) Extension due date", "data_type": "date", "sort_order": 10},
    {"fact_key": "or65_box_g_form_or24", "label": "(g) Form OR-24", "data_type": "boolean", "sort_order": 11},
    {"fact_key": "or65_box_h_8886_reit_ric", "label": "(h) You have federal Form 8886, a REIT, or a RIC",
     "data_type": "boolean", "sort_order": 12,
     "notes": ("⚠ A THREE-IN-ONE box. Form OR-20-S splits the same concepts into TWO separate "
               "checkboxes (`REIT/RIC` and `Federal Form 8886`). DO NOT SHARE ONE FIELD DEFINITION "
               "ACROSS THE TWO OREGON FORMS.")},
    {"fact_key": "or65_q1a_doing_business", "label": "1A. Did the partnership do business in Oregon during the year?",
     "data_type": "boolean", "required": True, "sort_order": 20,
     "notes": "⚠ THE TAX GATE, half of it. 'Doing business' is defined the same for partnerships and corporations."},
    {"fact_key": "or65_q2a_oregon_source_income",
     "label": "2A. Does the partnership have income or loss derived from sources in Oregon?",
     "data_type": "boolean", "required": True, "sort_order": 21},
    {"fact_key": "or65_q2b_oregon_resident_partners",
     "label": "2B. Does the partnership have Oregon resident partners?",
     "data_type": "boolean", "required": True, "sort_order": 22,
     "notes": ("⚠ The face prints `2B` without a trailing period - a typographic inconsistency with "
               "1A/2A, noted only so a transcription diff does not read as an error.")},
    {"fact_key": "or65_l3b_prepayments", "label": "3B. Payments - prepayments already made",
     "data_type": "decimal", "sort_order": 30,
     "notes": "⚠ Extension and voluntary prepayments ONLY. Estimated payments are NOT REQUIRED for Form OR-65."},
    {"fact_key": "or65_months_in_short_period", "label": "Months in the short period (accounting period change only)",
     "data_type": "integer", "sort_order": 31, "validation_rule": "1-12 when checkbox (e) is set"},
    {"fact_key": "or65_q4a_pl_percentages_changed",
     "label": "4A. Did the partners' profit/loss sharing percentages change during the year?",
     "data_type": "boolean", "sort_order": 40},
    {"fact_key": "or65_q4b_mods_by_profit_pct",
     "label": "4B. Were the Oregon modifications divided according to each partner's profit sharing percentage?",
     "data_type": "boolean", "sort_order": 41,
     "notes": ("⚠ A 'No' here means the partnership used some other allocation and the K-1 amounts "
               "will NOT reconcile to `Schedule I total x profit %`. ANY TIE-OUT DIAGNOSTIC MUST "
               "RESPECT 4B.")},
    {"fact_key": "or65_q4c_corporate_partners", "label": "4C. Does the partnership have corporate partners?",
     "data_type": "boolean", "sort_order": 42,
     "notes": ("No computational consequence on Form OR-65 itself, but it is the flag that tells the "
               "preparer the withholding analysis has a 6.6%/7.6% CORPORATE rate branch rather than "
               "the 9.9% individual rate.")},
    {"fact_key": "or65_l4d_total_k1s", "label": "4D. Number of federal Schedules K-1 issued - Total",
     "data_type": "integer", "sort_order": 43,
     "notes": ("⚠ THREE separate numeric boxes ALL PRINT THE LABEL '4D' (Total / Oregon residents / "
               "Nonresidents); the grouping is POSITIONAL ONLY. ⚠ It counts FEDERAL Schedules K-1 "
               "ISSUED - NOT Oregon Schedules OR-K-1, and NOT the partner count from Form 1065 page 1 "
               "line I.")},
    {"fact_key": "or65_l4d_resident_k1s", "label": "4D. Number issued - Oregon residents",
     "data_type": "integer", "sort_order": 44},
    {"fact_key": "or65_l4d_nonresident_k1s", "label": "4D. Number issued - Nonresidents",
     "data_type": "integer", "sort_order": 45},
    {"fact_key": "or65_l4e_composite_partners",
     "label": "4E. Number of nonresident partners included on a Form OR-OC", "data_type": "integer",
     "sort_order": 46,
     "notes": ("⚠ A FORWARD-LOOKING count - 'filed or will be filing'. It can be non-zero BEFORE Form "
               "OR-OC exists, so Form OR-65 can be completed before the composite return is prepared. "
               "Sequencing matters for the app.")},
    {"fact_key": "or65_q5a_prior_return_filed", "label": "5A. Was a 2024 Oregon partnership return filed?",
     "data_type": "boolean", "sort_order": 50},
    {"fact_key": "or65_q5c_federal_audit_change",
     "label": "5C. Did a federal audit or adjustment change a prior year or the current year tax return?",
     "data_type": "boolean", "sort_order": 51, "notes": "The CPAR gate."},
    {"fact_key": "or65_q5d_6221b_optout", "label": "5D. IRC Section 6221(b) opt-out election for tax year 2025",
     "data_type": "boolean", "sort_order": 52,
     "notes": ("A 'No' drives a conditional PR contact sub-block. ⚠ TWO CONTACT-PHONE FIELDS WITH "
               "IDENTICAL LABELS - one for the individual PR, one for the entity PR. Model as "
               "5D_pr_individual_phone and 5D_pr_entity_phone.")},
    {"fact_key": "or65_pr_individual_phone", "label": "5D. Federal partnership representative - individual contact phone",
     "data_type": "string", "sort_order": 53},
    {"fact_key": "or65_pr_entity_phone", "label": "5D. Federal partnership representative - entity contact phone",
     "data_type": "string", "sort_order": 54},
    {"fact_key": "or65_q6a_multistate",
     "label": "6A. Did the partnership have business activity both inside and outside of Oregon?",
     "data_type": "boolean", "sort_order": 60,
     "notes": ("⚠ THIS IS THE ENTIRE APPORTIONMENT INTERFACE ON FORM OR-65: one Yes/No and an "
               "attachment obligation. THE APPORTIONMENT PERCENTAGE ITSELF IS NEVER PRINTED ANYWHERE "
               "ON FORM OR-65 - it exists only on Schedule OR-AP part 1 line 23 and is carried to "
               "each Schedule OR-K-1 Part III header.")},
    {"fact_key": "or65_q7a_trimet_employees", "label": "7A. Employees performing services in the TriMet Transit District",
     "data_type": "boolean", "sort_order": 70,
     "notes": "⚠ NO RETURN CONSEQUENCE for the partnership - employer transit payroll tax is a payroll-side obligation. A diagnostic that fires on 7A is WRONG."},
    {"fact_key": "or65_q7b_trimet_se_income", "label": "7B. Partners with self-employment income in the TriMet Transit District",
     "data_type": "boolean", "sort_order": 71, "notes": "⚠ THIS one produces a return (Form OR-TM)."},
    {"fact_key": "or65_q7c_ltd_employees", "label": "7C. Employees performing services in the Lane Transit District",
     "data_type": "boolean", "sort_order": 72, "notes": "⚠ NO RETURN CONSEQUENCE. See 7A."},
    {"fact_key": "or65_q7d_ltd_se_income", "label": "7D. Partners with self-employment income in the Lane Transit District",
     "data_type": "boolean", "sort_order": 73, "notes": "⚠ THIS one produces a return (Form OR-LTD)."},
    {"fact_key": "or65_transit_entity_files_for_partners",
     "label": "Partnership elects to file Form OR-TM / OR-LTD on the partners' behalf",
     "data_type": "boolean", "sort_order": 74,
     "notes": "An ENTITY-vs-OWNER filing branch the app must model. RED-DEFER for v1, but the flag must exist so the diagnostic can fire."},
    {"fact_key": "or65_schedule_i_additions", "label": "Schedule I additions (name / code / amount rows 8-11)",
     "data_type": "string", "sort_order": 80,
     "notes": ("⚠ EACH ROW IS bare N (NAME) + Na (CODE) + Nb (AMOUNT). FOUR ROWS PER SECTION on the "
               "printed face; overflow to an attached schedule. ⚠⚠ CODES COME FROM THE INDIVIDUAL "
               "NAMESPACE (Publication OR-CODES) ONLY - see R-OR65-SCHED-I-NS.")},
    {"fact_key": "or65_schedule_i_subtractions", "label": "Schedule I subtractions (rows 12-15)",
     "data_type": "string", "sort_order": 81},
    {"fact_key": "or65_schedule_i_credits", "label": "Schedule I credits (rows 16-19)",
     "data_type": "string", "sort_order": 82},
    {"fact_key": "or65_partners_at_any_time", "label": "Persons who were partners during any part of the taxable year",
     "data_type": "integer", "sort_order": 90,
     "notes": ("The ORS 314.724(3) penalty measure. ⚠ A HIGHER count than year-end partners and higher "
               "than the line 4D K-1 count in a year with mid-year departures. Never posted to the "
               "return - Form OR-65 has no penalty line.")},
]

OR65_RULES: list[dict] = [
    {"rule_id": "R-OR65-FILE-GATE", "title": "FILING gate: file if 2A OR 2B", "rule_type": "conditional",
     "sort_order": 1, "inputs": ["or65_q2a_oregon_source_income", "or65_q2b_oregon_resident_partners"],
     "outputs": ["filing_required"],
     "formula": "filing_required = q2a OR q2b",
     "description": ("ORS 314.724(1) and Instr. p. 2, verbatim: 'The partnership is required to file if "
                     "it had income or (loss) apportioned or allocated to Oregon or if it had Oregon "
                     "resident partners. If you answered \"Yes\" to 2A or 2B (or both), you must file "
                     "Form OR-65. If you didn't answer \"Yes\" to either 2A or 2B, then the partnership "
                     "isn't required to file a return or pay the minimum tax.'"),
     "exceptions": ("Publicly traded partnerships taxed as corporations (ORS 314.722), and partnerships "
                    "not required to file a federal partnership return - the DOR's own example is a "
                    "married couple electing the qualified joint venture option.")},
    {"rule_id": "R-OR65-TAX-GATE", "title": "TAX gate: $150 only if 1A AND (2A OR 2B) - a DIFFERENT boolean",
     "rule_type": "calculation", "sort_order": 2,
     "inputs": ["or65_q1a_doing_business", "or65_q2a_oregon_source_income", "or65_q2b_oregon_resident_partners"],
     "outputs": ["OR65_L3A"],
     "formula": "L3A = 150 if (q1a AND (q2a OR q2b)) else 0",
     "description": ("⚠⚠ THE FILING GATE AND THE TAX GATE ARE DIFFERENT BOOLEANS AND BOTH LIVE ON PAGE 1. "
                     "A partnership with Oregon RESIDENT PARTNERS but NO Oregon business activity FILES "
                     "AND OWES NOTHING. A build that collapses the two gates BILLS $150 TO EVERY "
                     "OUT-OF-STATE PARTNERSHIP THAT HAPPENS TO HAVE ONE OREGON PARTNER. Corroborated: "
                     "'If the partnership is registered to do business in Oregon, but didn't have any "
                     "business activity, it's not subject to the minimum tax.'"),
     "notes": "Statutory basis ORS 314.725 - the whole of Oregon's partnership entity-level tax."},
    {"rule_id": "R-OR65-PRORATION", "title": "Short-period proration: a PUBLISHED 12-ROW TABLE, never a formula",
     "rule_type": "calculation", "sort_order": 3,
     "inputs": ["or65_box_e_accounting_period_change", "or65_months_in_short_period"],
     "outputs": ["OR65_L3A"],
     "formula": "L3A = OR65_PRORATION_TABLE[months] when checkbox (e) is set; otherwise 150",
     "description": ("The DOR publishes twelve ROUNDED values: 1=$13, 2=$25, 3=$38, 4=$50, 5=$63, 6=$75, "
                     "7=$88, 8=$100, 9=$113, 10=$125, 11=$138, 12=$150. EVERY HALF-DOLLAR ROUNDS UP. A "
                     "round() implementation using banker's ROUND-HALF-TO-EVEN diverges on THREE rows - "
                     "months 1, 5 and 9, giving $12/$62/$112 instead of $13/$63/$113. ⚠ THE SOURCE BRIEF "
                     "SAYS 'wrong on five of the twelve rows ... $12/$62/$112/$138' AND ITS ARITHMETIC IS "
                     "WRONG TWICE: round-half-to-even gives 37.5->38, 87.5->88 and 137.5->138, all of "
                     "which MATCH the chart, so $138 is not a divergence and the count is THREE, not "
                     "five. The substantive point is unaffected - SEED THE LITERAL TABLE. ⚠ THE SWITCH IS "
                     "CHECKBOX (e) `Accounting period change`, NOT the `Short-year return` box."),
     "exceptions": ("'This chart doesn't apply to other short tax year returns, such as initial returns "
                    "or final returns. The tax is $150 in those cases.' ⚠ AND FORM OR-20-S STATES THE "
                    "SAME RULE AS A BARE FORMULA ($150 x months / 12) - two different authorities. "
                    "D-12 W6: seed both as authored; DO NOT SHARE ONE PRORATION ROUTINE.")},
    {"rule_id": "R-OR65-L3CD", "title": "Lines 3C and 3D - mutually exclusive by construction",
     "rule_type": "calculation", "sort_order": 4,
     "inputs": ["OR65_L3A", "or65_l3b_prepayments"], "outputs": ["OR65_L3C", "OR65_L3D"],
     "formula": "L3C = max(0, L3A - L3B); L3D = max(0, L3B - L3A)",
     "description": "'If the tax liability and the payments already submitted are the same, enter $0.'"},
    {"rule_id": "R-OR65-SCHED-I-NS", "title": "Schedule I draws from the INDIVIDUAL namespace ONLY",
     "rule_type": "validation", "sort_order": 5,
     "inputs": ["or65_schedule_i_additions", "or65_schedule_i_subtractions", "or65_schedule_i_credits"],
     "outputs": ["namespace_violation"],
     "formula": "or_assert_namespace('OR65_SCHEDULE_I', NS_INDIVIDUAL)",
     "description": ("Instr. p. 2, verbatim: 'Modification and credit codes can be found in Publication "
                     "OR-CODES and Publication OR-17.' Form OR-65 therefore uses the INDIVIDUAL set, "
                     "while Form OR-20-S uses the CORPORATE one. TWELVE NUMBERS COLLIDE (118, 132, 150, "
                     "151, 158, 159, 352, 356, 358, 361 semantically; 338 and 344 by label). Code 158 "
                     "alone means 'gain or loss on disposition of depreciable property' on the corporate "
                     "schedule and 'interest and dividends on government bonds of other states' here."),
     "notes": ("C1 / D-12. HARD failure, not a warning: a mix-up posts a depreciation-basis difference "
               "onto a municipal-interest line AND THE RETURN STILL FOOTS.")},
    {"rule_id": "R-OR65-NO-FOOT", "title": "VERIFIED NEGATIVE: Schedule I does NOT foot and does NOT flow",
     "rule_type": "validation", "sort_order": 6, "inputs": [], "outputs": [],
     "formula": "no total line on any Schedule I section; no flow to line 3 or to any other OR-65 line",
     "description": ("⚠ ENCODE THE ABSENCE. There is NO total line on any of the three Schedule I "
                     "sections and NOTHING from Schedule I flows to line 3 or to any other line on Form "
                     "OR-65. It is PURE PASS-THROUGH REPORTING. A build that tries to tie Schedule I to "
                     "the tax computation has misread the form."),
     "notes": "N2. Pinned in validate_or.py so a later contributor cannot add a total 'for symmetry'."},
    {"rule_id": "R-OR65-PENALTY", "title": "PENALTY POSTURE: OR-65 does NOT self-assess (the OPPOSITE of OR-20-S)",
     "rule_type": "validation", "sort_order": 7,
     "inputs": ["or65_partners_at_any_time"], "outputs": ["penalty_exposure_estimate"],
     "formula": "exposure = 50 x partners_at_any_time x min(months_late, 5)  -- ESTIMATE ONLY, never a line",
     "description": ("Instr. p. 1, verbatim: 'Don't submit a penalty payment with the return. Penalty "
                     "payments are only required if the department assesses a penalty.' THE OR-65 FACE "
                     "HAS NO PENALTY OR INTEREST LINE AT ALL - its tax block is 3A-3D. Statutory measure "
                     "ORS 314.724(3): $50 per month per partner, capped at five months, counting persons "
                     "who were partners DURING ANY PART OF the taxable year."),
     "exceptions": ("Form OR-20-S self-assesses penalty AND interest on its face at lines 22-24, and "
                    "Form OR-21 has a THIRD, narrower set (5% + interest only). D-12 W6: THREE SEPARATE "
                    "PENALTY MODELS. A shared 'Oregon penalty engine' that writes computed penalties "
                    "onto both entity returns produces an INCORRECT OR-65.")},
    {"rule_id": "R-OR65-NO-EST", "title": "VERIFIED NEGATIVE: no estimated payments, no OR-37, no Schedule ES",
     "rule_type": "validation", "sort_order": 8, "inputs": [], "outputs": [],
     "formula": "estimated_payments_required = False",
     "description": ("Instr. p. 1: 'Estimated payments are not required.' Line 3B exists ONLY for "
                     "extension payments and voluntary prepayments. There is NO OR-65 analogue to Form "
                     "OR-37, no underpayment interest and no Schedule ES. Corroborated on the voucher: "
                     "Form OR-65-V carries only TWO payment types and has NO `Estimated payment` box, "
                     "where Form OR-20-V and Form OR-21-V each carry THREE."),
     "notes": "N5."},
    {"rule_id": "R-OR65-K1-DELIV", "title": "K-1 delivery: >= 11 partners => a summary",
     "rule_type": "routing", "sort_order": 9, "inputs": ["or65_l4d_total_k1s"], "outputs": ["k1_delivery_mode"],
     "formula": "summary if partner_count >= 11 else attach federal K-1s",
     "description": ("'Federal Schedules K-1, if there were fewer than 11 partners during the year. If "
                     "the partnership had more than 10 partners, include a summary of partner "
                     "information.' The threshold is stated TWICE in one bullet and is consistent. ⚠ The "
                     "parallel OR-20-S rule is written with ONLY the second half ('If you had more than "
                     "10 shareholders...') - SAME THRESHOLD, different phrasing. A SHARED COMPONENT MUST "
                     "NOT INFER A DIFFERENT RULE FROM THE MISSING CLAUSE.")},
    {"rule_id": "R-OR65-APPORT", "title": "The apportionment percentage has NO HOME on the Form OR-65 face",
     "rule_type": "routing", "sort_order": 10, "inputs": ["or65_q6a_multistate"], "outputs": ["or_ap_required"],
     "formula": "attach Schedule OR-AP when 6A is Yes; the percentage lives on OR-AP part 1 line 23",
     "description": ("⚠ Line 6A is the ENTIRE apportionment interface on Form OR-65: one Yes/No and an "
                     "attachment obligation. Any Delvio model expecting a `state_apportionment_pct` field "
                     "on the partnership return face WILL FIND NO HOME FOR IT, and any diagnostic that "
                     "validates 'apportionment % present when multistate' has to reach into the attached "
                     "schedule. The number lands on each Schedule OR-K-1 Part III header."),
     "notes": "N6."},
    {"rule_id": "R-OR65-GP-ORDER", "title": "Guaranteed payments: APPORTION-THEN-ATTRIBUTE (OAR 150-316-0155)",
     "rule_type": "calculation", "sort_order": 11, "inputs": [], "outputs": ["nonresident_oregon_source_share"],
     "formula": "apportion the ENTIRE distributive share INCLUDING guaranteed payments under ORS 314.605-314.675, THEN attribute irrespective of profit percentage",
     "description": ("✅ U9 CLOSED. OAR 150-316-0155 (REV 29-2017, valid for TY2025) states the ordering "
                     "explicitly. ⚠ THE DOR'S OWN PARAPHRASE - 'attributed DIRECTLY to the owner "
                     "receiving the payment', in the OR-19 instructions and Pub. OR-OC - IS LOOSER THAN "
                     "THE RULE and, read alone, invites a spec author to SKIP APPORTIONMENT ENTIRELY. "
                     "BUILD TO THE RULE TEXT."),
     "notes": "A stated Oregon rule with NO LINE anywhere on any form."},
    {"rule_id": "R-OR65-DUEDATE", "title": "Due March 16, 2026; extended September 15, 2026, SELF-DECLARED",
     "rule_type": "calculation", "sort_order": 12, "inputs": ["or65_box_f_extension_filed"], "outputs": ["due_date"],
     "formula": "due = the federal partnership due date (ORS 314.724(1)); extended = +6 months, automatic",
     "description": ("March 15, 2026 is a Sunday, so the TY2025 date is MARCH 16, 2026 - CONFIRMED "
                     "VERBATIM in the instructions. 'No request needs to be filed for an Oregon "
                     "extension.' ⚠ An extension to file is NOT more time to pay."),
     "notes": ("⚠ Form OR-65 is due ONE MONTH EARLIER than Form OR-20-S, because ORS 314.385(1)(b) shifts "
               "the CORPORATE date by a month and ORS 314.724(1) does not shift the partnership date at "
               "all. Five distinct due dates exist in the Oregon PTE space.")},
    {"rule_id": "R-OR65-CPAR", "title": "CPAR: the adjustments report is due REGARDLESS of the election",
     "rule_type": "routing", "sort_order": 13, "inputs": ["or65_q5c_federal_audit_change", "or65_q5d_6221b_optout"],
     "outputs": ["cpar_path"],
     "formula": "always -> Form OR-OC + Schedule OR-OC-3/-4; PLUS an amended OR-65 if the Oregon CPAR election is NOT made",
     "description": ("Three mutually exclusive routes, but the reporting obligation is unconditional: "
                     "'Partnerships with CPAR adjustments affecting Oregon tax must notify us by "
                     "submitting a completed adjustments report, REGARDLESS of whether the Oregon CPAR "
                     "election is made.' The election itself is made on Form OR-OC, NOT on Form OR-65. "
                     "The unelected path also requires an 'as if' federal Form 1065 per adjusted year, "
                     "marked 'as if' at the top. Owner-side codes: addition 187 / subtraction 384 - "
                     "identical in BOTH namespaces."),
     "notes": ("⚠ 'Don't use Form OR-65 to designate an Oregon partnership representative.' The face "
               "captures the FEDERAL PR only; an Oregon-only PR is designated by letter, fax or Revenue "
               "Online. THERE IS NO FORM AND NO FIELD, AND THE APP MUST NOT OFFER ONE (N9).")},
    {"rule_id": "R-OR65-TRANSIT", "title": "Transit self-employment: only 7B/7D produce a return",
     "rule_type": "routing", "sort_order": 14,
     "inputs": ["or65_q7a_trimet_employees", "or65_q7b_trimet_se_income",
                "or65_q7c_ltd_employees", "or65_q7d_ltd_se_income"],
     "outputs": ["or_tm_required", "or_ltd_required"],
     "formula": "OR-TM if 7B; OR-LTD if 7D. 7A and 7C produce NOTHING.",
     "description": ("⚠ NOTE THE ASYMMETRY. 7A and 7C (EMPLOYEES) have no return consequence for the "
                     "partnership - employer transit payroll tax is a payroll-side obligation, not a "
                     "Delvio artifact. ONLY 7B and 7D (PARTNERS' self-employment) produce a return. A "
                     "DIAGNOSTIC THAT FIRES ON 7A/7C WILL BE WRONG. TY2025 rates: TriMet 0.008237, Lane "
                     "0.0080, both with a $400 net-self-employment-earnings threshold; district "
                     "membership is by a ZIP-code list published in each instruction booklet."),
     "notes": "RED-DEFER for v1, but the four checkboxes MUST still be captured or the deferral diagnostic can never fire."},
    {"rule_id": "R-OR65-CONFORM", "title": "Oregon's HYBRID conformity - TY2025-keyed, and SB 1507 moves it",
     "rule_type": "classification", "sort_order": 15, "inputs": [], "outputs": ["irc_vintage"],
     "formula": "rolling for the definition of taxable income; fixed 12/31/2023 (TY2025) for the ORS 314.011(2)(c) enumeration",
     "description": ("⚠ DO NOT FLATTEN and DO NOT ENCODE THE DOR ONE-LINER. The OR-20-S booklet's 'Oregon "
                     "is tied to the federal definition of taxable income as of December 31, 2023' is "
                     "STATED BACKWARDS - the statute makes the taxable-income definition the ROLLING "
                     "prong. ⚠⚠ SB 1507 = 2026 Or. Laws ch. 142 sec. 35 moves the fixed date to "
                     "12/31/2025 for TY2026 and decouples Oregon from IRC 168(k) for property placed in "
                     "service in tax years beginning on or after 1/1/2026. EVERY FIGURE IN THIS SPEC IS "
                     "TY2025-ONLY."),
     "notes": "⚠ Near-miss on the record: HB 2092 (2025 R1) would have disconnected the rolling prong for exactly TY2025 and DIED in Senate Finance and Revenue."},
    {"rule_id": "R-OR65-DEPR-NEG", "title": "VERIFIED NEGATIVE: no TY2025 bonus add-back and no state 179 cap",
     "rule_type": "validation", "sort_order": 16, "inputs": [], "outputs": [],
     "formula": "no IRC 168(k) add-back, no state 179 dollar limit or phaseout, no new-asset Oregon basis for TY2025",
     "description": ("⚠ ENCODE THE ABSENCE DELIBERATELY. ORS 317.301 is the ONLY IRC 168(k)/179 "
                     "disconnect in Oregon law and its window is CLOSED - applicability note 2011 c.7 "
                     "sec. 31: 'ORS 316.739 and 317.301 apply to tax years beginning on or after January "
                     "1, 2009, and before January 1, 2011.' Its only TY2025 relevance is subsection (4), "
                     "the UNWIND of a 2009/2010 addition, which is why the DOR's 'What's new' bullet says "
                     "'may require SUBSEQUENT Oregon modifications'. Pub. OR-17 (Rev. 01-29-26) p. 91: "
                     "'As of the date this publication was last revised, Oregon had not disconnected "
                     "from any new federal depreciation expense provisions for this tax year.' The four "
                     "populated TY2025 cases are all LEGACY OR STRUCTURAL: 2009/2010 window assets still "
                     "unwinding; property transferred into Oregon; assets placed in service on or after "
                     "1/1/1985 for which a federal CREDIT Oregon does not allow was taken (ORS "
                     "317.356(1)(b)); and 1981-1985 ACRS assets where the 1996 basis alignment was not "
                     "made."),
     "notes": ("N1. ⚠ DO NOT BUILD A NULLABLE 'state depreciation adjustment' FIELD 'for symmetry with "
               "GA/TN' - a nullable field a preparer can fill is worse than no field. ⚠ BUT the per-asset "
               "DUAL BASIS must still exist in the asset model, because Schedule OR-DEPR column 1b reads "
               "'Date placed in service IN OREGON' and column 1d is a separate 'Oregon cost or other "
               "basis' - the hook for the property-transferred-into-Oregon rule. ⚠ SB 1507 makes TY2026 "
               "a full dual-basis regime; a TY2025 spec MUST NOT model it.")},
]

OR65_RULE_LINKS: list[tuple] = [
    ("R-OR65-FILE-GATE", "OR_ORS_314_724_725_PTNSHP", "primary", "ORS 314.724(1) - the statutory filing trigger"),
    ("R-OR65-FILE-GATE", "OR_2025_FORM_OR65_INSTR", "implementation", "Instr. p. 2 - 'you must file Form OR-65'"),
    ("R-OR65-TAX-GATE", "OR_2025_FORM_OR65", "primary", "line 3A as printed on the face"),
    ("R-OR65-TAX-GATE", "OR_ORS_314_724_725_PTNSHP", "primary", "ORS 314.725 - the $150 privilege tax"),
    ("R-OR65-PRORATION", "OR_2025_FORM_OR65_INSTR", "primary", "the published 12-row chart and its exclusion"),
    ("R-OR65-L3CD", "OR_2025_FORM_OR65", "primary", "lines 3C and 3D as printed"),
    ("R-OR65-SCHED-I-NS", "OR_2025_PUB_OR_CODES", "primary", "the INDIVIDUAL code universe"),
    ("R-OR65-SCHED-I-NS", "OR_2025_FORM_OR65_INSTR", "implementation", "'codes can be found in Publication OR-CODES and Publication OR-17'"),
    ("R-OR65-SCHED-I-NS", "OR_2025_SCH_ASC_CORP", "secondary", "the CORPORATE namespace this rule excludes"),
    ("R-OR65-NO-FOOT", "OR_2025_FORM_OR65", "primary", "no total line on any Schedule I section"),
    ("R-OR65-PENALTY", "OR_2025_FORM_OR65_INSTR", "primary", "'Don't submit a penalty payment with the return'"),
    ("R-OR65-PENALTY", "OR_ORS_314_724_725_PTNSHP", "primary", "ORS 314.724(3) - the statutory measure"),
    ("R-OR65-NO-EST", "OR_2025_FORM_OR65_INSTR", "primary", "'Estimated payments are not required'"),
    ("R-OR65-K1-DELIV", "OR_2025_FORM_OR65_INSTR", "primary", "the >= 11 partner summary switch"),
    ("R-OR65-APPORT", "OR_2025_SCH_OR_AP", "primary", "part 1 line 23 is where the percentage actually lives"),
    ("R-OR65-APPORT", "OR_2025_FORM_OR65", "primary", "line 6A is the entire interface"),
    ("R-OR65-GP-ORDER", "OR_OAR_150_316_0155_GP", "primary", "the ordering, explicit"),
    ("R-OR65-GP-ORDER", "OR_2025_FORM_OR65_INSTR", "implementation", "Instr. p. 1 restates the apportionment side"),
    ("R-OR65-DUEDATE", "OR_2025_FORM_OR65_INSTR", "primary", "March 16, 2026 confirmed verbatim"),
    ("R-OR65-DUEDATE", "OR_ORS_314_385_DUE", "primary", "the statutory construction"),
    ("R-OR65-CPAR", "OR_2025_FORM_OR65_INSTR", "primary", "the three routes and the unconditional report"),
    ("R-OR65-TRANSIT", "OR_2025_FORM_OR65", "primary", "lines 7A-7D as printed"),
    ("R-OR65-CONFORM", "OR_ORS_314_011_CONFORMITY", "primary", "the operative conformity statute for the whole PTE module"),
    ("R-OR65-CONFORM", "OR_SB1507_2026_CH142", "secondary", "the TY2026 staleness tripwire"),
    ("R-OR65-CONFORM", "OR_ORS_317_010_CONFORMITY", "secondary", "the corporate-excise twin, already seeded in RS"),
    ("R-OR65-DEPR-NEG", "OR_ORS_317_301_DEPR", "primary", "the ONLY 168(k)/179 disconnect - and its window is CLOSED"),
    ("R-OR65-DEPR-NEG", "OR_2025_PUB_OR17", "primary", "'Oregon had not disconnected from any new federal depreciation expense provisions'"),
]


OR65_LINES: list[dict] = [
    {"line_number": "1A", "line_type": "input", "sort_order": 1,
     "description": "Did the partnership do business in Oregon during the year?",
     "source_rules": ["R-OR65-TAX-GATE"],
     "notes": "Half of the TAX gate. A single `Yes` column is printed at the head of the question block."},
    {"line_number": "2A", "line_type": "input", "sort_order": 2,
     "description": "Does the partnership have income or loss derived from sources in Oregon?",
     "source_rules": ["R-OR65-FILE-GATE", "R-OR65-TAX-GATE"]},
    {"line_number": "2B", "line_type": "input", "sort_order": 3,
     "description": "Does the partnership have Oregon resident partners?",
     "source_rules": ["R-OR65-FILE-GATE", "R-OR65-TAX-GATE"],
     "notes": "⚠ The face prints `2B` with no trailing period - a typographic inconsistency, not a transcription error."},
    {"line_number": "3A", "line_type": "calculated", "sort_order": 4,
     "description": ("Tax liability. Did you answer yes to question 1 and question 2A and/or 2B? "
                     "If yes, enter $150; if no, enter 0"),
     "calculation": "150 if (1A AND (2A OR 2B)) else 0; the 12-row published table when checkbox (e) is set",
     "source_rules": ["R-OR65-TAX-GATE", "R-OR65-PRORATION"],
     "notes": "⚠ THE ENTIRE TAX COMPUTATION ON FORM OR-65 IS LINES 3A-3D. There is no income line, no apportionment line and no taxable-income line anywhere on the form."},
    {"line_number": "3B", "line_type": "input", "sort_order": 5,
     "description": "Payments. Enter prepayments already made",
     "source_facts": ["or65_l3b_prepayments"], "source_rules": ["R-OR65-NO-EST"],
     "notes": "Extension payments and voluntary prepayments ONLY - estimated payments are not required."},
    {"line_number": "3C", "line_type": "total", "sort_order": 6,
     "description": "Tax due. If line 3A is more than line 3B, you have tax to pay. Line 3A minus line 3B",
     "calculation": "max(0, 3A - 3B)", "source_rules": ["R-OR65-L3CD"]},
    {"line_number": "3D", "line_type": "total", "sort_order": 7,
     "description": "Refund. If line 3B is more than line 3A, you have a refund. Line 3B minus line 3A",
     "calculation": "max(0, 3B - 3A)", "source_rules": ["R-OR65-L3CD"],
     "notes": "'There is no tax to pay or refund unless you change the amount entered on line 3C or 3D' - the amended-return rule."},
    {"line_number": "4A", "line_type": "input", "sort_order": 8,
     "description": "Did the partners' profit/loss sharing percentages change during the year?"},
    {"line_number": "4B", "line_type": "input", "sort_order": 9,
     "description": "Were the Oregon modifications divided according to each partner's profit sharing percentage?",
     "notes": "⚠ A 'No' means the K-1 amounts will NOT reconcile to `Schedule I total x profit %`. Any tie-out diagnostic must respect 4B."},
    {"line_number": "4C", "line_type": "input", "sort_order": 10,
     "description": "Does the partnership have corporate partners?",
     "notes": "Flags the 6.6%/7.6% corporate withholding branch rather than the 9.9% individual rate."},
    {"line_number": "4D_total", "line_type": "input", "sort_order": 11,
     "description": "Enter the number of federal Schedules K-1 issued to all partners: Total",
     "source_facts": ["or65_l4d_total_k1s"], "source_rules": ["R-OR65-K1-DELIV"],
     "notes": ("⚠ THREE BOXES ALL PRINT THE LABEL '4D' - the grouping is POSITIONAL ONLY. Counts FEDERAL "
               "K-1s ISSUED, not Oregon OR-K-1s and not Form 1065 page 1 line I.")},
    {"line_number": "4D_resident", "line_type": "input", "sort_order": 12, "description": "Oregon residents"},
    {"line_number": "4D_nonres", "line_type": "input", "sort_order": 13, "description": "Nonresidents"},
    {"line_number": "4E", "line_type": "input", "sort_order": 14,
     "description": "If there are nonresident partners, enter how many partners were included on a Form OR-OC",
     "notes": "⚠ FORWARD-LOOKING - 'filed or will be filing'. Can be non-zero before Form OR-OC exists."},
    {"line_number": "5A", "line_type": "input", "sort_order": 15, "description": "Was a 2024 Oregon partnership return filed? If not, why?"},
    {"line_number": "5B", "line_type": "input", "sort_order": 16, "description": "Was an amended federal return filed for a prior year? If yes, what tax year(s) were changed?"},
    {"line_number": "5C", "line_type": "input", "sort_order": 17,
     "description": "Did a federal audit or adjustment change a prior year or the current year tax return?",
     "source_rules": ["R-OR65-CPAR"]},
    {"line_number": "5D", "line_type": "input", "sort_order": 18,
     "description": "Did the partnership make an opt-out election under IRC Section 6221(b) for tax year 2025?",
     "source_rules": ["R-OR65-CPAR"],
     "notes": "A 'No' opens the federal PR contact sub-block, which carries TWO identically-labelled contact-phone fields."},
    {"line_number": "6A", "line_type": "input", "sort_order": 19,
     "description": "Did the partnership have business activity both inside and outside of Oregon during the year?",
     "destination_form": "Schedule OR-AP", "source_rules": ["R-OR65-APPORT"],
     "notes": "⚠ THE ENTIRE APPORTIONMENT INTERFACE. The percentage itself is never printed on Form OR-65."},
    {"line_number": "7A", "line_type": "input", "sort_order": 20,
     "description": "Do partnership employees perform services in the TriMet Transit District?",
     "source_rules": ["R-OR65-TRANSIT"], "notes": "⚠ NO RETURN CONSEQUENCE."},
    {"line_number": "7B", "line_type": "input", "sort_order": 21,
     "description": "Do any partners have self-employment income from the partnership in the TriMet Transit District?",
     "destination_form": "Form OR-TM", "source_rules": ["R-OR65-TRANSIT"]},
    {"line_number": "7C", "line_type": "input", "sort_order": 22,
     "description": "Do partnership employees perform services in the Lane Transit District?",
     "source_rules": ["R-OR65-TRANSIT"], "notes": "⚠ NO RETURN CONSEQUENCE."},
    {"line_number": "7D", "line_type": "input", "sort_order": 23,
     "description": "Do any partners have self-employment income from the partnership in the Lane Transit District?",
     "destination_form": "Form OR-LTD", "source_rules": ["R-OR65-TRANSIT"]},
    {"line_number": "8", "line_type": "input", "sort_order": 30,
     "description": "Schedule I, Additions - row 1 NAME (bare `8`)", "source_rules": ["R-OR65-SCHED-I-NS"],
     "notes": "⚠ THE TRANSCRIPTION TRAP: bare `8` is the NAME field, `8a` is the Code box, `8b` is the Amount box."},
    {"line_number": "8a", "line_type": "input", "sort_order": 31,
     "description": "Schedule I, Additions - row 1 CODE (individual namespace)", "source_rules": ["R-OR65-SCHED-I-NS"]},
    {"line_number": "8b", "line_type": "input", "sort_order": 32, "description": "Schedule I, Additions - row 1 AMOUNT"},
    {"line_number": "9a", "line_type": "input", "sort_order": 33, "description": "Schedule I, Additions - row 2 CODE", "source_rules": ["R-OR65-SCHED-I-NS"]},
    {"line_number": "10a", "line_type": "input", "sort_order": 34, "description": "Schedule I, Additions - row 3 CODE", "source_rules": ["R-OR65-SCHED-I-NS"]},
    {"line_number": "11a", "line_type": "input", "sort_order": 35, "description": "Schedule I, Additions - row 4 CODE", "source_rules": ["R-OR65-SCHED-I-NS"]},
    {"line_number": "12a", "line_type": "input", "sort_order": 36, "description": "Schedule I, Subtractions - row 1 CODE", "source_rules": ["R-OR65-SCHED-I-NS"]},
    {"line_number": "13a", "line_type": "input", "sort_order": 37, "description": "Schedule I, Subtractions - row 2 CODE", "source_rules": ["R-OR65-SCHED-I-NS"]},
    {"line_number": "14a", "line_type": "input", "sort_order": 38, "description": "Schedule I, Subtractions - row 3 CODE", "source_rules": ["R-OR65-SCHED-I-NS"]},
    {"line_number": "15a", "line_type": "input", "sort_order": 39, "description": "Schedule I, Subtractions - row 4 CODE", "source_rules": ["R-OR65-SCHED-I-NS"]},
    {"line_number": "16a", "line_type": "input", "sort_order": 40, "description": "Schedule I, Credits - row 1 CODE", "source_rules": ["R-OR65-SCHED-I-NS"]},
    {"line_number": "17a", "line_type": "input", "sort_order": 41, "description": "Schedule I, Credits - row 2 CODE", "source_rules": ["R-OR65-SCHED-I-NS"]},
    {"line_number": "18a", "line_type": "input", "sort_order": 42, "description": "Schedule I, Credits - row 3 CODE", "source_rules": ["R-OR65-SCHED-I-NS"]},
    {"line_number": "19a", "line_type": "input", "sort_order": 43, "description": "Schedule I, Credits - row 4 CODE", "source_rules": ["R-OR65-SCHED-I-NS"],
     "notes": ("⚠ NO TOTAL LINE FOLLOWS ANY OF THE THREE SECTIONS, and nothing flows to line 3 or to any "
               "other line on Form OR-65 (R-OR65-NO-FOOT / N2). Overflow beyond four rows per section "
               "goes to an attached schedule.")},
]

OR65_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_OR65_TWO_GATES", "severity": "warning",
     "title": "The FILING gate and the TAX gate are different booleans",
     "condition": "(2A or 2B) is true and 1A is false",
     "message": ("This partnership MUST FILE Form OR-65 but OWES NO MINIMUM TAX. Filing is required if "
                 "2A OR 2B; the $150 is owed only if 1A AND (2A OR 2B). A partnership with Oregon "
                 "resident partners but no Oregon business activity files and owes nothing. Verify line "
                 "3A is 0, not $150."),
     "notes": "A build that collapses the two gates bills $150 to every out-of-state partnership that happens to have one Oregon partner."},
    {"diagnostic_id": "D_OR65_PRORATION_SWITCH", "severity": "warning",
     "title": "Short-year proration keys off checkbox (e), NOT the Short-year return box",
     "condition": "the `Short-year return` box is checked and checkbox (e) `Accounting period change` is not",
     "message": ("The 12-row minimum-tax proration chart applies ONLY to a change in accounting periods. "
                 "Verbatim: 'This chart doesn't apply to other short tax year returns, such as initial "
                 "returns or final returns. The tax is $150 in those cases.' Line 3A should be $150."),
     "notes": "Two different boxes on the same page. Keying off the wrong one mis-states the tax in BOTH directions."},
    {"diagnostic_id": "D_OR65_PRORATION_TABLE", "severity": "info",
     "title": "The proration values are a PUBLISHED ROUNDED TABLE, not 150 x n / 12",
     "condition": "checkbox (e) is set",
     "message": ("The DOR publishes twelve rounded values (1=$13, 3=$38, 5=$63, 7=$88, 9=$113, 11=$138 - "
                 "every half-dollar rounds UP). A banker's-rounding implementation produces "
                 "$12/$62/$112 on months 1, 5 and 9 and is wrong on THREE of the twelve rows. (⚠ The "
                 "source brief says five rows and lists $138 among them; $138 is the CORRECT chart value "
                 "and round-half-to-even reproduces it, so the brief's count is wrong - the mandate to "
                 "seed the literal table is not.) Form OR-20-S states the same rule as a bare FORMULA; "
                 "the two authorities are not shared."),
     "notes": "D-12 W6."},
    {"diagnostic_id": "D_OR65_SCHED_I_NAMESPACE", "severity": "error",
     "title": "Schedule I codes must come from Publication OR-CODES (INDIVIDUAL), never OR-ASC-CORP",
     "condition": "a Schedule I code was resolved against the corporate table, or resolved with no namespace",
     "message": ("Form OR-65 Schedule I uses the INDIVIDUAL code set. Twelve numbers collide with the "
                 "corporate set (118, 132, 150, 151, 158, 159, 352, 356, 358, 361 semantically; 338 and "
                 "344 by label). Code 158 means 'interest and dividends on government bonds of other "
                 "states' HERE and 'gain or loss on disposition of depreciable property' on Schedule "
                 "OR-ASC-CORP - and the individual number for THAT item is 154. A mix-up posts a "
                 "depreciation-basis difference onto a municipal-interest line AND THE RETURN STILL "
                 "FOOTS. Map by LABEL, key by NAMESPACE, never carry a bare integer across the boundary."),
     "notes": "C1 / D-12. The two DOR 'don't use these codes on Schedule SM' notes do NOT cover this - they police Schedule SM."},
    {"diagnostic_id": "D_OR65_SCHED_I_NO_FOOT", "severity": "info",
     "title": "Schedule I does not foot and does not flow to the tax computation",
     "condition": "any Schedule I amount is entered",
     "message": ("There is NO total line on any of the three Schedule I sections and NOTHING from "
                 "Schedule I reaches line 3 or any other line on Form OR-65. It is pure pass-through "
                 "reporting: each partner's share rides on their federal Schedule K-1, Schedule OR-K-1 "
                 "or equivalent. If line 4B is 'No', the K-1 amounts will not reconcile to "
                 "`Schedule I total x profit %` and no tie-out should be attempted."),
     "notes": "N2 - a verified negative, pinned in the harness."},
    {"diagnostic_id": "D_OR65_NO_PENALTY_LINE", "severity": "warning",
     "title": "Do NOT put a computed penalty on Form OR-65 - the DOR bills it",
     "condition": "a late-filed or late-paid Form OR-65",
     "message": ("Verbatim: 'Don't submit a penalty payment with the return. Penalty payments are only "
                 "required if the department assesses a penalty.' The OR-65 face has NO penalty or "
                 "interest line at all. Exposure for planning only: $50 per month per partner (counting "
                 "everyone who was a partner during ANY PART of the year - a higher count than the line "
                 "4D K-1 count), capped at five months, per ORS 314.724(3). ⚠ FORM OR-20-S TAKES THE "
                 "OPPOSITE POSTURE and self-assesses at lines 22-24."),
     "notes": "D-12 W6. A shared 'Oregon penalty engine' across the two entity forms is impossible."},
    {"diagnostic_id": "D_OR65_NO_ESTIMATES", "severity": "info",
     "title": "Form OR-65 has no estimated-payment regime at all",
     "condition": "an estimated payment is proposed for a partnership",
     "message": ("Estimated payments are NOT REQUIRED for Form OR-65. Line 3B carries extension and "
                 "voluntary prepayments only. There is no OR-65 analogue to Form OR-37, no underpayment "
                 "interest and no Schedule ES, and Form OR-65-V has only TWO payment types with NO "
                 "`Estimated payment` box."),
     "notes": "N5."},
    {"diagnostic_id": "D_OR65_APPORT_NO_FIELD", "severity": "info",
     "title": "The apportionment percentage has no field on the Form OR-65 face",
     "condition": "line 6A is Yes",
     "message": ("Attach Schedule OR-AP. The percentage lives on Schedule OR-AP part 1 line 23 (four "
                 "decimal places) and is carried by the preparer to each Schedule OR-K-1 Part III "
                 "header. Any model expecting a `state_apportionment_pct` field on the partnership "
                 "return face will find no home for it."),
     "notes": "N6."},
    {"diagnostic_id": "D_OR65_FINAL_RETURN_SCHEDULE", "severity": "error",
     "title": "Final return: a per-asset distribution schedule is required, with no form and no template",
     "condition": "checkbox (a) `Final return` is set",
     "message": ("Verbatim: 'If this is the final partnership return, a schedule showing to whom all "
                 "assets and liabilities were distributed, and each asset's adjusted basis, fair market "
                 "value, and sales price.' This is a free-text attachment obligation with no DOR "
                 "template. Prepare it manually."),
     "notes": "Also required: a NAME-CHANGE attachment when checkbox (d) is set - the prior name has no printed box."},
    {"diagnostic_id": "D_OR65_NO_OREGON_PR_FIELD", "severity": "info",
     "title": "Form OR-65 cannot designate an Oregon partnership representative",
     "condition": "the user attempts to designate an Oregon PR",
     "message": ("Verbatim: 'Don't use Form OR-65 to designate an Oregon partnership representative.' The "
                 "face captures the FEDERAL PR only. An Oregon-only PR is designated by letter, fax or "
                 "Revenue Online - there is no form and no field, and this product must not offer one. "
                 "By default ORS 314.733(2)(a) makes the federal PR the Oregon PR, with sole authority "
                 "binding all direct and indirect partners."),
     "notes": "N9 - a verified negative."},
    {"diagnostic_id": "D_OR65_TRANSIT_7A7C_NO_RETURN", "severity": "info",
     "title": "Lines 7A and 7C produce no partnership return",
     "condition": "7A or 7C is Yes and 7B/7D are No",
     "message": ("Employer transit payroll tax is a payroll-side obligation, not a Delvio artifact. Only "
                 "7B (TriMet) and 7D (Lane) - the PARTNERS' self-employment answers - produce Form OR-TM "
                 "or Form OR-LTD."),
     "notes": "A diagnostic that fires on 7A/7C is wrong."},
    {"diagnostic_id": "D_OR65_FORM_YEAR_SELECTION", "severity": "warning",
     "title": "Short years ending in 2026: use the 2025 form but follow 2026 law",
     "condition": "a short tax year that ends in 2026",
     "message": ("Verbatim: 'Use the 2025 form for a short tax year that ends in 2026, if the 2026 forms "
                 "are not available by the due date. Don't cross out the year on the form. Instead, "
                 "enter the beginning and ending dates for the short year and mark the Short-year return "
                 "box.' The DOR's Example 2 states the rule a form-year-keyed engine must respect: 'They "
                 "will use 2025 forms because 2026 forms aren't available yet, BUT THEY WILL FOLLOW 2026 "
                 "TAX LAWS when completing the return.' ⚠ PUBLICATION OR-OC SAYS THE OPPOSITE FOR THE "
                 "COMPOSITE RETURN - 'Don't use prior year forms.' Same agency, same season, opposite "
                 "instructions. DO NOT SHARE A FORM-YEAR-SELECTION ROUTINE."),
     "notes": "⚠ And 2026 law is NOT 2025 law here: SB 1507 moves the conformity date and decouples from IRC 168(k) for TY2026."},
]

OR65_SCENARIOS: list[dict] = [
    {"scenario_name": "OR-65 THE TWO GATES - resident partners, no Oregon business activity", "scenario_type": "edge",
     "inputs": {"q1a_doing_business": False, "q2a_oregon_source_income": False, "q2b_oregon_resident_partners": True},
     "expected_outputs": {"filing_required": True, "L3A": 0, "L3C": 0, "L3D": 0},
     "notes": "FILES AND OWES NOTHING. The single most likely OR-65 bug is billing $150 here.", "sort_order": 1},
    {"scenario_name": "OR-65 ordinary case - doing business with Oregon-source income", "scenario_type": "normal",
     "inputs": {"q1a_doing_business": True, "q2a_oregon_source_income": True, "q2b_oregon_resident_partners": False,
                "l3b_prepayments": 0},
     "expected_outputs": {"filing_required": True, "L3A": 150, "L3C": 150, "L3D": 0}, "sort_order": 2},
    {"scenario_name": "OR-65 no filing requirement at all", "scenario_type": "edge",
     "inputs": {"q1a_doing_business": True, "q2a_oregon_source_income": False, "q2b_oregon_resident_partners": False},
     "expected_outputs": {"filing_required": False, "L3A": 0},
     "notes": "'If you didn't answer Yes to either 2A or 2B, then the partnership isn't required to file a return or pay the minimum tax.'",
     "sort_order": 3},
    {"scenario_name": "OR-65 PRORATION ORACLE - 9-month accounting period change gives $113, not $112",
     "scenario_type": "edge",
     "inputs": {"q1a_doing_business": True, "q2a_oregon_source_income": True, "q2b_oregon_resident_partners": True,
                "accounting_period_change": True, "months_in_short_period": 9},
     "expected_outputs": {"L3A": 113, "banker_rounding_would_give": 112},
     "notes": ("The DOR's own Example 1 (Renters LLC, Jan 1 - Sep 30, 2025) states $113. 150 x 9/12 = "
               "112.50 and every half-dollar rounds UP. Round-half-to-even diverges on months 1, 5 and 9 "
               "only - the source brief's 'five rows, $12/$62/$112/$138' is arithmetically wrong on both "
               "counts and is corrected here."),
     "sort_order": 4},
    {"scenario_name": "OR-65 PRORATION - a FINAL short-year return is NOT prorated", "scenario_type": "edge",
     "inputs": {"q1a_doing_business": True, "q2a_oregon_source_income": True, "short_year_return": True,
                "accounting_period_change": False, "months_in_short_period": 5},
     "expected_outputs": {"L3A": 150},
     "notes": "The DOR's Example 2 (Freight Partners, ended May 11, 2026) states $150 for a 5-month final year.",
     "sort_order": 5},
    {"scenario_name": "OR-65 CODE NAMESPACE - code 158 on Schedule I is MUNICIPAL INTEREST", "scenario_type": "failure",
     "inputs": {"context": "OR65_SCHEDULE_I", "namespace": "corporate", "code": 158},
     "expected_outputs": {"raises": "OregonCodeNamespaceError",
                          "individual_158": "Interest and dividends on government bonds of other states",
                          "corporate_158": "Gain or loss on disposition of depreciable property",
                          "individual_twin_of_corporate_158": 154},
     "notes": "⚠⚠ C1. The guard must REFUSE. Both codes exist, both resolve, and the return foots either way.",
     "sort_order": 6},
    {"scenario_name": "OR-65 failure-to-file exposure uses partners at ANY TIME, capped at 5 months",
     "scenario_type": "normal",
     "inputs": {"partners_at_any_time": 12, "months_late": 8},
     "expected_outputs": {"exposure": 3000, "posted_to_return": False},
     "notes": "$50 x 12 x min(8, 5) = $3,000. ORS 314.724(3). NEVER posted to the return - there is no penalty line.",
     "sort_order": 7},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM OR_20_S -- FACTS
# ═══════════════════════════════════════════════════════════════════════════
OR20S_FACTS: list[dict] = [
    {"fact_key": "or20s_tax_basis", "label": "Excise tax or Income tax (ONE BOX MUST BE CHECKED)",
     "data_type": "choice", "choices": ["excise", "income"], "required": True, "sort_order": 1,
     "notes": ("⚠⚠ THE HIGHEST-LEVERAGE SINGLE FIELD ON THE FORM. It alone decides whether line 11 is "
               "$150 or 0 AND whether the credit floor is the minimum tax or zero. Excise = doing "
               "business in Oregon (ORS ch. 317). Income = NOT doing business but with Oregon-source "
               "income (ORS ch. 318). ⚠ 'Important: Don't file a Form OR-20-S unless you're required to "
               "do so. Filing an unnecessary return may result in a billing for minimum tax.'")},
    {"fact_key": "or20s_box_or_fcg_20", "label": "OR-FCG-20 attached", "data_type": "boolean", "sort_order": 2,
     "notes": "Drives line 9. ⚠ Schedule OR-FCG-20 (150-102-167) was NOT retrieved - RED-DEFER (U8)."},
    {"fact_key": "or20s_box_extension", "label": "Extension", "data_type": "boolean", "sort_order": 3,
     "notes": ("⚠ A POST-HOC CHECKBOX, NOT A FILING. 'Don't send the extension until you file your Oregon "
               "return.' An 'Oregon only' extension is a REPURPOSED FEDERAL FORM 7004 with 'For Oregon "
               "Only' HANDWRITTEN AT THE TOP - there is no Oregon extension form, and the document is "
               "filed as the LAST PAGE OF THE RETURN.")},
    {"fact_key": "or20s_box_form_or37", "label": "Form OR-37 attached", "data_type": "boolean", "sort_order": 4,
     "notes": "Drives line 24."},
    {"fact_key": "or20s_box_reit_ric", "label": "REIT/RIC", "data_type": "boolean", "sort_order": 5,
     "notes": "⚠ OR-20-S splits REIT/RIC and Form 8886 into TWO boxes where OR-65 box (h) fuses them with a third concept. Do not share the field definition."},
    {"fact_key": "or20s_box_amended", "label": "Amended", "data_type": "boolean", "sort_order": 6,
     "notes": "'Oregon doesn't have an amended return form for corporations.' Fill in ALL amounts, even unchanged ones."},
    {"fact_key": "or20s_box_form_or24", "label": "Form OR-24", "data_type": "boolean", "sort_order": 7},
    {"fact_key": "or20s_box_form_8886", "label": "Federal Form 8886", "data_type": "boolean", "sort_order": 8},
    {"fact_key": "or20s_box_gilti", "label": "GILTI included on federal return", "data_type": "boolean", "sort_order": 9,
     "notes": ("⚠ A BARE INFORMATIONAL CHECKBOX WITH NO COMPUTATION ATTACHED ANYWHERE. No GILTI line, no "
               "add-back, no subtraction, no Appendix A code. DO NOT INVENT ONE (N4). Forward-looking "
               "and NOT TY2025: SB 1510 (2026) replaces GILTI references with NCTI under IRC 951A.")},
    {"fact_key": "or20s_box_accounting_period_change", "label": "Accounting period change", "data_type": "boolean",
     "sort_order": 10,
     "notes": ("EXCISE FILERS ONLY; drives the $150 proration. ⚠ 'A short-period return doesn't "
               "automatically constitute a qualified change in accounting period. A taxpayer that isn't "
               "in existence for the entire year shouldn't check this box.'")},
    {"fact_key": "or20s_box_alt_apportionment", "label": "Alternative apportionment request included",
     "data_type": "boolean", "sort_order": 11,
     "notes": ("⚠ THE BOX FLAGS A REQUEST, NEVER AN APPLIED METHOD. 'Do not complete the original or "
               "amended return using an alternative method of apportionment unless/until that "
               "alternative method has been approved.' A build that lets the checkbox switch the "
               "computation is wrong IN BOTH DIRECTIONS. Approval is PERSISTENT CLIENT STATE across "
               "years - 'remains in effect unless and until we revoke it.'")},
    {"fact_key": "or20s_q_i_utility_telecom", "label": "Question I. Utility or telecommunications company election",
     "data_type": "boolean", "sort_order": 20,
     "notes": ("The ONLY place on the S-corp return where an apportionment method other than single "
               "sales factor lives - the ORS 314.280 double-weighted sales factor. ⚠ The face prints "
               "the Question I text TWICE (a PDF text-layer artifact); it is ONE checkbox.")},
    {"fact_key": "or20s_q_j_federal_ordinary_income",
     "label": "Question J. Ordinary business income or loss from federal Form 1120-S",
     "data_type": "decimal", "sort_order": 21,
     "notes": ("⚠⚠ SOURCE IT FROM 2025 FORM 1120-S LINE 22, NOT the DOR's printed 'line 21' (which is "
               "Total deductions). Stale since TY2023 across four booklet revisions. Question J carries "
               "NO LINE NUMBER ON THE FACE - the stale pointer lives only in the instructions. U3.")},
    {"fact_key": "or20s_q_k_total_oregon_sales", "label": "Question K. Total Oregon sales",
     "data_type": "decimal", "sort_order": 22,
     "notes": ("⚠ FEEDS NOTHING ON FORM OR-20-S (N11). The S-corp minimum tax is a flat $150, not "
               "sales-tiered. It exists because ORS 317.090(1)(a) defines 'Oregon sales' for the "
               "C-CORPORATION table and the DOR collects the datum uniformly. It IS needed downstream on "
               "Schedule OR-OC-2, per corporate composite owner. ⚠ The non-apportioned definition is "
               "explicitly NON-EXCLUSIVE - direct entry with a hint, never computed.")},
    {"fact_key": "or20s_l1a_built_in_gains", "label": "1a. Built-in gains income",
     "data_type": "decimal", "sort_order": 30,
     "notes": ("Federal Form 1120-S Schedule D Part III LINE 18 - `Net recognized built-in gain`, the "
               "INCOME BASE. ⚠ NOT line 23, which is the federal 21% TAX. Negative => enter $0. Line 18 "
               "is already a three-way 'smallest of', so Oregon inherits the federal limitation stack "
               "wholesale.")},
    {"fact_key": "or20s_l1b_excess_net_passive", "label": "1b. Excess net passive income",
     "data_type": "decimal", "sort_order": 31,
     "notes": ("From the IRS instruction-resident 'Worksheet for line 23a'. ⚠ MANUAL-ENTRY ONLY unless "
               "Delvio implements the federal IRC 1375 computation itself. ORS 314.767(4) de-overlaps "
               "1a and 1b BY STATUTE, not by convention.")},
    {"fact_key": "or20s_l2_asc_corp_additions", "label": "2. Total additions from Schedule OR-ASC-CORP, Section A",
     "data_type": "decimal", "sort_order": 32,
     "notes": ("⚠⚠ SCOPE-LIMITED: 'only if apply to amounts included in line 1'. These are NOT the "
               "entity's Oregon modifications - those live on Schedule SM. The two systems are DISJOINT "
               "and use DIFFERENT CODE VOCABULARIES. ⚠ CORPORATE NAMESPACE ONLY.")},
    {"fact_key": "or20s_l3_asc_corp_subtractions", "label": "3. Total subtractions from Schedule OR-ASC-CORP, Section B",
     "data_type": "decimal", "sort_order": 33, "notes": "⚠ CORPORATE NAMESPACE ONLY. Same scope limit as line 2."},
    {"fact_key": "or20s_l5_prior_c_corp_nol", "label": "5. Net loss from prior years as C corporation",
     "data_type": "decimal", "sort_order": 34,
     "notes": ("THREE CONSTRAINTS STACK: (a) usable against BUILT-IN GAIN INCOME ONLY - explicitly not "
               "against excess net passive income even though both sit in line 1c; (b) a 15-YEAR carry "
               "window; (c) MANDATORY REDUCTION BY INTERVENING-YEAR OREGON TAXABLE INCOME [ORS "
               "317.476(4)(b)], so the balance is NOT 'prior losses minus prior usage'. ⚠ Enter as a "
               "POSITIVE number. ⚠ ORS 314.762(2)(d): an S CORPORATION CANNOT GENERATE A NEW OREGON NOL "
               "AT ALL - line 5 can only ever draw down a pre-existing C-corp balance. ⚠ No carryback "
               "unless engaged in crop production, animal production or aquaculture (ORS 317.346).")},
    {"fact_key": "or20s_l6_apportionment_pct", "label": "6. Apportionment percentage from Schedule OR-AP part 1 line 23",
     "data_type": "decimal", "required": True, "sort_order": 35, "default_value": "100.0000",
     "validation_rule": "four decimal places; 100.0000 if not apportioning",
     "notes": ("⚠⚠ COMPLETED EVEN WHEN THE TAX IS ZERO. The face tells a no-BIG/no-ENPI filer to enter "
               "line 6 and then zeroes on 7, 8 and 10. It is the number every NONRESIDENT SHAREHOLDER "
               "needs. THE SINGLE MOST LIKELY OR-20-S BUG IS DROPPING IT.")},
    {"fact_key": "or20s_l9_fcg20_adjustment", "label": "9. Schedule OR-FCG-20 adjustment",
     "data_type": "decimal", "sort_order": 36, "notes": "RED-DEFER - the schedule was not retrieved (U8)."},
    {"fact_key": "or20s_l13_installment_interest", "label": "13. Tax adjustment for installment sales interest",
     "data_type": "decimal", "sort_order": 37,
     "notes": ("ORS 314.302 - INTEREST ADDED TO TAX, sitting ABOVE the credit lines, so credits at line "
               "15 can absorb it. ⚠ ORS 314.302 is one of the sections ORS 314.011(2)(c) PINS TO THE "
               "12/31/2023 IRC.")},
    {"fact_key": "or20s_l15_carryforward_credits", "label": "15. Total carryforward credits from Schedule OR-ASC-CORP, Section D",
     "data_type": "decimal", "sort_order": 38,
     "notes": ("⚠ A CREDIT LINE - the 8xx/999 series, NOT part of the modification-code collision hazard "
               "(the earlier 'lines 2/3/15' rule was corrected). ⚠ U24: PULL 2025 Or. Laws ch. 36 sec. 3 "
               "AND ITS APPLICABILITY DATE BEFORE THIS LINE SHIPS - it amends ORS 314.772 and is the only "
               "2025-session amendment to a load-bearing section in this brief.")},
    {"fact_key": "or20s_l17_lifo_recapture", "label": "17. LIFO benefit recapture addition",
     "data_type": "decimal", "sort_order": 39,
     "notes": ("ONE-THIRD OF THE DEFERRED **TAX**, not of the income - a TAX amount entering a TAX column "
               "despite the word 'addition'. ⚠ It sits BELOW the line-12 minimum comparison AND BELOW "
               "the line-15 credit subtraction, so it STACKS ON TOP OF THE $150 AND CANNOT BE ABSORBED "
               "BY CREDITS. ⚠ FOUR installments total, of which the first landed on the final C-corp "
               "return and THREE land here. ORS 314.771 is pinned to the 12/31/2023 IRC, so 'IRC 1363(d)' "
               "here means the 12/31/2023 version. Interest accrues PER INSTALLMENT.")},
    {"fact_key": "or20s_l19_estimated_payments", "label": "19. Estimated tax payments from Schedule ES line 8",
     "data_type": "decimal", "sort_order": 40,
     "notes": ("⚠ ON AN AMENDED RETURN THIS LINE IS COUNTER-INTUITIVE: 'enter the net excise tax per the "
               "original return or as previously adjusted' - i.e. THE PREVIOUSLY ASSESSED TAX, not the "
               "actual estimated payments. A naive re-run of the original Schedule ES DOUBLE-COUNTS.")},
    {"fact_key": "or20s_l22_penalty", "label": "22. Penalty due with this return", "data_type": "decimal",
     "sort_order": 41,
     "notes": ("⚠⚠ SELF-ASSESSED ON THE FACE. D-12 W6 lands on DIRECT ENTRY WITH A COMPUTED SUGGESTION, "
               "because the 5% waiver test is a FIVE-WAY CONJUNCTION whose last two conditions ('you pay "
               "the balance when you file'; 'you pay the interest') ARE NOT KNOWABLE AT PREPARATION "
               "TIME.")},
    {"fact_key": "or20s_l23_interest", "label": "23. Interest due with this return", "data_type": "decimal",
     "sort_order": 42,
     "notes": ("Daily interest: 8% / 0.0219% per day for periods beginning 1/1/2026; 9% / 0.0247% for "
               "1/1/2025; 8% / 0.0219% for 1/1/2024. ⚠ THE RATE CHANGES AT THE CALENDAR-YEAR BOUNDARY, "
               "so a balance paid late across 12/31/2025 needs a TWO-SEGMENT computation. Interest runs "
               "from the day after the ORIGINAL due date, excluding extensions.")},
    {"fact_key": "or20s_l28_credit_to_estimated", "label": "28. Amount of refund to be credited to the open estimated tax account",
     "data_type": "decimal", "sort_order": 43,
     "notes": "⚠ THE ELECTION IS IRREVOCABLE, and its TIMING changes how it is credited (ORS 314.515, OAR 150-314-0302)."},
    {"fact_key": "or20s_high_income_taxpayer", "label": "High-income taxpayer (federal taxable income >= $1M in any of the 3 prior years)",
     "data_type": "boolean", "sort_order": 44,
     "notes": ("⚠ A LOOKBACK DELVIO CANNOT COMPUTE FROM THE CURRENT RETURN. Persistent client state or "
               "direct entry (D-12 W10). It overrides the $500 estimated-tax exemption.")},
    {"fact_key": "or20s_sm_add_l1_other_state_bond_interest", "label": "Schedule SM line 1. Interest on government bonds of other states",
     "data_type": "decimal", "sort_order": 50,
     "notes": "⚠ Carries a companion `K-1 line` text field on the face."},
    {"fact_key": "or20s_sm_add_l2_depreciable_gain", "label": "Schedule SM line 2. Gain or loss on the sale of depreciable property",
     "data_type": "decimal", "sort_order": 51,
     "notes": ("⚠ THE CITATION IS TO ORS 316.716 - CHAPTER 316 (PERSONAL INCOME TAX), not 317 - because "
               "Schedule SM items are computed under the rules that will apply on the SHAREHOLDERS' "
               "returns. The return-level equivalent at line 2 of the form cites ORS 317.356. Two "
               "statutes, two schedules, same economic item, DIFFERENT TAXPAYER. Carries a `K-1 line` "
               "field.")},
    {"fact_key": "or20s_sm_add_l3_other", "label": "Schedule SM line 3. Other addition (include schedule)",
     "data_type": "decimal", "sort_order": 52,
     "notes": ("⚠ NO `K-1 line` companion field on this line (nor on line 8) - confirmed by y-band "
               "adjacency. ⚠ THE ELECTING ENTITY'S OWN PTE-E ADDITION GOES HERE, as a named 'other "
               "addition' - while the TIERED case (this S corp is a member of a DIFFERENT electing PTE) "
               "goes on Schedule OR-ASC-CORP with code 167. TWO DIFFERENT SCHEDULES FOR TWO DIFFERENT "
               "PTE-E ADDITION SCENARIOS ON THE SAME FORM.")},
    {"fact_key": "or20s_sm_sub_l5_us_interest", "label": "Schedule SM line 5. Interest from U.S. government",
     "data_type": "decimal", "sort_order": 53},
    {"fact_key": "or20s_sm_sub_l6_depreciable_gain", "label": "Schedule SM line 6. Gain or loss on the sale of depreciable property",
     "data_type": "decimal", "sort_order": 54},
    {"fact_key": "or20s_sm_sub_l7_wotc_wage_reduction", "label": "Schedule SM line 7. Work opportunity credit wage reductions",
     "data_type": "decimal", "sort_order": 55},
    {"fact_key": "or20s_sm_sub_l8_other", "label": "Schedule SM line 8. Other subtraction (include schedule)",
     "data_type": "decimal", "sort_order": 56,
     "notes": ("⚠ A GENUINE CIRCULAR DEPENDENCY: 'You may subtract the Oregon corporation tax paid on "
               "built-in gains reported on line 1 of the return' - so lines 12/18 must be computed "
               "FIRST, then Schedule SM. ⚠ U10: ORS 314.763(4) AND (5) provide for BOTH the ORS 314.766 "
               "(built-in gains) and ORS 314.767 (excess net passive income) taxes to reduce shareholder "
               "income, but the DOR's example list names ONLY the built-in-gains tax. The instruction's "
               "cross-reference 'ORS 314.734(4) and (5)' is to the FORMER NUMBERING of ORS 314.763, so "
               "the DOR is in fact pointing at both. WORKING ASSUMPTION: BOTH TAXES REDUCE THE "
               "PASS-THROUGH AMOUNT.")},
    {"fact_key": "or20s_sm_k1_line_refs", "label": "Schedule SM per-modification `K-1 line` reference (free text)",
     "data_type": "string", "sort_order": 57,
     "notes": ("⚠ A DISTINCTIVE OREGON REQUIREMENT WITH NO FEDERAL ANALOGUE. The entity must tell each "
               "shareholder WHICH FEDERAL SCHEDULE K-1 LINE each Oregon modification attaches to. "
               "Nothing in the federal K-1 carries that mapping. THERE IS NO PICKLIST - it is free text. "
               "Present on Schedule SM lines 1, 2, 5, 6 and 7; ABSENT on 3 and 8.")},
]

OR20S_RULES: list[dict] = [
    {"rule_id": "R-OR20S-BASIS", "title": "The excise/income checkbox drives the minimum tax AND the credit floor",
     "rule_type": "classification", "sort_order": 1, "inputs": ["or20s_tax_basis"],
     "outputs": ["OR20S_L11", "credit_floor"],
     "formula": "excise -> L11 = 150 and floor = 150; income -> L11 = 0 and floor = 0",
     "description": ("'Do you pay an excise tax or income tax to Oregon? ONE BOX MUST BE CHECKED.' Excise "
                     "tax is for the privilege of doing business in Oregon (ORS ch. 317); income tax "
                     "reaches an S corporation that derives Oregon-source income but whose "
                     "income-producing activity does not constitute doing business (ORS ch. 318). 'There "
                     "is no minimum tax for a corporate income tax filer.'"),
     "notes": ("⚠ THE $150 AND THE ZERO HAVE DIFFERENT AUTHORITIES. ORS 317.090(2)(b) supplies only the "
               "$150. The ZERO follows from the PREDICATE of ORS 317.090(2) read with ORS 318.020(1) and "
               "ORS 318.031. Cite 318.020/318.031 for the zero side, keyed to the `Income tax` checkbox.")},
    {"rule_id": "R-OR20S-PART1", "title": "Lines 1a-1c, 2, 3, 4 and 7 - and line 7's TWO exclusive paths",
     "rule_type": "calculation", "sort_order": 2,
     "inputs": ["or20s_l1a_built_in_gains", "or20s_l1b_excess_net_passive", "or20s_l2_asc_corp_additions",
                "or20s_l3_asc_corp_subtractions", "or20s_l5_prior_c_corp_nol"],
     "outputs": ["OR20S_L1c", "OR20S_L4", "OR20S_L7"],
     "formula": "L1c = 1a + 1b; L4 = L1c + L2 - L3; L7 = (L4 - L5) OR Schedule OR-AP part 2 line 12 - NEVER both",
     "description": ("⚠ Line 1a takes federal 1120-S Schedule D Part III LINE 18 (`Net recognized built-in "
                     "gain`) - the INCOME base. A build that grabs Schedule D line 23 imports the FEDERAL "
                     "21% TAX as if it were Oregon income. ⚠ The FACE says 'line 1c plus line 2, minus "
                     "line 3' while the instructions say 'line 1 plus line 2, minus line 3' - THE FACE "
                     "WINS (OR-DEF-3). ⚠ 'Most S corporations enter zero' on line 7."),
     "exceptions": ("Lines 2 and 3 are SCOPE-LIMITED to modifications attributable to income taxed AT THE "
                    "ENTITY LEVEL: 'Important: Additions for S corporations with federal taxable income "
                    "or LIFO benefit recapture only. S corporations without built-in gains or excess net "
                    "passive income, start on line 6.'")},
    {"rule_id": "R-OR20S-L6-ALWAYS", "title": "Line 6 is completed EVEN WHEN THE TAX IS ZERO",
     "rule_type": "validation", "sort_order": 3, "inputs": ["or20s_l6_apportionment_pct"], "outputs": ["OR20S_L6"],
     "formula": "L6 is always populated (100.0000 if not apportioning), even when L7 = L8 = L10 = 0",
     "description": ("Printed ON THE FACE above line 1: 'S corporations without built-in gains or excess "
                     "net passive income, fill in your apportionment percentage on line 6 then enter -0- "
                     "on lines 7, 8, and 10 and go to line 11.' ⚠⚠ THE SINGLE MOST LIKELY OR-20-S BUG IS "
                     "SHORT-CIRCUITING TO $150 AND DROPPING LINE 6. It is the number every NONRESIDENT "
                     "SHAREHOLDER depends on: 'Nonresident shareholders must report their ownership "
                     "percentage of modifications, multiplied by the S corporation's Oregon "
                     "apportionment percentage from Schedule OR-AP.'"),
     "notes": "Four decimal places. It lands on every Schedule OR-K-1 Part III header."},
    {"rule_id": "R-OR20S-TAX", "title": "Lines 8-12: 6.6% / 7.6%, then the greater of calculated and minimum tax",
     "rule_type": "calculation", "sort_order": 4, "inputs": ["OR20S_L7", "or20s_tax_basis", "or20s_l9_fcg20_adjustment"],
     "outputs": ["OR20S_L8", "OR20S_L10", "OR20S_L11", "OR20S_L12"],
     "formula": "L8 = 6.6% of the first $1M + 7.6% above (i.e. $66,000 + 7.6% x excess); L10 = L8 - L9; L12 = max(L10, L11)",
     "description": ("ORS 317.061, unamended since 2013. 'Enter 0 if the result is negative or zero' is "
                     "printed only on the <=$1M branch; a negative line 7 in the >$1M branch is "
                     "impossible by construction, so transcribe the asymmetry as printed. 'Don't enter "
                     "minimum tax on this line.' 'Corporation excise tax filers pay the greater of "
                     "calculated tax or minimum tax.'"),
     "notes": ("⚠ THE TWELVE-TIER C-CORPORATION MINIMUM-TAX TABLE AT ORS 317.090(2)(a) DOES NOT APPLY "
               "HERE (N8). S corps get the flat $150 under (2)(b). The table reappears only on Schedule "
               "OR-OC-2, per corporate composite owner, keyed to THAT OWNER'S share of Oregon sales. Do "
               "not let a shared 'Oregon minimum tax' component leak it onto the S-corp return.")},
    {"rule_id": "R-OR20S-L15-FLOOR", "title": "Line 15: four simultaneous constraints, one of which HAS NO FIELD",
     "rule_type": "calculation", "sort_order": 5,
     "inputs": ["or20s_l15_carryforward_credits", "or20s_tax_basis"], "outputs": ["OR20S_L15", "OR20S_L16"],
     "formula": "L15 = min(requested, max(0, L14 - floor)); floor = 150 (excise) or 0 (income)",
     "description": ("(i) the credit must be a CARRYFORWARD FROM A C-CORPORATION YEAR - Appendix A prints "
                     "'Standard credits: None'; (ii) it may offset ONLY the BUILT-IN-GAINS portion of the "
                     "tax, not the excess-net-passive portion and not the minimum tax [ORS 314.766(5)]; "
                     "(iii) the total may not drop excise tax below $150 or income tax below 0; (iv) "
                     "credits apply IN THE ORDER THE PREPARER LISTS THEM - 'we'll apply your credits "
                     "against your tax in the order in which they're listed on the schedule ... List all "
                     "credits you have available even if you can't use them this year.' A GENUINE UI "
                     "REQUIREMENT, not a nicety."),
     "exceptions": ("⚠ CONSTRAINT (ii) HAS NO FIELD ON THE FORM. Line 1c FUSES built-in gains and excess "
                    "net passive income into one number and line 14 is a single tax figure, so there is "
                    "nowhere on Form OR-20-S to show that only the built-in-gains slice was offset. A "
                    "REAL MODELLING GAP -> D_OR20S_L15_BIG_ONLY_NO_FIELD.")},
    {"rule_id": "R-OR20S-NO-C-E", "title": "VERIFIED NEGATIVE: no Section C line and no Section E line on OR-20-S",
     "rule_type": "validation", "sort_order": 6, "inputs": [], "outputs": [],
     "formula": "line 15 draws Section D ONLY; Sections C and E have NO OR-20-S destination",
     "description": ("⚠ ENCODE THE ABSENCE. Confirmed THREE independent ways: (1) the OR-ASC-CORP FACE "
                     "routes `Total C7` to 'Form OR-20, line 17; Form OR-20-INC, line 11; or Form "
                     "OR-20-INS, line 20' and `Total E5` to the OR-20 / OR-20-INC / OR-20-INS Schedule ES "
                     "line 7 - FORM OR-20-S APPEARS IN NEITHER LIST, while A21, B21 and D21 all name it "
                     "explicitly; (2) the schedule instructions say 'Form OR-20-S filers cannot claim "
                     "standard credits' and 'There are no refundable credits available to S "
                     "corporations'; (3) OR-20-S Schedule ES line 7 is printed `7. Reserved`."),
     "notes": ("N3. ⚠⚠ A LIVE LANDMINE: on Form OR-20 and OR-20-INC that same Schedule ES line 7 carries "
               "REFUNDABLE CREDITS. A shared corporate-series component mapping `ASC-CORP E5 -> Schedule "
               "ES line 7` WRITES A REFUNDABLE CREDIT INTO A DEAD BOX ON THE S-CORP RETURN AND THE "
               "ARITHMETIC STILL FOOTS, so nothing catches it.")},
    {"rule_id": "R-OR20S-LINES23-NS", "title": "OR-20-S lines 2 and 3 draw from the CORPORATE namespace ONLY",
     "rule_type": "validation", "sort_order": 7,
     "inputs": ["or20s_l2_asc_corp_additions", "or20s_l3_asc_corp_subtractions"], "outputs": ["namespace_violation"],
     "formula": "or_assert_namespace('OR20S_LINE_2'|'OR20S_LINE_3', NS_CORPORATE)",
     "description": ("⚠⚠ AND SIMULTANEOUSLY, THE SAME ENGAGEMENT MUST EMIT INDIVIDUAL CODES ON THE "
                     "SCHEDULE OR-K-1 OVERFLOW ATTACHMENT IT HANDS EACH SHAREHOLDER. Both namespaces are "
                     "live inside one OR-20-S engagement and the DOR has published no firewall at that "
                     "point. THE COLLISION ANALYSIS GOVERNS LINES 2 AND 3 ONLY - line 15 is a CREDIT line "
                     "drawing the unrelated 8xx/999 Section D series. ⚠ SEED THE CORPORATE TABLE FROM "
                     "THE FULL OR-ASC-CORP UNIVERSE with an OR-20-S eligibility filter on top: Appendix A "
                     "is the S-corp SUBSET and code 341 proves it."),
     "exceptions": ("⚠ Codes 361 and 364 are marked '(income filers only)' - available only when the "
                    "page-1 `Income tax` box is checked. A CHECKBOX-DRIVEN CODE-ELIGIBILITY RULE that a "
                    "generic code-list seeding pass drops on the floor."),
     "notes": "C1 / D-12. HARD failure."},
    {"rule_id": "R-OR20S-SM-SEP", "title": "Schedule SM is NAMED-LINE and CODE-FREE - a different object from Schedule I",
     "rule_type": "validation", "sort_order": 8, "inputs": [], "outputs": [],
     "formula": "Schedule SM carries NO codes; a shared 'PTE modifications' component across OR-65 and OR-20-S is IMPOSSIBLE",
     "description": ("Schedule SM is named-line: additions 1 (other states' bond interest), 2 (gain/loss "
                     "on depreciable property), 3 (other), total 4; subtractions 5 (U.S. government "
                     "interest), 6 (gain/loss), 7 (work opportunity credit wage reductions), 8 (other), "
                     "total 9. Form OR-65 Schedule I is CODE-DRIVEN and FREE-FORM. THEY ARE "
                     "STRUCTURALLY DIFFERENT OBJECTS DOING THE SAME JOB - the largest structural "
                     "divergence between the two entity forms - and the OR-65 partner and the OR-20-S "
                     "shareholder receive their Oregon modifications through TWO DIFFERENT VOCABULARIES "
                     "before both landing on the same Schedule OR-K-1."),
     "notes": ("⚠⚠ THE DECOY. The DOR firewalls Schedule SM explicitly TWICE. Those notes are TRUE AND "
               "IRRELEVANT: they police Schedule SM, which nobody claimed carries codes, and say nothing "
               "about the Schedule OR-K-1 overflow attachment where the namespaces genuinely meet. An "
               "earlier verification pass was fooled by exactly this, refuted the crossing point, and "
               "RETRACTED the refutation. NAMESPACE THE LOOKUP; DO NOT POLICE SCHEDULE SM.")},
    {"rule_id": "R-OR20S-SM-CIRC", "title": "Schedule SM line 8 is CIRCULAR - compute the return first",
     "rule_type": "calculation", "sort_order": 9, "inputs": ["OR20S_L18"], "outputs": ["or20s_sm_sub_l8_other"],
     "formula": "Schedule SM line 8 includes the Oregon tax on built-in gains produced by lines 12/18",
     "description": ("'You may subtract the Oregon corporation tax paid on built-in gains reported on "
                     "line 1 of the return.' ORS 314.763(4): each recognized built-in gain 'shall be "
                     "reduced by its proportionate share of such tax'; (5) does the same for each item "
                     "of passive investment income and the ORS 314.767 tax. ⚠ U10: THE DOR'S EXAMPLE "
                     "LIST NAMES ONLY THE BUILT-IN-GAINS TAX, but its cross-reference 'ORS 314.734(4) "
                     "and (5)' is to the FORMER NUMBERING of ORS 314.763, so the DOR is in fact pointing "
                     "at BOTH. WORKING ASSUMPTION: BOTH TAXES REDUCE THE PASS-THROUGH AMOUNT."),
     "notes": "COMPUTE THE RETURN, THEN SCHEDULE SM."},
    {"rule_id": "R-OR20S-ES-L8", "title": "Schedule ES totals on LINE 8 (the face), not line 7 (the instructions)",
     "rule_type": "calculation", "sort_order": 10, "inputs": [], "outputs": ["OR20S_L19"],
     "formula": "Schedule ES line 8 = lines 1-6 (line 7 is Reserved) -> Form OR-20-S line 19",
     "description": ("OR-DEF-2. The instructions say 'On line 7, enter the total of lines 1 through 6, "
                     "then carry total to Form OR-20-S, line 19'; the face prints `7. Reserved` and `8. "
                     "Total prepayments (carry to line 19 above)`. D-12 W2: THE FACE GOVERNS. ⚠ The "
                     "section header still reads 'and refundable credits' - a leftover from the shared "
                     "OR-20-series layout. Transcribe it as printed but DO NOT LET IT DRIVE A FIELD. ⚠ "
                     "`Payer name` / `Payer FEIN` exist because a payment may be made by an AFFILIATE."),
     "notes": "U4."},
    {"rule_id": "R-OR20S-PENALTY", "title": "PENALTY POSTURE: OR-20-S SELF-ASSESSES (the OPPOSITE of OR-65)",
     "rule_type": "calculation", "sort_order": 11, "inputs": ["or20s_l22_penalty", "or20s_l23_interest"],
     "outputs": ["OR20S_L25", "OR20S_L26"],
     "formula": "L25 = L22 + L23 + L24; L26 = L20 + L25; if L21 > 0 and L21 < L25 then L26 = L25 - L21",
     "description": ("Three penalties, self-assessed: 5% failure-to-pay if not paid by the ORIGINAL due "
                     "date even with an extension; 20% failure-to-file if not filed within THREE MONTHS "
                     "after the due date INCLUDING extensions (in addition to the 5%); 100% if returns "
                     "are not filed for THREE CONSECUTIVE YEARS, assessed on each year's balance. The 5% "
                     "exception is a FIVE-WAY CONJUNCTION and its last two conditions are NOT KNOWABLE "
                     "AT PREPARATION TIME. Interest is DAILY and SEGMENTED at the calendar-year "
                     "boundary. Payments received after the original due date apply first to PENALTY, "
                     "then INTEREST, then TAX [ORS 305.265(13)]."),
     "notes": ("D-12 W6 - direct entry with a computed suggestion. ⚠ FORM OR-65 TAKES THE OPPOSITE "
               "POSTURE and Form OR-21 has a THIRD, narrower set (5% + interest only). THREE SEPARATE "
               "PENALTY MODELS.")},
    {"rule_id": "R-OR20S-EST", "title": "Estimated tax: $500 INCLUDING the minimum tax, unless high-income",
     "rule_type": "conditional", "sort_order": 12,
     "inputs": ["OR20S_L18", "or20s_high_income_taxpayer"], "outputs": ["estimated_required", "OR20S_L24"],
     "formula": "required if net tax >= $500 (INCLUDING the $150 minimum) OR high_income_taxpayer",
     "description": ("'You must make quarterly estimated tax payments if you expect to owe $500 or more "
                     "in tax. THIS INCLUDES OREGON MINIMUM TAX.' An S corp with no built-in gains owes "
                     "exactly $150 and is below the threshold - BUT 'this provision doesn't apply to a "
                     "high-income taxpayer', defined as one with federal taxable income before NOL and "
                     "capital-loss carryovers of $1,000,000 or more IN ANY ONE OF THE LAST THREE YEARS. "
                     "Due dates Apr 15 / Jun 15 / Sep 15 / DEC 15 - a CORPORATE Q4, not the individual "
                     "January 15."),
     "notes": ("⚠ THREE DIFFERENT QUARTERLY CALENDARS COEXIST IN THE OREGON PTE SPACE: OR-20-S ends "
               "Dec 15, Form OR-21 ends Jan 15, and Form OR-65 has none at all. A shared 'Oregon "
               "estimates' component will get at least one wrong. ⚠ EFT is mandatory if federal EFT is - "
               "EXCEPT that amended-return payments must NOT go by EFT, including e-filed amended "
               "returns.")},
    {"rule_id": "R-OR20S-QJ", "title": "Question J: build to the LABEL, not the DOR's stale line pointer",
     "rule_type": "routing", "sort_order": 13, "inputs": ["or20s_q_j_federal_ordinary_income"], "outputs": ["OR20S_QJ"],
     "formula": "pull `Ordinary business income (loss)` = 2025 Form 1120-S LINE 22",
     "description": ("OR-DEF-1 / U3. The DOR prints 'line 21', which on the 2025 Form 1120-S is 'Total "
                     "deductions. Add lines 7 through 20'. STALE SINCE TY2023 across four booklet "
                     "revisions - it was CORRECT in the TY2022 booklet (Rev. 10-28-22) and has been "
                     "reprinted unchanged ever since, including a July-2024 re-revision of the TY2023 "
                     "booklet. ✅ The IRS's own cross-reference settles it: 2025 Schedule K line 1 reads "
                     "'(page 1, line 22)' on the 1120-S and '(page 1, line 23)' on the 1065."),
     "notes": "TY2023 and TY2024 Oregon builds carried the same defect. A TY2026 re-check is mandatory."},
    {"rule_id": "R-OR20S-QK-DEAD", "title": "VERIFIED NEGATIVE: Question K feeds nothing on this form",
     "rule_type": "validation", "sort_order": 14, "inputs": ["or20s_q_k_total_oregon_sales"], "outputs": [],
     "formula": "Question K has NO destination on Form OR-20-S",
     "description": ("The S-corp minimum tax is a flat $150, not sales-tiered. Question K exists because "
                     "ORS 317.090(1)(a) defines 'Oregon sales' for the C-CORPORATION minimum-tax table "
                     "and the DOR collects the datum uniformly across the OR-20 series. DO NOT WIRE IT "
                     "INTO A MINIMUM-TAX LOOKUP ON THE S-CORP FORM. It IS needed downstream on Schedule "
                     "OR-OC-2, where the twelve-tier table applies PER CORPORATE COMPOSITE OWNER, keyed "
                     "to that owner's SHARE of Oregon sales - a datum that appears nowhere on Form OR-65 "
                     "or OR-20-S."),
     "notes": "N11."},
    {"rule_id": "R-OR20S-GILTI-NEG", "title": "VERIFIED NEGATIVE: the GILTI checkbox has no computation",
     "rule_type": "validation", "sort_order": 15, "inputs": ["or20s_box_gilti"], "outputs": [],
     "formula": "no GILTI line, no add-back, no subtraction, no Appendix A code",
     "description": ("The instructions say only 'If you included GILTI on your federal return, check this "
                     "box.' DO NOT INVENT A COMPUTATION. Forward-looking and NOT TY2025: SB 1510 (2026) "
                     "replaces GILTI references with NCTI under IRC 951A, which staleness-invalidates "
                     "this checkbox's MEANING for TY2026."),
     "notes": "N4."},
    {"rule_id": "R-OR20S-ALT-APP", "title": "The alternative-apportionment box flags a REQUEST, never a method",
     "rule_type": "validation", "sort_order": 16, "inputs": ["or20s_box_alt_apportionment"], "outputs": [],
     "formula": "the return is ALWAYS filed on standard apportionment, even while a petition is pending",
     "description": ("Appendix C: 'This box is to denote requests only and isn't to be used after a "
                     "request is approved' and 'Do not complete the original or amended return using an "
                     "alternative method of apportionment unless/until that alternative method has been "
                     "approved.' Method 2 (a separate petition titled 'Alternative apportionment "
                     "request') is the DOR's stated preference, and 'We will not rule on your "
                     "alternative apportionment request until you file your original or amended return "
                     "using standard apportionment provisions.' Allow at least SIX MONTHS."),
     "notes": ("⚠ Approval is PERSISTENT CLIENT STATE - 'remains in effect unless and until we revoke "
               "it.' ⚠ Form OR-65 has NO alternative-apportionment checkbox at all and is absent from "
               "Appendix C's form list, so a partnership appears to have only Method 2 - but ORS "
               "314.667(1) is TAXPAYER-AGNOSTIC ('the taxpayer may petition for'), so the missing "
               "checkbox is a FORM-DESIGN fact, not a statutory bar (U11). ⚠ The settle-by originally "
               "cited OAR 150-314-0067, WHICH DOES NOT EXIST.")},
    {"rule_id": "R-OR20S-DUEDATE", "title": "Due April 15, 2026 - DERIVED, not published",
     "rule_type": "calculation", "sort_order": 17, "inputs": ["or20s_box_extension"], "outputs": ["due_date"],
     "formula": "the 15th day of the month FOLLOWING the federal due date (ORS 314.385(1)(b)); extended likewise",
     "description": ("⚠ THE RULE IS CONFIRMED; THE DATE IS DERIVED. The string 'April 15, 2026' appears "
                     "NOWHERE in the OR-20-S instructions as a return due date. Derivation: federal "
                     "1120-S 3/15/2026 (Sunday) -> 3/16/2026 -> +1 month, 15th = 4/15/2026. The extended "
                     "date derives the same way: federal extended 9/15/2026 -> Oregon 10/15/2026 - 'the "
                     "15th day of the month following what would be the federal extension's due date'. "
                     "ORS 314.385(1)(d) restates the shift for the no-federal-return case."),
     "notes": ("U18 - low risk, the construction is unambiguous, but confirm before a deadline "
               "calculator ships. ⚠ Oregon's corporate returns are due ONE MONTH LATER than the federal "
               "return, which is why OR-20-S and OR-65 diverge by a month despite both following the "
               "federal PTE calendar.")},
    {"rule_id": "R-OR20S-AMEND", "title": "Amended returns: line 19 takes the PRIOR NET TAX, not the payments",
     "rule_type": "calculation", "sort_order": 18, "inputs": ["or20s_box_amended"], "outputs": ["OR20S_L19"],
     "formula": "on an amended return, L19 = net excise tax per the original return or as previously adjusted",
     "description": ("Verbatim: 'On the estimated tax payments line on your amended Form OR-20-S, enter "
                     "the net excise tax per the original return or as previously adjusted. Don't "
                     "include any penalty or interest portions of payments already made.' A NAIVE RE-RUN "
                     "OF THE ORIGINAL SCHEDULE ES DOUBLE-COUNTS. Also: fill in ALL amounts even if "
                     "unchanged; file within 90 DAYS of an original or amended federal or other-state "
                     "return (ORS 314.380); ALWAYS USE THE CURRENT ADDRESS, because the DOR's system "
                     "treats the return as an address-change instruction; and mail an audit-report "
                     "amendment SEPARATELY from the current year's return."),
     "notes": ("⚠ 'Don't amend your Oregon return if you amend the federal return to carry a net "
               "operating loss BACK to prior years. Oregon allows corporations to carry net operating "
               "losses FORWARD only.' ⚠ Protective claims use FORM OR-PCR, never an amended return.")},
    {"rule_id": "R-OR20S-CONFORM", "title": "The frozen-side sections that land ON THIS FORM",
     "rule_type": "classification", "sort_order": 19, "inputs": [], "outputs": ["irc_vintage_per_line"],
     "formula": "ORS 314.302 -> L13; ORS 314.771 -> L17; ORS 314.767(7) -> L1b (the waiver only); ORS 314.525 -> L24; ORS 314.772 -> Schedule OR-K-1 line 19",
     "description": ("⚠ Every one of these is ADMINISTRATIVE or MECHANICAL; NONE of them moves an income "
                     "figure on a TY2025 return. ⚠ CORRECTED DESTINATION: ORS 314.772 lands on SCHEDULE "
                     "OR-K-1 LINE 19 (credits allowable to the SHAREHOLDERS), NOT on OR-20-S line 15. ⚠ "
                     "IRC 1375 IS SPLIT ACROSS BOTH PRONGS BY SUBSECTION: ORS 314.767(6) incorporates "
                     "the MEASUREMENT provisions (arguably rolling) while (7), the 1375(d) waiver, is "
                     "expressly frozen. OBBBA did not amend 1375, so the distinction is INERT for TY2025 "
                     "(U12). ⚠ Oregon's CORPORATE NOL rules live in ORS 317.476/317.479, NOT in chapter "
                     "314, so the chapter-314 freeze list does not reach them."),
     "notes": "⚠⚠ SB 1507 moves the fixed date to 12/31/2025 for TY2026. EVERY ROW HERE IS TY2025-ONLY."},
    {"rule_id": "R-OR20S-DEPR-NEG", "title": "VERIFIED NEGATIVE: OR-ASC-CORP codes 174/353 stay empty for new assets",
     "rule_type": "validation", "sort_order": 20, "inputs": [], "outputs": [],
     "formula": "no TY2025 IRC 168(k) or 179 difference; Schedule OR-DEPR produces zero for TY2025 acquisitions",
     "description": ("⚠ DO NOT READ THE 'What's new' DISCONNECT BULLET AS CURRENT. It says 'Deferral of "
                     "certain deductions for tax years beginning on or after January 1, 2009 and before "
                     "January 1, 2011 MAY REQUIRE SUBSEQUENT Oregon modifications (IRC 168(k) and 179; "
                     "ORS 317.301)' - and ORS 317.301's applicability note closes the window at 1/1/2011. "
                     "Its only TY2025 relevance is subsection (4), the UNWIND. Schedule OR-DEPR is a "
                     "WORKSHEET, not a filed form ('Don't include this form with your Oregon return'), "
                     "and it is absent from the assembly list; only the NET DIFFERENCE rides onto the "
                     "return as OR-ASC-CORP addition 174 / subtraction 353 (or as Schedule I codes "
                     "152/354 on Form OR-65 - the INDIVIDUAL numbers)."),
     "notes": ("N1. ⚠ Schedule OR-DEPR column 1b reads 'Date placed in service IN OREGON' and column 1d "
               "is a separate 'Oregon cost or other basis' - the hook for the "
               "property-transferred-into-Oregon rule, and the reason a PER-ASSET DUAL BASIS must exist "
               "in the asset model even though TY2025 acquisitions create no new difference. ⚠ The face "
               "also carries SSN and spouse fields, dead for a PTE, because one schedule serves "
               "individuals, partnerships, corporations and fiduciaries.")},
]

OR20S_RULE_LINKS: list[tuple] = [
    ("R-OR20S-BASIS", "OR_2025_FORM_OR20S", "primary", "the excise/income box is the first field on the face"),
    ("R-OR20S-BASIS", "OR_ORS_317_061_090_RATES", "primary", "ORS 317.090(2)(b) supplies the $150"),
    ("R-OR20S-BASIS", "OR_ORS_318_020_031_INCOME", "primary", "ORS 318.020/318.031 supply the ZERO"),
    ("R-OR20S-PART1", "OR_2025_FORM_OR20S", "primary", "lines 1a-1c, 2, 3, 4, 7 as printed"),
    ("R-OR20S-PART1", "OR_IRS_2025_1065_1120S", "implementation", "Schedule D (1120-S) Part III line 18 - the INCOME base"),
    ("R-OR20S-PART1", "OR_ORS_314_762_772_SCORP", "primary", "ORS 314.766 / 314.767 impose the two taxes"),
    ("R-OR20S-L6-ALWAYS", "OR_2025_FORM_OR20S", "primary", "the printed skip rule above line 1"),
    ("R-OR20S-L6-ALWAYS", "OR_2025_SCH_OR_K1", "implementation", "where the percentage lands for the shareholders"),
    ("R-OR20S-TAX", "OR_ORS_317_061_090_RATES", "primary", "ORS 317.061 and 317.090"),
    ("R-OR20S-TAX", "OR_2025_FORM_OR20S_INSTR", "implementation", "Appendix B restates the rate and the greater-of rule"),
    ("R-OR20S-L15-FLOOR", "OR_2025_SCH_ASC_CORP", "primary", "the credit floor forks on the excise/income checkbox"),
    ("R-OR20S-L15-FLOOR", "OR_ORS_314_762_772_SCORP", "primary", "ORS 314.766(5) - carryforwards, built-in gains only"),
    ("R-OR20S-NO-C-E", "OR_2025_SCH_ASC_CORP", "primary", "the face routes C7 and E5 away from OR-20-S"),
    ("R-OR20S-NO-C-E", "OR_2025_FORM_OR20S", "primary", "Schedule ES line 7 is printed `Reserved`"),
    ("R-OR20S-LINES23-NS", "OR_2025_SCH_ASC_CORP", "primary", "the CORPORATE code universe"),
    ("R-OR20S-LINES23-NS", "OR_2025_PUB_OR_CODES", "secondary", "the INDIVIDUAL namespace this rule excludes from lines 2/3"),
    ("R-OR20S-LINES23-NS", "OR_2025_SCH_OR_K1", "secondary", "⚠ and REQUIRES on the overflow attachment - the crossing point"),
    ("R-OR20S-SM-SEP", "OR_2025_FORM_OR20S", "primary", "Schedule SM is printed on the OR-20-S face, pages 5-6"),
    ("R-OR20S-SM-SEP", "OR_2025_FORM_OR20S_INSTR", "implementation", "the Schedule SM firewall note - HALF THE DECOY"),
    ("R-OR20S-SM-CIRC", "OR_ORS_314_762_772_SCORP", "primary", "ORS 314.763(4)-(5)"),
    ("R-OR20S-SM-CIRC", "OR_2025_FORM_OR20S_INSTR", "implementation", "the Schedule SM line 8 example list"),
    ("R-OR20S-ES-L8", "OR_2025_FORM_OR20S", "primary", "the face prints 7. Reserved and 8. Total prepayments"),
    ("R-OR20S-PENALTY", "OR_2025_FORM_OR20S", "primary", "lines 22-26 as printed"),
    ("R-OR20S-PENALTY", "OR_2025_FORM_OR20S_INSTR", "implementation", "the three penalties and the five-way exception"),
    ("R-OR20S-EST", "OR_2025_FORM_OR20S_INSTR", "primary", "the $500 threshold including minimum tax"),
    ("R-OR20S-QJ", "OR_IRS_2025_1065_1120S", "primary", "2025 Form 1120-S line 22 and Schedule K's own cross-reference"),
    ("R-OR20S-QJ", "OR_2025_FORM_OR20S_INSTR", "implementation", "the stale pointer, logged not silently corrected"),
    ("R-OR20S-QK-DEAD", "OR_ORS_317_061_090_RATES", "primary", "ORS 317.090(1)(a) defines Oregon sales for the C-corp table"),
    ("R-OR20S-GILTI-NEG", "OR_2025_FORM_OR20S_INSTR", "primary", "'If you included GILTI on your federal return, check this box' - and nothing else"),
    ("R-OR20S-ALT-APP", "OR_2025_FORM_OR20S_INSTR", "primary", "Appendix C, both methods"),
    ("R-OR20S-ALT-APP", "OR_2025_SCH_OR_AP", "secondary", "'the business must still complete Schedule OR-AP'"),
    ("R-OR20S-DUEDATE", "OR_ORS_314_385_DUE", "primary", "ORS 314.385(1)(b) and (1)(d)"),
    ("R-OR20S-AMEND", "OR_2025_FORM_OR20S_INSTR", "primary", "the amended-return section, Instr. p. 5"),
    ("R-OR20S-CONFORM", "OR_ORS_314_011_CONFORMITY", "primary", "the (2)(c) enumeration"),
    ("R-OR20S-CONFORM", "OR_ORS_317_010_CONFORMITY", "primary", "the corporate-excise twin, already seeded"),
    ("R-OR20S-CONFORM", "OR_SB1507_2026_CH142", "secondary", "the TY2026 tripwire"),
    ("R-OR20S-CONFORM", "OR_ORS_314_762_772_SCORP", "secondary", "⚠ U24 - ORS 314.772's 2025 c.36 s.3 amendment is unpulled"),
    ("R-OR20S-DEPR-NEG", "OR_ORS_317_301_DEPR", "primary", "the closed 2009-2011 window"),
    ("R-OR20S-DEPR-NEG", "OR_2025_PUB_OR17", "primary", "the DOR's own 'not disconnected' statement"),
]


OR20S_LINES: list[dict] = [
    {"line_number": "J", "line_type": "input", "sort_order": 1,
     "description": "Question J. Enter ordinary business income or loss from federal Form 1120-S",
     "source_rules": ["R-OR20S-QJ"], "source_facts": ["or20s_q_j_federal_ordinary_income"],
     "notes": "⚠ 2025 Form 1120-S LINE 22. The DOR prints 'line 21' (= Total deductions) and has since TY2023. No line number on the face."},
    {"line_number": "K", "line_type": "input", "sort_order": 2,
     "description": "Question K. Fill in the amount of your total Oregon sales",
     "source_rules": ["R-OR20S-QK-DEAD"],
     "notes": "⚠ FEEDS NOTHING ON THIS FORM. Needed downstream on Schedule OR-OC-2 only."},
    {"line_number": "1a", "line_type": "input", "sort_order": 3,
     "description": "Income taxed on federal Form 1120-S from: (a) Built-in gains",
     "source_rules": ["R-OR20S-PART1"],
     "notes": "Federal Schedule D (1120-S) Part III LINE 18 - the INCOME base. Negative => $0."},
    {"line_number": "1b", "line_type": "input", "sort_order": 4,
     "description": "Income taxed on federal Form 1120-S from: (b) Excess net passive income",
     "source_rules": ["R-OR20S-PART1"],
     "notes": "The IRS instruction-resident 'Worksheet for line 23a'. MANUAL ENTRY ONLY in v1."},
    {"line_number": "1c", "line_type": "subtotal", "sort_order": 5, "description": "Total: Line 1a plus line 1b",
     "calculation": "1a + 1b", "source_rules": ["R-OR20S-PART1"],
     "notes": "⚠ FUSES the two bases into one number, which is why the built-in-gains-only credit constraint has no field."},
    {"line_number": "2", "line_type": "input", "sort_order": 6,
     "description": "Total additions from Schedule OR-ASC-CORP, Section A (only if apply to amounts included in line 1)",
     "source_rules": ["R-OR20S-PART1", "R-OR20S-LINES23-NS"], "notes": "⚠ CORPORATE NAMESPACE ONLY."},
    {"line_number": "3", "line_type": "input", "sort_order": 7,
     "description": "Total subtractions from Schedule OR-ASC-CORP, Section B (only if apply to amounts included in line 1)",
     "source_rules": ["R-OR20S-PART1", "R-OR20S-LINES23-NS"], "notes": "⚠ CORPORATE NAMESPACE ONLY."},
    {"line_number": "4", "line_type": "subtotal", "sort_order": 8,
     "description": "S corporation income before net loss deduction (line 1c plus line 2, minus line 3)",
     "calculation": "1c + 2 - 3", "source_rules": ["R-OR20S-PART1"],
     "notes": "⚠ THE FACE says 1c; the instructions say 'line 1'. THE FACE WINS (OR-DEF-3)."},
    {"line_number": "5", "line_type": "input", "sort_order": 9,
     "description": "Net loss from prior years as C corporation (deductible from built-in gain income only), as a positive number",
     "source_facts": ["or20s_l5_prior_c_corp_nol"],
     "notes": "Three stacked constraints; an S corporation cannot generate a NEW Oregon NOL at all."},
    {"line_number": "6", "line_type": "input", "sort_order": 10,
     "description": "Enter the apportionment percentage from Schedule OR-AP, part 1, line 23. Enter 100.0000 if you don't apportion income",
     "source_rules": ["R-OR20S-L6-ALWAYS"], "destination_form": "Schedule OR-K-1 Part III header",
     "notes": "⚠⚠ COMPLETED EVEN AT ZERO TAX. THE SINGLE MOST LIKELY OR-20-S BUG."},
    {"line_number": "7", "line_type": "calculated", "sort_order": 11,
     "description": "Oregon taxable income (line 4 minus line 5, or from Schedule OR-AP, part 2, line 12)",
     "calculation": "(4 - 5) XOR Schedule OR-AP part 2 line 12", "source_rules": ["R-OR20S-PART1"],
     "notes": "TWO MUTUALLY EXCLUSIVE DERIVATIONS - a build must not do both. 'Most S corporations enter zero.'"},
    {"line_number": "8", "line_type": "calculated", "sort_order": 12, "description": "Calculated tax",
     "calculation": "6.6% of the first $1,000,000 + 7.6% above (i.e. $66,000 + 7.6% x excess)",
     "source_rules": ["R-OR20S-TAX"], "notes": "'Don't enter minimum tax on this line.'"},
    {"line_number": "9", "line_type": "input", "sort_order": 13, "description": "Schedule OR-FCG-20 adjustment",
     "notes": "RED-DEFER (U8) - the schedule was not retrieved."},
    {"line_number": "10", "line_type": "calculated", "sort_order": 14, "description": "Total calculated tax (line 8 minus line 9)",
     "calculation": "8 - 9", "source_rules": ["R-OR20S-TAX"]},
    {"line_number": "11", "line_type": "calculated", "sort_order": 15, "description": "Minimum tax",
     "calculation": "$150 if the Excise tax box is checked, else 0", "source_rules": ["R-OR20S-BASIS", "R-OR20S-TAX"],
     "notes": "⚠ THE $150 comes from ORS 317.090(2)(b); the ZERO comes from ORS 318.020/318.031, NOT from 317.090."},
    {"line_number": "12", "line_type": "calculated", "sort_order": 16, "description": "Tax (greater of line 10 or line 11)",
     "calculation": "max(10, 11)", "source_rules": ["R-OR20S-TAX"]},
    {"line_number": "13", "line_type": "input", "sort_order": 17,
     "description": "Tax adjustment for installment sales interest (include schedule)",
     "notes": "ORS 314.302 - frozen at the 12/31/2023 IRC. Interest ADDED TO TAX, above the credit lines."},
    {"line_number": "14", "line_type": "subtotal", "sort_order": 18, "description": "Tax before credits (line 12 plus line 13)",
     "calculation": "12 + 13"},
    {"line_number": "15", "line_type": "input", "sort_order": 19,
     "description": "Total carryforward credits from Schedule OR-ASC-CORP, Section D",
     "source_rules": ["R-OR20S-L15-FLOOR", "R-OR20S-NO-C-E"],
     "notes": "⚠ SECTION D ONLY - there is no Section C line and no Section E line on this form. ⚠ U24 blocks this line."},
    {"line_number": "16", "line_type": "calculated", "sort_order": 20, "description": "Tax after carryforward credits (line 14 minus line 15)",
     "calculation": "14 - 15", "source_rules": ["R-OR20S-L15-FLOOR"]},
    {"line_number": "17", "line_type": "input", "sort_order": 21, "description": "LIFO benefit recapture addition",
     "notes": "⚠ ONE-THIRD OF THE DEFERRED TAX. Stacks ON TOP of the $150 and cannot be absorbed by credits."},
    {"line_number": "18", "line_type": "total", "sort_order": 22, "description": "Net tax (line 16 plus line 17)",
     "calculation": "16 + 17"},
    {"line_number": "19", "line_type": "input", "sort_order": 23,
     "description": "Estimated tax payments from Schedule ES line 8. Include payments made with extension",
     "source_rules": ["R-OR20S-ES-L8", "R-OR20S-AMEND"],
     "notes": "⚠ FROM SCHEDULE ES LINE 8 (the face), not line 7 (the instructions). ⚠ On an AMENDED return this carries the PRIOR NET TAX instead."},
    {"line_number": "20", "line_type": "calculated", "sort_order": 24, "description": "Tax due. Is line 18 more than line 19? If so, line 18 minus line 19",
     "calculation": "max(0, 18 - 19)"},
    {"line_number": "21", "line_type": "calculated", "sort_order": 25, "description": "Overpayment. Is line 18 less than line 19? If so, line 19 minus line 18",
     "calculation": "max(0, 19 - 18)"},
    {"line_number": "22", "line_type": "input", "sort_order": 26, "description": "Penalty due with this return",
     "source_rules": ["R-OR20S-PENALTY"], "notes": "⚠ SELF-ASSESSED. THE OPPOSITE OF FORM OR-65."},
    {"line_number": "23", "line_type": "input", "sort_order": 27, "description": "Interest due with this return",
     "source_rules": ["R-OR20S-PENALTY"], "notes": "DAILY and SEGMENTED at the calendar-year boundary."},
    {"line_number": "24", "line_type": "input", "sort_order": 28, "description": "Interest on underpayment of estimated tax (include Form OR-37)",
     "source_rules": ["R-OR20S-EST"]},
    {"line_number": "25", "line_type": "subtotal", "sort_order": 29, "description": "Total penalty and interest (add lines 22 through 24)",
     "calculation": "22 + 23 + 24"},
    {"line_number": "26", "line_type": "total", "sort_order": 30, "description": "Total due (line 20 plus line 25)",
     "calculation": "20 + 25; SPECIAL RULE: if line 21 > 0 and line 21 < line 25, enter line 25 minus line 21",
     "source_rules": ["R-OR20S-PENALTY"],
     "notes": "Payments after the original due date apply first to PENALTY, then INTEREST, then TAX [ORS 305.265(13)]."},
    {"line_number": "27", "line_type": "calculated", "sort_order": 31, "description": "Refund available (line 21 minus line 25)",
     "calculation": "21 - 25"},
    {"line_number": "28", "line_type": "input", "sort_order": 32, "description": "Amount of refund to be credited to your open estimated tax account",
     "notes": "⚠ THE ELECTION IS IRREVOCABLE, and its timing changes how it is credited."},
    {"line_number": "29", "line_type": "total", "sort_order": 33, "description": "Net refund (line 27 minus line 28)", "calculation": "27 - 28"},
    {"line_number": "SM-1", "line_type": "input", "sort_order": 40, "description": "Schedule SM addition 1. Interest on government bonds of other states",
     "source_rules": ["R-OR20S-SM-SEP"], "notes": "⚠ Carries a `K-1 line` companion field."},
    {"line_number": "SM-2", "line_type": "input", "sort_order": 41, "description": "Schedule SM addition 2. Gain or loss on the sale of depreciable property",
     "source_rules": ["R-OR20S-SM-SEP"], "notes": "Cites ORS 316.716 - CHAPTER 316, not 317. `K-1 line` field present."},
    {"line_number": "SM-3", "line_type": "input", "sort_order": 42, "description": "Schedule SM addition 3. Other addition (include schedule)",
     "source_rules": ["R-OR20S-SM-SEP"],
     "notes": "⚠ NO `K-1 line` field. The ELECTING ENTITY'S OWN PTE-E addition goes here as a named other addition."},
    {"line_number": "SM-4", "line_type": "subtotal", "sort_order": 43, "description": "Schedule SM line 4. Total Oregon additions",
     "calculation": "SM-1 + SM-2 + SM-3"},
    {"line_number": "SM-5", "line_type": "input", "sort_order": 44, "description": "Schedule SM subtraction 5. Interest from U.S. government, such as Series EE and HH bonds",
     "source_rules": ["R-OR20S-SM-SEP"]},
    {"line_number": "SM-6", "line_type": "input", "sort_order": 45, "description": "Schedule SM subtraction 6. Gain or loss on the sale of depreciable property",
     "source_rules": ["R-OR20S-SM-SEP"]},
    {"line_number": "SM-7", "line_type": "input", "sort_order": 46, "description": "Schedule SM subtraction 7. Work opportunity credit wage reductions",
     "source_rules": ["R-OR20S-SM-SEP"]},
    {"line_number": "SM-8", "line_type": "input", "sort_order": 47, "description": "Schedule SM subtraction 8. Other subtraction (include schedule)",
     "source_rules": ["R-OR20S-SM-CIRC"],
     "notes": "⚠ NO `K-1 line` field. CIRCULAR - includes the Oregon tax on built-in gains from lines 12/18."},
    {"line_number": "SM-9", "line_type": "subtotal", "sort_order": 48, "description": "Schedule SM line 9. Total Oregon subtractions",
     "calculation": "SM-5 + SM-6 + SM-7 + SM-8"},
    {"line_number": "ES-7", "line_type": "informational", "sort_order": 50, "description": "Schedule ES line 7. Reserved",
     "source_rules": ["R-OR20S-NO-C-E", "R-OR20S-ES-L8"],
     "notes": ("⚠⚠ A DEAD FIELD ON THIS FORM AND A LIVE REFUNDABLE-CREDIT FIELD ON FORM OR-20 / OR-20-INC. "
               "A shared component mapping ASC-CORP E5 here writes into it AND THE RETURN STILL FOOTS.")},
    {"line_number": "ES-8", "line_type": "total", "sort_order": 51, "description": "Schedule ES line 8. Total prepayments (carry to line 19 above)",
     "calculation": "ES lines 1 through 6", "destination_form": "Form OR-20-S line 19",
     "source_rules": ["R-OR20S-ES-L8"], "notes": "⚠ THE FACE WINS over the instruction's 'line 7'."},
]

OR20S_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_OR20S_BASIS_BOX_REQUIRED", "severity": "error",
     "title": "One box MUST be checked - excise or income",
     "condition": "neither the Excise tax nor the Income tax box is set",
     "message": ("'Do you pay an excise tax or income tax to Oregon? One box must be checked.' Excise if "
                 "you do business in Oregon; income if you don't but have Oregon-source income. This is "
                 "the highest-leverage single field on the form: it decides whether line 11 is $150 or 0 "
                 "and whether the credit floor is the minimum tax or zero."),
     "notes": "The $150 rests on ORS 317.090(2)(b); the ZERO rests on ORS 318.020(1) and ORS 318.031."},
    {"diagnostic_id": "D_OR20S_L6_ZERO_TAX", "severity": "error",
     "title": "Line 6 is required even though lines 7, 8 and 10 are zero",
     "condition": "no built-in gains and no excess net passive income, and line 6 is blank",
     "message": ("The face directs: 'S corporations without built-in gains or excess net passive income, "
                 "fill in your apportionment percentage on line 6 then enter -0- on lines 7, 8, and 10 "
                 "and go to line 11.' Line 6 is the number every NONRESIDENT SHAREHOLDER needs to "
                 "compute their Oregon-source share, and it lands on every Schedule OR-K-1 Part III "
                 "header. Enter 100.0000 if you do not apportion."),
     "notes": "The single most likely OR-20-S bug: short-circuiting the whole form to $150."},
    {"diagnostic_id": "D_OR20S_QJ_STALE_POINTER", "severity": "warning",
     "title": "The DOR's Question J federal line pointer is stale by three form years",
     "condition": "Question J is populated",
     "message": ("The instructions say 'federal Form 1120-S, line 21'. On the 2025 Form 1120-S line 21 is "
                 "'Total deductions. Add lines 7 through 20' and ORDINARY BUSINESS INCOME IS LINE 22. "
                 "The pointer was correct in the TY2022 booklet and has been reprinted unchanged through "
                 "TY2023, TY2024 and TY2025. Build to the LABEL. The IRS's own Schedule K line 1 "
                 "cross-reference reads '(page 1, line 22)'."),
     "notes": "OR-DEF-1 / U3. TY2023 and TY2024 Oregon builds carried the same defect."},
    {"diagnostic_id": "D_OR20S_ES_TOTAL_LINE8", "severity": "warning",
     "title": "Schedule ES totals on line 8, not line 7 - line 7 is Reserved",
     "condition": "Schedule ES is populated",
     "message": ("The instructions say 'On line 7, enter the total of lines 1 through 6'; the FACE prints "
                 "'7. Reserved' and '8. Total prepayments (carry to line 19 above)'. The face governs. ⚠ "
                 "On Form OR-20 and OR-20-INC that same line 7 carries REFUNDABLE CREDITS - a shared "
                 "corporate-series component that maps OR-ASC-CORP Section E to Schedule ES line 7 will "
                 "write into a dead box here and the arithmetic will still foot."),
     "notes": "OR-DEF-2 / U4."},
    {"diagnostic_id": "D_OR20S_NO_SECTION_C_OR_E", "severity": "info",
     "title": "S corporations have no standard credits and no refundable credits",
     "condition": "a Section C or Section E amount is proposed for this return",
     "message": ("Verbatim: 'Form OR-20-S filers cannot claim standard credits although some credits can "
                 "flow through to shareholders' and 'There are no refundable credits available to S "
                 "corporations.' The OR-ASC-CORP face routes Total C7 and Total E5 to OR-20, OR-20-INC "
                 "and OR-20-INS only. Appendix A prints 'Standard credits: None'. Line 15 draws SECTION D "
                 "ONLY."),
     "notes": "N3 - a verified negative, pinned in the harness."},
    {"diagnostic_id": "D_OR20S_L15_BIG_ONLY_NO_FIELD", "severity": "warning",
     "title": "Carryforward credits may offset the built-in-gains tax ONLY, and the form has no field to show it",
     "condition": "line 15 is non-zero and line 1b (excess net passive income) is also non-zero",
     "message": ("ORS 314.766(5): credits carried forward from C-corporation years offset the built-in-"
                 "gains tax only - NOT the excess-net-passive tax and NOT the minimum tax. Line 1c FUSES "
                 "the two bases and line 14 is a single tax figure, so there is NOWHERE ON FORM OR-20-S "
                 "to show that only the built-in-gains slice was offset. Verify the credit manually and "
                 "retain the computation. The DOR's own gate: 'These credits can apply to tax on "
                 "recognized built-in gains only.'"),
     "notes": "A real modelling gap, not a transcription issue."},
    {"diagnostic_id": "D_OR20S_L15_U24_UNPULLED", "severity": "error",
     "title": "Line 15 is BLOCKED: ORS 314.772's 2025-session amendment was never run down",
     "condition": "line 15 is populated",
     "message": ("ORS 314.772 carries the credit line '[... 2025 c.36 s.3]'. IT IS THE ONLY LOAD-BEARING "
                 "ORS SECTION IN THE OREGON PTE BRIEF WITH A 2025-SESSION AMENDMENT, and its "
                 "applicability date was never pulled - so the served text may or may not be the TY2025 "
                 "text. PULL 2025 Or. Laws ch. 36 sec. 3 AND ITS APPLICABILITY SECTION FROM OLIS BEFORE "
                 "AUTHORING OR SHIPPING THIS LINE."),
     "notes": "U24, added by the verification pass. A pre-seed blocker recorded in the seed guard."},
    {"diagnostic_id": "D_OR20S_LINES23_NAMESPACE", "severity": "error",
     "title": "Lines 2 and 3 must draw from Schedule OR-ASC-CORP (CORPORATE), never Publication OR-CODES",
     "condition": "a line 2 or line 3 code was resolved against the individual table, or with no namespace",
     "message": ("Twelve numbers collide. Code 158 means 'gain or loss on disposition of depreciable "
                 "property' HERE and 'interest and dividends on government bonds of other states' in the "
                 "individual set - and the individual number for THIS item is 154. ⚠⚠ AND THE SAME "
                 "ENGAGEMENT MUST SIMULTANEOUSLY EMIT INDIVIDUAL CODES ON THE SCHEDULE OR-K-1 OVERFLOW "
                 "ATTACHMENT IT HANDS EACH SHAREHOLDER. Both namespaces are live inside one OR-20-S "
                 "engagement. Map by LABEL, key by NAMESPACE. ⚠ Codes 361 and 364 are available ONLY to "
                 "an INCOME-tax filer."),
     "notes": ("C1 / D-12. ⚠ The two DOR 'don't use OR-ASC-CORP codes on Schedule SM' notes DO NOT COVER "
               "THIS - they police Schedule SM, which is code-free. An earlier verification pass was "
               "fooled by exactly that and retracted its refutation.")},
    {"diagnostic_id": "D_OR20S_SM_K1_LINE_REQUIRED", "severity": "warning",
     "title": "Every Schedule SM modification needs a federal `K-1 line` reference",
     "condition": "a Schedule SM line 1, 2, 5, 6 or 7 amount is entered without its `K-1 line` text",
     "message": ("Schedule SM header, verbatim: 'Indicate which federal Schedule K-1 line item each "
                 "modification is for.' This has NO FEDERAL ANALOGUE - nothing in the federal K-1 carries "
                 "that mapping - and there is NO PICKLIST; it is free text. Lines 1, 2, 5, 6 and 7 carry "
                 "the companion field; lines 3 and 8 do not."),
     "notes": "Confirmed by y-band adjacency on the face."},
    {"diagnostic_id": "D_OR20S_SM_CIRCULAR", "severity": "info",
     "title": "Schedule SM line 8 depends on the tax the return computes",
     "condition": "line 1a (built-in gains) or line 1b (excess net passive income) is non-zero",
     "message": ("'You may subtract the Oregon corporation tax paid on built-in gains reported on line 1 "
                 "of the return.' COMPUTE THE RETURN FIRST, THEN SCHEDULE SM. ⚠ ORS 314.763(4) AND (5) "
                 "provide for BOTH the built-in-gains tax and the excess-net-passive tax to reduce "
                 "shareholder income; the DOR's example list names only the first, but its "
                 "cross-reference 'ORS 314.734(4) and (5)' is to the FORMER NUMBERING of ORS 314.763 and "
                 "therefore points at both. Working assumption: BOTH reduce the pass-through amount."),
     "notes": "U10."},
    {"diagnostic_id": "D_OR20S_SELF_ASSESS_PENALTY", "severity": "warning",
     "title": "Penalty and interest are SELF-ASSESSED on lines 22-23 - and two conditions are unknowable now",
     "condition": "the return is filed or paid late",
     "message": ("Form OR-20-S requires the filer to COMPUTE AND REMIT penalty and interest on the face. "
                 "The 5% failure-to-pay exception is a FIVE-WAY CONJUNCTION and its last two conditions "
                 "- 'you pay the balance of tax due when you file' and 'you pay the interest ... within "
                 "30 days of the bill' - CANNOT BE KNOWN AT PREPARATION TIME. Enter the amounts manually "
                 "after reviewing the computed suggestion. Interest is DAILY and the rate changes at the "
                 "calendar-year boundary (9% / 0.0247% in 2025; 8% / 0.0219% in 2026), so a balance paid "
                 "late across 12/31/2025 needs a TWO-SEGMENT computation."),
     "notes": "D-12 W6. ⚠ FORM OR-65 SAYS 'Don't submit a penalty payment with the return'. Do not unify the two."},
    {"diagnostic_id": "D_OR20S_HIGH_INCOME_LOOKBACK", "severity": "warning",
     "title": "The high-income-taxpayer test is a three-year FEDERAL lookback this return cannot supply",
     "condition": "net tax is under $500 and the high-income flag is unset",
     "message": ("An S corp with no built-in gains owes exactly $150 and is below the $500 estimated-tax "
                 "threshold - but a 'high-income taxpayer' is still required to pay estimates. The "
                 "definition looks at FEDERAL taxable income before NOL and capital-loss carryovers of "
                 "$1,000,000 or more in ANY ONE of the last three years, not including the current year. "
                 "Confirm the flag from client records."),
     "notes": "D-12 W10 - persistent client state with no home on any form."},
    {"diagnostic_id": "D_OR20S_AMENDED_L19_TRAP", "severity": "warning",
     "title": "On an amended return, line 19 carries the PRIOR NET TAX, not the estimated payments",
     "condition": "the Amended box is set",
     "message": ("Verbatim: 'On the estimated tax payments line on your amended Form OR-20-S, enter the "
                 "net excise tax per the original return or as previously adjusted. Don't include any "
                 "penalty or interest portions of payments already made.' A NAIVE RE-RUN OF THE ORIGINAL "
                 "SCHEDULE ES DOUBLE-COUNTS. Also fill in ALL amounts even if unchanged, ALWAYS use the "
                 "CURRENT address (the DOR's system treats the return as an address-change instruction), "
                 "file within 90 days of the federal or other-state change, mail an audit-report "
                 "amendment separately, and DO NOT pay an amended balance by EFT."),
     "notes": "⚠ Never amend to carry an NOL back - Oregon allows corporations to carry losses forward only."},
    {"diagnostic_id": "D_OR20S_ALT_APPORT_REQUEST", "severity": "warning",
     "title": "The alternative-apportionment box denotes a REQUEST - file on standard apportionment",
     "condition": "the alternative apportionment checkbox is set",
     "message": ("'Do not complete the original or amended return using an alternative method of "
                 "apportionment unless/until that alternative method has been approved.' 'This box is to "
                 "denote requests only and isn't to be used after a request is approved.' Method 2 (a "
                 "separate petition) is the DOR's preference and it will not rule until the return is "
                 "filed on standard apportionment. Allow at least SIX MONTHS. An approval PERSISTS "
                 "across years."),
     "notes": "⚠ Form OR-65 has no such checkbox; ORS 314.667(1) is taxpayer-agnostic, so a partnership may still petition (U11)."},
    {"diagnostic_id": "D_OR20S_DUE_DATE_DERIVED", "severity": "info",
     "title": "April 15, 2026 is DERIVED from the rule - the DOR never prints it",
     "condition": "the due date is displayed",
     "message": ("ORS 314.385(1)(b): the 15th day of the month FOLLOWING the federal due date. Federal "
                 "1120-S 3/15/2026 falls on a Sunday -> 3/16/2026 -> +1 month, 15th = 4/15/2026. The "
                 "string 'April 15, 2026' appears nowhere in the OR-20-S instructions as a return due "
                 "date. The extended date derives the same way: 10/15/2026. ⚠ Oregon's corporate returns "
                 "are due ONE MONTH LATER than the federal return, which is why Form OR-65 (March 16) "
                 "and Form OR-20-S (April 15) diverge by a month."),
     "notes": "U18. Confirm before a deadline calculator ships."},
    {"diagnostic_id": "D_OR20S_NO_C_CORP_MIN_TABLE", "severity": "info",
     "title": "The twelve-tier minimum-tax table does not apply to an S corporation",
     "condition": "an Oregon-sales-tiered minimum tax is proposed for this return",
     "message": ("S corporations pay a flat $150 under ORS 317.090(2)(b). The twelve-tier table at "
                 "(2)(a) is a C-CORPORATION table and reappears only on Schedule OR-OC-2, per corporate "
                 "composite owner, keyed to THAT OWNER'S share of Oregon sales. ⚠ Relatedly, HB 2339 "
                 "(2025) lets the agricultural overtime credit offset ORS 317.090(2)(a) minimum tax - "
                 "subsection (2)(a) only, so it does NOT offset an S corporation's $150."),
     "notes": "N8 / N11."},
    {"diagnostic_id": "D_OR20S_GILTI_NO_COMPUTATION", "severity": "info",
     "title": "The GILTI checkbox carries no computation anywhere on this form",
     "condition": "the GILTI checkbox is set",
     "message": ("There is no GILTI line, no add-back, no subtraction and no Appendix A code. The "
                 "instructions say only 'If you included GILTI on your federal return, check this box.' "
                 "DO NOT INVENT A COMPUTATION. (SB 1510 (2026) replaces GILTI with NCTI under IRC 951A "
                 "for TY2026 - that changes this checkbox's meaning, not TY2025's treatment.)"),
     "notes": "N4."},
    {"diagnostic_id": "D_OR20S_EXTENSION_IS_7004", "severity": "info",
     "title": "There is no Oregon extension form - annotate a federal Form 7004",
     "condition": "the Extension checkbox is set",
     "message": ("For an Oregon extension alongside a federal one, send a COPY of the federal extension "
                 "WITH the Oregon return, after all other enclosures. For an 'Oregon only' extension, "
                 "answer question 1 on federal Form 7004, WRITE 'For Oregon Only' AT THE TOP, and "
                 "include it with the return. 'Don't send the extension until you file your Oregon "
                 "return.' The extension document is the LAST PAGE OF THE RETURN, never a separate "
                 "advance filing."),
     "notes": "Contrast Form OR-65, whose extension is self-declared on the face with no document at all."},
]

OR20S_SCENARIOS: list[dict] = [
    {"scenario_name": "OR-20-S the ordinary case - no built-in gains, excise filer", "scenario_type": "normal",
     "inputs": {"tax_basis": "excise", "built_in_gains": 0, "excess_net_passive": 0, "apportionment_pct": 37.5},
     "expected_outputs": {"L1c": 0, "L6": 37.5, "L7": 0, "L8": 0, "L10": 0, "L11": 150, "L12": 150},
     "notes": "⚠ LINE 6 IS STILL 37.5, NOT BLANK. Dropping it is the single most likely OR-20-S bug.",
     "sort_order": 1},
    {"scenario_name": "OR-20-S income-tax filer pays ZERO minimum tax", "scenario_type": "edge",
     "inputs": {"tax_basis": "income", "built_in_gains": 0, "excess_net_passive": 0},
     "expected_outputs": {"L11": 0, "L12": 0, "credit_floor": 0,
                          "authority_for_zero": "ORS 318.020(1) and ORS 318.031, NOT ORS 317.090"},
     "sort_order": 2},
    {"scenario_name": "OR-20-S built-in gains - the 6.6%/7.6% rate step", "scenario_type": "normal",
     "inputs": {"tax_basis": "excise", "oregon_taxable_income": 1_500_000},
     "expected_outputs": {"L8": 104000.0, "L11": 150, "L12": 104000.0},
     "notes": "$66,000 + 7.6% x $500,000 = $104,000. The base constant $66,000 = 6.6% x $1,000,000.",
     "sort_order": 3},
    {"scenario_name": "OR-20-S credit floor - credits cannot drop excise tax below $150", "scenario_type": "edge",
     "inputs": {"tax_basis": "excise", "L12": 150, "L13": 0, "carryforward_credits_requested": 5000},
     "expected_outputs": {"L14": 150, "L15": 0, "L16": 150, "L15_limited_by_floor": True},
     "notes": "ORS 317.090(3) - the minimum tax 'may not be reduced, paid or otherwise satisfied through the use of any tax credit.'",
     "sort_order": 4},
    {"scenario_name": "OR-20-S LIFO recapture stacks ON TOP of the $150 and evades credits", "scenario_type": "edge",
     "inputs": {"tax_basis": "excise", "L12": 150, "carryforward_credits_requested": 0, "lifo_recapture": 4000},
     "expected_outputs": {"L16": 150, "L17": 4000, "L18": 4150},
     "notes": ("Line 17 sits BELOW the line-12 comparison and BELOW the line-15 credit subtraction. It is "
               "ONE-THIRD OF THE DEFERRED TAX, not of the income, and three of the four statutory "
               "installments land here."),
     "sort_order": 5},
    {"scenario_name": "OR-20-S CODE NAMESPACE - code 158 on line 2 is a DEPRECIATION item", "scenario_type": "failure",
     "inputs": {"context": "OR20S_LINE_2", "namespace": "individual", "code": 158},
     "expected_outputs": {"raises": "OregonCodeNamespaceError",
                          "corporate_158": "Gain or loss on disposition of depreciable property",
                          "individual_158": "Interest and dividends on government bonds of other states"},
     "notes": "⚠⚠ C1. And the SAME engagement must emit INDIVIDUAL codes on the OR-K-1 overflow attachment.",
     "sort_order": 6},
    {"scenario_name": "OR-20-S income-filer-only codes 361/364 are barred on an excise return",
     "scenario_type": "edge",
     "inputs": {"tax_basis": "excise", "codes_attempted": [361, 364]},
     "expected_outputs": {"allowed_361": False, "allowed_364": False,
                          "allowed_when_income_filer": True},
     "notes": "A CHECKBOX-DRIVEN code-eligibility rule that a generic code-list seeding pass drops on the floor.",
     "sort_order": 7},
    {"scenario_name": "OR-20-S estimated tax - $150 is below $500 unless high-income", "scenario_type": "edge",
     "inputs": {"net_tax": 150, "high_income_taxpayer": False},
     "expected_outputs": {"estimated_required": False, "if_high_income": True},
     "notes": "The $500 threshold INCLUDES the minimum tax. The high-income lookback is federal, three years, and not on this return.",
     "sort_order": 8},
    {"scenario_name": "OR-20-S code 341 exists on OR-ASC-CORP but NOT in Appendix A", "scenario_type": "edge",
     "inputs": {"namespace": "corporate", "code": 341},
     "expected_outputs": {"resolves": True, "appendix_a": False, "allowed_on_or20s": False,
                          "used_by": "a CORPORATE COMPOSITE OWNER on Schedule OR-ASC-CORP Section B, per Pub. OR-OC"},
     "notes": ("⚠ THE PROOF THAT APPENDIX A IS A SUBSET. Seeding Appendix A as the whole corporate table "
               "would FAIL a legitimate corporate composite subtraction."),
     "sort_order": 9},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM OR_21 -- FACTS. ⚠ EVERY LINE-BEARING FACT CARRIES THE PROVENANCE STAMP:
# there is no published Form OR-21 face, so the campaign's 'printed face governs'
# convention (D-12 W2) HAS NO SUBJECT on this form.
# ═══════════════════════════════════════════════════════════════════════════
OR21_FACTS: list[dict] = [
    {"fact_key": "or21_box1_election", "label": "Box 1. Election", "data_type": "boolean", "required": True,
     "sort_order": 1,
     "notes": ("THE ELECTING INSTRUMENT. It carries a PERJURY ATTESTATION that is a real UI requirement, "
               "not boilerplate: 'By checking this box and submitting the completed return, you are "
               "stating under penalty of false swearing that all members of the PTE have agreed to the "
               "election or you are stating under penalty of perjury that you are an officer, manager, "
               "or member of the PTE who is authorized under law or the PTE's organizational documents "
               "to make the election on the PTE's behalf.'")},
    {"fact_key": "or21_box2_revocation", "label": "Box 2. Revocation", "data_type": "boolean", "sort_order": 2,
     "notes": ("⚠ A REVOCATION IS A FILED FORM OR-21 WITH A ZEROED BODY: 'complete this form as if you "
               "are making the election, except enter 0 for all numeric fields on lines 6 through 23.' A "
               "distinct document state the app must be able to emit. ⚠ U22: the statute allows "
               "revocation only 'on or before the due date' with NO extension language while the DOR "
               "instructions add 'including extension'. BUILD TO THE INSTRUCTIONS AND DIAGNOSE - an "
               "invalid revocation leaves an election IN FORCE, which changes the tax.")},
    {"fact_key": "or21_box3_amended", "label": "Box 3. Amended", "data_type": "boolean", "sort_order": 3,
     "notes": ("'Check this box if the PTE is amending an earlier return to make corrections (not "
               "revoking a prior election).' Requires an amended Schedule OR-21-K-1 to EVERY member. ⚠ "
               "'Member listed by mistake ... list the member on the amended schedule as well, but enter "
               "zeroes for all of that member's amounts' - A ZEROED GHOST MEMBER ROW that must PERSIST "
               "rather than be deleted.")},
    {"fact_key": "or21_box4_extension", "label": "Box 4. Extension", "data_type": "boolean", "sort_order": 4,
     "notes": "⚠ THE EXTENDED DUE DATE IS NEVER STATED (U7). Payment is due 4/15/2026 regardless."},
    {"fact_key": "or21_box5_pass_through", "label": "Box 5. Pass through (upper-tier member of an electing lower-tier entity)",
     "data_type": "boolean", "sort_order": 5,
     "notes": ("⚠⚠ 'If the PTE is not making its own election to pay PTE-E tax, do not check any other "
               "boxes.' A NON-ELECTING UPPER-TIER PTE MUST STILL FILE A PARTIAL FORM OR-21 - Parts A, B "
               "(box 5 only) and F, with 0 on lines 6 through 33, plus Schedule OR-21-MD-PT plus an "
               "OR-21-K-1 to every member. A THIRD document state that is easy to miss entirely.")},
    {"fact_key": "or21_module", "label": "Attached federal return (1065 or 1120-S)", "data_type": "choice",
     "choices": ["1065", "1120S"], "required": True, "sort_order": 6,
     "notes": "⚠ THE ONLY FORK IN THE OR-21 BASE is line 9 (guaranteed payments), which is 0 for an S corporation."},
    {"fact_key": "or21_tax_year_begin", "label": "Tax year beginning date", "data_type": "date", "required": True,
     "sort_order": 7,
     "notes": ("⚠⚠ FORM OR-21 IS CALENDAR-YEAR ONLY. 'Enter 01/01/2025 and 12/31/2025 ... If the PTE's "
               "tax year ends in 2026, make the election on the 2026 Form OR-21.' A fiscal-year PTE "
               "makes the election for the calendar year in which its fiscal year ENDS, so THE SAME "
               "CLIENT CAN HAVE A FISCAL-YEAR OR-65 AND A CALENDAR-YEAR OR-21 FOR OVERLAPPING PERIODS. "
               "A genuine structural divergence from OR-65 and OR-20-S, both of which accept fiscal years.")},
    {"fact_key": "or21_l6_ordinary_business_income", "label": "6. Ordinary business income or (loss)",
     "data_type": "decimal", "sort_order": 10,
     "notes": "Federal Schedule K line 1 on BOTH the 1065 and the 1120-S. " + "⚠ Worksheet-sourced line number (U1)."},
    {"fact_key": "or21_l7_net_rental_real_estate", "label": "7. Net rental real estate income or (loss)",
     "data_type": "decimal", "sort_order": 11, "notes": "Schedule K line 2 on both."},
    {"fact_key": "or21_l8_other_net_rental", "label": "8. Other net rental income or (loss)",
     "data_type": "decimal", "sort_order": 12, "notes": "Schedule K line 3c on both."},
    {"fact_key": "or21_l9_guaranteed_payments", "label": "9. Guaranteed payments to partners",
     "data_type": "decimal", "sort_order": 13,
     "notes": ("⚠ THE ONLY MODULE FORK IN THE BASE. 'If the PTE is a partnership, enter the total "
               "guaranteed payments from federal Schedule K, line 4c; OTHERWISE, ENTER 0.'")},
    {"fact_key": "or21_l10_interest", "label": "10. Interest", "data_type": "decimal", "sort_order": 14,
     "notes": "⚠ FORKS: 1065 Schedule K line 5; 1120-S Schedule K line 4."},
    {"fact_key": "or21_l11_ordinary_dividends", "label": "11. Ordinary dividends", "data_type": "decimal",
     "sort_order": 15, "notes": "⚠ FORKS: 1065 line 6a; 1120-S line 5a."},
    {"fact_key": "or21_l12_royalties", "label": "12. Royalties", "data_type": "decimal", "sort_order": 16,
     "notes": "⚠ FORKS: 1065 line 7; 1120-S line 6."},
    {"fact_key": "or21_l13_net_capital_gain", "label": "13. Net capital gain or (loss)", "data_type": "decimal",
     "sort_order": 17,
     "notes": ("⚠ THE ONLY COMPOSED LINE: 1065 lines 8 + 9a; 1120-S lines 7 + 8a. It DELIBERATELY "
               "EXCLUDES 1065 lines 9b/9c and 1120-S lines 8b/8c (collectibles 28% gain and unrecaptured "
               "1250 gain), which are CHARACTERISATION SUB-LINES of 9a/8a and would DOUBLE-COUNT. ⚠ "
               "Schedule OR-K-1 keeps short-term and long-term SEPARATE at its lines 8 and 9 - three "
               "different orderings of the same federal data across three Oregon artifacts.")},
    {"fact_key": "or21_l14_section_1231", "label": "14. Net IRC section 1231 gain or (loss)",
     "data_type": "decimal", "sort_order": 18, "notes": "⚠ FORKS: 1065 line 10; 1120-S line 9."},
    {"fact_key": "or21_l15_other_income", "label": "15. Other income or (loss)", "data_type": "decimal",
     "sort_order": 19, "notes": "⚠ FORKS: 1065 line 11; 1120-S line 10."},
    {"fact_key": "or21_l17_non_apportionable", "label": "17. Non-apportionable income", "data_type": "decimal",
     "sort_order": 20,
     "notes": ("'Non-apportionable income means all income other than apportionable income (ORS "
               "314.610).' ⚠⚠ THIS is the line that line 21 draws from - NOT line 19, whatever the DOR "
               "instruction says twice.")},
    {"fact_key": "or21_l19_apportionment_pct", "label": "19. Apportionment percentage from Schedule OR-21-AP, line 12",
     "data_type": "decimal", "default_value": "100.0000", "sort_order": 21,
     "validation_rule": "four decimal places; 100.0000 if not apportioning",
     "notes": ("⚠ A FOUR-DECIMAL PERCENTAGE, which is why the DOR's 'enter the amount from line 19' at "
               "line 21 cannot be right. ⚠ Schedule OR-21-AP is SALES-FACTOR-ONLY - no property factor, "
               "no payroll factor, no double-weighted alternative - even though this line's instruction "
               "routes financial institutions and public utilities to ORS 314.280 (U13).")},
    {"fact_key": "or21_l21_oregon_allocated", "label": "21. Oregon allocated income", "data_type": "decimal",
     "sort_order": 22,
     "notes": ("⚠⚠ BUILD FROM LINE 17. The DOR instruction says 'enter the amount from line 19' TWICE in "
               "one paragraph and both are wrong; line 19 is a percentage and this is a dollar field "
               "feeding line 22. The paragraph's own opening sentence says 'from line 17'. A "
               "wholly-in-Oregon PTE has L19 = 100.0000, L20 = L18 and L21 = L17, giving L22 = L16 - the "
               "only arithmetic that closes. OR-DEF-5 / U2.")},
    {"fact_key": "or21_l24_payments", "label": "24. Total PTE-E tax payments made prior to April 15, 2026",
     "data_type": "decimal", "sort_order": 23,
     "notes": ("⚠ THE CUT-OFF IS THE **ORIGINAL** DUE DATE, NOT THE EXTENDED ONE. A payment made on the "
               "extended filing date lands in penalty/interest, not on line 24 - the DOR's Example 3 "
               "confirms it (a July 29 payment drives the 5% penalty).")},
    {"fact_key": "or21_l27_penalty_interest", "label": "27. Penalty and interest for paying late",
     "data_type": "decimal", "sort_order": 24,
     "notes": ("5% failure-to-pay + daily interest; ROUND THE TOTAL TO THE NEAREST $1 AFTER SUMMING, not "
               "component-wise. ⚠ NO 20% failure-to-file penalty and NO 100% three-year penalty on this "
               "form - a THIRD Oregon penalty posture.")},
    {"fact_key": "or21_l32_apply_to_next_year", "label": "32. Amount of line 31 applied to 2026 estimated PTE-E tax",
     "data_type": "decimal", "sort_order": 25,
     "notes": ("⚠ APPLYING AN OVERPAYMENT FORWARD IS A BET ON NEXT YEAR'S ELECTION, because the election "
               "is ANNUAL. 'If the PTE does not elect to pay PTE-E tax next year, you will need to "
               "request a refund on Revenue Online of the amount you're applying as an estimated payment.'")},
    {"fact_key": "or21_prior_year_tax_l23", "label": "2024 Form OR-21 line 23 (for the estimated-tax safe harbour)",
     "data_type": "decimal", "sort_order": 26,
     "notes": "⚠ THE SAFE HARBOUR REQUIRES THE PTE TO HAVE MADE THE ELECTION FOR 2024 - not merely to have filed."},
    {"fact_key": "or21_md_member_shares", "label": "Schedule OR-21-MD column r - each member's share of distributive proceeds",
     "data_type": "decimal", "sort_order": 30,
     "notes": ("Sourced from the entity's Form OR-65 or Form OR-20-S; for individual members it is "
               "reported on Schedule OR-K-1 Part III lines 1-11, OREGON COLUMN. ⚠ THE ONLY DOCUMENTED "
               "LINKAGE FROM THE ENTITY MODULE TO THE PTE-E MODULE, and it is a REPORTING linkage, not a "
               "computational one - line 22's total comes from the OR-21 lines 6-22 chain, never from "
               "summing column r. ⚠ Ownership percentage is taken AS OF THE CLOSE OF THE TAX YEAR, or "
               "BEFORE A MID-YEAR DISPOSITION if the member disposed of all or part of an interest.")},
    {"fact_key": "or21_md_total_addition", "label": "The total state-tax deduction taken on the entity's federal return",
     "data_type": "decimal", "sort_order": 31,
     "notes": "OR-21-MD Part B line 4 must equal this exactly, on pain of 'the schedule is not complete'."},
    {"fact_key": "or21_upper_tier_lower_entities", "label": "Electing lower-tier entities of which this PTE is a member",
     "data_type": "string", "sort_order": 32,
     "notes": "⚠ A SEPARATE Schedule OR-21-MD-PT for EACH electing lower-tier entity."},
]

OR21_RULES: list[dict] = [
    {"rule_id": "R-OR21-PROVENANCE", "title": "⚠ NO PUBLISHED FORM FACE - every line number is worksheet-sourced",
     "rule_type": "classification", "sort_order": 1, "inputs": [], "outputs": ["line_number_provenance"],
     "formula": "all OR-21 / OR-21-MD / OR-21-AP / OR-21-MD-PT line numbers come from 'do not file' worksheets",
     "description": ("The Oregon DOR HAS NEVER PUBLISHED A FORM OR-21 FACE, IN ANY YEAR. Established by "
                     "ENUMERATION, not by a failed URL guess: the DOR FormsPubs SharePoint list was "
                     "queried in full (1,712 items, __next = null, every year 2017-2026 plus 'General') "
                     "and 150-107-114 (Form OR-21), -112 (OR-21-MD), -111 (OR-21-AP) and -110 "
                     "(OR-21-MD-PT) appear ZERO TIMES IN ANY YEAR, only their `-1` instruction rows - "
                     "while 150-107-113 (Schedule OR-21-K-1) appears as a real face in 2022, 2023, 2024 "
                     "AND 2025, which proves the query is not blind to PTE-E artifacts. Corroborated "
                     "mechanically: AcroForm widget counts are 0/0/0/0 across the four instruction PDFs "
                     "versus 23 on the OR-21-K-1 face. Ten targeted URL probes returned 404 against "
                     "three 200-OK positive controls."),
     "exceptions": ("⚠⚠ THE COROLLARY TO D-12 W2. The campaign's 'the printed face governs; instruction "
                    "conflicts are logged' convention CANNOT APPLY TO THIS FORM, because there is no "
                    "face to govern. That is precisely why U1/U19/U23 - the DOR developers' handbook - "
                    "is the highest-value unlock in the Oregon wave, and it is a Ken-only action that "
                    "has been DECIDED (D-12 A5) BUT NOT SENT."),
     "notes": "Whether the worksheet line numbers are the MeF schema's line numbers is an INFERENCE (U1)."},
    {"rule_id": "R-OR21-SEPARATE", "title": "Form OR-21 takes ZERO inputs from Form OR-65 or Form OR-20-S",
     "rule_type": "classification", "sort_order": 2, "inputs": [], "outputs": [],
     "formula": "the entire base (lines 6-15) is federal Schedule K; line 19 pulls Schedule OR-21-AP",
     "description": ("Instr. p. 3: 'The amounts on lines 6 through 15 can generally be found on Schedule K "
                     "of federal Form 1065 or 1120-S.' VERIFIED WITH ZERO EXCEPTIONS by two independent "
                     "workstreams: the strings 'OR-65' and 'OR-20-S' DO NOT OCCUR ANYWHERE in "
                     "150-107-114-1. This is the strongest argument for OR_21 as its own RS spec, and it "
                     "is what campaign D-12 ruled."),
     "notes": ("The ONE linkage that does exist runs the other way and is a REPORTING linkage: Schedule "
               "OR-21-MD column r sources each member's share from the entity's return / Schedule OR-K-1 "
               "Part III lines 1-11 Oregon column.")},
    {"rule_id": "R-OR21-BASE", "title": "Part C lines 6-22 - the base, module-aware at line 9",
     "rule_type": "calculation", "sort_order": 3,
     "inputs": ["or21_module", "or21_l17_non_apportionable", "or21_l19_apportionment_pct"],
     "outputs": ["OR21_L16", "OR21_L18", "OR21_L20", "OR21_L21", "OR21_L22"],
     "formula": "L16 = sum(L6..L15); L18 = L16 - L17; L20 = L18 x L19; L21 = L17 (see R-OR21-L21); L22 = L20 + L21",
     "description": ("✅ EVERY FEDERAL REFERENCE VERIFIED POSITIONALLY against the FINAL 2025 IRS forms by "
                     "TWO independent workstreams, 0 errors across 20 references. ⚠ THE BASE IS GROSS OF "
                     "EVERY SEPARATELY-STATED DEDUCTION - Pub. OR-21-EST p. 1: 'Separately stated "
                     "deductions, such as the expense deduction allowed under Section 179 ... or the IRC "
                     "Section 170 deduction for charitable contributions are not included.' No 179 line, "
                     "no charitable line, no 199A line, no state-tax line."),
     "exceptions": ("Line 13 is the only COMPOSED line and it EXCLUDES the characterisation sub-lines "
                    "(1065 9b/9c, 1120-S 8b/8c) that would double-count. Line 9 is 0 for an S corporation."),
     "notes": "Statutory definition, 2021 Or. Laws ch. 589 sec. 2(1): net income, dividends, royalties, interest, rents, guaranteed payments and gains, connected with sources within this state."},
    {"rule_id": "R-OR21-L21", "title": "Line 21 draws from LINE 17 - the DOR instruction is wrong TWICE",
     "rule_type": "calculation", "sort_order": 4, "inputs": ["or21_l17_non_apportionable"], "outputs": ["OR21_L21"],
     "formula": "L21 = the portion of L17 allocated to Oregon; for a wholly-in-Oregon PTE, L21 = L17",
     "description": ("OR-DEF-5 / U2. The instruction reads 'Enter the total of the non-apportionable "
                     "income from line 17 that is allocated to Oregon. If the PTE does all of its "
                     "business activity in Oregon, enter the amount from line 19. If the PTE must "
                     "apportion its income, see \"Allocable income\" ... to determine whether the amount "
                     "on line 19 includes income that is allocated to Oregon.' BOTH 'line 19' references "
                     "are wrong. Line 19 is a FOUR-DECIMAL PERCENTAGE; line 21 is a dollar field feeding "
                     "'line 22 = line 20 plus line 21'. Following the DOR's literal text would ADD A "
                     "PERCENTAGE TO AN INCOME FIGURE. Only line 17 closes: a wholly-in-Oregon PTE has "
                     "L19 = 100.0000, L20 = L18, L21 = L17 and therefore L22 = L18 + L17 = L16."),
     "notes": ("Two occurrences of the same wrong pointer in one paragraph, with the CORRECT pointer in "
               "the paragraph's opening sentence, is the signature of a STALE RENUMBERING - which RAISES "
               "confidence in the correction, not lowers it. DO NOT SEED THE DOR'S LITERAL TEXT.")},
    {"rule_id": "R-OR21-RATE", "title": "Line 23 - 9% / 9.9% with a $250,000 breakpoint",
     "rule_type": "calculation", "sort_order": 5, "inputs": ["OR21_L22"], "outputs": ["OR21_L23"],
     "formula": "L23 = min(L22, 250000) x 0.09 + max(0, L22 - 250000) x 0.099",
     "description": ("2021 Or. Laws ch. 589 sec. 3(6): 'Nine percent of the first $250,000, OR FRACTION "
                     "THEREOF, of the sum of distributive proceeds; and Nine and nine-tenths percent of "
                     "any amount of distributive proceeds in excess of $250,000.' ⚠ THE 9% FIRST TIER IS "
                     "BELOW OREGON'S 9.9% INDIVIDUAL TOP RATE - a genuine rate BENEFIT, not a rate-match "
                     "PTET, so the PTE-E can be advantageous even ignoring the federal SALT-cap "
                     "workaround. Arithmetically CONTINUOUS at the breakpoint: both branches give "
                     "$22,500 at exactly $250,000."),
     "exceptions": ("The DOR's six-step worksheet is seeded alongside for AUDITABILITY. Its line e is a "
                    "BRANCH, not a formula, and $22,500 is a HARD-CODED SHORTCUT CONSTANT (= 9% x "
                    "$250,000). Both DOR worked examples must reproduce exactly: $425,000 -> $39,825 and "
                    "$180,000 -> $16,200.")},
    {"rule_id": "R-OR21-STOP", "title": "Line 22 <= 0 => DO NOT FILE. A client instruction, not a return.",
     "rule_type": "routing", "sort_order": 6, "inputs": ["OR21_L22"], "outputs": ["do_not_file"],
     "formula": "if L22 <= 0: STOP - request a refund of all estimated PTE-E payments through Revenue Online",
     "description": ("Verbatim: 'If line 22 is zero or a loss (negative number), STOP. Do not file Form "
                     "OR-21. Instead, go to the PTE's account on Revenue Online and request a refund of "
                     "all estimated PTE-E tax payments made for this tax year.' There is a PARALLEL path "
                     "with the same shape - 'Request for refund without election ... Do not file Form "
                     "OR-21' - when estimates were paid but no election will be made. Delvio must reach "
                     "the state 'PTE-E estimates were paid but no OR-21 will be filed' and produce the "
                     "right client instruction rather than a return."),
     "notes": "Form OR-21-REF is referenced once ('Contact us to request Form OR-21-REF if you do not have access to the internet') and is NOT in the DOR's published forms list (U8)."},
    {"rule_id": "R-OR21-ELECTION", "title": "The election is ANNUAL and REVOCABLE - NOT binding on future years",
     "rule_type": "classification", "sort_order": 7, "inputs": ["or21_box1_election", "or21_box2_revocation"],
     "outputs": ["election_state"],
     "formula": "annual; revocable by all current members on or before the due date; NEVER retroactive",
     "description": ("2021 Or. Laws ch. 589 sec. 3(2), verbatim and vintage-checked for TY2025. ⚠ THIS "
                     "WAS THE MISSISSIPPI QUESTION IN WAVE 3 AND OREGON ANSWERS IT THE OPPOSITE WAY - do "
                     "NOT carry the Mississippi 'binding on future years' assumption over. ⚠ ELIGIBILITY: "
                     "'All of the PTE's members must be individuals or other PTEs (upper-tier PTEs) "
                     "whose members are all individuals' - A SINGLE CORPORATE, TRUST OR ESTATE MEMBER "
                     "DISQUALIFIES THE ENTITY. Grantor trusts and single-member LLCs are LOOK-THROUGH "
                     "and do NOT disqualify. ⚠ REGISTRATION IS NOT THE SAME AS MAKING THE ELECTION - a "
                     "PTE must register on Revenue Online before making estimated payments, and both DOR "
                     "sources say so explicitly."),
     "exceptions": ("⚠ U22: the statute allows revocation only 'on or before the due date' with NO "
                    "extension language, in pointed contrast to the ELECTION sentence in the SAME "
                    "subsection ('including extensions'). The DOR instructions add 'including extension' "
                    "anyway. BUILD TO THE INSTRUCTIONS AND DIAGNOSE. ⚠ CONTINGENT SUNSET: ch. 589 "
                    "secs. 11-13 repeal the PTE-E on the date IRC 164(b)(6) is repealed - OBBBA RAISED "
                    "the SALT cap rather than repealing it, so it is in force for TY2025.")},
    {"rule_id": "R-OR21-CALYEAR", "title": "Form OR-21 is CALENDAR-YEAR ONLY",
     "rule_type": "validation", "sort_order": 8, "inputs": ["or21_tax_year_begin"], "outputs": [],
     "formula": "a fiscal-year PTE elects for the calendar year in which its fiscal year ENDS",
     "description": ("'Form OR-21 is filed on a calendar-year basis and is only available for tax years "
                     "beginning on or after January 1, 2022 and before January 1, 2028. PTEs using a "
                     "fiscal year will make the election for the calendar year in which their fiscal "
                     "year ends. PTEs must wait until the 2026 form is available to make the election "
                     "for a fiscal year beginning in 2025 and ending in 2026.' ⚠ THE SAME CLIENT CAN "
                     "HAVE A FISCAL-YEAR OR-65 AND A CALENDAR-YEAR OR-21 FOR OVERLAPPING PERIODS."),
     "notes": ("⚠ VINTAGE NOTE, THE REVERSE OF THE USUAL TRAP: the ORS 2025 Edition note at ch. 589 "
               "sec. 10 still shows the PRE-SB-1510 window ('before January 1, 2026') while the DOR's "
               "Rev. 04-01-26 instructions show 'before January 1, 2028'. TY2025 falls inside BOTH, so "
               "there is no TY2025 conflict - recorded so a later pass does not read the stale statute "
               "note and wrongly conclude the PTE-E expired.")},
    {"rule_id": "R-OR21-OWNER-LEGS", "title": "THREE owner-side legs: addition 167, refundable credit 900, subtraction 387",
     "rule_type": "routing", "sort_order": 9, "inputs": ["OR21_L23"], "outputs": ["OR21K1_L2", "OR21K1_L3"],
     "formula": "OR-21-K-1 line 2 -> Schedule OR-ASC Sec. A / OR-ASC-NP Sec. B code 167; line 3 -> Sec. F / Sec. I code 900; a LATER year -> code 387",
     "description": ("⚠⚠ THE OWNER-SIDE TREATMENT IS CREDIT **AND** ADD-BACK, BOTH, and the exact "
                     "destinations are published. 'The credit is refundable, so any portion that is more "
                     "than your Oregon tax liability can be claimed this year and may be refunded to "
                     "you.' Corroborated by ORS 316.502(3)(b), which lists ch. 589 sec. 3 among the "
                     "provisions authorising 'refund payments in excess of tax liability'. ⚠⚠ CODE 900 "
                     "IS NOT PRORATED FOR NONRESIDENTS OR PART-YEAR RESIDENTS: Pub. OR-CODES marks "
                     "895/896/897/898/901 'PR' and marks 900 plain 'X' on OR-40, OR-40-N AND OR-40-P. A "
                     "NONRESIDENT MEMBER GETS THE FULL CREDIT, and applying the generic nonresident "
                     "proration UNDERSTATES EVERY NONRESIDENT MEMBER'S REFUND."),
     "exceptions": ("⚠ Line 1 (distributive proceeds) is FOR INFORMATION ONLY - 'It is not reported on "
                    "your federal or Oregon personal income tax return.' ⚠ A FOURTH, easily-missed "
                    "interaction: ch. 589 sec. 3(3)(b) lets the code-167 add-back itself qualify as "
                    "QUALIFYING INCOME for Oregon's QBI reduced rate under ORS 316.043, 'in a proportion "
                    "determined by the department by rule' - and that OAR is UNLOCATED (U14). Neither "
                    "the OR-21-K-1 instructions nor Pub. OR-CODES mentions it."),
     "notes": "⚠ NO CORPORATE ANALOGUE to code 900 - the PTE-E credit reaches INDIVIDUAL members only (N10)."},
    {"rule_id": "R-OR21-MD-TIEOUT", "title": "⚠⚠ U5: the OR-21-MD allocation CANNOT tie out with a NEGATIVE member share",
     "rule_type": "validation", "sort_order": 10,
     "inputs": ["or21_md_member_shares", "or21_md_total_addition", "OR21_L23", "OR21_L22"],
     "outputs": ["md_line_4", "md_line_5", "tie_out_possible"],
     "formula": "line 4 = A x sum(positive r) / L22 and line 5 = T x sum(positive r) / L22; BOTH tie out IFF sum(positive r) == L22",
     "description": ("PROVEN, NOT SUSPECTED. The rule as written allocates 'for each member with a "
                     "POSITIVE share of distributive proceeds ... divide the member's share by the total "
                     "distributive proceeds FROM FORM OR-21, LINE 22', and Part B lines 4 and 5 must "
                     "equal the total addition and line 23 EXACTLY, on pain of 'the schedule is not "
                     "complete'. Line 22 is built entirely from entity-level federal Schedule K "
                     "aggregates (lines 6-22) with NO positive-share filter, so it cannot equal "
                     "sum(positive r) except by coincidence. WORKED COUNTEREXAMPLE: members at "
                     "+$100,000 / +$100,000 / -$50,000 give L22 = $150,000 and L23 = $13,500, but lines "
                     "4 and 5 each total $18,000 - 33.3% OVER, i.e. $18,000 OF REFUNDABLE MEMBER CREDIT "
                     "AGAINST $13,500 OF ENTITY TAX. ⚠ REFINEMENT: a ZERO share is HARMLESS; ONLY A "
                     "NEGATIVE SHARE BREAKS IT. All six PTE-E documents and ch. 589 were swept: NO "
                     "ESCAPE HATCH EXISTS - the 'enter zeroes' rule is scoped to the amended-return "
                     "'member listed by mistake' case only, and sec. 3(5) STRENGTHENS the contradiction."),
     "exceptions": ("⚠⚠ THE PROPOSED FIX IS NOT DOR GUIDANCE. Using sum(positive shares) as the "
                    "denominator reasons from the MANDATORY TIE-OUT CAUTION, not from any cited rule, "
                    "and MUST NOT be presented as a verified DOR position. `or21_md_allocation()` "
                    "therefore returns BOTH readings and labels NEITHER as authority. RED-DEFER: "
                    "D_OR21_R15_MD_DENOMINATOR. Settle by an OAR under ch. 589 sec. 5(3), DOR guidance, "
                    "or the MeF validation rules."),
     "notes": ("⚠ 'Line 3 is untied' is an INFERENCE, not a textual fact - the Caution's wording is "
               "generic and does not textually exclude line 3. Note the direction of the risk: IF line 3 "
               "= line 22 IS required, this contradiction gets SHARPER, not weaker.")},
    {"rule_id": "R-OR21-UPPER", "title": "A NON-ELECTING upper-tier PTE must still file a partial Form OR-21",
     "rule_type": "routing", "sort_order": 11, "inputs": ["or21_box5_pass_through"], "outputs": ["document_state"],
     "formula": "Parts A, B (box 5 only) and F, with 0 on lines 6-33, + Schedule OR-21-MD-PT + an OR-21-K-1 to every member",
     "description": ("Verbatim: 'Important: If you are an upper-tier PTE that is a member of an electing "
                     "lower-tier PTE and you are not making the election to pay PTE-E tax, enter 0 on "
                     "lines 6 through 33, then go to Part F.' and 'The upper-tier PTE must provide "
                     "Schedule OR-21-K-1 to each of its individual members ... EVEN IF THE UPPER-TIER PTE "
                     "ISN'T MAKING THE ELECTION.' ⚠ 'The addition and credit reported to the upper-tier "
                     "PTE by the electing lower-tier entity CAN'T BE CLAIMED ON AN ENTITY-LEVEL RETURN "
                     "and must be passed through to the upper-tier PTE's members.' ⚠ A SEPARATE Schedule "
                     "OR-21-MD-PT FOR EACH electing lower-tier entity. An ELECTING upper-tier PTE "
                     "completes ALL parts plus BOTH Schedule OR-21-MD and Schedule OR-21-MD-PT."),
     "notes": "A THIRD distinct document state alongside 'electing' and 'revoking', and it is easy to miss entirely."},
    {"rule_id": "R-OR21-EST", "title": "Estimated tax: $1,000 threshold, 90% current / 100% prior (election required)",
     "rule_type": "calculation", "sort_order": 12, "inputs": ["OR21_L23", "or21_prior_year_tax_l23"],
     "outputs": ["required_annual_payment", "regular_installment"],
     "formula": "required = min(90% of current L23, 100% of prior L23 if the 2024 election was made); installment = required / 4",
     "description": ("'The PTE must make estimated tax payments if the PTE expects to owe tax of $1,000 "
                     "or more.' 'To avoid underpayment interest, total estimated tax payments must equal "
                     "at least 90 percent of the PTE-E tax shown on the 2025 Form OR-21 or 100 percent "
                     "of the PTE-E tax shown on the 2024 Form OR-21 (if the election was made for "
                     "calendar year 2024), WHICHEVER IS LESS.' ⚠ 'To use safe harbor for 2025, the PTE "
                     "MUST HAVE MADE THE ELECTION FOR 2024' - filing alone is not enough. ⚠ "
                     "'Underpayment interest may be charged EVEN IF THE RETURN SHOWS AN OVERPAYMENT if "
                     "estimated payments were late or too small.' TY2025 installments: April 15, JUNE 16 "
                     "(June 15 was a Sunday), September 15, JANUARY 15, 2026. FISCAL-YEAR FILERS STILL "
                     "USE THE CALENDAR-YEAR PAYMENT DATES."),
     "exceptions": ("⚠ THREE DIFFERENT QUARTERLY CALENDARS: OR-21 ends JAN 15 (the individual date), "
                    "OR-20-S ends DEC 15 (the corporate date), and Form OR-65 has none. ⚠ Pub. OR-21-EST "
                    "puts the $1,000 test at ITS worksheet line 2 and the Form OR-21 instructions put it "
                    "at line 1 - same substance, different numbering; PREFER THE FORM OR-21 INSTRUCTIONS "
                    "(U6). Annualized option: period ends 3/31, 5/31, 8/31, 12/31 with multipliers "
                    "4 / 2.4 / 1.5 / 1 and cumulative percentages 22.5% / 45% / 67.5% / 90%; box 1D must "
                    "tie to line 22.")},
    {"rule_id": "R-OR21-UND-INT", "title": "Underpayment interest is an EVENT-DRIVEN RUNNING BALANCE, not a per-quarter percentage",
     "rule_type": "calculation", "sort_order": 13, "inputs": [], "outputs": ["OR21_L28"],
     "formula": "13 event rows; daily rate 0.000247 through 2025 and 0.000219 from 01/01/2026; 01/01/2026 is a RATE CHANGE EVENT",
     "description": ("⚠ THE RATE CHANGE ON 1/1/2026 IS A FIRST-CLASS EVENT LINE ON THE DOR'S OWN "
                     "WORKSHEET, which is the evidence that Oregon expects SEGMENTED daily interest "
                     "rather than a blended annual rate. ⚠ DAY-COUNT RULE, verbatim: 'Count the number "
                     "of days after the first event that creates a positive running balance until the "
                     "next event that changes the running balance, INCLUDING THE DAY OF THE NEXT EVENT "
                     "(EXCEPT JANUARY 1 WHEN THERE HAS BEEN A CHANGE IN THE INTEREST RATE; INCLUDE "
                     "JANUARY 1 IN THE DAY COUNT FOR A SUBSEQUENT EVENT) ... Don't count any days when "
                     "the running balance is negative or zero.' THE JANUARY-1 PARENTHETICAL IS A GENUINE "
                     "OFF-BY-ONE RULE AND IT IS EASY TO MISS."),
     "notes": ("⚠ NOTATION TRAP: the OR-21 worksheet prints the daily rates as DECIMALS (0.000247, "
               "0.000219) while the OR-20-S table prints them as PERCENTS (0.0247%, 0.0219%). Same "
               "numbers, two notations, same season, same agency. ⚠ Only TWO payment slots per period "
               "(one for periods 3 and 4a) - the worksheet caps at 13 event rows. Since it is not filed, "
               "that is a Delvio modelling choice.")},
    {"rule_id": "R-OR21-PENALTY", "title": "A THIRD penalty posture: 5% + interest only",
     "rule_type": "calculation", "sort_order": 14, "inputs": ["or21_l27_penalty_interest"], "outputs": ["OR21_L27"],
     "formula": "5% of the unpaid tax + daily interest; ROUND THE TOTAL to the nearest $1 after summing",
     "description": ("⚠ THERE IS NO 20% FAILURE-TO-FILE PENALTY AND NO 100% THREE-YEAR PENALTY ON FORM "
                     "OR-21, unlike Form OR-20-S - and Form OR-65 does not self-assess at all. THREE "
                     "SEPARATE PENALTY MODELS. The DOR's Example 3 pins the day-count convention: "
                     "$4,825 unpaid, April 16 to July 29, 2026 = 105 DAYS at 0.0219%, giving $241.25 "
                     "penalty + $110.95 interest = $352.20, ENTERED AS $352. ⚠ Additional interest of 4% "
                     "per year applies to deficiencies unpaid more than 60 days after assessment."),
     "notes": "Payment is due April 15, 2026 WITHOUT REGARD to any extension to file."},
    {"rule_id": "R-OR21-K1-SUPPRESS", "title": "An electing PTE issues TWO Oregon K-1s and suppresses PTE-E items on OR-K-1",
     "rule_type": "routing", "sort_order": 15, "inputs": ["or21_box1_election"], "outputs": ["or_k1_suppression"],
     "formula": "OR-K-1 lines 14-18 exclude the PTE-E addition and line 19 excludes the PTE-E credit whenever the election is made",
     "description": ("SUPPRESSION LOGIC, NOT JUST POPULATION LOGIC. 'Don't include the PTE-E addition if "
                     "the PTE made the election to pay PTE-E tax' and 'Don't include the PTE-E tax "
                     "credit if the PTE elected to pay the PTE-E tax.' Both instruction sets state that "
                     "neither schedule substitutes for the other, so AN ELECTING PTE ISSUES TWO OREGON "
                     "K-1s PER OWNER - and NEITHER IS FILED WITH ANY RETURN; both are furnished to the "
                     "owner and kept with records. Counting the federal K-1 and any composite reporting, "
                     "that is FOUR DISTINCT DOCUMENTS PER OWNER."),
     "exceptions": ("⚠ U17 - A GENUINE CIRCULAR REFERENCE. OR-K-1 says 'complete Form OR-21 and "
                    "associated schedules FIRST'; OR-21-MD says 'Complete Form OR-21 before completing "
                    "this schedule'; and OR-21-MD column r sources member shares from 'Schedule OR-K-1, "
                    "Part III, lines 1 through 11, Oregon column'. Practical resolution: the OR-K-1 "
                    "INCOME lines are computable before the PTE-E items exist, and only the PTE-E "
                    "addition/credit SUPPRESSION depends on OR-21 - BUT THE DOR NEVER SAYS SO."),
     "notes": "Engagement order: OR-65/OR-20-S -> OR-21 (+MD/AP/MD-PT) -> OR-21-K-1 -> OR-K-1 (suppressed) -> OR-19/OR-OC."},
    {"rule_id": "R-OR21-DUEDATE", "title": "Due April 15, 2026 by a chain, not by an ORS ch. 316 due-date section",
     "rule_type": "calculation", "sort_order": 16, "inputs": ["or21_box4_extension"], "outputs": ["due_date"],
     "formula": "2021 Or. Laws ch. 589 sec. 3(8) -> ORS 314.385(1)(a) -> IRC 6072(a); extended UNRESOLVED, default Sept 15",
     "description": ("⚠ THERE IS NO ORS CHAPTER 316 DUE-DATE SECTION AT ALL (ORS 316.457 is 'Department "
                     "may require...'). April 15 arrives ONLY via that chain. ⚠⚠ THE EXTENDED DATE IS "
                     "NEVER STATED (U7). 'Oregon will honor the same extension request' as the federal "
                     "1065/1120-S extension, which runs to SEPTEMBER 15, 2026 - but six months from "
                     "Oregon's own April 15 gives OCTOBER 15, 2026, which is EXACTLY the construction "
                     "Pub. OR-OC uses EXPLICITLY for the composite return. The DOR's Example 3 (a July "
                     "29 filing) does not discriminate. A MISSED FILING DEADLINE HERE IS IRRECOVERABLE - "
                     "'The election may not be made retroactively.' DEFAULT TO THE EARLIER DATE "
                     "(SEPTEMBER 15) AND DIAGNOSE."),
     "notes": ("Payment is due 4/15/2026 regardless of any extension to file. The arithmetic note for "
               "the record: March 16 -> April 15 is ONE month, not five (the FEDERAL EXTENDED date of "
               "September 15 is five months later still).")},
]

OR21_RULE_LINKS: list[tuple] = [
    ("R-OR21-PROVENANCE", "OR_2025_FORM_OR21_INSTR", "primary", "Worksheet OR-21 p. 10 and its 'Do not file' stamp"),
    ("R-OR21-PROVENANCE", "OR_DOR_PTE_E_PROGRAM_PAGE", "secondary", "'We will not be releasing the OR-21 in paper form'"),
    ("R-OR21-SEPARATE", "OR_2021_CH589_PTE_E", "primary", "sec. 3(8) - a separate entity tax return"),
    ("R-OR21-SEPARATE", "OR_IRS_2025_1065_1120S", "implementation", "the base is federal Schedule K"),
    ("R-OR21-BASE", "OR_2025_FORM_OR21_INSTR", "primary", "the federal source map, lines 6-15"),
    ("R-OR21-BASE", "OR_IRS_2025_1065_1120S", "implementation", "all 20 references verified positionally, 0 errors"),
    ("R-OR21-BASE", "OR_2025_PUB_OR21_EST", "secondary", "the separately-stated-deduction exclusion"),
    ("R-OR21-L21", "OR_2025_FORM_OR21_INSTR", "primary", "the self-contradicting line-21 paragraph, logged"),
    ("R-OR21-RATE", "OR_2021_CH589_PTE_E", "primary", "sec. 3(6) - the statutory rate"),
    ("R-OR21-RATE", "OR_2025_FORM_OR21_INSTR", "implementation", "the six-step worksheet and both worked examples"),
    ("R-OR21-STOP", "OR_2025_FORM_OR21_INSTR", "primary", "the line-22 STOP and the parallel no-election refund path"),
    ("R-OR21-ELECTION", "OR_2021_CH589_PTE_E", "primary", "sec. 3(1)-(2) - eligibility, annual, revocable, not retroactive"),
    ("R-OR21-ELECTION", "OR_2025_FORM_OR21_INSTR", "implementation", "the box-1 attestation and the revocation mechanics"),
    ("R-OR21-CALYEAR", "OR_2025_FORM_OR21_INSTR", "primary", "'filed on a calendar-year basis'"),
    ("R-OR21-CALYEAR", "OR_2021_CH589_PTE_E", "secondary", "⚠ the ORS 2025 Edition note carries the PRE-SB-1510 window"),
    ("R-OR21-OWNER-LEGS", "OR_2025_SCH_OR21_K1", "primary", "lines 1-3 and their published owner destinations"),
    ("R-OR21-OWNER-LEGS", "OR_2025_PUB_OR_CODES", "primary", "codes 167, 900 (NOT prorated) and 387"),
    ("R-OR21-OWNER-LEGS", "OR_2021_CH589_PTE_E", "secondary", "sec. 3(3)(b) - the unlocated QBI-rate OAR (U14)"),
    ("R-OR21-MD-TIEOUT", "OR_2025_SCH_OR21_MD_INSTR", "primary", "the column-s rule and the mandatory Part B Caution"),
    ("R-OR21-MD-TIEOUT", "OR_2021_CH589_PTE_E", "secondary", "swept for an escape hatch; none exists"),
    ("R-OR21-UPPER", "OR_2025_SCH_OR21_MDPT_INSTR", "primary", "the upper-tier pass-through rules"),
    ("R-OR21-UPPER", "OR_2025_FORM_OR21_INSTR", "implementation", "'enter 0 on lines 6 through 33, then go to Part F'"),
    ("R-OR21-EST", "OR_2025_FORM_OR21_INSTR", "primary", "the regular and annualized installment worksheets"),
    ("R-OR21-EST", "OR_2025_PUB_OR21_EST", "secondary", "⚠ Rev. 10-16-24 - the oldest artifact in the set (U6)"),
    ("R-OR21-EST", "OR_2021_CH589_PTE_E", "secondary", "sec. 5(2) - the statutory estimated-payment mandate"),
    ("R-OR21-UND-INT", "OR_2025_FORM_OR21_INSTR", "primary", "the 13-row event worksheet and the January-1 carve-out"),
    ("R-OR21-PENALTY", "OR_2025_FORM_OR21_INSTR", "primary", "5% + interest, and Example 3's 105-day count"),
    ("R-OR21-K1-SUPPRESS", "OR_2025_SCH_OR_K1", "primary", "the OR-K-1 suppression instructions"),
    ("R-OR21-K1-SUPPRESS", "OR_2025_SCH_OR21_K1", "primary", "'not a substitute for ... Oregon Schedule OR-K-1'"),
    ("R-OR21-DUEDATE", "OR_2021_CH589_PTE_E", "primary", "sec. 3(8) - the ORS ch. 316 date"),
    ("R-OR21-DUEDATE", "OR_ORS_314_385_DUE", "primary", "ORS 314.385(1)(a)"),
]


_P = "⚠ Worksheet-sourced line number (no published Form OR-21 face) - see R-OR21-PROVENANCE."

OR21_LINES: list[dict] = [
    {"line_number": "B1", "line_type": "input", "sort_order": 1, "description": "Part B box 1. Election",
     "source_rules": ["R-OR21-ELECTION"], "notes": "Carries the perjury attestation. " + _P},
    {"line_number": "B2", "line_type": "input", "sort_order": 2, "description": "Part B box 2. Revocation",
     "source_rules": ["R-OR21-ELECTION"], "notes": "A filed OR-21 with lines 6-23 ZEROED. " + _P},
    {"line_number": "B3", "line_type": "input", "sort_order": 3, "description": "Part B box 3. Amended",
     "notes": "Requires an amended OR-21-K-1 to every member, and a ZEROED GHOST ROW for a member listed by mistake. " + _P},
    {"line_number": "B4", "line_type": "input", "sort_order": 4, "description": "Part B box 4. Extension",
     "source_rules": ["R-OR21-DUEDATE"], "notes": "⚠ The extended due date is NEVER STATED (U7). " + _P},
    {"line_number": "B5", "line_type": "input", "sort_order": 5, "description": "Part B box 5. Pass through",
     "source_rules": ["R-OR21-UPPER"],
     "notes": "'If the PTE is not making its own election ... do not check any other boxes.' " + _P},
    {"line_number": "6", "line_type": "input", "sort_order": 6, "description": "Ordinary business income or (loss)",
     "calculation": "1065 Schedule K line 1 / 1120-S Schedule K line 1", "source_rules": ["R-OR21-BASE"], "notes": _P},
    {"line_number": "7", "line_type": "input", "sort_order": 7, "description": "Net rental real estate income or (loss)",
     "calculation": "Schedule K line 2 (both)", "source_rules": ["R-OR21-BASE"], "notes": _P},
    {"line_number": "8", "line_type": "input", "sort_order": 8, "description": "Other net rental income or (loss)",
     "calculation": "Schedule K line 3c (both)", "source_rules": ["R-OR21-BASE"], "notes": _P},
    {"line_number": "9", "line_type": "input", "sort_order": 9, "description": "Guaranteed payments to partners",
     "calculation": "1065 Schedule K line 4c; 1120-S: ENTER 0", "source_rules": ["R-OR21-BASE"],
     "notes": "⚠ THE ONLY MODULE FORK IN THE BASE. " + _P},
    {"line_number": "10", "line_type": "input", "sort_order": 10, "description": "Interest",
     "calculation": "1065 Schedule K line 5 / 1120-S Schedule K line 4", "source_rules": ["R-OR21-BASE"], "notes": _P},
    {"line_number": "11", "line_type": "input", "sort_order": 11, "description": "Ordinary dividends",
     "calculation": "1065 line 6a / 1120-S line 5a", "source_rules": ["R-OR21-BASE"], "notes": _P},
    {"line_number": "12", "line_type": "input", "sort_order": 12, "description": "Royalties",
     "calculation": "1065 line 7 / 1120-S line 6", "source_rules": ["R-OR21-BASE"], "notes": _P},
    {"line_number": "13", "line_type": "calculated", "sort_order": 13, "description": "Net capital gain or (loss)",
     "calculation": "1065 lines 8 + 9a / 1120-S lines 7 + 8a", "source_rules": ["R-OR21-BASE"],
     "notes": "⚠ THE ONLY COMPOSED LINE, and it EXCLUDES 9b/9c (1065) and 8b/8c (1120-S) - characterisation sub-lines that would double-count. " + _P},
    {"line_number": "14", "line_type": "input", "sort_order": 14, "description": "Net IRC section 1231 gain or (loss)",
     "calculation": "1065 line 10 / 1120-S line 9", "source_rules": ["R-OR21-BASE"], "notes": _P},
    {"line_number": "15", "line_type": "input", "sort_order": 15, "description": "Other income or (loss)",
     "calculation": "1065 line 11 / 1120-S line 10", "source_rules": ["R-OR21-BASE"], "notes": _P},
    {"line_number": "16", "line_type": "subtotal", "sort_order": 16, "description": "Total income from all sources. Add lines 6 through 15",
     "calculation": "sum(6..15)", "source_rules": ["R-OR21-BASE"],
     "notes": "⚠ GROSS of every separately-stated deduction - no IRC 179, no charitable, no 199A, no state tax. " + _P},
    {"line_number": "17", "line_type": "input", "sort_order": 17, "description": "Non-apportionable income",
     "source_rules": ["R-OR21-L21"], "notes": "⚠⚠ THIS is what line 21 draws from. " + _P},
    {"line_number": "18", "line_type": "subtotal", "sort_order": 18, "description": "Total apportionable income. Line 16 minus line 17",
     "calculation": "16 - 17", "source_rules": ["R-OR21-BASE"], "notes": _P},
    {"line_number": "19", "line_type": "input", "sort_order": 19,
     "description": "Apportionment percentage from Schedule OR-21-AP, line 12. Enter 100.0000 if you don't apportion income",
     "source_rules": ["R-OR21-BASE"],
     "notes": "⚠ A FOUR-DECIMAL PERCENTAGE - which is exactly why the DOR's line-21 instruction cannot be right. " + _P},
    {"line_number": "20", "line_type": "calculated", "sort_order": 20, "description": "Oregon apportionable income. Line 18 multiplied by line 19",
     "calculation": "18 x 19", "source_rules": ["R-OR21-BASE"], "notes": _P},
    {"line_number": "21", "line_type": "calculated", "sort_order": 21, "description": "Oregon allocated income",
     "calculation": "the portion of LINE 17 allocated to Oregon; = line 17 for a wholly-in-Oregon PTE",
     "source_rules": ["R-OR21-L21"],
     "notes": "⚠⚠ THE DOR SAYS 'LINE 19' TWICE AND IS WRONG BOTH TIMES (OR-DEF-5 / U2). " + _P},
    {"line_number": "22", "line_type": "total", "sort_order": 22, "description": "Total Oregon distributive proceeds. Line 20 plus line 21",
     "calculation": "20 + 21", "source_rules": ["R-OR21-BASE", "R-OR21-STOP"],
     "notes": "⚠ IF THIS IS ZERO OR NEGATIVE: STOP, DO NOT FILE. It is also the OR-21-MD allocation denominator (U5). " + _P},
    {"line_number": "23", "line_type": "calculated", "sort_order": 23, "description": "PTE elective tax",
     "calculation": "min(L22, 250000) x 0.09 + max(0, L22 - 250000) x 0.099",
     "source_rules": ["R-OR21-RATE"], "notes": "Validated against the DOR's six-step worksheet and both worked examples. " + _P},
    {"line_number": "24", "line_type": "input", "sort_order": 24, "description": "Total PTE-E tax payments. Include all payments made prior to April 15, 2026",
     "notes": "⚠ THE ORIGINAL DUE DATE, not the extended one. " + _P},
    {"line_number": "25", "line_type": "calculated", "sort_order": 25, "description": "Net tax. Line 23 minus line 24",
     "calculation": "max(0, 23 - 24)", "notes": _P},
    {"line_number": "26", "line_type": "calculated", "sort_order": 26, "description": "Overpayment of tax. Line 24 minus line 23",
     "calculation": "max(0, 24 - 23)", "notes": _P},
    {"line_number": "27", "line_type": "input", "sort_order": 27, "description": "Penalty and interest for paying late",
     "source_rules": ["R-OR21-PENALTY"],
     "notes": "5% + daily interest; round the TOTAL to the nearest $1 after summing. No 20% and no 100% penalty on this form. " + _P},
    {"line_number": "28", "line_type": "input", "sort_order": 28, "description": "Interest on underpayment of estimated tax",
     "source_rules": ["R-OR21-UND-INT"], "notes": "The 13-row running-balance worksheet with the 01/01/2026 rate-change event. " + _P},
    {"line_number": "29", "line_type": "subtotal", "sort_order": 29, "description": "Total penalty and interest due. Line 27 plus line 28",
     "calculation": "27 + 28", "notes": _P},
    {"line_number": "30", "line_type": "total", "sort_order": 30, "description": "Net tax including penalty and interest. Line 25 plus line 29",
     "calculation": "25 + 29", "notes": _P},
    {"line_number": "31", "line_type": "total", "sort_order": 31, "description": "Overpayment less penalty and interest. Line 26 minus line 29",
     "calculation": "26 - 29", "notes": _P},
    {"line_number": "32", "line_type": "input", "sort_order": 32, "description": "Amount of line 31 applied to 2026 estimated PTE-E tax",
     "notes": "⚠ A BET ON NEXT YEAR'S ELECTION - the election is ANNUAL. " + _P},
    {"line_number": "33", "line_type": "total", "sort_order": 33, "description": "Net refund. Line 31 minus line 32",
     "calculation": "31 - 32", "notes": _P},
    {"line_number": "AP-10", "line_type": "subtotal", "sort_order": 40, "description": "Schedule OR-21-AP line 10. Total Oregon sales. Add lines 1 through 9",
     "calculation": "sum(AP 1..9)",
     "notes": ("⚠ SALES-FACTOR-ONLY - no property factor, no payroll factor, no double-weighted "
               "alternative (N7). ⚠ DO NOT ASSUME A LINE-FOR-LINE MAPPING TO SCHEDULE OR-AP: the "
               "sequence matches but OR-21-AP line 2 carries an EXPLICIT exclusion ('but not to the U.S. "
               "government or purchasers where the PTE isn't taxable') that OR-AP line 14 leaves "
               "implicit. ⚠ Line 5 uses Schedule OR-PI 'as a guide' but OR-PI 'isn't required to be "
               "filed with Form OR-21.' " + _P)},
    {"line_number": "AP-12", "line_type": "calculated", "sort_order": 41,
     "description": "Schedule OR-21-AP line 12. Oregon apportionment percentage. Line 10 divided by line 11",
     "calculation": "AP-10 / AP-11, rounded to four decimal places", "destination_form": "Form OR-21 line 19", "notes": _P},
    {"line_number": "MD-r", "line_type": "input", "sort_order": 50, "description": "Schedule OR-21-MD column r. Member's distributive proceeds",
     "source_rules": ["R-OR21-MD-TIEOUT"],
     "notes": "From the entity's return / Schedule OR-K-1 Part III lines 1-11 OREGON COLUMN. A REPORTING linkage, not a computational one. " + _P},
    {"line_number": "MD-s", "line_type": "calculated", "sort_order": 51, "description": "Schedule OR-21-MD column s. Addition for tax deducted at federal level",
     "calculation": "(member's positive share / Form OR-21 line 22) x the total federal state-tax deduction",
     "source_rules": ["R-OR21-MD-TIEOUT"], "notes": "⚠⚠ U5 - cannot tie out when any member has a NEGATIVE share. " + _P},
    {"line_number": "MD-t", "line_type": "calculated", "sort_order": 52, "description": "Schedule OR-21-MD column t. Credit for PTE-E tax paid",
     "calculation": "the same percentage x Form OR-21 line 23", "source_rules": ["R-OR21-MD-TIEOUT"],
     "notes": "'Do not include penalty, interest on unpaid tax, or interest on an underpayment of estimated tax.' " + _P},
    {"line_number": "MD-3", "line_type": "total", "sort_order": 53, "description": "Schedule OR-21-MD line 3. Total distributive proceeds (column r)",
     "calculation": "sum(column r)",
     "notes": "⚠ NO STATED TIE-OUT TARGET - but that is an INFERENCE, not a textual fact; the Caution's wording is generic. " + _P},
    {"line_number": "MD-4", "line_type": "total", "sort_order": 54, "description": "Schedule OR-21-MD line 4. Total addition (column s)",
     "calculation": "sum(column s); MUST equal the federal state-tax deduction", "source_rules": ["R-OR21-MD-TIEOUT"], "notes": _P},
    {"line_number": "MD-5", "line_type": "total", "sort_order": 55, "description": "Schedule OR-21-MD line 5. Total credit (column t)",
     "calculation": "sum(column t); MUST equal Form OR-21 line 23", "source_rules": ["R-OR21-MD-TIEOUT"], "notes": _P},
    {"line_number": "K1-1", "line_type": "calculated", "sort_order": 60, "description": "Schedule OR-21-K-1 line 1. Distributive proceeds",
     "calculation": "OR-21-MD column r + OR-21-MD-PT column l", "source_rules": ["R-OR21-OWNER-LEGS"],
     "notes": "⚠ FOR THE MEMBER'S INFORMATION ONLY - 'It is not reported on your federal or Oregon personal income tax return.'"},
    {"line_number": "K1-2", "line_type": "calculated", "sort_order": 61, "description": "Schedule OR-21-K-1 line 2. Addition for tax deducted at federal level",
     "calculation": "OR-21-MD column s + OR-21-MD-PT column m",
     "destination_form": "Schedule OR-ASC Section A / OR-ASC-NP Section B, addition code 167",
     "source_rules": ["R-OR21-OWNER-LEGS"]},
    {"line_number": "K1-3", "line_type": "calculated", "sort_order": 62, "description": "Schedule OR-21-K-1 line 3. Credit for PTE-E tax paid",
     "calculation": "OR-21-MD column t + OR-21-MD-PT column n",
     "destination_form": "Schedule OR-ASC Section F / OR-ASC-NP Section I, refundable credit code 900",
     "source_rules": ["R-OR21-OWNER-LEGS"],
     "notes": "⚠⚠ CODE 900 IS NOT PRORATED FOR NONRESIDENTS OR PART-YEAR RESIDENTS. The full credit, every time."},
]

OR21_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_OR21_NO_PUBLISHED_FACE", "severity": "error",
     "title": "Form OR-21 has NO published form face - every line number is worksheet-sourced",
     "condition": "any Form OR-21 line is rendered or transmitted",
     "message": ("The Oregon DOR has never published a Form OR-21, Schedule OR-21-MD, Schedule OR-21-AP "
                 "or Schedule OR-21-MD-PT face, in any year. Every line number in this spec comes from "
                 "'Worksheet OR-21' inside the instructions, stamped 'This worksheet is for "
                 "informational purposes only. Do not file this worksheet.' Whether those numbers are "
                 "the MeF schema's line numbers is an INFERENCE. THERE IS NO PRINTABLE FORM OR-21 FOR "
                 "THIS PRODUCT TO FILL OR RENDER: the return is filed through Revenue Online or MeF, and "
                 "a paper substitute would have to go through the DOR's substitute-forms approval track. "
                 "⚠ The campaign's 'the printed face governs' convention cannot be applied to this form."),
     "notes": "U1. Settled only by the DOR developers' handbook, draft forms and test scenarios - a Ken-only action, DECIDED (D-12 A5) but NOT SENT."},
    {"diagnostic_id": "D_OR21_L21_FROM_L17", "severity": "warning",
     "title": "Line 21 is built from LINE 17 - the DOR instruction says line 19 TWICE and is wrong",
     "condition": "line 21 is computed",
     "message": ("The instruction reads 'enter the amount from line 19' twice in one paragraph. Line 19 "
                 "is a four-decimal PERCENTAGE and line 21 is a dollar field feeding 'line 22 = line 20 "
                 "plus line 21', so the DOR's literal text would ADD A PERCENTAGE TO AN INCOME FIGURE. "
                 "The paragraph's own opening sentence says 'from line 17', and line 17 is the only "
                 "arithmetic that closes: a wholly-in-Oregon PTE has L19 = 100.0000, L20 = L18, L21 = "
                 "L17 and therefore L22 = L16."),
     "notes": "OR-DEF-5 / U2. Two occurrences of the same wrong pointer is the signature of a stale renumbering."},
    {"diagnostic_id": "D_OR21_STOP_DO_NOT_FILE", "severity": "error",
     "title": "Line 22 is zero or negative - DO NOT FILE Form OR-21",
     "condition": "line 22 <= 0",
     "message": ("Verbatim: 'If line 22 is zero or a loss (negative number), STOP. Do not file Form "
                 "OR-21. Instead, go to the PTE's account on Revenue Online and request a refund of all "
                 "estimated PTE-E tax payments made for this tax year.' Produce a CLIENT INSTRUCTION, "
                 "NOT A RETURN. The same shape applies to the separate 'request for refund without "
                 "election' path."),
     "notes": "Form OR-21-REF is request-only and is not in the DOR's published forms list (U8)."},
    {"diagnostic_id": "D_OR21_ANNUAL_ELECTION", "severity": "info",
     "title": "The PTE-E election is ANNUAL and does NOT bind future years",
     "condition": "the election box is checked",
     "message": ("2021 Or. Laws ch. 589 sec. 3(2): 'The election shall be made ANNUALLY ... The election "
                 "may not be made retroactively.' It must be re-made every year and it is REVOCABLE by "
                 "all current members on or before the due date. ⚠ ELIGIBILITY: all members must be "
                 "individuals, or PTEs owned entirely by individuals - A SINGLE CORPORATE, TRUST OR "
                 "ESTATE MEMBER DISQUALIFIES THE ENTITY. Grantor trusts and single-member LLCs are "
                 "look-through and do not disqualify. ⚠ REGISTRATION ON REVENUE ONLINE IS NOT THE SAME "
                 "AS MAKING THE ELECTION."),
     "notes": "⚠ Do NOT carry the Mississippi 'binding on future years' assumption over - Oregon answers it the OPPOSITE way."},
    {"diagnostic_id": "D_OR21_REVOCATION_DEADLINE", "severity": "warning",
     "title": "Revocation deadline: the statute and the DOR instructions disagree",
     "condition": "a revocation is filed after the unextended due date",
     "message": ("2021 Or. Laws ch. 589 sec. 3(2) allows revocation 'only on or before THE DUE DATE of "
                 "the pass-through entity's return for that tax year' - with NO extension language, in "
                 "pointed contrast to the ELECTION sentence in the same subsection ('including "
                 "extensions'). The DOR instructions add 'including extension' to the revocation rule "
                 "anyway. This build follows the DOR (the broader, taxpayer-favourable reading). AN "
                 "INVALID REVOCATION LEAVES AN ELECTION IN FORCE, WHICH CHANGES THE TAX. Confirm with "
                 "the Department before relying on a post-deadline revocation."),
     "notes": "U22, added by the verification pass. Settle by an OAR under ch. 589 sec. 5(3) or DOR confirmation."},
    {"diagnostic_id": "D_OR21_CALENDAR_YEAR_ONLY", "severity": "warning",
     "title": "Form OR-21 is calendar-year only - a fiscal-year PTE elects for the year its fiscal year ENDS",
     "condition": "the entity's tax year is not the calendar year",
     "message": ("'Form OR-21 is filed on a calendar-year basis ... PTEs using a fiscal year will make "
                 "the election for the calendar year in which their fiscal year ends. PTEs must wait "
                 "until the 2026 form is available to make the election for a fiscal year beginning in "
                 "2025 and ending in 2026.' THE SAME CLIENT CAN THEREFORE HAVE A FISCAL-YEAR FORM OR-65 "
                 "AND A CALENDAR-YEAR FORM OR-21 FOR OVERLAPPING PERIODS. ⚠ Fiscal-year filers still use "
                 "the CALENDAR-YEAR estimated-payment due dates."),
     "notes": "A genuine structural divergence from OR-65 and OR-20-S, both of which accept fiscal years."},
    {"diagnostic_id": "D_OR21_CODE_900_NOT_PRORATED", "severity": "warning",
     "title": "Refundable credit 900 is NOT prorated for nonresident or part-year members",
     "condition": "a member is a nonresident or part-year resident and claims the PTE-E credit",
     "message": ("Publication OR-CODES marks credits that must be prorated with 'PR' - 895, 896, 897, 898 "
                 "and 901 carry it. CODE 900 IS MARKED PLAIN 'X' ON OR-40, OR-40-N AND OR-40-P. A "
                 "NONRESIDENT MEMBER GETS THE FULL CREDIT. Applying the generic nonresident proration to "
                 "code 900 UNDERSTATES EVERY NONRESIDENT MEMBER'S REFUND. The credit is refundable in "
                 "full - ORS 316.502(3)(b) lists ch. 589 sec. 3 among the provisions authorising 'refund "
                 "payments in excess of tax liability'."),
     "notes": "A genuine and favourable Oregon quirk. ⚠ There is NO corporate analogue - individual members only."},
    {"diagnostic_id": "D_OR21_THREE_OWNER_LEGS", "severity": "info",
     "title": "The owner side is CREDIT **AND** ADD-BACK - three legs, not one",
     "condition": "Schedule OR-21-K-1 is issued",
     "message": ("Leg 1: ADDITION code 167 (Schedule OR-ASC Section A / OR-ASC-NP Section B) for the "
                 "member's share of the PTE-E tax the entity deducted federally. Leg 2: REFUNDABLE "
                 "CREDIT code 900 (Section F / Section I), NOT prorated. Leg 3, in a LATER year: "
                 "SUBTRACTION code 387, when a refund of the previously-added tax is reported federally. "
                 "⚠ A FOURTH interaction exists and no DOR PTE-E document mentions it: ch. 589 sec. "
                 "3(3)(b) lets the code-167 add-back qualify as QUALIFYING INCOME for Oregon's QBI "
                 "reduced rate under ORS 316.043, 'in a proportion determined by the department by rule' "
                 "- and that OAR is UNLOCATED."),
     "notes": "U14. Individual-module scope, but it changes an owner's tax."},
    {"diagnostic_id": "D_OR21_TWO_K1S_SUPPRESSION", "severity": "warning",
     "title": "An electing PTE issues TWO Oregon K-1s and must SUPPRESS the PTE-E items on Schedule OR-K-1",
     "condition": "the PTE-E election is made",
     "message": ("'Don't include the PTE-E addition if the PTE made the election to pay PTE-E tax' "
                 "(OR-K-1 lines 14-18) and 'Don't include the PTE-E tax credit if the PTE elected to pay "
                 "the PTE-E tax' (line 19). The PTE-E items ride EXCLUSIVELY on Schedule OR-21-K-1. "
                 "Neither schedule substitutes for the other and NEITHER IS FILED - both are furnished "
                 "to the owner and kept with records. Counting the federal K-1 and any composite "
                 "reporting, that is FOUR DISTINCT DOCUMENTS PER OWNER. Both instruction sets must be "
                 "transmitted with their schedules."),
     "notes": "SUPPRESSION logic, not just population logic. Engagement order: OR-65/OR-20-S -> OR-21 -> OR-21-K-1 -> OR-K-1 -> OR-19/OR-OC."},
    {"diagnostic_id": "D_OR21_UPPER_TIER_MUST_FILE", "severity": "error",
     "title": "A NON-ELECTING upper-tier PTE must still file a partial Form OR-21",
     "condition": "the entity is an upper-tier member of an electing lower-tier PTE and is not electing",
     "message": ("Complete Parts A, B (BOX 5 ONLY - 'do not check any other boxes') and F, with 0 on "
                 "lines 6 through 33, plus Schedule OR-21-MD-PT (a SEPARATE one for EACH electing "
                 "lower-tier entity), plus a Schedule OR-21-K-1 to every member. 'The addition and "
                 "credit reported to the upper-tier PTE by the electing lower-tier entity CAN'T BE "
                 "CLAIMED ON AN ENTITY-LEVEL RETURN and must be passed through.' An ELECTING upper-tier "
                 "PTE completes ALL parts plus BOTH Schedule OR-21-MD and Schedule OR-21-MD-PT."),
     "notes": "A third distinct document state, easy to miss entirely."},
    {"diagnostic_id": "D_OR21_EXTENDED_DATE_UNKNOWN", "severity": "error",
     "title": "The Form OR-21 EXTENDED due date is never stated - defaulting to the EARLIER date",
     "condition": "an extension is claimed for Form OR-21",
     "message": ("'Oregon will honor the same extension request' as the federal Form 1065/1120-S "
                 "extension, which runs to SEPTEMBER 15, 2026 - but six months from Oregon's own April "
                 "15 due date gives OCTOBER 15, 2026, and that is exactly the construction Publication "
                 "OR-OC uses EXPLICITLY for the composite return. The DOR's own Example 3 (a July 29 "
                 "filing) does not discriminate. THIS BUILD DEFAULTS TO SEPTEMBER 15, 2026, BECAUSE A "
                 "MISSED DEADLINE IS IRRECOVERABLE - 'The election may not be made retroactively.' "
                 "CONFIRM WITH THE DEPARTMENT. Payment is due April 15, 2026 regardless of any extension "
                 "to file."),
     "notes": "U7. Settled by the DOR developers' handbook (U1) or an OAR."},
    {"diagnostic_id": "D_OR21_PAYMENT_CUTOFF_APRIL15", "severity": "warning",
     "title": "Line 24 counts only payments made BEFORE April 15, 2026",
     "condition": "a PTE-E payment was made after the original due date",
     "message": ("'Enter the total of all PTE-E tax payments made prior to April 15, 2026.' A payment "
                 "made on the EXTENDED filing date lands in penalty and interest, not on line 24. The "
                 "DOR's Example 3 confirms it: a July 29 payment is treated as unpaid tax at April 15 "
                 "and drives the 5% penalty."),
     "notes": "An extension to file is not an extension to pay."},
    {"diagnostic_id": "D_OR21_APPLY_FORWARD_BET", "severity": "info",
     "title": "Applying an overpayment forward is a bet on next year's election",
     "condition": "line 32 is non-zero",
     "message": ("The election is ANNUAL. 'Note: If the PTE does not elect to pay PTE-E tax next year, "
                 "you will need to request a refund on Revenue Online of the amount you're applying as "
                 "an estimated payment.' Confirm the client intends to re-elect for 2026 before applying "
                 "an overpayment forward."),
     "notes": "Form OR-21-REF is the no-internet alternative and is request-only."},
    {"diagnostic_id": "D_OR21_EST_SAFE_HARBOR", "severity": "warning",
     "title": "The 100%-of-prior-year safe harbour requires an ELECTION to have been made for 2024",
     "condition": "the prior-year safe harbour is used",
     "message": ("'To use safe harbor for 2025, the PTE must have MADE THE ELECTION for 2024.' Filing a "
                 "2024 return is not enough. The required annual payment is the LESSER of 90% of the "
                 "2025 tax and 100% of the 2024 tax. ⚠ Underpayment interest may be charged EVEN IF THE "
                 "RETURN SHOWS AN OVERPAYMENT, if estimated payments were late or too small. TY2025 "
                 "installments: April 15, JUNE 16 (June 15 was a Sunday), September 15 and JANUARY 15, "
                 "2026 - the INDIVIDUAL Q4 date, not the corporate December 15."),
     "notes": "⚠ Three different quarterly calendars coexist in the Oregon PTE space; a shared 'Oregon estimates' component will get at least one wrong."},
    {"diagnostic_id": "D_OR21_UND_JAN1_DAYCOUNT", "severity": "warning",
     "title": "Underpayment interest: January 1 is an off-by-one carve-out in the day count",
     "condition": "the underpayment period spans 01/01/2026",
     "message": ("The DOR's worksheet carries '01/01/2026 Rate change' as a first-class EVENT ROW. "
                 "Day-count rule, verbatim: 'Count the number of days after the first event that creates "
                 "a positive running balance until the next event that changes the running balance, "
                 "including the day of the next event (EXCEPT JANUARY 1 WHEN THERE HAS BEEN A CHANGE IN "
                 "THE INTEREST RATE; INCLUDE JANUARY 1 IN THE DAY COUNT FOR A SUBSEQUENT EVENT) ... "
                 "Don't count any days when the running balance is negative or zero.' Daily rates are "
                 "0.000247 through 2025 and 0.000219 from 2026."),
     "notes": "⚠ The OR-20-S table prints the same rates as PERCENTS (0.0247% / 0.0219%). Same numbers, two notations."},
    {"diagnostic_id": "D_OR21_R15_MD_DENOMINATOR", "severity": "error",
     "title": "RED-DEFER: the Schedule OR-21-MD allocation cannot tie out with a NEGATIVE member share",
     "condition": "any member's column-r share of distributive proceeds is negative",
     "message": ("PROVEN CONTRADICTION. The DOR allocates only to members with a POSITIVE share but "
                 "divides by Form OR-21 LINE 22, which is a NET entity-level figure including negative "
                 "shares. Part B lines 4 and 5 must tie exactly to the federal state-tax deduction and "
                 "to line 23 - and both tie out IF AND ONLY IF sum(positive shares) equals line 22. "
                 "Worked example: +$100,000 / +$100,000 / -$50,000 gives line 22 = $150,000 and line 23 "
                 "= $13,500, but lines 4 and 5 each total $18,000 - 33.3% OVER, i.e. $18,000 of "
                 "refundable member credit against $13,500 of entity tax. A ZERO share is harmless; only "
                 "a NEGATIVE share breaks it. PREPARE SCHEDULE OR-21-MD MANUALLY AND CONFIRM THE "
                 "DENOMINATOR WITH THE DEPARTMENT."),
     "notes": ("⚠⚠ THE OBVIOUS FIX - using the sum of positive shares as the denominator - REASONS FROM "
               "THE MANDATORY TIE-OUT CAUTION, NOT FROM ANY CITED RULE. It must NOT be presented to Ken "
               "or to a preparer as verified DOR guidance. Settle by an OAR under ch. 589 sec. 5(3), DOR "
               "guidance, or the MeF validation rules. U5.")},
    {"diagnostic_id": "D_OR21_R14_MEF_SCHEMA", "severity": "error",
     "title": "RED-DEFER: the Form OR-21 MeF submission type and schema family are UNKNOWN",
     "condition": "an electronic Form OR-21 submission is attempted",
     "message": ("Everything public is verified and it is still not enough. The DOR's PTE-E program page "
                 "confirms an approved software vendor MAY file the return ('Returns can only be filed "
                 "electronically either through Revenue Online or an approved software vendor'), and the "
                 "approved-vendor list carries a 'Pass-through Entity Elective' category - but the DOR's "
                 "corporate e-file page lists only FIVE MeF business programs (Corporation, Oregon "
                 "Composite, Partnership, Transit Self-Employment, Fiduciary) and OMITS PTE-E. NO PUBLIC "
                 "PAGE STATES THE SUBMISSION TYPE OR SCHEMA FAMILY. Obtainable ONLY from the LOI-gated "
                 "Oregon MeF Handbook for Software Developers and Tax Preparers. Until then, prepare the "
                 "Form OR-21 computation and have the preparer key it into Revenue Online."),
     "notes": ("U1 / U19. ONE EMAIL ANSWERS IT (electronic.filing@dor.oregon.gov, 503-945-8415) AND NO "
               "PUBLIC PAGE WILL. A Ken-only action, DECIDED at D-12 A5 but NOT YET SENT. It unlocks U1, "
               "U19 and U23 together - the highest-value single action in the Oregon wave.")},
    {"diagnostic_id": "D_OR21_PAPER_UNAVAILABLE", "severity": "warning",
     "title": "The DOR contradicts itself on whether a paper Form OR-21 exists at all",
     "condition": "a paper Form OR-21 is requested",
     "message": ("The FINAL TY2025 instruction booklet offers paper on request ('File Form OR-21 by mail "
                 "only if you requested a paper return because you don't have internet access') while "
                 "the DOR's PTE-E program page says 'Paper returns will not be accepted' and 'We will "
                 "not be releasing the OR-21 in paper form.' Both were re-fetched 2026-08-19 and they "
                 "cannot both be operative. WORKING POSITION: TREAT PAPER AS UNAVAILABLE and route the "
                 "no-internet case to BusinessAlternative.IncomeTax@dor.oregon.gov as an exception "
                 "request."),
     "notes": "U23 / OR-DEF-6. ⚠ The 'face beats instructions' rule cannot resolve it, because Form OR-21 has no face."},
]

OR21_SCENARIOS: list[dict] = [
    {"scenario_name": "OR-21 RATE ORACLE - DOR worked example 1: $425,000 gives $39,825", "scenario_type": "normal",
     "inputs": {"L22": 425000},
     "expected_outputs": {"worksheet_a": 425000, "worksheet_b": 250000, "worksheet_c": 175000,
                          "worksheet_d": 17325.0, "worksheet_e": 22500, "worksheet_f": 39825.0, "L23": 39825.0},
     "notes": "'Smith and Sons, a general partnership ... The PTE-E tax is $39,825.' The closed form must agree with the six-step worksheet.",
     "sort_order": 1},
    {"scenario_name": "OR-21 RATE ORACLE - DOR worked example 2: $180,000 gives $16,200", "scenario_type": "normal",
     "inputs": {"L22": 180000},
     "expected_outputs": {"worksheet_c": 0, "worksheet_d": 0.0, "worksheet_e": 16200.0, "L23": 16200.0},
     "notes": "'Mountaintop, Inc., an S corporation ... The PTE-E tax is $16,200.' Line e takes the FIRST branch when line d is 0.",
     "sort_order": 2},
    {"scenario_name": "OR-21 RATE BOUNDARY - exactly $250,000 gives $22,500 on both branches", "scenario_type": "edge",
     "inputs": {"L22": 250000},
     "expected_outputs": {"L23": 22500.0, "worksheet_f": 22500.0, "continuous": True},
     "notes": "The DOR's line-e branch is SAFE AT THE BOUNDARY: line c = 0 so line e computes 250,000 x 9% = the same $22,500 as the shortcut constant.",
     "sort_order": 3},
    {"scenario_name": "OR-21 LINE 21 - wholly-in-Oregon PTE closes only when L21 comes from L17", "scenario_type": "edge",
     "inputs": {"module": "1065", "sch_k": {"1": 300000, "5": 20000}, "L17": 20000, "L19": 100.0},
     "expected_outputs": {"L16": 320000.0, "L18": 300000.0, "L20": 300000.0, "L21": 20000.0, "L22": 320000.0,
                          "L22_equals_L16": True},
     "notes": ("⚠ Following the DOR's literal 'enter the amount from line 19' would put 100.0 into L21 "
               "and give L22 = 300,100 - a percentage added to an income figure. OR-DEF-5 / U2."),
     "sort_order": 4},
    {"scenario_name": "OR-21 MODULE FORK - guaranteed payments are 0 for an S corporation", "scenario_type": "edge",
     "inputs": {"sch_k": {"1": 100000, "4c": 80000, "5": 5000, "4": 5000}},
     "expected_outputs": {"L9_1065": 80000.0, "L9_1120S": 0.0, "L10_1065": 5000.0, "L10_1120S": 5000.0},
     "notes": ("'If the PTE is a partnership, enter the total guaranteed payments from federal Schedule "
               "K, line 4c; otherwise, enter 0.' The ONLY fork in the base. Note line 10 also forks its "
               "SOURCE (1065 line 5 vs 1120-S line 4) even where the value happens to match."),
     "sort_order": 5},
    {"scenario_name": "OR-21 STOP - a loss year produces a client instruction, not a return", "scenario_type": "failure",
     "inputs": {"L22": -40000},
     "expected_outputs": {"do_not_file": True, "L23": 0.0,
                          "action": "request a refund of all estimated PTE-E payments through Revenue Online"},
     "sort_order": 6},
    {"scenario_name": "OR-21-MD U5 - the PROVEN counterexample: $18,000 of credit against $13,500 of tax",
     "scenario_type": "failure",
     "inputs": {"member_shares": [100000, 100000, -50000], "total_addition": 18000, "L22": 150000, "L23": 13500},
     "expected_outputs": {"sum_positive_shares": 200000, "line_22": 150000, "tie_out_possible": False,
                          "as_written_line_4": 24000.0, "as_written_line_5": 18000.0,
                          "candidate_positive_denominator_line_4": 18000.0,
                          "candidate_positive_denominator_line_5": 13500.0,
                          "candidate_is_dor_guidance": False},
     "notes": ("⚠⚠ PROVEN, NOT SUSPECTED. Both Part B tie-outs hold IFF sum(positive r) == L22. The "
               "candidate fix is reasoned from the mandatory Caution, NOT from any cited rule, and must "
               "not be presented as DOR guidance."),
     "sort_order": 7},
    {"scenario_name": "OR-21-MD U5 - a ZERO share is harmless; only a NEGATIVE share breaks the tie-out",
     "scenario_type": "edge",
     "inputs": {"member_shares": [100000, 50000, 0], "total_addition": 9000, "L22": 150000, "L23": 13500},
     "expected_outputs": {"sum_positive_shares": 150000, "tie_out_possible": True,
                          "as_written_line_4": 9000.0, "as_written_line_5": 13500.0},
     "notes": "The original 'zero-or-loss' framing was TOO BROAD. A zero share contributes 0 to both sides.",
     "sort_order": 8},
    {"scenario_name": "OR-21 PENALTY - DOR Example 3 pins the 105-day count and the $1 rounding",
     "scenario_type": "normal",
     "inputs": {"unpaid_tax": 4825, "days_late": 105, "interest_calendar_year": 2026},
     "expected_outputs": {"penalty": 241.25, "interest": 110.95, "total": 352.20, "line_27": 352},
     "notes": ("April 16 to July 29, 2026 inclusive = 105 days at 0.0219%/day. The TOTAL is rounded to "
               "the nearest dollar AFTER summing, not component-wise. No 20% and no 100% penalty exists "
               "on this form."),
     "sort_order": 9},
    {"scenario_name": "OR-21 ESTIMATES - the safe harbour is the LESSER of 90% current and 100% prior",
     "scenario_type": "normal",
     "inputs": {"current_year_tax": 40000, "prior_year_tax": 30000},
     "expected_outputs": {"L2": 36000.0, "L3": 30000.0, "L4": 30000.0, "L5": 7500.0},
     "notes": "⚠ And only if the PTE MADE THE ELECTION for 2024 - filing a 2024 return is not enough.",
     "sort_order": 10},
    {"scenario_name": "OR-21 ESTIMATES - under $1,000 turns underpayment interest off entirely",
     "scenario_type": "edge",
     "inputs": {"current_year_tax": 900, "prior_year_tax": 5000},
     "expected_outputs": {"below_threshold": True, "L4": 0.0, "L5": 0.0},
     "notes": "The test is on the CURRENT-year tax at worksheet line 1 (Form OR-21 instructions) / line 2 (Pub. OR-21-EST). Prefer the former (U6).",
     "sort_order": 11},
    {"scenario_name": "OR-21 ANNUALIZED - column A: multiplier 4, cumulative 22.5%", "scenario_type": "normal",
     "inputs": {"period_index": 0, "period_proceeds": 60000},
     "expected_outputs": {"multiplier": 4.0, "percentage": 0.225, "L3": 240000.0, "L4": 21600.0, "L6": 4860.0},
     "notes": "Period ends 3/31, 5/31, 8/31, 12/31 => 3, 5, 8, 12 months; multipliers 4 / 2.4 / 1.5 / 1; cumulative 22.5 / 45 / 67.5 / 90%.",
     "sort_order": 12},
    {"scenario_name": "OR-21 DOCUMENT STATE - a non-electing upper-tier PTE still files", "scenario_type": "edge",
     "inputs": {"election": False, "revocation": False, "amended": False, "upper_tier_passthrough": True},
     "expected_outputs": {"document_state": "upper_tier_only", "lines_6_to_33": 0,
                          "parts_completed": ["A", "B (box 5 only)", "F"],
                          "schedules": ["OR-21-MD-PT (one per electing lower-tier entity)", "OR-21-K-1 to every member"]},
     "sort_order": 13},
    {"scenario_name": "OR-21 OWNER LEGS - credit 900 is NOT prorated for a nonresident", "scenario_type": "edge",
     "inputs": {"member_residency": "nonresident", "md_col_t": 9000},
     "expected_outputs": {"K1_L3": 9000.0, "prorated": False,
                          "destination": "Schedule OR-ASC-NP Section I, refundable credit code 900"},
     "notes": "Pub. OR-CODES marks 895/896/897/898/901 'PR'; 900 is plain 'X' on all three individual forms.",
     "sort_order": 14},
]


# ═══════════════════════════════════════════════════════════════════════════
# SHARED DIAGNOSTICS -- attached to ALL THREE specs. These are the cross-cutting
# rulings and the RED-DEFERS. ⚠ EVERY RED-DEFER HAS ITS OWN DIAGNOSTIC: NO SILENT
# GAP, AND NOTHING SILENTLY INCLUDED EITHER.
# ═══════════════════════════════════════════════════════════════════════════
OR_SHARED_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_OR_TY2026_CONFORMITY_STALE", "severity": "error",
     "title": "⚠ STATUTORY STALENESS TRIPWIRE - SB 1507 invalidates this spec's frozen side for TY2026",
     "condition": "the engagement tax year is later than 2025",
     "message": ("EVERY FIGURE IN THIS SPEC IS TY2025-KEYED. Enrolled SB 1507 = 2026 Oregon Laws ch. 142 "
                 "sec. 35 changes ORS 314.011(2)(b)(A) and (2)(c) from December 31, 2023 to December 31, "
                 "2025, and sec. 41 does the same to ORS 317.010(7). Section 48(1) applies those "
                 "amendments 'to transactions or activities occurring on or after January 1, 2026, in "
                 "tax years beginning on or after January 1, 2026', so TY2025 stays at 12/31/2023 and "
                 "TY2026 MOVES. SB 1507 ALSO DECOUPLES OREGON FROM IRC 168(k) for property placed in "
                 "service in tax years beginning on or after 1/1/2026, measured against 168(k) as in "
                 "effect December 1, 2017 - A TY2026 OREGON PTE SPEC MUST MODEL A FULL DUAL-BASIS "
                 "REGIME AND A TY2025 ONE MUST NOT. Re-verify every frozen-side figure before any TY2026 "
                 "authoring. ⚠ Residual open item: whether SB 1507 sec. 48(2)-(3)'s retroactivity "
                 "machinery reaches a TY2025 return is NOT SETTLED."),
     "notes": ("The tax-year-keyed lookup `_yk` RAISES rather than defaulting, so a TY2026 engagement "
               "cannot silently inherit TY2025 conformity. ⚠ Near-miss on the record: HB 2092 (2025 R1) "
               "would have disconnected the ROLLING prong for exactly TY2025 and died in Senate Finance "
               "and Revenue - the TY2025 conclusion is right, but it was one committee vote from void.")},
    {"diagnostic_id": "D_OR_CONFORMITY_NOT_FLAT", "severity": "info",
     "title": "Oregon's conformity is a HYBRID - do not flatten it, and do not encode the DOR one-liner",
     "condition": "any conformity determination is made",
     "message": ("ROLLING for the definition of taxable income (ORS 314.011(2)(b)(B) / 317.010(7)(b)), so "
                 "OBBBA flows into TY2025 automatically - 100% bonus, $2.5M/$4M IRC 179, NO add-back, NO "
                 "separate Oregon basis for TY2025 acquisitions. FIXED at 12/31/2023 for an ENUMERATED "
                 "list at ORS 314.011(2)(c), all of it administrative or mechanical. ⚠ THE DOR'S OWN "
                 "ONE-LINER - 'Oregon is tied to the federal definition of taxable income as of December "
                 "31, 2023', printed byte-for-byte across all three corporate instruction sets - IS "
                 "STATED BACKWARDS. ⚠ BUILD TO THE ENUMERATION, NOT TO A CATEGORY JUDGMENT: Oregon's "
                 "CORPORATE NOL rules live in ORS 317.476/317.479, NOT in chapter 314, so the "
                 "chapter-314 freeze list does not reach them."),
     "notes": "⚠ IRC 1375 is split across BOTH prongs by subsection - inert for TY2025, recorded for TY2026 (U12)."},
    {"diagnostic_id": "D_OR_CODE_NAMESPACE_REQUIRED", "severity": "error",
     "title": "⚠⚠ A bare Oregon modification code number is meaningless without a namespace",
     "condition": "any modification code is resolved without a namespace, or across namespaces",
     "message": ("Oregon runs TWO numerically-overlapping, semantically-different modification code sets "
                 "and ONE PTE ENGAGEMENT TOUCHES BOTH. Twelve numbers collide: 118, 132, 150, 151, 158, "
                 "159, 352, 356, 358 and 361 carry DIFFERENT ITEMS; 338 and 344 carry the same item under "
                 "DIFFERENT LABELS. Code 158 is the exemplar - 'gain or loss on disposition of "
                 "depreciable property' (corporate) versus 'interest and dividends on government bonds "
                 "of other states' (individual) - and its semantic twin in the individual set is 154, so "
                 "a NUMBER-DRIVEN mapper posts a depreciation-basis difference onto a municipal-interest "
                 "line AND THE RETURN STILL FOOTS. MAP BY LABEL, KEY BY NAMESPACE, NEVER CARRY A BARE "
                 "INTEGER ACROSS THE BOUNDARY. ⚠⚠ THE CROSSING POINT IS THE SCHEDULE OR-K-1 OVERFLOW "
                 "ATTACHMENT, which must carry INDIVIDUAL codes EVEN WHEN THE ISSUING PTE IS AN S "
                 "CORPORATION whose own lines 2/3 use CORPORATE codes."),
     "notes": ("⚠⚠ THE DECOY: the two DOR 'don't use Schedule OR-ASC-CORP codes on Schedule SM' notes are "
               "TRUE AND IRRELEVANT. Schedule SM is a code-free named-line schedule and nobody claimed "
               "otherwise; those notes say NOTHING about the overflow attachment. A verification pass "
               "was fooled by exactly this, refuted the crossing point, and RETRACTED the refutation. "
               "NAMESPACE THE LOOKUP; DO NOT POLICE SCHEDULE SM. C1 / D-12.")},
    {"diagnostic_id": "D_OR_APPENDIX_A_IS_SUBSET", "severity": "warning",
     "title": "Appendix A is the S-corp SUBSET of the OR-ASC-CORP code universe - code 341 proves it",
     "condition": "a corporate modification code is validated against Appendix A alone",
     "message": ("Schedule OR-ASC-CORP is shared across Forms OR-20, OR-20-INC, OR-20-INS and OR-20-S, "
                 "and codes exist on it that Appendix A does not list. Worked proof: code 341 ('Income "
                 "on a composite return') is directed by Publication OR-OC to Schedule OR-ASC-CORP "
                 "Section B for CORPORATE COMPOSITE OWNERS, yet appears NOWHERE in Appendix A. Seed the "
                 "corporate table from the FULL OR-ASC-CORP universe and apply an OR-20-S eligibility "
                 "filter on top - seeding Appendix A as if it were the whole corporate table will FAIL A "
                 "LEGITIMATE CORPORATE COMPOSITE SUBTRACTION."),
     "notes": "Pub. OR-CODES correctly lists 341 for OR-40-N and OR-40-P only, since composite joiners are nonresidents."},
    {"diagnostic_id": "D_OR_DEPR_ABSENCE_IS_A_RULING", "severity": "info",
     "title": "VERIFIED NEGATIVE: Oregon has no TY2025 bonus add-back and no state IRC 179 cap",
     "condition": "federal bonus depreciation or an IRC 179 deduction is claimed",
     "message": ("ORS 317.301 is the ONLY IRC 168(k)/179 disconnect in Oregon law and its window is "
                 "CLOSED - the applicability note (2011 c.7 sec. 31) limits it to tax years beginning on "
                 "or after 1/1/2009 and before 1/1/2011. Its only TY2025 relevance is subsection (4), "
                 "the UNWIND of a 2009/2010 addition. Publication OR-17 (Rev. 01-29-26) p. 91: 'As of "
                 "the date this publication was last revised, Oregon had not disconnected from any new "
                 "federal depreciation expense provisions for this tax year.' ⚠ DO NOT PORT ANOTHER "
                 "STATE'S ADD-BACK AND DO NOT BUILD A NULLABLE 'state depreciation adjustment' FIELD "
                 "'for symmetry' - a nullable field a preparer can fill is worse than no field. ⚠ BUT "
                 "the per-asset DUAL BASIS must still exist: Schedule OR-DEPR column 1b reads 'Date "
                 "placed in service IN OREGON' and column 1d is a separate 'Oregon cost or other basis', "
                 "the hook for the property-transferred-into-Oregon rule, and four legacy populations "
                 "can still throw a TY2025 difference."),
     "notes": "N1. Schedule OR-DEPR is a WORKSHEET, not filed; only the net difference rides as corporate 174/353 or individual 152/354."},
    {"diagnostic_id": "D_OR_R1_TRANSIT_SE", "severity": "error",
     "title": "R1 RED-DEFER - transit self-employment returns (Form OR-TM / OR-LTD) are prepared manually",
     "condition": "Form OR-65 line 7B or 7D is Yes",
     "message": ("Form OR-TM (TriMet, 150-555-001, rate 0.008237) and Form OR-LTD (Lane, 150-560-001, "
                 "rate 0.0080) are not prepared by this product, nor is Schedule OR-TSE-AP "
                 "(150-500-051). Both apply to net self-employment earnings OVER $400 and district "
                 "membership is determined by a ZIP-CODE LIST published in each instruction booklet. The "
                 "partnership MAY ELECT TO FILE ON THE PARTNERS' BEHALF - an entity-vs-owner filing "
                 "branch. Both are DOR-administered, both are MeF-fileable under the named 'Transit "
                 "Self-Employment' program, and the DOR's approved-vendor list carries a distinct "
                 "'Transit (partnerships)' category. Prepare manually."),
     "notes": "⚠ Only 7B and 7D produce a return; 7A and 7C (employees) do not. Still open (U8): the ZIP-code district lists and Schedule OR-TSE-AP itself."},
    {"diagnostic_id": "D_OR_R2_PORTLAND_METRO", "severity": "error",
     "title": "R2 RED-DEFER - Portland / Multnomah / Metro business returns. A ROUTING ITEM WITH NO DECISION TAKEN.",
     "condition": "the entity has Portland, Multnomah County or Metro District activity",
     "message": ("FOUR SEPARATE RETURNS are not prepared by this product: Form P-2025 (1065) and Form "
                 "SC-2025 (1120-S), each a COMBINED City of Portland Business License Tax + Multnomah "
                 "County Business Income Tax return, plus Form METBIT-65 and Form METBIT-20S for the "
                 "Metro Supportive Housing Services BIT, which is A SEPARATE RETURN. Administered by the "
                 "CITY OF PORTLAND REVENUE DIVISION - 'we are a separate government agency from the "
                 "Oregon Department of Revenue' - through its own portal and its OWN MeF program with "
                 "its own ATS, its own FTA-SES schemas and its own approved-vendor list. NOTHING ROUTES "
                 "THROUGH OREGON DOR. TY2025 rates: City 2.6% / $100 minimum / exempt under $50,000 "
                 "gross receipts; County 2.0% / $100 / under $100,000; Metro 1.0% / $100 / applies OVER "
                 "$5,000,000. ⚠ E-FILE IS MANDATORY FOR ALL FOUR FROM TY2025. ⚠ $0 AND EXEMPT CITY AND "
                 "COUNTY RETURNS MUST STILL BE FILED (12 exemption codes: 1, 2, 3, 6-13, 99); Metro is "
                 "different because the $5M threshold decides who files at all. PREPARE THESE RETURNS IN "
                 "ANOTHER PRODUCT."),
     "notes": ("D-12 W8 - a GROUP E ROUTING ITEM WITH NO DECISION TAKEN, named here so it is neither "
               "silently included nor silently excluded. ⚠ CORRECTED MECHANISM: LIC-2.05's PREPARER "
               "prong covers PERSONAL returns ONLY; the four business returns are bound by the BUSINESS "
               "prong, whose trigger is the TAXPAYER's own federal e-file duty (26 CFR 301.6011-3(a) for "
               "partnerships, 301.6037-2(a) for S corps; 301.6011-5 is the Form 1120 rule and does not "
               "reach 1120-S). LIC-2.05 has NO numeric threshold of its own. Because the count "
               "aggregates W-2s and 1099s, nearly every real PTE client is caught, so the force of the "
               "scope call is unchanged. ⚠ THE DEPENDENCY THAT ARGUES FOR DOING THEM TOGETHER: P-2025 "
               "and SC-2025 line 10 import 'Oregon modifications on Form 65 / Form 20-S' DIRECTLY, so "
               "Schedule I and Schedule SM are INPUTS to the local returns and any change re-flows.")},
    {"diagnostic_id": "D_OR_R2_METBIT_LINE_MAP", "severity": "error",
     "title": "R2a - the METBIT line map is NOT the P-2025/SC-2025 line map. Reusing it is BUILD-CORRUPTING.",
     "condition": "a METBIT-65 or METBIT-20S line map is authored",
     "message": ("P-2025 and SC-2025 start at PART II LINE 7 ('Ordinary net income or (loss)') and pull "
                 "Schedule K at LINE 10. METBIT-65 and METBIT-20S start at PART II LINE 4 ('Ordinary "
                 "income or (loss) from Form 1065 / 1120-S') and pull Schedule K at LINE 6. ⚠⚠ ON THE "
                 "METBIT FORMS, LINE 7 IS 'Non-business income or loss subtraction'. A spec that reuses "
                 "the P/SC map for the METBIT returns WRITES ORDINARY INCOME INTO THE NON-BUSINESS-INCOME "
                 "SUBTRACTION, AND THE RETURN STILL FOOTS. Federal starting points: Form 1065 (2025) "
                 "line 23 and Form 1120-S (2025) line 22 - and note Portland's TY2025 instructions use "
                 "the CURRENT federal line numbers throughout; the stale pointer is Oregon's alone."),
     "notes": ("⚠ Also two DIFFERENT 75% rules, not one: the NOL cap applies on THREE computations (City "
               "line 29, County line 19, METBIT line 12) AND the owner's compensation deduction is "
               "itself capped at 75% of net business income, with the per-owner dollar cap ($160,500 "
               "City / $158,500 County) a CEILING ON AN ALREADY-LIMITED FIGURE. Applying only the dollar "
               "cap OVER-DEDUCTS. Neither applies to Metro.")},
    {"diagnostic_id": "D_OR_R3_CPAR", "severity": "error",
     "title": "R3 RED-DEFER - CPAR reporting (Form OR-OC + Schedules OR-OC-3/-4) is prepared manually",
     "condition": "a federal partnership audit adjustment affects Oregon tax",
     "message": ("Not prepared by this product. Use Form OR-OC with Schedule OR-OC-3 (individual, "
                 "fiduciary, tiered) and Schedule OR-OC-4 (C corporation) to report CPAR adjustments "
                 "WHETHER OR NOT the election to pay CPAR tax is made, filing a separate form per "
                 "audited year. Rates are FLAT top rates with no brackets and no minimum tax: 9.9% "
                 "individual, 7.6% corporate. THREE DISTINCT CLOCKS, none of them a normal tax date: "
                 "filing 180 DAYS after the FPA (or 90 days from the audited partnership's extended due "
                 "date for a tiered partner); payment 270 DAYS from the FPA. The election is irrevocable "
                 "after the filing due date. If the election is NOT made, an amended Form OR-65 is also "
                 "required, with an 'as if' federal Form 1065 for each adjusted year marked 'as if' at "
                 "the top. Owner-side codes: addition 187 / subtraction 384 - and 'use these codes, even "
                 "if another code is assigned for the specific type of increased or decreased income.'"),
     "notes": "⚠ A CPAR Form OR-OC is a STRUCTURALLY DIFFERENT DOCUMENT from a composite Form OR-OC - a different subset of lines, no PTE-E credit, no kicker, no line 11."},
    {"diagnostic_id": "D_OR_R4_OC_TR", "severity": "error",
     "title": "R4 RED-DEFER - Form OR-OC-TR payment transfers are prepared manually, and the form was not retrievable",
     "condition": "a composite payment must be transferred to an owner's account",
     "message": ("Form OR-OC-TR (150-101-158) is not prepared by this product AND IT DOES NOT APPEAR IN "
                 "THE DOR'S TY2025 OR 'General' FORMS-LIST QUERY RESULTS despite being named throughout "
                 "Publication OR-OC. A transfer request must be submitted ON OR BEFORE the composite "
                 "return's due date INCLUDING extensions, and BEFORE the composite return is filed. "
                 "'Once the payments have been transferred to the owner, the payments can't be "
                 "transferred back to the PTE.' Mail to PO Box 14999."),
     "notes": "U8 - re-pull before the composite module is built."},
    {"diagnostic_id": "D_OR_R5_280E_AS_IF", "severity": "error",
     "title": "R5 RED-DEFER - the marijuana / psilocybin IRC 280E modification and its 'as if' federal return",
     "condition": "the entity is an Oregon-licensed marijuana or psilocybin business",
     "message": ("Not computed by this product. ORS 317.363 makes IRC 280E inapplicable to conduct "
                 "authorized under the Oregon marijuana and psilocybin statutes. The subtraction is 'the "
                 "difference between the profit/loss on the actual federal return and the \"as if\" "
                 "return' - requiring a SECOND SYNTHETIC FEDERAL RETURN, computed as if the expenses "
                 "were federally deductible, which is NEVER FILED and is kept with the entity's records. "
                 "⚠ A FLOOR RULE WITH NO CORPORATE ANALOGUE: the deduction 'can't be used to create a "
                 "net operating loss. It can only reduce your Oregon source income to zero.' Codes: "
                 "individual 359 marijuana / 385 psilocybin; corporate 375 / 385 - ⚠ PSILOCYBIN SHARES "
                 "385 ACROSS BOTH NAMESPACES BUT MARIJUANA DOES NOT."),
     "notes": "⚠ Oregon requires TWO DIFFERENT KINDS of 'as if' federal Form 1065 - this one and the CPAR one - and neither is a federal filing."},
    {"diagnostic_id": "D_OR_R6_ALT_APPORTIONMENT", "severity": "error",
     "title": "R6 RED-DEFER - alternative apportionment petitions (both methods) are prepared manually",
     "condition": "the taxpayer petitions for alternative apportionment",
     "message": ("Not prepared by this product. Method 1 files the petition with the return and checks "
                 "the face box; Method 2 is a separate petition titled 'Alternative apportionment "
                 "request' and is the DOR's stated preference. THE RETURN IS ALWAYS FILED ON STANDARD "
                 "APPORTIONMENT, even while a petition is pending, and the DOR 'will not rule ... until "
                 "you file your original or amended return using standard apportionment provisions.' "
                 "Allow at least SIX MONTHS. An approval PERSISTS across years 'unless and until we "
                 "revoke it'. Mail Method 2 petitions to the Corporation Section, 955 Center St NE, "
                 "Salem OR 97301-2555."),
     "notes": "⚠ Form OR-65 has no checkbox and is absent from Appendix C's list, but ORS 314.667(1) is taxpayer-agnostic, so a partnership may still petition (U11)."},
    {"diagnostic_id": "D_OR_R7_DOUBLE_WEIGHTED", "severity": "error",
     "title": "R7 RED-DEFER - the double-weighted sales factor, and ANY ORS 314.280 filer on Form OR-21",
     "condition": "a utility, telecommunications, financial-institution or public-utility PTE",
     "message": ("The double-weighted sales worksheet is not computed by this product. It is available "
                 "only to taxpayers 'primarily engaged in utilities or telecommunications' - AN UNDEFINED "
                 "THRESHOLD - and is cited to ORS 314.650 (1999 EDITION), a deliberately FROZEN prior "
                 "edition, so do not read the current single-sales-factor statute and conclude the "
                 "worksheet is obsolete. Three things a naive implementation gets wrong: the sales "
                 "factor is entered TWICE (that IS the double-weighting); the divisor is THE NUMBER OF "
                 "FACTORS WITH A POSITIVE COLUMN-(b) DENOMINATOR, not a constant 4; and the election "
                 "rides Form OR-20-S Question I. ⚠⚠ WORSE ON FORM OR-21: Schedule OR-21-AP HAS NO "
                 "PROPERTY OR PAYROLL FACTOR AT ALL and therefore no double-weighted alternative, YET "
                 "the OR-21 line 19 instruction routes financial institutions and public utilities to "
                 "ORS 314.280. THERE IS NO OR-21 ARTIFACT ON WHICH TO PERFORM THAT APPORTIONMENT."),
     "notes": "U13 - an unresolved DOR gap, not a research shortfall. RED-DEFER such PTEs regardless."},
    {"diagnostic_id": "D_OR_R8_BROADCASTERS", "severity": "error",
     "title": "R8 RED-DEFER - broadcaster apportionment (ORS 314.674) is prepared manually",
     "condition": "the entity is a broadcaster",
     "message": ("Oregon's distinct broadcaster regime - an audience/subscriber factor under ORS 314.674 "
                 "and a statutory 0.6% factor for certain subscription-service receipts - is not "
                 "computed by this product. ⚠ Broadcasters are ABSENT from the Schedule OR-AP "
                 "instructions' modified-apportionment industries table, which is a GAP IN THE OR-AP "
                 "BOOKLET rather than a conflict; the regime is sourced from the Form OR-20 instructions."),
     "notes": "Recorded so a later pass does not read the OR-AP table as exhaustive."},
    {"diagnostic_id": "D_OR_R9_FCG20", "severity": "error",
     "title": "R9 RED-DEFER - Schedule OR-FCG-20 (farm long-term capital gain) is prepared manually",
     "condition": "Form OR-20-S line 9 is entered",
     "message": ("Schedule OR-FCG-20 (150-102-167) is not prepared by this product AND WAS NOT RETRIEVED "
                 "during research. Complete it manually; its line 9 amount is SUBTRACTED at Form OR-20-S "
                 "line 9 to give line 10 (ORS 317.063)."),
     "notes": "U8 - re-pull before this line ships."},
    {"diagnostic_id": "D_OR_R10_OR24", "severity": "error",
     "title": "R10 RED-DEFER - Form OR-24 like-kind exchanges, including the RECURRING annual filing",
     "condition": "the Form OR-24 checkbox is set",
     "message": ("Form OR-24 (150-101-734) is not prepared by this product. ⚠ THE FILING OBLIGATION "
                 "RECURS EVERY YEAR UNTIL DISPOSITION, not once at the exchange: 'Include this form with "
                 "your Oregon return each year until the disposition of the like-kind property, and the "
                 "gain or loss is reported.' Required only when ALL THREE conditions hold: deferred gain "
                 "was reported on a federal Form 8824; all or part of the property given up was in "
                 "Oregon; and all or part of the acquired property is OUTSIDE Oregon. For a partnership "
                 "the deferral election is ALL-OR-NOTHING across consenting partners. ⚠⚠ FEDERAL FORM "
                 "8824 LINE PAIRS: lines 19/23/24 are PART III (the ordinary like-kind exchange); lines "
                 "32/36/37 are PART IV, DEFERRAL OF GAIN FROM SECTION 1043 CONFLICT-OF-INTEREST SALES - "
                 "a completely different fact pattern keyed off a certificate of divestiture. "
                 "RELATED-PARTY exchanges live in PART II and in line 24's own text. A BUILD THAT ROUTES "
                 "A RELATED-PARTY EXCHANGE TO THE 32/36/37 BRANCH IMPORTS SECTION 1043 DIVESTITURE "
                 "FIGURES INTO A SECTION 1031 RETURN."),
     "notes": ("✅ All six of Form OR-24's federal pointers were re-verified against the FINAL 2025 Form "
               "8824 and STILL RESOLVE, despite OR-24 being Rev. 08-18-23 - RE-CHECK EACH TAX YEAR. ⚠ "
               "The OR-20-S instructions cite the form as 150-800-734; the correct number is "
               "150-101-734. Related modifications: corporate addition 118 / subtraction 352.")},
    {"diagnostic_id": "D_OR_R11_PCR", "severity": "error",
     "title": "R11 RED-DEFER - Form OR-PCR protective claims are prepared manually",
     "condition": "a refund claim is contingent on a pending court decision or legislative action",
     "message": ("Form OR-PCR (150-101-184) is not prepared by this product. 'Don't file an amended "
                 "return as a protective claim.' Notify the DOR within 90 DAYS of the final "
                 "determination by filing an amended return, and 'Don't file an amended return before "
                 "the pending action is final.'")},
    {"diagnostic_id": "D_OR_R12_INSURANCE_FIN", "severity": "error",
     "title": "R12 RED-DEFER - insurance and financial-institution apportionment paths on Schedule OR-AP",
     "condition": "the entity is an insurer or a financial institution",
     "message": ("Schedule OR-AP tags lines 7a/7b, 8a/8b, 19, 20 and 21 '(insurance only)' and the "
                 "modified-apportionment industries table routes insurers to ORS 317.660 and financial "
                 "corporations to ORS 314.280 / OAR 150-314-0088. Neither path is computed by this "
                 "product. Note also the sales-factor exclusion that catches ordinary PTEs with a "
                 "portfolio: GROSS RECEIPTS FROM HEDGING TRANSACTIONS AND FROM THE MATURITY, REDEMPTION, "
                 "SALE, EXCHANGE, LOAN OR OTHER DISPOSITION OF CASH OR SECURITIES ARE OMITTED FROM THE "
                 "SALES FACTOR ENTIRELY - not sourced, OMITTED (ORS 314.610(7)(a)(A)). A build that "
                 "sweeps all federal Schedule K gross receipts into line 18 inflates BOTH numerator and "
                 "denominator and produces a wrong percentage."),
     "notes": "The ORS 317.660 citation is [UNVERIFIED] - ORS chapter 317 was not pulled for that section."},
    {"diagnostic_id": "D_OR_R13_PART_YEAR_OWNER", "severity": "error",
     "title": "R13 RED-DEFER - a part-year resident owner's Schedule OR-K-1 column (b) must be adjusted BY THE OWNER",
     "condition": "an owner is a part-year Oregon resident",
     "message": ("The schedule explicitly hands the problem to the owner: 'Oregon taxes all PTE income "
                 "received while an Oregon resident. For the portion of the year you are a nonresident, "
                 "Oregon only taxes income from Oregon sources. The amounts reported in column (b) MAY "
                 "NEED TO BE MODIFIED ... If your residency status changes, be sure to notify the PTE.' "
                 "The PTE cannot compute it. Provide the unadjusted column (b) with a clear note."),
     "notes": "⚠ And the resident/nonresident fill patterns are already asymmetric - a resident uses column (b) for lines 19 and 20 ONLY."},
    {"diagnostic_id": "D_OR_R16_LOSS_MEMBER_PTE", "severity": "error",
     "title": "R16 RED-DEFER (conditional) - a PTE-E entity with any LOSS-share member",
     "condition": "the PTE-E election is made and any member has a negative share of distributive proceeds",
     "message": ("Schedule OR-21-MD cannot be completed correctly for this entity until the DOR settles "
                 "the allocation denominator (see D_OR21_R15_MD_DENOMINATOR). Prepare Schedule OR-21-MD "
                 "and every Schedule OR-21-K-1 manually, and confirm the denominator with the Department "
                 "before filing. A ZERO-share member is fine; only a NEGATIVE share triggers this."),
     "notes": ("Conditional on U5. Deferring EVERY loss-member PTE would defer a large share of real "
               "clients, which is why the recommendation is a working rule plus a loud diagnostic - but "
               "the working rule is NOT DOR guidance and this build does not pretend otherwise.")},
    {"diagnostic_id": "D_OR_VOUCHER_NEVER_WITH_RETURN", "severity": "warning",
     "title": "NEVER send a payment voucher with a return - stated on all five Oregon PTE forms",
     "condition": "a voucher is attached to a return",
     "message": ("The rule is printed on the Form OR-65 face ('don't use a payment voucher'), the Form "
                 "OR-20-S face ('Do not include a payment voucher with your return'), OR-20-S "
                 "instructions p. 6, the Form OR-21 instructions and Publication OR-OC. A BUILD THAT "
                 "ALWAYS ATTACHES A VOUCHER IS WRONG ON ALL FIVE FORMS. All five vouchers mail to PO Box "
                 "14950; returns go to nine other destinations. ⚠ Form OR-65-V has only TWO payment "
                 "types (no `Estimated payment`), while OR-20-V and OR-21-V each have three. ⚠ Form "
                 "OR-21-V is published as a year-agnostic 'General' item, so a forms sweep filtered on "
                 "Year = 2025 will wrongly report it missing."),
     "notes": "⚠ PO Box 14555 serves BOTH Form OR-65 and a PAYING Form OR-OC - the address alone does not identify the return."},
    {"diagnostic_id": "D_OR_PERSISTENT_CLIENT_STATE", "severity": "warning",
     "title": "Six Oregon requirements are PERSISTENT CLIENT STATE with no home on any form",
     "condition": "an Oregon PTE engagement is opened",
     "message": ("(1) 2024 Schedule OR-OC-1 field (a) PER OWNER - including for owners who have since "
                 "LEFT - to compute the TY2025 composite kicker at 9.863%. (2) Form OR-19-AF affidavits, "
                 "standing across years, WITH A RE-FILING TRIGGER WHEN OWNERSHIP MOVES BY 10 PERCENTAGE "
                 "POINTS OR MORE. (3) The apportionment percentage FROM THE YEAR OF SALE for each "
                 "installment sale, carried indefinitely (ORS 314.615). (4) Alternative-apportionment "
                 "approvals, which persist 'unless and until we revoke it'. (5) High-income-taxpayer "
                 "status - federal taxable income of $1,000,000 or more in ANY of the three prior years. "
                 "(6) Per-asset Oregon basis distinct from federal, for legacy 2009/2010 and "
                 "transferred-in property. NONE of these can be derived from the current return."),
     "notes": ("D-12 W10 - a data-model commitment, not a form question. The kicker item is the single "
               "most stateful requirement in the Oregon PTE module.")},
    {"diagnostic_id": "D_OR_INSTRUCTION_DEFECTS", "severity": "info",
     "title": "SIX FINAL-booklet instruction defects: the printed FACE governs and the conflict is LOGGED",
     "condition": "any Oregon PTE return is prepared",
     "message": ("Standing Oregon authoring convention (campaign D-12 W2): transcribe the printed face; "
                 "where instruction text conflicts with the face or with arithmetic, THE FACE GOVERNS "
                 "AND THE CONFLICT IS LOGGED. The six: (1) OR-20-S Question J points at federal 1120-S "
                 "line 21 instead of line 22, stale THREE form years; (2) OR-20-S Schedule ES totals on "
                 "line 7 per the instructions but line 7 is printed `Reserved` and the total is line 8; "
                 "(3) OR-20-S line 4 arithmetic cites line 1 where the face says line 1c; (4) Form OR-24 "
                 "cited as 150-800-734 instead of 150-101-734; (5) Form OR-21 line 21 points at line 19 "
                 "TWICE where it must be line 17 - which would put a percentage into a dollar field; and "
                 "(6) the OR-21 booklet offers a paper return while the DOR's PTE-E program page says "
                 "paper will not be accepted. ⚠⚠ THE COROLLARY: DEFECT 5 AND DEFECT 6 SIT ON A FORM WITH "
                 "NO PUBLISHED FACE, so the convention CANNOT resolve them."),
     "notes": "That corollary is exactly why the DOR developers' handbook (U1/U19/U23) is the highest-value unlock in the Oregon wave."},
]


# ═══════════════════════════════════════════════════════════════════════════
# THE THREE SPECS
# ═══════════════════════════════════════════════════════════════════════════
FORMS: list[dict] = [
    {
        "identity": {
            "form_number": FORM_CODE_OR65,
            "form_title": "Oregon Partnership Income Return (Form OR-65)",
            "entity_types": ["1065"],
            "notes": (
                "TY2025. An INFORMATION RETURN with a flat $150 minimum tax bolted on - no income line, "
                "no apportionment line and no taxable-income line anywhere on the face (ORS 314.712(1): "
                "'a partnership as such is not subject to the tax imposed by ORS chapter 316, 317 or "
                "318'). The whole tax computation is lines 3A-3D. ⚠ THE FILING GATE (2A OR 2B) AND THE "
                "TAX GATE (1A AND (2A OR 2B)) ARE DIFFERENT BOOLEANS. ⚠ Schedule I is a code/amount grid "
                "drawing the INDIVIDUAL namespace (Publication OR-CODES) - it does NOT foot and NOTHING "
                "flows to line 3. ⚠ Penalty posture is the OPPOSITE of Form OR-20-S's: 'Don't submit a "
                "penalty payment with the return.' ⚠ NO ESTIMATED PAYMENTS. Face 150-101-065 Rev. "
                "05-29-25 ver. 01, completely re-derived positionally after a contamination incident: "
                "INTACT, 0 errors. ⚠ The DOR forms index calls it 'Oregon Partnership Return of Income'; "
                "THE FACE WINS."
            ),
        },
        "facts": OR65_FACTS, "rules": OR65_RULES, "rule_links": OR65_RULE_LINKS,
        "lines": OR65_LINES, "diagnostics": OR65_DIAGNOSTICS + OR_SHARED_DIAGNOSTICS,
        "scenarios": OR65_SCENARIOS,
    },
    {
        "identity": {
            "form_number": FORM_CODE_OR20S,
            "form_title": "Oregon S Corporation Tax Return (Form OR-20-S)",
            "entity_types": ["1120S"],
            "notes": (
                "TY2025. A CORPORATE RETURN THAT COMPUTES ZERO FOR MOST FILERS - lines 1-10 are zero "
                "unless there are built-in gains or excess net passive income - BUT LINE 6 (the "
                "apportionment percentage) IS STILL COMPLETED, because it is the number every "
                "nonresident shareholder needs. That is the single most likely OR-20-S bug. ⚠ The "
                "excise/income checkbox is the highest-leverage field on the form: $150 vs 0 at line 11, "
                "and $150 vs 0 as the credit floor - and THE TWO HALVES HAVE DIFFERENT AUTHORITIES (ORS "
                "317.090(2)(b) for the $150; ORS 318.020/318.031 for the zero). ⚠ Lines 2 and 3 draw the "
                "CORPORATE namespace while the Schedule OR-K-1 overflow attachment this same engagement "
                "issues draws the INDIVIDUAL one. ⚠ Schedule SM is NAMED-LINE and CODE-FREE - "
                "structurally unlike Form OR-65's Schedule I. ⚠ Penalty and interest are SELF-ASSESSED "
                "at lines 22-24. Face 150-102-025 Rev. 07-10-25 ver. 01, 8 pages, completely re-derived "
                "positionally: INTACT, ZERO ERRORS. ⚠ Four spellings of the form's name circulate; USE "
                "THE FACE."
            ),
        },
        "facts": OR20S_FACTS, "rules": OR20S_RULES, "rule_links": OR20S_RULE_LINKS,
        "lines": OR20S_LINES, "diagnostics": OR20S_DIAGNOSTICS + OR_SHARED_DIAGNOSTICS,
        "scenarios": OR20S_SCENARIOS,
    },
    {
        "identity": {
            "form_number": FORM_CODE_OR21,
            "form_title": "Oregon Pass-through Entity Elective Tax Return (Form OR-21)",
            "entity_types": ["1065", "1120S"],
            "notes": (
                "TY2025. A WHOLLY SEPARATE RETURN, and its own RS spec per campaign D-12. Its base is "
                "built ENTIRELY from federal Schedule K with ZERO inputs from Form OR-65 or Form OR-20-S "
                "(verified by two independent workstreams with zero exceptions; the strings 'OR-65' and "
                "'OR-20-S' do not occur anywhere in the instructions). It has its own due date (April "
                "15, via 2021 Or. Laws ch. 589 sec. 3(8) -> ORS 314.385(1)(a) -> IRC 6072(a)), its own "
                "CALENDAR-YEAR-ONLY rule, its own sales-factor-only apportionment schedule, its own "
                "member directory, its own K-1 and its own estimated-tax regime. ⚠⚠ THE DOR HAS NEVER "
                "PUBLISHED A FORM OR-21 FACE, IN ANY YEAR - established by enumerating the FormsPubs "
                "list (1,712 items) - so EVERY LINE NUMBER HERE RESTS ON A 'do not file' WORKSHEET and "
                "the campaign's 'printed face governs' convention has no subject. ⚠ The election is "
                "ANNUAL AND REVOCABLE, NOT binding on future years. Rate 9% / 9.9% at a $250,000 "
                "breakpoint. Owner side is CREDIT AND ADD-BACK: refundable code 900 (NOT prorated for "
                "nonresidents), addition code 167, later subtraction code 387. ⚠⚠ TWO ITEMS ARE BLOCKED "
                "ON THE DOR: the MeF submission type / schema family, and the Schedule OR-21-MD "
                "allocation denominator, which is PROVABLY UNCLOSABLE whenever any member has a negative "
                "share."
            ),
        },
        "facts": OR21_FACTS, "rules": OR21_RULES, "rule_links": OR21_RULE_LINKS,
        "lines": OR21_LINES, "diagnostics": OR21_DIAGNOSTICS + OR_SHARED_DIAGNOSTICS,
        "scenarios": OR21_SCENARIOS,
    },
]


# ═══════════════════════════════════════════════════════════════════════════
# FLOW ASSERTIONS -- exported as JSON and tested in delvio-tax.
# ⚠ assertion_id is CharField(20) and UNIQUE ACROSS THE WHOLE DATABASE.
# ═══════════════════════════════════════════════════════════════════════════
FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-OR-NS-GUARD", "title": "Oregon modification codes are NAMESPACED and cross-use is REFUSED",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 1,
     "description": ("Twelve numbers appear in BOTH the individual (Publication OR-CODES) and corporate "
                     "(Schedule OR-ASC-CORP) sets with non-identical labels: ten semantic collisions "
                     "(118, 132, 150, 151, 158, 159, 352, 356, 358, 361) and two label-only "
                     "near-collisions (338, 344). Form OR-65 Schedule I, Schedule OR-K-1 and the OR-K-1 "
                     "OVERFLOW ATTACHMENT may draw ONLY from the individual table; Form OR-20-S lines 2 "
                     "and 3 may draw ONLY from the corporate table; line 15 is a CREDIT line drawing the "
                     "unrelated 8xx/999 Section D series. No lookup may resolve a bare integer."),
     "definition": {"rule": "R-OR65-SCHED-I-NS + R-OR20S-LINES23-NS",
                    "check": "or_assert_namespace(context, namespace) raises OregonCodeNamespaceError on any mismatch; or_code() raises without a namespace"},
     "bug_reference": "Code 158 posts a depreciation-basis difference onto a municipal-interest line and the return still foots"},
    {"assertion_id": "FA-OR-NS-CROSS", "title": "An S corporation runs BOTH namespaces inside one engagement",
     "assertion_type": "flow_assertion", "entity_types": ["1120S"], "status": "draft", "sort_order": 2,
     "description": ("OR-20-S lines 2/3 use CORPORATE codes while the Schedule OR-K-1 overflow "
                     "attachment the same return issues to each shareholder must use INDIVIDUAL "
                     "(Publication OR-CODES) codes. The DOR publishes no firewall at that point; the two "
                     "'Schedule SM' notes police a code-free schedule and are a DECOY."),
     "definition": {"rule": "R-OR20S-LINES23-NS",
                    "check": "OR_CONTEXT_NAMESPACE['OR20S_LINE_2'] == 'corporate' AND OR_CONTEXT_NAMESPACE['OR_K1_OVERFLOW_ATTACHMENT'] == 'individual'"},
     "bug_reference": "A verification pass refuted this crossing on the strength of the Schedule SM notes and had to RETRACT the refutation"},
    {"assertion_id": "FA-OR-158-154", "title": "The same economic item is 158 corporate and 154 individual",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 3,
     "description": ("Corporate 158 = 'Gain or loss on disposition of depreciable property'; individual "
                     "154 = 'Gain or loss on sale of depreciable property with different basis for "
                     "Oregon'; individual 158 = 'Interest and dividends on government bonds of other "
                     "states'. A LABEL-driven mapper survives the crossing; a NUMBER-driven one fails "
                     "SILENTLY."),
     "definition": {"rule": "R-OR65-SCHED-I-NS",
                    "check": "or_code('corporate',158).label ~ or_code('individual',154).label AND or_code('individual',158).label is a municipal-interest item"}},
    {"assertion_id": "FA-OR65-GATES", "title": "OR-65's filing gate and tax gate are DIFFERENT booleans",
     "assertion_type": "flow_assertion", "entity_types": ["1065"], "status": "draft", "sort_order": 4,
     "description": ("file if (2A OR 2B); owe $150 only if (1A AND (2A OR 2B)). A partnership with Oregon "
                     "resident partners and no Oregon business activity FILES AND OWES NOTHING."),
     "definition": {"rule": "R-OR65-FILE-GATE + R-OR65-TAX-GATE",
                    "check": "or65_must_file(F,T) is True AND or65_line_3a(False,False,True) == 0"},
     "bug_reference": "Collapsing the gates bills $150 to every out-of-state partnership with one Oregon partner"},
    {"assertion_id": "FA-OR65-PRORATE", "title": "OR-65 proration is a PUBLISHED ROUNDED TABLE, not 150 x n / 12",
     "assertion_type": "table_invariant", "entity_types": ["1065"], "status": "draft", "sort_order": 5,
     "description": ("Twelve DOR-published values, every half-dollar rounding UP: 13/25/38/50/63/75/88/"
                     "100/113/125/138/150. Round-half-to-even gives $12/$62/$112 on months 1, 5 and 9 - "
                     "THREE wrong rows, not the five the source brief claims (it lists $138, which is "
                     "the correct chart value). The switch is checkbox (e) `Accounting period change`, "
                     "NOT the `Short-year return` box, and it does not reach initial or final short "
                     "years."),
     "definition": {"rule": "R-OR65-PRORATION", "check": "OR65_PRORATION_TABLE[2025][m] for m in 1..12 equals the DOR chart"},
     "bug_reference": "round(150*n/12) with round-half-to-even mis-states the minimum tax on months 1, 5 and 9"},
    {"assertion_id": "FA-OR65-SCHEDI", "title": "OR-65 Schedule I does not foot and does not flow",
     "assertion_type": "flow_assertion", "entity_types": ["1065"], "status": "draft", "sort_order": 6,
     "description": ("No total line on any of the three sections, and nothing reaches line 3 or any other "
                     "line. Pure pass-through reporting. A tie-out to `Schedule I total x profit %` is "
                     "invalid whenever line 4B is 'No'."),
     "definition": {"rule": "R-OR65-NO-FOOT", "check": "no Schedule I total line exists; L3A is independent of Schedule I"}},
    {"assertion_id": "FA-OR-PENALTY", "title": "THREE penalty postures, one per form. Never unify.",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 7,
     "description": ("OR-65: no penalty or interest line at all and 'Don't submit a penalty payment with "
                     "the return.' OR-20-S: SELF-ASSESSED at lines 22/23/24 with 5% / 20% / 100% "
                     "penalties. OR-21: 5% failure-to-pay plus interest ONLY - no 20%, no 100%."),
     "definition": {"rule": "R-OR65-PENALTY + R-OR20S-PENALTY + R-OR21-PENALTY",
                    "check": "OR65_SELF_ASSESSES_PENALTY is False AND OR20S_SELF_ASSESSES_PENALTY is True AND OR21_HAS_FAILURE_TO_FILE_PENALTY is False"},
     "bug_reference": "A shared 'Oregon penalty engine' writes computed penalties onto Form OR-65, which the DOR tells the filer not to remit"},
    {"assertion_id": "FA-OR20S-L6", "title": "OR-20-S line 6 survives a zero-tax return",
     "assertion_type": "flow_assertion", "entity_types": ["1120S"], "status": "draft", "sort_order": 8,
     "description": ("The face directs a no-BIG/no-ENPI filer to fill in line 6 and then enter -0- on "
                     "lines 7, 8 and 10. Line 6 is the number every nonresident shareholder needs and it "
                     "lands on every Schedule OR-K-1 Part III header."),
     "definition": {"rule": "R-OR20S-L6-ALWAYS", "check": "L6 is populated whenever the return is filed, independent of L7/L8/L10/L12"},
     "bug_reference": "Short-circuiting the form to $150 silently drops the shareholders' apportionment percentage"},
    {"assertion_id": "FA-OR20S-CE-NEG", "title": "OR-20-S has NO Section C line and NO Section E line",
     "assertion_type": "table_invariant", "entity_types": ["1120S"], "status": "draft", "sort_order": 9,
     "description": ("Line 15 draws Schedule OR-ASC-CORP Section D ONLY. The schedule's face routes Total "
                     "C7 and Total E5 to OR-20 / OR-20-INC / OR-20-INS and names OR-20-S in NEITHER "
                     "list, the instructions say S corporations cannot claim standard or refundable "
                     "credits, and Schedule ES line 7 is printed `Reserved`."),
     "definition": {"rule": "R-OR20S-NO-C-E", "check": "no OR_20_S line maps ASC-CORP Section C or Section E; ES line 7 is informational"},
     "bug_reference": "A shared corporate-series map of 'ASC-CORP E5 -> Schedule ES line 7' writes a refundable credit into a reserved box and the return still foots"},
    {"assertion_id": "FA-OR20S-ES8", "title": "Schedule ES totals on line 8, not the instructions' line 7",
     "assertion_type": "reconciliation", "entity_types": ["1120S"], "status": "draft", "sort_order": 10,
     "description": "The printed face governs (D-12 W2). Line 8 carries ES lines 1-6 to Form OR-20-S line 19.",
     "definition": {"rule": "R-OR20S-ES-L8", "check": "OR20S_SCHEDULE_ES_TOTAL_LINE == '8' and line 7 is Reserved"}},
    {"assertion_id": "FA-OR21-SEP", "title": "Form OR-21 takes ZERO lines from Form OR-65 or Form OR-20-S",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 11,
     "description": ("Lines 6-15 are keyed entirely to federal Schedule K and line 19 pulls Schedule "
                     "OR-21-AP. Verified by two independent workstreams with ZERO exceptions - the "
                     "strings 'OR-65' and 'OR-20-S' do not occur anywhere in 150-107-114-1. The one "
                     "linkage that exists runs the OTHER way and is a REPORTING linkage (OR-21-MD column "
                     "r sources member shares from the entity return / Schedule OR-K-1)."),
     "definition": {"rule": "R-OR21-SEPARATE", "check": "every OR_21 line 6..15 maps to a federal Schedule K line, never to an Oregon entity-return line"}},
    {"assertion_id": "FA-OR21-L21", "title": "OR-21 line 21 comes from line 17, and L22 == L16 when wholly in Oregon",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 12,
     "description": ("The DOR instruction says 'line 19' twice and both are wrong - line 19 is a "
                     "four-decimal percentage. Only line 17 closes: with L19 = 100.0000, L20 = L18 and "
                     "L21 = L17, so L22 = L18 + L17 = L16."),
     "definition": {"rule": "R-OR21-L21", "check": "or21_part_c(...,apportionment_pct_l19=100)['L22'] == ['L16']"},
     "bug_reference": "Seeding the DOR's literal text adds a PERCENTAGE to an income figure"},
    {"assertion_id": "FA-OR21-RATE", "title": "OR-21 line 23 closed form agrees with the DOR's six-step worksheet",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 13,
     "description": ("min(L22, 250000) x 0.09 + max(0, L22 - 250000) x 0.099 must equal worksheet line f "
                     "at every input, and must reproduce the DOR's own examples exactly: $425,000 -> "
                     "$39,825 and $180,000 -> $16,200. Continuous at the breakpoint ($22,500 both ways)."),
     "definition": {"rule": "R-OR21-RATE", "check": "or21_tax(x) == or21_tax_worksheet(x)['f'] for all x"}},
    {"assertion_id": "FA-OR21-MD-U5", "title": "⚠ OR-21-MD Part B ties out IFF sum(positive shares) == line 22",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 14,
     "description": ("Line 4 must equal the federal state-tax deduction and line 5 must equal line 23, "
                     "and the DOR allocates only to POSITIVE shares while dividing by the NET line 22. "
                     "Both tie-outs hold if and only if sum(positive column-r shares) == line 22, which "
                     "line 22 cannot satisfy except by coincidence. A ZERO share is harmless; ONLY A "
                     "NEGATIVE SHARE BREAKS IT. ⚠ THE OBVIOUS FIX IS NOT DOR GUIDANCE."),
     "definition": {"rule": "R-OR21-MD-TIEOUT",
                    "check": "or21_md_allocation(...)['tie_out_possible'] is False whenever any share < 0"},
     "bug_reference": "+100,000 / +100,000 / -50,000 yields $18,000 of refundable member credit against $13,500 of entity tax"},
    {"assertion_id": "FA-OR21-900", "title": "Refundable credit 900 is NOT prorated for nonresidents",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 15,
     "description": ("Publication OR-CODES marks 895, 896, 897, 898 and 901 'PR' (must be prorated) and "
                     "marks 900 plain 'X' on OR-40, OR-40-N AND OR-40-P. A nonresident member receives "
                     "the FULL credit. There is no corporate analogue."),
     "definition": {"rule": "R-OR21-OWNER-LEGS", "check": "OR_CODES_INDIVIDUAL_REFUNDABLE[900].prorated is False"},
     "bug_reference": "Applying the generic nonresident proration to code 900 understates every nonresident member's refund"},
    {"assertion_id": "FA-OR21-K1SUPP", "title": "PTE-E items are SUPPRESSED on Schedule OR-K-1 when the election is made",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 16,
     "description": ("OR-K-1 lines 14-18 exclude the PTE-E addition and line 19 excludes the PTE-E credit "
                     "whenever the election is made; the items ride exclusively on Schedule OR-21-K-1. "
                     "An electing PTE issues TWO Oregon K-1s per owner and NEITHER is filed."),
     "definition": {"rule": "R-OR21-K1-SUPPRESS",
                    "check": "or_k1_pte_e_suppression(True) suppresses both, and or_k1_pte_e_suppression(False) suppresses neither"}},
    {"assertion_id": "FA-OR-AP-PART2", "title": "Schedule OR-AP part 2: ONE filed instance, line 10 suppressed off-schedule",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 17,
     "description": ("D-12 W3. The 'must be run twice' mandate is DISPROVEN - the DOR's owner-level use "
                     "is PERMISSIVE. Only the entity-level run is a filed computation; the owner-source "
                     "figure is computed OFF-SCHEDULE with a different line-1 input and line 10 "
                     "SUPPRESSED, per 'Do not use line 10 when computing Oregon-source distributive "
                     "income for nonresident owners of PTEs.'"),
     "definition": {"rule": "R-OR20S-PART1",
                    "check": "or_ap_part2(purpose='owner_source')['filed'] is False and its L10a == L10b == 0"},
     "bug_reference": "Printing two part 2s would put an UNFILED computation on the filed return"},
    {"assertion_id": "FA-OR-DEPR-NEG", "title": "VERIFIED NEGATIVE: no Oregon TY2025 bonus add-back or state 179 cap",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 18,
     "description": ("A rule-says-no. ORS 317.301's window closed at 1/1/2011 and its only TY2025 "
                     "relevance is the unwind at subsection (4). No nullable 'state depreciation "
                     "adjustment' field may be created. ⚠ BUT the per-asset dual basis must exist, "
                     "because Schedule OR-DEPR distinguishes federal basis from 'Oregon cost or other "
                     "basis' keyed to the 'Date placed in service IN OREGON'."),
     "definition": {"rule": "R-OR65-DEPR-NEG + R-OR20S-DEPR-NEG",
                    "check": "no Oregon PTE form carries a bonus add-back, a state 179 limit, a phaseout or a recapture line"},
     "bug_reference": "Porting Georgia's or Tennessee's bonus add-back into Oregon"},
    {"assertion_id": "FA-OR-TY-KEYED", "title": "⚠ Every Oregon figure is TY2025-keyed and SB 1507 moves the frozen side",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 19,
     "description": ("SB 1507 = 2026 Or. Laws ch. 142 sec. 35 moves ORS 314.011(2)(b)(A) and (2)(c) from "
                     "12/31/2023 to 12/31/2025 effective TY2026, and decouples Oregon from IRC 168(k) "
                     "for property placed in service in tax years beginning on or after 1/1/2026. A "
                     "TY2026 spec must model a full dual-basis regime; a TY2025 one must not. The "
                     "tax-year lookup RAISES rather than defaulting, so nothing can silently inherit."),
     "definition": {"rule": "R-OR65-CONFORM + R-OR20S-CONFORM",
                    "check": "or_conformity_fixed_date(2025) == '2023-12-31' and or_conformity_fixed_date(2026) == '2025-12-31' and _yk raises on an unkeyed year"},
     "bug_reference": "A TY2026 engagement silently inheriting TY2025 conformity and no dual-basis depreciation"},
    {"assertion_id": "FA-OR-METBIT", "title": "⚠ The METBIT line map is NOT the P-2025/SC-2025 line map",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 20,
     "description": ("P-2025 and SC-2025 start at Part II line 7 and pull Schedule K at line 10; "
                     "METBIT-65 and METBIT-20S start at Part II line 4 and pull Schedule K at line 6, "
                     "and on the METBIT forms line 7 is 'Non-business income or loss subtraction'. "
                     "RED-DEFERred for v1, but pinned here so the map can never be reused."),
     "definition": {"rule": "D_OR_R2_METBIT_LINE_MAP",
                    "check": "OR_METBIT_LINE_MAP['METBIT-65']['starting_line'] != OR_METBIT_LINE_MAP['P-2025']['starting_line']"},
     "bug_reference": "Reusing the P/SC map writes ordinary income into the non-business-income subtraction and the return still foots"},
    {"assertion_id": "FA-OR21-NOFACE", "title": "⚠ Form OR-21 has no published face - the provenance stamp is mandatory",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft", "sort_order": 21,
     "description": ("Every OR-21 line number rests on a 'do not file' worksheet, so the campaign's "
                     "'printed face governs' convention (D-12 W2) cannot be applied to this form. The "
                     "negative is an ENUMERATION RESULT (FormsPubs list, 1,712 items, __next null; "
                     "150-107-114/-112/-111/-110 absent in every year; AcroForm widget counts 0/0/0/0 "
                     "against 23 on the OR-21-K-1 face)."),
     "definition": {"rule": "R-OR21-PROVENANCE",
                    "check": "every OR_21 line's notes carry the worksheet-provenance stamp"},
     "bug_reference": "Treating worksheet line numbers as MeF schema line numbers without the DOR developers' handbook"},
]


class Command(BaseCommand):
    help = (
        "Load the Oregon PTE specs - Form OR-65, Form OR-20-S and Form OR-21 (TY2025). THREE forms, "
        "TWO modification-code namespaces with a hard cross-use guard, and a TY2026 statutory staleness "
        "tripwire. ⚠ READY_TO_SEED IS FALSE: Gate 1 has not been taken for Oregon and two items are "
        "BLOCKED on the DOR developers' handbook."
    )

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad Oregon PTE specs (Form OR-65 / Form OR-20-S / Form OR-21, TY2025)\n"))
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
        """⚠ REFUSES TO WRITE ANYTHING TO THE DATABASE while Gate 1 is open.

        Runs BEFORE any write, inside the atomic block, so a refusal leaves the
        database untouched.
        """
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
                "\nREFUSING TO SEED THE OREGON PTE SPECS (OR_65 / OR_20_S / OR_21).\n"
                "Gate 1 has NOT been taken for Oregon, and two items are BLOCKED on sources\n"
                "only the Oregon Department of Revenue can supply.\n\n"
                "WHY THIS FILE REFUSES:\n\n"
                "  (1) GATE 1 IS OPEN. Campaign D-12 (2026-08-19) approved the WAVE SCOPE -\n"
                "      three Oregon specs, the code-namespace ruling (C1), the Schedule OR-AP\n"
                "      part 2 reversal, the opposite penalty postures, and the Portland\n"
                "      RED-DEFER. It did NOT approve seeding these specs.\n\n"
                "  (2) OR_21 IS BLOCKED TWICE, and both blockers are DOR-only:\n"
                "      (a) THE MeF SCHEMA FAMILY (U1 / U19 / U23). Oregon has NEVER published\n"
                "          a Form OR-21 face, in any year - established by enumerating the DOR\n"
                "          FormsPubs list (1,712 items, __next = null). EVERY OR-21 LINE NUMBER\n"
                "          IN THIS SPEC RESTS ON A WORKSHEET STAMPED 'Do not file this\n"
                "          worksheet.' Whether those are the MeF schema's line numbers is an\n"
                "          INFERENCE, and the campaign's 'the printed face governs' convention\n"
                "          CANNOT apply, because there is no face. The DOR also contradicts\n"
                "          itself on whether a paper OR-21 exists at all.\n"
                "      (b) THE SCHEDULE OR-21-MD DENOMINATOR (U5). PROVEN IMPOSSIBLE with any\n"
                "          NEGATIVE member share: Part B lines 4 and 5 tie out IF AND ONLY IF\n"
                "          sum(positive column-r shares) == Form OR-21 line 22, and line 22 is\n"
                "          an entity-level federal Schedule K aggregate with no positive-share\n"
                "          filter. Worked counterexample: +100,000 / +100,000 / -50,000 gives\n"
                "          $18,000 of refundable member credit against $13,500 of entity tax.\n"
                "          ⚠ THE OBVIOUS FIX REASONS FROM A TIE-OUT CAUTION, NOT FROM A CITED\n"
                "          RULE, and must never be shipped as DOR guidance.\n\n"
                "      BOTH are unlocked by ONE Ken-only action: request the Oregon DOR\n"
                "      developers' handbook, draft forms and test scenarios\n"
                "      (electronic.filing@dor.oregon.gov / 503-945-8415). D-12 A5 DECIDED to\n"
                "      send it. IT HAS NOT BEEN SENT.\n\n"
                "  (3) U24 IS UNPULLED AND IT BLOCKS OR_20_S LINE 15. ORS 314.772 carries a\n"
                "      2025-session amendment (2025 c.36 s.3) - the ONLY load-bearing ORS\n"
                "      section in the Oregon brief with one - and its applicability date was\n"
                "      never run down. Pull 2025 Or. Laws ch. 36 s.3 from OLIS first.\n\n"
                f"READY_TO_SEED = {READY_TO_SEED} (must be True to proceed)\n\n"
                f"Currently empty / placeholder:\n  {still_empty}\n\n"
                "DO NOT RELAX THIS GUARD TO SILENCE THE ERROR - fix the cause, which in every\n"
                "case above means getting an answer from the Oregon DOR, not editing this file.\n"
                "References: delvio-states/research/or_pte_source_brief.md (its SEC. 18\n"
                "VERIFICATION SECTION GOVERNS over the body) and delvio-states/DECISIONS.md D-12.\n"
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
                # Oregon's Tier-1 conformity rows ARE seeded in prod (campaign D-10,
                # conformity_type = 'partial'), so this must not fire there. It WILL
                # fire on a throwaway SQLite harness DB, which is expected.
                self.stdout.write(self.style.WARNING(
                    f"  existing source {code} NOT FOUND - links to it will be skipped "
                    "(expected only on a fresh/throwaway DB; OR Tier-1 conformity is seeded in prod)"))
        self.stdout.write(f"Sources ready: {len(sources)}")
        return sources

    def _upsert_form(self, identity: dict) -> TaxForm:
        form, created = TaxForm.objects.update_or_create(
            form_number=identity["form_number"], jurisdiction=FORM_JURISDICTION,
            tax_year=FORM_TAX_YEAR, version=FORM_VERSION,
            defaults={"form_title": identity["form_title"],
                      "entity_types": identity["entity_types"],
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
        self.stdout.write("\n" + "=" * 72)
        self.stdout.write("Oregon PTE specs loaded (TY2025).")
        for spec in FORMS:
            fn = spec["identity"]["form_number"]
            self.stdout.write(
                f"  {fn}: facts {len(spec['facts'])} / rules {len(spec['rules'])} / "
                f"lines {len(spec['lines'])} / diag {len(spec['diagnostics'])} / "
                f"tests {len(spec['scenarios'])} / links {len(spec['rule_links'])}"
            )
        self.stdout.write(
            f"  shared: flow assertions {len(FLOW_ASSERTIONS)} / sources {len(AUTHORITY_SOURCES)} / "
            f"topics {len(AUTHORITY_TOPICS)} / individual codes {len(OR_CODES_INDIVIDUAL)} / "
            f"corporate codes {len(OR_ASC_CORP_CODES)} / corporate credit codes {len(OR_ASC_CORP_CREDIT_CODES)} / "
            f"colliding codes {OR_COLLISION_COUNT}"
        )
        self.stdout.write("=" * 72)
