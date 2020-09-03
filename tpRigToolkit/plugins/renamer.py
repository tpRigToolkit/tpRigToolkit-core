#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains renamer tool implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc
from tpDcc.tools.renamer.core import renamer

from tpRigToolkit.core import plugin


class RenamerPlugin(plugin.DockPlugin, object):

    NAME = 'Renamer'
    TOOLTIP = 'Allows to rename DCC nodes'
    DEFAULT_DOCK_AREA = Qt.LeftDockWidgetArea

    def __init__(self):
        super(RenamerPlugin, self).__init__()

        self._renamer_widget = None
        self._content = QWidget()
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._content.setLayout(self._content_layout)
        self.setWidget(self._content)

    def show_plugin(self):
        super(RenamerPlugin, self).show_plugin()

        # TODO: This should be defined
        dev = False

        naming_config = tpDcc.ConfigsMgr().get_config(
            config_name='tpRigToolkit-naming', environment='development' if dev else 'production')
        self._renamer_widget = renamer.RenamerToolsetWidget(naming_config=naming_config, parent=self)
        self._renamer_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._content_layout.addWidget(self._renamer_widget)
