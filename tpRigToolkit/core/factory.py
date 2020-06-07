#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains base class to create tpNodeGraph factories
"""

from __future__ import print_function, division, absolute_import


class Factory(object):
    """
    Base class that defines factory classes
    """

    def __init__(self):
        super(Factory, self).__init__()

    def create(self, raw_inst, *args, **kwargs):
        pass


class NodeFactory(Factory, object):
    """
    Base class that defines node factory class
    """

    def __init__(self):
        super(NodeFactory, self).__init__()


class PinFactory(Factory, object):
    """
    Base class that defines node factory class
    """

    def __init__(self):
        super(PinFactory, self).__init__()

    def create(self, raw_inst, owning_node):
        pass


class InputWidgetsFactory(object):
    """
    Base class that defines input widgets factory class
    """

    def __init__(self):
        super(InputWidgetsFactory, self).__init__()

    def create(self, data_type, data_setter, default_value=None, widget_variant=None, **kwargs):
        pass
