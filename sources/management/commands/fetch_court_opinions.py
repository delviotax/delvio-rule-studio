"""fetch_court_opinions — the tax-litigation arm (funnel Phase 3).

Polls the CourtListener v4 SEARCH API for new opinions from the courts that can move our
perimeter: the U.S. Tax Court (everything it publishes is tax), the 11th Circuit (Georgia),
the 4th Circuit (the Carolinas), and the Supreme Court.

Endpoint discipline (verified 2026-08-05 during planning): `/api/rest/v4/search/?type=o` returns
200 unauthenticated; `/api/rest/v4/opinions/` 401s — so SEARCH ONLY. Poll, don't webhook:
<10 relevant items/month does not justify a public inbound endpoint.

Filtering happens SERVER-SIDE, in the query, not client-side after fetch: the Tax Court is
fetched unfiltered, while the circuits + SCOTUS are queried WITH a tax phrase (`TAX_QUERY`), so
this arm never sees — and therefore never suppresses — a non-tax circuit case. That keeps
relevance invariant #1 intact: everything fetched is recorded; the score orders it.

Dedup: `CL:<cluster_id>`. Search re-returns the same cluster on every poll inside the lookback
window; the namespace makes that a no-op.

Usage:
  manage.py fetch_court_opinions                    # default 30-day lookback, all four courts
  manage.py fetch_court_opinions --days 10          # the daily-poll overlap window
  manage.py fetch_court_opinions --courts tax       # subset
  manage.py fetch_court_opinions --dry-run
"""
import datetime as dt
import json
import urllib.parse
import urllib.request

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from sources.change_register_helpers import open_detected, parse_csv
from sources.models import ChangeRegisterItem, FeedType, ItemKind, SourceFeedDefinition
from sources.relevance import build_perimeter_index, score_summary

FEED_CODE = "COURT_OPINIONS"
SEARCH_URL = "https://www.courtlistener.com/api/rest/v4/search/"
USER_AGENT = "Mozilla/5.0 (compatible; delvio-rule-studio change-register; +https://kenlill.com)"

# Which courts, and whether they need the tax-phrase query. ca11 = GA; ca4 = SC/NC.
COURTS = {
    "tax": {"label": "U.S. Tax Court", "needs_tax_query": False},
    "ca11": {"label": "11th Circuit", "needs_tax_query": True},
    "ca4": {"label": "4th Circuit", "needs_tax_query": True},
    "scotus": {"label": "Supreme Court", "needs_tax_query": True},
}

# Server-side gate for the general courts — an IRC-shaped or unmistakably-tax phrase.
TAX_QUERY = '"internal revenue" OR "commissioner of internal revenue" OR "26 U.S.C." OR "tax court"'


class CourtSearchLayoutError(RuntimeError):
    """The search response had no parseable results structure — API change, not a quiet week."""


def _http_get_json(url: str) -> dict:
    """Isolated for tests."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
        return json.loads(resp.read().decode("utf-8"))


def search_court(court: str, filed_after: dt.date, *, tax_query: bool) -> list[dict]:
    """One search request; returns the raw result rows. Raises CourtSearchLayoutError on shape drift."""
    params = {
        "type": "o",
        "court": court,
        "filed_after": filed_after.isoformat(),
        "order_by": "dateFiled desc",
    }
    if tax_query:
        params["q"] = TAX_QUERY
    payload = _http_get_json(f"{SEARCH_URL}?{urllib.parse.urlencode(params)}")
    results = payload.get("results")
    if not isinstance(results, list):
        raise CourtSearchLayoutError(
            f"CourtListener search for {court!r} returned no 'results' list — API shape changed.")
    return results


def _first(row: dict, *keys, default=""):
    for k in keys:
        v = row.get(k)
        if v:
            return v
    return default


class Command(BaseCommand):
    help = "Open DETECTED items for new tax-relevant court opinions (funnel Phase 3)."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=30,
                            help="Lookback for filed_after (default 30; the daily poll uses 10).")
        parser.add_argument("--courts", help=f"Comma subset of {','.join(COURTS)} (default: all).")
        parser.add_argument("--dry-run", action="store_true", help="Report; open nothing.")

    def handle(self, *args, **o):
        courts = [c.lower() for c in parse_csv(o.get("courts"))] or list(COURTS)
        bad = set(courts) - set(COURTS)
        if bad:
            raise CommandError(f"--courts got unknown value(s) {sorted(bad)}; valid: {sorted(COURTS)}")
        if o["days"] < 1:
            raise CommandError("--days must be >= 1.")

        filed_after = timezone.now().date() - dt.timedelta(days=o["days"])
        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\nCourt opinions — {', '.join(courts)} · filed after {filed_after}\n"))

        if o["dry_run"]:
            feed = SourceFeedDefinition.objects.filter(feed_code=FEED_CODE).first()
        else:
            feed, _ = SourceFeedDefinition.objects.get_or_create(
                feed_code=FEED_CODE,
                defaults={
                    "feed_name": "Court opinions (Tax Court, 11th Cir., 4th Cir., SCOTUS)",
                    "jurisdiction_code": "US", "source_family": "COURTS",
                    "base_url": SEARCH_URL, "feed_type": FeedType.JSON_API,
                    "refresh_frequency": "daily", "parser_strategy": "courtlistener_search",
                    "arm_command": "fetch_court_opinions",
                    "notes": "Search API only (/opinions/ requires auth). Circuits queried with the tax phrase.",
                },
            )

        index = build_perimeter_index()
        opened = skipped = unusable = 0
        rows_total = 0
        failures: list[str] = []

        for court in courts:
            spec = COURTS[court]
            try:
                results = search_court(court, filed_after, tax_query=spec["needs_tax_query"])
            except CourtSearchLayoutError as e:
                raise CommandError(str(e))
            except Exception as e:  # noqa: BLE001 — one court down must not kill the rest
                failures.append(f"{court}: {e!r}")
                self.stderr.write(self.style.ERROR(f"— {court} search FAILED: {e!r}"))
                continue

            rows_total += len(results)
            for row in results:
                cluster = row.get("cluster_id") or row.get("id")
                case_name = _first(row, "caseName", "case_name")
                if not cluster or not case_name:
                    unusable += 1
                    continue
                ext_ref = f"CL:{cluster}"
                filed = _first(row, "dateFiled", "date_filed", default=None)
                try:
                    filed_date = dt.date.fromisoformat(str(filed)[:10]) if filed else None
                except ValueError:
                    filed_date = None
                snippet = _first(row, "snippet", "text", default="")
                abs_url = _first(row, "absolute_url", default="")
                url = f"https://www.courtlistener.com{abs_url}" if abs_url.startswith("/") else abs_url

                res = open_detected(
                    external_ref=ext_ref,
                    title=f"{spec['label']}: {case_name[:200]}",
                    summary=(f"[{spec['label']} · filed {filed_date or 'unknown'}]\n"
                             f"{snippet[:600]}\n{url}"),
                    index=index,
                    text=f"{case_name} {snippet}",
                    jurisdiction="US",
                    item_kind=ItemKind.COURT_OPINION,
                    source_url=url or None,
                    published_date=filed_date,
                    feed=feed,
                    dry_run=o["dry_run"],
                )
                if res.skipped:
                    skipped += 1
                    continue
                opened += 1
                line = f"{case_name[:48]:<48} {filed_date or '—'}  score {res.score:>3}  {score_summary(res.signals)}"
                if o["dry_run"]:
                    self.stdout.write(self.style.WARNING(f"NEW  {line}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"DETECTED {res.change_code}: {line}"))

        if not o["dry_run"] and feed is not None:
            feed.last_polled_at = timezone.now()
            feed.last_result_note = (f"ok · {rows_total} rows / {opened} opened / {skipped} already-known"
                                     + (f" / FAILED: {'; '.join(failures)}" if failures else ""))
            feed.save(update_fields=["last_polled_at", "last_result_note"])

        self.stdout.write("\n" + "=" * 60)
        verb = "would open" if o["dry_run"] else "opened"
        self.stdout.write(f"fetch_court_opinions: {rows_total} rows / {opened} {verb} / "
                          f"{skipped} already-known / {unusable} unusable row(s)")
        if failures:
            self.stdout.write(self.style.WARNING(f"  ⚠ {len(failures)} court search(es) failed: "
                                                 + "; ".join(failures)))
        self.stdout.write("=" * 60)
        if len(failures) == len(courts):
            raise CommandError("Every court search failed — treat as an arm outage.")
