=======
History
=======
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
