# climesync

[![Build Status](https://travis-ci.org/osuosl/climesync.svg?branch=master)](https://travis-ci.org/osuosl/climesync)

CLI for the TimeSync API

Climesync is a CLI frontend to submit times to a TimeSync implementation.

Install and Run
---------------

To install from git, run the following commands

```
$ git clone https://github.com/osuosl/climesync && cd climesync
$ python setup.py install
```

Then, to run the program, type

```
$ climesync
```

climesync accepts args like so:

```
$ climesync --connect <timesync baseurl> --user <username> --password <password>
```

or with short options:

```
$ climesync -c <timesync baseurl> -u <username> -p <password>
```

If all three args are provided, climesync will connect to timesync and
authenticate your username and password for you.
    

Once climesync is running, you can complete the following tasks:

```
c - connect
dc - disconnect
s - sign in
so - sign out/reset credentials

ct - submit time
ut - update time
gt - get times
st - sum times
dt - delete time

cp - create project
up - update project
gp - get projects
dp - delete project

ca - create activity
ua - update activity
ga - get activities
da - delete activity

cu - create user
uu - update user
gu - get users
du - delete user

q - exit
```

Developing for Climesync
------------------------

To set up a development environment, you must install `virtualenvwrapper` from PyPI and create
a new virtualenv.

```
$ pip install virtualenvwrapper
$ mkvirtualenv venv
...
(venv) $ ...
```

After creating the virtualenv, several dependencies must be installed

```
(venv) $ pip install -r requirements.txt
```

Documentation
-------------

To build Climesync documentation, run the following commands:

```
(venv) $ cd docs
(venv) $ make html
```

To view the documentation after it has been built, run this command in a virtualenv:

```
(venv) $ <browser> build/html/index.html
```

Testing
-------

To lint Climesync for PEP8 compliance, run this command in a virtualenv:

```
(venv) $ flake8 climesync.py testing
```

To run Climesync's unit test suite, run this command in a virtualenv:

```
(venv) $ nosetests
```
