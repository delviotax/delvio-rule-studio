"""Amend Form 4562 with basis fidelity + §280F caps in the AMT/state parallel arms.

WHY (QA Batch-001 item 6 Leg 3 / delvio s118, under Ken's four-part design GO of
2026-07-26 — Design/item6_depreciation_rebuild_proposal.md, "Leg 3 add-fields-only"
pick on record): the asset model carries ONE basis field (the depreciable basis the
engine consumes). A converted asset whose depreciable basis differs from its
original cost — the QA fleet's Barn: original cost 9,010, depreciable basis 4,505
after a historical 50% special depreciation allowance — cannot be represented
faithfully: the prior bonus must be lumped into prior regular depreciation, the
original cost is simply lost, and disposal math + §1250 additional-depreciation
math then start from the WRONG basis. Separately, the §280F passenger-automobile
caps were applied in the FEDERAL arm only (delvio s46 boundary #3): the AMT
refigure and the Georgia parallel computed UNCAPPED amounts on under-6,000-lb
vehicles — the GA arm materially over-deducts on any expensive auto (full-basis
MACRS with no bonus and no cap).

This loader AMENDS the existing multi-entity 4562 form ADDITIVELY (the
load_4562_destination_rounding pattern — looks up the TaxForm, never re-creates,
entity_types untouched):
  - adds facts `original_cost` + `prior_bonus_depreciation` (the split basis
    history; `depreciable_basis` remains the engine input, unchanged)
  - adds R018 (basis fidelity: accumulated depreciation / adjusted basis are
    DERIVED from the split fields; disposal + §1250 additional-depreciation math
    start from original cost) + R019 (§280F caps bind the AMT and state
    parallel arms; GA cap = the no-§168(k)-bump table)
  - adds diagnostic D_4562_BASIS (impossible/unreconciled basis history) under
    the canonical app code (specs.0003 40-char rule)
  - adds the verified §280F(a)(1)(A) excerpt on the existing IRC_280F source
  - adds 3 test scenarios (the Barn split-keying pin; the AMT-refigure cap pin;
    the GA no-bump cap pin)
  - stages flow assertion FA-4562-280F-01

LAW / SOURCE BASIS (verified 2026-07-26 against the cited texts, not memory):
  - §280F(a)(1)(A) VERBATIM: "The amount of the depreciation deduction for any
    taxable year for any passenger automobile shall not exceed—" [the annual
    dollar caps]. The cap binds THE DEPRECIATION DEDUCTION ITSELF, with no
    computation-method carve-out — so the §56(a)(1) AMT refigure of the same
    deduction is capped at the same dollars. FLAGGED per the Authoritative-
    Source Rule: the 2025 i6251 line 2l text is SILENT on §280F (checked
    2026-07-26) — the AMT-arm cap is a statutory derivation from §280F(a)(1)(A)
    matching the industry benchmark (TaxWise caps the AMT column identically),
    NOT quoted instruction text. In practice the AMT arm diverges from the
    already-capped federal arm only on the R007 refigure class (200DB
    never-bonus-eligible property recomputed at 150DB).
  - §168(k)(2)(F)(i): the special-allowance regime increases the
    §280F(a)(1)(A)(i) FIRST-YEAR limitation by $8,000 — this is exactly the
    Rev. Proc. 2025-16 Table 1 ($20,200) vs Table 2 ($12,200) difference; the
    year-2+ caps are identical in both tables. Georgia does NOT conform to
    §168(k) (delvio verified rule, GA-600S Schedule 1 add-back regime), so the
    $8,000 bump never exists for Georgia: the GA parallel arm caps at the
    NO-BONUS table ($12,200 first year for 2025).
  - Adjusted basis / accumulated depreciation: §1016(a)(2) requires basis
    reduction for depreciation "allowed or allowable" — original cost less ALL
    depreciation components (prior regular + prior bonus + §179 prior/elected +
    current bonus + current regular). The i4797 line-26a convention (SL
    equivalent figured on basis NOT reduced by the special allowance) is
    already spec-homed on the 4797; the split fields make that computation
    possible for converted assets (it was silently wrong on any asset keyed
    net-of-bonus).

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
# in-session AskUserQuestion, delvio s116 ("GO" on the four-leg build with the
# Leg-3 "add-fields-only" field-naming pick). Seeding proceeds under that GO;
# the two flagged judgment calls (AMT-arm cap as statutory derivation, GA cap
# at the no-bump table) land in delvio REVIEW_QUEUE for final ratification
# alongside the build leg — the R017 precedent.
# ═══════════════════════════════════════════════════════════════════════════
READY_TO_SEED = True


FORM_NUMBER = "4562"
FORM_JURISDICTION = "FED"
FORM_TAX_YEAR = 2025


# ═══════════════════════════════════════════════════════════════════════════
# NEW FACTS — the split basis history
# ═══════════════════════════════════════════════════════════════════════════

NEW_FACTS: list[dict] = [
    {"fact_key": "original_cost",
     "label": "Original cost / unadjusted basis",
     "data_type": "decimal", "required": False, "default_value": None, "sort_order": 32,
     "notes": ("What was paid for the asset (unadjusted basis), BEFORE any historical "
               "basis reductions. Blank ⇒ equals depreciable_basis (every pre-Leg-3 "
               "asset; behavior unchanged). The engine's current-year computation still "
               "consumes depreciable_basis — original_cost feeds the DERIVED figures "
               "(accumulated depreciation, adjusted basis) and the disposal + §1250 "
               "additional-depreciation math (R018).")},
    {"fact_key": "prior_bonus_depreciation",
     "label": "Special depreciation allowance taken in prior years",
     "data_type": "decimal", "required": False, "default_value": "0", "sort_order": 33,
     "notes": ("Historical §168(k) special allowance on THIS asset, held separately from "
               "prior regular depreciation (it was previously lumped into "
               "prior_depreciation, making the record lossy). Expected keying identity "
               "for a converted asset: depreciable_basis = original_cost − "
               "prior_bonus_depreciation − prior §179 (D_4562_BASIS nudges deviations; "
               "legitimate exceptions exist — credit basis reductions, carryover basis).")},
]


# ═══════════════════════════════════════════════════════════════════════════
# RULES — R018 (basis fidelity) + R019 (§280F in the parallel arms)
# ═══════════════════════════════════════════════════════════════════════════

RULES: list[dict] = [
    {"rule_id": "R018", "title": "Basis fidelity — split history, derived accumulated depreciation and adjusted basis",
     "rule_type": "calculation",
     "formula": ("accumulated_depreciation = prior_depreciation + prior_bonus_depreciation "
                 "+ sec_179_prior + sec_179_elected + bonus_amount + current_depreciation; "
                 "adjusted_basis = (original_cost or depreciable_basis) − accumulated_depreciation; "
                 "disposal: gain = sales_price − expenses_of_sale − adjusted_basis; "
                 "§1250 additional-depreciation SL equivalent figured on (original_cost or "
                 "depreciable_basis) − §179 (basis NOT reduced by the special allowance, "
                 "i4797 line 26a); AMT parallel uses amt_prior/amt_current with the same shape"),
     "inputs": ["original_cost", "prior_bonus_depreciation", "depreciable_basis"],
     "outputs": ["accumulated_depreciation", "adjusted_basis"],
     "precedence": 7, "sort_order": 18,
     "description": (
         "QA Batch-001 item 6 Leg 3 (delvio s118, Ken's 'add-fields-only' pick 2026-07-26). "
         "The asset record splits basis history instead of losing it: original_cost is the "
         "unadjusted basis (§1012), depreciable_basis remains the engine's current-year input "
         "(UNCHANGED — no recompute change for existing assets), and prior_bonus_depreciation "
         "holds the historical special allowance separately from prior regular depreciation. "
         "Accumulated depreciation is DERIVED as the sum of every depreciation component "
         "('allowed or allowable', §1016(a)(2)); adjusted basis = original cost less that sum. "
         "Disposal math and the §1250 additional-depreciation SL equivalent start from "
         "original_cost — on an asset keyed net-of-bonus (the only representation possible "
         "before the split), both started from the WRONG basis. A blank original_cost means "
         "'equal to depreciable_basis', preserving every pre-Leg-3 asset byte-for-byte. "
         "The Barn pin: original 9,010 / prior bonus 4,505 / depreciable 4,505 keys faithfully, "
         "current-year depreciation is unchanged, and adjusted basis reconciles to the packet."),
     "notes": "Companion to the app's disposal recompute + card display; the engine's current-year math is untouched by design."},
    {"rule_id": "R019", "title": "§280F caps bind the AMT and state parallel computations",
     "rule_type": "calculation",
     "formula": ("under_6000: amt_total(year) <= rp_2025_16_table(year_in_service, "
                 "federal_bonus_claimed) * business_pct; "
                 "state_GA_total(year) <= rp_2025_16_table(year_in_service, NO_BONUS) * business_pct; "
                 "over_6000 / work_truck_6ft: no §280F caps in any arm (same as federal)"),
     "inputs": ["vehicle_classification", "amt_method", "bonus_depreciation_amount"],
     "outputs": ["capped_amt_depreciation", "capped_state_depreciation"],
     "precedence": 14, "sort_order": 19,
     "description": (
         "Closes delvio s46 boundary #3 (federal-arm-only caps). §280F(a)(1)(A) caps 'the "
         "amount of the depreciation deduction for any taxable year' — the cap binds the "
         "DEDUCTION itself with no computation-method carve-out, so the §56(a)(1) AMT "
         "refigure of that deduction is capped at the SAME dollars and the same table "
         "(bonus is fully allowed for AMT, so table selection follows the federal arm). "
         "FLAGGED per the Authoritative-Source Rule: the 2025 i6251 line 2l is SILENT on "
         "§280F (checked 2026-07-26) — the AMT-arm cap is a statutory derivation matching "
         "the industry benchmark, not quoted instruction text. In practice it diverges from "
         "the capped federal amount only on the R007 refigure class (200DB never-bonus-"
         "eligible property recomputed at 150DB). GEORGIA: GA does not conform to §168(k), "
         "and the $8,000 first-year cap increase IS §168(k)(2)(F)(i) — for Georgia the bump "
         "never exists, so the GA parallel caps at the NO-BONUS table (Rev. Proc. 2025-16 "
         "Table 2, $12,200 first year for 2025; year-2+ caps are identical in both tables). "
         "Caps prorate by business-use percentage, mirroring R008."),
     "notes": ("Two judgment calls staged for Ken's ratification (delvio REVIEW_QUEUE): "
               "(1) AMT-arm cap as §280F(a)(1)(A) statutory derivation; (2) GA cap at the "
               "no-bump table via §168(k)(2)(F)(i) nonconformity.")},
]

RULE_LINKS: list[tuple[str, str, str, str]] = [
    ("R018", "IRS_2025_4562_INSTR_FULL", "primary",
     "Part III col (c) 'Basis for depreciation' vs cost — the split the record must carry"),
    ("R018", "IRS_PUB_946", "secondary",
     "Adjusted-basis / depreciation-allowed-or-allowable framework (§1016(a)(2))"),
    ("R019", "IRC_280F", "primary",
     "§280F(a)(1)(A) — the cap binds 'the amount of the depreciation deduction', method-independent (AMT arm)"),
    ("R019", "IRS_RP_2025_16", "primary",
     "2025 Tables 1/2 — the $8,000 §168(k)(2)(F)(i) bump is the only difference (GA arm = Table 2)"),
    ("R019", "IRC_168", "primary",
     "§168(k)(2)(F)(i) — the first-year cap increase Georgia never conforms to"),
    ("R019", "IRS_2025_6251_INSTR", "secondary",
     "Line 2l SILENT on §280F (checked 2026-07-26) — the flagged gap behind the statutory derivation"),
]


# ═══════════════════════════════════════════════════════════════════════════
# DIAGNOSTIC — canonical app code VERBATIM (specs.0003 widened id to 40)
# ═══════════════════════════════════════════════════════════════════════════

DIAGNOSTICS: list[dict] = [
    {"diagnostic_id": "D_4562_BASIS", "title": "Asset basis history does not reconcile",
     "severity": "error",
     "condition": ("original_cost is set AND original_cost < depreciable_basis → ERROR "
                   "(impossible: the depreciable basis exceeds what was paid — depreciation "
                   "is being over-claimed). original_cost is set AND original_cost − "
                   "prior_bonus_depreciation − sec_179_prior ≠ depreciable_basis → WARNING "
                   "(the history doesn't account for the gap; legitimate causes exist — "
                   "credit basis reductions, carryover basis — so the preparer may "
                   "acknowledge with a note). SEVERITY IS EFFECT-SCALED like D_4562_DEST."),
     "message": ("Asset '{description}': original cost {original_cost} minus recorded "
                 "prior bonus/§179 does not equal the depreciable basis {depreciable_basis}. "
                 "Check the basis history — or acknowledge with the reason (e.g. a credit "
                 "basis reduction)."),
     "notes": ("Leg 3 (delvio s118). Fires only when original_cost is SET — the pre-Leg-3 "
               "fleet (null original_cost) is untouched. The error arm guards impossible "
               "over-depreciation; the warning arm is an ackable reconciliation nudge.")},
]


# ═══════════════════════════════════════════════════════════════════════════
# TEST SCENARIOS
# ═══════════════════════════════════════════════════════════════════════════

SCENARIOS: list[dict] = [
    {"scenario_name": "Barn split-keying — faithful basis history, unchanged current-year result",
     "scenario_type": "normal",
     "inputs": {"original_cost": 9010, "prior_bonus_depreciation": 4505,
                "depreciable_basis": 4505, "prior_depreciation": 1200,
                "current_year_depreciation": 266},
     "expected_outputs": {"current_year_depreciation": 266,
                          "accumulated_depreciation": 5971,
                          "adjusted_basis": 3039,
                          "diagnostics": []},
     "notes": ("R018: the QA Barn keys faithfully (9,010 / 4,505 historical special "
               "allowance / 4,505 depreciable). Current-year math is untouched (266 — the "
               "engine still consumes depreciable_basis); accumulated = 1,200 + 4,505 + 266 "
               "= 5,971; adjusted = 9,010 − 5,971 = 3,039. The identity 9,010 − 4,505 = "
               "4,505 holds, so no D_4562_BASIS."),
     "sort_order": 34},
    {"scenario_name": "§280F caps the AMT refigure — never-eligible 200DB under-6000 auto",
     "scenario_type": "edge",
     "inputs": {"vehicle_classification": "under_6000", "depreciable_basis": 100000,
                "depreciation_method": "200DB", "recovery_period": 5, "bonus_eligible": False,
                "bonus_percentage": 0, "year_in_service": 1},
     "expected_outputs": {"current_year_depreciation": 12200,
                          "amt_current_depreciation": 12200},
     "notes": ("R019 AMT arm: federal 200DB yr1 = 20,000 → capped 12,200 (no-bonus table). "
               "AMT refigures at 150DB (R007 never-eligible class) = 15,000 UNCAPPED — the "
               "s46 boundary bug — now capped at the same 12,200."),
     "sort_order": 35},
    {"scenario_name": "§280F caps the Georgia arm at the NO-BONUS table",
     "scenario_type": "edge",
     "inputs": {"vehicle_classification": "under_6000", "depreciable_basis": 100000,
                "depreciation_method": "200DB", "recovery_period": 5, "bonus_eligible": True,
                "bonus_percentage": 100, "year_in_service": 1},
     "expected_outputs": {"current_year_depreciation": 20200,
                          "state_current_depreciation": 12200},
     "notes": ("R019 GA arm: federal bonus 100,000 → Table 1 cap 20,200. Georgia disallows "
               "bonus → full-basis MACRS 20,000, previously UNCAPPED (the material GA "
               "over-deduction) — now capped at Table 2's 12,200 (no §168(k)(2)(F)(i) bump "
               "for a nonconforming state)."),
     "sort_order": 36},
]


# ═══════════════════════════════════════════════════════════════════════════
# NEW EXCERPT on the EXISTING IRC_280F source — VERBATIM statutory text
# (verified 2026-07-26 against 26 U.S.C. §280F).
# ═══════════════════════════════════════════════════════════════════════════

NEW_EXCERPTS_ON_EXISTING: list[tuple[str, dict]] = [
    ("IRC_280F", {
        "excerpt_label": "§280F(a)(1)(A) — the cap binds the depreciation deduction itself",
        "location_reference": "26 U.S.C. §280F(a)(1)(A)",
        "excerpt_text": (
            "The amount of the depreciation deduction for any taxable year for any "
            "passenger automobile shall not exceed—"),
        "summary_text": ("The limitation attaches to the deduction, with no computation-"
                         "method carve-out — the basis for capping the §56(a)(1) AMT "
                         "refigure (and every parallel arm) at the same dollars."),
        "is_key_excerpt": True,
    }),
]


# ═══════════════════════════════════════════════════════════════════════════
# FLOW ASSERTION (staged; the app leg activates its pins in its own gate)
# ═══════════════════════════════════════════════════════════════════════════

FLOW_ASSERTIONS: list[dict] = [
    {"assertion_id": "FA-4562-280F-01", "assertion_type": "flow_assertion",
     "entity_types": ["1040", "1120S", "1065", "1120"],
     "title": "Under-6,000-lb auto: every arm's annual amount respects its §280F cap",
     "description": ("Validates R019. For an under_6000 vehicle: federal, AMT, and state "
                     "current-year amounts each ≤ their applicable RP 2025-16 cap × "
                     "business %. AMT/federal use the federal-bonus table; state (GA) uses "
                     "the no-bonus table. Bug it catches: the s46 boundary — an uncapped "
                     "AMT refigure or an uncapped full-basis GA amount on an expensive "
                     "auto."),
     "definition": {"kind": "formula_check", "form": "4562",
                    "formula": ("amt_current <= cap(year, federal_bonus) * business_pct AND "
                                "state_current <= cap(year, no_bonus) * business_pct")},
     "sort_order": 7},
]


# ═══════════════════════════════════════════════════════════════════════════
# Command
# ═══════════════════════════════════════════════════════════════════════════

class Command(BaseCommand):
    help = (
        "Amend Form 4562 with basis fidelity (original_cost / prior_bonus_depreciation "
        "split, R018) and §280F caps in the AMT/state parallel arms (R019 + "
        "D_4562_BASIS). AMENDS the existing multi-entity 4562 form additively "
        "(entity_types untouched)."
    )

    @transaction.atomic
    def handle(self, *args, **opts):
        self._guard_against_hollow_seed()

        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nAmend Form 4562 — basis fidelity + §280F parallel-arm caps\n"))

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
                "REFUSING TO SEED 4562 basis-fidelity amendment.\n"
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
    # Upsert helpers (mirror load_4562_destination_rounding.py)
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
        self.stdout.write(f"  {len(created)} rules (R018/R019 new)")
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
            f"4562 basis-fidelity amendment seeded onto form v{form.version}."))
        self.stdout.write(
            f"  facts +{len(NEW_FACTS)} · rules +{len(RULES)} · "
            f"diagnostics +{len(DIAGNOSTICS)} · tests +{len(SCENARIOS)} · "
            f"excerpts +{len(NEW_EXCERPTS_ON_EXISTING)} · FA {len(FLOW_ASSERTIONS)}")
        self.stdout.write("=" * 60)
