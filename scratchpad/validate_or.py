"""Throwaway-SQLite validation for the Oregon PTE specs (WO-W04-PTE, Wave 4).

OR_65 (Form OR-65) + OR_20_S (Form OR-20-S) + OR_21 (Form OR-21, the PTE-E
elective tax -- its own spec per campaign D-12).

Checks, in order:
  1. THE SEED GUARD -- asserted to REFUSE, and asserted to leave the DB CLEAN.
     Pins the MECHANISM, not the disk value, then flips IN MEMORY ONLY.
  2. CharField caps -- introspected from the REAL model fields via _meta, never
     hardcoded. SQLite does NOT enforce max_length; Postgres does. Wave 3's
     harnesses caught four topic_name values over the 255 cap that were INVISIBLE
     IN SQLITE and would have been Postgres DataErrors in prod.
  3. CHOICE-FIELD VALIDITY -- Django does NOT validate `choices` on save(), so an
     invalid enum value rides straight through SQLite AND Postgres and only
     surfaces as a broken export downstream. Introspected from _meta too.
  4. Structural integrity -- three forms, every rule authority-linked, no
     duplicate ids, rule_links referencing defined rules, identity fields.
  5. C1 -- THE CODE-NAMESPACE GUARD. Proves it FIRES, proves no colliding code
     resolves without a namespace, proves the 158/154 twin, proves the crossing
     point, and proves the collision ledger recomputes to TWELVE.
  6. Arithmetic oracles -- the OR-65 two gates and the published proration table,
     the OR-20-S rate/floor/LIFO stack, the OR-21 rate against the DOR's own two
     worked examples, the line-21 closure, and the U5 impossibility with its
     worked counterexample.
  7. VERIFIED NEGATIVES -- pinned so a later contributor cannot quietly add a
     field "for symmetry with other states".

ASCII-only. Run: poetry run python scratchpad/validate_or.py
"""
import os
import sys

PROJECT_ROOT = r"D:\dev\delvio-rule-studio"
sys.path.insert(0, PROJECT_ROOT)

SQLITE_PATH = os.path.join(PROJECT_ROOT, "scratchpad", "validate_or.sqlite3")
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
    AuthorityExcerpt, AuthorityFormLink, AuthoritySource, AuthorityTopic, RuleAuthorityLink,
)
from specs.management.commands import load_or_pte as OR  # noqa: E402

FAILURES: list = []
PASSES: list = []


def _safe(s):
    try:
        return str(s).encode("ascii", "replace").decode("ascii")
    except Exception:  # noqa: BLE001
        return "<unprintable>"


def check(cond, ok, bad):
    (PASSES if cond else FAILURES).append(_safe(ok) if cond else _safe(bad))


def approx(a, b, tol=0.005):
    return abs(float(a) - float(b)) <= tol


call_command("migrate", run_syncdb=True, verbosity=0)

# Mirror prod: the Tier-1 conformity batch (campaign D-10) is ALREADY SEEDED
# there, so the Oregon anchors in EXISTING_SOURCES_TO_REFERENCE resolve. Seed it
# here too, so the harness tests the same wiring the prod seed will see.
try:
    call_command("load_state_conformity", verbosity=0)
    PASSES.append("Tier-1 conformity batch seeded into the throwaway DB (mirrors prod, campaign D-10)")
except Exception as exc:  # noqa: BLE001
    FAILURES.append(f"could not seed the Tier-1 conformity batch: {exc!r}")

F65, F20S, F21 = OR.FORM_CODE_OR65, OR.FORM_CODE_OR20S, OR.FORM_CODE_OR21
M65, MS = OR.M_1065, OR.M_1120S

# ==========================================================================
# 1. THE SEED GUARD
# ==========================================================================
_shipped = OR.READY_TO_SEED
check(_shipped is False,
      "READY_TO_SEED ships FALSE on disk -- Gate 1 has NOT been taken for Oregon",
      f"READY_TO_SEED SHIPPED {_shipped!r} -- it MUST ship False; Gate 1 is open and "
      "OR_21 is blocked twice on the DOR")

try:
    call_command("load_or_pte", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: the loader seeded with READY_TO_SEED = False")
except CommandError as e:
    msg = str(e)
    check("REFUSING TO SEED" in msg, "guard REFUSES to seed while READY_TO_SEED is False",
          "guard raised CommandError but without the refusal banner")
    check("Gate 1 has NOT been taken" in msg,
          "guard states plainly that Gate 1 is open for Oregon",
          "guard message does not say Gate 1 is open")
    check("U5" in msg and "negative" in msg.lower(),
          "guard names the U5 OR-21-MD denominator blocker and its negative-share trigger",
          "guard message omits the U5 blocker")
    check("MeF" in msg and ("U1" in msg or "U19" in msg),
          "guard names the OR-21 MeF schema-family blocker (U1/U19/U23)",
          "guard message omits the MeF schema blocker")
    check("U24" in msg and "314.772" in msg,
          "guard names U24 (2025 c.36 s.3 amending ORS 314.772) as blocking OR-20-S line 15",
          "guard message omits the U24 blocker")
    check("has not been sent" in msg.lower() or "HAS NOT BEEN SENT" in msg,
          "guard records that the DOR developers'-handbook request is DECIDED but UNSENT",
          "guard does not record that the unlocking action is unsent")
    check("READY_TO_SEED = False" in msg, "guard reports the sentinel value it saw",
          "guard message omits the sentinel value")
    check("DO NOT RELAX THIS GUARD" in msg,
          "guard tells the next reader not to relax it",
          "guard omits the do-not-relax warning")
except Exception as e:  # noqa: BLE001
    FAILURES.append(f"guard raised the WRONG exception type: {e!r}")

check(TaxForm.objects.filter(jurisdiction="OR").count() == 0,
      "guard left the DB CLEAN -- no Oregon TaxForm rows were written while gated",
      "guard refused but Oregon rows were still written")
check(FormRule.objects.filter(rule_id__startswith="R-OR").count() == 0,
      "guard left the DB CLEAN -- no Oregon FormRule rows were written while gated",
      "guard refused but Oregon rules were still written")
check(FlowAssertion.objects.filter(assertion_id__startswith="FA-OR").count() == 0,
      "guard left the DB CLEAN -- no Oregon FlowAssertion rows were written while gated",
      "guard refused but Oregon flow assertions were still written")

# Flip IN MEMORY ONLY. The file on disk stays False.
OR.READY_TO_SEED = True
try:
    call_command("load_or_pte", verbosity=0)
    PASSES.append("loader ran + seeded into throwaway SQLite without error (in-memory flip only)")
except Exception as e:  # noqa: BLE001
    FAILURES.append(f"load_or_pte raised: {e!r}")
    print("\n".join(FAILURES))
    sys.exit(1)
finally:
    OR.READY_TO_SEED = _shipped   # never leave the module mutated

f65 = TaxForm.objects.get(form_number=F65, jurisdiction="OR")
f20s = TaxForm.objects.get(form_number=F20S, jurisdiction="OR")
f21 = TaxForm.objects.get(form_number=F21, jurisdiction="OR")
ALL_FORMS = [f65, f20s, f21]

# ==========================================================================
# 2. CharField caps -- introspected from the REAL model fields
# ==========================================================================
CAP = {
    "TaxForm.form_number":          TaxForm._meta.get_field("form_number").max_length,
    "TaxForm.jurisdiction":         TaxForm._meta.get_field("jurisdiction").max_length,
    "TaxForm.form_title":           TaxForm._meta.get_field("form_title").max_length,
    "FormFact.fact_key":            FormFact._meta.get_field("fact_key").max_length,
    "FormFact.label":               FormFact._meta.get_field("label").max_length,
    "FormFact.default_value":       FormFact._meta.get_field("default_value").max_length,
    "FormRule.rule_id":             FormRule._meta.get_field("rule_id").max_length,
    "FormRule.title":               FormRule._meta.get_field("title").max_length,
    "FormLine.line_number":         FormLine._meta.get_field("line_number").max_length,
    "FormLine.destination_form":    FormLine._meta.get_field("destination_form").max_length,
    "FormDiagnostic.diagnostic_id": FormDiagnostic._meta.get_field("diagnostic_id").max_length,
    "FormDiagnostic.title":         FormDiagnostic._meta.get_field("title").max_length,
    "TestScenario.scenario_name":   TestScenario._meta.get_field("scenario_name").max_length,
    "FlowAssertion.assertion_id":   FlowAssertion._meta.get_field("assertion_id").max_length,
    "FlowAssertion.title":          FlowAssertion._meta.get_field("title").max_length,
    "FlowAssertion.bug_reference":  FlowAssertion._meta.get_field("bug_reference").max_length,
    "AuthoritySource.source_code":  AuthoritySource._meta.get_field("source_code").max_length,
    "AuthoritySource.citation":     AuthoritySource._meta.get_field("citation").max_length,
    "AuthoritySource.issuer":       AuthoritySource._meta.get_field("issuer").max_length,
    "AuthorityTopic.topic_code":    AuthorityTopic._meta.get_field("topic_code").max_length,
    "AuthorityTopic.topic_name":    AuthorityTopic._meta.get_field("topic_name").max_length,
    "AuthorityExcerpt.excerpt_label": AuthorityExcerpt._meta.get_field("excerpt_label").max_length,
    "AuthorityExcerpt.location_reference": AuthorityExcerpt._meta.get_field("location_reference").max_length,
    "AuthorityFormLink.form_code":  AuthorityFormLink._meta.get_field("form_code").max_length,
}

# The caps the campaign brief states -- assert the MODEL still agrees, so a
# silent migration that widens or narrows a column is caught here too.
EXPECTED = {
    "FormRule.rule_id": 20, "FormLine.line_number": 20, "FlowAssertion.assertion_id": 20,
    "FormDiagnostic.diagnostic_id": 40, "FormFact.fact_key": 100,
    "AuthorityTopic.topic_name": 255, "AuthoritySource.citation": 255,
    "AuthoritySource.issuer": 100, "AuthoritySource.source_code": 100,
    "AuthorityFormLink.form_code": 50, "TaxForm.form_number": 50,
}
for k, want in EXPECTED.items():
    check(CAP[k] == want, f"model cap {k} == {want} (as the campaign brief states)",
          f"model cap {k} is {CAP[k]}, brief says {want} -- reconcile before seeding")

viol = []


def measure(label, value, cap_key):
    cap = CAP[cap_key]
    if value is None or cap is None:   # cap None => TextField, unbounded
        return
    if len(str(value)) > cap:
        viol.append(f"{label}: len {len(str(value))} > {cap} ({cap_key}) :: {_safe(value)[:70]}")


for form in ALL_FORMS:
    measure(f"form_number={form.form_number}", form.form_number, "TaxForm.form_number")
    measure(f"jurisdiction[{form.form_number}]", form.jurisdiction, "TaxForm.jurisdiction")
    measure(f"form_title[{form.form_number}]", form.form_title, "TaxForm.form_title")
    for r in FormRule.objects.filter(tax_form=form):
        measure(f"rule_id={r.rule_id}", r.rule_id, "FormRule.rule_id")
        measure(f"rule.title[{r.rule_id}]", r.title, "FormRule.title")
    for ln in FormLine.objects.filter(tax_form=form):
        measure(f"line_number={ln.line_number}", ln.line_number, "FormLine.line_number")
        measure(f"dest[{form.form_number}/{ln.line_number}]", ln.destination_form, "FormLine.destination_form")
    for fct in FormFact.objects.filter(tax_form=form):
        measure(f"fact_key={fct.fact_key}", fct.fact_key, "FormFact.fact_key")
        measure(f"fact.label[{fct.fact_key}]", fct.label, "FormFact.label")
        measure(f"fact.default[{fct.fact_key}]", fct.default_value, "FormFact.default_value")
    for d in FormDiagnostic.objects.filter(tax_form=form):
        measure(f"diagnostic_id={d.diagnostic_id}", d.diagnostic_id, "FormDiagnostic.diagnostic_id")
        measure(f"diag.title[{d.diagnostic_id}]", d.title, "FormDiagnostic.title")
    for t in TestScenario.objects.filter(tax_form=form):
        measure(f"scenario_name[{form.form_number}]", t.scenario_name, "TestScenario.scenario_name")

for fa in FlowAssertion.objects.filter(assertion_id__startswith="FA-OR"):
    measure(f"assertion_id={fa.assertion_id}", fa.assertion_id, "FlowAssertion.assertion_id")
    measure(f"fa.title[{fa.assertion_id}]", fa.title, "FlowAssertion.title")
    measure(f"fa.bug_ref[{fa.assertion_id}]", fa.bug_reference, "FlowAssertion.bug_reference")
for s in AuthoritySource.objects.filter(source_code__startswith="OR_"):
    measure(f"source_code={s.source_code}", s.source_code, "AuthoritySource.source_code")
    measure(f"citation[{s.source_code}]", s.citation, "AuthoritySource.citation")
    measure(f"issuer[{s.source_code}]", s.issuer, "AuthoritySource.issuer")
    for exc in AuthorityExcerpt.objects.filter(authority_source=s):
        measure(f"excerpt_label[{s.source_code}]", exc.excerpt_label, "AuthorityExcerpt.excerpt_label")
        measure(f"location_ref[{s.source_code}]", exc.location_reference, "AuthorityExcerpt.location_reference")
for tp in AuthorityTopic.objects.filter(topic_code__startswith="or_"):
    measure(f"topic_code={tp.topic_code}", tp.topic_code, "AuthorityTopic.topic_code")
    measure(f"topic_name={tp.topic_code}", tp.topic_name, "AuthorityTopic.topic_name")
for afl in AuthorityFormLink.objects.filter(form_code__startswith="OR_"):
    measure(f"form_code={afl.form_code}", afl.form_code, "AuthorityFormLink.form_code")

check(not viol, "CharField caps OK -- every seeded value fits its REAL model field",
      "CAP VIOLATIONS (Postgres would truncate/reject; SQLite silently accepts):\n    "
      + "\n    ".join(viol))

# ==========================================================================
# 3. CHOICE-FIELD VALIDITY
#    Django does NOT validate `choices` on save(). An invalid enum rides through
#    SQLite AND Postgres and only surfaces downstream as a broken export.
# ==========================================================================
bad_choice = []


def choices_for(model, field):
    return {c[0] for c in model._meta.get_field(field).choices or []}


def check_choice(model, field, rows, label_attr):
    allowed = choices_for(model, field)
    if not allowed:
        return
    for row in rows:
        val = getattr(row, field)
        if val in (None, "") and model._meta.get_field(field).null:
            continue
        if val not in allowed:
            bad_choice.append(
                f"{model.__name__}.{field} = {val!r} on {_safe(getattr(row, label_attr))} "
                f"-- allowed: {sorted(allowed)}")


for form in ALL_FORMS:
    check_choice(TaxForm, "status", [form], "form_number")
    check_choice(FormFact, "data_type", list(FormFact.objects.filter(tax_form=form)), "fact_key")
    check_choice(FormRule, "rule_type", list(FormRule.objects.filter(tax_form=form)), "rule_id")
    check_choice(FormLine, "line_type", list(FormLine.objects.filter(tax_form=form)), "line_number")
    check_choice(FormDiagnostic, "severity", list(FormDiagnostic.objects.filter(tax_form=form)), "diagnostic_id")
    check_choice(TestScenario, "scenario_type", list(TestScenario.objects.filter(tax_form=form)), "scenario_name")

_or_sources = list(AuthoritySource.objects.filter(source_code__startswith="OR_"))
check_choice(AuthoritySource, "source_type", _or_sources, "source_code")
check_choice(AuthoritySource, "source_rank", _or_sources, "source_code")
check_choice(AuthoritySource, "current_status", _or_sources, "source_code")
check_choice(AuthorityFormLink, "link_type",
             list(AuthorityFormLink.objects.filter(form_code__startswith="OR_")), "form_code")
check_choice(RuleAuthorityLink, "support_level",
             list(RuleAuthorityLink.objects.filter(form_rule__tax_form__jurisdiction="OR")), "support_level")
_or_fa = list(FlowAssertion.objects.filter(assertion_id__startswith="FA-OR"))
check_choice(FlowAssertion, "assertion_type", _or_fa, "assertion_id")
check_choice(FlowAssertion, "status", _or_fa, "assertion_id")

check(not bad_choice,
      "CHOICE-FIELD VALIDITY OK -- every seeded enum value is a declared model choice",
      "INVALID CHOICE VALUES (Django does NOT validate choices on save; these ride into "
      "Postgres unnoticed):\n    " + "\n    ".join(bad_choice))

# ==========================================================================
# 4. Structural integrity
# ==========================================================================
check(len(OR.FORMS) == 3 and TaxForm.objects.filter(jurisdiction="OR").count() == 3,
      "THREE Oregon specs seeded -- OR_65, OR_20_S and OR_21 (campaign D-12: OR_21 is its own spec)",
      f"expected 3 Oregon forms, got {TaxForm.objects.filter(jurisdiction='OR').count()}")
check(f65.entity_types == ["1065"], "OR_65 entity_types == ['1065'] -- Oregon never puts S corps on OR-65",
      f"OR_65 entity_types wrong: {f65.entity_types}")
check(f20s.entity_types == ["1120S"], "OR_20_S entity_types == ['1120S']",
      f"OR_20_S entity_types wrong: {f20s.entity_types}")
check(f21.entity_types == ["1065", "1120S"],
      "OR_21 entity_types == ['1065', '1120S'] -- the PTE-E return serves BOTH modules",
      f"OR_21 entity_types wrong: {f21.entity_types}")
for form in ALL_FORMS:
    check(form.jurisdiction == "OR" and form.tax_year == 2025 and form.version == 1
          and form.status == "draft",
          f"{form.form_number}: jurisdiction OR / TY2025 / v1 / draft",
          f"{form.form_number} identity wrong: {form.jurisdiction} {form.tax_year} v{form.version} {form.status}")
check({f.form_number for f in ALL_FORMS} == {"OR_65", "OR_20_S", "OR_21"},
      "form codes follow the campaign D-9 <ST>_<FORM> namespace",
      f"form codes wrong: {[f.form_number for f in ALL_FORMS]}")

ruleless = [r.rule_id for r in FormRule.objects.filter(tax_form__jurisdiction="OR")
            if not RuleAuthorityLink.objects.filter(form_rule=r).exists()]
check(not ruleless,
      f"all {FormRule.objects.filter(tax_form__jurisdiction='OR').count()} Oregon rules carry >= 1 authority link",
      f"rules with NO authority link: {ruleless}")

for spec in OR.FORMS:
    fn = spec["identity"]["form_number"]
    defined = {r["rule_id"] for r in spec["rules"]}
    linked = {rl[0] for rl in spec["rule_links"]}
    check(not (linked - defined), f"{fn}: rule_links reference only defined rules",
          f"{fn}: orphan rule_links: {linked - defined}")
    check(not (defined - linked), f"{fn}: every rule appears in rule_links",
          f"{fn}: unlinked rules: {defined - linked}")
    for label, seq, key in (
        ("rule_id", spec["rules"], "rule_id"),
        ("line_number", spec["lines"], "line_number"),
        ("fact_key", spec["facts"], "fact_key"),
        ("diagnostic_id", spec["diagnostics"], "diagnostic_id"),
        ("scenario_name", spec["scenarios"], "scenario_name"),
    ):
        ids = [x[key] for x in seq]
        dupes = {i for i in ids if ids.count(i) > 1}
        check(not dupes, f"{fn}: no duplicate {label} ({len(ids)} unique)",
              f"{fn}: DUPLICATE {label}: {dupes}")

fa_ids = [a["assertion_id"] for a in OR.FLOW_ASSERTIONS]
check(len(set(fa_ids)) == len(fa_ids), f"no duplicate assertion_id ({len(fa_ids)} flow assertions)",
      f"DUPLICATE assertion_id: {[i for i in fa_ids if fa_ids.count(i) > 1]}")
check(FlowAssertion.objects.filter(assertion_id__startswith="FA-OR").count() == len(fa_ids),
      f"all {len(fa_ids)} Oregon flow assertions seeded",
      "flow assertion count mismatch")

# EXISTING_SOURCES_TO_REFERENCE must be REAL, and Oregon's must RESOLVE here
# because the Tier-1 conformity batch was seeded above (mirroring prod, D-10).
for code in OR.EXISTING_SOURCES_TO_REFERENCE:
    check(AuthoritySource.objects.filter(source_code=code).exists(),
          f"existing Oregon anchor {code} RESOLVES (seeded by the Tier-1 conformity batch)",
          f"existing Oregon anchor {code} did NOT resolve -- check _state_conformity_tier1.py")
check("OR_ORS_317_010_CONFORMITY" in OR.EXISTING_SOURCES_TO_REFERENCE
      and "OR_2025_PUB_OR17" in OR.EXISTING_SOURCES_TO_REFERENCE
      and "OR_ORS_317_301_DEPR" in OR.EXISTING_SOURCES_TO_REFERENCE,
      "EXISTING_SOURCES_TO_REFERENCE reuses all three seeded Oregon anchors rather than re-creating them",
      "an Oregon conformity anchor is missing from EXISTING_SOURCES_TO_REFERENCE")
recreated = [s["source_code"] for s in OR.AUTHORITY_SOURCES
             if s["source_code"] in OR.EXISTING_SOURCES_TO_REFERENCE]
check(not recreated, "no already-seeded Oregon source is re-created by this loader",
      f"loader re-creates already-seeded sources: {recreated}")

# ==========================================================================
# 5. C1 -- THE CODE-NAMESPACE GUARD. The single most important thing here.
# ==========================================================================
led = OR.or_code_collisions()
check(len(OR.OR_COLLIDING_CODES) == 12 and OR.OR_COLLISION_COUNT == 12,
      "TWELVE colliding code numbers encoded (10 semantic + 2 label-only) -- the CORRECTED count",
      f"collision count wrong: {len(OR.OR_COLLIDING_CODES)}")
check(set(OR.OR_SEMANTIC_COLLISIONS) == {118, 132, 150, 151, 158, 159, 352, 356, 358, 361},
      "the ten SEMANTIC collisions are exactly 118/132/150/151/158/159/352/356/358/361",
      f"semantic collision set wrong: {OR.OR_SEMANTIC_COLLISIONS}")
check(118 in OR.OR_SEMANTIC_COLLISIONS and 132 in OR.OR_SEMANTIC_COLLISIONS,
      "118 and 132 -- the two the verification pass ADDED -- are in the table",
      "118/132 missing: the table is still under-scoped at ten")
check(set(led["semantic_collisions"]) == set(OR.OR_SEMANTIC_COLLISIONS),
      "the collision ledger RECOMPUTES from the two tables and agrees with the declared set",
      f"recomputed semantic collisions {led['semantic_collisions']} != declared {list(OR.OR_SEMANTIC_COLLISIONS)}")

# 158 vs 154 -- the twin that makes the hazard silent.
c158 = OR.or_code(OR.NS_CORPORATE, 158, OR.K_ADDITION)
i158 = OR.or_code(OR.NS_INDIVIDUAL, 158, OR.K_ADDITION)
i154 = OR.or_code(OR.NS_INDIVIDUAL, 154, OR.K_ADDITION)
check("depreciable" in c158["label"].lower() and "bonds of other states" in i158["label"].lower(),
      "158 CORPORATE = depreciable-property gain/loss; 158 INDIVIDUAL = other states' bond interest",
      f"code 158 labels wrong: corp={c158['label']!r} indiv={i158['label']!r}")
check("depreciable" in i154["label"].lower(),
      "154 is 158's SEMANTIC TWIN in the individual set -- a LABEL-driven mapper survives the crossing",
      "individual 154 is not the depreciable-property item")
check(c158["label"] != i158["label"],
      "the two 158s carry DIFFERENT labels, so a label-equality test catches the mix-up",
      "the two 158 labels are identical -- the oracle proves nothing")

# The guard must FIRE on every cross-use, in BOTH directions.
def guard_raises(context, namespace):
    try:
        OR.or_assert_namespace(context, namespace)
        return False
    except OR.OregonCodeNamespaceError:
        return True


check(guard_raises("OR65_SCHEDULE_I", OR.NS_CORPORATE),
      "GUARD FIRES: corporate codes REFUSED on Form OR-65 Schedule I",
      "guard did NOT fire for corporate codes on Schedule I")
check(guard_raises("OR20S_LINE_2", OR.NS_INDIVIDUAL),
      "GUARD FIRES: individual codes REFUSED on Form OR-20-S line 2",
      "guard did NOT fire for individual codes on OR-20-S line 2")
check(guard_raises("OR20S_LINE_3", OR.NS_INDIVIDUAL),
      "GUARD FIRES: individual codes REFUSED on Form OR-20-S line 3",
      "guard did NOT fire for individual codes on OR-20-S line 3")
check(guard_raises("OR_K1_OVERFLOW_ATTACHMENT", OR.NS_CORPORATE),
      "GUARD FIRES: corporate codes REFUSED on the Schedule OR-K-1 OVERFLOW ATTACHMENT",
      "guard did NOT fire on the overflow attachment -- THE CROSSING POINT IS UNPROTECTED")
check(guard_raises("OR20S_LINE_15", OR.NS_CORPORATE),
      "GUARD FIRES: line 15 takes the CREDIT table, not the corporate modification table",
      "guard did NOT distinguish line 15's credit namespace")
check(guard_raises("NOT_A_REAL_CONTEXT", OR.NS_INDIVIDUAL),
      "GUARD FIRES on an unknown context rather than defaulting silently",
      "guard accepted an unknown context")

check(OR.or_assert_namespace("OR20S_LINE_2", OR.NS_CORPORATE) == OR.NS_CORPORATE,
      "guard PERMITS corporate codes on OR-20-S line 2", "guard blocked a legitimate corporate use")
check(OR.or_assert_namespace("OR_K1_OVERFLOW_ATTACHMENT", OR.NS_INDIVIDUAL) == OR.NS_INDIVIDUAL,
      "guard PERMITS individual codes on the OR-K-1 overflow attachment", "guard blocked a legitimate individual use")

# ⚠ THE CROSSING POINT: an OR-20-S engagement runs BOTH namespaces at once.
check(OR.OR_CONTEXT_NAMESPACE["OR20S_LINE_2"] == OR.NS_CORPORATE
      and OR.OR_CONTEXT_NAMESPACE["OR_K1_OVERFLOW_ATTACHMENT"] == OR.NS_INDIVIDUAL,
      "THE CROSSING POINT is encoded: OR-20-S lines 2/3 are CORPORATE while the OR-K-1 overflow "
      "attachment the same return issues is INDIVIDUAL",
      "the crossing point is not encoded -- one OR-20-S engagement must run BOTH namespaces")
check(OR.or_k1_overflow_namespace() == OR.NS_INDIVIDUAL,
      "or_k1_overflow_namespace() resolves to the INDIVIDUAL table",
      "the overflow attachment does not resolve to the individual table")
check("SCHEDULE_SM" not in " ".join(OR.OR_CONTEXT_NAMESPACE),
      "Schedule SM is deliberately ABSENT from the context map -- it is code-free (the DECOY)",
      "Schedule SM appears in the namespace context map; it carries no codes")
check(OR.OR_SCHEDULE_SM_IS_CODE_FREE is True and "decoy" in OR.OR_SCHEDULE_SM_DECOY_NOTE.lower(),
      "the two DOR 'Schedule SM' notes are recorded AS A DECOY, with the retraction on the record",
      "the Schedule SM decoy is not recorded")

# No colliding code may be resolvable without a namespace.
no_ns_ok = True
for code in OR.OR_COLLIDING_CODES:
    check_ok = False
    try:
        OR.or_code(None, code)
    except OR.OregonCodeNamespaceError:
        check_ok = True
    except Exception:  # noqa: BLE001
        check_ok = False
    if not check_ok:
        no_ns_ok = False
check(no_ns_ok,
      "NO colliding code can be resolved without a namespace -- or_code(None, n) always REFUSES",
      "a colliding code resolved without a namespace")
check(all(OR.or_code_is_ambiguous_without_namespace(c) for c in OR.OR_COLLIDING_CODES),
      "all twelve colliding codes are flagged ambiguous-without-namespace",
      "a colliding code is not flagged ambiguous")

# THREE tables, not two -- and the credit series does not overlap.
mod_numbers = {r["code"] for r in OR.OR_CODES_INDIVIDUAL} | {r["code"] for r in OR.OR_ASC_CORP_CODES}
credit_numbers = {r["code"] for r in OR.OR_ASC_CORP_CREDIT_CODES}
check(not (mod_numbers & credit_numbers),
      "THREE tables: the OR-ASC-CORP Section D CREDIT series (8xx/999) shares NO number with the "
      "1xx/3xx modification codes -- line 15 is NOT part of the collision hazard",
      f"credit codes overlap the modification codes: {sorted(mod_numbers & credit_numbers)}")
check(len(OR.OR_ASC_CORP_CREDIT_CODES) >= 20 and 999 in credit_numbers,
      f"the corporate CREDIT table is seeded ({len(OR.OR_ASC_CORP_CREDIT_CODES)} codes incl. 999)",
      "the corporate credit table is missing or too small")
check("built-in gains only" in OR.OR_ASC_CORP_CREDIT_GATE,
      "the DOR's own line-15 gate rides on the credit table ('built-in gains only')",
      "the credit table does not carry the DOR's built-in-gains gate")

# Appendix A is a SUBSET -- code 341 proves it.
c341 = OR.or_code(OR.NS_CORPORATE, 341, OR.K_SUBTRACTION)
check(c341["appendix_a"] is False,
      "code 341 is in the FULL OR-ASC-CORP universe but NOT in Appendix A -- the proof that "
      "Appendix A is the S-corp SUBSET",
      "code 341 is flagged as an Appendix A member; the subset proof is broken")
check(341 not in OR.or_appendix_a_codes(),
      "the OR-20-S eligibility filter excludes 341 while the corporate table still carries it",
      "the Appendix A filter does not exclude 341")
check(OR.or_corporate_code_allowed_on_or20s(341, "excise") is False
      and OR.or_corporate_code_allowed_on_or20s(158, "excise") is True,
      "the OR-20-S eligibility filter admits 158 and refuses 341",
      "the OR-20-S eligibility filter is wrong")
check(341 in OR.OR_SAFE_SHARED_BEYOND_APPENDIX_A and OR.OR_COLLISION_COUNT == 12,
      "adding 341 to the corporate table does NOT change the count of twelve -- its labels AGREE",
      "seeding 341 changed the collision count; the ledger is unstable")

# income-filers-only eligibility (361/364) -- a checkbox-driven code rule.
check(OR.or_corporate_code_allowed_on_or20s(361, "excise") is False
      and OR.or_corporate_code_allowed_on_or20s(361, "income") is True,
      "code 361 is barred on an EXCISE return and permitted on an INCOME return",
      "the income-filers-only rule is not enforced for code 361")
check(OR.or_corporate_code_allowed_on_or20s(364, "excise") is False
      and OR.or_corporate_code_allowed_on_or20s(364, "income") is True,
      "code 364 is barred on an EXCISE return and permitted on an INCOME return",
      "the income-filers-only rule is not enforced for code 364")

# The seven verified '(not used)' markers -- absences, pinned.
ind_codes = {r["code"] for r in OR.OR_CODES_INDIVIDUAL}
corp_codes = {r["code"] for r in OR.OR_ASC_CORP_CODES}
check(all(c in ind_codes and c not in corp_codes for c in OR.OR_CODES_INDIVIDUAL_ONLY),
      "152, 153 and 354 are INDIVIDUAL-ONLY -- verified ABSENT from Appendix A",
      f"individual-only markers wrong: {[c for c in OR.OR_CODES_INDIVIDUAL_ONLY if c in corp_codes]}")
check(all(c in corp_codes and c not in ind_codes for c in OR.OR_CODES_CORPORATE_ONLY),
      "174, 353, 364 and 375 are CORPORATE-ONLY -- verified ABSENT from Publication OR-CODES",
      f"corporate-only markers wrong: {[c for c in OR.OR_CODES_CORPORATE_ONLY if c in ind_codes]}")
check(359 in ind_codes and 375 in corp_codes and 359 not in corp_codes and 375 not in ind_codes,
      "marijuana does NOT share a code (359 individual / 375 corporate) while psilocybin does (385)",
      "the marijuana code split is wrong")
check(385 in ind_codes and 385 in corp_codes,
      "psilocybin shares 385 across BOTH namespaces", "385 is not shared")

# label-driven lookup survives; 336/338/344 fail naive string equality.
label_mismatch = []
for c in OR.OR_SAFE_SHARED_CODES:
    try:
        a = OR.or_code(OR.NS_INDIVIDUAL, c)["label"]
        b = OR.or_code(OR.NS_CORPORATE, c)["label"]
        if a != b:
            label_mismatch.append(c)
    except KeyError:
        label_mismatch.append(c)
check(336 in label_mismatch,
      "336's LABELS DIFFER across the namespaces even though the item is the same -- naive string "
      "equality fails on three of the eight safe shared codes (336, 338, 344)",
      "336's label divergence is not encoded")
gp = OR.or_code_by_label(OR.NS_CORPORATE,
                         "Gain or loss on disposition of depreciable property", OR.K_ADDITION)
check(gp["code"] == 158, "label-driven lookup resolves the corporate depreciable-property item to 158",
      f"label lookup gave {gp['code']}")
try:
    OR.or_code_by_label(None, "anything")
    FAILURES.append("or_code_by_label accepted a None namespace")
except OR.OregonCodeNamespaceError:
    PASSES.append("or_code_by_label REFUSES a namespace-free lookup too")

# ==========================================================================
# 6a. ARITHMETIC ORACLE -- FORM OR-65
# ==========================================================================
check(OR.or65_must_file(False, True) is True and OR.or65_line_3a(False, False, True) == 0,
      "THE TWO GATES: resident partners with no Oregon activity FILE and OWE NOTHING",
      "the two-gate split is not encoded")
check(OR.or65_must_file(False, False) is False,
      "no filing requirement when both 2A and 2B are No", "the filing gate is wrong")
check(OR.or65_line_3a(True, True, False) == 150,
      "doing business + Oregon-source income => $150", "the tax gate is wrong")
check(OR.or65_owes_minimum_tax(True, False, False) is False,
      "doing business but no 2A/2B => no minimum tax (and no filing requirement either)",
      "the tax gate ignored the 2A/2B leg")

tbl = OR.OR65_PRORATION_TABLE[2025]
check(tbl == {1: 13, 2: 25, 3: 38, 4: 50, 5: 63, 6: 75, 7: 88, 8: 100, 9: 113, 10: 125, 11: 138, 12: 150},
      "the OR-65 proration table is the DOR's PUBLISHED 12-row chart, seeded literally",
      f"proration table wrong: {tbl}")
banker = {m: round(150 * m / 12) for m in range(1, 13)}
differ = sorted(m for m in tbl if tbl[m] != banker[m])
check(differ == [1, 5, 9] and [tbl[m] for m in differ] == [13, 63, 113]
      and [banker[m] for m in differ] == [12, 62, 112],
      "PRORATION ORACLE: round-half-to-even diverges from the DOR chart on months 1, 5 and 9 "
      "($12/$62/$112 against $13/$63/$113). NOTE: the source brief says FIVE rows and lists $138 "
      "among the wrong values; $138 is the CORRECT chart value and round-half-to-even reproduces "
      "it, so the brief's arithmetic is wrong on both counts. The mandate to seed the literal "
      "table is unaffected.",
      f"round-half-to-even divergence unexpected: {differ} -> {[banker[m] for m in differ]}")
check(OR.or65_line_3a(True, True, True, accounting_period_change=True, months_in_short_period=9) == 113,
      "9-month accounting-period change => $113 (the DOR's own Example 1), not $112",
      "the 9-month proration value is wrong")
check(OR.or65_line_3a(True, True, True, accounting_period_change=False, months_in_short_period=5) == 150,
      "a FINAL or INITIAL short year is NOT prorated -- $150 (the DOR's Example 2)",
      "a non-accounting-period short year was prorated")
try:
    OR.or65_line_3a(True, True, True, accounting_period_change=True, months_in_short_period=13)
    FAILURES.append("the proration table extrapolated beyond 12 months")
except ValueError:
    PASSES.append("the proration lookup REFUSES to extrapolate beyond the DOR's enumerated 12 rows")

l3 = OR.or65_line_3(150, 200)
check(approx(l3["L3C"], 0) and approx(l3["L3D"], 50),
      "OR-65 lines 3C/3D are mutually exclusive (overpaid $50 => refund, no tax due)",
      f"lines 3C/3D wrong: {l3}")
check(approx(OR.or65_failure_to_file_penalty(12, 8), 3000),
      "failure-to-file exposure = $50 x 12 partners x min(8, 5) months = $3,000",
      "the failure-to-file cap at five months is wrong")
check(OR.or65_k1_delivery(10) == "attach_k1s" and OR.or65_k1_delivery(11) == "summary",
      "K-1 delivery switches at >= 11 partners (the threshold is stated both ways in one bullet)",
      "the K-1 summary threshold is wrong")

# ==========================================================================
# 6b. ARITHMETIC ORACLE -- FORM OR-20-S
# ==========================================================================
check(OR.or20s_minimum_tax("excise") == 150 and OR.or20s_minimum_tax("income") == 0,
      "OR-20-S line 11: $150 for an EXCISE filer, 0 for an INCOME filer",
      "the minimum-tax fork is wrong")
try:
    OR.or20s_minimum_tax("neither")
    FAILURES.append("or20s_minimum_tax accepted an unchecked basis")
except ValueError:
    PASSES.append("or20s_minimum_tax REFUSES an unchecked basis ('One box must be checked')")
check("318.020" in OR.OR20S_MIN_TAX_AUTHORITY_ZERO and "317.090" in OR.OR20S_MIN_TAX_AUTHORITY_150,
      "the $150 and the ZERO carry DIFFERENT authorities (ORS 317.090(2)(b) vs ORS 318.020/318.031)",
      "the zero side is still attributed to ORS 317.090")

check(approx(OR.or20s_calculated_tax(1_000_000), 66000),
      "rate: 6.6% of exactly $1,000,000 = $66,000 (the base constant)", "the low-rate branch is wrong")
check(approx(OR.or20s_calculated_tax(1_500_000), 104000),
      "rate: $66,000 + 7.6% x $500,000 = $104,000", "the high-rate branch is wrong")
check(approx(OR.or20s_calculated_tax(-5000), 0),
      "a negative Oregon taxable income floors at 0 on the <=$1M branch, as printed",
      "the negative floor is wrong")

p1 = OR.or20s_part1(sch_d_part3_line18=-1000, enpi_worksheet=40000,
                    additions_asc_corp_a=5000, subtractions_asc_corp_b=2000,
                    prior_c_corp_nol=3000, apportionment_pct=37.5)
check(approx(p1["L1a"], 0), "line 1a floors a NEGATIVE net recognized built-in gain at $0",
      f"line 1a wrong: {p1['L1a']}")
check(approx(p1["L1c"], 40000) and approx(p1["L4"], 43000) and approx(p1["L7"], 40000),
      "L1c = 1a + 1b; L4 = 1c + 2 - 3; L7 = L4 - L5 on the Oregon-only path",
      f"OR-20-S part 1 arithmetic wrong: {p1}")
check(p1["line7_path"] == "oregon_only", "line 7 takes the Oregon-only path when OR-AP part 2 is absent",
      "line 7 path wrong")
p1b = OR.or20s_part1(sch_d_part3_line18=50000, or_ap_part2_line12=18000)
check(p1b["line7_path"] == "or_ap_part2" and approx(p1b["L7"], 18000),
      "line 7 takes Schedule OR-AP part 2 line 12 wholesale on the multistate path -- NEVER both",
      "the OR-AP part 2 path is not exclusive")
check(approx(p1["L6"], 37.5),
      "LINE 6 SURVIVES A ZERO-TAX RETURN -- the apportionment percentage every nonresident "
      "shareholder needs",
      "line 6 was dropped")

zero = OR.or20s_tax_block(0.0, "excise")
check(approx(zero["L8"], 0) and approx(zero["L10"], 0) and approx(zero["L11"], 150)
      and approx(zero["L12"], 150),
      "the ordinary S corp: L7 = L8 = L10 = 0 and L12 = the $150 minimum",
      f"the zero-tax path is wrong: {zero}")
zero_inc = OR.or20s_tax_block(0.0, "income")
check(approx(zero_inc["L11"], 0) and approx(zero_inc["L12"], 0),
      "an INCOME-tax filer with no tax owes ZERO, not $150",
      f"the income-filer path is wrong: {zero_inc}")

nt = OR.or20s_net_tax(150, carryforward_credits_l15=5000, tax_basis="excise")
check(approx(nt["L15"], 0) and approx(nt["L16"], 150) and nt["L15_limited_by_floor"] is True,
      "CREDIT FLOOR: credits cannot reduce excise tax below the $150 minimum",
      f"the excise credit floor failed: {nt}")
nt_inc = OR.or20s_net_tax(4000, carryforward_credits_l15=5000, tax_basis="income")
check(approx(nt_inc["L15"], 4000) and approx(nt_inc["L16"], 0),
      "CREDIT FLOOR: an income filer's credits may reduce tax to ZERO but no further",
      f"the income credit floor failed: {nt_inc}")
lifo = OR.or20s_net_tax(150, carryforward_credits_l15=5000, lifo_recapture_l17=4000, tax_basis="excise")
check(approx(lifo["L16"], 150) and approx(lifo["L18"], 4150),
      "LIFO ORACLE: line 17 stacks ON TOP of the $150 and CANNOT be absorbed by credits",
      f"the LIFO stacking is wrong: {lifo}")

check(OR.or20s_estimated_required(150) is False
      and OR.or20s_estimated_required(150, high_income_taxpayer=True) is True
      and OR.or20s_estimated_required(500) is True,
      "estimated tax: $150 is under the $500 threshold UNLESS the high-income lookback applies",
      "the estimated-tax gate is wrong")
seg = OR.or_interest_segments(10000, [(2025, 30), (2026, 60)])
check(approx(seg["total"], 10000 * 0.000247 * 30 + 10000 * 0.000219 * 60),
      "interest is SEGMENTED at the calendar-year boundary (0.000247 then 0.000219), never blended",
      f"segmented interest wrong: {seg['total']}")
check(OR.or_daily_interest(2025) == "0.000247" and OR.or_daily_interest(2026) == "0.000219",
      "the daily interest rates are TY-keyed and distinct across the 2025/2026 boundary",
      "the daily interest rates are wrong")

# ==========================================================================
# 6c. ARITHMETIC ORACLE -- FORM OR-21
# ==========================================================================
check(approx(OR.or21_tax(425000), 39825),
      "OR-21 RATE ORACLE: the DOR's worked Example 1 -- $425,000 gives $39,825",
      f"example 1 gave {OR.or21_tax(425000)}")
check(approx(OR.or21_tax(180000), 16200),
      "OR-21 RATE ORACLE: the DOR's worked Example 2 -- $180,000 gives $16,200",
      f"example 2 gave {OR.or21_tax(180000)}")
check(approx(OR.or21_tax(250000), 22500),
      "OR-21 rate is CONTINUOUS at the $250,000 breakpoint -- $22,500 on both branches",
      "the rate is discontinuous at the breakpoint")
mismatch = [x for x in (0, 1, 100, 249_999, 250_000, 250_001, 180_000, 425_000, 1_000_000, 5_000_000)
            if not approx(OR.or21_tax(x), OR.or21_tax_worksheet(x)["f"])]
check(not mismatch,
      "the CLOSED FORM agrees with the DOR's six-step worksheet at every probe, including the boundary",
      f"closed form and DOR worksheet diverge at: {mismatch}")
ws = OR.or21_tax_worksheet(425000)
check(ws["c"] == 175000 and approx(ws["d"], 17325) and ws["e"] == 22500 and approx(ws["f"], 39825),
      "the DOR worksheet reproduces line-by-line: c=175,000 d=17,325 e=22,500 f=39,825",
      f"worksheet lines wrong: {ws}")
ws2 = OR.or21_tax_worksheet(180000)
check(ws2["d"] == 0 and approx(ws2["e"], 16200),
      "worksheet line e takes the FIRST branch (a x 9%) when line d is 0",
      f"worksheet branch wrong: {ws2}")

# The base, and its ONE module fork.
K = {"1": 300000, "2": 10000, "3c": 5000, "4c": 80000, "5": 4000, "4": 4000,
     "6a": 2000, "5a": 2000, "7": 1000, "6": 1000, "8": 500, "9a": 1500,
     "7__": 0, "8a": 1500, "10": 3000, "9": 3000, "11": 250, "10__": 250}
b65 = OR.or21_part_c(M65, {"1": 300000, "2": 10000, "3c": 5000, "4c": 80000, "5": 4000,
                           "6a": 2000, "7": 1000, "8": 500, "9a": 1500, "10": 3000, "11": 250})
b20 = OR.or21_part_c(MS, {"1": 300000, "2": 10000, "3c": 5000, "4": 4000, "5a": 2000,
                          "6": 1000, "7": 500, "8a": 1500, "9": 3000, "10": 250})
check(approx(b65["L9"], 80000) and approx(b20["L9"], 0),
      "MODULE FORK: guaranteed payments are Schedule K line 4c for a 1065 and ZERO for an 1120-S",
      f"the line-9 fork is wrong: 1065={b65['L9']} 1120S={b20['L9']}")
check(approx(b65["L13"], 2000) and approx(b20["L13"], 2000),
      "line 13 COMPOSES two federal lines (1065 8+9a / 1120-S 7+8a)",
      f"line 13 composition wrong: {b65['L13']} / {b20['L13']}")
check(OR.or21_module_line9(M65) == ["4c"] and OR.or21_module_line9(MS) is None,
      "the line-9 source map itself forks by module",
      "the line-9 source map does not fork")
try:
    OR.or21_part_c("1120", {})
    FAILURES.append("or21_part_c accepted an unknown module")
except ValueError:
    PASSES.append("or21_part_c REFUSES an unknown module rather than defaulting silently")
check(approx(b65["L16"] - b20["L16"], 80000),
      "the SAME economic entity yields a base $80,000 apart across the two modules, on line 9 alone",
      "the module fork did not move the base")

# LINE 21 CLOSURE -- the U2 correction.
w = OR.or21_part_c(M65, {"1": 300000, "5": 20000}, non_apportionable_l17=20000,
                   apportionment_pct_l19=100.0)
check(approx(w["L16"], 320000) and approx(w["L18"], 300000) and approx(w["L20"], 300000)
      and approx(w["L21"], 20000) and approx(w["L22"], 320000),
      "LINE 21 ORACLE: a wholly-in-Oregon PTE closes at L22 == L16 only when L21 comes from L17",
      f"line 21 closure failed: {w}")
check(approx(w["L22"], w["L16"]),
      "L22 == L16 for a wholly-in-Oregon PTE -- the ONLY arithmetic that closes",
      "L22 != L16 for a wholly-in-Oregon PTE")
wrong = OR.or21_part_c(M65, {"1": 300000, "5": 20000}, non_apportionable_l17=20000,
                       apportionment_pct_l19=100.0, oregon_allocated_l21=100.0)
check(not approx(wrong["L22"], w["L22"]),
      "LINE 21 ORACLE: following the DOR's literal 'enter the amount from line 19' gives a "
      "DIFFERENT, WRONG line 22 (a percentage added to an income figure)",
      "the wrong-pointer path gave the same answer -- the oracle proves nothing")
check(approx(wrong["L22"], 300100),
      "the buggy path yields L22 = 300,100 -- the visible symptom of a percentage in a dollar field",
      f"buggy L22 unexpected: {wrong['L22']}")

check(OR.or21_stop_do_not_file(0) is True and OR.or21_stop_do_not_file(-1) is True
      and OR.or21_stop_do_not_file(1) is False,
      "THE STOP: line 22 zero or negative => DO NOT FILE (a client instruction, not a return)",
      "the do-not-file stop is wrong")

# ⚠ U5 -- the PROVEN impossibility, with the DOR's own arithmetic.
u5 = OR.or21_md_allocation([100000, 100000, -50000], total_addition=18000, tax_l23=13500, line_22=150000)
check(u5["tie_out_possible"] is False and u5["has_negative_share"] is True,
      "U5 ORACLE: with a NEGATIVE member share the OR-21-MD tie-out is IMPOSSIBLE",
      f"U5 impossibility not detected: {u5['tie_out_possible']}")
check(approx(u5["sum_positive_shares"], 200000) and approx(u5["line_22"], 150000),
      "U5 ORACLE: sum(positive shares) = 200,000 against line 22 = 150,000",
      "the U5 counterexample figures are wrong")
check(approx(u5["as_written_line22_denominator"]["line_5"], 18000),
      "U5 COUNTEREXAMPLE: the rule AS WRITTEN allocates $18,000 of refundable member credit "
      "against $13,500 of entity tax -- 33.3% over",
      f"U5 counterexample wrong: {u5['as_written_line22_denominator']['line_5']}")
check(approx(u5["candidate_positive_share_denominator"]["line_5"], 13500)
      and approx(u5["candidate_positive_share_denominator"]["line_4"], 18000),
      "the CANDIDATE positive-share denominator does tie out -- which is exactly why it is tempting",
      "the candidate denominator does not tie out")
check(u5["candidate_is_dor_guidance"] is False and "NOT cited DOR guidance" in u5["u5_note"],
      "the candidate fix is LABELLED AS NOT DOR GUIDANCE -- it reasons from a tie-out Caution, "
      "not from a cited rule",
      "the candidate fix is not disclaimed; it must never ship as DOR guidance")
u5z = OR.or21_md_allocation([100000, 50000, 0], total_addition=9000, tax_l23=13500, line_22=150000)
check(u5z["tie_out_possible"] is True and u5z["has_negative_share"] is False,
      "U5 REFINEMENT: a ZERO share is HARMLESS -- only a NEGATIVE share breaks the tie-out",
      "a zero share was treated as breaking the tie-out; the original 'zero-or-loss' framing was too broad")
check(approx(u5z["as_written_line22_denominator"]["line_5"], 13500),
      "with no negative share the rule as written ties out exactly to line 23",
      "the zero-share case does not tie out")

# Estimated tax and the annualized worksheet.
est = OR.or21_regular_installment(40000, 30000)
check(approx(est["L2"], 36000) and approx(est["L3"], 30000) and approx(est["L4"], 30000)
      and approx(est["L5"], 7500),
      "OR-21 estimates: the LESSER of 90% current and 100% prior, divided by four",
      f"the estimated worksheet is wrong: {est}")
est_low = OR.or21_regular_installment(900, 5000)
check(est_low["below_threshold"] is True and approx(est_low["L5"], 0),
      "under $1,000 of current-year tax turns underpayment interest off ENTIRELY",
      "the $1,000 threshold is wrong")
est_no_prior = OR.or21_regular_installment(40000, None)
check(approx(est_no_prior["L4"], 36000),
      "with no prior-year election the safe harbour is unavailable and 90% governs",
      "the no-prior-year path is wrong")
ann = OR.or21_annualized_installment(0, 60000)
check(approx(ann["multiplier"], 4) and approx(ann["percentage"], 0.225)
      and approx(ann["L3"], 240000) and approx(ann["L4"], 21600) and approx(ann["L6"], 4860),
      "annualized column A: multiplier 4, cumulative 22.5%, 240,000 annualized, 21,600 tax, 4,860 due",
      f"the annualized worksheet is wrong: {ann}")
check(OR.OR21_ANNUALIZATION_MULTIPLIERS[2025] == ["4", "2.4", "1.5", "1"]
      and OR.OR21_ANNUALIZATION_PERCENTAGES[2025] == ["0.225", "0.45", "0.675", "0.9"],
      "annualization multipliers 4 / 2.4 / 1.5 / 1 and cumulative 22.5 / 45 / 67.5 / 90 percent",
      "the annualization constants are wrong")

pen = OR.or21_late_penalty_interest(4825, 105, interest_calendar_year=2026)
check(approx(pen["penalty"], 241.25) and approx(pen["interest"], 110.95, tol=0.02)
      and pen["line_27"] == 352,
      "PENALTY ORACLE: the DOR's Example 3 -- $241.25 + $110.95 = $352.20, entered as $352",
      f"the penalty example is wrong: {pen}")

k1 = OR.or21_k1_lines(100000, 6000, 9000, 20000, 1200, 1800)
check(approx(k1["L1"], 120000) and approx(k1["L2"], 7200) and approx(k1["L3"], 10800),
      "OR-21-K-1 lines 1-3 are each a SUM ACROSS TWO SCHEDULES (OR-21-MD + OR-21-MD-PT)",
      f"the OR-21-K-1 sums are wrong: {k1}")
check("167" in k1["L2_owner_destination"] and "900" in k1["L3_owner_destination"],
      "the OR-21-K-1 lines carry their published OWNER destinations (codes 167 and 900)",
      "the owner destinations are missing")
legs = OR.or21_owner_legs()
check(len(legs) == 3 and {l["code"] for l in legs} == {167, 900, 387},
      "THREE owner legs encoded: addition 167, refundable credit 900, later subtraction 387",
      f"the owner legs are wrong: {legs}")
c900 = OR.OR_CODES_INDIVIDUAL_REFUNDABLE[0]
check(c900["code"] == 900 and c900["prorated"] is False,
      "code 900 is NOT PRORATED for nonresidents or part-year residents",
      "code 900 is flagged prorated -- that understates every nonresident member's refund")

check(OR.or21_document_state(True, False, False, False) == "election"
      and OR.or21_document_state(False, True, False, False) == "revocation"
      and OR.or21_document_state(False, False, False, True) == "upper_tier_only",
      "THREE Form OR-21 document states, including the NON-ELECTING UPPER-TIER partial return",
      "the OR-21 document states are wrong")
try:
    OR.or21_document_state(True, True, False, False)
    FAILURES.append("Election and Revocation were accepted together")
except ValueError:
    PASSES.append("Election and Revocation are enforced as mutually exclusive")

# ==========================================================================
# 6d. Schedule OR-AP, Schedule OR-K-1 and the due-date calendar
# ==========================================================================
check(approx(OR.or_ap_line23_standard(250000, 1000000), 25.0),
      "Schedule OR-AP line 23: 250,000 / 1,000,000 = 25.0000 percent, four decimals",
      "the standard apportionment worksheet is wrong")
check(OR.or_ap_line23_standard(250000, 0) is None,
      "a ZERO everywhere-denominator yields UNDEFINED, never a silent 0",
      "the zero denominator produced a silent value")
alt = OR.or_ap_line23_alternative([(10, 100), (0, 0), (30, 100), (30, 100)])
check(approx(alt, (10.0 + 30.0 + 30.0) / 3),
      "ALT WORKSHEET ORACLE: the divisor is the number of factors with a POSITIVE column-(b) "
      "denominator (3 here), NOT a constant 4",
      f"the alternative worksheet divisor is wrong: {alt}")
alt4 = OR.or_ap_line23_alternative([(10, 100), (20, 100), (30, 100), (30, 100)])
check(approx(alt4, 22.5),
      "ALT WORKSHEET: a full-factor taxpayer divides by 4, because SALES APPEARS TWICE",
      f"the full-factor alternative worksheet is wrong: {alt4}")

ap_ent = OR.or_ap_part2(500000, nonapportionable_l2=50000, apportionment_pct_l5=40.0,
                        nonapportionable_to_oregon_l7=10000, prior_net_loss_l10a=20000)
ap_own = OR.or_ap_part2(500000, nonapportionable_l2=50000, apportionment_pct_l5=40.0,
                        nonapportionable_to_oregon_l7=10000, prior_net_loss_l10a=20000,
                        purpose=OR.OR_AP_PART2_PURPOSE_OWNER)
check(ap_ent["filed"] is True and ap_own["filed"] is False,
      "D-12 W3: ONE FILED INSTANCE of Schedule OR-AP part 2 plus a SEPARATE OFF-SCHEDULE "
      "owner-source computation",
      "both part-2 evaluations were marked filed")
check(approx(ap_own["L10a"], 0) and approx(ap_own["L10b"], 0) and approx(ap_ent["L10a"], 20000),
      "the owner-source run SUPPRESSES line 10; the entity-level run uses it",
      f"line 10 suppression failed: owner={ap_own['L10a']} entity={ap_ent['L10a']}")
check(approx(ap_ent["L12"], 170000) and approx(ap_own["L12"], 190000),
      "the two evaluations give DIFFERENT line 12s (170,000 filed vs 190,000 owner-source)",
      f"part 2 arithmetic wrong: {ap_ent['L12']} / {ap_own['L12']}")
check("inference" in OR.OR_AP_PART2_L4_IS_INFERENCE.lower()
      and OR.OR_AP_PART2_FILED_INSTANCES[2025] == 1,
      "L4 = L1 - L2 - L3 is cited as an INFERENCE (the DOR publishes no part-2 line instruction "
      "for lines 4, 5, 6 or 9), and only ONE instance is filed",
      "the part-2 inference or the single-instance rule is not encoded")
check("permissive" in OR.OR_AP_PART2_PERMISSIVE_QUOTE.lower()
      or "may use it" in OR.OR_AP_PART2_PERMISSIVE_QUOTE,
      "the DOR's PERMISSIVE part-2 wording is on the record -- the 'run twice' mandate is disproven",
      "the permissive quote is missing")
check(OR.or_guaranteed_payment_ordering() == "apportion_then_attribute",
      "guaranteed payments: APPORTION-THEN-ATTRIBUTE (OAR 150-316-0155, closing U9)",
      "the guaranteed-payment ordering is wrong")

res = OR.or_k1_column_fill(True)
nonres = OR.or_k1_column_fill(False)
check(res["column_b_lines"] == ["19", "20"] and res["column_b_is_apportioned"] is False,
      "OR-K-1 RESIDENT fill: column (b) carries ONLY lines 19 and 20",
      f"the resident K-1 fill is wrong: {res}")
check(len(nonres["column_b_lines"]) == 21 and nonres["column_b_is_apportioned"] is True,
      "OR-K-1 NONRESIDENT fill: both columns, with column (b) = column (a) x apportionment percent",
      f"the nonresident K-1 fill is wrong: {nonres}")
supp = OR.or_k1_pte_e_suppression(True)
check(supp["suppress_pte_e_addition_lines_14_18"] and supp["suppress_pte_e_credit_line_19"]
      and supp["issue_or_21_k1"],
      "PTE-E SUPPRESSION: the election suppresses the addition on OR-K-1 lines 14-18 and the "
      "credit on line 19, and forces a Schedule OR-21-K-1",
      "the PTE-E suppression is wrong")
check(OR.or_k1_pte_e_suppression(False)["suppress_pte_e_credit_line_19"] is False,
      "with no election, nothing is suppressed on Schedule OR-K-1",
      "suppression fired without an election")
check(OR.OR_K1_LINE4_LIVE[M65] is True and OR.OR_K1_LINE4_LIVE[MS] is False,
      "OR-K-1 line 4 (guaranteed payments) is DEAD for an S corporation and must be suppressed by module",
      "the OR-K-1 line 4 module suppression is missing")

dd65 = OR.or_due_date(F65)
dd20 = OR.or_due_date(F20S)
dd21 = OR.or_due_date(F21)
check(dd65["due"] == "2026-03-16" and dd65["extended"] == "2026-09-15",
      "OR-65 due March 16, 2026 (March 15 is a Sunday), extended September 15, 2026, SELF-DECLARED",
      f"OR-65 dates wrong: {dd65}")
check(dd20["due"] == "2026-04-15" and dd20["derived"] is True,
      "OR-20-S due April 15, 2026 -- flagged DERIVED, because the DOR never prints the date",
      f"OR-20-S dates wrong: {dd20}")
check(dd21["due"] == "2026-04-15" and dd21["extended"] == "2026-09-15"
      and dd21.get("extended_unresolved") is True,
      "OR-21 due April 15, 2026; the EXTENDED date is UNRESOLVED and defaults to the EARLIER "
      "September 15 with a diagnostic",
      f"OR-21 dates wrong: {dd21}")
check(dd65["due"] != dd20["due"],
      "OR-65 and OR-20-S differ by a MONTH -- ORS 314.385(1)(b) shifts only the corporate date",
      "the one-month corporate shift is not encoded")
check(len(OR.OR_DUE_DATES[2025]) == 5,
      "FIVE distinct Oregon PTE due dates are seeded (OR-19, OR-65, OR-20-S, OR-21, OR-OC)",
      "the due-date calendar is incomplete")
try:
    OR.or_due_date(F21, 2026)
    FAILURES.append("the due-date table silently served an unkeyed tax year")
except KeyError:
    PASSES.append("the due-date table REFUSES an unkeyed tax year rather than defaulting")

check(OR.OR21_EST_DUE_DATES[2025][1] == "2025-06-16",
      "OR-21 Q2 is JUNE 16, 2025 (June 15 was a Sunday)", "the OR-21 Q2 date is wrong")
check(OR.OR21_EST_DUE_DATES[2025][3] == "2026-01-15"
      and OR.OR20S_EST_QUARTER_MONTH_DAY[2025][3] == (12, 15),
      "THREE quarterly calendars: OR-21 Q4 is January 15 (individual) while OR-20-S Q4 is "
      "December 15 (corporate); Form OR-65 has none",
      "the quarterly calendars are not distinct")
check(OR.OR65_ESTIMATES_REQUIRED[2025] is False,
      "Form OR-65 requires NO estimated payments at all", "the OR-65 estimates negative is missing")

# ==========================================================================
# 7. VERIFIED NEGATIVES AND THE RULINGS -- pinned so nothing is added
#    "for symmetry with other states"
# ==========================================================================
or65_line_numbers = {ln["line_number"] for ln in OR.FORMS[0]["lines"]}
check(not any(ln.lower().startswith("total") for ln in or65_line_numbers),
      "N2: Form OR-65 Schedule I has NO total line -- it does not foot and nothing flows to line 3",
      "a Schedule I total line appeared")
check(not any(("bonus" in (ln.get("description", "") + ln.get("calculation", "")).lower())
              for spec in OR.FORMS for ln in spec["lines"]),
      "N1: NO bonus-depreciation add-back line exists on ANY of the three Oregon forms",
      "a bonus-depreciation line appeared -- Oregon has no TY2025 add-back")
check(not any("179" in (ln.get("calculation", "") or "") and "limit" in (ln.get("calculation", "") or "").lower()
              for spec in OR.FORMS for ln in spec["lines"]),
      "N1: NO state IRC 179 dollar limit or phaseout on any Oregon PTE form",
      "a state 179 limit appeared")
or20s_lines = {ln["line_number"]: ln for ln in OR.FORMS[1]["lines"]}
check(or20s_lines["ES-7"]["line_type"] == "informational",
      "N3: OR-20-S Schedule ES line 7 is seeded as INFORMATIONAL (`Reserved`), not as a credit field",
      "Schedule ES line 7 is not marked informational")
check(OR.OR20S_SCHEDULE_ES_TOTAL_LINE == "8",
      "N3/OR-DEF-2: the Schedule ES total is LINE 8 (the face), not line 7 (the instructions)",
      "the Schedule ES total line is wrong")
check("15" in or20s_lines and "17" in or20s_lines and "16" in or20s_lines,
      "OR-20-S carries line 15 (Section D carryforward credits) and no Section C or E analogue",
      "the OR-20-S credit lines are missing")

check(OR.OR65_SELF_ASSESSES_PENALTY[2025] is False
      and OR.OR20S_SELF_ASSESSES_PENALTY[2025] is True
      and OR.OR21_HAS_FAILURE_TO_FILE_PENALTY[2025] is False
      and OR.OR21_HAS_THREE_YEAR_PENALTY[2025] is False,
      "THREE penalty postures pinned: OR-65 does not self-assess, OR-20-S does, OR-21 has neither "
      "the 20% nor the 100% penalty",
      "the three penalty postures are not distinct")
check(OR.OR21_ELECTION_IS_ANNUAL[2025] is True
      and OR.OR21_ELECTION_BINDS_FUTURE_YEARS[2025] is False
      and OR.OR21_ELECTION_REVOCABLE[2025] is True
      and OR.OR21_ELECTION_RETROACTIVE[2025] is False,
      "the PTE-E election is ANNUAL, REVOCABLE, NEVER retroactive and NOT binding on future years "
      "(the OPPOSITE of Mississippi's)",
      "the PTE-E election attributes are wrong")
check(OR.OR21_CALENDAR_YEAR_ONLY[2025] is True,
      "Form OR-21 is CALENDAR-YEAR ONLY, so a fiscal-year client can hold a fiscal OR-65 and a "
      "calendar OR-21 over overlapping periods",
      "the calendar-year-only rule is missing")
check(OR.OR21_REVOCATION_EXTENSION_PER_DOR[2025] is True
      and OR.OR21_REVOCATION_EXTENSION_PER_STATUTE[2025] is False,
      "U22: the revocation-deadline divergence is encoded BOTH ways -- build to the DOR, diagnose "
      "against the statute",
      "the U22 revocation divergence is not encoded")

check(OR.OR_LOCAL_IN_V1_SCOPE[2025] is False and "NO DECISION TAKEN" in OR.OR_LOCAL_DECISION_STATUS,
      "D-12 W8: Portland / Multnomah / Metro is RED-DEFERRED and NAMED as a routing item with no "
      "decision taken -- neither silently included nor silently excluded",
      "the Portland scope call is not recorded as undecided")
check(OR.OR_METBIT_LINE_MAP["METBIT-65"]["starting_line"] != OR.OR_METBIT_LINE_MAP["P-2025"]["starting_line"]
      and OR.OR_METBIT_LINE_MAP["METBIT-65"]["schedule_k_pull_line"] != OR.OR_METBIT_LINE_MAP["P-2025"]["schedule_k_pull_line"],
      "the METBIT line map DIFFERS from the P-2025/SC-2025 map (line 4 / line 6 vs line 7 / line 10)",
      "the METBIT map was flattened onto the P/SC map -- BUILD-CORRUPTING")
check("Non-business income" in OR.OR_METBIT_LINE_MAP["METBIT-20S"]["line_7_is"],
      "METBIT line 7 is recorded as `Non-business income or loss subtraction` -- reusing the P/SC "
      "map writes ordinary income there and the return still foots",
      "the METBIT line-7 trap is not recorded")
check("PERSONAL" in OR.OR_LIC_205_PREPARER_PRONG_SCOPE
      and "TAXPAYER" in OR.OR_LIC_205_BUSINESS_PRONG_TRIGGER,
      "LIC-2.05: the PREPARER prong is limited to PERSONAL returns and the BUSINESS prong keys off "
      "the TAXPAYER's own federal duty -- the corrected mechanism",
      "the LIC-2.05 prong correction is missing")
check("301.6011-5" in OR.OR_LIC_205_BUSINESS_PRONG_TRIGGER,
      "26 CFR 301.6011-5 is recorded as the Form 1120 rule that does NOT reach 1120-S",
      "the 301.6011-5 caveat is missing")
try:
    OR.or_local_line_map("METBIT-99")
    FAILURES.append("or_local_line_map served an unknown local return")
except KeyError:
    PASSES.append("or_local_line_map REFUSES an unknown local return rather than guessing")

check(OR.or_conformity_fixed_date(2025) == "2023-12-31"
      and OR.or_conformity_fixed_date(2026) == "2025-12-31",
      "THE STALENESS TRIPWIRE: the fixed conformity date is TY-keyed -- 12/31/2023 for TY2025 and "
      "12/31/2025 for TY2026 (SB 1507 sec. 35)",
      "the conformity dates are not TY-keyed")
check(OR.or_conformity_is_stale_for(2026) is True and OR.or_conformity_is_stale_for(2025) is False,
      "TY2026 is flagged STALE against this TY2025 spec",
      "the staleness flag is wrong")
try:
    OR._yk(OR.OR65_MINIMUM_TAX, 2027)
    FAILURES.append("a TY-keyed constant silently defaulted for an unkeyed year")
except KeyError as e:
    check("SB 1507" in str(e),
          "an unkeyed tax year RAISES, and the message names SB 1507 as the reason",
          "the unkeyed-year error does not explain why")
check("rolling" in OR.OR_CONFORMITY_ROLLING_PRONG.lower()
      and "314.011(2)(c)" in OR.OR_CONFORMITY_FIXED_PRONG,
      "the HYBRID is encoded as TWO prongs, not flattened, and the frozen side is the ENUMERATION",
      "the hybrid conformity was flattened")
check(len(OR.OR_CONFORMITY_FROZEN_SECTIONS_ON_PTE) >= 10
      and "ORS 314.772" in OR.OR_CONFORMITY_FROZEN_SECTIONS_ON_PTE
      and "OR-K-1 line 19" in OR.OR_CONFORMITY_FROZEN_SECTIONS_ON_PTE["ORS 314.772"],
      "ORS 314.772 lands on SCHEDULE OR-K-1 LINE 19, not on OR-20-S line 15 (the corrected destination)",
      "the ORS 314.772 destination is still wrong")
check("1375" in OR.OR_CONFORMITY_1375_SPLIT and "inert" in OR.OR_CONFORMITY_1375_SPLIT.lower(),
      "IRC 1375's split across both prongs is recorded and marked INERT for TY2025 (U12)",
      "the IRC 1375 split is not recorded")

check(len(OR.OR_INSTRUCTION_DEFECTS) == 6,
      "SIX FINAL-booklet instruction defects logged (D-12 W2: the face governs, the conflict is logged)",
      f"instruction defect count wrong: {len(OR.OR_INSTRUCTION_DEFECTS)}")
or21_defects = [d for d in OR.OR_INSTRUCTION_DEFECTS if d["form"] == F21]
check(len(or21_defects) == 2 and all("no face" in d["note"].lower() or "has no face" in d["note"].lower()
                                     or "NO FACE" in d["note"] for d in or21_defects[1:]),
      "the OR-21 defects record the COROLLARY -- the 'face governs' rule cannot resolve them, "
      "because Form OR-21 has no face",
      "the no-face corollary is not recorded on the OR-21 defects")
check("NEVER PUBLISHED" in OR.OR21_PROVENANCE.upper() and "INFERENCE" in OR.OR21_PROVENANCE.upper(),
      "every OR-21 line carries the worksheet-provenance stamp, including that the line numbers "
      "are an INFERENCE",
      "the OR-21 provenance stamp is incomplete")
unstamped = [ln["line_number"] for ln in OR.FORMS[2]["lines"]
             if not ln.get("notes") or "Worksheet-sourced" not in ln["notes"]]
check(len(unstamped) <= 6,
      f"the OR-21 line set carries the provenance stamp ({len(OR.FORMS[2]['lines']) - len(unstamped)} "
      f"of {len(OR.FORMS[2]['lines'])} lines; the OR-21-K-1 lines are exempt - that face IS published)",
      f"OR-21 lines missing the provenance stamp: {unstamped}")

# Every RED-DEFER has its own diagnostic on every form that can raise it.
RED_DEFERS = ["D_OR_R1_TRANSIT_SE", "D_OR_R2_PORTLAND_METRO", "D_OR_R2_METBIT_LINE_MAP",
              "D_OR_R3_CPAR", "D_OR_R4_OC_TR", "D_OR_R5_280E_AS_IF", "D_OR_R6_ALT_APPORTIONMENT",
              "D_OR_R7_DOUBLE_WEIGHTED", "D_OR_R8_BROADCASTERS", "D_OR_R9_FCG20", "D_OR_R10_OR24",
              "D_OR_R11_PCR", "D_OR_R12_INSURANCE_FIN", "D_OR_R13_PART_YEAR_OWNER",
              "D_OR_R16_LOSS_MEMBER_PTE"]
missing_rd = [d for d in RED_DEFERS
              if not FormDiagnostic.objects.filter(tax_form__jurisdiction="OR", diagnostic_id=d).exists()]
check(not missing_rd, f"all {len(RED_DEFERS)} shared RED-DEFERS carry their own diagnostic -- NO SILENT GAP",
      f"RED-DEFERS with no diagnostic: {missing_rd}")
for did in ("D_OR21_R14_MEF_SCHEMA", "D_OR21_R15_MD_DENOMINATOR"):
    check(FormDiagnostic.objects.filter(tax_form=f21, diagnostic_id=did, severity="error").exists(),
          f"the genuinely BLOCKED item {did} is a RED-DEFER on OR_21",
          f"{did} is missing or is not an error-severity diagnostic")
md = FormDiagnostic.objects.get(tax_form=f21, diagnostic_id="D_OR21_R15_MD_DENOMINATOR")
check("NOT DOR GUIDANCE" in md.notes.upper() or "NOT FROM ANY CITED RULE" in md.notes.upper(),
      "the U5 diagnostic states plainly that the obvious fix is NOT DOR guidance",
      "the U5 diagnostic does not disclaim the proposed fix")
mef = FormDiagnostic.objects.get(tax_form=f21, diagnostic_id="D_OR21_R14_MEF_SCHEMA")
check("NOT YET SENT" in mef.notes.upper() or "NOT SENT" in mef.notes.upper(),
      "the MeF diagnostic records that the unlocking DOR request is decided but UNSENT",
      "the MeF diagnostic does not record the unsent action")
check(FormDiagnostic.objects.filter(tax_form=f20s, diagnostic_id="D_OR20S_L15_U24_UNPULLED",
                                    severity="error").exists(),
      "U24 blocks OR-20-S line 15 with its own error diagnostic",
      "the U24 blocker diagnostic is missing")

for form in ALL_FORMS:
    check(FormDiagnostic.objects.filter(tax_form=form, diagnostic_id="D_OR_TY2026_CONFORMITY_STALE").exists(),
          f"{form.form_number} carries the TY2026 statutory staleness diagnostic",
          f"{form.form_number} is missing the staleness tripwire diagnostic")
    check(FormDiagnostic.objects.filter(tax_form=form, diagnostic_id="D_OR_CODE_NAMESPACE_REQUIRED").exists(),
          f"{form.form_number} carries the code-namespace diagnostic",
          f"{form.form_number} is missing the code-namespace diagnostic")

# ==========================================================================
# Report
# ==========================================================================
print("\n" + "=" * 78)
print(f"OR_65 / OR_20_S / OR_21 validation -- {len(PASSES)} PASS / {len(FAILURES)} FAIL "
      f"({len(PASSES) + len(FAILURES)} assertions)")
print("=" * 78)
if FAILURES:
    print("\nFAILURES:")
    for f in FAILURES:
        print(f"  [FAIL] {f}")
else:
    print("\nAll assertions passed.")
print("")
for form in ALL_FORMS:
    print(f"Seeded {form.form_number}: "
          f"facts {FormFact.objects.filter(tax_form=form).count()} / "
          f"rules {FormRule.objects.filter(tax_form=form).count()} / "
          f"lines {FormLine.objects.filter(tax_form=form).count()} / "
          f"diagnostics {FormDiagnostic.objects.filter(tax_form=form).count()} / "
          f"scenarios {TestScenario.objects.filter(tax_form=form).count()} / "
          f"authority links {RuleAuthorityLink.objects.filter(form_rule__tax_form=form).count()}")
print(f"Shared: flow assertions {FlowAssertion.objects.filter(assertion_id__startswith='FA-OR').count()} / "
      f"sources {AuthoritySource.objects.filter(source_code__startswith='OR_').count()} / "
      f"topics {AuthorityTopic.objects.filter(topic_code__startswith='or_').count()} / "
      f"form links {AuthorityFormLink.objects.filter(form_code__startswith='OR_').count()}")
print(f"Code tables: individual {len(OR.OR_CODES_INDIVIDUAL)} / corporate {len(OR.OR_ASC_CORP_CODES)} / "
      f"corporate credit {len(OR.OR_ASC_CORP_CREDIT_CODES)} / colliding {OR.OR_COLLISION_COUNT}")
print(f"READY_TO_SEED on disk: {OR.READY_TO_SEED} (MUST remain False -- Gate 1 is open for Oregon)")
sys.exit(1 if FAILURES else 0)
