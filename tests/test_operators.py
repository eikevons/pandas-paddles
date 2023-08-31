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

_dataframe_cases = [
    # Comparison operators
    # Simple binary comparison
    # >
    ("DF.x > DF.z", 2 * [False] + 3 * [True]),
    ("DF.x > 2", 2 * [False] + 3 * [True]),
    ("2 > DF.x", [True] + 4 * [False]),
    # >=
    ("DF.x >= DF.z", 5 * [True]),
    ("DF.x >= 2", [False, True] + 3 * [True]),
    ("2 >= DF.x", [True, True] + 3 * [False]),
    # ==
    ("DF.x == DF.z", 2 * [True] + 3 * [False]),
    ("DF.x == 2", [False, True] + 3 * [False]),
    ("2 == DF.x", [False, True] + 3 * [False]),
    # !=
    ("DF.x != DF.z", 2 * [False] + 3 * [True]),
    ("DF.x != 2", [True, False] + 3 * [True]),
    ("2 != DF.x", [True, False] + 3 * [True]),
    # <
    ("DF.x < DF.z", 5 * [False]),
    ("DF.x < 2", [True] + 4 * [False]),
    ("2 < DF.x", 2 * [False] + 3 * [True]),
    # <=
    ("DF.x <= DF.z", 2 * [True] + 3 * [False]),
    ("DF.x <= 2", [True, True] + 3 * [False]),
    ("2 <= DF.x", [False, True] + 3 * [True]),

    # Arithmetic operators
    #   1. column <OP> column
    #   2. column <OP> constant
    #   3. constant <ROP> column
    # +
    ("DF.x + DF.z", [2, 4, 4, 6, 6]),
    ("DF.x + 1", [2, 3, 4, 5, 6]),
    ("1 + DF.x", [2, 3, 4, 5, 6]),
    # -
    ("DF.x - DF.z", [0, 0, 2, 2, 4]),
    ("DF.x - 1", [0, 1, 2, 3, 4]),
    ("1 - DF.x", [0, -1, -2, -3, -4]),
    # *
    ("DF.x * DF.z", [1, 4, 3, 8, 5]),
    ("DF.x * 2", [2, 4, 6, 8, 10]),
    ("2 * DF.x", [2, 4, 6, 8, 10]),
    # /
    ("DF.x / DF.z", [1, 1, 3, 2, 5]),
    ("DF.x / 2", [0.5, 1.0, 1.5, 2.0, 2.5]),
    ("15 / DF.x", [15, 7.5, 5, 3.75, 3]),
    # //
    ("DF.z // DF.x", [1, 1, 0, 0, 0]),
    ("DF.x // 2", [0, 1, 1, 2, 2]),
    ("15 // DF.x", [15, 7, 5, 3, 3]),
    # **
    ("DF.x ** DF.z", [1, 4, 3, 16, 5]),
    ("DF.x ** 2", [1, 4, 9, 16, 25]),
    ("2 ** DF.x", [2, 4, 8, 16, 32]),
    # %
    ("DF.z % DF.x", [0, 0, 1, 2, 1]),
    ("DF.x % 3", [1, 2, 0, 1, 2]),
    ("3 % DF.x", [0, 1, 0, 3, 3]),
    # unary -
    ("-DF.x", [-1, -2, -3, -4, -5]),

    # Bit-wise operators:
    #   1. column <OP> column
    #   2. column <OP> constant
    #   3. constant <ROP> column
    # &
    ("DF.x & DF.z", [1, 2, 1, 0, 1]),
    ("DF.x & 2", [0, 2, 2, 0, 0]),
    ("2 & DF.x", [0, 2, 2, 0, 0]),
    # |
    ("DF.x | DF.z", [1, 2, 3, 6, 5]),
    ("DF.x | 2", [3, 2, 3, 6, 7]),
    ("2 | DF.x", [3, 2, 3, 6, 7]),
    # ^
    ("DF.x ^ DF.z", [0, 0, 2, 6, 4]),
    ("DF.x ^ 2", [3, 0, 1, 6, 7]),
    ("2 ^ DF.x", [3, 0, 1, 6, 7]),

    # Boolean combinations of binary comparisons
    ("(DF.x > 2) & (DF.y == 'd')", 3 * [False] + [True, False]),
    ("(DF.x > 2) | (DF.y == 'a')", [True, False] + 3 * [True]),
    ("(DF.x > 2) ^ (DF.y == 'd')", 2 * [False] + [True, False, True]),
    ("~(DF.x > 2)", 2 * [True] + 3 * [False]),
    # Boolean logic with parentheses
    ("((DF.x > 2) & (DF.y == 'd')) | (DF.z == 1)", [True, False] + 3 * [True]),
    ("(DF.x > 2) & (DF.y == 'd') | (DF.z == 1)", [True, False] + 3 * [True]),
    ("(DF.x > 2) & ((DF.y == 'd') | (DF.z == 1))", [False, False] + 3 * [True]),
]

@pytest.mark.parametrize("code, expected", _dataframe_cases)
def test_df_operators(df, code, expected):
    f = eval(code)
    test = f(df)
    assert test.to_list() == expected


@pytest.mark.parametrize(
    "code, expected",
    [
     ]
    )
def test_series_comparison(s, code, expected):
    f = eval(code)
    test = f(s)
    assert test.to_list() == expected


_series_cases = [
    # Arithmetic operators
    # +
    ("S + 1", list(range(1, 8))),
    ("1 + S", list(range(1, 8))),
    # -
    ("S - 1", list(range(-1, 6))),
    ("1 - S", list(range(1, -6, -1))),
    # *
    ("2 * S", [0, 2, 4, 6, 8, 10, 12]),
    ("S * 2", [0, 2, 4, 6, 8, 10, 12]),
    # / 
    ("S / 2", [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]),
    ("42 / (S + 1)", [42.0, 21.0, 14.0, 10.5, 8.4, 7.0, 6.0]),
    # //
    ("S // 2", [0, 0, 1, 1, 2, 2, 3]),
    ("42 // (S + 1)", [42, 21, 14, 10, 8, 7, 6]),
    # %
    ("S % 3", [0, 1, 2, 0, 1, 2, 0]),
    ("3 % (S + 1)", [0, 1, 0, 3, 3, 3, 3]),
    # **
    ("S ** 2", [0, 1, 4, 9, 16, 25, 36]),
    ("2 ** S", [1, 2, 4, 8, 16, 32, 64]),
    # unary -
    ("-S", [0, -1, -2, -3, -4, -5, -6]),

    # Bit-wise operators
    # |
    ("S | 2", [2, 3, 2, 3, 6, 7, 6]),
    ("2 | S", [2, 3, 2, 3, 6, 7, 6]),
    # &
    ("S & 2", [0, 0, 2, 2, 0, 0, 2]),
    ("2 & S", [0, 0, 2, 2, 0, 0, 2]),
    # ^
    ("S ^ 2", [2, 3, 0, 1, 6, 7, 4]),
    ("2 ^ S", [2, 3, 0, 1, 6, 7, 4]),

    # Comparison operators
    # <
    ("(S < 4)", 4 * [True]  + 3 * [False]),
    ("(4 < S)", 5 * [False]  + 2 * [True]),
    # <=
    ("(S <= 4)", 5 * [True]  + 2 * [False]),
    ("(4 <= S)", 4 * [False]  + 3 * [True]),
    # ==
    ("(S == 4)", 4 * [False]  + [True] + 2 * [False]),
    ("(4 == S)", 4 * [False]  + [True] + 2 * [False]),
    # !=
    ("(S != 4)", 4 * [True]  + [False] + 2 * [True]),
    ("(4 != S)", 4 * [True]  + [False] + 2 * [True]),
    # >
    ("(S > 4)", 5 * [False]  + 2 * [True]),
    ("(4 > S)", 4 * [True]  + 3 * [False]),
    # >=
    ("(S >= 4)", 4 * [False]  + 3 * [True]),
    ("(4 >= S)", 5 * [True]  + 2 * [False]),
    # inversion
    ("~(S != 4)", 4 * [False]  + [True] + 2 * [False]),

    # Combine operators
    ("(S > 1) & (S < 4)", [False, False, True, True] + 3 * [False]),
    ("(S > 1) | (S < 4)", 7 * [True]),

    # Complex constructs
    ("S.mod(3) == 0", [True, False, False, True, False, False, True]),
    ("(S % 3) == 0", [True, False, False, True, False, False, True]),
    ("(S >= 2) & (S.mod(3) == 0)", [False, False, False, True, False, False, True]),
]


@pytest.mark.parametrize("code,expected", _series_cases)
def test_series_operators(s, code, expected):
    f = eval(code)
    test = f(s)
    assert test.to_list() == expected
