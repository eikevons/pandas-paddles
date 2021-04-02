from pandas_selector import DF


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

