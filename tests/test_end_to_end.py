from pandas_paddles import DF, S

import pandas as pd
import pytest

HAS_DASK = False
try:
    import dask.dataframe
    HAS_DASK = True
except ImportError:
    pass

@pytest.fixture
def df():
    return pd.DataFrame({
        "x": range(5),
        })


@pytest.fixture
def ser():
    return pd.Series(range(5))


def ops(df):
    return (df
            .assign(
                y = DF.x // 2,
                z = DF.x * DF.y,
                )
            .loc[DF.y <= 1]
            )


def test_DF_end_to_end(df):
    test = ops(df)
    expected = pd.DataFrame({
        "x": [0, 1, 2, 3],
        "y": [0, 0, 1, 1],
        "z": [0, 0, 2, 3],
    })
    return pd.testing.assert_frame_equal(test, expected)

@pytest.mark.skipif(not HAS_DASK, reason="dask not available")
def test_DF_end_to_end_dask(df):
    dask_df = dask.dataframe.from_pandas(df, chunksize=2)
    dask_test = ops(dask_df)
    pd_test = dask_test.compute()
    expected = pd.DataFrame({
        "x": [0, 1, 2, 3],
        "y": [0, 0, 1, 1],
        "z": [0, 0, 2, 3],
    })

    return pd.testing.assert_frame_equal(pd_test, expected)


def test_S_end_to_end(ser):
    test = ser[S < 2]
    expected = pd.Series(range(2))
    return pd.testing.assert_series_equal(test, expected)
