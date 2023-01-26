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

import collections
import os
from urllib import parse
import uuid

import stevedore

from cinderclient import exceptions


def arg(*args, **kwargs):
    """Decorator for CLI args."""
    def _decorator(func):
        add_arg(func, *args, **kwargs)
        return func
    return _decorator


def exclusive_arg(group_name, *args, **kwargs):
    """Decorator for CLI mutually exclusive args."""
    def _decorator(func):
        required = kwargs.pop('required', None)
        add_exclusive_arg(func, group_name, required, *args, **kwargs)
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


def add_exclusive_arg(f, group_name, required, *args, **kwargs):
    """Bind CLI mutally exclusive arguments to a shell.py `do_foo` function."""

    if not hasattr(f, 'exclusive_args'):
        f.exclusive_args = collections.defaultdict(list)
        # Default required to False
        f.exclusive_args['__required__'] = collections.defaultdict(bool)

    # NOTE(sirp): avoid dups that can occur when the module is shared across
    # tests.
    if (args, kwargs) not in f.exclusive_args[group_name]:
        # Because of the semantics of decorator composition if we just append
        # to the options list positional options will appear to be backwards.
        f.exclusive_args[group_name].insert(0, (args, kwargs))
        if required is not None:
            f.exclusive_args['__required__'][group_name] = required


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


def build_query_param(params, sort=False):
    """parse list to url query parameters"""

    if not params:
        return ""

    if not sort:
        param_list = list(params.items())
    else:
        param_list = list(sorted(params.items()))

    query_string = parse.urlencode(
        [(k, v) for (k, v) in param_list if v not in (None, '')])

    # urllib's parse library used to adhere to RFC 2396 until
    # python 3.7. The library moved from RFC 2396 to RFC 3986
    # for quoting URL strings in python 3.7 and '~' is now
    # included in the set of reserved characters. [1]
    #
    # Below ensures "~" is never encoded. See LP 1784728 [2] for more details.
    # [1] https://docs.python.org/3/library/urllib.parse.html#url-quoting
    # [2] https://bugs.launchpad.net/python-cinderclient/+bug/1784728
    query_string = query_string.replace("%7E=", "~=")

    if query_string:
        query_string = "?%s" % (query_string,)

    return query_string


def find_resource(manager, name_or_id, **kwargs):
    """Helper for the _find_* methods."""
    is_group = kwargs.pop('is_group', False)
    # first try to get entity as integer id
    try:
        if isinstance(name_or_id, int) or name_or_id.isdigit():
            if is_group:
                return manager.get(int(name_or_id), **kwargs)
            return manager.get(int(name_or_id))
    except exceptions.NotFound:
        pass
    else:
        # now try to get entity as uuid
        try:
            uuid.UUID(name_or_id)
            if is_group:
                return manager.get(name_or_id, **kwargs)
            return manager.get(name_or_id)
        except (ValueError, exceptions.NotFound):
            pass

    try:
        try:
            resource = getattr(manager, 'resource_class', None)
            name_attr = resource.NAME_ATTR if resource else 'name'
            if is_group:
                kwargs[name_attr] = name_or_id
                return manager.find(**kwargs)
            return manager.find(**{name_attr: name_or_id})
        except exceptions.NotFound:
            pass

        # finally try to find entity by human_id
        try:
            if is_group:
                kwargs['human_id'] = name_or_id
                return manager.find(**kwargs)
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
    mgr = stevedore.NamedExtensionManager(
        namespace=ep_name,
        names=[name],
        # Ignore errors on load
        on_load_failure_callback=lambda mgr, entry_point, error: None,
    )
    try:
        return mgr[name].plugin
    except KeyError:
        pass


def get_function_name(func):
    return "%s.%s" % (func.__module__, func.__qualname__)
