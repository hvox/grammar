from grammar import Grammar, Rule


def test_prefixes():
    rules = [
        ("START", ("FIRST", "LAST")),
        ("FIRST", ("(", "?", ")")),
        ("LAST", ("[", "!", "]")),
        ("LAST", ("{", "}")),
    ]
    prefixes = {
        "START": {"("}, "FIRST": {"("}, "LAST": {"[", "{"},
        "(": {"("}, "?": {"?"}, ")": {")"}, "!": {"!"},
        "[": {"["}, "]": {"]"}, "{": {"{"}, "}": {"}"}
    }
    assert Grammar(rules).prefixes == prefixes


def test_followers():
    rules = [
        ("START", ("FIRST", "LAST")),
        ("FIRST", ("(", "?", ")")),
        ("LAST", ("[", "!", "]")),
        ("LAST", ("{", "}")),
    ]
    followers = {
        "START": {None}, "FIRST": {"[", "{"}, "LAST": {None},
        "(": {"?"}, "?": {")"}, ")": {"[", "{"}, "[": {"!"},
        "!": {"]"}, "]": {None}, "{": {"}"}, "}": {None}
    }
    assert Grammar(rules).followers == followers


def test_ll1_table_generation():
    rules = [
        ("E", ("T", "E'")),
        ("E'", ("+", "T", "E'")),
        ("E'", ()),
        ("T", ("F", "T'")),
        ("T'", ("*", "F", "T'")),
        ("T'", ()),
        ("F", ("(", "E", ")")),
        ("F", ("id",)),
    ]
    table = {
        ("E", "("): ("E", ("T", "E'")),
        ("E", "id"): ("E", ("T", "E'")),
        ("E'", "+"): ("E'", ("+", "T", "E'")),
        ("E'", None): ("E'", ()),
        ("E'", ")"): ("E'", ()),
        ("T", "("): ("T", ("F", "T'")),
        ("T", "id"): ("T", ("F", "T'")),
        ("T'", "*"): ("T'", ("*", "F", "T'")),
        ("T'", "+"): ("T'", ()),
        ("T'", None): ("T'", ()),
        ("T'", ")"): ("T'", ()),
        ("F", "("): ("F", ("(", "E", ")")),
        ("F", "id"): ("F", ("id",)),
    }
    assert Grammar(rules).construct_ll1_parsing_table() == table


def test_slr_table_generation():
    rules = [
        ("E", ("E", "+", "T")),
        ("E", ("T",)),
        ("T", ("T", "*", "F")),
        ("T", ("F",)),
        ("F", ("(", "E", ")")),
        ("F", ("id",)),
    ]
    expected_action_table = {
        (0, "("): ("shift", 4),
        (0, "id"): ("shift", 5),
        (1, "+"): ("shift", 6),
        (1, None): ("accept",),
        (2, "*"): ("shift", 7),
        (2, None): ("reduce", Rule(head="E", body=("T",))),
        (2, "+"): ("reduce", Rule(head="E", body=("T",))),
        (2, ")"): ("reduce", Rule(head="E", body=("T",))),
        (3, None): ("reduce", Rule(head="T", body=("F",))),
        (3, "+"): ("reduce", Rule(head="T", body=("F",))),
        (3, "*"): ("reduce", Rule(head="T", body=("F",))),
        (3, ")"): ("reduce", Rule(head="T", body=("F",))),
        (4, "("): ("shift", 4),
        (4, "id"): ("shift", 5),
        (5, None): ("reduce", Rule(head="F", body=("id",))),
        (5, "+"): ("reduce", Rule(head="F", body=("id",))),
        (5, "*"): ("reduce", Rule(head="F", body=("id",))),
        (5, ")"): ("reduce", Rule(head="F", body=("id",))),
        (6, "("): ("shift", 4),
        (6, "id"): ("shift", 5),
        (7, "("): ("shift", 4),
        (7, "id"): ("shift", 5),
        (8, "+"): ("shift", 6),
        (8, ")"): ("shift", 11),
        (9, "*"): ("shift", 7),
        (9, None): ("reduce", Rule(head="E", body=("E", "+", "T"))),
        (9, "+"): ("reduce", Rule(head="E", body=("E", "+", "T"))),
        (9, ")"): ("reduce", Rule(head="E", body=("E", "+", "T"))),
        (10, None): ("reduce", Rule(head="T", body=("T", "*", "F"))),
        (10, "+"): ("reduce", Rule(head="T", body=("T", "*", "F"))),
        (10, "*"): ("reduce", Rule(head="T", body=("T", "*", "F"))),
        (10, ")"): ("reduce", Rule(head="T", body=("T", "*", "F"))),
        (11, None): ("reduce", Rule(head="F", body=("(", "E", ")"))),
        (11, "+"): ("reduce", Rule(head="F", body=("(", "E", ")"))),
        (11, "*"): ("reduce", Rule(head="F", body=("(", "E", ")"))),
        (11, ")"): ("reduce", Rule(head="F", body=("(", "E", ")"))),
    }
    expected_goto_table = {
        (0, "E"): 1, (0, "T"): 2, (0, "F"): 3,
        (4, "E"): 8, (4, "T"): 2, (4, "F"): 3,
        (6, "T"): 9, (6, "F"): 3, (7, "F"): 10
    }
    actions, gotos = Grammar(rules).construct_slr_parsing_table()
    assert actions == expected_action_table
    assert gotos == expected_goto_table


def test_clr_table_generation():
    rules = [
        ("S", ("C", "C")),
        ("C", ("c", "C")),
        ("C", ("d",)),
    ]
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
    actions, gotos = Grammar(rules).construct_clr_parsing_table()
    assert actions == expected_action_table
    assert gotos == expected_goto_table


def test_lalr_table_generation():
    rules = [
        ("S", ("C", "C")),
        ("C", ("c", "C")),
        ("C", ("d",)),
    ]
    expected_action_table = {
        (0, "c"): ("shift", 3),
        (0, "d"): ("shift", 4),
        (1, None): ("accept",),
        (2, "c"): ("shift", 3),
        (2, "d"): ("shift", 4),
        (3, "c"): ("shift", 3),
        (3, "d"): ("shift", 4),
        (4, "d"): ("reduce", Rule(head="C", body=("d",))),
        (4, "c"): ("reduce", Rule(head="C", body=("d",))),
        (4, None): ("reduce", Rule(head="C", body=("d",))),
        (5, None): ("reduce", Rule(head="S", body=("C", "C"))),
        (6, None): ("reduce", Rule(head="C", body=("c", "C"))),
        (6, "c"): ("reduce", Rule(head="C", body=("c", "C"))),
        (6, "d"): ("reduce", Rule(head="C", body=("c", "C"))),
    }
    expected_goto_table = {(0, 'S'): 1, (0, 'C'): 2, (2, 'C'): 5, (3, 'C'): 6}
    actions, gotos = Grammar(rules).construct_lalr_parsing_table()
    assert actions == expected_action_table
    assert gotos == expected_goto_table
