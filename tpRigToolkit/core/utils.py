#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains utils functions for tpRigToolkit
"""

from __future__ import print_function, division, absolute_import

import os

import tpDcc as tp
from tpDcc.libs.python import folder, fileio, version, path as path_utils

import tpRigToolkit


def get_data_files_directory():
    """
    Returns default paths where data files for tpRigToolkit are located
    :return: list(str)
    """

    data_dirs = [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')]

    # TODO: Implement a generic way to include data for specific DCCs without add them here explicitly
    if tp.is_maya():
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
            tpRigToolkit.logger.info('Nothing to copy: {}\t\tData was probably created but not saved yet.'.format(
                path_utils.get_dirname(is_source_a_file)))
            return
        if path_utils.exists(target):
            folder.delete_folder(target)
        copied_path = folder.copy_folder(source, target)

    if not copied_path:
        tpRigToolkit.logger.warning('Error copying {}\t to\t{}'.format(source, target))
        return

    if copied_path > -1:
        tpRigToolkit.logger.info('Finished copying {} from {} to {}'.format(description, source, target))
        version_file = version.VersionFile(copied_path)
        version_file.save('Copied from {}'.format(source))
