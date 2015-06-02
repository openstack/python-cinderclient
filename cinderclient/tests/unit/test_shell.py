# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import re
import sys

import fixtures
from keystoneclient import fixture as keystone_client_fixture
import mock
import pkg_resources
import requests_mock
import requests
from six import moves
from testtools import matchers

from cinderclient import exceptions
from cinderclient import auth_plugin
from cinderclient import shell
from cinderclient.tests.unit.test_auth_plugins import mock_http_request
from cinderclient.tests.unit.test_auth_plugins import requested_headers
from cinderclient.tests.unit.fixture_data import base as fixture_base
from cinderclient.tests.unit.fixture_data import keystone_client
from cinderclient.tests.unit import utils
import keystoneclient.exceptions as ks_exc
from keystoneclient.exceptions import DiscoveryFailure


class ShellTest(utils.TestCase):

    FAKE_ENV = {
        'OS_USERNAME': 'username',
        'OS_PASSWORD': 'password',
        'OS_TENANT_NAME': 'tenant_name',
        'OS_AUTH_URL': '%s/v2.0' % keystone_client.BASE_HOST,
    }

    # Patch os.environ to avoid required auth info.
    def make_env(self, exclude=None, include=None):
        env = dict((k, v) for k, v in self.FAKE_ENV.items() if k != exclude)
        env.update(include or {})
        self.useFixture(fixtures.MonkeyPatch('os.environ', env))

    def setUp(self):
        super(ShellTest, self).setUp()
        for var in self.FAKE_ENV:
            self.useFixture(fixtures.EnvironmentVariable(var,
                                                         self.FAKE_ENV[var]))

    def shell(self, argstr):
        orig = sys.stdout
        try:
            sys.stdout = moves.StringIO()
            _shell = shell.OpenStackCinderShell()
            _shell.main(argstr.split())
        except SystemExit:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.assertEqual(0, exc_value.code)
        finally:
            out = sys.stdout.getvalue()
            sys.stdout.close()
            sys.stdout = orig

        return out

    def test_help_unknown_command(self):
        self.assertRaises(exceptions.CommandError, self.shell, 'help foofoo')

    def test_help(self):
        required = [
            '.*?^usage: ',
            '.*?(?m)^\s+create\s+Creates a volume.',
            '.*?(?m)^Run "cinder help SUBCOMMAND" for help on a subcommand.',
        ]
        help_text = self.shell('help')
        for r in required:
            self.assertThat(help_text,
                            matchers.MatchesRegex(r, re.DOTALL | re.MULTILINE))

    def test_help_on_subcommand(self):
        required = [
            '.*?^usage: cinder list',
            '.*?(?m)^Lists all volumes.',
        ]
        help_text = self.shell('help list')
        for r in required:
            self.assertThat(help_text,
                            matchers.MatchesRegex(r, re.DOTALL | re.MULTILINE))

    def register_keystone_auth_fixture(self, mocker, url):
        mocker.register_uri('GET', url,
                            text=keystone_client.keystone_request_callback)

    @requests_mock.Mocker()
    def test_version_discovery(self, mocker):
        _shell = shell.OpenStackCinderShell()

        os_auth_url = "https://WrongDiscoveryResponse.discovery.com:35357/v2.0"
        self.register_keystone_auth_fixture(mocker, os_auth_url)
        self.assertRaises(DiscoveryFailure, _shell._discover_auth_versions,
                          None, auth_url=os_auth_url)

        os_auth_url = "https://DiscoveryNotSupported.discovery.com:35357/v2.0"
        self.register_keystone_auth_fixture(mocker, os_auth_url)
        v2_url, v3_url = _shell._discover_auth_versions(
            None, auth_url=os_auth_url)
        self.assertEqual(v2_url, os_auth_url, "Expected v2 url")
        self.assertEqual(v3_url, None, "Expected no v3 url")

        os_auth_url = "https://DiscoveryNotSupported.discovery.com:35357/v3.0"
        self.register_keystone_auth_fixture(mocker, os_auth_url)
        v2_url, v3_url = _shell._discover_auth_versions(
            None, auth_url=os_auth_url)
        self.assertEqual(v3_url, os_auth_url, "Expected v3 url")
        self.assertEqual(v2_url, None, "Expected no v2 url")

    @requests_mock.Mocker()
    def test_cinder_version_legacy_endpoint_v1_and_v2(self, mocker):
        """Verify that legacy endpoint settings still work.

        Legacy endpoints that are not using version discovery is
        <hostname>:<port>/<version>/(tenant_id)s. For this unit test, we fill
        in the tenant_id for mocking purposes.
        """
        token = keystone_client_fixture.V2Token()
        cinder_url = 'http://127.0.0.1:8776/'

        volume_service = token.add_service('volume', 'Cinder v1')
        volume_service.add_endpoint(public=cinder_url, region='RegionOne')

        volumev2_service = token.add_service('volumev2', 'Cinder v2')
        volumev2_service.add_endpoint(public=cinder_url, region='RegionOne')

        mocker.post(keystone_client.BASE_HOST + '/v2.0/tokens',
                    json=token)
        mocker.get(cinder_url, json=fixture_base.generate_version_output())
        volume_request = mocker.get('http://127.0.0.1:8776/v1/volumes/detail',
                                    json={'volumes': {}})

        self.shell('list')
        self.assertTrue(volume_request.called)

    @requests_mock.Mocker()
    def test_cinder_version_legacy_endpoint_only_v1(self, mocker):
        """Verify that v1 legacy endpoint settings still work.

        Legacy endpoints that are not using version discovery is
        <hostname>:<port>/<version>/(tenant_id)s. For this unit test, we fill
        in the tenant_id for mocking purposes.
        """
        token = keystone_client_fixture.V2Token()
        cinder_url = 'http://127.0.0.1:8776/'

        volume_service = token.add_service('volume', 'Cinder v1')
        volume_service.add_endpoint(
            public=cinder_url,
            region='RegionOne'
        )

        mocker.get(
            cinder_url,
            json=fixture_base.generate_version_output(v1=True, v2=False)
        )
        mocker.post(keystone_client.BASE_HOST + '/v2.0/tokens',
                    json=token)
        volume_request = mocker.get('http://127.0.0.1:8776/v1/volumes/detail',
                                    json={'volumes': {}})

        self.shell('list')
        self.assertTrue(volume_request.called)

    @requests_mock.Mocker()
    def test_cinder_version_legacy_endpoint_only_v2(self, mocker):
        """Verify that v2 legacy endpoint settings still work.

        Legacy endpoints that are not using version discovery is
        <hostname>:<port>/<version>/(tenant_id)s. For this unit test, we fill
        in the tenant_id for mocking purposes.
        """
        token = keystone_client_fixture.V2Token()
        cinder_url = 'http://127.0.0.1:8776/'

        volumev2_service = token.add_service('volumev2', 'Cinder v2')
        volumev2_service.add_endpoint(
            public=cinder_url,
            region='RegionOne'
        )

        mocker.post(keystone_client.BASE_HOST + '/v2.0/tokens',
                    json=token)

        mocker.get(
            cinder_url,
            json=fixture_base.generate_version_output(v1=False, v2=True)
        )
        volume_request = mocker.get('http://127.0.0.1:8776/v2/volumes/detail',
                                    json={'volumes': {}})

        self.shell('list')
        self.assertTrue(volume_request.called)

    @requests_mock.Mocker()
    def test_cinder_version_discovery(self, mocker):
        """Verify client works two endpoints enabled under one service."""
        token = keystone_client_fixture.V2Token()

        volume_service = token.add_service('volume', 'Cinder')
        volume_service.add_endpoint(public='http://127.0.0.1:8776',
                                    region='RegionOne')

        mocker.post(keystone_client.BASE_HOST + '/v2.0/tokens',
                    json=token)
        mocker.get(
            'http://127.0.0.1:8776/',
            json=fixture_base.generate_version_output(v1=True, v2=True)
        )

        v1_request = mocker.get('http://127.0.0.1:8776/v1/volumes/detail',
                                json={'volumes': {}})
        v2_request = mocker.get('http://127.0.0.1:8776/v2/volumes/detail',
                                json={'volumes': {}})

        self.shell('list')
        self.assertTrue(v1_request.called)

        self.shell('--os-volume-api-version 2 list')
        self.assertTrue(v2_request.called)

    @requests_mock.Mocker()
    def test_cinder_version_discovery_only_v1(self, mocker):
        """Verify when v1 is only enabled, the client discovers it."""
        token = keystone_client_fixture.V2Token()

        volume_service = token.add_service('volume', 'Cinder')
        volume_service.add_endpoint(public='http://127.0.0.1:8776',
                                    region='RegionOne')

        mocker.post(keystone_client.BASE_HOST + '/v2.0/tokens',
                    json=token)
        mocker.get(
            'http://127.0.0.1:8776/',
            json=fixture_base.generate_version_output(v1=True, v2=True)
        )
        volume_request = mocker.get('http://127.0.0.1:8776/v1/volumes/detail',
                                    json={'volumes': {}})

        self.shell('list')
        self.assertTrue(volume_request.called)

    @requests_mock.Mocker()
    def test_cinder_version_discovery_only_v2(self, mocker):
        """Verify when v2 is enabled, the client discovers it."""
        token = keystone_client_fixture.V2Token()

        volumev2_service = token.add_service('volume', 'Cinder')
        volumev2_service.add_endpoint(public='http://127.0.0.1:8776',
                                      region='RegionOne')

        mocker.post(keystone_client.BASE_HOST + '/v2.0/tokens',
                    json=token)

        mocker.get(
            'http://127.0.0.1:8776/',
            json=fixture_base.generate_version_output(v1=False, v2=True)
        )
        volume_request = mocker.get('http://127.0.0.1:8776/v2/volumes/detail',
                                    json={'volumes': {}})

        self.shell('list')
        self.assertTrue(volume_request.called)

    @requests_mock.Mocker()
    def test_cinder_version_discovery_fallback(self, mocker):
        """Client defaults to v1, but v2 is only available, fallback to v2."""
        token = keystone_client_fixture.V2Token()

        volumev2_service = token.add_service('volumev2', 'Cinder v2')
        volumev2_service.add_endpoint(public='http://127.0.0.1:8776',
                                      region='RegionOne')

        mocker.post(keystone_client.BASE_HOST + '/v2.0/tokens',
                    json=token)

        mocker.get(
            'http://127.0.0.1:8776/',
            json=fixture_base.generate_version_output(v1=False, v2=True)
        )
        volume_request = mocker.get('http://127.0.0.1:8776/v2/volumes/detail',
                                    json={'volumes': {}})

        self.shell('list')
        self.assertTrue(volume_request.called)

    @requests_mock.Mocker()
    def test_cinder_version_discovery_unsupported_version(self, mocker):
        """Try a version from the client that's not enabled in Cinder."""
        token = keystone_client_fixture.V2Token()

        volume_service = token.add_service('volume', 'Cinder')
        volume_service.add_endpoint(public='http://127.0.0.1:8776',
                                    region='RegionOne')

        mocker.post(keystone_client.BASE_HOST + '/v2.0/tokens',
                    json=token)

        mocker.get(
            'http://127.0.0.1:8776/',
            json=fixture_base.generate_version_output(v1=False, v2=True)
        )

        self.assertRaises(exceptions.InvalidAPIVersion,
                          self.shell, '--os-volume-api-version 1 list')

    @mock.patch('sys.stdin', side_effect=mock.MagicMock)
    @mock.patch('getpass.getpass', return_value='password')
    def test_password_prompted(self, mock_getpass, mock_stdin):
        self.make_env(exclude='OS_PASSWORD')
        # We should get a Connection Refused because there is no keystone.
        self.assertRaises(ks_exc.ConnectionRefused, self.shell, 'list')
        # Make sure we are actually prompted.
        mock_getpass.assert_called_with('OS Password: ')

    @mock.patch.object(requests, "request")
    @mock.patch.object(pkg_resources, "iter_entry_points")
    def test_auth_system_not_keystone(self, mock_iter_entry_points,
                                      mock_request):
        """Test that we can authenticate using the auth plugin system."""
        non_keystone_auth_url = "http://non-keystone-url.com/v2.0"

        class MockEntrypoint(pkg_resources.EntryPoint):
            def load(self):
                return FakePlugin

        class FakePlugin(auth_plugin.BaseAuthPlugin):
            def authenticate(self, cls, auth_url):
                cls._authenticate(auth_url, {"fake": "me"})

            def get_auth_url(self):
                return non_keystone_auth_url

        mock_iter_entry_points.side_effect = lambda _t: [
            MockEntrypoint("fake", "fake", ["FakePlugin"])]

        mock_request.side_effect = mock_http_request()

        # Tell the shell we wish to use our 'fake' auth instead of keystone
        # and the auth plugin will provide the auth url
        self.make_env(exclude="OS_AUTH_URL",
                      include={'OS_AUTH_SYSTEM': 'fake'})
        # This should fail as we have not setup a mock response for 'list',
        # however auth should have been called
        _shell = shell.OpenStackCinderShell()
        self.assertRaises(KeyError, _shell.main, ['list'])

        headers = requested_headers(_shell.cs)
        token_url = _shell.cs.client.auth_url + "/tokens"
        self.assertEqual(non_keystone_auth_url + "/tokens", token_url)

        mock_request.assert_any_called(
            "POST",
            token_url,
            headers=headers,
            data='{"fake": "me"}',
            allow_redirects=True,
            **self.TEST_REQUEST_BASE)


class CinderClientArgumentParserTest(utils.TestCase):

    def test_ambiguity_solved_for_one_visible_argument(self):
        parser = shell.CinderClientArgumentParser(add_help=False)
        parser.add_argument('--test-parameter',
                            dest='visible_param',
                            action='store_true')
        parser.add_argument('--test_parameter',
                            dest='hidden_param',
                            action='store_true',
                            help=argparse.SUPPRESS)

        opts = parser.parse_args(['--test'])

        # visible argument must be set
        self.assertTrue(opts.visible_param)
        self.assertFalse(opts.hidden_param)

    def test_raise_ambiguity_error_two_visible_argument(self):
        parser = shell.CinderClientArgumentParser(add_help=False)
        parser.add_argument('--test-parameter',
                            dest="visible_param1",
                            action='store_true')
        parser.add_argument('--test_parameter',
                            dest="visible_param2",
                            action='store_true')

        self.assertRaises(SystemExit, parser.parse_args, ['--test'])

    def test_raise_ambiguity_error_two_hidden_argument(self):
        parser = shell.CinderClientArgumentParser(add_help=False)
        parser.add_argument('--test-parameter',
                            dest="hidden_param1",
                            action='store_true',
                            help=argparse.SUPPRESS)
        parser.add_argument('--test_parameter',
                            dest="hidden_param2",
                            action='store_true',
                            help=argparse.SUPPRESS)

        self.assertRaises(SystemExit, parser.parse_args, ['--test'])
