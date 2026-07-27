"""Amend Form 4562's D_4562_RECON so the §179 business-income limitation stops
reading as a routing failure (delvio s124).

THE DEFECT THIS FIXES (found live on production, 2026-07-27)
------------------------------------------------------------
`D_4562_RECON` (added by load_4562_destination_rounding, s116) is the permanent
guard against the silent-skip class: for each destination, the sum of the
rounded per-asset amounts must equal what the destination line carries. Its
condition, as authored, is unconditional equality — and it is WRONG whenever the
§179 business-income limitation bites.

Worked case, all three numbers correct: $10,000 of equipment fully elected under
§179 against $8,000 of Schedule C income. Form 4562 line 11 = 8,000, line 12 =
8,000, line 13 = 2,000 carries to next year, and Schedule C line 13 correctly
carries the ALLOWED 8,000. The asset module still holds the full 10,000
election, so the rule compares 10,000 against 8,000 and tells the preparer
"The difference would file a wrong return." The return is right; the guard is
wrong. It hits the ordinary small-Schedule-C-buys-equipment pattern, and the
danger is a preparer "correcting" a correct return.

THE AMENDMENT
-------------
Reconcile in TWO parts instead of one, so the guard survives intact while the
limitation's legitimate difference is accounted for:

  (a) PER DESTINATION — the destination must carry at least the NON-§179 asset
      total. Anything less means non-§179 depreciation failed to route (the
      original silent-skip class), and that is still a blocking error.
  (b) ACROSS THE RETURN — the §179 that actually landed (destination minus its
      non-§179 total, summed over the §179-participating destinations) must
      equal Form 4562 LINE 12. Not the elected amount, not line 9 — line 12,
      the allowed deduction after the limitation.

Where no §179 is in play at all (line 12 = 0 and no prior-year carryover) the
rule keeps today's strict per-destination equality unchanged. So (a)+(b) are
strictly STRONGER than the present check for the ordinary return and merely
stop accusing the limited one: a routing gap in a §179 return now fails (b) —
the landed total no longer ties to line 12 — where before the whole return was
already failing for a benign reason and the real gap was indistinguishable.

Adds R020 (the reconciliation basis), amends the D_4562_RECON condition/message/
notes, and adds four scenarios including the false-positive NEGATIVE CONTROL and
a genuine gap that must still fire underneath an active limitation.

LAW / SOURCE BASIS (verified 2026-07-27 against the local SHA-tracked template
resources/irs_forms/2025/f4562.pdf via pymupdf — NOT memory):
  - Line 11, VERBATIM: "Business income limitation. Enter the smaller of
    business income (not less than zero) or line 5. See instructions"
  - Line 12, VERBATIM: "Section 179 expense deduction. Add lines 9 and 10, but
    don't enter more than line 11 ."
  - Line 13, VERBATIM: "Carryover of disallowed deduction to 2026. Add lines 9
    and 10, less line 12"
  Statute: §179(b)(3)(A) limits the deduction to the taxable income derived from
  the active conduct of any trade or business; §179(b)(3)(B) carries the
  disallowed amount forward. So the gap between the elected amount and what
  reaches the activity's line is REQUIRED by law, not a defect — which is
  precisely what the unconditional equality could not express.

ONE JUDGMENT CALL, FLAGGED (Authoritative-Source Rule step 4). An ACCRUAL
Schedule F is excluded from the app's §179 limitation entirely — the whole farm
RED-defers as unsupported (D_SF_ACCRUAL), so its destination keeps the full
election and its §179 is not in line 12. Part (b) therefore scopes accrual farms
OUT of its sum. The IRS source says nothing about this (it is an artifact of the
app's v1 cash-method-only farm support, not of §179), so it is recorded here as
a scoping decision and logged for Ken's ratification, not as quoted authority.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from sources.models import AuthoritySource, RuleAuthorityLink
from specs.models import (
    FormDiagnostic,
    FormRule,
    TaxForm,
    TestScenario,
)


# ═══════════════════════════════════════════════════════════════════════════
# SAFETY GUARD — Ken's approval is ON RECORD for this unit: 2026-07-27,
# in-session AskUserQuestion (delvio s124), "Fix it properly" over the
# downgrade-to-warning and defer options, after being shown the worked
# 10,000-against-8,000 case and the two-part reconciliation this loader
# authors. The accrual-farm scoping rides to REVIEW_QUEUE for ratification.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = True


FORM_NUMBER = "4562"
FORM_JURISDICTION = "FED"
FORM_TAX_YEAR = 2025


# ═══════════════════════════════════════════════════════════════════════════
# RULE — R020: what a destination is reconciled AGAINST once §179 is in play
# ═══════════════════════════════════════════════════════════════════════════

RULES: list[dict] = [
    {"rule_id": "R020",
     "title": "Destination reconciliation basis under the §179 business-income limitation",
     "rule_type": "validation",
     "formula": (
         "non_179_total[dest] = sum over assets routed to dest of "
         "(rounded current-year depreciation - rounded §179 elected); "
         "landed_179[dest] = destination_value[dest] - non_179_total[dest]; "
         "REQUIRE landed_179[dest] >= 0 for every destination; "
         "REQUIRE sum(landed_179[dest] over §179-participating destinations) == line_12"
     ),
     "inputs": ["current_year_depreciation", "section_179_elected",
                "flow_destination", "activity_reference"],
     "outputs": ["destination_total"],
     "precedence": 7, "sort_order": 20,
     "description": (
         "A destination line is NOT simply the sum of the amounts routed to it once §179 is "
         "elected. Form 4562 line 12 (2025 face, verbatim) is 'Section 179 expense deduction. "
         "Add lines 9 and 10, but don't enter more than line 11', and line 11 is the 'Business "
         "income limitation' — so under §179(b)(3)(A) the allowed deduction is capped at the "
         "taxable income from the active conduct of the trade or business, and §179(b)(3)(B) "
         "carries the disallowed remainder to the next year (line 13, 'Carryover of disallowed "
         "deduction to 2026'). The activity's own line (Schedule C 13 / Schedule F 14, where "
         "§179 stays IN the total per R-SC-DEPR / R-SF-DEPR) therefore carries the ALLOWED "
         "share, while the asset module still holds the full election. The difference is "
         "required by law. Reconciliation is consequently TWO-PART: (a) per destination, the "
         "line must carry at least the non-§179 total routed there — less than that means "
         "ordinary depreciation failed to route, the original silent-skip class; (b) across the "
         "return, the §179 that actually landed must equal LINE 12 — not the elected amount and "
         "not line 9. Where the return has no §179 at all (line 12 = 0 with no prior-year "
         "carryover on line 10) the two parts collapse back to today's strict per-destination "
         "equality, unchanged."),
     "notes": (
         "Companion to R016 (routing) and R017 (per-asset rounding); it is what D_4562_RECON "
         "compares against. SCOPING DECISION, not IRS text (flagged for Ken): an ACCRUAL "
         "Schedule F is outside the app's §179 limitation because the whole farm RED-defers as "
         "unsupported (cash-method-only v1), so it keeps the full election and is scoped OUT of "
         "part (b)'s sum. Part (b) is also skipped in the rare pure-prior-year-carryover shape "
         "(line 9 = 0, line 10 > 0), where the allowed deduction is distributed by net profit "
         "and can land on an activity that has no depreciation assets at all — part (a) still "
         "applies there."),
     },
]


RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R020", "IRS_2025_4562_INSTR_FULL", "primary",
     "Part I lines 11/12/13 face text — the business income limitation, the capped deduction, "
     "and the carryover of the disallowed remainder"),
]


# ═══════════════════════════════════════════════════════════════════════════
# DIAGNOSTIC — D_4562_RECON amended (update_or_create on diagnostic_id)
# ═══════════════════════════════════════════════════════════════════════════

DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_4562_RECON",
     "title": "Depreciation module does not reconcile to destination lines",
     "severity": "error",
     "condition": (
         "Reconcile per R020, skipping preparer-overridden destination lines. "
         "NO §179 on the return (line 12 = 0 and line 10 = 0): fire when, for any destination, "
         "sum(rounded per-asset amounts routed there) != the destination line's value. "
         "§179 IN PLAY: fire when (a) any destination carries LESS than the non-§179 total "
         "routed to it, or (b) the §179 that landed across the §179-participating destinations "
         "!= line 12. Accrual Schedule F farms are outside the limitation and are scoped out of "
         "(b); (b) is skipped in the pure-prior-year-carryover shape (line 9 = 0, line 10 > 0)."),
     "message": (
         "Depreciation entered on the asset module ({module_total}) does not match what reached "
         "{destination} ({line_value}). The difference would file a wrong return — recalculate, "
         "and if the mismatch persists report it."),
     "notes": (
         "The permanent guard against the silent-skip class: any future routing gap surfaces as "
         "a blocking error instead of a quietly overstated income. Overridden destination lines "
         "are the preparer's call and are skipped. AMENDED 2026-07-27 (delvio s124): the "
         "original unconditional equality raised this blocking error on CORRECT returns whenever "
         "the §179 business-income limitation bit — 10,000 elected against 8,000 of Schedule C "
         "income puts the allowed 8,000 on line 13 and carries 2,000, exactly as §179(b)(3) "
         "requires, and the guard called it a wrong return. Two-part reconciliation (R020) keeps "
         "the guard — a real gap now breaks the tie to line 12 — without accusing the limited "
         "return. Strictly stronger than the original for the no-§179 case, which is unchanged."),
     },
]


# ═══════════════════════════════════════════════════════════════════════════
# TEST SCENARIOS — incl. the false-positive NEGATIVE CONTROL and a genuine
# gap that must still fire with the limitation active
# ═══════════════════════════════════════════════════════════════════════════

SCENARIOS: list[dict] = [
    {"scenario_name": "§179 limited by business income — module 10,000 vs destination 8,000 is CORRECT",
     "scenario_type": "edge",
     "inputs": {"flow_destination": "schedule_c", "activity_reference": "biz-1",
                "asset_amounts": [10000], "section_179_elected": [10000],
                "line_9": 10000, "line_10": 0, "line_11": 8000,
                "line_12": 8000, "line_13": 2000,
                "destination_line_value": 8000},
     "expected_outputs": {"diagnostics": [], "non_179_total": 0, "landed_179": 8000},
     "notes": ("NEGATIVE CONTROL for the s124 false positive. non-§179 total is 0, so the "
               "destination's whole 8,000 is landed §179 and ties to line 12 exactly. The "
               "2,000 gap against the module is the line-13 carryover, required by "
               "§179(b)(3)(B). Under the pre-amendment condition this fired a blocking error "
               "on a correct return."),
     "sort_order": 40},

    {"scenario_name": "Routing gap UNDERNEATH an active §179 limitation — must still fire",
     "scenario_type": "edge",
     "inputs": {"flow_destination": "schedule_c", "activity_reference": "biz-1",
                "asset_amounts": [10000, 1000], "section_179_elected": [10000, 0],
                "line_9": 10000, "line_10": 0, "line_11": 8000,
                "line_12": 8000, "line_13": 2000,
                "destination_line_value": 8000},
     "expected_outputs": {"diagnostics": ["D_4562_RECON"], "non_179_total": 1000,
                          "landed_179": 7000},
     "notes": ("The proof the guard survives. A second, non-§179 asset of 1,000 should make the "
               "destination 9,000 (1,000 ordinary + 8,000 allowed §179); it carries 8,000, so "
               "the 1,000 vanished. landed_179 comes out 7,000 against line 12 of 8,000 — part "
               "(b) breaks. The original condition also fired here, but only by accident: it "
               "was already firing on the benign limitation, so a real gap was invisible."),
     "sort_order": 41},

    {"scenario_name": "Destination below its non-§179 total — part (a) fires",
     "scenario_type": "edge",
     "inputs": {"flow_destination": "schedule_f", "activity_reference": "farm-1",
                "asset_amounts": [4068, 2000], "section_179_elected": [0, 2000],
                "line_9": 2000, "line_10": 0, "line_11": 50000,
                "line_12": 2000, "line_13": 0,
                "destination_line_value": 3000},
     "expected_outputs": {"diagnostics": ["D_4562_RECON"], "non_179_total": 4068,
                          "landed_179": -1068},
     "notes": ("The Benkoski shape with §179 present. The destination carries less than the "
               "ordinary depreciation alone, so landed_179 goes NEGATIVE — impossible, and "
               "caught per destination without waiting for the return-level tie."),
     "sort_order": 42},

    {"scenario_name": "No §179 anywhere — strict equality unchanged",
     "scenario_type": "normal",
     "inputs": {"flow_destination": "schedule_c", "activity_reference": "biz-1",
                "asset_amounts": [1200, 800], "section_179_elected": [0, 0],
                "line_9": 0, "line_10": 0, "line_11": 0, "line_12": 0, "line_13": 0,
                "destination_line_value": 2000},
     "expected_outputs": {"diagnostics": [], "non_179_total": 2000, "landed_179": 0},
     "notes": ("Regression pin: with line 12 = 0 and line 10 = 0 the two-part check collapses "
               "to the original per-destination equality. The overwhelming majority of returns "
               "take this path and see no behaviour change."),
     "sort_order": 43},
]


# ═══════════════════════════════════════════════════════════════════════════
# Command
# ═══════════════════════════════════════════════════════════════════════════

class Command(BaseCommand):
    help = (
        "Amend Form 4562's D_4562_RECON for the §179 business-income limitation: adds "
        "R020 (two-part reconciliation basis), rewrites the diagnostic condition, and "
        "adds four scenarios incl. the false-positive negative control. AMENDS the "
        "existing multi-entity 4562 form additively (entity_types untouched)."
    )

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()

        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nAmend Form 4562 — D_4562_RECON under the §179 income limitation\n"))

        form = self._get_existing_form()
        rules = self._upsert_rules(form, RULES)
        self._upsert_authority_links(rules, RULE_LINKS)
        self._upsert_diagnostics(form, DIAGNOSTICS)
        self._upsert_tests(form, SCENARIOS)
        self._report_totals(form)

    # ─────────────────────────────────────────────────────────────────────────
    # Safety guard
    # ─────────────────────────────────────────────────────────────────────────

    def _guard_against_hollow_seed(self):
        empty = [name for name, seq in (
            ("RULES", RULES), ("DIAGNOSTICS", DIAGNOSTICS),
            ("SCENARIOS", SCENARIOS), ("RULE_LINKS", RULE_LINKS),
        ) if not seq]

        # id-length guard — diagnostic_id is varchar(40) since specs.0003 (s115);
        # rule_id remains varchar(20).
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
                "REFUSING TO SEED the 4562 D_4562_RECON §179 amendment.\n"
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
                form_number=FORM_NUMBER, jurisdiction=FORM_JURISDICTION,
                tax_year=FORM_TAX_YEAR,
            )
            .order_by("version")
            .first()
        )
        if not form:
            raise CommandError(
                f"Form {FORM_NUMBER} ({FORM_JURISDICTION} {FORM_TAX_YEAR}) not found — run "
                "load_4562_destination_rounding first. This loader only AMENDS it."
            )
        if not FormDiagnostic.objects.filter(
                tax_form=form, diagnostic_id="D_4562_RECON").exists():
            raise CommandError(
                "D_4562_RECON is not on this form — run load_4562_destination_rounding "
                "(s116) first. This loader AMENDS that diagnostic, it does not introduce it."
            )
        self.stdout.write(
            f"Amending {FORM_NUMBER} v{form.version} "
            f"(entity_types={form.entity_types} — untouched)")
        return form

    # ─────────────────────────────────────────────────────────────────────────
    # Upsert helpers (mirror load_4562_destination_rounding.py)
    # ─────────────────────────────────────────────────────────────────────────

    def _upsert_rules(self, form, rules_data) -> dict:
        created = {}
        for r in rules_data:
            r = dict(r)
            rule, _ = FormRule.objects.update_or_create(
                tax_form=form, rule_id=r.pop("rule_id"), defaults=r,
            )
            created[rule.rule_id] = rule
        self.stdout.write(f"  {len(created)} rules (R020 new)")
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
                self.stdout.write(self.style.WARNING(
                    f"  source {source_code} not found — link skipped"))
        self.stdout.write(f"  {ct} authority links")

    def _upsert_diagnostics(self, form, diagnostics):
        for d in diagnostics:
            d = dict(d)
            FormDiagnostic.objects.update_or_create(
                tax_form=form, diagnostic_id=d.pop("diagnostic_id"), defaults=d,
            )
        self.stdout.write(f"  {len(diagnostics)} diagnostics AMENDED (canonical app codes)")

    def _upsert_tests(self, form, scenarios):
        for t in scenarios:
            t = dict(t)
            TestScenario.objects.update_or_create(
                tax_form=form, scenario_name=t.pop("scenario_name"), defaults=t,
            )
        self.stdout.write(f"  {len(scenarios)} scenarios")

    def _report_totals(self, form):
        self.stdout.write(self.style.SUCCESS(
            f"\nForm {FORM_NUMBER} now holds: "
            f"{form.rules.count()} rules · "
            f"{form.diagnostics.count()} diagnostics · "
            f"{form.test_scenarios.count()} scenarios\n"))
