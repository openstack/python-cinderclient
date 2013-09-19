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

from cinderclient.tests import utils
from cinderclient.tests.v1 import fakes
from cinderclient.v1 import services


cs = fakes.FakeClient()


class ServicesTest(utils.TestCase):

    def test_list_services(self):
        svs = cs.services.list()
        cs.assert_called('GET', '/os-services')
        self.assertEqual(len(svs), 3)
        [self.assertTrue(isinstance(s, services.Service)) for s in svs]

    def test_list_services_with_hostname(self):
        svs = cs.services.list(host='host2')
        cs.assert_called('GET', '/os-services?host=host2')
        self.assertEqual(len(svs), 2)
        [self.assertTrue(isinstance(s, services.Service)) for s in svs]
        [self.assertEqual(s.host, 'host2') for s in svs]

    def test_list_services_with_binary(self):
        svs = cs.services.list(binary='cinder-volume')
        cs.assert_called('GET', '/os-services?binary=cinder-volume')
        self.assertEqual(len(svs), 2)
        [self.assertTrue(isinstance(s, services.Service)) for s in svs]
        [self.assertEqual(s.binary, 'cinder-volume') for s in svs]

    def test_list_services_with_host_binary(self):
        svs = cs.services.list('host2', 'cinder-volume')
        cs.assert_called('GET', '/os-services?host=host2&binary=cinder-volume')
        self.assertEqual(len(svs), 1)
        [self.assertTrue(isinstance(s, services.Service)) for s in svs]
        [self.assertEqual(s.host, 'host2') for s in svs]
        [self.assertEqual(s.binary, 'cinder-volume') for s in svs]

    def test_services_enable(self):
        cs.services.enable('host1', 'cinder-volume')
        values = {"host": "host1", 'binary': 'cinder-volume'}
        cs.assert_called('PUT', '/os-services/enable', values)

    def test_services_disable(self):
        cs.services.disable('host1', 'cinder-volume')
        values = {"host": "host1", 'binary': 'cinder-volume'}
        cs.assert_called('PUT', '/os-services/disable', values)
