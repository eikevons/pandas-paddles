"""\
Pandas Selector
---------------

Just use ``DF`` in arguments to ``loc[]``, ``iloc[]``, ``assign()`` and
other methods to access columns, methods, and attributes of the calling data
frame (use ``S`` when dealing with ``pd.Series``). This allows to write
chains of operations much more concisely:

- Chain with ``pandas_selector.DF``::

        from pandas_selector import DF
        df_out = (df_in
                  .loc[DF['x'] == 3]
                  .assign(x_is_even = (DF['x'] % 2) == 0)
                 )

- Chain without ``pandas_selector.DF`` ::

        df_out = (df_in
                  .loc[lambda df: df['x'] == 3]
                  .assign(x_is_even = lambda df: (df['x'] % 2) == 0)
                 )
- No chain::

       df_out = df_in.loc[df_in['x'] == 3]
       df_out = df_out.assign(x_is_even = (df_out['x'] % 2) == 0)


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

You can also use ``DF`` in function arguments:

>>> df = pd.DataFrame({"x": range(6), "y": 2 * [1,2,3]})
>>> df.assign(x2 = DF["x"].clip(DF["y"].min(), DF["y"].max()))
   x  y  x2
0  0  1   1
1  1  2   1
2  2  3   2
3  3  1   3
4  4  2   3
5  5  3   3

 or with keyword arguments:

>>> DF.assign(x2 = DF["x"].clip(lower=DF["y"].min(), upper=DF["y"].max()))
# ...

Series examples
~~~~~~~~~~~~~~~

Select subset of series matching predicate:

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
