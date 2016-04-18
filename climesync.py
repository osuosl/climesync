#!/usr/bin/env python

import pymesync
import sys
import argparse

menu_options = (
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
    "q - exit\n")

arg_username = ""
arg_password = ""
timesync_url = ""
ts = None  # pymesync.TimeSync object


def print_json(response):
    """Prints values returned by Pymesync nicely"""

    print ""

    # List of dictionaries
    if isinstance(response, list):
        for json_dict in response:
            for key, value in json_dict.iteritems():
                print "{}: {}".format(key, value)

            print ""

    # Plain dictionary
    elif isinstance(response, dict):
        for key, value in response.iteritems():
            print "{}: {}".format(key, value)

    else:
        print "I don't know how to print that!"
        print response

    print ""


def get_field(prompt, optional=False, field_type=""):
    """Prompts the user for input and returns it in the specified format

    prompt - The prompt to display to the user
    optional - Whether or not the field is optional (defaults to False)
    field_type - The type of input. If left empty, input is a string

    Valid field_types:
    ? - Yes/No input
    # - Integer input
    ! - Multiple inputs delimited by commas returned as a list
    """

    # If necessary, add extra prompts that inform the user
    optional_prompt = ""
    type_prompt = ""

    if optional:
        optional_prompt = "(Optional) "

    if field_type == "?":
        type_prompt = "(y/N) "

    if field_type == "#":
        type_prompt = "(Integer) "

    if field_type == "!":
        type_prompt = "(Comma delimited) "

    # Format the original prompt with prepended additions
    formatted_prompt = "{}{}{}: ".format(optional_prompt, type_prompt, prompt)
    response = ""

    while True:
        response = raw_input(formatted_prompt)

        if not response and optional:
            return ""

        elif response:
            if field_type == "?":
                if response.upper() in ["Y", "YES", "N", "NO"]:
                    return True if response.upper() in ["Y", "YES"] else False

            elif field_type == "#":
                if response.isdigit():
                    return int(response)

            elif field_type == "!":
                return [r.strip() for r in response.split(",")]

            elif field_type == "":
                return response

            # If the provided field_type isn't valid, return an empty string
            else:
                return ""

        print "Please submit a valid input"


def get_fields(fields):
    """Prompts for multiple fields and returns everything in a dictionary

    fields - A list of tuples that are ordered (field_name, prompt)

    field_name can contain special characters that signify input type
    ? - Yes/No field
    # - Integer field
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

        elif "#" in field:
            field_type = "#"  # Integer
            field = field.replace("#", "")

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


def get_user_permissions(users):
    """Asks for permissions for multiple users and returns them in a dict"""

    permissions = dict()

    for user in users:
        user_permissions = dict()

        member = get_field("Is {} a project member?".format(user),
                           field_type="?")
        spectator = get_field("Is {} a project spectator?".format(user),
                              field_type="?")
        manager = get_field("Is {} a project manager?".format(user),
                            field_type="?")

        user_permissions["member"] = member
        user_permissions["spectator"] = spectator
        user_permissions["manager"] = manager

        permissions[user] = user_permissions

    return permissions


def connect():
    """Creates a new pymesync.TimeSync instance with a new URL"""

    global timesync_url, ts

    # Set the global variable so we can reconnect later
    timesync_url = raw_input("URL of TimeSync server: ")

    # Create a new instance and attempt to connect to the provided url
    ts = pymesync.TimeSync(baseurl=timesync_url)

    # No response from server upon connection
    return list()


def disconnect():
    """Disconnects from the TimeSync server"""

    global ts

    ts = None

    # No response from server
    return list()


def sign_in():
    """Attempts to sign in with user-supplied or command line credentials"""

    global arg_username, arg_password, ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    # If username or password not provided on command line, ask for them
    username = arg_username if arg_username else raw_input("Username: ")
    password = arg_password if arg_password else raw_input("Password: ")

    # Attempt to authenticate and return the server's response
    return ts.authenticate(username, password, "password")


def sign_out():
    """Signs out from TimeSync and resets command line credentials"""

    global arg_username, arg_password, timesync_url, ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    # Reset the credentials provided on the command line
    arg_username = arg_password = ""

    # Create a new instance connected to the same server as the last
    ts = pymesync.TimeSync(baseurl=timesync_url)

    # No response from server
    return list()


def create_time():
    """Creates a new time and submits it to the TimeSync server"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    # The data to send to the server containing the new time information
    post_data = get_fields([("#duration",   "Duration in seconds"),
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

    # The data to send to the server containing revised time information
    post_data = get_fields([("*#duration",   "Duration in seconds"),
                            ("*project",     "Project slug"),
                            ("*user",        "New user"),
                            ("*!activities", "Activity slugs"),
                            ("*date_worked", "Date worked (yyyy-mm-dd)"),
                            ("*issue_url",   "Issue URI"),
                            ("*notes",       "Notes")])

    # Attempt to update a time and return the reponse
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

    # Attempt to query the server for times with filtering parameters
    return ts.get_times(query_parameters=post_data)


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

            print ""
            print "Project: %s" % project
            print "Hours: %d" % (time_sum // 3600)
            print "Minutes: %d" % ((time_sum % 3600) // 60)
            print "Seconds: %d" % (time_sum % 60)

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
    really = get_field("Do you really want to delete {}?".format(uuid),
                       field_type="?")

    # If the user really wants to delete it
    if really:
        return ts.delete_time(uuid=uuid)

    # If no, return an empty list
    else:
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
                            ("*!slugs", "By project slug")])

    # Attempt to query the server with filtering parameters
    return ts.get_projects(query_parameters=post_data)


def delete_project():
    """Deletes a project from the TimeSync server"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    slug = get_field("Project slug")
    really = get_field("Do you really want to delete {}?".format(slug),
                       field_type="?")

    # If the user really wants to delete it
    if really:
        return ts.delete_project(slug=slug)

    # If no, return an empty list
    else:
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
    really = get_field("Do you really want to delete {}?".format(slug),
                       field_type="?")

    # If the user really wants to delete it
    if really:
        return ts.delete_activity(slug=slug)

    # If no, return an empty list
    else:
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
    really = get_field("Do you really want to delete {}?".format(username),
                       field_type="?")

    # If the user really wants to delete it
    if really:
        return ts.delete_user(username=username)

    # If no, return an empty list
    else:
        return list()


def menu():
    """Provides the user with menu options and executes commands"""

    print menu_options

    choice = raw_input(">> ")
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

    elif choice == "q":
        sys.exit(0)

    else:
        print "Invalid response"

    # Print server response
    print_json(response)


def main():
    global arg_username, arg_password, timesync_url, ts

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--connect", help="connect to a timesync server")
    parser.add_argument("-u", "--username", help="specify your username")
    parser.add_argument("-p", "--password", help="specify your password")

    # Command line arguments
    args = parser.parse_args()

    if args.connect:
        timesync_url = args.connect

        # Attempt to connect with the provided URL
        ts = pymesync.TimeSync(baseurl=timesync_url)

    if args.username:
        arg_username = args.username

    if args.password:
        arg_password = args.password

    # If all args are provided, attempt to sign in
    if timesync_url and arg_username and arg_password:
        print_json(sign_in())

    while True:
        menu()

if __name__ == "__main__":
    main()
