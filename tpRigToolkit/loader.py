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
import logging


def init(do_reload=False, dev=False):
    """
    Initializes tpRigToolkit module
    :param do_reload: bool, Whether to reload modules or not
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
