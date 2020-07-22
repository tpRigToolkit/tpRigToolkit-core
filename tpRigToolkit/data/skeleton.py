#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains Skeleton data
"""

from __future__ import print_function, division, absolute_import

import os
import json

import tpDcc as tp
from tpDcc.core import data
from tpDcc.libs.python import fileio

import tpRigToolkit
from tpRigToolkit.core import data as rig_data


class SkeletonFileData(data.CustomData, object):
    def __init__(self, name=None, path=None):
        super(SkeletonFileData, self).__init__(name=name, path=path)

    @staticmethod
    def get_data_type():
        return 'dcc.skeleton'

    @staticmethod
    def get_data_extension():
        return 'skl'

    @staticmethod
    def get_data_title():
        return 'Skeleton'

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

        root_nodes = list()
        if len(objects) == 1:
            root_nodes.append(objects[0])
        else:
            for object in objects:
                object_parent = tp.Dcc.node_parent(object, full_path=False)
                if not object_parent or not tp.Dcc.node_is_joint(object_parent):
                    root_nodes.append(object_parent)
        if not root_nodes:
            tpRigToolkit.logger.warning('No root joints found!')
            return False
        if len(root_nodes) > 1:
            tpRigToolkit.logger.warning(
                'Multiple root nodes found in skeleton. Only first one will be exported: {}'.format(root_nodes[0]))
        root_node = root_nodes[0]

        skeleton_data = list()
        child_nodes = tp.Dcc.list_children(root_node, children_type='transform')
        child_nodes.insert(0, root_node)

        visited_nodes = dict()
        for i, node in enumerate(child_nodes):
            node_data = dict()
            node_short_name = tp.Dcc.node_short_name(node)
            node_data['name'] = node_short_name
            node_data['index'] = i
            node_data['type'] = tp.Dcc.node_type(node)
            visited_nodes[node_short_name] = i
            world_matrix = tp.Dcc.node_world_matrix(node)
            node_data['world_matrix'] = world_matrix
            parent_index = None
            parent_node = tp.Dcc.node_parent(node)
            if parent_node:
                parent_short_name = tp.Dcc.node_short_name(parent_node)
                if parent_short_name in visited_nodes:
                    parent_index = visited_nodes[parent_short_name]
            if parent_index is None:
                parent_index = -1
            node_data['parent_index'] = parent_index
            skeleton_data.append(node_data)
        if not skeleton_data:
            tpRigToolkit.logger.warning('No skeleton data found!')
            return False
        tpRigToolkit.logger.info('Exporting Skeleton Data: {}'.format(skeleton_data))

        try:
            with open(file_path, 'w') as yaml_file:
                json.dump(skeleton_data, yaml_file, indent=2)
        except IOError:
            tpRigToolkit.logger.error('Skeleton data not saved to file {}'.format(file_path))
            return False

        tpRigToolkit.logger.info('Skeleton data exported successfully!')

        version = fileio.FileVersion(file_folder)
        version.save(comment)

        return True

    def import_data(self, file_path='', objects=None):

        file_path = file_path or self.get_file()
        if not file_path or not os.path.isfile(file_path):
            tpRigToolkit.logger.warning('Impossible to import skeleton data from: "{}"'.format(file_path))
            return False

        with open(file_path, 'r') as fh:
            skeleton_data = json.load(fh)
        if not skeleton_data:
            tpRigToolkit.logger.warning('No skeleton data found in file: "{}"'.format(file_path))
            return False

        created_nodes = dict()
        for node_data in skeleton_data:
            node_index = node_data.get('index', 0)
            node_parent_index = node_data.get('parent_index', -1)
            node_name = node_data.get('name', 'new_node')
            node_type = node_data.get('type', 'joint')
            node_world_matrix = node_data.get(
                'world_matrix', [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0])
            tp.Dcc.clear_selection()
            if node_type == 'joint':
                new_node = tp.Dcc.create_joint(name=node_name)
            else:
                new_node = tp.Dcc.create_empty_group(name=node_name)
            tp.Dcc.set_node_world_matrix(new_node, node_world_matrix)
            created_nodes[node_index] = {'node': new_node, 'parent_index': node_parent_index}

        for node_index, node_data in created_nodes.items():
            parent_index = node_data['parent_index']
            if parent_index <= -1:
                continue
            node_data = created_nodes.get(node_index, None)
            if not node_data:
                continue
            node_name = node_data.get('node')
            parent_node_data = created_nodes.get(parent_index, None)
            if not parent_node_data:
                continue
            parent_node_name = parent_node_data.get('node')
            tp.Dcc.set_parent(node_name, parent_node_name)


class SkeletonPreviewWidget(rig_data.DataPreviewWidget, object):
    def __init__(self, item, parent=None):
        super(SkeletonPreviewWidget, self).__init__(item=item, parent=parent)


class Skeleton(rig_data.DataItem, object):
    Extension = '.{}'.format(SkeletonFileData.get_data_extension())
    Extensions = ['.{}'.format(SkeletonFileData.get_data_extension())]
    MenuOrder = 5
    MenuName = SkeletonFileData.get_data_title()
    MenuIconName = 'skeleton.png'
    TypeIconName = 'skeleton.png'

    TypeIconName = 'skeleton.png'
    DataType = SkeletonFileData.get_data_type()
    DefaultDataFileName = 'new_skeleton_file'
    PreviewWidgetClass = SkeletonPreviewWidget

    def __init__(self, *args, **kwargs):
        super(Skeleton, self).__init__(*args, **kwargs)

        self.set_data_class(SkeletonFileData)
