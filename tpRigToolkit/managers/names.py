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


@decorators.Singleton
class RigToolkitNameLib(namelib.NameLib, object):
    def __init__(self, naming_file=None, dev=False):
        namelib.NameLib.__init__(self)
        environment = 'development' if dev else 'production'
        config = tpDcc.ConfigsMgr().get_config('tpRigToolkit-names', environment=environment)
        self.naming_file = naming_file or config.get_path()
        self.init_naming_data()


class RigToolkitNamesManager(object):

    def get_auto_suffixes(self, dev=True):
        """
        Returns dictionary containing suffixes that can be used to handle nomenclature
        :return:
        """

        environment = 'development' if dev else 'production'
        naming_config = tpDcc.ConfigsMgr().get_config(
            config_name='tpRigToolkit-naming', environment=environment)
        if not naming_config:
            return dict()

        auto_suffixes_dict = naming_config.get('auto_suffixes', default=dict())
        if not auto_suffixes_dict:
            return dict()

        return auto_suffixes_dict

    def parse_name(self, node_name, rule_name=None, naming_file=None, dev=False):
        """
        Parse a current solved name and return its different fields (metadata information)
        :param node_name: str
        :param rule_name: str
        :param project: str
        :param dev: bool
        :return: dict(str)
        """

        name_lib = RigToolkitNameLib(naming_file=naming_file, dev=dev)
        rule_name = rule_name or 'default'
        rule = None
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

    def solve_node_name_by_type(self, node_names=None, naming_file=None, dev=False, **kwargs):
        """
        Resolves node name taking into account its type
        In this case, the type of the node will be used to retrieve an an automatic rule
        The rule name will be retrieved using auto_suffix dict from tpDcc-naming configuration file
        :param node_names: str or list, name of the node we want to take name of
        :param naming_file: str
        :param dev: bool
        :return: str
        """

        if not tpDcc.is_maya():
            tpRigToolkit.logger.warning('Solve Node Name by type functionality is only supported in Maya!')
            return None

        import tpDcc.dccs.maya as maya
        from tpDcc.dccs.maya.core import name

        name_lib = RigToolkitNameLib(naming_file=naming_file, dev=dev)

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

        unique_name = kwargs.get('unique_name', False)

        for obj_id, solved_name in solved_names.items():
            obj_name = maya.cmds.ls(obj_id, long=True)[0]
            if not solved_names:
                return_names.append(obj_name)
            else:
                if unique_name:
                    solved_name = tpDcc.Dcc.find_unique_name(solved_name)
                new_name = name.rename(obj_name, solved_name, uuid=obj_id, rename_shape=True)
                return_names.append(new_name)

        return return_names

    def solve_name(self, *args, **kwargs):
        """
        Resolves name with given rule and attributes
        :param args: list
        :param kwargs: dict
        """

        naming_file = kwargs.get('naming_file', None)
        dev = kwargs.get('dev', False)
        use_auto_suffix = kwargs.pop('use_auto_suffix', True)
        node_type = kwargs.get('node_type', None)
        rule_name = kwargs.pop('rule_name', 'default')

        if use_auto_suffix and node_type:
            auto_suffixes = tpRigToolkit.NamesMgr().get_auto_suffixes() or dict()
            if node_type in auto_suffixes:
                kwargs['node_type'] = auto_suffixes[node_type]

        name_lib = RigToolkitNameLib(naming_file=naming_file, dev=dev)

        fallback_default = False
        if name_lib.has_rule(rule_name):
            rule = name_lib.get_rule(rule_name)
        else:
            tpRigToolkit.logger.warning('Rule with name "{}" is not defined. Default rule used'.format(rule_name))
            rule = name_lib.get_rule('default')
            fallback_default = True

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

        solved_name = solved_name or kwargs.get('default', None)

        unique_name = kwargs.get('unique_name', False)
        if solved_name and unique_name:
            solved_name = tpDcc.Dcc.find_unique_name(solved_name)

        if fallback_default:
            tpRigToolkit.logger.warning('Solved name with no rule (used default one): {}'.format(solved_name))

        return solved_name


@decorators.Singleton
class RigToolkitNamesManagerSingleton(RigToolkitNamesManager, object):
    def __init__(self):
        RigToolkitNamesManager.__init__(self)
