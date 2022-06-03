import context
import pytest
from collections import defaultdict
from grammar import Grammar, ε, τ
from grammar.llparser import construct_table, Parser


@pytest.fixture
def grammar():
    return Grammar(
        {"S", "F"},
        {"OPEN", "PLUS", "CLOSE", "a"},
        {"S": {("F",), ("OPEN", "S", "PLUS", "F", "CLOSE")}, "F": {("a",)}},
        "S",
    )


def test_table_construction(grammar):
    table = construct_table(grammar)
    assert table.keys() == {("S", "a"), ("S", "OPEN"), ("F", "a")}


def test_the_parser(grammar):
    parse = Parser(grammar).parse
    assert parse(["OPEN", "a", "PLUS", "a", "CLOSE"]) is not None


def test_parse_sum():
    grm = Grammar(
        {"S", "T"},
        set(map(ord, "(+)0123456789")),
        {
            "S": {
                ("T",),
                (ord("("), "S", ord("+"), "S", ord(")")),
            },
            "T": {
                (),
                (ord("0"), "T"),
                (ord("1"), "T"),
                (ord("2"), "T"),
                (ord("3"), "T"),
                (ord("4"), "T"),
                (ord("5"), "T"),
                (ord("6"), "T"),
                (ord("7"), "T"),
                (ord("8"), "T"),
                (ord("9"), "T"),
            },
        },
        "S",
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
        symbol: (lambda *a: len(a) + 1) for symbol in grammar.variables
    }
    assert parser.parse(["OPEN", "a", "PLUS", "a", "CLOSE"]) == 6
