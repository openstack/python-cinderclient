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

from cinderclient import api_versions
from cinderclient.v3 import volumes


class Volume(volumes.Volume):
    def upload_to_image(self, force, image_name, container_format,
                        disk_format):
        """Upload a volume to image service as an image."""
        return self.manager.upload_to_image(self, force, image_name,
                                            container_format, disk_format)


class VolumeManager(volumes.VolumeManager):
    resource_class = Volume

    @api_versions.wraps("2.0")
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
