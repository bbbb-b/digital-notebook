import sqlite3
import sys
import argparse

class QueryException(Exception):
	pass


class Query:
# OVERWRITTEN CONSTANTS

	table_name = ""
	keys = ()

	log_level = -2
	order_by = None
# MAIN FUNCTIONS

	def __init__(self, filename, log_level):
		self.log_level = log_level
		self.log_debug(f"Connecting to file: {filename}")
		self.con = sqlite3.connect(filename)
		self.cur = self.con.cursor()

	def init_args(self, order_by, **kwargs): # called right after init
		self.order_by = order_by
		return kwargs

	def close(self):
		self.log_debug("Closing db")
		self.con.commit()
		self.con.close()

# HELPER METHODS

	def make_data(self, e):
		d = self.get_data_t()(*e)
		d.init(self)
		return d

	def log_debug(self, s):
		if self.log_level < 1:
			return
		print(s, file = sys.stderr)

	def log(self, s): # always, unless quiet, why would it be quiet tho (...todo)
		if self.log_level < 0: # --quiet specificed
			return
		print(s, file=sys.stderr)

	def execute_sqlite_script(self, filename):
		self.log_debug(f"Executing script: {filename}\n") 
		with open(filename, "r") as f:
			script = f.read()
			self.cur.executescript(script)
		self.con.commit()

	def execute_sqlite_query(self, query, args):
		self.log_debug(f"Executing query:\n{query}\nwith args: {repr(tuple(args))}\n")
		args = tuple(map(str, args))
		self.cur.execute(query, args)
		return self.cur.fetchall()

	@staticmethod
	def validate(val, s):
		if not val:
			raise QueryException(s)

	def stringify_keys(self, keys = None):
		if keys is None:
			keys = self.keys
		return ', '.join(keys)

	def get_data_by_id(self, id):
		res = self.execute_sqlite_query(
			f"SELECT {self.stringify_keys()} from {self.table_name} WHERE id=?", (id,))
		if len(res) == 0:
			return None
		return self.make_data(res[0])

	def validate_id_exists(self, id):
		data = self.get_data_by_id(id)
		self.validate(data is not None, f"id {id} doesn't exist")
		return data

	def query_data(self, where_stmts = None, args = None, limit = None):
		if where_stmts is None:
			where_stmts = []
		if args is None:
			args = []
		limit_stmt = "" if limit is None else f"LIMIT {limit}\n"
		where_stmt = "" if len(where_stmts) == 0 else \
			f"WHERE {' AND '.join(map(lambda x : f'({x})', where_stmts))}\n"
		q = f"SELECT {self.stringify_keys()}\n" \
			f"FROM {self.table_name}\n" \
			f"{where_stmt}{limit_stmt}"
		raw_data = self.execute_sqlite_query(q, args)
		data = [*map(self.make_data, raw_data)]
		data.sort(**self.get_sort_args())
		return data

	def get_sort_args(self):
		return {
			"key" : self.sort_key if self.order_by is None else lambda x : getattr(x, self.order_by),
			"reverse": self.order_by is None,
		}

	@classmethod
	def add_argument_group(cls, parser, first_name, *names, required, **kwargs):
		assert first_name[:2] == "--"
		group = parser.add_mutually_exclusive_group(required = required)
		group.add_argument(first_name, *names, **kwargs)
		group.add_argument(first_name[2:], nargs="?")

# OVERWRITTEN METHODS

	@staticmethod
	def get_data_t():
		raise QueryException("get_data_t() not implemented")

	@classmethod
	def add_key_arguments(cls, parser, op):
		raise QueryException("add_key_arguments() not implemented")

	@classmethod
	def sort_key(cls, data):
		return -data.id

	@classmethod
	def create_get_parser(cls, parser):
		parser.set_defaults(func = cls.do_query_get)
		parser.add_argument("--limit", type = int, default = 9999)
		cls.add_key_arguments(parser, "get")

	@classmethod
	def create_add_parser(cls, parser):
		parser.set_defaults(func = cls.do_query_add)
		cls.add_key_arguments(parser, "add")

	@classmethod
	def create_update_parser(cls, parser):
		parser.set_defaults(func = cls.do_query_update)
		parser.add_argument(f"id", type=int)
		cls.add_key_arguments(parser, "update")

	@classmethod
	def create_delete_parser(cls, parser):
		parser.set_defaults(func = cls.do_query_delete)
		parser.add_argument("ids", type=int, nargs="+", default=[])
		cls.add_key_arguments(parser, "delete")

	#returns queried data
	def do_query_get(self, where_stmts = None, args = None, limit = 9999, **kwargs):
		if where_stmts is None:
			where_stmts = []
		if args is None:
			args = []
		for key in kwargs:
			val = kwargs[key]
			if isinstance(val, bool):
				val = int(val)
			if isinstance(val, str):
				where_stmts.append(f"{key} LIKE ?")
				args.append(f"%{val}%")
			elif isinstance(val, int):
				where_stmts.append(f"{key} = ?")
				args.append(val)
			else:
				self.validate(False, f"Invalid key {key} with value {val}")
		res = self.query_data(where_stmts = where_stmts, args = args, limit = limit)
		self.log(f"Total found: {len(res)}\n")
		for it in res:
			it.pretty_print()
		return res

	#returns new data
	def do_query_add(self, **kwargs):
		self.validate(len(kwargs) != 0, "Nothing to add") # this should never happen
		q = f"INSERT INTO {self.table_name}\n" \
			f"({self.stringify_keys(kwargs.keys())})\n" \
			f"VALUES ({', '.join('?' * len(kwargs))})\n"
		self.execute_sqlite_query(q, tuple(kwargs.values()))
		self.log(f"New id: {self.cur.lastrowid}")
		data = self.get_data_by_id(self.cur.lastrowid)
		data.pretty_print()
		return data

	#returns new data
	def do_query_update(self, id, **kwargs):
		self.validate(len(kwargs) != 0, "Nothing to add") # this should never happen
		data = self.validate_id_exists(id)
		for key in kwargs:
			if kwargs[key] == getattr(data, key):
				self.log(f"{key} unchanged: ({kwargs[key]})")
			else:
				self.log(f"{key}: {getattr(data, key)} -> {kwargs[key]}")
		self.log("")
		set_statement = ", ".join(map(lambda k : f"{k} = ?", kwargs.keys()))
		q = f"UPDATE {self.table_name}\n" \
			f"SET {set_statement}\n" \
			f"WHERE id=?\n"
		self.execute_sqlite_query(q, tuple(kwargs.values()) + (id,))
		new_data = self.get_data_by_id(id)
		new_data.pretty_print()
		return new_data

	# returns deleted data
	def do_query_delete(self, ids):
		all_data = [*map(self.validate_id_exists, ids)]
		for data in all_data:
			self.log(f"Deleting data:")
			self.log(data.pretty_str())
		q = f"DELETE FROM {self.table_name}\n" \
			f"WHERE ID in ({', '.join('?' * len(ids))})\n"
		self.execute_sqlite_query(q, ids)
		return all_data

	@classmethod
	def create_parser(cls, parser):
		parser.set_defaults(cls = cls)
		parser.add_argument("--order-by", default = None, choices = cls.keys)
		subparsers = parser.add_subparsers(required = True)
		cls.create_get_parser(subparsers.add_parser("get", aliases=["list", "search", "g"],
			argument_default = argparse.SUPPRESS))
		cls.create_add_parser(subparsers.add_parser("add", aliases=["a"],
			argument_default = argparse.SUPPRESS))
		cls.create_update_parser(subparsers.add_parser("update", aliases=["set", "s"],
			argument_default = argparse.SUPPRESS))
		cls.create_delete_parser(subparsers.add_parser("delete", aliases=["remove", "d"],
			argument_default = argparse.SUPPRESS))

#class Data:
