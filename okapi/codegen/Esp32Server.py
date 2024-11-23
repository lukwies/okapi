import re
import os

from . esp import EspCodeBase
from . esp import esp_wifi_setup
from . esp import esp_setup

#
# NOTE:
# The esp server code uses path regex. This won't work out of the box,
# so on Linux do the following:
# - Create file ~/.arduino15/packages/espxxxx/hardware/espxxxx/{version}/platform.local.txt
# - Paste the following: compiler.cpp.extra_flags=-DASYNCWEBSERVER_REGEX=1
#

"""
Export apidoc to esp server code.

Creates:
	.../<api-name>_server/
           |__ <api-name>_server.ino
"""

class Esp32ServerCode(EspCodeBase):
	def __init__(self, doc_, opts_):
		super().__init__(doc_, opts_)

	def generate(self):
		"""
		Generate ESP servercode
		"""
		dirpath = os.path.join(self.opts.path, self.opts.filename)
		fullpath = os.path.join(dirpath, self.opts.filename+'.ino')
		print(". Generating code ...")
		print(". mkdir", dirpath)
		print(". path:", fullpath)
		s = self._make_includes_and_globals()
		s += esp_wifi_setup + '\n'
		s += 'void setup_routing() {\n'
		for method,uri in self.opts.endpoints:
			ep_dict = self.doc['endpoints'][method][uri]
			s += self._make_route(method, uri, ep_dict)
		s += '}\n\n'
		s += esp_setup

		if not os.path.isdir(dirpath):
			os.mkdir(dirpath)
		return self._write_file(fullpath, s)

	def _make_includes_and_globals(self):
		s = '#include <Arduino.h>\n'\
			'#include <WiFi.h>\n'\
			'#include <AsyncTCP.h>\n'\
			'#include <ESPAsyncWebServer.h>\n'
		if self.doc['models']:
			s += '#include <ArduinoJson.h>\n'
		s += '\n'\
			'const char* ssid     = "YOUR_SSID";\n'\
			'const char* password = "YOUR_PASSWORD";\n\n'\
			'AsyncWebServer server(80);\n\n'
		return s

	def _make_route(self, method, path, ep_dict):
		# Creates routing function for given
		# endpoint (method,path,dict).
		s = self._make_comment(ep_dict, ('summary', 'info'),
				False, '\t')
		# Pathitems
		uri,pathitems = self._make_ep_path(path)
		s += '\tserver.on("' + uri + '", '\
			+ 'HTTP_' + method + ',\n'

		# If we have a request body, the onBody callback
		# function must be implemented instead of the
		# default callback.
		body = self.ep_get_body(ep_dict)

		if body:
			s += self._make_onbody_callback(ep_dict, body, pathitems)
		else:	s += self._make_default_callback(ep_dict, pathitems)

		s += '\t);\n'
		s += '\tSerial.println(". Setup '+method+' '+path+'");\n\n'
		return s

	def _make_default_callback(self, ep_dict, pathitems, indent='\t'):
		# Create the default callback
		s  = indent + '    [](AsyncWebServerRequest *request) {\n'
		s += self._make_init_path_items(pathitems, indent+'\t')
		s += self._make_init_headers(ep_dict, indent+'\t')
		s += self._make_init_params(ep_dict, indent+'\t')
		s += self._make_200_response(ep_dict, indent+'\t')
		s += indent + '    }\n'
		return s

	def _make_onbody_callback(self, ep_dict, body, pathitems, indent='\t'):
		# Create callback for requests with body data
		s  = indent + '    [](AsyncWebServerRequest *request){}, NULL,\n'
		s += indent + '    [](AsyncWebServerRequest *request, uint8_t *data, size_t len,\n'
		s += indent + '					size_t index, size_t total) {\n'
		s += self._make_init_path_items(pathitems, indent+'\t')
		s += self._make_init_headers(ep_dict, indent+'\t') + '\n'
		s += indent+'\t' + 'if (request->contentType() != "application/json")\n'
		s += indent+'\t\t' + 'request->send(400);\n'
		s += indent+'\t' + 'else {\n'
		if body['type'] in self.doc['models']:
			s += indent+'\t\t// Reading model "'+body['type']+'"\n'
			s += self._make_model_comment(body['type'], indent+'\t\t')
		s += indent+'\t\t' + 'JsonDocument doc;\n'
		s += indent+'\t\t' + 'DeserializationError error = deserializeJson(doc, (char*)data, len);\n\n'
		s += indent+'\t\t' + 'if (error) {\n'
		s += indent+'\t\t\t' + 'Serial.print("deserializeJson(): ");\n'
		s += indent+'\t\t\t' + 'Serial.println(error.c_str());\n'
		s += indent+'\t\t\t' + 'request->send(400);\n'
		s += indent+'\t\t\t' + 'return;\n'
		s += indent+'\t\t' + '}\n'
		s += self._make_200_response(ep_dict, indent+'\t\t')
		s += indent+'\t' + '}\n'
		s += indent+'    }\n'
		return s


	def _make_200_response(self, ep_dict, indent='\t'):
		# Creates a 200 response

		if 'response' not in ep_dict or '200' not in ep_dict['response']:
			return indent + 'request->send(200);\n'

		resp = ep_dict['response']['200']
		s    = ''

		if 'model' in resp and resp['model'] in self.doc['models']:
			# Response has model
			model = self.doc['models'][resp['model']]
			s += self._make_json_response(model,indent)
		else:
			s += indent +'AsyncWebServerResponse *response =\n' + \
				 indent + '\trequest->beginResponse(200, '

			if 'content_type' in resp and resp['content_type']:
				s += '"' + resp['content_type'] + '",\n'
			else:	s += '"text/plain",\n'

			if 'example' in resp and resp['example']:
				print("EXAMPLE: [",resp['example'],"]")
				s += self.text_wrap('"'+resp['example']+'"',
						indent+'\t', indent+'\t')
			else:	s += indent + '\t"TODO"'
			s += ');\n'

		if 'headers' in resp and resp['headers']:
			s += "\n"
			for k,v in resp['headers'].items():
				s += indent + 'response->addHeader('+\
					'"'+k+'", "'+v+'");\n'

		s += indent + "request->send(response);\n"
		return s

	def _make_json_response(self, model_dict, indent=""):
		# Create json model response
		s = indent + 'AsyncResponseStream *response = '+\
			'request->beginResponseStream("application/json");\n'
		s += self._model_to_JsonDocument(model_dict, indent)
		s += indent + "serializeJson(doc, *response);\n"
		return s

	def _make_init_params(self, ep_dict, indent='\t'):
		# Create code for reading query/form-data parameters.
		s = ''
		for key,param_dict in ep_dict['params'].items():
			if param_dict['source'] in ('form-data', 'query'):
				if param_dict['required']:
					s += indent + '// Required parameter "'+key+'"\n'
					s += indent + 'if (!request->hasParam("'+ key + '")) {\n'
					s += indent + '\trequest->send(400, "text/plain", "Missing parameter '+key+'");\n'
					s += indent + '\treturn;\n'
					s += indent + '} else {\n'
					s += indent + '\tString '+key+' = request->getParam("'+key+'")->value();\n'
					s += indent + '\t// ...\n'
					s += indent + '}\n'
				else:
					s += indent + '// Optional parameter "'+key+'"\n'
					s += indent + 'if (request->hasParam("'+key+'")) {\n'
					s += indent + '\tString '+key+' = request->getParam("'+key+'")->value();\n'
					s += indent + '\t// ...\n'
					s += indent + '}\n'
		return s

	def _make_init_headers(self, ep_dict, indent='\t'):
		# Create code for reading headers
		s = ''
		for key,param_dict in ep_dict['params'].items():
			if param_dict['source'] == "header":
				name = key.replace('-', '_').lower()
				if param_dict['required']:
					s += indent + '// Required header "'+key+'"\n'
					s += indent + 'if (!request->hasHeader("'+ key + '")) {\n'
					s += indent + '\trequest->send(400, "text/plain", "Missing header '+key+'");\n'
					s += indent + '\treturn;\n'
					s += indent + '} else {\n'
					s += indent + '\tString '+name+' = request->getHeader("'+key+'")->value();\n'
					s += indent + '\t// ...\n'
					s += indent + '}\n'
				else:
					s += indent + '// Optional header "'+key+'"\n'
					s += indent + 'if (request->hasHeader("'+key+'")) {\n'
					s += indent + '\tString '+name+' = request->getHeader("'+key+'")->value();\n'
					s += indent + '\t// ...\n'
					s += indent + '}\n'
		return s


	def _make_ep_path(self, path):
		# Get endpoint path (might be a regex) and
		# all the pathitems.
		# Eg: "^\\/sensor\\/([0-9]+)\\/action\\/([a-zA-Z0-9]+)$"
		pathitems = re.findall(r"\{(\w+)\}", path)
		if not pathitems: return path,()
		path = re.sub(r"\{\w+\}", "{}", path)
		s = '^'
		for x in path.split("/"):
			if not x: continue
			if x == "{}":
				s += "\\\\/([a-zA-Z0-9]+)"
			else:	s += "\\\\/"+x
		s += '$'
		return s,pathitems

	def _make_init_path_items(self, pathitems, indent='\t'):
		# Get pathitems initialization string
		s = ''
		if pathitems:
			for i,pathitem in enumerate(pathitems):
				s += indent + 'String ' + pathitem  +\
					' = request->pathArg(' +\
					str(i) + ');\n'
			s += '\n'
		return s

