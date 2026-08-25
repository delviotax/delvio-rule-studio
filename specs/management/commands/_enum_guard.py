# -*- coding: utf-8 -*-
"""THE ENUM RATCHET — the invalid-`source_type`/`source_rank` debt may SHRINK, never GROW.

WHY THIS EXISTS
---------------
`SourceType`/`SourceRank` are `TextChoices`, which Django validates in `full_clean()` —
a method `update_or_create()` never calls. There is no DB check constraint either. So a
loader can write `"state_instructions"` (plural), `"federal_form"` or `"statute"` and it
lands in production silently. 211 prod rows currently hold one.

⭐ A ratchet is the right instrument precisely because it needs NO ruling on the existing
debt. It does not ask anyone to fix the backlog. It stops the next one.

WHY IT MOVED HERE (2026-08-25, campaign D-41 — Ken: "yes", run it in the seed pre-flight)
------------------------------------------------------------------------------------------
It lived in `tests/test_state_conformity.py` alone, so it only ran when someone ran the
suite. ⚠⚠ **It went red on 2026-08-23 and FOUR SEED GATES PASSED THROUGH IT** — the four
loaders that broke it (`load_al_40nr`, `load_md_500`, `load_ms_83105`, `load_or_20`) were
all seeded afterwards, and the invalid values went live. Nobody saw, because seeding does
not run pytest.

It now runs where the damage happens: in `seed_all`, and in the per-loader pre-flight
`check_authority_owners --loader X --strict`. The test still exists and delegates here, so
there is **ONE baseline**, not two that can drift apart.

SCOPE
-----
⚠ The pytest version globbed `load_*.py` only — the same directory/pattern blindness that
made the two-writers guard miss two thirds of its problem (D-40). This one reuses
`_authority_guard.coverage()`, so it sees all three writer populations. Verified
2026-08-25: both scopes agreed exactly when measured, because no non-`load_` module
contributed an invalid value that day. Agreeing on one day is not a reason to stay narrow.

⚠ NOT CLAIMED: none of this affects a computed tax figure. `source_type` and `source_rank`
are provenance metadata — they drive retrieval (`sources/views.py` filters on
`source_type`) and reporting, not arithmetic.
"""
from __future__ import annotations

import collections

from . import _authority_guard as AG

# ---------------------------------------------------------------------------
# THE BASELINE — the debt as it stands. Regenerate with
#   python manage.py check_authority_owners --regenerate-enum-baseline
#
# ⚠ Lower it whenever the debt shrinks; that is what locks a gain in.
#   NEVER raise it to make a seed pass. A new invalid value is a typo to fix,
#   not a number to accommodate.
#
# Re-tightened 2026-08-25 after campaign A3/D-42: converting 20 non-owner declarations
# into references DELETED their invalid values too — source_type 233 -> 213, rank 5 -> 4.
# ⭐ Resolving ownership shrinks the vocabulary debt as a side effect.
# Previously set 2026-08-25 after campaign D-41 corrected seven rows across four loaders
# (`state_instructions`->`state_instruction` x4, `federal_form`->`official_form`,
# `official_instructions`->`state_instruction`, `state_guidance`->`state_instruction`).
# Previous baseline, frozen 2026-08-16, totalled 234 source_type occurrences.
# ---------------------------------------------------------------------------
SOURCE_TYPE_DEBT: dict[str, int] = {
    "statute":                 94,
    "official_instructions":   54,
    "federal_form":            29,
    "official_guidance":       28,
    "form":                    2,
    "instructions":            2,
    "revenue_procedure":       2,
    "case_law":                1,
    "irs_guidance":            1,
}

SOURCE_RANK_DEBT: dict[str, int] = {
    "primary_authority":       4,
}


def _valid():
    from sources.models import SourceRank, SourceType
    return ({c for c, _ in SourceType.choices}, {c for c, _ in SourceRank.choices})


def survey(decls=None):
    """-> (type_counts, rank_counts, {value: [(writer, source_code), ...]}).

    Counts DECLARATION SITES across every writer population, not prod rows.
    """
    valid_t, valid_r = _valid()
    if decls is None:
        decls = AG.coverage()["decls"]
    t, r = collections.Counter(), collections.Counter()
    where: dict[str, list] = collections.defaultdict(list)
    for code, writers in decls.items():
        for label, f in writers.items():
            st, sr = f.get("source_type"), f.get("source_rank")
            if st is not None and st not in valid_t:
                t[st] += 1
                where[st].append((label, code))
            if sr is not None and sr not in valid_r:
                r[sr] += 1
                where[sr].append((label, code))
    return dict(t), dict(r), dict(where)


def check(decls=None):
    """-> (ok, [problem strings]). Never raises; the caller decides how loud to be."""
    t, r, where = survey(decls)
    problems = []
    for label, found, base in (("source_type", t, SOURCE_TYPE_DEBT),
                               ("source_rank", r, SOURCE_RANK_DEBT)):
        for value in sorted(set(found) - set(base)):
            problems.append(
                "NEW invalid %s value %r (x%d) — use a real choice, see sources/models.py. %s"
                % (label, value, found[value],
                   "; ".join("%s:%s" % w for w in where[value][:6])))
        for value in sorted(set(found) & set(base)):
            if found[value] > base[value]:
                problems.append(
                    "invalid %s %r grew %d -> %d — the debt may shrink, never grow. %s"
                    % (label, value, base[value], found[value],
                       "; ".join("%s:%s" % w for w in where[value][:6])))
    return (not problems), problems


def shrinkage(decls=None):
    """-> [(field, value, baseline, now)] where the debt has FALLEN below the baseline.

    Not a failure — a prompt to lower the baseline so the gain is locked in. A ratchet
    that is never tightened stops being one.
    """
    t, r, _ = survey(decls)
    out = []
    for label, found, base in (("source_type", t, SOURCE_TYPE_DEBT),
                               ("source_rank", r, SOURCE_RANK_DEBT)):
        for value, n in sorted(base.items()):
            got = found.get(value, 0)
            if got < n:
                out.append((label, value, n, got))
    return out


def baseline_block(decls=None) -> str:
    """The two baseline literals for the CURRENT tree. Generated, never typed."""
    t, r, _ = survey(decls)
    lines = []
    for name, found in (("SOURCE_TYPE_DEBT", t), ("SOURCE_RANK_DEBT", r)):
        lines.append("%s: dict[str, int] = {" % name)
        for v, n in sorted(found.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append('    %-26s %d,' % ('"%s":' % v, n))
        lines.append("}")
        lines.append("")
    return "\n".join(lines)


def guard(write=None, raise_on_problem=True, decls=None):
    """Seed pre-flight entry point. Refuses a seed that would grow the debt."""
    def emit(m):
        if write is not None:
            write(m)

    ok, problems = check(decls)
    t, r, _ = survey(decls)
    emit("enum ratchet: %d invalid source_type + %d invalid source_rank declaration site(s); "
         "baseline %d + %d"
         % (sum(t.values()), sum(r.values()),
            sum(SOURCE_TYPE_DEBT.values()), sum(SOURCE_RANK_DEBT.values())))
    for field, value, base, now in shrinkage(decls):
        emit("    debt SHRANK: %s %r %d -> %d — lower the baseline in _enum_guard.py "
             "to lock it in" % (field, value, base, now))
    if ok:
        return True
    msg = "\n".join(
        ["", "ENUM RATCHET: this tree would GROW the invalid-vocabulary debt.", ""]
        + ["  %s" % p for p in problems]
        + ["",
           "Django validates TextChoices in full_clean(), which update_or_create() never",
           "calls, and there is no DB check constraint — so an invalid value seeds SILENTLY.",
           "That is how four loaders put five invalid values into production on 2026-08-23",
           "while this ratchet sat red in a test suite nobody ran at the gate.",
           "",
           "Fix the value. Raising the baseline in _enum_guard.py to make this pass is a",
           "decision to ship an unvalidated vocabulary word, and is Ken's call."])
    if raise_on_problem:
        from django.core.management.base import CommandError
        raise CommandError(msg)
    emit(msg)
    return False
