from operator import add, sub, mul


def sign(x):
    return (x > 0) - (x < 0)


def mod(x, y):
    return x % abs(y)


def floor_div(x, y):
    return x // abs(y) * sign(y)


def div(x, y, default_value=None):
    return x / y if y != 0 else default_value
