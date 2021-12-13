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
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import os
import sys
import toml
import re

sys.path.insert(0, os.path.abspath("../tisane"))

dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# -- Project information -----------------------------------------------------

with open(os.path.join(dir, "pyproject.toml"), "r") as f:
    pyproject = toml.loads(f.read())
    pass

project = "tisane"


authorNameRegex = r"(\w+(?: \w+)*)\s*<[^>]*>"

authors = pyproject["tool"]["poetry"]["authors"]

authors = [re.sub(authorNameRegex, r"\1", author) for author in authors]

author = " & ".join(authors)
copyright = "2021, {}".format(author)

# The full version, including alpha/beta/rc tags

# print(pyproject)

release = pyproject["tool"]["poetry"]["version"]


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "numpydoc",
]

autoapi_type = "python"
autoapi_dirs = [os.path.abspath("../tisane")]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "autodoc"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


autodoc_default_options = {
    "members": None,
    "member-order": "alphabetical",
}


autoapi_options = ["members", "show-inheritance"]

autoapi_member_order = "groupwise"
autodoc_typehints = "description"
