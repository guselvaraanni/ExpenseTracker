"""Date parsing and range helpers."""

from datetime import date, datetime, timedelta
from typing import Tuple


def today_iso() -> str:
    """Return today's date as ISO string (YYYY-MM-DD)."""
    return date.today().isoformat()


def parse_iso_date(value: str) -> date:
    """Parse an ISO date string into a date object."""
    return date.fromisoformat(value)


def date_range_days(days: int) -> Tuple[datetime, datetime]:
    """Return start and end datetime for a rolling day range ending today."""
    end = datetime.now()
    start = end - timedelta(days=days)
    return start, end
