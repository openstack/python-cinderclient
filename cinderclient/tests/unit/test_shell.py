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
import mock
import pkg_resources
import requests_mock
import requests
from six import moves
from testtools import matchers

import cinderclient
from cinderclient import exceptions
from cinderclient import auth_plugin
from cinderclient import shell
from cinderclient.tests.unit.test_auth_plugins import mock_http_request
from cinderclient.tests.unit.test_auth_plugins import requested_headers
from cinderclient.tests.unit.fixture_data import keystone_client
from cinderclient.tests.unit import utils
import keystoneclient.exceptions as ks_exc
from keystoneclient.exceptions import DiscoveryFailure


class ShellTest(utils.TestCase):

    FAKE_ENV = {
        'OS_USERNAME': 'username',
        'OS_PASSWORD': 'password',
        'OS_TENANT_NAME': 'tenant_name',
        'OS_AUTH_URL': 'http://no.where/v2.0',
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
        self.assertIsNone(v3_url, "Expected no v3 url")

        os_auth_url = "https://DiscoveryNotSupported.discovery.com:35357/v3.0"
        self.register_keystone_auth_fixture(mocker, os_auth_url)
        v2_url, v3_url = _shell._discover_auth_versions(
            None, auth_url=os_auth_url)
        self.assertEqual(v3_url, os_auth_url, "Expected v3 url")
        self.assertIsNone(v2_url, "Expected no v2 url")

    @requests_mock.Mocker()
    def list_volumes_on_service(self, count, mocker):
        os_auth_url = "http://multiple.service.names/v2.0"
        mocker.register_uri('POST', os_auth_url + "/tokens",
                            text=keystone_client.keystone_request_callback)
        mocker.register_uri('GET',
                            "http://cinder%i.api.com/v2/volumes/detail"
                            % count, text='{"volumes": []}')
        self.make_env(include={'OS_AUTH_URL': os_auth_url,
                               'CINDER_SERVICE_NAME': 'cinder%i' % count})
        _shell = shell.OpenStackCinderShell()
        _shell.main(['list'])

    def test_cinder_service_name(self):
        # Failing with 'No mock address' means we are not
        # choosing the correct endpoint
        for count in range(1, 4):
            self.list_volumes_on_service(count)

    @mock.patch('keystoneclient.adapter.Adapter.get_token',
                side_effect=ks_exc.ConnectionRefused())
    @mock.patch('keystoneclient.discover.Discover',
                side_effect=ks_exc.ConnectionRefused())
    @mock.patch('sys.stdin', side_effect=mock.MagicMock)
    @mock.patch('getpass.getpass', return_value='password')
    def test_password_prompted(self, mock_getpass, mock_stdin, mock_discover,
                               mock_token):
        self.make_env(exclude='OS_PASSWORD')
        _shell = shell.OpenStackCinderShell()
        self.assertRaises(ks_exc.ConnectionRefused, _shell.main, ['list'])
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

        mock_request.assert_any_call(
            "POST",
            token_url,
            headers=headers,
            data='{"fake": "me"}',
            allow_redirects=True,
            **self.TEST_REQUEST_BASE)

    @mock.patch.object(cinderclient.client.HTTPClient, 'authenticate',
                       side_effect=exceptions.Unauthorized('No'))
    # Easiest way to make cinderclient use httpclient is a None session
    @mock.patch.object(cinderclient.shell.OpenStackCinderShell,
                       '_get_keystone_session', return_value=None)
    def test_http_client_insecure(self, mock_authenticate, mock_session):
        self.make_env(include={'CINDERCLIENT_INSECURE': True})

        _shell = shell.OpenStackCinderShell()

        # This "fails" but instantiates the client.
        self.assertRaises(exceptions.CommandError, _shell.main, ['list'])

        self.assertEqual(False, _shell.cs.client.verify_cert)

    @mock.patch('keystoneclient.session.Session.__init__',
                side_effect=RuntimeError())
    def test_http_client_with_cert(self, mock_session):
        _shell = shell.OpenStackCinderShell()

        # We crash the command after Session instantiation because this test
        # focuses only on arguments provided to Session.__init__
        args = '--os-cert', 'minnie', 'list'
        self.assertRaises(RuntimeError, _shell.main, args)
        mock_session.assert_called_once_with(cert='minnie', verify=mock.ANY)

    @mock.patch('keystoneclient.session.Session.__init__',
                side_effect=RuntimeError())
    def test_http_client_with_cert_and_key(self, mock_session):
        _shell = shell.OpenStackCinderShell()

        # We crash the command after Session instantiation because this test
        # focuses only on arguments provided to Session.__init__
        args = '--os-cert', 'minnie', '--os-key', 'mickey', 'list'
        self.assertRaises(RuntimeError, _shell.main, args)
        mock_session.assert_called_once_with(cert=('minnie', 'mickey'),
                                             verify=mock.ANY)


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
