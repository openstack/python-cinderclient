# Copyright (C) 2012 - 2014 EMC Corporation.
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

cs = fakes.FakeClient()


class ConsistencygroupsTest(utils.TestCase):

    def test_delete_consistencygroup(self):
        v = cs.consistencygroups.list()[0]
        v.delete(force='True')
        cs.assert_called('POST', '/consistencygroups/1234/delete')
        cs.consistencygroups.delete('1234', force=True)
        cs.assert_called('POST', '/consistencygroups/1234/delete')
        cs.consistencygroups.delete(v, force=True)
        cs.assert_called('POST', '/consistencygroups/1234/delete')

    def test_create_consistencygroup(self):
        cs.consistencygroups.create('type1,type2', 'cg')
        cs.assert_called('POST', '/consistencygroups')

    def test_create_consistencygroup_with_volume_types(self):
        cs.consistencygroups.create('type1,type2', 'cg')
        expected = {'consistencygroup': {'status': 'creating',
                                         'description': None,
                                         'availability_zone': None,
                                         'user_id': None,
                                         'name': 'cg',
                                         'volume_types': 'type1,type2',
                                         'project_id': None}}
        cs.assert_called('POST', '/consistencygroups', body=expected)

    def test_update_consistencygroup_name(self):
        v = cs.consistencygroups.list()[0]
        expected = {'consistencygroup': {'name': 'cg2'}}
        v.update(name='cg2')
        cs.assert_called('PUT', '/consistencygroups/1234', body=expected)
        cs.consistencygroups.update('1234', name='cg2')
        cs.assert_called('PUT', '/consistencygroups/1234', body=expected)
        cs.consistencygroups.update(v, name='cg2')
        cs.assert_called('PUT', '/consistencygroups/1234', body=expected)

    def test_update_consistencygroup_description(self):
        v = cs.consistencygroups.list()[0]
        expected = {'consistencygroup': {'description': 'cg2 desc'}}
        v.update(description='cg2 desc')
        cs.assert_called('PUT', '/consistencygroups/1234', body=expected)
        cs.consistencygroups.update('1234', description='cg2 desc')
        cs.assert_called('PUT', '/consistencygroups/1234', body=expected)
        cs.consistencygroups.update(v, description='cg2 desc')
        cs.assert_called('PUT', '/consistencygroups/1234', body=expected)

    def test_update_consistencygroup_add_volumes(self):
        v = cs.consistencygroups.list()[0]
        uuids = 'uuid1,uuid2'
        expected = {'consistencygroup': {'add_volumes': uuids}}
        v.update(add_volumes=uuids)
        cs.assert_called('PUT', '/consistencygroups/1234', body=expected)
        cs.consistencygroups.update('1234', add_volumes=uuids)
        cs.assert_called('PUT', '/consistencygroups/1234', body=expected)
        cs.consistencygroups.update(v, add_volumes=uuids)
        cs.assert_called('PUT', '/consistencygroups/1234', body=expected)

    def test_update_consistencygroup_remove_volumes(self):
        v = cs.consistencygroups.list()[0]
        uuids = 'uuid3,uuid4'
        expected = {'consistencygroup': {'remove_volumes': uuids}}
        v.update(remove_volumes=uuids)
        cs.assert_called('PUT', '/consistencygroups/1234', body=expected)
        cs.consistencygroups.update('1234', remove_volumes=uuids)
        cs.assert_called('PUT', '/consistencygroups/1234', body=expected)
        cs.consistencygroups.update(v, remove_volumes=uuids)
        cs.assert_called('PUT', '/consistencygroups/1234', body=expected)

    def test_update_consistencygroup_none(self):
        self.assertEqual(None, cs.consistencygroups.update('1234'))

    def test_update_consistencygroup_no_props(self):
        cs.consistencygroups.update('1234')

    def test_create_consistencygroup_from_src(self):
        cs.consistencygroups.create_from_src('5678', name='cg')
        expected = {
            'consistencygroup-from-src': {
                'status': 'creating',
                'description': None,
                'user_id': None,
                'name': 'cg',
                'cgsnapshot_id': '5678',
                'project_id': None
            }
        }
        cs.assert_called('POST', '/consistencygroups/create_from_src',
                         body=expected)

    def test_list_consistencygroup(self):
        cs.consistencygroups.list()
        cs.assert_called('GET', '/consistencygroups/detail')

    def test_list_consistencygroup_detailed_false(self):
        cs.consistencygroups.list(detailed=False)
        cs.assert_called('GET', '/consistencygroups')

    def test_list_consistencygroup_with_search_opts(self):
        cs.consistencygroups.list(search_opts={'foo': 'bar'})
        cs.assert_called('GET', '/consistencygroups/detail?foo=bar')

    def test_list_consistencygroup_with_empty_search_opt(self):
        cs.consistencygroups.list(search_opts={'foo': 'bar', 'abc': None})
        cs.assert_called('GET', '/consistencygroups/detail?foo=bar')

    def test_get_consistencygroup(self):
        consistencygroup_id = '1234'
        cs.consistencygroups.get(consistencygroup_id)
        cs.assert_called('GET', '/consistencygroups/%s' % consistencygroup_id)
