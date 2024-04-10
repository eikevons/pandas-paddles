"""Helpers for pandas-paddles to simplify compositions.

Use as::

    from pandas_paddles import paddles
"""
from typing import Union
from .contexts import DataframeContext

DF = DataframeContext()

ColSpec = Union[str, DataframeContext]


def ensure_DF_expr(col: ColSpec) -> DataframeContext:
    """Convert column names to ``DF``-expressions when necessary.

    Parameters
    ----------
    col
        The column name (``str``) or a ``DF`` expression.

    Returns
    -------
    DF expression
        The ``DF`` expression of ``col`` (if a ``str``) or just ``col``.

    Examples
    --------

    Strings are converted to ``DF`` expressions::

        >>> ensure_DF_expr("col-name")
        DF["col-name"]

    ``DF`` expressions are passed through::

        >>> expr2 = DF["another-column"]
        >>> expr2 is ensure_DF_expr(expr2)
        True
    """
    if isinstance(col, str):
        return DF[col]
    return col


def str_join(sep: str, col1: ColSpec, *cols: ColSpec) -> DataframeContext:
    """Create expression to join multiple columns in a string.

    This is similar to ``str.join``

    Parameters
    ----------
    sep
        The separator
    col1, cols
        The columns to be joined. These can be either ``str`` or
        ``DF``-expressions. If a ``str`` is passed, it's taken as column
        name and the respective ``DF``-expression is created.

        In both cases the expression is first casted to ``str`` using
        :func:`pandas.Series.astype()`.

    Returns
    -------
    DF expression
        The ``DF``-expression, a callable taking a
        :class:`~pandas.DataFrame` as argument.

    Examples
    --------

    Reference columns with their names::

        >>> df = pd.DataFrame({"a": list("abc"), "b": list("XYZ"), "c": range(3)})
        >>> df.assign(a_plus_b=str_join("+", "a", "b"))
           a  b  c a_plus_b
        0  a  X  0      a+X
        1  b  Y  1      b+Y
        2  c  Z  2      c+Z

    Reference columns with ``DF`` expressions::

        >>> df.assign(a_plus_b=str_join("+", "a", DF["b"].str.lower()))
           a  b  c a_plus_b
        0  a  X  0      a+x
        1  b  Y  1      b+y
        2  c  Z  2      c+z

    Non-string columns are converted::

        >>> df.assign(a_plus_c=str_join("+", "a", "c")
           a  b  c a_plus_b
        0  a  X  0      a+0
        1  b  Y  1      b+1
        2  c  Z  2      c+2
    """
    expr = ensure_DF_expr(col1).astype(str)
    for col in cols:
        expr = expr + sep + ensure_DF_expr(col).astype(str)
    return expr


# j = join("//", "a", DF["b"], DF["a"].str.upper())
# print(j)
# print("--")
# print(
#     df.assign(
#         new=j,
#         )
#     )
