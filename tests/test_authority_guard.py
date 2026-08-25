# -*- coding: utf-8 -*-
"""CI cover for the two-writers guard (campaign D-31 / D-38 / D-40).

⚠ Before this file the guard had NO test at all. It was enforced by `seed_all` and by
`check_authority_owners --strict`, both of which call `selftest()` — so the only thing
standing between a broken guard and a silent all-clear was the guard's own opinion of
itself, evaluated at seed time.

⭐ These tests are pinned to the MECHANISM, never to today's collision COUNT. Asserting
"there are exactly 46" would go red the moment Ken resolves one — the failure this
campaign has hit five times. What is asserted is that the guard can still SEE, still
FIRE, and still REFUSE.

No database. No Django models. Safe to run at any time.
"""
import os

import pytest

from specs.management.commands import _authority_guard as G


def test_selftest_passes():
    """The guard's own selftest must pass — seed_all refuses to run if it does not."""
    ok, failures = G.selftest_report()
    assert ok, "guard selftest failed:\n    " + "\n    ".join(failures)


def test_every_writer_population_is_read():
    """⚠⚠ THE A1 REGRESSION TEST.

    The pre-A1 guard scanned one of three directories that write AuthoritySource rows
    and reported 19 of 46 collisions as the whole truth. Counts are deliberately NOT
    asserted; that each population yields SOMETHING is.
    """
    cov = G.coverage()
    assert not cov["problems"], cov["problems"]
    assert not cov["blind"], "population(s) yielding zero declarations: %s" % cov["blind"]
    by_name = {p["name"]: p for p in cov["populations"]}
    assert set(by_name) == set(G.POPULATION_NAMES)
    for name, p in by_name.items():
        assert p["codes"] > 0, "population %r yielded no declarations" % name


def test_federal_data_needs_the_import_reader():
    """`sources/federal_data/` rows are built by helper calls (`_irc(...)`).

    An `ast` literal scan cannot see them — which is precisely why that population was
    invisible for as long as it was. If this ever fails, the import reader has stopped
    working and the guard is blind again.
    """
    _, _, declaring, problems = G._scan_federal_data()
    assert not problems, problems
    assert declaring > 0


def test_guard_refuses_when_a_population_goes_dark():
    """⭐ The property A1 exists to add: it cannot report clean while blind."""
    real = G.FEDERAL_DATA_DIR
    G.FEDERAL_DATA_DIR = os.path.join(os.path.dirname(real), "no_such_directory")
    try:
        assert "federal_data" in G.coverage()["blind"]
        ok, failures = G.selftest_report()
        assert not ok and failures
        with pytest.raises(Exception) as exc:
            G.guard(write=lambda _m: None, raise_on_new=True)
        assert "unreadable" in str(exc.value)
    finally:
        G.FEDERAL_DATA_DIR = real
    assert G.selftest_report()[0], "the guard did not recover after the fixture"


def test_no_unacknowledged_collisions_on_disk():
    """The library must not GROW a collision. Resolve ownership; do not acknowledge it."""
    result = G.guard(write=lambda _m: None, raise_on_new=False)
    assert not result["new"], (
        "NEW authority collision(s): %s — one module DECLARES, every other REFERENCES "
        "(campaign D-29). Adding to ACKNOWLEDGED is Ken's call, not a workaround."
        % sorted(result["new"])
    )


def test_acknowledgement_is_of_a_writer_set_not_a_code():
    """A module JOINING a known collision is a NEW collision.

    ⚠ Six of the pre-A1 acknowledgements recorded an incomplete writer set, so this is
    the property that had actually been failing rather than a hypothetical one.
    """
    code, (writers, _note) = next(iter(sorted(G.ACKNOWLEDGED.items())))
    assert G.is_acknowledged(code, list(writers))
    assert not G.is_acknowledged(code, list(writers) + ["specs/load_newcomer.py"])
    assert not G.is_acknowledged(code, list(writers)[:-1])


def test_guard_does_not_scan_its_own_fixtures():
    """Pre-A1 the guard's `selftest()` fixtures were scanned as real declarations."""
    assert not [c for c in G.coverage()["decls"] if c.startswith("ZZ_")]


def test_acknowledged_entries_all_correspond_to_a_real_collision():
    """A stale entry is a lie the guard tells itself.

    ⭐ The list is a WORKLIST: entries are meant to LEAVE it when Ken rules on ownership
    (D-39 removed `GA_OCGA_48_7`). An entry naming writers that no longer collide would
    make the guard quietly tolerate nothing at all — and hide that the work was done.
    """
    live = G.collisions(G.coverage()["decls"])
    stale = [c for c in G.ACKNOWLEDGED if c not in live]
    assert not stale, (
        "ACKNOWLEDGED names %s, which no longer collide. Remove the entry — the list is "
        "a worklist and shrinking it is the point." % stale
    )
