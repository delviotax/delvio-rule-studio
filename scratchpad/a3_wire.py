# -*- coding: utf-8 -*-
"""Wire `_authority_wiring` into every loader that needs it (campaign D-42, Ken's go).

    census : .venv/Scripts/python.exe scratchpad/a3_wire.py census
    apply  : .venv/Scripts/python.exe scratchpad/a3_wire.py apply
    verify : .venv/Scripts/python.exe scratchpad/a3_wire.py verify

Two populations, one fix:
  A — the list is DEFINED and NEVER READ (18 loaders). A trap: an entry would silently
      do nothing. ⚠ All eighteen were EMPTY when measured, so nothing is being dropped
      today; the defect is latent, not active.
  B — the list is ABSENT in a loader that A3 needs to convert. The machinery has to be
      added before its declaration can become a reference.

⭐ SAFE BY CONSTRUCTION: added lists are empty and wired lists were empty, so every edit
iterates nothing. Behaviour-neutral until someone adds an entry — which is the point.
No re-seed is required to land it.
"""
from __future__ import annotations

import ast
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
os.chdir(REPO)
CMD = os.path.join(REPO, "specs", "management", "commands")
SNAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "a3_wire_snapshot.json")

NAMES = ("EXISTING_SOURCES_TO_REFERENCE", "NEW_EXCERPTS_ON_EXISTING")
DECL = {"EXISTING_SOURCES_TO_REFERENCE": "EXISTING_SOURCES_TO_REFERENCE: list[str] = []",
        "NEW_EXCERPTS_ON_EXISTING": "NEW_EXCERPTS_ON_EXISTING: list[tuple[str, dict]] = []"}

# Loaders A3 still needs to convert, whose machinery is missing entirely.
# ⚠ DELIBERATE removals, declared so the verifier still catches UNintended ones.
# These two loaders have no `sources` dict — they resolve every code directly at the
# point of use — so their reference list was read by nothing and adding a code to it
# would have done nothing. Deleted rather than wired; every code still appears where
# it is actually used.
INTENDED_REMOVALS = {("load_4562_destination_rounding.py", "EXISTING_SOURCES_TO_REFERENCE"),
                     ("load_4562_section179_carryover.py", "EXISTING_SOURCES_TO_REFERENCE")}

POP_B = ["load_1065_schedule_k1.py", "load_1065_schedule_k.py", "load_1065_se.py",
         "load_1065_m1_m2.py", "load_1065_l_b.py", "load_1120_spine.py",
         "load_1041_spine.py", "load_1120s_complete.py", "load_remaining_1120s.py",
         "load_sc1120.py", "load_6765.py", "load_4684.py", "load_nc_passthrough.py"]


def module_state(path):
    """-> (defined:set, read:set, list_lengths:dict)."""
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    defined, read, lengths = set(), set(), {}
    for n in ast.walk(tree):
        t = v = None
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            t, v = n.targets[0].id, n.value
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            t, v = n.target.id, n.value
        if t in NAMES:
            defined.add(t)
            lengths[t] = len(getattr(v, "elts", []) or [])
        if isinstance(n, ast.Name) and n.id in NAMES and isinstance(n.ctx, ast.Load):
            read.add(n.id)
    return defined, read, lengths


def needs():
    """-> {module: {name: 'wire'|'add+wire'}} for every module needing work."""
    out = {}
    for f in sorted(os.listdir(CMD)):
        if not f.endswith(".py") or f.startswith("_authority") or f.startswith("_enum"):
            continue
        p = os.path.join(CMD, f)
        try:
            defined, read, _ = module_state(p)
        except SyntaxError:
            continue
        work = {}
        for nm in NAMES:
            if nm in defined and nm not in read:
                work[nm] = "wire"
            elif nm not in defined and f in POP_B:
                work[nm] = "add+wire"
        if work:
            out[f] = work
    return out


def _anchor(src):
    """Insert point: just before the loader announces its source count and returns."""
    m = re.search(r"^([ \t]+)self\.stdout\.write\(f?\"\s*Sources ready:.*\n", src, re.M)
    if m:
        return m.start(), m.group(1)
    m = re.search(r"^([ \t]+)return sources\s*$", src, re.M)
    return (m.start(), m.group(1)) if m else (None, None)


def apply_one(path, work):
    src = open(path, encoding="utf-8").read()
    orig = src

    # 1 — add any missing list, immediately after AUTHORITY_SOURCES ends
    for nm, mode in sorted(work.items()):
        if mode != "add+wire":
            continue
        tree = ast.parse(src)
        other = None
        for n in ast.walk(tree):
            t = None
            if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                t = n.targets[0].id
            elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
                t = n.target.id
            # ⚠ FRESH_SOURCES is the same thing under a different name in the 1120-S loaders.
            #   Anchoring only on AUTHORITY_SOURCES skipped them — a name-based scan that
            #   misses a synonym is the day's recurring defect in miniature.
            if t in ("AUTHORITY_SOURCES", "FRESH_SOURCES",
                     "EXISTING_SOURCES_TO_REFERENCE", "NEW_EXCERPTS_ON_EXISTING"):
                if other is None or n.end_lineno > other.end_lineno:
                    other = n
        if other is None:
            return {"status": "SKIPPED — no AUTHORITY_SOURCES anchor"}
        lines = src.splitlines(keepends=True)
        pos = sum(len(l) for l in lines[:other.end_lineno])
        src = src[:pos] + "\n# Added 2026-08-25 (campaign D-42) so the D-29 ownership remedy is\n" \
                          "# available here. Empty: adding it changes nothing until an entry lands.\n" \
              + DECL[nm] + "\n" + src[pos:]

    # 2 — import the shared helper
    if "_authority_wiring" not in src:
        m = re.search(r"^from django\.core\.management\.base import .*$", src, re.M) or \
            re.search(r"^from django\.db import .*$", src, re.M)
        if not m:
            return {"status": "SKIPPED — no import anchor"}
        src = src[:m.end()] + "\n\nfrom . import _authority_wiring as _wire" + src[m.end():]

    # 3 — call the helper where the sources dict is complete
    pos, indent = _anchor(src)
    if pos is None:
        return {"status": "SKIPPED — no source-loading anchor"}
    call = ("%s# ⚠ D-42: these two lists existed and were NEVER READ. One module DECLARES a\n"
            "%s#   source, every other REFERENCES it (D-29) — that only works if both halves run.\n" % (indent, indent))
    for nm in sorted(set(work) | {n for n in NAMES if n in src}):
        if nm == "EXISTING_SOURCES_TO_REFERENCE" and nm in src:
            call += "%s_wire.resolve_references(EXISTING_SOURCES_TO_REFERENCE, sources, self.stdout.write)\n" % indent
        if nm == "NEW_EXCERPTS_ON_EXISTING" and nm in src:
            call += "%s_wire.apply_new_excerpts(NEW_EXCERPTS_ON_EXISTING, sources, self.stdout.write)\n" % indent
    if "_wire.resolve_references" in src or "_wire.apply_new_excerpts" in src:
        return {"status": "already wired"}
    src = src[:pos] + call + src[pos:]

    ast.parse(src)                                   # never write something unparseable
    if src != orig:
        open(path, "w", encoding="utf-8", newline="").write(src)
    return {"status": "wired", "lists": sorted(work)}


def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else "census").lower()
    work = needs()

    if mode == "census":
        snap = {}
        for f in sorted(work):
            defined, read, lengths = module_state(os.path.join(CMD, f))
            snap[f] = {"work": work[f], "lengths": lengths}
            print("   %-38s %s   lengths=%s" % (f, work[f], lengths or "{}"))
        json.dump(snap, open(SNAP, "w", encoding="utf-8"), indent=1)
        nonempty = {f: v["lengths"] for f, v in snap.items()
                    if any(n for n in v["lengths"].values())}
        print("\n   modules needing work: %d" % len(work))
        print("   ⚠ any NON-EMPTY list among them (would make wiring behaviour-CHANGING): %s"
              % (nonempty or "none — every edit is behaviour-neutral"))
        return 0

    if mode == "apply":
        for f in sorted(work):
            r = apply_one(os.path.join(CMD, f), work[f])
            print("   %-38s %s" % (f, r["status"]))
        return 0

    # verify
    ok = True
    left = needs()
    print("A3 WIRE VERIFY")
    print("   modules still unwired: %d %s" % (len(left), sorted(left) or ""))
    ok &= not left
    # ⚠ SEPARATE verdict. The first version reused `ok`, so this line printed FAIL
    #   because 4 modules were still unwired — a check contaminated by an earlier one,
    #   which is worse than no check: it reports a problem that is not there and hides
    #   whether the real one is.
    contents_ok = True
    before = json.load(open(SNAP, encoding="utf-8"))
    for f, v in sorted(before.items()):
        _d, _r, lengths = module_state(os.path.join(CMD, f))
        for nm, n in v["lengths"].items():
            now = lengths.get(nm, 0)
            if (f, nm) in INTENDED_REMOVALS:
                print("   ok   %s %s removed deliberately (%d -> gone)" % (f, nm, n))
                continue
            if now != n:
                contents_ok = False
                print("   FAIL %s %s length %d -> %d (wiring must not change contents)" % (f, nm, n, now))
    ok &= contents_ok
    print("   list contents unchanged by the wiring: %s" % ("PASS" if contents_ok else "FAIL"))
    print("\n%s" % ("ALL WIRED, BEHAVIOUR-NEUTRAL" if ok else "*** PROBLEMS ABOVE ***"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
