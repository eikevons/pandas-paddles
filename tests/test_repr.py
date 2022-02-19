from pandas_paddles.df_accessor import AccessorBase
from pandas_paddles import DF, S


def test_DF_repr():
    r = repr(DF["key"].attrib.method(arg=1))
    assert isinstance(r, str)

def test_S_repr():
    r = repr(S["key"].attrib.method(arg=1))
    assert isinstance(r, str)
