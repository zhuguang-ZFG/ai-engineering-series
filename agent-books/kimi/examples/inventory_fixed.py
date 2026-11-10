"""Reference solution: positive integer quantities, including all remaining stock."""


def reserve(stock: int, quantity: int) -> int:
    if type(stock) is not int or type(quantity) is not int:
        raise TypeError("stock and quantity must be integers")
    if stock < 0:
        raise ValueError("stock must not be negative")
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    if quantity > stock:
        raise ValueError("insufficient stock")
    return stock - quantity
