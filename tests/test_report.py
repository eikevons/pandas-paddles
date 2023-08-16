import pytest

import pandas as pd
from pandas_paddles import DF

from pandas_paddles.pipe import report


@pytest.fixture
def df():
    return pd.DataFrame({
        'x': ['a', 'b', 'b'],
        'y': range(3),
    })



@pytest.mark.parametrize(
    'arg', [report, report()]
)
def test_basic(arg, df, capsys):
    df2 = df.pipe(arg)
    captured = capsys.readouterr()
    assert captured.out == '(3, 2)\n'
    assert df2 is df

@pytest.mark.parametrize(
    'args',
    [
        (report('Label'),),
        (report, 'Label'),
    ]
)
def test_with_label(args, df, capsys):
    df2 = df.pipe(*args)
    captured = capsys.readouterr()
    assert captured.out == 'Label (3, 2)\n'
    assert df2 is df

@pytest.mark.parametrize(
    ['args', 'kwargs'],
    [
        (
            (report('Label', sep=" # "),),
            dict(),
        ),
        (
            (report, 'Label'),
            dict(sep=" # "),
        ),
    ]
)
def test_with_label_kwargs(args, kwargs, df, capsys):
    df2 = df.pipe(*args, **kwargs)
    captured = capsys.readouterr()
    assert captured.out == 'Label # (3, 2)\n'
    assert df2 is df

@pytest.mark.parametrize(
    ['args', 'kwargs'],
    [
        (
            (report(end=' #'), ), 
            dict(),
        ),
        (
            (report,),
            dict(end=" #"),
        ),
    ]
)
def test_with_kwargs(args, kwargs, df, capsys):
    df2 = df.pipe(*args, **kwargs)
    captured = capsys.readouterr()
    assert captured.out == '(3, 2) #'
    assert df2 is df

def test_with_custom_print_func_called(df):
    out = {}
    def custom_fn(*args, out=None):
        out['buf'] = " ".join(
            str(a) for a in args
            )

    df2 = df.pipe(report(print_func=custom_fn, out=out))
    assert out == {"buf":  "(3, 2)"}
    assert df2 is df

def test_with_custom_print_func_pipe_args(df):
    out = {}
    def custom_fn(*args, out=None):
        out['buf'] = " ".join(
            str(a) for a in args
            )

    df2 = df.pipe(report, print_func=custom_fn, out=out)
    assert out == {"buf":  "(3, 2)"}
    assert df2 is df
