from climesync import commands


class TestData():

    def __init__(self, command=None, mocked_input=None, cli_args=None,
                 expected_response=None, admin=None):
        self.command = command
        self.mocked_input = mocked_input
        self.cli_args = cli_args
        self.expected_response = expected_response
        self.admin = admin


create_time_data = TestData(
        command=commands.create_time,
        mocked_input=[
            "1h0m",  # Duration
            "2016-05-04",  # Date worked
            "p_foo",  # Project slug
            ["planning", "code"],  # Activity slugs
            "https://www.github.com/osuosl/projectfoo/issues/42",  # Issue URI
            "Worked on coding"  # Notes
        ],
        cli_args="1h0m p_foo planning code --date-worked=2016-05-04 \
             --issue-uri=https://www.github.com/osuosl/projectfoo/issues/42 \
             --notes=\"Worked on coding\"",
        expected_response={
            "created_at": "2015-05-23",
            "updated_at": None,
            "deleted_at": None,
            "uuid": "838853e3-3635-4076-a26f-7efr4e60981f",
            "revision": 1,
            "duration": 3600,
            "project": "p_foo",
            "activities": ["planning", "code"],
            "date_worked": "2016-05-04",
            "user": "test",
            "notes": "Worked on coding",
            "issue_uri": "https://www.github.com/osuosl/projectfoo/issues/42"
        },
        admin=False)

update_time_data = TestData(
        command=commands.update_time,
        mocked_input=[
            "838853e3-3635-4076-a26f-7efr4e60981f",  # UUID of time to update
            "2h0m",  # Updated duration
            "p_bar",  # Updated project slug
            "usertwo",  # Updated user
            ["docs"],  # Updated activity slugs
            "2016-06-20",  # Updated date worked
            "https://www.github.com/osuosl/projectbar/issues/5",  # Updated URI
            "Worked on documentation"  # Updated notes
        ],
        cli_args="838853e3-3635-4076-a26f-7efr4e60981f --duration=2h0m \
             --project=p_bar --user=usertwo --activities=docs \
             --date-worked=2016-06-20 \
             --issue-uri=https://www.github.com/osuosl/projectbar/issues/5 \
             --notes=\"Worked on documentation\"",
        expected_response={
            "created_at": "2014-06-12",
            "updated_at": "2015-10-18",
            "deleted_at": None,
            "uuid": "838853e3-3635-4076-a26f-7efr4e60981f",
            "revision": 2,
            "duration": 7200,
            "project": "p_bar",
            "activities": ["docs"],
            "date_worked": "2016-06-20",
            "user": "usertwo",
            "notes": "Worked on documentation",
            "issue_uri": "https://www.github.com/osuosl/projectbar/issues/5"
        },
        admin=False)

get_times_no_uuid_data = TestData(
        command=commands.get_times,
        mocked_input=[None]*8,
        cli_args="",
        expected_response=[{
                "created_at": "2014-04-17",
                "updated_at": None,
                "deleted_at": None,
                "uuid": "c3706e79-1c9a-4765-8d7f-89b4544cad56",
                "revision": 1,
                "duration": 12,
                "project": ["ganeti-webmgr", "gwm"],
                "activities": ["docs", "planning"],
                "date_worked": "2014-04-17",
                "user": "userone",
                "notes": "Worked on documentation.",
                "issue_uri": "https://github.com/osuosl/ganeti_webmgr"
            },
            {
                "created_at": "2014-04-17",
                "updated_at": None,
                "deleted_at": None,
                "uuid": "12345676-1c9a-rrrr-bbbb-89b4544cad56",
                "revision": 1,
                "duration": 13,
                "project": ["ganeti-webmgr", "gwm"],
                "activities": ["code", "planning"],
                "date_worked": "2014-04-17",
                "user": "usertwo",
                "notes": "Worked on coding",
                "issue_uri": "https://github.com/osuosl/ganeti_webmgr"
            },
            {
                "created_at": "2014-04-17",
                "updated_at": None,
                "deleted_at": None,
                "uuid": "12345676-1c9a-ssss-cccc-89b4544cad56",
                "revision": 1,
                "duration": 14,
                "project": ["timesync", "ts"],
                "activities": ["code"],
                "date_worked": "2014-04-17",
                "user": "userthree",
                "notes": "Worked on coding",
                "issue_uri": "https://github.com/osuosl/timesync"
        }],
        admin=False)

get_times_uuid_data = TestData(
        command=commands.get_times,
        mocked_input=[
            "userone",  # User
            ["gwm"],  # Project slugs
            ["docs"],  # Activity slugs
            "2014-04-16",  # Start date
            "2014-04-18",  # End date
            False,  # Include revisions
            False,  # Include deleted
            "838853e3-3635-4076-a26f-7efr4e60981f"  # UUID
        ],
        cli_args="--user=userone --project=gwm --activity=docs \
                  --start=2014-04-16 --end=2014-05-18 \
                  --include-revisions=False --include-deleted=False \
                  --uuid=838853e3-3635-4076-a26f-7efr4e60981f",
        expected_response=[{
            "created_at": "2014-04-17",
            "updated_at": None,
            "deleted_at": None,
            "uuid": "838853e3-3635-4076-a26f-7efr4e60981f",
            "revision": 1,
            "duration": 12,
            "project": ["ganeti-webmgr", "gwm"],
            "activities": ["docs", "planning"],
            "date_worked": "2014-04-17",
            "user": "userone",
            "notes": "Worked on documentation.",
            "issue_uri": "https://github.com/osuosl/ganeti_webmgr"
        }],
        admin=False)

sum_times_data = TestData(
        command=commands.sum_times,
        mocked_input=[
            ["gwm"],  # Project slugs
            "",  # Include revisions
            ""  # Include deleted
        ],
        cli_args="gwm",
        expected_response=[],
        admin=False)

delete_time_no_data = TestData(
        command=commands.delete_time,
        mocked_input=[
            "838853e3-3635-4076-a26f-7efr4e60981f",  # UUID
            False  # Really?
        ],
        expected_response=[],
        admin=False)

delete_time_data = TestData(
        command=commands.delete_time,
        mocked_input=[
            "838853e3-3635-4076-a26f-7efr4e60981f",  # UUID
            True  # Really?
        ],
        cli_args="838853e3-3635-4076-a26f-7efr4e60981f",
        expected_response=[{
            "status": 200
        }],
        admin=False)

create_project_data = TestData(
        command=commands.create_project,
        mocked_input=[
            "projectx",  # Project name
            ["projx", "px"],  # Project slugs
            "https://www.github.com/osuosl/projectx",  # Project URI
            "code",  # Default activity
            ["userone", "usertwo"],  # Project users
        ],
        cli_args="projectx \"[projx px]\" userone 4 usertwo 7 \
                  --uri=https://www.github.com/osuosl/projectx \
                  --default-activity=code",
        expected_response={
            "created_at": "2015-05-23",
            "updated_at": None,
            "deleted_at": None,
            "revision": 1,
            "uuid": "309eae69-21dc-4538-9fdc-e6892a9c4dd4",
            "name": "projectx",
            "slugs": ["projx", "px"],
            "uri": "https://www.github.com/osuosl/projectx",
            "users": {
                "userone": {
                    "member": True,
                    "spectator": False,
                    "manager": False
                },
                "usertwo": {
                    "member": True,
                    "spectator": True,
                    "manager": True
                }
            },
            "default_activity": "code"
        },
        admin=True)

update_project_data = TestData(
        command=commands.update_project,
        mocked_input=[
            "projx",  # Slug of project to update
            "Project X",  # Updated name
            ["px"],  # Updated slugs
            "https://www.github.com/osuosl/projectx",  # Updated URI
            "planning"  # Updated default activity
        ],
        cli_args="projx --name=\"Project X\" \
                  --slugs=px --uri=https://www.github.com/osuosl/projectx \
                  --default-activity=planning",
        expected_response={
            "created_at": "2014-04-16",
            "updated_at": "2014-04-18",
            "deleted_at": None,
            "revision": 2,
            "uuid": "309eae69-21dc-4538-9fdc-e6892a9c4dd4",
            "name": "Project X",
            "slugs": ["px"],
            "uri": "https://www.github.com/osuosl/projectx",
            "users": {
                "patcht": {
                    "member": True,
                    "spectator": False,
                    "manager": False
                },
                "tschuy": {
                    "member": True,
                    "spectator": True,
                    "manager": True
                }
            },
        },
        admin=True)

get_projects_no_slug_data = TestData(
        command=commands.get_projects,
        mocked_input=[
            False,  # Include revisions
            False,  # Include deleted
            ""  # Project slug
        ],
        cli_args="",
        expected_response=[{
                "time_total": "0h0m",
                "first_time": "2014-04-17",
                "num_times": 3,
                "latest_time": "2014-04-17",
                "created_at": "2014-07-17",
                "updated_at": "2014-07-20",
                "deleted_at": None,
                "revision": 4,
                "uuid": "a034806c-00db-4fe1-8de8-514575f31bfb",
                "name": "Ganeti Web Manager",
                "slugs": ["gwm"],
                "uri": "https://code.osuosl.org/projects/ganeti-webmgr",
                "users": {
                    "patcht": {
                        "member": True,
                        "spectator": False,
                        "manager": False
                    },
                    "tschuy": {
                        "member": True,
                        "spectator": True,
                        "manager": True
                    }
                }
            },
            {
                "time_total": "0h0m",
                "first_time": "2014-04-17",
                "num_times": 3,
                "latest_time": "2014-04-17",
                "created_at": "2014-07-17",
                "updated_at": "2014-07-20",
                "deleted_at": None,
                "revision": 2,
                "uuid": "a034806c-rrrr-bbbb-8de8-514575f31bfb",
                "name": "TimeSync",
                "slugs": ["timesync", "ts"],
                "uri": "https://code.osuosl.org/projects/timesync",
                "users": {
                    "patcht": {
                        "member": True,
                        "spectator": False,
                        "manager": False
                    },
                    "mrsj": {
                        "member": True,
                        "spectator": True,
                        "manager": False
                    },
                    "tschuy": {
                        "member": True,
                        "spectator": True,
                        "manager": True
                    }
                }
            },
            {
                "time_total": "0h0m",
                "first_time": "2014-04-17",
                "num_times": 3,
                "latest_time": "2014-04-17",
                "created_at": "2014-07-17",
                "updated_at": "2014-07-20",
                "deleted_at": None,
                "revision": 1,
                "uuid": "a034806c-ssss-cccc-8de8-514575f31bfb",
                "name": "pymesync",
                "slugs": ["pymesync", "ps"],
                "uri": "https://code.osuosl.org/projects/pymesync",
                "users": {
                    "patcht": {
                        "member": True,
                        "spectator": False,
                        "manager": False
                    },
                    "tschuy": {
                        "member": True,
                        "spectator": True,
                        "manager": False
                    },
                    "mrsj": {
                        "member": True,
                        "spectator": True,
                        "manager": True
                    },
                    "MaraJade": {
                        "member": True,
                        "spectator": False,
                        "manager": False
                    },
                    "thai": {
                        "member": True,
                        "spectator": False,
                        "manager": False
                    }
                }
        }],
        admin=False)

get_projects_slug_data = TestData(
        command=commands.get_projects,
        mocked_input=[
            "",  # Include revisions
            "",  # Include deleted
            "gwm"  # Project slug
        ],
        cli_args="--slug=gwm --include-revisions=False",
        expected_response=[{
            "time_total": "0h0m",
            "first_time": "2014-04-17",
            "num_times": 3,
            "latest_time": "2014-04-17",
            "created_at": "2014-07-17",
            "updated_at": "2014-07-20",
            "deleted_at": None,
            "revision": 4,
            "uuid": "a034806c-00db-4fe1-8de8-514575f31bfb",
            "name": "Ganeti Web Manager",
            "slugs": ["gwm"],
            "uri": "https://code.osuosl.org/projects/ganeti-webmgr",
            "users": {
                "patcht": {
                    "member": True,
                    "spectator": False,
                    "manager": False
                },
                "tschuy": {
                    "member": True,
                    "spectator": True,
                    "manager": True
                }
            }
        }],
        admin=False)

delete_project_no_data = TestData(
        command=commands.delete_project,
        mocked_input=[
            "slug",  # Project slug
            False  # Really?
        ],
        expected_response=[],
        admin=True)

delete_project_data = TestData(
        command=commands.delete_project,
        mocked_input=[
            "slug",  # Project slug
            True  # Really?
        ],
        cli_args="slug",
        expected_response=[{
            "status": 200
        }],
        admin=True)

create_activity_data = TestData(
        command=commands.create_activity,
        mocked_input=[
            "Coding",  # Activity name
            "code"  # Activity slug
        ],
        cli_args="Coding code",
        expected_response={
            "created_at": "2013-07-27",
            "updated_at": None,
            "deleted_at": None,
            "revision": 1,
            "uuid": "cfa07a4f-d446-4078-8d73-2f77560c35c0",
            "name": "Coding",
            "slug": "code"
        },
        admin=True)

update_activity_data = TestData(
        command=commands.update_activity,
        mocked_input=[
            "slug",  # Slug of activity to update
            "Write Documentation",  # Activity name
            "docs"  # Activity slug
        ],
        cli_args="slug --name=\"Write Documentation\" --slug=docs",
        expected_response={
            "created_at": "2014-04-16",
            "updated_at": "2014-04-17",
            "deleted_at": None,
            "revision": 2,
            "uuid": "3cf78d25-411c-4d1f-80c8-a09e5e12cae3",
            "name": "Write Documentation",
            "slug": "docs"
        },
        admin=True)

get_activities_no_slug_data = TestData(
        command=commands.get_activities,
        mocked_input=[
            "",  # Include revisions
            "",  # Include deleted
            "",  # Activity slug
        ],
        cli_args="",
        expected_response=[{
                "created_at": "2014-04-17",
                "updated_at": None,
                "deleted_at": None,
                "revision": 5,
                "uuid": "adf036f5-3d49-4a84-bef9-062b46380bbf",
                "name": "Documentation",
                "slug": "docs"
            },
            {
                "created_at": "2014-04-17",
                "updated_at": None,
                "deleted_at": None,
                "revision": 1,
                "uuid": "adf036f5-3d49-bbbb-rrrr-062b46380bbf",
                "name": "Coding",
                "slug": "dev"
            },
            {
                "created_at": "2014-04-17",
                "updated_at": None,
                "deleted_at": None,
                "revision": 1,
                "uuid": "adf036f5-3d49-cccc-ssss-062b46380bbf",
                "name": "Planning",
                "slug": "plan"
        }],
        admin=False)

get_activities_slug_data = TestData(
        command=commands.get_activities,
        mocked_input=[
            "",  # Include revisions
            "",  # Include deleted
            "docs",  # Activity slug
        ],
        cli_args="--slug=docs --include-revisions=False",
        expected_response=[{
            "created_at": "2014-04-17",
            "updated_at": None,
            "deleted_at": None,
            "revision": 5,
            "uuid": "adf036f5-3d49-4a84-bef9-062b46380bbf",
            "name": "Documentation",
            "slug": "docs"
        }],
        admin=False)

delete_activity_no_data = TestData(
        command=commands.delete_activity,
        mocked_input=[
            "slug",  # Activity slug
            False  # Really?
        ],
        expected_response=[],
        admin=True)

delete_activity_data = TestData(
        command=commands.delete_activity,
        mocked_input=[
            "slug",  # Activity slug
            True  # Really?
        ],
        cli_args="slug",
        expected_response=[{
            "status": 200
        }],
        admin=True)

create_user_data = TestData(
        command=commands.create_user,
        mocked_input=[
            "newuser",  # Username
            "password",  # Password
            "John Doe",  # Display name
            "newuser@osuosl.org",  # Email
            False,  # Site admin?
            False,  # Site manager?
            False,  # Site spectator?
            "A new user",  # Metainfo
            True  # Active?
        ],
        cli_args="newuser password --display-name=\"John Doe\" \
                  --email=newuser@osuosl.org --meta=\"A new user\"",
        expected_response={
            "created_at": "2015-05-23",
            "deleted_at": None,
            "username": "newuser",
            "display_name": "John Doe",
            "email": "newuser@osuosl.org",
            "site_admin": False,
            "site_manager": False,
            "site_spectator": False,
            "meta": "A new user",
            "active": True
        },
        admin=True)

update_user_data = TestData(
        command=commands.update_user,
        mocked_input=[
            "olduser",  # Username of user to update
            "newuser",  # Updated username
            "pa$$word",  # Updated password
            "A. User",  # Updated display name
            "auser@osuosl.org",  # Updated email
            True,  # Site admin?
            False,  # Site manager?
            False,  # Site spectator?
            "Admin user",  # Metainfo
            True,  # Active?
        ],
        cli_args="olduser --username=newuser --password=pa$$word \
                  --display-name=\"A. User\" --email=auser@osuosl.org \
                  --site-admin=True --site-manager=False \
                  --site-spectator=False --meta=\"Admin user\" --active=True ",
        expected_response={
            "created_at": "2015-02-29",
            "deleted_at": None,
            "username": "newuser",
            "display_name": "A. User",
            "email": "auser@osuosl.org",
            "site_admin": True,
            "site_manager": False,
            "site_spectator": False,
            "active": True
        },
        admin=True)

get_users_no_slug_data = TestData(
        command=commands.get_users,
        mocked_input=[
            "",  # Username
            "",  # Metadata
            ""   # Project
        ],
        cli_args="",
        expected_response=[{
                "username": "userone",
                "display_name": "One Is The Loneliest Number",
                "email": "exampleone@example.com",
                "active": True,
                "site_admin": False,
                "site_manager": False,
                "site_spectator": False,
                "created_at": "2015-02-29",
                "deleted_at": None
            },
            {
                "username": "usertwo",
                "display_name": "Two Can Be As Bad As One",
                "email": "exampletwo@example.com",
                "active": True,
                "site_admin": False,
                "site_manager": False,
                "site_spectator": False,
                "created_at": "2015-02-29",
                "deleted_at": None
            },
            {
                "username": "userthree",
                "display_name": "Yes It's The Saddest Experience",
                "email": "examplethree@example.com",
                "active": True,
                "site_admin": False,
                "site_manager": False,
                "site_spectator": False,
                "created_at": "2015-02-29",
                "deleted_at": None
            },
            {
                "username": "userfour",
                "display_name": "You'll Ever Do",
                "email": "examplefour@example.com",
                "active": True,
                "site_admin": False,
                "site_manager": False,
                "site_spectator": False,
                "created_at": "2015-02-29",
                "deleted_at": None
        }],
        admin=True)

get_users_slug_data = TestData(
        command=commands.get_users,
        mocked_input=[
            "userone"  # Username
        ],
        cli_args="--username=userone",
        expected_response=[{
            "username": "userone",
            "display_name": "X. Ample User",
            "email": "example@example.com",
            "active": True,
            "site_admin": False,
            "site_spectator": False,
            "site_manager": False,
            "projects": {},
            "created_at": "2015-02-29",
            "deleted_at": None
        }],
        admin=False)

delete_user_no_data = TestData(
        command=commands.delete_user,
        mocked_input=[
            "user",  # Username
            False  # Really?
        ],
        expected_response=[],
        admin=True)

delete_user_data = TestData(
        command=commands.delete_user,
        mocked_input=[
            "user",  # Username
            True  # Really?
        ],
        cli_args="user",
        expected_response=[{
            "status": 200
        }],
        admin=True)
