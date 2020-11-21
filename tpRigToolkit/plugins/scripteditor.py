#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains script editor tool implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import Qt
from Qt.QtWidgets import QSizePolicy, QWidget

from tpDcc.managers import resources
from tpDcc.libs.qt.widgets import layouts
from tpDcc.tools.scripteditor.widgets import scripteditor

from tpRigToolkit.core import plugin


class ScriptsEditorPlugin(plugin.DockPlugin, object):

    NAME = 'Scripts Editor'
    TOOLTIP = 'Allow to edit scripts easily'
    DEFAULT_DOCK_AREA = Qt.RightDockWidgetArea
    IS_SINGLETON = True

    def __init__(self):
        super(ScriptsEditorPlugin, self).__init__()

        self._script_editor_widget = None
        self._content = QWidget()
        self._content_layout = layouts.VerticalLayout(spacing=0, margins=(0, 0, 0, 0))
        self._content.setLayout(self._content_layout)
        self.setWidget(self._content)

    @staticmethod
    def icon():
        return resources.icon('source_code')

    def show_plugin(self):
        super(ScriptsEditorPlugin, self).show_plugin()

        settings = self._app.settings()

        if not self._script_editor_widget:
            self._script_editor_widget = scripteditor.ScriptEditorWidget(settings=settings, load_session=False)
            # self._script_editor_widget.disable_save_script()
            self._script_editor_widget.disable_console()
            self._script_editor_widget.set_toolbar_visibility(False)
            self._script_editor_widget.set_menubar_visibility(False)
            self._script_editor_widget.close_all_tabs()
            self._script_editor_widget.scriptSaved.connect(self._on_script_saved)
            self._script_editor_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self._content_layout.addWidget(self._script_editor_widget)
            self._script_editor_widget.lastTabClosed.connect(self.close)

    def load_script(self, script_file):
        if not self._script_editor_widget:
            return

        self._script_editor_widget.load_script(script_file)

    def _on_script_saved(self, file_path):
        pass
