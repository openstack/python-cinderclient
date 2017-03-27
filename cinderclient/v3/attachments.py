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

"""Attachment interface."""

from cinderclient import base


class VolumeAttachment(base.Resource):
    """An attachment is a connected volume."""
    def __repr__(self):
        """Obj to Str method."""
        return "<Attachment: %s>" % self.id


class VolumeAttachmentManager(base.ManagerWithFind):
    resource_class = VolumeAttachment

    def create(self, volume_id, connector, instance_id):
        """Create a attachment for specified volume."""
        body = {'attachment': {'volume_uuid': volume_id,
                               'instance_uuid': instance_id,
                               'connector': connector}}
        retval = self._create('/attachments', body, 'attachment')
        return retval.to_dict()

    def delete(self, attachment):
        """Delete an attachment by ID."""
        return self._delete("/attachments/%s" % base.getid(attachment))

    def list(self, detailed=False, search_opts=None, marker=None, limit=None,
             sort_key=None, sort_dir=None, sort=None):
        """List all attachments."""
        resource_type = "attachments"
        url = self._build_list_url(resource_type,
                                   detailed=detailed,
                                   search_opts=search_opts,
                                   marker=marker,
                                   limit=limit,
                                   sort_key=sort_key,
                                   sort_dir=sort_dir, sort=sort)
        return self._list(url, resource_type, limit=limit)

    def show(self, id):
        """Attachment show.

        :param id: Attachment ID.
        """
        url = '/attachments/%s' % id
        resp, body = self.api.client.get(url)
        return self.resource_class(self, body['attachment'], loaded=True,
                                   resp=resp)

    def update(self, id, connector):
        """Attachment update."""
        body = {'attachment': {'connector': connector}}
        resp = self._update('/attachments/%s' % id, body)
        return self.resource_class(self, resp['attachment'], loaded=True,
                                   resp=resp)
