# Copyright (c) 2013 OpenStack Foundation
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

from cinderclient import extension
from cinderclient.v2.contrib import list_extensions

from cinderclient.tests.unit import utils
from cinderclient.tests.unit.v2 import fakes


extensions = [
    extension.Extension(list_extensions.__name__.split(".")[-1],
                        list_extensions),
]
cs = fakes.FakeClient(extensions=extensions)


class ListExtensionsTests(utils.TestCase):
    def test_list_extensions(self):
        """
        List all extensions in the extensions

        Args:
            self: (todo): write your description
        """
        all_exts = cs.list_extensions.show_all()
        cs.assert_called('GET', '/extensions')
        self.assertGreater(len(all_exts), 0)
        for r in all_exts:
            self.assertGreater(len(r.summary), 0)
