from pandas_paddles import DF, S

def j(*s):
    return "\n".join(s)


# DataFrame accessor formatting
def test_attribute_str():
    assert "DF.a" == str(DF.a)

def test_two_attributes_str():
    assert j("DF.a",
             "  .BB") == str(DF.a.BB)

def test_item_str():
    assert "DF['a']" == str(DF["a"])

def test_two_items_str():
    assert j("DF['a']",
             "  ['BB']") == str(DF["a"]["BB"])

def test_attribute_item_str():
    assert j("DF.a",
             "  ['BB']") == str(DF.a["BB"])

def test_item_attribute_str():
    assert j("DF['a']",
             "  .BB") == str(DF["a"].BB)

def test_operator_str():
    assert j("  DF.x",
             "<",
             "  9") == str(DF.x < 9)

def test_column_method_no_args_str():
    assert j("DF.x",
             "  .abs()") == str(DF.x.abs())

def test_column_method_with_arg_str():
    assert j("DF.x",
             "  .isin(",
             "    {1, 2},",
             "  )") == str(DF.x.isin({1, 2}))

def test_column_method_with_args_str():
    assert j("DF.x",
             "  .clip(",
             "    1,",
             "    2,",
             "  )") == str(DF.x.clip(1, 2))

def test_column_method_with_arg_kwarg_str():
    assert j("DF.x",
             "  .clip(",
             "    1,",
             "    upper=2,",
             "  )") == str(DF.x.clip(1, upper=2))

def test_method_with_nested_args_str():
    assert j("DF.x",
             "  .method_name(",
             "    DF.y",
             "      .min(),",
             "  )") == str(DF.x.method_name(DF.y.min()))

# Series accessor formatting
def test_series_operator_str():
    assert j("  S",
             "<",
             "  8") == str(S < 8)

def test_series_attribute_str():
    assert "S.index" == str(S.index)

def test_series_method_no_args_str():
    assert "S.abs()" == str(S.abs())

def test_series_method_with_arg_str():
    assert j("S.isin(",
             "   {3, 4},",
             " )") == str(S.isin({3, 4}))

def test_series_method_with_args_str():
    assert j("S.meth_name(",
             "   3,",
             "   'a',",
             " )") == str(S.meth_name(3, 'a'))

def test_series_method_with_kwarg_str():
    assert j("S.clip(",
             "   lower=1,",
             " )") == str(S.clip(lower=1))

def test_series_method_with_arg_kwarg_str():
    assert j("S.clip(",
             "   1,",
             "   upper=2,",
             " )") == str(S.clip(1, upper=2))
