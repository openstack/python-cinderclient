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

import os

from keystoneauth1 import loading
from keystoneauth1 import plugin


class CinderNoAuthPlugin(plugin.BaseAuthPlugin):
    def __init__(self, user_id, project_id=None, roles=None, endpoint=None):
        """
        Initialize the user and roles.

        Args:
            self: (todo): write your description
            user_id: (str): write your description
            project_id: (str): write your description
            roles: (str): write your description
            endpoint: (str): write your description
        """
        self._user_id = user_id
        self._project_id = project_id if project_id else user_id
        self._endpoint = endpoint
        self._roles = roles
        self.auth_token = '%s:%s' % (self._user_id,
                                     self._project_id)

    def get_headers(self, session, **kwargs):
        """
        Returns a dictionary.

        Args:
            self: (todo): write your description
            session: (todo): write your description
        """
        return {'x-user-id': self._user_id,
                'x-project-id': self._project_id,
                'X-Auth-Token': self.auth_token}

    def get_user_id(self, session, **kwargs):
        """
        Get user id.

        Args:
            self: (todo): write your description
            session: (todo): write your description
        """
        return self._user_id

    def get_project_id(self, session, **kwargs):
        """
        Gets the project id.

        Args:
            self: (todo): write your description
            session: (todo): write your description
        """
        return self._project_id

    def get_endpoint(self, session, **kwargs):
        """
        Gets an endpoint.

        Args:
            self: (todo): write your description
            session: (todo): write your description
        """
        return '%s/%s' % (self._endpoint, self._project_id)

    def invalidate(self):
        """
        Inspectorator : meth : py : meth : ~invalidate_invalidator

        Args:
            self: (todo): write your description
        """
        pass


class CinderOpt(loading.Opt):
    @property
    def argparse_args(self):
        """
        Parse command line arguments.

        Args:
            self: (todo): write your description
        """
        return ['--%s' % o.name for o in self._all_opts]

    @property
    def argparse_default(self):
        """
        Parse argparse argparse.

        Args:
            self: (todo): write your description
        """
        # select the first ENV that is not false-y or return None
        for o in self._all_opts:
            v = os.environ.get('Cinder_%s' % o.name.replace('-', '_').upper())
            if v:
                return v
        return self.default


class CinderNoAuthLoader(loading.BaseLoader):
    plugin_class = CinderNoAuthPlugin

    def get_options(self):
        """
        Returns the options specific to the options.

        Args:
            self: (todo): write your description
        """
        options = super(CinderNoAuthLoader, self).get_options()
        options.extend([
            CinderOpt('user-id', help='User ID', required=True,
                      metavar="<cinder user id>"),
            CinderOpt('project-id', help='Project ID',
                      metavar="<cinder project id>"),
            CinderOpt('endpoint', help='Cinder endpoint',
                      dest="endpoint", required=True,
                      metavar="<cinder endpoint>"),
        ])
        return options
