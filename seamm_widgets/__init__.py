# -*- coding: utf-8 -*-

"""
seamm_widgets
Custom Tk widgets for SEAMM.
"""

# Bring up the classes so that they appear to be directly in
# the seamm_widgets package.

from seamm_widgets.mousewheel_support import MousewheelSupport  # noqa: F401
from seamm_widgets.labeled_widget import LabeledWidget, align_labels  # noqa: F401, E501
from seamm_widgets.scrolled_frame import ScrolledFrame  # noqa: F401
from seamm_widgets.scrolled_labelframe import ScrolledLabelFrame  # noqa: F401
from seamm_widgets.scrolled_columns import ScrolledColumns  # noqa: F401
from seamm_widgets.keywords import Keywords  # noqa: F401
from seamm_widgets.property_table import PropertyTable  # noqa: F401
from seamm_widgets.labeled_entry import LabeledEntry  # noqa: F401
from seamm_widgets.labeled_combobox import LabeledCombobox  # noqa: F401
from seamm_widgets.periodic_table import PeriodicTable  # noqa: F401
from seamm_widgets.unit_entry import UnitEntry  # noqa: F401
from seamm_widgets.unit_combobox import UnitCombobox  # noqa: F401
from seamm_widgets.search_criteria import Criterion  # noqa: F401
from seamm_widgets.search_criteria import SearchCriteria  # noqa: F401
from seamm_widgets.check_tree import CheckTree  # noqa: F401
from .html_widgets import HTMLScrolledText, HTMLText, HTMLLabel  # noqa: F401

# Handle versioneer
from ._version import get_versions

__author__ = """Paul Saxe"""
__email__ = "psaxe@molssi.org"
versions = get_versions()
__version__ = versions["version"]
__git_revision__ = versions["full-revisionid"]
del get_versions, versions
