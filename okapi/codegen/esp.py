from . CodeGenBase import CodeGenBase

"""
Baseclass, global variables and functions for
ESP code generation.
"""


esp_wifi_setup = \
	'void wifi_setup(void)\n'\
	'{\n'\
	'\tWiFi.mode(WIFI_STA);\n'\
	'\tWiFi.begin(ssid, password);\n'\
	'\n'\
	'\tuint32_t counter = 0;\n'\
	'\twhile (WiFi.status() != WL_CONNECTED) {\n'\
	'\t\tdelay(100);\n'\
	'\t\tcounter++;\n'\
	'\t\tif (counter > 150) {\n'\
        '\t\t\tSerial.println("Restarting ...");\n'\
        '\t\t\tESP.restart();\n'\
	'\t\t}\n'\
	'\t}\n'\
	'}\n'

esp_setup = \
	'void setup(void)\n'\
	'{\n'\
	'\tSerial.begin(115200);\n'\
	'\twifi_setup();\n'\
	'\tsetup_routing();\n'\
	'\tserver.begin();\n\n'\
	'\tSerial.print("Listening at ");\n'\
	'\tSerial.print(WiFi.localIP());\n'\
	'\tSerial.println(":80 ...");\n'\
	'}\n'\
	'\n'\
	'void loop() {\n'\
	'}\n'\


class EspCodeBase(CodeGenBase):
	"""
	Baseclass for ESP code generation.
	"""
	def __init__(self, doc_, opts_):
		super().__init__(doc_, opts_)

	def _make_comment(self, dct, keys:list,
			multiline=True, indent=''):
		# Creates a C-style comment from the value of
		# one or more keys in given dictionary.
		if not self.opts.comments:
			return ''

		if multiline:
			cmt = indent + '/*\n'
			for i, key in enumerate(keys):
				if key in dct and dct[key]:
					if i > 0: cmt += indent + ' *\n'
					cmt += self.text_wrap(dct[key],
							indent + ' * ',
							indent + ' * ')
			cmt += indent + ' */\n'
		else:
			cmt = ''
			for i, key in enumerate(keys):
				if key in dct and dct[key]:
					if i > 0: cmt += indent + '//\n'
					cmt += self.text_wrap(dct[key],
							indent + '// ',
							indent + '// ')
		return cmt

	def _make_model_comment(self, model_name, indent='\t'):
		# Make single line comments with model description
		s = ""
		if model_name not in self.doc['models']:
			return s
		for k,v in self.doc['models'][model_name]['attributes'].items():
			s += indent + '// ' + k + ' (' + v['type'] + ')\n'
		return s

	def _model_to_JsonDocument(self, model_dict, indent=''):
		# Creates a DynamicJsonDocument named 'json' with all
		# model attributes.
		s = indent + "JsonDocument doc;\n"
		for name,attr in model_dict['attributes'].items():
			s += indent + 'doc["' + name + '"] = // TODO ('+attr["type"]+')\n'
		return s


def type_to_c_datatype(typ):
	"""
	Convert model attribute type or parameter type to
	c/c++ datatype. Returns None if given type is invalid.
	"""
	types = {
		'string' : 'const char*',
		'integer' : 'int',
		'decimal' : 'float',
		'boolean' : 'bool'
	}
	return types[typ] if typ in types else None
