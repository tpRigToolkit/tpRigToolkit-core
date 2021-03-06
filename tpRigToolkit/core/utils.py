#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains utils functions for tpRigToolkit
"""

from __future__ import print_function, division, absolute_import

import os
import logging

from tpDcc import dcc
from tpDcc.libs.python import folder, fileio, version, path as path_utils

LOGGER = logging.getLogger('tpRigToolkit-core')


def get_data_files_directory():
    """
    Returns default paths where data files for tpRigToolkit are located
    :return: list(str)
    """

    data_dirs = [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')]

    # TODO: Implement a generic way to include data for specific DCCs without add them here explicitly
    if dcc.is_maya():
        from tpRigToolkit.dccs.maya import data
        data_dirs.append(os.path.join(os.path.dirname(data.__path__[0]), 'data'))

    return data_dirs


def copy(source, target, description=''):
    """
    Copies given file or files and creates a new version of the file with the given description
    :param source: str, source file or folder we want to copy
    :param target: str, destination file or folder we want to copy into
    :param description: str, description of the new version
    """

    is_source_a_file = path_utils.is_file(source)

    if is_source_a_file:
        copied_path = fileio.copy_file(source, target)
    else:
        if not path_utils.exists(source):
            LOGGER.info('Nothing to copy: {}\t\tData was probably created but not saved yet.'.format(
                path_utils.get_dirname(is_source_a_file)))
            return
        if path_utils.exists(target):
            folder.delete_folder(target)
        copied_path = folder.copy_folder(source, target)

    if not copied_path:
        LOGGER.warning('Error copying {}\t to\t{}'.format(source, target))
        return

    if copied_path > -1:
        LOGGER.info('Finished copying {} from {} to {}'.format(description, source, target))
        version_file = version.VersionFile(copied_path)
        version_file.save('Copied from {}'.format(source))


def get_custom(name, default=''):
    """
    Returns custom attributte defined in tpRigToolkit __custom__ module
    This module can be override by users if necessary
    :param name: str
    :param default: str
    :return: object
    """

    try:
        from tpRigToolkit import __custom__
    except Exception:
        return default

    value = None
    exec('value = __custom__.{}'.format(name))
    if not value:
        return default

    return value
