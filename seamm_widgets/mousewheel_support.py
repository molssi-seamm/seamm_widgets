# -*- coding: utf-8 -*-

"""Add support for the mousewheel to scrolled widgets

Based on a version:
# Version: 0.22
# Author: Miguel Martinez Lopez
# Uncomment the next line to see my email
# print("Author's email: ",
# "61706c69636163696f6e616d656469646140676d61696c2e636f6d".decode("hex"))

with minor changes.
"""

import platform

OS = platform.system()


class MousewheelSupport(object):

    # implementation of singleton pattern
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(
        self,
        root,
        horizontal_factor=2,
        vertical_factor=2,
        natural_scroll_direction=True,
    ):
        """Initialize the instance"""

        self._active_area = None
        self.natural_scroll_direction = natural_scroll_direction

        if isinstance(horizontal_factor, int):
            self.horizontal_factor = horizontal_factor
        else:
            raise Exception("Vertical factor must be an integer.")

        if isinstance(vertical_factor, int):
            self.vertical_factor = vertical_factor
        else:
            raise Exception("Horizontal factor must be an integer.")

        if OS == "Linux":
            root.bind_all("<4>", self._on_mousewheel, add="+")
            root.bind_all("<5>", self._on_mousewheel, add="+")
        else:
            # Windows and MacOS
            root.bind_all("<MouseWheel>", self._on_mousewheel, add="+")

    def _on_mousewheel(self, event):
        if self._active_area:
            self._active_area.onMouseWheel(event)

    def _mousewheel_bind(self, widget):
        self._active_area = widget

    def _mousewheel_unbind(self):
        self._active_area = None

    def add_support_to(
        self,
        widget=None,
        xscrollbar=None,
        yscrollbar=None,
        what="units",
        horizontal_factor=None,
        vertical_factor=None,
    ):
        if xscrollbar is None and yscrollbar is None:
            return

        if xscrollbar is not None:
            horizontal_factor = horizontal_factor or self.horizontal_factor

            xscrollbar.onMouseWheel = self._make_mouse_wheel_handler(
                widget, "x", horizontal_factor, what, self.natural_scroll_direction
            )
            xscrollbar.bind(
                "<Enter>",
                lambda event, scrollbar=xscrollbar: self._mousewheel_bind(scrollbar),
            )
            xscrollbar.bind("<Leave>", lambda event: self._mousewheel_unbind())

        if yscrollbar is not None:
            vertical_factor = vertical_factor or self.vertical_factor

            yscrollbar.onMouseWheel = self._make_mouse_wheel_handler(
                widget, "y", vertical_factor, what, self.natural_scroll_direction
            )
            yscrollbar.bind(
                "<Enter>",
                lambda event, scrollbar=yscrollbar: self._mousewheel_bind(scrollbar),
            )
            yscrollbar.bind("<Leave>", lambda event: self._mousewheel_unbind())

        main_scrollbar = yscrollbar if yscrollbar is not None else xscrollbar

        if widget is not None:
            if isinstance(widget, list) or isinstance(widget, tuple):
                list_of_widgets = widget
                for widget in list_of_widgets:
                    widget.bind("<Enter>", lambda event: self._mousewheel_bind(widget))
                    widget.bind("<Leave>", lambda event: self._mousewheel_unbind())

                    widget.onMouseWheel = main_scrollbar.onMouseWheel
            else:
                widget.bind("<Enter>", lambda event: self._mousewheel_bind(widget))
                widget.bind("<Leave>", lambda event: self._mousewheel_unbind())

                widget.onMouseWheel = main_scrollbar.onMouseWheel

    @staticmethod
    def _make_mouse_wheel_handler(
        widget, orient, factor=1, what="units", natural_scroll_direction=True
    ):
        view_command = getattr(widget, orient + "view")

        if natural_scroll_direction:
            if OS == "Linux":

                def onMouseWheel(event):
                    if event.num == 4:
                        view_command("scroll", factor, what)
                    elif event.num == 5:
                        view_command("scroll", (-1) * factor, what)

            elif OS == "Windows":

                def onMouseWheel(event):
                    view_command("scroll", int((event.delta / 120) * factor), what)

            elif OS == "Darwin":

                def onMouseWheel(event):
                    view_command("scroll", (-1) * event.delta, what)

        else:
            if OS == "Linux":

                def onMouseWheel(event):
                    if event.num == 4:
                        view_command("scroll", (-1) * factor, what)
                    elif event.num == 5:
                        view_command("scroll", factor, what)

            elif OS == "Windows":

                def onMouseWheel(event):
                    view_command(
                        "scroll", (-1) * int((event.delta / 120) * factor), what
                    )

            elif OS == "Darwin":

                def onMouseWheel(event):
                    view_command("scroll", event.delta, what)

        return onMouseWheel
