=====
Usage
=====

To use the SEAMM Widgets in a project::

    import seamm_widgets

Tooltips
--------

Every labeled widget (``LabeledEntry``, ``LabeledCombobox``, ``UnitEntry``,
``UnitCombobox``, ``LabeledText``, ``BasisSetField``, ...) can show help text when
the pointer rests on it, on either the label or the field::

    w = seamm_widgets.LabeledEntry(frame, labeltext="Basis:", tooltip="The orbital basis set.")
    w.tooltip = "Changed help text."      # or w.configure(tooltip=...)

The tip appears after the pointer has rested on the widget for 0.6 s and disappears when
the pointer leaves, a mouse button is pressed or the widget is destroyed. The text is
reflowed: common indentation and line breaks within a paragraph are removed, and blank
lines separate paragraphs. Any other Tk widget can have a tip with
``seamm_widgets.Tooltip(widget, text)``.

SEAMM's ``Parameter.widget()`` sets each parameter's ``help_text`` as the tooltip of the
widget it creates, so the step dialogs show it without further code.
