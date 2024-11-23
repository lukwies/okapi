import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesno
import json
import pyperclip

from widgets import ScrollFrame
from widgets import ButtonLabel
from widgets import ButtonFrame
from widgets import LeftLabel
from widgets import ScrollTextFrame
from widgets import LabeledTextFrame
from widgets import TextStyler
from widgets import PopupMenu

from EndpointEditWindow import EndpointEditWindow
from EndpointRequest import EndpointRequestFrame

from style import TableHeader
from style import InfoLabel

import DOC as doc

import time

"""
 0     1        2     			     3      4   5
+----------------------------------------------------------+
| GET | /index |  Get index data            | edit | X | ↓ |
+----------------------------------------------------------+

"""


METHOD_COLORS = {
	"GET" : "#00802b",
	"POST" : "#0066ff",
	"PUT"  : "#993399",
	"DELETE" : "#e60000",
	"HEAD"   : "#00e600" }

# Used fonts
A8 = "Arial 8"
A8b = A8+" bold"
A9 = "Arial 9"
A9b = A9+" bold"


class EndpointsFrame(tk.Frame):
	"""
	Frame with a scrollable list of API endpoints.
	"""
	def __init__(self, apidoc, *args, **kwargs):
		super().__init__(apidoc, *args, **kwargs)
		self.A = apidoc
		self._setup_gui()

	def load_from_DOC(self):
		"""
		Load endpoints from doc to ui.
		"""
		if self.scroll:
			self.scroll.grid_remove()

		self.scroll = ScrollFrame(self)

		if not doc.DOC['endpoints']:
			tk.Label(self, text="No endpoints")\
				.grid(row=1, column=0, sticky='nswe')
		else:
			self.scroll.interior.grid_columnconfigure(0, weight=1)
			self.scroll.grid(row=1, column=0, sticky='nswe', pady=2, padx=2)

			self.max_method_len = doc.DOC_max_endpoint_method_len()
			self.max_uri_len    = doc.DOC_max_endpoint_uri_len()

			# Create list with endpoint frames
			self.epframes = []
			for method in doc.DOC['endpoints'].keys():
				for uri in doc.DOC['endpoints'][method].keys():
					ep = EndPointListItem(self.scroll.interior,
							self, method, uri)
					self.epframes.append(ep)

			# Sort list and add all frames to grid
			y=0
			self.epframes = sorted(self.epframes)
			for epf in self.epframes:
				epf.grid(row=y, column=0, sticky='nswe',
					padx=3, pady=(3,0))
				y += 1

	def save_to_DOC(self):
		pass

	def _edit_endpoint(self, method=None, uri=None):
		win = EndpointEditWindow(self, method, uri)
		win.attributes('-topmost', 'true')

	def _setup_gui(self):
		# Endpoints are ordered by ("method" or "url")
		self.order_type = "method"
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)
		self.scroll = None
		btns = {" Add ":self._edit_endpoint}
		self.btnframe = ButtonFrame(self, btns, style='label', bg='#ddd', border_fg='#aaa',
				btn_fg='#444', btn_fg_hover='#777', btn_font="Arial 8 bold",
				btn_bg='#e3e3e3', btn_bg_hover='#efefef',
				btn_border_fg='#aaa', btn_border_hover_fg='#a0a0a0',
				btn_pady=3, btn_padx=3)
		self.btnframe.grid(row=0, column=0, sticky='senw')


class EndPointListItem(tk.Frame):
	"""
	Single endpoint list item.
	The listitem can be right-clicked to open a menu.

	GET /index/{foo}            (edit)[x][↓]
	"""
	BG = '#eee'

	def __init__(self, scrlframe, parent, method, uri):
		super().__init__(scrlframe)
		self.scrlframe = scrlframe
		self.parent = parent
		self.A = parent.A
		self.method = method
		self.uri = uri
		self.ep_dict = doc.DOC['endpoints'][method][uri]
		self._setup_gui()
		self._bind_events()


	def _setup_gui(self):
		self.grid_columnconfigure(0, weight=1)

		# Topframe with Method, URI and click-labels
		self.tf = tk.Frame(self, background=self.BG)
		self.tf.grid_columnconfigure(2, weight=1)
		self.tf.grid(row=0, column=0, sticky='nswe')

		# Method
		if self.method in METHOD_COLORS: fg=METHOD_COLORS[self.method]
		else: fg="#444"
		m = self.method + " "*(self.parent.max_method_len-len(self.method))
		self.lMethod = LeftLabel(self.tf, text=m,
				font='monospace 11 bold', bg=self.BG, fg=fg)
		self.lMethod.grid(row=0, column=0, sticky='nswe', padx=2)
		# URI
		u = self.uri + " "*(self.parent.max_uri_len-len(self.uri))
		self.lUri = LeftLabel(self.tf, text=u, fg='#444',
				font='monospace 10', bg=self.BG)
		self.lUri.grid(row=0, column=1, sticky='nswe')
		# Summary
		if 'summary' in self.ep_dict:
			self.lSum = LeftLabel(self.tf, text=self.ep_dict['summary'],
						font=A9, fg='#a0a0a0', bg=self.BG)
			self.lSum.grid(row=0, column=2, sticky='nswe', padx=15, pady=(3,0))
		# Edit button
#		self.bEdit = ButtonLabel(self.tf, text="(edit)", bg=self.BG, hover_bg=self.BG,
#				on_click=self.edit_endpoint, font='Arial 8')
#		self.bEdit.grid(row=0, column=3)

		# Delete button
#		self.bDel = ButtonLabel(self.tf, text="[x]",
#				bg=self.BG, hover_bg=self.BG,
#				fg='#e00', font='Arial 8',
#				on_click=self.delete_endpoint)
#		self.bDel.grid(row=0, column=4)
		# Expand button
		self.bExpand = ButtonLabel(self.tf, text="[↓]",
				on_click=self._expand, bg=self.BG,
				hover_bg=self.BG, font='Arial 8')
		self.bExpand.grid(row=0, column=5, padx=2)
		# Expand frame
		self.fExpand = ExpandFrame(self, self.ep_dict, self.BG)



	def edit_endpoint(self):
		ew = EndpointEditWindow(self.parent, self.method, self.uri)
		ew.attributes('-topmost', 'true')

	def delete_endpoint(self):
		yes = askyesno(title='Delete endpoint?',
				message='Do you really want to delete endpoint '+self.uri+'?')
		if yes:
			if doc.DOC_delete_endpoint(self.method, self.uri):
				print(". deleted " + self.uri)
				self.A.msg("Deleted '"+self.uri+"'")
				self.parent.load_from_DOC()

	def _bind_events(self):
		# Bind events
		self.bind("<Enter>", lambda e: self._set_border(True))
		self.bind("<Leave>", lambda e: self._set_border(False))

		menu_items = {
			"Request" : lambda: self.A.open_endpoint_request_frame(
					self.method, self.uri),
			"Edit" :  self.edit_endpoint,
			"Delete" : self.delete_endpoint
		}
		menu = PopupMenu(self, menu_items,
			(self.tf, self.lMethod, self.lUri, self.lSum))
		menu.bind("<Enter>", lambda e: self._set_border(True))


	def _set_border(self, on=True):
		# Set colored border around listitem
		if on:
			self.configure(highlightthickness=1,
				highlightbackground=METHOD_COLORS[self.method])
		else:	self.configure(highlightthickness=0)

	def _expand(self, ev=None):
		# Expand frame
		self.bExpand['text'] = '[↑]'
		self.bExpand.on_click = self._shrink
		self.lUri['fg'] = '#00b'
		self.fExpand.grid(row=1, column=0, sticky='nswe',
				columnspan=6)

	def _shrink(self):
		# Shring frame
		self.bExpand['text'] = '[↓]'
		self.bExpand.on_click = self._expand
		self.lUri['fg'] = '#444'
		self.fExpand.grid_remove()


	def __lt__(self, other):
		# Used for sorting
		if self.uri < other.uri:
			return True
		if self.uri == other.uri:
			return self.method < other.method
		return False

class ExpandFrame(tk.Frame):
	"""
	Expanded endpoint frame.
	"""
	def __init__(self, parent, ep_dict, bg):
		super().__init__(parent, background=bg)
		self.BG = bg
		self.parent = parent
		self.A = parent.A
		self.ep_dict = ep_dict
		self.params = ep_dict['params']
		self._setup_gui()


	def _setup_gui(self):
		"""
		"""
		self.grid_columnconfigure(0, minsize=20)
		self.grid_columnconfigure(2, weight=1)

		# Endpoint Info
		if 'info' in self.ep_dict and self.ep_dict['info']:
			InfoLabel(self, self.ep_dict['info'])\
				.do_grid(0, 1, columnspan=2)

		# Parameters
		f = tk.Frame(self, background='#ddd', padx=3)
		f.grid_columnconfigure(1, weight=1)
		f.grid(row=1, column=1, sticky='nswe', columnspan=2,
				pady=(15,10), padx=(0,3))
		LeftLabel(f, text="Parameters", bg='#ddd',
				font='Arial 11 bold', fg='#222')\
			.grid(row=0, column=0, sticky='nswe')

		# Button to send request
		ButtonLabel(f, text='request',
				on_click=self._on_send_request, bg='#ddd',
				font='monospace 9', hover_font='monospace 9',
				fg='#1f7a1f', hover_fg='#2eb82e')\
			.grid(row=0, column=2, sticky='we', padx=3)

		y = 4
		if len(self.ep_dict['params']):
			TableHeader(self, "Name").do_grid(2, 1)
			TableHeader(self, "Description").do_grid(2, 2)
			ttk.Separator(self, orient='horizontal')\
				.grid(row=3, column=1, sticky='we', padx=(2,5), columnspan=2)

			for key,p in self.ep_dict['params'].items():
				ParamFrame(self, key, p, self.BG)\
					.grid(row=y, column=1, sticky='nswe', padx=(0,30))
				pif = ParamInfoFrame(self, key, p, self.BG)
				pif.grid(row=y, column=2, padx=(1,5), sticky='nswe',
						pady=(5,0))
				y += 1
		else:	InfoLabel(self, "No parameters").do_grid(3, 1, padx=3, columnspan=2)

		# Responses
		LeftLabel(self, text="Response", bg='#ddd',
				font='Arial 11 bold', fg='#222')\
			.grid(row=y, column=1, pady=10, ipady=1,
				ipadx=1, columnspan=2, padx=(0, 5), sticky='nswe')
		y+=1
		if len(self.ep_dict['response']):
			TableHeader(self, "Code").do_grid(y, 1)
			TableHeader(self, "Description").do_grid(y, 2)
			ttk.Separator(self, orient='horizontal')\
				.grid(row=y+1, column=1, sticky='we',
					padx=2, columnspan=2, pady=(0,5))
			y += 2
			for code,resp in self.ep_dict['response'].items():
				ResponseFrame(self, code, resp, self.BG)\
					.grid(row=y, column=1, sticky='nswe', padx=(2,30))
				ResponseInfoFrame(self, code, resp, self.BG)\
					.grid(row=y, column=2, padx=(1,5), sticky='nswe')
				y += 1
		else:	InfoLabel(self, "No responses")\
				.do_grid(y, 1, padx=3, pady=(0,5), columnspan=2)

	def _on_send_request(self, ev=None):
		self.A.open_endpoint_request_frame(
			self.parent.method, self.parent.uri)

class ParamFrame(tk.Frame):
	"""
	Frame with parameter parameter key, datatype and required?
	KEY (TYPE) *(required)
	"""
	def __init__(self, parent, key, param, bg):
		super().__init__(parent, background=bg)
#		self.parent = parent
		self.BG = bg
		self._setup_gui(key, param)

	def _setup_gui(self, key, p):
		"""
		| body *required | <INFO>
		| datatype       |
		| source         |
		"""
		self.grid_columnconfigure(1, weight=1)

		lframe = tk.Frame(self, background=self.BG)
		lframe.grid(row=0, column=0, sticky='nw', pady=4)

		# Key
		LeftLabel(lframe, text=key, bg=self.BG, fg='#222',
				font='monospace 10 bold')\
			.grid(row=0, column=0, padx=(3,0), sticky='nsw')
		# Is required ?
		if p['required']:
			LeftLabel(lframe, text='*required',
					bg=self.BG, font='Arial 8', fg='red')\
				.grid(row=0, column=1, sticky='nsw')
		# Datatype
		s = p['type']
		if 'is_array' in p and p['is_array']:
			s = "array[" + s + "]"
		LeftLabel(lframe, text=s, fg='#444', bg=self.BG,
				font='monospace 9')\
			.grid(row=1, column=0, sticky='nsw', columnspan=2, padx=3)
		# Source
		LeftLabel(lframe, text='('+p['source']+')', fg='#aaa', bg=self.BG,
				font='monospace 9 italic')\
			.grid(row=2, column=0, sticky='nsw', columnspan=2, padx=3)

class ParamInfoFrame(tk.Frame):
	"""
	Right side of single parameter list item.
	Holds the parameter information, example/model, ...
	"""

	def __init__(self, parent, key, param, bg):
		super().__init__(parent, background=bg)
#		self.parent = parent
		self.BG = bg
		self.key = key
		self.param_dict = param
		self.eValue = None
		self._setup_gui(key, param)

	def get(self):
		"""
		Return:
		  key,type,source,required,value
		"""
		return self.key,\
			self.param_dict['type'], \
			self.param_dict['source'],\
			self.param_dict['required'],\
			self.eValue.get()

	def _setup_gui(self, key, p):
		"""
		"""
		self.grid_columnconfigure(1, weight=1)

		# Parameter description
		if 'info' in p and p['info']:
			InfoLabel(self, p['info'], font_size=9, bg=self.BG)\
				.do_grid(0, 0, pady=(2,3), columnspan=2)

		# Request content-type
		if 'content_type' in p and p['content_type']:
			tk.Label(self, text=p['content_type'],
					font='Arial 8 bold', bg=self.BG, fg='#333')\
				.grid(row=0, column=1, sticky='e', padx=5, pady=(5,0))

		height=5
		# If parameter has a model, show example/model frame
		if p['type'] in doc.DOC['models']:
			mef = ModelExampleFrame(self, p['type'])
			mef.grid(row=1, column=0, sticky='nswe',
					padx=1, columnspan=2, pady=(5,0))
			height = mef.get_height()


class ResponseFrame(tk.Frame):
	"""
	Show http status code and content-type
	"""
	def __init__(self, parent, code, resp, bg):
		super().__init__(parent, background=bg)
		LeftLabel(self, text=code, font='Arial 10 bold',
				fg='#333', bg=bg)\
			.grid(row=0, column=0, sticky='nwes')

		if 'content_type' in resp and resp['content_type']:
			LeftLabel(self, text=resp['content_type'],
					font='Arial 8 bold', bg=bg, fg='#555')\
				.grid(row=1, column=0, sticky='nswe', pady=(2,5))

class ResponseInfoFrame(tk.Frame):
	"""
	Right side of single response list item.
	"""
	def __init__(self, parent, status_code, resp_dict, bg):
		super().__init__(parent, background=bg)
		self.parent = parent
		self._setup_gui(status_code, resp_dict, bg)

	def _setup_gui(self, code, resp, bg):

		self.grid_columnconfigure(0, weight=1)

		InfoLabel(self, resp['summary'], font_size=9, bg=bg)\
			.do_grid(0, 0, pady=(1,5))

		if 'model' in resp and resp['model']:
			# Show model and example
			ModelExampleFrame(self, resp['model'])\
				.grid(row=2, column=0, sticky='nswe',
					columnspan=2, pady=(0,10))
		elif 'example' in resp and resp['example']:
			# Show example
			ltf = LabeledTextFrame(self, "Example")
			ltf.text.set_text(resp['example'])
			ltf.text.adjust_height()
			ltf.grid(row=2, column=0, sticky='nswe',
					columnspan=2, pady=(0,10))

		if 'headers' in resp and resp['headers']:
			# Show headers
			ltf = LabeledTextFrame(self, "Headers")
			ltf.text.set_dict(resp['headers'])
			ltf.text.adjust_height()
			ltf.grid(row=3, column=0, sticky='nswe',
					columnspan=2, pady=(0,10))


class ModelExampleFrame(tk.Frame):
	"""
	Frame holding the model as example and model definition.
	+-------------------------------+
	| Example | Model		|
	+-------------------------------+
	|				|
	|				|
	|				|
	+-------------------------------+
	| [json/xml]			|
	+-------------------------------+

	"""
	BG = "#dedede"
	def __init__(self, parent, model_name):
		super().__init__(parent)
		self.model_name = model_name
		self.model_dict = doc.DOC_model_to_dict(model_name)
		self.content_type = 'json' # or 'xml'
		self._setup_gui()
		self._open_tab('example', 'json')

	def get_height(self):
		return self.scroll.nlines()

	def _setup_gui(self):
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)

		# Top frame
		self.topframe = self._make_top_frame()

		# Shows the model as colored json/xml
		self.scroll = ScrollTextFrame(self, disabled=True,
				scroll_vertical=False, scroll_horizontal=False,
				font='Monospace 9', fg='#eee', bg='#292929',  #bg='#1f1f14', #fg='#333', bg='#cdcdcd',
				relief='flat')
		self.textStyler = TextStyler(self.scroll, True)
		PopupMenu(self.scroll, {'copy': lambda:pyperclip.copy(self.scroll.get_text())})
		# Shows the model
		self.modelframe = self._make_model_frame()

		# Bottomframe to select the content-type (json/xml)
		self.bottomframe = self._make_bottom_frame()

		self.topframe.grid(row=0, column=0, sticky='nswe')
		self.scroll.grid(row=1, column=0, sticky='nswe')
		self.modelframe.grid(row=1, column=0, sticky='nswe')

	def _open_tab(self, tab='example', ctype=None):
		# Open tab ('example' or 'model')
		if tab == "example":
			self.scroll.tkraise()
			self.bExample.enable()
			self.bModel.disable()
			if ctype: self._set_content_type(ctype)
			self.bottomframe.grid(row=2, column=0, sticky='nswe')
		elif tab == "model":
			self.modelframe.tkraise()
			self.bModel.enable()
			self.bExample.disable()
			self.bottomframe.grid_remove()

	def _set_content_type(self, ctype):
		# Set content-type of example model output.
		# Types are: 'json' and 'xml'
		if ctype == 'json':
			if not self.bJson.enabled:
				self.textStyler.set_json(self.model_dict)
				self.bJson.enable()
				self.bXml.disable()
		elif ctype == 'xml':
			if not self.bXml.enabled:
				self.textStyler.set_xml(self.model_name, self.model_dict)
				self.bXml.enable()
				self.bJson.disable()
		else:	return

	def _make_top_frame(self):
		# Create topframe.
		class Btn(ButtonLabel):
			def __init__(self, parent, text, func=None, bg='#999'):
				super().__init__(parent, text=text, on_click=func,
					font='Arial 8 bold', hover_font='Arial 8 bold',
					fg='#555', hover_fg='#222', bg=bg, hover_bg=bg)
		top = tk.Frame(self, background=self.BG)
		self.bExample = Btn(top, " Example ", lambda:self._open_tab('example'), bg=self.BG)
		self.bExample.grid(row=0, column=0, sticky='nswe', pady=2)

		self.bSep = tk.Label(top, text='|', font='Arial 8', bg=self.BG)
		self.bSep.grid(row=0, column=1, sticky='nw')

		self.bModel = Btn(top, " Model ", lambda:self._open_tab('model'), bg=self.BG)
		self.bModel.grid(row=0, column=2, sticky='nswe')
		return top

	def _make_model_frame(self):
		# Create a frame with model definition
		BG = '#bebcbc'
		FG = '#222'
		model = doc.DOC['models'][self.model_name]
		f = tk.Frame(self, background=BG)
		f.grid_columnconfigure(2, weight=1)

		LeftLabel(f, text=self.model_name+" {",
					font="Arial 9 bold", bg=BG, fg=FG)\
			.grid(row=0, column=0, columnspan=3, sticky='nswe', padx=3, pady=(5,3))
		y = 1
		for name,attr in model['attributes'].items():

			if attr['required']:
				tk.Label(f, text='*', font='Arial 8 bold', bg=BG, fg='red')\
					.grid(row=y, column=0, sticky='e', padx=(20,0))

			LeftLabel(f, text=name, font="Arial 8 bold", bg=BG, fg=FG)\
				.grid(row=y, column=1, sticky='nswe', padx=(0, 10))
			LeftLabel(f, text=attr['type'], font="Arial 8", bg=BG, fg=FG)\
				.grid(row=y, column=2, sticky='nswe')
			y += 1
		LeftLabel(f, text="}", font="Arial 9 bold", bg=BG)\
			.grid(row=y, column=0, sticky='nswe', padx=3, columnspan=3)
		return f


	def _make_bottom_frame(self):
		# Creates the bottom frame.
		# This frame holds two buttons to change the content-type.
		BG = '#dedede'
		values = ["application/json", "application/xml"]
		self.vCType = tk.StringVar(self)
		self.vCType.set(values[0])

		class Btn(ButtonLabel):
			def __init__(self, parent, text, func=None, bg=BG):
				super().__init__(parent, text=text, on_click=func,
					font='Arial 8 bold', hover_font='Arial 8 bold',
					fg='#555', hover_fg='#1b1b1b', bg=bg, hover_bg=bg)

		bottom = tk.Frame(self, background=BG)
		bottom.grid_columnconfigure(3, weight=1)

		self.bJson = Btn(bottom, " json", lambda:self._set_content_type('json'))
		self.bJson.grid(row=0, column=0, sticky='nswe', pady=2, padx=(1,0))

		tk.Label(bottom, text='|', font="Arial 8", bg=BG)\
			.grid(row=0, column=1, sticky='nw')

		self.bXml = Btn(bottom, "xml", lambda:self._set_content_type('xml'))
		self.bXml.grid(row=0, column=2, sticky='nswe')
		return bottom

