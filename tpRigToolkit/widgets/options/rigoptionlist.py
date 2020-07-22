#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget to handle editable options for rigs
"""

from __future__ import print_function, division, absolute_import

from functools import partial

from Qt.QtWidgets import *

import tpDcc as tp
from tpDcc.libs.qt.widgets.options import optionlist

from tpRigToolkit.widgets.options import factory


class RigOptionList(optionlist.OptionList, object):

    FACTORY_CLASS = factory.RigOptionsFactorySingleton

    def __init__(self, parent=None, option_object=None):
        super(RigOptionList, self).__init__(parent=parent, option_object=option_object)

    def _create_context_menu(self, menu, parent=None):
        create_menu = super(RigOptionList, self)._create_context_menu(menu=menu, parent=parent)

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

        return create_menu
