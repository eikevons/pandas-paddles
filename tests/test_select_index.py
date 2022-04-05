import pickle
import pandas as pd
import pytest

from pandas_paddles import I
from pandas_paddles.axis import OpComposerBase


def rows(df: pd.DataFrame, idx_sel: OpComposerBase) -> list:
    return df.loc[idx_sel].index.to_list()


@pytest.fixture
def simple_df():
    return pd.DataFrame(
        {
            "a": range(4),
        },
        index=["x", "y", "z", "u"],
    )


@pytest.fixture
def mi_df():
    return pd.DataFrame(
        index=pd.MultiIndex.from_product(
            [list("abc"), list("XYZ")],
            names=["one", "two"],
        )
    )


def test_basic(simple_df):
    idx_sel = I["y", "z", "x"]
    assert rows(simple_df, idx_sel) == ["y", "z", "x"]


def test_combine(simple_df):
    idx_sel = I["y"] | I["z"] | I["x"]
    assert rows(simple_df, idx_sel) == ["y", "z", "x"]


def test_ellipsis(simple_df):
    idx_sel = I["y"] | ...
    assert rows(simple_df, idx_sel) == ["y", "x", "z", "u"]


def test_startswith(simple_df):
    idx_sel = I.startswith("x")
    assert rows(simple_df, idx_sel) == ["x"]


def test_endswith(simple_df):
    idx_sel = I.endswith("x")
    assert rows(simple_df, idx_sel) == ["x"]


def test_level0_subset(mi_df):
    expected = [
        ("c", "X"),
        ("c", "Y"),
        ("c", "Z"),
        ("a", "X"),
        ("a", "Y"),
        ("a", "Z"),
    ]

    idx_sel = I.levels[0]["c", "a"]
    assert rows(mi_df, idx_sel) == expected

    idx_sel = I.levels["one"]["c", "a"]
    assert rows(mi_df, idx_sel) == expected


def test_level0_str_methods(mi_df):
    expected = [
        ("c", "X"),
        ("c", "Y"),
        ("c", "Z"),
    ]

    idx_sel = I.levels[0].startswith("c")
    assert rows(mi_df, idx_sel) == expected

    idx_sel = I.levels[0].endswith("c")
    assert rows(mi_df, idx_sel) == expected

    idx_sel = I.levels[0].contains("c")
    assert rows(mi_df, idx_sel) == expected

    idx_sel = I.levels[0].match("c")
    assert rows(mi_df, idx_sel) == expected


def test_level0_composition(mi_df):
    idx_sel = I.levels[0]['c'] | ...
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
    assert rows(mi_df, idx_sel) == expected


def test_combine_complex(mi_df):
    # Move (c, [X, Y]) to the left
    idx_sel =  (I.levels[0]['c'] & I.levels[1]["X", "Y"]) | ...
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
    assert rows(mi_df, idx_sel) == expected

    # Select (b, [Y, X, Z]) to the left
    idx_sel = (I.levels[0]["b"] & (I.levels[1]["Y"] | ...)) | ...
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
    assert rows(mi_df, idx_sel) == expected

    # Select (b, [Y]) + (c, *)
    idx_sel = (I.levels[0]["b"] & I.levels[1]["Y"]) | I.levels[0]["c"]
    expected = [
        ("b", "Y"),
        ("c", "X"),
        ("c", "Y"),
        ("c", "Z"),
    ]
    assert rows(mi_df, idx_sel) == expected

    # Select (b, Y)
    idx_sel = I.levels[0]["b"] & I.levels[1]["Y"]
    expected = [
        ("b", "Y"),
    ]
    assert rows(mi_df, idx_sel) == expected


def test_inversion_basic(simple_df):
    idx_sel = ~I["y"]
    assert rows(simple_df, idx_sel) == ["x", "z", "u"]


def test_inversion_complex(mi_df):
    # Exclude (b, [Y]) + (c, *)
    idx_sel = ~((I.levels[0]["b"] & I.levels[1]["Y"]) | I.levels[0]["c"])
    expected = [
        ("a", "X"),
        ("a", "Y"),
        ("a", "Z"),
        ("b", "X"),
        ("b", "Z"),
    ]
    assert rows(mi_df, idx_sel) == expected


def test_inversion_composition(mi_df):
    # Select (*, ~[Y, Z])
    sel_1 = ... & ~I.levels[1]["Y", "Z"]
    expected_1 = [
        ("a", "X"),
        ("b", "X"),
        ("c", "X"),
    ]
    assert rows(mi_df, sel_1) == expected_1

    # Select (b, *)
    sel_2 = I.levels[0]["b"]
    expected_2 = [
        ("b", "X"),
        ("b", "Y"),
        ("b", "Z"),
    ]
    assert rows(mi_df, sel_2) == expected_2

    # Select (b, *) + (*, ~[Y, Z])
    sel_composed = sel_2 | sel_1
    expected_composed = [
        ("b", "X"),
        ("b", "Y"),
        ("b", "Z"),
        ("a", "X"),
        ("c", "X"),
    ]

    test = rows(mi_df, sel_composed)
    print(test)
    print(expected_composed)
    assert test == expected_composed


@pytest.mark.parametrize(
    "sel",
    [
        I["y", "z", "x"],
        I.startswith("x"),
        ... & ~I.levels[1]["Y", "Z"],
    ],
)
def test_serializable(sel):
    buf = pickle.dumps(sel)
    pickle.loads(buf)
