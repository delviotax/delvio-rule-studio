"""Throwaway-SQLite validation for the VA PTE batch: VA_502 + VA_502PTET (TY2025).

Checks, in order:
  0. THE SAFETY GUARD -- the sentinel is driven DOWN and the loader must REFUSE. This pins the
     GUARD MECHANISM, not the sentinel's disk value: a prior harness asserted "ships False" and
     went red the moment the work it validated was approved (campaign D-10).
  1. CharField caps read from the REAL MODEL FIELDS via Django's _meta (rule_id 20 /
     line_number 20 / assertion_id 20 / diagnostic_id 40 / fact_key 100 / topic_name 255 /
     AuthoritySource.citation 255 / issuer 100 / source_code 100, plus the rest). **Postgres
     enforces these; SQLite does NOT** -- six Tier-1 citations overflowed 255 on the last seed
     and Postgres DataError'd. This harness is the only thing standing in the way.
  2. no duplicate rule_id / line_number / fact_key / diagnostic_id / assertion_id;
  3. every FormRule carries >= 1 authority link; rule_links resolve to defined rules and
     declared sources; support levels are valid;
  4. identity -- jurisdiction VA, TY2025, v1, draft, entity_types ["1065","1120S"] on BOTH forms;
  5. ARITHMETIC ORACLES driven through the loader's own helpers:
       * the six module branch points (1065 vs 1120S) as REAL distinctions
       * Form 502 Line 1 (income only) vs 502PTET Section I Line 1 (deductions in, s.179 and
         charitable re-limited at the C-corp level) -- the clone trap
       * the 5.75% PTET rate, the per-column floor, Line 7 = 7a + 7b, credit keyed to 7a
       * the 5% withholding: full-year, part-year day-count proration, per-owner zero floor,
         exemption codes, the safe harbor, the Extension Penalty Worksheet and Line 10's
         four branches
       * apportionment: /4 double-weighted sales and every missing-factor divisor
       * the TWO due-date clocks and the never-extending payment date
       * conformity routing (bonus 8/14, disposed 9(1)/15(1), residual bucket 9(2)/15(2))
       * NO Virginia s.179 figure is seeded, and the OBBBA figures are absent
  6. every RED-defer R1..R16 has its own diagnostic.

ASCII-only output. Run:  poetry run python scratchpad/validate_va.py
"""
import os
import sys

PROJECT_ROOT = r"D:\dev\delvio-rule-studio"
sys.path.insert(0, PROJECT_ROOT)

SQLITE_PATH = os.path.join(PROJECT_ROOT, "scratchpad", "validate_va.sqlite3")
if os.path.exists(SQLITE_PATH):
    os.remove(SQLITE_PATH)
os.environ["DATABASE_URL"] = f"sqlite:///{SQLITE_PATH}"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

import django  # noqa: E402
django.setup()

from django.core.management import call_command  # noqa: E402
from specs.models import (  # noqa: E402
    FlowAssertion, FormDiagnostic, FormFact, FormLine, FormRule, TaxForm, TestScenario,
)
from sources.models import (  # noqa: E402
    AuthorityExcerpt, AuthoritySource, AuthorityTopic, RuleAuthorityLink,
)
from specs.management.commands import load_va_pte as VA  # noqa: E402

FAILURES: list[str] = []
PASSES: list[str] = []


def check(cond, ok, bad):
    (PASSES if cond else FAILURES).append(ok if cond else bad)


def approx(a, b, tol=0.0000005):
    return a is not None and abs(float(a) - float(b)) <= tol


# ======================================================================
# 0. THE SAFETY GUARD -- pin the MECHANISM, not the disk value.
# ======================================================================
_shipped_ready = VA.READY_TO_SEED
check(isinstance(_shipped_ready, bool),
      "SAFETY GUARD: the sentinel is a real bool the harness can drive",
      f"SAFETY GUARD BREACHED: READY_TO_SEED = {_shipped_ready!r} is not a bool")

VA.READY_TO_SEED = False  # force the guard DOWN so the refusal below is a real test

call_command("migrate", run_syncdb=True, verbosity=0)

try:
    call_command("load_va_pte", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: load_va_pte seeded while READY_TO_SEED was False")
except Exception as exc:  # noqa: BLE001
    check("REFUSING TO SEED" in str(exc),
          "Guard REFUSES to seed while READY_TO_SEED is False",
          f"Guard raised the wrong error: {exc!r}")

# The guard must also fire on an emptied content list, independently of the sentinel.
VA.READY_TO_SEED = True
_saved_fa = VA.FLOW_ASSERTIONS
VA.FLOW_ASSERTIONS = []
try:
    call_command("load_va_pte", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE on empty FLOW_ASSERTIONS")
except Exception as exc:  # noqa: BLE001
    check("REFUSING TO SEED" in str(exc),
          "Guard REFUSES to seed hollow content (empty FLOW_ASSERTIONS) even with the sentinel up",
          f"Hollow-seed guard raised the wrong error: {exc!r}")
VA.FLOW_ASSERTIONS = _saved_fa

# Now seed for real, IN MEMORY ONLY (never written back to disk).
try:
    call_command("load_va_pte", verbosity=0)
    PASSES.append("load_va_pte ran + seeded into throwaway SQLite without error")
except Exception as exc:  # noqa: BLE001
    FAILURES.append(f"load_va_pte raised: {exc!r}")
    print("\n".join(f"  FAIL  {f}" for f in FAILURES))
    sys.exit(1)

FORM_SHAPE = {"VA_502": ("VA", ["1065", "1120S"]), "VA_502PTET": ("VA", ["1065", "1120S"])}

# ======================================================================
# 1. CharField caps -- read from the REAL MODEL FIELDS, not hardcoded.
# ======================================================================
def cap(model, field):
    return model._meta.get_field(field).max_length


EXPECTED_CAPS = {
    (FormRule, "rule_id"): 20,
    (FormLine, "line_number"): 20,
    (FlowAssertion, "assertion_id"): 20,
    (FormDiagnostic, "diagnostic_id"): 40,
    (FormFact, "fact_key"): 100,
    (AuthorityTopic, "topic_name"): 255,
    (AuthoritySource, "citation"): 255,
    (AuthoritySource, "issuer"): 100,
    (AuthoritySource, "source_code"): 100,
}
for (model, field), expected in EXPECTED_CAPS.items():
    actual = cap(model, field)
    check(actual == expected,
          f"model cap confirmed: {model.__name__}.{field} = {actual}",
          f"MODEL CAP MOVED: {model.__name__}.{field} = {actual}, harness expected {expected}")

CAPS: dict = {}
for fn in FORM_SHAPE:
    form = TaxForm.objects.get(form_number=fn)
    CAPS[f"form_number={fn}"] = (form.form_number, cap(TaxForm, "form_number"))
    CAPS[f"form_title={fn}"] = (form.form_title, cap(TaxForm, "form_title"))
    CAPS[f"jurisdiction={fn}"] = (form.jurisdiction, cap(TaxForm, "jurisdiction"))
    CAPS[f"status={fn}"] = (form.status, cap(TaxForm, "status"))
    for r in FormRule.objects.filter(tax_form=form):
        CAPS[f"rule_id={fn}:{r.rule_id}"] = (r.rule_id, cap(FormRule, "rule_id"))
        CAPS[f"rule_title={fn}:{r.rule_id}"] = (r.title, cap(FormRule, "title"))
        CAPS[f"rule_type={fn}:{r.rule_id}"] = (r.rule_type, cap(FormRule, "rule_type"))
    for d in FormDiagnostic.objects.filter(tax_form=form):
        CAPS[f"diag_id={fn}:{d.diagnostic_id}"] = (d.diagnostic_id, cap(FormDiagnostic, "diagnostic_id"))
        CAPS[f"diag_title={fn}:{d.diagnostic_id}"] = (d.title, cap(FormDiagnostic, "title"))
        CAPS[f"diag_sev={fn}:{d.diagnostic_id}"] = (d.severity, cap(FormDiagnostic, "severity"))
    for ln in FormLine.objects.filter(tax_form=form):
        CAPS[f"line_number={fn}:{ln.line_number}"] = (ln.line_number, cap(FormLine, "line_number"))
        CAPS[f"line_type={fn}:{ln.line_number}"] = (ln.line_type, cap(FormLine, "line_type"))
    for fct in FormFact.objects.filter(tax_form=form):
        CAPS[f"fact_key={fn}:{fct.fact_key}"] = (fct.fact_key, cap(FormFact, "fact_key"))
        CAPS[f"fact_label={fn}:{fct.fact_key}"] = (fct.label, cap(FormFact, "label"))
        CAPS[f"fact_dtype={fn}:{fct.fact_key}"] = (fct.data_type, cap(FormFact, "data_type"))
    for ts in TestScenario.objects.filter(tax_form=form):
        CAPS[f"scen_name={fn}:{ts.scenario_name[:24]}"] = (ts.scenario_name, cap(TestScenario, "scenario_name"))
        CAPS[f"scen_type={fn}:{ts.scenario_name[:24]}"] = (ts.scenario_type, cap(TestScenario, "scenario_type"))
for fa in FlowAssertion.objects.filter(assertion_id__startswith="FA-VA"):
    CAPS[f"assertion_id={fa.assertion_id}"] = (fa.assertion_id, cap(FlowAssertion, "assertion_id"))
    CAPS[f"assertion_title={fa.assertion_id}"] = (fa.title, cap(FlowAssertion, "title"))
    CAPS[f"assertion_type={fa.assertion_id}"] = (fa.assertion_type, cap(FlowAssertion, "assertion_type"))
for t in AuthorityTopic.objects.all():
    CAPS[f"topic_code={t.topic_code}"] = (t.topic_code, cap(AuthorityTopic, "topic_code"))
    CAPS[f"topic_name={t.topic_code}"] = (t.topic_name, cap(AuthorityTopic, "topic_name"))
for s in AuthoritySource.objects.filter(jurisdiction_code="VA"):
    CAPS[f"source_code={s.source_code}"] = (s.source_code, cap(AuthoritySource, "source_code"))
    CAPS[f"citation={s.source_code}"] = (s.citation or "", cap(AuthoritySource, "citation"))
    CAPS[f"issuer={s.source_code}"] = (s.issuer or "", cap(AuthoritySource, "issuer"))
    CAPS[f"juris_code={s.source_code}"] = (s.jurisdiction_code, cap(AuthoritySource, "jurisdiction_code"))
    CAPS[f"source_type={s.source_code}"] = (s.source_type, cap(AuthoritySource, "source_type"))
    CAPS[f"source_rank={s.source_code}"] = (s.source_rank, cap(AuthoritySource, "source_rank"))
    CAPS[f"status={s.source_code}"] = (s.current_status, cap(AuthoritySource, "current_status"))
    for e in s.excerpts.all():
        CAPS[f"exc_label={(e.excerpt_label or '')[:28]}"] = (e.excerpt_label or "",
                                                             cap(AuthorityExcerpt, "excerpt_label"))

viol = [f"{k}: len {len(v)} > {c}" for k, (v, c) in CAPS.items() if len(v) > c]
check(not viol, f"CharField caps OK ({len(CAPS)} values checked against the real model fields)",
      "CAP VIOLATIONS:\n    " + "\n    ".join(viol))

# The citation cap is the one that DataError'd last seed -- assert it explicitly and loudly.
long_cites = [(s["source_code"], len(s.get("citation") or ""))
              for s in VA.AUTHORITY_SOURCES if len(s.get("citation") or "") > 255]
check(not long_cites, f"every authored citation <= 255 chars ({len(VA.AUTHORITY_SOURCES)} sources)",
      f"CITATION OVERFLOW (Postgres will DataError): {long_cites}")
long_issuers = [(s["source_code"], len(s.get("issuer") or ""))
                for s in VA.AUTHORITY_SOURCES if len(s.get("issuer") or "") > 100]
check(not long_issuers, "every authored issuer <= 100 chars", f"ISSUER OVERFLOW: {long_issuers}")
check(all(len(s["source_code"]) <= 100 for s in VA.AUTHORITY_SOURCES),
      "every source_code <= 100 chars", "source_code > 100 chars present")
check(all(len(r["rule_id"]) <= 20 for s in VA.FORMS for r in s["rules"]),
      "every authored rule_id <= 20 chars", "rule_id > 20 chars present")
check(all(len(d["diagnostic_id"]) <= 40 for s in VA.FORMS for d in s["diagnostics"]),
      "every authored diagnostic_id <= 40 chars", "diagnostic_id > 40 chars present")
check(all(len(ln["line_number"]) <= 20 for s in VA.FORMS for ln in s["lines"]),
      "every authored line_number <= 20 chars", "line_number > 20 chars present")
check(all(len(f["fact_key"]) <= 100 for s in VA.FORMS for f in s["facts"]),
      "every authored fact_key <= 100 chars", "fact_key > 100 chars present")
check(all(len(a["assertion_id"]) <= 20 for a in VA.FLOW_ASSERTIONS),
      "every authored assertion_id <= 20 chars", "assertion_id > 20 chars present")
check(all(len(t[1]) <= 255 for t in VA.AUTHORITY_TOPICS),
      "every topic_name <= 255 chars", "topic_name > 255 chars present")

# ======================================================================
# 2/3. Duplicates, authority links, resolvable references.
# ======================================================================
declared_sources = {s["source_code"] for s in VA.AUTHORITY_SOURCES} | set(VA.EXISTING_SOURCES_TO_REFERENCE)
for spec in VA.FORMS:
    fn = spec["identity"]["form_number"]
    form = TaxForm.objects.get(form_number=fn)
    for key, field in (("facts", "fact_key"), ("rules", "rule_id"),
                       ("lines", "line_number"), ("diagnostics", "diagnostic_id")):
        ids = [row[field] for row in spec[key]]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        check(not dupes, f"{fn}: no duplicate {field} ({len(ids)} rows)",
              f"{fn}: DUPLICATE {field}: {dupes}")
    names = [t["scenario_name"] for t in spec["scenarios"]]
    check(len(names) == len(set(names)), f"{fn}: no duplicate scenario_name",
          f"{fn}: duplicate scenario_name")

    ruleless = [r.rule_id for r in FormRule.objects.filter(tax_form=form)
                if not RuleAuthorityLink.objects.filter(form_rule=r).exists()]
    check(not ruleless,
          f"{fn}: all {FormRule.objects.filter(tax_form=form).count()} rules have >= 1 authority link",
          f"{fn}: rules with NO authority link: {ruleless}")

    defined = {r["rule_id"] for r in spec["rules"]}
    linked = {rl[0] for rl in spec["rule_links"]}
    check(not (linked - defined), f"{fn}: rule_links reference defined rules",
          f"{fn}: orphan rule_links {sorted(linked - defined)}")
    check(not (defined - linked), f"{fn}: every rule appears in rule_links",
          f"{fn}: unlinked rules {sorted(defined - linked)}")
    bad_src = {rl[1] for rl in spec["rule_links"]} - declared_sources
    check(not bad_src, f"{fn}: rule_links reference declared sources",
          f"{fn}: undeclared sources {sorted(bad_src)}")
    bad_lvl = {rl[2] for rl in spec["rule_links"]} - {"primary", "secondary", "interpretive", "implementation"}
    check(not bad_lvl, f"{fn}: rule_link support levels valid", f"{fn}: bad support levels {bad_lvl}")

    # Every line that names a source_rule must name a rule that exists on this form.
    named = {rid for ln in spec["lines"] for rid in ln.get("source_rules", [])}
    check(not (named - defined), f"{fn}: every line source_rule resolves to a defined rule",
          f"{fn}: lines reference undefined rules {sorted(named - defined)}")
    # Every line that names a source_fact must name a fact that exists on this form.
    fact_keys = {f["fact_key"] for f in spec["facts"]}
    named_facts = {k for ln in spec["lines"] for k in ln.get("source_facts", [])}
    check(not (named_facts - fact_keys), f"{fn}: every line source_fact resolves to a defined fact",
          f"{fn}: lines reference undefined facts {sorted(named_facts - fact_keys)}")

fa_ids = [a["assertion_id"] for a in VA.FLOW_ASSERTIONS]
check(len(fa_ids) == len(set(fa_ids)), "no duplicate assertion_id", "DUPLICATE assertion_id present")
all_diag = [d["diagnostic_id"] for s in VA.FORMS for d in s["diagnostics"]]
check(len(all_diag) == len(set(all_diag)),
      "no duplicate diagnostic_id ACROSS both forms (the per-form prefixes hold)",
      "duplicate diagnostic_id across forms")
bad_form_links = {fl[1] for fl in VA.AUTHORITY_FORM_LINKS} - set(FORM_SHAPE)
check(not bad_form_links, "AUTHORITY_FORM_LINKS point only at VA_502 / VA_502PTET",
      f"bad form codes: {sorted(bad_form_links)}")

# ======================================================================
# 4. Identity.
# ======================================================================
check(VA.FORM_JURISDICTION == "VA", "FORM_JURISDICTION = VA", f"wrong jurisdiction {VA.FORM_JURISDICTION!r}")
check(VA.FORM_TAX_YEAR == 2025, "FORM_TAX_YEAR = 2025", f"wrong tax year {VA.FORM_TAX_YEAR}")
check(VA.FORM_VERSION == 1 and VA.FORM_STATUS == "draft",
      "FORM_VERSION = 1, FORM_STATUS = draft", "wrong version/status")
check(VA.FORM_ENTITY_TYPES == ["1065", "1120S"],
      "FORM_ENTITY_TYPES = ['1065','1120S'] -- S corps are PTEs for Virginia purposes",
      f"entity types wrong: {VA.FORM_ENTITY_TYPES}")
for fn, (juris, ets) in FORM_SHAPE.items():
    form = TaxForm.objects.get(form_number=fn)
    check(form.jurisdiction == juris, f"{fn}: jurisdiction = {juris}", f"{fn}: jurisdiction {form.jurisdiction!r}")
    check(form.tax_year == 2025, f"{fn}: tax_year = 2025", f"{fn}: tax_year {form.tax_year}")
    check(form.entity_types == ets, f"{fn}: entity_types = {ets} (ONE spec, BOTH modules)",
          f"{fn}: entity_types {form.entity_types}")
    check(form.status == "draft", f"{fn}: status = draft", f"{fn}: status {form.status!r}")
check("VA_CODE_58_1_301" in VA.EXISTING_SOURCES_TO_REFERENCE,
      "EXISTING_SOURCES_TO_REFERENCE anchors the seeded VA conformity row VA_CODE_58_1_301",
      f"VA conformity anchor missing: {VA.EXISTING_SOURCES_TO_REFERENCE}")
check("VA_TB_26_1" in VA.EXISTING_SOURCES_TO_REFERENCE,
      "EXISTING_SOURCES_TO_REFERENCE also anchors VA_TB_26_1 (the operative DOR guidance)",
      f"TB 26-1 anchor missing: {VA.EXISTING_SOURCES_TO_REFERENCE}")
# The anchors must be REAL source_codes declared in the Tier-1 conformity batch, not invented
# names. On this throwaway DB they legitimately warn "NOT FOUND" (that batch is not loaded here);
# in prod the VA rows are seeded, so no warning is expected there. Prove the NAMES exist.
try:
    from specs.management.commands import _state_conformity_tier1 as T1  # noqa: E402
    t1_codes = {row["source_code"] for row in getattr(T1, "AUTHORITY_SOURCES", [])}
    if not t1_codes:  # the module may name the list differently; fall back to a text scan
        import inspect
        t1_src = inspect.getsource(T1)
        t1_codes = {c for c in ("VA_CODE_58_1_301", "VA_TB_26_1") if f"'{c}'" in t1_src}
    missing_anchor = [c for c in VA.EXISTING_SOURCES_TO_REFERENCE if c not in t1_codes]
    check(not missing_anchor,
          "both conformity anchors are REAL source_codes declared in _state_conformity_tier1",
          f"anchors not found in the Tier-1 batch: {missing_anchor}")
except Exception as exc:  # noqa: BLE001
    FAILURES.append(f"could not verify the conformity anchors against _state_conformity_tier1: {exc!r}")

# ======================================================================
# 5. ARITHMETIC ORACLES
# ======================================================================

# ---- 5a. The six module branch points -- REAL distinctions, not a copy ----
p, s = VA._va_module_branch("1065"), VA._va_module_branch("1120S")
check(s["entity_type_codes"] == ("SC",) and "SC" not in p["entity_type_codes"],
      "branch 1: entity type code SC for 1120S; PG/PL/LL/LP/NZ/OB for 1065", "branch 1 wrong")
check("1065" in p["owner_count_source"] and "1120-S" in s["owner_count_source"]
      and "SHAREHOLDERS" in s["owner_count_source"],
      "branch 2: owner count off Form 1065 item I vs Form 1120-S item I (same letter, different meaning)",
      f"branch 2 wrong: {p['owner_count_source']} / {s['owner_count_source']}")
check("item J" in p["participation_pct_source"] and "ENDING PROFIT" in p["participation_pct_source"]
      and "item G" in s["participation_pct_source"] and "AS PRINTED" in s["participation_pct_source"],
      "branch 3: 1065 K-1 item J ending profit % vs 1120-S K-1 item G AS PRINTED (C7)",
      "branch 3 wrong")
check(s["participation_type_codes"] == ("SHR",) and "SHR" not in p["participation_type_codes"],
      "branch 4: participation type SHR for 1120S; GPT/LPT/LLM/OTR for 1065", "branch 4 wrong")
check(p["federal_enclosure"].startswith("Form 1065") and s["federal_enclosure"].startswith("Form 1120-S"),
      "branch 5: federal enclosure differs by module (no K-1, no K-2/K-3 either way)", "branch 5 wrong")
check(s["bank_franchise_branch"] is True and p["bank_franchise_branch"] is False,
      "branch 6: the Bank Franchise Tax consequence is S-CORP ONLY", "branch 6 wrong")
check(s["scorp_all_nonresident_option_502ptet"] is True
      and p["scorp_all_nonresident_option_502ptet"] is False,
      "502PTET-only: the all-nonresident computation option is S-corp only (U9)",
      "S-corp all-nonresident option wrong")
check(p["form_502fed1_path"] is True and s["form_502fed1_path"] is False,
      "Form 502FED-1 / 502FED-2 is a PARTNERSHIP-ONLY path (R6/W11)", "502FED-1 path wrong")
check(p != s, "the two module branches are genuinely different objects, not a copy",
      "MODULE BRANCH IS A COPY -- the six divergences were not encoded")
try:
    VA._va_module_branch("1120")
    FAILURES.append("module branch accepted an invalid module ('1120')")
except ValueError:
    PASSES.append("module branch rejects a module that is not 1065 or 1120S")

# ---- 5b. THE BASE DIVERGENCE -- Form 502 L1 vs 502PTET Section I L1 ----
wks = {"wk_ordinary_income": 1000000}
l1_502 = VA._va_502_line1(wks)
check(approx(l1_502, 1000000.0), "Form 502 Line 1 = 1,000,000 (income only)", f"502 L1 wrong: {l1_502}")
ptet_l1 = VA._va_ptet_section_i_line1(1000000, 150000, 100000, 60000, 50000, 30000, 1.0)
check(approx(ptet_l1, 910000.0),
      "502PTET Sec I L1 = 910,000 -- deductions IN, s.179 100k->60k and charitable 50k->30k at C-corp limits",
      f"PTET base wrong: {ptet_l1}")
check(not approx(ptet_l1, l1_502),
      "THE CLONE TRAP: the two bases differ on identical facts", "BASE CLONE: 502 L1 == PTET Sec I L1")
check(approx(VA._va_ptet_section_i_line1(1000000, 150000, 100000, 60000, 50000, 30000, 0.60), 546000.0),
      "PTET base narrows by the eligible owners' participation share (60% -> 546,000)",
      "eligible-owner narrowing wrong")
check(approx(VA._va_502_line1({"wk_ordinary_income": 400000, "wk_interest": 25000}), 425000.0),
      "Line 1 sums the eleven worksheet categories and is NOT reduced by Line 2 deductions",
      "Line 1 worksheet sum wrong")
check(len(VA.VA_L1_WORKSHEET_KEYS) == 11,
      "the Line 1 worksheet carries all ELEVEN income categories (worksheet line 12 is the VA total)",
      f"worksheet key count wrong: {len(VA.VA_L1_WORKSHEET_KEYS)}")

# ---- 5c. The PTET rate, the per-column floor, 7a vs 7 ----
check(VA._yk(VA.VA_PTET_RATE) == "0.0575", "PTET rate constant is 5.75%", "PTET rate constant wrong")
col_a = VA._va_ptet_section_i_column(500000, 20000, 0)
col_b = VA._va_ptet_section_i_column(-100000, 0, 50000)
check(approx(col_a["L5"], 520000.0), "Section I Col A L5 = 520,000", f"col A wrong: {col_a}")
check(approx(col_b["L5"], 0.0),
      "Section I Col B L5 FLOORS AT ZERO (-150,000 -> 0) -- the floor is PER COLUMN",
      f"col B floor wrong: {col_b}")
l6 = VA._va_ptet_line6(col_a["L5"], col_b["L5"])
check(approx(l6, 520000.0),
      "Line 6 = 520,000 -- the resident-column loss CANNOT offset nonresident-column income",
      f"L6 wrong: {l6}")
check(approx(VA._va_ptet_line6(-10, -20), 0.0), "Line 6 floors again after summing the two columns",
      "L6 second floor wrong")
l7a = VA._va_ptet_line7a(l6)
check(approx(l7a, 29900.0), "Line 7a = 520,000 x 5.75% = 29,900", f"L7a wrong: {l7a}")
l7b = VA._va_ptet_line7b(200000)
check(approx(l7b, 10000.0), "Line 7b = 200,000 x 5% (W4 -- INFERRED from s.58.1-486.2, not the package)",
      f"L7b wrong: {l7b}")
check(approx(VA._va_ptet_line7(l7a, l7b), 39900.0), "Line 7 = 7a + 7b = 39,900", "L7 wrong")
check(approx(VA._va_ptet_credit_to_owners(l7a), 29900.0),
      "the PTET credit to owners is keyed to LINE 7a (29,900), NOT Line 7 (39,900)",
      "PTET credit keyed to the wrong line")
check(not approx(VA._va_ptet_credit_to_owners(l7a), 39900.0),
      "the corporate withholding leg is EXCLUDED from the owner credit",
      "corporate withholding leaked into the owner credit")
check(VA._yk(VA.VA_PTET_OWNER_CREDIT_REFUNDABLE) is True,
      "the owner-side PTET credit is REFUNDABLE (s.58.1-390.3 E)", "owner credit refundability wrong")

# ---- 5d. PTET election, estimates, penalties, sunset ----
check(VA._va_ptet_estimates_required(40000) is True and VA._va_ptet_estimates_required(1000) is False,
      "estimates required only when the PTET is expected to EXCEED $1,000 (exactly 1,000 does not)",
      "estimate threshold wrong")
check(approx(VA._va_ptet_installment(40000), 10000.0), "four 25% instalments: 40,000 -> 10,000 each",
      "instalment wrong")
check(VA._yk(VA.VA_PTET_ESTIMATE_DATES_CY) == ("04-15", "06-15", "09-15", "12-15"),
      "calendar-year instalment dates Apr 15 / Jun 15 / Sep 15 / Dec 15", "instalment dates wrong")
check(approx(VA._va_ptet_late_filing_penalty(0), 100.0),
      "late filing penalty has a $100 MINIMUM that applies whether or not tax is due",
      "the $100 minimum did not apply on zero tax")
check(approx(VA._va_ptet_late_filing_penalty(10000), 3000.0),
      "late filing penalty = 30% of tax due (10,000 -> 3,000)", "30% late filing penalty wrong")
check(VA._va_ptet_election_permitted(8, False) is False,
      "the 6-MONTH HARD BAR refuses Form 502PTET at 8 months with no payment", "hard bar did not fire")
check(VA._va_ptet_election_permitted(8, True) is True,
      "an estimated or extension payment rescues the election past the 6-month bar (U5)",
      "hard bar escape wrong")
check(VA._va_ptet_election_permitted(6, False) is True,
      "at exactly 6 months the bar has not yet fallen", "hard bar boundary wrong")
check(VA._va_ptet_sunset_year() is None,
      "NO PTET SUNSET IS ENCODED -- the statute has none (U4); build to the statute",
      f"A SUNSET WAS ENCODED: {VA._va_ptet_sunset_year()}")
check(VA._yk(VA.VA_PTET_STALE_SUNSET_RECITALS) == 6,
      "the re-issued Rev. 08/26 package's stale sunset recitals are recorded as SIX (correction C2)",
      "stale sunset recital count wrong")
check(VA._va_ptet_may_file_765() is False,
      "an electing PTET entity may NOT file Form 765", "Form 765 mutual exclusivity wrong")

# ---- 5e. The withholding computation ----
check(approx(VA._va_wh_owner_tax(200000), 10000.0),
      "withholding: 200,000 x 5% = 10,000 for a full-year nonresident owner", "5% withholding wrong")
check(approx(VA._va_wh_owner_tax(200000, days_nonresident=146), 4000.0),
      "part-year proration: 200,000 x 146/365 = 80,000, x 5% = 4,000", "day-count proration wrong")
check(approx(VA._va_wh_owner_tax(200000, credits_passed_through=12000), 0.0),
      "credits float the owner to ZERO, never negative -- the floor is PER OWNER",
      "per-owner zero floor wrong")
check(approx(VA._va_wh_owner_tax(200000, credits_passed_through=4000), 6000.0),
      "credits below the liability pass through (10,000 - 4,000 = 6,000)", "credit offset wrong")
check(approx(VA._va_wh_owner_tax(200000, exemption_code="03"), 0.0),
      "an owner exemption code suppresses withholding for that owner", "exemption code wrong")
check(approx(VA._va_wh_owner_tax(200000, is_nonresident=False), 0.0),
      "no withholding for a resident owner", "resident owner withholding wrong")
total = VA._va_wh_line1([
    {"va_source_share": 200000},
    {"va_source_share": 200000, "days_nonresident": 146},
    {"va_source_share": 200000, "credits_passed_through": 12000},
])
check(approx(total, 14000.0),
      "Page 2 Line 1 = 10,000 + 4,000 + 0 = 14,000 (floors applied PER OWNER before summing)",
      f"P2 L1 total wrong: {total}")
check(not approx(total, 12000.0),
      "an over-credited owner does NOT reduce another owner's withholding",
      "the zero floor was applied to the entity total instead of per owner")
check(VA._yk(VA.VA_NR_WITHHOLDING_RATE) == "0.05", "withholding rate constant is 5%", "withholding rate wrong")
check(set(VA.VA_ENTITY_EXEMPTION_CODES).issubset(set(VA.VA_OWNER_EXEMPTION_CODES))
      and len(VA.VA_OWNER_EXEMPTION_CODES) > len(VA.VA_ENTITY_EXEMPTION_CODES),
      "the entity exemption codes are a strict SUBSET of the owner codes (Line d vs VK-1 Line f)",
      "exemption code sets wrong")
check(approx(VA._va_wh_safe_harbor(20000, 15000, True, True), 15000.0),
      "safe harbor = lesser of 90% current (18,000) and 100% prior (15,000) = 15,000",
      "safe harbor wrong")
check(approx(VA._va_wh_safe_harbor(20000, 15000, False, True), 18000.0),
      "a prior year shorter than 12 months removes the prior-year leg -> 18,000", "safe harbor proviso 1 wrong")
check(approx(VA._va_wh_safe_harbor(20000, 15000, True, False), 18000.0),
      "a prior year with no withholding liability removes the prior-year leg -> 18,000",
      "safe harbor proviso 2 wrong")
check(VA._va_withhold_for_owner_pte(False) is False and VA._va_withhold_for_owner_pte(True) is True,
      "R10: do NOT withhold on a nonresident owner PTE unless it notified you it will not file",
      "anti-cascade rule wrong")

# ---- 5f. Withholding penalties and Line 10's four branches ----
check(VA._va_wh_ext_penalty_applies(10000, 1500) is True,
      "extension penalty applies when the Line 4 balance exceeds 10% of Line 1", "ext penalty threshold wrong")
check(VA._va_wh_ext_penalty_applies(10000, 900) is False,
      "no extension penalty when at least 90% of Line 1 was paid timely (one test, not two)",
      "ext penalty 90%/10% equivalence wrong")
check(approx(VA._va_wh_ext_penalty(10000, 45), 400.0),
      "Extension Penalty Worksheet: ceil(45/30) = 2 months x 2% = 4%; 10,000 x 4% = 400",
      f"ext penalty wrong: {VA._va_wh_ext_penalty(10000, 45)}")
check(approx(VA._va_wh_ext_penalty(10000, 31), 400.0),
      "31 days ROUNDS UP to 2 full 30-day months", "30-day round-up wrong")
check(approx(VA._va_wh_ext_penalty(10000, 200), 1200.0),
      "7 months would be 14% -- CAPPED at 12% = 1,200", "12% cap wrong")
check(approx(VA._va_wh_ext_penalty(0, 200), 0.0), "no balance due -> no extension penalty", "ext penalty zero wrong")
check(approx(VA._va_wh_line6(10000, True), 3000.0), "Page 2 Line 6 = 30% of Line 4", "L6 wrong")
check(approx(VA._va_wh_line6(10000, False), 0.0), "Line 6 does not apply within 6 months", "L6 gating wrong")
check(approx(VA._va_wh_line9(True, False), 1200.0) and approx(VA._va_wh_line9(False, True), 1200.0),
      "Page 2 Line 9 is a FLAT $1,200, on either late-filing trigger", "L9 wrong")
check(approx(VA._va_wh_line9(False, False), 0.0), "no late filing -> no $1,200", "L9 gating wrong")
check(VA._va_wh_penalties_mutually_exclusive(400, 0) and not VA._va_wh_penalties_mutually_exclusive(400, 3000),
      "Lines 5 and 6 are MUTUALLY EXCLUSIVE", "L5/L6 exclusivity wrong")
check(approx(VA._va_wh_line15(3000, 1200), 3000.0), "Line 15 takes the GREATER of Line 6 or Line 9",
      "L15 greater-of wrong")
check(approx(VA._va_wh_line15(0, 1200), 1200.0), "Line 15 falls back to Line 9 when Line 6 is zero",
      "L15 fallback wrong")
check(VA._va_wh_line10(5000, 0, 100, 6000, 0) is None,
      "Line 10 BRANCH 1 (L8 > L3): exit to Line 13, returns None -- NOT zero", "L10 branch 1 wrong")
check(VA._va_wh_line10(5000, 0, 100, 100, 6000) is None,
      "Line 10 BRANCH 1 also fires when L9 exceeds L3", "L10 branch 1 (L9) wrong")
check(approx(VA._va_wh_line10(5000, 1200, 100, 100, 0), 4900.0),
      "Line 10 BRANCH 2 (L6 > L9): L3 - L8 = 4,900", "L10 branch 2 wrong")
check(approx(VA._va_wh_line10(5000, 0, 100, 100, 1200), 3700.0),
      "Line 10 BRANCH 3 (L9 > L6): L3 - (L7 + L9) = 3,700", "L10 branch 3 wrong")
check(approx(VA._va_wh_line10(5000, 0, 100, 100, 0), 5000.0),
      "Line 10 BRANCH 4 (otherwise): the Line 3 overpayment carries through", "L10 branch 4 wrong")
check(approx(VA._va_wh_line13(0, 10000, 400, 0, 0), 10400.0),
      "Line 13 = Line 4 + Line 5 where tax is due", "L13 wrong")
check(approx(VA._va_wh_line13(5000, 0, 400, 6000, 0), -4600.0),
      "Line 13 = Line 5 - Line 3 on the overpayment-consumed branch", "L13 overpayment branch wrong")
check(approx(VA._va_wh_line16(10400, 250, 3000), 13650.0), "Line 16 = L13 + L14 + L15", "L16 wrong")
r = VA._va_wh_line20_21(13650, 5000)
check(approx(r["L20_amount_due"], 8650.0) and approx(r["L21_refund"], 0.0),
      "Line 20 amount due = L16 - L17 (Motion Picture credit)", "L20 wrong")
r2 = VA._va_wh_line20_21(1000, 5000, l12=250)
check(approx(r2["L21_refund"], 4250.0),
      "Line 21 refund = (L17 - L16) + Line 12 when there is an amount on Line 12", "L21 wrong")

# ---- 5g. Apportionment ----
full = VA._va_apportionment_pct((200000, 1000000), (300000, 1000000), (400000, 2000000))
check(approx(full, 0.225),
      "/4 double-weighted sales: (0.20 + 0.30 + 2x0.20) / 4 = 0.225", f"apportionment wrong: {full}")
no_sales = VA._va_apportionment_pct((200000, 1000000), (300000, 1000000), (0, 0))
check(approx(no_sales, 0.25),
      "no SALES denominator: 0.50 / 2 = 0.25 (the divisor drops by the sales factor's DOUBLE weight)",
      f"sales-missing divisor wrong: {no_sales}")
check(not approx(no_sales, 0.166667),
      "the sales-missing divisor is NOT 3 -- counting sales as one factor would be wrong",
      "sales-missing divisor counted sales at single weight")
no_prop = VA._va_apportionment_pct((0, 0), (300000, 1000000), (400000, 2000000))
check(approx(no_prop, 0.233333),
      "no PROPERTY denominator: (0.30 + 0.40) / 3 = 0.233333", f"property-missing wrong: {no_prop}")
no_pay = VA._va_apportionment_pct((200000, 1000000), (0, 0), (400000, 2000000))
check(approx(no_pay, 0.2), "no PAYROLL denominator: (0.20 + 0.40) / 3 = 0.20", f"payroll-missing wrong: {no_pay}")
only_sales = VA._va_apportionment_pct((0, 0), (0, 0), (400000, 2000000))
check(approx(only_sales, 0.2), "sales only: 0.40 / 2 = 0.20", f"sales-only wrong: {only_sales}")
check(VA._va_apportionment_pct((0, 0), (0, 0), (0, 0)) is None,
      "no factor has a denominator -> no apportionment percentage exists (None)", "all-zero case wrong")
check(VA._yk(VA.VA_APPORT_WEIGHTS) == {"property": 1, "payroll": 1, "sales": 2}
      and VA._yk(VA.VA_APPORT_DIVISOR) == 4,
      "weights are property 1 / payroll 1 / sales 2, divisor 4 -- NOT single sales factor",
      "apportionment weights wrong")
pn, pd = VA._va_property_factor(100000, 300000, 1000000, 1000000, rent_va=5000, rent_ew=20000)
check(approx(pn, 240000.0) and approx(pd, 1160000.0),
      "property factor: (100k+300k)/2 + 8x5,000 = 240,000 over (1m+1m)/2 + 8x20,000 = 1,160,000",
      f"property factor wrong: {pn}/{pd}")
check(VA._yk(VA.VA_RENT_MULTIPLIER) == 8, "rented property enters the property factor at 8x annual rent",
      "rent multiplier wrong")
check(VA._yk(VA.VA_MARKET_SOURCING_GENERAL) is False and VA._yk(VA.VA_THROWBACK_RULE) is False,
      "non-TPP sales are COST OF PERFORMANCE, and there is no throwback/throwout rule",
      "sourcing constants wrong")
sc = VA._va_502a_section_c(1000000, 50000, 30000, 10000, False)
check(approx(sc["502_L5"], 70000.0) and approx(sc["502_L6"], 930000.0) and approx(sc["502_L4"], 0.0),
      "502A Sec C, domicile OUTSIDE VA: L5 = (50k+30k)-10k = 70,000; L6 = 1,000,000 - 70,000 = 930,000",
      f"Section C (non-domiciled) wrong: {sc}")
sc2 = VA._va_502a_section_c(1000000, 50000, 0, 0, True)
check(approx(sc2["502_L4"], 50000.0) and approx(sc2["502_L6"], 950000.0) and approx(sc2["502_L5"], 0.0),
      "502A Sec C, domicile IN VA: dividends go to L4 and L6 = L1 - L2 = 950,000",
      f"Section C (domiciled) wrong: {sc2}")
sp = VA._va_wholly_virginia_shortpath(425000)
check(sp["502_L4"] is None and sp["502_L5"] is None
      and approx(sp["502_L6"], 425000.0) and approx(sp["502_L7"], 1.00),
      "wholly-Virginia short path: L4/L5 BLANK, L6 = L1, L7 = 100%, Schedule 502A skipped",
      f"short path wrong: {sp}")

# ---- 5h. The two due-date clocks ----
check(VA._va_due_month_day("VA_502") == (4, 15) and VA._va_due_month_day("VA_502PTET") == (4, 15),
      "entity clock: the 15th day of the 4th month (Va. Code s.58.1-392 A)", "entity due date wrong")
check(VA._va_due_month_day("VA_760") == (5, 1) and VA._va_due_month_day("VA_770") == (5, 1),
      "individual/fiduciary clock: MAY 1 for Form 760 and Form 770", "May 1 clock wrong")
check(VA._va_due_dates_conflated("VA_502", "VA_760") is False,
      "W10: the two clocks are DIFFERENT -- a single Virginia due-date constant would be wrong",
      "DUE DATES CONFLATED: the entity and individual clocks came out equal")
check(VA._va_due_dates_conflated("VA_502", "VA_502PTET") is True,
      "both entity returns share the same clock", "entity clocks disagree with each other")
check(VA._va_payment_due_extends() is False,
      "the extension NEVER extends the payment date (s.58.1-486.2 D.2)", "payment date extends -- wrong")
check(VA._yk(VA.VA_EXTENSION_MONTHS) == 6 and VA._yk(VA.VA_EXTENSION_FED_PLUS_DAYS) == 30,
      "automatic extension: 6 months, or 30 days after the federal extended due date, whichever is later",
      "extension constants wrong")

# ---- 5i. Conformity routing, and NO Virginia s.179 figure ----
check(VA._va_conformity_line("bonus_depreciation_recompute") == "8/14",
      "bonus depreciation recompute routes to Lines 8 / 14 (scoped 2001-2025)", "bonus routing wrong")
check(VA._va_conformity_line("bonus_disposed_asset_trueup") == "9(1)/15(1)",
      "the disposed-asset basis true-up routes to Lines 9(1) / 15(1)", "disposed-asset routing wrong")
for member in VA.VA_CONFORMITY_BUCKET_MEMBERS:
    check(VA._va_conformity_line(member) == "9(2)/15(2)",
          f"bucket member routes to Lines 9(2)/15(2): {member[:52]}",
          f"bucket routing wrong for {member!r}")
check(VA._va_conformity_bucket_is_wider_than_hr1() is True,
      "C1: the Lines 9(2)/15(2) bucket is WIDER THAN H.R.1 -- not an 'H.R.1 line'",
      "the bucket was encoded as H.R.1-only")
check(len(VA.VA_CONFORMITY_BUCKET_MEMBERS) == 8 and VA._yk(VA.VA_BUCKET_EXCLUDES_BONUS) is True,
      "the bucket has 8 members and EXCLUDES bonus depreciation (the word 'other' does that work)",
      f"bucket membership wrong: {len(VA.VA_CONFORMITY_BUCKET_MEMBERS)}")
lim = VA._va_179_limits()
check(lim["virginia_published"] is None,
      "*** VIRGINIA PUBLISHES NO s.179 FIGURE -- none is seeded (W3/U2) ***",
      f"A VIRGINIA s.179 FIGURE WAS SEEDED: {lim['virginia_published']!r}")
check(VA._yk(VA.VA_179_PUBLISHED) is None, "VA_179_PUBLISHED[2025] is None by design",
      "VA_179_PUBLISHED is not None")
check(lim["derived_not_va_sourced"]["limit"] == 1250000
      and lim["derived_not_va_sourced"]["phaseout"] == 3130000
      and lim["derived_not_va_sourced"]["suv_sublimit"] == 31300,
      "the DERIVED reference figures are 1,250,000 / 3,130,000 / 31,300 (Rev. Proc. 2024-40 s.3.25)",
      f"derived figures wrong: {lim['derived_not_va_sourced']}")
check("NOT a Virginia source" in lim["derived_not_va_sourced"]["provenance"],
      "the derived figures carry their non-Virginia provenance inline",
      "derived figures lack a provenance marker")
check(lim["derived_not_va_sourced"]["limit"] != 2500000
      and lim["derived_not_va_sourced"]["phaseout"] != 4000000,
      "the federal OBBBA 2,500,000 / 4,000,000 figures are NOT used for Virginia",
      "OBBBA s.179 figures leaked into the Virginia values")
check(VA._yk(VA.VA_CONFORMITY_DATE) == "2025-12-31" and VA._yk(VA.VA_OBBBA_IN) is True,
      "fixed conformity date 12/31/2025, so OBBBA IS IN the Virginia base for TY2025",
      "conformity date/posture wrong")
check(VA._yk(VA.VA_BONUS_CONFORMS) is False and VA._yk(VA.VA_BONUS_VINTAGE_WINDOW) == (2001, 2025),
      "Virginia does not conform to s.168(k); the bonus recompute window is 2001-2025",
      "bonus conformity constants wrong")
check(VA._yk(VA.VA_BUSINESS_INTEREST_PCT) == "0.20" and VA.VA_BUSINESS_INTEREST_PCT[2024] == "0.50",
      "the business interest subtraction drops from 50% (TY2024) to 20% (TY2025)",
      "business interest percentages wrong")

# ---- 5j. Credit totals, allocation classes, filing gates ----
part1 = {n: 1000 for n in range(1, 28)}
check(approx(VA._va_credit_part2_total(part1), 18000.0),
      "Part II total ENUMERATES 18 slots and skips the nine Reserved ones (C4)",
      f"Part II total wrong: {VA._va_credit_part2_total(part1)}")
for res in VA.VA_CREDIT_PART1_RESERVED:
    check(res not in VA.VA_CREDIT_PART2_SUMMANDS,
          f"Reserved slot {res} is excluded from the Part II total", f"Reserved slot {res} leaked in")
p3 = {1: 100, 7: 200, 9: 300, 10: 400}
check(approx(VA._va_credit_part4_total(p3, is_ptet=False), 600.0),
      "Schedule 502ADJ Part IV = Lines 1 + 7 + 9 = 600 (NO Line 10)", "502ADJ Part IV wrong")
check(approx(VA._va_credit_part4_total(p3, is_ptet=True), 1000.0),
      "Schedule PTET ADJ Part IV = Lines 1 + 7 + 9 + 10 = 1,000", "PTET ADJ Part IV wrong")
check(VA._va_credit_allocation_class(13) == "mutual_agreement_allowed"
      and VA._va_credit_allocation_class(2) == "pro_rata_required",
      "two allocation classes preserved: 5 credits may be allocated as the owners mutually agree",
      "credit allocation classes wrong")
check(len(VA.VA_CREDITS_FREE_ALLOCATION) == 5 and VA._yk(VA.VA_CREDITS_PRO_RATA_COUNT) == 16,
      "FIVE free-allocation credits and SIXTEEN strictly pro-rata credits", "allocation counts wrong")
check(VA._yk(VA.VA_PTE_COMPUTES_CARRYOVERS) is False,
      "'Pass-through entities do not use or compute credit carryovers'", "carryover flag wrong")
check(len(VA.VA_ADJ_ADDITION_CODES) == 10 and len(VA.VA_ADJ_SUBTRACTION_CODES) == 20,
      "C3: TEN addition codes and TWENTY subtraction codes (not the 22/19 the brief body said)",
      f"code counts wrong: {len(VA.VA_ADJ_ADDITION_CODES)}/{len(VA.VA_ADJ_SUBTRACTION_CODES)}")
check(VA._va_files_form_502(is_single_member_disregarded_llc=True) is False,
      "a disregarded single-member LLC does NOT file Form 502 (opposite of the TN J2 trap)",
      "single-member LLC gate wrong")
check(VA._va_files_form_502(is_investment_only_pte=True) is False,
      "an investment-only PTE does NOT file Form 502", "investment PTE gate wrong")
check(VA._va_files_form_502() is True, "an ordinary PTE doing business in Virginia files Form 502",
      "ordinary filing gate wrong")
ez_base = dict(all_business_in_va=True, all_income_va_source=True, commercial_domicile_va=True,
               owner_count=5, files_form_500=False, files_schedule_502a=False, is_500hs_provider=False,
               passes_schedule_cr_credits=False, has_conformity_modifications=False,
               total_taxable_income=30000, total_modifications=500,
               amending_for_fed_adjustment=False, electing_ptet=False)
check(VA._va_502ez_eligible(**ez_base) is True, "502EZ gate passes when all 13 criteria are met",
      "502EZ gate wrong on the passing case")
check(VA._va_502ez_eligible(**{**ez_base, "has_conformity_modifications": True}) is False,
      "ANY conformity modification puts a TY2025 PTE out of 502EZ by definition",
      "the decisive 502EZ conformity exclusion did not fire")
check(VA._va_502ez_eligible(**{**ez_base, "owner_count": 11}) is False,
      "more than 10 owners fails the 502EZ gate", "502EZ owner-count criterion wrong")
check(VA._va_502ez_eligible(**{**ez_base, "total_taxable_income": 40001}) is False,
      "taxable income above $40,000 fails the 502EZ gate", "502EZ income criterion wrong")
check(VA._va_502_and_ptet_mutually_exclusive() is True,
      "Form 502 and Form 502PTET are mutually exclusive filings", "mutual exclusivity wrong")

# ---- 5k. The VK-1 cross-form assertion set ----
f502 = {1: 1000000, 2: 150000, 3: 0, 4: 0, 5: 70000, 6: 930000, 7: 0.225,
        8: 0, 9: 0, 10: 0, 11: 0, 13: 0, 18: 0, "c": 14000}
rows = [
    {1: 600000, 5: 42000, 6: 558000, 2: 90000, 7: 0.225, "d": 60.00, "e": 10000},
    {1: 400000, 5: 28000, 6: 372000, 2: 60000, 7: 0.225, "d": 40.00, "e": 4000},
]
res = VA._va_vk1_crossform_checks(f502, rows)
check(res["sum_vk1_L1_eq_502_L1"], "sum(VK-1 Line 1) = Form 502 Line 1", "VK-1 Line 1 reconciliation failed")
check(res["sum_vk1_L5_eq_502_L5"] and res["sum_vk1_L6_eq_502_L6"],
      "sum(VK-1 Lines 5 and 6) = Form 502 Lines 5 and 6", "VK-1 Line 5/6 reconciliation failed")
check(res["vk1_L7_same_for_every_owner"],
      "VK-1 Line 7 is the SAME for every owner and is never summed", "VK-1 Line 7 rule failed")
check(res["sum_vk1_Ld_eq_100pct"], "sum(VK-1 Line d participation %) = 100.00%", "participation % does not total 100")
check(res["sum_vk1_Le_eq_502_Lc"], "sum(VK-1 Line e withheld) = Form 502 Line c", "withholding roll-up failed")
_row0_bad = dict(rows[0])
_row0_bad[7] = 0.5
bad = VA._va_vk1_crossform_checks(f502, [_row0_bad, rows[1]])
check(bad["vk1_L7_same_for_every_owner"] is False,
      "a divergent VK-1 Line 7 is DETECTED (the assertion is real, not vacuous)",
      "the VK-1 Line 7 assertion is vacuous")
check(12 == len(VA.VA_VK1_MIRROR_LINES),
      "the mirror set is the 12 lines the DOR enumerates", f"mirror set wrong: {VA.VA_VK1_MIRROR_LINES}")

# ======================================================================
# 6. Every RED-defer R1..R16 has its own diagnostic.
# ======================================================================
RED_MAP = {
    "R1": ("VA_502", "D_VA502_R1_502EZ_AVAILABLE"),
    "R2": ("VA_502", "D_VA502_R2_VA_DEPRECIATION_BOOK"),
    "R3": ("VA_502", "D_VA502_R3_174A_CATCHUP"),
    "R4": ("VA_502", "D_VA502_R4_APPORT_METHOD_BOX"),
    "R5": ("VA_502", "D_VA502_R5_ALLIED_SIGNAL"),
    "R6": ("VA_502", "D_VA502_R6_FORM_502FED1"),
    "R7": ("VA_502", "D_VA502_R7_SCHEDULE_500AB"),
    "R8": ("VA_502", "D_VA502_R8_FORM_765"),
    "R9": ("VA_502", "D_VA502_R9_FORM_TCA"),
    "R10": ("VA_502", "D_VA502_R10_TIERED_PTE_WH"),
    "R11": ("VA_502PTET", "D_VAPTET_R11_ENTITY_RD_CREDIT"),
    "R12": ("VA_502", "D_VA502_R12_WAIVER_REQUESTS"),
    "R13": ("VA_502", "D_VA502_R13_BANK_FRANCHISE"),
    "R14": ("VA_502", "D_VA502_R14_ALT_APPORTIONMENT"),
    "R15": ("VA_502", "D_VA502_R15_FORM_500HS"),
    "R16": ("VA_502", "D_VA502_R16_VK1_CONSOLIDATED"),
}
missing_red = [f"{k}({did})" for k, (fn, did) in RED_MAP.items()
               if not FormDiagnostic.objects.filter(tax_form__form_number=fn, diagnostic_id=did).exists()]
check(not missing_red, "all 16 RED-defers R1-R16 have their own diagnostic",
      f"RED-defers with NO diagnostic: {missing_red}")

# The depreciation-book RED-defers must exist on BOTH forms -- they apply to both paths.
for fn in FORM_SHAPE:
    pref = "D_VA502" if fn == "VA_502" else "D_VAPTET"
    for did in (f"{pref}_R2_VA_DEPRECIATION_BOOK", f"{pref}_R3_174A_CATCHUP",
                f"{pref}_W2_CONFORMITY_BUCKET", f"{pref}_W3_NO_VA_179_FIGURE",
                f"{pref}_W10_TWO_DUE_CLOCKS"):
        check(FormDiagnostic.objects.filter(tax_form__form_number=fn, diagnostic_id=did).exists(),
              f"{fn}: {did} present", f"{fn}: MISSING {did}")

# The hard blocks must be severity 'error'.
for fn, did in (("VA_502", "D_VA502_R2_VA_DEPRECIATION_BOOK"),
                ("VA_502", "D_VA502_R3_174A_CATCHUP"),
                ("VA_502", "D_VA502_R10_TIERED_PTE_WH"),
                ("VA_502", "D_VA502_R6_FORM_502FED1"),
                ("VA_502PTET", "D_VAPTET_HARD_BAR"),
                ("VA_502PTET", "D_VAPTET_R11_ENTITY_RD_CREDIT")):
    d = FormDiagnostic.objects.filter(tax_form__form_number=fn, diagnostic_id=did).first()
    check(d is not None and d.severity == "error", f"{did} is severity 'error' (a hard block)",
          f"{did} severity is {getattr(d, 'severity', 'MISSING')!r}, expected 'error'")

# The money-moving walk items each have their own review diagnostic.
for fn, did in (("VA_502PTET", "D_VAPTET_W4_LINE7B_RATE"),
                ("VA_502PTET", "D_VAPTET_U4_STALE_SUNSET"),
                ("VA_502PTET", "D_VAPTET_BASE_DIVERGES"),
                ("VA_502PTET", "D_VAPTET_U6_ELIGIBLE_SHARE"),
                ("VA_502PTET", "D_VAPTET_U9_SCORP_ALL_NONRES"),
                ("VA_502PTET", "D_VAPTET_U8_PTETADJ_PART2"),
                ("VA_502", "D_VA502_U7_ADJ_D5_TRUNCATED"),
                ("VA_502", "D_VA502_R16_VK1_CONSOLIDATED")):
    check(FormDiagnostic.objects.filter(tax_form__form_number=fn, diagnostic_id=did).exists(),
          f"open-item diagnostic present: {did}", f"MISSING open-item diagnostic {did}")

# The e-file waiver diagnostics must NOT assert that a waiver is impossible (W7).
for fn, did in (("VA_502", "D_VA502_R12_WAIVER_REQUESTS"),
                ("VA_502PTET", "D_VAPTET_EFILE_ONLY_POLICY")):
    d = FormDiagnostic.objects.filter(tax_form__form_number=fn, diagnostic_id=did).first()
    txt = (d.message if d else "").lower()
    check(d is not None and "58.1-392" in txt and "cannot exist" not in txt,
          f"{did} states the waiver posture POSITIVELY and cites s.58.1-392 E (W7)",
          f"{did} does not state the waiver posture correctly")
check(VA._yk(VA.VA_PTET_EFILE_WAIVER_LEGALLY_POSSIBLE) is True
      and VA._yk(VA.VA_PTET_EFILE_WAIVER_POLICY_DEFAULT) is False,
      "e-file-only is a POLICY default; a waiver remains LEGALLY POSSIBLE (s.58.1-392 E)",
      "the e-file waiver posture was encoded as a legal invariant")

# Page-1 block really is shared: the two forms carry the same Lines 1-20 and the same fact keys.
l502 = {ln.line_number for ln in FormLine.objects.filter(tax_form__form_number="VA_502")}
lptet = {ln.line_number for ln in FormLine.objects.filter(tax_form__form_number="VA_502PTET")}
check({str(n) for n in range(1, 21)} <= (l502 & lptet),
      "Page 1 Lines 1-20 exist IDENTICALLY on both forms (the shared block held)",
      f"Page-1 lines diverge: {sorted({str(n) for n in range(1, 21)} - (l502 & lptet))}")
check("P2-10" in l502 and "P2-10" not in lptet,
      "the Form 502 withholding return (Page 2) exists only on VA_502", "Page 2 leaked onto VA_502PTET")
check("II-7a" in lptet and "II-7a" not in l502,
      "the 5.75% tax computation exists only on VA_502PTET", "PTET Section II leaked onto VA_502")
f_502 = {f.fact_key for f in FormFact.objects.filter(tax_form__form_number="VA_502")}
f_ptet = {f.fact_key for f in FormFact.objects.filter(tax_form__form_number="VA_502PTET")}
check({f["fact_key"] for f in VA._page1_facts()} <= (f_502 & f_ptet),
      "the shared Page-1 fact block is present on both forms", "the shared fact block diverged")

# ======================================================================
# 6b. G1 PROVENANCE RATCHET - campaign D-18 (2026-08-22), superseding D-12 B1
# ----------------------------------------------------------------------
# The 4/3/3/2 divisor is a TRANSCRIPTION from Va. Code Sec. 58.1-408 A, which
# states BOTH branches outright. D-12 B1 had ratified the same NUMBERS on the
# premise that no source stated the rule - a premise the Wave-5 C-corp
# verification pass disproved. The arithmetic never changed and is pinned at
# section 5g; what changed is the PROVENANCE, and stale provenance is this
# campaign's repeat failure mode. These checks pin the seeded provenance text
# so a later edit cannot quietly restore the superseded premise or "reconcile"
# the spec to the DEFECTIVE Form 502 instruction book (which restates
# Sec. 58.1-408 A but drops the words "plus one", printing 2 where the statute
# requires 3).
# ======================================================================
_div4 = FlowAssertion.objects.filter(assertion_id="FA-VA-APPORT-DIV4").first()
_div4_txt = (_div4.description or "") if _div4 else ""
check(_div4 is not None,
      "FA-VA-APPORT-DIV4 exists",
      "FA-VA-APPORT-DIV4 is MISSING")
check("58.1-408" in _div4_txt,
      "FA-VA-APPORT-DIV4 cites Sec. 58.1-408 A as the divisor authority (D-18/G1)",
      "FA-VA-APPORT-DIV4 does NOT cite Sec. 58.1-408 A - provenance regressed (D-18/G1)")
check("IS AN INTERPRETATION" not in _div4_txt.upper(),
      "FA-VA-APPORT-DIV4 no longer calls the divisor an INTERPRETATION (D-12 B1 premise retired)",
      "FA-VA-APPORT-DIV4 still asserts the SUPERSEDED D-12 B1 premise ('an interpretation')")
check("plus one" in _div4_txt.lower(),
      "FA-VA-APPORT-DIV4 records that the Form 502 book drops the statutory 'plus one'",
      "FA-VA-APPORT-DIV4 omits the 'plus one' divergence - the substance of D-18/G1")

# ⚠ The -502AB rule is emitted ONCE PER FORM (R-VA-502AB on VA_502, R-VAP-502AB
# on VA_502PTET) from one shared template, so BOTH carry the DIVISOR NOTE and
# BOTH must be checked - .first() would have inspected only one of them.
_b2fs = list(FormRule.objects.filter(rule_id__endswith="-502AB").order_by("rule_id"))
check(len(_b2fs) == 2,
      f"the 502A Section B apportionment rule exists on BOTH forms ({len(_b2fs)} found)",
      f"expected 2 '-502AB' rules (one per form), found {len(_b2fs)}")
for _b2f in _b2fs:
    _b2f_txt = _b2f.description or ""
    _rid = _b2f.rule_id
    check("58.1-408" in _b2f_txt,
          f"{_rid}: the DIVISOR NOTE cites Sec. 58.1-408 A (D-18/G1)",
          f"{_rid}: the DIVISOR NOTE does NOT cite Sec. 58.1-408 A - provenance regressed")
    check("agree only when" not in _b2f_txt,
          f"{_rid}: the DIVISOR NOTE no longer rests on the face-vs-instruction reconciliation",
          f"{_rid}: the DIVISOR NOTE still rests on the SUPERSEDED reconciliation premise")

# ======================================================================
# 7. Report
# ======================================================================
print("\n" + "=" * 74)
for fn in FORM_SHAPE:
    form = TaxForm.objects.get(form_number=fn)
    print(f"  {fn}: facts {FormFact.objects.filter(tax_form=form).count()} / "
          f"rules {FormRule.objects.filter(tax_form=form).count()} / "
          f"lines {FormLine.objects.filter(tax_form=form).count()} / "
          f"diag {FormDiagnostic.objects.filter(tax_form=form).count()} / "
          f"tests {TestScenario.objects.filter(tax_form=form).count()}")
print(f"  flow assertions: {FlowAssertion.objects.filter(assertion_id__startswith='FA-VA').count()}")
print(f"  authority sources (VA): {AuthoritySource.objects.filter(jurisdiction_code='VA').count()}")
print(f"  authority excerpts: {AuthorityExcerpt.objects.count()}")
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

from django.db import connections  # noqa: E402
connections.close_all()
try:
    if os.path.exists(SQLITE_PATH):
        os.remove(SQLITE_PATH)
except OSError:
    pass
sys.exit(1 if FAILURES else 0)
