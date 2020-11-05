# Copyright (c) 2017 OpenStack Foundation
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

from cinderclient.tests.unit import utils
from cinderclient.tests.unit.v3 import fakes


cs = fakes.FakeClient()


class QuotaSetsTest(utils.TestCase):

    def test_update_quota_with_skip_(self):
        """
        Updates the quota for the quota.

        Args:
            self: (todo): write your description
        """
        q = cs.quotas.get('test')
        q.update(skip_validation=False)
        cs.assert_called('PUT', '/os-quota-sets/test?skip_validation=False')
        self._assert_request_id(q)
