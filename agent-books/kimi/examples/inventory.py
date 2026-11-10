"""Deliberately faulty inventory reservation for the book's review exercise."""


def reserve(stock: int, quantity: int) -> int:
    if quantity >= stock:
        raise ValueError("insufficient stock")
    return stock - quantity
