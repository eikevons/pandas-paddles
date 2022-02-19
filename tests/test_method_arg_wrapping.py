import pandas as pd
import pytest

from pandas_paddles import DF


@pytest.fixture
def df():
    return pd.DataFrame({"x": range(5)})


def test_method_arg_wrapping(df):
    selector = DF["x"].clip(DF.loc[2, "x"])
    test = selector(df).tolist()
    assert test == [2, 2, 2, 3, 4]

def test_method_2arg_wrapping(df):
    selector = DF["x"].clip(DF.loc[2, "x"], DF.loc[3, "x"])
    test = selector(df).tolist()
    assert test == [2, 2, 2, 3, 3]

def test_method_kwarg_wrapping(df):
    selector = DF["x"].clip(lower=DF.loc[2, "x"])
    test = selector(df).tolist()
    assert test == [2, 2, 2, 3, 4]

def test_method_2_kwarg_wrapping(df):
    selector = DF["x"].clip(lower=DF.loc[2, "x"], upper=DF.loc[3, "x"])
    test = selector(df).tolist()
    assert test == [2, 2, 2, 3, 3]

def test_method_mixed_arg_wrapping(df):
    selector = DF["x"].clip(DF.loc[2, "x"], upper=DF.loc[3, "x"])
    test = selector(df).tolist()
    assert test == [2, 2, 2, 3, 3]
