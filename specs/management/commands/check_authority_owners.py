# -*- coding: utf-8 -*-
"""Report — and optionally enforce — AuthoritySource ownership across ALL writer populations.

    poetry run python manage.py check_authority_owners            # report, exit 0
    poetry run python manage.py check_authority_owners --strict   # fail on NEW collisions
    poetry run python manage.py check_authority_owners --loader load_ga500_form_500.py
    poetry run python manage.py check_authority_owners --compare-prod
    poetry run python manage.py check_authority_owners --regenerate-acknowledged

`--strict` is what CI and `seed_all` use: a NEW collision is an error, the acknowledged
ones are not. See `_authority_guard.py` for why that split exists.

⚠ `--loader X --strict` IS the pre-seed pre-flight. The guard is not wired into
individual loaders, so seeding one directly does not run it. That pre-flight is how
D-38's GA-500 hazard was caught before it fired.

`--compare-prod` reads the live rows and reports, for each acknowledged collision,
WHICH writer production currently matches — i.e. which command happened to run last.
That is the concrete harm rather than the theoretical one.
⚠⚠ It also reports CHIMERA rows, which match no writer at all. Those are not drift:
a writer that OMITS a key leaves that column untouched, so production can hold a
blend of two writers that neither would produce. Re-seeding the rightful owner does
NOT restore such a row.

`--regenerate-acknowledged` prints the ACKNOWLEDGED block from the CURRENT scan, so
that list is generated rather than hand-typed. It prints; it never writes.
"""
from django.core.management.base import BaseCommand

from . import _authority_guard as AG
from . import _enum_guard as EG
from ._authority_guard import (
    ACKNOWLEDGED, MATERIAL_FIELDS, collisions, coverage, guard, is_acknowledged,
    selftest_report,
)


def _acknowledged_block(found):
    """The ACKNOWLEDGED literal for the collisions currently on disk."""
    dis = {c: v for c, v in found.items() if v["differs"]}
    same = {c: v for c, v in found.items() if not v["differs"]}
    out = []
    for title, group, note in (
        ("writers DISAGREE: live last-writer-wins rows (%d)" % len(dis), dis, None),
        ("writers AGREE today: benign, but still two writers (%d)" % len(same), same, "identical today"),
    ):
        out.append("    # --- %s ---" % title)
        for c in sorted(group):
            ws = group[c]["writers"]
            tup = "(%s)" % ", ".join("%r" % w for w in ws) if len(ws) > 1 else "(%r,)" % ws[0]
            n = note or ("differs: " + ",".join(group[c]["differs"]))
            out.append("    %-28s (%s, %r)," % ('"%s":' % c, tup, n))
        out.append("")
    return "\n".join(out)


class Command(BaseCommand):
    help = "Report/enforce AuthoritySource ownership (the two-writers guard)."

    def add_arguments(self, parser):
        parser.add_argument("--strict", action="store_true",
                            help="exit non-zero if any UNACKNOWLEDGED collision exists")
        parser.add_argument("--loader", default=None,
                            help="restrict to collisions involving this module")
        parser.add_argument("--compare-prod", action="store_true",
                            help="show which writer production currently matches")
        parser.add_argument("--regenerate-acknowledged", action="store_true",
                            help="print the ACKNOWLEDGED block for the current scan (never writes)")
        parser.add_argument("--regenerate-enum-baseline", action="store_true",
                            help="print the enum-ratchet baseline for the current tree (never writes)")

    def handle(self, *args, **o):
        ok, failures = selftest_report()
        if not ok:
            self.stderr.write(self.style.ERROR(
                "the guard's own selftest FAILED — a clean report from it would mean nothing:"))
            for f in failures:
                self.stderr.write(self.style.ERROR("    %s" % f))
            raise SystemExit(2)
        self.stdout.write("guard selftest: PASS (fires on a synthetic collision; all populations read)")

        cov = coverage()
        decls = cov["decls"]
        found = collisions(decls)

        if o["regenerate_acknowledged"]:
            self.stdout.write("")
            self.stdout.write(_acknowledged_block(found))
            return

        if o["regenerate_enum_baseline"]:
            self.stdout.write("")
            self.stdout.write(EG.baseline_block(decls))
            return

        if o["loader"]:
            found = {c: v for c, v in found.items()
                     if AG._matches_loader(o["loader"], v["writers"])}

        differ = {c: v for c, v in found.items() if v["differs"]}
        same = {c: v for c, v in found.items() if not v["differs"]}
        # ⚠ Membership is by WRITER SET, not by code. Checking `c not in ACKNOWLEDGED`
        #    would report "0 NEW" for a code whose writer set has changed, while
        #    guard() refuses it — a summary that disagrees with the verdict below it.
        new = {c: v for c, v in found.items() if not is_acknowledged(c, v["writers"])}

        self.stdout.write("")
        self.stdout.write("writer populations:")
        for p in cov["populations"]:
            self.stdout.write("    %-14s %3d modules, %3d declaring, %4d codes"
                              % (p["name"], p["modules"], p["declaring"], p["codes"]))
        self.stdout.write("authority codes      : %d" % len(decls))
        self.stdout.write("multi-writer codes   : %d" % len(found))
        self.stdout.write("  writers DISAGREE   : %d   <- last module to run decides prod"
                          % len(differ))
        self.stdout.write("  identical today    : %d" % len(same))
        self.stdout.write("  NOT acknowledged   : %d   %s"
                          % (len(new), "<- NEW, must be fixed" if new else "(none)"))

        if o["compare_prod"] and differ:
            from sources.models import AuthoritySource
            self.stdout.write("")
            self.stdout.write("which writer production currently matches:")
            chimeras = 0
            for c, v in sorted(differ.items()):
                row = AuthoritySource.objects.filter(source_code=c).first()
                if not row:
                    self.stdout.write("  %-26s NOT IN PROD" % c)
                    continue
                match = [m for m, f in decls[c].items()
                         if all(f.get(k) == getattr(row, k, None) for k in MATERIAL_FIELDS)]
                if len(match) == 1:
                    verdict = match[0]
                elif match:
                    verdict = "ambiguous %s" % match
                else:
                    verdict = "CHIMERA — matches NO writer (omitted keys kept a previous value)"
                    chimeras += 1
                self.stdout.write("  %-26s %s" % (c, verdict))
            if chimeras:
                self.stdout.write(self.style.WARNING(
                    "\n%d chimera row(s): production holds a blend no single module would "
                    "produce. Re-seeding the owner will NOT restore those rows." % chimeras))

        self.stdout.write("")
        guard(loader_name=o["loader"], write=self.stdout.write, raise_on_new=o["strict"])

        # ⚠ The enum ratchet is library-wide, not per-loader: an invalid value anywhere is a
        #   seed that must not proceed, and scoping it to --loader would let the next loader
        #   ship the one this one avoided. Campaign D-41.
        self.stdout.write("")
        EG.guard(write=self.stdout.write, raise_on_problem=o["strict"], decls=decls)
        if new and not o["strict"]:
            self.stdout.write(self.style.WARNING(
                "\n%d NEW collision(s) reported above. Re-run with --strict to fail on them."
                % len(new)))
        elif not new:
            self.stdout.write(self.style.SUCCESS("no new collisions."))
