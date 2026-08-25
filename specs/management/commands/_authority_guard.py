# -*- coding: utf-8 -*-
"""THE TWO-WRITERS GUARD — refuses to let a second module declare an AuthoritySource
another module already declares.

WHY THIS EXISTS
---------------
Campaign D-31 named "two writers of one row" as the fourth member of the defect
family. D-38 showed it is not an incident but a standing property of the library:
modules write with `AuthoritySource.objects.update_or_create(source_code=...,
defaults=...)`, so where two of them declare one code **what production holds
depends on which command was run last** — silently, with no error and no diagnostic.

WHY IT WAS REWRITTEN (2026-08-25, campaign A1 — Ken's direct go)
-----------------------------------------------------------------
The first version of this guard scanned `specs/management/commands/` only.
**Three directories write AuthoritySource rows.** It therefore saw **19 of 46**
disagreeing codes — 41% — and reported the rest as clean.

⚠⚠ That was the SAME defect one generation earlier, repeated. The ad-hoc guard this
file replaced scanned only `load_*.py` for a double-quoted `"source_code":`, so it
could not see `_state_conformity_tier1.py`, which owns rows. The fix widened the
FILE PATTERN and kept the DIRECTORY — and the population it still could not see was
four times larger than the one that motivated the fix.

⭐ The lesson, now structural rather than advisory: **a guard that cannot see an owner
cannot detect a second writer of it, and a self-test pinned to a synthetic fixture
cannot check its own SCOPE.** `selftest()` now asserts that every population is
actually being read, and `guard()` REFUSES rather than reporting when one goes dark.

WHAT IT DOES
------------
* REFUSES any collision that is not on the acknowledged list  -> the problem cannot GROW.
* REFUSES if a whole writer population goes unreadable        -> it cannot go blind quietly.
* WARNS loudly on the acknowledged ones                       -> the problem stays VISIBLE.

That split is deliberate. A guard that refused outright would fail on ~50 pre-existing
codes and block real work on day one, and would be switched off within a week. This
one fails closed on anything new and hands Ken a finite worklist for the rest.

⚠ WHERE THIS RUNS. Only `seed_all` and `check_authority_owners` invoke it; an individual
`manage.py load_xx` does NOT. The pre-flight before seeding one loader is therefore
explicit and manual:

    python manage.py check_authority_owners --loader load_xx.py --strict

That is how D-38's GA-500 hazard was caught. Wiring the guard into every loader is a
separate change across 124 files and is NOT done here.

⚠⚠ WHAT THE GUARD DOES NOT FIX. The damage is worse than "last writer wins": keys a
writer OMITS are absent from `defaults`, so Django leaves those columns alone.
Production can hold a CHIMERA of two writers that neither would produce, and
re-seeding the rightful owner does NOT restore its row. Ownership and content are
two separate decisions. See delvio-states `research/authority_ownership_assessment.md`.

DESIGN NOTES, each one paid for
-------------------------------
* Scans EVERY population, EVERY module and BOTH quote styles.
* Reports its own COVERAGE, per population. A sweep that does not say how much it
  examined is not evidence; a clean result from 41% coverage is indistinguishable
  from a clean library.
* Pinned to the MECHANISM, not to today's data. `selftest()` proves the guard FIRES
  on a synthetic collision and proves each population is READ. Asserting "there are
  exactly 46" would go red the moment Ken resolves one — the failure this campaign
  has hit five times.
* ⚠ `sources/federal_data/` is read by IMPORT, not by `ast`. Its rows are built by
  helper functions (`_irc(...)`, `_instr(...)`), so no literal-dict scan can see them.
  This is a deliberate, scoped exception to the "no execution" rule: those modules are
  pure data and import without Django (verified 2026-08-25). The alternative —
  pattern-matching the helper call — is the prose-matching method this campaign has
  already discarded three times.
* Writer labels are POPULATION-QUALIFIED (`specs/load_x.py`, `federal_data/irc_sections.py`)
  so two modules sharing a basename across directories can never be confused for one.
"""
from __future__ import annotations

import ast
import glob
import importlib
import os
import pkgutil

_HERE = os.path.dirname(os.path.abspath(__file__))
CMD_DIR = _HERE                                                   # specs/management/commands
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))  # repo root
SOURCES_CMD_DIR = os.path.join(_REPO, "sources", "management", "commands")
FEDERAL_DATA_PKG = "sources.federal_data"
FEDERAL_DATA_DIR = os.path.join(_REPO, "sources", "federal_data")

POPULATION_NAMES = ("specs", "sources", "federal_data")

# Fields whose disagreement changes what a spec points at.
MATERIAL_FIELDS = ("source_type", "source_rank", "title", "citation", "issuer", "official_url")

# ---------------------------------------------------------------------------
# ACKNOWLEDGED collisions — the state of the world when the guard's SCOPE was
# corrected (2026-08-25, campaign A1). Regenerated with
# `python manage.py check_authority_owners --regenerate-acknowledged`, never typed.
#
# ⚠ Each entry is a KNOWN defect awaiting an ownership ruling from Ken, NOT an
#    approval of the pattern. The list grew from 23 because the guard's SCOPE was
#    fixed, not because anything got worse. The rows were always there.
#
# ⚠ Adding a code here is a decision to tolerate a silent last-writer-wins row.
#    Do not add one to make a seed pass. Resolve the ownership instead:
#    one module DECLARES, every other module REFERENCES (campaign D-29).
#
# ⚠⚠ The WRITER SET is part of the acknowledgement. A module joining an existing
#     collision is a NEW collision and the guard will refuse it. Six of the previous
#     23 sets were INCOMPLETE — each omitted a writer in a population the old guard
#     could not see — including `IRC_704`, which was filed as "identical today"
#     while its unseen third writer disagreed on six fields.
# ---------------------------------------------------------------------------
ACKNOWLEDGED: dict[str, tuple[tuple[str, ...], str]] = {
    # --- writers DISAGREE: live last-writer-wins rows (46) ---
    "AL_CODE_40_18":             (('specs/load_al_form20c.py', 'specs/load_al_passthrough.py'), 'differs: title,citation'),
    "IRC_1":                     (('federal_data/irc_sections.py', 'specs/load_1040_spine.py'), 'differs: source_rank,title,citation,official_url'),
    "IRC_1031":                  (('federal_data/irc_sections.py', 'specs/load_8824.py'), 'differs: source_type,source_rank,title,issuer,official_url'),
    "IRC_11":                    (('federal_data/irc_sections.py', 'specs/load_1120_spine.py'), 'differs: source_type,title,citation,issuer,official_url'),
    "IRC_1402":                  (('federal_data/irc_sections.py', 'specs/load_1040_minister.py', 'specs/load_1040_schedule_k1.py', 'specs/load_1065_se.py'), 'differs: source_type,source_rank,title,citation,issuer,official_url'),
    "IRC_1411":                  (('federal_data/irc_sections.py', 'specs/load_1040_8960.py'), 'differs: source_type,source_rank,citation,issuer,official_url'),
    "IRC_163":                   (('federal_data/irc_sections.py', 'specs/load_sch_1a.py'), 'differs: title,citation'),
    "IRC_163J":                  (('specs/load_1120_spine.py', 'specs/load_8990.py'), 'differs: title,citation'),
    "IRC_165":                   (('federal_data/irc_sections.py', 'specs/load_4684.py'), 'differs: source_type,title,citation,issuer,official_url'),
    "IRC_168":                   (('sources/load_1120s_family.py', 'specs/_1120s_sources.py', 'specs/load_4797.py'), 'differs: source_type,source_rank,title,citation,issuer,official_url'),
    "IRC_170":                   (('federal_data/irc_sections.py', 'specs/load_1040_schedule_a.py'), 'differs: source_type,source_rank,title,citation,official_url'),
    "IRC_172":                   (('specs/load_1040_form_172.py', 'specs/load_1120_spine.py'), 'differs: source_type,title,citation,official_url'),
    "IRC_199A":                  (('federal_data/irc_sections.py', 'specs/load_1040_schedule_k1.py'), 'differs: source_type,source_rank,citation,issuer,official_url'),
    "IRC_1G":                    (('specs/load_1040_form_8615.py', 'specs/load_8814.py'), 'differs: source_rank,title,citation'),
    "IRC_25A":                   (('federal_data/irc_sections.py', 'specs/load_1040_form_8863.py'), 'differs: source_type,source_rank,title,citation,issuer,official_url'),
    "IRC_280A":                  (('federal_data/irc_sections.py', 'specs/load_1040_form_8829.py'), 'differs: source_type,source_rank,title,citation,issuer,official_url'),
    "IRC_36B":                   (('federal_data/irc_sections.py', 'specs/load_1040_form_8962.py'), 'differs: source_type,source_rank,citation,issuer,official_url'),
    "IRC_41":                    (('federal_data/irc_sections.py', 'specs/load_6765.py'), 'differs: source_type,source_rank,issuer,official_url'),
    "IRC_453":                   (('federal_data/irc_sections.py', 'specs/load_6252.py'), 'differs: source_type,source_rank,issuer,official_url'),
    "IRC_465":                   (('federal_data/irc_sections.py', 'specs/load_1040_schedule_e.py'), 'differs: source_type,source_rank,citation,issuer,official_url'),
    "IRC_469":                   (('federal_data/irc_sections.py', 'specs/load_1040_schedule_e.py'), 'differs: source_type,source_rank,citation,issuer,official_url'),
    "IRC_61":                    (('federal_data/irc_sections.py', 'specs/load_1040_w2g.py'), 'differs: source_type,source_rank,citation,issuer,official_url'),
    "IRC_62":                    (('federal_data/irc_sections.py', 'specs/load_1040_sch123.py'), 'differs: source_rank,title,issuer,official_url'),
    "IRC_6654":                  (('specs/load_1040_2210.py', 'specs/load_1040_spine.py'), 'differs: source_type,title,citation,issuer,official_url'),
    "IRC_702":                   (('federal_data/irc_sections.py', 'specs/load_1065_m1_m2.py', 'specs/load_1065_schedule_k.py', 'specs/load_1065_schedule_k1.py', 'specs/load_1065_se.py'), 'differs: source_type,source_rank,title,citation,issuer,official_url'),
    "IRC_703":                   (('federal_data/irc_sections.py', 'specs/load_1065_schedule_k.py'), 'differs: source_type,source_rank,title,citation,issuer,official_url'),
    "IRC_704":                   (('federal_data/irc_sections.py', 'specs/load_1065_schedule_k.py', 'specs/load_1065_schedule_k1.py'), 'differs: source_type,source_rank,title,citation,issuer,official_url'),
    "IRC_705":                   (('federal_data/irc_sections.py', 'specs/load_1065_l_b.py', 'specs/load_1065_m1_m2.py', 'specs/load_1065_schedule_k1.py'), 'differs: source_type,source_rank,title,citation,issuer,official_url'),
    "IRC_752":                   (('federal_data/irc_sections.py', 'specs/load_1065_schedule_k1.py'), 'differs: source_type,source_rank,title,citation,issuer,official_url'),
    "IRS_2025_1065_INSTR":       (('federal_data/forms_1065.py', 'specs/load_4797.py'), 'differs: source_type,title,citation'),
    "IRS_2025_1065_K1_INSTR":    (('federal_data/forms_1065.py', 'specs/load_1040_schedule_k1.py'), 'differs: source_type,title,citation,official_url'),
    "IRS_2025_1120S_K1_INSTR":   (('federal_data/forms_1120s.py', 'specs/load_1040_schedule_k1.py'), 'differs: source_type,title,citation,official_url'),
    "IRS_2025_1125A_INSTR":      (('federal_data/forms_1120.py', 'specs/load_remaining_1120s.py'), 'differs: title,official_url'),
    "IRS_2025_1125E_INSTR":      (('sources/load_1120s_family.py', 'specs/load_remaining_1120s.py'), 'differs: title,official_url'),
    "IRS_2025_8283_INSTR":       (('specs/load_1040_form_8283.py', 'specs/load_1120s_complete.py'), 'differs: title,citation,official_url'),
    "IRS_2025_8949_INSTR":       (('sources/load_1120s_family.py', 'specs/_1120s_sources.py', 'specs/load_1040_schedule_d.py'), 'differs: source_type,title,citation,official_url'),
    "IRS_2025_8959_INSTR":       (('federal_data/forms_supporting.py', 'specs/load_1040_schedule_c.py'), 'differs: source_type,title,citation,official_url'),
    "IRS_2025_8995_INSTR":       (('federal_data/forms_supporting.py', 'specs/load_1040_schedule_c.py'), 'differs: source_type,title,citation,official_url'),
    "IRS_2025_F1065":            (('specs/load_1065_l_b.py', 'specs/load_1065_m1_m2.py', 'specs/load_1065_schedule_k.py'), 'differs: title,citation'),
    "IRS_2025_F7206_INSTR":      (('specs/load_1040_form_7206.py', 'specs/load_1040_retirement.py'), 'differs: source_type,citation'),
    "IRS_2025_I1065":            (('specs/load_1065_l_b.py', 'specs/load_1065_m1_m2.py', 'specs/load_1065_schedule_k.py'), 'differs: title,citation'),
    "IRS_PUB_544":               (('specs/load_4797.py', 'specs/load_8824.py'), 'differs: official_url'),
    "NC_GS_105_CORP":            (('specs/load_nc_cd405.py', 'specs/load_nc_passthrough.py'), 'differs: title,citation'),
    "RP_2024_40":                (('specs/load_1040_spine.py', 'specs/load_1041_spine.py'), 'differs: source_type,title,citation,issuer'),
    "SC_2025_SC1120I":           (('specs/load_sc1120.py', 'specs/load_sc_passthrough.py'), 'differs: source_type,title'),
    "SC_ACT63_2025_CONFORMITY":  (('specs/load_sc1040.py', 'specs/load_sc1120.py'), 'differs: source_type,citation,official_url'),

    # --- writers AGREE today: benign, but still two writers (7) ---
    "IRC_1222":                  (('sources/load_1120s_family.py', 'specs/_1120s_sources.py'), 'identical today'),
    "IRC_179":                   (('sources/load_1120s_family.py', 'specs/_1120s_sources.py'), 'identical today'),
    "IRC_707C":                  (('specs/load_1065_schedule_k.py', 'specs/load_1065_schedule_k1.py', 'specs/load_1065_se.py'), 'identical today'),
    "IRS_2025_1120S_SCHD_INSTR": (('sources/load_1120s_family.py', 'specs/_1120s_sources.py'), 'identical today'),
    "IRS_2025_4562_INSTR":       (('sources/load_1120s_family.py', 'specs/_1120s_sources.py'), 'identical today'),
    "IRS_2025_F1120":            (('specs/load_1120_schl.py', 'specs/load_1120_spine.py'), 'identical today'),
    "IRS_2025_I1120":            (('specs/load_1120_schl.py', 'specs/load_1120_spine.py'), 'identical today'),
}


# ---------------------------------------------------------------------------
# Readers — one per population.
# ---------------------------------------------------------------------------
def _declarations_in(path: str) -> dict[str, dict]:
    """Literal AuthoritySource declarations in one module, via `ast`. Never raises."""
    out: dict[str, dict] = {}
    try:
        tree = ast.parse(open(path, encoding="utf-8").read())
    except (SyntaxError, OSError, UnicodeDecodeError):
        return out
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        d = {}
        for k, v in zip(node.keys, node.values):
            if isinstance(k, ast.Constant) and isinstance(k.value, str) and isinstance(v, ast.Constant):
                d[k.value] = v.value
        # a declaration, not a mere reference: it carries the row's own content
        if "source_code" in d and "source_type" in d:
            out[d["source_code"]] = d
    return out


def _scan_dir_ast(directory: str, label: str):
    """-> (decls, modules_seen, modules_declaring, problems)."""
    decls: dict[str, dict[str, dict]] = {}
    if not os.path.isdir(directory):
        return decls, 0, 0, ["%s: directory not found (%s)" % (label, directory)]
    # ⚠ Skip THIS file. Its selftest fixtures are literal dicts carrying source_code
    #   and source_type, so the pre-A1 scanner counted ZZ_SYNTHETIC_CODE and
    #   ZZ_SOLE_WRITER as real declarations of the guard itself. Harmless in effect,
    #   but it inflated the code count and would have collided with any real code of
    #   that name. Only this one module is skipped — `_state_conformity_tier1.py` and
    #   every other underscore module genuinely owns rows and must still be read.
    _self = os.path.basename(__file__).replace(".pyc", ".py")
    paths = sorted(p for p in glob.glob(os.path.join(directory, "*.py"))
                   if os.path.basename(p) != _self)
    declaring = 0
    for p in paths:
        found = _declarations_in(p)
        if found:
            declaring += 1
        for code, fields in found.items():
            decls.setdefault(code, {})["%s/%s" % (label, os.path.basename(p))] = fields
    return decls, len(paths), declaring, []


def _scan_federal_data():
    """Read `sources/federal_data/` by IMPORT — its rows are built by helper calls.

    Discovers every module-level list/tuple of source dicts rather than naming the
    six that exist today, so a new data module cannot be silently missed.
    """
    decls: dict[str, dict[str, dict]] = {}
    problems: list[str] = []
    if not os.path.isdir(FEDERAL_DATA_DIR):
        return decls, 0, 0, ["federal_data: directory not found (%s)" % FEDERAL_DATA_DIR]
    names = sorted(m.name for m in pkgutil.iter_modules([FEDERAL_DATA_DIR])
                   if not m.name.startswith("_"))
    declaring = 0
    for name in names:
        try:
            mod = importlib.import_module("%s.%s" % (FEDERAL_DATA_PKG, name))
        except Exception as exc:                                   # noqa: BLE001
            problems.append("federal_data/%s: import failed (%s: %s)"
                            % (name, type(exc).__name__, exc))
            continue
        got = False
        for attr in dir(mod):
            if attr.startswith("_"):
                continue
            val = getattr(mod, attr)
            if not isinstance(val, (list, tuple)):
                continue
            for d in val:
                if isinstance(d, dict) and "source_code" in d and "source_type" in d:
                    decls.setdefault(d["source_code"], {})["federal_data/%s.py" % name] = d
                    got = True
        if got:
            declaring += 1
    return decls, len(names), declaring, problems


# ---------------------------------------------------------------------------
def coverage() -> dict:
    """Per-population census. THE thing a clean report is worthless without."""
    readers = (lambda: _scan_dir_ast(CMD_DIR, "specs"),
               lambda: _scan_dir_ast(SOURCES_CMD_DIR, "sources"),
               _scan_federal_data)
    pops, merged, problems = [], {}, []
    for name, reader in zip(POPULATION_NAMES, readers):
        d, seen, declaring, probs = reader()
        pops.append({"name": name, "modules": seen, "declaring": declaring,
                     "codes": len(d), "problems": probs})
        problems.extend(probs)
        for code, writers in d.items():
            merged.setdefault(code, {}).update(writers)
    return {"populations": pops,
            "decls": merged,
            "modules": sum(p["modules"] for p in pops),
            "codes": len(merged),
            "problems": problems,
            "blind": [p["name"] for p in pops if p["codes"] == 0]}


def scan(cmd_dir: str | None = None):
    """-> ({source_code: {writer_label: fields}}, modules_scanned, modules_declaring).

    `cmd_dir=None` scans ALL THREE writer populations. Passing an explicit directory
    scans only that directory with the `ast` reader — the pre-A1 behaviour, kept so
    single-population comparisons stay reproducible.
    """
    if cmd_dir is not None:
        label = os.path.basename(cmd_dir.rstrip("/\\")) or "dir"
        d, seen, declaring, _ = _scan_dir_ast(cmd_dir, label)
        return d, seen, declaring
    cov = coverage()
    return cov["decls"], cov["modules"], sum(p["declaring"] for p in cov["populations"])


def collisions(decls: dict[str, dict[str, dict]] | None = None):
    """-> {source_code: {"writers": [...], "differs": [fields]}} for codes with >1 writer."""
    if decls is None:
        decls, _, _ = scan()
    out = {}
    for code, writers in decls.items():
        if len(writers) < 2:
            continue
        differs = [f for f in MATERIAL_FIELDS
                   if len({w.get(f) for w in writers.values()}) > 1]
        out[code] = {"writers": sorted(writers), "differs": differs}
    return out


def is_acknowledged(code: str, writers) -> bool:
    """The acknowledgement is of a SPECIFIC collision, not of the code forever:
    a module joining an existing collision is itself a new collision."""
    entry = ACKNOWLEDGED.get(code)
    return entry is not None and set(entry[0]) == set(writers)


def _matches_loader(loader_name: str, writers) -> bool:
    """Accept a bare basename (`load_ga500_form_500.py`) or a qualified label."""
    want = loader_name.split("/")[-1]
    return any(w == loader_name or w.split("/")[-1] == want for w in writers)


def guard(loader_name: str | None = None, write=None, raise_on_new=True):
    """Refuse UNACKNOWLEDGED collisions and BLIND populations; report the rest.

    loader_name: restrict to collisions involving this module (pre-seed use).
                 None -> check the whole library (seed_all / CI use).
    """
    def emit(msg):
        if write is not None:
            write(msg)

    def fail(msg):
        if raise_on_new:
            from django.core.management.base import CommandError
            raise CommandError(msg)
        emit(msg)

    cov = coverage()
    decls = cov["decls"]

    # --- coverage FIRST. A clean result from a blind guard is worse than no guard. ---
    emit("two-writers guard coverage:")
    for p in cov["populations"]:
        emit("    %-14s %3d modules, %3d declaring, %4d codes%s"
             % (p["name"], p["modules"], p["declaring"], p["codes"],
                "   <- BLIND" if p["codes"] == 0 else ""))
    if cov["blind"] or cov["problems"]:
        lines = ["", "TWO-WRITERS GUARD: a writer population went unreadable.", ""]
        for b in cov["blind"]:
            lines.append("  population %r yielded ZERO declarations" % b)
        for q in cov["problems"]:
            lines.append("  %s" % q)
        lines += [
            "",
            "This guard reported 19 of 46 collisions for a day because it could not see",
            "two of the three populations. A clean report from a blind guard is worse than",
            "no guard at all, so it refuses instead of passing.",
        ]
        fail("\n".join(lines))

    found = collisions(decls)
    if loader_name:
        found = {c: v for c, v in found.items() if _matches_loader(loader_name, v["writers"])}

    new = {c: v for c, v in found.items() if not is_acknowledged(c, v["writers"])}
    known = {c: v for c, v in found.items() if is_acknowledged(c, v["writers"])}

    emit("two-writers guard: %d modules scanned, %d authority codes declared, "
         "%d collisions (%d acknowledged, %d NEW)"
         % (cov["modules"], len(decls), len(found), len(known), len(new)))
    for c, v in sorted(known.items()):
        emit("  ~ acknowledged %-26s %s%s"
             % (c, ", ".join(v["writers"]),
                ("  [differs: %s]" % ",".join(v["differs"])) if v["differs"] else "  [identical today]"))

    if new:
        lines = ["", "TWO-WRITERS GUARD: %d NEW authority collision(s)." % len(new), ""]
        for c, v in sorted(new.items()):
            lines.append("  %s" % c)
            lines.append("      declared by  : %s" % ", ".join(v["writers"]))
            lines.append("      fields differ: %s" % (", ".join(v["differs"]) or "none (identical today)"))
            if c in ACKNOWLEDGED:
                lines.append("      NOTE: acknowledged with a DIFFERENT writer set: %s"
                             % ", ".join(ACKNOWLEDGED[c][0]))
        lines += [
            "",
            "Modules write sources with update_or_create(defaults=...), so whichever of these",
            "runs LAST silently decides what production holds. That is campaign D-31's",
            "two-writers defect.",
            "",
            "And it is not even 'last writer wins': keys a writer OMITS are absent from",
            "defaults, so Django leaves those columns alone. Production can hold a CHIMERA of",
            "two writers that neither would produce, and re-seeding the rightful owner does",
            "NOT restore its row.",
            "",
            "FIX IT, do not acknowledge it: ONE module DECLARES the source; every other module",
            "REFERENCES it via EXISTING_SOURCES_TO_REFERENCE (campaign D-29). If the non-owner",
            "also contributes excerpts, re-home them rather than dropping them.",
            "",
            "Adding a code to _authority_guard.ACKNOWLEDGED to make this pass is a decision to",
            "ship a silent last-writer-wins row, and is Ken's call, not a workaround.",
        ]
        fail("\n".join(lines))
    return {"new": new, "acknowledged": known, "modules": cov["modules"],
            "codes": len(decls), "coverage": cov["populations"]}


def selftest_report():
    """-> (ok, [failure strings]). Proves the guard FIRES *and* that its SCOPE is intact.

    ⚠ Deliberately does NOT assert how many collisions exist today — that number
    changes the moment Ken resolves one, and a check pinned to current state goes
    red on success. These test the MECHANISM.

    ⚠⚠ Test 2 is the one the previous selftest could not have written. The old guard
    passed its own selftest while blind to two of three populations, because a
    synthetic fixture proves the MATCHING works and says nothing about the SCOPE.
    """
    failures: list[str] = []

    # 1 — MATCHING: a synthetic collision is detected; a sole writer is not.
    fake = {
        "ZZ_SYNTHETIC_CODE": {
            "specs/load_a.py": {"source_code": "ZZ_SYNTHETIC_CODE", "source_type": "statute",
                                "source_rank": "controlling", "title": "A"},
            "federal_data/zz.py": {"source_code": "ZZ_SYNTHETIC_CODE", "source_type": "regulation",
                                   "source_rank": "primary_official", "title": "B"},
        },
        "ZZ_SOLE_WRITER": {
            "specs/load_a.py": {"source_code": "ZZ_SOLE_WRITER", "source_type": "statute"},
        },
    }
    found = collisions(fake)
    if "ZZ_SYNTHETIC_CODE" not in found:
        failures.append("matching: a synthetic two-writer collision was NOT detected")
    if "ZZ_SOLE_WRITER" in found:
        failures.append("matching: a sole writer was wrongly reported as a collision")
    if set(found.get("ZZ_SYNTHETIC_CODE", {}).get("differs", [])) < {"source_type", "source_rank", "title"}:
        failures.append("matching: the differing fields were not all reported")
    if "ZZ_SYNTHETIC_CODE" in ACKNOWLEDGED:
        failures.append("matching: the synthetic fixture leaked into ACKNOWLEDGED")

    # 2 — SCOPE: every population is actually being read. Counts are NOT asserted.
    cov = coverage()
    for p in cov["populations"]:
        if p["codes"] == 0:
            failures.append(
                "scope: population %r yielded ZERO declarations — the guard is blind to it, "
                "which is the defect this rewrite exists to fix" % p["name"])
    failures.extend("scope: " + q for q in cov["problems"])

    # 3 — SCOPE, positively: the federal_data reader must survive helper-built rows,
    #     which is exactly what an ast-only reader cannot do.
    _, _, fd_declaring, _ = _scan_federal_data()
    if fd_declaring == 0:
        failures.append("scope: federal_data yielded no declaring module — its rows are built "
                        "by helper calls, so this is the ast-blindness failure recurring")

    # 4 — HYGIENE: the guard must not count its OWN fixtures as real declarations.
    #     The pre-A1 version did: ZZ_SYNTHETIC_CODE and ZZ_SOLE_WRITER were scanned
    #     out of this file's own selftest and counted as declared by it.
    if any(c.startswith("ZZ_") for c in cov["decls"]):
        failures.append("hygiene: a ZZ_ selftest fixture is being scanned as a real declaration")

    return (not failures), failures


def selftest() -> bool:
    """Backward-compatible bool form. `selftest_report()` says WHY it failed."""
    return selftest_report()[0]
