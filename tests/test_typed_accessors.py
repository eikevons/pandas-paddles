import pandas as pd
import pytest

from pandas_selector import DF


@pytest.fixture
def df():
    return pd.DataFrame({
        "x": list("abcde"),
        "y": pd.date_range('2021-04-03T10:00:00Z', periods=5, freq='10min'),
        "z": list("A..dE"),
        })

def test_str_accessor_replace(df):
    selector = DF.x.str.replace('c', '.')
    test = selector(df).to_list()
    assert test == list("ab.de")

def test_str_accessor_upper(df):
    selector = DF.x.str.upper()
    test = selector(df).to_list()
    assert test == list("ABCDE")

def test_str_accessor_upper_superfluous_argument(df):
    selector = DF.x.str.upper('too much')
    with pytest.raises(TypeError):
        selector(df)

def test_str_complex_comparison(df):
    selector = DF.x.str.upper() == DF.z.str.upper()
    test = selector(df).to_list()
    assert test == [True, False, False, True, True]

def test_dt_accessor(df):
    selector = DF.y.dt.minute
    test = selector(df).to_list()
    assert test == [0, 10, 20, 30, 40]
