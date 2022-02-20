Pandas Paddles
==============

Access the calling ``pandas`` data frame in ``loc[]``, ``iloc[]``,
``assign()`` and other methods with ``DF`` to write better chains of
data frame operations, e.g.:

.. code-block:: python

    df = (df
          # Select all rows with column "x" < 2
          .loc[DF["x"] < 2]
          .assign(
              # Shift "x" by its minimum.
              y = DF["x"] - DF["x"].min(),
              # Clip "x" to it's central 50% window. Note how DF is used
              # in the argument to `clip()`.
              z = DF["x"].clip(
                  lower=DF["x"].quantile(0.25),
                  upper=DF["x"].quantile(0.75)
              ),
          )
         )

.. image:: https://readthedocs.org/projects/pandas-paddles/badge/?version=latest
  :target: https://pandas-paddles.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status
.. image:: https://github.com/eikevons/pandas-paddles/actions/workflows/check.yml/badge.svg
  :target: https://github.com/eikevons/pandas-paddles/actions/workflows/check.yml
  :alt: Test Status
.. image:: https://img.shields.io/pypi/v/pandas-paddles
   :target: https://pypi.org/project/pandas-paddles/
   :alt: Latest version
.. image:: https://img.shields.io/pypi/pyversions/pandas-paddles
   :target: https://pypi.org/project/pandas-paddles/
   :alt: Supported Python versions
.. image:: https://img.shields.io/pypi/dm/pandas-paddles
   :target: https://pypi.org/project/pandas-paddles/
   :alt: PyPI downloads

Overview
--------

- **Motivation**: Make chaining Pandas operations easier and bring
  functionality to Pandas similar to Spark's `col()
  <https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.sql.functions.col.html#pyspark.sql.functions.col>`_
  function or referencing columns in R's `dplyr
  <https://dplyr.tidyverse.org/articles/dplyr.html>`_.
- **Install** from PyPI with ``pip install
  pandas-paddles``. Pandas versions 1.0+ (``^1.0``) are supported.
- **Documentation** can be found at `readthedocs
  <https://pandas-paddles.readthedocs.io/en/latest/>`_.
- **Source code** can be obtained from `GitHub <https://github.com/eikevons/pandas-paddles>`_.
- `Changelog <Changelog.md>`_

Example: Create new column and filter
-------------------------------------

Instead of writing "traditional" Pandas like this:

.. code-block:: python

    df_in = pd.DataFrame({"x": range(5)})
    df = df_in.assign(y = df_in["x"] // 2)
    df = df.loc[df["y"] <= 1]
    df
    #    x  y
    # 0  0  0
    # 1  1  0
    # 2  2  1
    # 3  3  1

One can write:

.. code-block:: python

    from pandas_paddles import DF
    df = (df_in
          .assign(y = DF["x"] // 2)
          .loc[DF["y"] <= 1]
         )

This is especially handy when re-iterating on data frame manipulations
interactively, e.g. in a notebook (just imagine you have to rename
``df`` to ``df_out``).

But you can access all methods and attributes of the data frame from the
context:

.. code-block:: python

    df = pd.DataFrame({
        "X": range(5),
        "y": ["1", "a", "c", "D", "e"],
    })
    df.loc[DF["y"]str.isupper() | DF["y"]str.isnumeric()]
    #    X  y
    # 0  0  1
    # 3  3  D
    df.loc[:, DF.columns.str.isupper()]
    #    X
    # 0  0
    # 1  1
    # 2  2
    # 3  3
    # 4  4

You can even use ``DF`` in the arguments to methods:

.. code-block:: python

    df = pd.DataFrame({
        "x": range(5),
        "y": range(2, 7),
    })
    df.assign(z = DF['x'].clip(lower=2.2, upper=DF['y'].median()))
    #    x  y    z
    # 0  0  2  2.2
    # 1  1  3  2.2
    # 2  2  4  2.2
    # 3  3  5  3.0
    # 4  4  6  4.0

When working with ``~pd.Series`` the ``S`` object exists. It can be used
similar to ``DF``:

.. code-block:: python

  s = pd.Series(range(5))
  s[s < 3]
  # 0    0
  # 1    1
  # 2    2
  # dtype: int64

Similar projects for pandas
===========================

* `siuba <https://github.com/machow/siuba>`_

  * (+) active
  * (-) new API to learn

* `pandas-ply <https://github.com/coursera/pandas-ply>`_

  * (-) stale(?), last change 6 years ago
  * (-) new API to learn
  * (-) ``Symbol`` / ``pandas_ply.X`` works only with ``ply_*`` functions

* `pandas-select <https://pandas-select.readthedocs.io/en/latest/reference/label_selection.html>`_

  * (+) no explicite ``df`` necessary
  * (-) new API to learn

* `pandas-selectable <https://github.com/jseabold/pandas-selectable>`_

  * (+) simple ``select`` accessor
  * (-) usage inside chains clumsy (needs explicite ``df``):

    .. code-block:: python

       ((df
         .select.A == 'a')
         .select.B == 'b'
       )

  * (-) hard-coded ``str``, ``dt`` accessor methods
  * (?) composable?

Development
===========

Development is containerized with [Docker](https://www.docker.com/) to
separte from host systems and improve reproducability. No other
prerequisites are needed on the host system.

**Recommendation for Windows users:** install `WSL 2
<https://docs.microsoft.com/en-us/windows/wsl/install-win10>`_ (tested
on Ubuntu 20.04), and for containerized workflows, `Docker
Desktop <https://www.docker.com/products/docker-desktop>`_ for Windows.

The **common tasks** are collected in ``Makefile`` (See ``make help`` for a
complete list):

- Run the unit tests: ``make test`` or ``make watch`` for continuously running
  tests on code-changes.
- Build the documentation: ``make docs``
- **TODO**: Update the ``poetry.lock`` file: ``make lock``
- Add a dependency:

  1. Start a shell in a new container.
  2. Add dependency with ``poetry add`` in the running container. This will update
     ``poetry.lock`` automatically::

        # 1. On the host system
        % make shell
        # 2. In the container instance:
        I have no name!@7d0e85b3a303:/app$ poetry add --dev --lock falcon

- Build the development image ``make devimage``
  (Note: This should be done automatically for the targets.) 
