# Copyright 2013 Red Hat, Inc.
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
from cinderclient.tests.unit.fixture_data import client
from cinderclient.tests.unit.fixture_data import snapshots


class SnapshotActionsTest(utils.FixturedTestCase):

    client_fixture_class = client.V2
    data_fixture_class = snapshots.Fixture

    def test_update_snapshot_status(self):
        s = self.cs.volume_snapshots.get('1234')
        stat = {'status': 'available'}
        self.cs.volume_snapshots.update_snapshot_status(s, stat)
        self.assert_called('POST', '/snapshots/1234/action')

    def test_update_snapshot_status_with_progress(self):
        s = self.cs.volume_snapshots.get('1234')
        stat = {'status': 'available', 'progress': '73%'}
        self.cs.volume_snapshots.update_snapshot_status(s, stat)
        self.assert_called('POST', '/snapshots/1234/action')

    def test_list_snapshots_with_marker_limit(self):
        self.cs.volume_snapshots.list(marker=1234, limit=2)
        self.assert_called('GET', '/snapshots/detail?limit=2&marker=1234')

    def test_list_snapshots_with_sort(self):
        self.cs.volume_snapshots.list(sort="id")
        self.assert_called('GET', '/snapshots/detail?sort=id')
