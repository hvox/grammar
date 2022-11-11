from ebnf import EBNF
import pytest

parse_arithmetic_expression = EBNF("""
    sum = product | sum, "+", product | sum, "-", product;
    product = factor | product, "*", factor | product, "/", factor;
    factor = "(", sum, ")" | number;
    number = ?\\d+?;
""").parse


@pytest.mark.parametrize("expr, expected_ast", [
    (
        "2+2",
        (
            (0, 3),
            "sum",
            (
                (0, 1),
                "sum",
                (
                    (0, 1),
                    "product",
                    ((0, 1), "factor", ((0, 1), "number", ((0, 1), "?\\d+?", "2"))),
                ),
            ),
            ((1, 2), '"+"', "+"),
            (
                (2, 3),
                "product",
                ((2, 3), "factor", ((2, 3), "number", ((2, 3), "?\\d+?", "2"))),
            ),
        ),
    ),
    (
        "7991*706",
        (
            (0, 8),
            "sum",
            (
                (0, 8),
                "product",
                (
                    (0, 4),
                    "product",
                    ((0, 4), "factor", ((0, 4), "number", ((0, 4), "?\\d+?", "7991"))),
                ),
                ((4, 5), '"*"', "*"),
                ((5, 8), "factor", ((5, 8), "number", ((5, 8), "?\\d+?", "706"))),
            ),
        ),
    ),
])
def test_arithmetic_expression_parsing(expr, expected_ast):
    ast = parse_arithmetic_expression(expr)
    assert ast == expected_ast
