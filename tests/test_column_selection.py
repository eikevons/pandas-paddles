import pandas as pd
import pytest

from pandas_selector import DF


@pytest.fixture
def simple_df():
    return pd.DataFrame({
        "x": [1,2,3,4,5],
        "y": [1,2,5,5,4],
        })

@pytest.fixture
def multilevel_df():
    return pd.DataFrame({
        ("x", "A"): [1,2,3,4,5],
        ("x", "B"): [1,2,5,5,4],
        ("y", "A"): [5,4,3,2,1],
        })


def test_simple_column_by_attr(simple_df):
    expected = simple_df.x
    return pd.testing.assert_series_equal(expected, DF.x(simple_df))

def test_simple_column_by_key(simple_df):
    expected = simple_df.loc[:, "x"]
    return pd.testing.assert_series_equal(expected, DF["x"](simple_df))

def test_multilevel_column_by_attrs(multilevel_df):
    expected = multilevel_df.x.B
    return pd.testing.assert_series_equal(expected, DF.x.B(multilevel_df))

def test_multilevel_column_by_keys(multilevel_df):
    expected = multilevel_df["x"]["B"]
    return pd.testing.assert_series_equal(expected, DF["x"]["B"](multilevel_df))

def test_multilevel_column_by_attr_and_key(multilevel_df):
    expected = multilevel_df.x["B"]
    return pd.testing.assert_series_equal(expected, DF.x["B"](multilevel_df))

def test_multilevel_column_by_key_and_attr(multilevel_df):
    expected = multilevel_df["x"].B
    return pd.testing.assert_series_equal(expected, DF["x"].B(multilevel_df))

def test_multilevel_column_by_tuple_key(multilevel_df):
    expected = multilevel_df[("x", "B")]
    return pd.testing.assert_series_equal(expected, DF[("x", "B")](multilevel_df))
