"""Throwaway-SQLite validation for CO_DR0112 (TY2025).

⚠ NEVER touches `test_postgres` - RS and delvio-tax share that database name, and
the runner destroys and recreates it. This harness builds a private SQLite file.

The checks that matter are PROVED, not asserted - each shows the wrong answer
DIFFERS, which is the only way a reader can tell the rule was necessary:
  * the 80% NOL limit on line 16(b) vs line 15 - the wrong base is IMPOSSIBLE,
    not merely different (it can produce a deduction larger than the income)
  * the two $5,000 predicates disagree at exactly $5,000
  * a December 52-53 week year takes the FOLLOWING year's rate
  * 80%-or-more foreign property/payroll excludes even a 6-of-6 unitary member
  * the line-17 cap is TY2025-only - TY2026 uncaps it
  * Colorado NOL vintages are NOT federal
  * an ABSENCE check on CODE: the "prior to 1965" Guide gloss is not encoded

⚠⚠ THE TWO-WRITERS GUARD HERE IS HARDENED relative to the MO/VA/AZ versions.
Those scan `load_*.py` for a DOUBLE-QUOTED `"source_code":`. The shared module
`_state_conformity_tier1.py` matches NEITHER - it is not `load_*` and it uses
SINGLE quotes - so it is invisible to the old guard, and it owns CO_CRS_39_22_103
among others. This version scans every .py in the commands directory and both
quote styles.

Run:  .venv/Scripts/python.exe scratchpad/validate_co_dr0112.py
"""
import io as io2
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

PROJECT_ROOT = r"D:\dev\delvio-rule-studio"
sys.path.insert(0, PROJECT_ROOT)

SQLITE_PATH = os.path.join(PROJECT_ROOT, "scratchpad", "validate_co_dr0112.sqlite3")
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
from sources.models import AuthoritySource, AuthorityTopic  # noqa: E402
from specs.management.commands import load_co_dr0112 as CO  # noqa: E402

FAILURES: list[str] = []
PASSES: list[str] = []
COMMANDS_DIR = os.path.join(PROJECT_ROOT, "specs", "management", "commands")


def check(cond, ok, bad):
    (PASSES if cond else FAILURES).append(ok if cond else bad)


def approx(a, b, tol=0.005):
    return a is not None and abs(float(a) - float(b)) <= tol


def declares_source(text: str, code: str) -> bool:
    """⚠ Both quote styles. `_state_conformity_tier1.py` uses single quotes."""
    return bool(re.search(r"""['"]source_code['"]\s*:\s*['"]%s['"]""" % re.escape(code), text))


call_command("migrate", run_syncdb=True, verbosity=0)

# ⚠ PREREQUISITES: CO_DR0112 REFERENCES seven AuthoritySource rows owned by other
# loaders - the shared conformity module owns CO_CRS_39_22_103, the seeded DR 0106
# loader owns the rest. Seed both owners first so this harness proves the
# references RESOLVE, not merely that they are spelled plausibly.
call_command("load_state_conformity", verbosity=0)
call_command("load_co_dr0106", verbosity=0)

# ======================================================================
# 0. THE SEED GUARD - pinned to the GATE MECHANISM, not the sentinel value
# ======================================================================
check(CO.READY_TO_SEED is False, "READY_TO_SEED ships as False (D-27 approved SCOPE, not the seed gate)",
      f"⚠⚠ READY_TO_SEED SHIPPED AS {CO.READY_TO_SEED!r} - would seed without Ken's gate")

CO.READY_TO_SEED = False
try:
    call_command("load_co_dr0112", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: seeded while READY_TO_SEED was False")
except CommandError as exc:
    msg = " ".join(str(exc).split())
    check("not cleared to seed" in msg, "the seed guard REFUSES when the sentinel is down",
          f"unexpected guard message: {msg[:150]!r}")
    check("relayed approval never opens a human gate" in msg,
          "the guard states the gate rule", "the guard omits the gate rule")

CO.READY_TO_SEED = True
_saved = CO.FLOW_ASSERTIONS
CO.FLOW_ASSERTIONS = []
try:
    call_command("load_co_dr0112", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: seeded a hollow spec")
except CommandError:
    PASSES.append("the seed guard ALSO refuses a hollow spec, sentinel up")
CO.FLOW_ASSERTIONS = _saved

try:
    call_command("load_co_dr0112", verbosity=0)
    PASSES.append("load_co_dr0112 ran + seeded into throwaway SQLite")
except Exception as exc:  # noqa: BLE001
    FAILURES.append(f"load_co_dr0112 raised: {exc!r}")

# ======================================================================
# 1. CharField caps from the REAL model fields (D-17 - Postgres-only failures)
# ======================================================================
for model, field, values in (
    (FormRule, "rule_id", [r["rule_id"] for r in CO.F_RULES]),
    (FormRule, "title", [r["title"] for r in CO.F_RULES]),
    (FormLine, "line_number", [l["line_number"] for l in CO.F_LINES]),
    (FlowAssertion, "assertion_id", [a["assertion_id"] for a in CO.FLOW_ASSERTIONS]),
    (FlowAssertion, "title", [a["title"] for a in CO.FLOW_ASSERTIONS]),
    (FormDiagnostic, "diagnostic_id", [d["diagnostic_id"] for d in CO.F_DIAGNOSTICS]),
    (FormDiagnostic, "title", [d["title"] for d in CO.F_DIAGNOSTICS]),
    (FormFact, "fact_key", [f["fact_key"] for f in CO.F_FACTS]),
    (FormFact, "label", [f["label"] for f in CO.F_FACTS]),
    (TestScenario, "scenario_name", [s["scenario_name"] for s in CO.F_SCENARIOS]),
    (AuthorityTopic, "topic_name", [n for _c, n in CO.AUTHORITY_TOPICS]),
    (AuthoritySource, "source_code", [s["source_code"] for s in CO.AUTHORITY_SOURCES]),
    (AuthoritySource, "citation", [s.get("citation") or "" for s in CO.AUTHORITY_SOURCES]),
    (AuthoritySource, "title", [s["title"] for s in CO.AUTHORITY_SOURCES]),
    (TaxForm, "form_title", [f["identity"]["form_title"] for f in CO.FORMS]),
):
    limit = model._meta.get_field(field).max_length
    if limit is None:
        PASSES.append(f"{model.__name__}.{field}: unbounded (TextField)")
        continue
    over = [(v[:40], len(v)) for v in values if v and len(v) > limit]
    check(not over, f"{model.__name__}.{field}: all within the real cap ({limit})",
          f"{model.__name__}.{field} OVERFLOWS {limit} (Postgres-only failure): {over}")

# ======================================================================
# 2. Structure, dangling references, and the HARDENED two-writers guard
# ======================================================================
form = TaxForm.objects.filter(form_number="CO_DR0112").first()
check(form is not None, "CO_DR0112 exists", "CO_DR0112 was not created")
if form:
    check(form.jurisdiction == "CO" and form.tax_year == 2025, "identity: CO / TY2025", "identity wrong")
    check(form.entity_types == ["1120"], "entity_types == ['1120']", f"wrong: {form.entity_types}")

for label, values in (("rule_id", [r["rule_id"] for r in CO.F_RULES]),
                      ("line_number", [l["line_number"] for l in CO.F_LINES]),
                      ("fact_key", [f["fact_key"] for f in CO.F_FACTS]),
                      ("diagnostic_id", [d["diagnostic_id"] for d in CO.F_DIAGNOSTICS]),
                      ("scenario_name", [s["scenario_name"] for s in CO.F_SCENARIOS])):
    dupes = {v for v in values if values.count(v) > 1}
    check(not dupes, f"no duplicate {label}", f"duplicate {label}: {sorted(dupes)}")

_declared = {r["rule_id"] for r in CO.F_RULES}
_cited = {rl[0] for rl in CO.F_RULE_LINKS}
check(not sorted(_declared - _cited), "every FormRule carries at least one authority link",
      f"uncitable rules: {sorted(_declared - _cited)}")
check(not sorted(_cited - _declared), "every authority link names a declared rule",
      f"⚠ DANGLING RULE REFERENCE: {sorted(_cited - _declared)}")

_universe = {s["source_code"] for s in CO.AUTHORITY_SOURCES} | set(CO.EXISTING_SOURCES_TO_REFERENCE)
check(not ({rl[1] for rl in CO.F_RULE_LINKS} - _universe),
      "every rule link resolves to a declared or referenced source",
      f"⚠ DANGLING SOURCE: {sorted({rl[1] for rl in CO.F_RULE_LINKS} - _universe)}")
check(not ({fl[0] for fl in CO.AUTHORITY_FORM_LINKS} - _universe),
      "every AUTHORITY_FORM_LINK resolves",
      f"⚠ DANGLING SOURCE in form links: {sorted({fl[0] for fl in CO.AUTHORITY_FORM_LINKS} - _universe)}")

# ⚠⚠ HARDENED TWO-WRITERS GUARD - every .py in the commands dir, both quote styles.
_declared_here = {s["source_code"] for s in CO.AUTHORITY_SOURCES}
_all_modules = [p for p in os.listdir(COMMANDS_DIR)
                if p.endswith(".py") and p != "load_co_dr0112.py"]
_clashes, _owners = [], {}
for _name in _all_modules:
    _text = io2.open(os.path.join(COMMANDS_DIR, _name), encoding="utf-8").read()
    for _code in _declared_here:
        if declares_source(_text, _code):
            _clashes.append((_code, _name))
    for _code in CO.EXISTING_SOURCES_TO_REFERENCE:
        if declares_source(_text, _code):
            _owners.setdefault(_code, []).append(_name)
check(not _clashes,
      "⚠⚠ TWO-WRITERS GUARD (hardened): no source declared here is declared by any other module",
      f"TWO WRITERS OF ONE ROW - would OVERWRITE a source another module owns: {_clashes}")

_orphans = [c for c in CO.EXISTING_SOURCES_TO_REFERENCE if c not in _owners]
check(not _orphans,
      "every EXISTING_SOURCES_TO_REFERENCE code is genuinely owned by another module",
      f"⚠ referenced but owned by NOTHING (a dangling reference on a clean database): {_orphans}")
_multi = {c: m for c, m in _owners.items() if len(m) > 1}
check(not _multi, "no referenced source has two owners",
      f"⚠ DUPLICATE OWNERSHIP - two modules declare the same row: {_multi}")

# ⚠ Prove the hardening was necessary: the OLD guard's pattern misses the module
# that actually owns CO_CRS_39_22_103.
_conf = io2.open(os.path.join(COMMANDS_DIR, "_state_conformity_tier1.py"), encoding="utf-8").read()
_old_pattern_hit = '"source_code": "CO_CRS_39_22_103"' in _conf
check(declares_source(_conf, "CO_CRS_39_22_103") and not _old_pattern_hit,
      "⚠⚠ PROVED the hardening was needed: `_state_conformity_tier1.py` DOES own "
      "CO_CRS_39_22_103, and the older double-quote/load_*.py guard cannot see it",
      "the conformity module no longer matches the expectation this hardening was built for - "
      "re-check whether the old guard is now sufficient")

# ======================================================================
# 3. ⚠ THE 80% NOL LIMIT - the wrong base is IMPOSSIBLE, not merely different
# ======================================================================
_nol = CO._co_nol_deduction(1000000, 400000, 900000)
check(approx(_nol["16a"], 400000) and approx(_nol["16b"], 600000)
      and approx(_nol["16c"], 480000) and approx(_nol["16d"], 880000),
      "16(a)=400k, 16(b)=600k, 16(c)=80% of 16(b)=480k, 16(d)=880k", f"got {_nol}")
_wrong_c = min(900000, 1000000 * 0.80)          # 80% applied to line 15 instead
_wrong_d = 400000 + _wrong_c
check(_wrong_d > 1000000,
      "⚠ PROVED: applying 80%% to line 15 gives a deduction of %.0f against income of 1,000,000 - "
      "LARGER than the income it offsets. The wrong base is not merely different, it is "
      "impossible, which is exactly why line 16(b) is printed as its own line." % _wrong_d,
      "the wrong base does not overshoot here - pick a fixture with larger pre-2018 losses")
check(approx(CO._yk(CO.CO_NOL_80PCT_LIMIT), 0.80), "the 80% limitation constant is present",
      "the 80% limitation is missing")

# NOL vintages - Colorado is NOT federal.
check(CO._co_nol_carryforward_years(2017) == 20, "pre-2018 losses carry forward 20 years", "wrong")
check(CO._co_nol_carryforward_years(2019) is None,
      "2018-2020 losses carry forward WITHOUT LIMIT", "wrong")
check(CO._co_nol_carryforward_years(2021) == 20,
      "⚠ 2021-onward losses revert to TWENTY years - a Colorado-only rule; federal post-2017 "
      "NOLs are indefinite, so a federal assumption over-states every such carryforward", "wrong")
check(CO._co_nol_carryforward_years(2015, is_financial_institution=True) == 15,
      "⚠ an IRC § 585/§ 593 financial institution gets FIFTEEN years for a 2015 loss - the rule "
      "the Guide's carryforward table OMITS", "wrong")
check(CO._co_nol_carryforward_years(2015, is_financial_institution=True)
      < CO._co_nol_carryforward_years(2015),
      "⚠ PROVED: a preparer working from the Guide's table would over-state a financial "
      "institution's carryforward by five years",
      "the financial-institution rule does not shorten the period here")
check(CO._yk(CO.CO_NOL_CARRYBACK_YEARS) == 0,
      "no Colorado NOL carryback in any year (§ 39-22-504(3)(b))", "a carryback is encoded")

# ======================================================================
# 4. ⚠⚠ THE TWO $5,000 PREDICATES DISAGREE AT EXACTLY $5,000
# ======================================================================
check(CO._co_must_remit_estimates(5001) is True, "obligation arises above $5,000", "wrong")
check(CO._co_must_remit_estimates(5000) is False,
      "⚠ at exactly $5,000 there is NO obligation to remit ('greater than')", "wrong")
check(CO._co_penalty_exception_applies(4999) is True, "the penalty exception applies below $5,000", "wrong")
check(CO._co_penalty_exception_applies(5000) is False,
      "⚠ at exactly $5,000 the penalty exception does NOT apply ('less than', § 39-22-606(6)(a)(I))",
      "wrong")
check(CO._co_must_remit_estimates(5000) is False and CO._co_penalty_exception_applies(5000) is False,
      "⚠⚠ D-18 PROVED: at exactly $5,000 the taxpayer owed no estimates AND has no penalty "
      "exception - a single shared predicate is wrong at precisely this point, and it is a round "
      "number taxpayers land on",
      "the two predicates agree at $5,000 - then D-18's correction would be vacuous")
check(CO.CO_ESTIMATED_OBLIGATION_THRESHOLD is not CO.CO_ESTIMATED_PENALTY_EXCEPTION_THRESHOLD,
      "the two thresholds are separate constants, so a future year can move one without the other",
      "the two thresholds are the same object - a change to one would silently change both")

# ======================================================================
# 5. ⚠ W9 - THE 52-53 WEEK RATE TRAP
# ======================================================================
_rate_deemed = CO._co_tax(2000000, CO._co_rate_year_from_deemed_commencement(2024))
_rate_calendar = CO._co_tax(2000000, 2023)
check(approx(_rate_deemed, 85000.0), "a year DEEMED to commence 2024-01-01 uses 4.25%", f"got {_rate_deemed}")
check(approx(_rate_calendar, 88000.0), "the calendar-start year 2023 would use 4.4%", f"got {_rate_calendar}")
check(abs(_rate_deemed - _rate_calendar) > 0.0,
      "⚠ W9 PROVED: a December-starting 52-53 week year takes the FOLLOWING year's rate - $%.0f "
      "difference on 2,000,000 of Colorado taxable income, and the wrong rate looks entirely "
      "plausible on the printed return" % abs(_rate_deemed - _rate_calendar),
      "the deemed and calendar rate years agree - pick a boundary where the rate moved")
check(2027 not in CO.CO_CCORP_RATE and 2028 not in CO.CO_CCORP_RATE,
      "⚠ TY2027/28 rates are ABSENT - LCS projections (4.33%/4.29%) are not enacted rates and this "
      "campaign does not fill gaps with plausible figures",
      "⚠ a PROJECTED rate has been encoded as if enacted")
try:
    CO._co_tax(1000, 2027)
    FAILURES.append("⚠ TY2027 computed a tax from a projection instead of refusing")
except CommandError as exc:
    check("projection is not an enacted rate" in str(exc),
          "TY2027 REFUSES and says why", f"unexpected TY2027 message: {str(exc)[:120]!r}")

# ======================================================================
# 6. ⚠ P.L. 86-272 and the line-17 cap
# ======================================================================
_tax = CO._co_tax(1950000)
check(approx(CO._co_line19_with_pl86272(_tax, True), 0.0),
      "P.L. 86-272 zeroes line 19", "line 19 was not zeroed")
check(approx(CO._co_line19_with_pl86272(_tax, False), 85800.0),
      "without P.L. 86-272 the computed tax stands (85,800)", f"got {CO._co_line19_with_pl86272(_tax, False)}")

_l17_25 = CO._co_line17_hb21_1002(400000, 2025)
_l17_26 = CO._co_line17_hb21_1002(400000, 2026)
check(approx(_l17_25, 150000.0), "line 17 is capped at $150,000 for TY2025", f"got {_l17_25}")
check(approx(_l17_26, 400000.0), "⚠ the cap is REMOVED for TY2026 (§ 39-22-304(3)(p)(II)(B))",
      f"got {_l17_26}")
check(abs(_l17_26 - _l17_25) > 0.0,
      "⚠⚠ PROVED: carrying the TY2025 cap into TY2026 would under-claim this subtraction by "
      "$%.0f - the fourth cliff item, added by the verification pass" % (_l17_26 - _l17_25),
      "the cap makes no difference across the boundary")
check(len(CO.CO_TY2026_REAUTHORING_CHANGES) == 4,
      "⚠⚠ the TY2026 cliff is recorded as FOUR changes, not three",
      f"the cliff records {len(CO.CO_TY2026_REAUTHORING_CHANGES)} changes - D-27 ruled four")

# ======================================================================
# 7. ⚠⚠ COMBINED INCLUSION - all three conditions, and the 80% edge
# ======================================================================
check(CO._co_combined_inclusion_required(True, 0.10, 3) is True,
      "included: affiliated, 10% foreign, three tests met", "wrong")
check(CO._co_combined_inclusion_required(True, 0.80, 6) is False,
      "⚠ EXCLUDED at exactly 80% foreign even with SIX of six tests met - § 39-22-303(8)(a) "
      "excludes at 'eighty percent OR MORE', so inclusion needs strictly less", "wrong")
check(CO._co_combined_inclusion_required(True, 0.7999, 6) is True,
      "⚠ PROVED the boundary bites: the same corporation at 79.99% IS included", "wrong")
check(CO._co_combined_inclusion_required(True, 0.10, 2) is False,
      "not included on two of six tests", "wrong")
check(CO._co_combined_inclusion_required(False, 0.10, 6) is False,
      "not included when not an affiliated-group member", "wrong")
check(CO.CO_UNITY_TESTS_REQUIRED == 3 and CO.CO_UNITY_TESTS_TOTAL == 6
      and CO.CO_UNITY_LOOKBACK_YEARS == 2,
      "three of six, over the current and two preceding years", "the unity constants are wrong")
check(CO.CO_PARTNERSHIP_LOOKTHROUGH_TESTS == (1, 2, 3, 4),
      "⚠ the partnership look-through reaches tests 1-4 ONLY - a uniform look-through is the "
      "natural wrong assumption", "the look-through scope is wrong")
check("fifty states" in CO.CO_US_DEFINITION,
      "⚠ 'United States' is the fifty states and DC - territories count toward the 80%",
      "the US definition is not recorded")

# ======================================================================
# 8. ⚠⚠ W5 - THE DEPRECIATION RULING IS AFFIRMATIVE, AND THE 1965 GLOSS IS NOT ENCODED
# ======================================================================
check(CO.CO_DEPRECIATION_MODIFICATION_EXISTS is False,
      "no Colorado depreciation modification", "a modification is encoded")
check("39-22-304(3)(p)(III)" in CO.CO_DEPRECIATION_RULING_AUTHORITY,
      "⚠⚠ the depreciation negative carries its CITATION - an affirmative ruling, not an absence",
      "the depreciation negative has no authority recorded, which is the class-(b) defect itself")
check(CO.CO_304_3C_HAS_1965_CUTOFF_IN_STATUTE is False,
      "the 1965 cut-off is recorded as absent from the statute", "wrong")

# ⚠ ABSENCE CHECK ON CODE, not prose: 1965 must appear nowhere as a numeric literal,
# and the check must not be able to pass by being empty.
_src = io2.open(os.path.join(COMMANDS_DIR, "load_co_dr0112.py"), encoding="utf-8").read()
_numeric_1965 = re.search(r"(?<![\d,'\"])1965(?![\d])\s*[,)\]]", _src)
check(_numeric_1965 is None,
      "⚠⚠ ABSENCE CHECK (code, not prose): 1965 appears in NO numeric position - it is a Guide "
      "gloss the statute does not carry",
      f"⚠ 1965 is encoded as a value: {_numeric_1965.group(0) if _numeric_1965 else ''!r}")
check("1965" in _src,
      "...and the check cannot pass by being empty - 1965 IS discussed in prose, as a gloss to reject",
      "1965 is not mentioned at all, so a future reader will not know it was considered and rejected")

# ======================================================================
# 9. The deferrals and the diagnostics each NAME what they refuse
# ======================================================================
_diag_ids = {d["diagnostic_id"] for d in CO.F_DIAGNOSTICS}
for _need, _why in (("D_CO0112_TY2026_REAUTHOR", "the TY2026 re-authoring cliff"),
                    ("D_CO0112_UNITY_TEST_WORDING", "C2 the three-way test divergence"),
                    ("D_CO0112_UNITY_LOOKBACK", "the current + two preceding years"),
                    ("D_CO0112_US_DEFINITION", "the fifty-states definition"),
                    ("D_CO0112_COMBINED_NOT_AN_ENTITY", "combined-group-as-taxpayer is TY2026-only"),
                    ("D_CO0112_SCHEDULE_C_TRIGGER", "§ 303(12) membership, not the Section B box"),
                    ("D_CO0112_NOL_LIMITS_DEFERRED", "C3 the deferred NOL limitations"),
                    ("D_CO0112_NOL_FINANCIAL_INSTITUTION", "the 15-year financial-institution rule"),
                    ("D_CO0112_RATE_52_53_WEEK", "W9 the deemed commencement date"),
                    ("D_CO0112_EST_TWO_PREDICATES", "the two $5,000 predicates"),
                    ("D_CO0112_NO_PAYMENT_EXTENSION", "filing extension is not a payment extension"),
                    ("D_CO0112_WRITEIN_STATUTORY_LIST", "W4 the statutory write-in lists"),
                    ("D_CO0112_FOREIGN_SOURCE_RF", "C5 the RF denominator propagation"),
                    ("D_CO0112_AMENDED_DEFERRED", "W12 DR 0112X with the Box-H trigger built")):
    check(_need in _diag_ids, f"diagnostic present for {_why}", f"MISSING diagnostic for {_why}")

for _d in CO.F_DIAGNOSTICS:
    if _d["severity"] == "error":
        check(len(_d["message"]) > 200,
              f"{_d['diagnostic_id']}: the refusal explains itself at length",
              f"{_d['diagnostic_id']}: a hard stop with a {len(_d['message'])}-char message - a "
              "refusal that does not name what it refuses is a dead end for the preparer")

_unity = next(d for d in CO.F_DIAGNOSTICS if d["diagnostic_id"] == "D_CO0112_UNITY_TEST_WORDING")
for _phrase in ("gross receipts", "total annual value", "BOTH directions"):
    check(_phrase in _unity["message"],
          f"the unity diagnostic names the '{_phrase}' divergence",
          f"the unity diagnostic omits '{_phrase}' - it must show the preparer WHERE the texts part")

check(len(CO.CO_DEFERRED_ITEMS) >= 7,
      f"{len(CO.CO_DEFERRED_ITEMS)} deferrals each NAME what they refuse",
      "the deferral list is short - each refusal must name itself")

# ======================================================================
# 10. Due date and persisted-row counts
# ======================================================================
check(CO._yk(CO.CO_RETURN_DUE_MONTH) == 5 and CO._yk(CO.CO_RETURN_DUE_DAY) == 15,
      "⚠ due the fifteenth day of the FIFTH month (§ 39-22-608(2)(b), HB 23-1277) - a "
      "fourth-month assumption would be a month early and look like an on-time filing",
      "the due date is not the fifth-month rule")
check(CO.CO_EXTENSION_IS_PAYMENT_EXTENSION is False,
      "the six-month extension is to FILE, never to PAY", "the extension is modelled as a payment extension")

if form:
    for _model, _decl, _label in ((FormFact, CO.F_FACTS, "facts"),
                                  (FormRule, CO.F_RULES, "rules"),
                                  (FormLine, CO.F_LINES, "lines"),
                                  (FormDiagnostic, CO.F_DIAGNOSTICS, "diagnostics"),
                                  (TestScenario, CO.F_SCENARIOS, "scenarios")):
        _n = _model.objects.filter(tax_form=form).count()
        check(_n == len(_decl), f"{_label}: {_n} rows persisted == {len(_decl)} declared",
              f"{_label}: {_n} persisted but {len(_decl)} declared")

_fa_ids = [a["assertion_id"] for a in CO.FLOW_ASSERTIONS]
_fa_n = FlowAssertion.objects.filter(assertion_id__in=_fa_ids).count()
check(_fa_n == len(_fa_ids), f"flow assertions: {_fa_n} of this spec's {len(_fa_ids)} persisted",
      f"flow assertions: {_fa_n} persisted but {len(_fa_ids)} declared")

# ======================================================================
print("\n" + "=" * 74)
for p in PASSES:
    print(f"  PASS  {p}")
if FAILURES:
    print("\n" + "!" * 74)
    for f in FAILURES:
        print(f"  FAIL  {f}")
print("=" * 74)
print(f"CO_DR0112 harness: {len(PASSES)} pass / {len(FAILURES)} fail")
print("=" * 74)
sys.exit(1 if FAILURES else 0)
