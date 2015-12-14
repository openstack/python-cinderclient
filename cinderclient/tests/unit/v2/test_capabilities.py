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

from cinderclient.tests.unit import utils
from cinderclient.tests.unit.v2 import fakes

cs = fakes.FakeClient()


class CapabilitiesTest(utils.TestCase):

    def test_get_capabilities(self):
        expected = {
            'namespace': 'OS::Storage::Capabilities::fake',
            'vendor_name': 'OpenStack',
            'volume_backend_name': 'lvm',
            'pool_name': 'pool',
            'storage_protocol': 'iSCSI',
            'properties': {
                'compression': {
                    'title': 'Compression',
                    'description': 'Enables compression.',
                    'type': 'boolean'},
            }
        }

        capabilities = cs.capabilities.get('host')
        cs.assert_called('GET', '/capabilities/host')
        self.assertEqual(expected, capabilities._info)
        self._assert_request_id(capabilities)
