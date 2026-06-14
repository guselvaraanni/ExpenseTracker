"""Unit tests for utility helpers."""

from decimal import Decimal

from app.utils.dates import date_range_days, parse_iso_date, today_iso
from app.utils.money import format_currency, to_decimal


def test_today_iso_format() -> None:
    """today_iso returns YYYY-MM-DD format."""
    assert len(today_iso()) == 10
    assert today_iso().count("-") == 2


def test_parse_iso_date() -> None:
    """parse_iso_date parses valid ISO strings."""
    result = parse_iso_date("2026-06-14")
    assert result.year == 2026
    assert result.month == 6
    assert result.day == 14


def test_date_range_days() -> None:
    """date_range_days returns a valid start/end tuple."""
    start, end = date_range_days(30)
    assert start < end


def test_format_currency() -> None:
    """format_currency formats decimal values."""
    assert format_currency(Decimal("1234.5")) == "$1,234.50"


def test_to_decimal() -> None:
    """to_decimal converts numeric values."""
    assert to_decimal(10.5) == Decimal("10.5")
