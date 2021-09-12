Welcome to Pandas Selector's documentation!
===========================================

.. toctree::

{% if githash is defined %}
{{project}} documentation for version ``{{version}}`` (`{{githash}} <https://github.com/eikevons/pandas-selector/commit/{{githash}}>`_).
{% else %}
{{project}} documentation for version ``{{version}}``.
{% endif %}

.. automodule:: pandas_selector

.. 
   NOTE: List all sub-packages as
   `pandas_selector.SUBPACKAGE` in the autosummary block
   below.

API
---

.. autosummary::
   :toctree: api
   :recursive:
   :template: custom-module-template.rst

   pandas_selector.df_accessor


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
