"""\
Pandas Selector
---------------

Simple, composable column selector for ``loc[]``, ``iloc[]``, ``assign()`` and others. Juse use ``DF``.

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


Author: Eike von Seggern <eike@vonseggern.space>
"""
__version__ = "0.1.1"
__all__ = ["DF"]

from .accessor import DataframeAccessor

DF = DataframeAccessor()
