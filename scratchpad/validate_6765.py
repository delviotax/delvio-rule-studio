"""Throwaway SQLite validation for load_6765.py (WO-14, 2026-08-04).

Two legs:
  1. ARITHMETIC ORACLES — every scenario recomputed through the loader's own
     pure helpers (regular_credit / asc_credit / section_c_credit / qre_total)
     against independently hand-derived expected values.
  2. SEED DRY-RUN — the loader run against a throwaway SQLite DB (guard
     temporarily bypassed IN MEMORY ONLY) to prove every block upserts clean
     (CharField caps, choice values, FK integrity) before prod Supabase.

Run:  poetry run python scratchpad/validate_6765.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
os.environ["SQLITE_VALIDATE"] = "1"

import django  # noqa: E402

# Throwaway SQLite before setup.
from django.conf import settings  # noqa: E402

SQLITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "validate_6765.sqlite3")


def main():
    django.setup()
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3", "NAME": SQLITE_PATH,
        "ATOMIC_REQUESTS": False, "AUTOCOMMIT": True, "CONN_MAX_AGE": 0,
        "OPTIONS": {}, "TIME_ZONE": None, "CONN_HEALTH_CHECKS": False,
        "HOST": "", "PORT": "", "USER": "", "PASSWORD": "", "TEST": {},
    }
    from django.db import connections
    connections.databases["default"] = settings.DATABASES["default"]

    passes, fails = [], []

    def check(name, got, want):
        if got == want:
            passes.append(name)
        else:
            fails.append(f"{name}: got {got!r}, want {want!r}")

    # ── Leg 1 — arithmetic oracles ─────────────────────────────────────────
    from specs.management.commands.load_6765 import (
        asc_credit, qre_total, regular_credit, section_c_credit,
    )

    # T1 — packet 227 shape (ASC, no 280C; inferred priors)
    qre = qre_total(53704, 0, 0, 0, 0)
    check("T1 line 48", qre, 53704)
    c = asc_credit(0, 0, 0, qre, 140382, True, False)
    check("T1 line 26", c, 4243)
    check("T1 line 30", section_c_credit(c, 0, 0), 4243)
    # hand-oracle: L22 = 140382/6 = 23397; L23 = 30307; 0.14×30307 = 4242.98 → 4243

    # T2 — first-year 6% path
    check("T2 line 26", asc_credit(0, 0, 0, 53704, 0, False, False), 3222)
    # 0.06 × 53704 = 3222.24 → 3222

    # T3 — regular credit, 280C elected
    check("T3 line 13", regular_credit(0, 0, 0, 250000, 0.05, 2000000, True), 19750)
    # L8 = 100000; L9 = 150000; L10 = 125000; L11 = 125000; 0.158×125000 = 19750

    # T4 — ASC with 280C ×0.79
    check("T4 line 26", asc_credit(0, 0, 0, 53704, 140382, True, True), 3352)
    # 4242.98 × 0.79 = 3351.95… hand-check: 0.14×30307 = 4242.98; ×0.79 = 3351.9542 → 3352

    # T5 — Section C composition
    c5 = asc_credit(0, 0, 0, 53704, 140382, True, False)
    check("T5 line 28+30", section_c_credit(c5, 500, 1000), 4743)

    # T6 — the 50%-of-QREs limit binds
    check("T6 line 13", regular_credit(0, 0, 0, 100000, 0.03, 200000, False), 10000)
    # L8 = 6000; L9 = 94000; L10 = 50000; L11 = 50000; ×0.20 = 10000

    # FBP cap: 20% keyed caps to 16%
    check("FBP cap", regular_credit(0, 0, 0, 100000, 0.20, 500000, False),
          round(min(max(0.0, 100000 - 500000 * 0.16), 50000) * 0.20))
    # L8 = 80000; L9 = 20000; L10 = 50000; L11 = 20000; L13 = 4000

    # Basic research + energy consortia ride both methods
    check("REG basic research", regular_credit(1000, 5000, 2000, 0, 0.03, 0, False),
          round((1000 + 3000 + 0) * 0.20))     # L12 = 1000+3000 → 800
    check("ASC basic research", asc_credit(1000, 5000, 2000, 0, 0, False, False),
          round((1000 + 3000) * 0.20))          # L19 = 800; L24 = 0

    # ── Leg 2 — SQLite seed dry-run ────────────────────────────────────────
    from django.core.management import call_command

    call_command("migrate", "--run-syncdb", verbosity=0)

    import specs.management.commands.load_6765 as loader
    loader.READY_TO_SEED = True  # in-memory only; the file stays False
    try:
        call_command("load_6765")
        passes.append("SQLite seed: loader ran clean")
    except Exception as exc:  # noqa: BLE001
        fails.append(f"SQLite seed FAILED: {exc}")

    from specs.models import (
        FlowAssertion, FormDiagnostic, FormFact, FormLine, FormRule, TaxForm,
        TestScenario,
    )
    form = TaxForm.objects.filter(form_number="6765").first()
    if form is None:
        fails.append("TaxForm 6765 missing after seed")
    else:
        check("facts", FormFact.objects.filter(tax_form=form).count(), 24)
        check("rules", FormRule.objects.filter(tax_form=form).count(), 7)
        check("lines", FormLine.objects.filter(tax_form=form).count(), 50)
        check("diagnostics", FormDiagnostic.objects.filter(tax_form=form).count(), 10)
        check("scenarios", TestScenario.objects.filter(tax_form=form).count(), 6)
        check("flow assertions", FlowAssertion.objects.filter(
            assertion_id__startswith="FA-6765").count(), 2)
        uncited = [r.rule_id for r in FormRule.objects.filter(tax_form=form)
                   if not r.authority_links.exists()]
        check("uncited rules", uncited, [])

    print(f"\n{'='*60}\nPASS {len(passes)} / FAIL {len(fails)}")
    for f in fails:
        print("  FAIL:", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
