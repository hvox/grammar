from typing import Callable
from grammar import Rule, Grammar
from contextlib import suppress as suppress_exception
from clr_parser import parse


def lr_parser(rules: dict[Rule, Callable] | list[Rule]) -> Callable:
    grammar = Grammar(rules.keys() if isinstance(rules, dict) else rules)
    rules = rules if isinstance(rules, dict) else {}
    with suppress_exception(ValueError):
        actions, gotos = grammar.construct_slr_parsing_table()
        return lambda source: parse(actions, gotos, rules, source)
    with suppress_exception(ValueError):
        actions, gotos = grammar.construct_lalr_parsing_table()
        return lambda source: parse(actions, gotos, rules, source)
    with suppress_exception(ValueError):
        actions, gotos = grammar.construct_clr_parsing_table()
        return lambda source: parse(actions, gotos, rules, source)
    raise ValueError("Grammar is too complex")
