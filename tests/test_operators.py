import pandas as pd
import pytest

from pandas_selector import DF, S


@pytest.fixture
def df():
    return pd.DataFrame(
        {"x": [1, 2, 3, 4, 5], "y": list("abcde"), "z": [1, 2, 1, 2, 1]}
    )


@pytest.fixture
def s():
    return pd.Series(range(-3, 4))


@pytest.mark.parametrize(
    "code, expected",
    [
        # Simple binary comparison
        ("DF.x < 2", [True] + 4 * [False]),
        ("DF.x <= 2", [True, True] + 3 * [False]),
        ("DF.x == 2", [False, True] + 3 * [False]),
        ("DF.x != 2", [True, False] + 3 * [True]),
        ("DF.x >= 2", [False, True] + 3 * [True]),
        ("DF.x > 2", 2 * [False] + 3 * [True]),
        # Comparison between 2 columns
        ("DF.x > DF.z", 2 * [False] + 3 * [True]),
        # Boolean combinations of binary comparisons
        ("(DF.x > 2) & (DF.y == 'd')", 3 * [False] + [True, False]),
        ("(DF.x > 2) | (DF.y == 'a')", [True, False] + 3 * [True]),
        ("(DF.x > 2) ^ (DF.y == 'd')", 2 * [False] + [True, False, True]),
        ("~(DF.x > 2)", 2 * [True] + 3 * [False]),
        # Reverse operators
        ("2 > DF.x", [True] + 4 * [False]),
        ("2 >= DF.x", [True, True] + 3 * [False]),
        ("2 == DF.x", [False, True] + 3 * [False]),
        ("2 != DF.x", [True, False] + 3 * [True]),
        ("2 <= DF.x", [False, True] + 3 * [True]),
        ("2 < DF.x", 2 * [False] + 3 * [True]),
    ],
)
def test_df_comparison(df, code, expected):
    f = eval(code)
    test = f(df)
    assert test.to_list() == expected


@pytest.mark.parametrize(
    "code, expected",
    [
        ("DF.x + DF.z", [2, 4, 4, 6, 6]),
        ("DF.x - DF.z", [0, 0, 2, 2, 4]),
        ("DF.x * DF.z", [1, 4, 3, 8, 5]),
        ("DF.x / DF.z", [1, 1, 3, 2, 5]),
        ("DF.z // DF.x", [1, 1, 0, 0, 0]),
        ("DF.x ** DF.z", [1, 4, 3, 16, 5]),
    ],
)
def test_df_arithmetic(df, code, expected):
    f = eval(code)
    test = f(df)
    assert test.to_list() == expected


@pytest.mark.parametrize(
    "code, expected",
    [ 
     ("(S < 1)", 4 * [True]  + 3 * [False]),
     ("(S <= 1)", 5 * [True]  + 2 * [False]),
     ("(S == 1)", 4 * [False]  + [True] + 2 * [False]),
     ("(S != 1)", 4 * [True]  + [False] + 2 * [True]),
     ("~(S != 1)", 4 * [False]  + [True] + 2 * [False]),
     # Reverse operator
     ("(1 > S)", 4 * [True]  + 3 * [False]),
     ]
    )
def test_series_comparison(s, code, expected):
    f = eval(code)
    test = f(s)
    assert test.to_list() == expected
