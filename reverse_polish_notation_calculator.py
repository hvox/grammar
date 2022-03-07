from grammars import Grammar
from llparser import Parser


parser = Parser(
    Grammar(
        [
            ("expression", ("addition",)),
            ("expression", ("digits",)),
            ("addition", ("+", " ", "expression", " ", "expression")),
            ("digits", ("digit", "digits_rest")),
            ("digits_rest", ("digit", "digits_rest")),
            ("digits_rest", ()),
            ("digit", ("0",)),
            ("digit", ("1",)),
            ("digit", ("2",)),
            ("digit", ("3",)),
            ("digit", ("4",)),
            ("digit", ("5",)),
            ("digit", ("6",)),
            ("digit", ("7",)),
            ("digit", ("8",)),
            ("digit", ("9",)),
        ]
    )
)


def cat(*strings):
    return "".join(strings)


def idy(argument):
    return argument


def parse_digits(digit, rest):
    return ("number", int(digit + rest))


parser.actions = {"digits_rest": cat, "digits": parse_digits, "digit": idy}
