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


from cinderclient.tests.functional import base


class CinderClientReadOnlyTests(base.ClientTestBase):
    """Basic read-only test for cinderclient.

    Simple check of base list commands, verify they
    respond and include the expected headers in the
    resultant table.

    Not intended for testing things that require actual
    resource creation/manipulation, thus the name 'read-only'.

    """

    # Commands in order listed in 'cinder help'
    def test_absolute_limits(self):
        limits = self.parser.listing(self.cinder('absolute-limits'))
        self.assertTableStruct(limits, ['Name', 'Value'])

    def test_availability_zones(self):
        zone_list = self.parser.listing(self.cinder('availability-zone-list'))
        self.assertTableStruct(zone_list, ['Name', 'Status'])

    def test_backup_list(self):
        backup_list = self.parser.listing(self.cinder('backup-list'))
        self.assertTableStruct(backup_list, ['ID', 'Volume ID', 'Status',
                                             'Name', 'Size', 'Object Count',
                                             'Container'])

    def test_encryption_type_list(self):
        encrypt_list = self.parser.listing(self.cinder('encryption-type-list'))
        self.assertTableStruct(encrypt_list, ['Volume Type ID', 'Provider',
                                              'Cipher', 'Key Size',
                                              'Control Location'])

    def test_endpoints(self):
        out = self.cinder('endpoints')
        tables = self.parser.tables(out)
        for table in tables:
            headers = table['headers']
            self.assertTrue(2 >= len(headers))
            self.assertEqual('Value', headers[1])

    def test_list(self):
        list = self.parser.listing(self.cinder('list'))
        self.assertTableStruct(list, ['ID', 'Status', 'Name', 'Size',
                                      'Volume Type', 'Bootable',
                                      'Attached to'])

    def test_qos_list(self):
        qos_list = self.parser.listing(self.cinder('qos-list'))
        self.assertTableStruct(qos_list, ['ID', 'Name', 'Consumer', 'specs'])

    def test_rate_limits(self):
        rate_limits = self.parser.listing(self.cinder('rate-limits'))
        self.assertTableStruct(rate_limits, ['Verb', 'URI', 'Value', 'Remain',
                                             'Unit', 'Next_Available'])

    def test_service_list(self):
        service_list = self.parser.listing(self.cinder('service-list'))
        self.assertTableStruct(service_list, ['Binary', 'Host', 'Zone',
                                              'Status', 'State', 'Updated_at'])

    def test_snapshot_list(self):
        snapshot_list = self.parser.listing(self.cinder('snapshot-list'))
        self.assertTableStruct(snapshot_list, ['ID', 'Volume ID', 'Status',
                                               'Name', 'Size'])

    def test_transfer_list(self):
        transfer_list = self.parser.listing(self.cinder('transfer-list'))
        self.assertTableStruct(transfer_list, ['ID', 'Volume ID', 'Name'])

    def test_type_list(self):
        type_list = self.parser.listing(self.cinder('type-list'))
        self.assertTableStruct(type_list, ['ID', 'Name'])
