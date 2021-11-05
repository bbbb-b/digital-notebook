import string
import random
from recordclass import recordclass
import pyperclip
from query import Query
from colors import Colors

class PasswordQuery(Query):
	table_name = "passwords"
	keys = ("id", "url", "username", "password", "notes")
	order_by = "url"

	valid_chars = string.ascii_letters + string.digits # + "!" ???
	password_length = 42
	copy_password = True
	print_password = False

	def generate_password(self):
		return "".join([random.choice(self.valid_chars) for _ in range(self.password_length)])

	@staticmethod
	def get_data_t():
		return PasswordData

	@staticmethod
	def sort_key(event):
		return event.url

	def init_args(self, copy_password, print_password, password_length, **kwargs):
		self.print_password = print_password
		self.copy_password = copy_password
		if password_length is not None:
			self.password_length = password_length
		return super().init_args(**kwargs)

	@classmethod
	def add_key_arguments(cls, parser, op):
		if op == "delete":
			return
		if op == "get":
			parser.add_argument("--id", type = int)
		cls.add_argument_group(parser, "--url", "--domain", required = op == "add")
		cls.add_argument_group(parser, "--username", "--name", required = op == "add")
		parser.add_argument("--notes", "--note", "--desc")
		password_group = parser.add_mutually_exclusive_group()
		password_group.add_argument("--password", "--pass")
		if op == "update":
			password_group.add_argument("--regenerate-password", "--regen-pass", "--regenerate-pass",
				action = "store_true", default = False)

	def do_query_get(self, **kwargs):
		all_data = super().do_query_get(**kwargs)
		if not self.copy_password:
			return all_data
		if len(all_data) == 1:
			pyperclip.copy(all_data[0].password)
			self.log("Password copied to clipboard")
		else:
			self.log(f"Can't copy password" \
				f" ({'no data queried' if len(all_data) == 0 else 'more than one data queried'})")
		return all_data

	def do_query_update(self, regenerate_password, **kwargs):
		if regenerate_password:
			kwargs["password"] = self.generate_password()
		data = super().do_query_update(**kwargs)
		if "password" in kwargs and self.copy_password:
			pyperclip.copy(data.password)
			self.log("New password copied to clipboard")
		return data

	def do_query_add(self, password = None, **kwargs):
		if password is None:
			password = self.generate_password()
		kwargs["password"] = password
		data = super().do_query_add(**kwargs)
		if self.copy_password:
			pyperclip.copy(data.password)
			self.log("New password copied to clipboard")
		return data

	@classmethod
	def create_parser(cls, parser):
		parser.add_argument("--print-password", "--print-pass",
			help = "prints password", action="store_true")
		parser.add_argument("--no-copy", dest = "copy_password",
			help = "doesn't copy password", action="store_false")
		parser.add_argument("--length", "-l", dest = "password_length", default = None, type = int)
		return super().create_parser(parser)

extra_keys = {
	"query": None,
	"print_password": False
}

class PasswordData(recordclass("PasswordData",
	PasswordQuery.keys + (*extra_keys.keys(),), defaults=extra_keys)):
	def init(self, query):
		self.print_password = query.print_password

	def pretty_str(self):
		s = []
		s.append(Colors.basic_text(f"Url: "))
		s.append(Colors.important_text(1, f"{self.url}"))
		s.append(Colors.basic_text(f" (id = {self.id})\n"))
		s.append(Colors.basic_text(f"Username: "))
		s.append(Colors.highlight_text(f"{self.username}\n"))
		if self.print_password:
			s.append(Colors.basic_text(f"Password: "))
			s.append(Colors.highlight_text(f"{self.password}\n"))
		s.append(Colors.color_reset)
		return "".join(s)

	def pretty_print(self):
		print(self.pretty_str())


PasswordQuery.DataT = PasswordData
