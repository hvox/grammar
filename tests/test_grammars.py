import context
import pytest
from grammar import Grammar, ε, τ


@pytest.fixture
def grammar():
    return Grammar(
        [
            ("S", ("F",)),
            ("S", ("OPEN", "S", "PLUS", "F", "CLOSE")),
            ("F", ("a",)),
        ]
    )


def test_followers(grammar):
    assert grammar.followers == {"S": {"PLUS", τ}, "F": {"CLOSE", "PLUS", τ}}


def test_hashing(grammar):
    grm1 = Grammar([("S", ("f", "f"))])
    grm2 = grammar
    grm3 = eval(repr(grm2))
    assert hash(grm1) != hash(grm2)
    assert hash(grm2) == hash(grm3)


def test_serialization(grammar):
    grm1 = grammar
    grm2 = eval(repr(grm1))
    assert repr(grm1) == repr(grm2)
    assert grm1 == grm2


def test_prefixes(grammar):
    assert grammar.prefixes == {
        "S": {"a", "OPEN"},
        "F": {"a"},
        (): {ε},
        ("F",): {"a"},
        ("OPEN", "S", "PLUS", "F", "CLOSE"): {"OPEN"},
        ("S", "PLUS", "F", "CLOSE"): {"OPEN", "a"},
        ("PLUS", "F", "CLOSE"): {"PLUS"},
        ("F", "CLOSE"): {"a"},
        ("CLOSE",): {"CLOSE"},
        ("a",): {"a"},
    }
