from recordclass import recordclass
from query import Query
from misc import parse_bool
from colors import Colors


class TodoQuery(Query):
	table_name = "todos"
	keys = ("id", "name", "notes", "url", "priority", "completed")
	order_by = "priority"

	@staticmethod
	def get_priorities():
		return {
			"asap" : 0,
			"soon" : 1,
			"passive" : 2,
			"eventually" : 3,
		}

	@classmethod
	def sort_key(cls, data):
		return cls.get_priorities()[data.priority]

	@staticmethod
	def get_data_t():
		return TodoData

	@classmethod
	def add_key_arguments(cls, parser, op):
		if op == "delete":
			return # delete only deletes by ids
		if op == "get":
			parser.add_argument("--id", type = int)
		cls.add_argument_group(parser, "--name", required = op == "add")
		cls.add_argument_group(parser, "--notes", "--note", "--desc")
		if op == "update":
			parser.add_argument("--notes-concat", "--note-concat", "--desc-concat", default = None)
		parser.add_argument("--url", "--domain")
		parser.add_argument("--priority", choices = tuple(cls.get_priorities().keys()))
		completed_group = parser.add_mutually_exclusive_group()
		completed_group.add_argument("--completed", type = parse_bool)
		if op == "get":
			completed_group.add_argument("--show-completed", action = "store_true", default = False)

	def do_query_get(self, show_completed, **kwargs):
		if not show_completed:
			kwargs["completed"] = False
		return super().do_query_get(**kwargs)

	def do_query_update(self, id, notes_concat, **kwargs):
		data = self.validate_id_exists(id)
		if notes_concat is not None:
			self.validate("notes" not in kwargs, "can't use both `notes` and `notes-concat` arguments")
			if len(data.notes) != 0:
				notes_concat = f"{data.notes} // {notes_concat}"
			kwargs["notes"] = notes_concat
		return super().do_query_update(id = id, **kwargs)

extra_keys = {
	"query": None,
	"priority_int" : 0
}

# this part is still kinda weird
class TodoData(recordclass("Todo", TodoQuery.keys + tuple(extra_keys.keys()), defaults=extra_keys)):
	def init(self, query):
		self.query = query
		self.priority_int = TodoQuery.get_priorities()[self.priority]

	def pretty_str(self):
		s = []
		s.append(Colors.basic_text("Todo: "))
		s.append(Colors.important_text(self.priority_int, self.name))
		s.append(Colors.basic_text(f" {self.priority} (id = {self.id})\n"))
		if self.url is not None:
			s.append(Colors.basic_text(f"Url: "))
			s.append(Colors.highlight_text(f"{self.url}\n"))
		if len(self.notes) > 0:
			s.append(Colors.highlight_text(f"{self.notes}\n"))
		s.append(Colors.color_reset)
		return "".join(s)

	def pretty_print(self):
		print(self.pretty_str())
