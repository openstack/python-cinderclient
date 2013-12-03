# Copyright 2011 OpenStack Foundation
#
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

from cinderclient.tests import utils
from cinderclient.v1 import limits


class TestRateLimit(utils.TestCase):
    def test_repr(self):
        l1 = limits.RateLimit("verb1", "uri1", "regex1", "value1", "remain1",
                              "unit1", "next1")
        self.assertEqual("<RateLimit: method=verb1 uri=uri1>", repr(l1))
