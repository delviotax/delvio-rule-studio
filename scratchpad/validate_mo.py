"""Throwaway-SQLite validation for the Missouri PTE specs (WO-W04-PTE, Wave 4).

MO_1065 (Form MO-1065) + MO_1120S (Form MO-1120S) + MO_PTE (Form MO-PTE, the
SALT Parity Act elective tax -- ⚠ filed IN ADDITION TO the other two, not
instead of them), with Form MO-MS PTE and Schedule PTE-BD carried as COMPUTING
SUB-SPECS inside MO_PTE per campaign D-12 Group B.

Checks, in order:
  1. THE SEED GUARD -- asserted to REFUSE, and asserted to leave the DB CLEAN.
     Pins the MECHANISM, not the disk value, then flips IN MEMORY ONLY.
  2. CharField caps -- introspected from the REAL model fields via _meta, never
     hardcoded. SQLite does NOT enforce max_length; Postgres does. Wave 3's
     harnesses caught four topic_name values over the 255 cap that were
     INVISIBLE IN SQLITE, and the Arizona pass had a 390-character CITATION blow
     its cap during Tier-1.
  3. CHOICE-FIELD VALIDITY -- Django does NOT validate `choices` on save(), so
     an invalid enum rides straight through SQLite AND Postgres and only
     surfaces downstream as a broken export. Introspected from _meta too.
  4. Structural integrity -- THREE forms and only three (D-12 Group B), D-9
     namespacing, every rule authority-linked, no duplicate ids, rule_links
     referencing defined rules.
  5. THE RULINGS THAT BIND THIS WAVE -- both-returns-filed, the e-file
     inversion and the A6 privacy ruling, the two client-harm paths, the U4
     flip, the L5/L6 non-reconciliation, C11, the opt-out two-field rule,
     PTE-BD sum-then-floor, the conjunctive withholding exceptions, the
     no-scanline ruling, and the advisory-only capital-gain treatment.
  6. Arithmetic oracles -- the MO-PTE Page 1 and Page 2 chains, MO-MS PTE's
     back-solve and its hard RED, the rounded-product rule, PTE-BD Line 8's two
     readings, the DOR's own 10/70 = 14 and $20,000/$16,000/80% examples, the
     MO-MSS six-step example, the withholding bases, the $500 floor and the
     Name Control algorithm.
  7. VERIFIED NEGATIVES -- pinned so a later contributor cannot quietly add a
     field "for symmetry with other states".

ASCII-only. Run: poetry run python scratchpad/validate_mo.py
"""
import os
import sys

PROJECT_ROOT = r"D:\dev\delvio-rule-studio"
sys.path.insert(0, PROJECT_ROOT)

SQLITE_PATH = os.path.join(PROJECT_ROOT, "scratchpad", "validate_mo.sqlite3")
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
from specs.management.commands import load_mo_pte as MO  # noqa: E402

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
# there, so the Missouri anchors in EXISTING_SOURCES_TO_REFERENCE resolve. Seed
# it here too, so the harness tests the same wiring the prod seed will see.
try:
    call_command("load_state_conformity", verbosity=0)
    PASSES.append("Tier-1 conformity batch seeded into the throwaway DB (mirrors prod, campaign D-10)")
except Exception as exc:  # noqa: BLE001
    FAILURES.append(f"could not seed the Tier-1 conformity batch: {exc!r}")

F65, F20S, FPTE = MO.FORM_CODE_MO1065, MO.FORM_CODE_MO1120S, MO.FORM_CODE_MOPTE

# ==========================================================================
# 1. THE SEED GUARD
# ==========================================================================
_shipped = MO.READY_TO_SEED
check(_shipped is False,
      "READY_TO_SEED ships FALSE on disk -- the Gate-1 SEED approval has NOT been taken for Missouri",
      f"READY_TO_SEED SHIPPED {_shipped!r} -- it MUST ship False; D-12 approved the wave SCOPE, "
      "not the seed")

try:
    call_command("load_mo_pte", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: the loader seeded with READY_TO_SEED = False")
except CommandError as e:
    msg = str(e)
    check("REFUSING TO SEED" in msg, "guard REFUSES to seed while READY_TO_SEED is False",
          "guard raised CommandError but without the refusal banner")
    check("Gate 1 has NOT been taken" in msg,
          "guard states plainly that the Gate-1 seed approval is open for Missouri",
          "guard message does not say Gate 1 is open")
    check("U8" in msg and "IRS" in msg,
          "guard names U8 -- the federal line references are uncross-checked against the FINAL IRS forms",
          "guard message omits the U8 blocker")
    check("U4" in msg and "143.421.4" in msg and "APPLICATION" in msg.upper(),
          "guard names the NARROWED U4 and the 143.421.4 'on application' problem",
          "guard message omits the narrowed U4")
    check("FREE PREPARER ELECTION" in msg.upper(),
          "guard records that MO-NRP Part 3 must NOT default to a free preparer election",
          "guard does not carry the Part 3 non-default instruction")
    check("U9" in msg and "DOUBLE-COUNT" in msg.upper(),
          "guard names U9 and the double-counting withholding base",
          "guard message omits U9")
    check("U11" in msg and "U14" in msg and "U15" in msg and "U17" in msg and "U20" in msg,
          "guard enumerates the load-bearing open items (U11/U14/U15/U17/U20)",
          "guard message omits one or more load-bearing open items")
    check("U27" in msg and "MO-3NR" in msg,
          "guard names U27 -- Form MO-PTE Opt-Out prints Form MO-3NR's scanline",
          "guard message omits the U27 scanline defect")
    check("10-2.436(11)" in msg and "10-2.436(8)" in msg,
          "guard names BOTH client-harm regulations (credit poisoning and surviving withholding)",
          "guard message omits one of the two client-harm regulations")
    check("4349" in msg and "5629" in msg,
          "guard records that MO-PTE rides the substitute-forms track and it is not set up",
          "guard message omits the substitute-forms track")
    check("Virginia" in msg and "502" in msg,
          "guard tells the next reader NOT to port the Virginia 502 / 502PTET fork",
          "guard omits the do-not-port-Virginia warning")
    check("143.121.2(3)" in msg,
          "guard records that the depreciation negative is closed AT THE STATUTE",
          "guard omits the statutory basis of the depreciation negative")
    check("D-10" in msg and "BUILD TO THE FORM" in msg.upper(),
          "guard records that the capital-gain question is RULED and must not be re-opened",
          "guard omits the D-10 capital-gain ruling")
    check(f"READY_TO_SEED = {_shipped}" in msg, "guard reports the sentinel value it saw",
          "guard message omits the sentinel value")
    check("DO NOT RELAX THIS GUARD" in msg,
          "guard tells the next reader not to relax it",
          "guard omits the do-not-relax warning")
    check("22.11" in msg or "SEC. 22" in msg,
          "guard points at the brief's section 22 (and 22.11) as governing",
          "guard does not name the governing verification section")
except Exception as e:  # noqa: BLE001
    FAILURES.append(f"guard raised the WRONG exception type: {e!r}")

check(TaxForm.objects.filter(jurisdiction="MO").count() == 0,
      "guard left the DB CLEAN -- no Missouri TaxForm rows were written while gated",
      "guard refused but Missouri rows were still written")
check(FormRule.objects.filter(rule_id__startswith="R-MO").count() == 0,
      "guard left the DB CLEAN -- no Missouri FormRule rows were written while gated",
      "guard refused but Missouri rules were still written")
check(FlowAssertion.objects.filter(assertion_id__startswith="FA-MO").count() == 0,
      "guard left the DB CLEAN -- no Missouri FlowAssertion rows were written while gated",
      "guard refused but Missouri flow assertions were still written")
check(AuthoritySource.objects.filter(source_code__startswith="MO_2025_FORM_").count() == 0,
      "guard left the DB CLEAN -- no new Missouri AuthoritySource rows were written while gated",
      "guard refused but Missouri sources were still written")

# ⚠ The guard must ALSO refuse on a structural violation even if the sentinel
# were flipped. Pin the MECHANISM by flipping the sentinel and breaking an
# invariant IN MEMORY, then restore.
MO.READY_TO_SEED = True
_saved_179 = MO.MO_SECTION_179_STATE_LIMIT
MO.MO_SECTION_179_STATE_LIMIT = 2500000
try:
    call_command("load_mo_pte", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE on an invented Missouri IRC 179 figure")
except CommandError as e:
    check("MISSOURI DEPRECIATION FIGURE HAS BEEN INVENTED" in str(e),
          "guard REFUSES even with the sentinel True if a Missouri IRC 179 figure is invented",
          "guard fired but without naming the invented depreciation figure")
except Exception as e:  # noqa: BLE001
    FAILURES.append(f"the 179 guard raised the WRONG exception type: {e!r}")
finally:
    MO.MO_SECTION_179_STATE_LIMIT = _saved_179

_saved_email = MO.MO_AUTOMATE_EMAIL_SUBMISSION
MO.MO_AUTOMATE_EMAIL_SUBMISSION = True
try:
    call_command("load_mo_pte", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE when the A6 e-mail-automation ruling was flipped")
except CommandError as e:
    check("A6 forbids it" in str(e),
          "guard REFUSES if MO_AUTOMATE_EMAIL_SUBMISSION is flipped (campaign D-12 A6)",
          "guard fired but without naming the A6 privacy ruling")
except Exception as e:  # noqa: BLE001
    FAILURES.append(f"the A6 guard raised the WRONG exception type: {e!r}")
finally:
    MO.MO_AUTOMATE_EMAIL_SUBMISSION = _saved_email

check(TaxForm.objects.filter(jurisdiction="MO").count() == 0,
      "the structural guards ALSO left the DB clean",
      "a structural guard refused but Missouri rows were still written")

# Now the real in-memory-only seed.
try:
    call_command("load_mo_pte", verbosity=0)
    PASSES.append("loader ran + seeded into throwaway SQLite without error (in-memory flip only)")
except Exception as e:  # noqa: BLE001
    FAILURES.append(f"load_mo_pte raised: {e!r}")
    print("\n".join(FAILURES))
    sys.exit(1)
finally:
    MO.READY_TO_SEED = _shipped   # never leave the module mutated

f65 = TaxForm.objects.get(form_number=F65, jurisdiction="MO")
f20s = TaxForm.objects.get(form_number=F20S, jurisdiction="MO")
fpte = TaxForm.objects.get(form_number=FPTE, jurisdiction="MO")
ALL_FORMS = [f65, f20s, fpte]

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
    "AuthoritySource.jurisdiction_code": AuthoritySource._meta.get_field("jurisdiction_code").max_length,
    "AuthoritySource.entity_type_code": AuthoritySource._meta.get_field("entity_type_code").max_length,
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
        measure(f"line_number={form.form_number}/{ln.line_number}", ln.line_number, "FormLine.line_number")
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

for fa in FlowAssertion.objects.filter(assertion_id__startswith="FA-MO"):
    measure(f"assertion_id={fa.assertion_id}", fa.assertion_id, "FlowAssertion.assertion_id")
    measure(f"fa.title[{fa.assertion_id}]", fa.title, "FlowAssertion.title")
    measure(f"fa.bug_ref[{fa.assertion_id}]", fa.bug_reference, "FlowAssertion.bug_reference")
for s in AuthoritySource.objects.filter(source_code__startswith="MO_"):
    measure(f"source_code={s.source_code}", s.source_code, "AuthoritySource.source_code")
    measure(f"citation[{s.source_code}]", s.citation, "AuthoritySource.citation")
    measure(f"issuer[{s.source_code}]", s.issuer, "AuthoritySource.issuer")
    measure(f"jurisdiction[{s.source_code}]", s.jurisdiction_code, "AuthoritySource.jurisdiction_code")
    measure(f"entity_type[{s.source_code}]", s.entity_type_code, "AuthoritySource.entity_type_code")
    for exc in AuthorityExcerpt.objects.filter(authority_source=s):
        measure(f"excerpt_label[{s.source_code}]", exc.excerpt_label, "AuthorityExcerpt.excerpt_label")
        measure(f"location_ref[{s.source_code}]", exc.location_reference, "AuthorityExcerpt.location_reference")
for tp in AuthorityTopic.objects.filter(topic_code__startswith="mo_"):
    measure(f"topic_code={tp.topic_code}", tp.topic_code, "AuthorityTopic.topic_code")
    measure(f"topic_name={tp.topic_code}", tp.topic_name, "AuthorityTopic.topic_name")
for afl in AuthorityFormLink.objects.filter(form_code__startswith="MO_"):
    measure(f"form_code={afl.form_code}", afl.form_code, "AuthorityFormLink.form_code")

check(not viol, "CharField caps OK -- every seeded value fits its REAL model field",
      "CAP VIOLATIONS (Postgres would truncate/reject; SQLite silently accepts):\n    "
      + "\n    ".join(viol))

# ==========================================================================
# 3. CHOICE-FIELD VALIDITY
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

_mo_sources = list(AuthoritySource.objects.filter(source_code__startswith="MO_"))
check_choice(AuthoritySource, "source_type", _mo_sources, "source_code")
check_choice(AuthoritySource, "source_rank", _mo_sources, "source_code")
check_choice(AuthoritySource, "current_status", _mo_sources, "source_code")
check_choice(AuthorityFormLink, "link_type",
             list(AuthorityFormLink.objects.filter(form_code__startswith="MO_")), "form_code")
check_choice(RuleAuthorityLink, "support_level",
             list(RuleAuthorityLink.objects.filter(form_rule__tax_form__jurisdiction="MO")), "support_level")
_mo_fa = list(FlowAssertion.objects.filter(assertion_id__startswith="FA-MO"))
check_choice(FlowAssertion, "assertion_type", _mo_fa, "assertion_id")
check_choice(FlowAssertion, "status", _mo_fa, "assertion_id")

check(not bad_choice,
      "CHOICE-FIELD VALIDITY OK -- every seeded enum value is a declared model choice",
      "INVALID CHOICE VALUES (Django does NOT validate choices on save; these ride into "
      "Postgres unnoticed):\n    " + "\n    ".join(bad_choice))

# ==========================================================================
# 4. Structural integrity
# ==========================================================================
check(len(MO.FORMS) == 3 and TaxForm.objects.filter(jurisdiction="MO").count() == 3,
      "THREE Missouri specs seeded -- MO_1065, MO_1120S and MO_PTE (campaign D-12 Group B)",
      f"expected 3 Missouri forms, got {TaxForm.objects.filter(jurisdiction='MO').count()}")
check(MO.MO_TOP_LEVEL_SPEC_COUNT == 3,
      "MO_TOP_LEVEL_SPEC_COUNT pins the D-12 Group B ruling at THREE top-level codes",
      f"MO_TOP_LEVEL_SPEC_COUNT is {MO.MO_TOP_LEVEL_SPEC_COUNT}")
check(not TaxForm.objects.filter(jurisdiction="MO",
                                 form_number__in=["MO_MS_PTE", "MO_PTE_BD", "SCHEDULE_PTE_BD"]).exists(),
      "MO-MS PTE and Schedule PTE-BD are SUB-SPECS inside MO_PTE, not TaxForm rows of their own",
      "a fourth Missouri TaxForm row exists -- that re-litigates campaign D-12 Group B")
check(f65.entity_types == ["1065"], "MO_1065 entity_types == ['1065']",
      f"MO_1065 entity_types wrong: {f65.entity_types}")
check(f20s.entity_types == ["1120S"], "MO_1120S entity_types == ['1120S']",
      f"MO_1120S entity_types wrong: {f20s.entity_types}")
check(fpte.entity_types == ["1065", "1120S"],
      "MO_PTE entity_types == ['1065', '1120S'] -- the elective return serves BOTH modules",
      f"MO_PTE entity_types wrong: {fpte.entity_types}")
for form in ALL_FORMS:
    check(form.jurisdiction == "MO" and form.tax_year == 2025 and form.version == 1
          and form.status == "draft",
          f"{form.form_number}: jurisdiction MO / TY2025 / v1 / draft",
          f"{form.form_number} identity wrong: {form.jurisdiction} {form.tax_year} v{form.version} {form.status}")
check({f.form_number for f in ALL_FORMS} == {"MO_1065", "MO_1120S", "MO_PTE"},
      "form codes follow the campaign D-9 <ST>_<FORM> namespace",
      f"form codes wrong: {[f.form_number for f in ALL_FORMS]}")
check(not ({f.form_number for f in ALL_FORMS} & set(MO.FORBIDDEN_BARE_CODES)),
      "no Missouri form code was shortened to a bare federal code (RS holds federal 1065 / 1120S loaders)",
      "a Missouri form code collides with a FEDERAL loader's bare code")

ruleless = [r.rule_id for r in FormRule.objects.filter(tax_form__jurisdiction="MO")
            if not RuleAuthorityLink.objects.filter(form_rule=r).exists()]
check(not ruleless,
      f"all {FormRule.objects.filter(tax_form__jurisdiction='MO').count()} Missouri rules carry >= 1 authority link",
      f"rules with NO authority link: {ruleless}")

for spec in MO.FORMS:
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
        check(not dupes, f"{fn}: no duplicate {label} ({len(ids)} entries)",
              f"{fn}: DUPLICATE {label}: {dupes}")
    # every source_rules reference on a line must name a rule that exists
    orphan_srcs = set()
    for ln in spec["lines"]:
        for rid in ln.get("source_rules", []):
            if rid not in defined:
                orphan_srcs.add(f"{ln['line_number']} -> {rid}")
    check(not orphan_srcs, f"{fn}: every line's source_rules names a defined rule",
          f"{fn}: lines referencing undefined rules: {sorted(orphan_srcs)}")
    # every source_facts reference must name a fact that exists
    fact_keys = {x["fact_key"] for x in spec["facts"]}
    orphan_facts = set()
    for ln in spec["lines"]:
        for fk in ln.get("source_facts", []):
            if fk not in fact_keys:
                orphan_facts.add(f"{ln['line_number']} -> {fk}")
    check(not orphan_facts, f"{fn}: every line's source_facts names a defined fact",
          f"{fn}: lines referencing undefined facts: {sorted(orphan_facts)}")

fa_ids = [a["assertion_id"] for a in MO.FLOW_ASSERTIONS]
check(len(set(fa_ids)) == len(fa_ids), f"no duplicate assertion_id ({len(fa_ids)} flow assertions)",
      f"DUPLICATE assertion_id: {[i for i in fa_ids if fa_ids.count(i) > 1]}")
check(FlowAssertion.objects.filter(assertion_id__startswith="FA-MO").count() == len(fa_ids),
      f"all {len(fa_ids)} Missouri flow assertions seeded", "flow assertion count mismatch")

src_codes = [s["source_code"] for s in MO.AUTHORITY_SOURCES]
check(len(set(src_codes)) == len(src_codes),
      f"no duplicate source_code among the {len(src_codes)} new Missouri sources",
      f"DUPLICATE source_code: {[c for c in src_codes if src_codes.count(c) > 1]}")
defined_srcs = set(src_codes) | set(MO.EXISTING_SOURCES_TO_REFERENCE)
orphan_links = {(sc, fc) for sc, fc, _ in MO.AUTHORITY_FORM_LINKS if sc not in defined_srcs}
check(not orphan_links, "every AUTHORITY_FORM_LINK names a defined or already-seeded source",
      f"form links to undefined sources: {sorted(orphan_links)}")
orphan_rule_srcs = set()
for spec in MO.FORMS:
    for _, sc, _, _ in spec["rule_links"]:
        if sc not in defined_srcs:
            orphan_rule_srcs.add(sc)
check(not orphan_rule_srcs, "every rule_link names a defined or already-seeded source",
      f"rule links to undefined sources: {sorted(orphan_rule_srcs)}")

# EXISTING_SOURCES_TO_REFERENCE must be REAL, and Missouri's must RESOLVE here
# because the Tier-1 conformity batch was seeded above (mirroring prod, D-10).
for code in MO.EXISTING_SOURCES_TO_REFERENCE:
    check(AuthoritySource.objects.filter(source_code=code).exists(),
          f"existing Missouri anchor {code} RESOLVES (seeded by the Tier-1 conformity batch)",
          f"existing Missouri anchor {code} did NOT resolve -- check _state_conformity_tier1.py")
recreated = [s["source_code"] for s in MO.AUTHORITY_SOURCES
             if s["source_code"] in MO.EXISTING_SOURCES_TO_REFERENCE]
check(not recreated, "no already-seeded Missouri source is re-created by this loader",
      f"loader re-creates already-seeded sources: {recreated}")
check("MO_RSMO_143_091" in MO.EXISTING_SOURCES_TO_REFERENCE
      and "MO_RSMO_143_121" in MO.EXISTING_SOURCES_TO_REFERENCE
      and "MO_RSMO_143_436" in MO.EXISTING_SOURCES_TO_REFERENCE,
      "EXISTING_SOURCES_TO_REFERENCE reuses the seeded Missouri conformity anchors",
      "a Missouri conformity anchor is missing from EXISTING_SOURCES_TO_REFERENCE")

# The sub-spec namespaces really are present inside MO_PTE.
pte_lines = {ln["line_number"] for ln in MO.FORMS[2]["lines"]}
check(any(x.startswith("MS-") for x in pte_lines) and any(x.startswith("BD-") for x in pte_lines),
      "MO_PTE carries the MS-* (Form MO-MS PTE) and BD-* (Schedule PTE-BD) sub-spec line namespaces",
      "the MO_PTE sub-spec namespaces are missing")
p65_lines = {ln["line_number"] for ln in MO.FORMS[0]["lines"]}
check(any(x.startswith("NRP-") for x in p65_lines) and any(x.startswith("NR-") for x in p65_lines),
      "MO_1065 carries the NRP-* and NR-* attachment/record namespaces",
      "the MO_1065 attachment namespaces are missing")
p20s_lines = {ln["line_number"] for ln in MO.FORMS[1]["lines"]}
check(any(x.startswith("NRS-") for x in p20s_lines) and any(x.startswith("MSS-") for x in p20s_lines),
      "MO_1120S carries the NRS-* and MSS-* attachment/record namespaces",
      "the MO_1120S attachment namespaces are missing")

# ==========================================================================
# 5. THE RULINGS THAT BIND THIS WAVE
# ==========================================================================
# 5a. MO-PTE is filed IN ADDITION TO -- do NOT port the Virginia fork.
d = FormDiagnostic.objects.get(tax_form=fpte, diagnostic_id="D_MO_PTE_ALSO_FILE_ENTITY_RETURN")
check(d.severity == "error" and "does not substitute" in d.message,
      "the both-returns-filed diagnostic is an ERROR carrying the DOR's verbatim answer",
      "the both-returns diagnostic is missing, weak, or lacks the verbatim DOR authority")
check("Virginia" in d.notes or "VIRGINIA" in d.notes.upper(),
      "the both-returns diagnostic names Virginia as the pattern NOT to port",
      "the both-returns diagnostic does not warn against porting the Virginia fork")
check(FormRule.objects.filter(tax_form=fpte, rule_id="R-MOPTE-BOTH").exists()
      and FormRule.objects.filter(tax_form=f65, rule_id="R-MO65-BOTH").exists(),
      "the both-returns rule is carried on BOTH the elective spec and the partnership spec",
      "the both-returns rule is missing from one of the two specs")

# 5b. The e-file inversion and the A6 privacy ruling.
check(MO.MO_PTE_EFILE_AVAILABLE is False and MO.MO_PTE_ELECTRONIC_PAYMENT_AVAILABLE is False,
      "MO_PTE is pinned as NOT e-fileable and NOT electronically payable",
      "the MO-PTE e-file posture is wrong")
check(MO.MO_MEF_ELIGIBLE_FORMS == (F65, F20S),
      "MeF scope is MO_1065 + MO_1120S ONLY -- the tax-computing return is the manual one",
      f"MeF scope wrong: {MO.MO_MEF_ELIGIBLE_FORMS}")
check(len(MO.MO_EFILE_EVIDENCE) == 6,
      "the e-file finding carries all SIX independent corroborating sources",
      f"expected 6 e-file sources, got {len(MO.MO_EFILE_EVIDENCE)}")
ch = MO.mo_submission_channels(FPTE)
check(any("email" in c or "e-mail" in c for c in ch["channels"]),
      "the e-mail channel IS recorded as a sanctioned channel ('paper-only' would overstate it)",
      "the sanctioned e-mail channel is missing from the channel list")
check(not any("mail to pteincome" in a or "e-mail" in a for a in ch["delvio_automates"]),
      "⚠ A6: Delvio does NOT automate the Department's e-mail submission channel",
      "the e-mail channel appears in delvio_automates -- campaign D-12 A6 forbids it")
check(MO.mo_email_channel_is_automatable() is False,
      "mo_email_channel_is_automatable() returns False (the A6 privacy ruling, pinned)",
      "mo_email_channel_is_automatable() did not return False")
check(MO.mo_submission_channels(F65)["mef"] is True
      and MO.mo_submission_channels(F20S)["mef"] is True,
      "MO_1065 and MO_1120S ARE MeF-eligible -- the inversion is real",
      "an entity return is not marked MeF-eligible")

# 5c. The two client-harm paths.
d = FormDiagnostic.objects.get(tax_form=fpte, diagnostic_id="D_MO_TC_POISONS_CREDIT")
check(d.severity == "error", "the MO-TC credit-poisoning diagnostic is a HARD (error) diagnostic",
      f"the credit-poisoning diagnostic is severity {d.severity}, must be error")
check("10-2.436(11)" in d.message and "actually paid" in d.message.lower(),
      "the credit-poisoning diagnostic cites 12 CSR 10-2.436(11) and 'tax actually paid'",
      "the credit-poisoning diagnostic lacks its regulatory citation")
d = FormDiagnostic.objects.get(tax_form=fpte, diagnostic_id="D_MO_WH_SURVIVES_ELECTION")
check(d.severity == "error" and "10-2.436(8)" in d.message,
      "the surviving-withholding diagnostic is a HARD diagnostic citing 12 CSR 10-2.436(8)",
      "the surviving-withholding diagnostic is missing, weak, or uncited")
check("only in the regulation" in d.message.lower() or "NOWHERE ON FORM MO-PTE" in d.message,
      "the surviving-withholding diagnostic records that it appears ONLY in the regulation",
      "the surviving-withholding diagnostic does not record where the rule is (and is not) stated")
check(MO.MO_WH_SURVIVES_ELECTION is True,
      "MO_WH_SURVIVES_ELECTION is pinned True (campaign D-12 C6)",
      "MO_WH_SURVIVES_ELECTION is not True")

# 5d. THE U4 FLIP -- expected-ZERO, and the meaning is recorded.
exp = MO.MO_SOURCING_EXPECTATIONS[(MO.REGIME_143_455, MO.REGIME_NRP_PART3)]
check(exp["expected_delta"] == "ZERO" and exp["reconcile"] is True,
      "⚠ THE U4 FLIP: MO-NRP vs MO-MS PTE is EXPECTED-ZERO and IS reconciled",
      f"the U4 expectation is wrong: {exp['expected_delta']}")
check("PROBABLE ERROR" in exp["on_nonzero"],
      "a non-zero MO-NRP / MO-MS PTE delta now reads as a PROBABLE ERROR, not regime disagreement",
      "the flipped meaning of the divergence diagnostic is not recorded")
res = MO.mo_sourcing_divergence(MO.REGIME_143_455, MO.REGIME_NRP_PART3, 62.5, 48.0)
check(approx(res["delta"], 14.5) and res["severity"] == "warning",
      "a non-zero MO-NRP / MO-MS PTE delta raises a warning",
      f"the divergence computation is wrong: {res}")
res0 = MO.mo_sourcing_divergence(MO.REGIME_143_455, MO.REGIME_NRP_PART3, 62.5, 62.5)
check(res0["delta"] == 0.0 and res0["severity"] is None,
      "an agreeing MO-NRP / MO-MS PTE pair raises nothing -- agreement is now the NORMAL case",
      f"an agreeing pair still raised: {res0}")
check("MO_1065" in {fn for fn in [f65.form_number]} and FormDiagnostic.objects.filter(
    tax_form=f65, diagnostic_id="D_MO_NRP_MSPTE_DELTA").exists(),
      "the MO-NRP / MO-MS PTE divergence diagnostic exists on MO_1065",
      "the divergence diagnostic is missing")
check("12 CSR 10-2.190" in MO.MO_SOURCING_REGIMES[MO.REGIME_143_455]["authority"]
      and "10-2.255" in MO.MO_SOURCING_REGIMES[MO.REGIME_143_455]["authority"],
      "the delegation chain (10-2.190 -> 10-2.255 -> 143.455) is recorded on the regime",
      "the U4 delegation chain is not recorded")
check("does not exist" in MO.MO_NO_143_181_REGULATION.lower()
      and "10-2.130" in MO.MO_NO_143_181_REGULATION,
      "the NEGATIVE FINDING is recorded: no live regulation under 143.181 governs partnership sourcing",
      "the 143.181 negative finding is not recorded")

# 5e. The narrowed U4 residue -- Part 3 must NOT default to a free election.
p3 = MO.mo_nrp_part3_available()
check(p3["available"] is False and "GATE-1" in p3["status"],
      "MO-NRP Part 3 is NOT offered as a free preparer election -- it is a Gate-1 seed question",
      f"MO-NRP Part 3 availability is wrong: {p3}")
check("on application" in p3["gate1_question"].lower() and "143.421.4" in p3["gate1_question"],
      "the Part 3 Gate-1 question names 143.421.4's 'on application' requirement",
      "the Part 3 Gate-1 question is incomplete")
check(FormDiagnostic.objects.filter(tax_form=f65, diagnostic_id="D_MO65_NRP_PART3_BASIS").exists(),
      "the narrowed U4 carries its own diagnostic on MO_1065",
      "the narrowed U4 has no diagnostic -- that is a silent gap")

# 5f. THE SEVERE HALF -- L5 vs L6 must NOT be reconciled.
res = MO.mo_sourcing_divergence(MO.REGIME_143_455, MO.REGIME_BRAINS, 60.0, 45.0)
check(res["reconcile"] is False and res["delta"] is None and res["severity"] == "info",
      "⚠⚠ L5 vs L6: the engine REFUSES to compute a reconciliation (campaign D-12 C3)",
      f"the L5/L6 pair was reconciled anyway: {res}")
check(MO.MO_SOURCING_REGIMES[MO.REGIME_BRAINS]["quantitative"] is False,
      "the 'brains of the operation' regime is marked QUALITATIVE -- there is nothing to reconcile to",
      "the brains regime is marked quantitative")
check("U17" in MO.MO_SOURCING_REGIMES[MO.REGIME_BRAINS]["authority"],
      "U17 is recorded as FULLY OPEN on the brains regime",
      "U17 is not recorded on the brains regime")
d = FormDiagnostic.objects.get(tax_form=fpte, diagnostic_id="D_MO_L5_L6_SOURCING")
check(d.severity == "info" and "NOT an error" in d.message,
      "the L5/L6 diagnostic is INFORMATIONAL and says a difference is not an error",
      "the L5/L6 diagnostic treats the divergence as an error")

# 5g. C11 -- only FOUR and SIX are mileage-driven.
mm = MO.mo_mileage_note_defect()
check(MO.MO_MILEAGE_METHODS == ("4", "6"),
      "C11: only Methods FOUR and SIX are mileage-driven",
      f"the mileage-driven set is wrong: {MO.MO_MILEAGE_METHODS}")
check(mm["defective_for"] == ("3", "5") and mm["count"] == 2,
      "C11: the face note is defective for TWO methods -- Three AND Five, not one",
      f"the C11 defect scope is wrong: {mm['defective_for']}")
check(MO.MO_APPORTIONMENT_METHODS["3"]["basis"] == MO.BASIS_GROSS_EARNINGS,
      "Method Three is a GROSS-EARNINGS rule (143.455.14), not mileage",
      "Method Three's basis is wrong")
check(MO.MO_APPORTIONMENT_METHODS["5"]["basis"] == MO.BASIS_FLAT_ONE_HALF,
      "Method Five is a FLAT ONE-HALF rule (143.455.16), not mileage",
      "Method Five's basis is wrong")
check("gross earnings" in MO.MO_APPORTIONMENT_METHODS["3"]["verbatim"].lower(),
      "Method Three carries the verbatim 'gross earnings' statutory text",
      "Method Three lacks its verbatim statutory support")
check(FormDiagnostic.objects.filter(tax_form=f20s, diagnostic_id="D_MO_MILEAGE_NOTE_DEFECT").exists(),
      "the C11 mileage-note defect carries its own diagnostic",
      "the C11 defect has no diagnostic")

# 5h. Method Seven is ADVISORY ONLY, never a filing-time gate.
m7 = MO.mo_method_seven_petition_deadline("2025-12-31")
check(m7["days_before_year_end"] == 60 and "ADVISORY" in m7["enforcement"],
      "Method Seven's 60-day petition deadline is ADVISORY ONLY, never a filing-time gate",
      f"the Method Seven deadline posture is wrong: {m7['enforcement']}")
check("10-2.076(2)(G)" in m7["authority"],
      "the Method Seven deadline is sourced to the REGULATION, so it binds all three lanes",
      "the Method Seven deadline is not sourced to 12 CSR 10-2.076(2)(G)")

# 5i. The opt-out: two separate fields, and the DOR's own 10 / 70 = 14.
mp = MO.mo_member_percentages(10.0, opt_out_percent_total=30.0)
check(approx(mp["k1_percent"], 10.0) and approx(mp["credit_percent"], 14.29),
      "OPT-OUT RE-GROSS-UP ORACLE: 10 / 70 = 14.29% AT THE TWO DECIMALS Column 5 mandates",
      f"the re-gross-up is wrong: {mp}")
# ⚠⚠ THE DEFECT THE HARNESS FOUND. Campaign D-12 Group D names "10 / 70 = 14%"
# as the unit test, but MO-PTE Part B Column 5's OWN instruction says to round
# to TWO DECIMAL PLACES, and 10 / 70 = 14.285714... = 14.29, not 14.00. The
# Department's illustration is rounded to a WHOLE NUMBER against its own column
# rule. Both figures are asserted: the two-decimal truth DRIVES the field, and
# the Department's whole-number illustration is reproduced on its own terms.
check(approx(mp["dor_example_whole_number"], 14.0),
      "the DOR's printed '14%' reproduces exactly when rounded to a WHOLE NUMBER -- which is what "
      "the Department actually did, against its own two-decimal column rule",
      f"the DOR whole-number illustration does not reproduce: {mp}")
check(approx(mp["credit_percent_unrounded"], 14.285714, tol=0.0001),
      "the unrounded re-gross-up (14.285714...) is retained, so neither rounding is lost",
      "the unrounded re-gross-up is missing")
check(approx(MO.MO_OPTOUT_EXAMPLE_ROUNDING_DEFECT["at_two_decimals"], 14.29)
      and "ESCALATED" in MO.MO_OPTOUT_EXAMPLE_ROUNDING_DEFECT["status"],
      "⚠ the DOR's self-contradictory rounding example is RECORDED AND ESCALATED, not papered over",
      "the opt-out example rounding defect is not recorded")
check(FormDiagnostic.objects.filter(tax_form=fpte,
                                    diagnostic_id="D_MO_OPTOUT_EXAMPLE_ROUNDING").exists(),
      "the opt-out example rounding defect carries its own diagnostic",
      "the opt-out rounding defect has no diagnostic")
check(mp["k1_percent"] != mp["credit_percent"] and "k1_percent" in mp and "credit_percent" in mp,
      "the K-1 percentage and the credit percentage are TWO SEPARATE FIELDS",
      "the two percentages were collapsed into one field")
mp0 = MO.mo_member_percentages(25.0, opt_out_percent_total=0.0)
check(approx(mp0["credit_percent"], 25.0) and mp0["regrossed"] is False,
      "with no opt-out the credit percentage equals the K-1 percentage and is NOT marked re-grossed",
      f"the no-opt-out case is wrong: {mp0}")
mpo = MO.mo_member_percentages(30.0, is_opt_out=True)
check(mpo["credit_percent"] is None and mpo["part_b_col6_blank"] and mpo["part_b_col7_not_eligible"],
      "an opt-out member: Column 3 implies Column 7 and a BLANK Column 6 (12 CSR 10-2.436(12)(C))",
      f"the opt-out member case is wrong: {mpo}")
check("carry forward" in mpo["note"].lower(),
      "the opt-out ineligibility carries the pre-opt-out carryforward SAVING CLAUSE",
      "the saving clause is missing from the opt-out note")
check(MO.MO_OPTOUT_MODE == "return_level_recomputation" and len(MO.MO_OPTOUT_RECOMPUTE_SCOPE) == 4,
      "the opt-out is modelled as a RETURN-LEVEL RECOMPUTATION MODE with a four-part scope",
      "the opt-out is not modelled as a recomputation mode")
g = MO.mo_optout_available("2026-04-15", original_return_filed_by_that_date=True)
check(g["available"] is False and g["limb_1_deadline_on_or_after_2025_08_28"] is True
      and g["limb_2_original_return_not_yet_filed"] is False,
      "the opt-out availability gate is CONJUNCTIVE and its SECOND limb is enforced",
      f"the conjunctive opt-out gate is wrong: {g}")
g2 = MO.mo_optout_available("2026-04-15", original_return_filed_by_that_date=False)
check(g2["available"] is True, "both limbs satisfied -> the opt-out is available",
      f"the satisfied case failed: {g2}")

# 5j. PTE-BD Line 8 SUM-THEN-FLOOR, with the alternative recorded but unused.
bd = MO.pte_bd_line8({"1": 300000, "2": -80000, "3": 0, "4": 50000, "5": 0, "6": -40000, "7": -30000})
check(approx(bd["L8"], 200000.0),
      "PTE-BD Line 8 ORACLE: sum-then-floor gives 200,000 on the mixed-sign case",
      f"PTE-BD Line 8 is wrong: {bd['L8']}")
check(approx(bd["alternative_reading_not_built"], 350000.0) and bd["readings_agree"] is False,
      "the drop-negatives reading (350,000) is RECORDED AND NOT USED -- the two differ by 150,000",
      f"the alternative reading is wrong or missing: {bd}")
check(bd["any_negative_row"] is True and bd["sign_convention_unstated"] is True,
      "PTE-BD records the negative row and that the DOR states NO sign convention for Lines 6 and 7",
      "the PTE-BD ambiguity flags are missing")
bdn = MO.pte_bd_line8({"1": -200000, "2": 50000})
check(approx(bdn["L8"], 0.0), "PTE-BD Line 8 floors at zero ('but not below $0')",
      f"the floor failed: {bdn['L8']}")
check(approx(MO.pte_bd_line9(500000), 100000.0) and approx(MO.mo_bid_percent(2025), 0.20),
      "PTE-BD Line 9 ORACLE: 500,000 x 20% = 100,000, with the 20% READ OFF THE FACE",
      "the PTE-BD Line 9 computation or the 20% figure is wrong")
check(FormDiagnostic.objects.filter(tax_form=fpte, diagnostic_id="D_MO_BD_L8_NEGATIVE_ROW").exists(),
      "the PTE-BD Line 8 ambiguity carries its own diagnostic",
      "the PTE-BD Line 8 ambiguity has no diagnostic")

# 5k. Withholding exceptions build to the NARROW CONJUNCTIVE form reading.
check("CONJUNCTIVE" in MO.MO_WH_EXCEPTIONS_READING.upper()
      and "RULED" in MO.MO_WH_EXCEPTIONS_READING.upper(),
      "the withholding exceptions build to the NARROW CONJUNCTIVE form reading, RECORDED AS A RULING",
      f"the withholding exceptions reading is wrong: {MO.MO_WH_EXCEPTIONS_READING}")
check(len(MO.MO_WH_EXCEPTIONS) == 4
      and any(e["id"] == "liquidation_conjunctive" for e in MO.MO_WH_EXCEPTIONS),
      "the five statutory exceptions are encoded as FOUR, with (3)(4)(5) collapsed conjunctively",
      f"the exception set is wrong: {[e['id'] for e in MO.MO_WH_EXCEPTIONS]}")
check("or" in MO.MO_WH_EXCEPTIONS_STATUTE_VERBATIM
      and "closely-held" in MO.MO_WH_EXCEPTIONS_RULING_NOTE,
      "the DISJUNCTIVE statutory text and the reason the literal reading is rejected are both recorded",
      "the statute-vs-form withholding tension is not fully recorded")

# 5l. No scanline on Form MO-PTE Opt-Out in v1.
check(MO.MO_PTE_OPTOUT_PRINT_SCANLINE is False,
      "PRINT NO SCANLINE on Form MO-PTE Opt-Out in v1 (campaign D-12 Group D)",
      "the MO-PTE Opt-Out scanline ruling was not encoded")
check(MO.MO_PTE_OPTOUT_SCANLINE_DEFECT["barcode_actually_belongs_to"] == "Form MO-3NR",
      "the wrong scanline is identified as Form MO-3NR's",
      "the scanline defect is mis-recorded")

# 5m. Capital gain: ADVICE LAYER ONLY. It computes nothing.
adv = MO.mo_capital_gain_advisory(True, True, True)
check(adv["fires"] is True and adv["severity"] == "info" and adv["audience"] == "preparer",
      "the capital-gain advisory fires as a preparer-facing INFORMATIONAL notice",
      f"the capital-gain advisory posture is wrong: {adv['severity']}")
check(adv["computes_comparison"] is False and adv["recommends"] is False
      and adv["optimises"] is False and adv["auto_elects"] is False,
      "⚠⚠ C4: the capital-gain advisory COMPUTES NOTHING, RECOMMENDS NOTHING and ELECTS NOTHING",
      "the capital-gain advisory does more than state the interaction")
check("143.121.3(14)" in adv["text"] and "143.436" in adv["text"],
      "the advisory states the interaction in the Department's own terms and cites both statutes",
      "the advisory is missing one of its required citations")
check(MO.mo_capital_gain_advisory(True, True, False)["fires"] is False,
      "the advisory does NOT fire when no election was made",
      "the advisory fires without an election")
_no_capgain_line = [ln for ln in MO.FORMS[2]["lines"]
                    if "capital gain" in (ln.get("description") or "").lower()]
check(not _no_capgain_line,
      "N4 PINNED: MO_PTE carries NO capital-gain subtraction line (campaign D-10 -- do not add one)",
      f"a capital-gain line was added to MO_PTE: {[l['line_number'] for l in _no_capgain_line]}")
check(MO.mo_capital_gain_entity_relief_active(2025) is False,
      "143.121.3(14)(b) is NOT operative at TY2025's 4.7% top rate -- the form is right",
      "the (14)(b) trigger evaluated True at 4.7%")
check(MO.MO_CAPGAIN_ENTITY_TRIGGER_RATE == 0.045,
      "the (14)(b) staleness tripwire is pinned at a 4.5% top rate",
      "the (14)(b) trigger rate is wrong")
check(FormDiagnostic.objects.filter(tax_form=fpte,
                                    diagnostic_id="D_MO_CAPGAIN_TRIGGER_TRIPWIRE").exists(),
      "the 143.121.3(14)(b) staleness tripwire carries its own diagnostic",
      "the (14)(b) tripwire has no diagnostic")

# ==========================================================================
# 6. ARITHMETIC ORACLES
# ==========================================================================
# 6a. The MO-PTE Page 1 chain, at the FACE rate.
check(approx(MO.mo_pte_rate(2025), 0.047),
      "the 4.7% rate comes from the FORM FACE (never from the DOR FAQ, whose table stops at 2024)",
      f"the MO-PTE rate is wrong: {MO.mo_pte_rate(2025)}")
pg1 = MO.mo_pte_page1(1000000, 50000, 20000, 1030000, 200000, 0, 0, 0)
check(approx(pg1["L4"], 1030000) and approx(pg1["L9"], 830000) and approx(pg1["L10"], 39010.0),
      "MO-PTE PAGE 1 ORACLE: L4 = 1,030,000; L9 = 830,000; L10 = 39,010 at 4.7%",
      f"the Page 1 chain is wrong: {pg1}")
neg7 = MO.mo_pte_page1(0, 0, 0, 500000, 90000, -75000, 0, 0)
check(approx(neg7["L9"], 485000),
      "MO-PTE LINE 7 IS SIGNED: a lower-tier LOSS is ADDED BACK (143.436.5(1))",
      f"the signed Line 7 is wrong: {neg7['L9']}")
flr = MO.mo_pte_page1(0, 0, 0, 100000, 20000, 0, 500000, 0)
check(approx(flr["L8"], 80000) and flr["L8_floored"] is True and approx(flr["L9"], 0.0),
      "MO-PTE LINE 8 FLOOR: a prior-year loss cannot drive Line 9 below zero",
      f"the Line 8 floor is wrong: {flr}")
neg9 = MO.mo_pte_page1(0, 0, 0, -50000, 0, 0, 0, 0)
check(approx(neg9["L10"], 0.0), "MO-PTE Line 10 floors at zero on a Missouri net loss",
      f"the Line 10 floor is wrong: {neg9['L10']}")

# 6b. Page 2, the $1.00 refund floor and the Form 5378 threshold.
pg2 = MO.mo_pte_page2(1000, 0, 1000.60, 0, 0, 0)
check(approx(pg2["L20"], 0.60) and pg2["L23"] == 0.0 and pg2["refund_floored"] is True,
      "MO-PTE $1.00 REFUND FLOOR: a $0.60 overpayment is not refunded",
      f"the refund floor is wrong: {pg2}")
pg2b = MO.mo_pte_page2(0, 0, 150000, 0, 0, 0)
check(pg2b["form_5378_required"] is True,
      "a refund of $100,000 or more requires Form 5378",
      "the Form 5378 threshold did not trigger")

# 6c. MO-MS PTE -- the short path, the back-solve, and the HARD RED.
ms_stop = MO.mo_ms_pte_part1(400000, 1000000, 900000, has_nonapportionable=False)
check(approx(ms_stop["L3"], 40.0) and ms_stop["stop_here"] is True
      and ms_stop["mo_pte_l5_percent_source"] == "MO-MS PTE Line 3",
      "MO-MS PTE 'STOP HERE' path: MO-PTE Line 5 Percent comes from Line 3",
      f"the stop-here path is wrong: {ms_stop}")
ms = MO.mo_ms_pte_part1(400000, 1000000, 900000, 100000, 25000, has_nonapportionable=True)
check(approx(ms["L6"], 320000.0) and approx(ms["L8"], 345000.0) and approx(ms["L9"], 38.333),
      "MO-MS PTE BACK-SOLVE ORACLE: L6 = 320,000; L8 = 345,000; L9 = 38.333%",
      f"the back-solve is wrong: {ms}")
ms_zero = MO.mo_ms_pte_part1(400000, 1000000, 0, 0, 0, has_nonapportionable=True)
check(ms_zero["blocked"] is True and ms_zero["L9"] is None,
      "⚠ HARD RED: MO-MS PTE Line 9 refuses when Line 4 is ZERO (division by zero)",
      f"a zero Line 4 was not blocked: {ms_zero}")
ms_neg = MO.mo_ms_pte_part1(400000, 1000000, -500000, 0, 0, has_nonapportionable=True)
check(ms_neg["blocked"] is True and ms_neg["L9"] is None,
      "⚠ HARD RED: MO-MS PTE Line 9 refuses when Line 4 is NEGATIVE (the sign inverts)",
      f"a negative Line 4 was not blocked: {ms_neg}")
check("PREPARE MANUALLY" in ms_zero["block_reason"].upper(),
      "the MO-MS PTE block explains itself and says to prepare manually",
      "the MO-MS PTE block reason is missing or silent")

# 6d. MO-PTE Line 5 -- the ROUNDED PRODUCT WINS, and MS-5 stays an input.
l5 = MO.mo_pte_line5(900000, apportionment_percent=38.3333333)
check(approx(l5["rounded_percent"], 38.333) and approx(l5["L5"], 344997.0, tol=0.5),
      "MO-PTE LINE 5 ORACLE: the ROUNDED product (344,997) wins over MO-MS PTE Line 8 (345,000)",
      f"the Line 5 rounding is wrong: {l5}")
l5all = MO.mo_pte_line5(900000, all_missouri=True)
check(approx(l5all["L5"], 900000) and l5all["percent"] is None,
      "all-Missouri -> MO-PTE Line 5 equals Line 4 with no percentage",
      f"the all-Missouri branch is wrong: {l5all}")
try:
    MO.mo_pte_line5(900000)
    FAILURES.append("mo_pte_line5 accepted a missing apportionment percentage")
except ValueError:
    PASSES.append("mo_pte_line5 REFUSES a missing apportionment percentage rather than defaulting")
_ms5 = [ln for ln in MO.FORMS[2]["lines"] if ln["line_number"] == "MS-5"][0]
check(_ms5["line_type"] == "input" and "Nonapportionable income" in _ms5["description"],
      "⚠ MO-MS PTE Line 5 stays what the FACE says it is -- `Nonapportionable income - Everywhere`, "
      "a DIRECT-ENTRY input -- not the L4 x round(L9,3) product",
      "MO-MS PTE Line 5 was mis-encoded as the rounded product")
check(FormDiagnostic.objects.filter(tax_form=fpte,
                                    diagnostic_id="D_MO_L5_ROUNDED_PRODUCT_WINS").exists(),
      "the MO-PTE Line 5 / MO-MS PTE Line 5 disambiguation carries its own diagnostic",
      "the Line-5 disambiguation has no diagnostic")

# 6e. U11 -- the engine REFUSES to decide.
try:
    MO.mo_ms_pte_lines_4_9_required(method="4")
    FAILURES.append("mo_ms_pte_lines_4_9_required GUESSED at U11 instead of refusing")
except NotImplementedError as e:
    check("U11" in str(e), "⚠ U11: mo_ms_pte_lines_4_9_required() RAISES rather than guessing",
          "it raised NotImplementedError but without naming U11")
check(FormDiagnostic.objects.filter(tax_form=fpte, diagnostic_id="D_MO_U11_MILEAGE_TRIGGER",
                                    severity="error").exists(),
      "U11 carries an ERROR-severity diagnostic -- no silent gap",
      "the U11 diagnostic is missing or too weak")

# 6f. The $500 FLOOR -- on the EXPENSE, not on the subtraction.
f400 = MO.mo_related_expense_net(10000, 400)
check(approx(f400["net"], 10000) and f400["expense_dropped_by_floor"] is True,
      "$500 FLOOR ORACLE: a $400 expense is DROPPED and the modification stays at 10,000",
      f"the $500 floor is wrong: {f400}")
f500 = MO.mo_related_expense_net(10000, 500)
check(approx(f500["net"], 9500) and f500["expense_dropped_by_floor"] is False,
      "$500 FLOOR BOUNDARY: exactly $500 IS applied ('must EQUAL OR EXCEED $500')",
      f"the $500 boundary is wrong: {f500}")
check(MO.MO_RELATED_EXPENSE_FLOOR == 500, "the floor constant is 500", "the floor constant is wrong")

# 6g. The modification chains, and the OUTSIDE-the-totals lines.
a65 = MO.mo_1065_adjustment(5000, 1000, 0, 0, 2000, 500, 0, 0)
check(approx(a65["L5"], 6000) and approx(a65["L10"], 2500) and approx(a65["L11"], 3500)
      and approx(a65["L12"], 0),
      "MO-1065 ORACLE: L5 = 6,000; L10 = 2,500; L11 = 3,500; L12 = 0 (mutually exclusive)",
      f"the MO-1065 chain is wrong: {a65}")
a20s = MO.mo_1120s_adjustment(0, 0, 0, 0, 1000, 200, 5000, 300, 400, 100)
check(approx(a20s["L12"], 7000),
      "MO-1120S ORACLE: the subtraction total runs Lines 6-11 (MO-1065's runs 6-9) -> 7,000",
      f"the MO-1120S subtraction range is wrong: {a20s['L12']}")
_l13 = [ln for ln in MO.FORMS[0]["lines"] if ln["line_number"] == "13"][0]
_l15 = [ln for ln in MO.FORMS[1]["lines"] if ln["line_number"] == "15"][0]
_a10 = [ln for ln in MO.FORMS[2]["lines"] if ln["line_number"] == "A10"][0]
check(_l13["line_type"] == "informational" and _l15["line_type"] == "informational",
      "Agriculture Disaster Relief is OUTSIDE the totals on MO-1065 L13 and MO-1120S L15",
      "an Agriculture Disaster Relief line was folded into a total")
check("A10" in ([ln["line_number"] for ln in MO.FORMS[2]["lines"]])
      and "A6 + A7 + A8 + A9 + A10 + A11" in
      [ln.get("calculation") for ln in MO.FORMS[2]["lines"] if ln["line_number"] == "A12"][0],
      "MO-PTE Line 10 IS inside the Part A Line 12 subtraction total -- the opposite behaviour",
      "MO-PTE A10 is not inside the A12 total")
check("Agriculture Disaster Relief" in _l13["description"]
      and "Agriculture Disaster Relief" in _l15["description"]
      and "Agricultural Disaster Relief" in _a10["description"],
      "⚠ THE DOR'S TWO SPELLINGS ARE TRANSCRIBED PER FACE: `Agriculture` twice, `Agricultural` once",
      "the two DOR spellings were normalised away -- transcribe each face's own")

# 6h. MO-NRP vs MO-NRS -- INVERSE derivations, and the DOR's worked example.
nrp = MO.mo_nrp_columns(20000, 16000, 12000)
check(approx(nrp["col_c_pct"], 80.0) and approx(nrp["col_e"], 9600.0),
      "MO-NRP ORACLE: the DOR's own 20,000 / 16,000 / 80% / 12,000 / 9,600 example reproduces",
      f"the MO-NRP example failed: {nrp}")
nrs = MO.mo_nrs_columns(20000, 80.0, 12000)
check(approx(nrs["col_b"], 16000.0) and approx(nrs["col_e"], 9600.0),
      "MO-NRS derives (b) FORWARD from (c) -- the REVERSE of MO-NRP's (c) = (b) / (a)",
      f"the MO-NRS derivation failed: {nrs}")
check("(c) = (b) / (a)" in nrp["derivation"] and "(b) = (a) x (c)" in nrs["derivation"],
      "the two INVERSE derivations are recorded explicitly so no rule is shared between them",
      "the inverse derivations are not recorded")

# 6i. MO-MSS -- the printed SIX-STEP per-item example.
mss = MO.mo_mss_per_item_percentage(15000, 3000, 1000, 33.333)
check(approx(mss["apportioned"], 4000.0, tol=0.5) and approx(mss["col_b"], 5000.0, tol=0.5)
      and approx(mss["col_c_pct"], 33.333, tol=0.01),
      "MO-MSS ORACLE: the DOR's printed six-step example gives (b) 5,000 and (c) 33.333%",
      f"the MO-MSS six-step example failed: {mss}")
check("VECTOR" in mss["note"].upper(),
      "MO-NRS Column (c) is recorded as a PER-ITEM VECTOR, not a scalar",
      "the per-item vector warning is missing")

# 6j. The withholding bases -- U9, both directions.
nrs_base = MO.mo_nrs_withholding_base({"1": 200000, "2": 0, "3": 0, "4": 3000, "5a": 10000,
                                       "5b": 8000, "6": 0, "7": 1000, "8a": 40000, "8b": 12000,
                                       "8c": 9000, "9": 0, "10": 0})
check(approx(nrs_base["base"], 254000.0) and approx(nrs_base["literal_sum_would_be"], 283000.0),
      "MO-NRS WITHHOLDING ORACLE: 5b + 8b + 8c are SUPPRESSED, avoiding a 29,000 overstatement",
      f"the MO-NRS base is wrong: {nrs_base}")
check(nrs_base["requires_human_review"] is True,
      "a non-zero 5b / 8b / 8c raises requires_human_review (campaign D-12 Group D)",
      "the subset-line review flag did not fire")
nrp_base = MO.mo_nrp_withholding_base({"1": 100000, "2": 0, "3c": 0, "4a": 20000, "5": 5000,
                                       "10": 0, "11": 0, "12": 30000, "13": 2000, "13e": 1000})
check(approx(nrp_base["base"], 125000.0) and approx(nrp_base["excluded_total"], 33000.0),
      "MO-NRP WITHHOLDING ORACLE: 'Lines 1 through 11' silently EXCLUDES 179, contributions and deductions",
      f"the MO-NRP base is wrong: {nrp_base}")
check(nrp_base["requires_human_review"] is True,
      "a non-zero excluded line raises requires_human_review on the partnership side too",
      "the MO-NRP exclusion flag did not fire")
check(set(MO.MO_NRS_SUBSET_LINES) == {"5b", "8b", "8c"},
      "the MO-NRS subset lines are exactly 5b, 8b and 8c",
      f"the subset set is wrong: {MO.MO_NRS_SUBSET_LINES}")

# 6k. Withholding required / not required, including the election.
w = MO.mo_withholding_required("individual", 200000, pte_election_made=True)
check(w["required"] is True and approx(w["amount"], 9400.0)
      and w["election_relieved_withholding"] is False,
      "⚠⚠ WITHHOLDING ORACLE: an ELECTING entity still withholds 4.7% -- 200,000 -> 9,400",
      f"the electing-entity withholding is wrong: {w}")
wc = MO.mo_withholding_required("corporation", 500000)
check(wc["required"] is False and wc["issue_mo_2nr"] is False,
      "a corporate partner is OUT OF SCOPE and gets no MO-2NR",
      f"the corporate-owner gate is wrong: {wc}")
wg = MO.mo_withholding_required("grantor_trust_1671_4b", 50000)
check(wg["required"] is True,
      "a Reg. 1.671-4(b) grantor trust IS treated as an individual and IS in scope",
      "the grantor-trust carve-in failed")
wd = MO.mo_withholding_required("individual", 1200)
check(wd["required"] is True and wd["exception"] is None,
      "the $1,200 de minimis is STRICTLY LESS THAN -- an owner at exactly $1,200 is IN scope",
      f"the de minimis boundary is wrong: {wd}")
wd2 = MO.mo_withholding_required("individual", 1199.99)
check(wd2["required"] is False and wd2["exception"] == "de_minimis",
      "just under $1,200 falls in the de minimis exception",
      f"the de minimis exception did not apply: {wd2}")
wz = MO.mo_withholding_required("individual", 800, mo_3nr_on_file=True)
check(wz["issue_mo_2nr"] is True and wz["required"] is False,
      "A ZERO-DOLLAR MO-2NR IS STILL REQUIRED even with a Form MO-3NR exemption on file",
      f"the zero-dollar MO-2NR rule failed: {wz}")
wcomp = MO.mo_withholding_required("individual", 90000, on_composite=True)
check(wcomp["required"] is False and wcomp["issue_mo_2nr"] is False,
      "a composite-return owner is BOTH exempt from withholding and suppressed from MO-2NR",
      f"the composite suppression failed: {wcomp}")

# 6l. Tax actually paid -- the derived field, and the two harm cases.
tap = MO.mo_tax_actually_paid(100000, 40000, 60000)
check(approx(tap["L12"], 60000.0) and approx(tap["member_credit_pool"], 60000.0)
      and tap["severity"] == "error",
      "CREDIT-POISONING ORACLE: a 40,000 MO-TC credit cuts the member pool from 100,000 to 60,000",
      f"the credit-poisoning computation is wrong: {tap}")
tap2 = MO.mo_tax_actually_paid(80000, 0, 30000)
check(approx(tap2["member_credit_pool"], 30000.0) and tap2["pool_equals_l12"] is False
      and tap2["severity"] == "warning",
      "an unpaid balance caps the member pool below Line 12 ('to the extent paid')",
      f"the unpaid-balance case is wrong: {tap2}")
check(tap2["refundable_excess_counted"] is False and "UNANSWERED" in tap2["open_item"].upper(),
      "the Line 13 refundable-excess question is SURFACED, not silently decided",
      "the refundable-excess open question is not surfaced")
tap3 = MO.mo_tax_actually_paid(50000, 0, 50000)
check(tap3["harm"] is False and tap3["severity"] is None,
      "a fully-paid, credit-free return raises nothing",
      f"a clean return raised a diagnostic: {tap3}")

# 6m. Name Control -- the DOR's six printed examples.
nc_bad = [(ln, want, MO.mo_name_control(ln)) for ln, want in MO.MO_NAME_CONTROL_EXAMPLES
          if MO.mo_name_control(ln) != want]
check(not nc_bad,
      "NAME CONTROL ORACLE: all six DOR examples reproduce (BROW / DEJE / LEE / TORR / MCCA / ONEI)",
      f"name control mismatches: {nc_bad}")
check(MO.mo_name_control("Lee") == "LEE",
      "short names are NOT padded -- LEE is three characters, exactly as the DOR prints it",
      "a short name was padded")

# 6n. Extensions -- the INVERTED MO-PTE payment rule, and only for MO-PTE.
ep = MO.mo_extension(FPTE)
check(ep["extension_extends_payment"] is True and ep["missouri_form"] == "MO-7004"
      and ep["max_months"] == 6,
      "⭐⭐ MO-PTE EXTENSION: it extends the time to PAY, uses Form MO-7004, capped at six months",
      f"the MO-PTE extension branch is wrong: {ep}")
check("ORIGINAL" in ep["interest_runs_from"].upper(),
      "interest still runs from the ORIGINAL due date under 143.731.2",
      "the interest-from-original rule is missing")
for fc in (F65, F20S):
    e = MO.mo_extension(fc)
    check(e["extension_extends_payment"] is False and e["missouri_form"] is None,
          f"{fc}: NO Missouri extension form and NO payment extension -- do not share the PTE branch",
          f"{fc} inherited the MO-PTE payment-extension branch")
check("180" in ep["conflict"] and "six months" in ep["conflict"],
      "the U24 180-days-vs-six-months contradiction is recorded on the extension result",
      "the U24 extension contradiction is not recorded")

# 6o. Depreciation window.
check(MO.mo_depreciation_modification_applies("2002-12-15") is True,
      "2002-03 vintage property IS inside the JCWAA window",
      "the in-window case failed")
check(MO.mo_depreciation_modification_applies("2025-06-01") is False
      and MO.mo_depreciation_modification_applies("2003-07-01") is False,
      "post-30-June-2003 property produces NO Missouri depreciation modification",
      "a post-window date produced a modification")

# 6p. Form 5889 mapping BY SUBSTANCE.
m5889 = MO.mo_5889_map()
check("COLUMN 5" in m5889["form_5889_map_by_substance"]["Line 1 (Membership Percentage)"]
      and "COLUMN 6" in m5889["form_5889_map_by_substance"]["Line 2 (Member's PTE Tax Credit)"],
      "Form 5889 maps BY SUBSTANCE: Line 1 <- Part B Column 5, Line 2 <- Part B Column 6",
      f"the 5889 substance map is wrong: {m5889['form_5889_map_by_substance']}")
check(m5889["reproduce_stale_numbers_in_help"] is False,
      "the stale Form 5889 column numbers are NEVER reproduced in help text",
      "the stale column numbers would be reproduced")
check(m5889["defect_vintage"] == "TY2024",
      "⚠ the Form 5889 defect is dated TY2024 -- A YEAR OLDER than first reported",
      f"the 5889 defect vintage is wrong: {m5889['defect_vintage']}")
check("PERSISTED" in m5889["defect_note"].upper(),
      "the 5889 defect is recorded as PERSISTED through a full revision cycle, not a publication lag",
      "the persisted-defect finding is not recorded")

# ==========================================================================
# 7. VERIFIED NEGATIVES -- pinned so nobody adds a field "for symmetry"
# ==========================================================================
check(MO.MO_SECTION_179_STATE_LIMIT is None and MO.MO_SECTION_179_STATE_PHASEOUT is None,
      "N1 PINNED: there is NO Missouri IRC 179 limit or phaseout constant",
      "a Missouri IRC 179 constant has appeared -- Missouri has none")
try:
    MO.mo_section_179_state_limit()
    FAILURES.append("mo_section_179_state_limit() RETURNED a figure -- Missouri has none")
except ValueError as e:
    check("VIRGINIA" in str(e).upper(),
          "mo_section_179_state_limit() RAISES and names Virginia's pattern as the one not to port",
          "it raised but without the do-not-port-Virginia warning")
check(MO.MO_HAS_BONUS_ADDBACK is False and MO.MO_HAS_SHADOW_DEPRECIATION_BOOK is False,
      "N1 PINNED: no bonus add-back and NO Missouri shadow depreciation book",
      "a Missouri bonus add-back or shadow book has appeared")
check(MO.MO_JCWAA_WINDOW == ("2002-07-01", "2003-06-30"),
      "the JCWAA window is pinned to 1 July 2002 - 30 June 2003",
      f"the JCWAA window is wrong: {MO.MO_JCWAA_WINDOW}")
check("143.121.2(3)" in MO.MO_JCWAA_ADDBACK_CITE,
      "the negative is anchored on 143.121.2(3) -- THE ADD-BACK PROVISION ITSELF",
      "the add-back citation is missing")
check(MO.MO_DEPRECIATION_LINES["MO_PTE"] == [],
      "N5 PINNED: Form MO-PTE has NO depreciation line of any kind",
      "a depreciation line appeared on MO_PTE")
check(MO.MO_DEPRECIATION_LINES["MO_1065"] == ["9"]
      and MO.MO_DEPRECIATION_LINES["MO_1120S"] == ["10", "11"],
      "N9 PINNED: MO-1065 has ONLY the .3(7) basis line; MO-1120S has both",
      "the depreciation line inventory is wrong")
check(len(MO.MO_SECTION_179_APPEARANCES) == 3
      and all("distributive share item" in v for v in MO.MO_SECTION_179_APPEARANCES.values()),
      "IRC 179 appears in the lane exactly THREE times, ALWAYS as a distributive-share item",
      "the IRC 179 appearance inventory is wrong")
check(MO.MO_CONFORMITY_TYPE == "rolling" and MO.MO_CONFORMITY_HAS_ADJUSTMENT_BUCKET is False,
      "N3 PINNED: rolling conformity, and NO conformity-adjustment bucket",
      "the Missouri conformity posture is wrong")
_food = [f for f in MO.FORMS[2]["facts"] if "food_pantry" in f["fact_key"]]
check(not _food, "N6 PINNED: MO_PTE has NO Food Pantry add-back",
      "a Food Pantry line appeared on MO_PTE")
_163j_65 = [f for f in MO.FORMS[0]["facts"] if "163j" in f["fact_key"]]
check(not _163j_65, "N7 PINNED: MO_1065 has NO 163(j) fact in either direction",
      "a 163(j) fact appeared on MO_1065")
_mohela_65 = [f for f in MO.FORMS[0]["facts"] if "mohela" in f["fact_key"]]
check(not _mohela_65, "N8 PINNED: MO_1065 has NO MOHELA line",
      "a MOHELA fact appeared on MO_1065")
check(MO.MO_CITY_EARNINGS_TAXES_IN_SCOPE is False and MO.MO_CITY_EARNINGS_TAX_LINE == "1b",
      "KC / St. Louis earnings taxes are OUT OF SCOPE but the state module knows they live at Line 1b",
      "the city-earnings-tax posture is wrong")
_l1b = {"MO_1065": None, "MO_1120S": None, "MO_PTE": None}
for spec in MO.FORMS:
    for ln in spec["lines"]:
        if ln["line_number"] in ("1b", "A1b"):
            _l1b[spec["identity"]["form_number"]] = ln["description"]
check(all(v for v in _l1b.values()) and len({v for v in _l1b.values()}) == 3,
      "the KC / St. Louis carve-out is on ALL THREE faces and each face's OWN wording is transcribed",
      f"the Line 1b transcriptions are missing or were normalised: {_l1b}")

# 7b. Every RED-DEFER has a diagnostic somewhere -- NO SILENT GAP.
RED_DEFER_DIAGNOSTICS = [
    "D_MO_PTE_NOT_EFILEABLE",          # R1
    "D_MO_COMPOSITE_DEFERRED",         # R2
    "D_MO_R3_MO_CR_RECIPROCAL",        # R3
    "D_MO_METHOD_DEFERRED",            # R4
    "D_MO_R5_DEPR_2002_03_MANUAL",     # R5
    "D_MO_BTC_BANK_CREDIT",            # R6
    "D_MO_PTE_AMENDED_CASCADE",        # R7
    "D_MO_OPTOUT_MEMBER_FORMS",        # R8
    "D_MO_R9_CERT_GATED_CREDITS",      # R9
    "D_MO_ABE_REP_MISSING",            # R10
    "D_MO_R11_FORM_4458_NEXUS",        # R11
    "D_MO_FORM_5378_REFUND",           # R12
    "D_MO_501C_ROSTER",                # R13
    "D_MO65_SPECIAL_ALLOCATION",       # R14
    "D_MO_R15_CITY_EARNINGS_TAX",      # R15
]
missing_rd = [d for d in RED_DEFER_DIAGNOSTICS
              if not FormDiagnostic.objects.filter(tax_form__jurisdiction="MO",
                                                   diagnostic_id=d).exists()]
check(not missing_rd,
      f"all {len(RED_DEFER_DIAGNOSTICS)} RED-DEFERS (R1-R15) carry their own diagnostic -- NO SILENT GAP",
      f"RED-DEFERS with no diagnostic: {missing_rd}")

# 7c. The shared diagnostics really are on all three specs.
for did in ("D_MO_DEPR_ABSENCE_IS_A_RULING", "D_MO_CONFORMITY_ROLLING",
            "D_MO_FEDERAL_LINES_UNVERIFIED", "D_MO_OPEN_ITEMS_OUTSTANDING",
            "D_MO_R15_CITY_EARNINGS_TAX", "D_MO_OWNER_EXTRACT_PACKAGE"):
    n = FormDiagnostic.objects.filter(tax_form__jurisdiction="MO", diagnostic_id=did).count()
    check(n == 3, f"shared diagnostic {did} is attached to all THREE Missouri specs",
          f"shared diagnostic {did} is on {n} spec(s), expected 3")

# 7d. U8 is surfaced everywhere a federal line reference is made.
u8 = FormDiagnostic.objects.filter(tax_form=fpte,
                                   diagnostic_id="D_MO_FEDERAL_LINES_UNVERIFIED").first()
check(u8 is not None and "had not finalized" in u8.message,
      "U8 carries the DOR's own disclaimer verbatim -- printed on a FINAL form",
      "the U8 diagnostic is missing or lacks the DOR disclaimer")
stamped = [f for spec in MO.FORMS for f in spec["facts"]
           if "[UNVERIFIED - U8]" in (f.get("notes") or "")]
check(len(stamped) >= 6,
      f"the U8 stamp rides on {len(stamped)} federal-line facts across the three specs",
      "the U8 stamp is missing from the federal-line facts")

# 7e. The DOR defect ledger and the open-item counters.
check(len(MO.MO_DOR_DEFECTS) == 22,
      "22 DOR citation/label defects carried: the brief's 21, plus #22 found by THIS harness",
      f"the DOR defect ledger holds {len(MO.MO_DOR_DEFECTS)} entries, expected 22")
_optrnd = [d for d in MO.MO_DOR_DEFECTS if d["id"] == 22][0]
check("NOT IN THE SOURCE BRIEF" in _optrnd["spec_impact"],
      "defect #22 is flagged as a NEW finding surfaced by the validation harness",
      "defect #22 does not record that it is new")
_faq = [d for d in MO.MO_DOR_DEFECTS if d["id"] == 19][0]
check("4.8%" in _faq["printed"] and "4.7%" in _faq["actual"],
      "defect #19 records that the DOR FAQ's rate table is STALE and must never source the rate",
      "the stale-FAQ-rate defect is not recorded")
check(MO.MO_OPEN_ITEMS_GENUINELY_OPEN == 22 and MO.MO_WALK_ITEMS_LIVE == 15,
      "the open-item counters match the verification pass: 22 open [UNVERIFIED], 15 live walk items",
      f"the counters are wrong: {MO.MO_OPEN_ITEMS_GENUINELY_OPEN} / {MO.MO_WALK_ITEMS_LIVE}")
check(set(MO.MO_OPEN_ITEMS_CLOSED) == {"U1", "U2", "U5", "U6"}
      and MO.MO_OPEN_ITEMS_NARROWED == ("U4",),
      "the closed (U1/U2/U5/U6) and narrowed (U4) items are recorded as the verification pass left them",
      "the closed/narrowed item sets are wrong")

# 7f. Rounding: three conventions, and the tie-break is NOT a DOR rule.
check(MO.MO_ROUND_PAGE3_SHARE_DECIMALS == 0 and MO.MO_ROUND_PARTB_SHARE_DECIMALS == 2
      and MO.MO_ROUND_APPORTIONMENT_DECIMALS == 3,
      "THREE rounding conventions pinned: whole numbers / two decimals / three decimals",
      "a rounding convention is wrong")
check(MO.MO_ROUNDING_TIEBREAK_IS_DOR_RULE is False,
      "⚠ the round-half-up tie-break is recorded as an ENGINEERING DECISION, not a DOR rule",
      "the tie-break is mislabelled as a Departmental rule")
check(MO._round_half_up(2.5, 0) == 3.0 and MO._round_half_up(0.125, 2) == 0.13,
      "the explicit half-up rounder does NOT use Python's banker's rounding",
      "the rounder fell back to round-half-to-even")
check(FormDiagnostic.objects.filter(tax_form=fpte, diagnostic_id="D_MO_ROUNDING_TIEBREAK").exists(),
      "the unpublished tie-break carries its own diagnostic",
      "the rounding tie-break has no diagnostic")

# 7g. 105.1500 -- never auto-populate, never auto-suppress.
r501 = MO.mo_501c_roster_decision(True)
check(r501["auto_populate"] is False and r501["auto_suppress"] is False
      and r501["decision_required"] is True,
      "105.1500: a 501(c) member's identity is NEITHER auto-populated NOR auto-suppressed",
      f"the 501(c) roster handling is wrong: {r501}")
check(MO.mo_501c_roster_decision(False)["decision_required"] is False,
      "a non-501(c) member needs no roster decision",
      "a roster decision was demanded for an ordinary member")

# 7h. The representative gate.
ev = MO.mo_election_valid(True, False, True)
check(ev["valid"] is False and "INEFFECTIVE" in (ev["blocking_failure"] or "").upper(),
      "the election is INEFFECTIVE without a designated Affected Business Entity Representative",
      f"the representative gate did not block: {ev}")
check(MO.mo_election_valid(True, True, True)["valid"] is True,
      "a complete election with a representative and a timely filing is valid",
      "a complete election was rejected")
check(len(MO.MO_ABE_REP_FORMS) == 2 and "Form 2827 PTE" in MO.MO_ABE_REP_FORMS,
      "BOTH Form 2827 and Form 2827 PTE are supported (the regulation names both; the instructions do not)",
      "Form 2827 PTE is missing from the representative forms")

# 7i. Trust-fund grid and the non-contiguous code list.
check(len(MO.MO_TRUST_FUND_BOXES) == 14 and MO.MO_TRUST_FUND_WRITEIN_MAX == 2,
      "the Line 22 trust-fund grid has 14 boxes and a HARD CAP of two write-ins",
      "the trust-fund grid is wrong")
check("04" not in MO.MO_ADDITIONAL_FUND_CODES and "06" not in MO.MO_ADDITIONAL_FUND_CODES
      and "11" not in MO.MO_ADDITIONAL_FUND_CODES,
      "the additional fund codes are NON-CONTIGUOUS -- 04, 06, 11, 12 and 13 are unpublished",
      "an unpublished fund code was invented")
check(MO.MO_ADDITIONAL_FUND_UNCAPPED == ("14",) and MO.MO_ADDITIONAL_FUND_CAP == 200,
      "code 14 is uncapped; the others are capped at $200",
      "the fund cap handling is wrong")

# ==========================================================================
# Report
# ==========================================================================
print("\n" + "=" * 78)
print(f"MO_1065 / MO_1120S / MO_PTE validation -- {len(PASSES)} PASS / {len(FAILURES)} FAIL "
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
print(f"Shared: flow assertions {FlowAssertion.objects.filter(assertion_id__startswith='FA-MO').count()} / "
      f"sources {AuthoritySource.objects.filter(source_code__startswith='MO_').count()} / "
      f"topics {AuthorityTopic.objects.filter(topic_code__startswith='mo_').count()} / "
      f"form links {AuthorityFormLink.objects.filter(form_code__startswith='MO_').count()}")
print(f"DOR defects logged: {len(MO.MO_DOR_DEFECTS)} / apportionment methods "
      f"{len(MO.MO_APPORTIONMENT_METHODS)} / open [UNVERIFIED] {MO.MO_OPEN_ITEMS_GENUINELY_OPEN} / "
      f"live walk items {MO.MO_WALK_ITEMS_LIVE}")
print(f"READY_TO_SEED on disk: {MO.READY_TO_SEED} (MUST remain False -- Gate 1 is open for Missouri)")
sys.exit(1 if FAILURES else 0)
