import unittest
from mock import patch

import commands
from interpreter import ClimesyncInterpreter


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

    def test_connect_command(self):
        self.run_command("connect")

        assert not self.interpreter.output
        print self.interpreter.prompt
        assert self.interpreter.prompt == self.interpreter.connected_prompt

    def test_disconnect_command(self):
        self.run_command("disconnect")

        assert not self.interpreter.output
        assert self.interpreter.prompt == self.interpreter.disconnected_prompt

    def test_sign_in_command(self):
        self.run_command("sign_in")

        assert "token" in self.interpreter.output

    def test_sign_out_command(self):
        self.run_command("sign_out")

        assert not self.interpreter.output
