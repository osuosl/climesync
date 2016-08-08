import ConfigParser
import os
import re
import stat
import codecs
import sys  # NOQA flake8 ignore
from collections import OrderedDict
from datetime import datetime
from getpass import getpass


def create_config(path="~/.climesyncrc"):
    """Create the configuration file if it doesn't exist"""

    realpath = os.path.expanduser(path)

    # Create the file if it doesn't exist then set its mode to 600 (Owner RW)
    with codecs.open(realpath, "w", "utf-8-sig") as f:
        f.write(u"# Climesync configuration file")

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

    # If read_config errored and returned None instead of a ConfigParser
    if not config:
        return

    # If the configuration file doesn't exist (read_config returned an
    # empty config), create it
    if "climesync" not in config.sections():
        create_config(path)

    # Attempt to set the option value in the config
    # If the "climesync" section doesn't exist (NoSectionError), create it
    try:
        config.set("climesync", key, value.encode("utf-8"))
    except ConfigParser.NoSectionError:
        config.add_section("climesync")
        config.set("climesync", key, value.encode("utf-8"))

    # Truncate existing file before writing to it
    with codecs.open(realpath, "w", "utf-8") as f:
        f.write(u"# Climesync configuration file\n")

        # Write the config values
        config.write(f)


def check_token_expiration(ts):
    """Checks to see if the auth token has expired. If it has, try to log the
    user back in using the username and password in their config file"""

    # If ts_token_expiration_time() returns a dict, there must be an error
    if type(ts.token_expiration_time()) is dict:
        return True

    # If the token is expired, try to log the user back in
    if ts and not ts.test and ts.token_expiration_time() <= datetime.now():
        config = read_config()
        username = config.get("climesync", "username")
        baseurl = config.get("climesync", "timesync_url")
        if baseurl[-1] == "/":
            baseurl = baseurl[:-1]

        if config.has_option("climesync", "username") \
           and config.has_option("climesync", "password") \
           and username == ts.user \
           and baseurl == ts.baseurl:
            username = config.get("climesync", "username")
            password = config.get("climesync", "password")

            ts.authenticate(username, password, "password")
        else:
            return True


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


def value_to_printable(value, **format_flags):
    """Formats values returned by Pymesync into nice-looking strings

    format_flags is a dictionary of boolean flags used to format the output in
    different ways

    Supported flags:
    time_value - Take the integer value and make it a human-readable time
    short_perms - Return users in a permissions dict but not permissions
    """

    if isinstance(value, list):  # List of values
        return ", ".join(value)
    elif isinstance(value, dict):  # Project permission dict
        if format_flags.get("short_perms"):
            return ", ".join(value.keys())

        users_sorted = list(reversed(sorted(value.keys(), key=len)))
        if users_sorted:
            max_name_len = len(users_sorted[0])

        user_strings = []
        for user in value:
            permissions = ", ".join([p for p in value[user] if value[user][p]])
            name_len = len(user)
            buffer_spaces = ' ' * (max_name_len - name_len)
            user_strings.append("\t{}{} <{}>".format(user, buffer_spaces,
                                                     permissions))

        return "\n" + "\n".join(user_strings)
    else:  # Something else (integer, string, etc.)
        if format_flags.get("time_value"):
            return to_readable_time(value)
        else:
            return "{}".format(value)


def print_json(response):
    """Prints raw JSON returned by Pymesync"""

    print ""

    if isinstance(response, list):  # List of dictionaries
        for json_dict in response:
            for key, value in json_dict.iteritems():
                time_value = True if key == "duration" else False
                print u"{}: {}" \
                      .format(key, value_to_printable(value,
                                                      time_value=time_value))

            print ""
    elif isinstance(response, dict):  # Plain dictionary
        for key, value in response.iteritems():
            time_value = True if key == "duration" else False
            print u"{}: {}" \
                  .format(key, value_to_printable(value,
                                                  time_value=time_value))

        print ""
    else:
        print "I don't know how to print that!"
        print response


def compare_date_worked(time_a, time_b):
    """"""

    date_format = "%Y-%m-%d"

    date_a = datetime.strptime(time_a["date_worked"], date_format)
    date_b = datetime.strptime(time_b["date_worked"], date_format)

    return date_a < date_b


def determine_data_type(data):
    """"""

    if not data:
        return ""

    if isinstance(data, list):
        data = data[0]

    if "duration" in data:
        return "time"
    elif "username" in data:
        return "user"
    elif "slugs" in data:
        return "project"
    elif "slug" in data:
        return "activity"
    else:
        return ""


def print_pretty_time(response):
    """Abandon all hope ye who enter here"""

    if isinstance(response, dict):
        time_data = {k: v for k, v in response.iteritems()
                     if k in ["uuid", "duration", "project", "activity",
                              "user", "date_worked"]}

        print_json(time_data)
    elif isinstance(response, list):
        times = sorted(response, cmp=compare_date_worked)
        projects = list({time["project"][0] for time in times})
        activities = list({a for time in times for a in time["activities"]})
        users = list({time["user"] for time in times})

        print

        sorted_times = OrderedDict((p, 0) for p in projects)

        min_leading_whitespace = 9

        # I sure hope no one submits a time over 9999h59m
        min_activity_whitespace = 10

        for project in projects:
            project_times = [t for t in times
                             if project in t["project"]]

            project_activities = [a for a in activities
                                  if any(a in t["activities"]
                                         for t in project_times)]

            project_users = [u for u in users
                             if any(u == t["user"]
                                    for t in project_times)]

            leading_whitespace = max([min_leading_whitespace] +
                                     [len(u) + 1 for u in project_users])

            activity_time_whitespace = [max(min_activity_whitespace,
                                            len(a) + 2)
                                        for a in project_activities]

            activity_whitespaces = [" "*(activity_time_whitespace[i] - len(a))
                                    for i, a in enumerate(project_activities)]

            activity_row = "".join("{}{}".format(a, w)
                                   for a, w in zip(project_activities,
                                                   activity_whitespaces))

            sorted_activity_time_sums = OrderedDict((a, 0)
                                                    for a
                                                    in project_activities)

            sorted_times[project] = OrderedDict((u, 0) for u in users)

            entry_text = "entry" if len(project_times) == 1 else "entries"

            print u"{} - {} {} ({} - {})".format(project,
                                                 len(project_times),
                                                 entry_text,
                                                 project_times[0]
                                                              ["date_worked"],
                                                 project_times[-1]
                                                              ["date_worked"])

            print u"{}{}".format(" "*leading_whitespace, activity_row)

            for user in project_users:
                user_times = [t for t in project_times
                              if user == t["user"]]

                user_activities = [a for a in project_activities
                                   if any(a in t["activities"]
                                          for t in user_times)]

                sorted_times[project][user] = OrderedDict((a, 0)
                                                          for a in
                                                          project_activities)

                for activity in user_activities:
                    activity_times = [t for t in user_times
                                      if activity in t["activities"]]

                    activity_time_sum = sum(t["duration"]
                                            for t in activity_times)

                    sorted_activity_time_sums[activity] += activity_time_sum
                    sorted_times[project][user][activity] = activity_time_sum

                activity_time_sums = [s for s in sorted_times[project][user]
                                      .itervalues()]

                activity_times = [to_readable_time(s)
                                  for s in activity_time_sums]

                user_time_sum = sum(t["duration"] for t in user_times)

                user_time_whitespace = " "*(leading_whitespace - len(user))

                time_whitespaces = [" "*(activity_time_whitespace[i] - len(t))
                                    for i, t in enumerate(activity_times)]

                time_row = "".join("{}{}".format(t, w)
                                   for t, w in zip(activity_times,
                                                   time_whitespaces))

                print u"{}{}{}Total: {}".format(user, user_time_whitespace,
                                                time_row,
                                                to_readable_time(
                                                    user_time_sum))

                sorted_times[project][user] = user_time_sum

            total_activity_time_sums = [s for s in sorted_activity_time_sums
                                        .itervalues()]

            total_activity_times = [to_readable_time(s)
                                    for s in total_activity_time_sums]

            project_time_sum = sum(t["duration"] for t in project_times)

            project_total_whitespace = " "*(leading_whitespace - 7)
            time_total_whitespaces = [" "*(activity_time_whitespace[i]
                                           - len(t))
                                      for i, t in enumerate(
                                                      total_activity_times)]

            time_total_row = "".join("{}{}".format(t, w)
                                     for t, w in zip(total_activity_times,
                                                     time_total_whitespaces))

            print u"Totals:{}{}Total: {}".format(project_total_whitespace,
                                                 time_total_row,
                                                 to_readable_time(
                                                     project_time_sum))

            sorted_times[project] = project_time_sum

            print
    else:
        print_json(response)


def print_pretty_project(response):
    """"""

    if isinstance(response, dict):
        response = [response]

    projects_data = []

    for project in response:
        project_data = OrderedDict()
        project_data = {k: v for k, v in project.iteritems()
                        if k in ["name", "slugs", "users"]}

        if "users" not in project_data:
            project_data["users"] = {}

        projects_data.append(project_data)

    print_json(projects_data)


def print_pretty_activity(response):
    """"""

    if isinstance(response, dict):
        response = [response]

    activity_data = []

    for activity in response:
        activity_data.append({k: v for k, v in activity.iteritems()
                              if k in ["name", "slug"]})

    print_json(activity_data)


def print_pretty_user(response):
    """"""

    if isinstance(response, dict):
        response = [response]

    user_data = []

    for user in response:
        user_data.append({k: v for k, v in user.iteritems()
                          if k in ["username", "display_name", "email",
                                   "active"]})

    print_json(user_data)


def print_pretty(response):
    """Attempts to print data returned by Pymesync nicely"""

    data_type = determine_data_type(response)

    if data_type == "time":
        print_pretty_time(response)
    elif data_type == "project":
        print_pretty_project(response)
    elif data_type == "activity":
        print_pretty_activity(response)
    elif data_type == "user":
        print_pretty_user(response)
    else:
        print_json(response)


def get_field(prompt, optional=False, field_type="", current=None):
    """Prompts the user for input and returns it in the specified format

    prompt - The prompt to display to the user
    optional - Whether or not the field is optional (defaults to False)
    field_type - The type of input. If left empty, input is a string

    Valid field_types:
    ? - Yes/No input
    : - Time input
    ! - Multiple inputs delimited by commas returned as a list
    $ - Password input
    """

    # If necessary, add extra prompts that inform the user
    optional_prompt = ""
    type_prompt = ""
    current_prompt = ""

    if optional:
        optional_prompt = "(Optional) "

    if field_type == "?":
        if optional and current is None:
            type_prompt = "(y/N) "
        else:
            type_prompt = "(y/n) "
    elif field_type == ":":
        type_prompt = "(Time input - <value>h<value>m) "
    elif field_type == "!":
        type_prompt = "(Comma delimited) "
    elif field_type == "$":
        type_prompt = "(Hidden) "
    elif field_type != "":
        # If the field type isn't valid, return an empty string
        return ""

    if current is not None:
        time_value = True if field_type == ":" else False
        current_prompt = " [{}]" \
                         .format(value_to_printable(current,
                                                    time_value=time_value,
                                                    short_perms=True))

    # Format the original prompt with prepended additions
    formatted_prompt = "{}{}{}{}: ".format(optional_prompt, type_prompt,
                                           prompt, current_prompt)
    response = ""

    while True:
        if field_type == "$":
            response = getpass(formatted_prompt).decode(sys.stdin.encoding)
        else:
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
            elif field_type == "" or field_type == "$":
                return response

        print "Please submit a valid input"


def get_fields(fields, current_object=None):
    """Prompts for multiple fields and returns everything in a dictionary

    fields - A list of tuples that are ordered (field_name, prompt)

    field_name can contain special characters that signify input type
    ? - Yes/No field
    : - Time field
    ! - List field
    $ - Password field

    In addition to those, field_name can contain a * for an optional field
    """
    responses = dict()

    for field, prompt in fields:
        optional = False
        field_type = ""
        current = None

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
        elif "$" in field:
            field_type = "$"  # Password entry
            field = field.replace("$", "")

        if "*" in field:
            optional = True
            field = field.replace("*", "")

        if current_object and field in current_object:
            current = current_object.get(field)

            if current is None:
                current = "None"

        response = get_field(prompt, optional, field_type, current)

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

    if key == "password":
        print "> password = [PASSWORD HIDDEN]"
    else:
        print u"> {} = {}".format(key, value)

    response = get_field("Add to the config file?",
                         optional=True, field_type="?")

    if response:
        write_config(key, value, path)
        print "New value added!"


def get_user_permissions(users, current_users={}):
    """Asks for permissions for multiple users and returns them in a dict"""

    permissions = {}

    for user in users:
        user_permissions = {}
        current_permissions = {}
        optional = False

        if user in current_users:
            current_permissions = {k: "Y" if v else "N"
                                   for k, v in current_users[user].iteritems()}
            optional = True

        member = get_field(u"Is {} a project member?".format(user),
                           optional=optional, field_type="?",
                           current=current_permissions.get("member"))
        spectator = get_field(u"Is {} a project spectator?".format(user),
                              optional=optional, field_type="?",
                              current=current_permissions.get("spectator"))
        manager = get_field(u"Is {} a project manager?".format(user),
                            optional=optional, field_type="?",
                            current=current_permissions.get("manager"))

        if optional and member == "":
            member = current_users[user]["member"]

        if optional and spectator == "":
            spectator = current_users[user]["spectator"]

        if optional and manager == "":
            manager = current_users[user]["manager"]

        user_permissions["member"] = member
        user_permissions["spectator"] = spectator
        user_permissions["manager"] = manager

        permissions[user] = user_permissions

    return permissions


def fix_user_permissions(permissions):
    """Converts numeric user permissions to a dictionary of permissions"""

    fixed_permissions = dict()

    for user in permissions:
        mode = int(permissions[user])

        user_permissions = dict()
        user_permissions["member"] = (mode & 0b100 != 0)
        user_permissions["spectator"] = (mode & 0b010 != 0)
        user_permissions["manager"] = (mode & 0b001 != 0)

        fixed_permissions[user] = user_permissions

    return fixed_permissions


def fix_args(args, optional_args):
    """Fix the names and values of arguments gotten from docopt"""

    fixed_args = {}

    for arg in args:
        # If args are optional and an arg is empty, don't include it
        if not args[arg] and optional_args:
            continue

        # If it's an argument inside brackets
        if arg[0] == '<':
            fixed_arg = arg[1:-1]
        # If it's an argument in all uppercase
        elif arg.isupper():
            fixed_arg = arg.lower()
        # If it's a long option
        elif arg[0:2] == '--' and arg not in ("--help", "--members",
                                              "--managers", "--spectators"):
            fixed_arg = arg[2:].replace('-', '_')
        # If it's the help option or we don't know
        else:
            print "Invalid arg: {}".format(arg)
            continue

        value = args[arg]

        # If the value is an integer duration value
        if fixed_arg == "duration":
            if value.isdigit():
                fixed_value = int(value)
            else:
                fixed_value = value
        # If the value is a boolean (flag) value
        elif isinstance(value, bool):
            fixed_value = value
        # If the value is a space-delimited list
        elif value and value[0] == "[" and value[-1] == "]":
            fixed_value = value[1:-1].split()
        # If it's a True/False value
        elif value == "True" or value == "False":
            fixed_value = True if value == "True" else False
        else:
            fixed_value = value

        fixed_args[fixed_arg] = fixed_value

    return fixed_args
