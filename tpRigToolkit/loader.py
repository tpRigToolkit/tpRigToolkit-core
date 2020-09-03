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
import logging.config

import tpDcc
from tpRigToolkit import register

# =================================================================================

PACKAGE = 'tpRigToolkit'

# =================================================================================


def init(import_libs=True, dev=False):
    """
    Initializes tpRigToolkit module
    :param import_libs: bool, Whether to import deps libraries by default or not
    :param dev: bool, Whether tpRigToolkit is initialized in dev mode or not
    """

    if dev:
        register.cleanup()

    logger = create_logger(dev=dev)

    register.register_class('logger', logger)

    if import_libs:
        import tpDcc.loader as dcc_loader
        dcc_loader.init(dev=dev)

    # We do the importer and registering of the classes after ensuring tpDcc is loaded
    from tpRigToolkit.managers import data as data_manager, names as names_manager, packages as packages_manager
    from tpRigToolkit.managers import plugins as plugins_manager, scripts as scripts_manager
    from tpRigToolkit.widgets import window, dialog

    register.register_class('DataMgr', data_manager.DataManagerSingleton)
    register.register_class('NamesMgr', names_manager.RigToolkitNamesManagerSingleton)
    register.register_class('PackagesMgr', packages_manager.PackagesManagerSingleton)
    register.register_class('PluginsMgr', plugins_manager.PluginsManagerSingleton)
    register.register_class('ScriptsMgr', scripts_manager.ScriptsManagerSingleton)
    register.register_class('Window', window.MainWindow)
    register.register_class('Dialog', dialog.MainDialog)

    # skip_modules = ['{}.{}'.format(PACKAGE, name) for name in ['libs', 'tools']]
    # importer.init_importer(package=PACKAGE, skip_modules=skip_modules)

    init_managers(dev=dev)

    dcc_loader_module = tpDcc.get_dcc_loader_module('tpRigToolkit.dccs')
    if dcc_loader_module:
        dcc_loader_module.init(dev=dev)


def init_managers(dev=True):
    """
    Initializes all tpDcc managers
    """

    import tpDcc
    import tpRigToolkit
    from tpRigToolkit import config, toolsets

    # Register resources
    resources_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')
    tpDcc.ResourcesMgr().register_resource(resources_path)

    # Register configuration files
    tpDcc.ConfigsMgr().register_package_configs('tpRigToolkit', os.path.dirname(config.__file__))

    core_config = tpDcc.ConfigsMgr().get_config(
        'tpRigToolkit-core',
        environment='development' if dev else 'production'
    )
    if not core_config:
        tpDcc.logger.warning(
            'tpRigToolkit-core configuration file not found! '
            'Make sure that you have tpRigToolkit-config package installed!')
        return None

    # Register resources
    resources_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'resources'))
    tpDcc.ResourcesMgr().register_resource(resources_path)

    # Register tools
    tools_to_load = core_config.get('tools', list())
    tpDcc.ToolsMgr().register_package_tools(pkg_name=PACKAGE, tools_to_register=tools_to_load, dev=dev)
    tpDcc.ToolsMgr().load_registered_tools(PACKAGE)

    # Register toolsets
    tpDcc.ToolsetsMgr().register_path(PACKAGE, os.path.dirname(os.path.abspath(toolsets.__file__)))
    tpDcc.ToolsetsMgr().load_registered_toolsets(package_name=PACKAGE, tools_to_load=tools_to_load)

    # Create tpRigToolkit menu
    # The creation of the menu depends on the registered toolsets
    tpDcc.MenusMgr().create_menus(package_name=PACKAGE, dev=dev)

    # Initialize data and scripts manager
    tpRigToolkit.DataMgr()
    tpRigToolkit.ScriptsMgr()


def create_logger(dev=False):
    """
    Returns logger of current module
    """

    logger_dir = os.path.normpath(os.path.join(os.path.expanduser('~'), 'tpRigToolkit', 'logs'))
    if not os.path.isdir(logger_dir):
        os.makedirs(logger_dir)

    logging_config = os.path.normpath(os.path.join(os.path.dirname(__file__), '__logging__.ini'))

    logging.config.fileConfig(logging_config, disable_existing_loggers=False)
    logger = logging.getLogger('tpRigToolkit')
    if dev:
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)

    return logger
