"""Throwaway-SQLite validation for the MD PTE batch: MD_510 + MD_511 (TY2025).

Checks, in order:
  0. The SAFETY GUARD -- the sentinel is forced DOWN in memory and the loader must REFUSE.
     (Pins the MECHANISM, not the disk value -- campaign D-10's expiry-dated-test lesson.)
  1. CharField caps read from the REAL MODEL FIELDS via _meta.get_field(...).max_length --
     Postgres enforces them, SQLite does NOT, and six Tier-1 citations overflowed 255 on the
     last seed and DataError'd.
  2. No duplicate ids; every FormRule has >= 1 authority link; rule_links resolve both ways.
  3. Identity: MD / 2025 / v1 / draft / entity_types ['1065','1120S'] / conformity anchor.
  4. ARITHMETIC ORACLES driven through the loader's own helpers:
       * the ELECTION STATE MACHINE, including BOTH deeming defaults and the undetermined case
       * THE SAME MEMBER producing DIFFERENT TAX on Form 510 vs Form 511
       * both DCF worksheets (9A scales by ownership; 11A does not) and the CONDITIONAL lesser-of
       * the owner side: credit PLUS add-back, attaching to K-1 D2/D4 and NEVER to D1
       * the zero-factor convention (.000001) and the six-decimal rounding
       * the PTET rate as a DERIVATION with a staleness assertion
       * *** the load-bearing NEGATIVE: NO insignificant-denominator reweighting exists in
         Maryland -- that rule is Fla. Stat. 220.15(1) and must not leak in from the FL wave ***
  5. Every RED-defer R1..R15 has its own diagnostic; the hard blocks are severity 'error'.
  6. Structural spot checks on the two encoded line maps.

ASCII-only output. Run: poetry run python scratchpad/validate_md.py
"""
import os
import sys

PROJECT_ROOT = r"D:\dev\delvio-rule-studio"
sys.path.insert(0, PROJECT_ROOT)

SQLITE_PATH = os.path.join(PROJECT_ROOT, "scratchpad", "validate_md.sqlite3")
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
from specs.management.commands import load_md_pte as MD  # noqa: E402

FAILURES: list[str] = []
PASSES: list[str] = []


def check(cond, ok, bad):
    (PASSES if cond else FAILURES).append(ok if cond else bad)


def approx(a, b, tol=0.005):
    return a is not None and abs(float(a) - float(b)) <= tol


# ══════════════════════════════════════════════════════════════════════
# 0. SAFETY GUARD -- must ship False AND must refuse while it is down.
# ══════════════════════════════════════════════════════════════════════
_shipped_ready = MD.READY_TO_SEED
check(isinstance(_shipped_ready, bool),
      "SAFETY GUARD: the sentinel is a real bool the harness can drive",
      f"SAFETY GUARD BREACHED: READY_TO_SEED = {_shipped_ready!r} is not a bool")
check(_shipped_ready is False,
      "SAFETY GUARD: load_md_pte ships READY_TO_SEED = False (Gate-1 walk not yet held)",
      f"SAFETY GUARD BREACHED: load_md_pte ships READY_TO_SEED = {_shipped_ready!r}, expected False")

MD.READY_TO_SEED = False  # force the guard down so the refusal below is a real test

call_command("migrate", run_syncdb=True, verbosity=0)

try:
    call_command("load_md_pte", verbosity=0)
    FAILURES.append("GUARD DID NOT FIRE: load_md_pte seeded with READY_TO_SEED False")
except Exception as exc:  # noqa: BLE001
    check("REFUSING TO SEED" in str(exc),
          "Guard refuses to seed while READY_TO_SEED is False",
          f"Guard raised the wrong error: {exc!r}")
    check("W3 is WITHDRAWN" in str(exc),
          "Guard message records that W3 is WITHDRAWN (nobody re-raises the false conflict)",
          "Guard message does not record the W3 withdrawal")

check(TaxForm.objects.filter(jurisdiction="MD").count() == 0,
      "Guard wrote NOTHING to the database while refusing",
      "Guard refused but rows were still written")

# Flip IN MEMORY ONLY (never on disk) so the content can be validated.
MD.READY_TO_SEED = True
try:
    call_command("load_md_pte", verbosity=0)
    PASSES.append("load_md_pte ran + seeded into throwaway SQLite without error")
except Exception as exc:  # noqa: BLE001
    FAILURES.append(f"load_md_pte raised: {exc!r}")
    print("\n".join(f"  FAIL  {f}" for f in FAILURES))
    sys.exit(1)

F510, F511 = MD.FORM_510, MD.FORM_511
FORM_SHAPE = {F510: ("MD", ["1065", "1120S"]), F511: ("MD", ["1065", "1120S"])}


# ══════════════════════════════════════════════════════════════════════
# 1. CharField caps -- READ FROM THE REAL MODEL FIELDS, not hardcoded.
#    Postgres enforces these; SQLite silently accepts overlong values.
# ══════════════════════════════════════════════════════════════════════
def cap(model, field_name):
    """Read the REAL max_length off the model field. None = unbounded (TextField)."""
    return model._meta.get_field(field_name).max_length


CAP_SPECS = [
    (TaxForm, ("form_number", "form_title", "jurisdiction", "status")),
    (FormRule, ("rule_id", "title", "rule_type")),
    (FormLine, ("line_number", "line_type")),
    (FormFact, ("fact_key", "label", "data_type")),
    (FormDiagnostic, ("diagnostic_id", "title", "severity")),
    (TestScenario, ("scenario_name", "scenario_type")),
    (FlowAssertion, ("assertion_id", "title", "assertion_type", "status", "bug_reference")),
    (AuthoritySource, ("source_code", "citation", "issuer", "jurisdiction_code", "source_type",
                       "source_rank", "title", "current_status")),
    (AuthorityTopic, ("topic_code", "topic_name")),
    (AuthorityExcerpt, ("excerpt_label",)),
]

# The caps the campaign brief names explicitly -- assert the MODEL still agrees with them,
# so a silent migration cannot quietly widen/narrow what the loader was authored against.
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
for (model, fname), expected in EXPECTED_CAPS.items():
    actual = cap(model, fname)
    check(actual == expected,
          f"model cap {model.__name__}.{fname} = {expected} (as the loader was authored against)",
          f"MODEL CAP DRIFT: {model.__name__}.{fname} is {actual}, loader authored against {expected}")
    check(actual is not None,
          f"{model.__name__}.{fname} is a bounded CharField, so Postgres WILL enforce it",
          f"{model.__name__}.{fname} is unbounded -- the cap assertion would be vacuous")

violations = []
checked = 0
md_forms = list(TaxForm.objects.filter(jurisdiction="MD"))
rows_by_model = {
    TaxForm: md_forms,
    FormRule: list(FormRule.objects.filter(tax_form__in=md_forms)),
    FormLine: list(FormLine.objects.filter(tax_form__in=md_forms)),
    FormFact: list(FormFact.objects.filter(tax_form__in=md_forms)),
    FormDiagnostic: list(FormDiagnostic.objects.filter(tax_form__in=md_forms)),
    TestScenario: list(TestScenario.objects.filter(tax_form__in=md_forms)),
    FlowAssertion: list(FlowAssertion.objects.filter(assertion_id__startswith="FA-MD")),
    AuthoritySource: list(AuthoritySource.objects.filter(jurisdiction_code="MD")),
    AuthorityTopic: list(AuthorityTopic.objects.filter(topic_code__startswith="md_")),
    AuthorityExcerpt: list(AuthorityExcerpt.objects.filter(authority_source__jurisdiction_code="MD")),
}
for model, fields in CAP_SPECS:
    # TextFields (max_length None) are unbounded in Postgres -- nothing to enforce.
    limit_by_field = {f: cap(model, f) for f in fields if cap(model, f) is not None}
    for row in rows_by_model[model]:
        for fname, limit in limit_by_field.items():
            value = getattr(row, fname) or ""
            checked += 1
            if len(value) > limit:
                violations.append(f"{model.__name__}.{fname} len {len(value)} > {limit}: {value[:60]!r}")

check(not violations, f"CharField caps OK against the REAL model fields ({checked} values checked)",
      "CAP VIOLATIONS:\n    " + "\n    ".join(violations))

# The citation overflow that DataError'd on the last seed gets its own explicit assertion.
long_citations = [s.source_code for s in rows_by_model[AuthoritySource]
                  if len(s.citation or "") > cap(AuthoritySource, "citation")]
check(not long_citations,
      f"every MD AuthoritySource.citation <= {cap(AuthoritySource, 'citation')} chars "
      f"({len(rows_by_model[AuthoritySource])} sources)",
      f"CITATION OVERFLOW (the Tier-1 DataError class of bug): {long_citations}")

# Source-list level assertions (catch problems before they ever reach the DB).
check(all(len(r["rule_id"]) <= 20 for s in MD.FORMS for r in s["rules"]),
      "every authored rule_id <= 20 chars", "rule_id > 20 chars present in the source lists")
check(all(len(d["diagnostic_id"]) <= 40 for s in MD.FORMS for d in s["diagnostics"]),
      "every authored diagnostic_id <= 40 chars", "diagnostic_id > 40 chars present in the source lists")
check(all(len(ln["line_number"]) <= 20 for s in MD.FORMS for ln in s["lines"]),
      "every authored line_number <= 20 chars", "line_number > 20 chars present in the source lists")
check(all(len(f["fact_key"]) <= 100 for s in MD.FORMS for f in s["facts"]),
      "every authored fact_key <= 100 chars", "fact_key > 100 chars present in the source lists")
check(all(len(a["assertion_id"]) <= 20 for a in MD.FLOW_ASSERTIONS),
      "every authored assertion_id <= 20 chars", "assertion_id > 20 chars present in the source lists")


# ══════════════════════════════════════════════════════════════════════
# 2. No duplicate ids; every rule has >= 1 authority link; links resolve.
# ══════════════════════════════════════════════════════════════════════
declared_sources = {s["source_code"] for s in MD.AUTHORITY_SOURCES} | set(MD.EXISTING_SOURCES_TO_REFERENCE)
for spec in MD.FORMS:
    fn = spec["identity"]["form_number"]
    form = TaxForm.objects.get(form_number=fn)
    for key, field in (("facts", "fact_key"), ("rules", "rule_id"),
                       ("lines", "line_number"), ("diagnostics", "diagnostic_id")):
        ids = [row[field] for row in spec[key]]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        check(not dupes, f"{fn}: no duplicate {field} ({len(ids)} rows)", f"{fn}: DUPLICATE {field}: {dupes}")
    names = [t["scenario_name"] for t in spec["scenarios"]]
    check(len(names) == len(set(names)), f"{fn}: no duplicate scenario_name", f"{fn}: duplicate scenario_name")

    ruleless = [r.rule_id for r in FormRule.objects.filter(tax_form=form)
                if not RuleAuthorityLink.objects.filter(form_rule=r).exists()]
    check(not ruleless,
          f"{fn}: all {FormRule.objects.filter(tax_form=form).count()} rules have >= 1 authority link",
          f"{fn}: rules with NO authority link: {ruleless}")

    defined = {r["rule_id"] for r in spec["rules"]}
    linked = {rl[0] for rl in spec["rule_links"]}
    check(not (linked - defined), f"{fn}: rule_links reference defined rules", f"{fn}: orphan rule_links {linked - defined}")
    check(not (defined - linked), f"{fn}: every rule appears in rule_links", f"{fn}: unlinked rules {defined - linked}")
    bad_src = {rl[1] for rl in spec["rule_links"]} - declared_sources
    check(not bad_src, f"{fn}: rule_links reference declared sources", f"{fn}: undeclared sources {bad_src}")
    bad_lvl = {rl[2] for rl in spec["rule_links"]} - {"primary", "secondary", "interpretive", "implementation"}
    check(not bad_lvl, f"{fn}: rule_link support levels valid", f"{fn}: bad support levels {bad_lvl}")
    # Every line's source_rules must reference a rule that exists on that form.
    bad_line_rules = sorted({r for ln in spec["lines"] for r in ln.get("source_rules", [])} - defined)
    check(not bad_line_rules, f"{fn}: every line source_rule resolves", f"{fn}: lines cite unknown rules {bad_line_rules}")
    # Every line's source_facts must reference a fact that exists on that form.
    fact_keys = {f["fact_key"] for f in spec["facts"]}
    bad_line_facts = sorted({f for ln in spec["lines"] for f in ln.get("source_facts", [])} - fact_keys)
    check(not bad_line_facts, f"{fn}: every line source_fact resolves", f"{fn}: lines cite unknown facts {bad_line_facts}")

fa_ids = [a["assertion_id"] for a in MD.FLOW_ASSERTIONS]
check(len(fa_ids) == len(set(fa_ids)), "no duplicate assertion_id", "DUPLICATE assertion_id present")
all_diag = [d["diagnostic_id"] for s in MD.FORMS for d in s["diagnostics"]]
check(len(all_diag) == len(set(all_diag)),
      "no duplicate diagnostic_id across both forms", "duplicate diagnostic_id across the two forms")
bad_form_links = {fl[1] for fl in MD.AUTHORITY_FORM_LINKS} - set(FORM_SHAPE)
check(not bad_form_links, "AUTHORITY_FORM_LINKS point at MD_510 / MD_511", f"bad form codes: {bad_form_links}")


# ══════════════════════════════════════════════════════════════════════
# 3. Identity + the conformity anchor.
# ══════════════════════════════════════════════════════════════════════
check(MD.FORM_JURISDICTION == "MD", "FORM_JURISDICTION = MD", f"wrong jurisdiction {MD.FORM_JURISDICTION!r}")
check(MD.FORM_TAX_YEAR == 2025, "FORM_TAX_YEAR = 2025", f"wrong tax year {MD.FORM_TAX_YEAR}")
check(MD.FORM_VERSION == 1 and MD.FORM_STATUS == "draft", "FORM_VERSION = 1, FORM_STATUS = draft", "wrong version/status")
check(MD.FORM_ENTITY_TYPES == ["1065", "1120S"], "FORM_ENTITY_TYPES = ['1065','1120S']",
      f"wrong entity types {MD.FORM_ENTITY_TYPES}")
for fn, (juris, ets) in FORM_SHAPE.items():
    form = TaxForm.objects.get(form_number=fn)
    check(form.jurisdiction == juris and form.tax_year == 2025 and form.entity_types == ets,
          f"{fn}: MD / 2025 / entity_types {ets}",
          f"{fn}: identity wrong ({form.jurisdiction} / {form.tax_year} / {form.entity_types})")
check("MD_TG_10_108" in MD.EXISTING_SOURCES_TO_REFERENCE,
      "EXISTING_SOURCES_TO_REFERENCE anchors the MD conformity source MD_TG_10_108",
      f"conformity anchor missing: {MD.EXISTING_SOURCES_TO_REFERENCE}")
check("MD_TG_10_210_1" in MD.EXISTING_SOURCES_TO_REFERENCE,
      "EXISTING_SOURCES_TO_REFERENCE also anchors MD_TG_10_210_1 (the R10 manufacturing carve-out statute)",
      f"decoupling anchor missing: {MD.EXISTING_SOURCES_TO_REFERENCE}")


# ══════════════════════════════════════════════════════════════════════
# 4. ARITHMETIC ORACLES
# ══════════════════════════════════════════════════════════════════════

# ---- 4a. THE ELECTION STATE MACHINE, including BOTH deeming defaults ----
e = MD._md_election("510_511D", box_a=True, box_b=False)
check(e["form"] == F511 and e["irrevocable"] and not e["deemed"],
      "election: Box A on the 510/511D -> Form 511, irrevocable", f"Box A wrong: {e}")
e = MD._md_election("510_511D", box_a=False, box_b=True)
check(e["form"] == F510 and e["irrevocable"] and not e["deemed"],
      "election: Box B on the 510/511D -> Form 510, irrevocable", f"Box B wrong: {e}")
e = MD._md_election("510_511E", box_a=False, box_b=False)
check(e["form"] == F510 and e["deemed"] and e["irrevocable"],
      "DEEMING DEFAULT 1: neither box on a first filing -> DEEMED Form 510, irrevocably", f"neither-box default wrong: {e}")
e = MD._md_election("510_511E", box_a=True, box_b=True)
check(e["form"] == F511 and e["deemed"] and e["irrevocable"],
      "DEEMING DEFAULT 2: both boxes checked in error -> DEEMED Form 511, irrevocably", f"both-boxes default wrong: {e}")
check(MD._md_election("510_511D", box_a=False, box_b=False)["form"]
      != MD._md_election("510_511D", box_a=True, box_b=True)["form"],
      "the two deeming defaults resolve to OPPOSITE forms (510 vs 511)",
      "the two deeming defaults collapsed to the same form")
e = MD._md_election("year_end_return", year_end_form=F511)
check(e["form"] == F511 and e["deemed"] and e["irrevocable"],
      "no D or E filed: filing Form 511 IS the irrevocable election", f"year-end 511 election wrong: {e}")
e = MD._md_election("year_end_return", year_end_form=F510)
check(e["form"] == F510 and e["deemed"],
      "no D or E filed: filing Form 510 is deemed an irrevocable non-election", f"year-end 510 election wrong: {e}")
e = MD._md_election("unknown")
check(e["form"] is None and "UNDETERMINED" in e["basis"],
      "election UNDETERMINED when the first filing is not on record -- never inferred from return data",
      f"undetermined case wrong: {e}")
e = MD._md_election(None)
check(e["form"] is None,
      "election with no first-filing fact at all -> UNDETERMINED (no silent default)", f"None case wrong: {e}")
e = MD._md_election("year_end_return", year_end_form=None)
check(e["form"] is None,
      "year-end path with no form chosen -> UNDETERMINED rather than a guess", f"year-end None wrong: {e}")
check(MD._md_election_conflict(F511, F510) is True and MD._md_election_conflict(F510, F510) is False,
      "a year-end return contradicting the recorded election is detected as a conflict",
      "election conflict detection wrong")
check(MD._md_amended_may_change_election() is False,
      "an amended return may NEVER change the election or non-election",
      "amended-return election bar is not enforced")
check(MD._md_first_filing_wins(2025) is True and MD._md_first_filing_wins(2026) is False,
      "the election machine is YEAR-KEYED: 'first filing wins' holds for TY2025, suspended for TY2026",
      f"first-filing-wins not year-keyed: 2025={MD._md_first_filing_wins(2025)} 2026={MD._md_first_filing_wins(2026)}")
check(MD.MD_510C_ALLOWED[F510] is True and MD.MD_510C_ALLOWED[F511] is False,
      "composite Form 510C is permitted for a 510 filer and BARRED for an Electing PTE",
      "the 510C bar for electing PTEs is not encoded")

# ---- 4b. THE SAME MEMBER, DIFFERENT BOX, DIFFERENT TAX ----
box510 = MD._md_member_box(F510, "entity", is_resident=True)
box511 = MD._md_member_box(F511, "entity", is_resident=True)
check(box510["line"] == "1d" and box510["taxed"] is False,
      "resident ENTITY member -> Form 510 line 1d 'Others', UNTAXED", f"510 resident entity box wrong: {box510}")
check(box511["line"] == "1c" and box511["taxed"] is True,
      "resident ENTITY member -> Form 511 line 1c 'Nonresident and resident entities', TAXED",
      f"511 resident entity box wrong: {box511}")
t510 = MD._md_member_tax(F510, "entity", True, 100000)
t511 = MD._md_member_tax(F511, "entity", True, 100000)
check(approx(t510, 0.0) and approx(t511, 8250.0),
      "SAME MEMBER (resident entity, 100,000 share): Form 510 tax 0 vs Form 511 tax 8,250",
      f"cross-form resident-entity tax wrong: 510={t510} 511={t511}")
check(t510 != t511, "the two forms genuinely produce different tax for the same member", "cross-form tax collapsed")
t510i = MD._md_member_tax(F510, "individual", True, 200000)
t511i = MD._md_member_tax(F511, "individual", True, 200000)
check(approx(t510i, 0.0) and approx(t511i, 17500.0),
      "SAME MEMBER (resident individual, 200,000 share): Form 510 tax 0 vs Form 511 tax 17,500 (8.75%)",
      f"cross-form resident-individual tax wrong: 510={t510i} 511={t511i}")
nr510 = MD._md_member_tax(F510, "individual", False, 400000)
nr511 = MD._md_member_tax(F511, "individual", False, 400000)
check(approx(nr510, 35000.0) and approx(nr511, 35000.0),
      "nonresident individual, 400,000 share: 26,000 + 9,000 on the 510 and 35,000 on the 511 -- same total, different arithmetic",
      f"nonresident individual tax wrong: 510={nr510} 511={nr511}")
fid = MD._md_member_box(F510, "fiduciary", is_resident=False)
check(fid["line"] == "1b" and fid["rate_key"] == "individual_nonresident",
      "fiduciary members sit in the INDIVIDUAL leg (line 1b), never the entity leg", f"fiduciary box wrong: {fid}")
check(approx(MD._md_member_tax(F510, "fiduciary", False, 100000), 8750.0),
      "nonresident FIDUCIARY taxed at 6.50% + 2.25% = 8,750 on 100,000 (not the 8.25% entity rate)",
      "fiduciary rate wrong")
for form_number in (F510, F511):
    ex = MD._md_member_box(form_number, "entity", is_resident=False, is_exempt=True)
    check(ex["line"] == "1d" and ex["taxed"] is False,
          f"{form_number}: REIT / IRC 408(e) / 501 exempt member -> line 1d, untaxed (TB 6 II.A + TG 10-104)",
          f"{form_number}: exempt member box wrong: {ex}")
nre511 = MD._md_member_box(F511, "entity", is_resident=False)
check(nre511["line"] == "1c", "Form 511 line 1c also holds NONRESIDENT entities", f"511 nonresident entity box wrong: {nre511}")

# ---- 4c. The rate DERIVATION and its staleness assertion ----
check(approx(MD._md_ptet_individual_rate(2025), 0.0875, tol=1e-9),
      "PTET individual rate = 0.0225 (10-106.1) + 0.0650 (10-105(a)) = 0.0875 -- DERIVED",
      f"individual rate wrong: {MD._md_ptet_individual_rate(2025)}")
check(approx(MD._md_ptet_entity_rate(2025), 0.0825, tol=1e-9),
      "PTET entity rate = 0.0825 (10-105(b))", f"entity rate wrong: {MD._md_ptet_entity_rate(2025)}")
check(approx(float(MD._yk(MD.MD_TOP_MARGINAL_INDIVIDUAL_RATE)) + float(MD._yk(MD.MD_LOWEST_COUNTY_RATE)),
             MD._md_ptet_individual_rate(2025), tol=1e-9),
      "the 8.75% is computed from its two statutory inputs, not asserted as a literal",
      "the PTET rate is not actually derived from its inputs")
check(MD._md_rate_inputs_are_stale(2026) is True and MD._md_rate_inputs_are_stale(2025) is False,
      "staleness assertion: the rate inputs are verified for TY2025 only",
      "rate staleness assertion missing or wrong")
check(float(MD._yk(MD.MD_TOP_MARGINAL_INDIVIDUAL_RATE)) == 0.0650,
      "top marginal individual rate is the TY2025 6.50% (BRFA 2025 Ch. 604), not the old 5.75%",
      "top marginal rate constant wrong")

# ---- 4d. Ownership-percentage conventions DIFFER between the forms ----
check(approx(MD._md_ownership_pct(F510, None), 1.0),
      "Form 510 convention: a BLANK ownership percentage means 100%", "510 blank convention wrong")
check(approx(MD._md_ownership_pct(F511, 9999), 1.0),
      "Form 511 convention: 9999 means 100%", "511 sentinel convention wrong")
check(approx(MD._md_ownership_pct(F511, 0.4), 0.4) and approx(MD._md_ownership_pct(F510, 0.4), 0.4),
      "a decimal percentage passes through unchanged on both forms", "decimal percentage handling wrong")
try:
    MD._md_ownership_pct(F511, None)
    FAILURES.append("Form 511 accepted a BLANK percentage -- it has no blank convention")
except ValueError:
    PASSES.append("Form 511 REJECTS a blank percentage (no blank convention exists on the 511)")
check(MD.MD_511_FULL_OWNERSHIP_SENTINEL == 9999,
      "the 511 full-ownership sentinel constant is 9999", "9999 sentinel constant wrong")

# ---- 4e. The two tax computations ----
t = MD._md_510_tax(1000000, 0.40, 0.25)
check(approx(t["L6"], 400000) and approx(t["L7"], 26000) and approx(t["L8"], 9000)
      and approx(t["L9"], 35000) and approx(t["L11"], 250000) and approx(t["L12"], 20625)
      and approx(t["L13"], 55625),
      "510: L6 400,000 -> L7 26,000 + L8 9,000 = L9 35,000; L11 250,000 -> L12 20,625; L13 55,625",
      f"510 tax computation wrong: {t}")
t = MD._md_510_tax(500000, None, 0)
check(approx(t["L6"], 500000) and approx(t["L13"], 43750),
      "510: a blank line-5 percentage takes line 4 whole (500,000 -> 43,750 total)",
      f"510 blank-percentage tax wrong: {t}")
t = MD._md_511_tax(1000000, 0.70, 0.30)
check(approx(t["L5c"], 1.0) and approx(t["L6"], 700000) and approx(t["L7"], 61250)
      and approx(t["L8"], 300000) and approx(t["L9"], 24750) and approx(t["L10"], 86000),
      "511: L6 700,000 -> L7 61,250 (8.75%); L8 300,000 -> L9 24,750 (8.25%); L10 86,000",
      f"511 tax computation wrong: {t}")
t = MD._md_511_tax(400000, 9999, 0)
check(approx(t["L5a"], 1.0) and approx(t["L7"], 35000),
      "511: the 9999 sentinel yields 100% -> 400,000 x 8.75% = 35,000", f"511 sentinel tax wrong: {t}")
# The 510 reaches the same total through TWO multipliers; the 511 through ONE.
five_ten = MD._md_510_tax(400000, None, 0)
five_eleven = MD._md_511_tax(400000, 9999, 0)
check(approx(five_ten["L7"] + five_ten["L8"], five_eleven["L7"]),
      "510 L7 + L8 equals 511 L7 on the same base -- same rate, different line structure",
      f"the two arithmetics disagree: {five_ten['L7'] + five_ten['L8']} vs {five_eleven['L7']}")
check(five_ten.get("L10") != five_eleven.get("L10"),
      "the two forms' line numbering is genuinely separate (510 L10 is a percentage, 511 L10 is the total tax)",
      "the two line maps were collapsed")

# ---- 4f. The two DCF worksheets ----
DCF_IN = dict(b=400000, c=100000, d=150000, e=50000, g=200000, h=0)
w9a = MD._md_dcf_9a(1000000, nonresident_pct=0.65, prior_nonresident_tax_paid=10000, **DCF_IN)
check(approx(w9a["F"], 700000) and approx(w9a["I"], 500000) and approx(w9a["K"], 325000)
      and approx(w9a["M"], 315000),
      "worksheet 9A: F 700,000; I 500,000; K = I x 0.65 = 325,000; M = 315,000",
      f"worksheet 9A wrong: {w9a}")
w11a = MD._md_dcf_11a(1000000, members_tax_previously_paid=10000, **DCF_IN)
check(approx(w11a["F"], 700000) and approx(w11a["I"], 500000) and approx(w11a["K"], 490000),
      "worksheet 11A: F 700,000; I 500,000; K = I - 10,000 = 490,000 (NO ownership step)",
      f"worksheet 11A wrong: {w11a}")
check(not approx(w9a["M"], w11a["K"]),
      "*** the two DCF worksheets are NOT interchangeable: 9A gives 315,000 where 11A gives 490,000 ***",
      "DCF BREACH: the two worksheets produced the same limitation on identical inputs")
check("J" in w9a and approx(w9a["J"], 0.65),
      "9A line J is the NONRESIDENT OWNERSHIP PERCENTAGE", f"9A line J wrong: {w9a.get('J')}")
check(approx(w11a["J"], 10000),
      "11A line J is MEMBERS' TAX PREVIOUSLY PAID -- same letter, different meaning",
      f"11A line J wrong: {w11a.get('J')}")
check(MD._yk(MD.MD_DCF_9A_HAS_OWNERSHIP_STEP) is True and MD._yk(MD.MD_DCF_11A_HAS_OWNERSHIP_STEP) is False,
      "the ownership-step constants record 9A=True / 11A=False", "DCF ownership-step constants wrong")
check(MD._yk(MD.MD_DCF_F_INCLUDES_LINE_A) is False,
      "W5(a): worksheet line F is encoded verbatim as 'Add lines B through E' (line A excluded) pending Ken's confirmation",
      "the line-F transcription constant was changed without a ruling")
check(approx(MD._md_dcf_11a(1000000, members_tax_previously_paid=9999999, **DCF_IN)["K"], 0.0),
      "11A line K floors at zero ('If less than 0, enter 0')", "11A zero floor wrong")
check(approx(MD._md_dcf_9a(1000000, nonresident_pct=0.65, prior_nonresident_tax_paid=9999999, **DCF_IN)["M"], 0.0),
      "9A line M floors at zero ('If less than 0, enter 0')", "9A zero floor wrong")
# The CONDITIONAL lesser-of.
check(approx(MD._md_tax_due_after_dcf(55625, None, dcf_worksheet_used=False), 55625),
      "510 L15 / 511 L12 = the full tax when the DCF worksheet is NOT used (an unconditional MIN() would give 0)",
      "CONDITIONAL LESSER-OF BREACH: a blank DCF line zeroed the tax")
check(approx(MD._md_tax_due_after_dcf(55625, 40000, dcf_worksheet_used=True), 40000),
      "with the worksheet used, the lesser of the tax and the DCF limitation applies (40,000)",
      "DCF lesser-of wrong when the worksheet is used")
check(approx(MD._md_tax_due_after_dcf(55625, 90000, dcf_worksheet_used=True), 55625),
      "with the worksheet used and a higher limitation, the tax itself stands (55,625)",
      "DCF lesser-of wrong when the limitation exceeds the tax")
check(approx(MD._md_tax_due_after_dcf(86000, 0, dcf_worksheet_used=False), 86000),
      "a zero DCF limitation with the box UNCHECKED still leaves the full tax standing",
      "CONDITIONAL LESSER-OF BREACH: a zero limitation leaked through an unchecked box")
check(MD._yk(MD.MD_DCF_AMENDED_RETURN_BAR_SOURCED) is False,
      "U7: the 'cannot be elected on an amended return' bar is UNSOURCED and is not encoded as a rule",
      "an unsourced amended-return bar was encoded")

# ---- 4g. Owner side: credit PLUS add-back, D2/D4 only ----
o = MD._md_owner_side(k1_d1=12000)
check(approx(o["D5_credit_total"], 12000) and approx(o["addback"], 0.0),
      "510 leg (D1 only): credit 12,000 and add-back 0 -- D1 is NEVER added back",
      f"D1-only owner side wrong: {o}")
o = MD._md_owner_side(k1_d2=61250, k1_d4=5000)
check(approx(o["D5_credit_total"], 66250) and approx(o["addback"], 66250),
      "511 legs (D2 + D4): credit 66,250 AND add-back 66,250 -- both legs required",
      f"D2/D4 owner side wrong: {o}")
o = MD._md_owner_side(k1_d1=12000, k1_d2=61250, k1_d4=5000)
check(approx(o["D5_credit_total"], 78250) and approx(o["addback"], 66250),
      "*** mixed K-1: credit 78,250 but add-back only 66,250 -- D1 excluded (adding it back double-taxes) ***",
      f"MIXED-K1 BREACH: {o}")
check(o["addback_sources"] == ["D2", "D4"] and o["d1_in_addback"] is False,
      "the add-back is declared to attach to D2 and D4 only", f"add-back source declaration wrong: {o}")
check(o["section_b_preloaded"] is False,
      "the add-back is NOT pre-loaded into K-1 Section B additions (per the Section B instruction)",
      "the add-back leaked into K-1 Section B")
check("code 'r'" in o["individual_addback_route"] or "code 'r'" in o["individual_addback_route"].lower(),
      "the individual add-back route is recorded (Form 502 Other Additions code 'r')",
      f"individual add-back route missing: {o['individual_addback_route']}")

# ---- 4h. Apportionment: the .000001 floor, six decimals, and THE NEGATIVE ----
check(approx(MD._md_apportionment_factor(200000, 1000000), 0.2, tol=1e-9),
      "apportionment: 200,000 / 1,000,000 = 0.200000", "basic factor wrong")
check(approx(MD._md_apportionment_factor(1, 3), 0.333333, tol=1e-9),
      "the factor is rounded to SIX decimal places (1/3 -> 0.333333)", "six-decimal rounding wrong")
check(approx(MD._md_apportionment_factor(0, 5000000), 0.000001, tol=1e-12),
      "a ZERO factor is entered as .000001 -- never dropped", "zero-factor floor wrong")
check(approx(MD._md_apportionment_factor(1, 10 ** 9), 0.000001, tol=1e-12),
      "a factor that rounds to zero at six places also floors at .000001", "rounds-to-zero floor wrong")
check(approx(MD._md_apportionment_factor(500000, 0), 0.000001, tol=1e-12),
      "a ZERO DENOMINATOR still yields a factor (COMAR 03.04.03.08 B(5): a factor must exist even on a loss return)",
      "zero-denominator case dropped the factor instead of flooring it")
check(MD._md_apportionment_factor(500000, 0) is not None,
      "a zero denominator NEVER returns None / eliminates the factor (that is the Florida behaviour)",
      "NEGATIVE BREACH: a zero denominator eliminated the factor")
check(MD._yk(MD.MD_APPORT_DECIMALS) == 6 and float(MD._yk(MD.MD_APPORT_ZERO_FLOOR)) == 0.000001,
      "apportionment constants: six decimals, .000001 zero floor", "apportionment constants wrong")
# *** THE LOAD-BEARING NEGATIVE ***
check(MD._yk(MD.MD_INSIGNIFICANT_DENOMINATOR_RULE) is False,
      "*** MD_INSIGNIFICANT_DENOMINATOR_RULE is False -- Maryland has NO such rule (it is Fla. Stat. 220.15(1)) ***",
      "NEGATIVE BREACH: an insignificant-denominator rule was asserted of Maryland")
base = MD._md_final_apportionment_factor(0.2)
zeroed = MD._md_final_apportionment_factor(0.2, property_factor=0.0, payroll_factor=0.0)
tiny = MD._md_final_apportionment_factor(0.2, property_factor=0.000001, payroll_factor=0.000001)
check(approx(base, 0.2, tol=1e-12) and approx(zeroed, 0.2, tol=1e-12) and approx(tiny, 0.2, tol=1e-12),
      "*** NO REWEIGHTING: zero or tiny property/payroll denominators leave the receipts factor at 0.200000 ***",
      f"REWEIGHT BREACH: base={base} zeroed={zeroed} tiny={tiny}")
check(not approx(zeroed, 0.233333) and not approx(zeroed, 0.25) and not approx(zeroed, 0.3),
      "*** the zero-denominator result is NOT any Florida 33-1/3 / 50-50 / 100% reweight ***",
      f"REWEIGHT BREACH: the Florida reweighting leaked in -> {zeroed}")
_saved = MD.MD_INSIGNIFICANT_DENOMINATOR_RULE.get(2025)
MD.MD_INSIGNIFICANT_DENOMINATOR_RULE[2025] = True
try:
    MD._md_final_apportionment_factor(0.2)
    FAILURES.append("NEGATIVE BREACH: flipping MD_INSIGNIFICANT_DENOMINATOR_RULE True did NOT trip the guard")
except AssertionError as exc:
    check("Fla" in str(exc) or "Florida" in str(exc) or "insignificant" in str(exc),
          "the insignificance constant is a live GUARD (flipping it True raises, naming Florida as the real source)",
          f"the guard raised the wrong error: {exc!r}")
finally:
    MD.MD_INSIGNIFICANT_DENOMINATOR_RULE[2025] = _saved
# No reweighting machinery may exist in the module at all.
reweight_names = [n for n in dir(MD) if "reweight" in n.lower() or "insignif" in n.lower()
                  and n != "MD_INSIGNIFICANT_DENOMINATOR_RULE"]
check(not [n for n in reweight_names if callable(getattr(MD, n, None))],
      "no reweighting FUNCTION exists in the module (only the negative constant and its guard)",
      f"reweighting machinery present: {reweight_names}")
fl_weight_constants = [n for n in dir(MD) if isinstance(getattr(MD, n, None), dict)
                       and set(getattr(MD, n)) == {"property", "payroll", "sales"}]
check(not fl_weight_constants,
      "no property/payroll/sales weight table exists (TY2025 Maryland is a SINGLE receipts factor)",
      f"a Florida-style weight table leaked in: {fl_weight_constants}")
check(MD._md_may_alter_formula("Comptroller") is True
      and MD._md_may_alter_formula("preparer") is False
      and MD._md_may_alter_formula("software") is False,
      "only the COMPTROLLER may alter a formula (10-402(e); 10-401(2)) -- never the preparer or the software",
      "formula-alteration authority wrong")
check(MD._yk(MD.MD_SINGLE_RECEIPTS_FACTOR) is True,
      "TY2025 uses a single receipts factor (tax years beginning after 12/31/2021)",
      "single-receipts-factor constant wrong")
check(approx(MD._md_final_apportionment_factor(0.2, special_or_alternative=0.375), 0.375),
      "a Comptroller-accepted special/alternative factor is ENTERED, not derived",
      "special/alternative factor handling wrong")

# ---- 4i. Downstream mechanics ----
check(approx(MD._md_k1_section_h_column2(500000, 0.2), 100000),
      "K-1 Section H column 2 = column 1 x the Maryland apportionment factor (500,000 x 0.2)",
      "Section H column 2 wrong")
check(approx(MD._md_schedule_b_share_base(850000, 170000), 850000),
      "Schedule B per-member shares run off LINE 2 (850,000), not the apportioned line 4",
      "Schedule B base wired off the wrong line")
check(MD._md_scorp_also_files_form_500(18000, 0) is True
      and MD._md_scorp_also_files_form_500(0, 4200) is True
      and MD._md_scorp_also_files_form_500(0, 0) is False
      and MD._md_scorp_also_files_form_500(None, None) is False,
      "R6/W10: 1120-S line 23a or 23b > 0 triggers a Maryland Form 500 in ADDITION to Form 510/511",
      "the S-corp dual-filing trigger is wrong")

# ---- 4j. Constants that must NOT be someone else's ----
check(MD._yk(MD.MD_179_LIMIT) == 25000 and MD._yk(MD.MD_179_PHASEOUT) == 200000,
      "Maryland Sec.179 is frozen at $25,000 / $200,000 (10-210.1(b)(3)(i))", "MD Sec.179 figures wrong")
check(MD._yk(MD.MD_179_LIMIT) != 2500000 and MD._yk(MD.MD_179_PHASEOUT) != 4000000,
      "the federal OBBBA $2,500,000 / $4,000,000 Sec.179 figures did NOT leak into Maryland",
      "OBBBA Sec.179 figures leaked into the Maryland spec")
check(MD._yk(MD.MD_PTE_COMPUTES_500DM) is False,
      "the PTE computes NOTHING on Form 500DM -- it attaches it and passes shares through the K-1",
      "the PTE was made to compute 500DM")
check(MD.MD_MFG_NAICS_EDITION == "2012" and MD.MD_MFG_NAICS_SECTORS == ("31", "32", "33"),
      "the 10-210.1 manufacturing carve-out uses NAICS 2012 Edition, Sectors 31/32/33",
      "manufacturing carve-out constants wrong")
check(MD.MD_Q8_IS_DEPRECIATION_CARVEOUT is False,
      "page-3 Q8 is explicitly DISCONNECTED from the depreciation carve-out (different NAICS edition and sectors)",
      "Q8 was wired to the depreciation carve-out")
check(set(MD.MD_KNOWN_CODE_NUMBERS) == {"704", "705", "301"},
      "only the three verified code numbers (704 / 705 / 301) are offered (U12)", "code-number list wrong")
check(MD._yk(MD.MD_ESTIMATED_THRESHOLD) == 1000 and MD._yk(MD.MD_ESTIMATED_SAFE_HARBOR) == (0.90, 1.10),
      "estimated tax: $1,000 threshold, 90% / 110% safe harbour", "estimated-tax constants wrong")
check(MD._yk(MD.MD_ESTIMATED_MONTHS_SCORP) == (4, 6, 9, 12)
      and MD._yk(MD.MD_ESTIMATED_MONTHS_OTHER) == (4, 6, 9, 13),
      "two DIFFERENT installment calendars: 4/6/9/12 for S corps, 4/6/9/13 for other PTEs",
      "installment calendars wrong")
check(MD._yk(MD.MD_EXTENSION_MONTHS) == {"1120S": 7, "other": 6},
      "extension is 7 months for S corporations and 6 months for other PTEs", "extension lengths wrong")


# ══════════════════════════════════════════════════════════════════════
# 5. Required diagnostics -- every RED-defer and every walk-item block.
# ══════════════════════════════════════════════════════════════════════
REQUIRED_DIAG = {
    F510: [
        "D_MD510_ELECTION_UNDETERMINED", "D_MD510_WRONG_FORM_FILE_511", "D_MD510_DEEMED_NEITHER_BOX",
        "D_MD510_DEEMED_BOTH_BOXES", "D_MD510_AMENDED_ELECTION_BAR", "D_MD510_RESIDENT_ENTITY_1D",
        "D_MD510_FIDUCIARY_IN_IND_LEG", "D_MD510_EXEMPT_MEMBER_U6", "D_MD510_APPORT_ZERO_FLOOR",
        "D_MD510_NO_FACTOR_REWEIGHT", "D_MD510_DCF_CONDITIONAL", "D_MD510_DCF_OWNERSHIP_STEP",
        "D_MD510_DCF_AMENDED_U7", "D_MD510_GATE_ERRATUM_U4", "D_MD510_AMEND_LINE_ERRATUM_U5",
        "D_MD510_K1_D4_ERRATUM_U3", "D_MD510_TB38_ERRATUM_U10", "D_MD510_SCHB_OFF_LINE2",
        "D_MD510_EFILE_MANDATE", "D_MD510_Q8_NOT_MFG_CARVEOUT", "D_MD510_CODE_NUMBERS_U12",
        "D_MD510_RESIDENT_ESTIMATE_REFUND", "D_MD510_K1H_NO_TAX_LINE", "D_MD510_K1H_408_ERRATUM",
        "D_MD510_R1_COMPOSITE_510C", "D_MD510_R2_SPECIAL_APPORT", "D_MD510_R3_ALTERNATIVE_APPORT",
        "D_MD510_R4_500CR_502S", "D_MD510_R5_ONE_MARYLAND", "D_MD510_R6_SCORP_FORM_500",
        "D_MD510_R7_FORM_500UP", "D_MD510_R8_MW506NRS", "D_MD510_R9_FORM_500DM",
        "D_MD510_R10_MFG_CARVEOUT", "D_MD510_R11_TIERED_PTE", "D_MD510_R12_PTP_CODE_704",
        "D_MD510_R13_INVEST_PTNSHP_705", "D_MD510_R14_EL102B", "D_MD510_R15_501_PTE_FTI",
    ],
    F511: [
        "D_MD511_ELECTION_UNDETERMINED", "D_MD511_WRONG_FORM_FILE_510", "D_MD511_DEEMED_BOTH_BOXES",
        "D_MD511_YEAR_END_IS_ELECTION", "D_MD511_AMENDED_ELECTION_BAR", "D_MD511_RESIDENT_ENTITY_1C",
        "D_MD511_RESIDENT_INDIVIDUAL_TAXED", "D_MD511_FIDUCIARY_IN_IND_LEG", "D_MD511_EXEMPT_MEMBER_U6",
        "D_MD511_SALT_ADDBACK_REQUIRED", "D_MD511_PRIOR_REFUND_ADJUST", "D_MD511_TY2027_BASE_CHANGE",
        "D_MD511_APPORT_ZERO_FLOOR", "D_MD511_NO_FACTOR_REWEIGHT", "D_MD511_DCF_CONDITIONAL",
        "D_MD511_DCF_NO_OWNERSHIP_STEP", "D_MD511_DCF_AMENDED_U7", "D_MD511_ADDBACK_D2_D4_ONLY",
        "D_MD511_ADDBACK_NOT_IN_SEC_B", "D_MD511_NO_COMPOSITE_510C", "D_MD511_INVEST_PTNSHP_ERRATUM",
        "D_MD511_AMEND_LINE_ERRATUM_U5", "D_MD511_TB38_ERRATUM_U10", "D_MD511_PCT_9999_CONVENTION",
        "D_MD511_SCHB_OFF_LINE2", "D_MD511_EFILE_MANDATE", "D_MD511_Q8_NOT_MFG_CARVEOUT",
        "D_MD511_CODE_NUMBERS_U12", "D_MD511_K1H_NO_TAX_LINE", "D_MD511_K1H_408_ERRATUM",
        "D_MD511_R2_SPECIAL_APPORT", "D_MD511_R3_ALTERNATIVE_APPORT", "D_MD511_R4_500CR_502S",
        "D_MD511_R5_ONE_MARYLAND", "D_MD511_R6_SCORP_FORM_500", "D_MD511_R7_FORM_500UP",
        "D_MD511_R8_MW506NRS", "D_MD511_R9_FORM_500DM", "D_MD511_R10_MFG_CARVEOUT",
        "D_MD511_R11_TIERED_PTE", "D_MD511_R12_PTP_SHOULD_NOT_FILE", "D_MD511_R15_501_PTE_FTI",
    ],
}
for fn, dids in REQUIRED_DIAG.items():
    form = TaxForm.objects.get(form_number=fn)
    missing = [d for d in dids if not FormDiagnostic.objects.filter(tax_form=form, diagnostic_id=d).exists()]
    check(not missing, f"{fn}: all {len(dids)} required diagnostics present", f"{fn}: MISSING diagnostics {missing}")

present = set(all_diag)
RED_MAP = {
    "R1": ["D_MD510_R1_COMPOSITE_510C"],
    "R2": ["D_MD510_R2_SPECIAL_APPORT", "D_MD511_R2_SPECIAL_APPORT"],
    "R3": ["D_MD510_R3_ALTERNATIVE_APPORT", "D_MD511_R3_ALTERNATIVE_APPORT"],
    "R4": ["D_MD510_R4_500CR_502S", "D_MD511_R4_500CR_502S"],
    "R5": ["D_MD510_R5_ONE_MARYLAND", "D_MD511_R5_ONE_MARYLAND"],
    "R6": ["D_MD510_R6_SCORP_FORM_500", "D_MD511_R6_SCORP_FORM_500"],
    "R7": ["D_MD510_R7_FORM_500UP", "D_MD511_R7_FORM_500UP"],
    "R8": ["D_MD510_R8_MW506NRS", "D_MD511_R8_MW506NRS"],
    "R9": ["D_MD510_R9_FORM_500DM", "D_MD511_R9_FORM_500DM"],
    "R10": ["D_MD510_R10_MFG_CARVEOUT", "D_MD511_R10_MFG_CARVEOUT"],
    "R11": ["D_MD510_R11_TIERED_PTE", "D_MD511_R11_TIERED_PTE"],
    "R12": ["D_MD510_R12_PTP_CODE_704", "D_MD511_R12_PTP_SHOULD_NOT_FILE"],
    "R13": ["D_MD510_R13_INVEST_PTNSHP_705"],
    "R14": ["D_MD510_R14_EL102B"],
    "R15": ["D_MD510_R15_501_PTE_FTI", "D_MD511_R15_501_PTE_FTI"],
}
missing_red = [r for r, ids in RED_MAP.items() if not any(i in present for i in ids)]
check(not missing_red, "all 15 RED-defers R1-R15 have their own diagnostic",
      f"RED-defers with no diagnostic: {missing_red}")

# The hard blocks must be severity 'error'.
HARD_BLOCKS = [
    (F510, "D_MD510_ELECTION_UNDETERMINED"), (F510, "D_MD510_WRONG_FORM_FILE_511"),
    (F510, "D_MD510_DEEMED_BOTH_BOXES"), (F510, "D_MD510_AMENDED_ELECTION_BAR"),
    (F510, "D_MD510_NO_FACTOR_REWEIGHT"), (F510, "D_MD510_R10_MFG_CARVEOUT"),
    (F511, "D_MD511_ELECTION_UNDETERMINED"), (F511, "D_MD511_WRONG_FORM_FILE_510"),
    (F511, "D_MD511_AMENDED_ELECTION_BAR"), (F511, "D_MD511_NO_FACTOR_REWEIGHT"),
    (F511, "D_MD511_ADDBACK_D2_D4_ONLY"), (F511, "D_MD511_NO_COMPOSITE_510C"),
    (F511, "D_MD511_R10_MFG_CARVEOUT"),
]
bad_sev = []
for fn, did in HARD_BLOCKS:
    d = FormDiagnostic.objects.filter(tax_form__form_number=fn, diagnostic_id=did).first()
    if d is None or d.severity != "error":
        bad_sev.append(f"{did}={getattr(d, 'severity', 'MISSING')}")
check(not bad_sev, f"all {len(HARD_BLOCKS)} hard blocks are severity 'error'",
      f"hard blocks with the wrong severity: {bad_sev}")

# The R10 wording must actually carry the statutory detail and the 'no printed line' warning.
for fn, did in ((F510, "D_MD510_R10_MFG_CARVEOUT"), (F511, "D_MD511_R10_MFG_CARVEOUT")):
    d = FormDiagnostic.objects.get(tax_form__form_number=fn, diagnostic_id=did)
    ok = ("2012" in d.message and "31, 32 or 33" in d.message
          and "NO TY2025 MARYLAND PTE FORM" in d.message.upper()
          and "280F" in d.message)
    check(ok, f"{fn}: the R10 carve-out wording carries NAICS 2012 / sectors 31-33 / 'no printed line' / the 280F limit",
          f"{fn}: R10 wording is missing required detail")


# ══════════════════════════════════════════════════════════════════════
# 6. Structural spot checks on the two encoded line maps.
# ══════════════════════════════════════════════════════════════════════
f510 = TaxForm.objects.get(form_number=F510)
f511 = TaxForm.objects.get(form_number=F511)

check(FormLine.objects.filter(tax_form=f510, line_number__startswith="16").count() == 8,
      "Form 510 has all EIGHT payment lines 16a-16h", "Form 510 payment-line count wrong")
check(FormLine.objects.filter(tax_form=f511, line_number__startswith="13").count() == 6,
      "Form 511 has all SIX payment lines 13a-13f (five inputs + the total)", "Form 511 payment-line count wrong")
check(FormLine.objects.filter(tax_form=f510, line_number="16e").exists()
      and not FormLine.objects.filter(tax_form=f511, line_number="16e").exists(),
      "the 16d/16e resident-vs-nonresident credit split exists ONLY on Form 510",
      "the 510-only credit split leaked onto the 511")
check(FormLine.objects.filter(tax_form=f510, line_number__startswith="W9A-").count() == 13,
      "worksheet 9A has all THIRTEEN lines A-M", "worksheet 9A line count wrong")
check(FormLine.objects.filter(tax_form=f511, line_number__startswith="W11A-").count() == 11,
      "worksheet 11A has all ELEVEN lines A-K", "worksheet 11A line count wrong")
check(not FormLine.objects.filter(tax_form=f511, line_number__startswith="W9A-").exists()
      and not FormLine.objects.filter(tax_form=f510, line_number__startswith="W11A-").exists(),
      "the two DCF worksheets are encoded SEPARATELY, one per form", "the DCF worksheets were shared between forms")
for fn, form in ((F510, f510), (F511, f511)):
    check(FormLine.objects.filter(tax_form=form, line_number__startswith="SchA-").count() == 19,
          f"{fn}: Schedule A has all 19 lines (1a-1h, 2a-2g, 3a-3c, 4)", f"{fn}: Schedule A line count wrong")
l1c_510 = FormLine.objects.get(tax_form=f510, line_number="1c")
l1c_511 = FormLine.objects.get(tax_form=f511, line_number="1c")
check("Nonresident entities" in l1c_510.description and "RESIDENT entities" in l1c_511.description,
      "line 1c reads 'Nonresident entities' on the 510 and 'Nonresident AND RESIDENT entities' on the 511",
      f"line 1c scope wrong: 510={l1c_510.description[:60]!r} 511={l1c_511.description[:60]!r}")
l7_510 = FormLine.objects.get(tax_form=f510, line_number="7")
l7_511 = FormLine.objects.get(tax_form=f511, line_number="7")
check("6.50%" in l7_510.description and "8.75%" in l7_511.description,
      "line 7 is 'Multiply line 6 by 6.50%' on the 510 and 'by 8.75%' on the 511 -- separate line maps",
      "the two line-7 rate labels are wrong")
check("2.25%" in FormLine.objects.get(tax_form=f510, line_number="8").description,
      "Form 510 line 8 carries the verbatim 2.25% special nonresident tax", "Form 510 line 8 label wrong")
check(FormFact.objects.filter(tax_form=f510, fact_key="count_1c_nonresident_entities").exists()
      and FormFact.objects.filter(tax_form=f511, fact_key="count_1c_nonres_and_res_entities").exists()
      and not FormFact.objects.filter(tax_form=f511, fact_key="count_1c_nonresident_entities").exists(),
      "the line-1c fact KEYS encode the scope divergence (510 nonresident-only vs 511 nonresident-and-resident)",
      "the two forms share a single line-1c fact key, hiding the scope divergence")
check(FormFact.objects.filter(tax_form=f511, fact_key="salt_deduction_1065_l14_or_1120s_l12").exists()
      and not FormFact.objects.filter(tax_form=f510, fact_key="salt_deduction_1065_l14_or_1120s_l12").exists(),
      "the SALT add-back input exists ONLY on Form 511 (Form 510 line 2 has no add-back)",
      "the SALT add-back leaked onto Form 510")
check(FormFact.objects.filter(tax_form=f511, fact_key="prior_year_md_refund_in_federal_income").exists(),
      "the prior-year Maryland refund adjustment is an explicit Form 511 input (multi-year state)",
      "the prior-year refund adjustment is missing")
check(FormFact.objects.filter(tax_form=f510, fact_key="election_first_filing_kind", required=True).exists()
      and FormFact.objects.filter(tax_form=f511, fact_key="election_first_filing_kind", required=True).exists(),
      "the election first-filing fact is REQUIRED on both forms (it is never inferred)",
      "the election first-filing fact is missing or optional")
check(FormFact.objects.filter(tax_form=f510, fact_key="naics_31_33_manufacturing_entity").exists()
      and FormFact.objects.filter(tax_form=f511, fact_key="naics_31_33_manufacturing_entity").exists(),
      "the manufacturing-entity attribute exists as a spec-level fact on both forms (no form line captures it)",
      "the manufacturing-entity attribute is missing")
check(FormFact.objects.filter(tax_form=f510, fact_key="box_510c_filed").exists()
      and not FormFact.objects.filter(tax_form=f511, fact_key="box_510c_filed").exists(),
      "the '510C Filed' checkbox exists only on Form 510 (there is none on Form 511)",
      "a 510C checkbox leaked onto Form 511")
check(FlowAssertion.objects.filter(assertion_id="FA-MD-NO-REWEIGHT").exists()
      and FlowAssertion.objects.filter(assertion_id="FA-MD-D1-NO-ADDBK").exists()
      and FlowAssertion.objects.filter(assertion_id="FA-MD-MEMBER-BOX").exists()
      and FlowAssertion.objects.filter(assertion_id="FA-MD-DCF-SPLIT").exists(),
      "the four load-bearing flow assertions are present (no-reweight, D1-no-addback, member-box, DCF-split)",
      "a load-bearing flow assertion is missing")
fa_nore = FlowAssertion.objects.get(assertion_id="FA-MD-NO-REWEIGHT")
check("220.15" in fa_nore.bug_reference or "Florida" in fa_nore.bug_reference,
      "FA-MD-NO-REWEIGHT records the wave-premise error it exists to catch (the Florida rule)",
      "FA-MD-NO-REWEIGHT has no bug_reference naming the Florida contamination")

# The withdrawn walk item must be recorded as withdrawn, and must NOT be encoded as a live conflict.
check("W3 IS WITHDRAWN" in MD.__doc__.upper(),
      "the module docstring records that W3 was WITHDRAWN, and why (the 2025 BRFA vintage error)",
      "the docstring does not record the W3 withdrawal")
live_w3 = [d["diagnostic_id"] for s in MD.FORMS for d in s["diagnostics"]
           if "W3" in (d.get("notes") or "") and "WITHDRAWN" not in (d.get("notes") or "").upper()]
check(not live_w3, "no diagnostic encodes the WITHDRAWN W3 as a live conflict", f"W3 re-raised by: {live_w3}")


# ══════════════════════════════════════════════════════════════════════
# 7. Report
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
for fn in FORM_SHAPE:
    form = TaxForm.objects.get(form_number=fn)
    print(f"  {fn}: facts {FormFact.objects.filter(tax_form=form).count()} / "
          f"rules {FormRule.objects.filter(tax_form=form).count()} / "
          f"lines {FormLine.objects.filter(tax_form=form).count()} / "
          f"diag {FormDiagnostic.objects.filter(tax_form=form).count()} / "
          f"tests {form.test_scenarios.count()}")
print(f"  flow assertions: {FlowAssertion.objects.filter(assertion_id__startswith='FA-MD').count()}")
print(f"  authority sources (MD, new this loader): {AuthoritySource.objects.filter(jurisdiction_code='MD').count()}")
print(f"  rule authority links: {RuleAuthorityLink.objects.count()}")
print("=" * 72)
for p in PASSES:
    print(f"  PASS  {p}")
for f in FAILURES:
    print(f"  FAIL  {f}")
print("=" * 72)
print(f"RESULT: {len(PASSES)} pass / {len(FAILURES)} fail - "
      f"{'ALL PASS' if not FAILURES else 'FAILURES PRESENT'}")
print(f"NOTE: READY_TO_SEED flipped IN MEMORY ONLY; on disk it ships {_shipped_ready}.")

from django.db import connections  # noqa: E402
connections.close_all()
try:
    if os.path.exists(SQLITE_PATH):
        os.remove(SQLITE_PATH)
except OSError:
    pass
sys.exit(1 if FAILURES else 0)
