from datetime import datetime
import stat
import ConfigParser
from StringIO import StringIO

import unittest

from climesync import util

from mock import patch, MagicMock


class UtilTest(unittest.TestCase):

    def test_ts_error_no_error(self):
        ts_objects = [{"example": "object"}]

        assert not util.ts_error(*ts_objects)

    def test_ts_error_error(self):
        ts_objects = [{"example": "object"}, {"error": 404}]

        assert util.ts_error(*ts_objects)

    @patch("climesync.util.codecs.open")
    @patch("climesync.util.os.chmod")
    @patch("climesync.util.os.path")
    def test_create_config_default_path(self, mock_path, mock_chmod,
                                        mock_open):
        default_path = "~/.climesyncrc"
        fullpath = "/path/to/config"
        open_args = ["w", "utf-8-sig"]
        chmod_args = [stat.S_IRUSR | stat.S_IWUSR]

        mock_path.expanduser.return_value = fullpath

        util.create_config(path=default_path)

        mock_open.assert_called_with(fullpath, *open_args)
        mock_chmod.assert_called_with(fullpath, *chmod_args)

    @patch("climesync.util.codecs.open")
    @patch("climesync.util.os.chmod")
    @patch("climesync.util.os.path")
    def test_create_config_provided_path(self, mock_path, mock_chmod,
                                         mock_open):
        provided_path = "~/.config/climesync/config"
        fullpath = "/path/to/config"
        open_args = ["w", "utf-8-sig"]
        chmod_args = [stat.S_IRUSR | stat.S_IWUSR]

        mock_path.expanduser.return_value = fullpath

        util.create_config(path=provided_path)

        mock_open.assert_called_with(fullpath, *open_args)
        mock_chmod.assert_called_with(fullpath, *chmod_args)

    @patch("climesync.util.ConfigParser.RawConfigParser")
    @patch("climesync.util.codecs.open")
    @patch("climesync.util.os.path")
    def test_read_config_path_exists(self, mock_path, mock_open, _):
        fullpath = "/path/to/config"

        mock_path.expanduser.return_value = fullpath
        mock_path.isfile.return_value = True

        mock_file = MagicMock()

        mock_open.return_value.__enter__.return_value = mock_file

        mock_configparser = util.read_config()

        mock_configparser.readfp.assert_called_with(mock_file)

    @patch("climesync.util.ConfigParser.RawConfigParser")
    @patch("climesync.util.os.path")
    def test_read_config_path_not_exist(self, mock_path, _):
        fullpath = "/path/to/config"

        mock_path.expanduser.return_value = fullpath
        mock_path.isfile.return_value = False

        mock_configparser = util.read_config()

        mock_configparser.read.assert_not_called()

    @patch("climesync.util.codecs.open")
    @patch("climesync.util.ConfigParser.RawConfigParser")
    @patch("climesync.util.os.path")
    def test_read_config_parsing_error(self, mock_path, mock_rawconfigparser,
                                       _):
        fullpath = "/path/to/config"

        mock_path.expanduser.return_value = fullpath
        mock_path.isfile.return_value = True

        mock_parser = MagicMock()
        mock_parser.readfp.side_effect = ConfigParser.ParsingError("")

        mock_rawconfigparser.return_value = mock_parser

        result = util.read_config()

        assert result is None

    @patch("climesync.util.create_config")
    @patch("climesync.util.read_config")
    @patch("climesync.util.codecs.open")
    def test_write_config_file_exists(self, mock_open, mock_read_config,
                                      mock_create_config):
        section_name = "climesync"
        path = "~/.climesyncrc"
        key = "key"
        value = "value"

        mock_config = MagicMock()
        mock_config.sections.return_value = [section_name]

        mock_file = MagicMock(spec=file)

        mock_open.return_value.__enter__.return_value = mock_file
        mock_read_config.return_value = mock_config

        util.write_config(key, value, path=path)

        mock_create_config.assert_not_called()
        mock_config.set.assert_called_with(section_name, key, value)
        mock_config.add_section.assert_not_called()
        mock_config.write.assert_called_with(mock_file)

    @patch("climesync.util.create_config")
    @patch("climesync.util.read_config")
    @patch("climesync.util.codecs.open")
    def test_write_config_file_not_exist(self, mock_open, mock_read_config,
                                         mock_create_config):
        section_name = "climesync"
        path = "~/.climesyncrc"
        key = "key"
        value = "value"

        mock_config = MagicMock()
        mock_config.sections.return_value = []
        mock_config.set.side_effect = [ConfigParser.NoSectionError(""), None]

        mock_read_config.return_value = mock_config

        util.write_config(key, value, path=path)

        mock_create_config.assert_called_with(path)
        mock_config.add_section.assert_called_with(section_name)

    @patch("climesync.util.create_config")
    @patch("climesync.util.read_config")
    def test_write_config_read_error(self, mock_read_config,
                                     mock_create_config):
        path = "~/.climesyncrc"
        key = "key"
        value = "value"

        mock_read_config.return_value = None

        util.write_config(key, value, path=path)

        mock_create_config.assert_not_called()

    @patch("climesync.util.os.path.exists")
    def test_session_exists_true(self, mock_exists):
        mock_exists.return_value = True

        assert util.session_exists()

    @patch("climesync.util.os.path.exists")
    def test_session_exists_false(self, mock_exists):
        mock_exists.return_value = False

        assert not util.session_exists()

    @patch("climesync.util.session_exists")
    @patch("climesync.util.codecs.open")
    def test_read_session(self, mock_open, mock_session_exists):
        mock_session_object = {
            "start_date": "2015-03-14",
            "start_time": "09:26",
            "project": "px",
            "issue_uri": "https://github.com/org/px/issues/42/",
            "user": "test"
        }

        mock_session_file_lines = [
            "start_date: 2015-03-14",
            "start_time: 09:26",
            "project: px",
            "issue_uri: https://github.com/org/px/issues/42/",
            "user: test"
        ]

        mock_file = MagicMock(spec=file)
        mock_file.readlines.return_value = mock_session_file_lines
        mock_open.return_value.__enter__.return_value = mock_file

        mock_session_exists.return_value = True

        result = util.read_session()

        assert result == mock_session_object

    @patch("climesync.util.session_exists")
    @patch("climesync.util.codecs.open")
    def test_read_session_no_session(self, mock_open, mock_session_exists):
        mock_session_exists.return_value = False

        util.read_session()

        assert not mock_open.mock_calls

    @patch("climesync.util.session_exists")
    @patch("climesync.util.codecs.open")
    def test_create_session(self, mock_open, mock_session_exists):
        mock_session_object = {
            "start_date": "2015-03-14",
            "start_time": "09:26",
            "project": "px",
            "issue_uri": "https://github.com/org/px/issues/42/",
            "user": "test"
        }

        mock_file = MagicMock(spec=file)
        mock_open.return_value.__enter__.return_value = mock_file

        mock_session_exists.return_value = False

        util.create_session(mock_session_object)

        for k, v in mock_session_object.iteritems():
            # Assert that the session data was written to the file
            assert any(k in args[0] and v in args[0]
                       for _, args, __ in mock_file.mock_calls)

    @patch("climesync.util.session_exists")
    @patch("climesync.util.codecs.open")
    def test_create_session_existing_session(self, mock_open,
                                             mock_session_exists):
        mock_session_exists.return_value = True

        util.create_session({})

        mock_open.assert_not_called()

    @patch("climesync.util.session_exists")
    @patch("climesync.util.os.remove")
    def test_clear_session(self, mock_remove, mock_session_exists):
        mock_session_exists.return_value = True

        util.clear_session()

        assert mock_remove.mock_calls

    @patch("climesync.util.session_exists")
    @patch("climesync.util.os.remove")
    def test_clear_session_no_session(self, mock_remove, mock_session_exists):
        mock_session_exists.return_value = False

        util.clear_session()

        assert not mock_remove.mock_calls

    def test_construct_clock_out_time(self):
        mocked_session = {
            "start_date": "2016-03-14",
            "start_time": "03:14",
            "project": "px",
            "activities": "dev docs",
            "user": "test"
        }

        mocked_now = datetime(2016, 3, 14, 4, 14)
        mocked_revisions = {"project": "py"}

        expected = {
            "duration": 3600,
            "date_worked": "2016-03-14",
            "project": "py",
            "activities": ["dev", "docs"],
            "user": "test"
        }

        result = util.construct_clock_out_time(mocked_session, mocked_now,
                                               mocked_revisions, None)

        assert result == expected

    def test_construct_clock_out_time_no_revisions(self):
        mocked_session = {
            "start_date": "2016-03-14",
            "start_time": "03:14",
            "project": "px",
            "activities": "dev docs",
            "user": "test"
        }

        mocked_now = datetime(2016, 3, 14, 4, 14)
        mocked_revisions = {}

        expected = {
            "duration": 3600,
            "date_worked": "2016-03-14",
            "project": "px",
            "activities": ["dev", "docs"],
            "user": "test"
        }

        result = util.construct_clock_out_time(mocked_session, mocked_now,
                                               mocked_revisions, None)

        assert result == expected

    def test_construct_clock_out_time_default_activity(self):
        mocked_session = {
            "start_date": "2016-03-14",
            "start_time": "03:14",
            "project": "px",
            "user": "test"
        }

        mocked_now = datetime(2016, 3, 14, 4, 14)
        mocked_revisions = {}
        mocked_project = {"default_activity": "dev"}

        expected = {
            "duration": 3600,
            "date_worked": "2016-03-14",
            "project": "px",
            "activities": ["dev"],
            "user": "test"
        }

        result = util.construct_clock_out_time(mocked_session, mocked_now,
                                               mocked_revisions,
                                               mocked_project)

        assert result == expected

    def test_construct_clock_out_time_invalid_project(self):
        mocked_session = {
            "start_date": "2016-03-14",
            "start_time": "03:14",
            "project": "px",
            "user": "test"
        }

        mocked_now = datetime(2016, 3, 14, 4, 14)
        mocked_revisions = {}
        mocked_project = {"error": "error"}

        result = util.construct_clock_out_time(mocked_session, mocked_now,
                                               mocked_revisions,
                                               mocked_project)

        assert result == {"error": "Invalid project"}

    def test_construct_clock_out_time_no_session(self):
        mocked_session = {}
        mocked_now = datetime.now()
        mocked_revisions = {}

        result = util.construct_clock_out_time(mocked_session, mocked_now,
                                               mocked_revisions, None)

        assert result == {"error": "No session data"}

    def test_construct_clock_out_time_invalid_session(self):
        mocked_session = {
            "invalid": "session"
        }

        mocked_now = datetime.now()
        mocked_revisions = {}

        result = util.construct_clock_out_time(mocked_session, mocked_now,
                                               mocked_revisions, None)

        assert result == {"error": "Invalid session data"}

    def test_construct_clock_out_time_negative_delta(self):
        mocked_session = {
            "start_date": "2016-03-14",
            "start_time": "03:14",
            "project": "px",
            "user": "test"
        }

        mocked_now = datetime(2016, 1, 1, 1, 1)
        mocked_revisions = {}

        result = util.construct_clock_out_time(mocked_session, mocked_now,
                                               mocked_revisions, None)

        assert result == {"error": "Invalid session date/time"}

    @patch("climesync.util.sys.stdout", new_callable=StringIO)
    def test_print_json_list(self, mock_stdout):
        key = "key"
        value = "value"

        test_response = [{key: value}]

        util.print_json(test_response)

        assert "{}: {}".format(key, value) in mock_stdout.getvalue()

    @patch("climesync.util.sys.stdout", new_callable=StringIO)
    def test_print_json_dict(self, mock_stdout):
        key = "key"
        value = "value"

        test_response = {key: value}

        util.print_json(test_response)

        assert "{}: {}".format(key, value) in mock_stdout.getvalue()

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

    @patch("climesync.util.raw_input")
    def test_get_field_string(self, mock_raw_input):
        prompt = "Prompt"
        expected_formatted_prompt = "Prompt: "

        mocked_input = "test input"

        mock_raw_input.return_value = mocked_input

        value = util.get_field(prompt)

        assert value == mocked_input
        mock_raw_input.assert_called_with(expected_formatted_prompt)

    @patch("climesync.util.raw_input")
    def test_get_field_string_empty(self, mock_raw_input):
        prompt = "Prompt"

        mocked_input = ["", "value"]

        mock_raw_input.side_effect = mocked_input

        value = util.get_field(prompt)

        assert value == mocked_input[1]
        assert mock_raw_input.call_count == 2

    @patch("climesync.util.raw_input")
    def test_get_field_string_optional(self, mock_raw_input):
        prompt = "Prompt"
        expected_formatted_prompt = "(Optional) Prompt: "

        mocked_input = ""

        mock_raw_input.return_value = mocked_input

        value = util.get_field(prompt, optional=True)

        assert value == ""
        mock_raw_input.assert_called_with(expected_formatted_prompt)

    @patch("climesync.util.raw_input")
    def test_get_field_string_validated(self, mock_raw_input):
        prompt = "Prompt"
        validator = ["v1", "v2"]

        mocked_input = "v1"

        mock_raw_input.return_value = mocked_input

        value = util.get_field(prompt, validator=validator)

        assert value == "v1"

    @patch("climesync.util.raw_input")
    def test_get_field_string_invalid(self, mock_raw_input):
        prompt = "Prompt"
        validator = ["v1", "v2"]

        mocked_input = ["v3", "v2"]

        mock_raw_input.side_effect = mocked_input

        value = util.get_field(prompt, validator=validator)

        assert value == "v2"

    @patch("climesync.util.raw_input")
    def test_get_field_bool_yes(self, mock_raw_input):
        prompt = "Prompt"
        expected_formatted_prompt = "(y/n) Prompt: "

        mocked_input = "Y"

        mock_raw_input.return_value = mocked_input

        value = util.get_field(prompt, field_type="?")

        assert value
        mock_raw_input.assert_called_with(expected_formatted_prompt)

    @patch("climesync.util.raw_input")
    def test_get_field_bool_no(self, mock_raw_input):
        prompt = "Prompt"

        mocked_input = "N"

        mock_raw_input.return_value = mocked_input

        value = util.get_field(prompt, field_type="?")

        assert not value

    @patch("climesync.util.raw_input")
    def test_get_field_bool_empty(self, mock_raw_input):
        prompt = "Prompt"

        mocked_input = ["", "yes"]

        mock_raw_input.side_effect = mocked_input

        value = util.get_field(prompt, field_type="?")

        assert value
        assert mock_raw_input.call_count == 2

    @patch("climesync.util.raw_input")
    def test_get_field_bool_invalid(self, mock_raw_input):
        prompt = "Prompt"

        mocked_input = ["maybe", "yes"]

        mock_raw_input.side_effect = mocked_input

        value = util.get_field(prompt, field_type="?")

        assert value
        assert mock_raw_input.call_count == 2

    @patch("climesync.util.raw_input")
    def test_get_field_bool_optional(self, mock_raw_input):
        prompt = "Prompt"
        expected_formatted_prompt = "(Optional) (y/N) Prompt: "

        mocked_input = ""

        mock_raw_input.return_value = mocked_input

        value = util.get_field(prompt, optional=True, field_type="?")

        assert value == ""
        mock_raw_input.assert_called_with(expected_formatted_prompt)

    @patch("climesync.util.raw_input")
    def test_get_field_time(self, mock_raw_input):
        prompt = "Prompt"
        expected_formatted_prompt = "(Time input - <value>h<value>m) Prompt: "

        mocked_input = "1h0m"

        mock_raw_input.return_value = mocked_input

        value = util.get_field(prompt, field_type=":")

        assert value == "1h0m"
        mock_raw_input.assert_called_with(expected_formatted_prompt)

    @patch("climesync.util.raw_input")
    def test_get_field_time_invalid(self, mock_raw_input):
        prompt = "Prompt"

        mocked_input = ["1 hour", "1h0m"]

        mock_raw_input.side_effect = mocked_input

        value = util.get_field(prompt, field_type=":")

        assert value == "1h0m"

    @patch("climesync.util.raw_input")
    def test_get_field_time_optional(self, mock_raw_input):
        prompt = "Prompt"
        expected_formatted_prompt = \
            "(Optional) (Time input - <value>h<value>m) Prompt: "

        mocked_input = ""

        mock_raw_input.return_value = mocked_input

        value = util.get_field(prompt, optional=True, field_type=":")

        assert value == ""
        mock_raw_input.assert_called_with(expected_formatted_prompt)

    @patch("climesync.util.raw_input")
    def test_get_field_list(self, mock_raw_input):
        prompt = "Prompt"
        expected_formatted_prompt = "(Comma delimited) Prompt: "

        mocked_input = " v1 ,   v2, v3,v4"

        mock_raw_input.return_value = mocked_input

        value = util.get_field(prompt, field_type="!")

        assert value == ["v1", "v2", "v3", "v4"]
        mock_raw_input.assert_called_with(expected_formatted_prompt)

    @patch("climesync.util.raw_input")
    def test_get_field_list_single_value(self, mock_raw_input):
        prompt = "Prompt"

        mocked_input = "v1"

        mock_raw_input.return_value = mocked_input

        value = util.get_field(prompt, field_type="!")

        assert value == ["v1"]

    @patch("climesync.util.raw_input")
    def test_get_field_list_empty(self, mock_raw_input):
        prompt = "Prompt"

        mocked_input = ["", "v1, v2"]

        mock_raw_input.side_effect = mocked_input

        value = util.get_field(prompt, field_type="!")

        assert value == ["v1", "v2"]

    @patch("climesync.util.raw_input")
    def test_get_field_list_optional(self, mock_raw_input):
        prompt = "Prompt"
        expected_formatted_prompt = "(Optional) (Comma delimited) Prompt: "

        mocked_input = ""

        mock_raw_input.return_value = mocked_input

        value = util.get_field(prompt, optional=True, field_type="!")

        assert value == ""
        mock_raw_input.assert_called_with(expected_formatted_prompt)

    @patch("climesync.util.raw_input")
    def test_get_field_list_validated(self, mock_raw_input):
        prompt = "Prompt"
        validator = ["v1", "v2", "v3"]

        mocked_input = "v1, v3"

        mock_raw_input.return_value = mocked_input

        value = util.get_field(prompt, field_type="!", validator=validator)

        assert value == ["v1", "v3"]

    @patch("climesync.util.raw_input")
    def test_get_field_list_invalid(self, mock_raw_input):
        prompt = "Prompt"
        validator = ["v1", "v2", "v3"]

        mocked_input = ["v1, v4, v2", "v1, v2"]

        mock_raw_input.side_effect = mocked_input

        value = util.get_field(prompt, field_type="!", validator=validator)

        assert value == ["v1", "v2"]

    @patch("climesync.util.raw_input")
    def test_get_field_type_invalid(self, mock_raw_input):
        prompt = "Prompt"

        value = util.get_field(prompt, field_type="invalid")

        assert value == ""

    @patch("climesync.util.get_field")
    def test_get_fields(self, mock_get_field):
        fields = [
            ("strval",       "String value", ["str", "val"]),
            ("*optstrval",   "Optional string value"),
            ("?boolval",     "Bool value"),
            ("*?optboolval", "Optional bool value"),
            (":timeval",     "Time value"),
            ("*:opttimeval", "Optional time value"),
            ("!listval",     "List value", ["val1", "val2", "val3"]),
            ("*!optlistval", "Optional list value")
        ]

        mocked_input = ["str", "", True, False, "1h0m", "0h30m",
                        ["val1", "val2"], []]

        expected_values = {
            "strval": "str",
            "boolval": True,
            "optboolval": False,
            "timeval": "1h0m",
            "opttimeval": "0h30m",
            "listval": ["val1", "val2"],
        }

        mock_get_field.side_effect = mocked_input

        values = util.get_fields(fields)

        assert values == expected_values

    @patch("climesync.util.get_field")
    @patch("climesync.util.read_config")
    def test_add_kv_pair_redundant(self, mock_read_config, mock_get_field):
        key = "redundant"
        value = "value"

        mock_config = MagicMock()
        mock_config.has_option.return_value = True
        mock_config.get.return_value = value

        mock_read_config.return_value = mock_config

        util.add_kv_pair(key, value)

        mock_get_field.assert_not_called()

    @patch("climesync.util.get_field")
    @patch("climesync.util.write_config")
    @patch("climesync.util.read_config")
    def test_add_kv_pair_no(self, mock_read_config, mock_write_config,
                            mock_get_field):
        key = "key"
        value = "value"
        path = "~/.climesyncrc"

        mock_config = MagicMock()
        mock_config.has_option.return_value = True
        mock_config.get.return_value = None

        mock_read_config.return_value = mock_config

        mock_get_field.return_value = False

        util.add_kv_pair(key, value, path)

        mock_write_config.assert_not_called()

    @patch("climesync.util.get_field")
    @patch("climesync.util.write_config")
    @patch("climesync.util.read_config")
    def test_add_kv_pair(self, mock_read_config, mock_write_config,
                         mock_get_field):
        key = "key"
        value = "value"
        path = "~/.climesyncrc"

        mock_config = MagicMock()
        mock_config.has_option.return_value = True
        mock_config.get.return_value = None

        mock_read_config.return_value = mock_config

        mock_get_field.return_value = True

        util.add_kv_pair(key, value, path)

        mock_write_config.assert_called_with(key, value, path)

    @patch("climesync.util.get_field")
    def test_get_user_permissions(self, mock_get_field):
        users = ["userone", "usertwo"]

        expected_permissions = {
            "userone": {
                "member": True,
                "spectator": False,
                "manager": False
            },
            "usertwo": {
                "member": True,
                "spectator": True,
                "manager": True
            }
        }

        mocked_input = [True, False, False,
                        True, True, True]

        mock_get_field.side_effect = mocked_input

        permissions = util.get_user_permissions(users)

        assert permissions == expected_permissions

    def test_get_user_permissions_empty(self):
        users = []

        permissions = util.get_user_permissions(users)

        assert not permissions

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

    def test_fix_args_optional(self):
        args = {
            "<angle_arg>": "value",
            "--long-opt": "[list values]",
            "UPPER_ARG": "True",
            "--duration": "300",
            "--blank-arg": None
        }

        expected_args = {
            "angle_arg": "value",
            "long_opt": ["list", "values"],
            "upper_arg": True,
            "duration": 300,
        }

        fixed_args = util.fix_args(args, True)

        print fixed_args
        print expected_args
        assert fixed_args == expected_args

    def test_fix_args_nonoptional(self):
        args = {
            "<angle_arg>": "value",
            "--long-opt": "[list values]",
            "UPPER_ARG": "True",
            "--duration": "300",
            "--blank-arg": None,
            "invalidarg": None
        }

        expected_args = {
            "angle_arg": "value",
            "long_opt": ["list", "values"],
            "upper_arg": True,
            "duration": 300,
            "blank_arg": None
        }

        fixed_args = util.fix_args(args, False)

        assert fixed_args == expected_args
