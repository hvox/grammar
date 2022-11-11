from re import compile as re

import pytest

from lexer import construct_lexer, get_very_simple_lexer


@pytest.mark.parametrize("expr, tokens", [
    ("2 + 2", [('number', 2), ('+', '+'), ('number', 2)]),
    ("2 + 2 * 123 / 15", [
        ('number', 2), ('+', '+'), ('number', 2), ('*', '*'),
        ('number', 123), ('/', '/'), ('number', 15)]),
    ("(123)*42", [('(', '('), ('number', 123), (')', ')'), ('*', '*'), ('number', 42)]),
    ("var x + variable y", [('identifier', 'var x'), ('+', '+'), ('identifier', 'variable y')]),
    ("var x*d y", [('identifier', 'var x'), ('*', '*'), ('identifier', 'd y')]),
    ("d y/d x(5)", [
        ('identifier', 'd y'), ('/', '/'), ('identifier', 'd x'),
        ('(', '('), ('number', 5), (')', ')')]),
    ("f(x)", [('identifier', 'f'), ('(', '('), ('identifier', 'x'), (')', ')')]),
])
def test_very_simple_lexer(expr, tokens):
    scan = get_very_simple_lexer("+-*/()")
    assert list(scan(expr)) == tokens + [(None, None)]


@pytest.mark.parametrize("expr, tokens", [
    ("2 + 2", [('number', 2), ('+', '+'), ('number', 2)]),
    ("2 + 2 * 123 / 15", [
        ('number', 2), ('+', '+'), ('number', 2), ('*', '*'),
        ('number', 123), ('/', '/'), ('number', 15)]),
    ("(123)*42", [('(', '('), ('number', 123), (')', ')'), ('*', '*'), ('number', 42)]),
    ("var x + variable y", [('identifier', 'var x'), ('+', '+'), ('identifier', 'variable y')]),
    ("var x*d y", [('identifier', 'var x'), ('*', '*'), ('identifier', 'd y')]),
    ("d y/d x(5)", [
        ('identifier', 'd y'), ('/', '/'), ('identifier', 'd x'),
        ('(', '('), ('number', 5), (')', ')')]),
    ("f(x)", [('identifier', 'f'), ('(', '('), ('identifier', 'x'), (')', ')')]),
])
def test_scanner(expr, tokens):
    scan = construct_lexer({
        re(r"\s+"): None,
        re(r"[-+*/()]"): lambda _, s: (s, s),
        re(r"\d+"): lambda _, s: ("number", int(s)),
        re(r"\w+(\s+\w+)*"): lambda _, s: ("identifier", s),
    })
    assert list(scan(expr)) == tokens
