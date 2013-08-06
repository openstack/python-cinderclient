# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import cinderclient.client
import cinderclient.v1.client
import cinderclient.v2.client
from cinderclient.tests import utils


class ClientTest(utils.TestCase):

    def test_get_client_class_v1(self):
        output = cinderclient.client.get_client_class('1')
        self.assertEqual(output, cinderclient.v1.client.Client)

    def test_get_client_class_v2(self):
        output = cinderclient.client.get_client_class('2')
        self.assertEqual(output, cinderclient.v2.client.Client)

    def test_get_client_class_unknown(self):
        self.assertRaises(cinderclient.exceptions.UnsupportedVersion,
                          cinderclient.client.get_client_class, '0')
