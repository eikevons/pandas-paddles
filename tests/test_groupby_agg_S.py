from pandas_paddles import S

import pandas as pd
import pytest

@pytest.fixture
def df():
    return pd.DataFrame({
        "x": range(5),
        "y": list("ababa"),
        })

def test_groupby_column_agg_simple(df):
    test = (df
            .groupby("y")
            ["x"]
            .agg(S.min())
            )
    expected = pd.Series(
        [0, 1],
        index=pd.Index(['a', 'b'], name="y"),
        name='x',
    )
    return pd.testing.assert_series_equal(test, expected)

def test_groupby_column_agg_composed(df):
    test = (df
            .groupby("y")
            ["x"]
            .agg(S.max() - S.min())
            )
    expected = pd.Series(
        [4, 2],
        index=pd.Index(['a', 'b'], name="y"),
        name='x',
    )
    return pd.testing.assert_series_equal(test, expected)

def test_groupby_column_agg_list(df):
    test = (df
            .groupby("y")
            ["x"]
            .agg([S.min(), S.max(), S.max() - S.min()])
            )
    expected = pd.DataFrame(
        {
            'S.min()': [0, 1],
            'S.max()': [4, 3],
            'S.max() - S.min()': [4, 2],
        },
        index=pd.Index(['a', 'b'], name='y'),
    )
    return pd.testing.assert_frame_equal(test, expected)

def test_groupby_df_agg_list(df):
    test = (
        df
        .groupby("y")
        .agg([S.min(), S.max(), S.max() - S.min()])
    )
    expected = pd.DataFrame(
        {
            ('x', 'S.min()'): [0, 1],
            ('x', 'S.max()'): [4, 3],
            ('x', 'S.max() - S.min()'): [4, 2],
        },
        index=pd.Index(['a', 'b'], name='y'),
    )
    return pd.testing.assert_frame_equal(test, expected)

def test_groupby_df_agg_dict(df):
    test = (
        df
        .groupby("y")
        .agg({
            'x': [S.min(), S.max(), S.max() - S.min()],
        })
    )
    expected = pd.DataFrame(
        {
            ('x', 'S.min()'): [0, 1],
            ('x', 'S.max()'): [4, 3],
            ('x', 'S.max() - S.min()'): [4, 2],
        },
        index=pd.Index(['a', 'b'], name='y'),
    )
    return pd.testing.assert_frame_equal(test, expected)
