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

from cinderclient import base


class QuotaClassSet(base.Resource):

    @property
    def id(self):
        """Needed by base.Resource to self-refresh and be indexed."""
        return self.class_name

    def update(self, *args, **kwargs):
        """
        Updates this instance.

        Args:
            self: (todo): write your description
        """
        return self.manager.update(self.class_name, *args, **kwargs)


class QuotaClassSetManager(base.Manager):
    resource_class = QuotaClassSet

    def get(self, class_name):
        """
        Returns a specific class by name.

        Args:
            self: (todo): write your description
            class_name: (str): write your description
        """
        return self._get("/os-quota-class-sets/%s" % (class_name),
                         "quota_class_set")

    def update(self, class_name, **updates):
        """
        Updates an update class.

        Args:
            self: (todo): write your description
            class_name: (str): write your description
            updates: (dict): write your description
        """
        quota_class_set = {}

        for update in updates:
            quota_class_set[update] = updates[update]

        result = self._update('/os-quota-class-sets/%s' % (class_name),
                              {'quota_class_set': quota_class_set})
        return self.resource_class(self,
                                   result['quota_class_set'], loaded=True,
                                   resp=result.request_ids)
