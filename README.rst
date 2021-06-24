Pandas Selector
===============

Simple, composable selectors for ``loc[]``, ``iloc[]``, ``assign()`` and others.

.. image:: https://readthedocs.org/projects/pandas-selector/badge/?version=latest
  :target: https://pandas-selector.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status
.. image:: https://github.com/eikevons/pandas-selector/actions/workflows/check.yml/badge.svg
  :target: https://github.com/eikevons/pandas-selector/actions/workflows/check.yml
  :alt: Test Status

Overview
--------

- **Motivation**: Make chaining Pandas operations easier and bring
  functionality to Pandas similar to Spark's `col()
  <https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.sql.functions.col.html#pyspark.sql.functions.col>`_
  function or referencing columns in R's `dplyr
  <https://dplyr.tidyverse.org/articles/dplyr.html>`_.
- **Install** from PyPI with ``pip install
  pandas-selector``. Pandas versions 1.0+ (``^1.0``) are supported.
- **Documentation** can be found at `readthedocs
  <https://pandas-selector.readthedocs.io/en/latest/>`_.
- **Source code** can be obtained from `GitHub <https://github.com/eikevons/pandas-selector>`_.

Example: Create new column and filter
-------------------------------------

Instead of writing "traditional" Pandas like this:

.. code-block:: python

    df_in = pd.DataFrame({"x": range(5)})
    df = df_in.assign(y = df_in.x // 2)
    df = df.loc[df.y <= 1]
    df
    #    x  y
    # 0  0  0
    # 1  1  0
    # 2  2  1
    # 3  3  1

One can write:

.. code-block:: python

    from pandas_selector import DF
    df = (df_in
          .assign(y = DF.x // 2)
          .loc[DF.y <= 1]
         )

This is especially handy when re-iterating on data frame manipulations
interactively, e.g. in a notebook.

But you can access all methods and attributes of the data frame from the
context:

.. code-block:: python

    df = pd.DataFrame({
        "X": range(5),
        "Y": ["1", "a", "c", "D", "e"],
    })
    df.loc[DF.y.str.isupper() | DF.y.str.isnumeric()]
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
