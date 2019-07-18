# -*- coding: utf-8 -*-

"""Top-level package for SEAMM Widgets."""

__author__ = """Paul Saxe"""
__email__ = 'psaxe@vt.edu'
__version__ = '0.2.0'

# Unit handling! This needs to be bofre other import which use e.g. ureg.
import pint

ureg = pint.UnitRegistry(auto_reduce_dimensions=True)

# Add our conversions for chemistry
_d = pint.Context('chemistry')
_d.add_transformation('[mass]/[substance]', '[mass]',
                      lambda units, x: x / units.avogadro_number)
ureg.add_context(_d)
ureg.enable_contexts('chemistry')
pint.set_application_registry(ureg)

Q_ = ureg.Quantity
units_class = ureg('1 km').__class__

# Bring up the classes so that they appear to be directly in
# the seamm_widgets package.

from seamm_widgets.mousewheel_support import MousewheelSupport  # nopep8
from seamm_widgets.scrolled_frame import ScrolledFrame  # nopep8
from seamm_widgets.scrolled_columns import ScrolledColumns  # nopep8
from seamm_widgets.labeled_widget import LabeledWidget, align_labels  # nopep8
from seamm_widgets.labeled_entry import LabeledEntry  # nopep8
from seamm_widgets.labeled_combobox import LabeledCombobox  # nopep8
from seamm_widgets.unit_entry import UnitEntry  # nopep8
from seamm_widgets.unit_combobox import UnitCombobox  # nopep8


default_units = {
    '[length]': ['Å', 'pm', 'nm', 'um'],
    '[length] ** 3': ['Å**3', 'pm**3', 'nm**3', 'um**3'],
    '[mass]': ['g', 'kg', 'tonne', 'lb', 'ton'],
    '[substance]': ['mol'],
    '[temperature]': ['K', 'degC', 'degF', 'degR'],
    '[mass] / [length] ** 3': ['g/mL', 'kg/L', 'kg/m**3', 'g/mol/Å**3'],  # nopep8
    '[time]': ['fs', 'ps', 'ns', 'us', 'ms', 's'],
    '[length] ** 2 * [mass] / [substance] / [time] ** 2': ['kcal/mol', 'kJ/mol'],  # nopep8
    '[length] * [mass] / [substance] / [time] ** 2': ['kcal/mol/Å', 'kJ/mol/Å', 'eV/Å'],  # nopep8
    '[length] * [mass] / [time] ** 2': ['kcal/mol/Å', 'kJ/mol/Å', 'eV/Å'],  # nopep8
    '[length] / [time] ** 2': ['m/s**2', 'ft/s**2', 'Å/fs**2'],
    '[mass] / [length] / [time] ** 2': ['Pa', 'atm', 'bar', 'psi', 'ksi'],
}
