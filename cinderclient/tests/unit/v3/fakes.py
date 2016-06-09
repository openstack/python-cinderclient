# Copyright (c) 2013 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime

from cinderclient.tests.unit import fakes
from cinderclient.v3 import client
from cinderclient.tests.unit.v2 import fakes as fake_v2


class FakeClient(fakes.FakeClient, client.Client):

    def __init__(self, *args, **kwargs):
        client.Client.__init__(self, 'username', 'password',
                               'project_id', 'auth_url',
                               extensions=kwargs.get('extensions'))
        self.client = FakeHTTPClient(**kwargs)

    def get_volume_api_version_from_endpoint(self):
        return self.client.get_volume_api_version_from_endpoint()


class FakeHTTPClient(fake_v2.FakeHTTPClient):

    def __init__(self, **kwargs):
        super(FakeHTTPClient, self).__init__()
        self.management_url = 'http://10.0.2.15:8776/v3/fake'
        vars(self).update(kwargs)

    #
    # Services
    #
    def get_os_services(self, **kw):
        host = kw.get('host', None)
        binary = kw.get('binary', None)
        services = [
            {
                'id': 1,
                'binary': 'cinder-volume',
                'host': 'host1',
                'zone': 'cinder',
                'status': 'enabled',
                'state': 'up',
                'updated_at': datetime(2012, 10, 29, 13, 42, 2),
                'cluster': 'cluster1',
            },
            {
                'id': 2,
                'binary': 'cinder-volume',
                'host': 'host2',
                'zone': 'cinder',
                'status': 'disabled',
                'state': 'down',
                'updated_at': datetime(2012, 9, 18, 8, 3, 38),
                'cluster': 'cluster1',
            },
            {
                'id': 3,
                'binary': 'cinder-scheduler',
                'host': 'host2',
                'zone': 'cinder',
                'status': 'disabled',
                'state': 'down',
                'updated_at': datetime(2012, 9, 18, 8, 3, 38),
                'cluster': 'cluster2',
            },
        ]
        if host:
            services = list(filter(lambda i: i['host'] == host, services))
        if binary:
            services = list(filter(lambda i: i['binary'] == binary, services))
        if not self.api_version.matches('3.7'):
            for svc in services:
                del svc['cluster']
        return (200, {}, {'services': services})

    #
    # Clusters
    #
    def _filter_clusters(self, return_keys, **kw):
        date = datetime(2012, 10, 29, 13, 42, 2),
        clusters = [
            {
                'id': '1',
                'name': 'cluster1@lvmdriver-1',
                'state': 'up',
                'status': 'enabled',
                'binary': 'cinder-volume',
                'is_up': 'True',
                'disabled': 'False',
                'disabled_reason': None,
                'num_hosts': '3',
                'num_down_hosts': '2',
                'updated_at': date,
                'created_at': date,
                'last_heartbeat': date,
            },
            {
                'id': '2',
                'name': 'cluster1@lvmdriver-2',
                'state': 'down',
                'status': 'enabled',
                'binary': 'cinder-volume',
                'is_up': 'False',
                'disabled': 'False',
                'disabled_reason': None,
                'num_hosts': '2',
                'num_down_hosts': '2',
                'updated_at': date,
                'created_at': date,
                'last_heartbeat': date,
            },
            {
                'id': '3',
                'name': 'cluster2',
                'state': 'up',
                'status': 'disabled',
                'binary': 'cinder-backup',
                'is_up': 'True',
                'disabled': 'True',
                'disabled_reason': 'Reason',
                'num_hosts': '1',
                'num_down_hosts': '0',
                'updated_at': date,
                'created_at': date,
                'last_heartbeat': date,
            },
        ]

        for key, value in kw.items():
            clusters = [cluster for cluster in clusters
                        if cluster[key] == str(value)]

        result = []
        for cluster in clusters:
            result.append({key: cluster[key] for key in return_keys})
        return result

    CLUSTER_SUMMARY_KEYS = ('name', 'binary', 'state', 'status')
    CLUSTER_DETAIL_KEYS = (CLUSTER_SUMMARY_KEYS +
                           ('num_hosts', 'num_down_hosts', 'last_heartbeat',
                            'disabled_reason', 'created_at', 'updated_at'))

    def get_clusters(self, **kw):
        clusters = self._filter_clusters(self.CLUSTER_SUMMARY_KEYS, **kw)
        return (200, {}, {'clusters': clusters})

    def get_clusters_detail(self, **kw):
        clusters = self._filter_clusters(self.CLUSTER_DETAIL_KEYS, **kw)
        return (200, {}, {'clusters': clusters})

    def get_clusters_1(self):
        res = self.get_clusters_detail(id=1)
        return (200, {}, {'cluster': res[2]['clusters'][0]})

    def put_clusters_enable(self, body):
        res = self.get_clusters(id=1)
        return (200, {}, {'cluster': res[2]['clusters'][0]})

    def put_clusters_disable(self, body):
        res = self.get_clusters(id=3)
        return (200, {}, {'cluster': res[2]['clusters'][0]})
