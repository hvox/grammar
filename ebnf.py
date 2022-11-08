import string
from typing import Any, Iterable

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
#    -    exception  <-- not supported yet
#    ;    termination


class EBNF:
    def __init__(self, rules: Iterable[tuple[str, Any]]):
        self.rules = {head: body for head, body in rules}

    def __repr__(self):
        def node_repr(node):
            match node:
                case "alt", *alts:
                    return " | ".join(map(node_repr, alts))
                case "cat", *terms:
                    return ", ".join(map(node_repr, terms))
                case "opt", value:
                    return "[" + node_repr(value) + "]"
                case "rep", value:
                    return "{" + node_repr(value) + "}"
                case str(literal):
                    return repr(literal)
        result = []
        for head, body in self.rules.items():
            result.append(f"{head} = {node_repr(body)};")
        return "\n".join(result)


def skip_whitespaces(source: str, i: int = 0):
    while i < len(source) and source[i] in " \t\n":
        i += 1
    return i


def parse_optional(source: str, i: int = 0):
    inside, i = parse_ebnf_alternation(source, skip_whitespaces(source, i + 1))
    return ("opt", inside), skip_whitespaces(source, i + 1)


def parse_repetition(source: str, i: int = 0):
    inside, i = parse_ebnf_alternation(source, skip_whitespaces(source, i + 1))
    return ("rep", inside), skip_whitespaces(source, i + 1)


def parse_grouping(source: str, i: int = 0):
    inside, i = parse_ebnf_alternation(source, skip_whitespaces(source, i + 1))
    return inside, skip_whitespaces(source, i + 1)


def parse_terminal(source: str, i: int = 0):
    marker = source[i]
    assert marker in "'\""
    j = i + 1
    while source[j] != marker:
        j += 1
    return source[i + 1: j], skip_whitespaces(source, j + 1)


def parse_variable(source: str, i: int = 0):
    j = i
    while source[j] in string.ascii_letters + string.whitespace:
        j += 1
    return source[i: j].strip(), j


def parse_ebnf_concatenation(source: str, i: int = 0):
    body = []
    while i < len(source):
        if source[i] == "[":
            term, i = parse_optional(source, i)
        elif source[i] == "{":
            term, i = parse_repetition(source, i)
        elif source[i] == "(":
            term, i = parse_grouping(source, i)
        elif source[i] in "'\"":
            term, i = parse_terminal(source, i)
        elif source[i] in string.ascii_letters:
            term, i = parse_variable(source, i)
        else:
            break
        body.append(term)
        if source[i] != ",":
            break
        i = skip_whitespaces(source, i + 1)
    result = tuple(["cat"] + body) if len(body) > 2 else body[0]
    return result, skip_whitespaces(source, i)


def parse_ebnf_alternation(source: str, i: int = 0):
    options = []
    while i < len(source):
        option, i = parse_ebnf_concatenation(source, skip_whitespaces(source, i))
        options.append(option)
        if source[i] != "|":
            break
        i = skip_whitespaces(source, i + 1)
    result = tuple(["alt"] + options) if len(options) > 2 else options[0]
    return result, skip_whitespaces(source, i)


def parse_ebnf_rule(source: str, i: int = 0):
    head, i = parse_variable(source, i)
    assert source[i] == "="
    i = skip_whitespaces(source, i + 1)
    body, i = parse_ebnf_alternation(source, i)
    return (head, body), i


def parse_ebnf(source: str) -> EBNF:
    i = 0
    rules = {}
    source = source.replace("\n", " ").strip()
    while i < len(source):
        (head, body), i = parse_ebnf_rule(source, skip_whitespaces(source, i))
        rules[head] = body
        if source[i] != ";":
            break
        i = skip_whitespaces(source, i + 1)
    return EBNF(rules.items())


from pathlib import Path
print(parse_ebnf(Path("./ebnf.ebnf").read_text()))
