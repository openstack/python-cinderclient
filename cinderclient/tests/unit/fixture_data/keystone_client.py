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

import copy
import json

from oslo_utils import uuidutils


# these are copied from python-keystoneclient tests
BASE_HOST = 'http://keystone.example.com'
BASE_URL = "%s:5000/" % BASE_HOST
UPDATED = '2013-03-06T00:00:00Z'

V2_URL = "%sv2.0" % BASE_URL
V2_DESCRIBED_BY_HTML = {'href': 'http://docs.openstack.org/api/'
                                'openstack-identity-service/2.0/content/',
                        'rel': 'describedby',
                        'type': 'text/html'}

V2_DESCRIBED_BY_PDF = {'href': 'http://docs.openstack.org/api/openstack-ident'
                               'ity-service/2.0/identity-dev-guide-2.0.pdf',
                       'rel': 'describedby',
                       'type': 'application/pdf'}

V2_VERSION = {'id': 'v2.0',
              'links': [{'href': V2_URL, 'rel': 'self'},
                        V2_DESCRIBED_BY_HTML, V2_DESCRIBED_BY_PDF],
              'status': 'stable',
              'updated': UPDATED}

V3_URL = "%sv3" % BASE_URL
V3_MEDIA_TYPES = [{'base': 'application/json',
                   'type': 'application/vnd.openstack.identity-v3+json'},
                  {'base': 'application/xml',
                   'type': 'application/vnd.openstack.identity-v3+xml'}]

V3_VERSION = {'id': 'v3.0',
              'links': [{'href': V3_URL, 'rel': 'self'}],
              'media-types': V3_MEDIA_TYPES,
              'status': 'stable',
              'updated': UPDATED}

WRONG_VERSION_RESPONSE = {'id': 'v2.0',
                          'links': [V2_DESCRIBED_BY_HTML, V2_DESCRIBED_BY_PDF],
                          'status': 'stable',
                          'updated': UPDATED}


def _create_version_list(versions):
    """
    Create a list of versions of the given versions.

    Args:
        versions: (str): write your description
    """
    return json.dumps({'versions': {'values': versions}})


def _create_single_version(version):
    """
    Create a version of the version.

    Args:
        version: (str): write your description
    """
    return json.dumps({'version': version})


V3_VERSION_LIST = _create_version_list([V3_VERSION, V2_VERSION])
V2_VERSION_LIST = _create_version_list([V2_VERSION])

V3_VERSION_ENTRY = _create_single_version(V3_VERSION)
V2_VERSION_ENTRY = _create_single_version(V2_VERSION)

CINDER_ENDPOINT = 'http://www.cinder.com/v1'


def _get_normalized_token_data(**kwargs):
    """
    Retrieve the token data dicts for the salt.

    Args:
    """
    ref = copy.deepcopy(kwargs)
    # normalized token data
    ref['user_id'] = ref.get('user_id', uuidutils.generate_uuid(dashed=False))
    ref['username'] = ref.get('username',
                              uuidutils.generate_uuid(dashed=False))
    ref['project_id'] = ref.get('project_id',
                                ref.get('tenant_id', uuidutils.generate_uuid(
                                    dashed=False)))
    ref['project_name'] = ref.get('project_name',
                                  ref.get('tenant_name',
                                          uuidutils.generate_uuid(
                                              dashed=False)))
    ref['user_domain_id'] = ref.get('user_domain_id',
                                    uuidutils.generate_uuid(dashed=False))
    ref['user_domain_name'] = ref.get('user_domain_name',
                                      uuidutils.generate_uuid(dashed=False))
    ref['project_domain_id'] = ref.get('project_domain_id',
                                       uuidutils.generate_uuid(dashed=False))
    ref['project_domain_name'] = ref.get('project_domain_name',
                                         uuidutils.generate_uuid(dashed=False))
    ref['roles'] = ref.get('roles',
                           [{'name': uuidutils.generate_uuid(dashed=False),
                             'id': uuidutils.generate_uuid(dashed=False)}])
    ref['roles_link'] = ref.get('roles_link', [])
    ref['cinder_url'] = ref.get('cinder_url', CINDER_ENDPOINT)

    return ref


def generate_v2_project_scoped_token(**kwargs):
    """Generate a Keystone V2 token based on auth request."""
    ref = _get_normalized_token_data(**kwargs)
    token = uuidutils.generate_uuid(dashed=False)

    o = {'access': {'token': {'id': token,
                              'expires': '2099-05-22T00:02:43.941430Z',
                              'issued_at': '2013-05-21T00:02:43.941473Z',
                              'tenant': {'enabled': True,
                                         'id': ref.get('project_id'),
                                         'name': ref.get('project_id')
                                         }
                              },
                    'user': {'id': ref.get('user_id'),
                             'name': uuidutils.generate_uuid(dashed=False),
                             'username': ref.get('username'),
                             'roles': ref.get('roles'),
                             'roles_links': ref.get('roles_links')
                             }
                    }}

    # Add endpoint Keystone
    o['access']['serviceCatalog'] = [
        {
            'endpoints': [
            {
                'publicURL': ref.get('auth_url'),
                'adminURL': ref.get('auth_url'),
                'internalURL': ref.get('auth_url'),
                'id': uuidutils.generate_uuid(dashed=False),
                'region': 'RegionOne'
            }],
            'endpoint_links': [],
            'name': 'keystone',
            'type': 'identity'
        }
    ]

    cinder_endpoint = {
        'endpoints': [
            {
                'publicURL': 'public_' + ref.get('cinder_url'),
                'internalURL': 'internal_' + ref.get('cinder_url'),
                'adminURL': 'admin_' + (ref.get('auth_url') or ""),
                'id': uuidutils.generate_uuid(dashed=False),
                'region': 'RegionOne'
            }
        ],
        'endpoints_links': [],
        'name': None,
        'type': 'volumev2'
    }

    # Add multiple Cinder endpoints
    for count in range(1, 4):
        # Copy the endpoint and create a service name
        endpoint_copy = copy.deepcopy(cinder_endpoint)
        name = "cinder%i" % count
        # Assign the service name and a unique endpoint
        endpoint_copy['endpoints'][0]['publicURL'] = \
            'http://%s.api.com/v2' % name
        endpoint_copy['name'] = name

        o['access']['serviceCatalog'].append(endpoint_copy)

    return token, o


def generate_v3_project_scoped_token(**kwargs):
    """Generate a Keystone V3 token based on auth request."""
    ref = _get_normalized_token_data(**kwargs)

    o = {'token': {'expires_at': '2099-05-22T00:02:43.941430Z',
                   'issued_at': '2013-05-21T00:02:43.941473Z',
                   'methods': ['password'],
                   'project': {'id': ref.get('project_id'),
                               'name': ref.get('project_name'),
                               'domain': {'id': ref.get('project_domain_id'),
                                          'name': ref.get(
                                              'project_domain_name')
                                          }
                               },
                   'user': {'id': ref.get('user_id'),
                            'name': ref.get('username'),
                            'domain': {'id': ref.get('user_domain_id'),
                                       'name': ref.get('user_domain_name')
                                       }
                            },
                   'roles': ref.get('roles')
                   }}

    # we only care about Neutron and Keystone endpoints
    o['token']['catalog'] = [
        {'endpoints': [
            {
                'id': uuidutils.generate_uuid(dashed=False),
                'interface': 'public',
                'region': 'RegionOne',
                'url': 'public_' + ref.get('cinder_url')
            },
            {
                'id': uuidutils.generate_uuid(dashed=False),
                'interface': 'internal',
                'region': 'RegionOne',
                'url': 'internal_' + ref.get('cinder_url')
            },
            {
                'id': uuidutils.generate_uuid(dashed=False),
                'interface': 'admin',
                'region': 'RegionOne',
                'url': 'admin_' + ref.get('cinder_url')
            }],
         'id': uuidutils.generate_uuid(dashed=False),
         'type': 'network'},
        {'endpoints': [
            {
                'id': uuidutils.generate_uuid(dashed=False),
                'interface': 'public',
                'region': 'RegionOne',
                'url': ref.get('auth_url')
            },
            {
                'id': uuidutils.generate_uuid(dashed=False),
                'interface': 'admin',
                'region': 'RegionOne',
                'url': ref.get('auth_url')
            }],
         'id': uuidutils.generate_uuid(dashed=False),
         'type': 'identity'}]

    # token ID is conveyed via the X-Subject-Token header so we are generating
    # one to stash there
    token_id = uuidutils.generate_uuid(dashed=False)

    return token_id, o


def keystone_request_callback(request, context):
    """
    The callback for the oauth

    Args:
        request: (todo): write your description
        context: (todo): write your description
    """
    context.headers['Content-Type'] = 'application/json'

    if request.url == BASE_URL:
        return V3_VERSION_LIST
    elif request.url == BASE_URL + "/v2.0":
        token_id, token_data = generate_v2_project_scoped_token()
        return token_data
    elif request.url.startswith("http://multiple.service.names"):
        token_id, token_data = generate_v2_project_scoped_token()
        return json.dumps(token_data)
    elif request.url == BASE_URL + "/v3":
        token_id, token_data = generate_v3_project_scoped_token()
        context.headers["X-Subject-Token"] = token_id
        context.status_code = 201
        return token_data
    elif "wrongdiscoveryresponse.discovery.com" in request.url:
        return str(WRONG_VERSION_RESPONSE)
    else:
        context.status_code = 500
        return str(WRONG_VERSION_RESPONSE)
