import unittest
import shlex

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

    @test_script(data=test_data.create_time_data)
    def test_create_time(self, expected, result):
        assert result == expected

    @test_script(data=test_data.update_time_data)
    def test_update_time(self, expected, result):
        assert result == expected

    @test_script(data=test_data.get_times_no_uuid_data)
    def test_get_times_no_uuid(self, expected, result):
        assert result == expected

    @test_script(data=test_data.get_times_uuid_data)
    def test_get_times_uuid(self, expected, result):
        assert result == expected

    @test_script(data=test_data.sum_times_data)
    def test_sum_times(self, expected, result):
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
