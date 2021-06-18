import pandas as pd
import pytest

from pandas_selector import DF, S

@pytest.mark.parametrize(
    "df_sel,exp_doc",
    [
        (DF.sum, pd.DataFrame.sum.__doc__),
        (DF.a.isin, pd.Series.isin.__doc__),
        (DF['a'].isin, pd.Series.isin.__doc__),
        (DF.a.dt.tz_convert, pd.Series.dt.tz_convert.__doc__),
        (DF.a.str.match, pd.Series.str.match.__doc__),
        (DF['a'].dt.tz_convert, pd.Series.dt.tz_convert.__doc__),
        (DF['a'].str.match, pd.Series.str.match.__doc__),
        (S.sum, pd.Series.sum.__doc__),
        (S.isin, pd.Series.isin.__doc__),
        (S.dt.tz_convert, pd.Series.dt.tz_convert.__doc__),
        (S.str.match, pd.Series.str.match.__doc__),
        ]
    )

def test_dataframe_function_doc(df_sel, exp_doc):
    assert df_sel.__doc__[:len(exp_doc)] == exp_doc
