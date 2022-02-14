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
    def __init__(self, *, mask=None, order=None):
        self.mask = mask
        self.order = order

    def evaluate(self, df) -> list:
        """Build list of selected axis labels."""
        # Empty selections act as a no-op pass-through
        if self.order is None and self.mask is None:
            return df

        sel = []
        if self.order is not None:
            for c in self.order:
                if c in df.columns:
                    sel.append(c)
                else:
                    raise ValueError(f"Columns {c!r} not found in data frame columns: {df.columns!r}")
        if self.mask is not None:
            for c in df.columns[self.mask]:
                if c not in sel:
                    sel.append(c)

        return sel

    def __and__(self, other):
        mask = combine_nones(self.mask, other.mask, operator.and_)

        def and_order(a, b):
            r = []
            for l in a:
                if l in b:
                    r.append(l)
            return r
        order = combine_nones(self.order, other.order, and_order)
        return Selection(mask, order)

    def __or__(self, other):
        mask = combine_nones(self.mask, other.mask, operator.or_)

        def or_order(a, b):
            return a + [i for i in b if i not in a]

        order = combine_nones(self.order, other.order, or_order)
        return Selection(mask=mask, order=order)

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
        if self.level is None:
            order = list(self.labels)
        else:
            order = []
            lvl = df.columns.get_level_values(self.level)
            for l in self.labels:
                order.extend(df.columns[lvl == l].to_list())

        return Selection(order=order)


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


class DtypeEqualOp:
    def __init__(self, dtype, sample_size=10):
        self.dtype = dtype
        self.sample_size = sample_size

    def __call__(self, df):
        for typ in (str, bytes):
            if self.dtype in (typ, typ.__name__):
                mask = (df.sample(min(len(df), self.sample_size))
                        .applymap(lambda i: isinstance(i, typ))
                        .agg("all")
                       )
                break
        else:
            mask = (df.dtypes == self.dtype).values

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
        return selection.evaluate(df)


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
        return OpComposerBase(DtypeEqualOp(dtype, self.sample_size))

    def isin(self, dtypes):
        raise NotImplementedError("isin currently not implemented")


class SelectionComposer(LabelComposer):
    def __init__(self, op=None):
        super().__init__(op=op)
        self.dtype = DtypeComposer()
        self.levels = LeveledComposer()


C = SelectionComposer()
