# Copyright (c) 2013 OpenStack, LLC.
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

from tests import utils
from tests.v2 import fakes


cs = fakes.FakeClient()


class VolumesTest(utils.TestCase):

    def test_delete_volume(self):
        v = cs.volumes.list()[0]
        v.delete()
        cs.assert_called('DELETE', '/volumes/1234')
        cs.volumes.delete('1234')
        cs.assert_called('DELETE', '/volumes/1234')
        cs.volumes.delete(v)
        cs.assert_called('DELETE', '/volumes/1234')

    def test_create_keypair(self):
        cs.volumes.create(1)
        cs.assert_called('POST', '/volumes')

    def test_attach(self):
        v = cs.volumes.get('1234')
        cs.volumes.attach(v, 1, '/dev/vdc')
        cs.assert_called('POST', '/volumes/1234/action')

    def test_detach(self):
        v = cs.volumes.get('1234')
        cs.volumes.detach(v)
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
