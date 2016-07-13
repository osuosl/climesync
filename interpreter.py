import cmd

import commands
import util


class ClimesyncInterpreter(cmd.Cmd):
    """CLI interpreter for Climesync"""

    prompt = ""
    output = []

    connect_status = ""
    auth_status = ""

    connected_prompt = "(Connected) "
    disconnected_prompt = "(Disconnected) "

    test = False

    def update_prompt(self):
        if commands.ts:
            self.connect_status = self.connected_prompt

            if commands.ts.user:
                self.auth_status = "({}) ".format(commands.ts.user)
            else:
                self.auth_status = "(N/A) "
        else:
            self.connect_status = self.disconnected_prompt
            self.auth_status = ""

        self.prompt = "{}{}$ ".format(self.connect_status,
                                       self.auth_status)

    def preloop(self):
        self.update_prompt()

    def do_connect(self, line):
        """Connect to a TimeSync server"""
        self.output = commands.connect(test=self.test)

    def do_disconnect(self, line):
        """Disconnect from a TimeSync server"""
        self.output = commands.disconnect()

    def do_sign_in(self, line):
        """Authenticate with a TimeSync server"""
        self.output = commands.sign_in()

    def do_sign_out(self, line):
        """Sign out from a TimeSync server"""
        self.output = commands.sign_out()

    def do_create_time(self, line):
        """Submit a time to a TimeSync server"""
        self.output = commands.create_time()

    def do_update_time(self, line):
        """Update a time on a TimeSync server"""
        self.output = commands.update_time()

    def do_get_times(self, line):
        """Gets a list of times from a TimeSync server"""
        self.output = commands.get_times()

    def do_sum_times(self, line):
        """Sums the total amount of times worked on one or more projects"""
        self.output = commands.sum_times()

    def do_delete_time(self, line):
        """Deletes a time from a TimeSync server"""
        self.output = commands.delete_time()

    def do_create_project(self, line):
        """Creates a project on a TimeSync server"""
        self.output = commands.create_project()

    def do_update_project(self, line):
        """Updates a project on a TimeSync server"""
        self.output = commands.update_project()

    def do_get_projects(self, line):
        """Gets a list of projects from a TimeSync server"""
        self.output = commands.get_projects()

    def do_delete_project(self, line):
        """Deletes a project from a TimeSync server"""
        self.output = commands.delete_project()

    def do_create_activity(self, line):
        """Creates an activity on a TimeSync server"""
        self.output = commands.create_activity()

    def do_update_activity(self, line):
        """Updates an activity on a TimeSync server"""
        self.output = commands.update_activity()

    def do_get_activities(self, line):
        """Gets a list of activities from a TimeSync server"""
        self.output = commands.get_activities()

    def do_delete_activity(self, line):
        """Deletes an activity from a TimeSync server"""
        self.output = commands.delete_activity()

    def do_create_user(self, line):
        """Creates a user on a TimeSync server"""
        self.output = commands.create_user()

    def do_update_user(self, line):
        """Updates a user on a TimeSync server"""
        self.output = commands.update_user()

    def do_get_users(self, line):
        """Gets a list of users from a TimeSync server"""
        self.output = commands.get_users()

    def do_delete_user(self, line):
        """Deletes a user from a TimeSync server"""
        self.output = commands.delete_user()

    def do_quit(self, line):
        """Exit Climesync"""
        return True

    def postcmd(self, stop, line):
        # Only print and flush output if not in test mode
        if self.output and not self.test:
            util.print_json(self.output)
            self.output = []

        self.update_prompt()

        return cmd.Cmd.postcmd(self, stop, line)
