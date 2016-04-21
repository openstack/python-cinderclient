# Copyright (c) 2011 OpenStack Foundation
# Copyright 2010 Jacob Kaplan-Moss
# Copyright 2011 Piston Cloud Computing, Inc.
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
OpenStack Client interface. Handles the REST calls and responses.
"""

from __future__ import print_function

import glob
import hashlib
import imp
import itertools
import logging
import os
import pkgutil
import re
import six

from keystoneclient import access
from keystoneclient import adapter
from keystoneclient.auth.identity import base
from keystoneclient import discover
import requests

from cinderclient import api_versions
from cinderclient import exceptions
import cinderclient.extension
from cinderclient._i18n import _
from oslo_utils import encodeutils
from oslo_utils import importutils
from oslo_utils import strutils

from cinderclient import _i18n
# Enable i18n lazy translation
_i18n.enable_lazy()

osprofiler_web = importutils.try_import("osprofiler.web")

import six.moves.urllib.parse as urlparse

try:
    from eventlet import sleep
except ImportError:
    from time import sleep

try:
    import json
except ImportError:
    import simplejson as json

_VALID_VERSIONS = ['v1', 'v2', 'v3']
V3_SERVICE_TYPE = 'volumev3'
V2_SERVICE_TYPE = 'volumev2'
V1_SERVICE_TYPE = 'volume'
SERVICE_TYPES = {'1': V1_SERVICE_TYPE,
                 '2': V2_SERVICE_TYPE,
                 '3': V3_SERVICE_TYPE}

# tell keystoneclient that we can ignore the /v1|v2/{project_id} component of
# the service catalog when doing discovery lookups
for svc in ('volume', 'volumev2', 'volumev3'):
    discover.add_catalog_discover_hack(svc, re.compile('/v[12]/\w+/?$'), '/')


def get_volume_api_from_url(url):
    scheme, netloc, path, query, frag = urlparse.urlsplit(url)
    components = path.split("/")

    for version in _VALID_VERSIONS:
        if version in components:
            return version[1:]

    msg = (_("Invalid url: '%(url)s'. It must include one of: %(version)s.")
        % {'url': url, 'version': ', '.join(_VALID_VERSIONS)})
    raise exceptions.UnsupportedVersion(msg)


class SessionClient(adapter.LegacyJsonAdapter):

    def __init__(self, *args, **kwargs):
        self.api_version = kwargs.pop('api_version', None)
        self.api_version = self.api_version or api_versions.APIVersion()
        super(SessionClient, self).__init__(*args, **kwargs)

    def request(self, *args, **kwargs):
        kwargs.setdefault('headers', kwargs.get('headers', {}))
        api_versions.update_headers(kwargs["headers"], self.api_version)
        kwargs.setdefault('authenticated', False)
        # Note(tpatil): The standard call raises errors from
        # keystoneclient, here we need to raise the cinderclient errors.
        raise_exc = kwargs.pop('raise_exc', True)
        resp, body = super(SessionClient, self).request(*args,
                                                        raise_exc=False,
                                                        **kwargs)
        if raise_exc and resp.status_code >= 400:
            raise exceptions.from_response(resp, body)

        return resp, body

    def _cs_request(self, url, method, **kwargs):
        # this function is mostly redundant but makes compatibility easier
        kwargs.setdefault('authenticated', True)
        return self.request(url, method, **kwargs)

    def get(self, url, **kwargs):
        return self._cs_request(url, 'GET', **kwargs)

    def post(self, url, **kwargs):
        return self._cs_request(url, 'POST', **kwargs)

    def put(self, url, **kwargs):
        return self._cs_request(url, 'PUT', **kwargs)

    def delete(self, url, **kwargs):
        return self._cs_request(url, 'DELETE', **kwargs)

    def get_volume_api_version_from_endpoint(self):
        try:
            version = get_volume_api_from_url(self.get_endpoint())
        except exceptions.UnsupportedVersion as e:
            msg = (_("Service catalog returned invalid url.\n"
                     "%s") % six.text_type(e.message))
            raise exceptions.UnsupportedVersion(msg)

        return version

    def authenticate(self, auth=None):
        self.invalidate(auth)
        return self.get_token(auth)

    @property
    def service_catalog(self):
        # NOTE(jamielennox): This is ugly and should be deprecated.
        auth = self.auth or self.session.auth

        if isinstance(auth, base.BaseIdentityPlugin):
            return auth.get_access(self.session).service_catalog

        raise AttributeError('There is no service catalog for this type of '
                             'auth plugin.')


class HTTPClient(object):

    SENSITIVE_HEADERS = ('X-Auth-Token', 'X-Subject-Token',)
    USER_AGENT = 'python-cinderclient'

    def __init__(self, user, password, projectid, auth_url=None,
                 insecure=False, timeout=None, tenant_id=None,
                 proxy_tenant_id=None, proxy_token=None, region_name=None,
                 endpoint_type='publicURL', service_type=None,
                 service_name=None, volume_service_name=None,
                 bypass_url=None, retries=None,
                 http_log_debug=False, cacert=None,
                 auth_system='keystone', auth_plugin=None, api_version=None):
        self.user = user
        self.password = password
        self.projectid = projectid
        self.tenant_id = tenant_id
        self.api_version = api_version or api_versions.APIVersion()

        if auth_system and auth_system != 'keystone' and not auth_plugin:
            raise exceptions.AuthSystemNotFound(auth_system)

        if not auth_url and auth_system and auth_system != 'keystone':
            auth_url = auth_plugin.get_auth_url()
            if not auth_url:
                raise exceptions.EndpointNotFound()

        self.auth_url = auth_url.rstrip('/') if auth_url else None
        self.version = 'v1'
        self.region_name = region_name
        self.endpoint_type = endpoint_type
        self.service_type = service_type
        self.service_name = service_name
        self.volume_service_name = volume_service_name
        self.bypass_url = bypass_url.rstrip('/') if bypass_url else bypass_url
        self.retries = int(retries or 0)
        self.http_log_debug = http_log_debug

        self.management_url = self.bypass_url or None
        self.auth_token = None
        self.proxy_token = proxy_token
        self.proxy_tenant_id = proxy_tenant_id
        self.timeout = timeout

        if insecure:
            self.verify_cert = False
        else:
            if cacert:
                self.verify_cert = cacert
            else:
                self.verify_cert = True

        self.auth_system = auth_system
        self.auth_plugin = auth_plugin

        self._logger = logging.getLogger(__name__)

    def _safe_header(self, name, value):
        if name in HTTPClient.SENSITIVE_HEADERS:
            encoded = value.encode('utf-8')
            hashed = hashlib.sha1(encoded)
            digested = hashed.hexdigest()
            return encodeutils.safe_decode(name), "{SHA1}%s" % digested
        else:
            return (encodeutils.safe_decode(name),
                    encodeutils.safe_decode(value))

    def http_log_req(self, args, kwargs):
        if not self.http_log_debug:
            return

        string_parts = ['curl -i']
        for element in args:
            if element in ('GET', 'POST', 'DELETE', 'PUT'):
                string_parts.append(' -X %s' % element)
            else:
                string_parts.append(' %s' % element)

        for element in kwargs['headers']:
            header = ("-H '%s: %s'" %
                      self._safe_header(element, kwargs['headers'][element]))
            string_parts.append(header)

        if 'data' in kwargs:
            if "password" in kwargs['data']:
                data = strutils.mask_password(kwargs['data'])
            else:
                data = kwargs['data']
            string_parts.append(" -d '%s'" % (data))
        self._logger.debug("\nREQ: %s\n" % "".join(string_parts))

    def http_log_resp(self, resp):
        if not self.http_log_debug:
            return
        self._logger.debug(
            "RESP: [%s] %s\nRESP BODY: %s\n",
            resp.status_code,
            resp.headers,
            resp.text)

    def request(self, url, method, **kwargs):
        kwargs.setdefault('headers', kwargs.get('headers', {}))
        kwargs['headers']['User-Agent'] = self.USER_AGENT
        kwargs['headers']['Accept'] = 'application/json'

        if osprofiler_web:
            kwargs['headers'].update(osprofiler_web.get_trace_id_headers())

        if 'body' in kwargs:
            kwargs['headers']['Content-Type'] = 'application/json'
            kwargs['data'] = json.dumps(kwargs['body'])
            del kwargs['body']
        api_versions.update_headers(kwargs["headers"], self.api_version)

        if self.timeout:
            kwargs.setdefault('timeout', self.timeout)
        self.http_log_req((url, method,), kwargs)
        resp = requests.request(
            method,
            url,
            verify=self.verify_cert,
            **kwargs)
        self.http_log_resp(resp)

        body = None
        if resp.text:
            try:
                body = json.loads(resp.text)
            except ValueError as e:
                self._logger.debug("Load http response text error: %s", e)

        if resp.status_code >= 400:
            raise exceptions.from_response(resp, body)

        return resp, body

    def _cs_request(self, url, method, **kwargs):
        auth_attempts = 0
        attempts = 0
        backoff = 1
        while True:
            attempts += 1
            if not self.management_url or not self.auth_token:
                self.authenticate()
            kwargs.setdefault('headers', {})['X-Auth-Token'] = self.auth_token
            if self.projectid:
                kwargs['headers']['X-Auth-Project-Id'] = self.projectid
            try:
                if not url.startswith(self.management_url):
                    url = self.management_url + url
                resp, body = self.request(url, method, **kwargs)
                return resp, body
            except exceptions.BadRequest as e:
                if attempts > self.retries:
                    raise
            except exceptions.Unauthorized:
                if auth_attempts > 0:
                    raise
                self._logger.debug("Unauthorized, reauthenticating.")
                self.management_url = self.auth_token = None
                # First reauth. Discount this attempt.
                attempts -= 1
                auth_attempts += 1
                continue
            except exceptions.ClientException as e:
                if attempts > self.retries:
                    raise
                if 500 <= e.code <= 599:
                    pass
                else:
                    raise
            except requests.exceptions.ConnectionError as e:
                self._logger.debug("Connection error: %s" % e)
                if attempts > self.retries:
                    msg = 'Unable to establish connection: %s' % e
                    raise exceptions.ConnectionError(msg)
            except requests.exceptions.Timeout as e:
                self._logger.debug("Timeout error: %s" % e)
                if attempts > self.retries:
                    raise
            self._logger.debug(
                "Failed attempt(%s of %s), retrying in %s seconds" %
                (attempts, self.retries, backoff))
            sleep(backoff)
            backoff *= 2

    def get(self, url, **kwargs):
        return self._cs_request(url, 'GET', **kwargs)

    def post(self, url, **kwargs):
        return self._cs_request(url, 'POST', **kwargs)

    def put(self, url, **kwargs):
        return self._cs_request(url, 'PUT', **kwargs)

    def delete(self, url, **kwargs):
        return self._cs_request(url, 'DELETE', **kwargs)

    def get_volume_api_version_from_endpoint(self):
        try:
            version = get_volume_api_from_url(self.management_url)
        except exceptions.UnsupportedVersion as e:
            if self.management_url == self.bypass_url:
                msg = (_("Invalid url was specified in --bypass-url or "
                         "environment variable CINDERCLIENT_BYPASS_URL.\n"
                         "%s") % six.text_type(e.message))
            else:
                msg = (_("Service catalog returned invalid url.\n"
                         "%s") % six.text_type(e.message))

            raise exceptions.UnsupportedVersion(msg)

        return version

    def _extract_service_catalog(self, url, resp, body, extract_token=True):
        """See what the auth service told us and process the response.
        We may get redirected to another site, fail or actually get
        back a service catalog with a token and our endpoints.
        """

        if resp.status_code == 200:  # content must always present
            try:
                self.auth_url = url
                self.auth_ref = access.AccessInfo.factory(resp, body)
                self.service_catalog = self.auth_ref.service_catalog

                if extract_token:
                    self.auth_token = self.auth_ref.auth_token

                management_url = self.service_catalog.url_for(
                    region_name=self.region_name,
                    endpoint_type=self.endpoint_type,
                    service_type=self.service_type,
                    service_name=self.service_name)
                self.management_url = management_url.rstrip('/')
                return None
            except exceptions.AmbiguousEndpoints:
                print("Found more than one valid endpoint. Use a more "
                      "restrictive filter")
                raise
            except KeyError:
                raise exceptions.AuthorizationFailure()
            except exceptions.EndpointNotFound:
                print("Could not find any suitable endpoint. Correct region?")
                raise

        elif resp.status_code == 305:
            return resp['location']
        else:
            raise exceptions.from_response(resp, body)

    def _fetch_endpoints_from_auth(self, url):
        """We have a token, but don't know the final endpoint for
        the region. We have to go back to the auth service and
        ask again. This request requires an admin-level token
        to work. The proxy token supplied could be from a low-level enduser.

        We can't get this from the keystone service endpoint, we have to use
        the admin endpoint.

        This will overwrite our admin token with the user token.
        """

        # GET ...:5001/v2.0/tokens/#####/endpoints
        url = '/'.join([url, 'tokens', '%s?belongsTo=%s'
                        % (self.proxy_token, self.proxy_tenant_id)])
        self._logger.debug("Using Endpoint URL: %s" % url)
        resp, body = self.request(url, "GET",
                                  headers={'X-Auth-Token': self.auth_token})
        return self._extract_service_catalog(url, resp, body,
                                             extract_token=False)

    def set_management_url(self, url):
        self.management_url = url

    def authenticate(self):
        magic_tuple = urlparse.urlsplit(self.auth_url)
        scheme, netloc, path, query, frag = magic_tuple
        port = magic_tuple.port
        if port is None:
            port = 80
        path_parts = path.split('/')
        for part in path_parts:
            if len(part) > 0 and part[0] == 'v':
                self.version = part
                break

        # TODO(sandy): Assume admin endpoint is 35357 for now.
        # Ideally this is going to have to be provided by the service catalog.
        new_netloc = netloc.replace(':%d' % port, ':%d' % (35357,))
        admin_url = urlparse.urlunsplit((scheme, new_netloc,
                                         path, query, frag))

        auth_url = self.auth_url
        if self.version == "v2.0":
            while auth_url:
                if not self.auth_system or self.auth_system == 'keystone':
                    auth_url = self._v2_auth(auth_url)
                else:
                    auth_url = self._plugin_auth(auth_url)

            # Are we acting on behalf of another user via an
            # existing token? If so, our actual endpoints may
            # be different than that of the admin token.
            if self.proxy_token:
                if self.bypass_url:
                    self.set_management_url(self.bypass_url)
                else:
                    self._fetch_endpoints_from_auth(admin_url)
                # Since keystone no longer returns the user token
                # with the endpoints any more, we need to replace
                # our service account token with the user token.
                self.auth_token = self.proxy_token
        else:
            try:
                while auth_url:
                    auth_url = self._v1_auth(auth_url)
            # In some configurations cinder makes redirection to
            # v2.0 keystone endpoint. Also, new location does not contain
            # real endpoint, only hostname and port.
            except exceptions.AuthorizationFailure:
                if auth_url.find('v2.0') < 0:
                    auth_url = auth_url + '/v2.0'
                self._v2_auth(auth_url)

        if self.bypass_url:
            self.set_management_url(self.bypass_url)
        elif not self.management_url:
            raise exceptions.Unauthorized('Cinder Client')

    def _v1_auth(self, url):
        if self.proxy_token:
            raise exceptions.NoTokenLookupException()

        headers = {'X-Auth-User': self.user,
                   'X-Auth-Key': self.password}
        if self.projectid:
            headers['X-Auth-Project-Id'] = self.projectid

        resp, body = self.request(url, 'GET', headers=headers)
        if resp.status_code in (200, 204):  # in some cases we get No Content
            try:
                mgmt_header = 'x-server-management-url'
                self.management_url = resp.headers[mgmt_header].rstrip('/')
                self.auth_token = resp.headers['x-auth-token']
                self.auth_url = url
            except (KeyError, TypeError):
                raise exceptions.AuthorizationFailure()
        elif resp.status_code == 305:
            return resp.headers['location']
        else:
            raise exceptions.from_response(resp, body)

    def _plugin_auth(self, auth_url):
        return self.auth_plugin.authenticate(self, auth_url)

    def _v2_auth(self, url):
        """Authenticate against a v2.0 auth service."""
        body = {"auth": {
            "passwordCredentials": {"username": self.user,
                                    "password": self.password}}}

        if self.projectid:
            body['auth']['tenantName'] = self.projectid
        elif self.tenant_id:
            body['auth']['tenantId'] = self.tenant_id

        self._authenticate(url, body)

    def _authenticate(self, url, body):
        """Authenticate and extract the service catalog."""
        token_url = url + "/tokens"

        # Make sure we follow redirects when trying to reach Keystone
        resp, body = self.request(
            token_url,
            "POST",
            body=body,
            allow_redirects=True)

        return self._extract_service_catalog(url, resp, body)


def _construct_http_client(username=None, password=None, project_id=None,
                           auth_url=None, insecure=False, timeout=None,
                           proxy_tenant_id=None, proxy_token=None,
                           region_name=None, endpoint_type='publicURL',
                           service_type='volume',
                           service_name=None, volume_service_name=None,
                           bypass_url=None, retries=None,
                           http_log_debug=False,
                           auth_system='keystone', auth_plugin=None,
                           cacert=None, tenant_id=None,
                           session=None,
                           auth=None, api_version=None,
                           **kwargs):

    # Don't use sessions if third party plugin is used
    if session and not auth_plugin:
        kwargs.setdefault('user_agent', 'python-cinderclient')
        kwargs.setdefault('interface', endpoint_type)
        return SessionClient(session=session,
                             auth=auth,
                             service_type=service_type,
                             service_name=service_name,
                             region_name=region_name,
                             api_version=api_version,
                             **kwargs)
    else:
        # FIXME(jamielennox): username and password are now optional. Need
        # to test that they were provided in this mode.
        return HTTPClient(username,
                          password,
                          projectid=project_id,
                          auth_url=auth_url,
                          insecure=insecure,
                          timeout=timeout,
                          tenant_id=tenant_id,
                          proxy_token=proxy_token,
                          proxy_tenant_id=proxy_tenant_id,
                          region_name=region_name,
                          endpoint_type=endpoint_type,
                          service_type=service_type,
                          service_name=service_name,
                          volume_service_name=volume_service_name,
                          bypass_url=bypass_url,
                          retries=retries,
                          http_log_debug=http_log_debug,
                          cacert=cacert,
                          auth_system=auth_system,
                          auth_plugin=auth_plugin,
                          )


def _get_client_class_and_version(version):
    if not isinstance(version, api_versions.APIVersion):
        version = api_versions.get_api_version(version)
    else:
        api_versions.check_major_version(version)
    if version.is_latest():
        raise exceptions.UnsupportedVersion(
            _("The version should be explicit, not latest."))
    return version, importutils.import_class(
        "cinderclient.v%s.client.Client" % version.ver_major)


def get_client_class(version):
    version_map = {
        '1': 'cinderclient.v1.client.Client',
        '2': 'cinderclient.v2.client.Client',
        '3': 'cinderclient.v3.client.Client',
    }
    try:
        client_path = version_map[str(version)]
    except (KeyError, ValueError):
        msg = "Invalid client version '%s'. must be one of: %s" % (
            (version, ', '.join(version_map)))
        raise exceptions.UnsupportedVersion(msg)

    return importutils.import_class(client_path)


def discover_extensions(version):
    extensions = []
    for name, module in itertools.chain(
            _discover_via_python_path(),
            _discover_via_contrib_path(version)):

        extension = cinderclient.extension.Extension(name, module)
        extensions.append(extension)

    return extensions


def _discover_via_python_path():
    for (module_loader, name, ispkg) in pkgutil.iter_modules():
        if name.endswith('cinderclient_ext'):
            if not hasattr(module_loader, 'load_module'):
                # Python 2.6 compat: actually get an ImpImporter obj
                module_loader = module_loader.find_module(name)

            module = module_loader.load_module(name)
            yield name, module


def _discover_via_contrib_path(version):
    module_path = os.path.dirname(os.path.abspath(__file__))
    version_str = "v%s" % version.replace('.', '_')
    ext_path = os.path.join(module_path, version_str, 'contrib')
    ext_glob = os.path.join(ext_path, "*.py")

    for ext_path in glob.iglob(ext_glob):
        name = os.path.basename(ext_path)[:-3]

        if name == "__init__":
            continue

        module = imp.load_source(name, ext_path)
        yield name, module


def Client(version, *args, **kwargs):
    """Initialize client object based on given version.

    HOW-TO:
    The simplest way to create a client instance is initialization with your
    credentials::

    .. code-block:: python

        >>> from cinderclient import client
        >>> cinder = client.Client(VERSION, USERNAME, PASSWORD,
        ...                      PROJECT_ID, AUTH_URL)

    Here ``VERSION`` can be a string or
    ``cinderclient.api_versions.APIVersion`` obj. If you prefer string value,
    you can use ``1`` (deprecated now), ``2``, or ``3.X``
    (where X is a microversion).


    Alternatively, you can create a client instance using the keystoneclient
    session API. See "The cinderclient Python API" page at
    python-cinderclient's doc.
    """
    api_version, client_class = _get_client_class_and_version(version)
    return client_class(api_version=api_version,
                        *args, **kwargs)
