#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base wrapper classes to create DCC dialogs
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import tpDcc


class MainDialog(tpDcc.Dialog, object):

    def __init__(
            self,
            tool=None,
            name='MainDialog',
            title='MainDialog',
            show_dragger=True, size=(200, 125),
            fixed_size=False,
            parent=None):

        self._tool = tool

        super(MainDialog, self).__init__(
            name=name,
            title=title,
            parent=parent,
            show_dragger=show_dragger,
            size=size,
            fixed_size=fixed_size
        )

    def ui(self):
        super(MainDialog, self).ui()

        dialog_icon = self._get_icon()
        self.setWindowIcon(dialog_icon)

        if self._tool:
            self.main_layout.addWidget(self._tool)

        # if self._project.is_dev():
        #     int_colors = self._project.dev_color0.split(',')
        #     dev_style = "background-color: rgb({}, {}, {})".format(
        #         int_colors[0], int_colors[1], int_colors[2], 255)
        #     self._dragger.setStyleSheet(dev_style)

    def setWindowTitle(self, title):
        # if self._project.is_dev():
        #     title = '{} - [{}]'.format(title, self._project.get_environment())

        super(MainDialog, self).setWindowTitle(title)

    def _get_icon(self):
        """
        Internal function that returns the icon used for the window
        :return: QIcon
        """

        if self._project:
            window_icon = self._project.icon
            if not window_icon.isNull():
                return window_icon
            else:
                self._project.logger.warning(
                    '{} Project Icon not found: {}!'.format(
                        self._project.name.title(), self._project.icon_name + '.png'))

        return tpDcc.ResourcesMgr().icon('tpdcc')
