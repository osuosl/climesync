import unittest

import commands
from commands import *


class CommandsTest(unittest.TestCase):

    def setUp(self):
        self.config = {
            "timesync_url": "test",
            "username":     "test",
            "password":     "test"
        }

        connect(config_dict=self.config, test=True)

    def tearDown(self):
        disconnect()

    def authenticate_nonadmin(self):
        res = sign_in(config_dict=self.config)

        return res

    def authenticate_admin(self):
        config_admin = dict(self.config)
        config_admin["username"] = "admin"

        res = sign_in(config_dict=config_nonadmin)

        return res

    def test_connect(self):
        global ts

        self.assertIsNotNone(commands.ts)
        self.assertTrue(commands.ts.test)

    def test_disconnect(self):
        disconnect()
        self.assertIsNone(ts)

    def test_sign_in(self):
        disconnect()
        res = self.authenticate_nonadmin()
        self.assertIn("error", res)

        connect(config_dict=self.config, test=True)
        res = self.authenticate_nonadmin()
        self.assertEqual(res["token"], "TESTTOKEN")

    def test_sign_out(self):
        res = self.authenticate_nonadmin()

        self.assertIsNotNone(commands.ts.user)

        sign_out()

        self.assertIsNone(commands.ts.user)
