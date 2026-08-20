"""Throwaway-SQLite validation for the Arizona PTE specs (WO-W04-PTE, Wave 4).

AZ_165 (Arizona Form 165, partnership) + AZ_120S (Arizona Form 120S, S corporation).

⚠ TWO specs, not three. Arizona's elective PTE tax rides on the two existing
returns (Form 165 Part 2 lines 8-40; Form 120S Part 2 lines 37-52) — the only
state in Wave 4 that needs no third form.

Checks, in order:
  1. THE SEED GUARD -- asserted to REFUSE, and asserted to leave the DB CLEAN.
     Pins the MECHANISM, not the disk value, then flips IN MEMORY ONLY.
  2. THE SUBSTANTIVE TRIPWIRES -- each campaign ruling is flipped IN MEMORY and
     the guard is asserted to fire. Re-pinned to the mechanism per the D-10 and
     D-11 process notes: a test pinned to a pre-approval VALUE has an expiry
     date; a test pinned to "does the guard still withhold?" does not.
  3. CharField caps -- introspected from the REAL model fields via _meta, never
     hardcoded. SQLite does NOT enforce max_length; Postgres does. Wave 3's
     harnesses caught four topic_name values over the 255 cap that were INVISIBLE
     IN SQLITE, and ARIZONA HAS FORM HERE: one of its citations ran 390
     characters and blew the cap during the Tier-1 conformity seed.
  4. CHOICE-FIELD VALIDITY -- Django does NOT validate `choices` on save(), so an
     invalid enum rides straight through SQLite AND Postgres and only surfaces
     downstream as a broken export.
  5. Structural integrity -- two forms, every rule authority-linked, no duplicate
     ids, rule_links referencing defined rules, identity fields, the D-9
     namespace.
  6. THE VERIFIED NEGATIVES -- pinned so a later contributor cannot quietly add a
     Form 120S modification field "for symmetry with AZ_165".
  7. Arithmetic oracles -- the five depreciation vintage tiers, the $150,000
     boundary in BOTH directions, the dynamic apportionment divisor, the
     conditional $50 minimum, the compound conformity date, the PTE installment
     calendar, and the inverted multistate booleans.
  8. RED-DEFERS and the open [UNVERIFIED] register -- every one carries a
     diagnostic. NO SILENT GAP, AND NOTHING SILENTLY INCLUDED EITHER.

ASCII-only output. Run: poetry run python scratchpad/validate_az.py
"""
import os
import sys

PROJECT_ROOT = r"D:\dev\delvio-rule-studio"
sys.path.insert(0, PROJECT_ROOT)

SQLITE_PATH = os.path.join(PROJECT_ROOT, "scratchpad", "validate_az.sqlite3")
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
from specs.management.commands import load_az_pte as AZ  # noqa: E402

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
# there, so the Arizona anchors in EXISTING_SOURCES_TO_REFERENCE resolve. Seed it
# here too, so the harness tests the same wiring the prod seed will see.
try:
    call_command("load_state_conformity", verbosity=0)
    PASSES.append("Tier-1 conformity batch seeded into the throwaway DB (mirrors prod, campaign D-10)")
except Exception as exc:  # noqa: BLE001
    FAILURES.append(f"could not seed the Tier-1 conformity batch: {exc!r}")

F165, F120S = AZ.FORM_CODE_165, AZ.FORM_CODE_120S

# ==========================================================================
# 1. THE SEED GUARD
# ==========================================================================
_shipped = AZ.READY_TO_SEED
check(_shipped is False,
      "READY_TO_SEED ships FALSE on disk -- Gate 1 has NOT been taken for Arizona",
      f"READY_TO_SEED SHIPPED {_shipped!r} -- it MUST ship False; Gate 1 is open and 21 "
      "[UNVERIFIED] items stand, three of them blocking")

try:
    call_command("load_az_pte", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: the loader seeded with READY_TO_SEED = False")
except CommandError as e:
    msg = str(e)
    check("REFUSING TO SEED" in msg, "guard REFUSES to seed while READY_TO_SEED is False",
          "guard raised CommandError but without the refusal banner")
    check("Gate 1 has NOT been taken" in msg,
          "guard states plainly that Gate 1 is open for Arizona",
          "guard message does not say Gate 1 is open")
    check("U19" in msg and "150,000" in msg,
          "guard names U19 (WHICH taxable income measures the $150,000 threshold) as blocking",
          "guard message omits the U19 blocker")
    check("U14" in msg and "165PA" in msg and "4.5" in msg,
          "guard names U14 (Form 165PA's 4.5% vs the statute's 2.5%) as blocking",
          "guard message omits the U14 blocker")
    check("U3" in msg and "OBBBA" in msg,
          "guard names U3 (AZDOR's unpublished OBBBA retroactivity mapping) as blocking",
          "guard message omits the U3 blocker")
    check("ITP 16-2" in msg and "U1" in msg,
          "guard names ITP 16-2 / U1 as the only unpulled document gating a mainstream line",
          "guard message omits the ITP 16-2 gate")
    check("READY_TO_SEED = False" in msg, "guard reports the sentinel value it saw",
          "guard message omits the sentinel value")
    check("DO NOT RELAX THIS GUARD" in msg,
          "guard tells the next reader not to relax it",
          "guard omits the do-not-relax warning")
    check("SECTION 16" in msg.upper(),
          "guard points at the source brief's section 16, which GOVERNS over the body",
          "guard does not point at the governing verification section")
    check("Idempotent via update_or_create" in msg,
          "guard records that the loader is idempotent",
          "guard omits the idempotency note")
except Exception as e:  # noqa: BLE001
    FAILURES.append(f"guard raised the WRONG exception type: {e!r}")

check(TaxForm.objects.filter(jurisdiction="AZ").count() == 0,
      "guard left the DB CLEAN -- no Arizona TaxForm rows were written while gated",
      "guard refused but Arizona rows were still written")
check(FormRule.objects.filter(rule_id__startswith="R-AZ").count() == 0,
      "guard left the DB CLEAN -- no Arizona FormRule rows were written while gated",
      "guard refused but Arizona rules were still written")
check(FlowAssertion.objects.filter(assertion_id__startswith="FA-AZ").count() == 0,
      "guard left the DB CLEAN -- no Arizona FlowAssertion rows were written while gated",
      "guard refused but Arizona flow assertions were still written")

# ==========================================================================
# 2. THE SUBSTANTIVE TRIPWIRES -- flip each ruling IN MEMORY, assert refusal
#    ⚠ Pinned to the MECHANISM (does the guard still withhold?), never to a
#    pre-approval VALUE. Same lesson as D-10 and D-11's process notes.
# ==========================================================================
AZ.READY_TO_SEED = True


def tripwire(attr, bad_value, label, needle):
    original = getattr(AZ, attr)
    setattr(AZ, attr, bad_value)
    try:
        call_command("load_az_pte", verbosity=0)
        FAILURES.append(f"TRIPWIRE DID NOT FIRE: {label} ({attr} = {bad_value!r} was accepted)")
    except CommandError as exc:
        m = str(exc)
        check(needle.lower() in m.lower(),
              f"tripwire FIRES and names the ruling: {label}",
              f"tripwire fired for {label} but did not explain it (looked for {needle!r})")
    except Exception as exc:  # noqa: BLE001
        FAILURES.append(f"tripwire {label} raised the wrong exception: {exc!r}")
    finally:
        setattr(AZ, attr, original)


tripwire("AZ_120S_HAS_MODIFICATION_APPARATUS", True,
         "Form 120S has NO modification apparatus (D-12 Group B)", "VERIFIED NEGATIVE")
tripwire("AZ_120S_HAS_DEPRECIATION_LOGIC", True,
         "the depreciation shadow book is Form 165 ONLY (D-12)", "VERIFIED NEGATIVE")
tripwire("AZ_EST_BOUNDARY", "or more",
         "the $150,000 boundary is EXCEEDS (settled, seven sources)", "EXCEEDS")
tripwire("AZ_EST_BOUNDARY_EXACTLY_AT_THRESHOLD_IS_IN", True,
         "exactly $150,000 is OUT", "exactly $150,000 is OUT")
tripwire("AZ_EST_MEASUREMENT_BASIS", "pte_income_but_undeclared",
         "the ruled measurement basis must stay adjudicable (D-12 A1)", "four recorded candidates")
tripwire("AZ_165PA_STATUS", "COMPUTES",
         "Form 165PA is RED-DEFERRED (D-12 A2)", "over-taxes by 80%")
tripwire("AZ_1021_15_ENTITY_ADDBACK_BUILT", True,
         "the 43-1021(15) add-back is OWNER LEVEL ONLY (D-12 A3)", "OWNER LEVEL ONLY")
tripwire("AZ_CORPORATE_BASIS_RECOMPUTATION", "computed",
         "no corporate-basis recomputation (D-12 A4)", "compute NOTHING")
tripwire("AZ_179_IS_RULING_NOT_PUBLICATION", False,
         "the 179 figure is a RULING, not a published Arizona number (D-10)", "U3 stays OPEN")
tripwire("AZ_165_B1_TIER_COUNT", 4,
         "Form 165 line B1 has FIVE vintage tiers, not four", "FIVE placed-in-service")
tripwire("AZ_165_B1_KEYED_ON", "acquired",
         "line B1 is keyed on PLACED IN SERVICE, stated four times", "placed-in-service")
tripwire("AZ_SBI_LINE_COUNT", 17,
         "SBI reaches EIGHTEEN K-1 routing lines, not seventeen", "Eighteen K-1 lines")
tripwire("AZ_SBI_REACHES_ENTITY_COMPUTATION", True,
         "SBI does NOT reach either entity computation", "does NOT reach either entity")
tripwire("AZ_UNVERIFIED_COUNT", 18,
         "the [UNVERIFIED] register holds 21 items (three were ADDED, none closed)",
         "closed NONE outright")

# A hollow spec must also refuse, even with the sentinel flipped.
_saved_lines = AZ.FORMS[1]["lines"]
AZ.FORMS[1]["lines"] = []
try:
    call_command("load_az_pte", verbosity=0)
    FAILURES.append("HOLLOW-SPEC GUARD DID NOT FIRE: an empty AZ_120S line list was accepted")
except CommandError as e:
    check("AZ_120S.lines" in str(e),
          "hollow-spec guard REFUSES an empty line list and names it",
          "hollow-spec guard fired but did not name the empty collection")
except Exception as e:  # noqa: BLE001
    FAILURES.append(f"hollow-spec guard raised the wrong exception: {e!r}")
finally:
    AZ.FORMS[1]["lines"] = _saved_lines

check(TaxForm.objects.filter(jurisdiction="AZ").count() == 0,
      "the DB is STILL CLEAN after every tripwire test -- nothing leaked through a refusal",
      "a tripwire refusal still wrote Arizona rows")

# Now seed for real, IN MEMORY ONLY. The file on disk stays False.
try:
    call_command("load_az_pte", verbosity=0)
    PASSES.append("loader ran + seeded into throwaway SQLite without error (in-memory flip only)")
except Exception as e:  # noqa: BLE001
    FAILURES.append(f"load_az_pte raised: {e!r}")
    print("\n".join(FAILURES))
    sys.exit(1)
finally:
    AZ.READY_TO_SEED = _shipped   # never leave the module mutated

f165 = TaxForm.objects.get(form_number=F165, jurisdiction="AZ")
f120s = TaxForm.objects.get(form_number=F120S, jurisdiction="AZ")
ALL_FORMS = [f165, f120s]

# Idempotency: a second run must not duplicate anything.
_before = (FormFact.objects.filter(tax_form__jurisdiction="AZ").count(),
           FormRule.objects.filter(tax_form__jurisdiction="AZ").count(),
           FormLine.objects.filter(tax_form__jurisdiction="AZ").count(),
           FormDiagnostic.objects.filter(tax_form__jurisdiction="AZ").count(),
           TestScenario.objects.filter(tax_form__jurisdiction="AZ").count())
AZ.READY_TO_SEED = True
try:
    call_command("load_az_pte", verbosity=0)
finally:
    AZ.READY_TO_SEED = _shipped
_after = (FormFact.objects.filter(tax_form__jurisdiction="AZ").count(),
          FormRule.objects.filter(tax_form__jurisdiction="AZ").count(),
          FormLine.objects.filter(tax_form__jurisdiction="AZ").count(),
          FormDiagnostic.objects.filter(tax_form__jurisdiction="AZ").count(),
          TestScenario.objects.filter(tax_form__jurisdiction="AZ").count())
check(_before == _after,
      "loader is IDEMPOTENT -- a second run created no duplicate rows (update_or_create)",
      f"loader is NOT idempotent: {_before} -> {_after}")

# ==========================================================================
# 3. CharField caps -- introspected from the REAL model fields
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
    "AuthoritySource.entity_type_code": AuthoritySource._meta.get_field("entity_type_code").max_length,
    "AuthoritySource.jurisdiction_code": AuthoritySource._meta.get_field("jurisdiction_code").max_length,
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

for fa in FlowAssertion.objects.filter(assertion_id__startswith="FA-AZ"):
    measure(f"assertion_id={fa.assertion_id}", fa.assertion_id, "FlowAssertion.assertion_id")
    measure(f"fa.title[{fa.assertion_id}]", fa.title, "FlowAssertion.title")
    measure(f"fa.bug_ref[{fa.assertion_id}]", fa.bug_reference, "FlowAssertion.bug_reference")
for s in AuthoritySource.objects.filter(source_code__startswith="AZ_"):
    measure(f"source_code={s.source_code}", s.source_code, "AuthoritySource.source_code")
    measure(f"citation[{s.source_code}]", s.citation, "AuthoritySource.citation")
    measure(f"issuer[{s.source_code}]", s.issuer, "AuthoritySource.issuer")
    measure(f"entity_type[{s.source_code}]", s.entity_type_code, "AuthoritySource.entity_type_code")
    measure(f"jurisdiction[{s.source_code}]", s.jurisdiction_code, "AuthoritySource.jurisdiction_code")
    for exc in AuthorityExcerpt.objects.filter(authority_source=s):
        measure(f"excerpt_label[{s.source_code}]", exc.excerpt_label, "AuthorityExcerpt.excerpt_label")
        measure(f"location_ref[{s.source_code}]", exc.location_reference, "AuthorityExcerpt.location_reference")
for tp in AuthorityTopic.objects.filter(topic_code__startswith="az_"):
    measure(f"topic_code={tp.topic_code}", tp.topic_code, "AuthorityTopic.topic_code")
    measure(f"topic_name={tp.topic_code}", tp.topic_name, "AuthorityTopic.topic_name")
for afl in AuthorityFormLink.objects.filter(form_code__startswith="AZ_"):
    measure(f"form_code={afl.form_code}", afl.form_code, "AuthorityFormLink.form_code")

check(not viol, "CharField caps OK -- every seeded value fits its REAL model field "
                "(Arizona blew a 255-char cap once already, in the Tier-1 conformity seed)",
      "CAP VIOLATIONS (Postgres would truncate/reject; SQLite silently accepts):\n    "
      + "\n    ".join(viol))

# ==========================================================================
# 4. CHOICE-FIELD VALIDITY
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

_az_sources = list(AuthoritySource.objects.filter(source_code__startswith="AZ_"))
check_choice(AuthoritySource, "source_type", _az_sources, "source_code")
check_choice(AuthoritySource, "source_rank", _az_sources, "source_code")
check_choice(AuthoritySource, "current_status", _az_sources, "source_code")
check_choice(AuthorityFormLink, "link_type",
             list(AuthorityFormLink.objects.filter(form_code__startswith="AZ_")), "form_code")
check_choice(RuleAuthorityLink, "support_level",
             list(RuleAuthorityLink.objects.filter(form_rule__tax_form__jurisdiction="AZ")), "support_level")
_az_fa = list(FlowAssertion.objects.filter(assertion_id__startswith="FA-AZ"))
check_choice(FlowAssertion, "assertion_type", _az_fa, "assertion_id")
check_choice(FlowAssertion, "status", _az_fa, "assertion_id")

check(not bad_choice,
      "CHOICE-FIELD VALIDITY OK -- every seeded enum value is a declared model choice",
      "INVALID CHOICE VALUES (Django does NOT validate choices on save):\n    "
      + "\n    ".join(bad_choice))

# ==========================================================================
# 5. Structural integrity
# ==========================================================================
check(len(AZ.FORMS) == 2 and TaxForm.objects.filter(jurisdiction="AZ").count() == 2,
      "TWO Arizona specs seeded -- AZ_165 and AZ_120S. Arizona's PTE tax needs NO third form "
      "(A.R.S. 43-1014(A), question A on both faces, Pub 713 narrative, Pub 713 FAQ)",
      f"expected 2 Arizona forms, got {TaxForm.objects.filter(jurisdiction='AZ').count()}")
check(f165.entity_types == ["1065"], "AZ_165 entity_types == ['1065']",
      f"AZ_165 entity_types wrong: {f165.entity_types}")
check(f120s.entity_types == ["1120S"], "AZ_120S entity_types == ['1120S']",
      f"AZ_120S entity_types wrong: {f120s.entity_types}")
check(not TaxForm.objects.filter(jurisdiction="AZ", form_number__icontains="PTET").exists(),
      "no AZ_PTET spec exists -- Arizona is the only Wave 4 state whose PTE tax rides on the "
      "existing returns (MO, OR and MA each need a separate form)",
      "an AZ_PTET spec was invented; Arizona needs no third form")
for form in ALL_FORMS:
    check(form.jurisdiction == "AZ" and form.tax_year == 2025 and form.version == 1
          and form.status == "draft",
          f"{form.form_number}: jurisdiction AZ / TY2025 / v1 / draft",
          f"{form.form_number} identity wrong: {form.jurisdiction} {form.tax_year} v{form.version} {form.status}")
check({f.form_number for f in ALL_FORMS} == {"AZ_165", "AZ_120S"},
      "form codes follow the campaign D-9 <ST>_<FORM> namespace",
      f"form codes wrong: {[f.form_number for f in ALL_FORMS]}")

ruleless = [r.rule_id for r in FormRule.objects.filter(tax_form__jurisdiction="AZ")
            if not RuleAuthorityLink.objects.filter(form_rule=r).exists()]
check(not ruleless,
      f"all {FormRule.objects.filter(tax_form__jurisdiction='AZ').count()} Arizona rules carry "
      ">= 1 authority link",
      f"rules with NO authority link: {ruleless}")

for spec in AZ.FORMS:
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
    src_rules = {sr for ln in spec["lines"] for sr in ln.get("source_rules", [])}
    check(not (src_rules - defined), f"{fn}: every line's source_rules names a defined rule",
          f"{fn}: lines reference undefined rules: {src_rules - defined}")
    fact_keys = {f["fact_key"] for f in spec["facts"]}
    src_facts = {sf for ln in spec["lines"] for sf in ln.get("source_facts", [])}
    check(not (src_facts - fact_keys), f"{fn}: every line's source_facts names a defined fact",
          f"{fn}: lines reference undefined facts: {src_facts - fact_keys}")
    rule_inputs = {i for r in spec["rules"] for i in r.get("inputs", [])}
    check(not (rule_inputs - fact_keys), f"{fn}: every rule input names a defined fact",
          f"{fn}: rules reference undefined facts: {rule_inputs - fact_keys}")

fa_ids = [a["assertion_id"] for a in AZ.FLOW_ASSERTIONS]
check(len(set(fa_ids)) == len(fa_ids), f"no duplicate assertion_id ({len(fa_ids)} flow assertions)",
      f"DUPLICATE assertion_id: {[i for i in fa_ids if fa_ids.count(i) > 1]}")
check(FlowAssertion.objects.filter(assertion_id__startswith="FA-AZ").count() == len(fa_ids),
      f"all {len(fa_ids)} Arizona flow assertions seeded",
      "flow assertion count mismatch")

link_targets = {c for c, _f, _t in AZ.AUTHORITY_FORM_LINKS}
declared = {s["source_code"] for s in AZ.AUTHORITY_SOURCES} | set(AZ.EXISTING_SOURCES_TO_REFERENCE)
check(not (link_targets - declared),
      "every AUTHORITY_FORM_LINK names a source this loader declares or reuses",
      f"AUTHORITY_FORM_LINKS reference unknown sources: {link_targets - declared}")
rl_targets = {rl[1] for spec in AZ.FORMS for rl in spec["rule_links"]}
check(not (rl_targets - declared),
      "every rule_link names a source this loader declares or reuses",
      f"rule_links reference unknown sources: {rl_targets - declared}")

# EXISTING_SOURCES_TO_REFERENCE must be REAL, and Arizona's must RESOLVE here
# because the Tier-1 conformity batch was seeded above (mirroring prod, D-10).
for code in AZ.EXISTING_SOURCES_TO_REFERENCE:
    check(AuthoritySource.objects.filter(source_code=code).exists(),
          f"existing Arizona anchor {code} RESOLVES (seeded by the Tier-1 conformity batch)",
          f"existing Arizona anchor {code} did NOT resolve -- check _state_conformity_tier1.py")
check(set(AZ.EXISTING_SOURCES_TO_REFERENCE)
      == {"AZ_HB4168_2026_CH140", "AZ_ARS_43_1022", "AZ_ARS_43_1122"},
      "EXISTING_SOURCES_TO_REFERENCE reuses the three seeded Arizona anchors rather than "
      "re-creating them (campaign D-10 / D-8)",
      f"EXISTING_SOURCES_TO_REFERENCE is wrong: {AZ.EXISTING_SOURCES_TO_REFERENCE}")
recreated = [s["source_code"] for s in AZ.AUTHORITY_SOURCES
             if s["source_code"] in AZ.EXISTING_SOURCES_TO_REFERENCE]
check(not recreated, "no already-seeded Arizona source is re-created by this loader",
      f"loader re-creates already-seeded sources: {recreated}")

# ⚠ U21: cite what actually exists. No AuthoritySource may claim A.R.S. 43-1011.
_1011 = [s["source_code"] for s in AZ.AUTHORITY_SOURCES if "43_1011" in s["source_code"]]
check(not _1011,
      "no AuthoritySource is created for A.R.S. 43-1011 -- its azleg pages 404 / serve a "
      "superseded 4.50% version (U21), so the 2.5% rate is cited to the FORM FACES and Pub 713",
      f"an AuthoritySource claims A.R.S. 43-1011, which cannot be read: {_1011}")

# ==========================================================================
# 6. THE VERIFIED NEGATIVES -- pinned so nobody adds a field "for symmetry"
# ==========================================================================
check(AZ.AZ_120S_HAS_MODIFICATION_APPARATUS is False
      and AZ.AZ_120S_HAS_DEPRECIATION_LOGIC is False
      and AZ.AZ_120S_LINE37_EQUALS_LINE1 is True,
      "VERIFIED NEGATIVE PINNED: Form 120S has NO modification apparatus, NO depreciation logic, "
      "and line 37 == line 1",
      "the Form 120S verified negative was weakened")
for helper in ("az_120s_modification", "az_120s_depreciation_adjustment"):
    try:
        getattr(AZ, helper)()
        FAILURES.append(f"{helper}() did NOT raise -- the Form 120S negative is unguarded")
    except AZ.ArizonaFormGovernsError as exc:
        check("VERIFIED NEGATIVE" in str(exc)
              or "no arizona depreciation adjustment" in str(exc).lower()
              or "no federal-to-arizona modification" in str(exc).lower(),
              f"{helper}() RAISES and explains the verified negative",
              f"{helper}() raised but without the explanation")
    except Exception as exc:  # noqa: BLE001
        FAILURES.append(f"{helper}() raised the wrong exception: {exc!r}")

proof = AZ.AZ_120S_NEGATIVE_PROOF
check(proof["modification_statute_citations_in_the_28_page_book"]
      == {"43-1021": 0, "43-1022": 0, "43-1121": 0, "43-1122": 0},
      "the negative's statute-cite census is pinned: all four Arizona modification statutes are "
      "cited ZERO times in the Form 120S book",
      "the statute-cite census was altered")
check(proof["arizona_basis_string_occurrences"] == 0
      and proof["addition_subtraction_hits_read_in_context"] == 70
      and sum(proof["buckets"].values()) == 58,
      "the 70 addition/subtract* hits are pinned as READ IN CONTEXT and bucketed -- the alarm was "
      "a FALSE POSITIVE, not an unexamined lexical negative",
      "the addition/subtraction bucket record was altered")

# The absence must also be structural, not just a flag: no 120S fact, line or
# rule may look like a modification.
_120s_facts = {f["fact_key"] for f in AZ.AZ120S_FACTS}
_bad_facts = [k for k in _120s_facts
              if any(t in k for t in ("_addition", "_subtraction", "_depreciation", "_bonus",
                                      "arizona_basis", "_modification"))]
check(not _bad_facts,
      "NO AZ_120S fact key looks like an Arizona modification, addition, subtraction or "
      "depreciation field -- the absence is structural, not merely flagged",
      f"AZ_120S has modification-shaped facts: {_bad_facts}")
_120s_lines = {ln["line_number"] for ln in AZ.AZ120S_LINES}
check(not ({"A1", "B1", "B2", "B3", "B4", "B5"} & _120s_lines),
      "NO AZ_120S line carries a Form 165 Schedule A/B row number -- its Schedule A is the "
      "APPORTIONMENT FORMULA",
      f"AZ_120S carries Form 165 modification line numbers: {sorted({'A1','B1','B2','B3','B4','B5'} & _120s_lines)}")

check(AZ.AZ_165_BONUS_REGIME == "individual" and AZ.AZ_CORPORATE_BONUS_REGIME == "decoupled",
      "the OPPOSITE bonus regimes are pinned: Form 165 applies the INDIVIDUAL rule "
      "(43-1022(17)(e)) while corporations DECOUPLE (43-1122(20))",
      "the individual/corporate bonus split was flattened")
check(AZ.AZ_179_FORM_LINE_EXISTS is False and AZ.AZ_43_1412_CATEGORY_COUNT == 16,
      "pinned: NEITHER Arizona PTE form states a 179 figure, and line 9 covers SIXTEEN statutory "
      "categories in one undifferentiated box",
      "the 179 / 43-1412 record was altered")
check(AZ.AZ_1021_15_ENTITY_ADDBACK_BUILT is False and AZ.AZ_1021_15_OWNER_ADDBACK_BUILT is True,
      "pinned: the 43-1021(15) add-back is built at OWNER level only (D-12 A3) and the entity "
      "half is deliberately absent",
      "the 43-1021(15) build posture was altered")
check(all(len(v) == 4 for v in AZ.AZ_OWNER_ADDBACK_LINES.values())
      and len(AZ.AZ_OWNER_ADDBACK_LINES) == 4,
      "all FOUR owner schedules carry FOUR add-back lines each -- Arizona vs other-state x "
      "prior-year vs current-year",
      f"the owner add-back map is wrong: {AZ.AZ_OWNER_ADDBACK_LINES}")
check(AZ.AZ_PART7_SURVIVES_NON_ELECTION_YEAR is True,
      "pinned: Part 7 / Part 5 must still be issued for a PRIOR-year election, so 'if Q.A = No, "
      "suppress' is not a valid shortcut",
      "the prior-year add-back survival rule was dropped")
check(AZ.AZ_165_SCHK1_LINE3_HAS_SBI_ROUTE is False
      and AZ.AZ_SBI_REACHES_ENTITY_COMPUTATION is False
      and AZ.AZ_SBI_ENTITY_BOOK_HITS == 0,
      "pinned: SBI reaches NEITHER entity computation, and Form 165 Schedule K-1 line 3 has NO SBI "
      "destination (U6)",
      "the SBI negatives were weakened")
check(AZ.AZ_120S_HAS_DEMINIMIS_CARVE_OUT is False
      and AZ.AZ_OPTICAL_MEDIA_K1_PATH[F120S] is False
      and AZ.AZ_OPTICAL_MEDIA_K1_PATH[F165] is True,
      "pinned: Form 120S has NO de-minimis carve-out and NO optical-media K-1 path -- both exist "
      "only on the partnership side, and neither may be ported",
      "a partnership-only rule was ported to Form 120S")
check(AZ.AZ_120S_NONREFUNDABLE_CREDITS_REACH_PTE_TAX is False
      and AZ.AZ_165_HAS_ENTITY_CREDIT_LINE is False,
      "pinned: nonrefundable credits cannot reach the 120S PTE tax, and Form 165 has no "
      "entity-level credit line at all",
      "the credit-ordering record was altered")

# ==========================================================================
# 7. Arithmetic oracles
# ==========================================================================
# --- the FIVE depreciation vintage tiers ----------------------------------
check(AZ.AZ_165_B1_TIER_COUNT == 5 and len(AZ.AZ_165_B1_TIERS) == 5,
      "Form 165 line B1 has FIVE placed-in-service vintage tiers (the brief's 'four' was "
      "CORRECTED on verification -- section 16.4 C6)",
      f"tier count wrong: {AZ.AZ_165_B1_TIER_COUNT} / {len(AZ.AZ_165_B1_TIERS)}")
for ty, want in ((2010, "0.00"), (2012, "0.00"), (2013, None), (2014, "0.10"), (2015, "0.10"),
                 (2016, "0.55"), (2017, "1.00"), (2025, "1.00")):
    got = AZ.az_165_b1_bonus_pct(ty)
    check(got == want,
          f"line B1 tier oracle: a TY{ty} placed-in-service year gives {want!r}",
          f"line B1 tier oracle FAILED for TY{ty}: got {got!r}, want {want!r}")
check(AZ.az_165_b1_tier(2013)["method"] == "ITP_16_2",
      "the TY2013 tier returns the ITP_16_2 sentinel with a NULL percentage -- that is U1, the "
      "only unpulled document gating a mainstream line, NOT a bug",
      "the TY2013 tier no longer defers to ITP 16-2")
check(AZ.AZ_165_B1_KEYED_ON == "placed_in_service",
      "line B1 is keyed on PLACED IN SERVICE -- Arizona states it four times in four sentences, so "
      "unlike TN and TX (D-10 rulings 3 and 4) NO date-keying ruling is needed",
      "the line B1 date keying was altered")

# --- the $150,000 boundary, pinned in BOTH directions ---------------------
check(AZ.az_estimated_payments_required(150_000) is False,
      "$150,000 BOUNDARY: an entity at EXACTLY $150,000 is OUT ('exceeds', seven sources incl. "
      "the statute)",
      "BOUNDARY DRIFT: exactly $150,000 was treated as IN -- an earlier verification pass made "
      "exactly this error and a later one caught it")
check(AZ.az_estimated_payments_required(150_001) is True,
      "$150,000 BOUNDARY: $150,001 is IN",
      "$150,001 was treated as OUT")
check(AZ.az_estimated_payments_required(149_999) is False,
      "$150,000 BOUNDARY: $149,999 is OUT",
      "$149,999 was treated as IN")
check(AZ.AZ_EST_BOUNDARY == "exceeds"
      and AZ.AZ_EST_BOUNDARY_EXACTLY_AT_THRESHOLD_IS_IN is False
      and AZ.AZ_EST_BOUNDARY_SOURCE_COUNT_EXCEEDS == 7
      and AZ.AZ_EST_BOUNDARY_SOURCE_COUNT_OR_MORE == 1,
      "the boundary evidence is pinned inline: SEVEN sources say 'exceeds', ONE Pub 713 FAQ says "
      "'or more', and Pub 713 is internally inconsistent three ways",
      "the boundary evidence record was altered")
check("wrong" in AZ.AZ_EST_BOUNDARY_CORRECTION_HISTORY.lower()
      and "az_conformity.md" in AZ.AZ_EST_BOUNDARY_CORRECTION_HISTORY,
      "the correction history travels WITH the constant, so a later pass can RE-ADJUDICATE rather "
      "than inherit -- and it names the campaign file that still needs amending",
      "the boundary correction history is missing or does not name the stale campaign file")

# --- the measurement basis: a RULING with the losers on record ------------
check(AZ.AZ_EST_MEASUREMENT_BASIS == "statutory_bare_taxable_income",
      "the $150,000 measurement basis is the statute's bare 'taxable income' (campaign D-12 A1)",
      f"measurement basis wrong: {AZ.AZ_EST_MEASUREMENT_BASIS}")
check(len(AZ.AZ_EST_MEASUREMENT_BASIS_CANDIDATES) == 4
      and AZ.AZ_EST_MEASUREMENT_BASIS in AZ.AZ_EST_MEASUREMENT_BASIS_CANDIDATES,
      "all FOUR AZDOR measurement bases stay on the record so a DOR answer can be ADJUDICATED "
      "rather than inherited",
      "the four-candidate conflict record was collapsed")
check(all("not refuted" in v["status"] for k, v in AZ.AZ_EST_MEASUREMENT_BASIS_CANDIDATES.items()
          if k != AZ.AZ_EST_MEASUREMENT_BASIS),
      "the three losing readings are recorded as NOT REFUTED -- D-12 A1 is a ruling on a contested "
      "question, not a finding",
      "a losing measurement-basis candidate was marked refuted")
check("RULING" in AZ.AZ_EST_MEASUREMENT_BASIS_RULING
      and "NOT A PUBLISHED AZDOR POSITION" in AZ.AZ_EST_MEASUREMENT_BASIS_RULING.upper()
      and "U19" in AZ.AZ_EST_MEASUREMENT_BASIS_RULING,
      "the ruling text says plainly that it is NOT a published AZDOR position and that U19 stays open",
      "the ruling text does not disclaim itself as a published position")
check(len(AZ.AZ_EST_INTERNAL_CONTRADICTIONS) == 4,
      "FOUR of the six AZDOR documents contradict themselves internally on the measurement base",
      f"the internal-contradiction record is wrong: {len(AZ.AZ_EST_INTERNAL_CONTRADICTIONS)}")

# --- the required annual payment, and the installment calendar ------------
check(AZ.az_required_annual_payment(100_000, 80_000) == 80_000
      and AZ.az_required_annual_payment(100_000, 95_000) == 90_000
      and AZ.az_required_annual_payment(100_000, None) == 90_000,
      "required annual payment = THE SMALLER OF 90% current-year or 100% prior-year (a SAFE "
      "HARBOUR framing, not a minimum)",
      "the required-annual-payment safe harbour is wrong")
check(len(AZ.AZ_PTE_INSTALLMENT_MONTHS) == 4
      and "1st month" in AZ.AZ_PTE_INSTALLMENT_MONTHS[3]
      and "FOLLOWING" in AZ.AZ_PTE_INSTALLMENT_MONTHS[3].upper(),
      "the FOURTH PTE installment is the 15th day of the 1ST MONTH AFTER the close of the taxable "
      "year -- not the 12th month",
      f"installment calendar wrong: {AZ.AZ_PTE_INSTALLMENT_MONTHS}")
check(AZ.AZ_PTE_INSTALLMENT_MONTHS != AZ.AZ_CORP_INSTALLMENT_MONTHS,
      "the PTE and CORPORATE installment patterns are kept separate -- Form 220/PTE line 7 prints "
      "the corporate one on its FACE and appends 'PTE's see instructions'",
      "the PTE installment pattern collapsed into the corporate one")

# --- the compound conformity date ----------------------------------------
c25, c26 = AZ.az_conformity(2025), AZ.az_conformity(2026)
check(c25["base_irc_date"] == "2025-01-01" and c25["includes_retroactively_effective_obbba"] is True
      and c25["subsection"].endswith("43-105(B)"),
      "TY2025 conformity is the COMPOUND rule: IRC as of 1/1/2025 PLUS retroactively-effective "
      "OBBBA, under the RENUMBERED subsection (B)",
      f"TY2025 conformity wrong: {c25}")
check(c26["base_irc_date"] == "2026-01-01" and c26["includes_retroactively_effective_obbba"] is False
      and c26["subsection"].endswith("43-105(A)"),
      "TY2026 is a DIFFERENT SUBSECTION and a clean 1/1/2026 -- which is what the practitioner "
      "headline actually describes",
      f"TY2026 conformity wrong: {c26}")
check(AZ.az_conformity_is_compound(2025) is True and AZ.az_conformity_is_compound(2026) is False,
      "the compound-vs-clean distinction is explicit, so 'Arizona conformed to January 1, 2026' "
      "cannot be applied to a TY2025 return",
      "the compound conformity flag is wrong")
check(c25["obbba_provision_map_published_by_azdor"] is False,
      "the conformity structure records that AZDOR has published NO provision-by-provision OBBBA "
      "mapping (U3, open as a fact)",
      "the U3 gap was closed without evidence")
try:
    AZ.az_conformity(2027)
    FAILURES.append("_yk() did NOT raise for an unseeded tax year -- TY2027 could inherit TY2025 law")
except KeyError as exc:
    check("tax-year-keyed" in str(exc), "_yk() RAISES on an unseeded tax year and explains why",
          "_yk() raised but without the staleness explanation")
check(AZ.az_168n_addback_applies(2025) is False and AZ.az_168n_addback_applies(2026) is True,
      "IRC 168(n) QPP: NO Arizona add-back for TY2025, add-back from TY2026 (Ch. 140 Secs. 14/22 "
      "and Sec. 35(B))",
      "the 168(n) year gate is wrong")
check("43-105" in AZ.AZ_CH140_RETRO_TY2025_SECTIONS and "43-1021" in AZ.AZ_CH140_RETRO_TY2026_SECTIONS,
      "the Ch. 140 Sec. 35 retroactivity SPLIT is pinned -- 43-105 reaches TY2025 while 43-1021 "
      "reaches only TY2026, which is why 168(n) is a TY2026 item",
      "the Ch. 140 retroactivity split was flattened")

# --- the rate, pinned to the FACE ----------------------------------------
check(AZ.az_pte_rate(2025) == "0.0250", "the PTE rate is 2.5% for TY2025",
      f"PTE rate wrong: {AZ.az_pte_rate(2025)}")
check("PRE-PRINTED ON BOTH FORM FACES" in AZ.AZ_PTE_RATE_SOURCE,
      "the rate is pinned to the FORM FACE, not to a statutory lookup -- if Arizona's individual "
      "rate moves, the form is reprinted and the form is what is e-filed",
      "the rate's provenance no longer points at the form faces")
check("U21" in AZ.AZ_PTE_RATE_STATUTORY_BASIS and "404" in AZ.AZ_PTE_RATE_STATUTORY_BASIS,
      "the 43-1011 provenance gap (U21) travels WITH the rate constant",
      "the U21 provenance warning was dropped from the rate constant")
try:
    AZ.az_pte_rate(2027)
    FAILURES.append("az_pte_rate() did NOT raise for TY2027")
except KeyError:
    PASSES.append("az_pte_rate() is tax-year-keyed and RAISES for an unseeded year")

# --- the conditional $50 minimum -----------------------------------------
check(AZ.az_120s_line12_tax(0, True) == 50.0,
      "Form 120S line 12: $50 minimum applies at a ZERO Arizona figure when federal-level income exists",
      "the conditional $50 minimum failed at zero")
check(AZ.az_120s_line12_tax(-50_000, True) == 50.0,
      "Form 120S line 12: $50 minimum applies at a NEGATIVE Arizona figure when federal-level "
      "income exists ('even if line 11 is zero or a negative amount')",
      "the conditional $50 minimum failed at a negative figure")
check(approx(AZ.az_120s_line12_tax(100_000, True), 4_900),
      "Form 120S line 12: 4.9% of $100,000 = $4,900",
      "the 4.9% corporate rate is wrong")
check(AZ.az_120s_line12_tax(100_000, False) is None,
      "Form 120S line 12 is BLANK (None), not zero, when there is NO federal-level taxable income "
      "-- a CONDITIONAL minimum, not an unconditional one",
      "line 12 returned a value with no federal-level taxable income; do not port another state's "
      "flat minimum tax")

# --- the dynamic apportionment divisor -----------------------------------
check(AZ.az_apportionment_divisor(False, False, False) == 4,
      "divisor 4 when no factor is excluded", "divisor wrong with all factors present")
check(AZ.az_apportionment_divisor(True, False, False) == 3
      and AZ.az_apportionment_divisor(False, True, False) == 3,
      "divisor 3 when PROPERTY or PAYROLL is excluded", "divisor wrong with property/payroll excluded")
check(AZ.az_apportionment_divisor(False, False, True) == 2,
      "divisor TWO when the SALES factor is excluded -- even though sales is DOUBLE-WEIGHTED; the "
      "weighting and the divisor are not tied together",
      "divisor wrong when sales is excluded")
check(AZ.az_apportionment_divisor(True, False, True) is None,
      "NO DIVISOR when two factors are excluded -- the survivor IS the ratio, unweighted",
      "divisor wrong with two factors excluded")
check(AZ.az_factor_is_excluded(0, 0) is True and AZ.az_factor_is_excluded(0, 5_000_000) is False,
      "a factor is excluded IFF BOTH numerator and denominator are zero (A.A.C. R15-2D-901(B)) -- "
      "a zero numerator over a positive denominator is a LIVE ZERO FACTOR",
      "the factor-exclusion rule is wrong -- this is the rule most engines get wrong")

# --- nexus semantics ------------------------------------------------------
check(AZ.az_nexus_from_ratio("0.000000") == AZ.AZ_RATIO_ZERO_MEANS
      and AZ.az_nexus_from_ratio(None) == AZ.AZ_RATIO_BLANK_MEANS
      and AZ.az_nexus_from_ratio("1.000000") == AZ.AZ_RATIO_BLANK_MEANS
      and AZ.az_nexus_from_ratio("0.000000") != AZ.az_nexus_from_ratio(None),
      "'0.000000' means NO ARIZONA NEXUS while BLANK and '1.000000' mean sourced ENTIRELY within "
      "Arizona -- a null-vs-zero bug here silently zeroes every nonresident's Arizona income",
      "the nexus semantics collapsed blank and zero")

# --- the inverted multistate booleans ------------------------------------
check(AZ.az_is_multistate(F165, True) is False and AZ.az_is_multistate(F165, False) is True,
      "Form 165 question D: 'Yes' = ARIZONA-ONLY = NOT multistate",
      "Form 165's multistate polarity is wrong")
check(AZ.az_is_multistate(F120S, True) is True and AZ.az_is_multistate(F120S, False) is False,
      "Form 120S question B: 'Yes' = within and without Arizona = IS multistate",
      "Form 120S's multistate polarity is wrong")
check(AZ.az_is_multistate(F165, True) != AZ.az_is_multistate(F120S, True),
      "the two Arizona forms ask the SAME question in OPPOSITE polarity -- a shared boolean is "
      "wrong for one of them",
      "the inverted multistate booleans were collapsed")
try:
    AZ.az_is_multistate("AZ_NONSENSE", True)
    FAILURES.append("az_is_multistate() accepted an unknown form code instead of refusing")
except AZ.ArizonaFormGovernsError:
    PASSES.append("az_is_multistate() REFUSES an unknown form code rather than defaulting")

# --- the Part 2 gate ------------------------------------------------------
check(AZ.az_part2_required(True, 0) is True
      and AZ.az_part2_required(False, 40_000) is True
      and AZ.az_part2_required(False, 0) is False,
      "Part 2 opens on `Q.A == Yes OR pte_estimates_paid > 0` -- branching on question A alone "
      "suppresses Part 2 for exactly the population that most needs it in TY2025",
      "the Part 2 gate is wrong")

# --- MSP and ACA ----------------------------------------------------------
_msp = AZ.az_msp_qualifies(900_000, 1_000_000)
check(_msp["A3"] == "0.900000" and _msp["qualifies_on_A4"] is True,
      "Schedule MSP: A3 = A1/A2 to six decimals, qualifying above 0.850000",
      f"MSP qualification oracle failed: {_msp}")
check(AZ.az_msp_qualifies(850_000, 1_000_000)["qualifies_on_A4"] is False,
      "Schedule MSP: exactly 0.850000 does NOT qualify ('Is line A3 MORE THAN 0.850000?')",
      "the MSP threshold is not strictly greater than")
check(AZ.AZ_MSP_BINDING_YEARS == 5 and AZ.AZ_MSP_REQUIRES_TIMELY_ORIGINAL_RETURN is True
      and AZ.AZ_PTE_ELECTION_TIMELINESS_REQUIRED is False,
      "TWO ELECTIONS ON ONE RETURN WITH OPPOSITE TIMELINESS RULES: MSP needs a timely ORIGINAL "
      "return and binds five years; the PTE election needs neither",
      "the MSP / PTE timeliness divergence was flattened")
check(AZ.az_aca_ratio(1_000, 4_000) == "0.250000" and AZ.az_aca_ratio(0, 0) == "0.000000",
      "Schedule ACA line 3 = line 1 / line 2 to six decimals, with a safe zero denominator",
      "the Schedule ACA ratio is wrong")

# --- the election, and its cascade ---------------------------------------
check(AZ.AZ_PTE_ELECTION_IS_ANNUAL is True and AZ.AZ_PTE_ELECTION_BINDS_FUTURE_YEARS is False,
      "the PTE election is ANNUAL and does NOT bind future years -- contrast 43-1126(C), which DOES "
      "carry the federal S election forward",
      "the election was made binding on future years")
check(AZ.AZ_PTE_NON_RESPONSE_MEANS == "included" and AZ.AZ_PTE_OPT_OUT_NOTICE_DAYS == 60,
      "opt-OUT, not opt-in: non-response within the 60-day notice period means INCLUDED "
      "(43-1014(D))",
      "the opt-out mechanics are wrong")
check(AZ.AZ_PTE_TIERED_PARTICIPATION_ALLOWED is False
      and AZ.AZ_PTE_LOOK_THROUGH_OWNERS_MAY_PARTICIPATE is True,
      "no tiered participation, but look-through owners (grantor trusts, SMLLCs disregarded to an "
      "individual) CAN participate",
      "the eligibility rules are wrong")
check("Sec. 6" in AZ.AZ_CH182_SECTION_MAP and "43-1014" in AZ.AZ_CH182_SECTION_MAP["Sec. 6"]
      and "43-1414" in AZ.AZ_CH182_SECTION_MAP["Sec. 7"],
      "the CORRECTED Laws 2025 Ch. 182 section map is pinned (the brief was OFF BY ONE in seven "
      "places: Sec.6 = 43-1014, Sec.7 = 43-1414, Sec.9 = Retroactivity)",
      "the Ch. 182 section map is wrong or reverted to the off-by-one numbering")
check(AZ.AZ_ES_BOOKLET_CARRIES_REPEALED_LAW is True,
      "pinned: Booklet 120/165ES carries REPEALED law on election timeliness -- vouchers only",
      "the ES booklet stale-law warning was dropped")

# --- Form 165PA -----------------------------------------------------------
try:
    AZ.az_165pa_rate()
    FAILURES.append("az_165pa_rate() did NOT raise -- Form 165PA must be RED-DEFERRED (D-12 A2)")
except AZ.ArizonaDeferredFormError as exc:
    check("RED-DEFER" in str(exc) and "80%" in str(exc),
          "az_165pa_rate() RAISES and explains that building to the face over-taxes by 80%",
          "az_165pa_rate() raised but without the over-taxation explanation")
check(AZ.AZ_165PA_FACE_RATE == "0.045" and AZ.AZ_165PA_STATUTORY_RATE == "0.025"
      and len(AZ.AZ_165PA_FAMILY) == 4,
      "the 165PA conflict is recorded in full and the WHOLE FAMILY is deferred (165PA + Sch. K-1 + "
      "Sch. K-1(NR) + 165PA-X)",
      "the 165PA conflict record or family list was altered")
check(AZ.AZ_165PA_LATE_FILING_PENALTY_PCT == "0.045"
      and "DO NOT CONFLATE" in AZ.AZ_165PA_TWO_45S_WARNING.upper(),
      "the SECOND 4.5% -- the 165PA LATE-FILING PENALTY, which is CORRECT -- is preserved with its "
      "do-not-conflate warning",
      "the two-4.5%s warning was dropped; a search-and-replace would break the penalty")
check("Sec. 7" in AZ.AZ_165PA_CONFLICT and "ZERO times" in AZ.AZ_165PA_CONFLICT,
      "both 165PA negatives are pinned: Ch. 182 Sec. 7 amended subsection (A) ONLY, and 43-1414 "
      "occurs ZERO times in Ch. 140",
      "a 165PA vintage negative was dropped")
check(AZ.AZ_165PA_K1NR_TRIGGERS_AMENDED_165 is True,
      "pinned: a RECEIVED 165PA Schedule K-1(NR) still forces an amended Form 165 even while "
      "COMPUTING a 165PA is deferred -- receiving one and computing one are different things",
      "the received-165PA amended-return trigger was dropped with the deferral")

# --- A4, the corporate partner -------------------------------------------
_a4 = AZ.az_corporate_partner_adjustment(54_000)
check(_a4["pass_through_amount"] == 54_000.0 and _a4["column"] == "(a)"
      and _a4["recomputed_on_corporate_basis"] is None
      and _a4["review_diagnostic"] == AZ.AZ_A4_DIAGNOSTIC_ID,
      "A4: the K-1 figure passes through AS PRINTED in COLUMN (a), nothing is recomputed, and a "
      "review diagnostic is raised (campaign D-12 A4)",
      f"the A4 pass-through is wrong: {_a4}")
check("open" in _a4["open_fact"].lower() and "U2" in _a4["open_fact"],
      "A4 carries its open fact (U2 / W9) rather than presenting the ruling as settled law",
      "the A4 open fact was dropped")

# --- the entity-level add-back guard --------------------------------------
try:
    AZ.az_entity_level_pte_addback(25_000)
    FAILURES.append("az_entity_level_pte_addback() did NOT raise -- D-12 A3 says owner level only")
except AZ.ArizonaFormGovernsError as exc:
    check("OWNER LEVEL ONLY" in str(exc).upper() and "D-12 A3" in str(exc),
          "az_entity_level_pte_addback() RAISES and names the ruling",
          "the entity add-back guard raised but did not name D-12 A3")
check("circular" in AZ.AZ_1021_15_CIRCULARITY.lower() or "CIRCULARITY" in AZ.AZ_1021_15_CIRCULARITY.upper(),
      "the cash-basis circularity is RECORDED rather than fixed -- the base is understated by the "
      "PTE tax itself",
      "the cash-basis circularity record was dropped")

# --- 179 -----------------------------------------------------------------
_179 = AZ.az_179_limits(2025)
check(_179["limit"] == 2_500_000 and _179["phaseout"] == 4_000_000
      and _179["basis"] == "ruling" and _179["unverified_item"] == "U3",
      "179 = $2,500,000 / $4,000,000 for TY2025 BY RULING (D-10), carried together with its open "
      "U3 gap",
      f"the 179 record is wrong: {_179}")
check("RULING" in AZ.AZ_179_PROVENANCE and "OPEN AS A MATTER OF FACT" in AZ.AZ_179_PROVENANCE.upper(),
      "the 179 provenance says plainly that it is a ruling and that the gap stays open",
      "the 179 provenance no longer carries both the ruling and the gap")
check("line 9" in AZ.AZ_179_PARTNERSHIP_ROUTE and "none" in AZ.AZ_179_SCORP_ROUTE.lower(),
      "the 179 ROUTING that D-10 did not reach is recorded: Form 165 line 9 for a partnership, no "
      "routing question at all for an S corporation",
      "the 179 routing record is wrong")

# --- SBI ------------------------------------------------------------------
check(sum(len(v) for v in AZ.AZ_SBI_ROUTING_LINES.values()) == 18
      and AZ.AZ_SBI_LINE_COUNT == 18,
      "the SBI routing map RECOMPUTES to EIGHTEEN lines (4+4+1+4+1+4) -- the brief's prose said 17 "
      "in three places and was CORRECTED on verification; the table was always right",
      f"SBI line count wrong: {sum(len(v) for v in AZ.AZ_SBI_ROUTING_LINES.values())}")
check(AZ.AZ_SBI_LINE_COUNT_INCLUDING_CREDIT_LINES == 22
      and "own printed routing block" in AZ.AZ_SBI_COUNTING_BASIS,
      "the COUNTING BASIS is stated explicitly and the alternative (22, including the four "
      "PTE-credit lines) is recorded -- any loader must pick one basis and hold it",
      "the SBI counting basis is not stated")
check(AZ.AZ_QUALIFIED_SMALL_BUSINESS_HITS == {F165: 14, F120S: 12}
      and "QUALIFIED small business" in AZ.AZ_SBI_VOCABULARY_TRAP,
      "the vocabulary trap is pinned: all 26 'small business' hits in the entity books are "
      "'QUALIFIED small business' (43-1022(21)) -- a DIFFERENT REGIME",
      "the SBI vocabulary trap was dropped")

# --- printed defects ------------------------------------------------------
check(AZ.AZ_PRINTED_DEFECT_COUNT == len(AZ.AZ_PRINTED_DEFECTS) >= 8,
      f"{AZ.AZ_PRINTED_DEFECT_COUNT} printed defects are transcribed AS PRINTED and flagged, never "
      "silently 'fixed'",
      "the printed-defect register is incomplete")
_defect_ids = {d["defect_id"] for d in AZ.AZ_PRINTED_DEFECTS}
check({"AZ-D1", "AZ-D2", "AZ-D3", "AZ-D4", "AZ-D5"} <= _defect_ids,
      "the five substantive printed defects are all registered (stale year, the line-45 "
      "cross-check, the two Form 220/PTE routing errors, and the mislabelled K-1(NR) line 20)",
      f"a substantive printed defect is missing: {_defect_ids}")
_reconfirmed = [d["defect_id"] for d in AZ.AZ_PRINTED_DEFECTS
                if d.get("independently_reconfirmed_by_verification_pass")]
check(len(_reconfirmed) >= 4,
      f"{len(_reconfirmed)} printed defects were INDEPENDENTLY RE-CONFIRMED by the verification "
      "pass, and that provenance travels with them",
      "the re-confirmation provenance was dropped")
check(AZ.AZ_FACE_GOVERNS_OVER_INSTRUCTIONS is True
      and "SUPPORTING form" in AZ.AZ_FACE_GOVERNS_NOTE
      and "EXCEPTION" in AZ.AZ_FACE_GOVERNS_NOTE.upper(),
      "the 'face governs' convention is recorded WITH its two boundaries -- a supporting form's "
      "routing list is a different question, and the Form 165 zero floor runs the other way",
      "the face-governs note lost one of its boundaries")

# --- the Massachusetts Form 355 collision ---------------------------------
check("MASSACHUSETTS" in AZ.AZ_FORM_355_COLLISION_NOTE.upper(),
      "the ARIZONA Form 355 / MASSACHUSETTS Form 355 collision is named, so the next reader is not "
      "trapped",
      "the Form 355 collision note was dropped")
check(AZ.AZ_FORM_355_LINE_BY_ENTITY[AZ.M_1065].endswith("line 1")
      and AZ.AZ_FORM_355_LINE_BY_ENTITY[AZ.M_1120S].endswith("line 2"),
      "the Arizona Form 355 line differs by entity type: partnership K-1s -> Part 1 line 1; S-corp "
      "K-1s -> Part 1 line 2",
      "the Form 355 line-by-entity map is wrong")

# ==========================================================================
# 8. RED-DEFERS and the open [UNVERIFIED] register
# ==========================================================================
missing_rd = [d for d in AZ.AZ_RED_DEFERS
              if not FormDiagnostic.objects.filter(tax_form__jurisdiction="AZ",
                                                   diagnostic_id=d).exists()]
check(not missing_rd,
      f"all {AZ.AZ_RED_DEFER_COUNT} RED-DEFERS carry their own diagnostic -- NO SILENT GAP, AND "
      "NOTHING SILENTLY INCLUDED EITHER",
      f"RED-DEFERS with no diagnostic: {missing_rd}")
for did in AZ.AZ_RED_DEFERS:
    check(FormDiagnostic.objects.filter(tax_form__jurisdiction="AZ", diagnostic_id=did,
                                        severity="error").exists(),
          f"RED-DEFER {did} is an ERROR-severity diagnostic",
          f"RED-DEFER {did} is not error severity")

check(AZ.AZ_UNVERIFIED_COUNT == 21,
      "the open register holds 21 [UNVERIFIED] items -- the verification pass closed NONE outright "
      "and ADDED three (U19, U20, U21)",
      f"the [UNVERIFIED] count is {AZ.AZ_UNVERIFIED_COUNT}, not 21")
check(set(AZ.AZ_UNVERIFIED_BLOCKING) == {"U3", "U14", "U19"},
      "the three BLOCKING items are U3 (OBBBA mapping), U14 (165PA rate) and U19 (which taxable "
      "income)",
      f"the blocking set is wrong: {AZ.AZ_UNVERIFIED_BLOCKING}")
_all_diag_ids = set(FormDiagnostic.objects.filter(tax_form__jurisdiction="AZ")
                    .values_list("diagnostic_id", flat=True))
unencoded = []
for uid, rec in AZ.AZ_UNVERIFIED.items():
    enc = rec["encoded_as"]
    named = [tok.strip(" ()+.,") for tok in enc.split() if tok.startswith("D_AZ")]
    if named and not any(n in _all_diag_ids for n in named):
        unencoded.append(f"{uid} -> {named}")
check(not unencoded,
      f"every one of the {AZ.AZ_UNVERIFIED_COUNT} open [UNVERIFIED] items names a diagnostic, a "
      "constant or a helper that actually exists -- NO SILENT GAPS",
      f"[UNVERIFIED] items whose diagnostic does not exist: {unencoded}")

for form in ALL_FORMS:
    for did in ("D_AZ_TY2026_CONFORMITY_STALE", "D_AZ_CONFORMITY_COMPOUND",
                "D_AZ_NO_SHARED_MOD_ENGINE", "D_AZ_PART2_GATE_NOT_QA_ONLY",
                "D_AZ_MULTISTATE_QUESTION_INVERT", "D_AZ_RATIO_ZERO_VS_BLANK",
                "D_AZ_150K_BOUNDARY_EXCEEDS", "D_AZ_U19_150K_BASIS",
                "D_AZ_EST_4TH_INSTALLMENT_MONTH", "D_AZ_FORM_355_COLLISION",
                "D_AZ_179_RULING_NOT_PUBLISHED", "D_AZ_U21_43_1011_CITE"):
        check(FormDiagnostic.objects.filter(tax_form=form, diagnostic_id=did).exists(),
              f"{form.form_number} carries the shared diagnostic {did}",
              f"{form.form_number} is MISSING the shared diagnostic {did}")

_stale = FormDiagnostic.objects.get(tax_form=f165, diagnostic_id="D_AZ_TY2026_CONFORMITY_STALE")
check(_stale.severity == "error" and "43-105(A)" in _stale.message and "168(n)" in _stale.message,
      "the staleness tripwire is an ERROR and names both the subsection switch and the TY2026 "
      "168(n) add-backs",
      "the staleness tripwire is incomplete")
_basis = FormDiagnostic.objects.get(tax_form=f165, diagnostic_id="D_AZ_U19_150K_BASIS")
check("NOT A PUBLISHED AZDOR POSITION" in _basis.notes.upper() and "U19" in _basis.notes,
      "the U19 diagnostic states plainly that D-12 A1 is a ruling, not a published AZDOR position, "
      "and that the fact stays open",
      "the U19 diagnostic does not disclaim the ruling")
_a4d = FormDiagnostic.objects.get(tax_form=f165, diagnostic_id=AZ.AZ_A4_DIAGNOSTIC_ID)
check("U2" in _a4d.notes and "C-CORP-WAVE" in _a4d.notes.upper(),
      "the A4 diagnostic records the open fact and routes it to the C-corp wave",
      "the A4 diagnostic does not record its open fact")
_165pa = FormDiagnostic.objects.get(tax_form=f165, diagnostic_id="D_AZ_RD_165PA_FAMILY")
check("U14" in _165pa.notes and "LATE-FILING PENALTY" in _165pa.notes.upper(),
      "the 165PA RED-DEFER names U14 and preserves the do-not-conflate warning about the second "
      "4.5%",
      "the 165PA RED-DEFER is incomplete")
_nomods = FormDiagnostic.objects.get(tax_form=f120s, diagnostic_id="D_AZ120S_NO_MODIFICATIONS")
check("FALSE POSITIVE" in _nomods.notes.upper() and "70" in _nomods.notes,
      "the Form 120S negative diagnostic carries its own evidence -- 70 hits read in context and "
      "the alarm disproven",
      "the Form 120S negative diagnostic lost its evidence")

# ==========================================================================
# Report
# ==========================================================================
print("\n" + "=" * 78)
print(f"AZ_165 / AZ_120S validation -- {len(PASSES)} PASS / {len(FAILURES)} FAIL "
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
print(f"Shared: flow assertions {FlowAssertion.objects.filter(assertion_id__startswith='FA-AZ').count()} / "
      f"sources {AuthoritySource.objects.filter(source_code__startswith='AZ_').count()} / "
      f"topics {AuthorityTopic.objects.filter(topic_code__startswith='az_').count()} / "
      f"form links {AuthorityFormLink.objects.filter(form_code__startswith='AZ_').count()} / "
      f"excerpts {AuthorityExcerpt.objects.filter(authority_source__source_code__startswith='AZ_').count()}")
print(f"Registers: RED-DEFERS {AZ.AZ_RED_DEFER_COUNT} / open [UNVERIFIED] {AZ.AZ_UNVERIFIED_COUNT} "
      f"(blocking {', '.join(AZ.AZ_UNVERIFIED_BLOCKING)}) / printed defects {AZ.AZ_PRINTED_DEFECT_COUNT} / "
      f"depreciation tiers {AZ.AZ_165_B1_TIER_COUNT} / SBI routing lines {AZ.AZ_SBI_LINE_COUNT}")
print(f"READY_TO_SEED on disk: {AZ.READY_TO_SEED} (MUST remain False -- Gate 1 is open for Arizona)")
sys.exit(1 if FAILURES else 0)
