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
  Pandas allows to pass a callback to handle the contextual object. (See
  `DataFrame examples`_ and `Series examples`_)
* ``C`` can be used to simplify column selection in
  :attr:`~pandas.DataFrame.loc` by column name or data type. (See `Column or
  index selection`_)
* ``I`` can be used to simplify row selection in
  :attr:`~pandas.DataFrame.loc` by row label. (See `Column or index
  selection`_)
* :func:`~pandas_paddles.pipe.report` can be used to inspect the dataframe in a chain
  of operations.
* :mod:`~pandas_paddles.paddles` contains useful helper functions, e.g.
  :func:`~pandas_paddles.paddles.str_join` to join multiple columns into a
  string.

DataFrame examples
~~~~~~~~~~~~~~~~~~

See full documentation at :class:`~pandas_paddles.contexts.DataframeContext`.

Filter rows with :attr:`~pandas.DataFrame.loc`::

    from pandas_paddles import DF
    df = pd.DataFrame({"x": range(9), "y": 3 * ["a", "B", "c"]})
    df.loc[DF["x"] < 3]
    # Out:
    #    x  y
    # 0  0  a
    # 1  1  B
    # 2  2  c

Access nested column attributes::

    df.loc[DF["y"].str.islower()]
    #    x  y
    # 0  0  a
    # 2  2  c
    # 3  3  a
    # 5  5  c
    # 6  6  a
    # 8  8  c

Combine filter predicates::

    df.loc[DF["y"].str.islower() & (df.x < 3)]
    # Out:
    #    x  y
    # 0  0  a
    # 2  2  c

Create new columns::

    df.assign(z = DF["x"] * DF["y"])
    # Out:
    #    x  y         z
    # 0  0  a
    # 1  1  B         B
    # 2  2  c        cc
    # 3  3  a       aaa
    # 4  4  B      BBBB
    # 5  5  c     ccccc
    # 6  6  a    aaaaaa
    # 7  7  B   BBBBBBB
    # 8  8  c  cccccccc

Chain operations::

    (df
     .assign(z = DF["x"] * DF["y"])
     .loc[DF["z"].str.len() > 3]
    )
    # Out:
    #    x  y         z
    # 3  3  a       aaa
    # 4  4  B      BBBB
    # 5  5  c     ccccc
    # 6  6  a    aaaaaa
    # 7  7  B   BBBBBBB
    # 8  8  c  cccccccc

You can also use ``DF`` in function arguments::

    df = pd.DataFrame({"x": range(6), "y": 2 * [1,2,3]})
    df.assign(x2 = DF["x"].clip(DF["y"].min(), DF["y"].max()))
    # Out:
    #    x  y  x2
    # 0  0  1   1
    # 1  1  2   1
    # 2  2  3   2
    # 3  3  1   3
    # 4  4  2   3
    # 5  5  3   3

or with keyword arguments::

    df.assign(x2 = DF["x"].clip(lower=DF["y"].min(), upper=DF["y"].max()))
    # ...

Series examples
~~~~~~~~~~~~~~~

See full documentation at :class:`~pandas_paddles.contexts.SeriesContext`.

Select subset of series matching predicate::

    from pandas_paddles import S
    s = pd.Series(range(10))
    s[S < 3]
    # Out:
    # 0    0
    # 1    1
    # 2    2
    # dtype: int64
    s[(S > 2) & (S.mod(2) == 0)]
    # Out:
    # 4    4
    # 6    6
    # 8    8
    # dtype: int64

``S`` can also be used in aggregations, e.g.::

    df.groupby("Y")["x"].agg([S.max() - S.min() * 2])
    # y
    # B    5
    # a    6
    # c    4
    # Name: x, dtype: int64

Column or index selection
~~~~~~~~~~~~~~~~~~~~~~~~~

See :class:`~pandas_paddles.axis.ColumnSelectionComposer` for complete API
documentation. (:class:`~pandas_paddles.axis.SelectionComposerBase` for
index-wise selection.)

.. note::
    Except for `C.dtype`, the examples below work in a similar manner when
    selecting by index by replacing ``C`` with ``I``, e.g.::

        df.loc[I["a", "b"] | ...]

Move some columns to the left of the data frame. ``...`` is used to include
all other columns at the end and the typical logical operators ``&``, ``|``
(or ``+``), and ``~`` to compose selections::

    from pandas_paddles import C
    df = pd.DataFrame({"x": 1, "y": 3.14, "z": "abc", "u": 42}, index=[0])
    df.loc[:, C["y", "u"] | ...]
    # Out:
    #       y   u  x    z
    # 0  3.14  42  1  abc

Select slices of columns::

    df.loc[:, C["y":"z"] | ...]
    # Out:
    #       y    z  x   u
    # 0  3.14  abc  1  42

Select by "simple" dtype::

    df.loc[:, C.dtype == int]
    # Out:
    #    x   u
    # 0  1  42

Select by "complex" dtype::

    df.loc[:, C.dtype == str]
    # Out:
    #      z
    # 0  abc

Select by multiple dtypes::

    df.loc[:, C.dtype.isin((int, float))]
    # Out:
    #    x     y   u
    # 0  1  3.14  42

Select by multi-index level::

    midf = pd.DataFrame.from_records(
        data=[range(9)],
        index=[0],
        columns=pd.MultiIndex.from_product([["a", "b", "c"], ["x", "y", "z"]], names=["one", "two"]),
    )
    midf
    # Out:
    # one  a        b        c      
    # two  x  y  z  x  y  z  x  y  z
    # 0    0  1  2  3  4  5  6  7  8
    midf.loc[:, C.levels[0]["b", "c"] | ...]
    # Out:
    # one  b        c        a      
    # two  x  y  z  x  y  z  x  y  z
    # 0    3  4  5  6  7  8  0  1  2
    midf.loc[:, (C.levels[0]["b", "c"] | ...) & C.levels[1]["z"]]
    # Out:
    # one  b  c  a
    # two  z  z  z
    # 0    5  8  2

.. warning::
    Selecting slices of a multi-index level might not work as expected
    because only one consecutive slice is taken from the level's labels,
    e.g. only the first ``"x":"y"`` slice can be fetched from level 1 of
    ``midf``:

    >>> midf.loc[:, C.levels[1]["x":"y"]]
    one  a   
    two  x  y
    0    0  1

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
referenced multiple times, which adds a lot of noise::

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
__version__ = "1.6.0-dev"
__all__ = ["C", "DF", "I", "S", "report", "paddles"]


from .axis import ColumnSelectionComposer, IndexSelectionComposer
from .pipe import report
from . import paddles
try:
    from .dask import DF, S
except ImportError as e:
    print("Using pandas-only...", e)
    from .pandas import DF, S


C = ColumnSelectionComposer()
I = IndexSelectionComposer()
