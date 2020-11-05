# Copyright (C) 2016 EMC Corporation.
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

import ddt

from cinderclient import api_versions
from cinderclient.tests.unit import utils
from cinderclient.tests.unit.v3 import fakes

cs = fakes.FakeClient(api_versions.APIVersion('3.13'))


@ddt.ddt
class GroupsTest(utils.TestCase):

    def test_delete_group(self):
        """
        Deletes the group

        Args:
            self: (todo): write your description
        """
        expected = {'delete': {'delete-volumes': True}}
        v = cs.groups.list()[0]
        grp = v.delete(delete_volumes=True)
        self._assert_request_id(grp)
        cs.assert_called('POST', '/groups/1234/action', body=expected)
        grp = cs.groups.delete('1234', delete_volumes=True)
        self._assert_request_id(grp)
        cs.assert_called('POST', '/groups/1234/action', body=expected)
        grp = cs.groups.delete(v, delete_volumes=True)
        self._assert_request_id(grp)
        cs.assert_called('POST', '/groups/1234/action', body=expected)

    def test_create_group(self):
        """
        Create a new group

        Args:
            self: (todo): write your description
        """
        grp = cs.groups.create('my_group_type', 'type1,type2', name='group')
        cs.assert_called('POST', '/groups')
        self._assert_request_id(grp)

    def test_create_group_with_volume_types(self):
        """
        Create a storage group groups.

        Args:
            self: (todo): write your description
        """
        grp = cs.groups.create('my_group_type', 'type1,type2', name='group')
        expected = {'group': {'description': None,
                              'availability_zone': None,
                              'name': 'group',
                              'group_type': 'my_group_type',
                              'volume_types': ['type1', 'type2']}}
        cs.assert_called('POST', '/groups', body=expected)
        self._assert_request_id(grp)

    @ddt.data(
        {'name': 'group2', 'desc': None, 'add': None, 'remove': None},
        {'name': None, 'desc': 'group2 desc', 'add': None, 'remove': None},
        {'name': None, 'desc': None, 'add': 'uuid1,uuid2', 'remove': None},
        {'name': None, 'desc': None, 'add': None, 'remove': 'uuid3,uuid4'},
    )
    @ddt.unpack
    def test_update_group_name(self, name, desc, add, remove):
        """
        Update the group name

        Args:
            self: (todo): write your description
            name: (str): write your description
            desc: (str): write your description
            add: (todo): write your description
            remove: (bool): write your description
        """
        v = cs.groups.list()[0]
        expected = {'group': {'name': name, 'description': desc,
                              'add_volumes': add, 'remove_volumes': remove}}
        grp = v.update(name=name, description=desc,
                       add_volumes=add, remove_volumes=remove)
        cs.assert_called('PUT', '/groups/1234', body=expected)
        self._assert_request_id(grp)
        grp = cs.groups.update('1234', name=name, description=desc,
                               add_volumes=add, remove_volumes=remove)
        cs.assert_called('PUT', '/groups/1234', body=expected)
        self._assert_request_id(grp)
        grp = cs.groups.update(v, name=name, description=desc,
                               add_volumes=add, remove_volumes=remove)
        cs.assert_called('PUT', '/groups/1234', body=expected)
        self._assert_request_id(grp)

    def test_update_group_none(self):
        """
        Check if the test is none if none.

        Args:
            self: (todo): write your description
        """
        self.assertIsNone(cs.groups.update('1234'))

    def test_update_group_no_props(self):
        """
        Update the test_group_no_group.

        Args:
            self: (todo): write your description
        """
        cs.groups.update('1234')

    def test_list_group(self):
        """
        Add a list of groups of the group.

        Args:
            self: (todo): write your description
        """
        lst = cs.groups.list()
        cs.assert_called('GET', '/groups/detail')
        self._assert_request_id(lst)

    def test_list_group_detailed_false(self):
        """
        This is a list of a list of groups in the group.

        Args:
            self: (todo): write your description
        """
        lst = cs.groups.list(detailed=False)
        cs.assert_called('GET', '/groups')
        self._assert_request_id(lst)

    def test_list_group_with_search_opts(self):
        """
        Test if a request to search

        Args:
            self: (todo): write your description
        """
        lst = cs.groups.list(search_opts={'foo': 'bar'})
        cs.assert_called('GET', '/groups/detail?foo=bar')
        self._assert_request_id(lst)

    def test_list_group_with_volume(self):
        """
        Test if a list of a volume group

        Args:
            self: (todo): write your description
        """
        lst = cs.groups.list(list_volume=True)
        cs.assert_called('GET', '/groups/detail?list_volume=True')
        self._assert_request_id(lst)

    def test_list_group_with_empty_search_opt(self):
        """
        Add a list of all groups in - group

        Args:
            self: (todo): write your description
        """
        lst = cs.groups.list(
            search_opts={'foo': 'bar', 'abc': None}
        )
        cs.assert_called('GET', '/groups/detail?foo=bar')
        self._assert_request_id(lst)

    def test_get_group(self):
        """
        Returns the group of the group

        Args:
            self: (todo): write your description
        """
        group_id = '1234'
        grp = cs.groups.get(group_id)
        cs.assert_called('GET', '/groups/%s' % group_id)
        self._assert_request_id(grp)

    def test_get_group_with_list_volume(self):
        """
        Get a list of all groups

        Args:
            self: (todo): write your description
        """
        group_id = '1234'
        grp = cs.groups.get(group_id, list_volume=True)
        cs.assert_called('GET', '/groups/%s?list_volume=True' % group_id)
        self._assert_request_id(grp)

    def test_create_group_from_src_snap(self):
        """
        Create a new snapshot.

        Args:
            self: (todo): write your description
        """
        cs = fakes.FakeClient(api_versions.APIVersion('3.14'))
        grp = cs.groups.create_from_src('5678', None, name='group')
        expected = {
            'create-from-src': {
                'description': None,
                'name': 'group',
                'group_snapshot_id': '5678'
            }
        }
        cs.assert_called('POST', '/groups/action',
                         body=expected)
        self._assert_request_id(grp)

    def test_create_group_from_src_group_(self):
        """
        Create a new group from a src group.

        Args:
            self: (todo): write your description
        """
        cs = fakes.FakeClient(api_versions.APIVersion('3.14'))
        grp = cs.groups.create_from_src(None, '5678', name='group')
        expected = {
            'create-from-src': {
                'description': None,
                'name': 'group',
                'source_group_id': '5678'
            }
        }
        cs.assert_called('POST', '/groups/action',
                         body=expected)
        self._assert_request_id(grp)

    def test_enable_replication_group(self):
        """
        Enable replication group.

        Args:
            self: (todo): write your description
        """
        cs = fakes.FakeClient(api_versions.APIVersion('3.38'))
        expected = {'enable_replication': {}}
        g0 = cs.groups.list()[0]
        grp = g0.enable_replication()
        self._assert_request_id(grp)
        cs.assert_called('POST', '/groups/1234/action', body=expected)
        grp = cs.groups.enable_replication('1234')
        self._assert_request_id(grp)
        cs.assert_called('POST', '/groups/1234/action', body=expected)
        grp = cs.groups.enable_replication(g0)
        self._assert_request_id(grp)
        cs.assert_called('POST', '/groups/1234/action', body=expected)

    def test_disable_replication_group(self):
        """
        Disables replication group.

        Args:
            self: (todo): write your description
        """
        cs = fakes.FakeClient(api_versions.APIVersion('3.38'))
        expected = {'disable_replication': {}}
        g0 = cs.groups.list()[0]
        grp = g0.disable_replication()
        self._assert_request_id(grp)
        cs.assert_called('POST', '/groups/1234/action', body=expected)
        grp = cs.groups.disable_replication('1234')
        self._assert_request_id(grp)
        cs.assert_called('POST', '/groups/1234/action', body=expected)
        grp = cs.groups.disable_replication(g0)
        self._assert_request_id(grp)
        cs.assert_called('POST', '/groups/1234/action', body=expected)

    def test_failover_replication_group(self):
        """
        Test for replication group.

        Args:
            self: (todo): write your description
        """
        cs = fakes.FakeClient(api_versions.APIVersion('3.38'))
        expected = {'failover_replication':
                    {'allow_attached_volume': False,
                     'secondary_backend_id': None}}
        g0 = cs.groups.list()[0]
        grp = g0.failover_replication()
        self._assert_request_id(grp)
        cs.assert_called('POST', '/groups/1234/action', body=expected)
        grp = cs.groups.failover_replication('1234')
        self._assert_request_id(grp)
        cs.assert_called('POST', '/groups/1234/action', body=expected)
        grp = cs.groups.failover_replication(g0)
        self._assert_request_id(grp)
        cs.assert_called('POST', '/groups/1234/action', body=expected)

    def test_list_replication_targets(self):
        """
        List replication replication groups.

        Args:
            self: (todo): write your description
        """
        cs = fakes.FakeClient(api_versions.APIVersion('3.38'))
        expected = {'list_replication_targets': {}}
        g0 = cs.groups.list()[0]
        grp = g0.list_replication_targets()
        self._assert_request_id(grp)
        cs.assert_called('POST', '/groups/1234/action', body=expected)
        grp = cs.groups.list_replication_targets('1234')
        self._assert_request_id(grp)
        cs.assert_called('POST', '/groups/1234/action', body=expected)
        grp = cs.groups.list_replication_targets(g0)
        self._assert_request_id(grp)
        cs.assert_called('POST', '/groups/1234/action', body=expected)
