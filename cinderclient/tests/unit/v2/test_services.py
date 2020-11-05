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

from cinderclient.tests.unit import utils
from cinderclient.tests.unit.v2 import fakes
from cinderclient.v2 import services


cs = fakes.FakeClient()


class ServicesTest(utils.TestCase):

    def test_list_services(self):
        """
        Return a list of the services.

        Args:
            self: (todo): write your description
        """
        svs = cs.services.list()
        cs.assert_called('GET', '/os-services')
        self.assertEqual(3, len(svs))
        for service in svs:
            self.assertIsInstance(service, services.Service)
            # Make sure cluster fields from v3.7 are not there
            self.assertFalse(hasattr(service, 'cluster'))
        self._assert_request_id(svs)

    def test_list_services_with_hostname(self):
        """
        Check if a list of services in a list of services.

        Args:
            self: (todo): write your description
        """
        svs = cs.services.list(host='host2')
        cs.assert_called('GET', '/os-services?host=host2')
        self.assertEqual(2, len(svs))
        [self.assertIsInstance(s, services.Service) for s in svs]
        [self.assertEqual('host2', s.host) for s in svs]
        self._assert_request_id(svs)

    def test_list_services_with_binary(self):
        """
        Get a list of services.

        Args:
            self: (todo): write your description
        """
        svs = cs.services.list(binary='cinder-volume')
        cs.assert_called('GET', '/os-services?binary=cinder-volume')
        self.assertEqual(2, len(svs))
        [self.assertIsInstance(s, services.Service) for s in svs]
        [self.assertEqual('cinder-volume', s.binary) for s in svs]
        self._assert_request_id(svs)

    def test_list_services_with_host_binary(self):
        """
        List all services in - enabled list of services.

        Args:
            self: (todo): write your description
        """
        svs = cs.services.list('host2', 'cinder-volume')
        cs.assert_called('GET', '/os-services?host=host2&binary=cinder-volume')
        self.assertEqual(1, len(svs))
        [self.assertIsInstance(s, services.Service) for s in svs]
        [self.assertEqual('host2', s.host) for s in svs]
        [self.assertEqual('cinder-volume', s.binary) for s in svs]
        self._assert_request_id(svs)

    def test_services_enable(self):
        """
        Enable services that are enabled.

        Args:
            self: (todo): write your description
        """
        s = cs.services.enable('host1', 'cinder-volume')
        values = {"host": "host1", 'binary': 'cinder-volume'}
        cs.assert_called('PUT', '/os-services/enable', values)
        self.assertIsInstance(s, services.Service)
        self.assertEqual('enabled', s.status)
        self._assert_request_id(s)

    def test_services_disable(self):
        """
        Disable services that services.

        Args:
            self: (todo): write your description
        """
        s = cs.services.disable('host1', 'cinder-volume')
        values = {"host": "host1", 'binary': 'cinder-volume'}
        cs.assert_called('PUT', '/os-services/disable', values)
        self.assertIsInstance(s, services.Service)
        self.assertEqual('disabled', s.status)
        self._assert_request_id(s)

    def test_services_disable_log_reason(self):
        """
        Test for services that are enabled.

        Args:
            self: (todo): write your description
        """
        s = cs.services.disable_log_reason(
            'host1', 'cinder-volume', 'disable bad host')
        values = {"host": "host1", 'binary': 'cinder-volume',
                  "disabled_reason": "disable bad host"}
        cs.assert_called('PUT', '/os-services/disable-log-reason', values)
        self.assertIsInstance(s, services.Service)
        self.assertEqual('disabled', s.status)
        self._assert_request_id(s)
