"""Throwaway-SQLite validation for the 8867 per-question rebuild
(QA Batch-001 item 11, 2026-07-26) inside load_1040_eic.py.

Checks: the loader seeds; the 8867 line map is EXACTLY the Rev. 11-2024 face
(21 answerable lines incl. 5_docs); the N/A vocabulary exists ONLY on the seven
lines whose printed face has an N/A checkbox (widget truth == XSD truth);
every line sources a defined fact and every answer fact is sourced by exactly
one line; CharField caps; D_8867_002 retired; the stale-artifact prune deletes
pre-planted compressed-model rows and is a no-op on re-run; the F8867-T6
cascade scenario is internally consistent with the authored choice vocabularies.
ASCII-only. Run: poetry run python scratchpad/validate_8867_rebuild.py
"""
import os
import sys

PROJECT_ROOT = r"D:\dev\sherpa-tax-rule-studio"
sys.path.insert(0, PROJECT_ROOT)

SQLITE_PATH = os.path.join(PROJECT_ROOT, "scratchpad", "validate_8867_rebuild.sqlite3")
if os.path.exists(SQLITE_PATH):
    os.remove(SQLITE_PATH)
os.environ["DATABASE_URL"] = f"sqlite:///{SQLITE_PATH}"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

import django  # noqa: E402
django.setup()

from django.core.management import call_command  # noqa: E402
from specs.models import FormDiagnostic, FormFact, FormLine, FormRule, TaxForm, TestScenario  # noqa: E402
from specs.management.commands import load_1040_eic as L  # noqa: E402

FAILURES: list[str] = []
PASSES: list[str] = []


def check(cond, ok, bad):
    (PASSES if cond else FAILURES).append(ok if cond else bad)


call_command("migrate", run_syncdb=True, verbosity=0)

# ── Pre-plant the compressed-model artifacts so the prune has something real
#    to retire (a fresh SQLite otherwise never contains them). ──
form_stub, _ = TaxForm.objects.update_or_create(
    form_number="8867", jurisdiction=L.FORM_JURISDICTION,
    tax_year=L.FORM_TAX_YEAR, version=L.FORM_VERSION,
    defaults={"form_title": "stub", "entity_types": ["1040"], "status": "draft", "notes": ""},
)
FormLine.objects.update_or_create(tax_form=form_stub, line_number="9",
                                  defaults={"description": "old merged 9", "line_type": "input"})
FormLine.objects.update_or_create(tax_form=form_stub, line_number="hoh",
                                  defaults={"description": "old hoh", "line_type": "input"})
FormFact.objects.update_or_create(tax_form=form_stub, fact_key="f8867_q9_eic",
                                  defaults={"label": "old merged", "data_type": "boolean"})
FormFact.objects.update_or_create(tax_form=form_stub, fact_key="f8867_q8_recertification",
                                  defaults={"label": "old 7a-as-8", "data_type": "boolean"})
FormDiagnostic.objects.update_or_create(tax_form=form_stub, diagnostic_id="D_8867_002",
                                        defaults={"title": "retired AOTC RED", "severity": "error",
                                                  "condition": "x", "message": "x"})

try:
    call_command("load_1040_eic", verbosity=0)
    PASSES.append("load_1040_eic ran + seeded into SQLite without error")
except Exception as e:  # noqa: BLE001
    FAILURES.append(f"load_1040_eic raised: {e!r}")
    print("\n".join(FAILURES))
    sys.exit(1)

form = TaxForm.objects.get(form_number="8867")

# ── The face: exactly these 21 lines (Rev. 11-2024, verified against the
#    template PDF text + AcroForm widget dump + IRS8867.xsd, all 2026-07-26) ──
EXPECTED_LINES = ["1", "2", "3", "4", "4a", "4b", "5", "5_docs", "6", "7", "7a", "8",
                  "9a", "9b", "9c", "10", "11", "12", "13", "14", "15"]
db_lines = set(FormLine.objects.filter(tax_form=form).values_list("line_number", flat=True))
check(db_lines == set(EXPECTED_LINES),
      f"line map is exactly the 21-entry Rev. 11-2024 face",
      f"line map mismatch: extra={sorted(db_lines - set(EXPECTED_LINES))} missing={sorted(set(EXPECTED_LINES) - db_lines)}")

# ── N/A vocabulary only where the printed face has an N/A checkbox ──
NA_LINES = {"2", "7", "7a", "8", "9c", "11", "12"}
facts = {f.fact_key: f for f in FormFact.objects.filter(tax_form=form)}
line_to_fact = {}
for ln in FormLine.objects.filter(tax_form=form):
    sf = ln.source_facts or []
    check(len(sf) == 1 and sf[0] in facts,
          f"line {ln.line_number} sources exactly one defined fact",
          f"line {ln.line_number} source_facts broken: {sf}")
    if sf:
        line_to_fact[ln.line_number] = sf[0]

for line_no, fk in line_to_fact.items():
    f = facts.get(fk)
    if f is None:
        continue
    if line_no == "5_docs":
        check(f.data_type == "string", "5_docs fact is string (free-text documents list)",
              f"5_docs fact data_type={f.data_type} (want string)")
        continue
    choices = set(f.choices or [])
    if line_no in NA_LINES:
        check(choices == {"yes", "no", "na"},
              f"line {line_no} vocabulary yes/no/na (face has an N/A box)",
              f"line {line_no} choices={sorted(choices)} (want yes/no/na)")
    else:
        check(choices == {"yes", "no"},
              f"line {line_no} vocabulary yes/no (face has NO N/A box)",
              f"line {line_no} choices={sorted(choices)} (want yes/no — the face has no N/A checkbox here)")

# every non-header answer fact is sourced by exactly one line
header_keys = {"f8867_claims_eic", "f8867_claims_ctc_actc_odc", "f8867_claims_aotc", "f8867_claims_hoh"}
answer_keys = set(facts) - header_keys
sourced = set(line_to_fact.values())
check(answer_keys == sourced,
      "every answer fact is sourced by exactly one line (no orphans)",
      f"fact/line mismatch: unsourced={sorted(answer_keys - sourced)} unknown={sorted(sourced - answer_keys)}")

# ── CharField caps ──
for r in FormRule.objects.filter(tax_form=form):
    check(len(r.rule_id) <= 20, f"rule_id {r.rule_id} <= 20", f"rule_id {r.rule_id} > 20")
for d in FormDiagnostic.objects.filter(tax_form=form):
    check(len(d.diagnostic_id) <= 20, f"diagnostic_id {d.diagnostic_id} <= 20", f"diagnostic_id {d.diagnostic_id} > 20")
for ln_no in db_lines:
    check(len(ln_no) <= 20, f"line_number {ln_no} <= 20", f"line_number {ln_no} > 20")
for fk in facts:
    check(len(fk) <= 100, f"fact_key {fk} <= 100", f"fact_key {fk} > 100")

# ── The prune retired the compressed model ──
diag_ids = set(FormDiagnostic.objects.filter(tax_form=form).values_list("diagnostic_id", flat=True))
check("D_8867_002" not in diag_ids, "D_8867_002 retired (Form 8863 is built)",
      "D_8867_002 still in the catalogue")
check(diag_ids == {"D_8867_001"}, "diagnostics are exactly {D_8867_001}",
      f"unexpected diagnostics: {sorted(diag_ids)}")
check("f8867_q9_eic" not in facts and "f8867_q8_recertification" not in facts,
      "old merged fact keys pruned", "old merged fact keys survive")
check("9" not in db_lines and "hoh" not in db_lines,
      "old merged lines 9/hoh pruned", "old merged lines survive")

# ── Prune idempotency: a second run deletes nothing and changes nothing ──
before = (FormLine.objects.filter(tax_form=form).count(),
          FormFact.objects.filter(tax_form=form).count(),
          FormDiagnostic.objects.filter(tax_form=form).count(),
          TestScenario.objects.filter(tax_form=form).count())
call_command("load_1040_eic", verbosity=0)
after = (FormLine.objects.filter(tax_form=form).count(),
         FormFact.objects.filter(tax_form=form).count(),
         FormDiagnostic.objects.filter(tax_form=form).count(),
         TestScenario.objects.filter(tax_form=form).count())
check(before == after, f"re-run is a no-op (lines/facts/diags/tests {after})",
      f"re-run changed counts: {before} -> {after}")

# ── Scenarios: exactly the authored six; T6 cascade expectations respect the
#    per-line vocabularies (a Y/N-only line never expects 'na', etc.) ──
scen = {t.scenario_name: t for t in TestScenario.objects.filter(tax_form=form)}
check(len(scen) == 6, "6 scenarios seeded", f"{len(scen)} scenarios (want 6)")
t6 = next((t for n, t in scen.items() if "attestation cascade" in n), None)
check(t6 is not None, "T6 cascade scenario present", "T6 cascade scenario missing")
if t6 is not None:
    exp = t6.expected_outputs
    q_to_line = {"q1": "1", "q2": "2", "q3": "3", "q4": "4", "q4a": "4a", "q4b": "4b",
                 "q5": "5", "q6": "6", "q7": "7", "q7a": "7a", "q8": "8",
                 "q9a": "9a", "q9b": "9b", "q9c": "9c", "q10": "10", "q11": "11",
                 "q12": "12", "q13": "13", "q14": "14", "q15": "15"}
    for qk, line_no in q_to_line.items():
        v = exp.get(qk)
        if v is None:
            continue
        fk = line_to_fact.get(line_no)
        allowed = set((facts[fk].choices or [])) if fk in facts else set()
        check(v in allowed,
              f"T6 {qk}={v} is a legal answer for line {line_no}",
              f"T6 {qk}={v} NOT in line {line_no} vocabulary {sorted(allowed)}")
    # the cascade must never leave an always-applicable Part I/VI line blank
    for qk in ("q1", "q2", "q3", "q4", "q5", "q6", "q7", "q7a", "q8", "q15"):
        check(exp.get(qk) is not None,
              f"T6 cascade answers always-applicable {qk}",
              f"T6 cascade leaves always-applicable {qk} blank")

print("\n=== validate_8867_rebuild ===")
print(f"PASS: {len(PASSES)}")
for p in PASSES:
    print(f"  ok  {p}")
if FAILURES:
    print(f"FAIL: {len(FAILURES)}")
    for f in FAILURES:
        print(f"  BAD {f}")
    sys.exit(1)
print("ALL GREEN")
