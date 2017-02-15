.. _usage:

Climesync - TimeSync Front End on the Command Line
==================================================

.. contents::

Climesync is a command line interface to the `Pymesync`_ frontend for the 
`OSU Open Source Lab's`_ `TimeSync API`_.

Climesync currently supports the following versions of the TimeSync API:

* v0

.. _Pymesync: http://pymesync.readthedocs.org/
.. _OSU Open Source Lab's: http://www.osuosl.org/
.. _TimeSync API: http://timesync.readthedocs.org/en/latest/

Install Climesync
-----------------

To install Climesync from PyPI (Recommended), run the following command::

    $ pip install climesync

To install Climesync from git, run the following commands::

    $ git clone https://github.com/osuosl/climesync && cd climesync
    $ python setup.py install

Running Climesync
-----------------

Once the virtualenv has been created and all of the required Python packages
have been installed, you can run climesync with

.. code-block:: none

    $ climesync

Climesync also accepts several optional command line arguments

-c <URL>, --connect <URL>             Connect to a TimeSync server on startup
-u <username>, --user <username>      Attempt to authenticate on startup with the given username
-p <password>, --password <password>  Attempt to authenticate on startup with the given password
-l, --ldap                            Attempt to authenticate using LDAP

Since server information and user credentials can be specified in multiple
places (See `Climesync Configuration`_ below), these values are prioritized
in the following order:

**User input inside program > Command line arguments > Configuration file values**

Interactive Mode
-----------------

Through an interactive shell, users have the following options:

    **c**
        Connect to a TimeSync server

    **dc**
        Disconnect from a TimeSync server

    **s**
        Sign in to the TimeSync server

    **so**
        Sign out from the TimeSync server

Once connected and authenticated, the following options are available:

    **us**
        Update user settings (Password, display name, and email)

    **ct**
        Submit a new time

    **ut**
        Update a previously submitted time with new/revised information

    **st**
        Sum the total time worked on a specific project

    **dt**
        Delete a time

    **gt**
        Query the TimeSync server for submitted times with optional filters

    **gp**
        Query the TimeSync server for projects with optional filters

    **ga**
        Query the TimeSync server for activities with optional filters

    **gu**
        Query the TimeSync server for users with optional filters

Admin-only options:

    **cp**
        Create a new project

    **up**
        Update a project with new/revised information

    **upu**
        Add/update users for a project

    **rpu**
        Remove users from a project

    **dp**
        Delete a project

    **ca**
        Create a new activity

    **ua**
        Update an activity with new/revised information

    **da**
        Delete an activity

    **cu**
        Create a new user

    **uu**
        Update a user with new/revised information

    **du**
        Delete a user

Scripting Mode
--------------

In addition to providing an interactive shell, Climesync also allows commands
to be run from the command line. This is useful when calling Climesync from
shell scripts and makes automating repetitive tasks for admins a breeze!

Scripting mode accepts arguments and options in the usual bash script format
with one addition. To pass a list of values to a command, you format the values
as a space-separated list enclosed within square brackets. For example:

.. code-block:: none

    $ climesync get-times --user="[user1 user2 user3]"

This example gets all the time entries submitted either by user1, user2, or user3.

When running Climesync in scripting mode, authentication can be done by
specifying the username and password as command line arguments or by using
the configuration file (See below)

To get a list of scripting mode commands, run

.. code-block:: none

    $ climesync --help

To get help for a specific scripting mode command, run

.. code-block:: none

    $ climesync <command_name> --help

Climesync Configuration
-----------------------

On the first run of the program in interactive mode, the configuration file
``.climesyncrc`` is created in the user's home directory. This configuration
file stores server information and user credentials. If Climesync is going to
only be run in interactive mode then manually editing this file manually won't
be necessary because Climesync will handle updating these values while it's
being run in interactive mode,

Information on the structure of this file can be obtained `here`_.

The following configuration values are stored under the "climesync" header
in .climesyncrc:

================= =======================================================
    Key                                 Description
================= =======================================================
timesync_url      The URL of the TimeSync server to connect to on startup
username          The username of the user to authenticate as on startup
password          The password of the user to authenticate as on startup
ldap              Use LDAP to authenticate
autoupdate_config Turn off prompts to automatically update your config
================= =======================================================

.. _here: https://docs.python.org/2/library/configparser.html
