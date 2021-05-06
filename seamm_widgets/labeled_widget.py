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


def align_labels(widgets, sticky=None):
    """Align the labels of a given list of widgets"""
    if len(widgets) <= 1:
        return

    widgets[0].update_idletasks()

    # Determine the size of the maximum length label string.
    max_width = 0
    for widget in widgets:
        width = widget.grid_bbox(0, 0)[2]
        if width > max_width:
            max_width = width

    # Adjust the margins for the labels such that the child sites and
    # labels line up.
    for widget in widgets:
        if sticky is not None:
            widget.label.grid(sticky=sticky)
        widget.grid_columnconfigure(0, minsize=max_width)


class LabeledWidget(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        """Initialize the instance"""
        class_ = kwargs.pop("class_", "MLabeledWidget")
        super().__init__(parent, class_=class_)

        # label
        labeltext = kwargs.pop("labeltext", "")
        # labeltextvariable = kwargs.pop('labeltextvariable', None)
        labeljustify = kwargs.pop("labeljustify", "right")
        labelpadding = kwargs.pop("labelpadding", 0)

        self.label = ttk.Label(
            self, text=labeltext, justify=labeljustify, padding=labelpadding
        )
        self.label.grid(row=0, column=0, sticky=tk.E)

        # interior frame
        self.interior = ttk.Frame(self)
        self.interior.grid(row=0, column=1, sticky=tk.NSEW)

        self.columnconfigure(1, weight=1)

        self.config(**kwargs)

    def show(self, *args):
        """Show only the specified subwidgets.
        'all' or no arguments reverts to showing all"""

        show_all = len(args) == 0 or args[0] == "all"

        if show_all or "label" in args:
            self.label.grid(row=0, column=0, sticky=tk.E)
        else:
            self.label.grid_forget()

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
            else:
                # Since this is the base class, raise an error force
                # unrecognized options
                raise RuntimeError("Unknown option '{}'".format(k))
