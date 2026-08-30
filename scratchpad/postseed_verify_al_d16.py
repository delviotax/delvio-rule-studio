# -*- coding: utf-8 -*-
"""POST-SEED verification for the D-16 Alabama reseed + AL_FORM_40 amendment.

Compares prod against `preflight_seed_al_d16_snapshot.json` -- i.e. against
what was ACTUALLY there before, not against what I expect was there.

Three questions:
  1. Are the 11 D-16 defect occurrences GONE from prod?
  2. Is the corrected substance actually PRESENT (not merely the old text absent)?
  3. Did anything move that should NOT have -- counts, ids, other forms?

Read-only. Writes nothing.
"""
import io, json, os, re, sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from specs.models import (FormDiagnostic, FormFact, FormLine, FormRule,  # noqa: E402
                          TaxForm, TestScenario)

HERE = os.path.dirname(os.path.abspath(__file__))
BEFORE = json.load(io.open(os.path.join(HERE, "preflight_seed_al_d16_snapshot.json"), encoding="utf-8"))

fails, oks = [], 0


def check(cond, ok_msg, fail_msg):
    global oks
    if cond:
        oks += 1
        print("  PASS  %s" % ok_msg)
    else:
        fails.append(fail_msg)
        print("  FAIL  %s" % fail_msg)


def blob(fn):
    form = TaxForm.objects.get(form_number=fn)
    d = {
        "form_title": form.form_title, "notes": form.notes,
        "rules": {r.rule_id: {"title": r.title, "description": r.description, "formula": r.formula}
                  for r in FormRule.objects.filter(tax_form=form)},
        "diagnostics": {x.diagnostic_id: x.message for x in FormDiagnostic.objects.filter(tax_form=form)},
        "facts": {f.fact_key: f.label for f in FormFact.objects.filter(tax_form=form)},
        "lines": {ln.line_number: ln.description for ln in FormLine.objects.filter(tax_form=form)},
        "scenarios": sorted(TestScenario.objects.filter(tax_form=form).values_list("scenario_name", flat=True)),
    }
    return d, json.dumps(d, ensure_ascii=False)


print("=" * 72)
print("1. THE D-16 DEFECTS -- must be GONE")
print("=" * 72)
DEFECTS = ["Schedule EPT-C", "Sch EPT-C", "NON-electing S-corp",
           "non-electing S-corporation", "Due Mar 15"]
for fn in ("AL_FORM_65", "AL_FORM_20S"):
    d, txt = blob(fn)
    for probe in DEFECTS:
        # EPT-C may legitimately survive ONLY inside an explicit negation
        n = txt.count(probe)
        if probe in ("Schedule EPT-C", "Sch EPT-C"):
            # ⚠ v1 of this check used substring probes like "via Sch EPT-C —" and
            # counted the NEGATION "NOT via Sch EPT-C —" as a positive, accusing
            # three CORRECT prod rows. A probe that cannot see the word NOT in
            # front of it is not a check, it is a keyword match — the exact
            # failure already recorded for the fixture sweep. Now: every mention
            # must sit inside an explicit negation.
            unnegated = []
            for m in re.finditer(re.escape(probe), txt):
                if "NOT" not in txt[max(0, m.start() - 90):m.start()].upper():
                    unnegated.append(txt[max(0, m.start() - 60):m.start() + 40])
            check(not unnegated,
                  "%s: all %d %r mentions are explicit negations" % (fn, n, probe),
                  "%s: %d UNNEGATED %r mention(s): %s" % (fn, len(unnegated), probe, unnegated[:2]))
        else:
            check(n == 0, "%s: %r gone" % (fn, probe), "%s: %r still present x%d" % (fn, probe, n))

print()
print("=" * 72)
print("2. THE CORRECTED SUBSTANCE -- must be PRESENT")
print("=" * 72)
_, t65 = blob("AL_FORM_65")
_, t20 = blob("AL_FORM_20S")
check("Schedule CP-B" in t65, "AL_FORM_65: upper-tier path names Schedule CP-B", "AL_FORM_65: CP-B missing")
check("Form 40, page 1, line 26" in t65, "AL_FORM_65: individual path names Form 40 line 26", "AL_FORM_65: line 26 missing")
check("Mar 16, 2026" in t65, "AL_FORM_65: TY2025 due date is Mon Mar 16 2026", "AL_FORM_65: corrected date missing")
check("An EPT would fill out lines 32-37" in t20, "AL_FORM_20S: the 20S-instructions quote is carried",
      "AL_FORM_20S: AL-2 verbatim quote missing")
# ⚠ v1 looked for AL-3 in the FORM's own rows. It lives on the AuthoritySource
# EXCERPT (AL_ACT_2021_1) — a different table that blob() never reads — so the
# check reported the note "missing" while it was sitting in prod. An instrument
# is only ever right about the population it reads.
from sources.models import AuthorityExcerpt, AuthoritySource  # noqa: E402
_src = AuthoritySource.objects.filter(source_code="AL_ACT_2021_1").first()
_exc = " ".join(e.excerpt_text or "" for e in AuthorityExcerpt.objects.filter(authority_source=_src)) if _src else ""
check("SOURCE CONFLICT" in _exc and "EPT 2021.qxp" in _exc and "must be checked each" in _exc,
      "AL-3 source-conflict note is on the AL_ACT_2021_1 excerpt in prod",
      "AL-3 source-conflict note missing from the AL_ACT_2021_1 excerpt")

print()
print("=" * 72)
print("3. AL_FORM_40 -- the Schedule CP amendment")
print("=" * 72)
d40, t40 = blob("AL_FORM_40")
check("pte_credit_schedule_cp" in d40["facts"], "fact pte_credit_schedule_cp exists", "fact missing")
check("26" in d40["lines"], "line 26 exists", "line 26 missing")
check("Schedule CP" in d40["lines"].get("26", ""), "line 26 names Schedule CP", "line 26 description wrong")
pay = d40["rules"].get("R-AL-PAYMENTS", {})
check("pte_credit_schedule_cp" in pay.get("formula", ""), "L27 formula sums the Schedule CP term",
      "L27 formula does NOT sum it -- the unmapped-input defect")
check(any("Schedule CP credit turns owed into refund" in s for s in d40["scenarios"]),
      "the discriminating scenario is seeded", "discriminating scenario missing")

print()
print("=" * 72)
print("4. NOTHING ELSE MOVED")
print("=" * 72)
EXPECT = {"AL_FORM_65": {"facts": 9, "rules": 3, "lines": 3, "diagnostics": 3, "scenarios": 4},
          "AL_FORM_20S": {"facts": 12, "rules": 4, "lines": 3, "diagnostics": 4, "scenarios": 4},
          "AL_FORM_40": {"facts": 23, "rules": 9, "lines": 21, "diagnostics": 6, "scenarios": 6}}
for fn, exp in EXPECT.items():
    form = TaxForm.objects.get(form_number=fn)
    got = {"facts": FormFact.objects.filter(tax_form=form).count(),
           "rules": FormRule.objects.filter(tax_form=form).count(),
           "lines": FormLine.objects.filter(tax_form=form).count(),
           "diagnostics": FormDiagnostic.objects.filter(tax_form=form).count(),
           "scenarios": TestScenario.objects.filter(tax_form=form).count()}
    check(got == exp, "%s counts %s" % (fn, got), "%s counts %s != expected %s" % (fn, got, exp))
    b = BEFORE.get(fn) or {}
    if b.get("rules"):
        check(set(b["rules"]) == set(d40["rules"]) if fn == "AL_FORM_40" else True,
              "%s: rule id set unchanged" % fn, "%s: rule ids CHANGED" % fn) if fn == "AL_FORM_40" else None
        before_ids, after_ids = set(b["rules"]), set(FormRule.objects.filter(tax_form=form).values_list("rule_id", flat=True))
        check(before_ids == after_ids, "%s: rule ids unchanged (%d)" % (fn, len(after_ids)),
              "%s: rule ids moved: +%s -%s" % (fn, after_ids - before_ids, before_ids - after_ids))

# the only intended structural additions, stated explicitly
b40 = BEFORE["AL_FORM_40"]
added_facts = set(d40["facts"]) - set(b40["facts"])
added_lines = set(d40["lines"]) - set(b40["lines"])
check(added_facts == {"pte_credit_schedule_cp"}, "AL_FORM_40 added exactly one fact: %s" % added_facts,
      "AL_FORM_40 fact delta unexpected: %s" % added_facts)
check(added_lines == {"26"}, "AL_FORM_40 added exactly one line: %s" % added_lines,
      "AL_FORM_40 line delta unexpected: %s" % added_lines)

print()
print("=" * 72)
print("RESULT: %d pass / %d fail" % (oks, len(fails)))
for f in fails:
    print("   " + f)
print("=" * 72)
sys.exit(1 if fails else 0)
