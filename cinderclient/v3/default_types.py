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


"""Default Volume Type interface."""

from cinderclient import base


class DefaultVolumeType(base.Resource):
    """Default volume types for projects."""
    def __repr__(self):
        return "<DefaultVolumeType: %s>" % self.project_id


class DefaultVolumeTypeManager(base.ManagerWithFind):
    """Manage :class:`DefaultVolumeType` resources."""
    resource_class = DefaultVolumeType

    def create(self, volume_type, project_id):
        """Creates a default volume type for a project

        :param volume_type: Name or ID of the volume type
        :param project_id: Project to set default type for
        """

        body = {
            "default_type": {
                "volume_type": volume_type
            }
        }

        return self._create_update_with_base_url(
            'v3/default-types/%s' % project_id, body,
            response_key='default_type')

    def list(self, project_id=None):
        """List the default types."""

        url = 'v3/default-types'
        response_key = "default_types"

        if project_id:
            url += '/' + project_id
            response_key = "default_type"

        return self._get_all_with_base_url(url, response_key)

    def delete(self, project_id):
        """Removes the default volume type for a project

        :param project_id: The ID of the project to unset default for.
        """

        return self._delete_with_base_url('v3/default-types/%s' % project_id)
