import unittest
import shlex

from commands import *

class TestCLI(unittest.TestCase):

    def setUp(self):
        connect(test=True)

    def auth_admin(self):
        sign_in("admin", "test")

    def auth_nonadmin(self):
        sign_in("user", "test")

    def run_command(self, command, argv_str):
        return command(shlex.split(argv_str))

    def test_create_time(self):
        self.auth_nonadmin()
        response = self.run_command(create_time, "120 test \"asdf fdsa\"")

        self.assertNotIn("pymesync error", response)

        self.assertEqual(response["duration"], 120)
        self.assertEqual(response["project"], "test")
        self.assertEqual(response["activities"], ["asdf", "fdsa"])
