from datetime import date, datetime

import pymesync
from docopt import docopt

import util

ts = None  # pymesync.TimeSync object

autoupdate_config = True
ldap = False  # Use LDAP?


# climesync_command decorator
class climesync_command():

    def __init__(self, select_arg=None, optional_args=False):
        self.select_arg = select_arg
        self.optional_args = optional_args

    def __call__(self, command):
        def wrapped_command(argv=None):
            if argv is not None:
                args = docopt(command.__doc__, argv=argv)

                command_kwargs = {}

                # Put values gotten from docopt into a Pymesync dictionary
                post_data = util.fix_args(args, self.optional_args)

                if self.select_arg:
                    command_kwargs[self.select_arg] = \
                            post_data.pop(self.select_arg)

                if post_data or self.select_arg not in command_kwargs:
                    command_kwargs["post_data"] = post_data

                roles = ("--members", "--managers", "--spectators")

                if any(args.get(r) for r in roles):
                    command_kwargs["role"] = [r for r in roles
                                              if args.get(r)][0]

                return command(**command_kwargs)
            else:
                if util.check_token_expiration(ts):
                    return {"error": "You need to sign in."}

                return command()

        return wrapped_command


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
    elif interactive:
        url = util.get_field("URL of TimeSync server") if not test else "tst"
    else:
        return {"climesync error": "Couldn't connect to TimeSync. Is "
                                   "timesync_url set in ~/.climesyncrc?"}

    if interactive and not test and autoupdate_config:
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
    auth_type = "ldap" if ldap else "password"

    # If username or password in config, use them at program startup.
    if arg_user:
        username = arg_user
    elif "username" in config_dict:
        username = config_dict["username"]
    elif interactive:
        username = util.get_field("Username")

    if arg_pass:
        password = arg_pass
    elif "password" in config_dict:
        password = config_dict["password"]
    elif interactive:
        password = util.get_field("Password", field_type="$")

    if not username or not password:
        return {"climesync error": "Couldn't authenticate with TimeSync. Are "
                                   "username and password set in "
                                   "~/.climesyncrc?"}

    if interactive and not ts.test and autoupdate_config:
        util.add_kv_pair("username", username)
        util.add_kv_pair("password", password)

    # Attempt to authenticate and return the server's response
    return ts.authenticate(username, password, auth_type)


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


def update_settings():
    """Prompts the user to update their password, display name, and/or email
    address"""

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    username = ts.user
    post_data = util.get_fields([("*password", "Updated password"),
                                 ("*display_name", "Updated display name"),
                                 ("*email", "Updated email address")])

    return ts.update_user(user=post_data, username=username)


@climesync_command(optional_args=True)
def create_time(post_data=None):
    """create-time

Usage: create-time [-h] <duration> <project> [<activities> ...]
                        [--date-worked=<date_worked>]
                        [--issue-uri=<issue_uri>]
                        [--notes=<notes>]

Arguments:
    <duration>    Duration of time entry
    <project>     Slug of project worked on
    <activities>  Slugs of activities worked on (Optional if the project has
                  a default activity)

Options:
    -h --help                    Show this help message and exit
    --date-worked=<date_worked>  The date of the entry [Default: today]
    --issue-uri=<issue_uri>      The URI of the issue on an issue tracker
    --notes=<notes>              Additional notes

Examples:
    climesync.py create-time 1h0m projectx docs design qa
`       --issue-uri=https//www.github.com/foo/projectx/issue/42

    climesync.py create-time 0h45m projecty design --notes="Designing the API"
    """

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    # The data to send to the server containing the new time information
    if post_data is None:
        post_data = util.get_fields([(":duration",   "Duration"),
                                     ("date_worked", "Date (yyyy-mm-dd)"),
                                     ("project",     "Project slug")])

        project_slug = post_data["project"]

        project = ts.get_projects({"slug": project_slug})[0]

        if "error" in project or "pymesync error" in project:
            return project

        if not ts.test and project["default_activity"]:
            activity_query = "*!activities"
        else:
            activity_query = "!activities"

        post_data_cont = util.get_fields([(activity_query, "Activity slugs"),
                                          ("*issue_uri",  "Issue URI"),
                                          ("*notes",      "Notes")])

        post_data.update(post_data_cont)

    # Today's date
    if post_data["date_worked"] == "today":
        post_data["date_worked"] = date.today().isoformat()

    # If activities was sent as a single item
    if "activities" in post_data and isinstance(post_data["activities"], str):
        post_data["activities"] = [post_data["activities"]]

    # Use the currently authenticated user
    post_data["user"] = ts.user

    # Attempt to create a time and return the response
    return ts.create_time(time=post_data)


@climesync_command(select_arg="uuid", optional_args=True)
def update_time(post_data=None, uuid=None):
    """update-time

Usage: update-time [-h] <uuid> [--duration=<duration>]
                        [--project=<project>]
                        [--user=<user>]
                        [--activities=<activities>]
                        [--date-worked=<date worked>]
                        [--issue-uri=<issue uri>]
                        [--notes=<notes>]

Arguments:
    <uuid>  The UUID of the time to update

Options:
    -h --help                    Show this help message and exit
    --duration=<duration>        Duration of time entry
    --project=<project>          Slug of project worked on
    --user=<user>                New time owner
    --activities=<activities>    Slugs of activities worked on
    --date-worked=<date worked>  The date of the entry
    --issue-uri=<issue uri>      The URI of the issue on an issue tracker
    --notes=<notes>              Additional notes

Examples:
    climesync.py update-time 838853e3-3635-4076-a26f-7efr4e60981f
`       --activities="[dev planning code]" --date-worked=2016-06-15

    climesync.py update-time c3706e79-1c9a-4765-8d7f-89b4544cad56
`       --project=projecty --notes="Notes notes notes"
    """

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    if uuid is None:
        uuid = util.get_field("UUID of time to update")

    # The data to send to the server containing revised time information
    if post_data is None:
        current_time = ts.get_times({"uuid": uuid})[0]

        if "error" in current_time or "pymesync error" in current_time:
            return current_time

        post_data = util.get_fields([("*:duration",   "Duration"),
                                     ("*project",     "Project slug"),
                                     ("*user",        "New user"),
                                     ("*!activities", "Activity slugs"),
                                     ("*date_worked", "Date (yyyy-mm-dd)"),
                                     ("*issue_uri",   "Issue URI"),
                                     ("*notes",       "Notes")],
                                    current_object=current_time)

    if "activities" in post_data and isinstance(post_data["activities"], str):
        post_data["activities"] = [post_data["activities"]]

    # Attempt to update a time and return the response
    return ts.update_time(uuid=uuid, time=post_data)


@climesync_command(optional_args=True)
def get_times(post_data=None):
    """get-times

Usage: get-times [-h] [--user=<users>] [--project=<projects>]
                      [--activity=<activities>] [--start=<start date>]
                      [--end=<end date>] [--uuid=<uuid>]
                      [--include-revisions=<True/False>]
                      [--include-deleted=<True/False>]

Options:
    -h --help                         Show this help message and exit
    --user=<users>                    Filter by a list of users
    --project=<projects>              Filter by a list of project slugs
    --activity=<activities>           Filter by a list of activity slugs
    --start=<start date>              Filter by start date
    --end=<end date>                  Filter by end date
    --uuid=<uuid>                     Get a specific time by uuid
                                      (If included, all options except
                                      --include-revisions and
                                      --include-deleted are ignored
`   --include-revisions=<True/False>  Whether to include all time revisions
`   --include-deleted=<True/False>    Whether to include deleted times

Examples:
    climesync.py get-times

    climesync.py get-times --project=projectx --activity=planning
`       --user="[userone usertwo]"

    climesync.py get-times --uuid=12345676-1c9a-rrrr-bbbb-89b4544cad56
    """

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    interactive = False if post_data else True

    # Optional filtering parameters to send to the server
    if post_data is None:
        post_data = util.get_fields([("*!user", "Submitted by users"),
                                     ("*!project", "Belonging to projects"),
                                     ("*!activity", "Belonging to activities"),
                                     ("*start", "Beginning on date"),
                                     ("*end", "Ending on date"),
                                     ("*?include_revisions", "Allow revised?"),
                                     ("*?include_deleted", "Allow deleted?"),
                                     ("*uuid", "By UUID")])

    if "user" in post_data and isinstance(post_data["user"], str):
        post_data["user"] = [post_data["user"]]

    if "project" in post_data and isinstance(post_data["project"], str):
        post_data["project"] = [post_data["project"]]

    if "activity" in post_data and isinstance(post_data["activity"], str):
        post_data["activity"] = [post_data["activity"]]

    if "start" in post_data:
        post_data["start"] = [post_data["start"]]

    if "end" in post_data:
        post_data["end"] = [post_data["end"]]

    times = ts.get_times(query_parameters=post_data)

    if interactive and not times:
        return {"note": "No times were returned"}

    # Attempt to query the server for times with filtering parameters
    return times


@climesync_command(optional_args=True)
def sum_times(post_data=None):
    """sum-times

Usage: sum-times [-h] <project> ... [--start=<start date>] [--end=<end date>]

Arguments:
    <project>  The project slugs of the projects to sum times for

Options:
    -h --help             Show this help message and exit
    --start=<start date>  The date to start summing times
    --end=<end date>      The date to end summing times

Examples:
    climesync.py sum-times projectx

    climesync.py sum-times projectx projecty --start=2016-06-01
    """

    if post_data is None:
        post_data = util.get_fields([("!project", "Project slugs"),
                                     ("*start", "Start date (yyyy-mm-dd)"),
                                     ("*end", "End date (yyyy-mm-dd)")])

    if isinstance(post_data["project"], str):
        post_data["project"] = [post_data["project"]]

    result = ts.get_times(post_data)

    try:
        for project in post_data["project"]:
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


@climesync_command(select_arg="uuid")
def delete_time(uuid=None):
    """delete-time

Usage: delete-time [-h] <uuid>

Arguments:
    <uuid>  The uuid of the time to delete

Options:
    -h --help  Show this help message and exit

Examples:
    climesync.py delete-time 12345676-1c9a-rrrr-bbbb-89b4544cad56
    """

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    if uuid is None:
        uuid = util.get_field("Time UUID")
        really = util.get_field(u"Do you really want to delete {}?"
                                .format(uuid),
                                field_type="?")

        if not really:
            return list()

    return ts.delete_time(uuid=uuid)


@climesync_command(optional_args=True)
def create_project(post_data=None):
    """create-project (Site admins only)

Usage: create-project [-h] <name> <slugs> [(<username> <access_mode>) ...]
                           [--uri=<project_uri>]
                           [--default-activity=<default_activity>]

Arguments:
    <name>         The project name
    <slugs>        Unique slugs associated with this project
    <username>     The name of a user to add to the project
    <access_mode>  The permissions of a user to add to the project

Options:
    -h --help                              Show this help message and exit
    --uri=<project_uri>                    The project's URI
    --default-activity=<default_activity>  The slug of the default activity
                                           associated with this project

User permissions help:
    User permissions are entered in a similar format to *nix file permissions.
    Each possible permission is represented as a binary 0 or 1 in the following
    format where each argument is a binary 0 or 1:

    <member><spectator><manager>

    For example, to set a user's permission level to both member and manager
    this would be the permission number:

    <member = 1><spectator = 0><manager = 1> == 101 == 5

    So the entire command would be entered as:

    create-project <name> <slugs> <username> 5

Examples:
    climesync.py create-project "Project Z" "[pz projectz]"
`       userone 4 usertwo 5 userthree 7

    climesync.py create-project "Project Foo" foo userone 7
`       --uri=https://www.github.com/bar/foo --default-activity=planning
    """

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    # The data to send to the server containing new project information
    if post_data is None:
        post_data = util.get_fields([("name", "Project name"),
                                     ("!slugs", "Project slugs"),
                                     ("*uri", "Project URI"),
                                     ("*default_activity",
                                      "Default activity"),
                                     ("*!users", "Users")])
    else:
        permissions_dict = dict(zip(post_data.pop("username"),
                                    post_data.pop("access_mode")))
        post_data["users"] = util.fix_user_permissions(permissions_dict)

    # If users have been added to the project, ask for user permissions
    if "users" in post_data and not isinstance(post_data["users"], dict):
        users = post_data["users"]
        post_data["users"] = util.get_user_permissions(users)

    if isinstance(post_data["slugs"], str):
        post_data["slugs"] = [post_data["slugs"]]

    # Attempt to create a new project and return the response
    return ts.create_project(project=post_data)


@climesync_command(select_arg="slug", optional_args=True)
def update_project(post_data=None, slug=None):
    """update-project (Site admins only)

Usage: update-project [-h] <slug> [--name=<project_name>]
                           [--slugs=<project_slugs>]
                           [--uri=<project_uri>]
                           [--default-activity=<default_activity>]

Arguments:
    <slug>  The slug of the project

Options:
    -h --help                              Show this help message and exit
    --name=<project_name>                  Updated project name
    --slugs=<project_slugs>                Updated list of project slugs
    --uri=<project_uri>                    Updated project's URI
    --default-activity=<default_activity>  Updated slug of the default activity
                                           associated with this project

Examples:
    climesync.py update-project foo --name=Foobarbaz --slugs="[foo bar baz]"

    climesync.py update-project pz --uri=https://www.github.com/bar/projectz
    """

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    if slug is None:
        slug = util.get_field("Slug of project to update")

    # The data to send to the server containing revised project information
    if post_data is None:
        current_project = ts.get_projects({"slug": slug})[0]

        if "error" in current_project or "pymesync error" in current_project:
            return current_project

        post_data = util.get_fields([("*name", "Updated project name"),
                                     ("*!slugs", "Updated project slugs"),
                                     ("*uri", "Updated project URI"),
                                     ("*default_activity",
                                      "Updated default activity")],
                                    current_object=current_project)

    if "slugs" in post_data and isinstance(post_data["slugs"], str):
        post_data["slugs"] = [post_data["slugs"]]

    # Attempt to update the project information and return the response
    return ts.update_project(project=post_data, slug=slug)


@climesync_command(select_arg="slug")
def update_project_users(post_data=None, slug=None):
    """update-project-users (Site admins/Site managers/Project managers only)

Usage: update-project-users [-h] <slug> (<username> <access_mode>) ...

Arguments:
    <slug>         The slug of the project
    <username>     The username of the user to either update or add to the
                   project
    <access_mode>  The new access mode of the user

User permissions help:
    User permissions are entered in a similar format to *nix file permissions.
    Each possible permission is represented as a binary 0 or 1 in the following
    format where each argument is a binary 0 or 1:

    <member><spectator><manager>

    For example, to set a user's permission level to both member and manager
    this would be the permission number:

    <member = 1><spectator = 0><manager = 1> == 101 == 5

    So the entire command would be entered as:

    update-project <name> <slugs> <username> 5

Examples:
    climesync.py update-project-users proj_foo newuser 4 olduser 6

    climesync.py update-project-users proj_bar olduser1 4 olduser2 7
    """

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    if slug is None:
        slug = util.get_field("Slug of project to update")

    if post_data is None:
        current_project = ts.get_projects({"slug": slug})[0]

        if "error" in current_project or "pymesync error" in current_project:
            return current_project

        post_data = util.get_fields([("*!users", "Users to add/update")],
                                    current_object=current_project)
    else:
        permissions_dict = dict(zip(post_data.pop("username"),
                                    post_data.pop("access_mode")))
        post_data["users"] = util.fix_user_permissions(permissions_dict)

    if "users" in post_data and not isinstance(post_data["users"], dict):
        users_list = post_data["users"]
        current_users = current_project["users"]
        post_data["users"] = util.get_user_permissions(users_list,
                                                       current_users)

    old_project = ts.get_projects(query_parameters={"slug": slug})[0]

    if "error" in old_project or "pymesync error" in old_project:
        return old_project

    users = old_project.setdefault("users", {})
    users.update(post_data["users"])

    return ts.update_project(project={"users": users}, slug=slug)


@climesync_command(select_arg="slug")
def remove_project_users(post_data=None, slug=None):
    """remove-project-users (Site admins/Site managers/Project managers only)

Usage: remove-project-users [-h] <slug> <users> ...

Arguments:
    <slug>      The slug of the project
    <username>  The username of the user to remove

Examples:
    climesync.py remove-project-users proj_foo user1 user2

    climesync.py remove-project-users proj_bar user1
    """

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    if slug is None:
        slug = util.get_field("Slug of project to update")

    if post_data is None:
        current_project = ts.get_projects({"slug": slug})[0]

        if "error" in current_project or "pymesync error" in current_project:
            return current_project

        post_data = util.get_fields([("*!users", "Users to remove")],
                                    current_object=current_project)

    old_project = ts.get_projects(query_parameters={"slug": slug})[0]

    if "error" in old_project or "pymesync error" in old_project:
        return old_project

    to_remove = post_data["users"] if "users" in post_data else []
    users = old_project.setdefault("users", {})

    if any(user not in users for user in to_remove):
        return {"error": "User doesn't exist in project"}

    users = {user: perms for user, perms in users.iteritems()
             if user not in to_remove}

    return ts.update_project(project={"users": users}, slug=slug)


@climesync_command(optional_args=True)
def get_projects(post_data=None):
    """get-projects

Usage: get-projects [-h] [--include-revisions=<True/False>]
                         [--include-deleted=<True/False>]
                         [--slug=<slug>]

Options:
    -h --help                         Show this help message and exit
    --include-revisions=<True/False>  Whether to include revised entries
    --include-deleted=<True/False>    Whether to include deleted entries
    --slug=<slug>                     Filter by project slug

Examples:
    climesync.py get-projects

    climesync.py get-projects --slug=projectx --include-revisions=True
    """

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    interactive = False if post_data else True

    # Optional filtering parameters
    if post_data is None:
        post_data = util.get_fields([("*?include_revisions", "Allow revised?"),
                                     ("*?include_deleted", "Allow deleted?"),
                                     ("*slug", "By project slug")])

    # Attempt to query the server with filtering parameters
    projects = ts.get_projects(query_parameters=post_data)

    if interactive and not projects:
        return {"note": "No projects were returned"}

    if "error" in projects[0] or "pymesync error" in projects[0]:
        return projects

    for project in projects:
        proj_slug = project["slugs"][0]
        proj_times = ts.get_times(query_parameters={"project": [proj_slug]})

        if not proj_times or \
           "error" in proj_times[0] or "pymesync error" in proj_times[0]:
            continue

        proj_time_sum = util.to_readable_time(sum(t["duration"]
                                                  for t in proj_times))
        proj_num_entries = len(proj_times)
        proj_latest_time = max(datetime.strptime(t["date_worked"], "%Y-%m-%d")
                               for t in proj_times).date().isoformat()
        proj_first_time = min(datetime.strptime(t["date_worked"], "%Y-%m-%d")
                              for t in proj_times).date().isoformat()

        project["time_total"] = proj_time_sum
        project["num_times"] = proj_num_entries
        project["latest_time"] = proj_latest_time
        project["first_time"] = proj_first_time

    return projects


@climesync_command(select_arg="slug")
def delete_project(slug=None):
    """delete-project (Site admins only)

Usage: delete-project [-h] <slug>

Arguments:
    <slug>  The slug of the project to delete

Options:
    -h --help  Show this help message and exit

Examples:
    climesync.py delete-project foo
    """

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    if slug is None:
        slug = util.get_field("Project slug")
        really = util.get_field(u"Do you really want to delete {}?"
                                .format(slug),
                                field_type="?")

        if not really:
            return list()

    return ts.delete_project(slug=slug)


@climesync_command()
def create_activity(post_data=None):
    """create-activity (Site admins only)

Usage: create-activity [-h] <name> <slug>

Arguments:
    <name>  The name of the new activity
    <slug>  The slug of the new activity

Options:
    -h --help  Show this help message and exit

Examples:
    climesync.py create-activity Coding code

    climesync.py create-activity "Project Planning" planning
    """

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    # The data to send to the server containing new activity information
    if post_data is None:
        post_data = util.get_fields([("name", "Activity name"),
                                     ("slug", "Activity slug")])

    # Attempt to create a new activity and return the response
    return ts.create_activity(activity=post_data)


@climesync_command(select_arg="old_slug", optional_args=True)
def update_activity(post_data=None, old_slug=None):
    """update-activity (Site admins only)

Usage: update-activity [-h] <old_slug> [--name=<name>] [--slug=<slug>]

Arguments:
    <old_slug>  The slug of the activity to update

Options:
    -h --help      Show this help message and exit
    --name=<name>  The updated activity name
    --slug=<slug>  The updated activity slug

Examples:
    climesync.py update-activity planning --name=Planning

    climesync.py update-activity code --slug=coding
    """

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    if old_slug is None:
        old_slug = util.get_field("Slug of activity to update")

    # The data to send to the server containing revised activity information
    if post_data is None:
        current_activity = ts.get_activities({"slug": old_slug})[0]

        if "error" in current_activity or "pymesync error" in current_activity:
            return current_activity

        post_data = util.get_fields([("*name", "Updated activity name"),
                                     ("*slug", "Updated activity slug")],
                                    current_object=current_activity)

    # Attempt to update the activity information and return the repsonse
    return ts.update_activity(activity=post_data, slug=old_slug)


@climesync_command(optional_args=True)
def get_activities(post_data=None):
    """get-activities

Usage: get-activities [-h] [--include-revisions=<True/False>]
                           [--include-deleted=<True/False>]
                           [--slug=<slug>]

Options:
    -h --help                         Show this help message and exit
    --include-revisions=<True/False>  Whether to include revised entries
    --include-deleted=<True/False>    Whether to include deleted entries
    --slug=<slug>                     Filter by activity slug

Examples:
    climesync.py get-activities

    climesync.py get-activities --include-deleted=True

    climesync.py get-activities --slug=planning
    """

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    interactive = False if post_data else True

    # Optional filtering parameters
    if post_data is None:
        post_data = util.get_fields([("*?include_revisions", "Allow revised?"),
                                     ("*?include_deleted", "Allow deleted?"),
                                     ("*slug", "By activity slug")])

    # Attempt to query the server with filtering parameters
    activities = ts.get_activities(query_parameters=post_data)

    if interactive and not activities:
        return {"note": "No activities were returned"}

    return activities


@climesync_command(select_arg="slug")
def delete_activity(slug=None):
    """delete-activity (Site admins only)

Usage: delete-activity [-h] <slug>

Arguments:
    <slug>  The slug of the activity to delete

Options:
    -h --help  Show this help message and exit

Examples:
    climesync.py delete-activity planning
    """

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    if slug is None:
        slug = util.get_field("Activity slug")
        really = util.get_field(u"Do you really want to delete {}?"
                                .format(slug),
                                field_type="?")

        if not really:
            return list()

    return ts.delete_activity(slug=slug)


@climesync_command(optional_args=True)
def create_user(post_data=None):
    """create-user (Site admins only)

Usage: create-user [-h] <username> <password> [--display-name=<display_name>]
                        [--email=<email>] [--site-admin=<True/False>]
                        [--site-manager=<True/False>]
                        [--site-spectator=<True/False>] [--meta=<metainfo>]
                        [--active=<True/False>]

Arguments:
    <username>  The username of the new user
    <password>  The password of the new user

Options:
    -h --help                      Show this help message and exit
    --display-name=<display_name>  The display name of the new user
    --email=<email>                The email address of the new user
    --site-admin=<True/False>      Whether the new user is a site admin
                                   [Default: False]
    --site-manager=<True/False>    Whether the new user is a site manager
                                   [Default: False]
    --site-spectator=<True/False>  Whether the new user is a site spectator
                                   [Default: False]
    --meta=<metainfo>              Extra user metainformation
    --active=<True/False>          Whether the new user is active
                                   [Default: True]

Examples:
    climesync.py create-user userfour pa$$word --display-name=4chan
`       --meta="Who is this 4chan?"

    climesync.py create-user anotheruser "correct horse battery staple"
`       --email=anotheruser@osuosl.org --site-admin=True
    """

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    # The data to send to the server containing new user information
    if post_data is None:
        post_data = util.get_fields([("username", "New user username"),
                                     ("$password", "New user password"),
                                     ("*display_name", "New display name"),
                                     ("*email", "New user email"),
                                     ("*?site_admin", "Site admin?"),
                                     ("*?site_manager", "Site manager?"),
                                     ("*?site_spectator", "Site spectator?"),
                                     ("*meta", "Extra meta-information"),
                                     ("*?active", "Is the new user active?")])

    # Attempt to create a new user and return the response
    return ts.create_user(user=post_data)


@climesync_command(select_arg="old_username", optional_args=True)
def update_user(post_data=None, old_username=None):
    """update-user (Site admins only)

Usage: update-user [-h] <old_username> [--username=<username>]
                        [--password=<password>] [--display-name=<display_name>]
                        [--email=<email>] [--site-admin=<True/False>]
                        [--site-manager=<True/False>]
                        [--site-spectator=<True/False>] [--meta=<metainfo>]
                        [--active=<True/False>]

Arguments:
    <old_username>  The username of the user to update

Options:
    -h --help                      Show this help message and exit
    --username=<username>          The updated username of the user
    --password=<password>          The updated password of the user
    --display-name=<display_name>  The updated display name of the user
    --email=<email>                The updated email address of the user
    --site-admin=<True/False>      Whether the user is a site admin
    --site-manager=<True/False>    Whether the user is a site manager
    --site-spectator=<True/False>  Whether the user is a site spectator
    --meta=<metainfo>              Extra user metainformation
    --active=<True/False>          Whether the user is active

Examples:
    climesync.py update-user userfour --display-name="System Administrator"
`       --active=False --site-spectator=True

    climesync.py update-user anotheruser --username=newuser
`       --meta="Metainformation goes here" --site-admin=False
    """

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    if old_username is None:
        old_username = util.get_field("Username of user to update")

    # The data to send to the server containing revised user information
    if post_data is None:
        current_user = ts.get_users(username=old_username)[0]

        if "error" in current_user or "pymesync error" in current_user:
                return current_user

        post_data = util.get_fields([("*username", "Updated username"),
                                     ("*$password", "Updated password"),
                                     ("*display_name", "Updated display name"),
                                     ("*email", "Updated email"),
                                     ("*?site_admin", "Site admin?"),
                                     ("*?site_manager", "Site manager?"),
                                     ("*?site_spectator", "Site spectator?"),
                                     ("*meta", "New metainformation"),
                                     ("*?active", "Is the user active?")],
                                    current_object=current_user)

    # Attempt to update the user and return the response
    return ts.update_user(user=post_data, username=old_username)


@climesync_command(optional_args=True)
def get_users(post_data=None, role=None):
    """get-users

Usage: get-users [-h] [--meta=<metainfo>] [--username=<username>] |
                     ([--project=<project>
                      [--members|--managers|--spectators]])

Options:
    -h --help              Show this help message and exit
    --username=<username>  Search for a user by username

Examples:
    climesync.py get-users

    climesync.py get-users --username=userfour

    climesync.py get-users --project=p_foo --managers

    climesync.py get-users --meta="fulltime"
    """

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    interactive = post_data is None

    # Optional filtering parameters
    if interactive:
        post_data = util.get_fields([("*username", "Username")])

    # Using dict.get so that None is returned if the key doesn't exist
    username = post_data.get("username")

    # Get metadata filter parameter
    if "meta" in post_data:
        meta = post_data["meta"].upper()
    elif interactive and not username:
        meta = util.get_field("By metadata", optional=True).upper()
    else:
        meta = None

    if interactive and not username:
        post_data.update(util.get_fields([("*project", "By project slug")]))

    project = post_data.get("project")

    if project:
        project_users = ts.project_users(project=project)

        if "error" in project_users or "pymesync error" in project_users:
            return project_users

        if interactive:
            filter_members = util.get_field("Get project members?",
                                            optional=True,
                                            field_type="?")

            filter_managers = filter_spectators = False

            if not filter_members:
                filter_managers = util.get_field("Get project managers?",
                                                 optional=True,
                                                 field_type="?")

            if not filter_members and not filter_managers:
                filter_spectators = util.get_field("Get project spectators?",
                                                   optional=True,
                                                   field_type="?")

            if filter_members:
                role = "--members"
            elif filter_managers:
                role = "--managers"
            elif filter_spectators:
                role = "--spectators"
            else:
                role = ""

        users = []
        for user, roles in project_users.iteritems():
            if (role == "--members" and "member" not in roles) or \
               (role == "--managers" and "manager" not in roles) or \
               (role == "--spectators" and "spectator" not in roles):
                continue

            user_object = ts.get_users(username=user)[0]

            if "error" in user_object or "pymesync error" in user_object:
                return user_object

            users.append(user_object)
    else:
        users = ts.get_users(username=username)

    if interactive and not users:
        return {"note": "No users were returned"}
    elif not users:
        return []

    if "error" in users[0] or "pymesync error" in users[0]:
        return users

    if username:  # Get user projects
        projects = ts.get_projects()

        if "error" in projects[0] or "pymesync error" in projects[0]:
            util.print_json(projects)
        else:
            # Create a dictionary of projects that the user has a role in
            user_projects = {project["name"]: project["users"][username]
                             for project in projects
                             if username in project.setdefault("users", [])}

            users[0]["projects"] = user_projects
    elif meta:  # Filter users by substrings in metadata
        users = [user for user in users
                 if user["meta"] and meta in user["meta"].upper()]

    return users


@climesync_command(select_arg="username")
def delete_user(username=None):
    """delete-user (Site admins only)

Usage: delete-user [-h] <username>

Arguments:
    <username>  The username of the user to delete

Options:
    -h --help  Show this help message and exit

Examples:
    climesync.py delete-user userfour
    """

    global ts

    if not ts:
        return {"error": "Not connected to TimeSync server"}

    if username is None:
        username = util.get_field("Username")
        really = util.get_field(u"Do you really want to delete {}?"
                                .format(username),
                                field_type="?")

        if not really:
            return list()

    return ts.delete_user(username=username)
