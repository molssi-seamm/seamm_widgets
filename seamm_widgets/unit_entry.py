# -*- coding: utf-8 -*-

"""Labeled entry widget with units.

The goal of these widgets is twofold: to make it easier for developers
to implement dialogs with compound widgets, and to naturally
standardize the user interface presented to the user.
"""

import logging
from seamm_util import Q_, units_class, default_units
import seamm_widgets as sw
import tkinter as tk
import tkinter.ttk as ttk

logger = logging.getLogger(__name__)

options = {
    "unitentry": {
        "as_quantity": "as_quantity",
    },
    "units": {
        "class_": "class_",
        "cursor": "cursor",
        "exportselection": "exportselection",
        "unitsheight": "height",
        "unitsjustify": "justify",
        "postcommand": "postcommand",
        "style": "style",
        "unitstakefocus": "takefocus",
        "variable": "textvariable",
        "unitsvalidate": "validate",
        "unitsvalidatecommand": "validatecommand",
        "unitswidth": "width",
        "unitsxscrollcommand": "xscrollcommand",
    },
}


class UnitEntry(sw.LabeledEntry):
    def __init__(self, parent, *args, **kwargs):
        """Initialize the instance"""
        self.as_quantity = kwargs.pop("as_quantity", False)

        myoptions = {
            "height": 7,
            "width": 10,
            "state": "readonly",
        }
        for option, myoption in options["units"].items():
            if option in kwargs:
                myoptions[myoption] = kwargs.pop(option)

        # Create our parent
        class_ = kwargs.pop("class_", "MUnitEntry")
        super().__init__(parent, class_=class_, *args, **kwargs)

        interior = self.interior

        # And put our widget in
        self.units = ttk.Combobox(interior, **myoptions)
        self.units.grid(row=0, column=0, sticky=tk.EW)

        # interior frame
        self.interior = ttk.Frame(interior)
        self.interior.grid(row=0, column=1, sticky=tk.NSEW)

    @property
    def value(self):
        return self.get()

    @value.setter
    def value(self, value):
        self.set(value)

    def show(self, *args):
        """Show only the specified subwidgets.
        'all' or no arguments reverts to showing all"""

        super().show(*args)

        show_all = len(args) == 0 or args[0] == "all"

        if show_all or "units" in args:
            self.units.grid_remove()
            self.units.grid()
        else:
            self.units.grid_remove()

    def set(self, value, unit_string=None):
        """Set the the value and units"""

        self.entry.delete(0, tk.END)
        if value is None:
            return

        # the value may have units or be a plain value
        if isinstance(value, units_class):
            self.entry.insert(0, value.magnitude)

            dimensionality = value.dimensionality
            current_units = self.units.cget("values")
            if len(current_units) > 0:
                for unit in current_units:
                    if Q_(unit).dimensionality != dimensionality:
                        self.units.configure(values=[])
                        current_units = []
                        break

            if len(current_units) == 0:
                self.set_units([*default_units(str(dimensionality)), ""])
                self.units.set("{0.units:~}".format(value).replace(" ", ""))
        elif unit_string:
            self.entry.insert(0, value)

            dimensionality = Q_(unit_string).dimensionality
            current_units = self.units.cget("values")
            if len(current_units) > 0:
                for unit in current_units:
                    if unit != "" and Q_(unit).dimensionality != dimensionality:
                        self.units.configure(values=[])
                        current_units = []
                        break

            if len(current_units) == 0:
                self.set_units([*default_units(str(dimensionality)), ""])
                self.units.set(unit_string)
        else:
            self.entry.insert(0, value)
            self.set_units("all")
            self.units.set("")

    def get(self):
        """return the current value with units"""
        value = self.entry.get()
        unit = self.units.get()
        if unit == "":
            return value
        elif self.as_quantity:
            try:
                magnitude = float(value)
                return Q_(magnitude, unit)
            except Exception:
                return (value, unit)
        else:
            return (value, unit)

    def set_units(self, values=None):
        # logger.debug('set_units: ' + str(values))
        if values is None:
            dimensionality = str(self.get().dimensionality)
            self.units.config(values=[*default_units(dimensionality), ""])
        elif values == "all":
            self.units.config(values=[*default_units("all"), ""])
        else:
            self.units.config(values=values)

    def config(self, **kwargs):
        """Set the configuration of the megawidget"""
        unitentry = options["unitentry"]
        units = options["units"]

        # cannot modify kwargs while iterating over it...
        keys = [*kwargs.keys()]
        for k in keys:
            if k in unitentry and unitentry[k] in self.__dict__:
                v = kwargs.pop(k)
                self.__dict__[unitentry[k]] = v
            elif k in units:
                v = kwargs.pop(k)
                self.units.config(**{units[k]: v})

        # having removed our options, pass rest to parent
        super().config(**kwargs)

    def state(self, stateSpec=None):
        """Set the state of the widget"""
        result = super().state(stateSpec)
        tmp = self.units.state(stateSpec)
        return result + tmp
