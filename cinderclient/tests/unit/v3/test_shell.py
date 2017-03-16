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

import ddt
import fixtures
import mock
from requests_mock.contrib import fixture as requests_mock_fixture

from cinderclient import client
from cinderclient import exceptions
from cinderclient import shell
from cinderclient.v3 import volumes
from cinderclient.tests.unit import utils
from cinderclient.tests.unit.v3 import fakes
from cinderclient.tests.unit.fixture_data import keystone_client

from six.moves.urllib import parse


@ddt.ddt
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

    def test_list_with_group_id_before_3_10(self):
        self.assertRaises(exceptions.UnsupportedAttribute,
                          self.run_command,
                          'list --group_id fake_id')

    @ddt.data("3.10", "3.11")
    def test_list_with_group_id_after_3_10(self, version):
        command = ('--os-volume-api-version %s list --group_id fake_id' %
                   version)
        self.run_command(command)
        self.assert_called('GET', '/volumes/detail?group_id=fake_id')

    @mock.patch("cinderclient.utils.print_list")
    def test_list_duplicate_fields(self, mock_print):
        self.run_command('list --field Status,id,Size,status')
        self.assert_called('GET', '/volumes/detail')
        key_list = ['ID', 'Status', 'Size']
        mock_print.assert_called_once_with(mock.ANY, key_list,
            exclude_unavailable=True, sortby_index=0)

    def test_list_availability_zone(self):
        self.run_command('availability-zone-list')
        self.assert_called('GET', '/os-availability-zone')

    @ddt.data({'cmd': '1234 1233',
               'body': {'instance_uuid': '1233',
                        'connector': {},
                        'volume_uuid': '1234'}},
              {'cmd': '1234 1233 '
                      '--connect True '
                      '--ip 10.23.12.23 --host server01 '
                      '--platform x86_xx '
                      '--ostype 123 '
                      '--multipath true '
                      '--mountpoint /123 '
                      '--initiator aabbccdd',
               'body': {'instance_uuid': '1233',
                        'connector': {'ip': '10.23.12.23',
                                      'host': 'server01',
                                      'os_type': '123',
                                      'multipath': 'true',
                                      'mountpoint': '/123',
                                      'initiator': 'aabbccdd',
                                      'platform': 'x86_xx'},
                        'volume_uuid': '1234'}})
    @ddt.unpack
    def test_attachment_create(self, cmd, body):
        command = '--os-volume-api-version 3.27 attachment-create '
        command += cmd
        self.run_command(command)
        expected = {'attachment': body}
        self.assert_called('POST', '/attachments', body=expected)

    @ddt.data({'cmd': '',
               'expected': ''},
              {'cmd': '--volume-id 1234',
               'expected': '?volume_id=1234'},
              {'cmd': '--status error',
               'expected': '?status=error'},
              {'cmd': '--all-tenants 1',
               'expected': '?all_tenants=1'},
              {'cmd': '--all-tenants 1 --volume-id 12345',
               'expected': '?all_tenants=1&volume_id=12345'},
              {'cmd': '--all-tenants 1 --tenant 12345',
               'expected': '?all_tenants=1&project_id=12345'},
              {'cmd': '--tenant 12345',
               'expected': '?all_tenants=1&project_id=12345'}

              )
    @ddt.unpack
    def test_attachment_list(self, cmd, expected):
        command = '--os-volume-api-version 3.27 attachment-list '
        command += cmd
        self.run_command(command)
        self.assert_called('GET', '/attachments%s' % expected)

    def test_attachment_show(self):
        self.run_command('--os-volume-api-version 3.27 attachment-show 1234')
        self.assert_called('GET', '/attachments/1234')

    @ddt.data({'cmd': '1234 '
                      '--ip 10.23.12.23 --host server01 '
                      '--platform x86_xx '
                      '--ostype 123 '
                      '--multipath true '
                      '--mountpoint /123 '
                      '--initiator aabbccdd',
               'body': {'connector': {'ip': '10.23.12.23',
                                      'host': 'server01',
                                      'os_type': '123',
                                      'multipath': 'true',
                                      'mountpoint': '/123',
                                      'initiator': 'aabbccdd',
                                      'platform': 'x86_xx'}}})
    @ddt.unpack
    def test_attachment_update(self, cmd, body):
        command = '--os-volume-api-version 3.27 attachment-update '
        command += cmd
        self.run_command(command)
        self.assert_called('PUT', '/attachments/1234', body={'attachment':
                                                             body})

    def test_attachment_delete(self):
        self.run_command('--os-volume-api-version 3.27 '
                         'attachment-delete 1234')
        self.assert_called('DELETE', '/attachments/1234')

    def test_upload_to_image(self):
        expected = {'os-volume_upload_image': {'force': False,
                                               'container_format': 'bare',
                                               'disk_format': 'raw',
                                               'image_name': 'test-image'}}
        self.run_command('upload-to-image 1234 test-image')
        self.assert_called_anytime('GET', '/volumes/1234')
        self.assert_called_anytime('POST', '/volumes/1234/action',
                                   body=expected)

    def test_upload_to_image_private_not_protected(self):
        expected = {'os-volume_upload_image': {'force': False,
                                               'container_format': 'bare',
                                               'disk_format': 'raw',
                                               'image_name': 'test-image',
                                               'protected': False,
                                               'visibility': 'private'}}
        self.run_command('--os-volume-api-version 3.1 '
                         'upload-to-image 1234 test-image')
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
        self.run_command('--os-volume-api-version 3.1 '
                         'upload-to-image --visibility=public '
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

    def test_create_volume_with_group(self):
        self.run_command('--os-volume-api-version 3.13 create --group-id 5678 '
                         '--volume-type 4321 1')
        self.assert_called('GET', '/volumes/1234')
        expected = {'volume': {'imageRef': None,
                               'project_id': None,
                               'status': 'creating',
                               'size': 1,
                               'user_id': None,
                               'availability_zone': None,
                               'source_replica': None,
                               'attach_status': 'detached',
                               'source_volid': None,
                               'consistencygroup_id': None,
                               'group_id': '5678',
                               'name': None,
                               'snapshot_id': None,
                               'metadata': {},
                               'volume_type': '4321',
                               'description': None,
                               'multiattach': False}}
        self.assert_called_anytime('POST', '/volumes', expected)

    def test_group_list(self):
        self.run_command('--os-volume-api-version 3.13 group-list')
        self.assert_called_anytime('GET', '/groups/detail')

    def test_group_list__with_all_tenant(self):
        self.run_command(
            '--os-volume-api-version 3.13 group-list --all-tenants')
        self.assert_called_anytime('GET', '/groups/detail?all_tenants=1')

    def test_group_show(self):
        self.run_command('--os-volume-api-version 3.13 '
                         'group-show 1234')
        self.assert_called('GET', '/groups/1234')

    @ddt.data(True, False)
    def test_group_delete(self, delete_vol):
        cmd = '--os-volume-api-version 3.13 group-delete 1234'
        if delete_vol:
            cmd += ' --delete-volumes'
        self.run_command(cmd)
        expected = {'delete': {'delete-volumes': delete_vol}}
        self.assert_called('POST', '/groups/1234/action', expected)

    def test_group_create(self):
        expected = {'group': {'name': 'test-1',
                              'description': 'test-1-desc',
                              'user_id': None,
                              'project_id': None,
                              'status': 'creating',
                              'group_type': 'my_group_type',
                              'volume_types': ['type1', 'type2'],
                              'availability_zone': 'zone1'}}
        self.run_command('--os-volume-api-version 3.13 '
                         'group-create --name test-1 '
                         '--description test-1-desc '
                         '--availability-zone zone1 '
                         'my_group_type type1,type2')
        self.assert_called_anytime('POST', '/groups', body=expected)

    def test_group_update(self):
        self.run_command('--os-volume-api-version 3.13 group-update '
                         '--name group2 --description desc2 '
                         '--add-volumes uuid1,uuid2 '
                         '--remove-volumes uuid3,uuid4 '
                         '1234')
        expected = {'group': {'name': 'group2',
                              'description': 'desc2',
                              'add_volumes': 'uuid1,uuid2',
                              'remove_volumes': 'uuid3,uuid4'}}
        self.assert_called('PUT', '/groups/1234',
                           body=expected)

    def test_group_update_invalid_args(self):
        self.assertRaises(exceptions.ClientException,
                          self.run_command,
                          '--os-volume-api-version 3.13 group-update 1234')

    def test_group_snapshot_list(self):
        self.run_command('--os-volume-api-version 3.14 group-snapshot-list')
        self.assert_called_anytime('GET', '/group_snapshots/detail')

    def test_group_snapshot_show(self):
        self.run_command('--os-volume-api-version 3.14 '
                         'group-snapshot-show 1234')
        self.assert_called('GET', '/group_snapshots/1234')

    def test_group_snapshot_delete(self):
        cmd = '--os-volume-api-version 3.14 group-snapshot-delete 1234'
        self.run_command(cmd)
        self.assert_called('DELETE', '/group_snapshots/1234')

    def test_group_snapshot_create(self):
        expected = {'group_snapshot': {'name': 'test-1',
                                       'description': 'test-1-desc',
                                       'user_id': None,
                                       'project_id': None,
                                       'group_id': '1234',
                                       'status': 'creating'}}
        self.run_command('--os-volume-api-version 3.14 '
                         'group-snapshot-create --name test-1 '
                         '--description test-1-desc 1234')
        self.assert_called_anytime('POST', '/group_snapshots', body=expected)

    @ddt.data(
        {'grp_snap_id': '1234', 'src_grp_id': None,
         'src': '--group-snapshot 1234'},
        {'grp_snap_id': None, 'src_grp_id': '1234',
         'src': '--source-group 1234'},
    )
    @ddt.unpack
    def test_group_create_from_src(self, grp_snap_id, src_grp_id, src):
        expected = {'create-from-src': {'name': 'test-1',
                                        'description': 'test-1-desc',
                                        'user_id': None,
                                        'project_id': None,
                                        'status': 'creating',
                                        'group_snapshot_id': grp_snap_id,
                                        'source_group_id': src_grp_id}}
        cmd = ('--os-volume-api-version 3.14 '
               'group-create-from-src --name test-1 '
               '--description test-1-desc ')
        cmd += src
        self.run_command(cmd)
        self.assert_called_anytime('POST', '/groups/action', body=expected)

    def test_volume_manageable_list(self):
        self.run_command('--os-volume-api-version 3.8 '
                         'manageable-list fakehost')
        self.assert_called('GET', '/manageable_volumes/detail?host=fakehost')

    def test_volume_manageable_list_details(self):
        self.run_command('--os-volume-api-version 3.8 '
                         'manageable-list fakehost --detailed True')
        self.assert_called('GET', '/manageable_volumes/detail?host=fakehost')

    def test_volume_manageable_list_no_details(self):
        self.run_command('--os-volume-api-version 3.8 '
                         'manageable-list fakehost --detailed False')
        self.assert_called('GET', '/manageable_volumes?host=fakehost')

    def test_snapshot_manageable_list(self):
        self.run_command('--os-volume-api-version 3.8 '
                         'snapshot-manageable-list fakehost')
        self.assert_called('GET', '/manageable_snapshots/detail?host=fakehost')

    def test_snapshot_manageable_list_details(self):
        self.run_command('--os-volume-api-version 3.8 '
                         'snapshot-manageable-list fakehost --detailed True')
        self.assert_called('GET', '/manageable_snapshots/detail?host=fakehost')

    def test_snapshot_manageable_list_no_details(self):
        self.run_command('--os-volume-api-version 3.8 '
                         'snapshot-manageable-list fakehost --detailed False')
        self.assert_called('GET', '/manageable_snapshots?host=fakehost')

    def test_list_messages(self):
        self.run_command('--os-volume-api-version 3.3 message-list')
        self.assert_called('GET', '/messages')

    @ddt.data('volume', 'backup', 'snapshot', None)
    def test_reset_state_entity_not_found(self, entity_type):
        cmd = 'reset-state 999999'
        if entity_type is not None:
            cmd += ' --type %s' % entity_type
        self.assertRaises(exceptions.CommandError, self.run_command, cmd)

    @ddt.data({'entity_types': [{'name': 'volume', 'version': '3.0',
                                 'command': 'os-reset_status'},
                                {'name': 'backup', 'version': '3.0',
                                 'command': 'os-reset_status'},
                                {'name': 'snapshot', 'version': '3.0',
                                 'command': 'os-reset_status'},
                                {'name': None, 'version': '3.0',
                                 'command': 'os-reset_status'},
                                {'name': 'group', 'version': '3.20',
                                 'command': 'reset_status'},
                                {'name': 'group-snapshot', 'version': '3.19',
                                 'command': 'reset_status'}],
               'r_id': ['1234'],
               'states': ['available', 'error', None]},
              {'entity_types': [{'name': 'volume', 'version': '3.0',
                                 'command': 'os-reset_status'},
                                {'name': 'backup', 'version': '3.0',
                                 'command': 'os-reset_status'},
                                {'name': 'snapshot', 'version': '3.0',
                                 'command': 'os-reset_status'},
                                {'name': None, 'version': '3.0',
                                 'command': 'os-reset_status'},
                                {'name': 'group', 'version': '3.20',
                                 'command': 'reset_status'},
                                {'name': 'group-snapshot', 'version': '3.19',
                                 'command': 'reset_status'}],
               'r_id': ['1234', '5678'],
               'states': ['available', 'error', None]})
    @ddt.unpack
    def test_reset_state_normal(self, entity_types, r_id, states):
        for state in states:
            for t in entity_types:
                if state is None:
                    expected = {t['command']: {}}
                    cmd = ('--os-volume-api-version '
                           '%s reset-state %s') % (t['version'],
                                                   ' '.join(r_id))
                else:
                    expected = {t['command']: {'status': state}}
                    cmd = ('--os-volume-api-version '
                           '%s reset-state '
                           '--state %s %s') % (t['version'],
                                               state, ' '.join(r_id))
                if t['name'] is not None:
                    cmd += ' --type %s' % t['name']

                self.run_command(cmd)

                name = t['name'] if t['name'] else 'volume'
                for re in r_id:
                    self.assert_called_anytime('POST', '/%ss/%s/action'
                                               % (name.replace('-', '_'), re),
                                               body=expected)

    @ddt.data({'command': '--attach-status detached',
               'expected': {'attach_status': 'detached'}},
              {'command': '--state in-use --attach-status attached',
               'expected': {'status': 'in-use',
                            'attach_status': 'attached'}},
              {'command': '--reset-migration-status',
               'expected': {'migration_status': 'none'}})
    @ddt.unpack
    def test_reset_state_volume_additional_status(self, command, expected):
        self.run_command('reset-state %s 1234' % command)
        expected = {'os-reset_status': expected}
        self.assert_called('POST', '/volumes/1234/action', body=expected)

    def test_snapshot_list_with_metadata(self):
        self.run_command('--os-volume-api-version 3.22 '
                         'snapshot-list --metadata key1=val1')
        expected = ("/snapshots/detail?metadata=%s"
                    % parse.quote_plus("{'key1': 'val1'}"))
        self.assert_called('GET', expected)

    @ddt.data(('resource_type',), ('event_id',), ('resource_uuid',),
              ('level', 'message_level'), ('request_id',))
    def test_list_messages_with_filters(self, filter):
        self.run_command('--os-volume-api-version 3.5 message-list --%s=TEST'
                         % filter[0])
        self.assert_called('GET', '/messages?%s=TEST' % filter[-1])

    def test_list_messages_with_sort(self):
        self.run_command('--os-volume-api-version 3.5 '
                         'message-list --sort=id:asc')
        self.assert_called('GET', '/messages?sort=id%3Aasc')

    def test_list_messages_with_limit(self):
        self.run_command('--os-volume-api-version 3.5 message-list --limit=1')
        self.assert_called('GET', '/messages?limit=1')

    def test_list_messages_with_marker(self):
        self.run_command('--os-volume-api-version 3.5 message-list --marker=1')
        self.assert_called('GET', '/messages?marker=1')

    def test_list_with_image_metadata_before_3_4(self):
        self.assertRaises(exceptions.UnsupportedAttribute,
                          self.run_command,
                          'list --image_metadata image_name=1234')

    def test_list_filter_image_metadata(self):
        self.run_command('--os-volume-api-version 3.4 '
                         'list --image_metadata image_name=1234')
        url = ('/volumes/detail?%s' %
               parse.urlencode([('glance_metadata', {"image_name": "1234"})]))
        self.assert_called('GET', url)

    def test_show_message(self):
        self.run_command('--os-volume-api-version 3.5 message-show 1234')
        self.assert_called('GET', '/messages/1234')

    def test_delete_message(self):
        self.run_command('--os-volume-api-version 3.5 message-delete 1234')
        self.assert_called('DELETE', '/messages/1234')

    def test_delete_messages(self):
        self.run_command(
            '--os-volume-api-version 3.3 message-delete 1234 12345')
        self.assert_called_anytime('DELETE', '/messages/1234')
        self.assert_called_anytime('DELETE', '/messages/12345')

    @mock.patch('cinderclient.utils.find_volume')
    def test_delete_metadata(self, mock_find_volume):
        mock_find_volume.return_value = volumes.Volume(self,
                                                       {'id': '1234',
                                                        'metadata':
                                                            {'k1': 'v1',
                                                             'k2': 'v2',
                                                             'k3': 'v3'}},
                                                       loaded = True)
        expected = {'metadata': {'k2': 'v2'}}
        self.run_command('--os-volume-api-version 3.15 '
                         'metadata 1234 unset k1 k3')
        self.assert_called('PUT', '/volumes/1234/metadata', body=expected)

    @ddt.data(("3.0", None), ("3.6", None),
              ("3.7", True), ("3.7", False), ("3.7", ""))
    @ddt.unpack
    def test_service_list_withreplication(self, version, replication):
        command = ('--os-volume-api-version %s service-list' %
                   version)
        if replication is not None:
            command += ' --withreplication %s' % replication
        self.run_command(command)
        self.assert_called('GET', '/os-services')
