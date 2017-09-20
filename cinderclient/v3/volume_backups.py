# Copyright (C) 2013 Hewlett-Packard Development Company, L.P.
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

"""
Volume Backups interface (v3 extension).
"""

from cinderclient import api_versions
from cinderclient import base
from cinderclient.v2 import volume_backups


VolumeBackup = volume_backups.VolumeBackup


class VolumeBackupManager(volume_backups.VolumeBackupManager):
    @api_versions.wraps("3.9", "3.43")
    def update(self, backup, **kwargs):
        """Update the name or description for a backup.

        :param backup: The :class:`Backup` to update.
        """
        # NOTE(jdg): Placing 3.43 in versions.wraps above for clarity,
        # but it's irrelevant as this just uses the kwargs, should we
        # remove that?
        if not kwargs:
            return

        body = {"backup": kwargs}

        return self._update("/backups/%s" % base.getid(backup), body)

    @api_versions.wraps("3.43")
    def create(self, volume_id, container=None,
               name=None, description=None,
               incremental=False, force=False,
               snapshot_id=None,
               metadata=None):
        """Creates a volume backup.

        :param volume_id: The ID of the volume to backup.
        :param container: The name of the backup service container.
        :param name: The name of the backup.
        :param description: The description of the backup.
        :param incremental: Incremental backup.
        :param force: If True, allows an in-use volume to be backed up.
        :param metadata: Key Value pairs
        :rtype: :class:`VolumeBackup`
        """
        body = {'backup': {'volume_id': volume_id,
                           'container': container,
                           'name': name,
                           'description': description,
                           'incremental': incremental,
                           'force': force,
                           'snapshot_id': snapshot_id,
                           'metadata': metadata, }}
        return self._create('/backups', body, 'backup')
