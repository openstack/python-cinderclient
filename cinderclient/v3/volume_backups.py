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
from cinderclient.apiclient import base as common_base
from cinderclient import base


class VolumeBackup(base.Resource):
    """A volume backup is a block level backup of a volume."""

    def __repr__(self):
        return "<VolumeBackup: %s>" % self.id

    def delete(self, force=False):
        """Delete this volume backup."""
        return self.manager.delete(self, force)

    def reset_state(self, state):
        return self.manager.reset_state(self, state)

    def update(self, **kwargs):
        """Update the name or description for this backup."""
        return self.manager.update(self, **kwargs)


class VolumeBackupManager(base.ManagerWithFind):
    """Manage :class:`VolumeBackup` resources."""
    resource_class = VolumeBackup

    @api_versions.wraps("3.9")
    def update(self, backup, **kwargs):
        """Update the name or description for a backup.

        :param backup: The :class:`Backup` to update.
        """
        if not kwargs:
            return

        body = {"backup": kwargs}

        return self._update("/backups/%s" % base.getid(backup), body)

    @api_versions.wraps("3.0")
    def create(self, volume_id, container=None,
               name=None, description=None,
               incremental=False, force=False,
               snapshot_id=None):
        """Creates a volume backup.

        :param volume_id: The ID of the volume to backup.
        :param container: The name of the backup service container.
        :param name: The name of the backup.
        :param description: The description of the backup.
        :param incremental: Incremental backup.
        :param force: If True, allows an in-use volume to be backed up.
        :param snapshot_id: The ID of the snapshot to backup. This should
                            be a snapshot of the src volume, when specified,
                            the new backup will be based on the snapshot.
        :rtype: :class:`VolumeBackup`
        """
        return self._create_backup(volume_id, container, name, description,
                                   incremental, force, snapshot_id)

    @api_versions.wraps("3.43")
    def create(self, volume_id, container=None,  # noqa: F811
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
        :param snapshot_id: The ID of the snapshot to backup. This should
                            be a snapshot of the src volume, when specified,
                            the new backup will be based on the snapshot.
        :rtype: :class:`VolumeBackup`
        """
        # pylint: disable=function-redefined
        return self._create_backup(volume_id, container, name, description,
                                   incremental, force, snapshot_id, metadata)

    @api_versions.wraps("3.51")
    def create(self, volume_id, container=None, name=None,  # noqa: F811
               description=None, incremental=False, force=False,
               snapshot_id=None, metadata=None, availability_zone=None):
        return self._create_backup(volume_id, container, name, description,
                                   incremental, force, snapshot_id, metadata,
                                   availability_zone)

    def _create_backup(self, volume_id, container=None, name=None,
                       description=None, incremental=False, force=False,
                       snapshot_id=None, metadata=None,
                       availability_zone=None):
        """Creates a volume backup.

        :param volume_id: The ID of the volume to backup.
        :param container: The name of the backup service container.
        :param name: The name of the backup.
        :param description: The description of the backup.
        :param incremental: Incremental backup.
        :param force: If True, allows an in-use volume to be backed up.
        :param metadata: Key Value pairs
        :param snapshot_id: The ID of the snapshot to backup. This should
                            be a snapshot of the src volume, when specified,
                            the new backup will be based on the snapshot.
        :param availability_zone: The AZ where we want the backup stored.
        :rtype: :class:`VolumeBackup`
        """
        # pylint: disable=function-redefined
        body = {'backup': {'volume_id': volume_id,
                           'container': container,
                           'name': name,
                           'description': description,
                           'incremental': incremental,
                           'force': force,
                           'snapshot_id': snapshot_id, }}
        if metadata:
            body['backup']['metadata'] = metadata
        if availability_zone:
            body['backup']['availability_zone'] = availability_zone
        return self._create('/backups', body, 'backup')

    def get(self, backup_id):
        """Show volume backup details.

        :param backup_id: The ID of the backup to display.
        :rtype: :class:`VolumeBackup`
        """
        return self._get("/backups/%s" % backup_id, "backup")

    def list(self, detailed=True, search_opts=None, marker=None, limit=None,
             sort=None):
        """Get a list of all volume backups.

        :rtype: list of :class:`VolumeBackup`
        """
        resource_type = "backups"
        url = self._build_list_url(resource_type, detailed=detailed,
                                   search_opts=search_opts, marker=marker,
                                   limit=limit, sort=sort)
        return self._list(url, resource_type, limit=limit)

    def delete(self, backup, force=False):
        """Delete a volume backup.

        :param backup: The :class:`VolumeBackup` to delete.
        :param force: Allow delete in state other than error or available.
        """
        if force:
            return self._action('os-force_delete', backup)
        else:
            return self._delete("/backups/%s" % base.getid(backup))

    def reset_state(self, backup, state):
        """Update the specified volume backup with the provided state."""
        return self._action('os-reset_status', backup,
                            {'status': state} if state else {})

    def _action(self, action, backup, info=None, **kwargs):
        """Perform a volume backup action."""
        body = {action: info}
        self.run_hooks('modify_body_for_action', body, **kwargs)
        url = '/backups/%s/action' % base.getid(backup)
        resp, body = self.api.client.post(url, body=body)
        return common_base.TupleWithMeta((resp, body), resp)

    def export_record(self, backup_id):
        """Export volume backup metadata record.

        :param backup_id: The ID of the backup to export.
        :rtype: A dictionary containing 'backup_url' and 'backup_service'.
        """
        resp, body = \
            self.api.client.get("/backups/%s/export_record" % backup_id)
        return common_base.DictWithMeta(body['backup-record'], resp)

    def import_record(self, backup_service, backup_url):
        """Import volume backup metadata record.

        :param backup_service: Backup service to use for importing the backup
        :param backup_url: Backup URL for importing the backup metadata
        :rtype: A dictionary containing volume backup metadata.
        """
        body = {'backup-record': {'backup_service': backup_service,
                                  'backup_url': backup_url}}
        self.run_hooks('modify_body_for_update', body, 'backup-record')
        resp, body = self.api.client.post("/backups/import_record", body=body)
        return common_base.DictWithMeta(body['backup'], resp)
