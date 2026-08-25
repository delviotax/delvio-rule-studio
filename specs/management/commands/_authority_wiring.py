# -*- coding: utf-8 -*-
"""THE D-29 OWNERSHIP REMEDY, actually wired up.

WHY THIS EXISTS
---------------
Campaign D-29 set the remedy for two writers of one authority row: **one module
DECLARES the source; every other module REFERENCES it** via
`EXISTING_SOURCES_TO_REFERENCE`, re-homing any excerpt it contributes into
`NEW_EXCERPTS_ON_EXISTING`.

⚠⚠ D-42 found the remedy was **not wired up**. Eighteen loaders defined one or both
lists and their `handle()` NEVER READ THEM — the lists sat there looking like a
mechanism and doing nothing. Adding an entry would have silently dropped the link and
the excerpt, which is the exact failure D-38 caught on GA-500.

⭐ That was the THIRD instance in one day of the same shape: the two-writers guard
scanned one of three writer populations (D-40); the enum checker was hardcoded to the
one module with zero violations (D-41); and this. **Each was present, documented and
believed in, and none had been verified to be connected to anything. "Does this exist?"
and "does this run?" are different questions.**

This module exists so the answer is written ONCE and called, rather than reimplemented
per loader — which is how the three variants above drifted apart in the first place.

⚠ SAFE BY CONSTRUCTION at the time of wiring: every one of the eighteen unwired lists
was EMPTY, and where a list was absent it was added empty. Iterating an empty list
changes nothing, so wiring these loaders is behaviour-neutral until someone puts an
entry in — which is the point. **Nothing needed re-seeding to land this.**
"""
from __future__ import annotations


def resolve_references(codes, sources, write=None):
    """Resolve `EXISTING_SOURCES_TO_REFERENCE` into the loader's `sources` dict.

    A referenced code is one this loader CITES but does not OWN. Resolving it lets the
    loader's authority links point at the real row without rewriting it.

    ⚠ A missing code WARNS rather than raising: a reference to something not yet seeded
    is a legitimate mid-rebuild state (phase 1 sources run before phase 2 specs). It is
    reported loudly so it cannot pass as success — the dangling-reference defect of
    D-25/O4 is a reference to something that does not exist ANYWHERE, which the
    two-writers/ownership tooling catches statically.
    """
    from sources.models import AuthoritySource

    missing = []
    for code in codes or ():
        src = AuthoritySource.objects.filter(source_code=code).first()
        if src:
            sources[code] = src
        else:
            missing.append(code)
    if missing and write is not None:
        write("  referenced source(s) NOT FOUND, links to them will be skipped: %s"
              % ", ".join(sorted(missing)))
    return sources


def apply_new_excerpts(pairs, sources=None, write=None):
    """Apply `NEW_EXCERPTS_ON_EXISTING` — excerpts this loader contributes to a row it
    does not own.

    ⭐ This is the half that makes ownership resolution non-destructive. Moving a
    declaration to a reference without re-homing its excerpts would DROP them, so the
    remedy is only safe when both halves run.
    """
    from sources.models import AuthorityExcerpt, AuthoritySource

    sources = sources if sources is not None else {}
    applied, missing = 0, []
    for code, exc in pairs or ():
        src = sources.get(code) or AuthoritySource.objects.filter(source_code=code).first()
        if not src:
            missing.append(code)
            continue
        exc = dict(exc)
        AuthorityExcerpt.objects.update_or_create(
            authority_source=src, excerpt_label=exc["excerpt_label"], defaults=exc,
        )
        applied += 1
    if write is not None:
        if applied:
            write("  %d excerpt(s) applied to existing sources" % applied)
        if missing:
            write("  source(s) NOT FOUND, excerpt(s) SKIPPED: %s" % ", ".join(sorted(set(missing))))
    return applied
