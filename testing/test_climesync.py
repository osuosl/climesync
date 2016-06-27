import unittest
from mock import call, patch, MagicMock

import climesync
from climesync import command_lookup
import commands

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

    @patch("commands.util")
    @patch("commands.pymesync.TimeSync")
    def test_connect_arg_url(self, mock_timesync, mock_util):
        baseurl = "ts_url"

        commands.connect(arg_url=baseurl)

        mock_util.add_kv_pair.assert_called_with("timesync_url", baseurl)
        mock_timesync.assert_called_with(baseurl=baseurl, test=False)

        commands.ts = None

    @patch("commands.util")
    @patch("commands.pymesync.TimeSync")
    def test_connect_config_dict(self, mock_timesync, mock_util):
        baseurl = "ts_url"
        config_dict = {"timesync_url": baseurl}

        commands.connect(config_dict=config_dict)

        mock_util.add_kv_pair.assert_called_with("timesync_url", baseurl)
        mock_timesync.assert_called_with(baseurl=baseurl, test=False)

        commands.ts = None

    @patch("commands.util")
    @patch("commands.pymesync.TimeSync")
    @patch("commands.raw_input")
    def test_connect_interactive(self, mock_raw_input, mock_timesync,
                                 mock_util):
        baseurl = "ts_url"

        mock_raw_input.return_value = baseurl
        
        commands.connect()

        mock_util.add_kv_pair.assert_called_with("timesync_url", baseurl)
        mock_timesync.assert_called_with(baseurl=baseurl, test=False)

        commands.ts = None

    @patch("commands.util")
    @patch("commands.pymesync.TimeSync")
    def test_connect_noninteractive(self, mock_timesync, mock_util):
        baseurl = "ts_url"

        commands.connect(arg_url=baseurl, interactive=False)

        mock_util.add_kv_pair.assert_not_called()
        mock_timesync.assert_called_with(baseurl=baseurl, test=False)

        commands.ts = None

    def test_connect_error(self):
        response = commands.connect(interactive=False)

        assert "climesync error" in response

    def test_disconnect(self):
        commands.ts = MagicMock()

        commands.disconnect()

        assert not commands.ts

    @patch("commands.util")
    @patch("commands.ts")
    def test_sign_in_args(self, mock_ts, mock_util):
        username = "test"
        password = "password"

        mock_ts.test = False

        commands.sign_in(arg_user=username, arg_pass=password)

        mock_util.add_kv_pair.assert_has_calls([call("username", username),
                                                call("password", password)])
        mock_ts.authenticate.assert_called_with(username, password, "password")

    @patch("commands.util")
    @patch("commands.ts")
    def test_sign_in_config_dict(self, mock_ts, mock_util):
        username = "test"
        password = "password"
        config_dict = {"username": username, "password": password}

        mock_ts.test = False

        commands.sign_in(config_dict=config_dict)

        mock_util.add_kv_pair.assert_has_calls([call("username", username),
                                                call("password", password)])
        mock_ts.authenticate.assert_called_with(username, password, "password")

    @patch("commands.util")
    @patch("commands.ts")
    @patch("commands.raw_input")
    def test_sign_in_interactive(self, mock_raw_input, mock_ts, mock_util):
        username = "test"
        password = "test"
        mocked_input = [username, password]

        mock_raw_input.side_effect = mocked_input
        mock_ts.test = False

        commands.sign_in()

        mock_util.add_kv_pair.assert_has_calls([call("username", username),
                                                call("password", password)])
        mock_ts.authenticate.assert_called_with(username, password, "password")

    @patch("commands.util")
    @patch("commands.ts")
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

    @patch("commands.ts")
    def test_sign_in_error(self, mock_ts):
        response = commands.sign_in(interactive=False)

        assert "climesync error" in response

    @patch("commands.ts")
    @patch("commands.pymesync.TimeSync")
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

    @patch("climesync.commands")
    @patch("climesync.interactive_mode")
    def test_start_interactive(self, mock_interactive_mode, mock_commands):
        argv = []

        climesync.main(argv=argv)

        mock_interactive_mode.assert_called_with()

    @patch("climesync.commands")
    @patch("climesync.scripting_mode")
    def test_start_scripting(self, mock_scripting_mode, mock_commands):
        command = "create-time"
        argv = [command]

        climesync.main(argv=argv)

        mock_scripting_mode.assert_called_with("create-time", [])

    @patch("climesync.util")
    @patch("climesync.commands")
    @patch("climesync.interactive_mode")
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

    @patch("climesync.scripting_mode")
    @patch("climesync.util.read_config")
    def test_use_config(self, mock_read_config, mock_scripting_mode):
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

    @patch("climesync.util")
    def test_connect_error(self, mock_util):
        argv = ["command"]

        config_dict = {}

        mock_config = MagicMock()
        mock_config.items.return_value = config_dict

        mock_util.read_config.return_value = mock_config

        climesync.main(argv=argv, test=True)

        assert mock_util.print_json.call_count == 1

    @patch("climesync.util")
    def test_authenticate_error(self, mock_util):
        baseurl = "ts_url"
        argv = ["command"]

        config_dict = {"timesync_url": baseurl}

        mock_config = MagicMock()
        mock_config.items.return_value = config_dict

        mock_util.read_config.return_value = mock_config

        climesync.main(argv=argv, test=True)

        assert mock_util.print_json.call_count == 1
