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


def register_class(cls_name, cls, is_unique=False):
    """
    This function registers given class into tpRigToolkit module
    :param cls_name: str, name of the class we want to register
    :param cls: class, class we want to register
    :param is_unique: bool, Whether if the class should be updated if new class is registered with the same name
    """

    import tpRigToolkit

    if is_unique:
        if cls_name in tpRigToolkit.__dict__:
            setattr(tpRigToolkit.__dict__, cls_name, getattr(tpRigToolkit.__dict__, cls_name))
    else:
        tpRigToolkit.__dict__[cls_name] = cls
