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
        return print_func(*to_print, **print_kwargs)
    return inner_report



def report(*args, print_func=print, **print_kwargs):
    """Print summary report for a data frame.

    This function is intended to be used in ``DataFrame.pipe()``. It can be used either by calling with the needed arguments, e.g.,::

        df.pipe(report("Label"))

    or by passing the arguments via ``pipe``, e.g.,::

        df.pipe(report, "Label")

    Examples
    --------
    Report the shape
    >>> df.pipe(report())

    or

    >>> df.pipe(report)

    Report the shape prefixed with a label
    >>> df.pipe(report("Label"))

    Combine with ``DF``
    >>> df.pipe(report("The shape:", DF.shape, "and unique values in some columns", DF["column"].nunique()))

    Pass arguments to ``print()``

    >>> df.pipe(report, sep="\n")
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
