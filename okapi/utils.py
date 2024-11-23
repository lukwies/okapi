import json

def parse_key_value_text_to_dict(text):
	"""
	Parses given text (lines separated by '\n') with
	key value pairs to dictionary.
	Args:
	  text: Text with key-value pairs.
		For example an input "Life: boring\nHobby: coding\n"
		would lead to {"Life":"boring", "Hobby":"coding"}.
	Return:
	  Parsed dictionary or None if given text has invalid
          format.
	"""
	d = {}
	for line in text.split("\n"):
		line = line.strip()
		if not line: continue

		try:
			i = line.index(':')
			key = line[:i].strip()
			val = line[i+1:].strip()
			if not key or not val:
				print(". parse text: Invalid line ["+line+"]")
				return None
			else:	d[key] = val
		except:
			print(". parse text: Invalid line ["+line+"]")
			return None
	return d


def block_widget(widget, block=True):
	"""
	Block or unblock given widget.
	"""
#	print("== Children of {} ==".format(type(widget)))
	for w in widget.winfo_children():
#		print("| {}".format(type(w)))
		if hasattr(w, "block"):
#			print("|  (block)")
			w.block(block)
		elif w.winfo_children():
			block_widget(w, block)
		elif 'state' in w.keys():
#			print("|  (en/disable)")
			w.configure(state="disabled" if block else "normal")
#		else:	print("|  (error)")
#	print("==============================\n")
