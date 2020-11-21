#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains manager that handles the registration of new tpRigToolkit plugins
"""

from __future__ import print_function, division, absolute_import

import logging

from tpDcc import dcc

from tpRigToolkit.core import plugin

LOGGER = logging.getLogger('tpRigToolkit-core')

_PLUGIN_CLASSES = list()
_PLUGINS = set()


def plugin_classes():
    return _PLUGIN_CLASSES


def get_registered_plugins(class_name_filters=None):
    """
    Returns a list with all registered plugin instances
    :param class_name_filters: str, String to filter plugins to search for
    :return: list(str)
    """

    if class_name_filters is None:
        class_name_filters = list()

    if len(class_name_filters) == 0:
        return _PLUGINS
    else:
        result = list()
        for plugin_inst in _PLUGINS:
            if plugin_inst.__class__.__name__ in class_name_filters:
                result.append(plugin_inst)

        return result


def is_plugin_opened(plugin_name):
    """
    Returns whether or not a plugin with given name is already opened
    :param plugin_name: str
    :return: bool
    """

    return plugin_name in [t.NAME for t in _PLUGINS]


def get_plugin_instance(plugin_name):
    """
    Returns plugin instance of the given plugin
    :param plugin_name: str
    :return: list(object)
    """

    plugins_found = list()
    for plugin_instance in _PLUGINS:
        if plugin_instance.NAME == plugin_name:
            plugins_found.append(plugin_instance)

    return plugins_found


def register_plugin_class(plugin_class):
    """
    Registers given tool class
    :param plugin_class: cls
    """

    if not plugin_class or plugin_class in _PLUGIN_CLASSES:
        return

    _PLUGIN_CLASSES.append(plugin_class)


def invoke_dock_plugin_by_name(plugin_name, parent_window=None, settings=None, **kwargs):
    plugin_class = None
    parent_window = parent_window or dcc.get_main_window()
    for t in _PLUGIN_CLASSES:
        if t.NAME == plugin_name:
            plugin_class = t
            break
    if not plugin_class:
        LOGGER.warning('No registered tool found with name: "{}"'.format(plugin_name))
        return None

    tool_instance = plugin.create_plugin_instance(plugin_class, _PLUGINS, **kwargs)
    if not tool_instance:
        return None
    if plugin_class.NAME in [t.NAME for t in _PLUGINS] and plugin_class.IS_SINGLETON:
        return tool_instance

    register_plugin_instance(tool_instance)
    if settings:
        tool_instance.restore_state(settings)
        # if not restoreDockWidget(tool_instance):
        #     pass
    else:
        parent_window.addDockWidget(tool_instance.DEFAULT_DOCK_AREA, tool_instance)

    tool_instance.app = parent_window
    tool_instance.show_plugin()

    return tool_instance


def register_plugin_instance(instance):
    """
    Internal function that registers given plugin instance
    Used to prevent plugin classes being garbage collected and to save plugin widgets states
    :param instance: Tool
    """

    _PLUGINS.add(instance)


def unregister_plugin_instance(instance):
    """
    Internal function that unregister plugin instance
    :param instance: Tool
    """

    if instance not in _PLUGINS:
        return False
    _PLUGINS.remove(instance)

    return True
