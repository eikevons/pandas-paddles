import pytest

from pandas_paddles.df_accessor import WrapperBase


def test_wrapper_base_cannot_be_called():
    wb = WrapperBase('foo')
    with pytest.raises(NotImplementedError):
        wb(object(), object())
