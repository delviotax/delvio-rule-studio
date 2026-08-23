"""Throwaway-SQLite validation for VA_500 - Virginia Corporation Income Tax Return (TY2025).

⚠ NEVER touches `test_postgres` - RS and delvio-tax share that database name.

Checks:
  0. The seed guard, pinned to the GATE MECHANISM (D-17), never the disk value.
  1. CharField caps from the REAL model fields (Postgres enforces; SQLite does not).
  2. Structural integrity.
  3. ARITHMETIC ORACLES - the Sec. 58.1-408 A weight-sum divisor in all four
     cases, INCLUDING the two that knowingly diverge from the printed forms.
  4. ⚠⚠ THE LINE 11 OVERWRITE - proved by showing the derived-only answer is
     observably different, not merely by asserting the override path exists.
  5. Ken's D-21 rulings are ENCODED - including an ABSENCE check: no Virginia
     Sec. 179 figure may appear anywhere.

Run:  .venv/Scripts/python.exe scratchpad/validate_va_500.py
"""
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

PROJECT_ROOT = r"D:\dev\delvio-rule-studio"
sys.path.insert(0, PROJECT_ROOT)

SQLITE_PATH = os.path.join(PROJECT_ROOT, "scratchpad", "validate_va_500.sqlite3")
if os.path.exists(SQLITE_PATH):
    os.remove(SQLITE_PATH)
os.environ["DATABASE_URL"] = f"sqlite:///{SQLITE_PATH}"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

import django  # noqa: E402
django.setup()

from django.core.management import call_command  # noqa: E402
from django.core.management.base import CommandError  # noqa: E402
from specs.models import (  # noqa: E402
    FlowAssertion, FormDiagnostic, FormFact, FormLine, FormRule, TaxForm, TestScenario,
)
from sources.models import AuthoritySource, AuthorityTopic, RuleAuthorityLink  # noqa: E402
from specs.management.commands import load_va_500 as VA  # noqa: E402

FAILURES: list[str] = []
PASSES: list[str] = []


def check(cond, ok, bad):
    (PASSES if cond else FAILURES).append(ok if cond else bad)


def approx(a, b, tol=0.0000005):
    return a is not None and abs(float(a) - float(b)) <= tol


call_command("migrate", run_syncdb=True, verbosity=0)

# ======================================================================
# 0. THE SEED GUARD
# ======================================================================
_shipped = VA.READY_TO_SEED

VA.READY_TO_SEED = False
try:
    call_command("load_va_500", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: seeded while READY_TO_SEED was False")
except CommandError as exc:
    msg = " ".join(str(exc).split())
    check("not cleared to seed" in msg, "the seed guard REFUSES when the sentinel is down",
          f"unexpected guard message: {msg[:150]!r}")
    check("relayed approval never opens a human gate" in msg,
          "the guard states the gate rule", "the guard omits the gate rule")

VA.READY_TO_SEED = True
_saved = VA.FLOW_ASSERTIONS
VA.FLOW_ASSERTIONS = []
try:
    call_command("load_va_500", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: seeded a hollow spec")
except CommandError:
    PASSES.append("the seed guard ALSO refuses a hollow spec, sentinel up")
VA.FLOW_ASSERTIONS = _saved

try:
    call_command("load_va_500", verbosity=0)
    PASSES.append("load_va_500 ran + seeded into throwaway SQLite without error")
except Exception as exc:  # noqa: BLE001
    FAILURES.append(f"load_va_500 raised: {exc!r}")

# ======================================================================
# 1. CharField caps from the REAL model fields
# ======================================================================
for model, field, values in (
    (FormRule, "rule_id", [r["rule_id"] for r in VA.F_RULES]),
    (FormRule, "title", [r["title"] for r in VA.F_RULES]),
    (FormLine, "line_number", [l["line_number"] for l in VA.F_LINES]),
    (FlowAssertion, "assertion_id", [a["assertion_id"] for a in VA.FLOW_ASSERTIONS]),
    (FlowAssertion, "title", [a["title"] for a in VA.FLOW_ASSERTIONS]),
    (FormDiagnostic, "diagnostic_id", [d["diagnostic_id"] for d in VA.F_DIAGNOSTICS]),
    (FormDiagnostic, "title", [d["title"] for d in VA.F_DIAGNOSTICS]),
    (FormFact, "fact_key", [f["fact_key"] for f in VA.F_FACTS]),
    (FormFact, "label", [f["label"] for f in VA.F_FACTS]),
    (TestScenario, "scenario_name", [s["scenario_name"] for s in VA.F_SCENARIOS]),
    (AuthorityTopic, "topic_name", [n for _c, n in VA.AUTHORITY_TOPICS]),
    (AuthoritySource, "source_code", [s["source_code"] for s in VA.AUTHORITY_SOURCES]),
    (AuthoritySource, "citation", [s.get("citation") or "" for s in VA.AUTHORITY_SOURCES]),
    (TaxForm, "form_title", [f["identity"]["form_title"] for f in VA.FORMS]),
):
    limit = model._meta.get_field(field).max_length
    if limit is None:
        PASSES.append(f"{model.__name__}.{field}: unbounded (TextField)")
        continue
    over = [(v[:40], len(v)) for v in values if v and len(v) > limit]
    check(not over, f"{model.__name__}.{field}: all within the real cap ({limit})",
          f"{model.__name__}.{field} OVERFLOWS {limit} (Postgres-only failure): {over}")

# ======================================================================
# 2. Structural integrity
# ======================================================================
form = TaxForm.objects.filter(form_number="VA_500").first()
check(form is not None, "VA_500 exists", "VA_500 was not created")
if form:
    check(form.jurisdiction == "VA" and form.tax_year == 2025 and form.version == 1,
          "identity: VA / TY2025 / v1", "identity wrong")
    check(form.entity_types == ["1120"], "entity_types == ['1120']", f"entity_types wrong: {form.entity_types}")

for label, values in (("rule_id", [r["rule_id"] for r in VA.F_RULES]),
                      ("line_number", [l["line_number"] for l in VA.F_LINES]),
                      ("fact_key", [f["fact_key"] for f in VA.F_FACTS]),
                      ("diagnostic_id", [d["diagnostic_id"] for d in VA.F_DIAGNOSTICS]),
                      ("assertion_id", [a["assertion_id"] for a in VA.FLOW_ASSERTIONS])):
    dupes = {v for v in values if values.count(v) > 1}
    check(not dupes, f"no duplicate {label}", f"duplicate {label}: {sorted(dupes)}")

_declared = {r["rule_id"] for r in VA.F_RULES}
_srcs = {s["source_code"] for s in VA.AUTHORITY_SOURCES} | set(VA.EXISTING_SOURCES_TO_REFERENCE)
check(not [rl for rl in VA.F_RULE_LINKS if rl[0] not in _declared],
      "every rule_link points at a declared rule", "rule_links reference undefined rules")
check(not [rl for rl in VA.F_RULE_LINKS if rl[1] not in _srcs],
      "every rule_link points at a declared source", "rule_links reference undeclared sources")
check(not sorted(_declared - {rl[0] for rl in VA.F_RULE_LINKS}),
      "every FormRule carries at least one authority link",
      f"uncitable rules: {sorted(_declared - {rl[0] for rl in VA.F_RULE_LINKS})}")

# ======================================================================
# 3. THE Sec. 58.1-408 A WEIGHT-SUM DIVISOR - all four cases
# ======================================================================
_ONE = (100.0, 100.0)
_NONE = (0, 0)

check(approx(VA._va500_apportionment_pct((200000, 1000000), (300000, 1000000), (400000, 2000000)), 0.225),
      "divisor 4: (0.20 + 0.30 + 2x0.20) / 4 = 0.225",
      "the all-three-factors case is wrong")
check(approx(VA._va500_apportionment_pct((200000, 1000000), (300000, 1000000), _NONE), 0.25),
      "⚠ sales MISSING -> divisor 2: 0.50 / 2 = 0.25 (statute; MORE tax than the printed forms)",
      "the sales-missing divisor is not 2")
check(approx(VA._va500_apportionment_pct((200000, 1000000), _NONE, (400000, 2000000)), 0.20),
      "⚠⚠ payroll MISSING -> divisor 3: (0.20 + 0.40) / 3 = 0.20 (statute; the 502 BOOK would give 0.30)",
      "the payroll-missing divisor is not 3")
check(approx(VA._va500_apportionment_pct(_NONE, (300000, 1000000), (400000, 2000000)), 0.2333333, tol=5e-7),
      "⚠ property MISSING -> divisor 3: (0.30 + 0.40) / 3 = 0.233333",
      "the property-missing divisor is not 3")
# The divergence the book would produce - proved observably different.
check(not approx(VA._va500_apportionment_pct((200000, 1000000), _NONE, (400000, 2000000)), 0.30),
      "⚠ the payroll-missing answer is NOT the Form 502 book's 0.30 - the book drops 'plus one'",
      "the spec reproduces the DEFECTIVE instruction-book divisor")
check(VA._va500_apportionment_pct(_NONE, _NONE, _NONE) is None,
      "no factor with a denominator -> None, never a substitute",
      "an all-empty apportionment produced a value")
check(VA._yk(VA.VA_APPORT_WEIGHTS) == {"property": 1, "payroll": 1, "sales": 2},
      "weights are property 1 / payroll 1 / sales 2 (sales double-weighted)",
      f"weights wrong: {VA.VA_APPORT_WEIGHTS}")

# ======================================================================
# 4. ⚠⚠ THE LINE 11 OVERWRITE - proved, not asserted
# ======================================================================
_derived = VA._va500_line11(line9=120000, line10=15000)
check(approx(_derived, 105000), "L11 derived normally = L9 - L10 = 105,000",
      f"the derived Line 11 is wrong: {_derived}")

_overwritten = VA._va500_line11(line9=120000, line10=15000, minimum_tax_override=250000)
check(approx(_overwritten, 250000),
      "⚠⚠ L11 with an SCC-certified regime = the MINIMUM TAX (250,000), REPLACING the computed amount",
      f"the Line 11 overwrite did not take effect: {_overwritten}")
check(not approx(_overwritten, _derived),
      "⚠⚠ the overwritten and derived answers are OBSERVABLY DIFFERENT (250,000 vs 105,000) - a "
      "derived-only Line 11 would under-tax a certified filer by 145,000 on a clean-looking return",
      "the overwrite is indistinguishable from the derived value - the whole guard is inert")
check(approx(VA._va500_line11(line9=50000, line10=90000), 0),
      "L11 floors at zero when credits exceed the tax",
      "L11 went negative")
check(approx(VA._va500_line11(line9=120000, line10=15000, minimum_tax_override=0), 0),
      "an explicit ZERO minimum tax still OVERWRITES - it is not treated as 'no override'",
      "a zero minimum tax was mistaken for an absent one, silently restoring the computed tax")

# ======================================================================
# 5. KEN'S D-21 RULINGS ARE ENCODED
# ======================================================================
_diag = {d["diagnostic_id"]: d for d in VA.F_DIAGNOSTICS}
_facts = {f["fact_key"]: f for f in VA.F_FACTS}
_text = " ".join([d["message"] + d["title"] + d.get("notes", "") for d in VA.F_DIAGNOSTICS]
                 + [r["description"] + r["title"] for r in VA.F_RULES]
                 + [a["description"] + a["title"] for a in VA.FLOW_ASSERTIONS])

# V2 - separate returns only, hard gate. W7 - preparer assertion. W11 - statute.
check("D_VA500_FILING_STATUS_GATE" in _diag
      and _diag["D_VA500_FILING_STATUS_GATE"]["severity"] == "error",
      "V2: combined/consolidated returns are refused by a HARD gate",
      "V2: no hard gate on filing status")
check("58.1-442 C" in _diag.get("D_VA500_FILING_STATUS_GATE", {}).get("message", ""),
      "W11: the gate cites the STATUTE Sec. 58.1-442 C, not the instruction book",
      "W11: the statute is not cited")
check("instruction book" in _diag.get("D_VA500_FILING_STATUS_GATE", {}).get("message", ""),
      "W11: the narrower instruction-book wording is recorded so nobody 'corrects' us to it",
      "W11: the instruction-book divergence is not recorded")
check("filing_status" in _facts, "W7: filing status is an explicit preparer-asserted FACT",
      "W7: filing status is not an explicit fact")

# V5 - Sec. 58.1-408 B.
check("D_VA500_408B_DEFERRED" in _diag and _diag["D_VA500_408B_DEFERRED"]["severity"] == "error",
      "V5: the Sec. 58.1-408 B numerator reduction is RED-deferred",
      "V5: no hard diagnostic for Sec. 58.1-408 B")
_v5 = _diag.get("D_VA500_408B_DEFERRED", {}).get("message", "")
check("six subsequent" in _v5 and "2019-2024" in _v5,
      "V5: the seven-year window and the still-inside-it years are stated",
      "V5: the window is not stated")
check("NO line" in _v5 and "NO checkbox" in _v5,
      "V5: the total absence of form support is stated",
      "V5: the zero-form-support fact is not stated")

# V6 - the minimum-tax regimes.
check("D_VA500_MIN_TAX_DEFERRED" in _diag and _diag["D_VA500_MIN_TAX_DEFERRED"]["severity"] == "error",
      "V6: the four minimum-tax regimes are RED-deferred",
      "V6: no hard diagnostic for the minimum-tax regimes")
_v6 = _diag.get("D_VA500_MIN_TAX_DEFERRED", {}).get("message", "")
check("REPLACE" in _v6.upper() and "500EL" in _v6,
      "V6: the diagnostic states that the minimum tax REPLACES Line 11, quoting 500EL",
      "V6: the REPLACE behaviour is not stated")
check("NO RATE" in _v6.upper(),
      "V6: it records that Schedule 500EL carries NO rate - the SCC certifies the amount",
      "V6: the 500EL no-rate fact is missing")

# ⚠⚠ V3 - AN ABSENCE CHECK. No Virginia Sec. 179 figure may exist anywhere.
import io as _io  # noqa: E402
_srcfile = _io.open(
    os.path.join(PROJECT_ROOT, "specs", "management", "commands", "load_va_500.py"), encoding="utf-8").read()
_forbidden = ["1250000", "1,250,000", "3130000", "3,130,000", "31300", "31,300"]
_hits = []
for tok in _forbidden:
    for ln in _srcfile.split("\n"):
        _l = ln.strip()
        _asserting_absence = (_l.startswith("#") or "NEVER" in ln or "never" in ln
                              or "no derived" in ln.lower() or "must not" in ln.lower())
        if tok in ln and not _asserting_absence:
            _hits.append((tok, ln.strip()[:70]))
check(not _hits,
      "⚠⚠ V3: NO Virginia Sec. 179 figure is encoded anywhere - their absence is the ruling",
      f"V3 VIOLATED - a derived Sec. 179 figure appears as a Virginia constant: {_hits}")
check("D_VA500_DEPRECIATION_ENTRY" in _diag,
      "V3: depreciation is direct-entry with a diagnostic saying Virginia publishes no figure",
      "V3: no depreciation diagnostic")

# V4 - the shared dollar box.
check("D_VA500_CONFORMITY_BUCKET" in _diag
      and "SHARES A SINGLE DOLLAR BOX" in _diag["D_VA500_CONFORMITY_BUCKET"]["message"],
      "V4: the residual bucket sharing one dollar box with the bonus true-up is recorded",
      "V4: the shared dollar box is not recorded")

# The Allied-Signal ratchet, the S&L method fork, the code crosswalk.
check("D_VA500_ALLIED_SIGNAL" in _diag and "ONE-WAY" in _diag["D_VA500_ALLIED_SIGNAL"]["message"],
      "the Allied-Signal ONE-WAY ratchet is recorded on lines 8(c)/8(d)",
      "the one-way ratchet is not recorded")
check("D_VA500_CODE_CROSSWALK" in _diag
      and "SEVEN" in _diag["D_VA500_CODE_CROSSWALK"]["message"].upper(),
      "⚠ G4: the seven same-number-different-meaning codes are recorded",
      "the corporate/PTE code collision is not recorded")

# S&L bad debt - only one method touches Line 6.
check(approx(VA._va500_line6_sl_bad_debt(500000, "percentage_of_income"), 200000),
      "S&L percentage-of-income: Line 5 x 40% = 200,000",
      "the percentage-of-income calculation is wrong")
for _m in ("percentage_of_loans", "experience"):
    check(approx(VA._va500_line6_sl_bad_debt(500000, _m), 0),
          f"⚠ S&L {_m}: Line 6 stays ZERO - it routes through addition code 13 instead",
          f"S&L {_m} wrongly produced a Line 6 figure, double-counting the deduction")

# TY-keying.
try:
    VA._yk(VA.VA_CORP_RATE, 2026)
    FAILURES.append("_yk returned an unverified TY2026 rate")
except CommandError:
    PASSES.append("_yk REFUSES an unverified tax year")
check(VA._yk(VA.VA_CORP_RATE) == "0.06", "the corporate rate is 6% (Va. Code Sec. 58.1-400), TY-keyed",
      f"rate wrong: {VA.VA_CORP_RATE}")

# G4 namespacing.
check(all(l["line_number"].startswith("VA500-") for l in VA.F_LINES),
      "G4: every line is VA500-namespaced, transcribed from the Form 500 face",
      "G4 violation: a line number is not VA500-namespaced")

# Scenario coverage of what matters.
_names = " ".join(s["scenario_name"] for s in VA.F_SCENARIOS)
for needle, why in (("OVERWRITES", "the Line 11 overwrite"),
                    ("divisor drops to 2", "the sales-missing divergence"),
                    ("divisor is 3", "the payroll-missing divergence"),
                    ("refused", "the combined-return gate"),
                    ("experience", "the S&L method fork")):
    check(needle.lower() in _names.lower(), f"a scenario covers {why}", f"NO scenario covers {why}")

# ======================================================================
# 6. Report
# ======================================================================
print("\n" + "=" * 74)
if form:
    print(f"  VA_500: facts {FormFact.objects.filter(tax_form=form).count()} / "
          f"rules {FormRule.objects.filter(tax_form=form).count()} / "
          f"lines {FormLine.objects.filter(tax_form=form).count()} / "
          f"diag {FormDiagnostic.objects.filter(tax_form=form).count()} / "
          f"tests {TestScenario.objects.filter(tax_form=form).count()}")
print(f"  flow assertions: {FlowAssertion.objects.filter(assertion_id__startswith='FA-VA500').count()}")
print(f"  rule authority links: {RuleAuthorityLink.objects.count()}")
print("=" * 74)
for p in PASSES:
    print(f"  PASS  {p}")
for f in FAILURES:
    print(f"  FAIL  {f}")
print("=" * 74)
print(f"RESULT: {len(PASSES)} pass / {len(FAILURES)} fail - "
      f"{'ALL PASS' if not FAILURES else 'FAILURES PRESENT'}")
print(f"NOTE: READY_TO_SEED driven in memory only; on disk it ships {_shipped}.")
print("NOTE: throwaway SQLite only -- test_postgres was never touched.")

from django.db import connections  # noqa: E402
connections.close_all()
try:
    if os.path.exists(SQLITE_PATH):
        os.remove(SQLITE_PATH)
except OSError:
    pass
sys.exit(1 if FAILURES else 0)
