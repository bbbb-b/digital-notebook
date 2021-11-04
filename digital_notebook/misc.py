

def parse_bool(val):
	bool_mp = {
		"true" : True,
		"false" : False,
		"1" : True,
		"0" : False,
	}
	if val not in bool_mp:
		raise ValueError(f"Invalid value for bool: {val}")
	return bool_mp[val]
