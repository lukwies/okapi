import os
from . CodeGenBase import CodeGenBase

class TextDoc(CodeGenBase):
	def __init__(self, doc_, opts_):
		super().__init__(doc_, opts_)

	def generate(self):
		fullpath = os.path.join(self.opts.path,
				self.opts.filename)

		s  = self._make_api_info()
		s += self._make_models()
		s += self._make_endpoints()

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
		s  = ' API DOCUMENTATION\n'
		s += ' ~~~~~~~~~~~~~~~~~\n\n'

		if self.doc['info']:
			s += self.text_wrap(self.doc['info'], ' ', ' ', 85) + '\n'

		s += ' Name:    ' + self.doc['name'] + '\n'
		s += ' Version: ' + self.doc['version'] + '\n'
		s += ' Address: ' + self.doc['address'] + '\n\n'

		return s + '\n'

	def _make_models(self):
		# Creates description for all models
		s  = ' MODELS\n'
		s += ' ~~~~~~\n\n'

		for name,m in self.doc['models'].items():

			# Name and info
			s += ' ' + name + '\n'
			if 'info' in m and m['info']:
				s += self.text_wrap(m['info'],
					'   ', '   ', 85-16) + '\n'

			nl = self._max_key_len(m['attributes'], 10)
			tl = self._max_value_len(m['attributes'], 'type', 4)

			s += '   ' + self._make_str('Attribute', nl) + '   '
			s += self._make_str('Type', tl) + '   '
			s += 'Required\n'
			s += '   ' + '-'*35 + '\n'

			for k,v in m['attributes'].items():
				s += '   '
				# Name
				s += self._make_str(k, nl) + '   '

				# Type
				if 'is_array' in v and v['is_array']:
					ts = '[' + v['type'] + ']'
				else:	ts = v['type']
				s += self._make_str(ts, tl) + '   '

				# Is required ?
				if 'required' in v and v['required']:
					s += 'yes' + ' '*7
				else:	s += 'no' + ' '*8


				s += '\n'
			s += '\n'
		return s + '\n'


	def _make_endpoints(self):
		# Creates description for all endpoints
		s  = ' ENDPOINTS\n'
		s += ' ~~~~~~~~~\n\n'

		for method,x in self.doc['endpoints'].items():
			for uri,ep in x.items():
				s += ' ' + method + ' ' + uri + '\n\n'

				if 'info' in ep and ep['info']:
					s += self.text_wrap(ep['info'],
						'   ', '   ', 85-16) + '\n'
				if ep['params']:
					s += '   Parameters\n\n'
					nl = self._max_key_len(ep['params'], 4)
					sl = self._max_value_len(ep['params'], 'source', 6)
					tl = self._max_value_len(ep['params'], 'type', 4)

					s += '     ' + self._make_str('Name', nl) + '   '
					s += self._make_str('Source', sl) + '   '
					s += self._make_str('Type', tl) + '   '
					s += 'Required\n'
					s += '     ' + '-'*55 + '\n'

					for name,p in ep['params'].items():
						s += '     '
						s += self._make_str(name, nl) + '   '
						s += self._make_str(p['source'], sl) + '   '

						# Type
						if 'is_array' in p and p['is_array']:
							ts = '[' + p['type'] + ']'
						else:	ts = p['type']
						s += self._make_str(ts, tl) + '   '

						# Is required ?
						if 'required' in p and p['required']:
							s += 'yes'
						else:	s += 'no'

						s += '\n'
					s += '\n'

				if ep['response']:
					s += '   Responses\n\n'

					tl = self._max_value_len(ep['response'], 'content_type', 12)
					ml = self._max_value_len(ep['response'], 'model', 5)

					s += '     Status   '
					s += self._make_str('Content-Type', tl) + '   '
					s += self._make_str('Model', ml) + '   '
					s += 'Headers\n'
					s += '     ' + '-'*55 + '\n'

					for status,res in ep['response'].items():
						s += '     ' + status + '      '
						s += self._make_str(res.get('content_type', '-'), tl) + '   '
						s += self._make_str(res.get('model', '-'), ml) + '   '

						if 'headers' in res and res['headers']:
							s += ', '.join(res['headers'].keys())
						else:	s += '-'
						s += '\n'
					s += '\n'
				s += '\n'
		return s

	def _make_str(self, text, n):
		# Make string filled with whitespaces until its
		# length reaches n.
		return text + ' '*(n-len(text))

	def _max_key_len(self, d, min=0):
		# Return length of longest key in given dictionary.
		n = min
		for key in d.keys():
			if len(key) > n: n=len(key)
		return n

	def _max_value_len(self, d, name, min=0):
		# Return length of longest value in dict[name]
		n = min
		for k,v in d.items():
			if name not in v: continue
			l = len(v[name])
			# If this is called with model['attributes'] as d,
			# increase length by 2 if type is array
			if 'is_array' in v and v['is_array']: l+=2
			if l > n: n = l
		return n

	def _make_line(self, length=85):
		# Create line with given length
		return "*"*length + '\n'
#		return " " + "-"*length + '\n'
