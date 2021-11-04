
# personal colors, used on konsole with a custom color theme
class Colors:
	@staticmethod
	def create_color(col, bold, text = ""):
		return f"\x1b[{int(bold)};38;5;{col}m{text}"

	@classmethod
	def important_text(cls, importance, text=""): # less is more
		dat = [
			cls.create_color(197, True, text), # red/pink
			cls.create_color(13, True, text), # orange
			cls.create_color(10, True, text), # cyan ?
		]
		return dat[min(importance, len(dat)-1)]

	@classmethod
	def basic_text(cls, text=""):
		return cls.create_color(6, False, text) # dark green/blue

	@classmethod
	def highlight_text(cls, text=""):
		return cls.create_color(9, False, text) # white

Colors.color_reset = Colors.create_color(0, False)
