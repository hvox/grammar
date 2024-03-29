from parser import lr_parser
import pytest

evaluate = lr_parser({
    ("sum", ("product",)): (lambda x: x),
    ("sum", ("sum", "+", "product")): (lambda x, _, y: x + y),
    ("sum", ("sum", "-", "product")): (lambda x, _, y: x - y),
    ("product", ("factor",)): (lambda x: x),
    ("product", ("product", "*", "factor")): (lambda x, _, y: x * y),
    ("product", ("product", "/", "factor")): (lambda x, _, y: x / y),
    ("factor", ("(", "sum", ")")): (lambda *x: x[1]),
    ("factor", ("number",)): (lambda x: x)
})


def test_simplest_case():
    parse = lr_parser([("S", ("C", "C")), ("C", ("c", "C")), ("C", ("d",))])
    ast = parse([(char, (i, char)) for i, char in enumerate("cdd")])
    assert ast == ("S", ("C", (0, "c"), ("C", (1, "d"))), ("C", (2, "d")))


ARITHMETIC_EXPRESSIONS = [
    "1 + 16 * 0 * 880 / 7 - 23 + 6 - 4 / 6 * 9 / 7 + 201 * 798 / 73 * 2 - 911",
    "38 - 4785 * 58 * 8 * 527 + 9 / 78 * 2 / 4 + 494 * 8 + 4 - 62 - 39 + 8337",
    "8 * 4 - 7 + 47 / 1 / 7 + 156 - 3 + 20 + 48 / 8 / 6 * 915 * 38 - 425 / 81",
    "344 * 3785 / 4 + 2 * 4 * 45 * 9 / 8 - 9 / 394 / 9 + 5 - 0 + 2670 + 8 - 4",
    "6647 - 0 * 61 - 2 * 8 / 8 - 5 / 130 * 5 - 21 + 905 - 1047 / 4 / 9 / 9290",
    "77 - 96 + 30 + 9 * 1 + 9 + 75 / 55 - 3 - 877 / 1 + 940 / 8 - 51 * 9 / 94",
    "24 * 5281 - 6 * 4 * 23 - 4171 - 7 / 50 / 228 * 23 / 20 / 0 * 4 + 5 - 128",
    "857 - 5 - 3392 / 1 / 754 + 37 / 39 / 7 / 2002 / 1106 + 84 * 84 + 28 - 87",
    "7 * 5 / 310 + 5 - 178 - 8046 - 906 / 78 - 156 / 0 / 239 + 1 * 699 - 7146",
    "673 * 619 - 64 * 7791 - 8 / 0 / 1570 + 3326 * 4 + 35 / 3 - 3 / 607 + 642",
    "425 - 1 * 974 + 4 * 2 + 86 / 5743 + 5 - 75 * 6 - 7 + 5 - 52 - 6328 - 397",
    "1 / 32 - 9 * 876 / 948 / 3 + 4 - 696 - 9 + 4 * 1873 + 4 / 97 * 5 * 3 * 8",
    "4 - 7 / 7686 * 8 * 9 - 2 + 1213 / 83 * 5 - 0 + 344 / 4 * 6 - 17 - 9 + 24",
    "9 - 2 - 5 / 611 * 9 + 500 + 7 + 3 / 674 + 6 + 579 * 9 / 4502 + 7 / 5 + 6",
    "280 * 1220 / 6 + 1 * 69 + 3 / 6658 * 4024 + 4 * 88 / 4 + 225 * 27 + 7671",
    "9 + 1 / 1882 - 7 * 4 + 7 - 35 / 57 * 2337 / 0 + 978 / 89 * 1 - 2 + 6 * 7",
    "85 + 45 / 45 + 8 * 0 - 7 * 6645 + 0 * 7 / 7 - 7263 / 874 - 7 + 40 / 4792",
    "6 - 909 * 34 + 6 + 1625 * 5 + 155 - 334 - 3 / 6 - 95 / 4160 - 8 * 4 / 72",
    "80 * 9 + 2 - 90 / 9 - 26 + 81 + 66 / 16 + 71 - 7745 - 58 / 95 - 398 - 47",
    "39 - 9 / 153 - 13 + 733 + 9 / 6 + 3 + 444 - 6 - 117 * 59 - 8 * 8 + 9 - 6",
    "65 - 379 - 2 * 0 + 8523 - 89 / 54 + 55 * 1 + 4 / 9 + 9 + 4 * 4044 / 4579",
    "54 * 7 - 90 - 4 / 7 + 5 + 92 / 85 - 97 / 0 - 3 - 81 * 7 / 31 * 4 - 9 / 6",
    "7193 / 6 + 4 - 380 / 917 * 46 - 5357 / 5600 * 98 + 91 * 538 - 3 * 7 / 81",
    "5 + 9549 + 5245 - 6 - 4 * 4 + 1 - 821 + 47 * 70 * 0 / 6 + 38 / 827 * 490",
    "914 + 287 / 684 * 41 * 6 + 7149 * 87 + 4395 * 4468 / 6863 - 7004 - 6 * 2",
    "22 + 75 - 34 + 8 / 79 / 7 + 3927 + 1771 + 6 - 331 + 4 / 9 * 9 / 3 / 2372",
    "1 + 93 - 5 / 5724 - 6 / 270 - 1 * 226 + 63 + 59 + 2383 + 8 - 8 * 0 - 819",
    "542 - 7369 * 74 * 8535 + 9 * 70 + 3 * 9 * 7 * 38 - 767 - 7388 + 4224 - 9",
    "4 * 6 / 28 / 55 / 9 - 4 + 58 + 7 / 1 * 0 / 3 + 72 - 762 / 76 * 75 + 3267",
    "84 + 6 - 0 * 3 + 539 - 63 * 456 / 925 - 6 - 3 * 24 * 8 * 9 - 2 * 53 / 29",
    "6 * 7 * 350 * 130 * 40 - 8 - 1 + 18 + 5822 / 43 - 95 + 2 * 8 * 2768 * 63",
    "1 - 1 * 407 * 9152 * 0 * 8 - 687 / 486 * 9050 + 771 + 53 - 919 - 308 * 7",
    "252 / 2 / 9088 - 14 + 3 * 4024 - 204 - 9 * 6562 * 6937 - 65 / 0 - 6 / 23",
    "72 * 6 * 5 - 19 + 2 + 7 / 6077 - 706 / 883 * 5 * 7 + 8272 / 9 - 6 - 5407",
    "47 - 9 - 74 * 933 / 17 * 99 + 814 / 8 / 9 - 824 / 0 + 0 / 1 / 6737 + 472",
    "39 + 80 + 3 / 7241 / 2264 - 2195 + 2 + 9 + 2 / 622 / 7 - 1 * 3 - 45 / 69",
]


@pytest.mark.parametrize("expr_number", range(len(ARITHMETIC_EXPRESSIONS)))
def test_arithmetic_expression_parsing(expr_number: str):
    expr = ARITHMETIC_EXPRESSIONS[expr_number]
    tokens = [("number", int(tok)) if tok.isdigit() else (tok, tok) for tok in expr.split()]
    try:
        result = evaluate(tokens)
    except ZeroDivisionError:
        result = ZeroDivisionError
    try:
        expected_result = eval(expr)
    except ZeroDivisionError:
        expected_result = ZeroDivisionError
    assert result == expected_result
