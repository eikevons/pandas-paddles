from pandas_selector.df_accessor import AccessorBase
from pandas_selector import DF, S


def test_DF_repr():
    r = repr(DF["key"].attrib.method(arg=1))
    assert isinstance(r, str)

def test_S_repr():
    r = repr(S["key"].attrib.method(arg=1))
    assert isinstance(r, str)
