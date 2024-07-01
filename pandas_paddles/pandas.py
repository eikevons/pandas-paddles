"""Pandas-only contexts"""

from typing import Optional

import pandas as pd

from .contexts import (
    add_dunder_operators,
    get_obj_attr_doc,
    ClosureFactoryBase,
)


@add_dunder_operators # This is necessary to overload all dunder operators.
class PandasDataframeContext(ClosureFactoryBase):
    """Build callable to access columns and operators.

    Use the global instance like::

        from pandas_paddles import DF
        df.loc[DF["x"] < 3]

    All operations (item/attribute access, method calls) are passed to the
    data frame of the context.

    This is useful in combination with :attr:`~pandas.DataFrame.loc`,
    :attr:`~pandas.DataFrame.iloc`, :meth:`~pandas.DataFrame.assign()` and
    other methods that accept callables taking the data frame to act on as
    single argument.

    Examples
    --------
    Usage with :attr:`~pandas.DataFrame.loc` or
    :attr:`~pandas.DataFrame.iloc`::

        df = pd.DataFrame({"x": [1, 2, 3, 4]})
        df.loc[DF["x"] <= 2]
        # Out:
        #    x
        # 0  1
        # 1  2

    Usage with :meth:`~pandas.DataFrame.assign()`::

        df.assign(y = DF["x"] * 2)
        # Out:
        #    x  y
        # 0  1  2
        # 1  2  4
        # 2  3  6
        # 3  4  8
    """
    wrapped_cls = (pd.DataFrame,)
    wrapped_s = "DF"
    def _get_doc(self) -> Optional[str]:
        doc = super()._get_doc()
        # Assume DataFrame-level function for 1-level accessor
        if len(self._closures) == 1 and isinstance(self._closures[-1].name, str):
            for wrapped_cls in self.wrapped_cls:
                wrapped_doc = get_obj_attr_doc(wrapped_cls, self._closures[-1].name) or doc
                if wrapped_doc is not None:
                    break
            doc = wrapped_doc
        # Check for typed Series accessors for 3+-level accessor
        elif len(self._closures) >= 3 and self._closures[-2].name in ('dt', 'str'):
            doc = (
                get_obj_attr_doc(
                    getattr(pd.Series, self._closures[-2].name),
                    self._closures[-1].name,
                )
                or doc
            )
        # Check for Series-level function for 2+-level accessor
        elif len(self._closures) > 1:
            doc = get_obj_attr_doc(pd.Series, self._closures[-1].name) or doc

        return doc


@add_dunder_operators # This is necessary to overload all dunder operators.
class PandasSeriesContext(ClosureFactoryBase):
    """Build callable for series attributes and operators.

    Use the global instance like::

        from pandas_paddles import S
        s[S < 0]

    All operations (item/attribute access, method calls) are passed to the
    series of the context.

    This is useful in combination with :attr:`~pandas.Series.loc`,
    :attr:`~pandas.Series.iloc`, and other methods that accept callables
    taking the series to act on as argument, e.g., `.agg()` after a
    group-by.

    Examples
    --------
    Usage with ``[]``, ``.loc[]`` or ``.iloc[]``::

        from pandas_paddles import S
        s = pd.Series(range(10))
        s[S <= 2]
        # Out:
        # 0    0
        # 1    1
        # 2    2
        # dtype: int64

    Aggregating a single column after ``groupby`` with
    ``groupby(...)[col].agg()``::

        df = pd.DataFrame({
            "x": [1, 2, 3, 4],
            "y": ["a", "b", "b", "a"],
            "z": [0.1, 0.5, 0.6, 0.9],
        })
        df.groupby("y")["x"].agg(S.max() - S.min())
        # Out:
        # y
        # a    3
        # b    1
        # Name: x, dtype: int64
    
    Appying multiple aggregations to a single column::

        df.groupby("y")["x"].agg([
            S.max() - S.min(),
            S.mean(),
        ])
        # Out:
        #    S.max() - S.min()  S.min()
        # y                            
        # a                  3        1
        # b                  1        2

    Aggregating multiple columns (**Note:** You must wrap the
    ``S``-expressions in a ``list`` even when using only one expression!)::

        df.groupby("y").agg([S.min()])
        # Out:
        #         x       z
        #   S.min() S.min()
        # y                
        # a       1     0.1
        # b       2     0.5

    Multiple ``S``-expressions work the same::

        df.groupby("y").agg([S.min(), S.mean()])
        # Out:
        #         x                z         
        #   S.min() S.mean() S.min() S.mean()
        # y                                  
        # a       1      2.5     0.1     0.50
        # b       2      2.5     0.5     0.55
    
    ``S``-expressions can alsoe be passed in a ``dict`` argument to
    ``.agg()`` (Again, they always need to be wrapped in a ``list``!)::

        df.groupby("y").agg({
            "x": [S.min(), S.mean()],
            "z": [S.max(), S.max() - S.min()],
        })
        # Out:
        #         x                z                  
        #   S.min() S.mean() S.max() S.max() - S.min()
        # y                                           
        # a       1      2.5     0.9               0.8
        # b       2      2.5     0.6               0.1
    """
    wrapped_cls = (pd.Series,)
    wrapped_s = "S"
    def _get_doc(self) -> Optional[str]:
        doc = super()._get_doc()
        # Assume Series-level function for 1-level accessor
        if len(self._closures) == 1 and isinstance(self._closures[-1].name, str):
            for wrapped_cls in self.wrapped_cls:
                wrapped_doc = get_obj_attr_doc(wrapped_cls, self._closures[-1].name) or doc
                if wrapped_doc is not None:
                    break
            doc = wrapped_doc
        # Check for typed Series accessors
        elif len(self._closures) > 1 and self._closures[0].name in ('dt', 'str'):
            doc = (
                get_obj_attr_doc(
                    getattr(pd.Series, self._closures[0].name),
                    self._closures[-1].name,
                )
                or doc
            )

        return doc

DF = PandasDataframeContext()
S = PandasSeriesContext()
