import argparse
from recordclass import recordclass
from misc import parse_bool
from date_utils import DateTime
from query import Query
from colors import Colors


class EventQuery(Query):
	table_name = "events"
	keys = ("id", "name", "notes", "url", "time", "end_time", "type", "completed")
	order_by = "time"
	precise_date = False # default

	@staticmethod
	def sort_key(event):
		return event.time

	@staticmethod
	def get_data_t():
		return EventData

	def init_args(self, precise_date, **kwargs):
		self.precise_date = precise_date
		return super().init_args(**kwargs)

	@classmethod
	def add_key_arguments(cls, parser, op):
		if op == "delete":
			return
		if op == "get":
			parser.add_argument("--id", type = int)
		cls.add_argument_group(parser, "--name", required = op == "add")
		#parser.add_argument("--name", required = op == "add")
		note_group = cls.add_argument_group(parser, "--notes", "--note", "--desc")
		#note_group.add_argument("--notes", "--desc")
		if op == "update":
			note_group.add_argument("--notes-concat", "--desc-concat", default = None)
		parser.add_argument("--url", "--domain")
		if op != "get":
			start_date_group = parser.add_mutually_exclusive_group(required = op == "add")
			start_date_group.add_argument("--time", "--date", type = DateTime.parse)
			start_date_group.add_argument("--utc-time", "--utc-date", type = DateTime.parse, default = None)
			end_date_group = parser.add_mutually_exclusive_group() # not required
			end_date_group.add_argument("--end-time", "--end-date", type = DateTime.parse)
			end_date_group.add_argument("--duration", type = DateTime.parse_delta, default = None)
		parser.add_argument("--type", choices = ["local", "global", "other"])
		parser.add_argument("--completed", type = parse_bool)
		if op == "get":
			parser.add_argument("--show-completed", "-s", "--all", action="store_true", default = False)
			parser.add_argument("--min-time", "--min-date", "--min", type = DateTime.parse, default = None)
			parser.add_argument("--max-time", "--max-date", "--max", type = DateTime.parse, default = None)

	def do_query_add(self, utc_time, duration, **kwargs):
		if utc_time is not None:
			kwargs["time"] = utc_time.from_utc()
		if duration is not None:
			kwargs["end_time"] = kwargs["time"] + duration
		elif "end_time" not in kwargs:
			kwargs["end_time"] = kwargs["time"]
		return super().do_query_add(**kwargs)

	def do_query_get(self, show_completed, min_time, max_time, **kwargs):
		if min_time is not None:
			min_time = min_time.round()
		if max_time is not None:
			max_time = max_time.round()
		if min_time is not None and max_time is not None:
			self.validate(min_time <= max_time, "min time is more than max time")
		if not show_completed:
			kwargs["completed"] = False
		where_stmts = []
		args = []
		if min_time is not None:
			where_stmts.append("? <= time")
			args.append(str(min_time))
		if max_time is not None:
			where_stmts.append("time <= ?")
			args.append(str(max_time))
		if len(where_stmts) != 0:
			where_stmts = [" AND ".join(where_stmts)]
		return super().do_query_get(where_stmts = where_stmts, args = args, **kwargs)

	def do_query_update(self, id, utc_time, notes_concat, duration, **kwargs):
		data = self.validate_id_exists(id)
		if notes_concat is not None:
			if len(data.notes) != 0:
				notes_concat = f"{data.notes} // {notes_concat}"
			kwargs["notes"] = notes_concat
		if utc_time is not None:
			kwargs["time"] = utc_time.from_utc()
		if duration is not None:
			kwargs["end_time"] = kwargs.get("time", data.time) + duration
		if "time" in kwargs and "end_time" not in kwargs:
			kwargs["end_time"] = kwargs["time"] + (data.end_time - data.time)
		time = kwargs.get("time", data.time)
		end_time = kwargs.get("end_time", data.end_time)
		self.validate(time <= end_time, "Time must not be more than end time")
		return super().do_query_update(id = id, **kwargs)

	@classmethod
	def create_parser(cls, parser):
		parser.add_argument("--precise-date", help = "makes the date format more precise, but unreadable",
			action="store_true")
		return super().create_parser(parser)

extra_keys = {
	"query": None,
	"precise_date": False
}

class EventData(recordclass("EventData",
	EventQuery.keys + (*extra_keys.keys(),), defaults=extra_keys)):
	def init(self, query):
		self.query = query
		self.precise_date = query.precise_date
	# they should all be rounded by default but lets make sure
		self.time = DateTime.fromisoformat(self.time).round()
		if self.end_time is not None: # pylint: disable=E0203
			self.end_time = DateTime.fromisoformat(self.end_time).round()

	def get_priority(self):
		if DateTime.now() > self.time:
			return 0
		if DateTime.parse("in 1 day") > self.time:
			return 1
		return 2

	def pretty_str(self):
		s = []
		s.append(Colors.basic_text(f"Event: "))
		s.append(Colors.important_text(self.get_priority(), f"{self.name} "))
		s.append(Colors.basic_text(f"{self.type} (id = {self.id})\n"))
		s.append(Colors.basic_text(f"Date: "))
		s.append(Colors.highlight_text(f"{self.time} ({self.time.to_str(self.precise_date)})\n"))
		if self.end_time != self.time:
			s.append(Colors.basic_text(f"Duration: "))
			s.append(Colors.highlight_text(f"{self.end_time.duration_str(self.time)} "))
			s.append(f"(until {self.end_time.to_str(self.precise_date)})\n")
		if self.url is not None:
			s.append(Colors.basic_text("Url: "))
			s.append(Colors.highlight_text(f"{self.url}\n"))
		if len(self.notes) != 0:
			s.append(Colors.highlight_text(f"{self.notes}\n"))
		if self.completed:
			s.append(Colors.basic_text("Completed\n"))
		s.append(Colors.color_reset)
		return "".join(s)

	def pretty_print(self):
		print(self.pretty_str())

EventQuery.DataT = EventData
