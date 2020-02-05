#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains manager to handle resources for tpRigToolkit
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from Qt.QtGui import QIcon, QPixmap

from tpPyUtils import decorators
from tpQtLib.core import resource

import tpRigToolkit


class ResourceTypes(object):
    ICON = 'icon'
    PIXMAP = 'pixmap'


@decorators.Singleton
class ResourceManager(object):
    """
    Class that handles all resources stored in registered paths
    """

    def __init__(self):

        self._resources = dict()

    def register_resource(self, resources_path):
        """
        Registers given resource path
        :param str resources_path: path to register.
        :param str key: optional key for the resource path.
        :return:
        """
        if resources_path in self._resources:
            return

        self._resources[resources_path] = resource.Resource(resources_path)

    def icon(self, *args, **kwargs):
        """
        Returns icon
        :param args: list
        :param kwargs: kwargs
        :return: QIcon
        """

        if not self._resources:
            return None

        return self.get(resource_type=ResourceTypes.ICON, *args, **kwargs) or QIcon()

    def pixmap(self, *args, **kwargs):
        """
        Returns pixmap
        :param args: list
        :param kwargs: dict
        :return: QPixmap
        """

        return self.get(resource_type=ResourceTypes.PIXMAP, *args, **kwargs) or QPixmap()


tpRigToolkit.register.register_class('resource', ResourceManager)
