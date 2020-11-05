# Copyright (C) 2013 eBay Inc.
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


class QoSSpecsTest(utils.TestCase):

    def test_create(self):
        """
        Creates a test

        Args:
            self: (todo): write your description
        """
        specs = dict(k1='v1', k2='v2')
        qos = cs.qos_specs.create('qos-name', specs)
        cs.assert_called('POST', '/qos-specs')
        self._assert_request_id(qos)

    def test_get(self):
        """
        Get the test information about the test.

        Args:
            self: (todo): write your description
        """
        qos_id = '1B6B6A04-A927-4AEB-810B-B7BAAD49F57C'
        qos = cs.qos_specs.get(qos_id)
        cs.assert_called('GET', '/qos-specs/%s' % qos_id)
        self._assert_request_id(qos)

    def test_list(self):
        """
        Set the test list.

        Args:
            self: (todo): write your description
        """
        lst = cs.qos_specs.list()
        cs.assert_called('GET', '/qos-specs')
        self._assert_request_id(lst)

    def test_delete(self):
        """
        Deletes the test.

        Args:
            self: (todo): write your description
        """
        qos = cs.qos_specs.delete('1B6B6A04-A927-4AEB-810B-B7BAAD49F57C')
        cs.assert_called('DELETE',
                         '/qos-specs/1B6B6A04-A927-4AEB-810B-B7BAAD49F57C?'
                         'force=False')
        self._assert_request_id(qos)

    def test_set_keys(self):
        """
        Set the test keys.

        Args:
            self: (todo): write your description
        """
        body = {'qos_specs': dict(k1='v1')}
        qos_id = '1B6B6A04-A927-4AEB-810B-B7BAAD49F57C'
        qos = cs.qos_specs.set_keys(qos_id, body)
        cs.assert_called('PUT', '/qos-specs/%s' % qos_id)
        self._assert_request_id(qos)

    def test_unset_keys(self):
        """
        Removes the unset.

        Args:
            self: (todo): write your description
        """
        qos_id = '1B6B6A04-A927-4AEB-810B-B7BAAD49F57C'
        body = {'keys': ['k1']}
        qos = cs.qos_specs.unset_keys(qos_id, body)
        cs.assert_called('PUT', '/qos-specs/%s/delete_keys' % qos_id)
        self._assert_request_id(qos)

    def test_get_associations(self):
        """
        Gets the id of qos

        Args:
            self: (todo): write your description
        """
        qos_id = '1B6B6A04-A927-4AEB-810B-B7BAAD49F57C'
        qos = cs.qos_specs.get_associations(qos_id)
        cs.assert_called('GET', '/qos-specs/%s/associations' % qos_id)
        self._assert_request_id(qos)

    def test_associate(self):
        """
        Associate the qos_id.

        Args:
            self: (todo): write your description
        """
        qos_id = '1B6B6A04-A927-4AEB-810B-B7BAAD49F57C'
        type_id = '4230B13A-7A37-4E84-B777-EFBA6FCEE4FF'
        qos = cs.qos_specs.associate(qos_id, type_id)
        cs.assert_called('GET', '/qos-specs/%s/associate?vol_type_id=%s'
                         % (qos_id, type_id))
        self._assert_request_id(qos)

    def test_disassociate(self):
        """
        Disassociate of the test.

        Args:
            self: (todo): write your description
        """
        qos_id = '1B6B6A04-A927-4AEB-810B-B7BAAD49F57C'
        type_id = '4230B13A-7A37-4E84-B777-EFBA6FCEE4FF'
        qos = cs.qos_specs.disassociate(qos_id, type_id)
        cs.assert_called('GET', '/qos-specs/%s/disassociate?vol_type_id=%s'
                         % (qos_id, type_id))
        self._assert_request_id(qos)

    def test_disassociate_all(self):
        """
        Disassociate all qos.

        Args:
            self: (todo): write your description
        """
        qos_id = '1B6B6A04-A927-4AEB-810B-B7BAAD49F57C'
        qos = cs.qos_specs.disassociate_all(qos_id)
        cs.assert_called('GET', '/qos-specs/%s/disassociate_all' % qos_id)
        self._assert_request_id(qos)
