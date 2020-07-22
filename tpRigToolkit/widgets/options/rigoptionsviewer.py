#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget to show custom rig options
"""

from __future__ import print_function, division, absolute_import

from tpDcc.libs.qt.widgets.options import viewer

from tpRigToolkit.widgets.options import rigoptionlist


class RigOptionsViewer(viewer.OptionsViewer, object):

    OPTION_LIST_CLASS = rigoptionlist.RigOptionList

    def __init__(self, option_object=None, settings=None, parent=None):
        super(RigOptionsViewer, self).__init__(option_object=option_object, settings=settings, parent=parent)
