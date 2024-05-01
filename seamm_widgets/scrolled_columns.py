# -*- coding: utf-8 -*-

"""A ttk-based widget for columns of widgets, with fixed titles and scrolling

This widgets has two areas: a row of titles across the top and a scrolled frame
below it. It is used to make a table of widgets with fixed column headers.
"""

import seamm_widgets as sw
import tkinter as tk
from tkinter import ttk


class ScrolledColumns(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        """Initialize the widget"""

        class_ = kwargs.pop("class_", "MScrolledColumns")
        super().__init__(parent, class_=class_)

        columns = kwargs.pop("columns", [])
        self.min_sizes = kwargs.pop("minsize", [])
        self._after_id = None

        # list (vector) of the header widgets, _ncolumns long
        self._header_widgets = []

        # list of lists (row x column) of widgets in the table
        self._widgets = []

        # Columns that are separators
        self._column_separators = set()

        # Create the two subframes, linking them both to the
        # horizontal scrollbar at the bottom
        # self.headers = ttk.Frame(self)
        self.table = sw.ScrolledFrame(
            self, scroll_vertically=True, borderwidth=2, relief=tk.SUNKEN
        )
        self.headers = sw.ScrolledFrame(
            self,
            scroll_vertically=False,
            borderwidth=2,
            relief=tk.RAISED,
            xscrollbar=self.table.xscrollbar,
            height=22,
        )

        # and patch up the horizontal scrolling
        self.table.xscrollbar["command"] = self.xview

        self.headers.grid(row=0, column=0, sticky=tk.EW)
        self.table.grid(row=1, column=0, sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Put in the column titles if given
        col = 0
        header = self.headers.interior()
        for item in columns:
            if isinstance(item, str):
                if item == "|":
                    self._column_separators.add(col)
                item = ttk.Label(header, text=item)
            item.grid(row=0, column=col)
            col += 1
            self._header_widgets.append(item)

    def cell(self, row, column, value=None):
        """Return or set the widget at the given cell"""
        if value is None:
            try:
                result = self._widgets[row][column]
            except Exception:
                raise
            return result
        else:
            if column >= self.ncolumns:
                # pad the header and each row with None's
                extra = [None] * (column - self.ncolumns + 1)
                self._header_widgets.extend(extra)
                for row_of_widgets in self._widgets:
                    row_of_widgets.extend(extra)
            if row >= self.nrows:
                # add rows 'till we get there
                for i in range(self.nrows, row + 1):
                    extra = []
                    for col in range(self.ncolumns):
                        if col in self._column_separators:
                            tmp = ttk.Label(self.table.interior(), text="|")
                            tmp.grid(row=i, column=col)
                            extra.append(tmp)
                        else:
                            extra.append(None)
                    self._widgets.append(extra)

            if isinstance(value, str):
                value = ttk.Label(self.table.interior(), text=value)

            value.grid(row=row, column=column)
            self._widgets[row][column] = value

            self._update_widths()

    def clear(self):
        """Clear the contents of the widget.

        Returns
        -------
        None
        """
        for row in self._widgets:
            for item in row:
                if item is not None:
                    item.destroy()
        self._widgets = []

    def delete_row(self, index):
        for item in self._widgets[index]:
            if item is not None:
                item.destroy()
        del self._widgets[index]

        self._update_widths()

    def delete_column(self, index):
        for row in self._widgets:
            item = row[index]
            if item is not None:
                item.destroy()
            del row[index]

        self._update_widths()

    # Provide matrix-like access to the widgets to make
    # the code cleaner

    def __getitem__(self, index):
        """Allow [row,column] access to the widgets!"""
        if isinstance(index, tuple):
            row, column = index
            return self.cell(row, column)
        else:
            raise Exception("Row and column indices are required")

    def __setitem__(self, index, value):
        """Allow x[row,column] access to the data"""
        if isinstance(index, tuple):
            row, column = index
            self.cell(row, column, value)
        else:
            raise Exception("Row and column indices are required")

    def __delitem__(self, key):
        """Allow deletion of keys"""
        if isinstance(key, tuple):
            row, column = key
            widget = self.cell(row, column)
            widget.destroy()
            self.cell(row, column, None)

            self._update_widths()
        else:
            raise Exception("Row and column indices are required")

    @property
    def nrows(self):
        return len(self._widgets)

    @property
    def ncolumns(self):
        return len(self._header_widgets)

    def _update_widths_now(self):
        """Force the update of the column widths to happen now"""
        self._update_widths(when="now")

    def _update_widths(self, when="later"):
        """Make the column widths of header and table identical"""

        if when == "later":
            if self._after_id is None:
                self._after_id = self.after_idle(self._update_widths_now)
            return

        self.after_cancel(self._after_id)
        self._after_id = None

        header = self.headers.interior()
        table = self.table.interior()

        # Remove any widths currently set
        for column in range(0, self.ncolumns):
            header.columnconfigure(column, minsize=0)
            table.columnconfigure(column, minsize=0)

        # Let everything settle and finds its size
        header.update_idletasks()

        # And make the sizes equal
        for column in range(0, self.ncolumns):
            # bbox returns (x, y, w, h) so we want the third item
            w1 = header.grid_bbox(column, 0)[2]
            w2 = table.grid_bbox(column, 0)[2]
            if w1 < w2:
                header.columnconfigure(column, minsize=w2)
            else:
                table.columnconfigure(column, minsize=w1)

        # ensure that the header area is large enough
        h = header.grid_bbox(0, 0)[3]
        self.headers.height = h + 5

    def interior(self):
        """Where the user packs widgets"""
        return self.table.interior()

    def xview(self, *args):
        """Connect the subwidgets to the single scrollbar"""
        self.headers.canvas.xview(*args)
        self.table.canvas.xview(*args)
