"""Reference solution for the book's isolated invoice exercise."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def total(unit_price: str, quantity: int, discount: str = "0") -> Decimal:
    if type(quantity) is not int or not 0 <= quantity <= 1_000_000:
        raise ValueError("quantity must be an integer between 0 and 1000000")
    if not isinstance(unit_price, str) or not isinstance(discount, str):
        raise ValueError("price and discount must be decimal strings")
    try:
        price, rate = Decimal(unit_price), Decimal(discount)
    except InvalidOperation as exc:
        raise ValueError("price and discount must be decimal strings") from exc
    if not price.is_finite() or not rate.is_finite():
        raise ValueError("price and discount must be finite")
    if not Decimal("0") <= price <= Decimal("1000000"):
        raise ValueError("price must be between 0 and 1000000")
    if not Decimal("0") <= rate <= Decimal("1"):
        raise ValueError("discount must be between 0 and 1")
    return (price * quantity * (Decimal("1") - rate)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP,
    )
