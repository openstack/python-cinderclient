# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import fixtures

IDENTITY_URL = 'http://identityserver:5000/v2.0'
VOLUME_URL = 'http://volume.host'
TENANT_ID = 'b363706f891f48019483f8bd6503c54b'

VOLUME_V1_URL = '%(volume_url)s/v1/%(tenant_id)s' % {'volume_url': VOLUME_URL,
                                                     'tenant_id': TENANT_ID}
VOLUME_V2_URL = '%(volume_url)s/v2/%(tenant_id)s' % {'volume_url': VOLUME_URL,
                                                     'tenant_id': TENANT_ID}


def generate_version_output(v1=True, v2=True):
    v1_dict = {
        "status": "SUPPORTED",
        "updated": "2014-06-28T12:20:21Z",
        "id": "v1.0",
        "links": [{
            "href": "http://127.0.0.1:8776/v1/",
            "rel": "self"
        }]
    }

    v2_dict = {
        "status": "CURRENT",
        "updated": "2012-11-21T11:33:21Z",
        "id": "v2.0", "links": [{
            "href": "http://127.0.0.1:8776/v2/",
            "rel": "self"
        }]
    }

    versions = []
    if v1:
        versions.append(v1_dict)

    if v2:
        versions.append(v2_dict)

    return {"versions": versions}


class Fixture(fixtures.Fixture):

    base_url = None
    json_headers = {'Content-Type': 'application/json'}

    def __init__(self, requests,
                 volume_url=VOLUME_URL,
                 identity_url=IDENTITY_URL):
        super(Fixture, self).__init__()
        self.requests = requests
        self.volume_url = volume_url
        self.identity_url = identity_url

    def url(self, *args):
        url_args = [self.volume_url]

        if self.base_url:
            url_args.append(self.base_url)

        return '/'.join(str(a).strip('/') for a in tuple(url_args) + args)
