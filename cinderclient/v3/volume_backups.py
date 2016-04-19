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
from cinderclient import base
from cinderclient.openstack.common.apiclient import base as common_base


class VolumeBackup(base.Resource):
    """A volume backup is a block level backup of a volume."""

    def __repr__(self):
        return "<VolumeBackup: %s>" % self.id

    def delete(self):
        """Delete this volume backup."""
        return self.manager.delete(self)

    def reset_state(self, state):
        return self.manager.reset_state(self, state)


class VolumeBackupManager(base.ManagerWithFind):
    """Manage :class:`VolumeBackup` resources."""
    resource_class = VolumeBackup

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
        :rtype: :class:`VolumeBackup`
        """
        body = {'backup': {'volume_id': volume_id,
                           'container': container,
                           'name': name,
                           'description': description,
                           'incremental': incremental,
                           'force': force,
                           'snapshot_id': snapshot_id, }}
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

    def delete(self, backup):
        """Delete a volume backup.

        :param backup: The :class:`VolumeBackup` to delete.
        """
        return self._delete("/backups/%s" % base.getid(backup))

    def reset_state(self, backup, state):
        """Update the specified volume backup with the provided state."""
        return self._action('os-reset_status', backup, {'status': state})

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
