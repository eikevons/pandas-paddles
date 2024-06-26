"""Factories for closures wrapping dataframe and series context."""

from itertools import chain
from typing import Any, Callable, ClassVar, Dict, Iterable, Optional, Union, Tuple, Type
from warnings import warn

import pandas as pd

from .closures import ClosureBase, AttributeClosure, ItemClosure, MethodClosure
from .util import AstNode
from . import operator_helpers


def add_dunder_operators(cls):
    """Dress class with all sensible comparison operations.

    The class must implement a ``_operator_proxy`` method.

    .. note::
        This need to be applied on the concrete classes not the base class
        to allow copying of docstrings.
    """
    # Fix the closure of `op_wrap` to the current value of `op`. Without
    # `fix_closure()` all created methods point to the last `op` value.

    cls_lookup_candidates = [pd.Series]
    for wrapped_cls in cls.wrapped_cls:
        if wrapped_cls in cls_lookup_candidates:
            continue
        cls_lookup_candidates.append(wrapped_cls)


    def fix_closure(op):
        def op_wrap(self, *args, **kwargs):
            return self._operator_proxy(op)(*args, **kwargs)
        # Update method metadata to improve usablility
        op_wrap.__name__ = op
        for orig_cls in cls_lookup_candidates:
            if hasattr(orig_cls, op):
                a = getattr(orig_cls, op)
                if not a.__doc__:
                    continue
                op_wrap.__doc__ = a.__doc__
                try:
                    op_wrap.__annotations__ = a.__annotations__
                except AttributeError:
                    pass
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


def get_obj_attr_doc(obj_or_class: Any, attr: str):
    """Get doc-string for attribute ``attr`` of ``obj_or_class`` if it exists."""
    if isinstance(attr, str):
        a = getattr(obj_or_class, attr, None)
        if a:
            return a.__doc__
    return None


def _get_closure_cmp_keys(closures: Iterable[ClosureBase]) -> Tuple:
    return tuple(cl._cmp_values() for cl in closures)


class ClosureFactoryBase:
    """Abstract base-class for generating DataFrame and Series context closures."""
    wrapped_cls: ClassVar[Tuple[Type]] = (type('NotABaseOfAnything', (), {}),)
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

        Used by :func:`add_dunder_operators`
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

    def __bool__(self):
        """Custom __bool__ to allow comparing closures in if-statements."""
        if not self._closures:
            return True

        cl = self._closures[-1]
        if not isinstance(cl, MethodClosure):
            return True

        op = cl.name[2:-2] 
        if op not in {"eq", "ne", "le", "lt", "ge", "gt"}:
            return True
        if op in {"ge", "gt", "le", "lt"}:
            warn(
                "Evaluating context expression directly as boolean with <, <=, >, >=. Are you sure you intend this?",
                stacklevel=2,
            )

        left = self._closures[:-1]
        right_expr = cl.args[0]

        ask_equal = op in {"eq", "le", "ge"}
        is_equal = False

        if isinstance(right_expr, type(self)):
            right = right_expr._closures

            left_cmp = _get_closure_cmp_keys(left)
            right_cmp = _get_closure_cmp_keys(right)

            is_equal = left_cmp == right_cmp

        return (is_equal and ask_equal) or (not is_equal and not ask_equal)
