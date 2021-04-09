import pandas as pd
import pytest

from pandas_selector import DF


@pytest.fixture
def df():
    return pd.DataFrame(
        {
            "x": [1],
            "y": [2],
            "z": [3],
            },
        index=[1],
        )


def test_column_selection_end_to_end(df):
    selector = DF.columns.str.match('[xz]')
    # columns.str.match() returns a ndarray with tolist (not to_list as
    # pd.Series) method.
    test = selector(df).tolist()
    assert test == [True, False, True]
