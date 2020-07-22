#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains project widgets implementation for tpRigToolkit
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import tpDcc as tp
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import dividers, buttons

import tpRigToolkit
from tpRigToolkit.widgets.options import rigoptionsviewer


class ProjectSettingsWidget(base.BaseWidget, object):
    exitSettings = Signal()

    def __init__(self, project=None, parent=None):
        self._project = None
        super(ProjectSettingsWidget, self).__init__(parent=parent)

        if project:
            self.set_project(project)

    def ui(self):
        super(ProjectSettingsWidget, self).ui()

        image_layout = QHBoxLayout()
        image_layout.setContentsMargins(2, 2, 2, 2)
        image_layout.setSpacing(2)
        self.main_layout.addLayout(image_layout)
        self._project_image = QLabel()
        self._project_image.setAlignment(Qt.AlignCenter)
        image_layout.addItem(QSpacerItem(30, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        image_layout.addWidget(self._project_image)
        image_layout.addItem(QSpacerItem(30, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        self.main_layout.addWidget(dividers.Divider('Nomenclature'))
        self._naming_widget = NamingWidget(project=self._project)
        self.main_layout.addWidget(self._naming_widget)

        self.main_layout.addWidget(dividers.Divider('Settings'))
        self._project_options_widget = rigoptionsviewer.RigOptionsViewer(option_object=self._project)
        self.main_layout.addWidget(self._project_options_widget)
        self.main_layout.addWidget(dividers.Divider())

        bottom_layout = QVBoxLayout()
        bottom_layout.setContentsMargins(2, 2, 2, 2)
        bottom_layout.setSpacing(2)
        bottom_layout.setAlignment(Qt.AlignBottom)
        self.main_layout.addLayout(bottom_layout)
        bottom_layout.addLayout(dividers.DividerLayout())

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(2, 2, 2, 2)
        buttons_layout.setSpacing(2)
        bottom_layout.addLayout(buttons_layout)

        ok_icon = tp.ResourcesMgr().icon('ok')
        back_icon = tp.ResourcesMgr().icon('back')
        self._ok_btn = buttons.StyleBaseButton(
            icon=ok_icon, icon_padding=2, parent=self, button_style=buttons.ButtonStyles.FlatStyle)
        self._ok_btn.setMinimumSize(QSize(35, 35))
        self._back_btn = buttons.StyleBaseButton(
            icon=back_icon, icon_padding=2, parent=self, button_style=buttons.ButtonStyles.FlatStyle)
        self._back_btn.setMaximumWidth(50)
        buttons_layout.addWidget(self._ok_btn)
        buttons_layout.addWidget(self._back_btn)

    def setup_signals(self):
        self._ok_btn.clicked.connect(self._on_save)
        self._back_btn.clicked.connect(self._on_exit)

    def get_project(self):
        """
        Returns current RigBuilder project used by this widget
        :return: Project
        """

        return self._project

    def set_project(self, project):
        """
        Sets current project used by this widget
        :param project: Project
        """

        self._project = project

        self._project_options_widget.set_option_object(self._project)
        if self._project:
            self._project_image.setPixmap(
                QPixmap(self._project.get_project_image()).scaled(QSize(150, 150), Qt.KeepAspectRatio))
        self._naming_widget.set_project(self._project)

    def update_options(self, do_reload=False):
        """
        Update options of the current project
        """

        if not self._project:
            return

        if do_reload:
            self._project.reload_options()

        self._project_options_widget.update_options()

    def _on_save(self):
        """
        Internal callback function that is called when the user exists settings widget
        """

        self.exitSettings.emit()

    def _on_exit(self):
        """
        Internal callback function that is called when the user exists settings widget
        """

        self.exitSettings.emit()


class NamingWidget(base.BaseWidget, object):
    def __init__(self, project=None, parent=None):

        self._project = project

        super(NamingWidget, self).__init__(parent=parent)

        self.update_rules()

    def get_main_layout(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)

        return main_layout

    def ui(self):
        super(NamingWidget, self).ui()

        edit_icon = tp.ResourcesMgr().icon('edit')
        name_lbl = QLabel('Naming Rule: ')
        self._name_rules = QComboBox()
        self._name_rules.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._edit_btn = buttons.IconButton(icon=edit_icon, icon_padding=2, button_style=buttons.ButtonStyles.FlatStyle)
        self.main_layout.addWidget(name_lbl)
        self.main_layout.addWidget(self._name_rules)
        self.main_layout.addWidget(dividers.get_horizontal_separator_widget())
        self.main_layout.addWidget(self._edit_btn)

    def setup_signals(self):
        self._name_rules.currentIndexChanged.connect(self._on_update_rule)
        self._edit_btn.clicked.connect(self._on_open_naming_manager)

    def set_project(self, project):
        self._project = project
        self.update_rules()

    def update_rules(self):

        try:
            self._name_rules.blockSignals(True)

            self._name_rules.clear()
            if not self._project:
                return
            naming_lib = self._project.naming_lib
            if not naming_lib:
                return
            naming_lib.load_session()
            rules = naming_lib.rules
            for rule in rules:
                self._name_rules.addItem(rule.name, userData=rule)
            rule_name = self._set_rule()
            self._name_rules.setCurrentText(rule_name)
        except Exception as exc:
            tpRigToolkit.logger.warning('Error while updating rules: {}'.format(exc))
        finally:
            self._name_rules.blockSignals(False)

    def _set_rule(self, rule=None):
        if not self._project:
            return
        naming_lib = self._project.naming_lib
        if not naming_lib:
            return

        if rule:
            rule_name = rule.name
            if self._project.settings.has_setting('naming_rule'):
                current_rule = self._project.settings.get('naming_rule')
                if current_rule == rule_name:
                    return
                self._project.settings.set('naming_rule', rule_name)
        else:
            if not self._project.settings.has_setting('naming_rule'):
                self._project.settings.set('naming_rule', self._name_rules.currentText())

        if not self._project.settings.has_setting('naming_rule'):
            return
        rule_name = self._project.settings.get('naming_rule')
        if not naming_lib.has_rule(rule_name):
            return
        naming_lib.set_active_rule(rule_name)

        return rule_name

    def _on_update_rule(self, index):
        rule = self._name_rules.itemData(index)
        self._set_rule(rule=rule)

    def _on_open_naming_manager(self):
        naming_manager_tool = tp.ToolsMgr().launch_tool_by_id(
            'tpRigToolkit-tools-namemanager', do_reload=True, debug=False, project=self._project)
        attacher = naming_manager_tool.attacher
        attacher.closed.connect(self.update_rules)
