"""poll_change_feeds — the scheduler entry point for the change-register funnel.

ONE command the Render cron runs on a schedule. It runs every automated FEED_POLL detector
RESILIENTLY — a failure in one arm (a network blip, an irs.gov layout change) is logged and does
not stop the others — then reports what opened and (optionally) pings Pushover.

It changes nothing about the gates: it only fills the register to DETECTED. Triage, promotion and
authoring still run through Ken and the existing front door.

Exit code: 0 if at least one arm succeeded (even if it opened nothing); non-zero only if EVERY arm
errored (so Render surfaces a real outage, not a quiet week).

Arms (each gets a generated --no-<key> flag):
  fr    fetch_federal_register  — IRS/Treasury regulations (final + proposed)
  irb   fetch_irb               — weekly Internal Revenue Bulletin, BULLETIN level. Now a backstop:
                                  `drop` gets the same items weeks earlier and item-by-item.
  ecfr  fetch_ecfr_title26      — 26 CFR section-level amendments
  drop  fetch_irs_drop          — individual Rev. Procs / Notices / Rev. Ruls / Announcements
  dft   fetch_irs_drafts        — draft forms/instructions, exact perimeter filter (Phase 3)
  chk   fetch_irs_form_checksums— final-form PDF checksum watch, HEAD-first (Phase 3)
  court fetch_court_opinions    — Tax Court / 11th Cir. / 4th Cir. / SCOTUS via CourtListener (Phase 3)

Usage:
  manage.py poll_change_feeds                      # all arms, scheduler defaults
  manage.py poll_change_feeds --dry-run            # run every arm, open nothing
  manage.py poll_change_feeds --no-irb --no-drop   # skip arms
  manage.py poll_change_feeds --only ecfr          # debug a single arm in production

Optional notification: set PUSHOVER_TOKEN + PUSHOVER_USER to get a ping when new items open.
"""
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Callable

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from sources.models import ChangeRegisterItem


@dataclass(frozen=True)
class Arm:
    key: str                      # short name; drives the generated --no-<key> flag and --only
    command: str
    kwargs: Callable[[dict], dict]


# Defaults carry deliberate overlap so nothing slips between runs — idempotency dedups it.
ARMS = (
    Arm("fr", "fetch_federal_register",
        lambda o: {"lookback_days": o["fr_lookback_days"], "dry_run": o["dry_run"]}),
    Arm("irb", "fetch_irb",
        lambda o: {"limit": o["irb_limit"], "dry_run": o["dry_run"]}),
    Arm("ecfr", "fetch_ecfr_title26",
        lambda o: {"lookback_days": o["ecfr_lookback_days"], "dry_run": o["dry_run"]}),
    Arm("drop", "fetch_irs_drop",
        lambda o: {"pages": o["drop_pages"], "no_text": o["drop_no_text"], "dry_run": o["dry_run"]}),
    Arm("dft", "fetch_irs_drafts",
        lambda o: {"pages": o["dft_pages"], "dry_run": o["dry_run"]}),
    Arm("chk", "fetch_irs_form_checksums",
        lambda o: {"dry_run": o["dry_run"]}),
    Arm("court", "fetch_court_opinions",
        lambda o: {"days": o["court_days"], "dry_run": o["dry_run"]}),
)


def _notify(message: str) -> bool:
    """Best-effort Pushover ping; only fires if both env vars are set; never raises."""
    token, user = os.getenv("PUSHOVER_TOKEN"), os.getenv("PUSHOVER_USER")
    if not (token and user):
        return False
    try:
        data = urllib.parse.urlencode(
            {"token": token, "user": user, "title": "RS change register", "message": message}).encode()
        req = urllib.request.Request("https://api.pushover.net/1/messages.json", data=data)
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310
            resp.read()
        return True
    except Exception:  # noqa: BLE001 — notification must never break the poll
        return False


class Command(BaseCommand):
    help = "Run every automated change-register feed poller for the scheduler."

    def add_arguments(self, parser):
        parser.add_argument("--fr-lookback-days", type=int, default=8, help="Federal Register lookback (default 8).")
        parser.add_argument("--irb-limit", type=int, default=3,
                            help="IRB: most-recent N bulletins to check (default 3). IRB is a backstop now.")
        parser.add_argument("--ecfr-lookback-days", type=int, default=30,
                            help="26 CFR amendment lookback (default 30); the arm short-circuits when nothing moved.")
        parser.add_argument("--drop-pages", type=int, default=1,
                            help="irs-drop listing pages, 50 rows each (default 1).")
        parser.add_argument("--drop-no-text", action="store_true",
                            help="irs-drop: skip PDF downloads (fast; everything scores unscoreable).")
        parser.add_argument("--dft-pages", type=int, default=1,
                            help="irs-dft listing pages, 50 rows each (default 1).")
        parser.add_argument("--court-days", type=int, default=10,
                            help="Court-opinion lookback for the daily poll (default 10; overlap is dedup'd).")
        parser.add_argument("--only", help="Run exactly one arm by key: " + ", ".join(a.key for a in ARMS))
        parser.add_argument("--dry-run", action="store_true", help="Run every arm; open nothing.")
        for arm in ARMS:
            parser.add_argument(f"--no-{arm.key}", action="store_true",
                                help=f"Skip the {arm.command} arm.")

    def handle(self, *args, **o):
        self.stdout.write(self.style.MIGRATE_HEADING("\npoll_change_feeds — automated change-register intake\n"))

        only = (o.get("only") or "").strip().lower()
        if only and only not in {a.key for a in ARMS}:
            raise CommandError(f"--only got {only!r}; valid keys: {', '.join(a.key for a in ARMS)}")

        results, total_opened = [], 0
        for arm in ARMS:
            if only:
                if arm.key != only:
                    continue
            elif o.get(f"no_{arm.key}"):
                self.stdout.write(f"— {arm.command}: skipped")
                continue

            before = ChangeRegisterItem.objects.count()
            try:
                call_command(arm.command, stdout=self.stdout, stderr=self.stderr, **arm.kwargs(o))
                opened = 0 if o["dry_run"] else ChangeRegisterItem.objects.count() - before
                results.append((arm.command, True, opened, None))
                total_opened += max(0, opened)
            except Exception as e:  # noqa: BLE001 — one arm must not kill the others
                results.append((arm.command, False, 0, repr(e)))
                self.stderr.write(self.style.ERROR(f"— {arm.command} FAILED: {e!r}"))

        ok = [r for r in results if r[1]]

        self.stdout.write("\n" + "=" * 60)
        if o["dry_run"]:
            # Don't print a DB delta of 0 as if it were a finding — the per-arm "would open"
            # counts above are the real answer in a dry run.
            self.stdout.write(f"poll_change_feeds: {len(ok)}/{len(results)} arms ok "
                              f"[dry-run — see each arm's 'would open' count above]")
        else:
            self.stdout.write(f"poll_change_feeds: {len(ok)}/{len(results)} arms ok / "
                              f"{total_opened} new item(s) opened")
        for name, okflag, opened, err in results:
            self.stdout.write(f"  {'OK ' if okflag else 'ERR'} {name}: "
                              + (f"{opened} opened" if okflag and not o["dry_run"]
                                 else ("ran" if okflag else err)))
        self.stdout.write("=" * 60)

        if total_opened and not o["dry_run"]:
            pinged = _notify(f"{total_opened} new tax-law change item(s) detected — triage in the register "
                             f"(change_register list --status detected).")
            self.stdout.write(f"Pushover: {'sent' if pinged else 'not configured (set PUSHOVER_TOKEN/PUSHOVER_USER)'}")

        # Non-zero ONLY if everything errored — a real outage, not a quiet week.
        if results and not ok:
            raise CommandError("All change-feed arms failed — see errors above.")
