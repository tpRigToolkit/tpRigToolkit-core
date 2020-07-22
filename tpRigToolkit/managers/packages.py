#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementation for node manager
"""

from __future__ import print_function, division, absolute_import

import os
import pkgutil
import logging
import traceback
from collections import defaultdict

from tpDcc.libs.python import python, decorators

from tpRigToolkit import packages
# from tpRigToolkit.core import package

LOGGER = logging.getLogger('tpRigToolkit')

"""
TODO
This is class is related to PyFlow packages implementation. We do not need altough before removing it we should
check if this can be useful for the RigNode implementation
"""


class PackagesManager(object):

    ENV_VAR_NAME = 'TPRIGTOOLKIT_PACKAGE_PATHS'
    ENV_VAR_PATHS_DELIMITER = ';'

    def __init__(self, package_paths=None):
        super(PackagesManager, self).__init__()

        self._registered_modules = dict()
        self._registered_module_paths = dict()
        self._registered_ui_nodes_factories = dict()
        self._registered_ui_ports_factories = dict()
        self._registered_input_widgets_factories = dict()
        self._registered_tools = defaultdict(list)
        self._registered_prefs = defaultdict(list)

        self._module_paths = python.force_list(package_paths) if package_paths else list()
        self._update_module_paths_from_environment()

    @property
    def registered_modules(self):
        """
        Returns dict with the registered modules
        :return: dict
        """

        return self._registered_modules

    @property
    def registered_modules_paths(self):
        """
        Returns dict containing registered modules paths
        :return: dict
        """

        return self._registered_module_paths

    @property
    def registered_ui_nodes_factories(self):
        """
        Returns dict containing registered UI nodes factories
        :return: dict
        """

        return self._registered_ui_nodes_factories

    @property
    def registered_ui_ports_factories(self):
        """
        Returns dict containing registered UI ports factories
        :return: dict
        """

        return self._registered_ui_ports_factories

    @property
    def registered_input_widgets_factories(self):
        """
        Returns dict containing registered input widgets
        :return: dict
        """

        return self._registered_input_widgets_factories

    @property
    def registered_tools(self):
        """
        Returns dict containing registered tools
        :return: dict
        """

        return self._registered_tools

    @property
    def registered_prefs(self):
        """
        Returns dict containing registered preference widgets
        :return: dict
        """

        return self._registered_prefs

    def register_module_path(self, module_path):
        """
        Registers given path into the manager so path is taking into account when loading tpNodeGrpah modules
        :param module_path: str
        """

        if not module_path or not os.path.isdir(module_path) or module_path in self._module_paths:
            return

        self._module_paths.append(module_path)
        self._load_modules(module_path)

    def register_ui_node_factory(self, module_name, factory):
        """
        Registers given factory and maps it to given module name
        :param module_name: str
        :param factory: Factory
        """

        if module_name not in self._registered_ui_nodes_factories:
            self._registered_ui_nodes_factories[module_name] = factory

    def register_ui_port_factory(self, module_name, factory):
        """
        Registers given factory and maps it to given module name
        :param module_name: str
        :param factory: Factory
        """

        if module_name not in self._registered_ui_ports_factories:
            self._registered_ui_ports_factories[module_name] = factory

    def register_input_widgets_factory(self, module_name, factory):
        """
        Registers given factory and maps it to given module name
        :param module_name: str
        :param factory: Factory
        """

        if module_name not in self._registered_input_widgets_factories:
            self._registered_input_widgets_factories[module_name] = factory

    def register_tool(self, module_name, tool_class):
        """
        Registers given tool class and maps it to given module name
        :param module_name: str
        :param tool_class: cls
        """

        registered_tool_names = [tool.NAME for tool in self._registered_tools[module_name]]
        if tool_class.NAME not in registered_tool_names:
            self._registered_tools[module_name].append(tool_class)
            tool_class.MODULE_NAME = module_name

    def register_preference_widget(self, module_name, preference_widget_class):
        """
        Registers given preference widget class and maps it to the given module name
        :param module_name: str
        :param preference_widget_class: cls
        """

        registered_prefs_categories = [pref.CATEGORY for pref in self._registered_prefs[module_name]]
        if preference_widget_class.CATEGORY not in registered_prefs_categories:
            self._registered_prefs[module_name].append(preference_widget_class)
            preference_widget_class.MODULE_NAME = module_name

    def initialize(self):
        import PyFlow
        self._load_modules()

    def _load_modules(self, module_path=None):
        """
        Function that loads all the modules located in the registered paths
        """

        if not module_path:
            module_paths = self._module_paths
        else:
            module_paths = [module_path]

        for importer, mod_name, is_pkg in pkgutil.iter_modules(module_paths):
            try:
                if is_pkg:
                    mod = importer.find_module(mod_name).load_module(mod_name)
                    mod_path = mod.__path__[0]
                    if hasattr(mod, 'MODULE_NAME'):
                        module_name = mod.MODULE_NAME
                    else:
                        module_name = mod_name
                    mod_class = type(module_name, (package.Package,), {})
                    new_module = mod_class(mod_path)
                    self._registered_modules[module_name] = new_module
                    self._registered_module_paths[module_name] = os.path.normpath(mod_path)
            except Exception as e:
                LOGGER.error('Error on Module: {} : \n{}'.format(mod_name, str(e)))
                LOGGER.error(traceback.format_exc())
                continue

        registered_internal_port_data_types = set()

        for name, mod in self._registered_modules.items():
            module_name = mod.__class__.__name__

            for n in mod.node_classes.values():
                n.MODULE_NAME = module_name

            for p in mod.port_classes.values():
                p.MODULE_NAME = module_name
                if p.is_value_port():
                    internal_type = p.internal_data_structure()
                    if internal_type in registered_internal_port_data_types:
                        raise Exception(
                            'Port with "{}" internal data type already been registered!'.format(internal_type))
                    registered_internal_port_data_types.add(internal_type)

            ui_nodes_factory = mod.ui_nodes_factory_classes
            if ui_nodes_factory:
                self.register_ui_node_factory(module_name, ui_nodes_factory)

            ui_ports_factory = mod.ui_ports_factory_classes
            if ui_ports_factory:
                self.register_ui_port_factory(name, ui_ports_factory)

            input_widgets_factory = mod.input_widgets_factory_classes
            if input_widgets_factory:
                self.register_input_widgets_factory(name, input_widgets_factory)

            for tool_class in mod.tool_classes.values():
                supported_softwares = tool_class.SUPPORTED_SOFTWARES
                if 'any' not in supported_softwares:
                    continue
                self.register_tool(name, tool_class)

            for pref_widget_class in mod.preference_widget_classes.values():
                self.register_preference_widget(name, pref_widget_class)

    def _update_module_paths_from_environment(self):
        """
        Internal function that updates registered module paths by taking into account current environment variables
        """

        def _recurse_module_paths(module_path):
            """
            Recursively loops through given path searching modules
            :param module_path: str
            :return: list(str)
            """

            paths_found = list()
            for sub_folder in os.listdir(module_path):
                sub_folder_path = os.path.join(module_path, sub_folder)
                if os.path.isdir(sub_folder_path):
                    if sub_folder_path.endswith('Package') or sub_folder_path.endswith('package'):
                        paths_found.append(sub_folder_path)

            return paths_found

        module_paths = packages.__path__

        if self.ENV_VAR_NAME in os.environ:
            extra_paths = os.environ.get(self.ENV_VAR_NAME).rstrip(self.ENV_VAR_PATHS_DELIMITER)
            for modules_root in extra_paths.split(self.ENV_VAR_PATHS_DELIMITER):
                if os.path.isdir(modules_root):
                    paths = _recurse_module_paths(modules_root)
                    extra_paths.extend(paths)

            module_paths.extend(extra_paths)

        for p in module_paths:
            self.register_module_path(p)


@decorators.Singleton
class PackagesManagerSingleton(PackagesManager, object):
    def __init__(self):
        PackagesManager.__init__(self)
