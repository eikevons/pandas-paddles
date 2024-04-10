Welcome to Pandas Paddles's documentation!
==========================================

.. toctree::

{% if githash is defined %}
{{project}} documentation for version ``{{version}}`` (`{{githash}} <https://github.com/eikevons/pandas-paddles/commit/{{githash}}>`_).
{% else %}
{{project}} documentation for version ``{{version}}``.
{% endif %}

Install with ``pip install pandas-paddles``. Source code available at
`GitHub <https://github.com/eikevons/pandas-paddles>`_.

.. automodule:: pandas_paddles

.. 
   NOTE: List all sub-packages as
   `pandas_paddles.SUBPACKAGE` in the autosummary block
   below.

API
---

.. autosummary::
   :toctree: api
   :recursive:
   :template: custom-module-template.rst

   pandas_paddles.contexts
   pandas_paddles.closures
   pandas_paddles.axis
   pandas_paddles.pipe
   pandas_paddles.paddles


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
