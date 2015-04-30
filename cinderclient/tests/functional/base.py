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

from tempest_lib.cli import base
from tempest_lib.cli import output_parser


class ClientTestBase(base.ClientTestBase):
    """Cinder base class, issues calls to cinderclient.

    """
    def setUp(self):
        super(ClientTestBase, self).setUp()
        self.clients = self._get_clients()
        self.parser = output_parser

    def _get_clients(self):
        cli_dir = os.environ.get(
            'OS_CINDERCLIENT_EXEC_DIR',
            os.path.join(os.path.abspath('.'), '.tox/functional/bin'))

        return base.CLIClient(
            username=os.environ.get('OS_USERNAME'),
            password=os.environ.get('OS_PASSWORD'),
            tenant_name=os.environ.get('OS_TENANT_NAME'),
            uri=os.environ.get('OS_AUTH_URL'),
            cli_dir=cli_dir)

    def cinder(self, *args, **kwargs):
        return self.clients.cinder(*args,
                                   **kwargs)

    def assertTableStruct(self, items, field_names):
        """Verify that all items has keys listed in field_names.

        :param items: items to assert are field names in the output table
        :type items: list
        :param field_names: field names from the output table of the cmd
        :type field_names: list
        """
        # Strip off the --- if present

        for item in items:
            for field in field_names:
                self.assertIn(field, item)
