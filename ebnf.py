from collections import Counter
from functools import cached_property
from parser import ast_to_str, lr_parser
from pathlib import Path
from re import compile as re
from typing import Any, Iterable
from lexer import construct_lexer
from libs.set_utils import add_to_set

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


def parse_ebnf_rules(source: str, i: int = 0) -> dict[str, tuple]:
    rules = parse_ebnf_tokens(scan_ebnf_tokens(source, i))
    for var in (var for var, cnt in Counter(var for var, _ in rules).items() if cnt > 1):
        raise ValueError(f"variable {var} has multiple definitions")
    return dict(rules)


class EBNF:
    def __init__(self, rules: Iterable[tuple[str, Any]] | str):
        self.rules = parse_ebnf_rules(rules) if isinstance(rules, str) else dict(rules)
        variables, terminals = set(self.rules), set()
        for exp in self.rules.values():
            stack = [exp]
            while stack:
                match stack.pop():
                    case "alt" | "cat" | "opt" | "rep", *args if len(args):
                        stack.extend(args)
                    case terminal if terminal not in variables:
                        terminals.add(terminal)
        self.variables, self.terminals = variables, terminals
        self.symbols = self.variables | self.terminals
        for var in filter(lambda v: v[0] not in "'\"?", terminals):
            raise Exception(f"Undefined variable {var}")

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

    @cached_property
    def parse(self):
        tokens = [(re(s[1:-1]) if s[0] == "?" else s[1:-1], s) for s in self.terminals]
        patterns = {pattern: lambda span, s: (tok, (span, tok, s)) for pattern, tok in tokens}
        scan = construct_lexer(patterns)
        rules, used_names = {}, set(self.symbols)

        def dfs(head, body):
            nonlocal used_names
            used_names.add(head)
            if body in used_names:
                body = ("cat", body)
            args = tuple(
                str(arg) if str(arg) in used_names else dfs(str(arg), arg) for arg in body[1:]
            )
            if body[0] == "alt":
                _ = [dfs(head, expr) for expr in body[1:]]
            elif body[0] == "cat":
                if args:
                    rules[head, args] = lambda *x: ((x[0][0][0], x[-1][0][1]), head, *x)
                else:
                    rules[head, args] = lambda: (head, ((None, None),))
            elif body[0] == "opt":
                return dfs(head, ("alt", args[0], ("cat",)))
            elif body[0] == "rep":
                arg = args[0]
                arg_repeated = add_to_set(used_names, str(arg) + " repeated")
                dfs(arg_repeated, ("opt", ("cat", arg_repeated, arg)))
                return dfs(head, (arg_repeated,))
            return head

        for head, expr in (
            (head, expr)
            for head, alts in self.rules.items()
            for expr in (alts[1:] if alts[0] == "alt" else [alts])
        ):
            # TODO: use stack instead of complex local function
            old_rules, rules = rules, {}
            dfs(head, expr)
            rules = old_rules | dict(reversed(rules.items()))
        parse = lr_parser(rules)
        return lambda source, start=0: parse(scan(source, start))


print(EBNF(Path("./ebnf.ebnf").read_text()))
