import pickle
import string

import pandas as pd
import pytest

from pandas_paddles import C
from pandas_paddles.axis import OpComposerBase


def cols(df: pd.DataFrame, col_sel: OpComposerBase) -> list:
    """Get list of column names after applying column selection."""
    return df.loc[:, col_sel].columns.to_list()


@pytest.fixture
def simple_df():
    return pd.DataFrame(
        {
            "x": range(5),
            "y": range(5),
            "z": list("abcde"),
            "u": 1.0,
        }
    )


@pytest.fixture
def mi_df():
    return pd.DataFrame(
        columns=pd.MultiIndex.from_product(
            [list("abc"), list("XYZ")],
            names=["one", "two"],
        )
    )


def test_basic(simple_df):
    col_sel = C["y", "z", "x"]
    assert cols(simple_df, col_sel) == ["y", "z", "x"]


def test_basic_slice(simple_df):
    col_sel = C["y":"u"]
    assert cols(simple_df, col_sel) == ["y", "z", "u"]


def test_invert_slice(simple_df):
    col_sel = ~C["y":"z"]
    assert cols(simple_df, col_sel) == ["x", "u"]

    col_sel = C[:"y"]
    assert cols(simple_df, col_sel) == ["x", "y"]

    col_sel = C["z":]
    assert cols(simple_df, col_sel) == ["z", "u"]


def test_combine(simple_df):
    col_sel = C["y"] | C["z"] | C["x"]
    assert cols(simple_df, col_sel) == ["y", "z", "x"]


def test_combine_slice():
    df = pd.DataFrame(columns=list(string.ascii_lowercase))
    col_sel = C["g":"i"] | C["b":"d"]
    assert cols(df, col_sel) == ["g", "h", "i", "b", "c", "d"]


def test_ellipsis(simple_df):
    col_sel = C["y"] | ...
    assert cols(simple_df, col_sel) == ["y", "x", "z", "u"]


def test_startswith(simple_df):
    col_sel = C.startswith("x")
    assert cols(simple_df, col_sel) == ["x"]


def test_endswith(simple_df):
    col_sel = C.endswith("x")
    assert cols(simple_df, col_sel) == ["x"]


def test_str_dtype(simple_df):
    col_sel = C.dtype == str
    assert cols(simple_df, col_sel) == ["z"]


def test_int_dtype(simple_df):
    col_sel = C.dtype == int
    assert cols(simple_df, col_sel) == ["x", "y"]


def test_dtype_isin(simple_df):
    col_sel = C.dtype.isin((str, float))
    assert cols(simple_df, col_sel) == ["z", "u"]


def test_level0_subset(mi_df):
    expected = [
        ("c", "X"),
        ("c", "Y"),
        ("c", "Z"),
        ("a", "X"),
        ("a", "Y"),
        ("a", "Z"),
    ]

    col_sel = C.levels[0]["c", "a"]
    assert cols(mi_df, col_sel) == expected

    col_sel = C.levels["one"]["c", "a"]
    assert cols(mi_df, col_sel) == expected


def test_level0_str_methods(mi_df):
    expected = [
        ("c", "X"),
        ("c", "Y"),
        ("c", "Z"),
    ]

    col_sel = C.levels[0].startswith("c")
    assert cols(mi_df, col_sel) == expected

    col_sel = C.levels[0].endswith("c")
    assert cols(mi_df, col_sel) == expected

    col_sel = C.levels[0].contains("c")
    assert cols(mi_df, col_sel) == expected

    col_sel = C.levels[0].match("c")
    assert cols(mi_df, col_sel) == expected


def test_level0_composition(mi_df):
    col_sel = C.levels[0]['c'] | ...
    expected = [
        ("c", "X"),
        ("c", "Y"),
        ("c", "Z"),
        ("a", "X"),
        ("a", "Y"),
        ("a", "Z"),
        ("b", "X"),
        ("b", "Y"),
        ("b", "Z"),
    ]
    assert cols(mi_df, col_sel) == expected


def test_level0_slice(mi_df):
    print(mi_df.columns)
    expected = [
        ("a", "X"),
        ("a", "Y"),
        ("a", "Z"),
        ("b", "X"),
        ("b", "Y"),
        ("b", "Z"),
    ]

    col_sel = C.levels[0]["a":"b"]
    assert cols(mi_df, col_sel) == expected

    col_sel = C.levels["one"]["a":"b"]
    assert cols(mi_df, col_sel) == expected


def test_combine_complex(mi_df):
    # Move (c, [X, Y]) to the left
    col_sel =  (C.levels[0]['c'] & C.levels[1]["X", "Y"]) | ...
    expected = [
        ("c", "X"),
        ("c", "Y"),
        ("a", "X"),
        ("a", "Y"),
        ("a", "Z"),
        ("b", "X"),
        ("b", "Y"),
        ("b", "Z"),
        ("c", "Z"),
    ]
    assert cols(mi_df, col_sel) == expected

    # Select (b, [Y, X, Z]) to the left
    col_sel = (C.levels[0]["b"] & (C.levels[1]["Y"] | ...)) | ...
    expected = [
        ("b", "Y"),
        ("b", "X"),
        ("b", "Z"),
        ("a", "X"),
        ("a", "Y"),
        ("a", "Z"),
        ("c", "X"),
        ("c", "Y"),
        ("c", "Z"),
    ]
    assert cols(mi_df, col_sel) == expected

    # Select (b, [Y]) + (c, *)
    col_sel = (C.levels[0]["b"] & C.levels[1]["Y"]) | C.levels[0]["c"]
    expected = [
        ("b", "Y"),
        ("c", "X"),
        ("c", "Y"),
        ("c", "Z"),
    ]
    assert cols(mi_df, col_sel) == expected


def test_inversion_basic(simple_df):
    col_sel = ~C["y"]
    assert cols(simple_df, col_sel) == ["x", "z", "u"]


def test_inversion_complex(mi_df):
    # Exclude (b, [Y]) + (c, *)
    col_sel = ~((C.levels[0]["b"] & C.levels[1]["Y"]) | C.levels[0]["c"])
    expected = [
        ("a", "X"),
        ("a", "Y"),
        ("a", "Z"),
        ("b", "X"),
        ("b", "Z"),
    ]
    assert cols(mi_df, col_sel) == expected


def test_inversion_composition(mi_df):
    # Select (*, ~[Y, Z])
    sel_1 = ... & ~C.levels[1]["Y", "Z"]
    expected_1 = [
        ("a", "X"),
        ("b", "X"),
        ("c", "X"),
    ]
    assert cols(mi_df, sel_1) == expected_1

    # Select (b, *)
    sel_2 = C.levels[0]["b"]
    expected_2 = [
        ("b", "X"),
        ("b", "Y"),
        ("b", "Z"),
    ]
    assert cols(mi_df, sel_2) == expected_2

    # Select (b, *) + (*, ~[Y, Z])
    sel_composed = sel_2 | sel_1
    expected_composed = [
        ("b", "X"),
        ("b", "Y"),
        ("b", "Z"),
        ("a", "X"),
        ("c", "X"),
    ]

    test = cols(mi_df, sel_composed)
    assert test == expected_composed


@pytest.mark.parametrize(
    "sel",
    [
        C["y", "z", "x"],
        C.dtype.isin((str, float)),
        ... & ~C.levels[1]["Y", "Z"],
    ],
)
def test_serializable(sel):
    buf = pickle.dumps(sel)
    pickle.loads(buf)
