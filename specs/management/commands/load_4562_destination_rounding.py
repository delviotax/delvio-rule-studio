"""Amend Form 4562 with 1040 destination routing + per-asset rounding + reconciliation.

WHY (QA Batch-001 item 6 / delvio s116, Ken's design GO 2026-07-26): the deployed
4562 spec routes depreciation by destination for the S-Corp only (R013). The 1040
side has activity-linked destinations in the app (Schedule C line 13 / Schedule E
line 18 / Schedule F line 14 via real FKs), but the spec is SILENT on them — and
the app's 1040 UI shipped offering the ENTITY farm arm ("sched_f"), which writes a
line ("F14") that does not exist on a 1040 form. The write misses silently and the
asset's depreciation lands NOWHERE (the Benkoski defect: module shows
"Schedule F $4,069" while Schedule F line 14 stays 0 — farm loss understated
4,068, AGI overstated 6,102). Nothing diagnosed the unroutable asset and nothing
reconciled the module total against the destination lines.

Separately, destination totals were summed in unrounded cents and rounded once at
the write; the QA fleet's benchmark (TaxWise) rounds each asset as reported and
sums the whole-dollar amounts (Benkoski: 4,069.03 unrounded-sum vs 4,068 per-asset).

This loader AMENDS the existing multi-entity 4562 form ADDITIVELY (the
load_4562_section179_carryover pattern — looks up the TaxForm, never re-creates,
entity_types untouched):
  - adds facts `flow_destination` + `activity_reference` (the app's flow_to + FK)
  - adds R016 (1040 depreciation by destination — activity-linked routing,
    companion to the S-Corp R013) + R017 (per-asset whole-dollar rounding)
  - adds diagnostics D_4562_DEST (unroutable asset = error) + D_4562_RECON
    (module/destination mismatch = error) — CANONICAL app codes verbatim per the
    s115 rule (FormDiagnostic.diagnostic_id widened to 40 in specs.0003)
  - adds the verbatim Part IV line 22 face excerpt (destination authority)
  - adds 4 test scenarios (rounding pin incl. the Benkoski shape; routing;
    both diagnostic edges)
  - stages flow assertions FA-4562-DEST-01 + FA-4562-ROUND-01

LAW / SOURCE BASIS (verified 2026-07-26 against the local SHA-tracked template
resources/irs_forms/2025/f4562.pdf, pymupdf dump — NOT memory):
  - Form 4562 (2025) face, Part IV line 22, VERBATIM: "Total. Add amounts from
    line 12, lines 14 through 17, lines 19 and 20 in column (g), and line 21.
    Enter here and on the appropriate lines of your return. Partnerships and
    S corporations—see instructions." For a 1040, the "appropriate lines" are the
    activity schedules' own depreciation lines: Schedule C line 13, Schedule E
    line 18, Schedule F line 14 (each already spec-homed: R-SC-DEPR, R-SCHE-NET,
    R-SF-DEPR on their owning specs). A 1040 has NO page-1 depreciation line.
  - ROUNDING: the form's Part III lines 19a-20e column (g) and every destination
    line are whole-dollar entries. The IRS publishes no per-ASSET rounding
    directive (the i1040 generic "include cents when adding and round the total"
    note addresses adding amounts onto one return line, not the multi-asset
    depreciation schedule) — a genuine ambiguity, FLAGGED per the
    Authoritative-Source Rule and RULED BY KEN (CPA, 2026-07-26, in-session):
    round each asset's reported amount to whole dollars (ROUND_HALF_UP), then sum
    — matching the industry benchmark (TaxWise) and the whole-dollar face. This
    is recorded as a ratified house convention, NOT as quoted IRS text.

Idempotent: update_or_create / get_or_create throughout. Safe to re-run.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from sources.models import (
    AuthorityExcerpt,
    AuthoritySource,
    RuleAuthorityLink,
)
from specs.models import (
    FlowAssertion,
    FormDiagnostic,
    FormFact,
    FormRule,
    TaxForm,
    TestScenario,
)


# ═══════════════════════════════════════════════════════════════════════════
# SAFETY GUARD — Ken's approval is ON RECORD for this unit: 2026-07-26,
# in-session AskUserQuestion, delvio s116 ("GO — start Leg 1" + "Ratify"
# per-asset ROUND_HALF_UP + the migration policy). The Design proposal is
# Design/item6_depreciation_rebuild_proposal.md (delvio 58ce774). Seeding
# proceeds under that GO — the same Ken-relayed-QA-backlog class as the s109b/
# s112 amendments; the routing/rounding mechanics land in REVIEW_QUEUE for
# final ratification alongside the build leg.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = True


FORM_NUMBER = "4562"
FORM_JURISDICTION = "FED"
FORM_TAX_YEAR = 2025


# ═══════════════════════════════════════════════════════════════════════════
# NEW FACTS — the app's flow destination + activity link
# ═══════════════════════════════════════════════════════════════════════════

NEW_FACTS: list[dict] = [
    {"fact_key": "flow_destination",
     "label": "Depreciation flow destination (per asset)",
     "data_type": "choice", "required": True, "default_value": None, "sort_order": 30,
     "choices": ["page1", "8825", "sched_f", "schedule_c", "schedule_f"],
     "notes": ("The app's DepreciationAsset.flow_to. ENTITY arms: page1 (1120-S/1120 L14, "
               "1065 L16), 8825 (per rental property), sched_f (entity farm — FormFieldValue "
               "F14). 1040 arms: schedule_c (per Schedule C business, L13), schedule_f (per "
               "1040 farm, L14), 8825 (retargeted = Schedule E L18 per property). A "
               "destination FOREIGN to the return's form is UNROUTABLE (D_4562_DEST) — the "
               "entity sched_f arm on a 1040 writes a line that does not exist there.")},
    {"fact_key": "activity_reference",
     "label": "Linked activity (business / farm / rental property)",
     "data_type": "text", "required": False, "default_value": None, "sort_order": 31,
     "notes": ("The app's FK — ScheduleC / ScheduleF / RentalProperty row id. REQUIRED for "
               "the activity-linked arms (schedule_c / schedule_f / 8825): without it the "
               "asset's depreciation reaches no line (D_4562_DEST).")},
]


# ═══════════════════════════════════════════════════════════════════════════
# RULES — R016 (1040 destination routing) + R017 (per-asset rounding)
# ═══════════════════════════════════════════════════════════════════════════

RULES: list[dict] = [
    {"rule_id": "R016", "title": "Depreciation by destination (1040) — activity-linked routing",
     "rule_type": "routing",
     "formula": ("ScheduleC_L13[biz] = sum(assets linked to biz, incl. §179); "
                 "ScheduleE_L18[prop] = sum(assets linked to prop); "
                 "ScheduleF_L14[farm] = sum(assets linked to farm, incl. §179); "
                 "NO page-1 destination exists on a 1040 — every asset REQUIRES an activity link"),
     "inputs": ["flow_destination", "activity_reference"],
     "outputs": ["schedule_c_line13", "schedule_e_line18", "schedule_f_line14"],
     "precedence": 5, "sort_order": 16,
     "description": (
         "Companion to R013 (S-Corp). Form 4562 Part IV line 22 (2025 face, verbatim): 'Enter "
         "here and on the appropriate lines of your return.' On a 1040 the appropriate lines "
         "are the activity schedules' own depreciation lines — Schedule C line 13 ('Depreciation "
         "and section 179 expense deduction (not included in Part III)', R-SC-DEPR: §179 stays "
         "IN the line-13 total), Schedule E line 18 (per rental property, R-SCHE-NET), Schedule "
         "F line 14 (R-SF-DEPR: §179 stays IN the line-14 total). Each destination is a SPECIFIC "
         "activity record, never a form-level label: an asset carrying an activity-linked "
         "destination with no linked activity, or a destination foreign to the return's form "
         "(the entity farm arm on a 1040), is UNROUTABLE — its depreciation reaches no line and "
         "the return's income is overstated silently (the Benkoski defect). Unroutable assets "
         "are a blocking error (D_4562_DEST), and the module total must reconcile to the "
         "destination lines (D_4562_RECON)."),
     "notes": "QA Batch-001 item 6 Leg 1 (delvio s116). Destination lines spec-homed on SCHEDULE_C / SCHEDULE_E / SCHEDULE_F."},
    {"rule_id": "R017", "title": "Per-asset whole-dollar rounding of reported depreciation",
     "rule_type": "calculation",
     "formula": ("reported_asset_amount = ROUND_HALF_UP(computed_asset_amount, 0); "
                 "destination_total = sum(reported_asset_amounts)"),
     "inputs": ["current_year_depreciation"],
     "outputs": ["destination_total"],
     "precedence": 6, "sort_order": 17,
     "description": (
         "Each asset's current-year depreciation is reported as a WHOLE-DOLLAR amount, and every "
         "destination total (Form 4562 lines, Schedule C 13 / Schedule E 18 / Schedule F 14, and "
         "the AMT/state parallels) is the sum of the rounded per-asset amounts — never a "
         "rounded sum of unrounded cents. RATIFIED HOUSE CONVENTION (Ken, CPA, 2026-07-26): the "
         "IRS publishes no per-asset rounding directive (genuine ambiguity, flagged per the "
         "Authoritative-Source Rule); the form's Part III column (g) and every destination line "
         "are whole-dollar entries, and the industry benchmark (TaxWise) rounds per asset. "
         "Divergence pin: seven assets summing 4,069.03 in cents report 4,068 per-asset-rounded "
         "(the Benkoski packet)."),
     "notes": "NOT quoted IRS text — a ratified convention. Re-verify only if the IRS publishes a directive."},
]

RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R016", "IRS_2025_4562_INSTR_FULL", "primary",
     "Part IV line 22 face text — 'appropriate lines of your return' (the destination mandate)"),
    ("R017", "IRS_2025_4562_INSTR_FULL", "secondary",
     "Part III col (g) / destination lines are whole-dollar entries; per-asset rounding is the Ken-ratified convention"),
]


# ═══════════════════════════════════════════════════════════════════════════
# DIAGNOSTICS — canonical app codes VERBATIM (specs.0003 widened id to 40)
# ═══════════════════════════════════════════════════════════════════════════

DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_4562_DEST", "title": "Depreciation asset has no reachable destination",
     "severity": "error",
     "condition": ("flow_destination is foreign to the return's form (entity arm on a 1040 / "
                   "1040 arm on an entity) OR an activity-linked destination (schedule_c / "
                   "schedule_f / 8825-rental) has no linked activity_reference. SEVERITY IS "
                   "EFFECT-SCALED: error when the asset carries any nonzero current-year "
                   "amount (money is being lost from the return); warning when every "
                   "current-year amount is zero (fully-depreciated legacy inventory — the "
                   "routing metadata is incomplete but no line is wrong)."),
     "message": ("Asset '{description}' does not feed any line of this return — its "
                 "depreciation is currently lost. Pick the business, farm, or rental property "
                 "it belongs to on the asset card."),
     "notes": ("The Benkoski class: the entity sched_f arm on a 1040 wrote nonexistent 'F14' "
               "and the miss was silent. Expands the S-Corp-era D013 to the unroutable/"
               "unlinked cases; blocking (when dollars move) because the return's income is "
               "otherwise overstated with no visible sign. The zero-amount warning arm keeps "
               "a 39-asset fully-depreciated legacy inventory from bricking a return over "
               "metadata with no tax effect.")},
    {"diagnostic_id": "D_4562_RECON", "title": "Depreciation module does not reconcile to destination lines",
     "severity": "error",
     "condition": ("for any destination: sum(rounded per-asset amounts routed there) != the "
                   "destination line's value (skip preparer-overridden lines)"),
     "message": ("Depreciation entered on the asset module ({module_total}) does not match "
                 "what reached {destination} ({line_value}). The difference would file a "
                 "wrong return — recalculate, and if the mismatch persists report it."),
     "notes": ("The permanent guard against the silent-skip class: any future routing gap "
               "surfaces as a blocking error instead of a quietly overstated income. "
               "Overridden destination lines are the preparer's call and are skipped.")},
]


# ═══════════════════════════════════════════════════════════════════════════
# TEST SCENARIOS
# ═══════════════════════════════════════════════════════════════════════════

SCENARIOS: list[dict] = [
    {"scenario_name": "Per-asset rounding — cent-sum vs reported-sum divergence (Benkoski shape)",
     "scenario_type": "normal",
     "inputs": {"asset_amounts": [266.49, 1002.44, 750.10, 500.00, 300.00, 749.00, 501.00],
                "note": "unrounded cent-sum 4069.03"},
     "expected_outputs": {"destination_total": 4068},
     "notes": ("R017: per-asset ROUND_HALF_UP → 266+1002+750+500+300+749+501 = 4068. The "
               "cent-sum path would report ROUND(4069.03) = 4069 — the TaxWise delta the QA "
               "fleet flagged. The pin: destination_total = sum(round(asset)), never "
               "round(sum(asset))."),
     "sort_order": 30},
    {"scenario_name": "1040 farm assets feed the LINKED farm's Schedule F line 14",
     "scenario_type": "normal",
     "inputs": {"flow_destination": "schedule_f", "activity_reference": "farm-1",
                "asset_amounts": [4068]},
     "expected_outputs": {"schedule_f_line14": 4068, "diagnostics": []},
     "notes": "R016 happy path — the destination is the specific farm's line 14, §179 included.",
     "sort_order": 31},
    {"scenario_name": "Unroutable asset — entity farm arm on a 1040 fires D_4562_DEST",
     "scenario_type": "edge",
     "inputs": {"return_form": "1040", "flow_destination": "sched_f",
                "activity_reference": None, "asset_amounts": [4068]},
     "expected_outputs": {"schedule_f_line14": 0, "diagnostics": ["D_4562_DEST"]},
     "notes": "The Benkoski defect, now a blocking error instead of silence.",
     "sort_order": 32},
    {"scenario_name": "Destination line diverges from module total — D_4562_RECON",
     "scenario_type": "edge",
     "inputs": {"flow_destination": "schedule_f", "activity_reference": "farm-1",
                "asset_amounts": [4068], "destination_line_value": 0},
     "expected_outputs": {"diagnostics": ["D_4562_RECON"]},
     "notes": "Any future silent routing gap surfaces here.",
     "sort_order": 33},
]


# ═══════════════════════════════════════════════════════════════════════════
# NEW EXCERPT on the EXISTING IRS_2025_4562_INSTR_FULL source (face text,
# the load_4562_section179_carryover L12-13 precedent) — VERBATIM from the
# local SHA-tracked template, pymupdf dump 2026-07-26.
# ═══════════════════════════════════════════════════════════════════════════

EXISTING_SOURCES_TO_REFERENCE: list[str] = ["IRS_2025_4562_INSTR_FULL"]

NEW_EXCERPTS_ON_EXISTING: list[tuple[str, dict]] = [
    ("IRS_2025_4562_INSTR_FULL", {
        "excerpt_label": "Part IV Line 22 — total, and the destination mandate",
        "location_reference": "Form 4562 (2025) face, Part IV, line 22",
        "excerpt_text": (
            "Total. Add amounts from line 12, lines 14 through 17, lines 19 and 20 in column "
            "(g), and line 21. Enter here and on the appropriate lines of your return. "
            "Partnerships and S corporations—see instructions."),
        "summary_text": ("L22 total goes to 'the appropriate lines of your return' — on a 1040 "
                         "that is each activity schedule's own depreciation line (Sch C 13 / "
                         "Sch E 18 / Sch F 14)."),
        "is_key_excerpt": True,
    }),
]


# ═══════════════════════════════════════════════════════════════════════════
# FLOW ASSERTIONS (staged; the app leg activates its pins in its own gate)
# ═══════════════════════════════════════════════════════════════════════════

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-4562-DEST-01", "assertion_type": "flow_assertion", "entity_types": ["1040"],
     "title": "Every 1040 depreciation asset's amount reaches its LINKED activity's line",
     "description": ("Validates R016. An asset linked to a Schedule C business / 1040 farm / "
                     "rental property must land on that activity's line 13 / 14 / 18. Bug it "
                     "catches: an unroutable or unlinked asset's depreciation vanishing "
                     "silently (the Benkoski defect — Sch F line 14 = 0 under a $4,068 module)."),
     "definition": {"kind": "flow_assertion", "form": "4562",
                    "source": "activity-linked asset depreciation",
                    "must_write_to": ["SCHEDULE_C.13", "SCHEDULE_E.18", "SCHEDULE_F.14"]},
     "sort_order": 5},
    {"assertion_id": "FA-4562-ROUND-01", "assertion_type": "flow_assertion",
     "entity_types": ["1040", "1120S", "1065", "1120"],
     "title": "Destination totals = sum of per-asset whole-dollar amounts (R017)",
     "description": ("Validates the ratified rounding convention: destination_total == "
                     "sum(ROUND_HALF_UP(asset, 0)), never ROUND_HALF_UP(sum(asset)). Bug it "
                     "catches: the cent-sum drift (4,069 vs TaxWise 4,068 on seven farm assets)."),
     "definition": {"kind": "formula_check", "form": "4562",
                    "formula": "destination_total == sum(round_half_up(asset_amount, 0) for each asset)"},
     "sort_order": 6},
]


# ═══════════════════════════════════════════════════════════════════════════
# Command
# ═══════════════════════════════════════════════════════════════════════════

class Command(BaseCommand):
    help = (
        "Amend Form 4562 with 1040 activity-linked destination routing (R016), the "
        "per-asset whole-dollar rounding convention (R017), and the D_4562_DEST / "
        "D_4562_RECON blocking diagnostics. AMENDS the existing multi-entity 4562 "
        "form additively (entity_types untouched)."
    )

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()

        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nAmend Form 4562 — destination routing + per-asset rounding + reconciliation\n"))

        form = self._get_existing_form()
        self._upsert_facts(form, NEW_FACTS)
        rules = self._upsert_rules(form, RULES)
        self._upsert_authority_links(rules, RULE_LINKS)
        self._upsert_diagnostics(form, DIAGNOSTICS)
        self._upsert_tests(form, SCENARIOS)
        self._load_new_excerpts_on_existing()
        self._load_flow_assertions()
        self._report_totals(form)

    # ─────────────────────────────────────────────────────────────────────────
    # Safety guard
    # ─────────────────────────────────────────────────────────────────────────

    def _guard_against_hollow_seed(self):
        empty = [name for name, seq in (
            ("NEW_FACTS", NEW_FACTS), ("RULES", RULES),
            ("DIAGNOSTICS", DIAGNOSTICS), ("SCENARIOS", SCENARIOS),
            ("RULE_LINKS", RULE_LINKS), ("NEW_EXCERPTS_ON_EXISTING", NEW_EXCERPTS_ON_EXISTING),
            ("FLOW_ASSERTIONS", FLOW_ASSERTIONS),
        ) if not seq]

        # id-length guard — diagnostic_id is varchar(40) since specs.0003 (s115);
        # rule_id / line_number remain varchar(20).
        too_long = []
        for d in DIAGNOSTICS:
            if len(d["diagnostic_id"]) > 40:
                too_long.append(f"diagnostic_id {d['diagnostic_id']}")
        for r in RULES:
            if len(r["rule_id"]) > 20:
                too_long.append(f"rule_id {r['rule_id']}")

        if not READY_TO_SEED or empty or too_long:
            still_empty = "\n  ".join(f"- {n}" for n in empty) or "(all populated)"
            length_issues = "\n  ".join(f"- {n}" for n in too_long) or "(none)"
            raise CommandError(
                "\n"
                "REFUSING TO SEED 4562 destination/rounding amendment.\n"
                f"READY_TO_SEED = {READY_TO_SEED} (must be True)\n"
                f"Empty lists:\n  {still_empty}\n"
                f"ID-length issues:\n  {length_issues}\n"
            )

    # ─────────────────────────────────────────────────────────────────────────
    # Form lookup (NEVER recreate — preserve entity_types)
    # ─────────────────────────────────────────────────────────────────────────

    def _get_existing_form(self) -> TaxForm:
        form = (
            TaxForm.objects.filter(
                form_number=FORM_NUMBER, jurisdiction=FORM_JURISDICTION, tax_year=FORM_TAX_YEAR,
            )
            .order_by("version")
            .first()
        )
        if not form:
            raise CommandError(
                f"Form {FORM_NUMBER} ({FORM_JURISDICTION} {FORM_TAX_YEAR}) not found — run "
                "load_1120s_specs / load_remaining_1120s first. This loader only AMENDS it."
            )
        self.stdout.write(
            f"Amending {FORM_NUMBER} v{form.version} (entity_types={form.entity_types} — untouched)")
        return form

    # ─────────────────────────────────────────────────────────────────────────
    # Upsert helpers (mirror load_4562_section179_carryover.py)
    # ─────────────────────────────────────────────────────────────────────────

    def _upsert_facts(self, form, facts):
        for f in facts:
            f = dict(f)
            FormFact.objects.update_or_create(
                tax_form=form, fact_key=f.pop("fact_key"), defaults=f,
            )
        self.stdout.write(f"  {len(facts)} facts")

    def _upsert_rules(self, form, rules_data) -> dict:
        created = {}
        for r in rules_data:
            r = dict(r)
            rule, _ = FormRule.objects.update_or_create(
                tax_form=form, rule_id=r.pop("rule_id"), defaults=r,
            )
            created[rule.rule_id] = rule
        self.stdout.write(f"  {len(created)} rules (R016/R017 new)")
        return created

    def _upsert_authority_links(self, rules, rule_links):
        ct = 0
        for rule_id, source_code, level, note in rule_links:
            rule = rules.get(rule_id)
            source = AuthoritySource.objects.filter(source_code=source_code).first()
            if rule and source:
                RuleAuthorityLink.objects.get_or_create(
                    form_rule=rule, authority_source=source,
                    defaults={"support_level": level, "relevance_note": note},
                )
                ct += 1
            elif not source:
                self.stdout.write(self.style.WARNING(f"  source {source_code} not found — link skipped"))
        self.stdout.write(f"  {ct} authority links")

    def _upsert_diagnostics(self, form, diagnostics):
        for d in diagnostics:
            d = dict(d)
            FormDiagnostic.objects.update_or_create(
                tax_form=form, diagnostic_id=d.pop("diagnostic_id"), defaults=d,
            )
        self.stdout.write(f"  {len(diagnostics)} diagnostics (canonical app codes)")

    def _upsert_tests(self, form, scenarios):
        for t in scenarios:
            t = dict(t)
            TestScenario.objects.update_or_create(
                tax_form=form, scenario_name=t.pop("scenario_name"), defaults=t,
            )
        self.stdout.write(f"  {len(scenarios)} test scenarios")

    def _load_new_excerpts_on_existing(self):
        ct = 0
        for code, exc in NEW_EXCERPTS_ON_EXISTING:
            src = AuthoritySource.objects.filter(source_code=code).first()
            if not src:
                self.stdout.write(self.style.WARNING(f"  source {code} not found — excerpt skipped"))
                continue
            exc = dict(exc)
            AuthorityExcerpt.objects.update_or_create(
                authority_source=src, excerpt_label=exc["excerpt_label"], defaults=exc,
            )
            ct += 1
        self.stdout.write(f"  {ct} new excerpts on existing sources")

    def _load_flow_assertions(self):
        for a in FLOW_ASSERTIONS:
            a = dict(a)
            FlowAssertion.objects.update_or_create(
                assertion_id=a.pop("assertion_id"), defaults=a,
            )
        self.stdout.write(f"  {len(FLOW_ASSERTIONS)} flow assertions")

    # ─────────────────────────────────────────────────────────────────────────
    # Report
    # ─────────────────────────────────────────────────────────────────────────

    def _report_totals(self, form):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(
            f"4562 destination/rounding amendment seeded onto form v{form.version}."))
        self.stdout.write(
            f"  facts +{len(NEW_FACTS)} · rules +{len(RULES)} · "
            f"diagnostics +{len(DIAGNOSTICS)} · tests +{len(SCENARIOS)} · "
            f"excerpts +{len(NEW_EXCERPTS_ON_EXISTING)} · FA {len(FLOW_ASSERTIONS)}")
        self.stdout.write("=" * 60)
