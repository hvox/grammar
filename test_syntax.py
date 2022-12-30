from syntax import Syntax, Rule


def test_prefixes():
    rules = {
        ("start", ("first", "last")): None,
        ("first", ("(", "?", ")")): None,
        ("last", ("[", "!", "]")): None,
        ("last", ("{", "}")): None,
    }
    expected_prefixes = {
        "start": {"("}, "first": {"("}, "last": {"[", "{"},
        "(": {"("}, "?": {"?"}, ")": {")"}, "!": {"!"},
        "[": {"["}, "]": {"]"}, "{": {"{"}, "}": {"}"}
    }
    get_prefixes = Syntax(rules).get_prefixes
    for symbol, symbol_prefixes in expected_prefixes.items():
        assert get_prefixes(symbol) == symbol_prefixes


def test_clr_table_generation():
    rules = {
        ("S", ("C", "C")): None,
        ("C", ("c", "C")): None,
        ("C", ("d",)): None,
    }
    expected_action_table = {
        (0, "c"): ("shift", 3),
        (0, "d"): ("shift", 4),
        (1, None): ("accept",),
        (2, "c"): ("shift", 6),
        (2, "d"): ("shift", 7),
        (3, "c"): ("shift", 3),
        (3, "d"): ("shift", 4),
        (4, "d"): ("reduce", Rule(head="C", body=("d",))),
        (4, "c"): ("reduce", Rule(head="C", body=("d",))),
        (5, None): ("reduce", Rule(head="S", body=("C", "C"))),
        (6, "c"): ("shift", 6),
        (6, "d"): ("shift", 7),
        (7, None): ("reduce", Rule(head="C", body=("d",))),
        (8, "d"): ("reduce", Rule(head="C", body=("c", "C"))),
        (8, "c"): ("reduce", Rule(head="C", body=("c", "C"))),
        (9, None): ("reduce", Rule(head="C", body=("c", "C"))),
    }
    expected_goto_table = {(0, "S"): 1, (0, "C"): 2, (2, "C"): 5, (3, "C"): 8, (6, "C"): 9}
    actions, gotos = Syntax(rules).get_clr_parsing_table(root_node="S")
    assert actions == expected_action_table
    assert gotos == expected_goto_table


def test_rule_parsing():
    rules = {
        "S C C": None,
        "C c C": None,
        "C d": None,
    }
    expected_action_table = {
        (0, "c"): ("shift", 3),
        (0, "d"): ("shift", 4),
        (1, None): ("accept",),
        (2, "c"): ("shift", 6),
        (2, "d"): ("shift", 7),
        (3, "c"): ("shift", 3),
        (3, "d"): ("shift", 4),
        (4, "d"): ("reduce", Rule(head="C", body=("d",))),
        (4, "c"): ("reduce", Rule(head="C", body=("d",))),
        (5, None): ("reduce", Rule(head="S", body=("C", "C"))),
        (6, "c"): ("shift", 6),
        (6, "d"): ("shift", 7),
        (7, None): ("reduce", Rule(head="C", body=("d",))),
        (8, "d"): ("reduce", Rule(head="C", body=("c", "C"))),
        (8, "c"): ("reduce", Rule(head="C", body=("c", "C"))),
        (9, None): ("reduce", Rule(head="C", body=("c", "C"))),
    }
    expected_goto_table = {(0, "S"): 1, (0, "C"): 2, (2, "C"): 5, (3, "C"): 8, (6, "C"): 9}
    actions, gotos = Syntax(rules).get_clr_parsing_table(root_node="S")
    assert actions == expected_action_table
    assert gotos == expected_goto_table
