import pandas as pd
import pytest

from pandas_paddles import DF, S


@pytest.fixture
def df():
    return pd.DataFrame({
        "x": [1, 2, 3, 4, 5],
        "y": list("abcde"),
        "z": [1, 2, 1, 2, 1],
    })


@pytest.fixture
def s():
    return pd.Series(range(7))


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
        ("DF.z % DF.x", [0, 0, 1, 2, 1]),
        # Operators with constants
        ("DF.x + 1", [2, 3, 4, 5, 6]),
        ("DF.x - 1", [0, 1, 2, 3, 4]),
        ("DF.x * 2", [2, 4, 6, 8, 10]),
        ("DF.x / 2", [0.5, 1.0, 1.5, 2.0, 2.5]),
        ("DF.x // 2", [0, 1, 1, 2, 2]),
        ("DF.x ** 2", [1, 4, 9, 16, 25]),
        ("DF.x % 3", [1, 2, 0, 1, 2]),
        # Reverse operators with constants
        ("1 + DF.x", [2, 3, 4, 5, 6]),
        ("1 - DF.x", [0, -1, -2, -3, -4]),
        ("2 * DF.x", [2, 4, 6, 8, 10]),
        ("15 / DF.x", [15, 7.5, 5, 3.75, 3]),
        ("15 // DF.x", [15, 7, 5, 3, 3]),
        ("2 ** DF.x", [2, 4, 8, 16, 32]),
        ("3 % DF.x", [0, 1, 0, 3, 3]),
    ],
)
def test_df_arithmetic(df, code, expected):
    f = eval(code)
    test = f(df)
    assert test.to_list() == expected

@pytest.mark.parametrize(
    "code, expected",
    [
        # Boolean combinations of binary comparisons
        ("(DF.x > 2) & (DF.y == 'd')", 3 * [False] + [True, False]),
        ("(DF.x > 2) | (DF.y == 'a')", [True, False] + 3 * [True]),
        ("(DF.x > 2) ^ (DF.y == 'd')", 2 * [False] + [True, False, True]),
        ("~(DF.x > 2)", 2 * [True] + 3 * [False]),
        # Boolean logic with parentheses
        ("((DF.x > 2) & (DF.y == 'd')) | (DF.z == 1)", [True, False] + 3 * [True]),
        ("(DF.x > 2) & (DF.y == 'd') | (DF.z == 1)", [True, False] + 3 * [True]),
        ("(DF.x > 2) & ((DF.y == 'd') | (DF.z == 1))", [False, False] + 3 * [True]),
    ],
)
def test_df_boolean_logic(df, code, expected):
    f = eval(code)
    test = f(df)
    assert test.to_list() == expected


@pytest.mark.parametrize(
    "code, expected",
    [
     ("(S < 4)", 4 * [True]  + 3 * [False]),
     ("(S <= 4)", 5 * [True]  + 2 * [False]),
     ("(S == 4)", 4 * [False]  + [True] + 2 * [False]),
     ("(S != 4)", 4 * [True]  + [False] + 2 * [True]),
     ("~(S != 4)", 4 * [False]  + [True] + 2 * [False]),
     # Reverse operator
     ("(4 > S)", 4 * [True]  + 3 * [False]),
     # Combine operators
     ("(S > 1) & (S < 4)", [False, False, True, True] + 3 * [False]),
     ]
    )
def test_series_comparison(s, code, expected):
    f = eval(code)
    test = f(s)
    assert test.to_list() == expected


@pytest.mark.parametrize(
    "code,expected",
    [
        ("S.mod(3) == 0", [True, False, False, True, False, False, True]),
        ("(S >= 2) & (S.mod(3) == 0)", [False, False, False, True, False, False, True]),
    ]
    )
def test_series_operators(s, code, expected):
    f = eval(code)
    test = f(s)
    assert test.to_list() == expected
