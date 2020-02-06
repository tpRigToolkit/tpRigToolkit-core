#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialization module for tpRigToolkit
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import inspect
import logging.config
from collections import OrderedDict

import tpDccLib as tp
from tpPyUtils import python


def init(do_reload=False, import_libs=True, dev=False):
    """
    Initializes tpRigToolkit module
    :param do_reload: bool, Whether to reload modules or not
    :param import_libs: bool, Whether to import deps libraries by default or not
    :param dev: bool, Whether tpRigToolkit is initialized in dev mode or not
    """

    # Load logger configuration
    logging.config.fileConfig(get_logging_config(), disable_existing_loggers=False)

    from tpPyUtils import importer

    class tpRigToolkit(importer.Importer, object):
        def __init__(self, debug=False):
            super(tpRigToolkit, self).__init__(module_name='tpRigToolkit', debug=debug)

        def get_module_path(self):
            """
            Returns path where tpNameIt module is stored
            :return: str
            """

            try:
                mod_dir = os.path.dirname(
                    inspect.getframeinfo(inspect.currentframe()).filename)
            except Exception:
                try:
                    mod_dir = os.path.dirname(__file__)
                except Exception:
                    try:
                        import tpRigToolkit
                        mod_dir = tpRigToolkit.__path__[0]
                    except Exception:
                        return None

            return mod_dir

    packages_order = [
        'tpRigToolkit.utils',
        'tpRigToolkit.core',
        'tpRigToolkit.widgets'
    ]

    if import_libs:
        import tpPyUtils
        tpPyUtils.init(do_reload=do_reload)
        import tpDccLib
        tpDccLib.init(do_reload=do_reload)
        import tpQtLib
        tpQtLib.init(do_reload=do_reload)
        import tpNameIt
        tpNameIt.init(do_reload=do_reload)

    rigtoolkit_importer = importer.init_importer(importer_class=tpRigToolkit, do_reload=False, debug=dev)
    rigtoolkit_importer.import_packages(
        order=packages_order,
        only_packages=False)
    if do_reload:
        rigtoolkit_importer.reload_all()

    create_logger_directory()

    from tpRigToolkit.core import resource
    resources_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')
    resource.ResourceManager().register_resource(resources_path)

    register_tools(dev=dev)


def create_logger_directory():
    """
    Creates tpRigToolkit logger directory
    """

    logger_dir = os.path.normpath(os.path.join(os.path.expanduser('~'), 'tpRigToolkit', 'logs'))
    if not os.path.isdir(logger_dir):
        os.makedirs(logger_dir)


def get_logging_config():
    """
    Returns logging configuration file path
    :return: str
    """

    create_logger_directory()

    return os.path.normpath(os.path.join(os.path.dirname(__file__), '__logging__.ini'))


def get_resources_path():
    """
    Returns path where resources for tpRigToolkit are stored
    :return: str
    """

    return os.path.normpath(os.path.join(os.path.dirname(__file__), 'resources'))


def register_tools(dev=True):
    """
    Function that register all available tools for tpRigToolkit
    """

    import tpRigToolkit
    from tpRigToolkit.core import config

    if python.is_python2():
        import pkgutil as loader
    else:
        import importlib as loader

    environment = 'development' if dev else 'production'

    core_config = config.get_config('tpRigToolkit-core')
    tools = core_config.get('tools', list())
    tools_to_register = OrderedDict()
    tools_path = '{}.tools.{}'
    for tool_name in tools:
        for pkg in ['tpRigToolkit']:
            pkg_path = tools_path.format(pkg, tool_name)
            pkg_loader = loader.find_loader(pkg_path)
            if tool_name not in tools_to_register:
                tools_to_register[tool_name] = list()
            if pkg_loader is not None:
                tools_to_register[tool_name].append(pkg_loader)

    for pkg_loaders in tools_to_register.values():
        tpRigToolkit.ToolsMgr().register_tool(pkg_loaders=pkg_loaders, environment=environment)
