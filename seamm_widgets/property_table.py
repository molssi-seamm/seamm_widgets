# -*- coding: utf-8 -*-

"""A Tk scrolled frame containing and handling a table of properties.

This megawidget displays a list of properties that the user can add to and also
delete.
"""

from itertools import takewhile
import logging
import Pmw
import seamm_widgets as sw
import tkinter as tk
import tkinter.ttk as ttk

module_logger = logging.getLogger(__name__)


def lcp(*s):
    """Longest common prefix of strings"""
    return "".join(a for a, b in takewhile(lambda x: x[0] == x[1], zip(min(s), max(s))))


class PropertyTable(sw.ScrolledFrame):
    """A widget to handle manual input of property names"""

    def __init__(
        self,
        master,
        metadata=None,
        properties="",
        logger=module_logger,
        labeltext="",
        **kwargs
    ):
        """ """
        self.logger = logger
        self._properties = []
        self._max_width = 0
        self._working_properties = None
        self._add_widget = None
        self._dialog = None
        self._set_property_cb = None
        self._labeltext = labeltext
        self.popup_menu = None

        class_ = kwargs.pop("class_", "MProperties")

        s = ttk.Style()
        s.configure("Red.TEntry", foreground="red")

        super().__init__(master, class_=class_, inner_frame=ttk.Frame, **kwargs)

        # After everything is set up can put in the properties and metadata
        self.metadata = metadata
        self.properties = properties

    @property
    def properties(self):
        """The current properties, reflecting changes in the widgets"""
        # result = []
        # for d in self._working_properties:
        #     result.append((d['property'], d['accuracy']))
        # return result
        return self.get()

    @properties.setter
    def properties(self, value):
        self.logger.debug("Properties::properties: " + str(value))
        self.clear()
        self._working_properties = []
        self._properties = value
        if value is not None:
            for item in value:
                _property, accuracy = item
                self._working_properties.append(
                    {"property": _property, "accuracy": accuracy}
                )
        self.logger.debug("  properties.setter call layout_properties")
        self.layout_properties()

    def set(self, value):
        """Set the properties in the widget."""
        self.properties = value

    @property
    def metadata(self):
        """The current metadata"""
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        self._metadata = value
        self._max_width = 0
        if value is not None:
            for _property in self._metadata.keys():
                width = len(_property)
                if width > self._max_width:
                    self._max_width = width
            self._max_width += 3  # a little padding...
            self.properties = self._properties

    def clear(self):
        """Remove the widgets."""
        if self._working_properties is not None:
            for d in self._working_properties:
                if "widgets" in d:
                    for widget in d["widgets"].values():
                        widget.destroy()
                    del d["widgets"]

    def reset(self):
        """Remove any changes made in the dialog."""
        self.properties = self._properties

    def layout_properties(self):
        """Layout the table of additional properties and any arguments they
        need"""
        self.logger.debug("Properties::layout_properties")

        frame = self.innerframe

        # Unpack any widgets
        for slave in frame.grid_slaves():
            slave.grid_forget()

        # Callbacks
        if self._set_property_cb is None:
            self._set_property_cb = frame.register(self.set_property_cb)

        row = -1
        for d in self._working_properties:
            self.logger.debug(d)
            row += 1
            _property = d["property"]
            if "widgets" not in d:
                widgets = d["widgets"] = {}
            else:
                widgets = d["widgets"]

            if "remove" not in widgets:
                # The button to remove a row...
                widgets["remove"] = ttk.Button(
                    frame,
                    text="-",
                    width=2,
                    command=lambda row=row: self.remove_property(row),
                    takefocus=True,
                )

            if "name" not in widgets:
                # the name of the property
                widgets["name"] = ttk.Label(
                    frame, width=self._max_width, text=_property
                )
                widgets["plusminus"] = ttk.Label(frame, text="±")
                # and desired accuracy
                widgets["accuracy"] = sw.UnitEntry(frame)
                if "accuracy" in d:
                    accuracy, units = d["accuracy"]
                else:
                    units = self._metadata[_property]["units"]
                    if "accuracy" in self._metadata[_property]:
                        accuracy = self._metadata[_property]["accuracy"]
                    else:
                        accuracy = "0.1%"
                widgets["accuracy"].set(accuracy, units)

            self.logger.debug("  widgets: " + str(widgets))
            widgets["remove"].grid(row=row, column=0, sticky=tk.W)
            col = 1
            widgets["name"].grid(row=row, column=col, stick=tk.EW)
            col += 1
            widgets["plusminus"].grid(row=row, column=col, stick=tk.EW)
            col += 1
            widgets["accuracy"].grid(row=row, column=col, stick=tk.EW)
            col += 1

        # The button to add a row...
        row += 1
        if self._add_widget is None:
            self._add_widget = ttk.Button(
                frame,
                text="+",
                width=5,
                command=self.add_property,
                takefocus=True,
            )
            self._add_widget.focus_set()
        self._add_widget.lift()
        self._add_widget.grid(row=row, column=0, columnspan=3, sticky=tk.W)

        frame.grid_columnconfigure(2, weight=1)

    def get(self):
        """Get the values of the properties from the widgets"""
        self.logger.debug("Properties::get_properties")

        properties = []
        for d in self._working_properties:
            widgets = d["widgets"]
            _property = widgets["name"].cget("text")
            accuracy = widgets["accuracy"].get()

            properties.append((_property, accuracy))

        return properties

    def set_property_cb(self, _property):
        self.logger.debug("Properties::set_property_cb")
        self.logger.debug(_property)

        self._working_properties.append({"property": _property})
        self.layout_properties()

    def add_property(self, _property=""):
        """Add a property to the input"""
        # Post a menu with the choices
        popup_menu = tk.Menu(self.innerframe, tearoff=0)
        current = []
        for d, _ in self.properties:
            current.append(d)

        for _property in self._metadata:
            if _property not in current:
                description = self._metadata[_property]["description"]
                popup_menu.add_command(
                    label="{}: {}".format(_property, description),
                    command=(self._set_property_cb, _property),
                )
        x, y = self.winfo_pointerxy()
        popup_menu.tk_popup(x, y, 0)

    def remove_property(self, row=None):
        """Remove a property from dd to input"""
        self.logger.debug("remove row {}".format(row))
        for widget in self._working_properties[row]["widgets"].values():
            widget.destroy()
        del self._working_properties[row]
        self.layout_properties()


if __name__ == "__main__":  # pragma: no cover
    import sys

    metadata = {
        "T": {
            "calculation": [
                "nve",
                "nvt",
                "npt",
            ],
            "description": "temperature",
            "dimensionality": "scalar",
            "type": "float",
            "units": "K",
            "accuracy": "2.0",
        },
        "P": {
            "calculation": [
                "nve",
                "nvt",
                "npt",
            ],
            "description": "pressure",
            "dimensionality": "scalar",
            "type": "float",
            "units": "atm",
        },
        "density": {
            "calculation": [
                "nve",
                "nvt",
                "npt",
            ],
            "description": "pressure",
            "dimensionality": "scalar",
            "type": "float",
            "units": "g/ml",
        },
        "a": {
            "calculation": [
                "nve",
                "nvt",
                "npt",
            ],
            "description": "cell parameter 'a'",
            "dimensionality": "scalar",
            "type": "float",
            "units": "Å",
        },
        "b": {
            "calculation": [
                "nve",
                "nvt",
                "npt",
            ],
            "description": "cell parameter 'b'",
            "dimensionality": "scalar",
            "type": "float",
            "units": "Å",
        },
        "c": {
            "calculation": [
                "nve",
                "nvt",
                "npt",
            ],
            "description": "cell parameter 'c'",
            "dimensionality": "scalar",
            "type": "float",
            "units": "Å",
        },
        "Etot": {
            "calculation": [
                "nve",
                "nvt",
                "npt",
            ],
            "description": "total energy",
            "dimensionality": "scalar",
            "type": "float",
            "units": "kcal/mol",
        },
        "Eke": {
            "calculation": [
                "nve",
                "nvt",
                "npt",
            ],
            "description": "kinetic energy",
            "dimensionality": "scalar",
            "type": "float",
            "units": "kcal/mol",
        },
        "Epe": {
            "calculation": [
                "nve",
                "nvt",
                "npt",
            ],
            "description": "potential energy",
            "dimensionality": "scalar",
            "type": "float",
            "units": "kcal/mol",
        },
        "Epair": {
            "calculation": [
                "nve",
                "nvt",
                "npt",
            ],
            "description": "nonbonded (vdW & electrostatic) energy",
            "dimensionality": "scalar",
            "type": "float",
            "units": "kcal/mol",
        },
    }

    # Helper to print the current properties
    def print_properties(*args):
        print(w.get())

    def print_focus(*args):
        print(root.focus_get())

    def handle_dialog(result):
        dialog.deactivate(result)
        if result == "OK":
            properties = w.get()
            print("OK")
            print(properties)
            w.properties = properties
        else:
            w.reset()
            print("Cancel")
            print(w.properties)

    ##################################################
    # Initialize Tk
    ##################################################
    if sys.platform.startswith("darwin"):
        CmdKey = "Command-"
    else:
        CmdKey = "Control-"

    #    logging.basicConfig(level=10)
    #    module_logger.critical('Turned on debugging!')
    #    module_logger.setLevel('DEBUG')
    #    module_logger.setLevel(10)
    #    print(module_logger.getEffectiveLevel())
    #    module_logger.debug('Turned on debugging!')

    root = tk.Tk()
    Pmw.initialise(root)

    dialog = Pmw.Dialog(
        root,
        buttons=("OK", "Cancel"),
        defaultbutton=None,
        master=root,
        title="Add property",
        command=handle_dialog,
    )
    dialog.geometry("500x400")

    properties = [("P", (0.003, "atm"))]

    w = PropertyTable(dialog.interior(), metadata)
    w.properties = properties
    w.pack(expand="yes", fill="both")

    root.bind_all("<" + CmdKey + "P>", print_properties)
    root.bind_all("<" + CmdKey + "p>", print_properties)
    root.bind_all("<" + CmdKey + "f>", print_focus)

    exit_button = ttk.Button(root, text="Exit", command=exit)
    post_button = ttk.Button(root, text="Edit Properties", command=dialog.activate)
    post_button.grid(column=0, row=0)
    exit_button.grid(column=1, row=0)

    dialog.activate(geometry="centerscreenfirst")

    # enter the event loop
    root.mainloop()
