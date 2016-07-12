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

import six
import ddt

from tempest.lib import exceptions

from cinderclient.tests.functional import base


@ddt.ddt
class CinderVolumeNegativeTests(base.ClientTestBase):
    """Check of cinder volume create commands."""

    @ddt.data(
        ('', (r'Size is a required parameter')),
        ('-1', (r'Invalid volume size provided for create request')),
        ('0', (r'Invalid input received')),
        ('size', (r'invalid int value')),
        ('0.2', (r'invalid int value')),
        ('2 GB', (r'unrecognized arguments')),
        ('999999999', (r'VolumeSizeExceedsAvailableQuota')),
    )
    @ddt.unpack
    def test_volume_create_with_incorrect_size(self, value, ex_text):

        six.assertRaisesRegex(self, exceptions.CommandFailed, ex_text,
                              self.object_create, 'volume', params=value)
