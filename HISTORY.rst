=======
History
=======
2026.9.25 -- A labeled multi-line text widget
    * Added LabeledText, a labeled, scrollable multi-line text box with the same
      label/get/set/show interface as LabeledEntry, for free-form input such as a
      verbatim block of keywords for a code. Used by the ORCA plug-in for its extra
      input blocks.

2026.9.18 -- Bugfix: pip metadata lacked requests
    * ``pip install seamm-widgets`` did not install ``requests``, which the HTML
      widgets import, so seamm-widgets failed to import outside a conda-forge
      environment (whose recipe already listed it). It is now an install requirement.

2026.6.28 -- A Basis Set Exchange basis-set picker
    * Added BasisSetField, a basis-set name field with a '...' button, and
      BasisSetSelector, the dialog it opens: a periodic table to choose the
      elements of interest, narrowing a searchable list to the basis sets that
      cover all of them. A choice is returned as 'bse:NAME'.
    * Shared by the quantum-chemistry plug-ins (ORCA, Gaussian, Psi4, ...). The
      Basis Set Exchange is loaded only when the picker is opened, so the package
      gains no required dependency on it.

2026.2.26 -- Internal: moving from pkg_resources to importlib.resources

2025.10.22 -- Enhancement for extra keywords
    * Small enhancement to the GUI code to allow a code, such as VASP, that always has
      keyword = value to let the extra keywords tab know there will always be a value.

2025.10.15 -- Bugfix: Fixed error with labels on labeled entries
    * The label for labeled entries was not displayed. This fixes this.
      
2025.9.20 -- Bugfix: Fixed error typing into entry widgets
    * The last release inadvertently caused issues with the bindings for the entry
      widgets, which made it impossible to type text into them. This is fixed.
      
2025.9.10 -- Bugfix: options such as width not correctly applied
    * The handling of options for widgets was not robust. This is now fixed and options
      are applied as requested.
      
2025.8.27 -- Bugfix: fixed an error showing selected subwidgets of compound widgets
    * The compound widgets 'show' methods did not correctly display the requested
      subwidgets.

2024.10.10 -- Enhancement: Added state method for some widgets
    * Added a state method to LabeledWidget, LabeledComboBox, LabeledEntry, UnitEntry
      and UnitComboBox. This method sets or returns the state of the widget

2024.7.21 -- Return the width of aligned labels
    * The align_labels procedure now returns the width of the labels. This is useful for
      laying out indented widgets.
      
2024.5.1 -- Enhancement to ScrolledColumns
    * Added optional separator columns for dividing sections of the table.
      
2022.10.28 -- Bugfix: problem deleting 2 or more keywords
  There was a crash if you deleted a second keyword in the Keywords tab of
  calculation.

0.1.0 (2019-04-02)
  * First release on PyPI.
