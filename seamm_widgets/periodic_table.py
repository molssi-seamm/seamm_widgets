# -*- coding: utf-8 -*-

"""A Tk scrolled frame with a periodic table of elements

This megawidget displays a periodic table for selecting one or optionally
several elements. It works with a list of element symbols.
"""

import logging
import seamm_widgets as sw
import tkinter as tk
import tkinter.ttk as ttk

module_logger = logging.getLogger(__name__)

element_layout = [
    [
        "H",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "He",
    ],  # noqa: E501, E201
    [
        "Li",
        "Be",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "B",
        "C",
        "N",
        "O",
        "F",
        "Ne",
    ],  # noqa: E501
    [
        "Na",
        "Mg",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "Al",
        "Si",
        "P",
        "S",
        "Cl",
        "Ar",
    ],  # noqa: E501
    [
        "K",
        "Ca",
        "",
        "Sc",
        "Ti",
        "V",
        "Cr",
        "Mn",
        "Fe",
        "Co",
        "Ni",
        "Cu",
        "Zn",
        "Ga",
        "Ge",
        "As",
        "Se",
        "Br",
        "Kr",
    ],  # noqa: E501, E201
    [
        "Rb",
        "Sr",
        "",
        "Y",
        "Zr",
        "Nb",
        "Mo",
        "Tc",
        "Ru",
        "Rh",
        "Pd",
        "Ag",
        "Cd",
        "In",
        "Sn",
        "Sb",
        "Te",
        "I",
        "Xe",
    ],  # noqa: E501
    [
        "Cs",
        "Ba",
        "",
        "Lu",
        "Hf",
        "Ta",
        "W",
        "Re",
        "Os",
        "Ir",
        "Pt",
        "Au",
        "Hg",
        "Tl",
        "Pb",
        "Bi",
        "Po",
        "At",
        "Rn",
    ],  # noqa: E501
    [
        "Fr",
        "Ra",
        "",
        "Lr",
        "Rf",
        "Db",
        "Sg",
        "Bh",
        "Hs",
        "Mt",
        "Ds",
        "Rg",
        "Cn",
        "Nh",
        "Fl",
        "Mc",
        "Lv",
        "Ts",
        "Og",
    ],  # noqa: E501
    [],
    [
        "",
        "",
        "",
        "La",
        "Ce",
        "Pr",
        "Nd",
        "Pm",
        "Sm",
        "Eu",
        "Gd",
        "Tb",
        "Dy",
        "Ho",
        "Er",
        "Tm",
        "Yb",
    ],  # noqa: E501, E201
    [
        "",
        "",
        "",
        "Ac",
        "Th",
        "Pa",
        "U",
        "Np",
        "Pu",
        "Am",
        "Cm",
        "Bk",
        "Cf",
        "Es",
        "Fm",
        "Md",
        "No",
    ],  # noqa: E501, E201
]  # yapf: disable


class PeriodicTable(sw.LabeledWidget):
    """A widget to handle manual input of keywords with optional values"""

    def __init__(
        self, master, labelanchor=tk.N, logger=module_logger, command=None, **kwargs
    ):
        """ """
        self.logger = logger

        self._widget = {}
        self._max_selected = "all"
        self._command = command
        self._disabled = []

        class_ = kwargs.pop("class_", "MPeriodicTable")

        # s = ttk.Style()
        # s.configure('Red.TEntry', foreground='red')

        super().__init__(master, class_=class_, labelanchor=labelanchor, **kwargs)

        # Create the widgets
        frame = self.interior
        for row, elements in enumerate(element_layout):
            for col, element in enumerate(elements):
                if element != "":
                    self._widget[element] = tk.Button(
                        frame,
                        text=element,
                        width=2,
                        relief="raised",
                        command=lambda x=element: self.handle_button(element=x),
                    )

        # Setup the graphical table
        self.reset_widgets()

        # After everything is set up can put

    @property
    def command(self):
        """A command to execute when an element is selected."""
        return self._command

    @command.setter
    def command(self, command):
        self._command = command

    @property
    def disabled(self):
        """The elements that are disabled."""
        return self._disabled

    @disabled.setter
    def disabled(self, elements):
        for element in self.elements:
            button = self._widget[element]
            if element in self._disabled:
                if element not in elements:
                    button.configure(state="normal", relief="raised")
            else:
                button.configure(state="disabled", relief="raised")
        self._disabled = elements

    @property
    def elements(self):
        elements = []
        for period in element_layout:
            for element in period:
                if element != "":
                    elements.append(element)
        return elements

    def disable(self, elements):
        """Disable the buttons for the given elements"""
        if elements == "all":
            elements = self.elements
        for element in elements:
            if element not in self._disabled:
                button = self._widget[element]
                button.configure(state="disabled", relief="raised")
                if isinstance(self._disabled, set):
                    self._disabled.add(element)
                else:
                    self._disabled.append(element)

    def enable(self, elements):
        """Disable the buttons for the given elements"""
        if elements == "all":
            elements = self.elements
        for element in elements:
            if element in self._disabled:
                button = self._widget[element]
                button.configure(state="normal", relief="raised")
                self._disabled.remove(element)

    def set_text_color(self, elements="all", color="black"):
        """Set the color of the text in the button for the given elements"""
        if elements == "all":
            for element in self.elements:
                self._widget[element].configure(fg=color)
        else:
            for element in elements:
                self._widget[element].configure(fg=color)

    def reset_widgets(self):
        """Layout the widgets for the current state."""
        frame = self.interior

        # Unpack any widgets
        for slave in frame.grid_slaves():
            slave.grid_forget()

        for row, elements in enumerate(element_layout):
            for col, element in enumerate(elements):
                if element != "":
                    self._widget[element].grid(row=row, column=col, sticky=tk.EW)

        frame.grid_columnconfigure(2, minsize=30)
        frame.grid_rowconfigure(7, minsize=30)

        self._activebackground = self._widget["H"].cget("activebackground")
        self._background = self._widget["H"].cget("background")

    def handle_button(self, element):
        button = self._widget[element]
        relief = button.cget("relief")
        if relief == "sunken":
            button.configure(state="normal", relief="raised")
        else:
            button.configure(state="active", relief="sunken")
        if self._command is not None:
            self._command(self.get())

    def get(self):
        """Return the list of selected elements."""
        result = []
        for element in self._widget:
            button = self._widget[element]
            if button.cget("relief") == "sunken":
                result.append(element)
        return result

    def set(self, elements):
        """Return the list of selected elements."""
        for element in self._widget:
            button = self._widget[element]
            if element in elements:
                button.configure(state="active", relief="sunken")
            else:
                button.configure(state="normal", relief="raised")
        if self._command is not None:
            self._command(self.get())


if __name__ == "__main__":  # pragma: no cover
    import sys
    import Pmw

    def handle_dialog(result):
        global gElements
        print(f"result = {result}")
        if result == "Update":
            # w.set(gElements)
            w.set(["H", "Li", "Na", "K"])
            return
        dialog.deactivate(result)
        if result == "OK":
            gElements = w.get()
            print(gElements)
        w.destroy()

    def open_dialog():
        global w
        print("open dialog")
        print(gElements)

        w = PeriodicTable(dialog.interior())
        w.pack(expand="yes", fill="both")

        w.set(gElements)
        dialog.activate()

    ##################################################
    # Initialize Tk
    ##################################################
    if sys.platform.startswith("darwin"):
        CmdKey = "Command-"
    else:
        CmdKey = "Control-"

    root = tk.Tk()
    Pmw.initialise(root)

    dialog = Pmw.Dialog(
        root,
        buttons=("OK", "Update", "Cancel"),
        defaultbutton=None,
        master=root,
        title="Periodic Table",
        command=handle_dialog,
    )
    dialog.geometry("500x400")

    w = PeriodicTable(dialog.interior())
    w.pack(expand="yes", fill="both")

    gElements = ["C", "H"]
    w.set(gElements)
    exit_button = ttk.Button(root, text="Exit", command=exit)
    post_button = ttk.Button(root, text="Edit", command=open_dialog)
    post_button.grid(column=0, row=0)
    exit_button.grid(column=2, row=0)

    dialog.activate(geometry="centerscreenfirst")

    # enter the event loop
    root.mainloop()
