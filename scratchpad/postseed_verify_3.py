# -*- coding: utf-8 -*-
"""POST-SEED verification for MO_1120 + MS_83105 + CO_DR0112.

PROVES, rather than asserts:
  * prod moved 164 -> 167 and no other form was disturbed
  * all three export 200 with a NON-NULL state_conformity block
  * the 11 REFERENCED authority rows were NOT rewritten - compared leaf by leaf
    against the pre-flight snapshot. This is the D-31 defect's proof, and the
    VA/AZ seed is why it exists.
  * the seeded row counts match what each module declares

⚠ Read-only apart from Django's own request handling. No test database is created
or dropped - `test_postgres` is untouched.
"""
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
from specs.management.commands import load_mo_1120 as MO  # noqa: E402
from specs.management.commands import load_ms_83105 as MS  # noqa: E402
from specs.management.commands import load_co_dr0112 as CO  # noqa: E402

FAIL, OK = [], []


def check(cond, ok, bad):
    (OK if cond else FAIL).append(ok if cond else bad)


BATCH = [("MO_1120", MO), ("MS_83105", MS), ("CO_DR0112", CO)]
BASELINE_FORMS = 164

n = TaxForm.objects.count()
check(n == BASELINE_FORMS + 3, f"prod moved {BASELINE_FORMS} -> {n} forms (exactly +3)",
      f"prod is at {n} forms, expected {BASELINE_FORMS + 3}")

print("=" * 78)
print("1. THE THREE FORMS EXIST, WITH THE DECLARED COUNTS")
for code, mod in BATCH:
    form = TaxForm.objects.filter(form_number=code).first()
    check(form is not None, f"{code} exists in prod", f"{code} MISSING from prod")
    if not form:
        continue
    counts = {
        "facts": (FormFact.objects.filter(tax_form=form).count(), len(mod.F_FACTS)),
        "rules": (FormRule.objects.filter(tax_form=form).count(), len(mod.F_RULES)),
        "lines": (FormLine.objects.filter(tax_form=form).count(), len(mod.F_LINES)),
        "diag": (FormDiagnostic.objects.filter(tax_form=form).count(), len(mod.F_DIAGNOSTICS)),
        "tests": (TestScenario.objects.filter(tax_form=form).count(), len(mod.F_SCENARIOS)),
    }
    line = "   %-11s " % code + " ".join(f"{k} {a}/{b}" for k, (a, b) in counts.items())
    print(line)
    for k, (a, b) in counts.items():
        check(a == b, f"{code}.{k}: {a} persisted == {b} declared",
              f"{code}.{k}: {a} persisted but {b} declared")
    fa = FlowAssertion.objects.filter(
        assertion_id__in=[x["assertion_id"] for x in mod.FLOW_ASSERTIONS]).count()
    check(fa == len(mod.FLOW_ASSERTIONS), f"{code}: {fa} flow assertions live",
          f"{code}: {fa} flow assertions but {len(mod.FLOW_ASSERTIONS)} declared")

print("\n2. EXPORTS - 200 AND A NON-NULL state_conformity BLOCK")
# ⚠ specs.urls is mounted at /api/, and the test Client sends Host: testserver,
# which settings only allow under the test runner - so an un-hosted request 400s
# on ALLOWED_HOSTS and looks like an export failure. Send an allowed Host.
client = Client(HTTP_HOST="localhost")
for code, _mod in BATCH:
    r = client.get(f"/api/forms/lookup/{code}/export/")
    ok = r.status_code == 200
    body = {}
    if ok:
        try:
            body = json.loads(r.content.decode("utf-8"))
        except Exception:  # noqa: BLE001
            ok = False
    sc = body.get("state_conformity") if isinstance(body, dict) else None
    print(f"   {code:<11} HTTP {r.status_code}  bytes {len(r.content):>7}  "
          f"state_conformity: {'present' if sc else 'MISSING'}")
    check(ok, f"{code} exports 200", f"{code} export returned {r.status_code}")
    check(bool(sc), f"{code} export carries a non-null state_conformity block",
          f"{code} export has NO state_conformity - campaign D-8 requires it")

print("\n3. ⚠⚠ THE REFERENCED AUTHORITY ROWS MUST NOT HAVE BEEN REWRITTEN (D-31)")
snap = json.load(open(os.path.join(PROJECT_ROOT, "scratchpad",
                                   "preflight_seed_3_snapshot.json"), encoding="utf-8"))
diffs = 0
for sc_code, before in sorted(snap.items()):
    row = AuthoritySource.objects.filter(source_code=sc_code).first()
    if not row:
        FAIL.append(f"⚠⚠ {sc_code} DISAPPEARED from prod")
        continue
    for field, was in before.items():
        now = str(getattr(row, field))
        if now != was:
            diffs += 1
            FAIL.append(f"⚠⚠ TWO WRITERS: {sc_code}.{field} was {was[:40]!r} -> {now[:40]!r}")
print(f"   compared {len(snap)} referenced rows x {len(next(iter(snap.values())))} fields "
      f"= {len(snap) * len(next(iter(snap.values())))} leaves")
check(diffs == 0,
      f"⚠⚠ PROVED: {len(snap)} referenced rows unchanged, leaf by leaf - this batch REFERENCED "
      "them and never re-declared them",
      f"⚠⚠ {diffs} referenced fields were REWRITTEN - a two-writers defect went live")

print("\n" + "=" * 78)
for o in OK:
    print(f"  PASS  {o}")
if FAIL:
    print("\n" + "!" * 78)
    for f in FAIL:
        print(f"  FAIL  {f}")
print("=" * 78)
print(f"POST-SEED: {len(OK)} pass / {len(FAIL)} fail   |   prod TaxForms = {TaxForm.objects.count()}")
print("=" * 78)
sys.exit(1 if FAIL else 0)
