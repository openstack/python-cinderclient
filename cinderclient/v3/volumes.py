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

"""Volume interface (v3 extension)."""
from cinderclient.apiclient import base as common_base
from cinderclient import api_versions
from cinderclient import base
from cinderclient.v2 import volumes


class Volume(volumes.Volume):

    def upload_to_image(self, force, image_name, container_format,
                        disk_format, visibility=None,
                        protected=None):
        """Upload a volume to image service as an image.
        :param force: Boolean to enables or disables upload of a volume that
                      is attached to an instance.
        :param image_name: The new image name.
        :param container_format: Container format type.
        :param disk_format: Disk format type.
        :param visibility: The accessibility of image (allowed for
                           3.1-latest).
        :param protected: Boolean to decide whether prevents image from being
                          deleted (allowed for 3.1-latest).
        """
        if self.manager.api_version >= api_versions.APIVersion("3.1"):
            visibility = 'private' if visibility is None else visibility
            protected = False if protected is None else protected
            return self.manager.upload_to_image(self, force, image_name,
                                                container_format, disk_format,
                                                visibility, protected)
        return self.manager.upload_to_image(self, force, image_name,
                                            container_format, disk_format)

    def revert_to_snapshot(self, snapshot):
        """Revert a volume to a snapshot."""
        self.manager.revert_to_snapshot(self, snapshot)


class VolumeManager(volumes.VolumeManager):
    resource_class = Volume

    def create(self, size, consistencygroup_id=None,
               group_id=None, snapshot_id=None,
               source_volid=None, name=None, description=None,
               volume_type=None, user_id=None,
               project_id=None, availability_zone=None,
               metadata=None, imageRef=None, scheduler_hints=None,
               source_replica=None, multiattach=False):
        """Create a volume.

        :param size: Size of volume in GB
        :param consistencygroup_id: ID of the consistencygroup
        :param group_id: ID of the group
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

        if group_id:
            body['volume']['group_id'] = group_id

        if scheduler_hints:
            body['OS-SCH-HNT:scheduler_hints'] = scheduler_hints

        return self._create('/volumes', body, 'volume')

    @api_versions.wraps('3.40')
    def revert_to_snapshot(self, volume, snapshot):
        """Revert a volume to a snapshot.

        The snapshot must be the most recent one known to cinder.
        :param volume: volume object.
        :param snapshot: snapshot object.
        """
        return self._action('revert', volume,
                            info={'snapshot_id': base.getid(snapshot.id)})

    @api_versions.wraps("3.0")
    def delete_metadata(self, volume, keys):
        """Delete specified keys from volumes metadata.

        :param volume: The :class:`Volume`.
        :param keys: A list of keys to be removed.
        """
        response_list = []
        for k in keys:
            resp, body = self._delete("/volumes/%s/metadata/%s" %
                                      (base.getid(volume), k))
        response_list.append(resp)

        return common_base.ListWithMeta([], response_list)

    @api_versions.wraps("3.15")
    def delete_metadata(self, volume, keys):
        """Delete specified keys from volumes metadata.

        :param volume: The :class:`Volume`.
        :param keys: A list of keys to be removed.
        """
        # pylint: disable=function-redefined
        data = self._get("/volumes/%s/metadata" % base.getid(volume))
        metadata = data._info.get("metadata", {})
        if set(keys).issubset(metadata.keys()):
            for k in keys:
                metadata.pop(k)
            body = {'metadata': metadata}
            kwargs = {'headers': {'If-Match': data._checksum}}
            return self._update("/volumes/%s/metadata" % base.getid(volume),
                                body, **kwargs)

    @api_versions.wraps("3.0")
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

    @api_versions.wraps("3.1")
    def upload_to_image(self, volume, force, image_name, container_format,
                        disk_format, visibility, protected):
        """Upload volume to image service as image.
        :param volume: The :class:`Volume` to upload.
        """
        # pylint: disable=function-redefined
        return self._action('os-volume_upload_image',
                            volume,
                            {'force': force,
                             'image_name': image_name,
                             'container_format': container_format,
                             'disk_format': disk_format,
                             'visibility': visibility,
                             'protected': protected})

    @api_versions.wraps("3.8")
    def list_manageable(self, host, detailed=True, marker=None, limit=None,
                        offset=None, sort=None):
        url = self._build_list_url("manageable_volumes", detailed=detailed,
                                   search_opts={'host': host}, marker=marker,
                                   limit=limit, offset=offset, sort=sort)
        return self._list(url, "manageable-volumes")

    @api_versions.wraps("2.0", "3.32")
    def get_pools(self, detail):
        """Show pool information for backends."""
        query_string = ""
        if detail:
            query_string = "?detail=True"

        return self._get('/scheduler-stats/get_pools%s' % query_string, None)

    @api_versions.wraps("3.33")
    def get_pools(self, detail, search_opts):
        """Show pool information for backends."""
        # pylint: disable=function-redefined
        options = {'detail': detail}
        options.update(search_opts)
        url = self._build_list_url('scheduler-stats/get_pools', detailed=False,
                                   search_opts=options)

        return self._get(url, None)
