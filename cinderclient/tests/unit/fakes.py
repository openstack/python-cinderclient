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

"""
A fake server that "responds" to API methods with pre-canned responses.

All of these responses come from the spec, so if for some reason the spec's
wrong the tests might raise AssertionError. I've indicated in comments the
places where actual behavior differs from the spec.
"""


def assert_has_keys(dict, required=None, optional=None):
    """
    Asserts that a dictionary exists.

    Args:
        dict: (todo): write your description
        required: (todo): write your description
        optional: (todo): write your description
    """
    required = required or []
    optional = optional or []

    for k in required:
        try:
            assert k in dict
        except AssertionError:
            extra_keys = set(dict).difference(set(required + optional))
            raise AssertionError("found unexpected keys: %s" %
                                 list(extra_keys))


class FakeClient(object):

    def _dict_match(self, partial, real):
        """
        Return true if the given partial match.

        Args:
            self: (todo): write your description
            partial: (dict): write your description
            real: (bool): write your description
        """

        result = True
        try:
            for key, value in partial.items():
                if isinstance(value, dict):
                    result = self._dict_match(value, real[key])
                else:
                    assert real[key] == value
                    result = True
        except (AssertionError, KeyError):
            result = False
        return result

    def assert_in_call(self, url_part):
        """Assert a call contained a part in its URL."""
        assert self.client.callstack, "Expected call but no calls were made"

        called = self.client.callstack[-1][1]
        assert url_part in called, 'Expected %s in call but found %s' % (
            url_part, called)

    def assert_called(self, method, url, body=None,
                      partial_body=None, pos=-1, **kwargs):
        """Assert than an API method was just called."""
        expected = (method, url)
        assert self.client.callstack, ("Expected %s %s but no calls "
                                       "were made." % expected)

        called = self.client.callstack[pos][0:2]

        assert expected == called, 'Expected %s %s; got %s %s' % (
            expected + called)

        if body is not None:
            actual_body = self.client.callstack[pos][2]
            assert actual_body == body, ("body mismatch. expected:\n" +
                                         str(body) + "\n" +
                                         "actual:\n" + str(actual_body))

        if partial_body is not None:
            try:
                assert self._dict_match(partial_body,
                                        self.client.callstack[pos][2])
            except AssertionError:
                print(self.client.callstack[pos][2])
                print("does not contain")
                print(partial_body)
                raise

    def assert_called_anytime(self, method, url, body=None, partial_body=None):
        """
        Assert than an API method was called anytime in the test.
        """
        expected = (method, url)

        assert self.client.callstack, ("Expected %s %s but no calls "
                                       "were made." % expected)

        found = False
        for entry in self.client.callstack:
            if expected == entry[0:2]:
                found = True
                break

        assert found, 'Expected %s %s; got %s' % (
            expected + (self.client.callstack, ))

        if body is not None:
            try:
                assert entry[2] == body
            except AssertionError:
                print(entry[2])
                print("!=")
                print(body)
                raise

        if partial_body is not None:
            try:
                assert self._dict_match(partial_body, entry[2])
            except AssertionError:
                print(entry[2])
                print("does not contain")
                print(partial_body)
                raise

    def clear_callstack(self):
        """
        Clears callstack.

        Args:
            self: (todo): write your description
        """
        self.client.callstack = []

    def authenticate(self):
        """
        Authenticate the request.

        Args:
            self: (todo): write your description
        """
        pass
