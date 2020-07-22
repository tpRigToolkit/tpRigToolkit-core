#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains manager that handles the registration of new tpRigToolkit plugins
"""

from __future__ import print_function, division, absolute_import

import tpDcc as tp
from tpDcc.libs.python import decorators

from tpRigToolkit.core import log, plugin


class PluginsManager(object):

    def __init__(self):
        super(PluginsManager, self).__init__()

        self._plugin_classes = list()
        self._plugins = set()

    # ============================================================================================================
    # PROPERTIES
    # ============================================================================================================

    @property
    def plugin_classes(self):
        return self._plugin_classes

    # ============================================================================================================
    # BASE
    # ============================================================================================================

    def get_registered_plugins(self, class_name_filters=None):
        """
        Returns a list with all registered plugin instances
        :param class_name_filters: str, String to filter plugins to search for
        :return: list(str)
        """

        if class_name_filters is None:
            class_name_filters = list()

        if len(class_name_filters) == 0:
            return self._plugins
        else:
            result = list()
            for plugin_inst in self._plugins:
                if plugin_inst.__class__.__name__ in class_name_filters:
                    result.append(plugin_inst)

            return result

    def is_plugin_opened(self, plugin_name):
        """
        Returns whether or not a plugin with given name is already opened
        :param plugin_name: str
        :return: bool
        """

        return plugin_name in [t.NAME for t in self._plugins]

    def get_plugin_instance(self, plugin_name):
        """
        Returns plugin instance of the given plugin
        :param plugin_name: str
        :return: list(object)
        """

        plugins_found = list()
        for plugin_instance in self._plugins:
            if plugin_instance.NAME == plugin_name:
                plugins_found.append(plugin_instance)

        return plugins_found

    def register_plugin_class(self, plugin_class):
        """
        Registers given tool class
        :param plugin_class: cls
        """

        if not plugin_class or plugin_class in self._plugin_classes:
            return

        self._plugin_classes.append(plugin_class)

    def invoke_dock_plugin_by_name(self, plugin_name, parent_window=None, settings=None):
        plugin_class = None
        parent_window = parent_window or tp.Dcc.get_main_window()
        for t in self._plugin_classes:
            if t.NAME == plugin_name:
                plugin_class = t
                break
        if not plugin_class:
            log.warning('No registered tool found with name: "{}"'.format(plugin_name))
            return None

        tool_instance = plugin.create_plugin_instance(plugin_class, self._plugins)
        if not tool_instance:
            return None
        if plugin_class.NAME in [t.NAME for t in self._plugins] and plugin_class.IS_SINGLETON:
            return tool_instance

        self.register_plugin_instance(tool_instance)
        if settings:
            tool_instance.restore_state(settings)
            if not self.restoreDockWidget(tool_instance):
                pass
        else:
            parent_window.addDockWidget(tool_instance.DEFAULT_DOCK_AREA, tool_instance)

        tool_instance.app = parent_window
        tool_instance.show_plugin()

        return tool_instance

    def register_plugin_instance(self, instance):
        """
        Internal function that registers given plugin instance
        Used to prevent plugin classes being garbage collected and to save plugin widgets states
        :param instance: Tool
        """

        self._plugins.add(instance)

    def unregister_plugin_instance(self, instance):
        """
        Internal function that unregister plugin instance
        :param instance: Tool
        """

        if instance not in self._plugins:
            return False
        self._plugins.remove(instance)

        return True


@decorators.Singleton
class PluginsManagerSingleton(PluginsManager, object):
    def __init__(self):
        PluginsManager.__init__(self)
