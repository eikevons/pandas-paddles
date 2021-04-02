"""\
Pandas Accessors

Simple column selector for ``loc[]``, ``iloc[]``, ``assign()`` and others.

Authors:

* Eike von Seggern <eike@vonseggern.space>
"""
__version__ = "0.1.0-dev"
__all__ = ["DF"]

from .accessor import DataframeAccessor

DF = DataframeAccessor()
