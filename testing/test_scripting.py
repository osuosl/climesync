import unittest
import shlex

import commands


class ScriptingTest(unittest.TestCase):

    def setUp(self):
        commands.connect(test=True)

    def tearDown(self):
        commands.disconnect()

    def auth_admin(self):
        return commands.sign_in("admin", "test")

    def auth_nonadmin(self):
        return commands.sign_in("user", "test")

    def auth_configdict(self, config_dict):
        return commands.sign_in(config_dict=config_dict, interactive=False)

    def run_command(self, command, argv_str):
        return command(shlex.split(argv_str))

    def test_incomplete_config(self):
        complete_config = {
            "username": "user",
            "password": "test"
        }

        incomplete_config_username = {
            "username": "user"
        }

        incomplete_config_password = {
            "password": "test"
        }

        blank_config = {}

        response = self.auth_configdict(complete_config)
        self.assertNotIn("climesync error", response)

        response = self.auth_configdict(incomplete_config_username)
        self.assertIn("climesync error", response)

        response = self.auth_configdict(incomplete_config_password)
        self.assertIn("climesync error", response)

        response = self.auth_configdict(blank_config)
        self.assertIn("climesync error", response)

    def test_create_time(self):
        self.auth_nonadmin()
        response = self.run_command(commands.create_time,
                                    "0h2m proj_slug \"act1 act2\"")

        self.assertEqual(response["duration"], 120)
        self.assertEqual(response["project"], "proj_slug")
        self.assertEqual(response["activities"], ["act1", "act2"])

    def test_update_time(self):
        self.auth_nonadmin()
        response = self.run_command(commands.update_time,
                                    "uuid --duration=0h5m \
                                     --activities=\"act1 act2\"")

        self.assertEqual(response["duration"], 300)
        self.assertEqual(response["activities"], ["act1", "act2"])

    def test_get_times(self):
        self.auth_nonadmin()
        response = self.run_command(commands.get_times, "--end=2016-05-04")

        self.assertEqual(len(response), 3)

        response = self.run_command(commands.get_times, "--uuid=uuid")

        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]["uuid"], "uuid")

    def test_sum_times(self):
        self.auth_nonadmin()
        response = self.run_command(commands.sum_times,
                                    "proj_slug --start=2016-06-01")

        self.assertEqual(len(response), 0)

    def test_delete_time(self):
        self.auth_nonadmin()
        response = self.run_command(commands.delete_time, "uuid")

        self.assertEqual(response[0]["status"], 200)

    def test_create_project(self):
        self.auth_admin()
        response = self.run_command(commands.create_project,
                                    "name \"slug1 slug2\" userone 2 usertwo 5")

        self.assertEqual(response["name"], "name")
        self.assertEqual(response["slugs"], ["slug1", "slug2"])
        self.assertEqual(response["users"], {
            "userone": {
                "member": False,
                "spectator": True,
                "manager": False
            },
            "usertwo": {
                "member": True,
                "spectator": False,
                "manager": True
            }
        })

    def test_update_project(self):
        self.auth_admin()
        response = self.run_command(commands.update_project,
                                    "slug userone 6 usertwo 4 --name=newname")

        self.assertEqual(response["name"], "newname")
        # Commented out for now because of a Pymesync bug
#        self.assertEqual(response["users"], {
#            "userone": {
#                "member": True,
#                "spectator": True,
#                "manager": False
#            },
#            "usertwo": {
#                "member": True,
#                "spectator": False,
#                "manager": False
#            }
#        })

    def test_get_projects(self):
        self.auth_nonadmin()
        response = self.run_command(commands.get_projects, "")

        self.assertEqual(len(response), 3)

        response = self.run_command(commands.get_projects, "--slug=slug")

        self.assertEqual(len(response), 1)

    def test_delete_project(self):
        self.auth_admin()
        response = self.run_command(commands.delete_project, "slug")[0]

        self.assertIn("status", response)
        self.assertEqual(response["status"], 200)

    def test_create_activity(self):
        self.auth_admin()
        response = self.run_command(commands.create_activity, "name slug")

        self.assertEqual(response["name"], "name")
        self.assertEqual(response["slug"], "slug")

    def test_update_activity(self):
        self.auth_admin()
        response = self.run_command(commands.update_activity,
                                    "slug --name=newname --slug=newslug")

        self.assertEqual(response["name"], "newname")
        self.assertEqual(response["slug"], "newslug")

    def test_get_activities(self):
        self.auth_nonadmin()
        response = self.run_command(commands.get_activities,
                                    "--include-deleted=True")

        self.assertEqual(len(response), 3)

        response = self.run_command(commands.get_activities, "--slug=slug")

        self.assertEqual(len(response), 1)

        # Test that both --slug and --include-deleted isn't accepted

        response = self.run_command(commands.get_activities,
                                    "--slug=slug --include-deleted=True")

        self.assertIn("pymesync error", response[0])

    def test_delete_activity(self):
        self.auth_admin()
        response = self.run_command(commands.delete_activity, "slug")[0]

        self.assertIn("status", response)
        self.assertEqual(response["status"], 200)

    def test_create_user(self):
        self.auth_admin()
        response = self.run_command(commands.create_user,
                                    "username password \
                                     --email=testuser@osuosl.org \
                                     --site-admin=True")

        self.assertEqual(response["username"], "username")
        self.assertEqual(response["email"], "testuser@osuosl.org")
        self.assertEqual(response["site_admin"], True)

    def test_update_user(self):
        self.auth_admin()
        response = self.run_command(commands.update_user,
                                    "username --username=newname \
                                     --site-admin=True")

        self.assertEqual(response["username"], "newname")
        self.assertEqual(response["site_admin"], True)

    def test_get_users(self):
        self.auth_nonadmin()
        response = self.run_command(commands.get_users, "")

        self.assertEqual(len(response), 4)

        response = self.run_command(commands.get_users, "--username=user")

        self.assertEqual(len(response), 1)

    def test_delete_user(self):
        self.auth_admin()
        response = self.run_command(commands.delete_user, "user")[0]

        self.assertIn("status", response)
        self.assertEqual(response["status"], 200)
