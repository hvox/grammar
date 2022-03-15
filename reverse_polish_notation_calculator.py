from grammars import Grammar
from llparser import Parser
from mymath import Rational, add, sub, mul, mod, div


parser = Parser(
    Grammar(
        [
            ("expression", ("binary operation",)),
            ("expression", ("digits",)),
            ("binary operation", ("addition",)),
            ("binary operation", ("substraction",)),
            ("binary operation", ("multiplication",)),
            ("binary operation", ("modulo",)),
            ("binary operation", ("division",)),
            ("addition", ("+", " ", "expression", " ", "expression")),
            ("substraction", ("-", " ", "expression", " ", "expression")),
            ("multiplication", ("*", " ", "expression", " ", "expression")),
            ("modulo", ("%", " ", "expression", " ", "expression")),
            ("division", ("/", " ", "expression", " ", "expression")),
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
    return ("number", Rational(digit + rest))


parser.actions = {"digits_rest": cat, "digits": parse_digits, "digit": idy}

operations = {
    "addition": add,
    "substraction": sub,
    "multiplication": mul,
    "modulo": mod,
    "division": div,
}


def calculate(node):
    operation, args = node
    if operation == "expression":
        return calculate(args[0])
    if operation == "binary operation":
        op_name, args = args[0]
        return operations[op_name](calculate(args[2]), calculate(args[4]))
    if operation == "number":
        return args
    raise Exception(f"wtf is {node}")


def eval(source):
    return calculate(parser.parse(source))

if __name__ == "__main__":
    while True:
        print(eval(input('>>> ')))
