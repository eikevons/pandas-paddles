from pandas_selector import DF, S

import pandas as pd
import pytest

@pytest.fixture
def df():
    return pd.DataFrame({
        "x": range(5),
        })


@pytest.fixture
def ser():
    return pd.Series(range(5))


def test_DF_end_to_end(df):
    test = (df
            .assign(
                y = DF.x // 2,
                z = DF.x * DF.y,
                )
            .loc[DF.y <= 1]
            )
    expected = pd.DataFrame({
        "x": [0, 1, 2, 3],
        "y": [0, 0, 1, 1],
        "z": [0, 0, 2, 3],
    })
    return pd.testing.assert_frame_equal(test, expected)

def test_S_end_to_end(ser):
    test = ser[S < 2]
    expected = pd.Series(range(2))
    return pd.testing.assert_series_equal(test, expected)
