# -*- coding: utf-8 -*-

"""Labeled entry widget.

The goal of these widgets is twofold: to make it easier for developers
to implement dialogs with compound widgets, and to naturally
standardize the user interface presented to the user.
"""

import logging
import seamm_widgets as sw
import tkinter as tk
import tkinter.ttk as ttk

logger = logging.getLogger(__name__)

options = {
    "entry": {
        "class_": "class_",
        "cursor": "cursor",
        "exportselection": "exportselection",
        "font": "font",
        "invalidcommand": "invalidcommand",
        "justify": "justify",
        "show": "show",
        "style": "style",
        "takefocus": "takefocus",
        "variable": "textvariable",
        "validate": "validate",
        "validatecommand": "validatecommand",
        "width": "width",
        "xscrollcommand": "xscrollcommand",
    },
}


class LabeledEntry(sw.LabeledWidget):
    def __init__(self, parent, *args, **kwargs):
        """Initialize the instance"""
        # Pull out any options specific to the entry
        myoptions = {
            "justify": tk.LEFT,
            "width": 15,
            "state": "normal",
        }
        for option, myoption in options["entry"].items():
            if option in kwargs:
                myoptions[myoption] = kwargs.pop(option)

        # Create our parent
        class_ = kwargs.pop("class_", "MLabeledEntry")
        super().__init__(parent, class_=class_)

        interior = self.interior

        # and put our widget in
        self.entry = ttk.Entry(interior, **myoptions)
        self.entry.grid(row=0, column=0, sticky=tk.EW)

        # interior frame
        self.interior = ttk.Frame(interior)
        self.interior.grid(row=0, column=1, sticky=tk.NSEW)
        interior.columnconfigure(0, weight=1)

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

        if show_all or "entry" in args:
            self.entry.grid_remove()
            self.entry.grid()
        else:
            self.entry.grid_remove()

    def set(self, value):
        """Set the value of the entry widget"""

        self.entry.delete(0, tk.END)
        if value is None:
            return

        self.entry.insert(0, value)

    def get(self):
        """return the current value"""
        value = self.entry.get()
        return value

    def config(self, **kwargs):
        """Set the configuration of the megawidget"""

        # our options that we deal with
        entry = options["entry"]

        # cannot modify kwargs while iterating over it...
        keys = [*kwargs.keys()]
        for k in keys:
            if k in entry:
                v = kwargs.pop(k)
                self.entry.config(**{entry[k]: v})

        # having removed our options, pass rest to parent
        super().config(**kwargs)

    def state(self, stateSpec=None):
        """Set the state of the widget"""
        result = super().state(stateSpec)
        tmp = self.entry.state(stateSpec)
        return result + tmp
