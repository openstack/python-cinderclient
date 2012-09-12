from cinderclient.v1 import volumes
from tests import utils
from tests.v1 import fakes


cs = fakes.FakeClient()


class VolumesTest(utils.TestCase):

    def test_delete_volume(self):
        v = cs.volumes.list()[0]
        v.delete()
        cs.assert_called('DELETE', '/volumes/1234')
        cs.volumes.delete('1234')
        cs.assert_called('DELETE', '/volumes/1234')
        cs.volumes.delete(v)
        cs.assert_called('DELETE', '/volumes/1234')

    def test_create_keypair(self):
        kp = cs.volumes.create(1)
        cs.assert_called('POST', '/volumes')

    def test_attach(self):
        v = cs.volumes.get('1234')
        cs.volumes.attach(v, 1, '/dev/vdc')
        cs.assert_called('POST', '/volumes/1234/action')

    def test_detach(self):
        v = cs.volumes.get('1234')
        cs.volumes.detach(v)
        cs.assert_called('POST', '/volumes/1234/action')

    def test_reserve(self):
        v = cs.volumes.get('1234')
        cs.volumes.reserve(v)
        cs.assert_called('POST', '/volumes/1234/action')

    def test_unreserve(self):
        v = cs.volumes.get('1234')
        cs.volumes.unreserve(v)
        cs.assert_called('POST', '/volumes/1234/action')

    def test_begin_detaching(self):
        v = cs.volumes.get('1234')
        cs.volumes.begin_detaching(v)
        cs.assert_called('POST', '/volumes/1234/action')

    def test_roll_detaching(self):
        v = cs.volumes.get('1234')
        cs.volumes.roll_detaching(v)
        cs.assert_called('POST', '/volumes/1234/action')

    def test_initialize_connection(self):
        v = cs.volumes.get('1234')
        cs.volumes.initialize_connection(v, {})
        cs.assert_called('POST', '/volumes/1234/action')

    def test_terminate_connection(self):
        v = cs.volumes.get('1234')
        cs.volumes.terminate_connection(v, {})
        cs.assert_called('POST', '/volumes/1234/action')
