from pandas_paddles import DF, S
import pytest

def j(*s):
    return "\n".join(s)


_cases = [
    # expression, expected str
    (DF.a, "DF.a"),
    (DF.a.BB, j("DF.a",
                "  .BB")),
    (DF["a"], "DF['a']"),
    (DF["a"]["BB"], j("DF['a']",
                      "  ['BB']")),
    (DF.a["BB"], j("DF.a",
                   "  ['BB']")),
    (DF["a"].BB, j("DF['a']",
                   "  .BB")),
    (DF.x < 9, j("  DF.x",
                 "<",
                 "  9")),
    # Python is internally converting to __gt__ because of __lt__ returning
    # NotImplemented
    (9 < DF.x, j("  DF.x",
                 ">",
                 "  9")),
    (DF.x + 1, j("  DF.x",
                 "+",
                 "  1")),
    (1 + DF.x, j("  1",
                 "+",
                 "  DF.x")),

    (DF.x.abs(), j("DF.x",
                   "  .abs()")),
    (DF.x.isin({1, 2}), j("DF.x",
                          "  .isin(",
                          "    {1, 2},",
                          "  )")),
    (DF.x.clip(1, 2), j("DF.x",
                        "  .clip(",
                        "    1,",
                        "    2,",
                        "  )")),

    (DF.x.clip(1, upper=2), j("DF.x",
                              "  .clip(",
                              "    1,",
                              "    upper=2,",
                              "  )")),
   (DF.x.method_name(DF.y.min()),
    j("DF.x",
      "  .method_name(",
      "    DF.y",
      "      .min(),",
      "  )")),
    (~DF["x"], "~DF['x']"),
    (-DF["x"], "-DF['x']"),

    # Series accessor formatting
    (S < 8, j("  S",
              "<",
              "  8")),
    (S.index, "S.index"),
    (S.abs(), "S.abs()"),
    (abs(S), "S.__abs__()"),
    (S.isin({3, 4}), j("S.isin(",
                       "   {3, 4},",
                       " )")),
    (S.meth_name(3, 'a'), j("S.meth_name(",
                            "   3,",
                            "   'a',",
                            " )")),
    (S.clip(lower=1), j("S.clip(",
                        "   lower=1,",
                        " )")),

    (S.clip(1, upper=2), j("S.clip(",
                           "   1,",
                           "   upper=2,",
                           " )")),
]
@pytest.mark.parametrize('expression,expected_str', _cases)
def test_str(expression, expected_str):
    assert expected_str == str(expression)
