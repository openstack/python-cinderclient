# Copyright (c) 2021 Red Hat, Inc
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

import importlib
import inspect

from cinderclient.tests.unit import utils
import cinderclient.v2 as cv2
import cinderclient.v3 as cv3


class v2_CompatibilityTest(utils.TestCase):

    def test_all_v2_classes_are_v3_classes(self):
        CV2 = 'cinderclient.v2'
        CV3 = 'cinderclient.v3'

        v2_class_names = []
        for mod_name, mod_data in inspect.getmembers(cv2, inspect.ismodule):
            mod = importlib.import_module(CV2 + '.' + mod_name)
            v2_class_names.extend([cls_name for cls_name, cls_data
                                   in inspect.getmembers(mod,
                                                         inspect.isclass)])

        v3_class_names = []
        for mod_name, mod_data in inspect.getmembers(cv3, inspect.ismodule):
            mod = importlib.import_module(CV3 + '.' + mod_name)
            v3_class_names.extend([cls_name for cls_name, cls_data
                                   in inspect.getmembers(mod,
                                                         inspect.isclass)])

        for cls_name in v2_class_names:
            self.assertIn(cls_name, v3_class_names)
