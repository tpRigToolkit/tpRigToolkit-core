#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains options to select rig bones/joints
"""

from __future__ import print_function, division, absolute_import

import os
import json

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc as tp
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import layouts, lineedit, buttons, dividers
from tpDcc.libs.qt.widgets.options import option, list, text

from tpRigToolkit.data import skeleton


class BoneOption(option.Option, object):
    def __init__(self, name, parent, main_widget):
        super(BoneOption, self).__init__(name=name, parent=parent, main_widget=main_widget)

    def get_option_type(self):
        return 'bone'

    def get_option_widget(self):
        return GetBoneWidget(name=self._name)

    def get_value(self):
        value = self._option_widget.get_text()
        if not value:
            value = ''

        return value

    def set_value(self, value):
        value = str(value)
        self._option_widget.set_text(value)

    def _setup_option_widget_value_change(self):
        self._option_widget.textChanged.connect(self._on_value_changed)


class BoneOptionList(list.ListOption, object):
    def __init__(self, name, parent, main_widget):
        super(BoneOptionList, self).__init__(name=name, parent=parent, main_widget=main_widget)

    def get_option_type(self):
        return 'boneList'


class GetBoneWidget(text.TextWidget, object):
    def __init__(self, name='', parent=None):
        super(GetBoneWidget, self).__init__(name=name, parent=parent)

    def get_text_widget(self):
        return BoneLineEdit()


class BoneLineEdit(lineedit.BaseLineEdit, object):
    def __init__(self, text='', parent=None):
        super(BoneLineEdit, self).__init__(text=text, parent=parent)

    @property
    def selected_node(self):
        return self.text()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            data = event.mimeData().urls()
            file_info = QFileInfo(data[0].toLocalFile())
            file_name = file_info.absoluteFilePath()
            if file_name and os.path.isfile(file_name):
                file_extension = os.path.splitext(file_name)[-1]
                data_extension = skeleton.SkeletonFileData.get_data_extension()
                if not data_extension.startswith('.'):
                    data_extension = '.{}'.format(data_extension)
                if file_extension == data_extension:
                    self._show_bones_hierarchy(file_name)
                    event.accept()
        elif event.mimeData().hasText():
            self.setText(event.mimeData().text())

        event.accept()

    def _show_bones_hierarchy(self, file_path):
        dlg = QDialog(parent=tp.Dcc.get_main_window() or None)
        dlg.setWindowTitle('Select Skeleton Node')
        lyt = QVBoxLayout()
        lyt.setSpacing(0)
        lyt.setContentsMargins(0, 0, 0, 0)
        dlg.setLayout(lyt)
        bone_hierarchy_widget = BoneHierarchyWidget(file_path, parent=dlg)
        current_bone = self.text() or ''
        bone_hierarchy_widget.set_bone(current_bone)
        lyt.addWidget(bone_hierarchy_widget)
        dlg.exec_()
        selected_node = bone_hierarchy_widget.selected_node
        if not selected_node:
            return
        self.setText(selected_node)


class BoneHierarchyWidget(base.BaseWidget, object):
    def __init__(self, file_path, parent=None):
        self._file_path = file_path
        self._selected_node = None
        super(BoneHierarchyWidget, self).__init__(parent=parent)

        self._load_data()

    @property
    def selected_node(self):
        return self._selected_node

    def ui(self):
        super(BoneHierarchyWidget, self).ui()

        self._tree_hierarchy = QTreeWidget()
        self._node_line = QLineEdit()
        self._node_line.setReadOnly(True)
        self._ok_btn = buttons.BaseButton('Ok')
        self._cancel_btn = buttons.BaseButton('Cancel')
        buttons_layout = layouts.HorizontalLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(self._ok_btn)
        buttons_layout.addWidget(self._cancel_btn)

        self.main_layout.addWidget(self._tree_hierarchy)
        self.main_layout.addWidget(self._node_line)
        self.main_layout.addWidget(dividers.Divider())
        self.main_layout.addLayout(buttons_layout)

    def setup_signals(self):
        self._tree_hierarchy.currentItemChanged.connect(self._on_item_selected)
        self._ok_btn.clicked.connect(self._on_ok)
        self._cancel_btn.clicked.connect(self._on_cancel)

    def set_bone(self, bone_name):
        if not bone_name:
            return

        find_items = self._tree_hierarchy.findItems(bone_name, Qt.MatchExactly | Qt.MatchRecursive, 0)
        if not find_items:
            return

        find_item = find_items[0]
        find_item.setSelected(True)
        self._tree_hierarchy.setCurrentItem(find_item)
        self._tree_hierarchy.scrollTo(self._tree_hierarchy.indexFromItem(find_item))

    def _load_data(self):
        self._tree_hierarchy.clear()
        if not self._file_path or not os.path.isfile(self._file_path):
            return

        with open(self._file_path, 'r') as fh:
            skeleton_data = json.load(fh)
        if not skeleton_data:
            return

        created_nodes = dict()
        for node_data in skeleton_data:
            node_index = node_data.get('index', 0)
            node_parent_index = node_data.get('parent_index', -1)
            node_name = node_data.get('name', 'new_node')
            new_node = QTreeWidgetItem()
            new_node.setText(0, node_name)
            created_nodes[node_index] = {'node': new_node, 'parent_index': node_parent_index}
        sorted(created_nodes.items(), key=lambda x: int(x[0]))

        for node_index, node_data in created_nodes.items():
            node_data = created_nodes.get(node_index, None)
            if not node_data:
                continue
            node_item = node_data.get('node')
            parent_index = node_data['parent_index']
            if parent_index <= -1:
                self._tree_hierarchy.addTopLevelItem(node_item)
                continue
            parent_node_data = created_nodes.get(parent_index, None)
            if not parent_node_data:
                continue
            parent_node_item = parent_node_data.get('node')
            parent_node_item.addChild(node_item)

        self._tree_hierarchy.expandAll()

    def _on_item_selected(self, current, previous):
        node_name = current.text(0)
        self._node_line.setText(node_name)
        self._selected_node = node_name

    def _on_ok(self):
        self.parent().close()

    def _on_cancel(self):
        self._selected_node = None
        self.parent().close()
