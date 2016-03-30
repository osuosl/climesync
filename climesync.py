#!/usr/bin/env python

import pymesync
import sys
import argparse
import json
import pprint

pp = pprint.PrettyPrinter(indent=4)

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--connect", help="connect to a timesync baseurl")
parser.add_argument("-u", "--username", help="specify your username")
parser.add_argument("-p", "--password", help="specify your password")

args = parser.parse_args()

baseurl = ""
username = ""
password = ""

if args.connect:
    baseurl = args.connect

ts = pymesync.TimeSync(baseurl)

if args.username:
    username = args.username

if args.password:
    password = args.password
    
if baseurl and username and password:
    pp.pprint(ts.authenticate(username, password, "password"))


menu = (
    "===============================================================\n"
    " pymesync CLI to interact with TimeSync\n"
    "===============================================================\n"
    "\nWhat do you want to do?\n"
    "c - connect\n"
    "s - sign in\n\n"
    "ct - submit time\n"
    "ut - update time\n"
    "gt - get times\n\n"
    "cp - create project\n"
    "up - update project\n"
    "gp - get projects\n\n"
    "ca - create activity\n"
    "ua - update activity\n"
    "ga - get activities\n\n"
    "cu - create user\n"
    "uu - update user\n"
    "gu - get users\n\n"
    "m - print this menu\n"
    "q - exit\n")
print menu

while 1:
    choice = raw_input(">> ")

    if choice == "q":
        sys.exit()

    if choice == "m":
        print menu

    if choice == "c":
        baseurl = raw_input("baseurl: ")
        print getattr(ts, "__init__")(baseurl)

    if choice == "s":
        if not username:
            username = raw_input("username: ")
        if not password:
            password = raw_input("password (plaintext): ")
        auth_type = "password"
        pp.pprint(ts.authenticate(username, password, auth_type))

    if choice == "ct":
        timeobj = {}
        duration = int(raw_input("duration (seconds): "))
        project = raw_input("project slug: ")
        activities = raw_input("activity slugs (comma delimited): ")
        date_worked = raw_input("date worked (yyyy-mm-dd): ")
        issue_uri = raw_input("issue uri (optional): ")
        notes = raw_input("notes (optional): ")
        timeobj = {
            "duration": duration,
            "project": project,
            "user": ts.user,
            "activities": activities.split(","),
            "date_worked": date_worked,
            "issue_uri": issue_uri,
        }
        if notes:
            timeobj["notes"] = notes
        if issue_uri:
            timeobj["issue_uri"] = issue_uri
        pp.pprint(ts.create_time(timeobj))

    if choice == "ut":
        timeobj = {}
        uuid = raw_input("uuid: ")
        print "All following fields are optional"
        duration = int(raw_input("duration (seconds): "))
        project = raw_input("project slug: ")
        user = raw_input("new user: ")
        activities = raw_input("activity slugs (comma delimited): ")
        date_worked = raw_input("date worked (yyyy-mm-dd): ")
        issue_uri = raw_input("issue uri: ")
        notes = raw_input("notes: ")
        if duration:
            timeobj["duration"] = duration
        if project:
            timeobj["project"] = project
        if user:
            timeobj["user"] = user
        if activities:
            timeobj["activities"] = activities
        if date_worked:
            timeobj["date_worked"] = date_worked
        if issue_uri:
            timeobj["issue_uri"] = issue_uri
        if notes:
            timeobj["notes"] = notes
        pp.pprint(ts.update_time(uuid=uuid, time=timeobj))

    if choice == "gt":
        query = dict()
        print "All fields are optional"
        user = raw_input("user: ")
        project = raw_input("project: ")
        activity = raw_input("activity: ")
        start = raw_input("start (yyyy-mm-dd): ")
        end = raw_input("end (yyyy-mm-dd): ")
        include_revisions = raw_input("include revisions (y or n): ")
        include_deleted = raw_input("include deleted (y or no): ")
        uuid = raw_input("uuid: ")
        if user:
            user = user.split(",")
            query["user"] = [u.strip(" ") for u in user]
        if project:
            project = project.split(",")
            query["project"] = [p.strip(" ") for p in project]
        if activity:
            activity = activity.split(",")
            query["activity"] = [a.strip(" ") for a in activity]
        if start:
            query["start"] = start
        if end:
            query["end"] = end
        if include_revisions == "y":
            query["include_revisions"] = True
        if include_revisions == "n":
            query["include_revisions"] = False
        if include_deleted == "y":
            query["include_deleted"] = True
        if include_deleted == "n":
            query["include_deleted"] = False
        if uuid:
            query["uuid"] = uuid
        print
        pp.pprint(ts.get_times(query))

    if choice == "cp":
        project = dict()
        name = raw_input("name: ")
        slugs = raw_input("slugs (comma delimited): ").split(",")
        uri = raw_input("uri (optional): ")
        print "this cli does not yet support project creation with users"
        default_activity = raw_input("default activity (optional): ")
        if uri:
            project["uri"] = uri
        if default_activity:
            project["default_activity"] = default_activity
        ts.create_project(project)

    if choice == "up":
        print "not implemented"
        project = dict()
        slug = raw_input("project slug: ")
        print "All following fields are optional"
        name = raw_input("name: ")
        slugs = raw_input("slugs (comma delimited): ")
        uri = raw_input("uri: ")
        default_activity = raw_input("default activity: ")
        print "this cli does not yet support project updates with users"
        project["slug"] = slug
        if name:
            project["name"] = name
        if slugs:
            project["slugs"] = slugs.split(",")
        if uri:
            project["uri"] = uri
        if default_activity:
            project["default_activity"] = default_activity
        ts.update_project(project)

    if choice == "gp":
        query = dict()
        print "All fields are optional"
        include_revisions = raw_input("include revisions (y or n): ")
        include_deleted = raw_input("include deleted (y or no): ")
        slug = raw_input("slug: ")
        if include_revisions == "y":
            query["include_revisions"] = True
        if include_revisions == "n":
            query["include_revisions"] = False
        if include_deleted == "y":
            query["include_deleted"] = True
        if include_deleted == "n":
            query["include_deleted"] = False
        if slug:
            query["slug"] = slug
        pp.pprint(ts.get_projects(query))

    if choice == "ca":
        activity = dict()
        name = raw_input("name:" )
        slug = raw_input("slug: ")
        if name and slug:
            activity["name"] = name
            activity["slug"] = slug
            pp.pprint(ts.create_activity(activity))
        else:
            print "Provide both name and slug"

    if choice == "ua":
        print "not implemented"
        slug_to_update = raw_input("slug of activity to update: ")
        print "All following fields are optional"
        activity = dict()
        name = raw_input("name: ")
        slug = raw_input("slug: ")
        if name:
            activity["name"] = name
        if slug:
            activity["slug"] = slug
        if slug_to_update:
            pp.pprint(ts.update_activity(activity=activity,
                                         slug=slug_to_update))
        else:
            print "Provide a slug of activity to update"

    if choice == "ga":
        query = dict()
        print "All fields are optional"
        include_revisions = raw_input("include revisions (y or n): ")
        include_deleted = raw_input("include deleted (y or no): ")
        slug = raw_input("slug: ")
        if include_revisions == "y":
            query["include_revisions"] = True
        if include_revisions == "n":
            query["include_revisions"] = False
        if include_deleted == "y":
            query["include_deleted"] = True
        if include_deleted == "n":
            query["include_deleted"] = False
        if slug:
            query["slug"] = slug
        pp.pprint(ts.get_activities(query))

    if choice == "cu":
        print "not implemented"

    if choice == "uu":
        print "not implemented"

    if choice == "gu":
        query = dict()
        username = raw_input("username (optional): ")
        if username:
            query["username"] = username
        pp.pprint(ts.get_users(username=username))
