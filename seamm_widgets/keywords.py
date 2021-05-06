# -*- coding: utf-8 -*-

"""A Tk scrolled frame containing and handling keywords.

This megawidget displays a list of keywords that the user can add to and also
delete. It provides tab completion as the user types, highlights incorrect
keywords in red and generally helps the user find the keywords they wish.
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


class Keywords(sw.ScrolledFrame):
    """A widget to handle manual input of keywords with optional values"""

    def __init__(
        self,
        master,
        metadata=None,
        keywords="",
        width=None,
        anchor=tk.N,
        height=None,
        mousewheel_speed=2,
        scroll_horizontally=True,
        xscrollbar=None,
        scroll_vertically=True,
        yscrollbar=None,
        background=None,
        logger=module_logger,
        **kwargs
    ):
        """ """
        self.logger = logger
        self._keywords = ""
        self._max_width = 0
        self._working_keywords = None
        self._add_widget = None
        self._dialog = None
        self.keyword_cb = None
        self.value_cb = None
        self.set_keyword_cb = None
        self.popup_menu = None

        class_ = kwargs.pop("class_", "MKeywords")

        s = ttk.Style()
        s.configure("Red.TEntry", foreground="red")

        super().__init__(
            master,
            class_=class_,
            width=width,
            anchor=anchor,
            height=height,
            mousewheel_speed=mousewheel_speed,
            scroll_horizontally=scroll_horizontally,
            xscrollbar=xscrollbar,
            scroll_vertically=scroll_vertically,
            yscrollbar=yscrollbar,
            background=background,
            inner_frame=ttk.Frame,
            **kwargs
        )

        # After everything is set up can put in the keywords and metadata
        self.metadata = metadata
        if keywords != "":
            self.keywords = keywords

    @property
    def keywords(self):
        """The current keywords, reflecting changes in the widgets"""
        result = []
        for d in self._working_keywords:
            result.append(d["keyword"])
        return result

    @keywords.setter
    def keywords(self, value):
        self.logger.debug("Keywords::keywords: " + str(value))
        self.clear()
        self._working_keywords = []
        self._keywords = value
        if value is not None:
            for keyword in value:
                if "=" in keyword:
                    keyword, value = keyword.split("=")
                    self._working_keywords.append({"keyword": keyword, "value": value})
                else:
                    self._working_keywords.append({"keyword": keyword})
        self.logger.debug("  keywords.setter call layout_keywords")
        self.layout_keywords()

    @property
    def metadata(self):
        """The current metadata"""
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        self._metadata = value
        self._max_width = 0
        if value is not None:
            for keyword in self._metadata.keys():
                width = len(keyword)
                if width > self._max_width:
                    self._max_width = width
            self._max_width += 3  # a little padding...
            self.keywords = self._keywords

    def clear(self):
        """Remove the widgets."""
        if self._working_keywords is not None:
            for d in self._working_keywords:
                if "widgets" in d:
                    for widget in d["widgets"].values():
                        widget.destroy()
                    del d["widgets"]

    def reset(self):
        """Remove any changes made in the dialog."""
        self.keywords = self._keywords

    def layout_keywords(self):
        """Layout the table of additional keywords and any arguments they
        need"""
        self.logger.debug("Keywords::layout_keywords")

        frame = self.innerframe

        # Unpack any widgets
        for slave in frame.grid_slaves():
            slave.grid_forget()

        # Callbacks
        if self.keyword_cb is None:
            self.keyword_cb = frame.register(self.handle_keyword)
        if self.value_cb is None:
            self.value_cb = frame.register(self.validate_keyword_value)
        if self.set_keyword_cb is None:
            self.set_keyword_cb = frame.register(self.set_keyword)

        row = -1
        for d in self._working_keywords:
            self.logger.debug(d)
            row += 1
            keyword = d["keyword"]
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
                    command=lambda row=row: self.remove_keyword(row),
                    takefocus=True,
                )

            if "entry" not in widgets:
                # the name of the keyword
                widgets["entry"] = ttk.Entry(
                    frame,
                    width=self._max_width,
                    validate="key",
                    validatecommand=(
                        self.keyword_cb,
                        keyword,
                        row,
                        "%W",
                        "%P",
                        "%s",
                        "%d",
                        "%S",
                    ),
                    takefocus=True,
                    style="Red.TEntry",
                )
                widgets["entry"].bind(
                    "<KeyPress-Tab>",
                    lambda event=None, row=row: self.handle_tab(event, row),
                )
                widgets["entry"].insert("end", keyword)

            self.logger.debug("  widgets: " + str(widgets))
            widgets["remove"].grid(row=row, column=0, sticky=tk.W)
            col = 1
            widgets["entry"].grid(row=row, column=col, stick=tk.EW)
            col += 1

            if keyword == "":
                continue

            if keyword not in self._metadata:
                # See if it is a unique prefix
                possible_keywords = []
                for trial in self._metadata:
                    if trial.startswith(keyword):
                        possible_keywords.append(trial)
                if len(possible_keywords) == 1:
                    keyword = possible_keywords[0]

            if keyword not in self._metadata:
                continue
            definition = self._metadata[keyword]
            if "takes values" in definition:
                if "value" not in d:
                    d["value"] = definition["default"]

                if "value" not in widgets:
                    widgets["value"] = ttk.Entry(
                        frame,
                        width=20,
                        validate="key",
                        validatecommand=(
                            self.value_cb,
                            keyword,
                            "%W",
                            "%P",
                            "%s",
                            "%d",
                            "%S",
                        ),
                        takefocus=True,
                    )
                    widgets["value"].insert("end", d["value"])
                    widgets["value"].focus_set()

                widgets["value"].grid(row=row, column=col, sticky=tk.EW)

        # The button to add a row...
        row += 1
        if self._add_widget is None:
            self._add_widget = ttk.Button(
                frame,
                text="+",
                width=5,
                command=self.add_keyword,
                takefocus=True,
            )
            self._add_widget.focus_set()
        self._add_widget.lift()
        self._add_widget.grid(row=row, column=0, columnspan=3, sticky=tk.W)

        frame.grid_columnconfigure(2, weight=1)

    def get_keywords(self):
        """Get the values of the keywords from the widgets"""
        self.logger.debug("Keywords::get_keywords")

        keywords = []
        for d in self._working_keywords:
            widgets = d["widgets"]
            keyword = widgets["entry"].get()

            if keyword not in self._metadata:
                # See if it is a unique prefix
                possible_keywords = []
                for trial in self._metadata:
                    if trial.startswith(keyword):
                        possible_keywords.append(trial)
                if len(possible_keywords) == 1:
                    keyword = possible_keywords[0]

            if keyword in self._metadata:
                definition = self._metadata[keyword]
                if "takes values" in definition:
                    value = widgets["value"].get().strip()
                    if value == "":
                        keywords.append(keyword)
                    else:
                        keywords.append(format(definition["format"], keyword, value))
                else:
                    keywords.append(keyword)

        return keywords

    def handle_keyword(self, keyword, row, w_name, value, before, action, changed):
        """Handle typing in a combobox for the keyword

        Arguments:
            keyword: the MOPAC keyword
            w_name: the widget name
            value: the value *after* the keystroke
            before: the value before the keystroke
            action: 0 for deletion, 1 for insertion
            changed: the text being inserted or deleted
        """

        self.logger.debug("Keywords::handle_keyword")
        w = self.nametowidget(w_name)  # nopep8
        self.logger.debug("Validating the keyword")

        if changed == "\t":
            changed = "TAB"
        self.logger.debug("\tkeyword: {}".format(keyword))
        self.logger.debug("\t    row: {}".format(row))
        self.logger.debug("\t  value: {}".format(value))
        self.logger.debug("\t before: {}".format(before))
        self.logger.debug("\t action: {}".format(action))
        self.logger.debug("\tchanged: {}".format(changed))

        d = self._working_keywords[int(row)]
        self.logger.debug("\tmetadata: " + str(d))
        d["keyword"] = value

        if value in self._metadata:
            w.configure(style="TEntry")
            self.layout_keywords()
        else:
            w.configure(style="Red.TEntry")

        return True

    def post_cb(self, row):
        """Handle post command for the combobox 'w'

        Arguments:
            w_name: the name of the widget (from %W)
        """

        w = self["keyword_" + str(row)]
        current = w.get().upper()

        keywords = []
        for keyword in self._metadata:
            if keyword.startswith(current):
                keywords.append(keyword)

        w.configure(values=sorted(keywords))

    def set_keyword_cb(self, event, w, row=None):
        self.logger.debug("Keywords::set_keyword_cb")
        self.logger.debug(event)
        self.logger.debug(w)
        self.logger.debug(w.get())
        self.logger.debug(row)

    def add_keyword(self, keyword=""):
        """Add a keyword to the input"""
        self._working_keywords.append({"keyword": keyword})
        self.layout_keywords()
        d = self._working_keywords[-1]
        d["widgets"]["entry"].focus_set()

    def post_keyword_dialog(self):
        """Put up the dialog with the appropriate list of keywords"""
        if self._dialog is None:
            """Create the dialog!"""
            self._dialog = Pmw.Dialog(
                self.toplevel,
                buttons=("OK", "Help", "Cancel"),
                defaultbutton="OK",
                master=self._dialog,
                title="Add keyword",
                command=self.handle_keyword_dialog,
            )
            self._dialog.withdraw()
            frame = ttk.Frame(self._dialog.interior())
            frame.pack(expand=tk.YES, fill=tk.BOTH)
            self["keyword frame"] = frame

            w = self["keyword tree"] = ttk.Treeview(
                frame,
                columns=("Keyword", "Description"),
            )
            w.pack(expand=tk.YES, fill=tk.BOTH)

            w.heading("Keyword", text="Keyword")
            w.heading("Description", text="Description")
            w.column("#0", minwidth=1, width=1, stretch=False)
            w.column("Keyword", width=100, stretch=False)

            for keyword in self._metadata:
                description = self._metadata[keyword]["description"]
                w.insert("", "end", iid=keyword, values=(keyword, description))

        self._dialog.activate(geometry="centerscreenfirst")

    def handle_keyword_dialog(self, result):
        if result is None or result == "Cancel":
            self._dialog.deactivate(result)
            return

        if result == "Help":
            # display help!!!
            return

        if result != "OK":
            self._dialog.deactivate(result)
            raise RuntimeError("Don't recognize dialog result '{}'".format(result))

        self._dialog.deactivate(result)

        keyword = self["keyword tree"].selection()
        self.logger.debug(keyword)

    def validate_keyword_value(self, keyword, w_name, value, before, action, changed):
        """Handle typing in a combobox for the keyword

        Arguments:
            keyword: the MOPAC keyword
            w_name: the widget name
            value: the value *after* the keystroke
            before: the value before the keystroke
            action: 0 for deletion, 1 for insertion
            changed: the text being inserted or deleted
        """

        # w = self._dialog.nametowidget(w_name)
        self.logger.debug("Validating the value of a keyword")
        self.logger.debug("\tkeyword: {}".format(keyword))
        self.logger.debug("\t  value: {}".format(value))
        self.logger.debug("\t before: {}".format(before))
        self.logger.debug("\t action: {}".format(action))
        self.logger.debug("\tchanged: {}".format(changed))

        return True

    def remove_keyword(self, row=None):
        """Remove a keyword from dd to input"""
        self.logger.debug("remove row {}".format(row))
        for widget in self._working_keywords[row]["widgets"].values():
            widget.destroy()
        del self._working_keywords[row]
        self.layout_keywords()

    def handle_tab(self, event=None, row=None):
        """Handle a tab in a keyword entry field"""
        self.logger.debug("Caught tab in row {}".format(row))
        self.logger.debug(event)

        data = self._working_keywords[row]
        w = data["widgets"]["entry"]
        current = w.get()

        defs = self._metadata
        keywords = []
        for keyword in defs:
            if keyword.startswith(current):
                keywords.append(keyword)

        prefix = lcp(*keywords)
        self.logger.debug('prefix = "{}", current = "{}"'.format(prefix, current))

        if prefix != current:
            w.delete(0, "end")
            w.insert("end", prefix)
            data["keyword"] = prefix
            if prefix in defs:
                w.configure(style="TEntry")
                self.layout_keywords()
                w.tk_focusNext().focus()
        else:
            if len(keywords) == 1:
                w.tk_focusNext().focus()
            else:
                if self.popup_menu is not None:
                    self.popup_menu.destroy()

                self.popup_menu = tk.Menu(self.innerframe, tearoff=0)
                for keyword in keywords:
                    description = defs[keyword]["description"]
                    self.popup_menu.add_command(
                        label="{}: {}".format(keyword, description),
                        command=(self.set_keyword_cb, w, keyword, row),
                    )
                    x, y = w.winfo_pointerxy()
                self.popup_menu.tk_popup(x, y, 0)
        return "break"

    def set_keyword(self, w_name, keyword, row):
        """Set the value in a widget to the full keyword"""
        w = self.nametowidget(w_name)
        w.delete(0, "end")
        w.insert("end", keyword)
        d = self._working_keywords[int(row)]
        d["keyword"] = keyword
        w.configure(style="TEntry")
        self.layout_keywords()
        w.tk_focusNext().focus()


if __name__ == "__main__":  # pragma: no cover
    import sys

    metadata = {
        "0SCF": {
            "description": "Read in data, then stop",
        },
        "1ELECTRON": {
            "description": "Print final one-electron matrix",
        },
        "1SCF": {
            "description": "Do one scf and then stop",
        },
        "ADD-H": {
            "description": (
                "Add hydrogen atoms (intended for use with " "organic compounds)"
            ),
        },
        "A0": {
            "description": "Input geometry is in atomic units",
        },
        "AIDER": {
            "description": "Read in ab-initio derivatives",
        },
        "AIGIN": {
            "description": "Geometry must be in Gaussian format",
        },
        "AIGOUT": {
            "description": ("Print the geometry in Gaussian format in the ARC " "file"),
        },
        "ALLBONDS": {
            "description": (
                "Print final bond-order matrix, including bonds " "to hydrogen"
            ),
        },
        "ALLVEC": {
            "description": "Print all vectors (keywords vectors also needed)",
        },
        "ALT_A": {
            "description": ("In PDB files with alternative atoms, select " "atoms A"),
            "takes values": 1,
            "default": "A",
        },
        "ANGSTROMS": {
            "description": "Input geometry is in Angstroms",
        },
        "AUTOSYM": {
            "description": "Symmetry to be imposed automatically",
        },
        "AUX": {
            "description": (
                "Output auxiliary information for use by other " "programs"
            ),
        },
        "AM1": {
            "description": "Use the AM1 hamiltonian",
        },
        "BAR": {
            "description": "reduce bar length by a maximum of n.nn%",
            "takes values": 1,
            "default": "0.01",
        },
    }

    # Helper to print the current keywords
    def print_keywords(*args):
        print(w.get_keywords())

    def print_focus(*args):
        print(root.focus_get())

    def handle_dialog(result):
        dialog.deactivate(result)
        if result == "OK":
            keywords = w.get_keywords()
            print("OK")
            print(keywords)
            w.keywords = keywords
        else:
            w.reset()
            print("Cancel")
            print(w.keywords)

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
        title="Add keyword",
        command=handle_dialog,
    )
    dialog.geometry("500x400")

    keywords = ["BAR"] * 10

    w = Keywords(dialog.interior(), metadata)
    w.keywords = keywords
    w.pack(expand="yes", fill="both")

    root.bind_all("<" + CmdKey + "P>", print_keywords)
    root.bind_all("<" + CmdKey + "p>", print_keywords)
    root.bind_all("<" + CmdKey + "f>", print_focus)

    exit_button = ttk.Button(root, text="Exit", command=exit)
    post_button = ttk.Button(root, text="Edit Keywords", command=dialog.activate)
    post_button.grid(column=0, row=0)
    exit_button.grid(column=1, row=0)

    dialog.activate(geometry="centerscreenfirst")

    # enter the event loop
    root.mainloop()
