"""Factories for closures wrapping dataframe and series context."""

from itertools import chain
from typing import Any, Callable, ClassVar, Dict, Iterable, Optional, Union, Tuple, Type

import pandas as pd

from .closures import ClosureBase, AttributeClosure, ItemClosure, MethodClosure
from .util import AstNode
from . import operator_helpers


def _add_dunder_operators(cls):
    """Dress class with all sensible comparison operations.

    The class must implement a ``_operator_proxy`` method.

    .. note::
        This need to be applied on the concrete classes not the base class
        to allow copying of docstrings.
    """
    # Fix the closure of `op_wrap` to the current value of `op`. Without
    # `fix_closure()` all created methods point to the last `op` value.
    def fix_closure(op):
        def op_wrap(self, *args, **kwargs):
            return self._operator_proxy(op)(*args, **kwargs)
        # Update method metadata to improve usablility
        op_wrap.__name__ = op
        orig_doc = None
        orig_annot = None
        for pd_cls in {pd.Series} | {cls.wrapped_cls}:
            if hasattr(pd_cls, op):
                a = getattr(pd_cls, op)
                if not a.__doc__:
                    continue
                op_wrap.__doc__ = a.__doc__
                op_wrap.__annotations__ = a.__annotations__
                break

        return op_wrap

    for op in chain(operator_helpers.unary_ops, operator_helpers.binary_ops_non_reversable):
        lop = f"__{op}__"
        setattr(cls, lop, fix_closure(lop))

    for op in operator_helpers.binary_ops:
        lop = f"__{op}__"
        rop = f"__r{op}__"
        setattr(cls, lop, fix_closure(lop))
        setattr(cls, rop, fix_closure(rop))
    return cls


def _get_obj_attr_doc(obj_or_class: Any, attr: str):
    """Get doc-string for attribute ``attr`` of ``obj_or_class`` if it exists."""
    if isinstance(attr, str):
        a = getattr(obj_or_class, attr, None)
        if a:
            return a.__doc__
    return None


class ClosureFactoryBase:
    """Abstract base-class for generating DataFrame and Series context closures."""
    wrapped_cls: ClassVar[Type] = type('NotABaseOfAnything', (), {})
    wrapped_s: str = "X"
    def __init__(self,
                 closures: Optional[Iterable[ClosureBase]]=None):
        """
        Parameters
        ----------
        closures:
            Iterable of callables to extract attributes from data frames or series.
        """
        self._closures: Tuple[ClosureBase, ...] = ()
        if closures is not None:
            self._closures = tuple(closures)

        # Update the doc-string if possible
        self.__doc__ = self._get_doc()

    def __getstate__(self) -> Dict[str, Any]:
        return self.__dict__.copy()

    def __setstate__(self, state: Dict[str, Any]):
        self.__dict__.update(state)

    def _get_doc(self) -> Optional[str]:
        return type(self).__doc__

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {'.'.join(repr(l) for l in self._closures)}>"

    def __str__(self) -> str:
        # return "".join(str(l) for l in self._closures)
        return str(self.as_tree().pprint())

    # GH-21: Needed to use S in groupby(...)[col].agg([S. ...])
    @property
    def __name__(self) -> str:
        lines = str(self).splitlines()
        return ' '.join(l.strip() for l in lines)

    def __getattr__(self, name: str) -> "ClosureFactoryBase":
        return type(self)(self._closures + (AttributeClosure(name),))

    def __getitem__(self, key: str) -> "ClosureFactoryBase":
        return type(self)(self._closures + (ItemClosure(key),))

    def _operator_proxy(self, op_name: str) -> Callable:
        """Generate proxy function for built-in operators.

        Used by :func:`_add_dunder_operators`
        """
        def op_wrapper(*args, **kwargs):
            return type(self)(self._closures + (MethodClosure(op_name, type(self), *args, **kwargs),))
        return op_wrapper

    def __call__(self, *args: Any, **kwargs: Any) -> Union[pd.DataFrame, pd.Series, "ClosureFactoryBase"]:
        # Heuristic: Assume the selector is applied if exactly one DataFrame
        # or Series argument is passed.
        if len(args) == 1 and isinstance(args[0], self.wrapped_cls):
            obj = root_df = args[0]
            for lvl in self._closures:
                obj = lvl(obj, root_df)
            return obj

        # Create a new accessor with the last level called as a method.
        return type(self)(self._closures[:-1] + (MethodClosure(self._closures[-1].name, type(self), *args, **kwargs),))

    def as_tree(self):
        def to_node(x):
            if hasattr(x, "as_tree"):
                return x.as_tree()
            return AstNode(repr(x))

        cur = AstNode((self.wrapped_s,))
        for c in self._closures:
            if isinstance(c, (AttributeClosure, ItemClosure)):
                new = AstNode(str(c), parent=cur)
                cur.right = new
                cur = new
            elif isinstance(c, MethodClosure):
                op_type, op = operator_helpers.get_op_syntax(c.name)
                if op_type == "binary" and len(c.args) == 1 and not c.kwargs:
                    new = AstNode(op, left=cur.root, right=to_node(c.args[0]))
                    new.left.parent = new
                    new.right.parent = new
                    cur = new
                elif op_type == "reverse-binary" and len(c.args) == 1 and not c.kwargs:
                    new = AstNode(op, left=to_node(c.args[0]), right=cur.root)
                    new.left.parent = new
                    new.right.parent = new
                    cur = new
                elif op_type == "unary" and not c.args and not c.kwargs:
                    right = cur.root
                    new = AstNode((op,), right=right)
                    right.parent = new
                    cur = new
                else:
                    # The funntion name and arguments are encoded in the payload
                    payload = (
                        c.name,
                        [to_node(a) for a in c.args],
                        [(k, to_node(a)) for k, a in c.kwargs.items()]
                    )
                    new = AstNode(payload, parent=cur)
                    cur.right = new
                    cur = new

        return cur.root


@_add_dunder_operators # This is necessary to overload all dunder operators.
class DataframeContext(ClosureFactoryBase):
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
    wrapped_cls = pd.DataFrame
    wrapped_s = "DF"
    def _get_doc(self) -> Optional[str]:
        doc = super()._get_doc()
        # Assume DataFrame-level function for 1-level accessor
        if len(self._closures) == 1 and isinstance(self._closures[-1].name, str):
            doc = _get_obj_attr_doc(self.wrapped_cls, self._closures[-1].name) or doc
        # Check for typed Series accessors for 3+-level accessor
        elif len(self._closures) >= 3 and self._closures[-2].name in ('dt', 'str'):
            doc = (
                _get_obj_attr_doc(
                    getattr(pd.Series, self._closures[-2].name),
                    self._closures[-1].name,
                )
                or doc
            )
        # Check for Series-level function for 2+-level accessor
        elif len(self._closures) > 1:
            doc = _get_obj_attr_doc(pd.Series, self._closures[-1].name) or doc

        return doc



@_add_dunder_operators # This is necessary to overload all dunder operators.
class SeriesContext(ClosureFactoryBase):
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

    Aggregating a single ``groupby``ed column with
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
    wrapped_cls = pd.Series
    wrapped_s = "S"
    def _get_doc(self) -> Optional[str]:
        doc = super()._get_doc()
        # Assume Series-level function for 1-level accessor
        if len(self._closures) == 1 and isinstance(self._closures[-1].name, str):
            doc = _get_obj_attr_doc(self.wrapped_cls, self._closures[-1].name) or doc
        # Check for typed Series accessors
        elif len(self._closures) > 1 and self._closures[0].name in ('dt', 'str'):
            doc = (
                _get_obj_attr_doc(
                    getattr(pd.Series, self._closures[0].name),
                    self._closures[-1].name,
                )
                or doc
            )

        return doc
