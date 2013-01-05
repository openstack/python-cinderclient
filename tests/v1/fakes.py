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

import urlparse

from cinderclient import client as base_client
from cinderclient.v1 import client
from tests import fakes
import tests.utils as utils


def _stub_volume(**kwargs):
    volume = {
        'id': '1234',
        'display_name': None,
        'display_description': None,
        "attachments": [],
        "bootable": "false",
        "availability_zone": "cinder",
        "created_at": "2012-08-27T00:00:00.000000",
        "display_description": None,
        "display_name": None,
        "id": '00000000-0000-0000-0000-000000000000',
        "metadata": {},
        "size": 1,
        "snapshot_id": None,
        "status": "available",
        "volume_type": "None",
    }
    volume.update(kwargs)
    return volume


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
                               'project_id', 'auth_url',
                               extensions=kwargs.get('extensions'))
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
        status, headers, body = getattr(self, callback)(**kwargs)
        r = utils.TestResponse({
            "status_code": status,
            "text": body,
            "headers": headers,
        })
        return r, body

        if hasattr(status, 'items'):
            return utils.TestResponse(status), body
        else:
            return utils.TestResponse({"status": status}), body

    #
    # Snapshots
    #

    def get_snapshots_detail(self, **kw):
        return (200, {}, {'snapshots': [
            _stub_snapshot(),
        ]})

    def get_snapshots_1234(self, **kw):
        return (200, {}, {'snapshot': _stub_snapshot(id='1234')})

    def put_snapshots_1234(self, **kw):
        snapshot = _stub_snapshot(id='1234')
        snapshot.update(kw['body']['snapshot'])
        return (200, {}, {'snapshot': snapshot})

    #
    # Volumes
    #

    def put_volumes_1234(self, **kw):
        volume = _stub_volume(id='1234')
        volume.update(kw['body']['volume'])
        return (200, {}, {'volume': volume})

    def get_volumes(self, **kw):
        return (200, {}, {"volumes": [
            {'id': 1234, 'name': 'sample-volume'},
            {'id': 5678, 'name': 'sample-volume2'}
        ]})

    # TODO(jdg): This will need to change
    # at the very least it's not complete
    def get_volumes_detail(self, **kw):
        return (200, {}, {"volumes": [
            {'id': 1234,
             'name': 'sample-volume',
             'attachments': [{'server_id': 1234}]},
        ]})

    def get_volumes_1234(self, **kw):
        r = {'volume': self.get_volumes_detail()[2]['volumes'][0]}
        return (200, {}, r)

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
            return (202, {}, {'connection_info': 'foos'})
        elif action == 'os-terminate_connection':
            assert body[action].keys() == ['connector']
        elif action == 'os-begin_detaching':
            assert body[action] is None
        elif action == 'os-roll_detaching':
            assert body[action] is None
        else:
            raise AssertionError("Unexpected server action: %s" % action)
        return (resp, {}, _body)

    def post_volumes(self, **kw):
        return (202, {}, {'volume': {}})

    def delete_volumes_1234(self, **kw):
        return (202, {}, None)

    #
    # Quotas
    #

    def get_os_quota_sets_test(self, **kw):
        return (200, {}, {'quota_set': {
                          'tenant_id': 'test',
                          'metadata_items': [],
                          'volumes': 1,
                          'gigabytes': 1}})

    def get_os_quota_sets_test_defaults(self):
        return (200, {}, {'quota_set': {
                          'tenant_id': 'test',
                          'metadata_items': [],
                          'volumes': 1,
                          'gigabytes': 1}})

    def put_os_quota_sets_test(self, body, **kw):
        assert body.keys() == ['quota_set']
        fakes.assert_has_keys(body['quota_set'],
                              required=['tenant_id'])
        return (200, {}, {'quota_set': {
                          'tenant_id': 'test',
                          'metadata_items': [],
                          'volumes': 2,
                          'gigabytes': 1}})

    #
    # Quota Classes
    #

    def get_os_quota_class_sets_test(self, **kw):
        return (200, {}, {'quota_class_set': {
                          'class_name': 'test',
                          'metadata_items': [],
                          'volumes': 1,
                          'gigabytes': 1}})

    def put_os_quota_class_sets_test(self, body, **kw):
        assert body.keys() == ['quota_class_set']
        fakes.assert_has_keys(body['quota_class_set'],
                              required=['class_name'])
        return (200, {}, {'quota_class_set': {
                          'class_name': 'test',
                          'metadata_items': [],
                          'volumes': 2,
                          'gigabytes': 1}})

    #
    # VolumeTypes
    #
    def get_types(self, **kw):
        return (200, {}, {
            'volume_types': [{'id': 1,
                              'name': 'test-type-1',
                              'extra_specs':{}},
                             {'id': 2,
                              'name': 'test-type-2',
                              'extra_specs':{}}]})

    def get_types_1(self, **kw):
        return (200, {}, {'volume_type': {'id': 1,
                          'name': 'test-type-1',
                          'extra_specs': {}}})

    def post_types(self, body, **kw):
        return (202, {}, {'volume_type': {'id': 3,
                          'name': 'test-type-3',
                          'extra_specs': {}}})

    def post_types_1_extra_specs(self, body, **kw):
        assert body.keys() == ['extra_specs']
        return (200, {}, {'extra_specs': {'k': 'v'}})

    def delete_types_1_extra_specs_k(self, **kw):
        return(204, {}, None)

    def delete_types_1(self, **kw):
        return (202, {}, None)

    #
    # Set/Unset metadata
    #
    def delete_volumes_1234_metadata_test_key(self, **kw):
        return (204, {}, None)

    def delete_volumes_1234_metadata_key1(self, **kw):
        return (204, {}, None)

    def delete_volumes_1234_metadata_key2(self, **kw):
        return (204, {}, None)

    def post_volumes_1234_metadata(self, **kw):
        return (204, {}, {'metadata': {'test_key': 'test_value'}})

    #
    # List all extensions
    #
    def get_extensions(self, **kw):
        exts = [
            {
                "alias": "FAKE-1",
                "description": "Fake extension number 1",
                "links": [],
                "name": "Fake1",
                "namespace": ("http://docs.openstack.org/"
                              "/ext/fake1/api/v1.1"),
                "updated": "2011-06-09T00:00:00+00:00"
            },
            {
                "alias": "FAKE-2",
                "description": "Fake extension number 2",
                "links": [],
                "name": "Fake2",
                "namespace": ("http://docs.openstack.org/"
                              "/ext/fake1/api/v1.1"),
                "updated": "2011-06-09T00:00:00+00:00"
            },
        ]
        return (200, {}, {"extensions": exts, })
