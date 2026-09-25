# -*- coding: utf-8 -*-
"""Tests for the LabeledText widget. Skipped where Tk cannot open a display."""

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


def test_labeled_text_roundtrip(root):
    w = sw.LabeledText(root, labeltext="Extra input", height=3, width=20)
    w.pack()
    w.set("%scf\n  MaxIter 500\nend")
    # Tk appends a trailing newline to the buffer; get() must not return it.
    assert w.get() == "%scf\n  MaxIter 500\nend"
    assert w.value == w.get()
    w.value = ""
    assert w.get() == ""


def test_labeled_text_show(root):
    w = sw.LabeledText(root, labeltext="x")
    w.pack()
    w.show("label")
    assert not w.text.winfo_manager()
    w.show("all")
    root.update_idletasks()
    assert w.text.winfo_manager() == "grid"
