#!/usr/bin/env python

import pymesync
import os
import sys
import stat
import codecs
import re
import ConfigParser
import argparse

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

ts = None  # pymesync.TimeSync object


def create_config(path="~/.climesyncrc"):
    """Create the configuration file if it doesn't exist"""

    realpath = os.path.expanduser(path)

    # Create the file if it doesn't exist then set its mode to 600 (Owner RW)
    with codecs.open(realpath, "w", "utf-8-sig") as f:
        f.write(u"# Climesync configuration file\n")

    os.chmod(realpath, stat.S_IRUSR | stat.S_IWUSR)


def read_config(path="~/.climesyncrc"):
    """Read the configuration file and return its contents"""

    realpath = os.path.expanduser(path)

    config = ConfigParser.RawConfigParser()

    # If the file already exists, try to read it
    if os.path.isfile(realpath):
        # Try to read the config file at the given path. If the file isn't
        # formatted correctly, inform the user
        try:
            with codecs.open(realpath, "r", "utf-8") as f:
                config.readfp(f)
        except ConfigParser.ParsingError as e:
            print e
            print "ERROR: Invalid configuration file!"
            return None

    return config


def write_config(key, value, path="~/.climesyncrc"):
    """Write a value to the configuration file"""

    realpath = os.path.expanduser(path)

    config = read_config(path)

    # If the configuration file doesn't exist (read_config returned an
    # empty config), create it
    if "climesync" not in config.sections():
        create_config(path)

    # If read_config errored and returned None instead of a ConfigParser
    if not config:
        return

    # Attempt to set the option value in the config
    # If the "climesync" section doesn't exist (NoSectionError), create it
    try:
        config.set("climesync", key, value.encode("utf-8"))
    except ConfigParser.NoSectionError:
        config.add_section("climesync")
        config.set("climesync", key, value.encode("utf-8"))

    print config.get("climesync", key)

    # Truncate existing file before writing to it
    with codecs.open(realpath, "w", "utf-8") as f:
        f.write(u"# Climesync configuration file\n")

        # Write the config values
        config.write(f)


def print_json(response):
    """Prints values returned by Pymesync nicely"""

    print ""

    if isinstance(response, list):  # List of dictionaries
        for json_dict in response:
            for key, value in json_dict.iteritems():
                print u"{}: {}".format(key, value)

            print ""
    elif isinstance(response, dict):  # Plain dictionary
        for key, value in response.iteritems():
            print u"{}: {}".format(key, value)

        print ""
    else:
        print "I don't know how to print that!"
        print response


def is_time(time_str):
    """Checks if the supplied string is formatted as a time value for Pymesync

    A string is formatted correctly if it matches the pattern

        <value>h<value>m

    where the first value is the number of hours and the second is the number
    of minutes.
    """

    return True if re.match(r"\A[\d]+h[\d]+m\Z", time_str) else False


def to_readable_time(seconds):
    """Converts a time in seconds to a human-readable format"""

    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    return "{}h{}m".format(hours, minutes)


def get_field(prompt, optional=False, field_type=""):
    """Prompts the user for input and returns it in the specified format

    prompt - The prompt to display to the user
    optional - Whether or not the field is optional (defaults to False)
    field_type - The type of input. If left empty, input is a string

    Valid field_types:
    ? - Yes/No input
    : - Time input
    ! - Multiple inputs delimited by commas returned as a list
    """

    # If necessary, add extra prompts that inform the user
    optional_prompt = ""
    type_prompt = ""

    if optional:
        optional_prompt = "(Optional) "

    if field_type == "?":
        if optional:
            type_prompt = "(y/N) "
        else:
            type_prompt = "(y/n) "

    if field_type == ":":
        type_prompt = "(Time input - <value>h<value>m) "

    if field_type == "!":
        type_prompt = "(Comma delimited) "

    # Format the original prompt with prepended additions
    formatted_prompt = "{}{}{}: ".format(optional_prompt, type_prompt, prompt)
    response = ""

    while True:
        response = raw_input(formatted_prompt).decode(sys.stdin.encoding)

        if not response and optional:
            return ""
        elif response:
            if field_type == "?":
                if response.upper() in ["Y", "YES", "N", "NO"]:
                    return True if response.upper() in ["Y", "YES"] else False
            elif field_type == ":":
                if is_time(response):
                    return response
            elif field_type == "!":
                return [r.strip() for r in response.split(",")]
            elif field_type == "":
                return response
            else:
                # If the provided field_type isn't valid, return empty string
                return ""

        print "Please submit a valid input"


def get_fields(fields):
    """Prompts for multiple fields and returns everything in a dictionary

    fields - A list of tuples that are ordered (field_name, prompt)

    field_name can contain special characters that signify input type
    ? - Yes/No field
    : - Time field
    ! - List field

    In addition to those, field_name can contain a * for an optional field
    """
    responses = dict()

    for field, prompt in fields:
        optional = False
        field_type = ""

        # Deduce field type
        if "?" in field:
            field_type = "?"  # Yes/No question
            field = field.replace("?", "")
        elif ":" in field:
            field_type = ":"  # Time
            field = field.replace(":", "")
        elif "!" in field:
            field_type = "!"  # Comma-delimited list
            field = field.replace("!", "")

        if "*" in field:
            optional = True
            field = field.replace("*", "")

        response = get_field(prompt, optional, field_type)

        # Only add response if it isn't empty
        if response != "":
            responses[field] = response

    return responses


def add_kv_pair(key, value, path="~/.climesyncrc"):
    """Ask the user if they want to add a key/value pair to the config file"""

    config = read_config(path)

    # If that key/value pair is already in the config, skip asking
    if config.has_option("climesync", key) \
       and config.get("climesync", key) == value:
        return

    print u"> {} = {}".format(key, value)
    response = get_field("Add to the config file?",
                         optional=True, field_type="?")

    if response:
        write_config(key, value, path)
        print "New value added!"


def get_user_permissions(users):
    """Asks for permissions for multiple users and returns them in a dict"""

    permissions = dict()

    for user in users:
        user_permissions = dict()

        member = get_field(u"Is {} a project member?".format(user),
                           field_type="?")
        spectator = get_field(u"Is {} a project spectator?".format(user),
                              field_type="?")
        manager = get_field(u"Is {} a project manager?".format(user),
                            field_type="?")

        user_permissions["member"] = member
        user_permissions["spectator"] = spectator
        user_permissions["manager"] = manager

        permissions[user] = user_permissions

    return permissions


def print_current(object_type, identifier):
    """Prints the current revision of an object or an error if it doesn't
    exist. Throw an exception if an error was returned from the server"""

    global ts

    if object_type == "time":
        current = ts.get_times({"uuid": identifier})[0]
    elif object_type == "project":
        current = ts.get_projects({"slug": identifier})[0]
    elif object_type == "activity":
        current = ts.get_activities({"slug": identifier})[0]
    elif object_type == "user":
        current = ts.get_users(username=identifier)[0]

    if "error" in current or "pymesync error" in current:
        print_json(current)
        raise RuntimeError()

    if object_type == "time":
        current["duration"] = to_readable_time(current["duration"])

    print_json(current)


def connect(arg_url="", config_dict=dict(), test=False):
    """Creates a new pymesync.TimeSync instance with a new URL"""

    global ts

    url = ""

    # Set the global variable so we can reconnect later.
    # If the URL is in the config, use that value at program startup
    # If the URL is provided in command line arguments, use that value
    if arg_url:
        url = arg_url
    elif "timesync_url" in config_dict:
        url = config_dict["timesync_url"]
    else:
        url = get_field("URL of TimeSync server") if not test else "tst"

    if not test:
        add_kv_pair("timesync_url", url)

    # Create a new instance and attempt to connect to the provided url
    ts = pymesync.TimeSync(baseurl=url, test=test)

    # No response from server upon connection
    return list()


def disconnect():
    """Disconnects from the TimeSync server"""

    global ts

    ts = None

    # No response from server
    return list()


def sign_in(arg_user="", arg_pass="", config_dict=dict()):
    """Attempts to sign in with user-supplied or command line credentials"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    username = ""
    password = ""

    # If username or password in config, use them at program startup.
    if arg_user:
        username = arg_user
    elif "username" in config_dict:
        username = config_dict["username"]
    else:
        username = get_field("Username")

    if arg_pass:
        password = arg_pass
    elif "password" in config_dict:
        password = config_dict["password"]
    else:
        password = get_field("Password")

    if not ts.test:
        add_kv_pair("username", username)
        add_kv_pair("password", password)

    # Attempt to authenticate and return the server's response
    return ts.authenticate(username, password, "password")


def sign_out():
    """Signs out from TimeSync and resets command line credentials"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    url = ts.baseurl
    test = ts.test

    # Create a new instance connected to the same server as the last
    ts = pymesync.TimeSync(baseurl=url, test=test)

    # No response from server
    return list()


def create_time():
    """Creates a new time and submits it to the TimeSync server"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    # The data to send to the server containing the new time information
    post_data = get_fields([(":duration",   "Duration"),
                            ("project",     "Project slug"),
                            ("!activities", "Activity slugs"),
                            ("date_worked", "Date worked (yyyy-mm-dd)"),
                            ("*issue_uri",  "Issue URI"),
                            ("*notes",      "Notes")])

    # Use the currently authenticated user
    post_data["user"] = ts.user

    # Attempt to create a time and return the response
    return ts.create_time(time=post_data)


def update_time():
    """Sends revised time information to the TimeSync server"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    uuid = get_field("UUID of time to update")

    try:
        print_current("time", uuid)
    except RuntimeError:
        return []

    # The data to send to the server containing revised time information
    post_data = get_fields([("*:duration",   "Duration"),
                            ("*project",     "Project slug"),
                            ("*user",        "New user"),
                            ("*!activities", "Activity slugs"),
                            ("*date_worked", "Date worked (yyyy-mm-dd)"),
                            ("*issue_url",   "Issue URI"),
                            ("*notes",       "Notes")])

    # Attempt to update a time and return the response
    return ts.update_time(uuid=uuid, time=post_data)


def get_times():
    """Queries the TimeSync server for submitted times with optional filters"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    # Optional filtering parameters to send to the server
    print "Filtering times..."
    post_data = get_fields([("*!user", "Submitted by users"),
                            ("*!project", "Belonging to projects"),
                            ("*!activity", "Belonging to activities"),
                            ("*start", "Beginning on date"),
                            ("*end", "Ending on date"),
                            ("*?include_revisions", "Include revised times?"),
                            ("*?include_deleted", "Include deleted times?"),
                            ("*uuid", "By UUID")])

    times = ts.get_times(query_parameters=post_data)

    # If the response is free of errors, make the times human-readable
    if 'error' not in times[0] and 'pymesync error' not in times[0]:
        for time in times:
            time["duration"] = to_readable_time(time["duration"])

    # Attempt to query the server for times with filtering parameters
    return times


def sum_times():
    """Sums all the times associated with a specific project"""

    query = get_fields([("!project", "Project slugs"),
                        ("*start", "Start date (yyyy-mm-dd)"),
                        ("*end", "End date (yyyy-mm-dd)")])

    result = ts.get_times(query)

    try:
        for project in query["project"]:
            time_sum = 0

            for user_time in result:
                if project in user_time["project"]:
                    time_sum += user_time["duration"]

            minutes, seconds = divmod(time_sum, 60)
            hours, minutes = divmod(minutes, 60)

            print
            print "{}".format(project)
            print to_readable_time(time_sum)

        return list()
    except Exception as e:
        print e
        return result


def delete_time():
    """Deletes a time from the TimeSync server"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    uuid = get_field("Time UUID")
    really = get_field(u"Do you really want to delete {}?".format(uuid),
                       field_type="?")

    if really:  # If the user really wants to delete it
        return ts.delete_time(uuid=uuid)
    else:  # If no, return an empty list
        return list()


def create_project():
    """Creates a new project on the TimeSync server"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    # The data to send to the server containing new project information
    post_data = get_fields([("name", "Project name"),
                            ("!slugs", "Project slugs"),
                            ("*uri", "Project URI"),
                            ("*!users", "Users"),
                            ("*default_activity", "Default activity")])

    # If users have been added to the project, ask for user permissions
    if "users" in post_data:
        users = post_data["users"]
        post_data["users"] = get_user_permissions(users)

    # Attempt to create a new project and return the response
    return ts.create_project(project=post_data)


def update_project():
    """Sends revised project information to the TimeSync server"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    slug = get_field("Slug of project to update")

    try:
        print_current("project", slug)
    except RuntimeError:
        return []

    # The data to send to the server containing revised project information
    post_data = get_fields([("*name", "Updated project name"),
                            ("*!slugs", "Updated project slugs"),
                            ("*uri", "Updated project URI"),
                            ("*!users", "Updated users"),
                            ("*default_activity", "Updated default activity")])

    # If user permissions are going to be updated, ask for them
    if "users" in post_data:
        users = post_data["users"]
        post_data["users"] = get_user_permissions(users)

    # Attempt to update the project information and return the response
    return ts.update_project(project=post_data, slug=slug)


def get_projects():
    """Queries the TimeSync server for projects with optional filters"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    # Optional filtering parameters
    print "Filtering projects..."
    post_data = get_fields([("*?include_revisions", "Include revisions?"),
                            ("*?include_deleted", "Include deleted?"),
                            ("*slug", "By project slug")])

    # Attempt to query the server with filtering parameters
    return ts.get_projects(query_parameters=post_data)


def delete_project():
    """Deletes a project from the TimeSync server"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    slug = get_field("Project slug")
    really = get_field(u"Do you really want to delete {}?".format(slug),
                       field_type="?")

    if really:  # If the user really wants to delete it
        return ts.delete_project(slug=slug)
    else:  # If no, return an empty list
        return list()


def create_activity():
    """Creates a new activity on the TimeSync server"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    # The data to send to the server containing new activity information
    post_data = get_fields([("name", "Activity name"),
                            ("slug", "Activity slug")])

    # Attempt to create a new activity and return the response
    return ts.create_activity(activity=post_data)


def update_activity():
    """Sends revised activity information to the TimeSync server"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    slug_to_update = get_field("Slug of activity to update")

    try:
        print_current("activity", slug_to_update)
    except RuntimeError:
        return []

    # The data to send to the server containing revised activity information
    post_data = get_fields([("*name", "Updated activity name"),
                            ("*slug", "Updated activity slug")])

    # Attempt to update the activity information and return the repsonse
    return ts.update_activity(activity=post_data, slug=slug_to_update)


def get_activities():
    """Queries the TimeSync server for activities with optional filters"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    # Optional filtering parameters
    print "Filtering activities..."
    post_data = get_fields([("*?include_revisions", "Include revisions?"),
                            ("*?include_deleted", "Include deleted?"),
                            ("*slug", "By activity slug")])

    # Attempt to query the server with filtering parameters
    return ts.get_activities(query_parameters=post_data)


def delete_activity():
    """Deletes an activity from the TimeSync server"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    slug = get_field("Activity slug")
    really = get_field(u"Do you really want to delete {}?".format(slug),
                       field_type="?")

    if really:  # If the user really wants to delete it
        return ts.delete_activity(slug=slug)

    else:  # If no, return an empty list
        return list()


def create_user():
    """Creates a new user on the TimeSync server"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    # The data to send to the server containing new user information
    post_data = get_fields([("username", "New user username"),
                            ("password", "New user password"),
                            ("*display_name", "New user display name"),
                            ("*email", "New user email"),
                            ("*?site_admin", "Is the user an admin?"),
                            ("*?site_manager", "Is the user a manager?"),
                            ("*?site_spectator", "Is the user a spectator?"),
                            ("*meta", "Extra meta-information"),
                            ("*?active", "Is the new user active?")])

    # Attempt to create a new user and return the response
    return ts.create_user(user=post_data)


def update_user():
    """Sends revised user information to the TimeSync server"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    username_to_update = get_field("Username of user to update")

    try:
        print_current("user", username_to_update)
    except:
        return []

    # The data to send to the server containing revised user information
    post_data = get_fields([("*username", "Updated username"),
                            ("*password", "Updated password"),
                            ("*display_name", "Updated display name"),
                            ("*email", "Updated email"),
                            ("*?site_admin", "Is the user an admin?"),
                            ("*?site_manager", "Is the user a manager?"),
                            ("*?site_spectator", "Is the user a spectator?"),
                            ("*meta", "New metainformation"),
                            ("*?active", "Is the user active?")])

    # Attempt to update the user and return the response
    return ts.update_user(user=post_data, username=username_to_update)


def get_users():
    """Queries the TimeSync server for users with optional filters"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    # Optional filtering parameters
    print "Filtering users..."
    username = get_field("By username", optional=True)

    # Attempt to query the server with filtering parameters
    return ts.get_users(username=username)


def delete_user():
    """Deletes a user from the TimeSync server"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    username = get_field("Username")
    really = get_field(u"Do you really want to delete {}?".format(username),
                       field_type="?")

    if really:  # If the user really wants to delete it
        return ts.delete_user(username=username)
    else:  # If no, return an empty list
        return list()


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
        sys.exit(0)

    # Print server response
    if response:
        print_json(response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--connect", help="connect to a timesync server")
    parser.add_argument("-u", "--username", help="specify your username")
    parser.add_argument("-p", "--password", help="specify your password")

    # Command line arguments
    args = parser.parse_args()
    url = args.connect
    user = args.username
    password = args.password

    try:
        config_dict = dict(read_config().items("climesync"))
    except:
        config_dict = {}

    # Attempt to connect with arguments and/or config
    connect(arg_url=url, config_dict=config_dict)

    response = sign_in(arg_user=user, arg_pass=password,
                       config_dict=config_dict)

    print_json(response)

    while True:
        menu()

if __name__ == "__main__":
    main()
