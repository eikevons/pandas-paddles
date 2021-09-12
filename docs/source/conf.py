# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from subprocess import getstatusoutput
from warnings import warn

sys.path.insert(0, os.path.abspath("../.."))


# -- Project information -----------------------------------------------------

project = "Pandas Selector"
author = "Eike von Seggern"
copyright = f"2021, {author}"

# The short X.Y version
import pandas_selector

version = pandas_selector.__version__

# The full version, including alpha/beta/rc tags
release = version

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.viewcode",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    # numpydoc does not support autodoc.typehins so far
    # https://github.com/numpy/numpydoc/issues/196
    # So we use napoleon instead
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    # "numpydoc",
]


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
#html_static_path = ["_static"]

# -- Extension configuration -------------------------------------------------
autosummary_generate = True
autodoc_typehints = "description"

intersphinx_mapping = {
    "pandas": ("https://pandas.pydata.org/pandas-docs/dev", None),
}

# Configuration for pydata sphinx theme

# https://pydata-sphinx-theme.readthedocs.io/en/latest/user_guide/configuring.html#adding-ethical-advertisements-to-your-sidebar-in-readthedocs
html_sidebars = {
    "**": ["search-field.html", "sidebar-nav-bs.html", "sidebar-ethical-ads.html"]
}

html_theme_options = {
    "footer_items": ["footer-version", "copyright", "sphinx-version"],
}

# Allow Jinja templating in source rst files.
# Adapted from https://www.ericholscher.com/blog/2016/jul/25/integrating-jinja-rst-sphinx/
def rstjinja(app, docname, source):
    """
    Render our pages as a jinja template for fancy templating goodness.
    """
    # Make sure we're outputting HTML
    if app.builder.format != 'html':
        return
    src = source[0]
    rendered = app.builder.templates.render_string(
        src, app.config.html_context
    )
    source[0] = rendered

html_context = {
    'project': project,
    'version': version,
}

def setup(app):
    app.connect("source-read", rstjinja)

ret, out = getstatusoutput('git rev-parse --short HEAD')
if ret == 0:
    githash = out
    html_context['githash'] = githash
else:
    warn(f'git rev-parse returned {ret}: {out}')
