import pandas as pd
import pytest

from pandas_selector import DF


@pytest.fixture
def df():
    return pd.DataFrame({
        "x": list("abcde"),
        })


def test_isin(df):
    selector = DF.x.isin(["b", "d"])
    test = selector(df).to_list()
    assert test == [False, True, False, True, False]
