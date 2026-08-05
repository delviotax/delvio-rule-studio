# CHANGE_REGISTER.md — the tax-law-change funnel (front-of-the-front-door)

*Adopted 2026-07-08. This is the TRIGGER that feeds `WORK_ORDERS.md` INTAKE. It closes the loop
CLAUDE.md and WORK_ORDERS.md always anticipated: **a law change → a new tax rule (RS spec) → a
tax-app change (tts build)**. Before this, net-new RS scope entered only when Ken named a form or a
form-usage report surfaced one. Now a law change is a first-class, tracked trigger.*

***This register does NOT bypass the two gates.** A change can START a draft; nothing CROSSES a gate
unattended. Gate 1 = draft→published spec (Ken). Gate 2 = published→compute (the existing tts ingest).
A promoted change becomes a WORK_ORDERS order and then runs the SAME front door as every other form.*

---

## The funnel

```
  DETECT ───────────────► TRIAGE ────────────────► PROMOTE ──────────► WORK_ORDERS.md INTAKE
  a source moved           ChangeRegisterItem        opens a WO           (the existing front door)
  · manual clip (Ken)      · affected forms?         · --work-order WO-NN  gap-check → research-verify
  · checksum diff          · which tax year?         · status = PROMOTED   → Gate-1 scope walk (Ken)
    (detect_source_        · substantive?                                  → author READY_TO_SEED=False
     changes)              status: DETECTED →                              → SQLite-validate → seed
                           TRIAGED → PROMOTED/                             → export → tts [APP] build
                           DISMISSED                                        ⟨Gate 2: tts ingest⟩
```

**Five arms into DETECT (all live):**
- **Manual clip** — Ken (or CC on a known law change) records it:
  `manage.py change_register add --title "..." --summary "..." --forms 3115 --tax-year 2026 --source REVPROC_2025_23`
- **Checksum diff** — re-fetch checksums, diff against each source's current `AuthorityVersion`:
  `manage.py detect_source_changes --manifest scratchpad/latest_checksums.json`
  (opens a `DETECTED` item per moved source; idempotent; flags sources with no current version as a
  feed-coverage gap. v1 diffs supplied checksums; the fetcher that produces the manifest is future work.)
- **Federal Register poll (FEED_POLL leg 1, BUILT 2026-07-08)** — auto-discovers recent IRS/Treasury
  regulatory documents from the free Federal Register API:
  `manage.py fetch_federal_register [--since YYYY-MM-DD | --lookback-days N] [--types RULE,PRORULE,NOTICE] [--dry-run]`
  (opens a `DETECTED` `feed_poll` item per new final/proposed rule; idempotent by FR `document_number`
  stored in `external_ref`; stdlib urllib, no key. ⚠ The FR carries REGULATIONS only.)
- **Internal Revenue Bulletin poll (FEED_POLL leg 2, BUILT 2026-07-08)** — the SUB-REGULATORY channel the
  FR misses: Revenue Procedures, Notices, Revenue Rulings, Announcements (e.g. the annual Form 3115
  automatic-change list, indexed amounts). Scrapes the IRS IRB index (no govinfo/IRS API exists):
  `manage.py fetch_irb [--since-bulletin YYYY-NN | --limit N] [--dry-run]`
  (opens a `DETECTED` `feed_poll` item per new WEEKLY BULLETIN, idempotent by `external_ref` `IRB-YYYY-NN`;
  browser UA; stdlib urllib. Detection is bulletin-level. **Now a BACKSTOP** — the irs-drop arm below gets
  the same items weeks earlier and one at a time.)
- **26 CFR section amendments (FEED_POLL leg 3, BUILT 2026-08-05)** — the eCFR versioner API (free, no key)
  reports SECTION-level amendments to Title 26, and `identifier` ('1.199A-3') maps straight onto
  `AuthoritySource.citation` so the scorer matches exactly rather than by keyword:
  `manage.py fetch_ecfr_title26 [--since YYYY-MM-DD | --lookback-days N] [--parts 1,301,602 | --all-parts]
   [--include-nonsubstantive] [--force] [--dry-run]`
  (idempotent by `CFR26:<identifier>@<amendment_date>`; short-circuits on one cheap request when Title 26's
  `latest_amended_on` hasn't moved. ⚠ **Filters on `amendment_date`, NOT `issue_date`** — eCFR re-issues
  unamended sections, and §1.0-1 currently carries issue_date 2026-04-03 with amendment_date 2016-12-19.)
- **IRS guidance drop (FEED_POLL leg 4, BUILT 2026-08-05)** — the arm that closes the real gap. One item per
  INDIVIDUAL Rev. Proc. / Notice / Rev. Rul. / Announcement from `irs.gov/downloads/irs-drop`, **weeks before
  the IRB bundles it**. The annual inflation Rev. Proc., the December mileage notice, the retirement-limits
  notice and the Form 3115 automatic-change list all land here first:
  `manage.py fetch_irs_drop [--pages N] [--since YYYY-MM-DD] [--kinds rp,n,rr,a] [--no-text] [--dry-run]`
  (idempotent by `DROP:<filename>`; ~8 items/month so no filter is needed — everything is recorded and
  RANKED. Designation comes from the FILENAME: live rows write 'Rev. Proc.  2026-28', 'RR-2026-13' and
  'N-2026-44' interchangeably. PDF text is extracted with stdlib zlib+re for scoring; unreadable text scores
  mid-band and surfaces to a human rather than falling silent.)

## Status lifecycle (the `ChangeRegisterItem` model, `sources` app)
`DETECTED → TRIAGED → PROMOTED` (or `→ DISMISSED`). Backed by a DB model (queryable, FKs to
`AuthoritySource` / `AuthorityVersion` / `SourceFeedDefinition`) AND this human-readable ledger.
Update this file at each transition, same discipline as WORK_ORDERS.md.

**At triage/promote, run the blast-radius report** — `stale_rules_report --change CR-YYYY-NNN` lists the
authored rules that depend on the moved authority (rules that CITE the source, rules named in triage, and
every rule on an affected form), so you know what to re-verify. Read-only — it flags, you decide. This is
the Authoritative-Source Rule step 5 ("when the source changes, treat dependent logic as stale until
re-verified") made operational.

## Commands
| Step | Command |
|---|---|
| record | `change_register add --title T --summary S [--forms a,b] [--tax-year Y] [--jurisdiction US] [--source CODE]` |
| triage | `change_register triage --code CR-YYYY-NNN --substantive|--not-substantive [--forms a,b] [--rules r1,r2] [--notes N]` |
| promote | `change_register promote --code CR-YYYY-NNN --work-order WO-NN` |
| dismiss | `change_register dismiss --code CR-YYYY-NNN --notes N` |
| list | `change_register list [--status detected]` |
| detect (checksum) | `detect_source_changes --manifest <json> | --from-files [--dry-run]` |
| detect (Fed. Register) | `fetch_federal_register [--since YYYY-MM-DD | --lookback-days N] [--types ...] [--dry-run]` |
| detect (IRB — backstop) | `fetch_irb [--since-bulletin YYYY-NN | --limit N] [--dry-run]` |
| detect (26 CFR) | `fetch_ecfr_title26 [--since | --lookback-days N] [--parts 1,301,602 | --all-parts] [--force] [--dry-run]` |
| detect (IRS guidance) | `fetch_irs_drop [--pages N] [--since YYYY-MM-DD] [--kinds rp,n,rr,a] [--no-text] [--dry-run]` |
| **poll all (scheduler)** | `poll_change_feeds [--fr-lookback-days N] [--irb-limit N] [--ecfr-lookback-days N] [--drop-pages N] [--no-fr|--no-irb|--no-ecfr|--no-drop] [--only KEY] [--dry-run]` |
| blast radius (staleness) | `stale_rules_report --change CR-YYYY-NNN | --source SOURCE_CODE [--json]` |

## What feeds it (design intent — see [[rs-change-register-funnel]])
- IRS IRB / Rev. Proc. / Notice releases (the annual automatic-change list, indexed-amount updates).
- Statute changes (OBBBA-style: P.L. amendments to the Code).
- State DOR conformity + form updates (GA/SC/AL/NC — via `JurisdictionConformitySource`).
- `SourceFeedDefinition` rows describe WHERE to look; `detect_source_changes` diffs WHAT moved.

## Deferred / follow-ups
- ~~**Staleness report**~~ **DONE 2026-07-08** — `stale_rules_report` (read-only blast radius; cites-source
  / named / on-affected-form). A future escalation could add an on-`FormRule` stale FLAG + a re-verify queue,
  but the report is the agreed v1 (report, don't auto-edit — D-26).
- ~~**item-LEVEL IRB parsing**~~ **SUPERSEDED 2026-08-05** by `fetch_irs_drop`. Parsing individual Rev.Procs
  out of each bulletin PDF was always the fragile way to get item-level detection; the irs-drop directory is
  a structured index carrying the same items *weeks earlier*. Closed, not built.
- **Congress.gov statute arm (leg 5)** — **DECIDED 2026-08-05: not building.** OBBBA-class acts are unmissable
  by anyone reading the news, so the register would gain an audit row and near-zero signal, at the cost of a
  second API key. govinfo is likewise skipped: it carries **no** Internal Revenue Bulletin collection
  (verified) and duplicates eCFR. Revisit only if the perimeter widens.
- **Remaining legs**: `fetch_irs_drafts` (irs-dft draft/final forms) and `fetch_irs_form_checksums` — the
  fetcher that finally produces the `detect_source_changes` checksum manifest. Then `poll_source_pages`
  (generic state DOR page-diff, deferred while the perimeter is federal-only) and `fetch_court_opinions`.
  (Leg 1 = Federal Register regulations; leg 2 = IRB bulletins — both BUILT 2026-07-08. Legs 3 and 4 =
  26 CFR + IRS guidance drop — both BUILT 2026-08-05.)
- **`change_digest`** — the ranked Friday reading surface, with blast radius inline and an **arm-health
  section**. Not yet built, and it is the highest-value remaining piece: on 2026-08-05 the register was found
  EMPTY because the Monday cron had never run since it shipped on 2026-07-08. Nothing in the current design
  would ever have said so.
- ~~**Scheduling**~~ **DONE 2026-07-08** — `poll_change_feeds` runs both automated arms resiliently (one arm
  failing doesn't stop the other) and is wired as a **Render cron job** (`render.yaml`, `type: cron`,
  `sherpa-rs-change-feeds`, Mondays 12:00 UTC). Optional Pushover ping on new items (set `PUSHOVER_TOKEN` +
  `PUSHOVER_USER`). **Deploy step (Ken, one-time):** the cron service ships in `render.yaml` — on the next
  Blueprint sync Render creates it; set its `DATABASE_URL` to the same Supabase value as the web service.
- **REST API** for the register (consistent with `/api/sources/…`) — CLI + this doc are the v1 front door.

---

## ▶ OPEN ITEMS
*None yet — the register is live and empty. The first real trigger (a law change or a checksum diff)
records here. When the S-16 queue drained (2026-07-06), this funnel became the primary way net-new RS
authoring scope enters.*

| Code | Status | TY | Forms | Title | → WO |
|---|---|---|---|---|---|
| _(none)_ | | | | | |

## ✅ PROMOTED / DISMISSED (history)
*(empty)*

---

## Maintenance
- Lives in the RS repo root (like WORK_ORDERS.md); on the CC boot list. Mirrored to the public
  `tts-tax-status` status repo on session close — keep PII/sensitive prose out.
- The model is `sources.ChangeRegisterItem`; the commands are `change_register` + `detect_source_changes`.
