# -*- coding: utf-8 -*-
"""Tests for the Tooltip and the tooltip option of the labeled widgets. The
widget tests are skipped where Tk cannot open a display."""

import tkinter as tk

import pytest

import seamm_widgets as sw


@pytest.fixture
def root():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("no display available for Tk")
    root.withdraw()
    yield root
    root.destroy()


def test_reflow():
    text = """
        The orbital basis set. Type a name
        or pick one from the list.

        A second paragraph.
    """
    assert sw.reflow(text) == (
        "The orbital basis set. Type a name or pick one from the list."
        "\n\nA second paragraph."
    )
    assert sw.reflow("  one   line  ") == "one line"


def test_tooltip_option(root):
    w = sw.LabeledEntry(root, labeltext="Basis:", tooltip="The   basis set.")
    assert w.tooltip == "The basis set."
    w.configure(tooltip="Another\n  text.")
    assert w.tooltip == "Another text."
    plain = sw.LabeledEntry(root, labeltext="Basis:")
    assert plain.tooltip == ""
    plain.tooltip = "Now with help."
    assert plain.tooltip == "Now with help."


def test_tooltip_show_and_hide(root, monkeypatch):
    root.deiconify()
    w = sw.LabeledCombobox(
        root, labeltext="Method:", values=["a", "b"], tooltip="Pick a method."
    )
    w.pack()
    root.update()
    tip = w._tooltip
    # The pointer is wherever the tester left it, so pretend it is inside
    monkeypatch.setattr(tip, "_pointer_inside", lambda: True)

    tip.show()
    assert tip._window is not None
    assert tip._window.label.cget("text") == "Pick a method."

    # Leaving to a child of the widget keeps the tip
    tip._on_leave()
    assert tip._window is not None

    # A click hides it (on the frame: a click on the combobox would post its list)
    w.event_generate("<ButtonPress-1>")
    assert tip._window is None

    # Leaving the widget cancels a pending tip
    tip._on_enter()
    assert tip._after_id is not None
    monkeypatch.setattr(tip, "_pointer_inside", lambda: False)
    tip._on_leave()
    assert tip._after_id is None and tip._window is None


def test_tooltip_on_plain_widget(root, monkeypatch):
    root.deiconify()
    button = tk.Button(root, text="?")
    button.pack()
    root.update()
    tip = sw.Tooltip(button, "Help for the button.")
    monkeypatch.setattr(tip, "_pointer_inside", lambda: True)
    tip.show()
    assert tip._window is not None
    button.destroy()
    assert tip._window is None
