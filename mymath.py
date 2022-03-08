from operator import add, sub, mul
from fractions import Fraction


class Rational(Fraction):
    def __str__(self):
        if self.denominator == 1:
            return str(self.numerator)
        return f"{self.numerator}/{self.denominator}"


def sign(x):
    return (x > 0) - (x < 0)


def mod(x, y):
    return x % abs(y)


def floor_div(x, y):
    return x // abs(y) * sign(y)


def div(x, y, default_value=None):
    return x / y if y != 0 else default_value
