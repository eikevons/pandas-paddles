import pytest

import pandas as pd
from pandas_paddles import DF

from pandas_paddles.paddles import str_join


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

