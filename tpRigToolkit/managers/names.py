#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementation for names manager
"""

from __future__ import print_function, division, absolute_import

import tpDcc
from tpDcc.libs.python import python, decorators
from tpDcc.libs.nameit.core import namelib

import tpRigToolkit
from tpRigToolkit.tools import rigbuilder


@decorators.Singleton
class RigToolkitNameLib(namelib.NameLib, object):
    def __init__(self):
        namelib.NameLib.__init__(self)
        config = tpDcc.ConfigsMgr().get_config('tpRigToolkit-naming')
        self.naming_file = config.get_path()
        self.init_naming_data()


class RigToolkitNamesManager(object):

    def get_auto_suffixes(self):
        """
        Returns dictionary containing suffixes that can be used to handle nomenclature
        :return:
        """

        naming_config = tpDcc.ConfigsMgr().get_config(
            config_name='tpRigToolkit-naming', environment='development')
        if not naming_config:
            return dict()

        auto_suffixes_dict = naming_config.get('auto_suffixes', default=dict())
        if not auto_suffixes_dict:
            return dict()

        return auto_suffixes_dict

    def parse_name(self, node_name, rule_name=None):
        """
        Parse a current solved name and return its different fields (metadata information)
        :param node_name: str
        :param rule_name: str
        :return: dict(str)
        """

        project = rigbuilder.project
        if not project:
            tpRigToolkit.logger.warning('Impossible to solve node name because project is not defined!')
            return None
        name_lib = project.naming_lib

        rule = None
        if not rule_name:
            rule = project.get_name_rule()
            if rule:
                rule_name = rule.name
        else:
            if name_lib.has_rule(rule_name):
                rule = name_lib.get_rule(rule_name)

        if not rule:
            tpRigToolkit.logger.warning(
                'Impossible to retrieve name because rule name "{}" is not defined!'.format(rule_name))
            return None

        current_rule = name_lib.active_rule()
        name_lib.set_active_rule(rule_name)
        parsed_name = name_lib.parse(node_name)
        if current_rule:
            if rule_name != current_rule.name:
                name_lib.set_active_rule(current_rule.name)
        else:
            name_lib.set_active_rule(None)

        return parsed_name

    def solve_node_name_by_type(self, node_names=None, **kwargs):
        """
        Resolves node name taking into account its type
        In this case, the type of the node will be used to retrieve an an automatic rule
        The rule name will be retrieved using auto_suffix dict from tpDcc-naming configuration file
        :param node_names: str or list, name of the node we want to take name of
        :return: str
        """

        if not tpDcc.is_maya():
            tpRigToolkit.logger.warning('Solve Node Name by type functionality is only supported in Maya!')
            return None

        import tpDcc.dccs.maya as maya
        from tpDcc.dccs.maya.core import name

        project = rigbuilder.project
        if not project:
            tpRigToolkit.logger.warning('Impossible to solve node name by type because project is not defined!')
            return None
        name_lib = project.naming_lib

        auto_suffix = self.get_auto_suffixes()
        if not auto_suffix:
            tpRigToolkit.logger.warning(
                'Impossible to launch auto suffix functionality because no auto suffixes are defined!')
            return None

        solved_names = dict()
        return_names = list()

        if not node_names:
            node_names = tpDcc.Dcc.selected_nodes()
        if not node_names:
            return
        node_names = python.force_list(node_names)

        for obj_name in node_names:
            obj_uuid = maya.cmds.ls(obj_name, uuid=True)
            if not obj_uuid:
                continue
            obj_uuid = obj_uuid[0]
            if obj_uuid in solved_names:
                tpRigToolkit.logger.warning(
                    'Node with name: "{} and UUID "{}" already renamed to "{}"! Skipping ...'.format(
                        obj_name, obj_uuid, solved_names[obj_name]))
                continue

            # TODO: This code is a duplicated version of the one in
            #  tpDcc.dccs.maya.core.name.auto_suffix_object function. Move this code to a DCC specific function
            obj_type = maya.cmds.objectType(obj_name)
            if obj_type == 'transform':
                shape_nodes = maya.cmds.listRelatives(obj_name, shapes=True, fullPath=True)
                if not shape_nodes:
                    obj_type = 'group'
                else:
                    obj_type = maya.cmds.objectType(shape_nodes[0])
            elif obj_type == 'joint':
                shape_nodes = maya.cmds.listRelatives(obj_name, shapes=True, fullPath=True)
                if shape_nodes and maya.cmds.objectType(shape_nodes[0]) == 'nurbsCurve':
                    obj_type = 'controller'
            if obj_type == 'nurbsCurve':
                connections = maya.cmds.listConnections('{}.message'.format(obj_name))
                if connections:
                    for node in connections:
                        if maya.cmds.nodeType(node) == 'controller':
                            obj_type = 'controller'
                            break
            if obj_type not in auto_suffix:
                rule_name = 'node'
                node_type = obj_type
            else:
                rule_name = auto_suffix[obj_type]
                node_type = auto_suffix[obj_type]

            if not name_lib.has_rule(rule_name):
                if not name_lib.has_rule('node'):
                    tpRigToolkit.logger.warning(
                        'Impossible to rename node "{}" by its type "{}" because rule "{}" it is not defined and '
                        'callback rule "node" either'.format(obj_name, obj_type, rule_name))
                else:
                    rule_name = 'node'

            if rule_name == 'node':
                solved_name = self.solve_name(obj_name, node_type=node_type, rule_name=rule_name, **kwargs)
            else:
                solved_name = self.solve_name(rule_name, obj_name, rule_name=rule_name, **kwargs)
            solved_names[obj_uuid] = solved_name

        if not solved_names:
            return

        for obj_id, solved_name in solved_names.items():
            obj_name = maya.cmds.ls(obj_id, long=True)[0]
            if not solved_names:
                return_names.append(obj_name)
            else:
                new_name = name.rename(obj_name, solved_name, uuid=obj_id, rename_shape=True)
                return_names.append(new_name)

        return return_names

    def solve_name(self, *args, **kwargs):
        """
        Resolves name with given rule and attributes
        :param rule_name: str
        :param args: list
        :param kwargs: dict
        """

        project = rigbuilder.project
        if not project:
            tpRigToolkit.logger.warning('Impossible to solve node name because project is not defined!')
            return None
        name_lib = project.naming_lib

        rule_name = kwargs.pop('rule_name', None)
        rule = None
        if not rule_name:
            rule = project.get_name_rule()
            if rule:
                rule_name = rule.name
        else:
            if name_lib.has_rule(rule_name):
                rule = name_lib.get_rule(rule_name)

        if not rule:
            tpRigToolkit.logger.warning(
                'Impossible to retrieve name because rule name "{}" is not defined!'.format(rule_name))
            return None

        current_rule = name_lib.active_rule()
        name_lib.set_active_rule(rule_name)
        solved_name = name_lib.solve(*args, **kwargs)
        if current_rule:
            if rule_name != current_rule.name:
                name_lib.set_active_rule(current_rule.name)
        else:
            name_lib.set_active_rule(None)

        return solved_name or kwargs.get('default', None)


@decorators.Singleton
class RigToolkitNamesManagerSingleton(RigToolkitNamesManager, object):
    def __init__(self):
        RigToolkitNamesManager.__init__(self)


tpRigToolkit.register.register_class('NamesMgr', RigToolkitNamesManagerSingleton)
