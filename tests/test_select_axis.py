import pandas as pd
import pytest


from pandas_selector.axis import C, OpComposerBase


def cols(df: pd.DataFrame, col_sel: OpComposerBase) -> list:
    """Get list of column names after applying column selection."""
    return df.loc[:,col_sel].columns.to_list()


@pytest.fixture
def simple_df():
    return pd.DataFrame({
        "x": [1,2,3,4,5],
        "y": [1,2,5,5,4],
        "z": list("abcde"),
        })


def test_basic(simple_df):
    col_sel = C["y", "z", "x"]
    assert ["y", "z", "x"] == cols(simple_df, col_sel)


def test_combine(simple_df):
    col_sel = C["y"] | C["z"] | C["x"]
    assert (["y", "z", "x"]
            == simple_df.loc[:, col_sel].columns.to_list())


def test_ellipsis(simple_df):
    col_sel = C["y"] | ...
    assert (["y", "x", "z"]
            == simple_df.loc[:, col_sel].columns.to_list())


def test_startswith(simple_df):
    col_sel = C.startswith("x")
    assert ["x"] == simple_df.loc[:, col_sel].columns.to_list() == ["x"]


def test_endswith(simple_df):
    col_sel = C.endswith("x")
    assert ["x"] == cols(simple_df, col_sel)


def test_str_dtype(simple_df):
    col_sel = C.dtype == str
    assert ["z"] == cols(simple_df, col_sel)


def test_int_dtype(simple_df):
    col_sel = C.dtype == int
    assert ["x", "y"] == cols(simple_df, col_sel)
