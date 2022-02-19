"""Access data frame/series from context in ``.loc[]``, ``.iloc[]``, ``.assign()``, and others."""

from typing import Any, Callable, ClassVar, Dict, Iterable, Optional, Union, Tuple, Type

import pandas as pd

# The context in which the wrappers might be used
PdContext = Union[pd.DataFrame, pd.Series]

# Wrappers for attribute, item and operator access
class WrapperBase:
    """Base class for wrapping attribute, item or operator/method access."""
    def __init__(self, name: str):
        """
        Parameters
        ----------
        name
            Name of the accessed object member.
        """
        self.name = name

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.name}>"

    def __call__(self, obj: Any, root_obj: PdContext) -> Any:
        """Access member of wrapped object.

        Parameters
        ----------
        obj
            Anything that can be reached view item-, attribute-, or
            method-calls from a ``~pandas.DataFrame`` or ``~pandas.Series``.
        root_obj
            The original data frame or series from the context.

        Returns
        -------
        member
            The referenced member of ``obj``.
        """
        raise NotImplementedError("Must be implemented by a sub-class.")

    def __getstate__(self) -> Dict[str, Any]:
        return self.__dict__.copy()

    def __setstate__(self, state:Dict[str, Any]):
        self.__dict__.update(state)


class Attribute(WrapperBase):
    """Wrap ``df.column_name`` or similar access patterns."""
    def __call__(self, obj, root_obj: PdContext) -> Any:
        """Access attribute of wrapped object.

        Parameters
        ----------
        obj
            Anything that can be reached view item-, attribute-, or
            method-calls from a ``~pandas.DataFrame`` or ``~pandas.Series``.
        root_obj
            The original data frame or series from the context.

        Returns
        -------
        member
            The referenced member of ``obj``.
        """
        return getattr(obj, self.name)

    def __str__(self):
        return f".{self.name}"


class Item(WrapperBase):
    """Wrap ``df["column_name"]`` or similar access patterns."""
    def __call__(self, obj, root_obj: PdContext):
        """Access item of wrapped object.

        Parameters
        ----------
        obj
            Anything that can be reached view item-, attribute-, or
            method-calls from a ``~pandas.DataFrame`` or ``~pandas.Series``.
        root_obj
            The original data frame or series from the context.

        Returns
        -------
        member
            The referenced member of ``obj``.
        """
        return obj[self.name]

    def __str__(self):
        return f"[{self.name!r}]"


class Method(WrapperBase):
    """Wrap method and operator calls.

    This can also be nested, i.e. use ``DF`` or ``S`` in method arguments.

    Examples
    --------
    Operators::

        DF["x"] <= other # or DF.x <= other

        # dynamically create comparison predicate from the same data frame
        DF["x"] <= DF["x"].mean()

        # or use another column
        DF["x"] <= DF["y"]
        DF["x"] <= DF["y"].min()

    Access series methods::

        DF["x"].method() # or DF.x.method()

        # You can also pass arguments.

        DF["x"].clip(0)
        DF["x"].clip(upper=0)

        # You can use DF (or S) in the arguments to access the outer object
        DF["x"].clip(DF["y"].min())
        DF["x"].clip(upper=DF["y"].min())
    """
    def __init__(self, name: str, *args: Any, **kwargs: Any):
        """
        Parameters
        ----------
        name
            Method or operator name, e.g. `mean` or `__eq__`.
        args, kwargs
            (Optional) arguments for the method or operator, e.g. the second
            argument for a binary operator.
        """
        super().__init__(name)
        self.args = args
        self.kwargs = kwargs

    def __repr__(self) -> str:
        arg_reprs = (
            [f"{a!r}" for a in self.args]
            + [f"{k}={a!r}" for k, a in self.kwargs.items()]
            )

        return f"<{type(self).__name__}: {self.name}({', '.join(arg_reprs)})>"

    def __str__(self) -> str:
        # Use shorter `str` representation for accessors and `repr` for the
        # rest
        fmt_arg = lambda a: str(a) if isinstance(a, AccessorBase) else repr(a)
        arg_strs = (
            [fmt_arg(a) for a in self.args]
            + [f"{k}={fmt_arg(a)}" for k, a in self.kwargs.items()]
            )
        return f".{self.name}({', '.join(arg_strs)})"

    def _evaluate_method_arg(self, arg: Any, root_obj: PdContext):
        """Evaluatue any ``DF``- or ``S``-based arguments for the method
        call.

        This is needed to support things like (``DF['x'].mean()`` will be
        evaluated with ``df``)::

            df.assign(
              y = DF['x'].clip(low=DF['x'].mean() - 0.5)
            )

        Parameters
        ----------
        arg
            The method argument.
        root_obj
            The dataframe or series to evaluate ``arg`` with.

        Returns
        -------
        eval_arg
            Evaluated method argument if the argument is ``DF`` or ``S``
            based, else just ``arg``.
        """
        if isinstance(arg, AccessorBase):
            return arg(root_obj)
        return arg

    def __call__(self, obj: Any, root_obj: PdContext) -> Any:
        """Call method ``self.name`` on ``obj``.

        Parameters
        ----------
        obj
            Anything that can be reached view item-,attribute- or
            method-calls from a ``~pandas.DataFrame`` or ``~pandas.Series``.
        root_obj
            The original data frame or series from the context.

        Returns
        -------
        result
            The result of the method or operator call.
        """
        op_meth = getattr(obj, self.name)
        return op_meth(
            *[self._evaluate_method_arg(arg, root_obj) for arg in self.args],
            **{k: self._evaluate_method_arg(arg, root_obj) for k, arg in self.kwargs.items()}
        )


def _add_dunder_operators(cls):
    """Dress class with all sensible comparison operations.

    The class must implement a ``_operator_proxy`` method.

    .. note::
        This need to be applied on the concrete classes not the base class
        to allow copying of docstrings.
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
        setattr(cls, op, fix_closure(op))
    return cls


def _get_obj_attr_doc(obj_or_class: Any, attr: str):
    """Get doc-string for attribute ``attr`` of ``obj_or_class`` if it exists."""
    if isinstance(attr, str):
        a = getattr(obj_or_class, attr, None)
        if a:
            return a.__doc__
    return None


class AccessorBase:
    """Abstract base-class for DataFrame and Series context accessors."""
    wrapped_cls: ClassVar[Type] = type('NotABaseOfAnything', (), {})
    def __init__(self,
                 levels: Optional[Iterable[WrapperBase]]=None):
        """
        Parameters
        ----------
        levels:
            Iterable of callables to extract attributes from data frames or series.
        """
        self._levels: Tuple[WrapperBase, ...] = ()
        if levels is not None:
            self._levels = tuple(levels)

        # Update the doc-string if possible
        self.__doc__ = self._get_doc()

    def __getstate__(self) -> Dict[str, Any]:
        return self.__dict__.copy()

    def __setstate__(self, state: Dict[str, Any]):
        self.__dict__.update(state)

    def _get_doc(self) -> Optional[str]:
        return type(self).__doc__

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {'.'.join(repr(l) for l in self._levels)}>"

    def __str__(self) -> str:
        return ''.join(str(l) for l in self._levels)

    def __getattr__(self, name: str) -> 'AccessorBase':
        return type(self)(self._levels + (Attribute(name),))

    def __getitem__(self, key: str) -> 'AccessorBase':
        return type(self)(self._levels + (Item(key),))

    def _operator_proxy(self, op_name: str) -> Callable:
        """Generate proxy function for built-in operators.

        Used by :func:`_add_dunder_operators`
        """
        def op_wrapper(*args, **kwargs):
            return type(self)(self._levels + (Method(op_name, *args, **kwargs),))
        return op_wrapper

    def __call__(self, *args: Any, **kwargs: Any) -> Union[pd.DataFrame, pd.Series, Any]:
        # Heuristic: Assume the selector is applied if exactly one DataFrame
        # or Series argument is passed.
        if len(args) == 1 and isinstance(args[0], self.wrapped_cls):
            obj = root_df = args[0]
            for lvl in self._levels:
                obj = lvl(obj, root_df)
            return obj

        # Create a new accessor with the last level called as a method.
        return type(self)(self._levels[:-1] + (Method(self._levels[-1].name, *args, **kwargs),))


@_add_dunder_operators # This is necessary to overload all dunder operators.
class DataframeAccessor(AccessorBase):
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
    :attr:`pandas.Dataframe.iloc`:

    >>> DF = DataframeAccessor()
    >>> df = pd.DataFrame({"x": [1, 2, 3, 4]})
    >>> df.loc[DF["x"] <= 2]

    Usage with :meth:`~pandas.DataFrame.assign()`:

    >>> df.assign(y = DF["x"] * 2)
    >>> df
    """
    wrapped_cls = pd.DataFrame
    def _get_doc(self) -> Optional[str]:
        doc = super()._get_doc()
        # Assume DataFrame-level function for 1-level accessor
        if len(self._levels) == 1 and isinstance(self._levels[-1].name, str):
            doc = _get_obj_attr_doc(self.wrapped_cls, self._levels[-1].name) or doc
        # Check for typed Series accessors for 3+-level accessor
        elif len(self._levels) >= 3 and self._levels[-2].name in ('dt', 'str'):
            doc = (
                _get_obj_attr_doc(
                    getattr(pd.Series, self._levels[-2].name),
                    self._levels[-1].name,
                )
                or doc
            )
        # Check for Series-level function for 2+-level accessor
        elif len(self._levels) > 1:
            doc = _get_obj_attr_doc(pd.Series, self._levels[-1].name) or doc

        return doc



@_add_dunder_operators # This is necessary to overload all dunder operators.
class SeriesAccessor(AccessorBase):
    """Build callable for series attributes and operators.

    Use the global instance like::

        from pandas_paddles import S
        s[S < 0]

    All operations (item/attribute access, method calls) are passed to the
    series of the context.

    This is useful in combination with :attr:`~pandas.Series.loc`,
    :attr:`~pandas.Series.iloc` and other methods that accept callables
    taking the series to act on as argument.

    Examples
    --------
    Usage with ``[]``, ``loc`` or ``iloc``:

    >>> S = SeriesAccessor()
    >>> s = pd.Series(range(10))
    >>> s[S <= 2]
    """
    wrapped_cls = pd.Series
    def _get_doc(self) -> Optional[str]:
        doc = super()._get_doc()
        # Assume Series-level function for 1-level accessor
        if len(self._levels) == 1 and isinstance(self._levels[-1].name, str):
            doc = _get_obj_attr_doc(self.wrapped_cls, self._levels[-1].name) or doc
        # Check for typed Series accessors
        elif len(self._levels) > 1 and self._levels[0].name in ('dt', 'str'):
            doc = (
                _get_obj_attr_doc(
                    getattr(pd.Series, self._levels[0].name),
                    self._levels[-1].name,
                )
                or doc
            )

        return doc
