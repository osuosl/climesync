import unittest
from mock import patch

from climesync import commands
from climesync.interpreter import ClimesyncInterpreter


class InterpreterTest(unittest.TestCase):

    def setUp(self):
        commands.connect(test=True)

        self.interpreter = ClimesyncInterpreter()

    def run_command(self, command):
        self.interpreter.test = True
        self.interpreter.precmd(command)
        stop = self.interpreter.onecmd(command)
        self.interpreter.postcmd(stop, command)
        self.interpreter.test = False

    @patch("climesync.interpreter.util")
    def test_postcmd_output(self, mock_util):
        stop = False
        line = ""
        output = {"key": "value"}

        self.interpreter.output = output

        self.interpreter.postcmd(stop, line)

        mock_util.print_json.assert_called_with(output)

    @patch("climesync.interpreter.util")
    def test_postcmd_no_output(self, mock_util):
        stop = False
        line = ""
        output = {}

        self.interpreter.output = output

        self.interpreter.postcmd(stop, line)

        mock_util.print_json.assert_not_called()

    @patch("climesync.interpreter.util")
    def test_postcmd_test_mode(self, mock_util):
        stop = False
        line = ""
        output = {"key": "value"}

        self.interpreter.output = output
        self.interpreter.test = True

        self.interpreter.postcmd(stop, line)

        mock_util.print_json.assert_not_called()

    def test_connect_command(self):
        self.run_command("connect")

        assert not self.interpreter.output
        print self.interpreter.prompt
        assert self.interpreter.prompt == "(Connected) (N/A) $ "

    def test_disconnect_command(self):
        self.run_command("disconnect")

        assert not self.interpreter.output
        assert self.interpreter.prompt == "(Disconnected) $ "

    def test_sign_in_command(self):
        self.run_command("sign_in")

        assert "token" in self.interpreter.output

    def test_sign_out_command(self):
        self.run_command("sign_out")

        assert not self.interpreter.output
