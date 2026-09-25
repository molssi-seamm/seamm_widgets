# -*- coding: utf-8 -*-

"""Labeled multi-line text widget.

Unlike LabeledEntry (a single-line ttk.Entry), this holds free-form
multi-line text -- e.g. a verbatim block of input for a code that a
single-line combobox/entry cannot represent.
"""

import logging

import seamm_widgets as sw
import tkinter as tk
import tkinter.ttk as ttk

logger = logging.getLogger(__name__)


class LabeledText(sw.LabeledWidget):
    def __init__(self, parent, *args, **kwargs):
        """Initialize the instance"""
        # Pull out the options specific to the text box (in characters/lines,
        # not pixels -- ttk.Frame's own width/height are in pixels, so these
        # must not reach it).
        height = kwargs.pop("height", 4)
        width = kwargs.pop("width", 40)

        # Create our parent
        class_ = kwargs.pop("class_", "MLabeledText")
        super().__init__(parent, class_=class_, *args, **kwargs)

        interior = self.interior

        self.text = tk.Text(interior, height=height, width=width, wrap="none")
        self.text.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar = ttk.Scrollbar(interior, orient="vertical", command=self.text.yview)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.text.configure(yscrollcommand=scrollbar.set)
        interior.rowconfigure(0, weight=1)
        interior.columnconfigure(0, weight=1)

        # Add the main widget to the bind tags so its events are passed to
        # the main LabeledText.
        tags = [*self.text.bindtags()]
        tags.insert(2, self)
        self.text.bindtags(tags)

        # interior frame, mirroring LabeledEntry, in case a caller wants to
        # add more widgets alongside the text box.
        self.interior = ttk.Frame(interior)
        self.interior.grid(row=0, column=2, sticky=tk.NSEW)

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

        if show_all or "text" in args:
            self.text.grid_remove()
            self.text.grid()
        else:
            self.text.grid_remove()

    def set(self, value):
        """Set the contents of the text box."""
        self.text.delete("1.0", tk.END)
        if value:
            self.text.insert("1.0", value)

    def get(self):
        """Return the current contents (Tk always adds a trailing newline to
        the buffer; 'end-1c' omits it)."""
        return self.text.get("1.0", "end-1c")

    def config(self, **kwargs):
        """Set the configuration of the megawidget"""
        if len(kwargs) == 0:
            return super().config()
        super().config(**kwargs)

    def configure(self, **kwargs):
        return self.config(**kwargs)
