"""Select axis labels (columns or index) of a data frame."""
import operator
from typing import Any, Callable, List, Optional, Sequence
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from warnings import warn

import numpy as np
import pandas as pd


Indices = List[int]


class Selection:
    """Container for selection along a data frame axis with combination logic. """
    def __init__(self, included:Optional[Indices]=None, excluded:Optional[Indices]=None, *,  mask:Optional[Sequence[int]]=None):
        """
        If ``mask`` is passed, ``included`` and ``excluded`` must be ``None``!

        Parameters
        ----------
        included:
            List of indices included in the selection.
        excluded:
            List of indices excluded from the selection.
        mask
            Boolean array that will be converted to list of included
            indices: All indices with corresponding truthy/non-zero value
            will be included in the selection.
        """
        if mask is not None:
            if included is not None:
                raise ValueError("included indices and mask cannot be passed together")
            if excluded is not None:
                raise ValueError("excluded indices and mask cannot be passed together")
            included = np.nonzero(mask)[0].tolist()

        self.included: Optional[Indices] = included
        self.excluded: Optional[Indices] = excluded

    def apply(self, axis:Literal["columns", "index"], df: pd.DataFrame):
        labels = getattr(df, axis)
        included = self.included
        if included is None:
            included = range(len(labels))

        if self.excluded is not None:
            excluded = set(self.excluded)
        else:
            excluded = set()

        return labels[[i for i in included if not i in excluded]]

    def __and__(self, other: "Selection") -> "Selection":
        included=_combine_nones(self.included, other.included, intersect_indices)
        excluded=_combine_nones(self.excluded, other.excluded, union_indices)
        if included is not None and excluded is not None:
            included = [i for i in included if i not in excluded]

        return Selection(included, excluded)

    def __or__(self, other: "Selection") -> "Selection":
        included = _combine_nones(self.included, other.included, union_indices)
        excluded = _combine_nones(self.excluded, other.excluded, intersect_indices)
        if included is not None and excluded is not None:
            excluded = [i for i in excluded if i not in included]

        return Selection(included, excluded)

    def __invert__(self) -> "Selection":
        return Selection(self.excluded, self.included)


# Utilities to collect and combine column selections
def _combine_nones(a: Optional[Indices], b: Optional[Indices], fn_both:Callable[[Indices, Indices], Indices]) -> Optional[Indices]:
    if a is None and b is None:
        return None
    if a is not None and b is None:
        return a
    if a is None and b is not None:
        return b
    return fn_both(a, b)


def intersect_indices(left: Indices, right: Indices) -> Indices:
    r = []
    for i in right:
        if i in left:
            r.append(i)
    return r


def union_indices(left: Indices, right: Indices) -> Indices:
    return left + [i for i in right if i not in left]


# Column selection operator closures
class BaseOp:
    """API definition of the closure object."""
    def __call__(self, axis: Literal["columns", "index"], df: pd.DataFrame) -> Selection:
        """Evaluate operator on data frame from context."""
        raise NotImplementedError("Must be implemented in sub-class.")


class LabelSelectionOp(BaseOp):
    """Explicitely select labels."""
    def __init__(self, labels, level=None):
        if isinstance(labels, list):
            labels = tuple(labels)
        elif not isinstance(labels, (slice, tuple)):
            # Convert "scalar" values to some iterable
            labels = (labels,)
        self.labels = labels
        self.level = level

    def __call__(self, axis, df):
        labels = getattr(df, axis)
        idx = np.arange(len(labels))
        if self.level is None:
            cands = labels
        else:
            cands = labels.get_level_values(self.level)

        indices = []
        if isinstance(self.labels, tuple):
            for lbl in self.labels:
                indices.extend(idx[cands == lbl])
        elif isinstance(self.labels, slice):
            # NOTE: We need to make this more complex because we also need
            # to treat situation with multiple repetitions of the same
            # value, e.g., cases of multi-index levels.
            in_slice = self.labels.start is None
            reached_slice_stop = False
            for i, lbl in enumerate(cands):
                if not in_slice and lbl == self.labels.start:
                    in_slice = True
                if reached_slice_stop and lbl != self.labels.stop:
                    # We stepped over the end of the slice.
                    break
                if in_slice:
                    indices.append(i)
                    if self.labels.stop is not None and lbl == self.labels.stop:
                        reached_slice_stop = True
        else:
            # This should never be reached becaus of the argument processing
            # in __init__.
            raise ValueError(f"Unexpected type for self.labels: {type(self.labels)}: {self.labels!r}")

        return Selection(indices)

    def __str__(self):
        if isinstance(self.labels, slice):
            fmt = lambda o, default: repr(o) if o else default
            items = [fmt(self.labels.start, ''), fmt(self.labels.stop, '')]
            if self.labels.step:
                items.append(repr(self.labels.step))
            pp_labels = ':'.join(items)
        else:
            pp_labels = ', '.join(str(l) for l in self.labels)

        if self.level:
            return f'(level={self.level})[{pp_labels}]'
        return f'[{pp_labels}]'


class LabelPredicateOp(BaseOp):
    """Select labels by a predicate, e.g. ``startswith``."""
    def __init__(self, meth, args, kwargs, level=None):
        self.meth = meth
        self.args = args
        self.kwargs = kwargs
        self.level = level

    def __str__(self):
        def pp(a):
            if isinstance(a, tuple):
                return [repr(i) for i in a]
            elif isinstance(a, dict):
                return [f'{k}={v!r}' for k, v in a.items()]

            return [repr(a)]

        pp_args = ', '.join(pp(self.args) + pp(self.kwargs))

        if self.level:
            return f'(level={self.level}).{self.meth}({pp_args})'
        return f'.{self.meth}({pp_args})'

    def __call__(self, axis, df: pd.DataFrame) -> Selection:
        labels = getattr(df, axis)
        if self.level is None:
            str_accessor = labels.str
        else:
            str_accessor = labels.get_level_values(self.level).str

        meth = getattr(str_accessor, self.meth)
        mask = meth(*self.args, **self.kwargs)
        return Selection(mask=mask)


class EllipsisOp(BaseOp):
    """Select all columns."""
    def __call__(self, axis, df: pd.DataFrame) -> Selection:
        labels = getattr(df, axis)
        return Selection(mask=np.ones(len(labels), dtype=bool))

    def __str__(self):
        return '...'


class BinaryOp(BaseOp):
    """Combine two operators."""
    def __init__(self, left: BaseOp, right: BaseOp, op: Callable[[Any, Any], Any]):
        self.left = left
        self.right = right
        self.op = op

    def __str__(self):
        op_name = getattr(self.op, '__name__', str(self.op))
        return f'({self.left}) {op_name} ({self.right})'

    def __call__(self, axis, df: pd.DataFrame) -> Selection:
        sel_left = self.left(axis, df)
        sel_right = self.right(axis, df)

        return self.op(sel_left, sel_right)


class UnaryOp(BaseOp):
    def __init__(self, wrapped: BaseOp, op: Callable[[Any], Any]):
        self.wrapped = wrapped
        self.op = op

    def __str__(self):
        op_name = getattr(self.op, '__name__', str(self.op))
        return f'{op_name}({self.wrapped})'

    def __call__(self, axis, df: pd.DataFrame) -> Selection:
        sel = self.wrapped(axis, df)

        return self.op(sel)


class DtypesOp:
    """Select columns by dtype."""
    def __init__(self, dtypes: Sequence, sample_size:int=10):
        self.dtypes = dtypes
        self.sample_size = sample_size

    def __str__(self):
        dtypes = self.dtypes
        if len(dtypes) == 1:
            return f'dtype == {dtypes[0]}'
        return f'dtype in {dtypes}'

    def __call__(self, axis, df):
        if axis != "columns":
            raise ValueError("Selection by dtype is only supported for column selection.")
        labels = getattr(df, axis)
        mask = np.zeros(len(labels), dtype=bool)
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
    def __init__(self, axis:Literal["columns", "index"], op):
        self.axis = axis
        self.op = op or Selection()

    def __str__(self):
        return f'<{self.axis}: {self.op}>'

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
        return OpComposerBase(self.axis, BinaryOp(
            self.op,
            self.get_other_op(other),
            op=operator.and_,
            ))

    def __rand__(self, other):
        return OpComposerBase(self.axis, BinaryOp(
            self.get_other_op(other),
            self.op,
            op=operator.and_,
            ))

    def __or__(self, other):
        return OpComposerBase(self.axis, BinaryOp(
            self.op,
            self.get_other_op(other),
            op=operator.or_,
            ))

    def __ror__(self, other):
        return OpComposerBase(self.axis, BinaryOp(
            self.get_other_op(other),
            self.op,
            op=operator.or_,
        ))

    def __add__(self, other):
        return self | other

    def __radd__(self, other):
        return other | self

    def __invert__(self):
        return OpComposerBase(self.axis, UnaryOp(
            self.op,
            op=operator.invert,
        ))

    def __call__(self, df:pd.DataFrame) -> pd.Index:
        """Evaluate the wrapped operations."""
        selection = self.op(self.axis, df)
        return selection.apply(self.axis, df)


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
    def __init__(self, axis, op=None, level=None):
        super().__init__(axis, op)
        self.level = level

    def _get_op_composer(self, op):
        return OpComposerBase(self.axis, op)

    def __getitem__(self, labels):
        return self._get_op_composer(LabelSelectionOp(labels, self.level))

    def startswith(self, *args, **kwargs):
        return self._get_op_composer(LabelPredicateOp("startswith", args, kwargs, self.level))

    def endswith(self, *args, **kwargs):
        return self._get_op_composer(LabelPredicateOp("endswith", args, kwargs, self.level))

    def contains(self, *args, **kwargs):
        return self._get_op_composer(LabelPredicateOp("contains", args, kwargs, self.level))

    def match(self, *args, **kwargs):
        return self._get_op_composer(LabelPredicateOp("match", args, kwargs, self.level))

class LeveledComposer:
    """Compose callable to access multi-level index labels."""
    def __init__(self, axis):
        self.axis = axis

    def __getitem__(self, level):
        return LabelComposer(self.axis, level=level)


class DtypeComposer:
    """Compose callable to select columns by dtype."""
    def __init__(self, axis, sample_size=10):
        self.axis = axis
        self.sample_size = sample_size

    def __eq__(self, dtype):
        return OpComposerBase(self.axis, DtypesOp((dtype,), self.sample_size))

    def isin(self, dtypes):
        return OpComposerBase(self.axis, DtypesOp(dtypes, self.sample_size))


class SelectionComposerBase(LabelComposer):
    """Compose callable to select or sort axis labels (index and columns).

    .. note::
        Use :class:`ColumnSelectionComposer` (``C``) if you want to select
        columns.

    This acts as global entrypoint.

    Use the global instance like::

        # Move rows x, z to the top
        from pandas_paddles import I
        df.loc[I["x", "z"] | ...]

    Other use-cases:

    - Select slices of rows::

        df.loc[I["B":"E"] | I["P":"S"]]

    - Select all rows with index starting with ``"PRE"``::

        df.loc[I.startswith("PRE")]
        # or just move them to the top and keep the remaining columns in
        # the data frame
        df.loc[I.startswith("PRE") | ...]

    - Access the level of a multi-index with::

        I.levels[0]
        I.levels["level-name"]

    Selections can be combined with ``&`` (intersection) and ``|`` or ``+``
    (union). In intersections, the right-most order takes precedence, while
    it's the left-most for unions, e.g. the following will select all
    rows with first-level label "b" starting with the rows with
    second-level labels "Y" and "Z" followed by all other second-level
    labels with first-level "b"::

        I.levels[0]["b"] & (I.levels[1]["Y"] | ...)

    Inversion (negation) of selections is possible with ``~``, e.g. to select all but first-level label "b"::

        ~I.levels[0]["b"]

    This can also be applied to composed selections::

        ~(I.levels[0]["b"] | I.levels[1]["X", "Y"])
    """
    def __init__(self, axis, op=None):
        super().__init__(axis, op=op)
        self.levels = LeveledComposer(self.axis)

    # Warn about experimental status of this feature.
    # TODO: Remove once API is stable
    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if not name in {"__init__", "axis"}:
            warn("Column/index selection with C/I is an experimental feature! The API might change in minor version updates.", stacklevel=2)
        return attr


class ColumnSelectionComposer(SelectionComposerBase):
    """Compose callable to select or sort columns.

    This acts as global entrypoint.

    Use the global instance like::

        # Move columns x, z to left
        from pandas_paddles import C
        df.loc[:, C["x", "z"] | ...]

    Other use-cases:

    - Select slices of columns, e.g., when handling Excel-like named columns
      (A, B, ...)::

        df.loc[:, C["B":"E"] | C["P":"S"]]

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

    - Access the level of a multi-index with::

        C.levels[0]
        C.levels["level-name"]

    Selections can be combined with ``&`` (intersection) and ``|`` or ``+``
    (union). In intersections, the right-most order takes precedence, while
    it's the left-most for unions, e.g. the following will select all
    columns with first-level label "b" starting with the columns with
    second-level labels "Y" and "Z" followed by all other second-level
    labels with first-level "b"::

        C.levels[0]["b"] & (C.levels[1]["Y"] | ...)

    Inversion (negation) of selections is possible with ``~``, e.g. to select all but first-level label "b"::

        ~C.levels[0]["b"]

    This can also be applied to composed selections::

        ~(C.levels[0]["b"] | C.levels[1]["X", "Y"])
    """
    def __init__(self, axis, op=None, sample_size=None):
        super().__init__(axis, op=op)
        self.dtype = DtypeComposer(self.axis)
        if sample_size is not None:
            self.sample_size = sample_size

    @property
    def sample_size(self):
        """Sample size for dtype determination of object-typed columns."""
        return self.dtype.sample_size

    @sample_size.setter
    def sample_size(self, val):
        self.dtype.sample_size = val
