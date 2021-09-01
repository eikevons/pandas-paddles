from pickle import dumps, loads
import pandas as pd

from pandas_selector import DF, S


def test_can_be_pickled():
    # This should not raise an error.
    dumps(DF)

def test_unpickled_instance_works_again():
    df = pd.DataFrame({'x': range(5, 10)})
    sel1 = DF['x'] < 7
    a = df.loc[sel1]
    sel2 = loads(dumps(sel1))
    b = df[sel2]
    pd.testing.assert_frame_equal(a, b)
