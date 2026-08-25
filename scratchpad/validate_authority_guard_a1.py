# -*- coding: utf-8 -*-
"""PROOF harness for the A1 scope widening of the two-writers guard.

Run:  .venv/Scripts/python.exe scratchpad/validate_authority_guard_a1.py
      (no Django, no database, no test_postgres — safe to run at any time)

⭐ Every check PROVES the guard behaves differently from the version it replaces,
rather than asserting the new version is right. Campaign rule: a harness should show
the wrong answer differs; a fixture that cannot fail is not a test.
"""
from __future__ import annotations

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "specs", "management", "commands"))

import _authority_guard as G  # noqa: E402

PASS, FAIL = [], []


def check(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    print("  %s  %-58s %s" % ("PASS" if ok else "FAIL", name, detail))


print("=" * 78)
print("A1 PROOF HARNESS — the two-writers guard's SCOPE")
print("=" * 78)

# ---------------------------------------------------------------------------
print("\n1. COVERAGE — all three writer populations are actually read")
cov = G.coverage()
for p in cov["populations"]:
    check("population %r yields declarations" % p["name"], p["codes"] > 0,
          "%d modules, %d declaring, %d codes" % (p["modules"], p["declaring"], p["codes"]))
check("no reader reported a problem", not cov["problems"], str(cov["problems"] or "none"))

# ---------------------------------------------------------------------------
print("\n2. ⭐ THE POINT OF A1 — the widened scan sees rows the old one could not")
old_only, _, _ = G.scan(G.CMD_DIR)          # pre-A1 behaviour: specs/ alone
new_all = cov["decls"]
old_coll = {c for c, v in G.collisions(old_only).items() if v["differs"]}
new_coll = {c for c, v in G.collisions(new_all).items() if v["differs"]}
check("widened scan sees strictly more codes", len(new_all) > len(old_only),
      "%d -> %d" % (len(old_only), len(new_all)))
check("widened scan sees strictly more DISAGREEING collisions", len(new_coll) > len(old_coll),
      "%d -> %d  (the old guard saw %.0f%%)"
      % (len(old_coll), len(new_coll), 100.0 * len(old_coll) / max(len(new_coll), 1)))
check("every collision the old scan found is still found", old_coll <= new_coll,
      "no regression: %d retained" % len(old_coll))

# ---------------------------------------------------------------------------
print("\n3. ⚠⚠ THE SPECIFIC MISS — a cross-population row the old guard called clean")
#    IRC_704 was filed as "identical today" pre-A1. Its two specs/ writers DO agree;
#    the federal_data writer disagrees. Proven structurally, not by pinning to the code.
cross = sorted(
    c for c in new_coll
    if c not in old_coll
    and len({w.split("/")[0] for w in G.collisions(new_all)[c]["writers"]}) > 1
)
check("at least one DISAGREEING collision spans two populations", bool(cross),
      "%d such rows, e.g. %s" % (len(cross), ", ".join(cross[:3])))
benign_before = [
    c for c in cross
    if c in old_only and len(old_only[c]) > 1
    and not G.collisions(old_only)[c]["differs"]
]
check("at least one was filed BENIGN before A1 and is not", bool(benign_before),
      "%s — agreed within specs/, disagrees once federal_data is visible"
      % (", ".join(benign_before) or "none found"))

# ---------------------------------------------------------------------------
print("\n4. THE GUARD REFUSES — it does not merely report")
#    Temporarily drop one acknowledgement and confirm that exact row is refused.
victim = sorted(new_coll)[0]
saved = G.ACKNOWLEDGED.pop(victim)
try:
    r = G.guard(write=lambda m: None, raise_on_new=False)
    check("an unacknowledged collision is reported NEW", victim in r["new"], victim)
    fired = False
    try:
        G.guard(write=lambda m: None, raise_on_new=True)
    except Exception as exc:                                       # noqa: BLE001
        fired = victim in str(exc)
    check("raise_on_new=True actually RAISES naming it", fired, victim)
finally:
    G.ACKNOWLEDGED[victim] = saved
r = G.guard(write=lambda m: None, raise_on_new=False)
check("restored: zero NEW collisions across the whole library", not r["new"],
      "%d acknowledged" % len(r["acknowledged"]))

# ---------------------------------------------------------------------------
print("\n5. THE WRITER SET IS PART OF THE ACKNOWLEDGEMENT")
code, (writers, note) = next(iter(sorted(G.ACKNOWLEDGED.items())))
check("a module JOINING a known collision is refused as NEW",
      not G.is_acknowledged(code, list(writers) + ["specs/load_newcomer.py"]),
      "%s + a newcomer" % code)
check("the exact recorded set is accepted", G.is_acknowledged(code, list(writers)), code)

# ---------------------------------------------------------------------------
print("\n6. ⭐ IT CANNOT GO BLIND QUIETLY — the failure mode A1 exists to prevent")
real_dir = G.FEDERAL_DATA_DIR
G.FEDERAL_DATA_DIR = os.path.join(REPO, "no_such_directory")
try:
    blind = G.coverage()
    check("a missing population is detected", "federal_data" in blind["blind"],
          str(blind["blind"]))
    ok, fails = G.selftest_report()
    check("selftest FAILS when a population goes dark", not ok,
          "%d failure(s)" % len(fails))
    refused = False
    try:
        G.guard(write=lambda m: None, raise_on_new=True)
    except Exception as exc:                                       # noqa: BLE001
        refused = "unreadable" in str(exc)
    check("guard REFUSES rather than reporting clean", refused,
          "⭐ the pre-A1 guard would have passed here")
finally:
    G.FEDERAL_DATA_DIR = real_dir
ok, fails = G.selftest_report()
check("restored: selftest passes again", ok, str(fails or "no failures"))

# ---------------------------------------------------------------------------
print("\n7. HYGIENE — the guard no longer scans its own selftest fixtures")
check("no ZZ_ fixture appears as a real declaration",
      not any(c.startswith("ZZ_") for c in cov["decls"]),
      "pre-A1 this file declared ZZ_SYNTHETIC_CODE and ZZ_SOLE_WRITER")

# ---------------------------------------------------------------------------
print("\n8. NOT PINNED TO TODAY'S DATA")
check("selftest asserts no collision COUNT",
      "46" not in open(G.__file__, encoding="utf-8").read().split("def selftest_report")[1],
      "a count would go red the moment Ken resolves one — D-38's stated failure mode")

print("\n" + "=" * 78)
print("%d passed, %d failed" % (len(PASS), len(FAIL)))
if FAIL:
    for f in FAIL:
        print("  FAILED: %s" % f)
print("=" * 78)
sys.exit(1 if FAIL else 0)
