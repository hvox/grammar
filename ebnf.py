from parser import lr_parser
from pathlib import Path
from re import compile as re
from typing import Any, Iterable
from lexer import construct_lexer

# from lib.deterministic import DeterministicSet as set

# Extended Backus–Naur form
#    =    definition
#    ,    concatenation
#    |    alternation
# [ ... ] optional
# { ... } repetition
# ( ... ) grouping
# " ... " terminal
# ' ... ' terminal
# ? ... ? special sequence
#    -    exception  <-- not supported yet
#    ;    termination


class EBNF:
    def __init__(self, rules: Iterable[tuple[str, Any]]):
        self.rules = dict(rules)

    def __repr__(self):
        def node_repr(node, operator_lvl=0):
            match node:
                case "alt", *alts:
                    result = " | ".join(node_repr(alt, 1) for alt in alts)
                    return result if operator_lvl < 1 else f"({result})"
                case "cat", *terms:
                    result = ", ".join(node_repr(term, 2) for term in terms)
                    return result if operator_lvl < 2 else f"({result})"
                case "opt", value:
                    return "[" + node_repr(value) + "]"
                case "rep", value:
                    return "{" + node_repr(value) + "}"
                case terminal:
                    return terminal
        result = []
        for head, body in self.rules.items():
            if body[0] != "alt":
                result.append(f"{head} = {node_repr(body)};")
                continue
            body = [node_repr(alt, 1) for alt in body[1:]]
            if sum(map(len, body)) + 3 * len(body) + 1 + len(head) <= 72:
                result.append(f"{head} = {' | '.join(body)};")
                continue
            lines = [head]
            for i, alt in enumerate(body):
                if len(lines[-1]) + 3 + len(alt) <= 71 + (i != len(body) - 1):
                    lines[-1] += " | " + alt
                else:
                    lines.append(" " * len(head) + " | " + alt)
            lines[0] = lines[0].replace("|", "=", 1)
            lines[-1] += ";"
            result.extend(lines)
        return "\n".join(result)


scan_ebnf_tokens = construct_lexer({
    re(r"\s+"): None,
    re(r"[-|,(){}\[\]=;]"): lambda _, s: (s, s),
    re(r"\w+(\s+\w+)*"): lambda _, s: ("identifier", s),
    re(r"\?[^?]+\?"): lambda _, s: ("special sequence", s),
    re(r'"[^"]+"'): lambda _, s: ("terminal", s),
    re(r"'[^']+'"): lambda _, s: ("terminal", s),
})
parse_ebnf_tokens = lr_parser({
    ("defs", ("def", "defs")): lambda x, y: [x] + y,
    ("defs", ("def",)): lambda x: [x],
    ("def", ("identifier", "=", "alt", ";")): lambda var, _, expr, __: (var, expr),
    ("alt", ("alt", "|", "cat")): lambda x, _, y: x + (y,) if x[0] == "alt" else ("alt", x, y),
    ("alt", ("cat",)): lambda x: x,
    ("cat", ("cat", ",", "term")): lambda x, _, y: x + (y,) if x[0] == "cat" else ("cat", x, y),
    ("cat", ("term",)): lambda x: x,
    ("term", ("terminal",)): lambda x: x,
    ("term", ("identifier",)): lambda x: x,
    ("term", ("special sequence",)): lambda x: x,
    ("term", ("[", "alt", "]")): lambda _, x, __: ("opt", x),
    ("term", ("{", "alt", "}")): lambda _, x, __: ("rep", x),
    ("term", ("(", "alt", ")")): lambda _, x, __: x,
})


def parse_ebnf(source: str, i: int = 0):
    rules = {}
    for variable, definition in parse_ebnf_tokens(scan_ebnf_tokens(source, i)):
        if variable in rules:
            raise ValueError(f"variable {variable} is defined twise")
        rules[variable] = definition
    return EBNF(rules)


print(parse_ebnf(Path("./ebnf.ebnf").read_text()))
