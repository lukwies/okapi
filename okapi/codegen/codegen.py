import os
from enum import Enum

from . Esp32Server import Esp32ServerCode
from . Esp32Client import Esp32ClientCode
from . TextDoc import TextDoc

class CodeGenType(str,Enum):
	NOTHING      = ""
	ESP32_SERVER = "Esp32 Server"
	ESP32_CLIENT = "Esp32 Client"
	HTML         = "HTML documentation"
	TEXT         = "Textfile"

class CodeGenOptions:
	"""
	Options for code generation.
	"""
	def __init__(self, gentype=CodeGenType.NOTHING):

		# Defines what to export
		self.type = gentype

		# Path to the directory where generated code
		# will be stored.
		self.path = ""

		# Name of stored file
		self.filename = ""

		# This list must hold a tuple at each index where
		# the first item is the http-method and the second
		# item is the endpoint path/uri. If list is empty,
		# all endpoints are exported.
		# Example: [("GET", "/users"),("POST", "/users")]
		self.endpoints = []

		# Create comments ?
		self.comments = True

	def set_path(self, path):
		"""
		Set the directory path where exported code
		shall be created.
		"""
		self.path = path

	def add_endpoint(self, method, path):
		"""
		Add an endpoint to export
		"""
		self.endpoints.append((method, path))


def get_filename(doc, gentype:CodeGenType):
	"""
	Returns the name of the file/directory created
	when generating code.
	"""
	name = doc['name'].lower().replace(' ', '_').replace('-', '_')
	if gentype == CodeGenType.ESP32_SERVER:
		return name + '_server'
	elif gentype == CodeGenType.ESP32_CLIENT:
		return name + '_client'
	elif gentype == CodeGenType.TEXT:
		return name + '.txt'
	return name

def gen_code(doc, opts:CodeGenOptions):
	"""
	Generates the code and stores it..
	"""
	if opts.type == CodeGenType.ESP32_SERVER:
		return Esp32ServerCode(doc, opts).generate()
	elif opts.type == CodeGenType.ESP32_CLIENT:
		return Esp32ClientCode(doc, opts).generate()
	elif opts.type == CodeGenType.TEXT:
		return TextDoc(doc, opts).generate()

	return False
