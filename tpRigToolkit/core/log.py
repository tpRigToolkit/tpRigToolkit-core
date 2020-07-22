#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains helpers functions to log info during rigging process
"""

from __future__ import print_function, division, absolute_import

import string

import tpDcc as tp
from tpDcc.libs.python import log

import tpRigToolkit


def start_temp_log():
    """
    Initializes a new temp and stores its results in environment variable
    """

    log.start_temp_log(tpRigToolkit.logger.name)


def record_temp_log(value):
    """
    Adds a new value to the temp log with the given name (if exists)
    :param log_name: str, name of the log we want to add value into
    :param value: str
    """

    log.record_temp_log(tpRigToolkit.logger.name, value)


def end_temp_log():
    """
    Removes temp log with given name and returns its contents
    :param log_name: str, nam of the temp log we want to remove
    :return: str
    """

    return log.end_temp_log(tpRigToolkit.logger.name)


def show(*args):
    """
    Helper function that prints given arguments into proper Dcc logs and temp logger
    :param args: list(variant)
    """

    try:
        string_value = show_list_to_string(*args)
        log_value = string_value.replace('\n', '\nLOG:\t\t')
        text = '\t\t{}'.format(string_value)
        print(text)
        log.record_temp_log(tpRigToolkit.logger.name, '\n{}'.format(log_value))
    except RuntimeError as e:
        text = '\t\tCould not show {}'.format(args)
        print(text)
        log.record_temp_log(tpRigToolkit.logger.name, '\n{}'.format(log_value))
        raise RuntimeError(e)


def warning(*args):
    """
    Helper function that prints given arguments as warning into proper Dcc logs and temp logger
    :param args: list(variant)
    """

    try:
        string_value = show_list_to_string(*args)
        log_value = string_value.replace('\n', '\nLOG:\t\t')
        text = '[WARNING]\t{}'.format(string_value)
        if not tp.is_maya():
            print(text)
        else:
            tp.Dcc.warning('LOG: \t{}'.format(string_value))

        log.record_temp_log(tpRigToolkit.logger.name, '\n[WARNING]: {}'.format(log_value))
    except RuntimeError as e:
        raise RuntimeError(e)


def error(*args):
    """
    Helper function that prints given arguments as error into proper Dcc logs and temp logger
    :param args: list(variant)
    """

    try:
        string_value = show_list_to_string(*args)
        log_value = string_value.replace('\n', '\nLOG:\t\t')
        text = '[ERROR]\t{}'.format(string_value)
        print(text)
        log.record_temp_log(tpRigToolkit.logger.name, '\n[ERROR]: {}'.format(log_value))
    except RuntimeError as e:
        raise RuntimeError(e)


def show_list_to_string(*args):
    """
    Converts given arguments into a string
    :param args: list(variant)
    :return: str
    """

    try:
        if args is None:
            return 'None'
        if not args:
            return ''

        new_args = list()
        for arg in args:
            if args is not None:
                new_args.append(str(arg))
        args = new_args
        if not args:
            return ''

        string_value = string.join(args).replace('\n', '\t\n')
        if string_value.endswith('\t\n'):
            string_value = string_value[:-2]

        return string_value
    except RuntimeError as e:
        raise RuntimeError(e)
