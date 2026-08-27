"""Pre-seed content checker for load_4562_recon_179_limitation (the D_4562_RECON
amendment for the §179 business-income limitation).

Run:  poetry run python check_4562_recon_integrity.py

Mirrors check_4562_section179_integrity.py: validates the authored lists WITHOUT
touching the DB, then INDEPENDENTLY recomputes every scenario's verdict from its
OWN transcription of the two-part reconciliation (NOT imported from the loader):

    non_179[dest]   = Σ (round(asset amount) − round(§179 elected on that asset))
    landed_179[dest] = destination_value[dest] − non_179[dest]
    (a) fire when landed_179[dest] < 0 for any destination
    (b) fire when Σ landed_179 over §179-participating destinations != line 12
    no §179 on the return (line 12 == 0 and line 10 == 0):
        fire when destination_value[dest] != Σ round(asset amount)

with the §179 side re-typed off the 2025 Form 4562 face
(resources/irs_forms/2025/f4562.pdf, pymupdf dump 2026-07-27):
    L11 "Business income limitation. Enter the smaller of business income (not
         less than zero) or line 5. See instructions"
    L12 "Section 179 expense deduction. Add lines 9 and 10, but don't enter more
         than line 11 ."
    L13 "Carryover of disallowed deduction to 2026. Add lines 9 and 10, less
         line 12"

This is the MATH GATE that must pass before the app leg. Loader & gate share no
logic. It also runs a NEGATIVE CONTROL: the pre-amendment unconditional-equality
condition is re-implemented here and asserted to MISFIRE on the limited-but-
correct scenario — proving the amendment changes a real verdict rather than
restating one (the s121 "a check that echoes the authored answer proves nothing"
lesson).
"""
# stdout forced to UTF-8 (2026-08-26, delvio-states S-10): this gate prints non-ASCII in its
# SUCCESS summary, so on a cp1252 console it raised UnicodeEncodeError and exited 1 AFTER
# passing every check -- a false red that an exit-code sweep cannot tell from a real one.
import sys as _sys
try:
    _sys.stdout.reconfigure(encoding="utf-8")
    _sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import os
import sys
from decimal import ROUND_HALF_UP, Decimal

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from specs.management.commands import load_4562_recon_179_limitation as m  # noqa: E402

errors: list[str] = []


def err(msg):
    errors.append(msg)


def D(x):
    return Decimal(str(x if x is not None else 0))


def whole(x):
    return D(x).quantize(Decimal("1"), rounding=ROUND_HALF_UP)


# ═══════════════════════════════════════════════════════════════════════════
# INDEPENDENT recomputation — the two-part reconciliation, re-typed
# ═══════════════════════════════════════════════════════════════════════════

def line_12(l9, l10, l11):
    """Face: 'Add lines 9 and 10, but don't enter more than line 11.'"""
    return min(D(l9) + D(l10), D(l11))


def line_13(l9, l10, l12):
    """Face: 'Add lines 9 and 10, less line 12.'"""
    return (D(l9) + D(l10)) - D(l12)


def reconcile(amounts, elected, destination_value, l9, l10, l12):
    """Return (fires, non_179_total, landed_179) under the AMENDED condition."""
    module_total = sum((whole(a) for a in amounts), Decimal("0"))
    non_179 = sum((whole(a) - whole(e) for a, e in zip(amounts, elected)),
                  Decimal("0"))
    landed = D(destination_value) - non_179

    s179_in_play = D(l12) != 0 or D(l10) != 0
    if not s179_in_play:
        return (D(destination_value) != module_total, non_179, landed)

    if landed < 0:                       # part (a)
        return (True, non_179, landed)
    pure_carryover = D(l9) == 0 and D(l10) > 0
    if pure_carryover:                   # part (b) skipped by design
        return (False, non_179, landed)
    return (landed != D(l12), non_179, landed)   # part (b)


def reconcile_pre_amendment(amounts, destination_value):
    """The ORIGINAL condition — unconditional per-destination equality."""
    module_total = sum((whole(a) for a in amounts), Decimal("0"))
    return D(destination_value) != module_total


# ═══════════════════════════════════════════════════════════════════════════
# Structural checks
# ═══════════════════════════════════════════════════════════════════════════

rule_ids = [r["rule_id"] for r in m.RULES]
if len(rule_ids) != len(set(rule_ids)):
    err("duplicate rule ids")
if "R020" not in rule_ids:
    err("RULES missing R020 (the reconciliation basis)")

diag_ids = [d["diagnostic_id"] for d in m.DIAGNOSTICS]
if len(diag_ids) != len(set(diag_ids)):
    err("duplicate diagnostic ids")
if "D_4562_RECON" not in diag_ids:
    err("DIAGNOSTICS must amend D_4562_RECON")

# DB column caps: diagnostic_id is varchar(40) since specs.0003; rule_id 20.
for did in diag_ids:
    if len(did) > 40:
        err(f"diagnostic_id too long (>40): {did}")
for rid in rule_ids:
    if len(rid) > 20:
        err(f"rule_id too long (>20): {rid}")

# every authored rule must be cited
linked = {rid for rid, *_ in m.RULE_LINKS}
uncited = [rid for rid in rule_ids if rid not in linked]
if uncited:
    err(f"uncited rules {uncited}")
dangling = [rid for rid in linked if rid not in rule_ids]
if dangling:
    err(f"rule_links reference rules not in this amendment {dangling}")

# The amendment must not silently change severity — this stays a blocking error.
for d in m.DIAGNOSTICS:
    if d["diagnostic_id"] == "D_4562_RECON" and d["severity"] != "error":
        err(f"D_4562_RECON severity changed to {d['severity']} — the approved fix "
            "was the two-part reconciliation, NOT a downgrade to warning")

# The amended condition must actually mention what changed.
recon = next(d for d in m.DIAGNOSTICS if d["diagnostic_id"] == "D_4562_RECON")
for token in ("line 12", "non-§179"):
    if token not in recon["condition"]:
        err(f"D_4562_RECON condition never mentions {token!r} — the amendment is "
            "not expressed in the condition the app implements from")

# Text-pin the face wording R020 leans on (a paraphrase here is the s113 class).
r020 = next(r for r in m.RULES if r["rule_id"] == "R020")
for token in ("Business income limitation",
              "Add lines 9 and 10, but don't enter more than line 11",
              "Carryover of disallowed deduction to 2026"):
    if token not in r020["description"]:
        err(f"R020 description missing the verbatim face text {token!r}")

scenario_names = [s["scenario_name"] for s in m.SCENARIOS]
if len(scenario_names) != len(set(scenario_names)):
    err("duplicate scenario names")


# ═══════════════════════════════════════════════════════════════════════════
# Recompute every scenario
# ═══════════════════════════════════════════════════════════════════════════

for sc in m.SCENARIOS:
    name = sc["scenario_name"]
    i = sc["inputs"]
    want = sc["expected_outputs"]

    # The §179 Part I arithmetic must itself be self-consistent.
    l12 = line_12(i["line_9"], i["line_10"], i["line_11"])
    if l12 != D(i["line_12"]):
        err(f"{name}: line 12 recomputes {l12}, authored {i['line_12']}")
    l13 = line_13(i["line_9"], i["line_10"], i["line_12"])
    if l13 != D(i["line_13"]):
        err(f"{name}: line 13 recomputes {l13}, authored {i['line_13']}")

    fires, non_179, landed = reconcile(
        i["asset_amounts"], i["section_179_elected"],
        i["destination_line_value"], i["line_9"], i["line_10"], i["line_12"],
    )
    if non_179 != D(want["non_179_total"]):
        err(f"{name}: non_179_total recomputes {non_179}, authored {want['non_179_total']}")
    if landed != D(want["landed_179"]):
        err(f"{name}: landed_179 recomputes {landed}, authored {want['landed_179']}")

    want_fires = "D_4562_RECON" in want["diagnostics"]
    if fires != want_fires:
        err(f"{name}: recomputed fires={fires}, authored diagnostics={want['diagnostics']}")


# ═══════════════════════════════════════════════════════════════════════════
# NEGATIVE CONTROL — the amendment must change a real verdict
# ═══════════════════════════════════════════════════════════════════════════

control = next(
    (s for s in m.SCENARIOS if "limited by business income" in s["scenario_name"]),
    None,
)
if control is None:
    err("no §179-limited scenario present — the false positive is unpinned")
else:
    i = control["inputs"]
    if not reconcile_pre_amendment(i["asset_amounts"], i["destination_line_value"]):
        err("NEGATIVE CONTROL FAILED: the pre-amendment condition does NOT fire on "
            "the §179-limited scenario, so this amendment fixes nothing — re-derive "
            "the scenario from the defect actually observed on production")
    fires, _, _ = reconcile(
        i["asset_amounts"], i["section_179_elected"], i["destination_line_value"],
        i["line_9"], i["line_10"], i["line_12"])
    if fires:
        err("NEGATIVE CONTROL FAILED: the amended condition still fires on the "
            "§179-limited scenario")

# A scenario must prove the guard SURVIVES with the limitation active.
survives = [
    s for s in m.SCENARIOS
    if "D_4562_RECON" in s["expected_outputs"]["diagnostics"]
    and D(s["inputs"]["line_13"]) > 0
]
if not survives:
    err("no scenario fires WHILE the limitation is active — nothing proves the "
        "guard still catches a real routing gap on a §179-limited return")

# And one must pin the unchanged no-§179 path.
if not any(D(s["inputs"]["line_12"]) == 0 and D(s["inputs"]["line_10"]) == 0
           for s in m.SCENARIOS):
    err("no scenario pins the no-§179 path (today's strict equality, unchanged)")


# ═══════════════════════════════════════════════════════════════════════════
# Report
# ═══════════════════════════════════════════════════════════════════════════

print("=" * 64)
if errors:
    print(f"FAIL — {len(errors)} issue(s):")
    for e in errors:
        print(f"  - {e}")
    print("=" * 64)
    sys.exit(1)
else:
    n = len(m.SCENARIOS)
    print(f"ALL CHECKS PASS — {n} reconciliation scenarios recomputed independently; "
          "structure + face-text pins + negative control green.")
    print("D_4562_RECON: (a) landed_179[dest] >= 0 ; (b) Σ landed_179 == line 12 ;")
    print("no §179 on the return -> strict per-destination equality, unchanged.")
    print("=" * 64)
