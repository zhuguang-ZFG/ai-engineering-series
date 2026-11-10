"""Exercise seed: the 1001 g boundary deliberately undercharges."""


def fee_cents(grams):
    if type(grams) is not int:
        raise TypeError("grams must be an integer")
    if not 1 <= grams <= 30_000:
        raise ValueError("grams must be between 1 and 30000")
    kilograms = grams // 1000  # Deliberate exercise defect.
    return 600 + max(0, kilograms - 1) * 200
