# -*- coding: utf-8 -*-

"""Base class for labeled widgets.

The goal of these widgets is twofold: to make it easier for developers
to implement dialogs with compound widgets, and to naturally
standardize the user interface presented to the user.


"""

import logging
import tkinter as tk
import tkinter.ttk as ttk

logger = logging.getLogger(__name__)

options = {
    "label": {
        "labelanchor": "anchor",
        "labelbackground": "background",
        "labelborderwidth": "borderwidth",
        "class_": "class_",
        "compound": "compound",
        "cursor": "cursor",
        "labelfont": "font",
        "labelforeground": "foreground",
        "labelimage": "image",
        "labeljustify": "justify",
        "labelpadding": "padding",
        "labelrelief": "relief",
        "style": "style",
        "labeltakefocus": "takefocus",
        "labeltext": "text",
        "labeltextvariable": "textvariable",
        "labelunderline": "underline",
        "labelwidth": "width",
        "labelwraplength": "wraplength",
    },
}


def align_labels(widgets, sticky=tk.E):
    """Align the labels of a given list of widgets"""
    if len(widgets) == 0:
        return 0

    widgets[0].update_idletasks()

    # Determine the size of the maximum length label string.
    max_width = 0
    for widget in widgets:
        width = widget.grid_bbox(0, 0)[2]
        if width > max_width:
            max_width = width

    # Adjust the margins for the labels such that the child sites and
    # labels line up.
    if len(widgets) > 1:
        for widget in widgets:
            if sticky is not None:
                widget.label.grid(sticky=sticky)
            widget.grid_columnconfigure(0, minsize=max_width)

    return max_width


class LabeledWidget(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        # Pull out any options specific to the label
        labelpos = kwargs.pop("labelpos", "w")
        myoptions = {
            "justify": "right",
            "padding": 0,
        }
        for option, myoption in options["label"].items():
            if option in kwargs:
                myoptions[myoption] = kwargs.pop(option)

        # Create our parent
        class_ = kwargs.pop("class_", "MLabeledWidget")
        super().__init__(parent, class_=class_, *args, **kwargs)

        # Put the label in
        self._labelpos = None
        self.label = ttk.Label(self, **myoptions)

        # interior frame
        self.interior = ttk.Frame(self)

        # Set the label position to the default if needed.
        self.labelpos = labelpos

    @property
    def labelpos(self):
        """Where the label is positioned relative to the widget."""
        return self._labelpos

    @labelpos.setter
    def labelpos(self, value):
        for slave in self.grid_slaves():
            slave.grid_forget()
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)

        if value[0] == "n":
            if len(value) == 2:
                self.label.grid(row=0, column=0, sticky=value[1])
            else:
                self.label.grid(row=0, column=0)
            self.interior.grid(row=1, column=0, sticky="nsew")
            self.rowconfigure(1, weight=1)
            self.columnconfigure(0, weight=1)
        elif value[0] == "e":
            self.interior.grid(row=0, column=0, sticky="nsew")
            if len(value) == 2:
                self.label.grid(row=0, column=1, sticky=value[1])
            else:
                self.label.grid(row=0, column=1)
            self.rowconfigure(0, weight=1)
            self.columnconfigure(0, weight=1)
        elif value[0] == "s":
            self.interior.grid(row=0, column=0, sticky="nsew")
            if len(value) == 2:
                self.label.grid(row=1, column=0, sticky=value[1])
            else:
                self.label.grid(row=1, column=0)
            self.rowconfigure(0, weight=1)
            self.columnconfigure(0, weight=1)
        elif value[0] == "w":
            if len(value) == 2:
                self.label.grid(row=0, column=0, sticky=value[1])
            else:
                self.label.grid(row=0, column=0)
            self.interior.grid(row=0, column=1, sticky="nsew")
            self.rowconfigure(0, weight=1)
            self.columnconfigure(1, weight=1)
        else:
            raise ValueError(f"Can't handle labelpos = '{value}'")
        self._labelpos = value

    def show(self, *args):
        """Show only the specified subwidgets.
        'all' or no arguments reverts to showing all"""

        show_all = len(args) == 0 or args[0] == "all"

        if show_all or "label" in args:
            self.label.grid_remove()
            self.label.grid()
        else:
            self.label.grid_remove()

    def config(self, **kwargs):
        """Set the configuration of the megawidget"""

        logger.debug("LabeledWidget options")
        # The options that we deal with this
        label = options["label"]

        # cannot modify kwargs while iterating over it...
        keys = [*kwargs.keys()]
        for k in keys:
            if k in label:
                v = kwargs.pop(k)
                logger.debug("   {} --> {}: {}".format(k, label[k], v))
                self.label.config(**{label[k]: v})
            elif k == "labelpos":
                self.labelpos = kwargs.pop(k)
            else:
                # Since this is the base class, raise an error force
                # unrecognized options
                raise RuntimeError("Unknown option '{}'".format(k))

    def state(self, stateSpec=None):
        """Set the state of the widget"""
        result = self.label.state(stateSpec)
        return result
