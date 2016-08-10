#!/usr/bin/env python

"""Climesync - CLI TimeSync Frontend

Usage: climesync.py [options] [<command> [<args>... ]]

Options:
    -h             --help                 Print this dialog
    -c <baseurl>   --connect=<baseurl>    TimeSync Server URL
    -u <username>  --username=<username>  Username of user to authenticate as
    -p <password>  --password=<password>  Password of user to authenticate as
    -l             --ldap                 Authenticate using LDAP credentials

Commands:

    create-time           Submit a new time
    update-time           Update the fields of an existing time
    get-times             List and optionally filter times on the server
    sum-times             Sum all the times worked on a project
    delete-time           Delete a time

    create-project        Create a new project
    update-project        Update the fields of an existing project
    update-project-users  Update a project's users/add new users to a project
    remove-project-users  Remove users from a project
    get-projects          List and optionally filter projects on the server
    delete-project        Delete a project

    create-activity       Create a new activity
    update-activity       Update the fields of an existing activity
    get-activities        List and optionally filter activities on the server
    delete-activity       Delete an activity

    create-user           Create a new user
    update-user           Update the information of an existing user
    get-users             List all users or get information on a specific user
    delete-user           Delete a user

By default, Climesync starts in interactive mode and allows the user to enter
commands into a shell. However, you can access certain Climesync functionality
without going into interactive mode by calling them from the command line.

For more detailed information about a specific command, type
climesync.py <command> --help

"""

import sys  # NOQA flake8 ignore

from docopt import docopt

import commands
import util

menu_options = (
    "\n"
    "===============================================================\n"
    " Climesync Interactive Mode\n"
    "===============================================================\n"
    "\nWhat do you want to do?\n"
    "c - connect\n"
    "dc - disconnect\n"
    "s - sign in\n"
    "so - sign out/reset credentials\n\n"
    "ct - submit time\n"
    "ut - update time\n"
    "gt - get times\n"
    "st - sum times\n"
    "dt - delete time\n\n"
    "cp - create project\n"
    "up - update project\n"
    "upu - update project users\n"
    "rpu - remove project users\n"
    "gp - get projects\n"
    "dp - delete project\n\n"
    "ca - create activity\n"
    "ua - update activity\n"
    "ga - get activities\n"
    "da - delete activity\n\n"
    "cu - create user\n"
    "uu - update user\n"
    "gu - get users\n"
    "du - delete user\n\n"
    "us - update user settings\n\n"
    "h - print this menu\n"
    "q - exit\n")

# Lookup table for Climesync commands in both interactive mode and
# scripting mode. Table entries are represented as a tuple in the form
# (interactive_name, scripting_name, command)
command_lookup = [
    ("c",   None,                   commands.connect),
    ("dc",  None,                   commands.disconnect),
    ("s",   None,                   commands.sign_in),
    ("so",  None,                   commands.sign_out),
    ("ct",  "create-time",          commands.create_time),
    ("ut",  "update-time",          commands.update_time),
    ("gt",  "get-times",            commands.get_times),
    ("st",  "sum-times",            commands.sum_times),
    ("dt",  "delete-time",          commands.delete_time),
    ("cp",  "create-project",       commands.create_project),
    ("up",  "update-project",       commands.update_project),
    ("upu", "update-project-users", commands.update_project_users),
    ("rpu", "remove-project-users", commands.remove_project_users),
    ("gp",  "get-projects",         commands.get_projects),
    ("dp",  "delete-project",       commands.delete_project),
    ("ca",  "create-activity",      commands.create_activity),
    ("ua",  "update-activity",      commands.update_activity),
    ("ga",  "get-activities",       commands.get_activities),
    ("da",  "delete-activity",      commands.delete_activity),
    ("cu",  "create-user",          commands.create_user),
    ("uu",  "update-user",          commands.update_user),
    ("gu",  "get-users",            commands.get_users),
    ("du",  "delete-user",          commands.delete_user),
]


def lookup_command(name, col):
    """Look for a command in the command lookup table by matching a name
       with a value in the specified column
    """
    names = [c[col] for c in command_lookup]
    if name in names:
        return command_lookup[names.index(name)][2]
    else:
        return None


def menu():
    """Provide an interactive shell for the user to execute commands"""
    choice = util.get_field("(h for help) ")

    command = lookup_command(choice, 0)

    if command:
        util.print_pretty(command())
    elif choice == "h":
        print menu_options
    elif choice == "q":
        return False
    elif choice:
        print "Invalid choice!"

    return True


def interactive_mode():
    """Start Climesync in interactive mode"""
    while menu():
        pass


def scripting_mode(command_name, argv):
    """Call a climesync command with command line arguments"""
    command = lookup_command(command_name, 1)

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
    ldap = args['-l']

    command = args['<command>']
    argv = args['<args>']

    interactive = False if command else True

    try:
        config_obj = util.read_config()

        if config_obj.has_option("climesync", "autoupdate_config"):
            commands.autoupdate_config = \
                config_obj.getboolean("climesync", "autoupdate_config")

        config_dict = dict(config_obj.items("climesync"))
    except:
        config_dict = {}

    if ldap or \
       ("ldap" in config_dict and config_dict["ldap"].lower() == "true"):
        commands.ldap = True
    else:
        commands.ldap = False

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
        interactive_mode()

if __name__ == "__main__":
    main()
