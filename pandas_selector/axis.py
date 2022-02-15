import operator
from typing import Optional

import numpy as np

# Utilities to collect and combine column selections
def combine_nones(a, b, fn_both):
    if a is None and b is None:
        return None
    if a is not None and b is None:
        return a
    if a is None and b is not None:
        return b
    return fn_both(a, b)


class Selection:
    """Container for selection along a data frame axis with combination logic."""
    def __init__(self, indices=None, mask=None):
        if mask is not None:
            if indices is not None:
                raise ValueError("indices and mask cannot be passed together")
            indices = np.nonzero(mask)[0].tolist()

        self.indices = indices

    def __and__(self, other):
        def and_indices(a, b):
            r = []
            for i in a:
                if i in b:
                    r.append(i)
            return r
        indices = combine_nones(self.indices, other.indices, and_indices)
        return Selection(indices)

    def __or__(self, other):
        def or_indices(a, b):
            return a + [i for i in b if i not in a]

        indices = combine_nones(self.indices, other.indices, or_indices)
        return Selection(indices)

    def __add__(self, other):
        return self | other


# Column selection operator closures
class LabelSelectionOp:
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


class LabelMatchOp:
    def __init__(self, meth, args, kwargs, level=None):
        self.meth = meth
        self.args = args
        self.kwargs = kwargs
        self.level = level

    def __call__(self, df):
        if self.level is None:
            str_accessor = df.columns.str
        else:
            str_accessor = df.columns.get_level_values(self.level).str

        meth = getattr(str_accessor, self.meth)
        mask = meth(*self.args, **self.kwargs)
        return Selection(mask=mask)


class EllipsisOp:
    def __call__(self, df):
        return Selection(mask=np.ones(len(df.columns), dtype=bool))


class BinaryOp:
    def __init__(self, left, right, op):
        self.left = left
        self.right = right
        self.op = op

    def __call__(self, df):
        sel_left = self.left(df)
        sel_right = self.right(df)
        return self.op(sel_left, sel_right)


class DtypesOp:
    def __init__(self, dtypes, sample_size=10):
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
    def __init__(self, op=None):
        self.op = op or Selection()

    def get_other_op(self, other):
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
        selection = self.op(df)
        return df.columns[selection.indices]


class LabelComposer(OpComposerBase):
    def __init__(self, op=None, level=None):
        super().__init__(op)
        self.level = level

    def __getitem__(self, labels):
        return OpComposerBase(LabelSelectionOp(labels, self.level))

    def startswith(self, *args, **kwargs):
        return OpComposerBase(LabelMatchOp("startswith", args, kwargs, self.level))

    def endswith(self, *args, **kwargs):
        return OpComposerBase(LabelMatchOp("endswith", args, kwargs, self.level))

    def contains(self, *args, **kwargs):
        return OpComposerBase(LabelMatchOp("contains", args, kwargs, self.level))

    def match(self, *args, **kwargs):
        return OpComposerBase(LabelMatchOp("match", args, kwargs, self.level))


class LeveledComposer:
    def __getitem__(self, level):
        return LabelComposer(level=level)


class DtypeComposer:
    def __init__(self, sample_size=10):
        self.sample_size = sample_size

    def __eq__(self, dtype):
        return OpComposerBase(DtypesOp((dtype,), self.sample_size))

    def isin(self, dtypes):
        return OpComposerBase(DtypesOp(dtypes, self.sample_size))


class SelectionComposer(LabelComposer):
    def __init__(self, op=None):
        super().__init__(op=op)
        self.dtype = DtypeComposer()
        self.levels = LeveledComposer()


C = SelectionComposer()
