#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget to handle editable options for rigs
"""

from __future__ import print_function, division, absolute_import

from tpDcc.libs.qt.widgets.options import option


class RigOption(option.Option, object):
    def __init__(self, name, parent, main_widget, rig_object):
        self._rig = rig_object
        super(RigOption, self).__init__(name=name, parent=parent, main_widget=main_widget)
