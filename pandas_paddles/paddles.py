"""Helpers for pandas-paddles to simplify compositions.

Use as::

    from pandas_paddles import paddles
"""
from functools import reduce
import operator
from typing import Any, Callable, Dict, Iterable, Literal, Union

from .pandas import PandasDataframeContext
try:
    from .dask import DF
except ImportError:
    from .pandas import DF

__all__ = [
    "build_filter",
    "combine",
    "str_join",
]

# Some typing hints
ColSpec = Union[str, PandasDataframeContext]
BinaryOp = Union[
    Callable[[Any, Any], Any],
    Literal["and"],
    Literal["&"],
    Literal["or"],
    Literal["|"],
]


def ensure_DF_expr(col: ColSpec) -> PandasDataframeContext:
    """Convert column names to ``DF``-expressions when necessary.

    Parameters
    ----------
    col
        The column name (``str``) or a ``DF``-expression.

    Returns
    -------
    PandasDataframeContext
        The ``DF``-expression of ``col`` (if a ``str``) or just ``col``.

    Examples
    --------

    Strings are converted to ``DF``-expressions::

        >>> ensure_DF_expr("col-name")
        DF["col-name"]

    ``DF``-expressions are passed through::

        >>> expr2 = DF["another-column"]
        >>> expr2 is ensure_DF_expr(expr2)
        True
    """
    if isinstance(col, str):
        return DF[col]
    return col


def str_join(sep: str, col1: ColSpec, *cols: ColSpec) -> PandasDataframeContext:
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
    PandasDataframeContext
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

    Reference columns with ``DF``-expressions::

        >>> df.assign(a_plus_b=str_join("+", "a", DF["b"].str.lower()))
           a  b  c a_plus_b
        0  a  X  0      a+x
        1  b  Y  1      b+y
        2  c  Z  2      c+z

    Non-string columns are converted::

        >>> df.assign(a_plus_c=str_join("+", "a", "c"))
           a  b  c a_plus_b
        0  a  X  0      a+0
        1  b  Y  1      b+1
        2  c  Z  2      c+2
    """
    expr = ensure_DF_expr(col1).astype(str)
    for col in cols:
        expr = expr + sep + ensure_DF_expr(col).astype(str)
    return expr


def combine(
    bool_expressions: Iterable[PandasDataframeContext],
    op: Callable[[Any, Any], Any] = operator.and_,
) -> PandasDataframeContext:
    """Combine multiple DF-expressions to use in df.loc[].

    The ``DF``-expressions must evaluate to a boolean array, e.g.,::

        DF["col"] > 1
        DF["col"].str.startswith("prefix")
        DF["col_1"] < DF["col_2"]

    Parameters
    ----------
    bool_expressions
        Iterable of ``DF``-expressions that will be combined.
    op
        The operator to combine the filters. :func:`operator.and_` and
        :func:`operator.or_` will be most useful. ``"and"``, ``"&"`` and
        ``"or"``, ``"|"`` are also accepted and the respective operator is
        used.

    Returns
    -------
    The combined expression.
    """
    if isinstance(op, str):
        if op == "and" or op == "&":
            op = operator.and_
        elif op == "or" or op == "|":
            op = operator.or_
        else:
            raise ValueError(f"Unsupported operator name: {op!r}")
    return reduce(op, bool_expressions)


def build_filter(
    predicates: Dict[ColSpec, Any], op: BinaryOp = operator.and_
) -> PandasDataframeContext:
    """Build a filter expression from column-value pairs

    .. code::

        df.loc[build_filter({"a": "A", "b": "B"})

    is equivalent to::

        df.loc[
            (DF["a"] == "A")
            & (DF["b"] == "B")
        ]

    Parameters
    ----------
    predicates
        The column-value pairs to filter on.

        Columns can be either specified as ``str`` or as ``DF``-expressions.

        Values can be literal values or ``DF``-expressions.
    op
        The operator to combine the predicates. :func:`operator.and_` and
        :func:`operator.or_` will be most useful. ``"and"``, ``"&"`` and
        ``"or"``, ``"|"`` are also accepted and the respective operator is
        used.

    Returns
    -------
    PandasDataframeContext
        The ``DF``-expression combining the predicates.
    """
    expressions = (ensure_DF_expr(col) == val for col, val in predicates.items())
    return combine(expressions, op=op)
