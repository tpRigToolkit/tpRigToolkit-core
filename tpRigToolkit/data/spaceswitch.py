#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains Space Switch data
"""

from __future__ import print_function, division, absolute_import

from tpDcc.core import data
from tpDcc.libs.qt.widgets.library import savewidget

from tpRigToolkit.core import data as rig_data


class SpaceSwitchFileData(data.CustomData, object):
    def __init__(self, name=None, path=None):
        super(SpaceSwitchFileData, self).__init__(name=name, path=path)

    @staticmethod
    def get_data_type():
        return 'dcc.spaceswitch'

    @staticmethod
    def get_data_extension():
        return 'sswitch'

    @staticmethod
    def get_data_title():
        return 'Space Switch'


class SpaceSwitchPreviewWidget(rig_data.DataPreviewWidget, object):
    def __init__(self, item, parent=None):
        super(SpaceSwitchPreviewWidget, self).__init__(item=item, parent=parent)


class SpaceSwitchSaveWidget(savewidget.BaseSaveWidget, object):
    def __init__(self, item, settings, temp_path=None, parent=None):
        super(SpaceSwitchSaveWidget, self).__init__(item, settings, temp_path, parent=parent)

    def ui(self):
        super(SpaceSwitchSaveWidget, self).ui()

        from tpRigToolkit.tools.spaceswitcher.widgets import spaceswitcher

        self._space_switcher = spaceswitcher.SpaceSwitcherWidget()
        self._extra_layout.addWidget(self._space_switcher)


class SpaceSwitch(rig_data.DataItem, object):
    Extension = '.{}'.format(SpaceSwitchFileData.get_data_extension())
    Extensions = ['.{}'.format(SpaceSwitchFileData.get_data_extension())]
    MenuOrder = 6
    MenuName = SpaceSwitchFileData.get_data_title()
    MenuIconName = 'spaceswitch.png'
    TypeIconName = 'spaceswitch.png'

    TypeIconName = 'spaceswitch.png'
    DataType = SpaceSwitchFileData.get_data_type()
    DefaultDataFileName = 'new_space_switch'
    CreateWidgetClass = SpaceSwitchSaveWidget
    PreviewWidgetClass = SpaceSwitchPreviewWidget

    def __init__(self, *args, **kwargs):
        super(SpaceSwitch, self).__init__(*args, **kwargs)

        self.set_data_class(SpaceSwitchFileData)
