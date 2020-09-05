#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget to handle editable options for rigs
"""

from __future__ import print_function, division, absolute_import

from functools import partial

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc as tp
from tpDcc.libs.python import name as name_utils
from tpDcc.libs.qt.core import qtutils
from tpDcc.libs.qt.widgets import layouts
from tpDcc.libs.qt.widgets.options import optionlist

from tpRigToolkit.widgets.options import factory


class RigOptionList(optionlist.OptionList, object):

    FACTORY_CLASS = factory.RigOptionsFactorySingleton

    def __init__(self, parent=None, option_object=None):
        self._menu_added = False

        super(RigOptionList, self).__init__(parent=parent, option_object=option_object)

        self._option_group_class = RigOptionListGroup

    def _create_context_menu(self, menu, parent=None):
        create_menu = super(RigOptionList, self)._create_context_menu(menu=menu, parent=parent)

        if self._menu_added:
            return create_menu

        control_icon = tp.ResourcesMgr().icon('rigcontrol')
        bone_icon = tp.ResourcesMgr().icon('bone')
        link_icon = tp.ResourcesMgr().icon('link')

        create_menu.addSeparator()
        add_rig_control_action = QAction(control_icon, 'Add Rig Control', create_menu)
        create_menu.addAction(add_rig_control_action)
        add_bone_action = QAction(bone_icon, 'Add Rig Joint', create_menu)
        create_menu.addAction(add_bone_action)
        add_bone_list_action = QAction(bone_icon, 'Add Rig Joint List', create_menu)
        create_menu.addAction(add_bone_list_action)
        add_control_bone_link_action = QAction(link_icon, 'Add Control/Joint Link', create_menu)
        create_menu.addAction(add_control_bone_link_action)

        add_rig_control_action.triggered.connect(partial(parent._add_option, 'rigcontrol'))
        add_bone_action.triggered.connect(partial(parent._add_option, 'bone'))
        add_bone_list_action.triggered.connect(partial(parent._add_option, 'boneList'))
        add_control_bone_link_action.triggered.connect(partial(parent._add_option, 'boneControlLink'))

        self._menu_added = True

        return create_menu


class RigOptionListGroup(RigOptionList, object):
    updateValues = Signal(object)
    widgetClicked = Signal(object)

    def __init__(self, name, option_object, parent=None):
        self._name = name
        super(RigOptionListGroup, self).__init__(option_object=option_object, parent=parent)

        self.setObjectName(name)
        self._original_background_color = self.palette().color(self.backgroundRole())
        self._option_type = self.get_option_type()
        self.supress_select = False
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def mousePressEvent(self, event):
        super(RigOptionListGroup, self).mousePressEvent(event)

        if not event.button() == Qt.LeftButton:
            return

        half = self.width() * 0.5
        if event.y() > 25 and event.x() > (half - 50) and event.x() < (half + 50):
            return

        parent = self.get_parent()
        if parent:
            parent.supress_select = True
        if self.supress_select:
            self.supress_select = False
            return

        self.widgetClicked.emit(self)

    def setup_ui(self):
        main_group_layout = layouts.VerticalLayout()
        main_group_layout.setContentsMargins(0, 0, 0, 0)
        main_group_layout.setSpacing(1)
        self.group = optionlist.OptionGroup(self._name)
        self.child_layout = self.group.child_layout

        self.main_layout = layouts.VerticalLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addSpacing(2)
        self.main_layout.addWidget(self.group)
        self.setLayout(self.main_layout)

        self.group.expand.connect(self._on_expand_updated)
    #
    # def _create_context_menu(self, menu, parent):
    #     pass

    def get_name(self):
        """
        Returns option group name
        :return: str
        """

        return self.group.title()

    def set_name(self, name):
        """
        Sets option group name
        :param name: str
        """

        self.group.setTitle(name)

    def get_option_type(self):
        """
        Returns the type of the option
        :return: str
        """

        return 'group'

    def get_value(self):
        """
        Returns whether group is expanded or not
        :return: bool
        """

        expanded = not self.group.is_collapsed()
        return expanded

    def get_children(self):
        """
        Returns all group Options
        :return: list(Option)
        """

        item_count = self.child_layout.count()
        found = list()
        for i in range(item_count):
            item = self.child_layout.itemAt(i)
            widget = item.widget()
            found.append(widget)

        return found

    def set_expanded(self, flag):
        """
        Sets the expanded/collapsed state of the group
        :param flag: bool
        """

        if flag:
            self.expand_group()
        else:
            self.collapse_group()

    def expand_group(self):
        """
        Expands group
        """

        self.group.expand_group()

    def collapse_group(self):
        """
        Collapse gorup
        """

        self.group.collapse_group()

    def save(self):
        """
        Function that saves the current state of the group option
        :return:
        """
        self._write_options(clear=False)

    def rename(self, new_name=None):
        """
        Function that renames group
        :param new_name: variant, str or None
        """

        found = self._get_widget_names()
        title = self.group.title()
        if not new_name:
            new_name = qtutils.get_string_input('Rename Group', old_name=title)
        if new_name is None or new_name == title:
            return

        while new_name in found:
            new_name = name_utils.increment_last_number(new_name)

        self.group.setTitle(new_name)
        self._write_all()

    def move_up(self):
        """
        Function that moves up selected Options
        """

        parent = self.parent()
        layout = parent.child_layout
        index = layout.indexOf(self)
        if index == 0:
            return
        index -= 1
        parent.child_layout.removeWidget(self)
        layout.insertWidget(index, self)

        self._write_all()

    def move_down(self):
        """
        Function that moves down selected options
        """

        parent = self.parent()
        layout = parent.child_layout
        index = layout.indexOf(self)
        if index == (layout.count() - 1):
            return
        index += 1
        parent.child_layout.removeWidget(self)
        layout.insertWidget(index, self)

        self._write_all()

    def copy_to(self, parent):
        """
        Function that copy selected options into given parent
        :param parent: Option
        """

        group = parent.add_group(self.get_name(), parent)
        children = self.get_children()
        for child in children:
            if child == group:
                continue
            child.copy_to(group)

    def remove(self):
        """
        Function that removes selected options
        :return:
        """
        parent = self.parent()
        if self in self._parent._current_widgets:
            remove_index = self._parent._current_widgets.index(self)
            self._parent._current_widgets.pop(remove_index)
        parent.child_layout.removeWidget(self)
        self.deleteLater()
        self._write_all()

    def _on_expand_updated(self, value):
        self.updateValues.emit(False)