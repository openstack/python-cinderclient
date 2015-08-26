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


class CinderClientTests(base.ClientTestBase):
    """Basic test for cinder client.

    Check of base cinder commands.
    """
    def test_volume_create_delete_id(self):
        """Create and delete a volume by ID."""
        volume = self.volume_create(params='1')
        self.assert_volume_details(volume.keys())
        self.volume_delete(volume['id'])
        self.check_volume_deleted(volume['id'])

    def test_volume_create_delete_name(self):
        """Create and delete a volume by name."""
        volume = self.volume_create(params='1 --name TestVolumeNamedCreate')

        self.cinder('delete', params='TestVolumeNamedCreate')
        self.check_volume_deleted(volume['id'])

    def test_volume_show(self):
        """Show volume details."""
        volume = self.volume_create(params='1 --name TestVolumeShow')
        output = self.cinder('show', params='TestVolumeShow')
        volume = self._get_property_from_output(output)
        self.assertEqual('TestVolumeShow', volume['name'])
        self.assert_volume_details(volume.keys())

        self.volume_delete(volume['id'])
        self.check_volume_deleted(volume['id'])

    def test_volume_extend(self):
        """Extend a volume size."""
        volume = self.volume_create(params='1 --name TestVolumeExtend')
        self.cinder('extend', params="%s %s" % (volume['id'], 2))
        self.wait_for_volume_status(volume['id'], 'available')
        output = self.cinder('show', params=volume['id'])
        volume = self._get_property_from_output(output)
        self.assertEqual('2', volume['size'])

        self.volume_delete(volume['id'])
        self.check_volume_deleted(volume['id'])

    def test_snapshot_create_and_delete(self):
        """Create a volume snapshot and then delete."""
        volume = self.volume_create(params='1')
        snapshot = self.snapshot_create(volume['id'])
        self.assert_snapshot_details(snapshot.keys())
        self.snapshot_delete(snapshot['id'])
        self.check_snapshot_deleted(snapshot['id'])
        self.volume_delete(volume['id'])
        self.check_volume_deleted(volume['id'])
