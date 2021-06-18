from pandas_selector import DF, S


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
    assert ".x.__lt__(...)" == str(DF.x < None)

def test_column_method_no_args_str():
    assert ".x.abs()" == str(DF.x.abs())

def test_column_method_with_args_str():
    assert ".x.isin(...)" == str(DF.x.isin({None}))

def test_series_operator_str():
    assert ".__lt__(...)" == str(S < None)

def test_series_attribute_str():
    assert ".index" == str(S.index)

def test_series_method_no_args_str():
    assert ".abs()" == str(S.abs())

def test_series_method_with_args_str():
    assert ".isin(...)" == str(S.isin({None}))
