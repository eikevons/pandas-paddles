from typing import List, TypeAlias, Union

AnyDataframe: TypeAlias = Union["pandas.DataFrame", "dask.dataframe.DataFrame"]
Indices: TypeAlias = List[int]
