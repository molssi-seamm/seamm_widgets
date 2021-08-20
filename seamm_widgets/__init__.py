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

# Handle versioneer
from ._version import get_versions

__author__ = """Paul Saxe"""
__email__ = "psaxe@molssi.org"
versions = get_versions()
__version__ = versions["version"]
__git_revision__ = versions["full-revisionid"]
del get_versions, versions

default_units = {
    "dimensionless": ["degree"],
    "[length]": ["Å", "pm", "nm", "um"],
    "[length] ** 2": ["Å**2", "pm**2", "nm**2", "um**2"],
    "[length] ** 3": ["Å**3", "pm**3", "nm**3", "um**3"],
    "[mass]": ["g", "kg", "tonne", "lb", "ton"],
    "[substance]": ["mol"],
    "[temperature]": ["K", "degC", "degF", "degR"],
    "[mass] / [length] ** 3": ["g/mL", "kg/L", "kg/m**3", "g/mol/Å**3"],  # nopep8
    "[time]": ["fs", "ps", "ns", "us", "ms", "s"],
    "[length] ** 2 * [mass] / [substance] / [time] ** 2": [
        "kcal/mol",
        "kJ/mol",
    ],  # nopep8
    "[length] * [mass] / [substance] / [time] ** 2": [
        "kcal/mol/Å",
        "kJ/mol/Å",
        "eV/Å",
    ],  # nopep8
    "[length] * [mass] / [time] ** 2": ["kcal/mol/Å", "kJ/mol/Å", "eV/Å"],  # nopep8
    "[length] / [time] ** 2": ["m/s**2", "ft/s**2", "Å/fs**2"],
    "[mass] / [length] / [time] ** 2": ["Pa", "atm", "bar", "psi", "ksi"],
}
