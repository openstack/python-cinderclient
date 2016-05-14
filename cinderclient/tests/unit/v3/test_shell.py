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
from cinderclient import exceptions
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

    def test_upload_to_image(self):
        expected = {'os-volume_upload_image': {'force': False,
                                               'container_format': 'bare',
                                               'disk_format': 'raw',
                                               'image_name': 'test-image',
                                               'protected': False,
                                               'visibility': 'private'}}
        self.run_command('upload-to-image 1234 test-image')
        self.assert_called_anytime('GET', '/volumes/1234')
        self.assert_called_anytime('POST', '/volumes/1234/action',
                                   body=expected)

    def test_upload_to_image_public_protected(self):
        expected = {'os-volume_upload_image': {'force': False,
                                               'container_format': 'bare',
                                               'disk_format': 'raw',
                                               'image_name': 'test-image',
                                               'protected': 'True',
                                               'visibility': 'public'}}
        self.run_command('upload-to-image --visibility=public '
                         '--protected=True 1234 test-image')
        self.assert_called_anytime('GET', '/volumes/1234')
        self.assert_called_anytime('POST', '/volumes/1234/action',
                                   body=expected)

    def test_backup_update(self):
        self.run_command('--os-volume-api-version 3.9 '
                         'backup-update --name new_name 1234')
        expected = {'backup': {'name': 'new_name'}}
        self.assert_called('PUT', '/backups/1234', body=expected)

    def test_backup_update_with_description(self):
        self.run_command('--os-volume-api-version 3.9 '
                         'backup-update 1234 --description=new-description')
        expected = {'backup': {'description': 'new-description'}}
        self.assert_called('PUT', '/backups/1234', body=expected)

    def test_backup_update_all(self):
        # rename and change description
        self.run_command('--os-volume-api-version 3.9 '
                         'backup-update --name new-name '
                         '--description=new-description 1234')
        expected = {'backup': {
            'name': 'new-name',
            'description': 'new-description',
        }}
        self.assert_called('PUT', '/backups/1234', body=expected)

    def test_backup_update_without_arguments(self):
        # Call rename with no arguments
        self.assertRaises(SystemExit, self.run_command,
                          '--os-volume-api-version 3.9 backup-update')

    def test_backup_update_bad_request(self):
        self.assertRaises(exceptions.ClientException,
                          self.run_command,
                          '--os-volume-api-version 3.9 backup-update 1234')

    def test_backup_update_wrong_version(self):
        self.assertRaises(SystemExit,
                          self.run_command,
                          '--os-volume-api-version 3.8 '
                          'backup-update --name new-name 1234')

    def test_group_type_list(self):
        self.run_command('--os-volume-api-version 3.11 group-type-list')
        self.assert_called_anytime('GET', '/group_types?is_public=None')

    def test_group_type_show(self):
        self.run_command('--os-volume-api-version 3.11 '
                         'group-type-show 1')
        self.assert_called('GET', '/group_types/1')

    def test_group_type_create(self):
        self.run_command('--os-volume-api-version 3.11 '
                         'group-type-create test-type-1')
        self.assert_called('POST', '/group_types')

    def test_group_type_create_public(self):
        expected = {'group_type': {'name': 'test-type-1',
                                   'description': 'test_type-1-desc',
                                   'is_public': True}}
        self.run_command('--os-volume-api-version 3.11 '
                         'group-type-create test-type-1 '
                         '--description=test_type-1-desc '
                         '--is-public=True')
        self.assert_called('POST', '/group_types', body=expected)

    def test_group_type_create_private(self):
        expected = {'group_type': {'name': 'test-type-3',
                                   'description': 'test_type-3-desc',
                                   'is_public': False}}
        self.run_command('--os-volume-api-version 3.11 '
                         'group-type-create test-type-3 '
                         '--description=test_type-3-desc '
                         '--is-public=False')
        self.assert_called('POST', '/group_types', body=expected)

    def test_group_specs_list(self):
        self.run_command('--os-volume-api-version 3.11 group-specs-list')
        self.assert_called('GET', '/group_types?is_public=None')
