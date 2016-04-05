# Copyright (c) 2013 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import print_function

import os
import pkg_resources
import sys
import types
import uuid

import six
import prettytable

from cinderclient import exceptions
from oslo_utils import encodeutils


def arg(*args, **kwargs):
    """Decorator for CLI args."""
    def _decorator(func):
        add_arg(func, *args, **kwargs)
        return func
    return _decorator


def env(*vars, **kwargs):
    """
    returns the first environment variable set
    if none are non-empty, defaults to '' or keyword arg default
    """
    for v in vars:
        value = os.environ.get(v, None)
        if value:
            return value
    return kwargs.get('default', '')


def add_arg(f, *args, **kwargs):
    """Bind CLI arguments to a shell.py `do_foo` function."""

    if not hasattr(f, 'arguments'):
        f.arguments = []

    # NOTE(sirp): avoid dups that can occur when the module is shared across
    # tests.
    if (args, kwargs) not in f.arguments:
        # Because of the semantics of decorator composition if we just append
        # to the options list positional options will appear to be backwards.
        f.arguments.insert(0, (args, kwargs))


def unauthenticated(f):
    """
    Adds 'unauthenticated' attribute to decorated function.
    Usage:
        @unauthenticated
        def mymethod(f):
            ...
    """
    f.unauthenticated = True
    return f


def isunauthenticated(f):
    """
    Checks to see if the function is marked as not requiring authentication
    with the @unauthenticated decorator. Returns True if decorator is
    set to True, False otherwise.
    """
    return getattr(f, 'unauthenticated', False)


def service_type(stype):
    """
    Adds 'service_type' attribute to decorated function.
    Usage:
        @service_type('volume')
        def mymethod(f):
            ...
    """
    def inner(f):
        f.service_type = stype
        return f
    return inner


def get_service_type(f):
    """
    Retrieves service type from function
    """
    return getattr(f, 'service_type', None)


def _print(pt, order):
    if sys.version_info >= (3, 0):
        print(pt.get_string(sortby=order))
    else:
        print(encodeutils.safe_encode(pt.get_string(sortby=order)))


def print_list(objs, fields, exclude_unavailable=False, formatters=None,
               sortby_index=0):
    '''Prints a list of objects.

    @param objs: Objects to print
    @param fields: Fields on each object to be printed
    @param exclude_unavailable: Boolean to decide if unavailable fields are
                                removed
    @param formatters: Custom field formatters
    @param sortby_index: Results sorted against the key in the fields list at
                         this index; if None then the object order is not
                         altered
    '''
    formatters = formatters or {}
    mixed_case_fields = ['serverId']
    removed_fields = []
    rows = []

    for o in objs:
        row = []
        for field in fields:
            if field in removed_fields:
                continue
            if field in formatters:
                row.append(formatters[field](o))
            else:
                if field in mixed_case_fields:
                    field_name = field.replace(' ', '_')
                else:
                    field_name = field.lower().replace(' ', '_')
                if isinstance(o, dict) and field in o:
                    data = o[field]
                else:
                    if not hasattr(o, field_name) and exclude_unavailable:
                        removed_fields.append(field)
                        continue
                    else:
                        data = getattr(o, field_name, '')
                if data is None:
                    data = '-'
                if isinstance(data, six.string_types) and "\r" in data:
                    data = data.replace("\r", " ")
                row.append(data)
        rows.append(row)

    for f in removed_fields:
        fields.remove(f)

    pt = prettytable.PrettyTable((f for f in fields), caching=False)
    pt.aligns = ['l' for f in fields]
    for row in rows:
        count = 0
        # Converts unicode values in dictionary to string
        for part in row:
            count = count + 1
            if isinstance(part, dict):
                part = unicode_key_value_to_string(part)
                row[count - 1] = part
        pt.add_row(row)

    if sortby_index is None:
        order_by = None
    else:
        order_by = fields[sortby_index]
    _print(pt, order_by)


def unicode_key_value_to_string(dictionary):
    """Recursively converts dictionary keys to strings."""
    if not isinstance(dictionary, dict):
        return dictionary
    return dict((str(k), str(unicode_key_value_to_string(v)))
        for k, v in dictionary.items())


def print_dict(d, property="Property", formatters=None):
    pt = prettytable.PrettyTable([property, 'Value'], caching=False)
    pt.aligns = ['l', 'l']
    formatters = formatters or {}

    for r in six.iteritems(d):
        r = list(r)

        if r[0] in formatters:
            r[1] = unicode_key_value_to_string(r[1])

        if isinstance(r[1], six.string_types) and "\r" in r[1]:
            r[1] = r[1].replace("\r", " ")
        pt.add_row(r)
    _print(pt, property)


def find_resource(manager, name_or_id):
    """Helper for the _find_* methods."""
    # first try to get entity as integer id
    try:
        if isinstance(name_or_id, int) or name_or_id.isdigit():
            return manager.get(int(name_or_id))
    except exceptions.NotFound:
        pass
    else:
        # now try to get entity as uuid
        try:
            uuid.UUID(name_or_id)
            return manager.get(name_or_id)
        except (ValueError, exceptions.NotFound):
            pass

    if sys.version_info <= (3, 0):
        name_or_id = encodeutils.safe_decode(name_or_id)

    try:
        try:
            resource = getattr(manager, 'resource_class', None)
            name_attr = resource.NAME_ATTR if resource else 'name'
            return manager.find(**{name_attr: name_or_id})
        except exceptions.NotFound:
            pass

        # finally try to find entity by human_id
        try:
            return manager.find(human_id=name_or_id)
        except exceptions.NotFound:
            msg = "No %s with a name or ID of '%s' exists." % \
                (manager.resource_class.__name__.lower(), name_or_id)
            raise exceptions.CommandError(msg)

    except exceptions.NoUniqueMatch:
        msg = ("Multiple %s matches found for '%s', use an ID to be more"
               " specific." % (manager.resource_class.__name__.lower(),
                               name_or_id))
        raise exceptions.CommandError(msg)


def find_volume(cs, volume):
    """Get a volume by name or ID."""
    return find_resource(cs.volumes, volume)


def safe_issubclass(*args):
    """Like issubclass, but will just return False if not a class."""

    try:
        if issubclass(*args):
            return True
    except TypeError:
        pass

    return False


def _load_entry_point(ep_name, name=None):
    """Try to load the entry point ep_name that matches name."""
    for ep in pkg_resources.iter_entry_points(ep_name, name=name):
        try:
            return ep.load()
        except (ImportError, pkg_resources.UnknownExtra, AttributeError):
            continue


def retype_method(old_type, new_type, namespace):
    for attr in namespace.values():
        if (isinstance(attr, types.FunctionType) and
                getattr(attr, 'service_type', None) == old_type):
            setattr(attr, 'service_type', new_type)


def get_function_name(func):
    if six.PY2:
        if hasattr(func, "im_class"):
            return "%s.%s" % (func.im_class, func.__name__)
        else:
            return "%s.%s" % (func.__module__, func.__name__)
    else:
        return "%s.%s" % (func.__module__, func.__qualname__)
