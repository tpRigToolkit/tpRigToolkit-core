#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains data manager widgets
"""

from __future__ import print_function, division, absolute_import

import os
import logging
import pkgutil
import inspect
import traceback

from tpDcc.core import data as core_data, scripts

LOGGER = logging.getLogger('tpRigToolkit-core')

_DIRECTORIES = list()
_ASK_NAME_ON_CREATION = True
_LOADED_DATA_CLASSES = list()

STANDARD_DATA_CLASSES = [scripts.ScriptManifestData, scripts.ScriptPythonData]


def get_all_data_classes(_reload=False):
    """
    Returns all data widgets loaded by the manager
    :return: list<DataWidget>
    """

    return STANDARD_DATA_CLASSES + load_data_classes(_reload=_reload)


def add_directory(directory, do_update=False):
    """
    Adds a new directory where data should be find
    :param directory: str
    :param do_update: bool
    """

    if directory not in _DIRECTORIES:
        _DIRECTORIES.append(directory)
        if do_update:
            load_data_classes()


def set_directories(directories):
    """
    Sets the directories where data should be find
    :param directories: list(str)
    """

    new_dir = False
    for d in directories:
        if d not in directories:
            new_dir = True
            directories.append(d)

    if new_dir:
        load_data_classes()


def load_data_classes(_reload=False):
    """
    Loads all data classes
    :param _reload: bool
    :return: list
    """

    for d in _DIRECTORIES:
        loaded_classes = _load_data_classes(directory=d, _reload=_reload)
        _LOADED_DATA_CLASSES.extend(loaded_classes)

    return _LOADED_DATA_CLASSES


def get_available_types():
    """
    Returns a list with all available data types
    :return: list<str>
    """

    data_types = list()
    for data in get_all_data_classes():
        data_types.append(data.get_data_type())

    return data_types


def get_type_instance(data_type):
    """
    Returns a new instance of data type
    :param data_type: str, type of data type instance we want to create
    :return: variant
    """

    for data in get_all_data_classes():
        if data.is_type_match(data_type):
            return data()


def _load_data_classes(directory, _reload=False):

    imported = list()

    if directory is None or not os.path.exists(directory):
        LOGGER.warning('Data Path {} does not exists!'.format(directory))
        return imported

    for loader, mod_name, is_package in pkgutil.walk_packages([directory]):
        try:
            module = loader.find_module(mod_name).load_module(mod_name)
            if _reload:
                reload(module)
            for cname, obj in inspect.getmembers(module, inspect.isclass):
                if not issubclass(obj, core_data.FileData):
                    continue
                # globals()[cname] = obj
                imported.append(obj)
        except Exception as e:
            LOGGER.warning('Aborting loading Data Class {} : {}'.format(mod_name, str(e)))
            LOGGER.debug(traceback.format_exc())

    return sorted(list(set(imported)))
