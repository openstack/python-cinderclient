# Copyright (c) 2011 X.commerce, a business unit of eBay Inc.
# Copyright 2011 OpenStack, LLC
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

import httplib2
import urlparse

from cinderclient import client as base_client
from cinderclient.v1 import client
from tests import fakes


def _stub_snapshot(**kwargs):
    snapshot = {
        "created_at": "2012-08-28T16:30:31.000000",
        "display_description": None,
        "display_name": None,
        "id": '11111111-1111-1111-1111-111111111111',
        "size": 1,
        "status": "available",
        "volume_id": '00000000-0000-0000-0000-000000000000',
    }
    snapshot.update(kwargs)
    return snapshot


class FakeClient(fakes.FakeClient, client.Client):

    def __init__(self, *args, **kwargs):
        client.Client.__init__(self, 'username', 'password',
                               'project_id', 'auth_url')
        self.client = FakeHTTPClient(**kwargs)


class FakeHTTPClient(base_client.HTTPClient):

    def __init__(self, **kwargs):
        self.username = 'username'
        self.password = 'password'
        self.auth_url = 'auth_url'
        self.callstack = []

    def _cs_request(self, url, method, **kwargs):
        # Check that certain things are called correctly
        if method in ['GET', 'DELETE']:
            assert 'body' not in kwargs
        elif method == 'PUT':
            assert 'body' in kwargs

        # Call the method
        args = urlparse.parse_qsl(urlparse.urlparse(url)[4])
        kwargs.update(args)
        munged_url = url.rsplit('?', 1)[0]
        munged_url = munged_url.strip('/').replace('/', '_').replace('.', '_')
        munged_url = munged_url.replace('-', '_')

        callback = "%s_%s" % (method.lower(), munged_url)

        if not hasattr(self, callback):
            raise AssertionError('Called unknown API method: %s %s, '
                                 'expected fakes method name: %s' %
                                 (method, url, callback))

        # Note the call
        self.callstack.append((method, url, kwargs.get('body', None)))

        status, body = getattr(self, callback)(**kwargs)
        if hasattr(status, 'items'):
            return httplib2.Response(status), body
        else:
            return httplib2.Response({"status": status}), body

    #
    # Snapshots
    #

    def get_snapshots_detail(self, **kw):
        return (200, {'snapshots': [
            _stub_snapshot(),
        ]})

    #
    # volumes
    #

    def get_volumes(self, **kw):
        return (200, {"volumes": [
            {'id': 1234, 'name': 'sample-volume'},
            {'id': 5678, 'name': 'sample-volume2'}
        ]})

    # TODO(jdg): This will need to change
    # at the very least it's not complete
    def get_volumes_detail(self, **kw):
        return (200, {"volumes": [
            {'id': 1234,
             'name': 'sample-volume',
             'attachments': [{'server_id': 1234}]},
        ]})

    def get_volumes_1234(self, **kw):
        r = {'volume': self.get_volumes_detail()[1]['volumes'][0]}
        return (200, r)

    def post_volumes_1234_action(self, body, **kw):
        _body = None
        resp = 202
        assert len(body.keys()) == 1
        action = body.keys()[0]
        if action == 'os-attach':
            assert body[action].keys() == ['instance_uuid', 'mountpoint']
        elif action == 'os-detach':
            assert body[action] is None
        elif action == 'os-reserve':
            assert body[action] is None
        elif action == 'os-unreserve':
            assert body[action] is None
        elif action == 'os-initialize_connection':
            assert body[action].keys() == ['connector']
            return (202, {'connection_info': 'foos'})
        elif action == 'os-terminate_connection':
            assert body[action].keys() == ['connector']
        elif action == 'os-begin_detaching':
            assert body[action] is None
        elif action == 'os-roll_detaching':
            assert body[action] is None
        else:
            raise AssertionError("Unexpected server action: %s" % action)
        return (resp, _body)

    def post_volumes(self, **kw):
        return (202, {'volume': {}})

    def delete_volumes_1234(self, **kw):
        return (202, None)

    #
    # Quotas
    #

    def get_os_quota_sets_test(self, **kw):
        return (200, {'quota_set': {
                      'tenant_id': 'test',
                      'metadata_items': [],
                      'volumes': 1,
                      'gigabytes': 1}})

    def get_os_quota_sets_test_defaults(self):
        return (200, {'quota_set': {
                      'tenant_id': 'test',
                      'metadata_items': [],
                      'volumes': 1,
                      'gigabytes': 1}})

    def put_os_quota_sets_test(self, body, **kw):
        assert body.keys() == ['quota_set']
        fakes.assert_has_keys(body['quota_set'],
                              required=['tenant_id'])
        return (200, {'quota_set': {
                      'tenant_id': 'test',
                      'metadata_items': [],
                      'volumes': 2,
                      'gigabytes': 1}})

    #
    # Quota Classes
    #

    def get_os_quota_class_sets_test(self, **kw):
        return (200, {'quota_class_set': {
                      'class_name': 'test',
                      'metadata_items': [],
                      'volumes': 1,
                      'gigabytes': 1}})

    def put_os_quota_class_sets_test(self, body, **kw):
        assert body.keys() == ['quota_class_set']
        fakes.assert_has_keys(body['quota_class_set'],
                              required=['class_name'])
        return (200, {'quota_class_set': {
                      'class_name': 'test',
                      'metadata_items': [],
                      'volumes': 2,
                      'gigabytes': 1}})
