from itertools import product
import pytest

from operator import eq, ne, ge, gt, le, lt
from pandas_paddles import DF, S


eq_operators = (eq, le, ge)
ne_operators = (ne, lt, gt)
eq_args = [
    # 1 level
    (DF["a"], None),
    (DF["a"], DF["a"]),
    (DF.a, None),
    (DF.a, DF.a),
    (DF.min(), None),
    (DF.min(), DF.min()),
    # 2 levels
    (DF["a"].min(), None),
    (DF["a"].min(), DF["a"].min()),
    (DF.a.min(), None),
    (DF.a.min(), DF.a.min()),
    # series
    (S.min(), None),
    (S.min(), S.min()),
]
ne_args = [
    # 1 level
    (DF["a"], DF["b"]),
    (DF.a, DF.b),
    (DF.min(), DF.max()),
    # 2 levels
    (DF["a"].min(), DF["a"].max()),
    (DF["a"].min(), DF["b"].min()),
    (DF.a.min(), DF.a.max()),
    (DF.a.min(), DF.b.min()),
    # series
    (S.min(), S.max()),
    # mismatching objects
    (S.min(), DF.min()),
    (S.min(), 3),
    (DF["a"], 3),
    (DF["a"].min(), 3),
]


@pytest.mark.parametrize(
    ["op", "left", "right"],
    [(op, l, r) for op, (l, r) in product(eq_operators, eq_args)]
    + [(op, l, r) for op, (l, r) in product(ne_operators, ne_args)]

 )
def test_comparisons_evaluate_true(op, left, right):
    if right is None:
        right = left
    expr = op(left, right)
    test = bool(expr)
    assert test is True


@pytest.mark.parametrize(
    ["op", "left", "right"],
    [(op, l, r) for op, (l, r) in product(ne_operators, eq_args)]
    + [(op, l, r) for op, (l, r) in product(eq_operators, ne_args)]
 )
def test_comparisons_evaluate_false(op, left, right):
    if right is None:
        right = left
    expr = op(left, right)
    test = bool(expr)
    assert test is False


@pytest.mark.parametrize("expr", [
    DF, DF.min(), DF["a"], DF.a,
    S, S.min(),
])
def test_plain_expressions_evaluate_true(expr):
    test = bool(expr)
    assert test
