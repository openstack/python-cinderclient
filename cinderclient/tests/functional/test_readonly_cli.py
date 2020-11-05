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
        """
        Test if the limits for the database limits.

        Args:
            self: (todo): write your description
        """
        limits = self.cinder('absolute-limits')
        self.assertTableHeaders(limits, ['Name', 'Value'])

    def test_availability_zones(self):
        """
        Test for availability zone.

        Args:
            self: (todo): write your description
        """
        zone_list = self.cinder('availability-zone-list')
        self.assertTableHeaders(zone_list, ['Name', 'Status'])

    def test_backup_list(self):
        """
        Test for backup backup.

        Args:
            self: (todo): write your description
        """
        backup_list = self.cinder('backup-list')
        self.assertTableHeaders(backup_list, ['ID', 'Volume ID', 'Status',
                                              'Name', 'Size', 'Object Count',
                                              'Container'])

    def test_encryption_type_list(self):
        """
        Encrypts of the encryption types.

        Args:
            self: (todo): write your description
        """
        encrypt_list = self.cinder('encryption-type-list')
        self.assertTableHeaders(encrypt_list, ['Volume Type ID', 'Provider',
                                               'Cipher', 'Key Size',
                                               'Control Location'])

    def test_extra_specs_list(self):
        """
        Lists extra extra specs.

        Args:
            self: (todo): write your description
        """
        extra_specs_list = self.cinder('extra-specs-list')
        self.assertTableHeaders(extra_specs_list, ['ID', 'Name',
                                                   'extra_specs'])

    def test_list(self):
        """
        Lists all the test list.

        Args:
            self: (todo): write your description
        """
        list = self.cinder('list')
        self.assertTableHeaders(list, ['ID', 'Status', 'Name', 'Size',
                                       'Volume Type', 'Bootable',
                                       'Attached to'])

    def test_qos_list(self):
        """
        List qos qos qos.

        Args:
            self: (todo): write your description
        """
        qos_list = self.cinder('qos-list')
        self.assertTableHeaders(qos_list, ['ID', 'Name', 'Consumer', 'specs'])

    def test_rate_limits(self):
        """
        Test if rate limit.

        Args:
            self: (todo): write your description
        """
        rate_limits = self.cinder('rate-limits')
        self.assertTableHeaders(rate_limits, ['Verb', 'URI', 'Value', 'Remain',
                                              'Unit', 'Next_Available'])

    def test_service_list(self):
        """
        Returns a list of all service instances.

        Args:
            self: (todo): write your description
        """
        service_list = self.cinder('service-list')
        self.assertTableHeaders(service_list, ['Binary', 'Host', 'Zone',
                                               'Status', 'State',
                                               'Updated_at'])

    def test_snapshot_list(self):
        """
        Test snapshot snapshot of snapshot

        Args:
            self: (todo): write your description
        """
        snapshot_list = self.cinder('snapshot-list')
        self.assertTableHeaders(snapshot_list, ['ID', 'Volume ID', 'Status',
                                                'Name', 'Size'])

    def test_transfer_list(self):
        """
        List all transfer transfer transfer.

        Args:
            self: (todo): write your description
        """
        transfer_list = self.cinder('transfer-list')
        self.assertTableHeaders(transfer_list, ['ID', 'Volume ID', 'Name'])

    def test_type_list(self):
        """
        Set the test types.

        Args:
            self: (todo): write your description
        """
        type_list = self.cinder('type-list')
        self.assertTableHeaders(type_list, ['ID', 'Name'])

    def test_list_extensions(self):
        """
        List all extensions.

        Args:
            self: (todo): write your description
        """
        list_extensions = self.cinder('list-extensions')
        self.assertTableHeaders(list_extensions, ['Name', 'Summary', 'Alias',
                                                  'Updated'])
