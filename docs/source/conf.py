import os
import sys
import django
from django.conf import settings

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
    ),
)

# Minimal Django configuration so that autodoc works with models.
if not settings.configured:
    settings.configure(
        **{"INSTALLED_APPS": ["chard"], "LOGGING_CONFIG": None}, DEBUG=True
    )
django.setup()

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Chard"
copyright = "Takota Limited"
author = "Takota Limited"
release = "0.2"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinx.ext.autosummary"]
templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
