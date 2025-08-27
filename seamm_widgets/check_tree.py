# -*- coding: utf-8 -*-

"""A Tk widget for a tree of checkboxes."""

import logging
from pathlib import Path
import pkg_resources
import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image

import seamm_widgets as sw

logger = logging.getLogger(__name__)

options = {
    "treeview": {
        "columns": "columns",
        "cursor": "cursor",
        "displaycolumns": "displaycolumns",
        "height": "height",
        "padding": "padding",
        "show": "show",
        "style": "style",
        "takefocus": "takefocus",
    },
}


class CheckTree(sw.LabeledWidget):
    """Class to provide a tree of checkboxes."""

    def __init__(self, parent, *args, columns=[], **kwargs):
        class_ = kwargs.pop("class_", "MCheckTree")
        super().__init__(parent, class_=class_)

        self.frame = self.interior
        self._columns = columns

        self.tree = ttk.Treeview(
            self.frame,
            selectmode="none",
            columns=self._columns,
        )
        for column in self._columns:
            self.tree.heading(column, text=column)

        self.tree.tag_bind("_node_", "<Button-1>", self._click_cb)

        self.x_scrollbar = ttk.Scrollbar(
            self.frame, orient=tk.HORIZONTAL, command=self.tree.xview
        )
        self.tree.config(xscrollcommand=self.x_scrollbar.set)
        self.y_scrollbar = ttk.Scrollbar(
            self.frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.config(yscrollcommand=self.y_scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        self.y_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.x_scrollbar.grid(row=1, column=0, sticky=tk.EW)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        path = Path(pkg_resources.resource_filename(__name__, "data/"))

        self.checked_image = ImageTk.PhotoImage(Image.open(path / "checked.png"))
        self.unchecked_image = ImageTk.PhotoImage(Image.open(path / "unchecked.png"))
        self.mixed_image = ImageTk.PhotoImage(Image.open(path / "mixed.png"))

        self.config(**kwargs)

    def bbox(self, item, column=None):
        """Return the bonding box for the item.

        For the item with iid item, if the item is currently visible, this method
        returns a tuple (x, y, w, h), where (x, y) are the coordinates of the upper left
        corner of that item relative to the widget, and w and h are the width and height
        of the item in pixels. If the item is not visible, the method returns an empty
        string.

        If the optional column argument is omitted, you get the bounding box of the
        entire row. To get the bounding box of one specific column of the item's row,
        use column=C where C is either the integer index of the column or its column
        identifier.
        """
        return self.tree.bbox(item, column=column)

    def column(self, cid, option=None, **kw):
        """
        This method configures the appearance of the logical column specified by cid,
        which may be either a column index or a column identifier. To configure the icon
        column, use a cid value of '#0'.

        Each column in a Treeview widget has its own set of options from this table:

            anchor
                The anchor that specifies where to position the content of the
                column. The default value is 'w'.

            id
                The column name. This option is read-only and set when the constructor
                is called.

            minwidth
                Minimum width of the column in pixels; the default value is 20.

            stretch
                If this option is True, the column's width will be adjusted when the
                widget is resized. The default setting is 1.

            width
                Initial width of the column in pixels; the default is 200.

        If no option value or any other keyword argument is supplied, the method returns
        a dictionary of the column options for the specified column.

        To interrogate the current value of an option named X , use an argument
        option=X.

        To set one or more column options, you may pass keyword arguments using the
        option names shown above, e.g., anchor=tk.CENTER to center the column contents.
        """
        return self.tree.column(cid, option=option, **kw)

    def config(self, **kwargs):
        """Set the configuration of the megawidget"""

        # our options that we deal with
        entry = options["treeview"]

        # cannot modify kwargs while iterating over it...
        keys = [*kwargs.keys()]
        for k in keys:
            if k in entry:
                v = kwargs.pop(k)
                self.tree.config(**{entry[k]: v})

        # having removed our options, pass rest to parent
        super().config(**kwargs)

    def configure(self, **kwargs):
        """Alias for config()"""
        return self.config(**kwargs)

    def _check_parents(self, iid):
        """Correct the state of all parents up the tree to make their state correct.

        Parameters
        ----------
        iid : str
            The item to start with.
        """
        parent = self.tree.parent(iid)
        logger.debug(f"{iid=} {parent=}")
        if parent == "":
            self.state(iid)
        else:
            self._check_parents(parent)

    def _click_cb(self, event):
        iid = self.tree.identify_row(event.y)

        element = self.tree.identify_element(event.x, event.y)

        logger.info(f"_click_cb, {iid=} {element=}")

        if element in ("image", "text"):
            self.invoke(iid)

    def delete(self, *items):
        """The arguments are iid values. All the items in the widget that have matching
        iid values are destroyed, along with all their descendants.
        """
        return self.tree.delete(*items)

    def _deselect(self, iid, recursive=True, check_parents=True):
        """Change the state of the item 'iid' to unchecked.

        Parameters
        ----------
        iid : str
            The unique id of the item in the tree.
        recursive : bool
            Whether to select all children
        check_parents: bool
            Whether to set the state of parents

        Returns
        -------
        any
            The return from any command invoked by changing the state.
        """
        tags = [*self.tree.item(iid, "tags")]
        if "checked" in tags:
            tags.remove("checked")
        self.tree.item(iid, image=self.unchecked_image, tags=tags)

        # If this is a branch node, i.e. it has children, change them too
        if recursive:
            children = self.tree.get_children(iid)
            for child in children:
                self._deselect(child, recursive=True)

        if check_parents:
            self._check_parents(iid)

    def detach(self, *items):
        """The arguments are iid values. All the items in the widget that have matching
        iid values are removed from the visible widget, along with all their
        descendants.

        The items are not destroyed. You may reattach them to the visible tree using the
        .move() method described below.
        """
        return self.tree.detach(*items)

    def exists(self, iid):
        """Returns True if there exists an item in the widget with the given iid, or
        False otherwise. If an item is not currently visible because it was removed with
        the .detach() method, it is still considered to exist for the purposes of the
        .exists() method.
        """
        return self.tree.exists(iid)

    def from_dict(self, parent, metadata):
        for key, value in metadata.items():
            # Get any data in the columns
            column_data = []
            for column in self._columns:
                tmp = ""
                for column_name in value.keys():
                    if column_name.lower() == column.lower():
                        tmp = value[column_name]
                        break
                column_data.append(tmp)

            tags = ["_node_", key]
            checked = value.get("checked", False)
            if checked:
                tags.append("checked")

            self.tree.insert(
                parent,
                "end",
                iid=key,
                text=key,
                image=self.checked_image if checked else self.unchecked_image,
                tag=tags,
                open="open" in value and value["open"],
                values=column_data,
            )
            # Recurse if a branch node
            if "items" in value:
                self.from_dict(key, value["items"])

        # Set the state of intermediate nodes
        children = self.tree.get_children("")
        for child in children:
            self.state(child)

    def focus(self, iid=None):
        """If you don't provide an argument to this method, you get back either the iid
        of the item that currently has focus, or '' if no item has focus.

        You can give focus to an item by passing its iid as the argument to this method.
        """
        return self.tree.focus(iid)

    def get(self, parent="", as_dict=False):
        """Get the selected items.

        Parameters
        ----------
        parent : str = ""
            Get selected children of the parent. Defaults to the entire tree.
        as_dict : bool = False
            Return a dictionary keyed by the branching nodes, rather than a flat list.

        Returns
        -------
        [str] or dict(str: str|dict(str: str|dict(...)
        """
        if as_dict:
            result = {"selected": [], "children": {}}
        else:
            result = []
        for child in self.get_children(parent):
            if len(self.get_children(child)) > 0:
                if as_dict:
                    result["children"][child] = self.get(parent=child, as_dict=as_dict)
                else:
                    result.extend(self.get(parent=child))
            else:
                tags = self.item(child, "tags")
                if "checked" in tags:
                    if as_dict:
                        result["selected"].append(child)
                    else:
                        result.append(child)
        return result

    def get_children(self, item=None):
        """Returns a tuple of the iid values of the children of the item specified by
        the item argument. If the argument is omitted, you get a tuple containing the
        iid values of the top-level items.
        """
        return self.tree.get_children(item)

    def get_leaves(self, item=None):
        """Returns the iid values of all leaves of the tree belove of the item specified
        by the item argument. If the argument is omitted, it gives the leaves for the
        entire tree.
        """
        leaves = []
        for child in self.tree.get_children(item):
            children = self.tree.get_children(child)
            if len(children) > 0:
                leaves.extend(self.get_leaves(child))
            else:
                leaves.append(child)
        return leaves

    def heading(self, cid, option=None, **kw):
        """Use this method to configure the column heading that appears at the top of
        the widget for the column specified by cid, which may be either a column index
        or a column identifier. Use a cid argument value of '#0' to configure the
        heading over the icon column.

        Each heading has its own set of options with these names and values:

        anchor
            An anchor that specifies how the heading is aligned within the column; see
            Section 5.5, “Anchors”. The default value is tk.W.
        command
            A procedure to be called when the user clicks on this column heading.
        image
            To present a graphic in the column heading (either with or instead of a text
            heading), set this option to an image, as specified in Section 5.9,
            “Images”.
        text
            The text that you want to appear in the column heading.

        If you supply no keyword arguments, the method will return a dictionary showing
        the current settings of the column heading options.

        To interrogate the current value of some heading option X, use an argument of
        the form option=X; the method will return the current value of that option.

        You can set one or more heading options by supplying them as keyword arguments
        such as “anchor=tk.CENTER”.
        """
        return self.tree.heading(cid, option=option, **kw)

    def identify_column(self, x):
        """Given an x coordinate, this method returns a string of the form '#n' that
        identifies the column that contains that x coordinate.

        Assuming that the icon column is displayed, the value of n is 0 for the icon
        column; 1 for the second physical column; 2 for the third physical column; and
        so on. Recall that the physical column number may be different from the logical
        column number in cases where you have rearranged them using the displaycolumns
        argument to the Treeview constructor.

        If the icon column is not displayed, the value of n is 1 for the first physical
        column, 2 for the second, and so on.
        """
        return self.tree.identify_column(x)

    def identify_element(self, x, y):
        """Returns the name of the element at location (x, y) relative to the widget, or
        '' if no element appears at that position. Element names are discussed in
        Section 50, “The ttk element layer”.
        """
        return self.tree.identify_element(x, y)

    def identify_region(self, x, y):
        """Given the coordinates of a point relative to the widget, this method returns
        a string indicating what part of the widget contains that point. Return values
        may include:

        'nothing'
            The point is not within a functional part of the widget.
        'heading'
            The point is within one of the column headings.
        'separator'
             The point is located within the column headings row, but on the separator
             between columns. Use the .identify_column() method to determine which
             column is located just to the left of this separator.
        'tree'
             The point is located within the icon column.
        'cell'
             The point is located within an item row but not within the icon column.
        """
        return self.tree.identify_region(x, y)

    def identify_row(self, y):
        """If y-coordinate y is within one of the items, this method returns the iid of
        that item. If that vertical coordinate is not within an item, this method
        returns an empty string.
        """
        return self.tree.identify_row(y)

    def index(self, iid):
        """This method returns the index of the item with the specified iid relative to
        its parent, counting from zero.
        """
        return self.tree.index(iid)

    def insert(
        self,
        parent,
        index,
        iid=None,
        open=False,
        selected=False,
        state=True,
        tags=[],
        text="",
        values=[],
    ):
        """This method adds a new item to the tree, and returns the item's iid
        value.

        Parameters
        ----------
        parent : str
            To insert a new top-level item, make this argument an empty string. To
            insert a new item as a child of an existing item, make this argument the
            parent item's iid.
        index : int or 'end'
            This argument specifies the position among this parent's children where you
            want the new item to be added. For example, to insert the item as the new
            first child, use a value of zero; to insert it after the parent's first
            child, use a value of 1; and so on. To add the new item as the last child of
            the parent, make this argument's value 'end'.
        iid : str = None
            You may supply an iid for the item as a string value. If you don't supply an
            iid, one will be generated automatically and returned by the method.
        open : bool
            This option specifies whether this item will be open initially. If you
            supply open=False, this item will be closed. If you supply open=True, the
            item's children will be visible whenever the item itself is visible. The
            default value is False.
        selected : bool = False
            Whether the item is initially selected.
        state : bool = True
            Whether to correct the state of the tree, default=True
        tags : [str] = []
            You may supply one or more tag strings to be associated with this item. The
            value may be either a single string or a sequence of strings.
        text : str = ""
            You may supply text to be displayed within the icon column of this item. If
            given, this text will appear just to the right of the icon, and also to the
            right of the image if provided.
        values : [str] = []
            This argument supplies the data items to be displayed in each column of the
            item. The values are supplied in logical column order. If too few values are
            supplied, the remaining columns will be blank in this item; if too many
            values are supplied, the extras will be discarded.
        """
        tmp_tags = [*tags]
        if "_node_" not in tmp_tags:
            tmp_tags.append("_node_")

        iid = self.tree.insert(
            parent,
            index,
            iid=iid,
            open=open,
            tags=tmp_tags,
            text=text,
            values=values,
            image=self.checked_image if selected else self.unchecked_image,
        )

        if selected:
            self.selection_add(iid)
        if state:
            self.state()
        return iid

    def invoke(self, iid, recursive=True):
        """Change the state of the item 'iid' just as if clicked.

        Parameters
        ----------
        iid : str
            The unique id of the item in the tree.
        recursive : bool
            Change all children, grandchildren, etc. if True

        Returns
        -------
        any
            The return from any command invoked by changing the state.
        """
        tags = [*self.tree.item(iid, "tags")]
        if "checked" in tags:
            self._deselect(iid, recursive=recursive)
        else:
            self._select(iid, recursive=recursive)

    def item(self, iid, option=None, **kw):
        """Use this method to set or retrieve the options within the item specified by
        iid. Refer to the .insert() method above for the names of the item options.

        With no arguments, it returns a dictionary whose keys are the option names and
        the corresponding values are the settings of those options. To retrieve the
        value of a given option, pass the option's name as its second argument. To set
        one or more options, pass them as keyword arguments to the method.
        """
        return self.tree.item(iid, option=option, **kw)

    def move(self, iid, parent, index):
        """Move the item specified by iid to the values under the item specified by
        parent at position index. The parent and index arguments work the same as those
        arguments to the .index() method.
        """
        return self.tree.move(iid, parent, index)

    def next(self, iid):
        """If the item specified by iid is not the last child of its parent, this method
        returns the iid of the following child; if it is the last child of its parent,
        this method returns an empty string. If the specified item is a top-level item,
        the method returns the iid of the next top-level item, or an empty string if the
        specified item is the last top-level item.
        """
        return self.tree.next(iid)

    def parent(self, iid):
        """If the item specified by iid is a top-level item, this method returns an
        empty string; otherwise it returns the iid of that item's parent.
        """
        return self.tree.parent(iid)

    def prev(self, iid):
        """If the item specified by iid is not the first child of its parent, this
        method returns the iid of the previous child; otherwise it returns an empty
        string. If the specified item is a top-level item, this method returns the iid
        of the previous top-level item, or an empty string if it is the first top-level
        item.
        """
        return self.tree.prev(iid)

    def see(self, iid):
        """This method ensures that the item specified by iid is visible. Any of its
        ancestors that are closed are opened. The widget is scrolled, if necessary, so
        that the item appears.
        """
        return self.tree.see(iid)

    def selection_add(self, items):
        """In addition to any items already selected, add the specified items. The
        argument may be either a single iid or a sequence of iids.
        """
        if isinstance(items, str):
            self._select(items)
        else:
            for item in items:
                self._select(item)

    def selection_clear(self, items=None):
        """Clear all selections from the subtree(s)"""
        if items is None:
            self.selection_remove("")
        elif isinstance(items, str):
            self.selection_remove(self.get(items))
        else:
            for item in items:
                self.selection_remove(self.get(item))

    def selection_remove(self, items):
        """Unselect any items specified by the argument, which may be a single iid or a
        sequence of iids.
        """
        if isinstance(items, str):
            self._deselect(items)
        else:
            for item in items:
                self._deselect(item)

    def selection_set(self, items):
        """Only the specified items will be selected; if any other items were selected
        before, they will become unselected.
        """
        self.selection_remove(self.get_leaves())
        self.selection_add(items)

    def selection_toggle(self, items):
        """The argument may be a single iid or a sequence of iids. For each item
        specified by the argument, if it was selected, unselect it; if it was
        unselected, select it.
        """
        if isinstance(items, str):
            self.invoke(items)
        else:
            for item in items:
                self.invoke(item)

    def _select(self, iid, recursive=True, check_parents=True):
        """Change the state of the item 'iid' to checked.

        Parameters
        ----------
        iid : str
            The unique id of the item in the tree.
        recursive : bool
            Whether to select all children
        check_parents: bool
            Whether to set the state of parents

        Returns
        -------
        any
            The return from any command invoked by changing the state.
        """
        tags = [*self.tree.item(iid, "tags")]
        tags.append("checked")
        self.tree.item(iid, image=self.checked_image, tags=tags)

        # If this is a branch node, i.e. it has children, change them too
        if recursive:
            children = self.tree.get_children(iid)
            for child in children:
                self._select(child, recursive=True, check_parents=False)

        if check_parents:
            self._check_parents(iid)

    def set(self, iid, column=None, value=None):
        """Use this method to retrieve or set the column values of the item specified by
        iid. With one argument, the method returns a dictionary: the keys are the column
        identifiers, and each related value is the text in the corresponding column.

        With two arguments, the method returns the data value from the column of the
        selected item whose column identifier is the column argument. With three
        arguments, the item's value for the specified column is set to the third
        argument.
        """
        return self.tree.set(iid, column=column, value=value)

    def set_children(self, item, *newChildren):
        """Use this method to change the set of children of the item whose iid is
        item. The newChildren argument is a sequence of iid strings. Any current
        children of item that are not in newChildren are removed.
        """
        return self.tree.set_children(item, *newChildren)

    def state(self, iid="", recursive=True):
        """Determine the state of this item, and optionally its subtree.

        Parameters
        ----------
        iid : str
            The item to check, or entire tree if ""
        recursive : bool
            Whether to check the subtree

        Returns
        -------
        str
            "checked", "unchecked", or "mixed"
        """
        state = None
        logger.debug(f"\n state for {iid}")
        if recursive:
            logger.debug(f"{recursive=}")
            if iid is None:
                children = self.get_children("")
            else:
                children = self.get_children(iid)
            for child in children:
                tmp = self.state(child, recursive=True)
                if state is None:
                    state = tmp
                    logger.debug(f"    {child=} {state=}")
                elif state != tmp:
                    logger.debug(f"    {child=} returning 'mixed'")
                    state = "mixed"
            if state is not None:
                tags = [*self.tree.item(iid, "tags")]
                logger.debug(f"{state=} {tags=}")
                if state == "checked":
                    if "checked" not in tags:
                        tags.append("checked")
                    if "mixed" in tags:
                        tags.remove("mixed")
                    self.tree.item(iid, image=self.checked_image, tags=tags)
                elif state == "unchecked":
                    if "checked" in tags:
                        tags.remove("checked")
                    if "mixed" in tags:
                        tags.remove("mixed")
                    self.tree.item(iid, image=self.unchecked_image, tags=tags)
                else:
                    if "checked" in tags:
                        tags.remove("checked")
                    if "mixed" not in tags:
                        tags.append("mixed")
                    self.tree.item(iid, image=self.mixed_image, tags=tags)

                logger.debug(f"returning {state=} from branch node {iid=}")
                return state

        tags = [*self.tree.item(iid, "tags")]
        logger.debug(f"    {tags=}")
        if "checked" in tags:
            state = "checked"
        elif "mixed" in tags:
            state = "mixed"
        else:
            state = "unchecked"

        logger.debug(f"returning {state=} from leaf node {iid=}")
        return state

    def tag_bind(self, tagName, sequence=None, callback=None):
        """This method binds the event handler specified by the callback argument to all
        items that have tag tagName. The sequence and callback arguments work the same
        as the sequence and func arguments of the .bind() method described in Section
        26, “Universal widget methods”.
        """
        return self.tree.tag_bind(tagName, sequence=sequence, callback=callback)

    def tag_configure(self, tagName, option=None, **kw):
        """This method can either interrogate or set options that affect the appearance
        of all the items that have tag tagName. Tag options include:

        'background'
            The background color.
        'font'
            The text font.
        'foreground'
            The foreground color.
        'image'
            An image to be displayed in items with the given tag.

        When called with one argument, it returns a dictionary of the current tag
        options. To return the value of a specific option X, use X as the second
        argument.

        To set one or more options, use keyword arguments such as foreground='red'.
        """
        return self.tree.tag_configure(tagName, option=option, **kw)

    def tag_has(self, tagName, iid=None):
        """Called with one argument, this method returns a list of the iid values for
        all items that carry tag tagName. If you provide an iid as the second argument,
        the method returns True if the item with that iid has tag tagName, False
        otherwise.
        """
        return self.tree.tag_has(tagName, iid=iid)


if __name__ == "__main__":  # pragma: no cover
    import pprint  # noqa: F401

    # logging.basicConfig(level="INFO")

    def load_dict(tree, parent, metadata):
        """Custom code to load the dictionary in the test.
        NB. the 'state=False' argument prevents insert from working out the
        state of the parent nodes every time an item is inserted. This is done
        at the end with 'tree.state()'
        """
        for key, value in metadata.items():
            # Get any data in the columns
            checked = value.get("checked", False)

            tree.insert(
                parent,
                "end",
                iid=key,
                text=key,
                selected=checked,
                state=False,
                open="open" in value and value["open"],
                values=[value["description"] if "description" in value else ""],
            )
            # Recurse if a branch node
            if "items" in value:
                load_dict(tree, key, value["items"])

        # Set the state of intermediate nodes
        tree.state()

    root = tk.Tk()
    root.title("Search Criteria")

    tree = CheckTree(root, labeltext="Features", labelpos="n", columns=["Description"])
    tree.pack(expand=True, fill="both")

    metadata = {
        "1-D": {
            "open": True,
            "items": {
                "D1": {"description": "This describes D1"},
                "D2": {"checked": True, "description": "This describes D2"},
                "Sub1": {
                    "items": {
                        "S1": {"description": "This describes S1"},
                        "S2": {"item": "alias for S2", "description": "Ain't none!"},
                    },
                },
                "D3": {"item": "D3"},
            },
        },
    }

    if False:
        metadata["2-D"] = {"items": {}}
        tmp = metadata["2-D"]["items"]
        for i in range(20):
            tmp[f"E{i}"] = {"description": f"And a super E{i} thingamajig"}
        load_dict(tree, "", metadata)
    else:
        load_dict(tree, "", metadata)
        twoD = tree.insert("", "end", text="2-D", values=["Two dimensional features"])
        print(f"{twoD=}")
        for i in range(20):
            tree.insert(
                twoD,
                "end",
                text=f"2-D Descriptor {i}",
                values=[f"Fancy 2-D descriptor #{i}"],
            )

    # enter the event loop
    root.mainloop()
