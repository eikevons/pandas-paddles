"""\
Pandas Paddles
--------------

*Help* ``pandas`` *navigate its fluent API with paddles: Write concise
chained data-frame operations.*

Just use ``DF`` in arguments to :attr:`~pandas.DataFrame.loc`,
:attr:`~pandas.DataFrame.iloc`, :meth:`~pandas.DataFrame.assign()` and other
methods to access columns, methods, and attributes of the calling data frame
(use ``S`` when dealing with :class:`pandas.Series`). Select columns in
:attr:`~pandas.DataFrame.loc` with ``C``. This allows to write chains of
operations much more concisely. See `Comparison`_ below.

* ``DF`` and ``S`` give you access to all data frame/series attributes where
  Pandas allows to pass a callback to handle the contextual object. (See `DataFrame examples`_ and `Series examples`_)
* ``C`` can be used to simplify column selection in
  :attr:`~pandas.DataFrame.loc` by column name or data type. (See `Column selection`_)

DataFrame examples
~~~~~~~~~~~~~~~~~~

Filter rows with :attr:`~pandas.DataFrame.loc`:

>>> from pandas_paddles import DF
>>> df = pd.DataFrame({"x": range(9), "y": 3 * ["a", "B", "c"]})
>>> df.loc[DF["x"] < 3]
   x  y
0  0  a
1  1  B
2  2  c

Access nested column attributes:

>>> df.loc[DF["y"].str.islower()]
   x  y
0  0  a
2  2  c
3  3  a
5  5  c
6  6  a
8  8  c

Combine filter predicates:

>>> df.loc[DF["y"].str.islower() & (df.x < 3)]
   x  y
0  0  a
2  2  c

Create new columns:

>>> df.assign(z = DF["x"] * DF["y"])
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
...  .assign(z = DF["x"] * DF["y"])
...  .loc[DF["z"].str.len() > 3]
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

>>> from pandas_paddles import S
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

Column selection
~~~~~~~~~~~~~~~~

.. note::
    This feature is experimental! The API might change in minor version updates.

See :class:`~pandas_paddles.axis.SelectionComposer` for complete API documentation.

Move some columns to the left of the data frame. ``...`` is used to include all other columns at the end and the typical logical operators ``&``, ``|`` (or ``+``), and ``~`` to compose selections

>>> from pandas_paddles import C
>>> df = pd.DataFrame({"x": 1, "y": 3.14, "z": "abc", "u": 42}, index=[0])
>>> df.loc[:, C["y", "u"] | ...]
      y   u  x    z
0  3.14  42  1  abc

Select by "simple" dtype

>>> df.loc[:, C.dtype == int]
   x   u
0  1  42

Select by "complex" dtype

>>> df.loc[:, C.dtype == str]
     z
0  abc

Select by multiple dtypes

>>> df.loc[:, C.dtype.isin((int, float))]
   x     y   u
0  1  3.14  42

Select by multi-index level

>>> midf = pd.DataFrame.from_records(
... data=[range(9)],
... index=[0],
... columns=pd.MultiIndex.from_product([["a", "b", "c"], ["x", "y", "z"]], names=["one", "two"]))
>>> midf
one  a        b        c      
two  x  y  z  x  y  z  x  y  z
0    0  1  2  3  4  5  6  7  8
>>> midf.loc[:, C.levels[0]["b", "c"] | ...]
one  b        c        a      
two  x  y  z  x  y  z  x  y  z
0    3  4  5  6  7  8  0  1  2
>>>  midf.loc[:, (C.levels[0]["b", "c"] | ...) & C.levels[1]["z"]]
one  b  c  a
two  z  z  z
0    5  8  2

Comparison
~~~~~~~~~~

With ``pandas_paddles.DF`` data frame operations can be easily composed in
a way that does not need to reference the initial dataframes::

    from pandas_paddles import DF
    df_out = (df_in
              .loc[DF["x"] == 3]
              .assign(x_is_even = (DF["x"] % 2) == 0)
             )

Without operator chaining, the data frame needs to be reassigned and
referenced multiple times, which adds a lot of nois.::

       df_out = df_in.loc[df_in["x"] == 3]
       df_out = df_out.assign(x_is_even = (df_out["x"] % 2) == 0)

Operator chaining without ``DF`` requires a lot of ``lambda`` boilerplate
code::

        df_out = (df_in
                  .loc[lambda df: df["x"] == 3]
                  .assign(x_is_even = lambda df: (df["x"] % 2) == 0)
                 )


Author: Eike von Seggern <eike@vonseggern.space>
"""
__version__ = "1.3.0"
__all__ = ["C", "DF", "S"]

from .df_accessor import DataframeAccessor, SeriesAccessor
from .axis import SelectionComposer

DF = DataframeAccessor()
S = SeriesAccessor()
C = SelectionComposer()
