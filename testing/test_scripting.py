import datetime
import unittest
import shlex
from mock import patch

from climesync import commands

import test_data


class test_script():

    def __init__(self, data):
        self.command = data.command
        self.cli_args = data.cli_args
        self.expected_response = data.expected_response
        self.admin = data.admin

        self.config = {
            "timesync_url": "test",
            "username": "test",
            "password": "test",
            "ldap": False
        }

    def authenticate_nonadmin(self):
        res = commands.sign_in(config_dict=self.config)

        return res

    def authenticate_admin(self):
        config_admin = dict(self.config)
        config_admin["username"] = "admin"

        res = commands.sign_in(config_dict=config_admin)

        return res

    def run_command(self):
        return self.command(shlex.split(self.cli_args))

    def __call__(self, test):
        def test_wrapped(testcase):
            commands.connect(config_dict=self.config, test=True)

            if self.admin:
                self.authenticate_admin()
            else:
                self.authenticate_nonadmin()

            response = self.run_command()

            test(testcase, self.expected_response, response)

        return test_wrapped


class ScriptingTest(unittest.TestCase):

    @patch("climesync.util.session_exists")
    @patch("climesync.util.create_session")
    @patch("climesync.util.current_datetime")
    def test_clock_in(self, mock_now, mock_create_session,
                      mock_session_exists):
        mock_now.return_value = datetime.datetime(2015, 3, 14, 9, 26)

        mock_session_exists.return_value = False

        expected_session_object = {
            "start_date": "2015-03-14",
            "start_time": "09:26",
            "project": "px",
            "issue_uri": "https://github.com/org/px/issues/42/",
            "user": "test"
        }

        argv = ["px", "--issue-uri",
                "https://github.com/org/px/issues/42/"]

        commands.connect(arg_url="test", test=True)
        commands.sign_in(arg_user="test", arg_pass="test", arg_ldap=True)

        commands.clock_in(argv)

        mock_create_session.assert_called_with(expected_session_object)

    @patch("climesync.util.session_exists")
    @patch("climesync.util.create_session")
    def test_clock_in_already_clocked_in(self, mock_create_session,
                                         mock_session_exists):
        mock_session_exists.return_value = True

        argv = ["px"]

        commands.connect(arg_url="test", test=True)
        commands.sign_in(arg_user="test", arg_pass="test", arg_ldap=True)

        commands.clock_in(argv)

        mock_create_session.assert_not_called()

    @patch("climesync.util.session_exists")
    @patch("climesync.util.read_session")
    @patch("climesync.util.clear_session")
    @patch("climesync.util.current_datetime")
    def test_clock_out(self, mock_now, mock_clear_session, mock_read_session,
                       mock_session_exists):
        mocked_session = {
            "start_date": "2015-03-14",
            "start_time": "09:26",
            "project": "px",
            "issue_uri": "https://github.com/org/px/issues/42/",
            "user": "test"
        }

        mock_now.return_value = datetime.datetime(2015, 3, 14, 10, 26)

        mock_read_session.return_value = mocked_session

        mock_session_exists.return_value = True

        argv = ["--activities", "development planning", "--notes",
                "Fixed issue X by doing Y"]

        expected_response = {
            "created_at": "2015-05-23",
            "updated_at": None,
            "deleted_at": None,
            "uuid": "838853e3-3635-4076-a26f-7efr4e60981f",
            "revision": 1,
            "duration": 3600,
            "project": "px",
            "activities": ["development", "planning"],
            "date_worked": "2015-03-14",
            "user": "test",
            "notes": "Fixed issue X by doing Y",
            "issue_uri": "https://github.com/org/px/issues/42/"
        }

        commands.connect(arg_url="test", test=True)
        commands.sign_in(arg_user="test", arg_pass="test", arg_ldap=True)

        response = commands.clock_out(argv)

        assert response == expected_response

    @patch("climesync.util.current_datetime")
    @patch("climesync.util.session_exists")
    @patch("climesync.util.read_session")
    def test_clock_out_no_clock_in(self, mock_read_session,
                                   mock_session_exists, mock_now):
        mock_session_exists.return_value = False

        mock_now.return_value = datetime.datetime(2015, 3, 14, 9, 26)

        argv = ""

        commands.connect(arg_url="test", test=True)
        commands.sign_in(arg_user="test", arg_pass="test", arg_ldap=True)

        commands.clock_out(argv)

        mock_read_session.assert_not_called()

    @test_script(data=test_data.create_time_data)
    def test_create_time(self, expected, result):
        assert result == expected

    @test_script(data=test_data.update_time_data)
    def test_update_time(self, expected, result):
        assert result == expected

    @test_script(data=test_data.get_times_no_uuid_data)
    def test_get_times_no_uuid(self, expected, result):
        print result
        print expected
        assert result == expected

    @test_script(data=test_data.get_times_uuid_data)
    def test_get_times_uuid(self, expected, result):
        assert result == expected

    @test_script(data=test_data.delete_time_data)
    def test_delete_time(self, expected, result):
        assert result == expected

    @test_script(data=test_data.create_project_data)
    def test_create_project(self, expected, result):
        assert result == expected

    @test_script(data=test_data.update_project_data)
    def test_update_project(self, expected, result):
        assert result == expected

    @test_script(data=test_data.get_projects_no_slug_data)
    def test_get_projects_no_slug(self, expected, result):
        assert result == expected

    @test_script(data=test_data.get_projects_slug_data)
    def test_get_projects_slug(self, expected, result):
        assert result == expected

    @test_script(data=test_data.delete_project_data)
    def test_delete_project(self, expected, result):
        assert result == expected

    @test_script(data=test_data.create_activity_data)
    def test_create_activity(self, expected, result):
        assert result == expected

    @test_script(data=test_data.update_activity_data)
    def test_update_activity(self, expected, result):
        assert result == expected

    @test_script(data=test_data.get_activities_no_slug_data)
    def test_get_activities_no_slug(self, expected, result):
        assert result == expected

    @test_script(data=test_data.get_activities_slug_data)
    def test_get_activities_slug(self, expected, result):
        assert result == expected

    @test_script(data=test_data.delete_activity_data)
    def test_delete_activity(self, expected, result):
        assert result == expected

    @test_script(data=test_data.create_user_data)
    def test_create_user(self, expected, result):
        assert result == expected

    @test_script(data=test_data.update_user_data)
    def test_update_user(self, expected, result):
        assert result == expected

    @test_script(data=test_data.get_users_no_slug_data)
    def test_get_users_no_slug(self, expected, result):
        assert result == expected

    @test_script(data=test_data.get_users_slug_data)
    def test_get_users_slug(self, expected, result):
        assert result == expected

    @test_script(data=test_data.delete_user_data)
    def test_delete_user(self, expected, result):
        assert result == expected
