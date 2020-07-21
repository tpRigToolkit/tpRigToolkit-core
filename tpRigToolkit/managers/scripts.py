#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains data manager widgets
"""

from __future__ import print_function, division, absolute_import

import os
import pkgutil
import inspect
import traceback

from tpDcc.core import data as core_data, scripts
from tpDcc.libs.python import decorators

import tpRigToolkit


class ScriptsManager(object):

    def __init__(self):
        super(ScriptsManager, self).__init__()

        self.directories = list()
        self.ask_name_on_creation = True
        self.loaded_data_classes = list()

        self.standard_data_classes = [
            scripts.ScriptManifestData,
            scripts.ScriptPythonData
        ]

    def get_all_data_classes(self, _reload=False):
        """
        Returns all data widgets loaded by the manager
        :return: list<DataWidget>
        """

        return self.standard_data_classes + self.load_data_classes(_reload=_reload)

    def add_directory(self, directory, do_update=False):
        """
        Adds a new directory where data should be find
        :param directory: str
        :param do_update: bool
        """

        if directory not in self.directories:
            self.directories.append(directory)
            if do_update:
                self.load_data_classes()

    def set_directories(self, directories):
        """
        Sets the directories where data should be find
        :param directories: list(str)
        """

        new_dir = False
        for d in directories:
            if d not in self.directories:
                new_dir = True
                self.directories.append(d)

        if new_dir:
            self.load_data_classes()

    def load_data_classes(self, _reload=False):
        """
        Loads all data classes
        :param _reload: bool
        :return: list
        """

        for d in self.directories:
            loaded_classes = self._load_data_classes(directory=d, _reload=_reload)
            self.loaded_data_classes.extend(loaded_classes)

        return self.loaded_data_classes

    def get_available_types(self):
        """
        Returns a list with all available data types
        :return: list<str>
        """

        data_types = list()
        for data in self.get_all_data_classes():
            data_types.append(data.get_data_type())

        return data_types

    def get_type_instance(self, data_type):
        """
        Returns a new instance of data type
        :param data_type: str, type of data type instance we want to create
        :return: variant
        """

        for data in self.get_all_data_classes():
            if data.is_type_match(data_type):
                return data()

    def _load_data_classes(self, directory, _reload=False):

        imported = list()

        if directory is None or not os.path.exists(directory):
            tpRigToolkit.logger.warning('Data Path {} does not exists!'.format(directory))
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
                tpRigToolkit.logger.warning('Aborting loading Data Class {} : {}'.format(mod_name, str(e)))
                tpRigToolkit.logger.debug(traceback.format_exc())

        return sorted(list(set(imported)))


@decorators.Singleton
class ScriptsManagerSingleton(ScriptsManager, object):
    def __init__(self):
        ScriptsManager.__init__(self)
