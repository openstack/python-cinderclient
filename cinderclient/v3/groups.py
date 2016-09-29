# Copyright (C) 2016 EMC Corporation.
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

"""Group interface (v3 extension)."""

from cinderclient import base
from cinderclient.apiclient import base as common_base
from cinderclient import utils


class Group(base.Resource):
    """A Group of volumes."""
    def __repr__(self):
        return "<Group: %s>" % self.id

    def delete(self, delete_volumes=False):
        """Delete this group."""
        return self.manager.delete(self, delete_volumes)

    def update(self, **kwargs):
        """Update the name or description for this group."""
        return self.manager.update(self, **kwargs)


class GroupManager(base.ManagerWithFind):
    """Manage :class:`Group` resources."""
    resource_class = Group

    def create(self, group_type, volume_types, name=None,
               description=None, user_id=None,
               project_id=None, availability_zone=None):
        """Creates a group.

        :param group_type: Type of the Group
        :param volume_types: Types of volume
        :param name: Name of the Group
        :param description: Description of the Group
        :param user_id: User id derived from context
        :param project_id: Project id derived from context
        :param availability_zone: Availability Zone to use
        :rtype: :class:`Group`
        """
        body = {'group': {'name': name,
                          'description': description,
                          'group_type': group_type,
                          'volume_types': volume_types.split(','),
                          'user_id': user_id,
                          'project_id': project_id,
                          'availability_zone': availability_zone,
                          'status': "creating",
                          }}

        return self._create('/groups', body, 'group')

    def create_from_src(self, group_snapshot_id, source_group_id,
                        name=None, description=None, user_id=None,
                        project_id=None):
        """Creates a group from a group snapshot or a source group.

        :param group_snapshot_id: UUID of a GroupSnapshot
        :param source_group_id: UUID of a source Group
        :param name: Name of the Group
        :param description: Description of the Group
        :param user_id: User id derived from context
        :param project_id: Project id derived from context
        :rtype: A dictionary containing Group metadata
        """
        body = {'create-from-src': {'name': name,
                                    'description': description,
                                    'group_snapshot_id': group_snapshot_id,
                                    'source_group_id': source_group_id,
                                    'user_id': user_id,
                                    'project_id': project_id,
                                    'status': "creating", }}

        self.run_hooks('modify_body_for_action', body,
                       'create-from-src')
        resp, body = self.api.client.post(
            "/groups/action", body=body)
        return common_base.DictWithMeta(body['group'], resp)

    def get(self, group_id):
        """Get a group.

        :param group_id: The ID of the group to get.
        :rtype: :class:`Group`
        """
        return self._get("/groups/%s" % group_id,
                         "group")

    def list(self, detailed=True, search_opts=None):
        """Lists all groups.

        :rtype: list of :class:`Group`
        """
        query_string = utils.build_query_param(search_opts)

        detail = ""
        if detailed:
            detail = "/detail"

        return self._list("/groups%s%s" % (detail, query_string),
                          "groups")

    def delete(self, group, delete_volumes=False):
        """Delete a group.

        :param group: the :class:`Group` to delete.
        :param delete_volumes: delete volumes in the group.
        """
        body = {'delete': {'delete-volumes': delete_volumes}}
        self.run_hooks('modify_body_for_action', body, 'group')
        url = '/groups/%s/action' % base.getid(group)
        resp, body = self.api.client.post(url, body=body)
        return common_base.TupleWithMeta((resp, body), resp)

    def update(self, group, **kwargs):
        """Update the name or description for a group.

        :param Group: The :class:`Group` to update.
        """
        if not kwargs:
            return

        body = {"group": kwargs}

        return self._update("/groups/%s" %
                            base.getid(group), body)

    def _action(self, action, group, info=None, **kwargs):
        """Perform a group "action."

        :param action: an action to be performed on the group
        :param group: a group to perform the action on
        :param info: details of the action
        :param **kwargs: other parameters
        """

        body = {action: info}
        self.run_hooks('modify_body_for_action', body, **kwargs)
        url = '/groups/%s/action' % base.getid(group)
        resp, body = self.api.client.post(url, body=body)
        return common_base.TupleWithMeta((resp, body), resp)
