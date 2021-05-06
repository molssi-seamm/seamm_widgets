# -*- coding: utf-8 -*-

"""A Tk scrolled frame widget compatible with tkinter.ttk

Based on a version:
# Version: 0.22
# Author: Miguel Martinez Lopez
# Uncomment the next line to see my email
# print("Author's email: ",
# "61706c69636163696f6e616d656469646140676d61696c2e636f6d".decode("hex"))

with minor changes.
"""

import seamm_widgets as sw
import tkinter as tk
from tkinter import ttk


class ScrolledFrame(ttk.Frame):
    def __init__(
        self,
        master,
        width=None,
        anchor=tk.N,
        height=None,
        mousewheel_speed=2,
        scroll_horizontally=True,
        xscrollbar=None,
        scroll_vertically=True,
        yscrollbar=None,
        background=None,
        inner_frame=ttk.Frame,
        **kwargs
    ):
        """ """
        class_ = kwargs.pop("class_", "MScrolledFrame")
        super().__init__(master, class_=class_)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._width = width
        self._height = height

        self.canvas = tk.Canvas(
            self,
            background=background,
            highlightthickness=0,
            width=width,
            height=height,
            takefocus=True,
        )
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)

        if scroll_vertically:
            if yscrollbar is not None:
                self.yscrollbar = yscrollbar
            else:
                self.yscrollbar = ttk.Scrollbar(
                    self, orient=tk.VERTICAL, takefocus=False
                )
                self.yscrollbar.grid(row=0, column=1, sticky=tk.NS)

            self.canvas.configure(yscrollcommand=self.yscrollbar.set)
            self.yscrollbar["command"] = self.canvas.yview
        else:
            self.yscrollbar = None

        if scroll_horizontally:
            if xscrollbar is not None:
                self.xscrollbar = xscrollbar
            else:
                self.xscrollbar = ttk.Scrollbar(
                    self, orient=tk.HORIZONTAL, takefocus=False
                )
                self.xscrollbar.grid(row=1, column=0, sticky=tk.EW)

            self.canvas.configure(xscrollcommand=self.xscrollbar.set)
            self.xscrollbar["command"] = self.canvas.xview
        else:
            self.xscrollbar = None

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.innerframe = inner_frame(self.canvas, **kwargs)
        self.innerframe.pack(anchor=anchor)

        self.canvas.create_window(
            0, 0, window=self.innerframe, anchor="nw", tags="inner_frame"
        )

        self.canvas.bind("<Configure>", self._on_canvas_configure)

        sw.MousewheelSupport(self).add_support_to(
            self.canvas, xscrollbar=self.xscrollbar, yscrollbar=self.yscrollbar
        )

    @property
    def width(self):
        return self.canvas.winfo_width()

    @width.setter
    def width(self, width):
        self.canvas.configure(width=width)

    @property
    def height(self):
        return self.canvas.winfo_height()

    @height.setter
    def height(self, height):
        self.canvas.configure(height=height)

    def interior(self):
        """The frame that contains user widgets"""
        return self.innerframe

    def set_size(self, width, height):
        self.canvas.configure(width=width, height=height)

    def _on_canvas_configure(self, event):
        width = max(self.innerframe.winfo_reqwidth(), event.width)
        height = max(self.innerframe.winfo_reqheight(), event.height)

        self.canvas.configure(scrollregion="0 0 %s %s" % (width, height))
        self.canvas.itemconfigure("inner_frame", width=width, height=height)

    def update_viewport(self):
        self.update()

        window_width = self.innerframe.winfo_reqwidth()
        window_height = self.innerframe.winfo_reqheight()

        if self._width is None:
            canvas_width = window_width
        else:
            canvas_width = min(self._width, window_width)

        if self._height is None:
            canvas_height = window_height
        else:
            canvas_height = min(self._height, window_height)

        self.canvas.configure(
            scrollregion="0 0 %s %s" % (window_width, window_height),
            width=canvas_width,
            height=canvas_height,
        )
        self.canvas.itemconfigure(
            "inner_frame", width=window_width, height=window_height
        )
