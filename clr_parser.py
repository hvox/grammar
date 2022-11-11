from itertools import chain
from typing import Any, Callable, Iterable
from grammar import Rule  # do I really need the Rule type here?


def parse(
    action_table: dict[tuple[int, str], tuple],
    goto_table: dict[tuple[int, str], tuple],
    postprocessings: dict[Rule, Callable],
    source: Iterable[tuple[str, Any]],
):
    tokens = chain(iter(source), [(None, None)])
    stack = [0]
    token_type, next_token = next(tokens)
    while True:
        match action_table.get((stack[-1], token_type), "error"):
            case "error":
                raise ValueError("Unexpected token: " + repr(token_type))
            case ("shift", j):
                stack.append(next_token)
                stack.append(j)
                token_type, next_token = next(tokens)
            case ("reduce", rule):
                f = postprocessings.get(rule, lambda *x: (rule.head, *x))
                stack, body = stack[: -len(rule.body) * 2], stack[-len(rule.body)*2::2]
                state = goto_table[stack[-1], rule.head]
                stack.append(f(*body))
                stack.append(state)
            case ("accept",):
                return stack[1]
