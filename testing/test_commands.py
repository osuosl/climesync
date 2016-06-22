import unittest
from mock import patch

import climesync
import commands


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

    def test_command_decorator(self):
        for command in [c[2] for c in climesync.command_lookup if c[1]]:
            self.assertEqual(command.__name__, "wrapped_command")

    @patch("util.get_field")
    def test_create_time(self, mock_get_field):
        expected_response = {
            "created_at": "2015-05-23",
            "updated_at": None,
            "deleted_at": None,
            "uuid": "838853e3-3635-4076-a26f-7efr4e60981f",
            "revision": 1,
            "duration": 3600,
            "project": "proj",
            "activities": ["act1", "act2"],
            "date_worked": "2016-05-04",
            "user": "test",
            "notes": "notes",
            "issue_uri": "Issue"
        }

        mock_get_field.side_effect = ["1h0m", "proj", ["act1", "act2"],
                                      "2016-05-04", "Issue", "notes"]

        self.authenticate_nonadmin()

        response = commands.create_time()

        self.assertEqual(response, expected_response)

    @patch("util.get_field")
    def test_update_time(self, mock_get_field):
        expected_response = {
            "created_at": "2014-06-12",
            "updated_at": "2015-10-18",
            "deleted_at": None,
            "uuid": "myuuid",
            "revision": 2,
            "duration": 7200,
            "project": "other_proj",
            "activities": ["other_act1", "other_act2"],
            "date_worked": "2016-06-20",
            "user": "other_user",
            "notes": "more notes",
            "issue_uri": "URI"
        }

        mock_get_field.side_effect = ["myuuid", "2h0m", "other_proj",
                                      "other_user",
                                      ["other_act1", "other_act2"],
                                      "2016-06-20", "URI", "more notes"]

        self.authenticate_nonadmin()

        response = commands.update_time()

        self.assertEqual(response, expected_response)

    @patch("util.get_field")
    def test_get_times_no_uuid(self, mock_get_field):
        expected_response = [{
            "created_at": "2014-04-17",
            "updated_at": None,
            "deleted_at": None,
            "uuid": "c3706e79-1c9a-4765-8d7f-89b4544cad56",
            "revision": 1,
            "duration": "0h0m",
            "project": ["ganeti-webmgr", "gwm"],
            "activities": ["docs", "planning"],
            "date_worked": "2014-04-17",
            "user": "userone",
            "notes": "Worked on documentation.",
            "issue_uri": "https://github.com/osuosl/ganeti_webmgr"
        },
        {
            "created_at": "2014-04-17",
            "updated_at": None,
            "deleted_at": None,
            "uuid": "12345676-1c9a-rrrr-bbbb-89b4544cad56",
            "revision": 1,
            "duration": "0h0m",
            "project": ["ganeti-webmgr", "gwm"],
            "activities": ["code", "planning"],
            "date_worked": "2014-04-17",
            "user": "usertwo",
            "notes": "Worked on coding",
            "issue_uri": "https://github.com/osuosl/ganeti_webmgr"
        },
        {
            "created_at": "2014-04-17",
            "updated_at": None,
            "deleted_at": None,
            "uuid": "12345676-1c9a-ssss-cccc-89b4544cad56",
            "revision": 1,
            "duration": "0h0m",
            "project": ["timesync", "ts"],
            "activities": ["code"],
            "date_worked": "2014-04-17",
            "user": "userthree",
            "notes": "Worked on coding",
            "issue_uri": "https://github.com/osuosl/timesync"
        }]

        mock_get_field.return_value = None

        self.authenticate_nonadmin()

        response = commands.get_times()

        self.assertEqual(response, expected_response)

    @patch("util.get_field")
    def test_get_times_uuid(self, mock_get_field):
        expected_response = [{
            "created_at": "2014-04-17",
            "updated_at": None,
            "deleted_at": None,
            "uuid": "myuuid",
            "revision": 1,
            "duration": "0h0m",
            "project": ["ganeti-webmgr", "gwm"],
            "activities": ["docs", "planning"],
            "date_worked": "2014-04-17",
            "user": "userone",
            "notes": "Worked on documentation.",
            "issue_uri": "https://github.com/osuosl/ganeti_webmgr"
        }]

        mock_get_field.side_effect = ["userone", ["gwm"], ["docs"],
                                      "2014-04-16", "2014-04-18", False, False,
                                      "myuuid"]

        self.authenticate_nonadmin()

        response = commands.get_times()

        self.assertEqual(response, expected_response)

    @patch("util.get_field")
    def test_delete_time_no(self, mock_get_field):
        expected_response = []

        mock_get_field.side_effect = ["uuid", False]

        self.authenticate_nonadmin()

        response = commands.delete_time()

        self.assertEqual(response, expected_response)

    @patch("util.get_field")
    def test_delete_time(self, mock_get_field):
        expected_response = [{
            "status": 200
        }]

        mock_get_field.side_effect = ["uuid", True]

        self.authenticate_nonadmin()

        response = commands.delete_time()

        self.assertEqual(response, expected_response)
