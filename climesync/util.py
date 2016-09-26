import ConfigParser
import os
import re
import stat
import codecs
import csv
import cStringIO
import sys  # NOQA flake8 ignore
from collections import OrderedDict
from datetime import datetime
from getpass import getpass


config_file = None


class UnicodeDictWriter:
    """
    Wrapper for csv.DictWriter that adds support for dictionaries with
    Unicode string contents

    Based on a recipe from the Python 2 docs
    """

    def __init__(self, f, headers, dialect=csv.excel, encoding="utf-8",
                 **kwargs):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwargs)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
        self.headers = headers

    def writeheader(self):
        uni_headers = [u"{}".format(h) for h in self.headers]

        self.__writerow(uni_headers)

    def writerow(self, row):
        row_ordered = OrderedDict()

        for header in self.headers:
            uni_value = self.__convert_csv_writable(row.setdefault(header, ""))

            row_ordered[header] = uni_value

        self.__writerow(row_ordered.itervalues())

    ####################

    def __writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])

        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)

        self.stream.write(data)
        self.queue.truncate(0)

    def __convert_csv_writable(self, value):
        if isinstance(value, list):
            return u"[{}]" \
                   .format(u",".join(u"'{}'"
                                     .format(self.__convert_csv_writable(v))
                                     for v in value))
        elif isinstance(value, dict):
            return u"{{{}}}" \
                   .format(u",".join(u"'{}': '{}'"
                                     .format(self.__convert_csv_writable(k),
                                             self.__convert_csv_writable(v))
                                     for k, v in value.iteritems()))
        elif value is None:
            return u""
        else:
            return u"{}".format(value)


def ts_error(*ts_objects):
    for ts_object in ts_objects:
        if not ts_object:
            continue

        if isinstance(ts_object, list):
            ts_object = ts_object[0]

        if "error" in ts_object or "pymesync error" in ts_object:
            print_json(ts_object)
            return True


def create_config(path="~/.climesyncrc"):
    """Create the configuration file if it doesn't exist"""

    global config_file

    if config_file:
        path = config_file

    realpath = os.path.expanduser(path)

    # Create the file if it doesn't exist then set its mode to 600 (Owner RW)
    with codecs.open(realpath, "w", "utf-8-sig") as f:
        f.write(u"# Climesync configuration file")

    os.chmod(realpath, stat.S_IRUSR | stat.S_IWUSR)

    config_file = path


def read_config(path="~/.climesyncrc"):
    """Read the configuration file and return its contents"""

    global config_file

    if config_file:
        path = config_file

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

    config_file = path

    return config


def write_config(key, value, path="~/.climesyncrc"):
    """Write a value to the configuration file"""

    global config_file

    if config_file:
        path = config_file

    realpath = os.path.expanduser(path)

    config = read_config(path)

    # If read_config errored and returned None instead of a ConfigParser
    if not config:
        return

    # If the configuration file doesn't exist (read_config returned an
    # empty config), create it
    if "climesync" not in config.sections():
        create_config(path)

    # Make sure the value is a string so it can be encoded
    value = u"{}".format(value)

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

    config_file = path


def session_exists(path="~/.climesyncsession"):
    """Checks whether or not a clock-in session exists"""

    realpath = os.path.expanduser(path)

    return os.path.exists(realpath)


def read_session(path="~/.climesyncsession"):
    """Reads data from a session file, if it exists"""

    if not session_exists(path):
        return

    realpath = os.path.expanduser(path)

    with codecs.open(realpath, "r", "utf-8") as f:
        lines = f.readlines()

    split_lines = [[s.strip() for s in l.split(":", 1)] for l in lines]
    session = {l[0]: l[1] for l in split_lines}

    return session


def create_session(session, path="~/.climesyncsession"):
    """Creates a session by saving dictionary data to a file"""

    if session_exists(path):
        return

    realpath = os.path.expanduser(path)

    with codecs.open(realpath, "w", "utf-8") as f:
        for key, value in session.iteritems():
            f.write("{}: {}\n".format(key, value))


def clear_session(path="~/.climesyncsession"):
    """Removes a session file, if it exists"""

    if not session_exists(path):
        return

    realpath = os.path.expanduser(path)

    os.remove(realpath)


def construct_clock_out_time(session, now, revisions):
    """Construct a time for clocking out using session data, the current
    datetime, and any revisions the user wished to make"""

    if not session:
        return {"error": "No session data"}

    if not all(k in session for k in ("start_date", "start_time")):
        return {"error": "Invalid session data"}

    datetime_string = "{start_date} {start_time}".format(**session)
    session_start_datetime = datetime.strptime(datetime_string,
                                               "%Y-%m-%d %H:%M")
    delta = now - session_start_datetime

    if now < session_start_datetime:
        return {"error": "Invalid session date/time"}

    time = {k: v for k, v in session.items() if k not in ("start_date", "start_time")}

    time["duration"] = int(delta.total_seconds())
    time["date_worked"] = session_start_datetime.date().isoformat()

    time.update(revisions)

    return time


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


def output_csv(response, data_type, path=None):
    """Outputs a TimeSync response to a CSV file at the specified path, or
    to stdout if no path is supplied"""

    if response and "error" in response[0] or "pymesync error" in response[0]:
        return

    common_headers = ["uuid", "revision", "created_at", "updated_at",
                      "deleted_at", "parents"]

    if data_type == "time":
        headers = ["duration", "user", "project", "activities",
                   "date_worked", "issue_uri", "notes"] + common_headers
    elif data_type == "project":
        headers = ["name", "slugs", "uri", "default_activity",
                   "users"] + common_headers
    elif data_type == "activity":
        headers = ["name", "slug"] + common_headers
    elif data_type == "user":
        headers = ["username", "display_name", "email", "site_spectator",
                   "site_manager", "site_admin", "active", "meta",
                   "created_at", "updated_at", "deleted_at"]
    elif path is not None:
        print "Unknown data type!"
        return
    else:
        return

    if path is not None:
        csvfile = codecs.open(path, "w", "utf-8-sig")
    else:
        csvfile = sys.stdout

    writer = UnicodeDictWriter(csvfile, headers, quoting=csv.QUOTE_ALL)

    writer.writeheader()
    for ts_object in response:
        writer.writerow(ts_object)

    if path is not None:
        csvfile.close()


def is_time(time_str):
    """Checks if the supplied string is formatted as a time value for Pymesync

    A string is formatted correctly if it matches the pattern

        <value>h<value>m

    where the first value is the number of hours and the second is the number
    of minutes.
    """

    return True if re.match(r"\A[\d]+h[\d]+m\Z", time_str) else False


def is_date(date_str):
    """Checks if the supplied string is formatted as an ISO 8601 datestring

    i.e. 2016-04-01, 2015-03-14, etc.
    """

    if not isinstance(date_str, basestring):
        return False

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:  # If strptime fails, a ValueError is raised
        return False

    return True


def check_start_end(start_date_str, end_date_str):
    """Checks if the supplied end datestring is the same as or comes after the
    suplied start datestring
    """

    if not is_date(start_date_str):
        print "{} is not a valid datestring".format(start_date_str)
        return False

    if not is_date(end_date_str):
        print "{} is not a valid datestring".format(end_date_str)
        return False

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    return end_date >= start_date


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
        response = [response] + ["detail"]

    if "detail" not in response:
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
        del response[response.index("detail")]

        # Sort by date worked
        times = sorted(response, cmp=compare_date_worked)

        # Sort again by project slug
        times = sorted(times, key=lambda t: t["project"])

        times_data = []

        for time in times:
            time_data = OrderedDict()
            time_data["user"] = time["user"]
            time_data["project"] = time["project"]
            time_data["activities"] = time["activities"]
            time_data["duration"] = time["duration"]
            time_data["date_worked"] = time["date_worked"]
            time_data["created_at"] = time["created_at"]
            time_data["issue_uri"] = time.setdefault("issue_uri", "")
            time_data["notes"] = time.setdefault("notes", "")
            time_data["uuid"] = time["uuid"]

            times_data.append(time_data)

        print_json(times_data)


def print_pretty_project(response):
    """Prints project data returned by Pymesync nicely"""

    if isinstance(response, dict):
        response = [response]

    # Sort by project name
    projects = sorted(response, key=lambda p: p["name"])

    projects_data = []

    for project in projects:
        project_data = OrderedDict()
        project_data["name"] = project["name"]
        project_data["slugs"] = project["slugs"]
        project_data["users"] = project.setdefault("users", {})

        projects_data.append(project_data)

    print_json(projects_data)


def print_pretty_activity(response):
    """Prints activity data returned by Pymesync nicely"""

    if isinstance(response, dict):
        response = [response]

    # Sort by activity name
    activities = sorted(response, key=lambda a: a["name"])

    activities_data = []

    for activity in activities:
        activity_data = OrderedDict()
        activity_data["name"] = activity["name"]
        activity_data["slug"] = activity["slug"]

        activities_data.append(activity_data)

    print_json(activities_data)


def print_pretty_user(response):
    """Prints user data returned by Pymesync nicely"""

    if isinstance(response, dict):
        response = [response]

    # Sort by username
    users = sorted(response, key=lambda u: u["username"])

    # Sort again by active users
    users = sorted(users, key=lambda u: u["active"], reverse=True)

    users_data = []

    for user in users:
        user_data = OrderedDict()
        user_data["username"] = user["username"]
        user_data["display_name"] = user["display_name"]
        user_data["email"] = user.setdefault("email", "")
        user_data["active"] = user["active"]

        users_data.append(user_data)

    print_json(users_data)


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


def get_field(prompt, optional=False, field_type="", validator=None,
              current=None):
    """Prompts the user for input and returns it in the specified format

    prompt - The prompt to display to the user
    optional - Whether or not the field is optional (defaults to False)
    field_type - The type of input. If left empty, input is a string
    validator - A list of valid inputs (only applicable for text/list fields)
    current - The current value of the field

    Valid field_types:
    ? - Yes/No input
    : - Time input
    ~ - Date input
    ! - Multiple inputs delimited by commas returned as a list
    $ - Password input
    """

    # Check for an empty validator and raise an error
    if validator == []:
        raise IndexError("No valid choices for field '{}'".format(prompt))

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
    elif field_type == '~':
        type_prompt = "(Date input - YYYY-MM-DD) "
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
            elif field_type == "~":
                if is_date(response) and \
                   (not validator or check_start_end(validator, response)):
                    return response
            elif field_type == "!":
                response = [r.strip() for r in response.split(",")]
                for r in response:
                    if validator and r not in validator:
                        print "Invalid response {}".format(r)
                        break
                else:
                    return response
            elif field_type == "$":
                return response
            elif field_type == "":
                if validator and response not in validator:
                    print "Invalid response {}".format(response)
                else:
                    return response

        print "Please submit a valid input"
        if validator:
            if is_date(validator):
                print "The input date must be the same as or later than {}" \
                      .format(validator)
            else:
                print "Valid choices: [{}]".format(", ".join(validator))


def get_fields(fields, current_object=None):
    """Prompts for multiple fields and returns everything in a dictionary

    fields - A list of tuples that are ordered (field_name, prompt,
                                                validator=None)

    field_name can contain special characters that signify input type
    ? - Yes/No field
    : - Time field
    ~ - Date field
    ! - List field
    $ - Password field

    In addition to those, field_name can contain a * for an optional field
    """
    global start_cached

    responses = dict()

    padded_fields = [(f + (None,))[:3] for f in fields]

    # Check to see if any of the validators are empty lists
    for _, prompt, validator in padded_fields:
        if validator == []:
            raise IndexError("No valid choices for field '{}'".format(prompt))

    for field, prompt, validator in padded_fields:
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
        elif "~" in field:
            field_type = "~"  # Date
            field = field.replace("~", "")
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

        if field == "end":
            validator = start_cached

        response = get_field(prompt, optional, field_type, validator, current)

        if field == "start":
            start_cached = response
        elif field == "end":
            start_cached = None

        # Only add response if it isn't empty
        if response != "":
            responses[field] = response

    return responses


def ask_csv():
    """Ask the user if they want to output data to a CSV file, and if so
    ask for the relative path of the file"""

    do_create_csv = get_field("Write data to a CSV file?", field_type="?",
                              optional=True)

    if do_create_csv:
        return get_field("Enter the path to the new CSV file")
    else:
        return None


def add_kv_pair(key, value, path="~/.climesyncrc"):
    """Ask the user if they want to add a key/value pair to the config file"""

    config = read_config(path)

    # Get the current value in the config if there is one
    if config.has_option("climesync", key):
        if isinstance(value, bool):
            current_value = config.getboolean("climesync", key)
        else:
            current_value = config.get("climesync", key)
    else:
        current_value = None

    # If that key/value pair is already in the config, skip asking
    if current_value is not None and value == current_value:
        return

    if key == "password":
        print "> password = [PASSWORD HIDDEN]"
    else:
        print u"> {} = {}".format(key, value)

    response = get_field("Add to the config file ({})?".format(config_file),
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
        elif arg[0:2] == "--" and arg not in ("--help", "--members", "--csv",
                                              "--managers", "--spectators"):
            fixed_arg = arg[2:].replace('-', '_')
        # If it's the help option or we don't know
        else:
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
