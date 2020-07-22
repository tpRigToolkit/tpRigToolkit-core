#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains options to link bones/joints with controls
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *

from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import layouts, buttons
from tpDcc.libs.qt.widgets.options import list

from tpRigToolkit.widgets.options import bone, control


class BoneControlLinkOption(list.ListOption, object):
    def __init__(self, name, parent, main_widget, rig_object):
        self._rig = rig_object
        super(BoneControlLinkOption, self).__init__(name=name, parent=parent, main_widget=main_widget)

    def get_option_type(self):
        return 'boneControlLink'

    def get_option_widget(self):
        return GetBoneControlLinkWidget(name=self._name, rig_object=self._rig)

    def get_value(self):
        list_value = self._option_widget.get_value()

        return list_value


class GetBoneControlLinkWidget(list.GetListWidget, object):
    def __init__(self, name, rig_object, parent=None):
        self._rig = rig_object
        super(GetBoneControlLinkWidget, self).__init__(name=name, parent=parent)

    def get_list_widget(self):
        return BoneControlLinkList(rig_object=self._rig)


class BoneControlLinkList(list.ListWidget, object):
    def __init__(self, rig_object):
        self._rig = rig_object
        super(BoneControlLinkList, self).__init__()

    def _get_entry_widget(self, name):
        return BoneControlLinkItem(self._rig, name)

    def _build_entry(self, link_info=None):
        entry_widget = self._get_entry_widget(link_info)
        entry_widget.itemRemoved.connect(self._cleanup_garbage)
        entry_widget.valueChanged.connect(self._on_value_changed)
        entry_widget.itemDuplicated.connect(self._on_duplicated_item)

        return entry_widget

    def _on_duplicated_item(self, widget):
        value = widget.get_value()
        if not value:
            return
        self.add_entry(value)

        self._on_value_changed()


class BoneControlLinkItem(base.BaseWidget, object):
    valueChanged = Signal(object, object)
    itemRemoved = Signal(object)
    itemDuplicated = Signal(object)

    def __init__(self, rig_object, link_info=None, parent=None):
        self._rig = rig_object
        link_info = link_info if link_info else dict()
        self._control_data = link_info.get('control', dict())
        self._bone_name = link_info.get('node', '')
        self._garbage = None
        super(BoneControlLinkItem, self).__init__(parent=parent)

    def get_main_layout(self):
        main_layout = layouts.HorizontalLayout()
        main_layout.setAlignment(Qt.AlignRight)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        return main_layout

    def ui(self):
        super(BoneControlLinkItem, self).ui()

        self._control_line = control.ControlLineEdit(rig_object=self._rig)
        self._bone_line = bone.BoneLineEdit()
        self._duplicate_btn = buttons.BaseToolButton().image('clone').icon_only()
        self._remove_btn = buttons.BaseToolButton().image('delete').icon_only()

        self._control_line.set_data(self._control_data)
        self._bone_line.setText(self._bone_name)

        self.main_layout.addWidget(self._control_line)
        self.main_layout.addWidget(self._bone_line)
        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(self._duplicate_btn)
        self.main_layout.addWidget(self._remove_btn)

    def setup_signals(self):
        self._control_line.controlSelected.connect(self._on_selected_control)
        self._duplicate_btn.clicked.connect(self._on_duplicate_item)
        self._remove_btn.clicked.connect(self._on_remove_item)
        self._control_line.controlSelected.connect(self._on_value_changed)
        self._bone_line.textChanged.connect(self._on_value_changed)

    def get_value(self):
        control_data = self._control_line.control_data
        selected_bone = self._bone_line.selected_node

        return {
            'control': control_data,
            'node': selected_bone
        }

    def _on_selected_control(self, control_data):
        self._control_data = control_data or dict()
        self._control_line.set_data(self._control_data)

    def _on_remove_item(self):
        self._garbage = True
        self.itemRemoved.emit(self)

    def _on_duplicate_item(self):
        self._garbage = True
        self.itemDuplicated.emit(self)

    def _on_value_changed(self):
        control_data = self._control_line.control_data
        bone_node = self._bone_line.selected_node
        self.valueChanged.emit(control_data, bone_node)
