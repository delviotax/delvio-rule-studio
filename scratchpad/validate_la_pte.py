"""Validation harness for the Louisiana pass-through specs (IT-565 + CIT-620).

Runs the loader's own computation helpers against hand-derived vectors AND
asserts the spec's structural invariants WITHOUT seeding. The seed-gate check
is pinned to the GATE MECHANISM, never to the sentinel's current value (see
the note at that check).

Run: poetry run python scratchpad/validate_la_pte.py
"""
import io
import os
import sys
import importlib.util

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django  # noqa: E402

django.setup()

spec = importlib.util.spec_from_file_location(
    "la", os.path.join(REPO, "specs", "management", "commands", "load_la_pte.py"))
LA = importlib.util.module_from_spec(spec)
spec.loader.exec_module(LA)

_pass, _fail = 0, 0


def check(cond, ok, bad=""):
    global _pass, _fail
    if cond:
        _pass += 1
        print(f"  PASS  {ok}")
    else:
        _fail += 1
        print(f"  FAIL  {bad or ok}")


print("\n=== Louisiana pass-through spec validation ===\n")
print("-- Rates and the two-constant discipline --")
check(float(LA.LA_COMPOSITE_RATE[2025]) == 0.03, "composite rate 3% (R.S. 47:201.1(D)(1))")
check(float(LA.LA_PTE_ELECT_RATE[2025]) == 0.03, "electing-PTE rate 3% (R.S. 47:287.732.2(B))")
check(LA.LA_COMPOSITE_RATE is not LA.LA_PTE_ELECT_RATE,
      "the two 3% rates are SEPARATE constants (two authority chains)",
      "the two 3% rates were collapsed into one object")
check(float(LA.LA_CIT_RATE[2025]) == 0.055, "corporate rate 5.5% flat (R.S. 47:287.12)")

print("\n-- Composite (Schedule 6922, embedded in IT-565) --")
check(LA.la_composite_tax(500000) == 15000.0, "composite: 500,000 x 3% = 15,000")
check(LA.la_composite_tax(100000) == 3000.0, "composite: 100,000 x 3% = 3,000")

print("\n-- CIT-620 track 1: ELECTING PTE (Schedule H-1) --")
check(LA.la_electing_pte_tax(1000000) == 30000.0, "electing PTE: 1,000,000 x 3% = 30,000")

print("\n-- CIT-620 track 2: NON-ELECTING S CORP computed as a C CORP --")
excl = LA.la_scorp_exclusion(1000000, 600, 1000)
check(excl == 600000.0, "Line 1B: 1,000,000 x (600/1,000) = 600,000")
check(LA.la_corporate_tax(1000000 - excl) == 22000.0,
      "track 3 pin: taxable 400,000 x 5.5% = 22,000")
check(LA.la_scorp_exclusion(1000000, 0, 0) == 0.0,
      "Line 1B: zero-denominator guard returns 0, never divides by zero")
check(LA.la_scorp_exclusion(1000000, 1000, 1000) == 1000000.0,
      "Line 1B: all-resident shares exclude the whole LA net income")

print("\n-- CIT-620 track 3: ordinary C corporation --")
check(LA.la_corporate_tax(1000000) == 55000.0, "C corp: 1,000,000 x 5.5% = 55,000")

print("\n-- NOL: 72% cap, indefinite carryforward --")
check(LA.la_nol_utilization(1000000, 900000) == 720000.0,
      "NOL: min(72% x 1,000,000, 900,000) = 720,000 (cap binds)")
check(LA.la_nol_utilization(1000000, 500000) == 500000.0,
      "NOL: min(720,000, 500,000) = 500,000 (the cap does not create deduction)")
check(LA.la_nol_utilization(0, 500000) == 0.0, "NOL: no LA income -> no utilization")

print("\n-- Schedule F line 3f: $20,000 standard deduction --")
check(LA.la_corp_standard_deduction(1000000) == 20000.0, "3f capped at 20,000")
check(LA.la_corp_standard_deduction(12000) == 12000.0, "3f limited to the income it offsets")
check(LA.la_corp_standard_deduction(-5000) == 0.0, "3f floored at zero on a loss")

print("\n-- TY-keying: TY2026 must REFUSE, not silently extend (four-act cliff) --")
try:
    LA.la_corporate_tax(1000000, year=2026)
    check(False, "", "TY2026 silently computed -- the cliff guard did not fire")
except Exception as e:
    check("RE-AUTHORING" in str(e) or "TY-keyed" in str(e),
          "TY2026 refuses with the re-authoring message (Acts 5/6/11/382)",
          f"TY2026 raised the wrong error: {e}")

print("\n-- Structural invariants --")
codes = {f["identity"]["form_number"] for f in LA.FORMS}
check(codes == {"LA_IT565", "LA_CIT620"}, "two form codes: LA_IT565 + LA_CIT620")
check("LA_CIFT620" not in codes, "the STALE LA_CIFT620 code is not used (form renamed for TY2025)")
cit = next(f for f in LA.FORMS if f["identity"]["form_number"] == "LA_CIT620")
check(set(cit["identity"]["entity_types"]) == {"1120S", "1120"},
      "LA_CIT620 serves BOTH the 1120S module and the future 1120 module (D-16 A1)")
it565 = next(f for f in LA.FORMS if f["identity"]["form_number"] == "LA_IT565")
check(it565["identity"]["entity_types"] == ["1065"], "LA_IT565 serves the 1065 module")

all_text = repr(LA.FORMS).lower()
check("bonus_addback = none" in repr(LA.CIT620_RULES).lower()
      or "la_bonus_addback = none" in repr(LA.CIT620_RULES).lower(),
      "the NO-bonus-add-back rule is encoded explicitly (rule says no)")
check("r-90158" in all_text or "r_90158" in all_text or "R-90158" in repr(LA.FORMS),
      "Form R-90158 (unpublished, U1) is RED-deferred in the spec")

diag_ids = {d["diagnostic_id"] for f in LA.FORMS for d in f["diagnostics"]}
check("D_LAIT565_EFILE_MANDATE" in diag_ids,
      "the statutory composite e-file mandate is an ERROR diagnostic (D-16 A2)")
check("D_LACIT620_TY2026_CLIFF" in diag_ids, "the TY2026 four-act cliff is surfaced")
check("D_LACIT620_SCORP_EXCL_INPUTS" in diag_ids,
      "the Line 1B filed-and-paid numerator caveat is surfaced (W4)")
sev = {d["diagnostic_id"]: d["severity"] for f in LA.FORMS for d in f["diagnostics"]}
check(sev.get("D_LAIT565_EFILE_MANDATE") == "error", "e-file mandate is severity=error")
check(sev.get("D_LAIT565_R90158_DEFER") == "error", "R-90158 RED-defer is severity=error")

# ⚠ RE-PINNED 2026-08-22 TO THE MECHANISM, NOT THE VALUE (campaign standing
# rule, now its FIFTH occurrence): this check asserted READY_TO_SEED is False
# and went red the moment Ken approved the seed — a check describing the world
# BEFORE an approval always does. Check that the GATE WORKS, never what the
# gate currently holds.
_guard_src = io.open(os.path.join(
    REPO, "specs", "management", "commands", "load_la_pte.py"), encoding="utf-8").read()
check("if not READY_TO_SEED or empty:" in _guard_src,
      "the seed guard still REFUSES when the sentinel is False (mechanism intact)",
      "the seed guard's refusal path is gone -- the gate no longer exists")
check('a bonus ADD-BACK was invented' in _guard_src,
      "the guard still refuses a fabricated Louisiana bonus add-back (LA has none)",
      "the no-bonus-add-back refusal was removed from the guard")
check(isinstance(LA.READY_TO_SEED, bool),
      f"READY_TO_SEED is a real boolean sentinel (currently {LA.READY_TO_SEED})")

fa = {a["assertion_id"] for a in LA.FLOW_ASSERTIONS}
check("FA-LAIT565-NOTAX" in fa, "flow assertion pins the IT-565 as computing NO entity tax")
check("FA-LACIT620-XOR" in fa,
      "flow assertion pins election XOR S-corp exclusion")
check(len(LA.FLOW_ASSERTIONS) == 5, f"5 flow assertions (got {len(LA.FLOW_ASSERTIONS)})")

print("\n" + "=" * 70)
print(f"RESULT: {_pass} pass / {_fail} fail - {'ALL PASS' if not _fail else 'FAILURES PRESENT'}")
sys.exit(1 if _fail else 0)
