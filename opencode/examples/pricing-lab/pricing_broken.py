"""Original exercise: converting to int loses cents before the discount."""
from decimal import Decimal


def total(unit_price: str, quantity: int, discount: str = "0") -> Decimal:
    subtotal = int(Decimal(unit_price) * quantity)
    return Decimal(subtotal) * (Decimal("1") - Decimal(discount))
