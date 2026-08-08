# Source brief — Form 1099-LTC → Form 8853 Section C

*Authored 2026-08-08 (s232). Companion to the `8853_SEC_C` spec
(`specs/management/commands/load_1040_8853_sec_c.py`).*

Per s222, **no RS spec is authored for an information return** — the 404-STOP gate
applies to computed forms. An information return builds from the IRS form plus a
source brief, and this is that brief. The computed half (Form 8853 Section C) DOES
have a spec; this document covers only the 1099-LTC rows that feed it.

⚠ **There is deliberately no spec under the bare form number `8853`.** Ken's s224
ruling put Section C only in season-one scope, and a spec claiming the whole form
while describing half of it is the s231 Form-3800 defect. Sections A/B (Archer MSA,
Medicare Advantage MSA) reserve the form number `8853_SEC_AB`. A future session that
curls `/lookup/8853/` and gets a 404 should read this brief, not improvise.

---

## The form

**Form 1099-LTC (Rev. April 2025)** — Long-Term Care and Accelerated Death Benefits.
`https://www.irs.gov/pub/irs-pdf/f1099ltc.pdf`
SHA256 `69623198392f04003e66480c084cac90f920951d830a5fc73f35ad45aefaabdc`

⚠ **CONTINUOUS-USE FORM.** It carries a revision line (`Rev. April 2025`), not a tax
year. Per the s230 rule the s224 `f<form>.pdf` next-revision trap does **not** apply —
but the revision must be read out of the PDF rather than assumed. Verified 2026-08-08:
`irs-pdf/f1099ltc.pdf` and `irs-prior/f1099ltc--2025.pdf` are byte-identical.

## Three parties, three TINs — and Section C keys on the third

| Party | On the form | Role |
|---|---|---|
| PAYER | name, TIN, address, phone | the insurer or viatical settlement provider |
| POLICYHOLDER | name, TIN, address | **files the return** and reports the income |
| INSURED | name, TIN, address | **the Section C aggregation key** |

The policyholder reports the income *even when payment was assigned to a third party*
(i8853: "even if payment is assigned to a third party or parties") — so benefits paid
straight to a nursing home are still the client's to pick up, a common case where no
cash ever reached them. On a group contract the **certificate holder** is the
policyholder.

Section C is **one per INSURED**, not one per policyholder and not one per 1099-LTC,
because §7702B(d)(3) treats "all persons receiving periodic payments … with respect to
the same insured … as 1 person."

## Box map

| Box | Content | Destination |
|---|---|---|
| 1 | Gross long-term care benefits paid | Section C **line 17**, but only where box 3 = *Per diem* |
| 2 | Accelerated death benefits paid | Section C **line 19** — the chronically-ill SLICE only |
| 3 | Check one: *Per diem* / *Reimbursed amount* | the ROUTER (see below) |
| 4 | Qualified contract (**optional**) | informs **line 18** (the qualified part of line 17) |
| 5 | Check if applicable (**optional**): *Chronically ill* / *Terminally ill* / *Date certified* | informs **line 16** and splits line 19 |
| — | Account number | row identity for the import lane |

### ⚠⚠ The trap: absence is never an answer

Boxes 4 and 5 are **optional for the payer** ("May show…"), and box 3 **"may not be
checked"** when the insured was terminally ill. Therefore:

- An unchecked **box 4** is *not* evidence of a non-qualified contract → `D_8853C_QUALIFIED_UNCONFIRMED`.
- An unchecked **box 3** is *not* evidence of reimbursement basis, and the row must not
  be silently dropped from line 17 → `D_8853C_BOX3_UNCHECKED`.
- An unchecked **box 5** is *not* evidence the insured was neither chronically nor
  terminally ill.

This is the s224 "missing column read as a missing box" class, inverted: here the box
exists and is legitimately blank. Every one of these is a preparer confirmation with a
diagnostic, never an inference from absence.

### Box 2 is not line 19

Line 19 is the **chronically-ill slice** of box 2. i8853 line 19: exclude amounts
received while the insured was terminally ill; on mid-year redesignation from
chronically to terminally ill, include only payments received *before* terminal
certification — box 5's *Date certified* is the split point. **Do not auto-fill line 19
from box 2.**

## Row shape for the import lane

One row per Form 1099-LTC received, grouped by insured:

```
payer_name, payer_tin, payer_address, payer_phone
policyholder_name, policyholder_tin, policyholder_address
insured_name, insured_tin, insured_address          # the grouping key
account_number
box1_gross_ltc_benefits          decimal
box2_accelerated_death_benefits  decimal
box3_basis                       choice: per_diem | reimbursed | unchecked
box4_qualified_contract          boolean, nullable (optional box)
box5_chronically_ill             boolean, nullable (optional box)
box5_terminally_ill              boolean, nullable (optional box)
box5_date_certified              date, nullable
corrected                        boolean
```

`box3_basis` must be able to represent **unchecked** as distinct from either value, and
`box4` / `box5_*` must be **nullable** rather than defaulting false — a `False` default
would encode "not a qualified contract" from a blank optional box, which is precisely
the inference the form forbids. This is the s224 lesson about a hardcoded zero making a
limit too large, applied to booleans.

## Lane wiring checklist (the s224/s225 lane registries)

A form is not importable until every one of these is touched — s214: *"the form is
built" ≠ "the form is importable"*:

- `LIST_SECTIONS` — the section appears in the published lane schema
- `SECTION_ALLOWLISTS` — its fields are accepted
- `SECTION_RELATED` — the insured grouping is fetched
- `_model_for` — the section resolves to its model
- the validator **and** `_create_rows` (s225: nested rows need both)
- the doc-contract test that polices NOT-SUPPORTED vs LIST_SECTIONS (s227)

## What Section C then does with it

See the spec for the full statement. In brief:

```
line 17 = Σ box 1 where box 3 = Per diem        (per insured)
line 18 = the QUALIFIED part of line 17          (preparer-confirmed)
line 19 = chronically-ill slice of box 2         (preparer-asserted)
line 20 = 18 + 19
line 21 = $420 × days in the LTC period          (Rev. Proc. 2024-40 §2.62)
line 23 = MAX(21, 22)                            (§7702B(d)(2) greater-of)
line 25 = 23 − 24
line 26 = MAX(0, 20 − 25)                        (§7702B(d)(1) the excess)
       → a COMPONENT of Schedule 1 line 8e
```

⚠ **Line 8e is composed, not owned.** Its MeF element is `TotArcherMSAMedcrLTCAmt` —
Archer MSA + Medicare Advantage MSA + LTC in one line. The s230 Schedule-K-13g ruling
governs: the writer is a registry. Section C contributes its component; the Sections
A/B residual stays preparer-keyed.

## Refusals (declared, never silent)

| Condition | Diagnostic | Why refuse |
|---|---|---|
| line 15 = Yes (multiple payees) | `D_8853C_MULTIPAYEE_HOLD` | the limitation is shared; computing a full one **under-reports** income |
| line 15 unanswered | `D_8853C_PAYEE_UNANSWERED` | the permissive answer must never be the silent default |
| more than one LTC period | `D_8853C_MULTI_PERIOD` | blending periods produces a wrong line 21 |
| days outside 1–365 | `D_8853C_DAYS_RANGE` | arithmetically impossible; an inflated count inflates the limitation |
| 1040-NR | `D_8853C_NR_UNWIRED` | destination is Schedule NEC line 12 with the literal `LTC`; not built |

## Not in scope

- **Sections A/B** (Archer MSA, Medicare Advantage MSA) — Ken's s224 ruling. Form 8889
  line 4 stays a keyed figure under the existing `D_8889_ARCHER` guard.
- **The Multiple Payees aggregate statement** — fully specced in `R-8853C-MULTIPAYEE`
  ready for a follow-on build. When built, allocate on the **unrounded** payment ratio:
  i8853 Example 2 Step 3 gives 33,000/51,000 × 51,480 = **33,311**, not 64.7% × 51,480
  = 33,308. The s230 never-split-an-already-rounded-share rule, confirmed by the IRS's
  own arithmetic.
- **A 1099-LTC e-filing/issuing lane** — this is a received document only. (The firm's
  issuing side lives in `sherpa-1099`, which keeps its own tables per
  `SUITE_CONTRACT.md`.)
