from StringIO import StringIO
import unittest
from mock import call, patch, MagicMock

from climesync import climesync
from climesync.climesync import command_lookup
from climesync import commands


class ClimesyncTest(unittest.TestCase):

    def test_lookup_command_interactive(self):
        test_queries = [
            ("ct", 4)
        ]

        for query, actual in test_queries:
            command = command_lookup[actual][2]

            assert climesync.lookup_command(query, 0) == command

    def test_lookup_command_scripting(self):
        test_queries = [
            ("create-time", 4)
        ]

        for query, actual in test_queries:
            command = command_lookup[actual][2]

            assert climesync.lookup_command(query, 1) == command

    def test_lookup_command_invalid(self):
        query = "invalid"

        assert not climesync.lookup_command(query, 0)

    @patch("climesync.commands.util")
    @patch("climesync.commands.pymesync.TimeSync")
    def test_connect_arg_url(self, mock_timesync, mock_util):
        baseurl = "ts_url"

        commands.connect(arg_url=baseurl)

        mock_util.add_kv_pair.assert_called_with("timesync_url", baseurl)
        mock_timesync.assert_called_with(baseurl=baseurl, test=False)

        commands.ts = None

    @patch("climesync.commands.util")
    @patch("climesync.commands.pymesync.TimeSync")
    def test_connect_config_dict(self, mock_timesync, mock_util):
        baseurl = "ts_url"
        config_dict = {"timesync_url": baseurl}

        commands.connect(config_dict=config_dict)

        mock_util.add_kv_pair.assert_called_with("timesync_url", baseurl)
        mock_timesync.assert_called_with(baseurl=baseurl, test=False)

        commands.ts = None

    @patch("climesync.commands.util")
    @patch("climesync.commands.pymesync.TimeSync")
    def test_connect_interactive(self, mock_timesync, mock_util):
        baseurl = "ts_url"

        mock_util.get_field.return_value = baseurl

        commands.connect()

        mock_util.add_kv_pair.assert_called_with("timesync_url", baseurl)
        mock_timesync.assert_called_with(baseurl=baseurl, test=False)

        commands.ts = None

    @patch("climesync.commands.util")
    @patch("climesync.commands.pymesync.TimeSync")
    def test_connect_noninteractive(self, mock_timesync, mock_util):
        baseurl = "ts_url"

        commands.connect(arg_url=baseurl, interactive=False)

        mock_util.add_kv_pair.assert_not_called()
        mock_timesync.assert_called_with(baseurl=baseurl, test=False)

        commands.ts = None

    def test_disconnect(self):
        commands.ts = MagicMock()

        commands.disconnect()

        assert not commands.ts

    @patch("climesync.commands.util")
    @patch("climesync.commands.ts")
    def test_sign_in_args(self, mock_ts, mock_util):
        username = "test"
        password = "password"

        mock_ts.test = False

        commands.sign_in(arg_user=username, arg_pass=password)

        mock_util.add_kv_pair.assert_has_calls([call("username", username),
                                                call("password", password)])
        mock_ts.authenticate.assert_called_with(username, password, "password")

    @patch("climesync.commands.util")
    @patch("climesync.commands.ts")
    def test_sign_in_config_dict(self, mock_ts, mock_util):
        username = "test"
        password = "password"
        config_dict = {"username": username, "password": password}

        mock_ts.test = False

        commands.sign_in(config_dict=config_dict)

        mock_util.add_kv_pair.assert_has_calls([call("username", username),
                                                call("password", password)])
        mock_ts.authenticate.assert_called_with(username, password, "password")

    @patch("climesync.commands.util")
    @patch("climesync.commands.ts")
    def test_sign_in_interactive(self, mock_ts, mock_util):
        username = "test"
        password = "test"
        mocked_input = [username, password]

        mock_util.get_field.side_effect = mocked_input
        mock_ts.test = False

        commands.sign_in()

        mock_util.add_kv_pair.assert_has_calls([call("username", username),
                                                call("password", password)])
        mock_ts.authenticate.assert_called_with(username, password, "password")

    @patch("climesync.commands.util")
    @patch("climesync.commands.ts")
    def test_sign_in_noninteractive(self, mock_ts, mock_util):
        username = "test"
        password = "test"

        mock_ts.test = False

        commands.sign_in(arg_user=username, arg_pass=password,
                         interactive=False)

        mock_util.add_kv_pair.assert_not_called()
        mock_ts.authenticate.assert_called_with(username, password, "password")

    def test_sign_in_not_connected(self):
        commands.ts = None

        response = commands.sign_in()

        assert "error" in response

    @patch("climesync.commands.ts")
    def test_sign_in_error(self, mock_ts):
        response = commands.sign_in(interactive=False)

        assert "climesync error" in response

    @patch("climesync.commands.ts")
    @patch("climesync.commands.pymesync.TimeSync")
    def test_sign_out(self, mock_timesync, mock_ts):
        url = "ts_url"
        test = False

        mock_ts.baseurl = url
        mock_ts.test = test

        commands.sign_out()

        mock_timesync.assert_called_with(baseurl=url, test=test)

    def test_sign_out_not_connected(self):
        commands.ts = None

        response = commands.sign_out()

        assert "error" in response

    @patch("climesync.climesync.commands")
    @patch("climesync.climesync.interactive_mode")
    def test_start_interactive(self, mock_interactive_mode, mock_commands):
        argv = []

        climesync.main(argv=argv)

        mock_interactive_mode.assert_called_with()

    @patch("climesync.climesync.commands")
    @patch("climesync.climesync.scripting_mode")
    def test_start_scripting(self, mock_scripting_mode, mock_commands):
        command = "create-time"
        argv = [command]

        climesync.main(argv=argv)

        mock_scripting_mode.assert_called_with("create-time", [])

    @patch("climesync.climesync.util")
    @patch("climesync.climesync.commands")
    @patch("climesync.climesync.interactive_mode")
    def test_connect_args(self, mock_interactive_mode, mock_commands,
                          mock_util):
        baseurl = "ts_url"
        username = "test"
        password = "password"
        argv = ["-c", baseurl, "-u", username, "-p", password]

        config_dict = {}

        mock_config = MagicMock()
        mock_config.items.return_value = config_dict

        mock_util.read_config.return_value = mock_config

        climesync.main(argv=argv, test=True)

        mock_commands.connect.assert_called_with(arg_url=baseurl,
                                                 config_dict=config_dict,
                                                 interactive=True,
                                                 test=True)
        mock_commands.sign_in.assert_called_with(arg_user=username,
                                                 arg_pass=password,
                                                 config_dict=config_dict,
                                                 interactive=True)
        mock_interactive_mode.assert_called_with()

    @patch("climesync.climesync.util")
    @patch("climesync.climesync.lookup_command")
    def test_menu_command(self, mock_lookup_command, mock_util):
        command = "ct"
        command_result = {}

        mock_command = MagicMock()
        mock_command.return_value = command_result

        mock_lookup_command.return_value = mock_command

        mock_util.get_field.return_value = command

        result = climesync.menu()

        assert result
        mock_util.print_pretty.assert_called_with(command_result)

    @patch("climesync.climesync.util")
    @patch("climesync.climesync.sys.stdout", new_callable=StringIO)
    def test_menu_help(self, mock_stdout, mock_util):
        command = "h"

        mock_util.get_field.return_value = command

        result = climesync.menu()

        assert result
        assert climesync.menu_options in mock_stdout.getvalue()

    @patch("climesync.climesync.util")
    def test_menu_quit(self, mock_util):
        command = "q"

        mock_util.get_field.return_value = command

        result = climesync.menu()

        assert not result

    @patch("climesync.climesync.util")
    @patch("climesync.climesync.sys.stdout", new_callable=StringIO)
    def test_menu_invalid(self, mock_stdout, mock_util):
        command = "invalid"

        mock_util.get_field.return_value = command

        result = climesync.menu()

        assert result
        assert "Invalid choice!" in mock_stdout.getvalue()

    @patch("climesync.climesync.scripting_mode")
    @patch("climesync.climesync.util.read_config")
    def test_main_use_config(self, mock_read_config, mock_scripting_mode):
        baseurl = "ts_url"
        username = "test"
        password = "password"
        argv = ["command"]

        config_dict = {
            "timesync_url": baseurl,
            "username": username,
            "password": password,
        }

        mock_config = MagicMock()
        mock_config.items.return_value = config_dict

        mock_read_config.return_value = mock_config

        climesync.main(argv=argv, test=True)

        mock_scripting_mode.assert_called_with("command", [])

    @patch("climesync.climesync.util")
    def test_connect_error(self, mock_util):
        username = "test"
        password = "test"
        argv = ["command"]

        config_dict = {"username": username, "password": password}

        mock_config = MagicMock()
        mock_config.items.return_value = config_dict

        mock_util.read_config.return_value = mock_config

        climesync.main(argv=argv, test=True)

        assert mock_util.print_json.call_count == 2

    @patch("climesync.climesync.util")
    def test_main_authenticate_error(self, mock_util):
        baseurl = "ts_url"
        argv = ["command"]

        config_dict = {"timesync_url": baseurl}

        mock_config = MagicMock()
        mock_config.items.return_value = config_dict

        mock_util.read_config.return_value = mock_config

        climesync.main(argv=argv, test=True)

        assert mock_util.print_json.call_count == 1
