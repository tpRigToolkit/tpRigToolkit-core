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

import tpDcc.loader as dcc_loader
from tpDcc.libs.python import contexts
from tpDcc.core import dcc as core_dcc
from tpDcc.managers import configs, resources, libs, tools, menus
from tpDcc.libs.qt.managers import toolsets as qt_toolsets

import tpRigToolkit.config
import tpRigToolkit.toolsets

# =================================================================================

PACKAGE = 'tpRigToolkit'

# =================================================================================


def init(import_libs=True, dev=False):
    """
    Initializes tpRigToolkit module
    :param import_libs: bool, Whether to import deps libraries by default or not
    :param dev: bool, Whether tpRigToolkit is initialized in dev mode or not
    """

    logger = create_logger(dev=dev)

    if import_libs:
        dcc_loader.init(dev=dev)

    dcc_loader_module = core_dcc.get_dcc_loader_module('tpRigToolkit.dccs')
    if dcc_loader_module:
        dcc_loader_module.init(dev=dev)

    register_resources()

    # Register configuration files
    configs.register_package_configs(PACKAGE, os.path.dirname(tpRigToolkit.config.__file__))
    core_config = configs.get_config('tpRigToolkit-core', environment='development' if dev else 'production')
    if not core_config:
        logger.warning(
            'tpRigToolkit-core configuration file not found! '
            'Make sure that you have tpRigToolkit-config package installed!')
        return None

    libs_to_load = core_config.get('libs', list())
    tools_to_load = core_config.get('tools', list())

    with contexts.Timer('Libraries loaded', logger=logger):
        libs.LibsManager().register_package_libs(PACKAGE, libs_to_register=libs_to_load, dev=dev)
        libs.LibsManager().load_registered_libs(PACKAGE)

    with contexts.Timer('Tools loaded', logger=logger):
        tools.ToolsManager().register_package_tools(PACKAGE, tools_to_register=tools_to_load, dev=dev)
        tools.ToolsManager().load_registered_tools(PACKAGE)

    with contexts.Timer('Toolsets loaded', logger=logger):
        qt_toolsets.ToolsetsManager().register_path(
            PACKAGE, os.path.dirname(os.path.abspath(tpRigToolkit.toolsets.__file__)))
        qt_toolsets.ToolsetsManager().load_registered_toolsets(package_name=PACKAGE, tools_to_load=tools_to_load)

    with contexts.Timer('Menu created', logger=logger):
        menus.create_menus(package_name=PACKAGE, dev=dev)


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


def register_resources():
    """
    Registers tpDcc.libs.qt resources path
    """

    resources_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')
    resources.register_resource(resources_path, key='tpRigToolkit-core')


create_logger()
