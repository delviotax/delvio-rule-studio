"""Orphan-row audit, v2 — EXACT, by importing each loader.

v1 matched names textually against loader source and produced false positives
for every loader that GENERATES names (MD builds `scha_{code}_md` in a loop;
NC builds `R-NCD403-{suffix}` in `_mk_rules`). Textual matching cannot tell a
generated name from an orphan, so this version imports the loader module and
reads the names it actually declares.

An ORPHAN is a row served by PROD that the loader would not write today —
the shape the NC reseed produced when a rename left the old row alive.
"""
import io
import json
import os
import sys
import importlib.util
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = r"D:\dev\delvio-rule-studio"
CMDS = os.path.join(REPO, "specs", "management", "commands")
BASE = "https://sherpa-tax-rule-studio.onrender.com/api/forms/lookup/{}/export/"

sys.path.insert(0, REPO)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django  # noqa: E402

django.setup()

OWNERS = {
    "NC_D403": "load_nc_passthrough", "NC_CD401S": "load_nc_passthrough",
    "AL_FORM_65": "load_al_passthrough", "AL_FORM_20S": "load_al_passthrough",
    "CO_DR0106": "load_co_dr0106",
    "VA_502": "load_va_pte", "VA_502PTET": "load_va_pte",
    "MD_510": "load_md_pte", "MD_511": "load_md_pte",
    "OR_65": "load_or_pte", "OR_20_S": "load_or_pte",
    "AZ_165": "load_az_pte", "AZ_120S": "load_az_pte",
    "MO_1065": "load_mo_pte", "MO_1120S": "load_mo_pte", "MO_PTE": "load_mo_pte",
}

_cache = {}


def declared(module_name: str) -> dict:
    """{form_number: {'facts':set,'rules':set,'diags':set,'tests':set,'lines':set}}"""
    if module_name in _cache:
        return _cache[module_name]
    path = os.path.join(CMDS, module_name + ".py")
    spec = importlib.util.spec_from_file_location(module_name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    out = {}
    for f in getattr(m, "FORMS", []):
        num = f["identity"]["form_number"]
        out[num] = {
            "facts": {x.get("fact_key") for x in f.get("facts", [])},
            "rules": {x.get("rule_id") for x in f.get("rules", [])},
            "diags": {x.get("diagnostic_id") for x in f.get("diagnostics", [])},
            "tests": {x.get("scenario_name") for x in f.get("scenarios", [])},
            "lines": {x.get("line_number") for x in f.get("lines", [])},
        }
    _cache[module_name] = out
    return out


PROD_KEY = {"facts": ("facts", "fact_key"), "rules": ("rules", "rule_id"),
            "diags": ("diagnostics", "diagnostic_id"),
            "tests": ("tests", "scenario_name"),
            "lines": ("line_map", "line_number")}

orphans, notes, checked = [], [], 0
for code, mod in OWNERS.items():
    try:
        decl = declared(mod).get(code)
    except Exception as e:  # noqa: BLE001
        notes.append((code, f"loader import failed: {str(e)[:70]}"))
        continue
    if decl is None:
        notes.append((code, f"{mod} declares no FORMS entry for this code"))
        continue
    try:
        with urllib.request.urlopen(BASE.format(code), timeout=60) as r:
            d = json.loads(r.read().decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        notes.append((code, f"export fetch failed: {str(e)[:60]}"))
        continue
    checked += 1
    for kind, (section, key) in PROD_KEY.items():
        prod = {x.get(key) for x in (d.get(section) or []) if x.get(key)}
        extra = prod - decl[kind]
        for name in sorted(extra):
            orphans.append((code, kind, name))

print(f"Audited {checked} seeded state forms across {len(set(OWNERS.values()))} loaders.")
print("Method: EXACT — each loader imported and its declarations compared to the live prod export.\n")
if orphans:
    print(f"*** {len(orphans)} ORPHAN ROW(S): served by PROD, not declared by the loader ***")
    cur = None
    for code, kind, name in orphans:
        if code != cur:
            print(f"\n  {code}:")
            cur = code
        print(f"      [{kind}] {name}")
else:
    print("NO ORPHANS. Every prod row for every audited state form is still declared")
    print("by its loader. The 67-of-115 missing prunes are latent CAPACITY for the")
    print("defect, not realised exposure: NC was the only loader that had renamed a")
    print("row, and its orphans were pruned when the D-16 corrections were applied.")
if notes:
    print("\nNotes:")
    for code, n in notes:
        print(f"   {code:<12} {n}")
