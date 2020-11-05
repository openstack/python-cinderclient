# Copyright (c) 2015 Hitachi Data Systems, Inc.
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

"""Capabilities interface (v2 extension)"""

from cinderclient import base


class Capabilities(base.Resource):
    NAME_ATTR = 'name'

    def __repr__(self):
        """
        Return a repr representation of - repr repr.

        Args:
            self: (todo): write your description
        """
        return "<Capabilities: %s>" % self._info.get('namespace')


class CapabilitiesManager(base.Manager):
    """Manage :class:`Capabilities` resources."""
    resource_class = Capabilities

    def get(self, host):
        """Show backend volume stats and properties.

        :param host: Specified backend to obtain volume stats and properties.
        :rtype: :class:`Capabilities`
        """
        return self._get('/capabilities/%s' % host, None)
