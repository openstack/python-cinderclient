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

from requests import Response

from cinderclient import base
from cinderclient import exceptions
from cinderclient.openstack.common.apiclient import base as common_base
from cinderclient.v1 import volumes
from cinderclient.tests.unit import utils
from cinderclient.tests.unit.v1 import fakes


cs = fakes.FakeClient()


REQUEST_ID = 'req-test-request-id'


def create_response_obj_with_header():
    resp = Response()
    resp.headers['x-openstack-request-id'] = REQUEST_ID
    return resp


class BaseTest(utils.TestCase):

    def test_resource_repr(self):
        r = base.Resource(None, dict(foo="bar", baz="spam"))
        self.assertEqual("<Resource baz=spam, foo=bar>", repr(r))
        self.assertNotIn("x_openstack_request_ids", repr(r))

    def test_getid(self):
        self.assertEqual(4, base.getid(4))

        class TmpObject(object):
            id = 4
        self.assertEqual(4, base.getid(TmpObject))

    def test_eq(self):
        # Two resources with same ID: never equal if their info is not equal
        r1 = base.Resource(None, {'id': 1, 'name': 'hi'})
        r2 = base.Resource(None, {'id': 1, 'name': 'hello'})
        self.assertNotEqual(r1, r2)

        # Two resources with same ID: equal if their info is equal
        r1 = base.Resource(None, {'id': 1, 'name': 'hello'})
        r2 = base.Resource(None, {'id': 1, 'name': 'hello'})
        self.assertEqual(r1, r2)

        # Two resoruces of different types: never equal
        r1 = base.Resource(None, {'id': 1})
        r2 = volumes.Volume(None, {'id': 1})
        self.assertNotEqual(r1, r2)

        # Two resources with no ID: equal if their info is equal
        r1 = base.Resource(None, {'name': 'joe', 'age': 12})
        r2 = base.Resource(None, {'name': 'joe', 'age': 12})
        self.assertEqual(r1, r2)

    def test_findall_invalid_attribute(self):
        # Make sure findall with an invalid attribute doesn't cause errors.
        # The following should not raise an exception.
        cs.volumes.findall(vegetable='carrot')

        # However, find() should raise an error
        self.assertRaises(exceptions.NotFound,
                          cs.volumes.find,
                          vegetable='carrot')

    def test_to_dict(self):
        r1 = base.Resource(None, {'id': 1, 'name': 'hi'})
        self.assertEqual({'id': 1, 'name': 'hi'}, r1.to_dict())

    def test_resource_object_with_request_ids(self):
        resp_obj = create_response_obj_with_header()
        r = base.Resource(None, {"name": "1"}, resp=resp_obj)
        self.assertEqual([REQUEST_ID], r.request_ids)


class ListWithMetaTest(utils.TestCase):
    def test_list_with_meta(self):
        resp = create_response_obj_with_header()
        obj = common_base.ListWithMeta([], resp)
        self.assertEqual([], obj)
        # Check request_ids attribute is added to obj
        self.assertTrue(hasattr(obj, 'request_ids'))
        self.assertEqual([REQUEST_ID], obj.request_ids)


class DictWithMetaTest(utils.TestCase):
    def test_dict_with_meta(self):
        resp = create_response_obj_with_header()
        obj = common_base.DictWithMeta([], resp)
        self.assertEqual({}, obj)
        # Check request_ids attribute is added to obj
        self.assertTrue(hasattr(obj, 'request_ids'))
        self.assertEqual([REQUEST_ID], obj.request_ids)


class TupleWithMetaTest(utils.TestCase):
    def test_tuple_with_meta(self):
        resp = create_response_obj_with_header()
        obj = common_base.TupleWithMeta((), resp)
        self.assertEqual((), obj)
        # Check request_ids attribute is added to obj
        self.assertTrue(hasattr(obj, 'request_ids'))
        self.assertEqual([REQUEST_ID], obj.request_ids)
