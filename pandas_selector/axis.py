"""Select axis labels (columns or index) of a data frame."""
import operator
from typing import Any, Callable, List, Optional, Sequence
from warnings import warn

import numpy as np
import pandas as pd


Indices = List[int]


class Selection:
    """Container for selection along a data frame axis with combination logic."""
    def __init__(self, indices:Optional[Indices]=None, mask:Optional[Sequence[int]]=None):
        if mask is not None:
            if indices is not None:
                raise ValueError("indices and mask cannot be passed together")
            indices = np.nonzero(mask)[0].tolist()

        self.indices: Indices = indices

    def __and__(self, other: "Selection") -> "Selection":
        def and_indices(a, b):
            r = []
            for i in b:
                if i in a:
                    r.append(i)
            return r
        indices = _combine_nones(self.indices, other.indices, and_indices)
        return Selection(indices)

    def __or__(self, other: "Selection") -> "Selection":
        def or_indices(a, b):
            return a + [i for i in b if i not in a]

        indices = _combine_nones(self.indices, other.indices, or_indices)
        return Selection(indices)

# Utilities to collect and combine column selections
def _combine_nones(a: Optional[Indices], b: Optional[Indices], fn_both:Callable[[Indices, Indices], Indices]):
    if a is None and b is None:
        return None
    if a is not None and b is None:
        return a
    if a is None and b is not None:
        return b
    return fn_both(a, b)

# Column selection operator closures
class BaseOp:
    """API definition of the closure object."""
    def __call__(self, df: pd.DataFrame) -> Selection:
        """Evaluate operator on data frame from context."""
        raise NotImplementedError("Must be implemented in sub-class.")


class LabelSelectionOp(BaseOp):
    """Explicitely select labels."""
    def __init__(self, labels, level=None):
        if isinstance(labels, list):
            labels = tuple(labels)
        elif not isinstance(labels, tuple):
            labels = (labels,)
        self.labels = labels
        self.level=level

    def __call__(self, df):
        idx = np.arange(len(df.columns))
        if self.level is None:
            cands = df.columns
        else:
            cands = df.columns.get_level_values(self.level)

        indices = []
        for lbl in self.labels:
            indices.extend(idx[cands == lbl])

        return Selection(indices)


class LabelPredicateOp(BaseOp):
    """Select labels by a predicate, e.g. ``startswith``."""
    def __init__(self, meth, args, kwargs, level=None):
        self.meth = meth
        self.args = args
        self.kwargs = kwargs
        self.level = level

    def __call__(self, df: pd.DataFrame) -> Selection:
        if self.level is None:
            str_accessor = df.columns.str
        else:
            str_accessor = df.columns.get_level_values(self.level).str

        meth = getattr(str_accessor, self.meth)
        mask = meth(*self.args, **self.kwargs)
        return Selection(mask=mask)


class EllipsisOp(BaseOp):
    """Select all columns."""
    def __call__(self, df: pd.DataFrame) -> Selection:
        return Selection(mask=np.ones(len(df.columns), dtype=bool))


class BinaryOp(BaseOp):
    """Combine two operators."""
    def __init__(self, left: BaseOp, right: BaseOp, op: Callable[[Any, Any], Any]):
        self.left = left
        self.right = right
        self.op = op

    def __call__(self, df: pd.DataFrame) -> Selection:
        sel_left = self.left(df)
        sel_right = self.right(df)
        return self.op(sel_left, sel_right)


class DtypesOp:
    """Select columns by dtype."""
    def __init__(self, dtypes: Sequence, sample_size:int=10):
        self.dtypes = dtypes
        self.sample_size = sample_size

    def __call__(self, df):
        mask = np.zeros(len(df.columns), dtype=bool)
        for dtype in self.dtypes:
            for typ in (str, bytes):
                if dtype in (typ, typ.__name__):
                    mask |= (df.sample(min(len(df), self.sample_size))
                            .applymap(lambda i: isinstance(i, typ))
                            .agg("all")
                            .values
                           )
                    break
            else:
                mask |= (df.dtypes == dtype).values

        return Selection(mask=mask)


# Objects to create, compose, and evaluate column selection operators
class OpComposerBase:
    """Base-class for composing column selection operations.

    This class wraps around the actual operation and overloads the relevant
    operators (``+``, ``&``, and ``|``) and defers the evaluation of the
    operators until called (by the context data-frame in ``.loc[]``).
    """
    def __init__(self, op=None):
        self.op = op or Selection()

    def get_other_op(self, other):
        """Get/create a wrapped operation for composing operations."""
        if isinstance(other, OpComposerBase):
            return other.op

        # Assume label selection
        if isinstance(other, list):
            return LabelOp(other)
        if isinstance(other, str):
            return LabelOp([other])

        if other is ...:
            return EllipsisOp()

        if isinstance(other, (type, np.dtype)):
            return DtypeEqualOp(other)

        raise ValueError(f"Cannot convert argument of type {type(other)!r} to selection operator")

    def __and__(self, other):
        return OpComposerBase(BinaryOp(
            self.op,
            self.get_other_op(other),
            op=operator.and_,
            ))

    def __rand__(self, other):
        return OpComposerBase(BinaryOp(
            self.get_other_op(other),
            self.op,
            op=operator.and_,
            ))

    def __or__(self, other):
        return OpComposerBase(BinaryOp(
            self.op,
            self.get_other_op(other),
            op=operator.or_,
            ))

    def __ror__(self, other):
        return OpComposerBase(BinaryOp(
            self.get_other_op(other),
            self.op,
            op=operator.or_,
            ))

    def __add__(self, other):
        return self | other

    def __radd__(self, other):
        return other | self

    def __call__(self, df):
        """Evaluate the wrapped operations."""
        selection = self.op(df)
        return df.columns[selection.indices]


class LabelComposer(OpComposerBase):
    """Compose callable to select columns by name.

    Columns can be selected by name or string predicates:
    - ``startswith``
    - ``endswith``
    - ``contains``
    - ``match``
    which are passed through to ``pd.Series.str``.
    """
    # TODO: Implement ``C.lower()...``
    def __init__(self, op=None, level=None):
        super().__init__(op)
        self.level = level

    def __getitem__(self, labels):
        return OpComposerBase(LabelSelectionOp(labels, self.level))

    def startswith(self, *args, **kwargs):
        return OpComposerBase(LabelPredicateOp("startswith", args, kwargs, self.level))

    def endswith(self, *args, **kwargs):
        return OpComposerBase(LabelPredicateOp("endswith", args, kwargs, self.level))

    def contains(self, *args, **kwargs):
        return OpComposerBase(LabelPredicateOp("contains", args, kwargs, self.level))

    def match(self, *args, **kwargs):
        return OpComposerBase(LabelPredicateOp("match", args, kwargs, self.level))


class LeveledComposer:
    """Compose callable to access multi-level index labels."""
    def __getitem__(self, level):
        return LabelComposer(level=level)


class DtypeComposer:
    """Compose callable to select columns by dtype."""
    def __init__(self, sample_size=10):
        self.sample_size = sample_size

    def __eq__(self, dtype):
        return OpComposerBase(DtypesOp((dtype,), self.sample_size))

    def isin(self, dtypes):
        return OpComposerBase(DtypesOp(dtypes, self.sample_size))


class SelectionComposer(LabelComposer):
    """Compose callable to select or sort columns.

    This acts as global entrypoint.

    Use the global instance like::

        # Move columns x, z to left
        from pandas_selector import C
        df.loc[:, C["x", "z"] | ...]

    Other use-cases:

    - Select by dtype::

        df.loc[:, C.dtype == str]
        df.loc[:, C.dtype == int]
        df.loc[:, C.dtype.isin((str, int))]

      Note that for "non-trivial" dtypes (i.e. those stored in
      ``object``-typed columns, e.g. ``str``), a subsample of the dataframe
      is tested explicitely. The sample-size can be set with
      :attr:`~SelectionComposer.sample_size`.

    - Select all columns starting with ``"PRE"``::

        df.loc[:, C.startswith("PRE")]
        # or just move them to the left and keep the remaining columns in
        # the data frame
        df.loc[:, C.startswith("PRE") | ...]

    Selections can be combined with ``&`` (intersection) and ``|`` or ``+``
    (union). In intersections, the right-most order takes precedence, while
    it's the left-most for unions, e.g. the following will select all
    columns with first-level label "b" starting with the columns with
    second-level labels "Y" and "Z" followed by all other second-level
    labels with first-level "b"::

        C.levels[0]["b"] & (C.levels[1]["Y"] | ...)
    """
    def __init__(self, op=None, sample_size=None):
        super().__init__(op=op)
        self.dtype = DtypeComposer()
        self.levels = LeveledComposer()
        if sample_size is not None:
            self.sample_size = sample_size

    @property
    def sample_size(self):
        """Sample size for dtype determination of object-typed columns."""
        return self.dtype.sample_size

    @sample_size.setter
    def sample_size(self, val):
        self.dtype.sample_size = val

    # Warn about experimental status of this feature.
    # TODO: Remove once API is stable
    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if name != "__init__":
            warn("Column selection is an experimental feature! The API might change in minor version update.", stacklevel=2)
        return attr

C = SelectionComposer()
