# -*- coding: utf-8 -*-
"""Report — and optionally enforce — AuthoritySource ownership across all loaders.

    poetry run python manage.py check_authority_owners            # report, exit 0
    poetry run python manage.py check_authority_owners --strict   # fail on NEW collisions
    poetry run python manage.py check_authority_owners --loader load_ga500_form_500.py
    poetry run python manage.py check_authority_owners --compare-prod

`--strict` is what CI and `seed_all` use: a NEW collision is an error, the 24
acknowledged ones are not. See `_authority_guard.py` for why that split exists.

`--compare-prod` additionally reads the live rows and reports, for each acknowledged
collision, WHICH writer production currently matches — i.e. which command happened to
run last. That is the concrete harm, rather than the theoretical one.
"""
from django.core.management.base import BaseCommand

from ._authority_guard import ACKNOWLEDGED, MATERIAL_FIELDS, collisions, guard, scan, selftest


class Command(BaseCommand):
    help = "Report/enforce AuthoritySource ownership (the two-writers guard)."

    def add_arguments(self, parser):
        parser.add_argument("--strict", action="store_true",
                            help="exit non-zero if any UNACKNOWLEDGED collision exists")
        parser.add_argument("--loader", default=None,
                            help="restrict to collisions involving this module")
        parser.add_argument("--compare-prod", action="store_true",
                            help="show which writer production currently matches")

    def handle(self, *args, **o):
        if not selftest():
            self.stderr.write(self.style.ERROR(
                "the guard's own selftest FAILED — it cannot detect a synthetic collision, "
                "so a clean report from it would mean nothing"))
            raise SystemExit(2)
        self.stdout.write("guard selftest: PASS (fires on a synthetic collision)")

        decls, n_files, _ = scan()
        found = collisions(decls)
        if o["loader"]:
            found = {c: v for c, v in found.items() if o["loader"] in v["writers"]}

        differ = {c: v for c, v in found.items() if v["differs"]}
        same = {c: v for c, v in found.items() if not v["differs"]}
        new = {c: v for c, v in found.items() if c not in ACKNOWLEDGED}

        self.stdout.write("")
        self.stdout.write("modules scanned      : %d" % n_files)
        self.stdout.write("authority codes      : %d" % len(decls))
        self.stdout.write("multi-writer codes   : %d" % len(found))
        self.stdout.write("  writers DISAGREE   : %d   <- last loader to run decides prod"
                          % len(differ))
        self.stdout.write("  identical today    : %d" % len(same))
        self.stdout.write("  NOT acknowledged   : %d   %s"
                          % (len(new), "<- NEW, must be fixed" if new else "(none)"))

        if o["compare_prod"] and differ:
            from sources.models import AuthoritySource
            self.stdout.write("")
            self.stdout.write("which writer production currently matches:")
            for c, v in sorted(differ.items()):
                row = AuthoritySource.objects.filter(source_code=c).first()
                if not row:
                    self.stdout.write("  %-26s NOT IN PROD" % c)
                    continue
                match = [m for m, f in decls[c].items()
                         if all(f.get(k) == getattr(row, k, None) for k in MATERIAL_FIELDS)]
                self.stdout.write("  %-26s %s" % (c, match[0] if len(match) == 1 else
                                                  ("ambiguous %s" % match if match else "NEITHER writer")))

        self.stdout.write("")
        guard(loader_name=o["loader"], write=self.stdout.write, raise_on_new=o["strict"])
        if new and not o["strict"]:
            self.stdout.write(self.style.WARNING(
                "\n%d NEW collision(s) reported above. Re-run with --strict to fail on them."
                % len(new)))
        elif not new:
            self.stdout.write(self.style.SUCCESS("no new collisions."))
