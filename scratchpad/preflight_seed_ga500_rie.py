# -*- coding: utf-8 -*-
"""PRE-FLIGHT for the GA-500 RIE worksheet line-10 amendment.

Gate 1: Ken, direct to the states session, 2026-08-30 --
"approve the GA RIE amendment, statute primary".

Same two jobs as the AL pre-flight, and for the same reasons:
  1. CAP SCAN -- every CharField-bound value against the model's REAL
     max_length. The D-17 class fails on Postgres only; SQLite does not
     enforce varchar caps, so every local check passes.
  2. SNAPSHOT -- what prod actually holds, so the post-seed check compares
     against reality rather than against expectation.

GA-500 is the biggest spec in the library, so the "nothing else moved" half
matters more here than it did for Alabama.

Read-only. Writes nothing.
"""
import io, json, os, sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from specs.models import (FormDiagnostic, FormFact, FormLine, FormRule,  # noqa: E402
                          TaxForm, TestScenario)
from sources.models import AuthoritySource, AuthorityTopic  # noqa: E402
from specs.management.commands import load_ga500_form_500 as GA  # noqa: E402

FORMS = ["500"]


def cap(model, field):
    return getattr(model._meta.get_field(field), "max_length", None)


print("=" * 72)
print("1. CAP SCAN")
print("=" * 72)
CHECKS = [
    (FormFact, "fact_key", "facts"), (FormFact, "label", "facts"), (FormFact, "data_type", "facts"),
    (FormFact, "default_value", "facts"),
    (FormRule, "rule_id", "rules"), (FormRule, "title", "rules"), (FormRule, "rule_type", "rules"),
    (FormLine, "line_number", "lines"), (FormLine, "line_type", "lines"),
    (FormDiagnostic, "diagnostic_id", "diagnostics"), (FormDiagnostic, "title", "diagnostics"),
    (FormDiagnostic, "severity", "diagnostics"),
    (TestScenario, "scenario_name", "scenarios"), (TestScenario, "scenario_type", "scenarios"),
]
violations, measured = [], 0
for spec in GA.FORMS:
    fn = spec["identity"].get("form_number")
    for field in ("form_number", "form_title", "jurisdiction"):
        lim = cap(TaxForm, field)
        v = spec["identity"].get(field)
        if lim and isinstance(v, str):
            measured += 1
            if len(v) > lim:
                violations.append("%s TaxForm.%s len %d > %d" % (fn, field, len(v), lim))
    for model, field, bucket in CHECKS:
        lim = cap(model, field)
        if lim is None:
            continue
        for row in spec.get(bucket, []) or []:
            v = row.get(field)
            if isinstance(v, str):
                measured += 1
                if len(v) > lim:
                    violations.append("%s %s.%s len %d > %d :: %r"
                                      % (fn, model.__name__, field, len(v), lim, v[:60]))

for src in getattr(GA, "AUTHORITY_SOURCES", []) or []:
    for field in ("source_code", "source_type", "source_rank", "jurisdiction_code",
                  "title", "citation", "issuer", "current_status"):
        lim = cap(AuthoritySource, field)
        v = src.get(field)
        if lim and isinstance(v, str):
            measured += 1
            if len(v) > lim:
                violations.append("AuthoritySource.%s len %d > %d :: %r" % (field, len(v), lim, v[:70]))
    for t in src.get("topics", []) or []:
        lim = cap(AuthorityTopic, "topic_code")
        if lim and len(t) > lim:
            violations.append("AuthorityTopic.topic_code len %d > %d :: %r" % (len(t), lim, t))

print("values measured : %d" % measured)
print("VIOLATIONS      : %d" % len(violations))
for v in violations:
    print("   " + v)
if violations:
    print("\nSTOP. These fail on Postgres only.")
    sys.exit(1)
print("clean.\n")

print("=" * 72)
print("2. SNAPSHOT")
print("=" * 72)
snap = {}
for fn in FORMS:
    form = TaxForm.objects.filter(form_number=fn).first()
    if not form:
        print("  %-8s NOT IN PROD" % fn)
        snap[fn] = None
        continue
    d = {
        "form_title": form.form_title, "notes": form.notes,
        "counts": {
            "facts": FormFact.objects.filter(tax_form=form).count(),
            "rules": FormRule.objects.filter(tax_form=form).count(),
            "lines": FormLine.objects.filter(tax_form=form).count(),
            "diagnostics": FormDiagnostic.objects.filter(tax_form=form).count(),
            "scenarios": TestScenario.objects.filter(tax_form=form).count(),
        },
        "rule_ids": sorted(FormRule.objects.filter(tax_form=form).values_list("rule_id", flat=True)),
        "fact_keys": sorted(FormFact.objects.filter(tax_form=form).values_list("fact_key", flat=True)),
        "line_numbers": sorted(FormLine.objects.filter(tax_form=form).values_list("line_number", flat=True)),
        "diag_ids": sorted(FormDiagnostic.objects.filter(tax_form=form).values_list("diagnostic_id", flat=True)),
        "scenario_names": sorted(TestScenario.objects.filter(tax_form=form).values_list("scenario_name", flat=True)),
        "rie_rule": {},
        "rie_facts": {},
    }
    r = FormRule.objects.filter(tax_form=form, rule_id="R-GA500-RIE").first()
    if r:
        d["rie_rule"] = {"title": r.title, "formula": r.formula, "description": r.description}
    for k in ("g_tp_rie_other_income", "g_sp_rie_other_income"):
        f = FormFact.objects.filter(tax_form=form, fact_key=k).first()
        if f:
            d["rie_facts"][k] = {"label": f.label, "notes": f.notes}
    snap[fn] = d
    c = d["counts"]
    print("  %-8s facts %-4d rules %-4d lines %-4d diag %-4d scen %-4d"
          % (fn, c["facts"], c["rules"], c["lines"], c["diagnostics"], c["scenarios"]))

print("\n-- RIE worksheet line 10 in prod, BEFORE (proving the gap is real) --")
blob = json.dumps(snap.get("500") or {}, ensure_ascii=False)
for probe in ("48-7-27(a)(5)(E)(i)", "EJUSDEM GENERIS", "WORKSHEET LINE 10",
              "RIE worksheet line 10 (unearned).", "unemployment", "§111"):
    print("   %-36s x%d" % (probe, blob.count(probe)))

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preflight_seed_ga500_rie_snapshot.json")
io.open(OUT, "w", encoding="utf-8").write(json.dumps(snap, indent=1, ensure_ascii=False))
print("\nsnapshot written: %s" % OUT)
