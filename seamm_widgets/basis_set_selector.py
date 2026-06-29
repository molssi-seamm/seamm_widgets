# -*- coding: utf-8 -*-

"""A dialog for choosing a basis set from the Basis Set Exchange (BSE).

The user picks the elements their calculations need on a periodic table; the list
is narrowed to the basis sets that cover *all* of those elements, so a single
basis can be chosen that works for every compound of interest. A text filter
helps when the list is long.

This widget is shared by the quantum-chemistry plug-ins (ORCA, Gaussian, Psi4,
...). It returns the basis-set name; callers typically store it as ``bse:NAME``
so the consuming code fetches that exact definition from the Exchange.

The Basis Set Exchange package is imported lazily (only when the dialog is
actually opened), so ``seamm_widgets`` carries no hard dependency on it -- the
quantum-chemistry plug-ins that use this dialog provide it.
"""

import logging
import tkinter as tk
from tkinter import ttk

import Pmw

from seamm_util import element_data
from seamm_widgets.labeled_widget import LabeledWidget
from seamm_widgets.periodic_table import PeriodicTable

module_logger = logging.getLogger(__name__)

# Element symbol -> atomic number, for translating periodic-table picks to the
# atomic numbers the BSE metadata uses.
_symbol_to_z = {sym: d["atomic number"] for sym, d in element_data.items()}


def orbital_basis_metadata():
    """The Basis Set Exchange metadata for the orbital basis sets, by name.

    Auxiliary/fitting sets (jfit, rifit, ...) are excluded -- only the orbital
    basis sets a user selects as "the basis" are returned. ``basis_set_exchange``
    is imported here (lazily) so importing this module does not require it.
    """
    import basis_set_exchange as bse

    md = bse.get_metadata()
    return {
        name: info
        for name, info in md.items()
        if info.get("role", "orbital") == "orbital"
    }


def _covered_elements(info):
    """The set of atomic numbers covered by a BSE metadata entry."""
    versions = info.get("versions", {})
    if not versions:
        return set()
    latest = info.get("latest_version")
    version = versions.get(str(latest))
    if version is None:
        version = versions[sorted(versions)[-1]]
    return {int(z) for z in version.get("elements", [])}


def filter_basis_names(metadata, elements=(), search=""):
    """Display names of basis sets covering all `elements` and matching `search`.

    Parameters
    ----------
    metadata : dict
        BSE metadata keyed by basis name (e.g. from `orbital_basis_metadata`).
    elements : iterable of str
        Element symbols the basis must *all* cover. Empty means no element
        filter.
    search : str
        Case-insensitive substring matched against the display name (and family).

    Returns
    -------
    list of str
        Matching display names, sorted case-insensitively.
    """
    zset = {_symbol_to_z[s] for s in elements if s in _symbol_to_z}
    needle = search.strip().lower()
    names = []
    for name, info in metadata.items():
        if zset and not zset <= _covered_elements(info):
            continue
        display = info.get("display_name", name)
        family = info.get("family", "") or ""
        if needle and needle not in display.lower() and needle not in family.lower():
            continue
        names.append(display)
    return sorted(names, key=str.lower)


class BasisSetSelector:
    """A modal dialog for choosing a basis set from the Basis Set Exchange.

    Create once, then call :meth:`ask` (optionally with elements to preselect)
    each time you need a choice; it returns the chosen basis-set display name, or
    ``None`` if cancelled.

    Example (pseudo-code; needs a Tk parent and a display)::

        selector = BasisSetSelector(parent)
        name = selector.ask(elements=["C", "H", "O"])
    """

    def __init__(
        self,
        master,
        title="Select a basis set from the Basis Set Exchange",
        logger=module_logger,
    ):
        self.logger = logger
        self._metadata = None  # loaded lazily on first ask()
        self._result = None

        self.dialog = Pmw.Dialog(
            master,
            buttons=("OK", "Cancel"),
            defaultbutton="OK",
            title=title,
            command=self._handle,
        )
        self.dialog.withdraw()
        interior = self.dialog.interior()

        ttk.Label(
            interior,
            text=(
                "Select the elements your calculations need. The list shows the "
                "basis sets that cover all of them; type to filter further."
            ),
            wraplength=620,
            justify=tk.LEFT,
        ).grid(row=0, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=(5, 8))

        self._periodic_table = PeriodicTable(interior, command=self._on_elements)
        self._periodic_table.grid(
            row=1, column=0, columnspan=2, sticky=tk.NSEW, padx=5, pady=5
        )

        ttk.Label(interior, text="Filter:").grid(row=2, column=0, sticky=tk.E)
        self._search = tk.StringVar()
        self._search.trace_add("write", lambda *args: self._refilter())
        ttk.Entry(interior, textvariable=self._search, width=30).grid(
            row=2, column=1, sticky=tk.W, padx=5, pady=2
        )

        listframe = ttk.Frame(interior)
        listframe.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW, padx=5, pady=5)
        self._listbox = tk.Listbox(
            listframe, height=12, width=44, exportselection=False
        )
        scrollbar = ttk.Scrollbar(
            listframe, orient=tk.VERTICAL, command=self._listbox.yview
        )
        self._listbox.configure(yscrollcommand=scrollbar.set)
        self._listbox.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self._listbox.bind("<Double-Button-1>", lambda event: self._handle("OK"))

        listframe.columnconfigure(0, weight=1)
        listframe.rowconfigure(0, weight=1)
        interior.columnconfigure(1, weight=1)
        interior.rowconfigure(3, weight=1)

    def ask(self, elements=(), current=None):
        """Show the dialog modally; return ``(name, elements)`` (or ``(None, None)``
        if cancelled).

        Parameters
        ----------
        elements : iterable of str
            Element symbols to preselect on the periodic table (e.g. those used
            last time, or the current system's), narrowing the initial list.
        current : str, optional
            A basis display name to highlight in the list (the current choice).

        Returns
        -------
        tuple
            ``(basis_name, [element_symbols])`` chosen on OK, else ``(None, None)``.
        """
        if self._metadata is None:
            self._metadata = orbital_basis_metadata()
        self._periodic_table.set(list(elements) if elements else [])
        self._refilter()
        if current:
            items = self._listbox.get(0, tk.END)
            if current in items:
                index = items.index(current)
                self._listbox.selection_clear(0, tk.END)
                self._listbox.selection_set(index)
                self._listbox.see(index)
        self._result = (None, None)
        self.dialog.activate()  # modal; blocks until _handle deactivates
        return self._result

    def _on_elements(self, selected):
        """Periodic-table callback: re-narrow the list to the selected elements."""
        self._refilter()

    def _refilter(self):
        if self._metadata is None:
            return
        names = filter_basis_names(
            self._metadata, self._periodic_table.get(), self._search.get()
        )
        self._listbox.delete(0, tk.END)
        for name in names:
            self._listbox.insert(tk.END, name)

    def _handle(self, result):
        if result == "OK":
            selection = self._listbox.curselection()
            name = self._listbox.get(selection[0]) if selection else None
            self._result = (name, self._periodic_table.get()) if name else (None, None)
        else:
            self._result = (None, None)
        self.dialog.deactivate(result)


class BasisSetField(LabeledWidget):
    """A labeled basis-set name field with a ``...`` button.

    The field is an editable combobox: type a name the quantum-chemistry code
    knows internally (e.g. ``def2-TZVP``), or pick one of the ``values`` a code
    offers as quick choices. Pressing ``...`` opens a :class:`BasisSetSelector`;
    the chosen basis is written back as ``bse:NAME``, which forces that exact
    Basis Set Exchange definition (the consuming code fetches it from the
    Exchange). When no ``values`` are given it behaves as a plain entry + button.

    To preselect the current system's elements in the dialog, set
    :attr:`elements_callback` to a function returning their symbols.

    The value is a dict ``{"name": <basis>, "elements": [<symbols>]}`` -- the
    elements are remembered so the dialog can be reconstructed (the periodic-table
    selection restored, the basis re-highlighted) on reopen. ``set`` also accepts
    a plain string (a name with no remembered elements) for backward
    compatibility, and ``get`` always returns the dict.
    """

    def __init__(self, parent, *args, **kwargs):
        width = kwargs.pop("width", 20)
        state = kwargs.pop("state", "normal")
        values = kwargs.pop("values", ())
        class_ = kwargs.pop("class_", "MBasisSetField")
        super().__init__(parent, class_=class_, *args, **kwargs)

        #: A callable returning element symbols to preselect in the dialog.
        self.elements_callback = None
        self._selector = None
        self._elements = []  # remembered element selection, for reconstruction

        interior = self.interior
        self.combobox = ttk.Combobox(
            interior, width=width, state=state, values=list(values)
        )
        self.combobox.grid(row=0, column=0, sticky=tk.EW)
        self.button = ttk.Button(interior, text="...", width=3, command=self._browse)
        self.button.grid(row=0, column=1, sticky=tk.W, padx=(2, 0))
        interior.columnconfigure(0, weight=1)

    def _browse(self):
        """Open the Basis Set Exchange selector and store the choice as bse:NAME,
        remembering the elements selected so the dialog can be reconstructed."""
        if self._selector is None:
            self._selector = BasisSetSelector(self.winfo_toplevel())
        # Reopen with the remembered elements, else the current system's.
        elements = list(self._elements)
        if not elements and self.elements_callback is not None:
            try:
                elements = list(self.elements_callback() or [])
            except Exception as e:  # pragma: no cover - preselection is best-effort
                module_logger.debug(f"elements_callback failed: {e}")
                elements = []
        current = self.combobox.get()
        if current.lower().startswith("bse:"):
            current = current[4:]
        name, selected = self._selector.ask(elements=elements, current=current)
        if name:
            self._elements = list(selected)
            self.combobox.delete(0, tk.END)
            self.combobox.insert(0, f"bse:{name}")

    @property
    def value(self):
        return self.get()

    @value.setter
    def value(self, value):
        self.set(value)

    def set(self, value):
        """Set the field from a dict ``{"name", "elements"}`` or a plain name."""
        if isinstance(value, dict):
            name = value.get("name", "") or ""
            self._elements = list(value.get("elements", []) or [])
        else:
            name = "" if value is None else str(value)
            self._elements = []
        self.combobox.delete(0, tk.END)
        self.combobox.insert(0, name)

    def get(self):
        """Return ``{"name": <text>, "elements": [<symbols>]}``."""
        return {"name": self.combobox.get(), "elements": list(self._elements)}

    def get_name(self):
        """Return just the basis name (convenience for callers that ignore the
        remembered elements)."""
        return self.combobox.get()

    def config(self, **kwargs):
        """Pass ``state``/``values`` to the combobox; everything else to parent."""
        for key in ("state", "values"):
            if key in kwargs:
                self.combobox.config(**{key: kwargs.pop(key)})
        if kwargs:
            super().config(**kwargs)

    def configure(self, **kwargs):
        return self.config(**kwargs)
