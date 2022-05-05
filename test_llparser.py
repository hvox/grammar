import pytest
from collections import defaultdict
from grammars import Grammar, ε, τ
from llparser import construct_table, Parser


@pytest.fixture
def grammar():
    return Grammar(
        [
            ("S", ("F",)),
            ("S", ("OPEN", "S", "PLUS", "F", "CLOSE")),
            ("F", ("a",)),
        ]
    )


def test_table_construction(grammar):
    table = construct_table(grammar)
    assert table == {("S", "a"): 0, ("S", "OPEN"): 1, ("F", "a"): 2}


def test_the_parser(grammar):
    parse = Parser(grammar).parse
    assert parse(["OPEN", "a", "PLUS", "a", "CLOSE"]) is not None


def test_parse_sum():
    grm = Grammar(
        [
            ("S", ("T",)),
            ("S", (ord("("), "S", ord("+"), "S", ord(")"))),
            ("T", (ord("0"), "T")),
            ("T", (ord("1"), "T")),
            ("T", (ord("2"), "T")),
            ("T", (ord("3"), "T")),
            ("T", (ord("4"), "T")),
            ("T", (ord("5"), "T")),
            ("T", (ord("6"), "T")),
            ("T", (ord("7"), "T")),
            ("T", (ord("8"), "T")),
            ("T", (ord("9"), "T")),
            ("T", ()),
        ]
    )

    def parse_sum(*args):
        if len(args) == 1:
            return int(args[0])
        return int(args[1]) + int(args[3])

    def parse_number(*args):
        if len(args) > 0:
            return chr(args[0]) + args[1]
        return ""

    actions = {"T": parse_number, "S": parse_sum}
    parse = Parser(grm, actions=actions).parse
    src = "(123+(321+555))"
    assert parse(b"(123+(321+555))") == 999


def test_actions(grammar):
    parser = Parser(grammar)
    parser.actions = {
        symbol: (lambda *a: len(a) + 1) for symbol in grammar.nonterminals
    }
    assert parser.parse(["OPEN", "a", "PLUS", "a", "CLOSE"]) == 6
