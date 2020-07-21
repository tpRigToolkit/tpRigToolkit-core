#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains functions to interact with tpRigToolkit
"""

from __future__ import print_function, division, absolute_import

import tpDcc as tp
from tpDcc.core import project
from tpDcc.libs.qt.widgets import project

import tpRigToolkit
from tpRigToolkit.core import consts


def get_project_by_name(projects_path, project_name, project_class):
    """
    Returns a project located in the given path and with the given name (if exists)
    :param projects_path: str
    :param project_name: str
    :param project_class: cls
    :return: Project or None
    """

    return project.get_project_by_name(projects_path, project_name, project_class=project_class)


def get_projects(projects_path, project_class):
    """
    Returns all projects located in given path
    :param projects_path: str
    :param project_class: cls
    :return: list(Project)
    """

    return project.get_projects(projects_path, project_class=project_class)


def solve_name(*args, **kwargs):
    """
    Resolves name with given rule and attributes
    :param args: list
    :param kwargs: str
    """

    kwargs['unique_name'] = kwargs.get('unique_name', True)

    solved_name = tpRigToolkit.NamesMgr().solve_name(*args, **kwargs)

    return solved_name


def parse_name(node_name, rule_name=None):
    """
    Parse a current solved name and return its different fields (metadata information)
    :param node_name: str
    :param rule_name: str
    :return: dict(str)
    """

    return tpRigToolkit.NamesMgr().parse_name(node_name=node_name, rule_name=rule_name)


def get_sides(current_project, skip_default=False, default_sides=None, default_side=None):
    """
    Returns sides being used
    This is the order that is used to check the list of available sides
        1) Check if project has already a dict option called sides. Default side will be the first side in the list.
        2) Check project nomenclature rule looking for a rule called side
        3) Default sides for tpRigToolkit will be used
    :return: List of sides and default one
    :rtype: list(str), str
    """

    if current_project:
        # Check project options
        if current_project.has_option('sides'):
            sides = current_project.get_option('sides')
            if sides:
                default_side = sides[0]
                if skip_default:
                    sides.remove(default_side)
                return sides, default_side
        # Check project nomenclature
        name_lib = current_project.naming_lib
        side_token = name_lib.get_token('side')
        if side_token:
            token_items = side_token.get_items().keys()
            token_default = side_token.default or 1
            token_default_value = token_items[token_default - 1] if token_items else ''
            if skip_default:
                if token_default_value in token_items:
                    token_items.remove(token_default_value)
            return token_items, token_default_value
    else:
        # Default fallback
        return default_sides or consts.DEFAULT_SIDES.keys(), default_side or consts.DEFAULT_SIDE


def get_side_long_name(short_side, current_project=None):
    """
    Returns full version of the given side
    :param short_side: str
    :return: str
    """

    if current_project:
        # Check project options
        if current_project.has_option('sides'):
            sides = current_project.get_option('sides')
            if sides:
                for side_name, side_short in sides.items():
                    if side_short.lower() == short_side.lower():
                        return side_name

        # Check project nomenclature
        name_lib = current_project.naming_lib
        side_token = name_lib.get_token('side')
        for side_key, side_value in side_token.get_items().items():
            if side_value.lower() == short_side.lower():
                return side_key
    else:
        # Default fallback
        for side_name, side_short in consts.DEFAULT_SIDE.items():
            if side_short.lower() == short_side.lower():
                return side_name

    return short_side


def get_mirror_side(current_project, default_mirror_side=None):
    """
    Returns current mirror side used by the project
    :return: str
    """

    if current_project:
        # Check project options
        if current_project.has_option('mirror side'):
            return current_project.get_option('mirror side')

        # Check project nomenclature
        name_lib = current_project.naming_lib
        mirror_side_token = name_lib.get_token('mirror side')
        if mirror_side_token:
            token_items = mirror_side_token.get_items().keys()
            token_default = mirror_side_token.default or 1
            token_default_value = token_items[token_default - 1] if token_items else ''
            return token_default_value
        else:
            return default_mirror_side or consts.DEFAULT_MIRROR_SIDE
    else:
        # Default fallback
        return default_mirror_side or consts.DEFAULT_MIRROR_SIDE


def get_default_side(current_project):
    """
    Returns current default side used by the project
    :return: str
    """

    sides, default_side = get_sides(current_project=current_project)

    return default_side


def get_color_of_side(current_project, side, sub_color=False):
    """
    Returns override color of the given side
     This is the order that is used to check the list of available sides
        1) Check if project has already side colors defined.
        2) Default sides for DCC will be used
    :param current_project: str
    :param side: str
    :param sub_color: fool, whether to return a sub color or not
    :return:
    """

    side_color = None
    if current_project:
        groups = ['Controls', 'controls'] if not sub_color else ['SubControls', 'subcontrols']
        for group in groups:
            if current_project.has_option(side, group=group):
                side_color = current_project.get_option(side, group=group)
            else:
                side_long = get_side_long_name(side, current_project=current_project)
                if current_project.has_option(side_long, group=group):
                    side_color = current_project.get_option(side_long, group=group)
                if current_project.has_option(side_long.title(), group=group):
                    side_color = current_project.get_option(side_long.title(), group=group)
            if side_color:
                break

    return side_color if side_color else tp.Dcc.get_color_of_side(side=side, sub_color=sub_color)


def get_side_colors(current_project, sides=None, sub_color=False):
    """
    Returns dictionary containing the side color for each of the side of the current project
    :param current_project: Project
    :param sides: list(str) or None, If not given, default sides will be used
    :param sub_color: bool, Whether to return the color for main controls or sub controls
    :return: dict(str, list)
    """

    side_colors = dict()
    sides, default_side = sides or get_sides(current_project=current_project)
    for side in sides:
        side_color_data = get_color_of_side(current_project, side=side, sub_color=sub_color)
        if side_color_data:
            side_colors[side] = side_color_data

    return side_colors


def get_mirror_name(current_project, node_name):
    """
    Returns the mirrored name of the given node
    :param current_project: str
    :param node_name: str
    :return: str
    """

    all_sides, default_side = get_sides(current_project=current_project, skip_default=True)
    parsed_name = parse_name(node_name)
    if 'side' not in parsed_name or not parsed_name['side'] or parsed_name['side'] not in all_sides:
        return tp.Dcc.get_mirror_name(node_name)
    else:
        mirror_side = parsed_name['side']
        for side in all_sides:
            if side != parsed_name['side']:
                mirror_side = side
                break
        parsed_name['side'] = mirror_side

        return solve_name(parsed_name)
