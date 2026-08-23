"""Throwaway-SQLite validation for MD_500 — Maryland Corporation Income Tax Return (TY2025).

Runs entirely against a throwaway SQLite file. ⚠ It NEVER touches `test_postgres`
— delvio-rule-studio and delvio-tax share that database name, so an RS suite run
is a delvio-tax pytest run for locking purposes (found the hard way 2026-08-22).

Checks, in order:
  0. THE SAFETY GUARD — pinned to the GATE MECHANISM, never to the sentinel's
     disk value. The campaign has watched a harness go red the moment Ken
     approved something FIVE times (campaign D-17); each time the fix was the
     same. So this drives the sentinel DOWN and proves the loader REFUSES, then
     drives it UP to load. It never asserts "ships False".
  1. CharField caps read from the REAL MODEL FIELDS via Django's _meta. ⚠
     Postgres enforces these; SQLite does NOT. Nine values overflowed on the
     Louisiana seed and failed only against prod (campaign D-17). This harness
     is the only thing standing in the way.
  2. Structural integrity — no duplicate ids, every rule carries an authority
     link, every rule_link resolves, identity is MD/TY2025/v1/draft/["1120"].
  3. ARITHMETIC ORACLES driven through the loader's OWN helpers.
  4. KEN'S RULINGS ARE ENCODED — each of D-19/D-20's decisions is pinned by a
     check that would FAIL if a later edit quietly reversed it.
  5. Every RED-defer has its own diagnostic.

ASCII-only output. Run:  .venv/Scripts/python.exe scratchpad/validate_md_500.py
"""
import os
import sys

PROJECT_ROOT = r"D:\dev\delvio-rule-studio"
sys.path.insert(0, PROJECT_ROOT)

SQLITE_PATH = os.path.join(PROJECT_ROOT, "scratchpad", "validate_md_500.sqlite3")
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
from sources.models import (  # noqa: E402
    AuthoritySource, AuthorityTopic, RuleAuthorityLink,
)
from specs.management.commands import load_md_500 as MD  # noqa: E402

FAILURES: list[str] = []
PASSES: list[str] = []


def check(cond, ok, bad):
    (PASSES if cond else FAILURES).append(ok if cond else bad)


def approx(a, b, tol=0.005):
    return a is not None and abs(float(a) - float(b)) <= tol


call_command("migrate", run_syncdb=True, verbosity=0)

# ======================================================================
# 0. THE SAFETY GUARD -- pin the MECHANISM, not the sentinel's value.
# ======================================================================
_shipped_ready = MD.READY_TO_SEED

MD.READY_TO_SEED = False
try:
    call_command("load_md_500", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: load_md_500 seeded while READY_TO_SEED was False")
except CommandError as exc:
    check("not cleared to seed" in str(exc),
          "the seed guard REFUSES when the sentinel is down, and says why",
          f"guard fired but with an unexpected message: {exc!r}")
    # The message is hard-wrapped, so normalise whitespace before matching.
    _guard_msg = " ".join(str(exc).split())
    check("relayed approval never opens a human gate" in _guard_msg,
          "the guard's message states the gate rule (a relayed approval never opens it)",
          f"the guard message does not state the gate rule: {_guard_msg[:200]!r}")

# A hollow spec must ALSO be refused, even with the sentinel UP.
MD.READY_TO_SEED = True
_saved_fa = MD.FLOW_ASSERTIONS
MD.FLOW_ASSERTIONS = []
try:
    call_command("load_md_500", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: load_md_500 seeded a spec with NO flow assertions")
except CommandError:
    PASSES.append("the seed guard ALSO refuses a hollow spec (empty FLOW_ASSERTIONS), sentinel up")
MD.FLOW_ASSERTIONS = _saved_fa

# Now load for real.
try:
    call_command("load_md_500", verbosity=0)
    PASSES.append("load_md_500 ran + seeded into throwaway SQLite without error")
except Exception as exc:  # noqa: BLE001
    FAILURES.append(f"load_md_500 raised: {exc!r}")

# ======================================================================
# 1. CharField caps -- read from the REAL MODEL FIELDS, not hardcoded.
#    Postgres enforces these; SQLite does not. This is the ONLY guard.
# ======================================================================
def cap(model, field):
    return model._meta.get_field(field).max_length


_CAP_TARGETS = [
    (FormRule, "rule_id", [r["rule_id"] for r in MD.F_RULES]),
    (FormRule, "title", [r["title"] for r in MD.F_RULES]),
    (FormLine, "line_number", [l["line_number"] for l in MD.F_LINES]),
    (FlowAssertion, "assertion_id", [a["assertion_id"] for a in MD.FLOW_ASSERTIONS]),
    (FlowAssertion, "title", [a["title"] for a in MD.FLOW_ASSERTIONS]),
    (FormDiagnostic, "diagnostic_id", [d["diagnostic_id"] for d in MD.F_DIAGNOSTICS]),
    (FormDiagnostic, "title", [d["title"] for d in MD.F_DIAGNOSTICS]),
    (FormFact, "fact_key", [f["fact_key"] for f in MD.F_FACTS]),
    (FormFact, "label", [f["label"] for f in MD.F_FACTS]),
    (TestScenario, "scenario_name", [s["scenario_name"] for s in MD.F_SCENARIOS]),
    (AuthorityTopic, "topic_name", [n for _c, n in MD.AUTHORITY_TOPICS]),
    (AuthoritySource, "source_code", [s["source_code"] for s in MD.AUTHORITY_SOURCES]),
    (AuthoritySource, "citation", [s.get("citation") or "" for s in MD.AUTHORITY_SOURCES]),
    (AuthoritySource, "issuer", [s.get("issuer") or "" for s in MD.AUTHORITY_SOURCES]),
    (AuthoritySource, "title", [s["title"] for s in MD.AUTHORITY_SOURCES]),
    (TaxForm, "form_number", [f["identity"]["form_number"] for f in MD.FORMS]),
    (TaxForm, "form_title", [f["identity"]["form_title"] for f in MD.FORMS]),
]
for model, field, values in _CAP_TARGETS:
    limit = cap(model, field)
    if limit is None:
        # TextField -- unbounded in Postgres too, so there is nothing to guard.
        PASSES.append(f"{model.__name__}.{field}: unbounded (TextField) -- no cap to enforce")
        continue
    over = [(v, len(v)) for v in values if v is not None and len(v) > limit]
    check(not over,
          f"{model.__name__}.{field}: all {len(values)} values within the real cap ({limit})",
          f"{model.__name__}.{field} OVERFLOWS the {limit}-char column (Postgres-only failure): {over}")

# ======================================================================
# 2. Structural integrity
# ======================================================================
form = TaxForm.objects.filter(form_number="MD_500").first()
check(form is not None, "MD_500 exists", "MD_500 was not created")

if form:
    check(form.jurisdiction == "MD" and form.tax_year == 2025 and form.version == 1,
          "identity: jurisdiction MD, TY2025, version 1",
          f"identity wrong: {form.jurisdiction}/{form.tax_year}/v{form.version}")
    check(form.entity_types == ["1120"],
          "entity_types == ['1120'] -- MD_500 is the C-corp return only",
          f"entity_types wrong: {form.entity_types}")
    check(form.status == "draft", "status is draft (approve_specs is a separate phase)",
          f"status wrong: {form.status}")

for label, values in (
    ("rule_id", [r["rule_id"] for r in MD.F_RULES]),
    ("line_number", [l["line_number"] for l in MD.F_LINES]),
    ("fact_key", [f["fact_key"] for f in MD.F_FACTS]),
    ("diagnostic_id", [d["diagnostic_id"] for d in MD.F_DIAGNOSTICS]),
    ("assertion_id", [a["assertion_id"] for a in MD.FLOW_ASSERTIONS]),
):
    dupes = {v for v in values if values.count(v) > 1}
    check(not dupes, f"no duplicate {label}", f"duplicate {label}: {sorted(dupes)}")

_declared_rules = {r["rule_id"] for r in MD.F_RULES}
_declared_sources = {s["source_code"] for s in MD.AUTHORITY_SOURCES} | set(MD.EXISTING_SOURCES_TO_REFERENCE)
_bad_link_rule = [rl[0] for rl in MD.F_RULE_LINKS if rl[0] not in _declared_rules]
_bad_link_src = [rl[1] for rl in MD.F_RULE_LINKS if rl[1] not in _declared_sources]
check(not _bad_link_rule, "every rule_link points at a declared rule",
      f"rule_links reference undefined rules: {sorted(set(_bad_link_rule))}")
check(not _bad_link_src, "every rule_link points at a declared source",
      f"rule_links reference undeclared sources: {sorted(set(_bad_link_src))}")

_linked = {rl[0] for rl in MD.F_RULE_LINKS}
_unlinked = sorted(_declared_rules - _linked)
check(not _unlinked, "every FormRule carries at least one authority link",
      f"rules with NO authority link (unciteable): {_unlinked}")

if form:
    check(RuleAuthorityLink.objects.filter(form_rule__tax_form=form).count() > 0,
          "authority links resolved and persisted", "no authority links persisted")

# Every rule's source_rules on lines must name a real rule.
_line_rule_refs = {r for l in MD.F_LINES for r in l.get("source_rules", [])}
check(_line_rule_refs <= _declared_rules,
      "every FormLine.source_rules entry names a declared rule",
      f"lines reference undefined rules: {sorted(_line_rule_refs - _declared_rules)}")

# ======================================================================
# 3. ARITHMETIC ORACLES -- through the loader's own helpers
# ======================================================================
# -- 3a. The rate, and that it is the WHOLE tax (no county overlay) --------
check(MD._yk(MD.MD_CORP_RATE) == "0.0825",
      "the corporate rate is 8.25% (Tax-Gen 10-105(b)), TY-keyed",
      f"rate wrong: {MD.MD_CORP_RATE}")

# -- 3b. Line 6: THE ASYMMETRY. This is the spec's sharpest trap. ----------
check(approx(MD._md500_line6(-400000, 250000), -400000),
      "L6: a LOSS passes through untouched -- the NOL is NOT applied when L4 <= 0",
      "L6 applied the NOL to a loss year -- the loss would never reach lines 23/24")
check(approx(MD._md500_line6(300000, 500000), 0),
      "L6: a PROFIT reduced below zero by the NOL floors at 0",
      "L6 did not floor a profit reduced past zero")
check(approx(MD._md500_line6(300000, 100000), 200000),
      "L6: a PROFIT reduced by a smaller NOL subtracts normally",
      "L6 arithmetic wrong on the ordinary profit branch")
check(approx(MD._md500_line6(0, 900000), 0),
      "L6: exactly zero takes the 'less than or equal to' branch",
      "L6 mishandled L4 == 0 (the face says 'less than OR EQUAL TO zero')")
# The collapse that would look like a simplification and is a real defect:
check(not approx(MD._md500_line6(-400000, 250000), max(0.0, -400000 - 250000)),
      "L6 is NOT a single max() -- collapsing the branches is provably different",
      "L6 behaves like max(0, L4-L5); the two-branch rule has been collapsed")

# -- 3c. Apportionment: six decimals, zero factor, NO reweight -------------
check(approx(MD._md500_apportionment_factor(1234567, 10000000), 0.123457, tol=5e-7),
      "Schedule A Column 3 rounds to SIX places (0.1234567 -> 0.123457)",
      "apportionment did not round to six decimals")
check(MD._md500_apportionment_factor(500000, 0) is None,
      "a ZERO denominator yields NO factor (None) -- never a reweight, never 1.0",
      "a zero denominator produced a factor -- D-5 auto-reweight prohibition broken")
check(MD._md500_apportionment_factor(500000, None) is None,
      "a MISSING denominator yields NO factor (None)",
      "a missing denominator produced a factor")
check(approx(MD._md500_apportionment_factor(0, 4000000), 0.0),
      "a zero numerator yields a zero factor (which prints as .000000)",
      "zero-numerator case wrong")
check(approx(MD._md500_apportionment_factor(4000000, 4000000), 1.0),
      "an all-Maryland multistate corporation yields exactly 1.000000",
      "the factor-of-one case is wrong")

# ⚠ D-4 -- the constant that must NEVER be harmonised with 510/511's .000001
check(MD._yk(MD.MD500_ZERO_FACTOR) == "0.000000",
      "D-4: MD_500's zero factor is '.000000'",
      f"MD_500 zero factor is {MD._yk(MD.MD500_ZERO_FACTOR)!r} -- must be '0.000000'")
check(MD._yk(MD.MD500_ZERO_FACTOR) != "0.000001",
      "D-4: MD_500 did NOT inherit the Forms 510/511 '.000001' convention",
      "MD_500 carries the PTE forms' .000001 -- the sibling-form constants were harmonised")

# -- 3d. NAM: line 24 = line 9 EXACTLY (D-6) ------------------------------
check(approx(MD._md500_line24_nam(-400000, 60000), 60000),
      "D-6: L24 = L9 exactly when L6 < 0 AND L9 > 0",
      "L24 is not L9 in the firing case")
check(approx(MD._md500_line24_nam(-400000, -5000), 0),
      "L24 is zero when L9 is not positive",
      "L24 fired on a non-positive L9")
check(approx(MD._md500_line24_nam(120000, 60000), 0),
      "L24 is zero when L6 is not negative",
      "L24 fired on a non-negative L6")
check(approx(MD._md500_line24_nam(0, 60000), 0),
      "L24 does not fire at L6 == 0 (the face says 'less than zero')",
      "L24 fired at L6 exactly zero")

# -- 3e. Maryland's own s.179 figures, which are NOT the federal ones ------
check(MD._yk(MD.MD_179_LIMIT) == 25000 and MD._yk(MD.MD_179_PHASEOUT) == 200000,
      "Maryland s.179 is $25,000 / $200,000 (Tax-Gen 10-210.1(b)(3)(i))",
      f"MD s.179 wrong: {MD._yk(MD.MD_179_LIMIT)}/{MD._yk(MD.MD_179_PHASEOUT)}")
check(MD._yk(MD.MD_179_LIMIT) not in (2500000, 1250000, 1050000),
      "Maryland s.179 is NOT the federal OBBBA figure and NOT Georgia's",
      "MD s.179 has been contaminated with a federal or Georgia figure")

# -- 3f. TY-keying: an unverified year must REFUSE, not silently pass ------
try:
    MD._yk(MD.MD_CORP_RATE, 2026)
    FAILURES.append("_yk returned a TY2026 rate that was never verified -- staleness guard broken")
except CommandError:
    PASSES.append("_yk REFUSES an unverified tax year (a new TY staleness-invalidates every figure)")

# ======================================================================
# 4. KEN'S RULINGS ARE ENCODED -- each pinned so a later edit cannot
#    quietly reverse it. (Campaign D-19 / D-20, 2026-08-23.)
# ======================================================================
_diag = {d["diagnostic_id"]: d for d in MD.F_DIAGNOSTICS}
_rules = {r["rule_id"]: r for r in MD.F_RULES}
_facts = {f["fact_key"]: f for f in MD.F_FACTS}
_alltext = " ".join(
    [d["message"] + d["title"] + d.get("notes", "") for d in MD.F_DIAGNOSTICS]
    + [r["description"] + r["title"] for r in MD.F_RULES]
    + [a["description"] + a["title"] for a in MD.FLOW_ASSERTIONS]
)

# D3 -- worldwide-HQ is an ELECTION; the booklet's "must use" is an erratum.
check("D_MD500_WWHQ_ELECTION" in _diag and _diag["D_MD500_WWHQ_ELECTION"]["severity"] == "error",
      "D3: the worldwide-HQ election is RED-deferred (severity error)",
      "D3: no hard diagnostic for the worldwide-HQ election")
check("may elect" in _alltext,
      "D3: the spec records the statute's 'may elect' language",
      "D3: the statutory 'may elect' is not recorded anywhere")
check("erratum" in _alltext.lower() or "contradict" in _alltext.lower(),
      "D3: the booklet's contradiction is recorded so nobody 'fixes' the spec back to it",
      "D3: the booklet erratum is not recorded -- a future reader could 'correct' us to it")
check("worldwide_hq_election" in _facts,
      "D3: the election is an explicit taxpayer FACT, never inferred",
      "D3: no explicit election fact -- the election could be inferred")

# W9 -- 500CR deferred, and the diagnostic must name waiver reason B.
check("D_MD500_500CR_DEFERRED" in _diag and _diag["D_MD500_500CR_DEFERRED"]["severity"] == "error",
      "W9: Form 500CR is RED-deferred (severity error)",
      "W9: no hard diagnostic for the 500CR deferral")
check("500CRW" in _diag.get("D_MD500_500CR_DEFERRED", {}).get("message", "")
      and "REASON B" in _diag.get("D_MD500_500CR_DEFERRED", {}).get("message", "").upper(),
      "W9: the 500CR diagnostic names Form 500CRW REASON B as the remedy (Ken's explicit ask)",
      "W9: the 500CR diagnostic does not name Form 500CRW reason B")

# W6 -- the s.10-305(b) addition, no invented code letter.
check("D_MD500_CAPLOSS_CARRYBACK" in _diag,
      "W6: the s.10-305(b) capital-loss-carryback addition is diagnosed",
      "W6: no diagnostic for the s.10-305(b) addition")
_w6 = _diag.get("D_MD500_CAPLOSS_CARRYBACK", {}).get("message", "")
check("7f" in _w6 and "NO code letter" in _w6 and "attach" in _w6.lower(),
      "W6: it routes to line 7f with NO code letter plus an attached schedule",
      "W6: the placement ruling (7f / no code / attach a schedule) is not stated")

# D2 -- the NEGATIVE as a ruling, with the RIGHT recorded reason.
check("D_MD500_NO_COMBINED" in _diag,
      "D2: the combined-reporting negative is recorded as a ruling",
      "D2: no combined-reporting diagnostic")
_d2 = _diag.get("D_MD500_NO_COMBINED", {}).get("message", "")
check("NO OPERATIVE RULE WAS FOUND" in _d2.upper(),
      "D2: the recorded reason is 'no operative rule found'",
      "D2: the recorded reason is missing")
check("expired" not in _d2.lower().replace("not that any rule expired", ""),
      "D2: the spec does NOT claim any rule expired (the vestigial rationale was withdrawn)",
      "D2: the withdrawn 'the rule expired' rationale has crept back in")

# D5 -- never auto-reweight.
check("D_MD500_NO_DENOMINATOR" in _diag and _diag["D_MD500_NO_DENOMINATOR"]["severity"] == "error",
      "D5: a missing denominator raises a HARD diagnostic",
      "D5: the missing-denominator case is not a hard error")

# D7 -- two mechanisms, different lifespans, s.168(k) never merged with s.168(n).
check("D_MD500_DECOUPLE_LIFESPAN" in _diag,
      "D7: the two decoupling mechanisms are diagnosed separately",
      "D7: no diagnostic separating the two decoupling mechanisms")
_d7 = _diag.get("D_MD500_DECOUPLE_LIFESPAN", {}).get("message", "")
check("168(k)" in _d7 and "168(n)" in _d7 and "NEVER be merged" in _d7,
      "D7: s.168(k) and s.168(n) are explicitly flagged as never-to-be-merged",
      "D7: the s.168(k)/s.168(n) separation warning is missing")
check("TY2026" in _d7 and ("unwind" in _d7 or "RESERVED" in _d7),
      "D7: the TY2026 unwind is recorded on the spec itself",
      "D7: the TY2026 unwind is not recorded")

# W11 -- the two PTE credits stay split.
check("D_MD500_PTE_CREDIT_SPLIT" in _diag,
      "W11: the two PTE credits are diagnosed as distinct",
      "W11: no diagnostic distinguishing the two PTE credits")
check("refundable_credits_ddd" in _facts and "pte_nonresident_tax_paid" in _facts,
      "W11: 15d and 15f are SEPARATE facts, so they cannot be merged upstream",
      "W11: the two PTE credit inputs are not separate facts")

# W10 -- dual filing.
check("D_MD500_DUAL_FILING" in _diag,
      "W10: the dual-filing S corp (500 + 510/511) is diagnosed",
      "W10: no dual-filing diagnostic")
check("23a" in _diag.get("D_MD500_DUAL_FILING", {}).get("message", ""),
      "W10: the diagnostic names the federal 1120-S trigger lines Maryland omits",
      "W10: the 1120-S trigger lines are not named")

# W8 -- line 23 built as printed, support flagged as inferential.
check("INFERENTIAL" in _rules.get("R-MD500-L23", {}).get("description", "").upper(),
      "W8: line 23's support is flagged INFERENTIAL on the spec itself",
      "W8: line 23 does not disclose that its support is inferential")

# U4 / U5 -- carried open, not silently resolved.
check("D_MD500_UNISTATE_GATE" in _diag, "U4: the two-gate divergence is carried, not hidden",
      "U4: the unistate/multistate gate divergence is not recorded")
check("D_MD500_LINE21_U5" in _diag, "U5: the line 20/21 inconsistency is carried, not 'fixed'",
      "U5: the line 20/21 inconsistency is not recorded")

# The inferred zero floor on tax is disclosed as an inference.
check("D_MD500_NEGATIVE_TAXABLE" in _diag,
      "the inferred zero floor on line 14 is disclosed as an INFERENCE, not passed off as printed",
      "the line-14 zero floor is applied without disclosing that Maryland prints no such floor")

# ⚠ G4 -- MD_500 must not have inherited the PTE module's election machinery.
check(not any("510" == f["fact_key"] or "election_511" in f["fact_key"] for f in MD.F_FACTS),
      "G4: no 510/511 election-state facts were ported into the corporate spec",
      "G4: PTE election-state machinery has been cloned into MD_500")
check(all(l["line_number"].startswith("MD500-") for l in MD.F_LINES),
      "G4: every line is MD500-namespaced -- transcribed from the Form 500 face",
      "G4: a line number is not MD500-namespaced (possible sibling-form clone)")

# ======================================================================
# 5. Every RED-defer has its own diagnostic; severities are sane.
# ======================================================================
_valid_sev = {"error", "warning", "info"}
_bad_sev = [(d["diagnostic_id"], d["severity"]) for d in MD.F_DIAGNOSTICS
            if d["severity"] not in _valid_sev]
check(not _bad_sev, "every diagnostic carries a valid severity", f"invalid severities: {_bad_sev}")

_hard = [d["diagnostic_id"] for d in MD.F_DIAGNOSTICS if d["severity"] == "error"]
check(len(_hard) >= 3,
      f"the RED-defers are hard blocks ({len(_hard)}): {', '.join(sorted(_hard))}",
      "too few hard diagnostics -- a RED-defer may have been downgraded")

# Scenario coverage of the branch points that actually matter.
_names = " ".join(s["scenario_name"] for s in MD.F_SCENARIOS)
for needle, why in (("asymmetric", "the line-6 asymmetry"),
                    (".000000", "the zero-factor divergence"),
                    ("denominator", "the no-reweight rule"),
                    ("worldwide", "the worldwide-HQ election"),
                    ("500CR", "the 500CR deferral")):
    check(needle.lower() in _names.lower(),
          f"a scenario covers {why}", f"NO scenario covers {why}")

check(len(MD.F_SCENARIOS) >= 8,
      f"{len(MD.F_SCENARIOS)} test scenarios cover the spine and the edges",
      "too few scenarios")

# ======================================================================
# 6. Report
# ======================================================================
print("\n" + "=" * 74)
if form:
    print(f"  MD_500: facts {FormFact.objects.filter(tax_form=form).count()} / "
          f"rules {FormRule.objects.filter(tax_form=form).count()} / "
          f"lines {FormLine.objects.filter(tax_form=form).count()} / "
          f"diag {FormDiagnostic.objects.filter(tax_form=form).count()} / "
          f"tests {TestScenario.objects.filter(tax_form=form).count()}")
print(f"  flow assertions: {FlowAssertion.objects.filter(assertion_id__startswith='FA-MD500').count()}")
print(f"  authority sources (MD): {AuthoritySource.objects.filter(jurisdiction_code='MD').count()}")
print(f"  rule authority links: {RuleAuthorityLink.objects.count()}")
print("=" * 74)
for pmsg in PASSES:
    print(f"  PASS  {pmsg}")
for fmsg in FAILURES:
    print(f"  FAIL  {fmsg}")
print("=" * 74)
print(f"RESULT: {len(PASSES)} pass / {len(FAILURES)} fail - "
      f"{'ALL PASS' if not FAILURES else 'FAILURES PRESENT'}")
print(f"NOTE: READY_TO_SEED was driven in memory only; on disk it ships {_shipped_ready}.")
print("NOTE: throwaway SQLite only -- test_postgres was never touched.")

from django.db import connections  # noqa: E402
connections.close_all()
try:
    if os.path.exists(SQLITE_PATH):
        os.remove(SQLITE_PATH)
except OSError:
    pass
sys.exit(1 if FAILURES else 0)
