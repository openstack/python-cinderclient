# Copyright (c) 2011 OpenStack Foundation
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

from cinderclient.apiclient import base as common_base
from cinderclient import base
from cinderclient import utils


class Extension(common_base.HookableMixin):
    """Extension descriptor."""

    SUPPORTED_HOOKS = ('__pre_parse_args__', '__post_parse_args__')

    def __init__(self, name, module):
        """
        Initialize a module.

        Args:
            self: (todo): write your description
            name: (str): write your description
            module: (str): write your description
        """
        self.name = name
        self.module = module
        self._parse_extension_module()

    def _parse_extension_module(self):
        """
        Parses the extension module.

        Args:
            self: (todo): write your description
        """
        self.manager_class = None
        for attr_name, attr_value in list(self.module.__dict__.items()):
            if attr_name in self.SUPPORTED_HOOKS:
                self.add_hook(attr_name, attr_value)
            elif utils.safe_issubclass(attr_value, base.Manager):
                self.manager_class = attr_value

    def __repr__(self):
        """
        Return a human - friendly name.

        Args:
            self: (todo): write your description
        """
        return "<Extension '%s'>" % self.name
