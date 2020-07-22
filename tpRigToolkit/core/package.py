# #! /usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """
# Module that contains base class to handle tpRigToolkit packages
# """
#
# from __future__ import print_function, division, absolute_import
#
# import os
# import pkgutil
# import inspect
# import logging
#
# from tpDcc.libs.qt.core import preferences, tool
#
# from PyFlow.Core import NodeBase, FunctionLibrary, PinBase
#
# from tpRigToolkit.core import factory
# # from tpNodeGraph.core.base import functionlib, factory
# # from tpNodeGraph.core.data import node, port
#
# LOGGER = logging.getLogger('tpRigToolkit')
#
#
# class Package(object):
#     """
#     Base class that defines packages that can be used to extend tpNodeGraph functionality
#     """
#
#     def __init__(self, module_path):
#         super(Package, self).__init__()
#
#         self._package_path = module_path
#
#         self._node_classes = dict()
#         self._node_paths = dict()
#         self._port_classes = dict()
#         self._port_paths = dict()
#         self._function_libs = dict()
#         self._function_lib_paths = dict()
#         self._ui_nodes_factory_classes = dict()
#         self._ui_nodes_factory_paths = dict()
#         self._ui_ports_factory_classes = dict()
#         self._ui_ports_factory_paths = dict()
#         self._input_widgets_factory_classes = dict()
#         self._input_widgets_factory_paths = dict()
#         self._tool_classes = dict()
#         self._tool_paths = dict()
#         self._preference_widget_classes = dict()
#         self._preference_widget_paths = dict()
#
#         self.load()
#
#     @property
#     def package_path(self):
#         """
#         Returns path where module is located
#         :return: str
#         """
#
#         return self._package_path
#
#     def load(self):
#         """
#         Load info of the module
#         :return:
#         """
#
#         if not self._package_path or not os.path.isdir(self._package_path):
#             LOGGER.warning('Module Path is not valid: "{}"!'.format(self._package_path))
#             return
#         for importer, mod_name, is_pkg in pkgutil.walk_packages([self._package_path]):
#             module = importer.find_module(mod_name).load_module(mod_name)
#             for cname, obj in inspect.getmembers(module, inspect.isclass):
#                 obj_name = obj.__name__
#                 try:
#                     obj_path = inspect.getfile(obj)
#                 except Exception:
#                     continue
#                 if issubclass(obj, NodeBase):
#                     self._node_classes[obj_name] = obj
#                     self._node_paths[obj_name] = obj_path
#                 elif issubclass(obj, PinBase):
#                     self._port_classes[obj_name] = obj
#                     self._port_paths[obj_name] = obj_path
#                 elif issubclass(obj, FunctionLibrary.FunctionLibraryBase):
#                     self._function_libs[obj_name] = obj(module_name=self.__class__.__name__)
#                     self._function_lib_paths[obj_name] = obj_path
#                 elif issubclass(obj, factory.NodeFactory):
#                     self._ui_nodes_factory_classes[obj_name] = obj
#                     self._ui_nodes_factory_paths[obj_name] = obj_path
#                 elif issubclass(obj, factory.PinFactory):
#                     self._ui_ports_factory_classes[obj_name] = obj
#                     self._ui_ports_factory_paths[obj_name] = obj_path
#                 elif issubclass(obj, factory.InputWidgetsFactory):
#                     self._input_widgets_factory_classes[obj_name] = obj
#                     self._input_widgets_factory_paths[obj_name] = obj_path
#                 elif issubclass(obj, tool.BaseTool):
#                     self._tool_classes[obj_name] = obj
#                     self._tool_paths[obj_name] = obj_path
#                 elif issubclass(obj, preferences.CategoryWidgetBase):
#                     self._preference_widget_classes[obj_name] = obj
#                     self._preference_widget_paths[obj_name] = obj_path
#
#     @property
#     def node_classes(self):
#         """
#         Returns registered node classes
#         :return: list(dict(str, class))
#         """
#
#         return self._node_classes
#
#     @property
#     def node_paths(self):
#         """
#         Returns registered node paths
#         :return: list(dict(str, str))
#         """
#
#         return self._node_paths
#
#     @property
#     def port_classes(self):
#         """
#         Returns registered port classes
#         :return: list(dict(str, class))
#         """
#
#         return self._port_classes
#
#     @property
#     def port_paths(self):
#         """
#         Returns registered port paths
#         :return: list(dict(str, str))
#         """
#
#         return self._port_paths
#
#     @property
#     def function_libs(self):
#         """
#         Returns registered function libs instances
#         :return: list(dict(str, FunctionLibrary))
#         """
#
#         return self._function_libs
#
#     @property
#     def function_lib_paths(self):
#         """
#         Returns registered function lib paths
#         :return: list(dict(str, str))
#         """
#
#         return self._function_lib_paths
#
#     @property
#     def ui_nodes_factory_classes(self):
#         """
#         Returns registered UI nodes factory classes
#         :return: list(dict(str, str))
#         """
#
#         return self._ui_nodes_factory_classes
#
#     @property
#     def ui_nodes_factory_paths(self):
#         """
#         Returns registered UI nodes factory paths
#         :return: list(dict(str, str))
#         """
#
#         return self._ui_nodes_factory_paths
#
#     @property
#     def ui_ports_factory_classes(self):
#         """
#         Returns registered UI ports factory classes
#         :return: list(dict(str, str))
#         """
#
#         return self._ui_ports_factory_classes
#
#     @property
#     def ui_ports_factory_paths(self):
#         """
#         Returns registered UI ports factory paths
#         :return: list(dict(str, str))
#         """
#
#         return self._ui_ports_factory_paths
#
#     @property
#     def input_widgets_factory_classes(self):
#         """
#         Returns registered input widgets factory classes
#         :return: list(dict(str, str))
#         """
#
#         return self._input_widgets_factory_classes
#
#     @property
#     def tool_classes(self):
#         """
#         Returns registered tool classes
#         :return: list(dict(str, class))
#         """
#
#         return self._tool_classes
#
#     @property
#     def tool_paths(self):
#         """
#         Returns registered tool paths
#         :return: list(dict(str, str))
#         """
#
#         return self._tool_paths
#
#     @property
#     def preference_widget_classes(self):
#         """
#         Returns registered preference widget classes
#         :return: list(dict(str, class))
#         """
#
#         return self._preference_widget_classes
#
#     @property
#     def preference_widget_paths(self):
#         """
#         Returns registered preference widget paths
#         :return: list(dict(str, str)
#         """
#
#         return self._preference_widget_paths
#
#     def has_node_classes(self):
#         """
#         Returns whether current module has available nodes or not
#         :return: bool
#         """
#
#         return bool(self._node_classes)
#
#     def has_port_classes(self):
#         """
#         Returns whether current module has available ports or not
#         :return: bool
#         """
#
#         return bool(self._port_classes)
#
#     def has_ui_nodes_factory_classes(self):
#         """
#         Returns whether current module has available UI nodes factories or not
#         :return: bool
#         """
#
#         return bool(self._ui_nodes_factory_classes)
#
#     def has_function_lib_classes(self):
#         """
#         Returns whether current module has available function libraries or not
#         :return: bool
#         """
#
#         return bool(self._function_libs)
