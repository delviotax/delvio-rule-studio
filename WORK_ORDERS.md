# WORK_ORDERS.md — Rule Studio work queue (the front door)

*Adopted 2026-07-04. This makes RS the TRIGGER: authoring work enters HERE first, is
approved by Ken, and only THEN is the tax-app build dispatched. Reverses the old
spec-last habit (app discovers a missing spec mid-build) into spec-first-by-sequence —
which is the standard the app already enforces and CLAUDE.md already requires.*

***ORDER LIVES IN BUILD_ORDER.md (canonical in `tts-tax-status`), NOT here.** This file is
the RS front-door MECHANISM: it holds the gap-check, the transition states, Gate-1 approval,
and the working detail of the CURRENT order. It takes its next authoring order FROM the
BUILD_ORDER SPINE. Do NOT maintain a second ordered backlog here — that is what drifted
(states showed queued here while DONE in the spine). At session start, reconcile against
BUILD_ORDER + live STATUS before pulling the next order.*

## What this changes (and what it doesn't)
- **Unchanged:** the runtime wiring. Specs still seed→export→home in the app→load via the
  existing gated ingest. No new coupling, no auto-propagation.
- **Changed:** the WORK ORDER. New modules start with a spec-gap check on the RS side; gaps
  are cleared and Ken-approved BEFORE the app build starts. The app stops discovering
  missing specs mid-flight because the question is asked at the top.

## The flow
```
  scope item (Ken) ─┐
                    ├─► THIS QUEUE ─► spec-gap check ─► CC drafts from verified source
  change register ──┘    (intake)     (first step)             │
                                              ⟨GATE 1: Ken approves the spec⟩
                                                      │
                                          spec seeds + exports (RS)
                                                      │
                                          Pushover ping: "ready to dispatch"
                                                      │
                                          app build dispatched (tts session)
                                                      │
                                              ⟨GATE 2: existing gated ingest⟩
                                                      │
                                          compute + flow assertions + regression
```
**Two human gates, non-negotiable.** A tax-law update or Ken may START a draft; nothing
CROSSES a gate unattended. Gate 1 = draft→published spec (Ken). Gate 2 = published→compute
(existing ingest). An update can trigger *authoring*; never *publication* or *computation*.

## Two modes (pick per module)
- **RS-first (default for NEW/greenfield modules):** enumerate the required form set up front,
  gap-check, author + approve all gaps, THEN dispatch the app build. Use for SC/AL/NC, 1041,
  1065 core.
- **Tail-completion (for finishing a huge module, e.g. 1040):** keep the app/ATS discovery
  loop — when testing surfaces a missing spec, it drops back into THIS queue as a new order,
  not a silent stall. This is a feature for unknowable long tails, not the default.

## The spec-gap check (CC runs this as step 1 of any module)
1. Ken (or PRODUCT_MAP scope) names the module's required forms/schedules.
2. For each, check RS coverage: `GET /api/forms/lookup/<FORM>/export/` → 200 = spec exists,
   404 = gap. (Cross-check the RS forms index / session_log.)
3. Write the gap list into this file as an order with status `GAP-CHECKED`.
4. Do NOT start the app build until every gap for that module is `APPROVED`.

## Order format
`[ID] source · module · status · required set → gaps · links/approval`
Statuses: `INTAKE → GAP-CHECKED → DRAFTING → ⏳ AWAITING KEN → APPROVED (seeded/exported)
→ DISPATCHED (app) → ✅ DONE`

## Wave orders — the 45-state campaign batching convention (added 2026-08-05)
*Campaign charter: Tax Shelter Future D-030; sequence detail in `delviotax/delvio-states`
`STATE_MATRIX.md`; batching ruled by Ken as delvio-states D-4.*

The one-form-per-order shape above does not scale to the campaign's ~130-200 state forms —
it would put ~150 Gate-1 walks on Ken personally. State authoring therefore batches:

- **One WO per WAVE**, not per form. A wave = **3-5 states × 1 module type**
  (`[WO-W##-<MODULE>]`, e.g. `[WO-W03-PTE]`). Wave order: PTE (1065+1120S paired) →
  C-corp → individual (the slow lane) → fiduciary on demand. CA runs as its own wave.
- **Transitions are tracked at wave level** — the whole wave moves GAP-CHECKED → DRAFTING →
  AWAITING KEN → APPROVED together. A single state that turns out to be a monster is SPLIT
  OUT into its own WO rather than stalling its wave.
- **Two batched Gate-1 walks per wave**, not two per form: one SCOPE walk (per-state quirks
  — PTET regime, conformity posture, apportionment — are the walk items) and one SEED
  approval. **Both gates still exist**; batching changes their granularity, never their
  existence, and nothing crosses either unattended.
- **The gap-check still runs per FORM** (`lookup/<FORM>/export/`, 404 = gap) — the batching
  is in the approval and authoring, not in the evidence.
- **Conformity first:** a new state's `JurisdictionConformitySource` row
  (`load_state_conformity.py`) is authored BEFORE any of that state's form specs, so all of
  its module specs export one shared, cited conformity block.

### State form-number namespacing (settled 2026-08-05, campaign D-9)
New state forms use **`<ST>_<FORM>`** — `SC1120`, `NC_D400`, `AL_FORM_40`. Rationale:
`_lookup_queryset` filters on `form_number__iexact` and **does NOT filter by jurisdiction**,
so a bare numeric form number is a live collision hazard once 45 states arrive (many states
use bare-numeric form names). GA's individual return is seeded as bare **`500`** — a legacy
exception, NOT a pattern; leave it (renaming breaks the app's existing mirror + field maps)
and namespace everything new. ⚠ Also note the app-side wart this feeds: delvio-tax mixes
`GA-500` (hyphenated) with `SC1040`/`AL40`/`NC_D400`, which already caused a live
`FORM_TO_STATE` bug — its state-registry refactor owns normalizing that end.

---

## ▶ CURRENT ORDER — pulled from the BUILD_ORDER SPINE (canonical in `tts-tax-status`)
*No independent backlog here (see header). Sequence = BUILD_ORDER.md SPINE; statuses seeded
from live STATUS.md per BUILD_ORDER's own rule. Reconciled 2026-07-05.*

> **[WO-8853-SEC-C] Ken's s224 scope ruling item 4, lane re-confirmed 2026-08-08 (s232 —
> Ken picked spec-first for the last day before a 10-day absence) · Form 8853 **Section C
> only**, long-term care insurance contracts + accelerated death benefits · ✅ APPROVED
> (seeded/exported/cached) — Gate 1 approved by Ken in-session 2026-08-08 ("Approve as
> drafted", explicitly including the statutory floor on line 25 and the composed Schedule 1
> line 8e) → sentinel flipped → seeded to the RS prod DB (**135 forms**; 18 authority links;
> all 10 rules cited; 5 flow assertions) → deployed `lookup/8853_SEC_C/export/` returns
> **200** → cached to delvio-tax `server/specs/8853_sec_c_spec.json` (69,685 bytes; 23 facts
> / 10 rules / 14 line_map rows / 12 diagnostics / 14 tests / 7 authority sources verified
> present in the cached file). Form `status` left at `draft`, matching the house convention
> (126 of 135 forms, incl. every recently Gate-1-approved spec) — the approval is recorded
> here and in the sentinel, not in the model field. **NEXT: DISPATCH the app build (tts
> session)** — the whole point of the spec-first call was that the build needs nothing
> further from Ken during his 08-09 → ~08-19 absence.**
> · **required set:** `8853_SEC_C` → gap CONFIRMED 2026-08-08. `lookup/8853/export/`,
> `lookup/1099LTC/export/` and `lookup/1099_LTC/export/` all 404; nothing in delvio-tax
> `server/specs/`; no source brief in this repo. App side: NO compute, NO model, NO field
> map, NO PDF template (f8853 absent from `forms_manifest.json`).
> · ⚠ **The destination already exists and already fails.** Schedule 1 line **8e** is
> seeded "Income from Form 8853" as a KEYED currency line, and `form_manifest.py` already
> declares `AttachmentRequirement("Form 8853")` on it — `test_form_manifest.py` literally
> pins the comment *"Form 8853 — never generated"*. So today an LTC client's taxable
> payments must be hand-keyed and the manifest correctly reports a required attachment the
> app cannot produce. That comment is the build leg's acceptance criterion to delete.
> · **Authored:** `load_1040_8853_sec_c.py` (`READY_TO_SEED=False`) — 23 facts / 10 rules
> (R-8853C-SCOPE/FILING/LINE17/LINE20/LIMIT/LINE26/MULTIPAYEE/PERIOD/DEST/ATTACH, all
> cited) / 14 face lines (14a-26) / 12 diagnostics / 13 scenarios / 5 flow assertions.
> Integrity gate `check_8853_sec_c_integrity.py` GREEN, shares no math — and its teeth were
> PROVEN by a negative control that injected 6 defects (min-for-max at line 23, a stale
> $410 rate, a fact default drifting off the constant, a dropped face line, an invalid
> enum, and an unfloored line 25) and confirmed all 6 are caught.
> · ⚠⚠ **THE STATUTE CORRECTED THE DRAFT — line 25 is FLOORED and the FACE DOES NOT SAY SO.**
> §7702B(d)(2) verbatim defines the limitation as "the **excess (if any)** of— (A) the
> greater of … over (B) … reimbursements". "Excess (if any)" is the Code's floor-at-zero
> idiom. The face prints "If zero or less, enter -0-" on line **26 only**; line 25 says
> merely "Subtract line 24 from line 23". This spec was FIRST DRAFTED UNFLOORED off the
> face plus an LII fetch that returned a paraphrase with the phrase dropped; a second fetch
> from uscode.house.gov caught it. The defect was live, not theoretical: line 20 = 10,000
> with reimbursements driving line 25 to −5,000 produced line 26 = **15,000** — taxing half
> again more than the taxpayer ever received. Now pinned by scenario **T14** plus a
> structural gate invariant (line 26 may never exceed line 20) that is hardcoded
> independently of the scenarios. **The lesson, again: a paraphrase is not a verbatim, and
> the face is not the statute.**
> · ⚠⚠ **THE CENTRAL DESIGN FINDING — Schedule 1 line 8e is a COMPOSED line, and the IRS's
> own schema says so.** Its MeF element is **`TotArcherMSAMedcrLTCAmt`** — Total **Archer
> MSA / Medcr / LTC** Amount — and the face itself says "include this amount in the TOTAL
> on line 8e". i8853 confirms from the other side (an Archer MSA deemed-loan is also
> reported on 8e). This is the s230 Schedule-K-13g situation exactly, so DECISIONS.md
> governs: **a shared line's writer is a REGISTRY, not whichever form got there first.**
> v1 composes 8e = (Section C component) + (preparer-keyed Sections A/B residual), so a
> later Sections A/B build joins instead of silently overwriting. The failure mode this
> prevents is a DISAPPEARED number — which is why nobody would ever report it.
> · **Law verified 2026-08-08 (fetched, not memory):** §7702B(d)(1) excess includible /
> (d)(2) the "greater of" less reimbursements — which maps 1:1 onto face lines 21/22→23→
> less 24→25 / (d)(3)(A)+(B) verbatim (all payees for one insured treated as **1 person**;
> limitation allocated first to the insured) / (d)(4) the $175 baseline / (d)(5) indexing.
> **Rev. Proc. 2024-40 §2.62 verbatim: the 2025 per diem limitation is $420** — and the
> 2025 face PRINTS $420 on line 21 while i8853's Example 1 footnote cites that exact
> section, so the constant has **three independent confirmations**. §101(g)(1)/(3)/(4):
> terminally ill excluded outright (the face's skip-17-through-25), chronically ill limited
> to the §7702B treatment, and the two statuses mutually exclusive.
> · ⚠ **NOT the §213(d)(10) item** already in delvio-tax DECISIONS.md: that is Rev. Proc.
> 2024-40 **§3.28**, the age-band cap on deductible LTC **premiums** (a DEDUCTION). This is
> **§2.62**, the per diem cap on an **EXCLUSION**. Different halves of the same subject.
> · **Scenarios T1-T3 are the IRS's own published examples transcribed verbatim** (i8853
> Example 1; Example 2 Steps 1 and 2), so the rate, the greater-of and the zero floor are
> validated against an IRS answer key rather than against our reading. The gate also
> reproduces Example 2 Step 3's allocation on the **UNROUNDED** ratio (33,000/51,000 ×
> 51,480 = **33,311**, not 64.7% × 51,480 = 33,308) — the s230 never-split-an-
> already-rounded-share rule, confirmed by the IRS's own arithmetic.
> · **GATE-1 WALK ITEMS for Ken:** (1) line 8e becomes COMPOSED per the K13g registry
> ruling; (2) Multiple Payees (line 15 = Yes) is **REFUSED, not approximated** — ⚠ check
> the sign: computing an unshared limitation makes line 25 too large and line 26 too small,
> i.e. it UNDER-reports taxable income, so refusing is the conservative direction;
> (3) lines 15 and 16 are three-state (yes/no/**unanswered**) because the permissive answer
> must never be the silent default; (4) the LTC-period day count is a preparer ELECTION
> between two defined methods, so only a 1-365 range check is available — and a 365 keyed
> where the truth is 1 inflates the limitation 365-fold in the taxpayer's favour;
> (5) the pre-August-1-1996 reimbursement carve-out defaults OFF (excluding reimbursements
> is taxpayer-favourable); (6) Sections A/B stay out of scope and Form 8889 line 4 stays
> keyed under `D_8889_ARCHER`; (7) the **narrowness of the terminally-ill short circuit** —
> line 16 = Yes alone is NOT enough, the ONLY payments must be ADB paid for that reason
> (scenario T7 pins a case where short-circuiting on line 16 alone would wrongly exclude
> 29,580); (8) **the statutory floor on line 25** that the face does not print — the one
> item where the spec now departs from a literal reading of the form, so it is the item
> most worth Ken's eye. ⚠ ONE remaining `requires_human_review` verbatim flag: the
> §101(g)(3) conditions for chronically-ill accelerated death benefits. (§7702B(d)(1) and
> (d)(2) are now captured verbatim and the flag is cleared.)
> · **Deliberately NO spec under the bare form number `8853`** — a spec claiming the whole
> form while describing half of it is the s231 Form-3800 defect (a `line_map` that did not
> match the real face). `8853_SEC_AB` is reserved for the Archer sections, and
> `f8853_1099ltc_source_brief.md` explains the 404 to whoever hits it next.
> · **The 1099-LTC gets no spec** (s222: information returns build from the form + a source
> brief) → `f8853_1099ltc_source_brief.md`, incl. the lane-registry checklist and the
> ⚠ optional-box trap: boxes 4 and 5 are optional and box 3 "may not be checked" when the
> insured was terminally ill, so **absence is never an answer** — the nullable-not-false
> rule, or a blank optional box silently encodes a negative.
> · ⓘ **Adjacent observation, NOT a new order (Ken's call):** Rev. Proc. 2024-40 exists
> under **three** source_codes — `RP_2024_40`, `REV_PROC_2024_40`, `IRS_RP_2024_40`. This
> spec reuses `RP_2024_40` and attaches its §2.62 excerpt there rather than minting a
> fourth. Distinct from **[WO-SOURCETYPE-RECON]** (invalid `source_type` *values*); this is
> duplicate *source_codes for one document*, which nothing currently tracks. ✔ Re-ran that
> order's survey while here: my counts match its 2026-08-05 figures, and the `1065`/`1041`/
> `1120s` values that look alarming are exactly its documented 13 false positives
> (TestScenario `inputs` payloads) — my grep wasn't scoped to dicts carrying `source_code`,
> so the caveat earned its keep. This loader uses only valid enums, and the ratchet test
> stayed green. ⚠ `RP_2024_40` itself still carries the invalid `source_type=revenue_procedure`
> in the DB; this order deliberately did NOT repair it (that rewrites a published export
> across other forms — WO-SOURCETYPE-RECON's job), and attaching an excerpt does not rewrite
> the parent row.
> · ⓘ **Second adjacent observation for [WO-SOURCETYPE-RECON] — the same root cause on a
> SECOND field.** `TaxForm.status` choices are draft/review/approved/archived, but **5 rows
> carry `active`**, which is the *FlowAssertion* Status vocabulary (draft/active/disabled).
> Django does not enforce choices, so the two Status classes have cross-contaminated exactly
> the way `source_type` did. Worth folding into that order's scope rather than opening a
> third: the fix and the verification pass are identical in shape.
> · ⓘ **Export-shape gap (small, unowned):** the spec export serializer omits
> `requires_human_review` — the field is authoring-side only and never reaches the app's
> cached spec. So a build session reading `server/specs/*.json` cannot see which authorities
> are flagged as unverified. Verified 2026-08-08 against the live export (source keys:
> citation, current_status, excerpts, is_substantive_authority, issuer, jurisdiction_code,
> source_code, source_rank, source_type, title, topics, trust_score). For 8853_SEC_C the one
> live flag is `IRC_101_G`, recorded here instead.
>
> **[WO-K1-BASIS-704D] Mixed-entity pilot #7 (filing blocker; Ken chose spec-first
> 2026-08-07 s226) · partner §704(d) basis limitation, preparer-asserted · ✅ APPROVED (seeded/exported) — Gate 1 approved by Ken in-session
> 2026-08-07 ("Approve — flip, seed, export") → sentinel flipped (`0dab0f3`) → seeded to the
> RS prod DB (134 forms; 12 authority links; all rules cited) → deployed
> `lookup/K1_BASIS_704D/export/` returns 200 → spec cached to delvio-tax
> `server/specs/k1_basis_704d_spec.json`. NEXT: DISPATCH the app build (tts session). · required set: `K1_BASIS_704D` → gap CONFIRMED (no spec existed;
> `SCHEDULE_K1_1065 R-K1-ITEM-L` is the ENTITY-side item L capital roll-forward, itself
> RED-deferred — item L capital ≠ outside basis, §752).
> · **Authored:** `load_1040_k1_basis_704d.py` (`READY_TO_SEED=False`) — 8 facts / 6 rules
> (R-K1B-SCOPE/ASSERT/ARITH/ORDER/QBI/CARRY, all cited) / 8 worksheet lines / 5 diagnostics
> (D_K1B_ARITH error — arithmetically impossible never acknowledgable; EXCESS_DISTRIB;
> PASSIVE; UNASSERTED — the D_K1_BASIS successor, saved-worksheet-clears per the 7203
> confirm precedent; FULLY_ALLOWED) / 7 scenarios (T1 = the pilot's 26,850/10,621/16,229) /
> 5 flow assertions (FA-1040-K1B-01…05, incl. the persistence gate — deliberately NO
> MeF/render check). Integrity gate `check_k1_basis_704d_integrity.py` GREEN (shares no math).
> · **The shape (the s225 REVIEW_QUEUE recommendation, Ken-picked):** the preparer ASSERTS
> allowed + suspended from the source return's worksheet; the app routes max(raw, −allowed)
> once in `k1_sche_net()` (the Form-7203 arm's twin), checks the two identities (allowed +
> suspended = loss; allowed ≤ max(0, beginning + additions − distributions)) and DIAGNOSES —
> never derives the §704(d) limit.
> · **Law verified 2026-08-07 (fetched, not memory):** §704(d)(1) verbatim; (d)(3)(A)/(B)
> charitable/FTC nuance; 2025 Partner's Instructions verbatim — the ORDER (basis → at-risk →
> passive → EBL, agrees with FORM_6198 R008), the carryforward, and "the partner's
> responsibility to track" (⚠ the scope finding: NOT attached to the return → no MeF doc, no
> render leg); Reg §1.199A-3(b)(1)(iv)(A) — QBI never double-limited.
> · **GATE-1 WALK ITEMS for Ken:** (1) the preparer-asserted shape (nothing derived); (2) the
> arithmetic checks + error severity; (3) the no-attachment scope finding; (4) QBI
> no-double-limit; (5) v1 scope = 1065 nonpassive (materially participating) only — passive
> basis-limited keeps the Decision-4 RED; (6) the asserted "allowed" covers basis AND at-risk
> combined (the app checkbox couples them). ⚠ Two sources flagged `requires_human_review` on
> verbatim status: Reg §1.704-1(d) (eCFR blocked the fetch — summary corroborated by the
> instructions) and §704(d)(2)'s odd "repaid" sentence.**
>
> **[WO-CONF-SPINE] 45-state campaign Phase 2 (Tax Shelter Future D-030, 2026-08-05) ·
> state conformity spine + campaign scale pre-work · ✅ DONE — Gate 1 APPROVED by Ken
> in-session 2026-08-05 (W1 "Approve — flip, seed, verify"; W4 "Separate WO, ratchet holds
> meanwhile") → sentinel flipped → migration `sources.0006` confirmed applied (the Render
> deploy of `8948e2e` ran it via `build.sh`; unique constraint verified present in prod) →
> `load_state_conformity` seeded **4 rows** (GA updated, SC/AL/NC created) → `load_ga700`
> re-seeded so the `source_type` fix reached prod (verified `state_instruction`) →
> **ALL 17 STATE FORM EXPORTS NOW CARRY NON-NULL `state_conformity`** (GA×5 partial · SC×4
> static · AL×4 rolling · NC×4 static; federal 4797 correctly null) → `seed_all --dry-run`
> lists `load_state_conformity` under phase 3 amends → **full suite 224 passed**.
> ⚠ One self-inflicted catch worth recording: the first version of `test_conformity_loader_is_gated`
> asserted `READY_TO_SEED is False`, which went red the instant the loader was legitimately
> approved — the same "permanently-red test is one nobody reads" class as the 8879 harness rot.
> Rewritten to pin the guard MECHANISM (monkeypatch to False, assert it refuses and writes
> nothing) plus a --dry-run case. · W4 → new order **[WO-SOURCETYPE-RECON]** below.**
> · original scope follows:
> · **Scope:** make `JurisdictionConformitySource` the shared, exported conformity spine for
> every state BEFORE the campaign multiplies state specs ~10×. Not new tax research — the
> SC/AL/NC content is TRANSCRIBED from their own already-Gate-1-approved loaders and cited to
> the same AuthoritySource rows (GA ← load_remaining_1120s / D-8; SC ← load_sc1040 W1/W5 +
> SC_ACT63_2025_CONFORMITY / D-6; AL ← load_al_form20c W5 + AL_CODE_40_18 §40-18-1.1 / D-14;
> NC ← load_nc_d400 W2/W3 + NC_GS_105_153_6 / D-7). It still crosses Gate 1 because it changes
> what the export endpoints serve.
> · **The gap it closes:** GA/2025 was the ONLY conformity row; **SC, AL and NC each exported
> `"state_conformity": null`**, so 3 of the 4 built states shipped no machine-readable
> conformity to delvio-tax.
> · **Built (all tests green, 223 passed):** `load_state_conformity.py` (new, `READY_TO_SEED=False`,
> the SINGLE writer — GA's inline row REMOVED from `load_remaining_1120s.py`, since two writers of
> one row is the 2026-07-05 delta-audit hazard) · migration `sources.0006` adding
> **unique (jurisdiction_code, tax_year)** · export lookup `.get()` → `.filter().first()` (it could
> raise MultipleObjectsReturned uncaught — a 500 on a spec-package endpoint) · `decoupled_items`
> normalized to the documented 5-key shape with `authority_source_code` (a CODE string, not the
> documented UUID — UUIDs differ per environment and the rest of the package resolves authority by
> code) · added to `AMEND_LOADERS` (its FK anchors need phase-2 sources) · `tests/test_state_conformity.py`
> (12 tests) · **`load_ga700.py` `source_type: "state_guidance"` → `state_instruction`** (that value
> was never a valid `SourceType` choice; Django does not enforce choices at the DB layer).
> · **W1.** Approve the four TY2025 rows as transcribed (GA partial / SC static 12-31-2024 /
> AL rolling / NC static 01-01-2023), incl. each row's `decoupled_items`.
> · **W2.** Approve the canonical `decoupled_items` shape — delvio-tax's state-registry refactor
> consumes it, so it is a downstream contract.
> · **W3.** Approve the GA row MOVING loaders (content preserved verbatim + enriched to the 5-key
> shape; re-seed required for the GA700 `source_type` fix to reach prod).
> · **W4.** ⚠ **FINDING, out of scope, needs its own order:** the `source_type` vocabulary is
> systemically drifted — **232 invalid values across 74 loaders** (`statute` 108, `official_instructions`
> 59, `federal_form` 29, `official_guidance` 28, +5 more), every one a near-miss of a real choice
> (note `OFFICIAL_INSTRUCTION` is singular). Reconciling rewrites published exports. Phase 2 fixed
> only the one value it touched and installed a **ratchet test** (counts may only fall; a new
> distinct value fails). Ken: separate WO, or leave ratcheted?
> · **On approval:** flip `READY_TO_SEED` → `migrate` → `load_state_conformity` → re-run `load_ga700`
> → verify SC/AL/NC/GA exports carry non-null `state_conformity` → `seed_all --dry-run` →
> explicit-path commit. **Prod probe (read-only, 2026-08-05): 1 conformity row, no duplicate
> (state,year) keys — the unique constraint applies cleanly; all 5 authority anchors FOUND.**

> **[WO-SOURCETYPE-RECON] Ken (2026-08-05, WO-CONF-SPINE W4: "Separate WO, ratchet holds
> meanwhile") · repo-wide `source_type` vocabulary reconciliation · INTAKE**
> · **The finding:** `AuthoritySource.source_type` is a CharField with `choices`, and Django does
> NOT enforce choices at the DB layer — so an informal vocabulary has been persisting silently
> since the earliest loaders. Survey 2026-08-05: **232 invalid values across 74 loaders** —
> `statute` 108 · `official_instructions` 59 · `federal_form` 29 · `official_guidance` 28 ·
> `instructions` 2 · `revenue_procedure` 2 · `form` 2 · `irs_guidance` 1 · `case_law` 1.
> Every one is a near-miss of a real choice (note `OFFICIAL_INSTRUCTION` is **singular**;
> `statute` should be `code_section` or `state_statute` depending on jurisdiction).
> · **Why it matters:** the field is unusable for filtering, grouping or reporting, and the
> campaign is about to add ~130-200 more state forms on top of it.
> · **Why it is its own order:** correcting the values rewrites **published exports** across 74
> forms, so it needs its own Gate-1 review and its own verification pass — it is not a
> drive-by fix.
> · **Holding pattern (live now):** `tests/test_state_conformity.py::test_no_new_invalid_source_types`
> is a RATCHET — per-value counts may only fall, and any NEW distinct value fails the suite.
> `test_state_conformity_loader_uses_valid_source_types` keeps campaign loaders clean from the start.
> · ⚠ **Survey caveat for whoever takes this:** scope the AST walk to dicts that carry
> `source_code`. `source_type` also appears inside TestScenario `inputs` payloads meaning
> something unrelated ("this K-1 came from a 1065"), which produced 13 false positives on the
> first run of the survey. Verify the gate against a known case before trusting its output.

> **[WO-GA500-RECON] Ken (2026-08-02, "GA 500 spec next") · GA-500 spec reconciliation ·
> ✅ DONE — Gate 1 APPROVED by Ken in-session 2026-08-02 ("Approve as drafted", incl. the
> g_lic_not_dependent default flip) → re-seeded (84 facts / 23 rules / 91 lines / 17 diag /
> 20 scenarios; the stale renamed-T2 orphan deleted — the 6-25 renamed-T11 precedent) →
> re-exported canonical `tts server/specs/500_spec.json` → id-level diff EXACTLY the
> intended set → tts GA-500 band 596 green. No app build to dispatch (the engine already
> implements all three rulings — this order reconciled the spec TO the engine). ·
> original scope: bring the seeded GA-500 spec up to the season's three
> Ken-ruled engine corrections it drifted behind — NO new law, every change implements a
> ruling already live in the tts engine:**
> **① R-GA500-MIL** — the 2026-07-05 military over-exclusion fix finally applied RS-side
> (the handoff `tts docs/rs_handoff/2026-07-05_ga500_military_exclusion_fix.md` was never
> executed): worksheet L7 = the preprinted $35,000 cap, L8 = min(retirement, L7) entered
> ALONE (never L3+L8); the mis-transcribed authority excerpt corrected; scenario T5
> re-pinned + NEW T19 (midrange $20k retirement → $20k excluded, tax 1,453 vs the buggy 675).
> **② Line 7c derived** (tts s176): 7c = 7a + 7b, preparer-saved 7c wins; `g_num_dependents`
> repointed to 7a (its old note contradicted itself), `g_num_unborn_dependents` joins
> R-GA500-L14-DEP's inputs (unborn COUNT for line 14 — LIFE Act); T2 re-pinned with an
> unborn dependent (7c 3 → L14 12,000 → tax 3,322).
> **③ R-GA500-LIC** (Ken ruling s182, the batch-002 LIC hold): exemptions = IT-511 p35 VERBATIM
> "self, spouse and natural or legally adopted children" + age-65 count — NEW fact
> `g_lic_children` (the app's derived LIC-CHILD) replaces the all-7c count; the wrong
> excerpt paraphrase corrected at the source; NEW T20 (HOH + ODC brother: L14 4,000 but
> 17a = 1, credit $5 not $10). **Plus one DEFAULT DECISION for Ken:** `g_lic_not_dependent`
> default flipped true → false — the engine gates the whole credit on the explicit
> LIC-NODEP assertion (the batch-005 finding), and a default-granted eligibility is a silent
> credit. **Gate `check_ga500_integrity.py` ALL CHECKS PASS — 20 scenarios** (loader and
> gate share no math). NOT re-seeded / NOT re-exported — awaiting Ken's Gate-1 approval;
> then: re-seed RS DB → re-export canonical `tts server/specs/500_spec.json` (id-level
> diff: only R-GA500-MIL / R-GA500-L14-DEP / R-GA500-LIC + the two facts + the two
> excerpts) → verify the tts pure-scenario suite stays green. Out of scope (priced
> separately as the follow-on "August GA build unit"): the UET worksheet computation
> (line 42, currently direct-entry by design) and the S4-8/S4-NB-18
> seeded-computed-but-never-written NOL lines; TY2026 military full exemption (SB 31)
> stays the standing loader W-item.**

> **⟨GATE-1⟩ APPROVED + SEEDED — 2026-07-27 (tts s124): Form 4562 `D_4562_RECON`
> amended for the §179 business-income limitation. State: DONE.**
> Defect intake was a DEFECT, not a law change — the tts s124 test-settlement pass
> found the s116 reconciliation guard raising a BLOCKING error on a CORRECT return
> whenever §179(b)(3)(A) capped the deduction ($10,000 elected against $8,000 of
> Schedule C income legitimately puts the allowed 8,000 on Schedule C line 13 and
> carries 2,000 to line 13 of the 4562, and the guard compared against the full
> election). **Ken approved the two-part fix in-session over the alternatives of
> downgrading the severity or deferring.**
> Authored: **R020** (reconciliation basis — (a) each destination carries at least
> its non-§179 total; (b) the §179 that landed ties to LINE 12) + the amended
> `D_4562_RECON` condition/notes + **4 scenarios** incl. the false-positive negative
> control and a genuine gap that must still fire under an active limitation.
> Face text re-pinned verbatim off the local SHA-tracked `f4562.pdf` (L11/L12/L13,
> pymupdf 2026-07-27) — not memory. Harness `check_4562_recon_integrity.py`
> recomputes every scenario independently and re-implements the PRE-amendment
> condition as a negative control; **three perturbation controls each observed
> failing** before restore. Seeded to prod (4562 now 20 rules · 17 diagnostics ·
> 39 scenarios); deployed `lookup/4562/export/` verified carrying R020 and the new
> condition; mirrored verbatim to tts `server/specs/form_4562_spec.json`.
> FLAGGED for ratification (in tts REVIEW_QUEUE, not IRS-sourced): accrual Schedule F
> scoped out of part (b), and part (b) standing down in the pure-prior-year-carryover
> shape.

> **⟨GATE-1⟩ ×5 APPROVED + SEEDED — 2026-07-14 (tts s83): Ken approve-all across
> WO-28 (9465) · WO-29 (8888) · WO-30 (1040-V/ES pair) · WO-31 (4868) · WO-32 (8915-F),
> recommendations adopted as filed.** Sentinels flipped (+approval in docstrings); the five
> harnesses re-cut to the post-approval guard pattern (monkeypatch-off proves the mechanism)
> and re-run: **85/0 · 53/0 · 63/0 · 97/0 · 87/0**. All five prod-seeded (SIX TaxForms —
> 9465 46L/9R/17D · 8888 16L/6R/12D · 1040V 6L/3R/5D + 1040ES 8L/4R/10D · 4868 17L/11R/16D ·
> 8915F 44L/10R/15D; 15 FAs staged DRAFT). Deployed `lookup/{9465,8888,1040V,1040ES,4868,
> 8915F}/export/` = **200 ×6**; tts mirrors cached (`server/specs/{9465,8888,1040v,1040es,
> 4868,8915f}_spec.json`); the deployed 1040 FA export verified clean — 398 = the tts 397
> mirror + the known s71-staged FA-1040-4835-06, **zero cluster drafts leaked**; tts flow
> gate 500 green. → DISPATCHED: **the six tts legs as a set** (9465 print+IRS9465 · 8888
> print+IRS8888+35a · V/ES print-only w/ suppression ties · 4868 print + the NEW extension
> submission builder + Sch3-L10 tie · 8915-F full unit: inputs + per-disaster compute +
> render + IRS8915F + the 5329 suppression seam). Ken-sequenced: SEC-1 (tts authz audit)
> runs first; the six legs follow.

- **⏳ [WO-33] Forms 8879 + 8878 · IRS e-file Signature Authorization pair · greenfield RS-first ·
  status `GAP-CHECKED → research-verified → DRAFTED + SQLite-VALIDATED → ⏳ AWAITING KEN (Gate-1)`
  (the next NEW autonomous item per BUILD_ORDER after the six-leg set landed; tts s90).**
  Gap confirmed 2026-07-15 (`lookup/{8879,FORM_8879,8878,FORM_8878}/export/` = 404 ×4; local cache
  holds only the entity-side 8879S/8453S). **The structural headline: NEITHER FORM TRANSMITS** —
  both faces say "ERO Must Retain This Form — Don't Submit This Form to the IRS Unless Requested To
  Do So"; there is NO MeF document and NO new family — the electronic mirror is the Return Header
  signature block tts ALREADY e-files (PINTypeCd/JuratDisclosureCd/PractitionerPINGrp — ATS-proven).
  The tts leg on approval = a persistent signature-input surface + TWO AcroForm print units +
  diagnostics tying the print to the header PIN data + extract gating (the s87 print-only recipe
  with a HEADER tie instead of a payment tie). **✅ RESEARCH-VERIFIED (2026-07-15, verbatim vs Form
  8879 Rev. 01-2021 (continuous-use, self-contained instructions; About: developments none) + Form
  8878 (2025) (YEAR-DATED, Created 4/17/25; About: none) + Pub. 1345 signature chapter pp. 14-18 +
  efileTypes/ReturnHeader1040x XSDs 2025v5.3 + the 47 signature-family Active rules in the 1040
  Business Rules CSV)** → `f8879_8878_source_brief.md`. **Research catches:** (1) **the 8879 4-row
  chart collapses to: required iff Practitioner PIN method OR ERO enters/generates any taxpayer
  PIN** — the counter-intuitive row: PP + taxpayer-keys-own-PIN STILL requires the full form incl.
  Part III (Pub 1345: PP taxpayers "must ALWAYS sign"); the ONLY skip row = self-select + own PIN;
  (2) **the 8878's load-bearing negative: a 4868 WITHOUT an EFW election NEVER needs an 8878**
  (chart row 2 beats everything — the print mirror of the s88 R0000-098 no-payment-no-signature
  story); the 2350 arm needs ERO-entered only and **NEVER reaches Part III ("Practitioner PIN
  Method for Form 4868 Only", face verbatim twice)**; (3) **the Pub-1345 $50/$14 re-sign
  tolerance**: a NEW signature only when post-signing changes exceed $50 Total income/AGI or $14
  total tax/withholding/refund/owed ("differ by MORE than" — at the boundary exactly, no re-sign)
  — requires a SIGNED-AT Part I snapshot to compare against recomputes; (4) the 3-day stockpiling
  clock + sign-BEFORE-transmit + the 20-digit SID-after-filing (or associate Form 9325 — the S-22b
  triage item) + 3-year retention (Rev. Proc. 97-22); (5) non-PP authentication = DOB + prior-year
  AGI/PIN from the ORIGINALLY FILED prior-year return (never amended/math-error; IND-025..032);
  the under-16 ×2 + duplicate-SSN self-select bars (IND-664..667/674..680); (6) the 8878 face is
  YEAR-DATED (jurat embeds "December 31, 2025") vs the continuous-use 8879 — year-watch, the s48
  class; (7) 1040-SS filers use 8879 line 4 ONLY (face note; app boundary). **✅ AUTHORED (draft) +
  SQLite-VALIDATED** (`load_8879_8878.py`, ONE loader TWO TaxForms `8879`+`8878` (the WO-30 pair
  precedent): 22+14 facts / 8+4 rules / 16+13 lines / 9+7 diag / 8+6 scenarios / 3 FA staged DRAFT;
  `scratchpad/validate_8879_8878.py` = **77 pass / 0 fail** — all FOUR 8879 chart rows + all FIVE
  8878 rows pinned, the tolerance at/over the boundary both families, PIN hygiene, the bars, the
  1040-SS arm, every scenario recomputed, the flagged seams asserted present, guard-refusal +
  twice-run). **⛔ GATE-1 PENDING — READY_TO_SEED ships False; NOT seeded, NOT exported.**
  **Gate-1 walk for Ken (W1-W4, recommendations = approve all):** W1 the 8879 need-gate (the
  4-row chart; house default = PP method → in practice every e-filed 1040 prints one) + Part I
  amounts off the 1040 face; W2 signature mechanics (PIN hygiene; sign-before-transmit; SID/9325;
  the $50/$14 tolerance + snapshot; stockpiling; the self-select bars + prior-year authentication);
  W3 the 8878 EFW gate (no-EFW-never; the 4868-line-7 tie; 2350 = encoded boundary, never Part
  III); W4 ties + print-only-BY-DESIGN (no MeF document anywhere in ReturnData) + the
  extract-refusal recommendation. **FOUR seams flagged, not resolved (recommendations attached):
  (a) 8879 line 3 mapping — face literal is 1040 25a+25b, RECOMMEND 25d (total withholding) so
  Part I stays self-consistent with L4/L5; divergence only when 25c ≠ 0; (b) the 1040-X arm —
  RECOMMEND Part I carries the column-C world off the existing 1040-X unit; (c) extract gating —
  RECOMMEND the extract refuses when a required authorization lacks a signed date (revisit at
  S-17g transmit); (d) the signed-at snapshot persists Part I at signature time for the tolerance
  compare.** On approval: flip, seed, verify exports (8879 + 8878), cache the tts mirrors →
  dispatch the tts print-pair leg. ⏭ Next NEW autonomous item per BUILD_ORDER while gated:
  SEC-2..6 → S-24; A2A preempts the moment the WSDLs land.

- **✅ [WO-32] Form 8915-F · Qualified Disaster Retirement Plan Distributions and Repayments ·
  greenfield RS-first · status `GAP-CHECKED → research-verified → DRAFTED + SQLite-VALIDATED → Gate-1 APPROVED + SEEDED + EXPORTED
  2026-07-14 → DISPATCHED → ✅ DONE 2026-07-15 (tts s89 build leg landed — the LAST of the six dispatched legs; FA-8915F-CAP/SPRD/LAND
  flipped draft → active + reseeded; deployed 1040 FA export verified 413 active; tts flow gate 515)` (post-payment-cluster order 2, tts s79).**
  Gap confirmed 2026-07-14 (`lookup/8915F|8915-F/export/` = 404 ×2). **The SECURE 2.0 §331 "forever
  form"** — items A/B name the instance; married = a SEPARATE form per spouse; MeF channel EXISTS:
  IRS8915F rides ReturnData1040 (2025v5.3, **maxOccurs=6**, per-document name/SSN) — the tts leg on
  approval = inputs + per-disaster compute + print + MeF document (the s72 recipe). **✅ RESEARCH-
  VERIFIED (2026-07-14, verbatim vs Form 8915-F Rev. December 2025 (Created 5/23/25) + i8915f Rev.
  12-2025 (73 pp) + IRS8915F.xsd 2025v5.3 + the 1040 rules CSV — exactly 3 Active F8915F rules)** →
  `f8915f_source_brief.md`. **Research catches:** (1) ⚠ the About page's Recent Developments ALL
  target older revisions (the live form+instructions are Rev. 12-2025); the 20-Dec-2024 development
  = the IRS's own **Appendix-D off-by-one** ("1 less day than is granted for repayments") — fixed in
  the current tables AND it names the failure class the period helpers pin: **Part I distributions
  get 179 days, Part IV repayments get 180** (one-day asymmetry, pinned in both directions against
  all published examples: DR-4682-WA 7/10 vs 7/11 · DR-4681 6/27 vs 6/28 · DR-4685-GA 7/14 vs 7/15 ·
  DR-4644-VA 6/26 vs 6/27 via the 12/29/2022 SECURE-floor arm); (2) **the Rev-12-2025 face REDESIGNED
  Part I: NEW line 5a** (non-QDD carve-out; old 5 → 5b; the 2025v5.3 XSD already models it);
  (3) the **$22,000-per-disaster cap is ALL-plans, ACROSS-YEARS** ($100,000 only for item-B-2020),
  F8915F-003 Active caps line 1d; the single-new-disaster shortcut (skip to 1e = $22,000);
  (4) **the designation rule**: once the 3-part test holds (period + main-home-in-area + economic
  loss), ANY distribution — including RMDs and periodic payments — may be designated a QDD;
  (5) the 11↔22 opt-out boxes MUST MATCH (face verbatim both lines); ÷3.0 prints no rounding →
  whole-dollar convention FLAGGED (the 9465 ÷72 class); (6) repayments = day-after through
  **3 years + 1 day**; this-year inclusion needs before-filing AND by-due-date, else forward/
  carryback (the Rudy examples pinned); can't repay non-spouse-beneficiary/RMD/SEPP; (7) the 8606
  15b/25b ties (lines 18/19, attributable-to-THIS-form — the tts s75 8606 unit is the producing
  seam); (8) **line 6 QDDs are exempt from the 10%/25% early tax and NEVER generate a 5329** (the
  tts 5329-unit seam: suppress the early-tax row for line-6 amounts; line 7 + Part IV line 32 route
  normally); landings 15 → 1040 5b · 26 → 4b; (9) worksheet lines 12/14/23/25 carry BinaryAttachment
  refs (the attach-worksheet-to-back e-file mirror); Worksheet 1B/2/3/4/5 internals + the Appendix
  A/C/D tables = STATED BOUNDARY (engine-derived, never re-encoded). **✅ AUTHORED (draft) +
  SQLite-VALIDATED** (`load_8915f.py`, 28 facts / 10 rules / 44 lines / 15 diag / 10 scenarios /
  3 FA staged DRAFT; `scratchpad/validate_8915f.py` = **87 pass / 0 fail** — all eight published
  date pins, the 1a-1e ladder incl. the 44,000 F8915F-003 boundary, the 5a/5b redesign math, spread/
  opt-out consistency all four arms, the receipt-window edges, every scenario recomputed, the
  flagged conventions asserted present, guard-refusal + twice-run). **⛔ GATE-1 PENDING —
  READY_TO_SEED ships False; NOT seeded, NOT exported.** **Gate-1 walk for Ken (W1-W4,
  recommendations = approve all):** W1 the QDD framework (3-part test + the any-distribution
  designation rule + the 179-day period + the $22,000 cap + DR-majors-only); W2 the Part I ladder +
  the 5a/5b redesign + the spread conventions (÷3.0 flag; 11↔22; death-collapse); W3 repayments
  (3y+1d; Rudy both directions; can't-repay list) + the 8606 ties + Part IV (the [-180d, +30d]
  window; the 180-day repayment period; re-designation); W4 the MeF document (max 6; year-enum
  rejects; worksheet attachments) + the 4b/5b landings + the 5329-waiver seam (entity_types
  ['1040']; print + MeF document). On approval: flip, seed, verify export, cache the tts mirror →
  dispatch the tts unit (inputs + per-disaster compute engine + render + IRS8915F builder + the
  4b/5b landing ties + the 5329 suppression seam). ⏭ Next NEW autonomous item per BUILD_ORDER:
  W-2G → 8879/8878; A2A preempts the moment the WSDLs land. **Ken now holds FIVE walks
  (WO-28/29/30/31/32).**

- **✅ [WO-31] Form 4868 · Automatic Extension of Time To File · greenfield RS-first · status
  `GAP-CHECKED → research-verified → DRAFTED + SQLite-VALIDATED → Gate-1 APPROVED + SEEDED + EXPORTED
  2026-07-14 → ✅ DONE 2026-07-15 (tts s88 build leg landed: Form4868 singleton migs 0202/0203 +
  compute_4868 pinned to all 10 spec oracles incl. both partition-pinned where-to-file columns (the
  FOUR-way GA Charlotte trap cross-module-pinned) + 16 D_4868_* + f4868 AcroForm face render
  (suppression IS the render gate; STANDALONE — never in the packet) + the NEW extension submission
  family (Return4868 builder/read-model/mapper + schema_locator family root; no-payment = NO
  signature, the jurat ladder with one; live-XSD valid both shapes) + the R-4868-CREDIT Sch3-L10
  YELLOW feeder (component-sum L5 derive — the divergence guard) + the Payments-tab card;
  FA-4868-L6/EFW/CREDIT flipped draft → active + reseeded, deployed 1040 FA export verified 410
  active, tts mirror refreshed export-verbatim 409, runners in BOTH chains — tts flow gate 509 → 512)`
  (post-payment-cluster order, tts s78 — the BUILD_ORDER "next NEW item: 4868, separate MeF family").**
  Gap confirmed 2026-07-14 (`lookup/4868/export/` = 404). **The structural headline: the 4868 is its OWN
  MeF submission family** (ReturnTypeCd "4868" — Return4868/ReturnHeader4868/ReturnData4868), NOT a
  ReturnData1040 document — the tts leg on approval = print render + a NEW extension submission builder.
  ReturnData = six-element IRS4868 (L4-L9) + ≤1 IRSPayment + ≤4 IRSESPayment (the s76 records, reused
  verbatim) + NO binary attachments (R0000-195 Active despite the XSD slot — refusal-encoded).
  **✅ RESEARCH-VERIFIED (2026-07-14, verbatim vs Form 4868 (2025, Created 10/1/25 — self-contained
  form+instructions, no separate i4868; About page "None at this time") + the LOCAL MeF 4868_2026v1.0
  package (XSDs + rules PDF read directly)) → `f4868_source_brief.md`.** **Research catches:** (1) **the
  signature story — a no-payment e-filed 4868 carries NO signature at all** (every header signature group
  minOccurs=0; the paper face has no signature line); R0000-098 triggers the PIN+jurat ladder ONLY when an
  IRSPayment/IRSESPayment rides (jurat enum = exactly "Form 4868" / "Form 4868 with Practitioner PIN and
  EFW", F4868-007/8/9); (2) **FPYMT-052-02 = the s76 EFW tie** (IRSPayment PaymentAmt == line 7 — the
  4868's F9465-019-02 analogue); (3) **⚠ the TY2026v1.0 package's FPYMT-088-11 still lists the
  2026-calendar ES dates** — self-contradictory with FPYMT-086 for a 2027-filed extension; flagged as a
  stale early-drop carryover, year-keyed, re-pull later drops; (4) **⚠ version seam**: face = 2025 revision
  (TY2025), local MeF package = TY2026v1.0 (the Jan-2027 season vintage; the TY2026 face publishes ~Oct
  2026 — re-verify then, the s48 face-drift class); (5) **the Charlotte trap is now FOUR-way**: GA
  4868-with-payment → **Box 1302** (V 1214 · ES 1300 · foreign 1303), rosters encoded + partition-pinned;
  (6) the L5 exclusion (expected line 33 EXCLUDING Sch 3 L10 — which IS the 4868 payment; double-count
  guard) + the L6 "-0-" floor; (7) the 90%-paid two-prong reasonable-cause safe harbor + the $525 (YEAR-
  KEYED) >60-day minimum; (8) the 709/709-NA FILING rider (payment = 8892 — the 4868↔709 seam for the
  mission's 709 lane); (9) line 9 (1040-NR June-15 due) lands **Dec 15 DERIVED** (6 months from the
  June-15 due date; the face prints only "October 15, 2026, for most" — i1040-NR states it; walk note).
  **✅ AUTHORED (draft) + SQLite-VALIDATED** (`load_4868.py`, 18 facts / 11 rules / 17 lines / 16 diag /
  10 scenarios / 3 FA staged DRAFT; `scratchpad/validate_4868.py` = **97 pass / 0 fail** — L6 floor
  oracles, both window arms incl. boundaries + the after-period-end floor, all four extension landings,
  the 90%-exactly harbor boundary, the EFW tie, the payment-triggered signature + jurat ladder, the
  joint-ampersand rule BOTH directions, the address chart incl. 51-jurisdiction partition pins + the
  four-way divergence, every scenario recomputed, the flagged seams asserted PRESENT in the spec text,
  guard-refusal + twice-run). **⛔ GATE-1 PENDING — READY_TO_SEED ships False; NOT seeded, NOT exported.**
  **Gate-1 walk for Ken (W1-W4, recommendations = approve all):** W1 face math + qualifying (L6 floor;
  L4 = expected line 24, zero → -0-, unreasonable = null-and-void; L5 exclusions); W2 windows (4/15 //
  line 8/9 → 6/15; landings 10/15 // line-9 Dec-15 DERIVED; fiscal-year = paper only; the e-pay-marked-
  extension no-form alternative); W3 the own-family MeF channel (no-payment-no-signature; the jurat
  ladder; the EFW tie; no attachments; IND-900 duplicate; **+ ratify the two flagged seams: the stale
  FPYMT-088-11 list + the 2025-face/TY2026-package anchoring**); W4 penalties/safe harbor ($525 year-
  keyed) + Sch 3 L10 credit routing (joint/separate splits both directions) + the four-row year-watched
  chart + the 709 rider (entity_types ['1040']; print + own-family MeF). On approval: flip, seed, verify
  export, cache the tts mirror → dispatch the tts unit (4868 print render + extension submission builder +
  the Sch 3 L10 derive tie + diagnostics + FA runners/activate/mirror-refresh). ⏭ Next NEW autonomous
  item per BUILD_ORDER: 8915-F → W-2G → 8879/8878; A2A preempts the moment the WSDLs land.

- **✅ [WO-30] 1040-V + 1040-ES voucher pair · Payment Vouchers · greenfield RS-first · status
  `GAP-CHECKED → research-verified → DRAFTED + SQLite-VALIDATED → Gate-1 APPROVED + SEEDED + EXPORTED
  2026-07-14 → ✅ DONE 2026-07-15 (tts s87 build leg landed: PaymentVouchers singleton migs 0200/0201 +
  compute_vouchers pinned to all 10 spec oracles incl. both partition-pinned charts + 15 D_V_*/D_ES_* +
  f1040v/f1040es AcroForm print legs (v_needed/emission ARE the render gates — a suppressed voucher
  can't reach paper) + the packet "voucher" back tier + the Payments-tab card; FA-1040V-EFW/FA-ES-RAP/
  FA-ES-QDEBIT flipped draft → active + reseeded, deployed 1040 FA export verified 407 active, tts
  mirror refreshed export-verbatim 406, runners in BOTH chains — tts flow gate 506 → 509)`
  (payment-cluster draft-to-gate batch order 3 of 3, tts s77 — ONE order, TWO TaxForms: `1040V` + `1040ES`,
  one loader `load_1040v_es.py`).** Gaps re-confirmed 2026-07-13 (`lookup/1040V|1040ES/export/` = 404 ×2).
  PRINT-ONLY pair — the electronic halves shipped in tts s76 (IRSPayment / IRSESPayment), and the spec TIES
  them: an EFW-elected return SUPPRESSES the 1040-V; an ES-debited quarter suppresses its paper voucher
  (both = double-payment guards). **✅ RESEARCH-VERIFIED (2026-07-13, verbatim vs Form 1040-V (2025, Created
  12/22/25) + Form 1040-ES (2026, Feb 12 2026 — the correct vintage: the estimates a TY2025 client pays
  DURING 2026)) → `f1040v_es_source_brief.md`.** **Research catch — the reason the pair is specced: a
  THREE-WAY ADDRESS TRAP (the 2553 address-drift class).** The V chart, the ES chart, and the return address
  all differ, year-watched; **GA mails the V to Charlotte P.O. Box 1214 but the ES vouchers to Charlotte
  P.O. Box 1300**, and the ES package says verbatim "do not mail your estimated tax payments to the address
  shown in the Form 1040 instructions"; USPS-only P.O. boxes (no FedEx/UPS); Guam/USVI bona-fide split.
  Both full state rosters encoded as constants (29 Charlotte + 22 Louisville on the ES chart; 9 southern
  states on the V chart). Also pinned: the ES due dates = the s76 FPYMT-088-11 calendar (Apr/Jun/Sep 15
  2026 + Jan 15 2027; Feb-1 full-pay Q4 skip; farmer Jan-15/Mar-1 options); the RAP test (90/100/110/66⅔
  incl. the farmers-never-110% arm and the $150,000-exactly boundary); joint-voucher bars (NRA/decree/
  different-years/RDP); the overpayment-credit box exclusion; the $100M check cap; postmark = USPS
  PROCESSING date (the new clarification). The ES WORKSHEET math stays the app engine's job — stated
  boundary. **✅ AUTHORED (draft) + SQLite-VALIDATED** (`load_1040v_es.py`, 1040V 6 facts / 3 rules / 6
  lines / 5 diag / 3 scenarios · 1040ES 19 facts / 4 rules / 8 lines / 10 diag / 7 scenarios · 3 FA staged
  DRAFT; `scratchpad/validate_1040v_es.py` = **63 pass / 0 fail** — the GA 1214-vs-1300 drift pin, both
  chart rosters counted, V-emission/EFW-suppression, RAP arms incl. MFS $75k and the 150k-exactly boundary,
  the $1,000 gate + no-liability exception, joint bars, Q4 skip, box exclusion, guard-refusal + twice-run).
  **⛔ GATE-1 PENDING — READY_TO_SEED ships False; NOT seeded, NOT exported.** **Gate-1 walk for Ken
  (W1-W4, recommendations = approve all):** W1 1040-V mechanics + the EFW suppression tie; W2 the
  required-annual-payment diagnostics; W3 dates + voucher mechanics + the ES-debit suppression tie; W4 the
  three-way year-watched address charts (entity_types ['1040']; print-only both). On approval: flip, seed,
  verify both exports, refresh both tts mirrors → dispatch the tts print unit (voucher renders + packet
  emission rules + diagnostics + FA runners/activate/mirror-refresh). ⏭ The batch is COMPLETE at the gate —
  Ken holds THREE walks (WO-28 9465 · WO-29 8888 · WO-30 the pair); one approve-all clears the whole
  payment-cluster RS lane and the tts legs dispatch as a set.

- **✅ [WO-29] Form 8888 · Allocation of Refund · greenfield RS-first · status
  `GAP-CHECKED → research-verified → DRAFTED + SQLite-VALIDATED → Gate-1 APPROVED + SEEDED + EXPORTED
  2026-07-14 → ✅ DONE 2026-07-14 (tts s86 build leg landed: Form8888 singleton mig 0198 + compute_8888
  pinned to the spec scenarios + 12 D_8888_* + f8888 Rev-12-2025 AcroForm print + the IRS8888 MeF
  document w/ Form8888Ind/IND-084 ties + the Payments-tab card; FA-8888-TIE/SPLIT/NOBOND flipped
  draft → active + reseeded, deployed 1040 FA export verified 404 active, tts mirror refreshed
  export-verbatim, runners in BOTH chains — tts flow gate 503 → 506)`
  (payment-cluster draft-to-gate batch order 2 of 3, tts s77).** Gap re-confirmed 2026-07-13
  (`lookup/8888/export/` = 404). MeF channel EXISTS: IRS8888 rides ReturnData1040 (2025v5.3, ~1958 slot,
  DirectDepositInfoGroup maxOccurs=3) — the tts leg on approval = print + MeF document + the 1040 line-35a
  8888-attached checkbox wiring. **✅ RESEARCH-VERIFIED (2026-07-13, verbatim vs Form 8888 Rev. December
  2025 — a CONTINUOUS-USE conversion with instructions included in the 3-page PDF; About page "None at this
  time"; + the TY2025v5.3 business rules CSV + IRS8888.xsd) → `f8888_source_brief.md`.** **Research catches
  (the structural pair):** (1) **the savings-bond purchase program is DISCONTINUED** (Rev. 12-2025 Reminders
  verbatim: TreasuryDirect deposits AND paper bonds; "Form 8888 is now only used to split your direct
  deposit refund between two or more accounts") — face line 4 prints "Reserved for future use", the 2025v5.3
  XSD **dropped the bond group entirely**, every bond business rule is Disabled, and F8888-023 (Active)
  forbids any RefundByCheckAmt value — the spec encodes the retirement as a REFUSAL (R-8888-RETIRED) so no
  tts surface resurrects the old Part II; (2) **EO 14247** — paper refund checks generally end October 2025.
  Both printed adjustment examples pinned as scenarios (decrease $300→$150 strips 3→2→1 to 100/50/0;
  increase +$50 lands on line 3); BFS offsets hit the LOWEST routing number first (a DIFFERENT ordering than
  federal offsets — easy to conflate). **✅ AUTHORED (draft) + SQLite-VALIDATED** (`load_8888.py`, 16 facts /
  6 rules / 16 lines / 12 diag / 8 scenarios / 3 FA staged DRAFT; `scratchpad/validate_8888.py` = **53 pass /
  0 fail** — the two-way tie (sum == L5 == RefundAmt), $1 minimum, single-account routing (return-DD path),
  RTN prefix oracles shared with the S-17b rule, uniqueness/all-zeros, BOTH printed examples recomputed,
  BFS ordering, e-file blockers, guard-refusal + twice-run pins). **⛔ GATE-1 PENDING — READY_TO_SEED ships
  False; NOT seeded, NOT exported.** **Gate-1 walk for Ken (W1-W4, recommendations = approve all):** W1
  allocation math + the single-account route-to-return rule; W2 account hygiene (prefix/17-char/one-box/
  unique) + the 8379 bar + 3-per-year; W3 the RETIRED bond/check surface (refusal, line 4 blank, no
  RefundByCheckAmt ever); W4 the fallback/offset orderings + IRA mechanics as info diagnostics
  (entity_types ['1040']; print + MeF document). On approval: flip, seed, verify export, refresh the tts
  mirror → dispatch the tts unit. ⏭ Batch continues: WO-30 the 1040-V/1040-ES voucher pair.

- **✅ [WO-28] Form 9465 · Installment Agreement Request · greenfield RS-first · status
  `GAP-CHECKED → research-verified → DRAFTED + SQLite-VALIDATED → Gate-1 APPROVED + SEEDED + EXPORTED
  2026-07-14 → DISPATCHED (the tts leg rides the six-leg set, s83 approve-all) → DONE 2026-07-14
  (tts s85: model+compute+17 diagnostics+AcroForm print+IRS9465 MeF document+card shipped; the three
  FAs ACTIVATED here + runners live in tts test_flow_assertions (both chains) + the 1040 mirror
  refreshed export-verbatim, flow gate 500→503)`
  (payment-cluster draft-to-gate batch order 1 of 3, tts s77; the batch plan is the tts REVIEW_QUEUE s76
  recommendation Ken has not yet ratified — this draft parks AT the gate either way).** Gap re-confirmed
  2026-07-13 (`lookup/9465/export/` = 404). UNLIKE 2553/2848 the 9465 HAS a MeF channel — IRS9465 rides
  ReturnData1040 (2025v5.3 InstallmentAgreement family), so the tts leg on approval = print + MeF document
  + diagnostics. **✅ RESEARCH-VERIFIED (2026-07-13, verbatim vs Form 9465 Rev. September 2020 + i9465 Rev.
  July 2024 (About page: Recent Developments "None at this time") + the LIVE IRS payment-plans fee page
  (reviewed 28-Jun-2026) + the TY2025v5.3 1040 business rules CSV + IRS9465.xsd) → `f9465_source_brief.md`.**
  **Research catches:** (1) the fee-currency check (the s67 stale-fee class) surfaced **T.D. 10045 (91 FR
  20902, Apr. 20, 2026)** amending 26 CFR Part 300 AFTER the printed i9465 table — cross-checked against the
  live fee page (post-dating the T.D.): **IA fees UNCHANGED, the July-1-2024 table stands** ($22/$69 OPA,
  $107/$178 form-channel, payroll $178, low-income DDIA-waived/$43/13c-reimbursed, modify $89/$43/$10-OPA;
  YEAR-KEYED — Cornell's §300.1 text is 2016-era, do not cite it); (2) **F9465-019-02 is the s76 EFW tie**
  — line 8 must EQUAL the IRSPayment record's PaymentAmt when both ride the return; (3) the e-file gate is
  narrow (≤$50k, no payroll box, no can't-increase box, payment ≥ line 10, phone required) — every arm a
  published Active reject, refusal-beats-fabrication on the tts side; (4) the line-10 divisor ("divide by
  72.0") prints NO rounding — encoded as whole-dollar CEILING (the full-pay-within-72-months test), flagged
  for the walk. **✅ AUTHORED (draft) + SQLite-VALIDATED** (`load_9465.py`, 46 facts / 9 rules / 46 lines /
  17 diag / 10 scenarios / 3 FA staged DRAFT; `scratchpad/validate_9465.py` = **85 pass / 0 fail** — the
  line-10 ceiling pins (8400→117 · 30000→417 · 50000→695 · exact-division 7200→100), guaranteed/streamlined
  tier boundaries (10,000/10,001 · 25,000/25,001 · 50,000/50,001), the Part II three-condition gate incl.
  each-absent arms, the e-file blocker router arm-by-arm, the full fee ladder, EFW consistency, guard-refusal
  + twice-run pins). **⛔ GATE-1 PENDING — READY_TO_SEED ships False; NOT seeded, NOT exported.** **Gate-1
  walk for Ken (W1-W4, recommendations = approve all):** W1 face math + the line-10 whole-dollar-ceiling
  convention + day 1-28; W2 the agreement-tier router (guaranteed ≤$10k / streamlined ≤$25k or 25k-50k-with-
  DD / 433-F paths) as diagnostics; W3 the F9465-* e-file gate + the EFW PaymentAmt tie (F9465-019-02); W4
  the year-keyed fee schedule + Part II gate + where-to-file (entity_types ['1040']; print + MeF document).
  On approval: flip READY_TO_SEED, seed, verify the deployed export, refresh the tts mirror → dispatch the
  tts unit (render + IRS9465 extract/builder + diagnostics + FA runners/activate/mirror-refresh). ⏭ Batch
  continues: WO-29 Form 8888 → WO-30 the 1040-V/1040-ES voucher pair.

- **▶ [WO-27] Form 2848 · Power of Attorney and Declaration of Representative · greenfield RS-first · status
  `GAP-CHECKED → research-verified → DRAFTED + SQLite-VALIDATED → Gate-1 APPROVED → SEEDED + EXPORTED
  2026-07-12 → ✅ DONE (Gate-2: tts print unit SHIPPED, tts s69 2026-07-12 — input model + L2 preparer
  autofill + D_2848_* code-registered + AcroForm render + FA-2848-FUTURE/SIGN45/CAFFILL ACTIVATED with
  runners + all three tts gate mirrors refreshed; flow gate 475)` (SPINE S-20c). Ken APPROVED W1-W4 (live walk, tts s68 conversation: "Approve" ×2 with 2553);
  sentinel flipped, prod-seeded (34/9/30/17/9 + 3 draft FAs; 16 authority links), `lookup/2848/export/` = 200
  verified (60,684 bytes), tts mirror `server/specs/2848_spec.json` cached from the deployed endpoint; the FA
  export verified clean (drafts excluded — 1120S still serves 32). → DISPATCHED: the tts print unit (pairs with
  WO-26's).** Gap re-confirmed 2026-07-12 (`lookup/2848/export/` = 404). Administrative POA — print-first (mail/fax/
  online at IRS.gov/Submit2848; NO MeF); the app value-add = **line-2 preparer autofill (name/address/CAF/PTIN/
  phone/fax) from the Preparer record**. **✅ RESEARCH-VERIFIED (2026-07-12, verbatim vs FINAL Form 2848 Rev.
  January 2021 + i2848 Rev. September 2021 + the "Items to consider while completing Form 2848" Recent Development
  posted 08-Jul-2026 — FOUR DAYS OLD; About page reviewed 09-Jul-2026) → `f2848_source_brief.md`.** No annual
  reissue; no OBBBA impact. **Research catches:** the fresh Rec. Dev.: **5a entries beyond disclosure/substitution/
  return-signing OR any 5b limitation record the POA as "MODIFIED" on the CAF — blocking the rep's Transcript
  Delivery System access and Tax Pro Account installment agreements; "never check line 4 unless Form 2848 is, in
  fact, a specific-use form"** (encoded as D_2848_MODCAF / D_2848_L4CAF — practitioner-workflow gold); the printed
  where-to-file chart stands (Memphis 855-214-7519 / Ogden 855-214-7522 / Philadelphia Intl 855-772-3156 —
  year-watched, "may change without notice"); the printed "Secure Access" login is superseded but IRS.gov/Submit2848
  stands. **✅ AUTHORED (draft) + SQLite-VALIDATED** (`load_2848.py`, 34 facts / 9 rules / 30 lines / 17 diag /
  9 scenarios / 3 FA staged DRAFT; `scratchpad/validate_2848.py` = **73 pass / 0 fail** — the future-period CAF
  clock (Dec 31 receipt-year + 3: 2026→2029 yes / 2030 no); the 45/60-day rep-signature window incl. the day-45/46
  boundary + rep-signed-first-no-limit; the URP (h) four-condition gate; 4-rep/2-notice-copy counts; the
  modified-CAF and filing-route routers; scenario outputs recomputed; guard-refusal + twice-run pins; the
  Rec-Dev language pinned in the diagnostics). **⛔ GATE-1 PENDING — READY_TO_SEED ships False; NOT seeded, NOT
  exported.** **Gate-1 walk for Ken (W1-W4, recommendations = approve all):** W1 line-3 validity + the future-period
  clock (the "All years" RETURN-the-POA error); W2 rep constraints (4 blocks / 2 notice copies / CAF-PTIN) + the
  unenrolled-preparer representation gate (PTIN + prepared-signed + AFSP both years; 8821 fallback); W3 signature
  mechanics (45/60-day sequence window; e-sign online-only; joint filers separate; entity signer rules as print
  guidance); W4 CAF hygiene (the 08-Jul-2026 modified-CAF + line-4 diagnostics) + line-6 attach-to-retain +
  REVOKE/WITHDRAW info + entity_types ['1040','1120S','1065','1120','1041','709'] print-first scope. On approval:
  flip READY_TO_SEED, seed, verify the deployed export, refresh the tts mirror → dispatch the tts print unit
  (Gate 2; pairs naturally with the 2553 tts leg if both gates clear together). ⏭ Queue: **S-20d 3115 tts app
  build** (RS DONE at WO-23 — buildable now, no gate).

- **▶ [WO-26] Form 2553 · Election by a Small Business Corporation · greenfield RS-first · status
  `GAP-CHECKED → research-verified → DRAFTED + SQLite-VALIDATED → Gate-1 APPROVED → SEEDED + EXPORTED
  2026-07-12 → ✅ DONE (Gate-2: tts print unit SHIPPED, tts s69 2026-07-12 — input model + consent/QSST
  rows + §1362(b) window calculator + D_2553_* code-registered + AcroForm render w/ overflow copies +
  the 2013-30 margin legend + FA-2553-WINDOW/COUNT/8832 ACTIVATED with runners; flow gate 475)`
  (SPINE S-20b). Ken APPROVED W1-W4 (live walk, tts s68 conversation); sentinel flipped,
  prod-seeded (28/8/45/19/10 + 3 draft FAs; 18 authority links — IRC_1361/1362 bound on prod),
  `lookup/2553/export/` = 200 verified (68,235 bytes), tts mirror `server/specs/2553_spec.json` cached from
  the deployed endpoint. → DISPATCHED: the tts print unit (pairs with WO-27's).** Gap re-confirmed 2026-07-12 (`lookup/2553/export/` = 404; first flagged at the WO-22 gap-check). The
  §1362(a) S-election — structural, print-first (paper/fax only, NO MeF channel); pairs with WO-22 (8832 routes
  S-elections here; 2553 is the deemed §301.7701-3(c)(1)(v) classification election). **✅ RESEARCH-VERIFIED
  (2026-07-12, verbatim vs FINAL Form 2553 Rev. December 2017 + i2553 Rev. December 2020 + Rev. Proc. 2026-1 App. A
  fetched from IRB 2026-1 PDF) → `f2553_source_brief.md`.** No annual reissue; no OBBBA impact. **Research catches:**
  the item-Q1 user fee printed in i2553 ($6,200, Rev. Proc. 2021-1 era) is SUPERSEDED → **$5,750** (Rev. Proc. 2026-1
  App. A (A)(3)(a)(ii), verbatim; §1362(b)(5) late-election PLR = $14,500; YEAR-KEYED — re-verify each January);
  the KC/Ogden filing addresses live-verified current (irs.gov where-to-file page reviewed 2026-03-30); Rev. Proc.
  2022-19 §3.03 covers consent/signature defects without a PLR (via Rev. Proc. 2026-1 §6.03(49)). **✅ AUTHORED
  (draft) + SQLite-VALIDATED** (`load_2553.py`, 28 facts / 8 rules / 45 lines / 19 diag / 10 scenarios / 3 FA staged
  DRAFT; `scratchpad/validate_2553.py` = **82 pass / 0 fail** — the §1362(b) 2mo15d corresponding-day deadline math
  reproduces ALL THREE published i2553 examples (Jan 7→Mar 21 · Jan 1→Mar 15 · Nov 8→Jan 22) + the
  no-corresponding-day and leap-Feb edges; timeliness incl. preceding-year + pre-first-day-invalid; the
  spouse/family-aggregation 100-shareholder gate (item G); the Rev. Proc. 2013-30 path chooser (corporate 1-5 /
  6a-c alternative / entity + Part IV / PLR); consent-scope timing; Part II routing; twice-run idempotent; the
  Gate-1 guard proven to refuse). **⛔ GATE-1 PENDING — READY_TO_SEED ships False; NOT seeded, NOT exported.**
  `seed_all` reports the gated loader as a named [FAIL] and keeps going (per-loader try/except) — a prod rebuild is
  unaffected. **Gate-1 walk for Ken (W1-W4, recommendations = approve all):** W1 the eight Who May Elect eligibility
  tests as diagnostics (count reads the AGGREGATED number; one-class-of-stock preparer-asserted INFO); W2 the
  election-window calculator with the three published examples as pinned scenarios; W3 the Rev. Proc. 2013-30
  late-relief path chooser + margin legend + the $14,500 PLR fallback; W4 consent timing/signers + Part II routing
  (Q1 $5,750 year-keyed) + QSST Part III gate + entity_types ['1120S'] print-first scope. On approval: flip
  READY_TO_SEED, seed, verify the deployed export, refresh the tts mirror → dispatch the tts print-unit build
  (Gate 2). tts app build NOT started (WORK_ORDERS rule: no app build until APPROVED). ⏭ Queue continues at
  **Form 2848 (S-20c — same greenfield draft-to-gate recipe)** → 3115 app build (S-20d; RS side DONE at WO-23).

- **▶ [WO-25] SCH_K_1120S 2025-face renumber (early-era audit queue unit #2) · AMENDMENT ·
  status `✅ DONE — seeded + exported 2026-07-11`.** Not greenfield — the s44 face-audit queue
  (Ken-approved retrospective item B) is the standing Gate-1 for the renumber units; same recipe
  as unit #1 (4562, s45). Rebuilt verbatim vs f1120s.pdf (2025) pages 3-4 + i1120s p.40/p.49:
  fabricated 13f FTC → Biofuel producer credit (foreign taxes = 16f); rehab credit 13d → 13c;
  12d/12e fixed (§59(e)(2) / other deductions); added 3b/3c, 8b/8c, 13b/13e, 14a/b, 15a-f,
  16e/16f, the 17a-d split (**17c AE&P dividends → 1099-DIV, never K-1** — i1120s p.40); L18
  formula fixed (combine 1-10 − 11-12e − 16f; ties to **M-1 line 8**, NOT page-1 — i1120s p.49);
  "page 1 line 21" refs → 22. **`load_1120s_full` amendments corrected too: R010 (line 22),
  R018 + D012 (K18 = M-1 L8 — the old "K18 must equal Page 1 Line 21" was a tax-law ERROR).**
  In-loader stale deletes (line "17" catch-all, fact `foreign_tax_credit`); allow-set protects
  the full-loader's K*->Box* rows. 52 facts / 19 rules / 47 face lines / 6 diag / 6 scenarios;
  `lookup/SCH_K_1120S/export/` = 200, content-verified; tts mirror `1120s_sched_k_spec.json`
  refreshed. **NEW audit finding filed: 1120S_PAGE1 + M1 + M2 blocks (load_1120s_full) still
  on pre-Form-7205 numbering (OBI line 21 vs face 22) + a fabricated M-1 excerpt line (1065
  guaranteed payments) — QUEUED in the audit ledger (tts docs/rs_handoff), not drive-by-patched.**

- **▶ [WO-23] Form 3115 · Application for Change in Accounting Method (§481(a)) · greenfield RS-first ·
  status `GAP-CHECKED → research-verified → Gate-1 APPROVED → ✅ DONE → ✅ tts APP BUILD DONE (Gate-2, tts s70
  2026-07-12: print unit shipped; FA-3115-CATCHUP/SPREAD/SCHA ACTIVATED with runners; tts flow gate 484;
  OMB-citation nit → tts REVIEW_QUEUE s70)` (RS DONE 2026-07-06; SPINE S-16, 10th — the LAST S-16 item;
  QUEUE DRAINED).**
  Ken's specialty (§481(a) depreciation catch-up). Gap-check (2026-07-06): no `load_3115*` loader; the only on-disk
  `3115` ref is diagnostic text in `load_1120s_complete.py` (not an authoring surface); `lookup/3115/export/` = GAP
  (server down, cross-checked on-disk — no loader authors form_number 3115). entity_types = 1040/1065/1120/1120S
  (any taxpayer changing an accounting method). NOT a return computation — it's the §446(e)/§481(a) method-change
  APPLICATION: automatic vs non-automatic change (Rev. Proc. 2015-13 procedural + the annual automatic-change list);
  the **§481(a) adjustment** (the catch-up) + spread (positive over 4 years / negative in 1 / de minimis) + DCN;
  Schedule E depreciation/amortization method changes (Ken's wheelhouse — impermissible→permissible, DCN 7).
  **✅ RESEARCH-VERIFIED (2026-07-06, verbatim vs FINAL Form 3115 **Rev. December 2022** + i3115 12-2022 + Rev. Proc.
  2015-13 §7.03 + Rev. Proc. 2025-23 §6.01/DCN 7 + IRC §446(e)/§481(a)) → `f3115_source_brief.md`.** No annual reissue;
  **no OBBBA impact on the procedural machinery/§481(a)** (OBBBA changed depreciation *amounts*, not §446/§481). Spread:
  negative = 1 yr / positive = 4 yrs ratable / positive <$50k = de minimis 1-yr election / under-exam positive = 2 yrs.
  DCN 7 depreciation catch-up = (taken present) − (allowable proposed) as of BOY. **✅ Gate-1 scope walk APPROVED
  2026-07-06 (DECISIONS D-25, all 4 recommended):** Q1 compute the full spread engine; Q2 compute the Schedule E
  depreciation catch-up + DCN 7 routing (direct-entry the 7a–7h descriptors); Q3 compute the Schedule A cash↔accrual
  2a–2h netting; Q4 scope limits (under-exam/5-year/cut-off/≥2-yr) = diagnostic badges. entity_types
  ['1040','1065','1120','1120S']. **✅ AUTHORED + SQLite-VALIDATED** (`load_3115.py`, 19 facts / 5 rules / 6 lines /
  8 diag / 7 tests / 3 FA; `scratchpad/validate_3115.py` = **36 pass / 0 fail** — the spread engine (neg 1 / pos 4 /
  de minimis 1 / under-exam 2 / de minimis precedence), the depreciation catch-up (8k−72k→−64k; 120k−20k→+100k),
  the Schedule A netting (+120k), DCN 7 routing all green; caught 1 topic_name > 255 cap, trimmed). **✅ DONE —
  seeded + exported 2026-07-06** (Ken Gate-1: "approved"; W1-W4 blessed) → **120 TaxForms**; `lookup/3115/export/`
  = 200; seed_all auto-discovers `load_3115` (reconstructable, verified via --dry-run). **Status: ✅ DONE (RS).** tts
  app build = [APP] lane. **⏭ SPINE S-16 federal-forms queue is now FULLY DRAINED (all 10: 8990 → Sch H → 4684 →
  4952 → 8379 → 8814 → 8839 → 709 → 8832 → 3115).** Net-new RS scope now needs the TaxWise forms-usage report or a
  law change (per BUILD_ORDER S-16 closing note).

- **▶ [WO-22] Form 8832 · Entity Classification Election ("check-the-box") · greenfield RS-first · status
  `GAP-CHECKED → research-verified → Gate-1 APPROVED → ✅ DONE` (2026-07-06; SPINE S-16, 9th).** Gap-check: no loader,
  `lookup/8832/export/` = 404 → GAP (2553 also absent). entity_types = [1065,1120,1120S,1040] (the classifications the
  election touches). Structural ELECTION (Treas. Reg. §301.7701-3), not a computation. **✅ RESEARCH-VERIFIED
  (2026-07-06, verbatim vs current FINAL Form 8832 **Rev. December 2013** + §301.7701-3 + Rev. Proc. 2009-41) →
  `f8832_source_brief.md`** (no annual reissue; no OBBBA impact; the printed Cincinnati filing addresses are
  superseded → Kansas City/Ogden). **✅ Gate-1 scope walk APPROVED (DECISIONS D-24, all 4 recommended):** compute the
  Part I eligibility/classification decision tree (per-se corp + 60-month gates) + available classifications; the
  default classification (domestic member-count / foreign limited-liability) + don't-file-if-default TIP; the
  effective-date window clamp (75-before/12-after) + Rev. Proc. 2009-41 late relief; the 2553 boundary + updated-
  address diagnostics. **✅ AUTHORED + SQLite-VALIDATED** (`load_8832.py`, 11 facts / 4 rules / 4 lines / 8 diag /
  7 tests / 3 FA; `scratchpad/validate_8832.py` = **31 pass / 0 fail** — eligibility tree, defaults (domestic/foreign),
  options, clamp all green). **✅ DONE — seeded + exported 2026-07-06** (Ken Gate-1: "Approve — flip, seed, export";
  W1-W4 blessed) → **119 TaxForms**; `lookup/8832/export/` = 200; seed_all auto-discovers `load_8832`
  (reconstructable). **Status: ✅ DONE (RS).** tts app build = [APP] lane. ⏭ Queue continues at **Form 3115**
  (Application for Change in Accounting Method — §481(a); the LAST S-16 item).

- **▶ [WO-21] Form 709 · United States Gift (and GST) Tax Return · greenfield RS-first · status `GAP-CHECKED →
  research-verified → Gate-1 APPROVED → ✅ DONE` (2026-07-06; SPINE S-16, 8th — the biggest module).** Gap-check: no
  loader, `lookup/709/export/` = 404 → GAP. entity_types = 709 (its own gift-tax return). **✅ RESEARCH-VERIFIED
  (2026-07-06, verbatim vs 2025 i709 + §2001(c)/§2010/§2503/§2523/§2631 + OBBBA §70106) → `f709_source_brief.md`.**
  **★ Load-bearing correction: 2025 applicable credit = $5,541,800** (= tentative tax on the $13,990,000 BEA; the
  initial brief's $5,389,800 was the 2024 figure). **★ OBBBA does NOT change TY2025** — 2025 BEA/GST exemption stay
  $13,990,000; the permanent $15M lands 2026+ (year-keyed). **✅ Gate-1 scope walk APPROVED (DECISIONS D-23, all 4
  recommended):** compute the full cumulative engine (§2001(c) schedule + L3-L8 + $5,541,800 credit); Schedule A
  reconciliation + gift-splitting + noncitizen; GST 40%×inclusion-ratio + DSUE→L7; author now with carried
  [UNVERIFIED] structural line-# flags. **⚠ PROVENANCE: the raw f709.pdf face was unfetchable — all dollar figures +
  compute logic + Part 2 lines 1-8 VERIFIED; the Part 1/Sch A recon/Sch D SUB-LINE numbers are [UNVERIFIED]** and
  flagged in the loader + `D_709_UNVERIFIED` for a PDF-face re-verify before the tts build (NC/AL line-# precedent).
  **✅ AUTHORED + SQLite-VALIDATED** (`load_709.py`, 12 facts / 6 rules / 5 lines / 8 diag / 6 tests / 3 FA;
  `scratchpad/validate_709.py` = **32 pass / 0 fail** — the rate schedule ($5,541,800 credit derivation), cumulative
  engine ($20M→$2.4M, cumulative $5M-on-$10M→$404k), Schedule A, gift-splitting, GST all green). **✅ DONE — seeded +
  exported 2026-07-06** (Ken Gate-1: "Approve — flip, seed, export"; W1-W4 blessed) → **118 TaxForms**;
  `lookup/709/export/` = 200; seed_all auto-discovers `load_709` (reconstructable). **Status: ✅ DONE (RS).** tts app
  build = [APP] lane (⚠ re-verify [UNVERIFIED] line #s first). ⏭ Queue continues at **Form 8832** (Entity
  Classification Election / check-the-box).

- **▶ [WO-20] Form 8839 · Qualified Adoption Expenses · greenfield RS-first · status `GAP-CHECKED → research-verified
  → Gate-1 APPROVED → ✅ DONE` (2026-07-06; SPINE S-16, 7th after 8990 + Sch H + 4684 + 4952 + 8379 + 8814).**
  Gap-check: no loader, `lookup/8839/export/` = 404 → GAP. entity_types = 1040. Two parts: §23 adoption CREDIT
  (Part II) + §137 employer-benefit EXCLUSION (Part III). **✅ RESEARCH-VERIFIED (2026-07-06, verbatim vs FINAL 2025
  Form 8839 Created 9/2/25 + i8839 + §23/§36C/§137 + OBBBA §70402/§70403) → `f8839_source_brief.md`.** **★ CONFIRMED
  the 2025 headline: up to $5,000 of the credit is REFUNDABLE per child (OBBBA, first year partly refundable) — new
  L11a/11b/11c → L13 → 1040 L30.** 2025 indexed: max **$17,280** / phaseout **$259,190-$299,190** / divisor **$40,000**
  / refundable cap **$5,000**. ⚠ Provenance: the $5,000 indexing is statutory (§36C, $5,120 for 2026), NOT in i8839.
  **✅ Gate-1 scope walk APPROVED (DECISIONS D-22, all 4 recommended):** Part II full compute incl. refundable split;
  Part III full exclusion; special-needs override + coordination diagnostics; year-keyed $5,000 w/ provenance +
  carryforward diagnostics. **✅ AUTHORED + SQLite-VALIDATED** (`load_8839.py`, 9 facts / 5 rules / 6 lines / 8 diag /
  6 tests / 3 FA; `scratchpad/validate_8839.py` = **30 pass / 0 fail** — refundable split, phaseout boundaries,
  tax-limit carryforward, exclusion all green). **✅ DONE — seeded + exported 2026-07-06** (Ken Gate-1: "Approve —
  flip, seed, export"; W1-W4 blessed) → **117 TaxForms**; `lookup/8839/export/` = 200; seed_all auto-discovers
  `load_8839` (reconstructable). **Status: ✅ DONE (RS).** tts app build = [APP] lane. ⏭ Queue continues at
  **Form 709** (United States Gift (and GST) Tax Return — a bigger new module).

- **▶ [WO-19] Form 8814 · Parents' Election to Report Child's Interest & Dividends · greenfield RS-first · status
  `GAP-CHECKED → research-verified → Gate-1 APPROVED → ✅ DONE` (2026-07-06; SPINE S-16, 6th after 8990 + Sch H +
  4684 + 4952 + 8379).** Gap-check: no loader, `lookup/8814/export/` = 404 → GAP (**`8615` already in prod at 200** —
  the sibling). entity_types = 1040. 8814 = the §1(g)(7) election for the PARENT to report the child's income instead
  of the child filing 8615 — **closes the existing 8615 spec's `D_8615_004` RED-defer loop.** **✅ RESEARCH-VERIFIED
  (2026-07-06, verbatim vs FINAL 2025 Form 8814 Created 3/19/25 + i8814) → `f8814_source_brief.md`.** 2025 indexed
  figures: base **$2,700** / not-taxed **$1,350** / flat second-tier tax **$135** / don't-file ceiling **$13,500**.
  ⚠ Provenance: the 8615/§1(g) relationship is cited to §1(g)/Pub 929, NOT i8814 (the 8814 sources don't mention it).
  **✅ Gate-1 scope walk APPROVED (DECISIONS D-21, all 4 recommended):** Part I full allocation + proportional QD/
  cap-gain carries; compute `can_elect` + the two gates; 8615 cross-ref cited to §1(g)/Pub 929; Part II tax + one
  8814 form [1040] + multi-child. **✅ AUTHORED + SQLite-VALIDATED** (`load_8814.py`, 13 facts / 4 rules / 6 lines /
  7 diag / 6 tests / 3 FA; `scratchpad/validate_8814.py` = **26 pass / 0 fail** — allocation conservation + Part II
  $135/10% + boundary all green). **✅ DONE — seeded + exported 2026-07-06** (Ken Gate-1: "Approve — flip, seed,
  export"; W1-W4 blessed) → **116 TaxForms**; `lookup/8814/export/` = 200; seed_all auto-discovers `load_8814`
  (reconstructable). **Status: ✅ DONE (RS).** tts app build = [APP] lane. ⏭ Queue continues at **Form 8839**
  (Qualified Adoption Expenses).

- **▶ [WO-18] Form 8379 · Injured Spouse Allocation · greenfield RS-first · status `GAP-CHECKED → research-verified →
  Gate-1 APPROVED → ✅ DONE` (2026-07-06; SPINE S-16, 5th after 8990 + Sch H + 4684 + 4952).** **Confirmed the form
  is 8379** (Ken's BUILD_ORDER "8679" is a typo — no such IRS form; both 404). Gap-check: no loader, not in the
  114-form prod set → GAP. entity_types = 1040. NOT a tax-computation form — it ALLOCATES joint-return items (Part
  III cols a/b/c) so the IRS computes the injured spouse's share of a joint overpayment offset (§6402) against the
  OTHER spouse's separate past-due debt. **✅ RESEARCH-VERIFIED (2026-07-06, verbatim vs current FINAL Form 8379
  Rev. 11-2023 + i8379 Rev. 11-2024 + §6402) → `f8379_source_brief.md`** (no annual reissue; no OBBBA impact).
  **✅ Gate-1 scope walk APPROVED (DECISIONS D-20, all 4 recommended):** compute the Part I decision tree →
  is_injured_spouse + stop-reasons; validate Part III col(a)=(b)+(c) + allocation-rule diagnostics (refund share NOT
  estimated — IRS computes it); 9 community-property states + L5-skip override; 8379-vs-8857 + 3yr/2yr + Part IV +
  processing diagnostics. **✅ AUTHORED + SQLite-VALIDATED** (`load_8379.py`, 16 facts / 4 rules / 4 lines / 8 diag /
  7 tests / 3 FA; `scratchpad/validate_8379.py` = **29 pass / 0 fail** — decision tree, allocation constraint,
  community-property list all green). **✅ DONE — seeded + exported 2026-07-06** (Ken Gate-1: "Approve — flip, seed,
  export"; W1-W4 blessed) → **115 TaxForms**; `lookup/8379/export/` = 200; seed_all auto-discovers `load_8379`
  (reconstructable). **Status: ✅ DONE (RS).** tts app build = [APP] lane. ⏭ Queue continues at **Form 8814**
  (Parents' Election to Report Child's Interest & Dividends).

- **▶ [WO-17] Form 4952 · Investment Interest Expense Deduction · greenfield RS-first · status `GAP-CHECKED →
  research-verified → Gate-1 APPROVED → ✅ DONE` (2026-07-06; SPINE S-16, 4th after 8990 + Sch H + 4684).**
  Gap-check: no `load_4952*` loader; `lookup/4952/export/` = 404, not in the 113-form prod set → GAP.
  **✅ RESEARCH-VERIFIED (2026-07-06, verbatim vs FINAL 2025 Form 4952 Created 5/28/25 — no separate i4952,
  instructions on pp. 3-4 — + §163(d)) → `f4952_source_brief.md`.** §163(d) UNCHANGED by OBBBA for TY2025 (that's
  §163(j)/8990, a different provision). **✅ Gate-1 scope walk APPROVED (DECISIONS D-19, all 4 recommended):** full
  Parts I-III compute (L8 = min(L3, L6), L7 indefinite carryforward); 4g election mechanic + rate-tradeoff
  diagnostic; entity_types [1040,1041] + routing/filing-exception diagnostics; L5 misc-itemized + investment-interest
  exclusion diagnostics. **✅ AUTHORED + SQLite-VALIDATED** (`load_4952.py`, 9 facts / 5 rules / 5 lines / 7 diag /
  5 tests / 3 FA; `scratchpad/validate_4952.py` = **26 pass / 0 fail** — incl. the 4g counterfactual: electing $5k
  frees $4,500 of deduction). **✅ DONE — seeded + exported 2026-07-06** (Ken Gate-1: "Approve — flip, seed,
  export"; W1-W4 blessed) → **114 TaxForms**; `lookup/4952/export/` = 200; seed_all auto-discovers `load_4952`
  (reconstructable). **Status: ✅ DONE (RS).** tts app build = [APP] lane. ⏭ Queue continues at **Form 8379**
  (Injured Spouse Allocation).

- **▶ [WO-16] Form 4684 · Casualties & Thefts · greenfield RS-first · status `GAP-CHECKED → research-verified →
  Gate-1 APPROVED → ✅ DONE` (2026-07-05/06; SPINE S-16, 3rd after 8990 + Schedule H).** Gap-check: no `load_4684*`
  loader (downstream Sch A / Sch D / 4797 / 8829 route TO 4684 but none authors it); `lookup/4684/export/` = 404 →
  GAP. **✅ RESEARCH-VERIFIED (verbatim vs FINAL 2025 Form 4684 Created 9/26/25 + i4684 updated 30-Apr-2026 + Pub 547
  + §165 + Rev. Proc. 2009-20) → `f4684_source_brief.md`.** Load-bearing law: the **§165(h)(5) federally-declared-
  disaster limitation is STILL in effect for TY2025**; OBBBA EXTENDED the qualified-disaster special rules (window to
  **9/2/2025**) + ADDED a financial-scam theft-loss avenue (Section B) — did NOT repeal the base limitation or add
  state-declared disasters. **✅ Gate-1 scope walk APPROVED (DECISIONS D-18, all 4 recommended):** Section A full
  compute incl. qualified-disaster $500/no-AGI/std-deduction path (year-keyed window); Section B Part I + Part II
  §1231/ordinary routing to 4797 L3/L14; Section C Ponzi 95%/75% safe harbor computed, Section D §165(i) = diagnostic;
  entity_types 1040/1065/1120S/1120 + financial-scam diagnostic. **✅ AUTHORED + SQLite-VALIDATED** (`load_4684.py`,
  20 facts / 5 rules / 6 lines / 8 diag / 7 tests / 3 FA; `scratchpad/validate_4684.py` = **29 pass / 0 fail** — FDD
  gate, qualified-disaster $500, total-destruction full basis, §1231 routing, Ponzi 95/75 all green). **✅ DONE —
  seeded + exported 2026-07-06** (Ken Gate-1: "Approve — flip, seed, export"; W1-W4 blessed) → **113 TaxForms**;
  `lookup/4684/export/` = 200; seed_all auto-discovers `load_4684` (reconstructable). **Status: ✅ DONE (RS).** tts
  app build = [APP] lane. ⏭ Queue continues at **Form 4952** (Investment Interest Expense Deduction).

- **▶ [WO-15] Schedule H · Household Employment Taxes (1040) · greenfield RS-first · status `GAP-CHECKED →
  research-verified → Gate-1 APPROVED → ✅ DONE` (2026-07-05; SPINE S-16, 2nd item after 8990).** Next in Ken's
  federal-forms queue. Gap-check: no `load_sch*h*` loader; `SCHEDULE_H` not in the 111-form prod set → GAP.
  entity_types = 1040. **✅ RESEARCH-VERIFIED (2026-07-05, verbatim vs FINAL 2025 Schedule H Created 4/15/25 +
  i1040sh + Pub 926 + Fed. Reg. 2026-00342) → `sch_h_source_brief.md`.** Research CAUGHT the load-bearing
  correction: **2025 cash-wage trigger = $2,800** (not the stale $2,700). OBBBA did NOT change Sch H
  structure/rates for TY2025 — only indexed dollars + the CA/VI credit-reduction list.
  **✅ Gate-1 scope walk APPROVED (DECISIONS D-17, all 4 recommended):** FUTA Section A + credit-reduction path
  (year-keyed CA 1.2% / VI 4.5%, multi-state table direct-entry); gating tests + exclusion diagnostics; one
  `SCHEDULE_H` form entity_types ['1040'] + Part IV/EIN diagnostics; full Part I compute + $176,100 SS-base
  diagnostic. **✅ AUTHORED + SQLite-VALIDATED** (`load_sch_h.py`, 15 facts / 5 rules / 7 lines / 7 diag / 6 tests /
  3 FA; `scratchpad/validate_sch_h.py` = **31 pass / 0 fail** — incl. CA 1.8% / VI 5.1% net FUTA + the $2,800/$1,000
  gating boundaries). **✅ DONE — seeded + exported 2026-07-05** (Ken Gate-1: "Approve — flip, seed, export";
  W1-W4 blessed) → **112 TaxForms**; `lookup/SCHEDULE_H/export/` = 200; seed_all auto-discovers `load_sch_h`
  (reconstructable). **Status: ✅ DONE (RS).** tts app build = [APP] lane. ⏭ Queue continues at **Form 4684**
  (Casualties & Thefts).

- **▶ ACTIVE — [WO-14] Form 8990 · §163(j) business-interest limitation · greenfield RS-first · status
  `GAP-CHECKED → DRAFTING (research)` (opened 2026-07-05; SPINE S-16, first of Ken's federal-forms queue).**
  Finishes the 1120 module's biggest deferred leg. Gap-check: `8990` not in the 92-form federal prod set → GAP.
  entity_types = 1120/1065/1120S/1040 (any taxpayer with business interest expense subject to the limit). OBBBA
  restored the **EBITDA-basis ATI** for TY2025 (add back depreciation/amortization/depletion) — the compute heart;
  $31M §448(c) small-business exemption; 30% ATI + BII + floor-plan; indefinite disallowed-BIE carryforward;
  §163(j)(7) excepted businesses; Part II partnership EBIE/ETI + Part III S-corp pass-through items.
  **✅ RESEARCH-VERIFIED (2026-07-05, verbatim vs FINAL Form 8990 Rev. 12-2025 Created 9/9/25 + i8990 Rev. 12-2025
  + §163(j)) → `f8990_source_brief.md`.** Confirmed **line 11 = the EBITDA add-back** (dep/amort/depletion, an
  ADDITION for TY2025, reinstated by OBBBA — was suspended 2022-24); Part I ATI (L22) → 30% limit (L26) → total
  limit L29 = 30%ATI+BII+floor-plan → allowable L30 → disallowed carryforward L31 (indefinite); Part II partnership
  EBIE/ETI (L32-37); Part III S-corp ETI (L38-42, no EBIE); Sch A/B feeders; $31M §448(c) exemption. Cite OBBBA
  effective date to P.L. 119-21 + i8990 (Cornell lags).
  **✅ Gate-1 scope walk APPROVED (DECISIONS D-16, all 3 recommended):** full Part I compute; Part II/III formulas +
  direct-entry Sch A/B; $31M gate + §163(j)(7) diagnostic. **✅ AUTHORED + SQLite-VALIDATED** (`load_8990.py`, 15
  facts / 6 rules / 8 lines / 5 diag / 6 tests / 3 FA; `scratchpad/validate_8990.py` = **19 pass / 0 fail** — incl.
  the EBIT counterfactual: no L11 add-back → disallowed 180k vs 90k). **✅ DONE — seeded + exported 2026-07-05**
  (Ken Gate-1: "Approve — flip, seed, export"; W1-W3 blessed) → **111 TaxForms**; `lookup/8990/export/` = 200;
  seed_all reconstructable. **Status: ✅ DONE (RS).** ⏭ Queue continues at **Schedule H** (post-context-clear).
  **⏭ Federal-forms queue AFTER 8990 (SPINE S-16, Ken's order — author each via the full front door):**
  Schedule H → Form 4684 → Form 4952 → Form 8379 (Ken wrote "8679" = 8379) → Form 8814 → Form 8839 → Form 709 →
  Form 8832 → Form 3115. Take the TOP unchecked item at each boot. **Ken clears context after 8990 seeds.**

- **▶ ACTIVE — [WO-09] S-11 · 1041 module · greenfield RS-first · status `GAP-CHECKED → research-verified → Gate-1 scope LOCKED → DRAFTING (authoring)` (opened 2026-07-05).**
  Gap-check run against live prod (96 forms) — **all five authoring surfaces are 404 GAPs**; the module is fully
  greenfield (no `load_1041_*` loaders; the only on-disk `1041` refs are the boundary-diag Sch I note + the *receiving*
  side in `load_1040_schedule_k1.py` where a 1040 imports a trust K-1). Required set from BUILD_ORDER S-11:
  - **Spine** (`1041`) — entity types / 2025 §1(e) rate schedule / §642(b) exemptions → **GAP**
  - **DNI / IDD / Schedule B** (`1041` or `1041_SCHB`) — §643(a) DNI, §651/§661 distribution deduction, tier/separate-share → **GAP**
  - **Schedule G** (`1041_SCHG`) — tax computation, cap-gain rates, §1411 NIIT on trusts/estates → **GAP**
  - **K-1 (Form 1041)** (`SCHEDULE_K1_1041`) — beneficiary distributive shares + character pass-through → **GAP**
  - **GA Form 501** (`GA501`) — Georgia fiduciary income tax return → **GAP**
  - **Schedule I (AMT)** — **RED-defer diagnostic only** (D-2, ruled 2026-07-04; do NOT author the compute).
  - **✅ Research-verified** (4 passes, verbatim vs FINAL IRS/GA sources) → **`f1041_source_brief.md`**. Rev. Proc.
    2025-32 confirmed = TY2026 (2024-40 governs TY2025). PDF text dumps cached in `scratchpad/` for excerpt seeding.
  - **✅ Gate-1 scope LOCKED (2026-07-05, DECISIONS D-10):** core 4 + **ESBT** computed; grantor = structure/
    grantor-letter; PIF → routed to the 5227 leg; bankruptcy = RED-defer. **FULL** distribution engine (§662 tiers
    + §663(c) separate-share + §663(b) 65-day + character retention). Cap-gains-in-DNI = direct-entry + 3-circumstance
    diagnostic. **GA 501 resident-only v1** (Sch 4 NR + conformity add-backs deferred). Sch I AMT = RED-defer (D-2).
    K-1 full verbatim codes. Form keys: `1041` (spine+SchB+SchG) + `SCHEDULE_K1_1041` + `GA501`.
  - **➕ Spun off — [WO-10] Form 5227 split-interest trusts** (PIF + CRT/CRAT/CRUT + CLT, §664(b) 4-tier) = its own
    dedicated leg with its own research pass + source brief, AFTER the 1041 core. Enters this queue as a new order when reached.
  - **Authoring legs (this order):** (a) `1041` spine+SchB+SchG · (b) `SCHEDULE_K1_1041` · (c) `GA501`. Each:
    author `READY_TO_SEED=False` → SQLite-validate (CharField caps: rule/diagnostic/assertion_id ≤ 20) → Ken review
    walk → seed → export = 200.
  - **✅ ALL 3 LEGS DONE — S-11 1041 module RS authoring COMPLETE 2026-07-05** (Ken Gate-1 approved each; every
    guard flipped after its review walk). Prod: **99 TaxForms / 471 FlowAssertions / 859 FormRules**.
    - **(a) `1041` spine** — `load_1041_spine.py`; 35 facts / 15 rules / 39 lines / 11 diag / 9 tests / 6 FA;
      `validate_1041.py` 17/0; `lookup/1041/export/` = 200. (page-1 + Sch B DNI/IDD engine + Sch G tax.)
    - **(b) `SCHEDULE_K1_1041`** — `load_1041_schedule_k1.py`; 29 facts / 7 rules / 17 lines / 6 diag / 6 tests /
      4 FA; full verbatim box codes; `validate_1041_k1.py` 18/0; `lookup/SCHEDULE_K1_1041/export/` = 200.
    - **(c) `GA501`** — `load_ga501.py`; 19 facts / 7 rules / 14 lines / 8 diag / 5 tests / 4 FA; resident-only;
      `validate_ga501.py` 16/0; `lookup/GA501/export/` = 200.
  - **Status: ✅ DONE (RS).** Sch I AMT RED-defer (D-2) satisfied via `D_1041_AMT`. **tts app build = the [APP] lane
    (dispatch when CC has a lane).** Next 1041-family authoring order: **[WO-10] Form 5227** split-interest trusts.
- **▶ ACTIVE — [WO-10] Form 5227 · Split-Interest Trust Information Return · greenfield RS-first · status
  `GAP-CHECKED → DRAFTING (research)` (opened 2026-07-05, spun off from S-11 D-10).**
  Gap-check: all candidate keys (`5227`, `CRAT`, `CRUT`, `POOLED_INCOME_FUND`, `5227_SCHA`) 404 GAP (99 forms);
  greenfield (only on-disk ref = the spine's `D_1041_PIF` routing note). Covers the §664 split-interest family:
  charitable remainder trusts (CRAT §664(d)(1) / CRUT §664(d)(2)), pooled income funds (§642(c)(5)), and
  §4947(a)(2) split-interest trusts; the **§664(b) four-tier character-ordering** of CRT distributions is the
  compute heart. **✅ Research-verified** (3 passes, verbatim vs FINAL 2025 Form 5227 Created 5/7/25 + i5227
  Dec 3 2025 + IRC §664/§642(c)/§4947 + Reg §1.664-1(d)) → **`f5227_source_brief.md`**. Caught the stale
  Part IV-A/IV-B layout (2025 = flat Part I–IX + Schedule A I–V).
  - **✅ Gate-1 scope LOCKED (2026-07-05, DECISIONS D-11):** CRAT + CRUT compute the §664(b) tier engine
    (**tier-level** — ordinary→capgain→other→corpus + accumulation carryforward + category-isolation netting;
    capital gain as ONE class, no within-Tier-2 rate split); PIF/CLT/§4947-other = structure + diagnostics;
    CRT qualification (5–50% payout / 10% remainder / 5% exhaustion) = diagnostic (funding-time, no §7520/
    mortality compute); §664(c)(2) **100% UBTI excise** COMPUTED (year-keyed post-2006) + Form 4720 route +
    Part VIII §4941/4943/4944/4945 screening diagnostics. One consolidated `5227` form.
  - **✅ DONE — seeded + exported 2026-07-05** (Ken Gate-1: "Approve — flip, seed, export"; W1-W4 blessed).
    `load_5227.py`: 23 facts / 8 rules / 12 lines / 11 diag / 6 tests / 4 FA; all rules cited (5 sources);
    SQLite-validated `scratchpad/validate_5227.py` 20/0. Seeded → **100 TaxForms / 475 FlowAssertions / 867 FormRules**;
    `lookup/5227/export/` = 200. **Status: ✅ DONE (RS).** tts app build = [APP] lane. The 1041 family (S-11 + WO-10)
    is now fully authored on the RS side. Carried [UNVERIFIED] clauses noted in the loader for re-pull if a deeper compute leg is scoped.
- **▶ ACTIVE — [WO-11] S-13 · 1120 C-corp module · greenfield RS-first · status `INTAKE → GAP-CHECKED → DRAFTING (research)` (opened 2026-07-05, DECISIONS D-12; Ken: "build 1120").**
  Ken added the **C corporation (Form 1120)** to the season-one plan (a scope-add beyond the original 1040/1120-S/1065/1041
  set — a NEW entity type nothing else covers). Ran the front door from step 1.
  **✅ GAP-CHECK (2026-07-05, live prod 100 forms):** required set (BUILD_ORDER S-13) vs coverage —
  - **Spine** (`1120`, page-1 income L1–11 / deductions L12–29 / taxable income L30 / §11 21% tax L31) → **GAP**
  - **Schedule C** (`1120_SCHC`, dividends + §243/§245A DRD) → **GAP**
  - **Schedule J** (`1120_SCHJ`, tax computation Part I + payments Part II) → **GAP**
  - **Schedule K** (other information) → **GAP**  ·  **Schedule L** (balance sheet) → **GAP**
  - **Schedule M-1 / M-2** (book-tax recon / unappropriated R/E) → **GAP**
  - **GA Form 600** (`GA600`, net income + net worth tax) → **GAP** (only the S-corp `GA600S` exists)
  - **✅ CONFIRMED already cover C-corp `1120`** (no authoring): `1125A` `['1120S','1065','1120']` (COGS),
    `1125E` `['1120S','1120']` (officer comp), `3800`, `4562`, `4797`, `8949`, `7004` — all carry `1120` in entity_types
    (verified live, like the 1065-core 8825/4562/3800 confirmation).
  - **➡ 8 gaps to author.**
  - **✅ RESEARCH-VERIFIED (2026-07-05, 3 parallel passes, verbatim vs FINAL sources) → `f1120_source_brief.md`.**
    Federal face: Form 1120 (2025) **Created 9/26/25**; caught OBBBA restructure — Sch J is now one continuous list
    to L23 (no Part I/II), page-1 total tax = Sch J **L12**; new L25 (Form 7205), L32 (§1062/Form 1062). IRC: §11 21%,
    §243 50/65/100% DRD, §246(b) TI-limit + loss exception, §172 80%/no-carryback/indefinite, **§163(j) EBITDA basis
    RESTORED for TY2025 (OBBBA)** + $31M §448(c), §55 CAMT 15%/$1B/Form 4626, §541 PHC 20%, §531 AET 20%/$250k-$150k.
    GA 600: rate **5.19%** (HB 111), net worth tax **Schedule 2** table (≤$100k=$0, max $5,000 over $22M), single-factor
    gross-receipts (6 dec), conformity Jan 1 2025 (HB 290, OBBBA not adopted). **⚠ GA §179 2025 = $1,250,000/$3,130,000**
    (GA indexes; the $1.05M/$2.62M in CLAUDE.md is the 2021 figure — STALE; flag + check GA700/GA600S).
  - **✅ Gate-1 scope walk APPROVED 2026-07-05 (DECISIONS D-13, all 4 recommended):** form shape = spine + 2
    (`1120` / `1120_SCHL` / `GA600`); Sch C = domestic DRD + §246(b) limit; federal = NOL 80% compute, §163(j)/
    CAMT/PHC/AET/§1062 screen+route; GA 600 = full (income + net worth + depr delta).
  - **✅ AUTHORED + SQLite-VALIDATED 2026-07-05 (READY_TO_SEED=False, awaiting Ken review walk W1-W10):**
    `load_1120_spine.py` (`1120`, 35 facts / 11 rules / 11 lines / 10 diag / 8 tests / 4 FA),
    `load_1120_schl.py` (`1120_SCHL`, 27 / 7 / 5 / 5 / 6 / 3), `load_ga600.py` (`GA600`, 15 / 6 / 6 / 5 / 8 / 3).
    `scratchpad/validate_1120.py` = **55 pass / 0 fail** (caps clean 159 checked; all rules cited; DRD 50/65/100
    + §246(b) limit + loss exception, §172 NOL 80%, §11 21%, Sch L balance/M-1/M-2 ties, GA 5.19% + §179 delta
    + net worth table all green).
  - **✅ DONE — seeded + exported 2026-07-05** (Ken Gate-1: "Approve — flip, seed, export"; W1-W10 blessed).
    Flipped all three guards → seeded to prod → **103 TaxForms**; `lookup/{1120,1120_SCHL,GA600}/export/` all = 200
    (65 KB / 24 KB / 24 KB; facts/rules/line_map/diagnostics all present). Spun off the stale GA §179 fix
    (`task_1c8d891e`: CLAUDE.md $1.05M/$2.62M → $1.25M/$3.13M + re-check GA700/GA600S). **Status: ✅ DONE (RS).**
    tts app build = [APP] lane. Carried [UNVERIFIED] flags noted in the loaders (§11 label, §246(b) combined
    50/65 worksheet, TY2026 §163(j) capitalized-interest) for re-pull if a deeper compute leg is scoped.
    Confirmed covering 1120 (no authoring): 1125-A/1125-E/3800/4562/4797/8949/7004.
- **▶ ACTIVE — [WO-12] State C-corp batch · SC1120 + AL Form 20C + NC CD-405 · greenfield RS-first · status
  `GAP-CHECKED → DRAFTING (research)` (opened 2026-07-05; Ken: "state C corp rules", batch the reuse-states).**
  Extends the federal 1120 module (WO-11) to GA's income-tax neighbors' C-corp returns. **✅ GAP-CHECK (live prod
  103 forms):** all three are GAPs — SC has `SC1120S` (S-corp) but no `SC1120` (C-corp); AL/NC have only their
  individual returns (`AL_FORM_40`, `NC_D400`). Ken picked SC1120 first + BATCH the three reuse-states (each reuses
  conformity sources already seeded: SC ← `load_sc1040`/`load_sc_passthrough`, AL ← `load_al_form40`, NC ←
  `load_nc_d400`; via `EXISTING_SOURCES_TO_REFERENCE`). FL F-1120 / TN FAE 170 = later greenfield orders.
  - **SC1120** — SC C-corp income tax (5% flat) + license fee (capital × .001 + $15, min $25); federal-TI start;
    single-factor apportionment; §168(k)/§179 non-conformity. Reuses SC1120S structure. → **GAP**
  - **AL Form 20C** — AL corporate income tax (6.5%); federal-TI start; apportionment; the AL federal-income-tax
    deduction question (verify C-corp treatment); §168(k)/§179. → **GAP**
  - **NC CD-405** — NC C-corp income tax (phasing down — verify TY2025 rate); federal-TI start; single sales-factor
    apportionment; NC 85% bonus add-back (Jan 1 2023 conformity freeze). → **GAP**
  - **✅ RESEARCH-VERIFIED (2026-07-05, 3 parallel passes, verbatim vs FINAL 2025 sources) → `state_ccorp_batch_source_brief.md`.**
    SC1120 (Rev. 7/2/25): 5% flat + license fee ($15 + capital×.001, min $25) + §168(k) decouple + §179
    $1.25M/$3.13M (12/31/2024 conformity); **⚠ H.3368 OBBBA-pending = live wire, retroactive TY2025 risk, SC
    deadline extended to Oct 15 2026**. AL 20C: 6.5% + **⚠ FIT deduction NOT repealed** (Amendment 662, L11a/Sch E —
    premise overturned) + **AL CONFORMS to §168(k)/§179** (no add-back; GILTI §40-18-35.2 + §174 §40-18-62 are the
    real decouples) + single sales factor; due May 15 (1 mo after federal). NC CD-405: income **2.25%** (S.B. 105
    phase-down) + **franchise tax** ($1.50/$1,000 net worth, first $1M cap $500, min $200, **net-worth-only base** —
    3-way test repealed 2017) + 85% bonus add-back + §179 $25k/$200k + single sales factor 4-dec (Jan 1 2023 conformity).
  - **✅ Gate-1 scope walk APPROVED 2026-07-05 (DECISIONS D-14, all 4 recommended):** full compute all three;
    AL FIT deduction = compute apportioned; SC = author current law + H.3368 flag; AL GILTI/§174 = diagnostic+direct-entry.
  - **✅ AUTHORED + SQLite-VALIDATED 2026-07-05 (READY_TO_SEED=False, awaiting Ken review walk W1-W9):**
    `load_sc1120.py` (`SC1120`, 11 facts / 6 rules / 5 lines / 5 diag / 6 tests / 3 FA), `load_al_form20c.py`
    (`AL_FORM_20C`, 12 / 5 / 5 / 6 / 4 / 2), `load_nc_cd405.py` (`NC_CD405`, 12 / 6 / 4 / 5 / 6 / 3).
    `scratchpad/validate_state_ccorp.py` = **41 pass / 0 fail** (caps clean 88; all rules cited; SC 5%+license+§179,
    AL 6.5%+apportioned FIT+GILTI, NC 2.25%+net-worth franchise table+85% bonus/§179 all green).
  - **✅ DONE — seeded + exported 2026-07-05** (Ken Gate-1: "Seed all three now"; W1-W9 blessed). Flipped all three
    guards → seeded → **106 TaxForms**; `lookup/{SC1120,AL_FORM_20C,NC_CD405}/export/` all = 200 (22/20/19 KB).
    Auto-discovered by `seed_all` (reconstructable). **Status: ✅ DONE (RS).** tts app build = [APP] lane.
    **⚠ SC carried caveat:** authored to the ENACTED 12/31/2024 law + `D_SC1120_H3368` flag; if H.3368 passes
    (adopting OBBBA retroactively for TY2025), SC1120 needs a §179/bonus amend ($2.5M/$4M, drop the add-back) —
    Ken accepted. FL F-1120 / TN FAE 170 = later greenfield orders.
- **▶ ACTIVE — [WO-13] NC + AL pass-through entity batch · greenfield RS-first · status `GAP-CHECKED → DRAFTING
  (research)` (opened 2026-07-05; Ken: "do the NC + AL"; SPINE S-15).** Completes the adjacent-state PASS-THROUGH
  track (SC pass-through done via SC1065/SC1120S/PTET, D-9; the individual + C-corp sides done for AL/NC/SC).
  **✅ GAP-CHECK (live prod 106 forms):** all pass-through keys GAP — NC has NC_D400(1040)+NC_CD405(1120) but no
  D-403/CD-401S; AL has AL_FORM_40(1040)+AL_FORM_20C(1120) but no Form 65/20S. Required set:
  - **NC D-403** (partnership, 1065) + **NC CD-401S** (S-corp, 1120S) + the **NC Taxed PTE** election
  - **AL Form 65** (partnership, 1065) + **AL Form 20S** (S-corp, 1120S) + the **Alabama Electing PTE** tax (Act 2021-1)
  - Reuse: NC 85% bonus/§179 $25k/$200k + Jan 1 2023 conformity (as NC D-400/CD-405); AL conforms §168(k)/§179 +
    GILTI/§174 (as AL 20C). Template = `load_sc_passthrough.py` (two forms one loader) + the SC PTET pattern.
  - ⚠ Each state's PTET DIFFERS — verify, never clone GA: NC Taxed-PTE (rate = individual 4.25% for 2025? owner-side
    DEDUCTION not credit — verify) vs AL Electing-PTE (5%, owner-side CREDIT). NC franchise applies to S-corps (CD-401S).
  - **✅ RESEARCH-VERIFIED (2026-07-05, 2 parallel passes, verbatim vs FINAL 2025 NCDOR/ALDOR) → `nc_al_passthrough_source_brief.md`.**
    **NC Taxed PTE:** 4.25% (individual rate); owner side = **DEDUCTION** (income removed from NC AGI via NC-PE);
    base = resident full + nonresident NC-source; 85% bonus/§179 $25k/$200k decouple; **CD-401S computes NC
    franchise** ($1.50/$1,000, $500 first-$1M cap, $200 min — as CD-405); nonresident withholding 4.25%; conformity
    Jan 1 2023; due Apr 15. **AL Electing PTE:** 5%; owner side = **refundable CREDIT** (Sch EPT-C); computed on
    **Form EPT** (65/20S Sch K L23/L25 reference it); election = checkbox + Form EPT + >50% consent; **AL CONFORMS
    to §168(k)/§179** (no add-back); composite PTE-C 5%; Form 20S non-electing = LIFO/BIG/excess-passive only; BPT
    separate; due Mar 15. ⚠ AL conformity item-by-item (not blanket). [UNVERIFIED] exact NC/AL line numbers (PDFs
    didn't extract) — re-pull before seeding.
  - **✅ Gate-1 scope walk APPROVED 2026-07-05 (DECISIONS D-15, all 4 recommended):** full compute both states;
    encode NC deduction + AL credit; AL non-electing S-corp taxes = diagnostic+direct-entry; 2 loaders state-paired.
  - **✅ AUTHORED + SQLite-VALIDATED 2026-07-05 (READY_TO_SEED=False, awaiting Ken review walk W1-W6):**
    `load_nc_passthrough.py` (`NC_D403` 1065 + `NC_CD401S` 1120S) + `load_al_passthrough.py` (`AL_FORM_65` 1065 +
    `AL_FORM_20S` 1120S). `scratchpad/validate_nc_al_pt.py` = **47 pass / 0 fail** (caught 2 topic_name > 255 caps,
    trimmed; NC Taxed-PTE 4.25%/franchise/NRW/85% add-back + AL Electing-PTE 5%/composite/Line-32 all green; all 16
    rules cited).
  - **✅ DONE — seeded + exported 2026-07-05** (Ken Gate-1: "Approve — flip, seed, export"; W1-W6 blessed). Flipped
    both guards → seeded → **110 TaxForms**; `lookup/{NC_D403,NC_CD401S,AL_FORM_65,AL_FORM_20S}/export/` all = 200.
    Auto-discovered by `seed_all` (reconstructable). **Status: ✅ DONE (RS).** tts app build = [APP] lane. The
    adjacent-state pass-through track is now COMPLETE (GA-700 + SC1065/SC1120S + NC + AL). [UNVERIFIED] exact NC/AL
    line numbers noted for a re-pull. **Post-WO-13: net-new RS scope needs the TaxWise forms-usage report or a law change.**
- **▶ ACTIVE — [WO-14] Form 6765 (§41 research credit) · production-packet trigger · status `GAP-CHECKED →
  DRAFTING` (opened 2026-08-04; Ken: "run the form 6765 rule studio spec").**
  Trigger: delvio-tax CC batch-005 #2 — packet 227 (1120-S) carries a real Form 6765 (ASC, QREs $53,704,
  credit $4,243 → Schedule K); the entity lane refused to improvise without a spec (`lookup/6765/export/`
  = **404, GAP confirmed 2026-08-04**). The production-packet trigger is the "TaxWise forms-usage" class
  of net-new scope. **✅ RESEARCH (2026-08-04):** f6765 Rev. 12-2024 face (4 pp) + i6765 Rev. 12-2025
  (12 pp, "for use with the January 2025 revision" — label mismatch flagged, line refs verified against
  the 12-2024 face) + i1120ssk (K-1 box 13 **code M** verbatim) fetched and read line-by-line;
  `f6765_source_brief.md` written. Key law: Section G OPTIONAL for TYs beginning before 2026; ASC
  election irrevocable for the current year (Reg. §1.41-9(b)(3)); §280C reduced credit = Item A on a
  timely original return (15.8% regular / ×79% ASC); no-election ⇒ §174A deduction reduced by the credit
  (OBBBA P.L. 119-21). Gate-1 scope walk: 4 questions (FBP entry mode; §280C diagnostic-only; Section D
  defer; controlled-group HOLD) — see the brief's "Open scope questions".
  **✅ GATE-1 SCOPE WALK (2026-08-04, DECISIONS D-16):** all four recommended options approved by Ken
  (FBP preparer-entered · §280C diagnostic-only · Section D deferred+HOLD · controlled group HOLD).
  **🟡 AUTHORED — status `⏳ AWAITING KEN (seed approval)`:** `load_6765.py` (24 facts / 7 rules /
  50 lines / 10 diagnostics / 6 scenarios / 2 draft flow assertions; 5 sources, all rules cited;
  READY_TO_SEED=False) + `scratchpad/validate_6765.py` = **19 pass / 0 fail** (arithmetic oracles on
  every scenario through the loader's pure helpers + a clean SQLite seed dry-run). Scenario T1 pins
  packet 227's shape (QREs 53,704 → credit 4,243; line 21 INFERRED — the real priors come off the
  packet at authoring). Next: Ken's review walk → "Approve — flip, seed, export" → the delvio-tax
  app build (compose 6765 + 8941 into Schedule K 13g — never stomp).
- **✅ S-5 completed the front-door loop 2026-07-05** (GAP-CHECKED → DRAFTING → AWAITING KEN → seeded/exported).
  New consolidated `ENTITY_BOUNDARY` form (`load_entity_boundary.py`, 6 self-owned sources): B1 M-3 threshold
  (1065 4-prong / 1120-S $10M); B2 K-2/K-3 DFE 4-criteria gate (COMPUTED, RED on fail + D_EB_DFE_OK affirmative
  record); B3 §704(c) indicator; B4 §754/§743(d)/§734(d) ($250k triggers); B5 apportionment (P.L. 86-272).
  SQLite-validated (ALL PASS) → seeded to prod (**96 TaxForms / 457 FlowAssertions**) → `lookup/ENTITY_BOUNDARY/
  export/` = 200. `boundary_diag_source_brief.md`. BUILD_ORDER S-5 ticked [RS]✅→[APP]⬜. Caveats: M-3 instr not
  annual (1065 Rev 11/2023, 1120-S Rev 12/2019); apportionment state-specific (re-verify per state). **Next: tts app dispatch.**
  PRODUCT_MAP scope: wire the Core boundary diagnostics so Core never goes silent when a return crosses into
  module territory. Gap-check (existing vs gap):
  - **M-3 threshold** → EXISTS: `D_L_M3` / `R-L-M3` on 1065_L (≥$10M assets / ≥$35M receipts / ≥50% REP, sourced).
    Verify 1120-S side ($10M) has an equivalent.
  - **§754 / §743(b) / §734(b)** → EXISTS: 1065_B Q10 + `IRC_754` (basis-adjust math RED-deferred). Adequate flag.
  - **§704(c)** → EXISTS: `D_SCHK_704C` structure-only (item M/N). Adequate boundary flag.
  - **K-2/K-3** → PARTIAL: `D_SCHK_K3` is a **blanket "out of scope" RED-defer** — but PRODUCT_MAP makes the
    **DFE determination** ("record WHY K-2/K-3 aren't required") CORE season one. **GAP: the DFE-fail criteria diagnostic.**
  - **Multistate apportionment (beyond-licensed-state)** → **GAP: no indicator found.**
  - (§461(l) boundary = DONE via S-6 Form 461; 1041 Sch I AMT = defer to S-11 per D-2.)
  - **Next:** research-verify (M-3 thresholds 1065+1120S; K-2/K-3 DFE 2025 criteria; §704(c)/§754 triggers;
    apportionment nexus) → source brief → Gate-1 scope walk (incl. the shape: amend existing forms vs a
    consolidated boundary-diagnostics reference). Research pass running.
- **Other open SPINE authoring rock:** S-11 1041 (WO-09, Sept greenfield).
- **✅ S-6 completed the front-door loop 2026-07-05** (GAP-CHECKED → DRAFTING → AWAITING KEN → seeded/exported).
  Scope (Ken-approved, all recommended): R1 self-rental + R2 PTP = COMPUTE; R3 REP = checkbox + §1.469-9(g)
  election flag; R4 at-risk = diagnostic-only (route to 6198); R5 §461(l) = diagnostic, thresholds $313k/$626k.
  Authored: R1-R4 amend `load_1040_schedule_e.py` (FORM_8582/SCHEDULE_E home loader; REP RED-defer→checkbox);
  R5 = new `load_1040_form_461.py` (form `461`). SQLite-validated (`scratchpad/validate_pal.py`, ALL PASS) →
  **seeded to prod (95 TaxForms / 454 FlowAssertions)** → `lookup/{FORM_8582,SCHEDULE_E,461}/export/` all **200**.
  `pal_basis_source_brief.md`. Carried caveats: Form 461 face line-numbering mapped to the §461(l)(3) mechanic
  (i461 `requires_human_review`); disallowed-EBL→NOL year-keyed (re-verify each season). **Next: tts app dispatch.**
  Required set / gap-check (recorded at open):
  - R1 self-rental recharacterization → **amend `FORM_8582`** (home `load_1040_schedule_e.py`, v1 bucket) — exists.
  - R2 PTP per-entity segregation → **amend `FORM_8582`** — exists.
  - R3 REP (real estate professional) tests/checkbox → **amend `FORM_8582` / `SCHEDULE_E`** — exists.
  - R4 at-risk diagnostic → **`6198`** (exists; integrated by 4835) — amendment/diagnostic.
  - R5 §461(l) excess-business-loss diagnostic → **NEW = the one real GAP**; 2025 thresholds need source-pinning (indexed, OBBBA-permanent).
  - **Next:** research-verify authorities (§469 self-rental Reg. 1.469-2(f)(6); §469(k) PTP; §469(c)(7)
    REP; §465 at-risk; §461(l) 2025 thresholds) → source brief → Gate-1 scope walk → author
    `READY_TO_SEED=False` → validate on SQLite → seed → export.
- **Other open SPINE authoring rocks:** S-5 Boundary diagnostics (WO-04); S-11 1041 (WO-09, Sept greenfield).

## Status reconciliation (against live STATUS.md + on-disk loaders, 2026-07-05)
- **[WO-01]** 1040 ATS S3/S4 gaps — **✅ DONE (RS)** · 4835 + 8835 + 8936 (+8936_SCHA) all
  seeded/exported, all four `lookup/<form>/export/` = 200 · tts building S3/S4 mappers (SPINE S-1).
- **[WO-02]** 1065 core — **✅ DONE** · campaign complete 2026-07-04: all 6 forms (Schedule K
  spine `1065_PAGE1`+`SCH_K_1065`, K-1+alloc, M-1/M-2, L/B seeded+exported = 200; 8825/4562/3800
  cover 1065); the 7-form batch is in `approved_specs.py`. *(BUILD_ORDER S-4 still lists these
  unticked + "▶ NEXT authoring = Schedule K" — a stale mark; the canonical file's own "never trust
  a stale mark" rule says correct it. S-4 [RS] = DONE; only [APP] issuer-side K-1 persistence remains.)*
- **[WO-05]** SC1040 (+ Schedule NR) + SC entity (SC1065/SC1120S/PTET) — **🟡 AUTHORED** ·
  seeded/exported = 200; not yet in the approved manifest (SPINE S-7).
- **[WO-06]** AL Form 40 — **🟡 AUTHORED** · `lookup/AL_FORM_40/export/` = 200 (SPINE S-8).
- **[WO-07]** NC D-400 — **🟡 AUTHORED** · `lookup/NC_D400/export/` = 200 (SPINE S-9).
- **[WO-08]** GA-700 + PTET — **🟡 AUTHORED** · `lookup/GA700/export/` = 200 (SPINE S-10; ⚠ app
  build gated behind S-4 — GA partnership numbers depend on the federal 1065 flow).
- **[WO-03] / [WO-04] / [WO-09]** — INTAKE, genuinely open = SPINE **S-6 / S-5 / S-11**.

## ✅ DONE (recent — proves the pipeline)
- 1065 core (Schedule K → K-1 → M-1/M-2 → L/B) — 2026-07-04 · spec→seed→export (all 200).
- 1065 SE (line 14a) — 2026-07-01 · spec→seed→export→build→DB-verified.
- 4797 recapture classification + nuance legs — 2026-07-02 · caught the K8c→K9c misroute.
- GA-500 HB 463 tips/OT exclusions — 2026-07-02.

---

## Maintenance
- Lives in RS repo root + the tts-tax-status mirror (`rule-studio/`). CC boot list.
- **The CHANGE_REGISTER is BUILT (2026-07-08, DECISIONS D-26)** — see `CHANGE_REGISTER.md`. A triaged law-change
  item is PROMOTED (`change_register promote --code CR-YYYY-NNN --work-order WO-NN`) and enters THIS file's INTAKE as
  a new order, then runs the standard front door. It does NOT bypass the gates. This is now the primary intake for
  net-new RS scope post-S-16-drain.
- Completion ping reuses the existing Pushover hook: draft ready → notify Ken → approve.
