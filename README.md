# climesync
CLI for the TimeSync API

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

If all three args are provided, climesync will connect to timesync and
authenticate your username and password for you.
