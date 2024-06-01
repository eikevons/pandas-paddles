# Unreleased (YYYY-MM-DD)

- Add support for dask dataframes

# 1.5.0 (2024-04-17)

- Move `C` and `I` to stable API: drop warning that they are experimental
- Make string representation of `C` and `I` even prettier, e.g.,
  `~C['a':'d'] & C.dtype.isin({int, float})` renders exactly the same.
- Add helper functions in `paddles` submodule: `str_join`, `build_filter`,
  `combine`.

# 1.4.2 (2023-09-01)

- Add reverse binary operators, e.g. `__radd__`.

# 1.4.1 (2023-08-25)

- Fix using `S` in `groupby().agg()`
  ([GH-21](https://github.com/eikevons/pandas-paddles/issues/21))

# 1.4.0 (2023-08-16)

- Add `report` function.
- Add prettier string representations for `C` and `I` expressions.

# 1.3.4 (2023-04-07)

- Don't warn when creating `C` and `I` instances.

# 1.3.3 (2023-04-05)

- Refactor code: Give DF and S supporting classes better names.
- Allow selecting slices of labels, e.g., `C["C":"G"]`.
- Support `pandas` version 2.


# 1.3.2 (2022-03-21)

- Add `I` for label-selection for index similar as `C` for columns. (Still
  experimental)

# 1.3.1 (2022-02-21)

- Fix build of stub package (`pandas_selector`).

# 1.3.0 (2022-02-21)

- Rename package to `pandas_paddles`.
- Drop Python 3.6 from actively supported releases.
- Add Python 3.10 to test matrix.

# 1.2.2 (2022-02-19)

- Add experimental warning when using `C`.

# 1.2.1 (2022-02-19)

- Add experimental `C` object to simplify column selection and sorting.

# 1.1.0 (2021-09-12)

- Add typing hints.
- Raise test-coverage.

# 1.0.0 (2021-09-03)

- Expand `DF` in wrapped function arguments.
- Update Sphinx.
- Fix serialization of `DF` and `S` with `pickle`.

# 0.1.2 (2021-08-22)

- Add series accessor (#3)
- Improve doc handling by passing through original pandas documentation for
  wrapped objects.

# 0.1.1 (2021-04-13)

- Host documentation on RTD.
- Add project metadata.

# 0.1.0 (2021-04-12)

- Initial release.
- Add GitHub actions CI pipeline.
- Add test coverage report.
- Inital set of test cases.
