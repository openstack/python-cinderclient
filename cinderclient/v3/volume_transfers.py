# Copyright (C) 2013 Hewlett-Packard Development Company, L.P.
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

"""
Volume transfer interface (v3 extension).
"""

from cinderclient import api_versions
from cinderclient import base
from cinderclient import utils
from cinderclient.v2 import volume_transfers


VolumeTransfer = volume_transfers.VolumeTransfer


class VolumeTransferManager(volume_transfers.VolumeTransferManager):
    @api_versions.wraps("3.55")
    def create(self, volume_id, name=None, no_snapshots=False):
        """Creates a volume transfer.

        :param volume_id: The ID of the volume to transfer.
        :param name: The name of the transfer.
        :param no_snapshots: Transfer volumes without snapshots.
        :rtype: :class:`VolumeTransfer`
        """
        body = {'transfer': {'volume_id': volume_id,
                             'name': name,
                             'no_snapshots': no_snapshots}}
        return self._create('/volume-transfers', body, 'transfer')

    @api_versions.wraps("3.55")
    def accept(self, transfer_id, auth_key):
        """Accept a volume transfer.

        :param transfer_id: The ID of the transfer to accept.
        :param auth_key: The auth_key of the transfer.
        :rtype: :class:`VolumeTransfer`
        """
        body = {'accept': {'auth_key': auth_key}}
        return self._create('/volume-transfers/%s/accept' % transfer_id,
                            body, 'transfer')

    @api_versions.wraps("3.55")
    def get(self, transfer_id):
        """Show details of a volume transfer.

        :param transfer_id: The ID of the volume transfer to display.
        :rtype: :class:`VolumeTransfer`
        """
        return self._get("/volume-transfers/%s" % transfer_id, "transfer")

    @api_versions.wraps("3.55")
    def list(self, detailed=True, search_opts=None):
        """Get a list of all volume transfer.

        :rtype: list of :class:`VolumeTransfer`
        """
        query_string = utils.build_query_param(search_opts)

        detail = ""
        if detailed:
            detail = "/detail"

        return self._list("/volume-transfers%s%s" % (detail, query_string),
                          "transfers")

    @api_versions.wraps("3.55")
    def delete(self, transfer_id):
        """Delete a volume transfer.

        :param transfer_id: The :class:`VolumeTransfer` to delete.
        """
        return self._delete("/volume-transfers/%s" % base.getid(transfer_id))
