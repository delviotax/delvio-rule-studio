# -*- coding: utf-8 -*-
"""A3 — convert a NON-OWNER's AuthoritySource declaration into a REFERENCE (campaign D-29).

    plan   : .venv/Scripts/python.exe scratchpad/a3_convert.py plan
    apply  : .venv/Scripts/python.exe scratchpad/a3_convert.py apply
    verify : .venv/Scripts/python.exe scratchpad/a3_convert.py verify

⭐ THE INVARIANT this is built around, and the only reason a mechanical edit is safe here:

    for every module, the set of authority codes it declares-OR-references, and the set of
    (code, excerpt_label) pairs it contributes, must be IDENTICAL before and after.

A conversion moves WHERE a contribution is expressed, never WHETHER it is expressed. If the
invariant holds, the loader seeds exactly the same excerpts by a different route, and stops
rewriting a row it does not own.

⚠ Only conversions whose losing module actually READS both `EXISTING_SOURCES_TO_REFERENCE`
and `NEW_EXCERPTS_ON_EXISTING` are attempted. 25 of the 45 cannot be applied today because
their loader never reads those lists — converting there would silently drop the link and the
excerpt, which is the exact failure D-38 caught on GA-500. Those are reported, not forced.

⚠ NOTHING IS SEEDED. Ken's A3 ruling is ownership-only: prod content is untouched, and the
conversions take effect the next time each loader is seeded for its own reasons.
"""
from __future__ import annotations

import ast
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
os.chdir(REPO)

CMD = os.path.join(REPO, "specs", "management", "commands")
SNAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "a3_contribution_snapshot.json")

# (loser module basename, source_code, owner label) — from a3_feasible.py, generated not typed.
CONVERSIONS = [
    # ── A3-ii, 2026-08-25 — the 16 the objective criteria could not decide.
    #
    # ⭐ THEY RESOLVE ON ONE PRINCIPLE, NOT SIXTEEN RULINGS:
    #    A SOURCE ROW DESCRIBES A DOCUMENT. The consumer's SLICE of that document
    #    belongs in its EXCERPT, which is per-consumer by design. Every one of these
    #    disagreements is a writer having put its own slice into the shared row -
    #    IRC §168's citation varying by which subsections a loader cites, Form 1065's
    #    title varying by which schedule it cares about. The writer whose title and
    #    citation describe the WHOLE DOCUMENT owns it; the slice-writers reference it
    #    and keep their slice where it always belonged.
    #
    # ⭐ AND ONE STRUCTURAL CALL settles six of them: specs/_1120s_sources.py and
    #    sources/load_1120s_family.py are two halves of one intent. The sources app
    #    runs in seed_all PHASE 1, before every specs loader - which is the dependency
    #    order the whole library already uses. The sources side owns.
    ("load_1040_spine.py", "IRC_1", "federal_data/irc_sections.py"),
    ("load_1040_sch123.py", "IRC_62", "federal_data/irc_sections.py"),
    ("load_sch_1a.py", "IRC_163", "federal_data/irc_sections.py"),
    ("load_1120_spine.py", "IRC_163J", "specs/load_8990.py"),
    ("load_8814.py", "IRC_1G", "specs/load_1040_form_8615.py"),
    ("load_4797.py", "IRC_168", "sources/load_1120s_family.py"),
    ("load_1040_schedule_d.py", "IRS_2025_8949_INSTR", "sources/load_1120s_family.py"),
    ("load_4797.py", "IRS_PUB_544", "specs/load_8824.py"),
    ("load_1065_schedule_k1.py", "IRC_707C", "specs/load_1065_schedule_k.py"),
    ("load_1065_se.py", "IRC_707C", "specs/load_1065_schedule_k.py"),
    ("load_1120_schl.py", "IRS_2025_F1120", "specs/load_1120_spine.py"),
    ("load_1120_schl.py", "IRS_2025_I1120", "specs/load_1120_spine.py"),
]


# ---------------------------------------------------------------------------
def parse(path):
    return ast.parse(open(path, encoding="utf-8").read())


def contribution(path):
    """-> {code: sorted[excerpt_label]} for everything this module CONTRIBUTES,
    by either route. THE invariant's subject."""
    out = {}
    tree = parse(path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            d = {k.value: v for k, v in zip(node.keys, node.values) if isinstance(k, ast.Constant)}
            sc, st = d.get("source_code"), d.get("source_type")
            if isinstance(sc, ast.Constant) and st is not None:
                labels = []
                for e in getattr(d.get("excerpts"), "elts", []) or []:
                    ed = {k.value: v for k, v in zip(e.keys, e.values) if isinstance(k, ast.Constant)}
                    lb = ed.get("excerpt_label")
                    labels.append(lb.value if isinstance(lb, ast.Constant) else "<expr>")
                out.setdefault(sc.value, []).extend(labels)
        tgt = val = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            tgt, val = node.targets[0].id, node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            tgt, val = node.target.id, node.value
        if tgt == "EXISTING_SOURCES_TO_REFERENCE" and val is not None:
            for e in getattr(val, "elts", []):
                if isinstance(e, ast.Constant):
                    out.setdefault(e.value, [])
        if tgt == "NEW_EXCERPTS_ON_EXISTING" and val is not None:
            for e in getattr(val, "elts", []):
                els = getattr(e, "elts", None)
                if not els or not isinstance(els[0], ast.Constant):
                    continue
                code = els[0].value
                ed = {k.value: v for k, v in zip(els[1].keys, els[1].values) if isinstance(k, ast.Constant)}
                lb = ed.get("excerpt_label")
                out.setdefault(code, []).append(lb.value if isinstance(lb, ast.Constant) else "<expr>")
    return {k: sorted(v) for k, v in out.items()}


def snapshot():
    return {f: contribution(os.path.join(CMD, f))
            for f in sorted({m for m, _, _ in CONVERSIONS})}


def _span(src, node):
    lines = src.splitlines(keepends=True)
    start = sum(len(l) for l in lines[:node.lineno - 1]) + node.col_offset
    end = sum(len(l) for l in lines[:node.end_lineno - 1]) + node.end_col_offset
    return start, end


def _find_decl(tree, code):
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        d = {k.value: v for k, v in zip(node.keys, node.values) if isinstance(k, ast.Constant)}
        sc, st = d.get("source_code"), d.get("source_type")
        if isinstance(sc, ast.Constant) and sc.value == code and st is not None:
            return node, d
    return None, None


def _find_list(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
                isinstance(node.targets[0], ast.Name) and node.targets[0].id == name:
            return node.value
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and \
                node.target.id == name:
            return node.value
    return None


def convert_one(path, code, owner):
    """Apply ONE conversion to one file. Returns a summary dict."""
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    decl, d = _find_decl(tree, code)
    if decl is None:
        return {"code": code, "status": "already converted (no declaration found)"}

    excerpt_nodes = getattr(d.get("excerpts"), "elts", []) or []
    excerpt_src = [src[slice(*_span(src, e))] for e in excerpt_nodes]
    topics = [t.value for t in getattr(d.get("topics"), "elts", []) or []
              if isinstance(t, ast.Constant)]

    ref_list = _find_list(tree, "EXISTING_SOURCES_TO_REFERENCE")
    exc_list = _find_list(tree, "NEW_EXCERPTS_ON_EXISTING")
    if ref_list is None or (excerpt_src and exc_list is None):
        return {"code": code, "status": "BLOCKED — module lacks the target list(s)"}

    note = ('  # ownership -> %s (A3/D-42, 2026-08-25)' % owner.split("/")[-1])
    edits = []                                     # (start, end, replacement)

    # 1 — excerpts move to NEW_EXCERPTS_ON_EXISTING
    if excerpt_src:
        ins = _span(src, exc_list)[1] - 1          # just before the closing ']'
        block = ("    # Re-homed 2026-08-25 (campaign A3/D-42): %s is DECLARED by %s.\n"
                 "    # This spec still contributes these excerpts; it no longer rewrites the row.\n"
                 % (code, owner.split("/")[-1]))
        for e in excerpt_src:
            body = "\n".join("    " + l if l.strip() else l for l in e.splitlines())
            block += '    ("%s", %s),\n' % (code, body.lstrip())
        edits.append((ins, ins, block))

    # 2 — the code joins EXISTING_SOURCES_TO_REFERENCE
    ins = _span(src, ref_list)[1] - 1
    edits.append((ins, ins, '    "%s",%s\n' % (code, note)))

    # 3 — the declaration itself is removed, trailing comma and all
    s, e = _span(src, decl)
    while e < len(src) and src[e] in ", ":
        e += 1
    while e < len(src) and src[e] == "\n":
        e += 1
        break
    while s > 0 and src[s - 1] in " \t":
        s -= 1
    edits.append((s, e, ""))

    for start, end, rep in sorted(edits, key=lambda t: -t[0]):
        src = src[:start] + rep + src[end:]
    ast.parse(src)                                  # refuse to write anything unparseable
    open(path, "w", encoding="utf-8", newline="").write(src)
    return {"code": code, "status": "converted", "excerpts": len(excerpt_src), "topics": topics}


def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else "plan").lower()

    if mode == "plan":
        json.dump(snapshot(), open(SNAP, "w", encoding="utf-8"), indent=1)
        print("A3 PLAN — %d conversions across %d modules"
              % (len(CONVERSIONS), len({m for m, _, _ in CONVERSIONS})))
        for m, c, o in CONVERSIONS:
            print("   %-30s %-26s -> declared by %s" % (m, c, o.split("/")[-1]))
        print("\nsnapshot written: %s" % SNAP)
        return 0

    if mode == "apply":
        for m, c, o in CONVERSIONS:
            r = convert_one(os.path.join(CMD, m), c, o)
            print("   %-30s %-26s %s%s" % (m, c, r["status"],
                  ("  (%d excerpt(s) re-homed)" % r["excerpts"]) if r.get("excerpts") else ""))
        return 0

    # verify
    before = json.load(open(SNAP, encoding="utf-8"))
    after = snapshot()
    ok = True
    print("A3 VERIFY — the invariant: each module contributes exactly what it did before")
    for m in sorted(before):
        b, a = before[m], after[m]
        lost_codes = sorted(set(b) - set(a))
        new_codes = sorted(set(a) - set(b))
        bad = []
        for code in sorted(set(b) & set(a)):
            if b[code] != a[code]:
                bad.append((code, b[code], a[code]))
        good = not (lost_codes or new_codes or bad)
        ok &= good
        print("   %s %-30s %d codes, %d excerpt contributions"
              % ("PASS" if good else "FAIL", m, len(a), sum(len(v) for v in a.values())))
        for c in lost_codes:
            print("        LOST code       %s (%s)" % (c, b[c]))
        for c in new_codes:
            print("        UNEXPECTED code %s" % c)
        for c, bb, aa in bad:
            print("        EXCERPTS MOVED  %s: %s -> %s" % (c, bb, aa))
    print("\n%s" % ("INVARIANT HOLDS" if ok else "*** INVARIANT VIOLATED ***"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
