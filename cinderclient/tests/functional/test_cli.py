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


import sys
import unittest

from cinderclient.tests.functional import base


class CinderVolumeTests(base.ClientTestBase):
    """Check of base cinder volume commands."""

    CREATE_VOLUME_PROPERTY = (
        'attachments',
        'os-vol-tenant-attr:tenant_id',
        'availability_zone', 'bootable',
        'created_at', 'description', 'encrypted', 'id',
        'metadata', 'name', 'size', 'status',
        'user_id', 'volume_type')

    SHOW_VOLUME_PROPERTY = ('attachment_ids', 'attached_servers',
                       'availability_zone', 'bootable',
                       'created_at', 'description', 'encrypted', 'id',
                       'metadata', 'name', 'size', 'status',
                       'user_id', 'volume_type')

    def test_volume_create_delete_id(self):
        """Create and delete a volume by ID."""
        volume = self.object_create('volume', params='1')
        self.assert_object_details(self.CREATE_VOLUME_PROPERTY, volume.keys())
        self.object_delete('volume', volume['id'])
        self.check_object_deleted('volume', volume['id'])

    def test_volume_create_delete_name(self):
        """Create and delete a volume by name."""
        volume = self.object_create('volume',
                                    params='1 --name TestVolumeNamedCreate')

        self.cinder('delete', params='TestVolumeNamedCreate')
        self.check_object_deleted('volume', volume['id'])

    def test_volume_show(self):
        """Show volume details."""
        volume = self.object_create('volume', params='1 --name TestVolumeShow')
        output = self.cinder('show', params='TestVolumeShow')
        volume = self._get_property_from_output(output)
        self.assertEqual('TestVolumeShow', volume['name'])
        self.assert_object_details(self.SHOW_VOLUME_PROPERTY, volume.keys())

        self.object_delete('volume', volume['id'])
        self.check_object_deleted('volume', volume['id'])

    def test_volume_extend(self):
        """Extend a volume size."""
        volume = self.object_create('volume',
                                    params='1 --name TestVolumeExtend')
        self.cinder('extend', params="%s %s" % (volume['id'], 2))
        self.wait_for_object_status('volume', volume['id'], 'available')
        output = self.cinder('show', params=volume['id'])
        volume = self._get_property_from_output(output)
        self.assertEqual('2', volume['size'])

        self.object_delete('volume', volume['id'])
        self.check_object_deleted('volume', volume['id'])


class CinderSnapshotTests(base.ClientTestBase):
    """Check of base cinder snapshot commands."""

    SNAPSHOT_PROPERTY = ('created_at', 'description', 'metadata', 'id',
                         'name', 'size', 'status', 'volume_id')

    def test_snapshot_create_and_delete(self):
        """Create a volume snapshot and then delete."""
        volume = self.object_create('volume', params='1')
        snapshot = self.object_create('snapshot', params=volume['id'])
        self.assert_object_details(self.SNAPSHOT_PROPERTY, snapshot.keys())
        self.object_delete('snapshot', snapshot['id'])
        self.check_object_deleted('snapshot', snapshot['id'])
        self.object_delete('volume', volume['id'])
        self.check_object_deleted('volume', volume['id'])


class CinderBackupTests(base.ClientTestBase):
    """Check of base cinder backup commands."""

    BACKUP_PROPERTY = ('id', 'name', 'volume_id')

    @unittest.skipIf((sys.version_info[0] == 3 and sys.version_info[1] == 9),
                     "This test is failing because of bug#2008010")
    def test_backup_create_and_delete(self):
        """Create a volume backup and then delete."""
        volume = self.object_create('volume', params='1')
        backup = self.object_create('backup', params=volume['id'])
        self.assert_object_details(self.BACKUP_PROPERTY, backup.keys())
        self.object_delete('volume', volume['id'])
        self.check_object_deleted('volume', volume['id'])
        self.object_delete('backup', backup['id'])
        self.check_object_deleted('backup', backup['id'])


class VolumeTransferTests(base.ClientTestBase):
    """Check of base cinder volume transfers command"""

    TRANSFER_PROPERTY = ('created_at', 'volume_id', 'id', 'auth_key', 'name')
    TRANSFER_SHOW_PROPERTY = ('created_at', 'volume_id', 'id', 'name')

    def test_transfer_create_delete(self):
        """Create and delete a volume transfer"""
        volume = self.object_create('volume', params='1')
        transfer = self.object_create('transfer', params=volume['id'])
        self.assert_object_details(self.TRANSFER_PROPERTY, transfer.keys())
        self.object_delete('transfer', transfer['id'])
        self.check_object_deleted('transfer', transfer['id'])
        self.object_delete('volume', volume['id'])
        self.check_object_deleted('volume', volume['id'])

    def test_transfer_show_delete_by_name(self):
        """Show volume transfer by name"""
        volume = self.object_create('volume', params='1')
        self.object_create(
            'transfer',
            params=('%s --name TEST_TRANSFER_SHOW' % volume['id']))
        output = self.cinder('transfer-show', params='TEST_TRANSFER_SHOW')
        transfer = self._get_property_from_output(output)
        self.assertEqual('TEST_TRANSFER_SHOW', transfer['name'])
        self.assert_object_details(self.TRANSFER_SHOW_PROPERTY,
                                   transfer.keys())
        self.object_delete('transfer', 'TEST_TRANSFER_SHOW')
        self.check_object_deleted('transfer', 'TEST_TRANSFER_SHOW')
        self.object_delete('volume', volume['id'])
        self.check_object_deleted('volume', volume['id'])
