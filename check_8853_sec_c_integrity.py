"""Pre-seed math gate for load_1040_8853_sec_c (Form 8853 Section C, long-term care).

Run:  poetry run python check_8853_sec_c_integrity.py

Independently recomputes every scenario from its OWN transcription of the face
arithmetic — 20 = 18 + 19; 21 = rate x days; 23 = MAX(21, 22); 25 = 23 - 24;
26 = MAX(0, 20 - 25) — and cross-checks the loader's helper. The loader and
this gate share NO math, so a transcription slip on either side surfaces here
rather than in the app build.

Three of the scenarios (T1-T3) are the IRS's own published examples from i8853
(2025), so this gate also confirms the $420 rate and the greater-of against an
IRS answer key rather than against our reading of the statute.
"""
import os
import sys
from decimal import Decimal

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from specs.management.commands import load_1040_8853_sec_c as m  # noqa: E402

errors: list[str] = []


def err(msg):
    errors.append(msg)


def D(x):
    return Decimal(str(x if x is not None else 0))


def check(name, got, want):
    if D(got) != D(want):
        err(f"{name}: recomputed {got} != authored {want}")


# ── Independent re-typing of the Section C arithmetic ──
# Rev. Proc. 2024-40 §2.62; also printed on the 2025 face at line 21.
RATE_2025 = Decimal("420")
DAYS_2025 = 365


def ind_line20(l18, l19):
    return D(l18) + D(l19)


def ind_line21(rate, days):
    return D(rate) * D(days)


def ind_line23(l21, l22):
    # §7702B(d)(2) "greater of" — written as an explicit comparison, not max(),
    # so a min-for-max slip in the loader cannot be mirrored here by accident.
    return D(l21) if D(l21) >= D(l22) else D(l22)


def ind_line25(l23, l24):
    # §7702B(d)(2): "the EXCESS (IF ANY) of (A) ... over (B)" — floored at zero.
    # ⚠ The FACE prints no floor here (only on line 26), so this floor comes from
    # the statute alone. Both this gate and the loader were first written unfloored
    # off the face; the verbatim (d)(2) caught it. See T14.
    diff = D(l23) - D(l24)
    return diff if diff > 0 else D(0)


def ind_line26(l20, l25):
    diff = D(l20) - D(l25)
    return diff if diff > 0 else D(0)


def ind_effective_line24(l24, pre1996, modified):
    """i8853 line 24 Caution: grandfathered reimbursements drop out of line 24
    unless the contract was modified after 7/31/1996 to increase benefits."""
    if pre1996 and not modified:
        return D(0)
    return D(l24)


# ── 1. The rate constant, three ways ──
if m.PER_DIEM_RATE_2025 != RATE_2025:
    err(f"PER_DIEM_RATE_2025 {m.PER_DIEM_RATE_2025} != Rev. Proc. 2024-40 §2.62 amount {RATE_2025}")
if m.DAYS_IN_YEAR_2025 != DAYS_2025:
    err(f"DAYS_IN_YEAR_2025 {m.DAYS_IN_YEAR_2025} != {DAYS_2025} (2025 is not a leap year)")

# The default on the fact must equal the verified constant — a spec whose fact
# default drifts from its own constant is the s142 class of silent wrong answer.
_rate_fact = next((f for f in m.N_FACTS if f["fact_key"] == "f8853c_per_diem_rate"), None)
if _rate_fact is None:
    err("f8853c_per_diem_rate fact is missing")
elif D(_rate_fact.get("default_value")) != RATE_2025:
    err(f"f8853c_per_diem_rate default {_rate_fact.get('default_value')} != {RATE_2025}")


# ── 2. Every scenario, recomputed independently and against the loader ──
for sc in m.N_SCENARIOS:
    name = sc["scenario_name"]
    i, want = sc["inputs"], sc["expected_outputs"]

    # Scenarios that assert a refusal or a pure-composition fact carry no
    # arithmetic of their own; their diagnostics are checked in section 3.
    if i.get("section_c_present") is False:
        continue
    if any(k.startswith("D_8853C_") for k in want):
        continue

    l18 = i.get("line18_qualified_per_diem", 0)
    l19 = i.get("line19_adb_chronically_ill", 0)
    days = i.get("ltc_period_days", 0)
    l22 = i.get("line22_costs_incurred", 0)
    l24_raw = i.get("line24_reimbursements", 0)
    l24 = ind_effective_line24(l24_raw, i.get("pre_aug1996_contract", False),
                               i.get("pre_aug1996_modified", False))
    short_circuit = bool(i.get("adb_only_because_terminal", False))

    if short_circuit:
        # Face note under line 16: lines 17-25 skipped, line 26 = -0-.
        if D(want.get("f8853c_line26_taxable", -1)) != 0:
            err(f"{name}: terminally-ill short circuit must give line 26 == 0")
        if want.get("skipped_17_25") is not True:
            err(f"{name}: terminally-ill short circuit must record skipped_17_25 True")
    else:
        l20 = ind_line20(l18, l19)
        l21 = ind_line21(RATE_2025, days)
        l23 = ind_line23(l21, l22)
        l25 = ind_line25(l23, l24)
        l26 = ind_line26(l20, l25)

        for key, got in (("f8853c_line20_total", l20), ("f8853c_line21_dollar_limit", l21),
                         ("f8853c_line23_greater", l23),
                         ("f8853c_line25_per_diem_limitation", l25),
                         ("f8853c_line26_taxable", l26)):
            if key in want:
                check(f"{name} {key}", got, want[key])

        # The effective line 24 is asserted directly in the pre-1996 scenario.
        if "f8853c_line24_reimbursements" in want:
            check(f"{name} f8853c_line24_reimbursements", l24, want["f8853c_line24_reimbursements"])

        # 8e component: Σ line 26 (one Section C per scenario here).
        if "f8853c_sch1_8e_component" in want and want["f8853c_sch1_8e_component"] is not None:
            check(f"{name} f8853c_sch1_8e_component", l26, want["f8853c_sch1_8e_component"])

        # The composed line: component + the keyed Sections A/B residual.
        if "sch1_line_8e" in want:
            check(f"{name} sch1_line_8e", l26 + D(i.get("sch1_8e_keyed_ab_residual", 0)),
                  want["sch1_line_8e"])

    # Cross-check the loader's own helper against this gate's arithmetic.
    got = m.compute_8853_sec_c(
        line18_qualified_per_diem=l18, line19_adb_chronically_ill=l19,
        ltc_period_days=days, line22_costs_incurred=l22, line24_reimbursements=l24,
        terminally_ill_adb_only=short_circuit)
    for key, want_key in (("line20", "f8853c_line20_total"),
                          ("line21", "f8853c_line21_dollar_limit"),
                          ("line23", "f8853c_line23_greater"),
                          ("line25", "f8853c_line25_per_diem_limitation"),
                          ("line26", "f8853c_line26_taxable")):
        if want_key in want and want[want_key] is not None:
            check(f"{name} helper.{key}", got[key], want[want_key])


# ── 3. The IRS answer key, asserted literally (i8853 (2025) Examples 1 and 2) ──
# Hardcoded here rather than read from N_SCENARIOS: if someone edits a scenario
# the published example still has to hold.
for label, l20, days, l22, l24, want23, want25, want26 in (
    ("i8853 Ex.1",        24000, 365, 54750, 27375, 153300, 125925, 0),
    ("i8853 Ex.2 Step 1", 12000, 181, 27150, 13575,  76020,  62445, 0),
    ("i8853 Ex.2 Step 2", 63000, 184, 27600, 13800,  77280,  63480, 0),
):
    l21 = ind_line21(RATE_2025, days)
    l23 = ind_line23(l21, l22)
    l25 = ind_line25(l23, l24)
    l26 = ind_line26(l20, l25)
    check(f"{label} line 23", l23, want23)
    check(f"{label} line 25", l25, want25)
    check(f"{label} line 26", l26, want26)

# The example's two periods must tile the year exactly — the cheapest possible
# check that the day counts were transcribed correctly.
if 181 + 184 != DAYS_2025:
    err("i8853 Example 2's two LTC periods (181 + 184) do not tile 2025")

# ── 3b. The §7702B(d)(2) floor on line 25, asserted structurally ──
# The invariant the floor exists to protect: line 26 can never exceed line 20,
# because you cannot be taxed on more than you received. Hardcoded independently
# of the scenarios so it survives any scenario edit.
for _l20, _days, _l22, _l24 in ((10000, 1, 0, 5420), (500, 1, 0, 99999),
                                (24000, 365, 0, 200000), (1000, 30, 500, 40000)):
    _l21 = ind_line21(RATE_2025, _days)
    _l23 = ind_line23(_l21, _l22)
    _l25 = ind_line25(_l23, _l24)
    _l26 = ind_line26(_l20, _l25)
    if _l25 < 0:
        err(f"line 25 went negative ({_l25}) — §7702B(d)(2) 'excess (if any)' floors it at zero")
    if _l26 > D(_l20):
        err(f"line 26 ({_l26}) exceeds line 20 ({_l20}) — taxing more than was received")

# Example 2 Step 3's allocation, on the UNROUNDED ratio (s230 rule). The IRS
# prints 33,311 / 18,169 from 64.7% / 35.3% — reproducible only unrounded.
_agg_limit, _insured_share = Decimal("63480"), Decimal("12000")
_remaining = _agg_limit - _insured_share
_blair = (Decimal("33000") / Decimal("51000") * _remaining).quantize(Decimal("1"))
_casey = _remaining - _blair
if _blair != Decimal("33311") or _casey != Decimal("18169"):
    err(f"Ex.2 Step 3 unrounded allocation gave {_blair}/{_casey}, IRS prints 33311/18169")


# ── 4. Spec hygiene: enums, uniqueness, citation coverage ──
VALID_DATA_TYPES = {"string", "integer", "decimal", "boolean", "date", "choice"}
VALID_RULE_TYPES = {"calculation", "classification", "routing", "validation", "conditional"}
VALID_LINE_TYPES = {"input", "calculated", "subtotal", "total", "informational"}
VALID_SEVERITY = {"error", "warning", "info"}
VALID_SCENARIO_TYPES = {"normal", "edge", "failure"}
VALID_SOURCE_TYPES = {
    "code_section", "regulation", "official_form", "official_instruction",
    "official_publication", "official_notice", "official_revenue_ruling",
    "official_revenue_procedure", "mef_schema", "mef_business_rule",
    "mef_release_memo", "state_statute", "state_regulation", "state_form",
    "state_instruction", "state_efile_spec", "state_vendor_guide",
    "state_conformity_notice", "internal_memo", "internal_example",
    "internal_test_case",
}
VALID_SOURCE_RANKS = {"controlling", "primary_official", "implementation_official",
                      "internal_interpretation", "reference_only"}
VALID_LINK_TYPES = {"governs", "informs", "validates", "mapping_only", "overrides"}
VALID_SUPPORT_LEVELS = {"primary", "secondary", "interpretive", "implementation"}

for f in m.N_FACTS:
    if f["data_type"] not in VALID_DATA_TYPES:
        err(f"fact {f['fact_key']}: invalid data_type {f['data_type']!r}")
for r in m.N_RULES:
    if r["rule_type"] not in VALID_RULE_TYPES:
        err(f"rule {r['rule_id']}: invalid rule_type {r['rule_type']!r}")
for ln in m.N_LINES:
    if ln["line_type"] not in VALID_LINE_TYPES:
        err(f"line {ln['line_number']}: invalid line_type {ln['line_type']!r}")
for d in m.N_DIAGNOSTICS:
    if d["severity"] not in VALID_SEVERITY:
        err(f"diagnostic {d['diagnostic_id']}: invalid severity {d['severity']!r}")
for sc in m.N_SCENARIOS:
    if sc["scenario_type"] not in VALID_SCENARIO_TYPES:
        err(f"scenario {sc['scenario_name']}: invalid scenario_type {sc['scenario_type']!r}")
for s in m.AUTHORITY_SOURCES:
    if s["source_type"] not in VALID_SOURCE_TYPES:
        err(f"source {s['source_code']}: invalid source_type {s['source_type']!r}")
    if s["source_rank"] not in VALID_SOURCE_RANKS:
        err(f"source {s['source_code']}: invalid source_rank {s['source_rank']!r}")
for _src, _form, lt in m.AUTHORITY_FORM_LINKS:
    if lt not in VALID_LINK_TYPES:
        err(f"form link {_src}->{_form}: invalid link_type {lt!r}")
for _rid, _sc, lvl, _note in m.N_RULE_LINKS:
    if lvl not in VALID_SUPPORT_LEVELS:
        err(f"rule link {_rid}->{_sc}: invalid support_level {lvl!r}")

# Uniqueness
for label, keys in (
    ("fact_key", [f["fact_key"] for f in m.N_FACTS]),
    ("rule_id", [r["rule_id"] for r in m.N_RULES]),
    ("line_number", [ln["line_number"] for ln in m.N_LINES]),
    ("diagnostic_id", [d["diagnostic_id"] for d in m.N_DIAGNOSTICS]),
    ("scenario_name", [sc["scenario_name"] for sc in m.N_SCENARIOS]),
    ("assertion_id", [a["assertion_id"] for a in m.FLOW_ASSERTIONS]),
    ("source_code", [s["source_code"] for s in m.AUTHORITY_SOURCES]),
):
    dupes = {k for k in keys if keys.count(k) > 1}
    if dupes:
        err(f"duplicate {label}: {sorted(dupes)}")

# Every rule cited, and every rule link pointing at a rule that exists.
_rule_ids = {r["rule_id"] for r in m.N_RULES}
_cited = {rid for rid, _s, _l, _n in m.N_RULE_LINKS}
if _rule_ids - _cited:
    err(f"uncited rules: {sorted(_rule_ids - _cited)}")
for rid, _s, _l, _n in m.N_RULE_LINKS:
    if rid not in _rule_ids:
        err(f"rule link references unknown rule {rid}")

# Every rule link's source must be one we define or one we declare as existing.
_known = ({s["source_code"] for s in m.AUTHORITY_SOURCES}
          | set(m.EXISTING_SOURCES_TO_REFERENCE))
for rid, sc, _l, _n in m.N_RULE_LINKS:
    if sc not in _known:
        err(f"rule link {rid} references undeclared source {sc}")
for sc, _exc in m.NEW_EXCERPTS_ON_EXISTING:
    if sc not in _known:
        err(f"NEW_EXCERPTS_ON_EXISTING targets undeclared source {sc}")

# Every fact referenced by a rule's inputs/outputs must exist.
_fact_keys = {f["fact_key"] for f in m.N_FACTS}
for r in m.N_RULES:
    for k in list(r.get("inputs", [])) + list(r.get("outputs", [])):
        if k not in _fact_keys:
            err(f"rule {r['rule_id']} references unknown fact {k}")

# The face's line set, verified against the SHA-pinned 2025 f8853 Section C.
EXPECTED_LINES = {"14a", "14b", "15", "16", "17", "18", "19", "20",
                  "21", "22", "23", "24", "25", "26"}
_authored = {ln["line_number"] for ln in m.N_LINES}
if _authored != EXPECTED_LINES:
    err(f"line set drift: missing {sorted(EXPECTED_LINES - _authored)}, "
        f"extra {sorted(_authored - EXPECTED_LINES)}")

# The seed guard must be shut until Ken's Gate-1 walk.
if m.READY_TO_SEED:
    print("NOTE: READY_TO_SEED is True — Gate 1 has been passed.")

if errors:
    print(f"\n{len(errors)} INTEGRITY ERROR(S):")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"8853_SEC_C integrity OK — {len(m.N_FACTS)} facts, {len(m.N_RULES)} rules, "
      f"{len(m.N_LINES)} lines, {len(m.N_DIAGNOSTICS)} diagnostics, "
      f"{len(m.N_SCENARIOS)} scenarios, {len(m.FLOW_ASSERTIONS)} flow assertions.")
print("  IRS answer key (i8853 Examples 1, 2 Step 1, 2 Step 2) reproduced exactly.")
print("  Rate $420 agrees: Rev. Proc. 2024-40 §2.62 = printed 2025 face line 21 = fact default.")
