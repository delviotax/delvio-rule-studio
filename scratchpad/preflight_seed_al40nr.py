# -*- coding: utf-8 -*-
"""PRE-FLIGHT for the AL_FORM_40NR seed. READ-ONLY against PROD.

Ken opened the Gate-1 SEED gate directly. This runs BEFORE anything is flipped.

It hunts the four-member defect family against the LIVE database, not against files:
  1. TWO WRITERS OF ONE ROW - does any source_code / topic_code this loader DECLARES
     already exist in prod, owned by something else? update_or_create would silently
     rewrite it (the D-31 defect, which the VA/AZ pre-flight caught the hard way).
  2. DANGLING REFERENCE - does every EXISTING_SOURCES_TO_REFERENCE code resolve?
  3. It SNAPSHOTS every referenced row so the post-seed pass can PROVE they were
     not rewritten, rather than assert it.
  4. Confirms the three target forms are genuinely absent (a re-seed is a different
     operation from a first seed).

⚠ Writes nothing. Prints no secrets.
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
from django.db.models import Q  # noqa: E402
from sources.models import AuthoritySource, AuthorityTopic, RuleAuthorityLink  # noqa: E402
from specs.models import FlowAssertion, TaxForm  # noqa: E402
from specs.management.commands import load_al_40nr as AL  # noqa: E402

db = settings.DATABASES["default"]
print("=" * 78)
print("PRE-FLIGHT - READ ONLY")
print("  engine :", db["ENGINE"].rsplit(".", 1)[-1])
print("  db name:", db.get("NAME"))          # name only - never the credentials
print("  host   :", (db.get("HOST") or "")[:18] + "..." if db.get("HOST") else "(local)")
print("=" * 78)

if "sqlite" in db["ENGINE"]:
    print("\n!! REFUSING: this is NOT prod. DATABASE_URL did not resolve to Postgres.")
    sys.exit(2)

BATCH = [("AL_FORM_40NR", AL)]

print("\nPROD BASELINE")
print("  TaxForm rows            :", TaxForm.objects.count())
print("  AuthoritySource rows    :", AuthoritySource.objects.count())
print("  AuthorityTopic rows     :", AuthorityTopic.objects.count())
print("  FlowAssertion rows      :", FlowAssertion.objects.count())

problems = []

print("\n1. TARGET FORMS MUST BE ABSENT (a re-seed is a different operation)")
for code, _mod in BATCH:
    n = TaxForm.objects.filter(form_number=code).count()
    print(f"   {code:<12} present in prod: {n}")
    if n:
        problems.append(f"{code} ALREADY EXISTS in prod - this would be a RE-seed, not a seed")

print("\n2. TWO-WRITERS: does prod already hold a source_code this batch DECLARES?")
declared_by = {}
for code, mod in BATCH:
    for s in mod.AUTHORITY_SOURCES:
        declared_by.setdefault(s["source_code"], []).append(code)
for sc, owners in sorted(declared_by.items()):
    if len(owners) > 1:
        problems.append(f"{sc} is declared by MORE THAN ONE loader in this batch: {owners}")
    existing = AuthoritySource.objects.filter(source_code=sc).first()
    if existing:
        cites = RuleAuthorityLink.objects.filter(authority_source=existing).count()
        problems.append(
            f"⚠⚠ TWO WRITERS: {sc} ALREADY EXISTS in prod (rank={existing.source_rank!r}, "
            f"trust={existing.trust_score}, cited by {cites} live rule links) and would be "
            f"SILENTLY REWRITTEN by {owners}")
        print(f"   ⚠⚠ {sc:<28} EXISTS - {cites} live rule links")
    else:
        print(f"   ok {sc:<28} new")

print("\n2b. TWO-WRITERS on TOPICS (update_or_create rewrites topic_name too)")
for code, mod in BATCH:
    for tc, tname in mod.AUTHORITY_TOPICS:
        existing = AuthorityTopic.objects.filter(topic_code=tc).first()
        if existing and existing.topic_name != tname:
            problems.append(
                f"⚠⚠ TOPIC TWO-WRITERS: {tc} exists in prod with a DIFFERENT name and "
                f"{code} would rewrite it")
            print(f"   ⚠⚠ {tc:<28} EXISTS with a different name")
        elif existing:
            print(f"   ok {tc:<28} exists, identical name")
        else:
            print(f"   ok {tc:<28} new")

print("\n3. DANGLING REFERENCES: every EXISTING_SOURCES_TO_REFERENCE must resolve")
referenced = set()
for code, mod in BATCH:
    for sc in mod.EXISTING_SOURCES_TO_REFERENCE:
        referenced.add(sc)
        ok = AuthoritySource.objects.filter(source_code=sc).exists()
        print(f"   {'ok' if ok else '!!'} {code:<10} -> {sc:<28} {'resolves' if ok else 'MISSING'}")
        if not ok:
            problems.append(f"DANGLING REFERENCE: {code} references {sc}, absent from prod")

print("\n4. SNAPSHOT of every referenced row (to PROVE afterwards they were not rewritten)")
FIELDS = ("source_code", "source_type", "source_rank", "jurisdiction_code", "title", "citation",
          "issuer", "official_url", "current_status", "is_substantive_authority", "trust_score")
snap = {}
for sc in sorted(referenced):
    row = AuthoritySource.objects.filter(source_code=sc).first()
    if row:
        snap[sc] = {f: str(getattr(row, f)) for f in FIELDS}
out = os.path.join(PROJECT_ROOT, "scratchpad", "preflight_seed_al40nr_snapshot.json")
open(out, "w", encoding="utf-8").write(json.dumps(snap, indent=1, sort_keys=True))
print(f"   snapshotted {len(snap)} referenced source rows -> {os.path.basename(out)}")

print("\n5. SENTINELS (must all still be DOWN at pre-flight time)")
for code, mod in BATCH:
    print(f"   {code:<12} READY_TO_SEED = {mod.READY_TO_SEED}")
    if mod.READY_TO_SEED:
        problems.append(f"{code} sentinel is ALREADY UP before the pre-flight completed")

print("\n" + "=" * 78)
if problems:
    print("!! PRE-FLIGHT FOUND %d PROBLEM(S) - DO NOT SEED:" % len(problems))
    for p in problems:
        print("   -", p)
    sys.exit(1)
print("PRE-FLIGHT CLEAN - safe to flip the sentinels and seed.")
print("=" * 78)
