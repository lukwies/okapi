import os
from . CodeGenBase import CodeGenBase

HTML_PREFIX="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; padding: 20px; background-color: #f9f9f9; }
	h1 { color:#333; margin:0; }
        h2, h3, h4 {color: #333; margin: 0 0 10px 0; }
        .box { margin-bottom: 20px; padding: 5px 10px 10px 10px; border: 1px solid #ccc; border-radius: 5px; background-color: #fff; }
	.boxh { color: #3a3a3a; font-family: monospace; font-weight: bold; font-size: 20px; }
	.boxh2 { color: #444; font-family: monospace; font-size: 17px; }
        table { font-family: monospace; border-collapse: collapse; margin-bottom: 10px; }
        th, td { border: 1px solid #ddd; padding: 5px 8px 5px 8px; text-align: left; }
	th { color: #111; background-color: #f9f9f9; font-weight: bold; }
	b { color:#333; }
    </style>
</head>
<body>
"""

class HtmlDoc(CodeGenBase):
	def __init__(self, doc_, opts_):
		super().__init__(doc_, opts_)

	def generate(self):
		fullpath = os.path.join(self.opts.path,
				self.opts.filename)
		s  = HTML_PREFIX
		s += self._make_api_info()
		s += self._make_models()
		s += self._make_endpoints()
		s += '</body>\n</html>\n'
		try:
			f = open(fullpath, 'w')
			f.write(s)
			f.close()
			return True
		except Exception as e:
			print("! Failed to export textfile, "+str(e))
			return False

	def _make_api_info(self):
		# Creates title, description and address information
		s  = '  <h1>API Documentation</h1>\n'
		s += '  <hr>\n'
		s += '  <p>\n'
		s += '    <b>Api Name</b>: ' + self.doc['name'] + '<br>\n'
		s += '    <b>Version</b>: ' + self.doc['version'] + '<br>\n'
		s += '    <b>Address</b>: <a href="' + self.doc.get('address', '') + '">' + self.doc.get('address','') + '</a>\n'
		s += '  </p>\n'
		s += '  <p>' + self.doc.get('info','') + '</p>\n'
		return s + '\n'

	def _make_models(self):
		# Creates description for all models
		s  = '  <h2>Models</h2>\n'
		for name,m in self.doc['models'].items():
			s += '  <div class="box">\n'
			s += '    <span class="boxh">' + name + '</span>\n'
			if 'info' in m and m['info']:
				s += '    <p>' + m['info'] + '</p>\n'

			# Table with attributes
			s += '    <table>\n'
			s += '      <tr><th>Attribute</th><th>Type</th><th>Required</th><th>Values</th><th>Info</th></tr>\n'
			for k,v in m['attributes'].items():
				s += '      <tr>'
				s += '<td>' + k + '</td>'

				if 'is_array' in v and v['is_array']:
					ts = 'array[' + v['type'] + ']'
				else:	ts = v['type']
				s += '<td>' + ts + '</td>'

				if 'required' in v and v['required']:
					s += '<td>yes</td>'
				else:	s += '<td>no</td>'

				if 'values' in v and v['values']:
					s += '<td>' + ', '.join(v['values']) + '</td>'
				else:	s += '<td></td>'

				if 'info' in v and v['info']:
					s += '<td>' + v['info'] + '</td>'
				else:	s += '<td></td>'
				s += '</tr>\n'
			s += '    </table>\n'
			s += '  </div>\n'
		return s + '\n'


	def _make_endpoints(self):
		# Creates description for all endpoints
		s = '  <h2>Endpoints</h2>\n'

		for method,x in self.doc['endpoints'].items():
			for uri,ep in x.items():
				s += '  <div class="box">\n'
				s += '    <span class="boxh">' + method + '</span>\n'
				s += '    <span class="boxh2">' + uri + '</span>\n'
				s += '    <br>\n'

				if 'info' in ep and ep['info']:
					s += '    <p>' + ep['info'] + '</p>\n'

				if ep['params']:
					s += '    <h4>Parameters</h4>\n'
					s += '    <table>\n'
					s += '      <tr><th>Name</th><th>Source</th><th>Type</th><th>Required</th><th>Values</th><th>Info</th></tr>\n'

					for name,p in ep['params'].items():
						s += '      <tr>'
						s += '<td>' + name + '</td>'
						s += '<td>' + p['source'] + '</td>'

						if 'is_array' in p and p['is_array']:
							ts = 'array[' + p['type'] + ']'
						else:	ts = p['type']
						s += '<td>' + ts + '</td>'

						if 'required' in p and p['required']:
							s += '<td>yes</td>'
						else:	s += '<td>no</td>'

						if 'values' in p and p['values']:
							s += '<td>' + ', '.join(p['values']) + '</td>'
						else:	s += '<td></td>'

						s += '<td>' + p.get('info', '') + '</td>'

						s += '</tr>\n'
					s += '    </table>\n'

				if ep['response']:
					s += '    <h4>Responses</h4>\n'
					s += '    <table>\n'
					s += '      <tr><th>Status</th><th>Content-Type</th><th>Model</th><th>Headers</th><th>Info</th></tr>\n'

					for status,res in ep['response'].items():
						s += '      <tr>'
						s += '<td>' + status + '</td>'
						s += '<td>' + res.get('content_type', '') + '</td>'
						s += '<td>' + res.get('model', '') + '</td>'

						if 'headers' in res and res['headers']:
							s += '<td>' + ', '.join(res['headers'].keys()) + '</td>'
						else:	s += '<td></td>'
						s += '<td>' + res.get('info', '') + '</td>'
						s += '</tr>\n'
					s += '    </table>\n'
				s += '  </div>\n'
		return s
