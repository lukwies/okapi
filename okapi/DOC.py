import re
import json
from os.path import join as path_join
from os.path import isfile as path_isfile
from urllib.parse import quote_plus

"""

Apis are stored at ~/.okapi/apidoc/{api-name} by default.

The API doc ist stored in a global dictionary named DOC.
It has the following format ([!] required, [ ] optional):
{
  'name' : <str>,			# [!] Api name
  'version' : <str>,			# [!] Api version
  'info': <str>,			# [!] Api description
  'address' : <str>,			# [!] Api server address
  'headers' : {},			# [!] Api headers
  'auth' : {				# [!] Authentication TODO
    'type' : <str>, ?			# [!] Authentication type (basic,bearer,...) TODO
    'params' : {} ?			# [!] Parameters for authentication TODO
  },
  'models' : {				# [!] Model definitions
    <NAME> : {
      'info' : <string>,		# [ ] Model description
      'attributes' : {			# [!] Attributes
        <NAME> : {
		'required' : <bool>,    # [!] Attribute is required?
		'type' : <string>,      # [!] Datatype
		'is_array': <bool>,     # [ ] Value is array
		'values' : [val1, ...], # [ ] Default values
		'info' : <string>	# [ ]
        }, ...
      }
    }, ...
  },
  'endpoints' : {			# [!] Api Endpoints
    <METHOD> : {			# [!] HTTP method
      <URI> : {				# [!] Endpoint URI
	'summary' : <str>,		# [!] Short description
        'info: <str>,			# [ ] Long description
        'params' : {			# [ ] Parameters
          <KEY> : {			# [!] Parameter name/key
            'required' : <bool>		# [!] Parameter is mandatory?
            'type' : <str>,		# [!] Datatype
            'source' : <string>,	# [!] Where does the parameter come from ? (query,path,body,header)
	    'is_array': <bool>,     	# [ ] Value is array
	    'content_type': <str>,	# [ ] Request content type
            'info' : <str>,		# [ ] Additional information
          },
	  ...
        },
        'response' : {			# [!] Response
          <CODE> : {			# [!] HTTP status code
            'summary' : <str>,		# [!] Short description
	    'content_type' : <str>,	# [ ] content-type: ('text/ascii', 'application/json', ...)
	    'example': <str>,		# [ ] Example for response body
	    'model' : <str>		# [ ] Respond with model? This is the model's name.
            'headers' : {},		# [ ] Response headers TODO
          },
          ...
        }
    },
    ...
  }
}
"""
PARAMETER_DATATYPES = [
	'string', 'integer', 'decimal', 'boolean',
	'object', 'array[integer]',
	'array[string]', 'array[object]'
]
PARAMETER_EXAMPLES = {
	'string'  : "",
	'integer' : 0,
	'decimal' : 0.0,
	'boolean' : False,
	'object'  : {} }

PARAMETER_SOURCES = ['query', 'body', 'path']

RESPONSE_CONTENT_TYPES = [
	'application/json',
	'application/xml',
	'image/giff',
	'image/jpg',
	'image/png',
	'text/css',
	'text/csv',
	'text/html',
	'text/javascript',
	'text/plain'
]

# The dictionary where the current apidoc is
# stored.
DOC = {}

# Hash of last status to detect changes.
DOC_last_hash = None

def DOC_new():
	"""
	Create a new, empty apidoc dictionary at 'DOC'.
	"""
	global DOC
	DOC = dict({
		'name'    : '',
		'version' : '',
		'address' : '',
		'info'    : '',
		'headers' : {},
		'auth'    : {
			'type' : None,
			'params' : {}
		},
		'models'    : {},
		'endpoints' : {}
	})
	DOC_set_unchanged()


def DOC_load(filepath):
	""" Load DOC """
	global DOC
	try:
		f = open(filepath, "r")
		DOC = json.load(f)
		DOC_set_unchanged()
		return True
	except Exception as e:
		print("! Failed to load apidoc " + filepath)
		print("  "+str(e))
		return False

def DOC_hash():
	""" Get hash of DOC """
	global DOC
	return hash(json.dumps(DOC, sort_keys=True))

def DOC_has_changed():
	""" Has DOC changed ? """
	global DOC_last_hash
	return DOC_last_hash != DOC_hash()

def DOC_set_unchanged():
	""" Set DOC to not changed """
	global DOC_last_hash
	DOC_last_hash = DOC_hash()

def DOC_print():
	""" Print DOC formatted. """
	global DOC
	print(json.dumps(DOC, indent=4))

def DOC_get_storage_filename(doc=None):
	""" Get filename for storing apidoc """
	if not doc:
		global DOC
		doc = DOC
	if not doc['name']: return ''
	return doc['name'].lower().replace(' ', '_')

def DOC_get_storage_path(basedir, doc=None):
	"""
	Get storage path.
	The path will be: <basedir>/apidoc/DOC['name'].json
	"""
	return path_join(path_join(basedir, "apidoc"),
			DOC_get_storage_filename(doc) + ".json")

def DOC_is_storage_path(basedir, doc=None):
	""" Does path for current DOC exists ? """
	return path_isfile(DOC_get_storage_path(basedir, doc))

def DOC_save_json(basedir):
	"""
	Store DOC as json file.
	The path will be <basedir>/apidoc/DOC['name'].json
	Return:
	  Path of stored file
	"""
	global DOC
	p = DOC_get_storage_path(basedir)
	f = open(p, "w")
	json.dump(DOC, f, indent=2)
	f.close()
	DOC_set_unchanged()
	return p


def DOC_is_endpoint(method, uri):
	"""
	Check if endpoint exists in DOC.
	"""
	if not method or not uri:
		return False
	elif method not in DOC['endpoints'] or \
		uri not in DOC['endpoints'][method]:
		return False
	return True

def DOC_add_endpoint(method, uri, ep_dict):
	"""
	Add endpoint to DOC.
	"""
	global DOC
	if method not in DOC['endpoints']:
		DOC['endpoints'][method] = {}
	DOC['endpoints'][method][uri] = ep_dict.copy()

def DOC_get_endpoint(method, uri, return_new_EP=False):
	"""
	Get endpoint from DOC by method and uri.
	Args:
	  method: HTTP method
	  uri: Endpoint URI
	  return_new_EP: Return new endpoint if not exists?
	Return:
	  Endpoint or New endpoint or None
	"""
	global DOC
	if DOC_is_endpoint(method, uri):
		return DOC['endpoints'][method][uri]
	if return_new_EP:
		return new_endpoint()
	return None

def DOC_delete_endpoint(method, uri):
	"""
	Delete endpoint from DOC by method and uri.
	"""
	global DOC
	if DOC_is_endpoint(method, uri):
		del DOC['endpoints'][method][uri]
		if not DOC['endpoints'][method]:
			del DOC['endpoints'][method]
		return True
	return False

def DOC_model_to_dict(model_name, zero=False):
	"""
	Returns model as example dictionary.
	Args:
	  model_name: Name of model
	  zero:       Set model attributes to 0?
	"""
	global DOC
	if model_name not in DOC['models']:
		return {}

	realtype = {
		'string'  : lambda x: str(x),
		'integer' : lambda x: int(x),
		'bool'    : lambda x: bool(x),
		'decimal' : lambda x: float(x),
		'object'  : lambda x: json.loads(x)
	}
	res = {}
	for name,attr in DOC['models'][model_name]['attributes'].items():
		typ = attr['type']
		if typ in DOC['models']:
			# Attribute is model
			res[name] = DOC_model_to_dict(typ)
		elif 'example' in attr and attr['example']:
			# Attribute has an example set
			res[name] = realtype[typ](attr['example'])
		else:	res[name] = PARAMETER_EXAMPLES[typ]

	return res

def DOC_max_endpoint_method_len():
#	global DOC
	if not DOC['endpoints']:
		return 0
	else:	return len(max(DOC['endpoints'].keys(), key=len))

def DOC_max_endpoint_uri_len():
	global DOC
	max_ = 0
	for method,v in DOC['endpoints'].items():
		if not v: continue
		n = len(max(v))
		if n > max_: max_=n
	return max_
'''
def DOC_model_dumps(model_name, format='json', indent=2):
	"""
	Return model as either json or xml string.
	Args:
	  model_name:  Name of model
	  format:      Return format ('json' or 'xml')
	Return:
	  Model as formatted string.
	"""
	mod = DOC_model_to_dict(model_name)
	if format == 'json':
		return json.dumps(mod, indent=indent)
'''
def new_model():
	return {'info' : '',
		'attributes' : {}}
def new_model_attribute():
	return {'type' : 'string',
		'required' : True,
#		'is_array' : False,
#		'values' : [],
		'info' : ''}

def new_endpoint():
	return {'summary' : '',
		'info' : '',
		'params' : {},
                'response' : {}}
def new_endpoint_parameter():
	return {'type' : 'string',
		'source' : 'query',
		'required' : False}
def new_endpoint_response():
	return {'summary' : ''}
#		'type' : '',
#		'model' : '',
#		'example' : '',
#		'headers' : ''}




### Validation #####
reg = re.compile(r"/?(?:\w/?)+")
reg_ph = re.compile(r"/?(?:\{?\w\}?/?)+")
reg_params = re.compile(r"(?:\w+=\w+&?)+")

def is_valid_URI(uri, allow_parameters=False, allow_placeholders=False):
	"""
	Returns True if given URI is well formatted.
	Uri with parameters:
	  /foo/bar?key=value&...
	Uri with placeholders:
	  /foo/{bar}/...
	"""
	if allow_parameters and '?' in uri:
		x = uri.split('?')
		uri = x[0]

		if not reg_params.fullmatch(x[1]):
			return False

	if allow_placeholders:
		res = reg_ph.fullmatch(uri)
	else:   res = reg.fullmatch(uri)

	return False if not res else True

def is_valid_http_code(code:str):
	"""
	Check if given string is a valid HTTP status code.
	"""
	if not code or not code.isdigit():
		return False
	c = int(code)
	return (c >= 100 and c <= 103) or \
	   (c >= 200 and c <= 208) or c == 226 or \
	   (c >= 300 and c <= 308) or \
	   (c >= 400 and c <= 418) or \
	   (c >= 421 and c <= 426) or \
	   c==428 or c==429 or c==431 or c==451 or \
	   (c >= 500 and c <= 508) or c==510 or c==511

def is_valid_parameter_key(key):
	"""
	Check if given key has valid format.
	That key must start with a lowercase alphabetic
	ascii character followed by an arbitrary number
	of alphanumerics, '-' or '_'.
	"""
	if not key or not key[0].isalpha():
		return False
	for c in key:
		if not c.isalnum() and not c in ('-', '_'):
			return False
	return True


def is_valid_model_name(name):
	if not name or not name[0].isalpha():
		return False
	for c in name:
		if not c.isalnum() and not c in ('-', '_'):
			return False
	return True


#def url_path_item(url):

def get_url_path_items(url):
	"""
	Get all path items from url.
	example: "/foo/{bar}/{baz}" returns ["bar", "baz"]
	"""
	return re.findall(r"\{(\w+)\}", url)

def set_url_path_item(url, pathitem, value):
	"""
	Replace pathitem in uri with given value.
	Args:
	  url:      URL       (eg. '/users/{userid}'
	  pathitem: Path item (eg. 'userid')
	  value:    Value     (eg. '123456')
	Return:
	  Url with replaced pathitems (eg. '/users/123456')
	"""
	pattern = r"\{" + pathitem + r"\}"
	return re.sub(pattern, value, url)

def remove_url_path_items(path):
	"""
	Remove path item names from given path.
	example: "/foo/{bar}/{baz}" returns "/foo/{}/{}"
	"""
	return re.sub(r"\{\w+\}", "{}", path)

def encode_query_params(s):
	"""
	Encode given url/query-params.
	"""
	return quote_plus(s)
