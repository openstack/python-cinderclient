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

defaults = fakes.FakeClient(api_versions.APIVersion('3.62'))


class VolumeTypeDefaultTest(utils.TestCase):

    def test_set(self):
        defaults.default_types.create('4c298f16-e339-4c80-b934-6cbfcb7525a0',
                                      '629632e7-99d2-4c40-9ae3-106fa3b1c9b7')
        defaults.assert_called(
            'PUT', 'v3/default-types/629632e7-99d2-4c40-9ae3-106fa3b1c9b7',
            body={'default_type':
                  {'volume_type': '4c298f16-e339-4c80-b934-6cbfcb7525a0'}}
        )

    def test_get(self):
        defaults.default_types.list('629632e7-99d2-4c40-9ae3-106fa3b1c9b7')
        defaults.assert_called(
            'GET', 'v3/default-types/629632e7-99d2-4c40-9ae3-106fa3b1c9b7')

    def test_get_all(self):
        defaults.default_types.list()
        defaults.assert_called(
            'GET', 'v3/default-types')

    def test_unset(self):
        defaults.default_types.delete('629632e7-99d2-4c40-9ae3-106fa3b1c9b7')
        defaults.assert_called(
            'DELETE', 'v3/default-types/629632e7-99d2-4c40-9ae3-106fa3b1c9b7')
