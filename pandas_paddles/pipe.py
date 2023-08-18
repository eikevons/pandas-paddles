"""Helpers for working with :meth:`pandas.DataFrame.pipe()`."""
import pandas as pd

from .contexts import DataframeContext

# Here to prevent recursive import from __init__.py
# r
DF = DataframeContext()

def _generate_report(args, print_func, print_kwargs):
    def inner_report(df):
        to_print = []
        for a in args:
            if callable(a):
                to_print.append(a(df))
            else:
                to_print.append(a)
        print_func(*to_print, **print_kwargs)
        return df
    return inner_report



def report(*args, print_func=print, **print_kwargs):
    r"""Print summary report for a data frame.

    This function is intended to be used in ``DataFrame.pipe()``. It can be
    used either by calling with the needed arguments ("call" semantics),
    e.g.,::

        df.pipe(report("Label"))

    or by passing the arguments via ``pipe`` ("no-call" semantics), e.g.,::

        df.pipe(report, "Label")

    See *Returns* below.

    Examples
    --------
    Report the shape::

        df = pd.DataFrame({
            "x": range(3),
            "y": ["a", "b", "a"],
        })
        df.pipe(report())
        # or
        df.pipe(report)
        # Output:
        # (3, 2)

    Report the shape prefixed with a label::

        df.pipe(report("Label"))
        # or
        df.pipe(report, "Label")
        # Output:
        # Label (3, 2)

    Combine with ``DF``::

        df.pipe(report("The shape:", DF.shape, "and unique y-values:", DF["y"].nunique()))
        # or
        df.pipe(report, "The shape:", DF.shape, "and unique y-values:", DF["y"].nunique())
        # Output:
        # The shape: (3, 2) and unique y-values: 2

    Pass arguments to ``print()``::

        df.pipe(report("Label", sep="\n"))
        # or
        df.pipe(report, "Label", sep="\n")
        # Output:
        # Label
        # (3, 2)

    Parameters
    ----------
    args : str, callable
        Things to be printed. Can be either ``str`` or callables taking a
        data frame as single argument, e.g. created with ``DF``.

        The first argument can be a ``~pandas.DataFrame``.
    print_func : callable
        The function used to print the "report". Defaults to :func:`print`.
    print_kwargs
        All keyword arguments are passed through to ``print_func``.

    Returns
    -------
    callable, pandas.DataFrame
        If the first argument is a ``~pandas.DataFrame``, the report is
        generated and this data frame is returned. This is the "no-call"
        semantics above (``df.pipe(report, "Label")``).

        Otherwise, a function is returned that takes a single
        ``~pandas.DataFrame`` argument that generates the report and
        returned the passed data frame. This is the "call" semantics above
        (``df.pipe(report("Label"))``.
    """
    df = None
    args = list(args)
    if args and isinstance(args[0], pd.DataFrame):
        df = args.pop(0)

    if len(args) == 0:
        args = [DF.shape]
    elif len(args) == 1 and isinstance(args[0], str):
        args.append(DF.shape)

    inner_report = _generate_report(args, print_func, print_kwargs)
    if df is None:
        return inner_report
    return inner_report(df)
