#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains Joints data implementation
"""

from __future__ import print_function, division, absolute_import

import os
import json

import tpDcc as tp
from tpDcc.core import data
from tpDcc.libs.python import fileio

import tpRigToolkit
from tpRigToolkit.core import data as rig_data


class JointsFileData(data.CustomData, object):
    def __init__(self, name=None, path=None):
        super(JointsFileData, self).__init__(name=name, path=path)

    @staticmethod
    def get_data_type():
        return 'dcc.joints'

    @staticmethod
    def get_data_extension():
        return 'joints'

    @staticmethod
    def get_data_title():
        return 'Joints'

    def export_data(self, file_path=None, comment='-', create_version=True, *args, **kwargs):

        file_path = file_path or self.get_file()

        objects = kwargs.get('objects', None)
        if not objects:
            objects = tp.Dcc.selected_nodes(full_path=True)
        if not objects:
            tpRigToolkit.logger.warning(
                'Select root node of the skeleton to export or the list of skeleton nodes to export')
            return False

        file_folder = os.path.dirname(file_path)

        joints_data = dict()
        joints_data['header'] = dict()
        joints_data['data'] = list()

        # store skeleton header
        dcc_name = tp.Dcc.get_name()
        joints_data['header']['dcc'] = dcc_name
        joints_data['header']['up_axis'] = tp.Dcc.get_up_axis_name()

        # store joints data
        visited_nodes = dict()
        for i, node in enumerate(objects):
            node_data = dict()
            node_short_name = tp.Dcc.node_short_name(node, remove_namespace=True)
            node_data['name'] = node_short_name
            node_data['index'] = i
            node_data['type'] = tp.Dcc.node_type(node)
            visited_nodes[node_short_name] = i
            world_matrix = tp.Dcc.node_world_matrix(node)
            node_data['world_matrix'] = world_matrix
            parent_index = None
            parent_node = tp.Dcc.node_parent(node)
            if parent_node:
                parent_short_name = tp.Dcc.node_short_name(parent_node, remove_namespace=True)
                if parent_short_name in visited_nodes:
                    parent_index = visited_nodes[parent_short_name]
            if parent_index is None:
                parent_index = -1
            node_data['parent_index'] = parent_index

            node_data['side'] = tp.Dcc.get_side_labelling(node)
            node_data['bone_type'] = tp.Dcc.get_type_labelling(node)
            node_data['bone_other_type'] = tp.Dcc.get_other_type_labelling(node)
            node_data['draw_label'] = tp.Dcc.get_draw_label_labelling(node)
            node_data['radius'] = tp.Dcc.get_joint_radius(node)

            node_namespace = tp.Dcc.node_namespace(node) or ''
            if node_namespace.startswith('|'):
                node_namespace = node_namespace[1:]
            node_data['namespace'] = node_namespace

            joints_data['data'].append(node_data)

        if not joints_data:
            tpRigToolkit.logger.warning('No skeleton data found!')
            return False
        tpRigToolkit.logger.info('Exporting Skeleton Data: {}'.format(joints_data))

        try:
            with open(file_path, 'w') as json_file:
                json.dump(joints_data, json_file, indent=2)
        except IOError:
            tpRigToolkit.logger.error('Joints data not saved to file {}'.format(file_path))
            return False

        version = fileio.FileVersion(file_path)
        if version.has_versions():
            version.save(comment)

        tpRigToolkit.logger.info('Joints data exported successfully!')

        return True

    def import_data(self, file_path='', objects=None, namespace=None):

        file_path = file_path or self.get_file()
        if not file_path or not os.path.isfile(file_path):
            tpRigToolkit.logger.warning('Impossible to import joints data from: "{}"'.format(file_path))
            return False

        with open(file_path, 'r') as fh:
            joints_data = json.load(fh)
        if not joints_data:
            tpRigToolkit.logger.warning('No joints data found in file: "{}"'.format(file_path))
            return False

        header = joints_data.get('header', dict())
        data = joints_data.get('data', dict())

        nodes_list = list()
        created_nodes = dict()
        for node_data in data:
            node_index = node_data.get('index', 0)
            node_parent_index = node_data.get('parent_index', -1)
            node_name = node_data.get('name', 'new_node')
            node_type = node_data.get('type', 'joint')
            node_namespace = namespace if namespace else node_data.get('namespace', '')
            node_label_side = node_data.get('side', '')
            node_label_type = node_data.get('bone_type', '')
            node_label_other_type = node_data.get('bone_other_type', '')
            node_label_draw = node_data.get('draw_label', False)
            node_radius = node_data.get('radius', 1.0)
            node_world_matrix = node_data.get(
                'world_matrix', [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0])
            tp.Dcc.clear_selection()
            if node_type == 'joint':
                new_node = tp.Dcc.create_joint(name=node_name)
            else:
                new_node = tp.Dcc.create_empty_group(name=node_name)
            tp.Dcc.set_node_world_matrix(new_node, node_world_matrix)
            created_nodes[node_index] = {
                'node': new_node, 'parent_index': node_parent_index, 'namespace': node_namespace,
                'label_side': node_label_side, 'label_type': node_label_type,
                'label_other_type': node_label_other_type, 'label_draw': node_label_draw, 'radius': node_radius
            }

            if node_type == 'joint':
                tp.Dcc.zero_orient_joint(new_node)

            nodes_list.append(new_node)

        for node_index, node_data in created_nodes.items():
            parent_index = node_data['parent_index']
            if parent_index < -1:
                continue
            node_data = created_nodes.get(node_index, None)
            if not node_data:
                continue
            node_name = node_data.get('node')

            tp.Dcc.set_side_labelling(node_name, node_data.get('label_side'))
            tp.Dcc.set_type_labelling(node_name, node_data.get('label_type'))
            tp.Dcc.set_other_type_labelling(node_name, node_data.get('label_other_type'))
            tp.Dcc.set_draw_label_labelling(node_name, node_data.get('label_draw'))
            tp.Dcc.set_joint_radius(node_name, node_data.get('radius'))

            parent_node_data = created_nodes.get(parent_index, None)
            if not parent_node_data:
                continue

            parent_node_name = parent_node_data.get('node')
            tp.Dcc.set_parent(node_name, parent_node_name)

        # We assign namespaces once the hierarchy of nodes is created
        for node_index, node_data in created_nodes.items():
            node_name = node_data.get('node')
            node_namespace = node_data.get('namespace')
            if node_namespace:
                tp.Dcc.assign_node_namespace(node_name, node_namespace, force_create=True)

        tp.Dcc.select_node(nodes_list)
        tp.Dcc.fit_view()
        tp.Dcc.clear_selection()

        return nodes_list


class JointsPreviewWidget(rig_data.DataPreviewWidget, object):
    def __init__(self, item, parent=None):
        super(JointsPreviewWidget, self).__init__(item=item, parent=parent)

        self._export_btn.setText('Save')
        self._export_btn.setVisible(True)
        self._load_btn.setVisible(False)


class Joints(rig_data.DataItem, object):
    Extension = '.{}'.format(JointsFileData.get_data_extension())
    Extensions = ['.{}'.format(JointsFileData.get_data_extension())]
    MenuOrder = 5
    MenuName = JointsFileData.get_data_title()
    MenuIconName = 'joints_data.png'
    TypeIconName = 'joints_data.png'
    DataType = JointsFileData.get_data_type()
    DefaultDataFileName = 'new_joints_file'
    PreviewWidgetClass = JointsPreviewWidget

    def __init__(self, *args, **kwargs):
        super(Joints, self).__init__(*args, **kwargs)

        self.set_data_class(JointsFileData)
