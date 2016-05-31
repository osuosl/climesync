#!/usr/bin/env python

"""Climesync

Usage: climesync.py [-h -c BASEURL -u USERNAME -p PASSWORD]

-h, --help                       Show this dialog
-c BASEURL, --connect=BASEURL    TimeSync Server URL
-u USERNAME, --username=USERNAME Username of user to authenticate as
-p PASSWORD, --password=PASSWORD Password of user to authenticate as

"""

import pymesync
from docopt import docopt

import commands
import util

menu_options = (
    "\n"
    "===============================================================\n"
    " pymesync CLI to interact with TimeSync\n"
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
        response = commands.connect()
    elif choice == "dc":
        response = commands.disconnect()
    elif choice == "s":
        response = commands.sign_in()
    elif choice == "so":
        response = commands.sign_out()
    elif choice == "ct":
        response = commands.create_time()
    elif choice == "ut":
        response = commands.update_time()
    elif choice == "gt":
        response = commands.get_times()
    elif choice == "st":
        response = commands.sum_times()
    elif choice == "dt":
        response = commands.delete_time()
    elif choice == "cp":
        response = commands.create_project()
    elif choice == "up":
        response = commands.update_project()
    elif choice == "gp":
        response = commands.get_projects()
    elif choice == "dp":
        response = commands.delete_project()
    elif choice == "ca":
        response = commands.create_activity()
    elif choice == "ua":
        response = commands.update_activity()
    elif choice == "ga":
        response = commands.get_activities()
    elif choice == "da":
        response = commands.delete_activity()
    elif choice == "cu":
        response = commands.create_user()
    elif choice == "uu":
        response = commands.update_user()
    elif choice == "gu":
        response = commands.get_users()
    elif choice == "du":
        response = commands.delete_user()
    elif choice == "h":
        print menu_options
    elif choice == "q":
        return False

    # Print server response
    if response:
        util.print_json(response)

    return True


def main(argv=None):
    # Command line arguments
    args = docopt(__doc__, argv=argv)

    url = args['--connect']
    user = args['--username']
    password = args['--password']

    try:
        config_dict = dict(util.read_config().items("climesync"))
    except:
        config_dict = {}

    # Attempt to connect with arguments and/or config
    commands.connect(arg_url=url, config_dict=config_dict)

    response = commands.sign_in(arg_user=user, arg_pass=password,
                                config_dict=config_dict)

    util.print_json(response)

    while menu():
        pass

if __name__ == "__main__":
    main()
