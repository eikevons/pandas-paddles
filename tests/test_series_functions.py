import pandas as pd
import pytest

from pandas_selector import DF, S


@pytest.fixture
def df():
    return pd.DataFrame({"x": list("abcde")})


@pytest.fixture
def ser():
    return pd.Series(range(-2, 3))


def test_isin(df):
    selector = DF.x.isin(["b", "d"])
    test = selector(df).to_list()
    assert test == [False, True, False, True, False]


def test_series_abs_selection(ser):
    selector = S.abs() <= 1
    test = selector(ser).to_list()
    assert test == ([False] + 3 * [True] + [False])
