#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains options to select rig controls
"""

from __future__ import print_function, division, absolute_import

import os

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc as tp
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import layouts, label, lineedit, buttons

from tpRigToolkit.widgets.options import rigoption


class RigControlOption(rigoption.RigOption, object):
    def __init__(self, name, parent, main_widget, rig_object):
        super(RigControlOption, self).__init__(name=name, parent=parent, main_widget=main_widget, rig_object=rig_object)

    def get_option_type(self):
        return 'rigcontrol'

    def get_option_widget(self):
        return GetControlRigWidget(name=self._name, rig_object=self._rig)

    def get_name(self):
        name = self._option_widget.get_name()
        return name

    def set_name(self, name):
        self._option_widget.set_name(name)

    def get_value(self):
        return self._option_widget.control_data

    def set_value(self, value):
        self._option_widget.set_value(value)

    def _setup_option_widget_value_change(self):
        self._option_widget.valueChanged.connect(self._on_value_changed)


class GetControlRigWidget(base.BaseWidget, object):
    valueChanged = Signal(object)

    def __init__(self, name, rig_object, parent=None):
        self._name = name
        self._rig = rig_object
        super(GetControlRigWidget, self).__init__(parent=parent)

        self._control_data = dict()

    @property
    def control_data(self):
        return self._control_data

    def get_main_layout(self):
        main_layout = layouts.HorizontalLayout()
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(2, 2, 2, 2)

        return main_layout

    def ui(self):
        super(GetControlRigWidget, self).ui()

        self._label = label.BaseLabel(self._name)
        self._label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._control = ControlLineEdit(self._rig)

        self.main_layout.addWidget(self._label)
        self.main_layout.addWidget(self._control)

    def setup_signals(self):
        self._control.controlSelected.connect(self._on_selected_control)

    def get_value(self):
        return self._control_data

    def set_value(self, value_dict):
        self._control_data = value_dict or dict()
        self._control.set_data(self._control_data)

    def get_name(self):
        return self._label.text()

    def set_name(self, value):
        self._label.setText(value)

    def _on_selected_control(self, control_data):
        self.set_value(control_data)
        self.valueChanged.emit(control_data)


class ControlLineEdit(base.BaseWidget, object):
    controlSelected = Signal(object)

    def __init__(self, rig_object, parent=None):
        self._rig_object = rig_object
        self._control_data = dict()
        super(ControlLineEdit, self).__init__(parent=parent)

    @property
    def control_data(self):
        return self._control_data

    def get_main_layout(self):
        main_layout = layouts.HorizontalLayout()
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(2, 2, 2, 2)

        return main_layout

    def ui(self):
        super(ControlLineEdit, self).ui()

        self._line = lineedit.BaseLineEdit()
        self._btn = buttons.BaseButton(text='...')

        self.main_layout.addWidget(self._line)
        self.main_layout.addWidget(self._btn)

    def setup_signals(self):
        self._btn.clicked.connect(self._on_open_rig_control_selector)

    def set_data(self, data):
        data = data if data is not None else dict()
        name = data.get('control_name', '')
        self._line.setText(str(name))
        self._line.setToolTip(str(data))
        self._control_data = data

    def _on_open_rig_control_selector(self):

        from tpRigToolkit.tools.controlrig.widgets import controlrig

        dlg = QDialog(parent=tp.Dcc.get_main_window() or None)
        dlg.setWindowTitle('Select Control')
        lyt = QVBoxLayout()
        lyt.setSpacing(0)
        lyt.setContentsMargins(0, 0, 0, 0)
        dlg.setLayout(lyt)

        if hasattr(self._rig_object, 'full_path'):
            current_project = self._rig_object
        else:
            current_project = self._rig_object.project
        project_path = current_project.full_path

        # TODO: The project itself should return this path
        controls_path = os.path.join(project_path, 'controls.json')

        control_selector = controlrig.ControlSelector(controls_path=controls_path)
        if self._control_data:
            control_selector.set_control_data(self._control_data)
        lyt.addWidget(control_selector)
        dlg.resize(600, 700)
        dlg.exec_()
        control_data = control_selector.control_data or dict()
        if not control_data and self._control_data:
            return
        if control_data:
            control_data.pop('shape_data', None)
            control_data.pop('name', None)

        self.controlSelected.emit(control_data)
