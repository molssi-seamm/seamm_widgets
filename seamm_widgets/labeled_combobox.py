# -*- coding: utf-8 -*-

"""Labeled combobox widget.

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
    "combobox": {
        "class_": "class_",
        "cursor": "cursor",
        "exportselection": "exportselection",
        "justify": "justify",
        "height": "height",
        "postcommand": "postcommand",
        "state": "state",
        "style": "style",
        "takefocus": "takefocus",
        "variable": "textvariable",
        "values": "values",
        "width": "width",
    },
}


class LabeledCombobox(sw.LabeledWidget):
    def __init__(self, parent, *args, **kwargs):
        """Initialize the instance"""
        # Pull out any options specific to the label
        myoptions = {
            "height": 7,
            "width": 20,
        }
        for option, myoption in options["combobox"].items():
            if option != "class_" and option in kwargs:
                myoptions[myoption] = kwargs.pop(option)

        # Create our parent
        class_ = kwargs.pop("class_", "MLabeledCombobox")
        super().__init__(parent, class_=class_, *args, **kwargs)

        interior = self.interior

        # and put our widget in
        self.combobox = ttk.Combobox(interior, **myoptions)
        self.combobox.grid(row=0, column=0, sticky=tk.EW)

        # Add the main widget to the bind tags for the combobox so its events
        # are passed to the main LabeledCombobox.
        tags = [*self.combobox.bindtags()]
        tags.insert(2, self)
        self.combobox.bindtags(tags)

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
        'all' or no arguments reverts to showing all

        Parameters
        ----------
        *args : str
            The names of the subwidgets to show, defaults to 'all'

        Notes
        -----
        The subwidgets are 'label' and 'combobox', though 'entry' can be used as an
        alias for 'combobox'. 'all' or no arguments results in show all the subwidgets.
        """

        super().show(*args)

        show_all = len(args) == 0 or args[0] == "all"

        if show_all or "combobox" in args or "entry" in args:
            self.combobox.grid_remove()
            self.combobox.grid()
        else:
            self.combobox.grid_remove()

    def set(self, value):
        """Set the value of the widget"""

        if value is None:
            return

        self.combobox.set(value)

    def get(self):
        """return the current value"""
        value = self.combobox.get()
        return value

    def config(self, **kwargs):
        """Set the configuration of the megawidget"""
        # our options that we deal with
        combobox = options["combobox"]

        # cannot modify kwargs while iterating over it...
        keys = [*kwargs.keys()]
        for k in keys:
            if k in combobox:
                v = kwargs.pop(k)
                self.combobox.config(**{combobox[k]: v})

        # having removed our options, pass rest to parent
        super().config(**kwargs)

    def configure(self, **kwargs):
        return self.config(**kwargs)

    def state(self, stateSpec=None):
        """Set the state of the widget"""
        result = super().state(stateSpec)
        tmp = self.combobox.state(stateSpec)
        return result + tmp
