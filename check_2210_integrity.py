"""Pre-seed math gate for load_1040_2210 (Underpayment of Estimated Tax §6654).

Run:  poetry run python check_2210_integrity.py

Independently recomputes every scenario from its OWN transcription of the §6654
required annual payment (min(90% current, 100/110% prior)), the $1,000 de-minimis,
and the §6621 regular-method penalty — the DATED accrual (2026-07-01 amendment:
each payment applies to the earliest still-underpaid installment and stops that
amount's accrual on the date paid, capped 4/15/2026; 7% through 3/31/2026 then
6%) + Schedule AI. Also pins the day-count equivalence: the dated day counter at
the cap reproduces the legacy DAYS_7/DAYS_6 arrays. The loader and this gate
share NO math.
"""
import os
import sys
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from specs.management.commands import load_1040_2210 as m  # noqa: E402

errors: list[str] = []


def err(msg):
    errors.append(msg)


def D(x):
    return Decimal(str(x if x is not None else 0))


def check(name, got, want):
    if D(got) != D(want):
        err(f"{name}: recomputed {got} != authored {want}")


def r0(x):
    return int(D(x).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


# ── Independent math (re-typed) ──
# RATE RE-VERIFIED 2026-07-26 against the 2025 i2210 Penalty Worksheet: × 0.07
# in ALL FOUR rate periods (Rate Period 4 = 1/1/2026–4/15/2026, one 7% period;
# Table 2 total days 365/304/212/90). The prior 350/15-style 7%/6% split was a
# pre-publication assumption.
IND_DAYS7 = [365, 304, 212, 90]
IND_DAYS6 = [0, 0, 0, 0]
IND_AI_PCT = [Decimal("0.225"), Decimal("0.45"), Decimal("0.675"), Decimal("0.90")]
IND_DUE = [date(2025, 4, 15), date(2025, 6, 15), date(2025, 9, 15), date(2026, 1, 15)]
IND_R7_END = date(2026, 4, 15)
IND_CAP = date(2026, 4, 15)


def ind_factor(i):
    return D(IND_DAYS7[i]) / 365 * Decimal("0.07") + D(IND_DAYS6[i]) / 365 * Decimal("0.06")


def ind_days(due, end):
    """Independent day counter: (days@7%, days@6%) for an underpayment due
    `due` cured `end` (capped by the caller). Simple date subtraction."""
    if end <= due:
        return 0, 0
    d7 = max(0, (min(end, IND_R7_END) - due).days)
    d6 = max(0, (min(end, IND_CAP) - max(due, IND_R7_END)).days)
    return d7, d6


def ind_chunk(due, cure, amount):
    d7, d6 = ind_days(due, min(cure, IND_CAP))
    return D(amount) * (D(d7) / 365 * Decimal("0.07") + D(d6) / 365 * Decimal("0.06"))


def ind_columns(installments, withholding, est_payments, payments_dated=None):
    """Part III Section A lines 10-18, re-typed 2026-07-27 straight from the
    2025 face text — deliberately NOT from the loader's version.

      10 required installment            13 = 11 + 12
      11 paid this column (wh/4 + window) 14 = prev 16 + prev 17
      12 = prev 18                        15 = 13 - 14 (floor 0); col (a) = 11
      16 = 14 - 13 when 15 is zero        17 underpayment = 10 - 15 when 10 >= 15
      18 overpayment = 15 - 10 when 15 > 10

    Line 14 is the part that matters: this column's money covers the previous
    column's still-unpaid amount BEFORE it counts toward this installment.
    """
    if payments_dated:
        pays = [(date.fromisoformat(str(dd)), D(a)) for dd, a in payments_dated]
    else:
        pays = [(IND_DUE[i], D(est_payments[i])) for i in range(4)]
    per_col = [D(withholding) / 4 for _ in range(4)]
    for when, amt in pays:
        for i in range(4):
            if when <= IND_DUE[i]:
                per_col[i] += D(amt)
                break
    cols = []
    p16 = p17 = p18 = D(0)
    for i in range(4):
        c10 = D(installments[i])
        c11 = per_col[i]
        c12 = p18
        c13 = c11 + c12
        c14 = p16 + p17
        c15 = c11 if i == 0 else max(D(0), c13 - c14)
        c16 = (c14 - c13) if c15 == 0 else D(0)
        c17 = (c10 - c15) if c10 >= c15 else D(0)
        c18 = (c15 - c10) if c15 > c10 else D(0)
        cols.append({"10": c10, "11": c11, "12": c12, "13": c13, "14": c14,
                     "15": c15, "16": c16, "17": c17, "18": c18})
        p16, p17, p18 = c16, c17, c18
    return cols


def ind_compute(current_tax=0, other_taxes=0, refundable_credits=0, withholding=0, prior_year_tax=0,
                prior_year_agi=0, filing_status="single", prior_full_year=True, est_payments=(0, 0, 0, 0),
                use_annualized=False, ai_tax=(0, 0, 0, 0), payments_dated=None,
                penalty_source_amount=None, penalty_source_label="", penalty_source_note=""):
    l4 = D(current_tax) + D(other_taxes) - D(refundable_credits)
    l5 = D(r0(l4 * Decimal("0.90")))
    l7 = l4 - D(withholding)
    agi_thr = 75000 if (filing_status or "single").lower() == "mfs" else 150000
    pct = Decimal("1.10") if D(prior_year_agi) > agi_thr else Decimal("1.00")
    l8 = D(r0(D(prior_year_tax) * pct)) if (prior_full_year and D(prior_year_tax) > 0) else None
    l9 = l5 if l8 is None else min(l5, l8)
    if l7 < 1000:
        return {"l8": D(l8 or 0), "l9": l9, "penalty": Decimal("0"), "columns": []}
    reg = [l9 / 4] * 4
    if use_annualized:
        inst, prior = [], Decimal("0")
        for i in range(4):
            ann = max(Decimal("0"), D(ai_tax[i]) * IND_AI_PCT[i] - prior)
            req = min(ann, reg[i])
            inst.append(req)
            prior += req
        installments = inst
    else:
        installments = reg
    # Dated accrual, independently re-typed: payment events in date order
    # (withholding 1/4 ON each due date + dated payments, or the quarter
    # buckets dated on their due dates); each applies earliest-first; chunks
    # accrue due -> min(cured, cap); leftovers accrue due -> cap.
    if payments_dated:
        pays = [(date.fromisoformat(str(dd)), D(a)) for dd, a in payments_dated]
    else:
        pays = [(IND_DUE[i], D(est_payments[i])) for i in range(4)]
    wh_q = D(withholding) / 4
    events = sorted([(IND_DUE[i], wh_q) for i in range(4) if wh_q > 0] + pays,
                    key=lambda e: e[0])
    remaining = [D(x) for x in installments]
    penalty = Decimal("0")
    for paid_on, amt in events:
        amt = D(amt)
        for i in range(4):
            if amt <= 0:
                break
            if remaining[i] <= 0:
                continue
            take = min(amt, remaining[i])
            remaining[i] -= take
            amt -= take
            penalty += ind_chunk(IND_DUE[i], paid_on, take)
    for i in range(4):
        if remaining[i] > 0:
            penalty += ind_chunk(IND_DUE[i], IND_CAP, remaining[i])
    cols = ind_columns(installments, withholding, est_payments, payments_dated)
    # R-2210-SRC: a documented source amount controls what the RETURN reports,
    # but never replaces the computed penalty (which stays right here).
    computed = D(r0(penalty))
    reported = D(penalty_source_amount) if penalty_source_amount is not None else computed
    return {"l8": D(l8 or 0), "l9": l9, "penalty": computed, "reported_penalty": reported,
            "columns": cols, "line_10": [c["10"] for c in cols], "line_17": [c["17"] for c in cols]}


# ── 1. Loader constants + helpers vs the independent transcription ──
check("PCT_CURRENT", D(m.PCT_CURRENT), Decimal("0.90"))
check("RATE_7", D(m.RATE_7), Decimal("0.07"))
check("RATE_6", D(m.RATE_6), Decimal("0.07"))  # equal rates in TY2025 (i2210)
for i in range(4):
    check(f"DAYS_7[{i}]", m.DAYS_7[i], IND_DAYS7[i])
    check(f"AI_PCT[{i}]", m.AI_PCT[i], IND_AI_PCT[i])
    check(f"penalty_factor({i})", m.penalty_factor(i), ind_factor(i))
    # Dated amendment: due dates match, and the day counter at the cap
    # reproduces the legacy fixed-day arrays (both loaders AND this gate's
    # independent counter).
    if m.DUE_DATES[i] != IND_DUE[i]:
        err(f"DUE_DATES[{i}]: {m.DUE_DATES[i]} != {IND_DUE[i]}")
    check(f"days_at_rates({i}, cap).d7 (loader)", m.days_at_rates(m.DUE_DATES[i], m.CAP_DATE)[0], IND_DAYS7[i])
    check(f"days_at_rates({i}, cap).d6 (loader)", m.days_at_rates(m.DUE_DATES[i], m.CAP_DATE)[1], IND_DAYS6[i])
    check(f"ind_days({i}, cap).d7", ind_days(IND_DUE[i], IND_CAP)[0], IND_DAYS7[i])
    check(f"ind_days({i}, cap).d6", ind_days(IND_DUE[i], IND_CAP)[1], IND_DAYS6[i])
if m.R7_END != IND_R7_END:
    err(f"R7_END: {m.R7_END} != {IND_R7_END}")
if m.CAP_DATE != IND_CAP:
    err(f"CAP_DATE: {m.CAP_DATE} != {IND_CAP}")
# A payment on/before the due date must accrue zero days (both transcriptions).
if m.days_at_rates(m.DUE_DATES[0], m.DUE_DATES[0]) != (0, 0):
    err("loader days_at_rates(due, due) != (0, 0)")
if ind_days(IND_DUE[0], IND_DUE[0]) != (0, 0):
    err("ind_days(due, due) != (0, 0)")

# ── 2. Scenarios — independent recompute ──
DIAG_KEYS = {"D_2210_NO_PENALTY", "D_2210_PRIOR_YEAR", "D_2210_110", "D_2210_AI",
             "D_2210_TY2026", "D_2210_DATED", "D_2210_SRC", "D_2210_TIE"}
# Scenario inputs the pure functions don't take (they describe app state).
NON_COMPUTE_INPUTS = {"tax_year", "penalty_source_label", "penalty_source_note"}
spec = m.FORMS[0]


def _compute_kwargs(inp):
    return {k: v for k, v in inp.items() if k not in NON_COMPUTE_INPUTS}


for s in spec["scenarios"]:
    name = s["scenario_name"].split(" ")[0]
    inp, exp = s["inputs"], s["expected_outputs"]
    if any(k in DIAG_KEYS for k in exp):
        if exp.get("D_2210_NO_PENALTY") and (D(inp.get("current_tax", 0)) - D(inp.get("withholding", 0))) >= 1000:
            err(f"{name}: D_2210_NO_PENALTY expected but line 7 >= 1000")
        if exp.get("D_2210_DATED"):
            dated_total = sum((D(a) for _, a in inp.get("payments_dated", [])), D(0))
            flat_total = sum((D(x) for x in inp.get("est_payments", [0, 0, 0, 0])), D(0))
            if dated_total == flat_total:
                err(f"{name}: D_2210_DATED expected but dated total == flat line-26 total")
        if exp.get("D_2210_SRC"):
            # Effect-scaled: the diagnostic exists to flag a DIVERGENCE. A
            # scenario claiming it fires must actually diverge, and the
            # source/reason must be documented (R-2210-SRC requires both).
            src = inp.get("penalty_source_amount")
            if src is None:
                err(f"{name}: D_2210_SRC expected but no penalty_source_amount entered")
            else:
                base = ind_compute(**_compute_kwargs(
                    {k: v for k, v in inp.items() if k != "penalty_source_amount"}))
                if D(src) == base["penalty"]:
                    err(f"{name}: D_2210_SRC expected but the source amount EQUALS "
                        f"the computed penalty ({src}) — corroboration must stay silent")
                if not inp.get("penalty_source_label") or not inp.get("penalty_source_note"):
                    err(f"{name}: D_2210_SRC scenario omits the source label/reason "
                        f"(R-2210-SRC requires both whenever an amount is entered)")
        continue
    got = ind_compute(**_compute_kwargs(inp))
    # cross-check the loader helper too
    gl = m.compute_2210(**_compute_kwargs(inp))
    out_map = {"t2210_line8": "l8", "t2210_line9": "l9", "t2210_penalty": "penalty",
               "line_10": "line_10", "line_17": "line_17"}
    for k, want in exp.items():
        if k in DIAG_KEYS:
            continue
        if k not in out_map:
            err(f"{name}.{k}: no independent recompute mapped")
            continue
        if isinstance(want, list):
            # Per-column expectations: compare all four columns element-wise.
            g_ind = got[out_map[k]]
            g_load = [c[k.split("_")[1]] for c in gl.get("columns", [])]
            if len(g_ind) != len(want):
                err(f"{name}.{k}: recomputed {len(g_ind)} columns != authored {len(want)}")
                continue
            for i, w in enumerate(want):
                check(f"{name}.{k}[{i}] (ind)", g_ind[i], w)
            if len(g_load) != len(want):
                err(f"{name}.{k}: loader returned {len(g_load)} columns != authored {len(want)}")
            else:
                for i, w in enumerate(want):
                    check(f"{name}.{k}[{i}] (loader)", g_load[i], w)
            continue
        check(f"{name}.{k} (ind)", got[out_map[k]], want)
        check(f"{name}.{k} (loader)", gl[out_map[k]], want)

# ── 2b. The face grid: the two allocations agree on the due dates, and the
# column identities hold in every scenario (independent transcription only).
for s in spec["scenarios"]:
    inp = s["inputs"]
    if D(inp.get("current_tax", 0)) - D(inp.get("withholding", 0)) < 1000:
        continue
    name = s["scenario_name"].split(" ")[0]
    got = ind_compute(**_compute_kwargs(inp))
    for i, c in enumerate(got["columns"]):
        if c["13"] != c["11"] + c["12"]:
            err(f"{name} col{i}: line 13 != 11 + 12")
        if c["17"] > 0 and c["18"] > 0:
            err(f"{name} col{i}: both an underpayment AND an overpayment")
        if c["17"] < 0 or c["18"] < 0 or c["15"] < 0 or c["16"] < 0:
            err(f"{name} col{i}: negative face amount")
    # Line 12 of each column must be the PREVIOUS column's line 18.
    for i in range(1, 4):
        if got["columns"][i]["12"] != got["columns"][i - 1]["18"]:
            err(f"{name} col{i}: line 12 != previous column's line 18")
        if got["columns"][i]["14"] != got["columns"][i - 1]["16"] + got["columns"][i - 1]["17"]:
            err(f"{name} col{i}: line 14 != previous column's 16 + 17")

# ── 2c. Section A must TIE to Section B ──
# The face's line 17 is a RUNNING OUTSTANDING balance (line 14 makes each
# column's payments cover the prior column's unpaid amount first), while the
# penalty charges each period's own shortfall from its own due date to the cap.
# Those are the same integral of outstanding-dollars over time, so:
#
#   Σ_i (line16_i + line17_i) × days(due_i → due_{i+1}, last one → cap) × 0.07/365
#
# must equal the Section B penalty. Computed by two completely different routes,
# so agreement is real evidence — and it is what proves the running-balance
# reading of line 17 is right rather than a transcription slip.
# Only meaningful with no estimated payments (withholding-only), where nothing
# is cured early and the whole balance rides to the cap.
IND_NEXT = [IND_DUE[1], IND_DUE[2], IND_DUE[3], IND_CAP]
for s in spec["scenarios"]:
    inp = s["inputs"]
    if inp.get("payments_dated") or any(D(x) for x in inp.get("est_payments", [0, 0, 0, 0])):
        continue
    if D(inp.get("current_tax", 0)) - D(inp.get("withholding", 0)) < 1000:
        continue
    name = s["scenario_name"].split(" ")[0]
    got = ind_compute(**_compute_kwargs(inp))
    amount_days = D(0)
    for i, c in enumerate(got["columns"]):
        outstanding = c["16"] + c["17"]
        amount_days += outstanding * D((IND_NEXT[i] - IND_DUE[i]).days)
    tie = D(r0(amount_days * Decimal("0.07") / 365))
    if tie != got["penalty"]:
        err(f"{name}: Section A ties to {tie} but Section B computed {got['penalty']} "
            f"(the running-balance and per-period readings must integrate to the same amount-days)")

# The divergence that motivated the renumber+rewrite: a LATE catch-up payment.
# The retired overpayment-carry-only allocation credited it to the current
# column; the face makes it cure the earlier shortfall first. Pinned so the old
# behaviour can never quietly return.
_late = ind_columns([D(2500)] * 4, 0, [0, 0, 5000, 0])
if [c["17"] for c in _late] != [D(2500)] * 4:
    err(f"late catch-up: face underpayments {[str(c['17']) for c in _late]} != [2500]*4 "
        f"(the payment must cover columns (a)+(b) via line 14 before column (c)'s own installment)")

# ── 3. Structural checks ──
known_sources = {s["source_code"] for s in m.AUTHORITY_SOURCES} | set(m.EXISTING_SOURCES_TO_REFERENCE)
for key, idk in (("facts", "fact_key"), ("rules", "rule_id"), ("lines", "line_number"),
                 ("diagnostics", "diagnostic_id"), ("scenarios", "scenario_name")):
    ids = [x[idk] for x in spec[key]]
    if len(ids) != len(set(ids)):
        err(f"FORM_2210.{key}: duplicate ids")
for r in spec["rules"]:
    if len(r["rule_id"]) > 20:
        err(f"rule_id too long ({len(r['rule_id'])} > 20): {r['rule_id']}")
for d in spec["diagnostics"]:
    # 40, not 20 — FormDiagnostic.diagnostic_id was widened 20 -> 40 in
    # specs.0003 (s115) because the app's canonical codes run past 20. This
    # guard still said 20.
    if len(d["diagnostic_id"]) > 40:
        err(f"diagnostic_id too long ({len(d['diagnostic_id'])} > 40): {d['diagnostic_id']}")

# ── 3b. The 2025 face line numbering (2026-07-27 renumber) ──
# Transcribed from resources/irs_forms/2025/f2210.pdf: Part I = 1-9,
# Part III Section A = 10-18, Section B = 19.
FACE_LINES = {str(n) for n in range(1, 20)}
authored = {ln["line_number"] for ln in spec["lines"]}
missing = FACE_LINES - authored
if missing:
    err(f"face lines absent from the spec: {sorted(missing, key=int)}")
for retired in m.RETIRED_LINES:
    if retired in authored:
        err(f"line {retired} is in RETIRED_LINES but still authored in P_LINES — "
            f"the retirement would delete the row this load just wrote")
    if retired in FACE_LINES:
        err(f"line {retired} is marked retired but IS a 2025 face line")
# The specific correction: line 18 must describe the OVERPAYMENT and line 10
# the required installment. Guards the exact mistake being fixed.
_by_num = {ln["line_number"]: ln["description"].lower() for ln in spec["lines"]}
if "required installment" not in _by_num.get("10", ""):
    err("line 10 must be the required installment (2025 face)")
if "overpayment" not in _by_num.get("18", ""):
    err("line 18 must be the OVERPAYMENT on the 2025 face — it was previously "
        "specced as the required installment (superseded numbering)")
if "underpayment" not in _by_num.get("17", ""):
    err("line 17 must be the underpayment (2025 face)")
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
        if k.startswith("D_2210_") and k not in diag_ids:
            err(f"{sc['scenario_name']}: expects unknown diagnostic {k}")
fa_ids = [a["assertion_id"] for a in m.FLOW_ASSERTIONS]
if len(fa_ids) != len(set(fa_ids)):
    err("duplicate flow-assertion ids")

# ── Report ──
print("FORM_2210 (facts/rules/lines/diagnostics/scenarios/links):",
      (len(spec["facts"]), len(spec["rules"]), len(spec["lines"]),
       len(spec["diagnostics"]), len(spec["scenarios"]), len(spec["rule_links"])))
print(f"Flow assertions: {len(m.FLOW_ASSERTIONS)}; authority sources: {len(m.AUTHORITY_SOURCES)}")
print("Independently recomputed - T1 deminimis 0 / T2 prior-SH 0 / T3 full 466 / T4 110% l9=44000 / "
      "T5 estimates-cure 0 / T6 partial 145 / T7 dated-lump 219 / T8 late-Q4 5 / T9 per-column "
      "l8=27473 l9=23837 pen=289 / T10 no-prior 189 / T11 same-return-with-prior 0; the §6654 safe "
      "harbors + the §6621 dated accrual (earliest-first, due date -> date cured, FLAT 7% to the "
      "4/15/2026 cap per the 2025 i2210 Penalty Worksheet, re-verified 2026-07-26) + the DAYS "
      "equivalence at the cap + Schedule AI cross-checked.")
print("Part III Section A (2025 face lines 10-18) re-typed independently: column identities, the "
      "12<-prev-18 and 14<-prev-(16+17) carries, and the late-catch-up divergence from the retired "
      "overpayment-carry-only allocation.")

if errors:
    print("\nFAILURES:")
    for e in errors:
        print(f"  X {e}")
    sys.exit(1)
print("\nALL CHECKS PASS")
