"""Load the Arizona PTE specs — Arizona Form 165 and Arizona Form 120S (TY2025).

═══════════════════════════════════════════════════════════════════════════
WHAT THIS IS — AND WHY THERE ARE ONLY TWO SPECS
═══════════════════════════════════════════════════════════════════════════
Arizona needs TWO pass-through specs, not three:

  AZ_165    Arizona Form 165,  Arizona Partnership Income Tax Return   (1065)
  AZ_120S   Arizona Form 120S, Arizona S Corporation Income Tax Return (1120S)

⚠⚠ **ARIZONA'S ELECTIVE PTE TAX NEEDS NO THIRD FORM.** Missouri, Oregon and
Massachusetts — the other three states in Wave 4 — each put their elective
entity-level tax on its OWN return (`MO_PTE`, `OR_21`, `MA_63D_ELT`). Arizona
bolted its tax onto the two returns that already existed:

  Form 165  Part 2, lines 8-40   (tax at line 25)
  Form 120S Part 2, lines 37-52  (tax at line 52, carried to Part 1 line 18)

Confirmed FOUR ways, and given EXTRA scrutiny precisely because Arizona is the
odd one out in its own wave (source brief §16.6):
  1. A.R.S. § 43-1014(A) final sentence, verbatim: "The election under this
     subsection is made by filing the business's return under this title."
  2. Question **A** on BOTH page 1s IS the election.
  3. AZDOR Pub 713: "The Department modified existing Forms 165 and 120S to
     allow partnerships and S Corporations wishing to make the PTE election..."
  4. Pub 713 FAQ "How do I make the PTE election?" names ONLY those two returns;
     every form number appearing anywhere in Pub 713 was enumerated and there is
     no Arizona PTE-specific return among them.
**DO NOT INVENT AN `AZ_PTET` SPEC.** Campaign D-12 Group B ratified two.

Spec source: `delvio-states/research/az_pte_source_brief.md` — VERIFIED
(adversarial pass 2026-08-18). ⚠ **ITS §16 VERIFICATION SECTION GOVERNS OVER THE
BODY** and this loader follows §16 everywhere they differ.
Conformity: `delvio-states/conformity/az_conformity.md` (VERIFIED 2026-08-06);
its §12 governs over its body — EXCEPT that the source brief's §8.5/§16.2
CORRECTS that brief's §4 / §12-H `$150,000` boundary (see below), and §5.6
corrects its §11 ModDate table.

NO prior RS spec exists — `api/forms/lookup/AZ_165/export/` and
`api/forms/lookup/AZ_120S/export/` both returned **404** on 2026-08-17 against a
VA_502 / bare-`500` control pair. Both greenfield; `<ST>_<FORM>` per campaign D-9.

═══════════════════════════════════════════════════════════════════════════
⚠⚠ THE SINGLE MOST IMPORTANT FACT IN THIS FILE (campaign D-12, Group B)
    THE TWO ARIZONA RETURNS ARE **NOT PARALLEL**, AND THERE IS **NO SHARED
    ARIZONA MODIFICATION ENGINE**
═══════════════════════════════════════════════════════════════════════════
Every other state in this campaign has a partnership return and an S-corp return
that are near-mirrors. **Arizona's are not.**

  Form 165  — a FULL federal→Arizona modification stack ON THE FACE:
              SCHEDULE A additions A1-A4 (A1 = *Total federal depreciation*),
              SCHEDULE B subtractions B1-B5 (B1 = *Recalculated Arizona
              depreciation*), line 5 "Partnership income adjusted to Arizona
              basis", line 6 "Net adjustment ... from federal to Arizona basis",
              three page-6 worksheets, and a **FIVE**-vintage-tier depreciation
              recomputation. PTE base = line 5 + line 9.

  Form 120S — **NONE OF IT. LINE 37 = LINE 1, UNADJUSTED.**

**THIS IS A VERIFIED NEGATIVE — "the rule says no", not "no rule found."** The
first evidence was lexical (`depreciation`/`bonus`/`168(k)`/`179` ≈ zero hits),
which is a textbook class-(b) fallacy, and a false-positive alarm was raised over
**28 `addition` + 42 `subtract*` hits** in the same 28-page book. **All 70 were
read in context** and resolve into five innocuous buckets (23 × "additional";
2 × "In addition:"; 12 × "Subtract line X from line Y"; 3 × "has no Arizona
additions to, or subtractions from, federal taxable income" — ALL THREE inside
the *Rounding Dollar Amounts* worked examples lifted from the Form 120 C-corp
book, each saying the company HAS NONE; ~18 × the owner-level net-LTCG
subtraction, ALL in the Schedule K-1 instruction section at the BACK of the book).

Three further independent proofs (source brief §16.3):
  (i)  **The Arizona modification statutes are cited ZERO times in the entire
       Form 120S book**: `43-1021` = 0, `43-1022` = 0, `43-1121` = 0,
       `43-1122` = 0. Every Title 43 section it DOES cite (43-1130.01, 43-1131,
       43-1134, 43-1138, 43-1139(B), 43-1140, 43-1142, 43-1143, 43-1144,
       43-1145, 43-1147(E)(3)(a), 43-1148, 43-1150) is an APPORTIONMENT
       provision. A book computing Arizona modifications could not avoid citing
       the modification statutes; this one never does.
  (ii) **Face comparison.** Form 120S's `Schedule A` is the APPORTIONMENT
       FORMULA. The string `Arizona basis` occurs ZERO times in its book.
  (iii) **The corporate-level base is unadjusted too**, not just the PTE base:
       line 4 = 2 + 3 straight from federal; line 11 = line 4 or line 10;
       line 12 = greater of $50 or 4.9% of line 11. Nothing added, nothing
       subtracted, anywhere in the chain.
  (iv) **A.R.S. § 43-1014(B)(1)(b)**: the S-corp base is "the total of all
       distributive income passed through to the shareholders under section
       43-1126, subsection B" — and § 43-1126(B) is a REPORTING provision.

**BUILD CONSEQUENCE: `AZ_120S` GETS NO DEPRECIATION LOGIC AND NO MODIFICATION
STACK.** `az_120s_modification()` and `az_120s_depreciation_adjustment()` RAISE.
`AZ_120S_HAS_MODIFICATION_APPARATUS` is False and `validate_az.py` pins it, so a
later contributor cannot add a 120S modification field "for symmetry."
Had this gone the other way it would have wrongly stripped every Arizona S-corp
return of its state adjustments — which is why it cost two sessions.

⚠ **The asymmetry is REAL ECONOMICS, not bookkeeping.** The individual bonus rule
is net-zero for post-2016 assets (A1 add-back and B1 subtraction cancel) — but it
does NOT cancel for the 0% / 10% / 55% pre-2017 tiers, nor for the § 43-1022(18)
disposition true-up. A partnership with an old asset base computes a DIFFERENT
PTE base than an otherwise identical S corporation. Delvio will surface it.

═══════════════════════════════════════════════════════════════════════════
THE D-12 RULINGS THAT BIND THIS FILE (Gate-1, 2026-08-19; A4 same session)
═══════════════════════════════════════════════════════════════════════════
**A1 · THE `$150,000` MEASUREMENT BASE — the only item in the wave with no safe
default.** AZDOR prints **FOUR** different bases and **four of six documents
contradict themselves INTERNALLY**:
    1. bare "taxable income"      — § 43-581(C), Form 165 instr., Form 120S
                                    instr., Form 120/PTE-W instr., Pub 713
                                    narrative
    2. "*Arizona* taxable income" — Form 220/PTE instr. ×2, Form 120/PTE-W
                                    instr., Pub 713 FAQ
    3. "*PTE* income"             — Form 165 instr. AND Form 120S instr.
    4. "*total* taxable income"   — Booklet 120/165ES
Worked case: $1,000,000 of Arizona taxable income with 10% consenting ownership
= $100,000 of PTE income — **IN under base 2, OUT under base 3, from readings
printed in the same book.** It decides whether the Form 220/PTE underpayment
penalty applies.
**RULED: the statute's bare "taxable income"** — the only one of the four with
controlling authority behind it. ⚠ **Recorded as a RULING ON A CONTESTED
QUESTION, NOT a published AZDOR position**; `[UNVERIFIED]` **U19 stays OPEN as a
matter of fact.** **The basis is a SINGLE NAMED CONSTANT**
(`AZ_EST_MEASUREMENT_BASIS`) so a DOR answer changes one thing.

**⚠⚠ A1 REFINED, SAME SESSION — THE RULING NAMED A SOURCE; IT NOW ALSO NAMES A
NUMBER. RULED: COMPUTE ARIZONA TAXABLE INCOME (A.R.S. § 43-1401(2)).**
*Why the refinement happened, so a later reader sees reasoning rather than an
unexplained change:* **A1 as first ruled settled WHICH SOURCE GOVERNS but not
WHICH FIGURE TO COMPUTE** — and estimated-payment and Form 220/PTE penalty logic
need a figure, not a citation. Title 43 chapter 14 **defines the statute's very
term** at § 43-1401(2) as *"Arizona taxable income"* — i.e. AZDOR's **base 2** —
so on its most natural reading the ruled source **RESOLVES INTO base 2** rather
than standing apart from all four, and base 2 vs base 3 was the whole reason A1
was blocking. The refinement follows the statutory definition where it leads,
which is the same reasoning that produced A1 in the first place. The authoring
pass encoded A1 **as ruled**, refused to resolve the gap on its own authority,
and escalated it rather than discovering it at build time.

**⚠ THE REFINEMENT NARROWS WHAT WE COMPUTE; IT DOES NOT CLOSE THE QUESTION.**
All four candidate bases stay on the record, the three losers stay explicitly
**not refuted**, the ruling still disclaims itself as **not a published AZDOR
position**, `[UNVERIFIED]` **U19 stays OPEN as a matter of fact**, and
`D_AZ_U19_150K_BASIS` still tells the preparer the threshold determination is
**PROVISIONAL**. Second leg encoded as `AZ_EST_MEASUREMENT_BASIS_RESOLVES_TO`
plus `az_est_measurement_figure()` / `az_estimated_payments_required_for()`.

**⚠⚠ WHERE THE FIGURE LANDS — AND THE SECOND-ORDER GAP THE REFINEMENT CREATES.**
For a **partnership** it is exact and sourced: § 43-1401(2) is *"Arizona gross
income adjusted by the modifications specified in sections 43-1021 and 43-1022
and section 43-1414, subsection A"*, which is precisely **Form 165 line 5** —
**NOT line 10**, because line 8 (= line 5) PLUS line 9 reconstructs
§ 43-1014(B)(1)(a)(ii); line 10 is the larger PTE BASE and using it would be a
FIFTH reading no AZDOR document prints. For an **S corporation**, ⚠ **§ 43-1401
is a chapter-14 PARTNERSHIP definitions section with NO S-corp analogue**, while
§ 43-581(C) reaches both entity types. Because Form 120S carries **no Arizona
modification apparatus at all**, applying the § 43-1401(2) *shape* to it changes
nothing and the figure is **line 1 = line 37** — build-to-the-form, not a
synthesised corporate definition, but **an ENGINEERING INFERENCE and labelled
one** (`AZ_EST_MEASUREMENT_SCORP_GAP`, diagnostic
`D_AZ120S_EST_BASIS_NO_ANALOGUE`). **Flagged for Ken, not resolved on this
file's authority.**

**⚠ THE SEPARATE BOUNDARY QUESTION IS SETTLED AND NEEDED NO RULING: "EXCEEDS",
so an entity at EXACTLY $150,000 is OUT.** Seven sources say so, including the
statute and all six instruction sets. A single Pub 713 FAQ answer says "or more"
and Pub 713's own FAQ lead-in offers a THIRD phrasing ("meets or exceeds") —
**Pub 713 is internally inconsistent three ways and cannot displace the statute.**
⚠⚠ **AN EARLIER VERIFICATION PASS "CORRECTED" THIS THE WRONG WAY** (flipping
`exceeds` → `or more` in `conformity/az_conformity.md` §4 and §12-H) **and a
later pass caught it.** `az_estimated_payments_required()` is STRICTLY GREATER
THAN and `validate_az.py` pins the exact-$150,000 boundary in BOTH directions so
it cannot drift back. Vintage-clean: `43-581` appears ZERO times in the Ch. 140
chaptered PDF and Ch. 182 does not touch it either.

**A2 · FORM 165PA IS RED-DEFERRED — DO NOT PICK A RATE.** Face line 13 and the
165PA instructions BOTH print **4.5%**; A.R.S. § 43-1414(B)(1)(b) imposes the tax
"at the highest tax rate imposed on individuals under section 43-1011" = **2.5%**
for TY2025. Both negatives verified: S.B. 1274 (Laws 2025 Ch. 182) **Sec. 7**
amended only subsection **(A)** (the capitalised new text appears ONLY there;
subsection (B) is entirely lowercase ⇒ unamended), and H.B. 4168 (Laws 2026
Ch. 140) does not touch § 43-1414 at all (`43-1414` = ZERO occurrences).
Building to the face knowingly **over-taxes by 80%**; building to the statute
contradicts a printed FINAL form. **DEFER, with its own diagnostic — no silent
gap.** The whole 165PA family is RED-DEFERRED: 165PA + 165PA Sch. K-1 + 165PA
Sch. K-1(NR) + 165PA-X. `az_165pa_rate()` RAISES.
⚠ **Do NOT conflate the two 4.5%s.** The 165PA *late-filing penalty* is also
4.5% and it is CORRECT. Only the line-13 TAX rate is stale.

**A3 · THE A.R.S. § 43-1021(15) ENTITY-LEVEL PTE ADD-BACK IS BUILT TO THE FORM —
OWNER LEVEL ONLY.** The statute's final sentence is explicit that the add-back
"shall be reflected in the partner's or shareholder's Arizona gross income **and
the partnership's or S corporation's Arizona taxable income**" — but **it has no
line on either form**: Form 165's page-6 A4 worksheet is a CLOSED list of three
items with no free-text "other" row anywhere on page 6, and Form 120S has no
additions schedule at all. Pub 713 answers a practitioner question asking exactly
this and says "owner level only" (while not addressing the entity clause, and
while closing with the confused words "reports this amount on his/her individual
**federal** income tax return"). **There is a REAL CASH-BASIS CIRCULARITY and it
is recorded**: the PTE tax is deductible federally in the year PAID, so line 1 /
line 37 is already net of it and the PTE base is understated by the PTE tax
itself. Same reasoning as D-10 ruling 2 (Missouri) and D-11 A1 (Colorado
§ 174A): **where the form cannot express a position, the form governs.**

**A4 · A CORPORATE PARTNER RECEIVING AN INDIVIDUAL-BASIS ARIZONA ADJUSTMENT —
PASS THE FIGURE THROUGH AS THE K-1 PRINTS IT, AND RAISE A REVIEW DIAGNOSTIC.**
Arizona's split (individuals conform to § 168(k); corporations decouple) runs
straight through a partnership K-1: Form 165 computes line B1 on the INDIVIDUAL
full-§168(k) rule, and Form 165 Schedule K-1(NR) line 15 routes that number to a
C-corp partner's **Form 120/120A Schedule A line A8 / Schedule B line B10** with
no re-computation instruction — while § 43-1122(20) requires that corporation to
compute Arizona depreciation as if bonus had been ELECTED OUT.
**RULED: COMPUTE NO CORPORATE-BASIS RECOMPUTATION.** Arizona publishes none and
no form line carries one; building it would invent a position the state has never
stated. `AZ_CORPORATE_BASIS_RECOMPUTATION is None` and
`az_corporate_partner_adjustment()` passes the printed figure through and returns
the review diagnostic id. Ruled separately, same session, after the gap was
surfaced rather than papered over. The gap stays **open as a matter of fact**
(U2 / W9); the Form 120 / 120A instructions were never pulled and are C-corp-wave
scope.

**D-10 · § 179 = $2,500,000 / $4,000,000 for TY2025 BY RULING, NOT BY
PUBLICATION.** AZDOR has never published its provision-by-provision OBBBA
retroactivity mapping and that `[UNVERIFIED]` (U3) stays **OPEN AS A FACT**.
**Carry the ruling AND the gap.** Neither Arizona PTE form states a § 179 figure,
so the ruling is invisible on the entity returns.
⚠ **New wrinkle the ruling did not reach:** for a PARTNERSHIP, § 179 is a
**separately-stated item under A.R.S. § 43-1412(5)**, so it enters the PTE base
through **Form 165 line 9** — a SINGLE UNDIFFERENTIATED BOX covering **SIXTEEN
statutory categories**. The dollar limit and the routing are two different
questions and only the limit was ruled on. For an S CORPORATION there is no
routing question at all (line 37 = line 1 = federal Schedule K, already net of
federal § 179 at whatever federal limit applied).

**D-12 · DEPRECIATION SHADOW BOOK: FORM 165 ONLY.** `AZ_120S` gets none.

═══════════════════════════════════════════════════════════════════════════
⚠ ARIZONA'S TY2025 CONFORMITY DATE IS A **COMPOUND** DATE — NEITHER 1/1/2025
  NOR 1/1/2026. GETTING THIS WRONG SILENTLY POISONS EVERY DEPRECIATION FIGURE.
═══════════════════════════════════════════════════════════════════════════
A.R.S. § 43-105(**B**) as amended by H.B. 4168 (Laws 2026 Ch. 140 **Sec. 12**),
read from the CHAPTERED act — old subsection (A) became (B):

  TY2025 (taxable years beginning after 12/31/2024 THROUGH 12/31/2025) =
      the IRC in effect **January 1, 2025**,
      including provisions that became effective during 2024 with specific
      adoption of all retroactive effective dates,
      **but EXCLUDING any changes to the code enacted after January 1, 2025**,
      **AND INCLUDING those provisions of P.L. 119-21 (OBBBA) that are
      RETROACTIVELY EFFECTIVE during taxable years beginning from and after
      December 31, 2024 through December 31, 2025.**

  TY2026+ = § 43-105(**A**): the IRC in effect **January 1, 2026**, excluding
      changes enacted after that date. **A DIFFERENT SUBSECTION.**

⚠ **"Arizona updated conformity to January 1, 2026" is the practitioner headline
and it describes TY2026.** Porting it into a TY2025 spec is the single most
likely way to get Arizona wrong. `az_conformity(2025)` returns the compound
structure; `_yk()` REFUSES an unkeyed year.

⚠ **Ch. 140 Sec. 35 splits the retroactivity and the split matters:**
  Sec. 35(A) → §§ 42-1001, **43-105**, 43-1022, 43-1041, 43-1121, 43-1122 reach
              back to taxable years beginning after **12/31/2024** (⇒ TY2025).
  Sec. 35(B) → §§ **43-1021**, 43-1042, 43-1073.01, 43-1074.01, 43-1168 reach
              back only to after **12/31/2025** (⇒ TY2026).
So § 168(n) qualified production property (new § 43-1021(17) / § 43-1121(25)) is
**TY2026-ONLY** — **no Arizona add-back for TY2025, on either form.** Do not code
one § 168(n) rule across both years.

⚠ **azleg SERVES PRE-Ch.140 TEXT FOR § 43-1021** (it still ends at paragraph 16).
Harmless for TY2025; a TY2026 pass must NOT rely on it.

⚠ **THE OBBBA GRAFT CLAUSE IS A CATEGORY, NOT A LIST.** Which P.L. 119-21
provisions AZDOR treats as "retroactively effective" is unmapped (U3). D-10
governs meanwhile.

═══════════════════════════════════════════════════════════════════════════
⚠ FACE-VS-INSTRUCTION VINTAGE SKEW — IT IS LIVE, AND IT RESOLVES **TO THE FACE**
═══════════════════════════════════════════════════════════════════════════
Arizona's TY2025 PTE package is a **November-2025 form face wearing an
August-2026 instruction book**:

  Form 165  face          /ModDate 2025-11-13   (predates H.B. 4168 by 7 months)
  Form 165  instructions  /ModDate 2026-08-11   (POST-dates it by 2 months)
  Form 120S face          /ModDate 2025-11-12   (predates)
  Form 120S instructions  Creation = ModDate = 2026-08-12 — **REGENERATED**

**So AZDOR had the chance to change substance AFTER enactment and changed
NOTHING**: no § 168(n) line, no H.B. 4168 / OBBBA / conformity discussion, no
change to the Form 165 line B1 tiers, no change to the 2.5% rate, and — critically
— **no MCTCP subtractions added to Schedule B or the page-6 B5 worksheet**, even
though the Form 165 PTE base is defined **by open reference to § 43-1022 as a
whole**, which now contains new ¶¶ (31) tips, (32) overtime, (35) senior and
(36) vehicle-loan interest, all TY2025-effective (U18 / W23).
**The entity-level PTE package is CONFORMITY-NEUTRAL for TY2025. BUILD TO THE
FORM.** Divergences between face and instructions resolve **to the face** —
the face is what is e-filed. (Note this points the OPPOSITE way from Virginia's,
where re-stamped forms with no H.R.1 line made the ABSENCE the finding.)

═══════════════════════════════════════════════════════════════════════════
⚠ ARIZONA HAS ITS OWN **FORM 355** — A COLLISION WITH MASSACHUSETTS FORM 355
═══════════════════════════════════════════════════════════════════════════
Every `Form 355` reference in the Arizona material is **ARIZONA's** Form 355,
*Credit for Entity-Level Income Tax Paid on Your Behalf* — confirmed on the AZDOR
K-1 faces themselves ("Individuals, enter this amount on Form 355, Part 1,
line 1"). Massachusetts Form 355 is its C-corporation excise return and is a
different document entirely; MA left this wave for its own (D-12 Group B).
`AZ_FORM_355_COLLISION_NOTE` carries the warning so the next reader is not
trapped. ⚠ And the AZ Form 355 line DIFFERS by entity type: partnership K-1s →
**Part 1 line 1**; S-corp K-1s → **Part 1 line 2**.

═══════════════════════════════════════════════════════════════════════════
⚠ THE `A.R.S. § 43-1011(A)(9)` PINPOINT IS **UNSUPPORTED** — CITE WHAT EXISTS
═══════════════════════════════════════════════════════════════════════════
`azleg.gov/ars/43/01011.01.htm` returns a **404** (the ONLY 404 among the
fourteen A.R.S. pages cached for the brief) and `azleg.gov/ars/43/01011.htm`
serves a **superseded conditional version** stamped `(L21, Ch. 411, sec. 4)`
whose subsection A stops at paragraph 4 with a **4.50%** top bracket while its
own subsection E refers to paragraphs 6-9 that are absent from the served text.
**No flat 2.5% and no paragraph (9) can be read off either page.**

**THE 2.5% RATE ITSELF IS SAFE** — five printed AZDOR confirmations (Form 165
face lines 20 and 24; Form 120S face lines 47 and 51, each "the PTE tax rate,
2.5% (0.0250)"; Pub 713 "For taxable year 2025, the PTE tax rate is 2.5%").
**ONLY THE PROVENANCE CHANGED.** This file therefore cites the FORM FACES and
Pub 713 for the rate and creates **no AuthoritySource for § 43-1011** — U21 is
carried as a diagnostic instead. `AZ_PTE_RATE` is pinned to the FACE, not to a
statutory lookup: if Arizona's individual rate ever moves, the PTE rate follows
in statute but the FORM will be reprinted, and the form is what is e-filed.
⚠ The consequence for § 43-1414(B)(1)(b) is that U14's 4.5%-vs-2.5% conflict is
established by SYLLOGISM (§ 43-1014(A) sets the PTE rate by reference to the
highest § 43-1011 rate; AZDOR prints that rate as 2.5%; ∴ the highest § 43-1011
rate is 2.5%; ∴ § 43-1414(B)(1)(b) = 2.5%), not by reading § 43-1011.

═══════════════════════════════════════════════════════════════════════════
THE EIGHT THINGS MOST LIKELY TO BE BUILT WRONG (all encoded as real branches)
═══════════════════════════════════════════════════════════════════════════
1. ⚠ **PORTING THE FORM 165 MODIFICATION STACK ONTO FORM 120S.** It would compute
   lines that DO NOT EXIST. The guards raise. §16.3.
2. ⚠ **FORM 165 LINE 5 vs LINE 6 — two different outputs of the same block going
   to two different places.** Line **5** feeds the PTE base (line 8) and
   Schedule D column (h). Line **6** — the NET ADJUSTMENT — feeds 165 Sch. K-1
   line 1 and 165 Sch. K-1(NR) line 15. **Crossing these is the most likely
   single transcription error on this form.**
3. ⚠ **PART 2 IS NOT GATED ON QUESTION A ALONE.** Both Part 2 headers read
   "...or estimated payments were made and the partnership is not claiming the
   PTE election." The gate is `Q.A == Yes OR pte_estimates_paid > 0`. A loader
   branching on Q.A alone suppresses Part 2 for exactly the population that most
   needs it — and TY2025 is THE year for it, because the federal SALT cap moved
   from $10,000 to $40,000 and Pub 713 scripts the "$0 return" refund path.
4. ⚠ **FORM 165 QUESTION D AND FORM 120S QUESTION B ARE INVERTED BOOLEANS.**
   165 line D "Is this partnership an Arizona-only partnership?" — **Yes = NOT
   multistate**. 120S line B "Does the S corporation conduct business within and
   without Arizona?" — **Yes = IS multistate**. A shared boolean is wrong for one
   of them. `az_is_multistate()` takes the form code and refuses to guess.
5. ⚠ **THE APPORTIONMENT DIVISOR IS DYNAMIC: 4, 3, 2, OR NONE.** Exclude a factor
   only when BOTH its numerator and denominator are zero (A.A.C. R15-2D-901(B)).
   Property or payroll excluded ⇒ divide by **three**; **sales excluded ⇒ divide
   by TWO** even though sales is double-weighted — the weighting and the divisor
   are NOT tied together; two factors excluded ⇒ the remaining factor IS the
   ratio, unweighted.
6. ⚠ **`0.000000` AND BLANK MEAN OPPOSITE THINGS.** "If line C5 is '0.000000',
   the partnership is considered to have no Arizona nexus. If line C5 is **blank
   or '1.000000'**, the income is sourced entirely within Arizona." A null-vs-zero
   bug here silently zeroes every nonresident's Arizona income.
7. ⚠ **THE FOURTH PTE ESTIMATED INSTALLMENT IS THE 15TH DAY OF THE **1ST** MONTH
   AFTER YEAR END, NOT THE 12TH MONTH.** Form 220/PTE line 7 prints the CORPORATE
   pattern (4th/6th/9th/12th) on the face and appends "PTE's see instructions",
   where the 1st-month rule lives. A loader reading the face alone puts the
   fourth installment **three months early**.
8. ⚠ **FORM 120S LINE 12'S $50 MINIMUM IS CONDITIONAL.** "The S Corporation is
   subject to the tax computed on line 12 **only if it has income subject to tax
   at the corporate level reported on federal Form 1120S**, even if line 11 is
   zero or a negative amount." Do not port an unconditional state minimum tax.

═══════════════════════════════════════════════════════════════════════════
WHY `READY_TO_SEED` IS FALSE
═══════════════════════════════════════════════════════════════════════════
D-12 approved the WAVE SHAPE and four blocking rulings; it did **not** approve
seeding. **21 `[UNVERIFIED]` items are open** and NONE was closed outright by the
verification pass (three were ADDED). Three of them are 🔴:
  **U19** — which taxable income measures the $150,000 threshold. RULED by D-12
           A1 so authoring may proceed, but the fact stays open.
  **U14** — Form 165PA's 4.5% vs the statute's 2.5%. RED-DEFERRED by D-12 A2.
  **U3**  — AZDOR's OBBBA retroactivity mapping. D-10 governs meanwhile.
Highest-value remaining pulls, in order: an AZDOR ruling on the § 43-581(C)
measurement base (U19); **ITP 16-2** (U1 — the ONLY unpulled document gating a
mainstream line, Form 165 line B1's TY2013 tier); Form 120 / 120A instructions
(U2, closes A4's factual gap); TY2025 Form 140-SBI / 140PY-SBI instructions (U6);
§ 43-1011 from a source serving the operative version (U21); AZDOR's OBBBA
mapping (U3, may not exist).

⚠ **STANDING STALENESS RULE.** Every figure here is TY2025-keyed. AZDOR reissued
essentially the whole corporate/partnership instruction set between 2026-08-06
and 2026-08-12 and may do so again. **A new tax year staleness-invalidates this
spec in full.** `_yk()` raises rather than defaulting.

⚠ **PROCESS NOTE CARRIED FORWARD (D-12).** A checking pass is not
self-validating: the AZ `$150,000` boundary was "corrected" the WRONG way by one
verification pass and caught by a later one. Corrections in this file carry their
evidence inline so a later pass can re-adjudicate rather than inherit.
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
# It is False because Gate 1 has NOT been taken for the Arizona specs. D-12
# approved the wave SHAPE and four rulings, not the seed. 21 [UNVERIFIED] items
# are open, ITP 16-2 (U1) still gates Form 165 line B1's TY2013 tier, and the
# whole Form 165PA family is RED-DEFERRED on an un-adjudicated rate conflict.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = False


FORM_JURISDICTION = "AZ"
FORM_TAX_YEAR = 2025
FORM_VERSION = 1
FORM_STATUS = "draft"

FORM_CODE_165 = "AZ_165"
FORM_CODE_120S = "AZ_120S"
FORM_CODES = (FORM_CODE_165, FORM_CODE_120S)

# Module tokens, derived from the ATTACHED FEDERAL RETURN. Arizona keeps them
# strictly separate: Form 165 serves 1065 only, Form 120S serves 1120S only.
# Neither form serves both, and there is no third form serving both (contrast
# Oregon's OR-21).
M_1065 = "1065"
M_1120S = "1120S"
MODULES = (M_1065, M_1120S)


def _yk(d: dict, year: int):
    """Tax-year-keyed lookup. RAISES rather than silently defaulting.

    Every figure in this spec is TY2025-keyed. Arizona's conformity moves to a
    DIFFERENT SUBSECTION for TY2026 (§ 43-105(A), Jan 1 2026) and § 168(n)
    add-backs switch on for TY2026 under Ch. 140 Sec. 35(B). A silent fallback
    would let a TY2026 engagement inherit TY2025 law, which is exactly the
    failure the campaign's staleness rule exists to prevent.
    """
    if year not in d:
        raise KeyError(
            f"No TY{year} value seeded. Arizona figures are tax-year-keyed and a new tax "
            f"year staleness-invalidates them: § 43-105 switches from subsection (B) "
            f"(TY2025: 1/1/2025 + retroactively-effective OBBBA) to subsection (A) "
            f"(TY2026+: 1/1/2026), and the § 168(n) add-backs at § 43-1021(17) / "
            f"§ 43-1121(25) begin in TY2026. Seeded years: {sorted(d)}"
        )
    return d[year]


class ArizonaFormGovernsError(ValueError):
    """Raised when code asks Arizona for a computation NO ARIZONA FORM CARRIES.

    Every raise site is a place where a campaign ruling said `build to the form`
    and the form is silent. Raising is the point: the alternative is inventing a
    position Arizona has never stated.
    """


class ArizonaDeferredFormError(ValueError):
    """Raised for a RED-DEFERRED Arizona form (the Form 165PA family)."""


# ═══════════════════════════════════════════════════════════════════════════
# CONFORMITY — THE COMPOUND TY2025 DATE
#
# ⚠ DO NOT FLATTEN AND DO NOT PORT THE HEADLINE. Arizona TY2025 is NOT
# "1/1/2025" and NOT "1/1/2026". It is 1/1/2025 PLUS a statutory graft of
# retroactively-effective OBBBA provisions, in a subsection (B) that only exists
# because H.B. 4168 renumbered the old (A). TY2026 is a different subsection.
#
# The JurisdictionConformitySource row is ALREADY SEEDED with
# conformity_type = 'static' (campaign D-10) — that value is the row's, and this
# constant mirrors it rather than re-deciding it.
# ═══════════════════════════════════════════════════════════════════════════
AZ_CONFORMITY_TYPE = "static"          # matches the seeded row (D-10)

AZ_CONFORMITY_BASE_DATE: dict[int, str] = {2025: "2025-01-01", 2026: "2026-01-01"}
AZ_CONFORMITY_SUBSECTION: dict[int, str] = {2025: "A.R.S. § 43-105(B)", 2026: "A.R.S. § 43-105(A)"}
AZ_CONFORMITY_OBBBA_GRAFT: dict[int, bool] = {2025: True, 2026: False}

AZ_CONFORMITY_TY2025_VERBATIM = (
    "For the purposes of computing income tax pursuant to this title, for taxable years beginning "
    "from and after December 31, 2024 THROUGH DECEMBER 31, 2025, 'internal revenue code' means the "
    "United States internal revenue code of 1986, as amended, in effect on January 1, 2025, "
    "including those provisions that became effective during 2024 with the specific adoption of all "
    "retroactive effective dates, but excluding any changes to the code enacted after January 1, "
    "2025 AND INCLUDING THOSE PROVISIONS OF PUBLIC LAW 119-21 THAT ARE RETROACTIVELY EFFECTIVE "
    "DURING TAXABLE YEARS BEGINNING FROM AND AFTER DECEMBER 31, 2024 THROUGH DECEMBER 31, 2025."
)

# Ch. 140 Sec. 35 retroactivity split, verbatim in substance. The SPLIT is what
# makes § 168(n) a TY2026 item while the conformity date itself reaches TY2025.
AZ_CH140_RETRO_TY2025_SECTIONS = ("42-1001", "43-105", "43-1022", "43-1041", "43-1121", "43-1122")
AZ_CH140_RETRO_TY2026_SECTIONS = ("43-1021", "43-1042", "43-1073.01", "43-1074.01", "43-1168")


def az_conformity(year: int = FORM_TAX_YEAR) -> dict:
    """The COMPOUND Arizona conformity statement for a tax year.

    ⚠ Returns a structure, never a bare date string, precisely because a bare
    date is what gets Arizona wrong.
    """
    return {
        "conformity_type": AZ_CONFORMITY_TYPE,
        "base_irc_date": _yk(AZ_CONFORMITY_BASE_DATE, year),
        "subsection": _yk(AZ_CONFORMITY_SUBSECTION, year),
        "excludes_changes_enacted_after_base_date": True,
        "includes_retroactively_effective_obbba": _yk(AZ_CONFORMITY_OBBBA_GRAFT, year),
        "obbba_provision_map_published_by_azdor": False,   # U3 — OPEN AS A FACT
        "authority": "H.B. 4168 (Laws 2026 Ch. 140) Sec. 12, amending A.R.S. § 43-105",
        "retroactivity": ("Ch. 140 Sec. 35(A) reaches taxable years beginning after 12/31/2024 for "
                          "§ 43-105; Sec. 35(B) reaches only after 12/31/2025 for § 43-1021"),
    }


def az_conformity_is_compound(year: int = FORM_TAX_YEAR) -> bool:
    """TY2025 is 1/1/2025 PLUS an OBBBA graft. TY2026 is a clean 1/1/2026."""
    return bool(_yk(AZ_CONFORMITY_OBBBA_GRAFT, year))


# ⚠ § 168(n) qualified production property: NO Arizona add-back for TY2025, on
# EITHER form, for EITHER owner class. New § 43-1021(17) (individuals, Ch. 140
# Sec. 14) and § 43-1121(25) (corporations, Sec. 22) are BOTH expressly limited
# to "TAXABLE YEARS BEGINNING FROM AND AFTER DECEMBER 31, 2025", reinforced by
# Sec. 35(B). Neither PTE form has a § 168(n) line and neither instruction book
# mentions it — CORRECT for TY2025. A TY2026 pass MUST re-read the page-6 A4
# worksheet: if AZDOR adds a QPP row it lands there, and if it does not, § 168(n)
# inherits the "no line exists" problem.
AZ_168N_ADDBACK_FIRST_TAX_YEAR = 2026


def az_168n_addback_applies(year: int) -> bool:
    return year >= AZ_168N_ADDBACK_FIRST_TAX_YEAR


# ═══════════════════════════════════════════════════════════════════════════
# THE PTE TAX RATE — PINNED TO THE FORM FACE, NOT TO A STATUTORY LOOKUP
# ═══════════════════════════════════════════════════════════════════════════
# A.R.S. § 43-1014(A) sets it BY REFERENCE: "at a tax rate that is the same as
# the highest tax rate prescribed by section 43-1011". But § 43-1011 CANNOT BE
# READ off azleg (U21, see the banner), and the face is what is e-filed. Pinning
# to the face keeps statute and form from drifting silently.
AZ_PTE_RATE: dict[int, str] = {2025: "0.0250"}
AZ_PTE_RATE_SOURCE = (
    "PRE-PRINTED ON BOTH FORM FACES: Form 165 lines 20 and 24, Form 120S lines 47 and 51, each "
    "reading 'the PTE tax rate, 2.5% (0.0250)'. Confirmed by Pub 713 (rev. Nov 2025): 'For taxable "
    "year 2025, the PTE tax rate is 2.5%.' FIVE printed AZDOR confirmations."
)
AZ_PTE_RATE_STATUTORY_BASIS = (
    "A.R.S. § 43-1014(A): 'at a tax rate that is the same as the highest tax rate prescribed by "
    "section 43-1011'. ⚠ THE § 43-1011 PINPOINT IS UNVERIFIABLE (U21): "
    "azleg.gov/ars/43/01011.01.htm 404s and 01011.htm serves a superseded version topping at "
    "4.50%. THE RATE IS SAFE; ONLY THE PROVENANCE CHANGED."
)


def az_pte_rate(year: int = FORM_TAX_YEAR) -> str:
    return _yk(AZ_PTE_RATE, year)


# Corporate-level tax on Form 120S ONLY (Form 165 has no such line).
AZ_120S_CORP_RATE: dict[int, str] = {2025: "0.049"}
AZ_120S_CORP_MINIMUM: dict[int, int] = {2025: 50}


def az_120s_line12_tax(line11_net_income: float, has_federal_level_taxable_income: bool,
                       year: int = FORM_TAX_YEAR) -> float | None:
    """Form 120S line 12 — 'the greater of $50 or 4.9% of line 11'.

    ⚠ THE MINIMUM IS CONDITIONAL, NOT UNCONDITIONAL. Verbatim: 'The S Corporation
    is subject to the tax computed on line 12 ONLY IF it has income subject to
    tax at the corporate level reported on federal Form 1120S, even if line 11 is
    zero or a negative amount.' Returns None (line left blank) when there is no
    federal-level taxable income. Do NOT port an unconditional state minimum tax
    from another jurisdiction.
    """
    if not has_federal_level_taxable_income:
        return None
    return max(float(_yk(AZ_120S_CORP_MINIMUM, year)),
               round(float(line11_net_income) * float(_yk(AZ_120S_CORP_RATE, year)), 2))


# ═══════════════════════════════════════════════════════════════════════════
# § 179 — CARRIED AS A RULING, WITH ITS GAP OPEN (campaign D-10)
# ═══════════════════════════════════════════════════════════════════════════
# ⚠ Arizona has NO § 179 modification. Searched §§ 43-1021 / 43-1022 / 43-1121 /
# 43-1122 — Arizona enumerates its modifications EXHAUSTIVELY in those four
# sections and § 179 is ABSENT. That is "the rule says no", and it is the
# VERIFIED half. The resulting NUMBER is the inferred half, because it routes
# through § 43-105(B)'s OBBBA graft clause and AZDOR has published no
# provision-by-provision mapping.
AZ_179_LIMIT: dict[int, int] = {2025: 2_500_000}
AZ_179_PHASEOUT: dict[int, int] = {2025: 4_000_000}
AZ_179_IS_RULING_NOT_PUBLICATION = True
AZ_179_PROVENANCE = (
    "CAMPAIGN RULING D-10 (2026-08-16), NOT A PUBLISHED ARIZONA FIGURE. Ken ruled the BROAD "
    "reading of A.R.S. § 43-105(B)'s OBBBA graft clause. The MECHANISM is verified (Arizona has no "
    "§ 179 modification in any of §§ 43-1021 / 43-1022 / 43-1121 / 43-1122, which enumerate "
    "exhaustively); the NUMBER is an inference. AZDOR has never published its "
    "provision-by-provision OBBBA retroactivity mapping and [UNVERIFIED] U3 STAYS OPEN AS A MATTER "
    "OF FACT. Re-verify if AZDOR ever publishes it. ⚠ NEITHER PTE FORM STATES A § 179 FIGURE, so "
    "the ruling is invisible on the entity returns."
)
AZ_179_FORM_LINE_EXISTS = False   # verified by reading both faces and both books end to end


def az_179_limits(year: int = FORM_TAX_YEAR) -> dict:
    return {"limit": _yk(AZ_179_LIMIT, year), "phaseout": _yk(AZ_179_PHASEOUT, year),
            "basis": "ruling", "provenance": AZ_179_PROVENANCE, "unverified_item": "U3"}


# ⚠ THE ROUTING QUESTION D-10 DID NOT REACH. For a PARTNERSHIP, § 179 is a
# SEPARATELY-STATED ITEM under A.R.S. § 43-1412(5) ("Additional first year
# depreciation computed pursuant to section 179 of the internal revenue code"),
# and § 43-1401(1) EXCLUDES the § 43-1412 ¶1-16 items from a partnership's
# "Arizona gross income" in the first place. So § 179 enters the Arizona PTE base
# through **Form 165 LINE 9**, not through line 1 and not through Schedule A/B.
# For an S CORPORATION there is no routing question: line 37 = line 1 = federal
# Schedule K total distributive income, already net of federal § 179.
AZ_179_PARTNERSHIP_ROUTE = "Form 165 line 9 (A.R.S. § 43-1412(5), a separately-stated item)"
AZ_179_SCORP_ROUTE = "none — Form 120S line 37 = line 1 = federal Schedule K, already net of § 179"

# A.R.S. § 43-1412 ¶1-16 — SIXTEEN statutory categories collapsing into ONE
# undifferentiated box on the Form 165 face ("Enter the total of all items
# requiring separate computation"), with NO supporting schedule and NO
# itemisation. ⚠ THE LARGEST DIRECT-ENTRY SURFACE ON FORM 165 AND THE PLACE A
# § 179 ERROR WILL HIDE (W10).
AZ_43_1412_CATEGORIES: tuple[str, ...] = (
    "gains and losses from sales or exchanges of capital assets",
    "gains and losses from sales or exchanges of property described in IRC § 1231",
    "charitable contributions",
    "dividends entitled to the exclusions of IRC § 116 / § 243",
    "additional first year depreciation computed pursuant to IRC § 179",
    "taxes described in IRC § 901 paid or accrued to foreign countries or U.S. possessions",
    "partially tax-exempt interest on U.S. obligations",
    "income taxes paid to another state or country",
    "recoveries of bad debts, prior taxes and delinquency amounts under IRC § 111",
    "gains and losses from wagering transactions under IRC § 165(d)",
    "soil and water conservation expenditures under IRC § 175",
    "nonbusiness expenses under IRC § 212",
    "expenses for care of certain dependents under IRC § 214",
    "certain payments under IRC § 215",
    "amounts representing taxes and interest paid to a cooperative housing corporation under IRC § 216",
    "intangible drilling and development costs under IRC § 263(c), mining exploration expenditures "
    "under IRC § 617, items subject to IRC § 751(b), and any specially-allocated items",
)
AZ_43_1412_CATEGORY_COUNT = 16


# ═══════════════════════════════════════════════════════════════════════════
# THE DEPRECIATION SHADOW BOOK — **FORM 165 ONLY** (campaign D-12)
#
# Form 165 line A1 adds back the ENTIRE federal § 167(a) allowance
# (A.R.S. § 43-1021(11)); line B1 subtracts a RECOMPUTED Arizona figure. The
# recomputation is keyed by PLACED-IN-SERVICE tax year across **FIVE** vintage
# tiers.
#
# ⚠ [CORRECTED — verification pass §16.4 C6: the brief's heading said "four
# tiers". The instruction and its table both carry FIVE placed-in-service
# windows. Substance unaffected; the count is now right.]
#
# ⚠ THE KEYING IS **PLACED IN SERVICE**, AND ARIZONA STATES IT FOUR TIMES IN FOUR
# SENTENCES. Campaign D-10 rulings 3 and 4 had to RULE placed-in-service vs
# acquired-date for Tennessee and Texas because those sources were SILENT.
# **Arizona is not silent — no ruling is needed here.** Ratification, not decision.
# ═══════════════════════════════════════════════════════════════════════════
AZ_165_B1_TIERS: tuple[dict, ...] = (
    {"tier": 1, "window": "taxable years beginning before December 31, 2012",
     "az_bonus_pct_of_federal_168k": "0.00", "method": "elect-out equivalent",
     "verbatim": ("For assets placed in service in taxable years beginning before December 31, 2012, "
                  "enter the total amount of depreciation allowable pursuant to IRC § 167(a) for the "
                  "taxable year calculated as if the taxpayer had elected not to claim bonus "
                  "depreciation for eligible properties for federal purposes.")},
    {"tier": 2, "window": "taxable years beginning after 12/31/2012 through 12/31/2013",
     "az_bonus_pct_of_federal_168k": None, "method": "ITP_16_2",
     "verbatim": ("For assets placed in service in taxable years beginning from and after December 31, "
                  "2012 through December 31, 2013, the amount of the subtraction for these assets "
                  "depends on the method used to compute the depreciation for assets. See the "
                  "department's procedure, ITP 16-2, Procedure for Individuals who Claim Federal "
                  "and/or Arizona Bonus Depreciation.")},
    {"tier": 3, "window": "taxable years beginning after 12/31/2013 through 12/31/2015",
     "az_bonus_pct_of_federal_168k": "0.10", "method": "10% of federal § 168(k)",
     "verbatim": ("...calculated as if the bonus depreciation is 10% of the amount of federal bonus "
                  "depreciation pursuant to IRC § 168(k). See the department's procedure, ITP 16-2 ...")},
    {"tier": 4, "window": "taxable years beginning after 12/31/2015 through 12/31/2016",
     "az_bonus_pct_of_federal_168k": "0.55", "method": "55% of federal § 168(k)",
     "verbatim": ("...calculated as if the bonus depreciation is 55% of the amount of federal bonus "
                  "depreciation pursuant to IRC § 168(k).")},
    {"tier": 5, "window": "taxable years beginning after 12/31/2016",
     "az_bonus_pct_of_federal_168k": "1.00", "method": "full § 168(k) — the INDIVIDUAL rule",
     "verbatim": ("For assets placed in service in taxable years beginning after December 31, 2016, "
                  "enter the total amount of depreciation allowable pursuant to IRC § 167(a) for the "
                  "taxable year calculated as if the bonus depreciation had been the full amount of "
                  "federal bonus depreciation pursuant to IRC § 168(k).")},
)
AZ_165_B1_TIER_COUNT = 5
AZ_165_B1_KEYED_ON = "placed_in_service"
AZ_165_B1_UNRESOLVED_TIER = 2           # U1 — ITP 16-2 not pulled
AZ_165_B1_AUTHORITY_PROCEDURE = "AZDOR procedure ITP 16-2"


def az_165_b1_tier(placed_in_service_tax_year_begin: int) -> dict:
    """Return the Form 165 line B1 vintage tier for a placed-in-service TY.

    ⚠ Tier 2 (TY2013) returns method 'ITP_16_2' with a NULL percentage. That is
    NOT a gap in this file — the AZDOR instruction itself defers entirely
    ("depends on the method used to compute the depreciation for assets") and
    **ITP 16-2 has never been pulled** (U1). The tier is DIRECT-ENTRY with a
    diagnostic. Exposure is narrow but real: § 168(k) never applied to 27.5-year
    residential rental or 39-year nonresidential real property, so the live
    TY2025 exposure is 15-year qualified leasehold / retail improvement property
    from a TY2013 year, still depreciating.
    """
    y = int(placed_in_service_tax_year_begin)
    if y < 2012:
        return AZ_165_B1_TIERS[0]
    if y == 2012:
        # A taxable year BEGINNING before December 31, 2012 is tier 1; a taxable
        # year beginning from and after December 31, 2012 is tier 2. Calendar
        # 2012 years begin 1/1/2012, i.e. BEFORE 12/31/2012.
        return AZ_165_B1_TIERS[0]
    if y == 2013:
        return AZ_165_B1_TIERS[1]
    if y in (2014, 2015):
        return AZ_165_B1_TIERS[2]
    if y == 2016:
        return AZ_165_B1_TIERS[3]
    return AZ_165_B1_TIERS[4]


def az_165_b1_bonus_pct(placed_in_service_tax_year_begin: int) -> str | None:
    return az_165_b1_tier(placed_in_service_tax_year_begin)["az_bonus_pct_of_federal_168k"]


# ⚠ FORM 165 APPLIES THE **INDIVIDUAL** BONUS REGIME AT THE ENTITY LEVEL.
# Line B1's final tier is word-for-word A.R.S. § 43-1022(17)(e) ("as if the bonus
# depreciation had been THE FULL AMOUNT"), the instruction's own authority
# pointer is **ITP 16-2 — "Procedure for INDIVIDUALS who Claim Federal and/or
# Arizona Bonus Depreciation"** (cited three times on that one line), and the
# PTE-base note builds Arizona taxable income from "any Arizona additions found
# in A.R.S. § 43-1021 less any Arizona subtractions found in A.R.S. § 43-1022" —
# THE INDIVIDUAL SECTIONS. A.R.S. § 43-1401(2) says the same.
AZ_165_BONUS_REGIME = "individual"      # § 43-1021(11) add-back + § 43-1022(17)(e) subtraction
AZ_CORPORATE_BONUS_REGIME = "decoupled"  # § 43-1121(4) add-back + § 43-1122(20) elect-out
AZ_BONUS_SPLIT_NOTE = (
    "Arizona runs OPPOSITE bonus regimes for individuals and corporations IN THE SAME TAX YEAR. "
    "Individuals CONFORM (net zero: § 43-1021(11) backs out all federal § 167(a) depreciation, "
    "§ 43-1022(17)(e) subtracts it recomputed as if bonus had been the FULL § 168(k) amount). "
    "Corporations DECOUPLE (§ 43-1122(20) subtracts as if the § 168(k)(7) ELECTION OUT had been "
    "made, requiring a separate Arizona schedule and basis). Any engine carrying one rule across "
    "both modules is wrong for one of them. Both were re-verified UNCHANGED by H.B. 4168."
)


# ═══════════════════════════════════════════════════════════════════════════
# ⚠⚠ A4 — THE CORPORATE PARTNER RECEIVING AN INDIVIDUAL-BASIS ADJUSTMENT
#         RULED SEPARATELY, SAME D-12 SESSION
# ═══════════════════════════════════════════════════════════════════════════
# Form 165 Schedule K-1(NR) Part 2 line 15 instructions, verbatim:
#     "Corporate partners:
#      • If the amount on line 15 is positive, enter the amount from line 15,
#        column (a) on Schedule A, line A8 of Form(s) 120 or 120A.
#      • If the amount on line 15 is negative, enter the amount from line 15,
#        column (a) on Schedule B, line B10 of Form(s) 120 or 120A."
# NOTHING on Form 165, on the K-1(NR), or on the Form 120 A8/B10 lines instructs
# the corporate partner to re-compute on the corporate (elect-out) basis — while
# § 43-1122(20) says corporations must. Three readings were available and the
# brief deliberately chose none of them.
#
# **RULED: pass the figure through AS THE K-1 PRINTS IT and raise a review
# diagnostic. COMPUTE NO CORPORATE-BASIS RECOMPUTATION.** Arizona publishes none
# and no form line carries one. The gap stays OPEN as a matter of fact (U2 / W9);
# it is a C-CORP-WAVE concern and does NOT block this wave — Form 165's own
# computation is unambiguous.
# ═══════════════════════════════════════════════════════════════════════════
AZ_CORPORATE_BASIS_RECOMPUTATION = None          # ⚠ deliberately None. D-12 A4.
AZ_A4_DIAGNOSTIC_ID = "D_AZ165_A4_CORP_PARTNER_BASIS"


def az_corporate_partner_adjustment(k1nr_line15_column_a: float) -> dict:
    """D-12 A4. Pass the printed figure through; raise a review diagnostic.

    ⚠ Returns `recomputed` = None ALWAYS. Do not "fill it in later": Arizona has
    published no corporate-basis recomputation for a partnership-level adjustment
    and no form line carries one, so computing one would invent a state position.
    """
    amount = float(k1nr_line15_column_a)
    return {
        "pass_through_amount": amount,
        "column": "(a)",   # ⚠ corporations and partnerships use column (a); individuals and
                           #    estates/trusts use column (c). Four owner types, two columns.
        "destination": ("Form 120 or 120A Schedule A line A8 if positive; Schedule B line B10 if "
                        "negative"),
        "recomputed_on_corporate_basis": AZ_CORPORATE_BASIS_RECOMPUTATION,
        "review_diagnostic": AZ_A4_DIAGNOSTIC_ID,
        "ruling": "campaign D-12 A4 (2026-08-19)",
        "open_fact": ("OPEN AS A FACT — U2 / W9: the Form 120 / 120A instructions were never "
                      "pulled and are C-corp-wave scope"),
    }


# ═══════════════════════════════════════════════════════════════════════════
# ⚠⚠ THE VERIFIED NEGATIVE — FORM 120S HAS **NO** MODIFICATION APPARATUS
#     PINNED HERE AND PINNED AGAIN IN validate_az.py
# ═══════════════════════════════════════════════════════════════════════════
AZ_120S_HAS_MODIFICATION_APPARATUS = False
AZ_120S_HAS_DEPRECIATION_LOGIC = False
AZ_120S_LINE37_EQUALS_LINE1 = True

AZ_120S_NEGATIVE_PROOF: dict = {
    "claim": "Form 120S carries NO federal→Arizona modification apparatus of any kind.",
    "verdict": "CONFIRMED — the false-positive alarm was chased down and DISPROVEN (§16.3).",
    "modification_statute_citations_in_the_28_page_book": {
        "43-1021": 0, "43-1022": 0, "43-1121": 0, "43-1122": 0,
    },
    "title_43_sections_the_book_DOES_cite": (
        "43-1130.01", "43-1131", "43-1134", "43-1138", "43-1139(B)", "43-1140", "43-1142",
        "43-1143", "43-1144", "43-1145", "43-1147(E)(3)(a)", "43-1148", "43-1150",
    ),
    "and_every_one_of_them_is": "an apportionment (UDITPA) provision",
    "addition_subtraction_hits_read_in_context": 70,
    "buckets": {
        "the word 'additional'": 23,
        "the list lead-in 'In addition:'": 2,
        "pure line arithmetic ('Subtract line X from line Y')": 12,
        "'has no Arizona additions to, or subtractions from, federal taxable income' — ALL THREE "
        "inside the Rounding Dollar Amounts worked examples (Company A / W / Z), boilerplate lifted "
        "from the Form 120 C-corp book, each saying the company HAS NONE": 3,
        "the owner-level net long-term capital gain subtraction (§ 43-1022), ALL of them in the "
        "Schedule K-1 / K-1(NR) instruction section at the BACK of the book": 18,
    },
    "arizona_basis_string_occurrences": 0,
    "face_comparison": ("Form 165 prints SCHEDULE A: Additions (A1-A4) and SCHEDULE B: Subtractions "
                        "(B1-B5) ON THE FACE plus lines 5 and 6. Form 120S has no counterpart to any "
                        "of it — its Schedule A is the APPORTIONMENT FORMULA."),
    "corporate_level_base_also_unadjusted": ("line 4 = 2 + 3 straight from federal; line 11 = line 4 "
                                             "or line 10; line 12 = greater of $50 or 4.9% of line 11"),
    "statute": ("A.R.S. § 43-1014(B)(1)(b): 'the total of all distributive income passed through to "
                "the shareholders under section 43-1126, subsection B' — and § 43-1126(B) is a "
                "REPORTING provision, not a modification provision"),
    "owner_side_corroboration": ("the 120S Schedule K-1 has NO income-adjustment part at all, where "
                                 "the 165 Schedule K-1 Part 1 lines 1-3 carry one"),
    "where_the_shareholder_adjustment_happens_instead": ("on the shareholder's OWN individual return "
                                                        "under §§ 43-1021(11) / 43-1022(17)(e), from "
                                                        "the shareholder's own records"),
    "why_it_survives_being_net_zero": ("internally consistent, because individuals FULLY conform — "
                                       "the entity and the individual reach the same number"),
}


def az_120s_modification(*_args, **_kwargs):
    """⚠ ALWAYS RAISES. Form 120S has no additions/subtractions schedule.

    This is a VERIFIED NEGATIVE, not an unimplemented feature. See
    AZ_120S_NEGATIVE_PROOF and source brief §16.3. Do not add a 120S modification
    field "for symmetry with AZ_165" or with another state — the Arizona
    asymmetry is real, statutory, and the harness pins it.
    """
    raise ArizonaFormGovernsError(
        "Arizona Form 120S has NO federal-to-Arizona modification apparatus. Line 37 = line 1, "
        "unadjusted (A.R.S. § 43-1014(B)(1)(b)). The four Arizona modification statutes "
        "(43-1021 / 43-1022 / 43-1121 / 43-1122) are cited ZERO times in the entire 28-page TY2025 "
        "Form 120S instruction book, the string 'Arizona basis' occurs ZERO times, and the "
        "corporate-level chain (lines 2-4, 11, 12) is unadjusted too. This is a VERIFIED NEGATIVE "
        "(source brief §16.3, campaign D-12 Group B: NO SHARED ARIZONA MODIFICATION ENGINE). "
        "Porting the Form 165 Schedule A/B stack onto Form 120S computes lines that do not exist."
    )


def az_120s_depreciation_adjustment(*_args, **_kwargs):
    """⚠ ALWAYS RAISES. AZ_120S gets NO depreciation logic (campaign D-12)."""
    raise ArizonaFormGovernsError(
        "Arizona Form 120S makes NO Arizona depreciation adjustment at the entity level. The "
        "depreciation shadow book is FORM 165 ONLY (campaign D-12). An S-corp shareholder's Arizona "
        "depreciation adjustment happens on the SHAREHOLDER'S OWN individual return under "
        "§§ 43-1021(11) / 43-1022(17)(e). See AZ_120S_NEGATIVE_PROOF."
    )


# ═══════════════════════════════════════════════════════════════════════════
# ⚠⚠ A3 — THE § 43-1021(15) ENTITY-LEVEL PTE ADD-BACK THAT HAS NO LINE
#         BUILT TO THE FORM: **OWNER LEVEL ONLY** (campaign D-12 A3)
# ═══════════════════════════════════════════════════════════════════════════
AZ_1021_15_ENTITY_ADDBACK_BUILT = False        # ⚠ deliberately False. D-12 A3.
AZ_1021_15_OWNER_ADDBACK_BUILT = True          # fully implemented on all four K-1s
AZ_1021_15_VERBATIM = (
    "15. For taxable years beginning from and after December 31, 2021, the amount deducted by the "
    "partnership or S corporation pursuant to the internal revenue code for the amount paid to this "
    "state under section 43-1014 and for taxes that the department determines are substantially "
    "similar to the tax imposed under section 43-1014. This amount shall be reflected in the "
    "partner's or shareholder's Arizona gross income and the partnership's or S corporation's "
    "Arizona taxable income."
)
AZ_1021_15_CIRCULARITY = (
    "⚠ REAL, AND RECORDED RATHER THAN FIXED. The PTE tax is deductible FEDERALLY in the year PAID, "
    "and electing entities are almost universally cash-basis. So the federal ordinary income at "
    "Form 165 line 1 / Form 120S line 1 is ALREADY NET of the Arizona PTE tax the entity paid "
    "during the year, and without an entity-level add-back the PTE base is UNDERSTATED BY THE PTE "
    "TAX ITSELF. That circularity is exactly what the statute's second sentence exists to close, "
    "and the forms do not close it."
)
AZ_1021_15_NO_LINE_PROOF = (
    "Form 165 Schedule A has FOUR rows (A1-A4); the page-6 A4 worksheet is a CLOSED ENUMERATION of "
    "three items (Positive Partnership Income Adjustment, Federal Depreciation of Child Care "
    "Facilities, Expenditures for the ADA) and THERE IS NO FREE-TEXT 'OTHER' ROW ANYWHERE ON PAGE "
    "6. The Form 165 PTE base is line 5 + line 9, and line 9 is § 43-1412 ¶1-16, which contains no "
    "PTE-tax add-back. Form 120S has no additions schedule at all and line 37 = line 1."
)
AZ_1021_15_AZDOR_ANSWER = (
    "Pub 713, OTHER: practitioners asked this EXACT question ('we are unable to determine where the "
    "add back of the taxes paid on behalf of the partner/shareholder is listed'). AZDOR's published "
    "answer is OWNER LEVEL ONLY: 'The add back ... is passed through to that individual partner or "
    "shareholder.' ⚠ It does not address the statute's 'and the partnership's or S corporation's "
    "Arizona taxable income' clause at all, and its closing words ('reports this amount on his/her "
    "individual FEDERAL income tax return') are themselves confused — the add-back is an ARIZONA "
    "modification."
)


def az_entity_level_pte_addback(*_args, **_kwargs):
    """⚠ ALWAYS RAISES. D-12 A3: build to the form, owner level only."""
    raise ArizonaFormGovernsError(
        "A.R.S. § 43-1021(15) directs the entity-level PTE tax add-back into the entity's own "
        "Arizona taxable income, but NO LINE EXISTS on Form 165 or Form 120S to carry it. "
        "CAMPAIGN RULING D-12 A3: BUILD TO THE FORM — OWNER LEVEL ONLY. Same shape as D-10 ruling 2 "
        "(Missouri capital gain) and D-11 A1 (Colorado § 174A): where the form cannot express a "
        "position, the form governs. The cash-basis circularity is REAL and is recorded, not fixed. "
        "[UNVERIFIED] U5 stays open. Do NOT synthesise a line."
    )


# The owner half IS fully implemented — FOUR add-back lines per schedule, split on
# TWO axes (Arizona vs other-state × prior-year vs current-year), because the
# add-back is keyed to tax PAID DURING the calendar year and must be split by the
# year it relates to. Note the CREDIT is ONE line and is NOT decomposed by year.
AZ_OWNER_ADDBACK_LINES: dict[str, tuple[str, ...]] = {
    "AZ_165_SCHK1": ("12", "13", "14", "15"),
    "AZ_165_SCHK1NR": ("24", "25", "26", "27"),
    "AZ_120S_SCHK1": ("9", "10", "11", "12"),
    "AZ_120S_SCHK1NR": ("22", "23", "24", "25"),
}
AZ_OWNER_ADDBACK_AXES = ("arizona_vs_other_state", "prior_year_vs_current_year")
AZ_OWNER_CREDIT_LINES: dict[str, str] = {
    "AZ_165_SCHK1": "11", "AZ_165_SCHK1NR": "23",
    "AZ_120S_SCHK1": "8", "AZ_120S_SCHK1NR": "21",
}
# ⚠ A partnership that did NOT elect for TY2025 may STILL have to issue K-1
# Part 7 lines 12/14. Part 7's own gate: "Complete Part 7 if the partner
# consented to the partnership's election ... for this year OR FOR A PRIOR YEAR."
# This defeats any "if Q.A = No, suppress Part 7" shortcut. Pub 713 confirms the
# prior-year leg survives a non-election year.
AZ_PART7_SURVIVES_NON_ELECTION_YEAR = True


# ═══════════════════════════════════════════════════════════════════════════
# ⚠⚠ ESTIMATED PAYMENTS — THE $150,000 TEST
#     ONE NAMED CONSTANT FOR THE BASIS (D-12 A1); STRICTLY GREATER FOR THE
#     BOUNDARY (settled, no ruling needed)
# ═══════════════════════════════════════════════════════════════════════════
AZ_EST_THRESHOLD: dict[int, int] = {2025: 150_000}

# ⚠⚠ THE ONE THING TO CHANGE IF AZDOR EVER ANSWERS. Campaign D-12 A1 ruled the
# statute's BARE "taxable income" — the only one of AZDOR's four printed bases
# with controlling authority behind it. RECORDED AS A RULING ON A CONTESTED
# QUESTION, NOT A PUBLISHED AZDOR POSITION. U19 STAYS OPEN AS A MATTER OF FACT.
#
# ⚠⚠ A1 REFINED, SAME SESSION (2026-08-19) — THE RULING NAMED A **SOURCE**; IT NOW
# ALSO NAMES A **NUMBER**. The Arizona authoring pass surfaced that A1 as first
# ruled settled WHICH SOURCE GOVERNS but not WHICH FIGURE TO COMPUTE, and said so
# rather than resolving it silently. For a partnership, Title 43 chapter 14
# **defines that very term** at A.R.S. § 43-1401(2) as "ARIZONA TAXABLE INCOME"
# — i.e. AZDOR's base 2 — so on its most natural reading the ruled source
# RESOLVES INTO base 2 rather than standing apart from all four. And base 2 vs
# base 3 was THE WHOLE REASON A1 WAS BLOCKING (the $1,000,000 / 10%-consenting
# worked case turns on exactly that).
#
# ⚠ THE REFINEMENT NARROWS WHAT WE COMPUTE; IT DOES NOT CLOSE THE QUESTION. All
# four candidate bases stay on the record, the three losers stay explicitly NOT
# REFUTED, the ruling still disclaims itself as not a published AZDOR position,
# and U19 STAYS OPEN AS A MATTER OF FACT. The preparer diagnostic continues to
# mark the threshold determination PROVISIONAL.
AZ_EST_MEASUREMENT_BASIS = "statutory_bare_taxable_income"          # the SOURCE leg
AZ_EST_MEASUREMENT_BASIS_RESOLVES_TO = "arizona_taxable_income"     # the NUMBER leg (A1 REFINED)
AZ_EST_MEASUREMENT_DEFINITION = "A.R.S. § 43-1401(2)"

AZ_EST_MEASUREMENT_BASIS_RULING = (
    "CAMPAIGN RULING D-12 A1 (2026-08-19) — A RULING ON A CONTESTED QUESTION, NOT A PUBLISHED AZDOR "
    "POSITION. AZDOR prints FOUR different measurement bases and FOUR OF SIX DOCUMENTS CONTRADICT "
    "THEMSELVES INTERNALLY. Ken ruled the statutory reading (A.R.S. § 43-581(C)'s bare 'taxable "
    "income') as the only one with controlling authority. ⚠ REFINED THE SAME SESSION: that ruling "
    "named a SOURCE without naming a NUMBER, and A.R.S. § 43-1401(2) DEFINES the statute's term as "
    "'ARIZONA TAXABLE INCOME', so the ruled source RESOLVES TO base 2 — follow the statutory "
    "definition where it leads, which is the same reasoning that produced A1 in the first place. "
    "[UNVERIFIED] U19 STAYS OPEN AS A MATTER OF FACT. Settled by: an AZDOR ruling, procedure, or "
    "written Corporate Income Tax section response."
)

AZ_EST_MEASUREMENT_BASIS_REFINEMENT = (
    "WHY THE REFINEMENT HAPPENED, so a later reader sees reasoning rather than an unexplained "
    "change: A1 as first ruled picked 'the statute's bare taxable income' as the measurement base. "
    "That settles WHICH SOURCE GOVERNS but NOT WHICH NUMBER TO COMPUTE — and estimated-payment and "
    "Form 220/PTE penalty logic need a figure, not a citation. A.R.S. § 43-1401(2) defines a "
    "partnership's 'Arizona taxable income' as 'its Arizona gross income adjusted by the "
    "modifications specified in sections 43-1021 and 43-1022 and section 43-1414, subsection A' — "
    "which is precisely AZDOR's base 2. The authoring pass encoded A1 AS RULED, refused to resolve "
    "the gap on its own authority, and escalated it rather than discovering it at build time. "
    "RULED 2026-08-19: compute ARIZONA TAXABLE INCOME (§ 43-1401(2))."
)

# ⚠ WHERE § 43-1401(2) LANDS ON EACH FACE. For the PARTNERSHIP this is exact and
# sourced: the brief's own statutory reconstruction is that Form 165 line 8 (= line
# 5) PLUS line 9 (§ 43-1412 ¶1-16) equals § 43-1014(B)(1)(a)(ii) — therefore
# § 43-1401(2) ALONE IS **LINE 5**, and NOT line 10.
# ⚠⚠ THAT DISTINCTION MATTERS AND IS EASY TO MISS: line 10 is the PTE BASE, a
# LARGER figure that adds the sixteen separately-stated categories back in. Using
# line 10 for the § 43-581(C) test would be a FIFTH reading that no AZDOR document
# prints at all.
# ⚠ The test measures the **PRECEDING** taxable year, so it is the PRIOR-year line.
AZ_EST_MEASUREMENT_FIGURE_BY_FORM: dict[str, str] = {
    FORM_CODE_165: ("PRIOR-YEAR Form 165 LINE 5 — 'Partnership income adjusted to Arizona basis'. "
                    "§ 43-1401(2) = Arizona gross income adjusted by §§ 43-1021 / 43-1022 and "
                    "§ 43-1414(A), which is exactly what line 5 holds. ⚠ NOT line 10: line 8 + line "
                    "9 = § 43-1014(B)(1)(a)(ii), so § 43-1401(2) alone is line 5."),
    FORM_CODE_120S: ("PRIOR-YEAR Form 120S LINE 1 — 'TOTAL DISTRIBUTIVE INCOME (LOSS) from federal "
                     "Form 1120-S, Schedule K'. ⚠ AN ENGINEERING CONSEQUENCE OF THE VERIFIED "
                     "NEGATIVE, NOT A PUBLISHED DEFINITION — see AZ_EST_MEASUREMENT_SCORP_GAP."),
}

# ⚠⚠ THE SECOND-ORDER GAP THE REFINEMENT CREATES, RECORDED RATHER THAN PAPERED.
# A.R.S. § 43-1401 is the DEFINITIONS section of Title 43 CHAPTER 14, the
# PARTNERSHIP chapter. Its subsection (2) defines "Arizona taxable income" OF A
# PARTNERSHIP. **There is no S-corporation analogue in it**, and the research pass
# never pulled a corporate "Arizona taxable income" definition. So the
# refinement's mechanism — "chapter 14 defines the term" — is a PARTNERSHIP
# mechanism, while § 43-581(C) reaches "an entity that is treated as a partnership
# OR S CORPORATION".
#
# WHAT THIS FILE DOES ABOUT IT, and why it is not an invention: Form 120S carries
# NO Arizona modification apparatus at all (the verified negative at
# AZ_120S_NEGATIVE_PROOF). So on the S-corp return there is NOTHING to adjust, and
# the only Arizona income figure the form produces is line 1 = line 37. Applying
# the § 43-1401(2) SHAPE — federal income as adjusted by Arizona's modifications —
# to a return with zero modifications yields line 1 unchanged. That is
# BUILD-TO-THE-FORM, the campaign's standing posture (D-10 ruling 2, D-11 A1,
# D-12 A3 and A4), NOT a synthesised corporate definition.
# ⚠ IT IS STILL AN ENGINEERING INFERENCE AND IS LABELLED ONE. It carries its own
# diagnostic (D_AZ120S_EST_BASIS_NO_ANALOGUE) and is flagged for Ken.
AZ_EST_MEASUREMENT_SCORP_GAP = (
    "⚠ A.R.S. § 43-1401(2) IS A CHAPTER-14 **PARTNERSHIP** DEFINITION AND HAS NO S-CORPORATION "
    "ANALOGUE, while § 43-581(C) reaches partnerships AND S corporations alike. No corporate "
    "'Arizona taxable income' definition was pulled by the research pass. Delvio resolves the "
    "S-corp figure to Form 120S line 1 BY BUILDING TO THE FORM: Form 120S carries no Arizona "
    "modification apparatus at all, so applying the § 43-1401(2) shape to it changes nothing and "
    "line 1 = line 37 is the only Arizona income figure the return produces. ⚠ THIS IS AN "
    "ENGINEERING INFERENCE, NOT A PUBLISHED AZDOR OR STATUTORY DEFINITION, and it is a "
    "SECOND-ORDER consequence of the A1 refinement rather than something the refinement ruled on. "
    "Diagnostic: D_AZ120S_EST_BASIS_NO_ANALOGUE."
)

# All four candidates, kept on the record so a DOR answer can be adjudicated
# rather than inherited. Do NOT delete the losing three.
AZ_EST_MEASUREMENT_BASIS_CANDIDATES: dict[str, dict] = {
    "statutory_bare_taxable_income": {
        "label": "bare 'taxable income'",
        "sources": ("A.R.S. § 43-581(C)", "Form 165 instructions", "Form 120S instructions",
                    "Form 120/PTE-W instructions (occurrence 1)", "Pub 713 narrative"),
        "status": ("RULED (D-12 A1) — THE SOURCE LEG. ⚠ REFINED the same session: § 43-1401(2) "
                   "DEFINES this very term as 'Arizona taxable income', so the ruled source "
                   "RESOLVES INTO base 2 rather than standing apart from it."),
    },
    "arizona_taxable_income": {
        "label": "'ARIZONA taxable income' (A.R.S. § 43-1401(2) for a partnership)",
        "sources": ("Form 220/PTE instructions ×2", "Form 120/PTE-W instructions (occurrence 2)",
                    "Pub 713 FAQ"),
        "status": ("not refuted — recorded; ⚠ AND THIS IS THE FIGURE THE RULED STATUTORY SOURCE "
                   "RESOLVES TO (D-12 A1 REFINED, 2026-08-19). It reaches the engine through the "
                   "STATUTORY DEFINITION, not because AZDOR's base-2 documents were preferred over "
                   "its base-1 documents."),
    },
    "pte_income": {
        "label": "'PTE income' — only the CONSENTING owners' share",
        "sources": ("Form 165 instructions", "Form 120S instructions"),
        "status": "not refuted — recorded; MATERIALLY NARROWER than the others",
    },
    "total_taxable_income": {
        "label": "'TOTAL taxable income'",
        "sources": ("Booklet 120/165ES",),
        "status": "not refuted — recorded",
    },
}
AZ_EST_BASIS_WORKED_DIVERGENCE = (
    "NOT ACADEMIC. An entity with $1,000,000 of Arizona taxable income and 10% consenting ownership "
    "has $100,000 of PTE income: IN under base 2 and OUT under base 3, from readings printed in the "
    "SAME instruction book. It decides whether the Form 220/PTE underpayment penalty applies."
)
AZ_EST_INTERNAL_CONTRADICTIONS = {
    "Form 120/PTE-W instructions": ("statutory_bare_taxable_income", "arizona_taxable_income"),
    "Form 165 instructions": ("statutory_bare_taxable_income", "pte_income"),
    "Form 120S instructions": ("statutory_bare_taxable_income", "pte_income"),
    "Booklet 120/165ES": ("statutory_bare_taxable_income", "arizona_taxable_income",
                          "total_taxable_income"),
}

# ⚠⚠ THE BOUNDARY IS SETTLED AND NEEDS NO RULING: **EXCEEDS**, so an entity at
# EXACTLY $150,000 is OUT. SEVEN sources say so — the statute plus all six
# instruction sets. ONE Pub 713 FAQ answer says 'or more'; Pub 713's own FAQ
# lead-in offers a THIRD phrasing ('meets or exceeds'). Pub 713 is internally
# inconsistent THREE WAYS and cannot displace the statute.
# ⚠⚠ AN EARLIER VERIFICATION PASS FLIPPED THIS THE WRONG WAY AND A LATER ONE
# CAUGHT IT. It is pinned in validate_az.py in BOTH directions so it cannot drift
# back. Vintage-clean: `43-581` occurs ZERO times in the Ch. 140 chaptered PDF and
# Ch. 182 does not amend it either.
AZ_EST_BOUNDARY = "exceeds"                      # STRICTLY GREATER THAN
AZ_EST_BOUNDARY_EXACTLY_AT_THRESHOLD_IS_IN = False
AZ_EST_BOUNDARY_SOURCE_COUNT_EXCEEDS = 7
AZ_EST_BOUNDARY_SOURCE_COUNT_OR_MORE = 1
AZ_EST_BOUNDARY_CORRECTION_HISTORY = (
    "conformity/az_conformity.md §4 and its §12 correction H flipped 'exceeds' to 'or more' on the "
    "strength of ONE Pub 713 FAQ sentence. THE CORRECTION WAS WRONG AND THE ORIGINAL TEXT WAS "
    "RIGHT (source brief §8.5, confirmed final at §16.2). The campaign record needs amending. "
    "Recorded here so a later pass RE-ADJUDICATES rather than inherits."
)
AZ_581C_VERBATIM = (
    "C. For taxable years beginning from and after December 31, 2021, an entity that is treated as a "
    "partnership or S corporation for federal income tax purposes, that elects to pay the tax under "
    "section 43-1014 and whose taxable income for the taxable year exceeds $150,000 in the preceding "
    "taxable year shall make payments of estimated tax during the taxable year in a manner that is "
    "consistent with the manner prescribed in this section for individuals."
)


def az_est_measurement_figure(form_code: str, prior_year_line: float | None) -> dict:
    """THE SECOND STEP A1 ORIGINALLY LACKED: turn the ruled SOURCE into a NUMBER.

    A1 as first ruled named the statute's bare "taxable income" — which settles
    WHICH SOURCE GOVERNS but not WHICH FIGURE TO COMPUTE. A1 AS REFINED
    (2026-08-19) follows the statutory definition where it leads: A.R.S.
    § 43-1401(2) DEFINES that term as **ARIZONA TAXABLE INCOME**, so that is the
    figure the engine computes.

    PARTNERSHIP — exact and sourced. § 43-1401(2) is "Arizona gross income adjusted
    by the modifications specified in sections 43-1021 and 43-1022 and section
    43-1414, subsection A", which is precisely **Form 165 LINE 5**.
    ⚠⚠ NOT LINE 10. Line 8 (= line 5) PLUS line 9 reconstructs
    § 43-1014(B)(1)(a)(ii), so § 43-1401(2) ALONE is line 5; line 10 is the larger
    PTE BASE and using it here would be a FIFTH reading no AZDOR document prints.

    S CORPORATION — ⚠ AN ENGINEERING INFERENCE, AND LABELLED ONE. § 43-1401 is a
    chapter-14 PARTNERSHIP definitions section with no S-corp analogue, while
    § 43-581(C) reaches both entity types. Because Form 120S carries NO Arizona
    modification apparatus (the verified negative), applying the § 43-1401(2)
    SHAPE to it changes nothing and the figure is **line 1 = line 37**. That is
    BUILD-TO-THE-FORM, not a synthesised corporate definition — but it is a
    SECOND-ORDER consequence of the refinement rather than something the
    refinement ruled on. See AZ_EST_MEASUREMENT_SCORP_GAP.

    ⚠ The test measures the **PRECEDING** taxable year.
    """
    if form_code not in AZ_EST_MEASUREMENT_FIGURE_BY_FORM:
        raise ArizonaFormGovernsError(
            f"Unknown Arizona form code {form_code!r}. The § 43-581(C) measurement figure lands on "
            f"DIFFERENT LINES on the two returns (Form 165 line 5; Form 120S line 1) and this helper "
            f"refuses to default."
        )
    return {
        "basis_source": AZ_EST_MEASUREMENT_BASIS,                 # the ruled SOURCE leg
        "basis_resolves_to": AZ_EST_MEASUREMENT_BASIS_RESOLVES_TO,  # the ruled NUMBER leg
        "definition": AZ_EST_MEASUREMENT_DEFINITION,
        "source_line": AZ_EST_MEASUREMENT_FIGURE_BY_FORM[form_code],
        "figure": None if prior_year_line is None else float(prior_year_line),
        "is_engineering_inference": form_code == FORM_CODE_120S,
        "diagnostic": ("D_AZ120S_EST_BASIS_NO_ANALOGUE" if form_code == FORM_CODE_120S
                       else "D_AZ_U19_150K_BASIS"),
        "ruling": "campaign D-12 A1 as REFINED 2026-08-19",
        "provisional": True,          # ⚠ U19 stays OPEN AS A MATTER OF FACT
        "unverified_item": "U19",
    }


def az_estimated_payments_required(prior_year_taxable_income: float,
                                   year: int = FORM_TAX_YEAR) -> bool:
    """A.R.S. § 43-581(C) — STRICTLY GREATER THAN $150,000.

    ⚠ `>` NOT `>=`. An entity at EXACTLY $150,000 of prior-year taxable income
    owes NO PTE estimated payments. See AZ_EST_BOUNDARY_CORRECTION_HISTORY.
    ⚠ WHICH taxable income is `AZ_EST_MEASUREMENT_BASIS`, RESOLVING TO
    `AZ_EST_MEASUREMENT_BASIS_RESOLVES_TO` per § 43-1401(2) — a RULING (D-12 A1 as
    refined), NOT a published AZDOR position. U19 is open and the determination
    stays PROVISIONAL. Use az_estimated_payments_required_for() to resolve the
    figure and apply the boundary in one step.
    """
    return float(prior_year_taxable_income) > float(_yk(AZ_EST_THRESHOLD, year))


def az_estimated_payments_required_for(form_code: str, prior_year_line: float | None,
                                       year: int = FORM_TAX_YEAR) -> dict:
    """Resolve the § 43-1401(2) figure, THEN apply the settled `exceeds` boundary.

    The two halves of the § 43-581(C) question were resolved differently and stay
    separable on purpose:
      • THE NOUN — which taxable income — is a RULING on a contested question
        (D-12 A1, refined). U19 is OPEN and the answer is PROVISIONAL.
      • THE VERB — "exceeds" — is SETTLED by seven sources and needs no ruling.
        ⚠ An earlier verification pass flipped it the wrong way and a later one
        caught it, so it is pinned in both directions and must not drift.
    """
    resolved = az_est_measurement_figure(form_code, prior_year_line)
    figure = resolved["figure"]
    resolved["threshold"] = _yk(AZ_EST_THRESHOLD, year)
    resolved["boundary"] = AZ_EST_BOUNDARY                    # STRICTLY GREATER THAN
    resolved["required"] = (None if figure is None
                            else az_estimated_payments_required(figure, year))
    return resolved


# Installments. ⚠ THE FOURTH ONE IS THE 15TH DAY OF THE **1ST** MONTH AFTER THE
# CLOSE OF THE TAXABLE YEAR — NOT the 12th month. Form 220/PTE line 7 prints the
# CORPORATE pattern (4th/6th/9th/12th) on the FACE and appends "PTE's see
# instructions", where the 1st-month rule lives. A loader reading the face alone
# puts the fourth PTE installment THREE MONTHS EARLY (W17).
AZ_PTE_INSTALLMENT_MONTHS = ("4th month of the taxable year",
                             "6th month of the taxable year",
                             "9th month of the taxable year",
                             "1st month FOLLOWING the close of the taxable year")
AZ_CORP_INSTALLMENT_MONTHS = ("4th", "6th", "9th", "12th")   # ⚠ NOT the PTE pattern
AZ_PTE_INSTALLMENT_CALENDAR_YEAR_DATES = ("April 15", "June 15", "September 15",
                                          "January 15 of the following year")
AZ_PTE_INSTALLMENT_COUNT = 4


def az_pte_installment_months() -> tuple[str, ...]:
    return AZ_PTE_INSTALLMENT_MONTHS


# Required annual payment — a SAFE HARBOUR framing ("the SMALLER of"), not a
# minimum. Pub 713 and both instruction books agree verbatim.
AZ_REQUIRED_ANNUAL_PAYMENT_RULE = (
    "the SMALLER of (a) ninety percent of the current taxable year's Arizona tax liability, or "
    "(b) one hundred percent of the tax due for the previous taxable year"
)
AZ_TAX_LIABILITY_DEFINITION = (
    "'Tax liability' means the liability reduced by any refundable tax credits and the claim of "
    "right adjustment, if applicable."
)
AZ_EST_PENALTY_FLOOR = {2025: 1_000}     # § 43-581(E)(2) — no penalty if liability < $1,000
AZ_EFT_THRESHOLD = {2025: 500}
AZ_EFT_FAILURE_PENALTY_PCT = "0.05"      # A.R.S. § 42-1125(O)
AZ_NO_OVERPAYMENT_PENALTY = True         # Pub 713: "Is there a penalty for overpayment? No."


def az_required_annual_payment(current_year_liability: float,
                               prior_year_tax_due: float | None) -> float:
    """The § 43-581 safe harbour: the SMALLER of 90% current or 100% prior."""
    ninety = round(float(current_year_liability) * 0.90, 2)
    if prior_year_tax_due is None:
        return ninety
    return min(ninety, round(float(prior_year_tax_due), 2))


# ═══════════════════════════════════════════════════════════════════════════
# THE ELECTION — ANNUAL, NOT BINDING, AND THE TIMELINESS RULE WAS REPEALED
# RETROACTIVELY TO TY2021
# ═══════════════════════════════════════════════════════════════════════════
AZ_PTE_ELECTION_IS_ANNUAL = True
AZ_PTE_ELECTION_BINDS_FUTURE_YEARS = False
AZ_PTE_ELECTION_TIMELINESS_REQUIRED = False
AZ_PTE_ELECTION_TIMELINESS_REPEAL = (
    "S.B. 1274, 57th Leg. 1st Reg. Sess. (2025) = LAWS 2025 CHAPTER 182, 'APPROVED BY THE GOVERNOR "
    "MAY 13, 2025'. **Sec. 6** amends § 43-1014(A): 'The election under this subsection ~~must be "
    "made on or before the due date or extended due date of the~~ IS MADE BY FILING THE business's "
    "return under this title.' **Sec. 9(A)** Retroactivity: 'Section 43-1014 ... applies "
    "retroactively to taxable years beginning from and after December 31, 2021.' So for TY2022-TY2025 "
    "there is NO timeliness condition on the PTE election. "
    "⚠ [CORRECTED — verification pass §16.4 C4: the Ch. 182 section numbering was OFF BY ONE "
    "throughout the brief. The CHAPTERED act's own headers read Sec.6 = § 43-1014, Sec.7 = § 43-1414, "
    "Sec.8 = Laws 2023 ch.147 § 3, Sec.9 = Retroactivity. Substance unaffected.] "
    "⚠ Note also that NO retroactivity was granted for the § 43-1414 amendment — Sec. 9(B) covers "
    "only Laws 2023 ch. 147 § 3."
)
AZ_CH182_SECTION_MAP: dict[str, str] = {
    "Sec. 6": "A.R.S. § 43-1014 — strikes the PTE election's timely-filing requirement",
    "Sec. 7": "A.R.S. § 43-1414 — subsection (A) ONLY (adds § 6227 AAR partnerships)",
    "Sec. 8": "Laws 2023, ch. 147, § 3 — a different subject",
    "Sec. 9": "Retroactivity — (A) § 43-1014 to TY2022+; (B) Laws 2023 ch.147 § 3 only",
}
# ⚠ THE STALE-LAW TRAP: Booklet 120/165ES, posted under AZDOR's **2025** row, has
# /ModDate 2024-11-19 and is headed "2024 CORPORATE INCOME TAX HIGHLIGHTS". It
# still says "This election must be made by the S Corporation no later than the
# due date or extended due date of its return." THAT SENTENCE IS REPEALED LAW.
# Use the booklet for the VOUCHERS ONLY.
AZ_ES_BOOKLET_CARRIES_REPEALED_LAW = True

AZ_PTE_ELECTION_ON_AMENDED_RETURN = True         # within the four-year SOL
AZ_PTE_REVOCATION_ON_AMENDED_RETURN = True       # within the four-year SOL
AZ_PTE_ELECTION_SOL_YEARS = 4
AZ_PTE_ELECTION_IS_N_OWNER_EVENT = True
AZ_PTE_ELECTION_CASCADE_NOTE = (
    "⚠ BOTH the election and its revocation are N-OWNER-RETURN EVENTS. One entity amendment "
    "cascades to EVERY consenting owner: each partner/shareholder who did not opt out must also "
    "file an amended Arizona individual return (to claim, or to remove, the PTE tax credit). A "
    "WORKFLOW fact, not just a computation."
)

# Eligibility / opt-out. A.R.S. § 43-1014(C) and (D).
AZ_PTE_ELIGIBLE_OWNER_TYPES = ("individual", "estate", "trust")
AZ_PTE_INELIGIBLE_OWNER_TYPES = ("corporation", "S corporation", "partnership", "IRA",
                                 "any other entity")
AZ_PTE_OPT_OUT_NOTICE_DAYS = 60
AZ_PTE_NON_RESPONSE_MEANS = "included"    # opt-OUT, not opt-in
AZ_PTE_LOOK_THROUGH_OWNERS_MAY_PARTICIPATE = True   # grantor trusts, SMLLCs disregarded to an individual
AZ_PTE_TIERED_PARTICIPATION_ALLOWED = False
AZ_PTE_TIERED_NOTE = (
    "Pub 713: 'Can a lower-tier partnership or S Corporation make the PTE election and pass the "
    "credit through to its partners or shareholders that are other partnerships or S Corporations? "
    "NO. Only individuals, estates, or trusts that did not opt out of the PTE election may "
    "participate.' A lower-tier entity may still make its OWN election for its OWN eligible owners; "
    "what it cannot do is pass the credit UP. On the form an upper-tier partnership partner is an "
    "'O' in Schedule D column (f) and lands in E7."
)
AZ_PTE_MULTIPLE_ELECTIONS_PER_OWNER_OK = True
AZ_PTE_FINAL_YEAR_ELECTION_OK = True
AZ_PTE_LOSS_YEAR_ELECTION_OK_BUT_POINTLESS = True   # consistent with the zero floors


# ⚠⚠ PART 2 IS **NOT** GATED ON QUESTION A ALONE (W18).
def az_part2_required(question_a_election: bool, pte_estimated_payments_made: float) -> bool:
    """Both Part 2 headers, verbatim: 'Complete only if ... answered "Yes" to
    Question A on page 1, OR ESTIMATED PAYMENTS WERE MADE AND THE PARTNERSHIP IS
    NOT CLAIMING THE PTE ELECTION.'

    ⚠ A loader branching on Question A alone SUPPRESSES PART 2 FOR EXACTLY THE
    POPULATION THAT MOST NEEDS IT. TY2025 is the year for it: the federal SALT cap
    moved from $10,000 to $40,000 and Pub 713 scripts the '$0 return' refund path
    for entities that prepaid and then declined to elect.
    """
    return bool(question_a_election) or float(pte_estimated_payments_made or 0) > 0


AZ_ZERO_RETURN_PATH_IS_SCRIPTED = True
AZ_ZERO_RETURN_VARIANTS_ON_120S = 2      # 'not subject to Arizona income tax' / 'subject to'
AZ_ZERO_RETURN_REFUND_RESTRICTIONS = (
    "⚠ 'This refund cannot be applied to the S Corporation's 2026 taxable year PTE estimated tax "
    "liability. It cannot be applied to an individual shareholder's tax liability.' The estimated "
    "payments come back to the ENTITY as cash, full stop."
)


# ═══════════════════════════════════════════════════════════════════════════
# THE OWNER-SIDE CREDIT — A.R.S. § 43-1077
# ═══════════════════════════════════════════════════════════════════════════
AZ_PTE_CREDIT_REFUNDABLE = False
AZ_PTE_CREDIT_CARRYFORWARD_YEARS = 5
AZ_PTE_CREDIT_CARRYFORWARD_ORDERING = (
    "Pub 713: a PRIOR-year PTE credit carryforward may be used up BEFORE the current-year PTE "
    "credit ('Yes. The 2024 PTE tax credit carryforward can be used up before applying the 2025 PTE "
    "tax credit.')"
)
# ⚠ ARIZONA'S OWN FORM 355 — SEE THE BANNER. Not Massachusetts Form 355.
AZ_FORM_355_COLLISION_NOTE = (
    "⚠ ARIZONA HAS ITS OWN FORM 355 — 'Credit for Entity-Level Income Tax Paid on Your Behalf'. It "
    "is a NUMBER COLLISION with MASSACHUSETTS Form 355 (the MA C-corporation excise return), and it "
    "is a trap for the next reader. Every 'Form 355' reference in Arizona material is ARIZONA'S, "
    "confirmed on the AZDOR K-1 faces themselves. MA left Wave 4 for its own wave (D-12 Group B)."
)
AZ_FORM_355_LINE_BY_ENTITY: dict[str, str] = {
    M_1065: "Arizona Form 355, Part 1, line 1",
    M_1120S: "Arizona Form 355, Part 1, line 2",
}
AZ_ESTATE_TRUST_CREDIT_ROUTE = "Arizona Form 141AZ, line 19 (see its instructions)"
AZ_FIDUCIARY_MAY_DISTRIBUTE_CREDIT_TO = "individual beneficiaries ONLY"

# ⚠ THE CREDIT IS KEYED TO TAX **PAID**, NOT TAX ACCRUED — and the forms give no
# reconciliation schedule (U9 / W19).
AZ_CREDIT_STATUTORY_KEY = "tax PAID (§ 43-1077(B))"
AZ_CREDIT_BUILD_KEY = "liability"        # Pub 713's own Addendum #1 example allocates from liability
AZ_CREDIT_KEY_DIAGNOSTIC_ID = "D_AZ_U9_PTE_CREDIT_PAID_VS_OWED"
AZ_CREDIT_KEY_NOTE = (
    "§ 43-1077(B): the credit is 'the portion of the tax PAID by the partnership or S corporation'. "
    "Pub 713 hammers it: 'if the partnership or S Corporation does not pay its PTE tax liability, "
    "the S Corporation cannot pass through the full amount ... as a tax credit'. But Form 165 line "
    "25 and Form 120S line 52 compute tax OWED and NO SCHEDULE RECONCILES OWED TO PAID BEFORE THE "
    "K-1s ARE CUT. Recommended default: key the K-1 credit to the LIABILITY (matching Pub 713's own "
    "worked example) and raise a diagnostic whenever payments are less than line 25 / line 52. "
    "Backstop at § 43-1014(B)(2): the department may collect from the OWNERS if the entity does not "
    "pay. [UNVERIFIED] U9."
)

# ⚠ CREDIT ORDERING ON FORM 120S IS A REAL STRUCTURAL FACT, AND THE FORM IS NOT
# AMBIGUOUS EVEN THOUGH PUB 713 IS. Nonrefundable credits apply at line 15
# against line 14 (corporate tax + recapture) and the PTE tax is added AFTER at
# line 18/19 — so nonrefundable credits CANNOT reduce the PTE tax. Refundable
# credits sit in the PAYMENTS block at line 20 and CAN. Pub 713 says both 'No'
# and 'nothing precludes' in the same section (U4 / W7). THE FORM GOVERNS.
AZ_120S_NONREFUNDABLE_CREDITS_REACH_PTE_TAX = False
AZ_120S_REFUNDABLE_CREDITS_REACH_PTE_TAX = True
AZ_165_HAS_ENTITY_CREDIT_LINE = False    # Form 165 has NO entity-level credit line at all


# ═══════════════════════════════════════════════════════════════════════════
# APPORTIONMENT — ONE ENGINE, TWO SCHEDULE NAMES, AND A **DYNAMIC** DIVISOR
#
# Form 165 Schedule C (rows C1-C5) and Form 120S Schedule A (rows A1-A5) are
# STRUCTURALLY IDENTICAL, differing only in the payroll-factor wording
# ("per federal Form 1065" vs "per federal Form 1120S") and in their destination
# pointers. THIS is the one place the two Arizona returns genuinely do share an
# engine — and it is NOT a modification engine.
# ═══════════════════════════════════════════════════════════════════════════
AZ_APPORTIONMENT_METHODS = ("air_carrier", "standard", "sales_factor_only")
AZ_APPORTIONMENT_DECIMALS = 6
AZ_APPORTIONMENT_ROUNDING = (
    "carry to six places after the decimal; if the seventh place is five or more, round the sixth "
    "decimal place up"
)
AZ_SALES_WEIGHT: dict[str, int] = {"standard": 2, "sales_factor_only": 1}
AZ_FACTOR_CAPS: dict[str, str] = {
    "property": "may not exceed 1.0",
    "sales_standard": "may not exceed 2.0",
    "sales_only": "may not exceed 1.0",
}
AZ_FACTOR_EXCLUSION_RULE = (
    "Partnerships must EXCLUDE a factor if BOTH the numerator and the denominator of that factor "
    "are zero. Do NOT exclude a factor if the numerator is zero and the denominator is greater than "
    "zero. See A.A.C. R15-2D-901(B)."
)


def az_factor_is_excluded(numerator: float, denominator: float) -> bool:
    """A.A.C. R15-2D-901(B): excluded ONLY when BOTH are zero.

    ⚠ A zero numerator with a positive denominator is a LIVE ZERO FACTOR, not an
    excluded one. This is the rule most engines get wrong.
    """
    return float(numerator) == 0.0 and float(denominator) == 0.0


def az_apportionment_divisor(property_excluded: bool, payroll_excluded: bool,
                             sales_excluded: bool) -> int | None:
    """⚠ THE DIVISOR IS DYNAMIC: 4, 3, 2, OR NONE.

    Verbatim: 'If either the property or the payroll factor is excluded,
    determine the average ratio by dividing the total ratio by THREE. If the
    SALES factor is excluded, determine the average ratio by dividing the total
    ratio by TWO. If TWO of the factors are excluded, the remaining factor,
    WITHOUT RESPECT TO ANY WEIGHTING, is the apportionment ratio.'

    ⚠ Note that when SALES is the excluded factor the divisor drops to TWO even
    though sales is DOUBLE-WEIGHTED — the weighting and the divisor are NOT tied
    to each other. Returns None when two factors are excluded (no divisor at all;
    the survivor IS the ratio, unweighted).
    """
    excluded = sum((bool(property_excluded), bool(payroll_excluded), bool(sales_excluded)))
    if excluded == 0:
        return 4
    if excluded >= 2:
        return None          # the remaining factor IS the ratio, unweighted
    if sales_excluded:
        return 2
    return 3                 # property OR payroll excluded


# ⚠ `0.000000` AND BLANK MEAN OPPOSITE THINGS. Stated verbatim on both returns
# (Form 165 line C5 note; Form 120S line 7 note). A null-vs-zero bug here
# SILENTLY ZEROES every nonresident owner's Arizona income.
AZ_RATIO_ZERO_MEANS = "no Arizona nexus"
AZ_RATIO_BLANK_MEANS = "income sourced ENTIRELY within Arizona (same as 1.000000)"


def az_nexus_from_ratio(ratio: str | float | None) -> str:
    if ratio is None or ratio == "":
        return AZ_RATIO_BLANK_MEANS
    if float(ratio) == 0.0:
        return AZ_RATIO_ZERO_MEANS
    return "apportioned" if float(ratio) < 1.0 else AZ_RATIO_BLANK_MEANS


# ⚠ FORM 165 QUESTION D AND FORM 120S QUESTION B ARE **INVERTED**.
AZ_MULTISTATE_QUESTION: dict[str, dict] = {
    FORM_CODE_165: {"question": "D", "label": "Is this partnership an Arizona-only partnership?",
                    "yes_means_multistate": False},
    FORM_CODE_120S: {"question": "B",
                     "label": "Does the S corporation conduct business within and without Arizona?",
                     "yes_means_multistate": True},
}


def az_is_multistate(form_code: str, question_answer_is_yes: bool) -> bool:
    """⚠ REFUSES to guess. The two forms ask the SAME question OPPOSITE ways.

    Form 165 line D 'Yes' = Arizona-only = NOT multistate.
    Form 120S line B 'Yes' = within and without Arizona = IS multistate.
    A shared boolean is inverted for one of them.
    """
    if form_code not in AZ_MULTISTATE_QUESTION:
        raise ArizonaFormGovernsError(
            f"Unknown Arizona form code {form_code!r}. The multistate gate is asked in OPPOSITE "
            f"polarity on Form 165 (question D, Yes = Arizona-only) and Form 120S (question B, "
            f"Yes = multistate); this helper refuses to default."
        )
    spec = AZ_MULTISTATE_QUESTION[form_code]
    return bool(question_answer_is_yes) if spec["yes_means_multistate"] else (not question_answer_is_yes)


# Schedule MSP — the ONLY stateful multi-year attribute on the Arizona PTE
# returns. A.R.S. § 43-1147(B)/(C): the election is made on a TIMELY FILED
# ORIGINAL return and is BINDING FOR FIVE CONSECUTIVE TAXABLE YEARS.
AZ_MSP_QUALIFY_THRESHOLD = "0.850000"
AZ_MSP_BINDING_YEARS = 5
AZ_MSP_REQUIRES_TIMELY_ORIGINAL_RETURN = True
AZ_MSP_PART_A_ONLY_IN_YEAR_ONE = True
AZ_MSP_TERMINATION = ("without department permission on acquisition or merger of the taxpayer",
                      "with department permission before the five years expire")
AZ_MSP_DESTINATION: dict[str, str] = {
    FORM_CODE_165: "Schedule C line C3b, column A",
    FORM_CODE_120S: "Schedule A line A3b, column A",
}
# ⚠ TWO ELECTIONS ON ONE RETURN WITH **OPPOSITE** TIMELINESS RULES (W21): the MSP
# election REQUIRES a timely filed original return; the PTE election does NOT
# (S.B. 1274 struck that requirement retroactively to TY2021).
AZ_ELECTION_TIMELINESS_DIVERGENCE = (
    "MSP: timely filed ORIGINAL return REQUIRED (§ 43-1147(C)(1)). "
    "PTE: NO timeliness condition (§ 43-1014(A) as amended by Laws 2025 Ch. 182 Sec. 6, "
    "retroactive to TY2022). Two elections, same return, opposite rules."
)


def az_msp_qualifies(out_of_state_service_sales: float, total_sales_everywhere: float) -> dict:
    """Schedule MSP Part A: A3 = A1 / A2; qualify if A3 > 0.850000."""
    if float(total_sales_everywhere) == 0:
        return {"A3": None, "qualifies_on_A4": False,
                "note": "denominator is zero — fall through to lines A5/A6"}
    a3 = round(float(out_of_state_service_sales) / float(total_sales_everywhere), 6)
    return {"A3": f"{a3:.6f}", "qualifies_on_A4": a3 > float(AZ_MSP_QUALIFY_THRESHOLD),
            "alternate_qualification": "lines A5 (university campus) and A6 (support-services employer)"}


def az_aca_ratio(revenue_aircraft_miles_in_az: float, revenue_aircraft_miles_everywhere: float) -> str:
    """Schedule ACA line 3 = line 1 / line 2, six decimals.

    ⚠ Schedule ACA's own routing list omits Form 165 Part 2 line 22 and Form 120S
    Part 2 line 49 — but BOTH parent forms' line instructions say 'from Schedule
    C/A OR SCHEDULE ACA'. THE PARENT FORM CLOSES THE LOOP; the omission is not a
    prohibition (U12).
    """
    if float(revenue_aircraft_miles_everywhere) == 0:
        return "0.000000"
    return f"{round(float(revenue_aircraft_miles_in_az) / float(revenue_aircraft_miles_everywhere), 6):.6f}"


AZ_ACA_ROUTING_LIST_OMITS_PTE_LINES = True     # U12 — recorded so it is not read as a prohibition


# ═══════════════════════════════════════════════════════════════════════════
# ⚠⚠ FORM 165PA FAMILY — RED-DEFERRED (campaign D-12 A2). DO NOT PICK A RATE.
# ═══════════════════════════════════════════════════════════════════════════
AZ_165PA_STATUS = "RED_DEFER"
AZ_165PA_FAMILY = ("AZ_165PA", "AZ_165PA_SCHK1", "AZ_165PA_SCHK1NR", "AZ_165PA_X")
AZ_165PA_FACE_RATE = "0.045"        # printed on the face AND repeated in the instructions
AZ_165PA_STATUTORY_RATE = "0.025"   # § 43-1414(B)(1)(b) via the syllogism below
AZ_165PA_OVERTAX_FACTOR = 1.8       # 4.5 / 2.5 — building to the face over-taxes by 80%
AZ_165PA_CONFLICT = (
    "FORM-VS-STATUTE CONFLICT, REAL AND UN-REPEALED. Form 165PA face line 13 prints 'Multiply the "
    "amount on line 12 by the tax rate, 4.5%' and the instructions repeat it verbatim. "
    "A.R.S. § 43-1414(B)(1)(b): 'The tax shall be imposed on the Arizona share of the adjustments at "
    "THE HIGHEST TAX RATE IMPOSED ON INDIVIDUALS UNDER SECTION 43-1011' = 2.5% for TY2025. 4.5% was "
    "Arizona's top individual rate BEFORE the S.B. 1828 flat-tax phase-in completed. BOTH NEGATIVES "
    "VERIFIED: S.B. 1274 (Laws 2025 Ch. 182) Sec. 7 amended § 43-1414 subsection (A) ONLY — the "
    "capitalised new text appears only there and subsection (B) is entirely lowercase, i.e. "
    "unamended — and H.B. 4168 (Laws 2026 Ch. 140) does not amend § 43-1414 at all ('43-1414' "
    "occurs ZERO times in the chaptered PDF and the section is absent from the AN ACT list)."
)
AZ_165PA_SYLLOGISM = (
    "The 2.5% leg is reached BY SYLLOGISM because § 43-1011 cannot be read off azleg (U21): "
    "(1) § 43-1014(A) sets the PTE rate as 'the same as the highest tax rate prescribed by section "
    "43-1011'; (2) AZDOR prints that PTE rate as 2.5% on four TY2025 face lines and in Pub 713; "
    "(3) therefore the highest § 43-1011 rate for TY2025 IS 2.5%; (4) § 43-1414(B)(1)(b) imposes "
    "the 165PA tax at that same rate = 2.5%; (5) Form 165PA line 13 prints 4.5% ⇒ conflict."
)
AZ_165PA_LATE_FILING_PENALTY_PCT = "0.045"   # ⚠ ALSO 4.5% — AND THIS ONE IS CORRECT
AZ_165PA_TWO_45S_WARNING = (
    "⚠ DO NOT CONFLATE THE TWO 4.5%s. The Form 165PA LATE-FILING PENALTY is 4.5% and is CORRECT. "
    "Only the LINE 13 TAX RATE is stale. A search-and-replace on '4.5' breaks the penalty."
)
AZ_165PA_TRIGGER = (
    "Form 165 page-1 question J and the face note: 'For taxable years 2016 through 2025, if you "
    "received a federal imputed underpayment assessment, or you filed an Administrative Adjustment "
    "Request that resulted in a federal imputed underpayment assessment, you must file Arizona Form "
    "165PA to report those changes.' Due 90 days after the IRS final determination "
    "(§ 43-1414(B)(1)(a); computed on the 165PA face at Part 1 line B)."
)
AZ_165PA_COMPANIONS_UNREAD = True   # U13 — Sch. K-1, Sch. K-1(NR) and 165PA-X never downloaded


def az_165pa_rate(*_args, **_kwargs):
    """⚠ ALWAYS RAISES. D-12 A2: RED-DEFER rather than pick a rate."""
    raise ArizonaDeferredFormError(
        "Arizona Form 165PA is RED-DEFERRED (campaign D-12 A2). Its face and instructions print "
        "4.5% while A.R.S. § 43-1414(B)(1)(b) imposes the tax at the highest individual rate under "
        "§ 43-1011, which is 2.5% for TY2025. Building to the face KNOWINGLY OVER-TAXES BY 80%; "
        "building to the statute contradicts a printed FINAL form. Ken ruled: DEFER, with a "
        "diagnostic — no silent gap. The whole family (165PA, 165PA Sch. K-1, 165PA Sch. K-1(NR), "
        "165PA-X) is deferred. Settled by an AZDOR correction or a direct answer from the Corporate "
        "Income Tax section. [UNVERIFIED] U14."
    )


# ⚠ ONE 165PA OUTPUT DOES REACH FORM 165 EVEN WHILE 165PA ITSELF IS DEFERRED:
# the page-6 A4 worksheet instruction says that if the partnership RECEIVED a
# Form 165PA Schedule K-1(NR) with a positive line 3, it must FILE AN AMENDED
# FORM 165 and enter that amount on line A4. That is an INPUT to AZ_165 and is
# modelled; only the COMPUTATION of a 165PA is deferred.
AZ_165PA_K1NR_TRIGGERS_AMENDED_165 = True


# ═══════════════════════════════════════════════════════════════════════════
# PRINTED DEFECTS — TRANSCRIBE AS PRINTED, FLAG, DO NOT "FIX"
# Four printed cross-reference defects plus a stale year plus a mislabel, all in
# ONE TY2025 package. The FACE governs a face/instruction divergence; but where
# a SUPPORTING form's routing list is wrong about a PARENT form, the parent's own
# instructions govern (that is a different question).
# ═══════════════════════════════════════════════════════════════════════════
AZ_PRINTED_DEFECTS: list[dict] = [
    {"defect_id": "AZ-D1", "form": FORM_CODE_165, "location": "face line 39", "walk_item": "W5",
     "printed": "Amount of line 38 to be applied to 2025 estimated tax",
     "correct": ("the INSTRUCTION for the same line says 2026: 'The partnership may apply part or "
                 "all of an overpayment reported on line 38 as a 2026 PTE estimated tax payment.'"),
     "resolution": ("STALE YEAR ON THE FACE. On a TY2025 return, applying an overpayment to 2025 "
                    "estimated tax is meaningless. Compare Form 120S line 35, which correctly reads "
                    "'to be applied to 2026 estimated tax'. Transcribe as printed; compute 2026."),
     "independently_reconfirmed_by_verification_pass": True},
    {"defect_id": "AZ-D2", "form": FORM_CODE_120S, "location": "line 49 instruction", "walk_item": "W8",
     "printed": ("NOTE: The apportionment ratio entered on LINE 45 must be the same as the "
                 "apportionment ratio entered on line 7."),
     "correct": "line 49 == line 7",
     "resolution": ("LINE 45 IS AN INCOME AMOUNT, NOT A RATIO. The FACE is correct (line 49 is the "
                    "ratio line). ⚠ AND THE CROSS-CHECK CANNOT BE A HARD EQUALITY: line 7 is only "
                    "reached when the S corp has federal-level taxable income, so a multistate "
                    "electing S corp with no BIG and no excess net passive income never computes "
                    "line 7 yet still needs line 49. Encode: IF line 7 is populated, line 49 must "
                    "equal it; OTHERWISE line 49 comes from Schedule A line A5 / A3f or Schedule "
                    "ACA line 3 directly."),
     "independently_reconfirmed_by_verification_pass": True},
    {"defect_id": "AZ-D3", "form": "AZ_220_PTE", "location": "Part B line 5", "walk_item": "W20",
     "printed": ("Enter the 2025 Arizona tax liability from Form 99T, line 11 less line 12; or Form "
                 "120, line 21 less line 22; or Form 120A, line 13 less line 14; or Form 120S, line "
                 "19 less line 20, or FORM 165, LINE 23."),
     "correct": "Form 165, line 25",
     "resolution": ("Form 165 line 23 is 'Multiply the amount on line 21 by the decimal on line 22' "
                    "— an INTERMEDIATE APPORTIONED NONRESIDENT BASE, not a tax. Line 25 is 'Add "
                    "line 20 and line 24 ... the total amount of tax owed by the Partnership'. "
                    "Every other entry in the same sentence points at a NET TAX figure. COMPUTE "
                    "FROM FORM 165 LINE 25 AND FLAG. [UNVERIFIED] U11."),
     "independently_reconfirmed_by_verification_pass": True},
    {"defect_id": "AZ-D4", "form": "AZ_220_PTE", "location": "face line 37 routing list",
     "walk_item": "W25",
     "printed": ("Enter the total here and on Form 99T, line 22; or Form 120, line 29; or Form 120A, "
                 "line 21; or FORM 120S, LINE 25."),
     "correct": "Form 120S line 31, and Form 165 line 35 (which the list omits entirely)",
     "resolution": ("Form 120S line 25 is 'Overpayments of tax from original return or later "
                    "adjustments' — the estimated-penalty line is 31. And FORM 165 IS ABSENT FROM "
                    "THE LIST ALTOGETHER even though Form 165 line 35 imports this figure. "
                    "**BUILD TO THE 165 / 120S INSTRUCTIONS, WHICH ARE RIGHT — NOT TO THE 220/PTE "
                    "FACE.** [UNVERIFIED] U20."),
     "independently_reconfirmed_by_verification_pass": True},
    {"defect_id": "AZ-D5", "form": "AZ_120S_SCHK1NR", "location": "Part 5 line 20 label",
     "walk_item": "W14",
     "printed": ("Multiply the amount on line 19 by the shareholder's ownership percentage shown on "
                 "page 1. Enter the result. THIS IS THE SHAREHOLDER'S PORTION OF THE CREDIT."),
     "correct": "the shareholder's portion of the DISALLOWED FEDERAL EXPENSES",
     "resolution": ("IT IS NOT A CREDIT — it is a share of disallowed expenses (marijuana Schedule "
                    "DFE). The resident 120S K-1's parallel line 7 says it correctly. Printed-form "
                    "error; transcribe as printed and flag."),
     "independently_reconfirmed_by_verification_pass": False},
    {"defect_id": "AZ-D6", "form": "AZ_165_SCHK1NR", "location": "Part 8 lines 24-27 routing",
     "walk_item": "U8",
     "printed": "Form 140PY, page 3, line N",
     "correct": "unknown — the item LETTER is reliable, the PAGE NUMBER is not",
     "resolution": ("THE FORM 140PY / 140NR PAGE REFERENCES ACROSS THE FOUR OWNER SCHEDULES ARE "
                    "MUTUALLY INCONSISTENT: 165 Sch. K-1 says 140PY page 5 line N; 165 Sch. K-1(NR) "
                    "says page 3 line N; 120S Sch. K-1(NR) Part 6 says page 5 line N while Part 5 "
                    "on the SAME schedule says page 6 line V / 140NR page 6 line L against Part 6's "
                    "140NR page 5 line L. The item LETTERS (P/N/L/V/Q) are internally consistent. "
                    "**BIND ON THE ITEM LETTER, NOT THE PAGE NUMBER.** Settled by the TY2025 Form "
                    "140PY / 140NR faces (individual wave). [UNVERIFIED] U8."),
     "independently_reconfirmed_by_verification_pass": False},
    {"defect_id": "AZ-D7", "form": "AZ_165_SCHK1NR", "location": "Part 1 lines 10 and 14",
     "walk_item": "U7",
     "printed": "(no Form 140NR destination printed)",
     "correct": "unknown",
     "resolution": ("Every other income line on the face (4, 5, 6, 7, 8, 9, 11, 12, 13) carries a "
                    "printed 'Form 140NR Filers: Enter the amount in column (c) on: Line NN'. "
                    "'Guaranteed payments to partner' (line 10) and 'Other deductions' (line 14) do "
                    "not. A PRINTED-FORM GAP, verified against the face — not a transcription "
                    "artifact. The K-1(NR) emitter must still PRINT the columns; only the "
                    "owner-side binding is unknown. [UNVERIFIED] U7."),
     "independently_reconfirmed_by_verification_pass": False},
    {"defect_id": "AZ-D8", "form": FORM_CODE_120S, "location": "Schedule K-1 face question B",
     "walk_item": "cosmetic",
     "printed": "If the S Corporation made the the Pass-Through Election, ...",
     "correct": "'the the' is printed on the face",
     "resolution": "Cosmetic. Transcribe as printed.",
     "independently_reconfirmed_by_verification_pass": False},
]
AZ_PRINTED_DEFECT_COUNT = len(AZ_PRINTED_DEFECTS)
AZ_FACE_GOVERNS_OVER_INSTRUCTIONS = True
AZ_FACE_GOVERNS_NOTE = (
    "Arizona's TY2025 PTE package is a NOVEMBER-2025 FORM FACE wearing an AUGUST-2026 INSTRUCTION "
    "BOOK. Any divergence between the two resolves IN FAVOUR OF THE FACE, because the face is what "
    "is e-filed. ⚠ THIS IS A DIFFERENT QUESTION from a SUPPORTING form's routing list being wrong "
    "about a PARENT form (AZ-D3, AZ-D4, and Schedule ACA's U12): there the PARENT form's own "
    "instructions govern. ⚠ AND IT HAS ONE KNOWN EXCEPTION IN THE OTHER DIRECTION: Form 165 lines "
    "19 and 21 carry a zero floor that appears ONLY in the instructions and NOT on the face (W4) — "
    "the engine must supply it, because Form 120S prints exactly the same floor on ITS face at "
    "lines 46 and 48."
)


# ═══════════════════════════════════════════════════════════════════════════
# THE SBI HANDOFF — IT DOES NOT REACH THE ENTITY COMPUTATION; IT REACHES THE
# K-1 ROUTING ON **18** LINES; AND THERE IS ONE PLACE IT REACHES AND FINDS
# NOTHING
# ═══════════════════════════════════════════════════════════════════════════
AZ_SBI_REACHES_ENTITY_COMPUTATION = False
AZ_SBI_ENTITY_BOOK_HITS = 0
AZ_SBI_ENTITY_NEGATIVE = (
    "The TWO ENTITY INSTRUCTION BOOKS CONTAIN ZERO `SBI` REFERENCES ANYWHERE — including in their "
    "own K-1 line walkthroughs, which cover 165 lines 11-15 and 120S lines 8-12 / 21-25 with no SBI "
    "branch at all. Zero on the form faces too. The SBI routing lives on the K-1 FACES and in the "
    "SEPARATE OWNER-FACING K-1 INSTRUCTION PDFs. ⚠ [CORRECTED — verification pass §16.4 C3: the "
    "brief previously sourced this to the entity books' K-1 walkthroughs. That sourcing was FALSE "
    "and it UNDERSTATED the finding; the conclusion is unchanged and now rests on a stronger "
    "negative.] Structurally necessary: the SBI election is made by an INDIVIDUAL, on their own "
    "return, AFTER the K-1 has been issued. The entity does not know and does not need to know."
)
# ⚠⚠ THE VOCABULARY TRAP. A bare search for `small business` returns 14 hits in
# the Form 165 book and 12 in the Form 120S book — and EVERY ONE OF THE 26 is
# "**QUALIFIED** small business", the A.R.S. § 43-1022(21) Arizona Commerce
# Authority capital-gain subtraction. THAT IS A COMPLETELY DIFFERENT REGIME from
# the elective Arizona Small Business Income tax. The discriminating search terms
# are `SBI` and `43-1011.01`, both of which return ZERO in both entity books.
AZ_SBI_VOCABULARY_TRAP = (
    "All 26 'small business' hits in the two entity books are 'QUALIFIED small business' "
    "(§ 43-1022(21), the ACA-certified capital-gain subtraction) — a DIFFERENT REGIME from the "
    "elective Arizona Small Business Income tax. Discriminating terms: `SBI`, `43-1011.01`."
)
AZ_QUALIFIED_SMALL_BUSINESS_HITS = {FORM_CODE_165: 14, FORM_CODE_120S: 12}

# THE 18 SBI-BEARING K-1 ROUTING LINES.
# ⚠ [CORRECTED — verification pass §16.4 C1: the brief's PROSE said 17 in three
# places; its TABLE was always right. 4 + 4 + 1 + 4 + 1 + 4 = 18.]
# ⚠ COUNTING BASIS, STATED EXPLICITLY: lines whose OWN PRINTED ROUTING BLOCK
# names an `-SBI` form. The FOUR PTE-CREDIT lines (165 K-1 line 11, 165 K-1(NR)
# line 23, 120S K-1 line 8, 120S K-1(NR) line 21) are EXCLUDED, because they
# route to Form 355 and reach SBI only one hop further out via Form 301-SBI.
# COUNTING THEM TOO WOULD GIVE 22. ANY LOADER MUST PICK ONE BASIS AND HOLD IT.
AZ_SBI_ROUTING_LINES: dict[str, tuple[str, ...]] = {
    "AZ_165_SCHK1 Part 7": ("12", "13", "14", "15"),
    "AZ_165_SCHK1NR Part 8": ("24", "25", "26", "27"),
    "AZ_120S_SCHK1 Part 4": ("7",),
    "AZ_120S_SCHK1 Part 5": ("9", "10", "11", "12"),
    "AZ_120S_SCHK1NR Part 5": ("20",),
    "AZ_120S_SCHK1NR Part 6": ("22", "23", "24", "25"),
}
AZ_SBI_LINE_COUNT = 18
AZ_SBI_LINE_COUNT_INCLUDING_CREDIT_LINES = 22
AZ_SBI_COUNTING_BASIS = "lines whose own printed routing block names an -SBI form"
AZ_SBI_DOWNSTREAM_FORMS = ("Form 301-SBI", "Form 309-SBI", "Form 140-SBI", "Form 140PY-SBI",
                           "Form 140NR-SBI")

# ⚠⚠ WHERE SBI REACHES AND FINDS NOTHING: FORM 165 SCHEDULE K-1 **LINE 3**.
# Line 3 — the resident partner's share of the Arizona basis adjustment — carries
# NO SBI route. Its instruction lists exactly THREE owner situations (resident
# individual → Form 140 line 16/27; part-year → Form 140PY line 31/44; resident
# estate/trust → Form 141AZ Sch. B B3/B9) and STOPS, while lines 12-15 OF THE
# SAME DOCUMENT use a four-way route INCLUDING the SBI destinations.
# ⚠ THE REASON IS SHARPER THAN "AZDOR FORGOT": line 3 routes to Form 140 PAGE 1
# lines 16/27 (the MAIN FORM, TWO-WAY), whereas the SBI-bearing lines 12-15 route
# to Form 140 PAGE 5 line P (a ONE-WAY other-additions schedule). LINE 3 WAS
# NEVER AN INSTANCE OF THAT TEMPLATE.
# ⚠ WHY IT IS NOT A NITPICK: Arizona small business income is defined by
# reference to federal Schedules B, C, D, E, F and Form 4797 (Pub 712).
# Partnership income on federal Schedule E is squarely inside that definition, so
# a resident Arizona partner in an operating partnership is a PRIME SBI-election
# candidate — and precisely that taxpayer has no printed destination.
# **DO NOT GUESS.** It blocks the INDIVIDUAL wave's binding, not this one:
# Form 165 computes line 6 correctly either way and the K-1 prints line 3
# correctly either way.
AZ_165_SCHK1_LINE3_HAS_SBI_ROUTE = False
AZ_165_SCHK1_LINE3_ROUTES = (
    "Resident individuals: Form 140 page 1 line 16 (positive) / line 27 (negative). "
    "Part-year residents: Form 140PY line 31 (positive) / line 44 (negative), the portion allocable "
    "to partnership income taxable by Arizona. "
    "Resident estates or trusts: Form 141AZ Schedule B line B3 (positive) / line B9 (negative)."
)
AZ_165_SCHK1_LINE3_GAP_ID = "U6"


# ═══════════════════════════════════════════════════════════════════════════
# PENALTIES — Form 165 and Form 120S carry the same set
# ═══════════════════════════════════════════════════════════════════════════
AZ_PENALTIES: dict[str, dict] = {
    "information_return": {
        "rate": "$100 for each month or fraction of a month that the failure continues",
        "cap": 500,
        "applies_only_when_no_pte_election": True,
        "face_line": {FORM_CODE_165: "7 (repeated at 36)", FORM_CODE_120S: "32"},
        "note": ("⚠ APPLIES ONLY TO ENTITIES THAT DID NOT MAKE THE PTE ELECTION. Both books: "
                 "'Partnerships/S Corporations that made the PTE election, this is not an "
                 "information return.' Pub 713 asked directly: 'Does the Information Return Penalty "
                 "apply if a partnership or S Corporation made the PTE election...? NO.'")},
    "late_filing": {"rate": "4.5% (.045) of the amount of tax required to be shown on the return, "
                            "per month or fraction of a month", "cap_pct": "0.25"},
    "extension_underpayment": {
        "rate": "0.5% (.005) of the tax not paid, for each 30-day period or fraction",
        "cap_pct": "0.25",
        "trigger": "the electing entity must pay 90% of the tax liability by the ORIGINAL due date",
        "mutually_exclusive_with": "late_payment"},
    "late_payment": {"rate": "0.5% (.005) of the unpaid tax for each month or fraction",
                     "cap_pct": "0.10"},
    "estimated_underpayment": {"rate": "per Form 220/PTE Part C line 37",
                               "imports_to": {FORM_CODE_165: "line 35 (box 35A)",
                                              FORM_CODE_120S: "line 31 (box 31A)"}},
    "failure_to_pay_by_eft": {"rate": "5% of the payment not made by EFT",
                              "authority": "A.R.S. § 42-1125(O)", "threshold": 500},
}
AZ_COMBINED_PENALTY_CAP_PCT = "0.25"
AZ_COMBINED_PENALTY_NOTE = (
    "NOTE: If more than one of the penalties described in A (late filing), B (extension "
    "underpayment) or C (late payment) apply, THE MAXIMUM COMBINED PENALTY IS 25%."
)
AZ_VOLUNTARY_AMENDMENT_RELIEF = (
    "If the taxpayer voluntarily files an amended return and pays the additional tax due when "
    "filing, the department will NOT assess the late payment penalty. Exceptions: the taxpayer is "
    "under audit, or the amended return was filed on demand or request by the department. "
    "Authority: AZDOR ruling CTR 09-1."
)
AZ_AMENDED_DO_NOT_RECOMPUTE_EST_PENALTY = (
    "Amended returns: DO NOT recompute the estimated tax underpayment penalty. Enter the amount "
    "from line 31 of the original return, or the amount from an AZDOR correction notice."
)


# ═══════════════════════════════════════════════════════════════════════════
# DUE DATES, EXTENSIONS, E-FILE
# ═══════════════════════════════════════════════════════════════════════════
AZ_ORIGINAL_DUE_MONTH = 3            # 15th day of the 3rd month after year end
AZ_EXTENSION_MONTHS: dict[str, int] = {FORM_CODE_165: 6, FORM_CODE_120S: 6}
AZ_EXTENSION_MONTHS_CCORP = 7        # ⚠ Forms 120 / 120A / 99T / 99M get SEVEN
AZ_EXTENSION_FORM = "Arizona Form 120/165EXT"
AZ_FEDERAL_EXTENSION_ACCEPTED = True
AZ_EXTENSION_CHECKBOX: dict[str, str] = {FORM_CODE_165: "82E", FORM_CODE_120S: "82F"}
AZ_EXTENSION_90_PCT_RULE = (
    "The taxpayer is liable for the extension underpayment penalty if at least 90 percent of the "
    "tax liability disclosed by the return has not been paid by the ORIGINAL due date."
)
AZ_EXT_PAYMENT_LEG_LIMITED_TO_ELECTING_PARTNERSHIPS = True   # face: '165 (for partnerships that elected...)'
AZ_COMPOSITE_EXTENSION_FORM = "Arizona Form 204"             # NOT 120/165EXT
AZ_COMPOSITE_ESTIMATES_FORM = "Arizona Form 140ES"           # NOT 120/165ES
AZ_COMPOSITE_PAYMENT_CONVERSION_ALLOWED = False

AZ_EFILE_MANDATORY = True
AZ_EFILE_STATUTE = "A.R.S. § 43-323(F)"
AZ_EFILE_SIZE_LIMIT_MB = 246
AZ_K1_ELECTRONIC_CEILING = 66_054
AZ_EFILE_EXEMPTIONS: tuple[str, ...] = (
    "the entity cannot e-file its FEDERAL return",
    "the entity was granted a FEDERAL waiver from filing its federal return electronically",
    "the entity has a FEDERAL exemption from e-filing its federal return",
    "the entity has an Arizona electronic filing waiver (Form 292) or an Arizona exemption",
    "⚠ a 2026 SHORT-PERIOD return submitted on the 2025 form — SUBMIT PAPER, DO NOT E-FILE",
    "the entity has been directed to file a paper return by the IRS or by the department",
    "the return exceeds 246 MB (approximately 66,054 Schedules K-1 / K-1(NR))",
)
AZ_EFILE_IS_DERIVATIVE_OF_FEDERAL = True
AZ_EFILE_DERIVATIVE_NOTE = (
    "⚠ FOUR OF THE SEVEN EXEMPTIONS KEY OFF FEDERAL STATUS. The app cannot decide Arizona e-file "
    "eligibility without knowing the FEDERAL filing posture. This is a Gate-2 INGEST dependency for "
    "delvio-tax, not an RS spec item."
)
# ⚠ Optical-media K-1 submission is a PARTNERSHIP-ONLY path. Form 120S's book
# says S corporations filing a PAPER return must submit K-1s BY PAPER — no
# CD/DVD/flash alternative is offered. Do not port it.
AZ_OPTICAL_MEDIA_K1_PATH: dict[str, bool] = {FORM_CODE_165: True, FORM_CODE_120S: False}
AZ_EFILE_REJECTION_CONTACT = "azefile@azdor.gov"
AZ_EFILE_WAIVER_FORM = "Arizona Form 292"

# Software-developer gate — feeds EFILE_GATES.md, not a computation.
AZ_LOI_TY2025_DUE = "2025-11-28"        # PASSED
AZ_LOI_TY2026_PUBLISHED = False         # U16 — not published as of 2026-08-17
AZ_LOI_TY2026_EXPECTED = "~end of November 2026 — A PATTERN INFERENCE, NOT A PUBLISHED DATE (U16)"
AZ_LOI_REQUIRES_IRS_ATS_FIRST = True
AZ_LOI_SEPARATE_MODULE_BOXES = ("Partnership return", "S-corporation return")
AZ_LOI_NOTE = (
    "⚠ 'Partnership return' and 'S-corporation return' are SEPARATE REGISTRATIONS and the PTE wave "
    "needs BOTH boxes; the '(*) amended-later' concession appears ONLY on the individual and "
    "corporation rows, NOT on these two. The COR Credit Forms tab must also be completed — "
    "declaring the core return without the credit forms it references is an INCOMPLETE SUBMISSION "
    "and the LOI's consequences clause bites. Delvio is a NEW provider, so IRS MeF ATS acceptance "
    "is a BLOCKING PREDECESSOR. 'Business' is ONE EFIN/ETIN bucket covering partnership, S-corp, "
    "corporate and fiduciary."
)


# ═══════════════════════════════════════════════════════════════════════════
# COMPOSITE RETURNS — MUTUALLY EXCLUSIVE WITH THE PTE ELECTION, PER OWNER
# ═══════════════════════════════════════════════════════════════════════════
AZ_COMPOSITE_FORM = "Arizona Form 140NR"
AZ_COMPOSITE_MIN_PARTICIPANTS = 10
AZ_COMPOSITE_PARTICIPANTS_MUST_HAVE_OPTED_OUT = True
AZ_COMPOSITE_RULING = "AZDOR ruling ITR 16-2"
AZ_COMPOSITE_NOTE = (
    "AZDOR accepts a composite Form 140NR for qualifying nonresident individual owners THAT OPTED "
    "OUT of the PTE election. 'A partnership making the PTE election CANNOT file a composite return "
    "on behalf of its nonresident partners that did NOT opt out.' Minimum TEN participating "
    "members. For the PTE wave the only deliverables are the page-1 checkbox (165 question L / 120S "
    "question F) and those two validations — the composite return itself is an INDIVIDUAL-module "
    "artifact."
)


# ═══════════════════════════════════════════════════════════════════════════
# SUPPORTING FORMS — SIX THAT THE NAIVE COUNT MISSES, PLUS FOUR K-1 VARIANTS
# ═══════════════════════════════════════════════════════════════════════════
AZ_SUPPORTING_FORMS: dict[str, dict] = {
    "AZ_120_165EXT": {"title": "Application for Automatic Extension of Time to File Corporation, "
                               "Partnership, and Exempt Organization Returns",
                      "ador": "ADOR 10340 (25)", "v1": "IN — thin",
                      "note": "⚠ SEVEN months for C corps, SIX for 120S and 165. Printed on the face."},
    "AZ_120_165ES": {"title": "Corporate and Pass-Through Entity Estimated Tax Payment (booklet)",
                     "ador": "⚠ headed '2024 CORPORATE INCOME TAX HIGHLIGHTS', /ModDate 2024-11-19",
                     "v1": "vouchers only",
                     "note": "⚠ CARRIES REPEALED LAW on election timeliness. Use for VOUCHERS ONLY (U10)."},
    "AZ_120_PTE_W": {"title": "Estimated Tax Worksheet for Corporations & Pass-Through Entities",
                     "ador": "⚠ ADOR 10551 (24) — a genuinely STALE (24) stamp on the 2025-row file",
                     "v1": "IN — thin (lines 1, 2a-2e, 3, 4 only)",
                     "note": ("⚠ LINE 9 CARRIES TWO RATES IN ONE LABEL: 4.9% for corporations with "
                              "the parenthetical '(PTE's use 2.5% as tax rate.)'. A single-rate "
                              "transcription is wrong for one population. ⚠ Schedule A Part 1 "
                              "ANNUALIZED method IS available to PTEs (RED-DEFER for v1); Part 2 "
                              "ADJUSTED SEASONAL is NOT AVAILABLE to PTEs at all.")},
    "AZ_220_PTE": {"title": "Underpayment of Estimated Tax by Corporations & Pass-Through Entities",
                   "ador": "ADOR 10342 (25)", "v1": "IN — thin, DO NOT AUTO-FILE",
                   "note": ("The form itself says 'In most cases, the taxpayer DOES NOT HAVE TO FILE "
                            "Form 220/PTE ... The department will compute any penalty due and bill "
                            "the taxpayer.' ⚠ Part C line 17 substitutes months by form type: "
                            "'Forms 120S: Use 3rd month instead of 4th month. PTE's: Use 3rd month "
                            "instead of 4th month. Form 99T: Use 5th month.' Two printed defects "
                            "(AZ-D3, AZ-D4).")},
    "AZ_120_165V": {"title": "Arizona Corporate or Partnership Income Tax Payment Voucher",
                    "ador": "ADOR 11365 (25)", "v1": "IN — thin",
                    "note": ("⚠ SIX checkboxes, FOUR of them PTE-election-state variants of two "
                             "forms. A NON-ELECTING partnership uses this voucher only to pay the "
                             "INFORMATION RETURN PENALTY. E-filed returns paying by cheque only.")},
    "AZ_292": {"title": "Electronic Filing and Payment Waiver Application", "ador": "not pulled (U15)",
               "v1": "RED-DEFER",
               "note": "Grounds: no computer / no internet access / any other circumstance the "
                       "director considers worthy. Annual; renewable for one subsequent year."},
    "AZ_SCH_MSP": {"title": "Multistate Service Provider Election and Computation",
                   "ador": "ADOR 11220 (25)", "v1": "IN — full",
                   "note": "⚠ A FIVE-YEAR BINDING ELECTION (§ 43-1147(C)) — the ONLY stateful "
                           "multi-year attribute on these returns."},
    "AZ_SCH_ACA": {"title": "Air Carrier Apportionment", "ador": "ADOR 10535 (25)", "v1": "IN — full",
                   "note": "line 3 = line 1 / line 2, six decimals. ⚠ Its own routing list omits the "
                           "Part 2 PTE lines; the parent forms close the loop (U12)."},
    "AZ_165_SCHK1": {"title": "Resident and Part-Year Resident Partner's Share of Adjustment to "
                              "Partnership Income", "ador": "ADOR 10344 (25)", "v1": "IN",
                     "note": "Parts 1 and 7 COMPUTE; Parts 2-6 are information rows."},
    "AZ_165_SCHK1NR": {"title": "Arizona Nonresident and Out-of-State Partner's Share of Income and "
                                "Deductions", "ador": "ADOR 10345 (25)", "v1": "IN",
                       "note": "⚠ ALL corporate partners and partners that are partnerships MUST use "
                               "this schedule, not the resident K-1."},
    "AZ_120S_SCHK1": {"title": "Resident and Part-Year Resident Shareholder's Information Schedule",
                      "ador": "ADOR 11191 (25)", "v1": "IN",
                      "note": "⚠ NO income-adjustment part exists — §5.3 seen from the owner side."},
    "AZ_120S_SCHK1NR": {"title": "Nonresident Shareholder's Share of Income and Deductions",
                        "ador": "ADOR 10338 (25)", "v1": "IN",
                        "note": "⚠ NO guaranteed-payments line, so every line from 10 on is OFFSET BY "
                                "ONE relative to the 165 K-1(NR). A shared line map WILL be off by one."},
}
AZ_SUPPORTING_FORM_COUNT = len(AZ_SUPPORTING_FORMS)

# ⚠ A PART-YEAR OWNER RECEIVES **TWO** SCHEDULES, NOT ONE. Pub 713 footnote 2:
# complete a Schedule K-1 for the resident period AND a Schedule K-1(NR) for the
# nonresident period. A per-owner document multiplier the app must handle.
AZ_PART_YEAR_OWNER_GETS_TWO_SCHEDULES = True
AZ_K1_ROUTING_RULE = (
    "Split by RESIDENCY AND ENTITY TYPE, not by form. Form 165 Schedule K-1 face: 'Corporate "
    "partners and partners that are partnerships must use Form 165 Schedule K-1(NR).' Form 165 "
    "Schedule K-1(NR) face: 'All corporate partners and partners that are partnerships must use "
    "this schedule.'"
)


# ═══════════════════════════════════════════════════════════════════════════
# RED-DEFERS — EVERY ONE CARRIES ITS OWN DIAGNOSTIC. NO SILENT GAP, AND NOTHING
# SILENTLY INCLUDED EITHER.
# ═══════════════════════════════════════════════════════════════════════════
AZ_RED_DEFERS: tuple[str, ...] = (
    "D_AZ_RD_165PA_FAMILY",
    "D_AZ_RD_PTEW_ANNUALIZED",
    "D_AZ_RD_220PTE_SCHEDULE_A",
    "D_AZ_RD_COMPOSITE_140NR",
    "D_AZ_RD_ALT_APPORTIONMENT",
    "D_AZ_RD_OPTICAL_MEDIA_K1",
    "D_AZ_RD_SHORT_PERIOD_PAPER",
    "D_AZ_RD_FORM_292_WAIVER",
    "D_AZ_RD_MARIJUANA_99M",
    "D_AZ_RD_1021_15_ENTITY_ADDBACK",
    "D_AZ_RD_CORP_PARTNER_RECOMPUTE",
    "D_AZ_RD_B1_TY2013_TIER",
)
AZ_RED_DEFER_COUNT = len(AZ_RED_DEFERS)


# ═══════════════════════════════════════════════════════════════════════════
# THE OPEN REGISTER — 21 [UNVERIFIED] ITEMS. NONE WAS CLOSED BY THE
# VERIFICATION PASS; THREE WERE ADDED (U19, U20, U21).
# ⚠ EVERY ONE IS ENCODED — as a diagnostic, a note, or both. NO SILENT GAPS.
# ═══════════════════════════════════════════════════════════════════════════
AZ_UNVERIFIED: dict[str, dict] = {
    "U1": {"risk": "orange", "topic": "ITP 16-2 unpulled; Form 165 line B1 TY2013 tier undefined",
           "encoded_as": "D_AZ_RD_B1_TY2013_TIER + az_165_b1_tier() returns method 'ITP_16_2'"},
    "U2": {"risk": "orange", "topic": "corporate partner re-computation on the elect-out basis",
           "encoded_as": "D_AZ165_A4_CORP_PARTNER_BASIS (ruled by D-12 A4; the FACT stays open)"},
    "U3": {"risk": "red", "topic": "AZDOR's provision-by-provision OBBBA retroactivity mapping",
           "encoded_as": "D_AZ_U3_OBBBA_MAP_UNPUBLISHED (D-10 governs meanwhile)"},
    "U4": {"risk": "yellow", "topic": "Pub 713 self-contradiction on credits offsetting PTE tax",
           "encoded_as": "D_AZ120S_U4_CREDIT_ORDERING (the FORM is unambiguous and governs)"},
    "U5": {"risk": "orange", "topic": "§ 43-1021(15) entity-level add-back has no line",
           "encoded_as": "D_AZ_RD_1021_15_ENTITY_ADDBACK (ruled by D-12 A3)"},
    "U6": {"risk": "yellow", "topic": "Form 165 Sch. K-1 line 3 has no SBI destination",
           "encoded_as": "D_AZ165_U6_K1_LINE3_NO_SBI"},
    "U7": {"risk": "yellow", "topic": "165 Sch. K-1(NR) lines 10 and 14 have no printed destination",
           "encoded_as": "D_AZ165_U7_K1NR_NO_DESTINATION + AZ_PRINTED_DEFECTS AZ-D7"},
    "U8": {"risk": "yellow", "topic": "140PY/140NR page references are mutually inconsistent",
           "encoded_as": "D_AZ_U8_OWNER_PAGE_REFS + AZ_PRINTED_DEFECTS AZ-D6 (bind on the LETTER)"},
    "U9": {"risk": "orange", "topic": "K-1 PTE credit keyed to tax owed or tax paid",
           "encoded_as": "D_AZ_U9_PTE_CREDIT_PAID_VS_OWED"},
    "U10": {"risk": "yellow", "topic": "which vintage of Form 120/PTE-W and Booklet 120/165ES to surface",
            "encoded_as": "D_AZ_U10_ES_VINTAGE"},
    "U11": {"risk": "yellow", "topic": "Form 220/PTE line 5 cites Form 165 line 23, not a tax line",
            "encoded_as": "D_AZ_U11_220PTE_LINE5 + AZ_PRINTED_DEFECTS AZ-D3"},
    "U12": {"risk": "yellow", "topic": "Schedule ACA's routing list omits the Part 2 PTE lines",
            "encoded_as": "AZ_ACA_ROUTING_LIST_OMITS_PTE_LINES + the ACA rule notes (parent governs)"},
    "U13": {"risk": "yellow", "topic": "the three 165PA companion schedules were never read",
            "encoded_as": "D_AZ_RD_165PA_FAMILY (low priority while 165PA is RED-DEFERRED)"},
    "U14": {"risk": "red", "topic": "Form 165PA line 13's 4.5% vs the statute's 2.5%",
            "encoded_as": "D_AZ_RD_165PA_FAMILY + az_165pa_rate() raises (D-12 A2)"},
    "U15": {"risk": "yellow", "topic": "Form 292 was not downloaded",
            "encoded_as": "D_AZ_RD_FORM_292_WAIVER"},
    "U16": {"risk": "orange", "topic": "the TY2026 Arizona MeF LOI is unpublished; its date is inferred",
            "encoded_as": "D_AZ_U16_LOI_TY2026 (feeds EFILE_GATES.md, not a computation)"},
    "U17": {"risk": "yellow", "topic": "twelve referenced AZDOR rulings/procedures were not pulled",
            "encoded_as": "D_AZ_U17_RULINGS_UNPULLED (ITP 16-2 is the only one gating a mainstream line)"},
    "U18": {"risk": "orange", "topic": "do the H.B. 4168 § 43-1022 MCTCP subtractions reach the 165 PTE base",
            "encoded_as": "D_AZ165_U18_MCTCP_BY_REFERENCE"},
    "U19": {"risk": "red", "topic": "WHICH taxable income measures the $150,000 threshold",
            "encoded_as": ("D_AZ_U19_150K_BASIS + AZ_EST_MEASUREMENT_BASIS, resolving via "
                           "AZ_EST_MEASUREMENT_BASIS_RESOLVES_TO and az_est_measurement_figure() "
                           "(ruled by D-12 A1, REFINED same session; STILL OPEN AS A FACT)")},
    "U20": {"risk": "yellow", "topic": "Form 220/PTE line 37's routing list is wrong and omits Form 165",
            "encoded_as": "D_AZ_U20_220PTE_LINE37 + AZ_PRINTED_DEFECTS AZ-D4"},
    "U21": {"risk": "yellow", "topic": "the A.R.S. § 43-1011(A)(9) pinpoint is unsupported (404 / superseded)",
            "encoded_as": "D_AZ_U21_43_1011_CITE (the RATE is safe; only the provenance changed)"},
}
AZ_UNVERIFIED_COUNT = len(AZ_UNVERIFIED)
AZ_UNVERIFIED_BLOCKING = tuple(k for k, v in AZ_UNVERIFIED.items() if v["risk"] == "red")

AZ_RULINGS_UNPULLED: tuple[str, ...] = (
    "ITP 16-2", "ITR 06-1", "ITP 12-1", "ITR 16-2", "CTR 09-1", "CTR 01-2", "CTR 02-2", "CTR 07-1",
    "PTR 97-1 / CTR 97-1", "PTR 97-2 / CTR 97-2", "Pub 720", "Pub 712",
)


# ═══════════════════════════════════════════════════════════════════════════
# FEDERAL HANDOFF POINTS — AND THE FEDERAL FIGURES THAT DELIBERATELY DO NOT FLOW
# ═══════════════════════════════════════════════════════════════════════════
AZ_FEDERAL_HANDOFF: dict[str, dict[str, str]] = {
    FORM_CODE_165: {
        "1": ("federal Form 1065 Schedule K — ordinary business income (loss) PLUS net rental real "
              "estate income (loss) PLUS other net rental income (loss). ⚠ THREE components summed, "
              "not Schedule K line 1 alone"),
        "A1": "total depreciation deducted on the federal return — the entire § 167(a) allowance",
        "A2": ("federal tax-exempt interest LESS Arizona-exempt obligations LESS related carrying "
               "costs. ⚠ A NET figure, not gross"),
        "B3": ("U.S. government obligation interest included on Form 1065 Schedule K. ⚠ GNMA and "
               "FNMA are NOT U.S. government obligations for this purpose (ITR 06-1)"),
        "9": "federal Schedule K separately-stated items mapped to A.R.S. § 43-1412 ¶1-16",
        "Sch C C1": "federal fixed-asset detail at ORIGINAL COST, not net book value",
        "Sch D (e)": "partner TIN — ⚠ for an IRA partner, the CUSTODIAN'S TIN, not the beneficiary's",
    },
    FORM_CODE_120S: {
        "1": ("federal Form 1120-S Schedule K — 'the net total of the pro rata share items of "
              "nonseparately computed income (loss) and separately stated income (loss) and "
              "deductions'. ⚠ ONE aggregate number, NO Arizona modifications"),
        "2": "federal excess net passive income subject to federal tax (federal 1120-S worksheet)",
        "3": "federal capital gains / built-in gains subject to federal tax (same worksheet)",
        "Sch B (h)": "⚠ the shareholder's pro rata share of LINE 1, not of an adjusted figure",
    },
}
AZ_FEDERAL_FIGURES_THAT_DO_NOT_FLOW: tuple[str, ...] = (
    "no federal taxable income line — neither return starts from one",
    "no federal depreciation adjustment on Form 120S at all",
    "no § 168(n) QPP figure on either form for TY2025",
    "no federal § 179 dollar limit stated on either form",
    "no federal PTE-tax deduction add-back at the entity level (the statute wants one; no line exists)",
    "federal Schedules K-2 and K-3 — EXPRESSLY not to be submitted",
    "the federal § 743(b) basis-adjustment statement — EXPRESSLY not to be submitted",
    "federal Form 1065 Schedule L / M-1 / M-2 — nothing on either Arizona return requests balance "
    "sheet or book-tax reconciliation data, EXCEPT the apportionment property factor, which wants "
    "ORIGINAL COST rather than the Schedule L figures",
)
AZ_QSUB_RULE = (
    "Qualified subchapter S subsidiaries are NOT treated as entities separate from the parent and "
    "are included on a SINGLE Arizona Form 120S filed by the parent S corporation."
)
AZ_SMLLC_TWO_ROLES = (
    "⚠ A single-member LLC disregarded federally is OUT of both entity returns as a FILER "
    "(PTR 97-2 / CTR 97-2 — it is a branch or division of its owner) but CAN be a PTE-PARTICIPATING "
    "OWNER (§8.3, both books' footnotes, Pub 713). Two different roles, opposite answers. Do not "
    "collapse them."
)
AZ_165_DEMINIMIS_CARVE_OUT = (
    "'A partnership that has no Arizona income, deductions or credits for the taxable year is not "
    "required to file a partnership return for that year.' Stated TWICE in the Form 165 book."
)
AZ_120S_HAS_DEMINIMIS_CARVE_OUT = False   # ⚠ the S-corp book has NONE. Do not port it.


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY TOPICS
# ⚠ topic_name is a CharField(255). Wave-3 harnesses caught FOUR values over the
# cap that were INVISIBLE IN SQLITE and would have been Postgres DataErrors in
# prod — and ARIZONA HAS FORM HERE: one of its citations ran 390 characters and
# blew the cap during the Tier-1 conformity seed. These are deliberately short;
# validate_az.py measures them against the LIVE model _meta, never a hardcoded
# number.
# ═══════════════════════════════════════════════════════════════════════════
AUTHORITY_TOPICS: list[tuple[str, str]] = [
    ("az_pte_entity_returns",
     "Arizona Forms 165 and 120S: two returns that are NOT parallel — a full modification stack on "
     "165, none at all on 120S."),
    ("az_pte_elective_tax",
     "Arizona's elective PTE tax at A.R.S. § 43-1014 — computed IN Form 165 Part 2 and Form 120S "
     "Part 2, with no return of its own."),
    ("az_165_depreciation",
     "Form 165 line A1/B1: the five-vintage-tier Arizona depreciation recomputation, on the "
     "INDIVIDUAL full-§168(k) basis."),
    ("az_conformity_compound",
     "Arizona's TY2025 conformity: IRC as of 1/1/2025 PLUS retroactively-effective OBBBA "
     "provisions — neither 1/1/2025 nor 1/1/2026 alone."),
    ("az_apportionment",
     "Form 165 Schedule C / Form 120S Schedule A, plus Schedule MSP and Schedule ACA: a dynamic "
     "4/3/2/none divisor and a double-weighted sales factor."),
    ("az_owner_schedules_sbi",
     "The four Arizona owner schedules and the 18 K-1 lines carrying a Small Business Income "
     "destination alongside the non-SBI one."),
    ("az_pte_estimated_payments",
     "A.R.S. § 43-581(C): the $150,000 test, its four printed measurement bases, and the PTE "
     "installment calendar that ends in the 1st month after year end."),
]

# ⚠ ALREADY SEEDED IN RS — REUSE, NEVER RE-CREATE (campaign D-10). Arizona's
# JurisdictionConformitySource row is live with conformity_type = 'static', so
# these anchors resolve immediately in prod. They WILL warn on a throwaway SQLite
# harness DB unless the Tier-1 batch is seeded first, which validate_az.py does.
EXISTING_SOURCES_TO_REFERENCE: list[str] = [
    "AZ_HB4168_2026_CH140",   # the controlling TY2025 conformity authority (§ 43-105(B))
    "AZ_ARS_43_1022",         # individuals CONFORM to § 168(k) — the rule Form 165 line B1 applies
    "AZ_ARS_43_1122",         # corporations DECOUPLE — the rule Form 165 does NOT apply, and A4
]

AUTHORITY_SOURCES: list[dict] = [
    # ------------------------------------------------------------ form faces
    {
        "source_code": "AZ_2025_FORM_165",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "AZ",
        "tax_year_start": 2025, "tax_year_end": 2025, "entity_type_code": "1065",
        "title": ("Arizona Form 165 (2025), Arizona Partnership Income Tax Return — the FACE. Part 1 "
                  "lines 1-7 with Schedules A and B; Part 2 lines 8-40 (the elective PTE tax); "
                  "Schedule C apportionment; Schedules D-G; the page-6 worksheets"),
        "citation": "Arizona Form 165 (2025), ADOR 10343 (25), 6 pages, /ModDate 2025-11-13",
        "issuer": "Arizona Department of Revenue",
        "official_url": ("https://azdor.gov/sites/default/files/document/"
                         "FORMS_PARTNERSHIP_2025_165_f.pdf"),
        "current_status": "active", "is_substantive_authority": True, "is_filing_authority": True,
        "trust_score": 9.9, "topics": ["az_pte_entity_returns", "az_pte_elective_tax"],
        "notes": ("Read POSITIONALLY, never from flat text — flat extraction scrambles the "
                  "multi-column face and interleaves the page-4 schedule captions with the wrong "
                  "grids (Schedule D caption y=60.3 above row D1 y=165.7, with E1 down at y=616.4). "
                  "DO NOT REPORT A CAPTION SWAP AS A FORM DEFECT. 48 line numbers and verbatim "
                  "labels were sampled positionally across all 15 Arizona forms with a 0.0% error "
                  "rate. ⚠ THE FACE PREDATES H.B. 4168 BY 7 MONTHS while the instruction book "
                  "post-dates it by 2 — and the face governs, because the face is what is e-filed."),
        "excerpts": [
            {"excerpt_label": "Question A — the election IS an act of filing this return",
             "location_reference": "Form 165 page 1, question A",
             "excerpt_text": ("Did the partnership make the Pass-Through Entity (PTE) election to pay "
                              "tax on its flow-through income at the entity level? (See "
                              "instructions).......... Yes  No"),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("THE MASTER BRANCH, and one of the four proofs that Arizona needs no "
                              "third PTE form. ⚠ But Part 2 is NOT gated on question A alone — see "
                              "the Part 2 header.")},
            {"excerpt_label": "Part 2 header — the gate is Q.A = Yes OR estimates paid",
             "location_reference": "Form 165 page 2, Part 2 header",
             "excerpt_text": ("Part 2 - Calculation of Partnership Tax to be Paid at the Entity Level "
                              "- Complete only if the Partnership answered \"Yes\" to Question A on "
                              "page 1, or estimated payments were made and the partnership is not "
                              "claiming the PTE election. See instructions."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ A loader branching on Question A alone SUPPRESSES PART 2 FOR EXACTLY "
                              "THE POPULATION THAT MOST NEEDS IT. TY2025 is the year for it: the "
                              "federal SALT cap moved from $10,000 to $40,000 and Pub 713 scripts a "
                              "'$0 return' refund path for entities that prepaid then declined.")},
            {"excerpt_label": "Lines 20 and 24 — the 2.5% rate, PRE-PRINTED ON THE FACE",
             "location_reference": "Form 165 page 2, Part 2 lines 20 and 24",
             "excerpt_text": ("20 Multiply the amount on line 19 by the PTE tax rate, 2.5% (0.0250) "
                              "Enter the result. ... 24 Multiply the amount on line 23 by the PTE tax "
                              "rate, 2.5% (0.0250). Enter the result."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("The rate is NOT a lookup — it is printed. Pin the constant to the "
                              "FACE, not to A.R.S. § 43-1011, which cannot be read off azleg (U21).")},
            {"excerpt_label": "Lines 5 and 6 — TWO DIFFERENT OUTPUTS OF ONE BLOCK",
             "location_reference": "Form 165 page 1, Part 1 lines 5 and 6",
             "excerpt_text": ("5 Partnership income adjusted to Arizona basis: Subtract line 4 from "
                              "line 3. Enter the difference. ... 6 Net adjustment of partnership "
                              "income from federal to Arizona basis: Subtract line 1 from line 5. "
                              "Enter the difference."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ LINE 5 feeds the PTE base (line 8) and Schedule D column (h). "
                              "LINE 6 — the NET ADJUSTMENT — is the ONLY number that leaves Part 1 "
                              "for the owners, feeding 165 Sch. K-1 line 1 and Sch. K-1(NR) line 15. "
                              "CROSSING THESE IS THE MOST LIKELY SINGLE TRANSCRIPTION ERROR ON THIS "
                              "FORM.")},
            {"excerpt_label": "Schedule E cross-foot and the Part 2 cross-foot — BOTH on the face",
             "location_reference": "Form 165 page 4 line E8; page 2 note under line 18",
             "excerpt_text": ("E8 Total partner count and total partnership ownership share. Add "
                              "lines E6 and E7 in columns (b) and (c). Enter the totals. (Column (c) "
                              "should equal 1.000000.) ... NOTE: The total of lines 12, 14, 16 and 18 "
                              "must equal the amount reported on line 10."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("Arizona gives TWO INDEPENDENT PROOF OBLIGATIONS on the same "
                              "allocation, and both are stated ON THE FACE rather than merely in the "
                              "instructions. Carry both as flow assertions.")},
            {"excerpt_label": "Line 39 — THE STALE YEAR (defect AZ-D1)",
             "location_reference": "Form 165 page 3, line 39",
             "excerpt_text": "39 Amount of line 38 to be applied to 2025 estimated tax",
             "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ The INSTRUCTION for the same line says 2026, and Form 120S line 35 "
                              "correctly reads 2026. Applying a TY2025 overpayment to 2025 estimated "
                              "tax is meaningless. Transcribe as printed; compute 2026. W5, "
                              "independently re-confirmed by the verification pass.")},
        ],
    },
    {
        "source_code": "AZ_2025_FORM_165_INSTR",
        "source_type": "state_instruction", "source_rank": "implementation_official",
        "jurisdiction_code": "AZ", "tax_year_start": 2025, "tax_year_end": 2025,
        "entity_type_code": "1065",
        "title": ("2025 Arizona Form 165 instructions — every line instruction, the PTE-base note, "
                  "the five-tier line B1 depreciation recomputation, penalties, e-file and composite "
                  "rules. ⚠ RE-ISSUED 2026-08-11, AFTER H.B. 4168"),
        "citation": "2025 Arizona Form 165 instructions, 27 pages, /ModDate 2026-08-11 (re-issued)",
        "issuer": "Arizona Department of Revenue",
        "official_url": ("https://azdor.gov/sites/default/files/document/"
                         "FORMS_PARTNERSHIP_2025_165_i.pdf"),
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.5,
        "topics": ["az_pte_entity_returns", "az_165_depreciation", "az_pte_estimated_payments"],
        "notes": ("⚠ RE-ISSUED TWO MONTHS AFTER ENACTMENT AND SUBSTANTIVELY UNCHANGED — no § 168(n) "
                  "line, no H.B. 4168 / OBBBA / conformity discussion (searched for '4168', "
                  "'119-21', 'H.R. 1', 'One Big Beautiful', 'conformity'), no change to the line B1 "
                  "tiers, no change to the 2.5% rate, and NO MCTCP subtractions added to Schedule B "
                  "or the page-6 B5 worksheet. THAT ABSENCE IS THE FINDING: the entity-level PTE "
                  "package is conformity-neutral for TY2025."),
        "excerpts": [
            {"excerpt_label": "Line B1 — the FIVE-tier Arizona depreciation recomputation",
             "location_reference": "Form 165 instructions, Line B1 - Recalculated Arizona Depreciation",
             "excerpt_text": ("For assets placed in service in taxable years beginning before December "
                              "31, 2012, enter the total amount of depreciation allowable pursuant to "
                              "IRC § 167(a) ... calculated as if the taxpayer had elected not to claim "
                              "bonus depreciation ... after December 31, 2012 through December 31, "
                              "2013, the amount of the subtraction ... depends on the method used ... "
                              "See the department's procedure, ITP 16-2 ... after December 31, 2013 "
                              "through December 31, 2015 ... as if the bonus depreciation is 10% ... "
                              "after December 31, 2015 through December 31, 2016 ... as if the bonus "
                              "depreciation is 55% ... after December 31, 2016 ... as if the bonus "
                              "depreciation had been the full amount of federal bonus depreciation "
                              "pursuant to IRC § 168(k). Add all amounts together and enter the total "
                              "on line B1."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("FIVE tiers (the brief's 'four' was corrected on verification), keyed "
                              "on PLACED IN SERVICE — stated four times in four sentences, so no "
                              "date-keying ruling is needed here (contrast D-10 rulings 3 and 4 for "
                              "TN and TX). ⚠ The TY2013 tier is UNDEFINED without ITP 16-2, which has "
                              "never been pulled (U1): DIRECT-ENTRY with a diagnostic. ⚠ The final "
                              "tier is word-for-word the INDIVIDUAL rule at § 43-1022(17)(e), and the "
                              "authority pointer is the INDIVIDUALS' procedure — cited three times on "
                              "this one line.")},
            {"excerpt_label": "The PTE-base note — built on the INDIVIDUAL modification sections",
             "location_reference": "Form 165 instructions, line 9",
             "excerpt_text": ("NOTE: 2023 legislation, SB 1734 mandated a change in the starting point "
                              "to compute the Arizona taxable income for partnerships making the PTE "
                              "election. For taxable years beginning from and after December 31, 2022, "
                              "the starting point ... is the partnership's ordinary income and rental "
                              "income including any Arizona additions found in A.R.S. § 43-1021 less "
                              "any Arizona subtractions found in A.R.S. § 43-1022, plus, the items "
                              "that require separate computation under A.R.S. § 43-1412, paragraphs 1 "
                              "through 16."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("TWO flow facts live here. (1) The PTE base is built on §§ 43-1021 / "
                              "43-1022 — THE INDIVIDUAL SECTIONS — which is the statutory root of the "
                              "individual-bonus finding. (2) The § 43-1412 ¶1-16 items are added back "
                              "at line 9 because § 43-1401(1) EXCLUDED them from a partnership's "
                              "Arizona gross income in the first place. Line 8 + line 9 is an exact "
                              "statutory reconstruction of § 43-1014(B)(1)(a)(ii). ⚠ The open "
                              "§ 43-1022 reference is also the U18 exposure: H.B. 4168's new MCTCP "
                              "paragraphs are TY2025-effective and AZDOR added no line for them.")},
            {"excerpt_label": "Lines 19 and 21 — a zero floor stated ONLY in the instructions",
             "location_reference": "Form 165 instructions, lines 19 and 21",
             "excerpt_text": ("Add line 12 and line 16A. Enter the total. If the total is less than "
                              "zero, \"0\", enter \"0\"."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ THE FACE CARRIES NO SUCH NOTE, while Form 120S prints exactly the "
                              "same floor ON ITS FACE at lines 46 and 48. A real face-vs-instruction "
                              "divergence and a diagnostic the engine must supply (W4). This is the "
                              "one place the 'face governs' convention runs the other way — the "
                              "instruction ADDS a rule the face omits rather than contradicting it.")},
            {"excerpt_label": "The factor-exclusion rule and the DYNAMIC divisor",
             "location_reference": "Form 165 instructions, Schedule C",
             "excerpt_text": ("NOTE: Partnerships must exclude a factor if both the numerator and the "
                              "denominator of a factor are zero. Do not exclude a factor if the "
                              "numerator of the factor is zero and the denominator of that factor is "
                              "greater than zero. See A.A.C. R15-2D-901(B). If either the property or "
                              "the payroll factor is excluded, determine the average ratio by "
                              "dividing the total ratio by three. If the sales factor is excluded, "
                              "determine the average ratio by dividing the total ratio by two. If two "
                              "of the factors are excluded, the remaining factor, without respect to "
                              "any weighting, is the apportionment ratio."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ THE DIVISOR IS DYNAMIC: 4, 3, 2, OR NONE — and when SALES is the "
                              "excluded factor the divisor drops to TWO even though sales is "
                              "DOUBLE-WEIGHTED. The weighting and the divisor are NOT tied together. "
                              "A zero numerator over a positive denominator is a LIVE ZERO FACTOR, "
                              "not an excluded one.")},
            {"excerpt_label": "Line 7 — the information-return penalty and its PTE carve-out",
             "location_reference": "Form 165 instructions, line 7",
             "excerpt_text": ("Partnerships that did not make the PTE election, this is an information "
                              "return. If it is incomplete or it is filed late (including extension) "
                              "it is subject to a penalty of $100 per month or fraction of a month "
                              "during which the failure continues, up to a maximum of $500. ... "
                              "Partnerships that made the PTE election, this is not an information "
                              "return. Continue to Part 2, line 8."),
             "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("The penalty and the PTE election are MUTUALLY EXCLUSIVE. Pub 713 was "
                              "asked directly and answered 'No'.")},
        ],
    },
    {
        "source_code": "AZ_2025_FORM_120S",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "AZ",
        "tax_year_start": 2025, "tax_year_end": 2025, "entity_type_code": "1120S",
        "title": ("Arizona Form 120S (2025), Arizona S Corporation Income Tax Return — the FACE. "
                  "Part 1 lines 1-36 (corporate-level tax and payments); Part 2 lines 37-52 (the "
                  "elective PTE tax); Schedules A-E"),
        "citation": "Arizona Form 120S (2025), ADOR 10337 (25), 5 pages, /ModDate 2025-11-12",
        "issuer": "Arizona Department of Revenue",
        "official_url": ("https://azdor.gov/sites/default/files/document/"
                         "FORMS_CORPORATE_2025_120S_f.pdf"),
        "current_status": "active", "is_substantive_authority": True, "is_filing_authority": True,
        "trust_score": 9.9, "topics": ["az_pte_entity_returns", "az_pte_elective_tax"],
        "notes": ("⚠ THE DECISIVE NEGATIVE EVIDENCE IS ON THIS FACE: there is NO additions schedule, "
                  "NO subtractions schedule and NO 'Arizona basis' line anywhere. Its lettered "
                  "Schedule A is the APPORTIONMENT FORMULA. Line 37 reads 'Enter the amount from "
                  "line 1' and line 1 reads 'TOTAL DISTRIBUTIVE INCOME (LOSS) from federal Form "
                  "1120-S, Schedule K'. Read positionally (Schedule B caption y=59.8 above row B1 "
                  "y=159.9)."),
        "excerpts": [
            {"excerpt_label": "Line 37 = line 1 — the PTE base, UNADJUSTED",
             "location_reference": "Form 120S page 1 line 1; page 2 Part 2 line 37",
             "excerpt_text": ("1 TOTAL DISTRIBUTIVE INCOME (LOSS) from federal Form 1120-S, Schedule "
                              "K ... 37 Enter the amount from line 1"),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠⚠ NOTHING IN BETWEEN. Arizona applies NO modifications to an S "
                              "corporation's PTE base. Contrast Form 165, whose base is line 5 (after "
                              "a full Schedule A/B stack) PLUS line 9. THE TWO RETURNS ARE NOT "
                              "PARALLEL and there is NO SHARED ARIZONA MODIFICATION ENGINE (D-12).")},
            {"excerpt_label": "Lines 46 and 48 — the zero floor, PRINTED ON THE FACE",
             "location_reference": "Form 120S page 2, Part 2 lines 46 and 48",
             "excerpt_text": ("46 Add line 39 and line 43A. Enter the total. If less than zero, enter "
                              "\"0\" ... 48 Add line 41 and line 43B. Enter the total. If less than "
                              "zero, enter \"0\""),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("Same rule as Form 165 lines 19 and 21, but printed HERE and not "
                              "THERE. W4.")},
            {"excerpt_label": "Credit ordering — nonrefundable credits STOP at line 17",
             "location_reference": "Form 120S page 1, lines 14-20",
             "excerpt_text": ("14 Subtotal: Add lines 12 and 13 ... 15 Nonrefundable tax credits from "
                              "Arizona Form 300, Part 2, line 40 ... 17 Tax liability: Subtract line "
                              "15 from line 14 ... 18 PTE Tax Liability: Enter the amount from Part 2, "
                              "line 52 ... 19 Total Tax Liability: Add line 17 and 18 ... 20 "
                              "Refundable tax credits"),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ A REAL STRUCTURAL FACT. Nonrefundable credits apply against line 14 "
                              "(corporate tax + recapture) and the PTE tax is ADDED AFTERWARDS at "
                              "line 18/19, so they CANNOT reduce it. Refundable credits sit in the "
                              "PAYMENTS block and CAN. Pub 713 says both 'No' and 'nothing precludes' "
                              "in the same section (U4); THE FORM IS NOT AMBIGUOUS AND THE FORM "
                              "GOVERNS.")},
            {"excerpt_label": "Question B — the multistate gate, asked the OPPOSITE way from Form 165",
             "location_reference": "Form 120S page 1, question B",
             "excerpt_text": ("Does the S corporation conduct business within and without Arizona? "
                              "Yes  No"),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ 'Yes' HERE MEANS MULTISTATE. Form 165 question D asks 'Is this "
                              "partnership an Arizona-only partnership?' where 'Yes' means NOT "
                              "multistate. A SHARED BOOLEAN IS INVERTED FOR ONE OF THEM.")},
        ],
    },
    {
        "source_code": "AZ_2025_FORM_120S_INSTR",
        "source_type": "state_instruction", "source_rank": "implementation_official",
        "jurisdiction_code": "AZ", "tax_year_start": 2025, "tax_year_end": 2025,
        "entity_type_code": "1120S",
        "title": ("2025 Arizona Form 120S instructions — the conditional $50 minimum, the '$0 return' "
                  "refund script, penalties and e-file. ⚠ REGENERATED 2026-08-12, AFTER H.B. 4168, "
                  "AND STILL CITES NO ARIZONA MODIFICATION STATUTE"),
        "citation": ("2025 Arizona Form 120S instructions, 28 pages, /CreationDate = /ModDate "
                     "2026-08-12 (REGENERATED, not merely re-saved)"),
        "issuer": "Arizona Department of Revenue",
        "official_url": ("https://azdor.gov/sites/default/files/document/"
                         "FORMS_CORPORATE_2025_120S_i.pdf"),
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.5,
        "topics": ["az_pte_entity_returns", "az_pte_elective_tax"],
        "notes": ("⚠⚠ THE 28-PAGE BOOK THAT PROVES THE NEGATIVE. Counts over the whole book: "
                  "43-1021 = 0, 43-1022 = 0, 43-1121 = 0, 43-1122 = 0; 'Arizona basis' = 0; "
                  "depreciation / bonus / 168(k) = 0 substantive hits (the sole '179' is the digit "
                  "string inside the apportionment example .179865). The ONLY Title 43 sections it "
                  "cites are apportionment provisions. The 28 'addition' and 42 'subtract*' hits were "
                  "ALL READ IN CONTEXT and resolve into five innocuous buckets. Source brief §16.3."),
        "excerpts": [
            {"excerpt_label": "Line 12 — the $50 minimum is CONDITIONAL",
             "location_reference": "Form 120S instructions, line 12",
             "excerpt_text": ("The S Corporation is subject to the tax computed on line 12 only if it "
                              "has income subject to tax at the corporate level reported on federal "
                              "Form 1120S, even if line 11 is zero or a negative amount. The amount of "
                              "Arizona income tax is the greater of $50 or 4.9% of line 11."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ A CONDITIONAL MINIMUM, NOT AN UNCONDITIONAL ONE. Do NOT port "
                              "another state's flat minimum-tax logic here.")},
            {"excerpt_label": "Line 49's cross-check cites LINE 45, which is an income amount",
             "location_reference": "Form 120S instructions, line 49",
             "excerpt_text": ("NOTE: The apportionment ratio entered on line 45 must be the same as "
                              "the apportionment ratio entered on line 7."),
             "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ INSTRUCTION DEFECT AZ-D2 (W8). The intended cross-check is line 49 == "
                              "line 7 and THE FACE IS CORRECT. ⚠ SECOND-ORDER CONSEQUENCE: line 7 is "
                              "only reached when the S corp has federal-level taxable income, so a "
                              "multistate electing S corp with no BIG and no excess net passive income "
                              "never computes line 7 yet still needs line 49. The equality CANNOT be "
                              "hard.")},
            {"excerpt_label": "The '$0 return' refund script — a required, fully-scripted path",
             "location_reference": "Form 120S instructions, PTE estimated payments without an election",
             "excerpt_text": ("Line A, check the \"No\" box. Complete lines B through H and 1 through 17 "
                              "as directed. Skip to Part 2 on page 2. Line 37, enter \"0\". Lines 46 "
                              "through 48 and lines 50 through 52, enter \"0\". Return to Part 1, line "
                              "18 and enter \"0\". Line 19, enter \"0\". Line 21, enter the total of all "
                              "extension payments made. Line 22, enter the total of all estimated "
                              "payments made during the year. Line 23, enter \"0\". Line 24, add lines "
                              "20 through 23 and enter the total. Also, enter this amount on lines 26, "
                              "27, 29, 34, and 36. Line 36, this amount is refundable to the S "
                              "Corporation."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("NOT advisory prose — a LINE-BY-LINE FILING RECIPE, and the most likely "
                              "real-world Arizona PTE scenario for TY2025 because the federal SALT "
                              "deduction rose from $10,000 to $40,000. TWO variants exist on the 120S. "
                              "⚠ The refund CANNOT be applied to the 2026 PTE estimated tax liability "
                              "and CANNOT be applied to a shareholder's liability.")},
        ],
    },
]

AUTHORITY_SOURCES += [
    # -------------------------------------------------------------- statutes
    {
        "source_code": "AZ_ARS_43_1014",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "AZ",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("A.R.S. § 43-1014 — Entity-level tax election; partnerships; S corporations. THE "
                  "operative PTE statute: the election is an act of FILING THE ORDINARY RETURN, the "
                  "rate is set BY REFERENCE, and the two bases are DIFFERENT for the two entity types"),
        "citation": ("A.R.S. § 43-1014(A) (election and rate), (B)(1)(a)(ii) (partnership base), "
                     "(B)(1)(b) (S-corp base), (B)(2) (owner collection backstop), (C) eligibility, "
                     "(D) 60-day opt-out; as amended by Laws 2025 Ch. 182 Sec. 6"),
        "issuer": "Arizona Legislature",
        "official_url": "https://www.azleg.gov/ars/43/01014.htm",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.9,
        "topics": ["az_pte_elective_tax", "az_pte_entity_returns"],
        "notes": ("The azleg text served 2026-08-17 ALREADY REFLECTS the Laws 2025 Ch. 182 Sec. 6 "
                  "amendment — but only because that was CHECKED against the chaptered act. Do not "
                  "assume it for other sections: azleg still serves PRE-Ch.140 text for § 43-1021."),
        "excerpts": [
            {"excerpt_label": "§ 43-1014(A) — the election IS the filing; the rate is BY REFERENCE",
             "location_reference": "A.R.S. § 43-1014(A)",
             "excerpt_text": ("... at a tax rate that is the same as the highest tax rate prescribed by "
                              "section 43-1011. ... The election under this subsection is made by "
                              "filing the business's return under this title."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("THE STATUTORY PROOF THAT ARIZONA NEEDS NO THIRD PTE FORM. ⚠ The rate "
                              "leg cannot be resolved directly: § 43-1011 CANNOT BE READ off azleg "
                              "(U21). Pin the rate to the FORM FACE instead. ⚠ The timeliness clause "
                              "was STRUCK retroactively to TY2022 by Laws 2025 Ch. 182 Sec. 6.")},
            {"excerpt_label": "§ 43-1014(B)(1) — TWO DIFFERENT BASES for the two entity types",
             "location_reference": "A.R.S. § 43-1014(B)(1)(a)(ii) and (B)(1)(b)",
             "excerpt_text": ("(a)(ii) the Arizona taxable income determined under chapter 14 of this "
                              "title, including the items that require separate computation under "
                              "section 43-1412, paragraphs 1 through 16 ... (b) For an S corporation, "
                              "the total of all distributive income passed through to the shareholders "
                              "under section 43-1126, subsection B."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠⚠ THE STATUTORY ROOT OF THE NON-PARALLELISM. The partnership base runs "
                              "through chapter 14 (i.e. §§ 43-1401/43-1021/43-1022) PLUS the "
                              "§ 43-1412 separately-stated items; the S-corp base is raw federal "
                              "distributive income, and § 43-1126(B) is a REPORTING provision, not a "
                              "modification provision. Form 165 line 8 + line 9 = (a)(ii) exactly; "
                              "Form 120S line 37 = (b) exactly.")},
            {"excerpt_label": "§ 43-1014(C) and (D) — eligibility, the 60-day notice, and OPT-OUT",
             "location_reference": "A.R.S. § 43-1014(C)-(D)",
             "excerpt_text": ("C. The election ... does not apply to the following: 1. Partners or "
                              "shareholders that are not individuals, estates or trusts. ... 2. "
                              "Partners or shareholders who are individuals, estates or trusts and who "
                              "opt out ... D. ... shall notify all partners or shareholders who are "
                              "individuals, estates or trusts of the intent to make the election and "
                              "that each ... has the right to opt out ... The notice shall allow each "
                              "... at least sixty days ... If the partner or shareholder ... does not "
                              "respond within the sixty-day period or waives the right to opt out, the "
                              "partner or shareholder will be included in the election."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("OPT-OUT, NOT OPT-IN: NON-RESPONSE MEANS INCLUDED. Eligible = "
                              "individuals, estates, trusts. Ineligible = everything else, including "
                              "IRAs. ⚠ But a grantor trust or an SMLLC DISREGARDED TO AN INDIVIDUAL "
                              "CAN participate through look-through, and lands on Schedule E rows "
                              "E1-E3 (the INDIVIDUAL rows), not E4-E5.")},
        ],
    },
    {
        "source_code": "AZ_ARS_43_581",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "AZ",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("A.R.S. § 43-581 — Payment of estimated tax. Subsection (C) is the $150,000 PTE "
                  "estimated-payment trigger and the operative authority behind campaign ruling D-12 "
                  "A1; subsection (E)(2) is the $1,000 penalty floor"),
        "citation": "A.R.S. § 43-581(C) and § 43-581(E)(2); azleg text current for TY2025",
        "issuer": "Arizona Legislature",
        "official_url": "https://www.azleg.gov/ars/43/00581.htm",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.9,
        "topics": ["az_pte_estimated_payments"],
        "notes": ("VINTAGE CHECKED BOTH WAYS: § 43-581 is amended by NEITHER Laws 2025 Ch. 182 NOR "
                  "Laws 2026 Ch. 140 — the string '43-581' occurs ZERO times in the Ch. 140 chaptered "
                  "PDF — so the azleg text is current for TY2025."),
        "excerpts": [
            {"excerpt_label": "§ 43-581(C) — 'EXCEEDS $150,000', and the contested noun",
             "location_reference": "A.R.S. § 43-581(C)",
             "excerpt_text": AZ_581C_VERBATIM,
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("TWO SEPARATE QUESTIONS LIVE IN THIS SENTENCE AND THEY WERE RESOLVED "
                              "DIFFERENTLY. (1) THE VERB IS SETTLED: 'exceeds', so exactly $150,000 is "
                              "OUT — seven sources say so and one Pub 713 FAQ answer says 'or more' "
                              "while Pub 713's own FAQ lead-in says a third thing, 'meets or exceeds'. "
                              "⚠ AN EARLIER VERIFICATION PASS FLIPPED THIS THE WRONG WAY AND A LATER "
                              "ONE CAUGHT IT. (2) THE NOUN IS CONTESTED: AZDOR prints FOUR different "
                              "measurement bases and four of six documents contradict themselves "
                              "internally. RULED by campaign D-12 A1 to the statute's bare 'taxable "
                              "income' — A RULING, NOT A PUBLISHED AZDOR POSITION. U19 stays open.")},
        ],
    },
    {
        "source_code": "AZ_ARS_43_1021",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "AZ",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("A.R.S. § 43-1021 — Additions to Arizona gross income (individuals). ¶11 is the "
                  "depreciation add-back Form 165 line A1 implements; ¶15 is the PTE-tax add-back "
                  "whose ENTITY-LEVEL half has no line on either form"),
        "citation": "A.R.S. § 43-1021(11) (depreciation add-back) and § 43-1021(15) (PTE-tax add-back)",
        "issuer": "Arizona Legislature",
        "official_url": "https://www.azleg.gov/ars/43/01021.htm",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.6,
        "topics": ["az_165_depreciation", "az_pte_elective_tax"],
        "notes": ("⚠ azleg SERVES PRE-H.B.4168 TEXT for this section — it still ends at paragraph 16 "
                  "and the new § 168(n) paragraph 17 is absent. HARMLESS for TY2025 (¶17 is TY2026-only "
                  "under Ch. 140 Sec. 35(B)) but a TY2026 pass MUST NOT rely on it. ¶15 was re-read "
                  "VERBATIM from the CHAPTERED Ch. 140 Sec. 14, entirely lowercase and therefore "
                  "UNAMENDED, so its vintage is safe both ways."),
        "excerpts": [
            {"excerpt_label": "§ 43-1021(15) — the add-back the forms cannot express",
             "location_reference": "A.R.S. § 43-1021(15); chaptered Laws 2026 Ch. 140 Sec. 14",
             "excerpt_text": AZ_1021_15_VERBATIM,
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("READ THE FINAL SENTENCE CAREFULLY: the add-back is to be reflected in "
                              "TWO places — the owner's Arizona gross income AND THE ENTITY'S ARIZONA "
                              "TAXABLE INCOME. The owner half is fully implemented on all four K-1s. "
                              "THE ENTITY HALF HAS NO LINE: Form 165's page-6 A4 worksheet is a CLOSED "
                              "list of three items with no free-text row anywhere on page 6, and Form "
                              "120S has no additions schedule at all. ⚠ THE CASH-BASIS CIRCULARITY IS "
                              "REAL — federal ordinary income is already NET of the PTE tax paid "
                              "during the year, so the base is understated by the tax itself. "
                              "CAMPAIGN RULING D-12 A3: BUILD TO THE FORM, OWNER LEVEL ONLY.")},
            {"excerpt_label": "§ 43-1021(11) — the depreciation add-back behind Form 165 line A1",
             "location_reference": "A.R.S. § 43-1021(11)",
             "excerpt_text": ("The amount of any depreciation allowance allowed pursuant to section "
                              "167(a) of the internal revenue code to the extent not previously added."),
             "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("The ENTIRE federal § 167(a) allowance comes back, including bonus and "
                              "MACRS. Form 165 line A1: 'Enter the total amount of depreciation "
                              "deducted on the federal return.' Paired with the § 43-1022(17)(e) "
                              "subtraction at line B1.")},
        ],
    },
    {
        "source_code": "AZ_ARS_43_1401_1412",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "AZ",
        "tax_year_start": 2025, "tax_year_end": 2025, "entity_type_code": "1065",
        "title": ("A.R.S. §§ 43-1401 and 43-1412 — the partnership definitions and the SIXTEEN "
                  "separately-computed categories that Form 165 line 9 collapses into one box "
                  "(§ 179 is paragraph 5)"),
        "citation": ("A.R.S. § 43-1401(1) 'Arizona gross income' and (2) 'Arizona taxable income'; "
                     "A.R.S. § 43-1412 paragraphs 1 through 16, of which ¶5 is IRC § 179"),
        "issuer": "Arizona Legislature",
        "official_url": "https://www.azleg.gov/ars/43/01401.htm",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.9,
        "topics": ["az_pte_elective_tax", "az_165_depreciation"],
        "notes": ("H.B. 4168 does NOT amend either section — confirmed against the chaptered act's "
                  "AN ACT list."),
        "excerpts": [
            {"excerpt_label": "§ 43-1401(1)-(2) — the exclusion that line 9 exists to reverse",
             "location_reference": "A.R.S. § 43-1401(1) and (2)",
             "excerpt_text": ("1. \"Arizona gross income\" of a partnership means its taxable income for "
                              "the year, computed according to subtitle A, chapter 1, subchapter K of "
                              "the internal revenue code, exclusive of items requiring separate "
                              "computation under section 43-1412, paragraphs 1 through 16. ... "
                              "2. \"Arizona taxable income\" of a partnership means its Arizona gross "
                              "income adjusted by the modifications specified in sections 43-1021 and "
                              "43-1022 and section 43-1414, subsection A."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("Form 165 line 8 + line 9 is an EXACT STATUTORY RECONSTRUCTION of "
                              "§ 43-1014(B)(1)(a)(ii): § 43-1401(2) plus § 43-1412(1)-(16). ⚠ Note "
                              "'Arizona taxable income' of a partnership is defined by the INDIVIDUAL "
                              "modification sections — which is why Form 165 applies the individual "
                              "bonus rule at the entity level.")},
            {"excerpt_label": "§ 43-1412(5) — § 179 is a SEPARATELY-STATED item",
             "location_reference": "A.R.S. § 43-1412(5)",
             "excerpt_text": ("In computing taxable income of each partner, he shall include, whether "
                              "or not distribution is made to him, his distributive share of the "
                              "partnership's: ... 5. Additional first year depreciation computed "
                              "pursuant to section 179 of the internal revenue code."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ THE ROUTING QUESTION D-10 DID NOT REACH. For a partnership § 179 "
                              "enters the Arizona PTE base through FORM 165 LINE 9, not through line 1 "
                              "and not through Schedule A/B. Line 9 is a SINGLE UNDIFFERENTIATED BOX "
                              "covering SIXTEEN statutory categories with no supporting schedule — "
                              "the largest direct-entry surface on Form 165 and the place a § 179 "
                              "error will hide (W10). For an S corporation there is no routing "
                              "question at all.")},
        ],
    },
    {
        "source_code": "AZ_ARS_43_1077",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "AZ",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("A.R.S. § 43-1077 — Credit for entity-level income tax. Nonrefundable, five-year "
                  "carryforward, and KEYED TO TAX ACTUALLY PAID"),
        "citation": "A.R.S. § 43-1077(A), (B) and (C)",
        "issuer": "Arizona Legislature",
        "official_url": "https://www.azleg.gov/ars/43/01077.htm",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.9,
        "topics": ["az_pte_elective_tax", "az_owner_schedules_sbi"],
        "notes": "Short section, quoted entire because every clause is operative.",
        "excerpts": [
            {"excerpt_label": "§ 43-1077 in full — PAID, nonrefundable, five-year carryforward",
             "location_reference": "A.R.S. § 43-1077",
             "excerpt_text": ("A. For taxable years beginning from and after December 31, 2021, a "
                              "credit is allowed against the taxes imposed by this title for a taxpayer "
                              "who is a partner in a partnership or a shareholder of an S corporation "
                              "that elects to pay the tax under section 43-1014. B. The amount of the "
                              "credit is the portion of the tax paid by the partnership or S "
                              "corporation under section 43-1014 that is attributable to the partner's "
                              "or shareholder's share of income taxable in this state. C. If the "
                              "allowable credit exceeds the taxes otherwise due ... the amount of the "
                              "claim not used to offset taxes under this title may be carried forward "
                              "for not more than five consecutive taxable years ..."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ 'THE TAX **PAID**' — but Form 165 line 25 and Form 120S line 52 "
                              "compute tax OWED, and NO SCHEDULE RECONCILES OWED TO PAID BEFORE THE "
                              "K-1s ARE CUT. Pub 713's own Addendum #1 example allocates from the "
                              "LIABILITY, so that is the recommended default with a diagnostic when "
                              "payments fall short. Backstop: § 43-1014(B)(2) lets the department "
                              "collect from the OWNERS if the entity does not pay. U9 / W19.")},
        ],
    },
    {
        "source_code": "AZ_ARS_43_1414",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "AZ",
        "tax_year_start": 2025, "tax_year_end": 2025, "entity_type_code": "1065",
        "title": ("A.R.S. § 43-1414 — Federal assessment of imputed underpayment. Subsection "
                  "(B)(1)(b) imposes the Form 165PA tax at the highest INDIVIDUAL rate, against the "
                  "form's printed 4.5%"),
        "citation": ("A.R.S. § 43-1414(B)(1)(a) (the 90-day due date) and (B)(1)(b) (the rate); "
                     "subsection (A) amended by Laws 2025 Ch. 182 Sec. 7, subsection (B) UNTOUCHED"),
        "issuer": "Arizona Legislature",
        "official_url": "https://www.azleg.gov/ars/43/01414.htm",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.9,
        "topics": ["az_pte_entity_returns"],
        "notes": AZ_165PA_CONFLICT,
        "excerpts": [
            {"excerpt_label": "§ 43-1414(B)(1)(b) — the rate the form contradicts",
             "location_reference": "A.R.S. § 43-1414(B)(1)(b)",
             "excerpt_text": ("(b) The tax shall be imposed on the Arizona share of the adjustments at "
                              "the highest tax rate imposed on individuals under section 43-1011."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("= 2.5% for TY2025 BY SYLLOGISM (§ 43-1011 cannot be read off azleg — "
                              "U21). Form 165PA face line 13 and its instructions both print 4.5%, "
                              "which was Arizona's top individual rate BEFORE the S.B. 1828 flat-tax "
                              "phase-in completed. RED-DEFERRED by campaign D-12 A2 rather than "
                              "picking a rate. ⚠ Do not conflate with the 165PA LATE-FILING PENALTY, "
                              "also 4.5%, which is CORRECT.")},
        ],
    },
    {
        "source_code": "AZ_SB1274_2025_CH182",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "AZ",
        "tax_year_start": 2022, "tax_year_end": 2025,
        "title": ("S.B. 1274 (2025) = Laws 2025 Chapter 182, the tax corrections act of 2025 — struck "
                  "the PTE election's TIMELY-FILING requirement retroactively to TY2022, and touched "
                  "§ 43-1414 subsection (A) ONLY"),
        "citation": ("Laws 2025, Ch. 182 (S.B. 1274, 57th Leg. 1st Reg. Sess.), chaptered; Sec. 6 "
                     "(§ 43-1014), Sec. 7 (§ 43-1414(A)), Sec. 9 (retroactivity); approved by the "
                     "Governor May 13, 2025"),
        "issuer": "Arizona Legislature",
        "official_url": "https://www.azleg.gov/legtext/57leg/1r/laws/0182.pdf",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.9,
        "topics": ["az_pte_elective_tax"],
        "notes": ("⚠ [CORRECTED — verification pass §16.4 C4: the section numbering was OFF BY ONE in "
                  "SEVEN places. The CHAPTERED act's own headers read Sec.6 = § 43-1014, "
                  "Sec.7 = § 43-1414, Sec.8 = Laws 2023 ch.147 § 3, Sec.9 = Retroactivity. Substance "
                  "unaffected.] ⚠ NO RETROACTIVITY WAS GRANTED FOR THE § 43-1414 AMENDMENT — Sec. 9(B) "
                  "covers only Laws 2023 ch. 147 § 3."),
        "excerpts": [
            {"excerpt_label": "Sec. 6 + Sec. 9(A) — the timeliness repeal, retroactive to TY2022",
             "location_reference": "Laws 2025 Ch. 182 Sec. 6 and Sec. 9(A)",
             "excerpt_text": ("Sec. 6: The election under this subsection [must be made on or before "
                              "the due date or extended due date of the] IS MADE BY FILING THE "
                              "business's return under this title. ... Sec. 9(A): Section 43-1014, "
                              "Arizona Revised Statutes, as amended by this act, applies retroactively "
                              "to taxable years beginning from and after December 31, 2021."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ THE STALE-LAW TRAP THIS CLOSES: Booklet 120/165ES, posted under "
                              "AZDOR's 2025 row, still says 'This election must be made ... no later "
                              "than the due date or extended due date of its return.' Its /ModDate is "
                              "2024-11-19 and it is headed '2024 CORPORATE INCOME TAX HIGHLIGHTS' — "
                              "SIX MONTHS BEFORE THE REPEAL. Pub 713 confirms AZDOR's administration: "
                              "'2025 legislation (S.B. 1274) retroactively removed the timely filing "
                              "requirement.'")},
        ],
    },
    {
        "source_code": "AZ_ARS_43_1147_MSP",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "AZ",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("A.R.S. § 43-1147 — Situs of sales other than tangible personal property; the "
                  "Multistate Service Provider election, BINDING FOR FIVE CONSECUTIVE TAXABLE YEARS"),
        "citation": "A.R.S. § 43-1147(B) (the election) and § 43-1147(C)(1)-(2) (the terms of the lock)",
        "issuer": "Arizona Legislature",
        "official_url": "https://www.azleg.gov/ars/43/01147.htm",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.9,
        "topics": ["az_apportionment"],
        "notes": AZ_ELECTION_TIMELINESS_DIVERGENCE,
        "excerpts": [
            {"excerpt_label": "§ 43-1147(C) — timely ORIGINAL return, five-year lock, two exits",
             "location_reference": "A.R.S. § 43-1147(C)",
             "excerpt_text": ("1. The election must be made on the taxpayer's timely filed original "
                              "income tax return. The election is: (a) Effective retroactively for the "
                              "full taxable year ... (b) Binding on the taxpayer for at least five "
                              "consecutive taxable years, regardless of whether the taxpayer no longer "
                              "meets the percentage threshold ... 2. During the election period, the "
                              "election may be terminated as follows: (a) Without the permission of the "
                              "department on the acquisition or merger of the taxpayer. (b) With the "
                              "permission of the department before the expiration of five consecutive "
                              "taxable years."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ THE ONLY STATEFUL MULTI-YEAR ATTRIBUTE ON THE ARIZONA PTE RETURNS. "
                              "Question G on Form 165 / question D on Form 120S carries the Yr 1 ... "
                              "Yr 5 cycle marker and Schedule MSP Part A is completed ONLY IN YEAR "
                              "ONE. ⚠ AND TIMELINESS MATTERS HERE, unlike the PTE election — two "
                              "elections on the same return with OPPOSITE timeliness rules (W21).")},
        ],
    },
    {
        "source_code": "AZ_ARS_43_323_EFILE",
        "source_type": "state_statute", "source_rank": "controlling", "jurisdiction_code": "AZ",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("A.R.S. § 43-323(F)-(G) — partnership and corporate returns SHALL be filed "
                  "electronically, with an annual waiver and a no-waiver-needed carve-out"),
        "citation": "A.R.S. § 43-323(F) (the mandate and the waiver) and § 43-323(G) (no waiver needed)",
        "issuer": "Arizona Legislature",
        "official_url": "https://www.azleg.gov/ars/43/00323.htm",
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.9,
        "topics": ["az_pte_entity_returns"],
        "notes": AZ_EFILE_DERIVATIVE_NOTE,
        "excerpts": [
            {"excerpt_label": "§ 43-323(F) — the e-file mandate",
             "location_reference": "A.R.S. § 43-323(F)",
             "excerpt_text": ("Fiduciary returns, partnership returns, withholding returns and "
                              "corporate returns shall be filed electronically for taxable years "
                              "beginning from and after December 31, 2019, or when the department "
                              "establishes an electronic filing program, whichever is later. Any person "
                              "who is required to file electronically pursuant to this subsection may "
                              "apply to the director, on a form prescribed by the department, for an "
                              "annual waiver ..."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("Printed on BOTH faces above the declaration block. ⚠ FOUR OF THE SEVEN "
                              "EXEMPTIONS KEY OFF FEDERAL STATUS — a Gate-2 ingest dependency for "
                              "delvio-tax. ⚠ A 2026 SHORT-PERIOD RETURN ON THE 2025 FORM MUST BE "
                              "PAPER-FILED: a hard e-file block that must produce a RED diagnostic, "
                              "not a silent e-file attempt.")},
        ],
    },
    # ------------------------------------------------------ AZDOR publication
    {
        "source_code": "AZ_2025_PUB_713",
        "source_type": "state_instruction", "source_rank": "implementation_official",
        "jurisdiction_code": "AZ", "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("AZDOR Publication 713, The Arizona Pass-Through Entity Election — the department's "
                  "narrative and FAQ on the rate, election, amendment, revocation, eligibility, "
                  "estimates, credit, add-back, composite returns and credit ordering"),
        "citation": "AZDOR Publication 713, printed stamp 'Revised: Nov 2025', 12 pages, /ModDate 2026-06-02",
        "issuer": "Arizona Department of Revenue",
        "official_url": "https://azdor.gov/sites/default/files/2023-03/PUBLICATION_713.pdf",
        "current_status": "active", "is_substantive_authority": False, "trust_score": 8.0,
        "topics": ["az_pte_elective_tax", "az_pte_estimated_payments"],
        "notes": ("⚠⚠ PUB 713 IS INTERNALLY INCONSISTENT IN AT LEAST TWO PLACES AND CANNOT DISPLACE "
                  "THE STATUTE OR THE FORM. (1) THE $150,000 BOUNDARY: its NARRATIVE says 'exceeds', "
                  "its FAQ ANSWER says '$150,000 or more', and its FAQ LEAD-IN says 'meets or "
                  "exceeds' — THREE PHRASINGS IN ONE DOCUMENT. The statute governs; exactly $150,000 "
                  "is OUT. (2) CREDITS AGAINST PTE TAX: it opens 'Can Arizona income tax credits "
                  "offset the PTE tax due? No.' and then says 'Nothing precludes a partnership or an "
                  "S Corporation from claiming a refundable tax credit, OR EVEN A NONREFUNDABLE TAX "
                  "CREDIT, against its PTE tax liability.' The FORM is unambiguous and the form "
                  "governs (U4). trust_score is deliberately lower than the forms and statutes."),
        "excerpts": [
            {"excerpt_label": "PTE TAX FORMS — the department names only the two existing returns",
             "location_reference": "Pub 713, PTE TAX FORMS",
             "excerpt_text": ("What are the name and form number associated with the new PTE tax "
                              "return? The Department modified existing Forms 165 and 120S to allow "
                              "partnerships and S Corporations wishing to make the PTE election to "
                              "claim that election and then pass the PTE tax credit to their eligible "
                              "partners and shareholders. The revised forms and related instructions "
                              "are available on our website."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("One of the FOUR proofs that Arizona needs no third PTE form. Every form "
                              "number named anywhere in Pub 713 was enumerated — 165, 120, 355, 309, "
                              "301, 292, 141, 140 — and NO Arizona PTE-specific return exists among "
                              "them.")},
            {"excerpt_label": "NO TIERED PARTICIPATION",
             "location_reference": "Pub 713, PTE ELECTION",
             "excerpt_text": ("Can a lower-tier partnership or S Corporation make the PTE election and "
                              "pass the credit through to its partners or shareholders that are other "
                              "partnerships or S Corporations? No. Only individuals, estates, or trusts "
                              "that did not opt out of the PTE election may participate."),
             "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("A lower-tier entity may still make its OWN election for its OWN eligible "
                              "owners; what it cannot do is pass the credit UP. On the form an "
                              "upper-tier partnership partner is an 'O' in Schedule D column (f) and "
                              "lands in E7.")},
            {"excerpt_label": "S corporations MAY NOT special-allocate; partnerships MAY",
             "location_reference": "Pub 713; Form 165 Schedule D instructions",
             "excerpt_text": ("An S Corporation may not allocate its income and loss items to its "
                              "shareholders using a special allocation. ... [Form 165] NOTE: If the "
                              "partnership operating agreement specifies partnership proceeds are to be "
                              "distributed on the basis of a special allocation, complete columns (g) "
                              "and (h) using that allocation method."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ AN ASYMMETRY THAT MUST BE ENCODED. Form 165 Schedule D is by "
                              "DISTRIBUTIVE SHARE with special allocations HONOURED (Pub 713 carries a "
                              "worked example); Form 120S Schedule B is by OWNERSHIP SHARE with special "
                              "allocations FORBIDDEN. There is no S-corporation analogue.")},
            {"excerpt_label": "The '$0 return' scenario AZDOR expects for TY2025",
             "location_reference": "Pub 713, OTHER",
             "excerpt_text": ("Our partnership (S Corporation) made estimated payments in 2025 in "
                              "anticipation of making the PTE election for the 2025 taxable year. "
                              "However, after the federal state and local tax (SALT) deduction was "
                              "increased in 2025 from $10,000 to $40,000, our passthrough entity has "
                              "decided to NOT make the PTE election for tax year 2025. How does our "
                              "partnership (S Corporation) request a refund of its estimated tax "
                              "payments?"),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("AZDOR ANTICIPATES THIS AS A MAINSTREAM TY2025 PATH and scripts it "
                              "line by line in both instruction books. It is why Part 2 cannot be "
                              "gated on Question A alone (W18).")},
            {"excerpt_label": "The § 43-1021(15) practitioner question — answered OWNER LEVEL ONLY",
             "location_reference": "Pub 713, OTHER",
             "excerpt_text": ("We are tax practitioners located in another state. We have a client that "
                              "made the Arizona PTE election. After reviewing the Arizona income tax "
                              "forms (Form 165 and Form 120S) we are unable to determine where the add "
                              "back of the taxes paid on behalf of the partner/shareholder is listed. "
                              "Please provide direction. — The add back of taxes paid on behalf of the "
                              "partner/shareholder by the partnership or S Corporation is passed "
                              "through to that individual partner or shareholder. The individual "
                              "partner or shareholder reports this amount on his/her individual federal "
                              "income tax return."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("Practitioners asked THIS EXACT QUESTION and AZDOR answered OWNER LEVEL "
                              "ONLY. ⚠ The answer does not address the statute's 'and the "
                              "partnership's or S corporation's Arizona taxable income' clause at all, "
                              "and its closing words are themselves confused — the add-back is an "
                              "ARIZONA modification, not a federal one. Campaign D-12 A3 nevertheless "
                              "rules BUILD TO THE FORM, because the form cannot express the "
                              "alternative. U5 stays open.")},
        ],
    },
]

AUTHORITY_SOURCES += [
    # ------------------------------------------------------- owner schedules
    {
        "source_code": "AZ_2025_165_SCHK1",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "AZ",
        "tax_year_start": 2025, "tax_year_end": 2025, "entity_type_code": "1065",
        "title": ("Arizona Form 165 Schedule K-1 (2025) — Resident and Part-Year Resident Partner's "
                  "Share of Adjustment to Partnership Income, and the partner's PTE credit and "
                  "four-line add-back"),
        "citation": "Form 165 Schedule K-1 (2025), ADOR 10344 (25), 3 pages, /ModDate 2025-11-07; "
                    "instructions /ModDate 2026-07-07",
        "issuer": "Arizona Department of Revenue",
        "official_url": ("https://azdor.gov/sites/default/files/document/"
                         "FORMS_PARTNERSHIP_2025_165_SchedK1_f.pdf"),
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.7,
        "topics": ["az_owner_schedules_sbi"],
        "notes": ("⚠ Corporate partners and partners that are partnerships MUST use Schedule K-1(NR) "
                  "instead. ⚠ Part 7's gate reaches BACK: 'Complete Part 7 if the partner consented "
                  "to the partnership's election ... for this year OR FOR A PRIOR YEAR', which "
                  "defeats any 'if Q.A = No, suppress Part 7' shortcut."),
        "excerpts": [
            {"excerpt_label": "Part 1 line 3 routing — and THE MISSING SBI DESTINATION (U6)",
             "location_reference": "Form 165 Schedule K-1 instructions, Part 1 line 3",
             "excerpt_text": ("Resident Individuals: If line 3 is a positive number, enter the amount "
                              "on Arizona Form 140, page 1, line 16. If line 3 is a negative number, "
                              "enter the amount on Arizona Form 140, page 1, line 27. Part-Year "
                              "Resident Individuals: ... Arizona Form 140PY, line 31 [/] line 44. "
                              "Resident Estates or Resident Trusts: ... Arizona Form 141AZ, Schedule B, "
                              "line B3 [/] line B9."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠⚠ EXACTLY THREE OWNER SITUATIONS, AND IT STOPS. Lines 12-15 OF THE SAME "
                              "DOCUMENT use a FOUR-WAY route INCLUDING 'Individuals that made the "
                              "Small Business Income election...'. A resident partner who made the SBI "
                              "election has NO STATED DESTINATION for the Arizona basis adjustment. "
                              "⚠ THE REASON IS SHARPER THAN 'AZDOR FORGOT': line 3 routes to Form 140 "
                              "PAGE 1 lines 16/27 (main form, TWO-WAY) while the SBI-bearing lines "
                              "route to PAGE 5 line P (a one-way other-additions schedule) — line 3 "
                              "was never an instance of that template. DO NOT GUESS. It blocks the "
                              "INDIVIDUAL wave's binding, not this one. U6 / W13.")},
            {"excerpt_label": "Part 7 lines 11-15 — ONE credit line, FOUR add-back lines",
             "location_reference": "Form 165 Schedule K-1 page 3, Part 7",
             "excerpt_text": ("11 Partner's pro-rata share of the PTE Tax Credit. [Individuals, enter "
                              "this amount on Form 355, Part 1, line 1.] 12 ... Arizona PTE Taxes paid "
                              "in 2025 for taxable years prior to 2025. 13 ... Arizona PTE Taxes paid in "
                              "2025 for taxable year 2025. 14 ... comparable PTE Taxes from other states "
                              "paid in 2025 for taxable years prior to 2025. 15 ... comparable PTE Taxes "
                              "from other states paid in 2025 for taxable year 2025."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ FOUR ADD-BACK LINES SPLIT ON TWO AXES — Arizona vs OTHER-STATE, and "
                              "prior-year vs current-year — because the add-back is keyed to tax PAID "
                              "DURING calendar 2025 and must be split by the year it relates to. The "
                              "CREDIT is ONE line and is NOT decomposed by year. ⚠ Line 11's Form 355 "
                              "destination is Part 1 LINE 1 for a partnership and LINE 2 for an S "
                              "corporation. ⚠ ARIZONA'S FORM 355, NOT MASSACHUSETTS'.")},
        ],
    },
    {
        "source_code": "AZ_2025_165_SCHK1NR",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "AZ",
        "tax_year_start": 2025, "tax_year_end": 2025, "entity_type_code": "1065",
        "title": ("Arizona Form 165 Schedule K-1(NR) (2025) — Arizona Nonresident and Out-of-State "
                  "Partner's Share of Income and Deductions. THE schedule for ALL corporate and "
                  "partnership partners, and the carrier of the A4 question"),
        "citation": "Form 165 Schedule K-1(NR) (2025), ADOR 10345 (25), 3 pages, /ModDate 2025-11-07; "
                    "instructions /ModDate 2026-08-07",
        "issuer": "Arizona Department of Revenue",
        "official_url": ("https://azdor.gov/sites/default/files/document/"
                         "FORMS_PARTNERSHIP_2025_165_SchedK1NR_f.pdf"),
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.7,
        "topics": ["az_owner_schedules_sbi", "az_165_depreciation"],
        "notes": ("⚠ Column (b) is the apportionment ratio applied LINE BY LINE, stamped into SIX "
                  "different parts ('through Part 6, column (b)'). ⚠ Lines 10 (guaranteed payments) "
                  "and 14 (other deductions) have NO printed Form 140NR destination while every other "
                  "income line does — a printed-form gap verified against the face (U7)."),
        "excerpts": [
            {"excerpt_label": "Line 15 — FOUR owner types, TWO different columns (and A4)",
             "location_reference": "Form 165 Schedule K-1(NR) instructions, Part 2 line 15",
             "excerpt_text": ("Line 15 reflects the amount of partnership income which must be adjusted "
                              "to determine the difference between Internal Revenue Code § 702(a)(8) "
                              "and Arizona Revised Statutes § 43-1401(2). If ... column (c) is a "
                              "positive number: Individual partners, ... Arizona Form 140NR, line 31. "
                              "Estates or trusts, ... Arizona Form 141AZ, page 2, line B3. [negative: "
                              "line 41 / line B9.] Corporate partners: If the amount on line 15 is "
                              "positive, enter the amount from line 15, column (a) on Schedule A, line "
                              "A8 of Form(s) 120 or 120A. If ... negative, ... Schedule B, line B10 ... "
                              "Partnerships that are partners: ... Schedule A, line A4 of Arizona Form "
                              "165 [/] Schedule B, line B5 of Arizona Form 165."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠⚠ INDIVIDUALS AND ESTATES USE COLUMN (c); CORPORATIONS AND PARTNERSHIPS "
                              "USE COLUMN (a). Four owner types, two columns, off ONE line. The "
                              "partnership branch closes the TIERED LOOP back into Form 165's page-6 "
                              "A4/B5 worksheets — and note the upper-tier partnership takes the "
                              "UNAPPORTIONED column (a) amount and re-apportions at its own level. "
                              "⚠⚠ THE CORPORATE BRANCH IS THE A4 QUESTION: it hands a C corporation a "
                              "figure computed on the INDIVIDUAL full-§168(k) basis while "
                              "§ 43-1122(20) requires that corporation to compute Arizona depreciation "
                              "as if bonus had been ELECTED OUT, and NOTHING anywhere instructs a "
                              "re-computation. CAMPAIGN D-12 A4: PASS THE FIGURE THROUGH AS PRINTED "
                              "AND RAISE A REVIEW DIAGNOSTIC; COMPUTE NO CORPORATE-BASIS "
                              "RECOMPUTATION.")},
            {"excerpt_label": "Passive-loss and § 179 limits carried on the owner side",
             "location_reference": "Form 165 Schedule K-1(NR) instructions, Part 1",
             "excerpt_text": ("If Arizona Form 165 Schedule K-1(NR) shows a loss, you may only claim "
                              "such losses on your Arizona nonresident return to the extent: ... The "
                              "loss is not considered to be a passive activity loss for federal "
                              "purposes. (If it is, the loss will be treated as a passive activity loss "
                              "for Arizona purposes.) ... NOTE: The amount of Internal Revenue Code "
                              "(IRC) § 179 expense deductible is limited to the Arizona portion of the "
                              "amount deducted on federal Form 1040, Schedule E."),
             "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("A real limitation the engine must respect: a nonresident with a passive "
                              "Arizona-source loss must NOT begin from column (c).")},
        ],
    },
    {
        "source_code": "AZ_2025_120S_SCHK1_SET",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "AZ",
        "tax_year_start": 2025, "tax_year_end": 2025, "entity_type_code": "1120S",
        "title": ("Arizona Form 120S Schedule K-1 and Schedule K-1(NR) (2025) — the S-corporation "
                  "owner schedules. NEITHER carries an Arizona income adjustment, and their "
                  "information-schedule inventories differ from the partnership pair"),
        "citation": ("Form 120S Schedule K-1 (2025) ADOR 11191 (25), 2 pages, /ModDate 2025-11-12; "
                     "Schedule K-1(NR) ADOR 10338 (25), 3 pages, /ModDate 2025-11-12; both "
                     "instruction sets /ModDate 2026-07-15"),
        "issuer": "Arizona Department of Revenue",
        "official_url": ("https://azdor.gov/sites/default/files/document/"
                         "FORMS_CORPORATE_2025_120S_SchedK1_f.pdf"),
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.7,
        "topics": ["az_owner_schedules_sbi", "az_pte_entity_returns"],
        "notes": ("⚠ THE SOURCE-SET REPAIR: the 120S Schedule K-1(NR) face and both 120S K-1 "
                  "instruction extracts were 0-BYTE in the original research session and were "
                  "UNVERIFIABLE. They were re-extracted successfully on the verification pass (the "
                  "PDFs were never corrupt) and are now VERIFIED. ⚠ THE 120S K-1(NR) HAS NO "
                  "GUARANTEED-PAYMENTS LINE, so every line from 10 on is OFFSET BY ONE relative to "
                  "the 165 K-1(NR): A SHARED LINE MAP WILL BE OFF BY ONE. ⚠ The resident 120S K-1 has "
                  "NO virtual-currency/NFT part and NO gas-fees part (which the 165 resident K-1 has) "
                  "and instead has a MARIJUANA Schedule DFE part (which the 165 resident K-1 lacks). "
                  "DO NOT BUILD ONE SHARED K-1 MODEL."),
        "excerpts": [
            {"excerpt_label": "NO income-adjustment part — §5.3 seen from the owner side",
             "location_reference": "Form 120S Schedule K-1 page 1, Parts 1-5",
             "excerpt_text": ("Part 1 Net Capital Gain (Loss) From Investment in a Qualified Small "
                              "Business ... Part 2 Net capital gain (loss) from the exchange of legal "
                              "tender ... Part 3 Net long-term capital gain (loss) ... Part 4 Marijuana "
                              "Establishments Only ... Part 5 Shareholder's Share of the S "
                              "Corporation's Pass-Through Entity Tax Credit"),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ THERE IS NO LINE FOR A RESIDENT SHAREHOLDER'S SHARE OF AN ARIZONA "
                              "INCOME ADJUSTMENT — the schedule goes straight from the header block to "
                              "the qualified-small-business part, where the 165 resident K-1 has Part 1 "
                              "lines 1-3 carrying the fed→AZ adjustment. Corroborates the verified "
                              "negative from the owner side.")},
            {"excerpt_label": "Schedule K-1(NR) Part 5 line 20 — a MISLABELLED result (AZ-D5)",
             "location_reference": "Form 120S Schedule K-1(NR) page 3, Part 5 line 20",
             "excerpt_text": ("Multiply the amount on line 19 by the shareholder's ownership percentage "
                              "shown on page 1. Enter the result. This is the shareholder's portion of "
                              "the credit."),
             "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ IT IS NOT A CREDIT — it is a share of DISALLOWED FEDERAL EXPENSES "
                              "(marijuana Schedule DFE). The resident 120S K-1's parallel line 7 says "
                              "so correctly. Printed-form error W14: transcribe as printed, flag. "
                              "⚠ Note also that Part 5 and Part 6 ON THE SAME SCHEDULE route to "
                              "DIFFERENT PAGES of Form 140NR (page 6 line L vs page 5 line L) — bind "
                              "on the item LETTER, not the page number (U8).")},
        ],
    },
    # ---------------------------------------------------- supporting forms
    {
        "source_code": "AZ_2025_220_PTE",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "AZ",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("Arizona Form 220/PTE (2025) — Underpayment of Estimated Tax by Corporations & "
                  "Pass-Through Entities. Carries TWO printed cross-reference defects and the "
                  "corporate installment pattern with a 'PTE's see instructions' escape"),
        "citation": "Arizona Form 220/PTE (2025), ADOR 10342 (25), 4 pages, /ModDate 2025-11-07; "
                    "instructions /ModDate 2026-08-05",
        "issuer": "Arizona Department of Revenue",
        "official_url": ("https://azdor.gov/sites/default/files/document/"
                         "FORMS_CORPORATE_2025_220_PTE_f.pdf"),
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.0,
        "topics": ["az_pte_estimated_payments"],
        "notes": ("⚠ 'In most cases, the taxpayer DOES NOT HAVE TO FILE Form 220/PTE ... The "
                  "department will compute any penalty due and bill the taxpayer.' DO NOT AUTO-FILE "
                  "IT. ⚠ The ANNUALIZED income installment method IS available to electing PTEs; the "
                  "ADJUSTED SEASONAL method is NOT — stated on the faces of both this form and Form "
                  "120/PTE-W. ⚠ Part C line 17 substitutes the month by form type: 'Forms 120S: Use "
                  "3rd month instead of 4th month. PTE's: Use 3rd month instead of 4th month. Form "
                  "99T: Use 5th month.'"),
        "excerpts": [
            {"excerpt_label": "Part B line 5 — cites 'Form 165, line 23', which is NOT a tax line",
             "location_reference": "Form 220/PTE Part B line 5",
             "excerpt_text": ("Enter the 2025 Arizona tax liability from Form 99T, line 11 less line 12; "
                              "or Form 120, line 21 less line 22; or Form 120A, line 13 less line 14; or "
                              "Form 120S, line 19 less line 20, or Form 165, line 23."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ Form 165 line 23 is 'Multiply the amount on line 21 by the decimal on "
                              "line 22' — an INTERMEDIATE APPORTIONED NONRESIDENT BASE, not a tax. "
                              "Every other entry in the same sentence points at a NET TAX figure. THE "
                              "INTENDED REFERENCE IS FORM 165 LINE 25. Compute from line 25 and flag "
                              "(U11 / W20).")},
            {"excerpt_label": "Face line 37 — the routing list is wrong AND omits Form 165 (AZ-D4)",
             "location_reference": "Form 220/PTE Part C line 37",
             "excerpt_text": ("Enter the total here and on Form 99T, line 22; or Form 120, line 29; or "
                              "Form 120A, line 21; or Form 120S, line 25."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("⚠ Form 120S line 25 is 'Overpayments of tax from original return or "
                              "later adjustments'; the estimated-penalty line is 31. AND FORM 165 IS "
                              "ABSENT ALTOGETHER even though Form 165 line 35 imports this figure. "
                              "A FOURTH printed cross-reference defect in one package. **BUILD TO THE "
                              "165 / 120S INSTRUCTIONS, WHICH ARE RIGHT — NOT TO THIS FACE** "
                              "(U20 / W25).")},
        ],
    },
    {
        "source_code": "AZ_2025_120_PTE_W",
        "source_type": "state_form", "source_rank": "implementation_official", "jurisdiction_code": "AZ",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("Arizona Form 120/PTE-W — Estimated Tax Worksheet for Corporations & Pass-Through "
                  "Entities. ⚠ The file AZDOR posts under its 2025 row is stamped ADOR 10551 (24)"),
        "citation": "Arizona Form 120/PTE-W, ⚠ ADOR 10551 (24) — a genuinely STALE (24) revision "
                    "stamp; face /ModDate 2024-11-20, instructions /ModDate 2026-06-05",
        "issuer": "Arizona Department of Revenue",
        "official_url": ("https://azdor.gov/sites/default/files/document/"
                         "FORMS_CORPORATE_2025_120_PTE-W_f.pdf"),
        "current_status": "active", "is_substantive_authority": False, "trust_score": 7.5,
        "topics": ["az_pte_estimated_payments"],
        "notes": ("⚠ VINTAGE OPEN ITEM U10: AZDOR also posts a 2026 edition, and the Form 165 "
                  "instructions direct electing entities to THAT one to compute 2026 estimates. A "
                  "TY2025 return is prepared in 2026 and drives 2026 estimates, so the app should "
                  "probably surface the 2026 edition — confirm by diffing at authoring time. ⚠ Line 9 "
                  "CARRIES TWO RATES IN ONE LABEL: 4.9% for corporations, with the parenthetical "
                  "\"(PTE's use 2.5% as tax rate.)\". A single-rate transcription is wrong for one of "
                  "the two populations. ⚠ Its instructions are ALSO one of the four documents that "
                  "contradict themselves on the $150,000 measurement base."),
        "excerpts": [],
    },
    {
        "source_code": "AZ_2025_120_165EXT_V",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "AZ",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("Arizona Forms 120/165EXT and 120/165V (2025) — the extension application and the "
                  "e-file payment voucher, both of which ENCODE THE PTE ELECTION STATE ON THEIR FACES"),
        "citation": ("Form 120/165EXT, ADOR 10340 (25), 1 page, /ModDate 2025-11-06; Form 120/165V, "
                     "ADOR 11365 (25), 1 page, /ModDate 2025-11-06"),
        "issuer": "Arizona Department of Revenue",
        "official_url": ("https://azdor.gov/sites/default/files/document/"
                         "FORMS_CORPORATE_2025_120_165EXT_f.pdf"),
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.5,
        "topics": ["az_pte_entity_returns"],
        "notes": ("⚠ SEVEN months for Forms 120/120A/99T/99M, SIX for Forms 120S and 165 — printed on "
                  "the EXT face. Do not carry one number for both. ⚠ The EXT payment computation is "
                  "expressly limited to '165 (for partnerships that elected to pay tax at the entity "
                  "level)': a NON-electing partnership files it purely for time, with no payment leg. "
                  "⚠ The 120/165V voucher has SIX checkboxes, FOUR of them PTE-election-state variants "
                  "of two forms — a non-electing partnership uses it ONLY to pay the information "
                  "return penalty. ⚠ COMPOSITE filers use Form 204 for extensions and Form 140ES for "
                  "estimates, and payments CANNOT be converted between the two pots."),
        "excerpts": [],
    },
    {
        "source_code": "AZ_2025_SCH_MSP_ACA",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "AZ",
        "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("Arizona Schedule MSP and Schedule ACA (2025) — the two apportionment overrides: "
                  "the five-year-binding Multistate Service Provider election, and Air Carrier "
                  "revenue-aircraft-miles apportionment"),
        "citation": ("Schedule MSP, ADOR 11220 (25), /ModDate 2025-11-07 (instructions 2026-08-03); "
                     "Schedule ACA, ADOR 10535 (25), /ModDate 2025-11-07"),
        "issuer": "Arizona Department of Revenue",
        "official_url": ("https://azdor.gov/sites/default/files/document/"
                         "FORMS_CORPORATE_2025_SchedMSP_f.pdf"),
        "current_status": "active", "is_substantive_authority": True, "trust_score": 9.6,
        "topics": ["az_apportionment"],
        "notes": ("MSP: Part A qualification is computed ONLY IN YEAR ONE (A3 = A1/A2; qualify if "
                  "A3 > 0.850000, with alternate qualification at A5/A6 for a large Arizona university "
                  "campus or its 2,000+-employee support-services provider). Part B's market-sales "
                  "figure lands on Form 165 Schedule C line C3b column A / Form 120S Schedule A line "
                  "A3b column A. ⚠ NON-ELECTING service providers leave line C3b BLANK and include "
                  "Arizona service sales on line C3c. ACA: 'Revenue aircraft miles flown' takes its "
                  "meaning from the U.S. DOT uniform system of accounts, 14 C.F.R. Part 241. ⚠ "
                  "Schedule ACA's own routing list OMITS Form 165 Part 2 line 22 and Form 120S Part 2 "
                  "line 49, but BOTH parent forms say 'from Schedule C/A OR SCHEDULE ACA' — THE "
                  "PARENT FORM CLOSES THE LOOP and the omission is NOT a prohibition (U12)."),
        "excerpts": [],
    },
    {
        "source_code": "AZ_2025_FORM_165PA",
        "source_type": "state_form", "source_rank": "primary_official", "jurisdiction_code": "AZ",
        "tax_year_start": 2025, "tax_year_end": 2025, "entity_type_code": "1065",
        "title": ("Arizona Form 165PA (2025) — the BBA federal-adjustment partnership return. "
                  "RED-DEFERRED: its printed 4.5% tax rate contradicts A.R.S. § 43-1414(B)(1)(b)"),
        "citation": "Arizona Form 165PA (2025), ADOR 11291 (25), 3 pages, /ModDate 2025-11-07; "
                    "instructions /ModDate 2025-10-21",
        "issuer": "Arizona Department of Revenue",
        "official_url": ("https://azdor.gov/sites/default/files/document/"
                         "FORMS_PARTNERSHIP_2025_165PA_f.pdf"),
        "current_status": "active", "is_substantive_authority": True, "trust_score": 8.5,
        "topics": ["az_pte_entity_returns"],
        "notes": AZ_165PA_CONFLICT + " " + AZ_165PA_TWO_45S_WARNING,
        "excerpts": [
            {"excerpt_label": "Line 13 — the stale 4.5% tax rate",
             "location_reference": "Form 165PA Part 3 line 13",
             "excerpt_text": ("13 Multiply the amount on line 12 by the tax rate, 4.5%. Enter the "
                              "result."),
             "is_key_excerpt": True, "effective_year_start": 2025, "effective_year_end": 2025,
             "summary_text": ("The instructions repeat it verbatim ('This is the amount of tax owed by "
                              "the partnership'). RED-DEFERRED by campaign D-12 A2 — building to the "
                              "face knowingly OVER-TAXES BY 80%; building to the statute contradicts a "
                              "printed FINAL form. ⚠ ONE 165PA OUTPUT STILL REACHES FORM 165 WHILE "
                              "165PA ITSELF IS DEFERRED: a received 165PA Schedule K-1(NR) with a "
                              "positive line 3 requires an AMENDED Form 165 with that amount on line "
                              "A4.")},
        ],
    },
    {
        "source_code": "AZ_DOR_MEF_LOI_TY2025",
        "source_type": "state_efile_spec", "source_rank": "implementation_official",
        "jurisdiction_code": "AZ", "tax_year_start": 2025, "tax_year_end": 2025,
        "title": ("AZDOR Income Tax Letter of Intent for Tax Software Providers, TY2025 — the "
                  "Arizona MeF registration gate. TY2025 window CLOSED; TY2026 NOT YET PUBLISHED"),
        "citation": "AZDOR Income Tax Letter of Intent TY2025, 11 pages, /ModDate 2025-08-27; stated "
                    "due date November 28, 2025 (printed twice)",
        "issuer": "Arizona Department of Revenue",
        "official_url": ("https://azdor.gov/file-and-pay/e-file-services/e-file-software-developers/"
                         "arizona-mef-letter-intent"),
        "current_status": "active", "is_filing_authority": True, "trust_score": 9.0,
        "topics": ["az_pte_entity_returns"],
        "notes": AZ_LOI_NOTE + (" ⚠ TY2026 LOI NOT PUBLISHED as of 2026-08-17 — the landing page still "
                                "reads 'For tax year 2025, please download the Letter of Intent'. The "
                                "~end-of-November-2026 expectation is a PATTERN INFERENCE, not a "
                                "published date (U16). AZDOR posted the TY2025 LOI on 2025-08-27, "
                                "three months ahead, so DIARY A CHECK FROM SEPTEMBER 2026. Feeds "
                                "EFILE_GATES.md, not a computation."),
        "excerpts": [],
    },
]


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY → FORM LINKS
# ═══════════════════════════════════════════════════════════════════════════
AUTHORITY_FORM_LINKS: list[tuple[str, str, str]] = [
    # AZ_165
    ("AZ_2025_FORM_165", FORM_CODE_165, "governs"),
    ("AZ_2025_FORM_165_INSTR", FORM_CODE_165, "governs"),
    ("AZ_ARS_43_1014", FORM_CODE_165, "governs"),
    ("AZ_ARS_43_581", FORM_CODE_165, "governs"),
    ("AZ_ARS_43_1021", FORM_CODE_165, "governs"),
    ("AZ_ARS_43_1401_1412", FORM_CODE_165, "governs"),
    ("AZ_ARS_43_1077", FORM_CODE_165, "informs"),
    ("AZ_ARS_43_1414", FORM_CODE_165, "informs"),
    ("AZ_ARS_43_1147_MSP", FORM_CODE_165, "governs"),
    ("AZ_ARS_43_323_EFILE", FORM_CODE_165, "governs"),
    ("AZ_SB1274_2025_CH182", FORM_CODE_165, "governs"),
    ("AZ_HB4168_2026_CH140", FORM_CODE_165, "governs"),
    ("AZ_ARS_43_1022", FORM_CODE_165, "governs"),
    ("AZ_ARS_43_1122", FORM_CODE_165, "informs"),
    ("AZ_2025_PUB_713", FORM_CODE_165, "informs"),
    ("AZ_2025_165_SCHK1", FORM_CODE_165, "informs"),
    ("AZ_2025_165_SCHK1NR", FORM_CODE_165, "informs"),
    ("AZ_2025_220_PTE", FORM_CODE_165, "informs"),
    ("AZ_2025_120_PTE_W", FORM_CODE_165, "informs"),
    ("AZ_2025_120_165EXT_V", FORM_CODE_165, "informs"),
    ("AZ_2025_SCH_MSP_ACA", FORM_CODE_165, "governs"),
    ("AZ_2025_FORM_165PA", FORM_CODE_165, "informs"),
    ("AZ_DOR_MEF_LOI_TY2025", FORM_CODE_165, "informs"),
    # AZ_120S
    ("AZ_2025_FORM_120S", FORM_CODE_120S, "governs"),
    ("AZ_2025_FORM_120S_INSTR", FORM_CODE_120S, "governs"),
    ("AZ_ARS_43_1014", FORM_CODE_120S, "governs"),
    ("AZ_ARS_43_581", FORM_CODE_120S, "governs"),
    ("AZ_ARS_43_1077", FORM_CODE_120S, "informs"),
    ("AZ_ARS_43_1147_MSP", FORM_CODE_120S, "governs"),
    ("AZ_ARS_43_323_EFILE", FORM_CODE_120S, "governs"),
    ("AZ_SB1274_2025_CH182", FORM_CODE_120S, "governs"),
    ("AZ_HB4168_2026_CH140", FORM_CODE_120S, "informs"),
    ("AZ_ARS_43_1122", FORM_CODE_120S, "informs"),
    ("AZ_2025_PUB_713", FORM_CODE_120S, "informs"),
    ("AZ_2025_120S_SCHK1_SET", FORM_CODE_120S, "informs"),
    ("AZ_2025_220_PTE", FORM_CODE_120S, "informs"),
    ("AZ_2025_120_PTE_W", FORM_CODE_120S, "informs"),
    ("AZ_2025_120_165EXT_V", FORM_CODE_120S, "informs"),
    ("AZ_2025_SCH_MSP_ACA", FORM_CODE_120S, "governs"),
    ("AZ_DOR_MEF_LOI_TY2025", FORM_CODE_120S, "informs"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM AZ_165 — FACTS
# ═══════════════════════════════════════════════════════════════════════════
AZ165_FACTS: list[dict] = [
    # --- page 1 masthead / control flags -----------------------------------
    {"fact_key": "az165_return_type", "label": "CHECK ONE: Original / Amended", "data_type": "choice",
     "choices": ["Original", "Amended"], "required": True, "sort_order": 1,
     "notes": ("⚠ ARIZONA HAS NO SEPARATE PARTNERSHIP AMENDED FORM — the 165 itself carries the "
               "toggle. (Contrast the corporate side, which has Form 120X.) ⚠ BBA partnerships are "
               "ROUTED AWAY from the amended 165: 'Do not use this form to report changes from the "
               "filing of an amended federal Form 1065 if the partnership is subject to the BBA "
               "centralized audit regime. Report any federal imputed underpayment assessment ... on "
               "Arizona Form 165PA.'")},
    {"fact_key": "az165_fiscal_year_5253_week", "label": "52/53 week taxable year", "data_type": "boolean",
     "sort_order": 2},
    {"fact_key": "az165_filed_under_extension", "label": "Return filed under extension (box 82E)",
     "data_type": "boolean", "sort_order": 3,
     "notes": ("⚠ THE BOX IS `82E` ON FORM 165 AND `82F` ON FORM 120S, both inside the same "
               "revenue-use field 82. Transcribe each as printed. 'If the original return is filed "
               "under extension, DO NOT include a copy of the extension with your return.'")},
    {"fact_key": "az165_q_a_pte_election",
     "label": ("A. Did the partnership make the Pass-Through Entity (PTE) election to pay tax on its "
               "flow-through income at the entity level?"),
     "data_type": "boolean", "required": True, "sort_order": 10,
     "notes": ("⚠⚠ THE MASTER BRANCH — and one of the four proofs that Arizona needs no third PTE "
               "form (A.R.S. § 43-1014(A): 'The election under this subsection is made by filing the "
               "business's return under this title'). Yes → Part 2 + Schedule E, and line 7 must be "
               "zero. No → the information-return penalty at line 7. ⚠ BUT PART 2 IS NOT GATED ON "
               "THIS ALONE: see az165_pte_estimates_paid.")},
    {"fact_key": "az165_pte_estimates_paid",
     "label": "PTE estimated payments made during the taxable year (drives the Part 2 gate)",
     "data_type": "decimal", "sort_order": 11,
     "notes": ("⚠⚠ THE SECOND HALF OF THE PART 2 GATE. The Part 2 header reads '... or estimated "
               "payments were made and the partnership is not claiming the PTE election.' A loader "
               "branching on question A alone SUPPRESSES PART 2 FOR EXACTLY THE POPULATION THAT MOST "
               "NEEDS IT — and TY2025 is the year for it, because the federal SALT cap rose from "
               "$10,000 to $40,000 and Pub 713 scripts the '$0 return' refund path. W18.")},
    {"fact_key": "az165_q_b_dba", "label": "B. DBA", "data_type": "string", "sort_order": 12},
    {"fact_key": "az165_q_c_date_commenced", "label": "C. Date business commenced", "data_type": "date",
     "sort_order": 13},
    {"fact_key": "az165_q_d_arizona_only",
     "label": "D. Is this partnership an Arizona-only partnership?", "data_type": "boolean",
     "required": True, "sort_order": 14,
     "notes": ("⚠⚠ INVERTED RELATIVE TO FORM 120S QUESTION B. Here 'Yes' means ARIZONA-ONLY, i.e. NOT "
               "multistate — the 120S asks 'Does the S corporation conduct business within and "
               "without Arizona?', where 'Yes' means multistate. A SHARED BOOLEAN IS WRONG FOR ONE OF "
               "THEM; use az_is_multistate(form_code, answer). Instruction for line 22: 'If Line D is "
               "\"Yes\", enter 1.0'.")},
    {"fact_key": "az165_q_e_final_return", "label": "E. Is this the partnership's final return under this EIN?",
     "data_type": "boolean", "sort_order": 15,
     "notes": "⚠ A PLAIN FLAG. Form 120S question E is RICHER (Dissolved / Withdrawn / "
              "Merged-Reorganized plus a successor EIN). Do not share the field definition."},
    {"fact_key": "az165_q_f_apportionment_method",
     "label": "F. ARIZONA apportionment for multistate partnerships only (check one box)",
     "data_type": "choice", "choices": ["1 AIR CARRIER", "2 STANDARD", "3 SALES FACTOR ONLY"],
     "sort_order": 16,
     "notes": ("THE SCHEDULE C BRANCH. AIR CARRIER → Schedule ACA, skip Schedule C. STANDARD → the "
               "full Schedule C with the dynamic divisor. SALES FACTOR ONLY → Schedule C section C3 "
               "lines a-f only, then STOP (skip C4 and C5). ⚠ The methods are MUTUALLY EXCLUSIVE: "
               "'The taxpayer cannot use \"Standard\" to calculate one factor of the ratio, and "
               "\"SALES FACTOR ONLY\" to calculate another factor.'")},
    {"fact_key": "az165_q_g_msp_included", "label": "G. Arizona Schedule MSP is included",
     "data_type": "boolean", "sort_order": 17},
    {"fact_key": "az165_q_g_msp_cycle_year", "label": "G. Year of the MSP election cycle (Yr 1 - Yr 5)",
     "data_type": "choice", "choices": ["Yr 1", "Yr 2", "Yr 3", "Yr 4", "Yr 5"], "sort_order": 18,
     "notes": ("⚠ PERSISTENT MULTI-YEAR STATE — the ONLY stateful attribute on this return. The "
               "§ 43-1147(B) election is IRREVOCABLE and BINDING FOR FIVE CONSECUTIVE TAXABLE YEARS, "
               "and Schedule MSP Part A is completed ONLY IN YEAR ONE. ⚠ Unlike the PTE election, "
               "this one REQUIRES A TIMELY FILED ORIGINAL RETURN (W21).")},
    {"fact_key": "az165_q_h_filed_prior_returns",
     "label": "H. Did you file 2023 and 2024 Arizona partnership returns?", "data_type": "boolean",
     "sort_order": 19},
    {"fact_key": "az165_q_i_amended_federal_years",
     "label": "I. Years for which amended federal partnership returns were filed (MM/DD/YYYY)",
     "data_type": "string", "sort_order": 20},
    {"fact_key": "az165_q_j_irs_adjustments",
     "label": ("J. Has the IRS made any adjustments in any federal income tax return filed by the "
               "partnership not previously reported to the department?"),
     "data_type": "boolean", "sort_order": 21,
     "notes": ("⚠ THE FORM 165PA TRIGGER, and the face says so immediately below: 'For taxable years "
               "2016 through 2025, if you received a federal imputed underpayment assessment, or you "
               "filed an Administrative Adjustment Request that resulted in a federal imputed "
               "underpayment assessment, you must file Arizona Form 165PA to report those changes.' "
               "⚠ FORM 165PA IS RED-DEFERRED (D-12 A2) — this flag raises a prepare-manually "
               "diagnostic, it does not compute a 165PA. Due 90 days after the IRS final "
               "determination.")},
    {"fact_key": "az165_q_k_books_in_care_of", "label": "K. The partnership books are in care of",
     "data_type": "string", "sort_order": 22},
    {"fact_key": "az165_q_l_composite_return",
     "label": "L. Will a composite return be filed on Form 140NR?", "data_type": "boolean",
     "sort_order": 23,
     "notes": ("⚠ MUTUALLY EXCLUSIVE WITH THE PTE ELECTION, PER OWNER. A composite Form 140NR may "
               "cover only nonresident individuals that OPTED OUT, and requires a MINIMUM OF TEN "
               "participating members (AZDOR ruling ITR 16-2). Extension for the composite is Form "
               "204, NOT Form 120/165EXT; estimates are Form 140ES, NOT Form 120/165ES; and payments "
               "CANNOT be converted between the two pots.")},
    {"fact_key": "az165_q_m_marijuana_licence",
     "label": "M. Marijuana Establishments only — licence configuration", "data_type": "choice",
     "choices": ["1 Adult Use only", "2 Dual Lic. elected for-profit",
                 "3 Dual Lic. did not elect for-profit", "4 NMMD only"], "sort_order": 24,
     "notes": "Drives Form 99M and Schedule DFE routing. Form 99M is RED-DEFERRED for v1."},
    {"fact_key": "az165_q_n_adhs_registry_id", "label": "N. ADHS Registry Identification Number",
     "data_type": "string", "sort_order": 25,
     "notes": "Required if any question-M box is checked."},

    # --- Part 1 inputs ------------------------------------------------------
    {"fact_key": "az165_l1_federal_ordinary_and_rental",
     "label": "1. Federal ordinary business and rental income (loss) from Form 1065, Schedule K",
     "data_type": "decimal", "required": True, "sort_order": 30,
     "notes": ("⚠ THREE FEDERAL SCHEDULE K COMPONENTS SUMMED, NOT ONE. Verbatim: 'Enter the total of "
               "ordinary income (loss) from trade or business activities, rental real estate "
               "activities, and other rental activities from the federal Form 1065, Schedule K.' "
               "Mapping only federal Schedule K line 1 understates the entire return.")},
    {"fact_key": "az165_a1_total_federal_depreciation", "label": "A1. Total federal depreciation",
     "data_type": "decimal", "sort_order": 31,
     "notes": ("The ENTIRE federal § 167(a) allowance comes back, bonus and MACRS alike "
               "(A.R.S. § 43-1021(11)). 'Enter the total amount of depreciation deducted on the "
               "federal return.'")},
    {"fact_key": "az165_a2_non_az_muni_interest", "label": "A2. Non-Arizona municipal bond interest",
     "data_type": "decimal", "sort_order": 32,
     "notes": ("⚠ A **NET** FIGURE, NOT A GROSS ONE. 'Reduce the amount of interest income by the "
               "amount of any interest on indebtedness and other related expenses incurred or "
               "continued to purchase or carry those obligations that were not otherwise deducted or "
               "subtracted ... Do not include interest from obligations specifically exempt from "
               "Arizona income tax, nor any related expenses.' A loader mapping federal tax-exempt "
               "interest straight onto A2 WILL OVERSTATE IT.")},
    {"fact_key": "az165_a3_credit_related_additions",
     "label": "A3. Additions related to Arizona tax credits (page-6 worksheet total)",
     "data_type": "decimal", "sort_order": 33,
     "notes": ("Computed on the page-6 worksheet: Agricultural Water Conservation System Credit "
               "(Form 312), Credit for Taxes Paid for Coal Consumed in Generating Electrical Power "
               "(Form 318), Credit for Employment of TANF Recipients (Form 320), and Agricultural "
               "Pollution Control Equipment Credit (Form 325) split into D1 excess federal "
               "depreciation/amortization and D2 excess in federal adjusted basis. 'If you enter an "
               "amount on line A3, include the worksheet with your return.'")},
    {"fact_key": "az165_a4_other_additions",
     "label": "A4. Other additions to partnership income (page-6 worksheet total)",
     "data_type": "decimal", "sort_order": 34,
     "notes": ("⚠ A CLOSED ENUMERATION OF THREE ITEMS — Positive Partnership Income Adjustment, "
               "Federal Depreciation of Child Care Facilities, Expenditures for the Americans with "
               "Disabilities Act. THERE IS NO FREE-TEXT 'OTHER' ROW ANYWHERE ON PAGE 6, which is what "
               "makes the § 43-1021(15) entity-level add-back inexpressible (D-12 A3).")},
    {"fact_key": "az165_a4a_positive_partnership_adjustment",
     "label": "A4-A. Positive Partnership Income Adjustment (tiered-partnership loop)",
     "data_type": "decimal", "sort_order": 35,
     "notes": ("⚠ COLUMN (a), NOT COLUMN (c). 'If the partnership received Arizona Form 165 Schedule "
               "K-1(NR), and the net amount on line 15 is positive, enter the amount from column "
               "(a).' The UPPER-TIER partnership takes the UNAPPORTIONED distributive-share amount "
               "and re-apportions at its own level. A NEGATIVE line 15 goes to Schedule B line B5 "
               "instead. ⚠ SEPARATELY: a received Form 165PA Schedule K-1(NR) with a positive line 3 "
               "requires an AMENDED Form 165 carrying that amount here.")},
    {"fact_key": "az165_a4b_child_care_facility_depreciation",
     "label": "A4-B. Federal Depreciation of Child Care Facilities", "data_type": "decimal",
     "sort_order": 36},
    {"fact_key": "az165_a4c_ada_expenditures_addition",
     "label": "A4-C. Expenditures for the Americans with Disabilities Act (addition)",
     "data_type": "decimal", "sort_order": 37},
    {"fact_key": "az165_b1_recalculated_az_depreciation",
     "label": "B1. Recalculated Arizona depreciation (five vintage tiers)", "data_type": "decimal",
     "sort_order": 40,
     "notes": ("⚠ FIVE PLACED-IN-SERVICE TIERS: pre-12/31/2012 = 0% of federal § 168(k) (elect-out "
               "equivalent); 12/31/2012-12/31/2013 = ITP 16-2 METHOD-DEPENDENT AND UNPULLED (U1, "
               "DIRECT-ENTRY); 12/31/2013-12/31/2015 = 10%; 12/31/2015-12/31/2016 = 55%; after "
               "12/31/2016 = 100%. ⚠ THE FINAL TIER IS WORD-FOR-WORD THE INDIVIDUAL RULE AT "
               "§ 43-1022(17)(e), and the authority pointer is ITP 16-2, 'Procedure for INDIVIDUALS'. "
               "⚠ KEYED ON PLACED IN SERVICE, stated four times — NO date-keying ruling is needed "
               "here (contrast D-10 rulings 3 and 4 for TN and TX).")},
    {"fact_key": "az165_b1_ty2013_tier_amount",
     "label": "B1 (TY2013 tier only). ITP 16-2 amount — DIRECT ENTRY", "data_type": "decimal",
     "sort_order": 41,
     "notes": ("⚠ THE ONLY UNPULLED DOCUMENT GATING A MAINSTREAM LINE (U1). The AZDOR instruction "
               "defers entirely: 'the amount of the subtraction for these assets depends on the "
               "method used to compute the depreciation for assets. See the department's procedure, "
               "ITP 16-2.' Exposure is narrow but real: § 168(k) never applied to 27.5-year "
               "residential rental or 39-year nonresidential real property, so the live TY2025 "
               "exposure is 15-year qualified leasehold / retail improvement property from a TY2013 "
               "year, which finishes in 2028.")},
    {"fact_key": "az165_b2_basis_adjustment_on_disposition",
     "label": "B2. Basis adjustment for property sold or otherwise disposed of during the year",
     "data_type": "decimal", "sort_order": 42,
     "notes": ("⚠ CONDITIONED ON AN UNBROKEN ADD-BACK HISTORY BACK TO TY2000 — 'a taxpayer who has "
               "complied with the requirement to add back all depreciation with respect to that "
               "property on tax returns for ALL taxable years beginning from and after December 31, "
               "1999'. A STATEFUL, MULTI-DECADE ATTRIBUTE the app cannot derive from the current "
               "year. § 43-1022(18).")},
    {"fact_key": "az165_b3_us_government_interest",
     "label": "B3. Interest from U.S. government obligations", "data_type": "decimal", "sort_order": 43,
     "notes": ("⚠ 'NOT ALL OBLIGATIONS ASSOCIATED WITH THE FEDERAL GOVERNMENT ARE OBLIGATIONS OF THE "
               "FEDERAL GOVERNMENT. Obligations of the Government National Mortgage Association "
               "(GNMA) or the Federal National Mortgage Association (FNMA) are not obligations of the "
               "U.S. government and, therefore, are taxable to Arizona.' AZDOR ruling ITR 06-1 "
               "(unpulled, U17).")},
    {"fact_key": "az165_b4_agricultural_crop_contribution",
     "label": "B4. Agricultural crops charitable contribution", "data_type": "decimal", "sort_order": 44,
     "notes": "Crops contributed to Arizona tax-exempt charities for use in Arizona; AZDOR procedure "
              "ITP 12-1 (unpulled, U17)."},
    {"fact_key": "az165_b5_other_subtractions",
     "label": "B5. Other subtractions from partnership income (page-6 worksheet total)",
     "data_type": "decimal", "sort_order": 45,
     "notes": ("A CLOSED ENUMERATION OF EIGHT ITEMS: Negative Partnership Income Adjustment; Mine "
               "Exploration Expenses; Interest on Federally Taxable Arizona Obligations Evidenced by "
               "Bonds; Wood Stoves, Wood Fireplaces or Gas-Fired Fireplaces; Expenses Related to "
               "Certain Federal Credits (Work Opportunity, Empowerment Zone Employment, Employer-Paid "
               "Social Security Taxes on Employee Cash Tips, Indian Employment); Expenditures for the "
               "ADA; and Marijuana Establishments' Disallowed Federal Expenses (from Schedule DFE). "
               "⚠ NO FREE-TEXT ROW. ⚠ AND NO MCTCP ROW — H.B. 4168's new § 43-1022(31)/(32)/(35)/(36) "
               "tips, overtime, senior and vehicle-loan-interest subtractions are TY2025-effective "
               "and AZDOR REISSUED THIS BOOK AFTER ENACTMENT WITHOUT ADDING THEM (U18 / W23).")},
    {"fact_key": "az165_l7_information_return_penalty",
     "label": "7. Penalty for late filing or incomplete filing (Information return penalty)",
     "data_type": "decimal", "sort_order": 46,
     "notes": ("$100 per month or fraction, capped at $500. ⚠ APPLIES ONLY TO PARTNERSHIPS THAT DID "
               "NOT MAKE THE PTE ELECTION: 'Partnerships that made the PTE election, this is not an "
               "information return.' Pub 713 was asked directly and answered 'No'.")},

    # --- Part 2 inputs ------------------------------------------------------
    {"fact_key": "az165_l9_separately_stated_items",
     "label": "9. Total of all items requiring separate computation (A.R.S. § 43-1412 ¶1-16)",
     "data_type": "decimal", "sort_order": 50,
     "notes": ("⚠⚠ THE BIG ONE. A SINGLE UNDIFFERENTIATED BOX ON THE FACE covering SIXTEEN STATUTORY "
               "CATEGORIES, with NO supporting schedule and NO itemisation: capital gains/losses; "
               "§ 1231 gains/losses; charitable contributions; § 116/§ 243 dividends; § 901 foreign "
               "taxes; partially tax-exempt U.S. interest; income taxes paid to another state or "
               "country; **§ 179 expense**; § 111 recoveries; § 165(d) wagering; § 175 soil and "
               "water; § 212 nonbusiness expenses; § 214 dependent care; § 215 payments; § 216 "
               "co-op housing; § 263(c) IDC, § 617 mining exploration, § 751(b) items and specially "
               "allocated items. THE LARGEST DIRECT-ENTRY SURFACE ON FORM 165 AND THE PLACE A § 179 "
               "ERROR WILL HIDE (W10). Line 8 + line 9 is an exact reconstruction of "
               "§ 43-1014(B)(1)(a)(ii).")},
    {"fact_key": "az165_l16a_part_year_resident_portion",
     "label": "16A. Portion of line 16 earned while RESIDENTS of Arizona", "data_type": "decimal",
     "sort_order": 51,
     "notes": "⚠ SPLIT BY ACTUAL ARIZONA RESIDENCY PERIOD, NOT BY A DAY COUNT. 16A + 16B must equal "
              "line 16 — stated on the face."},
    {"fact_key": "az165_l16b_part_year_nonresident_portion",
     "label": "16B. Portion of line 16 earned while NONRESIDENTS of Arizona", "data_type": "decimal",
     "sort_order": 52},
    {"fact_key": "az165_l26_extension_payment", "label": "26. Extension payment made with Form 120/165EXT",
     "data_type": "decimal", "sort_order": 53,
     "notes": ("⚠ DO NOT AUTO-DERIVE FROM SCHEDULE F COLUMN (c). Line 27 EXPLICITLY imports 'from "
               "Schedule F, line F7, column (b)'; line 26's instruction says only 'Enter the "
               "Extension Payment made with Form 120/165EXT or online' and does NOT cite F7(c). A "
               "loader that auto-links it invents a relationship the form does not state (W6).")},
    {"fact_key": "az165_l27_estimated_tax_payments", "label": "27. Estimated Tax Payments",
     "data_type": "decimal", "sort_order": 54,
     "notes": "Explicitly = Schedule F line F7 column (b)."},
    {"fact_key": "az165_l28_amended_payments",
     "label": "28. Amended Returns: payment made with original return plus all payments after filing",
     "data_type": "decimal", "sort_order": 55},
    {"fact_key": "az165_l30_prior_overpayments",
     "label": "30. Overpayments of tax from original return or previously filed amended returns",
     "data_type": "decimal", "sort_order": 56},
    {"fact_key": "az165_l34_penalty_and_interest", "label": "34. Penalty and interest",
     "data_type": "decimal", "sort_order": 57,
     "notes": ("'Interest is calculated on the amount shown on LINE 25 at the prevailing rate. The "
               "interest period is from the ORIGINAL due date of the return to the payment date.' "
               "⚠ 'Partnerships making the PTE election ... may not be subject to the Information "
               "Return Penalty.'")},
    {"fact_key": "az165_l35_estimated_underpayment_penalty",
     "label": "35. Estimated underpayment penalty (Form 220/PTE Part C line 37; box 35A)",
     "data_type": "decimal", "sort_order": 58,
     "notes": ("⚠ BUILD THIS FLOW FROM THE FORM 165 INSTRUCTIONS, NOT FROM THE FORM 220/PTE FACE — "
               "the 220/PTE face's own routing list at line 37 names Form 120S line 25 (an "
               "OVERPAYMENT line, not the penalty line 31) and OMITS FORM 165 ENTIRELY (U20 / W25). "
               "⚠ On an AMENDED return, DO NOT RECOMPUTE: carry the original figure.")},
    {"fact_key": "az165_l39_overpayment_applied_next_year",
     "label": "39. Amount of line 38 to be applied to estimated tax (face prints 2025; MEANS 2026)",
     "data_type": "decimal", "sort_order": 59,
     "notes": ("⚠ PRINTED-FORM DEFECT AZ-D1 / W5. The FACE reads '2025'; the INSTRUCTION for the same "
               "line reads 'as a 2026 PTE estimated tax payment'; and Form 120S line 35 correctly "
               "reads 2026. On a TY2025 return, applying an overpayment to 2025 estimated tax is "
               "meaningless. Transcribe as printed, compute 2026, flag. Independently re-confirmed by "
               "the verification pass.")},

    # --- Schedule C ---------------------------------------------------------
    {"fact_key": "az165_schc_property_inventories", "label": "Schedule C C1a1. Inventories (original cost)",
     "data_type": "decimal", "sort_order": 60,
     "notes": "⚠ ORIGINAL COST, not net book value and not the federal Schedule L figures."},
    {"fact_key": "az165_schc_property_depreciable",
     "label": "Schedule C C1a2. Depreciable assets (do not include construction in progress)",
     "data_type": "decimal", "sort_order": 61},
    {"fact_key": "az165_schc_property_land", "label": "Schedule C C1a3. Land", "data_type": "decimal",
     "sort_order": 62},
    {"fact_key": "az165_schc_property_other", "label": "Schedule C C1a4. Other assets (describe)",
     "data_type": "decimal", "sort_order": 63},
    {"fact_key": "az165_schc_property_nonbusiness",
     "label": "Schedule C C1a5. Less: Nonbusiness property (if included in above totals)",
     "data_type": "decimal", "sort_order": 64},
    {"fact_key": "az165_schc_rented_property_net_rent",
     "label": "Schedule C C1b. Rented property — net annual rental rate (capitalised at 8×)",
     "data_type": "decimal", "sort_order": 65,
     "notes": ("EIGHT TIMES the NET annual rental rate, and 'net' means 'LESS THE AGGREGATE ANNUAL "
               "SUBRENTAL RATES PAID BY SUBTENANTS of the taxpayer'. Computer-software treatment: "
               "AZDOR ruling CTR 01-2 (unpulled, U17).")},
    {"fact_key": "az165_schc_payroll",
     "label": "Schedule C C2. Total wages, salaries, commissions and other compensation to employees",
     "data_type": "decimal", "sort_order": 66,
     "notes": "'(per federal Form 1065, or payroll reports)' — printed on the face. Form 120S says "
              "'per federal Form 1120S' in the same slot."},
    {"fact_key": "az165_schc_sales_to_az_purchasers",
     "label": "Schedule C C3a. Sales delivered or shipped to Arizona purchasers", "data_type": "decimal",
     "sort_order": 67},
    {"fact_key": "az165_schc_msp_service_sales",
     "label": "Schedule C C3b. Sales from services / designated intangibles (MSP electors only)",
     "data_type": "decimal", "sort_order": 68,
     "notes": "⚠ NON-ELECTING service providers LEAVE THIS BLANK and include Arizona service sales on "
              "line C3c instead."},
    {"fact_key": "az165_schc_other_gross_receipts", "label": "Schedule C C3c. Other gross receipts",
     "data_type": "decimal", "sort_order": 69},

    # --- Schedule D / E / F / G ---------------------------------------------
    {"fact_key": "az165_partner_rows",
     "label": "Schedule D. Partner rows D1-D10 (name, address, TIN, residency code, share)",
     "data_type": "string", "sort_order": 70,
     "notes": ("Column (a) PTE checkbox = 'the partner did NOT opt out'. Column (f) residency code: "
               "R resident individual, N nonresident individual, P part-year resident individual, "
               "E estate or trust, O other entity (corporation, partnership, etc.). Column (g) is a "
               "DECIMAL TO SIX PLACES (1% = .010000). ⚠ FOR AN IRA PARTNER, ENTER THE TIN OF THE "
               "CUSTODIAN, NOT of the person for whom the IRA is maintained; do not truncate any "
               "TIN. ⚠ For a grantor trust or an SMLLC disregarded to an individual THAT DID NOT OPT "
               "OUT, enter only the BENEFICIAL OWNER'S information and use the BENEFICIAL OWNER'S "
               "residency. ⚠ SPECIAL ALLOCATIONS ARE HONOURED HERE and forbidden on Form 120S. More "
               "than 10 partners → additional schedules.")},
    {"fact_key": "az165_sched_e_rows",
     "label": "Schedule E. Summary rows E1-E8 (consent, count, total distributive shares)",
     "data_type": "string", "sort_order": 71,
     "notes": ("Gate: 'Partnerships making the PTE election, complete Schedule E. All others, skip to "
               "Schedule G.' Rows: E1 resident individuals; E2 nonresident individuals; E3 part-year "
               "resident individuals; E4 resident estates/trusts; E5 nonresident estates/trusts; "
               "E6 = E1..E5; E7 partners that opted out or are excluded; E8 = E6 + E7. ⚠ LOOK-THROUGH "
               "PARTNERS ARE COUNTED IN E1-E3, NOT E4-E5 — a grantor trust lands on the INDIVIDUAL "
               "rows, which is counter-intuitive and easy to get wrong. ⚠ E8 COLUMN (c) SHOULD EQUAL "
               "1.000000 — a hard cross-foot printed ON THE FACE.")},
    {"fact_key": "az165_schf_estimated_payments",
     "label": "Schedule F line F7 column (b). Total estimated tax payments", "data_type": "decimal",
     "sort_order": 72,
     "notes": "⚠ Form 165's Schedule F has THREE columns (date, estimated, extension). Form 120S's "
              "Schedule D has FOUR, splitting S-corp estimates from PTE estimates, because an S corp "
              "can owe both a corporate-level tax and a PTE tax in the same year. A partnership "
              "cannot."},
    {"fact_key": "az165_schf_extension_payments",
     "label": "Schedule F line F7 column (c). Total extension payments", "data_type": "decimal",
     "sort_order": 73,
     "notes": "⚠ NOT auto-linked to line 26 — the form does not state that link (W6)."},
    {"fact_key": "az165_schg_az_activities",
     "label": "Schedule G1. Nature and location(s) of the partnership's Arizona business activities",
     "data_type": "string", "sort_order": 74},
    {"fact_key": "az165_schg_non_az_activities",
     "label": "Schedule G2. Nature and location(s) of business activities outside of Arizona",
     "data_type": "string", "sort_order": 75},
    {"fact_key": "az165_paid_preparer_tin", "label": "PAID PREPARER'S TIN", "data_type": "string",
     "sort_order": 76,
     "notes": "⚠ Form 165 prints 'PAID PREPARER'S TIN'; Form 120S prints 'PAID PREPARER'S PTIN'. "
              "Transcribe each as printed."},
    {"fact_key": "az165_prior_year_taxable_income",
     "label": "Prior-year taxable income (the § 43-581(C) $150,000 estimated-payment test)",
     "data_type": "decimal", "sort_order": 77,
     "notes": ("⚠⚠ TWO SEPARATE QUESTIONS. (1) THE BOUNDARY IS SETTLED: the statute and all six "
               "instruction sets say 'EXCEEDS', so exactly $150,000 is OUT. A single Pub 713 FAQ "
               "answer says 'or more' and Pub 713's FAQ lead-in says a third thing; Pub 713 is "
               "internally inconsistent three ways. AN EARLIER VERIFICATION PASS FLIPPED THIS THE "
               "WRONG WAY AND A LATER ONE CAUGHT IT. (2) WHICH TAXABLE INCOME IS A RULING, NOT A "
               "PUBLISHED POSITION: AZDOR prints FOUR bases and four of six documents contradict "
               "themselves internally. D-12 A1 ruled the statute's bare 'taxable income' and was "
               "REFINED the same session — that named a SOURCE without naming a NUMBER, and A.R.S. "
               "§ 43-1401(2) DEFINES the term as ARIZONA TAXABLE INCOME. ⚠ ON THIS FORM THE FIGURE "
               "IS **PRIOR-YEAR LINE 5**, NOT LINE 10 — line 8 (= line 5) plus line 9 reconstructs "
               "§ 43-1014(B)(1)(a)(ii), so line 10 is the larger PTE BASE and would be a FIFTH reading "
               "no AZDOR document prints. U19 STAYS OPEN and the determination is PROVISIONAL.")},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM AZ_165 — RULES
# ═══════════════════════════════════════════════════════════════════════════
AZ165_RULES: list[dict] = [
    {"rule_id": "R-AZ165-CONFORM", "title": "TY2025 conformity is COMPOUND: 1/1/2025 PLUS retroactive OBBBA",
     "rule_type": "classification", "sort_order": 1, "inputs": [], "outputs": ["az_conformity"],
     "formula": "az_conformity(2025) -> § 43-105(B): IRC @ 2025-01-01, excluding later enactments, "
                "PLUS P.L. 119-21 provisions retroactively effective in TY2025",
     "description": ("A.R.S. § 43-105(B) as amended by H.B. 4168 (Laws 2026 Ch. 140 Sec. 12). ⚠ "
                     "ARIZONA'S TY2025 CONFORMITY IS NEITHER 1/1/2025 NOR 1/1/2026 — it is 1/1/2025 "
                     "PLUS a statutory graft of retroactively-effective OBBBA provisions, in a "
                     "subsection that only exists because H.B. 4168 renumbered the old (A). TY2026+ "
                     "is § 43-105(A), a clean 1/1/2026 — AND THAT IS THE PRACTITIONER HEADLINE. "
                     "Porting the headline into a TY2025 spec is the single most likely way to get "
                     "Arizona wrong. Ch. 140 Sec. 35(A) makes § 43-105 retroactive to taxable years "
                     "beginning after 12/31/2024, so it DOES reach TY2025."),
     "exceptions": ("⚠ THE GRAFT CLAUSE IS A CATEGORY, NOT A LIST. AZDOR has published no "
                    "provision-by-provision mapping of which P.L. 119-21 provisions it treats as "
                    "'retroactively effective' (U3, OPEN AS A FACT). Campaign D-10 governs the § 179 "
                    "consequence by RULING, not by publication."),
     "notes": "_yk() RAISES on an unkeyed year so a TY2026 engagement cannot inherit TY2025 law."},
    {"rule_id": "R-AZ165-168N-NEG", "title": "§ 168(n) QPP: NO Arizona add-back for TY2025 — a verified absence",
     "rule_type": "classification", "sort_order": 2, "inputs": [], "outputs": ["az_168n_addback"],
     "formula": "az_168n_addback_applies(2025) == False; az_168n_addback_applies(2026) == True",
     "description": ("New § 43-1021(17) (individuals, Ch. 140 Sec. 14) and § 43-1121(25) "
                     "(corporations, Sec. 22) are BOTH expressly limited to 'TAXABLE YEARS BEGINNING "
                     "FROM AND AFTER DECEMBER 31, 2025', reinforced by Sec. 35(B), which gives "
                     "§ 43-1021 a TY2026 retroactive date. Read from the CHAPTERED act: the new "
                     "paragraph is ALL-CAPS (new text) and carries the date on its face. Neither "
                     "Arizona PTE form has a § 168(n) line and neither instruction book mentions "
                     "§ 168(n) — CORRECT FOR TY2025."),
     "exceptions": ("⚠ A TY2026 pass MUST re-read the page-6 A4 worksheet: if AZDOR adds a QPP row it "
                    "will land there, and if it does not, § 168(n) inherits the same 'no line exists' "
                    "problem. DO NOT CODE ONE § 168(n) RULE ACROSS BOTH YEARS."),
     "notes": "⚠ azleg still serves PRE-Ch.140 § 43-1021 text (ending at ¶16). Harmless for TY2025."},
    {"rule_id": "R-AZ165-P1-ADD", "title": "Line 2 = A1 + A2 + A3 + A4 (Schedule A additions)",
     "rule_type": "calculation", "sort_order": 3,
     "inputs": ["az165_a1_total_federal_depreciation", "az165_a2_non_az_muni_interest",
               "az165_a3_credit_related_additions", "az165_a4_other_additions"],
     "outputs": ["AZ165_L2"], "formula": "L2 = A1 + A2 + A3 + A4",
     "description": ("Form 165 prints its modification apparatus ON THE FACE, which Form 120S does "
                     "not. A3 and A4 are page-6 worksheet totals and the worksheet must be included "
                     "with the return whenever an amount is entered."),
     "exceptions": "⚠ A2 IS A NET FIGURE — carrying costs and Arizona-exempt obligations are removed "
                   "before it reaches this line.",
     "notes": "A1 is the ENTIRE federal § 167(a) allowance (§ 43-1021(11))."},
    {"rule_id": "R-AZ165-P1-SUB", "title": "Line 4 = B1 + B2 + B3 + B4 + B5 (Schedule B subtractions)",
     "rule_type": "calculation", "sort_order": 4,
     "inputs": ["az165_b1_recalculated_az_depreciation", "az165_b2_basis_adjustment_on_disposition",
               "az165_b3_us_government_interest", "az165_b4_agricultural_crop_contribution",
               "az165_b5_other_subtractions"],
     "outputs": ["AZ165_L4"], "formula": "L4 = B1 + B2 + B3 + B4 + B5",
     "description": "Line 3 = line 1 + line 2 is the subtotal these subtract from.",
     "exceptions": ("⚠ B2 is conditioned on an UNBROKEN Arizona add-back history for that asset back "
                    "to taxable years beginning after 12/31/1999 — a stateful, multi-decade attribute."),
     "notes": "⚠ B5's page-6 worksheet is a CLOSED list of eight items with NO free-text row."},
    {"rule_id": "R-AZ165-DEPR-B1", "title": "Line B1: the FIVE-tier Arizona depreciation recomputation",
     "rule_type": "calculation", "sort_order": 5,
     "inputs": ["az165_b1_ty2013_tier_amount"], "outputs": ["AZ165_B1"],
     "formula": ("B1 = sum over assets of allowable § 167(a) depreciation recomputed at the tier's AZ "
                 "bonus percentage of federal § 168(k): 0% (pre-12/31/2012) | ITP 16-2 "
                 "(12/31/2012-12/31/2013) | 10% (12/31/2013-12/31/2015) | 55% (12/31/2015-12/31/2016) "
                 "| 100% (after 12/31/2016)"),
     "description": ("⚠ FIVE tiers, not four — the brief's heading was corrected on verification; the "
                     "instruction and its table both carry five placed-in-service windows. ⚠ KEYED ON "
                     "**PLACED IN SERVICE**, STATED FOUR TIMES IN FOUR SENTENCES, so unlike Tennessee "
                     "and Texas (D-10 rulings 3 and 4) ARIZONA IS NOT SILENT AND NO RULING IS NEEDED. "
                     "Add all tiers together and enter the total on line B1."),
     "exceptions": ("⚠ THE TY2013 TIER IS UNDEFINED WITHOUT ITP 16-2, WHICH HAS NEVER BEEN PULLED "
                    "(U1). AZDOR defers entirely: 'the amount of the subtraction for these assets "
                    "depends on the method used'. DIRECT-ENTRY with a diagnostic. Exposure is narrow "
                    "but real — § 168(k) never applied to 27.5-/39-year real property, so what "
                    "survives is 15-year qualified leasehold / retail improvement property from a "
                    "TY2013 year."),
     "notes": "⚠ FORM 165 ONLY. AZ_120S gets NO depreciation logic (campaign D-12)."},
    {"rule_id": "R-AZ165-BONUS-IND", "title": "Form 165 applies the INDIVIDUAL bonus regime at the entity level",
     "rule_type": "classification", "sort_order": 6, "inputs": [], "outputs": ["az165_bonus_regime"],
     "formula": "AZ_165_BONUS_REGIME == 'individual' (§ 43-1021(11) + § 43-1022(17)(e))",
     "description": ("Three independent confirmations. (1) Line B1's final tier is WORD-FOR-WORD "
                     "§ 43-1022(17)(e) — 'as if the bonus depreciation had been the full amount of "
                     "federal bonus depreciation pursuant to IRC § 168(k)'. (2) The instruction's own "
                     "authority pointer is ITP 16-2, 'Procedure for INDIVIDUALS who Claim Federal "
                     "and/or Arizona Bonus Depreciation', cited THREE TIMES on this one line. (3) The "
                     "PTE-base note and § 43-1401(2) both build a partnership's Arizona taxable "
                     "income from §§ 43-1021 and 43-1022 — THE INDIVIDUAL SECTIONS. ⚠ Arizona runs "
                     "OPPOSITE regimes in the same year: corporations DECOUPLE under § 43-1122(20), "
                     "which subtracts as if the § 168(k)(7) ELECTION OUT had been made."),
     "exceptions": ("⚠ THE INDIVIDUAL RULE IS NET-ZERO ONLY FOR POST-2016 ASSETS. It does NOT cancel "
                    "for the 0% / 10% / 55% tiers or for the § 43-1022(18) disposition true-up, so a "
                    "partnership with an old asset base computes a DIFFERENT PTE base than an "
                    "otherwise identical S corporation. A REAL ECONOMIC DIFFERENCE between the two "
                    "Arizona entity types, and Delvio will surface it."),
     "notes": "Both regimes were re-verified UNCHANGED by H.B. 4168 (Secs. 15 and 23, no strike-through)."},
    {"rule_id": "R-AZ165-A4-CORP", "title": "A4: pass the K-1 figure to a corporate partner AS PRINTED; no recomputation",
     "rule_type": "routing", "sort_order": 7, "inputs": [], "outputs": ["az165_k1nr_l15_corporate_route"],
     "formula": ("az_corporate_partner_adjustment(k1nr_line15_col_a) -> pass through to Form 120/120A "
                 "Schedule A line A8 (positive) or Schedule B line B10 (negative); "
                 "recomputed_on_corporate_basis is None"),
     "description": ("⚠⚠ CAMPAIGN RULING D-12 A4 (2026-08-19), ruled separately in the same session "
                     "after the gap was surfaced rather than papered over. Arizona's split runs "
                     "straight through a partnership K-1: Form 165 computes its Arizona depreciation "
                     "adjustment on the INDIVIDUAL full-§168(k) basis and Schedule K-1(NR) line 15 "
                     "hands that number to a C-corp partner, while § 43-1122(20) requires that "
                     "corporation to compute Arizona depreciation as if bonus had been ELECTED OUT. "
                     "NOTHING on Form 165, on the K-1(NR), or on the Form 120 A8/B10 lines instructs "
                     "a re-computation. RULED: PASS THE FIGURE THROUGH AS THE K-1 PRINTS IT AND RAISE "
                     "A REVIEW DIAGNOSTIC NAMING THE SITUATION. COMPUTE NO CORPORATE-BASIS "
                     "RECOMPUTATION — Arizona publishes none and no form line carries one, so "
                     "building it would invent a position the state has never stated."),
     "exceptions": ("⚠ THREE READINGS ARE AVAILABLE and the research deliberately chose none: (a) "
                    "AZDOR intends the corporate partner to accept the partnership-level number "
                    "(administrative simplification — the ENTITY owns the asset); (b) the corporate "
                    "partner is expected to layer its own § 43-1121(4)/§ 43-1122(20) adjustment on "
                    "top, EXCEPT that line 15 is expressly the whole page-1 line 6 adjustment "
                    "INCLUDING A1/B1 and the form gives no way to split it; (c) a genuine AZDOR gap "
                    "arising only for C-corp partners of bonus-taking partnerships. THE FACT STAYS "
                    "OPEN (U2 / W9); the Form 120 / 120A instructions were never pulled and are "
                    "C-CORP-WAVE scope. It does NOT block this wave."),
     "notes": ("⚠ COLUMN DISCIPLINE: individuals and estates/trusts take column (c); CORPORATIONS AND "
               "PARTNERSHIPS TAKE COLUMN (a). Four owner types, two columns, off one line.")},
    {"rule_id": "R-AZ165-L5", "title": "Line 5 = line 3 − line 4: partnership income adjusted to ARIZONA BASIS",
     "rule_type": "calculation", "sort_order": 8, "inputs": ["az165_l1_federal_ordinary_and_rental"],
     "outputs": ["AZ165_L5"], "formula": "L5 = (L1 + L2) − L4",
     "description": ("⚠ LINE 5 FEEDS THE PTE BASE (line 8) AND SCHEDULE D COLUMN (h). It does NOT go "
                     "to the owners — that is line 6."),
     "exceptions": "", "notes": "See R-AZ165-L6: crossing 5 and 6 is the most likely single "
                                "transcription error on this form."},
    {"rule_id": "R-AZ165-L6", "title": "Line 6 = line 5 − line 1: THE NET ADJUSTMENT, and the only number that leaves Part 1",
     "rule_type": "calculation", "sort_order": 9, "inputs": ["az165_l1_federal_ordinary_and_rental"],
     "outputs": ["AZ165_L6"], "formula": "L6 = L5 − L1",
     "description": ("⚠⚠ THE MOST IMPORTANT HANDOFF ON THE FORM. Line 6 — and ONLY line 6 — leaves "
                     "Part 1 for the owners: it feeds 165 Schedule K-1 line 1 (× the partner's "
                     "percentage → line 3) and 165 Schedule K-1(NR) line 15. TWO DIFFERENT OUTPUTS OF "
                     "THE SAME BLOCK GO TO TWO DIFFERENT PLACES, and getting them crossed is the most "
                     "likely single transcription error on this form."),
     "exceptions": "", "notes": "K-1(NR) line 15's instruction states the concept: 'the difference "
                                "between IRC § 702(a)(8) and A.R.S. § 43-1401(2)'."},
    {"rule_id": "R-AZ165-PART2-GATE", "title": "Part 2 gate: Q.A = Yes OR PTE estimates paid — NOT Q.A alone",
     "rule_type": "conditional", "sort_order": 10,
     "inputs": ["az165_q_a_pte_election", "az165_pte_estimates_paid"], "outputs": ["az165_part2_required"],
     "formula": "part2_required = (question_A == Yes) OR (pte_estimated_payments_made > 0)",
     "description": ("The Part 2 header, verbatim: 'Complete only if the Partnership answered \"Yes\" "
                     "to Question A on page 1, OR ESTIMATED PAYMENTS WERE MADE AND THE PARTNERSHIP IS "
                     "NOT CLAIMING THE PTE ELECTION.' ⚠ A loader that branches on Question A alone "
                     "SUPPRESSES PART 2 FOR EXACTLY THE POPULATION THAT MOST NEEDS IT. W18."),
     "exceptions": ("The second limb is the '$0 return' refund path, which both instruction books "
                    "script LINE BY LINE (two variants on the 120S) and which Pub 713 expects to be "
                    "mainstream in TY2025 because the federal SALT deduction rose from $10,000 to "
                    "$40,000. ⚠ The refund CANNOT be applied to the next year's PTE estimates and "
                    "CANNOT be applied to an owner's liability."),
     "notes": "az_part2_required() implements it."},
    {"rule_id": "R-AZ165-PTE-BASE", "title": "Line 10 = line 8 + line 9 — an EXACT statutory reconstruction",
     "rule_type": "calculation", "sort_order": 11, "inputs": ["az165_l9_separately_stated_items"],
     "outputs": ["AZ165_L10"], "formula": "L10 = L8 + L9, where L8 = L5",
     "description": ("§ 43-1401(2) defines a partnership's Arizona taxable income as Arizona gross "
                     "income adjusted by §§ 43-1021/43-1022 and § 43-1414(A) — that is line 5. "
                     "§ 43-1401(1) EXCLUDED the § 43-1412 ¶1-16 items from Arizona gross income in "
                     "the first place, so line 9 adds them back. Line 8 + line 9 = "
                     "§ 43-1014(B)(1)(a)(ii) exactly. THE FORM IS DOING PRECISELY WHAT THE STATUTE "
                     "SAYS. ⚠ CONTRAST FORM 120S, WHOSE LINE 37 = LINE 1 WITH NOTHING IN BETWEEN."),
     "exceptions": ("⚠ Line 9 is a SINGLE UNDIFFERENTIATED BOX covering SIXTEEN statutory categories "
                    "with no supporting schedule — the largest direct-entry surface on the form and "
                    "the place a § 179 error will hide (W10)."),
     "notes": "The AZDOR note attributes the TY2023+ starting point to 2023 legislation S.B. 1734; "
              "the EFFECT is verified directly from § 43-1014(B)(1)(a)(ii) and § 43-1412."},
    {"rule_id": "R-AZ165-179-ROUTE", "title": "§ 179 enters the PTE base through LINE 9, and its limit is a RULING",
     "rule_type": "routing", "sort_order": 12, "inputs": [], "outputs": ["az_179_route", "az_179_limits"],
     "formula": "AZ_179_PARTNERSHIP_ROUTE == 'Form 165 line 9'; az_179_limits(2025) == 2,500,000 / 4,000,000",
     "description": ("TWO DIFFERENT QUESTIONS, AND ONLY ONE WAS RULED ON. (a) THE LIMIT: campaign "
                     "D-10 ruled Arizona's TY2025 § 179 to $2,500,000 / $4,000,000 on a BROAD reading "
                     "of § 43-105(B)'s OBBBA graft clause — ⚠ A RULING ON AN INTERPRETIVE QUESTION, "
                     "NOT A PUBLISHED ARIZONA FIGURE. The MECHANISM is verified (Arizona has NO § 179 "
                     "modification in any of §§ 43-1021/43-1022/43-1121/43-1122, which enumerate "
                     "EXHAUSTIVELY — 'the rule says no'); the NUMBER is an inference and U3 STAYS "
                     "OPEN AS A FACT. (b) THE ROUTING, which D-10 did not reach: for a PARTNERSHIP "
                     "§ 179 is a SEPARATELY-STATED ITEM under § 43-1412(5), so it enters the Arizona "
                     "PTE base through LINE 9 — not through line 1 and not through Schedule A/B."),
     "exceptions": ("⚠ NEITHER ARIZONA PTE FORM STATES A § 179 FIGURE, so the D-10 ruling is INVISIBLE "
                    "on the entity returns; it shows up only through federal Schedule K amounts and "
                    "the line 9 total. ⚠ FOR AN S CORPORATION THERE IS NO ROUTING QUESTION AT ALL — "
                    "Form 120S line 37 = line 1 = federal Schedule K, already net of federal § 179."),
     "notes": "Form 165 Schedule K-1(NR) Part 1 line 13 confirms the item exists at partner level "
              "('IRC Section 179 expense', routed to Form 140NR line 21)."},
    {"rule_id": "R-AZ165-SHARES", "title": "Lines 11/13/15/17 from Schedule E column (c), six decimals",
     "rule_type": "calculation", "sort_order": 13, "inputs": ["az165_sched_e_rows"],
     "outputs": ["AZ165_L11", "AZ165_L13", "AZ165_L15", "AZ165_L17"],
     "formula": "L11 = E1 + E4; L13 = E2 + E5; L15 = E3; L17 = E7 — each as a 6-decimal ratio",
     "description": ("Verbatim instruction note: 'Enter the amounts from Schedule E on these lines as "
                     "a decimal carried out to 6 digits to the right of the decimal. A partnership "
                     "distribution of 6.54% would be 0.065400. A partnership distribution of 100% "
                     "would be 1.000000.' L11 is resident individuals PLUS resident estates/trusts; "
                     "L13 nonresident individuals PLUS nonresident estates/trusts; L15 part-year "
                     "individuals; L17 everyone who opted out or is ineligible."),
     "exceptions": ("⚠ LOOK-THROUGH OWNERS (grantor trusts, SMLLCs disregarded to an individual) THAT "
                    "DID NOT OPT OUT ARE COUNTED IN E1-E3 — THE INDIVIDUAL ROWS — NOT IN E4-E5. "
                    "Counter-intuitive and easy to get wrong."),
     "notes": "Eligible owners are individuals, estates and trusts only; non-response to the 60-day "
              "opt-out notice means INCLUDED."},
    {"rule_id": "R-AZ165-ALLOC", "title": "Lines 12/14/16/18 = line 10 × the corresponding ratio, and they must cross-foot",
     "rule_type": "calculation", "sort_order": 14,
     "inputs": ["az165_l16a_part_year_resident_portion", "az165_l16b_part_year_nonresident_portion"],
     "outputs": ["AZ165_L12", "AZ165_L14", "AZ165_L16", "AZ165_L18"],
     "formula": "L12 = L10×L11; L14 = L10×L13; L16 = L10×L15; L18 = L10×L17; and L12+L14+L16+L18 == L10",
     "description": ("The cross-foot is PRINTED ON THE FACE: 'NOTE: The total of lines 12, 14, 16 and "
                     "18 must equal the amount reported on line 10.' A second face-printed obligation "
                     "sits at 16A + 16B == 16."),
     "exceptions": "⚠ 16A/16B split by ACTUAL ARIZONA RESIDENCY PERIOD, not by a day count.",
     "notes": "With E8 column (c) == 1.000000 this gives TWO INDEPENDENT PROOF OBLIGATIONS on the same "
              "allocation, both stated on the face rather than merely in the instructions."},
    {"rule_id": "R-AZ165-ZEROFLOOR", "title": "Lines 19 and 21 are floored at zero — a rule the FACE omits",
     "rule_type": "validation", "sort_order": 15, "inputs": [], "outputs": ["AZ165_L19", "AZ165_L21"],
     "formula": "L19 = max(0, L12 + L16A); L21 = max(0, L14 + L16B)",
     "description": ("⚠ THE FLOOR APPEARS ONLY IN THE INSTRUCTIONS: 'Add line 12 and line 16A. Enter "
                     "the total. If the total is less than zero, \"0\", enter \"0\".' THE FACE CARRIES "
                     "NO SUCH NOTE — while FORM 120S PRINTS EXACTLY THE SAME FLOOR ON ITS FACE at "
                     "lines 46 and 48. A real face-vs-instruction divergence and a diagnostic the "
                     "engine must supply (W4)."),
     "exceptions": ("This is the one place Arizona's 'the face governs' convention runs the other way: "
                    "the instruction ADDS a rule the face omits rather than contradicting it, and the "
                    "sister form proves the rule is intended."),
     "notes": "Consistent with Pub 713's observation that a loss-year election is possible but "
              "pointless."},
    {"rule_id": "R-AZ165-RATE", "title": "The 2.5% PTE rate is PRE-PRINTED ON THE FACE, not looked up",
     "rule_type": "calculation", "sort_order": 16, "inputs": [], "outputs": ["AZ165_L20", "AZ165_L24"],
     "formula": "L20 = L19 × 0.0250; L24 = L23 × 0.0250",
     "description": ("Printed at BOTH line 20 and line 24 as 'the PTE tax rate, 2.5% (0.0250)', and "
                     "again on Form 120S lines 47 and 51 — FOUR face confirmations plus Pub 713's "
                     "'For taxable year 2025, the PTE tax rate is 2.5%.' A.R.S. § 43-1014(A) sets it "
                     "BY REFERENCE to 'the highest tax rate prescribed by section 43-1011'."),
     "exceptions": ("⚠ THE § 43-1011 PINPOINT IS UNSUPPORTED (U21): azleg.gov/ars/43/01011.01.htm "
                    "RETURNS A 404 — the only 404 among the fourteen A.R.S. pages cached — and "
                    "01011.htm serves a SUPERSEDED conditional version stamped (L21, Ch. 411, sec. 4) "
                    "whose subsection A stops at paragraph 4 with a 4.50% top bracket while its own "
                    "subsection E refers to paragraphs 6-9 that are absent. THE RATE IS SAFE; ONLY "
                    "THE PROVENANCE CHANGED. Cite the faces and Pub 713, not § 43-1011(A)(9)."),
     "notes": ("PIN THE CONSTANT TO THE FACE. If Arizona's individual rate ever moves, the PTE rate "
               "follows automatically in statute but the FORM will be reprinted — and the form is "
               "what is e-filed.")},
    {"rule_id": "R-AZ165-APPORT", "title": "Line 22 = the Arizona apportionment ratio; 1.0 when question D is Yes",
     "rule_type": "calculation", "sort_order": 17, "inputs": ["az165_q_d_arizona_only",
                                                             "az165_q_f_apportionment_method"],
     "outputs": ["AZ165_L22"],
     "formula": ("L22 = 1.0 if question D == Yes else (Schedule C line C5 for STANDARD, line C3f for "
                 "SALES FACTOR ONLY, or Schedule ACA line 3 for AIR CARRIER)"),
     "description": ("⚠ QUESTION D IS INVERTED RELATIVE TO FORM 120S QUESTION B: here 'Yes' means "
                     "ARIZONA-ONLY, i.e. NOT multistate. The instruction says 'If Line D is \"Yes\", "
                     "enter 1.0'. ⚠ `0.000000` AND BLANK MEAN OPPOSITE THINGS: '0.000000' = NO "
                     "ARIZONA NEXUS; blank or 1.000000 = income sourced ENTIRELY within Arizona. A "
                     "null-vs-zero bug here SILENTLY ZEROES EVERY NONRESIDENT'S ARIZONA INCOME."),
     "exceptions": ("⚠ Schedule ACA's OWN routing list omits Form 165 Part 2 line 22, but the parent "
                    "form's line instruction says 'from Schedule C OR SCHEDULE ACA'. THE PARENT FORM "
                    "CLOSES THE LOOP; the omission is not a prohibition (U12)."),
     "notes": "The same ratio is stamped into Schedule K-1(NR) column (b) 'through Part 6'."},
    {"rule_id": "R-AZ165-DIVISOR", "title": "The apportionment divisor is DYNAMIC: 4, 3, 2, or none",
     "rule_type": "calculation", "sort_order": 18, "inputs": [],
     "outputs": ["AZ165_C4", "AZ165_C5"],
     "formula": ("exclude a factor IFF numerator == 0 AND denominator == 0; divisor = 4 | 3 (property "
                 "or payroll excluded) | 2 (SALES excluded) | none (two excluded: the survivor IS the "
                 "ratio, unweighted)"),
     "description": ("A.A.C. R15-2D-901(B) and the Form 165 instructions. ⚠ A ZERO NUMERATOR OVER A "
                     "POSITIVE DENOMINATOR IS A LIVE ZERO FACTOR, NOT AN EXCLUDED ONE — this is the "
                     "rule most engines get wrong. ⚠ WHEN SALES IS THE EXCLUDED FACTOR THE DIVISOR "
                     "DROPS TO TWO EVEN THOUGH SALES IS DOUBLE-WEIGHTED: the weighting and the "
                     "divisor are NOT tied to each other."),
     "exceptions": ("Caps: property factor may not exceed 1.0; the sales factor may not exceed 2.0 "
                    "under STANDARD and 1.0 under SALES FACTOR ONLY. Rounding: six decimals, with the "
                    "seventh place rounding the sixth UP at five or more. Alternative apportionment "
                    "relief under § 43-1148 requires a letter to the Corporate Income Tax Audit "
                    "Section 60 DAYS BEFORE FILING — RED-DEFERRED."),
     "notes": "Identical engine on Form 120S Schedule A rows A1-A5; the methods are mutually exclusive."},
    {"rule_id": "R-AZ165-MSP", "title": "Schedule MSP: an IRREVOCABLE FIVE-YEAR election on a TIMELY ORIGINAL return",
     "rule_type": "conditional", "sort_order": 19,
     "inputs": ["az165_q_g_msp_included", "az165_q_g_msp_cycle_year", "az165_schc_msp_service_sales"],
     "outputs": ["AZ165_C3B"],
     "formula": "A3 = A1 / A2 (six decimals); qualify if A3 > 0.850000; Part B lands on Schedule C line C3b column A",
     "description": ("A.R.S. § 43-1147(B)/(C). Part A is completed ONLY IN YEAR ONE; alternate "
                     "qualification at A5 (a regionally accredited institution of higher education "
                     "with an Arizona campus of 2,000+ resident students) and A6 (an employer with "
                     "2,000+ Arizona employees deriving 85%+ of sales from support services to such "
                     "an institution). ⚠ THE ONLY STATEFUL MULTI-YEAR ATTRIBUTE ON THESE RETURNS — "
                     "binding for five consecutive taxable years REGARDLESS of whether the taxpayer "
                     "still meets the threshold."),
     "exceptions": ("⚠ TIMELINESS MATTERS HERE AND NOT FOR THE PTE ELECTION — two elections on the "
                    "same return with OPPOSITE timeliness rules (W21). Exits: without department "
                    "permission on acquisition or merger; with permission before the five years "
                    "expire. ⚠ NON-ELECTING service providers leave line C3b BLANK and use C3c."),
     "notes": "Question G carries the Yr 1 - Yr 5 cycle marker; Form 120S question D is the twin."},
    {"rule_id": "R-AZ165-TAX", "title": "Line 25 = line 20 + line 24 — the total PTE tax owed",
     "rule_type": "calculation", "sort_order": 20, "inputs": [], "outputs": ["AZ165_L25"],
     "formula": "L25 = L20 + L24, where L23 = L21 × L22 and L24 = L23 × 0.0250",
     "description": ("Resident and part-year-resident-period income is taxed WITHOUT apportionment "
                     "(line 19 → line 20); nonresident and part-year-nonresident-period income is "
                     "APPORTIONED FIRST (line 21 → × line 22 → line 23 → line 24)."),
     "exceptions": ("⚠ FORM 220/PTE Part B line 5 CITES 'Form 165, line 23' FOR THE ARIZONA TAX "
                    "LIABILITY. Line 23 is an intermediate apportioned base, not a tax. THE INTENDED "
                    "REFERENCE IS LINE 25 — every other entry in that sentence points at a net-tax "
                    "figure. Compute from line 25 and flag (U11 / W20)."),
     "notes": "Form 165 has NO entity-level credit line at all, unlike Form 120S lines 13/15/20."},
    {"rule_id": "R-AZ165-PAYMENTS", "title": "Payments block: lines 29, 31, 32, 33",
     "rule_type": "calculation", "sort_order": 21,
     "inputs": ["az165_l26_extension_payment", "az165_l27_estimated_tax_payments",
               "az165_l28_amended_payments", "az165_l30_prior_overpayments"],
     "outputs": ["AZ165_L29", "AZ165_L31", "AZ165_L32", "AZ165_L33"],
     "formula": "L29 = L26+L27+L28; L31 = L29 − L30; L32 = max(0, L25 − L31); L33 = max(0, L31 − L25)",
     "description": "Payment arithmetic exactly as printed.",
     "exceptions": ("⚠ LINE 26 IS NOT AUTO-DERIVED FROM SCHEDULE F COLUMN (c): line 27 explicitly "
                    "imports F7(b) but line 26's instruction never cites F7(c). Auto-linking invents "
                    "a relationship the form does not state (W6)."),
     "notes": "EFT is mandatory at a $500 anticipated liability, with a 5% penalty under "
              "§ 42-1125(O). ⚠ A FOREIGN BANK ACCOUNT MUST USE ACH CREDIT — AZDOR does not accept ACH "
              "Debit from one."},
    {"rule_id": "R-AZ165-DUE-REFUND", "title": "Lines 37/38/40 — and line 37 SKIPS line 33",
     "rule_type": "calculation", "sort_order": 22,
     "inputs": ["az165_l34_penalty_and_interest", "az165_l35_estimated_underpayment_penalty",
               "az165_l39_overpayment_applied_next_year"],
     "outputs": ["AZ165_L37", "AZ165_L38", "AZ165_L40"],
     "formula": ("L37 = L32 + L34 + L35 + L36 (⚠ SKIPS L33); L38 = L33 − (L34+L35+L36), entered as a "
                 "POSITIVE number — AND IF THE DIFFERENCE IS NEGATIVE IT GOES TO L37 AS A POSITIVE "
                 "NUMBER INSTEAD; L40 = L38 − L39"),
     "description": ("Line 37 instruction verbatim: 'Add lines 32 and 34 through 36.' Line 38 "
                     "verbatim: 'If the partnership has an overpayment of tax on line 33, subtract "
                     "the total of lines 34 through 36 from line 33. Enter a positive number on line "
                     "38. This is the total overpayment. IF THE DIFFERENCE IS NEGATIVE, ENTER THE "
                     "DIFFERENCE AS A POSITIVE NUMBER ON LINE 37.' A SIGN-FLIP CROSSOVER between the "
                     "two totals."),
     "exceptions": ("⚠ LINE 39 PRINTS A STALE YEAR (face '2025', instruction '2026', and Form 120S "
                    "line 35 correctly says 2026). Transcribe as printed; compute 2026 (AZ-D1 / W5)."),
     "notes": "Overpayments may be carried to the next year's PTE estimates for TY2023+ (Pub 713); any "
              "unapplied balance is refunded."},
    {"rule_id": "R-AZ165-INFO-PEN", "title": "The information-return penalty and the PTE election are mutually exclusive",
     "rule_type": "conditional", "sort_order": 23,
     "inputs": ["az165_q_a_pte_election", "az165_l7_information_return_penalty"],
     "outputs": ["AZ165_L7", "AZ165_L36"],
     "formula": "if question A == Yes: L7 == 0 and L36 == 0; else L7 = min(100 × months_late, 500)",
     "description": ("'Partnerships that did not make the PTE election, this is an information "
                     "return... subject to a penalty of $100 per month or fraction of a month during "
                     "which the failure continues, up to a maximum of $500. ... Partnerships that "
                     "made the PTE election, this is not an information return. Continue to Part 2, "
                     "line 8.' Pub 713 was asked directly and answered 'No'. Line 36 simply imports "
                     "line 7."),
     "exceptions": "", "notes": "Form 120S carries the same rule at its line 32."},
    {"rule_id": "R-AZ165-PENALTY", "title": "The Arizona penalty set, and the 25% combined cap",
     "rule_type": "calculation", "sort_order": 24, "inputs": [], "outputs": ["AZ165_L34"],
     "formula": ("late filing 4.5%/month capped 25%; extension underpayment 0.5% per 30-day period "
                 "capped 25%; late payment 0.5%/month capped 10%; EFT failure 5%; COMBINED CAP 25%"),
     "description": ("The extension underpayment penalty and the late payment penalty are MUTUALLY "
                     "EXCLUSIVE. The extension penalty triggers when less than 90% of the tax "
                     "liability was paid by the ORIGINAL due date. Interest runs on line 25 from the "
                     "original due date at the prevailing rate."),
     "exceptions": ("VOLUNTARY-AMENDMENT RELIEF: no late payment penalty if the taxpayer voluntarily "
                    "files an amended return and pays the additional tax with it — unless under audit "
                    "or filing on the department's demand (AZDOR ruling CTR 09-1, unpulled). "
                    "⚠ ESTIMATED-TAX PENALTIES ARE NOT ASSESSED when the Arizona liability due on the "
                    "return is less than $1,000 (§ 43-581(E)(2)), and there is NO overpayment penalty."),
     "notes": ("⚠ ARIZONA'S TWO 4.5%s ARE UNRELATED: this LATE-FILING penalty is 4.5% and is correct; "
               "Form 165PA line 13's 4.5% TAX RATE is stale. Do not let a search-and-replace conflate "
               "them.")},
    {"rule_id": "R-AZ165-EST-PAY", "title": "$150,000 estimated-payment test: STRICTLY GREATER, four installments",
     "rule_type": "conditional", "sort_order": 25, "inputs": ["az165_prior_year_taxable_income"],
     "outputs": ["az165_estimated_payments_required"],
     "formula": "required = prior_year_taxable_income > 150000  (⚠ `>` NOT `>=`)",
     "description": ("A.R.S. § 43-581(C): '...whose taxable income for the taxable year EXCEEDS "
                     "$150,000 in the preceding taxable year shall make payments of estimated tax...' "
                     "SEVEN INDEPENDENT SOURCES SAY 'EXCEEDS' — the statute, the Form 165 "
                     "instructions, the Form 120S instructions, the Form 220/PTE instructions (×2), "
                     "the Form 120/PTE-W instructions (×2), Booklet 120/165ES (×3) and Pub 713's "
                     "narrative. EXACTLY ONE SOURCE SAYS 'OR MORE': a single Pub 713 FAQ answer — and "
                     "Pub 713's own FAQ lead-in offers a THIRD phrasing, 'meets or exceeds'. PUB 713 "
                     "IS INTERNALLY INCONSISTENT THREE WAYS AND CANNOT DISPLACE THE STATUTE. AN "
                     "ENTITY AT EXACTLY $150,000 IS OUT."),
     "exceptions": ("⚠⚠ THE FOURTH INSTALLMENT IS THE 15TH DAY OF THE **1ST** MONTH AFTER THE CLOSE OF "
                    "THE TAXABLE YEAR, NOT THE 12TH MONTH — April 15, June 15, September 15 and "
                    "January 15 for a calendar-year filer. Form 220/PTE line 7 prints the CORPORATE "
                    "pattern (4th/6th/9th/12th) on the FACE and appends 'PTE's see instructions'. A "
                    "loader reading the face alone puts the fourth installment THREE MONTHS EARLY "
                    "(W17). Required annual payment = THE SMALLER OF 90% of the current year's "
                    "liability or 100% of the prior year's — a SAFE HARBOUR framing, not a minimum."),
     "notes": ("⚠ AN EARLIER VERIFICATION PASS FLIPPED THIS BOUNDARY TO 'OR MORE' AND A LATER ONE "
               "CAUGHT IT; conformity/az_conformity.md §4 and §12-H still carry the wrong version and "
               "need amending. Vintage-clean: § 43-581 is amended by neither Ch. 182 nor Ch. 140.")},
    {"rule_id": "R-AZ165-EST-BASIS", "title": "WHICH taxable income: a RULING on a contested question (D-12 A1, refined)",
     "rule_type": "classification", "sort_order": 26, "inputs": ["az165_prior_year_taxable_income"],
     "outputs": ["az_est_measurement_basis", "az_est_measurement_figure"],
     "formula": ("AZ_EST_MEASUREMENT_BASIS == 'statutory_bare_taxable_income' (the SOURCE leg) "
                 "RESOLVES TO 'arizona_taxable_income' per A.R.S. § 43-1401(2) (the NUMBER leg) = "
                 "PRIOR-YEAR Form 165 line 5 — ⚠ NOT line 10"),
     "description": ("⚠⚠ AZDOR PRINTS **FOUR** DIFFERENT MEASUREMENT BASES AND **FOUR OF SIX "
                     "DOCUMENTS CONTRADICT THEMSELVES INTERNALLY**: (1) bare 'taxable income' — the "
                     "statute, both entity instruction books, one Form 120/PTE-W sentence and the Pub "
                     "713 narrative; (2) 'ARIZONA taxable income' — Form 220/PTE ×2, another "
                     "120/PTE-W sentence, the Pub 713 FAQ; (3) 'PTE INCOME' — BOTH entity instruction "
                     "books; (4) 'TOTAL taxable income' — Booklet 120/165ES. THIS IS NOT ACADEMIC: an "
                     "entity with $1,000,000 of Arizona taxable income and 10% consenting ownership "
                     "has $100,000 of PTE income — IN under base 2, OUT under base 3, FROM READINGS "
                     "PRINTED IN THE SAME BOOK — and it decides whether the Form 220/PTE underpayment "
                     "penalty applies. CAMPAIGN D-12 A1 RULED THE STATUTE'S BARE 'TAXABLE INCOME', as "
                     "the only one of the four with controlling authority behind it. ⚠⚠ REFINED THE "
                     "SAME SESSION — THE RULING NAMED A SOURCE WITHOUT NAMING A NUMBER, AND "
                     "ESTIMATED-PAYMENT AND FORM 220/PTE PENALTY LOGIC NEED A FIGURE. Title 43 "
                     "chapter 14 DEFINES the statute's term at § 43-1401(2) as 'ARIZONA TAXABLE "
                     "INCOME' — 'its Arizona gross income adjusted by the modifications specified in "
                     "sections 43-1021 and 43-1022 and section 43-1414, subsection A' — so the ruled "
                     "source RESOLVES INTO base 2. RULED 2026-08-19: COMPUTE ARIZONA TAXABLE INCOME. "
                     "On Form 165 that is PRIOR-YEAR LINE 5. ⚠ NOT LINE 10: line 8 (= line 5) PLUS "
                     "line 9 reconstructs § 43-1014(B)(1)(a)(ii), so § 43-1401(2) ALONE is line 5, and "
                     "line 10 — the larger PTE base — would be a FIFTH reading no AZDOR document "
                     "prints."),
     "exceptions": ("⚠⚠ THE REFINEMENT NARROWS WHAT WE COMPUTE; IT DOES NOT CLOSE THE QUESTION. "
                    "STILL RECORDED AS A RULING ON A CONTESTED QUESTION, **NOT A PUBLISHED AZDOR "
                    "POSITION**. [UNVERIFIED] U19 STAYS OPEN AS A MATTER OF FACT, all four candidate "
                    "bases stay on the record in AZ_EST_MEASUREMENT_BASIS_CANDIDATES with the three "
                    "losers explicitly NOT REFUTED, and D_AZ_U19_150K_BASIS still tells the preparer "
                    "the threshold determination is PROVISIONAL. Settled by an AZDOR ruling, "
                    "procedure, or written Corporate Income Tax section response."),
     "notes": ("ENCODED AS A SINGLE NAMED CONSTANT (plus its RESOLVES_TO second leg) so a DOR answer "
               "changes ONE THING. ⚠ A DIFFERENT question from the BOUNDARY, which is settled and "
               "needed no ruling. ⚠⚠ SECOND-ORDER GAP: § 43-1401 is a chapter-14 PARTNERSHIP "
               "definitions section with NO S-corp analogue, while § 43-581(C) reaches both entity "
               "types — see AZ_EST_MEASUREMENT_SCORP_GAP and D_AZ120S_EST_BASIS_NO_ANALOGUE.")},
    {"rule_id": "R-AZ165-1021-15", "title": "§ 43-1021(15): OWNER LEVEL ONLY — the entity half has no line",
     "rule_type": "classification", "sort_order": 27, "inputs": [],
     "outputs": ["az_entity_level_pte_addback"],
     "formula": "AZ_1021_15_ENTITY_ADDBACK_BUILT == False; AZ_1021_15_OWNER_ADDBACK_BUILT == True",
     "description": ("⚠⚠ CAMPAIGN RULING D-12 A3: BUILD TO THE FORM. The statute's final sentence "
                     "says the PTE-tax add-back 'shall be reflected in the partner's or shareholder's "
                     "Arizona gross income AND THE PARTNERSHIP'S OR S CORPORATION'S ARIZONA TAXABLE "
                     "INCOME'. The OWNER half is fully implemented on all four K-1s. THE ENTITY HALF "
                     "HAS NO LINE: Form 165 Schedule A has four rows, the page-6 A4 worksheet is a "
                     "CLOSED list of three items, THERE IS NO FREE-TEXT 'OTHER' ROW ANYWHERE ON PAGE "
                     "6, line 9 is § 43-1412 ¶1-16 which contains no PTE add-back, and Form 120S has "
                     "no additions schedule at all. Pub 713 answers a practitioner question asking "
                     "exactly this and says OWNER LEVEL ONLY. Same shape as D-10 ruling 2 (Missouri) "
                     "and D-11 A1 (Colorado § 174A): WHERE THE FORM CANNOT EXPRESS A POSITION, THE "
                     "FORM GOVERNS."),
     "exceptions": ("⚠ THE CASH-BASIS CIRCULARITY IS REAL AND IS RECORDED RATHER THAN FIXED. The PTE "
                    "tax is deductible federally in the year PAID and electing entities are almost "
                    "universally cash-basis, so line 1 is ALREADY NET of the Arizona PTE tax paid "
                    "during the year and the PTE base is UNDERSTATED BY THE PTE TAX ITSELF. That is "
                    "what the statute's second sentence exists to close, and the forms do not close "
                    "it. [UNVERIFIED] U5 stays open."),
     "notes": ("⚠ AZDOR's published answer does not address the entity clause AT ALL, and its closing "
               "words ('reports this amount on his/her individual FEDERAL income tax return') are "
               "themselves confused — the add-back is an ARIZONA modification.")},
    {"rule_id": "R-AZ165-SCHE-XFOOT", "title": "Schedule E must cross-foot to 1.000000 — printed on the FACE",
     "rule_type": "validation", "sort_order": 28, "inputs": ["az165_sched_e_rows"],
     "outputs": ["AZ165_E8"],
     "formula": "E6 = E1+E2+E3+E4+E5; E8 = E6 + E7; E8 column (c) == 1.000000",
     "description": ("'E8 Total partner count and total partnership ownership share. Add lines E6 and "
                     "E7 in columns (b) and (c). Enter the totals. (Column (c) should equal "
                     "1.000000.)' A HARD CROSS-FOOT, ON THE FACE."),
     "exceptions": "Gate: 'Partnerships making the PTE election, complete Schedule E. All others, skip "
                   "to Schedule G.'",
     "notes": "Together with the Part 2 cross-foot this gives two independent proof obligations."},
    {"rule_id": "R-AZ165-SCHD", "title": "Schedule D column (h) = line 5 × column (g), with SPECIAL ALLOCATIONS honoured",
     "rule_type": "calculation", "sort_order": 29, "inputs": ["az165_partner_rows"],
     "outputs": ["AZ165_SCHD_H"],
     "formula": "col(h) = L5 × col(g) per partner; sum(col(g)) == 1.000000",
     "description": ("Column (h) is 'the partner's distributive share of the partnership income and "
                     "expenses ADJUSTED TO THE ARIZONA BASIS (from page 1, line 5)'. ⚠ 'NOTE: If the "
                     "partnership operating agreement specifies partnership proceeds are to be "
                     "distributed on the basis of a SPECIAL ALLOCATION, complete columns (g) and (h) "
                     "using that allocation method.' Pub 713 carries a worked example. THERE IS NO "
                     "S-CORPORATION ANALOGUE — Pub 713: 'An S Corporation may not allocate its income "
                     "and loss items to its shareholders using a special allocation.'"),
     "exceptions": ("⚠ FOR AN IRA PARTNER, ENTER THE CUSTODIAN'S TIN, not the TIN of the person for "
                    "whom the IRA is maintained; do not truncate. ⚠ For a look-through partner that "
                    "did not opt out, enter only the BENEFICIAL OWNER'S information and residency. "
                    "⚠ Form 120S Schedule B column (h) points at LINE 1, not line 5 — the same column "
                    "position, a different source line."),
     "notes": "More than 10 partners → additional schedules."},
    {"rule_id": "R-AZ165-K1-SPLIT", "title": "K-1 routing by residency AND entity type; a part-year owner gets TWO",
     "rule_type": "routing", "sort_order": 30, "inputs": ["az165_partner_rows"],
     "outputs": ["az165_k1_documents"],
     "formula": ("resident/part-year individuals and resident estates/trusts → Schedule K-1; ALL "
                 "corporate partners, ALL partnership partners and all nonresidents → Schedule "
                 "K-1(NR); a PART-YEAR owner receives BOTH"),
     "description": ("Both faces state it: 'Corporate partners and partners that are partnerships must "
                     "use Form 165 Schedule K-1(NR).' Pub 713 footnote 2 adds the part-year rule — "
                     "one K-1 for the resident period AND one K-1(NR) for the nonresident period. "
                     "⚠ A PER-OWNER DOCUMENT MULTIPLIER THE APP MUST HANDLE."),
     "exceptions": ("⚠ K-1 line 3 — the resident partner's share of the Arizona basis adjustment — "
                    "carries NO SBI DESTINATION (U6 / W13), while lines 12-15 of the SAME document "
                    "use a four-way route including the SBI forms. The reason is structural: line 3 "
                    "routes to Form 140 PAGE 1 lines 16/27 (main form, two-way) while the SBI-bearing "
                    "lines route to PAGE 5 line P (a one-way other-additions schedule) — line 3 was "
                    "never an instance of that template. DO NOT GUESS A DESTINATION."),
     "notes": ("K-1 line 1 = Form 165 line 6; line 2 = the partner's profit/loss percentage; line 3 = "
               "line 1 × line 2. K-1(NR) line 15 = the same line 6 figure, in three columns.")},
    {"rule_id": "R-AZ165-K1NR-COL", "title": "K-1(NR) column (c) = column (a) × column (b), on every line",
     "rule_type": "calculation", "sort_order": 31, "inputs": [], "outputs": ["az165_k1nr_col_c"],
     "formula": "col(c) = col(a) × col(b) for every line; col(b) = the apportionment ratio",
     "description": ("The Schedule C instruction stamps the ratio into column (b) 'through Part 6, "
                     "column (b)' — SIX different parts of the schedule. Part 1 is a re-ordered "
                     "federal Schedule K-1 with a pre-printed Form 140NR destination column."),
     "exceptions": ("⚠ LINES 10 (guaranteed payments) AND 14 (other deductions) HAVE NO PRINTED "
                    "DESTINATION while every other income line does — a printed-form gap verified "
                    "against the face (U7 / AZ-D7). The emitter must still print the columns. "
                    "⚠ Part 7's net-LTCG aggregation is line 9 PLUS line 11 (§ 1231), a combination "
                    "rule the RESIDENT K-1's Part 6 does not carry."),
     "notes": ("⚠ Passive-loss limitation: a nonresident with a federal passive activity loss must NOT "
               "begin from column (c). § 179 is limited to the Arizona portion of the amount deducted "
               "on federal Schedule E.")},
    {"rule_id": "R-AZ165-K1-CREDIT", "title": "K-1 PTE credit: ONE credit line, FOUR add-back lines, keyed to LIABILITY",
     "rule_type": "calculation", "sort_order": 32, "inputs": [], "outputs": ["az165_k1_pte_credit"],
     "formula": ("K-1 line 11 / K-1(NR) line 23 = the partner's pro-rata share of line 25, allocated "
                 "from the LIABILITY; lines 12-15 / 24-27 = the four add-backs"),
     "description": ("A.R.S. § 43-1077: nonrefundable, FIVE-YEAR carryforward, and a prior-year "
                     "carryforward may be used up before the current-year credit. Delivered on "
                     "ARIZONA Form 355 — Part 1 LINE 1 for a partnership, LINE 2 for an S corporation "
                     "— or, for estates and trusts, Form 141AZ line 19. ⚠ FOUR ADD-BACK LINES SPLIT "
                     "ON TWO AXES: Arizona vs OTHER-STATE, and prior-year vs current-year, because "
                     "the add-back is keyed to tax PAID DURING calendar 2025."),
     "exceptions": ("⚠ THE STATUTE KEYS THE CREDIT TO TAX **PAID** (§ 43-1077(B)) while line 25 "
                    "computes tax OWED, and NO SCHEDULE RECONCILES OWED TO PAID BEFORE THE K-1s ARE "
                    "CUT. Pub 713's own Addendum #1 example allocates from the LIABILITY, so that is "
                    "the default, WITH A DIAGNOSTIC when payments fall short (U9 / W19). Backstop: "
                    "§ 43-1014(B)(2) lets AZDOR collect from the OWNERS if the entity does not pay. "
                    "⚠ A PARTNERSHIP THAT DID NOT ELECT THIS YEAR MAY STILL HAVE TO ISSUE PART 7 "
                    "LINES 12/14 — Part 7's gate reaches 'this year OR FOR A PRIOR YEAR'."),
     "notes": AZ_FORM_355_COLLISION_NOTE},
    {"rule_id": "R-AZ165-TIERED", "title": "The tiered-partnership loop closes through the page-6 A4/B5 worksheets",
     "rule_type": "routing", "sort_order": 33,
     "inputs": ["az165_a4a_positive_partnership_adjustment"], "outputs": ["AZ165_A4", "AZ165_B5"],
     "formula": ("received 165 Sch. K-1(NR) line 15 COLUMN (a): positive → page-6 line A4-A; negative "
                 "→ page-6 line B5-A"),
     "description": ("⚠ COLUMN (a), NOT COLUMN (c): the upper-tier partnership takes the "
                     "UNAPPORTIONED distributive-share amount and RE-APPORTIONS AT ITS OWN LEVEL. "
                     "More than one K-1(NR) received → total the line 15 column (a) amounts. ⚠ A "
                     "lower-tier entity CANNOT pass the PTE credit up to an entity owner (Pub 713: "
                     "'No. Only individuals, estates, or trusts ... may participate'), though it may "
                     "make its own election for its own eligible owners; on the form an upper-tier "
                     "partnership partner is an 'O' in Schedule D column (f) and lands in E7."),
     "exceptions": ("⚠ A SEPARATE TRIGGER LIVES IN THE SAME WORKSHEET INSTRUCTION: if the partnership "
                    "received a FORM 165PA Schedule K-1(NR) with a POSITIVE line 3, it must FILE AN "
                    "AMENDED FORM 165 carrying that amount to line A4, and reissue amended Schedules "
                    "K-1 and K-1(NR) to the partners. THIS IS AN INPUT AND IT IS MODELLED EVEN THOUGH "
                    "COMPUTING A 165PA IS RED-DEFERRED."),
     "notes": ""},
    {"rule_id": "R-AZ165-ELECTION", "title": "The PTE election is ANNUAL, not binding, and needs no timeliness",
     "rule_type": "conditional", "sort_order": 34, "inputs": ["az165_q_a_pte_election"],
     "outputs": ["az165_election_state"],
     "formula": ("election = filing the return with question A = Yes; revocation = an amended return "
                 "with question A = No; both available within the FOUR-YEAR statute of limitations"),
     "description": ("A.R.S. § 43-1014(A): 'The election under this subsection is made by filing the "
                     "business's return under this title.' NOTHING makes it binding on succeeding "
                     "years — contrast § 43-1126(C), which DOES say the federal S election 'is "
                     "effective for the taxable year for which it is made and for all succeeding "
                     "taxable years'. THE DRAFTERS KNEW HOW TO WRITE A CARRY-FORWARD ELECTION AND DID "
                     "NOT DO SO HERE. ⚠ THE TIMELY-FILING REQUIREMENT WAS STRUCK RETROACTIVELY TO "
                     "TY2021 by S.B. 1274 = Laws 2025 Ch. 182 Sec. 6, with retroactivity at Sec. 9(A)."),
     "exceptions": ("⚠⚠ THE STALE-LAW TRAP: Booklet 120/165ES, posted under AZDOR's 2025 row, still "
                    "says 'This election must be made by the S Corporation no later than the due date "
                    "or extended due date of its return.' Its /ModDate is 2024-11-19 and it is headed "
                    "'2024 CORPORATE INCOME TAX HIGHLIGHTS' — SIX MONTHS BEFORE THE REPEAL. USE THAT "
                    "BOOKLET FOR VOUCHERS ONLY. ⚠ Both the election AND its revocation are "
                    "N-OWNER-RETURN EVENTS: one entity amendment cascades to every consenting owner, "
                    "each of whom must amend to claim — or to remove — the PTE credit."),
     "notes": ("Eligible = individuals, estates, trusts. NON-RESPONSE TO THE 60-DAY OPT-OUT NOTICE "
               "MEANS INCLUDED. A final-year election is allowed; a loss-year election is allowed but "
               "pointless; an owner may participate in more than one entity's election.")},
    {"rule_id": "R-AZ165-ZERORETURN", "title": "The '$0 return' refund path — a scripted, high-frequency TY2025 filing",
     "rule_type": "conditional", "sort_order": 35, "inputs": ["az165_pte_estimates_paid"],
     "outputs": ["az165_zero_return"],
     "formula": "question A = No AND pte_estimates_paid > 0 → complete Part 2 with zeros and refund the estimates",
     "description": ("Both instruction books carry a LINE-BY-LINE FILING RECIPE, not advisory prose, "
                     "and Pub 713 frames it explicitly around the federal SALT deduction rising from "
                     "$10,000 to $40,000 in 2025. THE MOST LIKELY REAL-WORLD ARIZONA PTE SCENARIO FOR "
                     "TY2025."),
     "exceptions": ("⚠ THE REFUND CANNOT BE APPLIED TO THE NEXT YEAR'S PTE ESTIMATED TAX AND CANNOT BE "
                    "APPLIED TO AN OWNER'S LIABILITY — it comes back to the ENTITY as cash. ⚠ TWO "
                    "VARIANTS EXIST ON FORM 120S (not subject to Arizona income tax / subject to it) "
                    "and the second runs lines 19-26 differently."),
     "notes": "This is why Part 2 cannot be gated on question A alone (W18)."},
    {"rule_id": "R-AZ165-COMPOSITE", "title": "Composite Form 140NR: opted-out owners only, minimum TEN participants",
     "rule_type": "validation", "sort_order": 36, "inputs": ["az165_q_l_composite_return"],
     "outputs": ["az165_composite_valid"],
     "formula": "composite_allowed = all participants opted out AND participant_count >= 10",
     "description": ("'The Arizona Department of Revenue will accept a composite return on Arizona "
                     "Form 140NR for qualifying nonresident individual partners of a partnership that "
                     "OPTED OUT of the partnership's PTE election. NOTE: A composite return cannot be "
                     "filed with fewer than TEN participating members. A partnership making the PTE "
                     "election CANNOT file a composite return on behalf of its nonresident partners "
                     "that did NOT opt out.' AZDOR ruling ITR 16-2."),
     "exceptions": ("⚠ PAYMENT PLUMBING IS DELIBERATELY SEPARATED: the composite extension is FORM "
                    "204 (not 120/165EXT), composite estimates are FORM 140ES (not 120/165ES), and "
                    "Pub 713 says composite payments CANNOT be converted to PTE estimated payments."),
     "notes": "The composite return itself is an INDIVIDUAL-module artifact and is RED-DEFERRED; for "
              "this wave only the checkbox and these two validations are in scope."},
    {"rule_id": "R-AZ165-EFILE", "title": "E-file is MANDATORY, with a closed exemption list that keys off FEDERAL status",
     "rule_type": "validation", "sort_order": 37, "inputs": [], "outputs": ["az165_efile_required"],
     "formula": "efile_required unless one of the seven printed exemptions applies",
     "description": ("A.R.S. § 43-323(F) and the statement printed ON THE FACE above the declaration: "
                     "'This form must be e-filed unless the partnership has a waiver or is exempt "
                     "from e-filing.' ⚠ FOUR OF THE SEVEN EXEMPTIONS KEY OFF FEDERAL STATUS, so the "
                     "app cannot decide Arizona e-file eligibility without knowing the FEDERAL filing "
                     "posture — a GATE-2 INGEST DEPENDENCY for delvio-tax, not an RS spec item."),
     "exceptions": ("⚠ A 2026 SHORT-PERIOD RETURN FILED ON THE 2025 FORM MUST BE PAPER-FILED — a hard "
                    "e-file block that must produce a RED diagnostic, not a silent e-file attempt. "
                    "⚠ THE 246 MB / ~66,054 K-1 CEILING forces paper too, with an OPTICAL-MEDIA "
                    "(CD/DVD/flash, Excel) alternative THAT EXISTS ONLY ON THE PARTNERSHIP SIDE — "
                    "Form 120S's book says paper-filing S corporations must submit K-1s BY PAPER. Do "
                    "not port it. ⚠ Waivers are annual, renewable once, on Form 292 (unpulled, U15)."),
     "notes": ("Do NOT enclose federal Schedules K-2/K-3 or the § 743(b) statement. Rejections: "
               "azefile@azdor.gov, quoting the Arizona submission ID and the form type.")},
    {"rule_id": "R-AZ165-165PA", "title": "Form 165PA is RED-DEFERRED — do not pick a rate",
     "rule_type": "routing", "sort_order": 38, "inputs": ["az165_q_j_irs_adjustments"],
     "outputs": ["az165_165pa_required"],
     "formula": "az_165pa_rate() RAISES ArizonaDeferredFormError",
     "description": AZ_165PA_CONFLICT,
     "exceptions": ("⚠ ONE 165PA OUTPUT STILL REACHES FORM 165 WHILE 165PA ITSELF IS DEFERRED: a "
                    "RECEIVED Form 165PA Schedule K-1(NR) with a positive line 3 requires an AMENDED "
                    "Form 165 with that amount on page-6 line A4. That input IS modelled. ⚠ The three "
                    "165PA companion schedules were never downloaded (U13)."),
     "notes": AZ_165PA_SYLLOGISM + " " + AZ_165PA_TWO_45S_WARNING},
]

AZ165_RULE_LINKS: list[tuple] = [
    ("R-AZ165-CONFORM", "AZ_HB4168_2026_CH140", "primary", "§ 43-105(B) as amended by Ch. 140 Sec. 12"),
    ("R-AZ165-CONFORM", "AZ_2025_FORM_165_INSTR", "secondary",
     "the reissued book adds NO conformity discussion — the absence is the finding"),
    ("R-AZ165-168N-NEG", "AZ_HB4168_2026_CH140", "primary",
     "Secs. 14 and 22 create the § 168(n) add-backs FOR TY2026; Sec. 35(B) confirms the date"),
    ("R-AZ165-168N-NEG", "AZ_ARS_43_1021", "primary", "azleg still serves the pre-Ch.140 text ending at ¶16"),
    ("R-AZ165-P1-ADD", "AZ_2025_FORM_165", "primary", "Schedule A rows A1-A4 as printed on the face"),
    ("R-AZ165-P1-ADD", "AZ_2025_FORM_165_INSTR", "implementation", "the A2 NET rule and the page-6 worksheets"),
    ("R-AZ165-P1-ADD", "AZ_ARS_43_1021", "primary", "§ 43-1021(11), the depreciation add-back behind A1"),
    ("R-AZ165-P1-SUB", "AZ_2025_FORM_165", "primary", "Schedule B rows B1-B5 as printed on the face"),
    ("R-AZ165-P1-SUB", "AZ_2025_FORM_165_INSTR", "implementation", "the B2 1999-compliance condition and ITR 06-1"),
    ("R-AZ165-P1-SUB", "AZ_ARS_43_1022", "primary", "§ 43-1022(17)(e) and (18) — the seeded Tier-1 anchor"),
    ("R-AZ165-DEPR-B1", "AZ_2025_FORM_165_INSTR", "primary", "the five-tier line B1 instruction, verbatim"),
    ("R-AZ165-DEPR-B1", "AZ_ARS_43_1022", "primary", "§ 43-1022(17)(e), the rule the final tier restates"),
    ("R-AZ165-BONUS-IND", "AZ_ARS_43_1022", "primary", "individuals CONFORM to § 168(k)"),
    ("R-AZ165-BONUS-IND", "AZ_ARS_43_1122", "secondary", "corporations DECOUPLE — the rule Form 165 does NOT apply"),
    ("R-AZ165-BONUS-IND", "AZ_ARS_43_1401_1412", "primary",
     "§ 43-1401(2) builds a partnership's Arizona taxable income from the INDIVIDUAL sections"),
    ("R-AZ165-A4-CORP", "AZ_2025_165_SCHK1NR", "primary", "the line 15 corporate-partner routing, verbatim"),
    ("R-AZ165-A4-CORP", "AZ_ARS_43_1122", "primary", "§ 43-1122(20), the elect-out rule the corporate partner is under"),
    ("R-AZ165-A4-CORP", "AZ_2025_FORM_165_INSTR", "implementation", "line B1 computes on the INDIVIDUAL basis"),
    ("R-AZ165-L5", "AZ_2025_FORM_165", "primary", "line 5 as printed"),
    ("R-AZ165-L6", "AZ_2025_FORM_165", "primary", "line 6 as printed — the only number that leaves Part 1"),
    ("R-AZ165-L6", "AZ_2025_165_SCHK1", "implementation", "K-1 line 1 imports it"),
    ("R-AZ165-L6", "AZ_2025_165_SCHK1NR", "implementation", "K-1(NR) line 15 imports it"),
    ("R-AZ165-PART2-GATE", "AZ_2025_FORM_165", "primary", "the Part 2 header, verbatim"),
    ("R-AZ165-PART2-GATE", "AZ_2025_PUB_713", "secondary", "the SALT-driven '$0 return' scenario"),
    ("R-AZ165-PTE-BASE", "AZ_ARS_43_1014", "primary", "§ 43-1014(B)(1)(a)(ii), the partnership base"),
    ("R-AZ165-PTE-BASE", "AZ_ARS_43_1401_1412", "primary", "§ 43-1401(1)-(2) and § 43-1412 ¶1-16"),
    ("R-AZ165-PTE-BASE", "AZ_2025_FORM_165_INSTR", "implementation", "the line 9 PTE-base note"),
    ("R-AZ165-179-ROUTE", "AZ_ARS_43_1401_1412", "primary", "§ 43-1412(5) makes § 179 separately stated"),
    ("R-AZ165-179-ROUTE", "AZ_HB4168_2026_CH140", "interpretive",
     "§ 43-105(B)'s OBBBA graft clause is the textual hook D-10's broad reading rests on"),
    ("R-AZ165-SHARES", "AZ_2025_FORM_165", "primary", "Schedule E rows E1-E7 and Part 2 lines 11/13/15/17"),
    ("R-AZ165-SHARES", "AZ_ARS_43_1014", "primary", "§ 43-1014(C)-(D), eligibility and the opt-out"),
    ("R-AZ165-ALLOC", "AZ_2025_FORM_165", "primary", "lines 12/14/16/18 and the face-printed cross-foot"),
    ("R-AZ165-ZEROFLOOR", "AZ_2025_FORM_165_INSTR", "primary", "the floor, stated only here"),
    ("R-AZ165-ZEROFLOOR", "AZ_2025_FORM_120S", "secondary",
     "the sister form PRINTS the same floor on its face at lines 46 and 48"),
    ("R-AZ165-RATE", "AZ_2025_FORM_165", "primary", "2.5% (0.0250) pre-printed at lines 20 and 24"),
    ("R-AZ165-RATE", "AZ_ARS_43_1014", "primary", "§ 43-1014(A) sets the rate BY REFERENCE"),
    ("R-AZ165-RATE", "AZ_2025_PUB_713", "secondary", "'For taxable year 2025, the PTE tax rate is 2.5%.'"),
    ("R-AZ165-APPORT", "AZ_2025_FORM_165", "primary", "line 22 and the Schedule C nexus note"),
    ("R-AZ165-APPORT", "AZ_2025_SCH_MSP_ACA", "primary", "Schedule ACA line 3 is the air-carrier alternative"),
    ("R-AZ165-DIVISOR", "AZ_2025_FORM_165_INSTR", "primary", "the factor-exclusion rule and A.A.C. R15-2D-901(B)"),
    ("R-AZ165-MSP", "AZ_ARS_43_1147_MSP", "primary", "§ 43-1147(C), the five-year lock and its two exits"),
    ("R-AZ165-MSP", "AZ_2025_SCH_MSP_ACA", "primary", "Schedule MSP Parts A and B as printed"),
    ("R-AZ165-TAX", "AZ_2025_FORM_165", "primary", "lines 19-25 as printed"),
    ("R-AZ165-TAX", "AZ_2025_220_PTE", "secondary", "⚠ its line 5 cites Form 165 line 23, which is not a tax line"),
    ("R-AZ165-PAYMENTS", "AZ_2025_FORM_165", "primary", "lines 26-33 and Schedule F"),
    ("R-AZ165-PAYMENTS", "AZ_2025_120_165EXT_V", "implementation", "the extension payment and the voucher"),
    ("R-AZ165-DUE-REFUND", "AZ_2025_FORM_165", "primary", "lines 34-40 as printed, including the stale line 39"),
    ("R-AZ165-DUE-REFUND", "AZ_2025_FORM_165_INSTR", "implementation", "the line 37 / line 38 sign-flip crossover"),
    ("R-AZ165-INFO-PEN", "AZ_2025_FORM_165_INSTR", "primary", "the line 7 penalty and its PTE carve-out"),
    ("R-AZ165-INFO-PEN", "AZ_2025_PUB_713", "secondary", "AZDOR answered the question directly: 'No.'"),
    ("R-AZ165-PENALTY", "AZ_2025_FORM_165_INSTR", "primary", "the penalty table and the 25% combined cap"),
    ("R-AZ165-PENALTY", "AZ_ARS_43_581", "primary", "§ 43-581(E)(2), the $1,000 penalty floor"),
    ("R-AZ165-EST-PAY", "AZ_ARS_43_581", "primary", "§ 43-581(C) — 'EXCEEDS $150,000'"),
    ("R-AZ165-EST-PAY", "AZ_2025_FORM_165_INSTR", "implementation", "'exceeds $150,000' repeated"),
    ("R-AZ165-EST-PAY", "AZ_2025_220_PTE", "secondary", "⚠ its face prints the CORPORATE installment months"),
    ("R-AZ165-EST-BASIS", "AZ_ARS_43_581", "primary", "the statute's bare 'taxable income' — the ruled basis"),
    ("R-AZ165-EST-BASIS", "AZ_2025_PUB_713", "secondary", "⚠ internally inconsistent THREE ways on this rule"),
    ("R-AZ165-EST-BASIS", "AZ_2025_120_PTE_W", "secondary", "⚠ uses TWO different bases in one book"),
    ("R-AZ165-1021-15", "AZ_ARS_43_1021", "primary", "§ 43-1021(15), verbatim, including the entity clause"),
    ("R-AZ165-1021-15", "AZ_2025_PUB_713", "interpretive", "AZDOR's 'owner level only' answer to the same question"),
    ("R-AZ165-1021-15", "AZ_2025_FORM_165", "primary", "the page-6 A4 worksheet is a CLOSED list of three items"),
    ("R-AZ165-SCHE-XFOOT", "AZ_2025_FORM_165", "primary", "E8 column (c) should equal 1.000000, on the face"),
    ("R-AZ165-SCHD", "AZ_2025_FORM_165", "primary", "Schedule D columns (a)-(h) as printed"),
    ("R-AZ165-SCHD", "AZ_2025_PUB_713", "secondary", "special allocations: allowed here, forbidden on the 120S"),
    ("R-AZ165-K1-SPLIT", "AZ_2025_165_SCHK1", "primary", "the resident schedule and its line 3 routing"),
    ("R-AZ165-K1-SPLIT", "AZ_2025_165_SCHK1NR", "primary", "'All corporate partners and partners that are partnerships'"),
    ("R-AZ165-K1NR-COL", "AZ_2025_165_SCHK1NR", "primary", "columns (a)/(b)/(c) and the printed destinations"),
    ("R-AZ165-K1-CREDIT", "AZ_ARS_43_1077", "primary", "the credit, keyed to tax PAID, with a five-year carryforward"),
    ("R-AZ165-K1-CREDIT", "AZ_2025_165_SCHK1", "implementation", "Part 7 lines 11-15"),
    ("R-AZ165-K1-CREDIT", "AZ_2025_PUB_713", "secondary", "the Addendum #1 allocation example, from LIABILITY"),
    ("R-AZ165-TIERED", "AZ_2025_FORM_165_INSTR", "primary", "the page-6 A4-A / B5-A instruction, column (a)"),
    ("R-AZ165-TIERED", "AZ_2025_FORM_165PA", "secondary", "the received-165PA-K-1(NR) amended-return trigger"),
    ("R-AZ165-ELECTION", "AZ_ARS_43_1014", "primary", "§ 43-1014(A) — the election IS the filing"),
    ("R-AZ165-ELECTION", "AZ_SB1274_2025_CH182", "primary", "Sec. 6 struck timeliness; Sec. 9(A) made it retroactive"),
    ("R-AZ165-ELECTION", "AZ_2025_PUB_713", "secondary", "amendment, revocation and the four-year SOL"),
    ("R-AZ165-ZERORETURN", "AZ_2025_FORM_120S_INSTR", "primary", "the line-by-line script (the 165 book's twin)"),
    ("R-AZ165-ZERORETURN", "AZ_2025_PUB_713", "secondary", "the SALT-cap framing AZDOR itself supplies"),
    ("R-AZ165-COMPOSITE", "AZ_2025_FORM_165_INSTR", "primary", "the composite rules and ITR 16-2"),
    ("R-AZ165-COMPOSITE", "AZ_2025_PUB_713", "secondary", "'No.' — electing owners must file their own returns"),
    ("R-AZ165-EFILE", "AZ_ARS_43_323_EFILE", "primary", "§ 43-323(F)-(G)"),
    ("R-AZ165-EFILE", "AZ_2025_FORM_165_INSTR", "implementation", "the seven-item exemption list and the 246 MB cap"),
    ("R-AZ165-EFILE", "AZ_DOR_MEF_LOI_TY2025", "secondary", "the Arizona MeF registration gate"),
    ("R-AZ165-165PA", "AZ_ARS_43_1414", "primary", "§ 43-1414(B)(1)(b) — the highest INDIVIDUAL rate"),
    ("R-AZ165-165PA", "AZ_2025_FORM_165PA", "primary", "face line 13 prints 4.5%"),
    ("R-AZ165-165PA", "AZ_SB1274_2025_CH182", "secondary", "Sec. 7 amended subsection (A) ONLY"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM AZ_165 — LINES (transcribed AS PRINTED; defects flagged, never "fixed")
# ═══════════════════════════════════════════════════════════════════════════
AZ165_LINES: list[dict] = [
    # ---- Part 1 -----------------------------------------------------------
    {"line_number": "1", "line_type": "input", "sort_order": 1,
     "description": ("Federal ordinary business and rental income (loss) from Form 1065, Schedule K. "
                     "See instructions"),
     "source_facts": ["az165_l1_federal_ordinary_and_rental"], "source_rules": ["R-AZ165-L5", "R-AZ165-L6"],
     "notes": ("⚠ THREE federal Schedule K components summed — ordinary income (loss) from trade or "
               "business activities, rental real estate activities, and other rental activities. NOT "
               "Schedule K line 1 alone.")},
    {"line_number": "A1", "line_type": "input", "sort_order": 2,
     "description": "SCHEDULE A: Additions to Partnership Income — A1 Total federal depreciation",
     "source_facts": ["az165_a1_total_federal_depreciation"], "source_rules": ["R-AZ165-P1-ADD"],
     "notes": "The ENTIRE federal § 167(a) allowance (A.R.S. § 43-1021(11)), bonus and MACRS alike."},
    {"line_number": "A2", "line_type": "input", "sort_order": 3,
     "description": "A2 Non-Arizona municipal bond interest",
     "source_facts": ["az165_a2_non_az_muni_interest"], "source_rules": ["R-AZ165-P1-ADD"],
     "notes": "⚠ NET of carrying costs and of Arizona-exempt obligations — not gross federal "
              "tax-exempt interest."},
    {"line_number": "A3", "line_type": "subtotal", "sort_order": 4,
     "description": "A3 Additions related to Arizona tax credits. See instructions",
     "calculation": "page-6 worksheet line E (Forms 312 + 318 + 320 + 325 D1 + 325 D2)",
     "source_facts": ["az165_a3_credit_related_additions"], "source_rules": ["R-AZ165-P1-ADD"],
     "notes": "Include the page-6 worksheet with the return whenever an amount is entered."},
    {"line_number": "A4", "line_type": "subtotal", "sort_order": 5,
     "description": "A4 Other additions to partnership income. See instructions",
     "calculation": "page-6 worksheet line D (A4-A + A4-B + A4-C)",
     "source_facts": ["az165_a4_other_additions"], "source_rules": ["R-AZ165-P1-ADD", "R-AZ165-TIERED"],
     "notes": ("⚠ A CLOSED ENUMERATION OF THREE ITEMS. NO FREE-TEXT 'OTHER' ROW EXISTS ANYWHERE ON "
               "PAGE 6 — which is exactly why the § 43-1021(15) entity-level PTE add-back cannot be "
               "expressed on this form (D-12 A3).")},
    {"line_number": "2", "line_type": "subtotal", "sort_order": 6,
     "description": "Total additions to partnership income: Add lines A1 through A4. Enter the total",
     "calculation": "A1 + A2 + A3 + A4", "source_rules": ["R-AZ165-P1-ADD"]},
    {"line_number": "3", "line_type": "subtotal", "sort_order": 7,
     "description": "Subtotal: Add lines 1 and 2. Enter the total", "calculation": "1 + 2",
     "source_rules": ["R-AZ165-P1-ADD"]},
    {"line_number": "B1", "line_type": "calculated", "sort_order": 8,
     "description": "SCHEDULE B: Subtractions From Partnership Income — B1 Recalculated Arizona depreciation",
     "calculation": ("sum over assets of § 167(a) depreciation recomputed at the tier's AZ bonus % of "
                     "federal § 168(k): 0% | ITP 16-2 | 10% | 55% | 100%, keyed on PLACED IN SERVICE"),
     "source_facts": ["az165_b1_recalculated_az_depreciation", "az165_b1_ty2013_tier_amount"],
     "source_rules": ["R-AZ165-DEPR-B1", "R-AZ165-BONUS-IND"],
     "notes": ("⚠ FIVE tiers (the brief's 'four' was corrected on verification). ⚠ THE TY2013 TIER IS "
               "DIRECT-ENTRY pending ITP 16-2 (U1). ⚠ THE FINAL TIER IS THE INDIVIDUAL RULE — this "
               "line is the whole reason AZ_165 has a depreciation shadow book and AZ_120S has none.")},
    {"line_number": "B2", "line_type": "input", "sort_order": 9,
     "description": ("B2 Basis adjustment for property sold or otherwise disposed of during the "
                     "taxable year. See instructions"),
     "source_facts": ["az165_b2_basis_adjustment_on_disposition"], "source_rules": ["R-AZ165-P1-SUB"],
     "notes": ("⚠ CONDITIONED ON AN UNBROKEN ARIZONA ADD-BACK HISTORY FOR THAT ASSET BACK TO TAXABLE "
               "YEARS BEGINNING AFTER 12/31/1999 — a stateful, multi-decade attribute the current "
               "year cannot derive. § 43-1022(18).")},
    {"line_number": "B3", "line_type": "input", "sort_order": 10,
     "description": "B3 Interest from U.S. government obligations",
     "source_facts": ["az165_b3_us_government_interest"], "source_rules": ["R-AZ165-P1-SUB"],
     "notes": "⚠ GNMA and FNMA obligations are NOT U.S. government obligations for this purpose and "
              "ARE taxable to Arizona (AZDOR ruling ITR 06-1, unpulled)."},
    {"line_number": "B4", "line_type": "input", "sort_order": 11,
     "description": "B4 Agricultural crops charitable contribution. See instructions",
     "source_facts": ["az165_b4_agricultural_crop_contribution"], "source_rules": ["R-AZ165-P1-SUB"],
     "notes": "Arizona tax-exempt charities, for use in Arizona; AZDOR procedure ITP 12-1 (unpulled)."},
    {"line_number": "B5", "line_type": "subtotal", "sort_order": 12,
     "description": "B5 Other subtractions from partnership income. See instructions",
     "calculation": "page-6 worksheet line H (eight enumerated items)",
     "source_facts": ["az165_b5_other_subtractions"], "source_rules": ["R-AZ165-P1-SUB", "R-AZ165-TIERED"],
     "notes": ("⚠ A CLOSED LIST OF EIGHT. ⚠ AND NO MCTCP ROW: H.B. 4168's new § 43-1022(31)/(32)/(35)/"
               "(36) tips, overtime, senior and vehicle-loan-interest subtractions are TY2025-effective "
               "and AZDOR REISSUED THIS BOOK AFTER ENACTMENT WITHOUT ADDING THEM (U18 / W23).")},
    {"line_number": "4", "line_type": "subtotal", "sort_order": 13,
     "description": "Total subtractions from partnership income: Add lines B1 through B5. Enter the total",
     "calculation": "B1 + B2 + B3 + B4 + B5", "source_rules": ["R-AZ165-P1-SUB"]},
    {"line_number": "5", "line_type": "total", "sort_order": 14,
     "description": ("Partnership income adjusted to Arizona basis: Subtract line 4 from line 3. Enter "
                     "the difference"),
     "calculation": "3 − 4", "source_rules": ["R-AZ165-L5"],
     "destination_form": "AZ_165 line 8 (the PTE base) and AZ_165 Schedule D column (h)",
     "notes": "⚠ LINE 5 STAYS ON THE RETURN. It is LINE 6 that goes to the owners. Do not cross them."},
    {"line_number": "6", "line_type": "total", "sort_order": 15,
     "description": ("Net adjustment of partnership income from federal to Arizona basis: Subtract "
                     "line 1 from line 5. Enter the difference"),
     "calculation": "5 − 1", "source_rules": ["R-AZ165-L6"],
     "destination_form": "AZ_165 Schedule K-1 line 1 and AZ_165 Schedule K-1(NR) line 15",
     "notes": ("⚠⚠ THE ONLY NUMBER THAT LEAVES PART 1 FOR THE OWNERS. Two different outputs of the "
               "same block going to two different places — CROSSING LINES 5 AND 6 IS THE MOST LIKELY "
               "SINGLE TRANSCRIPTION ERROR ON THIS FORM.")},
    {"line_number": "7", "line_type": "input", "sort_order": 16,
     "description": ("Penalty for late filing or incomplete filing. (Information return penalty). See "
                     "instructions"),
     "source_facts": ["az165_l7_information_return_penalty"], "source_rules": ["R-AZ165-INFO-PEN"],
     "notes": "⚠ NON-ELECTING PARTNERSHIPS ONLY. $100/month or fraction, capped at $500. If the "
              "partnership elected, this line is zero and Part 2 is completed instead."},

    # ---- Part 2, block 1 ---------------------------------------------------
    {"line_number": "8", "line_type": "calculated", "sort_order": 20,
     "description": "Enter the amount from line 5", "calculation": "= line 5",
     "source_rules": ["R-AZ165-PTE-BASE", "R-AZ165-PART2-GATE"],
     "notes": "Part 2 is completed when question A = Yes OR PTE estimated payments were made (W18)."},
    {"line_number": "9", "line_type": "input", "sort_order": 21,
     "description": "Enter the total of all items requiring separate computation",
     "source_facts": ["az165_l9_separately_stated_items"],
     "source_rules": ["R-AZ165-PTE-BASE", "R-AZ165-179-ROUTE"],
     "notes": ("⚠⚠ SIXTEEN STATUTORY CATEGORIES IN ONE UNDIFFERENTIATED BOX, with no supporting "
               "schedule and no itemisation — A.R.S. § 43-1412 ¶1-16, of which ¶5 IS § 179. THE "
               "LARGEST DIRECT-ENTRY SURFACE ON FORM 165 AND THE PLACE A § 179 ERROR WILL HIDE (W10).")},
    {"line_number": "10", "line_type": "subtotal", "sort_order": 22,
     "description": "Add lines 8 and 9. Enter the total", "calculation": "8 + 9",
     "source_rules": ["R-AZ165-PTE-BASE"],
     "notes": "= A.R.S. § 43-1014(B)(1)(a)(ii) exactly. ⚠ Contrast Form 120S line 37 = line 1."},
    {"line_number": "11", "line_type": "calculated", "sort_order": 23,
     "description": ("Add lines E1 and E4 in column (c) of Schedule E. ... resident individual partners "
                     "and resident estate and trust partners that did not opt out"),
     "calculation": "E1(c) + E4(c), as a decimal to six places", "source_rules": ["R-AZ165-SHARES"]},
    {"line_number": "12", "line_type": "calculated", "sort_order": 24,
     "description": "Multiply line 10 by line 11. Enter the result", "calculation": "10 × 11",
     "source_rules": ["R-AZ165-ALLOC"]},
    {"line_number": "13", "line_type": "calculated", "sort_order": 25,
     "description": ("Add lines E2 and E5 in column (c) of Schedule E. ... nonresident individual "
                     "partners and nonresident estate and trust partners that did not opt out"),
     "calculation": "E2(c) + E5(c), six decimals", "source_rules": ["R-AZ165-SHARES"]},
    {"line_number": "14", "line_type": "calculated", "sort_order": 26,
     "description": "Multiply line 10 by line 13. Enter the result", "calculation": "10 × 13",
     "source_rules": ["R-AZ165-ALLOC"]},
    {"line_number": "15", "line_type": "calculated", "sort_order": 27,
     "description": ("Enter the distributive share from line E3, column (c) of Schedule E. ... "
                     "part-year resident partners that did not opt out"),
     "calculation": "E3(c), six decimals", "source_rules": ["R-AZ165-SHARES"]},
    {"line_number": "16", "line_type": "calculated", "sort_order": 28,
     "description": "Multiply line 10 by line 15. Enter the result", "calculation": "10 × 15",
     "source_rules": ["R-AZ165-ALLOC"]},
    {"line_number": "16A", "line_type": "input", "sort_order": 29,
     "description": "Enter the portion of line 16 that all part-year residents earned while residents of Arizona",
     "source_facts": ["az165_l16a_part_year_resident_portion"], "source_rules": ["R-AZ165-ALLOC"],
     "notes": "⚠ BY ACTUAL RESIDENCY PERIOD, NOT BY DAY COUNT. 16A + 16B must equal line 16 — stated "
              "on the face."},
    {"line_number": "16B", "line_type": "input", "sort_order": 30,
     "description": ("Enter the portion of line 16 that all part-year residents earned while "
                     "nonresidents of Arizona"),
     "source_facts": ["az165_l16b_part_year_nonresident_portion"], "source_rules": ["R-AZ165-ALLOC"]},
    {"line_number": "17", "line_type": "calculated", "sort_order": 31,
     "description": ("Enter the distributive share from line E7, column (c) of Schedule E. ... partners "
                     "that opted out ... and entity partners that are not eligible to make the election"),
     "calculation": "E7(c), six decimals", "source_rules": ["R-AZ165-SHARES"],
     "notes": "Ineligible = anything that is not an individual, estate or trust — including an "
              "upper-tier partnership or S corporation, and an IRA."},
    {"line_number": "18", "line_type": "calculated", "sort_order": 32,
     "description": "Multiply line 10 by line 17. Enter the result", "calculation": "10 × 17",
     "source_rules": ["R-AZ165-ALLOC"],
     "notes": "⚠ FACE-PRINTED CROSS-FOOT: 'The total of lines 12, 14, 16 and 18 must equal the amount "
              "reported on line 10.'"},

    # ---- Part 2, block 2 ---------------------------------------------------
    {"line_number": "19", "line_type": "calculated", "sort_order": 33,
     "description": "Add line 12 and line 16A. Enter the total",
     "calculation": "max(0, 12 + 16A)", "source_rules": ["R-AZ165-ZEROFLOOR"],
     "notes": "⚠ THE ZERO FLOOR IS IN THE INSTRUCTIONS ONLY — the face carries no such note, while "
              "Form 120S PRINTS it at lines 46 and 48 (W4)."},
    {"line_number": "20", "line_type": "calculated", "sort_order": 34,
     "description": ("Multiply the amount on line 19 by the PTE tax rate, 2.5% (0.0250) Enter the "
                     "result. This is the tax attributable to resident partners and part-year resident "
                     "partners (during the period of residency) that did not opt out"),
     "calculation": "19 × 0.0250", "source_rules": ["R-AZ165-RATE"],
     "notes": "⚠ THE RATE IS PRE-PRINTED ON THE FACE, NOT LOOKED UP. Resident-period income is NOT "
              "apportioned."},
    {"line_number": "21", "line_type": "calculated", "sort_order": 35,
     "description": "Add line 14 and line 16B. Enter the total", "calculation": "max(0, 14 + 16B)",
     "source_rules": ["R-AZ165-ZEROFLOOR"]},
    {"line_number": "22", "line_type": "calculated", "sort_order": 36,
     "description": "Enter the Arizona apportionment ratio from Schedule C or Schedule ACA",
     "calculation": "1.0 if question D = Yes, else Schedule C line C5 (STANDARD) / C3f (SALES FACTOR "
                    "ONLY) / Schedule ACA line 3 (AIR CARRIER)",
     "source_facts": ["az165_q_d_arizona_only", "az165_q_f_apportionment_method"],
     "source_rules": ["R-AZ165-APPORT", "R-AZ165-DIVISOR"],
     "notes": ("⚠ '0.000000' = NO ARIZONA NEXUS; BLANK or '1.000000' = sourced entirely within "
               "Arizona. A null-vs-zero bug here silently zeroes every nonresident's Arizona income.")},
    {"line_number": "23", "line_type": "calculated", "sort_order": 37,
     "description": "Multiply the amount on line 21 by the decimal on line 22. Enter the result",
     "calculation": "21 × 22", "source_rules": ["R-AZ165-TAX"],
     "notes": ("⚠ FORM 220/PTE PART B LINE 5 CITES THIS LINE AS 'the 2025 Arizona tax liability'. IT "
               "IS NOT A TAX — it is an intermediate apportioned nonresident base. The intended "
               "reference is LINE 25 (U11 / W20).")},
    {"line_number": "24", "line_type": "calculated", "sort_order": 38,
     "description": ("Multiply the amount on line 23 by the PTE tax rate, 2.5% (0.0250). Enter the "
                     "result. This is the tax attributable to nonresident partners and part-year "
                     "resident partners (during the period of nonresidency) that did not opt out"),
     "calculation": "23 × 0.0250", "source_rules": ["R-AZ165-RATE"]},

    # ---- Part 2, block 3 ---------------------------------------------------
    {"line_number": "25", "line_type": "total", "sort_order": 39,
     "description": ("Add line 20 and line 24. Enter the total. This is the total amount of tax owed by "
                     "the Partnership"),
     "calculation": "20 + 24", "source_rules": ["R-AZ165-TAX", "R-AZ165-K1-CREDIT"],
     "destination_form": "AZ_220_PTE Part B line 5 (⚠ its face cites line 23; build from line 25)",
     "notes": "⚠ TAX OWED, NOT TAX PAID. § 43-1077(B) keys the owner credit to tax PAID and no "
              "schedule reconciles the two before the K-1s are cut (U9 / W19)."},
    {"line_number": "26", "line_type": "input", "sort_order": 40,
     "description": "Extension payment made with Form 120/165EXT",
     "source_facts": ["az165_l26_extension_payment"], "source_rules": ["R-AZ165-PAYMENTS"],
     "notes": "⚠ DO NOT auto-derive from Schedule F column (c) — the form states no such link (W6)."},
    {"line_number": "27", "line_type": "calculated", "sort_order": 41,
     "description": "Estimated Tax Payments", "calculation": "= Schedule F line F7 column (b)",
     "source_facts": ["az165_l27_estimated_tax_payments"], "source_rules": ["R-AZ165-PAYMENTS"]},
    {"line_number": "28", "line_type": "input", "sort_order": 42,
     "description": ("Amended Returns. Payment made with original return plus all payments made after "
                     "it was filed"),
     "source_facts": ["az165_l28_amended_payments"], "source_rules": ["R-AZ165-PAYMENTS"]},
    {"line_number": "29", "line_type": "subtotal", "sort_order": 43,
     "description": "Subtotal of tax payments. Add lines 26 through 28", "calculation": "26 + 27 + 28",
     "source_rules": ["R-AZ165-PAYMENTS"]},
    {"line_number": "30", "line_type": "input", "sort_order": 44,
     "description": "Overpayments of tax from original return or previously filed amended returns",
     "source_facts": ["az165_l30_prior_overpayments"], "source_rules": ["R-AZ165-PAYMENTS"]},
    {"line_number": "31", "line_type": "subtotal", "sort_order": 45,
     "description": "Total payments. Subtract line 30 from line 29. Enter the difference",
     "calculation": "29 − 30", "source_rules": ["R-AZ165-PAYMENTS"]},
    {"line_number": "32", "line_type": "calculated", "sort_order": 46,
     "description": "Balance of tax due: If line 25 is larger than line 31, subtract line 31 from line 25",
     "calculation": "max(0, 25 − 31)", "source_rules": ["R-AZ165-PAYMENTS"]},
    {"line_number": "33", "line_type": "calculated", "sort_order": 47,
     "description": "Overpayment of tax. If line 31 is larger than 25, subtract line 25 from line 31",
     "calculation": "max(0, 31 − 25)", "source_rules": ["R-AZ165-PAYMENTS"]},
    {"line_number": "34", "line_type": "input", "sort_order": 48,
     "description": "Penalty and interest",
     "source_facts": ["az165_l34_penalty_and_interest"], "source_rules": ["R-AZ165-PENALTY"],
     "notes": "Interest runs on LINE 25 from the ORIGINAL due date at the prevailing rate. Combined "
              "penalty cap 25%."},
    {"line_number": "35", "line_type": "input", "sort_order": 49,
     "description": ("Estimated underpayment penalty: If Form 220/PTE is included check box 35A"),
     "source_facts": ["az165_l35_estimated_underpayment_penalty"],
     "source_rules": ["R-AZ165-EST-PAY", "R-AZ165-PENALTY"],
     "notes": ("Imports Form 220/PTE Part C line 37. ⚠ BUILD THE FLOW FROM THE FORM 165 INSTRUCTIONS: "
               "the 220/PTE face's own line 37 routing list names Form 120S line 25 (an overpayment "
               "line) and OMITS FORM 165 ENTIRELY (U20 / W25). ⚠ On an amended return, do not "
               "recompute.")},
    {"line_number": "36", "line_type": "calculated", "sort_order": 50,
     "description": ("Penalty for Late or Incomplete Filing. (Information Return Penalty.) Enter the "
                     "amount from line 7"),
     "calculation": "= line 7", "source_rules": ["R-AZ165-INFO-PEN"],
     "notes": "Zero whenever the PTE election is made."},
    {"line_number": "37", "line_type": "total", "sort_order": 51,
     "description": "Total amount due", "calculation": "32 + 34 + 35 + 36  (⚠ SKIPS line 33)",
     "source_rules": ["R-AZ165-DUE-REFUND"],
     "notes": "⚠ AND IT ALSO RECEIVES A NEGATIVE LINE 38 AS A POSITIVE NUMBER — see line 38."},
    {"line_number": "38", "line_type": "total", "sort_order": 52,
     "description": "Overpayment. See instructions",
     "calculation": "33 − (34 + 35 + 36), entered POSITIVE; if negative, carry the absolute value to line 37",
     "source_rules": ["R-AZ165-DUE-REFUND"],
     "notes": "A SIGN-FLIP CROSSOVER between the two totals, stated only in the instructions."},
    {"line_number": "39", "line_type": "input", "sort_order": 53,
     "description": "Amount of line 38 to be applied to 2025 estimated tax  [FACE AS PRINTED]",
     "source_facts": ["az165_l39_overpayment_applied_next_year"], "source_rules": ["R-AZ165-DUE-REFUND"],
     "notes": ("⚠ PRINTED-FORM DEFECT AZ-D1 / W5: the face says 2025, the instruction says 2026, and "
               "Form 120S line 35 correctly says 2026. TRANSCRIBE AS PRINTED; COMPUTE 2026. "
               "Independently re-confirmed by the verification pass.")},
    {"line_number": "40", "line_type": "total", "sort_order": 54,
     "description": "Amount to be refunded. Subtract line 39 from line 38. Enter the difference",
     "calculation": "38 − 39", "source_rules": ["R-AZ165-DUE-REFUND"]},

    # ---- page 6 worksheets --------------------------------------------------
    {"line_number": "P6-A3-A", "line_type": "input", "sort_order": 60,
     "description": "Page 6, A3-A: Agricultural Water Conservation System Credit [Form 312]",
     "source_rules": ["R-AZ165-P1-ADD"]},
    {"line_number": "P6-A3-B", "line_type": "input", "sort_order": 61,
     "description": ("Page 6, A3-B: Credit for Taxes Paid for Coal Consumed in Generating Electrical "
                     "Power [Form 318]"),
     "source_rules": ["R-AZ165-P1-ADD"]},
    {"line_number": "P6-A3-C", "line_type": "input", "sort_order": 62,
     "description": "Page 6, A3-C: Credit for Employment of TANF Recipients [Form 320]",
     "source_rules": ["R-AZ165-P1-ADD"]},
    {"line_number": "P6-A3-D1", "line_type": "input", "sort_order": 63,
     "description": ("Page 6, A3-D1: Agricultural Pollution Control Equipment Credit — Excess Federal "
                     "Depreciation or Amortization [Form 325]"),
     "source_rules": ["R-AZ165-P1-ADD"]},
    {"line_number": "P6-A3-D2", "line_type": "input", "sort_order": 64,
     "description": ("Page 6, A3-D2: Agricultural Pollution Control Equipment Credit — Excess in "
                     "Federal Adjusted Basis [Form 325]"),
     "source_rules": ["R-AZ165-P1-ADD"]},
    {"line_number": "P6-A3-E", "line_type": "subtotal", "sort_order": 65,
     "description": "Page 6, A3-E: Total Additions Related to Arizona Tax Credits → page 1 line A3",
     "calculation": "A3-A + A3-B + A3-C + A3-D1 + A3-D2", "source_rules": ["R-AZ165-P1-ADD"]},
    {"line_number": "P6-A4-A", "line_type": "input", "sort_order": 66,
     "description": "Page 6, A4-A: Positive Partnership Income Adjustment",
     "source_facts": ["az165_a4a_positive_partnership_adjustment"], "source_rules": ["R-AZ165-TIERED"],
     "notes": ("⚠ FROM A RECEIVED 165 Schedule K-1(NR) LINE 15, **COLUMN (a)** — the UNAPPORTIONED "
               "amount, re-apportioned at this level. Total multiple K-1(NR)s. A NEGATIVE line 15 goes "
               "to B5-A instead. ⚠ ALSO the amended-return landing point for a received 165PA Schedule "
               "K-1(NR) line 3.")},
    {"line_number": "P6-A4-B", "line_type": "input", "sort_order": 67,
     "description": "Page 6, A4-B: Federal Depreciation of Child Care Facilities",
     "source_facts": ["az165_a4b_child_care_facility_depreciation"], "source_rules": ["R-AZ165-P1-ADD"]},
    {"line_number": "P6-A4-C", "line_type": "input", "sort_order": 68,
     "description": "Page 6, A4-C: Expenditures for the Americans with Disabilities Act",
     "source_facts": ["az165_a4c_ada_expenditures_addition"], "source_rules": ["R-AZ165-P1-ADD"]},
    {"line_number": "P6-A4-D", "line_type": "subtotal", "sort_order": 69,
     "description": "Page 6, A4-D: Total Other Additions to Partnership Income → page 1 line A4",
     "calculation": "A4-A + A4-B + A4-C", "source_rules": ["R-AZ165-P1-ADD", "R-AZ165-1021-15"],
     "notes": ("⚠⚠ THE LIST ENDS HERE. THERE IS NO 'OTHER' ROW. This closed enumeration is the "
               "structural fact behind campaign ruling D-12 A3 — the § 43-1021(15) entity-level PTE "
               "add-back has nowhere to go on this form.")},
    {"line_number": "P6-B5-A", "line_type": "input", "sort_order": 70,
     "description": "Page 6, B5-A: Negative Partnership Income Adjustment",
     "source_rules": ["R-AZ165-TIERED"],
     "notes": "The negative-line-15 branch of the tiered-partnership loop, also column (a)."},
    {"line_number": "P6-B5-B", "line_type": "input", "sort_order": 71,
     "description": "Page 6, B5-B: Mine Exploration Expenses", "source_rules": ["R-AZ165-P1-SUB"]},
    {"line_number": "P6-B5-C", "line_type": "input", "sort_order": 72,
     "description": ("Page 6, B5-C: Interest on Federally Taxable Arizona Obligations Evidenced by "
                     "Bonds"),
     "source_rules": ["R-AZ165-P1-SUB"]},
    {"line_number": "P6-B5-D", "line_type": "input", "sort_order": 73,
     "description": "Page 6, B5-D: Wood Stoves, Wood Fireplaces or Gas-Fired Fireplaces",
     "source_rules": ["R-AZ165-P1-SUB"]},
    {"line_number": "P6-B5-E1", "line_type": "input", "sort_order": 74,
     "description": "Page 6, B5-E1: Expenses Related to the Work Opportunity Credit",
     "source_rules": ["R-AZ165-P1-SUB"]},
    {"line_number": "P6-B5-E2", "line_type": "input", "sort_order": 75,
     "description": "Page 6, B5-E2: Expenses Related to the Empowerment Zone Employment Credit",
     "source_rules": ["R-AZ165-P1-SUB"]},
    {"line_number": "P6-B5-E3", "line_type": "input", "sort_order": 76,
     "description": ("Page 6, B5-E3: Expenses Related to the Credit for Employer-Paid Social Security "
                     "Taxes on Employee Cash Tips"),
     "source_rules": ["R-AZ165-P1-SUB"]},
    {"line_number": "P6-B5-E4", "line_type": "input", "sort_order": 77,
     "description": "Page 6, B5-E4: Expenses Related to the Indian Employment Credit",
     "source_rules": ["R-AZ165-P1-SUB"]},
    {"line_number": "P6-B5-F", "line_type": "input", "sort_order": 78,
     "description": "Page 6, B5-F: Expenditures for the Americans with Disabilities Act",
     "source_rules": ["R-AZ165-P1-SUB"]},
    {"line_number": "P6-B5-G", "line_type": "input", "sort_order": 79,
     "description": "Page 6, B5-G: Marijuana Establishments Only — Disallowed Federal Expenses",
     "source_rules": ["R-AZ165-P1-SUB"],
     "notes": ("Fed by Schedule DFE line 16. ⚠ ON THE PARTNERSHIP SIDE THIS IS AN **ENTITY-LEVEL** "
               "SUBTRACTION; on the S-corp side the same Schedule DFE figure goes to the SHAREHOLDER "
               "via 120S Schedule K-1 Part 4. Different plumbing for the same input.")},
    {"line_number": "P6-B5-H", "line_type": "subtotal", "sort_order": 80,
     "description": "Page 6, B5-H: Total Other Subtractions from Partnership Income → page 1 line B5",
     "calculation": "B5-A through B5-G", "source_rules": ["R-AZ165-P1-SUB"],
     "notes": "⚠ NO FREE-TEXT ROW HERE EITHER, AND NO MCTCP ROW (U18 / W23)."},

    # ---- Schedule C ---------------------------------------------------------
    {"line_number": "C1c", "line_type": "calculated", "sort_order": 90,
     "description": "Schedule C C1c: Total owned and rented property (section a plus section b)",
     "calculation": "(inventories + depreciable assets + land + other − nonbusiness) + (net annual rent × 8)",
     "source_facts": ["az165_schc_property_inventories", "az165_schc_property_depreciable",
                      "az165_schc_property_land", "az165_schc_property_other",
                      "az165_schc_property_nonbusiness", "az165_schc_rented_property_net_rent"],
     "source_rules": ["R-AZ165-DIVISOR"],
     "notes": ("⚠ OWNED PROPERTY AT **ORIGINAL COST**, not net book value. Rented property at EIGHT "
               "TIMES the net annual rental rate, and 'net' means LESS aggregate annual SUBRENTAL "
               "rates paid by subtenants. The property factor may not exceed 1.0. STANDARD "
               "apportionment only.")},
    {"line_number": "C2", "line_type": "input", "sort_order": 91,
     "description": ("Schedule C C2: Payroll Factor — total wages, salaries, commissions and other "
                     "compensation to employees (per federal Form 1065, or payroll reports)"),
     "source_facts": ["az165_schc_payroll"], "source_rules": ["R-AZ165-DIVISOR"],
     "notes": "STANDARD apportionment only. Form 120S says 'per federal Form 1120S' in the same slot."},
    {"line_number": "C3d", "line_type": "subtotal", "sort_order": 92,
     "description": "Schedule C C3d: Total sales and other gross receipts (lines a through c)",
     "calculation": "C3a + C3b + C3c",
     "source_facts": ["az165_schc_sales_to_az_purchasers", "az165_schc_msp_service_sales",
                      "az165_schc_other_gross_receipts"],
     "source_rules": ["R-AZ165-DIVISOR", "R-AZ165-MSP"],
     "notes": "⚠ C3b is for MSP ELECTORS ONLY; non-electing service providers leave it blank and use C3c."},
    {"line_number": "C3e", "line_type": "informational", "sort_order": 93,
     "description": "Schedule C C3e: Weight AZ sales (STANDARD × 2; SALES FACTOR ONLY × 1)",
     "source_rules": ["R-AZ165-DIVISOR"],
     "notes": "⚠ THE WEIGHTING AND THE DIVISOR ARE NOT TIED TO EACH OTHER — when the sales factor is "
              "EXCLUDED the divisor drops to TWO, not to three."},
    {"line_number": "C3f", "line_type": "calculated", "sort_order": 94,
     "description": ("Schedule C C3f: Sales Factor Only — Column A = C3d × C3e; Column B = C3d; "
                     "Column C = A ÷ B. Skip C4 and C5"),
     "calculation": "(C3d × weight) ÷ C3d, six decimals", "source_rules": ["R-AZ165-APPORT"],
     "destination_form": "AZ_165 Schedule K-1(NR) Part 1 column (b); and Part 2 line 22 if the PTE "
                         "election is made",
     "notes": "Sales factor cap: 2.0 under STANDARD, 1.0 under SALES FACTOR ONLY."},
    {"line_number": "C4", "line_type": "subtotal", "sort_order": 95,
     "description": "Schedule C C4: STANDARD Apportionment Total Ratio — add Column C of C1c, C2 and C3f",
     "calculation": "C1c(C) + C2(C) + C3f(C)", "source_rules": ["R-AZ165-DIVISOR"]},
    {"line_number": "C5", "line_type": "total", "sort_order": 96,
     "description": ("Schedule C C5: Average Apportionment Ratio for STANDARD Apportionment — divide "
                     "line C4, Column C, by four (4)"),
     "calculation": "C4 ÷ divisor, where divisor = 4 | 3 | 2 | none (see the factor-exclusion rule)",
     "source_rules": ["R-AZ165-DIVISOR", "R-AZ165-APPORT"],
     "destination_form": "AZ_165 Schedule K-1(NR) Part 1 column (b); and Part 2 line 22 if the PTE "
                         "election is made",
     "notes": ("⚠ THE PRINTED '(4)' IS THE DEFAULT, NOT THE RULE. ⚠ '0.000000' = no Arizona nexus; "
               "BLANK or '1.000000' = sourced entirely within Arizona.")},

    # ---- Schedules D / E / F -------------------------------------------------
    {"line_number": "D-h", "line_type": "calculated", "sort_order": 100,
     "description": ("Schedule D column (h): Distributive Share of Income, Page 1, Line 5, per partner"),
     "calculation": "line 5 × column (g)", "source_facts": ["az165_partner_rows"],
     "source_rules": ["R-AZ165-SCHD"],
     "notes": ("⚠ POINTS AT LINE 5 (Arizona-adjusted). Form 120S Schedule B column (h) points at LINE 1 "
               "(federal, unadjusted) — the same column position, a different source line, and the "
               "§2.2 asymmetry showing up a second time. ⚠ SPECIAL ALLOCATIONS ARE HONOURED HERE.")},
    {"line_number": "E6", "line_type": "subtotal", "sort_order": 101,
     "description": ("Schedule E E6: Add lines E1 through E5 — the totals for partners who did NOT opt "
                     "out of the PTE election"),
     "calculation": "E1 + E2 + E3 + E4 + E5, in columns (b) and (c)",
     "source_facts": ["az165_sched_e_rows"], "source_rules": ["R-AZ165-SCHE-XFOOT", "R-AZ165-SHARES"],
     "notes": "⚠ LOOK-THROUGH OWNERS THAT DID NOT OPT OUT GO IN E1-E3 (the INDIVIDUAL rows), NOT E4-E5."},
    {"line_number": "E7", "line_type": "input", "sort_order": 102,
     "description": "Schedule E E7: Partners that opted out of the election or are excluded from making it",
     "source_facts": ["az165_sched_e_rows"], "source_rules": ["R-AZ165-SHARES"]},
    {"line_number": "E8", "line_type": "total", "sort_order": 103,
     "description": ("Schedule E E8: Total partner count and total partnership ownership share. Add E6 "
                     "and E7 in columns (b) and (c). (Column (c) should equal 1.000000.)"),
     "calculation": "E6 + E7; column (c) must equal 1.000000",
     "source_rules": ["R-AZ165-SCHE-XFOOT"],
     "notes": "⚠ A HARD CROSS-FOOT PRINTED ON THE FACE — one of TWO independent proof obligations on "
              "the same allocation."},
    {"line_number": "F7b", "line_type": "subtotal", "sort_order": 104,
     "description": "Schedule F line F7 column (b): Total estimated tax payments → Part 2 line 27",
     "source_facts": ["az165_schf_estimated_payments"], "source_rules": ["R-AZ165-PAYMENTS"],
     "destination_form": "AZ_165 line 27"},
    {"line_number": "F7c", "line_type": "subtotal", "sort_order": 105,
     "description": "Schedule F line F7 column (c): Total extension payments",
     "source_facts": ["az165_schf_extension_payments"], "source_rules": ["R-AZ165-PAYMENTS"],
     "notes": "⚠ NOT STATED TO FEED LINE 26. Line 27 explicitly imports F7(b); line 26 cites no "
              "schedule. Do not invent the link (W6)."},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM AZ_165 — DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════════════════
AZ165_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_AZ165_A4_CORP_PARTNER_BASIS", "severity": "warning",
     "title": "⚠ A corporate partner is receiving an INDIVIDUAL-BASIS Arizona adjustment (D-12 A4)",
     "condition": ("a Schedule K-1(NR) is being issued to a partner whose residency code is 'O' and "
                   "who is a corporation, and the partnership claimed federal bonus depreciation"),
     "message": ("This partner is a CORPORATION and the partnership's Arizona adjustment on line 6 was "
                 "computed on the INDIVIDUAL full-IRC-168(k) basis (A.R.S. 43-1022(17)(e)), because "
                 "that is what Form 165 line B1 prescribes and what A.R.S. 43-1401(2) requires. "
                 "A.R.S. 43-1122(20) separately requires a CORPORATION to compute Arizona depreciation "
                 "as if the IRC 168(k)(7) election OUT of bonus had been made. Nothing on Form 165, on "
                 "this Schedule K-1(NR), or on Form 120/120A Schedule A line A8 / Schedule B line B10 "
                 "instructs the corporate partner to re-compute. CAMPAIGN RULING D-12 A4: DELVIO "
                 "PASSES THE FIGURE THROUGH AS THE K-1 PRINTS IT (column (a)) AND COMPUTES NO "
                 "CORPORATE-BASIS RECOMPUTATION — Arizona publishes none and no form line carries one. "
                 "REVIEW THE CORPORATE PARTNER'S OWN ARIZONA POSITION SEPARATELY."),
     "notes": ("Three readings are on the record and the research chose none of them: (a) AZDOR "
               "intends the corporate partner to accept the partnership-level number; (b) the "
               "corporate partner layers its own adjustment on top, except that line 15 is expressly "
               "the WHOLE line 6 figure INCLUDING A1/B1 and the form gives no way to split it; (c) a "
               "genuine AZDOR gap arising only for C-corp partners of bonus-taking partnerships. "
               "[UNVERIFIED] U2 / W9 stays OPEN AS A FACT — the Form 120 / 120A instructions were "
               "never pulled and are C-CORP-WAVE scope. Ruled 2026-08-19, same session as D-12, after "
               "the gap was surfaced rather than papered over.")},
    {"diagnostic_id": "D_AZ_RD_B1_TY2013_TIER", "severity": "error",
     "title": "RED-DEFER: Form 165 line B1's TY2013 depreciation tier requires AZDOR procedure ITP 16-2",
     "condition": "any asset was placed in service in a taxable year beginning after 12/31/2012 through 12/31/2013",
     "message": ("Arizona Form 165 line B1's second vintage tier must be computed MANUALLY. The AZDOR "
                 "instruction defers entirely: 'For assets placed in service in taxable years "
                 "beginning from and after December 31, 2012 through December 31, 2013, the amount of "
                 "the subtraction for these assets depends on the method used to compute the "
                 "depreciation for assets. See the department's procedure, ITP 16-2.' ITP 16-2 HAS "
                 "NEVER BEEN PULLED. Enter the ITP 16-2 amount directly. The other four tiers are "
                 "fully specified on the form (0% pre-2013, 10% 2014-2015, 55% 2016, 100% 2017+)."),
     "notes": ("[UNVERIFIED] U1 — THE ONLY UNPULLED DOCUMENT THAT GATES A MAINSTREAM LINE. Exposure is "
               "narrow but real: IRC 168(k) never applied to 27.5-year residential rental or 39-year "
               "nonresidential real property, so what is still depreciating in TY2025 from a TY2013 "
               "year is 15-year qualified leasehold / retail improvement property, finishing in 2028. "
               "Settled by downloading ITP 16-2 from AZDOR Legal Research -> Procedures; it is cited "
               "THREE TIMES on this one line and may carry worked examples that change how the other "
               "tiers are implemented.")},
    {"diagnostic_id": "D_AZ165_U6_K1_LINE3_NO_SBI", "severity": "warning",
     "title": "⚠ A resident SBI-electing partner has NO printed destination for the Arizona adjustment",
     "condition": "Schedule K-1 line 3 is non-zero for a resident or part-year resident partner who "
                  "made the Arizona Small Business Income election",
     "message": ("Form 165 Schedule K-1 line 3 lists exactly THREE owner situations and stops: "
                 "resident individuals -> Form 140 page 1 line 16 (positive) or line 27 (negative); "
                 "part-year residents -> Form 140PY line 31 or line 44; resident estates or trusts -> "
                 "Form 141AZ Schedule B line B3 or B9. THERE IS NO SMALL BUSINESS INCOME DESTINATION, "
                 "even though lines 12-15 OF THE SAME DOCUMENT carry a four-way route that includes "
                 "the -SBI forms. Arizona small business income is defined by reference to federal "
                 "Schedules B, C, D, E, F and Form 4797, so partnership income on federal Schedule E "
                 "is squarely inside it and a resident partner in an operating partnership is a prime "
                 "SBI candidate. DELVIO DOES NOT GUESS A DESTINATION. Determine the owner-side "
                 "treatment manually."),
     "notes": ("[UNVERIFIED] U6 / W13. ⚠ THE REASON IS SHARPER THAN 'AZDOR FORGOT': line 3 routes to "
               "Form 140 PAGE 1 lines 16/27 (the main form, a TWO-WAY route) whereas the SBI-bearing "
               "lines 12-15 route to PAGE 5 line P (a ONE-WAY other-additions schedule). LINE 3 WAS "
               "NEVER AN INSTANCE OF THAT TEMPLATE. This is the highest-risk 'rule says no' claim in "
               "the Arizona brief and it was re-attacked on verification and SURVIVED. It does NOT "
               "block this wave — Form 165 line 6 and K-1 line 3 are computed and printed correctly "
               "either way; it blocks the INDIVIDUAL wave's binding. Settled by the TY2025 Form "
               "140-SBI / 140PY-SBI instructions.")},
    {"diagnostic_id": "D_AZ165_U7_K1NR_NO_DESTINATION", "severity": "warning",
     "title": "Schedule K-1(NR) lines 10 and 14 have no printed Form 140NR destination",
     "condition": "Schedule K-1(NR) Part 1 line 10 (guaranteed payments) or line 14 (other deductions) "
                  "is non-zero",
     "message": ("Every other income line on the Form 165 Schedule K-1(NR) face (4, 5, 6, 7, 8, 9, 11, "
                 "12, 13) carries a printed 'Form 140NR Filers: Enter the amount in column (c) on: "
                 "Line NN'. Lines 10 and 14 do not, and the instructions cover passive-loss limits and "
                 "IRC 179 without giving either line a destination. Delvio PRINTS the columns as the "
                 "form requires; the nonresident partner's own reporting position must be determined "
                 "manually."),
     "notes": ("[UNVERIFIED] U7 / printed defect AZ-D7, verified positionally against the face — NOT a "
               "transcription artifact. Likely answers: guaranteed payments fold into the line-4 -> "
               "Line 21 route; other deductions may have no Form 140NR home at all. Settled by the "
               "Form 140NR instructions (individual wave). Note the 120S Schedule K-1(NR) has no "
               "guaranteed-payments line at all and its line 13 'Other deductions' is likewise "
               "undirected.")},
    {"diagnostic_id": "D_AZ165_U18_MCTCP_BY_REFERENCE", "severity": "info",
     "title": "The Form 165 PTE base is defined by OPEN REFERENCE to A.R.S. § 43-1022 as a whole",
     "condition": "the PTE base is computed for TY2025",
     "message": ("The AZDOR PTE-base note builds a partnership's Arizona taxable income from 'any "
                 "Arizona additions found in A.R.S. 43-1021 less any Arizona subtractions found in "
                 "A.R.S. 43-1022'. H.B. 4168 inserted NEW paragraphs into 43-1022 — (31) qualified "
                 "tips, (32) qualified overtime, (35) senior, (36) vehicle-loan interest — all "
                 "effective for TY2025 under Ch. 140 Sec. 35(A). READ LITERALLY, a partnership's "
                 "Arizona taxable income now includes subtractions for items that are in substance "
                 "individual wage-side deductions. DELVIO EXCLUDES THEM FROM THE ENTITY BASE."),
     "notes": ("[UNVERIFIED] U18 / W23. THE EVIDENCE FOR EXCLUDING THEM IS AZDOR'S OWN CONDUCT: both "
               "PTE instruction books were REISSUED AFTER ENACTMENT (2026-08-11 and 2026-08-12, the "
               "120S book regenerated from scratch) and were searched for 'tips', 'overtime', '224', "
               "'225', '151(d)' and '163(h)' with NO HIT; the page-6 B5 worksheet remains a closed "
               "list of eight items, none of them MCTCP. AZDOR had the opportunity and did not act. "
               "Almost certainly a non-issue in substance — a partnership does not receive tips or "
               "overtime compensation — but it is a LIVE DRAFTING EXPOSURE created by defining an "
               "entity base by open reference to an individual modification section.")},
    {"diagnostic_id": "D_AZ165_L5_VS_L6", "severity": "info",
     "title": "Form 165 lines 5 and 6 are DIFFERENT numbers going to DIFFERENT places",
     "condition": "Part 1 is computed",
     "message": ("LINE 5 ('Partnership income adjusted to Arizona basis') feeds the PTE base at line 8 "
                 "and Schedule D column (h). LINE 6 ('Net adjustment of partnership income from "
                 "federal to Arizona basis') is the ONLY number that leaves Part 1 for the owners, "
                 "feeding Schedule K-1 line 1 and Schedule K-1(NR) line 15. Two outputs of one block, "
                 "two destinations."),
     "notes": "Recorded because crossing them is the most likely single transcription error on this form."},
    {"diagnostic_id": "D_AZ165_ZERO_FLOOR_FACE_GAP", "severity": "warning",
     "title": "Lines 19 and 21 carry a zero floor that appears ONLY in the instructions",
     "condition": "line 12 + line 16A, or line 14 + line 16B, computes to less than zero",
     "message": ("The Form 165 instructions for lines 19 and 21 say 'If the total is less than zero, "
                 "\"0\", enter \"0\"'. THE FACE CARRIES NO SUCH NOTE. Form 120S PRINTS exactly the same "
                 "floor ON ITS FACE at lines 46 and 48, which is what makes this an omission rather "
                 "than a difference of substance. Delvio applies the floor."),
     "notes": ("W4. This is the ONE place Arizona's 'the printed face governs' convention runs the "
               "other way: the instruction ADDS a rule the face omits rather than contradicting it, "
               "and the sister form proves the rule is intended. Consistent with Pub 713's note that a "
               "loss-year election is possible but pointless.")},
    {"diagnostic_id": "D_AZ165_L39_STALE_YEAR", "severity": "warning",
     "title": "Form 165 line 39 prints a STALE YEAR on the face (2025; means 2026)",
     "condition": "an overpayment on line 38 is being applied forward",
     "message": ("The FACE reads 'Amount of line 38 to be applied to 2025 estimated tax'. The "
                 "INSTRUCTION for the same line reads 'The partnership may apply part or all of an "
                 "overpayment reported on line 38 as a 2026 PTE estimated tax payment', and Form 120S "
                 "line 35 correctly reads 'to be applied to 2026 estimated tax'. On a TY2025 return, "
                 "applying an overpayment to 2025 estimated tax is meaningless. Delvio transcribes the "
                 "label as printed and computes the 2026 application."),
     "notes": "Printed defect AZ-D1 / W5, INDEPENDENTLY RE-CONFIRMED by the verification pass."},
    {"diagnostic_id": "D_AZ165_L26_NOT_F7C", "severity": "info",
     "title": "Line 26 is NOT auto-derived from Schedule F column (c)",
     "condition": "an extension payment is entered on line 26",
     "message": ("Line 27's instruction EXPLICITLY imports 'the total amount Estimated Tax Payments "
                 "from Schedule F, line F7, column (b)'. Line 26's instruction says only 'Enter the "
                 "Extension Payment made with Form 120/165EXT or online' and does NOT cite F7 column "
                 "(c). Delvio does not auto-link them."),
     "notes": "W6. A loader that auto-derives line 26 from F7(c) invents a relationship the form does "
              "not state."},
    {"diagnostic_id": "D_AZ165_XFOOT_PART2", "severity": "error",
     "title": "Part 2 cross-foot failed: lines 12 + 14 + 16 + 18 must equal line 10",
     "condition": "line 12 + line 14 + line 16 + line 18 != line 10",
     "message": ("Printed ON THE FACE: 'NOTE: The total of lines 12, 14, 16 and 18 must equal the "
                 "amount reported on line 10.' Every partner's share must be allocated to exactly one "
                 "of the four buckets — resident, nonresident, part-year, or opted-out/ineligible. "
                 "A shortfall means a partner is missing from Schedule E; an excess means one is "
                 "double-counted."),
     "notes": "One of TWO independent face-printed proof obligations on the same allocation; the other "
              "is E8 column (c) == 1.000000. Also check 16A + 16B == 16."},
    {"diagnostic_id": "D_AZ165_SCHE_XFOOT", "severity": "error",
     "title": "Schedule E cross-foot failed: E8 column (c) must equal 1.000000",
     "condition": "Schedule E line E8 column (c) != 1.000000",
     "message": ("Printed ON THE FACE: '(Column (c) should equal 1.000000.)' E8 = E6 + E7, where E6 is "
                 "every partner who did NOT opt out and E7 is everyone who opted out or is "
                 "ineligible. ⚠ LOOK-THROUGH PARTNERS (grantor trusts, SMLLCs disregarded to an "
                 "individual) THAT DID NOT OPT OUT BELONG IN E1-E3, THE INDIVIDUAL ROWS — NOT IN "
                 "E4-E5. Placing them in the estate/trust rows is a common source of this failure."),
     "notes": "Ratios are carried to six decimals throughout: 6.54% = 0.065400, 100% = 1.000000."},
    {"diagnostic_id": "D_AZ165_L9_SIXTEEN_CATEGORIES", "severity": "warning",
     "title": "⚠ Line 9 is ONE box for SIXTEEN statutory categories — including § 179",
     "condition": "Part 2 is completed",
     "message": ("Form 165 line 9 ('Enter the total of all items requiring separate computation') has "
                 "NO supporting schedule and NO itemisation on the face. It must carry the partner-"
                 "level total of ALL SIXTEEN A.R.S. 43-1412 categories: capital gains/losses; IRC 1231 "
                 "gains/losses; charitable contributions; IRC 116/243 dividends; IRC 901 foreign "
                 "taxes; partially tax-exempt U.S. interest; income taxes paid to another state or "
                 "country; **IRC 179 EXPENSE (paragraph 5)**; IRC 111 recoveries; IRC 165(d) wagering; "
                 "IRC 175 soil and water; IRC 212 nonbusiness expenses; IRC 214 dependent care; IRC "
                 "215 payments; IRC 216 co-op housing; and IRC 263(c) IDC / IRC 617 mining exploration "
                 "/ IRC 751(b) items / specially allocated items. VERIFY THE COMPOSITION."),
     "notes": ("W10 — THE LARGEST DIRECT-ENTRY SURFACE ON FORM 165 AND THE PLACE A 179 ERROR WILL "
               "HIDE. A.R.S. 43-1401(1) EXCLUDES these items from a partnership's Arizona gross income "
               "in the first place, which is why line 9 exists to add them back. For an S corporation "
               "there is no equivalent: Form 120S line 37 = line 1 = federal Schedule K, already net "
               "of federal 179.")},
    {"diagnostic_id": "D_AZ165_TIERED_COLUMN_A", "severity": "warning",
     "title": "Tiered partnership: take COLUMN (a), not column (c)",
     "condition": "the partnership received one or more Form 165 Schedule K-1(NR)s as a partner",
     "message": ("Page-6 line A4-A / B5-A takes the amount from the received Schedule K-1(NR) line 15 "
                 "COLUMN (a) — the UNAPPORTIONED distributive-share amount — because the upper-tier "
                 "partnership re-apportions at its OWN level. Positive amounts go to A4-A; negative "
                 "amounts go to B5-A. Total the amounts if more than one K-1(NR) was received. ⚠ Using "
                 "column (c) (Arizona source income) double-apportions the figure."),
     "notes": ("Individuals and estates/trusts use column (c); CORPORATIONS AND PARTNERSHIPS USE "
               "COLUMN (a). Four owner types, two columns, off one line. A lower-tier entity cannot "
               "pass the PTE CREDIT up to an entity owner (Pub 713), though it may make its own "
               "election for its own eligible owners.")},
    {"diagnostic_id": "D_AZ165_165PA_AMENDED_TRIGGER", "severity": "warning",
     "title": "A received Form 165PA Schedule K-1(NR) with a positive line 3 forces an AMENDED Form 165",
     "condition": "the partnership received a Form 165PA Schedule K-1(NR) for this taxable year with a "
                  "positive line 3",
     "message": ("Verbatim: 'If this partnership received Arizona Form 165PA Schedule K-1(NR) for this "
                 "taxable year, and the amount on line 3 is positive, FILE AN AMENDED ARIZONA FORM 165 "
                 "for this taxable year. Enter the positive amount from line 3 of the 165PA Schedule "
                 "K-1(NR) on line A4. Complete the amended return. Provide amended Arizona Form 165 "
                 "Schedule(s) K-1 and K-1(NR) to the partners. Submit the amended Arizona Form 165 and "
                 "the amended Schedule(s) to the department.' AN N-OWNER-RETURN EVENT."),
     "notes": ("⚠ THIS INPUT IS MODELLED EVEN THOUGH **COMPUTING** A FORM 165PA IS RED-DEFERRED (D-12 "
               "A2) — receiving one and computing one are different things. The 165PA companion "
               "schedules themselves were never downloaded (U13).")},
    {"diagnostic_id": "D_AZ165_B2_1999_HISTORY", "severity": "warning",
     "title": "Line B2 is conditioned on an unbroken add-back history back to TY2000",
     "condition": "an amount is entered on Schedule B line B2",
     "message": ("The B2 subtraction is available only to 'a taxpayer WHO HAS COMPLIED WITH THE "
                 "REQUIREMENT TO ADD BACK ALL DEPRECIATION with respect to that property on tax "
                 "returns for ALL taxable years beginning from and after December 31, 1999', and only "
                 "'to the extent that the amount has not already reduced Arizona taxable income in the "
                 "current or prior years'. CONFIRM THE ASSET'S ARIZONA ADD-BACK HISTORY."),
     "notes": "A STATEFUL, MULTI-DECADE ATTRIBUTE the current year cannot derive. A.R.S. 43-1022(18) "
              "is the individual analogue; the instruction describes the effect as allowing a "
              "subtraction for the basis difference on any bonus-depreciated asset."},
    {"diagnostic_id": "D_AZ165_IRA_CUSTODIAN_TIN", "severity": "info",
     "title": "Schedule D column (e): an IRA partner reports the CUSTODIAN'S TIN",
     "condition": "a Schedule D partner row is an IRA",
     "message": ("Verbatim: 'If the partner is an IRA, enter the TIN of the CUSTODIAN of the IRA. Do "
                 "not enter the TIN of the person for whom the IRA is maintained. Do not truncate the "
                 "partner's TIN.' ⚠ An IRA is ALSO INELIGIBLE for the PTE election (A.R.S. 43-1014(C) "
                 "limits it to individuals, estates and trusts), so the partner is an 'O' in column "
                 "(f) and belongs in Schedule E line E7."),
     "notes": "⚠ FORM 120S HAS NO IRA-CUSTODIAN RULE — S corporations generally cannot have IRA "
              "shareholders. DO NOT PORT IT."},
    {"diagnostic_id": "D_AZ165_LOOKTHROUGH_E1_E3", "severity": "info",
     "title": "Look-through partners are counted in E1-E3 — the INDIVIDUAL rows",
     "condition": "a partner is a grantor trust or an SMLLC disregarded to an individual and did not opt out",
     "message": ("Verbatim: 'If the partner is a disregarded entity (grantor trust or SMLLC that is "
                 "disregarded to an individual) that did not opt out of the PTE election, include "
                 "those partners and their distributive shares in the totals for LINES E1 THROUGH E3, "
                 "columns (b) and (c).' A grantor trust therefore lands on the INDIVIDUAL rows, NOT on "
                 "the estate/trust rows E4-E5. In Schedule D, enter only the BENEFICIAL OWNER'S name, "
                 "address, TIN and RESIDENCY."),
     "notes": ("Counter-intuitive and easy to get wrong; it is a common cause of an E8 cross-foot "
               "failure. ⚠ Note the two roles of a disregarded SMLLC: it is OUT of Form 165 as a FILER "
               "(PTR 97-2 / CTR 97-2) but CAN be a PTE-participating OWNER. Do not collapse them.")},
    {"diagnostic_id": "D_AZ165_SPECIAL_ALLOCATION", "severity": "info",
     "title": "Special allocations ARE honoured on Form 165 — and are FORBIDDEN on Form 120S",
     "condition": "the partnership operating agreement specifies a special allocation",
     "message": ("Verbatim: 'If the partnership operating agreement specifies partnership proceeds are "
                 "to be distributed on the basis of a special allocation, complete columns (g) and (h) "
                 "using that allocation method.' Pub 713 carries a worked example. THERE IS NO "
                 "S-CORPORATION ANALOGUE: 'An S Corporation may not allocate its income and loss items "
                 "to its shareholders using a special allocation.'"),
     "notes": "This asymmetry must be encoded, not smoothed over — Form 165 Schedule D is by "
              "DISTRIBUTIVE SHARE, Form 120S Schedule B is by OWNERSHIP SHARE."},
    {"diagnostic_id": "D_AZ165_INFO_PENALTY_CONFLICT", "severity": "error",
     "title": "An electing partnership cannot carry an information-return penalty",
     "condition": "question A = Yes AND (line 7 != 0 OR line 36 != 0)",
     "message": ("'Partnerships that made the PTE election, this is not an information return.' The "
                 "information return penalty ($100 per month or fraction, capped at $500) applies ONLY "
                 "to partnerships that did NOT make the PTE election. Pub 713 was asked directly: "
                 "'Does the Information Return Penalty apply if a partnership or S Corporation made "
                 "the PTE election...? No.' Lines 7 and 36 must be zero."),
     "notes": "Form 120S carries the identical rule at its line 32: 'S Corporations that made the PTE "
              "election ... Do not enter an amount on line 32.'"},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM AZ_165 — TEST SCENARIOS (arithmetic oracles and pinned negatives)
# ═══════════════════════════════════════════════════════════════════════════
AZ165_SCENARIOS: list[dict] = [
    {"scenario_name": "AZ-165 ordinary electing partnership — all-resident, Arizona-only",
     "scenario_type": "normal", "sort_order": 1,
     "inputs": {"question_A": True, "question_D_arizona_only": True, "line_1": 1_000_000,
                "A1": 200_000, "A2": 0, "A3": 0, "A4": 0,
                "B1": 200_000, "B2": 0, "B3": 0, "B4": 0, "B5": 0,
                "line_9": 0, "E1_c": "1.000000", "E7_c": "0.000000"},
     "expected_outputs": {"line_2": 200_000, "line_3": 1_200_000, "line_4": 200_000,
                          "line_5": 1_000_000, "line_6": 0, "line_10": 1_000_000,
                          "line_11": "1.000000", "line_12": 1_000_000, "line_19": 1_000_000,
                          "line_20": 25_000, "line_21": 0, "line_24": 0, "line_25": 25_000,
                          "line_22": "1.0"},
     "notes": ("The post-2016 tier is NET-ZERO: the A1 add-back and the B1 subtraction cancel, so "
               "line 6 = 0 and line 5 = line 1. 2.5% of $1,000,000 = $25,000. Question D = Yes means "
               "ARIZONA-ONLY, so line 22 = 1.0.")},
    {"scenario_name": "AZ-165 PRE-2017 ASSET ORACLE — the tiers do NOT cancel, and the PTE base moves",
     "scenario_type": "edge", "sort_order": 2,
     "inputs": {"question_A": True, "line_1": 1_000_000, "A1": 100_000,
                "asset_placed_in_service_ty": 2014, "federal_168k_bonus_in_A1": 60_000,
                "B1": 46_000, "E1_c": "1.000000"},
     "expected_outputs": {"az_bonus_pct": "0.10", "line_5": 1_054_000, "line_6": 54_000,
                          "line_25": 26_350,
                          "note": "an identical S corporation would compute its PTE base with NO adjustment"},
     "notes": ("The TY2014 tier allows only 10% of the federal IRC 168(k) bonus: $100,000 federal "
               "depreciation of which $60,000 was bonus recomputes to $40,000 + $6,000 = $46,000. "
               "Line 5 = 1,000,000 + 100,000 - 46,000 = 1,054,000; line 6 = +54,000; tax = 2.5% x "
               "1,054,000 = 26,350. ⚠ THIS IS THE PROOF THAT THE 165/120S ASYMMETRY IS REAL ECONOMICS "
               "AND NOT BOOKKEEPING: the individual regime is net-zero ONLY for post-2016 assets.")},
    {"scenario_name": "AZ-165 DEPRECIATION TIER ORACLE — all five placed-in-service windows",
     "scenario_type": "edge", "sort_order": 3,
     "inputs": {"placed_in_service_years": [2010, 2012, 2013, 2014, 2015, 2016, 2017, 2025]},
     "expected_outputs": {"2010": "0.00", "2012": "0.00", "2013": "ITP_16_2", "2014": "0.10",
                          "2015": "0.10", "2016": "0.55", "2017": "1.00", "2025": "1.00",
                          "tier_count": 5},
     "notes": ("⚠ FIVE TIERS, NOT FOUR — the brief's heading said four and was corrected on "
               "verification; the instruction and its table both carry five windows. ⚠ A calendar-2012 "
               "taxable year BEGINS 1/1/2012, i.e. BEFORE 12/31/2012, so it is tier 1. ⚠ TY2013 "
               "returns the ITP_16_2 sentinel with a NULL percentage — that is the U1 gap, not a bug.")},
    {"scenario_name": "AZ-165 $150,000 BOUNDARY — EXACTLY at the threshold is OUT",
     "scenario_type": "edge", "sort_order": 4,
     "inputs": {"prior_year_taxable_income": 150_000},
     "expected_outputs": {"estimated_payments_required": False, "boundary": "exceeds",
                          "at_150_001_required": True, "at_149_999_required": False},
     "notes": ("⚠⚠ PINNED IN BOTH DIRECTIONS SO IT CANNOT DRIFT BACK. A.R.S. 43-581(C) says 'EXCEEDS "
               "$150,000' and so do all six AZDOR instruction sets — SEVEN sources. ONE Pub 713 FAQ "
               "answer says 'or more' and Pub 713's own FAQ lead-in says 'meets or exceeds' — three "
               "phrasings in one document. AN EARLIER VERIFICATION PASS FLIPPED THIS THE WRONG WAY IN "
               "conformity/az_conformity.md AND A LATER PASS CAUGHT IT. Vintage-clean: 43-581 is "
               "amended by neither Laws 2025 Ch. 182 nor Laws 2026 Ch. 140.")},
    {"scenario_name": "AZ-165 $150,000 MEASUREMENT BASIS — the ruled base, with the losers on record",
     "scenario_type": "edge", "sort_order": 5,
     "inputs": {"arizona_taxable_income": 1_000_000, "consenting_ownership_share": "0.10",
                "pte_income": 100_000},
     "expected_outputs": {"ruled_basis": "statutory_bare_taxable_income",
                          "candidate_count": 4, "unverified_item": "U19",
                          "under_arizona_taxable_income_basis": "IN",
                          "under_pte_income_basis": "OUT"},
     "notes": ("⚠ THE WORKED DIVERGENCE THAT MADE THIS BLOCKING: the SAME entity is IN under AZDOR's "
               "base 2 and OUT under AZDOR's base 3, from readings printed in the SAME instruction "
               "book, and it decides whether the Form 220/PTE underpayment penalty applies. CAMPAIGN "
               "D-12 A1 RULED the statute's bare 'taxable income' — A RULING ON A CONTESTED QUESTION, "
               "NOT A PUBLISHED AZDOR POSITION. All four candidates stay on the record so a DOR answer "
               "can be adjudicated rather than inherited.")},
    {"scenario_name": "AZ-165 A1 REFINED — the ruled SOURCE resolves to a computable NUMBER",
     "scenario_type": "edge", "sort_order": 17,
     "inputs": {"form_code": "AZ_165", "prior_year_line_5": 1_000_000,
                "prior_year_line_10_for_contrast": 1_180_000},
     "expected_outputs": {"basis_source": "statutory_bare_taxable_income",
                          "basis_resolves_to": "arizona_taxable_income",
                          "definition": "A.R.S. 43-1401(2)",
                          "figure": 1_000_000, "source_line": "PRIOR-YEAR Form 165 line 5",
                          "required": True, "provisional": True,
                          "is_engineering_inference": False,
                          "line_10_would_be_a_FIFTH_reading": True},
     "notes": ("⚠ THE SECOND STEP A1 ORIGINALLY LACKED. § 43-1401(2) is 'Arizona gross income "
               "adjusted by the modifications specified in sections 43-1021 and 43-1022 and section "
               "43-1414, subsection A' = FORM 165 LINE 5. ⚠⚠ NOT LINE 10: line 8 (= line 5) PLUS line "
               "9 reconstructs 43-1014(B)(1)(a)(ii), so line 10 is the larger PTE BASE and using it "
               "here would be a FIFTH reading no AZDOR document prints. The determination stays "
               "PROVISIONAL because U19 is open.")},
    {"scenario_name": "AZ-165 PART 2 GATE — no election, but PTE estimates were paid",
     "scenario_type": "edge", "sort_order": 6,
     "inputs": {"question_A": False, "pte_estimated_payments_made": 40_000},
     "expected_outputs": {"part2_required": True, "line_37_120s_analogue": 0, "line_25": 0,
                          "refund_to_entity": 40_000, "refund_applicable_to_next_year": False,
                          "refund_applicable_to_owner": False},
     "notes": ("⚠ THE MOST LIKELY REAL-WORLD ARIZONA PTE SCENARIO FOR TY2025. Both Part 2 headers say "
               "'or estimated payments were made and the partnership is not claiming the PTE "
               "election', and Pub 713 frames it around the federal SALT deduction rising from $10,000 "
               "to $40,000. A loader branching on question A alone SUPPRESSES PART 2 FOR EXACTLY THIS "
               "POPULATION (W18). The refund goes to the ENTITY as cash and cannot be applied forward "
               "or to an owner.")},
    {"scenario_name": "AZ-165 APPORTIONMENT DIVISOR — sales excluded gives TWO, not three",
     "scenario_type": "edge", "sort_order": 7,
     "inputs": {"property_num": 0, "property_den": 0, "payroll_num": 0, "payroll_den": 5_000_000,
                "sales_num": 0, "sales_den": 0},
     "expected_outputs": {"property_excluded": True, "payroll_excluded": False,
                          "sales_excluded": True, "divisor": None,
                          "rule": "two factors excluded -> the remaining factor IS the ratio, unweighted"},
     "notes": ("⚠ A ZERO NUMERATOR OVER A POSITIVE DENOMINATOR IS A LIVE ZERO FACTOR, NOT AN EXCLUDED "
               "ONE (A.A.C. R15-2D-901(B)) — payroll stays in at 0.000000. With property and sales "
               "both excluded there is NO DIVISOR AT ALL and payroll IS the ratio. ⚠ Had ONLY sales "
               "been excluded the divisor would be TWO even though sales is DOUBLE-WEIGHTED — the "
               "weighting and the divisor are not tied together.")},
    {"scenario_name": "AZ-165 NEXUS SEMANTICS — 0.000000 and blank mean OPPOSITE things",
     "scenario_type": "failure", "sort_order": 8,
     "inputs": {"schedule_c_line_C5_values": ["0.000000", None, "1.000000", "0.372500"]},
     "expected_outputs": {"0.000000": "no Arizona nexus",
                          "None": "income sourced ENTIRELY within Arizona (same as 1.000000)",
                          "1.000000": "income sourced ENTIRELY within Arizona (same as 1.000000)",
                          "0.372500": "apportioned"},
     "notes": ("⚠ A NULL-VS-ZERO BUG HERE SILENTLY ZEROES EVERY NONRESIDENT PARTNER'S ARIZONA INCOME. "
               "Stated verbatim on the face of both returns.")},
    {"scenario_name": "AZ-165 A4 CORPORATE PARTNER — pass through, do NOT recompute",
     "scenario_type": "failure", "sort_order": 9,
     "inputs": {"partner_type": "C corporation", "k1nr_line15_column_a": 54_000},
     "expected_outputs": {"pass_through_amount": 54_000, "column": "(a)",
                          "recomputed_on_corporate_basis": None,
                          "review_diagnostic": "D_AZ165_A4_CORP_PARTNER_BASIS",
                          "destination": "Form 120/120A Schedule A line A8 (positive)"},
     "notes": ("⚠⚠ CAMPAIGN RULING D-12 A4. The figure was computed on the INDIVIDUAL full-168(k) "
               "basis while A.R.S. 43-1122(20) puts the corporate partner on the ELECT-OUT basis, and "
               "no Arizona form line carries a recomputation. PASS THE FIGURE THROUGH AS THE K-1 "
               "PRINTS IT AND RAISE THE DIAGNOSTIC. Computing a corporate-basis figure would invent a "
               "position Arizona has never stated. U2 stays open as a fact.")},
    {"scenario_name": "AZ-165 § 43-1021(15) ENTITY ADD-BACK — the guard must REFUSE",
     "scenario_type": "failure", "sort_order": 10,
     "inputs": {"attempt": "az_entity_level_pte_addback(pte_tax_paid=25000)"},
     "expected_outputs": {"raises": "ArizonaFormGovernsError",
                          "entity_addback_built": False, "owner_addback_built": True,
                          "page6_a4_worksheet_rows": 3, "free_text_other_row_exists": False},
     "notes": ("⚠ D-12 A3: BUILD TO THE FORM, OWNER LEVEL ONLY. The statute wants the add-back in TWO "
               "places; the forms carry only one. THE CASH-BASIS CIRCULARITY IS REAL AND IS RECORDED "
               "RATHER THAN FIXED: line 1 is already net of the PTE tax paid during the year, so the "
               "base is understated by the tax itself. Same shape as D-10 ruling 2 (Missouri) and "
               "D-11 A1 (Colorado 174A).")},
    {"scenario_name": "AZ-165 FORM 165PA — the rate helper must REFUSE, not choose",
     "scenario_type": "failure", "sort_order": 11,
     "inputs": {"attempt": "az_165pa_rate()"},
     "expected_outputs": {"raises": "ArizonaDeferredFormError", "face_rate": "0.045",
                          "statutory_rate": "0.025", "overtax_factor": 1.8,
                          "late_filing_penalty_still_4_5_pct": True},
     "notes": ("⚠ D-12 A2: DEFER RATHER THAN PICK. Building to the face knowingly OVER-TAXES BY 80%; "
               "building to the statute contradicts a printed FINAL form. Both negatives verified: "
               "S.B. 1274 Sec. 7 amended only 43-1414(A), and H.B. 4168 does not touch 43-1414 at all. "
               "⚠ DO NOT CONFLATE THE TWO 4.5%s — the 165PA LATE-FILING PENALTY is 4.5% and is "
               "CORRECT.")},
    {"scenario_name": "AZ-165 SCHEDULE E CROSS-FOOT with a look-through grantor trust",
     "scenario_type": "edge", "sort_order": 12,
     "inputs": {"partners": "2 resident individuals at .400000 each, 1 grantor trust disregarded to an "
                            "individual at .150000 (did not opt out), 1 upper-tier partnership at .050000",
                "E1_c": "0.950000", "E4_c": "0.000000", "E7_c": "0.050000"},
     "expected_outputs": {"E1_c": "0.950000", "E4_c": "0.000000", "E7_c": "0.050000",
                          "E8_c": "1.000000", "grantor_trust_row": "E1, not E4",
                          "upper_tier_partnership_row": "E7 (ineligible entity)"},
     "notes": ("⚠ THE GRANTOR TRUST GOES IN E1, NOT E4 — look-through owners that did not opt out are "
               "counted in E1-E3, THE INDIVIDUAL ROWS. ⚠ The upper-tier partnership is INELIGIBLE "
               "(A.R.S. 43-1014(C)(1)) and lands in E7 as an 'O'. E8 column (c) must still equal "
               "1.000000.")},
    {"scenario_name": "AZ-165 LINE 37 SKIPS LINE 33, and a negative line 38 crosses over",
     "scenario_type": "edge", "sort_order": 13,
     "inputs": {"line_25": 10_000, "line_31": 12_000, "line_34": 500, "line_35": 2_000, "line_36": 0},
     "expected_outputs": {"line_32": 0, "line_33": 2_000, "line_38_raw": -500,
                          "line_38": 0, "line_37": 500},
     "notes": ("Line 38 verbatim: 'subtract the total of lines 34 through 36 from line 33. Enter a "
               "POSITIVE number on line 38. IF THE DIFFERENCE IS NEGATIVE, ENTER THE DIFFERENCE AS A "
               "POSITIVE NUMBER ON LINE 37.' 2,000 - 2,500 = -500, so $500 becomes an amount DUE. "
               "⚠ Line 37's own formula is 32 + 34 + 35 + 36 and SKIPS line 33.")},
    {"scenario_name": "AZ-165 PTE INSTALLMENTS — the fourth is the 1st month AFTER year end",
     "scenario_type": "edge", "sort_order": 14,
     "inputs": {"filer": "calendar-year electing partnership", "prior_year_taxable_income": 400_000},
     "expected_outputs": {"estimated_payments_required": True, "installments": 4,
                          "dates": ["April 15", "June 15", "September 15",
                                    "January 15 of the following year"],
                          "corporate_pattern_would_give": ["4th", "6th", "9th", "12th"]},
     "notes": ("⚠ FORM 220/PTE LINE 7 PRINTS THE CORPORATE PATTERN ON THE FACE and appends 'PTE's see "
               "instructions'. A loader reading the face alone puts the fourth installment THREE "
               "MONTHS EARLY (W17). Required annual payment = THE SMALLER OF 90% current-year or 100% "
               "prior-year — a safe harbour, not a minimum. No penalty if the Arizona liability due is "
               "under $1,000 (43-581(E)(2)); no overpayment penalty at all.")},
    {"scenario_name": "AZ-165 INFORMATION RETURN PENALTY is mutually exclusive with the election",
     "scenario_type": "failure", "sort_order": 15,
     "inputs": {"question_A": True, "months_late": 8, "line_7_attempted": 500},
     "expected_outputs": {"line_7": 0, "line_36": 0,
                          "diagnostic": "D_AZ165_INFO_PENALTY_CONFLICT",
                          "if_not_electing_would_be": 500},
     "notes": ("$100/month or fraction, capped at $500 — so eight months late is capped at $500 for a "
               "NON-electing partnership. 'Partnerships that made the PTE election, this is not an "
               "information return.' Pub 713 answered the question directly: 'No.'")},
    {"scenario_name": "AZ-165 MULTISTATE GATE — question D is INVERTED relative to Form 120S",
     "scenario_type": "failure", "sort_order": 16,
     "inputs": {"az165_question_D_answer_yes": True, "az120s_question_B_answer_yes": True},
     "expected_outputs": {"az_is_multistate_AZ_165": False, "az_is_multistate_AZ_120S": True,
                          "shared_boolean_would_be": "wrong for one of them"},
     "notes": ("⚠ Form 165 question D asks 'Is this partnership an ARIZONA-ONLY partnership?'; Form "
               "120S question B asks 'Does the S corporation conduct business WITHIN AND WITHOUT "
               "Arizona?'. Same concept, opposite polarity. az_is_multistate() takes the form code and "
               "REFUSES an unknown one rather than defaulting.")},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM AZ_120S — FACTS
# ⚠ THERE ARE NO MODIFICATION FACTS HERE, AND THAT IS THE POINT. Form 120S has
# no additions schedule, no subtractions schedule, no depreciation line and no
# 'Arizona basis' line. If you are about to add one "for symmetry with AZ_165",
# read AZ_120S_NEGATIVE_PROOF first — validate_az.py pins the absence.
# ═══════════════════════════════════════════════════════════════════════════
AZ120S_FACTS: list[dict] = [
    {"fact_key": "az120s_return_type", "label": "CHECK ONE: Original / Amended", "data_type": "choice",
     "choices": ["Original", "Amended"], "required": True, "sort_order": 1,
     "notes": ("'Do NOT file an amended return until your original return has been processed.' Any S "
               "corporation that files an amended federal return must report the changes to Arizona. "
               "⚠ On an amended return, DO NOT RECOMPUTE the estimated tax underpayment penalty — "
               "carry line 31 from the original return or from an AZDOR correction notice.")},
    {"fact_key": "az120s_filed_under_extension", "label": "Return filed under extension (box 82F)",
     "data_type": "boolean", "sort_order": 2,
     "notes": "⚠ `82F` HERE, `82E` ON FORM 165 — same revenue-use field 82, different letter. "
              "Transcribe each as printed."},
    {"fact_key": "az120s_q_a_pte_election",
     "label": ("A. Did the S Corporation make the Pass-Through Entity (PTE) election to pay tax on its "
               "flow-through income at the entity level?"),
     "data_type": "boolean", "required": True, "sort_order": 10,
     "notes": ("THE MASTER BRANCH → Part 2 + Schedule C. ⚠ BUT PART 2 IS NOT GATED ON THIS ALONE — see "
               "az120s_pte_estimates_paid and the Part 2 header.")},
    {"fact_key": "az120s_pte_estimates_paid",
     "label": "PTE estimated payments made during the taxable year (drives the Part 2 gate)",
     "data_type": "decimal", "sort_order": 11,
     "notes": ("⚠ The Part 2 header adds: '... or if estimated payments were made and the S "
               "Corporation is not claiming the PTE election. If estimated payments were made and the "
               "S Corporation is not claiming the PTE election, SEE THE INSTRUCTIONS BEFORE COMPLETING "
               "PART 2.' The book then scripts the '$0 return' line by line, in TWO VARIANTS.")},
    {"fact_key": "az120s_q_b_conducts_business_within_and_without",
     "label": "B. Does the S corporation conduct business within and without Arizona?",
     "data_type": "boolean", "required": True, "sort_order": 12,
     "notes": ("⚠⚠ INVERTED RELATIVE TO FORM 165 QUESTION D. Here 'Yes' MEANS MULTISTATE; on Form 165 "
               "'Yes' means ARIZONA-ONLY. A shared boolean is wrong for one of them — use "
               "az_is_multistate(form_code, answer), which refuses an unknown form code.")},
    {"fact_key": "az120s_q_c_apportionment_method",
     "label": "C. ARIZONA apportionment for Multistate S Corporations only (check one box)",
     "data_type": "choice", "choices": ["1 AIR CARRIER", "2 STANDARD", "3 SALES FACTOR ONLY"],
     "sort_order": 13,
     "notes": "The Schedule A branch. The methods are MUTUALLY EXCLUSIVE — a taxpayer cannot compute "
              "one factor under STANDARD and another under SALES FACTOR ONLY."},
    {"fact_key": "az120s_q_d_msp_included", "label": "D. Arizona Schedule MSP is included",
     "data_type": "boolean", "sort_order": 14},
    {"fact_key": "az120s_q_d_msp_cycle_year", "label": "D. Year of the MSP election cycle (Yr 1 - Yr 5)",
     "data_type": "choice", "choices": ["Yr 1", "Yr 2", "Yr 3", "Yr 4", "Yr 5"], "sort_order": 15,
     "notes": "⚠ A FIVE-YEAR IRREVOCABLE ELECTION requiring a TIMELY FILED ORIGINAL RETURN "
              "(§ 43-1147(C)) — the opposite timeliness rule from the PTE election on the same form."},
    {"fact_key": "az120s_q_e_final_return",
     "label": "E. Is this the S corporation's final Arizona return under this EIN?",
     "data_type": "boolean", "sort_order": 16,
     "notes": "⚠ RICHER THAN FORM 165's: if 'Yes', check one of Dissolved / Withdrawn / "
              "Merged-Reorganized and list the successor corporation's EIN. Do not share the field."},
    {"fact_key": "az120s_q_e_final_reason", "label": "E. Final-return reason",
     "data_type": "choice", "choices": ["1 Dissolved", "2 Withdrawn", "3 Merged/Reorganized"],
     "sort_order": 17},
    {"fact_key": "az120s_q_f_composite_return",
     "label": "F. Will a composite return be filed on Arizona Form 140NR?", "data_type": "boolean",
     "sort_order": 18,
     "notes": "Minimum TEN nonresident shareholders, ALL of whom must have OPTED OUT of the PTE "
              "election (ITR 16-2)."},
    {"fact_key": "az120s_q_g_marijuana_licence",
     "label": "G. Marijuana Establishments only — licence configuration", "data_type": "choice",
     "choices": ["1 Adult Use only", "2 Dual Lic. elected for-profit",
                 "3 Dual Lic. did not elect for-profit", "4 NMMD only"], "sort_order": 19,
     "notes": "⚠ An NMMD-only S corporation subject to federal corporate-level tax 'is NOT subject to "
              "Arizona corporate income tax. Do not complete lines 2 through 12.'"},
    {"fact_key": "az120s_q_h_adhs_registry_id", "label": "H. ADHS Registry Identification Number",
     "data_type": "string", "sort_order": 20},

    # --- Part 1 -------------------------------------------------------------
    {"fact_key": "az120s_l1_total_distributive_income",
     "label": "1. TOTAL DISTRIBUTIVE INCOME (LOSS) from federal Form 1120-S, Schedule K",
     "data_type": "decimal", "required": True, "sort_order": 30,
     "notes": ("⚠⚠ ONE AGGREGATE FEDERAL NUMBER, AND ARIZONA APPLIES **NO MODIFICATIONS** TO IT. "
               "Verbatim: 'Enter the net total of the pro rata share items of nonseparately computed "
               "income (loss) and separately stated income (loss) and deductions (from federal Form "
               "1120S, Schedule K).' Line 37 = this line, unadjusted. There is no Schedule A/B stack, "
               "no depreciation line, no separately-stated add-back, and no 'Arizona basis' anywhere "
               "on this form. VERIFIED NEGATIVE — see AZ_120S_NEGATIVE_PROOF.")},
    {"fact_key": "az120s_l2_excess_net_passive_income", "label": "2. Excess net passive income",
     "data_type": "decimal", "sort_order": 31,
     "notes": "From the federal Form 1120-S worksheet. Only reached if the S corporation was subject "
              "to federal-level tax."},
    {"fact_key": "az120s_l3_capital_and_built_in_gains", "label": "3. Capital gains/built-in gains",
     "data_type": "decimal", "sort_order": 32,
     "notes": "Same federal worksheet. Lines 2 and 3 are FEDERAL figures taken straight across."},
    {"fact_key": "az120s_l4a_100pct_arizona", "label": "4a. 100% Arizona S Corporation (checkbox)",
     "data_type": "boolean", "sort_order": 33,
     "notes": "If checked, go to line 11 and enter line 4. Multistate S corporations continue to line 5."},
    {"fact_key": "az120s_l5_nonapportionable_income",
     "label": "5. Nonapportionable or allocable income (include schedule; multistate only)",
     "data_type": "decimal", "sort_order": 34,
     "notes": "⚠ A SCHEDULE IS REQUIRED and the form provides none — a free-form attachment."},
    {"fact_key": "az120s_l9_other_income_allocated_to_az",
     "label": "9. Other income allocated to Arizona (include schedule; multistate only)",
     "data_type": "decimal", "sort_order": 35},
    {"fact_key": "az120s_l13_credit_recapture",
     "label": "13. Tax from recapture of tax credits from Arizona Form 300, Part 2, line 22",
     "data_type": "decimal", "sort_order": 36,
     "notes": ("⚠ FORM 165 HAS NO RECAPTURE LINE AT ALL. An S corporation with ONLY a recapture "
               "liability completes lines 13-36 and skips 2-12.")},
    {"fact_key": "az120s_l15_nonrefundable_credits",
     "label": "15. Nonrefundable tax credits from Arizona Form 300, Part 2, line 40",
     "data_type": "decimal", "sort_order": 37,
     "notes": ("⚠⚠ APPLIED AGAINST LINE 14 (corporate tax + recapture) AND THE PTE TAX IS ADDED "
               "AFTERWARDS AT LINE 18/19 — SO NONREFUNDABLE CREDITS CANNOT REDUCE THE PTE TAX. Pub 713 "
               "says both 'No' and 'nothing precludes' in the same section (U4 / W7); THE FORM IS NOT "
               "AMBIGUOUS AND THE FORM GOVERNS. ⚠ Form 165 has NO entity-level credit line at all.")},
    {"fact_key": "az120s_l16_credit_form_numbers",
     "label": "16. Form number for each nonrefundable credit claimed (fields 161-164)",
     "data_type": "string", "sort_order": 38,
     "notes": "⚠ Form 315 (Pollution Control Credit): 'An S Corporation may claim this credit at the "
              "corporate level. An S Corporation may NOT pass this credit through to its shareholders.'"},
    {"fact_key": "az120s_l20_refundable_credits",
     "label": "20. Refundable tax credits (check 308 / 334 / 349; enter amount)", "data_type": "decimal",
     "sort_order": 39,
     "notes": "⚠ REFUNDABLE credits sit in the PAYMENTS block and therefore CAN reduce what is owed on "
              "the PTE tax, unlike the nonrefundable credits at line 15."},
    {"fact_key": "az120s_l21_extension_payment",
     "label": "21. Extension payment made with Form 120/165EXT or online", "data_type": "decimal",
     "sort_order": 40},
    {"fact_key": "az120s_l22_estimated_payments", "label": "22. Estimated tax payments",
     "data_type": "decimal", "sort_order": 41,
     "notes": "⚠ = Schedule D line D7 COLUMN (c) PLUS COLUMN (d) — the S-corp estimates AND the PTE "
              "estimates. Form 165's Schedule F has only one estimated column."},
    {"fact_key": "az120s_l23_amended_payments",
     "label": "23. Amended Returns: payments made with original return plus all payments after filing",
     "data_type": "decimal", "sort_order": 42},
    {"fact_key": "az120s_l25_prior_overpayments",
     "label": "25. Overpayments of tax from original return or later adjustments", "data_type": "decimal",
     "sort_order": 43,
     "notes": ("⚠ FORM 220/PTE'S FACE LINE 37 WRONGLY ROUTES THE ESTIMATED-PENALTY FIGURE TO THIS "
               "LINE. This is an OVERPAYMENT line; the penalty line is 31 (U20 / W25).")},
    {"fact_key": "az120s_l30_penalty_and_interest", "label": "30. Penalty and interest",
     "data_type": "decimal", "sort_order": 44},
    {"fact_key": "az120s_l31_estimated_underpayment_penalty",
     "label": "31. Estimated tax underpayment penalty (Form 220/PTE Part C line 37; box 31A)",
     "data_type": "decimal", "sort_order": 45,
     "notes": "⚠ BUILD FROM THE FORM 120S INSTRUCTIONS, NOT FROM THE 220/PTE FACE ROUTING LIST. On an "
              "amended return, do not recompute."},
    {"fact_key": "az120s_l32_information_return_penalty",
     "label": "32. Information return penalty", "data_type": "decimal", "sort_order": 46,
     "notes": "⚠ NON-ELECTING S CORPORATIONS ONLY: 'S Corporations that made the PTE election, this is "
              "not an information return. Do not enter an amount on line 32.' $100/month, capped $500."},
    {"fact_key": "az120s_l35_overpayment_applied_2026",
     "label": "35. Amount of line 34 to be applied to 2026 estimated tax", "data_type": "decimal",
     "sort_order": 47,
     "notes": "⚠ CORRECTLY PRINTS 2026 — unlike Form 165 line 39, which prints a stale 2025 (AZ-D1)."},

    # --- Part 2 -------------------------------------------------------------
    {"fact_key": "az120s_l43a_part_year_resident_portion",
     "label": "43A. Portion of line 43 earned while RESIDENTS of Arizona", "data_type": "decimal",
     "sort_order": 50,
     "notes": "43A + 43B must equal line 43 — printed on the face."},
    {"fact_key": "az120s_l43b_part_year_nonresident_portion",
     "label": "43B. Portion of line 43 earned while NONRESIDENTS of Arizona", "data_type": "decimal",
     "sort_order": 51},

    # --- Schedules ----------------------------------------------------------
    {"fact_key": "az120s_scha_property_inventories",
     "label": "Schedule A A1a1. Inventories (original cost)", "data_type": "decimal", "sort_order": 60},
    {"fact_key": "az120s_scha_property_depreciable",
     "label": "Schedule A A1a2. Depreciable assets (do not include construction in progress)",
     "data_type": "decimal", "sort_order": 61},
    {"fact_key": "az120s_scha_property_land", "label": "Schedule A A1a3. Land", "data_type": "decimal",
     "sort_order": 62},
    {"fact_key": "az120s_scha_property_other", "label": "Schedule A A1a4. Other assets (describe)",
     "data_type": "decimal", "sort_order": 63},
    {"fact_key": "az120s_scha_property_nonbusiness",
     "label": "Schedule A A1a5. Less: Nonbusiness property", "data_type": "decimal", "sort_order": 64},
    {"fact_key": "az120s_scha_rented_property_net_rent",
     "label": "Schedule A A1b. Rented property — net annual rental rate (capitalised at 8×)",
     "data_type": "decimal", "sort_order": 65,
     "notes": "Net = annual rent LESS aggregate annual subrental rates paid by subtenants."},
    {"fact_key": "az120s_scha_payroll",
     "label": ("Schedule A A2. Total wages, salaries, commissions and other compensation (per federal "
               "Form 1120S, or payroll reports)"),
     "data_type": "decimal", "sort_order": 66,
     "notes": "⚠ 'per federal Form 1120S' — Form 165's Schedule C says 'per federal Form 1065' in the "
              "same slot. The only wording difference between the two apportionment schedules."},
    {"fact_key": "az120s_scha_sales_to_az_purchasers",
     "label": "Schedule A A3a. Sales delivered or shipped to Arizona purchasers", "data_type": "decimal",
     "sort_order": 67},
    {"fact_key": "az120s_scha_msp_service_sales",
     "label": "Schedule A A3b. Sales from services / designated intangibles (MSP electors only)",
     "data_type": "decimal", "sort_order": 68},
    {"fact_key": "az120s_scha_other_gross_receipts", "label": "Schedule A A3c. Other gross receipts",
     "data_type": "decimal", "sort_order": 69},
    {"fact_key": "az120s_shareholder_rows",
     "label": "Schedule B. Shareholder rows B1-B10 (name, address, TIN, residency code, share)",
     "data_type": "string", "sort_order": 70,
     "notes": ("⚠ COLUMN (h) POINTS AT **LINE 1**, not line 5 — the same column position as Form 165's "
               "Schedule D but a DIFFERENT SOURCE LINE, and the 165/120S asymmetry showing up a second "
               "time. ⚠ SPECIAL ALLOCATIONS ARE FORBIDDEN: 'An S Corporation may not allocate its "
               "income and loss items to its shareholders using a special allocation.' ⚠ NO "
               "IRA-CUSTODIAN RULE HERE — do not port Form 165's. Column (f) codes are the same five "
               "letters but the parenthetical differs ('C corporation, S Corporation, etc.' vs "
               "'corporation, partnership, etc.'). More than 10 shareholders → additional schedules.")},
    {"fact_key": "az120s_sched_c_rows",
     "label": "Schedule C. Summary rows C1-C8 (consent, count, ownership share)", "data_type": "string",
     "sort_order": 71,
     "notes": ("Gate: 'S Corporations making the PTE election, complete Schedule C. All others, skip to "
               "Schedule E.' ⚠ C8 COLUMN (c) SHOULD **TOTAL** 1.000000 (Form 165's E8 says 'should "
               "EQUAL' — a cosmetic wording difference, same rule). ⚠ Look-through shareholders that "
               "did not opt out go in C1-C3. ⚠ Line C7 carries a pointer Form 165's E7 does not: 'Also "
               "enter this percentage in column (c) in Part 2, line 44.'")},
    {"fact_key": "az120s_schd_extension_payments",
     "label": "Schedule D line D7 column (b). Total extension payments", "data_type": "decimal",
     "sort_order": 72},
    {"fact_key": "az120s_schd_scorp_estimates",
     "label": "Schedule D line D7 column (c). Total S Corp estimated payments", "data_type": "decimal",
     "sort_order": 73},
    {"fact_key": "az120s_schd_pte_estimates",
     "label": "Schedule D line D7 column (d). Total PTE estimated payments", "data_type": "decimal",
     "sort_order": 74,
     "notes": ("⚠ SCHEDULE D HAS **FOUR** PAYMENT COLUMNS WHERE FORM 165'S SCHEDULE F HAS THREE, "
               "because an S corporation can owe BOTH a corporate-level tax AND a PTE tax in the same "
               "year. A partnership cannot. Line 22 = column (c) + column (d).")},
    {"fact_key": "az120s_sche_business_began_az",
     "label": "Schedule E1. Date business began in Arizona or income was first derived from Arizona sources",
     "data_type": "date", "sort_order": 75},
    {"fact_key": "az120s_sche_audit_contact",
     "label": "Schedule E3. Audit contact designation (name / phone / title)", "data_type": "string",
     "sort_order": 76,
     "notes": "⚠ THIS DESIGNATION AUTHORISES DISCLOSURE OF CONFIDENTIAL INFORMATION. No Form 165 "
              "counterpart."},
    {"fact_key": "az120s_sche_federal_exam_years",
     "label": "Schedule E4. Prior taxable years for which a federal examination has been finalised",
     "data_type": "string", "sort_order": 77,
     "notes": ("⚠ A.R.S. § 43-327 requires the taxpayer, WITHIN NINETY DAYS after final determination, "
               "to report these changes under separate cover or to file amended returns.")},
    {"fact_key": "az120s_sche_accounting_method",
     "label": "Schedule E5. Tax accounting method (Cash / Accrual / Other)", "data_type": "choice",
     "choices": ["Cash", "Accrual", "Other"], "sort_order": 78,
     "notes": ("⚠ MATERIAL TO THE § 43-1021(15) CIRCULARITY: a CASH-BASIS electing entity deducts the "
               "PTE tax federally in the year PAID, so line 1 is already net of it and the PTE base is "
               "understated by the tax itself. Arizona provides no entity-level add-back line (D-12 "
               "A3). No Form 165 counterpart field.")},
    {"fact_key": "az120s_paid_preparer_ptin", "label": "PAID PREPARER'S PTIN", "data_type": "string",
     "sort_order": 79,
     "notes": "⚠ 'PTIN' here; Form 165 prints 'TIN'. Transcribe each as printed."},
    {"fact_key": "az120s_prior_year_taxable_income",
     "label": "Prior-year taxable income (the § 43-581(C) $150,000 estimated-payment test)",
     "data_type": "decimal", "sort_order": 80,
     "notes": ("⚠ SAME TWO QUESTIONS AS ON FORM 165. Boundary: 'EXCEEDS' — exactly $150,000 is OUT "
               "(settled, seven sources). Basis: RULED to the statute's bare 'taxable income' (D-12 "
               "A1) and REFINED the same session to the figure A.R.S. § 43-1401(2) defines — ARIZONA "
               "TAXABLE INCOME — which on this return resolves to PRIOR-YEAR LINE 1. ⚠⚠ THAT LAST "
               "STEP IS AN ENGINEERING INFERENCE, NOT A PUBLISHED DEFINITION: § 43-1401 is a "
               "chapter-14 PARTNERSHIP definitions section with NO S-corp analogue, and Delvio "
               "reaches line 1 by BUILDING TO THE FORM — Form 120S has no Arizona modification "
               "apparatus, so there is nothing to adjust. See D_AZ120S_EST_BASIS_NO_ANALOGUE. U19 "
               "stays open as a fact. ⚠ THE FORM 120S INSTRUCTIONS THEMSELVES CONTRADICT THEMSELVES, "
               "using bare 'taxable income' in one place and 'PTE income' in another.")},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM AZ_120S — RULES
# ═══════════════════════════════════════════════════════════════════════════
AZ120S_RULES: list[dict] = [
    {"rule_id": "R-AZ120S-NO-MODS", "title": "⚠⚠ Form 120S has NO Arizona modification apparatus — a VERIFIED NEGATIVE",
     "rule_type": "classification", "sort_order": 1, "inputs": [],
     "outputs": ["az120s_modification_apparatus"],
     "formula": "AZ_120S_HAS_MODIFICATION_APPARATUS == False; az_120s_modification() RAISES",
     "description": ("⚠⚠ THIS IS 'THE RULE SAYS NO', NOT 'NO RULE FOUND'. The first evidence was "
                     "lexical (depreciation / bonus / 168(k) / 179 ≈ zero substantive hits, the sole "
                     "'179' being the digit string inside the apportionment example .179865) — a "
                     "textbook class-(b) risk — and a FALSE-POSITIVE ALARM was raised over 28 "
                     "'addition' and 42 'subtract*' hits in the same 28-page book. ALL 70 WERE READ IN "
                     "CONTEXT and resolve into five innocuous buckets: 23 x 'additional'; 2 x 'In "
                     "addition:'; 12 x pure line arithmetic; 3 x 'has no Arizona additions to, or "
                     "subtractions from, federal taxable income' — ALL THREE inside the Rounding "
                     "Dollar Amounts worked examples lifted from the Form 120 C-corp book, each "
                     "saying the company HAS NONE; and ~18 x the OWNER-LEVEL net long-term capital "
                     "gain subtraction, ALL of them in the Schedule K-1 instruction section at the "
                     "BACK of the book. THREE FURTHER INDEPENDENT PROOFS: (i) the Arizona modification "
                     "statutes 43-1021 / 43-1022 / 43-1121 / 43-1122 are cited ZERO times in the whole "
                     "book, while every Title 43 section it DOES cite is an APPORTIONMENT provision; "
                     "(ii) the face has no additions or subtractions schedule and the string 'Arizona "
                     "basis' occurs ZERO times; (iii) the CORPORATE-LEVEL chain is unadjusted too "
                     "(line 4 = 2 + 3 from federal, line 11 = 4 or 10, line 12 = greater of $50 or "
                     "4.9% of line 11). And the statute agrees: A.R.S. 43-1014(B)(1)(b) takes 'the "
                     "total of all distributive income passed through to the shareholders under "
                     "section 43-1126, subsection B', and 43-1126(B) is a REPORTING provision."),
     "exceptions": ("⚠ THE S-CORP SHAREHOLDER'S ARIZONA DEPRECIATION ADJUSTMENT STILL HAPPENS — on the "
                    "SHAREHOLDER'S OWN individual return under 43-1021(11) / 43-1022(17)(e), from the "
                    "shareholder's own records. Arizona simply does not compute it at the entity "
                    "level, which is internally consistent because individuals fully conform."),
     "notes": ("⚠ DO NOT ADD A 120S MODIFICATION FIELD 'FOR SYMMETRY' WITH AZ_165 OR WITH ANOTHER "
               "STATE. The asymmetry is real, statutory, and campaign D-12 Group B ratified it: NO "
               "SHARED ARIZONA MODIFICATION ENGINE. validate_az.py PINS the absence. ⚠ Had this gone "
               "the other way it would have wrongly stripped every Arizona S-corp return of its state "
               "adjustments — which is why it cost two research sessions.")},
    {"rule_id": "R-AZ120S-L1", "title": "Line 1 = federal Form 1120-S Schedule K total distributive income",
     "rule_type": "calculation", "sort_order": 2, "inputs": ["az120s_l1_total_distributive_income"],
     "outputs": ["AZ120S_L1"],
     "formula": "L1 = the net total of nonseparately computed income (loss) plus separately stated "
                "income (loss) and deductions, from federal Form 1120-S Schedule K",
     "description": ("ONE AGGREGATE NUMBER. Note it ALREADY reflects the federal § 179 deduction at "
                     "whatever federal limit applied, which is why the D-10 § 179 ruling is invisible "
                     "on this form — unlike Form 165, where § 179 rides in through line 9."),
     "exceptions": "", "notes": "Line 37 is this line, unadjusted."},
    {"rule_id": "R-AZ120S-CORP-TAX", "title": "Lines 2-11: the corporate-level base, taken straight from federal",
     "rule_type": "calculation", "sort_order": 3,
     "inputs": ["az120s_l2_excess_net_passive_income", "az120s_l3_capital_and_built_in_gains",
               "az120s_l4a_100pct_arizona", "az120s_l5_nonapportionable_income",
               "az120s_l9_other_income_allocated_to_az"],
     "outputs": ["AZ120S_L4", "AZ120S_L6", "AZ120S_L8", "AZ120S_L10", "AZ120S_L11"],
     "formula": ("L4 = L2 + L3; L6 = L4 − L5; L8 = L6 × L7; L10 = L8 + L9; "
                 "L11 = L4 (100% Arizona) or L10 (multistate)"),
     "description": ("'If the S Corporation was subject to the federal excess net passive income tax, "
                     "capital gains tax, or built-in gains tax on its federal Form 1120S, it is "
                     "subject to Arizona corporate income tax on the total of this income. Use the "
                     "federal worksheet included in the instructions for federal Form 1120S...' ⚠ "
                     "NOTHING IS ADDED TO OR SUBTRACTED FROM FEDERAL ANYWHERE IN THIS CHAIN — the "
                     "corporate-level base is unadjusted too, not just the PTE base."),
     "exceptions": ("⚠ An S corporation with ONLY a recapture liability skips lines 2-12 and completes "
                    "lines 13-36. ⚠ An NMMD-only marijuana S corporation subject to federal "
                    "corporate-level tax 'is not subject to Arizona corporate income tax. Do not "
                    "complete lines 2 through 12.' ⚠ Lines 5 and 9 each REQUIRE a schedule the form "
                    "does not provide."),
     "notes": "Form 165 has no corporate-level tax at all — a partnership cannot owe one."},
    {"rule_id": "R-AZ120S-L12-MIN", "title": "Line 12: greater of $50 or 4.9% — but ONLY if federal-level tax exists",
     "rule_type": "calculation", "sort_order": 4, "inputs": [], "outputs": ["AZ120S_L12"],
     "formula": "L12 = max(50, 0.049 × L11) IF the S corp has federal-level taxable income; else BLANK",
     "description": ("Verbatim: 'The S Corporation is subject to the tax computed on line 12 ONLY IF "
                     "IT HAS INCOME SUBJECT TO TAX AT THE CORPORATE LEVEL REPORTED ON FEDERAL FORM "
                     "1120S, EVEN IF LINE 11 IS ZERO OR A NEGATIVE AMOUNT. The amount of Arizona "
                     "income tax is the greater of $50 or 4.9% of line 11.'"),
     "exceptions": ("⚠⚠ A CONDITIONAL MINIMUM, NOT AN UNCONDITIONAL ONE. Both halves of the sentence "
                    "matter: an S corp WITH federal-level income pays at least $50 even on a zero or "
                    "negative Arizona figure; an S corp WITHOUT federal-level income pays NOTHING at "
                    "the corporate level. DO NOT PORT ANOTHER STATE'S FLAT MINIMUM-TAX LOGIC."),
     "notes": "az_120s_line12_tax() returns None rather than 0 when there is no federal-level income, "
              "so 'blank' and 'zero' stay distinguishable."},
    {"rule_id": "R-AZ120S-CREDITS", "title": "⚠ Credit ordering: nonrefundable credits STOP before the PTE tax",
     "rule_type": "calculation", "sort_order": 5,
     "inputs": ["az120s_l13_credit_recapture", "az120s_l15_nonrefundable_credits",
               "az120s_l20_refundable_credits"],
     "outputs": ["AZ120S_L14", "AZ120S_L17", "AZ120S_L19"],
     "formula": "L14 = L12 + L13; L17 = L14 − L15; L19 = L17 + L18 (the PTE tax from line 52)",
     "description": ("⚠ A REAL STRUCTURAL FACT. Nonrefundable credits are applied at line 15 against "
                     "line 14 — the corporate-level tax PLUS recapture — and the PTE tax is added "
                     "AFTERWARDS at line 18/19. THEY THEREFORE CANNOT REDUCE THE PTE TAX. Refundable "
                     "credits at line 20 sit in the PAYMENTS block and CAN."),
     "exceptions": ("⚠ PUB 713 IS SELF-CONTRADICTORY HERE (U4 / W7): it opens 'Can Arizona income tax "
                    "credits offset the PTE tax due? NO. The tax credits in Chapter 10 of Title 43 "
                    "apply to individuals ... They do not apply to the PTE tax.' and then says "
                    "'NOTHING PRECLUDES a partnership or an S Corporation from claiming a refundable "
                    "tax credit, or even a nonrefundable tax credit, against its PTE tax liability.' "
                    "THE FORM IS NOT AMBIGUOUS AND THE FORM GOVERNS. ⚠ Form 315 may be claimed at the "
                    "corporate level but NOT passed through to shareholders."),
     "notes": "⚠ FORM 165 HAS NO ENTITY-LEVEL CREDIT LINE AT ALL — neither recapture nor "
              "nonrefundable nor refundable. Another 165/120S asymmetry."},
    {"rule_id": "R-AZ120S-PART2-GATE", "title": "Part 2 gate: Q.A = Yes OR PTE estimates paid — NOT Q.A alone",
     "rule_type": "conditional", "sort_order": 6,
     "inputs": ["az120s_q_a_pte_election", "az120s_pte_estimates_paid"],
     "outputs": ["az120s_part2_required"],
     "formula": "part2_required = (question_A == Yes) OR (pte_estimated_payments_made > 0)",
     "description": ("The Part 2 header, verbatim: 'Complete only if the S Corporation answered "
                     "\"Yes\" to Question A on page 1, OR IF ESTIMATED PAYMENTS WERE MADE AND THE S "
                     "CORPORATION IS NOT CLAIMING THE PTE ELECTION. If estimated payments were made "
                     "and the S Corporation is not claiming the PTE election, SEE THE INSTRUCTIONS "
                     "BEFORE COMPLETING PART 2.'"),
     "exceptions": "⚠ TWO SCRIPTED VARIANTS exist on the 120S — 'not subject to Arizona income tax' "
                   "and 'subject to Arizona income tax' — and the second runs lines 19-26 differently.",
     "notes": "W18. Same gate as Form 165's."},
    {"rule_id": "R-AZ120S-PTE-BASE", "title": "⚠⚠ Line 37 = line 1. Nothing in between",
     "rule_type": "calculation", "sort_order": 7, "inputs": ["az120s_l1_total_distributive_income"],
     "outputs": ["AZ120S_L37"], "formula": "L37 = L1, UNADJUSTED",
     "description": ("A.R.S. § 43-1014(B)(1)(b): the S-corp PTE base is 'the total of all distributive "
                     "income passed through to the shareholders under section 43-1126, subsection B'. "
                     "Face line 1 is 'TOTAL DISTRIBUTIVE INCOME (LOSS) from federal Form 1120-S, "
                     "Schedule K' and face line 37 is 'Enter the amount from line 1'. Pub 713 "
                     "confirms in one sentence: 'For an S Corporation making the PTE election, ALL "
                     "ITS TOTAL FEDERAL DISTRIBUTABLE INCOME is included in the starting point for "
                     "calculating the PTE tax.' ⚠ CONTRAST FORM 165, whose base is line 5 (after a "
                     "full Schedule A/B stack) PLUS line 9 (sixteen separately-stated categories)."),
     "exceptions": "⚠ THERE IS NO § 43-1412 ANALOGUE FOR AN S CORPORATION and no § 179 routing "
                   "question — line 1 is already net of the federal § 179 deduction.",
     "notes": "This single equality is the cleanest statement of the 165/120S asymmetry."},
    {"rule_id": "R-AZ120S-SHARES", "title": "Lines 38/40/42/44 from Schedule C column (c), six decimals",
     "rule_type": "calculation", "sort_order": 8, "inputs": ["az120s_sched_c_rows"],
     "outputs": ["AZ120S_L38", "AZ120S_L40", "AZ120S_L42", "AZ120S_L44"],
     "formula": "L38 = C1 + C4; L40 = C2 + C5; L42 = C3; L44 = C7 — each a six-decimal ratio",
     "description": ("Structurally identical to Form 165's lines 11/13/15/17 off Schedule E. ⚠ Line "
                     "C7 carries a pointer Form 165's E7 does not: 'Also enter this percentage in "
                     "column (c) in Part 2, line 44.'"),
     "exceptions": ("⚠ LOOK-THROUGH SHAREHOLDERS that did not opt out go in C1-C3 — the INDIVIDUAL "
                    "rows. Both instruction books footnote the rule: a share owned by a grantor trust "
                    "disregarded federally, or by an SMLLC disregarded to an individual, MAY make the "
                    "PTE election."),
     "notes": "Eligible = individuals, estates, trusts; non-response to the 60-day opt-out notice "
              "means INCLUDED."},
    {"rule_id": "R-AZ120S-ALLOC", "title": "Lines 39/41/43/45 = line 37 × the ratio, and they must cross-foot",
     "rule_type": "calculation", "sort_order": 9,
     "inputs": ["az120s_l43a_part_year_resident_portion", "az120s_l43b_part_year_nonresident_portion"],
     "outputs": ["AZ120S_L39", "AZ120S_L41", "AZ120S_L43", "AZ120S_L45"],
     "formula": "L39 = L37×L38; L41 = L37×L40; L43 = L37×L42; L45 = L37×L44; and L39+L41+L43+L45 == L37",
     "description": ("Printed on the face: 'NOTE: The total of lines 39, 41, 43, and 45 must equal the "
                     "amount on line 37', and 'the total of lines 43A and 43B must equal the amount "
                     "reported on line 43'."),
     "exceptions": "43A/43B split by ACTUAL Arizona residency period, not by day count.",
     "notes": "Form 165's twin is lines 12/14/16/18 against line 10."},
    {"rule_id": "R-AZ120S-ZEROFLOOR", "title": "Lines 46 and 48 are floored at zero — PRINTED ON THE FACE",
     "rule_type": "validation", "sort_order": 10, "inputs": [], "outputs": ["AZ120S_L46", "AZ120S_L48"],
     "formula": "L46 = max(0, L39 + L43A); L48 = max(0, L41 + L43B)",
     "description": ("The face prints 'If less than zero, enter \"0\"' at BOTH lines. ⚠ FORM 165 LINES "
                     "19 AND 21 CARRY THE SAME RULE IN THE INSTRUCTIONS ONLY — same rule, printed in "
                     "one place and not the other (W4)."),
     "exceptions": "", "notes": "Consistent with Pub 713's note that a loss-year election is possible "
                                "but pointless."},
    {"rule_id": "R-AZ120S-RATE", "title": "The 2.5% PTE rate is PRE-PRINTED at lines 47 and 51",
     "rule_type": "calculation", "sort_order": 11, "inputs": [],
     "outputs": ["AZ120S_L47", "AZ120S_L51"],
     "formula": "L47 = L46 × 0.0250; L51 = L50 × 0.0250",
     "description": ("Both lines read 'the PTE tax rate, 2.5% (0.0250)'. With Form 165 lines 20 and 24 "
                     "that is FOUR face confirmations, plus Pub 713's 'For taxable year 2025, the PTE "
                     "tax rate is 2.5%.'"),
     "exceptions": ("⚠ The A.R.S. § 43-1011 pinpoint behind § 43-1014(A)'s by-reference rate cannot be "
                    "verified (U21): the 01011.01 URL 404s and 01011.htm serves a superseded version "
                    "topping at 4.50%. THE RATE IS SAFE; ONLY THE PROVENANCE CHANGED."),
     "notes": "Pin to the FACE, not to a statutory lookup."},
    {"rule_id": "R-AZ120S-APPORT", "title": "Line 49 = the apportionment ratio; the line-7 cross-check is CONDITIONAL",
     "rule_type": "calculation", "sort_order": 12,
     "inputs": ["az120s_q_b_conducts_business_within_and_without", "az120s_q_c_apportionment_method"],
     "outputs": ["AZ120S_L7", "AZ120S_L49"],
     "formula": ("L49 = L7 IF L7 is populated; ELSE Schedule A line A5 (STANDARD) / A3f (SALES FACTOR "
                 "ONLY) / Schedule ACA line 3 (AIR CARRIER) directly"),
     "description": ("⚠ THE INSTRUCTION'S CROSS-CHECK IS MISPRINTED: 'NOTE: The apportionment ratio "
                     "entered on LINE 45 must be the same as the apportionment ratio entered on line "
                     "7.' LINE 45 IS AN INCOME AMOUNT, NOT A RATIO — the intended check is line 49 == "
                     "line 7, and THE FACE IS CORRECT (AZ-D2 / W8). ⚠ SECOND-ORDER CONSEQUENCE: line 7 "
                     "is only reached when the S corp has federal-level taxable income (lines 2-12), "
                     "so A MULTISTATE ELECTING S CORP WITH NO BUILT-IN GAINS AND NO EXCESS NET PASSIVE "
                     "INCOME NEVER COMPUTES LINE 7 YET STILL NEEDS LINE 49. THE EQUALITY CANNOT BE "
                     "HARD."),
     "exceptions": ("⚠ '0.000000' = no Arizona nexus; BLANK or '1.000000' = income sourced ENTIRELY "
                    "within Arizona. A null-vs-zero bug silently zeroes every nonresident "
                    "shareholder's Arizona income. ⚠ Question B is INVERTED relative to Form 165's "
                    "question D."),
     "notes": "Schedule ACA's own routing list omits Part 2 line 49; the parent form closes the loop "
              "(U12)."},
    {"rule_id": "R-AZ120S-DIVISOR", "title": "Schedule A: the same dynamic 4/3/2/none divisor as Form 165's Schedule C",
     "rule_type": "calculation", "sort_order": 13, "inputs": [],
     "outputs": ["AZ120S_A4", "AZ120S_A5"],
     "formula": ("exclude a factor IFF numerator == 0 AND denominator == 0; divisor = 4 | 3 (property "
                 "or payroll) | 2 (SALES) | none (two excluded)"),
     "description": ("Schedule A rows A1-A5 are STRUCTURALLY IDENTICAL to Form 165 Schedule C rows "
                     "C1-C5, with one wording change ('per federal Form 1120S') and different "
                     "destination pointers. ⚠ THIS IS THE ONE PLACE THE TWO ARIZONA RETURNS GENUINELY "
                     "SHARE AN ENGINE — and it is NOT a modification engine."),
     "exceptions": ("Property at ORIGINAL COST; rented property at 8× the NET annual rental rate (less "
                    "subrentals). Property factor cap 1.0; sales factor cap 2.0 STANDARD / 1.0 SALES "
                    "FACTOR ONLY. Six decimals, rounding the sixth up at a seventh digit of five or "
                    "more. Computer software: AZDOR ruling CTR 01-2."),
     "notes": "Alternative apportionment relief under § 43-1148 needs a letter 60 days before filing — "
              "RED-DEFERRED."},
    {"rule_id": "R-AZ120S-MSP", "title": "Schedule MSP on the 120S: same five-year lock, different destination",
     "rule_type": "conditional", "sort_order": 14,
     "inputs": ["az120s_q_d_msp_included", "az120s_q_d_msp_cycle_year", "az120s_scha_msp_service_sales"],
     "outputs": ["AZ120S_A3B"],
     "formula": "Part B lands on Schedule A line A3b column A (Form 165's lands on Schedule C line C3b)",
     "description": ("A.R.S. § 43-1147(B)/(C): qualification at A3 = A1/A2 > 0.850000, computed ONLY "
                     "IN YEAR ONE; IRREVOCABLE and binding for FIVE CONSECUTIVE TAXABLE YEARS "
                     "regardless of whether the threshold is still met."),
     "exceptions": ("⚠ THE MSP ELECTION REQUIRES A TIMELY FILED ORIGINAL RETURN WHILE THE PTE ELECTION "
                    "DOES NOT — two elections on the same return with OPPOSITE timeliness rules (W21)."),
     "notes": "Question D carries the Yr 1 - Yr 5 cycle marker."},
    {"rule_id": "R-AZ120S-TAX", "title": "Line 52 = line 47 + line 51 → carried to line 18",
     "rule_type": "calculation", "sort_order": 15, "inputs": [], "outputs": ["AZ120S_L52", "AZ120S_L18"],
     "formula": "L50 = L48 × L49; L51 = L50 × 0.0250; L52 = L47 + L51; L18 = L52",
     "description": ("Resident and part-year-resident-period income is taxed WITHOUT apportionment; "
                     "nonresident and part-year-nonresident-period income is APPORTIONED FIRST. The "
                     "result crosses back into Part 1 at line 18 and joins line 17 to make line 19."),
     "exceptions": ("⚠ Because the PTE tax enters at line 18, AFTER nonrefundable credits have been "
                    "applied at line 15 against line 14, THOSE CREDITS CANNOT REDUCE IT."),
     "notes": "Form 165's twin is line 25, which stands alone with no credit interaction at all."},
    {"rule_id": "R-AZ120S-PAYMENTS", "title": "Payments block: lines 24, 26, 27, 28, 29",
     "rule_type": "calculation", "sort_order": 16,
     "inputs": ["az120s_l21_extension_payment", "az120s_l22_estimated_payments",
               "az120s_l23_amended_payments", "az120s_l25_prior_overpayments",
               "az120s_schd_scorp_estimates", "az120s_schd_pte_estimates"],
     "outputs": ["AZ120S_L24", "AZ120S_L26", "AZ120S_L27", "AZ120S_L28", "AZ120S_L29"],
     "formula": ("L22 = D7(c) + D7(d); L24 = L20+L21+L22+L23; L26 = L24 − L25; L27 = L26; "
                 "L28 = max(0, L19 − L27); L29 = max(0, L27 − L19)"),
     "description": ("⚠ LINE 22 MERGES TWO SCHEDULE D COLUMNS: 'Enter the total of line D7, column (c), "
                     "and line D7, column (d) from Schedule D' — the S-corp estimates AND the PTE "
                     "estimates. Schedule D HAS FOUR PAYMENT COLUMNS because an S corporation can owe "
                     "BOTH a corporate-level tax and a PTE tax in the same year. FORM 165'S SCHEDULE F "
                     "HAS THREE, because a partnership cannot."),
     "exceptions": "Line 27 simply carries line 26 forward from page 1 to page 2.",
     "notes": "EFT mandatory at $500; 5% penalty under § 42-1125(O), including on estimated payments."},
    {"rule_id": "R-AZ120S-DUE-REFUND", "title": "Lines 33/34/36 — total due, overpayment, refund",
     "rule_type": "calculation", "sort_order": 17,
     "inputs": ["az120s_l30_penalty_and_interest", "az120s_l31_estimated_underpayment_penalty",
               "az120s_l32_information_return_penalty", "az120s_l35_overpayment_applied_2026"],
     "outputs": ["AZ120S_L33", "AZ120S_L34", "AZ120S_L36"],
     "formula": "L33 = L28 + L30 + L31 + L32; L34 = L29 − (L30+L31+L32); L36 = L34 − L35",
     "description": ("Line 35 correctly reads 'to be applied to 2026 estimated tax' — ⚠ UNLIKE FORM "
                     "165 LINE 39, which prints a stale 2025 (AZ-D1 / W5). The 120S is the form that "
                     "gets this right."),
     "exceptions": "", "notes": "Overpayments may be applied to the next year's PTE estimates for "
                                "TY2023+; any unapplied balance is refunded."},
    {"rule_id": "R-AZ120S-INFO-PEN", "title": "Line 32: the information-return penalty, non-electing S corps only",
     "rule_type": "conditional", "sort_order": 18,
     "inputs": ["az120s_q_a_pte_election", "az120s_l32_information_return_penalty"],
     "outputs": ["AZ120S_L32"],
     "formula": "if question A == Yes: L32 == 0; else L32 = min(100 × months_late, 500)",
     "description": ("Verbatim: 'S Corporations that did not make the PTE election, this is an "
                     "information return. If it is incomplete or it is filed late (including "
                     "extension) it is subject to a penalty of $100 per month or fraction of a month "
                     "during which the failure continues, up to a maximum of $500. ... S Corporations "
                     "that made the PTE election, this is not an information return. DO NOT ENTER AN "
                     "AMOUNT ON LINE 32.'"),
     "exceptions": "", "notes": "Form 165 carries the same rule at lines 7 and 36."},
    {"rule_id": "R-AZ120S-PENALTY", "title": "The Arizona penalty set on the S-corp side, and the 25% combined cap",
     "rule_type": "calculation", "sort_order": 19, "inputs": [], "outputs": ["AZ120S_L30"],
     "formula": ("late filing 4.5%/month capped 25%; extension underpayment 0.5% per 30-day period "
                 "capped 25%; late payment 0.5%/month capped 10%; EFT failure 5%; COMBINED CAP 25%"),
     "description": ("Identical to Form 165's set. The extension underpayment penalty triggers when "
                     "less than 90% of the tax liability was paid by the ORIGINAL due date, and is "
                     "MUTUALLY EXCLUSIVE with the late payment penalty."),
     "exceptions": ("No estimated-tax penalty when the Arizona liability due on the return is under "
                    "$1,000 (§ 43-581(E)(2)); no overpayment penalty at all; voluntary-amendment "
                    "relief from the late payment penalty per CTR 09-1 unless under audit or filing on "
                    "the department's demand."),
     "notes": "⚠ Do not conflate this 4.5% late-filing penalty with Form 165PA line 13's stale 4.5% "
              "TAX rate."},
    {"rule_id": "R-AZ120S-EST-PAY", "title": "$150,000 estimated-payment test on the S-corp side",
     "rule_type": "conditional", "sort_order": 20, "inputs": ["az120s_prior_year_taxable_income"],
     "outputs": ["az120s_estimated_payments_required"],
     "formula": "required = prior_year_taxable_income > 150000  (⚠ STRICTLY GREATER)",
     "description": ("A.R.S. § 43-581(C) applies to 'an entity that is treated as a partnership OR S "
                     "CORPORATION for federal income tax purposes'. The Form 120S instructions repeat "
                     "'S Corporations whose taxable income for the previous year EXCEEDS $150,000 must "
                     "make payments of estimated tax.' EXACTLY $150,000 IS OUT."),
     "exceptions": ("⚠ THE FORM 120S BOOK CONTRADICTS ITSELF ON THE MEASUREMENT BASE, using bare "
                    "'taxable income' in one place and 'PTE INCOME' in another. Campaign D-12 A1 ruled "
                    "the statute's bare 'taxable income' and REFINED it the same session to the figure "
                    "A.R.S. § 43-1401(2) defines — ARIZONA TAXABLE INCOME — which on this return "
                    "resolves to PRIOR-YEAR LINE 1. ⚠⚠ THAT LAST STEP IS AN ENGINEERING INFERENCE: "
                    "§ 43-1401 is a chapter-14 PARTNERSHIP definitions section with NO S-corp "
                    "analogue, and Delvio reaches line 1 by BUILDING TO THE FORM (Form 120S has no "
                    "Arizona modification apparatus, so there is nothing to adjust). See "
                    "D_AZ120S_EST_BASIS_NO_ANALOGUE. U19 stays open as a fact. ⚠ The FOURTH "
                    "installment is the 15th day of the 1ST MONTH AFTER the close of the taxable year "
                    "(W17). ⚠ Form 220/PTE Part C line 17 substitutes months by form type: 'Forms "
                    "120S: Use 3rd month instead of 4th month. PTE's: Use 3rd month instead of 4th "
                    "month.'"),
     "notes": "Form 220/PTE Part A reason 4 is a 120S-only alternative computation for S corporations "
              "subject to federal-level tax (90% of built-in-gains/capital-gains tax plus 100% of the "
              "prior year's excess-net-passive-income tax)."},
    {"rule_id": "R-AZ120S-SCHC-XFOOT", "title": "Schedule C must cross-foot: C8 column (c) should TOTAL 1.000000",
     "rule_type": "validation", "sort_order": 21, "inputs": ["az120s_sched_c_rows"],
     "outputs": ["AZ120S_C8"],
     "formula": "C6 = C1+C2+C3+C4+C5; C8 = C6 + C7; C8 column (c) == 1.000000",
     "description": ("Printed on the face: '(Column (c) should total 1.000000)'. ⚠ Form 165's E8 says "
                     "'should EQUAL 1.000000' — a cosmetic wording difference, the same rule."),
     "exceptions": "Gate: 'S Corporations making the PTE election, complete Schedule C. All others, "
                   "skip to Schedule E.'",
     "notes": "With the Part 2 cross-foot this gives two independent proof obligations."},
    {"rule_id": "R-AZ120S-SCHB", "title": "Schedule B column (h) = line 1 × column (g) — NO special allocations",
     "rule_type": "calculation", "sort_order": 22, "inputs": ["az120s_shareholder_rows"],
     "outputs": ["AZ120S_SCHB_H"],
     "formula": "col(h) = L1 × col(g) per shareholder; sum(col(g)) == 1.000000",
     "description": ("⚠ COLUMN (h) POINTS AT **LINE 1** (federal, unadjusted) where Form 165's "
                     "Schedule D column (h) points at LINE 5 (Arizona-adjusted). Same column position, "
                     "different source line — the asymmetry showing up a second time. ⚠ SPECIAL "
                     "ALLOCATIONS ARE FORBIDDEN: 'An S Corporation may not allocate its income and "
                     "loss items to its shareholders using a special allocation.'"),
     "exceptions": ("⚠ NO IRA-CUSTODIAN RULE — S corporations generally cannot have IRA shareholders. "
                    "DO NOT PORT FORM 165'S. ⚠ The residency-code parenthetical differs: 'O' is "
                    "'other entity (i.e. C corporation, S Corporation, etc.)' here and '(i.e. "
                    "corporation, partnership, etc.)' on Form 165."),
     "notes": "The header carries a SINGLE ownership percentage, with no beginning/end split and no "
              "profit/loss/capital breakdown — because S corporations cannot special-allocate."},
    {"rule_id": "R-AZ120S-K1-SPLIT", "title": "120S K-1 routing, and the K-1(NR) line map that is OFF BY ONE",
     "rule_type": "routing", "sort_order": 23, "inputs": ["az120s_shareholder_rows"],
     "outputs": ["az120s_k1_documents"],
     "formula": "resident / part-year → 120S Schedule K-1; nonresident → 120S Schedule K-1(NR); a "
                "PART-YEAR shareholder receives BOTH",
     "description": ("Pub 713 footnote 2: 'For part-year shareholders, complete one Schedule K-1 (as "
                     "needed) to report that shareholder's distribution for the time the shareholder "
                     "lived in Arizona AND complete Schedule K-1(NR) to report that shareholder's "
                     "distribution for the time the shareholder did NOT live in Arizona.' ⚠ THE 120S "
                     "SCHEDULE K-1(NR) HAS NO GUARANTEED-PAYMENTS LINE, so EVERY LINE FROM 10 ONWARD "
                     "IS OFFSET BY ONE relative to the 165 Schedule K-1(NR). A SHARED LINE MAP WILL BE "
                     "OFF BY ONE."),
     "exceptions": ("⚠⚠ NEITHER 120S OWNER SCHEDULE CARRIES AN ARIZONA INCOME ADJUSTMENT. The resident "
                    "K-1 goes straight from the header block to 'Part 1 Net Capital Gain (Loss) From "
                    "Investment in a Qualified Small Business'; the K-1(NR) has no analogue to the "
                    "165 K-1(NR)'s line 15. §5.3 seen from the owner side. ⚠ The information-schedule "
                    "INVENTORIES also differ: the 120S resident K-1 has NO virtual-currency/NFT part "
                    "and NO gas-fees part but DOES have a marijuana Schedule DFE part; the 165 "
                    "resident K-1 is the mirror image. DO NOT BUILD ONE SHARED K-1 MODEL."),
     "notes": "'the the' is printed on the 120S Schedule K-1 face at question B. Transcribe as printed."},
    {"rule_id": "R-AZ120S-K1NR-COL", "title": "120S K-1(NR) column (c) = column (a) × column (b)",
     "rule_type": "calculation", "sort_order": 24, "inputs": [], "outputs": ["az120s_k1nr_col_c"],
     "formula": "col(c) = col(a) × col(b) on every Part 1 line",
     "description": ("Part 1 is the partnership K-1(NR)'s Part 1 MINUS guaranteed payments, "
                     "renumbered: 1-3 ordinary/rental, 4 total → Form 140NR line 21, 5 interest → line "
                     "16, 6 dividends → line 17, 7 royalties → line 21, 8 short-term gain → line 20, "
                     "9 long-term gain → line 20, 10 IRC 1231 → line 20, 11 other income → line 22, "
                     "12 IRC 179 → line 21, 13 other deductions → (no destination)."),
     "exceptions": ("⚠ Part 4's net-LTCG schedule sources from 'page 1, line 9, column (a) AND/OR line "
                    "10, column (a)' — the S-corp equivalent of the 165's line 9 + line 11. ⚠ Line 11 "
                    "reads 'Other income (loss)' with NO 'include schedule', where the 165 version "
                    "says 'Other income (loss): include schedule'."),
     "notes": "⚠ Part 5 and Part 6 ON THE SAME SCHEDULE route to DIFFERENT PAGES of Form 140NR — page "
              "6 line L vs page 5 line L. BIND ON THE ITEM LETTER, NOT THE PAGE NUMBER (U8)."},
    {"rule_id": "R-AZ120S-K1-CREDIT", "title": "120S K-1 PTE credit → Form 355 Part 1 LINE 2 (not line 1)",
     "rule_type": "routing", "sort_order": 25, "inputs": [], "outputs": ["az120s_k1_pte_credit"],
     "formula": ("Schedule K-1 Part 5 line 8 / Schedule K-1(NR) Part 6 line 21 = the shareholder's "
                 "pro-rata share of line 52, allocated from the LIABILITY; lines 9-12 / 22-25 = the "
                 "four add-backs"),
     "description": ("A.R.S. § 43-1077: nonrefundable, FIVE-YEAR carryforward. ⚠ THE FORM 355 LINE "
                     "DIFFERS BY ENTITY TYPE: partnership K-1s route to Part 1 LINE 1; S-corp K-1s "
                     "route to Part 1 LINE 2. Estates and trusts instead go to Form 141AZ line 19. "
                     "⚠ FOUR ADD-BACK LINES split on two axes (Arizona vs other-state × prior-year vs "
                     "current-year), because the add-back is keyed to tax PAID during the calendar "
                     "year."),
     "exceptions": ("⚠ THE STATUTE KEYS THE CREDIT TO TAX PAID while line 52 computes tax OWED, and no "
                    "schedule reconciles them before the K-1s are cut (U9 / W19). Default to the "
                    "liability, per Pub 713's own worked example, and diagnose when payments fall "
                    "short. ⚠ Part 5's gate reaches 'this year OR FOR A PRIOR YEAR', so an S corp that "
                    "did NOT elect this year may still have to issue the prior-year add-back lines."),
     "notes": AZ_FORM_355_COLLISION_NOTE},
    {"rule_id": "R-AZ120S-DFE", "title": "Marijuana disallowed federal expenses reach the SHAREHOLDER here, not the entity",
     "rule_type": "routing", "sort_order": 26, "inputs": ["az120s_q_g_marijuana_licence"],
     "outputs": ["az120s_k1_dfe_share"],
     "formula": ("Schedule K-1 Part 4: line 6 = Schedule DFE line 16; line 7 = line 6 × the "
                 "shareholder's ownership percentage"),
     "description": ("Routes four ways: Form 140 page 6 line Q (non-SBI resident); Form 140PY page 6 "
                     "line V (non-SBI part-year); Form 140-SBI line 47 (SBI resident); Form 140PY-SBI "
                     "line 44 (SBI part-year). The K-1(NR) twin is Part 5 lines 19-20, routing to Form "
                     "140NR page 6 line L / 140PY page 6 line V / 140NR-SBI line 44 / 140PY-SBI line "
                     "44."),
     "exceptions": ("⚠⚠ THE SAME SCHEDULE DFE INPUT IS PLUMBED DIFFERENTLY ON THE TWO RETURNS: on the "
                    "PARTNERSHIP side it is an ENTITY-LEVEL subtraction at Form 165 page-6 line B5-G; "
                    "on the S-CORP side it goes to the SHAREHOLDER via the K-1. ⚠ THE K-1(NR) LINE 20 "
                    "LABEL IS WRONG — it says 'the shareholder's portion of the CREDIT' when it is a "
                    "share of disallowed EXPENSES; the resident K-1's line 7 says it correctly "
                    "(AZ-D5 / W14)."),
     "notes": "One of the 18 SBI-bearing K-1 routing lines."},
    {"rule_id": "R-AZ120S-QSUB", "title": "QSubs are folded into a SINGLE parent Form 120S",
     "rule_type": "classification", "sort_order": 27, "inputs": [], "outputs": ["az120s_filing_entity"],
     "formula": "a QSub is not a separate Arizona filer",
     "description": ("Verbatim: 'Qualified subchapter S subsidiaries are not treated as entities "
                     "separate from the parent corporation and would be included on a SINGLE Arizona "
                     "Form 120S filed by the parent S Corporation.' Entity classification otherwise "
                     "follows the federal check-the-box result (PTR 97-1 / CTR 97-1); an LLC with a "
                     "valid federal S election files Form 120S."),
     "exceptions": ("⚠ FORM 120S HAS NO DE-MINIMIS CARVE-OUT. The Form 165 book says twice that a "
                    "partnership with no Arizona income, deductions or credits need not file; THE "
                    "S-CORP BOOK SAYS NO SUCH THING. DO NOT PORT IT. ⚠ A single-member LLC disregarded "
                    "federally is OUT of both returns as a FILER but CAN be a PTE-participating OWNER "
                    "— two roles, opposite answers."),
     "notes": "Forms 51 and 122 (combined/consolidated affiliation and subsidiary consent) are FORM "
              "120 ONLY and have no PTE application."},
    {"rule_id": "R-AZ120S-ELECTION", "title": "The PTE election on the S-corp side: annual, revocable, no timeliness",
     "rule_type": "conditional", "sort_order": 28, "inputs": ["az120s_q_a_pte_election"],
     "outputs": ["az120s_election_state"],
     "formula": "election = filing with question A = Yes; revocation = an amended return with A = No; "
                "four-year SOL both ways",
     "description": ("A.R.S. § 43-1014(A) as amended by Laws 2025 Ch. 182 Sec. 6, retroactive to "
                     "TY2022 (Sec. 9(A)). ⚠ CONTRAST § 43-1126(C), which DOES make the federal S "
                     "election effective 'for all succeeding taxable years' — the drafters knew how to "
                     "write a carry-forward election and did not do so for the PTE election."),
     "exceptions": ("⚠ THE STALE-LAW TRAP IS ON THE S-CORP SIDE SPECIFICALLY: Booklet 120/165ES, "
                    "posted under AZDOR's 2025 row but /ModDate 2024-11-19 and headed '2024 CORPORATE "
                    "INCOME TAX HIGHLIGHTS', still says 'This election must be made by THE S "
                    "CORPORATION no later than the due date or extended due date of its return.' THAT "
                    "SENTENCE IS REPEALED LAW. Use the booklet for VOUCHERS ONLY."),
     "notes": "Both the election and its revocation are N-OWNER-RETURN EVENTS."},
    {"rule_id": "R-AZ120S-ZERORETURN", "title": "The '$0 return' refund script — TWO variants on the 120S",
     "rule_type": "conditional", "sort_order": 29, "inputs": ["az120s_pte_estimates_paid"],
     "outputs": ["az120s_zero_return"],
     "formula": ("question A = No AND pte_estimates_paid > 0 → line 37 = 0; lines 46-48 and 50-52 = 0; "
                 "line 18 = 0; line 19 = 0; line 21 = extension payments; line 22 = estimated "
                 "payments; line 23 = 0; line 24 = lines 20-23, also entered on lines 26, 27, 29, 34 "
                 "and 36; line 36 is refundable to the S corporation"),
     "description": ("A LINE-BY-LINE FILING RECIPE printed in the instruction book, not advisory "
                     "prose. Pub 713 frames the scenario explicitly around the federal SALT deduction "
                     "rising from $10,000 to $40,000 in 2025."),
     "exceptions": ("⚠ THE REFUND 'CANNOT BE APPLIED TO THE S CORPORATION'S 2026 TAXABLE YEAR PTE "
                    "ESTIMATED TAX LIABILITY. IT CANNOT BE APPLIED TO AN INDIVIDUAL SHAREHOLDER'S TAX "
                    "LIABILITY.' ⚠ TWO VARIANTS EXIST — 'not subject to Arizona income tax' and "
                    "'subject to Arizona income tax' — and the second runs lines 19-26 differently."),
     "notes": "The most likely real-world Arizona PTE filing for TY2025."},
    {"rule_id": "R-AZ120S-COMPOSITE", "title": "Composite Form 140NR on the S-corp side: ten shareholders, all opted out",
     "rule_type": "validation", "sort_order": 30, "inputs": ["az120s_q_f_composite_return"],
     "outputs": ["az120s_composite_valid"],
     "formula": "composite_allowed = all participants opted out AND participant_count >= 10",
     "description": ("The Form 120S book states the participant minimum inline: '...including having a "
                     "minimum of 10 nonresident shareholders included in the composite return.' Pub "
                     "713: shareholders who did NOT opt out must file their own Arizona returns to "
                     "claim the PTE credit."),
     "exceptions": "Composite extension = Form 204; composite estimates = Form 140ES; payments cannot "
                   "be converted between the composite and PTE pots.",
     "notes": "The composite return itself is an individual-module artifact and is RED-DEFERRED."},
    {"rule_id": "R-AZ120S-EFILE", "title": "E-file is mandatory — and the S-corp K-1 paper path has NO optical-media option",
     "rule_type": "validation", "sort_order": 31, "inputs": [], "outputs": ["az120s_efile_required"],
     "formula": "efile_required unless one of the seven printed exemptions applies",
     "description": ("A.R.S. § 43-323(F), and printed on the face: 'This form must be e-filed unless "
                     "the S Corporation has a waiver or is exempt from e-filing.' Four of the seven "
                     "exemptions key off FEDERAL status — a Gate-2 ingest dependency."),
     "exceptions": ("⚠⚠ 'S CORPORATIONS FILING A PAPER RETURN MUST SUBMIT SCHEDULE(S) K-1 AND K-1(NR) "
                    "TO THE DEPARTMENT BY PAPER.' NO CD/DVD/FLASH-DRIVE ALTERNATIVE IS OFFERED ON THE "
                    "S-CORP SIDE, unlike the partnership side. DO NOT PORT THE OPTICAL-MEDIA PATH. "
                    "⚠ A 2026 SHORT-PERIOD RETURN ON THE 2025 FORM MUST BE PAPER-FILED."),
     "notes": "246 MB / ~66,054 K-1 ceiling; waivers on Form 292 (unpulled, U15); rejections to "
              "azefile@azdor.gov."},
]

AZ120S_RULE_LINKS: list[tuple] = [
    ("R-AZ120S-NO-MODS", "AZ_2025_FORM_120S", "primary",
     "the face has no additions/subtractions schedule and no 'Arizona basis' line"),
    ("R-AZ120S-NO-MODS", "AZ_2025_FORM_120S_INSTR", "primary",
     "43-1021/43-1022/43-1121/43-1122 cited ZERO times in 28 pages"),
    ("R-AZ120S-NO-MODS", "AZ_ARS_43_1014", "primary",
     "§ 43-1014(B)(1)(b) takes raw federal distributive income via § 43-1126(B), a REPORTING provision"),
    ("R-AZ120S-NO-MODS", "AZ_ARS_43_1122", "secondary",
     "the corporate decoupling rule that Form 120S nevertheless does NOT implement at entity level"),
    ("R-AZ120S-L1", "AZ_2025_FORM_120S", "primary", "line 1 as printed on the face"),
    ("R-AZ120S-L1", "AZ_2025_FORM_120S_INSTR", "implementation", "the 'net total of the pro rata share items' definition"),
    ("R-AZ120S-CORP-TAX", "AZ_2025_FORM_120S", "primary", "lines 2-11 as printed"),
    ("R-AZ120S-CORP-TAX", "AZ_2025_FORM_120S_INSTR", "implementation", "the federal 1120-S worksheet pointer"),
    ("R-AZ120S-L12-MIN", "AZ_2025_FORM_120S_INSTR", "primary", "'only if it has income subject to tax at the corporate level'"),
    ("R-AZ120S-CREDITS", "AZ_2025_FORM_120S", "primary", "the line 14/15/17/18/19/20 ordering as printed"),
    ("R-AZ120S-CREDITS", "AZ_2025_PUB_713", "secondary", "⚠ says both 'No' and 'nothing precludes' (U4)"),
    ("R-AZ120S-PART2-GATE", "AZ_2025_FORM_120S", "primary", "the Part 2 header, verbatim"),
    ("R-AZ120S-PART2-GATE", "AZ_2025_FORM_120S_INSTR", "implementation", "the two scripted '$0 return' variants"),
    ("R-AZ120S-PTE-BASE", "AZ_ARS_43_1014", "primary", "§ 43-1014(B)(1)(b), the S-corp base"),
    ("R-AZ120S-PTE-BASE", "AZ_2025_FORM_120S", "primary", "line 37 = 'Enter the amount from line 1'"),
    ("R-AZ120S-PTE-BASE", "AZ_2025_PUB_713", "secondary", "'all its total federal distributable income'"),
    ("R-AZ120S-SHARES", "AZ_2025_FORM_120S", "primary", "Schedule C rows C1-C7 and Part 2 lines 38/40/42/44"),
    ("R-AZ120S-SHARES", "AZ_ARS_43_1014", "primary", "§ 43-1014(C)-(D), eligibility and the opt-out"),
    ("R-AZ120S-ALLOC", "AZ_2025_FORM_120S", "primary", "lines 39/41/43/45 and the face-printed cross-foot"),
    ("R-AZ120S-ZEROFLOOR", "AZ_2025_FORM_120S", "primary", "'If less than zero, enter \"0\"' printed at 46 and 48"),
    ("R-AZ120S-ZEROFLOOR", "AZ_2025_FORM_165_INSTR", "secondary", "the same rule, instructions-only on Form 165"),
    ("R-AZ120S-RATE", "AZ_2025_FORM_120S", "primary", "2.5% (0.0250) pre-printed at lines 47 and 51"),
    ("R-AZ120S-RATE", "AZ_ARS_43_1014", "primary", "§ 43-1014(A) sets the rate by reference"),
    ("R-AZ120S-APPORT", "AZ_2025_FORM_120S", "primary", "line 49 on the face is the ratio line"),
    ("R-AZ120S-APPORT", "AZ_2025_FORM_120S_INSTR", "implementation", "⚠ its cross-check misprints line 49 as line 45"),
    ("R-AZ120S-DIVISOR", "AZ_2025_FORM_120S", "primary", "Schedule A rows A1-A5"),
    ("R-AZ120S-DIVISOR", "AZ_2025_FORM_165_INSTR", "secondary", "the factor-exclusion rule, stated in the 165 book"),
    ("R-AZ120S-MSP", "AZ_ARS_43_1147_MSP", "primary", "§ 43-1147(C), the five-year lock"),
    ("R-AZ120S-MSP", "AZ_2025_SCH_MSP_ACA", "primary", "Part B → Schedule A line A3b column A"),
    ("R-AZ120S-TAX", "AZ_2025_FORM_120S", "primary", "lines 46-52 and the carry to line 18"),
    ("R-AZ120S-PAYMENTS", "AZ_2025_FORM_120S", "primary", "lines 20-29 and Schedule D's FOUR columns"),
    ("R-AZ120S-PAYMENTS", "AZ_2025_120_165EXT_V", "implementation", "the extension payment and the voucher"),
    ("R-AZ120S-DUE-REFUND", "AZ_2025_FORM_120S", "primary", "lines 30-36 as printed, including the CORRECT 2026 at line 35"),
    ("R-AZ120S-INFO-PEN", "AZ_2025_FORM_120S_INSTR", "primary", "'Do not enter an amount on line 32'"),
    ("R-AZ120S-INFO-PEN", "AZ_2025_PUB_713", "secondary", "AZDOR answered 'No' directly"),
    ("R-AZ120S-PENALTY", "AZ_2025_FORM_120S_INSTR", "primary", "the penalty table and the 25% combined cap"),
    ("R-AZ120S-PENALTY", "AZ_ARS_43_581", "primary", "§ 43-581(E)(2), the $1,000 floor"),
    ("R-AZ120S-EST-PAY", "AZ_ARS_43_581", "primary", "§ 43-581(C) reaches S corporations expressly"),
    ("R-AZ120S-EST-PAY", "AZ_2025_120_PTE_W", "implementation", "⚠ its line 9 carries TWO rates in one label"),
    ("R-AZ120S-EST-PAY", "AZ_2025_220_PTE", "secondary", "Part A reason 4 is the 120S-only alternative computation"),
    ("R-AZ120S-SCHC-XFOOT", "AZ_2025_FORM_120S", "primary", "C8 column (c) should total 1.000000, on the face"),
    ("R-AZ120S-SCHB", "AZ_2025_FORM_120S", "primary", "Schedule B columns (a)-(h); column (h) points at line 1"),
    ("R-AZ120S-SCHB", "AZ_2025_PUB_713", "primary", "'An S Corporation may not allocate ... using a special allocation'"),
    ("R-AZ120S-K1-SPLIT", "AZ_2025_120S_SCHK1_SET", "primary", "both owner schedules and their part inventories"),
    ("R-AZ120S-K1-SPLIT", "AZ_2025_PUB_713", "secondary", "footnote 2 — a part-year owner gets BOTH schedules"),
    ("R-AZ120S-K1NR-COL", "AZ_2025_120S_SCHK1_SET", "primary", "Part 1 columns (a)/(b)/(c) and the destinations"),
    ("R-AZ120S-K1-CREDIT", "AZ_ARS_43_1077", "primary", "the credit, keyed to tax PAID"),
    ("R-AZ120S-K1-CREDIT", "AZ_2025_120S_SCHK1_SET", "implementation", "Part 5 lines 8-12 / Part 6 lines 21-25"),
    ("R-AZ120S-DFE", "AZ_2025_120S_SCHK1_SET", "primary", "Part 4 lines 6-7 and the four-way routing"),
    ("R-AZ120S-QSUB", "AZ_2025_FORM_120S_INSTR", "primary", "the QSub rule and the absence of a de-minimis carve-out"),
    ("R-AZ120S-ELECTION", "AZ_SB1274_2025_CH182", "primary", "Sec. 6 struck timeliness; Sec. 9(A) made it retroactive"),
    ("R-AZ120S-ELECTION", "AZ_ARS_43_1014", "primary", "§ 43-1014(A) — the election IS the filing"),
    ("R-AZ120S-ZERORETURN", "AZ_2025_FORM_120S_INSTR", "primary", "the line-by-line script, both variants"),
    ("R-AZ120S-ZERORETURN", "AZ_2025_PUB_713", "secondary", "the SALT-cap framing AZDOR supplies"),
    ("R-AZ120S-COMPOSITE", "AZ_2025_FORM_120S_INSTR", "primary", "the ten-shareholder minimum, stated inline"),
    ("R-AZ120S-EFILE", "AZ_ARS_43_323_EFILE", "primary", "§ 43-323(F)-(G)"),
    ("R-AZ120S-EFILE", "AZ_2025_FORM_120S_INSTR", "implementation", "'must submit ... by paper' — no optical media"),
    ("R-AZ120S-EFILE", "AZ_DOR_MEF_LOI_TY2025", "secondary", "the S-corporation module is a SEPARATE LOI registration"),
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM AZ_120S — LINES
# ⚠ NOTE WHAT IS ABSENT: there is no A1/B1 analogue, no additions or
# subtractions schedule, no page-6 modification block, and no 'Arizona basis'
# line. The absence is the finding, not an omission by this loader.
# ═══════════════════════════════════════════════════════════════════════════
AZ120S_LINES: list[dict] = [
    {"line_number": "1", "line_type": "input", "sort_order": 1,
     "description": "TOTAL DISTRIBUTIVE INCOME (LOSS) from federal Form 1120-S, Schedule K",
     "source_facts": ["az120s_l1_total_distributive_income"],
     "source_rules": ["R-AZ120S-L1", "R-AZ120S-NO-MODS"],
     "destination_form": "AZ_120S line 37 (the PTE base) and AZ_120S Schedule B column (h)",
     "notes": ("⚠⚠ ONE AGGREGATE FEDERAL FIGURE, AND ARIZONA APPLIES NO MODIFICATIONS TO IT. Contrast "
               "Form 165, where line 1 is only the STARTING point for a full Schedule A/B stack.")},
    {"line_number": "2", "line_type": "input", "sort_order": 2,
     "description": "Excess net passive income",
     "source_facts": ["az120s_l2_excess_net_passive_income"], "source_rules": ["R-AZ120S-CORP-TAX"],
     "notes": "Federal figure, from the federal Form 1120-S worksheet."},
    {"line_number": "3", "line_type": "input", "sort_order": 3,
     "description": "Capital gains/built-in gains",
     "source_facts": ["az120s_l3_capital_and_built_in_gains"], "source_rules": ["R-AZ120S-CORP-TAX"]},
    {"line_number": "4", "line_type": "subtotal", "sort_order": 4,
     "description": "Total federal income subject to corporate income tax: Add lines 2 and 3",
     "calculation": "2 + 3", "source_rules": ["R-AZ120S-CORP-TAX"],
     "notes": "⚠ STRAIGHT FROM FEDERAL. Nothing is added or subtracted anywhere in this chain."},
    {"line_number": "4a", "line_type": "input", "sort_order": 5,
     "description": "100% AZ S Corporations check box. Go to line 11",
     "source_facts": ["az120s_l4a_100pct_arizona"], "source_rules": ["R-AZ120S-CORP-TAX"]},
    {"line_number": "5", "line_type": "input", "sort_order": 6,
     "description": "Nonapportionable or allocable income: Include schedule. Multistate only",
     "source_facts": ["az120s_l5_nonapportionable_income"], "source_rules": ["R-AZ120S-CORP-TAX"],
     "notes": "⚠ A SCHEDULE IS REQUIRED AND THE FORM PROVIDES NONE — a free-form attachment."},
    {"line_number": "6", "line_type": "subtotal", "sort_order": 7,
     "description": "Apportionable income: Subtract line 5 from line 4. Multistate only. Enter the difference",
     "calculation": "4 − 5", "source_rules": ["R-AZ120S-CORP-TAX"]},
    {"line_number": "7", "line_type": "calculated", "sort_order": 8,
     "description": "Arizona apportionment ratio from Schedule A or Schedule ACA",
     "calculation": "Schedule A line A5 (STANDARD) / A3f (SALES FACTOR ONLY) / Schedule ACA line 3",
     "source_rules": ["R-AZ120S-APPORT", "R-AZ120S-DIVISOR"],
     "notes": ("⚠ '0.000000' = NO ARIZONA NEXUS; BLANK or '1.000000' = sourced entirely within "
               "Arizona. ⚠ THIS LINE IS ONLY REACHED WHEN THE S CORP HAS FEDERAL-LEVEL TAXABLE "
               "INCOME, which is why the line 49 cross-check cannot be a hard equality.")},
    {"line_number": "8", "line_type": "calculated", "sort_order": 9,
     "description": "Income apportioned to Arizona: Line 6 multiplied by line 7. Multistate only",
     "calculation": "6 × 7", "source_rules": ["R-AZ120S-CORP-TAX"]},
    {"line_number": "9", "line_type": "input", "sort_order": 10,
     "description": "Other income allocated to Arizona: Include schedule. Multistate only",
     "source_facts": ["az120s_l9_other_income_allocated_to_az"], "source_rules": ["R-AZ120S-CORP-TAX"]},
    {"line_number": "10", "line_type": "subtotal", "sort_order": 11,
     "description": "Total income attributable to Arizona: Add lines 8 and 9", "calculation": "8 + 9",
     "source_rules": ["R-AZ120S-CORP-TAX"]},
    {"line_number": "11", "line_type": "calculated", "sort_order": 12,
     "description": ("Net income subject to Arizona corporate income tax: 100% Arizona S Corporations "
                     "enter line 4; Multistate S Corporations enter line 10"),
     "calculation": "4 if 100% Arizona else 10", "source_rules": ["R-AZ120S-CORP-TAX"]},
    {"line_number": "12", "line_type": "calculated", "sort_order": 13,
     "description": "Enter tax: See instructions before completing this line",
     "calculation": "max(50, 0.049 × line 11) IF federal-level taxable income exists; else BLANK",
     "source_rules": ["R-AZ120S-L12-MIN"],
     "notes": ("⚠⚠ A CONDITIONAL MINIMUM. 'The S Corporation is subject to the tax computed on line 12 "
               "ONLY IF it has income subject to tax at the corporate level reported on federal Form "
               "1120S, EVEN IF LINE 11 IS ZERO OR A NEGATIVE AMOUNT.' Do not port an unconditional "
               "state minimum tax.")},
    {"line_number": "13", "line_type": "input", "sort_order": 14,
     "description": "Tax from recapture of tax credits from Arizona Form 300, Part 2, line 22",
     "source_facts": ["az120s_l13_credit_recapture"], "source_rules": ["R-AZ120S-CREDITS"],
     "notes": "⚠ FORM 165 HAS NO RECAPTURE LINE. An S corp with only a recapture liability completes "
              "lines 13-36."},
    {"line_number": "14", "line_type": "subtotal", "sort_order": 15,
     "description": "Subtotal: Add lines 12 and 13. Enter the total", "calculation": "12 + 13",
     "source_rules": ["R-AZ120S-CREDITS"]},
    {"line_number": "15", "line_type": "input", "sort_order": 16,
     "description": "Nonrefundable tax credits from Arizona Form 300, Part 2, line 40",
     "source_facts": ["az120s_l15_nonrefundable_credits"], "source_rules": ["R-AZ120S-CREDITS"],
     "notes": "⚠⚠ APPLIED AGAINST LINE 14 ONLY. The PTE tax arrives afterwards at line 18, so "
              "NONREFUNDABLE CREDITS CANNOT REDUCE IT (U4 / W7)."},
    {"line_number": "16", "line_type": "informational", "sort_order": 17,
     "description": "Enter form number for each nonrefundable credit claimed (fields 161-164)",
     "source_facts": ["az120s_l16_credit_form_numbers"], "source_rules": ["R-AZ120S-CREDITS"],
     "notes": "⚠ Form 315 may be claimed at the corporate level but NOT passed through to shareholders."},
    {"line_number": "17", "line_type": "subtotal", "sort_order": 18,
     "description": "Tax liability: Subtract line 15 from line 14. Enter the difference",
     "calculation": "14 − 15", "source_rules": ["R-AZ120S-CREDITS"],
     "notes": "⚠ NONREFUNDABLE CREDITS STOP HERE."},
    {"line_number": "18", "line_type": "calculated", "sort_order": 19,
     "description": "PTE Tax Liability: Enter the amount from Part 2, line 52", "calculation": "= line 52",
     "source_rules": ["R-AZ120S-TAX"]},
    {"line_number": "19", "line_type": "total", "sort_order": 20,
     "description": ("Total Tax Liability: Add line 17 and 18. Enter the total. This is the total "
                     "amount of tax owed by the S Corporation"),
     "calculation": "17 + 18", "source_rules": ["R-AZ120S-CREDITS", "R-AZ120S-TAX"],
     "destination_form": "AZ_220_PTE Part B line 5 ('Form 120S, line 19 less line 20')"},
    {"line_number": "20", "line_type": "input", "sort_order": 21,
     "description": "Refundable tax credits: Check box(es) 201 (308) / 202 (334) / 203 (349); enter amount",
     "source_facts": ["az120s_l20_refundable_credits"], "source_rules": ["R-AZ120S-CREDITS"],
     "notes": "⚠ REFUNDABLE CREDITS SIT IN THE PAYMENTS BLOCK AND THEREFORE **CAN** REDUCE WHAT IS "
              "OWED ON THE PTE TAX, unlike the nonrefundable credits at line 15."},
    {"line_number": "21", "line_type": "input", "sort_order": 22,
     "description": "Extension payment made with Form 120/165EXT or online: See instructions",
     "source_facts": ["az120s_l21_extension_payment"], "source_rules": ["R-AZ120S-PAYMENTS"]},
    {"line_number": "22", "line_type": "calculated", "sort_order": 23,
     "description": "Estimated tax payments: See instructions",
     "calculation": "= Schedule D line D7 column (c) + line D7 column (d)",
     "source_facts": ["az120s_l22_estimated_payments"], "source_rules": ["R-AZ120S-PAYMENTS"],
     "notes": "⚠ TWO COLUMNS MERGE HERE — S-corp estimates AND PTE estimates. Form 165's Schedule F "
              "has only one estimated column."},
    {"line_number": "23", "line_type": "input", "sort_order": 24,
     "description": ("Amended Returns: Payments made with original return plus all payments made after "
                     "it was filed"),
     "source_facts": ["az120s_l23_amended_payments"], "source_rules": ["R-AZ120S-PAYMENTS"]},
    {"line_number": "24", "line_type": "subtotal", "sort_order": 25,
     "description": "Subtotal of tax payments: Add lines 20 through 23. Enter the total",
     "calculation": "20 + 21 + 22 + 23", "source_rules": ["R-AZ120S-PAYMENTS"]},
    {"line_number": "25", "line_type": "input", "sort_order": 26,
     "description": "Overpayments of tax from original return or later adjustments",
     "source_facts": ["az120s_l25_prior_overpayments"], "source_rules": ["R-AZ120S-PAYMENTS"],
     "notes": ("⚠ FORM 220/PTE'S FACE LINE 37 WRONGLY DIRECTS THE ESTIMATED-PENALTY FIGURE HERE. This "
               "is an OVERPAYMENT line; the penalty line is 31 (U20 / W25). Build from the Form 120S "
               "instructions, not from the 220/PTE face.")},
    {"line_number": "26", "line_type": "subtotal", "sort_order": 27,
     "description": "Total tax payments. Subtract line 25 from line 24", "calculation": "24 − 25",
     "source_rules": ["R-AZ120S-PAYMENTS"]},
    {"line_number": "27", "line_type": "subtotal", "sort_order": 28,
     "description": "Total tax payments from line 26 [page 2]", "calculation": "= line 26",
     "source_rules": ["R-AZ120S-PAYMENTS"]},
    {"line_number": "28", "line_type": "calculated", "sort_order": 29,
     "description": ("Balance of tax due: If line 19 is larger than line 27, subtract line 27 from line "
                     "19. Enter the difference. Skip line 29"),
     "calculation": "max(0, 19 − 27)", "source_rules": ["R-AZ120S-PAYMENTS"]},
    {"line_number": "29", "line_type": "calculated", "sort_order": 30,
     "description": "Overpayment of tax: If line 27 is larger than line 19, subtract line 19 from line 27",
     "calculation": "max(0, 27 − 19)", "source_rules": ["R-AZ120S-PAYMENTS"]},
    {"line_number": "30", "line_type": "input", "sort_order": 31,
     "description": "Penalty and interest",
     "source_facts": ["az120s_l30_penalty_and_interest"], "source_rules": ["R-AZ120S-PENALTY"]},
    {"line_number": "31", "line_type": "input", "sort_order": 32,
     "description": "Estimated tax underpayment penalty. If Form 220/PTE is included, check box 31A",
     "source_facts": ["az120s_l31_estimated_underpayment_penalty"],
     "source_rules": ["R-AZ120S-EST-PAY", "R-AZ120S-PENALTY"],
     "notes": ("Imports Form 220/PTE Part C line 37. ⚠ THE 220/PTE FACE ROUTES IT TO LINE 25 INSTEAD — "
               "an overpayment line. BUILD FROM THE 120S INSTRUCTIONS (U20 / W25). ⚠ On an amended "
               "return, DO NOT RECOMPUTE.")},
    {"line_number": "32", "line_type": "input", "sort_order": 33,
     "description": "Information return penalty: See instructions",
     "source_facts": ["az120s_l32_information_return_penalty"], "source_rules": ["R-AZ120S-INFO-PEN"],
     "notes": "⚠ NON-ELECTING S CORPORATIONS ONLY. $100/month or fraction, capped at $500."},
    {"line_number": "33", "line_type": "total", "sort_order": 34,
     "description": "TOTAL DUE: See instructions", "calculation": "28 + 30 + 31 + 32",
     "source_rules": ["R-AZ120S-DUE-REFUND"]},
    {"line_number": "34", "line_type": "total", "sort_order": 35,
     "description": "OVERPAYMENT: See instructions", "calculation": "29 − (30 + 31 + 32)",
     "source_rules": ["R-AZ120S-DUE-REFUND"]},
    {"line_number": "35", "line_type": "input", "sort_order": 36,
     "description": "Amount of line 34 to be applied to 2026 estimated tax",
     "source_facts": ["az120s_l35_overpayment_applied_2026"], "source_rules": ["R-AZ120S-DUE-REFUND"],
     "notes": "⚠ CORRECTLY PRINTS 2026 — Form 165 line 39 prints a stale 2025 for the same concept "
              "(AZ-D1 / W5). This form is the control that proves the 165 face is wrong."},
    {"line_number": "36", "line_type": "total", "sort_order": 37,
     "description": "Amount to be refunded: Subtract line 35 from line 34", "calculation": "34 − 35",
     "source_rules": ["R-AZ120S-DUE-REFUND"]},

    # ---- Part 2 -------------------------------------------------------------
    {"line_number": "37", "line_type": "calculated", "sort_order": 40,
     "description": "Enter the amount from line 1", "calculation": "= line 1, UNADJUSTED",
     "source_rules": ["R-AZ120S-PTE-BASE", "R-AZ120S-NO-MODS", "R-AZ120S-PART2-GATE"],
     "notes": ("⚠⚠ THE SINGLE CLEANEST STATEMENT OF THE 165/120S ASYMMETRY. Form 165's PTE base is "
               "line 5 (after a full Schedule A/B stack) PLUS line 9 (sixteen separately-stated "
               "categories). This one is line 1, full stop. A.R.S. § 43-1014(B)(1)(b).")},
    {"line_number": "38", "line_type": "calculated", "sort_order": 41,
     "description": ("Add lines C1 and C4 in column (c) of Schedule C — resident individual and "
                     "resident estate/trust shareholders that did not opt out"),
     "calculation": "C1(c) + C4(c), six decimals", "source_rules": ["R-AZ120S-SHARES"]},
    {"line_number": "39", "line_type": "calculated", "sort_order": 42,
     "description": "Multiply line 37 by line 38. Enter the result", "calculation": "37 × 38",
     "source_rules": ["R-AZ120S-ALLOC"]},
    {"line_number": "40", "line_type": "calculated", "sort_order": 43,
     "description": "Add lines C2 and C5 in column (c) of Schedule C — nonresident shareholders",
     "calculation": "C2(c) + C5(c), six decimals", "source_rules": ["R-AZ120S-SHARES"]},
    {"line_number": "41", "line_type": "calculated", "sort_order": 44,
     "description": "Multiply line 37 by line 40. Enter the result", "calculation": "37 × 40",
     "source_rules": ["R-AZ120S-ALLOC"]},
    {"line_number": "42", "line_type": "calculated", "sort_order": 45,
     "description": "Enter the ownership share from line C3, column (c) — part-year residents",
     "calculation": "C3(c), six decimals", "source_rules": ["R-AZ120S-SHARES"]},
    {"line_number": "43", "line_type": "calculated", "sort_order": 46,
     "description": "Multiply line 37 by line 42. Enter the result", "calculation": "37 × 42",
     "source_rules": ["R-AZ120S-ALLOC"]},
    {"line_number": "43A", "line_type": "input", "sort_order": 47,
     "description": "Enter the portion of line 43 that all part-year residents earned while residents of Arizona",
     "source_facts": ["az120s_l43a_part_year_resident_portion"], "source_rules": ["R-AZ120S-ALLOC"],
     "notes": "43A + 43B must equal line 43 — printed on the face."},
    {"line_number": "43B", "line_type": "input", "sort_order": 48,
     "description": ("Enter the portion of line 43 that all part-year residents earned while "
                     "nonresidents of Arizona"),
     "source_facts": ["az120s_l43b_part_year_nonresident_portion"], "source_rules": ["R-AZ120S-ALLOC"]},
    {"line_number": "44", "line_type": "calculated", "sort_order": 49,
     "description": ("Enter the ownership share from line C7, column (c) — shareholders that opted out "
                     "and shareholders that are not eligible to make the election"),
     "calculation": "C7(c), six decimals", "source_rules": ["R-AZ120S-SHARES"],
     "notes": "⚠ Line C7 itself instructs 'Also enter this percentage in column (c) in Part 2, line "
              "44' — a pointer Form 165's E7 does not carry."},
    {"line_number": "45", "line_type": "calculated", "sort_order": 50,
     "description": "Multiply line 37 by line 44. Enter the result", "calculation": "37 × 44",
     "source_rules": ["R-AZ120S-ALLOC"],
     "notes": ("⚠ FACE-PRINTED CROSS-FOOT: 'The total of lines 39, 41, 43, and 45 must equal the "
               "amount on line 37.' ⚠ AND THIS IS THE LINE THE LINE-49 INSTRUCTION WRONGLY NAMES AS "
               "AN APPORTIONMENT RATIO — it is an INCOME AMOUNT (AZ-D2 / W8).")},
    {"line_number": "46", "line_type": "calculated", "sort_order": 51,
     "description": "Add line 39 and line 43A. Enter the total. If less than zero, enter \"0\"",
     "calculation": "max(0, 39 + 43A)", "source_rules": ["R-AZ120S-ZEROFLOOR"],
     "notes": "⚠ THE FLOOR IS PRINTED ON THIS FACE. Form 165's equivalent (line 19) carries it only in "
              "the instructions (W4)."},
    {"line_number": "47", "line_type": "calculated", "sort_order": 52,
     "description": ("Multiply the amount on line 46 by the PTE tax rate, 2.5% (0.0250) Enter the "
                     "result"),
     "calculation": "46 × 0.0250", "source_rules": ["R-AZ120S-RATE"]},
    {"line_number": "48", "line_type": "calculated", "sort_order": 53,
     "description": "Add line 41 and line 43B. Enter the total. If less than zero, enter \"0\"",
     "calculation": "max(0, 41 + 43B)", "source_rules": ["R-AZ120S-ZEROFLOOR"]},
    {"line_number": "49", "line_type": "calculated", "sort_order": 54,
     "description": "Enter the Arizona apportionment ratio from Schedule A or Schedule ACA",
     "calculation": "= line 7 IF line 7 is populated; ELSE Schedule A line A5 / A3f or Schedule ACA line 3",
     "source_rules": ["R-AZ120S-APPORT"],
     "notes": ("⚠ THE INSTRUCTION'S CROSS-CHECK MISPRINTS THIS AS 'LINE 45', WHICH IS AN INCOME "
               "AMOUNT. The face is correct. ⚠ AND THE CHECK CANNOT BE A HARD EQUALITY: a multistate "
               "electing S corp with no built-in gains and no excess net passive income never computes "
               "line 7 yet still needs this line (AZ-D2 / W8).")},
    {"line_number": "50", "line_type": "calculated", "sort_order": 55,
     "description": "Multiply the amount on line 48 by line 49. Enter the result", "calculation": "48 × 49",
     "source_rules": ["R-AZ120S-TAX"]},
    {"line_number": "51", "line_type": "calculated", "sort_order": 56,
     "description": ("Multiply the amount on line 50 by the PTE tax rate, 2.5% (0.0250). Enter the "
                     "result"),
     "calculation": "50 × 0.0250", "source_rules": ["R-AZ120S-RATE"]},
    {"line_number": "52", "line_type": "total", "sort_order": 57,
     "description": ("Add line 47 and line 51. Enter the total here and on line 18. This is the PTE Tax "
                     "owed by the S Corporation"),
     "calculation": "47 + 51", "source_rules": ["R-AZ120S-TAX"],
     "destination_form": "AZ_120S line 18",
     "notes": "⚠ Because it lands at line 18 — AFTER nonrefundable credits were applied at line 15 — "
              "those credits cannot reduce it."},

    # ---- Schedules ----------------------------------------------------------
    {"line_number": "A1c", "line_type": "calculated", "sort_order": 60,
     "description": "Schedule A A1c: Total owned and rented property (section a plus section b)",
     "calculation": "(inventories + depreciable + land + other − nonbusiness) + (net annual rent × 8)",
     "source_facts": ["az120s_scha_property_inventories", "az120s_scha_property_depreciable",
                      "az120s_scha_property_land", "az120s_scha_property_other",
                      "az120s_scha_property_nonbusiness", "az120s_scha_rented_property_net_rent"],
     "source_rules": ["R-AZ120S-DIVISOR"],
     "notes": "⚠ ORIGINAL COST for owned property; EIGHT TIMES the NET annual rental rate for rented "
              "property, net of subrentals. Cap 1.0. STANDARD apportionment only."},
    {"line_number": "A2", "line_type": "input", "sort_order": 61,
     "description": ("Schedule A A2: Payroll Factor — total wages, salaries, commissions and other "
                     "compensation to employees (per federal Form 1120S, or payroll reports)"),
     "source_facts": ["az120s_scha_payroll"], "source_rules": ["R-AZ120S-DIVISOR"],
     "notes": "⚠ 'per federal Form 1120S' — the ONLY wording difference between this schedule and Form "
              "165's Schedule C."},
    {"line_number": "A3d", "line_type": "subtotal", "sort_order": 62,
     "description": "Schedule A A3d: Total sales and other gross receipts (lines a through c)",
     "calculation": "A3a + A3b + A3c",
     "source_facts": ["az120s_scha_sales_to_az_purchasers", "az120s_scha_msp_service_sales",
                      "az120s_scha_other_gross_receipts"],
     "source_rules": ["R-AZ120S-DIVISOR", "R-AZ120S-MSP"]},
    {"line_number": "A3f", "line_type": "calculated", "sort_order": 63,
     "description": "Schedule A A3f: Sales Factor Only ratio. Skip A4 and A5",
     "calculation": "(A3d × weight) ÷ A3d, six decimals", "source_rules": ["R-AZ120S-APPORT"],
     "destination_form": "AZ_120S page 1 line 7; and Part 2 line 49 if the PTE election is made"},
    {"line_number": "A4", "line_type": "subtotal", "sort_order": 64,
     "description": "Schedule A A4: STANDARD Apportionment Total Ratio — add Column C of A1c, A2 and A3f",
     "calculation": "A1c(C) + A2(C) + A3f(C)", "source_rules": ["R-AZ120S-DIVISOR"]},
    {"line_number": "A5", "line_type": "total", "sort_order": 65,
     "description": ("Schedule A A5: Average Apportionment Ratio for STANDARD Apportionment — divide "
                     "line A4, Column C, by four (4)"),
     "calculation": "A4 ÷ divisor, where divisor = 4 | 3 | 2 | none",
     "source_rules": ["R-AZ120S-DIVISOR", "R-AZ120S-APPORT"],
     "destination_form": "AZ_120S page 1 line 7; and Part 2 line 49 if the PTE election is made",
     "notes": "⚠ THE PRINTED '(4)' IS THE DEFAULT, NOT THE RULE — see the factor-exclusion rule."},
    {"line_number": "B-h", "line_type": "calculated", "sort_order": 70,
     "description": "Schedule B column (h): Distributive Share of Income, Page 1, Line 1, per shareholder",
     "calculation": "line 1 × column (g)", "source_facts": ["az120s_shareholder_rows"],
     "source_rules": ["R-AZ120S-SCHB"],
     "notes": ("⚠ POINTS AT **LINE 1** (federal, unadjusted). Form 165's Schedule D column (h) points "
               "at LINE 5 (Arizona-adjusted) — the same column position, a different source line. "
               "⚠ SPECIAL ALLOCATIONS ARE FORBIDDEN HERE. ⚠ NO IRA-CUSTODIAN RULE.")},
    {"line_number": "C6", "line_type": "subtotal", "sort_order": 71,
     "description": ("Schedule C C6: Add lines C1 to C5 — the totals for shareholders who did not opt "
                     "out of the election"),
     "calculation": "C1 + C2 + C3 + C4 + C5, in columns (b) and (c)",
     "source_facts": ["az120s_sched_c_rows"], "source_rules": ["R-AZ120S-SCHC-XFOOT", "R-AZ120S-SHARES"],
     "notes": "⚠ Look-through shareholders that did not opt out are counted in C1-C3, THE INDIVIDUAL "
              "ROWS."},
    {"line_number": "C7", "line_type": "input", "sort_order": 72,
     "description": ("Schedule C C7: Shareholders that opted out of the election or are excluded from "
                     "making the election"),
     "source_facts": ["az120s_sched_c_rows"], "source_rules": ["R-AZ120S-SHARES"],
     "destination_form": "AZ_120S Part 2 line 44",
     "notes": "⚠ Carries an explicit pointer Form 165's E7 does not: 'Also enter this percentage in "
              "column (c) in Part 2, line 44.'"},
    {"line_number": "C8", "line_type": "total", "sort_order": 73,
     "description": ("Schedule C C8: Total shareholder count and total shareholder ownership share. Add "
                     "lines C6 and C7 in columns (b) and (c). (Column (c) should total 1.000000)"),
     "calculation": "C6 + C7; column (c) must equal 1.000000", "source_rules": ["R-AZ120S-SCHC-XFOOT"],
     "notes": "⚠ 'should TOTAL 1.000000' here; Form 165's E8 says 'should EQUAL 1.000000'. Cosmetic "
              "wording difference, same rule."},
    {"line_number": "D7b", "line_type": "subtotal", "sort_order": 74,
     "description": "Schedule D line D7 column (b): Total extension payments",
     "source_facts": ["az120s_schd_extension_payments"], "source_rules": ["R-AZ120S-PAYMENTS"]},
    {"line_number": "D7c", "line_type": "subtotal", "sort_order": 75,
     "description": "Schedule D line D7 column (c): Total S Corp estimated payments",
     "source_facts": ["az120s_schd_scorp_estimates"], "source_rules": ["R-AZ120S-PAYMENTS"],
     "destination_form": "AZ_120S line 22 (with column (d))"},
    {"line_number": "D7d", "line_type": "subtotal", "sort_order": 76,
     "description": "Schedule D line D7 column (d): Total PTE estimated payments",
     "source_facts": ["az120s_schd_pte_estimates"], "source_rules": ["R-AZ120S-PAYMENTS"],
     "destination_form": "AZ_120S line 22 (with column (c))",
     "notes": "⚠ THE FOURTH COLUMN THAT FORM 165'S SCHEDULE F DOES NOT HAVE — an S corporation can owe "
              "both a corporate-level tax and a PTE tax in the same year."},
    {"line_number": "E5", "line_type": "input", "sort_order": 77,
     "description": "Schedule E5: Indicate tax accounting method (Cash / Accrual / Other)",
     "source_facts": ["az120s_sche_accounting_method"], "source_rules": ["R-AZ120S-PTE-BASE"],
     "notes": ("⚠ MATERIAL TO THE § 43-1021(15) CIRCULARITY: a cash-basis electing entity deducts the "
               "PTE tax federally in the year PAID, so line 1 — and therefore line 37 — is ALREADY NET "
               "of it, and Arizona provides no entity-level add-back line (D-12 A3). No Form 165 "
               "counterpart field.")},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM AZ_120S — DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════════════════
AZ120S_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_AZ120S_NO_MODIFICATIONS", "severity": "error",
     "title": "⚠⚠ Form 120S has NO Arizona modification apparatus — do not add one 'for symmetry'",
     "condition": "any federal-to-Arizona modification is attempted on Form 120S",
     "message": ("Arizona Form 120S carries NO additions schedule, NO subtractions schedule, NO "
                 "depreciation line and NO 'Arizona basis' line. Line 37 = line 1, unadjusted "
                 "(A.R.S. 43-1014(B)(1)(b)). THIS IS A VERIFIED NEGATIVE, NOT AN UNIMPLEMENTED "
                 "FEATURE: the four Arizona modification statutes 43-1021 / 43-1022 / 43-1121 / "
                 "43-1122 are cited ZERO times in the entire 28-page TY2025 instruction book, the "
                 "string 'Arizona basis' occurs ZERO times, every Title 43 section the book does cite "
                 "is an APPORTIONMENT provision, and the corporate-level chain (lines 2-4, 11, 12) is "
                 "unadjusted too. The S-corp shareholder's Arizona depreciation adjustment happens on "
                 "the SHAREHOLDER'S OWN individual return under 43-1021(11) / 43-1022(17)(e)."),
     "notes": ("⚠ AN ALARM WAS RAISED OVER 28 'addition' AND 42 'subtract*' HITS IN THIS BOOK AND ALL "
               "70 WERE READ IN CONTEXT: 23 x 'additional', 2 x 'In addition:', 12 x line arithmetic, "
               "3 x 'has no Arizona additions to, or subtractions from, federal taxable income' (ALL "
               "THREE inside the Rounding Dollar Amounts worked examples lifted from the Form 120 "
               "C-corp book, each saying the company HAS NONE), and ~18 x the OWNER-LEVEL net-LTCG "
               "subtraction in the K-1 instruction section at the BACK. THE ALARM WAS A FALSE "
               "POSITIVE. Campaign D-12 Group B: NO SHARED ARIZONA MODIFICATION ENGINE. Had this gone "
               "the other way it would have wrongly stripped every Arizona S-corp return of its state "
               "adjustments.")},
    {"diagnostic_id": "D_AZ120S_L37_EQUALS_L1", "severity": "info",
     "title": "Form 120S line 37 = line 1, with nothing in between",
     "condition": "the PTE base is computed on Form 120S",
     "message": ("The S-corporation PTE base is federal Form 1120-S Schedule K total distributive "
                 "income, full stop. Pub 713: 'For an S Corporation making the PTE election, ALL ITS "
                 "TOTAL FEDERAL DISTRIBUTABLE INCOME is included in the starting point for calculating "
                 "the PTE tax.' Contrast Form 165, whose base is line 5 (after Schedules A and B) PLUS "
                 "line 9 (sixteen separately-stated categories)."),
     "notes": "The cleanest single statement of the Arizona 165/120S asymmetry."},
    {"diagnostic_id": "D_AZ120S_L12_CONDITIONAL_MIN", "severity": "error",
     "title": "Line 12's $50 minimum applies ONLY when federal-level taxable income exists",
     "condition": "line 12 is computed",
     "message": ("'The S Corporation is subject to the tax computed on line 12 ONLY IF IT HAS INCOME "
                 "SUBJECT TO TAX AT THE CORPORATE LEVEL REPORTED ON FEDERAL FORM 1120S, EVEN IF LINE "
                 "11 IS ZERO OR A NEGATIVE AMOUNT. The amount of Arizona income tax is the greater of "
                 "$50 or 4.9% of line 11.' Both halves matter: WITH federal-level income the $50 floor "
                 "applies even on a zero or negative Arizona figure; WITHOUT it, nothing is owed at "
                 "the corporate level. DO NOT PORT AN UNCONDITIONAL STATE MINIMUM TAX."),
     "notes": "az_120s_line12_tax() returns None rather than 0 when there is no federal-level income, "
              "so 'blank' and 'zero' stay distinguishable on the printed form."},
    {"diagnostic_id": "D_AZ120S_U4_CREDIT_ORDERING", "severity": "warning",
     "title": "Nonrefundable credits cannot offset the Arizona PTE tax (Pub 713 says both things)",
     "condition": "a nonrefundable credit is claimed on line 15 while a PTE tax is computed at line 52",
     "message": ("The Form 120S face applies nonrefundable credits at LINE 15 AGAINST LINE 14 (the "
                 "corporate-level tax plus recapture) and adds the PTE tax AFTERWARDS at line 18/19. "
                 "NONREFUNDABLE CREDITS THEREFORE CANNOT REDUCE THE PTE TAX. Refundable credits at "
                 "line 20 sit in the payments block and CAN. Delvio builds to the form."),
     "notes": ("[UNVERIFIED] U4 / W7. Pub 713 is self-contradictory: it opens 'Can Arizona income tax "
               "credits offset the PTE tax due? No. The tax credits in Chapter 10 of Title 43 apply to "
               "individuals ... They do not apply to the PTE tax.' and then says 'NOTHING PRECLUDES a "
               "partnership or an S Corporation from claiming a refundable tax credit, OR EVEN A "
               "NONREFUNDABLE TAX CREDIT, against its PTE tax liability', adding that doing so also "
               "reduces the credit passed through. THE FORM IS NOT AMBIGUOUS AND THE FORM GOVERNS. The "
               "client-advice consequence — whether a preparer may route a nonrefundable credit "
               "against PTE tax — is a separate question the form answers 'no' to. ⚠ FORM 165 HAS NO "
               "ENTITY-LEVEL CREDIT LINE AT ALL.")},
    {"diagnostic_id": "D_AZ120S_L49_L7_CROSSCHECK", "severity": "warning",
     "title": "Line 49 must equal line 7 — but ONLY when line 7 was computed",
     "condition": "line 49 is populated and line 7 is populated and they differ",
     "message": ("The Form 120S instruction reads 'NOTE: The apportionment ratio entered on LINE 45 "
                 "must be the same as the apportionment ratio entered on line 7.' LINE 45 IS AN INCOME "
                 "AMOUNT, NOT A RATIO — the intended check is LINE 49 == LINE 7, and the face is "
                 "correct. ⚠ THE EQUALITY CANNOT BE HARD: line 7 is only reached when the S "
                 "corporation has federal-level taxable income (lines 2-12), so a multistate electing "
                 "S corp with no built-in gains and no excess net passive income NEVER COMPUTES LINE 7 "
                 "yet still needs line 49 from Schedule A line A5 / A3f or Schedule ACA line 3."),
     "notes": "Printed defect AZ-D2 / W8, independently re-confirmed by the verification pass."},
    {"diagnostic_id": "D_AZ120S_NO_SPECIAL_ALLOCATION", "severity": "error",
     "title": "An S corporation may NOT special-allocate — Schedule B is by OWNERSHIP share",
     "condition": "Schedule B column (g) does not follow stock ownership",
     "message": ("Pub 713: 'An S Corporation may not allocate its income and loss items to its "
                 "shareholders using a special allocation.' The Schedule K-1 header carries a SINGLE "
                 "ownership percentage with no beginning/end split and no profit/loss/capital "
                 "breakdown, precisely because there is nothing to special-allocate. ⚠ FORM 165 IS THE "
                 "OPPOSITE: 'If the partnership operating agreement specifies partnership proceeds are "
                 "to be distributed on the basis of a special allocation, complete columns (g) and (h) "
                 "using that allocation method', and Pub 713 carries a worked partnership example."),
     "notes": "This asymmetry must be encoded, not smoothed over."},
    {"diagnostic_id": "D_AZ120S_SCHB_H_LINE1", "severity": "warning",
     "title": "Schedule B column (h) draws from LINE 1, not from an adjusted figure",
     "condition": "Schedule B column (h) is computed",
     "message": ("Form 120S Schedule B column (h) reads 'Distributive Share of Income Page 1, Line 1'. "
                 "Form 165's Schedule D column (h) — the same column position — reads 'Page 1, Line "
                 "5', the Arizona-ADJUSTED figure. Using line 5 logic here would apply a Schedule A/B "
                 "stack that does not exist on this form."),
     "notes": "The 165/120S asymmetry surfacing a second time, in the owner grid."},
    {"diagnostic_id": "D_AZ120S_K1NR_OFFSET_BY_ONE", "severity": "error",
     "title": "⚠ The 120S Schedule K-1(NR) line map is OFFSET BY ONE from the 165 K-1(NR)'s",
     "condition": "a shared K-1(NR) line map is applied across the partnership and S-corp schedules",
     "message": ("The Form 120S Schedule K-1(NR) Part 1 is the Form 165 Schedule K-1(NR) Part 1 MINUS "
                 "the 'Guaranteed payments to partner' line — correct, since S corporations have none "
                 "— so EVERY LINE FROM 10 ONWARD IS OFFSET BY ONE. On the 120S: 10 = IRC 1231 gain, "
                 "11 = other income, 12 = IRC 179 expense, 13 = other deductions. On the 165: 10 = "
                 "guaranteed payments, 11 = IRC 1231, 12 = other income, 13 = IRC 179, 14 = other "
                 "deductions. A SHARED LINE MAP WILL SILENTLY MIS-POST EVERY ITEM FROM 10 ON."),
     "notes": ("Also: 120S line 11 reads 'Other income (loss)' with NO 'include schedule', where the "
               "165 version says 'Other income (loss): include schedule'. And the 120S K-1(NR) Part 4 "
               "net-LTCG schedule sources from 'page 1, line 9, column (a) AND/OR line 10, column "
               "(a)', the S-corp equivalent of the 165's line 9 + line 11.")},
    {"diagnostic_id": "D_AZ120S_K1NR_L20_MISLABEL", "severity": "warning",
     "title": "120S Schedule K-1(NR) Part 5 line 20 is MISLABELLED as a credit",
     "condition": "Schedule K-1(NR) Part 5 line 20 is printed",
     "message": ("Verbatim: 'Multiply the amount on line 19 by the shareholder's ownership percentage "
                 "shown on page 1. Enter the result. THIS IS THE SHAREHOLDER'S PORTION OF THE CREDIT.' "
                 "IT IS NOT A CREDIT — it is the shareholder's share of DISALLOWED FEDERAL EXPENSES "
                 "(marijuana Schedule DFE). The resident 120S Schedule K-1's parallel line 7 says so "
                 "correctly: 'This is the shareholder's portion of the Disallowed Federal Expenses.' "
                 "Transcribe as printed and flag."),
     "notes": "Printed defect AZ-D5 / W14."},
    {"diagnostic_id": "D_AZ120S_NO_DEMINIMIS", "severity": "info",
     "title": "Form 120S has NO de-minimis filing carve-out — do not port Form 165's",
     "condition": "an S corporation with no Arizona income, deductions or credits is considering not filing",
     "message": ("The Form 165 book states TWICE that 'A partnership that has no Arizona income, "
                 "deductions or credits for the taxable year is not required to file a partnership "
                 "return for that year.' THE FORM 120S BOOK CONTAINS NO SUCH CARVE-OUT. Corporations "
                 "taxed as S corporations 'must file Arizona Form 120S.'"),
     "notes": "⚠ A single-member LLC disregarded federally is OUT of both returns as a FILER "
              "(PTR 97-2 / CTR 97-2) but CAN be a PTE-participating OWNER. Two roles, opposite "
              "answers — do not collapse them."},
    {"diagnostic_id": "D_AZ120S_NO_OPTICAL_MEDIA", "severity": "warning",
     "title": "S corporations filing on paper must submit K-1s BY PAPER — no optical-media path",
     "condition": "an S corporation is paper-filing with a large shareholder count",
     "message": ("The Form 120S book says: 'S Corporations filing a paper return must submit "
                 "Schedule(s) K-1 and K-1(NR) to the department BY PAPER.' The CD / DVD / flash-drive "
                 "(Excel spreadsheet) alternative exists ONLY on the partnership side, where the Form "
                 "165 book offers it for returns above the ~66,054-K-1 electronic ceiling. DO NOT PORT "
                 "THE OPTICAL-MEDIA PATH TO FORM 120S."),
     "notes": "The 246 MB electronic size limit still applies to both."},
    {"diagnostic_id": "D_AZ120S_QSUB_SINGLE_RETURN", "severity": "info",
     "title": "A QSub is not a separate Arizona filer",
     "condition": "the S corporation has a qualified subchapter S subsidiary",
     "message": ("'Qualified subchapter S subsidiaries are not treated as entities separate from the "
                 "parent corporation and would be included on a SINGLE Arizona Form 120S filed by the "
                 "parent S Corporation.' Entity classification otherwise follows the federal "
                 "check-the-box result (PTR 97-1 / CTR 97-1 — note the different ruling prefixes for "
                 "what is described as the same rule)."),
     "notes": "Forms 51 and 122 are Form 120 only and have no PTE application."},
    {"diagnostic_id": "D_AZ120S_SCHD_FOUR_COLUMNS", "severity": "info",
     "title": "Schedule D has FOUR payment columns; Form 165's Schedule F has three",
     "condition": "line 22 is computed",
     "message": ("Form 120S Schedule D separates '(c) S Corp Estimated Payment' from '(d) PTE "
                 "Estimated Payments' because an S corporation can owe BOTH a corporate-level tax and "
                 "a PTE tax in the same year. Line 22's instruction confirms the merge point: 'Enter "
                 "the total of line D7, column (c), and line D7, column (d) from Schedule D.' A "
                 "partnership cannot owe a corporate-level tax, so Form 165's Schedule F has ONE "
                 "estimated column."),
     "notes": "Do not reuse one payment-schedule model across the two forms."},
    {"diagnostic_id": "D_AZ120S_XFOOT_PART2", "severity": "error",
     "title": "Part 2 cross-foot failed: lines 39 + 41 + 43 + 45 must equal line 37",
     "condition": "line 39 + line 41 + line 43 + line 45 != line 37",
     "message": ("Printed on the face: 'NOTE: The total of lines 39, 41, 43, and 45 must equal the "
                 "amount on line 37.' Every shareholder's ownership share must land in exactly one of "
                 "the four buckets. Also check 43A + 43B == 43."),
     "notes": "One of two face-printed proof obligations; the other is C8 column (c) == 1.000000."},
    {"diagnostic_id": "D_AZ120S_EST_BASIS_NO_ANALOGUE", "severity": "warning",
     "title": "⚠ § 43-1401(2) is a PARTNERSHIP definition -- the S-corp figure is an inference",
     "condition": "the § 43-581(C) $150,000 estimated-payment test is applied to an S corporation",
     "message": ("Campaign D-12 A1 as REFINED rules that the $150,000 threshold is measured on "
                 "ARIZONA TAXABLE INCOME as defined by A.R.S. 43-1401(2). ⚠ THAT SECTION IS THE "
                 "DEFINITIONS SECTION OF TITLE 43 CHAPTER 14 -- THE PARTNERSHIP CHAPTER -- AND ITS "
                 "SUBSECTION (2) DEFINES 'Arizona taxable income' OF A PARTNERSHIP. THERE IS NO "
                 "S-CORPORATION ANALOGUE IN IT, and no corporate 'Arizona taxable income' definition "
                 "was pulled by the research pass, while 43-581(C) reaches 'an entity that is treated "
                 "as a partnership OR S CORPORATION'. DELVIO RESOLVES THE S-CORP FIGURE TO PRIOR-YEAR "
                 "FORM 120S LINE 1 BY BUILDING TO THE FORM: Form 120S carries no Arizona modification "
                 "apparatus at all, so applying the 43-1401(2) shape to it changes nothing and line 1 "
                 "= line 37 is the only Arizona income figure the return produces. REVIEW THIS "
                 "ENTITY'S THRESHOLD DETERMINATION."),
     "notes": ("⚠⚠ AN ENGINEERING INFERENCE, NOT A PUBLISHED AZDOR OR STATUTORY DEFINITION, AND A "
               "SECOND-ORDER CONSEQUENCE OF THE A1 REFINEMENT RATHER THAN SOMETHING THE REFINEMENT "
               "RULED ON. It follows the campaign's standing build-to-the-form posture (D-10 ruling "
               "2, D-11 A1, D-12 A3 and A4) rather than synthesising a corporate definition Arizona "
               "has never stated. Settled by an AZDOR answer on 43-581(C) (which also closes U19), or "
               "by pulling a corporate 'Arizona taxable income' definition. Flagged to Ken as an open "
               "second-order question. Constant: AZ_EST_MEASUREMENT_SCORP_GAP.")},
    {"diagnostic_id": "D_AZ120S_SCHC_XFOOT", "severity": "error",
     "title": "Schedule C cross-foot failed: C8 column (c) must total 1.000000",
     "condition": "Schedule C line C8 column (c) != 1.000000",
     "message": ("Printed on the face: '(Column (c) should total 1.000000)'. C8 = C6 + C7. ⚠ "
                 "Look-through shareholders (a grantor trust disregarded federally, or an SMLLC "
                 "disregarded to an individual) that did NOT opt out belong in C1-C3, THE INDIVIDUAL "
                 "ROWS."),
     "notes": "Form 165's E8 says 'should EQUAL 1.000000' for the same rule — a cosmetic difference."},
]


# ═══════════════════════════════════════════════════════════════════════════
# FORM AZ_120S — TEST SCENARIOS
# ═══════════════════════════════════════════════════════════════════════════
AZ120S_SCENARIOS: list[dict] = [
    {"scenario_name": "AZ-120S ordinary electing S corp — no federal-level tax, all resident",
     "scenario_type": "normal", "sort_order": 1,
     "inputs": {"question_A": True, "line_1": 800_000, "has_federal_level_taxable_income": False,
                "C1_c": "1.000000", "C7_c": "0.000000"},
     "expected_outputs": {"line_12": None, "line_17": 0, "line_37": 800_000, "line_39": 800_000,
                          "line_46": 800_000, "line_47": 20_000, "line_48": 0, "line_51": 0,
                          "line_52": 20_000, "line_18": 20_000, "line_19": 20_000},
     "notes": ("⚠ LINE 12 IS BLANK, NOT ZERO — the $50 minimum applies ONLY when the S corporation has "
               "federal-level taxable income. And line 37 = line 1 with NO Arizona modifications: "
               "2.5% of $800,000 = $20,000.")},
    {"scenario_name": "AZ-120S the $50 MINIMUM ORACLE — conditional in BOTH directions",
     "scenario_type": "edge", "sort_order": 2,
     "inputs": {"cases": [{"line_11": 0, "federal_level_income": True},
                          {"line_11": -50_000, "federal_level_income": True},
                          {"line_11": 100_000, "federal_level_income": True},
                          {"line_11": 100_000, "federal_level_income": False}]},
     "expected_outputs": {"case_1": 50, "case_2": 50, "case_3": 4_900, "case_4": None},
     "notes": ("'ONLY IF it has income subject to tax at the corporate level reported on federal Form "
               "1120S, EVEN IF LINE 11 IS ZERO OR A NEGATIVE AMOUNT. ... the greater of $50 or 4.9% of "
               "line 11.' Case 4 returns None (BLANK), not 0 — an S corp with no federal-level income "
               "owes nothing at the corporate level regardless of its Arizona figure.")},
    {"scenario_name": "AZ-120S NO MODIFICATION APPARATUS — both guards must REFUSE",
     "scenario_type": "failure", "sort_order": 3,
     "inputs": {"attempts": ["az_120s_modification(...)", "az_120s_depreciation_adjustment(...)"]},
     "expected_outputs": {"raises": "ArizonaFormGovernsError",
                          "AZ_120S_HAS_MODIFICATION_APPARATUS": False,
                          "AZ_120S_HAS_DEPRECIATION_LOGIC": False,
                          "AZ_120S_LINE37_EQUALS_LINE1": True,
                          "modification_statute_citations_in_book": 0,
                          "arizona_basis_string_occurrences": 0},
     "notes": ("⚠⚠ THE PINNED VERIFIED NEGATIVE. 'The rule says no', not 'no rule found': four "
               "independent kinds of evidence (statute-cite census, face comparison, the whole-chain "
               "trace, and A.R.S. 43-1014(B)(1)(b) itself), plus 70 addition/subtraction hits read in "
               "context and disproven as an alarm. Campaign D-12 Group B: NO SHARED ARIZONA "
               "MODIFICATION ENGINE. IF THIS SCENARIO EVER GOES GREEN BY BEING DELETED, SOMEONE HAS "
               "ADDED A 120S MODIFICATION FIELD 'FOR SYMMETRY'.")},
    {"scenario_name": "AZ-120S CREDIT ORDERING — nonrefundable credits cannot touch the PTE tax",
     "scenario_type": "edge", "sort_order": 4,
     "inputs": {"line_12": 4_900, "line_13": 0, "line_15": 4_900, "line_52": 20_000, "line_20": 1_000},
     "expected_outputs": {"line_14": 4_900, "line_17": 0, "line_18": 20_000, "line_19": 20_000,
                          "nonrefundable_credit_applied_to_pte_tax": 0,
                          "refundable_credit_reduces_amount_owed": True},
     "notes": ("The $4,900 nonrefundable credit wipes out the corporate-level tax and NOTHING SPILLS "
               "OVER to the $20,000 PTE tax, because line 15 is applied to line 14 and the PTE tax "
               "arrives at line 18. The $1,000 refundable credit sits in the payments block and does "
               "reduce what is owed. ⚠ Pub 713 says both 'No' and 'nothing precludes' (U4); the form "
               "is not ambiguous.")},
    {"scenario_name": "AZ-120S LINE 49 CROSS-CHECK — a multistate electing S corp with no line 7",
     "scenario_type": "edge", "sort_order": 5,
     "inputs": {"question_B_multistate": True, "question_A": True,
                "has_built_in_gains": False, "has_excess_net_passive_income": False,
                "schedule_A_line_A5": "0.412500"},
     "expected_outputs": {"line_7": None, "line_49": "0.412500",
                          "hard_equality_check_applies": False,
                          "instruction_names_line_45": "an INCOME amount, not a ratio"},
     "notes": ("⚠ AZ-D2 / W8, BOTH HALVES. The instruction misprints the ratio line as 'line 45', and "
               "its 'must be the same as line 7' cannot be a hard equality because line 7 is never "
               "reached without federal-level taxable income. Encode: IF line 7 is populated, line 49 "
               "must equal it; OTHERWISE take Schedule A line A5 / A3f or Schedule ACA line 3 "
               "directly.")},
    {"scenario_name": "AZ-120S the '$0 return' refund script — estimates paid, election declined",
     "scenario_type": "edge", "sort_order": 6,
     "inputs": {"question_A": False, "pte_estimated_payments_made": 30_000,
                "extension_payments": 0, "refundable_credits": 0},
     "expected_outputs": {"part2_required": True, "line_37": 0, "line_46": 0, "line_47": 0,
                          "line_48": 0, "line_50": 0, "line_51": 0, "line_52": 0, "line_18": 0,
                          "line_19": 0, "line_22": 30_000, "line_24": 30_000, "line_26": 30_000,
                          "line_27": 30_000, "line_29": 30_000, "line_34": 30_000, "line_36": 30_000,
                          "refund_applicable_to_2026_pte_estimates": False,
                          "refund_applicable_to_shareholder": False},
     "notes": ("The instruction book's own line-by-line script, followed exactly. ⚠ 'This refund "
               "cannot be applied to the S Corporation's 2026 taxable year PTE estimated tax "
               "liability. It cannot be applied to an individual shareholder's tax liability.' TWO "
               "VARIANTS exist and the 'subject to Arizona income tax' one runs lines 19-26 "
               "differently.")},
    {"scenario_name": "AZ-120S PART-YEAR SHAREHOLDER — two schedules, and 43A + 43B must foot",
     "scenario_type": "edge", "sort_order": 7,
     "inputs": {"line_37": 500_000, "C3_c": "0.200000", "months_resident": 6,
                "line_43A": 50_000, "line_43B": 50_000, "line_49": "0.500000"},
     "expected_outputs": {"line_43": 100_000, "43A_plus_43B": 100_000,
                          "line_46_component_from_43A": 50_000,
                          "line_48_component_from_43B": 50_000,
                          "schedules_issued_to_this_shareholder": 2},
     "notes": ("⚠ A PART-YEAR OWNER RECEIVES **TWO** SCHEDULES — a Schedule K-1 for the resident "
               "period and a Schedule K-1(NR) for the nonresident period (Pub 713 footnote 2). The "
               "resident-period half is taxed WITHOUT apportionment at line 46/47; the "
               "nonresident-period half is APPORTIONED at line 48/49/50 before the rate.")},
    {"scenario_name": "AZ-120S K-1(NR) LINE MAP — off by one from the partnership schedule",
     "scenario_type": "failure", "sort_order": 8,
     "inputs": {"line_number": 12, "schedule": "AZ_120S_SCHK1NR"},
     "expected_outputs": {"az120s_k1nr_line_12": "IRC Section 179 expense",
                          "az165_k1nr_line_12": "Other income (loss): include schedule",
                          "az165_k1nr_line_13": "IRC Section 179 expense",
                          "cause": "the 120S schedule has NO guaranteed-payments line"},
     "notes": ("⚠ A SHARED LINE MAP SILENTLY MIS-POSTS EVERY ITEM FROM 10 ON. The 165 K-1(NR) has "
               "'Guaranteed payments to partner' at line 10 and the 120S has none — correctly, since "
               "S corporations make no guaranteed payments.")},
    {"scenario_name": "AZ-120S SPECIAL ALLOCATION — forbidden here, honoured on Form 165",
     "scenario_type": "failure", "sort_order": 9,
     "inputs": {"shareholder_stock_ownership": "0.500000", "attempted_allocation": "0.700000"},
     "expected_outputs": {"allowed": False, "schedule_B_column_g": "0.500000",
                          "az_165_equivalent_allowed": True},
     "notes": ("Pub 713: 'An S Corporation may not allocate its income and loss items to its "
               "shareholders using a special allocation.' Form 165's Schedule D instruction says the "
               "opposite for partnerships and Pub 713 carries a worked partnership example. ENCODE THE "
               "ASYMMETRY.")},
    {"scenario_name": "AZ-120S ESTIMATED PAYMENTS — the S-corp side of the $150,000 test",
     "scenario_type": "edge", "sort_order": 10,
     "inputs": {"prior_year_taxable_income": 150_000, "also_test": 150_001},
     "expected_outputs": {"at_150_000": False, "at_150_001": True,
                          "measurement_basis": "statutory_bare_taxable_income",
                          "book_also_says": "PTE income (an internal contradiction)"},
     "notes": ("A.R.S. 43-581(C) reaches 'an entity that is treated as a partnership OR S CORPORATION'. "
               "⚠ THE FORM 120S BOOK CONTRADICTS ITSELF, using bare 'taxable income' in one place and "
               "'PTE income' in another — one of the four documents that do. D-12 A1 ruled the "
               "statutory reading and REFINED it to 43-1401(2)'s Arizona taxable income; U19 stays "
               "open as a fact.")},
    {"scenario_name": "AZ-120S A1 REFINED — 43-1401(2) has NO S-corp analogue, and the figure says so",
     "scenario_type": "failure", "sort_order": 13,
     "inputs": {"form_code": "AZ_120S", "prior_year_line_1": 800_000},
     "expected_outputs": {"basis_resolves_to": "arizona_taxable_income",
                          "definition": "A.R.S. 43-1401(2)",
                          "figure": 800_000, "source_line": "PRIOR-YEAR Form 120S line 1",
                          "required": True, "provisional": True,
                          "is_engineering_inference": True,
                          "diagnostic": "D_AZ120S_EST_BASIS_NO_ANALOGUE"},
     "notes": ("⚠⚠ THE SECOND-ORDER GAP THE A1 REFINEMENT CREATES, RECORDED RATHER THAN PAPERED. "
               "A.R.S. 43-1401 is the DEFINITIONS section of Title 43 CHAPTER 14 — the PARTNERSHIP "
               "chapter — and its subsection (2) defines 'Arizona taxable income' OF A PARTNERSHIP. "
               "THERE IS NO S-CORPORATION ANALOGUE, while 43-581(C) reaches both entity types. Delvio "
               "resolves to line 1 BY BUILDING TO THE FORM (Form 120S has no Arizona modification "
               "apparatus, so there is nothing to adjust and line 1 = line 37 is the only Arizona "
               "income figure the return produces) — the campaign's standing posture, NOT a "
               "synthesised corporate definition. IT IS STILL AN ENGINEERING INFERENCE AND THE FLAG "
               "SAYS SO.")},
    {"scenario_name": "AZ-120S INFORMATION RETURN PENALTY — line 32 must be blank when electing",
     "scenario_type": "failure", "sort_order": 11,
     "inputs": {"question_A": True, "months_late": 3, "line_32_attempted": 300},
     "expected_outputs": {"line_32": 0, "if_not_electing_would_be": 300},
     "notes": "'S Corporations that made the PTE election, this is not an information return. DO NOT "
              "ENTER AN AMOUNT ON LINE 32.' Three months late for a NON-electing S corp is $300."},
    {"scenario_name": "AZ-120S MULTISTATE GATE — question B 'Yes' MEANS multistate",
     "scenario_type": "failure", "sort_order": 12,
     "inputs": {"question_B_answer_yes": True},
     "expected_outputs": {"az_is_multistate_AZ_120S": True, "az_is_multistate_AZ_165_same_answer": False},
     "notes": "⚠ INVERTED FROM FORM 165 QUESTION D, which asks whether the partnership is "
              "ARIZONA-ONLY. az_is_multistate() takes the form code and refuses an unknown one."},
]


# ═══════════════════════════════════════════════════════════════════════════
# SHARED DIAGNOSTICS — attached to BOTH specs. The cross-cutting rulings, the
# open [UNVERIFIED] register, and the RED-DEFERS.
# ⚠ EVERY RED-DEFER HAS ITS OWN DIAGNOSTIC: NO SILENT GAP, AND NOTHING SILENTLY
# INCLUDED EITHER.
# ═══════════════════════════════════════════════════════════════════════════
AZ_SHARED_DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_AZ_TY2026_CONFORMITY_STALE", "severity": "error",
     "title": "⚠ STALENESS TRIPWIRE — every figure in this spec is TY2025-keyed",
     "condition": "the engagement tax year is later than 2025",
     "message": ("ARIZONA'S CONFORMITY SWITCHES SUBSECTION FOR TY2026. A.R.S. 43-105(B) governs TY2025 "
                 "(taxable years beginning after 12/31/2024 THROUGH 12/31/2025) and is a COMPOUND "
                 "rule: the IRC in effect January 1, 2025, excluding changes enacted after that date, "
                 "PLUS those provisions of P.L. 119-21 that are RETROACTIVELY EFFECTIVE in TY2025. "
                 "A.R.S. 43-105(A) governs TY2026+ and is a clean January 1, 2026. SEPARATELY, the "
                 "IRC 168(n) qualified-production-property add-backs at 43-1021(17) and 43-1121(25) "
                 "BEGIN IN TY2026 under Ch. 140 Sec. 35(B) — a TY2026 spec must model them and a "
                 "TY2025 spec must not. RE-VERIFY EVERY FIGURE BEFORE ANY TY2026 AUTHORING."),
     "notes": ("The tax-year-keyed lookup _yk() RAISES rather than defaulting, so a TY2026 engagement "
               "cannot silently inherit TY2025 law. ⚠ AZDOR reissued essentially the whole "
               "corporate/partnership instruction set between 2026-08-06 and 2026-08-12 and may do so "
               "again. ⚠ A TY2026 pass MUST re-read the Form 165 page-6 A4 worksheet: if AZDOR adds a "
               "QPP row it lands there, and if it does not, IRC 168(n) inherits the 'no line exists' "
               "problem. ⚠ azleg still serves PRE-Ch.140 text for 43-1021.")},
    {"diagnostic_id": "D_AZ_CONFORMITY_COMPOUND", "severity": "info",
     "title": "⚠ Arizona's TY2025 conformity is NEITHER 1/1/2025 NOR 1/1/2026 — it is BOTH-ish",
     "condition": "any Arizona conformity determination is made for TY2025",
     "message": ("A.R.S. 43-105(B), as amended by H.B. 4168 (Laws 2026 Ch. 140 Sec. 12): the IRC in "
                 "effect JANUARY 1, 2025, including provisions that became effective during 2024 with "
                 "specific adoption of all retroactive effective dates, BUT EXCLUDING any changes "
                 "enacted after January 1, 2025, AND INCLUDING those provisions of P.L. 119-21 that "
                 "are RETROACTIVELY EFFECTIVE during taxable years beginning after December 31, 2024 "
                 "through December 31, 2025. ⚠ THE PRACTITIONER HEADLINE 'Arizona updated conformity "
                 "to January 1, 2026' DESCRIBES SUBSECTION (A) AND THEREFORE TY2026. Porting it into "
                 "a TY2025 engagement is the single most likely way to get Arizona wrong."),
     "notes": ("Ch. 140 Sec. 35 SPLITS the retroactivity: Sec. 35(A) reaches taxable years beginning "
               "after 12/31/2024 for 42-1001, 43-105, 43-1022, 43-1041, 43-1121 and 43-1122; "
               "Sec. 35(B) reaches only after 12/31/2025 for 43-1021, 43-1042, 43-1073.01, 43-1074.01 "
               "and 43-1168. That split is why the individual SUBTRACTIONS reach TY2025 while the "
               "individual ADDITIONS (including the new IRC 168(n) paragraph) do not.")},
    {"diagnostic_id": "D_AZ_NO_SHARED_MOD_ENGINE", "severity": "error",
     "title": "⚠⚠ Arizona's two PTE returns do NOT share a modification engine (campaign D-12)",
     "condition": "a shared federal-to-Arizona modification model is applied across AZ_165 and AZ_120S",
     "message": ("FORM 165 carries a full modification stack ON THE FACE — Schedule A additions A1-A4, "
                 "Schedule B subtractions B1-B5, three page-6 worksheets, a FIVE-vintage-tier "
                 "depreciation recomputation, line 5 'adjusted to Arizona basis' and line 6 'net "
                 "adjustment' — and its PTE base is line 5 PLUS line 9. FORM 120S CARRIES NONE OF IT "
                 "AND ITS PTE BASE IS LINE 37 = LINE 1. ANY LOADER THAT PORTS THE 165 SCHEDULE A/B "
                 "STACK ONTO FORM 120S WILL BE COMPUTING LINES THAT DO NOT EXIST ON THE FORM."),
     "notes": ("⚠ THE ASYMMETRY IS REAL ECONOMICS, NOT BOOKKEEPING. The individual bonus rule Form 165 "
               "applies is net-zero ONLY for post-2016 assets; it does NOT cancel for the 0% / 10% / "
               "55% tiers or for the 43-1022(18) disposition true-up. A partnership with an old asset "
               "base therefore computes a DIFFERENT PTE base than an otherwise identical S "
               "corporation, and Delvio surfaces it. Other asymmetries in the same family: Form 120S "
               "has a corporate-level tax, credit lines and recapture where Form 165 has none; Form "
               "165 honours SPECIAL ALLOCATIONS where Form 120S forbids them; Schedule D has FOUR "
               "payment columns where Schedule F has three; the two K-1(NR) line maps are OFF BY ONE.")},
    {"diagnostic_id": "D_AZ_PART2_GATE_NOT_QA_ONLY", "severity": "error",
     "title": "⚠ Part 2 is NOT gated on question A alone — estimates paid also open it",
     "condition": "question A = No and PTE estimated payments were made during the taxable year",
     "message": ("Both Part 2 headers read '... or estimated payments were made and the "
                 "partnership/S Corporation is not claiming the PTE election.' The gate is "
                 "`Q.A == Yes OR pte_estimates_paid > 0`. AN ENTITY THAT PREPAID PTE ESTIMATES AND "
                 "THEN DECLINED THE ELECTION MUST STILL COMPLETE PART 2 — with zeros — TO GET ITS "
                 "MONEY BACK. Both instruction books script the path line by line, and Pub 713 frames "
                 "it explicitly around the federal SALT deduction rising from $10,000 to $40,000 in "
                 "2025, which makes it the most likely real-world Arizona PTE filing for TY2025."),
     "notes": ("W18. ⚠ THE REFUND CANNOT BE APPLIED TO THE NEXT YEAR'S PTE ESTIMATES AND CANNOT BE "
               "APPLIED TO AN OWNER'S LIABILITY — it comes back to the entity as cash. ⚠ TWO SCRIPTED "
               "VARIANTS exist on Form 120S and the second runs lines 19-26 differently.")},
    {"diagnostic_id": "D_AZ_MULTISTATE_QUESTION_INVERT", "severity": "error",
     "title": "⚠ Form 165 question D and Form 120S question B are INVERTED booleans",
     "condition": "a shared multistate boolean is applied across the two Arizona forms",
     "message": ("Form 165 question D asks 'Is this partnership an ARIZONA-ONLY partnership?' — 'Yes' "
                 "means NOT multistate, and the line 22 instruction says 'If Line D is \"Yes\", enter "
                 "1.0'. Form 120S question B asks 'Does the S corporation conduct business WITHIN AND "
                 "WITHOUT Arizona?' — 'Yes' means IS multistate. SAME CONCEPT, OPPOSITE POLARITY. A "
                 "shared boolean is wrong for one of them."),
     "notes": "az_is_multistate(form_code, answer) takes the form code and RAISES on an unknown one "
              "rather than defaulting."},
    {"diagnostic_id": "D_AZ_APPORT_DIVISOR_DYNAMIC", "severity": "warning",
     "title": "The Arizona apportionment divisor is DYNAMIC: 4, 3, 2, or none",
     "condition": "any factor has a zero numerator or a zero denominator",
     "message": ("A.A.C. R15-2D-901(B) and both instruction books: 'exclude a factor if BOTH the "
                 "numerator and the denominator of a factor are zero. DO NOT exclude a factor if the "
                 "numerator is zero and the denominator is greater than zero.' Then: property or "
                 "payroll excluded -> divide by THREE; SALES excluded -> divide by TWO; two factors "
                 "excluded -> the remaining factor, WITHOUT RESPECT TO ANY WEIGHTING, IS the "
                 "apportionment ratio."),
     "notes": ("⚠ A ZERO NUMERATOR OVER A POSITIVE DENOMINATOR IS A LIVE ZERO FACTOR — the rule most "
               "engines get wrong. ⚠ WHEN SALES IS EXCLUDED THE DIVISOR DROPS TO TWO EVEN THOUGH SALES "
               "IS DOUBLE-WEIGHTED: the weighting and the divisor are NOT tied together. Caps: "
               "property 1.0; sales 2.0 STANDARD / 1.0 SALES FACTOR ONLY. Six decimals, rounding the "
               "sixth up at a seventh digit of five or more.")},
    {"diagnostic_id": "D_AZ_RATIO_ZERO_VS_BLANK", "severity": "error",
     "title": "⚠ An apportionment ratio of 0.000000 and a BLANK mean OPPOSITE things",
     "condition": "the apportionment ratio is zero or null",
     "message": ("Printed on both returns: 'If line C5 [Form 120S: line 7] is \"0.000000\", the "
                 "partnership/S Corporation is considered to have NO ARIZONA NEXUS. If it is BLANK OR "
                 "\"1.000000\", the income is considered to be sourced ENTIRELY WITHIN ARIZONA.' A "
                 "NULL-VS-ZERO BUG HERE SILENTLY ZEROES EVERY NONRESIDENT OWNER'S ARIZONA INCOME."),
     "notes": "az_nexus_from_ratio() distinguishes the three states explicitly."},
    {"diagnostic_id": "D_AZ_150K_BOUNDARY_EXCEEDS", "severity": "info",
     "title": "The $150,000 estimated-payment test is STRICTLY GREATER — exactly $150,000 is OUT",
     "condition": "prior-year taxable income is at or near $150,000",
     "message": ("A.R.S. 43-581(C): '...whose taxable income for the taxable year EXCEEDS $150,000 in "
                 "the preceding taxable year shall make payments of estimated tax...' SEVEN "
                 "INDEPENDENT SOURCES SAY 'EXCEEDS' — the statute, the Form 165 instructions, the Form "
                 "120S instructions, the Form 220/PTE instructions (x2), the Form 120/PTE-W "
                 "instructions (x2), Booklet 120/165ES (x3) and Pub 713's narrative. EXACTLY ONE "
                 "SOURCE SAYS 'OR MORE': a single Pub 713 FAQ answer — and Pub 713's own FAQ lead-in "
                 "offers a THIRD phrasing, 'meets or exceeds'. PUB 713 IS INTERNALLY INCONSISTENT "
                 "THREE WAYS AND CANNOT DISPLACE THE STATUTE."),
     "notes": ("⚠⚠ AN EARLIER VERIFICATION PASS 'CORRECTED' THIS THE WRONG WAY — conformity/"
               "az_conformity.md section 4 and its section 12 correction H flipped 'exceeds' to 'or "
               "more' on the strength of that one FAQ sentence — AND A LATER PASS CAUGHT IT. THE "
               "CAMPAIGN RECORD STILL NEEDS AMENDING. Vintage-clean: 43-581 is amended by neither "
               "Laws 2025 Ch. 182 nor Laws 2026 Ch. 140 ('43-581' occurs ZERO times in the Ch. 140 "
               "chaptered PDF). validate_az.py pins the boundary in BOTH directions so it cannot "
               "drift back. A CHECKING PASS IS NOT SELF-VALIDATING.")},
    {"diagnostic_id": "D_AZ_U19_150K_BASIS", "severity": "warning",
     "title": "⚠ WHICH taxable income measures $150,000 is a RULING, not a published AZDOR position",
     "condition": "the § 43-581(C) estimated-payment test is applied",
     "message": ("AZDOR PRINTS FOUR DIFFERENT MEASUREMENT BASES AND FOUR OF SIX DOCUMENTS CONTRADICT "
                 "THEMSELVES INTERNALLY: (1) bare 'taxable income' — the statute, both entity "
                 "instruction books, one Form 120/PTE-W sentence, the Pub 713 narrative; (2) 'ARIZONA "
                 "taxable income' — Form 220/PTE x2, another 120/PTE-W sentence, the Pub 713 FAQ; "
                 "(3) 'PTE INCOME', i.e. only the consenting owners' share — BOTH entity instruction "
                 "books; (4) 'TOTAL taxable income' — Booklet 120/165ES. WORKED CASE: an entity with "
                 "$1,000,000 of Arizona taxable income and 10% consenting ownership has $100,000 of "
                 "PTE income — IN under base 2, OUT under base 3, FROM READINGS PRINTED IN THE SAME "
                 "BOOK. It decides whether the Form 220/PTE underpayment penalty applies. CAMPAIGN "
                 "D-12 A1 RULED the statute's bare 'taxable income', AND WAS REFINED THE SAME "
                 "SESSION BECAUSE THAT NAMED A SOURCE WITHOUT NAMING A NUMBER: A.R.S. § 43-1401(2) "
                 "DEFINES the statute's term as 'ARIZONA TAXABLE INCOME', so Delvio computes that "
                 "figure — PRIOR-YEAR Form 165 LINE 5 for a partnership (⚠ NOT line 10, the larger "
                 "PTE base), and PRIOR-YEAR Form 120S LINE 1 for an S corporation. TREAT THIS "
                 "ENTITY'S THRESHOLD DETERMINATION AS PROVISIONAL."),
     "notes": ("[UNVERIFIED] U19 STAYS OPEN AS A MATTER OF FACT. Still recorded as a RULING ON A "
               "CONTESTED QUESTION, NOT A PUBLISHED AZDOR POSITION — THE REFINEMENT NARROWS WHAT WE "
               "COMPUTE, IT DOES NOT CLOSE THE QUESTION. All four candidates are kept in "
               "AZ_EST_MEASUREMENT_BASIS_CANDIDATES with the three losers explicitly NOT REFUTED, so "
               "a DOR answer can be ADJUDICATED rather than inherited, and the basis is a SINGLE "
               "NAMED CONSTANT (plus its RESOLVES_TO second leg) so a DOR answer changes ONE THING. "
               "Settled by an AZDOR ruling, procedure, or written Corporate Income Tax section "
               "response. ⚠ THE SEPARATE BOUNDARY QUESTION IS SETTLED AND NEEDED NO RULING. "
               "⚠⚠ SECOND-ORDER GAP: § 43-1401 is a chapter-14 PARTNERSHIP definitions section with "
               "NO S-corp analogue — see D_AZ120S_EST_BASIS_NO_ANALOGUE.")},
    {"diagnostic_id": "D_AZ_EST_4TH_INSTALLMENT_MONTH", "severity": "error",
     "title": "⚠ The FOURTH PTE installment is the 1st month AFTER year end, not the 12th month",
     "condition": "PTE estimated installment dates are computed",
     "message": ("Both instruction books and Pub 713 agree verbatim: 'Estimated tax payments are due "
                 "the 15th day of the 4th, 6th, and 9th months of the current taxable year. THE FINAL "
                 "PAYMENT IS DUE THE 15TH DAY OF THE 1ST MONTH FOLLOWING THE CLOSE OF THE TAXABLE "
                 "YEAR.' For a calendar-year filer: April 15, June 15, September 15, and JANUARY 15 OF "
                 "THE FOLLOWING YEAR. ⚠ FORM 220/PTE LINE 7 PRINTS THE CORPORATE PATTERN ON ITS FACE "
                 "('the 15th day of the 4th, 6th, 9th, and 12th months of the taxable year') and "
                 "appends 'PTE's see instructions', where the 1st-month rule lives. A LOADER READING "
                 "THE FACE ALONE PUTS THE FOURTH INSTALLMENT THREE MONTHS EARLY."),
     "notes": ("W17. Required annual payment = THE SMALLER OF 90% of the current year's Arizona tax "
               "liability or 100% of the prior year's tax due — a SAFE HARBOUR framing, not a minimum. "
               "'Tax liability' means the liability reduced by refundable credits and the claim of "
               "right adjustment. No penalty when the Arizona liability due is under $1,000 "
               "(43-581(E)(2)); no overpayment penalty at all. ⚠ Form 220/PTE Part C line 17 also "
               "substitutes months by form type: 'Forms 120S: Use 3rd month instead of 4th month. "
               "PTE's: Use 3rd month instead of 4th month.'")},
    {"diagnostic_id": "D_AZ_U9_PTE_CREDIT_PAID_VS_OWED", "severity": "warning",
     "title": "The owner PTE credit is keyed to tax PAID, but the form computes tax OWED",
     "condition": "PTE tax payments are less than Form 165 line 25 / Form 120S line 52",
     "message": ("A.R.S. 43-1077(B): the credit is 'the portion of the tax PAID by the partnership or "
                 "S corporation under section 43-1014 that is attributable to the partner's or "
                 "shareholder's share of income taxable in this state.' Pub 713 hammers it: 'A tax "
                 "credit is a dollar-for-dollar reduction of the amount of taxes owed by a taxpayer. "
                 "It is not a payment of tax. ... if the partnership or S Corporation does not pay its "
                 "PTE tax liability, [it] cannot pass through the full amount of its PTE tax liability "
                 "as a tax credit.' BUT FORM 165 LINE 25 AND FORM 120S LINE 52 COMPUTE TAX OWED, AND "
                 "NO SCHEDULE RECONCILES OWED TO PAID BEFORE THE K-1s ARE CUT. Delvio allocates from "
                 "the LIABILITY, matching Pub 713's own Addendum #1 worked example. THE ENTITY HAS "
                 "UNDERPAID — REVIEW THE CREDIT ALLOCATION BEFORE ISSUING THE K-1s."),
     "notes": ("[UNVERIFIED] U9 / W19. Backstop at 43-1014(B)(2): 'If the partnership or S corporation "
               "does not pay the amount owed to the department ..., the department may collect the "
               "amount FROM THE PARTNERS OR SHAREHOLDERS based on the proportionate share of income "
               "that is attributable to each.' Settled by an AZDOR clarification or a Gate-1 ruling.")},
    {"diagnostic_id": "D_AZ_179_RULING_NOT_PUBLISHED", "severity": "info",
     "title": "Arizona's TY2025 § 179 limits are a campaign RULING, not a published Arizona figure",
     "condition": "an IRC 179 deduction is present in an Arizona PTE computation",
     "message": ("CAMPAIGN DECISION D-10 (2026-08-16) ruled Arizona's TY2025 IRC 179 limits to "
                 "$2,500,000 / $4,000,000 on a BROAD reading of A.R.S. 43-105(B)'s OBBBA graft clause. "
                 "THE MECHANISM IS VERIFIED: Arizona has NO IRC 179 modification in any of 43-1021, "
                 "43-1022, 43-1121 or 43-1122, and Arizona enumerates its modifications EXHAUSTIVELY "
                 "in those four sections — 'the rule says no', not 'no rule found'. THE RESULTING "
                 "NUMBER IS AN INFERENCE, because it routes through the graft clause and AZDOR has "
                 "published no provision-by-provision OBBBA mapping. ⚠ NEITHER ARIZONA PTE FORM STATES "
                 "AN IRC 179 FIGURE, so the ruling is invisible on the entity returns."),
     "notes": ("[UNVERIFIED] U3 STAYS OPEN AS A MATTER OF FACT. ⚠ THE ROUTING QUESTION D-10 DID NOT "
               "REACH: for a PARTNERSHIP, IRC 179 is a SEPARATELY-STATED ITEM under A.R.S. 43-1412(5) "
               "and enters the PTE base through FORM 165 LINE 9 — a single undifferentiated box "
               "covering sixteen statutory categories. For an S CORPORATION there is no routing "
               "question at all: line 37 = line 1 = federal Schedule K, already net of federal 179. "
               "The dollar limit and the routing are two different questions and only the limit was "
               "ruled on.")},
    {"diagnostic_id": "D_AZ_U3_OBBBA_MAP_UNPUBLISHED", "severity": "info",
     "title": "AZDOR has never published which OBBBA provisions it treats as retroactively effective",
     "condition": "the TY2025 conformity graft clause is relied on",
     "message": ("A.R.S. 43-105(B) adopts 'THOSE PROVISIONS OF PUBLIC LAW 119-21 THAT ARE "
                 "RETROACTIVELY EFFECTIVE DURING TAXABLE YEARS BEGINNING FROM AND AFTER DECEMBER 31, "
                 "2024 THROUGH DECEMBER 31, 2025' — A CATEGORY, NOT AN ENUMERATED LIST. Neither AZDOR "
                 "nor the Senate Fact Sheet publishes a provision mapping. AZDOR's 'Conformity to IRC' "
                 "page still stopped at '2024 Conformity' when last checked. Campaign D-10 governs "
                 "meanwhile."),
     "notes": ("[UNVERIFIED] U3. Searched both REISSUED TY2025 PTE instruction books (post-enactment "
               "ModDates) for '4168', '119-21', 'H.R. 1', 'One Big Beautiful', 'conformity' and '179' "
               "— NO SUBSTANTIVE HIT. Settled by an AZDOR conformity notice, tax ruling or procedure "
               "enumerating the adopted provisions. It may not exist.")},
    {"diagnostic_id": "D_AZ_168N_TY2026_ONLY", "severity": "info",
     "title": "§ 168(n) qualified production property: NO Arizona add-back for TY2025",
     "condition": "an IRC 168(n) special depreciation allowance is claimed federally",
     "message": ("H.B. 4168 created the add-backs at A.R.S. 43-1021(17) (individuals, Sec. 14) and "
                 "43-1121(25) (corporations, Sec. 22), and BOTH are expressly limited to 'TAXABLE "
                 "YEARS BEGINNING FROM AND AFTER DECEMBER 31, 2025' — reinforced by Ch. 140 "
                 "Sec. 35(B). FOR TY2025 ARIZONA ALLOWS THE IRC 168(n) ALLOWANCE WITH NO STATE "
                 "ADD-BACK, FOR EITHER OWNER CLASS. Neither PTE form has a 168(n) line and neither "
                 "instruction book mentions it — correct for TY2025."),
     "notes": "⚠ DO NOT CODE ONE IRC 168(n) RULE ACROSS BOTH YEARS. A TY2026 pass must re-read the "
              "Form 165 page-6 A4 worksheet."},
    {"diagnostic_id": "D_AZ_FORM_355_COLLISION", "severity": "info",
     "title": "⚠ Any 'Form 355' here is ARIZONA'S — a collision with Massachusetts Form 355",
     "condition": "the owner PTE credit is routed",
     "message": ("Arizona Form 355 is 'Credit for Entity-Level Income Tax Paid on Your Behalf', where "
                 "the owner claims the PTE credit — confirmed on the AZDOR K-1 faces themselves "
                 "('Individuals, enter this amount on Form 355, Part 1, line 1'). MASSACHUSETTS FORM "
                 "355 IS ITS C-CORPORATION EXCISE RETURN AND IS A DIFFERENT DOCUMENT ENTIRELY. ⚠ AND "
                 "THE ARIZONA LINE DIFFERS BY ENTITY TYPE: partnership K-1s route to Form 355 PART 1 "
                 "LINE 1; S-corp K-1s route to PART 1 LINE 2. Estates and trusts instead use Form "
                 "141AZ line 19."),
     "notes": ("Recorded because it is a pure form-number collision and a trap for the next reader. "
               "Massachusetts left Wave 4 for its own wave (campaign D-12 Group B). The Arizona brief "
               "was checked for cross-state contamination and came back CLEAN: zero Oregon hits, five "
               "Missouri hits all citing D-10 as a precedent SHAPE, and every 'Form 355' hit "
               "Arizona's.")},
    {"diagnostic_id": "D_AZ_FACE_GOVERNS_SKEW", "severity": "info",
     "title": "A November-2025 form face wearing an August-2026 instruction book — the FACE governs",
     "condition": "a face-versus-instruction divergence is encountered",
     "message": ("Form 165 face /ModDate 2025-11-13 and Form 120S face 2025-11-12 both PREDATE H.B. "
                 "4168 (signed 2026-06-13) by seven months, while the Form 165 instructions were "
                 "reissued 2026-08-11 and the Form 120S instructions were REGENERATED 2026-08-12. "
                 "ANY DIVERGENCE RESOLVES IN FAVOUR OF THE FACE, BECAUSE THE FACE IS WHAT IS E-FILED. "
                 "⚠ AND WHAT DID NOT CHANGE IS THE FINDING: despite reissuing after enactment, AZDOR "
                 "added no IRC 168(n) line, no conformity or OBBBA discussion, no change to the line "
                 "B1 tiers, no change to the 2.5% rate, and NO MCTCP subtractions to Schedule B or the "
                 "page-6 B5 worksheet. THE ENTITY-LEVEL PTE PACKAGE IS CONFORMITY-NEUTRAL FOR TY2025."),
     "notes": ("⚠ THIS IS A DIFFERENT QUESTION from a SUPPORTING form's routing list being wrong about "
               "a PARENT form (defects AZ-D3, AZ-D4 and Schedule ACA's U12) — there the PARENT'S own "
               "instructions govern. ⚠ AND IT HAS ONE KNOWN EXCEPTION IN THE OTHER DIRECTION: Form 165 "
               "lines 19 and 21 carry a zero floor that appears ONLY in the instructions, and the "
               "engine must supply it because Form 120S PRINTS the same floor on its face (W4). ⚠ Note "
               "this points the OPPOSITE way from Virginia's skew, where re-stamped forms with no "
               "H.R.1 line made the ABSENCE the finding.")},
    {"diagnostic_id": "D_AZ_ELECTION_CASCADE", "severity": "warning",
     "title": "Electing or revoking on an amended return is an N-OWNER-RETURN event",
     "condition": "the PTE election is being made or revoked on an amended return",
     "message": ("Pub 713: 'Making the PTE election on an amended return requires the "
                 "partnership/S Corporation wishing to make the election AND EACH PARTNER/SHAREHOLDER "
                 "WHO DID NOT OPT OUT to each file an amended Arizona return to claim the election. In "
                 "addition, the partnership or S Corporation and the partners or shareholders MAY BE "
                 "SUBJECT TO PENALTIES AND INTEREST.' Revocation is the mirror image: each consenting "
                 "owner must file an amended Arizona individual return REMOVING the PTE tax credit "
                 "previously claimed. BOTH ARE AVAILABLE ONLY BEFORE THE FOUR-YEAR STATUTE OF "
                 "LIMITATIONS EXPIRES; past it, the request will be DENIED."),
     "notes": ("A WORKFLOW FACT, NOT JUST A COMPUTATION. ⚠ The election is ANNUAL and NOT BINDING on "
               "future years — contrast 43-1126(C), which DOES make the federal S election effective "
               "'for all succeeding taxable years'. The drafters knew how to write a carry-forward "
               "election and did not do so here.")},
    {"diagnostic_id": "D_AZ_ES_BOOKLET_REPEALED_LAW", "severity": "warning",
     "title": "⚠ Booklet 120/165ES carries REPEALED law on election timeliness — vouchers only",
     "condition": "Booklet 120/165ES is consulted for anything other than the payment vouchers",
     "message": ("The file AZDOR posts under its 2025 row has /ModDate 2024-11-19 and is headed '2024 "
                 "CORPORATE INCOME TAX HIGHLIGHTS'. It still says 'This election must be made by the S "
                 "Corporation no later than the due date or extended due date of its return.' THAT "
                 "SENTENCE IS REPEALED LAW: S.B. 1274 = Laws 2025 Chapter 182 Sec. 6 struck the "
                 "timely-filing requirement and Sec. 9(A) made the repeal RETROACTIVE TO TAXABLE YEARS "
                 "BEGINNING AFTER DECEMBER 31, 2021. Pub 713 confirms AZDOR's administration. USE THE "
                 "BOOKLET FOR THE VOUCHERS ONLY."),
     "notes": ("This is not an AZDOR error — the '2025' ES booklet is published in late 2024 so "
               "taxpayers can make their 2025 estimated payments — but it means its NARRATIVE is "
               "pre-S.B.-1274 law. ⚠ [UNVERIFIED] U10: AZDOR also posts 2026 editions of the booklet "
               "and of Form 120/PTE-W, and the Form 165 instructions point electing entities to THOSE "
               "for 2026 estimates. Confirm which vintage the app should surface. ⚠ Note also the "
               "OPPOSITE timeliness rule for the MSP election on the same return.")},
    {"diagnostic_id": "D_AZ_MSP_FIVE_YEAR_LOCK", "severity": "warning",
     "title": "Schedule MSP is a FIVE-YEAR IRREVOCABLE election requiring a timely ORIGINAL return",
     "condition": "Schedule MSP is included, or an existing MSP election cycle is running",
     "message": ("A.R.S. 43-1147(C): 'The election must be made on the taxpayer's TIMELY FILED ORIGINAL "
                 "income tax return. The election is: (a) Effective retroactively for the full taxable "
                 "year ... (b) BINDING ON THE TAXPAYER FOR AT LEAST FIVE CONSECUTIVE TAXABLE YEARS, "
                 "REGARDLESS OF WHETHER THE TAXPAYER NO LONGER MEETS THE PERCENTAGE THRESHOLD during "
                 "that time period.' It terminates only on acquisition or merger (no permission "
                 "needed) or with the department's permission. Part A qualification is computed ONLY "
                 "IN YEAR ONE. THE CYCLE YEAR MUST PERSIST ACROSS TAX YEARS IN THE APP."),
     "notes": ("⚠ THE ONLY STATEFUL MULTI-YEAR ATTRIBUTE ON THE ARIZONA PTE RETURNS. ⚠ TWO ELECTIONS "
               "ON ONE RETURN WITH OPPOSITE TIMELINESS RULES (W21): the MSP election REQUIRES a timely "
               "filed original return; the PTE election has NO timeliness condition at all since "
               "S.B. 1274.")},
    {"diagnostic_id": "D_AZ_U8_OWNER_PAGE_REFS", "severity": "warning",
     "title": "Bind owner routing on the ITEM LETTER, not the page number",
     "condition": "an owner-schedule destination is resolved to a Form 140PY or Form 140NR page",
     "message": ("The Form 140PY / 140NR page references across the four Arizona owner schedules are "
                 "MUTUALLY INCONSISTENT: 165 Schedule K-1 lines 12-15 say 'Form 140PY, PAGE 5, line "
                 "N'; 165 Schedule K-1(NR) lines 24-27 say 'Form 140PY, PAGE 3, line N'; 120S Schedule "
                 "K-1(NR) Part 6 says PAGE 5 line N while Part 5 ON THE SAME SCHEDULE says Form 140NR "
                 "PAGE 6 line L against Part 6's Form 140NR PAGE 5 line L. THE ITEM LETTERS (P / N / L "
                 "/ V / Q) ARE INTERNALLY CONSISTENT; THE PAGE NUMBERS ARE NOT. Bind on the letter."),
     "notes": ("[UNVERIFIED] U8. SBI line numbers also vary by form (140NR-SBI line 24 vs 140PY-SBI "
               "line 25; 140-SBI line 47 vs 140PY-SBI line 44). Settled by the TY2025 Form 140PY and "
               "Form 140NR faces (individual wave).")},
    {"diagnostic_id": "D_AZ_U10_ES_VINTAGE", "severity": "warning",
     "title": "Which vintage of Form 120/PTE-W and Booklet 120/165ES should the app surface?",
     "condition": "next-year estimated-tax figures are prepared",
     "message": ("The file AZDOR posts under its 2025 row for Form 120/PTE-W is stamped ADOR 10551 "
                 "(24) with /ModDate 2024-11-20, and the ES booklet is headed '2024 CORPORATE INCOME "
                 "TAX HIGHLIGHTS' with /ModDate 2024-11-19. AZDOR SEPARATELY POSTS 2026 EDITIONS OF "
                 "BOTH, and the Form 165 instructions direct electing entities to 'Arizona Form "
                 "120/PTE-W to compute the estimated payments for 2026'. A TY2025 return is prepared "
                 "in 2026 and drives 2026 estimates, so the 2026 edition is probably the right one to "
                 "surface — CONFIRM BY DIFFING THE 2026 EDITIONS."),
     "notes": ("[UNVERIFIED] U10. The 2026 editions were never downloaded. ⚠ Independent of vintage: "
               "the 2025-row ES booklet contains a REPEALED statement of law (see "
               "D_AZ_ES_BOOKLET_REPEALED_LAW). ⚠ Form 120/PTE-W line 9 carries TWO RATES IN ONE LABEL "
               "— 4.9% for corporations with the parenthetical '(PTE's use 2.5% as tax rate.)'.")},
    {"diagnostic_id": "D_AZ_U11_220PTE_LINE5", "severity": "warning",
     "title": "Form 220/PTE line 5 cites 'Form 165, line 23', which is NOT a tax line",
     "condition": "Form 220/PTE Part B line 5 is populated for a partnership",
     "message": ("Verbatim: 'Enter the 2025 Arizona tax liability from Form 99T, line 11 less line 12; "
                 "or Form 120, line 21 less line 22; or Form 120A, line 13 less line 14; or Form 120S, "
                 "line 19 less line 20, OR FORM 165, LINE 23.' Form 165 line 23 is 'Multiply the "
                 "amount on line 21 by the decimal on line 22' — AN INTERMEDIATE APPORTIONED "
                 "NONRESIDENT BASE, NOT A TAX. Every other entry in that sentence points at a NET TAX "
                 "figure. THE INTENDED REFERENCE IS FORM 165 LINE 25, 'the total amount of tax owed by "
                 "the Partnership'. Delvio computes from line 25."),
     "notes": "[UNVERIFIED] U11 / W20, printed defect AZ-D3. Settled by an AZDOR correction or the "
              "TY2026 Form 220/PTE."},
    {"diagnostic_id": "D_AZ_U20_220PTE_LINE37", "severity": "warning",
     "title": "Form 220/PTE line 37's routing list is wrong for the 120S and omits Form 165 entirely",
     "condition": "the Form 220/PTE Part C line 37 penalty is routed back to a parent return",
     "message": ("Verbatim: 'Enter the total here and on Form 99T, line 22; or Form 120, line 29; or "
                 "Form 120A, line 21; OR FORM 120S, LINE 25.' But Form 120S line 25 is 'Overpayments "
                 "of tax from original return or later adjustments' — THE ESTIMATED-PENALTY LINE IS "
                 "31 — and FORM 165 IS ABSENT FROM THE LIST ALTOGETHER, though Form 165 line 35 "
                 "imports the figure per the Form 165 instructions. BUILD TO THE 165 / 120S "
                 "INSTRUCTIONS, WHICH ARE RIGHT — NOT TO THE 220/PTE FACE."),
     "notes": ("[UNVERIFIED] U20 / W25 — a FOURTH printed cross-reference defect in one package, "
               "found by the verification pass. Same class as U11. Note this is NOT an exception to "
               "'the face governs': that rule resolves a FACE-vs-INSTRUCTION conflict on the SAME "
               "form, whereas here a SUPPORTING form's routing list is wrong about a PARENT form, and "
               "the parent's own instructions govern.")},
    {"diagnostic_id": "D_AZ_U16_LOI_TY2026", "severity": "info",
     "title": "The TY2026 Arizona MeF Letter of Intent is unpublished; its due date is an INFERENCE",
     "condition": "Arizona e-file registration is planned",
     "message": ("The TY2025 LOI was due NOVEMBER 28, 2025 (stated twice on its cover) and that window "
                 "is CLOSED. As of the last check the AZDOR LOI landing page still read 'For tax year "
                 "2025, please download the Letter of Intent and the Forms Supported Spreadsheet' and "
                 "linked ONLY the TY2025 PDF. THE ~END-OF-NOVEMBER-2026 EXPECTATION IS A PATTERN "
                 "INFERENCE, NOT A PUBLISHED DATE. AZDOR posted the TY2025 LOI on 2025-08-27, three "
                 "months ahead, so re-check the page from September 2026."),
     "notes": ("[UNVERIFIED] U16. Feeds EFILE_GATES.md, not a computation. ⚠ 'Partnership return' and "
               "'S-corporation return' are SEPARATE REGISTRATIONS and the PTE wave needs BOTH boxes; "
               "the '(*) amended-later' concession appears only on the individual and corporation "
               "rows. ⚠ The COR Credit Forms tab must also be completed — an incomplete spreadsheet "
               "can trigger denial or revocation under the LOI's own consequences clause. ⚠ DELVIO IS "
               "A NEW PROVIDER, SO IRS MeF ATS ACCEPTANCE IS A BLOCKING PREDECESSOR.")},
    {"diagnostic_id": "D_AZ_U17_RULINGS_UNPULLED", "severity": "info",
     "title": "Twelve referenced AZDOR rulings and procedures were never pulled",
     "condition": "a line whose instruction cites an AZDOR ruling or procedure is computed",
     "message": ("Named on the Arizona forms and instructions but not read: ITP 16-2 (Arizona bonus "
                 "depreciation — see D_AZ_RD_B1_TY2013_TIER), ITR 06-1 (U.S. government obligations, "
                 "Form 165 line B3), ITP 12-1 (agricultural crop contributions, line B4), ITR 16-2 "
                 "(composite returns), CTR 09-1 (penalties under extension), CTR 01-2 (computer "
                 "software in the property factor), CTR 02-2 (installment sale gain apportionment), "
                 "CTR 07-1 (short-term investments in the sales factor), PTR 97-1 / CTR 97-1 "
                 "(check-the-box), PTR 97-2 / CTR 97-2 (LLCs), Pub 720 (disaster relief) and Pub 712 "
                 "(small business income). Most affect edge cases."),
     "notes": "[UNVERIFIED] U17. ⚠ ITP 16-2 IS THE ONLY ONE THAT GATES A MAINSTREAM LINE."},
    {"diagnostic_id": "D_AZ_U21_43_1011_CITE", "severity": "info",
     "title": "The A.R.S. § 43-1011(A)(9) pinpoint is UNSUPPORTED — the rate is not",
     "condition": "the PTE rate's statutory provenance is cited",
     "message": ("azleg.gov/ars/43/01011.01.htm returns a 404 'Page not found' — THE ONLY 404 AMONG "
                 "THE FOURTEEN A.R.S. PAGES CACHED FOR THIS BRIEF — and azleg.gov/ars/43/01011.htm "
                 "serves a SUPERSEDED CONDITIONAL VERSION stamped (L21, Ch. 411, sec. 4) whose "
                 "subsection A stops at paragraph 4 with a 4.50% top bracket while its own subsection "
                 "E refers to paragraphs 6-9 that are ABSENT from the served text. NO FLAT 2.5% AND NO "
                 "PARAGRAPH (9) CAN BE READ OFF EITHER PAGE. ⚠ THE 2.5% RATE ITSELF IS SAFE — it is "
                 "proved five ways from AZDOR's own TY2025 documents (Form 165 face lines 20 and 24, "
                 "Form 120S face lines 47 and 51, and Pub 713). ONLY THE PROVENANCE CHANGED. THIS "
                 "SPEC CITES THE FORM FACES AND PUB 713, NOT § 43-1011(A)(9)."),
     "notes": ("[UNVERIFIED] U21, added by the verification pass and carried from the conformity brief "
               "rather than independently verified there. ⚠ CONSEQUENCE FOR FORM 165PA: "
               "§ 43-1414(B)(1)(b)'s 'highest tax rate imposed on individuals under section 43-1011' "
               "CANNOT be resolved directly against azleg, so the 2.5% leg of the U14 conflict is "
               "reached BY SYLLOGISM from § 43-1014(A) plus the printed AZDOR rate. Settled by pulling "
               "§ 43-1011 from a source that serves the operative version — Westlaw/Lexis, the printed "
               "A.R.S., or enrolled Laws 2021 Ch. 412 (S.B. 1828).")},
    {"diagnostic_id": "D_AZ_EFILE_DERIVATIVE", "severity": "warning",
     "title": "Arizona e-file eligibility is DERIVATIVE of the federal filing posture",
     "condition": "Arizona e-file eligibility is determined",
     "message": ("A.R.S. 43-323(F) makes e-filing MANDATORY and both faces print it above the "
                 "declaration. FOUR OF THE SEVEN PRINTED EXEMPTIONS KEY OFF FEDERAL STATUS: the entity "
                 "cannot e-file its federal return; it was granted a federal waiver; it has a federal "
                 "exemption; or it was directed to file on paper by the IRS. THE APP CANNOT DECIDE "
                 "ARIZONA E-FILE ELIGIBILITY WITHOUT KNOWING THE FEDERAL POSTURE — a Gate-2 INGEST "
                 "dependency for delvio-tax, not an RS spec item."),
     "notes": "Rejections: azefile@azdor.gov, quoting the Arizona submission ID and the form type. "
              "Waivers are annual and renewable once, on Form 292."},
    {"diagnostic_id": "D_AZ_PART_YEAR_TWO_SCHEDULES", "severity": "info",
     "title": "A part-year owner receives TWO owner schedules, not one",
     "condition": "any owner has a residency code of 'P'",
     "message": ("Pub 713 footnote 2: 'For part-year shareholders, complete one Schedule K-1 (as "
                 "needed) to report that shareholder's distribution for the time the shareholder lived "
                 "in Arizona AND complete Schedule K-1(NR) to report that shareholder's distribution "
                 "for the time the shareholder did NOT live in Arizona.' A PER-OWNER DOCUMENT "
                 "MULTIPLIER THE APP MUST HANDLE. The entity-level split is Form 165 lines 16A/16B and "
                 "Form 120S lines 43A/43B, BY ACTUAL RESIDENCY PERIOD rather than by day count."),
     "notes": "Routing is by RESIDENCY AND ENTITY TYPE, not by form: all corporate partners and all "
              "partnership partners must use Schedule K-1(NR) regardless of residency."},

    # ---------------------------- RED-DEFERS --------------------------------
    {"diagnostic_id": "D_AZ_RD_165PA_FAMILY", "severity": "error",
     "title": "RED-DEFER: the whole Form 165PA family — its printed rate contradicts the statute",
     "condition": "Form 165 question J is 'Yes', or a federal imputed underpayment assessment exists",
     "message": ("Arizona Form 165PA (and Form 165PA Schedule K-1, Schedule K-1(NR) and Form 165PA-X) "
                 "MUST BE PREPARED MANUALLY. Face line 13 and the instructions BOTH print a 4.5% tax "
                 "rate, while A.R.S. 43-1414(B)(1)(b) imposes the tax 'at the highest tax rate imposed "
                 "on individuals under section 43-1011' = 2.5% for TY2025. BUILDING TO THE FACE "
                 "KNOWINGLY OVER-TAXES BY 80%; BUILDING TO THE STATUTE CONTRADICTS A PRINTED FINAL "
                 "FORM. Campaign D-12 A2 ruled: DEFER RATHER THAN CHOOSE. The return is due 90 days "
                 "after the IRS final determination."),
     "notes": ("[UNVERIFIED] U14 (the rate) and U13 (the three companion schedules were never "
               "downloaded). BOTH NEGATIVES ARE VERIFIED: S.B. 1274 = Laws 2025 Ch. 182 Sec. 7 amended "
               "43-1414 SUBSECTION (A) ONLY — the capitalised new text appears only there and "
               "subsection (B) is entirely lowercase — and H.B. 4168 does not touch 43-1414 at all "
               "('43-1414' occurs ZERO times in the chaptered PDF). ⚠ DO NOT CONFLATE THE TWO 4.5%s: "
               "the 165PA LATE-FILING PENALTY is also 4.5% and IS CORRECT. ⚠ ONE 165PA OUTPUT STILL "
               "REACHES FORM 165 EVEN WHILE 165PA IS DEFERRED — a RECEIVED 165PA Schedule K-1(NR) with "
               "a positive line 3 forces an AMENDED Form 165. Settled by an AZDOR correction or a "
               "direct answer from the Corporate Income Tax section.")},
    {"diagnostic_id": "D_AZ_RD_1021_15_ENTITY_ADDBACK", "severity": "error",
     "title": "RED-DEFER: the § 43-1021(15) ENTITY-LEVEL PTE add-back has no line on either form",
     "condition": "a cash-basis electing entity paid Arizona PTE tax during the taxable year",
     "message": ("A.R.S. 43-1021(15) directs the PTE-tax add-back into TWO places — 'the partner's or "
                 "shareholder's Arizona gross income AND THE PARTNERSHIP'S OR S CORPORATION'S ARIZONA "
                 "TAXABLE INCOME'. THE OWNER HALF IS FULLY IMPLEMENTED on all four K-1s. THE ENTITY "
                 "HALF HAS NO LINE: Form 165's Schedule A has four rows, its page-6 A4 worksheet is a "
                 "CLOSED LIST OF THREE ITEMS with no free-text 'other' row anywhere on page 6, line 9 "
                 "is 43-1412 paragraphs 1-16 (no PTE add-back), and Form 120S has no additions "
                 "schedule at all. CAMPAIGN RULING D-12 A3: BUILD TO THE FORM, OWNER LEVEL ONLY. THE "
                 "ENTITY-LEVEL EFFECT IS NOT COMPUTED."),
     "notes": ("[UNVERIFIED] U5. ⚠ THE CASH-BASIS CIRCULARITY IS REAL AND IS RECORDED RATHER THAN "
               "FIXED: the PTE tax is deductible federally in the year PAID and electing entities are "
               "almost universally cash-basis, so Form 165 line 1 / Form 120S line 1 is ALREADY NET of "
               "the Arizona PTE tax paid during the year and the PTE base is UNDERSTATED BY THE PTE "
               "TAX ITSELF. That is exactly what the statute's second sentence exists to close. AZDOR "
               "answered a practitioner asking this precise question 'owner level only', without "
               "addressing the entity clause, and closed with the confused words 'reports this amount "
               "on his/her individual FEDERAL income tax return'. Same shape as D-10 ruling 2 "
               "(Missouri) and D-11 A1 (Colorado 174A): WHERE THE FORM CANNOT EXPRESS A POSITION, THE "
               "FORM GOVERNS. Settled by an AZDOR ruling or a revised A4 worksheet.")},
    {"diagnostic_id": "D_AZ_RD_CORP_PARTNER_RECOMPUTE", "severity": "error",
     "title": "RED-DEFER: no corporate-basis recomputation of a partnership-level Arizona adjustment",
     "condition": "a corporate partner receives a Form 165 Schedule K-1(NR) line 15 amount",
     "message": ("A.R.S. 43-1122(20) requires a CORPORATION to compute Arizona depreciation as if the "
                 "IRC 168(k)(7) election OUT of bonus had been made, while Form 165 computes its "
                 "adjustment on the INDIVIDUAL full-168(k) basis and routes it to the corporate "
                 "partner's Form 120/120A Schedule A line A8 / Schedule B line B10 WITH NO "
                 "RE-COMPUTATION INSTRUCTION ANYWHERE. CAMPAIGN RULING D-12 A4: DELVIO COMPUTES NO "
                 "CORPORATE-BASIS RECOMPUTATION — Arizona publishes none and no form line carries one. "
                 "THE CORPORATE PARTNER'S OWN ARIZONA POSITION MUST BE REVIEWED MANUALLY on its Form "
                 "120 or 120A."),
     "notes": ("[UNVERIFIED] U2 / W9 STAYS OPEN AS A FACT. Settled by reading the TY2025 Form 120 "
               "instructions for Schedule A line A8 and Schedule B line B10, which may carry the "
               "missing instruction — they were never pulled and are C-CORP-WAVE scope. If they do "
               "not, this remains an interpretive gap Arizona has never addressed. It does NOT block "
               "the PTE wave: Form 165's own computation is unambiguous.")},
    {"diagnostic_id": "D_AZ_RD_PTEW_ANNUALIZED", "severity": "error",
     "title": "RED-DEFER: Form 120/PTE-W Schedule A Part 1, the annualized income installment method",
     "condition": "the entity elects the annualized income installment method for its estimates",
     "message": ("The annualized income installment method IS available to partnerships and S "
                 "corporations making the PTE election, but it must be COMPUTED MANUALLY for v1: it is "
                 "a four-column annualization with a DUAL RATE ON ONE LINE — Form 120/PTE-W line 9 "
                 "reads 'Multiply the amount in each column on line 8 by 4.9%: Enter the result. "
                 "(PTE's use 2.5% as tax rate.)' — plus applicable percentages of 22.5% / 45% / 67.5% "
                 "/ 90%. ⚠ THE ADJUSTED SEASONAL INSTALLMENT METHOD (Part 2) IS NOT AVAILABLE TO "
                 "ELECTING PTEs AT ALL, stated on the faces of both this form and Form 220/PTE."),
     "notes": "A single-rate transcription of line 9 is wrong for one of the two populations it "
              "serves. See also D_AZ_U10_ES_VINTAGE on which edition to surface."},
    {"diagnostic_id": "D_AZ_RD_220PTE_SCHEDULE_A", "severity": "error",
     "title": "RED-DEFER: Form 220/PTE Schedule A (annualized / adjusted seasonal)",
     "condition": "Form 220/PTE Part A box 1 or box 2 is checked",
     "message": ("Form 220/PTE Schedule A must be computed MANUALLY for v1. Part A box 1 (annualized "
                 "income installment method) IS available to electing PTEs; box 2 (adjusted seasonal "
                 "installment method) is NOT. ⚠ AND IN MOST CASES THE FORM NEED NOT BE FILED AT ALL: "
                 "'In most cases, the taxpayer DOES NOT HAVE TO FILE Form 220/PTE. The department will "
                 "compute any penalty due and bill the taxpayer.' DO NOT AUTO-FILE IT."),
     "notes": ("If the form is used only to compute the penalty, enter the amount on the return's "
               "estimated-penalty line, DO NOT check the box, and DO NOT include Form 220/PTE with the "
               "return. Part A box 3 is Forms 120/120A only; box 4 is a Form 120S-only alternative "
               "computation for S corporations subject to federal-level tax.")},
    {"diagnostic_id": "D_AZ_RD_COMPOSITE_140NR", "severity": "error",
     "title": "RED-DEFER: the composite return on Arizona Form 140NR",
     "condition": "Form 165 question L or Form 120S question F is 'Yes'",
     "message": ("A composite return for OPTED-OUT nonresident individual owners must be prepared "
                 "manually on Arizona Form 140NR — an INDIVIDUAL-module form. Requirements: a MINIMUM "
                 "OF TEN participating members, and every participant must have OPTED OUT of the PTE "
                 "election (AZDOR ruling ITR 16-2). Extension on FORM 204 (not Form 120/165EXT); "
                 "voluntary estimates on FORM 140ES (not Form 120/165ES); and composite payments "
                 "CANNOT be converted to PTE estimated payments."),
     "notes": "For the PTE wave the only deliverables are the page-1 checkbox and those two "
              "validations."},
    {"diagnostic_id": "D_AZ_RD_ALT_APPORTIONMENT", "severity": "error",
     "title": "RED-DEFER: alternative apportionment relief under A.R.S. § 43-1148",
     "condition": "the standard apportionment formula does not fairly represent Arizona business activity",
     "message": ("Relief under A.R.S. 43-1148 must be requested manually and carries a HARD PROCEDURAL "
                 "DEADLINE: 'Taxpayers seeking such relief should submit a letter to the Corporate "
                 "Income Tax Audit Section SIXTY DAYS PRIOR TO THE FILING OF THE RETURN.' Delvio does "
                 "not compute an alternative formula."),
     "notes": "Sixty days before filing, not before the due date — the clock runs off the intended "
              "filing date."},
    {"diagnostic_id": "D_AZ_RD_OPTICAL_MEDIA_K1", "severity": "error",
     "title": "RED-DEFER: optical-media K-1 submission above Arizona's electronic ceiling",
     "condition": "the return would carry more than approximately 66,054 Schedules K-1 / K-1(NR)",
     "message": ("'Due to system constraints, the department's computer system can handle an "
                 "electronically filed return up to 246 MB in size. This accommodates a partnership's "
                 "return and approximately 66,054 Arizona Form 165 Schedule(s) K-1 and/or K-1(NR) ... "
                 "Partnerships submitting Arizona Form 165 with more than 66,054 Schedules K-1 and/or "
                 "K-1(NR) MUST FILE A PAPER RETURN. The department requests those partnerships submit "
                 "their Schedules K-1 and/or K-1(NR) BY CD, DVD, OR FLASH DRIVE' as a Microsoft Excel "
                 "spreadsheet, labelled with the partnership's name, EIN, taxable year and form, with "
                 "any password e-mailed separately to MediaLibrarian@azdor.gov."),
     "notes": "⚠⚠ THE OPTICAL-MEDIA PATH EXISTS ONLY ON THE PARTNERSHIP SIDE. The Form 120S book says "
              "'S Corporations filing a paper return must submit Schedule(s) K-1 and K-1(NR) to the "
              "department BY PAPER' and offers no alternative. DO NOT PORT IT."},
    {"diagnostic_id": "D_AZ_RD_SHORT_PERIOD_PAPER", "severity": "error",
     "title": "RED-DEFER: a 2026 short-period return on the 2025 form MUST be paper-filed",
     "condition": "a 2026 short-period return is being prepared on the TY2025 Arizona form",
     "message": ("Both instruction books carry the same exemption verbatim: a taxpayer 'submitting the "
                 "2025 Arizona Form 165 for a 2026 SHORT PERIOD RETURN, SUBMIT A PAPER FILED RETURN. "
                 "DO NOT SUBMIT THIS SHORT PERIOD RETURN ELECTRONICALLY.' THIS IS A HARD E-FILE BLOCK "
                 "AND MUST NOT PRODUCE A SILENT E-FILE ATTEMPT."),
     "notes": "A short-period return is otherwise due the 15th day of the 3rd month after the short "
              "period ends."},
    {"diagnostic_id": "D_AZ_RD_FORM_292_WAIVER", "severity": "error",
     "title": "RED-DEFER: the Arizona e-file / EFT waiver on Form 292",
     "condition": "the entity needs an Arizona electronic filing or payment waiver",
     "message": ("An Arizona e-file or EFT waiver must be requested manually on ARIZONA FORM 292, "
                 "'Electronic Filing and Payment Waiver Application'. Grounds, verbatim: the entity "
                 "'has no computer'; 'has no internet access'; or 'any other circumstance considered "
                 "to be worthy by the director'. WAIVERS ARE GRANTED ANNUALLY, EXPIRE AT THE END OF "
                 "THE REQUESTED TAX YEAR, AND MUST BE RENEWED EACH CALENDAR YEAR (renewable for one "
                 "subsequent year). ⚠ A waiver is NOT required if the return cannot be e-filed for "
                 "reasons beyond the taxpayer's control (A.R.S. 43-323(G))."),
     "notes": "[UNVERIFIED] U15 — Form 292 itself was never downloaded. Affects a delvio-tax workflow "
              "prompt, not an RS computation."},
    {"diagnostic_id": "D_AZ_RD_MARIJUANA_99M", "severity": "error",
     "title": "RED-DEFER: an ADHS-licensed entity may also owe Arizona Form 99M",
     "condition": "any marijuana licence box is checked (Form 165 question M / Form 120S question G)",
     "message": ("A Dual Licensee that did NOT elect to operate on a for-profit basis, and an NMMD-only "
                 "registrant, must file ARIZONA FORM 99M for the NMMD portion of operations ALONGSIDE "
                 "the entity return, and must still complete and provide Schedules K-1 and K-1(NR) — "
                 "'the partners are not exempt from Arizona income tax'. ⚠ On the S-corp side, an "
                 "NMMD-only S corporation subject to federal corporate-level tax 'is NOT subject to "
                 "Arizona corporate income tax. Do not complete lines 2 through 12.' Form 99M must be "
                 "prepared manually."),
     "notes": ("Schedule DFE (Disallowed Federal Expenses) IS in scope as an INPUT: on the partnership "
               "side it feeds Form 165 page-6 line B5-G at the ENTITY level; on the S-corp side the "
               "same figure goes to the SHAREHOLDER via Schedule K-1 Part 4 / Schedule K-1(NR) Part 5. "
               "Same input, different plumbing.")},
]


# ═══════════════════════════════════════════════════════════════════════════
# THE TWO SPECS
# ═══════════════════════════════════════════════════════════════════════════
FORMS: list[dict] = [
    {
        "identity": {
            "form_number": FORM_CODE_165,
            "form_title": "Arizona Partnership Income Tax Return (Arizona Form 165)",
            "entity_types": ["1065"],
            "notes": (
                "TY2025. THE FORM THAT CARRIES ARIZONA'S WHOLE MODIFICATION APPARATUS. Part 1 (lines "
                "1-7) runs federal ordinary and rental income through Schedule A additions A1-A4 and "
                "Schedule B subtractions B1-B5 to line 5 'Partnership income adjusted to Arizona "
                "basis' and line 6 'Net adjustment ... from federal to Arizona basis'; Part 2 (lines "
                "8-40) computes the ELECTIVE PTE TAX at 2.5% pre-printed on the face, on a base of "
                "line 5 PLUS line 9 (A.R.S. 43-1014(B)(1)(a)(ii)). ⚠⚠ LINE 5 AND LINE 6 ARE DIFFERENT "
                "NUMBERS GOING TO DIFFERENT PLACES — line 5 to the PTE base and Schedule D column (h), "
                "LINE 6 ALONE to the owners — and crossing them is the most likely single "
                "transcription error on this form. ⚠ LINE B1 IS A **FIVE**-VINTAGE-TIER DEPRECIATION "
                "RECOMPUTATION on the INDIVIDUAL full-168(k) basis (43-1022(17)(e)), keyed on PLACED "
                "IN SERVICE and stated four times, so no date-keying ruling is needed here; its TY2013 "
                "tier is DIRECT-ENTRY pending ITP 16-2 (U1), the only unpulled document gating a "
                "mainstream line. ⚠ LINE 9 IS ONE UNDIFFERENTIATED BOX FOR SIXTEEN STATUTORY "
                "CATEGORIES including IRC 179, whose Arizona limit is a campaign RULING (D-10), not a "
                "published figure. ⚠ THE PAGE-6 WORKSHEETS ARE CLOSED ENUMERATIONS WITH NO FREE-TEXT "
                "ROW, which is why the 43-1021(15) entity-level PTE add-back is inexpressible and was "
                "ruled OWNER LEVEL ONLY (D-12 A3). ⚠ Question D is INVERTED relative to Form 120S "
                "question B. ⚠ Special allocations ARE honoured here. ⚠ Face ADOR 10343 (25), "
                "/ModDate 2025-11-13, read POSITIONALLY; 48 line numbers sampled across all fifteen "
                "Arizona forms with a 0.0% error rate. Two printed defects on this form: the stale "
                "2025 at line 39, and Form 220/PTE's citation of line 23 as a tax line."
            ),
        },
        "facts": AZ165_FACTS, "rules": AZ165_RULES, "rule_links": AZ165_RULE_LINKS,
        "lines": AZ165_LINES, "diagnostics": AZ165_DIAGNOSTICS + AZ_SHARED_DIAGNOSTICS,
        "scenarios": AZ165_SCENARIOS,
    },
    {
        "identity": {
            "form_number": FORM_CODE_120S,
            "form_title": "Arizona S Corporation Income Tax Return (Arizona Form 120S)",
            "entity_types": ["1120S"],
            "notes": (
                "TY2025. ⚠⚠ THE FORM WITH **NO** ARIZONA MODIFICATION APPARATUS AT ALL — and that is a "
                "VERIFIED NEGATIVE, not an omission. Part 1 (lines 1-36) computes a corporate-level "
                "tax ONLY when the S corporation has federal-level taxable income (excess net passive "
                "income or capital/built-in gains), at the GREATER OF $50 OR 4.9% — A CONDITIONAL "
                "MINIMUM, both halves of the sentence operative. Part 2 (lines 37-52) computes the "
                "elective PTE tax at 2.5% pre-printed on the face, on a base of LINE 37 = LINE 1, "
                "UNADJUSTED (A.R.S. 43-1014(B)(1)(b), via 43-1126(B), a REPORTING provision). THE "
                "EVIDENCE FOR THE NEGATIVE IS FOURFOLD: the modification statutes 43-1021 / 43-1022 / "
                "43-1121 / 43-1122 are cited ZERO times in the 28-page book while every Title 43 "
                "section it does cite is an apportionment provision; the string 'Arizona basis' occurs "
                "ZERO times; the face has no additions or subtractions schedule (its lettered Schedule "
                "A is the APPORTIONMENT FORMULA); and the corporate-level chain is unadjusted too. "
                "70 'addition'/'subtract*' hits were read in context and disproven as an alarm. "
                "⚠ CREDIT ORDERING IS STRUCTURAL: nonrefundable credits apply at line 15 against line "
                "14 and the PTE tax arrives at line 18, SO THEY CANNOT REDUCE IT — Pub 713 says both "
                "'No' and 'nothing precludes' and the FORM GOVERNS. ⚠ Question B is INVERTED relative "
                "to Form 165 question D. ⚠ Special allocations are FORBIDDEN. ⚠ Schedule B column (h) "
                "draws LINE 1 where Form 165's draws LINE 5. ⚠ Schedule D has FOUR payment columns "
                "where Form 165's Schedule F has three. ⚠ The Schedule K-1(NR) line map is OFF BY ONE "
                "from the partnership schedule's. ⚠ No de-minimis filing carve-out and no "
                "optical-media K-1 path — do not port either from Form 165. Face ADOR 10337 (25), "
                "/ModDate 2025-11-12; the instruction book was REGENERATED 2026-08-12, after H.B. "
                "4168, and still cites no Arizona modification statute."
            ),
        },
        "facts": AZ120S_FACTS, "rules": AZ120S_RULES, "rule_links": AZ120S_RULE_LINKS,
        "lines": AZ120S_LINES, "diagnostics": AZ120S_DIAGNOSTICS + AZ_SHARED_DIAGNOSTICS,
        "scenarios": AZ120S_SCENARIOS,
    },
]


# ═══════════════════════════════════════════════════════════════════════════
# FLOW ASSERTIONS — exported as JSON and tested in delvio-tax.
# ⚠ assertion_id is CharField(20) and UNIQUE ACROSS THE WHOLE DATABASE.
# ═══════════════════════════════════════════════════════════════════════════
FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-AZ120S-NOMODS", "status": "draft", "sort_order": 1,
     "title": "Form 120S applies NO Arizona modifications — line 37 == line 1",
     "assertion_type": "table_invariant", "entity_types": ["1120S"],
     "description": ("Arizona Form 120S has no additions schedule, no subtractions schedule, no "
                     "depreciation line and no 'Arizona basis' line, and its PTE base is federal Form "
                     "1120-S Schedule K total distributive income unadjusted. VERIFIED NEGATIVE: the "
                     "modification statutes 43-1021 / 43-1022 / 43-1121 / 43-1122 are cited ZERO times "
                     "in the 28-page TY2025 instruction book; 'Arizona basis' occurs ZERO times; every "
                     "Title 43 section the book cites is an apportionment provision; and the "
                     "corporate-level chain (lines 2-4, 11, 12) is unadjusted too."),
     "definition": {"rule": "R-AZ120S-NO-MODS + R-AZ120S-PTE-BASE",
                    "check": ("AZ_120S_HAS_MODIFICATION_APPARATUS is False AND line 37 == line 1 AND "
                              "az_120s_modification() raises ArizonaFormGovernsError AND "
                              "az_120s_depreciation_adjustment() raises")},
     "bug_reference": "Porting the Form 165 Schedule A/B stack onto Form 120S computes lines that do "
                      "not exist on the form"},
    {"assertion_id": "FA-AZ165-L6-K1", "status": "draft", "sort_order": 2,
     "title": "Form 165 line 6 — not line 5 — is what reaches the owners",
     "assertion_type": "flow_assertion", "entity_types": ["1065"],
     "description": ("Line 5 ('Partnership income adjusted to Arizona basis') feeds the PTE base at "
                     "line 8 and Schedule D column (h). LINE 6 ('Net adjustment of partnership income "
                     "from federal to Arizona basis') is the ONLY number that leaves Part 1 for the "
                     "owners: Schedule K-1 line 1 imports it, and Schedule K-1(NR) line 15 imports it. "
                     "The per-partner share is K-1 line 3 = line 1 x line 2."),
     "definition": {"rule": "R-AZ165-L6",
                    "check": ("AZ_165_SCHK1.line_1 == AZ_165.line_6 AND AZ_165_SCHK1NR.line_15 == "
                              "AZ_165.line_6 AND sum(K-1 line 3 across partners) == AZ_165.line_6")},
     "bug_reference": "Crossing lines 5 and 6 is the most likely single transcription error on Form 165"},
    {"assertion_id": "FA-AZ165-XFOOT", "status": "draft", "sort_order": 3,
     "title": "Form 165 Part 2 cross-foot: 12 + 14 + 16 + 18 == 10, and 16A + 16B == 16",
     "assertion_type": "reconciliation", "entity_types": ["1065"],
     "description": ("Both obligations are printed ON THE FACE, not merely in the instructions. Every "
                     "partner's distributive share must land in exactly one of four buckets — "
                     "resident, nonresident, part-year, opted-out/ineligible — and the part-year "
                     "bucket splits by ACTUAL ARIZONA RESIDENCY PERIOD rather than by day count."),
     "definition": {"rule": "R-AZ165-ALLOC",
                    "check": "line_12 + line_14 + line_16 + line_18 == line_10 AND line_16A + line_16B == line_16"},
     "bug_reference": "A shortfall means a partner is missing from Schedule E; an excess means one is "
                      "double-counted"},
    {"assertion_id": "FA-AZ165-SCHE1", "status": "draft", "sort_order": 4,
     "title": "Form 165 Schedule E must cross-foot to 1.000000, with look-through owners in E1-E3",
     "assertion_type": "reconciliation", "entity_types": ["1065"],
     "description": ("E8 = E6 + E7 and column (c) 'should equal 1.000000' — printed on the face. "
                     "⚠ LOOK-THROUGH PARTNERS (grantor trusts, SMLLCs disregarded to an individual) "
                     "that did NOT opt out are counted in E1-E3, THE INDIVIDUAL ROWS, not in the "
                     "estate/trust rows E4-E5. Ineligible entity partners land in E7."),
     "definition": {"rule": "R-AZ165-SCHE-XFOOT",
                    "check": "E8(c) == 1.000000 AND sum(Schedule D column (g)) == 1.000000 AND "
                             "look-through owners appear only in E1-E3"},
     "bug_reference": "Placing a grantor trust in E4 instead of E1 is a common cause of a cross-foot "
                      "failure"},
    {"assertion_id": "FA-AZ120S-XFOOT", "status": "draft", "sort_order": 5,
     "title": "Form 120S Part 2 cross-foot: 39 + 41 + 43 + 45 == 37, and C8(c) == 1.000000",
     "assertion_type": "reconciliation", "entity_types": ["1120S"],
     "description": ("Printed on the face: 'The total of lines 39, 41, 43, and 45 must equal the "
                     "amount on line 37', 'the total of lines 43A and 43B must equal the amount "
                     "reported on line 43', and '(Column (c) should total 1.000000)'. Look-through "
                     "shareholders that did not opt out belong in C1-C3."),
     "definition": {"rule": "R-AZ120S-ALLOC + R-AZ120S-SCHC-XFOOT",
                    "check": ("line_39 + line_41 + line_43 + line_45 == line_37 AND line_43A + "
                              "line_43B == line_43 AND C8(c) == 1.000000 AND sum(Schedule B column "
                              "(g)) == 1.000000")},
     "bug_reference": ""},
    {"assertion_id": "FA-AZ120S-L18-52", "status": "draft", "sort_order": 6,
     "title": "Form 120S line 18 == line 52, and nonrefundable credits never reach it",
     "assertion_type": "flow_assertion", "entity_types": ["1120S"],
     "description": ("Part 2's total PTE tax at line 52 is carried back into Part 1 at line 18 and "
                     "joins line 17 to make line 19. Because nonrefundable credits were applied at "
                     "line 15 AGAINST LINE 14, they cannot reduce the PTE tax; refundable credits at "
                     "line 20 sit in the payments block and can."),
     "definition": {"rule": "R-AZ120S-TAX + R-AZ120S-CREDITS",
                    "check": ("line_18 == line_52 AND line_19 == line_17 + line_18 AND line_17 == "
                              "line_14 - line_15 AND the PTE tax is never reduced by line 15")},
     "bug_reference": "Pub 713 says both 'No' and 'nothing precludes' on this exact question (U4)"},
    {"assertion_id": "FA-AZ120S-L49-L7", "status": "draft", "sort_order": 7,
     "title": "Form 120S line 49 == line 7 ONLY when line 7 was computed",
     "assertion_type": "reconciliation", "entity_types": ["1120S"],
     "description": ("The instruction misprints the ratio line as 'line 45', which is an INCOME "
                     "amount; the face is correct that line 49 is the ratio. AND THE CHECK CANNOT BE "
                     "HARD: line 7 is only reached when the S corporation has federal-level taxable "
                     "income, so a multistate electing S corp with no built-in gains and no excess net "
                     "passive income never computes line 7 yet still needs line 49 from Schedule A "
                     "line A5 / A3f or Schedule ACA line 3."),
     "definition": {"rule": "R-AZ120S-APPORT",
                    "check": "if line_7 is populated: line_49 == line_7; else line_49 comes from "
                             "Schedule A or Schedule ACA directly"},
     "bug_reference": "A hard equality zeroes line 49 for every electing multistate S corp without "
                      "federal-level taxable income"},
    {"assertion_id": "FA-AZ-RATE-FACE", "status": "draft", "sort_order": 8,
     "title": "The 2.5% PTE rate is pinned to the FORM FACE, not to A.R.S. § 43-1011",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"],
     "description": ("Pre-printed at Form 165 lines 20 and 24 and Form 120S lines 47 and 51 as 'the "
                     "PTE tax rate, 2.5% (0.0250)', and confirmed by Pub 713. A.R.S. 43-1014(A) sets "
                     "it BY REFERENCE to 'the highest tax rate prescribed by section 43-1011', but "
                     "43-1011 CANNOT BE READ off azleg: the 01011.01 URL 404s and 01011.htm serves a "
                     "superseded version topping at 4.50% whose subsection A stops at paragraph 4 "
                     "while its own subsection E refers to paragraphs 6-9 that are absent. THE RATE IS "
                     "SAFE; ONLY THE PROVENANCE CHANGED."),
     "definition": {"rule": "R-AZ165-RATE + R-AZ120S-RATE",
                    "check": "az_pte_rate(2025) == '0.0250' AND the rate constant is TY-keyed AND no "
                             "AuthoritySource is created for A.R.S. 43-1011"},
     "bug_reference": "U21 — the § 43-1011(A)(9) pinpoint is unsupported; cite the faces and Pub 713"},
    {"assertion_id": "FA-AZ-150K-EXCEED", "status": "draft", "sort_order": 9,
     "title": "The $150,000 estimated-payment test is STRICTLY GREATER THAN",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"],
     "description": ("A.R.S. 43-581(C) says 'EXCEEDS $150,000' and so do all six AZDOR instruction "
                     "sets — seven sources. One Pub 713 FAQ answer says 'or more'; Pub 713's own FAQ "
                     "lead-in says 'meets or exceeds'. AN ENTITY AT EXACTLY $150,000 IS OUT. "
                     "⚠ AN EARLIER VERIFICATION PASS FLIPPED THIS THE WRONG WAY IN "
                     "conformity/az_conformity.md AND A LATER PASS CAUGHT IT."),
     "definition": {"rule": "R-AZ165-EST-PAY + R-AZ120S-EST-PAY",
                    "check": ("az_estimated_payments_required(150000) is False AND (150001) is True "
                              "AND (149999) is False AND AZ_EST_BOUNDARY == 'exceeds'")},
     "bug_reference": "A `>=` implementation bills four installments and a Form 220/PTE penalty to "
                      "entities the statute exempts"},
    {"assertion_id": "FA-AZ-150K-BASIS", "status": "draft", "sort_order": 10,
     "title": "The $150,000 basis is a RULING that names a SOURCE and now also a NUMBER",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"],
     "description": ("AZDOR prints FOUR measurement bases and four of six documents contradict "
                     "themselves internally. Campaign D-12 A1 ruled the statute's bare 'taxable "
                     "income' and was REFINED the same session, because that named a SOURCE without "
                     "naming a NUMBER: A.R.S. § 43-1401(2) DEFINES the statute's term as 'Arizona "
                     "taxable income', so the ruled source RESOLVES INTO base 2 and the engine "
                     "computes PRIOR-YEAR Form 165 line 5 / Form 120S line 1. ⚠ STILL A RULING ON A "
                     "CONTESTED QUESTION, NOT A PUBLISHED AZDOR POSITION, with U19 OPEN AS A FACT and "
                     "the determination PROVISIONAL — the refinement narrows what we compute, it "
                     "does not close the question. All four candidates stay on the record with the "
                     "three losers explicitly NOT REFUTED."),
     "definition": {"rule": "R-AZ165-EST-BASIS",
                    "check": ("AZ_EST_MEASUREMENT_BASIS == 'statutory_bare_taxable_income' AND "
                              "AZ_EST_MEASUREMENT_BASIS_RESOLVES_TO == 'arizona_taxable_income' AND "
                              "AZ_EST_MEASUREMENT_DEFINITION names § 43-1401(2) AND "
                              "az_est_measurement_figure() resolves a FIGURE for each form AND "
                              "len(AZ_EST_MEASUREMENT_BASIS_CANDIDATES) == 4 AND the three "
                              "non-ruled candidates are still recorded as NOT REFUTED AND the ruling "
                              "text says it is not a published AZDOR position AND "
                              "D_AZ_U19_150K_BASIS still says PROVISIONAL")},
     "bug_reference": "$1,000,000 of Arizona taxable income at 10% consenting ownership is IN under "
                      "base 2 and OUT under base 3, from the same instruction book"},
    {"assertion_id": "FA-AZ-DIVISOR", "status": "draft", "sort_order": 11,
     "title": "The apportionment divisor is dynamic and the sales exclusion drops it to TWO",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"],
     "description": ("A.A.C. R15-2D-901(B): exclude a factor IFF both its numerator and denominator "
                     "are zero. Property or payroll excluded -> divide by THREE; SALES excluded -> "
                     "divide by TWO even though sales is DOUBLE-WEIGHTED; two excluded -> the "
                     "remaining factor IS the ratio, unweighted. A zero numerator over a positive "
                     "denominator is a LIVE ZERO FACTOR."),
     "definition": {"rule": "R-AZ165-DIVISOR + R-AZ120S-DIVISOR",
                    "check": ("az_apportionment_divisor(F,F,F) == 4; (T,F,F) == 3; (F,T,F) == 3; "
                              "(F,F,T) == 2; (T,F,T) is None; az_factor_is_excluded(0, 5000) is False")},
     "bug_reference": "Tying the divisor to the sales weighting gives three where Arizona says two"},
    {"assertion_id": "FA-AZ-NEXUS-NULL", "status": "draft", "sort_order": 12,
     "title": "An apportionment ratio of 0.000000 and a BLANK mean opposite things",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"],
     "description": ("Printed on both returns: '0.000000' means NO ARIZONA NEXUS, while BLANK or "
                     "'1.000000' means income sourced ENTIRELY WITHIN ARIZONA. The two must never be "
                     "collapsed."),
     "definition": {"rule": "R-AZ165-APPORT + R-AZ120S-APPORT",
                    "check": "az_nexus_from_ratio('0.000000') != az_nexus_from_ratio(None) AND "
                             "az_nexus_from_ratio(None) == az_nexus_from_ratio('1.000000')"},
     "bug_reference": "A null-vs-zero bug silently zeroes every nonresident owner's Arizona income"},
    {"assertion_id": "FA-AZ-MULTISTATE", "status": "draft", "sort_order": 13,
     "title": "Form 165 question D and Form 120S question B are INVERTED booleans",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"],
     "description": ("Form 165 question D asks whether the partnership is ARIZONA-ONLY ('Yes' = NOT "
                     "multistate); Form 120S question B asks whether the S corporation conducts "
                     "business WITHIN AND WITHOUT Arizona ('Yes' = IS multistate). Same concept, "
                     "opposite polarity, and az_is_multistate() refuses to guess."),
     "definition": {"rule": "R-AZ165-APPORT + R-AZ120S-APPORT",
                    "check": ("az_is_multistate('AZ_165', True) is False AND "
                              "az_is_multistate('AZ_120S', True) is True AND an unknown form code "
                              "raises ArizonaFormGovernsError")},
     "bug_reference": "A shared multistate boolean is inverted for one of the two Arizona returns"},
    {"assertion_id": "FA-AZ-P2GATE", "status": "draft", "sort_order": 14,
     "title": "Part 2 opens on Q.A = Yes OR PTE estimates paid — never on Q.A alone",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"],
     "description": ("Both Part 2 headers add '... or estimated payments were made and the "
                     "partnership / S Corporation is not claiming the PTE election', and both "
                     "instruction books script the resulting '$0 return' refund path line by line. "
                     "Pub 713 frames it around the federal SALT deduction rising from $10,000 to "
                     "$40,000 in 2025."),
     "definition": {"rule": "R-AZ165-PART2-GATE + R-AZ120S-PART2-GATE",
                    "check": ("az_part2_required(False, 40000) is True AND az_part2_required(False, 0) "
                              "is False AND az_part2_required(True, 0) is True")},
     "bug_reference": "Branching on question A alone suppresses Part 2 for exactly the population "
                      "that most needs it in TY2025"},
    {"assertion_id": "FA-AZ-165PA-DEFER", "status": "draft", "sort_order": 15,
     "title": "Form 165PA is RED-DEFERRED and its rate helper REFUSES",
     "assertion_type": "table_invariant", "entity_types": ["1065"],
     "description": ("Face line 13 and the instructions print 4.5% while A.R.S. 43-1414(B)(1)(b) "
                     "imposes the tax at the highest individual rate under 43-1011 = 2.5%. Building to "
                     "the face over-taxes by 80%; building to the statute contradicts a printed FINAL "
                     "form. Campaign D-12 A2: DEFER RATHER THAN CHOOSE. Both negatives verified — "
                     "S.B. 1274 Sec. 7 amended only subsection (A), and H.B. 4168 does not touch "
                     "43-1414 at all."),
     "definition": {"rule": "R-AZ165-165PA",
                    "check": ("az_165pa_rate() raises ArizonaDeferredFormError AND AZ_165PA_STATUS == "
                              "'RED_DEFER' AND all four family members are listed AND the 4.5% "
                              "LATE-FILING PENALTY is preserved separately")},
     "bug_reference": "A search-and-replace on '4.5' would break the 165PA late-filing penalty, which "
                      "is correct"},
    {"assertion_id": "FA-AZ-1021-15", "status": "draft", "sort_order": 16,
     "title": "The § 43-1021(15) add-back is OWNER LEVEL ONLY; the entity helper refuses",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"],
     "description": ("The statute directs the add-back into the owner's Arizona gross income AND the "
                     "entity's Arizona taxable income; only the owner half has a line. Form 165's "
                     "page-6 A4 worksheet is a closed list of three items with no free-text row "
                     "anywhere on page 6, and Form 120S has no additions schedule at all. Campaign "
                     "D-12 A3: BUILD TO THE FORM. The four owner add-back lines per schedule ARE "
                     "emitted."),
     "definition": {"rule": "R-AZ165-1021-15",
                    "check": ("AZ_1021_15_ENTITY_ADDBACK_BUILT is False AND "
                              "AZ_1021_15_OWNER_ADDBACK_BUILT is True AND "
                              "az_entity_level_pte_addback() raises AND every schedule in "
                              "AZ_OWNER_ADDBACK_LINES carries exactly four lines")},
     "bug_reference": "The cash-basis circularity is real: line 1 is already net of the PTE tax paid "
                      "during the year"},
    {"assertion_id": "FA-AZ-A4-CORP", "status": "draft", "sort_order": 17,
     "title": "A corporate partner's K-1 figure passes through unrecomputed, with a diagnostic",
     "assertion_type": "flow_assertion", "entity_types": ["1065"],
     "description": ("Form 165 computes on the INDIVIDUAL full-168(k) basis and Schedule K-1(NR) line "
                     "15 routes the figure to a C-corp partner's Form 120/120A Schedule A line A8 or "
                     "Schedule B line B10 in COLUMN (a), with no re-computation instruction anywhere, "
                     "while 43-1122(20) puts that corporation on the ELECT-OUT basis. Campaign D-12 "
                     "A4: pass through as printed, raise a review diagnostic, compute nothing."),
     "definition": {"rule": "R-AZ165-A4-CORP",
                    "check": ("AZ_CORPORATE_BASIS_RECOMPUTATION is None AND "
                              "az_corporate_partner_adjustment(x)['pass_through_amount'] == x AND "
                              "its 'column' is '(a)' AND it names D_AZ165_A4_CORP_PARTNER_BASIS")},
     "bug_reference": "Computing a corporate-basis figure would invent a position Arizona has never "
                      "stated (U2 open)"},
    {"assertion_id": "FA-AZ-SBI-18", "status": "draft", "sort_order": 18,
     "title": "Eighteen K-1 lines carry an SBI destination alongside the non-SBI one",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"],
     "description": ("SBI does NOT reach either entity computation — the two entity instruction books "
                     "contain ZERO 'SBI' references anywhere, including in their own K-1 walkthroughs "
                     "— but it reaches the K-1 ROUTING on 18 lines: 165 K-1 Part 7 lines 12-15; 165 "
                     "K-1(NR) Part 8 lines 24-27; 120S K-1 Part 4 line 7 and Part 5 lines 9-12; 120S "
                     "K-1(NR) Part 5 line 20 and Part 6 lines 22-25. THE COUNTING BASIS IS LINES WHOSE "
                     "OWN PRINTED ROUTING BLOCK NAMES AN -SBI FORM; the four PTE-CREDIT lines route to "
                     "Form 355 and reach SBI one hop further out via Form 301-SBI, so counting them "
                     "too would give 22. THE K-1 EMITTER MUST CARRY BOTH DESTINATIONS or the "
                     "individual module will have nothing to bind to."),
     "definition": {"rule": "R-AZ165-K1-SPLIT + R-AZ120S-K1-SPLIT",
                    "check": ("sum(len(v) for v in AZ_SBI_ROUTING_LINES.values()) == 18 AND "
                              "AZ_SBI_REACHES_ENTITY_COMPUTATION is False AND "
                              "AZ_165_SCHK1_LINE3_HAS_SBI_ROUTE is False")},
     "bug_reference": ("All 26 'small business' hits in the entity books are 'QUALIFIED small "
                       "business' (43-1022(21)) — a different regime")},
    {"assertion_id": "FA-AZ-179-LINE9", "status": "draft", "sort_order": 19,
     "title": "§ 179 reaches the partnership PTE base through line 9, and its limit is a ruling",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"],
     "description": ("A.R.S. 43-1412(5) makes IRC 179 a separately-stated item and 43-1401(1) excludes "
                     "those items from a partnership's Arizona gross income, so line 9 adds them back "
                     "— sixteen statutory categories in one undifferentiated box. For an S "
                     "corporation there is no routing question: line 37 = line 1 = federal Schedule K, "
                     "already net of federal 179. The Arizona LIMIT is campaign ruling D-10 "
                     "($2,500,000 / $4,000,000), NOT a published Arizona figure, and neither form "
                     "states a 179 figure at all."),
     "definition": {"rule": "R-AZ165-179-ROUTE",
                    "check": ("AZ_179_FORM_LINE_EXISTS is False AND AZ_43_1412_CATEGORY_COUNT == 16 "
                              "AND az_179_limits(2025)['basis'] == 'ruling' AND its provenance names "
                              "U3 as open")},
     "bug_reference": "The dollar limit and the routing are two different questions and only the "
                      "limit was ruled on"},
    {"assertion_id": "FA-AZ-EST-MONTHS", "status": "draft", "sort_order": 20,
     "title": "The fourth PTE installment is the 1st month AFTER year end, not the 12th",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"],
     "description": ("Both instruction books and Pub 713 agree: the 15th day of the 4th, 6th and 9th "
                     "months of the taxable year, and 'the 15th day of the 1st month FOLLOWING the "
                     "close of the taxable year'. Form 220/PTE line 7 prints the CORPORATE pattern "
                     "(4th/6th/9th/12th) on its face and appends 'PTE's see instructions'."),
     "definition": {"rule": "R-AZ165-EST-PAY + R-AZ120S-EST-PAY",
                    "check": ("az_pte_installment_months()[3] names the 1st month FOLLOWING the close "
                              "AND AZ_PTE_INSTALLMENT_MONTHS != AZ_CORP_INSTALLMENT_MONTHS AND "
                              "len(AZ_PTE_INSTALLMENT_MONTHS) == 4")},
     "bug_reference": "Reading the Form 220/PTE face alone puts the fourth installment three months "
                      "early"},
    {"assertion_id": "FA-AZ-355-LINE", "status": "draft", "sort_order": 21,
     "title": "The PTE credit goes to ARIZONA Form 355 — line 1 for partnerships, line 2 for S corps",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"],
     "description": ("Every owner schedule routes the credit to Arizona Form 355, and the LINE differs "
                     "by entity type. Estates and trusts instead use Form 141AZ line 19, and a "
                     "fiduciary may distribute any unused credit only to INDIVIDUAL beneficiaries. "
                     "⚠ ARIZONA'S FORM 355 IS A NUMBER COLLISION WITH MASSACHUSETTS FORM 355, which is "
                     "that state's C-corporation excise return."),
     "definition": {"rule": "R-AZ165-K1-CREDIT + R-AZ120S-K1-CREDIT",
                    "check": ("AZ_FORM_355_LINE_BY_ENTITY['1065'] ends 'line 1' AND "
                              "AZ_FORM_355_LINE_BY_ENTITY['1120S'] ends 'line 2' AND the credit is "
                              "nonrefundable with a five-year carryforward")},
     "bug_reference": "Massachusetts Form 355 is a different document entirely; MA left this wave "
                      "(D-12 Group B)"},
    {"assertion_id": "FA-AZ-DEPR-165", "status": "draft", "sort_order": 22,
     "title": "The depreciation shadow book is Form 165 ONLY, on the INDIVIDUAL basis, five tiers",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"],
     "description": ("Form 165 line B1 recomputes Arizona depreciation across FIVE placed-in-service "
                     "vintage tiers (0% / ITP 16-2 / 10% / 55% / 100% of federal IRC 168(k)) on the "
                     "INDIVIDUAL full-168(k) basis at 43-1022(17)(e). FORM 120S HAS NO DEPRECIATION "
                     "LOGIC AT ALL (campaign D-12). The keying is PLACED IN SERVICE and Arizona states "
                     "it four times, so no date-keying ruling is needed — contrast D-10 rulings 3 and "
                     "4 for Tennessee and Texas, where the sources were silent."),
     "definition": {"rule": "R-AZ165-DEPR-B1 + R-AZ165-BONUS-IND + R-AZ120S-NO-MODS",
                    "check": ("AZ_165_B1_TIER_COUNT == 5 AND AZ_165_B1_KEYED_ON == 'placed_in_service' "
                              "AND az_165_b1_bonus_pct(2025) == '1.00' AND az_165_b1_bonus_pct(2013) "
                              "is None AND AZ_120S_HAS_DEPRECIATION_LOGIC is False")},
     "bug_reference": "The individual rule is net-zero ONLY for post-2016 assets, so an old asset base "
                      "moves the partnership PTE base and not the S corp's"},
    {"assertion_id": "FA-AZ-INFO-PEN", "status": "draft", "sort_order": 23,
     "title": "The information-return penalty and the PTE election are mutually exclusive",
     "assertion_type": "flow_assertion", "entity_types": ["1065", "1120S"],
     "description": ("Both books: an entity that did NOT elect files an information return subject to "
                     "$100 per month or fraction, capped at $500; an entity that DID elect 'is not an "
                     "information return' and the line stays blank. Pub 713 was asked directly and "
                     "answered 'No.' On Form 165 the penalty sits at line 7 and repeats at line 36; on "
                     "Form 120S it sits at line 32."),
     "definition": {"rule": "R-AZ165-INFO-PEN + R-AZ120S-INFO-PEN",
                    "check": ("if AZ_165 question A == Yes: line_7 == 0 and line_36 == 0; if AZ_120S "
                              "question A == Yes: line_32 == 0; else min(100 * months, 500)")},
     "bug_reference": ""},
    {"assertion_id": "FA-AZ-K1NR-OFFSET", "status": "draft", "sort_order": 24,
     "title": "The two K-1(NR) line maps are OFF BY ONE from line 10 onward",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"],
     "description": ("The 120S Schedule K-1(NR) Part 1 is the 165 Schedule K-1(NR) Part 1 MINUS the "
                     "'Guaranteed payments to partner' line — correct, since S corporations have none "
                     "— so every line from 10 on is offset. On the 120S: 10 = IRC 1231, 11 = other "
                     "income, 12 = IRC 179, 13 = other deductions. On the 165: 10 = guaranteed "
                     "payments, 11 = IRC 1231, 12 = other income, 13 = IRC 179, 14 = other "
                     "deductions. The information-schedule INVENTORIES differ too."),
     "definition": {"rule": "R-AZ120S-K1NR-COL + R-AZ165-K1NR-COL",
                    "check": "no shared line map is applied across AZ_165_SCHK1NR and AZ_120S_SCHK1NR"},
     "bug_reference": "A shared line map silently mis-posts every item from line 10 on, and the return "
                      "still foots"},
    {"assertion_id": "FA-AZ-CONFORM-25", "status": "draft", "sort_order": 25,
     "title": "TY2025 conformity is COMPOUND and tax-year-keyed; TY2026 is a different subsection",
     "assertion_type": "table_invariant", "entity_types": ["1065", "1120S"],
     "description": ("A.R.S. 43-105(B) for TY2025: the IRC in effect 1/1/2025, excluding later "
                     "enactments, PLUS retroactively-effective P.L. 119-21 provisions. 43-105(A) for "
                     "TY2026+: a clean 1/1/2026. The practitioner headline describes (A). The IRC "
                     "168(n) add-backs begin in TY2026 under Ch. 140 Sec. 35(B)."),
     "definition": {"rule": "R-AZ165-CONFORM + R-AZ165-168N-NEG",
                    "check": ("az_conformity(2025)['base_irc_date'] == '2025-01-01' AND "
                              "az_conformity_is_compound(2025) is True AND az_conformity(2026)"
                              "['base_irc_date'] == '2026-01-01' AND az_conformity_is_compound(2026) "
                              "is False AND az_168n_addback_applies(2025) is False AND _yk() raises "
                              "for an unseeded year")},
     "bug_reference": "'Arizona updated conformity to January 1, 2026' describes TY2026 and poisons a "
                      "TY2025 depreciation computation"},
]


# ═══════════════════════════════════════════════════════════════════════════
# THE COMMAND
# ═══════════════════════════════════════════════════════════════════════════
class Command(BaseCommand):
    help = (
        "Load the Arizona PTE specs — Arizona Form 165 and Arizona Form 120S (TY2025). TWO forms, "
        "NOT three: Arizona's elective PTE tax rides on the existing returns (Form 165 Part 2 lines "
        "8-40; Form 120S Part 2 lines 37-52). ⚠ THE TWO RETURNS ARE NOT PARALLEL — Form 165 carries a "
        "full modification stack and a five-tier depreciation shadow book, Form 120S carries NONE of "
        "it. ⚠ READY_TO_SEED IS FALSE: Gate 1 has not been taken for Arizona and 21 [UNVERIFIED] items "
        "are open, three of them blocking."
    )

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nLoad Arizona PTE specs (Arizona Form 165 / Arizona Form 120S, TY2025)\n"))
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
        database untouched. It also refuses on a HOLLOW spec — an empty facts /
        rules / lines / diagnostics / scenarios / rule_links list — so a
        half-authored file cannot be seeded even after the sentinel is flipped.
        """
        empty = []
        for spec in FORMS:
            fn = spec["identity"]["form_number"]
            for key in ("facts", "rules", "lines", "diagnostics", "scenarios", "rule_links"):
                if not spec[key]:
                    empty.append(f"{fn}.{key}")
        if not FLOW_ASSERTIONS:
            empty.append("FLOW_ASSERTIONS")

        # ⚠ SUBSTANTIVE TRIPWIRES. These are not style checks — each one guards a
        # campaign ruling that a later contributor could undo by editing a single
        # constant. Re-pinned to the MECHANISM, per the D-10 and D-11 process
        # notes: a test pinned to a pre-approval VALUE has an expiry date, but a
        # test pinned to "does the guard still withhold?" does not.
        tripwires = []
        if AZ_120S_HAS_MODIFICATION_APPARATUS or AZ_120S_HAS_DEPRECIATION_LOGIC:
            tripwires.append(
                "AZ_120S_HAS_MODIFICATION_APPARATUS / AZ_120S_HAS_DEPRECIATION_LOGIC were flipped "
                "TRUE. Form 120S has NO Arizona modification apparatus — a VERIFIED NEGATIVE proved "
                "four independent ways (source brief §16.3) and ratified by campaign D-12 Group B. "
                "Do not add a 120S modification field 'for symmetry'.")
        if AZ_EST_BOUNDARY != "exceeds" or AZ_EST_BOUNDARY_EXACTLY_AT_THRESHOLD_IS_IN:
            tripwires.append(
                "THE $150,000 BOUNDARY WAS FLIPPED. A.R.S. § 43-581(C) and all six AZDOR instruction "
                "sets say 'EXCEEDS', so an entity at exactly $150,000 is OUT. An earlier verification "
                "pass flipped this the wrong way on the strength of ONE Pub 713 FAQ sentence and a "
                "later pass caught it; Pub 713 is internally inconsistent three ways.")
        if AZ_EST_MEASUREMENT_BASIS not in AZ_EST_MEASUREMENT_BASIS_CANDIDATES:
            tripwires.append(
                "AZ_EST_MEASUREMENT_BASIS is not one of the four recorded candidates. The ruled basis "
                "(D-12 A1) must stay adjudicable against the three AZDOR alternatives.")
        if len(AZ_EST_MEASUREMENT_BASIS_CANDIDATES) != 4:
            tripwires.append(
                "The $150,000 measurement-base conflict record no longer holds FOUR candidates. "
                "D-12 A1 is a RULING ON A CONTESTED QUESTION and U19 is OPEN; the losing readings "
                "must survive so a DOR answer can be re-adjudicated rather than inherited.")
        if (AZ_EST_MEASUREMENT_BASIS_RESOLVES_TO != "arizona_taxable_income"
                or AZ_EST_MEASUREMENT_BASIS_RESOLVES_TO not in AZ_EST_MEASUREMENT_BASIS_CANDIDATES):
            tripwires.append(
                "THE A1 REFINEMENT WAS UNDONE. D-12 A1 named a SOURCE without naming a NUMBER and was "
                "REFINED the same session to compute ARIZONA TAXABLE INCOME, because A.R.S. "
                "§ 43-1401(2) DEFINES the statute's term. Without the RESOLVES_TO leg the "
                "estimated-payment and Form 220/PTE penalty logic has a citation instead of a figure.")
        if "43-1401(2)" not in AZ_EST_MEASUREMENT_DEFINITION:
            tripwires.append(
                "AZ_EST_MEASUREMENT_DEFINITION no longer names A.R.S. § 43-1401(2) — the definition "
                "the A1 refinement follows. The refinement's whole mechanism is that Title 43 "
                "chapter 14 defines the statute's term; drop the cite and the ruling loses its basis.")
        if not set(AZ_EST_MEASUREMENT_FIGURE_BY_FORM) == set(FORM_CODES):
            tripwires.append(
                "AZ_EST_MEASUREMENT_FIGURE_BY_FORM no longer resolves a figure for BOTH forms. "
                "§ 43-581(C) reaches partnerships AND S corporations, and the two figures land on "
                "DIFFERENT lines (Form 165 line 5; Form 120S line 1).")
        if AZ_165PA_STATUS != "RED_DEFER":
            tripwires.append(
                "FORM 165PA WAS UN-DEFERRED. Its face prints 4.5% against the statute's 2.5% and "
                "campaign D-12 A2 ruled DEFER RATHER THAN PICK A RATE. Building to the face "
                "over-taxes by 80%.")
        if AZ_1021_15_ENTITY_ADDBACK_BUILT:
            tripwires.append(
                "AN ENTITY-LEVEL § 43-1021(15) PTE ADD-BACK WAS BUILT. Campaign D-12 A3 ruled BUILD "
                "TO THE FORM, OWNER LEVEL ONLY — no line exists on either form and the page-6 A4 "
                "worksheet is a closed list of three items.")
        if AZ_CORPORATE_BASIS_RECOMPUTATION is not None:
            tripwires.append(
                "A CORPORATE-BASIS RECOMPUTATION WAS ADDED. Campaign D-12 A4 ruled: pass the K-1 "
                "figure through as printed and raise a review diagnostic; compute NOTHING. Arizona "
                "publishes no such recomputation and no form line carries one.")
        if not AZ_179_IS_RULING_NOT_PUBLICATION:
            tripwires.append(
                "The § 179 figure was reclassified as a published Arizona number. D-10 recorded it as "
                "a RULING on an interpretive question and U3 stays OPEN AS A FACT — carry the ruling "
                "AND the gap.")
        if AZ_165_B1_TIER_COUNT != 5 or AZ_165_B1_KEYED_ON != "placed_in_service":
            tripwires.append(
                "The Form 165 line B1 depreciation table was altered. It has FIVE placed-in-service "
                "vintage tiers (the brief's 'four' was corrected on verification) and Arizona states "
                "the placed-in-service keying four times.")
        if AZ_SBI_LINE_COUNT != 18 or AZ_SBI_REACHES_ENTITY_COMPUTATION:
            tripwires.append(
                "The SBI routing map was altered. Eighteen K-1 lines carry an -SBI destination "
                "(counting basis: lines whose own printed routing block names an -SBI form); SBI does "
                "NOT reach either entity computation.")
        if AZ_UNVERIFIED_COUNT != 21:
            tripwires.append(
                f"The [UNVERIFIED] register holds {AZ_UNVERIFIED_COUNT} items, not 21. The "
                "verification pass closed NONE outright and ADDED three (U19, U20, U21). Items are "
                "closed by evidence, not by deletion.")

        if not READY_TO_SEED or empty or tripwires:
            still_empty = "\n  ".join(f"- {n}" for n in empty) or "(all populated)"
            tripped = "\n  ".join(f"- {t}" for t in tripwires) or "(none tripped)"
            raise CommandError(
                "\nREFUSING TO SEED THE ARIZONA PTE SPECS (AZ_165 / AZ_120S).\n"
                "Gate 1 has NOT been taken for Arizona. Campaign D-12 (2026-08-19) approved the WAVE\n"
                "SHAPE and four blocking rulings; it did NOT approve seeding these specs.\n\n"
                "WHY THIS FILE REFUSES:\n\n"
                "  (1) GATE 1 IS OPEN. D-12 ratified two Arizona specs (not three — Arizona's PTE\n"
                "      tax rides on Form 165 Part 2 and Form 120S Part 2), ruled the $150,000\n"
                "      measurement base (A1), RED-DEFERRED Form 165PA (A2), ruled the § 43-1021(15)\n"
                "      add-back to the form (A3), and ruled the corporate-partner pass-through (A4).\n"
                "      Approving the SHAPE is not approving the SEED.\n\n"
                "  (2) 21 [UNVERIFIED] ITEMS ARE OPEN AND THE VERIFICATION PASS CLOSED NONE\n"
                "      OUTRIGHT — it ADDED three. Three are blocking:\n"
                "      (a) U19 — WHICH taxable income measures the $150,000 estimated-payment\n"
                "          threshold. AZDOR prints FOUR bases and FOUR OF SIX DOCUMENTS CONTRADICT\n"
                "          THEMSELVES INTERNALLY. D-12 A1 ruled the statutory reading so authoring\n"
                "          may proceed, but the FACT STAYS OPEN and only an AZDOR ruling closes it.\n"
                "      (b) U14 — Form 165PA prints a 4.5% tax rate against A.R.S. § 43-1414(B)(1)(b)'s\n"
                "          2.5%. Both negatives are verified (S.B. 1274 § 7 amended only subsection\n"
                "          (A); H.B. 4168 does not touch § 43-1414 at all), so the divergence is real\n"
                "          and un-repealed. RED-DEFERRED rather than chosen.\n"
                "      (c) U3  — AZDOR has never published its provision-by-provision OBBBA\n"
                "          retroactivity mapping, so the TY2025 § 179 figure is a RULING (D-10), not\n"
                "          a published Arizona number. Carry the ruling AND the gap.\n\n"
                "  (3) ITP 16-2 IS UNPULLED AND IT GATES FORM 165 LINE B1's TY2013 VINTAGE TIER\n"
                "      (U1) — the only unpulled document that gates a mainstream line. AZDOR defers\n"
                "      entirely: 'the amount of the subtraction for these assets depends on the\n"
                "      method used to compute the depreciation for assets. See ... ITP 16-2.'\n"
                "      Pull it from AZDOR Legal Research -> Procedures first; it is cited three\n"
                "      times on that one line and may carry worked examples that change how the\n"
                "      other four tiers are implemented.\n\n"
                "  (4) HIGHEST-VALUE REMAINING PULLS, IN ORDER: an AZDOR ruling on the § 43-581(C)\n"
                "      measurement base (U19); ITP 16-2 (U1); the Form 120 / 120A instructions,\n"
                "      which would close A4's factual gap (U2); the TY2025 Form 140-SBI /\n"
                "      140PY-SBI instructions (U6); A.R.S. § 43-1011 from a source that serves the\n"
                "      operative version, since azleg 404s on one URL and serves a superseded 4.50%\n"
                "      version on the other (U21); and AZDOR's OBBBA mapping (U3), which may not\n"
                "      exist.\n\n"
                f"READY_TO_SEED = {READY_TO_SEED} (must be True to proceed)\n\n"
                f"Currently empty / placeholder:\n  {still_empty}\n\n"
                f"Substantive tripwires:\n  {tripped}\n\n"
                "DO NOT RELAX THIS GUARD TO SILENCE THE ERROR — fix the cause, which in every case\n"
                "above means getting an answer from AZDOR or from Ken, not editing this file.\n"
                "⚠ AND DO NOT EDIT A TRIPWIRE CONSTANT TO PASS: each one guards a campaign ruling.\n"
                "References: delvio-states/research/az_pte_source_brief.md (its SECTION 16\n"
                "VERIFICATION SECTION GOVERNS over the body), delvio-states/conformity/\n"
                "az_conformity.md (its section 12 governs, EXCEPT that its $150,000 boundary and its\n"
                "ModDate table are both corrected by the source brief), and delvio-states/\n"
                "DECISIONS.md D-10 and D-12 (including A4, ruled separately the same session).\n"
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
                # Arizona's Tier-1 conformity row IS seeded in prod (campaign D-10,
                # conformity_type = 'static'), so this must not fire there. It WILL
                # fire on a throwaway SQLite harness DB unless the Tier-1 batch is
                # seeded first, which validate_az.py does deliberately.
                self.stdout.write(self.style.WARNING(
                    f"  existing source {code} NOT FOUND - links to it will be skipped "
                    "(expected only on a fresh/throwaway DB; AZ Tier-1 conformity is seeded in prod)"))
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
        self.stdout.write("Arizona PTE specs loaded (TY2025).")
        for spec in FORMS:
            fn = spec["identity"]["form_number"]
            self.stdout.write(
                f"  {fn}: facts {len(spec['facts'])} / rules {len(spec['rules'])} / "
                f"lines {len(spec['lines'])} / diag {len(spec['diagnostics'])} / "
                f"tests {len(spec['scenarios'])} / links {len(spec['rule_links'])}"
            )
        self.stdout.write(
            f"  shared: flow assertions {len(FLOW_ASSERTIONS)} / sources {len(AUTHORITY_SOURCES)} / "
            f"topics {len(AUTHORITY_TOPICS)} / shared diagnostics {len(AZ_SHARED_DIAGNOSTICS)} / "
            f"RED-DEFERS {AZ_RED_DEFER_COUNT} / open [UNVERIFIED] {AZ_UNVERIFIED_COUNT} "
            f"(blocking: {', '.join(AZ_UNVERIFIED_BLOCKING)}) / printed defects {AZ_PRINTED_DEFECT_COUNT}"
        )
        self.stdout.write("=" * 72)
