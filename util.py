import ConfigParser
import os
import re
import stat
import sys
import codecs


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

    if field_type == ":":
        type_prompt = "(Time input - <value>h<value>m) "

    if field_type == "!":
        type_prompt = "(Comma delimited) "

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


def get_fields(fields, current_object=None):
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
        elif arg[0:2] == '--' and arg != "--help":
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
