# -*- coding: utf-8 -*-
"""PRE-FLIGHT for the OR_20 seed. READ-ONLY against PROD.

⚠ The first attempt at this file was a sed-adaptation whose patch aborted before
writing, so it ran the PREVIOUS batch (MO/MS/CO) against prod. It REFUSED, loudly
and correctly - "already exists", "two writers", "sentinel already up". That is the
guard working: a pre-flight pointed at the wrong forms must fail closed, not
quietly pass. Rewritten from scratch rather than patched again.

Hunts the four-member defect family against the LIVE database:
  1. TWO WRITERS OF ONE ROW - would update_or_create silently rewrite a row
     another loader owns?
  2. DANGLING REFERENCE - does every referenced code resolve?
  3. Snapshots referenced rows so the post-seed pass can PROVE non-rewriting.
  4. ⚠ OREGON-SPECIFIC: snapshots OR_20_S, which campaign D-29 once wrongly
     claimed a seed would "re-point". Proved, not asserted.

⚠ Writes nothing to prod. Prints no secrets.
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

from django.conf import settings  # noqa: E402
from sources.models import AuthoritySource, AuthorityTopic, RuleAuthorityLink  # noqa: E402
from specs.models import (  # noqa: E402
    FlowAssertion, FormDiagnostic, FormFact, FormLine, FormRule, TaxForm, TestScenario,
)
from specs.management.commands import load_or_20 as OR  # noqa: E402

db = settings.DATABASES["default"]
print("=" * 78)
print("PRE-FLIGHT  OR_20  - READ ONLY")
print("  engine :", db["ENGINE"].rsplit(".", 1)[-1], "| db:", db.get("NAME"))
print("=" * 78)
if "sqlite" in db["ENGINE"]:
    print("\n!! REFUSING: this is NOT prod.")
    sys.exit(2)

problems = []
print("\nPROD BASELINE")
print("  TaxForm rows         :", TaxForm.objects.count())
print("  AuthoritySource rows :", AuthoritySource.objects.count())

print("\n1. TARGET FORM MUST BE ABSENT")
n = TaxForm.objects.filter(form_number="OR_20").count()
print("   OR_20 present in prod:", n)
if n:
    problems.append("OR_20 ALREADY EXISTS - this would be a RE-seed")

print("\n2. TWO-WRITERS: does prod already hold a source_code OR_20 DECLARES?")
for s in OR.AUTHORITY_SOURCES:
    sc = s["source_code"]
    existing = AuthoritySource.objects.filter(source_code=sc).first()
    if existing:
        cites = RuleAuthorityLink.objects.filter(authority_source=existing).count()
        problems.append(f"⚠⚠ TWO WRITERS: {sc} ALREADY EXISTS (rank={existing.source_rank!r}, "
                        f"trust={existing.trust_score}, {cites} live rule links)")
        print(f"   ⚠⚠ {sc:<30} EXISTS - {cites} live rule links")
    else:
        print(f"   ok {sc:<30} new")

print("\n2b. TWO-WRITERS on TOPICS")
for tc, tname in OR.AUTHORITY_TOPICS:
    ex = AuthorityTopic.objects.filter(topic_code=tc).first()
    if ex and ex.topic_name != tname:
        problems.append(f"⚠⚠ TOPIC TWO-WRITERS: {tc} exists with a DIFFERENT name")
        print(f"   ⚠⚠ {tc:<30} EXISTS with a different name")
    else:
        print(f"   {'ok' if not ex else 'ok'} {tc:<30} {'exists, identical' if ex else 'new'}")

print("\n3. DANGLING REFERENCES")
FIELDS = ("source_code", "source_type", "source_rank", "jurisdiction_code", "title", "citation",
          "issuer", "official_url", "current_status", "is_substantive_authority", "trust_score")
snap = {}
for sc in OR.EXISTING_SOURCES_TO_REFERENCE:
    row = AuthoritySource.objects.filter(source_code=sc).first()
    print(f"   {'ok' if row else '!!'} {sc:<30} {'resolves' if row else 'MISSING'}")
    if row:
        snap[sc] = {f: str(getattr(row, f)) for f in FIELDS}
    else:
        problems.append(f"DANGLING REFERENCE: {sc} absent from prod")
open(os.path.join(PROJECT_ROOT, "scratchpad", "preflight_or20_snapshot.json"),
     "w", encoding="utf-8").write(json.dumps(snap, indent=1, sort_keys=True))
print(f"   snapshotted {len(snap)} referenced rows")

print("\n4. ⚠ OREGON-SPECIFIC: OR_20_S non-disturbance baseline (the D-29 lesson)")
ors = TaxForm.objects.filter(form_number="OR_20_S").first()
if ors:
    s20 = {"facts": FormFact.objects.filter(tax_form=ors).count(),
           "rules": FormRule.objects.filter(tax_form=ors).count(),
           "lines": FormLine.objects.filter(tax_form=ors).count(),
           "diag": FormDiagnostic.objects.filter(tax_form=ors).count(),
           "tests": TestScenario.objects.filter(tax_form=ors).count(),
           "updated_at": str(ors.updated_at)}
    open(os.path.join(PROJECT_ROOT, "scratchpad", "preflight_or20s_snapshot.json"),
         "w", encoding="utf-8").write(json.dumps(s20, indent=1, sort_keys=True))
    print("   OR_20_S:", s20)
else:
    problems.append("OR_20_S is ABSENT from prod - the Oregon lane is not as expected")

print("\n5. SENTINEL")
print("   OR_20 READY_TO_SEED =", OR.READY_TO_SEED)
if OR.READY_TO_SEED:
    problems.append("OR_20 sentinel is ALREADY UP before the pre-flight completed")

print("\n" + "=" * 78)
if problems:
    print("!! PRE-FLIGHT FOUND %d PROBLEM(S) - DO NOT SEED:" % len(problems))
    for p in problems:
        print("   -", p)
    sys.exit(1)
print("PRE-FLIGHT CLEAN - safe to flip the sentinel and seed.")
print("=" * 78)
