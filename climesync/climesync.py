#!/usr/bin/env python

"""Climesync - CLI TimeSync Frontend

Usage: climesync.py [options] [<command> [<args>... ]]

Options:
    -h --help      Print this dialog
    -c <baseurl>   TimeSync Server URL
    -u <username>  Username of user to authenticate as
    -p <password>  Password of user to authenticate as

Commands:

    create-time      Submit a new time
    update-time      Update the fields of an existing time
    get-times        List and optionally filter all times on the server
    sum-times        Sum all the times worked on a project
    delete-time      Delete a time

    create-project   Create a new project
    update-project   Update the fields of an existing project
    get-projects     List and optionally filter all projects on the server
    delete-project   Delete a project

    create-activity  Create a new activity
    update-activity  Update the fields of an existing activity
    get-activities   List and optionally filter all activities on the server
    delete-activity  Delete an activity

    create-user      Create a new user
    update-user      Update the information of an existing user
    get-users        List all users or get information on a specific user
    delete-user      Delete a user

By default, Climesync starts in interactive mode and allows the user to enter
commands into a shell. However, you can access certain Climesync functionality
without going into interactive mode by calling them from the command line.

For more detailed information about a specific command, type
climesync.py <command> --help

"""

import sys  # NOQA flake8 ignore

from docopt import docopt

import commands
from interpreter import ClimesyncInterpreter
import util

# Command lookup table for scripting mode
command_lookup = {
    "create-time":     commands.create_time,
    "update-time":     commands.update_time,
    "get-times":       commands.get_times,
    "sum-times":       commands.sum_times,
    "delete-time":     commands.delete_time,
    "create-project":  commands.create_project,
    "update-project":  commands.update_project,
    "get-projects":    commands.get_projects,
    "delete-project":  commands.delete_project,
    "create-activity": commands.create_activity,
    "update-activity": commands.update_activity,
    "get-activities":  commands.get_activities,
    "delete-activity": commands.delete_activity,
    "create-user":     commands.create_user,
    "update-user":     commands.update_user,
    "get-users":       commands.get_users,
    "delete-user":     commands.delete_user,
}


def scripting_mode(command_name, argv):
    """Call a climesync command with command line arguments"""
    command = command_lookup.get(command_name)

    if command:
        util.print_json(command(argv))
    else:
        print __doc__


def main(argv=None, test=False):
    # Command line arguments
    args = docopt(__doc__, argv=argv, options_first=True)
    url = args['-c']
    user = args['-u']
    password = args['-p']

    command = args['<command>']
    argv = args['<args>']

    interactive = False if command else True

    try:
        config_dict = dict(util.read_config().items("climesync"))
    except:
        config_dict = {}

    # Attempt to connect with arguments and/or config
    response = commands.connect(arg_url=url, config_dict=config_dict,
                                interactive=interactive, test=test)

    if "climesync error" in response:
        util.print_json(response)

    response = commands.sign_in(arg_user=user, arg_pass=password,
                                config_dict=config_dict,
                                interactive=interactive)

    if "error" in response or "pymesync error" in response or \
            "climesync error" in response:
        util.print_json(response)

    if command:
        scripting_mode(command, argv)
    else:
        util.print_json(response)
        ClimesyncInterpreter().cmdloop()

if __name__ == "__main__":
    main()
