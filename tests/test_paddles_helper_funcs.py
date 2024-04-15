import operator

import pytest

import pandas as pd
from pandas_paddles import DF

from pandas_paddles.paddles import build_filter, str_join


@pytest.fixture
def df():
    return pd.DataFrame({
        'x': ['a', 'b', 'b'],
        'y': range(3),
    })


@pytest.mark.parametrize(
    "expr, expected",
    [
        (str_join("+", "x", "y"), ["a+0", "b+1", "b+2"]),
        (str_join("+", "x", DF["x"].str.upper()), ["a+A", "b+B", "b+B"]),
        (str_join("+", "x", DF["y"] + 1), ["a+1", "b+2", "b+3"]),
    ]
)
def test_str_join(df, expr, expected):
    test = expr(df)
    assert test.to_list() == expected


from pandas_paddles.contexts import ClosureFactoryBase
from pandas_paddles.closures import AttributeClosure, ItemClosure, MethodClosure

def assert_expr_eq(a, b):
    assert type(a) == type(b)
    if isinstance(a, ClosureFactoryBase):
        assert len(a._closures) == len(b._closures)
        for aa, bb in zip(a._closures, b._closures):
            assert_expr_eq(aa, bb)
    elif isinstance(a, (AttributeClosure, ItemClosure)):
        assert a.name == b.name
    elif isinstance(a, MethodClosure):
        assert a.name == b.name
        assert_expr_eq(a.args, b.args)
        assert_expr_eq(a.kwargs, b.kwargs)
    elif isinstance(a, (tuple, list)):
        assert len(a) == len(b)
        for aa, bb in zip(a, b):
            assert_expr_eq(aa, bb)

    elif isinstance(a, dict):
        assert len(a) == len(b)
        assert set(a) == set(b)
        for k in a:
            assert_expr_eq(a[k], b[k])
    else:
        assert a == b


@pytest.mark.parametrize(
    "preds, expected",
    [
        (
            {"a": "A", "b": "B"},
            (DF["a"] == "A") & (DF["b"] == "B"),
        ),
        (
            {DF["a"]: "A", "b": "B"},
            (DF["a"] == "A") & (DF["b"] == "B"),
        ),
        (
            {"a": DF["A"], "b": DF["B"] + 1},
            (DF["a"] == DF["A"]) & (DF["b"] == DF["B"] + 1),
        ),

    ],
)
def test_build_filter(preds, expected):
    test = build_filter(preds)
    assert_expr_eq(test, expected)

@pytest.mark.parametrize(
    "preds, op, expected",
    [
        # and'ed
        (
            {"a": "A", "b": "B"},
            operator.and_,
            (DF["a"] == "A") & (DF["b"] == "B"),
        ),
        (
            {"a": "A", "b": "B"},
            "and",
            (DF["a"] == "A") & (DF["b"] == "B"),
        ),
        (
            {"a": "A", "b": "B"},
            "&",
            (DF["a"] == "A") & (DF["b"] == "B"),
        ),
        # or'ed
        (
            {"a": "A", "b": "B"},
            operator.or_,
            (DF["a"] == "A") | (DF["b"] == "B"),
        ),
        (
            {"a": "A", "b": "B"},
            "or",
            (DF["a"] == "A") | (DF["b"] == "B"),
        ),
        (
            {"a": "A", "b": "B"},
            "|",
            (DF["a"] == "A") | (DF["b"] == "B"),
        ),
    ]
)
def test_build_filter(preds, op, expected):
    test = build_filter(preds, op)
    assert_expr_eq(test, expected)

def test_build_filter_fails_on_unknown_op():
    with pytest.raises(ValueError, match="Unsupported operator name: 'bad'"):
        build_filter({}, "bad")
