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


class UnicodeDictWriter:
    """
    Replacement for csv.DictWriter that adds support for dictionaries that
    have Unicode contents
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

        self.__writerow_int(uni_headers)

    def writerow(self, row):
        row_ordered = OrderedDict()

        for header in self.headers:
            uni_value = self.__convert_csv_writable(row.setdefault(header, ""))

            row_ordered[header] = uni_value

        self.__writerow_int(row_ordered.itervalues())

    ################

    def __writerow_int(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])

        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)

        self.stream.write(data)
        self.queue.truncate(0)

    def __convert_csv_writable(self, value):
        if isinstance(value, list):
            return u"[{}]".format(u",".join(u"'{}'"
                                            .format(self.__convert_csv_writable(v))
                                            for v in value))
        elif isinstance(value, dict):
            return u"{{{}}}" \
                   .format(u",".join(u"'{}': '{}'"
                                     .format(self.__convert_csv_writable(k),
                                             self.__convert_csv_writable(v))
                                     for k, v in value.iteritems()))
        else:
            return u"{}".format(value)


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


def output_csv(response, data_type, path):
    """Outputs a TimeSync response to a CSV file at the specified path, or
    to stdout if path is None"""

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
    """Prints JSON returned by Pymesync nicely to the terminal"""

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
        if optional:
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


def ask_csv():
    """Ask the user if they want to output data into a CSV file, and if so
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
        elif arg[0:2] == '--' and arg != "--help" and arg != "--csv":
            fixed_arg = arg[2:].replace('-', '_')
        # If it's the help option or the csv option or we don't know
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
