import pytest
from lexer import get_very_simple_lexer

scan = get_very_simple_lexer("+-*/()")


@pytest.mark.parametrize("expr, tokens", [
    ("2 + 2", [('number', 2), ('+', '+'), ('number', 2)]),
    ("2 + 2 * 123 / 15", [
        ('number', 2), ('+', '+'), ('number', 2), ('*', '*'),
        ('number', 123), ('/', '/'), ('number', 15)]),
    ("(123)*42", [('(', '('), ('number', 123), (')', ')'), ('*', '*'), ('number', 42)]),
    ("var x + variable y", [('identifier', 'var x '), ('+', '+'), ('identifier', 'variable y')]),
    ("var x*d y", [('identifier', 'var x'), ('*', '*'), ('identifier', 'd y')]),
    ("d y/d x(5)", [
        ('identifier', 'd y'), ('/', '/'), ('identifier', 'd x'),
        ('(', '('), ('number', 5), (')', ')')]),
    ("f(x)", [('identifier', 'f'), ('(', '('), ('identifier', 'x'), (')', ')')]),
])
def test_very_simple_lexer(expr, tokens):
    if list(scan(expr)) != tokens:
        print(list(scan(expr))[:-1])
    assert list(scan(expr)) == tokens + [(None, None)]
