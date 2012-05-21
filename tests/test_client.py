
import cinderclient.client
import cinderclient.v1.client
from tests import utils


class ClientTest(utils.TestCase):

    def setUp(self):
        pass

    def test_get_client_class_v1(self):
        output = cinderclient.client.get_client_class('1')
        self.assertEqual(output, cinderclient.v1.client.Client)

    def test_get_client_class_unknown(self):
        self.assertRaises(cinderclient.exceptions.UnsupportedVersion,
                          cinderclient.client.get_client_class, '0')
