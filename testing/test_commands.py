import unittest
from mock import patch, create_autospec

import commands
import util

from test_data import *


# test_command decorator
class test_command():
    
    def __init__(self, data=None):
        self.command = data.command
        self.mocked_input = data.mocked_input
        self.expected_response = data.expected_response
        self.admin = data.admin

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
        @patch("util.get_field")
        def wrapped_test(testcase, mock_get_field):
            commands.connect(config_dict=self.config, test=True)

            # Set up any additional mocks
            test(testcase)

            mock_get_field.side_effect = self.mocked_input

            if self.admin:
                self.authenticate_admin()
            else:
                self.authenticate_nonadmin()

            response = self.command()

            print response
            print self.expected_response
            assert response == self.expected_response

        return wrapped_test


class CommandsTest(unittest.TestCase):

    @test_command(data=create_time_data)
    def test_create_time(self):
        pass

    @test_command(data=update_time_data)
    def test_update_time(self):
        pass

    @test_command(data=get_times_no_uuid_data)
    def test_get_times_no_uuid(self):
        pass

    @test_command(data=get_times_uuid_data)
    def test_get_times_uuid(self):
        pass

    @test_command(data=sum_times_data)
    def test_sum_times(self):
        pass

    @test_command(data=delete_time_no_data)
    def test_delete_time_no(self):
        pass

    @test_command(data=delete_time_data)
    def test_delete_time(self):
        pass

    @test_command(data=create_project_data)
    def test_create_project(self):
        patcher = patch("util.get_user_permissions",
                        return_value=create_project_data.expected_response["users"])

        patcher.start()
        self.addCleanup(patcher.stop)

    @test_command(data=update_project_data)
    def test_update_project(self):
        patcher = patch("util.get_user_permissions",
                        return_value=update_project_data.expected_response["users"])

        patcher.start()
        self.addCleanup(patcher.stop)

    @test_command(data=get_projects_no_slug_data)
    def test_get_projects_no_slug(self):
        pass

    @test_command(data=get_projects_slug_data)
    def test_get_projects_slug(self):
        pass

    @test_command(data=delete_project_no_data)
    def test_delete_project_no(self):
        pass

    @test_command(data=delete_project_data)
    def test_delete_project(self):
        pass

    @test_command(data=create_activity_data)
    def test_create_activity(self):
        pass

    @test_command(data=update_activity_data)
    def test_update_activity(self):
        pass

    @test_command(data=get_activities_no_slug_data)
    def test_get_activities_no_slug(self):
        pass

    @test_command(data=get_activities_slug_data)
    def test_get_activities_slug(self):
        pass

    @test_command(data=delete_activity_no_data)
    def test_delete_activity_no(self):
        pass

    @test_command(data=delete_activity_data)
    def test_delete_activity(self):
        pass

    @test_command(data=create_user_data)
    def test_create_user(self):
        pass

    @test_command(data=update_user_data)
    def test_update_user(self):
        pass

    @test_command(data=get_users_no_slug_data)
    def test_get_users_no_slug(self):
        pass

    @test_command(data=get_users_slug_data)
    def test_get_users_slug(self):
        pass

    @test_command(data=delete_user_no_data)
    def test_delete_user_no(self):
        pass

    @test_command(data=delete_user_data)
    def test_delete_user(self):
        pass
