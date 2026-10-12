from datetime import datetime, timezone

from backend.api.chat import _local_day_start_utc


def test_daily_quota_starts_at_midnight_in_profile_timezone():
    # At 2026-10-12 08:00 UTC, Moscow is already at 11:00 local time.
    now = datetime(2026, 10, 12, 8, tzinfo=timezone.utc)
    assert _local_day_start_utc(now, "Europe/Moscow") == datetime(
        2026, 10, 11, 21, tzinfo=timezone.utc
    )


def test_daily_quota_boundary_respects_dst_timezone_offset():
    # New York local midnight on the 2026 spring DST transition is 05:00 UTC.
    now = datetime(2026, 3, 8, 16, tzinfo=timezone.utc)
    assert _local_day_start_utc(now, "America/New_York") == datetime(
        2026, 3, 8, 5, tzinfo=timezone.utc
    )


def test_daily_quota_accepts_naive_utc_datetime():
    now = datetime(2026, 10, 12, 8)
    assert _local_day_start_utc(now, "Europe/Moscow") == datetime(
        2026, 10, 11, 21, tzinfo=timezone.utc
    )
