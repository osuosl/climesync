import unittest
import climesync


class ClimesyncTest(unittest.TestCase):

    def setUp(self):
        self.config = {"timesync_url": "test",
                       "username":     "test",
                       "password":     "test"}

        climesync.connect(config_dict=self.config, test=True)

    def tearDown(self):
        climesync.disconnect()

    def test_connect(self):
        self.assertIsNotNone(climesync.ts)
        self.assertTrue(climesync.ts.test)

    def test_disconnect(self):
        climesync.disconnect()
        self.assertIsNone(climesync.ts)

    def test_sign_in(self):
        climesync.disconnect()
        response = climesync.sign_in(config_dict=self.config)
        self.assertIn("error", response)

        climesync.connect(config_dict=self.config, test=True)
        response = climesync.sign_in(config_dict=self.config)
        self.assertEqual(response["token"], "TESTTOKEN")
