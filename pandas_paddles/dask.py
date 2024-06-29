"""Pandas and dask contexts"""

from dask.dataframe import DataFrame
import pandas as pd

from .pandas import PandasDataframeContext, S


from .contexts import (
    add_dunder_operators,
    get_obj_attr_doc,
)

@add_dunder_operators
class DaskDataframeContext(PandasDataframeContext):
    wrapped_cls = (pd.DataFrame, DataFrame)

DF = DaskDataframeContext()
