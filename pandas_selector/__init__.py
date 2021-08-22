"""\
Pandas Selector
---------------

Simple, composable selector for ``loc[]``, ``iloc[]``, ``assign()`` and
others. Just use ``DF`` when working with DataFrames and ``S`` for Series.

DataFrame examples
~~~~~~~~~~~~~~~~~~

Filter rows:

>>> from pandas_selector import DF
>>> df = pd.DataFrame({"x": range(9), "y": 3 * ["a", "B", "c"]})
>>> df.loc[DF.x < 3]
   x  y
0  0  a
1  1  B
2  2  c

Access nested column attributes:

>>> df.loc[DF.y.str.islower()]
   x  y
0  0  a
2  2  c
3  3  a
5  5  c
6  6  a
8  8  c

Combine filter predicates:

>>> df.loc[DF.y.str.islower() & (df.x < 3)]
   x  y
0  0  a
2  2  c

Create new columns:

>>> df.assign(z = DF.x * DF.y)
   x  y         z
0  0  a
1  1  B         B
2  2  c        cc
3  3  a       aaa
4  4  B      BBBB
5  5  c     ccccc
6  6  a    aaaaaa
7  7  B   BBBBBBB
8  8  c  cccccccc

Chain operations:

>>> (df
...  .assign(z = DF.x * DF.y)
...  .loc[DF.z.str.len() > 3]
... )
   x  y         z
3  3  a       aaa
4  4  B      BBBB
5  5  c     ccccc
6  6  a    aaaaaa
7  7  B   BBBBBBB
8  8  c  cccccccc

Series examples
~~~~~~~~~~~~~~~

Select subset of series matching prediate:

>>> from pandas_selector import S
>>> s = pd.Series(range(10))
>>> s[S < 3]
0    0
1    1
2    2
dtype: int64
>>> s[(S > 2) & (S.mod(2) == 0)]
4    4
6    6
8    8
dtype: int64


Author: Eike von Seggern <eike@vonseggern.space>
"""
__version__ = "0.1.2"
__all__ = ["DF", "S"]

from .df_accessor import DataframeAccessor, SeriesAccessor

DF = DataframeAccessor()
S = SeriesAccessor()
