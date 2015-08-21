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

import os
import time

import six
from tempest_lib.cli import base
from tempest_lib.cli import output_parser
from tempest_lib import exceptions

_CREDS_FILE = 'functional_creds.conf'


def credentials():
    """Retrieves credentials to run functional tests

    Credentials are either read from the environment or from a config file
    ('functional_creds.conf'). Environment variables override those from the
    config file.

    The 'functional_creds.conf' file is the clean and new way to use (by
    default tox 2.0 does not pass environment variables).
    """

    username = os.environ.get('OS_USERNAME')
    password = os.environ.get('OS_PASSWORD')
    tenant_name = os.environ.get('OS_TENANT_NAME')
    auth_url = os.environ.get('OS_AUTH_URL')

    config = six.moves.configparser.RawConfigParser()
    if config.read(_CREDS_FILE):
        username = username or config.get('admin', 'user')
        password = password or config.get('admin', 'pass')
        tenant_name = tenant_name or config.get('admin', 'tenant')
        auth_url = auth_url or config.get('auth', 'uri')

    return {
        'username': username,
        'password': password,
        'tenant_name': tenant_name,
        'uri': auth_url
    }


class ClientTestBase(base.ClientTestBase):
    """Cinder base class, issues calls to cinderclient.

    """
    def setUp(self):
        super(ClientTestBase, self).setUp()
        self.clients = self._get_clients()
        self.parser = output_parser

    def _get_clients(self):
        cli_dir = os.environ.get(
            'OS_CINDERCLIENT_EXEC_DIR',
            os.path.join(os.path.abspath('.'), '.tox/functional/bin'))

        return base.CLIClient(cli_dir=cli_dir, **credentials())

    def cinder(self, *args, **kwargs):
        return self.clients.cinder(*args,
                                   **kwargs)

    def assertTableHeaders(self, output_lines, field_names):
        """Verify that output table has headers item listed in field_names.

        :param output_lines: output table from cmd
        :param field_names: field names from the output table of the cmd
        """
        table = self.parser.table(output_lines)
        headers = table['headers']
        for field in field_names:
            self.assertIn(field, headers)

    def assertTableStruct(self, items, field_names):
        """Verify that all items has keys listed in field_names.

        :param items: items to assert are field names in the output table
        :type items: list
        :param field_names: field names from the output table of the cmd
        :type field_names: list
        """
        # Strip off the --- if present

        for item in items:
            for field in field_names:
                self.assertIn(field, item)

    def assert_volume_details(self, items):
        """Check presence of common volume properties.

        :param items: volume properties
        """
        values = ('attachments', 'availability_zone', 'bootable', 'created_at',
                  'description', 'encrypted', 'id', 'metadata', 'name', 'size',
                  'status', 'user_id', 'volume_type')

        for value in values:
            self.assertIn(value, items)

    def wait_for_volume_status(self, volume_id, status, timeout=60):
        """Wait until volume reaches given status.

        :param volume_id: uuid4 id of given volume
        :param status: expected status of volume
        :param timeout: timeout in seconds
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if status in self.cinder('show', params=volume_id):
                break
        else:
            self.fail("Volume %s did not reach status %s after %d seconds."
                      % (volume_id, status, timeout))

    def check_volume_not_deleted(self, volume_id):
        """Check that volume exists.

        :param volume_id: uuid4 id of given volume
        """
        self.assertTrue(self.cinder('show', params=volume_id))

    def check_volume_deleted(self, volume_id, timeout=60):
        """Check that volume deleted successfully.

        :param volume_id: uuid4 id of given volume
        :param timeout: timeout in seconds
        """
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                if volume_id not in self.cinder('show', params=volume_id):
                    break
        except exceptions.CommandFailed:
            pass
        else:
            self.fail("Volume %s not deleted after %d seconds."
                      % (volume_id, timeout))

    def volume_create(self, params):
        """Create volume.

        :param params: parameters to cinder command
        :return: volume dictionary
        """
        output = self.cinder('create', params=params)
        volume = self._get_property_from_output(output)
        self.addCleanup(self.volume_delete, volume['id'])
        self.wait_for_volume_status(volume['id'], 'available')
        return volume

    def volume_delete(self, volume_id):
        """Delete specified volume by ID.

        :param volume_id: uuid4 id of given volume
        """
        if volume_id in self.cinder('list'):
            self.cinder('delete', params=volume_id)

    def _get_property_from_output(self, output):
        """Create a dictionary from an output

        :param output: the output of the cmd
        """
        obj = {}
        items = self.parser.listing(output)
        for item in items:
            obj[item['Property']] = six.text_type(item['Value'])
        return obj

    def wait_for_snapshot_status(self, snapshot_id, status, timeout=60):
        """Wait until snapshot reaches given status.

        :param snapshot_id: uuid4 id of given volume
        :param status: expected snapshot's status
        :param timeout: timeout in seconds
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if status in self.cinder('snapshot-show', params=snapshot_id):
                break
        else:
            self.fail("Snapshot %s did not reach status %s after %d seconds."
                      % (snapshot_id, status, timeout))

    def check_snapshot_deleted(self, snapshot_id, timeout=60):
        """Check that snapshot deleted successfully.

        :param snapshot_id: the given snapshot id
        :param timeout: timeout in seconds
        """
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                if snapshot_id not in self.cinder('snapshot-show',
                                                  params=snapshot_id):
                    break
        except exceptions.CommandFailed:
            pass
        else:
            self.fail("Snapshot %s has not deleted after %d seconds."
                      % (snapshot_id, timeout))

    def assert_snapshot_details(self, items):
        """Check presence of common volume snapshot properties.

        :param items: volume snapshot properties
        """
        values = ('created_at', 'description', 'id', 'metadata', 'name',
                  'size', 'status', 'volume_id')

        for value in values:
            self.assertIn(value, items)

    def snapshot_create(self, volume_id):
        """Create a volume snapshot from the volume id.

        :param volume_id: the given volume id to create a snapshot
        """
        output = self.cinder('snapshot-create', params=volume_id)
        snapshot = self._get_property_from_output(output)
        self.addCleanup(self.snapshot_delete, snapshot['id'])
        self.wait_for_snapshot_status(snapshot['id'], 'available')
        return snapshot

    def snapshot_delete(self, snapshot_id):
        """Delete specified snapshot by ID.

        :param snapshot_id: the given snapshot id
        """
        if snapshot_id in self.cinder('snapshot-list'):
            self.cinder('snapshot-delete', params=snapshot_id)
