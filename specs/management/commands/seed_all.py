"""Canonical full-rebuild orchestrator — runs every loader in dependency order.

This is the single command that reconstructs the entire RS spec database from the
loaders in source control. It exists because the individual `load_*` commands have
ordering dependencies (authority sources before forms; base forms before AMEND
loaders; flow assertions after all forms) that were previously tribal knowledge —
there was no one entrypoint, so a fresh DB could not be rebuilt reproducibly.

Phases:
  1. Sources    — feeds/topics + federal authority sources (forms reference these)
  2. Specs      — every specs `load_*` loader (forms/rules/lines/diagnostics/scenarios)
  3. Amends     — loaders that MUTATE a pre-existing base spec (must run after step 2)
  4. Flow       — flow assertions (reference forms across the whole DB)
  5. Approve    — apply the source-controlled approval manifest (draft -> approved)

Loaders are discovered dynamically, so new `load_*` commands are picked up
automatically. AMEND loaders and non-seed commands are listed explicitly below.

Idempotent: every loader uses update_or_create, so re-running is safe. NOTE this
brings a stale DB UP to the loaders (adds missing rules) but does NOT delete
orphaned rows left by refactored loaders — see reconstructability_check.md.

Usage:
  poetry run python manage.py seed_all            # run it
  poetry run python manage.py seed_all --dry-run  # print the plan only
"""
from django.core.management import call_command, get_commands
from django.core.management.base import BaseCommand, CommandError

from ._authority_guard import guard as authority_guard, selftest_report as authority_selftest_report

# Loaders that amend an existing base spec and must run AFTER all base forms exist.
# load_1120s_full amends SCH_K_1120S / SCHD_1120S (adds R010-R018 / R010-R012) — it must run
# after load_1120s_specs creates those bases, else it skips (its .first() lookup returns None)
# and the flow-detail rules are silently dropped on a fresh rebuild (2026-07-05 delta audit).
# load_state_conformity writes the JurisdictionConformitySource spine and anchors each row to an
# AuthoritySource seeded by that state's own form loader — so it must run after phase 2, same as
# a true amend loader (else the FK anchors resolve to None on a fresh rebuild).
AMEND_LOADERS = ["load_1040_form_3800", "load_1120s_full", "load_state_conformity"]

# specs commands that are NOT part of the specs-loader phase (they run in their own phases).
NON_SEED = {
    "export_flow_assertions", "seed_flow_assertions", "seed_all", "approve_specs", *AMEND_LOADERS,
}

# Phase 1 (sources app), phase 4 (flow assertions), phase 5 (approval) — explicit, order matters.
SOURCE_LOADERS = ["seed_sources", "load_all_federal", "load_1120s_family"]
FLOW_LOADERS = ["seed_flow_assertions"]
APPROVE_LOADERS = ["approve_specs"]


class Command(BaseCommand):
    help = "Reconstruct the entire RS spec DB from loaders, in dependency order."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Print the ordered loader plan without running anything.",
        )

    def handle(self, *_args, **opts):
        # ── THE TWO-WRITERS GUARD (campaign D-31 / D-38) ──────────────────────
        # Loaders write authority rows with update_or_create(defaults=...), so if two
        # of them declare the same source_code the LAST one to run silently decides
        # what production holds. seed_all runs them all, in order, so it is exactly
        # where an unnoticed collision does its damage. Refuse before writing anything.
        # ⚠ A1 (2026-08-25): the selftest now also proves the guard's SCOPE — that all
        #   three writer populations are actually being read. The pre-A1 guard passed
        #   its own selftest while blind to two of them, because a synthetic fixture
        #   proves the MATCHING works and says nothing about what is being matched.
        _ok, _why = authority_selftest_report()
        if not _ok:
            raise CommandError(
                "the two-writers guard's own selftest FAILED, so its all-clear would mean "
                "nothing. Refusing to seed.\n    " + "\n    ".join(_why)
            )
        authority_guard(write=self.stdout.write, raise_on_new=True)

        registered = get_commands()
        specs_loaders = sorted(
            name
            for name, app in registered.items()
            if app == "specs" and name.startswith("load_") and name not in NON_SEED
        )

        plan = [
            ("1. sources", SOURCE_LOADERS),
            (f"2. specs ({len(specs_loaders)})", specs_loaders),
            ("3. amends", AMEND_LOADERS),
            ("4. flow assertions", FLOW_LOADERS),
            ("5. approve", APPROVE_LOADERS),
        ]

        if opts["dry_run"]:
            self.stdout.write(self.style.MIGRATE_HEADING("seed_all plan (dry run):"))
            for phase, cmds in plan:
                self.stdout.write(f"  {phase}")
                for c in cmds:
                    mark = "" if c in registered else "   [MISSING]"
                    self.stdout.write(f"      - {c}{mark}")
            return

        ran, failed = 0, []
        for phase, cmds in plan:
            self.stdout.write(self.style.MIGRATE_HEADING(f"=== Phase {phase} ==="))
            for c in cmds:
                if c not in registered:
                    failed.append((c, "not registered"))
                    self.stdout.write(self.style.ERROR(f"  [MISSING] {c}"))
                    continue
                try:
                    call_command(c)
                    ran += 1
                    self.stdout.write(self.style.SUCCESS(f"  [OK] {c}"))
                except Exception as e:  # noqa: BLE001 — report, keep going
                    failed.append((c, f"{type(e).__name__}: {e}"))
                    self.stdout.write(self.style.ERROR(f"  [FAIL] {c} -> {e}"))

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING(f"seed_all complete: {ran} OK, {len(failed)} problem(s)"))
        for c, err in failed:
            self.stdout.write(self.style.ERROR(f"  {c}: {err}"))
