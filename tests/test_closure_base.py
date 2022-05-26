import pytest

from pandas_paddles.closures import ClosureBase


def test_closure_base_cannot_be_called():
    inst = ClosureBase('foo')
    with pytest.raises(NotImplementedError):
        inst(object(), object())
