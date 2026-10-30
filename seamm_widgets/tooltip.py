# -*- coding: utf-8 -*-

"""A tooltip: help text that pops up when the pointer rests on a widget.

The tip is bound to one widget, usually a compound widget such as a
LabeledEntry, and covers all of its children: it shows after the pointer
has rested anywhere inside the widget for a moment, and hides when the
pointer leaves it, a mouse button is pressed or the widget is destroyed.
"""

import logging
import textwrap
import tkinter as tk

logger = logging.getLogger(__name__)


def reflow(text):
    """Tidy help text for display: remove the common indentation, join the
    lines of each paragraph and keep the blank lines between paragraphs, so
    that the label wraps the text to its own width."""
    text = textwrap.dedent(text).strip()
    paragraphs = [" ".join(p.split()) for p in text.split("\n\n")]
    return "\n\n".join(p for p in paragraphs if p != "")


class Tooltip:
    """Show help text in a small window when the pointer rests on a widget.

    Parameters
    ----------
    widget : tk.Widget
        The widget to describe. The tip covers it and all its children.
    text : str
        The help text, reflowed to wrap at ``wraplength`` pixels.
    delay : int
        Milliseconds the pointer must rest before the tip shows.
    wraplength : int
        The width of the tip in pixels.
    """

    def __init__(self, widget, text="", delay=600, wraplength=360):
        self.widget = widget
        self.delay = delay
        self.wraplength = wraplength
        self._text = ""
        self._after_id = None
        self._window = None
        self.text = text

        widget.bind("<Enter>", self._on_enter, add="+")
        widget.bind("<Leave>", self._on_leave, add="+")
        widget.bind("<ButtonPress>", self.hide, add="+")
        widget.bind("<Destroy>", self._on_destroy, add="+")

    @property
    def text(self):
        """The help text shown in the tip."""
        return self._text

    @text.setter
    def text(self, value):
        self._text = reflow(value) if value else ""
        if self._window is not None:
            if self._text == "":
                self.hide()
            else:
                self._window.label.configure(text=self._text)

    def _on_enter(self, event=None):
        if self._text == "" or self._window is not None or self._after_id is not None:
            return
        self._after_id = self.widget.after(self.delay, self.show)

    def _on_leave(self, event=None):
        # Moving between the widget's own children also gives a <Leave>, so
        # only hide once the pointer is really outside the widget.
        if not self._pointer_inside():
            self.hide()

    def _on_destroy(self, event=None):
        if event is None or event.widget is self.widget:
            self.hide()

    def _pointer_inside(self):
        """Whether the pointer is over the widget or any of its children."""
        try:
            x, y = self.widget.winfo_pointerxy()
            w = self.widget.winfo_containing(x, y)
        except (tk.TclError, KeyError):
            # KeyError: the pointer is over a window Tkinter does not know,
            # such as a combobox's popdown list.
            return False
        while w is not None:
            if w is self.widget:
                return True
            w = w.master
        return False

    def show(self):
        """Show the tip just below the pointer, kept on the screen."""
        self._after_id = None
        if self._text == "" or self._window is not None:
            return
        try:
            if not self.widget.winfo_viewable() or not self._pointer_inside():
                return
        except tk.TclError:
            return

        tw = tk.Toplevel(self.widget)
        tw.withdraw()
        tw.wm_overrideredirect(True)
        try:
            # On macOS keep the tip from taking the focus or a title bar
            tw.tk.call(
                "::tk::unsupported::MacWindowStyle",
                "style",
                tw._w,
                "help",
                "noActivates",
            )
        except tk.TclError:
            pass

        tw.label = tk.Label(
            tw,
            text=self._text,
            justify=tk.LEFT,
            anchor=tk.W,
            wraplength=self.wraplength,
            background="#ffffe0",
            foreground="black",
            relief=tk.SOLID,
            borderwidth=1,
            padx=6,
            pady=4,
        )
        tw.label.pack(fill=tk.BOTH, expand=True)

        tw.update_idletasks()
        x, y = self.widget.winfo_pointerxy()
        x += 12
        y += 18
        width = tw.winfo_reqwidth()
        height = tw.winfo_reqheight()
        screen_width = tw.winfo_screenwidth()
        screen_height = tw.winfo_screenheight()
        if x + width > screen_width:
            x = max(0, screen_width - width)
        if y + height > screen_height:
            # Above the pointer instead
            y = max(0, y - height - 28)
        tw.wm_geometry(f"+{x}+{y}")
        tw.deiconify()
        try:
            tw.wm_attributes("-topmost", True)
        except tk.TclError:
            pass
        self._window = tw

    def hide(self, event=None):
        """Cancel a pending tip and remove a shown one."""
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None
        if self._window is not None:
            try:
                self._window.destroy()
            except tk.TclError:
                pass
            self._window = None
