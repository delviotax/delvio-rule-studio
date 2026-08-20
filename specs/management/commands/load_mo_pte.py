"""Load the Missouri PTE specs — Form MO-1065, Form MO-1120S and Form MO-PTE (TY2025).

═══════════════════════════════════════════════════════════════════════════
WHAT THIS IS
═══════════════════════════════════════════════════════════════════════════
Missouri needs THREE pass-through specs:

  MO_1065     Form MO-1065,  Partnership Return of Income            (1065)
  MO_1120S    Form MO-1120S, S Corporation Income Tax Return         (1120S)
  MO_PTE      Form MO-PTE,   Pass-Through Entity Income Tax Return   (1065 + 1120S)

⚠⚠ **MO_PTE IS FILED IN ADDITION TO MO_1065 / MO_1120S, NOT INSTEAD OF THEM.**
This is the OPPOSITE of Virginia's Form 502 / Form 502PTET fork and **the
Virginia pattern must NOT be ported.** It is settled by PUBLISHED DOR AUTHORITY,
not by inference — DOR *FAQs — Pass-Through Entity Tax*, verbatim:

    Q: "If a partnership or S corporation elects to file a MO-PTE return,
        should it still file a MO-1065 or MO-1120S?"
    A: "Yes. The filing of the MO-PTE does not substitute for a partnership
        filing its MO-1065 or an S corporation filing its MO-1120S."

The forms corroborate it: MO-PTE Page 3 Part A **Line 3** (addition) and
**Line 9** (subtraction) both read *"Enter the share of fiduciary and
partnership adjustment as shown on Form MO-1041, Page 2, Part 1, Line 19
[Line 20], and Form MO-1065, Line 11 [Line 12]. Copies of any Forms MO-1041 or
MO-1065 must be attached."* — the elective return FEEDS OFF a filed MO-1065.
**Porting the VA fork would leave every electing Missouri client's filing
incomplete.** Encoded at R-MO-BOTH-FILED / FA-MO-BOTH-FILED and pinned in the
harness.

Spec source: `delvio-states/research/mo_pte_source_brief.md` — VERIFIED
(adversarial pass 2026-08-19, plus a U4 follow-up addendum of the same date).
⚠ **ITS §22 VERIFICATION SECTION GOVERNS OVER THE BODY**, and **§22.11 (the U4
follow-up addendum) governs over §§2.2, 18, 19, 21.4 and 22.5/22.9/22.10.**
This loader follows §22 everywhere, and §22.11 where it is later still.
Conformity: `delvio-states/conformity/mo_conformity.md` (VERIFIED 2026-08-06);
its §12 governs over its body.

NO prior RS spec exists — `lookup/MO_1065/`, `/MO_1120S/`, `/MO_PTE/` all
returned 404 on 2026-08-17 and again on 2026-08-20, and `specs/management/
commands/` holds no `load_mo_*`. All three are greenfield; `<ST>_<FORM>` per
campaign D-9. ⚠ They must NEVER be shortened to `1065` / `1120S` — RS already
holds FEDERAL `load_1065_schedule_k.py` and `load_1120s_complete.py`, and the
lookup does not filter by jurisdiction.

═══════════════════════════════════════════════════════════════════════════
⚠ HOW THE SUB-SPECS ARE CARRIED — campaign D-12, Group B
═══════════════════════════════════════════════════════════════════════════
D-12 ratified **THREE top-level codes**, with **Form MO-MS PTE and Schedule
PTE-BD as their own sub-specs because they COMPUTE**, and the remaining
companions as attachment/record types. That produces exactly THREE `TaxForm`
rows, so the sub-specs live inside their parent spec in their own reserved
line/rule/fact namespaces:

  inside MO_PTE     `MS-*`   Form MO-MS PTE   (Part 1 Lines 1-9; computes)
                    `BD-*`   Schedule PTE-BD  (Lines 1-9, Cols A/B/C; computes)
  inside MO_1065    `NRP-*`  Form MO-NRP      (Parts 1/2/3; attachment/record)
                    `NR-*`   MO-1NR / MO-2NR / MO-3NR withholding leg
  inside MO_1120S   `NRS-*`  Form MO-NRS      (Parts 1/2; attachment/record)
                    `MSS-*`  Form MO-MSS      (Part 1 Lines 1-10; the S-corp
                             apportionment schedule that PARTNERSHIPS ALSO
                             BORROW — see the U4 section below)
                    `NR-*`   the same withholding leg

⚠ `TaxForm` count is THREE and the harness pins it. A later contributor who
adds a fourth Missouri `TaxForm` row for MO-MS PTE or PTE-BD has re-litigated
D-12 Group B.

═══════════════════════════════════════════════════════════════════════════
⚠⚠ A6 (campaign D-12) — THE E-FILE INVERSION AND THE PRIVACY RULING
═══════════════════════════════════════════════════════════════════════════
**Form MO-PTE cannot be filed through MeF and its tax cannot be paid
electronically. Forms MO-1065 and MO-1120S CAN be e-filed. THE TAX-COMPUTING
RETURN IS THE MANUAL ONE, AND MeF SCOPE HALVES.**

Settled SIX independent ways (brief §2.3 / §22.2 A), attacked from the
falsifying (MeF/approved-software) direction and unbroken:
  1. DOR PTE FAQ, re-pulled 2026-08-19, verbatim: *"No. You must submit your
     return Form MO-PTE to PO Box 3080, Jefferson City, MO 65105-3080, or by
     email to pteincome@dor.mo.gov."* and, for payment: *"No. You must submit
     your payment with Form MO-PTEV or MO-PTEAP with a check, money order, or
     cashier's check to PO Box 3080..."*
  2. The MO-PTE form face, ModDate **2026-03-31** — the NEWEST document in the
     lane — prints a mailing address and an e-mail address and NOTHING ELSE.
  3. A 9-page sweep of the MO-PTE instructions: `electronic` occurs EXACTLY
     ONCE, in the $100,000-refund context at Line 23.
  4. The DOR **Partnership e-file page** names only MO-1065.
  5. The DOR **Corporation-income e-file page** names only MO-1120 and
     MO-1120S; its 22-vendor approved list is scoped to those two returns.
  6. **Drake Software KB 18013**, independent commercial confirmation:
     *"Form MOPTE and the MOPTE Voucher are not e-fileable and there are no
     options for electronic payments this year."*

⚠ **PRECISION THAT §22 IMPOSES: "paper-only" OVERSTATES IT.** E-mailing a PDF
to `pteincome@dor.mo.gov` is a Department-sanctioned channel. The accurate
formulation is **"not e-fileable through MeF, and not electronically
payable."** (And MO-PTEAP's *"By submitting a check, you authorize the
Department of Revenue to process the check electronically"* is CHECK
CONVERSION, not electronic payment — do not read it as contradicting this.)

⭐ **A6 IS A PRIVACY RULING, NOT A TAX ONE. DELVIO DOES NOT AUTOMATE THE
DEPARTMENT'S E-MAIL SUBMISSION CHANNEL.** That channel carries member SSNs in
the clear. **Delvio computes and assembles; the preparer chooses the channel.**
`MO_AUTOMATE_EMAIL_SUBMISSION` is `False`, `mo_submission_channels()` REFUSES
to mark the e-mail channel automatable, and the harness pins both.
MO_PTE therefore rides the **substitute-forms track** (Form 4349 letter of
intent + Form 5629 guidelines + the 10x6 grid + the 2-D barcode spec), not the
MeF track.

═══════════════════════════════════════════════════════════════════════════
⚠⚠ VERIFIED NEGATIVE — NO DEPRECIATION SHADOW BOOK, NO MISSOURI §179 CONSTANT
    (campaign D-12, Group B) — CLOSED AT THE STATUTE, NOT AT THE FORM FACES
═══════════════════════════════════════════════════════════════════════════
**There is no §168(k) bonus add-back and no §179 modification in Missouri for
any property placed in service after 30 June 2003. 100% OBBBA bonus flows
straight through. There is NO Missouri shadow depreciation book and NO Missouri
§179 constant may EVER be encoded.**

This is a *"the rule says no"*, established from the ADD-BACK PROVISION ITSELF:

  §143.121.**2(3)** — the §168 add-back — is window-limited ON ITS FACE to
      property purchased *"on or after July 1, 2002, but before July 1, 2003"*,
      and is expressly measured against §168 *"as amended by the Job Creation
      and Worker Assistance Act of 2002."*
  §143.121.**3(7)** — the matching subtraction — carries the IDENTICAL window.
  §143.121.**3(9)** — disposition recovery — is expressly tied to *"an
      additional modification ... made under subdivision (3) of subsection 2 of
      this section,"* inheriting the same window.
  §143.121 contains **NO §179 modification at all.** §179 appears in the whole
      Missouri PTE lane ONLY as a *distributive-share item*:
      MO-NRP Part 1 **Line 12**, MO-NRS Part 1 **Line 11**, Schedule PTE-BD
      **Line 6** — all three re-verified positionally on the verification pass.

**THERE IS NO OPEN-ENDED BONUS ADD-BACK IN MISSOURI LAW TO FIND.** Missouri
takes the federal OBBBA §179 figures by default in all three returns with no
state recomputation. ⚠ **DO NOT PORT VIRGINIA'S DERIVED STATE §179 FIGURE**
(`va_pte_source_brief.md` W3) and **do not create a nullable "state
depreciation adjustment" field for symmetry with other states** — a nullable
field a preparer can fill is worse than no field at all.

⚠ Scoping correction §22 imposes: the brief's *"confirmed on five form faces"*
overstated the FORM-side support. FOUR faces carry a depreciation line
(MO-1065 L9, MO-1120S L10+L11, MO-NRP Pt 2 L9, MO-NRS Pt 2 L10+L11); the
2002-03 window is spelled out **in words in exactly ONE document** (the
MO-1120S instructions); the other three rely on the bare statutory cite. The
negative does not depend on that framing — it rests on §143.121.2(3).

⭐ **MO-PTE HAS NO DEPRECIATION LINE AT ALL**, and its 9-page instructions are
silent too (`depreciat|168|179|bonus` -> zero hits on both). The live 2002-03
residual therefore has NOWHERE TO GO on Form MO-PTE except the Line 9
*"Other adjustments"* write-in (U18). The mirror image is worse on MO-1065,
which has the .3(7) basis line but **no .3(9) disposition-recovery line** while
MO-1120S has both (U19). Both are encoded as RED-DEFER R5 with their own
diagnostics.

`MO_SECTION_179_STATE_LIMIT` is `None` and `mo_section_179_state_limit()`
RAISES rather than returning a number. `MO_HAS_BONUS_ADDBACK` is `False`.
The harness pins the ABSENCE so nobody later adds a field "for symmetry."

═══════════════════════════════════════════════════════════════════════════
⚠⚠ C3 + THE U4 FOLLOW-UP — THREE SOURCING REGIMES, AND WHICH DIAGNOSTIC FLIPS
═══════════════════════════════════════════════════════════════════════════
D-12 C3 approved: **three sourcing regimes, do NOT force them to reconcile.**
⚠ **BUT the U4 follow-up (brief §22.11, 2026-08-19) CHANGED THIS MATERIALLY
and §22.11 GOVERNS.** 12 CSR 10-2.190 was finally pulled from the Missouri
Secretary of State capture of chapter 12 CSR 10-2 (the official one; the DOR
copy was deliberately not used). Vintage-checked: .190 last amended filed
2024-01-24, eff. **2024-09-30** — before TY2025, with no amendment for or after
TY2025; 12 CSR 10-2.255 filed 2020-09-08, eff. **2021-03-30**, NEVER AMENDED.
Both texts ARE the TY2025 texts.

**.190 does not decide sourcing — (2)(C) DELEGATES to 12 CSR 10-2.255**, whose
**(3)** puts partnership nonresident-partner sourcing on **§143.455 — identical
to S corporations** — for all tax years beginning on or after 2020-01-01.
(4) supplies the bridge: *"any references in section 143.455, RSMo to the term
'corporation' shall be deemed to refer instead to the type of entity to which
this regulation is applied."* (1)(B) pins the factor to §143.455.**10**.

**CONSEQUENCE 1 — A DIAGNOSTIC'S MEANING FLIPS.** The **MO-NRP <-> MO-MS PTE
divergence is now EXPECTED-ZERO, not expected-nonzero.** The diagnostic stays,
but a non-zero delta now reads as a **PROBABLE ERROR** (or an unapproved MO-NRP
Part 3 election), NOT as normal regime disagreement. Encoded that way at
`mo_sourcing_divergence()` / `D_MO_NRP_MSPTE_DELTA` / FA-MO-U4-ZERO.
The MO-NRP -> MO-MSS cross-reference is DELIBERATE, not an editorial slip —
.255 makes the two entity types one rule, which is why NO `MO-MSP` WAS EVER
PUBLISHED. It is a HIERARCHY, not an election.

**CONSEQUENCE 2 — THE REAL COLLISION SURVIVES UNTOUCHED.** §143.455 (MO-PTE
**Line 5**, via MO-MS PTE) versus Schedule PTE-BD Column (C)'s qualitative
*"In general, if the 'brains' of the operation resulting in the item are
located in Missouri, that item is from Missouri sources"* test (**Line 6**).
**ADJACENT LINES on the same return, feeding the same Line 9. U17 STAYS FULLY
OPEN.** Neither .190 nor .255 mentions the brains test. **THAT pair must NOT be
forced to reconcile** — `D_MO_L5_L6_SOURCING` is an informational,
non-reconciling diagnostic and `mo_sourcing_divergence()` REFUSES to compute a
reconciliation for it.

**CONSEQUENCE 3 — NARROWED-BUT-OPEN, AND IT IS A GATE-1 SEED QUESTION.** The
**regulatory basis for MO-NRP Part 3 direct accounting.** 12 CSR 10-2.255 is a
closed TWO-branch test (apportioned or allocated, both under §143.455) with
**NO separate-accounting branch**, yet MO-NRP Part 3 prints one and offers it
whenever *"accompanying records clearly reflect income from Missouri sources."*
The only statutory room is §143.421.4: *"The director of revenue may, **on
application**, authorize the use of such other methods..."* — and **NOTHING on
the form, in its embedded instructions, or in either regulation mentions an
application, a petition, or a director's approval.** ⚠ **DO NOT DEFAULT PART 3
TO A FREE PREPARER ELECTION.** `MO_NRP_PART3_STATUS` is
`"GATE-1 SEED QUESTION - NOT A FREE ELECTION"`, `mo_nrp_part3_available()`
RETURNS `False` with the question attached, and `D_MO_NRP_PART3_BASIS` carries
it. The guard names it as a reason to refuse.

**NEGATIVE FINDING TO RECORD:** a regulation under §143.181 governing
partnership sourcing **DOES NOT EXIST.** The whole of 12 CSR 10-2 was searched:
only 12 CSR 10-2.010 (Missouri AGI / spousal allocation — unrelated) and the
**RESCINDED** 12 CSR 10-2.130 (*Rescinded March 30, 2024*) cite §143.181
authority. U4's second *"would settle it"* asked for a regulation that does not
exist. §143.581's §143.181 reference is a RETURN-FILING TRIGGER, not a
computation method — §143.421.1 says the part is determined *"under regulations
prescribed by the director of revenue"*, and the director's regulation says
§143.455. ⚠ This CORRECTS the framing in brief §2.2.

═══════════════════════════════════════════════════════════════════════════
⚠⚠ C11 — THE MO-MS PTE MILEAGE NOTE IS DEFECTIVE FOR **TWO** METHODS
═══════════════════════════════════════════════════════════════════════════
The brief's own correction C3 was itself wrong and D-12 C11 ordered it
restated **before it propagates**. §143.455 was pulled verbatim:

  **Method Three — Transportation, §143.455.14** — *"...shall report its
     **gross earnings** within the state on intrastate business and shall also
     report its gross earnings on all interstate business done in this state...
     This subsection shall not apply to a railroad."*  -> **GROSS EARNINGS,
     NOT MILEAGE.**
  **Method Four — Railroad, §143.455.15** -> **MILEAGE** (or an elective
     investment ratio in fixed transportation facilities).
  **Method Five — Interstate Bridge, §143.455.16** — *"shall include in its
     Missouri taxable income **one-half** of the net income from the operation
     of a bridge between this and another state"* -> **FLAT ONE-HALF.**
  **Method Six — Telephone and Telegraph, §143.455.17** -> **MILEAGE** (or an
     elective investment ratio).

**ONLY FOUR AND SIX ARE MILEAGE-DRIVEN.** The MO-MS PTE face note *"Complete
mileage information below for Method Three - Six"* is therefore defective for
**TWO** methods — **Three AND Five** — not one. Corroborated by 12 CSR
10-2.045(14)(B). Encoded in `MO_APPORTIONMENT_METHODS`, pinned by
FA-MO-C11-MILEAGE, and surfaced at `D_MO_MILEAGE_NOTE_DEFECT`.

═══════════════════════════════════════════════════════════════════════════
⚠⚠ TWO LIVE CLIENT-HARM PATHS — BOTH MISSOURI, BOTH STATED ONLY IN REGULATIONS
═══════════════════════════════════════════════════════════════════════════
**C5 — USING AN ENTITY-LEVEL MO-TC CREDIT DESTROYS THE MEMBERS' CREDIT.**
Three sources say the same thing:
  MO-PTE instructions, Line 11: *"In general, miscellaneous tax credits reduce
    tax liability under the SALT Parity Act, rather than constituting tax paid,
    and therefore do not qualify as payments for purposes of calculating the
    PTE credit for a member."*
  MO-PTE Part B Column 6: the member's credit is the pro rata share of Line 12
    *"to the extent paid."*
  12 CSR 10-2.436(11): *"...computed based on the member's direct and indirect
    pro rata share of **the tax actually paid** ... If an affected business
    entity reduces its tax liability under section 143.436, RSMo, by use of tax
    credits, other than a credit for payment or overpayment of this tax, the
    affected business entity's tax actually paid will generally be reduced."*
**THE FORM HAS NO FIELD FOR "TAX ACTUALLY PAID."** A DERIVED FIELD
(`mo_tax_actually_paid()`) feeds Part B Column 6, and `D_MO_TC_POISONS_CREDIT`
is a **HARD (error-severity) diagnostic whenever Line 11 > 0.**
**This is a live client-harm path, not a rounding item.** (U20)

**C6 — THE PTE ELECTION DOES *NOT* SWITCH OFF NONRESIDENT WITHHOLDING.**
12 CSR 10-2.436(8), verbatim, word for word: *"The election to become an
affected business entity does not relieve a partnership or S corporation of its
withholding obligations under section 143.411.5, RSMo, or section 143.471.6,
RSMo, respectively."* ⚠ It is stated **ONLY in the regulation** — nowhere on
Form MO-PTE, nowhere in its instructions, nowhere in the DOR FAQ. **An electing
Missouri partnership pays 4.7% entity tax AND withholds 4.7% on the same
income.** The withholding leg is BUILT INTO THE ELECTING PATH
(`mo_withholding_required()` ignores the election) with
`D_MO_WH_SURVIVES_ELECTION` citing the regulation. (U21)

═══════════════════════════════════════════════════════════════════════════
⚠⚠ C4 / D-10 — THE CAPITAL-GAIN TRAP IS ADVICE LAYER. **ENCODE NOTHING.**
═══════════════════════════════════════════════════════════════════════════
**Campaign D-10 (2026-08-16) RULED THE SPEC QUESTION: BUILD TO THE FORM.**
No entity-level capital-gain subtraction, anywhere. This loader documents the
conflict and DOES NOT RE-OPEN IT.

⭐ Supporting fact verified on the adversarial pass: the MO-PTE form was
**re-stamped 2026-03-31** — AFTER the 2025 session that enacted
§143.121.3(14), AFTER HB 594/508 was signed, and AFTER the amended SALT-Parity
regulation took effect 2025-09-30 — and **STILL HAS NO CAPITAL-GAIN LINE.**
Its Part A subtraction list is a CLOSED ENUMERATED LIST, Lines 6-11.

⭐ And §22 found the leg the brief missed, which **STRENGTHENS D-10 rather than
merely confirming it**: §143.121.3(14) has a **SECOND PRONG.**
  *"(b) For all tax years beginning on or after January first of the tax year
  following the tax year in which the top rate of tax imposed pursuant to
  section 143.011 is equal to or less than four and one-half percent, one
  hundred percent of all income reported as a capital gain for federal income
  tax purposes **by an entity subject to tax pursuant to section 143.071**."*
The General Assembly DID legislate entity-level capital-gain relief —
expressly, separately, and **deliberately DEFERRED** behind a rate trigger.
TY2025's top rate is **4.7%, so (b) is NOT operative.** If §143.436's import of
§143.121 already delivered entity-level relief, **(b) would be superfluous.**
⚠ **STALENESS TRIPWIRE:** when Missouri's top individual rate reaches **<= 4.5%**,
(14)(b) switches on for §143.071 entities THE FOLLOWING TAX YEAR.
`mo_capital_gain_entity_relief_active()` is tax-year-keyed and
`D_MO_CAPGAIN_TRIGGER_TRIPWIRE` carries it.

**C4 RULING, ENCODED LITERALLY: ENCODE NOTHING.** No optimiser, no
recommendation, no automatic election, no computation of the harm.
`mo_capital_gain_advisory()` returns TEXT AND CITATIONS ONLY — it takes no
amounts, computes no comparison, and REFUSES to recommend. It fires when an
electing entity's Line 1 carries material capital gain and a Missouri
individual member exists; it states the interaction in the DEPARTMENT'S OWN
TERMS, cites §143.121.3(14) and §143.436, **AND STOPS.**
(`D_MO_CAPGAIN_ELECTION_TRAP`, severity `info`, preparer-facing.)

⚠ U16 compounds it and cuts the OPPOSITE way: Schedule PTE-BD Column (A)
excludes from the BID base *"any business income that would, ignoring Section
143.022, RSMo, be subtractable or deductible for individual partners or
shareholders in arriving at their Missouri taxable incomes"* — which on its
face removes owner-exempt capital gain from the DEDUCTION while it stays in the
TAX base. Recorded, not computed.

═══════════════════════════════════════════════════════════════════════════
D-12 GROUP D — THE RATIFICATIONS THAT BIND THIS FILE
═══════════════════════════════════════════════════════════════════════════
* **THE OPT-OUT IS A RETURN-LEVEL RECOMPUTATION MODE, NOT A MEMBER FLAG.**
  12 CSR 10-2.436(12)(D) forces a full recomputation of Line 1, every
  modification, Schedule PTE-BD and the credit split **as though the opt-out
  member's items did not exist.** ⚠ **STORE THE K-1 PERCENTAGE AND THE
  CREDIT-ALLOCATION PERCENTAGE AS TWO SEPARATE FIELDS AND NEVER OVERWRITE ONE
  WITH THE OTHER.** MO-PTE Part B Column 5 is labelled `Membership %` but
  silently changes MEANING when any member opts out. DOR's own worked example
  is the unit test: an opt-out member at 30% and a participating member at 10%
  gives the participating member **14% (10 divided by 70)**.
  `mo_member_percentages()` returns BOTH fields and the harness proves they are
  distinct objects. (FA-MO-OPTOUT-1070)
* **MO-PTE LINE 5 = `L4 x round(L9, 3)`** per the printed instruction — the
  ROUNDED PRODUCT WINS over the directly-computed MO-MS PTE Line 8 — with a
  **HARD RED on `L4 <= 0`.**
  ⚠⚠ **WORDING DEFECT IN THE RULING AS RESTATED, RESOLVED HERE AND ESCALATED:**
  the ruling as handed down says *"MO-MS PTE Line 5 = L4 x round(L9, 3)"*, but
  **MO-MS PTE's OWN Line 5 is `Nonapportionable income - Everywhere`** — a
  direct-entry dollar amount that is an INPUT to Line 6, not a product. The
  formula belongs to **MO-PTE Line 5** (`Preliminary Missouri net income`),
  whose face reads *"Multiply Line 4 by the percentage"*, using MO-MS PTE
  Line 4 (= MO-PTE Line 4) and MO-MS PTE Line 9. This file encodes the
  SUBSTANTIVELY CORRECT version, keeps MO-MS PTE Line 5 as the direct-entry
  input it is, and carries `D_MO_L5_WHICH_LINE5` so the ambiguity cannot
  silently propagate. **Escalated rather than papered over.**
* **SCHEDULE PTE-BD LINE 8 BUILDS SUM-THEN-FLOOR** — `max(0, sum(C1..C7))` —
  supported by §143.022.1's *"the income greater than zero ... limited to the
  **Missouri source net profit from the combination of**"*. The alternative
  reading (drop the negative rows, then sum) is RECORDED, not built, and
  `pte_bd_line8()` returns BOTH figures with only one labelled operative.
  A diagnostic fires whenever any Column (C) row is negative. (U15)
* **WITHHOLDING EXCEPTIONS BUILD TO THE NARROW, CONJUNCTIVE FORM READING**, and
  that is **RECORDED AS A RULING, NOT A FINDING.** §143.411.5 lists five
  exceptions with **"or"** before (5); every FINAL form collapses (3)(4)(5)
  into ONE conjunctive test. The literal statutory "or" would exempt from
  withholding **every partnership that made no distributions in two years** —
  i.e. most closely-held partnerships. Build to the form, per D-10's principle.
  (U22)
* **FORM MO-PTE OPT-OUT PRINTS THE WRONG SCANLINE** — barcode `*25329010001*`
  (which is **Form MO-3NR's**) over human-readable `25125010001`, on a FINAL
  form re-stamped 2026-03-27. **PRINT NO SCANLINE AT ALL ON THIS FORM IN v1** —
  reproducing a wrong barcode is worse than omitting one. (U27)
* **METHOD SEVEN'S PETITION DEADLINE IS 60 DAYS *BEFORE* YEAR END**, so it is
  closed before the return is prepared: **ADVISORY DIAGNOSTIC ONLY, NEVER A
  FILING-TIME GATE.** ⚠ §22 correction #10: the deadline is **in the
  REGULATION** (12 CSR 10-2.076(2)(G), *"at least sixty (60) days before the
  end of the tax year"*), so it binds ALL THREE lanes — the narrower
  observation that the MO-1120S / MO-MSS text omits it is itself a DOR defect.
* **NO ESTIMATED-TAX SUBSYSTEM EXISTS AT ALL — BUT KEEP INTEREST AND THE 5%
  LATE-PAY ADDITION.** 12 CSR 10-2.436(7) is a POSITIVE RULE (*"is not subject
  to an estimated income tax declaration filing requirement, or an estimated
  income tax payment requirement"*), corroborated by the FAQ and by MO-PTEAP's
  own face (*"These anticipated tax payments are not required."*). ⚠ §22
  correction #9: *"no underpayment-penalty regime AT ALL"* OVERREACHED. What is
  absent is the ESTIMATED-TAX regime and any MO-2210 / Form 500C analogue.
  What SURVIVES: interest under §143.731.2 (expressly preserved by 12 CSR
  10-2.436(9)) and the **5% late-payment addition**.

═══════════════════════════════════════════════════════════════════════════
ALSO RECORDED (D-12, Group D and Group E)
═══════════════════════════════════════════════════════════════════════════
* **KC / ST. LOUIS EARNINGS TAXES ARE OUT OF SCOPE — BUT THE STATE MODULE MUST
  KNOW THEY EXIST**, because their carve-out is PRINTED ON ALL THREE FORM FACES
  at **Line 1b**, where they are subtracted from the state-and-local-tax
  add-back. INFO diagnostic (R15), never RED, never computed.
* **FORM 5889'S COLUMN REFERENCES ARE ONE COLUMN STALE, AND THE SHIFT HAPPENED
  IN TY2024** — a full year earlier than first thought. §22 correction #2
  REFUTED the brief's causal claim by pulling TY2022/23/24 MO-PTE: TY2022-23
  Part B ran `1 Name | 2 nonresident | 3 SSN | 4 Membership % | 5 Credit` (5889
  was CORRECT then); **TY2024** inserted Column 3 (opt-out), pushing SSN->4,
  Membership %->5, Credit->6; TY2025 changed only the Column 6 LABEL
  (`Shareholder's` -> `Member's`). Form 5889 was revised **03-2025 — AFTER the
  shift** — so this is a **PERSISTED defect through a full revision cycle, not
  a publication lag.** **GENERATE A DELVIO MEMBER REPORT** (Form 5889 is
  optional — *"may be used"* / *"can be utilized ... as an alternative to a
  report generated by the company"*) and **map Form 5889 BY SUBSTANCE, NOT BY
  ITS STALE COLUMN NUMBERS**: 5889 Line 1 <- Part B **Column 5**, 5889 Line 2
  <- Part B **Column 6**. Never reproduce the stale numbers in help text.
* **THE WITHHOLDING BASE SUMMATIONS ARE DEFECTIVE AS PRINTED.** MO-1NR defines
  the base as *"the net total of the amounts listed on Lines 1 through 11 of
  ... Form MO-NRP"* and *"Lines 1 through 10 of ... Form MO-NRS"*.
    - **MO-NRS Lines 1-10 DOUBLE-COUNT**: `5b Qualified dividends` is a SUBSET
      of `5a Ordinary dividends`, and `8b Collectibles (28%) gain` and
      `8c Unrecaptured section 1250 gain` are both SUBSETS of `8a Net long-term
      capital gain`. A literal sum overstates the base by `5b + 8b + 8c`.
    - **MO-NRP Lines 1-11 SILENTLY EXCLUDE** Line 12 (§179), Line 13
      (contributions) and Line 13e (other deductions), because the DOR's own
      line numbering is non-contiguous (`1, 2, 3c, 4a, 5, 10, 11, 12, 13, 13e`).
  **BUILD WITH THE SUBSET LINES SUPPRESSED**, and raise
  `requires_human_review` on ANY return where `5b`, `8b` or `8c` is non-zero.
  **This determines cash withheld on real returns.** (U9)
* **§105.1500 RSMo** is printed on **Form MO-PTE page 4 AND Form MO-TC page 2**:
  the Department **may not require** a list identifying a person as a member,
  supporter, volunteer or donor of a §501(c) entity, *"notwithstanding any
  publication, webpage, form, instruction, regulation, or statement shared by
  the Department."* It collides head-on with MO-PTE Part B Column 1's *"Name of
  each member. **All must be listed.**"* ⚠ **DO NOT SILENTLY SUPPRESS AND DO
  NOT SILENTLY INCLUDE.** Surface it as a PREPARER DECISION with the statutory
  text as help copy, and **NEVER AUTO-POPULATE A §501(c) MEMBER'S IDENTITY
  WITHOUT EXPLICIT CONFIRMATION.** `mo_501c_roster_decision()` returns
  `"PREPARER DECISION"` and REFUSES to auto-populate. (R13 / W17)

═══════════════════════════════════════════════════════════════════════════
THE SEVEN THINGS MOST LIKELY TO BE BUILT WRONG (all encoded as real branches)
═══════════════════════════════════════════════════════════════════════════
1. ⚠⚠ **FILING MO-PTE *INSTEAD OF* MO-1065 / MO-1120S** — the Virginia fork.
   Published DOR authority says both are filed. FA-MO-BOTH-FILED.
2. ⚠⚠ **SWITCHING OFF NONRESIDENT WITHHOLDING WHEN THE ELECTION IS MADE** —
   costs the client cash twice on the same income. 12 CSR 10-2.436(8).
3. ⚠⚠ **TREATING MO-PTE LINE 12 AS THE MEMBERS' CREDIT POOL WHEN MO-TC WAS
   USED** — Column 6 says *"to the extent paid"* and MO-TC use is not payment.
4. ⚠ **SHARING ONE RULE BETWEEN MO-NRP AND MO-NRS.** Their column derivations
   are STRUCTURALLY OPPOSITE: MO-NRP computes **`(c) = (b) / (a)`**; MO-NRS
   computes **`(b) = (a) x (c)`** with `(c)` supplied by MO-MSS Line 3. Two
   identical-looking five-column grids, two inverse arithmetics.
5. ⚠ **STORING ONE APPORTIONMENT PERCENTAGE PER RETURN.** MO-MSS's printed
   six-step example produces a **PER-DISTRIBUTIVE-SHARE-ITEM percentage**:
   *"If a distributive share item is wholly or partially allocated as
   nonapportionable income, a different percentage will be computed for the
   item."* MO-NRS Column (c) is a **VECTOR indexed by line**, defaulting to the
   Line 3 receipts factor. A scalar model is wrong.
6. ⚠ **PUTTING AGRICULTURE DISASTER RELIEF INSIDE THE TOTALS ON THE WRONG
   FORM.** On MO-1065 (**Line 13**) and MO-1120S (**Line 15**) it sits BELOW
   the net-adjustment lines, OUTSIDE the totals, and is separately allocated to
   owners with its own schedule landing on **MO-A Part 1 Line 16**. On MO-PTE
   (**Line 10**) it is INSIDE the Line 12 subtraction total and reduces the
   entity's tax base directly. Same statute, three placements, two behaviours.
   ⚠ And §22 correction #11: the DOR SPELLS IT TWO WAYS — MO-1065 L13 and
   MO-1120S L15 print `Agriculture Disaster Relief`; **MO-PTE L10 prints
   `Agricultural Disaster Relief`.** Transcribe each face's own spelling.
7. ⚠ **APPLYING THE $500 RELATED-EXPENSE RULE AS A THRESHOLD ON THE
   SUBTRACTION.** It is a **FLOOR ON THE EXPENSE**: *"The expenses must equal
   or exceed $500. If less than $500, enter zero."* — i.e. below $500 the
   EXPENSE is dropped and the GROSS amount survives, which makes the
   subtraction LARGER, not smaller.

═══════════════════════════════════════════════════════════════════════════
VERIFIED-NEGATIVE INVENTORY — encode the ABSENCE deliberately (pinned in the
harness so a later contributor cannot quietly add a field "for symmetry")
═══════════════════════════════════════════════════════════════════════════
N1  NO §168(k) bonus add-back and NO Missouri §179 cap, phaseout or constant,
    anywhere in the Missouri PTE lane, for any property placed in service after
    30 June 2003. Closed at §143.121.2(3) — the add-back provision ITSELF is
    window-limited. NO shadow depreciation book. (See the banner above.)
N2  NO estimated-tax declaration or payment requirement, and therefore NO
    MO-2210 / Form 500C analogue and no exception ladder. 12 CSR 10-2.436(7) is
    a POSITIVE rule. ⚠ But interest (§143.731.2) and the 5% late-payment
    addition SURVIVE.
N3  NO conformity-adjustment bucket of any kind. Missouri is ROLLING
    (§143.091, eff. 1/1/1990, unamended), so OBBBA applies for TY2025 with no
    adoption act — none was needed and none was enacted. There is no Missouri
    analogue of a fixed-date conformity line, and the modification blocks
    contain NO conformity line at all.
N4  NO capital-gain subtraction line on Form MO-PTE. The Part A subtraction
    list is a CLOSED ENUMERATED LIST, Lines 6-11, on a face re-stamped
    2026-03-31. (D-10. Do not add one.)
N5  NO depreciation line of ANY kind on Form MO-PTE — neither the
    §143.121.3(7) basis adjustment nor the §143.121.3(9) disposition recovery.
N6  NO Food Pantry add-back on Form MO-PTE, although MO-1065 Line 4 and
    MO-1120S Line 4 both carry one. An electing entity's Line 1 base therefore
    RETAINS a federal deduction that the non-electing returns add back.
N7  NO §163(j) machinery on MO-1065 — neither the §143.121.2(6) carryforward
    addition nor the §143.121.3(11) disallowed-interest subtraction, on the
    face or in the embedded instructions (full-text search for `163` -> ZERO
    hits). MO-1120S folds both into Lines 3 and 9 BY INSTRUCTION; MO-PTE gives
    each its OWN line (4 and 11). (U7)
N8  NO MOHELA subtraction line on MO-1065. MO-1120S Line 8 and MO-PTE Line 8
    both have one.
N9  NO §143.121.3(9) disposition-recovery line on MO-1065. MO-1120S Line 11
    has one. (U19)
N10 NO Missouri K-1. There is no `MO-K-1` and never has been. Each return
    carries a PER-OWNER EXTRACT OBLIGATION instead, and the owner keys the
    figures onto MO-1040 / MO-A / MO-NRI. **SIX different owner-side landing
    points across three returns.**
N11 NO composite checkbox on MO-1120S, although §143.471.5 grants S
    corporations the same right and the MO-1120S instructions list composite
    election as a withholding exception. MO-1065 HAS one. (U23)
N12 NO long-term capital gain row on MO-MSS Part 1 Lines 4-10 — only
    `7 Net Short-Term Capital Gain (Loss)` — although §143.455.7 allocates
    capital gains generally. It rides on an unstructured attachment. (U10)
N13 NO scanline on MO-PTE, MO-MS PTE, Schedule PTE-BD, MO-1065 or Form 5889.
    Fourteen other forms in the lane carry one. ⚠ The MAIN PTE RETURN is in the
    no-scanline group — consistent with it not being machine-processed.
N14 NO late-filing penalty figure, no minimum penalty, no cap and no penalty
    worksheet on ANY of the three returns. Only the 5% LATE-PAYMENT addition is
    stated. There is no Missouri analogue of Virginia's 30% / $100-minimum
    regime. (U26)
N15 NO federal taxable income starting point in the PTE lane. MO-PTE starts
    from §702(a) / §1366 separately-and-nonseparately-computed items;
    MO-1065 and MO-1120S start from NOTHING AT ALL — they compute only
    modifications. NO §199A (removed from the §143.436 base by H.B. 1912,
    eff. 8/28/2024). NO federal NOL line (§143.121.2(4) lives on MO-A Line 2
    and MO-1120 Line 9 and has no line in this lane — U28).

═══════════════════════════════════════════════════════════════════════════
DOR DEFECTS CARRIED (the FACE governs; the conflict is LOGGED — see
MO_DOR_DEFECTS). Twenty-one catalogued at brief §16; the load-bearing ones:
═══════════════════════════════════════════════════════════════════════════
* **The DOR FAQ's rate table is STALE and must NEVER be used as a rate source.**
  It lists 5.3% (2022), 4.95% (2023), 4.8% (2024) — **and STOPS. No TY2025
  entry.** The TY2025 rate is **4.7%, printed on the MO-PTE FORM FACE at Line
  10.** A preparer consulting the FAQ gets no 2025 figure and may carry 4.8%
  forward. `mo_pte_rate()` sources the face and the harness pins the provenance.
* **MO-PTE instructions send the mileage percentage to "Form MO-PTE, Line 4"** —
  a DOLLAR Balance. It belongs at **Line 5 Percent** per the MO-MS PTE face.
  Instruction typo; BUILD TO THE FACE.
* **U11 — the Methods 3-6 trigger is INVERTED between the two instruction
  books** and nothing resolves which is right: the MO-PTE instructions say
  complete Lines 4-9 *"If the mileage percentage ... is **applicable**"*; the
  MO-MSS / MO-1120S parallel text says *"is **inapplicable**."*
  **DO NOT GUESS IN CODE — FLAG.** `mo_ms_pte_lines_4_9_required()` RAISES.
* **U24 — the extension forms contradict each other.** MO-7004 tells S
  corporations to *"use Form MO-60"*; MO-60 has **no S-corp checkbox** and tells
  S corporations to ride the federal 7004; MO-1120S names no Missouri form; and
  MO-7004 says *"up to **180 days**"* while the MO-PTE instructions say *"not to
  exceed **six months**."* Build position: **MO-PTE -> MO-7004; MO-1120S and
  MO-1065 -> federal Form 7004 only; six-month cap.**
* **MO-MS PTE and MO-MS (the C-corp schedule) both print `Attachment Sequence
  No. 1120-01`.** Two different forms, one assembly-order slot. (U13)
* **The MO-PTE face still prints `Revised 12-2025` on a file re-stamped
  2026-03-31.** A vendor keying off the printed revision code will not notice
  the March re-issue. (U12)
* **MO-NRP prints, ON A FINAL FORM:** *"Note: At the time the Department
  finalized their tax booklets, the Internal Revenue Service had not finalized
  the federal income tax forms."* — the DOR DISCLAIMING federal-line alignment.
  **Every federal line reference in this spec is `[UNVERIFIED]` against the
  FINAL TY2025 IRS forms (U8) and each carries the stamp.**

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
# It is False because the Gate-1 SEED approval has NOT been taken for Missouri.
# Campaign D-12 (2026-08-19) approved the wave SHAPE and ruled the scope-walk
# items; it did NOT approve seeding these specs. See the guard at the bottom of
# this file for the full list of reasons, which includes 22 genuinely open
# `[UNVERIFIED]` items, the narrowed U4 (MO-NRP Part 3's regulatory basis is a
# Gate-1 seed-approval QUESTION, not a free preparer election), and U8 — every
# federal line reference in this lane is uncross-checked against the FINAL
# TY2025 IRS forms, which the brief says to do BEFORE authoring and which the
# DOR itself disclaims on the face of Form MO-NRP.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = False


FORM_JURISDICTION = "MO"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"

FORM_CODE_MO1065 = "MO_1065"
FORM_CODE_MO1120S = "MO_1120S"
FORM_CODE_MOPTE = "MO_PTE"
FORM_CODES = (FORM_CODE_MO1065, FORM_CODE_MO1120S, FORM_CODE_MOPTE)

# ⚠ D-9 namespacing. These must never be shortened -- RS holds FEDERAL loaders
# under the bare `1065` / `1120S` codes and lookup does not filter by state.
FORBIDDEN_BARE_CODES = ("1065", "1120S", "1120-S", "PTE")

# Module tokens, derived from the ATTACHED FEDERAL RETURN.
M_1065 = "1065"
M_1120S = "1120S"
MODULES = (M_1065, M_1120S)

# ⚠ THREE TaxForm rows, and only three (campaign D-12 Group B). MO-MS PTE and
# Schedule PTE-BD are COMPUTING SUB-SPECS carried inside MO_PTE in reserved
# line/rule namespaces; the other companions are attachment/record types.
MO_TOP_LEVEL_SPEC_COUNT = 3
MO_SUBSPEC_PREFIXES = {
    "MS-": "Form MO-MS PTE (computing sub-spec of MO_PTE)",
    "BD-": "Schedule PTE-BD (computing sub-spec of MO_PTE)",
}
MO_ATTACHMENT_PREFIXES = {
    "NRP-": "Form MO-NRP (attachment/record type of MO_1065)",
    "NRS-": "Form MO-NRS (attachment/record type of MO_1120S)",
    "MSS-": "Form MO-MSS (attachment/record type of MO_1120S; BORROWED by MO_1065)",
    "NR-": "Forms MO-1NR / MO-2NR / MO-3NR (withholding leg, both modules)",
}
MO_COMPANION_FORMS = (
    "MO-NRP", "MO-NRS", "MO-MSS", "MO-MS PTE", "Schedule PTE-BD",
    "MO-1NR", "MO-2NR", "MO-3NR", "MO-PTEV", "MO-PTEAP", "MO-PTENR",
    "MO-PTE Opt-Out",
)
MO_ADDITIONAL_FORMS = ("MO-7004", "MO-60", "MO-TC", "Form 5889", "Form 2827", "Form 2827 PTE")


def _yk(d: dict, year: int):
    """Tax-year-keyed lookup. RAISES rather than silently defaulting.

    Every Missouri figure in this spec is TY2025-keyed. Missouri is ROLLING
    (§143.091), so a federal expensing change flows in AUTOMATICALLY AND
    SILENTLY with no Missouri line that would surface it -- which is exactly
    why a silent fallback is forbidden here. A TY2026 staleness pass must
    re-read §143.121.2 and .3 IN FULL for any newly inserted subdivision, not
    merely re-read the forms; and §143.121.3(14)(b) switches on for entities
    the year after Missouri's top individual rate reaches 4.5% or less.
    """
    if year not in d:
        raise KeyError(
            f"No TY{year} value seeded. Missouri figures are tax-year-keyed and a new tax "
            f"year staleness-invalidates them. Missouri is ROLLING (Mo. Rev. Stat. 143.091), "
            f"so a federal change flows in silently with no Missouri line to surface it; and "
            f"143.121.3(14)(b) switches entity-level capital-gain relief ON the year after the "
            f"top individual rate reaches 4.5 percent or less. Seeded years: {sorted(d)}"
        )
    return d[year]


# ═══════════════════════════════════════════════════════════════════════════
# CONFORMITY -- ROLLING, AND THERE IS NOTHING TO ADJUST
#
# ⚠ DO NOT BUILD A CONFORMITY BUCKET. Missouri is rolling and the PTE forms
# show it: the modification blocks carry NO conformity line of any kind (N3).
# §143.091 RSMo, verbatim (already seeded in RS as MO_RSMO_143_091):
#   "Any reference in sections 143.011 to 143.996 to the laws of the United
#    States shall mean the provisions of the Internal Revenue Code of 1986, and
#    amendments thereto, ... as the same may be or become effective, at any
#    time or from time to time, for the taxable year."
# Effective 1/1/1990, UNAMENDED. OBBBA therefore applies for TY2025 with no
# adoption act -- none was needed and none was enacted.
# ═══════════════════════════════════════════════════════════════════════════
MO_CONFORMITY_TYPE = "rolling"          # matches the seeded JurisdictionConformitySource row (D-10)
MO_CONFORMITY_STATUTE = "Mo. Rev. Stat. 143.091 (eff. 1/1/1990, unamended)"
MO_CONFORMITY_HAS_ADJUSTMENT_BUCKET = False
MO_CONFORMITY_NOTE = (
    "ROLLING. No adoption act, no fixed date, no conformity line on any of the three PTE-lane "
    "returns. The single largest scope lever in the Virginia wave -- the state depreciation "
    "shadow book -- DOES NOT EXIST in Missouri. ⚠ The cost of rolling conformity is that a "
    "future federal expensing change flows in AUTOMATICALLY AND SILENTLY, with no Missouri line "
    "that would surface it: a TY-rollover pass must re-read 143.121.2 and .3 in full."
)


# ═══════════════════════════════════════════════════════════════════════════
# THE TY-KEYED FIGURE TABLES. Every one is read off a FINAL TY2025 FORM FACE or
# out of a vintage-checked statute -- never projected from a trigger schedule
# and NEVER taken from the DOR FAQ (whose rate table is stale, see below).
# ═══════════════════════════════════════════════════════════════════════════

# Form MO-PTE Line 10, printed ON THE FACE: "Multiply Line 9 by 4.7%".
# Statutory basis 143.436.3(1)/.4(1): "multiplied by the highest rate of tax
# used to determine a Missouri income tax liability for an individual pursuant
# to section 143.011".
MO_PTE_RATE: dict[int, float] = {2025: 0.047}

# Form MO-1NR, verbatim: "The amount of tax to be withheld for tax year 2025 is
# 4.70 percent (0.047) of the partner's or shareholder's share of Missouri
# source distributive income" -- OR the Missouri withholding tables if the
# owner files a Form MO W-4.
MO_NR_WITHHOLDING_RATE: dict[int, float] = {2025: 0.047}

# Schedule PTE-BD Line 9, printed ON THE FACE: "Multiply Line 8, Column C by
# 20%". ⚠ READ OFF THE FORM, never derived from 143.022.4's revenue-trigger
# ratchet (.4 sets only the 20% CEILING; .5 gates increases on a $150,000,000
# net-general-revenue growth test). A TY2026 pass must RE-READ THE FACE.
MO_BID_PERCENT: dict[int, float] = {2025: 0.20}
MO_BID_CEILING_STATUTE = "Mo. Rev. Stat. 143.022.4 (20 percent maximum); .5 ($150,000,000 trigger)"

MO_TOP_INDIVIDUAL_RATE: dict[int, float] = {2025: 0.047}
MO_CORPORATE_RATE: dict[int, float] = {2025: 0.04}
MO_COMPOSITE_RATE: dict[int, float] = {2025: 0.047}

# 143.121.3(14)(b): entity-level capital-gain relief switches on for the tax
# year FOLLOWING the year in which the top individual rate is <= 4.5%.
MO_CAPGAIN_ENTITY_TRIGGER_RATE = 0.045

# 143.411.5(2) / 143.471.6(2) -- the withholding de minimis, verbatim
# "Missouri assignable federal adjusted gross income ... of less than twelve
# hundred dollars". ⚠ STRICTLY LESS THAN.
MO_WH_DE_MINIMIS: dict[int, int] = {2025: 1200}

# The related-expense FLOOR on every a/b netting pair (1a/1b is the city
# carve-out and is NOT one of these; 2a/2b and 6a/6b are).
# ⚠ A FLOOR ON THE EXPENSE, NOT A THRESHOLD ON THE SUBTRACTION:
# "The expenses must equal or exceed $500. If less than $500, enter zero."
MO_RELATED_EXPENSE_FLOOR = 500

MO_REFUND_FLOOR = 1.00                 # MO-PTE L23: "No refund of less than $1.00 will be made."
MO_ELECTRONIC_REFUND_THRESHOLD = 100000  # MO-PTE L23: refunds >= $100,000 -> Form 5378
MO_LATE_PAYMENT_ADDITION = 0.05        # the 5% addition to tax (survives; see N2)
MO_EXTENSION_MAX_MONTHS = 6            # MO-PTE instructions: "not to exceed six months"
MO_EXTENSION_MO7004_DAYS_CLAIM = 180   # ⚠ MO-7004's own contradictory figure (U24)
MO_METHOD_SEVEN_PETITION_DAYS = 60     # 12 CSR 10-2.076(2)(G): BEFORE the end of the tax year
MO_FEDERAL_ADJUSTMENT_DAYS = 90        # 12 CSR 10-2.105; 143.601; 143.436.12

# Rounding, three different conventions on three different grids.
MO_ROUND_PAGE3_SHARE_DECIMALS = 0      # MO-1065/MO-1120S Page 3 Col 4: "Round ... to whole numbers"
MO_ROUND_PARTB_SHARE_DECIMALS = 2      # MO-PTE Part B Col 5: "to the nearest two decimal places"
MO_ROUND_APPORTIONMENT_DECIMALS = 3    # MO-PTE L5 Percent: "such as 12.345 percent"

# ⚠⚠ THE DOR STATES NO TIE-BREAK RULE FOR ANY OF THE THREE. This file uses
# ROUND-HALF-UP explicitly and records that choice as an ENGINEERING DECISION,
# not as a Departmental rule. Recorded because the OREGON wave proved the
# hazard is real in the other direction: Oregon publishes a rounded proration
# TABLE and a bare Python round() (banker's / round-half-to-even) silently
# diverges on three of twelve rows. Missouri publishes NO table and NO
# tie-break, so a silent banker's-rounding default here would be an invented
# rule. Flagged at D_MO_ROUNDING_TIEBREAK and reported to Ken.
MO_ROUNDING_TIEBREAK = "ROUND_HALF_UP"
MO_ROUNDING_TIEBREAK_IS_DOR_RULE = False


def _round_half_up(value: float, places: int) -> float:
    """Explicit half-up rounding. See MO_ROUNDING_TIEBREAK.

    Never use the builtin round() for a Missouri percentage -- it is
    round-half-to-even and would silently impose a tie-break the Department has
    not published.
    """
    from decimal import ROUND_HALF_UP, Decimal
    q = Decimal(1).scaleb(-places) if places else Decimal(1)
    return float(Decimal(repr(float(value))).quantize(q, rounding=ROUND_HALF_UP))


def mo_pte_rate(year: int = FORM_TAX_YEAR) -> float:
    """The Form MO-PTE Line 10 rate, sourced from the FORM FACE.

    ⚠⚠ NEVER SOURCE THIS FROM THE DOR FAQ. The FAQ's "What is the tax rate for
    pass-through entity tax?" table lists 5.3% (2022), 4.95% (2023) and 4.8%
    (2024) AND THEN STOPS -- there is no TY2025 entry, and a preparer consulting
    it may carry 4.8% forward. (Brief 16 #19, a defect the first pass missed.)
    """
    return _yk(MO_PTE_RATE, year)


def mo_withholding_rate(year: int = FORM_TAX_YEAR) -> float:
    """Form MO-1NR / MO-2NR: 4.70 percent (0.047), printed verbatim."""
    return _yk(MO_NR_WITHHOLDING_RATE, year)


def mo_bid_percent(year: int = FORM_TAX_YEAR) -> float:
    """Schedule PTE-BD Line 9: 20%, READ OFF THE FACE, not derived from 143.022.4."""
    return _yk(MO_BID_PERCENT, year)


def mo_capital_gain_entity_relief_active(year: int = FORM_TAX_YEAR) -> bool:
    """143.121.3(14)(b) -- the STALENESS TRIPWIRE, evaluated, never assumed.

    Entity-level capital-gain relief switches on for tax years beginning on or
    after January 1 of the year FOLLOWING the year in which Missouri's top
    individual rate is 4.5% or less. TY2025's top rate is 4.7%, so it is NOT
    operative and the FORM (which carries no capital-gain line) is right.
    """
    return _yk(MO_TOP_INDIVIDUAL_RATE, year) <= MO_CAPGAIN_ENTITY_TRIGGER_RATE


# ═══════════════════════════════════════════════════════════════════════════
# N1 -- THE DEPRECIATION VERIFIED NEGATIVE, ENCODED AS AN ABSENCE
# ═══════════════════════════════════════════════════════════════════════════
MO_HAS_BONUS_ADDBACK = False
MO_HAS_SHADOW_DEPRECIATION_BOOK = False
MO_SECTION_179_STATE_LIMIT = None       # ⚠ There is no such figure. Do not invent one.
MO_SECTION_179_STATE_PHASEOUT = None

# 143.121.2(3) / .3(7) / .3(9) -- the CLOSED window, on the face of the statute.
MO_JCWAA_WINDOW = ("2002-07-01", "2003-06-30")
MO_JCWAA_ADDBACK_CITE = "Mo. Rev. Stat. 143.121.2(3) (IRC 168 as amended by JCWAA 2002)"
MO_JCWAA_SUBTRACTION_CITE = "Mo. Rev. Stat. 143.121.3(7) (IRC 168 as in effect January 1, 2002)"
MO_JCWAA_DISPOSITION_CITE = "Mo. Rev. Stat. 143.121.3(9)"

# The FOUR faces that carry a depreciation line, and the ONE document that
# spells the window out IN WORDS. ⚠ 22 correction #7: the brief's "five form
# faces" framing overstated the form-side support; the negative rests on the
# STATUTE, not on this table.
MO_DEPRECIATION_LINES = {
    "MO_1065": ["9"],                    # basis adjustment only -- NO .3(9) line (N9)
    "MO_1120S": ["10", "11"],            # basis adjustment AND disposition recovery
    "MO_NRP": ["Part 2 Line 9"],
    "MO_NRS": ["Part 2 Line 10", "Part 2 Line 11"],
    "MO_PTE": [],                        # ⚠ NONE AT ALL (N5)
}
MO_DEPRECIATION_WINDOW_IN_WORDS_SOURCE = "MO-1120S Instructions (2025), Lines 10 and 11"

# 179 in the Missouri PTE lane -- a DISTRIBUTIVE SHARE ITEM, three times, and a
# modification ZERO times.
MO_SECTION_179_APPEARANCES = {
    "MO-NRP Part 1 Line 12": "Section 179 deduction (attach schedule) - distributive share item",
    "MO-NRS Part 1 Line 11": "Section 179 deduction - distributive share item",
    "Schedule PTE-BD Line 6": "Section 179 Deduction - distributive share item, no Missouri cap",
}


def mo_section_179_state_limit(year: int = FORM_TAX_YEAR):
    """REFUSES to return a Missouri 179 figure, because none exists.

    143.121 contains NO 179 modification of any kind and the string "179"
    appears in it ZERO times. Missouri takes the FEDERAL OBBBA figures by
    default in all three PTE-lane returns with no state recomputation.
    ⚠ Virginia needs a DERIVED state 179 figure. That pattern must not be
    ported (brief 10.3).
    """
    raise ValueError(
        "MISSOURI HAS NO STATE IRC 179 FIGURE AND NONE MAY BE ENCODED. Mo. Rev. Stat. 143.121 "
        "contains no IRC 179 modification of any kind (zero occurrences of the string '179'); "
        "IRC 179 appears in the Missouri PTE lane ONLY as a distributive-share item on MO-NRP "
        "Part 1 Line 12, MO-NRS Part 1 Line 11 and Schedule PTE-BD Line 6. Missouri takes the "
        "federal OBBBA figures by default with no state recomputation. DO NOT PORT VIRGINIA'S "
        f"DERIVED STATE FIGURE. (asked for TY{year})"
    )


def mo_depreciation_modification_applies(purchase_date: str) -> bool:
    """True ONLY for property purchased inside the closed JCWAA window.

    ⚠ This is the whole of Missouri's depreciation modification regime. There
    is no rule for post-30-June-2003 property to find, because the ADD-BACK
    PROVISION ITSELF -- 143.121.2(3) -- is window-limited on its face. 100%
    OBBBA bonus flows through untouched.
    """
    start, end = MO_JCWAA_WINDOW
    return start <= purchase_date <= end


# ═══════════════════════════════════════════════════════════════════════════
# A6 -- THE SUBMISSION-CHANNEL MODEL AND THE PRIVACY RULING
# ═══════════════════════════════════════════════════════════════════════════
MO_AUTOMATE_EMAIL_SUBMISSION = False    # ⚠ campaign D-12 A6. Do not flip.
MO_PTE_EFILE_AVAILABLE = False
MO_PTE_ELECTRONIC_PAYMENT_AVAILABLE = False
MO_MEF_ELIGIBLE_FORMS = (FORM_CODE_MO1065, FORM_CODE_MO1120S)
MO_SUBSTITUTE_FORMS_TRACK = (FORM_CODE_MOPTE,)
MO_SUBSTITUTE_FORMS_ARTIFACTS = (
    "Form 4349 (letter of intent)", "Form 5629 (Guidelines for Substitute and Reproduced Tax "
    "Forms)", "the published 10 x 6 grid layout spec", "the DOR 2-D barcode specification",
)

MO_EFILE_EVIDENCE = (
    ("DOR FAQs - Pass-Through Entity Tax (re-pulled 2026-08-19)",
     "'No. You must submit your return Form MO-PTE to PO Box 3080, Jefferson City, MO "
     "65105-3080, or by email to pteincome@dor.mo.gov.' and 'No. You must submit your payment "
     "with Form MO-PTEV or MO-PTEAP with a check, money order, or cashier's check...'"),
    ("Form MO-PTE face, page 4 (PDF ModDate 2026-03-31, the newest document in the lane)",
     "Prints a mailing address and an e-mail address. NO e-file reference anywhere on the face."),
    ("Form MO-PTE Instructions, all 9 pages",
     "The string 'electronic' occurs EXACTLY ONCE, in the $100,000-refund context at Line 23."),
    ("DOR Partnership e-file page", "Names ONLY MO-1065. MO-PTE absent."),
    ("DOR Corporation-income e-file page",
     "Names ONLY MO-1120 and MO-1120S; its 22-vendor approved list is scoped to those two."),
    ("Drake Software KB 18013 (independent commercial confirmation)",
     "'Form MOPTE and the MOPTE Voucher are not e-fileable and there are no options for "
     "electronic payments this year.' Also: 'Electronic filing of Forms MO-PTEAP is not allowed.'"),
)


def mo_submission_channels(form_code: str) -> dict:
    """The sanctioned submission channels per form, with automation posture.

    ⚠ campaign D-12 A6 -- A PRIVACY RULING, NOT A TAX ONE. The Department's
    e-mail channel is SANCTIONED (so "paper-only" overstates the finding) but
    it carries member SSNs IN THE CLEAR, so Delvio does not automate it.
    Delvio computes and assembles; the preparer chooses the channel.
    """
    if form_code in MO_MEF_ELIGIBLE_FORMS:
        return {
            "form": form_code,
            "mef": True,
            "electronic_payment": True,
            "channels": ["MeF (optional)", "paper"],
            "delvio_automates": ["MeF (optional)", "paper"],
            "note": ("MO-1065 and MO-1120S ARE MeF-eligible. MO-1120S has TWO methods: through an "
                     "IRS-approved ERO with the federal return, or as a STAND-ALONE state return."),
        }
    if form_code != FORM_CODE_MOPTE:
        raise ValueError(f"unknown Missouri form code {form_code!r}")
    return {
        "form": FORM_CODE_MOPTE,
        "mef": False,
        "electronic_payment": False,
        "channels": [
            "mail to PO Box 3080, Jefferson City, MO 65105-3080",
            "e-mail a PDF to pteincome@dor.mo.gov (Department-sanctioned)",
        ],
        # ⚠ THE E-MAIL CHANNEL IS DELIBERATELY ABSENT FROM THIS LIST.
        "delvio_automates": ["print / assemble for mailing"],
        "payment_instruments": ["check", "money order", "cashier's check"],
        "payment_vouchers": ["MO-PTEV", "MO-PTEAP"],
        "note": ("NOT e-fileable through MeF and NOT electronically payable -- settled six "
                 "independent ways. ⚠ 'Paper-only' OVERSTATES it: the e-mailed PDF is a sanctioned "
                 "channel. ⚠⚠ Delvio does NOT automate that channel (campaign D-12 A6): it carries "
                 "member SSNs in the clear. The preparer chooses the channel. MO-PTE rides the "
                 "SUBSTITUTE-FORMS track, not MeF."),
    }


def mo_email_channel_is_automatable() -> bool:
    """Always False. Campaign D-12 A6. The harness pins this."""
    return MO_AUTOMATE_EMAIL_SUBMISSION


# ═══════════════════════════════════════════════════════════════════════════
# THE SOURCING REGIMES -- C3 as re-scoped by the U4 follow-up (brief 22.11)
# ═══════════════════════════════════════════════════════════════════════════
REGIME_143_455 = "143.455"           # receipts factor / allocate-and-apportion
REGIME_NRP_PART3 = "nrp_part_3"      # MO-NRP Part 3 direct accounting (separate accounting)
REGIME_BRAINS = "pte_bd_column_c"    # PTE-BD Column (C) "brains of the operation"

MO_SOURCING_REGIMES = {
    REGIME_143_455: {
        "label": "Mo. Rev. Stat. 143.455 -- allocate and apportion (single receipts factor at .10)",
        "used_by": ["MO-MS PTE -> MO-PTE Line 5", "MO-MSS -> MO-NRS Column (c)",
                    "MO-NRP Column (c) when Part 3 is not used"],
        "authority": ("143.455; 12 CSR 10-2.255(1)(B), (2), (3), (4); 12 CSR 10-2.190(2)(C) "
                      "delegating to .255"),
        "quantitative": True,
    },
    REGIME_NRP_PART3: {
        "label": "MO-NRP Part 3 direct accounting (separate accounting), Lines 1-13",
        "used_by": ["MO-NRP Part 1 Column (c) when Part 3 is used"],
        "authority": ("⚠ NARROWED-BUT-OPEN. 12 CSR 10-2.255 is a CLOSED TWO-BRANCH test "
                      "(apportioned or allocated, both under 143.455) with NO separate-accounting "
                      "branch, yet MO-NRP Part 3 prints one. The only statutory room is "
                      "143.421.4 -- 'may, ON APPLICATION, authorize the use of such other methods' "
                      "-- and NOTHING on the form or in either regulation mentions an application."),
        "quantitative": True,
    },
    REGIME_BRAINS: {
        "label": ("Schedule PTE-BD Column (C) -- 'if the \"brains\" of the operation resulting in "
                  "the item are located in Missouri, that item is from Missouri sources'"),
        "used_by": ["Schedule PTE-BD Column (C) -> Line 8 -> Line 9 -> MO-PTE Line 6"],
        "authority": ("Schedule PTE-BD instructions ONLY. ⚠ It is NOWHERE in 143.455, and NEITHER "
                      "12 CSR 10-2.190 NOR 12 CSR 10-2.255 mentions it. U17 IS FULLY OPEN."),
        "quantitative": False,          # ⚠ QUALITATIVE. There is nothing to reconcile TO.
    },
}

# ⚠⚠ THE U4 FOLLOW-UP FLIPS ONE EXPECTATION AND LEAVES THE OTHER UNTOUCHED.
MO_SOURCING_EXPECTATIONS = {
    # 12 CSR 10-2.255(3) puts partnership nonresident-partner sourcing on 143.455,
    # IDENTICAL to S corporations. So these two now run the SAME statute.
    (REGIME_143_455, REGIME_NRP_PART3): {
        "expected_delta": "ZERO",
        "on_nonzero": "PROBABLE ERROR (or an unapproved MO-NRP Part 3 election)",
        "reconcile": True,
        "why": ("⚠ THE MEANING OF THIS DIAGNOSTIC FLIPPED on 2026-08-19. 12 CSR 10-2.190(2)(C) "
                "delegates to 12 CSR 10-2.255, whose (3) puts BOTH MO-NRP and MO-MS PTE on "
                "143.455. The MO-NRP -> MO-MSS cross-reference is DELIBERATE, not an editorial "
                "slip, and it is a HIERARCHY, not an election -- which is why no MO-MSP was ever "
                "published. A non-zero delta is now a PROBABLE ERROR, not normal regime "
                "disagreement."),
    },
    # The severe half, completely untouched by the U4 work.
    (REGIME_143_455, REGIME_BRAINS): {
        "expected_delta": "UNDEFINED",
        "on_nonzero": "EXPECTED AND CORRECT -- DO NOT FORCE THESE TO RECONCILE",
        "reconcile": False,
        "why": ("⚠⚠ THE REAL COLLISION, AND IT SURVIVES IN FULL. MO-PTE Line 5 sources under "
                "143.455 (formulary); MO-PTE Line 6 sources under Schedule PTE-BD Column (C)'s "
                "QUALITATIVE 'brains of the operation' place-of-production test. ADJACENT LINES on "
                "the same return, both feeding Line 9. Nothing in 143.455, 12 CSR 10-2.190 or "
                "12 CSR 10-2.255 mentions the brains test. U17 IS FULLY OPEN. Campaign D-12 C3: "
                "DO NOT FORCE THEM TO RECONCILE."),
    },
}

# The negative finding the U4 follow-up recorded, kept so nobody re-searches.
MO_NO_143_181_REGULATION = (
    "NEGATIVE FINDING (12 CSR 10-2 searched chapter-wide, 2026-08-19): NO LIVE REGULATION UNDER "
    "143.181 GOVERNS PARTNERSHIP SOURCING. Only 12 CSR 10-2.010 (Missouri AGI / spousal "
    "allocation -- unrelated) and the RESCINDED 12 CSR 10-2.130 (rescinded March 30, 2024) cite "
    "143.181 authority. U4's second 'would settle it' asked for a regulation that DOES NOT EXIST. "
    "143.581's 143.181 reference is a RETURN-FILING TRIGGER, not a computation method: 143.421.1 "
    "says the part is determined 'under regulations prescribed by the director of revenue', and "
    "the director's regulation (12 CSR 10-2.255) says 143.455. ⚠ This corrects brief 2.2."
)

MO_NRP_PART3_STATUS = "GATE-1 SEED QUESTION - NOT A FREE ELECTION"
MO_NRP_PART3_QUESTION = (
    "Is MO-NRP Part 3 a STANDING, PRE-APPROVED 143.421.4 alternative method (the form itself being "
    "the Department's grant), or is it PRE-2020 FORM FURNITURE that 12 CSR 10-2.255 superseded on "
    "2021-03-30 and the form was never conformed to? 12 CSR 10-2.255 is a closed two-branch test "
    "with no separate-accounting branch; 143.421.4 permits other methods only 'on application' to "
    "the director; and nothing on Form MO-NRP, in its embedded instructions, or in either "
    "regulation mentions an application, a petition or an approval. ⚠ DO NOT DEFAULT THIS TO A "
    "FREE PREPARER ELECTION. Settle by a DOR statement (corporate@dor.mo.gov / (573) 751-4541) or "
    "a full reading of 12 CSR 10-2.076's alternative-method machinery."
)


def mo_nrp_part3_available() -> dict:
    """MO-NRP Part 3 is NOT offered as a free preparer election. Campaign D-12 C3 / U4.

    Returns the refusal WITH the Gate-1 question attached, so the caller cannot
    treat "unavailable" as a settled negative either.
    """
    return {
        "available": False,
        "status": MO_NRP_PART3_STATUS,
        "gate1_question": MO_NRP_PART3_QUESTION,
        "fallback": ("The MO-MSS receipts factor. MO-NRP's own instructions, verbatim: 'When Part 3 "
                     "is not applicable, all business income should be apportioned by using Method "
                     "Two A Receipts Factor Apportionment. The apportionment factor percentage from "
                     "Form MO-MSS, Part 1, Line 3 is entered on Form MO-NRP, Column (c).'"),
    }


def mo_sourcing_divergence(regime_a: str, regime_b: str, pct_a=None, pct_b=None) -> dict:
    """Compare two Missouri sourcing regimes -- or REFUSE to, when refusing is right.

    ⚠ The (143.455, brains) pair is NOT reconcilable and this function will not
    pretend otherwise: one side is FORMULARY and the other is QUALITATIVE, and
    campaign D-12 C3 rules that they must not be forced to reconcile.
    """
    key = (regime_a, regime_b) if (regime_a, regime_b) in MO_SOURCING_EXPECTATIONS \
        else (regime_b, regime_a)
    spec = MO_SOURCING_EXPECTATIONS.get(key)
    if spec is None:
        raise ValueError(f"no expectation recorded for the pair {regime_a!r} / {regime_b!r}")
    out = {
        "pair": key,
        "expected_delta": spec["expected_delta"],
        "on_nonzero": spec["on_nonzero"],
        "reconcile": spec["reconcile"],
        "why": spec["why"],
        "delta": None,
        "severity": None,
    }
    if not spec["reconcile"]:
        out["severity"] = "info"
        out["note"] = ("REFUSING to compute a reconciliation. U17 is fully open and the two sides "
                       "are not commensurable.")
        return out
    if pct_a is None or pct_b is None:
        return out
    out["delta"] = round(float(pct_a) - float(pct_b), 6)
    # ⚠ THE FLIP: a non-zero delta is now a PROBABLE ERROR, not normal disagreement.
    out["severity"] = "warning" if out["delta"] else None
    return out


# ═══════════════════════════════════════════════════════════════════════════
# APPORTIONMENT METHODS -- C11, THE CORRECTED VERSION
#
# ⚠ The MO-MS PTE face note "Complete mileage information below for Method
# Three - Six" is DEFECTIVE FOR TWO METHODS: Three (gross earnings) AND Five
# (flat one-half). ONLY FOUR AND SIX ARE MILEAGE-DRIVEN.
# ═══════════════════════════════════════════════════════════════════════════
BASIS_RECEIPTS = "receipts_factor"
BASIS_GROSS_EARNINGS = "gross_earnings"
BASIS_MILEAGE = "mileage"
BASIS_FLAT_ONE_HALF = "flat_one_half"
BASIS_APPROVED = "approved_or_industry_regulation"

MO_APPORTIONMENT_METHODS: dict[str, dict] = {
    "2a": {
        "label": "Two A - Receipts Factor Apportionment",
        "basis": BASIS_RECEIPTS,
        "mileage_driven": False,
        "cited_on_face": "Mo. Rev. Stat. 143.455.2",
        "actual_authority": ("Mo. Rev. Stat. 143.455.10 (the single receipts factor); .11 and .12 "
                             "(sourcing). ⚠ .2 is the APPLICABILITY subsection, not the formula -- "
                             "the face's cite is a pointer to the regime. Cite .10/.11/.12."),
        "note": ("⚠ The 'taxpayers that do not qualify for a Special Method ... must choose Method "
                 "Two A' default sentence is printed on Form MO-MS (the C-CORP schedule) ONLY. "
                 "Neither Form MO-MS PTE nor the MO-PTE instructions repeat it -- they say only "
                 "'Choose only the appropriate one of the listed methods.' On the PTE forms the "
                 "default is INFERRED, NOT PRINTED. 22.5 grounds the inference in 12 CSR "
                 "10-2.076(1) plus 143.455's structure (.2 general, .13-.17 special), which makes "
                 "Two A the residual default BY CONSTRUCTION -- but 'inferred, not printed' "
                 "STANDS. (C4 / U5)"),
    },
    "3": {
        "label": "Three - Transportation",
        "basis": BASIS_GROSS_EARNINGS,        # ⚠⚠ NOT MILEAGE. C11.
        "mileage_driven": False,
        "cited_on_face": "Mo. Rev. Stat. 143.455.14",
        "actual_authority": "Mo. Rev. Stat. 143.455.14",
        "verbatim": ("'...shall report its GROSS EARNINGS within the state on intrastate business "
                     "and shall also report its gross earnings on all interstate business done in "
                     "this state... This subsection shall not apply to a railroad.'"),
        "note": ("⚠⚠ C11. THE FACE NOTE IS WRONG FOR THIS METHOD. It is a GROSS-EARNINGS reporting "
                 "rule, not a mileage formula. The brief's own correction C3 originally got this "
                 "wrong too and the verification pass overturned it."),
    },
    "4": {
        "label": "Four - Railroad",
        "basis": BASIS_MILEAGE,
        "mileage_driven": True,
        "cited_on_face": "Mo. Rev. Stat. 143.455.15",
        "actual_authority": "Mo. Rev. Stat. 143.455.15",
        "verbatim": ("'...as the MILEAGE used over the rails and lines of such corporation in the "
                     "state shall bear to the total mileage'"),
        "note": "Also offers an ELECTIVE INVESTMENT RATIO in fixed transportation facilities.",
    },
    "5": {
        "label": "Five - Interstate Bridge",
        "basis": BASIS_FLAT_ONE_HALF,          # ⚠⚠ NOT MILEAGE. C11.
        "mileage_driven": False,
        "cited_on_face": "Mo. Rev. Stat. 143.455.16",
        "actual_authority": "Mo. Rev. Stat. 143.455.16",
        "verbatim": ("'shall include in its Missouri taxable income ONE-HALF of the net income from "
                     "the operation of a bridge between this and another state'"),
        "note": ("⚠⚠ C11. THE FACE NOTE IS WRONG FOR THIS METHOD TOO. A flat one-half rule, with an "
                 "option to fold the bridge into a railroad's return."),
    },
    "6": {
        "label": "Six - Telephone and Telegraph",
        "basis": BASIS_MILEAGE,
        "mileage_driven": True,
        "cited_on_face": "Mo. Rev. Stat. 143.455.17",
        "actual_authority": "Mo. Rev. Stat. 143.455.17",
        "verbatim": ("'...such proportion of such revenue as the MILEAGE involved in this state "
                     "shall bear to the total mileage involved'"),
        "note": "Also offers an ELECTIVE INVESTMENT RATIO.",
    },
    "7": {
        "label": "Seven - Broadcasters or Other Approved Method",
        "basis": BASIS_APPROVED,
        "mileage_driven": False,
        "cited_on_face": "Mo. Rev. Stat. 143.455.13(2) in the election list; .13(1) in the instructions",
        "actual_authority": ("⚠ TWO DIFFERENT ROUTES AND THE FORM CONFLATES THEIR CITES. "
                             ".13(1) = the director 'shall promulgate rules for determining the "
                             "apportionment and allocation factors' for industries with unusual "
                             "factual situations -> the BROADCASTER REGULATION route (12 CSR "
                             "10-2.260). .13(2) = the PETITION for alternative apportionment "
                             "(separate accounting / additional factors / any other method), with a "
                             "preponderance-of-evidence burden on the petitioner under .13(3)."),
        "note": ("Entities defined as a broadcaster under 12 CSR 10-2.260 MUST choose Method Seven. "
                 "⚠ On Method Seven, Part 1 Line 3 SUBSTITUTES the approved percentage (without "
                 "taking allocation into account) for the receipts factor."),
    },
}

MO_MILEAGE_METHODS = tuple(k for k, v in MO_APPORTIONMENT_METHODS.items() if v["mileage_driven"])
MO_MILEAGE_NOTE_ON_FACE = "Complete mileage information below for Method Three - Six"
MO_MILEAGE_NOTE_DEFECTIVE_FOR = ("3", "5")   # ⚠ TWO methods, not one. C11.


def mo_mileage_note_defect() -> dict:
    """C11 -- restated BEFORE it propagates, per campaign D-12."""
    return {
        "printed_note": MO_MILEAGE_NOTE_ON_FACE,
        "actually_mileage_driven": MO_MILEAGE_METHODS,
        "defective_for": MO_MILEAGE_NOTE_DEFECTIVE_FOR,
        "count": len(MO_MILEAGE_NOTE_DEFECTIVE_FOR),
        "why": ("143.455.14 (Method Three - Transportation) is a GROSS-EARNINGS rule and "
                "143.455.16 (Method Five - Interstate Bridge) is a FLAT ONE-HALF rule. Only "
                "143.455.15 (Four - Railroad) and 143.455.17 (Six - Telephone and Telegraph) are "
                "mileage-driven. Corroborated by 12 CSR 10-2.045(14)(B), which maps '.14 (relating "
                "to transportation), .15 (railroads, and the like), .16 (interstate bridges), .17 "
                "(telephone or telegraph companies), .13 (other approved methods), or 12 CSR "
                "10-2.260'."),
    }


def mo_method_seven_petition_deadline(tax_year_end: str) -> dict:
    """ADVISORY ONLY. NEVER a filing-time gate. (D-12 Group D / W7)

    The petition is due at least SIXTY DAYS BEFORE THE END OF THE TAX YEAR, so
    by the time the return is prepared the window has ALREADY CLOSED.
    ⚠ 22 correction #10: the deadline is in the REGULATION -- 12 CSR
    10-2.076(2)(G) defines 'Petition' as 'the filing of written or electronic
    document(s) with the director AT LEAST SIXTY (60) DAYS BEFORE THE END OF
    THE TAX YEAR to which alternative apportionment is sought to apply' -- so it
    binds ALL THREE LANES regardless of which instruction sheet repeats it. The
    narrower observation (the MO-1120S / MO-MSS Method Seven text omits it) is
    itself a DOR defect.
    """
    return {
        "days_before_year_end": MO_METHOD_SEVEN_PETITION_DAYS,
        "tax_year_end": tax_year_end,
        "authority": "12 CSR 10-2.076(2)(G); Mo. Rev. Stat. 143.455.13(2)",
        "channel": "e-mail the petition to pteincome@dor.mo.gov",
        "content_requirements": "a seven-item content list, including a Form 2827 power of attorney",
        "enforcement": "ADVISORY DIAGNOSTIC ONLY - never a filing-time gate",
        "why": ("The window closes 60 days before year end, i.e. BEFORE the return is prepared. A "
                "filing-time gate would block a return over a deadline the preparer could not have "
                "met at filing time. Raise it as advice plus a NEXT-YEAR reminder."),
    }


# ═══════════════════════════════════════════════════════════════════════════
# FORM MO-MS PTE, PART 1 -- the BACK-SOLVED percentage, and its three hazards
#
#   L3 = L1 / L2                                        (receipts factor)
#   ... STOP HERE if there is no nonapportionable income: MO-PTE L5% = L3
#   L6 = (L4 - L5) x L3
#   L8 = L6 + L7
#   L9 = L8 / L4          ⚠ undefined at L4 = 0; SIGN-FLIPS at L4 < 0
#   MO-PTE L5 = L4 x round(L9, 3)   ⚠ the ROUNDED PRODUCT WINS, not L8
#
# ⭐ This is a MATERIALLY DIFFERENT ARCHITECTURE from MO-MS / MO-MSS. MO-MSS
# Line 3 produces a FACTOR applied per distributive-share item. MO-MS PTE
# Lines 4-9 produce a BLENDED EFFECTIVE PERCENTAGE by back-solving, so that
# L4 x L9 = L8. The percentage is a DERIVED ARTEFACT, not a factor.
# ═══════════════════════════════════════════════════════════════════════════
def mo_ms_pte_part1(l1_missouri_receipts: float, l2_total_receipts: float,
                    l4_balance: float, l5_nonapp_everywhere: float = 0.0,
                    l7_nonapp_missouri: float = 0.0,
                    has_nonapportionable: bool = False) -> dict:
    """Form MO-MS PTE Part 1, Lines 1-9, with the L4 <= 0 hard RED.

    ⚠ The instructions expressly require the form 'even if this balance is zero
    or negative', and Line 9 divides by Line 4. Neither the form nor the
    instructions address either case. DO NOT silently return 0% or 100%.
    (U14 / D-12 Group D)
    """
    out: dict = {"L1": l1_missouri_receipts, "L2": l2_total_receipts, "L4": l4_balance}
    out["L3"] = None if not l2_total_receipts else \
        _round_half_up(100.0 * l1_missouri_receipts / l2_total_receipts,
                       MO_ROUND_APPORTIONMENT_DECIMALS)
    if not has_nonapportionable:
        # The printed "stop here" short path -- Lines 4-9 stay BLANK and MO-PTE
        # Line 5 Percent comes from Line 3. TWO DIFFERENT SOURCES for one field.
        out.update({"stop_here": True, "L5": None, "L6": None, "L7": None, "L8": None,
                    "L9": None, "mo_pte_l5_percent_source": "MO-MS PTE Line 3",
                    "mo_pte_l5_percent": out["L3"], "blocked": False})
        return out
    out["stop_here"] = False
    out["L5"] = l5_nonapp_everywhere
    out["L7"] = l7_nonapp_missouri
    factor = (out["L3"] or 0.0) / 100.0
    out["L6"] = (l4_balance - l5_nonapp_everywhere) * factor
    out["L8"] = out["L6"] + l7_nonapp_missouri
    if l4_balance <= 0:
        # ⚠⚠ HARD RED. L4 == 0 -> division by zero; L4 < 0 -> a percentage whose
        # SIGN IS INVERTED relative to the intended allocation.
        out["L9"] = None
        out["blocked"] = True
        out["block_reason"] = (
            "MO-MS PTE Line 9 divides Line 8 by Line 4 and Line 4 is zero or negative. The "
            "instructions require this form 'even if this balance is zero or negative' but neither "
            "the form nor the instructions address either case: a zero denominator is undefined and "
            "a negative denominator INVERTS THE SIGN of the resulting percentage. PREPARE MANUALLY. "
            "(U14; campaign D-12 Group D)")
        out["mo_pte_l5_percent"] = None
        out["mo_pte_l5_percent_source"] = None
        return out
    out["blocked"] = False
    out["L9"] = _round_half_up(100.0 * out["L8"] / l4_balance, MO_ROUND_APPORTIONMENT_DECIMALS)
    out["mo_pte_l5_percent"] = out["L9"]
    out["mo_pte_l5_percent_source"] = "MO-MS PTE Line 9"
    return out


def mo_pte_line5(l4_balance: float, all_missouri: bool = False,
                 apportionment_percent: float | None = None) -> dict:
    """MO-PTE Line 5 -- 'Preliminary Missouri net income (loss)'.

    ⚠⚠ THE RULING AS RESTATED SAYS "MO-MS PTE Line 5 = L4 x round(L9, 3)". THAT
    IS A WORDING DEFECT AND IT IS RESOLVED HERE RATHER THAN PROPAGATED.
    MO-MS PTE's OWN Line 5 is `Nonapportionable income - Everywhere` -- a
    DIRECT-ENTRY dollar amount feeding Line 6, not a product. The formula
    belongs to **MO-PTE Line 5**, whose face reads 'Multiply Line 4 by the
    percentage', using MO-MS PTE Line 4 (which IS MO-PTE Line 4) and MO-MS PTE
    Line 9. Substance is unaffected; the line label is not. Escalated to Ken.

    THE ROUNDED PRODUCT WINS. MO-MS PTE Line 8 is computed directly AND
    reproduced via a percentage rounded to three decimals, so the round trip
    LOSES PRECISION and `L4 x round(L9, 3) != L8`. The MO-PTE Line 5 label
    settles which one is Line 5: 'Multiply Line 4 by the percentage.'
    Encode the rounding; DO NOT shortcut to Line 8.
    """
    if all_missouri:
        return {"L5": l4_balance, "basis": "all Missouri -- enter the amount from Line 4",
                "percent": None, "rounded_percent": None}
    if apportionment_percent is None:
        raise ValueError(
            "MO-PTE Line 5 needs an apportionment percentage from Form MO-MS PTE (Line 3 on the "
            "'stop here' short path, otherwise Line 9). The instructions require Form MO-MS PTE "
            "whenever Line 4 is not 100 percent from Missouri sources.")
    rounded = _round_half_up(apportionment_percent, MO_ROUND_APPORTIONMENT_DECIMALS)
    return {
        "L5": l4_balance * rounded / 100.0,
        "basis": "L4 x round(MO-MS PTE percentage, 3) -- the ROUNDED PRODUCT WINS",
        "percent": apportionment_percent,
        "rounded_percent": rounded,
        "note": ("⚠ The directly-computed MO-MS PTE Line 8 will differ by the rounding residue. "
                 "MO-PTE Line 5's own label -- 'Multiply Line 4 by the percentage' -- settles it. "
                 "⚠ The DOR states NO tie-break for the three-decimal rounding; this build uses "
                 "ROUND_HALF_UP as an ENGINEERING DECISION (see MO_ROUNDING_TIEBREAK)."),
    }


def mo_ms_pte_lines_4_9_required(*_args, **_kwargs):
    """REFUSES to decide. U11 -- the trigger is stated in OPPOSITE SENSES.

    MO-PTE instructions: 'If the mileage percentage on Form MO-MS PTE, Page 1,
    is APPLICABLE, or if the taxpayer has included any item of income to be
    allocated ..., the taxpayer must complete Form MO-MS PTE, Part 1, Lines 4
    through 9.'
    MO-MSS / MO-1120S parallel text: '... is INAPPLICABLE or if there is any
    income to be allocated ...'
    The SAME SENTENCE WITH THE OPPOSITE CONDITION. One of the two is inverted
    and NO SOURCE RESOLVES WHICH. The MO-MSS reading is the more coherent one
    (you complete the allocation lines when the mileage percentage alone will
    not do), but MO-MS PTE Line 9 exists PRECISELY to blend allocation into the
    percentage, so the PTE reading is not absurd.
    ⚠ DO NOT GUESS IN CODE -- FLAG.
    """
    raise NotImplementedError(
        "U11 IS UNRESOLVED AND MUST NOT BE GUESSED. The MO-PTE instructions and the MO-MSS / "
        "MO-1120S instructions state the Methods 3-6 trigger for MO-MS PTE Part 1 Lines 4-9 in "
        "OPPOSITE SENSES ('applicable' vs 'inapplicable') and no source resolves which is "
        "inverted. Raise diagnostic D_MO_U11_MILEAGE_TRIGGER and require the preparer to decide. "
        "Settle by a DOR correction."
    )


# ═══════════════════════════════════════════════════════════════════════════
# SCHEDULE PTE-BD -- the entity-level Missouri Business Income Deduction
# ═══════════════════════════════════════════════════════════════════════════
PTE_BD_ROWS = {
    "1": "Ordinary Business Income (Loss)",
    "2": "Net Rental Real Estate Income (Loss)",
    "3": "Other Net Rental Income (Loss)",
    "4": "Partnerships Only - Guaranteed Payments (Total)",
    "5": "Other Income (Loss) (See Instructions)",
    "6": "Section 179 Deduction",
    "7": "Other Deductions (See Instructions)",
}


def pte_bd_line8(column_c: dict) -> dict:
    """Schedule PTE-BD Line 8 -- SUM-THEN-FLOOR (campaign D-12 Group D / W9).

    Face: 'Missouri Source Net Profit - Total of Column (C), Lines 1-7, reduced
    by any negative amounts, but not below $0.'

    ⚠ THAT WORDING IS GENUINELY AMBIGUOUS AND IT CHANGES THE ANSWER (U15):
      (i)  sum everything, THEN floor the total at zero;   <- BUILT
      (ii) DROP the negative rows, then sum (which ignores losses entirely and
           INFLATES the deduction).                         <- recorded, not built
    The instruction restates it identically. §143.022.1 supports (i): business
    income is 'the income greater than zero arising from ... and shall be
    LIMITED TO THE MISSOURI SOURCE NET PROFIT FROM THE COMBINATION OF' the four
    federal schedules -- 'net profit from the COMBINATION' is a sum.

    ⚠ Note also that Lines 6 and 7 are DEDUCTIONS and THE FORM GIVES NO SIGN
    CONVENTION. Returns BOTH readings; only `L8` is operative.
    """
    vals = [float(column_c.get(k, 0.0) or 0.0) for k in PTE_BD_ROWS]
    sum_then_floor = max(0.0, sum(vals))
    drop_then_sum = sum(v for v in vals if v > 0)
    return {
        "L8": sum_then_floor,
        "reading_built": "sum-then-floor (campaign D-12 Group D)",
        "alternative_reading_not_built": drop_then_sum,
        "readings_agree": abs(sum_then_floor - drop_then_sum) < 1e-9,
        "any_negative_row": any(v < 0 for v in vals),
        "sign_convention_unstated": True,
        "authority": ("Mo. Rev. Stat. 143.022.1 -- 'the income greater than zero ... limited to the "
                      "Missouri source net profit from the COMBINATION OF' Schedule C, Schedule E "
                      "Part II, Schedule F and Form 4835."),
        "open_item": "U15 -- settle by a DOR worked example.",
    }


def pte_bd_line9(l8: float, year: int = FORM_TAX_YEAR) -> float:
    """Line 9 = Line 8 Column C x 20% -> Form MO-PTE Line 6.

    ⚠ The 20% is READ OFF THE FACE, not derived from 143.022.4's ratchet.
    """
    return l8 * mo_bid_percent(year)


PTE_BD_COLUMN_A_CARVE_OUT = (
    "'...do not include on Column (A), Lines 1 through 7, any business income that would, IGNORING "
    "SECTION 143.022, RSMo, BE SUBTRACTABLE OR DEDUCTIBLE FOR INDIVIDUAL PARTNERS OR SHAREHOLDERS "
    "in arriving at their Missouri taxable incomes.' The instruction's ONLY example is Agricultural "
    "Disaster Relief. ⚠ U16: on its face this also removes owner-exempt capital gain (143.121.3(14)) "
    "from the BID BASE while the same gain stays in the MO-PTE Line 1 TAX BASE -- an independent, "
    "second-order manifestation of the §11 conflict that cuts the OPPOSITE way (it SHRINKS the "
    "deduction). ⭐ Its existence is also evidence FOR D-10: if the Department believed owner-level "
    "subtractions were imported into the PTE base wholesale, this carve-out would be redundant."
)

PTE_BD_COLUMN_B_RULE = (
    "'Enter the amount from Column (A) that was reportable to INDIVIDUAL MEMBERS, including entities "
    "that are disregarded as separate from individuals for Missouri income tax purposes.' ⭐ The BID "
    "is available only to the extent the entity's income lands on INDIVIDUALS -- a C-corporation or "
    "trust member's share DROPS OUT at Column (B)."
)

PTE_BD_COLUMN_C_RULE = (
    "'The source of income is the place where the income is produced. An item is from Missouri "
    "sources if the item was produced by an overall effort centered in Missouri. In general, if the "
    "\"BRAINS\" OF THE OPERATION resulting in the item are located in Missouri, that item is from "
    "Missouri sources.' ⚠⚠ A THIRD SOURCING REGIME, QUALITATIVE, nowhere in 143.455 and not "
    "mentioned by 12 CSR 10-2.190 or .255. It collides with MO-PTE Line 5 on the ADJACENT LINE. "
    "U17 fully open; DO NOT force them to reconcile."
)

PTE_BD_LINES_5_7_TIEBREAKER = (
    "'When completing this schedule, if the inclusion of an item ... depends on an election or "
    "circumstance applicable only at the individual shareholder or individual partner level, ASSUME "
    "THE ELECTION OR CIRCUMSTANCE APPLIES IF IT WOULD TEND TO DECREASE business income reportable on "
    "this schedule, and ASSUME THE ELECTION OR CIRCUMSTANCE DOES NOT APPLY IF ... IT WOULD TEND TO "
    "INCREASE business income reportable on this schedule.' The DOR's own worked example: IRC "
    "59(e)(2) expenditures -- 'Because this item tends to decrease business income reportable on this "
    "schedule, hypothetically assume for this purpose that all individual partners materially "
    "participate in the business and have elected to deduct Internal Revenue Code Section 59(e)(2) "
    "expenditures in full.' ⭐ A TAXPAYER-ADVERSE MINIMISATION RULE with a printed example. "
    "Deterministic and encodable, but it requires the engine to reason COUNTERFACTUALLY about "
    "owner-level elections -- NOT A v1 COMPUTATION. v1: direct entry with the rule as help copy."
)


# ═══════════════════════════════════════════════════════════════════════════
# THE OPT-OUT -- A RETURN-LEVEL RECOMPUTATION MODE, NOT A MEMBER FLAG
# ═══════════════════════════════════════════════════════════════════════════
MO_OPTOUT_MODE = "return_level_recomputation"
MO_OPTOUT_RECOMPUTE_SCOPE = (
    "Form MO-PTE Line 1 (the 702(a)/1366 base)",
    "every Part A modification, Lines 1a-12",
    "Schedule PTE-BD in full (Columns A, B and C)",
    "the Part B credit split (the re-gross-up)",
)


def mo_member_percentages(k1_percent: float, opt_out_percent_total: float = 0.0,
                          is_opt_out: bool = False) -> dict:
    """Return the K-1 percentage and the CREDIT-ALLOCATION percentage as TWO
    SEPARATE FIELDS. ⚠⚠ NEVER OVERWRITE ONE WITH THE OTHER. (D-12 Group D)

    MO-PTE Part B Column 5 is LABELLED `Membership %` but SILENTLY CHANGES
    MEANING when any member opts out. Verbatim: 'If any member has made an
    opt-out election, the remaining participating members' percentage must be
    adjusted to allow the full amount of tax paid, to be properly allocated.
    For example, if an S corporation has an opt-out member with a share of 30%,
    and a non-opt-out member with a share percentage of 10%, then that
    non-opt-out member's new credit percentage is 14% (10% divided by 70%).'
    That is the unit test: 10 / 70 -> 14.00.
    """
    if is_opt_out:
        # 12 CSR 10-2.436(12)(C): the opt-out member is INELIGIBLE for the
        # credits 143.436.8 and .10 would otherwise grant.
        return {
            "k1_percent": k1_percent,
            "credit_percent": None,
            "eligible_for_credit": False,
            "part_b_col3_opt_out": True,
            "part_b_col6_blank": True,
            "part_b_col7_not_eligible": True,
            "note": ("12 CSR 10-2.436(12)(C). ⚠ SAVING CLAUSE: this 'shall not be construed to "
                     "affect an opt-out member's authorization to CARRY FORWARD AND REDEEM "
                     "OUTSTANDING TAX CREDITS THAT WERE INITIALLY ALLOWED FOR A TAX YEAR TO WHICH "
                     "THE OPT-OUT ELECTION DID NOT APPLY' -- an opt-out member can still be burning "
                     "a pre-opt-out carryforward."),
        }
    remaining = 100.0 - float(opt_out_percent_total)
    if remaining <= 0:
        raise ValueError(
            "Opt-out percentages total 100 percent or more; no participating member remains to "
            "carry the credit. Review the member roster before filing.")
    unrounded = 100.0 * float(k1_percent) / remaining
    credit_percent = _round_half_up(unrounded, MO_ROUND_PARTB_SHARE_DECIMALS)
    return {
        "k1_percent": k1_percent,                 # ⚠ the ORIGINAL, never overwritten
        "credit_percent": credit_percent,         # ⚠ a DIFFERENT field
        "credit_percent_unrounded": unrounded,
        # ⚠⚠ See MO_OPTOUT_EXAMPLE_ROUNDING_DEFECT. The DOR's printed "14%" is a
        # WHOLE-NUMBER illustration that contradicts the SAME COLUMN's own
        # two-decimal instruction. Reproduced here so the example can be
        # verified on its own terms without letting it drive the field.
        "dor_example_whole_number": _round_half_up(unrounded, 0),
        "eligible_for_credit": True,
        "regrossed": bool(opt_out_percent_total),
        "denominator_percent": remaining,
        "part_b_col3_opt_out": False,
        "part_b_col6_blank": False,
        "part_b_col7_not_eligible": False,
        "note": ("⚠ Column 5 prints the CREDIT percentage when any member has opted out, under a "
                 "label that still says `Membership %`. The K-1 percentage survives as its own "
                 "field. ⚠⚠ THE DOR'S OWN WORKED EXAMPLE IS ROUNDED INCONSISTENTLY WITH ITS OWN "
                 "COLUMN INSTRUCTION: 10 / 70 = 14.285714...%, which is 14.29% at the TWO DECIMAL "
                 "PLACES the same column mandates, but the Department prints '14%'. See "
                 "MO_OPTOUT_EXAMPLE_ROUNDING_DEFECT."),
    }


# ⚠⚠ A DOR DEFECT THE SOURCE BRIEF DID NOT CATCH, SURFACED BY THE HARNESS.
#
# Campaign D-12 Group D directs: "use DOR's own 10 / 70 = 14% example as a unit
# test". That example CANNOT be a two-decimal unit test, because MO-PTE Part B
# Column 5's OWN instruction -- one sentence earlier on the same page -- says
# "Round the percentage to the nearest TWO DECIMAL PLACES", and
# 10 / 70 = 14.285714...%, i.e. **14.29%**, not 14.00%.
#
# The Department's illustration is rounded to a WHOLE NUMBER, contradicting the
# rounding rule it prints for the very column it is illustrating. It matters:
# Column 5 must foot to 100.00% across the participating members, and a
# whole-number allocation will not close. Example: opt-out 30%, and three
# participating members at 10% / 25% / 35%. Two decimals gives
# 14.29 + 35.71 + 50.00 = 100.00. Whole numbers give 14 + 36 + 50 = 100 only by
# luck, and 14 + 35 + 50 = 99 as easily.
#
# ENCODED POSITION: compute at TWO DECIMALS (the printed column rule), and
# reproduce the Department's whole-number illustration alongside it so the
# example verifies on its own terms without driving the field. Diagnostic
# D_MO_OPTOUT_EXAMPLE_ROUNDING carries it. ESCALATED to Ken as an
# under-specified unit test in the ruling, not a defect in the ruling's
# substance -- the two-field rule it was protecting is unaffected.
MO_OPTOUT_EXAMPLE_ROUNDING_DEFECT = {
    "dor_printed_example": "14% (10% divided by 70%)",
    "exact": 100.0 * 10.0 / 70.0,
    "at_two_decimals": 14.29,
    "at_whole_numbers": 14.0,
    "column_rounding_rule": ("MO-PTE Part B Column 5, verbatim: 'Round the percentage to the "
                             "nearest two decimal places.'"),
    "encoded": "TWO DECIMALS (the printed column rule)",
    "why_it_matters": ("Column 5 must foot to 100.00% across the participating members after the "
                       "re-gross-up; a whole-number allocation does not reliably close."),
    "status": ("ESCALATED - the ruling's named unit test is under-specified. The SUBSTANCE of the "
               "ruling (two separate percentage fields, never overwritten) is unaffected."),
}


MO_OPTOUT_AVAILABILITY_GATE = (
    "⚠ THE INSTRUCTION SENTENCE IS CONJUNCTIVE AND ITS SECOND LIMB IS EASILY DROPPED. MO-PTE "
    "Instructions p.2, verbatim: 'The opt-out option is only allowed for members of an affected "
    "business entity if the affected business entity's original (un-extended) MO-PTE filing deadline "
    "is on or after August 28, 2025, AND THE AFFECTED BUSINESS ENTITY HAS NOT FILED ITS ORIGINAL "
    "RETURN BY THAT DATE.' ENCODE BOTH LIMBS. (22 correction #8)"
)
MO_OPTOUT_GATE_DIVERGENCE = (
    "THREE-WAY DIVERGENCE, no TY2025 impact, MATERIAL FOR TY2024 AMENDED RETURNS (U2): the MO-PTE "
    "instructions say the un-extended deadline must fall on or after 2025-08-28; the DOR FAQ says "
    "'affected business entities whose tax year ends on or after AUGUST 28, 2024'; and 143.436.5(2)-(4) "
    "(eff. 2024-08-28, NO 2025 amendment -- reproduced independently on the verification pass) plus "
    "12 CSR 10-2.436(12) (eff. 2025-09-30) impose NO DATE GATE AT ALL. A calendar-2025 entity "
    "satisfies every version."
)


def mo_optout_available(unextended_due_date: str, original_return_filed_by_that_date: bool) -> dict:
    """BOTH limbs of the conjunctive gate. (22 correction #8)"""
    limb_1 = unextended_due_date >= "2025-08-28"
    limb_2 = not original_return_filed_by_that_date
    return {
        "available": limb_1 and limb_2,
        "limb_1_deadline_on_or_after_2025_08_28": limb_1,
        "limb_2_original_return_not_yet_filed": limb_2,
        "gate_text": MO_OPTOUT_AVAILABILITY_GATE,
        "divergence": MO_OPTOUT_GATE_DIVERGENCE,
    }


MO_OPTOUT_MEMBER_FORM_DEADLINE = (
    "12 CSR 10-2.436(12)(A), and printed on both forms: the OPT-OUT MEMBER -- not the entity -- "
    "files Form MO-PTENR (nonresident) or Form MO-PTE Opt-Out (resident) with the Department by "
    "THE EARLIER OF the original (UN-EXTENDED) due date of the Form MO-PTE for that tax year OR "
    "the ACTUAL FILING DATE of the Form MO-PTE, and furnishes a copy to the entity."
)

# ⚠ D-12 Group D: PRINT NO SCANLINE AT ALL ON MO-PTE OPT-OUT IN v1.
MO_PTE_OPTOUT_SCANLINE_DEFECT = {
    "human_readable": "25125010001",
    "printed_barcode": "*25329010001*",
    "barcode_actually_belongs_to": "Form MO-3NR",
    "form_vintage": "Revised 03-2026, PDF ModDate 2026-03-27 (a FINAL form)",
    "ruling": "PRINT NO SCANLINE AT ALL ON THIS FORM IN v1",
    "why": ("Reproducing a wrong barcode is WORSE than omitting one: it would route the document to "
            "the wrong DOR process. Correcting it would deviate from the published form. Omitting "
            "it does neither. (U27; campaign D-12 Group D)"),
}
MO_PTE_OPTOUT_PRINT_SCANLINE = False


# ═══════════════════════════════════════════════════════════════════════════
# C5 -- THE CREDIT-POISONING RULE. A LIVE CLIENT-HARM PATH.
#
# Using an entity-level MO-TC credit DESTROYS the members' credit, and the
# engine has NO FIELD for "tax actually paid". Three sources say it:
#   MO-PTE instructions L11: "miscellaneous tax credits reduce tax liability
#     under the SALT Parity Act, RATHER THAN CONSTITUTING TAX PAID, and
#     therefore do not qualify as payments for purposes of calculating the PTE
#     credit for a member."
#   MO-PTE Part B Col 6: the member's credit is the pro rata share of Line 12
#     "TO THE EXTENT PAID."
#   12 CSR 10-2.436(11): "...computed based on the member's direct and indirect
#     pro rata share of THE TAX ACTUALLY PAID ... If an affected business entity
#     reduces its tax liability under section 143.436, RSMo, by use of tax
#     credits, other than a credit for payment or overpayment of this tax, the
#     affected business entity's TAX ACTUALLY PAID WILL GENERALLY BE REDUCED."
# ═══════════════════════════════════════════════════════════════════════════
MO_TC_ALPHA_CODE_SALT_PARITY = "SPA"
MO_TC_SPA_ROW_VERBATIM = "SPA    SALT Parity    Fed. K-1, Form 5889 or equivalent."
MO_TC_COLUMN_FOR_PTE = 1     # "A corporation income tax return, PASS-THROUGH ENTITY INCOME TAX, or fiduciary return."
MO_TC_ORDERING_RULE = (
    "Printed on the MO-TC face: 'Each credit will apply against your tax liability IN THE ORDER "
    "THEY APPEAR BELOW.' -- credit ordering is PREPARER-CONTROLLED BY ROW POSITION, never "
    "engine-determined."
)
MO_TC_BENEFIT_NUMBER_RULE = (
    "'The number is the last six (6) digits of the number located on your Certificate of "
    "Eligibility. Example: For benefit, ABC-2018-12345-123456, enter 123456.'"
)
MO_TC_OVERFLOW_RULE = "'If you are claiming more than 10 credits, attach additional MO-TC(s).'"


def mo_tax_actually_paid(l10_tax: float, l11_mo_tc_credits: float,
                         cash_payments_applied: float,
                         refundable_credit_excess: float = 0.0,
                         count_refundable_excess_as_paid: bool = False) -> dict:
    """The DERIVED field the form does not have. Feeds MO-PTE Part B Column 6.

    Line 12 = max(0, L10 - L11) is ALREADY net of MO-TC, so the credit pool is
    bounded by Line 12 -- and then bounded AGAIN by what was actually PAID.
    An entity filing with a balance due, or paying late, has a credit pool that
    DOES NOT EQUAL Line 12. (U20 / campaign D-12 C5)

    ⚠ `refundable_credit_excess` (MO-PTE Line 13) is NOT counted as tax paid by
    default and the Department has never said whether it should be. That is an
    OPEN QUESTION, surfaced rather than silently decided.
    """
    l12 = max(0.0, float(l10_tax) - float(l11_mo_tc_credits))
    paid = float(cash_payments_applied)
    if count_refundable_excess_as_paid:
        paid += float(refundable_credit_excess)
    pool = max(0.0, min(l12, paid))
    return {
        "L10": l10_tax,
        "L11": l11_mo_tc_credits,
        "L12": l12,
        "tax_actually_paid": pool,
        "member_credit_pool": pool,
        "pool_equals_l12": abs(pool - l12) < 1e-9,
        "mo_tc_used": float(l11_mo_tc_credits) > 0,
        "harm": (float(l11_mo_tc_credits) > 0) or (pool < l12),
        "severity": "error" if float(l11_mo_tc_credits) > 0 else
                    ("warning" if pool < l12 else None),
        "authority": ("MO-PTE Part B Column 6 ('to the extent paid'); MO-PTE Instructions Line 11; "
                      "12 CSR 10-2.436(11)"),
        "open_item": ("U20 -- the form has NO field for tax actually paid and the DOR has published "
                      "no worked example. Whether the Line 13 excess REFUNDABLE credit counts as "
                      "'tax actually paid' is UNANSWERED; this build does not count it and says so."),
        "refundable_excess_counted": count_refundable_excess_as_paid,
    }


MO_CREDIT_CARRYFORWARD_RULES = {
    "143.436.8": {
        "who": "individual / part-year / nonresident member",
        "credit": "the member's DIRECT AND INDIRECT pro rata share of the tax paid",
        "against": "Mo. Rev. Stat. 143.011 or 143.041",
        "excess": ("143.436.8(2): 'shall not be refunded but MAY BE CARRIED FORWARD to each "
                   "succeeding tax year until such credit is fully taken' -- UNLIMITED carryforward"),
    },
    "143.436.10": {
        "who": "corporation or fiduciary member",
        "credit": "the same pro-rata-share formula",
        "against": "143.071 (corporations) / 143.061 (fiduciaries)",
        "excess": "143.436.10(2): the SAME unlimited carryforward",
        "note": "⭐ 'Such credit shall be APPLIED AFTER ALL OTHER CREDITS.'",
    },
    "143.436.9": {
        "who": "Missouri RESIDENT member of an OUT-OF-STATE pass-through entity",
        "credit": ("pro rata share of taxes paid to another state under a program 'the director of "
                   "revenue determines is SUBSTANTIALLY SIMILAR'; 'the limitations provided in "
                   "subsection 2 of section 143.081 shall apply'"),
        "against": "143.011",
        "excess": ("⚠⚠ 143.436.9(2): the excess amount 'SHALL NOT BE REFUNDED AND SHALL NOT BE "
                   "CARRIED FORWARD' -- it DIES IN THE YEAR IT ARISES."),
        "note": ("⚠⚠ TWO CREDITS, TWO OPPOSITE CARRYFORWARD RULES, EASY TO CONFLATE. The reciprocal "
                 "credit is claimed on Form MO-CR, an INDIVIDUAL-module form -- out of scope here "
                 "but a hard dependency. (R3)"),
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# C6 -- THE PTE ELECTION DOES **NOT** SWITCH OFF NONRESIDENT WITHHOLDING
# ═══════════════════════════════════════════════════════════════════════════
MO_WH_SURVIVES_ELECTION = True
MO_WH_SURVIVES_ELECTION_AUTHORITY = "12 CSR 10-2.436(8)"
MO_WH_SURVIVES_ELECTION_VERBATIM = (
    "The election to become an affected business entity does not relieve a partnership or S "
    "corporation of its withholding obligations under section 143.411.5, RSMo, or section "
    "143.471.6, RSMo, respectively."
)
MO_WH_SURVIVES_ELECTION_NOTE = (
    "⭐ THE SINGLE MOST EASILY-MISSED OBLIGATION IN THE MISSOURI PTE LANE. Most PTET states suspend "
    "nonresident withholding for electing entities. MISSOURI DOES NOT. An electing Missouri "
    "partnership with a nonresident individual partner files MO-PTE **and** MO-1NR / MO-2NR and "
    "withholds 4.7% -- ON TOP OF paying 4.7% entity tax ON THE SAME INCOME. ⚠ It is stated ONLY in "
    "the regulation: nowhere on Form MO-PTE, nowhere in the MO-PTE instructions, nowhere in the DOR "
    "PTE FAQ. A tension sits alongside it -- 143.436.6 relieves a nonresident individual member of "
    "the FILING obligation where the entity files and pays, and 'not otherwise required to file' is "
    "a PRECONDITION of two of the five withholding exceptions but is not itself an exception. THE "
    "REGULATION RESOLVES IT AGAINST THE TAXPAYER: WITHHOLD ANYWAY. (U21 / campaign D-12 C6)"
)

# Owners in scope for withholding, verbatim from Form MO-2NR:
#   "ONLY INDIVIDUAL nonresident partners or S corporation shareholders are
#    subject to withholding. Do not withhold for any partners or S corporation
#    shareholders who are partnerships, corporations, trusts, or estates.
#    Grantor trusts that file or can file in accordance with IRC Reg. Section
#    1.671.4(b) ARE CONSIDERED INDIVIDUALS."
MO_WH_OWNER_KINDS_IN_SCOPE = ("individual", "grantor_trust_1671_4b")
MO_WH_OWNER_KINDS_OUT_OF_SCOPE = ("partnership", "corporation", "s_corporation", "trust", "estate")

# ⚠ D-12 Group D: BUILD THE NARROW, CONJUNCTIVE FORM READING. RECORDED AS A
# RULING, NOT A FINDING.
MO_WH_EXCEPTIONS_STATUTE_VERBATIM = (
    "143.411.5 (143.471.6 is word-for-word parallel): 'A partnership is not required to deduct and "
    "withhold Missouri income tax for a nonresident partner if: (1) The nonresident partner not "
    "otherwise required to file a return agrees to have the Missouri income tax due paid as part of "
    "the partnership's composite return; (2) The nonresident partner not otherwise required to file "
    "a return had Missouri assignable federal adjusted gross income from the partnership of less "
    "than twelve hundred dollars; (3) The partnership is liquidated or terminated; (4) Income was "
    "generated by a transaction related to termination or liquidation; OR (5) No cash or other "
    "property was distributed in the current and prior taxable year.'"
)
MO_WH_EXCEPTIONS_READING = "NARROW / CONJUNCTIVE (the FORM reading) -- RULED, campaign D-12 Group D"
MO_WH_EXCEPTIONS_RULING_NOTE = (
    "⚠⚠ THE STATUTORY 'or' BEFORE (5) WOULD, READ LITERALLY, EXEMPT FROM WITHHOLDING EVERY "
    "PARTNERSHIP THAT MADE NO DISTRIBUTIONS IN TWO YEARS -- i.e. most closely-held partnerships. "
    "That cannot be the intent and NO FORM READS IT THAT WAY: every FINAL form collapses (3)(4)(5) "
    "into ONE CONJUNCTIVE exception. This is the same statute-vs-form shape as the capital-gain "
    "question and it bites in the OPPOSITE direction -- here the FORM IS NARROWER THAN THE STATUTE. "
    "BUILD TO THE FORM, per D-10's principle. RECORDED AS A RULING. (U22) ⚠ The forms also disagree "
    "WITH EACH OTHER on the distribution test: MO-1065 says 'in the current OR prior taxable year'; "
    "MO-1120S says 'in BOTH the current and prior taxable year'; the statute says 'in the current "
    "AND prior taxable year'. THREE RENDERINGS OF ONE CONDITION."
)

MO_WH_EXCEPTIONS = (
    {"id": "composite", "text": "the owner, not otherwise required to file, is included on the "
     "partnership's / S corporation's composite return", "statute": "143.411.5(1) / 143.471.6(1)"},
    {"id": "de_minimis", "text": "the owner, not otherwise required to file, had Missouri "
     "assignable federal AGI from the entity of LESS THAN $1,200",
     "statute": "143.411.5(2) / 143.471.6(2)"},
    {"id": "liquidation_conjunctive", "text": "⚠ THE COLLAPSED ONE: the entity is liquidated or "
     "terminated, AND the income was generated by a transaction related to that termination or "
     "liquidation, AND no cash or property was distributed in the current or prior taxable year",
     "statute": "143.411.5(3)(4)(5) / 143.471.6(3)(4)(5), collapsed CONJUNCTIVELY by every form"},
    {"id": "mo_3nr", "text": "the owner has a Form MO-3NR withholding exemption agreement on file "
     "and unrevoked", "statute": "143.411.6 / the MO-3NR face"},
)


def mo_withholding_required(owner_kind: str, missouri_source_income: float,
                            pte_election_made: bool = False,
                            on_composite: bool = False,
                            mo_3nr_on_file: bool = False,
                            liquidation_all_three_limbs: bool = False,
                            year: int = FORM_TAX_YEAR) -> dict:
    """⚠⚠ `pte_election_made` DELIBERATELY DOES NOT SWITCH WITHHOLDING OFF.

    12 CSR 10-2.436(8). Campaign D-12 C6. The parameter is accepted only so the
    caller cannot pass it and quietly assume it was honoured -- it is recorded
    in the result and the diagnostic fires.
    """
    if owner_kind not in MO_WH_OWNER_KINDS_IN_SCOPE:
        return {"required": False, "reason": "owner entity type out of scope",
                "issue_mo_2nr": False,
                "note": ("Form MO-2NR: 'Only INDIVIDUAL nonresident partners or S corporation "
                         "shareholders are subject to withholding. Do not withhold for any partners "
                         "or S corporation shareholders who are partnerships, corporations, trusts, "
                         "or estates.' Grantor trusts under Reg. 1.671-4(b) ARE considered "
                         "individuals.")}
    if on_composite:
        # "DO NOT withhold for any partners or shareholders who include their
        #  Missouri income on a composite return." AND do not issue MO-2NR.
        return {"required": False, "reason": "included on a composite return",
                "issue_mo_2nr": False, "exception": "composite"}
    exception = None
    if mo_3nr_on_file:
        exception = "mo_3nr"
    elif float(missouri_source_income) < _yk(MO_WH_DE_MINIMIS, year):
        exception = "de_minimis"
    elif liquidation_all_three_limbs:
        exception = "liquidation_conjunctive"
    required = exception is None
    return {
        "required": required,
        "exception": exception,
        "rate": mo_withholding_rate(year),
        "amount": round(float(missouri_source_income) * mo_withholding_rate(year), 2)
        if required else 0.0,
        # ⚠ A ZERO-DOLLAR MO-2NR IS STILL REQUIRED. Verbatim: "Issue Form
        # MO-2NR, even if no tax is withheld or there is an exemption
        # certificate on file."
        "issue_mo_2nr": True,
        "pte_election_made": pte_election_made,
        "election_relieved_withholding": False,     # ⚠⚠ ALWAYS False. C6.
        "election_note": MO_WH_SURVIVES_ELECTION_NOTE if pte_election_made else None,
        "exceptions_reading": MO_WH_EXCEPTIONS_READING,
        "alternative_rate_basis": ("or the Missouri withholding tables, if the owner submits a "
                                   "Missouri Withholding Allowance Certification (Form MO W-4)"),
    }


# ═══════════════════════════════════════════════════════════════════════════
# U9 -- THE WITHHOLDING BASE SUMMATIONS ARE DEFECTIVE AS PRINTED
# ═══════════════════════════════════════════════════════════════════════════
MO_1NR_BASE_VERBATIM = (
    "'Missouri source distributive income consists of those items on an individual's K-1 schedule "
    "that are used to arrive at federal adjusted gross income as apportioned or allocated to "
    "Missouri. The Missouri source distributive income of PARTNERSHIPS is the net total of the "
    "amounts listed on LINES 1 THROUGH 11 of the Nonresident Partnership Form (Form MO-NRP). The "
    "Missouri source distributive income of S CORPORATIONS is the net total of the amounts listed on "
    "LINES 1 THROUGH 10 of the S Corporation Nonresident Form (Form MO-NRS).'"
)

# MO-NRP Part 1's line set is NON-CONTIGUOUS as the DOR prints it.
MO_NRP_PART1_LINES = ("1", "2", "3c", "4a", "5", "10", "11", "12", "13", "13e")
MO_NRP_WH_BASE_LINES = ("1", "2", "3c", "4a", "5", "10", "11")
MO_NRP_WH_BASE_EXCLUDED = ("12", "13", "13e")   # 179, contributions, other deductions

MO_NRS_PART1_LINES = ("1", "2", "3", "4", "5a", "5b", "6", "7", "8a", "8b", "8c", "9", "10",
                      "11", "12a", "12b", "12c", "12d", "12e")
MO_NRS_WH_BASE_LINES = ("1", "2", "3", "4", "5a", "6", "7", "8a", "9", "10")
# ⚠ SUBSETS, SUPPRESSED. 5b subset of 5a; 8b and 8c subsets of 8a.
MO_NRS_SUBSET_LINES = {"5b": "5a", "8b": "8a", "8c": "8a"}


def mo_nrp_withholding_base(part1_column_e: dict) -> dict:
    """Partnership withholding base -- MO-NRP Part 1 Lines 1 through 11.

    ⚠ 'Lines 1 through 11' over a NON-CONTIGUOUS line set captures
    1, 2, 3c, 4a, 5, 10, 11 and SILENTLY EXCLUDES Line 12 (179), Line 13
    (contributions) and Line 13e (other deductions). Whether that exclusion is
    deliberate (a gross-ish base) or an accident of the DOR's own numbering is
    NOT STATED. Built as printed, with the exclusion surfaced. (U9)
    ⚠ MO-NRP Line 5 is itself a ROLL-UP of federal Schedule K Lines 5-9a, so it
    already contains interest, dividends, royalties and capital gains.
    """
    included = {k: float(part1_column_e.get(k, 0.0) or 0.0) for k in MO_NRP_WH_BASE_LINES}
    excluded = {k: float(part1_column_e.get(k, 0.0) or 0.0) for k in MO_NRP_WH_BASE_EXCLUDED}
    return {
        "base": sum(included.values()),
        "lines_included": MO_NRP_WH_BASE_LINES,
        "lines_excluded": MO_NRP_WH_BASE_EXCLUDED,
        "excluded_amounts": excluded,
        "excluded_total": sum(excluded.values()),
        "requires_human_review": any(v for v in excluded.values()),
        "defect": ("The DOR's 'Lines 1 through 11' reads over a NON-CONTIGUOUS set "
                   f"({', '.join(MO_NRP_PART1_LINES)}), silently dropping IRC 179, contributions "
                   "and other deductions. THIS DETERMINES CASH WITHHELD. Get a DOR worked example "
                   "before season. (U9)"),
    }


def mo_nrs_withholding_base(part1_column_e: dict) -> dict:
    """S-corporation withholding base -- MO-NRS Part 1 Lines 1 through 10,
    WITH THE SUBSET LINES SUPPRESSED. (campaign D-12 Group D / U9)

    ⚠ A LITERAL sum DOUBLE-COUNTS: `5b Qualified dividends` is a SUBSET of
    `5a Ordinary dividends`, and `8b Collectibles (28%) gain` and
    `8c Unrecaptured section 1250 gain` are both SUBSETS of `8a Net long-term
    capital gain`. A literal sum overstates the base by `5b + 8b + 8c`.
    """
    included = {k: float(part1_column_e.get(k, 0.0) or 0.0) for k in MO_NRS_WH_BASE_LINES}
    subsets = {k: float(part1_column_e.get(k, 0.0) or 0.0) for k in MO_NRS_SUBSET_LINES}
    literal = sum(included.values()) + sum(subsets.values())
    return {
        "base": sum(included.values()),
        "literal_sum_would_be": literal,
        "overstatement_avoided": literal - sum(included.values()),
        "lines_included": MO_NRS_WH_BASE_LINES,
        "subset_lines_suppressed": MO_NRS_SUBSET_LINES,
        "subset_amounts": subsets,
        # ⚠ requires_human_review on ANY return where 5b, 8b or 8c is non-zero.
        "requires_human_review": any(v for v in subsets.values()),
        "defect": ("MO-NRS Part 1 Lines 1-10 DOUBLE-COUNT as literally summed: 5b is a subset of 5a, "
                   "and 8b and 8c are subsets of 8a. The instruction also excludes Line 11 (IRC 179) "
                   "and Lines 12a-12e (deductions). THIS DETERMINES CASH WITHHELD. (U9)"),
    }


def mo_name_control(last_name: str) -> str:
    """Form MO-2NR's printed Name Control algorithm, with the DOR's own examples.

    Verbatim: 'Enter the first four letters of the partner's/shareholder's last
    name. (Please use all capital letters as shown.) John Brown--BROW, Juan
    DeJesus--DEJE, Joan A. Lee--LEE, Pedro Torres-Lopes--TORR, Jean
    McCarty--MCCA, John O'Neill--ONEI.'
    ⭐ Note what the examples PROVE: hyphens SPLIT (only the first segment is
    used), apostrophes are DROPPED, and SHORT NAMES ARE NOT PADDED (LEE is
    three characters).
    """
    name = (last_name or "").strip()
    name = name.split("-")[0]                    # Torres-Lopes -> Torres
    name = name.replace("'", "").replace("’", "")   # O'Neill -> ONeill
    name = "".join(ch for ch in name if ch.isalpha())
    return name.upper()[:4]                      # Lee -> LEE, NOT padded


MO_NAME_CONTROL_EXAMPLES = (
    ("Brown", "BROW"), ("DeJesus", "DEJE"), ("Lee", "LEE"),
    ("Torres-Lopes", "TORR"), ("McCarty", "MCCA"), ("O'Neill", "ONEI"),
)

MO_1NR_SEQUENCING_RULE = (
    "'Form MO-1NR, payment and a copy of the Form MO-2NR MUST BE FILED WITH THE DEPARTMENT EITHER "
    "BEFORE OR AT THE SAME TIME the partnership or S corporation provides a copy of the Form MO-2NR "
    "to the nonresident partner or S corporation shareholder. FAILURE TO DO SO MAY RESULT IN THE "
    "DEPARTMENT DISALLOWING THE WITHHOLDING CLAIMED by the nonresident partner or S corporation "
    "shareholder.'"
)


# ═══════════════════════════════════════════════════════════════════════════
# DUE DATES, EXTENSIONS AND PAYMENTS
#
# ⭐ ONE Missouri PTE-lane due date -- the 15th day of the 4th month -- but
# FIVE DIFFERENT DEADLINE *BEHAVIOURS*, and that is where the complexity lives.
# ═══════════════════════════════════════════════════════════════════════════
MO_DUE_DATE_RULE = "the 15th day of the 4th month following the close of the taxable year"
MO_DUE_DATE_TY2025_CALENDAR = "2026-04-15"
MO_WEEKEND_HOLIDAY_ROLLOVER = (
    "'When the due date falls on a Saturday, Sunday, or a legal holiday, the return and payment "
    "will be considered timely if made on the next business day.'"
)

MO_DEADLINE_BEHAVIOURS = {
    FORM_CODE_MO1065: "original or extended (federal Form 7004 extends it automatically)",
    FORM_CODE_MO1120S: "original or extended (federal Form 7004 extends it automatically)",
    FORM_CODE_MOPTE: "original or extended (federal 7004 or Form MO-7004), six-month cap",
    "MO-1NR / MO-2NR": "the ORIGINAL **or EXTENDED** due date of the MO-1065 / MO-1120S",
    "MO-3NR": "⚠ the due date WITHOUT REGARD TO AN EXTENSION -- a DIFFERENT clock on an adjacent form",
    "MO-PTENR / MO-PTE Opt-Out": ("the EARLIER OF the original (un-extended) MO-PTE due date OR the "
                                  "ACTUAL FILING DATE of the MO-PTE"),
    "the 143.436 election itself": ("the filing deadline INCLUDING any approved extension -- 12 CSR "
                                    "10-2.436(3): 'No election can be made after the deadline, "
                                    "including any approved extension.' The election SURVIVES an "
                                    "extension; it just cannot be made late."),
    "federal-adjustment amended return": "within 90 days (12 CSR 10-2.105; 143.601; 143.436.12)",
}


def mo_extension(form_code: str) -> dict:
    """⚠ THE DOR'S OWN EXTENSION FORMS CONTRADICT EACH OTHER. (U24)

    MO-7004 tells S corporations to 'use Form MO-60'; MO-60 has NO S-CORP
    CHECKBOX and tells S corporations to ride the federal 7004; MO-1120S names
    no Missouri form; MO-1065 appears on neither form. And MO-7004 says the
    extension runs 'up to 180 DAYS' while the MO-PTE instructions say 'not to
    exceed SIX MONTHS'.

    BUILD POSITION (to the form faces, per D-10's principle):
      MO-PTE   -> Form MO-7004 (it HAS the checkbox and the P.O. Box 3080 routing)
      MO-1120S -> attach federal Form 7004; NO Missouri extension form
      MO-1065  -> attach federal Form 7004; NO Missouri extension form
    """
    common = {
        "max_months": MO_EXTENSION_MAX_MONTHS,
        "conflict": (f"MO-7004's instructions say 'up to {MO_EXTENSION_MO7004_DAYS_CLAIM} days'; "
                     f"the MO-PTE instructions say 'not to exceed six months'. 180 days is not six "
                     f"months for most calendar windows. (U24)"),
        "diagnostic_if_user_asks_for_mo_60": True,
    }
    if form_code == FORM_CODE_MOPTE:
        return {**common,
                "missouri_form": "MO-7004",
                "federal_form_attached": "Form 7004",
                # ⭐⭐ THE PAYMENT RULE IS INVERTED FOR MO-PTE ONLY.
                "extension_extends_payment": True,
                "late_pay_addition_waived_if_paid_by_extended_date": True,
                "interest_runs_from": "the ORIGINAL return due date",
                "note": ("⭐⭐ MO-PTE ONLY: 'An extension of time to file WILL EXTEND THE TIME FOR "
                         "PAYMENT of the tax. The pass-through entity must pay the tax on or before "
                         "the extended due date to avoid a 5 percent addition to tax. However, "
                         "SIMPLE INTEREST WILL BE CALCULATED FROM THE ORIGINAL RETURN DUE DATE until "
                         "the tax is paid.' Corroborated by 12 CSR 10-2.436(9) ('likewise granted an "
                         "equal extension of time for the payment of the tax due ... Pursuant to "
                         "section 143.731.2, RSMo, interest on this tax will continue to accrue "
                         "regardless of any extension of time for payment') and by MO-7004's own "
                         "PTE-specific sentence. THIS IS THE OPPOSITE of the general Missouri rule "
                         "AND of Virginia. DO NOT SHARE THIS BRANCH WITH MO-1065 / MO-1120S."),
                "mail_to": "P.O. Box 3080, Jefferson City, MO 65105-3080"}
    if form_code in (FORM_CODE_MO1065, FORM_CODE_MO1120S):
        return {**common,
                "missouri_form": None,
                "federal_form_attached": "Form 7004",
                "extension_extends_payment": False,
                "late_pay_addition_waived_if_paid_by_extended_date": False,
                "interest_runs_from": "the original return due date",
                "note": ("Check the extension box on the face and ATTACH the approved federal Form "
                         "7004. '(Failure to check this box and provide a copy of the extension may "
                         "result in disallowing the extension.)' ⚠ MO-7004 says S corporations "
                         "should use Form MO-60; MO-60 has no S-corp checkbox and says the opposite. "
                         "Build to the return's own face. (U24)")}
    raise ValueError(f"unknown Missouri form code {form_code!r}")


MO_INTEREST_RATE_STATUS = (
    "NOT PRINTED ON ANY FORM. Every form points to dor.mo.gov/taxation/statutory-interest-rates.html, "
    "which was NOT FETCHED. Statutory hook Mo. Rev. Stat. 143.731. DIRECT ENTRY until the page is "
    "pulled -- trivially fetchable, just not yet done. (U25)"
)

MO_MAIL_ROUTING = {
    "MO-1065 / MO-NRP": ("P.O. Box 3000, Jefferson City, MO 65105-3000", "(573) 751-1467",
                         "income@dor.mo.gov"),
    "MO-1120S / MO-NRS / MO-MSS": ("P.O. Box 336, Jefferson City, MO 65105-0336", "(573) 751-4541",
                                   "corporate@dor.mo.gov"),
    "MO-PTE / MO-MS PTE / PTE-BD / MO-PTEV / MO-PTEAP / MO-PTENR / MO-PTE Opt-Out":
        ("P.O. Box 3080, Jefferson City, MO 65105-3080", "(573) 751-4541", "pteincome@dor.mo.gov"),
    "MO-1NR / MO-2NR": ("P.O. Box 555, Jefferson City, MO 65105-0555", "(573) 751-3505",
                        "income@dor.mo.gov"),
    "MO-3NR": ("P.O. Box 3815, Jefferson City, MO 65105-3815", "(573) 751-1467", "income@dor.mo.gov"),
    "MO-7004 (PTE selection)": ("P.O. Box 3080", "(573) 751-4541", "corporate@dor.mo.gov"),
}
MO_MAIL_ROUTING_NOTE = (
    "⭐ AN ELECTING MISSOURI PARTNERSHIP WITH ONE NONRESIDENT PARTNER MAILS TO FOUR DIFFERENT P.O. "
    "BOXES IN ONE FILING. The print/assembly engine must model PER-FORM routing, not per-return."
)


# ═══════════════════════════════════════════════════════════════════════════
# FORM 5889 -- MAP BY SUBSTANCE, NOT BY THE STALE COLUMN NUMBERS
# ═══════════════════════════════════════════════════════════════════════════
MO_5889_STALE_MAP = {
    "Line 1": "Form 5889 says 'Form MO-PTE, Part B, Column 4' -- Column 4 is `Social Security "
              "Number or FEIN`.",
    "Line 2": "Form 5889 says 'Form MO-PTE, Part B, Column 5' -- Column 5 is `Membership %`.",
}
MO_5889_SUBSTANCE_MAP = {
    "Line 1 (Membership Percentage)": "MO-PTE Part B COLUMN 5",
    "Line 2 (Member's PTE Tax Credit)": "MO-PTE Part B COLUMN 6",
}
MO_5889_DEFECT_VINTAGE = "TY2024"        # ⚠ 22 correction #2 -- a YEAR OLDER than first reported.
MO_5889_DEFECT_NOTE = (
    "⚠ 22 correction #2 REFUTED the brief's causal claim by pulling the TY2022, TY2023 and TY2024 "
    "Forms MO-PTE. TY2022-23 Part B ran `1 Name | 2 nonresident | 3 SSN/FEIN | 4 Membership % | "
    "5 PTE Tax Credit`, so Form 5889's Column 4 / Column 5 references were CORRECT then. TY2024 "
    "inserted `3 Select if member has made an opt-out election`, pushing SSN->4, Membership %->5, "
    "Credit->6. TY2025 changed NOTHING STRUCTURAL -- only the Column 6 LABEL (`Shareholder's` -> "
    "`Member's`). So the defect is A FULL YEAR OLDER than first thought, it was ALREADY WRONG FOR "
    "TY2024 FILINGS, and Form 5889 was revised 03-2025 -- AFTER the shift -- and still not fixed. "
    "IT IS A PERSISTED DEFECT THROUGH A FULL REVISION CYCLE, NOT A PUBLICATION LAG. (C2 / U6)"
)
MO_5889_IS_OPTIONAL = True
MO_5889_OPTIONAL_VERBATIM = (
    "'The Form MO-5889 CAN BE UTILIZED ... AS AN ALTERNATIVE TO A REPORT GENERATED BY THE COMPANY.' "
    "and, on MO-PTE Part B Column 6, 'Form 5889 MAY be used to report the amount of the PTE tax "
    "credit to each member.' MO-TC's own SPA row requires 'Fed. K-1, Form 5889 OR EQUIVALENT.'"
)
MO_5889_THREE_NAMES = (
    "⚠ THREE NAMES FOR ONE FORM: titled `Form 5889` on its face, `Form MO-5889` throughout its own "
    "instructions, and `Form 5889` on MO-TC."
)


def mo_5889_map() -> dict:
    """D-12 Group D: GENERATE A DELVIO MEMBER REPORT; map 5889 BY SUBSTANCE.

    ⚠ Never reproduce the stale column numbers in help text.
    """
    return {
        "preferred": "a Delvio-generated member report carrying the same two data points",
        "why_preferred": MO_5889_OPTIONAL_VERBATIM,
        "form_5889_map_by_substance": MO_5889_SUBSTANCE_MAP,
        "printed_but_stale": MO_5889_STALE_MAP,
        "defect_vintage": MO_5889_DEFECT_VINTAGE,
        "defect_note": MO_5889_DEFECT_NOTE,
        "reproduce_stale_numbers_in_help": False,
        "separate_form_rule": ("'A separate ... Form (Form MO-5889) should be completed for EACH TAX "
                               "YEAR AND EACH MEMBER. Do not combine information for multiple tax "
                               "years, entities, or taxpayers.'"),
    }


# ═══════════════════════════════════════════════════════════════════════════
# C4 / D-10 -- THE CAPITAL-GAIN ADVISORY. **ENCODE NOTHING.**
# ═══════════════════════════════════════════════════════════════════════════
MO_CAPGAIN_ADVISORY_TEXT = (
    "MISSOURI CAPITAL GAIN AND THE PASS-THROUGH ENTITY ELECTION -- FOR YOUR CONSIDERATION.\n\n"
    "For tax years beginning on or after January 1, 2025, Mo. Rev. Stat. 143.121.3(14)(a) allows a "
    "subtraction of 'one hundred percent of all income reported as a capital gain for federal income "
    "tax purposes BY AN INDIVIDUAL subject to tax pursuant to section 143.011.' Paragraph (b) extends "
    "the same relief to 'an entity subject to tax pursuant to section 143.071', but only 'for all tax "
    "years beginning on or after January first of the tax year following the tax year in which the "
    "top rate of tax imposed pursuant to section 143.011 is equal to or less than four and one-half "
    "percent.' Missouri's top individual rate for 2025 is 4.7 percent, so paragraph (b) is not yet "
    "operative.\n\n"
    "Form MO-PTE, Page 3, Part A carries a closed list of subtractions at Lines 6 through 11 and NO "
    "capital-gain line. The Department re-issued the form on March 31, 2026 -- after the 2025 session "
    "that enacted section 143.121.3(14) and after the amended SALT Parity regulation took effect -- "
    "and did not add one. Mo. Rev. Stat. 143.436.3(1) and .4(1) provide that the entity's base is "
    "'increased or decreased by any modification made pursuant to sections 143.121 and 143.141 that "
    "relates to an item of the affected business entity's income, gain, loss, or deduction.'\n\n"
    "Discuss with the client how the section 143.436 election interacts with the section "
    "143.121.3(14) subtraction before making it. This notice states the interaction and nothing "
    "more."
)
MO_CAPGAIN_ADVISORY_CITES = ("Mo. Rev. Stat. 143.121.3(14)", "Mo. Rev. Stat. 143.436")


def mo_capital_gain_advisory(has_material_capital_gain: bool,
                             has_missouri_individual_member: bool,
                             election_made: bool) -> dict:
    """⚠⚠ ADVICE LAYER ONLY. IT COMPUTES NOTHING AND RECOMMENDS NOTHING.

    Campaign D-12 C4, verbatim: 'Encode NOTHING: no optimiser, no
    recommendation, no automatic election. Ship a preparer-facing informational
    diagnostic that fires when an electing entity's Line 1 carries material
    capital gain and a Missouri individual member exists, states the
    interaction in the Department's own terms, cites 143.121.3(14) and 143.436,
    AND STOPS.'

    ⚠ NOTE THE SIGNATURE: it takes THREE BOOLEANS AND NO AMOUNTS. It cannot
    compute a comparison because it is never given the numbers to compare.
    D-10 already ruled the SPEC question -- BUILD TO THE FORM, no entity-level
    subtraction anywhere -- and this function does not re-open it.
    """
    return {
        "fires": bool(election_made and has_material_capital_gain
                      and has_missouri_individual_member),
        "severity": "info",
        "audience": "preparer",
        "text": MO_CAPGAIN_ADVISORY_TEXT,
        "citations": MO_CAPGAIN_ADVISORY_CITES,
        # The four things this function refuses to be.
        "computes_comparison": False,
        "recommends": False,
        "optimises": False,
        "auto_elects": False,
        "ruling": "campaign D-10 (build to the form) and campaign D-12 C4 (encode nothing)",
    }


# ═══════════════════════════════════════════════════════════════════════════
# 105.1500 RSMo -- THE 501(c) ROSTER COLLISION
# ═══════════════════════════════════════════════════════════════════════════
MO_105_1500_VERBATIM = (
    "Pursuant to Section 105.1500, RSMo, the Department of Revenue is prohibited from requiring any "
    "entity exempt from federal income tax under Section 501(c) of the Internal Revenue Code, or any "
    "individual, to provide the Department with any list, record, register, registry, roll, roster, "
    "or other compilation of data of any kind that directly or indirectly identifies a person as a "
    "member, supporter, volunteer of, or donor of financial or nonfinancial support to, any entity "
    "exempt from federal income tax under Section 501(c)... Nothing in this form should be read or "
    "understood as a requirement that you provide any such information. NOTWITHSTANDING ANY "
    "PUBLICATION, WEBPAGE, FORM, INSTRUCTION, REGULATION, OR STATEMENT SHARED BY THE DEPARTMENT, YOU "
    "ARE NOT REQUIRED TO INCLUDE SUCH INFORMATION ON THIS FORM."
)
MO_105_1500_PRINTED_ON = ("Form MO-PTE page 4", "Form MO-TC page 2")
MO_105_1500_COLLIDES_WITH = (
    "MO-PTE Part B Column 1: 'Name of each member. ALL MUST BE LISTED. Use an attachment if "
    "necessary.' -- and, secondarily, the Line 22 trust-fund donation grid."
)


def mo_501c_roster_decision(member_is_501c: bool) -> dict:
    """⚠ DO NOT SILENTLY SUPPRESS AND DO NOT SILENTLY INCLUDE. (W17 / R13)

    Never auto-populate a 501(c) member's identity without explicit
    confirmation. This is a PRINTABLE-CONTENT rule the engine must not override
    in either direction; it is not a computation.
    """
    if not member_is_501c:
        return {"decision_required": False, "auto_populate": True}
    return {
        "decision_required": True,
        "decision_owner": "PREPARER DECISION",
        "auto_populate": False,        # ⚠ never, without explicit confirmation
        "auto_suppress": False,        # ⚠ and never silently the other way either
        "statute": "Mo. Rev. Stat. 105.1500",
        "help_copy": MO_105_1500_VERBATIM,
        "collides_with": MO_105_1500_COLLIDES_WITH,
        "note": ("Surface it as a preparer decision with the statutory text as help copy. Ken sets "
                 "the default."),
    }


# ═══════════════════════════════════════════════════════════════════════════
# KANSAS CITY / ST. LOUIS -- OUT OF SCOPE, BUT PRINTED ON ALL THREE FACES
# ═══════════════════════════════════════════════════════════════════════════
MO_CITY_EARNINGS_TAXES_IN_SCOPE = False
MO_CITY_EARNINGS_TAX_LINE = "1b"        # ⭐ ON ALL THREE FORM FACES
MO_CITY_EARNINGS_TAX_NOTE = (
    "⭐ THE SCOPE BOUNDARY IS PRINTED ON THE FORM, AT LINE 1b ON ALL THREE FACES: the Kansas City "
    "and St. Louis earnings taxes are CARVED OUT OF the state-and-local income tax add-back. Kansas "
    "City (Forms RD-108 / RD-109) and the City of St. Louis (Forms E-1 / E-234) levy 1 percent "
    "earnings taxes administered BY THE CITIES, not by the Missouri Department of Revenue -- separate "
    "filings through separate portals, not prepared by this product. ⚠ ALL KANSAS CITY TAXES MUST BE "
    "FILED ELECTRONICALLY AS OF JANUARY 1, 2025. THE STATE MODULE MUST KNOW THEY EXIST for Line 1b "
    "even though it does not compute them. INFO diagnostic, never RED. (R15)"
)
# ⚠ The three faces word the Line 1b label slightly DIFFERENTLY; transcribe each
# face's own wording -- see the per-form LINES blocks below.


# ═══════════════════════════════════════════════════════════════════════════
# DOR DEFECT LEDGER -- the FACE governs; the conflict is LOGGED
# ═══════════════════════════════════════════════════════════════════════════
MO_DOR_DEFECTS: list[dict] = [
    {"id": 1, "where": "MO-MS PTE / MO-MSS / MO-MS faces",
     "printed": "Two A - Receipts Factor Apportionment - Section 143.455.2",
     "actual": "143.455.2 is the APPLICABILITY subsection; the receipts factor is .10, sourcing .11/.12",
     "spec_impact": "none - cite .10/.11/.12 in the rule"},
    {"id": 2, "where": "MO-1120S / MO-MSS apportionment-election list",
     "printed": "Method Seven under Section 143.455.13(2)",
     "actual": ".13(1) is the industry-regulation (broadcaster) route; .13(2) is the "
               "alternative-apportionment petition. Their own Method Seven INSTRUCTIONS say .13(1).",
     "spec_impact": "none - cite both correctly"},
    {"id": 3, "where": "MO-PTE instructions, Methods 3-6",
     "printed": "enter ... on Form MO-MS PTE, Part 1, Line 3 and Form MO-PTE, LINE 4",
     "actual": "MO-PTE Line 4 is a DOLLAR Balance; the percentage goes to Line 5 Percent per the "
               "MO-MS PTE face",
     "spec_impact": "BUILD TO THE FACE"},
    {"id": 4, "where": "MO-PTE instructions vs MO-MSS instructions",
     "printed": "'If the mileage percentage ... is APPLICABLE' vs '... is INAPPLICABLE'",
     "actual": "one of the two is inverted and no source resolves which",
     "spec_impact": "⚠ REAL - U11. DO NOT GUESS IN CODE."},
    {"id": 5, "where": "MO-PTENR / MO-PTE Opt-Out Part 2",
     "printed": "'File an income tax return in accordance with the provisions of Section 143.481'",
     "actual": "143.436.5(3)(a) says 'in accordance with the provisions of section 143.181'. "
               "143.481 is 'Returns, who must file'; 143.181 is 'Missouri source income of a "
               "nonresident'. The FORMS' 143.481 is the sensible reading; the STATUTE's 143.181 "
               "looks like a drafting slip.",
     "spec_impact": "none"},
    {"id": 6, "where": "MO-1065 Line 9 vs MO-NRP Part 2 Line 9",
     "printed": "'Missouri depreciation BASIS adjustment (Section 143.121.3(7), RSMo)' vs "
                "'Missouri depreciation adjustment (See Section 143.121, RSMo.)'",
     "actual": "same line, two labels, two citation depths",
     "spec_impact": "none - transcribe each face"},
    {"id": 7, "where": "MO-1120S Line 7",
     "printed": "face '...included in federal ORDINARY income' vs heading '...INCLUDED IN FEDERAL "
                "TAXABLE INCOME'",
     "actual": "same line", "spec_impact": "none - the FACE governs"},
    {"id": 8, "where": "MO-TC header",
     "printed": "'Attach to Form MO-1040, MO-1120, or MO-1041' -- MO-PTE OMITTED",
     "actual": "Lines 12 and 13 both reference MO-PTE and the Column instruction names "
               "'pass-through entity income tax'",
     "spec_impact": "cosmetic"},
    {"id": 9, "where": "Form 5889 line instructions",
     "printed": "Part B, Column 4 / Column 5",
     "actual": "TY2025 MO-PTE Part B: Column 5 (Membership %) / Column 6 (Member's PTE Tax Credit)",
     "spec_impact": "⚠ REAL - U6. Map by SUBSTANCE."},
    {"id": 10, "where": "Form 5889 naming",
     "printed": "`Form 5889` on the face, `Form MO-5889` in its own instructions, `Form 5889` on MO-TC",
     "actual": "three names, one form", "spec_impact": "cosmetic"},
    {"id": 11, "where": "MO-PTE instructions, representative designation",
     "printed": "Form 2827 only",
     "actual": "12 CSR 10-2.436(5)(A) names Form 2827 OR Form 2827 PTE",
     "spec_impact": "⚠ REAL - support BOTH"},
    {"id": 12, "where": "MO-7004 vs MO-PTE instructions",
     "printed": "'extends the due date up to 180 days' vs 'not to exceed six months'",
     "actual": "different lengths", "spec_impact": "⚠ REAL - U24. Six-month cap."},
    {"id": 13, "where": "MO-7004 vs MO-60",
     "printed": "MO-7004: S corps 'use Form MO-60'; MO-60: no S-corp checkbox, S corps ride the "
                "federal 7004",
     "actual": "a three-way contradiction with MO-1120S, which names no Missouri form",
     "spec_impact": "⚠ REAL - U24"},
    {"id": 14, "where": "MO-1065 vs MO-1120S vs 143.411.5",
     "printed": "'current OR prior' / 'BOTH the current and prior' / 'the current AND prior'",
     "actual": "three renderings of one condition",
     "spec_impact": "⚠ REAL - U22. Build the narrow conjunctive form reading (RULED)."},
    {"id": 15, "where": "MO-MS PTE / MO-MS",
     "printed": "both print `Attachment Sequence No. 1120-01`",
     "actual": "an assembly-order slot COLLISION between two different forms",
     "spec_impact": "⚠ REAL - U13"},
    {"id": 16, "where": "Form MO-PTE Opt-Out",
     "printed": "barcode *25329010001* over human-readable 25125010001",
     "actual": "*25329010001* is FORM MO-3NR's code",
     "spec_impact": "⚠ REAL - U27. PRINT NO SCANLINE AT ALL IN v1."},
    {"id": 17, "where": "Form MO-PTE face",
     "printed": "revision stamp still `Revised 12-2025`",
     "actual": "the file was re-stamped 2026-03-31; no revision history is published",
     "spec_impact": "⚠ REAL - U12. A vendor keying off the printed code will miss the re-issue."},
    {"id": 18, "where": "Form MO-NRP (a FINAL form)",
     "printed": "'Note: At the time the Department finalized their tax booklets, the Internal "
                "Revenue Service had not finalized the federal income tax forms.'",
     "actual": "the DOR DISCLAIMING federal-line alignment on a FINAL TY2025 form",
     "spec_impact": "⚠ REAL - U8. EVERY federal line reference in this lane is [UNVERIFIED]."},
    {"id": 19, "where": "DOR FAQs - Pass-Through Entity Tax, 'What is the tax rate...'",
     "printed": "5.3% (2022), 4.95% (2023), 4.8% (2024) -- AND THEN STOPS. NO TY2025 ENTRY.",
     "actual": "the TY2025 rate is 4.7%, printed on the MO-PTE FORM FACE at Line 10",
     "spec_impact": "⚠ REAL - NEVER TAKE THE RATE FROM THE FAQ. A preparer consulting it gets no "
                    "2025 figure and may carry 4.8% forward."},
    {"id": 20, "where": "MO-MS PTE face note",
     "printed": "'Complete mileage information below for Method Three - Six'",
     "actual": "Three (143.455.14) is GROSS EARNINGS and Five (143.455.16) is a FLAT ONE-HALF. Only "
               "Four and Six are mileage-driven.",
     "spec_impact": "⚠ C11 - restate before propagating"},
    {"id": 22, "where": "MO-PTE Part B Column 5 instruction (opt-out re-gross-up example)",
     "printed": "'that non-opt-out member's new credit percentage is 14% (10% divided by 70%)'",
     "actual": ("10 / 70 = 14.285714...%, which is 14.29% at the TWO DECIMAL PLACES the SAME COLUMN "
                "mandates one sentence earlier ('Round the percentage to the nearest two decimal "
                "places'). The Department's illustration is rounded to a WHOLE NUMBER, contradicting "
                "the rounding rule printed for the very column it illustrates."),
     "spec_impact": ("⚠ REAL, AND NOT IN THE SOURCE BRIEF -- surfaced by the validation harness. "
                     "Column 5 must foot to 100.00% across participating members after the "
                     "re-gross-up, and a whole-number allocation does not reliably close. This build "
                     "computes at TWO DECIMALS and reproduces the Department's whole-number figure "
                     "alongside it. See MO_OPTOUT_EXAMPLE_ROUNDING_DEFECT.")},
    {"id": 21, "where": "Form 5889 (Revised 03-2025)",
     "printed": "column references stale SINCE TY2024, not TY2025",
     "actual": "the opt-out Column 3 was inserted on the TY2024 MO-PTE; 5889 was revised 03-2025, "
               "i.e. AFTER that shift, and still carries the pre-TY2024 numbering",
     "spec_impact": "⚠ REAL - a PERSISTED defect through a full revision cycle, not a lag"},
]

# U8 -- the stamp every federal line reference in this spec carries.
MO_FEDERAL_LINE_STAMP = (
    "⚠ [UNVERIFIED - U8] Transcribed from the Missouri DOR's own TY2025 instructions and NOT "
    "cross-checked against the FINAL TY2025 IRS forms. The DOR ITSELF DISCLAIMS THE ALIGNMENT, "
    "printing on the FINAL Form MO-NRP: 'At the time the Department finalized their tax booklets, "
    "the Internal Revenue Service had not finalized the federal income tax forms.' Re-pull the FINAL "
    "IRS Forms 1065, 1120-S, Schedules K-1, 4797 and 1125-A before the app build."
)

MO_OPEN_ITEMS_GENUINELY_OPEN = 22        # 28 raised, 4 closed and 2 strengthened by the 22 pass
MO_OPEN_ITEMS_CLOSED = ("U1", "U2", "U5", "U6")
MO_OPEN_ITEMS_STRENGTHENED = ("U3", "U18", "U19")
MO_OPEN_ITEMS_NARROWED = ("U4",)
MO_WALK_ITEMS_LIVE = 15                  # 17 raised, W2 closed, W4 downgraded


# ═══════════════════════════════════════════════════════════════════════════
# THE MODIFICATION CHAINS -- THREE FACES THAT LOOK INTERCHANGEABLE AND ARE NOT
#
# ⚠ READ MO_FACE_ASYMMETRY BEFORE WRITING A SINGLE SHARED RULE. Six load-bearing
# asymmetries fall out of it and every one is a spec hazard.
# ═══════════════════════════════════════════════════════════════════════════
MO_FACE_ASYMMETRY: list[dict] = [
    {"item": "State and local income taxes deducted federally, LESS KC/St. Louis earnings taxes",
     "MO_1065": "Line 1 (1a - 1b)", "MO_1120S": "Line 1 (1a - 1b)", "MO_PTE": "Line 1 (1a - 1b)"},
    {"item": "State and local bond interest except Missouri, less related expenses >= $500",
     "MO_1065": "Line 2 (2a - 2b)", "MO_1120S": "Line 2 (2a - 2b)", "MO_PTE": "Line 2 (2a - 2b)"},
    {"item": "Partnership / Fiduciary / Other ADDITION",
     "MO_1065": "Line 3", "MO_1120S": "Line 3", "MO_PTE": "Line 3"},
    {"item": "IRC 163(j) business interest expense CARRYFORWARD (addition), 143.121.2(6)",
     "MO_1065": "⚠ ABSENT - no line, no instruction (N7)",
     "MO_1120S": "folded into Line 3 BY INSTRUCTION", "MO_PTE": "⭐ ITS OWN LINE 4"},
    {"item": "Food Pantry Tax Credit donations add-back (135.647)",
     "MO_1065": "Line 4", "MO_1120S": "Line 4", "MO_PTE": "⚠ ABSENT (N6)"},
    {"item": "TOTAL ADDITIONS", "MO_1065": "Line 5", "MO_1120S": "Line 5", "MO_PTE": "Line 5"},
    {"item": "Interest from exempt federal obligations, less related expenses >= $500",
     "MO_1065": "Line 6 (6a - 6b)", "MO_1120S": "Line 6 (6a - 6b)", "MO_PTE": "Line 6 (6a - 6b)"},
    {"item": "State income tax refund included in income",
     "MO_1065": "Line 7", "MO_1120S": "Line 7", "MO_PTE": "Line 7"},
    {"item": "Federally taxable - Missouri exempt obligations (MOHELA, 173.440)",
     "MO_1065": "⚠ ABSENT (N8)", "MO_1120S": "Line 8", "MO_PTE": "Line 8"},
    {"item": "Partnership / Fiduciary / Other SUBTRACTION",
     "MO_1065": "Line 8", "MO_1120S": "Line 9", "MO_PTE": "Line 9"},
    {"item": "Missouri depreciation basis adjustment (143.121.3(7))",
     "MO_1065": "Line 9", "MO_1120S": "Line 10", "MO_PTE": "⚠ ABSENT (N5)"},
    {"item": "Depreciation recovery on qualified property sold (143.121.3(9))",
     "MO_1065": "⚠ ABSENT (N9)", "MO_1120S": "Line 11", "MO_PTE": "⚠ ABSENT (N5)"},
    {"item": "IRC 163(j) DISALLOWED business interest expense (subtraction), 143.121.3(11)",
     "MO_1065": "⚠ ABSENT (N7)", "MO_1120S": "folded into Line 9 BY INSTRUCTION",
     "MO_PTE": "⭐ ITS OWN LINE 11"},
    {"item": "Agricultur*e*/Agricultur*al* Disaster Relief (143.121.3(10)) ⚠ TWO SPELLINGS",
     "MO_1065": "Line 13 - ⚠ OUTSIDE the totals, `Agriculture Disaster Relief`",
     "MO_1120S": "Line 15 - ⚠ OUTSIDE the totals, `Agriculture Disaster Relief`, NO statutory cite "
                 "on the face",
     "MO_PTE": "⭐ Line 10 - INSIDE the subtraction total, `Agricultural Disaster Relief`"},
    {"item": "100% capital gain subtraction (143.121.3(14))",
     "MO_1065": "ABSENT", "MO_1120S": "ABSENT", "MO_PTE": "ABSENT (N4; D-10 -- do not add one)"},
    {"item": "TOTAL SUBTRACTIONS",
     "MO_1065": "Line 10 (6 through 9)", "MO_1120S": "Line 12 (6 through 11)",
     "MO_PTE": "Line 12 (6 through 11)"},
    {"item": "Net addition / net subtraction",
     "MO_1065": "Lines 11 / 12", "MO_1120S": "Lines 13 / 14",
     "MO_PTE": "n/a - carried to Page 1 Lines 2 and 3"},
]


def mo_related_expense_net(gross: float, related_expense: float) -> dict:
    """The a/b netting pairs (2a/2b and 6a/6b) with the $500 EXPENSE FLOOR.

    ⚠⚠ A FLOOR ON THE EXPENSE, NOT A THRESHOLD ON THE SUBTRACTION. Verbatim:
    'The expenses must equal or exceed $500. If less than $500, enter zero.'
    So below $500 the EXPENSE IS DROPPED and the GROSS amount survives, which
    makes the modification LARGER, not smaller. Getting this backwards is one
    of the seven most likely Missouri build errors.

    The DOR's own fallback ratio when the expense is not separately known:
      Exempt income / Total income x Expense items = Reduction to exempt income
      'The principal expense item in this formula is interest expense.'
    """
    expense = float(related_expense or 0.0)
    applied = expense if expense >= MO_RELATED_EXPENSE_FLOOR else 0.0
    return {
        "gross": gross,
        "expense_entered": expense,
        "expense_applied": applied,
        "expense_dropped_by_floor": expense > 0 and applied == 0.0,
        "net": float(gross) - applied,
        "floor": MO_RELATED_EXPENSE_FLOOR,
        "rule": "the expenses must EQUAL OR EXCEED $500; if less than $500, enter zero",
        "dor_fallback_ratio": ("Exempt income / Total income x Expense items = Reduction to exempt "
                               "income. 'The principal expense item in this formula is interest "
                               "expense.'"),
    }


def mo_1065_adjustment(l1: float, l2: float, l3: float, l4: float,
                       l6: float, l7: float, l8: float, l9: float) -> dict:
    """MO-1065 Lines 5, 10, 11 and 12. ⚠ Line 13 is NOT part of this chain."""
    l5 = l1 + l2 + l3 + l4
    l10 = l6 + l7 + l8 + l9
    return {
        "L5": l5, "L10": l10,
        "L11": max(0.0, l5 - l10),      # net ADDITION
        "L12": max(0.0, l10 - l5),      # net SUBTRACTION
        "note": ("⚠ MO-1065 Line 13 (Agriculture Disaster Relief) sits BELOW the net lines and is "
                 "NOT in Line 10. It is separately allocated to partners with its own schedule and "
                 "lands on MO-A Part 1 LINE 16 -- a DIFFERENT owner-side line from the Line 11/12 "
                 "landing at MO-A Part 1 Line 2 / Line 11."),
    }


def mo_1120s_adjustment(l1: float, l2: float, l3: float, l4: float,
                        l6: float, l7: float, l8: float, l9: float,
                        l10: float, l11: float) -> dict:
    """MO-1120S Lines 5, 12, 13 and 14. ⚠ Line 15 is NOT part of this chain."""
    l5 = l1 + l2 + l3 + l4
    l12 = l6 + l7 + l8 + l9 + l10 + l11
    return {
        "L5": l5, "L12": l12,
        # 'enter the difference on Line 13 AS A POSITIVE NUMBER' / 'Enter AS A
        # POSITIVE NUMBER on Line 14'
        "L13": max(0.0, l5 - l12),
        "L14": max(0.0, l12 - l5),
        "note": ("⚠ MO-1120S Line 15 (Agriculture Disaster Relief) sits OUTSIDE the Line 12 total, "
                 "same as MO-1065 Line 13 -- and UNLIKE MO-PTE Line 10, which is INSIDE the total."),
    }


def mo_pte_page1(l1_sum_702a_1366: float, l2_additions: float, l3_subtractions: float,
                 l5_preliminary: float, l6_bid: float, l7_lower_tier: float,
                 l8_prior_loss: float, l11_credits: float,
                 year: int = FORM_TAX_YEAR) -> dict:
    """Form MO-PTE Page 1, the tax computation -- Lines 4, 9, 10 and 12.

      L4  = L1 + L2 - L3
      L5  = all-Missouri ? L4 : L4 x round(MO-MS PTE percentage, 3)
      L9  = L5 - L6 - L7 - L8      (L8 FLOORED so L9 >= 0 before the loss)
      L10 = max(0, L9 x 4.7%)
      L12 = max(0, L10 - L11)      <- the number that becomes the members' pool

    ⭐ Line 7 is SUBTRACTED, so a POSITIVE Line 7 REMOVES lower-tier income and a
    NEGATIVE Line 7 ADDS BACK lower-tier loss -- exactly 143.436.5(1). The
    instruction is explicit: 'If this sum is negative, enter a negative figure
    on Line 7.'

    ⭐ THE LINE 8 FLOOR, verbatim: 'Do not use an amount of Missouri net loss
    from a prior tax year to reduce the Missouri net income below $0 for this
    tax year. If the amount to be reported on Line 9 would be $0 or below zero
    without utilizing any Missouri net loss carryforward from a prior tax year,
    ENTER $0 ON LINE 8.' And: 'This is not applicable for the affected business
    entity's FIRST YEAR filing Form MO-PTE. If it is the first year filing Form
    MO-PTE, enter $0.'
    """
    l4 = l1_sum_702a_1366 + l2_additions - l3_subtractions
    pre_loss = l5_preliminary - l6_bid - l7_lower_tier
    l8_allowed = 0.0 if pre_loss <= 0 else min(float(l8_prior_loss), pre_loss)
    l9 = pre_loss - l8_allowed
    l10 = max(0.0, l9 * mo_pte_rate(year))
    l12 = max(0.0, l10 - float(l11_credits))
    return {
        "L4": l4, "L5": l5_preliminary, "L6": l6_bid, "L7": l7_lower_tier,
        "L8_requested": l8_prior_loss, "L8": l8_allowed,
        "L8_floored": l8_allowed != float(l8_prior_loss),
        "L9": l9, "L10": l10, "L11": l11_credits, "L12": l12,
        "rate": mo_pte_rate(year),
        "credit_pool_warning": ("⚠ Line 12 is the members' credit pool ONLY TO THE EXTENT PAID. If "
                                "Line 11 is greater than zero, the members' credit is REDUCED -- see "
                                "mo_tax_actually_paid(). (campaign D-12 C5)")
        if float(l11_credits) > 0 else None,
    }


def mo_pte_page2(l12_liability: float, l13_excess_refundable: float, l14_anticipated: float,
                 l15_mo7004: float, l16_amended_paid: float, l18_amended_overpayment: float,
                 l21_applied_forward: float = 0.0, l22_donations: float = 0.0) -> dict:
    """Form MO-PTE Page 2 -- Lines 17, 19, 20, 23 and 24.

      L17 = L13 + L14 + L15 + L16
      L19 = L17 - L18
      L20 = max(0, L19 - L12)
      L23 = L20 - L21 - L22           ⚠ with the $1.00 refund floor
      L24 = max(0, L12 - L19)
    """
    l17 = l13_excess_refundable + l14_anticipated + l15_mo7004 + l16_amended_paid
    l19 = l17 - l18_amended_overpayment
    l20 = max(0.0, l19 - float(l12_liability))
    l23_raw = l20 - l21_applied_forward - l22_donations
    l23 = 0.0 if l23_raw < MO_REFUND_FLOOR else l23_raw
    return {
        "L17": l17, "L19": l19, "L20": l20,
        "L23": l23, "L23_before_floor": l23_raw,
        "refund_floored": l23_raw != l23,
        "L24": max(0.0, float(l12_liability) - l19),
        "form_5378_required": l23 >= MO_ELECTRONIC_REFUND_THRESHOLD,
        "note": ("'No refund of less than $1.00 will be made.' 'The Department generally requires "
                 "approved refunds of $100,000 or more to be issued electronically. If claiming a "
                 "refund of $100,000 or more, complete FORM 5378 and submit with your return.' "
                 "⚠ Line 13 is the ONE place where refundable credits in excess of liability "
                 "re-enter as a PAYMENT rather than as a credit."),
    }


# ═══════════════════════════════════════════════════════════════════════════
# MO-NRP AND MO-NRS -- STRUCTURALLY OPPOSITE COLUMN DERIVATIONS
# ⚠⚠ DO NOT SHARE A RULE BETWEEN THEM.
# ═══════════════════════════════════════════════════════════════════════════
def mo_nrp_columns(col_a_everywhere: float, col_b_missouri: float,
                   col_d_partner_k1: float) -> dict:
    """MO-NRP: `(c) = (b) / (a)` and `(e) = (d) x (c)`.

    DOR's own worked example, verbatim: 'Assume $20,000 income from a business
    deriving $16,000 (80%) from Missouri and a single 60% nonresident partner.
    Columns will appear: (a) $20,000, (b) $16,000, (c) 80%, (d) $12,000, and
    (e) $9,600.'
    """
    pct = None if not col_a_everywhere else 100.0 * col_b_missouri / col_a_everywhere
    return {"col_a": col_a_everywhere, "col_b": col_b_missouri, "col_c_pct": pct,
            "col_d": col_d_partner_k1,
            "col_e": None if pct is None else col_d_partner_k1 * pct / 100.0,
            "derivation": "(c) = (b) / (a);  (e) = (d) x (c)",
            "escape": "'Attach a detailed explanation if any other method is used.'"}


def mo_nrs_columns(col_a_everywhere: float, col_c_pct_from_mo_mss: float,
                   col_d_shareholder_k1: float) -> dict:
    """MO-NRS: `(b) = (a) x (c)` and `(e) = (d) x (c)` -- THE REVERSE OF MO-NRP.

    Verbatim: 'Column (b): MULTIPLY THE AMOUNT IN COLUMN (a) BY THE PERCENT IN
    COLUMN (c) and enter in Column (b).' / 'Column (c): Enter the percent from
    FORM MO-MSS, LINE 3.'
    ⚠⚠ Two identical-looking five-column grids, two INVERSE arithmetics. And
    Column (c) is a VECTOR indexed by distributive-share line, not a scalar --
    see mo_mss_per_item_percentage().
    """
    return {"col_a": col_a_everywhere, "col_c_pct": col_c_pct_from_mo_mss,
            "col_b": col_a_everywhere * col_c_pct_from_mo_mss / 100.0,
            "col_d": col_d_shareholder_k1,
            "col_e": col_d_shareholder_k1 * col_c_pct_from_mo_mss / 100.0,
            "derivation": "(b) = (a) x (c);  (e) = (d) x (c)  -- THE REVERSE OF MO-NRP",
            "downstream_caution": ("Printed on the form: 'The items from Form MO-NRS, Part 1, Column "
                                   "(e), that are to be income or losses should be entered on the "
                                   "Form MO-NRI, as Missouri source income. THESE AMOUNTS MUST BE "
                                   "ADJUSTED BY ANY CAPITAL GAIN OR PASSIVE LOSS LIMITATION AS "
                                   "REQUIRED.' -- the individual module inherits an unstated "
                                   "IRC 1211 / 469 limitation step.")}


def mo_mss_per_item_percentage(item_total: float, nonapportionable_everywhere: float,
                               nonapportionable_missouri: float,
                               receipts_factor_pct: float) -> dict:
    """MO-MSS's printed SIX-STEP algorithm -- a PER-ITEM percentage, not one factor.

    DOR's own worked example, verbatim, a ready-made unit-test vector:
      Assume $15,000 net rental real estate income of which $3,000 is
      nonapportionable, of which $1,000 is directly allocated to Missouri.
      Apportionment factor 33.333%.
        Step 1  $15,000
        Step 2  - 3,000  -> $12,000 apportionable
        Step 3  $12,000 x 33.333% = $4,000
        Step 4  $1,000 nonapportionable allocated to Missouri
        Step 5  + $4,000 -> $5,000 -> MO-NRS Part 1 Line 2 Column (b)
        Step 6  $5,000 / $15,000 = 33.333% -> MO-NRS Part 1 Line 2 Column (c)

    ⭐ Verbatim: 'If a distributive share item is wholly or partially allocated
    as nonapportionable income, A DIFFERENT PERCENTAGE WILL BE COMPUTED FOR THE
    ITEM.' ⚠ ANY MODEL THAT STORES ONE APPORTIONMENT PERCENTAGE PER RETURN IS
    WRONG.
    """
    apportionable = item_total - nonapportionable_everywhere
    apportioned = apportionable * receipts_factor_pct / 100.0
    col_b = apportioned + nonapportionable_missouri
    col_c = None if not item_total else 100.0 * col_b / item_total
    return {"col_b": col_b, "col_c_pct": col_c, "apportionable": apportionable,
            "apportioned": apportioned,
            "note": "A PER-DISTRIBUTIVE-SHARE-ITEM percentage. MO-NRS Column (c) is a VECTOR."}


MO_MSS_PRESUMPTION = (
    "'Directly allocable nonapportionable income. Do not allocate expenses that have been excluded "
    "from federal taxable income. ALL INCOME IS PRESUMED TO BE APPORTIONABLE INCOME UNLESS YOU CAN "
    "CLEARLY SHOW THE INCOME TO BE NONAPPORTIONABLE INCOME.'"
)

MO_RECEIPTS_SOURCING_RULES = (
    ("denominator_exclusion",
     "'receipts from hedging transactions or from the maturity, redemption, sale, exchange, loan, or "
     "other disposition of cash or securities (e.g. stocks, stock options, bonds) MUST NOT BE "
     "INCLUDED IN EITHER THE NUMERATOR OR DENOMINATOR of the receipts factor.'"),
    ("tangible_personal_property",
     "'in this state if the property is RECEIVED IN MISSOURI BY THE PURCHASER.' Rental / lease / "
     "license of TPP: to the extent the property is LOCATED in Missouri."),
    ("real_property", "to the extent located in Missouri"),
    ("services_tier_1",
     "'if and to the extent that the ULTIMATE BENEFICIARY is in Missouri... the entity that receives "
     "benefit or value from, but does not also receive monetary or credit-based payment in direct "
     "connection with, the service at issue (other than refunds, cashback, or discount-equivalents)'"),
    ("services_tier_2",
     "multi-state beneficiary -> 'The ratio of the number of Missouri locations, which the ultimate "
     "beneficiary owns or operates in, to the number of such locations throughout the United States.'"),
    ("services_tier_3",
     "'If the ratio above cannot reasonably be determined, then the ratio of ONE TO THE NUMBER OF "
     "STATES in which the ultimate beneficiary operates.'"),
    ("services_tier_4",
     "⭐ 'If the ratio above cannot reasonably be determined, then FIFTY PERCENT (50%). A taxpayer "
     "will not be subject to an addition to tax for negligence in relying upon this approximation of "
     "fifty percent (50%).' -- A FOUR-TIER STATUTORY SAFE HARBOUR ENDING IN A LITERAL 50% DEFAULT "
     "WITH NEGLIGENCE PROTECTION. The 50% tier is a RULE, not a guess. Encode all four tiers as an "
     "ORDERED FALLBACK CHAIN."),
    ("intangibles_licensed",
     "to the extent used in Missouri; marketing intangibles follow the consumer; franchise fees "
     "follow franchise location"),
    ("intangibles_sold",
     "to the extent used in Missouri; geographic-area rights are used in Missouri if the area "
     "includes any part of Missouri; productivity-contingent receipts are RE-CHARACTERISED as "
     "rental/license receipts; 'All other receipt from a sale of intangible property shall be "
     "EXCLUDED FROM BOTH THE NUMERATOR AND THE DENOMINATOR.'"),
    ("fallback",
     "'If the state or states to which to assign receipts cannot be determined, the state or states "
     "of assignment must be REASONABLY APPROXIMATED and you must attach a detailed statement "
     "explaining the basis of the reasonable approximation.'"),
)

MO_NONAPPORTIONABLE_ALLOCATION_RULES = (
    ("a", "Net rents/royalties from REAL PROPERTY LOCATED IN THIS STATE", "143.455.6(1)", False),
    ("b", "Net rents/royalties from TPP: (1) to the extent utilized in this state; OR (2) IN THEIR "
          "ENTIRETY if commercial domicile is in this state and the taxpayer is not organized under "
          "the laws of, or taxable in, the state in which the property is utilized. Day-count "
          "utilization fraction; unknown location -> the state where the payor obtained possession",
     "143.455.6(2)-(3)", False),
    ("c", "Capital gains/losses from sales of REAL PROPERTY located in this state", "143.455.7(1)",
     False),
    ("d", "Capital gains/losses from sales of TPP: (1) situs in this state at the time of sale; OR "
          "(2) commercial domicile in this state AND the taxpayer is NOT TAXABLE IN THE SITUS STATE",
     "143.455.7(2)", True),      # ⚠ THROWBACK-STYLE
    ("e", "Capital gains/losses from sales of INTANGIBLE personal property if commercial domicile is "
          "in this state", "143.455.7(3)", False),
    ("f", "INTEREST AND DIVIDENDS if commercial domicile is in this state", "143.455.8", False),
    ("g", "PATENT AND COPYRIGHT ROYALTIES: (1) to the extent utilized by the payor in this state; OR "
          "(2) to the extent utilized in a state in which the taxpayer is NOT TAXABLE and commercial "
          "domicile is in this state. Patent = employed in production/fabrication/manufacturing/"
          "processing, or patented product produced in the state; copyright = printing or other "
          "publication originates in the state; if unallocable, utilized at commercial domicile",
     "143.455.9", True),         # ⚠ THROWBACK-STYLE
)
MO_THROWBACK_STYLE_RULES = tuple(r[0] for r in MO_NONAPPORTIONABLE_ALLOCATION_RULES if r[3])
MO_THROWBACK_NOTE = (
    "⭐ CONFIRMED VERBATIM ON THE STATUTE AND ON ALL THREE APPORTIONMENT FORMS: the RECEIPTS FACTOR "
    "has NO throwback, but allocation rules (d)(2) and (g)(2) ARE THROWBACK-STYLE tests keyed to "
    "commercial domicile PLUS non-taxability elsewhere. They must be encoded. 'Commercial domicile' "
    "= 'the principal place from which the trade or business of the taxpayer is directed or managed' "
    "(143.455.3(2), printed on the forms)."
)
MO_TAXABLE_IN_ANOTHER_STATE = (
    "The two-test rule, printed on every apportionment form: (a) subject in that state to 'a net "
    "income tax, a franchise tax measured by net income, a franchise tax for the privilege of doing "
    "business, or a corporate stock tax'; OR (b) that state 'has jurisdiction to subject the taxpayer "
    "to a net income tax, regardless of whether or not that state imposes such a tax.' ANTI-ABUSE "
    "CARVE-OUT: voluntary filing, or a minimal qualification fee, without actual business activity or "
    "with activity insufficient for nexus, does NOT make a taxpayer taxable there. 'Jurisdiction to "
    "tax is not present where the state is prohibited from imposing the tax by reason of the "
    "provisions of Public Law 86-272, 15 U.S.C.A. Sections 381-385.'"
)


# ═══════════════════════════════════════════════════════════════════════════
# THE REPRESENTATIVE GATE -- A HARD PRECONDITION OF A VALID ELECTION
# ═══════════════════════════════════════════════════════════════════════════
MO_ABE_REP_REQUIRED = True
MO_ABE_REP_VERBATIM = (
    "'IF A PARTNERSHIP OR S CORPORATION DOES NOT DESIGNATE A PERSON AS AN AFFECTED BUSINESS ENTITY "
    "REPRESENTATIVE FOR THE TAX YEAR FOR WHICH THIS RETURN IS FILED, THE ELECTION TO BECOME AN "
    "AFFECTED BUSINESS ENTITY WILL BE INEFFECTIVE.' 12 CSR 10-2.436(2): 'An election ... shall not "
    "be effective if the partnership or S corporation has not successfully designated a person as an "
    "affected business entity representative for that tax year AT OR BEFORE THE TIME the partnership "
    "or S corporation attempts to make such election.'"
)
MO_ABE_REP_FORMS = ("Form 2827", "Form 2827 PTE")   # ⚠ the instructions name only 2827; the reg names both
MO_ABE_REP_CONSTRAINTS = (
    "ONLY ONE NATURAL PERSON (i.e. not a business entity) may serve for a particular tax year.",
    "That person must have a WORKING E-MAIL ADDRESS, TELEPHONE NUMBER AND PHYSICAL ADDRESS at which "
    "to receive mail (12 CSR 10-2.436(5)(B)).",
    "The representative has SOLE AUTHORITY to act for the entity for the tax year, and 143.436.13(1) "
    "provides that 'the affected business entity's members shall be bound by those actions'.",
    "Removal only by designating a new representative on a subsequently filed Form 2827; 12 CSR "
    "10-2.436(6): 'The removal ... does not change the binding effect of any prior actions taken by "
    "that affected business entity representative.'",
    "RE-DESIGNATION BOX: 'Do not select this box unless a person signing the return has been given "
    "authority, by the pass-through entity, to designate an affected business entity representative "
    "for the pass-through entity for this tax year.' 12 CSR 10-2.436(5)(D) adds that the prior-year "
    "representative may check it to re-designate HIMSELF OR HERSELF only with that authority.",
    "ALL-MEMBERS-SIGN ALTERNATIVE: attach a schedule with the 'signature, printed name, phone number, "
    "ownership percentage, and signature date for EACH AND EVERY partner, shareholder, and member' "
    "as of the filing date.",
)


def mo_election_valid(election_box_checked: bool, representative_designated: bool,
                      filed_by_deadline_including_extension: bool) -> dict:
    """The 143.436 election has THREE preconditions and one of them is easy to miss."""
    return {
        "valid": bool(election_box_checked and representative_designated
                      and filed_by_deadline_including_extension),
        "election_box_checked": election_box_checked,
        "representative_designated": representative_designated,
        "timely": filed_by_deadline_including_extension,
        "blocking_failure": (None if representative_designated else
                             "NO AFFECTED BUSINESS ENTITY REPRESENTATIVE -- THE ELECTION IS "
                             "INEFFECTIVE (12 CSR 10-2.436(2))"),
        "annual": "'A SEPARATE ELECTION MUST BE MADE FOR EACH TAX YEAR.'",
        "irrevocable": ("'If an election to become an affected business entity has been made for a "
                        "tax year, THE ELECTION CANNOT BE REVOKED FOR THAT TAX YEAR.'"),
        "deadline": ("12 CSR 10-2.436(3): 'The deadline for making an election ... is the filing "
                     "deadline for the affected business entity tax return (Form MO-PTE). No "
                     "election can be made after the deadline, INCLUDING ANY APPROVED EXTENSION.' "
                     "⭐ It reads on the EXTENDED deadline: the election survives an extension, it "
                     "just cannot be made late."),
        "since": "'For tax years ending on or after DECEMBER 31, 2022' (143.436.14)",
    }


# ═══════════════════════════════════════════════════════════════════════════
# MO-PTE LINE 22 -- THE TRUST-FUND DONATION GRID (inside the refund arithmetic)
# ═══════════════════════════════════════════════════════════════════════════
MO_TRUST_FUND_BOXES = (
    ("22a", "Children's Trust Fund", 2),
    ("22b", "Veterans Trust Fund", 2),
    ("22c", "Elderly Home Delivered Meals Trust Fund", 2),
    ("22d", "Missouri National Guard Trust Fund", 2),
    ("22e", "Workers' Memorial Fund", 1),
    ("22f", "Childhood Lead Testing Fund", 1),
    ("22g", "Missouri Military Family Relief Fund", 1),
    ("22h", "General Revenue Fund", 1),
    ("22i", "Organ Donor Program Fund", 2),
    ("22j", "Kansas City Regional Law Enforcement Memorial Foundation Fund", 1),
    ("22k", "Soldiers Memorial Military Museum in St. Louis Fund", 1),
    ("22l", "Medal of Honor Fund", 1),
    ("22m", "Additional Fund Code (write-in)", None),
    ("22n", "Additional Fund Amount (write-in)", None),
)
# ⚠ NON-CONTIGUOUS. Codes 04, 06, 11, 12 and 13 are NOT PUBLISHED.
MO_ADDITIONAL_FUND_CODES = {
    "01": "American Cancer Society Heartland Division",
    "02": "American Diabetes Association Gateway Area",
    "03": "American Heart Association",
    "05": "ALS (Lou Gehrig's Disease)",
    "07": "Muscular Dystrophy Association",
    "08": "March of Dimes",
    "09": "Arthritis Foundation",
    "10": "National Multiple Sclerosis Society",
    "14": "Foster Care and Adoptive Parents Recruitment and Retention Fund",
}
MO_ADDITIONAL_FUND_CAP = 200            # "Minimum irrevocable contribution: $1, not to exceed $200"
MO_ADDITIONAL_FUND_UNCAPPED = ("14",)   # code 14: "Minimum contribution: $1", no cap
MO_TRUST_FUND_WRITEIN_MAX = 2
MO_TRUST_FUND_RULES = (
    "'If you want to give to more than two additional funds, please submit a contribution directly "
    "to the fund.' -> a HARD CAP OF TWO WRITE-IN CODES.",
    "'If you file a balance due return and wish to contribute to the funds, enter the amount in the "
    "appropriate box and ATTACH A SEPARATE CHECK FOR THIS AMOUNT.'",
)


def mo_owner_landing_points() -> dict:
    """N10 -- SIX owner-side landing points across three returns. There is no MO-K-1.

    Missouri has NO K-1 equivalent and never has. Each return carries a
    PER-OWNER EXTRACT OBLIGATION and the owner keys the numbers onto MO-1040 /
    MO-A / MO-NRI.
    """
    return {
        "MO-1065 Page 3 Col 5": "MO-A Part 1 LINE 2 (addition) or LINE 11 (subtraction)",
        "MO-1065 Line 13": "MO-A Part 1 LINE 16 -- ⚠ a DIFFERENT line from the adjustment",
        "MO-1120S Page 3 Col 5": ("MO-1040, 'either as an addition to, or subtraction from, federal "
                                  "adjusted gross income' -- ⚠ the MO-1120S instructions do NOT name "
                                  "the MO-A line numbers that MO-1065's do"),
        "MO-NRP / MO-NRS Column (e)": "Form MO-NRI (Missouri Income Percentage)",
        "MO-PTE Part B Col 6": ("Form MO-TC with alpha code SPA, thence MO-1040 Line 42 / MO-1041 "
                                "Line 16 / MO-1120 Line 17"),
        "MO-2NR Line 2": "MO-1040 LINE 39",
    }


MO_DELIVERY_OBLIGATIONS = (
    ("MO-1065", "'A copy of this part (or its information) must be provided to each partner.' / "
                "'notify each partner of the adjustment to which he or she is entitled.' / for "
                "exempt federal obligations: 'A LIST OF EXEMPT U.S. OBLIGATIONS MUST BE PROVIDED TO "
                "EACH PARTNER BY THE PARTNERSHIP.' / 'Failure to attach a copy of the notification "
                "furnished to you that specifically details the amount of the subtraction being "
                "claimed as the distributive share MAY RESULT IN THE DISALLOWANCE of the deduction.'"),
    ("MO-1120S", "⭐ A REDACTION REQUIREMENT WITH NO MO-1065 COUNTERPART: 'On or before the due date "
                 "(including extensions) ..., furnish a copy of (or extract of all relevant "
                 "information from) the Form MO-1120S to each shareholder, BUT WITH INFORMATION "
                 "ABOUT OTHER SHAREHOLDERS, SUCH AS SOCIAL SECURITY NUMBERS OR SHARE PERCENTAGES, "
                 "REMOVED OR REDACTED.' The print engine needs a PER-SHAREHOLDER REDACTED VARIANT of "
                 "Page 3."),
    ("MO-NRP", "'Form MO-NRP must be completed and a copy (or its information) supplied to the "
               "nonresident partner.'"),
    ("MO-PTE", "143.436.7: 'EACH PARTNERSHIP AND S CORPORATION SHALL REPORT TO EACH OF ITS MEMBERS, "
               "for each tax year, such member's DIRECT pro rata share of the tax imposed ... and "
               "its INDIRECT pro rata share of the tax imposed on any affected business entity in "
               "which such affected business entity is a direct or indirect member.' ⚠ And: 'An "
               "affected business entity paying the tax ... shall INCLUDE WITH THE PAYMENT OF SUCH "
               "TAXES each report provided to a member' -- the member reports go WITH THE PAYMENT, "
               "not merely with the return."),
)


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY TOPICS
# ⚠ topic_name is a CharField(255). Wave-3 harnesses caught four values over
# the cap that were INVISIBLE IN SQLITE and would have been Postgres
# DataErrors in prod, and the Arizona pass had a 390-char CITATION blow its cap
# during Tier-1. These are deliberately short; validate_mo.py measures every
# value against the LIVE model _meta rather than a hardcoded number.
# ═══════════════════════════════════════════════════════════════════════════
AUTHORITY_TOPICS: list[tuple[str, str]] = [
    ("mo_pte_entity_returns",
     "Missouri Forms MO-1065 and MO-1120S: modification-and-allocation returns that compute NO tax, "
     "their gating questions, and the owner allocation grids."),
    ("mo_pte_salt_parity",
     "Missouri Form MO-PTE, the SALT Parity Act elective tax: 4.7% at Line 10, the annual "
     "irrevocable election, the representative gate, and the member opt-out."),
    ("mo_pte_filed_in_addition",
     "MO-PTE is filed IN ADDITION TO MO-1065 / MO-1120S, not instead of them -- published DOR "
     "authority, and the opposite of the Virginia 502/502PTET fork."),
    ("mo_conformity_rolling",
     "Missouri's ROLLING IRC conformity under 143.091, and the verified negatives it produces: no "
     "bonus add-back, no state 179 figure, no conformity bucket."),
    ("mo_sourcing_regimes",
     "The Missouri sourcing regimes: 143.455 apportionment, MO-NRP Part 3 direct accounting, and "
     "Schedule PTE-BD Column (C)'s qualitative 'brains of the operation' test."),
    ("mo_nonresident_withholding",
     "Missouri nonresident withholding: MO-1NR / MO-2NR / MO-3NR at 4.7%, the five exceptions, and "
     "the rule that the PTE election does NOT switch it off."),
    ("mo_pte_credits",
     "Form MO-TC, the SPA alpha code, and the credit-poisoning rule: entity-level credits reduce the "
     "members' credit because they are not tax actually paid."),
    ("mo_pte_efile_posture",
     "The Missouri e-file inversion: MO-1065 and MO-1120S are MeF-eligible; Form MO-PTE is not "
     "e-fileable and not electronically payable."),
    ("mo_business_income_deduction",
     "Schedule PTE-BD -- the entity-level Missouri business income deduction under 143.022, computed "
     "hypothetically at the pass-through entity level."),
]

# ⚠ ALREADY SEEDED IN RS -- REUSE, NEVER RE-CREATE (campaign D-10). Missouri's
# JurisdictionConformitySource row is live with conformity_type = 'rolling', so
# these anchors resolve immediately in prod. They WILL warn on a throwaway
# SQLite harness DB, which is expected and is asserted for in validate_mo.py.
EXISTING_SOURCES_TO_REFERENCE: list[str] = [
    "MO_RSMO_143_091",          # the ROLLING conformity anchor
    "MO_RSMO_143_121",          # the modifications statute -- proof of BOTH verified negatives
    "MO_RSMO_143_436",          # the SALT Parity Act
    "MO_2025_PTE_INSTR",        # the FINAL TY2025 MO-PTE instructions
    "MO_2025_TAX_LEG_CHANGES",  # the DOR's own TY2025 legislative-changes notice (4.7%)
]

AUTHORITY_SOURCES: list[dict] = [
    # --------------------------------------------------------------- the faces
    {
        "source_code": "MO_2025_FORM_MO1065",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "MO",
        "tax_year_start": 2025, "tax_year_end": 2025, "entity_type_code": "1065",
        "title": ("Form MO-1065 (2025), Missouri Partnership Return of Income -- the FACE plus TWO "
                  "PAGES OF EMBEDDED INSTRUCTIONS. There is NO separate MO-1065 instruction PDF."),
        "citation": "Missouri DOR Form MO-1065 (Revised 12-2025; PDF ModDate 2025-11-05; 5 pages)",
        "issuer": "Missouri Department of Revenue",
        "official_url": "https://dor.mo.gov/forms/MO-1065_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.8,
        "topics": ["mo_pte_entity_returns"],
        "notes": ("⚠ NO SCANLINE. ⚠ NO bankruptcy checkbox and NO Charter Number field (MO-1120S and "
                  "MO-PTE have both). ⚠ NO 163(j) machinery ANYWHERE -- a full-text search for '163' "
                  "returns ZERO hits (N7). ⚠ NO MOHELA line (N8) and NO 143.121.3(9) "
                  "disposition-recovery line (N9). HAS a Composite checkbox, which MO-1120S lacks."),
        "excerpts": [
            {"excerpt_label": "The two gating questions and the SHORT-FORM path, verbatim",
             "location_reference": "Form MO-1065 page 1 and the embedded instructions",
             "excerpt_text": ("1. Does the Partnership have any Missouri modifications? Yes No -- If "
                              "Yes, complete Lines 1-13 on pages 1 and 2, and the partner "
                              "information on page 3. 2. Does the Partnership have any nonresident "
                              "partners? Yes No -- If Yes, complete Lines 1-13 on pages 1 and 2, the "
                              "partner information on page 3, and Form MO-NRP. || If you select 'No' "
                              "on both questions 1 and 2 on Form MO-1065, attach a copy of Federal "
                              "Form 1065 and all its schedules, including Schedule K-1. Sign Form "
                              "MO-1065 and mail the return."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("A TWO-CHECKBOX, SIGNATURE-ONLY RETURN when both answers are No. "
                              "Implement it as a FILING MODE, not as a set of blank lines.")},
            {"excerpt_label": "Line 1b -- the KC / St. Louis carve-out, printed on the face",
             "location_reference": "Form MO-1065 page 1, Partnership Adjustments",
             "excerpt_text": ("Less: Kansas City & St. Louis earnings taxes. Enter Lines 1a less 1b "
                              "on Line 1"),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⭐ THE SCOPE BOUNDARY IS PRINTED ON THE FORM. The city earnings taxes "
                              "are CARVED OUT of the state-and-local add-back, so the state module "
                              "must KNOW they exist even though it does not compute them.")},
            {"excerpt_label": "The special-allocation escape hatch -- the anti-704(b) guard",
             "location_reference": "Form MO-1065 page 3 instructions, Column 5",
             "excerpt_text": ("Column 4 and the instructions for Column 5 are based upon the usual "
                              "situation that a single general profit and loss sharing percentage "
                              "applies to all partnership items and related modifications. Attach a "
                              "detailed explanation (including extracts from the partnership "
                              "agreement) if the Column 5 amounts are not based upon the same single "
                              "percentage allocation indicated on Federal Form 1065, Schedule K-1. "
                              "The explanation must include the non-tax purposes and effects of the "
                              "special allocation method."),
             "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("Missouri PRESUMES a single blended percentage and requires narrative "
                              "support otherwise. Cf. 143.411.3 (tax-avoidance special allocations "
                              "disregarded). RED-DEFER R14.")},
        ],
    },
    {
        "source_code": "MO_2025_FORM_MO1120S",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "MO",
        "tax_year_start": 2025, "tax_year_end": 2025, "entity_type_code": "1120S",
        "title": ("Form MO-1120S (2025), Missouri S-Corporation Income Tax Return -- the FACE. "
                  "⚠ THE TITLE LIES: it computes NO tax (143.471.1)."),
        "citation": "Missouri DOR Form MO-1120S (Revised 12-2025; PDF ModDate 2026-01-06; 3 pages)",
        "issuer": "Missouri Department of Revenue",
        "official_url": "https://dor.mo.gov/forms/MO-1120S_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.8,
        "topics": ["mo_pte_entity_returns"],
        "notes": ("143.471.1, verbatim: 'An S corporation, as defined by Section 1361(a)(1) of the "
                  "Internal Revenue Code, SHALL NOT BE SUBJECT TO THE TAXES IMPOSED BY SECTION "
                  "143.071, or other sections imposing income tax on corporations.' MO-1120S is a "
                  "modification-and-allocation return exactly like MO-1065. ⚠ Scanlines "
                  "*25112010001* / *25112020001* / *25112030001*. ⚠ NO composite checkbox (N11)."),
        "excerpts": [
            {"excerpt_label": "The THREE gating questions -- question 3 has no MO-1065 counterpart",
             "location_reference": "Form MO-1120S page 1",
             "excerpt_text": ("1. Does the S-Corporation have any Missouri modifications? Yes No -- "
                              "If Yes, complete Lines 1-15 on pages 1 and 2, and the shareholder "
                              "information on page 3. 2. Does the S-Corporation have any nonresident "
                              "shareholders? Yes No -- If Yes, complete Lines 1-15 ..., the "
                              "shareholder information on page 3, and Form MO-NRS. 3. Does the "
                              "S-Corporation have income derived from sources other than Missouri? "
                              "Yes No -- If Yes, complete and attach Form MO-MSS."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⭐ QUESTION 3 IS THE APPORTIONMENT GATE AND IT EXISTS ONLY ON THE "
                              "S-CORPORATION RETURN. MO-1065 has no apportionment question and no "
                              "apportionment schedule of its own -- partnerships BORROW MO-MSS.")},
            {"excerpt_label": "Lines 10 and 11 -- the 2002-03 depreciation window, IN WORDS",
             "location_reference": "MO-1120S Instructions (2025), Lines 10 and 11",
             "excerpt_text": ("[Line 10] Enter the difference between the federal and Missouri "
                              "depreciation calculated on assets purchased between July 1, 2002 and "
                              "June 30, 2003. See Section 143.121.3(7), RSMo. || [Line 11] Enter any "
                              "depreciation that was previously not recovered when an asset is sold "
                              "or otherwise disposed of and federal bonus depreciation was previously "
                              "taken. (Section 143.121.3(9), RSMo) This can only apply if the "
                              "property was purchased between July 1, 2002, and June 30, 2003."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⭐ THE ONLY DOCUMENT IN THE LANE THAT SPELLS THE WINDOW OUT IN WORDS. "
                              "The other three faces carrying a depreciation line rely on the bare "
                              "statutory cite. ⚠ The verified negative does NOT rest on this -- it "
                              "rests on 143.121.2(3), the add-back provision itself.")},
            {"excerpt_label": "The REDACTION requirement -- no MO-1065 counterpart",
             "location_reference": "MO-1120S Instructions (2025), duty to notify",
             "excerpt_text": ("On or before the due date (including extensions) of the MO-1120S, "
                              "furnish a copy of (or extract of all relevant information from) the "
                              "Form MO-1120S to each shareholder, but with information about other "
                              "shareholders, such as social security numbers or share percentages, "
                              "removed or redacted."),
             "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⭐ The print engine needs a PER-SHAREHOLDER REDACTED VARIANT of Page "
                              "3. MO-1065 has no equivalent sentence.")},
        ],
    },
    {
        "source_code": "MO_2025_FORM_MOPTE",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "MO",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("Form MO-PTE (2025), Missouri Pass-Through Entity Income Tax Return -- THE FACE, "
                  "and the ONLY tax-computing return in the Missouri PTE lane."),
        "citation": ("Missouri DOR Form MO-PTE (printed 'Revised 12-2025'; PDF ModDate 2026-03-31; "
                     "4 pages; NO scanline)"),
        "issuer": "Missouri Department of Revenue",
        "official_url": "https://dor.mo.gov/forms/MO-PTE_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.9,
        "topics": ["mo_pte_salt_parity", "mo_pte_efile_posture"],
        "notes": ("⚠⚠ THE ModDate IS THE STORY, TWICE OVER. (1) The FORM (2026-03-31) is nearly "
                  "THREE MONTHS NEWER THAN ITS OWN INSTRUCTIONS (2026-01-08), so where the two "
                  "disagree the FACE is the later expression of the Department's intent. (2) The "
                  "Department re-stamped the whole MO-PTE package in March 2026 -- AFTER the 2025 "
                  "session that enacted 143.121.3(14) and AFTER the amended SALT-Parity regulation "
                  "took effect on 2025-09-30 -- and STILL DID NOT ADD A CAPITAL-GAIN LINE. That is "
                  "why the finding is real and not an artifact of a stale form. ⚠ U12: the revision "
                  "stamp was NOT advanced, so a vendor keying off the printed code will miss the "
                  "re-issue."),
        "excerpts": [
            {"excerpt_label": "Line 10 -- the 4.7% rate, PRINTED ON THE FACE",
             "location_reference": "Form MO-PTE page 2, Computation of Income Tax",
             "excerpt_text": ("Pass-through entity income tax - Multiply Line 9 by 4.7% - If result "
                              "is less than 0, enter 0"),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⭐ THE RATE IS ON THE FORM FACE, not merely in the instructions. "
                              "⚠⚠ NEVER SOURCE IT FROM THE DOR FAQ, whose rate table stops at 4.8% "
                              "(2024) with NO TY2025 ENTRY. Statutory basis 143.436.3(1)/.4(1): "
                              "'multiplied by the highest rate of tax used to determine a Missouri "
                              "income tax liability for an individual pursuant to section 143.011'.")},
            {"excerpt_label": "The election box and the opt-out box, verbatim",
             "location_reference": "Form MO-PTE page 1 header",
             "excerpt_text": ("Select this box if you are electing to become an Affected Business "
                              "Entity and consent to become subject to the tax imposed by Section "
                              "143.436, RSMo, for the tax period for which this return is filed. || "
                              "Select this box if you have member(s) making an opt-out election. "
                              "Attach Federal K-1 for each opt-out member."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": "The electing instrument, and the opt-out trigger."},
            {"excerpt_label": "Part A Lines 3 and 9 -- MO-PTE FEEDS OFF A FILED MO-1065",
             "location_reference": "Form MO-PTE page 3, Part A, Lines 3 and 9 instructions",
             "excerpt_text": ("Enter the share of fiduciary and partnership adjustment as shown on "
                              "Form MO-1041, Page 2, Part 1, Line 19 [Line 20], and Form MO-1065, "
                              "Line 11 [Line 12] (Section 143.121.4 and 5, RSMo). Copies of any "
                              "Forms MO-1041 or MO-1065 must be attached."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠⚠ STRUCTURAL PROOF that MO-PTE is filed IN ADDITION TO MO-1065, not "
                              "instead of it: the elective return literally draws two of its own "
                              "lines off a filed MO-1065. DO NOT PORT THE VIRGINIA FORK.")},
            {"excerpt_label": "Part B Column 5 -- THE OPT-OUT RE-GROSS-UP, with the DOR's example",
             "location_reference": "Form MO-PTE page 4, Part B, Column 5 instructions",
             "excerpt_text": ("Enter the percentage from Federal Form 1120S or 1065, Schedule K-1. "
                              "If different percentages (e.g. for profit and capital) are listed on "
                              "the same Schedule K-1 from a partnership, you must generally enter the "
                              "profit percentage if the beginning and ending profit percentages are "
                              "the same. Round the percentage to the nearest two decimal places. || "
                              "If any member has made an opt-out election, the remaining "
                              "participating members' percentage must be adjusted to allow the full "
                              "amount of tax paid, to be properly allocated. For example, if an S "
                              "corporation has an opt-out member with a share of 30%, and a "
                              "non-opt-out member with a share percentage of 10%, then that "
                              "non-opt-out member's new credit percentage is 14% (10% divided by "
                              "70%). All non-opt-out member share percentages should be adjusted "
                              "using the same method."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠⚠ COLUMN 5 CARRIES TWO DIFFERENT MEANINGS under one label. With no "
                              "opt-out it is the K-1 percentage; with an opt-out it is a RE-GROSSED-UP "
                              "CREDIT-ALLOCATION percentage that no longer matches any K-1. Store "
                              "them as TWO SEPARATE FIELDS and never overwrite one with the other. "
                              "10 / 70 = 14 is the unit test.")},
            {"excerpt_label": "Part B Column 6 -- 'to the extent paid'",
             "location_reference": "Form MO-PTE page 4, Part B, Column 6 instructions",
             "excerpt_text": ("Enter the member's tax credit to be claimed on the member's income tax "
                              "return. This is the member's pro rata share of the Form MO-PTE, Line "
                              "12 Pass-Through Entity Income Tax Liability, to the extent paid. If "
                              "the member is a S corporation or partnership, leave this column blank "
                              "for that entity. Form 5889 may be used to report the amount of the PTE "
                              "tax credit to each member."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠⚠ 'TO THE EXTENT PAID' is half of the credit-poisoning rule. Combined "
                              "with the Line 11 instruction and 12 CSR 10-2.436(11), the members' "
                              "pool is TAX ACTUALLY PAID -- which is NOT Line 12 whenever the entity "
                              "used MO-TC credits or is in an unpaid-balance posture. ⭐ An UPPER-TIER "
                              "PTE member gets relief via Line 7, NOT via a credit.")},
            {"excerpt_label": "105.1500 RSMo -- the 501(c) roster prohibition, printed on page 4",
             "location_reference": "Form MO-PTE page 4 (and Form MO-TC page 2)",
             "excerpt_text": MO_105_1500_VERBATIM,
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ IN DIRECT TENSION with Part B Column 1's 'All must be listed.' DO "
                              "NOT SILENTLY SUPPRESS AND DO NOT SILENTLY INCLUDE -- surface it as a "
                              "preparer decision and never auto-populate a 501(c) member's identity "
                              "without explicit confirmation.")},
        ],
    },
    # -------------------------------------------------------- the companions
    {
        "source_code": "MO_2025_FORM_MONRP",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "MO",
        "tax_year_start": 2025, "tax_year_end": 2025, "entity_type_code": "1065",
        "title": ("Form MO-NRP (2025), Nonresident Partnership Form -- three parts, form plus "
                  "embedded instructions. ONE MO-NRP PER NONRESIDENT PARTNER."),
        "citation": "Missouri DOR Form MO-NRP (Revised 12-2025; ModDate 2025-11-05; scanline *25000000001*)",
        "issuer": "Missouri Department of Revenue",
        "official_url": "https://dor.mo.gov/forms/MO-NRP_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.7,
        "topics": ["mo_sourcing_regimes", "mo_nonresident_withholding"],
        "notes": ("Required only when the partnership has (1) a nonresident partner AND (2) income "
                  "from Missouri sources. 'Omit Form MO-NRP if all partners are residents of "
                  "Missouri. Use additional Forms MO-NRP if more than one nonresident partner.'"),
        "excerpts": [
            {"excerpt_label": "The DOR's own five-column worked example -- a unit-test vector",
             "location_reference": "Form MO-NRP, Part 1 instructions",
             "excerpt_text": ("Assume $20,000 income from a business deriving $16,000 (80%) from "
                              "Missouri and a single 60% nonresident partner. Columns will appear: "
                              "(a) $20,000, (b) $16,000, (c) 80%, (d) $12,000, and (e) $9,600."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("MO-NRP computes (c) = (b) / (a) and (e) = (d) x (c). ⚠⚠ MO-NRS "
                              "computes the REVERSE: (b) = (a) x (c). DO NOT SHARE A RULE.")},
            {"excerpt_label": "Part 3 and the MO-MSS fallback -- the narrowed U4",
             "location_reference": "Form MO-NRP, Part 3 instructions",
             "excerpt_text": ("Part 3, Line 13, indicates the Missouri source amount that is equal to "
                              "the total of Part 1, Lines 1 and 5, Column (b). The Missouri "
                              "percentage is then computed and entered in Part 1, Column (c). || When "
                              "Part 3 is not applicable, all business income should be apportioned by "
                              "using Method Two A Receipts Factor Apportionment. The apportionment "
                              "factor percentage from Form MO-MSS, Part 1, Line 3 is entered on Form "
                              "MO-NRP, Column (c)."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⭐ The MO-NRP -> MO-MSS cross-reference is DELIBERATE, not an editorial "
                              "slip: 12 CSR 10-2.255(3) puts partnerships on 143.455, IDENTICAL to S "
                              "corporations, which is why no MO-MSP was ever published. It is a "
                              "HIERARCHY, not an election. ⚠ Part 3 direct accounting has NO "
                              "regulatory branch -- the narrowed U4, a GATE-1 SEED QUESTION.")},
            {"excerpt_label": "⚠ The IRS-not-finalized note, printed ON A FINAL FORM (U8)",
             "location_reference": "Form MO-NRP face",
             "excerpt_text": ("Note: At the time the Department finalized their tax booklets, the "
                              "Internal Revenue Service had not finalized the federal income tax "
                              "forms."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠⚠ THE DOR DISCLAIMS FEDERAL-LINE ALIGNMENT ON A FINAL TY2025 FORM. "
                              "EVERY federal line reference in this spec is therefore [UNVERIFIED] "
                              "against the FINAL TY2025 IRS forms and carries the U8 stamp.")},
        ],
    },
    {
        "source_code": "MO_2025_FORM_MONRS",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "MO",
        "tax_year_start": 2025, "tax_year_end": 2025, "entity_type_code": "1120S",
        "title": ("Form MO-NRS (2025), S Corporation Nonresident Form -- ONE PER NONRESIDENT "
                  "SHAREHOLDER. ⚠ Its column derivation is the REVERSE of MO-NRP's."),
        "citation": ("Missouri DOR Form MO-NRS (Revised 12-2025; ModDate 2025-11-18; Attachment "
                     "Sequence No. 1120S-01)"),
        "issuer": "Missouri Department of Revenue",
        "official_url": "https://dor.mo.gov/forms/MO-NRS_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.7,
        "topics": ["mo_sourcing_regimes", "mo_nonresident_withholding"],
        "notes": ("⚠⚠ Part 1 Lines 5b, 8b and 8c are federal SUBSETS, not additive items: 5b is a "
                  "subset of 5a; 8b and 8c are subsets of 8a. ANY 'sum Lines 1 through 10' RULE "
                  "DOUBLE-COUNTS, and MO-1NR defines the withholding base exactly that way (U9). "
                  "⚠ 179 appears here at Part 1 Line 11 as a DISTRIBUTIVE SHARE ITEM, never as a "
                  "modification."),
        "excerpts": [
            {"excerpt_label": "The REVERSE column derivation, verbatim",
             "location_reference": "Form MO-NRS, Part 1 instructions",
             "excerpt_text": ("Column (b): Multiply the amount in Column (a) by the percent in Column "
                              "(c) and enter in Column (b). || Column (c): Enter the percent from "
                              "Form MO-MSS, Line 3."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠⚠ TWO STRUCTURALLY OPPOSITE DERIVATIONS OF THE SAME-LOOKING GRID. "
                              "MO-NRP: (c) = (b) / (a). MO-NRS: (b) = (a) x (c).")},
        ],
    },
    {
        "source_code": "MO_2025_FORM_MOMSS",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "MO",
        "tax_year_start": 2025, "tax_year_end": 2025, "entity_type_code": "1120S",
        "title": ("Form MO-MSS (2025), S-Corporation Allocation and Apportionment Schedule -- and "
                  "the schedule PARTNERSHIPS BORROW, because no MO-MSP was ever published."),
        "citation": ("Missouri DOR Form MO-MSS (Revised 12-2025; ModDate 2025-12-31; Attachment "
                     "Sequence No. 1120S-02)"),
        "issuer": "Missouri Department of Revenue",
        "official_url": "https://dor.mo.gov/forms/MO-MSS_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.7,
        "topics": ["mo_sourcing_regimes"],
        "notes": ("'Do not complete this form if all income is from Missouri sources.' Missouri "
                  "publishes exactly THREE allocation-and-apportionment forms -- MO-MS (C-corp), "
                  "MO-MSS (S-corp) and MO-MS PTE (PTE) -- and partnerships borrow the S-corp one. "
                  "⚠ N12: Part 1 Lines 4-10 enumerate only SHORT-TERM capital gain; there is no "
                  "long-term row, so long-term allocation rides on an unstructured attachment (U10)."),
        "excerpts": [
            {"excerpt_label": "The printed SIX-STEP per-item algorithm -- a unit-test vector",
             "location_reference": "Form MO-MSS, 'Allocation and Apportionment of Share Items'",
             "excerpt_text": ("Assume $15,000 in net rental real estate income (loss) of which "
                              "$12,000 is apportionable income and $3,000 is nonapportionable of "
                              "which $1,000 is directly allocated to Missouri income. Assume an "
                              "apportionment factor of 33.333%: Step 1 $15,000; Step 2 - 3,000 = "
                              "$12,000 apportionable; Step 3 $12,000 x 33.333% = $4,000; Step 4 "
                              "$1,000 nonapportionable allocated to Missouri; Step 5 + $4,000 = "
                              "$5,000 (enter on Form MO-NRS, Part 1, Line 2, Column (b)); Step 6 "
                              "$5,000/15,000 = 33.333% (enter in Column (c)). || If a distributive "
                              "share item is wholly or partially allocated as nonapportionable "
                              "income, a different percentage will be computed for the item."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⭐ THE CONSEQUENCE IS A PER-LINE PERCENTAGE, NOT ONE FACTOR. MO-NRS "
                              "Column (c) is a VECTOR indexed by distributive-share line, defaulting "
                              "to the Line 3 receipts factor. ANY MODEL THAT STORES ONE APPORTIONMENT "
                              "PERCENTAGE PER RETURN IS WRONG.")},
        ],
    },
    {
        "source_code": "MO_2025_FORM_MOMSPTE",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "MO",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("Form MO-MS PTE (2025), Pass-Through Entity Allocation and Apportionment of Income "
                  "Schedule -- a COMPUTING SUB-SPEC of MO_PTE (campaign D-12 Group B)."),
        "citation": ("Missouri DOR Form MO-MS PTE (Revised 12-2025; ModDate 2025-12-04; 1 page; NO "
                     "scanline; Attachment Sequence No. 1120-01)"),
        "issuer": "Missouri Department of Revenue",
        "official_url": "https://dor.mo.gov/forms/MO-MS%20PTE_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.7,
        "topics": ["mo_sourcing_regimes", "mo_pte_salt_parity"],
        "notes": ("⚠ U13: `Attachment Sequence No. 1120-01` is THE SAME SLOT Form MO-MS (the C-corp "
                  "schedule) prints. ⚠ C11: the face note 'Complete mileage information below for "
                  "Method Three - Six' is DEFECTIVE FOR TWO METHODS -- Three is GROSS EARNINGS "
                  "(143.455.14) and Five is a FLAT ONE-HALF (143.455.16). ⭐ Required 'even if this "
                  "balance is zero or negative', which is exactly when Line 9's division by Line 4 "
                  "breaks (U14)."),
        "excerpts": [
            {"excerpt_label": "Part 1 Lines 1-9 -- the BACK-SOLVED percentage, verbatim",
             "location_reference": "Form MO-MS PTE, Part 1",
             "excerpt_text": ("1. Amount of receipts in Missouri. 2. Amount of receipts everywhere. "
                              "3. Receipts factor - Divide Line 1 by Line 2. Note: Stop here if you "
                              "do not have any nonapportionable income. Enter Line 3 on Form MO-PTE, "
                              "Line 5 Percent. 4. Enter balance from Form MO-PTE, Line 4. 5. "
                              "Nonapportionable income - Everywhere - Attach a detailed explanation "
                              "to be considered. 6. Apportioned balance - Subtract Line 5 from Line 4, "
                              "then multiply by Line 3. 7. Nonapportionable income - "
                              "Missouri-allocated - Attach a detailed explanation to be considered. "
                              "8. Preliminary Missouri net income (loss) - Add Lines 6 and 7. 9. "
                              "Divide Line 8 by Line 4. Enter on Form MO-PTE, Line 5 Percent."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⭐⭐ A MATERIALLY DIFFERENT ARCHITECTURE FROM MO-MS / MO-MSS. MO-MSS "
                              "Line 3 produces a FACTOR applied per item. MO-MS PTE Lines 4-9 "
                              "BACK-SOLVE a blended effective percentage so that L4 x L9 = L8. The "
                              "percentage is a DERIVED ARTEFACT, not a factor. ⚠ Line 5 here is "
                              "`Nonapportionable income - Everywhere`, a DIRECT-ENTRY input -- NOT the "
                              "line that carries the L4 x round(L9,3) product. That is MO-PTE Line 5.")},
            {"excerpt_label": "The nonapportionable-income scoping rule (no MO-MSS analogue)",
             "location_reference": "MO-PTE Instructions, Form MO-MS PTE section",
             "excerpt_text": ("Items of nonapportionable income may be reported on the Form MO-MS PTE "
                              "... but only to the extent such items are included in Form MO-PTE, "
                              "Line 4 (Balance). For example, an item of nonapportionable income that "
                              "was added on Form MO-PTE, Line 2, would also be reported on Form MO-MS "
                              "PTE. If all or part of an item of nonapportionable income was "
                              "subtracted on Form MO-PTE Line 3, do not report the amount of "
                              "nonapportionable income so subtracted on Form MO-MS PTE."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⭐ THIS RESOLVES THE APPARENT ORDER-OF-OPERATIONS CONFLICT WITH "
                              "143.436.3(1). The statute sources first and modifies second; the form "
                              "modifies first (Lines 2/3) and sources second (Line 5). Modifications "
                              "enter the Balance, and the Balance is then split into apportionable and "
                              "directly-allocated components under 143.455. THE FORM IS A FAITHFUL "
                              "IMPLEMENTATION OF THE STATUTE, NOT A CONFLICT -- recorded "
                              "affirmatively so a later reviewer does not re-open it.")},
        ],
    },
    {
        "source_code": "MO_2025_SCHEDULE_PTE_BD",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "MO",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("Schedule PTE-BD (2025), Missouri Business Income Deduction -- a COMPUTING "
                  "SUB-SPEC of MO_PTE (campaign D-12 Group B). Its Line 9 feeds MO-PTE Line 6."),
        "citation": ("Missouri DOR Schedule PTE-BD (Revised 12-2025; ModDate 2025-11-26; 1 form page "
                     "+ 1 instruction page; NO scanline)"),
        "issuer": "Missouri Department of Revenue",
        "official_url": "https://dor.mo.gov/forms/Schedule%20PTE%20-%20BD_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.7,
        "topics": ["mo_business_income_deduction", "mo_sourcing_regimes"],
        "notes": ("⭐ THE 20% IS READ OFF LINE 9 OF THE FACE, not derived from 143.022.4's "
                  "revenue-trigger ratchet. A TY2026 pass must RE-READ THE FACE. ⭐ 143.436 pulls "
                  "exactly ONE owner-level deduction into the entity base BY NAME -- the 143.022 BID "
                  "-- and the Department implemented it with a dedicated line and a dedicated "
                  "schedule. That is the strongest structural argument supporting D-10: the "
                  "Department plainly knows how to lift an owner-level item into the PTE base, and it "
                  "did NOT do so for the capital-gain subtraction."),
        "excerpts": [
            {"excerpt_label": "Line 8 and Line 9, verbatim -- the ambiguity and the 20%",
             "location_reference": "Schedule PTE-BD, Lines 8 and 9",
             "excerpt_text": ("8. Missouri Source Net Profit - Total of Column (C), Lines 1-7, reduced "
                              "by any negative amounts, but not below $0. || 9. Allowable Business "
                              "Income Deduction - Multiply Line 8, Column C by 20%. Enter here and on "
                              "Form MO-PTE, Line 6."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠⚠ LINE 8'S WORDING IS GENUINELY AMBIGUOUS AND IT CHANGES THE ANSWER "
                              "(U15): sum-then-floor, or drop-the-negative-rows-then-sum. BUILD "
                              "SUM-THEN-FLOOR (campaign D-12 Group D), supported by 143.022.1's "
                              "'Missouri source net profit from the COMBINATION OF'. And note Lines 6 "
                              "and 7 are DEDUCTIONS with NO PRINTED SIGN CONVENTION.")},
            {"excerpt_label": "Column (C) -- the 'brains of the operation' test, verbatim",
             "location_reference": "Schedule PTE-BD instructions, Column (C)",
             "excerpt_text": ("Items of partnership or S corporation income, gain, loss, and deduction "
                              "must be analyzed to determine the extent to which they are from "
                              "Missouri sources. The source of income is the place where the income "
                              "is produced. An item is from Missouri sources if the item was produced "
                              "by an overall effort centered in Missouri. In general, if the 'brains' "
                              "of the operation resulting in the item are located in Missouri, that "
                              "item is from Missouri sources. Also, an item of income or deduction "
                              "from a partnership or S corporation business is wholly attributable to "
                              "Missouri if the business is only carried on in Missouri. For rental "
                              "income, where the rental property is located outside of Missouri and "
                              "the management is exercised outside of Missouri, that income is not "
                              "from Missouri sources."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠⚠ A THIRD MISSOURI-SOURCING REGIME, QUALITATIVE, ON THE SAME RETURN. "
                              "MO-PTE Line 5 sources under 143.455; Line 6 sources under this. "
                              "ADJACENT LINES, both feeding Line 9. Neither 12 CSR 10-2.190 nor "
                              "10-2.255 mentions it. U17 FULLY OPEN. DO NOT FORCE THEM TO RECONCILE.")},
            {"excerpt_label": "Column (A)'s owner-exempt carve-out (U16)",
             "location_reference": "Schedule PTE-BD instructions, Column (A)",
             "excerpt_text": ("However, do not include on Column (A), Lines 1 through 7, any business "
                              "income that would, ignoring Section 143.022, RSMo, be subtractable or "
                              "deductible for individual partners or shareholders in arriving at their "
                              "Missouri taxable incomes. For example, do not include the amount of "
                              "income received as a payment from a program which provides compensation "
                              "to agricultural producers who have suffered a loss as the result of a "
                              "disaster or emergency. See Section 143.121.3(10), RSMo, for examples of "
                              "such programs."),
             "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ U16 -- an INDEPENDENT, SECOND-ORDER manifestation of the capital-gain "
                              "conflict that cuts the OPPOSITE way: on its face it removes "
                              "owner-exempt capital gain from the DEDUCTION base while the same gain "
                              "stays in the TAX base. ⭐ Its existence is ALSO evidence FOR D-10: a "
                              "wholesale import of owner-level subtractions would make it redundant.")},
        ],
    },
    {
        "source_code": "MO_2025_FORM_MO1NR_2NR_3NR",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "MO",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("Forms MO-1NR, MO-2NR and MO-3NR (2025) -- the nonresident withholding leg: the "
                  "return, the per-owner statement, and the exemption/revocation agreement."),
        "citation": ("Missouri DOR Forms MO-1NR / MO-2NR / MO-3NR (all Revised 12-2025; ModDates "
                     "2025-11-25, 2025-11-25, 2025-11-05)"),
        "issuer": "Missouri Department of Revenue",
        "official_url": "https://dor.mo.gov/forms/MO-1NR_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.7,
        "topics": ["mo_nonresident_withholding"],
        "notes": ("⚠ THREE DIFFERENT CLOCKS AND TWO DIFFERENT P.O. BOXES ON ADJACENT FORMS. MO-1NR / "
                  "MO-2NR are due by the ORIGINAL OR EXTENDED due date; MO-3NR by the due date "
                  "WITHOUT REGARD TO AN EXTENSION. MO-1NR / MO-2NR mail to P.O. Box 555; MO-3NR to "
                  "P.O. Box 3815. ⚠ MO-3NR is filed BY THE OWNER with the Department, not with the "
                  "entity, yet the entity's withholding duty turns on whether it was filed -- model "
                  "it as an OWNER ATTRIBUTE with an effective date and a revocation date."),
        "excerpts": [
            {"excerpt_label": "The rate and the DEFECTIVE base definition, verbatim (U9)",
             "location_reference": "Form MO-1NR embedded instructions",
             "excerpt_text": ("The amount of tax to be withheld for tax year 2025 is 4.70 percent "
                              "(0.047) of the partner's or shareholder's share of Missouri source "
                              "distributive income, or the tax withheld may be determined based on "
                              "Missouri withholding tables if the partner or shareholder submits a "
                              "Missouri Withholding Allowance Certification (Form MO W-4). || "
                              "Missouri source distributive income consists of those items on an "
                              "individual's K-1 schedule that are used to arrive at federal adjusted "
                              "gross income as apportioned or allocated to Missouri. The Missouri "
                              "source distributive income of partnerships is the net total of the "
                              "amounts listed on Lines 1 through 11 of the Nonresident Partnership "
                              "Form (Form MO-NRP). The Missouri source distributive income of S "
                              "corporations is the net total of the amounts listed on Lines 1 through "
                              "10 of the S Corporation Nonresident Form (Form MO-NRS)."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠⚠ BOTH SUMMATIONS ARE DEFECTIVE AS LITERALLY WRITTEN. MO-NRS Lines "
                              "1-10 DOUBLE-COUNT (5b is a subset of 5a; 8b and 8c are subsets of 8a). "
                              "MO-NRP 'Lines 1 through 11' reads over a NON-CONTIGUOUS set and "
                              "SILENTLY EXCLUDES 179, contributions and other deductions. THIS "
                              "DETERMINES CASH WITHHELD. Build with the subsets suppressed and flag "
                              "any return where 5b/8b/8c is non-zero.")},
            {"excerpt_label": "MO-2NR scope rules and the Name Control algorithm, verbatim",
             "location_reference": "Form MO-2NR face",
             "excerpt_text": ("Only individual nonresident partners or S corporation shareholders are "
                              "subject to withholding. Do not withhold for any partners or S "
                              "corporation shareholders who are partnerships, corporations, trusts, or "
                              "estates. Grantor trusts that file or can file in accordance with IRC "
                              "Reg. Section 1.671.4(b) are considered individuals. || DO NOT withhold "
                              "for any partners or shareholders who include their Missouri income on a "
                              "composite return. || Issue Form MO-2NR, even if no tax is withheld or "
                              "there is an exemption certificate on file. || Enter the first four "
                              "letters of the partner's/shareholder's last name. (Please use all "
                              "capital letters as shown.) John Brown--BROW, Juan DeJesus--DEJE, Joan "
                              "A. Lee--LEE, Pedro Torres-Lopes--TORR, Jean McCarty--MCCA, John "
                              "O'Neill--ONEI"),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⭐ A PER-OWNER ENTITY-TYPE GATE with an explicit grantor-trust carve-in, "
                              "a ZERO-DOLLAR MO-2NR that is STILL REQUIRED, and a printable, testable "
                              "string algorithm (LEE is three characters -- short names are NOT "
                              "padded; hyphens split; apostrophes are dropped).")},
        ],
    },
    {
        "source_code": "MO_2025_FORM_MOTC",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "MO",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("Form MO-TC (2025), Miscellaneous Income Tax Credits -- the SPA alpha code, and "
                  "the entity-level credit that DESTROYS the members' credit."),
        "citation": "Missouri DOR Form MO-TC (Revised 12-2025; ModDate 2025-12-29; scanline *25306010001*)",
        "issuer": "Missouri Department of Revenue",
        "official_url": "https://dor.mo.gov/forms/MO-TC_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.7,
        "topics": ["mo_pte_credits"],
        "notes": ("Ten credit rows, then Line 11 subtotals, Line 12 the parent return's liability "
                  "(MO-PTE Line 10), Line 13 the total (-> MO-PTE Line 11). 'Line 13 cannot exceed "
                  "the amount on Line 12, UNLESS THE CREDIT IS REFUNDABLE.' An electing PTE uses "
                  "COLUMN 1 ONLY. ⚠ Defect #8: the MO-TC header omits MO-PTE although Lines 12 and 13 "
                  "both reference it. ⚠ MO-TC carries ITS OWN SIGNATURE BLOCK and an "
                  "immigration-compliance declaration, separate from the parent return's. ⚠ EVERY "
                  "non-DOR credit is CERTIFICATE-GATED -- the engine cannot compute any of them (R9)."),
        "excerpts": [
            {"excerpt_label": "The SPA row, verbatim -- confirmed on the FINAL TY2025 form",
             "location_reference": "Form MO-TC page 2, Missouri Department of Revenue issuer block",
             "excerpt_text": "SPA    SALT Parity    Fed. K-1, Form 5889 or equivalent.",
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⭐ The owner-side alpha code, confirmed VERBATIM rather than carried on "
                              "a draft's authority. Note 'OR EQUIVALENT', which matches the MO-PTE "
                              "instruction that 'Form 5889 MAY be used' -- a Delvio-generated member "
                              "report is equally valid and is the cleaner v1 answer.")},
            {"excerpt_label": "The ordering rule, printed on the face",
             "location_reference": "Form MO-TC face",
             "excerpt_text": ("Each credit will apply against your tax liability in the order they "
                              "appear below."),
             "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("Credit ordering is PREPARER-CONTROLLED BY ROW POSITION, never "
                              "engine-determined.")},
        ],
    },
    {
        "source_code": "MO_2025_FORM_5889",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "MO",
        "tax_year_start": 2025,
        "title": ("Form 5889, Pass-Through Entity Member Tax Credit -- OPTIONAL, and its Part B "
                  "column references have been ONE COLUMN STALE SINCE TY2024."),
        "citation": ("Missouri DOR Form 5889 (Revised 03-2025; ModDate 2025-03-03; no year suffix "
                     "exists at this URL)"),
        "issuer": "Missouri Department of Revenue",
        "official_url": "https://dor.mo.gov/forms/5889.pdf",
        "current_status": "active", "is_substantive_authority": False, "trust_score": 8.5,
        "topics": ["mo_pte_credits"],
        "notes": MO_5889_DEFECT_NOTE + " " + MO_5889_THREE_NAMES,
        "excerpts": [
            {"excerpt_label": "The stale line instructions, verbatim",
             "location_reference": "Form 5889, Lines 1 and 2",
             "excerpt_text": ("Line 1: Enter the membership percentage, as reflected on Form MO-PTE, "
                              "Part B, Column 4. || Line 2: Enter the affected member's pro-rata share "
                              "of the tax imposed, as reflected on Form MO-PTE, Part B, Column 5."),
             "is_key_excerpt": True, "effective_year_start": 2025,
             "summary_text": ("⚠ ONE COLUMN OFF. TY2025 MO-PTE Part B has Column 4 = SSN/FEIN, Column "
                              "5 = Membership %, Column 6 = Member's PTE Tax Credit. MAP BY SUBSTANCE "
                              "(Line 1 <- Col 5; Line 2 <- Col 6), never by the printed numbers, and "
                              "never reproduce the stale numbers in help text.")},
        ],
    },
    # ------------------------------------------------------------- statutes
    {
        "source_code": "MO_RSMO_143_455",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "MO",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("Mo. Rev. Stat. 143.455 -- allocation and apportionment. THE sourcing statute for "
                  "the whole Missouri PTE lane, S corporations AND partnerships alike."),
        "citation": "Mo. Rev. Stat. 143.455 (eff. 28 Aug 2018; L. 2018 S.B. 884; single version)",
        "issuer": "Missouri Revisor of Statutes",
        "official_url": "https://revisor.mo.gov/main/OneSection.aspx?section=143.455",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.9,
        "topics": ["mo_sourcing_regimes"],
        "notes": ("VINTAGE-CHECKED: single version, unamended since 2018 -- the served text IS the "
                  "TY2025 text. Structure: .2 applicability (which the forms MIS-CITE as the receipts "
                  "factor), .3 definitions incl. commercial domicile, .4 taxable-in-another-state, "
                  ".6-.9 the seven allocation rules incl. the TWO THROWBACK-STYLE tests at .7(2) and "
                  ".9, .10 the single receipts factor, .11-.12 sourcing, .13(1)/(2) the two Method "
                  "Seven routes, .14-.17 the four special methods, .19 the NOL ratio, .20 investment "
                  "funds service corporations."),
        "excerpts": [
            {"excerpt_label": "⚠ C11 -- the four special methods, verbatim, and only TWO are mileage",
             "location_reference": "Mo. Rev. Stat. 143.455.14 to .17",
             "excerpt_text": ("[.14 Transportation] ...shall report its gross earnings within the "
                              "state on intrastate business and shall also report its gross earnings "
                              "on all interstate business done in this state... This subsection shall "
                              "not apply to a railroad. || [.15 Railroad] ...as the mileage used over "
                              "the rails and lines of such corporation in the state shall bear to the "
                              "total mileage... || [.16 Interstate Bridge] shall include in its "
                              "Missouri taxable income one-half of the net income from the operation "
                              "of a bridge between this and another state... || [.17 Telephone and "
                              "Telegraph] ...such proportion of such revenue as the mileage involved "
                              "in this state shall bear to the total mileage involved..."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠⚠ CAMPAIGN D-12 C11. Method THREE is a GROSS-EARNINGS rule and Method "
                              "FIVE is a FLAT ONE-HALF rule. Only FOUR and SIX are mileage-driven, so "
                              "the MO-MS PTE face note 'Complete mileage information below for Method "
                              "Three - Six' is defective for TWO methods, not one. Corroborated by "
                              "12 CSR 10-2.045(14)(B). RESTATE BEFORE PROPAGATING.")},
        ],
    },
    {
        "source_code": "MO_RSMO_143_022",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "MO",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": "Mo. Rev. Stat. 143.022 -- the Missouri business income deduction behind Schedule PTE-BD",
        "citation": ("Mo. Rev. Stat. 143.022 (eff. 28 Aug 2023; L. 2014 S.B. 509 & 496, A.L. 2018 "
                     "H.B. 2540, A.L. 2023 H.B. 202 merged with S.B. 138)"),
        "issuer": "Missouri Revisor of Statutes",
        "official_url": "https://revisor.mo.gov/main/OneSection.aspx?section=143.022",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.9,
        "topics": ["mo_business_income_deduction"],
        "notes": ("⚠ .4 sets only the 20% CEILING and .5 gates increases on a $150,000,000 "
                  "net-general-revenue growth test with a 5-point-per-year, one-increase-per-calendar-"
                  "year mechanism. THE OPERATIVE TY2025 FIGURE IS READ OFF SCHEDULE PTE-BD LINE 9, "
                  "not derived from the ratchet."),
        "excerpts": [
            {"excerpt_label": "143.022.1 -- 'net profit from the COMBINATION of' (settles U15's direction)",
             "location_reference": "Mo. Rev. Stat. 143.022.1",
             "excerpt_text": ("the income greater than zero arising from transactions in the regular "
                              "course of all of a taxpayer's trade or business and shall be limited to "
                              "the Missouri source net profit from the combination of [Schedule C, "
                              "Schedule E Part II, Schedule F, Form 4835]"),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("'Net profit from the COMBINATION' is a SUM, which supports the "
                              "SUM-THEN-FLOOR reading of Schedule PTE-BD Line 8 that campaign D-12 "
                              "Group D ratified.")},
        ],
    },
    {
        "source_code": "MO_RSMO_143_411_471",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "MO",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("Mo. Rev. Stat. 143.411 and 143.471 -- owner modifications, composite returns, "
                  "nonresident withholding, and the S-corporation bank credits"),
        "citation": ("Mo. Rev. Stat. 143.411 (eff. 20 May 1997) and 143.471 (eff. 28 Aug 2018; "
                     "A.L. 2018 S.B. 884)"),
        "issuer": "Missouri Revisor of Statutes",
        "official_url": "https://revisor.mo.gov/main/OneSection.aspx?section=143.411",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.9,
        "topics": ["mo_nonresident_withholding", "mo_pte_entity_returns"],
        "notes": ("143.471.1: an S corporation IS NOT SUBJECT TO 143.071 -- MO-1120S computes no tax. "
                  "⭐ 143.471.4: 'Notwithstanding subsection 3 ..., FOR ALL TAX YEARS BEGINNING ON OR "
                  "AFTER JANUARY 1, 2020, the items referred to in that subsection shall be determined "
                  "to be from sources within this state pursuant to regulations of the director of "
                  "revenue in a manner consistent with the division of income provisions of SECTION "
                  "143.455 and section 143.461.' 143.411.3 is the anti-avoidance special-allocation "
                  "rule. 143.471.10-.12 are the BTC bank / S&L / credit-institution credits with a "
                  "carryforward of 'the lesser of five years or until used' (R6)."),
        "excerpts": [
            {"excerpt_label": "143.411.5 -- the FIVE exceptions, DISJUNCTIVE in the statute (U22)",
             "location_reference": "Mo. Rev. Stat. 143.411.5",
             "excerpt_text": MO_WH_EXCEPTIONS_STATUTE_VERBATIM,
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": MO_WH_EXCEPTIONS_RULING_NOTE},
        ],
    },
    {
        "source_code": "MO_RSMO_143_581_421",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "MO",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("Mo. Rev. Stat. 143.581 (partnership returns) and 143.421 (nonresident partner's "
                  "portion) -- the filing trigger, and the delegation that answers U4"),
        "citation": ("Mo. Rev. Stat. 143.581 (eff. 1 Jan 1973; L. 1972 S.B. 549) and 143.421 "
                     "(eff. 1 Jan 1973; never amended)"),
        "issuer": "Missouri Revisor of Statutes",
        "official_url": "https://revisor.mo.gov/main/OneSection.aspx?section=143.581",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.9,
        "topics": ["mo_sourcing_regimes", "mo_pte_entity_returns"],
        "notes": MO_NO_143_181_REGULATION,
        "excerpts": [
            {"excerpt_label": "143.421.1 and .4 -- the DELEGATION, and the 'on application' limit",
             "location_reference": "Mo. Rev. Stat. 143.421.1 and .4",
             "excerpt_text": ("[.1] ...as such part is determined under regulations prescribed by the "
                              "director of revenue in accordance with the general rules in section "
                              "143.181. || [.4] The director of revenue may, on application, authorize "
                              "the use of such other methods of determining a nonresident partner's "
                              "portion of partnership items derived from or connected with sources in "
                              "this state, and the modifications related thereto, as may be "
                              "appropriate and equitable, on such terms and conditions as he may "
                              "require."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⭐ .1 does NOT fix the method -- it delegates to the director's "
                              "regulations, and the director's regulation (12 CSR 10-2.255) says "
                              "143.455. ⚠ .4 is the ONLY statutory room for MO-NRP Part 3 direct "
                              "accounting, and it requires an APPLICATION that nothing on the form or "
                              "in either regulation mentions. THE NARROWED U4 -- A GATE-1 SEED "
                              "QUESTION, NOT A FREE PREPARER ELECTION.")},
        ],
    },
    # ---------------------------------------------------------- regulations
    {
        "source_code": "MO_12CSR_10_2_436",
        "source_type": "state_regulation", "source_rank": "controlling", "jurisdiction_code": "MO",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("12 CSR 10-2.436, SALT Parity Act Implementation -- and the ONLY place TWO LIVE "
                  "CLIENT-HARM RULES ARE STATED AT ALL"),
        "citation": ("12 CSR 10-2.436 (amended filed 3/31/2025, eff. 9/30/2025; authority cited as "
                     "'section 143.436, RSMo Supp. 2024')"),
        "issuer": "Missouri Department of Revenue / Missouri Secretary of State",
        "official_url": ("https://dor.mo.gov/resources/official-final-rules/documents/"
                         "12_CSR_10-2_436_SALT_Parity_Act_Implementation-_Law_9-30-2025.pdf"),
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.9,
        "topics": ["mo_pte_salt_parity", "mo_nonresident_withholding", "mo_pte_credits"],
        "notes": ("(2) the representative precondition; (3) the election deadline INCLUDING approved "
                  "extensions; (4) irrevocability; (5) Form 2827 OR 2827 PTE; (6) removal does not "
                  "unwind prior binding actions; (7) NO ESTIMATED TAX; ⚠⚠ (8) THE ELECTION DOES NOT "
                  "RELIEVE WITHHOLDING; (9) extension extends PAYMENT but interest accrues under "
                  "143.731.2; (10) the six-month federal-extension cap; ⚠⚠ (11) credits computed on "
                  "TAX ACTUALLY PAID; (12)(A)-(D) the opt-out, the 10/70 = 14% example, credit "
                  "ineligibility with the pre-opt-out carryforward saving clause, and the FULL "
                  "RECOMPUTATION duty."),
        "excerpts": [
            {"excerpt_label": "⚠⚠ (8) -- the election does NOT relieve withholding, verbatim",
             "location_reference": "12 CSR 10-2.436(8)",
             "excerpt_text": MO_WH_SURVIVES_ELECTION_VERBATIM,
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": MO_WH_SURVIVES_ELECTION_NOTE},
            {"excerpt_label": "⚠⚠ (11) -- tax ACTUALLY PAID, and the credit-poisoning rule, verbatim",
             "location_reference": "12 CSR 10-2.436(11)",
             "excerpt_text": ("The tax credits granted to a member ... shall be computed based on the "
                              "member's direct and indirect pro rata share of the tax actually paid "
                              "... If an affected business entity reduces its tax liability under "
                              "section 143.436, RSMo, by use of tax credits, other than a credit for "
                              "payment or overpayment of this tax, the affected business entity's tax "
                              "actually paid will generally be reduced."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠⚠ A LIVE CLIENT-HARM PATH. Using a Missouri miscellaneous credit at "
                              "the entity level converts a DOLLAR-FOR-DOLLAR OWNER CREDIT INTO "
                              "NOTHING, and THE FORM GIVES THE ENGINE NO FIELD FOR TAX ACTUALLY PAID. "
                              "Derived field plus a HARD diagnostic whenever Line 11 > 0. (C5 / U20)")},
            {"excerpt_label": "(7) -- NO estimated tax, stated as a POSITIVE rule",
             "location_reference": "12 CSR 10-2.436(7)",
             "excerpt_text": ("An affected business entity is not subject to an estimated income tax "
                              "declaration filing requirement, or an estimated income tax payment "
                              "requirement, with respect to the tax under section 143.436, RSMo. An "
                              "affected business entity may choose to make an early payment of its "
                              "anticipated tax liability for a tax year, even if the tax year is not "
                              "yet complete."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("A TRUE VERIFIED NEGATIVE -- the regulation STATES THE OBLIGATION DOES "
                              "NOT EXIST, rather than merely being silent. No MO-2210 / Form 500C "
                              "analogue, no exception ladder, no underpayment worksheet. ⚠ BUT the "
                              "blanket phrasing 'no underpayment-penalty regime at all' OVERREACHES: "
                              "interest under 143.731.2 (preserved by (9)) and the 5% late-payment "
                              "addition BOTH SURVIVE.")},
        ],
    },
    {
        "source_code": "MO_12CSR_10_2_190_255",
        "source_type": "state_regulation", "source_rank": "controlling", "jurisdiction_code": "MO",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("12 CSR 10-2.190 and 12 CSR 10-2.255 -- the delegation chain that NARROWED U4 and "
                  "put PARTNERSHIP nonresident sourcing on 143.455, identical to S corporations"),
        "citation": ("12 CSR 10-2.190 (amended filed 2024-01-24, eff. 2024-09-30) and 12 CSR 10-2.255 "
                     "(filed 2020-09-08, eff. 2021-03-30, never amended)"),
        "issuer": "Missouri Secretary of State (official chapter capture of 12 CSR 10-2)",
        "official_url": "https://www.sos.mo.gov/cmsimages/adrules/csr/current/12csr/12c10-2.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.8,
        "topics": ["mo_sourcing_regimes"],
        "notes": ("⚠ PULLED 2026-08-19 as the U4 follow-up (campaign D-12 A8), from the SECRETARY OF "
                  "STATE capture -- the official one; the DOR copy was deliberately not used. "
                  "VINTAGE-CHECKED because a stale-vintage read earlier in the campaign produced a "
                  "false statute-vs-form conflict that had to be withdrawn: .190's latest amendment "
                  "took effect BEFORE TY2025 began with no amendment for or after TY2025, and .255 "
                  "has NEVER been amended, so both texts ARE the TY2025 texts. SOS pages "
                  "footer-stamped 1/29/26. ⚠ A browser User-Agent is required -- bare curl returns "
                  "403. .190's real title is broader than the campaign assumed: 'Partnership and S "
                  "Corporation Annual Return Filing Requirements, Composite Returns, and Nonresident "
                  "Partner/Shareholder Income Tax Withholding'."),
        "excerpts": [
            {"excerpt_label": "12 CSR 10-2.190(2)(C) -- the DELEGATION, verbatim",
             "location_reference": "12 CSR 10-2.190(2)(C) (SOS chapter capture pp. 50-51)",
             "excerpt_text": ("The partnership return or S corporation return shall reflect, among "
                              "other things, the partnership or S corporation's Missouri allocated "
                              "income and Missouri apportioned income consistent with 12 CSR 10-2.255. "
                              "The partnership or S corporation's Missouri allocated income and "
                              "Missouri apportioned income shall be the basis on which a nonresident "
                              "partner or shareholder, consistent with 12 CSR 10-2.255, determines the "
                              "items of partnership or S corporation income, gain, loss, or deduction "
                              "entering into nonresident federal adjusted gross income from sources "
                              "within this state."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": (".190 does NOT decide sourcing itself -- it DELEGATES to .255. Its "
                              "composite half routes to the same place at (3)(A).")},
            {"excerpt_label": "⭐⭐ 12 CSR 10-2.255(3) -- the answer to U4, verbatim",
             "location_reference": "12 CSR 10-2.255(3) (SOS chapter capture pp. 55-56)",
             "excerpt_text": ("(3) Partnership Income Derived from Sources within this State. For all "
                              "tax years beginning on or after January 1, 2020, items of partnership "
                              "income, gain, loss, or deduction entering into a nonresident partner's "
                              "federal adjusted gross income are from sources within this state to the "
                              "extent that- (A) The partnership would include that item in its "
                              "Missouri Apportioned Income by applying the provisions of section "
                              "143.455, RSMo, and the regulations issued in connection with section "
                              "143.455, RSMo, (including any applicable regulations applying to unique "
                              "industries); or (B) The partnership would include that item in its "
                              "Missouri Allocated Income by applying the provisions of section "
                              "143.455, RSMo..."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⭐⭐ PARTNERSHIPS AND S CORPORATIONS RUN THE SAME STATUTE. (2) is the "
                              "word-for-word S-corporation twin; (4) supplies the bridge ('any "
                              "references in section 143.455 to the term corporation shall be deemed "
                              "to refer instead to the type of entity to which this regulation is "
                              "applied'); (1)(B) pins the factor to 143.455.10. ⚠⚠ CONSEQUENCE: the "
                              "MO-NRP vs MO-MS PTE divergence is now EXPECTED-ZERO and a non-zero "
                              "delta reads as a PROBABLE ERROR. ⚠ It is a CLOSED TWO-BRANCH TEST with "
                              "NO separate-accounting branch -- which is what leaves MO-NRP Part 3 "
                              "narrowed-but-open.")},
        ],
    },
    {
        "source_code": "MO_12CSR_10_2_076",
        "source_type": "state_regulation", "source_rank": "controlling", "jurisdiction_code": "MO",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("12 CSR 10-2.076, Allocation and Apportionment -- the alternative-apportionment "
                  "petition machinery and its 60-day-BEFORE-YEAR-END deadline"),
        "citation": "12 CSR 10-2.076(1) and (2)(G) (beginning on or after January 1, 2020)",
        "issuer": "Missouri Department of Revenue / Missouri Secretary of State",
        "official_url": "https://www.sos.mo.gov/cmsimages/adrules/csr/current/12csr/12c10-2.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.5,
        "topics": ["mo_sourcing_regimes"],
        "notes": ("⚠ NOT TRANSCRIBED IN FULL -- it remains a named open item for U5 (the Method Two A "
                  "default), U10 (long-term capital gain allocation on MO-MSS) and U14 (MO-MS PTE "
                  "Line 9's zero/negative denominator). Only (2)(G) was quoted, on the verification "
                  "pass, to correct the claim that the 60-day deadline lived only in the MO-PTE "
                  "instructions."),
        "excerpts": [
            {"excerpt_label": "(2)(G) -- the petition deadline is IN THE REGULATION, verbatim",
             "location_reference": "12 CSR 10-2.076(2)(G)",
             "excerpt_text": ("the filing of written or electronic document(s) with the director at "
                              "least sixty (60) days before the end of the tax year to which "
                              "alternative apportionment is sought to apply, in the manner "
                              "prescribed"),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ 22 correction #10: 'ONLY in the MO-PTE instructions' was WRONG. The "
                              "deadline is REGULATORY and BINDS ALL THREE LANES. That STRENGTHENS the "
                              "advisory diagnostic rather than weakening it -- and it stays ADVISORY, "
                              "because the window closes BEFORE the return is prepared. Followed by a "
                              "seven-item content list including a Form 2827 power of attorney.")},
        ],
    },
    # ------------------------------------------------- DOR web and third party
    {
        "source_code": "MO_DOR_PTE_FAQ",
        "source_type": "state_conformity_notice", "source_rank": "implementation_official",
        "jurisdiction_code": "MO", "tax_year_start": 2025,
        "title": ("Missouri DOR, FAQs -- Pass-Through Entity Tax. THE published authority that MO-PTE "
                  "is filed IN ADDITION TO MO-1065 / MO-1120S. ⚠ Its RATE TABLE IS STALE."),
        "citation": "Missouri DOR, FAQs - Pass-Through Entity Tax (re-pulled in full 2026-08-19)",
        "issuer": "Missouri Department of Revenue",
        "official_url": "https://dor.mo.gov/faq/taxation/business/entity-tax.html",
        "current_status": "active", "is_substantive_authority": False, "trust_score": 8.8,
        "topics": ["mo_pte_filed_in_addition", "mo_pte_efile_posture"],
        "notes": ("⚠⚠ DEFECT #19: the 'What is the tax rate for pass-through entity tax?' table lists "
                  "5.3% (2022), 4.95% (2023) and 4.8% (2024) AND THEN STOPS -- there is NO TY2025 "
                  "entry, while the form face prints 4.7% at Line 10. NEVER SOURCE THE RATE FROM THE "
                  "FAQ. ⚠ The FAQ also states the opt-out gate differently from the instructions "
                  "('tax year ends on or after August 28, 2024') -- no TY2025 impact, material for "
                  "TY2024 amended returns (U2). ⚠ It says NOTHING about capital gains at the entity "
                  "level (U3) and NOTHING about withholding surviving the election (U21)."),
        "excerpts": [
            {"excerpt_label": "⭐⭐ BOTH RETURNS ARE FILED -- the Q&A that closes W2, verbatim",
             "location_reference": "DOR FAQs - Pass-Through Entity Tax",
             "excerpt_text": ("Q: If a partnership or S corporation elects to file a MO-PTE return, "
                              "should it still file a MO-1065 or MO-1120S? A: Yes. The filing of the "
                              "MO-PTE does not substitute for a partnership filing its MO-1065 or an S "
                              "corporation filing its MO-1120S. [The answer continues that partners "
                              "and shareholders must still make the applicable adjustments, including "
                              "those related to state and local income taxes.]"),
             "is_key_excerpt": True, "effective_year_start": 2025,
             "summary_text": ("⚠⚠ PUBLISHED DOR AUTHORITY, NOT AN INFERENCE. This is the OPPOSITE of "
                              "Virginia's 502 / 502PTET fork and THE VIRGINIA PATTERN MUST NOT BE "
                              "PORTED -- doing so would leave every electing Missouri client's filing "
                              "INCOMPLETE.")},
            {"excerpt_label": "⭐⭐ NOT E-FILEABLE AND NOT ELECTRONICALLY PAYABLE, verbatim",
             "location_reference": "DOR FAQs - Pass-Through Entity Tax",
             "excerpt_text": ("No. You must submit your return Form MO-PTE to PO Box 3080, Jefferson "
                              "City, MO 65105-3080, or by email to pteincome@dor.mo.gov. || No. You "
                              "must submit your payment with Form MO-PTEV or MO-PTEAP with a check, "
                              "money order, or cashier's check to PO Box 3080... || No. A pass-through "
                              "entity is not required to make estimated tax payments of the "
                              "pass-through entity tax."),
             "is_key_excerpt": True, "effective_year_start": 2025,
             "summary_text": ("⚠⚠ THE BUILD PLAN INVERTS: the TAX-COMPUTING return is the MANUAL one "
                              "and MeF scope HALVES to MO-1065 + MO-1120S. ⚠ 'Paper-only' overstates "
                              "it -- the e-mailed PDF is sanctioned. ⚠⚠ Campaign D-12 A6: DELVIO DOES "
                              "NOT AUTOMATE THAT E-MAIL CHANNEL; it carries member SSNs in the clear.")},
        ],
    },
    {
        "source_code": "MO_DOR_EFILE_PAGES",
        "source_type": "state_efile_spec", "source_rank": "implementation_official",
        "jurisdiction_code": "MO", "tax_year_start": 2025,
        "title": ("Missouri DOR Partnership and Corporation-Income e-file pages -- the MeF ENUMERATION "
                  "that omits MO-PTE, plus the 22-vendor approved list"),
        "citation": ("Missouri DOR, /taxation/business/tax-types/partnership/efile.html and "
                     "/taxation/business/tax-types/corporation-income/efile.html (2026-08-19)"),
        "issuer": "Missouri Department of Revenue",
        "official_url": "https://dor.mo.gov/taxation/business/tax-types/corporation-income/efile.html",
        "current_status": "active", "is_substantive_authority": False, "trust_score": 8.8,
        "topics": ["mo_pte_efile_posture"],
        "notes": ("⭐ THE ADJUDICATION TURNS ON THESE TWO PAGES: they ENUMERATE the eligible returns "
                  "and OMIT MO-PTE, so this is not an argument from silence. Independently "
                  "corroborated by Drake Software KB 18013: 'Form MOPTE and the MOPTE Voucher are not "
                  "e-fileable and there are no options for electronic payments this year.'"),
        "excerpts": [
            {"excerpt_label": "The corporation-income enumeration, verbatim",
             "location_reference": "DOR Corporation-income e-file page",
             "excerpt_text": ("Corporations may file MO-1120 Corporation Income tax returns and "
                              "MO-1120S S Corporation Income tax returns electronically... through "
                              "Modernized E-File (MeF)."),
             "is_key_excerpt": True, "effective_year_start": 2025,
             "summary_text": ("Two returns named, a 22-vendor approved list scoped to those two, and "
                              "MO-PTE absent. The Partnership page names only MO-1065.")},
        ],
    },
    {
        "source_code": "MO_2025_EXTENSION_FORMS",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "MO",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("Forms MO-7004 and MO-60 (2025) -- and the THREE-WAY EXTENSION CONTRADICTION the "
                  "Department has published (U24)"),
        "citation": ("Missouri DOR Form MO-7004 (Revised 12-2025; ModDate 2025-11-17) and Form MO-60 "
                     "(Revised 12-2025; ModDate 2025-11-04)"),
        "issuer": "Missouri Department of Revenue",
        "official_url": "https://dor.mo.gov/forms/MO-7004_2025.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.0,
        "topics": ["mo_pte_salt_parity"],
        "notes": ("⚠ MO-7004 CARRIES A `Pass-Through Entity Income Tax Return, Form MO-PTE` CHECKBOX "
                  "and routes to P.O. Box 3080. ⚠ MO-7004 also says S corporations should 'use Form "
                  "MO-60'; MO-60's face has NO S-CORP CHECKBOX (only MO-1040, MO-1041 and the "
                  "composite MO-1040) and its instructions say S corporations ride the federal 7004; "
                  "and MO-1120S itself names NO Missouri form. ⚠ MO-7004 says the extension runs 'up "
                  "to 180 days' while the MO-PTE instructions say 'not to exceed six months'."),
        "excerpts": [
            {"excerpt_label": "⭐⭐ The INVERTED payment rule -- for MO-PTE only",
             "location_reference": "MO-PTE Instructions and Form MO-7004 instructions",
             "excerpt_text": ("[MO-PTE Instructions] An extension of time to file will extend the time "
                              "for payment of the tax. The pass-through entity must pay the tax on or "
                              "before the extended due date to avoid a 5 percent addition to tax. "
                              "However, simple interest will be calculated from the original return "
                              "due date until the tax is paid. || [MO-7004] If filing Form MO-7004 for "
                              "a pass-through entity tax return and payment is received on or before "
                              "the extended due date, you will not be charged a penalty of 5% but will "
                              "be charged interest on the part of tax that is not paid by the original "
                              "due date."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⭐⭐ THREE SOURCES AGREE (the third is 12 CSR 10-2.436(9)): FOR MO-PTE "
                              "ONLY, an approved extension EXTENDS THE TIME TO PAY -- no 5% addition "
                              "-- but INTEREST STILL RUNS FROM THE ORIGINAL DUE DATE under 143.731.2. "
                              "That is the OPPOSITE of the general Missouri rule and of Virginia. "
                              "ENCODE IT AS A PTE-SPECIFIC BRANCH; do not share it with MO-1065 / "
                              "MO-1120S.")},
        ],
    },
]

AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    # MO_1065
    ("MO_2025_FORM_MO1065", FORM_CODE_MO1065, "governs"),
    ("MO_2025_FORM_MONRP", FORM_CODE_MO1065, "governs"),
    ("MO_2025_FORM_MOMSS", FORM_CODE_MO1065, "informs"),
    ("MO_2025_FORM_MO1NR_2NR_3NR", FORM_CODE_MO1065, "governs"),
    ("MO_RSMO_143_581_421", FORM_CODE_MO1065, "governs"),
    ("MO_RSMO_143_411_471", FORM_CODE_MO1065, "governs"),
    ("MO_RSMO_143_455", FORM_CODE_MO1065, "governs"),
    ("MO_12CSR_10_2_190_255", FORM_CODE_MO1065, "governs"),
    ("MO_RSMO_143_091", FORM_CODE_MO1065, "governs"),
    ("MO_RSMO_143_121", FORM_CODE_MO1065, "governs"),
    ("MO_2025_EXTENSION_FORMS", FORM_CODE_MO1065, "informs"),
    ("MO_DOR_EFILE_PAGES", FORM_CODE_MO1065, "informs"),
    # MO_1120S
    ("MO_2025_FORM_MO1120S", FORM_CODE_MO1120S, "governs"),
    ("MO_2025_FORM_MONRS", FORM_CODE_MO1120S, "governs"),
    ("MO_2025_FORM_MOMSS", FORM_CODE_MO1120S, "governs"),
    ("MO_2025_FORM_MO1NR_2NR_3NR", FORM_CODE_MO1120S, "governs"),
    ("MO_RSMO_143_411_471", FORM_CODE_MO1120S, "governs"),
    ("MO_RSMO_143_455", FORM_CODE_MO1120S, "governs"),
    ("MO_12CSR_10_2_190_255", FORM_CODE_MO1120S, "governs"),
    ("MO_RSMO_143_091", FORM_CODE_MO1120S, "governs"),
    ("MO_RSMO_143_121", FORM_CODE_MO1120S, "governs"),
    ("MO_2025_EXTENSION_FORMS", FORM_CODE_MO1120S, "informs"),
    ("MO_DOR_EFILE_PAGES", FORM_CODE_MO1120S, "informs"),
    # MO_PTE
    ("MO_2025_FORM_MOPTE", FORM_CODE_MOPTE, "governs"),
    ("MO_2025_PTE_INSTR", FORM_CODE_MOPTE, "governs"),
    ("MO_2025_FORM_MOMSPTE", FORM_CODE_MOPTE, "governs"),
    ("MO_2025_SCHEDULE_PTE_BD", FORM_CODE_MOPTE, "governs"),
    ("MO_RSMO_143_436", FORM_CODE_MOPTE, "governs"),
    ("MO_12CSR_10_2_436", FORM_CODE_MOPTE, "governs"),
    ("MO_RSMO_143_455", FORM_CODE_MOPTE, "governs"),
    ("MO_RSMO_143_022", FORM_CODE_MOPTE, "governs"),
    ("MO_RSMO_143_121", FORM_CODE_MOPTE, "governs"),
    ("MO_RSMO_143_091", FORM_CODE_MOPTE, "governs"),
    ("MO_2025_FORM_MOTC", FORM_CODE_MOPTE, "governs"),
    ("MO_2025_FORM_5889", FORM_CODE_MOPTE, "informs"),
    ("MO_DOR_PTE_FAQ", FORM_CODE_MOPTE, "informs"),
    ("MO_DOR_EFILE_PAGES", FORM_CODE_MOPTE, "informs"),
    ("MO_12CSR_10_2_076", FORM_CODE_MOPTE, "informs"),
    ("MO_2025_EXTENSION_FORMS", FORM_CODE_MOPTE, "governs"),
    ("MO_2025_FORM_MO1NR_2NR_3NR", FORM_CODE_MOPTE, "governs"),
    ("MO_2025_TAX_LEG_CHANGES", FORM_CODE_MOPTE, "informs"),
    # the "both returns are filed" linkage, in both directions
    ("MO_DOR_PTE_FAQ", FORM_CODE_MO1065, "informs"),
    ("MO_DOR_PTE_FAQ", FORM_CODE_MO1120S, "informs"),
    ("MO_2025_FORM_MO1065", FORM_CODE_MOPTE, "informs"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM MO_1065 -- FACTS
# ═══════════════════════════════════════════════════════════════════════════
MO1065_FACTS: list[dict] = [
    {"fact_key": "mo1065_q1_has_modifications",
     "label": "1. Does the Partnership have any Missouri modifications?",
     "data_type": "boolean", "required": True, "sort_order": 1,
     "notes": ("⚠ HALF OF THE SHORT-FORM GATE. 'If Yes, complete Lines 1-13 on pages 1 and 2, and "
               "the partner information on page 3.'")},
    {"fact_key": "mo1065_q2_has_nonresident_partners",
     "label": "2. Does the Partnership have any nonresident partners?",
     "data_type": "boolean", "required": True, "sort_order": 2,
     "notes": ("⚠ THE OTHER HALF. 'If Yes, complete Lines 1-13 ..., the partner information on page "
               "3, AND FORM MO-NRP.' ⚠ MO-1065 has NO question 3 -- there is no partnership "
               "apportionment gate and no partnership apportionment schedule (partnerships borrow "
               "MO-MSS; see the U4 section).")},
    {"fact_key": "mo1065_box_composite", "label": "Composite", "data_type": "boolean", "sort_order": 3,
     "notes": ("⭐ MO-1065 HAS a composite checkbox; MO-1120S DOES NOT, even though 143.471.5 grants "
               "S corporations the same right (N11 / U23). 'The composite return is filed on the "
               "Form MO-1040' with Form 5677 instructions, at a flat 4.7 percent -- OUT OF SCOPE, "
               "RED-DEFER R2.")},
    {"fact_key": "mo1065_box_llc_taxed_as_partnership",
     "label": "If you are a Limited Liability Company being taxed as a partnership, select this box",
     "data_type": "boolean", "sort_order": 4},
    {"fact_key": "mo1065_box_federal_extension",
     "label": "Select this box if you have an approved federal extension (attach Federal Form 7004)",
     "data_type": "boolean", "sort_order": 5,
     "notes": ("⚠ THE ONLY EXTENSION MECHANISM ON MO-1065. There is no Missouri extension form for a "
               "partnership -- MO-1065 appears on neither MO-7004's nor MO-60's face. '(Failure to "
               "check this box and provide a copy of the extension may result in disallowing the "
               "extension.)' (U24)")},
    {"fact_key": "mo1065_box_amended", "label": "Amended Return", "data_type": "boolean", "sort_order": 6},
    {"fact_key": "mo1065_box_final", "label": "Final Return", "data_type": "boolean", "sort_order": 7,
     "notes": "⚠ MO-1065 has NO Bankruptcy checkbox and NO Charter Number field; MO-1120S and MO-PTE have both."},
    {"fact_key": "mo1065_l1a_state_local_income_taxes",
     "label": "1a. State and local income taxes deducted on Federal Form 1065",
     "data_type": "decimal", "sort_order": 10,
     "notes": ("143.141(1) and (2); 12 CSR 10-2.160. ⚠ 'Include on Line 1a the income taxes (however "
               "named) of all states that were taken as a deduction... THIS MAY INCLUDE, BUT NOT BE "
               "LIMITED TO, A STATE'S ELECTIVE PASS-THROUGH ENTITY INCOME TAX.' -- ANOTHER STATE'S "
               "PTET IS AN ADDITION HERE. ⚠ " + MO_FEDERAL_LINE_STAMP)},
    {"fact_key": "mo1065_l1b_city_earnings_taxes",
     "label": "1b. Less: Kansas City & St. Louis earnings taxes. Enter Lines 1a less 1b on Line 1",
     "data_type": "decimal", "sort_order": 11,
     "notes": MO_CITY_EARNINGS_TAX_NOTE},
    {"fact_key": "mo1065_l2a_state_local_bond_interest",
     "label": "2a. State and local bond interest (except Missouri)",
     "data_type": "decimal", "sort_order": 12, "notes": "143.121.2(2)"},
    {"fact_key": "mo1065_l2b_related_expenses",
     "label": "2b. Less: related expenses (omit if less than $500). Enter Line 2a less Line 2b on Line 2",
     "data_type": "decimal", "sort_order": 13,
     "notes": ("⚠⚠ A FLOOR ON THE EXPENSE, NOT A THRESHOLD ON THE SUBTRACTION: 'The expenses must "
               "equal or exceed $500. If less than $500, enter zero.' Below $500 the EXPENSE is "
               "dropped and the GROSS survives, which makes the modification LARGER.")},
    {"fact_key": "mo1065_l3_other_additions",
     "label": "3. Partnership / Fiduciary / Other adjustments (list) -- ADDITION",
     "data_type": "decimal", "sort_order": 14,
     "notes": ("Three checkboxes plus a write-in. Sources (from the parallel MO-1120S / MO-PTE "
               "instructions): MO-1041 Page 2 Part 1 LINE 19 and MO-1065 LINE 11 (143.121.4 and .5). "
               "⚠ MO-1065's OWN Line 3 HAS NO PRINTED INSTRUCTION AT ALL. ⚠ N7: this write-in is "
               "also the only home a partnership has for the 143.121.2(6) 163(j) carryforward, which "
               "MO-1065 does not name anywhere (U7); and for the 143.121.2(4) NOL addition (U28).")},
    {"fact_key": "mo1065_l4_food_pantry",
     "label": ("4. Donations claimed for the Food Pantry Tax Credit deducted from federal taxable "
               "income, Section 135.647, RSMo"),
     "data_type": "decimal", "sort_order": 15,
     "notes": "⚠ MO-PTE HAS NO FOOD PANTRY LINE (N6). Only the two non-electing returns add it back."},
    {"fact_key": "mo1065_l6a_exempt_federal_obligations",
     "label": "6a. Interest from exempt federal obligations",
     "data_type": "decimal", "sort_order": 16,
     "notes": ("143.121.3(1); 12 CSR 10-2.150. ⚠ DOCUMENTATION RULE: 'Partnerships that claim an "
               "exclusion for interest from U.S. obligations must identify the specific securities "
               "owned (e.g., U.S. savings bond). A general description, such as \"interest on U.S. "
               "obligation\" or \"U.S. Government securities\" IS NOT ACCEPTABLE.' Mutual-fund "
               "distributions qualify only to the extent attributable to DIRECT U.S. obligations, per "
               "a year-end statement. ⚠ 'A LIST OF EXEMPT U.S. OBLIGATIONS MUST BE PROVIDED TO EACH "
               "PARTNER BY THE PARTNERSHIP.'")},
    {"fact_key": "mo1065_l6b_related_expenses",
     "label": "6b. Less: related expenses (omit if less than $500). Enter Line 6a less Line 6b on Line 6",
     "data_type": "decimal", "sort_order": 17,
     "notes": ("Same $500 FLOOR. DOR fallback ratio: 'Exempt income / Total income x Expense items = "
               "Reduction to exempt income. The principal expense item in this formula is interest "
               "expense.'")},
    {"fact_key": "mo1065_l7_state_refund",
     "label": "7. Amount of any state income tax refund included in federal ordinary income",
     "data_type": "decimal", "sort_order": 18, "notes": "143.121.3(5)"},
    {"fact_key": "mo1065_l8_other_subtractions",
     "label": "8. Partnership / Fiduciary / Other adjustments (list) -- SUBTRACTION",
     "data_type": "decimal", "sort_order": 19,
     "notes": ("The instruction names ONE write-in item: the BROADBAND GRANT subtraction -- 'you may "
               "qualify to subtract 100 percent of the grant money received', attaching Form 1099-G, "
               "the grant documents and a copy of federal Form 1065. ⚠ The RECREATIONAL MARIJUANA "
               "(280E) deduction's instruction does NOT say which line it goes on; BY ELIMINATION it "
               "is here. ⚠ This write-in is also the only home for the 143.121.3(11) 163(j) "
               "disallowed-interest subtraction (N7 / U7) and for a 143.121.3(9) disposition "
               "recovery, which MO-1065 has no line for (N9 / U19).")},
    {"fact_key": "mo1065_l9_depreciation_basis_adj",
     "label": "9. Missouri depreciation basis adjustment (Section 143.121.3(7), RSMo)",
     "data_type": "decimal", "sort_order": 20,
     "notes": ("⭐ THE ONLY DEPRECIATION LINE ON MO-1065, and its window is CLOSED: property purchased "
               "on or after July 1, 2002 but before July 1, 2003. ⚠⚠ NO POST-2003 ADJUSTMENT EXISTS "
               "-- 143.121.2(3), the ADD-BACK ITSELF, is window-limited, so 100% OBBBA bonus flows "
               "through untouched and NO Missouri 179 constant may be encoded. ⚠ MO-1065 has NO "
               "143.121.3(9) disposition-recovery line although MO-1120S has one (N9 / U19). "
               "⚠ LABEL DRIFT: MO-NRP Part 2 Line 9 renders the same line as 'Missouri depreciation "
               "adjustment (See Section 143.121, RSMo.)' -- 'basis' dropped, citation broadened.")},
    {"fact_key": "mo1065_l13_agriculture_disaster_relief",
     "label": "13. Agriculture Disaster Relief (Section 143.121.3(10), RSMo)",
     "data_type": "decimal", "sort_order": 21,
     "notes": ("⚠⚠ SITS BELOW THE NET LINES -- IT IS NOT IN LINE 10. Separately allocated to partners "
               "with its own schedule: 'Include a schedule with each partner's name, identification "
               "number, ownership percentage, and their portion of the subtraction... The amount "
               "indicated after each partner's name must be reported as a modification on his or her "
               "Form MO-1040 ... PART 1 OF THE FORM MO-A, LINE 16.' ⚠ A DIFFERENT owner-side landing "
               "line from the Line 11/12 landing at MO-A Part 1 Line 2 / Line 11. ⚠ SPELLING: this "
               "face prints `Agriculture`; MO-PTE Line 10 prints `Agricultural`.")},
    {"fact_key": "mo1065_partner_roster",
     "label": "Page 3 partner roster (19 rows a) through s) plus Total)",
     "data_type": "string", "sort_order": 30,
     "notes": ("'Name of each partner. ALL PARTNERS MUST BE LISTED. Use attachment if necessary.' "
               "Columns: 1 Name | 2 Select if partner is nonresident | 3 Social Security Number "
               "('If the partner is another company or trust, enter the federal identification "
               "number') | 4 Partner's Share % | 5 Partner's Adjustment (Addition / Subtraction). "
               "⚠ 19 ROWS -- MO-PTE Part B has 15.")},
    {"fact_key": "mo1065_partner_share_pct",
     "label": "Page 3 Column 4 - Partner's Share %",
     "data_type": "decimal", "sort_order": 31,
     "validation_rule": "rounded to WHOLE NUMBERS; the Total row should foot to 100%",
     "notes": ("⚠ 'Enter percentages from Federal Schedule K-1(s). ROUND PERCENTAGES TO WHOLE "
               "NUMBERS.' -- THREE DIFFERENT ROUNDING CONVENTIONS LIVE IN THIS LANE: whole numbers "
               "here, TWO DECIMALS on MO-PTE Part B Column 5, THREE DECIMALS on the apportionment "
               "percentage. ⚠ The DOR states NO tie-break for any of them; this build uses "
               "ROUND_HALF_UP as an engineering decision. " + MO_FEDERAL_LINE_STAMP)},
    {"fact_key": "mo1065_nrp_required",
     "label": "Form MO-NRP required (a nonresident partner AND Missouri-source income)",
     "data_type": "boolean", "sort_order": 40,
     "notes": ("ONE MO-NRP PER NONRESIDENT PARTNER. 'Omit Form MO-NRP if all partners are residents "
               "of Missouri. Use additional Forms MO-NRP if more than one nonresident partner.'")},
    {"fact_key": "mo1065_nrp_part3_direct_accounting",
     "label": "MO-NRP Part 3 direct accounting used (⚠ NOT a free preparer election -- see U4)",
     "data_type": "boolean", "default_value": "False", "sort_order": 41,
     "notes": MO_NRP_PART3_QUESTION},
    {"fact_key": "mo1065_mo_mss_factor_pct",
     "label": "MO-MSS Part 1 Line 3 receipts factor borrowed for MO-NRP Column (c)",
     "data_type": "decimal", "sort_order": 42,
     "notes": ("⭐ A PARTNERSHIP FORM DIRECTING THE PREPARER TO THE S-CORPORATION SCHEDULE, and it is "
               "DELIBERATE: 12 CSR 10-2.190(2)(C) delegates to 12 CSR 10-2.255, whose (3) puts "
               "partnership nonresident-partner sourcing on 143.455 -- IDENTICAL to S corporations. "
               "That is why NO `MO-MSP` WAS EVER PUBLISHED. It is a HIERARCHY, NOT AN ELECTION.")},
    {"fact_key": "mo1065_nr_withholding_owner_kind",
     "label": "Withholding owner entity type (individual / grantor trust 1.671-4(b) / other)",
     "data_type": "choice",
     "choices": ["individual", "grantor_trust_1671_4b", "partnership", "corporation",
                 "s_corporation", "trust", "estate"],
     "sort_order": 50,
     "notes": ("⚠ ONLY the first two are in scope. 'Do not withhold for any partners or S corporation "
               "shareholders who are partnerships, corporations, trusts, or estates. Grantor trusts "
               "that file or can file in accordance with IRC Reg. Section 1.671.4(b) ARE CONSIDERED "
               "INDIVIDUALS.'")},
    {"fact_key": "mo1065_mo3nr_on_file",
     "label": "Form MO-3NR withholding exemption on file for this owner (with effective date)",
     "data_type": "boolean", "sort_order": 51,
     "notes": ("⚠ MO-3NR IS FILED BY THE OWNER WITH THE DEPARTMENT, NOT WITH THE ENTITY, yet the "
               "entity's withholding duty turns on whether it was filed and accepted -- and the "
               "entity has NO DIRECT VISIBILITY. Model it as an OWNER ATTRIBUTE with an effective "
               "date and a revocation date, never as a return attachment. It runs 'for the tax year "
               "2025, AND ALL SUBSEQUENT TAX YEARS, until I notify the Department of a change'. ⚠ It "
               "must be filed by the due date WITHOUT REGARD TO AN EXTENSION -- a different clock "
               "from MO-1NR's.")},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM MO_1065 -- RULES
# ═══════════════════════════════════════════════════════════════════════════
MO1065_RULES: list[dict] = [
    {"rule_id": "R-MO65-SHORTFORM", "title": "The SHORT-FORM path is a filing MODE, not blank lines",
     "rule_type": "routing", "sort_order": 1,
     "inputs": ["mo1065_q1_has_modifications", "mo1065_q2_has_nonresident_partners"],
     "outputs": ["filing_mode"],
     "formula": "short_form = (NOT q1) AND (NOT q2)",
     "description": ("Verbatim: 'If you select \"No\" on both questions 1 and 2 on Form MO-1065, "
                     "attach a copy of Federal Form 1065 and all its schedules, including Schedule "
                     "K-1. Sign Form MO-1065 and mail the return.' -> A TWO-CHECKBOX, SIGNATURE-ONLY "
                     "RETURN. Lines 1-13 and Page 3 are SUPPRESSED ENTIRELY. This is a genuine "
                     "short-circuit the engine should implement as a FILING MODE."),
     "notes": ("Who must file at all (143.581): 'Form MO-1065 must be filed, if Federal Form 1065 is "
               "required to be filed and the partnership has (1) a partner that is a Missouri "
               "resident or (2) any income derived from Missouri sources.'")},
    {"rule_id": "R-MO65-500FLOOR", "title": "The $500 related-expense FLOOR (2a/2b and 6a/6b)",
     "rule_type": "calculation", "sort_order": 2,
     "inputs": ["mo1065_l2a_state_local_bond_interest", "mo1065_l2b_related_expenses",
                "mo1065_l6a_exempt_federal_obligations", "mo1065_l6b_related_expenses"],
     "outputs": ["MO1065_L2", "MO1065_L6"],
     "formula": "net = gross - (expense if expense >= 500 else 0)",
     "description": ("⚠⚠ A FLOOR ON THE EXPENSE, NOT A THRESHOLD ON THE SUBTRACTION. 'The expenses "
                     "must equal or exceed $500. If less than $500, enter zero.' Below $500 the "
                     "EXPENSE IS DROPPED and the GROSS amount survives, which makes the modification "
                     "LARGER, not smaller. Getting this backwards is one of the seven most likely "
                     "Missouri build errors."),
     "exceptions": ("When the expense is not separately known the DOR supplies a fallback ratio: "
                    "'Exempt income / Total income x Expense items = Reduction to exempt income. The "
                    "principal expense item in this formula is interest expense.'")},
    {"rule_id": "R-MO65-ADJ", "title": "Lines 5, 10, 11 and 12 - the partnership adjustment",
     "rule_type": "calculation", "sort_order": 3,
     "inputs": ["MO1065_L1", "MO1065_L2", "mo1065_l3_other_additions", "mo1065_l4_food_pantry",
                "MO1065_L6", "mo1065_l7_state_refund", "mo1065_l8_other_subtractions",
                "mo1065_l9_depreciation_basis_adj"],
     "outputs": ["MO1065_L5", "MO1065_L10", "MO1065_L11", "MO1065_L12"],
     "formula": ("L5 = L1+L2+L3+L4; L10 = L6+L7+L8+L9; L11 = max(0, L5-L10); L12 = max(0, L10-L5)"),
     "description": ("L11 is the NET ADDITION and L12 the NET SUBTRACTION; they are mutually "
                     "exclusive by construction. Both feed Page 3 Column 5 and, for an electing "
                     "entity, MO-PTE Part A Line 3 / Line 9."),
     "notes": ("⚠ LINE 13 IS NOT IN THIS CHAIN. Agriculture Disaster Relief sits BELOW the net lines "
               "and is separately allocated -- see R-MO65-L13.")},
    {"rule_id": "R-MO65-L13", "title": "Line 13 sits OUTSIDE the totals and lands on a DIFFERENT line",
     "rule_type": "calculation", "sort_order": 4,
     "inputs": ["mo1065_l13_agriculture_disaster_relief"], "outputs": ["MO1065_L13"],
     "formula": "L13 is reported and allocated separately; it is NOT included in L10, L11 or L12",
     "description": ("⚠ SAME STATUTE, THREE PLACEMENTS, TWO BEHAVIOURS. On MO-1065 (Line 13) and "
                     "MO-1120S (Line 15) Agriculture Disaster Relief sits BELOW the net-adjustment "
                     "lines and is separately allocated to owners with its own schedule, landing on "
                     "MO-A Part 1 LINE 16. On MO-PTE (Line 10) it is INSIDE the Line 12 subtraction "
                     "total and reduces the entity's tax base directly. ⚠ And the DOR spells it TWO "
                     "WAYS: `Agriculture` here and on MO-1120S L15, `Agricultural` on MO-PTE L10."),
     "notes": "Attach a Form 1099 indicating the agricultural payment."},
    {"rule_id": "R-MO65-PG3", "title": "Page 3 allocation grid - 19 rows, WHOLE-NUMBER percentages",
     "rule_type": "calculation", "sort_order": 5,
     "inputs": ["mo1065_partner_share_pct", "MO1065_L11", "MO1065_L12"],
     "outputs": ["MO1065_PG3_COL5"],
     "formula": "Col 5 (per partner) = Col 4 x (L11 or L12 on the Total line)",
     "description": ("Verbatim: 'Enter Missouri Partnership adjustment from the Partnership "
                     "Adjustment section, Line 11 or Line 12 on the Total line. Enter each partner's "
                     "allocated portion on their respective line by multiplying the percentage in "
                     "Column 4 by the Total line in Column 5. Indicate at the top of Column 5 whether "
                     "the adjustments are either additions or subtractions.' Owner-side landing: "
                     "'...must be reported as a modification on his or her Form MO-1040 ... Part 1 of "
                     "the Form MO-A AS A PARTNERSHIP ADDITION ON LINE 2 OR SUBTRACTION ON LINE 11.'"),
     "exceptions": ("⚠ THE ANTI-704(b) GUARD: 'Attach a detailed explanation (including extracts from "
                    "the partnership agreement) if the Column 5 amounts are not based upon the same "
                    "single percentage allocation indicated on Federal Form 1065, Schedule K-1. The "
                    "explanation must include the non-tax purposes and effects of the special "
                    "allocation method.' Cf. 143.411.3. RED-DEFER R14."),
     "notes": "⚠ WHOLE NUMBERS here; MO-PTE Part B Column 5 rounds to TWO DECIMALS."},
    {"rule_id": "R-MO65-DEPR-NEG", "title": "VERIFIED NEGATIVE - no bonus add-back, no state 179",
     "rule_type": "validation", "sort_order": 6,
     "inputs": ["mo1065_l9_depreciation_basis_adj"], "outputs": ["depreciation_modification"],
     "formula": ("modification applies IFF the property was purchased on or after 2002-07-01 and "
                 "before 2003-07-01; otherwise ZERO, and no state 179 figure exists"),
     "description": ("⚠⚠ CLOSED AT THE STATUTE, NOT AT THE FORM FACES. 143.121.2(3) -- the IRC 168 "
                     "ADD-BACK ITSELF -- is window-limited on its face to property purchased 'on or "
                     "after July 1, 2002, but before July 1, 2003' and is measured against IRC 168 "
                     "'as amended by the Job Creation and Worker Assistance Act of 2002'. "
                     "143.121.3(7) carries the identical window and 143.121.3(9) inherits it by "
                     "cross-reference. 143.121 contains NO IRC 179 modification at all. THERE IS NO "
                     "OPEN-ENDED BONUS ADD-BACK IN MISSOURI LAW TO FIND. 100% OBBBA bonus flows "
                     "through untouched; there is NO Missouri shadow depreciation book and NO "
                     "Missouri 179 constant."),
     "exceptions": ("⚠ DO NOT PORT VIRGINIA'S DERIVED STATE 179 FIGURE and DO NOT create a nullable "
                    "'state depreciation adjustment' field for symmetry with other states -- a "
                    "nullable field a preparer can fill is worse than no field. RED-DEFER R5 covers "
                    "the live 2002-03 residual."),
     "notes": ("⚠ MO-1065 has the .3(7) basis line but NO .3(9) disposition-recovery line, while "
               "MO-1120S has both (N9 / U19). A partnership disposing of 2002-03 vintage property "
               "must use the Line 8 write-in.")},
    {"rule_id": "R-MO65-CONFORM", "title": "ROLLING conformity - there is NOTHING to adjust",
     "rule_type": "classification", "sort_order": 7,
     "inputs": [], "outputs": ["conformity_posture"],
     "formula": "MO_CONFORMITY_TYPE == 'rolling'; no conformity line exists on any PTE-lane return",
     "description": ("143.091 (eff. 1/1/1990, UNAMENDED): federal references mean the IRC 'as the "
                     "same may be or become effective, at any time or from time to time, FOR THE "
                     "TAXABLE YEAR.' OBBBA therefore applies for TY2025 with NO adoption act -- none "
                     "was needed and none was enacted. DO NOT BUILD A CONFORMITY BUCKET (N3)."),
     "notes": ("⚠ THE COST OF ROLLING CONFORMITY: a future federal expensing change flows in "
               "AUTOMATICALLY AND SILENTLY, with no Missouri line that would surface it. A TY-rollover "
               "pass must re-read 143.121.2 and .3 IN FULL for newly inserted subdivisions, not "
               "merely re-read the forms.")},
    {"rule_id": "R-MO65-BOTH", "title": "⚠⚠ MO-PTE is filed IN ADDITION TO MO-1065, not instead of it",
     "rule_type": "routing", "sort_order": 8,
     "inputs": ["pte_election_made"], "outputs": ["required_returns"],
     "formula": "election -> file MO_1065 AND MO_PTE (never MO_PTE alone)",
     "description": ("PUBLISHED DOR AUTHORITY, verbatim: 'Yes. The filing of the MO-PTE does not "
                     "substitute for a partnership filing its MO-1065 or an S corporation filing its "
                     "MO-1120S.' Corroborated structurally: MO-PTE Part A Lines 3 and 9 both draw "
                     "from 'Form MO-1065, Line 11 [Line 12]', with copies required as attachments; "
                     "and 143.581 imposes the partnership filing duty without regard to a 143.436 "
                     "election. ⚠⚠ THIS IS THE OPPOSITE OF VIRGINIA, where Form 502PTET is filed "
                     "INSTEAD OF Form 502. PORTING THAT PATTERN WOULD LEAVE EVERY ELECTING MISSOURI "
                     "CLIENT'S FILING INCOMPLETE."),
     "notes": "Campaign D-12; brief 22.3 correction #4 promoted this from inference to authority."},
    {"rule_id": "R-MO65-SOURCE", "title": "Partnership Missouri sourcing runs on 143.455 (the U4 answer)",
     "rule_type": "classification", "sort_order": 9,
     "inputs": ["mo1065_mo_mss_factor_pct", "mo1065_nrp_part3_direct_accounting"],
     "outputs": ["missouri_source_percentage"],
     "formula": ("MO-NRP Column (c) = MO-MSS Part 1 Line 3 (the 143.455 receipts factor) unless "
                 "MO-NRP Part 3 direct accounting applies"),
     "description": ("12 CSR 10-2.190(2)(C) DELEGATES to 12 CSR 10-2.255, whose (3) provides that for "
                     "tax years beginning on or after 1/1/2020 a nonresident partner's Missouri-source "
                     "items are those the partnership 'would include in its Missouri Apportioned "
                     "Income by applying the provisions of section 143.455' or 'in its Missouri "
                     "Allocated Income by applying the provisions of section 143.455'. (2) is the "
                     "word-for-word S-corporation twin and (4) supplies the entity-type bridge. "
                     "⭐ SO THE MO-NRP -> MO-MSS CROSS-REFERENCE IS DELIBERATE, NOT AN EDITORIAL SLIP, "
                     "AND IT IS A HIERARCHY, NOT AN ELECTION -- which is why no MO-MSP was ever "
                     "published. ⚠ 143.581's 143.181 reference is a RETURN-FILING TRIGGER, not a "
                     "computation method (143.421.1 delegates the method to the director's "
                     "regulations). This CORRECTS the source brief's 2.2."),
     "exceptions": MO_NRP_PART3_QUESTION,
     "notes": MO_NO_143_181_REGULATION},
    {"rule_id": "R-MO65-WH", "title": "Nonresident withholding at 4.7% - and the election does NOT stop it",
     "rule_type": "calculation", "sort_order": 10,
     "inputs": ["mo1065_nr_withholding_owner_kind", "mo1065_mo3nr_on_file", "pte_election_made"],
     "outputs": ["MO_2NR_L2", "MO_1NR_L2"],
     "formula": "MO-2NR L2 = 4.7% x MO-2NR L1; MO-1NR L1 = count(MO-2NR); MO-1NR L2 = sum(MO-2NR L2)",
     "description": ("Rate verbatim: 'The amount of tax to be withheld for tax year 2025 is 4.70 "
                     "percent (0.047) ..., or the tax withheld may be determined based on Missouri "
                     "withholding tables if the partner or shareholder submits a Missouri Withholding "
                     "Allowance Certification (Form MO W-4).' ⚠⚠ 12 CSR 10-2.436(8): 'The election to "
                     "become an affected business entity DOES NOT RELIEVE a partnership or S "
                     "corporation of its withholding obligations under section 143.411.5, RSMo, or "
                     "section 143.471.6, RSMo, respectively.' AN ELECTING MISSOURI PARTNERSHIP PAYS "
                     "4.7% ENTITY TAX **AND** WITHHOLDS 4.7% ON THE SAME INCOME. It is stated ONLY in "
                     "the regulation."),
     "exceptions": MO_WH_EXCEPTIONS_RULING_NOTE,
     "notes": ("⚠ A ZERO-DOLLAR MO-2NR IS STILL REQUIRED: 'Issue Form MO-2NR, even if no tax is "
               "withheld or there is an exemption certificate on file.' But NOT for an owner on a "
               "composite return. " + MO_1NR_SEQUENCING_RULE)},
    {"rule_id": "R-MO65-WHBASE", "title": "⚠ The MO-NRP withholding base is DEFECTIVE as printed (U9)",
     "rule_type": "calculation", "sort_order": 11,
     "inputs": ["mo1065_nrp_required"], "outputs": ["MO_2NR_L1"],
     "formula": ("base = sum(MO-NRP Part 1 Column (e) lines 1, 2, 3c, 4a, 5, 10, 11) -- the DOR's "
                 "'Lines 1 through 11' over a NON-CONTIGUOUS line set"),
     "description": ("MO-NRP Part 1's printed line set is `1, 2, 3c, 4a, 5, 10, 11, 12, 13, 13e`, so "
                     "'Lines 1 through 11' SILENTLY EXCLUDES Line 12 (IRC 179), Line 13 "
                     "(contributions) and Line 13e (other deductions). Whether that exclusion is "
                     "deliberate (a gross-ish base) or an accident of the DOR's own numbering is NOT "
                     "STATED. ⚠ MO-NRP Line 5 is itself a ROLL-UP of federal Schedule K Lines 5-9a, "
                     "so it already contains interest, dividends, royalties and capital gains -- "
                     "build it as a SUMMATION WORKSHEET, not a copy. THIS DETERMINES CASH WITHHELD."),
     "notes": ("requires_human_review whenever any excluded line is non-zero. Get a DOR worked "
               "example before season. " + MO_FEDERAL_LINE_STAMP)},
    {"rule_id": "R-MO65-DUE", "title": "Due date and extension - federal Form 7004 only",
     "rule_type": "conditional", "sort_order": 12,
     "inputs": ["mo1065_box_federal_extension"], "outputs": ["due_date"],
     "formula": "the 15th day of the 4th month following the close of the taxable year",
     "description": ("'For partnerships operating on a calendar year basis, the partnership return is "
                     "due on or before APRIL 15, 2026.' Weekend/holiday rollover to the next business "
                     "day. ⚠ MO-1065 appears on NEITHER MO-7004's NOR MO-60's face: the only "
                     "extension mechanism is the checkbox plus an attached federal Form 7004. "
                     "⚠ MO-1NR / MO-2NR follow the EXTENDED date; MO-3NR does NOT (U24)."),
     "notes": "⚠ The MO-PTE payment-extension branch does NOT apply here. Do not share it."},
    {"rule_id": "R-MO65-SIGN", "title": "Signature, notification and the composite carve-out",
     "rule_type": "validation", "sort_order": 13,
     "inputs": ["mo1065_box_composite"], "outputs": ["signature_requirements"],
     "formula": "any partner may sign; a per-partner extract must be furnished",
     "description": ("'Form MO-1065 ... must be signed by one of the partners of the partnership or "
                     "one of the members of the joint venture or other enterprise. ANY MEMBER OR "
                     "PARTNER, REGARDLESS OF POSITION, MAY SIGN THE RETURN.' (Contrast MO-1120S, "
                     "which requires AN OFFICER.) Duty to notify: 'notify each partner of the "
                     "adjustment to which he or she is entitled'; 'A copy of this part (or its "
                     "information) must be provided to each partner.' ⚠ MO-1065 has NO REDACTION "
                     "sentence -- MO-1120S does. ⚠ CREDITS: 'Partners may be entitled to tax credits. "
                     "These credits must be allocated to the partners' percentage of ownership and "
                     "reported on the Form MO-1040.' -- MO-1065 DOES NOT COMPUTE OR CARRY CREDITS."),
     "notes": ("The composite return is filed on FORM MO-1040 under 12 CSR 10-2.190 with Form 5677 "
               "instructions, at a flat 4.7%. OUT OF SCOPE -- RED-DEFER R2, and suppress MO-2NR for "
               "every owner on the composite.")},
]

MO1065_RULE_LINKS: list[tuple] = [
    ("R-MO65-SHORTFORM", "MO_2025_FORM_MO1065", "primary", "the two gating questions and the short-form sentence"),
    ("R-MO65-SHORTFORM", "MO_RSMO_143_581_421", "primary", "143.581 - who must file"),
    ("R-MO65-500FLOOR", "MO_2025_FORM_MO1065", "primary", "the 2b and 6b sub-line labels as printed"),
    ("R-MO65-ADJ", "MO_2025_FORM_MO1065", "primary", "Lines 1-12 as printed"),
    ("R-MO65-ADJ", "MO_RSMO_143_121", "primary", "the modifications statute behind every line"),
    ("R-MO65-L13", "MO_2025_FORM_MO1065", "primary", "Line 13 printed BELOW the net lines"),
    ("R-MO65-L13", "MO_RSMO_143_121", "primary", "143.121.3(10)"),
    ("R-MO65-PG3", "MO_2025_FORM_MO1065", "primary", "the Page 3 grid and its Column 5 instruction"),
    ("R-MO65-PG3", "MO_RSMO_143_411_471", "secondary", "143.411.3 - the anti-avoidance allocation rule"),
    ("R-MO65-DEPR-NEG", "MO_RSMO_143_121", "primary", "143.121.2(3) - the ADD-BACK ITSELF is window-limited"),
    ("R-MO65-DEPR-NEG", "MO_2025_FORM_MO1120S", "implementation", "the only document spelling the window out in words"),
    ("R-MO65-CONFORM", "MO_RSMO_143_091", "primary", "the ROLLING conformity anchor"),
    ("R-MO65-BOTH", "MO_DOR_PTE_FAQ", "primary", "published DOR authority that both returns are filed"),
    ("R-MO65-BOTH", "MO_RSMO_143_581_421", "primary", "143.581 imposes the duty regardless of the election"),
    ("R-MO65-BOTH", "MO_2025_FORM_MOPTE", "secondary", "MO-PTE Part A Lines 3/9 draw off a filed MO-1065"),
    ("R-MO65-SOURCE", "MO_12CSR_10_2_190_255", "primary", "the delegation chain that answers U4"),
    ("R-MO65-SOURCE", "MO_RSMO_143_455", "primary", "the sourcing statute both entity types run"),
    ("R-MO65-SOURCE", "MO_RSMO_143_581_421", "primary", "143.421.1 delegates; .4 needs an application"),
    ("R-MO65-SOURCE", "MO_2025_FORM_MONRP", "implementation", "MO-NRP Part 3 and the MO-MSS fallback"),
    ("R-MO65-WH", "MO_2025_FORM_MO1NR_2NR_3NR", "primary", "the 4.70 percent rate, verbatim"),
    ("R-MO65-WH", "MO_12CSR_10_2_436", "primary", "(8) - the election does NOT relieve withholding"),
    ("R-MO65-WH", "MO_RSMO_143_411_471", "primary", "143.411.5 - the five exceptions"),
    ("R-MO65-WHBASE", "MO_2025_FORM_MO1NR_2NR_3NR", "primary", "the defective base definition"),
    ("R-MO65-WHBASE", "MO_2025_FORM_MONRP", "primary", "the non-contiguous Part 1 line set"),
    ("R-MO65-DUE", "MO_2025_FORM_MO1065", "primary", "April 15, 2026 stated in the embedded instructions"),
    ("R-MO65-DUE", "MO_2025_EXTENSION_FORMS", "secondary", "MO-1065 appears on neither extension form"),
    ("R-MO65-SIGN", "MO_2025_FORM_MO1065", "primary", "the signature, notification and credit sentences"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM MO_1065 -- LINES
# ═══════════════════════════════════════════════════════════════════════════
MO1065_LINES: list[dict] = [
    {"line_number": "Q1", "line_type": "input", "sort_order": 1,
     "description": "1. Does the Partnership have any Missouri modifications?",
     "source_facts": ["mo1065_q1_has_modifications"], "source_rules": ["R-MO65-SHORTFORM"]},
    {"line_number": "Q2", "line_type": "input", "sort_order": 2,
     "description": "2. Does the Partnership have any nonresident partners?",
     "source_facts": ["mo1065_q2_has_nonresident_partners"], "source_rules": ["R-MO65-SHORTFORM"],
     "notes": "⚠ There is NO question 3 on MO-1065 -- no partnership apportionment gate exists."},
    {"line_number": "1a", "line_type": "input", "sort_order": 3,
     "description": "State and local income taxes deducted on Federal Form 1065",
     "source_facts": ["mo1065_l1a_state_local_income_taxes"], "source_rules": ["R-MO65-ADJ"],
     "notes": "⚠ Another state's elective PTET is an addition here. " + MO_FEDERAL_LINE_STAMP},
    {"line_number": "1b", "line_type": "input", "sort_order": 4,
     "description": "Less: Kansas City & St. Louis earnings taxes. Enter Lines 1a less 1b on Line 1",
     "source_facts": ["mo1065_l1b_city_earnings_taxes"], "source_rules": ["R-MO65-ADJ"],
     "notes": MO_CITY_EARNINGS_TAX_NOTE},
    {"line_number": "1", "line_type": "calculated", "sort_order": 5,
     "description": "Net state and local income taxes (1a minus 1b)",
     "calculation": "1a - 1b", "source_rules": ["R-MO65-ADJ"]},
    {"line_number": "2a", "line_type": "input", "sort_order": 6,
     "description": "State and local bond interest (except Missouri)",
     "source_facts": ["mo1065_l2a_state_local_bond_interest"], "source_rules": ["R-MO65-500FLOOR"]},
    {"line_number": "2b", "line_type": "input", "sort_order": 7,
     "description": "Less: related expenses (omit if less than $500). Enter Line 2a less Line 2b on Line 2",
     "source_facts": ["mo1065_l2b_related_expenses"], "source_rules": ["R-MO65-500FLOOR"],
     "notes": "⚠ A FLOOR ON THE EXPENSE, not a threshold on the subtraction."},
    {"line_number": "2", "line_type": "calculated", "sort_order": 8,
     "description": "Net state and local bond interest (2a minus 2b, expense floored at $500)",
     "calculation": "2a - (2b if 2b >= 500 else 0)", "source_rules": ["R-MO65-500FLOOR"]},
    {"line_number": "3", "line_type": "input", "sort_order": 9,
     "description": "Partnership / Fiduciary / Other adjustments (list ____) -- ADDITION",
     "source_facts": ["mo1065_l3_other_additions"], "source_rules": ["R-MO65-ADJ"],
     "notes": ("⚠ MO-1065's own Line 3 has NO printed instruction. It is also the only home a "
               "partnership has for the 163(j) carryforward (N7/U7) and the 143.121.2(4) NOL "
               "addition (U28).")},
    {"line_number": "4", "line_type": "input", "sort_order": 10,
     "description": ("Donations claimed for the Food Pantry Tax Credit deducted from federal taxable "
                     "income, Section 135.647, RSMo"),
     "source_facts": ["mo1065_l4_food_pantry"], "source_rules": ["R-MO65-ADJ"],
     "notes": "⚠ MO-PTE has NO Food Pantry line (N6)."},
    {"line_number": "5", "line_type": "subtotal", "sort_order": 11,
     "description": "Total of Lines 1 through 4", "calculation": "1 + 2 + 3 + 4",
     "source_rules": ["R-MO65-ADJ"]},
    {"line_number": "6a", "line_type": "input", "sort_order": 12,
     "description": "Interest from exempt federal obligations",
     "source_facts": ["mo1065_l6a_exempt_federal_obligations"], "source_rules": ["R-MO65-500FLOOR"],
     "notes": ("⚠ 'A general description, such as \"interest on U.S. obligation\" or \"U.S. "
               "Government securities\" is not acceptable.' A list of exempt U.S. obligations must be "
               "provided to EACH PARTNER.")},
    {"line_number": "6b", "line_type": "input", "sort_order": 13,
     "description": "Less: related expenses (omit if less than $500). Enter Line 6a less Line 6b on Line 6",
     "source_facts": ["mo1065_l6b_related_expenses"], "source_rules": ["R-MO65-500FLOOR"]},
    {"line_number": "6", "line_type": "calculated", "sort_order": 14,
     "description": "Net interest from exempt federal obligations (6a minus 6b, expense floored)",
     "calculation": "6a - (6b if 6b >= 500 else 0)", "source_rules": ["R-MO65-500FLOOR"]},
    {"line_number": "7", "line_type": "input", "sort_order": 15,
     "description": "Amount of any state income tax refund included in federal ordinary income",
     "source_facts": ["mo1065_l7_state_refund"], "source_rules": ["R-MO65-ADJ"]},
    {"line_number": "8", "line_type": "input", "sort_order": 16,
     "description": "Partnership / Fiduciary / Other adjustments (list ____) -- SUBTRACTION",
     "source_facts": ["mo1065_l8_other_subtractions"], "source_rules": ["R-MO65-ADJ"],
     "notes": ("Broadband Grant is the ONLY named write-in. The 280E marijuana deduction lands here "
               "BY ELIMINATION -- the instruction does not say which line. Also the only home for a "
               "143.121.3(9) disposition recovery (N9/U19) and the 163(j) disallowed-interest "
               "subtraction (N7/U7).")},
    {"line_number": "9", "line_type": "input", "sort_order": 17,
     "description": "Missouri depreciation basis adjustment (Section 143.121.3(7), RSMo)",
     "source_facts": ["mo1065_l9_depreciation_basis_adj"], "source_rules": ["R-MO65-DEPR-NEG"],
     "notes": ("⭐ THE ONLY DEPRECIATION LINE ON MO-1065 and its window is CLOSED (2002-07-01 to "
               "2003-06-30). NO post-2003 adjustment exists. RED-DEFER R5.")},
    {"line_number": "10", "line_type": "subtotal", "sort_order": 18,
     "description": "Total Subtractions - Add Lines 6 through 9", "calculation": "6 + 7 + 8 + 9",
     "source_rules": ["R-MO65-ADJ"]},
    {"line_number": "11", "line_type": "total", "sort_order": 19,
     "description": "Missouri Partnership adjustment - Net Addition - excess Line 5 over Line 10",
     "calculation": "max(0, 5 - 10)", "source_rules": ["R-MO65-ADJ"],
     "destination_form": "MO_PTE Part A Line 3; MO-1120S Line 3; MO-1065 Page 3 Column 5",
     "notes": "⚠ Feeds an ELECTING entity's MO-PTE Part A Line 3 -- proof both returns are filed."},
    {"line_number": "12", "line_type": "total", "sort_order": 20,
     "description": "Missouri Partnership adjustment - Net Subtraction - excess Line 10 over Line 5",
     "calculation": "max(0, 10 - 5)", "source_rules": ["R-MO65-ADJ"],
     "destination_form": "MO_PTE Part A Line 9; MO-1120S Line 9; MO-1065 Page 3 Column 5"},
    {"line_number": "13", "line_type": "informational", "sort_order": 21,
     "description": "Agriculture Disaster Relief (Section 143.121.3(10), RSMo)",
     "source_facts": ["mo1065_l13_agriculture_disaster_relief"], "source_rules": ["R-MO65-L13"],
     "destination_form": "MO-A Part 1 LINE 16 (a DIFFERENT line from the Line 11/12 landing)",
     "notes": ("⚠ OUTSIDE the Line 10 total. ⚠ SPELLING: this face prints `Agriculture`; MO-PTE Line "
               "10 prints `Agricultural`.")},
    {"line_number": "PG3-C1", "line_type": "input", "sort_order": 30,
     "description": "Page 3 Column 1 - Name of each partner. All partners must be listed.",
     "source_facts": ["mo1065_partner_roster"], "source_rules": ["R-MO65-PG3"]},
    {"line_number": "PG3-C2", "line_type": "input", "sort_order": 31,
     "description": "Page 3 Column 2 - Select if partner is nonresident",
     "source_rules": ["R-MO65-PG3", "R-MO65-WH"]},
    {"line_number": "PG3-C3", "line_type": "input", "sort_order": 32,
     "description": ("Page 3 Column 3 - Social Security Number (federal identification number if the "
                     "partner is another company or trust)"),
     "source_rules": ["R-MO65-PG3"]},
    {"line_number": "PG3-C4", "line_type": "input", "sort_order": 33,
     "description": "Page 3 Column 4 - Partner's Share % (rounded to WHOLE NUMBERS)",
     "source_facts": ["mo1065_partner_share_pct"], "source_rules": ["R-MO65-PG3"],
     "notes": "⚠ WHOLE NUMBERS. MO-PTE Part B Column 5 uses TWO DECIMALS."},
    {"line_number": "PG3-C5", "line_type": "calculated", "sort_order": 34,
     "description": "Page 3 Column 5 - Partner's Adjustment (Addition / Subtraction)",
     "calculation": "Column 4 x (Line 11 or Line 12 on the Total line)",
     "source_rules": ["R-MO65-PG3"],
     "destination_form": "MO-A Part 1 Line 2 (addition) or Line 11 (subtraction); MO-NRP Part 2 Column (d)"},
    {"line_number": "NRP-P1-C", "line_type": "calculated", "sort_order": 40,
     "description": "MO-NRP Part 1 Column (c) - MO % ",
     "calculation": "(c) = (b) / (a)   ⚠ THE REVERSE of MO-NRS's (b) = (a) x (c)",
     "source_rules": ["R-MO65-SOURCE"],
     "notes": ("DOR worked example: (a) $20,000, (b) $16,000, (c) 80%, (d) $12,000, (e) $9,600. "
               "'Attach a detailed explanation if any other method is used.'")},
    {"line_number": "NRP-P1-E", "line_type": "calculated", "sort_order": 41,
     "description": "MO-NRP Part 1 Column (e) - the partner's Missouri-source share",
     "calculation": "(e) = (d) x (c)", "source_rules": ["R-MO65-SOURCE"],
     "destination_form": "Form MO-NRI (Missouri Income Percentage)"},
    {"line_number": "NRP-P1-5", "line_type": "calculated", "sort_order": 42,
     "description": ("MO-NRP Part 1 Line 5 - Total portfolio income (loss), total of Federal Form "
                     "1065 Schedules K and K-1, Lines 5-9a"),
     "calculation": "a SUMMATION WORKSHEET over federal Schedule K Lines 5 through 9a",
     "source_rules": ["R-MO65-WHBASE"],
     "notes": ("⚠ A ROLL-UP, NOT A COPY -- it already contains interest, dividends, royalties and "
               "capital gains. IRC 1231 is broken out separately at Line 10. " + MO_FEDERAL_LINE_STAMP)},
    {"line_number": "NRP-P1-12", "line_type": "input", "sort_order": 43,
     "description": "MO-NRP Part 1 Line 12 - Section 179 deduction (attach schedule)",
     "source_rules": ["R-MO65-DEPR-NEG"],
     "notes": ("⭐ IRC 179 APPEARS HERE AS A DISTRIBUTIVE SHARE ITEM, NEVER AS A MISSOURI "
               "MODIFICATION -- one of three such appearances in the lane and part of the proof that "
               "no Missouri 179 figure exists. ⚠ EXCLUDED from the withholding base by the DOR's "
               "'Lines 1 through 11' (U9).")},
    {"line_number": "NRP-P3-13", "line_type": "calculated", "sort_order": 44,
     "description": "MO-NRP Part 3 Line 13 - Missouri sources (subtract Line 11 from Line 8, Column (b))",
     "calculation": "Column (b): Line 8 - Line 11",
     "source_rules": ["R-MO65-SOURCE"],
     "notes": ("⚠⚠ THE DIRECT-ACCOUNTING ENGINE, AND ITS REGULATORY BASIS IS THE NARROWED U4 -- A "
               "GATE-1 SEED QUESTION, NOT A FREE PREPARER ELECTION. ⚠ Lines 12 and 13 both read "
               "'subtract Line 11 from Line 8'; the difference is that Line 12 works COLUMN (a) "
               "(everywhere) and Line 13 COLUMN (b) (Missouri). Printed footnote: 'Line 12 may not "
               "equal other lines in initial years of partnership due to organizational costs.'")},
    {"line_number": "NR-1NR-2", "line_type": "total", "sort_order": 50,
     "description": "Form MO-1NR Line 2 - Total Missouri income tax withheld (total of all MO-2NRs)",
     "calculation": "sum of Form MO-2NR Line 2 across all in-scope owners",
     "source_rules": ["R-MO65-WH", "R-MO65-WHBASE"]},
    {"line_number": "NR-2NR-2", "line_type": "calculated", "sort_order": 51,
     "description": "Form MO-2NR Line 2 - Missouri Income Tax Payment",
     "calculation": "4.7% (0.047) x Line 1, or per the Missouri withholding tables if a Form MO W-4 is on file",
     "source_rules": ["R-MO65-WH"],
     "destination_form": "MO-1040 LINE 39 (the nonresident owner claims the payment)",
     "notes": "⚠ ISSUE A MO-2NR EVEN IF ZERO -- but not for an owner on a composite return."},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM MO_1065 -- DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════════════════
MO1065_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_MO65_SHORT_FORM", "severity": "info",
     "title": "Both gating questions are No - this is the signature-only short-form return",
     "condition": "question 1 is No AND question 2 is No",
     "message": ("'If you select \"No\" on both questions 1 and 2 on Form MO-1065, attach a copy of "
                 "Federal Form 1065 and all its schedules, including Schedule K-1. Sign Form MO-1065 "
                 "and mail the return.' Lines 1-13 and the Page 3 partner grid are suppressed "
                 "entirely."),
     "notes": "Implement as a FILING MODE, not as a set of blank lines."},
    {"diagnostic_id": "D_MO65_NRP_REQUIRED", "severity": "warning",
     "title": "Form MO-NRP is required - ONE PER NONRESIDENT PARTNER",
     "condition": "question 2 is Yes AND the partnership has Missouri-source income",
     "message": ("'Omit Form MO-NRP if all partners are residents of Missouri. USE ADDITIONAL FORMS "
                 "MO-NRP IF MORE THAN ONE NONRESIDENT PARTNER.' Each nonresident partner also needs a "
                 "copy: 'Form MO-NRP must be completed and a copy (or its information) supplied to "
                 "the nonresident partner.'")},
    {"diagnostic_id": "D_MO65_NRP_PART3_BASIS", "severity": "warning",
     "title": "⚠ MO-NRP Part 3 direct accounting has NO regulatory branch - a Gate-1 question",
     "condition": "MO-NRP Part 3 direct accounting is selected",
     "message": ("12 CSR 10-2.255 is a CLOSED TWO-BRANCH test -- Missouri Apportioned Income or "
                 "Missouri Allocated Income, BOTH under section 143.455 -- and it contains NO "
                 "separate-accounting branch at all. Yet Form MO-NRP Part 3 prints one and offers it "
                 "whenever 'accompanying records clearly reflect income from Missouri sources'. The "
                 "only statutory room is section 143.421.4, which lets the director authorize other "
                 "methods only 'ON APPLICATION', and nothing on the form, in its embedded "
                 "instructions, or in either regulation mentions an application, a petition or an "
                 "approval. DO NOT TREAT PART 3 AS A FREE PREPARER ELECTION. Confirm with the "
                 "Department (corporate@dor.mo.gov / (573) 751-4541) before relying on it."),
     "notes": ("The narrowed U4. Campaign D-12 C3 as re-scoped by the U4 follow-up of 2026-08-19. "
               "Two readings survive: a STANDING pre-approved 143.421.4 alternative method (the form "
               "itself being the grant), or PRE-2020 FORM FURNITURE that 12 CSR 10-2.255 superseded "
               "on 2021-03-30 and the form was never conformed to. The sources do not say.")},
    {"diagnostic_id": "D_MO_NRP_MSPTE_DELTA", "severity": "warning",
     "title": "⚠ MO-NRP and MO-MS PTE sourcing disagree - this now reads as a PROBABLE ERROR",
     "condition": "the MO-NRP Column (c) percentage differs from the MO-MS PTE percentage",
     "message": ("These two percentages should AGREE. 12 CSR 10-2.190(2)(C) delegates to 12 CSR "
                 "10-2.255, whose subsection (3) puts a partnership's nonresident-partner sourcing on "
                 "section 143.455 -- THE SAME STATUTE Form MO-MS PTE runs on -- for all tax years "
                 "beginning on or after January 1, 2020. A non-zero difference indicates a "
                 "computational error, or reliance on the MO-NRP Part 3 direct-accounting path whose "
                 "regulatory basis is unconfirmed. Review both computations before filing."),
     "notes": ("⚠⚠ THIS DIAGNOSTIC'S MEANING FLIPPED ON 2026-08-19. Before the U4 follow-up the "
               "divergence was EXPECTED-NONZERO (a genuine 143.181-vs-143.455 regime disagreement); "
               "after it, the divergence is EXPECTED-ZERO and a delta is a PROBABLE ERROR. Campaign "
               "D-12 C3 as re-scoped by brief 22.11, which GOVERNS. The MO-NRP -> MO-MSS "
               "cross-reference is DELIBERATE, and it is a HIERARCHY, not an election.")},
    {"diagnostic_id": "D_MO65_NO_163J_LINE", "severity": "info",
     "title": "VERIFIED NEGATIVE: Form MO-1065 has no 163(j) line, in either direction",
     "condition": "a 163(j) carryforward addition or disallowed-interest subtraction is present",
     "message": ("Form MO-1065 carries NEITHER the section 143.121.2(6) business-interest carryforward "
                 "addition NOR the section 143.121.3(11) disallowed-interest subtraction, on the face "
                 "or in its embedded instructions -- a full-text search of the PDF for '163' returns "
                 "ZERO hits. Form MO-1120S folds both into Lines 3 and 9 by instruction, and Form "
                 "MO-PTE gives each its own line (4 and 11). Neither statutory subdivision is "
                 "entity-type-limited on its face. Report the amount through the Line 3 or Line 8 "
                 "'Other adjustments' write-in with a description."),
     "notes": "U7 -- settle by a DOR statement on where a partnership reports these."},
    {"diagnostic_id": "D_MO65_NO_3_9_LINE", "severity": "info",
     "title": "VERIFIED NEGATIVE: MO-1065 has no 143.121.3(9) disposition-recovery line",
     "condition": "2002-03 vintage property with a Missouri basis difference is disposed of",
     "message": ("Form MO-1120S has BOTH the section 143.121.3(7) basis line (Line 10) and the "
                 "section 143.121.3(9) disposition-recovery line (Line 11). Form MO-1065 has ONLY the "
                 "basis line, at Line 9. A partnership disposing of property purchased between July "
                 "1, 2002 and June 30, 2003 must report the recovery through the Line 8 'Other "
                 "adjustments' write-in. Neither the form nor the instructions say so."),
     "notes": "N9 / U19. Paired with RED-DEFER R5."},
    {"diagnostic_id": "D_MO65_SPECIAL_ALLOCATION", "severity": "error",
     "title": "Special allocation - Missouri requires a narrative explanation (RED-DEFER R14)",
     "condition": "Page 3 Column 5 amounts are not derived from a single blended profit percentage",
     "message": ("Missouri requires a detailed explanation, INCLUDING EXTRACTS FROM THE PARTNERSHIP "
                 "AGREEMENT and the non-tax purposes and effects of the allocation method, when the "
                 "partner adjustment is not based on a single profit-and-loss percentage. See also "
                 "section 143.411.3, RSMo (tax-avoidance special allocations disregarded). Prepare "
                 "the explanation manually."),
     "notes": "The anti-704(b) guard, printed in the Column 5 instruction."},
    {"diagnostic_id": "D_MO_COMPOSITE_DEFERRED", "severity": "error",
     "title": "Composite return - filed on Form MO-1040, not prepared by this product (R2)",
     "condition": "the Composite box is checked on MO-1065, or any owner is flagged composite",
     "message": ("The Missouri composite return is filed on FORM MO-1040 under 12 CSR 10-2.190 with "
                 "instructions in Form 5677, at a flat 4.7 percent. It is not prepared by this "
                 "product. SUPPRESS FORM MO-2NR FOR EVERY OWNER INCLUDED ON THE COMPOSITE RETURN -- "
                 "'Do not issue a Form MO-2NR to a partner or shareholder who includes their Missouri "
                 "income on a composite return.'"),
     "notes": ("⚠ N11 / U23: MO-1065 HAS a composite checkbox and MO-1120S DOES NOT, even though "
               "143.471.5 grants S corporations the same right and the MO-1120S instructions list "
               "composite election as a withholding exception.")},
    {"diagnostic_id": "D_MO65_EXT_FEDERAL_ONLY", "severity": "info",
     "title": "MO-1065 has no Missouri extension form - attach the federal Form 7004",
     "condition": "an extension is claimed on Form MO-1065",
     "message": ("Form MO-1065 appears on NEITHER Form MO-7004's nor Form MO-60's face. Check the "
                 "extension box on the return and attach a copy of the approved federal Form 7004. "
                 "'(Failure to check this box and provide a copy of the extension may result in "
                 "disallowing the extension.)' ⚠ Forms MO-1NR and MO-2NR follow the EXTENDED due "
                 "date; FORM MO-3NR DOES NOT -- it is due by the original date WITHOUT REGARD TO AN "
                 "EXTENSION."),
     "notes": ("U24. The Department's own extension forms contradict each other; this build follows "
               "the return's own face, per D-10's principle.")},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM MO_1065 -- TEST SCENARIOS
# ═══════════════════════════════════════════════════════════════════════════
MO1065_SCENARIOS: list[dict] = [
    {"scenario_name": "MO-1065 SHORT FORM - both gating questions No, signature-only return",
     "scenario_type": "edge",
     "inputs": {"q1_has_modifications": False, "q2_has_nonresident_partners": False},
     "expected_outputs": {"filing_mode": "short_form", "lines_1_to_13_suppressed": True,
                          "page_3_suppressed": True,
                          "attachments": ["Federal Form 1065 and all schedules including Schedule K-1"]},
     "notes": "A genuine short-circuit. Implement as a filing MODE, not as blank lines.", "sort_order": 1},
    {"scenario_name": "MO-1065 $500 EXPENSE FLOOR - a $400 expense is DROPPED and the subtraction GROWS",
     "scenario_type": "edge",
     "inputs": {"l6a_exempt_federal_obligations": 10000, "l6b_related_expenses": 400},
     "expected_outputs": {"L6": 10000, "expense_applied": 0, "expense_dropped_by_floor": True},
     "notes": ("⚠⚠ THE FLOOR IS ON THE EXPENSE, NOT ON THE SUBTRACTION. Reading it as a threshold on "
               "the subtraction gives $9,600 and understates the modification by $400 on every "
               "affected return."),
     "sort_order": 2},
    {"scenario_name": "MO-1065 $500 EXPENSE FLOOR - a $500 expense IS applied (equal-to counts)",
     "scenario_type": "edge",
     "inputs": {"l6a_exempt_federal_obligations": 10000, "l6b_related_expenses": 500},
     "expected_outputs": {"L6": 9500, "expense_applied": 500, "expense_dropped_by_floor": False},
     "notes": "'The expenses must EQUAL OR EXCEED $500' -- the boundary is inclusive.", "sort_order": 3},
    {"scenario_name": "MO-1065 net adjustment - Line 11 and Line 12 are mutually exclusive",
     "scenario_type": "normal",
     "inputs": {"L1": 5000, "L2": 1000, "L3": 0, "L4": 0, "L6": 2000, "L7": 500, "L8": 0, "L9": 0},
     "expected_outputs": {"L5": 6000, "L10": 2500, "L11": 3500, "L12": 0},
     "sort_order": 4},
    {"scenario_name": "MO-1065 Line 13 stays OUTSIDE the totals and lands on MO-A Line 16",
     "scenario_type": "edge",
     "inputs": {"L5": 6000, "L10": 2500, "l13_agriculture_disaster_relief": 40000},
     "expected_outputs": {"L10": 2500, "L11": 3500, "L12": 0, "L13": 40000,
                          "l13_in_totals": False,
                          "l13_owner_landing": "MO-A Part 1 Line 16",
                          "face_spelling": "Agriculture Disaster Relief"},
     "notes": ("⚠ On MO-PTE the same statute's line (Line 10) is INSIDE the subtraction total, and "
               "the face spells it `Agricultural`. Same statute, three placements, two behaviours, "
               "two spellings."),
     "sort_order": 5},
    {"scenario_name": "MO-1065 DEPRECIATION - post-2003 property produces NO Missouri modification",
     "scenario_type": "edge",
     "inputs": {"purchase_date": "2025-06-01", "federal_bonus_taken": 1000000},
     "expected_outputs": {"missouri_modification": 0, "state_179_limit": None,
                          "shadow_book_required": False},
     "notes": ("VERIFIED NEGATIVE, closed at 143.121.2(3) -- the ADD-BACK ITSELF is window-limited to "
               "2002-07-01 through 2003-06-30. 100% OBBBA bonus flows through untouched."),
     "sort_order": 6},
    {"scenario_name": "MO-1065 DEPRECIATION - 2002-03 vintage property IS in the window",
     "scenario_type": "edge",
     "inputs": {"purchase_date": "2002-12-15"},
     "expected_outputs": {"in_window": True, "line": "9", "red_defer": "R5"},
     "notes": "The only Missouri depreciation modification that exists, and it is a legacy residual.",
     "sort_order": 7},
    {"scenario_name": "MO-1065 SOURCING - MO-NRP and MO-MS PTE percentages must AGREE (U4 flip)",
     "scenario_type": "normal",
     "inputs": {"mo_nrp_column_c_pct": 62.5, "mo_ms_pte_pct": 62.5},
     "expected_outputs": {"delta": 0.0, "expected_delta": "ZERO", "severity": None},
     "notes": ("⚠⚠ THE EXPECTATION FLIPPED on 2026-08-19. 12 CSR 10-2.255(3) puts partnerships on "
               "143.455, identical to S corporations, so agreement is now the NORMAL case."),
     "sort_order": 8},
    {"scenario_name": "MO-1065 SOURCING - a non-zero delta is now a PROBABLE ERROR, not normal",
     "scenario_type": "failure",
     "inputs": {"mo_nrp_column_c_pct": 62.5, "mo_ms_pte_pct": 48.0},
     "expected_outputs": {"delta": 14.5, "severity": "warning",
                          "reads_as": "PROBABLE ERROR (or an unapproved Part 3 election)"},
     "notes": "Keep the diagnostic; its MEANING changed, not its existence.", "sort_order": 9},
    {"scenario_name": "MO-1065 WITHHOLDING SURVIVES THE PTE ELECTION - the client pays twice",
     "scenario_type": "failure",
     "inputs": {"owner_kind": "individual", "missouri_source_income": 200000,
                "pte_election_made": True},
     "expected_outputs": {"required": True, "rate": 0.047, "amount": 9400.0,
                          "election_relieved_withholding": False, "issue_mo_2nr": True},
     "notes": ("⚠⚠ 12 CSR 10-2.436(8). An electing partnership pays 4.7% entity tax on this income "
               "AND withholds 4.7% on the same income. Stated ONLY in the regulation -- nowhere on "
               "Form MO-PTE, in its instructions, or in the DOR FAQ. Campaign D-12 C6."),
     "sort_order": 10},
    {"scenario_name": "MO-1065 WITHHOLDING - the $1,200 de minimis is STRICTLY LESS THAN",
     "scenario_type": "edge",
     "inputs": {"owner_kind": "individual", "missouri_source_income": 1200,
                "pte_election_made": False},
     "expected_outputs": {"required": True, "exception": None, "amount": 56.4},
     "notes": ("143.411.5(2): 'LESS THAN twelve hundred dollars'. An owner at exactly $1,200 is IN "
               "scope. (Same boundary discipline as the Arizona $150,000 'exceeds' question.)"),
     "sort_order": 11},
    {"scenario_name": "MO-1065 WITHHOLDING - a corporate partner is OUT OF SCOPE entirely",
     "scenario_type": "edge",
     "inputs": {"owner_kind": "corporation", "missouri_source_income": 500000},
     "expected_outputs": {"required": False, "issue_mo_2nr": False},
     "notes": ("'Do not withhold for any partners or S corporation shareholders who are partnerships, "
               "corporations, trusts, or estates.' ⚠ But a GRANTOR TRUST under Reg. 1.671-4(b) IS "
               "treated as an individual and IS in scope."),
     "sort_order": 12},
    {"scenario_name": "MO-1065 WITHHOLDING - a zero-dollar MO-2NR IS STILL REQUIRED",
     "scenario_type": "edge",
     "inputs": {"owner_kind": "individual", "missouri_source_income": 800,
                "mo_3nr_on_file": True},
     "expected_outputs": {"required": False, "exception": "mo_3nr", "issue_mo_2nr": True,
                          "amount": 0.0},
     "notes": ("'Issue Form MO-2NR, EVEN IF NO TAX IS WITHHELD or there is an exemption certificate "
               "on file.' The only suppression is a composite-return owner."),
     "sort_order": 13},
    {"scenario_name": "MO-1065 WITHHOLDING BASE - MO-NRP 'Lines 1 through 11' silently excludes 179",
     "scenario_type": "failure",
     "inputs": {"part1_column_e": {"1": 100000, "2": 0, "3c": 0, "4a": 20000, "5": 5000,
                                   "10": 0, "11": 0, "12": 30000, "13": 2000, "13e": 1000}},
     "expected_outputs": {"base": 125000, "excluded_total": 33000, "requires_human_review": True},
     "notes": ("The DOR's 'Lines 1 through 11' reads over a NON-CONTIGUOUS set (1, 2, 3c, 4a, 5, 10, "
               "11, 12, 13, 13e), so IRC 179, contributions and other deductions never enter the "
               "base. THIS DETERMINES CASH WITHHELD. (U9)"),
     "sort_order": 14},
    {"scenario_name": "MO-1065 NAME CONTROL - the six DOR examples, including LEE (not padded)",
     "scenario_type": "normal",
     "inputs": {"last_names": ["Brown", "DeJesus", "Lee", "Torres-Lopes", "McCarty", "O'Neill"]},
     "expected_outputs": {"name_controls": ["BROW", "DEJE", "LEE", "TORR", "MCCA", "ONEI"]},
     "notes": ("Printed on Form MO-2NR. Hyphens SPLIT, apostrophes are DROPPED, short names are NOT "
               "PADDED."),
     "sort_order": 15},
    {"scenario_name": "MO-1065 PAGE 3 - percentages round to WHOLE NUMBERS, not two decimals",
     "scenario_type": "edge",
     "inputs": {"k1_percent": 33.333, "L11": 90000},
     "expected_outputs": {"col_4_rounded": 33, "rounding_convention": "whole numbers",
                          "contrast": "MO-PTE Part B Column 5 uses TWO decimal places"},
     "notes": ("⚠ THREE ROUNDING CONVENTIONS LIVE IN THIS LANE and the DOR states a TIE-BREAK FOR "
               "NONE OF THEM. This build uses ROUND_HALF_UP as a declared engineering decision."),
     "sort_order": 16},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM MO_1120S -- FACTS
# ⚠ THE TITLE LIES. 143.471.1: an S corporation 'shall not be subject to the
# taxes imposed by section 143.071'. MO-1120S computes NO TAX. It is a
# modification-and-allocation return exactly like MO-1065.
# ═══════════════════════════════════════════════════════════════════════════
MO1120S_FACTS: list[dict] = [
    {"fact_key": "mo1120s_q1_has_modifications",
     "label": "1. Does the S-Corporation have any Missouri modifications?",
     "data_type": "boolean", "required": True, "sort_order": 1},
    {"fact_key": "mo1120s_q2_has_nonresident_shareholders",
     "label": "2. Does the S-Corporation have any nonresident shareholders?",
     "data_type": "boolean", "required": True, "sort_order": 2,
     "notes": "If Yes: complete Lines 1-15, the shareholder information on page 3, AND FORM MO-NRS."},
    {"fact_key": "mo1120s_q3_income_outside_missouri",
     "label": "3. Does the S-Corporation have income derived from sources other than Missouri?",
     "data_type": "boolean", "required": True, "sort_order": 3,
     "notes": ("⭐ THE APPORTIONMENT GATE, AND IT HAS NO MO-1065 COUNTERPART. 'If Yes, complete and "
               "attach Form MO-MSS.' Partnerships have no such question and no schedule of their own "
               "-- they BORROW MO-MSS, deliberately (12 CSR 10-2.255(3)).")},
    {"fact_key": "mo1120s_charter_number", "label": "Charter Number", "data_type": "string",
     "sort_order": 4, "notes": "⚠ MO-1120S and MO-PTE have a Charter Number field; MO-1065 does not."},
    {"fact_key": "mo1120s_box_bankruptcy", "label": "Bankruptcy", "data_type": "boolean",
     "sort_order": 5, "notes": "⚠ MO-1120S and MO-PTE have a Bankruptcy box; MO-1065 does not."},
    {"fact_key": "mo1120s_box_federal_extension",
     "label": "Select this box if you have an approved federal extension (attach Federal Form 7004)",
     "data_type": "boolean", "sort_order": 6,
     "notes": ("⚠⚠ THE THREE-WAY EXTENSION CONTRADICTION (U24). MO-1120S itself names NO Missouri "
               "form. MO-7004 says S corporations should 'use Form MO-60'. MO-60's face has NO S-CORP "
               "CHECKBOX and its instructions say 'Fiduciary and S corporation filers will be granted "
               "an automatic extension of time to file based on the allowed extension of time to file "
               "according to the Federal Form 7004.' BUILD TO THE RETURN'S OWN FACE: federal 7004 "
               "only.")},
    {"fact_key": "mo1120s_l1a_state_local_income_taxes",
     "label": "1a. State and local income taxes deducted on Federal Form 1120S",
     "data_type": "decimal", "sort_order": 10,
     "notes": ("Instruction heading: 'LINE 1 - MISSOURI CORPORATION INCOME TAX & CORPORATION INCOME "
               "TAX OF OTHER STATES DEDUCTED IN DETERMINING FEDERAL TAXABLE INCOME'. 143.141(1) and "
               "(2); 12 CSR 10-2.160. ⚠ 'This may include, but not be limited to, A STATE'S ELECTIVE "
               "PASS-THROUGH ENTITY INCOME TAX.' " + MO_FEDERAL_LINE_STAMP)},
    {"fact_key": "mo1120s_l1b_city_earnings_taxes",
     "label": "1b. Enter Kansas City and St. Louis earnings taxes on Line 1b. Enter Lines 1a minus 1b on Line 1.",
     "data_type": "decimal", "sort_order": 11, "notes": MO_CITY_EARNINGS_TAX_NOTE},
    {"fact_key": "mo1120s_l2a_state_local_bond_interest",
     "label": "2a. State and local bond interest (except Missouri)",
     "data_type": "decimal", "sort_order": 12, "notes": "143.121.2(2)"},
    {"fact_key": "mo1120s_l2b_related_expenses",
     "label": ("2b. Enter expenses related to Line 2a on Line 2b (if less than $500, enter zero). "
               "Enter Line 2a minus Line 2b on Line 2."),
     "data_type": "decimal", "sort_order": 13, "notes": "⚠ A FLOOR ON THE EXPENSE, not a threshold."},
    {"fact_key": "mo1120s_l3_other_additions",
     "label": "3. Partnership / Fiduciary / Other adjustments -- ADDITION (incl. the 163(j) carryforward)",
     "data_type": "decimal", "sort_order": 14,
     "notes": ("Heading 'LINE 3 - FIDUCIARY, PARTNERSHIP, AND OTHER ADJUSTMENTS'. Sources: MO-1041 "
               "Page 2 Part 1 LINE 19 and MO-1065 LINE 11 (143.121.4 and .5); 'A copy of Forms "
               "MO-1041 and MO-1065 must be attached.' ⭐ FOLDED IN HERE BY INSTRUCTION: 'Business "
               "Interest Expense Carryforward - Enter any interest expense paid or accrued in a "
               "previous taxable year, but allowed as a deduction under 26 U.S.C. Section 163 ... in "
               "the current taxable year by reason of the carryforward of disallowed business "
               "interest provisions of 26 U.S.C. Section 163(j) ... (Section 143.121.2(6), RSMo).' "
               "⚠ MO-PTE gives this its OWN Line 4; MO-1065 has it NOWHERE (N7).")},
    {"fact_key": "mo1120s_l4_food_pantry",
     "label": "4. Donations claimed for the Food Pantry Tax Credit deducted from federal taxable income",
     "data_type": "decimal", "sort_order": 15,
     "notes": ("135.647. 'donations claimed for the Food Pantry Tax Credit THAT WERE ALSO TAKEN AS A "
               "DEDUCTION on the Federal Form 1120-S return.' ⚠ MO-PTE has no such line (N6).")},
    {"fact_key": "mo1120s_l6a_exempt_federal_obligations",
     "label": "6a. Interest from exempt federal obligations",
     "data_type": "decimal", "sort_order": 16,
     "notes": "Heading adds '(MUST ATTACH SCHEDULE)'. 143.121.3(1); 12 CSR 10-2.150."},
    {"fact_key": "mo1120s_l6b_related_expenses",
     "label": ("6b. Enter expenses related to Line 6a on Line 6b (if less than $500, enter zero). "
               "Enter Line 6a minus Line 6b on Line 6."),
     "data_type": "decimal", "sort_order": 17},
    {"fact_key": "mo1120s_l7_state_refund",
     "label": "7. Amount of any state income tax refund included in federal ordinary income",
     "data_type": "decimal", "sort_order": 18,
     "notes": ("143.121.3(5). ⚠ DEFECT #7: the FACE says 'federal ORDINARY income' while the "
               "instruction heading says 'INCLUDED IN FEDERAL TAXABLE INCOME'. THE FACE GOVERNS.")},
    {"fact_key": "mo1120s_l8_mohela",
     "label": "8. Federally taxable - Missouri exempt obligations (MOHELA)",
     "data_type": "decimal", "sort_order": 19,
     "notes": ("'The amount of any bond issued by the Missouri Higher Education Loan Authority "
               "(MOHELA) INCLUDING INTEREST OR PROCEEDS RESULTING FROM THE SALE OF THE BOND is exempt "
               "from Missouri tax ... pursuant to Section 173.440, RSMo.' ⚠ MO-1065 HAS NO MOHELA "
               "LINE (N8).")},
    {"fact_key": "mo1120s_l9_other_subtractions",
     "label": ("9. Partnership / Fiduciary / Build America and Recovery Zone Bond Interest / Missouri "
               "Public-Private Transportation Act / Other adjustments -- SUBTRACTION"),
     "data_type": "decimal", "sort_order": 20,
     "notes": ("FIVE checkboxes. Sources: MO-1041 Page 2 Part 1 LINE 20 and MO-1065 LINE 12; Build "
               "America / Recovery Zone (108.1020); Public-Private Transportation Act (227.646); the "
               "MARIJUANA (280E) deduction; the BROADBAND GRANT (143.121.3(13)) ⚠ WITH AN S-CORP-ONLY "
               "CAP THAT HAS NO MO-1065 OR MO-PTE ANALOGUE: 'To the extent such grant income was also "
               "included on Federal Form 1120-S, LINE 5, the subtraction for that portion of the "
               "grant income CANNOT EXCEED THE AMOUNT ON FEDERAL FORM 1120-S, LINE 22'; and the "
               "DISALLOWED BUSINESS INTEREST EXPENSE (143.121.3(11)). " + MO_FEDERAL_LINE_STAMP)},
    {"fact_key": "mo1120s_l10_depreciation_basis_adj",
     "label": "10. Missouri depreciation basis adjustment",
     "data_type": "decimal", "sort_order": 21,
     "notes": ("⭐ THE ONE DOCUMENT IN THE WHOLE LANE THAT SPELLS THE WINDOW OUT IN WORDS: 'Enter the "
               "difference between the federal and Missouri depreciation calculated on assets "
               "purchased BETWEEN JULY 1, 2002 AND JUNE 30, 2003. See Section 143.121.3(7), RSMo.' "
               "⚠ The verified negative does NOT rest on this instruction -- it rests on "
               "143.121.2(3), the ADD-BACK PROVISION ITSELF, which is window-limited on its face.")},
    {"fact_key": "mo1120s_l11_depreciation_recovery",
     "label": "11. Depreciation recovery on qualified property that is sold",
     "data_type": "decimal", "sort_order": 22,
     "notes": ("'Enter any depreciation that was previously not recovered when an asset is sold or "
               "otherwise disposed of and federal bonus depreciation was previously taken. (Section "
               "143.121.3(9), RSMo) THIS CAN ONLY APPLY IF THE PROPERTY WAS PURCHASED BETWEEN JULY 1, "
               "2002, AND JUNE 30, 2003.' ⚠ MO-1065 HAS NO SUCH LINE (N9 / U19); MO-PTE has neither "
               "depreciation line at all (N5).")},
    {"fact_key": "mo1120s_l15_agriculture_disaster_relief",
     "label": "15. Agriculture Disaster Relief",
     "data_type": "decimal", "sort_order": 23,
     "notes": ("143.121.3(10). ⚠ OUTSIDE the Line 12 total, same as MO-1065 Line 13 -- and UNLIKE "
               "MO-PTE Line 10, which is INSIDE the total. ⚠ DEFECT #11 detail: this face carries NO "
               "STATUTORY CITE, whereas MO-1065 L13 and MO-NRS Part 2 L15 both print '(Section "
               "143.121.3(10), RSMo)'. ⚠ SPELLING: `Agriculture` here; `Agricultural` on MO-PTE L10.")},
    {"fact_key": "mo1120s_shareholder_share_pct",
     "label": "Page 3 Column 4 - Shareholder's Share %",
     "data_type": "decimal", "sort_order": 30,
     "validation_rule": "rounded to WHOLE NUMBERS; the Total row should foot to 100%",
     "notes": "⚠ 'Round percentages to whole numbers.' " + MO_FEDERAL_LINE_STAMP},
    {"fact_key": "mo1120s_mo_mss_required",
     "label": "Form MO-MSS required (question 3 is Yes)",
     "data_type": "boolean", "sort_order": 40,
     "notes": "'Do not complete this form if all income is from Missouri sources.'"},
    {"fact_key": "mo1120s_mo_mss_method",
     "label": "MO-MSS Apportionment Election (select exactly ONE)",
     "data_type": "choice", "choices": ["2a", "3", "4", "5", "6", "7"], "sort_order": 41,
     "notes": ("⚠ C11: the mileage note is defective for TWO methods. Method THREE (143.455.14) is a "
               "GROSS-EARNINGS rule and Method FIVE (143.455.16) is a FLAT ONE-HALF rule. ONLY FOUR "
               "AND SIX ARE MILEAGE-DRIVEN. ⚠ 'Once an election has been made, it cannot be changed "
               "with respect to the same taxable period.' ⚠ The 'must choose Method Two A' default is "
               "printed on Form MO-MS (C-corp) ONLY -- on the PTE/S-corp forms it is INFERRED, NOT "
               "PRINTED (C4 / U5). RED-DEFER R4 for everything but Two A.")},
    {"fact_key": "mo1120s_form_8886_attached",
     "label": "Federal Form 8886 copies attached (MANDATORY for every corporation)",
     "data_type": "boolean", "sort_order": 42,
     "notes": ("⭐ 'Every corporation must include with the Missouri return a copy of EACH FEDERAL "
               "FORM 8886 that was filed with the IRS as part of its federal return.' NO MO-1065 OR "
               "MO-PTE ANALOGUE.")},
    {"fact_key": "mo1120s_shareholder_extract_redacted",
     "label": "Per-shareholder redacted extract of Page 3 furnished",
     "data_type": "boolean", "sort_order": 43,
     "notes": ("⭐ A REDACTION REQUIREMENT WITH NO MO-1065 COUNTERPART: '...furnish a copy of (or "
               "extract of all relevant information from) the Form MO-1120S to each shareholder, BUT "
               "WITH INFORMATION ABOUT OTHER SHAREHOLDERS, SUCH AS SOCIAL SECURITY NUMBERS OR SHARE "
               "PERCENTAGES, REMOVED OR REDACTED.' The print engine needs a per-shareholder redacted "
               "variant of Page 3.")},
    {"fact_key": "mo1120s_is_financial_institution",
     "label": "S corporation is a bank, bank holding company, S&L or credit institution (BTC credit)",
     "data_type": "boolean", "sort_order": 44,
     "notes": ("143.471.10 (banks/bank holding companies), .11 (savings and loan associations), .12 "
               "(credit institutions) -- a pro-rata Chapter 148 tax CREDIT (alpha code BTC), NOT a "
               "modification, allocated by stock ownership, carried forward 'the lesser of five years "
               "or until used, provided such credits are used as soon as the taxpayer has Missouri "
               "taxable income.' RED-DEFER R6.")},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM MO_1120S -- RULES
# ═══════════════════════════════════════════════════════════════════════════
MO1120S_RULES: list[dict] = [
    {"rule_id": "R-MO20S-NOTAX", "title": "⚠ MO-1120S computes NO TAX, despite its title",
     "rule_type": "classification", "sort_order": 1,
     "inputs": [], "outputs": ["tax_liability"],
     "formula": "tax = 0 always; MO-1120S is a modification-and-allocation return",
     "description": ("143.471.1, verbatim: 'An S corporation, as defined by Section 1361(a)(1) of the "
                     "Internal Revenue Code, SHALL NOT BE SUBJECT TO THE TAXES IMPOSED BY SECTION "
                     "143.071, or other sections imposing income tax on corporations.' The form is "
                     "titled 'S-Corporation Income Tax Return' and computes no tax at all -- exactly "
                     "like MO-1065. The ONLY tax-computing return in the Missouri PTE lane is "
                     "Form MO-PTE."),
     "notes": "Every S corporation must nonetheless register for a Missouri Tax I.D. Number."},
    {"rule_id": "R-MO20S-GATES", "title": "THREE gating questions - and question 3 has no MO-1065 twin",
     "rule_type": "routing", "sort_order": 2,
     "inputs": ["mo1120s_q1_has_modifications", "mo1120s_q2_has_nonresident_shareholders",
                "mo1120s_q3_income_outside_missouri"],
     "outputs": ["required_schedules"],
     "formula": "q2 -> MO-NRS per nonresident shareholder; q3 -> MO-MSS",
     "description": ("Q1 and Q2 mirror MO-1065. ⭐ Q3 -- 'Does the S-Corporation have income derived "
                     "from sources other than Missouri? If Yes, complete and attach Form MO-MSS.' -- "
                     "IS THE APPORTIONMENT GATE AND EXISTS ONLY ON THE S-CORPORATION RETURN. "
                     "Partnerships have no apportionment question and no schedule of their own; they "
                     "BORROW MO-MSS, which 12 CSR 10-2.255(3) makes deliberate."),
     "notes": ("Who must file: 'Every S-Corporation must file Form MO-1120S if they file Federal Form "
               "1120-S and the S-Corporation has: 1) a shareholder that is a Missouri resident; or 2) "
               "any income derived from Missouri sources.' 143.471; 12 CSR 10-2.190.")},
    {"rule_id": "R-MO20S-500FLR", "title": "The $500 related-expense FLOOR (2a/2b and 6a/6b)",
     "rule_type": "calculation", "sort_order": 3,
     "inputs": ["mo1120s_l2a_state_local_bond_interest", "mo1120s_l2b_related_expenses",
                "mo1120s_l6a_exempt_federal_obligations", "mo1120s_l6b_related_expenses"],
     "outputs": ["MO1120S_L2", "MO1120S_L6"],
     "formula": "net = gross - (expense if expense >= 500 else 0)",
     "description": ("'if less than $500, enter zero' -- A FLOOR ON THE EXPENSE. Below $500 the "
                     "expense is dropped and the GROSS survives, making the modification LARGER."),
     "notes": "Identical in substance to MO-1065's and MO-PTE's, but transcribe each face's wording."},
    {"rule_id": "R-MO20S-ADJ", "title": "Lines 5, 12, 13 and 14 - the S-corporation adjustment",
     "rule_type": "calculation", "sort_order": 4,
     "inputs": ["MO1120S_L1", "MO1120S_L2", "mo1120s_l3_other_additions", "mo1120s_l4_food_pantry",
                "MO1120S_L6", "mo1120s_l7_state_refund", "mo1120s_l8_mohela",
                "mo1120s_l9_other_subtractions", "mo1120s_l10_depreciation_basis_adj",
                "mo1120s_l11_depreciation_recovery"],
     "outputs": ["MO1120S_L5", "MO1120S_L12", "MO1120S_L13", "MO1120S_L14"],
     "formula": ("L5 = L1+L2+L3+L4; L12 = L6+L7+L8+L9+L10+L11; L13 = max(0, L5-L12); "
                 "L14 = max(0, L12-L5)"),
     "description": ("⚠ NOTE THE DIFFERENT SUBTRACTION RANGE: MO-1065 totals Lines 6-9 at Line 10; "
                     "MO-1120S totals Lines 6-11 at Line 12, because it carries TWO depreciation "
                     "lines and a MOHELA line that MO-1065 does not. 'If Line 5 is greater than Line "
                     "12, enter the difference on Line 13 AS A POSITIVE NUMBER. If Line 5 is less "
                     "than Line 12, skip Line 13 and complete Line 14.' / 'Enter AS A POSITIVE NUMBER "
                     "on Line 14.'"),
     "notes": "⚠ LINE 15 IS NOT IN THIS CHAIN -- see R-MO20S-L15."},
    {"rule_id": "R-MO20S-L15", "title": "Line 15 sits OUTSIDE the totals (and carries no cite on the face)",
     "rule_type": "calculation", "sort_order": 5,
     "inputs": ["mo1120s_l15_agriculture_disaster_relief"], "outputs": ["MO1120S_L15"],
     "formula": "L15 is reported separately; it is NOT included in L12, L13 or L14",
     "description": ("Same placement as MO-1065 Line 13 and the OPPOSITE of MO-PTE Line 10, which is "
                     "INSIDE the subtraction total and reduces the entity's tax base directly. ⚠ This "
                     "face prints NO statutory cite, unlike MO-1065 L13 and MO-NRS Part 2 L15, which "
                     "both print '(Section 143.121.3(10), RSMo)'. ⚠ SPELLING: `Agriculture` here, "
                     "`Agricultural` on MO-PTE."),
     "notes": "Attach a Form 1099 indicating the agricultural payment."},
    {"rule_id": "R-MO20S-PG3", "title": "Page 3 allocation grid - 19 rows, and a REDACTED extract",
     "rule_type": "calculation", "sort_order": 6,
     "inputs": ["mo1120s_shareholder_share_pct", "MO1120S_L13", "MO1120S_L14"],
     "outputs": ["MO1120S_PG3_COL5"],
     "formula": "Col 5 (per shareholder) = Col 4 x (L13 or L14 on the Total line)",
     "description": ("Structurally identical to MO-1065 Page 3: 19 rows a) through s) plus Total. "
                     "Owner-side landing: '...must be reported as a modification by the shareholder "
                     "on their Form MO-1040 ..., either as an addition to, or subtraction from, "
                     "federal adjusted gross income.' ⚠ The MO-1120S instructions do NOT name the "
                     "MO-A line numbers that MO-1065's do."),
     "exceptions": ("⭐ THE REDACTION DUTY, with no MO-1065 counterpart: each shareholder's copy must "
                    "have 'information about other shareholders, such as social security numbers or "
                    "share percentages, REMOVED OR REDACTED.'"),
     "notes": "⚠ WHOLE NUMBERS here; MO-PTE Part B Column 5 uses TWO DECIMALS."},
    {"rule_id": "R-MO20S-MSS", "title": "MO-MSS produces a PER-ITEM percentage VECTOR, not one factor",
     "rule_type": "calculation", "sort_order": 7,
     "inputs": ["mo1120s_mo_mss_required", "mo1120s_mo_mss_method"],
     "outputs": ["MO_NRS_COLUMN_C"],
     "formula": ("Part 1 L3 = L1 / L2 (the receipts factor); per item, Column (c) = (apportioned "
                 "share + Missouri-allocated nonapportionable) / item total"),
     "description": ("The DOR's printed six-step example is the unit test: $15,000 net rental real "
                     "estate income, $3,000 nonapportionable of which $1,000 is Missouri-allocated, "
                     "factor 33.333% -> Column (b) $5,000 and Column (c) 33.333%. ⭐ Verbatim: 'If a "
                     "distributive share item is wholly or partially allocated as nonapportionable "
                     "income, A DIFFERENT PERCENTAGE WILL BE COMPUTED FOR THE ITEM.' ⚠⚠ MO-NRS COLUMN "
                     "(c) IS THEREFORE A VECTOR INDEXED BY DISTRIBUTIVE-SHARE LINE, defaulting to the "
                     "Line 3 receipts factor. ANY MODEL THAT STORES ONE APPORTIONMENT PERCENTAGE PER "
                     "RETURN IS WRONG."),
     "exceptions": ("Printed presumption: 'ALL INCOME IS PRESUMED TO BE APPORTIONABLE INCOME UNLESS "
                    "YOU CAN CLEARLY SHOW THE INCOME TO BE NONAPPORTIONABLE INCOME.' ⚠ N12 / U10: "
                    "Part 1 Lines 4-10 enumerate only SHORT-TERM capital gain -- there is no "
                    "long-term row, although 143.455.7 allocates capital gains generally, so "
                    "long-term allocation rides on an unstructured attachment."),
     "notes": ("⚠ MO-MSS Line 3 cites 143.455.2 on the face; .2 is the APPLICABILITY subsection. The "
               "receipts factor is .10 and sourcing is .11/.12 (defect #1).")},
    {"rule_id": "R-MO20S-C11", "title": "⚠ C11 - the mileage note is defective for TWO methods",
     "rule_type": "validation", "sort_order": 8,
     "inputs": ["mo1120s_mo_mss_method"], "outputs": ["method_basis"],
     "formula": "mileage_driven = method in ('4', '6')",
     "description": ("Campaign D-12 C11, restated BEFORE it propagates. 143.455.14 (Method THREE - "
                     "Transportation) is a GROSS-EARNINGS rule -- 'shall report its gross earnings "
                     "within the state on intrastate business and shall also report its gross "
                     "earnings on all interstate business done in this state... This subsection shall "
                     "not apply to a railroad.' 143.455.16 (Method FIVE - Interstate Bridge) is a "
                     "FLAT ONE-HALF rule. Only 143.455.15 (Four - Railroad) and 143.455.17 (Six - "
                     "Telephone and Telegraph) are mileage-driven, each with an elective INVESTMENT "
                     "RATIO alternative. So the printed note 'Complete mileage information below for "
                     "Method Three - Six' is defective for THREE **and** FIVE. Corroborated by "
                     "12 CSR 10-2.045(14)(B)."),
     "notes": ("⚠ Method Seven's cite is internally inconsistent on the DOR's own forms: the election "
               "list says 143.455.13(2) while the Method Seven instructions say .13(1). .13(1) is the "
               "industry-regulation (broadcaster, 12 CSR 10-2.260) route; .13(2) is the "
               "alternative-apportionment petition, with a preponderance-of-evidence burden under "
               ".13(3). Cite BOTH correctly. RED-DEFER R4.")},
    {"rule_id": "R-MO20S-THROWBK", "title": "Two THROWBACK-STYLE allocation tests survive (d)(2) and (g)(2)",
     "rule_type": "classification", "sort_order": 9,
     "inputs": ["mo1120s_mo_mss_required"], "outputs": ["nonapportionable_allocation"],
     "formula": "rules (a) through (g) per 143.455.6 to .9; (d)(2) and (g)(2) are throwback-style",
     "description": ("⭐ CONFIRMED VERBATIM ON THE STATUTE AND ON ALL THREE APPORTIONMENT FORMS: the "
                     "RECEIPTS FACTOR has NO throwback, but two ALLOCATION rules are throwback-style, "
                     "keyed to commercial domicile PLUS non-taxability elsewhere. (d)(2): capital "
                     "gains from TPP sales where commercial domicile is in this state AND the "
                     "taxpayer is not taxable in the situs state. (g)(2): patent and copyright "
                     "royalties utilized in a state where the taxpayer is not taxable, with "
                     "commercial domicile here. 'Commercial domicile' = 'the principal place from "
                     "which the trade or business of the taxpayer is directed or managed' "
                     "(143.455.3(2))."),
     "exceptions": MO_TAXABLE_IN_ANOTHER_STATE},
    {"rule_id": "R-MO20S-NRS", "title": "⚠⚠ MO-NRS derives its columns the REVERSE of MO-NRP",
     "rule_type": "calculation", "sort_order": 10,
     "inputs": ["MO_NRS_COLUMN_C"], "outputs": ["MO_NRS_COLUMN_B", "MO_NRS_COLUMN_E"],
     "formula": "(b) = (a) x (c);  (e) = (d) x (c)   ⚠ MO-NRP computes (c) = (b) / (a)",
     "description": ("Verbatim: 'Column (b): MULTIPLY THE AMOUNT IN COLUMN (a) BY THE PERCENT IN "
                     "COLUMN (c) and enter in Column (b).' / 'Column (c): Enter the percent from Form "
                     "MO-MSS, Line 3.' ⚠⚠ TWO IDENTICAL-LOOKING FIVE-COLUMN GRIDS, TWO INVERSE "
                     "ARITHMETICS. DO NOT SHARE A RULE BETWEEN MO-NRP AND MO-NRS."),
     "exceptions": ("Part 2: 'Do not complete Part 2 of Form MO-NRS if the \"Missouri S-Corporation "
                    "Adjustment\" and the \"Allocation of Missouri S-Corporation Adjustment to "
                    "Shareholders\" on Form MO-1120S were not completed.' Column (a) copies MO-1120S "
                    "Lines 1a-15 ROW FOR ROW; Column (d) copies MO-1120S Page 3 Column 5."),
     "notes": ("⚠ DOWNSTREAM CAUTION PRINTED ON THE FORM: 'The items from Form MO-NRS, Part 1, Column "
               "(e), that are to be income or losses should be entered on the Form MO-NRI, as "
               "Missouri source income. THESE AMOUNTS MUST BE ADJUSTED BY ANY CAPITAL GAIN OR PASSIVE "
               "LOSS LIMITATION AS REQUIRED.' -- the individual module inherits an unstated IRC 1211 "
               "/ 469 limitation step.")},
    {"rule_id": "R-MO20S-WHBASE", "title": "⚠ The MO-NRS withholding base DOUBLE-COUNTS as printed (U9)",
     "rule_type": "calculation", "sort_order": 11,
     "inputs": ["mo1120s_q2_has_nonresident_shareholders"], "outputs": ["MO_2NR_L1"],
     "formula": ("base = sum(MO-NRS Part 1 Column (e) lines 1, 2, 3, 4, 5a, 6, 7, 8a, 9, 10) -- "
                 "WITH 5b, 8b AND 8c SUPPRESSED"),
     "description": ("MO-1NR defines the S-corporation base as 'the net total of the amounts listed on "
                     "LINES 1 THROUGH 10 of ... Form MO-NRS'. ⚠⚠ SUMMED LITERALLY THAT DOUBLE-COUNTS: "
                     "`5b Qualified dividends` is a SUBSET of `5a Ordinary dividends`, and `8b "
                     "Collectibles (28%) gain` and `8c Unrecaptured section 1250 gain` are both "
                     "SUBSETS of `8a Net long-term capital gain`. A literal sum overstates the base "
                     "by 5b + 8b + 8c. It also excludes Line 11 (IRC 179) and Lines 12a-12e "
                     "(deductions). BUILD WITH THE SUBSET LINES SUPPRESSED. THIS DETERMINES CASH "
                     "WITHHELD."),
     "notes": ("⚠ requires_human_review on ANY return where 5b, 8b or 8c is non-zero. Campaign D-12 "
               "Group D. Get a DOR worked example before season. " + MO_FEDERAL_LINE_STAMP)},
    {"rule_id": "R-MO20S-WH", "title": "Nonresident withholding at 4.7% - the election does NOT stop it",
     "rule_type": "calculation", "sort_order": 12,
     "inputs": ["mo1120s_q2_has_nonresident_shareholders"], "outputs": ["MO_2NR_L2", "MO_1NR_L2"],
     "formula": "MO-2NR L2 = 4.7% x MO-2NR L1; MO-1NR L2 = sum(MO-2NR L2)",
     "description": ("143.471.6's five exceptions are word-for-word parallel to 143.411.5's. ⚠⚠ 12 CSR "
                     "10-2.436(8): the 143.436 election DOES NOT RELIEVE the S corporation of its "
                     "withholding obligations under 143.471.6. AN ELECTING S CORPORATION PAYS 4.7% "
                     "ENTITY TAX AND WITHHOLDS 4.7% ON THE SAME INCOME."),
     "exceptions": MO_WH_EXCEPTIONS_RULING_NOTE,
     "notes": ("⚠ THE FORMS DISAGREE WITH EACH OTHER ON THE DISTRIBUTION TEST: MO-1120S says 'in BOTH "
               "the current and prior taxable year'; MO-1065 says 'in the current OR prior'; the "
               "statute says 'in the current AND prior'. Three renderings of one condition (U22).")},
    {"rule_id": "R-MO20S-DEPR", "title": "VERIFIED NEGATIVE - both depreciation lines are window-closed",
     "rule_type": "validation", "sort_order": 13,
     "inputs": ["mo1120s_l10_depreciation_basis_adj", "mo1120s_l11_depreciation_recovery"],
     "outputs": ["depreciation_modification"],
     "formula": "both lines apply IFF the property was purchased 2002-07-01 through 2003-06-30",
     "description": ("MO-1120S is the ONLY document in the lane that prints the window IN WORDS, on "
                     "BOTH lines. But the negative is closed at the STATUTE: 143.121.2(3), the IRC "
                     "168 ADD-BACK ITSELF, is window-limited on its face and measured against IRC 168 "
                     "'as amended by the Job Creation and Worker Assistance Act of 2002'; "
                     "143.121.3(7) carries the identical window; 143.121.3(9) inherits it by "
                     "cross-reference; and 143.121 contains NO IRC 179 modification at all. THERE IS "
                     "NO OPEN-ENDED BONUS ADD-BACK IN MISSOURI LAW TO FIND."),
     "exceptions": ("⚠ NO MISSOURI 179 CONSTANT MAY EVER BE ENCODED, and no shadow depreciation book "
                    "exists. Do not port Virginia's derived state 179 figure and do not add a "
                    "nullable 'state depreciation adjustment' field for symmetry."),
     "notes": "RED-DEFER R5 covers the live 2002-03 residual."},
    {"rule_id": "R-MO20S-DUE", "title": "Due date, extension routing, and the mandatory Form 8886",
     "rule_type": "conditional", "sort_order": 14,
     "inputs": ["mo1120s_box_federal_extension", "mo1120s_form_8886_attached"],
     "outputs": ["due_date"],
     "formula": "the 15th day of the 4th month following the end of the tax year",
     "description": ("'Example: Taxable period of January 1, 2025, to December 31, 2025 is due APRIL "
                     "15, 2026.' Weekend/holiday rollover. ⚠⚠ THE THREE-WAY EXTENSION CONTRADICTION "
                     "(U24): MO-7004 says S corporations should use Form MO-60; MO-60's face has NO "
                     "S-corp checkbox and its instructions send S corporations to the federal 7004; "
                     "MO-1120S names no Missouri form. BUILD TO THE RETURN'S OWN FACE -- attach the "
                     "federal Form 7004, no Missouri extension form. ⭐ Form 8886: 'Every corporation "
                     "must include with the Missouri return a copy of EACH Federal Form 8886 that was "
                     "filed with the IRS.' NO MO-1065 OR MO-PTE ANALOGUE."),
     "notes": ("Signature: 'The Department of Revenue requires the return to be signed by AN OFFICER "
               "OF THE CORPORATION' -- contrast MO-1065's 'any member or partner'. Assembly: 'Assemble "
               "any forms and schedules in order behind Form MO-1120S ... DO NOT ATTACH ITEMS UNLESS "
               "REQUIRED TO DO SO.'")},
]

MO1120S_RULE_LINKS: list[tuple] = [
    ("R-MO20S-NOTAX", "MO_RSMO_143_411_471", "primary", "143.471.1 - not subject to 143.071"),
    ("R-MO20S-NOTAX", "MO_2025_FORM_MO1120S", "secondary", "the face computes no tax line"),
    ("R-MO20S-GATES", "MO_2025_FORM_MO1120S", "primary", "the three gating questions as printed"),
    ("R-MO20S-GATES", "MO_RSMO_143_411_471", "primary", "143.471 - who must file"),
    ("R-MO20S-500FLR", "MO_2025_FORM_MO1120S", "primary", "the 2b and 6b sub-line labels"),
    ("R-MO20S-ADJ", "MO_2025_FORM_MO1120S", "primary", "Lines 1a-14 as printed"),
    ("R-MO20S-ADJ", "MO_RSMO_143_121", "primary", "the modifications statute behind every line"),
    ("R-MO20S-L15", "MO_2025_FORM_MO1120S", "primary", "Line 15 printed OUTSIDE the totals, with no cite"),
    ("R-MO20S-L15", "MO_RSMO_143_121", "primary", "143.121.3(10)"),
    ("R-MO20S-PG3", "MO_2025_FORM_MO1120S", "primary", "the Page 3 grid and the redaction duty"),
    ("R-MO20S-MSS", "MO_2025_FORM_MOMSS", "primary", "the printed six-step per-item algorithm"),
    ("R-MO20S-MSS", "MO_RSMO_143_455", "primary", "the receipts factor at .10 and sourcing at .11/.12"),
    ("R-MO20S-C11", "MO_RSMO_143_455", "primary", ".14 gross earnings / .15 mileage / .16 one-half / .17 mileage"),
    ("R-MO20S-C11", "MO_2025_FORM_MOMSPTE", "secondary", "the defective face note, restated per C11"),
    ("R-MO20S-THROWBK", "MO_RSMO_143_455", "primary", ".6 to .9 - the seven allocation rules"),
    ("R-MO20S-THROWBK", "MO_2025_FORM_MOMSS", "implementation", "the same seven rules printed on the form"),
    ("R-MO20S-NRS", "MO_2025_FORM_MONRS", "primary", "the reverse column derivation, verbatim"),
    ("R-MO20S-NRS", "MO_12CSR_10_2_190_255", "primary", "12 CSR 10-2.255(2) - the S-corporation branch"),
    ("R-MO20S-WHBASE", "MO_2025_FORM_MO1NR_2NR_3NR", "primary", "the defective base definition"),
    ("R-MO20S-WHBASE", "MO_2025_FORM_MONRS", "primary", "the 5b / 8b / 8c subset lines"),
    ("R-MO20S-WH", "MO_RSMO_143_411_471", "primary", "143.471.6 - the five exceptions"),
    ("R-MO20S-WH", "MO_12CSR_10_2_436", "primary", "(8) - the election does NOT relieve withholding"),
    ("R-MO20S-DEPR", "MO_RSMO_143_121", "primary", "143.121.2(3) - the ADD-BACK ITSELF is window-limited"),
    ("R-MO20S-DEPR", "MO_2025_FORM_MO1120S", "implementation", "the only instructions stating the window in words"),
    ("R-MO20S-DUE", "MO_2025_FORM_MO1120S", "primary", "April 15, 2026, the officer signature and Form 8886"),
    ("R-MO20S-DUE", "MO_2025_EXTENSION_FORMS", "secondary", "the MO-7004 / MO-60 contradiction (U24)"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM MO_1120S -- LINES
# ═══════════════════════════════════════════════════════════════════════════
MO1120S_LINES: list[dict] = [
    {"line_number": "Q1", "line_type": "input", "sort_order": 1,
     "description": "1. Does the S-Corporation have any Missouri modifications?",
     "source_facts": ["mo1120s_q1_has_modifications"], "source_rules": ["R-MO20S-GATES"]},
    {"line_number": "Q2", "line_type": "input", "sort_order": 2,
     "description": "2. Does the S-Corporation have any nonresident shareholders?",
     "source_facts": ["mo1120s_q2_has_nonresident_shareholders"], "source_rules": ["R-MO20S-GATES"]},
    {"line_number": "Q3", "line_type": "input", "sort_order": 3,
     "description": "3. Does the S-Corporation have income derived from sources other than Missouri?",
     "source_facts": ["mo1120s_q3_income_outside_missouri"], "source_rules": ["R-MO20S-GATES"],
     "notes": "⭐ THE APPORTIONMENT GATE. No MO-1065 counterpart exists."},
    {"line_number": "1a", "line_type": "input", "sort_order": 4,
     "description": "State and local income taxes deducted on Federal Form 1120S",
     "source_facts": ["mo1120s_l1a_state_local_income_taxes"], "source_rules": ["R-MO20S-ADJ"],
     "notes": MO_FEDERAL_LINE_STAMP},
    {"line_number": "1b", "line_type": "input", "sort_order": 5,
     "description": ("Enter Kansas City and St. Louis earnings taxes on Line 1b. Enter Lines 1a minus "
                     "1b on Line 1."),
     "source_facts": ["mo1120s_l1b_city_earnings_taxes"], "source_rules": ["R-MO20S-ADJ"],
     "notes": "⚠ The three faces word this label DIFFERENTLY; transcribe each face's own wording."},
    {"line_number": "1", "line_type": "calculated", "sort_order": 6,
     "description": "Net state and local income taxes (1a minus 1b)", "calculation": "1a - 1b",
     "source_rules": ["R-MO20S-ADJ"]},
    {"line_number": "2a", "line_type": "input", "sort_order": 7,
     "description": "State and local bond interest (except Missouri)",
     "source_facts": ["mo1120s_l2a_state_local_bond_interest"], "source_rules": ["R-MO20S-500FLR"]},
    {"line_number": "2b", "line_type": "input", "sort_order": 8,
     "description": ("Enter expenses related to Line 2a on Line 2b (if less than $500, enter zero). "
                     "Enter Line 2a minus Line 2b on Line 2."),
     "source_facts": ["mo1120s_l2b_related_expenses"], "source_rules": ["R-MO20S-500FLR"]},
    {"line_number": "2", "line_type": "calculated", "sort_order": 9,
     "description": "Net state and local bond interest", "calculation": "2a - (2b if 2b >= 500 else 0)",
     "source_rules": ["R-MO20S-500FLR"]},
    {"line_number": "3", "line_type": "input", "sort_order": 10,
     "description": ("Partnership / Fiduciary / Other adjustments -- ADDITION, INCLUDING the 163(j) "
                     "business interest expense carryforward folded in by instruction"),
     "source_facts": ["mo1120s_l3_other_additions"], "source_rules": ["R-MO20S-ADJ"],
     "notes": "⭐ MO-PTE gives the 163(j) carryforward its OWN Line 4; MO-1065 has it nowhere (N7)."},
    {"line_number": "4", "line_type": "input", "sort_order": 11,
     "description": "Donations claimed for the Food Pantry Tax Credit deducted from federal taxable income",
     "source_facts": ["mo1120s_l4_food_pantry"], "source_rules": ["R-MO20S-ADJ"],
     "notes": "⚠ MO-PTE has NO Food Pantry line (N6)."},
    {"line_number": "5", "line_type": "subtotal", "sort_order": 12,
     "description": "Total of Lines 1 through 4", "calculation": "1 + 2 + 3 + 4",
     "source_rules": ["R-MO20S-ADJ"]},
    {"line_number": "6a", "line_type": "input", "sort_order": 13,
     "description": "Interest from exempt federal obligations (MUST ATTACH SCHEDULE)",
     "source_facts": ["mo1120s_l6a_exempt_federal_obligations"], "source_rules": ["R-MO20S-500FLR"]},
    {"line_number": "6b", "line_type": "input", "sort_order": 14,
     "description": ("Enter expenses related to Line 6a on Line 6b (if less than $500, enter zero). "
                     "Enter Line 6a minus Line 6b on Line 6."),
     "source_facts": ["mo1120s_l6b_related_expenses"], "source_rules": ["R-MO20S-500FLR"]},
    {"line_number": "6", "line_type": "calculated", "sort_order": 15,
     "description": "Net interest from exempt federal obligations",
     "calculation": "6a - (6b if 6b >= 500 else 0)", "source_rules": ["R-MO20S-500FLR"]},
    {"line_number": "7", "line_type": "input", "sort_order": 16,
     "description": "Amount of any state income tax refund included in federal ordinary income",
     "source_facts": ["mo1120s_l7_state_refund"], "source_rules": ["R-MO20S-ADJ"],
     "notes": "⚠ Defect #7 - the instruction heading says 'federal TAXABLE income'. THE FACE GOVERNS."},
    {"line_number": "8", "line_type": "input", "sort_order": 17,
     "description": "Federally taxable - Missouri exempt obligations (MOHELA, Section 173.440, RSMo)",
     "source_facts": ["mo1120s_l8_mohela"], "source_rules": ["R-MO20S-ADJ"],
     "notes": "⚠ MO-1065 HAS NO MOHELA LINE (N8)."},
    {"line_number": "9", "line_type": "input", "sort_order": 18,
     "description": ("Partnership / Fiduciary / Build America and Recovery Zone Bond Interest / "
                     "Missouri Public-Private Transportation Act / Other adjustments -- SUBTRACTION"),
     "source_facts": ["mo1120s_l9_other_subtractions"], "source_rules": ["R-MO20S-ADJ"],
     "notes": ("⚠ Carries an S-CORP-ONLY broadband cap with no MO-1065 or MO-PTE analogue: the "
               "subtraction 'cannot exceed the amount on Federal Form 1120-S, Line 22'. Also folds in "
               "the 163(j) DISALLOWED interest subtraction by instruction. " + MO_FEDERAL_LINE_STAMP)},
    {"line_number": "10", "line_type": "input", "sort_order": 19,
     "description": "Missouri depreciation basis adjustment",
     "source_facts": ["mo1120s_l10_depreciation_basis_adj"], "source_rules": ["R-MO20S-DEPR"],
     "notes": "⭐ The window is PRINTED IN WORDS here: July 1, 2002 through June 30, 2003. RED-DEFER R5."},
    {"line_number": "11", "line_type": "input", "sort_order": 20,
     "description": "Depreciation recovery on qualified property that is sold",
     "source_facts": ["mo1120s_l11_depreciation_recovery"], "source_rules": ["R-MO20S-DEPR"],
     "notes": "⚠ MO-1065 HAS NO SUCH LINE (N9 / U19); MO-PTE has neither depreciation line (N5)."},
    {"line_number": "12", "line_type": "subtotal", "sort_order": 21,
     "description": "Total Subtractions - Add Lines 6 through 11",
     "calculation": "6 + 7 + 8 + 9 + 10 + 11", "source_rules": ["R-MO20S-ADJ"],
     "notes": "⚠ A DIFFERENT RANGE from MO-1065's Line 10 (which totals 6 through 9)."},
    {"line_number": "13", "line_type": "total", "sort_order": 22,
     "description": "Missouri S-Corporation adjustment - Net Addition - excess Line 5 over Line 12",
     "calculation": "max(0, 5 - 12)  [enter AS A POSITIVE NUMBER]", "source_rules": ["R-MO20S-ADJ"],
     "destination_form": "MO-1120S Page 3 Column 5; MO-NRS Part 2 Column (a)"},
    {"line_number": "14", "line_type": "total", "sort_order": 23,
     "description": "Missouri S-Corporation adjustment - Net Subtraction - excess Line 12 over Line 5",
     "calculation": "max(0, 12 - 5)  [enter AS A POSITIVE NUMBER]", "source_rules": ["R-MO20S-ADJ"],
     "destination_form": "MO-1120S Page 3 Column 5; MO-NRS Part 2 Column (a)"},
    {"line_number": "15", "line_type": "informational", "sort_order": 24,
     "description": "Agriculture Disaster Relief",
     "source_facts": ["mo1120s_l15_agriculture_disaster_relief"], "source_rules": ["R-MO20S-L15"],
     "notes": ("⚠ OUTSIDE the Line 12 total. ⚠ NO statutory cite on THIS face, unlike MO-1065 L13 and "
               "MO-NRS Part 2 L15. ⚠ SPELLING: `Agriculture` here; `Agricultural` on MO-PTE L10.")},
    {"line_number": "PG3-C4", "line_type": "input", "sort_order": 30,
     "description": "Page 3 Column 4 - Shareholder's Share % (rounded to WHOLE NUMBERS)",
     "source_facts": ["mo1120s_shareholder_share_pct"], "source_rules": ["R-MO20S-PG3"]},
    {"line_number": "PG3-C5", "line_type": "calculated", "sort_order": 31,
     "description": "Page 3 Column 5 - Shareholder's Adjustment(s) (Addition / Subtraction)",
     "calculation": "Column 4 x (Line 13 or Line 14 on the Total line)",
     "source_rules": ["R-MO20S-PG3"],
     "destination_form": "MO-1040 (addition to or subtraction from federal AGI); MO-NRS Part 2 Column (d)",
     "notes": "⭐ The per-shareholder copy must be REDACTED of other shareholders' SSNs and percentages."},
    {"line_number": "MSS-1", "line_type": "input", "sort_order": 40,
     "description": "MO-MSS Part 1 Line 1 - Amount of receipts in Missouri",
     "source_rules": ["R-MO20S-MSS"]},
    {"line_number": "MSS-2", "line_type": "input", "sort_order": 41,
     "description": "MO-MSS Part 1 Line 2 - Amount of total receipts everywhere",
     "source_rules": ["R-MO20S-MSS"],
     "notes": ("⚠ DENOMINATOR EXCLUSION: 'receipts from hedging transactions or from the maturity, "
               "redemption, sale, exchange, loan, or other disposition of cash or securities ... must "
               "not be included in either the numerator or denominator of the receipts factor.'")},
    {"line_number": "MSS-3", "line_type": "calculated", "sort_order": 42,
     "description": ("MO-MSS Part 1 Line 3 - Receipts Factor. Divide Line 1 by Line 2. Enter on Form "
                     "MO-NRS, Parts 1 and 2, Column (c)."),
     "calculation": "Line 1 / Line 2", "source_rules": ["R-MO20S-MSS"],
     "destination_form": "MO-NRS Parts 1 and 2 Column (c); MO-NRP Column (c) when Part 3 is not used",
     "notes": ("⚠ The face cites 143.455.2, which is the APPLICABILITY subsection. The receipts factor "
               "is 143.455.10 and sourcing is .11/.12 (defect #1). ⭐ This same line is what a "
               "PARTNERSHIP borrows for MO-NRP Column (c) -- deliberately, per 12 CSR 10-2.255(3).")},
    {"line_number": "MSS-7", "line_type": "input", "sort_order": 43,
     "description": "MO-MSS Part 1 Line 7 - Net Short-Term Capital Gain (Loss), nonapportionable",
     "source_rules": ["R-MO20S-THROWBK"],
     "notes": ("⚠ N12 / U10: ONLY SHORT-TERM capital gain is enumerated. There is NO LONG-TERM ROW, "
               "although 143.455.7 allocates capital gains generally. 'If you have nonapportionable "
               "income pertaining to distributive share items not listed below, attach a table "
               "similar to the one below for the distributive share item.' -> long-term allocation "
               "rides on an UNSTRUCTURED ATTACHMENT. RED-DEFER R4.")},
    {"line_number": "MSS-10", "line_type": "subtotal", "sort_order": 44,
     "description": "MO-MSS Part 1 Line 10 - Total of each of the four nonapportionable columns",
     "calculation": "column totals for Gross Income (1) Everywhere, (2) Missouri; Related Expenses (3) Everywhere, (4) Missouri",
     "source_rules": ["R-MO20S-THROWBK"]},
    {"line_number": "NRS-P1-B", "line_type": "calculated", "sort_order": 50,
     "description": "MO-NRS Part 1 Column (b) - Missouri Source",
     "calculation": "(b) = (a) x (c)   ⚠⚠ THE REVERSE of MO-NRP's (c) = (b) / (a)",
     "source_rules": ["R-MO20S-NRS"]},
    {"line_number": "NRS-P1-E", "line_type": "calculated", "sort_order": 51,
     "description": "MO-NRS Part 1 Column (e) - the shareholder's Missouri-source share",
     "calculation": "(e) = (d) x (c)", "source_rules": ["R-MO20S-NRS"],
     "destination_form": "Form MO-NRI",
     "notes": ("⚠ 'These amounts must be adjusted by any capital gain or passive loss limitation as "
               "required' -- an unstated IRC 1211 / 469 step inherited by the individual module.")},
    {"line_number": "NRS-P1-11", "line_type": "input", "sort_order": 52,
     "description": "MO-NRS Part 1 Line 11 - Section 179 deduction",
     "source_rules": ["R-MO20S-DEPR"],
     "notes": ("⭐ IRC 179 as a DISTRIBUTIVE SHARE ITEM, never a Missouri modification -- the second of "
               "three such appearances in the lane. ⚠ EXCLUDED from the withholding base by the DOR's "
               "'Lines 1 through 10' (U9).")},
    {"line_number": "NR-1NR-2", "line_type": "total", "sort_order": 60,
     "description": "Form MO-1NR Line 2 - Total Missouri income tax withheld (total of all MO-2NRs)",
     "calculation": "sum of Form MO-2NR Line 2 across all in-scope shareholders",
     "source_rules": ["R-MO20S-WH", "R-MO20S-WHBASE"]},
    {"line_number": "NR-2NR-2", "line_type": "calculated", "sort_order": 61,
     "description": "Form MO-2NR Line 2 - Missouri Income Tax Payment",
     "calculation": "4.7% (0.047) x Line 1, or per the Missouri withholding tables with a Form MO W-4",
     "source_rules": ["R-MO20S-WH"],
     "destination_form": "MO-1040 LINE 39"},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM MO_1120S -- DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════════════════
MO1120S_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_MO20S_TITLE_LIES", "severity": "info",
     "title": "Form MO-1120S computes NO tax, despite being titled an income tax return",
     "condition": "any MO-1120S is prepared",
     "message": ("Section 143.471.1, RSMo: 'An S corporation, as defined by Section 1361(a)(1) of the "
                 "Internal Revenue Code, shall not be subject to the taxes imposed by section "
                 "143.071, or other sections imposing income tax on corporations.' Form MO-1120S is a "
                 "modification-and-allocation return exactly like Form MO-1065. The only "
                 "tax-computing return in the Missouri pass-through lane is Form MO-PTE."),
     "notes": "The S corporation must still register for a Missouri Tax I.D. Number."},
    {"diagnostic_id": "D_MO20S_MSS_REQUIRED", "severity": "warning",
     "title": "Question 3 is Yes - Form MO-MSS is required",
     "condition": "question 3 is Yes",
     "message": ("'If Yes, complete and attach Form MO-MSS.' The Line 3 receipts factor lands in "
                 "MO-NRS Parts 1 and 2, Column (c). ⚠ Column (c) is a VECTOR indexed by "
                 "distributive-share line, not a single figure: where an item is wholly or partly "
                 "allocated as nonapportionable income, 'a different percentage will be computed for "
                 "the item'."),
     "notes": "⚠ MO-1065 has no equivalent question. Partnerships borrow this same schedule."},
    {"diagnostic_id": "D_MO_MILEAGE_NOTE_DEFECT", "severity": "info",
     "title": "⚠ The 'Method Three - Six' mileage note is defective for TWO methods, not one",
     "condition": "apportionment Method Three, Four, Five or Six is selected",
     "message": ("The printed note 'Complete mileage information below for Method Three - Six' "
                 "misdescribes TWO methods. Section 143.455.14 (Method Three - Transportation) is a "
                 "GROSS-EARNINGS reporting rule: 'shall report its gross earnings within the state on "
                 "intrastate business and shall also report its gross earnings on all interstate "
                 "business done in this state... This subsection shall not apply to a railroad.' "
                 "Section 143.455.16 (Method Five - Interstate Bridge) is a flat rule: 'shall include "
                 "in its Missouri taxable income ONE-HALF of the net income from the operation of a "
                 "bridge between this and another state.' ONLY Method Four (143.455.15, railroad) and "
                 "Method Six (143.455.17, telephone and telegraph) are mileage-driven, and each also "
                 "offers an elective investment ratio."),
     "notes": ("Campaign D-12 C11 -- the brief's own correction C3 was itself wrong and had to be "
               "restated BEFORE propagating to mo_conformity.md. Corroborated by 12 CSR "
               "10-2.045(14)(B).")},
    {"diagnostic_id": "D_MO_METHOD_DEFERRED", "severity": "error",
     "title": "Apportionment Methods Three through Seven are RED-DEFERRED (R4)",
     "condition": "an apportionment method other than Two A is selected",
     "message": ("This product computes Method Two A (receipts factor) only. Prepare Methods Three "
                 "through Seven manually: Three - transportation gross earnings (143.455.14); Four - "
                 "railroad mileage or the elective investment ratio (143.455.15); Five - one-half of "
                 "interstate bridge net income (143.455.16); Six - telephone and telegraph mileage or "
                 "the elective investment ratio (143.455.17); Seven - broadcasters under 12 CSR "
                 "10-2.260 or another approved method (143.455.13(1) and (2)). Build Line 3 as a live "
                 "direct-entry percentage so the downstream arithmetic is right the day a method "
                 "lands. Also prepare manually any LONG-TERM capital gain allocated as "
                 "nonapportionable income -- Form MO-MSS enumerates only a short-term row."),
     "notes": "R4. ⚠ Entities defined as a broadcaster under 12 CSR 10-2.260 MUST choose Method Seven."},
    {"diagnostic_id": "D_MO_METHOD7_PETITION", "severity": "info",
     "title": "Method Seven's petition deadline closed 60 days BEFORE year end - advisory only",
     "condition": "Method Seven is selected or contemplated",
     "message": ("A petition for alternative apportionment must be filed with the director AT LEAST "
                 "SIXTY DAYS BEFORE THE END OF THE TAX YEAR to which it is sought to apply (12 CSR "
                 "10-2.076(2)(G); section 143.455.13(2), RSMo), by e-mailing the petition to "
                 "pteincome@dor.mo.gov, with a seven-item content list including a Form 2827 power of "
                 "attorney. BY THE TIME THIS RETURN IS PREPARED THE WINDOW HAS ALREADY CLOSED. This "
                 "is advice for NEXT year, not a filing-time gate."),
     "notes": ("⚠ Brief 22 correction #10: the deadline is in the REGULATION, so it binds all three "
               "lanes -- the observation that the MO-1120S / MO-MSS Method Seven text omits it is "
               "itself a DOR defect. That STRENGTHENS the advisory, and it stays advisory.")},
    {"diagnostic_id": "D_MO20S_WH_SUBSET_LINES", "severity": "warning",
     "title": "⚠ MO-NRS Lines 5b, 8b or 8c are non-zero - the printed withholding base double-counts",
     "condition": "MO-NRS Part 1 line 5b, 8b or 8c carries an amount",
     "message": ("Form MO-1NR defines the S-corporation withholding base as 'the net total of the "
                 "amounts listed on Lines 1 through 10 of ... Form MO-NRS'. Summed literally that "
                 "DOUBLE-COUNTS: Line 5b (Qualified dividends) is a SUBSET of Line 5a (Ordinary "
                 "dividends), and Lines 8b (Collectibles 28% gain) and 8c (Unrecaptured section 1250 "
                 "gain) are both SUBSETS of Line 8a (Net long-term capital gain). This return "
                 "suppresses the subset lines and computes the base without them. REVIEW THE WITHHELD "
                 "AMOUNT BEFORE FILING -- this determines cash withheld."),
     "notes": ("U9 / campaign D-12 Group D. Get a DOR worked example before season. The instruction "
               "also excludes Line 11 (IRC 179) and Lines 12a-12e without saying so.")},
    {"diagnostic_id": "D_MO20S_NO_COMPOSITE_BOX", "severity": "info",
     "title": "VERIFIED NEGATIVE: MO-1120S has no composite checkbox, though the statute allows one",
     "condition": "a composite election is contemplated for an S corporation",
     "message": ("Section 143.471.5, RSMo grants S corporations the same composite right as "
                 "partnerships, and the MO-1120S instructions list composite election as a "
                 "withholding exception -- but FORM MO-1120S HAS NO COMPOSITE CHECKBOX, while Form "
                 "MO-1065 does. Where and how an S corporation makes the election is unstated."),
     "notes": "N11 / U23 -- settle by Form 5677 (the composite instructions) and 12 CSR 10-2.190."},
    {"diagnostic_id": "D_MO20S_8886_MANDATORY", "severity": "warning",
     "title": "Federal Form 8886 copies are MANDATORY with MO-1120S",
     "condition": "any Federal Form 8886 was filed with the federal return",
     "message": ("'Every corporation must include with the Missouri return a copy of EACH Federal "
                 "Form 8886 that was filed with the IRS as part of its federal return.' There is no "
                 "MO-1065 or MO-PTE analogue of this requirement."),
     "notes": "⚠ Federal Form 8886 is MANDATORY on MO-1120S alone (N15 context)."},
    {"diagnostic_id": "D_MO20S_REDACTED_EXTRACT", "severity": "warning",
     "title": "The per-shareholder extract must be REDACTED - no MO-1065 counterpart",
     "condition": "the shareholder extract package is generated",
     "message": ("'On or before the due date (including extensions) of the MO-1120S, furnish a copy of "
                 "(or extract of all relevant information from) the Form MO-1120S to each "
                 "shareholder, BUT WITH INFORMATION ABOUT OTHER SHAREHOLDERS, SUCH AS SOCIAL SECURITY "
                 "NUMBERS OR SHARE PERCENTAGES, REMOVED OR REDACTED.' The print engine must emit a "
                 "per-shareholder redacted variant of Page 3."),
     "notes": "Form MO-1065 has no equivalent redaction sentence."},
    {"diagnostic_id": "D_MO_BTC_BANK_CREDIT", "severity": "error",
     "title": "Bank Tax Credit for S Corporations (BTC) - prepare manually (R6)",
     "condition": "the S corporation is a bank, bank holding company, S&L or credit institution",
     "message": ("A pro rata share of the Chapter 148 tax is allowed as a CREDIT to qualifying "
                 "shareholders under sections 143.471.10 through .12, RSMo, allocated by stock "
                 "ownership, carried forward the lesser of five years or until used, and required to "
                 "be used AS SOON AS the shareholder has Missouri taxable income. Attach Form BTC, "
                 "INT-3, 2823 or INT-2. This product does not compute it."),
     "notes": "⚠ It is a CREDIT (alpha code BTC on Form MO-TC), not a modification."},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM MO_1120S -- TEST SCENARIOS
# ═══════════════════════════════════════════════════════════════════════════
MO1120S_SCENARIOS: list[dict] = [
    {"scenario_name": "MO-1120S computes ZERO tax however large the adjustment", "scenario_type": "normal",
     "inputs": {"L5": 900000, "L12": 100000},
     "expected_outputs": {"L13": 800000, "L14": 0, "tax_liability": 0},
     "notes": "143.471.1 -- an S corporation is not subject to 143.071. The title lies.", "sort_order": 1},
    {"scenario_name": "MO-1120S subtraction range is Lines 6-11, NOT MO-1065's 6-9",
     "scenario_type": "edge",
     "inputs": {"L6": 1000, "L7": 200, "L8": 5000, "L9": 300, "L10": 400, "L11": 100},
     "expected_outputs": {"L12": 7000},
     "notes": ("⚠ MO-1120S carries a MOHELA line and TWO depreciation lines that MO-1065 does not, so "
               "the totals ranges differ. Sharing one summation rule across the two forms drops "
               "$5,500 here."),
     "sort_order": 2},
    {"scenario_name": "MO-1120S Line 15 stays OUTSIDE the totals and carries no cite on the face",
     "scenario_type": "edge",
     "inputs": {"L5": 10000, "L12": 4000, "l15_agriculture_disaster_relief": 25000},
     "expected_outputs": {"L12": 4000, "L13": 6000, "L15": 25000, "l15_in_totals": False,
                          "face_spelling": "Agriculture Disaster Relief",
                          "statutory_cite_on_face": None},
     "notes": ("⚠ On MO-PTE the same statute's line (Line 10) is INSIDE the subtraction total and the "
               "face spells it `Agricultural`. MO-1065 L13 and MO-NRS Part 2 L15 DO print the cite; "
               "this face does not."),
     "sort_order": 3},
    {"scenario_name": "MO-MSS PER-ITEM PERCENTAGE - the DOR's own six-step worked example",
     "scenario_type": "normal",
     "inputs": {"item_total": 15000, "nonapportionable_everywhere": 3000,
                "nonapportionable_missouri": 1000, "receipts_factor_pct": 33.333},
     "expected_outputs": {"apportionable": 12000, "apportioned": 4000, "col_b": 5000,
                          "col_c_pct": 33.333},
     "notes": ("⚠⚠ THE PERCENTAGE IS PER-ITEM. 'If a distributive share item is wholly or partially "
               "allocated as nonapportionable income, a different percentage will be computed for the "
               "item.' MO-NRS Column (c) is a VECTOR. A scalar model is wrong."),
     "sort_order": 4},
    {"scenario_name": "MO-NRS derives (b) FORWARD from (c) - the REVERSE of MO-NRP",
     "scenario_type": "edge",
     "inputs": {"col_a_everywhere": 20000, "col_c_pct_from_mo_mss": 80.0,
                "col_d_shareholder_k1": 12000},
     "expected_outputs": {"col_b": 16000, "col_e": 9600,
                          "derivation": "(b) = (a) x (c);  (e) = (d) x (c)"},
     "notes": ("⚠⚠ MO-NRP computes (c) = (b) / (a) from a KNOWN Missouri figure; MO-NRS computes (b) "
               "FROM a supplied percentage. The numbers coincide here only because the example was "
               "chosen to make the contrast visible. DO NOT SHARE A RULE."),
     "sort_order": 5},
    {"scenario_name": "MO-NRS WITHHOLDING BASE - 5b / 8b / 8c are SUPPRESSED, not summed",
     "scenario_type": "failure",
     "inputs": {"part1_column_e": {"1": 200000, "2": 0, "3": 0, "4": 3000, "5a": 10000,
                                   "5b": 8000, "6": 0, "7": 1000, "8a": 40000, "8b": 12000,
                                   "8c": 9000, "9": 0, "10": 0}},
     "expected_outputs": {"base": 254000, "literal_sum_would_be": 283000,
                          "overstatement_avoided": 29000, "requires_human_review": True},
     "notes": ("A literal 'Lines 1 through 10' sum overstates the base by 5b + 8b + 8c = $29,000, "
               "which at 4.7% is $1,363 of over-withholding on ONE shareholder. THIS DETERMINES "
               "CASH. (U9)"),
     "sort_order": 6},
    {"scenario_name": "MO-1120S C11 - Method Three is GROSS EARNINGS, Method Five is FLAT ONE-HALF",
     "scenario_type": "edge",
     "inputs": {"methods": ["3", "4", "5", "6"]},
     "expected_outputs": {"mileage_driven": ["4", "6"],
                          "note_defective_for": ["3", "5"],
                          "basis_3": "gross_earnings", "basis_5": "flat_one_half"},
     "notes": ("Campaign D-12 C11. The brief's own correction C3 said only Five was wrong; the "
               "verification pass proved THREE is wrong too. A checking pass is not self-validating."),
     "sort_order": 7},
    {"scenario_name": "MO-1120S question 3 gates Form MO-MSS - MO-1065 has no such question",
     "scenario_type": "normal",
     "inputs": {"q1_has_modifications": True, "q2_has_nonresident_shareholders": True,
                "q3_income_outside_missouri": True},
     "expected_outputs": {"required_schedules": ["MO-NRS (one per nonresident shareholder)",
                                                 "MO-MSS"]},
     "notes": ("⭐ The apportionment gate exists ONLY on the S-corporation return. Partnerships have "
               "no such question and BORROW MO-MSS -- deliberately, per 12 CSR 10-2.255(3)."),
     "sort_order": 9},
    {"scenario_name": "MO-1120S $500 EXPENSE FLOOR behaves identically to MO-1065's",
     "scenario_type": "edge",
     "inputs": {"l2a_state_local_bond_interest": 7000, "l2b_related_expenses": 499},
     "expected_outputs": {"L2": 7000, "expense_applied": 0, "expense_dropped_by_floor": True},
     "notes": ("Same substance on all three faces, but TRANSCRIBE EACH FACE'S OWN WORDING -- MO-1120S "
               "prints 'if less than $500, enter zero' where MO-PTE prints 'enter $0'."),
     "sort_order": 10},
    {"scenario_name": "MO-1120S THROWBACK-STYLE allocation - rules (d)(2) and (g)(2) survive",
     "scenario_type": "edge",
     "inputs": {"allocation_rules": ["a", "b", "c", "d", "e", "f", "g"]},
     "expected_outputs": {"throwback_style": ["d", "g"], "receipts_factor_has_throwback": False},
     "notes": ("⭐ CONFIRMED VERBATIM on the statute AND on all three apportionment forms: the "
               "receipts factor has NO throwback, but (d)(2) (capital gains from TPP) and (g)(2) "
               "(patent and copyright royalties) are throwback-style tests keyed to commercial "
               "domicile PLUS non-taxability elsewhere. They require a 'not taxable in the situs "
               "state' determination, which P.L. 86-272 can defeat."),
     "sort_order": 11},
    {"scenario_name": "MO-1120S per-shareholder extract must be REDACTED (no MO-1065 analogue)",
     "scenario_type": "edge",
     "inputs": {"shareholder_count": 4},
     "expected_outputs": {"extracts_generated": 4, "redacted": True,
                          "redacted_fields": ["other shareholders' social security numbers",
                                              "other shareholders' share percentages"]},
     "notes": ("'...furnish a copy of (or extract of all relevant information from) the Form MO-1120S "
               "to each shareholder, BUT WITH INFORMATION ABOUT OTHER SHAREHOLDERS, SUCH AS SOCIAL "
               "SECURITY NUMBERS OR SHARE PERCENTAGES, REMOVED OR REDACTED.' Form MO-1065 has no "
               "equivalent sentence, so the print engine needs a per-shareholder variant HERE and "
               "not there."),
     "sort_order": 12},
    {"scenario_name": "MO-1120S EXTENSION - build to the face, not to MO-7004's MO-60 pointer",
     "scenario_type": "edge",
     "inputs": {"form_code": "MO_1120S"},
     "expected_outputs": {"missouri_form": None, "federal_form_attached": "Form 7004",
                          "extension_extends_payment": False, "max_months": 6},
     "notes": ("⚠ THREE-WAY CONTRADICTION (U24): MO-7004 says use MO-60; MO-60 has no S-corp checkbox "
               "and says use the federal 7004; MO-1120S names no Missouri form. Build to the return's "
               "own face, per D-10's principle."),
     "sort_order": 13},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM MO_PTE -- FACTS
# ⭐ THE ONLY TAX-COMPUTING RETURN IN THE MISSOURI PTE LANE -- and the one that
# CANNOT BE E-FILED. Includes the MS-* (Form MO-MS PTE) and BD-* (Schedule
# PTE-BD) computing sub-specs, per campaign D-12 Group B.
# ═══════════════════════════════════════════════════════════════════════════
MOPTE_FACTS: list[dict] = [
    {"fact_key": "mopte_entity_type", "label": "Select type of entity (select one)",
     "data_type": "choice", "choices": ["S Corporation", "Partnership"], "required": True,
     "sort_order": 1,
     "notes": "Drives the Line 1 federal feed and Schedule PTE-BD Line 4 (partnerships only)."},
    {"fact_key": "mopte_election_box",
     "label": ("Select this box if you are electing to become an Affected Business Entity and consent "
               "to become subject to the tax imposed by Section 143.436, RSMo"),
     "data_type": "boolean", "required": True, "sort_order": 2,
     "notes": ("⭐ THE ELECTING INSTRUMENT AND THE WHOLE POINT OF THE FORM. 'A SEPARATE ELECTION MUST "
               "BE MADE FOR EACH TAX YEAR' and, once made, 'the election CANNOT BE REVOKED for that "
               "tax year'. Available 'for tax years ending on or after December 31, 2022' "
               "(143.436.14). ⚠ 12 CSR 10-2.436(2): the election IS NOT EFFECTIVE without a "
               "designated Affected Business Entity Representative -- see mopte_abe_representative.")},
    {"fact_key": "mopte_optout_box",
     "label": ("Select this box if you have member(s) making an opt-out election. Attach Federal K-1 "
               "for each opt-out member."),
     "data_type": "boolean", "sort_order": 3,
     "notes": ("⚠⚠ THE OPT-OUT IS A RETURN-LEVEL RECOMPUTATION MODE, NOT A MEMBER FLAG (campaign "
               "D-12 Group D). 12 CSR 10-2.436(12)(D) forces a full recomputation of Line 1, every "
               "modification, Schedule PTE-BD and the credit split AS THOUGH THE OPT-OUT MEMBER'S "
               "ITEMS DID NOT EXIST. Line 1 verbatim: 'Form MO-PTE, Line 1 must not include any items "
               "of income or deduction allocable to an opt-out member.' Line 6 verbatim: 'remove from "
               "the computation any opt-out member(s)' allocable items.'")},
    {"fact_key": "mopte_abe_representative",
     "label": "Affected Business Entity Representative designated (Form 2827 or Form 2827 PTE)",
     "data_type": "boolean", "required": True, "sort_order": 4,
     "notes": MO_ABE_REP_VERBATIM},
    {"fact_key": "mopte_abe_redesignation_box",
     "label": ("Select here if the pass-through entity is re-designating the same Affected Business "
               "Entity Representative as was used in the prior tax year"),
     "data_type": "boolean", "sort_order": 5,
     "notes": ("⚠ 'DO NOT SELECT THIS BOX UNLESS a person signing the return has been given "
               "authority, by the pass-through entity, to designate an affected business entity "
               "representative for the pass-through entity for this tax year.' 12 CSR 10-2.436(5)(D) "
               "adds that the prior-year representative may check it to re-designate HIMSELF OR "
               "HERSELF only with that authority.")},
    {"fact_key": "mopte_box_federal_extension",
     "label": "Select this box if you have an approved federal extension (attach Federal Form 7004)",
     "data_type": "boolean", "sort_order": 6,
     "notes": ("⚠ MO-PTE ALSO HAS ITS OWN MISSOURI EXTENSION FORM -- Form MO-7004 carries a "
               "`Pass-Through Entity Income Tax Return, Form MO-PTE` checkbox and routes to P.O. Box "
               "3080. ⭐⭐ AND THE PAYMENT RULE IS INVERTED FOR MO-PTE ONLY: the extension EXTENDS THE "
               "TIME TO PAY (no 5% addition) but INTEREST RUNS FROM THE ORIGINAL DUE DATE.")},
    {"fact_key": "mopte_box_amended", "label": "Amended Return", "data_type": "boolean", "sort_order": 7,
     "notes": ("⚠⚠ 'The pass-through entity must COMPLETE THE ENTIRE RETURN USING THE CORRECTED "
               "FIGURES. ... Failure to fill out the entire return will delay the processing.' AND "
               "THE MEMBER-FACING CONSEQUENCE: 'AN AMENDED RETURN REDUCING PASS-THROUGH ENTITY INCOME "
               "TAX LIABILITY MAY RESULT IN A REDUCTION OR ELIMINATION OF PTE TAX CREDITS FOR ALL "
               "MEMBERS.' An entity-level amendment cascades into every member's already-filed "
               "MO-1040. RED-DEFER R7.")},
    {"fact_key": "mopte_l1_sum_702a_1366",
     "label": "1. Sum of separately and nonseparately computed items",
     "data_type": "decimal", "required": True, "sort_order": 10,
     "notes": ("IRC 702(a) for partnerships, IRC 1366 for S corporations. THE TWO FEDERAL FEEDS, "
               "verbatim: 'For S corporations, enter the amount from FEDERAL FORM 1120S, SCHEDULE K, "
               "LINE 18. For partnerships, enter the amount from federal Form 1065, PAGE 6, ANALYSIS "
               "OF NET INCOME (LOSS), LINE 1.' ⚠ ESCAPE HATCH: 'If the sum ... differs from the "
               "amount calculated using the instructions above, enter on Line 1 the sum ... as "
               "described in Internal Revenue Code Sections 702(a) ... or 1366 ..., and ATTACH A "
               "DETAILED EXPLANATION, WITH CALCULATIONS.' ⚠ OPT-OUT: 'Form MO-PTE, Line 1 must not "
               "include any items of income or deduction allocable to an opt-out member.' "
               + MO_FEDERAL_LINE_STAMP)},
    {"fact_key": "mopte_a1a_state_local_income_taxes",
     "label": "Part A 1a. State and local income taxes deducted on Federal Form 1120S or 1065",
     "data_type": "decimal", "sort_order": 20,
     "notes": ("143.141(1) and (2); 12 CSR 10-2.160. ⚠ 'This may include, but not be limited to, a "
               "state's elective pass-through entity income tax.'")},
    {"fact_key": "mopte_a1b_city_earnings_taxes",
     "label": "Part A 1b. Kansas City & St. Louis earnings taxes. Enter Line 1a minus Line 1b on Line 1.",
     "data_type": "decimal", "sort_order": 21, "notes": MO_CITY_EARNINGS_TAX_NOTE},
    {"fact_key": "mopte_a2a_state_local_bond_interest",
     "label": "Part A 2a. State and local bond interest (except Missouri)",
     "data_type": "decimal", "sort_order": 22, "notes": "143.121.2(2)"},
    {"fact_key": "mopte_a2b_related_expenses",
     "label": "Part A 2b. Related expenses (omit if less than $500). Enter Line 2a minus Line 2b on Line 2.",
     "data_type": "decimal", "sort_order": 23,
     "notes": "⚠ A FLOOR ON THE EXPENSE: 'The expenses must equal or exceed $500. If less than $500, enter $0.'"},
    {"fact_key": "mopte_a3_other_additions",
     "label": "Part A 3. Partnership / Fiduciary / Other adjustments -- ADDITION",
     "data_type": "decimal", "sort_order": 24,
     "notes": ("⚠⚠ 'Enter the share of fiduciary and partnership adjustment as shown on Form MO-1041, "
               "Page 2, Part 1, LINE 19, and FORM MO-1065, LINE 11 (Section 143.121.4 and 5, RSMo). "
               "COPIES OF ANY FORMS MO-1041 OR MO-1065 MUST BE ATTACHED.' STRUCTURAL PROOF THAT "
               "MO-PTE IS FILED IN ADDITION TO MO-1065, NOT INSTEAD OF IT.")},
    {"fact_key": "mopte_a4_163j_carryforward",
     "label": "Part A 4. Business interest expense carryforward",
     "data_type": "decimal", "sort_order": 25,
     "notes": ("143.121.2(6). ⭐ ITS OWN LINE ON MO-PTE; buried in Line 3 by instruction on MO-1120S; "
               "ABSENT ENTIRELY FROM MO-1065 (N7 / U7). ⚠ THERE IS NO FOOD PANTRY ADD-BACK ON MO-PTE "
               "(N6), so an electing entity's Line 1 base RETAINS a federal deduction that the "
               "non-electing returns add back.")},
    {"fact_key": "mopte_a6a_exempt_federal_obligations",
     "label": "Part A 6a. Interest from exempt federal obligations",
     "data_type": "decimal", "sort_order": 26,
     "notes": ("143.121.3(1); 12 CSR 10-2.150. 'A detailed list showing the amount of monies received "
               "or the percentage of funds received from direct U.S. Government obligations must be "
               "attached to Form MO-PTE.'")},
    {"fact_key": "mopte_a6b_related_expenses",
     "label": "Part A 6b. Related expenses (omit if less than $500). Enter Line 6a minus Line 6b on Line 6.",
     "data_type": "decimal", "sort_order": 27},
    {"fact_key": "mopte_a7_state_refund",
     "label": ("Part A 7. Amount of the state income tax refund(s) included in the sum of separately "
               "and nonseparately computed items"),
     "data_type": "decimal", "sort_order": 28, "notes": "143.121.3(5)"},
    {"fact_key": "mopte_a8_mohela",
     "label": "Part A 8. Federally taxable - Missouri exempt obligations",
     "data_type": "decimal", "sort_order": 29,
     "notes": ("⭐ THE MOST DETAILED OF THE THREE MOHELA INSTRUCTIONS: '...any proceeds resulting from "
               "redemption, maturity, or sale of a bond issued by the Missouri Higher Education Loan "
               "Authority (MOHELA), as well as any interest on such bond, but only to the extent such "
               "amount was included in determining the sum ... on Form MO-PTE, Line 1. IN THE EVENT "
               "THAT PROCEEDS WERE RECEIVED FROM THE SALE OF SUCH A BOND, THE TAX-EXEMPT PROCEEDS ARE "
               "LIMITED TO THE EXTENT OF THE HOLDER'S COST OF ACQUISITION. ... see Section 173.440, "
               "RSMo.' ⚠ MO-1065 has no MOHELA line at all (N8).")},
    {"fact_key": "mopte_a9_other_subtractions",
     "label": ("Part A 9. Partnership / Fiduciary / Build America and Recovery Zone Bond Interest / "
               "Missouri Public-Private Transportation Act / Other adjustments -- SUBTRACTION"),
     "data_type": "decimal", "sort_order": 30,
     "notes": ("Sources MO-1041 Page 2 Part 1 LINE 20 and MO-1065 LINE 12; Build America / Recovery "
               "Zone (108.1020); Public-Private Transportation Act (227.646). ⚠⚠ TWO ITEMS APPEAR IN "
               "THE INSTRUCTION BUT ARE NOT NAMED ON THE FACE -- the MARIJUANA (280E) deduction "
               "('exclusively limited to taxpayers authorized to do business under Article XIV of "
               "Missouri's Constitution', submit the financial statement, schedules and MED number) "
               "and the BROADBAND GRANT ('Do not duplicate this subtraction if the same grant "
               "subtraction was already included in the fiduciary or partnership adjustments'). BOTH "
               "must go through the `Other adjustments` write-in WITH A HAND-TYPED DESCRIPTION; the "
               "engine must supply the description string because THE DOR PRINTS NO CODE. ⚠⚠ AND THIS "
               "WRITE-IN IS THE ONLY ROUTE ONTO MO-PTE for a live 143.121.3(7)/(9) depreciation "
               "residual (N5 / U18) and for the 143.121.2(4) NOL addition (U28) -- neither the form "
               "nor the instructions say so.")},
    {"fact_key": "mopte_a10_agricultural_disaster_relief",
     "label": "Part A 10. Agricultural Disaster Relief",
     "data_type": "decimal", "sort_order": 31,
     "notes": ("143.121.3(10); 'attach a copy of any Form 1099 indicating your agricultural payment'. "
               "⭐⭐ INSIDE THE LINE 12 SUBTRACTION TOTAL HERE -- it reduces the entity's tax base "
               "directly -- whereas on MO-1065 (Line 13) and MO-1120S (Line 15) it sits OUTSIDE the "
               "totals and is separately allocated to owners. SAME STATUTE, THREE PLACEMENTS, TWO "
               "BEHAVIOURS. ⚠ SPELLING: THIS FACE PRINTS `Agricultural`; the other two print "
               "`Agriculture`. Transcribe each face's own spelling.")},
    {"fact_key": "mopte_a11_163j_disallowed",
     "label": "Part A 11. Disallowed business interest expense",
     "data_type": "decimal", "sort_order": 32,
     "notes": ("143.121.3(11). ⭐ ITS OWN LINE ON MO-PTE; folded into Line 9 by instruction on "
               "MO-1120S; ABSENT from MO-1065 (N7).")},
    {"fact_key": "mopte_l6_bid",
     "label": "6. Missouri Business Income Deduction - Attach Schedule PTE-BD",
     "data_type": "decimal", "sort_order": 40,
     "notes": ("'Pursuant to Section 143.436, RSMo, pass-through entities determine the Missouri "
               "business income deduction that \"would be allowable to the owners under\" the Missouri "
               "business income deduction statute (Section 143.022, RSMo). THIS HYPOTHETICAL "
               "DETERMINATION IS MADE AT THE PASS-THROUGH ENTITY-LEVEL. ... THE RESULTING DEDUCTION "
               "MAY BE MORE OR LESS THAN THE AGGREGATE AMOUNT OF THE MISSOURI BUSINESS INCOME "
               "DEDUCTION ACTUALLY ALLOWED TO ALL OWNERS.' ⚠ Opt-out: 'remove from the computation any "
               "opt-out member(s)' allocable items.'")},
    {"fact_key": "mopte_l7_lower_tier",
     "label": ("7. Aggregate distributive share of Missouri net income (loss) from lower-tier "
               "affected business entities"),
     "data_type": "decimal", "sort_order": 41,
     "notes": ("⭐ SIGNED, AND LINE 9 SUBTRACTS IT: a POSITIVE Line 7 REMOVES lower-tier income and a "
               "NEGATIVE Line 7 ADDS BACK lower-tier loss -- exactly 143.436.5(1). Verbatim: 'IF THIS "
               "SUM IS NEGATIVE, ENTER A NEGATIVE FIGURE ON LINE 7. Attach a copy of the Missouri "
               "pass-through entity tax reports sent to the affected business entity ... from all "
               "lower-tier affected business entities pertaining to this tax year.'")},
    {"fact_key": "mopte_l8_prior_year_loss",
     "label": "8. Missouri net loss to be used from affected business entity's prior tax year(s)",
     "data_type": "decimal", "sort_order": 42,
     "notes": ("⭐ THE FLOOR RULE, verbatim: 'DO NOT USE AN AMOUNT OF MISSOURI NET LOSS FROM A PRIOR "
               "TAX YEAR TO REDUCE THE MISSOURI NET INCOME BELOW $0 FOR THIS TAX YEAR. If the amount "
               "to be reported on Line 9 would be $0 or below zero without utilizing any Missouri net "
               "loss carryforward from a prior tax year, ENTER $0 ON LINE 8.' ⚠ FIRST YEAR: 'This is "
               "not applicable for the affected business entity's first year filing Form MO-PTE. If "
               "it is the first year filing Form MO-PTE, enter $0.' ⚠ 'Do not include any amount ... "
               "that has already been carried forward and used'; 'attach a schedule showing the "
               "remaining loss balances from each tax year' -- A MAINTAINED CARRYFORWARD RECORD.")},
    {"fact_key": "mopte_l11_mo_tc_credits",
     "label": "11. Tax Credits - Attach Form MO-TC (from Form MO-TC, Line 13)",
     "data_type": "decimal", "sort_order": 43,
     "notes": ("⚠⚠ THE CREDIT-POISONING RULE, verbatim: 'In general, MISCELLANEOUS TAX CREDITS REDUCE "
               "TAX LIABILITY UNDER THE SALT PARITY ACT, RATHER THAN CONSTITUTING TAX PAID, and "
               "therefore DO NOT QUALIFY AS PAYMENTS for purposes of calculating the PTE credit for a "
               "member.' USING AN ENTITY-LEVEL CREDIT DESTROYS THE MEMBERS' CREDIT, and the form has "
               "NO FIELD FOR TAX ACTUALLY PAID. A HARD diagnostic fires whenever this is greater than "
               "zero. (campaign D-12 C5 / U20)")},
    {"fact_key": "mopte_cash_payments_applied",
     "label": "⭐ DERIVED - cash and credited payments actually applied to the Line 12 liability",
     "data_type": "decimal", "sort_order": 44,
     "notes": ("⚠⚠ THIS FIELD DOES NOT EXIST ON THE FORM. It is DERIVED, and it feeds Part B Column 6, "
               "because the members' credit is the pro rata share of Line 12 'TO THE EXTENT PAID' and "
               "12 CSR 10-2.436(11) computes the credit on 'the tax actually paid'. An entity filing "
               "with a balance due, or paying late, has a credit pool that DOES NOT EQUAL Line 12. "
               "⚠ Whether the Line 13 excess REFUNDABLE credit counts as tax actually paid is "
               "UNANSWERED by the Department; this build does NOT count it and says so.")},
    {"fact_key": "mopte_l14_anticipated_payments",
     "label": "14. Anticipated tax payments (Form MO-PTEAP), including approved overpayments applied from 2024",
     "data_type": "decimal", "sort_order": 45,
     "notes": ("⚠ 'If the requested overpayment(s) credited from 2024 HAS BEEN ADJUSTED, YOU MUST USE "
               "THE ADJUSTED AMOUNT.' ⭐ ANTICIPATED PAYMENTS ARE NOT REQUIRED -- 12 CSR 10-2.436(7) "
               "states positively that there is no estimated-tax declaration or payment requirement, "
               "and MO-PTEAP's own face says 'These anticipated tax payments are not required.' THERE "
               "IS THEREFORE NO MO-2210 / FORM 500C ANALOGUE AND NO EXCEPTION LADDER (N2). ⚠ BUT "
               "interest under 143.731.2 and the 5% late-payment addition BOTH SURVIVE.")},
    {"fact_key": "mopte_l22_trust_fund_donations",
     "label": "22. Total Donation - Add amounts from Boxes 22a through 22n",
     "data_type": "decimal", "sort_order": 46,
     "notes": ("⚠ REAL FORM SURFACE, NOT DECORATION -- it sits INSIDE the refund arithmetic at Line "
               "23. Fourteen boxes with printed minimums ($1 or $2), plus TWO write-in slots. The "
               "additional fund codes are NON-CONTIGUOUS (01, 02, 03, 05, 07, 08, 09, 10, 14 -- codes "
               "04, 06, 11, 12 and 13 are NOT PUBLISHED), most capped at $200 with code 14 uncapped. "
               "HARD CAP OF TWO WRITE-INS: 'If you want to give to more than two additional funds, "
               "please submit a contribution directly to the fund.' And: 'If you file a balance due "
               "return and wish to contribute ... ATTACH A SEPARATE CHECK FOR THIS AMOUNT.'")},
    {"fact_key": "mopte_partb_member_roster",
     "label": "Part B member roster (15 rows a) through o) plus Total)",
     "data_type": "string", "sort_order": 50,
     "notes": ("'Name of each member. ALL MUST BE LISTED. Use an attachment if necessary.' ⚠ 15 ROWS "
               "-- MO-1065 and MO-1120S Page 3 have 19. SEVEN columns: 1 Name | 2 nonresident | ⭐ 3 "
               "Select if member has made an opt-out election | 4 SSN or FEIN | 5 Membership % | 6 "
               "Member's PTE Tax Credit | 7 Members not eligible for PTE Tax Credit. ⚠⚠ Column 1 "
               "collides with 105.1500 RSMo, printed on page 4 of this very form -- see "
               "mo_501c_roster_decision().")},
    {"fact_key": "mopte_partb_k1_percent",
     "label": "Part B Column 5 - the K-1 membership percentage (as printed on the federal K-1)",
     "data_type": "decimal", "sort_order": 51,
     "validation_rule": "two decimal places; the non-opt-out re-grossed total must foot to 100.00%",
     "notes": ("'Enter the percentage from Federal Form 1120S or 1065, Schedule K-1. If different "
               "percentages (e.g. for profit and capital) are listed on the same Schedule K-1 from a "
               "partnership, YOU MUST GENERALLY ENTER THE PROFIT PERCENTAGE if the beginning and "
               "ending profit percentages are the same. Round the percentage to the nearest TWO "
               "DECIMAL PLACES.' " + MO_FEDERAL_LINE_STAMP)},
    {"fact_key": "mopte_partb_credit_percent",
     "label": "⭐ Part B Column 5 - the RE-GROSSED-UP credit-allocation percentage (a SEPARATE field)",
     "data_type": "decimal", "sort_order": 52,
     "validation_rule": "two decimal places; = k1_percent / (100% - sum of opt-out percentages)",
     "notes": ("⚠⚠ NEVER OVERWRITE mopte_partb_k1_percent WITH THIS FIELD, OR VICE VERSA (campaign "
               "D-12 Group D). MO-PTE Part B Column 5 is LABELLED `Membership %` but prints THIS "
               "figure whenever any member has opted out, and it no longer matches ANY K-1. DOR's own "
               "worked example: an opt-out member at 30% and a participating member at 10% gives the "
               "participating member 14% (10 divided by 70). That is the unit test.")},
    {"fact_key": "mopte_ms_pte_method",
     "label": "MO-MS PTE Apportionment Election (2a / 3 / 4 / 5 / 6 / 7) -- PERSISTED on MO-PTE Line 5",
     "data_type": "choice", "choices": ["2a", "3", "4", "5", "6", "7"], "sort_order": 60,
     "notes": ("⭐ THE METHOD NUMBER IS PERSISTED ON THE RETURN, NOT JUST THE PERCENTAGE: MO-PTE Line 5 "
               "has TWO adjacent boxes, `Method` and `Percent`. ⚠ C11: the mileage note is defective "
               "for METHOD THREE (gross earnings) AND METHOD FIVE (flat one-half); only Four and Six "
               "are mileage-driven.")},
    {"fact_key": "mopte_ms_pte_has_nonapportionable",
     "label": "MO-MS PTE - the entity has nonapportionable income (Lines 4-9 are required)",
     "data_type": "boolean", "sort_order": 61,
     "notes": ("⚠⚠ U11 IS UNRESOLVED AND MUST NOT BE GUESSED. The MO-PTE instructions say complete "
               "Lines 4-9 'If the mileage percentage ... is APPLICABLE'; the MO-MSS / MO-1120S "
               "parallel text says '... is INAPPLICABLE'. THE SAME SENTENCE WITH THE OPPOSITE "
               "CONDITION, and no source resolves which is inverted. The MO-MSS reading is the more "
               "coherent one, but MO-MS PTE Line 9 exists PRECISELY to blend allocation into the "
               "percentage, so the PTE reading is not absurd. FLAG, DO NOT GUESS.")},
    {"fact_key": "mopte_ms_pte_l4_balance",
     "label": "MO-MS PTE Part 1 Line 4 - the balance from Form MO-PTE, Line 4",
     "data_type": "decimal", "sort_order": 62,
     "notes": ("⚠⚠ LINE 9 DIVIDES BY THIS, and the instructions expressly require the form 'EVEN IF "
               "THIS BALANCE IS ZERO OR NEGATIVE'. Zero -> division by zero; negative -> a percentage "
               "whose SIGN IS INVERTED relative to the intended allocation. Neither the form nor the "
               "instructions address either case. HARD RED, prepare manually. (U14 / D-12 Group D)")},
    {"fact_key": "mopte_bd_column_c",
     "label": "Schedule PTE-BD Column (C) - Portion of Column (B) from Missouri Sources (Lines 1-7)",
     "data_type": "decimal", "sort_order": 70,
     "notes": PTE_BD_COLUMN_C_RULE},
    {"fact_key": "mopte_bd_column_a",
     "label": "Schedule PTE-BD Column (A) - Federal Schedule K (Lines 1-7)",
     "data_type": "decimal", "sort_order": 71,
     "notes": PTE_BD_COLUMN_A_CARVE_OUT + " " + MO_FEDERAL_LINE_STAMP},
    {"fact_key": "mopte_bd_column_b",
     "label": "Schedule PTE-BD Column (B) - Portion Reportable to Individual Owners (Lines 1-7)",
     "data_type": "decimal", "sort_order": 72, "notes": PTE_BD_COLUMN_B_RULE},
    {"fact_key": "mopte_has_material_capital_gain",
     "label": "⚠ ADVICE LAYER ONLY - Line 1 carries material capital gain",
     "data_type": "boolean", "sort_order": 80,
     "notes": ("⚠⚠ THIS FLAG DRIVES A PREPARER-FACING INFORMATIONAL DIAGNOSTIC AND NOTHING ELSE "
               "(campaign D-12 C4). NO optimiser, NO recommendation, NO automatic election, NO "
               "computation of the interaction. D-10 already ruled the spec question -- BUILD TO THE "
               "FORM, no entity-level capital-gain subtraction anywhere.")},
    {"fact_key": "mopte_has_missouri_individual_member",
     "label": "⚠ ADVICE LAYER ONLY - a Missouri individual member exists",
     "data_type": "boolean", "sort_order": 81,
     "notes": "The second half of the capital-gain advisory trigger. It computes nothing."},
    {"fact_key": "mopte_member_is_501c",
     "label": "A member is an entity exempt under IRC 501(c) (Section 105.1500, RSMo applies)",
     "data_type": "boolean", "sort_order": 82,
     "notes": ("⚠ 105.1500 RSMo, printed on THIS FORM's page 4, bars the Department from REQUIRING a "
               "roster identifying such a member 'notwithstanding any publication, webpage, form, "
               "instruction, regulation, or statement shared by the Department' -- colliding head-on "
               "with Part B Column 1's 'All must be listed.' DO NOT SILENTLY SUPPRESS AND DO NOT "
               "SILENTLY INCLUDE. Never auto-populate the identity without explicit confirmation.")},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM MO_PTE -- RULES
# ═══════════════════════════════════════════════════════════════════════════
MOPTE_RULES: list[dict] = [
    {"rule_id": "R-MOPTE-BOTH", "title": "⚠⚠ MO-PTE is filed IN ADDITION TO MO-1065 / MO-1120S",
     "rule_type": "routing", "sort_order": 1,
     "inputs": ["mopte_election_box", "mopte_entity_type"], "outputs": ["required_returns"],
     "formula": ("election -> {MO_1065, MO_PTE} for a partnership, {MO_1120S, MO_PTE} for an S "
                 "corporation. NEVER MO_PTE alone."),
     "description": ("PUBLISHED DOR AUTHORITY, verbatim: 'Yes. The filing of the MO-PTE does not "
                     "substitute for a partnership filing its MO-1065 or an S corporation filing its "
                     "MO-1120S.' Structurally corroborated on this very form: Part A Line 3 and Line "
                     "9 both read 'Enter the share of fiduciary and partnership adjustment as shown "
                     "on Form MO-1041, Page 2, Part 1, Line 19 [Line 20], AND FORM MO-1065, LINE 11 "
                     "[LINE 12]. Copies of any Forms MO-1041 or MO-1065 MUST BE ATTACHED.' And "
                     "143.581 / 143.471 impose their filing duties WITHOUT REGARD to a 143.436 "
                     "election. ⚠⚠ THIS IS THE OPPOSITE OF VIRGINIA'S FORM 502 / 502PTET FORK. "
                     "PORTING THE VIRGINIA PATTERN WOULD LEAVE EVERY ELECTING MISSOURI CLIENT'S "
                     "FILING INCOMPLETE."),
     "notes": ("Campaign D-12; brief 22.3 correction #4 promoted this from an inference to published "
               "authority and CLOSED walk item W2.")},
    {"rule_id": "R-MOPTE-ELECT", "title": "The election has THREE preconditions - and one is easy to miss",
     "rule_type": "validation", "sort_order": 2,
     "inputs": ["mopte_election_box", "mopte_abe_representative", "mopte_box_federal_extension"],
     "outputs": ["election_valid"],
     "formula": "valid = election_box AND representative_designated AND filed_by_extended_deadline",
     "description": ("⚠⚠ 12 CSR 10-2.436(2): 'An election ... SHALL NOT BE EFFECTIVE if the "
                     "partnership or S corporation has not successfully designated a person as an "
                     "affected business entity representative for that tax year AT OR BEFORE THE TIME "
                     "the partnership or S corporation attempts to make such election.' The "
                     "instructions put it even more plainly: 'IF A PARTNERSHIP OR S CORPORATION DOES "
                     "NOT DESIGNATE A PERSON AS AN AFFECTED BUSINESS ENTITY REPRESENTATIVE ..., THE "
                     "ELECTION TO BECOME AN AFFECTED BUSINESS ENTITY WILL BE INEFFECTIVE.' The "
                     "election is ANNUAL ('A separate election must be made for each tax year') and, "
                     "once made, IRREVOCABLE for that year. 12 CSR 10-2.436(3): 'No election can be "
                     "made after the deadline, INCLUDING ANY APPROVED EXTENSION' -- ⭐ it reads ON THE "
                     "EXTENDED deadline, so the election SURVIVES an extension; it just cannot be "
                     "made late."),
     "exceptions": ("ONLY ONE NATURAL PERSON may serve, with a working e-mail address, telephone "
                    "number and physical address; the representative has SOLE AUTHORITY and "
                    "143.436.13(1) binds the members to those actions; designation is on FORM 2827 OR "
                    "FORM 2827 PTE (⚠ the instructions name only 2827 -- the regulation names both). "
                    "An all-members-sign alternative exists and requires a schedule with the "
                    "signature, printed name, phone number, ownership percentage and signature date "
                    "for EACH AND EVERY member. RED-DEFER R10, blocking."),
     "notes": "Available 'for tax years ending on or after December 31, 2022' (143.436.14)."},
    {"rule_id": "R-MOPTE-PG1", "title": "Page 1 - the ONLY tax computation in the Missouri PTE lane",
     "rule_type": "calculation", "sort_order": 3,
     "inputs": ["mopte_l1_sum_702a_1366", "MOPTE_A_L5", "MOPTE_A_L12", "mopte_l6_bid",
                "mopte_l7_lower_tier", "mopte_l8_prior_year_loss", "mopte_l11_mo_tc_credits"],
     "outputs": ["MOPTE_L4", "MOPTE_L9", "MOPTE_L10", "MOPTE_L12"],
     "formula": ("L4 = L1 + L2 - L3; L9 = L5 - L6 - L7 - L8 (L8 floored so L9 >= 0 before the loss); "
                 "L10 = max(0, L9 x 4.7%); L12 = max(0, L10 - L11)"),
     "description": ("⭐ THE 4.7% RATE IS PRINTED ON THE FACE at Line 10 -- 'Multiply Line 9 by 4.7% - "
                     "If result is less than 0, enter 0'. ⚠⚠ NEVER SOURCE IT FROM THE DOR FAQ, whose "
                     "rate table lists 5.3% (2022), 4.95% (2023) and 4.8% (2024) and STOPS with no "
                     "TY2025 entry. ⭐ LINE 7 IS SUBTRACTED AND IS SIGNED: a positive Line 7 removes "
                     "lower-tier income, a negative Line 7 adds back lower-tier loss (143.436.5(1)). "
                     "⭐ THE LINE 8 FLOOR: 'Do not use an amount of Missouri net loss from a prior tax "
                     "year to reduce the Missouri net income below $0 for this tax year', and $0 in "
                     "the first year filing Form MO-PTE. ⭐ LINE 12 IS THE NUMBER THAT BECOMES THE "
                     "MEMBERS' CREDIT POOL -- but only TO THE EXTENT PAID."),
     "notes": ("Statutory basis 143.436.3(1)/.4(1): 'multiplied by the highest rate of tax used to "
               "determine a Missouri income tax liability for an individual pursuant to section "
               "143.011.'")},
    {"rule_id": "R-MOPTE-L5", "title": "⚠ Line 5 = L4 x round(MO-MS PTE %, 3) - the ROUNDED PRODUCT WINS",
     "rule_type": "calculation", "sort_order": 4,
     "inputs": ["MOPTE_L4", "mopte_ms_pte_method", "MS_PTE_PERCENT"], "outputs": ["MOPTE_L5"],
     "formula": "L5 = L4 if all-Missouri else L4 x round(MO-MS PTE Line 3 or Line 9, 3)",
     "description": ("Face: 'Preliminary Missouri net income (loss) - If all Missouri income, enter "
                     "amount from Line 4. If not, complete and attach MO-MS PTE. MULTIPLY LINE 4 BY "
                     "THE PERCENTAGE', with two adjacent boxes `Method` and `Percent`. Instruction: "
                     "'Enter the apportionment method number used (apportionment election 2a, 3, 4, "
                     "5, 6, or 7) and the appropriate percentage (ROUNDED TO THREE DIGITS TO THE RIGHT "
                     "OF THE DECIMAL POINT, SUCH AS 12.345 PERCENT) from Form MO-MS PTE in the boxes "
                     "provided.' ⭐ THE METHOD NUMBER IS PERSISTED ON THE RETURN, not just the "
                     "percentage. ⚠ THE ROUND TRIP LOSES PRECISION -- MO-MS PTE computes Line 8 "
                     "DIRECTLY and then back-solves a three-decimal percentage at Line 9, so "
                     "`L4 x round(L9, 3) != L8`. This line's own label settles which one is Line 5: "
                     "'Multiply Line 4 by the percentage.' ENCODE THE ROUNDING; DO NOT SHORTCUT TO "
                     "LINE 8."),
     "exceptions": ("⚠⚠ WORDING DEFECT IN THE RULING AS RESTATED, RESOLVED HERE AND ESCALATED: the "
                    "ruling says 'MO-MS PTE Line 5 = L4 x round(L9, 3)', but MO-MS PTE's OWN Line 5 "
                    "is `Nonapportionable income - Everywhere`, a DIRECT-ENTRY dollar amount feeding "
                    "Line 6. The product belongs to MO-PTE LINE 5, using MO-MS PTE Line 4 (which is "
                    "MO-PTE Line 4) and MO-MS PTE Line 9. Substance unaffected; the line label is not."),
     "notes": ("⚠ The DOR states NO TIE-BREAK for the three-decimal rounding. This build uses "
               "ROUND_HALF_UP as a declared ENGINEERING DECISION, not as a Departmental rule.")},
    {"rule_id": "R-MOPTE-MSPTE", "title": "MO-MS PTE Part 1 - a BACK-SOLVED percentage, with a hard RED",
     "rule_type": "calculation", "sort_order": 5,
     "inputs": ["mopte_ms_pte_l4_balance", "mopte_ms_pte_has_nonapportionable"],
     "outputs": ["MS_PTE_PERCENT"],
     "formula": ("L3 = L1/L2; STOP if no nonapportionable income (MO-PTE L5% = L3); "
                 "L6 = (L4-L5) x L3; L8 = L6+L7; L9 = L8/L4  ⚠ HARD RED when L4 <= 0"),
     "description": ("⭐⭐ A MATERIALLY DIFFERENT ARCHITECTURE FROM MO-MS / MO-MSS. MO-MSS Line 3 "
                     "produces a FACTOR applied per distributive-share item. MO-MS PTE Lines 4-9 "
                     "produce a BLENDED EFFECTIVE PERCENTAGE: they apportion the balance NET of "
                     "nonapportionable income (Line 6), add Missouri-allocated nonapportionable "
                     "income (Line 7), then BACK-SOLVE a percentage at Line 9 so that L4 x L9 = L8. "
                     "The percentage is a DERIVED ARTEFACT, not a factor. ⚠⚠ THREE HAZARDS ON ONE "
                     "PAGE: (1) Line 9 divides by Line 4 and the instructions require the form 'even "
                     "if this balance is zero or negative' -- zero is undefined and negative INVERTS "
                     "THE SIGN; (2) the round trip loses precision; (3) Line 3 is separately capped "
                     "by 'stop here', so MO-PTE Line 5 Percent has TWO DIFFERENT SOURCES."),
     "exceptions": ("⚠⚠ HARD RED ON L4 <= 0. Do NOT silently return 0% or 100%. Prepare manually. "
                    "(U14; campaign D-12 Group D)"),
     "notes": ("⭐ THE ORDER-OF-OPERATIONS QUESTION IS RESOLVED AND MUST NOT BE RE-OPENED. The statute "
               "sources first and modifies second; the form modifies first (Lines 2/3) and sources "
               "second (Line 5). The reconciliation is the printed scoping rule: nonapportionable "
               "items are reported on MO-MS PTE 'ONLY TO THE EXTENT SUCH ITEMS ARE INCLUDED IN FORM "
               "MO-PTE, LINE 4 (BALANCE)', and anything subtracted at Line 3 is NOT reported there. "
               "Modifications enter the Balance; the Balance is then split into apportionable and "
               "directly-allocated components under 143.455. THE FORM IS A FAITHFUL IMPLEMENTATION "
               "OF THE STATUTE, NOT A CONFLICT. ⚠ Tiered partnerships: 'the partnership factor(s) "
               "must be multiplied by the pass-through entity's percentage of ownership, and then "
               "added into the pass-through entity's apportionment factor(s).'")},
    {"rule_id": "R-MOPTE-U11", "title": "⚠ U11 - the Lines 4-9 trigger is INVERTED between the two books",
     "rule_type": "validation", "sort_order": 6,
     "inputs": ["mopte_ms_pte_has_nonapportionable", "mopte_ms_pte_method"],
     "outputs": ["ms_pte_lines_4_9_required"],
     "formula": "UNRESOLVED - the engine must NOT decide this; raise the diagnostic and ask",
     "description": ("MO-PTE instructions: 'If the mileage percentage on Form MO-MS PTE, Page 1, is "
                     "APPLICABLE, or if the taxpayer has included any item of income to be allocated "
                     "(as opposed to apportioned) on Form MO-PTE, Line 4, the taxpayer must complete "
                     "Form MO-MS PTE, Part 1, Lines 4 through 9...' MO-MSS / MO-1120S parallel text: "
                     "'If the mileage percentage ... is INAPPLICABLE or if there is any income to be "
                     "allocated ...' ⚠⚠ THE SAME SENTENCE WITH THE OPPOSITE CONDITION. One of the two "
                     "is inverted and NO SOURCE RESOLVES WHICH. DO NOT GUESS IN CODE."),
     "exceptions": ("Interim reading FOR HUMAN JUDGEMENT ONLY, not for code: the MO-MSS reading is "
                    "the more coherent one (complete the allocation lines when the mileage percentage "
                    "alone will not do), but MO-MS PTE Line 9 exists PRECISELY to blend allocation "
                    "into the percentage, so the PTE reading is not absurd."),
     "notes": ("Also defect #3: the MO-PTE instructions send the resulting mileage percentage to "
               "'Form MO-PTE, LINE 4' -- a DOLLAR Balance. It belongs at LINE 5 PERCENT per the "
               "MO-MS PTE face. BUILD TO THE FACE.")},
    {"rule_id": "R-MOPTE-BD", "title": "Schedule PTE-BD - SUM-THEN-FLOOR at Line 8, 20% at Line 9",
     "rule_type": "calculation", "sort_order": 7,
     "inputs": ["mopte_bd_column_a", "mopte_bd_column_b", "mopte_bd_column_c"],
     "outputs": ["MOPTE_L6"],
     "formula": "BD L8 = max(0, sum(Column C Lines 1-7)); BD L9 = L8 x 20% -> MO-PTE Line 6",
     "description": ("⚠⚠ LINE 8'S WORDING IS GENUINELY AMBIGUOUS AND IT CHANGES THE ANSWER: 'Total of "
                     "Column (C), Lines 1-7, reduced by any negative amounts, but not below $0' reads "
                     "as EITHER (i) sum everything then floor the total at zero, OR (ii) drop the "
                     "negative rows then sum -- which would ignore losses entirely and INFLATE the "
                     "deduction. The instruction restates it identically. BUILD SUM-THEN-FLOOR "
                     "(campaign D-12 Group D), supported by 143.022.1: business income is 'the income "
                     "greater than zero ... limited to the MISSOURI SOURCE NET PROFIT FROM THE "
                     "COMBINATION OF' the four federal schedules -- 'net profit from the COMBINATION' "
                     "is a sum. The alternative reading is RECORDED, NOT BUILT, and a diagnostic "
                     "fires whenever any Column (C) row is negative. ⚠ Lines 6 and 7 are DEDUCTIONS "
                     "and the form gives NO SIGN CONVENTION. (U15)"),
     "exceptions": ("⚠ THE 20% IS READ OFF LINE 9 OF THE FACE, never derived from 143.022.4's "
                    "revenue-trigger ratchet (.4 sets only the CEILING; .5 gates increases on a "
                    "$150,000,000 net-general-revenue growth test). A TY2026 pass must RE-READ THE "
                    "FACE."),
     "notes": ("⚠⚠ COLUMN (C) IS A THIRD SOURCING REGIME AND IT COLLIDES WITH LINE 5 ON THE ADJACENT "
               "LINE. See R-MOPTE-SRC. ⚠ COLUMN (A) excludes anything owner-level-subtractable "
               "(U16); COLUMN (B) drops any C-corporation or trust member's share. ⚠ Lines 5 and 7 "
               "carry a HYPOTHETICAL-INDIVIDUAL MINIMISATION RULE that is deterministic but requires "
               "counterfactual reasoning about owner-level elections -- v1 DIRECT ENTRY with the rule "
               "as help copy.")},
    {"rule_id": "R-MOPTE-SRC", "title": "⚠⚠ Line 5 and Line 6 source differently - DO NOT RECONCILE THEM",
     "rule_type": "classification", "sort_order": 8,
     "inputs": ["MS_PTE_PERCENT", "mopte_bd_column_c"], "outputs": ["sourcing_regimes_in_use"],
     "formula": "Line 5 <- 143.455 (formulary); Line 6 <- PTE-BD Column (C) (qualitative). NO RECONCILIATION.",
     "description": ("⚠⚠ THE REAL COLLISION, AND IT IS ON ADJACENT LINES OF THE SAME RETURN, BOTH "
                     "FEEDING LINE 9. MO-PTE Line 5 sources under 143.455 -- a receipts factor with "
                     "market sourcing. Schedule PTE-BD Column (C) sources under a QUALITATIVE "
                     "place-of-production test: 'The source of income is the place where the income is "
                     "produced. An item is from Missouri sources if the item was produced by an "
                     "overall effort centered in Missouri. In general, IF THE \"BRAINS\" OF THE "
                     "OPERATION resulting in the item are located in Missouri, that item is from "
                     "Missouri sources.' That test is NOWHERE in 143.455, and NEITHER 12 CSR 10-2.190 "
                     "NOR 12 CSR 10-2.255 mentions it. THEY WILL DISAGREE AND NOTHING RECONCILES "
                     "THEM. U17 IS FULLY OPEN. Campaign D-12 C3: DO NOT FORCE THEM TO RECONCILE."),
     "exceptions": ("⚠ CONTRAST THE OTHER PAIR, WHOSE EXPECTATION FLIPPED: MO-NRP versus MO-MS PTE is "
                    "now EXPECTED-ZERO, because 12 CSR 10-2.190(2)(C) delegates to 12 CSR 10-2.255, "
                    "whose (3) puts partnerships on 143.455 identically to S corporations. A non-zero "
                    "delta THERE is a PROBABLE ERROR. Keep the two diagnostics separate; they mean "
                    "opposite things."),
     "notes": MO_NO_143_181_REGULATION},
    {"rule_id": "R-MOPTE-OPTOUT", "title": "The opt-out is a RETURN-LEVEL RECOMPUTATION, not a member flag",
     "rule_type": "calculation", "sort_order": 9,
     "inputs": ["mopte_optout_box", "mopte_partb_k1_percent"],
     "outputs": ["mopte_partb_credit_percent", "MOPTE_L1", "MOPTE_L6"],
     "formula": "credit_percent = k1_percent / (100% - sum(opt-out percentages)); DOR example 10/70 = 14",
     "description": ("12 CSR 10-2.436(12)(D) forces a FULL RECOMPUTATION of Line 1, every "
                     "modification, Schedule PTE-BD and the credit split AS THOUGH THE OPT-OUT "
                     "MEMBER'S ITEMS DID NOT EXIST. Verbatim on Line 1: 'Form MO-PTE, Line 1 must not "
                     "include any items of income or deduction allocable to an opt-out member.' On "
                     "Line 6: 'remove from the computation any opt-out member(s)' allocable items.' "
                     "⚠⚠ AND COLUMN 5 SILENTLY CHANGES MEANING: 'If any member has made an opt-out "
                     "election, the remaining participating members' percentage must be adjusted to "
                     "allow the full amount of tax paid, to be properly allocated. For example, if an "
                     "S corporation has an opt-out member with a share of 30%, and a non-opt-out "
                     "member with a share percentage of 10%, then that non-opt-out member's new "
                     "credit percentage is 14% (10% divided by 70%).' STORE THE K-1 PERCENTAGE AND "
                     "THE CREDIT PERCENTAGE AS TWO SEPARATE FIELDS AND NEVER OVERWRITE ONE WITH THE "
                     "OTHER."),
     "exceptions": ("⚠ THE AVAILABILITY GATE IS CONJUNCTIVE AND ITS SECOND LIMB IS EASILY DROPPED: "
                    "'...if the affected business entity's original (un-extended) MO-PTE filing "
                    "deadline is on or after August 28, 2025, AND THE AFFECTED BUSINESS ENTITY HAS "
                    "NOT FILED ITS ORIGINAL RETURN BY THAT DATE.' ENCODE BOTH LIMBS. ⚠ The DOR FAQ "
                    "states the gate differently ('tax year ends on or after August 28, 2024') and "
                    "143.436.5(2)-(4) plus 12 CSR 10-2.436(12) impose NO date gate at all -- NO "
                    "TY2025 IMPACT, MATERIAL FOR TY2024 AMENDED RETURNS (U2)."),
     "notes": ("12 CSR 10-2.436(12)(C): the opt-out member is INELIGIBLE for the 143.436.8 and .10 "
               "credits -- 'This subsection shall not be construed to affect an opt-out member's "
               "authorization to CARRY FORWARD AND REDEEM OUTSTANDING TAX CREDITS THAT WERE INITIALLY "
               "ALLOWED FOR A TAX YEAR TO WHICH THE OPT-OUT ELECTION DID NOT APPLY.' The MEMBER, not "
               "the entity, files Form MO-PTENR or Form MO-PTE Opt-Out (RED-DEFER R8); THE "
               "ENTITY-SIDE RECOMPUTATION IS COMPUTED.")},
    {"rule_id": "R-MOPTE-CREDIT", "title": "⚠⚠ MO-TC credits DESTROY the members' credit (C5)",
     "rule_type": "calculation", "sort_order": 10,
     "inputs": ["mopte_l11_mo_tc_credits", "mopte_cash_payments_applied", "MOPTE_L10"],
     "outputs": ["tax_actually_paid", "MOPTE_PARTB_COL6"],
     "formula": "tax_actually_paid = max(0, min(max(0, L10 - L11), cash_payments_applied))",
     "description": ("⚠⚠ A LIVE CLIENT-HARM PATH, STATED THREE TIMES AND FOUND ON NO FORM FIELD. "
                     "(1) MO-PTE instructions, Line 11: 'miscellaneous tax credits reduce tax "
                     "liability under the SALT Parity Act, RATHER THAN CONSTITUTING TAX PAID, and "
                     "therefore do not qualify as payments for purposes of calculating the PTE credit "
                     "for a member.' (2) Part B Column 6: the member's credit is the pro rata share "
                     "of Line 12 'TO THE EXTENT PAID.' (3) 12 CSR 10-2.436(11): the credit is "
                     "'computed based on the member's direct and indirect pro rata share of THE TAX "
                     "ACTUALLY PAID ... If an affected business entity reduces its tax liability ... "
                     "by use of tax credits, other than a credit for payment or overpayment of this "
                     "tax, the affected business entity's TAX ACTUALLY PAID WILL GENERALLY BE "
                     "REDUCED.' USING A MISSOURI MISCELLANEOUS CREDIT AT THE ENTITY LEVEL CONVERTS A "
                     "DOLLAR-FOR-DOLLAR OWNER CREDIT INTO NOTHING. THE FORM GIVES THE ENGINE NO FIELD "
                     "FOR THIS, so a DERIVED FIELD supplies it and a HARD (error-severity) diagnostic "
                     "fires whenever Line 11 > 0."),
     "exceptions": ("⚠ OPEN: whether the Line 13 excess REFUNDABLE credit counts as 'tax actually "
                    "paid' is unanswered by the Department. This build does NOT count it and says so "
                    "rather than deciding silently. (U20)"),
     "notes": ("An electing PTE uses MO-TC COLUMN 1 only. Credit ORDERING is preparer-controlled by "
               "row position ('Each credit will apply against your tax liability in the order they "
               "appear below'), never engine-determined. ⚠ Owner side: 143.436.8 (individuals) and "
               ".10 (corporations/fiduciaries, 'applied AFTER ALL OTHER CREDITS') carry UNLIMITED "
               "carryforward; 143.436.9 (a resident member of an OUT-OF-STATE PTE) is NEITHER "
               "REFUNDED NOR CARRIED FORWARD -- two credits, two OPPOSITE rules, easy to conflate.")},
    {"rule_id": "R-MOPTE-PARTB", "title": "Part B - 15 rows, TWO-DECIMAL percentages, four assertions",
     "rule_type": "validation", "sort_order": 11,
     "inputs": ["mopte_partb_k1_percent", "mopte_partb_credit_percent", "MOPTE_L12"],
     "outputs": ["MOPTE_PARTB_COL5", "MOPTE_PARTB_COL6", "MOPTE_PARTB_COL7"],
     "formula": ("sum(Col 5 over non-opt-out members, re-grossed) = 100.00%; sum(Col 6) <= L12; "
                 "Col 3 -> Col 7 AND blank Col 6; member is a PTE -> blank Col 6"),
     "description": ("A 15-row grid a) through o) plus a Total row -- ⚠ MO-1065 and MO-1120S Page 3 "
                     "have NINETEEN. Column 6, verbatim: 'IF THE MEMBER IS A S CORPORATION OR "
                     "PARTNERSHIP, LEAVE THIS COLUMN BLANK FOR THAT ENTITY' -- an UPPER-TIER PTE "
                     "member gets relief through Line 7, NOT through a credit. Column 7: 'If a member "
                     "has made an opt-out election, the member is not eligible for a PTE tax credit.' "
                     "⚠ Percentages round to TWO DECIMAL PLACES here; the MO-1065 / MO-1120S Page 3 "
                     "grids round to WHOLE NUMBERS."),
     "exceptions": ("⚠⚠ 105.1500 RSMo, printed on page 4 of this very form, bars the Department from "
                    "REQUIRING a list identifying a member of a 501(c) entity 'NOTWITHSTANDING ANY "
                    "PUBLICATION, WEBPAGE, FORM, INSTRUCTION, REGULATION, OR STATEMENT SHARED BY THE "
                    "DEPARTMENT' -- in direct tension with Column 1's 'All must be listed.' DO NOT "
                    "SILENTLY SUPPRESS AND DO NOT SILENTLY INCLUDE. RED-DEFER R13."),
     "notes": ("Form 5889 is OPTIONAL ('may be used' / 'can be utilized ... as an alternative to a "
               "report generated by the company'), and its column references have been ONE COLUMN "
               "STALE SINCE TY2024. GENERATE A DELVIO MEMBER REPORT and map 5889 BY SUBSTANCE: "
               "Line 1 <- Column 5, Line 2 <- Column 6.")},
    {"rule_id": "R-MOPTE-PG2", "title": "Page 2 - payments, refund and the $1.00 floor",
     "rule_type": "calculation", "sort_order": 12,
     "inputs": ["mopte_l14_anticipated_payments", "mopte_l22_trust_fund_donations", "MOPTE_L12"],
     "outputs": ["MOPTE_L17", "MOPTE_L19", "MOPTE_L20", "MOPTE_L23", "MOPTE_L24"],
     "formula": ("L17 = L13+L14+L15+L16; L19 = L17-L18; L20 = max(0, L19-L12); "
                 "L23 = L20-L21-L22 (no refund below $1.00); L24 = max(0, L12-L19)"),
     "description": ("⭐ LINE 13 IS THE ONE PLACE WHERE REFUNDABLE CREDITS IN EXCESS OF LIABILITY "
                     "RE-ENTER AS A PAYMENT rather than as a credit: 'If MO-TC, Line 13 is greater "
                     "than MO-TC, Line 12, enter difference here.' 'No refund of less than $1.00 will "
                     "be made.' 'The Department generally requires approved refunds of $100,000 OR "
                     "MORE to be issued electronically. If claiming a refund of $100,000 or more, "
                     "COMPLETE FORM 5378 and submit with your return.' ⚠ Line 22's trust-fund grid "
                     "sits INSIDE this arithmetic and is real form surface."),
     "notes": ("⚠ Line 24 is a BARE underpayment amount -- no penalty computation, no exception "
               "ladder, no worksheet. There is NO estimated-tax underpayment regime (N2) and NO "
               "late-filing penalty figure anywhere on the return (N14 / U26). What survives is the "
               "5% LATE-PAYMENT addition and interest under 143.731.2.")},
    {"rule_id": "R-MOPTE-EXT", "title": "⭐⭐ MO-PTE ONLY - the extension EXTENDS THE TIME TO PAY",
     "rule_type": "conditional", "sort_order": 13,
     "inputs": ["mopte_box_federal_extension"], "outputs": ["payment_due_date", "late_pay_addition"],
     "formula": ("extended file date = original + up to 6 months; NO 5% addition if paid by the "
                 "extended date; INTEREST runs from the ORIGINAL due date"),
     "description": ("⭐⭐ THREE SOURCES AGREE AND THIS IS THE OPPOSITE OF THE GENERAL MISSOURI RULE "
                     "AND OF VIRGINIA. MO-PTE instructions: 'AN EXTENSION OF TIME TO FILE WILL EXTEND "
                     "THE TIME FOR PAYMENT OF THE TAX. The pass-through entity must pay the tax on or "
                     "before the extended due date to avoid a 5 percent addition to tax. However, "
                     "SIMPLE INTEREST WILL BE CALCULATED FROM THE ORIGINAL RETURN DUE DATE until the "
                     "tax is paid.' 12 CSR 10-2.436(9): '...likewise granted an equal extension of "
                     "time for the payment of the tax due ... Pursuant to section 143.731.2, RSMo, "
                     "INTEREST ON THIS TAX WILL CONTINUE TO ACCRUE regardless of any extension of "
                     "time for payment.' MO-7004: 'If filing Form MO-7004 for a pass-through entity "
                     "tax return and payment is received on or before the extended due date, you will "
                     "not be charged a penalty of 5% but will be charged interest on the part of tax "
                     "that is not paid by the original due date.' ⚠⚠ DO NOT SHARE THIS BRANCH WITH "
                     "MO-1065 OR MO-1120S."),
     "exceptions": ("⚠ U24: MO-7004's instructions say 'up to 180 DAYS'; the MO-PTE instructions say "
                    "'not to exceed SIX MONTHS'. 180 days is not six months for most calendar "
                    "windows. Build the six-month cap, per the return's own instructions and 12 CSR "
                    "10-2.436(10)."),
     "notes": ("Due date: the 15th day of the 4th month -- April 15, 2026 for a calendar year, with "
               "weekend/holiday rollover. ⚠ FIVE DISTINCT DEADLINE BEHAVIOURS live in this lane; see "
               "MO_DEADLINE_BEHAVIOURS. Interest rate: NOT PRINTED ON ANY FORM -- direct entry until "
               "dor.mo.gov/taxation/statutory-interest-rates.html is pulled (U25).")},
    {"rule_id": "R-MOPTE-EFILE", "title": "⚠⚠ NOT e-fileable, NOT electronically payable, NOT automated by e-mail",
     "rule_type": "routing", "sort_order": 14,
     "inputs": [], "outputs": ["submission_channel"],
     "formula": "MO_PTE -> print/assemble for mailing; MO_1065 and MO_1120S -> MeF eligible",
     "description": ("Settled SIX independent ways and attacked from the falsifying direction: the "
                     "re-pulled DOR FAQ (both the return and the payment answers, verbatim); the "
                     "2026-03-31 form face, which prints a mailing address and an e-mail address and "
                     "NOTHING ELSE; a 9-page instruction sweep in which 'electronic' occurs exactly "
                     "once, in the $100,000-refund context; the DOR Partnership e-file page naming "
                     "ONLY MO-1065; the DOR Corporation-income e-file page naming ONLY MO-1120 and "
                     "MO-1120S with a 22-vendor list scoped to those two; and Drake KB 18013. ⚠ "
                     "'PAPER-ONLY' OVERSTATES IT -- e-mailing a PDF to pteincome@dor.mo.gov is a "
                     "Department-sanctioned channel; the accurate formulation is 'not e-fileable "
                     "through MeF, and not electronically payable'. (MO-PTEAP's 'you authorize the "
                     "Department to process the check electronically' is CHECK CONVERSION, not "
                     "electronic payment.) ⚠⚠ CAMPAIGN D-12 A6 -- A PRIVACY RULING: DELVIO DOES NOT "
                     "AUTOMATE THE E-MAIL CHANNEL, because it carries member SSNs IN THE CLEAR. "
                     "DELVIO COMPUTES AND ASSEMBLES; THE PREPARER CHOOSES THE CHANNEL."),
     "exceptions": ("MeF schema scope covers MO-1065 + MO-1120S ONLY -- a real HALVING. MO-PTE rides "
                    "the SUBSTITUTE-FORMS track: Form 4349 (letter of intent), Form 5629 "
                    "(guidelines), the 10 x 6 grid layout spec and the 2-D barcode specification. "
                    "⚠ MO-PTE, MO-MS PTE, Schedule PTE-BD, MO-1065 and Form 5889 carry NO SCANLINE "
                    "at all (N13), which is consistent with MO-PTE not being machine-processed but "
                    "MUST be confirmed against the DOR substitute-forms spec before Delvio prints "
                    "one."),
     "notes": ("⚠ Form MO-PTE Opt-Out prints the WRONG SCANLINE -- barcode *25329010001*, which is "
               "FORM MO-3NR's, over human-readable 25125010001, on a FINAL form re-stamped "
               "2026-03-27. PRINT NO SCANLINE AT ALL ON THAT FORM IN v1: reproducing a wrong barcode "
               "is worse than omitting one. (U27; campaign D-12 Group D)")},
    {"rule_id": "R-MOPTE-CAPGAIN", "title": "⚠⚠ Capital gain - ADVICE LAYER ONLY. ENCODE NOTHING.",
     "rule_type": "validation", "sort_order": 15,
     "inputs": ["mopte_has_material_capital_gain", "mopte_has_missouri_individual_member",
                "mopte_election_box"],
     "outputs": ["capital_gain_advisory"],
     "formula": "fires = election AND material_capital_gain AND missouri_individual_member. NOTHING ELSE.",
     "description": ("CAMPAIGN D-10 RULED THE SPEC QUESTION: BUILD TO THE FORM. Form MO-PTE Part A "
                     "Subtractions is a CLOSED ENUMERATED LIST, Lines 6 through 11, with NO "
                     "capital-gain line -- on a face RE-STAMPED 2026-03-31, i.e. AFTER the 2025 "
                     "session that enacted 143.121.3(14) and AFTER the amended SALT-Parity regulation "
                     "took effect. NO ENTITY-LEVEL CAPITAL-GAIN SUBTRACTION IS ENCODED ANYWHERE. ⭐ "
                     "The statute's own architecture SUPPORTS the form: 143.121.3(14)(b) grants "
                     "entity-level relief only 'for all tax years beginning on or after January first "
                     "of the tax year following the tax year in which the top rate of tax imposed "
                     "pursuant to section 143.011 is equal to or less than four and one-half percent' "
                     "-- TY2025's top rate is 4.7%, so (b) is NOT operative, and if 143.436's import "
                     "of 143.121 already delivered entity-level relief, (b) WOULD BE SUPERFLUOUS. "
                     "⚠⚠ CAMPAIGN D-12 C4: ENCODE NOTHING. No optimiser, no recommendation, no "
                     "automatic election, no computation of the interaction. Ship a preparer-facing "
                     "INFORMATIONAL diagnostic that states the interaction in the Department's own "
                     "terms, cites 143.121.3(14) and 143.436, AND STOPS."),
     "exceptions": ("⚠ U16 compounds it and cuts the OPPOSITE way: Schedule PTE-BD Column (A) excludes "
                    "from the BID base anything that 'would, ignoring Section 143.022, RSMo, be "
                    "subtractable or deductible for individual partners or shareholders', which on "
                    "its face removes owner-exempt capital gain from the DEDUCTION while the same "
                    "gain stays in the TAX base. RECORDED, NOT COMPUTED."),
     "notes": ("⚠⚠ STALENESS TRIPWIRE: when Missouri's top individual rate reaches 4.5% or less, "
               "143.121.3(14)(b) switches on for 143.071 entities THE FOLLOWING TAX YEAR. That is a "
               "dated, foreseeable change and it must sit on the TY-rollover re-verification "
               "checklist. mo_capital_gain_entity_relief_active() evaluates it rather than assuming "
               "it.")},
    {"rule_id": "R-MOPTE-DEPR", "title": "VERIFIED NEGATIVE - MO-PTE has NO depreciation line at all",
     "rule_type": "validation", "sort_order": 16,
     "inputs": [], "outputs": ["depreciation_modification"],
     "formula": "no depreciation line exists on Form MO-PTE; no state 179 figure exists in Missouri",
     "description": ("⚠⚠ MO-PTE CARRIES NEITHER the 143.121.3(7) basis adjustment NOR the "
                     "143.121.3(9) disposition recovery, and its 9-page instructions are SILENT too "
                     "(`depreciat|168|179|bonus` -> ZERO hits on both). The negative is closed at the "
                     "STATUTE: 143.121.2(3), the IRC 168 ADD-BACK ITSELF, is window-limited on its "
                     "face to property purchased on or after July 1, 2002 but before July 1, 2003, as "
                     "are .3(7) and .3(9); and 143.121 contains NO IRC 179 modification at all. THERE "
                     "IS NO OPEN-ENDED BONUS ADD-BACK IN MISSOURI LAW TO FIND. 100% OBBBA bonus flows "
                     "through untouched, there is NO Missouri shadow depreciation book and NO "
                     "Missouri 179 constant may ever be encoded."),
     "exceptions": ("⚠ THE LIVE RESIDUAL HAS NOWHERE TO GO. 143.121.3(7) and .3(9) remain live "
                    "subtractions and 143.436.3(1)/.4(1) import 'any modification made pursuant to "
                    "sections 143.121 and 143.141', so an electing entity still holding 2002-03 "
                    "vintage property has a STATUTORY SUBTRACTION WITH NO LINE TO PUT IT ON. Its only "
                    "route is the Part A Line 9 'Other adjustments' WRITE-IN, and neither the form "
                    "nor the instructions say so. (N5 / U18; RED-DEFER R5)"),
     "notes": ("⚠ DO NOT PORT VIRGINIA'S DERIVED STATE 179 FIGURE and DO NOT create a nullable 'state "
               "depreciation adjustment' field for symmetry with other states.")},
    {"rule_id": "R-MOPTE-501C", "title": "105.1500 RSMo - the member roster is a PREPARER DECISION",
     "rule_type": "validation", "sort_order": 17,
     "inputs": ["mopte_member_is_501c"], "outputs": ["roster_disclosure_decision"],
     "formula": "501(c) member -> PREPARER DECISION; never auto-populate, never auto-suppress",
     "description": ("Printed on Form MO-PTE page 4 AND Form MO-TC page 2: 'Pursuant to Section "
                     "105.1500, RSMo, the Department of Revenue is PROHIBITED FROM REQUIRING any "
                     "entity exempt from federal income tax under Section 501(c) ..., or any "
                     "individual, to provide the Department with any list, record, register, "
                     "registry, roll, roster, or other compilation of data of any kind that directly "
                     "or indirectly identifies a person as a member, supporter, volunteer of, or "
                     "donor of financial or nonfinancial support to, any entity exempt ... NOTHING IN "
                     "THIS FORM SHOULD BE READ OR UNDERSTOOD AS A REQUIREMENT THAT YOU PROVIDE ANY "
                     "SUCH INFORMATION. NOTWITHSTANDING ANY PUBLICATION, WEBPAGE, FORM, INSTRUCTION, "
                     "REGULATION, OR STATEMENT SHARED BY THE DEPARTMENT, YOU ARE NOT REQUIRED TO "
                     "INCLUDE SUCH INFORMATION ON THIS FORM.' ⚠ IT COLLIDES HEAD-ON with Part B "
                     "Column 1's 'Name of each member. ALL MUST BE LISTED.' It is not a computation "
                     "-- it is a PRINTABLE-CONTENT rule the engine must not override IN EITHER "
                     "DIRECTION."),
     "notes": ("Surface it as a preparer decision with the statutory text as help copy; Ken sets the "
               "default. RED-DEFER R13. It also touches the Line 22 trust-fund donation grid.")},
]

MOPTE_RULE_LINKS: list[tuple] = [
    ("R-MOPTE-BOTH", "MO_DOR_PTE_FAQ", "primary", "published DOR authority that both returns are filed"),
    ("R-MOPTE-BOTH", "MO_2025_FORM_MOPTE", "primary", "Part A Lines 3/9 draw off a filed MO-1065"),
    ("R-MOPTE-BOTH", "MO_RSMO_143_581_421", "secondary", "143.581 - the duty survives the election"),
    ("R-MOPTE-ELECT", "MO_12CSR_10_2_436", "primary", "(2) the representative precondition; (3) the deadline; (4) irrevocability"),
    ("R-MOPTE-ELECT", "MO_RSMO_143_436", "primary", "143.436.11, .13 and .14"),
    ("R-MOPTE-ELECT", "MO_2025_PTE_INSTR", "implementation", "'the election ... will be ineffective'"),
    ("R-MOPTE-PG1", "MO_2025_FORM_MOPTE", "primary", "Lines 1-12 as printed, including the 4.7% at Line 10"),
    ("R-MOPTE-PG1", "MO_RSMO_143_436", "primary", "143.436.3(1)/.4(1) - the base and the rate reference"),
    ("R-MOPTE-PG1", "MO_2025_PTE_INSTR", "implementation", "the Line 7 sign rule and the Line 8 floor"),
    ("R-MOPTE-PG1", "MO_2025_TAX_LEG_CHANGES", "secondary", "the DOR's own 4.7% TY2025 statement"),
    ("R-MOPTE-L5", "MO_2025_FORM_MOPTE", "primary", "'Multiply Line 4 by the percentage', Method and Percent boxes"),
    ("R-MOPTE-L5", "MO_2025_FORM_MOMSPTE", "primary", "the source of the percentage (Line 3 or Line 9)"),
    ("R-MOPTE-MSPTE", "MO_2025_FORM_MOMSPTE", "primary", "Part 1 Lines 1-9 as printed"),
    ("R-MOPTE-MSPTE", "MO_RSMO_143_455", "primary", "the sourcing statute the schedule implements"),
    ("R-MOPTE-MSPTE", "MO_2025_PTE_INSTR", "implementation", "the nonapportionable scoping rule"),
    ("R-MOPTE-U11", "MO_2025_PTE_INSTR", "primary", "'is applicable' - one half of the inverted pair"),
    ("R-MOPTE-U11", "MO_2025_FORM_MOMSS", "primary", "'is inapplicable' - the other half"),
    ("R-MOPTE-BD", "MO_2025_SCHEDULE_PTE_BD", "primary", "Lines 8 and 9 and the three column rules"),
    ("R-MOPTE-BD", "MO_RSMO_143_022", "primary", "143.022.1 'net profit from the combination of'"),
    ("R-MOPTE-BD", "MO_RSMO_143_436", "secondary", "the one owner-level deduction 143.436 imports by name"),
    ("R-MOPTE-SRC", "MO_2025_SCHEDULE_PTE_BD", "primary", "Column (C)'s 'brains of the operation' test"),
    ("R-MOPTE-SRC", "MO_RSMO_143_455", "primary", "the formulary regime Line 5 runs on"),
    ("R-MOPTE-SRC", "MO_12CSR_10_2_190_255", "secondary", "silent on the brains test - U17 stays open"),
    ("R-MOPTE-OPTOUT", "MO_12CSR_10_2_436", "primary", "(12)(A)-(D) - timing, ineligibility, recomputation"),
    ("R-MOPTE-OPTOUT", "MO_2025_FORM_MOPTE", "primary", "Part B Column 5 and the 10/70 = 14% example"),
    ("R-MOPTE-OPTOUT", "MO_RSMO_143_436", "secondary", "143.436.5(2)-(4) - the opt-out itself"),
    ("R-MOPTE-CREDIT", "MO_12CSR_10_2_436", "primary", "(11) - tax ACTUALLY PAID"),
    ("R-MOPTE-CREDIT", "MO_2025_FORM_MOTC", "primary", "the SPA code and the Line 12/13 mechanics"),
    ("R-MOPTE-CREDIT", "MO_2025_PTE_INSTR", "primary", "the Line 11 credit-poisoning instruction"),
    ("R-MOPTE-CREDIT", "MO_RSMO_143_436", "secondary", ".8 / .9 / .10 - two opposite carryforward rules"),
    ("R-MOPTE-PARTB", "MO_2025_FORM_MOPTE", "primary", "Part B's seven columns and the 15-row grid"),
    ("R-MOPTE-PARTB", "MO_2025_FORM_5889", "secondary", "the optional member report, mapped by substance"),
    ("R-MOPTE-PG2", "MO_2025_FORM_MOPTE", "primary", "Lines 13-24 and the trust-fund grid"),
    ("R-MOPTE-EXT", "MO_2025_EXTENSION_FORMS", "primary", "the inverted payment rule, on three sources"),
    ("R-MOPTE-EXT", "MO_12CSR_10_2_436", "primary", "(9) and (10) - payment extension, interest, six months"),
    ("R-MOPTE-EFILE", "MO_DOR_PTE_FAQ", "primary", "'You must submit your return ... to PO Box 3080'"),
    ("R-MOPTE-EFILE", "MO_DOR_EFILE_PAGES", "primary", "the MeF enumeration that omits MO-PTE"),
    ("R-MOPTE-EFILE", "MO_2025_FORM_MOPTE", "secondary", "the 2026-03-31 face prints no e-file reference"),
    ("R-MOPTE-CAPGAIN", "MO_RSMO_143_121", "primary", "143.121.3(14)(a) and the (b) rate trigger"),
    ("R-MOPTE-CAPGAIN", "MO_RSMO_143_436", "primary", "143.436.3(1)/.4(1) - the import clause"),
    ("R-MOPTE-CAPGAIN", "MO_2025_FORM_MOPTE", "primary", "the CLOSED subtraction list on a 2026-03-31 face"),
    ("R-MOPTE-CAPGAIN", "MO_2025_TAX_LEG_CHANGES", "secondary", "the DOR's individual-only / trigger-gated split"),
    ("R-MOPTE-DEPR", "MO_RSMO_143_121", "primary", "143.121.2(3) - the ADD-BACK ITSELF is window-limited"),
    ("R-MOPTE-DEPR", "MO_2025_FORM_MOPTE", "secondary", "no depreciation line anywhere on the face"),
    ("R-MOPTE-501C", "MO_2025_FORM_MOPTE", "primary", "105.1500 printed on page 4"),
    ("R-MOPTE-501C", "MO_2025_FORM_MOTC", "secondary", "the same notice printed on MO-TC page 2"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM MO_PTE -- LINES
# Page 1-2 = "1".."24"; Part A = "A1a".."A12"; Part B = "B-C1".."B-C7";
# Form MO-MS PTE = "MS-1".."MS-9"; Schedule PTE-BD = "BD-1".."BD-9".
# ═══════════════════════════════════════════════════════════════════════════
MOPTE_LINES: list[dict] = [
    {"line_number": "ELECT", "line_type": "input", "sort_order": 1,
     "description": ("Select this box if you are electing to become an Affected Business Entity and "
                     "consent to become subject to the tax imposed by Section 143.436, RSMo, for the "
                     "tax period for which this return is filed"),
     "source_facts": ["mopte_election_box"], "source_rules": ["R-MOPTE-ELECT", "R-MOPTE-BOTH"],
     "notes": ("⚠ INEFFECTIVE without a designated Affected Business Entity Representative (12 CSR "
               "10-2.436(2)). Annual; irrevocable once made for that year.")},
    {"line_number": "OPTOUT", "line_type": "input", "sort_order": 2,
     "description": ("Select this box if you have member(s) making an opt-out election. Attach Federal "
                     "K-1 for each opt-out member."),
     "source_facts": ["mopte_optout_box"], "source_rules": ["R-MOPTE-OPTOUT"],
     "notes": "⚠⚠ A RETURN-LEVEL RECOMPUTATION MODE, not a member flag."},
    {"line_number": "1", "line_type": "input", "sort_order": 10,
     "description": "Sum of separately and nonseparately computed items. See instructions.",
     "source_facts": ["mopte_l1_sum_702a_1366"], "source_rules": ["R-MOPTE-PG1"],
     "notes": ("IRC 702(a) / 1366. S corporation -> Federal Form 1120S Schedule K LINE 18; partnership "
               "-> federal Form 1065 PAGE 6, Analysis of Net Income (Loss), LINE 1. ⚠ Must EXCLUDE "
               "every item allocable to an opt-out member. " + MO_FEDERAL_LINE_STAMP)},
    {"line_number": "2", "line_type": "calculated", "sort_order": 11,
     "description": "Total Additions - Enter Line 5 from Page 3, PTE Adjustments",
     "calculation": "Part A Line 5", "source_rules": ["R-MOPTE-PG1"]},
    {"line_number": "3", "line_type": "calculated", "sort_order": 12,
     "description": "Total Subtractions - Enter Line 12 from Page 3, PTE Adjustments",
     "calculation": "Part A Line 12", "source_rules": ["R-MOPTE-PG1"]},
    {"line_number": "4", "line_type": "subtotal", "sort_order": 13,
     "description": "Balance - Line 1 plus Line 2, minus Line 3",
     "calculation": "1 + 2 - 3", "source_rules": ["R-MOPTE-PG1"],
     "destination_form": "Form MO-MS PTE Part 1 Line 4",
     "notes": ("⚠ Defect #3: the MO-PTE instructions send the MILEAGE PERCENTAGE to 'Form MO-PTE, "
               "Line 4'. THIS IS A DOLLAR BALANCE. The percentage belongs at Line 5 Percent, per the "
               "MO-MS PTE face. BUILD TO THE FACE.")},
    {"line_number": "5", "line_type": "calculated", "sort_order": 14,
     "description": ("Preliminary Missouri net income (loss) - If all Missouri income, enter amount "
                     "from Line 4. If not, complete and attach MO-MS PTE. Multiply Line 4 by the "
                     "percentage. [Method] [Percent]"),
     "calculation": "Line 4 if all-Missouri, else Line 4 x round(MO-MS PTE Line 3 or Line 9, 3)",
     "source_rules": ["R-MOPTE-L5", "R-MOPTE-MSPTE", "R-MOPTE-SRC"],
     "notes": ("⭐ THE METHOD NUMBER IS PERSISTED HERE, not just the percentage. ⚠ THE ROUNDED PRODUCT "
               "WINS over MO-MS PTE Line 8. ⚠⚠ THIS LINE SOURCES UNDER 143.455 WHILE THE ADJACENT "
               "LINE 6 SOURCES UNDER PTE-BD COLUMN (C)'s QUALITATIVE 'BRAINS OF THE OPERATION' TEST. "
               "DO NOT FORCE THEM TO RECONCILE (U17 fully open).")},
    {"line_number": "6", "line_type": "calculated", "sort_order": 15,
     "description": "Missouri Business Income Deduction - Attach Schedule PTE-BD",
     "calculation": "Schedule PTE-BD Line 9", "source_rules": ["R-MOPTE-BD", "R-MOPTE-SRC"],
     "notes": ("'THIS HYPOTHETICAL DETERMINATION IS MADE AT THE PASS-THROUGH ENTITY-LEVEL ... The "
               "resulting deduction MAY BE MORE OR LESS than the aggregate amount of the Missouri "
               "business income deduction actually allowed to all owners.' ⭐ The ONE owner-level "
               "deduction 143.436 imports BY NAME -- which is the strongest structural argument "
               "supporting D-10 on the capital-gain question.")},
    {"line_number": "7", "line_type": "input", "sort_order": 16,
     "description": ("Aggregate distributive share of Missouri net income (loss) from lower-tier "
                     "affected business entities. See instructions."),
     "source_facts": ["mopte_l7_lower_tier"], "source_rules": ["R-MOPTE-PG1"],
     "notes": ("⭐ SIGNED AND SUBTRACTED AT LINE 9: a POSITIVE figure REMOVES lower-tier income; a "
               "NEGATIVE figure ADDS BACK lower-tier loss -- exactly 143.436.5(1). 'If this sum is "
               "negative, ENTER A NEGATIVE FIGURE on Line 7.' Attach the lower-tier PTE tax reports. "
               "⭐ An upper-tier PTE member gets its relief HERE, not through a Part B credit.")},
    {"line_number": "8", "line_type": "input", "sort_order": 17,
     "description": "Missouri net loss to be used from affected business entity's prior tax year(s)",
     "source_facts": ["mopte_l8_prior_year_loss"], "source_rules": ["R-MOPTE-PG1"],
     "notes": ("⭐ FLOORED: 'Do not use an amount of Missouri net loss from a prior tax year to reduce "
               "the Missouri net income BELOW $0 for this tax year.' $0 in the first year filing Form "
               "MO-PTE. Attach a schedule of remaining loss balances by year -- a MAINTAINED "
               "CARRYFORWARD RECORD.")},
    {"line_number": "9", "line_type": "subtotal", "sort_order": 18,
     "description": "Missouri net income (loss) - Line 5 minus Line 6, 7, and 8",
     "calculation": "5 - 6 - 7 - 8, with Line 8 floored so the result is not driven below $0 by the loss",
     "source_rules": ["R-MOPTE-PG1"]},
    {"line_number": "10", "line_type": "calculated", "sort_order": 19,
     "description": "Pass-through entity income tax - Multiply Line 9 by 4.7% - If result is less than 0, enter 0",
     "calculation": "max(0, Line 9 x 0.047)", "source_rules": ["R-MOPTE-PG1"],
     "destination_form": "Form MO-TC Line 12",
     "notes": ("⭐ THE RATE IS PRINTED ON THE FACE. ⚠⚠ NEVER SOURCE IT FROM THE DOR FAQ, whose rate "
               "table stops at 4.8% (2024) with NO TY2025 ENTRY (defect #19).")},
    {"line_number": "11", "line_type": "input", "sort_order": 20,
     "description": "Tax Credits - Attach Form MO-TC (the total from Form MO-TC, Line 13)",
     "source_facts": ["mopte_l11_mo_tc_credits"], "source_rules": ["R-MOPTE-CREDIT"],
     "notes": ("⚠⚠ USING AN ENTITY-LEVEL CREDIT HERE DESTROYS THE MEMBERS' CREDIT. 'Miscellaneous tax "
               "credits reduce tax liability under the SALT Parity Act, RATHER THAN CONSTITUTING TAX "
               "PAID.' HARD DIAGNOSTIC whenever this is greater than zero.")},
    {"line_number": "12", "line_type": "total", "sort_order": 21,
     "description": ("Pass-through entity income tax liability - Subtract Line 11 from Line 10 - "
                     "Result cannot be less than 0"),
     "calculation": "max(0, 10 - 11)", "source_rules": ["R-MOPTE-PG1", "R-MOPTE-CREDIT"],
     "destination_form": "MO-PTE Part B Column 6 (pro rata, TO THE EXTENT PAID)",
     "notes": ("⭐ THE NUMBER THAT BECOMES THE MEMBERS' CREDIT POOL -- but only TO THE EXTENT PAID, and "
               "MO-TC use reduces tax actually paid. The form has NO FIELD for that; a derived field "
               "supplies it. (U20)")},
    {"line_number": "13", "line_type": "input", "sort_order": 22,
     "description": ("Excess Refundable Tax Credits - If MO-TC, Line 13 is greater than MO-TC, Line "
                     "12, enter difference here"),
     "source_rules": ["R-MOPTE-PG2"],
     "notes": ("⭐ THE ONE PLACE where refundable credits in excess of liability re-enter as a PAYMENT "
               "rather than as a credit. ⚠ Whether this counts as 'tax actually paid' for the "
               "members' credit pool is UNANSWERED by the Department; this build does not count it.")},
    {"line_number": "14", "line_type": "input", "sort_order": 23,
     "description": "Anticipated tax payments - Include approved overpayments applied from previous year",
     "source_facts": ["mopte_l14_anticipated_payments"], "source_rules": ["R-MOPTE-PG2"],
     "notes": ("Form MO-PTEAP. ⭐ ANTICIPATED PAYMENTS ARE NOT REQUIRED (N2). ⚠ 'If the requested "
               "overpayment(s) credited from 2024 has been adjusted, YOU MUST USE THE ADJUSTED "
               "AMOUNT.'")},
    {"line_number": "15", "line_type": "input", "sort_order": 24,
     "description": "Payments with Form MO-7004", "source_rules": ["R-MOPTE-PG2", "R-MOPTE-EXT"]},
    {"line_number": "16", "line_type": "input", "sort_order": 25,
     "description": "Amended return only - Tax paid with (or after) the filing of the original return",
     "source_rules": ["R-MOPTE-PG2"]},
    {"line_number": "17", "line_type": "subtotal", "sort_order": 26,
     "description": "Subtotal - Add Lines 13 through 16", "calculation": "13 + 14 + 15 + 16",
     "source_rules": ["R-MOPTE-PG2"]},
    {"line_number": "18", "line_type": "input", "sort_order": 27,
     "description": ("Amended return only - Overpayment, if any, as shown on original return or as "
                     "later adjusted"),
     "source_rules": ["R-MOPTE-PG2"],
     "notes": ("'Any refund due on the original return will be refunded SEPARATELY from any additional "
               "refund claimed on the amended return.'")},
    {"line_number": "19", "line_type": "subtotal", "sort_order": 28,
     "description": "Total - Line 17 minus Line 18", "calculation": "17 - 18",
     "source_rules": ["R-MOPTE-PG2"]},
    {"line_number": "20", "line_type": "calculated", "sort_order": 29,
     "description": "If Line 19 is more than Line 12, enter overpayment here",
     "calculation": "max(0, 19 - 12)", "source_rules": ["R-MOPTE-PG2"]},
    {"line_number": "21", "line_type": "input", "sort_order": 30,
     "description": ("Amount of Line 20 to be applied to your anticipated 2026 pass-through entity "
                     "income tax"),
     "source_rules": ["R-MOPTE-PG2"],
     "notes": ("'If filing an amended return do not include the original amount requested to be "
               "applied to the next filing period.'")},
    {"line_number": "22", "line_type": "input", "sort_order": 31,
     "description": "Total Donation - Add amounts from Boxes 22a through 22n and enter here",
     "source_facts": ["mopte_l22_trust_fund_donations"], "source_rules": ["R-MOPTE-PG2"],
     "notes": ("⚠ REAL FORM SURFACE -- it is INSIDE the Line 23 refund arithmetic. 14 boxes with "
               "printed $1/$2 minimums plus TWO write-in slots; the additional fund codes are "
               "NON-CONTIGUOUS (04, 06, 11, 12 and 13 are unpublished); most are capped at $200 and "
               "code 14 is uncapped; HARD CAP OF TWO WRITE-INS; a balance-due return needs A SEPARATE "
               "CHECK for the donation.")},
    {"line_number": "23", "line_type": "total", "sort_order": 32,
     "description": "REFUND - Line 20 minus Lines 21 and 22",
     "calculation": "20 - 21 - 22, with no refund made below $1.00",
     "source_rules": ["R-MOPTE-PG2"],
     "notes": ("'No refund of less than $1.00 will be made.' Refunds of $100,000 or more generally "
               "issue electronically -- COMPLETE FORM 5378 and submit it with the return (R12). ⚠ "
               "This is the ONLY occurrence of the string 'electronic' in the entire 9-page "
               "instruction set.")},
    {"line_number": "24", "line_type": "total", "sort_order": 33,
     "description": ("AMOUNT DUE - If Line 19 is less than Line 12, enter underpayment here. (U.S. "
                     "funds only)"),
     "calculation": "max(0, 12 - 19)", "source_rules": ["R-MOPTE-PG2"],
     "notes": ("⚠ A BARE UNDERPAYMENT AMOUNT: no penalty computation, no exception ladder, no "
               "worksheet. There is NO estimated-tax underpayment regime (N2) and NO late-filing "
               "penalty figure on the return (N14 / U26). The 5% LATE-PAYMENT addition and interest "
               "under 143.731.2 survive and are charged by the Department.")},
    # ---------------------------------------------------------- Part A
    {"line_number": "A1a", "line_type": "input", "sort_order": 40,
     "description": "Part A 1a. State and local income taxes deducted on Federal Form 1120S or 1065",
     "source_facts": ["mopte_a1a_state_local_income_taxes"], "source_rules": ["R-MOPTE-PG1"]},
    {"line_number": "A1b", "line_type": "input", "sort_order": 41,
     "description": ("Part A 1b. Kansas City & St. Louis earnings taxes. Enter Line 1a minus Line 1b "
                     "on Line 1."),
     "source_facts": ["mopte_a1b_city_earnings_taxes"], "source_rules": ["R-MOPTE-PG1"],
     "notes": "⚠ The three faces word this label DIFFERENTLY. Transcribe each face's own wording."},
    {"line_number": "A2a", "line_type": "input", "sort_order": 42,
     "description": "Part A 2a. State and local bond interest (except Missouri)",
     "source_facts": ["mopte_a2a_state_local_bond_interest"], "source_rules": ["R-MOPTE-PG1"]},
    {"line_number": "A2b", "line_type": "input", "sort_order": 43,
     "description": ("Part A 2b. Related expenses (omit if less than $500). Enter Line 2a minus Line "
                     "2b on Line 2."),
     "source_facts": ["mopte_a2b_related_expenses"], "source_rules": ["R-MOPTE-PG1"],
     "notes": "⚠ A FLOOR ON THE EXPENSE: 'must equal or exceed $500. If less than $500, enter $0.'"},
    {"line_number": "A3", "line_type": "input", "sort_order": 44,
     "description": "Part A 3. Partnership / Fiduciary / Other adjustments (list) -- ADDITION",
     "source_facts": ["mopte_a3_other_additions"], "source_rules": ["R-MOPTE-BOTH", "R-MOPTE-PG1"],
     "notes": ("⚠⚠ Draws from MO-1041 Page 2 Part 1 Line 19 AND FORM MO-1065 LINE 11, with copies "
               "REQUIRED as attachments -- structural proof that both returns are filed.")},
    {"line_number": "A4", "line_type": "input", "sort_order": 45,
     "description": "Part A 4. Business interest expense carryforward (Section 143.121.2(6), RSMo)",
     "source_facts": ["mopte_a4_163j_carryforward"], "source_rules": ["R-MOPTE-PG1"],
     "notes": ("⭐ ITS OWN LINE HERE; folded into Line 3 by instruction on MO-1120S; ABSENT from "
               "MO-1065 entirely (N7). ⚠ THERE IS NO FOOD PANTRY ADD-BACK ON MO-PTE (N6).")},
    {"line_number": "A5", "line_type": "subtotal", "sort_order": 46,
     "description": "Part A 5. Total Additions - Add Lines 1 through 4",
     "calculation": "A1 + A2 + A3 + A4", "source_rules": ["R-MOPTE-PG1"],
     "destination_form": "MO-PTE Page 1 Line 2"},
    {"line_number": "A6a", "line_type": "input", "sort_order": 47,
     "description": "Part A 6a. Interest from exempt federal obligations",
     "source_facts": ["mopte_a6a_exempt_federal_obligations"], "source_rules": ["R-MOPTE-PG1"]},
    {"line_number": "A6b", "line_type": "input", "sort_order": 48,
     "description": ("Part A 6b. Related expenses (omit if less than $500). Enter Line 6a minus Line "
                     "6b on Line 6."),
     "source_facts": ["mopte_a6b_related_expenses"], "source_rules": ["R-MOPTE-PG1"]},
    {"line_number": "A7", "line_type": "input", "sort_order": 49,
     "description": ("Part A 7. Amount of the state income tax refund(s) included in the sum of "
                     "separately and nonseparately computed items"),
     "source_facts": ["mopte_a7_state_refund"], "source_rules": ["R-MOPTE-PG1"]},
    {"line_number": "A8", "line_type": "input", "sort_order": 50,
     "description": "Part A 8. Federally taxable - Missouri exempt obligations (MOHELA)",
     "source_facts": ["mopte_a8_mohela"], "source_rules": ["R-MOPTE-PG1"],
     "notes": ("⚠ Sale proceeds are exempt only TO THE EXTENT OF THE HOLDER'S COST OF ACQUISITION. "
               "MO-1065 has no MOHELA line at all (N8).")},
    {"line_number": "A9", "line_type": "input", "sort_order": 51,
     "description": ("Part A 9. Partnership / Fiduciary / Build America and Recovery Zone Bond "
                     "Interest / Missouri Public-Private Transportation Act / Other adjustments"),
     "source_facts": ["mopte_a9_other_subtractions"],
     "source_rules": ["R-MOPTE-BOTH", "R-MOPTE-PG1", "R-MOPTE-DEPR"],
     "notes": ("⚠⚠ TWO ITEMS APPEAR IN THE INSTRUCTION BUT NOT ON THE FACE -- the 280E MARIJUANA "
               "deduction and the BROADBAND GRANT subtraction -- and both must go through the `Other "
               "adjustments` write-in with a HAND-TYPED DESCRIPTION the engine must supply, because "
               "THE DOR PRINTS NO CODE. ⚠⚠ THIS WRITE-IN IS ALSO THE ONLY ROUTE ONTO MO-PTE for a "
               "live 143.121.3(7)/(9) depreciation residual (N5 / U18) and for the 143.121.2(4) NOL "
               "addition (U28). Neither the form nor the instructions say so.")},
    {"line_number": "A10", "line_type": "input", "sort_order": 52,
     "description": "Part A 10. Agricultural Disaster Relief",
     "source_facts": ["mopte_a10_agricultural_disaster_relief"], "source_rules": ["R-MOPTE-PG1"],
     "notes": ("⭐⭐ INSIDE THE LINE 12 SUBTRACTION TOTAL HERE -- it reduces the entity's tax base "
               "directly -- whereas MO-1065 Line 13 and MO-1120S Line 15 sit OUTSIDE their totals and "
               "are separately allocated to owners. ⚠ SPELLING: THIS FACE PRINTS `Agricultural`; the "
               "other two print `Agriculture`.")},
    {"line_number": "A11", "line_type": "input", "sort_order": 53,
     "description": "Part A 11. Disallowed business interest expense (Section 143.121.3(11), RSMo)",
     "source_facts": ["mopte_a11_163j_disallowed"], "source_rules": ["R-MOPTE-PG1"],
     "notes": "⭐ ITS OWN LINE HERE; folded into Line 9 on MO-1120S; ABSENT from MO-1065 (N7)."},
    {"line_number": "A12", "line_type": "subtotal", "sort_order": 54,
     "description": "Part A 12. Total Subtractions - Add Lines 6 through 11",
     "calculation": "A6 + A7 + A8 + A9 + A10 + A11", "source_rules": ["R-MOPTE-PG1"],
     "destination_form": "MO-PTE Page 1 Line 3",
     "notes": ("⚠⚠ A CLOSED ENUMERATED LIST, LINES 6-11. THERE IS NO CAPITAL-GAIN LINE, on a face "
               "re-stamped 2026-03-31. D-10: BUILD TO THE FORM. DO NOT ADD ONE. (N4)")},
    # ---------------------------------------------------------- Part B
    {"line_number": "B-C1", "line_type": "input", "sort_order": 60,
     "description": "Part B Column 1 - Name of each member. All must be listed. Use an attachment if necessary.",
     "source_facts": ["mopte_partb_member_roster", "mopte_member_is_501c"],
     "source_rules": ["R-MOPTE-PARTB", "R-MOPTE-501C"],
     "notes": ("⚠⚠ COLLIDES WITH 105.1500 RSMo, PRINTED ON PAGE 4 OF THIS VERY FORM. Do not silently "
               "suppress and do not silently include; never auto-populate a 501(c) member's identity "
               "without explicit confirmation. RED-DEFER R13.")},
    {"line_number": "B-C2", "line_type": "input", "sort_order": 61,
     "description": "Part B Column 2 - Select if member is a nonresident",
     "source_rules": ["R-MOPTE-PARTB"],
     "notes": ("⚠ A nonresident member is STILL SUBJECT TO WITHHOLDING even though the entity elected "
               "-- 12 CSR 10-2.436(8).")},
    {"line_number": "B-C3", "line_type": "input", "sort_order": 62,
     "description": "Part B Column 3 - Select if member has made an opt-out election",
     "source_rules": ["R-MOPTE-OPTOUT", "R-MOPTE-PARTB"],
     "notes": ("⭐ INSERTED IN TY2024 -- and that insertion is what pushed SSN to Column 4, Membership "
               "% to Column 5 and the Credit to Column 6, making FORM 5889'S REFERENCES ONE COLUMN "
               "STALE. TY2025 changed only the Column 6 label. Form 5889 was revised 03-2025, AFTER "
               "the shift, and still not fixed -- A PERSISTED DEFECT, NOT A LAG.")},
    {"line_number": "B-C4", "line_type": "input", "sort_order": 63,
     "description": "Part B Column 4 - Social Security Number or FEIN",
     "source_rules": ["R-MOPTE-PARTB"],
     "notes": ("⚠ Form 5889 Line 1 points HERE for the membership percentage. IT IS WRONG: this is "
               "the SSN/FEIN column. Map by SUBSTANCE.")},
    {"line_number": "B-C5", "line_type": "input", "sort_order": 64,
     "description": "Part B Column 5 - Membership % (rounded to the nearest TWO DECIMAL PLACES)",
     "source_facts": ["mopte_partb_k1_percent", "mopte_partb_credit_percent"],
     "source_rules": ["R-MOPTE-OPTOUT", "R-MOPTE-PARTB"],
     "destination_form": "Form 5889 Line 1 (BY SUBSTANCE, not by its printed column number)",
     "notes": ("⚠⚠ TWO MEANINGS UNDER ONE LABEL. With no opt-out it is the K-1 percentage; with an "
               "opt-out it is the RE-GROSSED-UP CREDIT-ALLOCATION percentage that matches no K-1. "
               "STORE THEM AS TWO SEPARATE FIELDS. DOR example: 10 / 70 = 14. ⚠ TWO DECIMALS here; "
               "the MO-1065 / MO-1120S Page 3 grids use WHOLE NUMBERS.")},
    {"line_number": "B-C6", "line_type": "calculated", "sort_order": 65,
     "description": "Part B Column 6 - Member's PTE Tax Credit (see instructions)",
     "calculation": "credit_percent x TAX ACTUALLY PAID (a DERIVED field), never simply x Line 12",
     "source_rules": ["R-MOPTE-CREDIT", "R-MOPTE-PARTB"],
     "destination_form": ("Form MO-TC alpha code SPA -> MO-1040 Line 42 / MO-1041 Line 16 / MO-1120 "
                          "Line 17; Form 5889 Line 2 (BY SUBSTANCE)"),
     "notes": ("⚠⚠ 'the member's pro rata share of the Form MO-PTE, Line 12 Pass-Through Entity Income "
               "Tax Liability, TO THE EXTENT PAID. IF THE MEMBER IS A S CORPORATION OR PARTNERSHIP, "
               "LEAVE THIS COLUMN BLANK FOR THAT ENTITY.' An upper-tier PTE gets relief via Line 7. "
               "⚠ MO-TC use at Line 11 REDUCES tax actually paid (12 CSR 10-2.436(11)).")},
    {"line_number": "B-C7", "line_type": "input", "sort_order": 66,
     "description": "Part B Column 7 - Members not eligible for PTE Tax Credit (see instructions)",
     "source_rules": ["R-MOPTE-OPTOUT", "R-MOPTE-PARTB"],
     "notes": ("'If a member has made an opt-out election, the member is not eligible for a PTE tax "
               "credit.' Column 3 checked -> Column 7 checked AND Column 6 blank.")},
    # ------------------------------------------- Form MO-MS PTE sub-spec
    {"line_number": "MS-1", "line_type": "input", "sort_order": 70,
     "description": "MO-MS PTE Part 1 Line 1 - Amount of receipts in Missouri",
     "source_rules": ["R-MOPTE-MSPTE"]},
    {"line_number": "MS-2", "line_type": "input", "sort_order": 71,
     "description": "MO-MS PTE Part 1 Line 2 - Amount of receipts everywhere",
     "source_rules": ["R-MOPTE-MSPTE"],
     "notes": ("⚠ DENOMINATOR EXCLUSION: hedging transactions and the maturity, redemption, sale, "
               "exchange, loan or other disposition of cash or securities are excluded from BOTH the "
               "numerator and the denominator.")},
    {"line_number": "MS-3", "line_type": "calculated", "sort_order": 72,
     "description": ("MO-MS PTE Part 1 Line 3 - Receipts factor. Divide Line 1 by Line 2. Note: Stop "
                     "here if you do not have any nonapportionable income. Enter Line 3 on Form "
                     "MO-PTE, Line 5 Percent."),
     "calculation": "Line 1 / Line 2", "source_rules": ["R-MOPTE-MSPTE", "R-MOPTE-L5"],
     "destination_form": "MO-PTE Line 5 Percent (the 'stop here' short path)",
     "notes": ("⚠ MO-PTE Line 5 Percent has TWO DIFFERENT SOURCES: this line on the short path, "
               "Line 9 otherwise. ⚠ On Method Seven, SUBSTITUTE the approved percentage (without "
               "taking allocation into account) for the receipts factor here.")},
    {"line_number": "MS-4", "line_type": "calculated", "sort_order": 73,
     "description": "MO-MS PTE Part 1 Line 4 - Enter balance from Form MO-PTE, Line 4",
     "calculation": "= MO-PTE Line 4", "source_facts": ["mopte_ms_pte_l4_balance"],
     "source_rules": ["R-MOPTE-MSPTE"],
     "notes": ("⚠⚠ LINE 9 DIVIDES BY THIS, and the form is required 'EVEN IF THIS BALANCE IS ZERO OR "
               "NEGATIVE'. HARD RED when it is zero or negative -- prepare manually. (U14)")},
    {"line_number": "MS-5", "line_type": "input", "sort_order": 74,
     "description": ("MO-MS PTE Part 1 Line 5 - Nonapportionable income - Everywhere - Attach a "
                     "detailed explanation to be considered"),
     "source_rules": ["R-MOPTE-MSPTE"],
     "notes": ("⚠⚠ THIS IS A DIRECT-ENTRY DOLLAR AMOUNT FEEDING LINE 6 -- it is NOT the line that "
               "carries the `L4 x round(L9, 3)` product. That product is MO-PTE LINE 5. Recorded "
               "because the ruling as restated named this line by mistake. ⚠ SCOPING RULE: report "
               "nonapportionable items here ONLY to the extent they are included in MO-PTE Line 4, "
               "and NOT to the extent they were subtracted at MO-PTE Line 3.")},
    {"line_number": "MS-6", "line_type": "calculated", "sort_order": 75,
     "description": ("MO-MS PTE Part 1 Line 6 - Apportioned balance - Subtract Line 5 from Line 4, "
                     "then multiply by Line 3"),
     "calculation": "(Line 4 - Line 5) x Line 3", "source_rules": ["R-MOPTE-MSPTE"]},
    {"line_number": "MS-7", "line_type": "input", "sort_order": 76,
     "description": ("MO-MS PTE Part 1 Line 7 - Nonapportionable income - Missouri-allocated - Attach "
                     "a detailed explanation to be considered"),
     "source_rules": ["R-MOPTE-MSPTE"],
     "notes": ("Allocated under the seven 143.455.6-.9 rules, TWO OF WHICH ARE THROWBACK-STYLE "
               "((d)(2) capital gains from TPP; (g)(2) patent and copyright royalties).")},
    {"line_number": "MS-8", "line_type": "subtotal", "sort_order": 77,
     "description": "MO-MS PTE Part 1 Line 8 - Preliminary Missouri net income (loss) - Add Lines 6 and 7",
     "calculation": "Line 6 + Line 7", "source_rules": ["R-MOPTE-MSPTE"],
     "notes": ("⚠ THE FORM ASKS THE PREPARER TO COMPUTE THIS DIRECTLY **AND** TO REPRODUCE IT VIA A "
               "THREE-DECIMAL PERCENTAGE AT LINE 9. The two will not agree exactly. MO-PTE Line 5's "
               "own label -- 'Multiply Line 4 by the percentage' -- settles it: THE ROUNDED PRODUCT "
               "WINS. Do not shortcut to this line.")},
    {"line_number": "MS-9", "line_type": "calculated", "sort_order": 78,
     "description": "MO-MS PTE Part 1 Line 9 - Divide Line 8 by Line 4. Enter on Form MO-PTE, Line 5 Percent.",
     "calculation": "Line 8 / Line 4, to three decimals  ⚠ HARD RED when Line 4 <= 0",
     "source_rules": ["R-MOPTE-MSPTE", "R-MOPTE-L5"],
     "destination_form": "MO-PTE Line 5 Percent",
     "notes": ("⭐ A BACK-SOLVED, BLENDED EFFECTIVE PERCENTAGE -- A DERIVED ARTEFACT, NOT A FACTOR. "
               "That is what makes MO-MS PTE architecturally different from MO-MSS, whose Line 3 "
               "factor is applied PER DISTRIBUTIVE-SHARE ITEM.")},
    # --------------------------------------- Schedule PTE-BD sub-spec
    {"line_number": "BD-CA", "line_type": "input", "sort_order": 80,
     "description": "Schedule PTE-BD Column (A) - Federal Schedule K (Lines 1-7)",
     "source_facts": ["mopte_bd_column_a"], "source_rules": ["R-MOPTE-BD"],
     "notes": PTE_BD_COLUMN_A_CARVE_OUT},
    {"line_number": "BD-CB", "line_type": "input", "sort_order": 81,
     "description": "Schedule PTE-BD Column (B) - Portion Reportable to Individual Owners (Lines 1-7)",
     "source_facts": ["mopte_bd_column_b"], "source_rules": ["R-MOPTE-BD"],
     "notes": PTE_BD_COLUMN_B_RULE},
    {"line_number": "BD-CC", "line_type": "input", "sort_order": 82,
     "description": "Schedule PTE-BD Column (C) - Portion of Column (B) from Missouri Sources (Lines 1-7)",
     "source_facts": ["mopte_bd_column_c"], "source_rules": ["R-MOPTE-BD", "R-MOPTE-SRC"],
     "notes": PTE_BD_COLUMN_C_RULE},
    {"line_number": "BD-4", "line_type": "input", "sort_order": 83,
     "description": "Schedule PTE-BD Line 4 - Partnerships Only - Guaranteed Payments (Total)",
     "source_rules": ["R-MOPTE-BD"],
     "notes": "The only entity-type fork in the PTE-BD grid. " + MO_FEDERAL_LINE_STAMP},
    {"line_number": "BD-6", "line_type": "input", "sort_order": 84,
     "description": "Schedule PTE-BD Line 6 - Section 179 Deduction",
     "source_rules": ["R-MOPTE-BD", "R-MOPTE-DEPR"],
     "notes": ("⭐ IRC 179 AS A DISTRIBUTIVE-SHARE ITEM WITH NO MISSOURI CAP OR RECOMPUTATION -- the "
               "third of three such appearances in the lane, and part of the proof that no Missouri "
               "179 constant exists. ⚠ Lines 6 and 7 are DEDUCTIONS and the form gives NO SIGN "
               "CONVENTION (U15).")},
    {"line_number": "BD-7", "line_type": "input", "sort_order": 85,
     "description": "Schedule PTE-BD Line 7 - Other Deductions (See Instructions)",
     "source_rules": ["R-MOPTE-BD"],
     "notes": PTE_BD_LINES_5_7_TIEBREAKER},
    {"line_number": "BD-8", "line_type": "subtotal", "sort_order": 86,
     "description": ("Schedule PTE-BD Line 8 - Missouri Source Net Profit - Total of Column (C), Lines "
                     "1-7, reduced by any negative amounts, but not below $0"),
     "calculation": "max(0, sum(Column C Lines 1-7))   [SUM-THEN-FLOOR, campaign D-12 Group D]",
     "source_rules": ["R-MOPTE-BD"],
     "notes": ("⚠⚠ GENUINELY AMBIGUOUS AND IT CHANGES THE ANSWER (U15). The alternative reading -- "
               "drop the negative rows, then sum -- would ignore losses and INFLATE the deduction. "
               "143.022.1's 'Missouri source net profit from the COMBINATION OF' supports "
               "sum-then-floor. The alternative is RECORDED, NOT BUILT, and a diagnostic fires "
               "whenever any Column (C) row is negative.")},
    {"line_number": "BD-9", "line_type": "total", "sort_order": 87,
     "description": ("Schedule PTE-BD Line 9 - Allowable Business Income Deduction - Multiply Line 8, "
                     "Column C by 20%. Enter here and on Form MO-PTE, Line 6."),
     "calculation": "Line 8 x 20%", "source_rules": ["R-MOPTE-BD"],
     "destination_form": "MO-PTE Line 6",
     "notes": ("⚠ THE 20% IS READ OFF THIS FACE, never derived from 143.022.4's revenue-trigger "
               "ratchet. A TY2026 pass must RE-READ THE FACE.")},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM MO_PTE -- DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════════════════
MOPTE_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_MO_PTE_ALSO_FILE_ENTITY_RETURN", "severity": "error",
     "title": "⚠⚠ MO-PTE does NOT replace Form MO-1065 / MO-1120S - both must be filed",
     "condition": "the affected business entity election is made",
     "message": ("Missouri DOR, FAQs - Pass-Through Entity Tax, verbatim: 'Yes. The filing of the "
                 "MO-PTE does not substitute for a partnership filing its MO-1065 or an S corporation "
                 "filing its MO-1120S.' An electing partnership files FORM MO-1065 AND FORM MO-PTE; "
                 "an electing S corporation files FORM MO-1120S AND FORM MO-PTE. Form MO-PTE Part A "
                 "Lines 3 and 9 literally draw from 'Form MO-1065, Line 11 [Line 12]' and require "
                 "copies as attachments, and sections 143.581 and 143.471 impose their filing duties "
                 "without regard to a section 143.436 election."),
     "notes": ("⚠⚠ THIS IS THE OPPOSITE OF VIRGINIA, where Form 502PTET is filed INSTEAD OF Form 502. "
               "PORTING THE VIRGINIA PATTERN WOULD LEAVE EVERY ELECTING MISSOURI CLIENT'S FILING "
               "INCOMPLETE. Campaign D-12.")},
    {"diagnostic_id": "D_MO_PTE_NOT_EFILEABLE", "severity": "info",
     "title": "Form MO-PTE cannot be e-filed and its tax cannot be paid electronically (R1)",
     "condition": "any Form MO-PTE is prepared",
     "message": ("Missouri does not accept Form MO-PTE through Modernized e-File. The Department "
                 "requires the return to be MAILED to P.O. Box 3080, Jefferson City, MO 65105-3080 "
                 "(the Department also accepts a PDF e-mailed to pteincome@dor.mo.gov), with PAYMENT "
                 "BY CHECK, MONEY ORDER OR CASHIER'S CHECK on Form MO-PTEV or Form MO-PTEAP. Forms "
                 "MO-1065 and MO-1120S MAY be filed electronically. This product prepares and "
                 "assembles the return for mailing; IT DOES NOT AUTOMATE THE DEPARTMENT'S E-MAIL "
                 "SUBMISSION CHANNEL, which would carry member Social Security numbers unencrypted. "
                 "The preparer chooses the channel."),
     "notes": ("Campaign D-12 A6 -- A PRIVACY DECISION, NOT A TAX ONE. The finding itself is settled "
               "six independent ways (FAQ, the 2026-03-31 form face, a 9-page instruction sweep, both "
               "DOR MeF pages, and Drake KB 18013). ⚠ 'Paper-only' overstates it: the e-mailed PDF is "
               "sanctioned. MeF scope covers MO-1065 + MO-1120S ONLY; MO-PTE rides the "
               "substitute-forms track (Form 4349 + Form 5629 + the 10x6 grid + the 2-D barcode "
               "spec).")},
    {"diagnostic_id": "D_MO_TC_POISONS_CREDIT", "severity": "error",
     "title": "⚠⚠ Entity-level tax credits REDUCE every member's PTE tax credit",
     "condition": "Form MO-PTE Line 11 is greater than zero",
     "message": ("Using a Missouri miscellaneous tax credit at the entity level DESTROYS "
                 "dollar-for-dollar owner credit. Form MO-PTE instructions, Line 11: 'miscellaneous "
                 "tax credits reduce tax liability under the SALT Parity Act, RATHER THAN "
                 "CONSTITUTING TAX PAID, and therefore do not qualify as payments for purposes of "
                 "calculating the PTE credit for a member.' 12 CSR 10-2.436(11): the member's credit "
                 "is 'computed based on the member's direct and indirect pro rata share of THE TAX "
                 "ACTUALLY PAID ... If an affected business entity reduces its tax liability ... by "
                 "use of tax credits, other than a credit for payment or overpayment of this tax, the "
                 "affected business entity's tax actually paid WILL GENERALLY BE REDUCED.' Part B "
                 "Column 6 is the pro rata share of Line 12 'TO THE EXTENT PAID.' REVIEW THE MEMBER "
                 "IMPACT WITH THE CLIENT BEFORE CLAIMING AN ENTITY-LEVEL CREDIT."),
     "notes": ("⚠ A LIVE CLIENT-HARM PATH, NOT A ROUNDING ITEM (campaign D-12 C5). The form has NO "
               "FIELD for tax actually paid, so this product derives one. ⚠ OPEN (U20): whether the "
               "Line 13 excess REFUNDABLE credit counts as tax actually paid is unanswered by the "
               "Department; this build does not count it. Confirm with the Department.")},
    {"diagnostic_id": "D_MO_PTE_UNPAID_CREDIT_POOL", "severity": "warning",
     "title": "The members' credit pool is TAX ACTUALLY PAID, which is less than Line 12 here",
     "condition": "cash payments applied are less than Form MO-PTE Line 12",
     "message": ("Form MO-PTE Part B Column 6 is each member's pro rata share of Line 12 'TO THE "
                 "EXTENT PAID.' This return shows a balance due or a partial payment, so the members' "
                 "credit pool is SMALLER THAN LINE 12. Confirm the amount actually paid before "
                 "issuing member reports -- every member's Missouri return depends on it."),
     "notes": "U20. The form provides no field for this; the figure is derived."},
    {"diagnostic_id": "D_MO_WH_SURVIVES_ELECTION", "severity": "error",
     "title": "⚠⚠ The PTE election does NOT switch off nonresident withholding",
     "condition": "the election is made and the entity has a nonresident individual owner",
     "message": ("12 CSR 10-2.436(8), verbatim: 'The election to become an affected business entity "
                 "DOES NOT RELIEVE a partnership or S corporation of its withholding obligations "
                 "under section 143.411.5, RSMo, or section 143.471.6, RSMo, respectively.' An "
                 "electing Missouri entity pays 4.7 percent entity tax AND withholds 4.7 percent on "
                 "the same income, and must still file Forms MO-1NR and MO-2NR. THIS RULE APPEARS "
                 "NOWHERE ON FORM MO-PTE, NOWHERE IN ITS INSTRUCTIONS AND NOWHERE IN THE DEPARTMENT'S "
                 "FAQ -- only in the regulation. Confirm with the Department; this costs clients cash "
                 "twice on the same income."),
     "notes": ("Campaign D-12 C6 / U21. A tension sits alongside it: 143.436.6 relieves a nonresident "
               "individual member of the FILING obligation where the entity files and pays, and 'not "
               "otherwise required to file' is a PRECONDITION of two of the five withholding "
               "exceptions -- but is not itself an exception. THE REGULATION RESOLVES IT AGAINST THE "
               "TAXPAYER: WITHHOLD ANYWAY.")},
    {"diagnostic_id": "D_MO_CAPGAIN_ELECTION_TRAP", "severity": "info",
     "title": "Missouri capital gain and the pass-through entity election - for your consideration",
     "condition": ("the election is made AND Line 1 carries material capital gain AND a Missouri "
                   "individual member exists"),
     "message": MO_CAPGAIN_ADVISORY_TEXT,
     "notes": ("⚠⚠ ADVICE LAYER ONLY. CAMPAIGN D-12 C4: ENCODE NOTHING -- no optimiser, no "
               "recommendation, no automatic election, no computation of the interaction. D-10 ruled "
               "the spec question: BUILD TO THE FORM, no entity-level capital-gain subtraction "
               "anywhere. ⭐ Supporting fact: the MO-PTE form was re-stamped 2026-03-31, AFTER "
               "enactment of 143.121.3(14) and AFTER the amended regulation took effect, and STILL "
               "has no capital-gain line. ⭐ And 143.121.3(14)(b) grants entity-level relief only "
               "behind a 4.5% rate trigger -- if the 143.436 import already delivered it, (b) would "
               "be superfluous. Ken sets the final wording.")},
    {"diagnostic_id": "D_MO_CAPGAIN_TRIGGER_TRIPWIRE", "severity": "warning",
     "title": "⚠ STALENESS TRIPWIRE - 143.121.3(14)(b) switches on below a 4.5% top rate",
     "condition": "Missouri's top individual rate for the tax year is 4.5 percent or less",
     "message": ("Section 143.121.3(14)(b), RSMo grants a 100 percent capital-gain subtraction to 'an "
                 "entity subject to tax pursuant to section 143.071' for all tax years beginning on "
                 "or after January first of the tax year FOLLOWING the year in which Missouri's top "
                 "individual rate reaches four and one-half percent or less. Missouri's top rate for "
                 "2025 is 4.7 percent, so the provision is NOT yet operative and Form MO-PTE "
                 "correctly carries no capital-gain line. WHEN THE RATE REACHES 4.5 PERCENT, "
                 "RE-VERIFY THIS ENTIRE ANALYSIS -- the form, the instructions and the campaign "
                 "ruling."),
     "notes": ("A dated, foreseeable change that belongs on the TY-rollover re-verification checklist. "
               "mo_capital_gain_entity_relief_active() EVALUATES the trigger rather than assuming it.")},
    {"diagnostic_id": "D_MO_L5_L6_SOURCING", "severity": "info",
     "title": "⚠⚠ Line 5 and Line 6 source Missouri income DIFFERENTLY - and that is expected",
     "condition": "both Form MO-MS PTE and Schedule PTE-BD are completed",
     "message": ("Form MO-PTE Line 5 sources under section 143.455, RSMo -- a receipts factor with "
                 "market sourcing. Schedule PTE-BD Column (C), which produces Line 6, sources under a "
                 "QUALITATIVE place-of-production test: 'The source of income is the place where the "
                 "income is produced. An item is from Missouri sources if the item was produced by an "
                 "overall effort centered in Missouri. In general, if the \"BRAINS\" OF THE OPERATION "
                 "resulting in the item are located in Missouri, that item is from Missouri sources.' "
                 "The two tests are NOT COMMENSURABLE, they sit on ADJACENT LINES of the same return, "
                 "and both feed Line 9. A difference between them is NOT an error. Review each "
                 "computation on its own terms."),
     "notes": ("⚠⚠ CAMPAIGN D-12 C3: DO NOT FORCE THEM TO RECONCILE. The 'brains' test appears NOWHERE "
               "in 143.455 and is not mentioned by 12 CSR 10-2.190 or 12 CSR 10-2.255. U17 IS FULLY "
               "OPEN. ⚠ Contrast D_MO_NRP_MSPTE_DELTA, which is EXPECTED-ZERO and whose non-zero "
               "delta IS an error -- the two diagnostics mean OPPOSITE things and must stay separate.")},
    {"diagnostic_id": "D_MO_MSPTE_L4_ZERO_OR_NEG", "severity": "error",
     "title": "⚠ MO-MS PTE Line 9 divides by Line 4, and Line 4 is zero or negative - prepare manually",
     "condition": "Form MO-MS PTE Part 1 Line 4 is zero or negative and Lines 4-9 are required",
     "message": ("Form MO-MS PTE Part 1 Line 9 divides Line 8 by Line 4, and the instructions "
                 "expressly require the schedule 'EVEN IF THIS BALANCE IS ZERO OR NEGATIVE.' A zero "
                 "denominator is undefined; a NEGATIVE denominator INVERTS THE SIGN of the resulting "
                 "percentage relative to the intended allocation. Neither the form nor the "
                 "instructions address either case. THIS PRODUCT WILL NOT GUESS: compute Line 9 and "
                 "Form MO-PTE Line 5 manually and document the basis."),
     "notes": ("U14 / campaign D-12 Group D. Do NOT silently return 0 percent or 100 percent. Settle "
               "by a DOR example or a full reading of 12 CSR 10-2.076.")},
    {"diagnostic_id": "D_MO_L5_ROUNDED_PRODUCT_WINS", "severity": "info",
     "title": "MO-PTE Line 5 is L4 x round(percentage, 3) - not MO-MS PTE Line 8",
     "condition": "Form MO-MS PTE Lines 4 through 9 are completed",
     "message": ("Form MO-MS PTE computes Line 8 directly and then BACK-SOLVES a percentage at Line 9, "
                 "which Form MO-PTE Line 5 asks you to round to three decimal places ('such as 12.345 "
                 "percent') and multiply by Line 4. The round trip loses precision, so Line 4 times "
                 "the rounded percentage WILL NOT EQUAL Line 8 exactly. Form MO-PTE Line 5's own "
                 "label settles it: 'Multiply Line 4 by the percentage.' THE ROUNDED PRODUCT IS LINE "
                 "5. Do not shortcut to MO-MS PTE Line 8."),
     "notes": ("⚠⚠ DISAMBIGUATION RECORDED SO IT CANNOT PROPAGATE: the Gate-1 ruling as restated says "
               "'MO-MS PTE Line 5 = L4 x round(L9, 3)', but MO-MS PTE's OWN Line 5 is "
               "`Nonapportionable income - Everywhere`, a direct-entry input to Line 6. The product "
               "belongs to MO-PTE LINE 5. Substance unaffected; the line label is not. ⚠ The DOR "
               "states NO TIE-BREAK for the three-decimal rounding; ROUND_HALF_UP here is a declared "
               "ENGINEERING DECISION.")},
    {"diagnostic_id": "D_MO_U11_MILEAGE_TRIGGER", "severity": "error",
     "title": "⚠ U11 - the two instruction books state the MO-MS PTE Lines 4-9 trigger OPPOSITELY",
     "condition": "apportionment Method Three, Four, Five or Six is selected on Form MO-MS PTE",
     "message": ("The Form MO-PTE instructions say to complete Form MO-MS PTE Part 1 Lines 4 through 9 "
                 "'IF THE MILEAGE PERCENTAGE on Form MO-MS PTE, Page 1, IS APPLICABLE, or if the "
                 "taxpayer has included any item of income to be allocated ...'. The parallel Form "
                 "MO-MSS / Form MO-1120S text says '... IS INAPPLICABLE or if there is any income to "
                 "be allocated ...'. THE SAME SENTENCE WITH THE OPPOSITE CONDITION. One is inverted "
                 "and no published source resolves which. THIS PRODUCT WILL NOT DECIDE IT: determine "
                 "whether Lines 4 through 9 apply and document the basis."),
     "notes": ("mo_ms_pte_lines_4_9_required() RAISES rather than guessing. Settle by a DOR "
               "correction. ⚠ Related defect: the MO-PTE instructions also send the mileage "
               "percentage to 'Form MO-PTE, Line 4' -- a DOLLAR Balance. Build to the MO-MS PTE face: "
               "it belongs at Line 5 Percent.")},
    {"diagnostic_id": "D_MO_BD_L8_NEGATIVE_ROW", "severity": "warning",
     "title": "Schedule PTE-BD Column (C) has a negative row - Line 8's wording is ambiguous",
     "condition": "any Schedule PTE-BD Column (C) row for Lines 1 through 7 is negative",
     "message": ("Schedule PTE-BD Line 8 reads 'Total of Column (C), Lines 1-7, REDUCED BY ANY "
                 "NEGATIVE AMOUNTS, BUT NOT BELOW $0', and the instruction restates it identically. "
                 "That admits two readings: SUM EVERYTHING THEN FLOOR THE TOTAL AT ZERO, or DROP THE "
                 "NEGATIVE ROWS THEN SUM -- which would ignore losses entirely and INFLATE the "
                 "deduction. This product builds SUM-THEN-FLOOR, supported by section 143.022.1, "
                 "RSMo ('the income greater than zero ... limited to the Missouri source net profit "
                 "FROM THE COMBINATION OF' the four federal schedules). The form also gives NO SIGN "
                 "CONVENTION for Lines 6 and 7, which are deductions. REVIEW LINE 8 BEFORE FILING."),
     "notes": ("U15 / campaign D-12 Group D. The alternative reading is recorded in "
               "pte_bd_line8()['alternative_reading_not_built'] and is NOT used. Settle by a DOR "
               "worked example.")},
    {"diagnostic_id": "D_MO_BD_COLUMN_A_CARVEOUT", "severity": "info",
     "title": "Schedule PTE-BD Column (A) excludes owner-level-subtractable income (U16)",
     "condition": "Schedule PTE-BD is completed",
     "message": ("Column (A) instruction: 'do not include on Column (A), Lines 1 through 7, ANY "
                 "BUSINESS INCOME THAT WOULD, IGNORING SECTION 143.022, RSMo, BE SUBTRACTABLE OR "
                 "DEDUCTIBLE FOR INDIVIDUAL PARTNERS OR SHAREHOLDERS in arriving at their Missouri "
                 "taxable incomes', with Agricultural Disaster Relief as its only example. Read "
                 "literally this also excludes capital gain that is 100 percent subtractable to an "
                 "individual owner under section 143.121.3(14)(a) -- SHRINKING THE DEDUCTION while "
                 "the same gain remains in the Form MO-PTE Line 1 tax base. Review Column (A) with "
                 "the client."),
     "notes": ("U16 -- it cuts the OPPOSITE way from the capital-gain question and compounds it. ⭐ Its "
               "existence is also evidence FOR campaign D-10: if the Department believed owner-level "
               "subtractions were imported into the PTE base wholesale, this carve-out would be "
               "redundant, which implies the Department handles them SELECTIVELY AND BY NAME.")},
    {"diagnostic_id": "D_MO_ABE_REP_MISSING", "severity": "error",
     "title": "⚠ No Affected Business Entity Representative - THE ELECTION IS INEFFECTIVE (R10)",
     "condition": "the election box is checked and no representative is designated for the tax year",
     "message": ("An election to become an Affected Business Entity is INEFFECTIVE unless a person has "
                 "been designated as the Affected Business Entity Representative for the tax year AT "
                 "OR BEFORE THE TIME OF THE ELECTION (12 CSR 10-2.436(2)). Designate on FORM 2827 OR "
                 "FORM 2827 PTE, or check the re-designation box ONLY IF the signer has authority to "
                 "re-designate. ONLY ONE NATURAL PERSON may serve, and that person must have a "
                 "working e-mail address, telephone number and physical address. The representative "
                 "has SOLE AUTHORITY and the members are BOUND by those actions (section "
                 "143.436.13(1), RSMo)."),
     "notes": ("⚠ The MO-PTE instructions name only Form 2827; the regulation names Form 2827 AND Form "
               "2827 PTE (defect #11) -- SUPPORT BOTH. An all-members-sign alternative exists and "
               "requires a schedule carrying the signature, printed name, phone number, ownership "
               "percentage and signature date for EACH AND EVERY member.")},
    {"diagnostic_id": "D_MO_OPTOUT_RECOMPUTE", "severity": "warning",
     "title": "An opt-out forces a FULL RETURN-LEVEL RECOMPUTATION, not a member flag",
     "condition": "the opt-out box is checked or any member is marked opted out",
     "message": ("12 CSR 10-2.436(12)(D) requires Form MO-PTE Line 1, every Part A modification, "
                 "Schedule PTE-BD and the Part B credit split to be recomputed AS THOUGH THE OPT-OUT "
                 "MEMBER'S ITEMS DID NOT EXIST. Line 1: 'must not include any items of income or "
                 "deduction allocable to an opt-out member.' Line 6: 'remove from the computation any "
                 "opt-out member(s)' allocable items.' Part B Column 5 then carries a RE-GROSSED-UP "
                 "CREDIT PERCENTAGE that no longer matches any Schedule K-1: the Department's own "
                 "example is an opt-out member at 30 percent and a participating member at 10 "
                 "percent, giving that member 14 percent (10 divided by 70). ATTACH THE FEDERAL "
                 "SCHEDULE K-1 FOR EACH OPT-OUT MEMBER."),
     "notes": ("Campaign D-12 Group D: store the K-1 percentage and the credit percentage as TWO "
               "SEPARATE FIELDS and never overwrite one with the other. ⚠ The availability gate is "
               "CONJUNCTIVE -- the un-extended deadline must fall on or after 2025-08-28 AND the "
               "original return must not yet have been filed by that date.")},
    {"diagnostic_id": "D_MO_OPTOUT_EXAMPLE_ROUNDING", "severity": "warning",
     "title": "⚠ The DOR's own 10 / 70 = 14% example is rounded against its own column rule",
     "condition": "any member has opted out and Part B Column 5 is re-grossed",
     "message": ("Form MO-PTE Part B Column 5 instructs 'Round the percentage to the nearest TWO "
                 "DECIMAL PLACES', and then illustrates the opt-out re-gross-up with 'that "
                 "non-opt-out member's new credit percentage is 14% (10% divided by 70%)'. "
                 "10 divided by 70 is 14.285714..., which is 14.29 PERCENT AT TWO DECIMAL PLACES -- "
                 "not 14.00. The Department's illustration is rounded to a whole number, "
                 "contradicting the rounding rule printed for the very column it illustrates. This "
                 "product computes at TWO DECIMAL PLACES, per the printed column rule, because "
                 "Column 5 must foot to 100.00 percent across the participating members after the "
                 "re-gross-up and a whole-number allocation does not reliably close. REVIEW THE "
                 "COLUMN 5 TOTAL BEFORE FILING."),
     "notes": ("⚠ THIS DEFECT IS NOT IN THE SOURCE BRIEF -- it was surfaced by the validation "
               "harness while reproducing the ruling's own named unit test, and it is ESCALATED as "
               "an UNDER-SPECIFIED UNIT TEST rather than an error in the ruling's substance. The "
               "two-field rule the ruling was protecting (store the K-1 percentage and the credit "
               "percentage separately, never overwriting one with the other) is unaffected. ⚠ It "
               "compounds D_MO_ROUNDING_TIEBREAK: the Department publishes no tie-break for any of "
               "its three rounding conventions either.")},
    {"diagnostic_id": "D_MO_OPTOUT_MEMBER_FORMS", "severity": "error",
     "title": "Form MO-PTENR / Form MO-PTE Opt-Out are the MEMBER's filings (R8)",
     "condition": "any member has made an opt-out election",
     "message": ("Missouri requires the OPT-OUT MEMBER -- not the entity -- to file Form MO-PTENR "
                 "(nonresident) or Form MO-PTE Opt-Out (resident) with the Department by THE EARLIER "
                 "OF the original un-extended Form MO-PTE due date OR the actual filing date of the "
                 "Form MO-PTE, and to furnish a copy to the entity. This product does not prepare "
                 "those forms. THE ENTITY-SIDE RECOMPUTATION IS COMPUTED; only the member's form is "
                 "deferred."),
     "notes": ("⚠ The published Form MO-PTE Opt-Out carries an INCORRECT SCANLINE -- barcode "
               "*25329010001*, which is Form MO-3NR's, printed above human-readable 25125010001, on a "
               "FINAL form re-stamped 2026-03-27. PRINT NO SCANLINE AT ALL ON IT IN v1: reproducing a "
               "wrong barcode would route the document to the wrong process, and correcting it would "
               "deviate from the published form. (U27; campaign D-12 Group D)")},
    {"diagnostic_id": "D_MO_PTE_NO_DEPR_LINE", "severity": "warning",
     "title": "⚠ Form MO-PTE has NO depreciation line - a 2002-03 residual needs the Line 9 write-in",
     "condition": "a live section 143.121.3(7) or .3(9) modification exists for an electing entity",
     "message": ("Sections 143.121.3(7) and 143.121.3(9), RSMo remain live subtractions for property "
                 "purchased between July 1, 2002 and June 30, 2003, and sections 143.436.3(1) and "
                 ".4(1) import 'any modification made pursuant to sections 143.121 and 143.141'. BUT "
                 "FORM MO-PTE HAS NO DEPRECIATION LINE OF ANY KIND, and its instructions are silent. "
                 "Report the amount as an 'Other adjustment' on Page 3, Part A, Line 9 with a written "
                 "explanation. NO ADJUSTMENT IS REQUIRED FOR POST-2003 PROPERTY: Missouri conforms to "
                 "federal bonus depreciation and IRC 179 with no add-back."),
     "notes": ("N5 / U18; RED-DEFER R5. Closed at the statute: 143.121.2(3), the add-back itself, is "
               "window-limited. ⚠ NO MISSOURI 179 CONSTANT MAY EVER BE ENCODED and no shadow "
               "depreciation book exists.")},
    {"diagnostic_id": "D_MO_501C_ROSTER", "severity": "error",
     "title": "105.1500 RSMo vs 'All must be listed' - a PREPARER DECISION (R13)",
     "condition": "any member is an entity exempt under IRC 501(c)",
     "message": ("Section 105.1500, RSMo -- printed on page 4 of Form MO-PTE itself -- prohibits the "
                 "Department from REQUIRING a list identifying a person as a member, supporter, "
                 "volunteer or donor of a section 501(c) organization, 'NOTWITHSTANDING ANY "
                 "PUBLICATION, WEBPAGE, FORM, INSTRUCTION, REGULATION, OR STATEMENT SHARED BY THE "
                 "DEPARTMENT'. Form MO-PTE Part B Column 1 says 'Name of each member. ALL MUST BE "
                 "LISTED.' DECIDE WITH THE CLIENT what is reported in Column 1. This product will "
                 "neither auto-populate nor auto-suppress the member's identity."),
     "notes": "W17. Ken sets the default. It also touches the Line 22 trust-fund donation grid."},
    {"diagnostic_id": "D_MO_PTE_AMENDED_CASCADE", "severity": "error",
     "title": "An amended MO-PTE can eliminate EVERY member's credit (R7)",
     "condition": "the Amended Return box is checked on Form MO-PTE",
     "message": ("An amended Form MO-PTE must RESTATE THE ENTIRE RETURN using corrected figures "
                 "('Failure to fill out the entire return will delay the processing'), and must be "
                 "filed WITHIN 90 DAYS of an amended federal partnership or S corporation return, or "
                 "within 90 days after the final determination date of federal adjustments (12 CSR "
                 "10-2.105; sections 143.601 and 143.436.12, RSMo). Attach the amended federal return "
                 "with applicable schedules; if the federal return was not amended, EXPLAIN WHY. ⚠⚠ "
                 "'AN AMENDED RETURN REDUCING PASS-THROUGH ENTITY INCOME TAX LIABILITY MAY RESULT IN "
                 "A REDUCTION OR ELIMINATION OF PTE TAX CREDITS FOR ALL MEMBERS' -- requiring each "
                 "member's Missouri return to be amended. REVIEW THE MEMBER IMPACT BEFORE FILING."),
     "notes": "An entity-level amendment cascades into every member's already-filed MO-1040."},
    {"diagnostic_id": "D_MO_PTE_EXT_EXTENDS_PAYMENT", "severity": "info",
     "title": "⭐⭐ For MO-PTE ONLY, an extension also extends the time to PAY",
     "condition": "an extension is claimed on Form MO-PTE",
     "message": ("'AN EXTENSION OF TIME TO FILE WILL EXTEND THE TIME FOR PAYMENT OF THE TAX. The "
                 "pass-through entity must pay the tax on or before the extended due date to avoid a "
                 "5 percent addition to tax. However, SIMPLE INTEREST WILL BE CALCULATED FROM THE "
                 "ORIGINAL RETURN DUE DATE until the tax is paid.' Corroborated by 12 CSR 10-2.436(9) "
                 "and by Form MO-7004's own pass-through sentence. Use FORM MO-7004 (it carries a "
                 "Form MO-PTE checkbox and routes to P.O. Box 3080). The extension is capped at SIX "
                 "MONTHS from the original Form MO-PTE deadline."),
     "notes": ("⚠⚠ THE OPPOSITE of the general Missouri rule and of Virginia. DO NOT SHARE THIS BRANCH "
               "WITH MO-1065 OR MO-1120S. ⚠ U24: MO-7004's instructions say 'up to 180 days' while "
               "the MO-PTE instructions say 'not to exceed six months'; this build uses the six-month "
               "cap. ⚠ U25: the interest RATE is not printed on any form -- direct entry until "
               "dor.mo.gov/taxation/statutory-interest-rates.html is pulled.")},
    {"diagnostic_id": "D_MO_NO_ESTIMATED_TAX", "severity": "info",
     "title": "VERIFIED NEGATIVE: no estimated tax, and therefore no MO-2210 / Form 500C analogue",
     "condition": "anticipated tax payments are contemplated for a Form MO-PTE",
     "message": ("12 CSR 10-2.436(7), verbatim: 'An affected business entity is NOT SUBJECT TO an "
                 "estimated income tax declaration filing requirement, or an estimated income tax "
                 "payment requirement, with respect to the tax under section 143.436, RSMo. An "
                 "affected business entity MAY choose to make an early payment of its anticipated tax "
                 "liability for a tax year, even if the tax year is not yet complete.' Form MO-PTEAP's "
                 "own face agrees: 'These anticipated tax payments are not required.' THERE IS NO "
                 "UNDERPAYMENT-OF-ESTIMATED-TAX PENALTY REGIME AND NO EXCEPTION LADDER. ⚠ INTEREST "
                 "UNDER SECTION 143.731.2 AND THE 5 PERCENT LATE-PAYMENT ADDITION STILL APPLY."),
     "notes": ("A TRUE VERIFIED NEGATIVE -- a POSITIVE RULE saying the obligation does not exist, not "
               "an absence of found authority. ⚠ The blanket phrasing 'no underpayment-penalty regime "
               "at all' OVERREACHES and was scoped on the verification pass. This removes an entire "
               "subsystem from the build (contrast Virginia's Form 500C exception ladder).")},
    {"diagnostic_id": "D_MO_5889_STALE_COLUMNS", "severity": "warning",
     "title": "Form 5889's column references are stale - map by SUBSTANCE (R/W14)",
     "condition": "a member PTE tax credit report is generated",
     "message": ("Form 5889 instructs 'Enter the membership percentage, as reflected on Form MO-PTE, "
                 "PART B, COLUMN 4' and 'Enter the affected member's pro-rata share of the tax "
                 "imposed, as reflected on Form MO-PTE, PART B, COLUMN 5'. On the TY2025 form Column "
                 "4 is the SSN or FEIN, Column 5 is the Membership percentage and Column 6 is the "
                 "Member's PTE Tax Credit. MAP BY SUBSTANCE: membership percentage from COLUMN 5, "
                 "member credit from COLUMN 6. Form 5889 is OPTIONAL -- Form MO-TC's SPA row accepts "
                 "'Fed. K-1, Form 5889 OR EQUIVALENT' -- so a Delvio-generated member report is "
                 "equally valid and is the cleaner answer."),
     "notes": ("⚠ THE DEFECT IS A YEAR OLDER THAN FIRST REPORTED. The opt-out Column 3 was inserted on "
               "the TY2024 form, and Form 5889 was revised 03-2025 -- AFTER that shift -- and still "
               "carries the pre-TY2024 numbering. A PERSISTED DEFECT THROUGH A FULL REVISION CYCLE, "
               "NOT A PUBLICATION LAG. Never reproduce the stale column numbers in help text. Note "
               "also that a separate Form 5889 is required FOR EACH TAX YEAR AND EACH MEMBER.")},
    {"diagnostic_id": "D_MO_ROUNDING_TIEBREAK", "severity": "info",
     "title": "⚠ Three rounding conventions, and the DOR states a tie-break for NONE of them",
     "condition": "any Missouri percentage is rounded",
     "message": ("Missouri's pass-through lane uses THREE different rounding conventions: WHOLE "
                 "NUMBERS on the Form MO-1065 and Form MO-1120S Page 3 owner grids, TWO DECIMAL "
                 "PLACES on Form MO-PTE Part B Column 5, and THREE DECIMAL PLACES on the "
                 "apportionment percentage at Form MO-PTE Line 5 ('such as 12.345 percent'). THE "
                 "DEPARTMENT PUBLISHES NO TIE-BREAK RULE FOR ANY OF THEM. This product uses "
                 "round-half-up throughout and records that as an ENGINEERING DECISION, not as a "
                 "Departmental rule. Review any figure that lands exactly on a half."),
     "notes": ("Recorded because the Oregon wave proved the hazard is real in the other direction: "
               "Oregon publishes a rounded proration TABLE and a bare Python round() "
               "(round-half-to-even) silently diverges on three of twelve rows. Missouri publishes "
               "NO table and NO tie-break, so a silent banker's-rounding default here would be an "
               "INVENTED RULE. Confirm with the Department if a boundary case ever matters.")},
    {"diagnostic_id": "D_MO_FORM_5378_REFUND", "severity": "error",
     "title": "Refund of $100,000 or more - Form 5378 required (R12)",
     "condition": "Form MO-PTE Line 23 is $100,000 or more",
     "message": ("'The Department generally requires approved refunds of $100,000 OR MORE to be issued "
                 "electronically. If claiming a refund of $100,000 or more, COMPLETE FORM 5378 and "
                 "submit with your return.' This product does not prepare Form 5378."),
     "notes": ("⚠ This is the ONLY occurrence of the string 'electronic' in the entire 9-page MO-PTE "
               "instruction set -- and it is about the REFUND, not about filing or paying.")},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM MO_PTE -- TEST SCENARIOS
# ═══════════════════════════════════════════════════════════════════════════
MOPTE_SCENARIOS: list[dict] = [
    {"scenario_name": "MO-PTE is filed IN ADDITION TO the entity return - NEVER instead of it",
     "scenario_type": "edge",
     "inputs": {"entity_type": "Partnership", "election_made": True},
     "expected_outputs": {"required_returns": ["MO_1065", "MO_PTE"],
                          "virginia_pattern_applied": False},
     "notes": ("PUBLISHED DOR AUTHORITY: 'Yes. The filing of the MO-PTE does not substitute for a "
               "partnership filing its MO-1065 or an S corporation filing its MO-1120S.' ⚠⚠ THE "
               "OPPOSITE OF VIRGINIA'S 502/502PTET FORK. Porting it would leave every electing "
               "Missouri client's filing INCOMPLETE."),
     "sort_order": 1},
    {"scenario_name": "MO-PTE Page 1 chain at 4.7% - the rate comes from the FACE, not the FAQ",
     "scenario_type": "normal",
     "inputs": {"L1": 1000000, "L2": 50000, "L3": 20000, "L5": 1030000, "L6": 200000,
                "L7": 0, "L8": 0, "L11": 0},
     "expected_outputs": {"L4": 1030000, "L9": 830000, "L10": 39010.0, "L12": 39010.0,
                          "rate": 0.047},
     "notes": ("⚠ The DOR FAQ's rate table stops at 4.8% (2024) with NO TY2025 entry, so a preparer "
               "consulting it may carry 4.8% forward -- which on this return would overstate the tax "
               "by $830. NEVER SOURCE THE RATE FROM THE FAQ."),
     "sort_order": 2},
    {"scenario_name": "MO-PTE Line 7 is SIGNED - a lower-tier LOSS is added back",
     "scenario_type": "edge",
     "inputs": {"L5": 500000, "L6": 90000, "L7": -75000, "L8": 0},
     "expected_outputs": {"L9": 485000},
     "notes": ("Line 9 SUBTRACTS Line 7, so a negative Line 7 INCREASES Missouri net income -- exactly "
               "143.436.5(1). 'If this sum is negative, enter a negative figure on Line 7.' Treating "
               "Line 7 as unsigned understates the tax here by $7,050."),
     "sort_order": 3},
    {"scenario_name": "MO-PTE Line 8 FLOOR - a prior-year loss cannot drive Line 9 below zero",
     "scenario_type": "edge",
     "inputs": {"L5": 100000, "L6": 20000, "L7": 0, "L8_requested": 500000},
     "expected_outputs": {"L8": 80000, "L8_floored": True, "L9": 0, "L10": 0},
     "notes": ("'Do not use an amount of Missouri net loss from a prior tax year to reduce the "
               "Missouri net income below $0 for this tax year.' The unused $420,000 stays on the "
               "carryforward schedule."),
     "sort_order": 4},
    {"scenario_name": "MO-PTE Line 8 is $0 in the FIRST year filing Form MO-PTE",
     "scenario_type": "edge",
     "inputs": {"first_year_filing_mo_pte": True, "L8_requested": 250000},
     "expected_outputs": {"L8": 0},
     "notes": "'This is not applicable for the affected business entity's first year filing Form MO-PTE.'",
     "sort_order": 5},
    {"scenario_name": "⚠⚠ MO-TC CREDIT POISONING - Line 11 destroys the members' credit",
     "scenario_type": "failure",
     "inputs": {"L10": 100000, "L11": 40000, "cash_payments_applied": 60000},
     "expected_outputs": {"L12": 60000, "tax_actually_paid": 60000, "mo_tc_used": True,
                          "harm": True, "severity": "error"},
     "notes": ("⚠⚠ THE MEMBERS' CREDIT POOL FELL FROM $100,000 TO $60,000 BECAUSE THE ENTITY USED A "
               "$40,000 MO-TC CREDIT. 12 CSR 10-2.436(11): the credit is computed on TAX ACTUALLY "
               "PAID, and MO-TC use is not payment. A LIVE CLIENT-HARM PATH. Campaign D-12 C5."),
     "sort_order": 6},
    {"scenario_name": "MO-PTE credit pool is capped by what was ACTUALLY PAID, not by Line 12",
     "scenario_type": "failure",
     "inputs": {"L10": 80000, "L11": 0, "cash_payments_applied": 30000},
     "expected_outputs": {"L12": 80000, "tax_actually_paid": 30000, "pool_equals_l12": False,
                          "severity": "warning"},
     "notes": ("Part B Column 6 is the pro rata share of Line 12 'TO THE EXTENT PAID.' A balance-due "
               "return has a credit pool smaller than Line 12, and the form has no field for it."),
     "sort_order": 7},
    {"scenario_name": "⚠⚠ OPT-OUT RE-GROSS-UP - the DOR's 10 / 70 example, and its ROUNDING DEFECT",
     "scenario_type": "edge",
     "inputs": {"k1_percent": 10.0, "opt_out_percent_total": 30.0},
     "expected_outputs": {"k1_percent": 10.0, "credit_percent": 14.29,
                          "credit_percent_unrounded": 14.285714285714286,
                          "dor_example_whole_number": 14.0, "denominator_percent": 70.0,
                          "fields_are_separate": True},
     "notes": ("⚠⚠ THE TWO PERCENTAGES ARE SEPARATE FIELDS AND NEITHER MAY OVERWRITE THE OTHER "
               "(campaign D-12 Group D). Column 5 prints the CREDIT percentage under a label that "
               "still says `Membership %`. ⚠⚠ AND THE DEPARTMENT'S OWN EXAMPLE IS ROUNDED AGAINST "
               "ITS OWN COLUMN RULE: Column 5 says 'Round the percentage to the nearest TWO DECIMAL "
               "PLACES', and 10 / 70 = 14.285714... = 14.29, not the printed 14. This build computes "
               "at two decimals -- Column 5 must foot to 100.00% after the re-gross-up and a "
               "whole-number allocation does not reliably close -- and reproduces the Department's "
               "whole-number illustration alongside it. Defect #22, found by the harness, NOT in the "
               "source brief, ESCALATED as an under-specified unit test."),
     "sort_order": 8},
    {"scenario_name": "OPT-OUT member - Column 3 implies Column 7 and a BLANK Column 6",
     "scenario_type": "edge",
     "inputs": {"k1_percent": 30.0, "is_opt_out": True},
     "expected_outputs": {"credit_percent": None, "eligible_for_credit": False,
                          "part_b_col6_blank": True, "part_b_col7_not_eligible": True},
     "notes": ("12 CSR 10-2.436(12)(C). ⚠ SAVING CLAUSE: the member may still carry forward and redeem "
               "credits allowed for a tax year to which the opt-out did NOT apply."),
     "sort_order": 9},
    {"scenario_name": "OPT-OUT availability gate is CONJUNCTIVE - both limbs must hold",
     "scenario_type": "failure",
     "inputs": {"unextended_due_date": "2026-04-15", "original_return_filed_by_that_date": True},
     "expected_outputs": {"available": False, "limb_1_deadline_on_or_after_2025_08_28": True,
                          "limb_2_original_return_not_yet_filed": False},
     "notes": ("⚠ The second limb -- 'AND the affected business entity has not filed its original "
               "return by that date' -- was DROPPED from the first pass's transcription and restored "
               "on verification (correction #8). Encode BOTH limbs."),
     "sort_order": 10},
    {"scenario_name": "MO-MS PTE 'stop here' - no nonapportionable income, Line 5 % comes from Line 3",
     "scenario_type": "normal",
     "inputs": {"l1_missouri_receipts": 400000, "l2_total_receipts": 1000000, "l4_balance": 900000,
                "has_nonapportionable": False},
     "expected_outputs": {"L3": 40.0, "stop_here": True, "L9": None,
                          "mo_pte_l5_percent_source": "MO-MS PTE Line 3",
                          "mo_pte_l5_percent": 40.0},
     "notes": "⚠ MO-PTE Line 5 Percent has TWO DIFFERENT SOURCES. This is the short path.",
     "sort_order": 11},
    {"scenario_name": "MO-MS PTE BACK-SOLVE - Line 9 is a derived artefact, not a factor",
     "scenario_type": "normal",
     "inputs": {"l1_missouri_receipts": 400000, "l2_total_receipts": 1000000, "l4_balance": 900000,
                "l5_nonapp_everywhere": 100000, "l7_nonapp_missouri": 25000,
                "has_nonapportionable": True},
     "expected_outputs": {"L3": 40.0, "L6": 320000.0, "L8": 345000.0, "L9": 38.333,
                          "mo_pte_l5_percent_source": "MO-MS PTE Line 9"},
     "notes": ("L6 = (900,000 - 100,000) x 40% = 320,000; L8 = 345,000; L9 = 345,000 / 900,000 = "
               "38.333%. ⭐ THE PERCENTAGE IS BACK-SOLVED so that L4 x L9 approximates L8."),
     "sort_order": 12},
    {"scenario_name": "⚠ MO-PTE LINE 5 - the ROUNDED PRODUCT WINS over MO-MS PTE Line 8",
     "scenario_type": "edge",
     "inputs": {"l4_balance": 900000, "apportionment_percent": 38.3333333},
     "expected_outputs": {"rounded_percent": 38.333, "L5": 344997.0,
                          "ms_pte_l8_would_be": 345000.0, "difference": -3.0},
     "notes": ("⚠⚠ THE ROUND TRIP LOSES PRECISION and MO-PTE Line 5's own label settles it: 'Multiply "
               "Line 4 by the percentage.' ENCODE THE ROUNDING; DO NOT SHORTCUT TO LINE 8. ⚠ NOTE "
               "ALSO: the ruling as restated named 'MO-MS PTE Line 5' for this formula, but that line "
               "is `Nonapportionable income - Everywhere`, a direct-entry input. The formula belongs "
               "to MO-PTE LINE 5."),
     "sort_order": 13},
    {"scenario_name": "⚠ MO-MS PTE HARD RED - Line 4 is zero, so Line 9 cannot be computed",
     "scenario_type": "failure",
     "inputs": {"l1_missouri_receipts": 400000, "l2_total_receipts": 1000000, "l4_balance": 0,
                "has_nonapportionable": True},
     "expected_outputs": {"blocked": True, "L9": None, "mo_pte_l5_percent": None},
     "notes": ("The instructions require the schedule 'even if this balance is zero or negative' and "
               "Line 9 divides by Line 4. DO NOT SILENTLY RETURN 0% OR 100%. (U14)"),
     "sort_order": 14},
    {"scenario_name": "⚠ MO-MS PTE HARD RED - a NEGATIVE Line 4 inverts the sign of the percentage",
     "scenario_type": "failure",
     "inputs": {"l1_missouri_receipts": 400000, "l2_total_receipts": 1000000, "l4_balance": -500000,
                "l5_nonapp_everywhere": 0, "l7_nonapp_missouri": 0, "has_nonapportionable": True},
     "expected_outputs": {"blocked": True, "L9": None},
     "notes": "A negative denominator inverts the sign relative to the intended allocation. (U14)",
     "sort_order": 15},
    {"scenario_name": "PTE-BD Line 8 SUM-THEN-FLOOR - the two readings DISAGREE when a row is negative",
     "scenario_type": "failure",
     "inputs": {"column_c": {"1": 300000, "2": -80000, "3": 0, "4": 50000, "5": 0,
                             "6": -40000, "7": -30000}},
     "expected_outputs": {"L8": 200000.0, "alternative_reading_not_built": 350000.0,
                          "readings_agree": False, "any_negative_row": True,
                          "L9_at_20pct": 40000.0},
     "notes": ("⚠⚠ THE TWO READINGS DIFFER BY $150,000 OF BASE AND $30,000 OF DEDUCTION. Campaign D-12 "
               "Group D builds SUM-THEN-FLOOR, supported by 143.022.1's 'Missouri source net profit "
               "FROM THE COMBINATION OF'. The alternative is recorded, not built. (U15)"),
     "sort_order": 16},
    {"scenario_name": "PTE-BD Line 8 floors at zero when the combination is negative",
     "scenario_type": "edge",
     "inputs": {"column_c": {"1": -200000, "2": 50000, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0}},
     "expected_outputs": {"L8": 0.0, "L9_at_20pct": 0.0},
     "notes": "'...but not below $0.' 143.022.1: 'the income GREATER THAN ZERO'.", "sort_order": 17},
    {"scenario_name": "PTE-BD Line 9 - the 20% is READ OFF THE FACE, not derived from the ratchet",
     "scenario_type": "normal",
     "inputs": {"L8": 500000},
     "expected_outputs": {"L9": 100000.0, "percent": 0.20, "source": "Schedule PTE-BD Line 9 face"},
     "notes": ("143.022.4 sets only the 20% CEILING and .5 gates increases on a $150,000,000 "
               "net-general-revenue growth test. A TY2026 pass must RE-READ THE FACE, never re-derive "
               "the trigger."),
     "sort_order": 18},
    {"scenario_name": "⚠⚠ Line 5 vs Line 6 sourcing - a difference is EXPECTED and must NOT be forced",
     "scenario_type": "edge",
     "inputs": {"regime_a": "143.455", "regime_b": "pte_bd_column_c"},
     "expected_outputs": {"reconcile": False, "severity": "info", "delta": None,
                          "expected_delta": "UNDEFINED"},
     "notes": ("⚠⚠ THE SEVERE HALF OF THE SOURCING PROBLEM, AND THE U4 WORK LEFT IT UNTOUCHED. One "
               "side is formulary (143.455), the other qualitative ('brains of the operation'), and "
               "they sit on ADJACENT LINES feeding the same Line 9. U17 IS FULLY OPEN. Campaign D-12 "
               "C3: DO NOT FORCE THEM TO RECONCILE."),
     "sort_order": 19},
    {"scenario_name": "⚠ U11 - the engine REFUSES to decide whether MO-MS PTE Lines 4-9 apply",
     "scenario_type": "failure",
     "inputs": {"method": "4", "mileage_percentage_applicable": True},
     "expected_outputs": {"raises": "NotImplementedError", "diagnostic": "D_MO_U11_MILEAGE_TRIGGER"},
     "notes": ("The MO-PTE instructions say 'is APPLICABLE'; the MO-MSS / MO-1120S text says 'is "
               "INAPPLICABLE'. One is inverted and no source resolves which. DO NOT GUESS IN CODE."),
     "sort_order": 20},
    {"scenario_name": "MO-PTE DEPRECIATION - post-2003 bonus flows through with NO adjustment",
     "scenario_type": "edge",
     "inputs": {"purchase_date": "2025-08-01", "federal_bonus_taken": 2500000},
     "expected_outputs": {"missouri_modification": 0, "mo_pte_depreciation_lines": [],
                          "state_179_limit": None, "shadow_book_required": False},
     "notes": ("Closed at 143.121.2(3) -- the ADD-BACK ITSELF is window-limited to 2002-07-01 through "
               "2003-06-30. ⚠ NO MISSOURI 179 CONSTANT MAY EVER BE ENCODED. Do not port Virginia's "
               "derived state figure."),
     "sort_order": 21},
    {"scenario_name": "MO-PTE DEPRECIATION - a live 2002-03 residual has NO LINE and needs a write-in",
     "scenario_type": "failure",
     "inputs": {"purchase_date": "2003-03-01", "residual_subtraction": 12000},
     "expected_outputs": {"in_window": True, "mo_pte_line": None,
                          "route": "Part A Line 9 'Other adjustments' write-in",
                          "diagnostic": "D_MO_PTE_NO_DEPR_LINE"},
     "notes": ("143.121.3(7)/(9) remain live and 143.436.3(1)/.4(1) import 143.121 modifications, but "
               "MO-PTE HAS NO DEPRECIATION LINE. Neither the form nor the instructions say where it "
               "goes. (N5 / U18)"),
     "sort_order": 22},
    {"scenario_name": "MO-PTE has NO capital-gain line and none may be added (D-10)",
     "scenario_type": "edge",
     "inputs": {"election_made": True, "capital_gain_in_line_1": 1000000,
                "missouri_individual_member": True},
     "expected_outputs": {"entity_level_subtraction": 0, "part_a_subtraction_lines": ["6", "7", "8", "9", "10", "11"],
                          "advisory_fires": True, "advisory_computes_comparison": False,
                          "advisory_recommends": False},
     "notes": ("⚠⚠ THE ADVISORY COMPUTES NOTHING AND RECOMMENDS NOTHING (campaign D-12 C4). D-10: "
               "build to the form. ⭐ The face was re-stamped 2026-03-31, AFTER enactment, and still "
               "has no line; and 143.121.3(14)(b) defers entity relief behind a 4.5% rate trigger, so "
               "the statute's own architecture supports the form."),
     "sort_order": 23},
    {"scenario_name": "143.121.3(14)(b) TRIPWIRE - not operative at 4.7%, operative at 4.5%",
     "scenario_type": "edge",
     "inputs": {"top_individual_rate_2025": 0.047, "hypothetical_rate": 0.045},
     "expected_outputs": {"entity_relief_active_2025": False,
                          "entity_relief_active_at_4_5_pct": True},
     "notes": ("A dated, foreseeable change. When Missouri's top rate reaches 4.5% or less, "
               "143.121.3(14)(b) switches on for 143.071 entities THE FOLLOWING TAX YEAR and this "
               "whole analysis must be re-verified."),
     "sort_order": 24},
    {"scenario_name": "⚠⚠ WITHHOLDING SURVIVES THE ELECTION - 4.7% entity tax AND 4.7% withholding",
     "scenario_type": "failure",
     "inputs": {"election_made": True, "owner_kind": "individual",
                "missouri_source_income": 300000},
     "expected_outputs": {"entity_tax_on_that_income": 14100.0, "withholding_required": True,
                          "withholding_amount": 14100.0, "election_relieved_withholding": False,
                          "total_cash_out": 28200.0},
     "notes": ("⚠⚠ 12 CSR 10-2.436(8), stated ONLY in the regulation. The client pays TWICE on the "
               "same income. Campaign D-12 C6. Confirm with the Department."),
     "sort_order": 25},
    {"scenario_name": "MO-PTE Part B - an upper-tier PTE member's Column 6 is BLANK",
     "scenario_type": "edge",
     "inputs": {"member_entity_type": "partnership", "k1_percent": 25.0},
     "expected_outputs": {"part_b_col6": None, "relief_route": "MO-PTE Line 7 at the upper tier"},
     "notes": ("'If the member is a S corporation or partnership, LEAVE THIS COLUMN BLANK for that "
               "entity.' An upper-tier PTE gets relief through Line 7, not through a credit."),
     "sort_order": 26},
    {"scenario_name": "MO-PTE Page 2 - the $1.00 refund floor and the Form 5378 threshold",
     "scenario_type": "edge",
     "inputs": {"L12": 1000, "L13": 0, "L14": 1000.60, "L15": 0, "L16": 0, "L18": 0,
                "L21": 0, "L22": 0},
     "expected_outputs": {"L17": 1000.60, "L19": 1000.60, "L20": 0.60, "L23_before_floor": 0.60,
                          "L23": 0.0, "refund_floored": True, "form_5378_required": False},
     "notes": "'No refund of less than $1.00 will be made.'", "sort_order": 27},
    {"scenario_name": "MO-PTE EXTENSION - the payment rule is INVERTED for this return only",
     "scenario_type": "edge",
     "inputs": {"form_code": "MO_PTE"},
     "expected_outputs": {"missouri_form": "MO-7004", "extension_extends_payment": True,
                          "late_pay_addition_waived_if_paid_by_extended_date": True,
                          "interest_runs_from": "the ORIGINAL return due date", "max_months": 6},
     "notes": ("⭐⭐ THREE SOURCES AGREE, and this is the OPPOSITE of the general Missouri rule and of "
               "Virginia. DO NOT SHARE THIS BRANCH WITH MO-1065 OR MO-1120S. ⚠ MO-7004's own "
               "instructions say 'up to 180 days'; the six-month cap governs (U24)."),
     "sort_order": 28},
    {"scenario_name": "MO-PTE is NOT e-fileable, and Delvio does NOT automate the e-mail channel",
     "scenario_type": "edge",
     "inputs": {"form_code": "MO_PTE"},
     "expected_outputs": {"mef": False, "electronic_payment": False,
                          "channels_include_email": True,
                          "delvio_automates_email": False,
                          "payment_instruments": ["check", "money order", "cashier's check"]},
     "notes": ("⚠⚠ CAMPAIGN D-12 A6 -- A PRIVACY RULING. The e-mail channel IS sanctioned (so "
               "'paper-only' overstates the finding) but it carries member SSNs in the clear. Delvio "
               "computes and assembles; the preparer chooses the channel."),
     "sort_order": 29},
    {"scenario_name": "MO-1065 and MO-1120S ARE MeF-eligible - only the tax-computing return is manual",
     "scenario_type": "normal",
     "inputs": {"form_codes": ["MO_1065", "MO_1120S"]},
     "expected_outputs": {"mef": True, "mef_scope": ["MO_1065", "MO_1120S"],
                          "substitute_forms_track": ["MO_PTE"]},
     "notes": ("⚠⚠ THE BUILD ECONOMICS INVERT: ordinarily the PTET return is the one you rush to "
               "e-file because it moves money. In Missouri it is paper (or an e-mailed PDF) with a "
               "paper check, while the two ZERO-TAX informational returns are the MeF-eligible ones. "
               "MeF schema scope HALVES."),
     "sort_order": 30},
    {"scenario_name": "105.1500 - a 501(c) member's identity is NEVER auto-populated",
     "scenario_type": "failure",
     "inputs": {"member_is_501c": True},
     "expected_outputs": {"decision_required": True, "auto_populate": False, "auto_suppress": False,
                          "decision_owner": "PREPARER DECISION"},
     "notes": ("⚠ DO NOT SILENTLY SUPPRESS AND DO NOT SILENTLY INCLUDE. The statute is printed on page "
               "4 of the very form whose Part B Column 1 says 'All must be listed.'"),
     "sort_order": 31},
]


# ═══════════════════════════════════════════════════════════════════════════
# SHARED DIAGNOSTICS -- attached to ALL THREE specs. The cross-cutting rulings,
# the verified negatives and the RED-DEFERS.
# ⚠ EVERY RED-DEFER HAS ITS OWN DIAGNOSTIC: NO SILENT GAP, AND NOTHING SILENTLY
#   INCLUDED EITHER.
# ═══════════════════════════════════════════════════════════════════════════
MO_SHARED_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_MO_DEPR_ABSENCE_IS_A_RULING", "severity": "info",
     "title": "VERIFIED NEGATIVE: no Missouri bonus add-back and no state IRC 179 figure",
     "condition": "federal bonus depreciation or an IRC 179 deduction is claimed",
     "message": ("Missouri has NO section 168(k) bonus add-back and NO IRC 179 modification for any "
                 "property placed in service after June 30, 2003. This is closed AT THE STATUTE, not "
                 "merely at the form faces: section 143.121.2(3), RSMo -- THE ADD-BACK PROVISION "
                 "ITSELF -- is window-limited on its face to property purchased 'on or after July 1, "
                 "2002, but before July 1, 2003' and is measured against section 168 'as amended by "
                 "the Job Creation and Worker Assistance Act of 2002'. Section 143.121.3(7) carries "
                 "the identical window and section 143.121.3(9) inherits it by cross-reference. "
                 "Section 143.121 contains NO IRC 179 modification at all -- IRC 179 appears in the "
                 "Missouri pass-through lane ONLY as a distributive-share item (Form MO-NRP Part 1 "
                 "Line 12, Form MO-NRS Part 1 Line 11, Schedule PTE-BD Line 6). 100 PERCENT OBBBA "
                 "BONUS FLOWS THROUGH UNTOUCHED. THERE IS NO MISSOURI SHADOW DEPRECIATION BOOK AND NO "
                 "MISSOURI IRC 179 CONSTANT."),
     "notes": ("⚠ DO NOT PORT VIRGINIA'S DERIVED STATE IRC 179 FIGURE and DO NOT create a nullable "
               "'state depreciation adjustment' field for symmetry with other states -- a nullable "
               "field a preparer can fill is worse than no field. ⚠ Scoping correction: the 'five "
               "form faces' framing overstated the FORM-side support (four faces carry a depreciation "
               "line; the window is spelled out IN WORDS in exactly ONE document, the MO-1120S "
               "instructions). The negative does not depend on that framing.")},
    {"diagnostic_id": "D_MO_R5_DEPR_2002_03_MANUAL", "severity": "error",
     "title": "2002-03 vintage Missouri depreciation - prepare manually (R5)",
     "condition": ("MO-1065 Line 9, MO-1120S Line 10 or 11, or a disposition of pre-July-2003 property "
                   "with a Missouri basis difference"),
     "message": ("Missouri's depreciation modification applies ONLY to property purchased between July "
                 "1, 2002 and June 30, 2003 (sections 143.121.3(7) and 143.121.3(9), RSMo). This "
                 "product does not maintain a Missouri depreciation basis book for that vintage. "
                 "COMPUTE THE ADJUSTMENT MANUALLY. On FORM MO-PTE there is NO DEPRECIATION LINE AT "
                 "ALL -- report the amount as an 'Other adjustment' on Page 3, Part A, Line 9 with an "
                 "explanation. On FORM MO-1065 there is no line for the section 143.121.3(9) "
                 "disposition recovery, although Form MO-1120S has one at Line 11 -- use the Line 8 "
                 "'Other adjustments' write-in. NO RED APPLIES TO POST-2003 ASSETS: Missouri conforms "
                 "to federal bonus depreciation and IRC 179 with no add-back."),
     "notes": "N5 / N9 / U18 / U19."},
    {"diagnostic_id": "D_MO_CONFORMITY_ROLLING", "severity": "info",
     "title": "Missouri conformity is ROLLING - there is no conformity bucket to build",
     "condition": "any conformity determination is made",
     "message": ("Section 143.091, RSMo (effective 1/1/1990, UNAMENDED): federal references mean the "
                 "Internal Revenue Code 'and amendments thereto ... AS THE SAME MAY BE OR BECOME "
                 "EFFECTIVE, AT ANY TIME OR FROM TIME TO TIME, FOR THE TAXABLE YEAR.' OBBBA therefore "
                 "applies for TY2025 with NO adoption act -- none was needed and none was enacted. "
                 "The modification blocks on Forms MO-1065, MO-1120S and MO-PTE contain NO CONFORMITY "
                 "LINE OF ANY KIND. There is no Missouri analogue of a fixed-date conformity "
                 "adjustment."),
     "notes": ("⚠ THE COST OF ROLLING CONFORMITY: a future federal expensing change flows in "
               "AUTOMATICALLY AND SILENTLY, with no Missouri line that would surface it. A TY-rollover "
               "pass must re-read 143.121.2 and .3 IN FULL for newly inserted subdivisions, not "
               "merely re-read the forms.")},
    {"diagnostic_id": "D_MO_FEDERAL_LINES_UNVERIFIED", "severity": "warning",
     "title": "⚠ Every federal line reference in this spec is UNVERIFIED against the FINAL IRS forms",
     "condition": "any federal line reference is relied on",
     "message": ("Every federal line reference in the Missouri pass-through lane was transcribed from "
                 "the Missouri Department of Revenue's own TY2025 instructions and HAS NOT been "
                 "cross-checked against the FINAL TY2025 IRS forms. THE DEPARTMENT ITSELF DISCLAIMS "
                 "THE ALIGNMENT, printing on the FINAL Form MO-NRP: 'Note: At the time the Department "
                 "finalized their tax booklets, the Internal Revenue Service had not finalized the "
                 "federal income tax forms.' Affected references include Federal Form 1120S Schedule "
                 "K Line 18; Federal Form 1065 Page 6 Analysis of Net Income (Loss) Line 1; Federal "
                 "Form 1120-S Lines 5 and 22; Federal Form 1065 Page 1 Lines 10 and 22; Federal Form "
                 "4797 Part II Line 17; Federal Form 1065 Schedule K Lines 13c and 13d; Form 1040 "
                 "Schedule E Part II Line 32; and the whole MO-NRP / MO-NRS Schedule K line maps. "
                 "RE-PULL THE FINAL IRS FORMS BEFORE THE APP BUILD."),
     "notes": ("U8. The source brief says to do this cross-check BEFORE authoring, and it was not "
               "done. It is one of the reasons the seed guard refuses.")},
    {"diagnostic_id": "D_MO_R15_CITY_EARNINGS_TAX", "severity": "info",
     "title": "Kansas City / St. Louis earnings taxes - out of scope, but they belong on Line 1b (R15)",
     "condition": "the entity has Kansas City or City of St. Louis activity",
     "message": ("Kansas City (Forms RD-108 / RD-109) and the City of St. Louis (Forms E-1 / E-234) "
                 "levy 1 percent earnings taxes administered BY THE CITIES, not by the Missouri "
                 "Department of Revenue. They are separate filings through separate portals and are "
                 "not prepared by this product. ALL KANSAS CITY TAXES MUST BE FILED ELECTRONICALLY AS "
                 "OF JANUARY 1, 2025. ENTER THE AMOUNTS PAID ON LINE 1b of the Missouri return, where "
                 "they are CARVED OUT of the state and local income tax add-back."),
     "notes": ("⭐ THE SCOPE BOUNDARY IS PRINTED ON ALL THREE FORM FACES AT LINE 1b, so the state "
               "module must KNOW these taxes exist even though it does not compute them. INFO, never "
               "RED. ⚠ The three faces word the Line 1b label slightly differently -- transcribe each "
               "face's own wording.")},
    {"diagnostic_id": "D_MO_R3_MO_CR_RECIPROCAL", "severity": "error",
     "title": "A resident member of an OUT-OF-STATE PTE claims on Form MO-CR (R3)",
     "condition": "an owner reports an out-of-state pass-through entity tax",
     "message": ("A Missouri resident member of an out-of-state pass-through entity claims relief on "
                 "FORM MO-CR, subject to section 143.436.9's 'SUBSTANTIALLY SIMILAR' test (as the "
                 "director of revenue determines) and the limitations of section 143.081.2, RSMo. "
                 "⚠⚠ EXCESS CREDIT UNDER SECTION 143.436.9(2) IS NEITHER REFUNDED NOR CARRIED FORWARD "
                 "-- it DIES IN THE YEAR IT ARISES. That is the OPPOSITE of the domestic section "
                 "143.436.8 credit, whose excess carries forward WITHOUT LIMIT. Prepare manually."),
     "notes": ("⚠⚠ TWO CREDITS, TWO OPPOSITE CARRYFORWARD RULES, EASY TO CONFLATE. Form MO-CR is an "
               "INDIVIDUAL-module form -- out of scope here but a HARD DEPENDENCY.")},
    {"diagnostic_id": "D_MO_R9_CERT_GATED_CREDITS", "severity": "error",
     "title": "Certificate-gated tax credits - enter the certified amount only (R9)",
     "condition": "any Form MO-TC alpha code outside the DOR-administered block is claimed",
     "message": ("This credit is administered by an agency other than the Department of Revenue -- the "
                 "Missouri Agricultural and Small Business Development Authority, the Department of "
                 "Economic Development, the Department of Natural Resources, the Department of Social "
                 "Services, the Missouri Development Finance Board, the Missouri Housing Development "
                 "Commission, the Department of Health Division of Senior Services or the State "
                 "Treasurer -- and must be APPROVED BY THE ISSUING AGENCY before it can be claimed. "
                 "This product does not compute it: enter the certified amount and the LAST SIX "
                 "DIGITS of the benefit number from the Certificate of Eligibility."),
     "notes": ("EVERY non-DOR credit on Form MO-TC is certificate-gated. ⚠ Credit ORDERING is "
               "preparer-controlled by row position -- 'Each credit will apply against your tax "
               "liability IN THE ORDER THEY APPEAR BELOW' -- and is never engine-determined. ⚠ Any "
               "amount entered at MO-PTE Line 11 also triggers D_MO_TC_POISONS_CREDIT.")},
    {"diagnostic_id": "D_MO_R11_FORM_4458_NEXUS", "severity": "error",
     "title": "Form 4458 Business Activity Questionnaire - not prepared by this product (R11)",
     "condition": "the user asserts insufficient Missouri nexus",
     "message": ("Missouri offers FORM 4458, Business Activity Questionnaire, to support a claim of "
                 "insufficient nexus: 'If you believe you do not have sufficient nexus and you are "
                 "not liable for Missouri tax, you may complete a Form 4458.' It is not prepared by "
                 "this product. Note that 'jurisdiction to tax is not present where the state is "
                 "prohibited from imposing the tax by reason of the provisions of Public Law 86-272, "
                 "15 U.S.C.A. Sections 381-385.'"),
     "notes": "Referenced in the MO-PTE instructions; also a Form MO-1120 attachment."},
    {"diagnostic_id": "D_MO_INTEREST_RATE_UNPULLED", "severity": "warning",
     "title": "⚠ The Missouri statutory interest rate is not printed on any form (U25)",
     "condition": "interest on a late Missouri payment must be computed",
     "message": ("The statutory interest rate is NOT PRINTED ON ANY MISSOURI FORM. Every form points "
                 "to dor.mo.gov/taxation/statutory-interest-rates.html (statutory hook: section "
                 "143.731, RSMo). ENTER THE RATE MANUALLY until that page has been pulled and the "
                 "figure seeded. ⚠ For Form MO-PTE, interest runs from the ORIGINAL return due date "
                 "even where an approved extension has extended the time to PAY."),
     "notes": "U25 -- trivially fetchable, simply not yet done."},
    {"diagnostic_id": "D_MO_MAIL_ROUTING_PER_FORM", "severity": "info",
     "title": "⭐ Missouri routes by FORM, not by return - up to four P.O. boxes in one filing",
     "condition": "a Missouri pass-through filing package is assembled",
     "message": ("Forms MO-1065 and MO-NRP go to P.O. Box 3000; Forms MO-1120S, MO-NRS and MO-MSS to "
                 "P.O. Box 336; Forms MO-PTE, MO-MS PTE, Schedule PTE-BD, MO-PTEV, MO-PTEAP, MO-PTENR "
                 "and MO-PTE Opt-Out to P.O. Box 3080; Forms MO-1NR and MO-2NR to P.O. Box 555; and "
                 "FORM MO-3NR TO P.O. BOX 3815. AN ELECTING MISSOURI PARTNERSHIP WITH ONE NONRESIDENT "
                 "PARTNER MAILS TO FOUR DIFFERENT P.O. BOXES IN ONE FILING. The print and assembly "
                 "engine must model PER-FORM routing, not per-return routing."),
     "notes": ("Five distinct boxes, three distinct phone numbers and three distinct e-mail addresses "
               "across the lane.")},
    {"diagnostic_id": "D_MO_SUBSTITUTE_FORMS_TRACK", "severity": "warning",
     "title": "Form MO-PTE rides the SUBSTITUTE-FORMS track, and its scanline posture is unconfirmed",
     "condition": "a Missouri pass-through form is printed by this product",
     "message": ("Because Form MO-PTE cannot be e-filed, it carries a SUBSTITUTE-FORMS obligation "
                 "rather than an MeF one: the Department's Form 4349 letter of intent, the Form 5629 "
                 "guidelines, the published 10 x 6 grid layout specification and a separate 2-D "
                 "barcode specification all apply to any paper form this product prints. ⚠ FORMS "
                 "MO-PTE, MO-MS PTE, SCHEDULE PTE-BD, MO-1065 AND FORM 5889 CARRY NO SCANLINE AT ALL, "
                 "while fourteen other forms in the lane do. That is consistent with Form MO-PTE not "
                 "being machine-processed, but IT MUST BE CONFIRMED AGAINST THE DEPARTMENT'S "
                 "SUBSTITUTE-FORMS SPECIFICATION BEFORE PRINTING ONE."),
     "notes": ("⚠ Form MO-PTE Opt-Out prints the WRONG SCANLINE (Form MO-3NR's) -- PRINT NO SCANLINE "
               "AT ALL on that form in v1 (U27). ⚠ Forms MO-MS and MO-MS PTE both print 'Attachment "
               "Sequence No. 1120-01' -- an assembly-order COLLISION between two different forms "
               "(U13). Settle both by Form 5629 and the Department's attachment-sequence table.")},
    {"diagnostic_id": "D_MO_OWNER_EXTRACT_PACKAGE", "severity": "warning",
     "title": "⭐ There is NO Missouri K-1 - six owner-side landing points across three returns",
     "condition": "an owner package is generated for any Missouri pass-through return",
     "message": ("MISSOURI HAS NO K-1 EQUIVALENT AND NEVER HAS. Each return carries a PER-OWNER "
                 "EXTRACT OBLIGATION instead, and the owner keys the figures onto Form MO-1040, Form "
                 "MO-A or Form MO-NRI. The landing points are: MO-1065 Page 3 Column 5 -> MO-A Part 1 "
                 "Line 2 or Line 11; MO-1065 Line 13 -> MO-A Part 1 LINE 16 (a DIFFERENT line); "
                 "MO-1120S Page 3 Column 5 -> MO-1040 as an addition to or subtraction from federal "
                 "adjusted gross income; MO-NRP and MO-NRS Column (e) -> Form MO-NRI; MO-PTE Part B "
                 "Column 6 -> Form MO-TC alpha code SPA -> MO-1040 Line 42, MO-1041 Line 16 or "
                 "MO-1120 Line 17; and MO-2NR Line 2 -> MO-1040 LINE 39. THE PACKAGES ARE NOT THE "
                 "SAME SHAPE ACROSS THE THREE MODULES."),
     "notes": ("⚠ MO-1120S adds a REDACTION duty that MO-1065 does not have. ⚠ MO-1065 requires a LIST "
               "OF EXEMPT U.S. OBLIGATIONS to be provided to each partner, and warns that failure to "
               "attach the notification 'may result in the disallowance of the deduction'. ⚠ Section "
               "143.436.7 requires the member reports to be INCLUDED WITH THE PAYMENT of the tax, not "
               "merely with the return, and to cover INDIRECT pro rata shares from lower-tier "
               "entities.")},
    {"diagnostic_id": "D_MO_OPEN_ITEMS_OUTSTANDING", "severity": "warning",
     "title": "⚠ 22 open [UNVERIFIED] items remain in the Missouri pass-through research",
     "condition": "this spec is relied on for an app build",
     "message": ("The Missouri source brief carries 22 genuinely open items after its adversarial "
                 "verification pass and the U4 follow-up. The load-bearing ones are: U4 (narrowed -- "
                 "the regulatory basis for MO-NRP Part 3 direct accounting); U8 (every federal line "
                 "reference, uncross-checked against the FINAL IRS forms); U9 (the defective "
                 "withholding base summations); U11 (the inverted mileage trigger); U14 (MO-MS PTE "
                 "Line 9 with a zero or negative denominator); U15 (Schedule PTE-BD Line 8's "
                 "ambiguity); U16 (Column (A)'s owner-exempt carve-out); U17 (the 'brains of the "
                 "operation' test versus section 143.455); U20 (tax actually paid); U21 (withholding "
                 "surviving the election); U22 (disjunctive statute versus conjunctive forms); U24 "
                 "(extension routing and length); U25 (the interest rate); and U27 (the incorrect "
                 "Form MO-PTE Opt-Out scanline). EACH IS ENCODED AS A DIAGNOSTIC OR A NOTE. NONE IS "
                 "SILENTLY FILLED WITH A GUESS."),
     "notes": ("Closed on verification: U1 (e-file, six-way corroborated), U2 (opt-out vintage), U5 "
               "(the Method Two A default), U6 (the Form 5889 causation). Strengthened but open by "
               "design: U3 (capital gain -- ruled at D-10), U18 and U19 (the depreciation residual's "
               "routing; the STATUTE is closed, only the write-in destination is open). Narrowed: U4.")},
]


# ═══════════════════════════════════════════════════════════════════════════
# THE THREE SPECS
# ═══════════════════════════════════════════════════════════════════════════
FORMS: list[dict] = [
    {
        "identity": {
            "form_number": FORM_CODE_MO1065,
            "form_title": "Missouri Partnership Return of Income (Form MO-1065)",
            "entity_types": ["1065"],
            "notes": (
                "TY2025. A MODIFICATION-AND-ALLOCATION RETURN THAT COMPUTES NO TAX -- there is no tax "
                "line anywhere on the face. Two gating questions drive the whole return, and 'No' to "
                "both produces a TWO-CHECKBOX, SIGNATURE-ONLY SHORT-FORM RETURN with the federal 1065 "
                "attached. ⚠⚠ AN ELECTING PARTNERSHIP FILES THIS **AND** FORM MO-PTE -- published DOR "
                "authority, and the OPPOSITE of Virginia's 502/502PTET fork; MO-PTE Part A Lines 3 "
                "and 9 literally draw off this return's Lines 11 and 12. ⚠ NO apportionment question "
                "and NO apportionment schedule of its own: partnerships BORROW Form MO-MSS, which "
                "12 CSR 10-2.255(3) makes deliberate (the narrowed U4). ⚠ NO 163(j) machinery in "
                "either direction, NO MOHELA line and NO 143.121.3(9) disposition-recovery line, all "
                "of which MO-1120S has. ⚠ Line 13 (Agriculture Disaster Relief) sits OUTSIDE the "
                "totals and lands on MO-A Part 1 LINE 16. ⚠ The $500 related-expense rule is a FLOOR "
                "ON THE EXPENSE, not a threshold on the subtraction. Face Revised 12-2025, ModDate "
                "2025-11-05, 5 pages (3 form + 2 embedded instruction), NO SCANLINE. MeF-eligible."
            ),
        },
        "facts": MO1065_FACTS, "rules": MO1065_RULES, "rule_links": MO1065_RULE_LINKS,
        "lines": MO1065_LINES, "diagnostics": MO1065_DIAGNOSTICS + MO_SHARED_DIAGNOSTICS,
        "scenarios": MO1065_SCENARIOS,
    },
    {
        "identity": {
            "form_number": FORM_CODE_MO1120S,
            "form_title": "Missouri S-Corporation Income Tax Return (Form MO-1120S)",
            "entity_types": ["1120S"],
            "notes": (
                "TY2025. ⚠ THE TITLE LIES -- section 143.471.1 provides that an S corporation 'shall "
                "not be subject to the taxes imposed by section 143.071', so this return computes NO "
                "TAX. It is a modification-and-allocation return exactly like Form MO-1065. ⭐ "
                "QUESTION 3 IS THE APPORTIONMENT GATE AND HAS NO MO-1065 COUNTERPART. ⚠⚠ AN ELECTING "
                "S CORPORATION FILES THIS **AND** FORM MO-PTE. ⚠ The subtraction total runs Lines "
                "6-11 (MO-1065's runs 6-9) because this return carries a MOHELA line and TWO "
                "depreciation lines MO-1065 does not. ⚠⚠ Form MO-NRS derives its columns the REVERSE "
                "of Form MO-NRP -- (b) = (a) x (c) here versus (c) = (b) / (a) there -- so DO NOT "
                "SHARE A RULE. ⚠⚠ Form MO-MSS produces a PER-DISTRIBUTIVE-SHARE-ITEM percentage "
                "VECTOR, not one factor. ⚠ The withholding base as printed DOUBLE-COUNTS (5b is a "
                "subset of 5a; 8b and 8c are subsets of 8a). ⭐ Federal Form 8886 copies are "
                "MANDATORY, and the per-shareholder extract must be REDACTED -- neither has a "
                "MO-1065 analogue. ⚠ NO composite checkbox although 143.471.5 grants the right. Face "
                "Revised 12-2025, ModDate 2026-01-06, 3 form pages plus a separate 6-page instruction "
                "PDF. MeF-eligible, including as a STAND-ALONE state return."
            ),
        },
        "facts": MO1120S_FACTS, "rules": MO1120S_RULES, "rule_links": MO1120S_RULE_LINKS,
        "lines": MO1120S_LINES, "diagnostics": MO1120S_DIAGNOSTICS + MO_SHARED_DIAGNOSTICS,
        "scenarios": MO1120S_SCENARIOS,
    },
    {
        "identity": {
            "form_number": FORM_CODE_MOPTE,
            "form_title": "Missouri Pass-Through Entity Income Tax Return (Form MO-PTE)",
            "entity_types": ["1065", "1120S"],
            "notes": (
                "TY2025. ⭐ THE ONLY TAX-COMPUTING RETURN IN THE MISSOURI PASS-THROUGH LANE -- 4.7 "
                "percent at Line 10, PRINTED ON THE FACE. It carries Form MO-MS PTE and Schedule "
                "PTE-BD as COMPUTING SUB-SPECS (campaign D-12 Group B) in the reserved MS-* and BD-* "
                "line namespaces. ⚠⚠ IT IS FILED IN ADDITION TO FORM MO-1065 / FORM MO-1120S, NOT "
                "INSTEAD OF THEM -- published DOR authority, and the OPPOSITE of Virginia; Part A "
                "Lines 3 and 9 draw off a filed MO-1065 and require copies as attachments. ⚠⚠ IT "
                "CANNOT BE E-FILED AND ITS TAX CANNOT BE PAID ELECTRONICALLY -- settled six "
                "independent ways -- so the TAX-COMPUTING RETURN IS THE MANUAL ONE and MeF scope "
                "halves to MO-1065 + MO-1120S. The Department's e-mail channel is sanctioned but "
                "carries member SSNs in the clear, and campaign D-12 A6 rules that DELVIO DOES NOT "
                "AUTOMATE IT. ⚠⚠ TWO LIVE CLIENT-HARM PATHS, BOTH STATED ONLY IN REGULATIONS: an "
                "entity-level MO-TC credit DESTROYS the members' credit (12 CSR 10-2.436(11)), and "
                "the election DOES NOT switch off nonresident withholding (12 CSR 10-2.436(8)). "
                "⚠⚠ Line 5 and Line 6 SOURCE MISSOURI INCOME DIFFERENTLY, on adjacent lines feeding "
                "the same Line 9, and must NOT be forced to reconcile (U17 fully open). ⚠ The Part A "
                "subtraction list is CLOSED, Lines 6-11, with NO CAPITAL-GAIN LINE on a face "
                "re-stamped 2026-03-31 -- campaign D-10: BUILD TO THE FORM; the trap is ADVICE LAYER "
                "ONLY. ⚠ NO depreciation line of any kind, NO Food Pantry add-back, NO estimated-tax "
                "regime. ⚠ The opt-out is a RETURN-LEVEL RECOMPUTATION MODE, not a member flag. Face "
                "printed 'Revised 12-2025' but ModDate 2026-03-31 -- NEARLY THREE MONTHS NEWER THAN "
                "ITS OWN INSTRUCTIONS -- with the revision stamp NOT advanced. 4 pages, NO SCANLINE."
            ),
        },
        "facts": MOPTE_FACTS, "rules": MOPTE_RULES, "rule_links": MOPTE_RULE_LINKS,
        "lines": MOPTE_LINES, "diagnostics": MOPTE_DIAGNOSTICS + MO_SHARED_DIAGNOSTICS,
        "scenarios": MOPTE_SCENARIOS,
    },
]


# ═══════════════════════════════════════════════════════════════════════════
# FLOW ASSERTIONS -- exported as JSON and tested in delvio-tax.
# ⚠ assertion_id is CharField(20) and UNIQUE ACROSS THE WHOLE DATABASE.
# ═══════════════════════════════════════════════════════════════════════════
FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-MO-BOTH-FILED", "title": "⚠⚠ MO-PTE is filed IN ADDITION TO MO-1065 / MO-1120S",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft",
     "sort_order": 1,
     "description": ("Published DOR authority: 'Yes. The filing of the MO-PTE does not substitute for "
                     "a partnership filing its MO-1065 or an S corporation filing its MO-1120S.' "
                     "MO-PTE Part A Lines 3 and 9 draw from 'Form MO-1065, Line 11 [Line 12]' with "
                     "copies required as attachments, and 143.581 / 143.471 impose their filing "
                     "duties without regard to a 143.436 election."),
     "definition": {"rule": "R-MOPTE-BOTH + R-MO65-BOTH",
                    "check": "election implies BOTH the entity return and MO_PTE are required; never MO_PTE alone"},
     "bug_reference": "Porting Virginia's 502/502PTET fork leaves every electing Missouri client's filing incomplete"},
    {"assertion_id": "FA-MO-EFILE-INV", "title": "The tax-computing return is the one that CANNOT be e-filed",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft",
     "sort_order": 2,
     "description": ("MO-1065 and MO-1120S are MeF-eligible; Form MO-PTE is not e-fileable and not "
                     "electronically payable, settled six independent ways including both DOR MeF "
                     "pages ENUMERATING the eligible returns and omitting MO-PTE. ⚠ 'Paper-only' "
                     "overstates it -- the e-mailed PDF is sanctioned -- but campaign D-12 A6 rules "
                     "that Delvio does NOT automate that channel, because it carries member SSNs in "
                     "the clear."),
     "definition": {"rule": "R-MOPTE-EFILE",
                    "check": ("mo_submission_channels('MO_PTE')['mef'] is False AND 'e-mail' not in "
                              "delvio_automates AND MO_MEF_ELIGIBLE_FORMS == ('MO_1065','MO_1120S')")},
     "bug_reference": "Building MeF for MO-PTE, or automating an unencrypted e-mail channel carrying member SSNs"},
    {"assertion_id": "FA-MO-DEPR-NEG", "title": "VERIFIED NEGATIVE: no MO bonus add-back and no state 179",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft",
     "sort_order": 3,
     "description": ("A rule-says-no, closed at the ADD-BACK PROVISION ITSELF: 143.121.2(3) is "
                     "window-limited on its face to property purchased 2002-07-01 through "
                     "2003-06-30, measured against IRC 168 as amended by JCWAA 2002; .3(7) carries "
                     "the identical window and .3(9) inherits it. 143.121 contains NO 179 "
                     "modification -- 179 appears only as a distributive-share item on MO-NRP Part 1 "
                     "Line 12, MO-NRS Part 1 Line 11 and Schedule PTE-BD Line 6. No shadow book; no "
                     "state 179 constant; no nullable 'state depreciation adjustment' field."),
     "definition": {"rule": "R-MO65-DEPR-NEG + R-MO20S-DEPR + R-MOPTE-DEPR",
                    "check": ("MO_SECTION_179_STATE_LIMIT is None AND MO_HAS_BONUS_ADDBACK is False "
                              "AND mo_section_179_state_limit() RAISES AND "
                              "MO_DEPRECIATION_LINES['MO_PTE'] == []")},
     "bug_reference": "Porting Virginia's derived state 179 figure, or adding a nullable state depreciation field"},
    {"assertion_id": "FA-MO-U4-ZERO", "title": "⚠ MO-NRP vs MO-MS PTE is now EXPECTED-ZERO (the flip)",
     "assertion_type": "reconciliation", "entity_types": ["1065"], "status": "draft", "sort_order": 4,
     "description": ("12 CSR 10-2.190(2)(C) DELEGATES to 12 CSR 10-2.255, whose (3) puts a "
                     "partnership's nonresident-partner sourcing on 143.455 -- IDENTICAL to S "
                     "corporations -- for tax years beginning on or after 2020-01-01. The MO-NRP -> "
                     "MO-MSS cross-reference is DELIBERATE and is a HIERARCHY, not an election, which "
                     "is why no MO-MSP was ever published. ⚠⚠ THE DIAGNOSTIC'S MEANING FLIPPED: a "
                     "non-zero delta is now a PROBABLE ERROR, not normal regime disagreement."),
     "definition": {"rule": "R-MO65-SOURCE",
                    "check": ("MO_SOURCING_EXPECTATIONS[('143.455','nrp_part_3')]['expected_delta'] "
                              "== 'ZERO' AND ['reconcile'] is True")},
     "bug_reference": "Treating a MO-NRP / MO-MS PTE divergence as normal after 12 CSR 10-2.255 collapsed the regimes"},
    {"assertion_id": "FA-MO-L5-L6-SRC", "title": "⚠⚠ Line 5 and Line 6 must NOT be reconciled (U17 open)",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft",
     "sort_order": 5,
     "description": ("MO-PTE Line 5 sources under 143.455 (formulary); Line 6, via Schedule PTE-BD "
                     "Column (C), sources under a QUALITATIVE 'brains of the operation' "
                     "place-of-production test that appears nowhere in 143.455 and is not mentioned "
                     "by 12 CSR 10-2.190 or 10-2.255. ADJACENT LINES, both feeding Line 9. U17 IS "
                     "FULLY OPEN and campaign D-12 C3 forbids forcing them to reconcile."),
     "definition": {"rule": "R-MOPTE-SRC",
                    "check": ("mo_sourcing_divergence('143.455','pte_bd_column_c')['reconcile'] is "
                              "False AND its severity is 'info' AND delta is None")},
     "bug_reference": "A tolerance check that treats the L5 / L6 difference as an error the preparer must eliminate"},
    {"assertion_id": "FA-MO-TC-POISON", "title": "⚠⚠ Entity MO-TC credits reduce the members' credit pool",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S"], "status": "draft",
     "sort_order": 6,
     "description": ("MO-PTE Part B Column 6 is the pro rata share of Line 12 'TO THE EXTENT PAID', "
                     "and 12 CSR 10-2.436(11) computes the credit on 'the tax actually paid', which "
                     "'will generally be reduced' by entity-level credit use. THE FORM HAS NO FIELD "
                     "FOR TAX ACTUALLY PAID, so a derived field supplies it and a HARD diagnostic "
                     "fires whenever Line 11 > 0."),
     "definition": {"rule": "R-MOPTE-CREDIT",
                    "check": ("mo_tax_actually_paid(...)['severity'] == 'error' whenever L11 > 0, and "
                              "member_credit_pool <= L12 always")},
     "bug_reference": "Allocating Line 12 as the member credit pool after the entity used a MO-TC credit"},
    {"assertion_id": "FA-MO-WH-ELECT", "title": "⚠⚠ The PTE election does NOT relieve nonresident withholding",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft",
     "sort_order": 7,
     "description": ("12 CSR 10-2.436(8), verbatim: 'The election to become an affected business "
                     "entity does not relieve a partnership or S corporation of its withholding "
                     "obligations under section 143.411.5, RSMo, or section 143.471.6, RSMo, "
                     "respectively.' Stated ONLY in the regulation -- nowhere on Form MO-PTE, in its "
                     "instructions, or in the DOR FAQ. An electing entity pays 4.7% entity tax AND "
                     "withholds 4.7% on the same income."),
     "definition": {"rule": "R-MO65-WH + R-MO20S-WH",
                    "check": ("mo_withholding_required(..., pte_election_made=True)['required'] is "
                              "True and ['election_relieved_withholding'] is False")},
     "bug_reference": "Suspending withholding on election, as most PTET states do -- Missouri does not"},
    {"assertion_id": "FA-MO-WH-SUBSET", "title": "The withholding base suppresses MO-NRS 5b / 8b / 8c",
     "assertion_type": "reconciliation", "entity_types": ["1120S"], "status": "draft", "sort_order": 8,
     "description": ("MO-1NR defines the S-corporation base as 'the net total of the amounts listed on "
                     "Lines 1 through 10 of ... Form MO-NRS', which summed literally DOUBLE-COUNTS: "
                     "5b is a subset of 5a, and 8b and 8c are subsets of 8a. Build with the subsets "
                     "suppressed and raise requires_human_review whenever any of them is non-zero. "
                     "⚠ The partnership base has the mirror defect: 'Lines 1 through 11' over MO-NRP's "
                     "NON-CONTIGUOUS set silently EXCLUDES 179, contributions and other deductions."),
     "definition": {"rule": "R-MO20S-WHBASE + R-MO65-WHBASE",
                    "check": ("mo_nrs_withholding_base excludes 5b/8b/8c and flags "
                              "requires_human_review; mo_nrp_withholding_base excludes 12/13/13e and "
                              "reports the excluded total")},
     "bug_reference": "A literal 'Lines 1 through 10' sum over-withholds by 5b + 8b + 8c on every affected owner"},
    {"assertion_id": "FA-MO-OPTOUT-1070", "title": "The K-1 % and the credit % are TWO SEPARATE FIELDS",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft",
     "sort_order": 9,
     "description": ("MO-PTE Part B Column 5 is labelled `Membership %` but prints a RE-GROSSED-UP "
                     "CREDIT-ALLOCATION percentage whenever any member opts out, and that figure "
                     "matches no Schedule K-1. The DOR's own example is the unit test: an opt-out "
                     "member at 30% and a participating member at 10% gives that member 14% (10 / "
                     "70). Store both and never overwrite one with the other. ⚠⚠ AND THE "
                     "DEPARTMENT'S PRINTED '14%' IS ROUNDED AGAINST ITS OWN COLUMN RULE -- Column 5 "
                     "mandates TWO DECIMAL PLACES and 10 / 70 = 14.29. Compute at two decimals; "
                     "reproduce the whole-number illustration alongside. (Defect #22, found by the "
                     "harness, escalated as an under-specified unit test.)"),
     "definition": {"rule": "R-MOPTE-OPTOUT",
                    "check": ("mo_member_percentages(10.0, 30.0) returns k1_percent == 10.0, "
                              "credit_percent == 14.29 and dor_example_whole_number == 14.0 as "
                              "distinct keys")},
     "bug_reference": "Overwriting the K-1 percentage with the re-grossed credit percentage loses the K-1 tie-out"},
    {"assertion_id": "FA-MO-L5-ROUND", "title": "MO-PTE Line 5 is L4 x round(%, 3) -- not MO-MS PTE Line 8",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S"], "status": "draft",
     "sort_order": 10,
     "description": ("MO-MS PTE computes Line 8 directly and back-solves a percentage at Line 9; "
                     "MO-PTE Line 5 says 'Multiply Line 4 by the percentage', rounded to three "
                     "decimals. The round trip loses precision, and THE ROUNDED PRODUCT WINS. ⚠ The "
                     "ruling as restated named 'MO-MS PTE Line 5' for this formula, but that line is "
                     "`Nonapportionable income - Everywhere`, a direct-entry input -- the product "
                     "belongs to MO-PTE LINE 5."),
     "definition": {"rule": "R-MOPTE-L5",
                    "check": ("mo_pte_line5(L4, apportionment_percent=p)['L5'] == L4 * "
                              "round_half_up(p, 3) / 100, and MS-5 remains an input line")},
     "bug_reference": "Shortcutting MO-PTE Line 5 to MO-MS PTE Line 8 and losing the printed rounding"},
    {"assertion_id": "FA-MO-MSPTE-L4", "title": "MO-MS PTE Line 9 HARD-REDs when Line 4 is zero or negative",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft",
     "sort_order": 11,
     "description": ("Line 9 divides Line 8 by Line 4 and the instructions require the schedule 'even "
                     "if this balance is zero or negative'. Zero is undefined; negative INVERTS THE "
                     "SIGN of the percentage. Neither the form nor the instructions address either "
                     "case, so the engine must refuse rather than return 0% or 100%."),
     "definition": {"rule": "R-MOPTE-MSPTE",
                    "check": "mo_ms_pte_part1(..., l4_balance=0 or < 0)['blocked'] is True and L9 is None"},
     "bug_reference": "Silently returning 0% or 100% and mis-stating Missouri net income on a loss year"},
    {"assertion_id": "FA-MO-BD-L8", "title": "Schedule PTE-BD Line 8 builds SUM-THEN-FLOOR",
     "assertion_type": "reconciliation", "entity_types": ["1065", "1120S"], "status": "draft",
     "sort_order": 12,
     "description": ("'Total of Column (C), Lines 1-7, reduced by any negative amounts, but not below "
                     "$0' admits two readings that give different deductions. Campaign D-12 Group D "
                     "builds SUM-THEN-FLOOR, supported by 143.022.1's 'Missouri source net profit "
                     "FROM THE COMBINATION OF'. The alternative reading is RETURNED FOR THE RECORD but "
                     "never used, and a diagnostic fires on any negative Column (C) row."),
     "definition": {"rule": "R-MOPTE-BD",
                    "check": ("pte_bd_line8(...)['L8'] == max(0, sum(C1..C7)) AND "
                              "['alternative_reading_not_built'] is present and unused")},
     "bug_reference": "Dropping the negative rows before summing inflates the business income deduction"},
    {"assertion_id": "FA-MO-C11-MILE", "title": "⚠ Only Methods FOUR and SIX are mileage-driven",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft",
     "sort_order": 13,
     "description": ("143.455.14 (Method Three - Transportation) is a GROSS-EARNINGS rule and "
                     "143.455.16 (Method Five - Interstate Bridge) is a FLAT ONE-HALF rule. The "
                     "MO-MS PTE face note 'Complete mileage information below for Method Three - Six' "
                     "is therefore defective for TWO methods, not one. Corroborated by 12 CSR "
                     "10-2.045(14)(B)."),
     "definition": {"rule": "R-MO20S-C11",
                    "check": ("MO_MILEAGE_METHODS == ('4','6') AND MO_MILEAGE_NOTE_DEFECTIVE_FOR == "
                              "('3','5') AND methods 3 and 5 carry basis gross_earnings / flat_one_half")},
     "bug_reference": "The brief's own correction C3 said only Method Five was wrong; Method Three is wrong too"},
    {"assertion_id": "FA-MO-AGRI-PLACE", "title": "Agriculture Disaster Relief sits in THREE places, two behaviours",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft",
     "sort_order": 14,
     "description": ("MO-1065 Line 13 and MO-1120S Line 15 sit OUTSIDE the subtraction totals and are "
                     "separately allocated to owners, landing on MO-A Part 1 LINE 16. MO-PTE Line 10 "
                     "is INSIDE the Line 12 subtraction total and reduces the entity's tax base "
                     "directly. Same statute (143.121.3(10)), three placements, two behaviours -- and "
                     "TWO SPELLINGS: `Agriculture` on the first two faces, `Agricultural` on MO-PTE."),
     "definition": {"rule": "R-MO65-L13 + R-MO20S-L15 + R-MOPTE-PG1",
                    "check": ("MO_1065 L13 and MO_1120S L15 are line_type informational and outside "
                              "the totals; MO_PTE A10 is inside the A12 total")},
     "bug_reference": "Sharing one Agriculture-Disaster-Relief rule across the three forms changes the tax base"},
    {"assertion_id": "FA-MO-NRP-NRS", "title": "⚠⚠ MO-NRP and MO-NRS derive their columns INVERSELY",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft",
     "sort_order": 15,
     "description": ("MO-NRP: '(c) is determined by DIVIDING Column (b) by Column (a)'. MO-NRS: "
                     "'MULTIPLY the amount in Column (a) by the percent in Column (c)', with (c) "
                     "supplied by MO-MSS Line 3. Two identical-looking five-column grids, two inverse "
                     "arithmetics. ⚠ And MO-NRS Column (c) is a VECTOR indexed by distributive-share "
                     "line, because MO-MSS computes a DIFFERENT percentage for any item partly "
                     "allocated as nonapportionable income."),
     "definition": {"rule": "R-MO65-SOURCE + R-MO20S-NRS + R-MO20S-MSS",
                    "check": ("mo_nrp_columns derives col_c from col_b/col_a; mo_nrs_columns derives "
                              "col_b from col_a x col_c; no rule is shared between them")},
     "bug_reference": "One shared five-column rule inverts the Missouri-source figure on one of the two forms"},
    {"assertion_id": "FA-MO-500-FLOOR", "title": "The $500 related-expense rule is a FLOOR ON THE EXPENSE",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft",
     "sort_order": 16,
     "description": ("'The expenses must equal or exceed $500. If less than $500, enter zero.' Below "
                     "$500 the EXPENSE is dropped and the GROSS amount survives, which makes the "
                     "modification LARGER, not smaller. The boundary is INCLUSIVE at exactly $500. It "
                     "applies to the 2a/2b and 6a/6b pairs on all three forms -- but NOT to 1a/1b, "
                     "which is the KC / St. Louis city carve-out."),
     "definition": {"rule": "R-MO65-500FLOOR + R-MO20S-500FLR",
                    "check": ("mo_related_expense_net(10000, 400)['net'] == 10000 AND "
                              "mo_related_expense_net(10000, 500)['net'] == 9500")},
     "bug_reference": "Reading it as a threshold on the subtraction understates every affected modification"},
    {"assertion_id": "FA-MO-ROUND-3", "title": "⚠ Three rounding conventions, and no published tie-break",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft",
     "sort_order": 17,
     "description": ("WHOLE NUMBERS on the MO-1065 / MO-1120S Page 3 owner grids; TWO DECIMALS on "
                     "MO-PTE Part B Column 5; THREE DECIMALS on the apportionment percentage at "
                     "MO-PTE Line 5. THE DEPARTMENT PUBLISHES NO TIE-BREAK RULE FOR ANY OF THEM, so "
                     "round-half-up is recorded as an ENGINEERING DECISION rather than a Departmental "
                     "rule -- explicitly, because a silent banker's-rounding default would be an "
                     "invented rule."),
     "definition": {"rule": "R-MO65-PG3 + R-MO20S-PG3 + R-MOPTE-PARTB + R-MOPTE-L5",
                    "check": ("MO_ROUND_PAGE3_SHARE_DECIMALS == 0, MO_ROUND_PARTB_SHARE_DECIMALS == 2, "
                              "MO_ROUND_APPORTIONMENT_DECIMALS == 3, "
                              "MO_ROUNDING_TIEBREAK_IS_DOR_RULE is False")},
     "bug_reference": "Oregon's published proration table: a bare round() diverged on three of twelve rows"},
    {"assertion_id": "FA-MO-5889-SUBST", "title": "Form 5889 maps by SUBSTANCE, not by its stale columns",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"], "status": "draft",
     "sort_order": 18,
     "description": ("Form 5889 points Line 1 at 'Part B, Column 4' (the SSN/FEIN column) and Line 2 "
                     "at 'Part B, Column 5' (the Membership % column). The correct mapping is Line 1 "
                     "<- COLUMN 5 and Line 2 <- COLUMN 6. ⚠ The defect dates from TY2024, not TY2025 "
                     "-- the opt-out Column 3 was inserted then -- and Form 5889 was revised 03-2025 "
                     "AFTER the shift and still not fixed. A PERSISTED defect, not a lag. Form 5889 "
                     "is OPTIONAL, so a Delvio member report is the cleaner v1 answer."),
     "definition": {"rule": "R-MOPTE-PARTB",
                    "check": ("mo_5889_map()['form_5889_map_by_substance'] targets Columns 5 and 6, "
                              "and ['reproduce_stale_numbers_in_help'] is False")},
     "bug_reference": "Mapping 5889 Line 1 to Part B Column 4 puts an SSN where a percentage belongs"},
    {"assertion_id": "FA-MO-NO-EST", "title": "VERIFIED NEGATIVE: no estimated tax, but interest survives",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft",
     "sort_order": 19,
     "description": ("12 CSR 10-2.436(7) is a POSITIVE RULE that the obligation does not exist, "
                     "corroborated by the DOR FAQ and by MO-PTEAP's own face. There is NO MO-2210 / "
                     "Form 500C analogue and no exception ladder -- an entire subsystem removed. "
                     "⚠ BUT the blanket phrasing overreached: interest under 143.731.2 (expressly "
                     "preserved by 12 CSR 10-2.436(9)) and the 5% LATE-PAYMENT addition BOTH SURVIVE."),
     "definition": {"rule": "R-MOPTE-PG2 + R-MOPTE-EXT",
                    "check": ("no estimated-tax penalty rule, line or worksheet exists on any Missouri "
                              "PTE-lane form; MO_LATE_PAYMENT_ADDITION == 0.05 is retained")},
     "bug_reference": "Porting Virginia's Form 500C exception ladder into Missouri, or dropping the 5% addition with it"},
    {"assertion_id": "FA-MO-EXT-PAY", "title": "⭐⭐ For MO-PTE ONLY, the extension extends the time to PAY",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft",
     "sort_order": 20,
     "description": ("Three sources agree -- the MO-PTE instructions, 12 CSR 10-2.436(9) and Form "
                     "MO-7004's own pass-through sentence: an approved extension extends the time to "
                     "PAY, so no 5% addition applies if paid by the extended date, BUT INTEREST RUNS "
                     "FROM THE ORIGINAL DUE DATE under 143.731.2. That is the OPPOSITE of the general "
                     "Missouri rule and of Virginia. ⚠ MO-7004 says 'up to 180 days'; the MO-PTE "
                     "instructions say 'not to exceed six months' -- the six-month cap governs."),
     "definition": {"rule": "R-MOPTE-EXT",
                    "check": ("mo_extension('MO_PTE')['extension_extends_payment'] is True while "
                              "mo_extension('MO_1065') and ('MO_1120S') are False")},
     "bug_reference": "A shared Missouri extension routine charging the 5% addition on a timely-extended MO-PTE"},
    {"assertion_id": "FA-MO-3-SPECS", "title": "THREE TaxForm rows, with MO-MS PTE and PTE-BD as sub-specs",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft",
     "sort_order": 21,
     "description": ("Campaign D-12 Group B ratified THREE top-level codes -- MO_1065, MO_1120S and "
                     "MO_PTE -- with Form MO-MS PTE and Schedule PTE-BD as their own COMPUTING "
                     "SUB-SPECS (they compute) carried inside MO_PTE in the reserved MS-* and BD-* "
                     "namespaces, and the remaining eleven companions as attachment/record types. A "
                     "fourth Missouri TaxForm row would re-litigate that ruling."),
     "definition": {"rule": "R-MOPTE-BD + R-MOPTE-MSPTE",
                    "check": ("MO_TOP_LEVEL_SPEC_COUNT == 3 AND MO_PTE carries MS-* and BD-* lines AND "
                              "no TaxForm row exists for MO-MS PTE or Schedule PTE-BD")},
     "bug_reference": "D-9 namespacing: MO_1065 / MO_1120S must never be shortened to the federal bare codes"},
    {"assertion_id": "FA-MO-501C", "title": "105.1500 - a 501(c) member's identity is a PREPARER DECISION",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"], "status": "draft",
     "sort_order": 22,
     "description": ("Section 105.1500 RSMo, printed on Form MO-PTE page 4 and Form MO-TC page 2, bars "
                     "the Department from REQUIRING a roster identifying a member of a 501(c) entity "
                     "'notwithstanding any publication, webpage, form, instruction, regulation, or "
                     "statement shared by the Department' -- colliding with Part B Column 1's 'All "
                     "must be listed.' Neither silently suppressed nor silently included."),
     "definition": {"rule": "R-MOPTE-501C",
                    "check": ("mo_501c_roster_decision(True)['auto_populate'] is False AND "
                              "['auto_suppress'] is False AND ['decision_required'] is True")},
     "bug_reference": "Auto-populating a 501(c) member's identity, or auto-suppressing it, both override the preparer"},
]


class Command(BaseCommand):
    help = (
        "Load the Missouri PTE specs - Form MO-1065, Form MO-1120S and Form MO-PTE (TY2025). THREE "
        "forms, with Form MO-MS PTE and Schedule PTE-BD as computing sub-specs inside MO_PTE. "
        "⚠⚠ MO-PTE is filed IN ADDITION TO MO-1065 / MO-1120S (published DOR authority - do NOT port "
        "the Virginia fork) and CANNOT be e-filed, so the tax-computing return is the manual one. "
        "⚠ READY_TO_SEED IS FALSE: the Gate-1 SEED approval has not been taken for Missouri."
    )

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad Missouri PTE specs (Form MO-1065 / Form MO-1120S / Form MO-PTE, TY2025)\n"))
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
        # ⚠ Two structural invariants the guard also polices, because getting
        # either wrong would re-litigate a ruling rather than merely under-fill
        # a list.
        if len(FORMS) != MO_TOP_LEVEL_SPEC_COUNT:
            empty.append(f"FORMS has {len(FORMS)} specs; campaign D-12 Group B ratified "
                         f"{MO_TOP_LEVEL_SPEC_COUNT}")
        for spec in FORMS:
            if spec["identity"]["form_number"] in FORBIDDEN_BARE_CODES:
                empty.append(f"BARE FORM CODE {spec['identity']['form_number']!r} - campaign D-9 "
                             f"requires <ST>_<FORM> namespacing")
        if MO_SECTION_179_STATE_LIMIT is not None or MO_HAS_BONUS_ADDBACK:
            empty.append("A MISSOURI DEPRECIATION FIGURE HAS BEEN INVENTED - see the N1 banner")
        if MO_AUTOMATE_EMAIL_SUBMISSION:
            empty.append("MO_AUTOMATE_EMAIL_SUBMISSION was flipped - campaign D-12 A6 forbids it")

        if not READY_TO_SEED or empty:
            still_empty = "\n  ".join(f"- {n}" for n in empty) or "(all populated)"
            raise CommandError(
                "\nREFUSING TO SEED THE MISSOURI PTE SPECS (MO_1065 / MO_1120S / MO_PTE).\n"
                "Gate 1 has NOT been taken for Missouri: campaign D-12 (2026-08-19) approved the\n"
                "WAVE SCOPE and ruled the scope-walk items, it did NOT approve seeding these specs.\n\n"
                "WHY THIS FILE REFUSES:\n\n"
                "  (1) THE GATE-1 SEED APPROVAL IS OPEN. D-12 ratified the wave shape (three\n"
                "      Missouri top-level codes, with Form MO-MS PTE and Schedule PTE-BD as\n"
                "      computing sub-specs), the A6 privacy ruling, C3/C4/C5/C6/C11 and the Group D\n"
                "      items. It is NOT a seed approval.\n\n"
                "  (2) U8 IS UNCLOSED AND THE BRIEF SAYS TO CLOSE IT *BEFORE* AUTHORING.\n"
                "      EVERY federal line reference in this lane was transcribed from the Missouri\n"
                "      DOR's own instructions and has NEVER been cross-checked against the FINAL\n"
                "      TY2025 IRS forms - and THE DEPARTMENT ITSELF DISCLAIMS THE ALIGNMENT,\n"
                "      printing on the FINAL Form MO-NRP: 'At the time the Department finalized\n"
                "      their tax booklets, the Internal Revenue Service had not finalized the\n"
                "      federal income tax forms.' Affected: 1120S Sch K L18, 1065 p.6 Analysis L1,\n"
                "      1120-S L5 and L22, 1065 p.1 L10 and L22, 4797 Pt II L17, 1065 Sch K L13c/13d,\n"
                "      Sch E Pt II L32, and the whole MO-NRP / MO-NRS Schedule K line maps.\n"
                "      Pull the FINAL IRS Forms 1065, 1120-S, Schedules K-1, 4797 and 1125-A first.\n\n"
                "  (3) U4 IS NARROWED, NOT CLOSED, AND ITS RESIDUE IS A GATE-1 SEED QUESTION.\n"
                "      12 CSR 10-2.190(2)(C) delegates to 12 CSR 10-2.255, whose (3) puts PARTNERSHIP\n"
                "      nonresident sourcing on section 143.455 - identical to S corporations - so the\n"
                "      MO-NRP vs MO-MS PTE divergence is now EXPECTED-ZERO and a non-zero delta is a\n"
                "      PROBABLE ERROR (that diagnostic's MEANING FLIPPED). But 12 CSR 10-2.255 is a\n"
                "      CLOSED TWO-BRANCH test with NO separate-accounting branch, while Form MO-NRP\n"
                "      Part 3 prints one. The only statutory room is section 143.421.4 - 'may, ON\n"
                "      APPLICATION, authorize' - and nothing on the form or in either regulation\n"
                "      mentions an application. ⚠ THIS MUST NOT DEFAULT TO A FREE PREPARER ELECTION.\n"
                "      Ken must rule, or the Department must answer (corporate@dor.mo.gov).\n\n"
                "  (4) TWENTY-TWO OPEN [UNVERIFIED] ITEMS REMAIN, and several move cash on real\n"
                "      returns rather than merely annotating them:\n"
                "        U9  - the withholding base summations are DEFECTIVE AS PRINTED. MO-NRS\n"
                "              'Lines 1 through 10' DOUBLE-COUNTS (5b is a subset of 5a; 8b and 8c\n"
                "              are subsets of 8a); MO-NRP 'Lines 1 through 11' over a NON-CONTIGUOUS\n"
                "              line set silently EXCLUDES IRC 179, contributions and other\n"
                "              deductions. THIS DETERMINES CASH WITHHELD. A DOR worked example is\n"
                "              needed before season.\n"
                "        U11 - the MO-MS PTE Lines 4-9 trigger is stated in OPPOSITE SENSES by the\n"
                "              two instruction books ('applicable' vs 'inapplicable') and no source\n"
                "              resolves which is inverted. mo_ms_pte_lines_4_9_required() RAISES\n"
                "              rather than guessing.\n"
                "        U14 - MO-MS PTE Line 9 divides by Line 4, and the schedule is required\n"
                "              'even if this balance is zero or negative'.\n"
                "        U15 - Schedule PTE-BD Line 8 is genuinely ambiguous and the two readings\n"
                "              give different deductions.\n"
                "        U17 - Schedule PTE-BD Column (C)'s 'brains of the operation' test versus\n"
                "              section 143.455, ON ADJACENT LINES of the same return. FULLY OPEN.\n"
                "        U20 - 'tax actually paid' has NO FIELD ON THE FORM, and whether the Line 13\n"
                "              excess refundable credit counts toward it is unanswered.\n"
                "        U21 - withholding surviving the election is stated ONLY in 12 CSR\n"
                "              10-2.436(8) and nowhere the preparer would look.\n"
                "        U24 - the Department's own extension forms contradict each other, and the\n"
                "              length is stated as both 180 days and six months.\n"
                "        U25 - the statutory interest rate is not printed on any form and the rate\n"
                "              page was never pulled.\n"
                "        U27 - Form MO-PTE Opt-Out prints FORM MO-3NR's scanline over its own\n"
                "              human-readable code, on a FINAL form.\n"
                "      Every one is carried as a diagnostic or a note. NONE is filled with a guess.\n\n"
                "  (5) TWO LIVE CLIENT-HARM PATHS ARE ENCODED BUT UNCONFIRMED WITH THE DEPARTMENT.\n"
                "      Using an entity-level MO-TC credit DESTROYS the members' credit (12 CSR\n"
                "      10-2.436(11)), and the election DOES NOT switch off nonresident withholding\n"
                "      (12 CSR 10-2.436(8)) - so an electing client pays 4.7 percent entity tax AND\n"
                "      withholds 4.7 percent on the same income. BOTH ARE STATED ONLY IN THE\n"
                "      REGULATION - nowhere on Form MO-PTE, in its instructions, or in the DOR FAQ.\n"
                "      D-12 directs that both be confirmed with the Department.\n\n"
                "  (6) MO-PTE IS ON THE SUBSTITUTE-FORMS TRACK AND THAT TRACK IS NOT SET UP.\n"
                "      Because Form MO-PTE cannot be e-filed, printing it engages the Department's\n"
                "      Form 4349 letter of intent, the Form 5629 guidelines, the 10 x 6 grid layout\n"
                "      spec and the 2-D barcode spec. None has been obtained. ⚠ And Form MO-PTE\n"
                "      itself carries NO SCANLINE while fourteen other forms in the lane do - which\n"
                "      is consistent with it not being machine-processed but is UNCONFIRMED.\n\n"
                "WHAT THIS FILE DOES *NOT* REFUSE OVER, so nobody re-opens them:\n"
                "  - The e-file inversion is SETTLED (six independent sources) and A6 is RULED:\n"
                "    Delvio does NOT automate the Department's unencrypted e-mail channel.\n"
                "  - 'MO-PTE is filed IN ADDITION TO MO-1065 / MO-1120S' is PUBLISHED DOR AUTHORITY,\n"
                "    not an inference. Do NOT port Virginia's 502 / 502PTET fork.\n"
                "  - The depreciation negative is CLOSED AT THE STATUTE (section 143.121.2(3) - the\n"
                "    add-back itself is window-limited). NO Missouri IRC 179 constant may ever be\n"
                "    encoded and NO shadow depreciation book exists.\n"
                "  - The capital-gain question is RULED at campaign D-10: BUILD TO THE FORM. The\n"
                "    trap is ADVICE LAYER ONLY - encode nothing.\n\n"
                f"READY_TO_SEED = {READY_TO_SEED} (must be True to proceed)\n\n"
                f"Currently empty / placeholder:\n  {still_empty}\n\n"
                "DO NOT RELAX THIS GUARD TO SILENCE THE ERROR - fix the cause, which in every case\n"
                "above means an answer from the Missouri Department of Revenue, a Ken ruling, or a\n"
                "source pull, not an edit to this file.\n"
                "References: delvio-states/research/mo_pte_source_brief.md (its SEC. 22 VERIFICATION\n"
                "SECTION GOVERNS over the body, and SEC. 22.11 - the U4 follow-up addendum - governs\n"
                "over that) and delvio-states/DECISIONS.md D-10 and D-12.\n"
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
                # Missouri's Tier-1 conformity rows ARE seeded in prod (campaign
                # D-10, conformity_type = 'rolling'), so this must not fire
                # there. It WILL fire on a throwaway SQLite harness DB, which is
                # expected and is asserted for in validate_mo.py.
                self.stdout.write(self.style.WARNING(
                    f"  existing source {code} NOT FOUND - links to it will be skipped "
                    "(expected only on a fresh/throwaway DB; MO Tier-1 conformity is seeded in prod)"))
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
        self.stdout.write("Missouri PTE specs loaded (TY2025).")
        for spec in FORMS:
            fn = spec["identity"]["form_number"]
            self.stdout.write(
                f"  {fn}: facts {len(spec['facts'])} / rules {len(spec['rules'])} / "
                f"lines {len(spec['lines'])} / diag {len(spec['diagnostics'])} / "
                f"tests {len(spec['scenarios'])} / links {len(spec['rule_links'])}"
            )
        self.stdout.write(
            f"  shared: flow assertions {len(FLOW_ASSERTIONS)} / sources {len(AUTHORITY_SOURCES)} / "
            f"topics {len(AUTHORITY_TOPICS)} / DOR defects logged {len(MO_DOR_DEFECTS)} / "
            f"apportionment methods {len(MO_APPORTIONMENT_METHODS)} / "
            f"open [UNVERIFIED] items {MO_OPEN_ITEMS_GENUINELY_OPEN} / "
            f"live walk items {MO_WALK_ITEMS_LIVE}"
        )
        self.stdout.write("=" * 72)
