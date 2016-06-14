import unittest
import shlex

from commands import *

class TestCLI(unittest.TestCase):

    def setUp(self):
        connect(test=True)

    def tearDown(self):
        disconnect()

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

    def test_update_time(self):
        self.auth_nonadmin()
        response = self.run_command(update_time, "uuid --duration=0h5m --activities=\"fdsa asdf\"")

        self.assertNotIn("pymesync error", response)

        self.assertEqual(response["duration"], 300)
        self.assertEqual(response["activities"], ["fdsa", "asdf"])

    def test_get_times(self):
        self.auth_nonadmin()
        response = self.run_command(get_times, "--end=2016-05-04")

        self.assertEqual(len(response), 3)

        response = self.run_command(get_times, "--uuid=uuid")

        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]["uuid"], "uuid")

    def test_sum_times(self):
        self.auth_nonadmin()
        response = self.run_command(sum_times, "test --start=2016-06-01")

        self.assertEqual(len(response), 0)

    def test_delete_time(self):
        self.auth_nonadmin()
        response = self.run_command(delete_time, "uuid")

        self.assertNotIn("pymesync error", response)

        self.assertEqual(response[0]["status"], 200)
