"""Throwaway-SQLite validation for MS_83105 (TY2025).

⚠ NEVER touches `test_postgres` - RS and delvio-tax share that database name, and
the runner destroys and recreates it. This harness builds a private SQLite file.

The checks that matter most are PROVED, not asserted - each shows that the wrong
answer DIFFERS, which is the only way a reader can tell the rule was necessary:
  * S1 - the DOR zero floor and the statutory $25 minimum return DIFFERENT numbers
  * S4 - the corporate and individual rate ladders DIVERGE at TY2027
  * the L19/L20 asymmetry - "symmetrising" it shorts the client
  * S3 - the stale five-year NOL regulation expires a live loss
  * S2 - the regulation's 1% is exactly double the form face's ½%
  * "or fractional part thereof" rounds the unit count UP, not down
  * an ABSENCE check that inspects CODE: the stale five-year figure appears nowhere

Run:  .venv/Scripts/python.exe scratchpad/validate_ms_83105.py
"""
import ast
import io as io2
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

PROJECT_ROOT = r"D:\dev\delvio-rule-studio"
sys.path.insert(0, PROJECT_ROOT)

SQLITE_PATH = os.path.join(PROJECT_ROOT, "scratchpad", "validate_ms_83105.sqlite3")
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
from specs.management.commands import load_ms_83105 as MS  # noqa: E402

FAILURES: list[str] = []
PASSES: list[str] = []


def check(cond, ok, bad):
    (PASSES if cond else FAILURES).append(ok if cond else bad)


def approx(a, b, tol=0.005):
    return a is not None and abs(float(a) - float(b)) <= tol


call_command("migrate", run_syncdb=True, verbosity=0)

# ⚠ PREREQUISITE: MS_83105 REFERENCES four AuthoritySource rows that the seeded
# MS PTE loader OWNS (the two-writers rule - we never re-declare them). On a
# throwaway database nothing owns them yet, so seed the owner first. This is not
# a convenience: it is the only way this harness can prove that the references
# RESOLVE rather than merely that they are spelled plausibly.
call_command("load_ms_84105", verbosity=0)

# ======================================================================
# 0. THE SEED GUARD - pinned to the GATE MECHANISM, not the sentinel value
# ======================================================================
_shipped = MS.READY_TO_SEED
check(_shipped is False, "READY_TO_SEED ships as False (D-26 approved SCOPE, not the seed gate)",
      f"⚠⚠ READY_TO_SEED SHIPPED AS {_shipped!r} - this loader would seed without Ken's gate")

MS.READY_TO_SEED = False
try:
    call_command("load_ms_83105", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: seeded while READY_TO_SEED was False")
except CommandError as exc:
    msg = " ".join(str(exc).split())
    check("not cleared to seed" in msg, "the seed guard REFUSES when the sentinel is down",
          f"unexpected guard message: {msg[:150]!r}")
    check("relayed approval never opens a human gate" in msg,
          "the guard states the gate rule", "the guard omits the gate rule")

MS.READY_TO_SEED = True
_saved = MS.FLOW_ASSERTIONS
MS.FLOW_ASSERTIONS = []
try:
    call_command("load_ms_83105", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: seeded a hollow spec")
except CommandError:
    PASSES.append("the seed guard ALSO refuses a hollow spec, sentinel up")
MS.FLOW_ASSERTIONS = _saved

try:
    call_command("load_ms_83105", verbosity=0)
    PASSES.append("load_ms_83105 ran + seeded into throwaway SQLite")
except Exception as exc:  # noqa: BLE001
    FAILURES.append(f"load_ms_83105 raised: {exc!r}")

# ======================================================================
# 1. CharField caps from the REAL model fields (D-17 - Postgres-only failures)
# ======================================================================
for model, field, values in (
    (FormRule, "rule_id", [r["rule_id"] for r in MS.F_RULES]),
    (FormRule, "title", [r["title"] for r in MS.F_RULES]),
    (FormLine, "line_number", [l["line_number"] for l in MS.F_LINES]),
    (FlowAssertion, "assertion_id", [a["assertion_id"] for a in MS.FLOW_ASSERTIONS]),
    (FlowAssertion, "title", [a["title"] for a in MS.FLOW_ASSERTIONS]),
    (FormDiagnostic, "diagnostic_id", [d["diagnostic_id"] for d in MS.F_DIAGNOSTICS]),
    (FormDiagnostic, "title", [d["title"] for d in MS.F_DIAGNOSTICS]),
    (FormFact, "fact_key", [f["fact_key"] for f in MS.F_FACTS]),
    (FormFact, "label", [f["label"] for f in MS.F_FACTS]),
    (TestScenario, "scenario_name", [s["scenario_name"] for s in MS.F_SCENARIOS]),
    (AuthorityTopic, "topic_name", [n for _c, n in MS.AUTHORITY_TOPICS]),
    (AuthoritySource, "source_code", [s["source_code"] for s in MS.AUTHORITY_SOURCES]),
    (AuthoritySource, "citation", [s.get("citation") or "" for s in MS.AUTHORITY_SOURCES]),
    (AuthoritySource, "title", [s["title"] for s in MS.AUTHORITY_SOURCES]),
    (TaxForm, "form_title", [f["identity"]["form_title"] for f in MS.FORMS]),
):
    limit = model._meta.get_field(field).max_length
    if limit is None:
        PASSES.append(f"{model.__name__}.{field}: unbounded (TextField)")
        continue
    over = [(v[:40], len(v)) for v in values if v and len(v) > limit]
    check(not over, f"{model.__name__}.{field}: all within the real cap ({limit})",
          f"{model.__name__}.{field} OVERFLOWS {limit} (Postgres-only failure): {over}")

# ======================================================================
# 2. Structure
# ======================================================================
form = TaxForm.objects.filter(form_number="MS_83105").first()
check(form is not None, "MS_83105 exists", "MS_83105 was not created")
if form:
    check(form.jurisdiction == "MS" and form.tax_year == 2025, "identity: MS / TY2025", "identity wrong")
    check(form.entity_types == ["1120"], "entity_types == ['1120']", f"wrong: {form.entity_types}")

for label, values in (("rule_id", [r["rule_id"] for r in MS.F_RULES]),
                      ("line_number", [l["line_number"] for l in MS.F_LINES]),
                      ("fact_key", [f["fact_key"] for f in MS.F_FACTS]),
                      ("diagnostic_id", [d["diagnostic_id"] for d in MS.F_DIAGNOSTICS]),
                      ("scenario_name", [s["scenario_name"] for s in MS.F_SCENARIOS])):
    dupes = {v for v in values if values.count(v) > 1}
    check(not dupes, f"no duplicate {label}", f"duplicate {label}: {sorted(dupes)}")

_declared = {r["rule_id"] for r in MS.F_RULES}
_cited = {rl[0] for rl in MS.F_RULE_LINKS}
check(not sorted(_declared - _cited), "every FormRule carries at least one authority link",
      f"uncitable rules: {sorted(_declared - _cited)}")
check(not sorted(_cited - _declared), "every authority link names a declared rule",
      f"⚠ DANGLING RULE REFERENCE in F_RULE_LINKS: {sorted(_cited - _declared)}")

# ⚠⚠ DANGLING-SOURCE GUARD (D-25/O4, D-29) - every code a rule link names must be
# either declared here or listed for reference.
_source_universe = ({s["source_code"] for s in MS.AUTHORITY_SOURCES}
                    | set(MS.EXISTING_SOURCES_TO_REFERENCE))
_bad_link_sources = {rl[1] for rl in MS.F_RULE_LINKS} - _source_universe
check(not _bad_link_sources, "every rule link resolves to a declared or referenced source",
      f"⚠ DANGLING SOURCE REFERENCE: {sorted(_bad_link_sources)}")
_bad_form_links = {fl[0] for fl in MS.AUTHORITY_FORM_LINKS} - _source_universe
check(not _bad_form_links, "every AUTHORITY_FORM_LINK resolves",
      f"⚠ DANGLING SOURCE in AUTHORITY_FORM_LINKS: {sorted(_bad_form_links)}")

# ⚠⚠ TWO-WRITERS GUARD (the D-31 lesson) - static, no database needed.
# ⚠ HARDENED while authoring CO_DR0112: the older version scanned only `load_*.py`
# for a DOUBLE-QUOTED `"source_code":`. The shared module `_state_conformity_tier1.py`
# matches NEITHER - it is not `load_*` and it uses single quotes - yet it OWNS
# several AuthoritySource rows. A guard that cannot see the owner cannot detect a
# second writer of it. This version scans every module and both quote styles.
import glob as _glob  # noqa: E402
import re as _re  # noqa: E402

_COMMANDS_DIR = os.path.join(PROJECT_ROOT, "specs", "management", "commands")


def _declares_source(text, code):
    return bool(_re.search(r"""['"]source_code['"]\s*:\s*['"]%s['"]""" % _re.escape(code), text))


_declared_here = {s["source_code"] for s in MS.AUTHORITY_SOURCES}
_clashes, _owners = [], {}
for _name in os.listdir(_COMMANDS_DIR):
    if not _name.endswith(".py") or _name == "load_ms_83105.py":
        continue
    _other = io2.open(os.path.join(_COMMANDS_DIR, _name), encoding="utf-8").read()
    for _code in _declared_here:
        if _declares_source(_other, _code):
            _clashes.append((_code, _name))
    for _code in MS.EXISTING_SOURCES_TO_REFERENCE:
        if _declares_source(_other, _code):
            _owners.setdefault(_code, []).append(_name)
check(not _clashes,
      "⚠⚠ TWO-WRITERS GUARD (hardened): no source declared here is declared by any other module",
      f"TWO WRITERS OF ONE ROW - would OVERWRITE a source another module owns: {_clashes}")

_orphan_refs = [c for c in MS.EXISTING_SOURCES_TO_REFERENCE if c not in _owners]
check(not _orphan_refs,
      "every EXISTING_SOURCES_TO_REFERENCE code is genuinely owned by another module",
      f"⚠ referenced but owned by NOTHING (a dangling reference on a clean database): "
      f"{_orphan_refs}")
_multi_owned = {c: m for c, m in _owners.items() if len(m) > 1}
check(not _multi_owned, "no referenced source has two owners",
      f"⚠ DUPLICATE OWNERSHIP - two modules declare the same row: {_multi_owned}")

# ======================================================================
# 3. ⚠⚠ S1 - THE FRANCHISE FLOOR. Both readings computed; they MUST differ.
# ======================================================================
_l2 = MS._ms_franchise_line2(5100000)
check(approx(_l2, 3750.0), "L2: (5,100,000 - 100,000)/1,000 x $0.75 = $3,750",
      f"L2 came out {_l2}")

_dor = MS._ms_franchise_line4(_l2, 4000)
_stat = MS._ms_franchise_line4_statutory_reading(_l2, 4000)
check(approx(_dor, 0.0), "⚠⚠ S1: the DOR L4 instruction returns ZERO when credits exceed line 2",
      f"the shipped floor returned {_dor}, not 0")
check(approx(_stat, 25.0), "⚠⚠ S1: the statutory reading returns $25 on the same facts",
      f"the statutory reading returned {_stat}, not 25")
check(abs(_dor - _stat) > 0.0,
      "⚠⚠ S1 PROVED: the two DOR texts give DIFFERENT answers - this was a real ruling, not a "
      "formality (difference $%.2f on every affected return)" % abs(_stat - _dor),
      "⚠ the two readings agree - the S1 ruling would then be vacuous, which contradicts D-26")
check(MS._yk(MS.MS_FRANCHISE_NET_FLOOR) == 0,
      "the SHIPPED floor is the DOR zero (D-26 S1)",
      f"⚠ the shipped floor is {MS._yk(MS.MS_FRANCHISE_NET_FLOOR)} - D-26 S1 ruled zero")
check("DOR ticket" in MS.MS_FRANCHISE_NET_FLOOR_BASIS and "27-13-5(1)(b)" in MS.MS_FRANCHISE_NET_FLOOR_BASIS,
      "the floor constant carries its basis AND the competing citation",
      "the floor constant does not record why it was chosen or what it was chosen against")

# ⚠ "or fractional part thereof" - the unit count is a CEILING.
_frac = MS._ms_franchise_line2(1000500)
_trunc = ((1000500 - 100000) / 1000) * 0.75
check(approx(_frac, 675.75), "⚠ 'or fractional part thereof': 900,500 -> 901 units x $0.75 = $675.75",
      f"fractional-unit rounding gave {_frac}")
check(_frac > _trunc,
      "⚠ PROVED: truncating the unit count understates the tax (%.3f vs %.2f)" % (_trunc, _frac),
      "truncation and ceiling agree here - pick a base that is not a multiple of $1,000")

_min = MS._ms_franchise_line2(110000)
check(approx(_min, 25.0), "the $25 line-2 minimum bites at small capital", f"got {_min}")

# The repeal is a REFUSAL, not a zero rate.
try:
    MS._ms_franchise_line2(5100000, 2028)
    FAILURES.append("⚠ TY2028 computed a franchise tax - the levy is REPEALED, not zero-rated")
except CommandError as exc:
    check("REPEALED" in str(exc), "TY2028 REFUSES: the franchise levy is repealed, not zero-rated",
          f"unexpected TY2028 message: {str(exc)[:120]!r}")

# ======================================================================
# 4. ⚠⚠ S4 - THE LADDER MUST BE KEYED BY TAXPAYER TYPE
# ======================================================================
_c25 = MS._ms_income_tax(250000, 2025, "corporation")
check(approx(_c25, 12200.0), "0/4/5: 0 + 200 + 5% x 240,000 = 12,200", f"got {_c25}")
check(abs(_c25 - 250000 * 0.05) > 0.0,
      "⚠ PROVED: a flat 5%% would give %.0f - the two low brackets are worth $300 to every "
      "Mississippi corporation, every year" % (250000 * 0.05),
      "a flat 5% agrees with the ladder - the bracket structure is not being applied")

_c27 = MS._ms_income_tax(250000, 2027, "corporation")
_i27 = MS._ms_income_tax(250000, 2027, "individual")
check(approx(_c27, 12200.0), "⚠⚠ S4: the CORPORATE ladder is still 0/4/5 at TY2027", f"got {_c27}")
check(approx(_i27, 9200.0), "⚠⚠ S4: the INDIVIDUAL ladder drops to 3.75% at TY2027 (HB 1)", f"got {_i27}")
check(abs(_c27 - _i27) > 0.0,
      "⚠⚠ S4 PROVED: the two ladders DIVERGE at TY2027 by $%.0f on this return - a single "
      "year-keyed table would hand a corporation the individual answer, silently, in a year "
      "nobody will be re-reading this spec" % abs(_c27 - _i27),
      "⚠ the ladders agree at TY2027 - then S4's keying would be unnecessary, contradicting D-26")
check(MS.MS_RATE_LADDER["corporation"][2030] == MS.MS_RATE_LADDER["corporation"][2025],
      "the corporate ladder is flat through TY2030 (it is not on a phase-down)",
      "the corporate ladder moves - HB 1's steps are limited to individuals")

try:
    MS._ms_income_tax(250000, 2025, "partnership")
    FAILURES.append("⚠ an unknown taxpayer_type computed silently instead of refusing")
except CommandError:
    PASSES.append("an unknown taxpayer_type REFUSES rather than defaulting")

# The § 27-7-5(4) blend is a real blend, proved across a boundary where rates differ.
_ident = MS._ms_income_tax_fiscal_blend(250000, 6, 12, 2025, 2026, "corporation")
check(approx(_ident, 12200.0), "§ 27-7-5(4): the TY2025/26 corporate blend is the IDENTITY",
      f"got {_ident}")
_real = MS._ms_income_tax_fiscal_blend(250000, 6, 12, 2026, 2027, "individual")
check(approx(_real, (12200.0 + 9200.0) / 2),
      "⚠ PROVED a REAL blend: across the individual TY2026/27 boundary it returns the "
      "months-weighted mean (%.0f), not either endpoint" % _real,
      f"the blend returned {_real} - it is not weighting the two schedules")

# ======================================================================
# 5. ⚠⚠ THE L19/L20 ASYMMETRY - symmetrising it shorts the client
# ======================================================================
_l19 = MS._ms_line19_balance_due(10000, 12000, 0, 300, 100, 100, 100)
_l20 = MS._ms_line20_overpayment(10000, 12000, 300)
check(approx(_l19, 0.0), "L19 is zero when line 13 exceeds line 9", f"got {_l19}")
check(approx(_l20, 1700.0), "L20 = 12,000 - 10,000 - 300 = 1,700 (nets L15 only)", f"got {_l20}")
_symmetrised = 12000 - 10000 - 300 - 100 - 100 - 100
check(abs(_l20 - _symmetrised) > 0.0,
      "⚠⚠ PROVED: a 'symmetrised' L20 that also netted L16-L18 would return %d and short the "
      "client $%d on the refund" % (_symmetrised, _l20 - _symmetrised),
      "symmetrising makes no difference here - choose a case with late-payment amounts")

# ======================================================================
# 6. ⚠ S3 - THE STALE FIVE-YEAR NOL REGULATION EXPIRES A LIVE LOSS
# ======================================================================
_exp = MS._ms_nol_expiry_year(2019)
check(_exp == 2039, "S3: a 2019 loss carries forward to 2039 (twenty periods)", f"got {_exp}")
_stale = 2019 + 5
check(_stale < MS.FORM_TAX_YEAR <= _exp,
      "⚠ S3 PROVED: the stale five-year regulation would have EXPIRED this loss in %d - before "
      "the TY%d return being prepared - silently disallowing fifteen more years of a deduction "
      "the taxpayer is entitled to" % (_stale, MS.FORM_TAX_YEAR),
      "the stale reading does not bite on this vintage - pick one where it does")
check(MS._yk(MS.MS_NOL_CARRYBACK_YEARS) == 2 and MS._yk(MS.MS_NOL_CARRYFORWARD_YEARS) == 20,
      "the shipped NOL periods are 2 back / 20 forward", "the NOL periods are not 2/20")

# ⚠⚠ AN ABSENCE CHECK THAT INSPECTS CODE, NOT PROSE (the MO_1120 pattern).
# The stale "five succeeding years" figure must appear NOWHERE as a numeric NOL
# constant - and the 20 must be present, so the check cannot pass by being empty.
_src = io2.open(os.path.join(PROJECT_ROOT, "specs", "management", "commands",
                             "load_ms_83105.py"), encoding="utf-8").read()
_tree = ast.parse(_src)
_nol_values = []
for _node in ast.walk(_tree):
    if isinstance(_node, ast.AnnAssign) and isinstance(_node.target, ast.Name) \
            and "NOL" in _node.target.id and _node.value is not None:
        for _sub in ast.walk(_node.value):
            if isinstance(_sub, ast.Constant) and isinstance(_sub.value, int):
                _nol_values.append(_sub.value)
check(5 not in _nol_values,
      "⚠⚠ ABSENCE CHECK (code, not prose): the stale five-year period appears in NO NOL constant",
      f"⚠ a literal 5 is present in an NOL constant: {_nol_values}")
check(20 in _nol_values,
      "...and the check cannot pass by being empty - the 20 IS present",
      f"the twenty-year period is missing from the NOL constants: {_nol_values}")

# ======================================================================
# 7. ⚠ S2 - THE REGULATION'S 1% IS EXACTLY DOUBLE THE FORM FACE
# ======================================================================
_face = MS._ms_underestimate_interest(40000, 6)
_reg = 40000 * 0.01 * 6
check(approx(_face, 1200.0), "S2: 40,000 x ½% x 6 months = 1,200 (the form face)", f"got {_face}")
check(approx(_reg / _face, 2.0),
      "⚠ S2 PROVED: the regulation's 1%% would charge %.0f - exactly DOUBLE - on every "
      "underpaid Mississippi corporate return" % _reg,
      "the two rates do not differ as expected")
check(MS._yk(MS.MS_UNDERESTIMATE_INTEREST_MONTHLY) == "0.005",
      "the shipped underestimate rate is the form face's ½%", "the shipped rate is not ½%")

# ======================================================================
# 8. The scope levers each NAME what they refuse
# ======================================================================
_diag_ids = {d["diagnostic_id"] for d in MS.F_DIAGNOSTICS}
for _need, _why in (("D_MS83105_COMBINED_RETURN", "W2/W16 combined filing"),
                    ("D_MS83105_INSURANCE_FILER", "W3 Form 83-391 insurance"),
                    ("D_MS83105_DIRECT_ACCOUNTING", "W4 Form 83-124 direct accounting"),
                    ("D_MS83105_FEE_IN_LIEU", "W5/U1 fee-in-lieu"),
                    ("D_MS83105_CAPITAL_EXEMPTION_UNDEFINED", "W5/U3/U4 capital exemption"),
                    ("D_MS83105_83110_L4_LOAN", "W15 loan recharacterisation"),
                    ("D_MS83105_INDUSTRY_APPORTIONMENT", "W6 special-industry apportionment"),
                    ("D_MS83105_CREDIT_ADDBACK_LOOP", "W9 credit add-back"),
                    ("D_MS83105_AVIATION_PER_ASSET", "W10 aviation per-asset regime"),
                    ("D_MS83105_FRANCHISE_FLOOR_BITES", "S1 the flag half of 'ship it flagged'")):
    check(_need in _diag_ids, f"diagnostic present for {_why}", f"MISSING diagnostic for {_why}")

for _d in MS.F_DIAGNOSTICS:
    if _d["severity"] == "error":
        check(len(_d["message"]) > 200,
              f"{_d['diagnostic_id']}: the refusal explains itself at length",
              f"{_d['diagnostic_id']}: a hard stop with a {len(_d['message'])}-char message - a "
              "refusal that does not name what it refuses is a dead end for the preparer")

_combined = next(d for d in MS.F_DIAGNOSTICS if d["diagnostic_id"] == "D_MS83105_COMBINED_RETURN")
check("DISJOINT" in _combined["message"],
      "⚠⚠ the combined diagnostic records WHY detection cannot be skipped (W16 disjointness)",
      "the combined diagnostic defers without recording the disjointness that makes detection a "
      "prerequisite")

# ======================================================================
# 9. Persisted-row counts match what the module declares
# ======================================================================
if form:
    for _model, _decl, _label in ((FormFact, MS.F_FACTS, "facts"),
                                  (FormRule, MS.F_RULES, "rules"),
                                  (FormLine, MS.F_LINES, "lines"),
                                  (FormDiagnostic, MS.F_DIAGNOSTICS, "diagnostics"),
                                  (TestScenario, MS.F_SCENARIOS, "scenarios")):
        _n = _model.objects.filter(tax_form=form).count()
        check(_n == len(_decl), f"{_label}: {_n} rows persisted == {len(_decl)} declared",
              f"{_label}: {_n} persisted but {len(_decl)} declared")
# ⚠ FlowAssertion is form-agnostic (no tax_form FK), and the prerequisite MS PTE
# loader writes its own. Count only the ids THIS spec declares.
_fa_ids = [a["assertion_id"] for a in MS.FLOW_ASSERTIONS]
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
print(f"MS_83105 harness: {len(PASSES)} pass / {len(FAILURES)} fail")
print("=" * 74)
sys.exit(1 if FAILURES else 0)
