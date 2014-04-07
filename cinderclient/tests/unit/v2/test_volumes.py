# Copyright (c) 2013 OpenStack Foundation
#
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

from cinderclient.tests.unit import utils
from cinderclient.tests.unit.v2 import fakes
from cinderclient.v2.volumes import Volume

cs = fakes.FakeClient()


class VolumesTest(utils.TestCase):

    def test_list_volumes_with_marker_limit(self):
        cs.volumes.list(marker=1234, limit=2)
        cs.assert_called('GET', '/volumes/detail?limit=2&marker=1234')

    def test_list_volumes_with_sort_key_dir(self):
        cs.volumes.list(sort_key='id', sort_dir='asc')
        cs.assert_called('GET', '/volumes/detail?sort_dir=asc&sort_key=id')

    def test_list_volumes_with_invalid_sort_key(self):
        self.assertRaises(ValueError,
                          cs.volumes.list, sort_key='invalid', sort_dir='asc')

    def test_list_volumes_with_invalid_sort_dir(self):
        self.assertRaises(ValueError,
                          cs.volumes.list, sort_key='id', sort_dir='invalid')

    def test__list(self):
        # There only 2 volumes available for our tests, so we set limit to 2.
        limit = 2
        url = "/volumes?limit=%s" % limit
        response_key = "volumes"
        fake_volume1234 = Volume(self, {'id': 1234,
                                        'name': 'sample-volume'},
                                 loaded=True)
        fake_volume5678 = Volume(self, {'id': 5678,
                                        'name': 'sample-volume2'},
                                 loaded=True)
        fake_volumes = [fake_volume1234, fake_volume5678]
        # osapi_max_limit is 1000 by default. If limit is less than
        # osapi_max_limit, we can get 2 volumes back.
        volumes = cs.volumes._list(url, response_key, limit=limit)
        cs.assert_called('GET', url)
        self.assertEqual(fake_volumes, volumes)

        # When we change the osapi_max_limit to 1, the next link should be
        # generated. If limit equals 2 and id passed as an argument, we can
        # still get 2 volumes back, because the method _list will fetch the
        # volume from the next link.
        cs.client.osapi_max_limit = 1
        volumes = cs.volumes._list(url, response_key, limit=limit)
        self.assertEqual(fake_volumes, volumes)
        cs.client.osapi_max_limit = 1000

    def test_delete_volume(self):
        v = cs.volumes.list()[0]
        v.delete()
        cs.assert_called('DELETE', '/volumes/1234')
        cs.volumes.delete('1234')
        cs.assert_called('DELETE', '/volumes/1234')
        cs.volumes.delete(v)
        cs.assert_called('DELETE', '/volumes/1234')

    def test_create_volume(self):
        cs.volumes.create(1)
        cs.assert_called('POST', '/volumes')

    def test_create_volume_with_hint(self):
        cs.volumes.create(1, scheduler_hints='uuid')
        expected = {'volume': {'status': 'creating',
                               'description': None,
                               'availability_zone': None,
                               'source_volid': None,
                               'snapshot_id': None,
                               'size': 1,
                               'user_id': None,
                               'name': None,
                               'imageRef': None,
                               'attach_status': 'detached',
                               'volume_type': None,
                               'project_id': None,
                               'metadata': {},
                               'source_replica': None,
                               'consistencygroup_id': None,
                               'multiattach': False},
                    'OS-SCH-HNT:scheduler_hints': 'uuid'}
        cs.assert_called('POST', '/volumes', body=expected)

    def test_attach(self):
        v = cs.volumes.get('1234')
        cs.volumes.attach(v, 1, '/dev/vdc', mode='ro')
        cs.assert_called('POST', '/volumes/1234/action')

    def test_attach_to_host(self):
        v = cs.volumes.get('1234')
        cs.volumes.attach(v, None, None, host_name='test', mode='rw')
        cs.assert_called('POST', '/volumes/1234/action')

    def test_detach(self):
        v = cs.volumes.get('1234')
        cs.volumes.detach(v, 'abc123')
        cs.assert_called('POST', '/volumes/1234/action')

    def test_reserve(self):
        v = cs.volumes.get('1234')
        cs.volumes.reserve(v)
        cs.assert_called('POST', '/volumes/1234/action')

    def test_unreserve(self):
        v = cs.volumes.get('1234')
        cs.volumes.unreserve(v)
        cs.assert_called('POST', '/volumes/1234/action')

    def test_begin_detaching(self):
        v = cs.volumes.get('1234')
        cs.volumes.begin_detaching(v)
        cs.assert_called('POST', '/volumes/1234/action')

    def test_roll_detaching(self):
        v = cs.volumes.get('1234')
        cs.volumes.roll_detaching(v)
        cs.assert_called('POST', '/volumes/1234/action')

    def test_initialize_connection(self):
        v = cs.volumes.get('1234')
        cs.volumes.initialize_connection(v, {})
        cs.assert_called('POST', '/volumes/1234/action')

    def test_terminate_connection(self):
        v = cs.volumes.get('1234')
        cs.volumes.terminate_connection(v, {})
        cs.assert_called('POST', '/volumes/1234/action')

    def test_set_metadata(self):
        cs.volumes.set_metadata(1234, {'k1': 'v2'})
        cs.assert_called('POST', '/volumes/1234/metadata',
                         {'metadata': {'k1': 'v2'}})

    def test_delete_metadata(self):
        keys = ['key1']
        cs.volumes.delete_metadata(1234, keys)
        cs.assert_called('DELETE', '/volumes/1234/metadata/key1')

    def test_extend(self):
        v = cs.volumes.get('1234')
        cs.volumes.extend(v, 2)
        cs.assert_called('POST', '/volumes/1234/action')

    def test_get_encryption_metadata(self):
        cs.volumes.get_encryption_metadata('1234')
        cs.assert_called('GET', '/volumes/1234/encryption')

    def test_migrate(self):
        v = cs.volumes.get('1234')
        cs.volumes.migrate_volume(v, 'dest', False)
        cs.assert_called('POST', '/volumes/1234/action')

    def test_metadata_update_all(self):
        cs.volumes.update_all_metadata(1234, {'k1': 'v1'})
        cs.assert_called('PUT', '/volumes/1234/metadata',
                         {'metadata': {'k1': 'v1'}})

    def test_readonly_mode_update(self):
        v = cs.volumes.get('1234')
        cs.volumes.update_readonly_flag(v, True)
        cs.assert_called('POST', '/volumes/1234/action')

    def test_retype(self):
        v = cs.volumes.get('1234')
        cs.volumes.retype(v, 'foo', 'on-demand')
        cs.assert_called('POST', '/volumes/1234/action',
                         {'os-retype': {'new_type': 'foo',
                                        'migration_policy': 'on-demand'}})

    def test_set_bootable(self):
        v = cs.volumes.get('1234')
        cs.volumes.set_bootable(v, True)
        cs.assert_called('POST', '/volumes/1234/action')

    def test_volume_manage(self):
        cs.volumes.manage('host1', {'k': 'v'})
        expected = {'host': 'host1', 'name': None, 'availability_zone': None,
                    'description': None, 'metadata': None, 'ref': {'k': 'v'},
                    'volume_type': None, 'bootable': False}
        cs.assert_called('POST', '/os-volume-manage', {'volume': expected})

    def test_volume_manage_bootable(self):
        cs.volumes.manage('host1', {'k': 'v'}, bootable=True)
        expected = {'host': 'host1', 'name': None, 'availability_zone': None,
                    'description': None, 'metadata': None, 'ref': {'k': 'v'},
                    'volume_type': None, 'bootable': True}
        cs.assert_called('POST', '/os-volume-manage', {'volume': expected})

    def test_volume_unmanage(self):
        v = cs.volumes.get('1234')
        cs.volumes.unmanage(v)
        cs.assert_called('POST', '/volumes/1234/action', {'os-unmanage': None})

    def test_replication_promote(self):
        v = cs.volumes.get('1234')
        cs.volumes.promote(v)
        cs.assert_called('POST', '/volumes/1234/action',
                         {'os-promote-replica': None})

    def test_replication_reenable(self):
        v = cs.volumes.get('1234')
        cs.volumes.reenable(v)
        cs.assert_called('POST', '/volumes/1234/action',
                         {'os-reenable-replica': None})

    def test_get_pools(self):
        cs.volumes.get_pools('')
        cs.assert_called('GET', '/scheduler-stats/get_pools')

    def test_get_pools_detail(self):
        cs.volumes.get_pools('--detail')
        cs.assert_called('GET', '/scheduler-stats/get_pools?detail=True')


class FormatSortParamTestCase(utils.TestCase):

    def test_format_sort_empty_input(self):
        for s in [None, '', []]:
            self.assertEqual(None, cs.volumes._format_sort_param(s))

    def test_format_sort_string_single_key(self):
        s = 'id'
        self.assertEqual('id', cs.volumes._format_sort_param(s))

    def test_format_sort_string_single_key_and_dir(self):
        s = 'id:asc'
        self.assertEqual('id:asc', cs.volumes._format_sort_param(s))

    def test_format_sort_string_multiple(self):
        s = 'id:asc,status,size:desc'
        self.assertEqual('id:asc,status,size:desc',
                         cs.volumes._format_sort_param(s))

    def test_format_sort_string_mappings(self):
        s = 'id:asc,name,size:desc'
        self.assertEqual('id:asc,display_name,size:desc',
                         cs.volumes._format_sort_param(s))

    def test_format_sort_whitespace_trailing_comma(self):
        s = ' id : asc ,status,  size:desc,'
        self.assertEqual('id:asc,status,size:desc',
                         cs.volumes._format_sort_param(s))

    def test_format_sort_list_of_strings(self):
        s = ['id:asc', 'status', 'size:desc']
        self.assertEqual('id:asc,status,size:desc',
                         cs.volumes._format_sort_param(s))

    def test_format_sort_list_of_tuples(self):
        s = [('id', 'asc'), 'status', ('size', 'desc')]
        self.assertEqual('id:asc,status,size:desc',
                         cs.volumes._format_sort_param(s))

    def test_format_sort_list_of_strings_and_tuples(self):
        s = [('id', 'asc'), 'status', 'size:desc']
        self.assertEqual('id:asc,status,size:desc',
                         cs.volumes._format_sort_param(s))

    def test_format_sort_invalid_direction(self):
        for s in ['id:foo',
                  'id:asc,status,size:foo',
                  ['id', 'status', 'size:foo'],
                  ['id', 'status', ('size', 'foo')]]:
            self.assertRaises(ValueError,
                              cs.volumes._format_sort_param,
                              s)
