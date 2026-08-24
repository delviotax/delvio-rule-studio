# -*- coding: utf-8 -*-
"""POST-SEED verification for OR_20. PROVES rather than asserts."""
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

PROJECT_ROOT = r"D:\dev\delvio-rule-studio"
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

import django  # noqa: E402
django.setup()

from django.test import Client  # noqa: E402
from sources.models import AuthoritySource  # noqa: E402
from specs.models import (  # noqa: E402
    FlowAssertion, FormDiagnostic, FormFact, FormLine, FormRule, TaxForm, TestScenario,
)
from specs.management.commands import load_or_20 as OR  # noqa: E402

FAIL, OK = [], []


def check(c, ok, bad):
    (OK if c else FAIL).append(ok if c else bad)


BASELINE = 168
n = TaxForm.objects.count()
check(n == BASELINE + 1, f"prod moved {BASELINE} -> {n} forms (exactly +1)",
      f"prod is at {n}, expected {BASELINE + 1}")

form = TaxForm.objects.filter(form_number="OR_20").first()
check(form is not None, "OR_20 exists in prod", "OR_20 MISSING")
if form:
    for model, decl, label in ((FormFact, OR.F_FACTS, "facts"), (FormRule, OR.F_RULES, "rules"),
                               (FormLine, OR.F_LINES, "lines"),
                               (FormDiagnostic, OR.F_DIAGNOSTICS, "diagnostics"),
                               (TestScenario, OR.F_SCENARIOS, "scenarios")):
        c = model.objects.filter(tax_form=form).count()
        check(c == len(decl), f"{label}: {c} persisted == {len(decl)} declared",
              f"{label}: {c} persisted but {len(decl)} declared")
    fa = FlowAssertion.objects.filter(
        assertion_id__in=[a["assertion_id"] for a in OR.FLOW_ASSERTIONS]).count()
    check(fa == len(OR.FLOW_ASSERTIONS), f"{fa} flow assertions live", "flow assertion mismatch")

print("EXPORT")
client = Client(HTTP_HOST="localhost")
r = client.get("/api/forms/lookup/OR_20/export/")
body = json.loads(r.content.decode("utf-8")) if r.status_code == 200 else {}
sc = body.get("state_conformity") if isinstance(body, dict) else None
print(f"   OR_20  HTTP {r.status_code}  bytes {len(r.content)}  state_conformity: "
      f"{'present' if sc else 'MISSING'}")
check(r.status_code == 200, "OR_20 exports 200", f"export returned {r.status_code}")
check(bool(sc), "OR_20 export carries a non-null state_conformity block", "state_conformity MISSING")

print("\n⚠⚠ REFERENCED ROWS MUST NOT HAVE BEEN REWRITTEN (D-31)")
snap = json.load(open(os.path.join(PROJECT_ROOT, "scratchpad", "preflight_or20_snapshot.json"),
                      encoding="utf-8"))
diffs = 0
for code, before in sorted(snap.items()):
    row = AuthoritySource.objects.filter(source_code=code).first()
    if not row:
        FAIL.append(f"⚠⚠ {code} DISAPPEARED")
        continue
    for field, was in before.items():
        if str(getattr(row, field)) != was:
            diffs += 1
            FAIL.append(f"⚠⚠ TWO WRITERS: {code}.{field} changed")
leaves = len(snap) * len(next(iter(snap.values())))
print(f"   compared {len(snap)} rows x {len(next(iter(snap.values())))} fields = {leaves} leaves")
check(diffs == 0, f"⚠⚠ PROVED: {len(snap)} referenced rows unchanged across {leaves} leaves",
      f"⚠⚠ {diffs} referenced fields were REWRITTEN")

print("\n⚠ OREGON-SPECIFIC: OR_20_S must be UNTOUCHED (the D-29 lesson)")
s20 = json.load(open(os.path.join(PROJECT_ROOT, "scratchpad", "preflight_or20s_snapshot.json"),
                     encoding="utf-8"))
ors = TaxForm.objects.filter(form_number="OR_20_S").first()
now = {"facts": FormFact.objects.filter(tax_form=ors).count(),
       "rules": FormRule.objects.filter(tax_form=ors).count(),
       "lines": FormLine.objects.filter(tax_form=ors).count(),
       "diag": FormDiagnostic.objects.filter(tax_form=ors).count(),
       "tests": TestScenario.objects.filter(tax_form=ors).count(),
       "updated_at": str(ors.updated_at)} if ors else {}
print("   before:", s20)
print("   after :", now)
check(now == s20,
      "⚠⚠ PROVED: OR_20_S is byte-for-byte untouched - same row counts AND the same updated_at "
      "timestamp. D-29 recorded a seed in this lane being WRONGLY described as 're-pointing' it; "
      "this one is proved not to.",
      f"⚠⚠ OR_20_S CHANGED: {s20} -> {now}")

print("\n" + "=" * 74)
for o in OK:
    print(f"  PASS  {o}")
if FAIL:
    print("\n" + "!" * 74)
    for f in FAIL:
        print(f"  FAIL  {f}")
print("=" * 74)
print(f"POST-SEED: {len(OK)} pass / {len(FAIL)} fail   |   prod TaxForms = {TaxForm.objects.count()}")
print("=" * 74)
sys.exit(1 if FAIL else 0)
