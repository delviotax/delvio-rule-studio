# -*- coding: utf-8 -*-
"""THE TWO-WRITERS GUARD — refuses to let a second loader declare an AuthoritySource
another loader already declares.

WHY THIS EXISTS
---------------
Campaign D-31 named "two writers of one row" as the fourth member of the defect
family. D-38 showed it is not an incident but a standing property of the library:
of 621 authority codes, 24 are declared by more than one loader and 20 of those
have writers that DISAGREE. Loaders write with
`AuthoritySource.objects.update_or_create(source_code=..., defaults=...)`, so for
those 20 **what production holds depends on which command was run last** — silently,
with no error and no diagnostic.

It was caught the only way it could be: a pre-flight before an approved, unrelated
fix. Re-seeding `load_ga500_form_500.py` would have downgraded `GA_OCGA_48_7` from
`controlling` to `primary_official` and replaced a dated section-list citation with
an undated "et seq." — changing what `load_ga700.py`'s spec points at.

WHAT IT DOES
------------
* REFUSES any collision that is not on the acknowledged list  -> the problem cannot GROW.
* WARNS loudly on the acknowledged ones                        -> the problem stays VISIBLE.

That split is deliberate. A guard that refused outright would fail on 24 pre-existing
codes and block real work on day one, and would be switched off within a week. This
one fails closed on anything new and hands Ken a finite worklist for the rest.

DESIGN NOTES, each one paid for
-------------------------------
* Scans EVERY module and BOTH quote styles. The previous ad-hoc guard scanned only
  `load_*.py` for a double-quoted `"source_code":`, so it could not see
  `_state_conformity_tier1.py` — which owns rows. A guard that cannot see an owner
  cannot detect a second writer of it.
* Reports its own COVERAGE. A sweep that does not say how much it examined is not
  evidence; a clean result from 0.8% coverage is indistinguishable from looking at
  nothing.
* Pinned to the MECHANISM, not to today's data. `selftest()` proves the guard FIRES
  on a synthetic collision. Asserting "there are exactly 24" would go red the moment
  Ken resolves one — the failure this campaign has hit five times.
"""
from __future__ import annotations

import ast
import glob
import os
import re

CMD_DIR = os.path.dirname(os.path.abspath(__file__))

# Fields whose disagreement changes what a spec points at.
MATERIAL_FIELDS = ("source_type", "source_rank", "title", "citation", "issuer", "official_url")

# ---------------------------------------------------------------------------
# ACKNOWLEDGED collisions — the state of the world when the guard was added
# (2026-08-24, campaign D-38). Each entry is a KNOWN defect awaiting an ownership
# ruling from Ken, NOT an approval of the pattern.
#
# ⚠ Adding a code here is a decision to tolerate a silent last-writer-wins row.
#    Do not add one to make a seed pass. Resolve the ownership instead:
#    one loader DECLARES, every other loader REFERENCES (campaign D-29).
# ---------------------------------------------------------------------------
ACKNOWLEDGED: dict[str, tuple[tuple[str, ...], str]] = {
    # code: ((exact writer set acknowledged), note)
    # ⚠ The WRITER SET is part of the acknowledgement. A new module joining an
    #    existing collision is a NEW collision and the guard will refuse it.
    # --- writers DISAGREE: live last-writer-wins rows ----------------------
    "AL_CODE_40_18":             (('load_al_form20c.py', 'load_al_passthrough.py'), "differs: title,citation"),
    "GA_OCGA_48_7":              (('load_ga500_form_500.py', 'load_ga700.py'), "differs: source_type,source_rank,title,citation. PROVEN downgrade; load_ga500_form_500 is gated on this (D-38)."),
    "IRC_1402":                  (('load_1040_minister.py', 'load_1040_schedule_k1.py', 'load_1065_se.py'), "differs: title,citation,official_url"),
    "IRC_163J":                  (('load_1120_spine.py', 'load_8990.py'), "differs: title,citation"),
    "IRC_168":                   (('_1120s_sources.py', 'load_4797.py'), "differs: source_type,source_rank,title,citation,issuer,official_url"),
    "IRC_172":                   (('load_1040_form_172.py', 'load_1120_spine.py'), "differs: source_type,title,citation,official_url"),
    "IRC_1G":                    (('load_1040_form_8615.py', 'load_8814.py'), "differs: source_rank,title,citation"),
    "IRC_6654":                  (('load_1040_2210.py', 'load_1040_spine.py'), "differs: source_type,title,citation,issuer,official_url"),
    "IRC_702":                   (('load_1065_m1_m2.py', 'load_1065_schedule_k.py', 'load_1065_schedule_k1.py', 'load_1065_se.py'), "differs: title,citation"),
    "IRC_705":                   (('load_1065_l_b.py', 'load_1065_m1_m2.py', 'load_1065_schedule_k1.py'), "differs: title"),
    "IRS_2025_8283_INSTR":       (('load_1040_form_8283.py', 'load_1120s_complete.py'), "differs: title,citation,official_url"),
    "IRS_2025_8949_INSTR":       (('_1120s_sources.py', 'load_1040_schedule_d.py'), "differs: source_type,title,citation,official_url"),
    "IRS_2025_F1065":            (('load_1065_l_b.py', 'load_1065_m1_m2.py', 'load_1065_schedule_k.py'), "differs: title,citation"),
    "IRS_2025_F7206_INSTR":      (('load_1040_form_7206.py', 'load_1040_retirement.py'), "differs: source_type,citation"),
    "IRS_2025_I1065":            (('load_1065_l_b.py', 'load_1065_m1_m2.py', 'load_1065_schedule_k.py'), "differs: title,citation"),
    "IRS_PUB_544":               (('load_4797.py', 'load_8824.py'), "differs: official_url"),
    "NC_GS_105_CORP":            (('load_nc_cd405.py', 'load_nc_passthrough.py'), "differs: title,citation"),
    "RP_2024_40":                (('load_1040_spine.py', 'load_1041_spine.py'), "differs: source_type,title,citation,issuer"),
    "SC_2025_SC1120I":           (('load_sc1120.py', 'load_sc_passthrough.py'), "differs: source_type,title"),
    "SC_ACT63_2025_CONFORMITY":  (('load_sc1040.py', 'load_sc1120.py'), "differs: source_type,citation,official_url"),
    # --- writers AGREE today: benign, but still two writers ----------------
    "IRC_704":                   (('load_1065_schedule_k.py', 'load_1065_schedule_k1.py'), "identical today"),
    "IRC_707C":                  (('load_1065_schedule_k.py', 'load_1065_schedule_k1.py', 'load_1065_se.py'), "identical today"),
    "IRS_2025_F1120":            (('load_1120_schl.py', 'load_1120_spine.py'), "identical today"),
    "IRS_2025_I1120":            (('load_1120_schl.py', 'load_1120_spine.py'), "identical today"),
}


def _declarations_in(path: str) -> dict[str, dict]:
    """Literal AuthoritySource declarations in one module. Never raises."""
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


def scan(cmd_dir: str = CMD_DIR) -> tuple[dict[str, dict[str, dict]], int, int]:
    """-> ({source_code: {module: fields}}, modules_scanned, modules_parsed)."""
    decls: dict[str, dict[str, dict]] = {}
    paths = sorted(glob.glob(os.path.join(cmd_dir, "*.py")))
    parsed = 0
    for p in paths:
        found = _declarations_in(p)
        if found or os.path.getsize(p) == 0:
            parsed += 1
        for code, fields in found.items():
            decls.setdefault(code, {})[os.path.basename(p)] = fields
    return decls, len(paths), parsed


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


def guard(loader_name: str | None = None, write=None, raise_on_new=True):
    """Refuse UNACKNOWLEDGED collisions; report acknowledged ones.

    loader_name: restrict to collisions involving this module (pre-seed use).
                 None -> check the whole library (seed_all / CI use).
    """
    def emit(msg):
        if write is not None:
            write(msg)

    decls, n_files, _ = scan()
    found = collisions(decls)
    if loader_name:
        found = {c: v for c, v in found.items() if loader_name in v["writers"]}

    def is_acknowledged(code, writers):
        entry = ACKNOWLEDGED.get(code)
        # the acknowledgement is of a SPECIFIC collision, not of the code forever:
        # a module joining an existing collision is itself a new collision.
        return entry is not None and set(entry[0]) == set(writers)

    new = {c: v for c, v in found.items() if not is_acknowledged(c, v["writers"])}
    known = {c: v for c, v in found.items() if is_acknowledged(c, v["writers"])}

    emit("two-writers guard: %d modules scanned, %d authority codes declared, "
         "%d collisions (%d acknowledged, %d NEW)"
         % (n_files, len(decls), len(found), len(known), len(new)))
    for c, v in sorted(known.items()):
        emit("  ~ acknowledged %-26s %s%s"
             % (c, ", ".join(v["writers"]),
                ("  [differs: %s]" % ",".join(v["differs"])) if v["differs"] else "  [identical today]"))

    if new:
        lines = ["", "TWO-WRITERS GUARD: %d NEW authority collision(s)." % len(new), ""]
        for c, v in sorted(new.items()):
            lines.append("  %s" % c)
            lines.append("      declared by : %s" % ", ".join(v["writers"]))
            lines.append("      fields differ: %s" % (", ".join(v["differs"]) or "none (identical today)"))
        lines += [
            "",
            "Loaders write sources with update_or_create(defaults=...), so whichever of these",
            "runs LAST silently decides what production holds. That is campaign D-31's",
            "two-writers defect.",
            "",
            "FIX IT, do not acknowledge it: ONE loader DECLARES the source; every other loader",
            "REFERENCES it via EXISTING_SOURCES_TO_REFERENCE (campaign D-29). If the non-owner",
            "also contributes excerpts, re-home them rather than dropping them.",
            "",
            "Adding a code to _authority_guard.ACKNOWLEDGED to make this pass is a decision to",
            "ship a silent last-writer-wins row, and is Ken's call, not a workaround.",
        ]
        msg = "\n".join(lines)
        if raise_on_new:
            from django.core.management.base import CommandError
            raise CommandError(msg)
        emit(msg)
    return {"new": new, "acknowledged": known, "modules": n_files, "codes": len(decls)}


def selftest() -> bool:
    """Prove the guard FIRES on a synthetic collision.

    ⚠ Deliberately does NOT assert how many collisions exist today — that number
    changes the moment Ken resolves one, and a check pinned to current state goes
    red on success. This tests the MECHANISM.
    """
    fake = {
        "ZZ_SYNTHETIC_CODE": {
            "load_a.py": {"source_code": "ZZ_SYNTHETIC_CODE", "source_type": "statute",
                          "source_rank": "controlling", "title": "A"},
            "load_b.py": {"source_code": "ZZ_SYNTHETIC_CODE", "source_type": "regulation",
                          "source_rank": "primary_official", "title": "B"},
        },
        "ZZ_SOLE_WRITER": {
            "load_a.py": {"source_code": "ZZ_SOLE_WRITER", "source_type": "statute"},
        },
    }
    found = collisions(fake)
    ok = (
        "ZZ_SYNTHETIC_CODE" in found
        and "ZZ_SOLE_WRITER" not in found
        and set(found["ZZ_SYNTHETIC_CODE"]["differs"]) >= {"source_type", "source_rank", "title"}
        and "ZZ_SYNTHETIC_CODE" not in ACKNOWLEDGED
    )
    return bool(ok)
