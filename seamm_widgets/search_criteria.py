# -*- coding: utf-8 -*-

"""A Tk widget for gathering criteria for e.g. a search.

This widget provides a table of criteria, plus a '+' button to add another
row to the table. Each criterion is implemented as a "Criterion" widget, which
has the following subwidgets:

    inclusion
        A combobox giving an introductory condition, such as 'with' or 'without',
        or 'contains' or 'does not contain'.
    field
        A combobox giving the field to search, e.g. 'keyword' or 'author'
    operator
        A combobox giving the search operator, e.g. '<', '>' or '='
    value
        An entry for the value of the, e.g. 'molecule' or 'Doe, John'
    value2
        A second optional entry for operators such as 'between'

Each of these subwidgets is itself a labeled widget, giving more flexibility
in composing a reasonable natural language statement, such as:

    entries that contain a keyword like molecule
    entries that do not contain a author like Doe, John
"""
import logging
import tkinter as tk
from tkinter import ttk

import seamm_widgets as sw

logger = logging.getLogger(__name__)


class Criterion(sw.LabeledWidget):
    """Class to provide a line in a search criteria widget."""

    def __init__(self, parent, *args, **kwargs):
        class_ = kwargs.pop("class_", "MCriterion")
        super().__init__(parent, class_=class_)

        frame = self.frame = self.interior

        self.command = kwargs.pop("command", None)

        # Inclusion combobox
        inclusiontext = kwargs.pop("inclusiontext", "")
        inclusionvalues = kwargs.pop("inclusionvalues", ("and", "or"))
        inclusionheight = kwargs.pop("inclusionheight", 7)
        inclusionwidth = kwargs.pop("inclusionwidth", 3)
        inclusionstate = kwargs.pop("inclusionstate", "readonly")

        self.inclusion = sw.LabeledCombobox(
            frame,
            labeltext=inclusiontext,
            values=inclusionvalues,
            height=inclusionheight,
            width=inclusionwidth,
            state=inclusionstate,
        )
        self.inclusion.grid(row=0, column=0, sticky=tk.EW)
        if len(inclusionvalues) > 0:
            self.inclusion.set(inclusionvalues[0])

        cb = self.inclusion.combobox
        cb.bind(
            "<<ComboboxSelected>>",
            lambda event, what="inclusion": self.callback(event, what),
        )
        if inclusionstate == "normal":
            cb.bind(
                "<Return>", lambda event, what="inclusion": self.callback(event, what)
            )
            cb.bind(
                "<FocusOut>", lambda event, what="inclusion": self.callback(event, what)
            )

        # Field combobox
        fieldtext = kwargs.pop("fieldtext", "")
        fieldvalues = kwargs.pop("fieldvalues", tuple())
        fieldheight = kwargs.pop("fieldheight", 7)
        fieldwidth = kwargs.pop("fieldwidth", 10)
        fieldstate = kwargs.pop("fieldstate", "readonly")

        self.field = sw.LabeledCombobox(
            frame,
            labeltext=fieldtext,
            values=fieldvalues,
            height=fieldheight,
            width=fieldwidth,
            state=fieldstate,
        )
        self.field.grid(row=0, column=1, sticky=tk.EW)
        if len(fieldvalues) > 0:
            self.field.set(fieldvalues[0])

        cb = self.field.combobox
        cb.bind(
            "<<ComboboxSelected>>",
            lambda event, what="field": self.callback(event, what),
        )
        if fieldstate == "normal":
            cb.bind("<Return>", lambda event, what="field": self.callback(event, what))
            cb.bind(
                "<FocusOut>", lambda event, what="field": self.callback(event, what)
            )

        # Operator combobox
        operatortext = kwargs.pop("operatortext", "")
        operatorvalues = kwargs.pop("operatorvalues", tuple())
        operatorheight = kwargs.pop("operatorheight", 7)
        operatorwidth = kwargs.pop("operatorwidth", 10)
        operatorstate = kwargs.pop("operatorstate", "readonly")

        self.operator = sw.LabeledCombobox(
            frame,
            labeltext=operatortext,
            values=operatorvalues,
            height=operatorheight,
            width=operatorwidth,
            state=operatorstate,
        )
        self.operator.grid(row=0, column=2, sticky=tk.EW)
        if len(operatorvalues) > 0:
            self.operator.set(operatorvalues[0])

        cb = self.operator.combobox
        cb.bind(
            "<<ComboboxSelected>>",
            lambda event, what="operator": self.callback(event, what),
        )
        if operatorstate == "normal":
            cb.bind(
                "<Return>", lambda event, what="operator": self.callback(event, what)
            )
            cb.bind(
                "<FocusOut>", lambda event, what="operator": self.callback(event, what)
            )

        # Value entry
        valuetext = kwargs.pop("valuetext", "")
        valuewidth = kwargs.pop("valuewidth", 10)

        self.value = sw.LabeledEntry(frame, labeltext=valuetext, width=valuewidth)
        self.value.grid(row=0, column=3, sticky=tk.EW)

        # Value2 entry
        value2text = kwargs.pop("value2text", " and ")
        value2width = kwargs.pop("value2width", 10)

        self.value2 = sw.LabeledEntry(frame, labeltext=value2text, width=value2width)
        self.value2.grid(row=0, column=4, sticky=tk.EW)

        # interior frame
        self.interior = ttk.Frame(frame)
        self.interior.grid(row=0, column=5, sticky=tk.NSEW)
        frame.columnconfigure(5, weight=1)

        two_values = kwargs.pop("two_values", False)

        self.config(**kwargs)

        self.two_values = two_values

    @property
    def two_values(self):
        """Whether to display two values for e.g. 'between'."""
        return self._two_values

    @two_values.setter
    def two_values(self, value):
        if not isinstance(value, bool):
            try:
                iter(value)
            except TypeError:
                raise ValueError(
                    "'two_values' must be a boolean or iterable of opertors that need "
                    "two values."
                )
        self._two_values = value
        self.callback("internal", "self.two_values")

    def callback(self, event, what):
        """Call the command for changes in the widget value.
        Also check the operator value and reconfigure the widget for one or two
        values if requested."""

        if what in ("operator", "self.two_values", "set"):
            if isinstance(self._two_values, bool):
                show = self._two_values
            else:
                operator = self.operator.get()
                show = operator in self._two_values

            if show:
                self.show("value2")
                # if self.value2 not in self.frame.grid_slaves():
                #     self.value2.grid(row=0, column=4, sticky=tk.EW)
            else:
                self.hide("value2")
                # if self.value2 in self.frame.grid_slaves():
                #     self.value2.grid_forget()
        elif what == "inclusion":
            include = self.inclusion.get()
            if include in ("and", "or", "(", ")"):
                self.hide("all")
                self.show("inclusion")
            else:
                self.show("all")
                if isinstance(self._two_values, bool):
                    show = self._two_values
                else:
                    operator = self.operator.get()
                    show = operator in self._two_values
                if not show:
                    self.hide("value2")

        if self.command is not None:
            self.command(self, event, what)

    def clear(self):
        """Remove all rows from the table."""
        for remove_button, criterion in self._rows.items():
            remove_button.destroy()
            criterion.destroy()

        self.callback(None, "internal", "clear")

        self._rows = []
        self.layout()

    def get(self):
        """Return the values of the widgets as a tuple."""
        return (
            self.inclusion.get(),
            self.field.get(),
            self.operator.get(),
            self.value.get(),
            self.value2.get(),
        )

    def hide(self, *args):
        """Hide the specified subwidgets.
        'all' or no arguments hides all the subwidgets
        """

        hide_all = len(args) == 0 or args[0] == "all"

        if hide_all or "inclusion" in args:
            self.inclusion.grid_forget()
        if hide_all or "field" in args:
            self.field.grid_forget()
        if hide_all or "operator" in args:
            self.operator.grid_forget()
        if hide_all or "value" in args:
            self.value.grid_forget()
        if hide_all or "value2" in args:
            self.value2.grid_forget()

    def set(self, *args):
        """Set the values of the widgets as a tuple.

        Parameters
        ----------
        args : [str] or str, str, str, str ,str
            either a single iterable of length 5 or 5 separate values...
        """
        if len(args) == 1:
            if len(args[0]) == 5:
                args = args[0]
            else:
                raise ValueError("set expects with a 5-long list or 5 separate values")
        elif len(args) != 5:
            raise ValueError("set expects with a 5-long list or 5 separate values")

        self.inclusion.set(args[0])
        self.field.set(args[1])
        self.operator.set(args[2])
        self.value.set(args[3])
        self.value2.set(args[4])

        self.callback("internal", "set")

    def show(self, *args):
        """Show the specified subwidgets.
        'all' or no arguments reverts to showing all"""

        show_all = len(args) == 0 or args[0] == "all"

        if show_all or "inclusion" in args:
            self.inclusion.grid(row=0, column=0, sticky=tk.EW)
        if show_all or "field" in args:
            self.field.grid(row=0, column=1, sticky=tk.EW)
        if show_all or "operator" in args:
            self.operator.grid(row=0, column=2, sticky=tk.EW)
        if show_all or "value" in args:
            self.value.grid(row=0, column=3, sticky=tk.EW)
        if show_all or "value2" in args:
            self.value2.grid(row=0, column=4, sticky=tk.EW)


class SearchCriteria(sw.ScrolledLabelFrame):
    """Class to editable list of criteria for e.g. searching."""

    def __init__(self, parent, *args, **kwargs):
        class_ = kwargs.pop("class_", "MSearchCriteria")
        super().__init__(parent, class_=class_)

        self.command = kwargs.pop("command", None)

        self.inclusiontext = kwargs.pop("inclusiontext", "")
        self.inclusionvalues = kwargs.pop("inclusionvalues", ("with", "without"))
        self.inclusionheight = kwargs.pop("inclusionheight", 7)
        self.inclusionwidth = kwargs.pop("inclusionwidth", 10)
        self.inclusionstate = kwargs.pop("inclusionstate", "readonly")

        self.fieldtext = kwargs.pop("fieldtext", "")
        self.fieldvalues = kwargs.pop("fieldvalues", tuple())
        self.fieldheight = kwargs.pop("fieldheight", 7)
        self.fieldwidth = kwargs.pop("fieldwidth", 10)
        self.fieldstate = kwargs.pop("fieldstate", "readonly")

        self.operatortext = kwargs.pop("operatortext", "")
        self.operatorvalues = kwargs.pop("operatorvalues", tuple())
        self.operatorheight = kwargs.pop("operatorheight", 7)
        self.operatorwidth = kwargs.pop("operatorwidth", 10)
        self.operatorstate = kwargs.pop("operatorstate", "readonly")

        self.two_values = kwargs.pop("two_values", ("between",))

        self._rows = []

        frame = self.frame = self.interior()

        # The button to add a new row
        self.add_button = ttk.Button(
            frame,
            text="+",
            width=2,
            command=self.add_row,
            takefocus=True,
        )

        # interior frame
        self.interior = ttk.Frame(frame)
        self.interior.grid(row=0, column=5, sticky=tk.NSEW)

        self.config(**kwargs)

        self.layout()

    def add_row(self, values=None):
        """Add a new row to the table.

        Parameters
        ----------
        values : [5]
            Values to set the criterion widget with.
        """
        # The button to remove a row...
        remove_button = ttk.Button(
            self.frame,
            text="-",
            width=2,
            command=lambda index=len(self._rows): self.remove_row(index),
            takefocus=True,
        )

        # and the criterion
        criterion = Criterion(
            self.frame,
            command=self.callback,
            inclusiontext=self.inclusiontext,
            inclusionvalues=self.inclusionvalues,
            inclusionheight=self.inclusionheight,
            inclusionwidth=self.inclusionwidth,
            inclusionstate=self.inclusionstate,
            fieldtext=self.fieldtext,
            fieldvalues=self.fieldvalues,
            fieldheight=self.fieldheight,
            fieldwidth=self.fieldwidth,
            fieldstate=self.fieldstate,
            operatortext=self.operatortext,
            operatorvalues=self.operatorvalues,
            operatorheight=self.operatorheight,
            operatorwidth=self.operatorwidth,
            operatorstate=self.operatorstate,
            two_values=self.two_values,
        )
        if values is not None:
            criterion.set(values)

        self._rows.append((remove_button, criterion))

        self.callback(criterion, "internal", "add row")

        self.layout()

        return criterion

    def callback(self, criterion, event, what):
        """Call the command for changes in the widget value."""
        if self.command is not None:
            self.command(self, criterion, event, what)

    def get(self):
        """Return the list of criteria."""
        result = []
        for _, criterion in self._rows:
            result.append(criterion.get())

        return result

    def layout(self):
        """Layout the criteria.

        Indent rows after a parenthesis.
        """

        frame = self.frame

        # Remove any weights on columns
        for i in range(frame.grid_size()[0]):
            frame.grid_columnconfigure(i, weight=0)

        # Unpack any widgets
        for slave in frame.grid_slaves():
            slave.grid_forget()

        level = 0
        max_level = 0
        for remove_button, criterion in self._rows:
            inclusion = criterion.get()[0]
            if "(" in inclusion:
                level += 1
                if level > max_level:
                    max_level = level
            elif ")" in inclusion:
                level -= 1

        level = 0
        row = 0
        for remove_button, criterion in self._rows:
            remove_button.grid(row=row, column=0, sticky=tk.EW)
            span = max_level - level + 1
            logger.debug(
                f"criterion.grid(row={row}, column={1 + level}, columnspan={span}..."
            )
            criterion.grid(row=row, column=1 + level, columnspan=span, sticky=tk.EW)
            row += 1

            inclusion = criterion.get()[0]
            if "(" in inclusion:
                level += 1
                if level > max_level:
                    max_level = level
            elif ")" in inclusion:
                level -= 1
            logger.debug(f"{inclusion=}, {level=}")

        self.add_button.grid(row=row, column=0, sticky=tk.EW)

        # Set up the last column as the one that expands
        frame.grid_columnconfigure(max_level + 1, weight=1)

        # and minumum widths to indent
        for i in range(1, max_level + 1):
            logger.debug(f"frame.grid_columnconfigure({i}, minsize=30)")
            frame.grid_columnconfigure(i, minsize=30)

    def remove_row(self, index):
        """Remove a row from the table.

        Parameters
        ----------
        index : int
            The row in the table to remove.
        """
        remove_button, criterion = self._rows[index]
        remove_button.destroy()
        criterion.destroy()
        del self._rows[index]

        self.callback(None, "internal", "remove row")

        # Set the index of each row...
        for i, row in enumerate(self._rows):
            row[0].configure(command=lambda index=i: self.remove_row(index))

        self.layout()

    def set(self, criteria):
        """Set the current value of the widget to the given criteria.

        Parameters
        ----------
        criteria : [tuple()]
            A list of the value for each criterion.
        """
        self.clear()

        for values in criteria:
            self.add_row(values=values)


if __name__ == "__main__":  # pragma: no cover

    def check(w):
        print(w.get())

    def set_values(w):
        w.set("with out", "author", "between", "a", "m")

    def callback(self, criterion, event, what):
        if what in ("add row", "field", "set"):
            inclusion, field, operator, value, value2 = criterion.get()
            w = criterion.operator
            if field == "author":
                w.configure(values=("like", "is"))
                w.set("like")
            elif field == "keyword":
                w.configure(values=("is", "like"))
                w.set("is")
            elif field == "date":
                w.configure(values=("is", "is before", "is after", "between"))
                w.set("is after")

    root = tk.Tk()
    root.title("Search Criteria")

    # criterion = Criterion(
    #     root,
    #     fieldvalues=("keyword", "author", "date"),
    #     operatorvalues=("=", "like"),
    #     two_values=("between",),
    # )
    # criterion.grid(row=0, column=0, columnspan=2, sticky=tk.EW)

    # w = ttk.Button(root, text="Check", command=lambda w=criterion: check(w))
    # w.grid(row=1, column=0)

    # w = ttk.Button(root, text="Set", command=lambda w=criterion: set_values(w))
    # w.grid(row=1, column=1)

    search = SearchCriteria(
        root,
        text="Find Flowcharts",
        labelanchor=tk.N,
        inclusiontext="That ",
        inclusionvalues=("contain", "do not contain"),
        fieldvalues=("keyword", "author", "date"),
        operatorvalues=("<", ">", "=", "like", "between"),
        two_values=("between",),
        command=callback,
    )
    search.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    root.mainloop()
