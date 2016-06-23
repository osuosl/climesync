import unittest
from mock import patch, create_autospec

import commands
import util

from test_data import *


# test_command decorator
class test_command():
    
    def __init__(self, command=None, data=None):
        self.command = command
        self.mocked_input = data.mocked_input
        self.expected_response = data.expected_response
        self.admin = data.admin
        self.data = data

        self.config = {
            "timesync_url": "test",
            "username": "test",
            "password": "test"
        }

    def authenticate_nonadmin(self):
        res = commands.sign_in(config_dict=self.config)

        return res

    def authenticate_admin(self):
        config_admin = dict(self.config)
        config_admin["username"] = "admin"

        res = commands.sign_in(config_dict=config_admin)

        return res

    def __call__(self, test):
        @patch("util.get_user_permissions")
        @patch("util.get_field")
        def test_wrapped(testcase, mock_get_field=None,
                         mock_get_user_permissions=None):
            commands.connect(config_dict=self.config, test=True)

            # Set up mocks
            if "users" in self.expected_response:
                mock_get_user_permissions.return_value = \
                        self.expected_response["users"]

            mock_get_field.side_effect = self.mocked_input

            # Authenticate with TimeSync
            if self.admin:
                self.authenticate_admin()
            else:
                self.authenticate_nonadmin()

            # Run the command and perform the test
            response = self.command()

            test(testcase, self.data, response)

        return test_wrapped


class CommandsTest(unittest.TestCase):

    @test_command(command=commands.create_time, data=create_time_data)
    def test_create_time(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.update_time, data=update_time_data)
    def test_update_time(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.get_times, data=get_times_no_uuid_data)
    def test_get_times_no_uuid(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.get_times, data=get_times_uuid_data)
    def test_get_times_uuid(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.sum_times, data=sum_times_data)
    def test_sum_times(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.delete_time, data=delete_time_no_data)
    def test_delete_time_no(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.delete_time, data=delete_time_data)
    def test_delete_time(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.create_project, data=create_project_data)
    def test_create_project(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.update_project, data=update_project_data)
    def test_update_project(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.get_projects, data=get_projects_no_slug_data)
    def test_get_projects_no_slug(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.get_projects, data=get_projects_slug_data)
    def test_get_projects_slug(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.delete_project, data=delete_project_no_data)
    def test_delete_project_no(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.delete_project, data=delete_project_data)
    def test_delete_project(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.create_activity, data=create_activity_data)
    def test_create_activity(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.update_activity, data=update_activity_data)
    def test_update_activity(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.get_activities, data=get_activities_no_slug_data)
    def test_get_activities_no_slug(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.get_activities, data=get_activities_slug_data)
    def test_get_activities_slug(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.delete_activity, data=delete_activity_no_data)
    def test_delete_activity_no(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.delete_activity, data=delete_activity_data)
    def test_delete_activity(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.create_user, data=create_user_data)
    def test_create_user(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.update_user, data=update_user_data)
    def test_update_user(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.get_users, data=get_users_no_slug_data)
    def test_get_users_no_slug(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.get_users, data=get_users_slug_data)
    def test_get_users_slug(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.delete_user, data=delete_user_no_data)
    def test_delete_user_no(self, data, result):
        assert result == data.expected_response

    @test_command(command=commands.delete_user, data=delete_user_data)
    def test_delete_user(self, data, result):
        assert result == data.expected_response
