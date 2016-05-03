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

To install Climesync, clone the `Github repo`_ and run the following command 
in a `virtualenv`_

.. code-block:: none

    (venv) $ pip install -r requirements.txt

.. _Github repo: https://www.github.com/osuosl/climesync/
.. _virtualenv: http://docs.python-guide.org/en/latest/dev/virtualenvs/

Running Climesync
-----------------

Once the virtualenv has been created and all of the required Python packages
have been installed, you can run climesync with

.. code-block:: none

    (venv) $ ./climesync

Climesync also accepts several optional command line arguments

-c <URL>, --connect <URL>             Connect to a TimeSync server on startup
-u <username>, --user <username>      Attempt to authenticate on startup with the given username
-p <password>, --password <password>  Attempt to authenticate on startup with the given password

Since server information and user credentials can be specified in multiple
places (See `Climesync Configuration`_ below), these values are prioritized
in the following order:

**User input inside program > Command line arguments > Configuration file values**

Climesync Options
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

Climesync Configuration
-----------------------

On the first run of the program, the configuration file .climesyncrc is
created in the user's home directory. This configuration file stores server
information and user credentials. Editing this file manually should not be
necessary because Climesync updates these values as necessary

The following configuration values are stored in .climesyncrc:

============ =======================================================
    Key                            Description
============ =======================================================
TIMESYNC_URL The URL of the TimeSync server to connect to on startup
USERNAME     The username of the user to authenticate as on startup
PASSWORD     The password of the user to authenticate as on startup
============ =======================================================
