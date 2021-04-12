"""Access wrappers for data frames members."""
from typing import Callable, Optional, Sequence, Union

import pandas as pd

# Wrappers for attribute, item and operator access
class WrapperBase:
    """Base class for wrapping attribute, item or operator access."""
    def __init__(self, name: str):
        """
        Parameters
        ----------
        name
            Name of the accessed object member.
        """
        self.name = name

    def __repr__(self):
        return f"<{type(self).__name__} {self.name}>"

    def __call__(self, obj, root_df: pd.DataFrame):
        """Access member of wrapped object.

        Parameters
        ----------
        obj
            Typically the ``~pandas.DataFrame`` or ``~pandas.Series`` to act
            upon.
        root_df
            The original data frame from the context.
        """
        raise NotImplementedError("Must be implemented by a sub-class.")

class Attribute(WrapperBase):
    """Wrap ``df.column_name`` or similar access patterns."""
    def __call__(self, obj, root_df):
        """Access attribute of ``obj``.

        Parameters
        ----------
        obj
            Typically the ``~pandas.DataFrame`` or ``~pandas.Series`` to act
            upon.
        root_df
            The original data frame from the context. (Unused)
        """
        return getattr(obj, self.name)

    def __str__(self):
        return f".{self.name}"


class Item(WrapperBase):
    """Wrap ``df["column_name"]`` or similar access patterns."""
    def __call__(self, obj, root_df):
        return obj[self.name]

    def __str__(self):
        return f"[{self.name!r}]"

class Method(WrapperBase):
    """Wrap method and operator calls.

    E.g.

    * ``DF.x <= other`` or similar operator patterns
    * ``DF.x.method(...)``
    * :code:`DF.x.method(1 + 'abc')`
    """
    def __init__(self, name: str,
                 # this: "DataframeAccessor",
                 *args, **kwargs):
        """
        Parameters
        ----------
        name
            Operator name, e.g. `__eq__`.
        this
            ``DataframeAccessor`` to apply operator upon.
        *args, **kwargs
            Optional arguments for the operator, e.g. the second argument for a binary operator.
        """
        super().__init__(name)
        # self.this = this
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        # TODO include args[0] (other) in string where sensible
        return f"<{type(self).__name__}: {self.name}(...)>"

    # TODO include args[0] (other) in string where sensible
    def __str__(self):
        # return f"{self.this}.{self.name}(...)"
        return f".{self.name}(...)"

    def __call__(self, obj, root_df):
        # this = self.this(obj)
        op_meth = getattr(obj, self.name)
        if len(self.args) == 1 and isinstance(self.args[0], DataframeAccessor):
            other = self.args[0](root_df)
            return op_meth(other)
        return op_meth(*self.args, **self.kwargs)


def _add_dunder_operators(cls):
    """Dress class with all sensible comparison operations.

    The class must implement a ``_operator_proxy`` method.
    """
    for op in [
        "__abs__",
        "__add__",
        "__and__",
        "__bool__",
        "__contains__",
        "__div__",
        "__divmod__",
        "__eq__",
        "__floordiv__",
        "__ge__",
        "__gt__",
        "__invert__",
        "__le__",
        "__lt__",
        "__mul__",
        "__ne__",
        "__neg__",
        "__not__",
        "__or__",
        "__pos__",
        "__pow__",
        "__sub__",
        "__truediv__",
        "__xor__",
        ]:
        # Fix the closure of `op_wrap` to the current value of `op`. Without
        # `fix_closure()` all created methods point to the last `op` value.
        def fix_closure(op):
            def op_wrap(self, *args, **kwargs):
                return self._operator_proxy(op)(*args, **kwargs)
            return op_wrap
        setattr(cls, op, fix_closure(op))
    return cls


@_add_dunder_operators # This is necessary to overload all dunder operators.
class DataframeAccessor:
    """Build callable for column access and operators.

    Use the global instance like::

        from pandas_selector import DF
        df.loc[DF.x < 3]

    All operations (item/attribute access, method calls) are passed to the
    data frame of the context.

    This is useful in combination with :attr:`~pandas.DataFrame.loc`,
    :attr:`~pandas.DataFrame.iloc`, :meth:`~pandas.DataFrame.assign` and
    other methods that accept callables taking the data frame to act on as
    single argument.

    Examples
    --------
    Usage with ``loc`` or ``iloc``:

    >>> DF = DataframeAccessor()
    >>> df = pd.DataFrame({"x": [1, 2, 3, 4]})
    >>> df.loc[DF.x <= 2]

    Usage with ``assign()``:

    >>> df.assign(y = DF.x * 2)
    >>> df
    """
    def __init__(self,
                 levels:Union[Sequence[Callable], None]=None):
        """
        Parameters
        ----------
        levels:
            Sequence of callables to extract attributes from data frames or series.
        """
        self._levels = levels or ()

    def __repr__(self):
        return f"<{type(self).__name__} {'.'.join(repr(l) for l in self._levels)}>"

    def __str__(self):
        return ''.join(str(l) for l in self._levels)

    def __getattr__(self, name):
        return DataframeAccessor(self._levels + (Attribute(name),))

    def __getitem__(self, key):
        return DataframeAccessor(self._levels + (Item(key),))

    def _operator_proxy(self, op_name):
        """Generate proxy function for built-in operators.

        Used by :func:`_add_dunder_operators`
        """
        def op_wrapper(*args, **kwargs):
            return DataframeAccessor(self._levels + (Method(op_name, *args, **kwargs),))
        return op_wrapper

    def __call__(self, *args, **kwargs):
        # Heuristic: Assume the selector is applied if exactly one DataFrame
        # argument is passed.
        if len(args) == 1 and isinstance(args[0], pd.DataFrame):
            obj = root_df = args[0]
            for lvl in self._levels:
                obj = lvl(obj, root_df)
            return obj

        # Create a new DataframeAccessor
        return DataframeAccessor(self._levels[:-1] + (Method(self._levels[-1].name, *args, **kwargs),))
