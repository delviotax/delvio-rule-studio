"""Shared helpers for the change-register funnel commands (change_register /
detect_source_changes / fetch_federal_register / fetch_irb / fetch_ecfr_title26 / fetch_irs_drop)."""
from dataclasses import dataclass, field

from django.db import IntegrityError, transaction
from django.utils import timezone

from sources.models import ChangeDetectionSource, ChangeRegisterItem, ChangeStatus


def next_change_code(year: int) -> str:
    """CR-<year>-<zero-padded seq>, sequential within the year."""
    prefix = f"CR-{year}-"
    seqs = []
    for c in ChangeRegisterItem.objects.filter(change_code__startswith=prefix).values_list("change_code", flat=True):
        tail = c.rsplit("-", 1)[-1]
        if tail.isdigit():
            seqs.append(int(tail))
    return f"{prefix}{(max(seqs) + 1) if seqs else 1:03d}"


def parse_csv(val):
    """'a, b ,c' -> ['a','b','c']; falsy -> []."""
    return [v.strip() for v in val.split(",") if v.strip()] if val else []


@dataclass
class OpenResult:
    """Outcome of one attempted register insert."""
    created: bool = False
    skipped: bool = False           # external_ref already known (idempotent no-op)
    score: int | None = None
    signals: list = field(default_factory=list)
    change_code: str | None = None
    item: ChangeRegisterItem | None = None


def open_detected(
    *,
    external_ref: str,
    title: str,
    summary: str,
    index=None,
    text: str | None = None,
    forms=(),
    sections=(),
    cfr=(),
    jurisdiction: str = "US",
    item_kind: str | None = None,
    source_url: str | None = None,
    published_date=None,
    tax_year: int | None = None,
    affected_forms=None,
    authority_source=None,
    authority_version=None,
    feed=None,
    dry_run: bool = False,
) -> OpenResult:
    """Score an item and open it as DETECTED — the one path every automated arm uses.

    Centralised so the funnel's invariants can't drift arm-to-arm:

      · IDEMPOTENT on `external_ref` (namespace it per-arm — see the model's help_text).
      · ALWAYS CREATES when the ref is new. The relevance score is attached, never consulted
        as a gate. An arm that wants to filter must do so with an EXACT structured match
        BEFORE calling this, and must log what it dropped — see `fetch_irs_drafts`.
      · Never crosses a gate: status is DETECTED, full stop.

    `index` is a `relevance.PerimeterIndex`; omit it to record without scoring (score stays
    null, which the digest renders as "unscored" rather than as zero).
    """
    if ChangeRegisterItem.objects.filter(external_ref=external_ref).exists():
        return OpenResult(skipped=True)

    score_val, signals = None, []
    if index is not None:
        from sources.relevance import score as _score
        score_val, signals = _score(
            text, index=index, forms=forms, sections=sections, cfr=cfr, jurisdiction=jurisdiction)

    if dry_run:
        return OpenResult(created=True, score=score_val, signals=signals)

    year = timezone.now().year
    # next_change_code() scans-then-increments; two arms racing can collide on change_code.
    # Retry rather than lose an item. (Arms run serially today, but the cost of insurance is 6 lines.)
    for _ in range(5):
        try:
            with transaction.atomic():
                code = next_change_code(year)
                item = ChangeRegisterItem.objects.create(
                    change_code=code,
                    title=title[:255],
                    summary=summary,
                    jurisdiction_code=jurisdiction,
                    tax_year=tax_year,
                    detected_via=ChangeDetectionSource.FEED_POLL,
                    status=ChangeStatus.DETECTED,
                    external_ref=external_ref,
                    item_kind=item_kind,
                    source_url=source_url,
                    published_date=published_date,
                    relevance_score=score_val,
                    relevance_signals=signals,
                    affected_forms=list(affected_forms or []),
                    authority_source=authority_source,
                    authority_version=authority_version,
                    feed=feed,
                )
            return OpenResult(created=True, score=score_val, signals=signals, change_code=code, item=item)
        except IntegrityError:
            # Either a change_code race (retry gets a fresh one) or the external_ref unique
            # constraint firing because a sibling arm just inserted it — re-check and bail out.
            if ChangeRegisterItem.objects.filter(external_ref=external_ref).exists():
                return OpenResult(skipped=True)
    raise IntegrityError(f"could not allocate a change_code for {external_ref!r} after 5 attempts")
