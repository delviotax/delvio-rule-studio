# -*- coding: utf-8 -*-
"""SWEEP - preparer-editable facts that are actually DERIVED from other facts.

    .venv/Scripts/python.exe scratchpad/sweep_derived_inputs.py

Origin: campaign D-43. Ken removed the CTC/ODC column-(7) boxes because "there is not a
scenario where any of it's up to the tax preparer's discretion - the credit amount is
based on the facts in the return and that should control." This asks the same question of
every other form.

THE STRONGEST SIGNAL IS MECHANICAL, NOT LEXICAL:
    If a rule VALIDATES fact X against facts Y and Z, then X is DERIVABLE from Y and Z.
    That is precisely the shape D-43 removed - R-DEP-03 checked `dep_ctc_flag` against
    `dep_dob` and `tax_year`, which is a derivation written as a consistency check.
    A validation of an input against other inputs is a derivation with extra steps.

    Same for a DIAGNOSTIC whose condition names the fact alongside other facts: it is
    detecting a disagreement that could not arise if the value were computed.

Lexical signals (a name ending `_flag`, a note saying "preparer-asserted") are reported
too, but ranked BELOW the mechanical ones and NOT presented as findings. Keyword matching
on prose is not a method; this campaign has three separate records of it producing
confident wrong answers.

READ-ONLY. `ast` only - no Django, no database.

COVERAGE IS REPORTED, and the list-name variance is discovered rather than assumed: this
library names its fact lists FORM_FACTS in some loaders and F_FACTS in others, so a scan
hardcoded to one name would silently miss half the library. Any module-level list whose
elements carry `fact_key` counts.
"""
from __future__ import annotations

import ast
import collections
import os
import re
import sys

CMD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "specs", "management", "commands")

CONCLUSION_WORDS = ("qualif", "eligib", "_flag", "is_", "_applies", "_required", "_allowed",
                    "_exempt", "_subject_to", "_meets", "_passes", "_claimed")
ASSERTED_WORDS = ("preparer-asserted", "preparer asserted", "asserted",
                  "entered by the preparer", "user-entered")


def _lists_of(tree, key):
    """Every module-level list whose elements are dicts carrying `key`. Name-agnostic."""
    out = []
    for n in ast.walk(tree):
        t = v = None
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            t, v = n.targets[0].id, n.value
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            t, v = n.target.id, n.value
        if t is None or not isinstance(v, (ast.List, ast.Tuple)):
            continue
        rows = []
        for e in v.elts:
            if not isinstance(e, ast.Dict):
                continue
            d = {k.value: val for k, val in zip(e.keys, e.values) if isinstance(k, ast.Constant)}
            if key in d:
                rows.append(d)
        if rows:
            out.append((t, rows))
    return out


def _const(node):
    return node.value if isinstance(node, ast.Constant) else None


def _strs(node):
    return [e.value for e in getattr(node, "elts", []) if isinstance(e, ast.Constant)
            and isinstance(e.value, str)]


def _text(node):
    """Best-effort string for a note that may be a parenthesised concatenation."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if node is None:
        return ""
    return " ".join(n.value for n in ast.walk(node)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str))


def scan():
    modules = parsed = 0
    facts = {}
    findings = collections.defaultdict(list)
    for f in sorted(os.listdir(CMD)):
        if not f.endswith(".py") or f.startswith("_"):
            continue
        modules += 1
        try:
            tree = ast.parse(open(os.path.join(CMD, f), encoding="utf-8").read())
        except SyntaxError:
            continue
        parsed += 1

        fact_rows = [r for _, rows in _lists_of(tree, "fact_key") for r in rows]
        if not fact_rows:
            continue
        keys = set()
        for d in fact_rows:
            k = _const(d.get("fact_key"))
            if not k:
                continue
            keys.add(k)
            facts[(f, k)] = {"label": _const(d.get("label")) or "",
                             "notes": _text(d.get("notes")),
                             "type": _const(d.get("data_type")) or ""}

        # SIGNAL ZERO - the only one with real precision, added after A and B each
        # over-reported. THE LIBRARY ITSELF COMPUTES THIS VALUE SOMEWHERE.
        #
        # If a fact is declared as an INPUT here and appears as a rule OUTPUT anywhere in
        # the library, then the library has already decided it is computable - and is
        # simultaneously accepting it as something a preparer types. That is not an
        # inference about tax law; it is an internal contradiction in our own spec, and it
        # is checkable without reading a single instruction booklet.
        #
        # A and B below stay, but they are HINTS. Whether a value is derivable is a tax
        # question about whether the return's facts determine it - dep_full_time_student
        # sits in the same validation rule as dep_dob and is not derivable from anything.
        # No amount of pattern-matching settles that; only reading does.
        for _, rules in _lists_of(tree, "rule_id"):
            for r in rules:
                rid = _const(r.get("rule_id")) or "?"
                for k in set(_strs(r.get("outputs"))) & keys:
                    findings[(f, k)].append(
                        ("Z", "%s OUTPUTS it - the library computes this value and also "
                              "accepts it as an input" % rid))

        # SIGNAL A - a rule VALIDATES this fact against other facts.
        for _, rules in _lists_of(tree, "rule_id"):
            for r in rules:
                rid = _const(r.get("rule_id")) or "?"
                rtype = (_const(r.get("rule_type")) or "").lower()
                if rtype not in ("validation", "consistency", "classification"):
                    continue
                ins = set(_strs(r.get("inputs")))
                outs = set(_strs(r.get("outputs")))
                present = (ins & keys) - outs
                # TIGHTENED after the first run reported 791 candidates - which meant the
                # SIGNAL was wrong, not that there were 791 problems. "A validation rule
                # lists N facts" does not make each derivable from the others: it caught
                # seven manufacturer PIN numbers cross-referenced by one rule, and a
                # total-equals-sum-of-buckets reconciliation. A sweep that overclaims gets
                # ignored on its second run.
                #
                # What made dep_ctc_flag a real finding was narrower, and all three parts
                # matter: it was a BOOLEAN CONCLUSION, validated against INDEPENDENT DATA
                # of a different shape, and adjudicated elsewhere. So require:
                #   1. the fact is a boolean - a conclusion is a yes/no
                #   2. the rule also reads a NON-boolean fact - real underlying data, not a
                #      row of sibling flags checked against each other
                #   3. the fact is nobody's output - it is genuinely an input today
                for k in present:
                    if facts[(f, k)]["type"] != "boolean":
                        continue
                    data_companions = sorted(
                        c for c in present - {k}
                        if facts.get((f, c), {}).get("type") not in ("boolean", ""))
                    if data_companions:
                        findings[(f, k)].append(
                            ("A", "%s (%s) checks this BOOLEAN against data: %s"
                             % (rid, rtype, ", ".join(data_companions[:4]))))

        # SIGNAL B - a DIAGNOSTIC condition names it alongside other facts.
        for _, diags in _lists_of(tree, "diagnostic_id"):
            for d in diags:
                did = _const(d.get("diagnostic_id")) or "?"
                cond = _text(d.get("condition"))
                if not cond:
                    continue
                named = {k for k in keys if re.search(r"\b%s\b" % re.escape(k), cond)}
                if len(named) >= 2:
                    for k in named:
                        # Same tightening as signal A, for the same reason.
                        if facts[(f, k)]["type"] != "boolean":
                            continue
                        data = sorted(c for c in named - {k}
                                      if facts.get((f, c), {}).get("type") not in ("boolean", ""))
                        if data:
                            findings[(f, k)].append(
                                ("B", "%s cross-checks this BOOLEAN against data: %s"
                                 % (did, ", ".join(data[:3]))))

        # SIGNAL C - lexical only.
        for k in keys:
            meta = facts[(f, k)]
            blob = (meta["notes"] + " " + meta["label"]).lower()
            if any(w in blob for w in ASSERTED_WORDS):
                findings[(f, k)].append(("C", "self-documented: " + meta["notes"][:60]))
            if meta["type"] == "boolean" and any(w in k.lower() for w in CONCLUSION_WORDS):
                findings[(f, k)].append(("C", "named like a conclusion"))
    return modules, parsed, facts, findings


def main():
    modules, parsed, facts, findings = scan()
    print("COVERAGE: %d loader modules seen, %d parsed, %d declare facts, %d facts total"
          % (modules, parsed, len({m for m, _ in facts}), len(facts)))
    print("          fact lists found by SHAPE, not by name - this library uses both")
    print("          FORM_FACTS and F_FACTS, and a hardcoded scan would miss half of it.")
    print()

    def tier(reasons):
        kinds = {r[0] for r in reasons}
        if "Z" in kinds:
            return -1
        return 0 if "A" in kinds else (1 if "B" in kinds else 2)

    counts = collections.Counter(tier(v) for v in findings.values())
    print("CANDIDATES: %d   (Z self-contradiction %d | A %d | B %d | C lexical only %d)"
          % (len(findings), counts[-1], counts[0], counts[1], counts[2]))
    print()
    zrows = sorted(k for k, v in findings.items() if tier(v) == -1)
    print("=" * 96)
    print("TIER Z - THE LIBRARY COMPUTES IT AND ALSO ACCEPTS IT AS AN INPUT.")
    print("An internal contradiction in our own spec - checkable without reading a booklet.")
    print("=" * 96)
    if not zrows:
        print("  (none)")
    for mod, key in zrows:
        print("  %-38s %-26s %s" % (key, mod[:-3], facts[(mod, key)]["label"][:40]))
        for kind, detail in sorted(set(findings[(mod, key)])):
            if kind == "Z":
                print("        %s" % detail)
    print()

    for t, title in ((0, "TIER A - a rule VALIDATES it against other facts."
                         " A validation of an input against other inputs IS a derivation."),
                     (1, "TIER B - a DIAGNOSTIC cross-checks it against other facts.")):
        rows = sorted(k for k, v in findings.items() if tier(v) == t)
        print("=" * 96)
        print(title)
        print("=" * 96)
        if not rows:
            print("  (none)")
        for mod, key in rows:
            meta = facts[(mod, key)]
            print("  %-38s %-26s %s" % (key, mod[:-3], meta["label"][:40]))
            for kind, detail in sorted(set(findings[(mod, key)])):
                if kind in ("A", "B"):
                    print("        %s" % detail)
        print()

    rows = sorted(k for k, v in findings.items() if tier(v) == 2)
    print("=" * 96)
    print("TIER C - lexical only. Reported for completeness, NOT as findings.")
    print("=" * 96)
    by_mod = collections.Counter(mod for mod, _ in rows)
    print("  %d facts across %d modules. Heaviest:" % (len(rows), len(by_mod)))
    for mod, n in by_mod.most_common(8):
        print("     %-38s %d" % (mod[:-3], n))


if __name__ == "__main__":
    main()
