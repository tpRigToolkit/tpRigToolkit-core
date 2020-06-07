#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains default implementation for tpRigToolkit configurations
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import logging

import metayaml

import tpDcc as tp

LOGGER = logging.getLogger()


class YAMLConfigurationAttribute(dict, object):
    """
    Class that allows access nested dictionaries using Python attribute access
    https://stackoverflow.com/questions/38034377/object-like-attribute-access-for-nested-dictionary
    """

    def __init__(self, *args, **kwargs):
        super(YAMLConfigurationAttribute, self).__init__(*args, **kwargs)
        self.__dict__ = self

    @staticmethod
    def from_nested_dict(data):
        """
        Construst a nested YAMLConfigurationAttribute from nested dictionaries
        :param data: dict
        :return: YAMLConfigurationAttribute
        """

        if not isinstance(data, dict):
            return data
        else:
            return YAMLConfigurationAttribute(
                {key: YAMLConfigurationAttribute.from_nested_dict(data[key]) for key in data})


class YAMLConfigurationParser(object):
    def __init__(self, config_data):
        super(YAMLConfigurationParser, self).__init__()

        self._config_data = config_data
        self._parsed_data = dict()

    def parse(self):
        self._parsed_data = self._config_data
        return YAMLConfigurationAttribute.from_nested_dict(self._parsed_data)


class YAMLConfiguration(object):
    def __init__(self, config_name, environment, config_dict=None,
                 parser_class=YAMLConfigurationParser):
        super(YAMLConfiguration, self).__init__()

        self._config_name = config_dict
        self._environment = environment
        self._parser_class = parser_class
        self._parsed_data = self.load(config_name=config_name, config_dict=config_dict)

    @property
    def data(self):
        return self._parsed_data

    def get_path(self):
        if not self._parsed_data:
            return None

        return self._parsed_data.get('config', {}).get('path', None)

    def get(self, attr_section, attr_name=None, default=None):
        """
        Returns an attribute of the configuration
        :param attr_name: str
        :param attr_section: str
        :param default: object
        :return:
        """

        if not self._parsed_data:
            LOGGER.warning('Configuration "{}" is empty for "{}"'.format(
                self._config_name, self._environment))
            return default

        if attr_section and attr_name:
            orig_section = attr_section
            attr_section = self._parsed_data.get(attr_section, dict())
            if not attr_section:
                LOGGER.warning('Configuration "{}" has no attribute "{}" in section "{}" for "{}"'.format(
                    self._config_name, attr_name, orig_section, self._environment))
                return default
            attr_value = attr_section.get(attr_name, None)
            if attr_value is None:
                LOGGER.warning('Configuration "{}" has no attribute "{}" in section "{}" for "{}"'.format(
                    self._config_name, attr_name, attr_section, self._environment))
                return default
            return attr_value
        else:
            attr_to_use = attr_section
            if attr_name and not default:
                default = attr_name
            if not attr_section:
                attr_to_use = attr_name
            attr_value = self._parsed_data.get(attr_to_use, None)
            if attr_value is None:
                LOGGER.warning('Configuration "{}" has no attribute "{}" for "{}"'.format(
                    self._config_name, attr_to_use, self._environment))
                return default
            return attr_value

    def load(self, config_name, config_dict=None):
        """
        Function that reads configuration file and initializes project variables properly
        This function can be extended in new projects
        """

        if not config_dict:
            config_dict = {}

        config_data = self._get_config_data(config_name, config_dict=config_dict)
        if not config_data:
            return False

        parsed_data = self._parser_class(config_data).parse()

        return parsed_data

    def _get_tprigtoolkit_config_paths(self, module_config_name):
        """
        Returns a list of paths where configuration file can be located in tpRigToolkit-config
        :return: list(str)
        """

        configs_path = os.environ.get('TPRIGTOOLKIT_CONFIGS_PATH', None)
        if not configs_path or not os.path.isdir(configs_path):
            from tpRigToolkit import config
            config_dir = os.path.dirname(config.__file__)
        else:
            config_dir = configs_path

        config_env_dir = os.path.join(config_dir, self._environment.lower())
        if not os.path.isdir(config_env_dir):
            LOGGER.warning('Configuration Folder for Environment "{}" does not exists: "{}"'.format(
                self._environment, config_env_dir))

        config_path = os.path.join(config_env_dir, module_config_name)
        dcc_config_path = os.path.join(config_env_dir, tp.Dcc.get_name(), module_config_name)
        dcc_version_config_path = os.path.join(
            config_env_dir, tp.Dcc.get_name(), tp.Dcc.get_version_name(), module_config_name)

        return [config_path, dcc_config_path, dcc_version_config_path]

    def _get_config_paths(self, module_config_name, skip_non_existent=True):
        """
        Returns a list of valid paths where configuration files can be located
        :return: list(str)
        """

        found_paths = list()
        paths_to_found = self._get_tprigtoolkit_config_paths(module_config_name=module_config_name)

        for p in paths_to_found:
            if not p:
                continue
            if skip_non_existent and not os.path.isfile(p):
                continue
            found_paths.append(p)

        return found_paths

    def _get_config_data(self, config_name, config_dict):
        """
        Returns the config data
        :return: dict
        """

        if not config_name:
            tp.Dcc.error(
                'Configuration File for tpRigToolkit not found! {}'.format(self, config_name))
            return

        module_config_name = config_name + '.yml'

        # We use tpRigToolkit configuration as base configuration file
        all_config_paths = self._get_config_paths(module_config_name=module_config_name, skip_non_existent=False)
        valid_config_paths = self._get_config_paths(module_config_name=module_config_name)
        if not valid_config_paths:
            raise RuntimeError(
                'Impossible to load configuration "{}"  for tpRigToolkit because it does not exists in any of '
                'the configuration folders: {}'.format(config_name, ''.join(all_config_paths)))

        config_path = valid_config_paths[-1]
        config_data = metayaml.read(valid_config_paths, config_dict)
        if not config_data:
            raise RuntimeError(
                'Configuration File is empty! {}'.format(self, config_path))

        # We store path where configuration file is located in disk
        if 'config' in config_data and 'path' in config_data['config']:
            raise RuntimeError(
                'Configuration File for cannot contains config section with path attribute! {}'.format(
                    self, config_path))
        if 'config' in config_data:
            config_data['config']['path'] = config_path
        else:
            config_data['config'] = {'path': config_path}

        return config_data


def get_config(config_name, config_dict=None, parser_class=YAMLConfigurationParser):
    """
    Returns a configuration with the given arguments
    :param config_name: str
    :param config_dict: dict
    :param parser_class: YAMLConfigurationParser
    :param environment: str (optional)
    :return: YAMLConfiguration
    """

    new_cfg = YAMLConfiguration(
        config_name=config_name,
        config_dict=config_dict,
        parser_class=parser_class,
        environment=os.environ.get('tpRigToolkit_env', 'DEVELOPMENT')
    )

    return new_cfg
