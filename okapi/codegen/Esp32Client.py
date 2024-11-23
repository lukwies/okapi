import os

from . esp import EspCodeBase
from . esp import esp_wifi_setup
from . esp import type_to_c_datatype

"""
Export apidoc to esp client code.

Creates:
	.../<api-name>_client/
           |__ <api-name>_client.ino
	   |__ api_calls.h
	   |__ api_calls.cpp

#ifndef API_CALLS_H
#define API_CALLS_H 1

#define API_HOST_ADDRESS "http://..."

bool GET_users(int userid);
bool POST_users(int userid, const char *name);
bool DELETE_users(int userid);


#endif


bool GET_users(int userid, const char *name) {
	String url = API_HOST_ADDRESS + "?name=" + name;
	HttpClient http;
	http.begin(url);

	http.addHeader("Content-Type", "application/json");
	http.POST(jsonData);

	int res = http.GET();
	if (res <= 0) {
		Serial.print("! Error on http request, ");
		Serial.println(res);
		return false;
	}

	String payload = http.getString();
	// ...
	http.end();
	return true;
}

"""

class Esp32ClientCode(EspCodeBase):
	def __init__(self, doc_, opts_):
		super().__init__(doc_, opts_)

	def generate(self):
		"""
		Generate ESP32 client code
		"""
		dirpath = os.path.join(self.opts.path, self.opts.filename)
		if not os.path.isdir(dirpath):
			os.mkdir(dirpath)

		if not self._create_main_file(dirpath):
			return False
		elif not self._create_header_file(dirpath):
			return False
		elif not self._create_source_file(dirpath):
			return False
		return True

	def _create_main_file(self, dirpath):
		# Creates the main (.ino) file
		s = '#include <WiFi.h>\n'\
			'#include <HTTPClient.h>\n'
		if self.doc['models']:
			s += '#include <ArduinoJson.h>\n'
		s += '#include "api_calls.h"\n'
		s += '\n'\
			'const char *ssid     = "YOUR_SSID";\n'\
			'const char *password = "YOUR_PASSWORD";\n\n'
		s += esp_wifi_setup + '\n'
		s += 'void setup()\n{\n'
		s += '\tSerial.begin(115200);\n'
		s += '\twifi_setup();\n\n'
		s += '\t// TODO ...\n\n'
		s += '}\n\n'
		s += 'void loop() {}\n'

		fullpath = os.path.join(dirpath, self.opts.filename+'.ino')
		return self._write_file(fullpath, s)

	def _create_header_file(self, dirpath):
		# Creates the file 'api_calls.h'
		p = os.path.join(dirpath, "api_calls.h")

		s  = '#ifndef API_CALLS_H\n#define API_CALLS_H 1\n\n'
		s += '#include <WiFi.h>\n'
		s += '#include <HttpClient.h>\n'
		if self.doc['models']:
			s += '#include <ArduinoJson.h>\n'
		s += '\n'
		for method,uri in self.opts.endpoints:
			s += self._make_func_decl(method, uri) + ';\n'

		s += '\n#endif\n'
		fullpath = os.path.join(dirpath, 'api_calls.h')
		return self._write_file(fullpath, s)

	def _create_source_file(self, dirpath):
		# Creates the file 'api_calls.cpp'
		p = os.path.join(dirpath, "api_calls.cpp")

		s  = '#include "api_calls.h"\n\n'
		s += '#define API_HOST_ADDRESS "'+self.doc['address']+'"\n\n'

		for method,uri in self.opts.endpoints:
			ep = self.doc['endpoints'][method][uri]
			s += self._make_func_impl(method, uri, ep) +'\n'

		fullpath = os.path.join(dirpath, 'api_calls.cpp')
		return self._write_file(fullpath, s)

	def _make_func_impl(self, method, path, ep_dict) -> str:
		# Make api call function implementation
		body = self.ep_get_body(ep_dict)
		s = self._make_comment(ep_dict, ('summary', 'info'))
		s += self._make_func_decl(method, path)
		s += '\n{\n'
		s += '\t' + self._make_url(method, path, ep_dict)
		s += '\t' + 'HttpClient http;\n'
		s += '\t' + 'http.begin(url);\n\n'

		if body:add = [('content-type','application/json')]
		else:	add = None
		s += self._make_add_header(ep_dict, add)

		if body:
			model = self.doc['models'][body['type']]
			s += self._model_to_JsonDocument(model, '\t') + '\n'
			s += '\tString body;\n'
			s += '\tserializeJson(doc, body);\n\n'

		s += '\t' + 'int code = http.' + method + '('
		if body: s += 'body'
		s += ');\n'
		s += '\t' + 'if (code <= 0) {\n'
		s += '\t\t' + 'Serial.println("! Error sending request (' + method \
				+ ' ' + path + '");\n'
		s += '\t\t' + 'Serial.println(http.errorToString(res));\n'
		s += '\t' + '} else {\n'
		s += '\t\t' + 'String resp = http.getString();\n'

		if 'response' in ep_dict and '200' in ep_dict['response']:
			r200 = ep_dict['response']['200']
			if 'model' in r200 and r200['model']:
				s += '\t\tif (code == 200) {\n'
				s += self._make_model_comment(r200['model'], '\t\t\t')
				s += '\t\t\tJsonDocument doc;\n'
				s += '\t\t\tDeserializationError error = deserializeJson(doc, resp);\n'
				s += '\t\t}\n'
		else:
			s += '\t\t' + 'Serial.println(code);\n'
			s += '\t\t' + 'Serial.println(resp);\n'
		s += '\t' + '}\n'
		s += '}\n'
		return s

	def _make_func_decl(self, method, path) -> str:
		# Make function declaration
		p = path.lower().replace('-', '')\
			.replace('{', '').replace('}', '')\
			.replace('/', '_')
		return 'void ' + method + p + '(void)'

	def _make_url(self, method, path, ep_dict):
		# Make url
		s = 'String url = API_HOST_ADDRESS + "' + path + '"'
		if method == 'GET':
			qs = self._make_query_string(ep_dict)
		else:	qs = None
		s += ';\n' if not qs else '\n\t\t+ "'+qs+'";\n'
		return s


	def _make_query_string(self, ep_dict, src='query') -> str:
		# Creates query string from parameters where
		# source is 'query'.
		nparam = 0
		s = ''
		for name,param in ep_dict['params'].items():
			if param['source'] == src:
				s += '&' if nparam>0 else '?'
				s += name + '='
				nparam += 1
		return s

	def _make_add_header(self, ep_dict, add=None) -> str:
		# Make http.addHeader() calls. To add extra headers
		# call it like self._make_add_header(ep, [('h1','val1'), ...])
		s = ''
		for name,param in ep_dict['params'].items():
			if param['source'] == 'header':
				s += '\thttp.addHeader("'+name+'", "");\n'
		if add:
			for k,v in add:
				s += '\thttp.addHeader("'+k+'", "'+v+'");\n'
		if s: s+='\n'
		return s

	"""
	def _make_api_call_func_decl(self, method, path, ep_dict) -> str:
		# Make apicall function declaration
		nparam = 0
		s = 'void ' + method + self._clear_path(path) + '('

		for name,param in ep_dict['params'].items():
			if param['source'] == 'header':
				if nparam: s += ', '
				s += 'const char *hdr_'
				s += name.lower().replace('-', '_')
				nparam += 1
		for name,param in ep_dict['params'].items():
			if param['source'] in ('path', 'query', 'form-data'):
				if nparam: s += ', '
				s += 'const char *'
				s += name.lower().replace('-', '_')
				nparam += 1
			elif param['source'] == 'body' and param['type'] in self.doc['models']:
				# If we have a model as body, make all model attributes
				# to be function parameters.
				modelname = param['type']
				model = self.doc['models'][modelname]
				for name,attr in model['attributes'].items():
					if nparam: s += ', '
					dtype = type_to_c_datatype(attr['type'])
					s += dtype + ' ' + modelname + '_' + name
					if 'is_array' in attr and attr['is_array']:
						s += '[], size_t ' + modelname + '_' + name + '_len'
					nparam += 1
		s += ')'
		return self._adjust_func_decl_width(s)

	def _adjust_func_decl_width(self, s, max_line_width=50) -> str:
		# Make function declaration string match given line width.
		snew = ''
		i = 0
		for c in s:
			snew += c
			i += 1
			if i >= max_line_width and c == ',':
				snew += '\n\t\t'
				i = 16
		return snew

	"""
