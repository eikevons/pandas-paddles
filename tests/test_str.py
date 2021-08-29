from pandas_selector.df_accessor import AccessorBase
from pandas_selector import DF, S


# DataFrame accessor formatting
def test_attribute_str():
    assert ".a" == str(DF.a)

def test_two_attributes_str():
    assert ".a.BB" == str(DF.a.BB)

def test_item_str():
    assert "['a']" == str(DF["a"])

def test_two_items_str():
    assert "['a']['BB']" == str(DF["a"]["BB"])

def test_attribute_item_str():
    assert ".a['BB']" == str(DF.a["BB"])

def test_item_attribute_str():
    assert "['a'].BB" == str(DF["a"].BB)

def test_operator_str():
    assert ".x.__lt__(9)" == str(DF.x < 9)

def test_column_method_no_args_str():
    assert ".x.abs()" == str(DF.x.abs())

def test_column_method_with_arg_str():
    assert ".x.isin({1, 2})" == str(DF.x.isin({1, 2}))

def test_column_method_with_args_str():
    assert ".x.clip(1, 2)" == str(DF.x.clip(1, 2))

def test_column_method_with_arg_kwarg_str():
    assert ".x.clip(1, upper=2)" == str(DF.x.clip(1, upper=2))

def test_method_with_nested_args_str():
    assert ".x.method_name(.y.min())" == str(DF.x.method_name(DF.y.min()))

# Series accessor formatting
def test_series_operator_str():
    assert ".__lt__(8)" == str(S < 8)

def test_series_attribute_str():
    assert ".index" == str(S.index)

def test_series_method_no_args_str():
    assert ".abs()" == str(S.abs())

def test_series_method_with_arg_str():
    assert ".isin({3, 4})" == str(S.isin({3, 4}))

def test_series_method_with_args_str():
    assert ".meth_name(3, 'a')" == str(S.meth_name(3, 'a'))

def test_series_method_with_kwarg_str():
    assert ".clip(lower=1)" == str(S.clip(lower=1))

def test_series_method_with_arg_kwarg_str():
    assert ".clip(1, upper=2)" == str(S.clip(1, upper=2))
