import unittest
import climesync


class ClimesyncTest(unittest.TestCase):

    def setUp(self):
        climesync.connect(test=True)

    def tearDown(self):
        climesync.disconnect()

    def test_connect(self):
        self.assertIsNotNone(climesync.ts)
        self.assertTrue(climesync.ts.test)

    def test_disconnect(self):
        climesync.disconnect()
        self.assertIsNone(climesync.ts)

    def test_sign_in(self):
        climesync.arg_username = "test-user"
        climesync.arg_password = "test-pass"

        climesync.disconnect()
        response = climesync.sign_in()
        self.assertIn("error", response)

        climesync.connect(test=True)
        response = climesync.sign_in()
        self.assertEqual(response["token"], "TESTTOKEN")
