from pandas_selector import DF

import pandas as pd
import pytest

@pytest.fixture
def df():
    return pd.DataFrame({
        "x": range(5),
        })


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
