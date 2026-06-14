from __future__ import annotations

"""Currency and money formatting helpers."""

from decimal import Decimal


def format_currency(amount: Decimal | float, symbol: str = "$") -> str:
    """Format a numeric amount as currency string."""
    value = Decimal(str(amount))
    return f"{symbol}{value:,.2f}"


def to_decimal(value: float | str | Decimal) -> Decimal:
    """Safely convert a value to Decimal."""
    return Decimal(str(value))
