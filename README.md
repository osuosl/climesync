# climesync
CLI for the TimeSync API

This is not an official TimeSync client, and is not officially supported by the
OSL. This CLI is used internally by the OSL for time-tracking purposes during
development of other tools.

Install and Run
---------------

To install clone this repo then run the following commands:

```
$ virtualenv venv
(venv) $ pip install -r requirements.txt
(venv) $ ./climesync.py
```

climesync accepts args like so:

```
(venv) $ ./climesync.py --connect <timesync baseurl> --user <username> --password <password>
```

or with short options:

```
(venv) $ ./climesync.py -c <timesync baseurl> -u <username> -p <password>
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
