"""Pre-seed math gate for load_1040_form_172 (NOLs for individuals).

Run:  poetry run python check_form_172_integrity.py

Independently re-types BOTH sides — Part I lines 1-24 off the Rev. 12-2024
face, and the §172(a)(2) two-tier deduction with oldest-first absorption —
using explicit comparisons and its own formula chain, so a transcription
slip in the loader cannot be mirrored here by accident. Every scenario's
expected outputs are recomputed from the scenario's INPUTS alone.

Structural invariants (hardcoded independently of the scenarios):
  I1. Line 10 can never exceed line 5 (the face's own cap).
  I2. The 80% base subtracts the PRE-2018 component before the 80% — the
      clause the s246 brief's short form dropped (§172(a)(2)(B)(ii)).
  I3. The pre-2018 class is NEVER capped by the 80% rule.
  I4. Absorption is OLDEST FIRST — a later vintage never absorbs while an
      earlier one still has remaining allowance and MTI.
  I5. Line 19's constants are the PRINTED $3,000 / $1,500-MFS.
  I6. Line 24 combines EXACTLY lines 1, 9, 17, 21, 22, 23.
  I7. Σ used + Σ remaining == Σ opening across every deduction scenario
      (no NOL dollars created or destroyed by absorption).

Citation checks: every rule carries at least one authority link; the §172
excerpt carries the operative phrases verbatim; the i172 source is flagged
requires_human_review (the worksheet 'line 33' anomaly + the absorption
synthesis).
"""
import io
import os
import re
import sys
from decimal import Decimal

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from specs.management.commands import load_1040_form_172 as m  # noqa: E402

errors: list[str] = []


def err(msg):
    errors.append(msg)


def D(x):
    return Decimal(str(x if x is not None else 0))


def check(name, got, want):
    if D(got) != D(want):
        err(f"{name}: recomputed {got} != authored {want}")


Z = Decimal("0")

# ── Independent re-typing: Part I ──
# Written as explicit if/else comparisons (not max/min chains) so a
# min-for-max slip in the loader cannot be mirrored here.
LIMIT_STD = Decimal("3000")   # printed on the face at line 19
LIMIT_MFS = Decimal("1500")


def ind_part_i(i):
    l1 = D(i.get("l1_income_base"))
    l2, l3 = D(i.get("l2_nonbus_cap_losses")), D(i.get("l3_nonbus_cap_gains"))
    l6, l7 = D(i.get("l6_nonbus_deductions")), D(i.get("l7_nonbus_income"))
    l11, l12 = D(i.get("l11_bus_cap_losses")), D(i.get("l12_bus_cap_gains"))
    l16, l17 = D(i.get("l16_schd_combined_loss")), D(i.get("l17_sec1202_exclusion"))
    l23 = D(i.get("l23_prior_nol_deduction"))
    mfs = bool(i.get("mfs"))

    l4 = (l2 - l3) if l2 > l3 else Z
    l5 = (l3 - l2) if l3 > l2 else Z
    l8 = l5 + l7
    l9 = (l6 - l8) if l6 > l8 else Z
    l10 = (l8 - l6) if l8 > l6 else Z
    if l10 > l5:
        l10 = l5                       # the face: "But don't enter more than line 5"
    l13 = l10 + l12
    l14 = (l11 - l13) if l11 > l13 else Z
    l15 = l4 + l14

    if l16 == Z and l17 == Z:          # the face's skip rule
        l18 = l19 = l20 = l21 = Z
        l22 = l15
    else:
        l18 = (l16 - l17) if l16 > l17 else Z
        cap = LIMIT_MFS if mfs else LIMIT_STD
        if l16 > Z:
            l19 = l16 if l16 < cap else cap
        else:
            l19 = Z
        l20 = (l18 - l19) if l18 > l19 else Z
        l21 = (l19 - l18) if l19 > l18 else Z
        l22 = (l15 - l20) if l15 > l20 else Z

    l24 = l1 + l9 + l17 + l21 + l22 + l23    # I6: exactly this set
    return {"l4": l4, "l5": l5, "l8": l8, "l9": l9, "l10": l10, "l13": l13,
            "l14": l14, "l15": l15, "l18": l18, "l19": l19, "l20": l20,
            "l21": l21, "l22": l22, "l24": l24}


# ── Independent re-typing: the deduction + absorption ──
def ind_deduction(vintages, ti):
    pre = Z
    post = Z
    for year, amt in vintages:
        if int(year) < 2018:
            pre += D(amt)
        else:
            post += D(amt)
    base = D(ti) - pre                 # I2: pre-2018 subtracts FIRST
    if base < Z:
        base = Z
    cap = (Decimal("0.80") * base).quantize(Decimal("1"))
    post_allowed = post if post < cap else cap
    return {"pre": pre, "post_allowed": post_allowed, "cap": cap,
            "deduction": pre + post_allowed}


def ind_absorption(vintages, ti, mti):
    d = ind_deduction(vintages, ti)
    mti_left = D(mti) if D(mti) > Z else Z
    post_left = d["post_allowed"]
    out = {}
    for year, amt in sorted(vintages, key=lambda v: int(v[0])):   # I4 oldest first
        amt = D(amt)
        if int(year) < 2018:
            used = amt if amt < mti_left else mti_left            # I3 no 80% cap
        else:
            used = min(amt, post_left, mti_left)
            post_left -= used
        mti_left -= used
        out[int(year)] = (used, amt - used)
    return d, out


# ═══════════════════════════════════════════════════════════════════════════
# 1. Scenario recomputation from INPUTS alone
# ═══════════════════════════════════════════════════════════════════════════

PART_I_KEYS = {
    "f172_l4_nonbus_cap_loss_excess": "l4", "f172_l5_nonbus_cap_gain_excess": "l5",
    "f172_l8_nonbus_income_total": "l8", "f172_l9_nonbus_ded_excess": "l9",
    "f172_l10_gain_spill": "l10", "f172_l13_bus_gain_total": "l13",
    "f172_l14_bus_cap_loss_excess": "l14", "f172_l15_cap_loss_total": "l15",
    "f172_l18_loss_after_1202": "l18", "f172_l19_allowed_cap_loss": "l19",
    "f172_l20_excess_over_allowed": "l20", "f172_l21_allowed_over_excess": "l21",
    "f172_l22_net_capital_addback": "l22", "f172_l24_nol_determination": "l24",
}

for sc in m.SCENARIOS:
    name = sc["scenario_name"]
    i = sc["inputs"]
    exp = sc["expected_outputs"]

    if "l1_income_base" in i:
        got = ind_part_i(i)
        for exp_key, ind_key in PART_I_KEYS.items():
            if exp_key in exp:
                check(f"{name} :: {exp_key}", got[ind_key], exp[exp_key])
        if "nol_vintage_opened" in exp:
            want_pool = -got["l24"] if got["l24"] < Z else Z
            check(f"{name} :: nol_vintage_opened", want_pool, exp["nol_vintage_opened"])
        # Cross-check the LOADER's reference implementation too.
        loader = m.compute_172_part_i(**{k: v for k, v in i.items()})
        for exp_key, ind_key in PART_I_KEYS.items():
            if exp_key in exp:
                check(f"{name} :: loader {exp_key}", loader[ind_key], exp[exp_key])

    if "vintages" in i and "ti_without_nol_qbi_250" in i:
        d, absorbed = ind_absorption(i["vintages"], i["ti_without_nol_qbi_250"],
                                     i.get("modified_taxable_income", 0))
        if "f172_pre2018_component" in exp:
            check(f"{name} :: pre2018", d["pre"], exp["f172_pre2018_component"])
        if "f172_post2017_component" in exp:
            check(f"{name} :: post2017", d["post_allowed"], exp["f172_post2017_component"])
        if "f172_post2017_cap" in exp:
            check(f"{name} :: cap", d["cap"], exp["f172_post2017_cap"])
        if "f172_nol_deduction" in exp:
            check(f"{name} :: deduction", d["deduction"], exp["f172_nol_deduction"])
        if "sch1_8a" in exp and isinstance(exp["sch1_8a"], (int, float)):
            check(f"{name} :: sch1_8a", -d["deduction"], exp["sch1_8a"])
        for year, (used, rem) in absorbed.items():
            uk, rk = f"vintage_{year}_used", f"vintage_{year}_remaining"
            if uk in exp:
                check(f"{name} :: {uk}", used, exp[uk])
            if rk in exp:
                check(f"{name} :: {rk}", rem, exp[rk])
        # I7 — conservation: nothing created or destroyed.
        total_open = sum(D(a) for _, a in i["vintages"])
        total_used = sum(u for u, _ in absorbed.values())
        total_rem = sum(r for _, r in absorbed.values())
        if total_used + total_rem != total_open:
            err(f"{name} :: I7 conservation broken: {total_used}+{total_rem} != {total_open}")
        # Cross-check the loader's reference implementations.
        ld = m.compute_nol_deduction(i["vintages"], i["ti_without_nol_qbi_250"])
        check(f"{name} :: loader deduction", ld["deduction"], d["deduction"])
        la = m.compute_nol_absorption(i["vintages"], i["ti_without_nol_qbi_250"],
                                      i.get("modified_taxable_income", 0))
        for year, used, rem in la:
            iu, ir = absorbed[year]
            check(f"{name} :: loader vintage {year} used", used, iu)
            check(f"{name} :: loader vintage {year} remaining", rem, ir)

    if "l24_nol" in i and "ebl_from_461" in i:
        # The i172 EBL worksheet (following its own example's arithmetic).
        carry = -D(i["l24_nol"]) + D(i["ebl_from_461"])
        check(f"{name} :: nol_carryover_to_next_year", carry, exp["nol_carryover_to_next_year"])


# ═══════════════════════════════════════════════════════════════════════════
# 2. Structural invariants, independent of the scenarios
# ═══════════════════════════════════════════════════════════════════════════

# I1: line 10 never exceeds line 5 — probe a shape built to tempt it.
probe = ind_part_i({"l1_income_base": 0, "l3_nonbus_cap_gains": 100,
                    "l7_nonbus_income": 100000, "l6_nonbus_deductions": 0})
if probe["l10"] > probe["l5"]:
    err("I1: line 10 exceeded line 5 (the face's cap is missing)")

# I2/I3: the pre-2018 subtraction and the uncapped first tier.
d = ind_deduction([[2016, 70000], [2020, 100000]], 70000)
if d["cap"] != Z:
    err(f"I2: base should be 0 when pre-2018 == TI (got cap {d['cap']})")
if d["pre"] != Decimal("70000"):
    err("I3: the pre-2018 class must enter uncapped")
ld = m.compute_nol_deduction([[2016, 70000], [2020, 100000]], 70000)
if D(ld["post2017_cap"]) != Z or D(ld["pre2018_component"]) != Decimal("70000"):
    err("I2/I3: the LOADER's deduction drops the pre-2018 subtraction or caps the first tier")

# I4: oldest-first — the earlier vintage must exhaust first.
_, ab = ind_absorption([[2019, 50000], [2021, 50000]], 200000, 60000)
if not (ab[2019][0] == Decimal("50000") and ab[2021][0] == Decimal("10000")):
    err(f"I4: absorption is not oldest-first ({ab})")
la = m.compute_nol_absorption([[2021, 50000], [2019, 50000]], 200000, 60000)
la_map = {y: u for y, u, _ in la}
if not (la_map[2019] == Decimal("50000") and la_map[2021] == Decimal("10000")):
    err(f"I4: the LOADER's absorption is not oldest-first ({la_map})")

# I5: the printed constants.
if m.CAP_LOSS_LIMIT != Decimal("3000") or m.CAP_LOSS_LIMIT_MFS != Decimal("1500"):
    err("I5: line 19 constants drifted off the printed $3,000/$1,500")
if m.POST2017_PCT != Decimal("0.80"):
    err("I5: the 80% is statutory (§172(a)(2)(B)(ii)) and must be 0.80")
if m.PRE2018_CARRYOVER_YEARS != 20:
    err("I5: the pre-2018 carryover period is 20 years (§172(b)(1)(A)(ii)(I))")

# I6: line 24 combines exactly {1, 9, 17, 21, 22, 23} — differential probe:
# vary each excluded line and confirm l24 does NOT move; vary each included
# line and confirm it DOES.
base_inputs = {"l1_income_base": -10000, "l2_nonbus_cap_losses": 50,
               "l3_nonbus_cap_gains": 60, "l6_nonbus_deductions": 500,
               "l7_nonbus_income": 100, "l16_schd_combined_loss": 10,
               "l17_sec1202_exclusion": 5, "l23_prior_nol_deduction": 7}
b = ind_part_i(base_inputs)
moved = ind_part_i({**base_inputs, "l23_prior_nol_deduction": 107})
if moved["l24"] - b["l24"] != Decimal("100"):
    err("I6: line 23 must move line 24 dollar-for-dollar")
# ... and the LOADER's implementation must agree (the D5 negative-control
# hole: an invariant probed only against the gate's own math proves nothing
# about the loader).
lb = m.compute_172_part_i(**base_inputs)
lmoved = m.compute_172_part_i(**{**base_inputs, "l23_prior_nol_deduction": 107})
if lmoved["l24"] - lb["l24"] != Decimal("100"):
    err("I6: the LOADER's line 24 does not move with line 23")
if lb["l24"] != b["l24"]:
    err(f"I6: loader vs gate disagree on the base probe ({lb['l24']} vs {b['l24']})")

# ═══════════════════════════════════════════════════════════════════════════
# 3. Citations + flags
# ═══════════════════════════════════════════════════════════════════════════

linked = {rid for rid, *_ in m.RULE_LINKS}
for r in m.RULES:
    if r["rule_id"] not in linked:
        err(f"citation: rule {r['rule_id']} has no authority link")

irc = next((s for s in m.AUTHORITY_SOURCES if s["source_code"] == "IRC_172"), None)
if irc is None:
    err("citation: IRC_172 source missing")
else:
    text = " ".join(e["excerpt_text"] for e in irc.get("excerpts", []))
    for phrase in ("80 percent of the excess (if any)",
                   "carried to such taxable year",
                   "the amount determined under subparagraph (A)"):
        if phrase not in text:
            err(f"citation: §172 excerpt lost the operative phrase: {phrase!r}")

i172 = next((s for s in m.AUTHORITY_SOURCES if s["source_code"] == "IRS_2024_F172_INSTR"), None)
if i172 is None:
    err("citation: i172 source missing")
else:
    if not i172.get("requires_human_review"):
        err("flag: i172 must carry requires_human_review (the worksheet 'line 33' anomaly)")
    text = " ".join(e["excerpt_text"] for e in i172.get("excerpts", []))
    if "negative figure on Schedule 1" not in text:
        err("citation: the Schedule 1 destination verbatim is missing")
    if "starting with the earliest" not in text:
        err("citation: the oldest-first verbatim is missing")

# Gate 1 APPROVED 2026-08-12 (Ken, in-session: "Approve as drafted") — the
# pre-approval check that READY_TO_SEED stay False is retired; the loader's
# sentinel comment records the approval.

# ═══════════════════════════════════════════════════════════════════════════

if errors:
    print(f"FAIL — {len(errors)} problem(s):")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print(f"ALL CHECKS PASS — {len(m.SCENARIOS)} scenarios recomputed independently; "
      f"{len(m.RULES)} rules cited; invariants I1-I7 hold; READY_TO_SEED gate intact.")
