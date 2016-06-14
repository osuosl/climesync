import ConfigParser
import os
import re
import stat


def create_config(path="~/.climesyncrc"):
    """Create the configuration file if it doesn't exist"""

    realpath = os.path.expanduser(path)

    # Create the file if it doesn't exist then set its mode to 600 (Owner RW)
    fd = os.open(realpath, os.O_CREAT, stat.S_IRUSR | stat.S_IWUSR)
    os.close(fd)


def read_config(path="~/.climesyncrc"):
    """Read the configuration file and return its contents"""

    realpath = os.path.expanduser(path)

    config = ConfigParser.RawConfigParser()

    # If the file already exists, try to read it
    if os.path.isfile(realpath):
        # Try to read the config file at the given path. If the file isn't
        # formatted correctly, inform the user
        try:
            config.read(realpath)
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
        config.set("climesync", key, value)
    except ConfigParser.NoSectionError:
        config.add_section("climesync")
        config.set("climesync", key, value)

    # Truncate existing file before writing to it
    with open(realpath, "w") as f:
        f.write("# Climesync configuration file\n")

        # Write the config values
        config.write(f)


def print_json(response):
    """Prints values returned by Pymesync nicely"""

    print ""

    if isinstance(response, list):  # List of dictionaries
        for json_dict in response:
            for key, value in json_dict.iteritems():
                print "{}: {}".format(key, value)

            print ""
    elif isinstance(response, dict):  # Plain dictionary
        for key, value in response.iteritems():
            print "{}: {}".format(key, value)

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
        response = raw_input(formatted_prompt)

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

    print "> {} = {}".format(key, value)
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
        elif value and " " in value:
            fixed_value = value.split()
        else:
            fixed_value = value

        fixed_args[fixed_arg] = fixed_value

    return fixed_args
