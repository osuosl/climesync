import unittest

from climesync import util


class UtilTest(unittest.TestCase):

    def test_is_time(self):
        self.assertFalse(util.is_time("AhBm"))
        self.assertFalse(util.is_time("hm"))
        self.assertFalse(util.is_time("4h"))
        self.assertFalse(util.is_time("10m"))
        self.assertFalse(util.is_time("4hm"))
        self.assertFalse(util.is_time("h4m"))
        self.assertFalse(util.is_time("A4h10m"))
        self.assertFalse(util.is_time("4h10mA"))
        self.assertFalse(util.is_time("4h1A0m"))
        self.assertFalse(util.is_time("4.0h10m"))

        self.assertTrue(util.is_time("4h10m"))
        self.assertTrue(util.is_time("222355h203402340m"))
        self.assertTrue(util.is_time("0h10m"))

    def test_to_readable_time(self):
        self.assertEqual(util.to_readable_time(60), "0h1m")
        self.assertEqual(util.to_readable_time(3600), "1h0m")
        self.assertEqual(util.to_readable_time(1000), "0h16m")

    def test_fix_user_permissions(self):
        permissions = {
            "userzero": "0",
            "userone": "1",
            "usertwo": "2",
            "userthree": "3",
            "userfour": "4",
            "userfive": "5",
            "usersix": "6",
            "userseven": "7"
        }

        fixed_permissions = {
            "userzero": {"member": False, "spectator": False,
                         "manager": False},
            "userone": {"member": False, "spectator": False, "manager": True},
            "usertwo": {"member": False, "spectator": True, "manager": False},
            "userthree": {"member": False, "spectator": True, "manager": True},
            "userfour": {"member": True, "spectator": False, "manager": False},
            "userfive": {"member": True, "spectator": False, "manager": True},
            "usersix": {"member": True, "spectator": True, "manager": False},
            "userseven": {"member": True, "spectator": True, "manager": True}
        }

        fixed = util.fix_user_permissions(permissions)

        self.assertEqual(fixed, fixed_permissions)

    def test_fix_args(self):
        args = {
            "<angle_arg>": "value",
            "--long-opt": "[list values]",
            "UPPER_ARG": "True",
            "--duration": "300",
            "--blank-arg": None
        }

        fixed_args_nonoptional = {
            "angle_arg": "value",
            "long_opt": ["list", "values"],
            "upper_arg": True,
            "duration": 300,
            "blank_arg": None
        }

        fixed_args_optional = dict(fixed_args_nonoptional)
        del(fixed_args_optional["blank_arg"])

        nonoptional = util.fix_args(args, False)
        optional = util.fix_args(args, True)

        self.assertEqual(nonoptional, fixed_args_nonoptional)
        self.assertEqual(optional, fixed_args_optional)
