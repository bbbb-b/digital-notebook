from datetime import datetime, timedelta
import math
import humanize
import dateparser
import pytimeparse

class DateTime(datetime):
	def relative_date_str(self):
		time_delta = self - DateTime.now().round()
		ret = self.duration_str(DateTime.now())
		if time_delta > timedelta():
			ret = "in " + ret
		else:
			ret = ret + " ago"
		return ret

	def duration_str(self, start_duration):
		time_delta = self - start_duration.round()
		ret = humanize.precisedelta(time_delta, format = "%.1f")
		return ret

	def human_date_str(self):
		return humanize.naturaltime(self)

	def to_str(self, precise_date = False):
		if not precise_date:
			return self.relative_date_str()
		return self.human_date_str()

	def round(self):
		return self.fromtimestamp(math.floor(self.timestamp()))

	def from_utc(self):
		return self.from_datetime(self + (DateTime.now().round() - DateTime.utcnow().round()))

	@classmethod
	def parse(cls, d):
		d = dateparser.parse(d)
		if d is not None:
			return cls.from_datetime(d).round()
		raise ValueError(f"Invalid date: {d}")

	@classmethod
	def parse_delta(cls, d):
		d = pytimeparse.parse(d)
		if d is not None:
			return timedelta(seconds = d)
		raise ValueError(f"Invalid delta: {d}")

	@classmethod
	def from_datetime(cls, d):
		return cls.fromtimestamp(d.timestamp())

	@classmethod
	def now(cls): # pylint: disable=W0221
		return super().now().round()
