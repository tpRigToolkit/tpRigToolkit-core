#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains factory class to create tpRigToolkit options
"""

from tpDcc.libs.python import python
from tpDcc.libs.qt.widgets.options import factory

from tpRigToolkit.widgets.options import bone, control, bonecontrollink


def add_option(option_type, name=None, value=None, parent=None, main_widget=None, option_object=None):
    if option_type == 'rigcontrol':
        new_option = _add_control_rig(
            name=name, value=value, parent=parent, main_widget=main_widget, option_object=option_object)
    elif option_type == 'bone':
        new_option = _add_bone(name=name, value=value, parent=parent, main_widget=main_widget)
    elif option_type == 'boneList':
        new_option = _add_bone_list(name=name, value=value, parent=parent, main_widget=main_widget)
    elif option_type == 'boneControlLink':
        new_option = _add_bone_control_link(
            name=name, value=value, parent=parent, main_widget=main_widget, option_object=option_object)
    else:
        new_option = factory.add_option(option_type, name, value, parent, main_widget, option_object)

    return new_option


def _add_control_rig(name='rigcontrol', value=None, parent=None, main_widget=None, option_object=None):
    if type(name) == bool:
        name = 'rigcontrol'

    control_option = control.RigControlOption(
        name=name, parent=parent, main_widget=main_widget, rig_object=option_object)
    control_option.set_value(value)

    return control_option


def _add_bone(name='bone', value=None, parent=None, main_widget=None):
    if type(name) == bool:
        name = 'bone'

    bone_option = bone.BoneOption(name=name, parent=parent, main_widget=main_widget)
    bone_option.set_value(value)

    return bone_option


def _add_bone_list(name='boneList', value=None, parent=None, main_widget=None):
    if type(name) == bool:
        name = 'boneList'

    value = python.force_list(value)
    bone_list_option = bone.BoneOptionList(name=name, parent=parent, main_widget=main_widget)
    bone_list_option.set_value(value)

    return bone_list_option


def _add_bone_control_link(name='boneControlLink', value=None, parent=None, main_widget=None, option_object=None):
    if type(name) == bool:
        name = 'boneControlLink'

    bone_control_link_option = bonecontrollink.BoneControlLinkOption(
        name=name, parent=parent, main_widget=main_widget, rig_object=option_object)
    bone_control_link_option.set_value(value or list())

    return bone_control_link_option
