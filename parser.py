from typing import Callable
from grammar import Rule, Grammar
from contextlib import suppress as suppress_exception
from clr_parser import parse


def lr_parser(rules: dict[Rule, Callable] | list[Rule]) -> Callable:
    grammar = Grammar(rules.keys() if isinstance(rules, dict) else rules)
    rules = rules if isinstance(rules, dict) else {}
    with suppress_exception(ValueError | AssertionError):
        actions, gotos = grammar.construct_slr_parsing_table()
        return lambda source: parse(actions, gotos, rules, source)
    with suppress_exception(ValueError | AssertionError):
        actions, gotos = grammar.construct_lalr_parsing_table()
        return lambda source: parse(actions, gotos, rules, source)
    with suppress_exception(ValueError | AssertionError):
        actions, gotos = grammar.construct_clr_parsing_table()
        return lambda source: parse(actions, gotos, rules, source)
    raise ValueError("Grammar is too complex")


def ast_to_str(ast) -> str:
    (begin, end), head, *body = ast
    header = f"{head} {begin}..{end-1}"
    if not body:
        return header
    if len(body) == 1 and isinstance(body[0], str):
        return header + " " + repr(body[0])
    first = ("├── " + ast_to_str(x).replace("\n", "\n│   ") for x in body[:-1])
    last = r"└── " + ast_to_str(body[-1]).replace("\n", "\n    ")
    return "\n".join((header, *first, last))
