import unittest

from climesync import commands


class CommandsTest(unittest.TestCase):

    def setUp(self):
        self.config = {
            "timesync_url": "test",
            "username":     "test",
            "password":     "test"
        }

        commands.connect(config_dict=self.config, test=True)

    def tearDown(self):
        commands.disconnect()

    def authenticate_nonadmin(self):
        res = commands.sign_in(config_dict=self.config)

        return res

    def authenticate_admin(self):
        config_admin = dict(self.config)
        config_admin["username"] = "admin"

        res = commands.sign_in(config_dict=config_admin)

        return res

    def test_connect(self):
        self.assertIsNotNone(commands.ts)
        self.assertTrue(commands.ts.test)

    def test_disconnect(self):
        commands.disconnect()
        self.assertIsNone(commands.ts)

    def test_sign_in(self):
        commands.disconnect()
        res = self.authenticate_nonadmin()
        self.assertIn("error", res)

        commands.connect(config_dict=self.config, test=True)
        res = self.authenticate_nonadmin()
        self.assertEqual(res["token"], "TESTTOKEN")

    def test_sign_out(self):
        self.authenticate_nonadmin()

        self.assertIsNotNone(commands.ts.user)

        commands.sign_out()

        self.assertIsNone(commands.ts.user)
