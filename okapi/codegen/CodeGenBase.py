import textwrap

class CodeGenBase:
	"""
	Baseclass for code generation.
	NOTE: Method generate() MUST be implemented by child class!
	"""
	def __init__(self, doc, opts):
		"""
		Args:
		  doc:    The doc dictionary (see "apidoc/DOC.py")
		  opts:   Options for code generation (CodeGenOpts)
		"""
		self.doc = doc
		self.opts = opts

	def generate(self) -> bool:
		"""
		Generate code and store it to self.opts.path.
		Returns True on success, False on error.
		NOTE: This must be implemented by child class!
		"""
		return False


	def text_wrap(self, text, indent="",
			indent2="", width=50,
			prefix="", suffix=""):
		"""
		Wrap text to lines.
		Like TextWrapper, except it returns a string not a list.
		"""
		s = textwrap.TextWrapper(width,
				initial_indent=indent,
				subsequent_indent=indent2)\
			.wrap(text)
		return prefix + "".join([x+"\n" for x in s]) + suffix


	def ep_get_body(self, ep_dict):
		"""
		Get endpoint request body parameter dict.
		If endpoint has no request body parameter,
		return value is None.
		"""
		for name,p in ep_dict['params'].items():
			if p['source'] == 'body' and name == 'body':
				return p
		return None

	def _write_file(self, path, content):
		"""
		Write to file.
		"""
		try:
			f = open(path, "w")
			f.write(content)
			f.close()
			print(". Stored " + self.opts.type.value + " at " + path)
			return True
		except Exception as ex:
			print("! Failed to export " + self.opts.type.value + " to " + path)
			print("  >> " + str(ex))
			return False
