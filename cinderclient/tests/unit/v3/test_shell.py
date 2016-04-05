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

import fixtures
import mock
from requests_mock.contrib import fixture as requests_mock_fixture

from cinderclient import client
from cinderclient import shell
from cinderclient.tests.unit import utils
from cinderclient.tests.unit.v3 import fakes
from cinderclient.tests.unit.fixture_data import keystone_client


@mock.patch.object(client, 'Client', fakes.FakeClient)
class ShellTest(utils.TestCase):

    FAKE_ENV = {
        'CINDER_USERNAME': 'username',
        'CINDER_PASSWORD': 'password',
        'CINDER_PROJECT_ID': 'project_id',
        'OS_VOLUME_API_VERSION': '3',
        'CINDER_URL': keystone_client.BASE_URL,
    }

    # Patch os.environ to avoid required auth info.
    def setUp(self):
        """Run before each test."""
        super(ShellTest, self).setUp()
        for var in self.FAKE_ENV:
            self.useFixture(fixtures.EnvironmentVariable(var,
                                                         self.FAKE_ENV[var]))

        self.shell = shell.OpenStackCinderShell()

        self.requests = self.useFixture(requests_mock_fixture.Fixture())
        self.requests.register_uri(
            'GET', keystone_client.BASE_URL,
            text=keystone_client.keystone_request_callback)

        self.cs = mock.Mock()

    def run_command(self, cmd):
        self.shell.main(cmd.split())

    def assert_called(self, method, url, body=None,
                      partial_body=None, **kwargs):
        return self.shell.cs.assert_called(method, url, body,
                                           partial_body, **kwargs)

    def test_list(self):
        self.run_command('list')
        # NOTE(jdg): we default to detail currently
        self.assert_called('GET', '/volumes/detail')

    def test_list_availability_zone(self):
        self.run_command('availability-zone-list')
        self.assert_called('GET', '/os-availability-zone')
