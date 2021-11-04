#!/usr/bin/python3
import os
import argparse
import sys
from __init__ import EventQuery, TodoQuery, PasswordQuery


def execute_args(cls, func, filename, log_level, **kwargs):
	query = cls(filename = filename, log_level = log_level)
	kwargs = query.init_args(**kwargs)
	init_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "init.sql")
	query.execute_sqlite_script(init_file) # init.sql is expected
	ret = func(query, **kwargs)
	query.close()
	return ret

#parents argument
def main():
	config_dir = os.path.expanduser("~/.digital_notebook/")
	if not os.path.isdir(config_dir):
		os.mkdir(config_dir)
	parser = argparse.ArgumentParser(description="my epic databse notebook", allow_abbrev=False)
	parser.add_argument("-f", "--file", dest = "filename", help = "db file",
		default= os.path.expanduser("~/.digital_notebook/data.sqlite3"))
	parser.add_argument("-v", "--verbose", dest="log_level", help = "verbose",
		action="count", default=0)
	parser.add_argument("-q", "--quiet", dest="log_level", help = "verbose",
		action="store_const", const = -1)
	subparsers = parser.add_subparsers(required=True)
	EventQuery.create_parser(subparsers.add_parser("event", aliases=["events", "e"]))
	TodoQuery.create_parser(subparsers.add_parser("todo", aliases=["todos", "t"]))
	PasswordQuery.create_parser(subparsers.add_parser("password", aliases=["passwords", "p"]))
	args = parser.parse_args()
	execute_args(**vars(args))
	return 0 # this would return non 0  if Query would have some sort of a flag set



if __name__ == "__main__":
	sys.exit(main())
