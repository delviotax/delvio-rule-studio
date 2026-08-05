"""fetch_irs_drop — FEED_POLL leg 4, and the arm that closes the real detection gap.

Opens a DETECTED item per INDIVIDUAL piece of IRS sub-regulatory guidance — Revenue Procedures,
Notices, Revenue Rulings, Announcements — from `irs.gov/downloads/irs-drop`.

Why this matters more than the other arms: `fetch_irb` detects at BULLETIN level, and a bulletin
appears WEEKS after the guidance itself drops here. The annual inflation Revenue Procedure, the
standard mileage notice, the retirement-plan limits notice, the Form 3115 automatic-change list —
all land in irs-drop first. Bulletin-level detection also means triage has to open a 100-page PDF
to find out whether anything in it matters. This arm gives you the item, its designation, and
enough extracted text to score it, on the day it publishes.

Volume is modest (~8/month), so this does NOT need a filter — every guidance file becomes a row,
ranked by relevance. See `sources.relevance`: the score orders the digest, it never gates.

⚠ Designation comes from the FILENAME, not the description column. Verified live 2026-08-05, real
rows carry 'Rev. Proc.  2026-28' (two spaces), 'Rev. Proc. 2026-26', 'RR-2026-13', 'N-2026-44' and
'N-2026-39 Appendix 2' interchangeably. Filenames are consistent: rp-/n-/rr-/a-.

Usage:
  manage.py fetch_irs_drop                      # newest page (50 files ≈ 6 months of coverage)
  manage.py fetch_irs_drop --pages 2 --since 2026-01-01
  manage.py fetch_irs_drop --kinds rp,n         # only Rev. Procs and Notices
  manage.py fetch_irs_drop --no-text            # skip PDF download (fast; everything unscoreable)
  manage.py fetch_irs_drop --dry-run            # report; open nothing
"""
import datetime as dt

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from sources import irs_directory as ix
from sources import pdf_text
from sources.change_register_helpers import open_detected, parse_csv
from sources.models import ChangeRegisterItem, FeedType, ItemKind, SourceFeedDefinition
from sources.relevance import build_perimeter_index, score_summary

FEED_CODE = "IRS_DROP"
DEFAULT_PAGES = 1

KIND_TO_ITEM_KIND = {
    "rp": ItemKind.REV_PROC,
    "n": ItemKind.NOTICE,
    "rr": ItemKind.REV_RUL,
    "a": ItemKind.ANNOUNCEMENT,
}


class Command(BaseCommand):
    help = "Open DETECTED change-register items per individual IRS guidance file (FEED_POLL leg 4)."

    def add_arguments(self, parser):
        parser.add_argument("--pages", type=int, default=DEFAULT_PAGES,
                            help="Listing pages to read, 50 rows each (default 1). The index is a full archive.")
        parser.add_argument("--since", help="Only files posted on/after YYYY-MM-DD.")
        parser.add_argument("--kinds", help="Comma subset of rp,n,rr,a (default: all).")
        parser.add_argument("--no-text", action="store_true",
                            help="Do not download PDFs. Fast, but every item scores unscoreable.")
        parser.add_argument("--dry-run", action="store_true", help="Report; open nothing.")

    def handle(self, *args, **o):
        kinds = {k.lower() for k in parse_csv(o.get("kinds"))} or set(KIND_TO_ITEM_KIND)
        bad = kinds - set(KIND_TO_ITEM_KIND)
        if bad:
            raise CommandError(f"--kinds got unknown value(s) {sorted(bad)}; valid: {sorted(KIND_TO_ITEM_KIND)}")

        since = None
        if o.get("since"):
            try:
                since = dt.date.fromisoformat(o["since"])
            except ValueError:
                raise CommandError("--since must be YYYY-MM-DD.")

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\nIRS guidance drop — {o['pages']} page(s)"
            f"{' since ' + since.isoformat() if since else ''} · kinds {','.join(sorted(kinds))}\n"))

        # --dry-run must write NOTHING, including the feed row — see fetch_ecfr_title26.
        if o["dry_run"]:
            feed = SourceFeedDefinition.objects.filter(feed_code=FEED_CODE).first()
        else:
            feed, _ = SourceFeedDefinition.objects.get_or_create(
                feed_code=FEED_CODE,
                defaults={
                    "feed_name": "IRS guidance drop (Rev. Procs, Notices, Rev. Ruls, Announcements)",
                    "jurisdiction_code": "US", "source_family": "IRS_GUIDANCE",
                    "base_url": f"{ix.BASE}/{ix.DROP}", "feed_type": FeedType.DIRECTORY_INDEX,
                    "refresh_frequency": "daily", "parser_strategy": "directory_index",
                    "arm_command": "fetch_irs_drop",
                    "notes": "Item-level; lands weeks before the IRB bundles it. Designation from filename.",
                },
            )

        try:
            rows = ix.iter_rows(ix.DROP, pages=o["pages"])
        except ix.IndexLayoutError as e:
            raise CommandError(str(e))
        except Exception as e:  # noqa: BLE001 — network/HTTP; surface as a clean arm failure
            raise CommandError(f"irs-drop index fetch failed: {e!r}")

        # Decode + filter to guidance files we care about.
        candidates = []
        undecodable = 0
        for row in rows:
            meta = ix.decode_drop(row)
            if meta is None:
                undecodable += 1
                continue
            if meta["kind"] not in kinds:
                continue
            if since and row.posted_at < since:
                continue
            candidates.append((row, meta))

        # One query for idempotency, so we never download a PDF for something we already have.
        refs = [f"DROP:{row.filename}" for row, _ in candidates]
        known = set(ChangeRegisterItem.objects.filter(external_ref__in=refs)
                    .values_list("external_ref", flat=True))

        index = build_perimeter_index()
        opened = skipped = fetched_pdfs = unreadable = 0

        for row, meta in candidates:
            ext_ref = f"DROP:{row.filename}"
            if ext_ref in known:
                skipped += 1
                continue

            body = None
            if not o["no_text"] and meta["ext"] == "pdf":
                body = pdf_text.text_for_url(row.url)
                fetched_pdfs += 1
                if body is None:
                    unreadable += 1

            # Description alone is thin, but for .xlsx appendices it is all there is; combining
            # keeps a parent notice's appendix from scoring purely unscoreable.
            scored_text = " ".join(p for p in (meta["designation"], row.description, body) if p) or None

            res = open_detected(
                external_ref=ext_ref,
                title=f"{meta['designation']} published",
                summary=(f"[{meta['designation']} · posted {row.posted_at} · {row.size}]\n"
                         f"Index description: {row.description or '(none)'}\n"
                         f"{'⚠ Text could not be extracted — triage must open the file.' if body is None and meta['ext'] == 'pdf' and not o['no_text'] else ''}\n"
                         f"{(body[:400] + '…') if body else ''}\n"
                         f"{row.url}"),
                index=index, text=scored_text, jurisdiction="US",
                item_kind=KIND_TO_ITEM_KIND[meta["kind"]], source_url=row.url,
                published_date=row.posted_at, tax_year=None,
                dry_run=o["dry_run"],
            )
            if res.skipped:
                skipped += 1
                continue
            opened += 1
            line = (f"{meta['designation']:<28} {row.posted_at}  score {res.score:>3}  "
                    f"{score_summary(res.signals)}")
            if o["dry_run"]:
                self.stdout.write(self.style.WARNING(f"NEW  {line}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"DETECTED {res.change_code}: {line}"))

        if not o["dry_run"] and feed is not None:
            feed.last_polled_at = timezone.now()
            feed.last_result_note = (f"ok · {len(rows)} rows / {len(candidates)} guidance / "
                                     f"{opened} opened / {unreadable} unreadable")
            feed.save(update_fields=["last_polled_at", "last_result_note"])

        self.stdout.write("\n" + "=" * 60)
        verb = "would open" if o["dry_run"] else "opened"
        self.stdout.write(f"fetch_irs_drop: {len(rows)} rows / {len(candidates)} guidance files / "
                          f"{opened} {verb} / {skipped} already-known")
        if fetched_pdfs:
            self.stdout.write(f"  PDFs read: {fetched_pdfs} ({unreadable} unreadable -> scored "
                              f"unscoreable, surfaced to a human)")
        if undecodable:
            self.stdout.write(f"  {undecodable} non-guidance file(s) on the index ignored")
        if o["no_text"]:
            self.stdout.write(self.style.WARNING(
                "  ⚠ --no-text: nothing was scored from document text; treat scores as provisional."))
        self.stdout.write("=" * 60)
