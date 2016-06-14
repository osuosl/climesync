from datetime import date

import pymesync
from docopt import docopt

import util

# climesync_command decorator
class climesync_command():

    def __init__(self, select_arg=None):
        self.select_arg = select_arg

    def __call__(self, command):
        def wrapped_command(argv=None):
            if argv:
                args = docopt(command.__doc__, argv=argv)

                # Put values gotten from docopt into a dictionary with Pymesync keys
                post_data = util.fix_args(args)
                
                if self.select_arg:
                    select = post_data.pop(self.select_arg)
                    return command(post_data, select)
                else:
                    return command(post_data)

            else:
                return command()

        return wrapped_command


ts = None  # pymesync.TimeSync object


def connect(arg_url="", config_dict=dict(), test=False, interactive=True):
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
        url = raw_input("URL of TimeSync server: ") if not test else "tst"

    if interactive and not test:
        util.add_kv_pair("timesync_url", url)

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


def sign_in(arg_user="", arg_pass="", config_dict=dict(), interactive=True):
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
        username = raw_input("Username: ")

    if arg_pass:
        password = arg_pass
    elif "password" in config_dict:
        password = config_dict["password"]
    else:
        password = raw_input("Password: ")

    if interactive and not ts.test:
        util.add_kv_pair("username", username)
        util.add_kv_pair("password", password)

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


@climesync_command()
def create_time(post_data=None):
    """create-time

Usage: create-time [-h] <duration> <project> <activities>
                       [--date-worked=<date_worked>]
                       [--issue-uri=<issue_uri>]
                       [--notes=<notes>]

Arguments:
    <duration>    Duration of time entry
    <project>     Slug of project worked on
    <activities>  Slugs of activities worked on

Options:
    -h --help                    Show this help message and exit
    --date-worked=<date_worked>  The date of the entry [Default: today]
    """

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    # The data to send to the server containing the new time information
    
    if not post_data:
        post_data = util.get_fields([(":duration",   "Duration"),
                                     ("project",     "Project slug"),
                                     ("!activities", "Activity slugs"),
                                     ("date_worked", "Date (yyyy-mm-dd)"),
                                     ("*issue_uri",  "Issue URI"),
                                     ("*notes",      "Notes")])

    # Today's date
    if post_data["date_worked"] == "today":
        post_data["date_worked"] = date.today().isoformat()

    # If activities was sent as a single item
    if isinstance(post_data["activities"], str):
        post_data["activities"] = [post_data["activities"]]

    # Use the currently authenticated user
    post_data["user"] = ts.user

    # Attempt to create a time and return the response
    return ts.create_time(time=post_data)


def update_time(post_data=None):
    """Sends revised time information to the TimeSync server"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    uuid = util.get_field("UUID of time to update")

    
    # The data to send to the server containing revised time information
    post_data = util.get_fields([("*:duration",   "Duration"),
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
    post_data = util.get_fields([("*!user", "Submitted by users"),
                                 ("*!project", "Belonging to projects"),
                                 ("*!activity", "Belonging to activities"),
                                 ("*start", "Beginning on date"),
                                 ("*end", "Ending on date"),
                                 ("*?include_revisions", "Include revised times?"),
                                 ("*?include_deleted", "Include deleted times?"),
                                 ("*uuid", "By UUID")])

    times = ts.get_times(query_parameters=post_data)

    # If the response is free of errors, make the times human-readable
    if 'error' not in times and 'pymesync error' not in times:
        for time in times:
            time["duration"] = util.to_readable_time(time["duration"])

    # Attempt to query the server for times with filtering parameters
    return times


def sum_times():
    """Sums all the times associated with a specific project"""

    query = util.get_fields([("!project", "Project slugs"),
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
            print util.to_readable_time(time_sum)

        return list()
    except Exception as e:
        print e
        return result


def delete_time():
    """Deletes a time from the TimeSync server"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    uuid = util.get_field("Time UUID")
    really = util.get_field("Do you really want to delete {}?".format(uuid),
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
    post_data = util.get_fields([("name", "Project name"),
                                 ("!slugs", "Project slugs"),
                                 ("*uri", "Project URI"),
                                 ("*!users", "Users"),
                                 ("*default_activity", "Default activity")])
     
    # If users have been added to the project, ask for user permissions
    if "users" in post_data:
        users = post_data["users"]
        post_data["users"] = util.get_user_permissions(users)

    # Attempt to create a new project and return the response
    return ts.create_project(project=post_data)


def update_project():
    """Sends revised project information to the TimeSync server"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    slug = util.get_field("Slug of project to update")

    # The data to send to the server containing revised project information
    post_data = util.get_fields([("*name", "Updated project name"),
                                 ("*!slugs", "Updated project slugs"),
                                 ("*uri", "Updated project URI"),
                                 ("*!users", "Updated users"),
                                 ("*default_activity", "Updated default activity")])

    # If user permissions are going to be updated, ask for them
    if "users" in post_data:
        users = post_data["users"]
        post_data["users"] = util.get_user_permissions(users)

    # Attempt to update the project information and return the response
    return ts.update_project(project=post_data, slug=slug)


def get_projects():
    """Queries the TimeSync server for projects with optional filters"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    # Optional filtering parameters
    print "Filtering projects..."
    post_data = util.get_fields([("*?include_revisions", "Include revisions?"),
                                 ("*?include_deleted", "Include deleted?"),
                                 ("*!slugs", "By project slug")])

    # Attempt to query the server with filtering parameters
    return ts.get_projects(query_parameters=post_data)


def delete_project():
    """Deletes a project from the TimeSync server"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    slug = util.get_field("Project slug")
    really = util.get_field("Do you really want to delete {}?".format(slug),
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
    post_data = util.get_fields([("name", "Activity name"),
                                 ("slug", "Activity slug")])

    # Attempt to create a new activity and return the response
    return ts.create_activity(activity=post_data)


def update_activity():
    """Sends revised activity information to the TimeSync server"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    slug_to_update = util.get_field("Slug of activity to update")

    # The data to send to the server containing revised activity information
    post_data = util.get_fields([("*name", "Updated activity name"),
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

    slug = util.get_field("Activity slug")
    really = util.get_field("Do you really want to delete {}?".format(slug),
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
    post_data = util.get_fields([("username", "New user username"),
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

    username_to_update = util.get_field("Username of user to update")

    # The data to send to the server containing revised user information
    post_data = util.get_fields([("*username", "Updated username"),
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
    username = util.get_field("By username", optional=True)

    # Attempt to query the server with filtering parameters
    return ts.get_users(username=username)


def delete_user():
    """Deletes a user from the TimeSync server"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    username = util.get_field("Username")
    really = util.get_field("Do you really want to delete {}?".format(username),
                            field_type="?")

    if really:  # If the user really wants to delete it
        return ts.delete_user(username=username)
    else:  # If no, return an empty list
        return list()


