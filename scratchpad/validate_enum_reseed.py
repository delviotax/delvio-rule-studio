# -*- coding: utf-8 -*-
"""Pre-flight / post-flight harness for the A2 enum-label re-seed (Ken, 2026-08-25).

    snapshot:  .venv/Scripts/python.exe scratchpad/validate_enum_reseed.py before
    compare :  .venv/Scripts/python.exe scratchpad/validate_enum_reseed.py after

Re-seeding a loader rewrites EVERY row it declares, not only the rows being corrected.
That is the blast radius, and the campaign's rule is to PROVE it rather than claim it:
snapshot every source each of the four loaders declares OR references, field by field,
plus its excerpt count and `updated_at`, and compare after.

⚠ `updated_at` is expected to move on rows the loader re-writes — `update_or_create`
touches them even when the values are identical. What must NOT move is CONTENT, and
above all not the content of rows these loaders merely REFERENCE.

READ-ONLY in both modes. It never writes to the database.
"""
from __future__ import annotations

import ast
import json
import os
import sys

import django

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
os.chdir(REPO)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from sources.models import AuthoritySource  # noqa: E402
from specs.management.commands import _authority_guard as G  # noqa: E402

LOADERS = ["load_al_40nr.py", "load_md_500.py", "load_ms_83105.py", "load_or_20.py"]
SNAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "enum_reseed_snapshot.json")

# The corrections Ken approved on 2026-08-25 — {source_code: {field: (from, to)}}.
INTENDED = {
    "AL_2025_BOOKLET_40NR":   {"source_type": ("state_instructions", "state_instruction")},
    "AL_2026_WH_TAX_TABLES":  {"source_type": ("state_instructions", "state_instruction")},
    "AL_40NR_IRS_2025_HANDOFF": {"source_type": ("federal_form", "official_form")},
    "MD_2025_CORP_BOOK":      {"source_type": ("official_instructions", "state_instruction")},
    "MD_AR_43":               {"source_type": ("state_guidance", "state_instruction"),
                               "source_rank": ("secondary_official", "implementation_official")},
    "MS_2025_BOOKLET_83_100": {"source_type": ("state_instructions", "state_instruction")},
    "OR_2025_FORM_OR20_INSTR": {"source_type": ("state_instructions", "state_instruction")},
}

FIELDS = ("source_type", "source_rank", "jurisdiction_code", "title", "citation",
          "issuer", "official_url", "current_status")


def _referenced(path):
    """EXISTING_SOURCES_TO_REFERENCE — handles ast.Assign AND ast.AnnAssign.

    ⚠ An earlier scan of mine handled only ast.Assign and returned a confident "0
    references" across 111 modules that use the annotated form. Both, always.
    """
    out = set()
    tree = ast.parse(open(path, encoding="utf-8").read())
    for node in ast.walk(tree):
        tgt = val = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            tgt, val = node.targets[0].id, node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            tgt, val = node.target.id, node.value
        if tgt == "EXISTING_SOURCES_TO_REFERENCE" and val is not None:
            for e in getattr(val, "elts", []):
                if isinstance(e, ast.Constant) and isinstance(e.value, str):
                    out.add(e.value)
    return out


def in_scope():
    """-> ({code: 'declared'|'referenced'}, per-loader detail)."""
    scope, detail = {}, {}
    for name in LOADERS:
        p = os.path.join(G.CMD_DIR, name)
        decl = set(G._declarations_in(p))
        ref = _referenced(p)
        detail[name] = {"declares": sorted(decl), "references": sorted(ref)}
        for c in decl:
            scope[c] = "declared"
        for c in ref:
            scope.setdefault(c, "referenced")
    return scope, detail


def capture():
    scope, detail = in_scope()
    rows = {}
    for r in AuthoritySource.objects.filter(source_code__in=list(scope)).prefetch_related("excerpts"):
        rows[r.source_code] = {
            **{f: getattr(r, f) for f in FIELDS},
            "excerpts": r.excerpts.count(),
            "updated_at": str(getattr(r, "updated_at", "")),
        }
    from specs.models import TaxForm
    return {"scope": scope, "detail": detail, "rows": rows,
            "form_count": TaxForm.objects.count(),
            "total_sources": AuthoritySource.objects.count()}


def show(state, label):
    print("%s: %d sources in scope (%d declared, %d referenced-only), %d present in prod"
          % (label, len(state["scope"]),
             sum(1 for v in state["scope"].values() if v == "declared"),
             sum(1 for v in state["scope"].values() if v == "referenced"),
             len(state["rows"])))
    print("   prod totals: %d forms, %d authority rows"
          % (state["form_count"], state["total_sources"]))
    missing = sorted(set(state["scope"]) - set(state["rows"]))
    if missing:
        print("   NOT IN PROD: %s" % missing)


def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else "before").lower()
    now = capture()
    if mode == "before":
        json.dump(now, open(SNAP, "w", encoding="utf-8"), indent=1, default=str)
        show(now, "BEFORE")
        print("\n   intended corrections: %d rows / %d field changes"
              % (len(INTENDED), sum(len(v) for v in INTENDED.values())))
        for c, ch in sorted(INTENDED.items()):
            row = now["rows"].get(c, {})
            for f, (frm, to) in ch.items():
                got = row.get(f)
                mark = "ok" if got == frm else "!! prod holds %r, expected %r" % (got, frm)
                print("      %-26s %-12s %-22s -> %-24s %s" % (c, f, frm, to, mark))
        print("\n   snapshot written: %s" % SNAP)
        return 0

    before = json.load(open(SNAP, encoding="utf-8"))
    show(before, "BEFORE")
    show(now, "AFTER ")
    print()
    ok = True

    # 1 — every intended change landed, and reads exactly the approved value
    print("1. the approved corrections landed")
    for c, ch in sorted(INTENDED.items()):
        for f, (_frm, to) in ch.items():
            got = now["rows"].get(c, {}).get(f)
            good = got == to
            ok &= good
            print("   %s %-26s %-12s -> %r" % ("PASS" if good else "FAIL", c, f, got))

    # 2 — NOTHING ELSE changed content, on any row in scope
    print("\n2. no unintended content change, across every row these loaders touch")
    unexpected = []
    for c in sorted(set(before["rows"]) | set(now["rows"])):
        b, a = before["rows"].get(c), now["rows"].get(c)
        if b is None or a is None:
            unexpected.append((c, "row appeared/disappeared", b, a))
            continue
        for f in FIELDS + ("excerpts",):
            if b.get(f) != a.get(f):
                intended = INTENDED.get(c, {}).get(f)
                if intended and str(a.get(f)) == intended[1]:
                    continue
                unexpected.append((c, f, b.get(f), a.get(f)))
    ok &= not unexpected
    print("   %s %d unintended difference(s)" % ("PASS" if not unexpected else "FAIL", len(unexpected)))
    for c, f, b, a in unexpected:
        print("      %-26s %-14s %r -> %r" % (c, f, b, a))

    # 3 — referenced-only rows must be untouched even in `updated_at`
    print("\n3. rows these loaders only REFERENCE were not written at all")
    touched = [c for c, kind in before["scope"].items()
               if kind == "referenced" and c in before["rows"] and c in now["rows"]
               and before["rows"][c]["updated_at"] != now["rows"][c]["updated_at"]]
    ok &= not touched
    print("   %s %d referenced-only row(s) had updated_at move" % ("PASS" if not touched else "FAIL", len(touched)))
    for c in touched:
        print("      %s" % c)

    # 4 — prod totals steady
    print("\n4. prod totals steady")
    for k in ("form_count", "total_sources"):
        good = before[k] == now[k]
        ok &= good
        print("   %s %-14s %d -> %d" % ("PASS" if good else "FAIL", k, before[k], now[k]))

    print("\n%s" % ("ALL CHECKS PASS" if ok else "*** FAILURES ABOVE ***"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
