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

from cinderclient.v2 import volume_transfers


class VolumeTransferManager(volume_transfers.VolumeTransferManager):
    def create(self, volume_id, name=None, no_snapshots=False):
        """Creates a volume transfer.

        :param volume_id: The ID of the volume to transfer.
        :param name: The name of the transfer.
        :param no_snapshots: Transfer volumes without snapshots.
        :rtype: :class:`VolumeTransfer`
        """
        body = {'transfer': {'volume_id': volume_id,
                             'name': name}}
        if self.api_version.matches('3.55'):
            body['transfer']['no_snapshots'] = no_snapshots
        return self._create('/volume-transfers', body, 'transfer')
