# Copyright 2016 FUJITSU LIMITED
#
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

from cinderclient import api_versions
from cinderclient.tests.unit import utils
from cinderclient.tests.unit.v3 import fakes
from cinderclient.v3.volumes import Volume
from cinderclient.v3.volumes import VolumeManager


class VolumesTest(utils.TestCase):

    def test_volume_manager_upload_to_image(self):
        expected = {'os-volume_upload_image':
                    {'force': False,
                     'container_format': 'bare',
                     'disk_format': 'raw',
                     'image_name': 'name',
                     'visibility': 'public',
                     'protected': True}}
        api_version = api_versions.APIVersion('3.1')
        cs = fakes.FakeClient(api_version)
        manager = VolumeManager(cs)
        fake_volume = Volume(manager, {'id': 1234,
                                       'name': 'sample-volume'},
                             loaded=True)
        fake_volume.upload_to_image(False, 'name', 'bare', 'raw',
                                    visibility='public', protected=True)
        cs.assert_called_anytime('POST', '/volumes/1234/action', body=expected)
