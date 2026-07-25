"""Pre-seed math gate for load_1040_5695 (Residential Energy Credits §25D + §25C).

Run:  poetry run python check_5695_integrity.py

Independently recomputes every scenario from its OWN transcription of the §25D
30% + fuel-cell cap + carryforward and the §25C caps ($1,200 aggregate + the
sub-caps + the separate $2,000 heat-pump group) and cross-checks the loader's
helper functions + constants. The loader and this gate share NO math.
"""
import os
import sys
from decimal import Decimal

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from specs.management.commands import load_1040_5695 as m  # noqa: E402

errors: list[str] = []


def err(msg):
    errors.append(msg)


def D(x):
    return Decimal(str(x if x is not None else 0))


def check(name, got, want):
    if D(got) != D(want):
        err(f"{name}: recomputed {got} != authored {want}")


# ── Independent constants + math (re-typed) ──
RATE = 0.30
FCKW = 1000
DOOR1, DOORS, WIN, ITEM, AUDIT, AGG, HP = 250, 500, 600, 600, 150, 1200, 2000


def r0(x):
    return int(round(x))


def no(g):
    """v2 tri-state: only an explicit False denies."""
    return g is False


def ind_25d(se=0, sw=0, wind=0, geo=0, batt=0, fc_cost=0, fc_kw=0, cf=0, tax_limit=0,
            battery_ge_3kwh=None, fuel_cell_main_home=None):
    l6b = RATE * (se + sw + wind + geo + (0 if no(battery_ge_3kwh) else batt))
    fuel = 0 if no(fuel_cell_main_home) else min(RATE * fc_cost, FCKW * fc_kw)
    l13 = r0(l6b + fuel + cf)
    l15 = min(l13, r0(tax_limit))
    return (l15, l13 - l15)


def ind_25c(insul=0, doors_top=0, doors=0, win=0, ac=0, wh=0, furn=0, panel=0, audit=0, hp=0,
            tax_limit=0, section_a=None, section_b=None, enabling=None, audit_ok=None):
    a = not no(section_a)
    b = not no(section_b)
    # Section A — lines 18b, 19h, 20d.
    l18b = min(RATE * insul, AGG) if a else 0
    l19h = min(min(RATE * doors_top, DOOR1) + RATE * doors, DOORS) if a else 0
    l20d = min(RATE * win, WIN) if a else 0
    # Section B — lines 22d, 23d, 24d, 25e, 26c (and line 29 below).
    l22d = min(RATE * ac, ITEM) if b else 0
    l23d = min(RATE * wh, ITEM) if b else 0
    l24d = min(RATE * furn, ITEM) if b else 0
    l25e = min(RATE * panel, ITEM) if (b and not no(enabling)) else 0
    l26c = min(RATE * audit, AUDIT) if not no(audit_ok) else 0
    l28 = min(l18b + l19h + l20d + l22d + l23d + l24d + l25e + l26c, AGG)
    l29h = min(RATE * hp, HP) if b else 0
    return min(r0(l28 + l29h), r0(tax_limit))


# ── 1. Loader constants + helpers vs the independent transcription ──
check("RATE", m.RATE, RATE)
check("FUEL_CELL_PER_KW", m.FUEL_CELL_PER_KW, FCKW)
for name, a, b in (("DOOR_TOP_CAP", m.DOOR_TOP_CAP, DOOR1), ("DOORS_CAP", m.DOORS_CAP, DOORS),
                   ("WINDOWS_CAP", m.WINDOWS_CAP, WIN),
                   ("ITEM_CAP", m.ITEM_CAP, ITEM), ("AUDIT_CAP", m.AUDIT_CAP, AUDIT),
                   ("AGG_25C", m.AGG_25C, AGG), ("HEATPUMP_CAP", m.HEATPUMP_CAP, HP)):
    check(name, a, b)

for kw in [dict(se=20000, tax_limit=100000), dict(se=20000, tax_limit=4000),
           dict(fc_cost=10000, fc_kw=2.0, tax_limit=100000), dict(geo=5000, batt=3000, cf=500, tax_limit=100000),
           # v2 gates — an explicit No denies; None and True do not.
           dict(se=20000, batt=10000, battery_ge_3kwh=False, tax_limit=100000),
           dict(se=20000, batt=10000, battery_ge_3kwh=True, tax_limit=100000),
           dict(fc_cost=10000, fc_kw=2.0, fuel_cell_main_home=False, tax_limit=100000),
           dict(fc_cost=10000, fc_kw=2.0, fuel_cell_main_home=None, tax_limit=100000)]:
    g = m.credit_25d(kw.get("se", 0), kw.get("sw", 0), kw.get("wind", 0), kw.get("geo", 0),
                     kw.get("batt", 0), kw.get("fc_cost", 0), kw.get("fc_kw", 0), kw.get("cf", 0),
                     kw.get("tax_limit", 0),
                     battery_ge_3kwh=kw.get("battery_ge_3kwh"),
                     fuel_cell_main_home=kw.get("fuel_cell_main_home"))
    w = ind_25d(**kw)
    check(f"credit_25d({kw})[15]", g[0], w[0])
    check(f"credit_25d({kw})[16]", g[1], w[1])

for kw in [dict(win=3000, tax_limit=100000), dict(doors_top=2000, tax_limit=100000),
           dict(insul=5000, win=3000, tax_limit=100000), dict(hp=10000, tax_limit=100000),
           dict(insul=10000, hp=10000, tax_limit=100000), dict(ac=3000, audit=1000, tax_limit=100000),
           # v2 doors split — the per-door $250 before the $500 aggregate.
           dict(doors_top=1200, doors=1500, tax_limit=100000),
           dict(doors_top=700, doors=300, tax_limit=100000),
           dict(doors=2000, tax_limit=100000),
           # v2 gates — each denies exactly its own branch; line 29 rides on Section B.
           dict(insul=5000, win=3000, doors_top=1000, section_a=False, tax_limit=100000),
           dict(ac=4000, hp=10000, audit=500, section_b=False, tax_limit=100000),
           dict(panel=4000, enabling=False, tax_limit=100000),
           dict(panel=4000, enabling=False, section_b=False, tax_limit=100000),
           dict(audit=500, audit_ok=False, tax_limit=100000),
           dict(win=3000, section_a=None, tax_limit=100000),
           dict(win=3000, section_a=True, tax_limit=100000)]:
    g = m.credit_25c(kw.get("insul", 0), kw.get("doors_top", 0), kw.get("doors", 0), kw.get("win", 0),
                     kw.get("ac", 0), kw.get("wh", 0), kw.get("furn", 0), kw.get("panel", 0),
                     kw.get("audit", 0), kw.get("hp", 0), kw.get("tax_limit", 0),
                     section_a=kw.get("section_a"), section_b=kw.get("section_b"),
                     enabling=kw.get("enabling"), audit_ok=kw.get("audit_ok"))
    check(f"credit_25c({kw})", g, ind_25c(**kw))

# ── 2. Scenarios — independent recompute ──
DIAG_KEYS = {"D_5695_2026", "D_5695_25C_CAP", "D_5695_25C_LOST", "D_5695_25D_CFWD",
             "D_5695_FUEL_CELL", "D_5695_JOINT",
             "D_5695_QM_PIN", "D_5695_GATE_OPEN", "D_5695_GATE_NO", "D_5695_ADDRESS",
             "D_5695_CONSTRUCT", "D_5695_FRACTION"}
spec = m.FORMS[0]
for s in spec["scenarios"]:
    name = s["scenario_name"].split(" ")[0]
    inp, exp = s["inputs"], s["expected_outputs"]
    if exp.get("D_5695_2026"):
        # OBBBA: the credit is not computed at all for 2026+, so there is no number to recheck.
        if inp.get("tax_year", 2025) < 2026:
            err(f"{name}: D_5695_2026 expected but tax_year < 2026")
        continue
    # v2: a scenario may expect a diagnostic AND a number (E-G2..E-G8). The number is the
    # part that matters most — a gate that fails to skip line 29 shows up ONLY here.
    if inp.get("kind") == "25d":
        l15, l16 = ind_25d(se=inp.get("solar_electric", 0), sw=inp.get("solar_water", 0),
                           wind=inp.get("small_wind", 0), geo=inp.get("geothermal", 0),
                           batt=inp.get("battery", 0), fc_cost=inp.get("fuel_cell_cost", 0),
                           fc_kw=inp.get("fuel_cell_kw", 0), cf=inp.get("carryforward", 0),
                           tax_limit=inp.get("tax_limit", 0),
                           battery_ge_3kwh=inp.get("battery_ge_3kwh"),
                           fuel_cell_main_home=inp.get("fuel_cell_main_home"))
        got = {"e5695_line15": l15, "e5695_line16": l16}
    else:
        l32 = ind_25c(insul=inp.get("insulation", 0), doors_top=inp.get("doors_top", 0),
                      doors=inp.get("doors", 0),
                      win=inp.get("windows", 0), ac=inp.get("central_ac", 0),
                      wh=inp.get("water_heater", 0), furn=inp.get("furnace", 0),
                      panel=inp.get("panelboard", 0), audit=inp.get("home_audit", 0),
                      hp=inp.get("heat_pump_biomass", 0), tax_limit=inp.get("tax_limit", 0),
                      section_a=inp.get("section_a"), section_b=inp.get("section_b"),
                      enabling=inp.get("enabling"), audit_ok=inp.get("audit_ok"))
        got = {"e5695_line32": l32}
    for k, want in exp.items():
        if k in DIAG_KEYS:
            continue
        if k not in got:
            err(f"{name}.{k}: no independent recompute mapped")
            continue
        check(f"{name}.{k}", got[k], want)

# ── 3. Structural checks ──
known_sources = {s["source_code"] for s in m.AUTHORITY_SOURCES} | set(m.EXISTING_SOURCES_TO_REFERENCE)
for key, idk in (("facts", "fact_key"), ("rules", "rule_id"), ("lines", "line_number"),
                 ("diagnostics", "diagnostic_id"), ("scenarios", "scenario_name")):
    ids = [x[idk] for x in spec[key]]
    if len(ids) != len(set(ids)):
        err(f"FORM_5695.{key}: duplicate ids")
for r in spec["rules"]:
    if len(r["rule_id"]) > 20:
        err(f"rule_id too long ({len(r['rule_id'])} > 20): {r['rule_id']}")
for d in spec["diagnostics"]:
    if len(d["diagnostic_id"]) > 20:
        err(f"diagnostic_id too long ({len(d['diagnostic_id'])} > 20): {d['diagnostic_id']}")
rule_ids = {r["rule_id"] for r in spec["rules"]}
for rid in rule_ids - {rl[0] for rl in spec["rule_links"]}:
    err(f"rule {rid} has ZERO authority links")
for rid, src, _, _ in spec["rule_links"]:
    if rid not in rule_ids:
        err(f"rule_link references unknown rule {rid}")
    if src not in known_sources:
        err(f"rule_link references unknown source {src}")
diag_ids = {d["diagnostic_id"] for d in spec["diagnostics"]}
for sc in spec["scenarios"]:
    for k in sc["expected_outputs"]:
        if k.startswith("D_5695_") and k not in diag_ids:
            err(f"{sc['scenario_name']}: expects unknown diagnostic {k}")
fa_ids = [a["assertion_id"] for a in m.FLOW_ASSERTIONS]
if len(fa_ids) != len(set(fa_ids)):
    err("duplicate flow-assertion ids")

# ── Report ──
print("FORM_5695 (facts/rules/lines/diagnostics/scenarios/links):",
      (len(spec["facts"]), len(spec["rules"]), len(spec["lines"]),
       len(spec["diagnostics"]), len(spec["scenarios"]), len(spec["rule_links"])))
print(f"Flow assertions: {len(m.FLOW_ASSERTIONS)}; authority sources: {len(m.AUTHORITY_SOURCES)}")
print("Independently recomputed - T1 25D 6,000 / T2 windows 600 / T3 ONE door 250 (v2) / T4 agg 1,200 / "
      "T5 heat-pump 2,000 / T6 max 3,200 / T7 fuel-cell 2,000 / T8 tax-limited 4,000+2,000 cf / "
      "T9 doors 500 / T10 doors 300; v2 gates G2 SectionA-denied 0 / G3 SectionB-denied keeps only the "
      "150 audit (line 29 skipped) / G4 battery dropped / G5 audit 0 / G6 enabling 0 / G8 unanswered "
      "never denies; the §25D/§25C caps + the carryforward + the OBBBA termination cross-checked.")

if errors:
    print("\nFAILURES:")
    for e in errors:
        print(f"  X {e}")
    sys.exit(1)
print("\nALL CHECKS PASS")
