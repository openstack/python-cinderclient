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

"""Volume interface (v2 extension)."""

import six
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from cinderclient import base


# Valid sort directions and client sort keys
SORT_DIR_VALUES = ('asc', 'desc')
SORT_KEY_VALUES = ('id', 'status', 'size', 'availability_zone', 'name',
                   'bootable', 'created_at')
# Mapping of client keys to actual sort keys
SORT_KEY_MAPPINGS = {'name': 'display_name'}


class Volume(base.Resource):
    """A volume is an extra block level storage to the OpenStack instances."""
    def __repr__(self):
        return "<Volume: %s>" % self.id

    def delete(self):
        """Delete this volume."""
        self.manager.delete(self)

    def update(self, **kwargs):
        """Update the name or description for this volume."""
        self.manager.update(self, **kwargs)

    def attach(self, instance_uuid, mountpoint, mode='rw', host_name=None):
        """Set attachment metadata.

        :param instance_uuid: uuid of the attaching instance.
        :param mountpoint: mountpoint on the attaching instance or host.
        :param mode: the access mode.
        :param host_name: name of the attaching host.
        """
        return self.manager.attach(self, instance_uuid, mountpoint, mode,
                                   host_name)

    def detach(self):
        """Clear attachment metadata."""
        return self.manager.detach(self)

    def reserve(self, volume):
        """Reserve this volume."""
        return self.manager.reserve(self)

    def unreserve(self, volume):
        """Unreserve this volume."""
        return self.manager.unreserve(self)

    def begin_detaching(self, volume):
        """Begin detaching volume."""
        return self.manager.begin_detaching(self)

    def roll_detaching(self, volume):
        """Roll detaching volume."""
        return self.manager.roll_detaching(self)

    def initialize_connection(self, volume, connector):
        """Initialize a volume connection.

        :param connector: connector dict from nova.
        """
        return self.manager.initialize_connection(self, connector)

    def terminate_connection(self, volume, connector):
        """Terminate a volume connection.

        :param connector: connector dict from nova.
        """
        return self.manager.terminate_connection(self, connector)

    def set_metadata(self, volume, metadata):
        """Set or Append metadata to a volume.

        :param volume : The :class: `Volume` to set metadata on
        :param metadata: A dict of key/value pairs to set
        """
        return self.manager.set_metadata(self, metadata)

    def upload_to_image(self, force, image_name, container_format,
                        disk_format):
        """Upload a volume to image service as an image."""
        return self.manager.upload_to_image(self, force, image_name,
                                            container_format, disk_format)

    def force_delete(self):
        """Delete the specified volume ignoring its current state.

        :param volume: The UUID of the volume to force-delete.
        """
        self.manager.force_delete(self)

    def reset_state(self, state):
        """Update the volume with the provided state."""
        self.manager.reset_state(self, state)

    def extend(self, volume, new_size):
        """Extend the size of the specified volume.

        :param volume: The UUID of the volume to extend
        :param new_size: The desired size to extend volume to.
        """
        self.manager.extend(self, new_size)

    def migrate_volume(self, host, force_host_copy):
        """Migrate the volume to a new host."""
        self.manager.migrate_volume(self, host, force_host_copy)

    def retype(self, volume_type, policy):
        """Change a volume's type."""
        self.manager.retype(self, volume_type, policy)

    def update_all_metadata(self, metadata):
        """Update all metadata of this volume."""
        return self.manager.update_all_metadata(self, metadata)

    def update_readonly_flag(self, volume, read_only):
        """Update the read-only access mode flag of the specified volume.

        :param volume: The UUID of the volume to update.
        :param read_only: The value to indicate whether to update volume to
            read-only access mode.
        """
        self.manager.update_readonly_flag(self, read_only)

    def manage(self, host, ref, name=None, description=None,
               volume_type=None, availability_zone=None, metadata=None,
               bootable=False):
        """Manage an existing volume."""
        self.manager.manage(host=host, ref=ref, name=name,
                            description=description, volume_type=volume_type,
                            availability_zone=availability_zone,
                            metadata=metadata, bootable=bootable)

    def unmanage(self, volume):
        """Unmanage a volume."""
        self.manager.unmanage(volume)

    def promote(self, volume):
        """Promote secondary to be primary in relationship."""
        self.manager.promote(volume)

    def reenable(self, volume):
        """Sync the secondary volume with primary for a relationship."""
        self.manager.reenable(volume)

    def get_pools(self, detail):
        """Show pool information for backends."""
        self.manager.get_pools(detail)


class VolumeManager(base.ManagerWithFind):
    """Manage :class:`Volume` resources."""
    resource_class = Volume

    def create(self, size, consistencygroup_id=None, snapshot_id=None,
               source_volid=None, name=None, description=None,
               volume_type=None, user_id=None,
               project_id=None, availability_zone=None,
               metadata=None, imageRef=None, scheduler_hints=None,
               source_replica=None, multiattach=False):
        """Create a volume.

        :param size: Size of volume in GB
        :param consistencygroup_id: ID of the consistencygroup
        :param snapshot_id: ID of the snapshot
        :param name: Name of the volume
        :param description: Description of the volume
        :param volume_type: Type of volume
        :param user_id: User id derived from context
        :param project_id: Project id derived from context
        :param availability_zone: Availability Zone to use
        :param metadata: Optional metadata to set on volume creation
        :param imageRef: reference to an image stored in glance
        :param source_volid: ID of source volume to clone from
        :param source_replica: ID of source volume to clone replica
        :param scheduler_hints: (optional extension) arbitrary key-value pairs
                            specified by the client to help boot an instance
        :param multiattach: Allow the volume to be attached to more than
                            one instance
        :rtype: :class:`Volume`
        """
        if metadata is None:
            volume_metadata = {}
        else:
            volume_metadata = metadata

        body = {'volume': {'size': size,
                           'consistencygroup_id': consistencygroup_id,
                           'snapshot_id': snapshot_id,
                           'name': name,
                           'description': description,
                           'volume_type': volume_type,
                           'user_id': user_id,
                           'project_id': project_id,
                           'availability_zone': availability_zone,
                           'status': "creating",
                           'attach_status': "detached",
                           'metadata': volume_metadata,
                           'imageRef': imageRef,
                           'source_volid': source_volid,
                           'source_replica': source_replica,
                           'multiattach': multiattach,
                           }}

        if scheduler_hints:
            body['OS-SCH-HNT:scheduler_hints'] = scheduler_hints

        return self._create('/volumes', body, 'volume')

    def get(self, volume_id):
        """Get a volume.

        :param volume_id: The ID of the volume to get.
        :rtype: :class:`Volume`
        """
        return self._get("/volumes/%s" % volume_id, "volume")

    def _format_sort_param(self, sort):
        '''Formats the sort information into the sort query string parameter.

        The input sort information can be any of the following:
        - Comma-separated string in the form of <key[:dir]>
        - List of strings in the form of <key[:dir]>
        - List of either string keys, or tuples of (key, dir)

        For example, the following import sort values are valid:
        - 'key1:dir1,key2,key3:dir3'
        - ['key1:dir1', 'key2', 'key3:dir3']
        - [('key1', 'dir1'), 'key2', ('key3', dir3')]

        :param sort: Input sort information
        :returns: Formatted query string parameter or None
        :raise ValueError: If an invalid sort direction or invalid sort key is
                           given
        '''
        if not sort:
            return None

        if isinstance(sort, six.string_types):
            # Convert the string into a list for consistent validation
            sort = [s for s in sort.split(',') if s]

        sort_array = []
        for sort_item in sort:
            if isinstance(sort_item, tuple):
                sort_key = sort_item[0]
                sort_dir = sort_item[1]
            else:
                sort_key, _sep, sort_dir = sort_item.partition(':')
            sort_key = sort_key.strip()
            if sort_key in SORT_KEY_VALUES:
                sort_key = SORT_KEY_MAPPINGS.get(sort_key, sort_key)
            else:
                raise ValueError('sort_key must be one of the following: %s.'
                                 % ', '.join(SORT_KEY_VALUES))
            if sort_dir:
                sort_dir = sort_dir.strip()
                if sort_dir not in SORT_DIR_VALUES:
                    msg = ('sort_dir must be one of the following: %s.'
                           % ', '.join(SORT_DIR_VALUES))
                    raise ValueError(msg)
                sort_array.append('%s:%s' % (sort_key, sort_dir))
            else:
                sort_array.append(sort_key)
        return ','.join(sort_array)

    def list(self, detailed=True, search_opts=None, marker=None, limit=None,
             sort_key=None, sort_dir=None, sort=None):
        """Lists all volumes.

        :param detailed: Whether to return detailed volume info.
        :param search_opts: Search options to filter out volumes.
        :param marker: Begin returning volumes that appear later in the volume
                       list than that represented by this volume id.
        :param limit: Maximum number of volumes to return.
        :param sort_key: Key to be sorted; deprecated in kilo
        :param sort_dir: Sort direction, should be 'desc' or 'asc'; deprecated
                         in kilo
        :param sort: Sort information
        :rtype: list of :class:`Volume`
        """
        if search_opts is None:
            search_opts = {}

        qparams = {}

        for opt, val in six.iteritems(search_opts):
            if val:
                qparams[opt] = val

        if marker:
            qparams['marker'] = marker

        if limit:
            qparams['limit'] = limit

        # sort_key and sort_dir deprecated in kilo, prefer sort
        if sort:
            qparams['sort'] = self._format_sort_param(sort)
        else:
            if sort_key is not None:
                if sort_key in SORT_KEY_VALUES:
                    qparams['sort_key'] = SORT_KEY_MAPPINGS.get(sort_key,
                                                                sort_key)
                else:
                    msg = ('sort_key must be one of the following: %s.'
                           % ', '.join(SORT_KEY_VALUES))
                    raise ValueError(msg)
            if sort_dir is not None:
                if sort_dir in SORT_DIR_VALUES:
                    qparams['sort_dir'] = sort_dir
                else:
                    msg = ('sort_dir must be one of the following: %s.'
                           % ', '.join(SORT_DIR_VALUES))
                    raise ValueError(msg)

        # Transform the dict to a sequence of two-element tuples in fixed
        # order, then the encoded string will be consistent in Python 2&3.
        if qparams:
            new_qparams = sorted(qparams.items(), key=lambda x: x[0])
            query_string = "?%s" % urlencode(new_qparams)
        else:
            query_string = ""

        detail = ""
        if detailed:
            detail = "/detail"

        return self._list("/volumes%s%s" % (detail, query_string),
                          "volumes", limit=limit)

    def delete(self, volume):
        """Delete a volume.

        :param volume: The :class:`Volume` to delete.
        """
        self._delete("/volumes/%s" % base.getid(volume))

    def update(self, volume, **kwargs):
        """Update the name or description for a volume.

        :param volume: The :class:`Volume` to update.
        """
        if not kwargs:
            return

        body = {"volume": kwargs}

        self._update("/volumes/%s" % base.getid(volume), body)

    def _action(self, action, volume, info=None, **kwargs):
        """Perform a volume "action."
        """
        body = {action: info}
        self.run_hooks('modify_body_for_action', body, **kwargs)
        url = '/volumes/%s/action' % base.getid(volume)
        return self.api.client.post(url, body=body)

    def attach(self, volume, instance_uuid, mountpoint, mode='rw',
               host_name=None):
        """Set attachment metadata.

        :param volume: The :class:`Volume` (or its ID)
                       you would like to attach.
        :param instance_uuid: uuid of the attaching instance.
        :param mountpoint: mountpoint on the attaching instance or host.
        :param mode: the access mode.
        :param host_name: name of the attaching host.
        """
        body = {'mountpoint': mountpoint, 'mode': mode}
        if instance_uuid is not None:
            body.update({'instance_uuid': instance_uuid})
        if host_name is not None:
            body.update({'host_name': host_name})
        return self._action('os-attach', volume, body)

    def detach(self, volume, attachment_uuid=None):
        """Clear attachment metadata.

        :param volume: The :class:`Volume` (or its ID)
                       you would like to detach.
        :param attachment_uuid: The uuid of the volume attachment.
        """
        return self._action('os-detach', volume,
                            {'attachment_id': attachment_uuid})

    def reserve(self, volume):
        """Reserve this volume.

        :param volume: The :class:`Volume` (or its ID)
                       you would like to reserve.
        """
        return self._action('os-reserve', volume)

    def unreserve(self, volume):
        """Unreserve this volume.

        :param volume: The :class:`Volume` (or its ID)
                       you would like to unreserve.
        """
        return self._action('os-unreserve', volume)

    def begin_detaching(self, volume):
        """Begin detaching this volume.

        :param volume: The :class:`Volume` (or its ID)
                       you would like to detach.
        """
        return self._action('os-begin_detaching', volume)

    def roll_detaching(self, volume):
        """Roll detaching this volume.

        :param volume: The :class:`Volume` (or its ID)
                       you would like to roll detaching.
        """
        return self._action('os-roll_detaching', volume)

    def initialize_connection(self, volume, connector):
        """Initialize a volume connection.

        :param volume: The :class:`Volume` (or its ID).
        :param connector: connector dict from nova.
        """
        return self._action('os-initialize_connection', volume,
                            {'connector': connector})[1]['connection_info']

    def terminate_connection(self, volume, connector):
        """Terminate a volume connection.

        :param volume: The :class:`Volume` (or its ID).
        :param connector: connector dict from nova.
        """
        self._action('os-terminate_connection', volume,
                     {'connector': connector})

    def set_metadata(self, volume, metadata):
        """Update/Set a volumes metadata.

        :param volume: The :class:`Volume`.
        :param metadata: A list of keys to be set.
        """
        body = {'metadata': metadata}
        return self._create("/volumes/%s/metadata" % base.getid(volume),
                            body, "metadata")

    def delete_metadata(self, volume, keys):
        """Delete specified keys from volumes metadata.

        :param volume: The :class:`Volume`.
        :param keys: A list of keys to be removed.
        """
        for k in keys:
            self._delete("/volumes/%s/metadata/%s" % (base.getid(volume), k))

    def upload_to_image(self, volume, force, image_name, container_format,
                        disk_format):
        """Upload volume to image service as image.

        :param volume: The :class:`Volume` to upload.
        """
        return self._action('os-volume_upload_image',
                            volume,
                            {'force': force,
                            'image_name': image_name,
                            'container_format': container_format,
                            'disk_format': disk_format})

    def force_delete(self, volume):
        """Delete the specified volume ignoring its current state.

        :param volume: The :class:`Volume` to force-delete.
        """
        return self._action('os-force_delete', base.getid(volume))

    def reset_state(self, volume, state):
        """Update the provided volume with the provided state."""
        return self._action('os-reset_status', volume, {'status': state})

    def extend(self, volume, new_size):
        """Extend the size of the specified volume.

        :param volume: The UUID of the volume to extend.
        :param new_size: The requested size to extend volume to.
        """
        return self._action('os-extend',
                            base.getid(volume),
                            {'new_size': new_size})

    def get_encryption_metadata(self, volume_id):
        """
        Retrieve the encryption metadata from the desired volume.

        :param volume_id: the id of the volume to query
        :return: a dictionary of volume encryption metadata
        """
        return self._get("/volumes/%s/encryption" % volume_id)._info

    def migrate_volume(self, volume, host, force_host_copy):
        """Migrate volume to new host.

        :param volume: The :class:`Volume` to migrate
        :param host: The destination host
        :param force_host_copy: Skip driver optimizations
        """
        return self._action('os-migrate_volume',
                            volume,
                            {'host': host, 'force_host_copy': force_host_copy})

    def migrate_volume_completion(self, old_volume, new_volume, error):
        """Complete the migration from the old volume to the temp new one.

        :param old_volume: The original :class:`Volume` in the migration
        :param new_volume: The new temporary :class:`Volume` in the migration
        :param error: Inform of an error to cause migration cleanup
        """
        new_volume_id = base.getid(new_volume)
        return self._action('os-migrate_volume_completion',
                            old_volume,
                            {'new_volume': new_volume_id, 'error': error})[1]

    def update_all_metadata(self, volume, metadata):
        """Update all metadata of a volume.

        :param volume: The :class:`Volume`.
        :param metadata: A list of keys to be updated.
        """
        body = {'metadata': metadata}
        return self._update("/volumes/%s/metadata" % base.getid(volume),
                            body)

    def update_readonly_flag(self, volume, flag):
        return self._action('os-update_readonly_flag',
                            base.getid(volume),
                            {'readonly': flag})

    def retype(self, volume, volume_type, policy):
        """Change a volume's type.

        :param volume: The :class:`Volume` to retype
        :param volume_type: New volume type
        :param policy: Policy for migration during the retype
        """
        return self._action('os-retype',
                            volume,
                            {'new_type': volume_type,
                             'migration_policy': policy})

    def set_bootable(self, volume, flag):
        return self._action('os-set_bootable',
                            base.getid(volume),
                            {'bootable': flag})

    def manage(self, host, ref, name=None, description=None,
               volume_type=None, availability_zone=None, metadata=None,
               bootable=False):
        """Manage an existing volume."""
        body = {'volume': {'host': host,
                           'ref': ref,
                           'name': name,
                           'description': description,
                           'volume_type': volume_type,
                           'availability_zone': availability_zone,
                           'metadata': metadata,
                           'bootable': bootable
                           }}
        return self._create('/os-volume-manage', body, 'volume')

    def unmanage(self, volume):
        """Unmanage a volume."""
        return self._action('os-unmanage', volume, None)

    def promote(self, volume):
        """Promote secondary to be primary in relationship."""
        return self._action('os-promote-replica', volume, None)

    def reenable(self, volume):
        """Sync the secondary volume with primary for a relationship."""
        return self._action('os-reenable-replica', volume, None)

    def get_pools(self, detail):
        """Show pool information for backends."""
        query_string = ""
        if detail:
            query_string = "?detail=True"

        return self._get('/scheduler-stats/get_pools%s' % query_string, None)
