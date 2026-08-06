"""Tests for the state conformity spine (JurisdictionConformitySource).

Authored 2026-08-05 for the 45-state campaign Phase 2 (Tax Shelter Future D-030).

What these pin:
  1. The (jurisdiction_code, tax_year) unique constraint — one row per state-year.
  2. `_build_export` attaches the row as `state_conformity` for state forms, and never
     500s when the row is absent (it was a bare .get() before).
  3. The loader's canonical `decoupled_items` shape and its seed guard.
  4. Every source_type used by a shipped loader is a real SourceType choice — the
     class of defect that let "state_guidance" persist silently in load_ga700.
"""
import ast
import collections
import pathlib

import pytest
from django.db import IntegrityError, transaction
from django.test import Client

from sources.models import AuthoritySource, JurisdictionConformitySource, SourceType
from specs.models import TaxForm

COMMANDS_DIR = pathlib.Path(__file__).resolve().parent.parent / "specs" / "management" / "commands"


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def sc_form():
    return TaxForm.objects.create(
        jurisdiction="SC",
        form_number="SC1040",
        form_title="South Carolina Individual Income Tax Return",
        entity_types=["1040"],
        tax_year=2025,
        version=1,
        status="draft",
    )


@pytest.fixture
def sc_conformity():
    return JurisdictionConformitySource.objects.create(
        jurisdiction_code="SC",
        tax_year=2025,
        conformity_type="static",
        federal_reference_note="IRC as amended through December 31, 2024 (Act 63 of 2025).",
        summary="South Carolina is a static-date conformity state; OBBBA not adopted for TY2025.",
        decoupled_items=[
            {
                "item": "IRC §168(k) bonus depreciation",
                "federal_treatment": "100% bonus (OBBBA).",
                "state_treatment": "Not adopted — add back.",
                "authority_source_code": "SC_ACT63_2025_CONFORMITY",
                "notes": "Computed on SC1040 line e.",
            },
        ],
        notes="PTET is a 3% ATB election with an owner-side exclusion — not a GA clone.",
    )


# ── 1. the unique constraint ────────────────────────────────────────────────


@pytest.mark.django_db
def test_one_conformity_row_per_state_year(sc_conformity):
    """A second row for the same (state, year) must be refused.

    Before the constraint, a duplicate made the export's .get() raise
    MultipleObjectsReturned — a 500 on an endpoint serving spec packages.
    """
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            JurisdictionConformitySource.objects.create(
                jurisdiction_code="SC", tax_year=2025, conformity_type="rolling",
            )


@pytest.mark.django_db
def test_same_state_different_years_allowed(sc_conformity):
    """Conformity is TY-keyed — the same state must be able to hold a row per year."""
    JurisdictionConformitySource.objects.create(
        jurisdiction_code="SC", tax_year=2026, conformity_type="static",
    )
    assert JurisdictionConformitySource.objects.filter(jurisdiction_code="SC").count() == 2


# ── 2. the export block ─────────────────────────────────────────────────────


@pytest.mark.django_db
def test_export_attaches_state_conformity(client, sc_form, sc_conformity):
    """A state form's package carries the shared conformity row.

    This is the gap Phase 2 closed: SC/AL/NC exported "state_conformity": null while
    only GA had a row.
    """
    resp = client.get("/api/forms/lookup/SC1040/export/")
    assert resp.status_code == 200

    conf = resp.json()["state_conformity"]
    assert conf is not None, "state form export must carry its conformity row"
    assert conf["jurisdiction_code"] == "SC"
    assert conf["tax_year"] == 2025
    assert conf["conformity_type"] == "static"
    assert len(conf["decoupled_items"]) == 1


@pytest.mark.django_db
def test_export_survives_missing_conformity_row(client, sc_form):
    """No row is a legitimate state (not yet authored) — null, never a 500."""
    resp = client.get("/api/forms/lookup/SC1040/export/")
    assert resp.status_code == 200
    assert resp.json()["state_conformity"] is None


@pytest.mark.django_db
def test_federal_form_has_no_conformity_block(client):
    """Federal forms carry null regardless of what state rows exist.

    Both spellings of the federal jurisdiction are in use in this DB ("federal" and
    "FED"), and neither should attempt a state lookup.
    """
    for jurisdiction, number in (("federal", "4797"), ("FED", "8825")):
        TaxForm.objects.create(
            jurisdiction=jurisdiction, form_number=number, form_title="Federal form",
            entity_types=["1065"], tax_year=2025, version=1, status="draft",
        )
        resp = client.get(f"/api/forms/lookup/{number}/export/")
        assert resp.status_code == 200
        assert resp.json()["state_conformity"] is None, f"{jurisdiction} must not resolve a state row"


# ── 3. the loader ───────────────────────────────────────────────────────────


@pytest.mark.django_db
def test_conformity_loader_guard_refuses_when_unflipped(monkeypatch):
    """The seed guard must REFUSE and write nothing while it is unflipped.

    This pins the guard MECHANISM, not the current value of the sentinel: the sentinel
    ships False and is flipped in-session once Ken approves the Gate-1 walk (here,
    2026-08-05, WO-CONF-SPINE), so asserting `is False` would make this test go red the
    moment the loader was legitimately approved — a permanently-red test nobody reads.
    """
    from django.core.management import call_command
    from django.core.management.base import CommandError

    from specs.management.commands import load_state_conformity

    monkeypatch.setattr(load_state_conformity, "READY_TO_SEED", False)

    with pytest.raises(CommandError, match="READY_TO_SEED"):
        call_command("load_state_conformity")

    assert JurisdictionConformitySource.objects.count() == 0, "the guard must write nothing"


@pytest.mark.django_db
def test_conformity_dry_run_bypasses_guard_without_writing(monkeypatch):
    """--dry-run inspects the planned rows even while gated, and still writes nothing."""
    from django.core.management import call_command

    from specs.management.commands import load_state_conformity

    monkeypatch.setattr(load_state_conformity, "READY_TO_SEED", False)
    call_command("load_state_conformity", "--dry-run")

    assert JurisdictionConformitySource.objects.count() == 0


def test_conformity_rows_use_canonical_decoupled_shape():
    """Every decoupled item carries the 5-key shape (campaign D-8).

    The model documented {item, federal_treatment, state_treatment, authority_source_*, notes}
    while the only real row used a 2-key {item, treatment}. delvio-tax's state-registry
    refactor consumes this shape, so drift here breaks a downstream contract.
    """
    from specs.management.commands.load_state_conformity import CONFORMITY_ROWS

    required = {"item", "federal_treatment", "state_treatment", "authority_source_code", "notes"}
    valid_types = {c for c, _ in __import__(
        "sources.models", fromlist=["ConformityType"]).ConformityType.choices}

    seen_states = set()
    for row in CONFORMITY_ROWS:
        state = row["jurisdiction_code"]
        assert state not in seen_states, f"{state} appears twice — one row per state-year"
        seen_states.add(state)

        assert row["conformity_type"] in valid_types, (
            f"{state}: {row['conformity_type']} is not a ConformityType choice"
        )
        assert row["summary"], f"{state}: summary is the human-readable posture — required"

        for item in row["decoupled_items"]:
            missing = required - set(item)
            assert not missing, f"{state} decoupled item {item.get('item')!r} missing {missing}"


def test_conformity_covers_every_built_state():
    """The four states with seeded specs must all have a conformity row.

    Guards the regression Phase 2 fixed — three of four states exporting null.
    """
    from specs.management.commands.load_state_conformity import CONFORMITY_ROWS

    assert {r["jurisdiction_code"] for r in CONFORMITY_ROWS} >= {"GA", "SC", "AL", "NC"}


@pytest.mark.django_db
def test_conformity_loader_seeds_and_is_idempotent(monkeypatch):
    """With the guard flipped the loader writes one row per state and re-runs clean."""
    from django.core.management import call_command

    from specs.management.commands import load_state_conformity

    monkeypatch.setattr(load_state_conformity, "READY_TO_SEED", True)

    call_command("load_state_conformity")
    first = JurisdictionConformitySource.objects.count()
    assert first == len(load_state_conformity.CONFORMITY_ROWS)

    call_command("load_state_conformity")
    assert JurisdictionConformitySource.objects.count() == first, "re-run must not duplicate"

    sc = JurisdictionConformitySource.objects.get(jurisdiction_code="SC", tax_year=2025)
    assert sc.conformity_type == "static"
    assert any("168(k)" in i["item"] for i in sc.decoupled_items)


@pytest.mark.django_db
def test_conformity_loader_anchors_authority_when_present(monkeypatch):
    """When the state's own loader has run, the row binds its controlling authority."""
    from django.core.management import call_command

    from specs.management.commands import load_state_conformity

    AuthoritySource.objects.create(
        source_code="SC_ACT63_2025_CONFORMITY",
        source_type=SourceType.STATE_STATUTE,
        source_rank="controlling",
        jurisdiction_code="SC",
        title="SC Act 63 of 2025 — IRC conformity through 12/31/2024",
        citation="SC Code §12-6-40(A)(1)",
    )
    monkeypatch.setattr(load_state_conformity, "READY_TO_SEED", True)
    call_command("load_state_conformity")

    sc = JurisdictionConformitySource.objects.get(jurisdiction_code="SC", tax_year=2025)
    assert sc.authority_source is not None
    assert sc.authority_source.source_code == "SC_ACT63_2025_CONFORMITY"


# ── 4. source_type hygiene across every loader ──────────────────────────────


# Known pre-existing debt, surveyed 2026-08-05. `source_type` is a CharField with choices
# and Django does not enforce choices at the DB layer, so an informal vocabulary
# ('statute', 'official_instructions', 'federal_form', …) has been persisting silently since
# the earliest loaders — 232 occurrences across 74 files, every one a near-miss of a real
# choice (note OFFICIAL_INSTRUCTION is singular). Reconciling them rewrites published
# exports and is its own work order, NOT campaign Phase 2.
#
# This baseline is a RATCHET, not an acceptance: counts may only fall, and a new distinct
# value fails the test. Lower a number here only when you have actually fixed occurrences.
# (load_ga700's 'state_guidance' was the 10th value and is fixed — hence its absence.)
SOURCE_TYPE_DEBT_BASELINE: dict[str, int] = {
    "statute": 108,
    "official_instructions": 59,
    "federal_form": 29,
    "official_guidance": 28,
    "instructions": 2,
    "revenue_procedure": 2,
    "form": 2,
    "irs_guidance": 1,
    "case_law": 1,
}


def _survey_invalid_source_types() -> dict[str, int]:
    """Count invalid source_type literals in AuthoritySource definition dicts.

    Scoped to dicts that also carry `source_code` — that is what makes a dict an authority
    definition. Without that scoping the walk also matches `source_type` keys inside
    TestScenario `inputs` payloads (where it means "this K-1 came from a 1065"), which
    produced 13 false positives on the first run of this survey.
    """
    valid = {c for c, _ in SourceType.choices}
    found: collections.Counter[str] = collections.Counter()

    for path in sorted(COMMANDS_DIR.glob("load_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            keys = {k.value for k in node.keys if isinstance(k, ast.Constant)}
            if "source_code" not in keys:
                continue
            for key, value in zip(node.keys, node.values):
                if (
                    isinstance(key, ast.Constant) and key.value == "source_type"
                    and isinstance(value, ast.Constant) and isinstance(value.value, str)
                    and value.value not in valid
                ):
                    found[value.value] += 1
    return dict(found)


def test_no_new_invalid_source_types():
    """Ratchet on the source_type vocabulary debt — it may shrink, never grow.

    The campaign adds ~130-200 state forms; without this gate each new loader is free to
    invent another unvalidated vocabulary word, and the enum drifts further from practice.
    """
    found = _survey_invalid_source_types()

    new_values = set(found) - set(SOURCE_TYPE_DEBT_BASELINE)
    assert not new_values, (
        f"new invalid source_type value(s): {sorted(new_values)}. "
        f"Use a real SourceType choice — see sources/models.py SourceType."
    )

    grew = {
        value: (count, SOURCE_TYPE_DEBT_BASELINE[value])
        for value, count in found.items()
        if count > SOURCE_TYPE_DEBT_BASELINE[value]
    }
    assert not grew, (
        "invalid source_type occurrences increased (value: now vs baseline): "
        f"{grew}. Use a real SourceType choice."
    )


def test_state_conformity_loader_uses_valid_source_types():
    """The campaign's own loaders carry zero debt — new work starts clean."""
    valid = {c for c, _ in SourceType.choices}
    tree = ast.parse((COMMANDS_DIR / "load_state_conformity.py").read_text(encoding="utf-8"))
    offenders = [
        value.value
        for node in ast.walk(tree) if isinstance(node, ast.Dict)
        for key, value in zip(node.keys, node.values)
        if (
            isinstance(key, ast.Constant) and key.value == "source_type"
            and isinstance(value, ast.Constant) and value.value not in valid
        )
    ]
    assert not offenders, f"campaign loader must use valid SourceType choices: {offenders}"
