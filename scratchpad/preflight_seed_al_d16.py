# -*- coding: utf-8 -*-
"""PRE-FLIGHT for the D-16 Alabama reseed + the AL_FORM_40 Schedule CP amendment.

Gate 1: Ken, direct, 2026-08-30 -- "approve the AL reseed and the AL_FORM_40 amendment".

Two jobs, both BEFORE anything is written to prod:

  1. CAP SCAN. Every value bound for a CharField is measured against that
     field's REAL max_length read off the model -- not against a remembered
     number. This is the D-17 class: nine field-length overflows that passed
     every local check and failed only on the live database, because SQLite
     does not enforce varchar caps and Postgres does.

  2. SNAPSHOT. The exact prod text of every row these two seeds will rewrite,
     so the post-seed verification compares against what was actually there
     rather than against what I expect was there.

Read-only. Writes nothing.
"""
import io, json, os, sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from django.apps import apps  # noqa: E402
from specs.models import (FormDiagnostic, FormFact, FormLine, FormRule,  # noqa: E402
                          TaxForm, TestScenario)
from specs.management.commands import load_al_form40 as F40  # noqa: E402
from specs.management.commands import load_al_passthrough as PT  # noqa: E402

FORMS = ["AL_FORM_65", "AL_FORM_20S", "AL_FORM_40"]


def cap(model, field):
    f = model._meta.get_field(field)
    return getattr(f, "max_length", None)


# ── 1. CAP SCAN ────────────────────────────────────────────────────────────
print("=" * 72)
print("1. CAP SCAN -- every CharField-bound value against the model's real max_length")
print("=" * 72)

CHECKS = [
    (FormFact, "fact_key"), (FormFact, "label"), (FormFact, "data_type"),
    (FormRule, "rule_id"), (FormRule, "title"), (FormRule, "rule_type"),
    (FormLine, "line_number"), (FormLine, "line_type"),
    (FormDiagnostic, "diagnostic_id"), (FormDiagnostic, "title"), (FormDiagnostic, "severity"),
    (TestScenario, "scenario_name"), (TestScenario, "scenario_type"),
    (TaxForm, "form_number"), (TaxForm, "form_title"), (TaxForm, "jurisdiction"),
]
KEYS = {FormFact: ("facts",), FormRule: ("rules",), FormLine: ("lines",),
        FormDiagnostic: ("diagnostics",), TestScenario: ("scenarios",)}

violations, measured = [], 0
for mod in (PT, F40):
    for spec in mod.FORMS:
        ident = spec["identity"]
        fn = ident.get("form_number")
        for model, field in CHECKS:
            lim = cap(model, field)
            if lim is None:
                continue
            if model is TaxForm:
                vals = [(field, ident.get(field))]
            else:
                bucket = KEYS[model][0]
                vals = [(field, row.get(field)) for row in spec.get(bucket, []) or []]
            for name, v in vals:
                if not isinstance(v, str):
                    continue
                measured += 1
                if len(v) > lim:
                    violations.append("%s %s.%s len %d > %d :: %r"
                                      % (fn, model.__name__, name, len(v), lim, v[:60]))

# authority sources / excerpts carry their own caps
from sources.models import AuthoritySource, AuthorityTopic  # noqa: E402
for mod in (PT, F40):
    for src in getattr(mod, "AUTHORITY_SOURCES", []) or []:
        for field in ("source_code", "source_type", "source_rank", "jurisdiction_code",
                      "title", "citation", "issuer", "current_status"):
            lim = cap(AuthoritySource, field)
            v = src.get(field)
            if lim and isinstance(v, str):
                measured += 1
                if len(v) > lim:
                    violations.append("AuthoritySource.%s len %d > %d :: %r" % (field, len(v), lim, v[:60]))
        for t in src.get("topics", []) or []:
            lim = cap(AuthorityTopic, "topic_code")
            if lim and len(t) > lim:
                violations.append("AuthorityTopic.topic_code len %d > %d :: %r" % (len(t), lim, t))

print("values measured : %d" % measured)
print("VIOLATIONS      : %d" % len(violations))
for v in violations:
    print("   " + v)
if violations:
    print("\nSTOP. Fix before seeding -- these fail on Postgres only.")
    sys.exit(1)
print("clean.\n")

# ── 2. SNAPSHOT ────────────────────────────────────────────────────────────
print("=" * 72)
print("2. SNAPSHOT of prod rows these seeds will rewrite")
print("=" * 72)

snap = {}
for fn in FORMS:
    form = TaxForm.objects.filter(form_number=fn).first()
    if not form:
        print("  %-14s NOT IN PROD" % fn)
        snap[fn] = None
        continue
    d = {
        "form_title": form.form_title,
        "notes": form.notes,
        "counts": {
            "facts": FormFact.objects.filter(tax_form=form).count(),
            "rules": FormRule.objects.filter(tax_form=form).count(),
            "lines": FormLine.objects.filter(tax_form=form).count(),
            "diagnostics": FormDiagnostic.objects.filter(tax_form=form).count(),
            "scenarios": TestScenario.objects.filter(tax_form=form).count(),
        },
        "rules": {r.rule_id: {"title": r.title, "description": r.description, "formula": r.formula}
                  for r in FormRule.objects.filter(tax_form=form)},
        "diagnostics": {x.diagnostic_id: x.message for x in FormDiagnostic.objects.filter(tax_form=form)},
        "lines": sorted(FormLine.objects.filter(tax_form=form).values_list("line_number", flat=True)),
        "facts": sorted(FormFact.objects.filter(tax_form=form).values_list("fact_key", flat=True)),
    }
    snap[fn] = d
    print("  %-14s facts %-4d rules %-4d lines %-4d diag %-4d scen %-4d"
          % (fn, d["counts"]["facts"], d["counts"]["rules"], d["counts"]["lines"],
             d["counts"]["diagnostics"], d["counts"]["scenarios"]))

# the specific defects being corrected -- prove they are IN prod right now
print("\n-- the four D-16 defects, as they stand in prod TODAY --")
hits = 0
for fn in ("AL_FORM_65", "AL_FORM_20S"):
    if not snap.get(fn):
        continue
    blob = json.dumps(snap[fn], ensure_ascii=False)
    for probe, why in (("Schedule EPT-C", "AL-1 owner credit on the wrong schedule"),
                       ("Sch EPT-C", "AL-1 short form"),
                       ("NON-electing S-corp", "AL-2 wrong scope"),
                       ("non-electing S-corporation", "AL-2 wrong scope"),
                       ("Due Mar 15", "AL-4 date")):
        n = blob.count(probe)
        if n:
            hits += n
            print("   %-14s %-28s x%d   (%s)" % (fn, probe, n, why))
print("   total defect occurrences visible in prod: %d" % hits)

print("\n-- AL_FORM_40: does prod already have line 26 / the Schedule CP fact? --")
if snap.get("AL_FORM_40"):
    print("   line 26 present : %s" % ("26" in snap["AL_FORM_40"]["lines"]))
    print("   fact present    : %s" % ("pte_credit_schedule_cp" in snap["AL_FORM_40"]["facts"]))

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preflight_seed_al_d16_snapshot.json")
io.open(OUT, "w", encoding="utf-8").write(json.dumps(snap, indent=1, ensure_ascii=False))
print("\nsnapshot written: %s" % OUT)
