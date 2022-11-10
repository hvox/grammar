from grammar import Grammar
from clr_parser import parse as parse_clr


def test_simplest_case():
    grammar = Grammar([("S", ("C", "C")), ("C", ("c", "C")), ("C", ("d",))])
    tokens = [(char, (i, char)) for i, char in enumerate("cdd")]
    ast = parse_clr(*grammar.construct_clr_parsing_table(), {}, tokens)
    assert ast == ("S", ("C", (0, "c"), ("C", (1, "d"))), ("C", (2, "d")))


def test_two_plus_two():
    rules = {
        ("sum", ("product",)): (lambda x: x),
        ("sum", ("sum", "+", "product")): (lambda x, _, y: x + y),
        ("product", ("number",)): (lambda x: x),
        ("product", ("product", "*", "number")): (lambda x, _, y: x * y),
    }
    grammar = Grammar(rules.keys())

    def scan(source):
        return [("number", int(w)) if w.isdigit() else (w, w) for w in source.split()]

    def evaluate(source):
        return parse_clr(*grammar.construct_clr_parsing_table(), rules, scan(source))

    assert evaluate("2 + 2") == 4
    assert evaluate("2 + 2 * 4") == 10
    assert evaluate("2 * 123 + 32 * 321 * 908 + 21 * 32037") == 9999999


def test_very_simple_arithmetic():
    rules = {
        ("sum", ("product",)): (lambda x: x),
        ("sum", ("sum", "+", "product")): (lambda x, _, y: x + y),
        ("product", ("factor",)): (lambda x: x),
        ("product", ("product", "*", "factor")): (lambda x, _, y: x * y),
        ("factor", ("(", "sum", ")")): (lambda *x: x[1]),
        ("factor", ("number",)): (lambda x: x),
    }
    grammar = Grammar(rules.keys())
    source = "2 + 3 * 23 + ( 32 * 34 )"
    tokens = [("number", int(word)) if word.isdigit() else (word, word) for word in source.split()]
    result = parse_clr(*grammar.construct_clr_parsing_table(), rules, tokens)
    assert result == 1159
