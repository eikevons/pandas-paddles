"""Closures for item, attribute, and method access."""

from typing import Any, Callable, ClassVar, Dict, Iterable, Optional, Union, Tuple, Type

import pandas as pd

# The context in which the wrappers might be used
PandasContext = Union[pd.DataFrame, pd.Series]

# Wrappers for attribute, item and operator access
class ClosureBase:
    """Base class for wrapping attribute, item or operator/method access closures."""
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

    def __call__(self, obj: Any, root_obj: PandasContext) -> Any:
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

    def as_node(self, parent=None):
        """Return an AST node."""
        return AstNode(self, parent=parent)


class AttributeClosure(ClosureBase):
    """Wrap ``df.column_name`` or similar access patterns."""
    def __call__(self, obj, root_obj: PandasContext) -> Any:
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


class ItemClosure(ClosureBase):
    """Wrap ``df["column_name"]`` or similar access patterns."""
    def __call__(self, obj, root_obj: PandasContext):
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


class MethodClosure(ClosureBase):
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
    def __init__(self, name: str, factory_cls: type, *args: Any, **kwargs: Any):
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
        self._factory_cls = factory_cls
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
        fmt_arg = lambda a: str(a) if isinstance(a, self._factory_cls) else repr(a)
        arg_strs = (
            [fmt_arg(a) for a in self.args]
            + [f"{k}={fmt_arg(a)}" for k, a in self.kwargs.items()]
            )

        return f".{self.name}({', '.join(arg_strs)})"

    def _evaluate_method_arg(self, arg: Any, root_obj: PandasContext):
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
        if isinstance(arg, self._factory_cls):
            return arg(root_obj)
        return arg

    def __call__(self, obj: Any, root_obj: PandasContext) -> Any:
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
