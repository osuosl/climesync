#!/usr/bin/env python

"""Climesync - CLI TimeSync Frontend

Usage: climesync.py [options] [<command> [<args>... ]]

Options:
    -h             --help                 Print this dialog
    -c <baseurl>   --connect=<baseurl>    TimeSync Server URL
    -u <username>  --username=<username>  Username of user to authenticate as
    -p <password>  --password=<password>  Password of user to authenticate as

By default, Climesync starts in interactive mode and allows the user to enter
commands into a shell. However, you can access certain Climesync functionality
without going into interactive mode by calling them from the command line.

The following commands are available from the command line:

    help             Get help for specific commands

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

For more detailed information about a specific command, type
climesync.py help <command>

"""

from docopt import docopt

from commands import *
import scripting
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
    "h - print this menu\n"
    "q - exit\n")


def menu():
    """Provides the user with options and executes commands"""

    choice = raw_input("(h for help) $ ")
    response = list()  # A list of python dictionaries

    if choice == "c":
        response = connect()
    elif choice == "dc":
        response = disconnect()
    elif choice == "s":
        response = sign_in()
    elif choice == "so":
        response = sign_out()
    elif choice == "ct":
        response = create_time()
    elif choice == "ut":
        response = update_time()
    elif choice == "gt":
        response = get_times()
    elif choice == "st":
        response = sum_times()
    elif choice == "dt":
        response = delete_time()
    elif choice == "cp":
        response = create_project()
    elif choice == "up":
        response = update_project()
    elif choice == "gp":
        response = get_projects()
    elif choice == "dp":
        response = delete_project()
    elif choice == "ca":
        response = create_activity()
    elif choice == "ua":
        response = update_activity()
    elif choice == "ga":
        response = get_activities()
    elif choice == "da":
        response = delete_activity()
    elif choice == "cu":
        response = create_user()
    elif choice == "uu":
        response = update_user()
    elif choice == "gu":
        response = get_users()
    elif choice == "du":
        response = delete_user()
    elif choice == "h":
        print menu_options
    elif choice == "q":
        return False

    # Print server response
    if response:
        util.print_json(response)

    return True


def interactive_mode():
    """Start Climesync in interactive mode"""
    while menu():
        pass


def scripting_mode(command, argv):
    if command == 'create-time':
        create_time(argv)


def main(argv=None):
    # Command line arguments
    args = docopt(__doc__, argv=argv, options_first = True)

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
    connect(arg_url=url, config_dict=config_dict,
                     interactive=interactive)

    response = sign_in(arg_user=user, arg_pass=password,
                                config_dict=config_dict,
                                interactive=interactive)

    if command:
        scripting_mode(command, argv)
    else:
        util.print_json(response)
        interactive_mode()

if __name__ == "__main__":
    main()
