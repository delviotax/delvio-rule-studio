"""fetch_irs_drafts — the draft forms/instructions arm (funnel Phase 3).

Watches `irs.gov/downloads/irs-dft` — the earliest public signal that a form or instruction is
changing for the coming season (~6 posts/day in season). The description column is structured
enough ('2026 Inst 8615 (PDF)', '1226 Form 1062 (Schedule A) (PDF)') that form number, kind and
year parse straight off the index — no PDF fetch, so this arm is cheap enough to run daily.

THE ONE ALLOWED FILTERING ARM. Relevance invariant #1 says the score never gates creation; this
arm is the sanctioned exception because its filter is an EXACT structured form-number match
against the authored perimeter (TaxForm / AuthorityFormLink), not a fuzzy text score — and it
LOGS what it dropped, every run, so the filter is auditable. Without the filter, six drafts a day
of 990/706/5500 material would bury the digest.

Dedup keys on `DFT:<filename>@<posted_date>` — NOT filename alone. The same draft is re-posted
under the same filename on each revision, and each re-post is a REAL change (regression #4).

Usage:
  manage.py fetch_irs_drafts                      # newest page (50 rows)
  manage.py fetch_irs_drafts --pages 2 --since 2026-07-01
  manage.py fetch_irs_drafts --all-forms          # perimeter filter OFF (audit/backfill)
  manage.py fetch_irs_drafts --dry-run
"""
import datetime as dt
import re

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from sources import irs_directory as ix
from sources.change_register_helpers import open_detected
from sources.models import ChangeRegisterItem, FeedType, ItemKind, SourceFeedDefinition
from sources.relevance import build_perimeter_index, score_summary

FEED_CODE = "IRS_DFT"

_NORM_RE = re.compile(r"[\s_-]+")


def _norm(form: str) -> str:
    """'1120-S' / '1120s' / '1120 S' -> '1120S' — one comparable token per form number."""
    return _NORM_RE.sub("", (form or "").strip().upper())


def perimeter_forms(index) -> set[str]:
    """The exact-match set: every form number the perimeter index knows, normalized."""
    return {_norm(code) for code in index.form_needles} | {_norm(e) for e in index.entity_needles}


class Command(BaseCommand):
    help = "Open DETECTED items for in-perimeter IRS draft forms/instructions (funnel Phase 3)."

    def add_arguments(self, parser):
        parser.add_argument("--pages", type=int, default=1,
                            help="Listing pages to read, 50 rows each (default 1).")
        parser.add_argument("--since", help="Only drafts posted on/after YYYY-MM-DD.")
        parser.add_argument("--all-forms", action="store_true",
                            help="Disable the perimeter filter (audit/backfill).")
        parser.add_argument("--dry-run", action="store_true", help="Report; open nothing.")

    def handle(self, *args, **o):
        since = None
        if o.get("since"):
            try:
                since = dt.date.fromisoformat(o["since"])
            except ValueError:
                raise CommandError("--since must be YYYY-MM-DD.")

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\nIRS draft forms — {o['pages']} page(s)"
            f"{' since ' + since.isoformat() if since else ''}"
            f"{' · PERIMETER FILTER OFF' if o['all_forms'] else ''}\n"))

        if o["dry_run"]:
            feed = SourceFeedDefinition.objects.filter(feed_code=FEED_CODE).first()
        else:
            feed, _ = SourceFeedDefinition.objects.get_or_create(
                feed_code=FEED_CODE,
                defaults={
                    "feed_name": "IRS draft forms and instructions (irs-dft)",
                    "jurisdiction_code": "US", "source_family": "IRS_FORMS",
                    "base_url": f"{ix.BASE}/{ix.DFT}", "feed_type": FeedType.DIRECTORY_INDEX,
                    "refresh_frequency": "daily", "parser_strategy": "directory_index",
                    "arm_command": "fetch_irs_drafts",
                    "notes": "Earliest signal a form is changing. Exact perimeter filter; drops logged.",
                },
            )

        try:
            rows = ix.iter_rows(ix.DFT, pages=o["pages"])
        except ix.IndexLayoutError as e:
            raise CommandError(str(e))
        except Exception as e:  # noqa: BLE001
            raise CommandError(f"irs-dft index fetch failed: {e!r}")

        index = build_perimeter_index()
        keep_set = perimeter_forms(index)

        candidates, dropped, undecodable = [], [], 0
        for row in rows:
            meta = ix.decode_dft(row)
            if meta is None:
                undecodable += 1
                continue
            if since and row.posted_at < since:
                continue
            if not o["all_forms"] and _norm(meta["form"]) not in keep_set:
                dropped.append(meta["form"])
                continue
            candidates.append((row, meta))

        refs = [f"DFT:{row.filename}@{row.posted_at.isoformat()}" for row, _ in candidates]
        known = set(ChangeRegisterItem.objects.filter(external_ref__in=refs)
                    .values_list("external_ref", flat=True))

        opened = skipped = 0
        for row, meta in candidates:
            ext_ref = f"DFT:{row.filename}@{row.posted_at.isoformat()}"
            if ext_ref in known:
                skipped += 1
                continue
            label = f"{meta['kind']} {meta['form']}"
            if meta["schedule"]:
                label += f" ({meta['schedule']})"
            year_bit = (f"TY{meta['tax_year']}" if meta["tax_year"]
                        else f"rev. {meta['revision']}" if meta["revision"] else "")
            res = open_detected(
                external_ref=ext_ref,
                title=f"Draft {label} posted" + (f" — {year_bit}" if year_bit else ""),
                summary=(f"[draft · posted {row.posted_at} · {row.size}]\n"
                         f"Index description: {row.description or '(none)'}\n"
                         "A re-post under the same filename is a new revision — compare against "
                         "the field maps and any authored rules for this form.\n"
                         f"{row.url}"),
                index=index,
                text=row.description,
                forms=(meta["form"],),
                jurisdiction="US",
                item_kind=ItemKind.DRAFT_FORM,
                source_url=row.url,
                published_date=row.posted_at,
                tax_year=meta["tax_year"],
                affected_forms=[meta["form"]],
                feed=feed,
                dry_run=o["dry_run"],
            )
            if res.skipped:
                skipped += 1
                continue
            opened += 1
            line = f"{label:<32} {row.posted_at}  score {res.score:>3}  {score_summary(res.signals)}"
            if o["dry_run"]:
                self.stdout.write(self.style.WARNING(f"NEW  {line}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"DETECTED {res.change_code}: {line}"))

        if not o["dry_run"] and feed is not None:
            feed.last_polled_at = timezone.now()
            feed.last_result_note = (f"ok · {len(rows)} rows / {len(candidates)} in perimeter / "
                                     f"{opened} opened / {len(dropped)} dropped out-of-perimeter")
            feed.save(update_fields=["last_polled_at", "last_result_note"])

        self.stdout.write("\n" + "=" * 60)
        verb = "would open" if o["dry_run"] else "opened"
        self.stdout.write(f"fetch_irs_drafts: {len(rows)} rows / {len(candidates)} in perimeter / "
                          f"{opened} {verb} / {skipped} already-known")
        if dropped:
            # The audit line the filter exception is conditioned on: what was dropped, visibly.
            uniq = sorted({_norm(f) for f in dropped})
            self.stdout.write(f"  dropped {len(dropped)} out-of-perimeter draft(s): "
                              f"{', '.join(uniq[:15])}{' …' if len(uniq) > 15 else ''}")
        if undecodable:
            self.stdout.write(f"  {undecodable} undecodable row(s) ignored")
        self.stdout.write("=" * 60)
