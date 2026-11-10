# Invoice practice repository

Only change the pricing implementation and its behavioral checks when asked.
Keep total(unit_price: str, quantity: int, discount: str = "0") -> Decimal.
Price and discount are decimal strings. Price is 0–1000000 inclusive.
Quantity is an integer (not bool), 0–1000000 inclusive.
Discount is 0–1 inclusive. Reject non-finite values with ValueError.
Round once, at the end, to two decimal places using ROUND_HALF_UP.

Run python check_pricing.py. Its successful exit means the known broken
baseline still fails and the reference implementation passes all cases.
Do not modify pricing_broken.py to make the exercise appear to pass.
This fixture has no network requirement or production data.
