#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains data manager implementation
"""

from __future__ import print_function, division, absolute_import

import os
import pkgutil
import inspect
import traceback

from tpDcc.core import scripts, data as core_data
from tpDcc.libs.python import path, decorators
from tpDcc.libs.qt.widgets.library import manager

import tpRigToolkit
from tpRigToolkit.core import data, utils


class DataManager(manager.LibraryManager, object):
    def __init__(self, settings=None, directories=None, update_on_init=True):
        super(DataManager, self).__init__(settings=settings)

        data_dirs = utils.get_data_files_directory()
        data_dirs.extend(directories or list())

        self._directories = list(set(data_dirs))
        self._loaded_data_items = list()
        self._loaded_data_classes = list()

        self.standard_data_classes = [
            scripts.ScriptManifestData,
            scripts.ScriptPythonData
        ]

        if update_on_init:
            self.update_data_classes()
            self.update_data_items()

    def get_all_data_classes(self, do_reload=False):
        """
        Returns all data classes loaded by the manager
        :return: list<DataWidget>
        """

        return self.standard_data_classes + self.update_data_classes(do_reload=do_reload)

    def get_all_data_items(self, do_reload=False):
        """
        Returns all data item classes loaded by the manager
        :param do_reload:
        :return:
        """

        return self.update_data_items(do_reload=do_reload)

    def get_available_types(self):
        """
        Returns a list with all available data types
        :return: list<str>
        """

        data_types = list()
        for data_class in self.get_all_data_classes():
            data_types.append(data_class.get_data_type())

        return data_types

    def add_directory(self, directory, do_update=False):
        """
        Adds a new directory where data should be find
        :param directory: str
        :param do_update: bool
        """

        if directory not in self._directories:
            self._directories.append(directory)
            if do_update:
                self.update_data_classes()

    def set_directories(self, directories):
        """
        Sets the directories where data should be find
        :param directories: list(str)
        """

        new_dir = False
        for d in directories:
            if d not in self._directories:
                new_dir = True
                self._directories.append(d)

        if new_dir:
            self.update_data_classes(do_reload=True)
            self.update_data_items(do_reload=True)

    def update_data_classes(self, do_reload=False):
        """

        :param do_reload:
        :return:
        """

        if not self._loaded_data_classes or do_reload:
            for d in self._directories:
                self._loaded_data_classes.extend(self._load_data_classes(d))

        return self._loaded_data_classes

    def update_data_items(self, do_reload=False):
        """
        Adds custom dat files located in the current data manager registered directories
        """

        if not self._loaded_data_items or do_reload:
            for d in self._directories:
                self._loaded_data_items.extend(self._load_data_items(d))
            for data_item in self._loaded_data_items:
                self.register_item(data_item)

        return self._loaded_data_items

    def get_type_instance(self, data_type):
        """
        Returns a new instance of data type
        :param data_type: str, type of data type instance we want to create
        :return: variant
        """

        for data_class in self.get_all_data_classes():
            if data_class.is_type_match(data_type):
                return data_class()

    def _load_data_classes(self, directory):

        imported = list()

        if directory is None or not os.path.exists(directory):
            tpRigToolkit.logger.warning('Data Path {} does not exists!'.format(directory))
            return imported

        for loader, mod_name, is_package in pkgutil.walk_packages([directory]):
            try:
                module = loader.find_module(mod_name).load_module(mod_name)
                for cname, obj in inspect.getmembers(module, inspect.isclass):
                    if not issubclass(obj, core_data.FileData):
                        continue
                    # globals()[cname] = obj
                    imported.append(obj)
            except Exception as e:
                tpRigToolkit.logger.warning('Aborting loading Data Class {} : {}'.format(mod_name, str(e)))
                tpRigToolkit.logger.debug(traceback.format_exc())

        # TODO: Not working in Python 3
        # return sorted(list(set(imported)))

        return list(set(imported))

    def _load_data_items(self, directory):
        """
        Internal function that loads data classes
        :param directory: str
        :return: list
        """

        data_classes = list()

        if directory is None or not path.is_dir(directory):
            tpRigToolkit.logger.warning('Data Path {} does not exists!'.format(directory))
            return data_classes

        for loader, mod_name, is_package in pkgutil.walk_packages([directory]):
            try:
                module = loader.find_module(mod_name).load_module(mod_name)
                for cname, obj in inspect.getmembers(module, inspect.isclass):
                    if not issubclass(obj, data.DataItem):
                        continue
                    data_classes.append(obj)
            except Exception as e:
                tpRigToolkit.logger.warning('Aborting loading Data Class {} : {}'.format(mod_name, str(e)))
                tpRigToolkit.logger.error(traceback.format_exc())

        for data_cls in data_classes:
            tpRigToolkit.logger.info('Found Data Class: {}'.format(data_cls))

        # TODO: Not working in Python 3
        # '<' not supported between instances of 'Shiboken.ObjectType' and 'Shiboken.ObjectType'
        # return sorted(list(set(data_classes)))
        return list(set(data_classes))


@decorators.Singleton
class DataManagerSingleton(DataManager, object):
    def __init__(self):
        DataManager.__init__(self)
