import unittest
import commands


class ClimesyncTest(unittest.TestCase):

    def setUp(self):
        self.config = {"timesync_url": "test",
                       "username":     "test",
                       "password":     "test"}

        commands.connect(config_dict=self.config, test=True)

    def tearDown(self):
        commands.disconnect()

    def test_connect(self):
        self.assertIsNotNone(commands.ts)
        self.assertTrue(commands.ts.test)

    def test_disconnect(self):
        commands.disconnect()
        self.assertIsNone(commands.ts)

    def test_sign_in(self):
        commands.disconnect()
        response = commands.sign_in(config_dict=self.config)
        self.assertIn("error", response)

        commands.connect(config_dict=self.config, test=True)
        response = commands.sign_in(config_dict=self.config)
        self.assertEqual(response["token"], "TESTTOKEN")
