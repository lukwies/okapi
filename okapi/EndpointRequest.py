import tkinter as tk
from tkinter import ttk
import json

from widgets import MultiEntry
from widgets import ScrollFrame
from widgets import LeftLabel
from widgets import ButtonFrame
from widgets import ButtonLabel
from widgets import Separator
from widgets import ToolTip
from style import SmallTableHeader
from style import EntryLabel
from ResponseFrame import ResponseFrame
import DOC as doc

"""
|-----------------------------------------------|
| POST /users/{userId}				|
|-----------------------------------------------|
| path						|
| ————————————————————————————————————————————— |
| userId*    [			  ] integer    	|
|						|
| body						|
| ————————————————————————————————————————————— |
| body*      [		          ] json	|
|            [			  ]		|
|            [			  ]		|
|            [			  ]		|
|            [____________________]		|
|          					|
| header					|
| ————————————————————————————————————————————— |
| X-Api-Key* [                    ] string      |
| X-Session  [                    ] string      |
|-----------------------------------------------|
| [CANCEL] [SEND]				|
|-----------------------------------------------|
: col 0      : col 1 (weight=1)   : col 2       :

"""
_BG     = "#d0d0d0"	# Background color
_BG_TOP = "#575757"	# Background topframe (title)
_BG_BOT = "#bfbfbf"	# Background bottomframe (buttons)

class EndpointRequestFrame(tk.Frame):
	"""
	"""
	def __init__(self, apidoc, method, uri, respFrame:ResponseFrame):
		super().__init__(apidoc, background=_BG, highlightthickness=0)
#			highlightbackground="#999")
		self.A = apidoc
		self.respFrame = respFrame
		self.is_initialized = False
		self.set_endpoint(method, uri)


	def set_endpoint(self, method, uri):
		self.method  = method
		self.uri     = uri
		self.entries = []
		self.ep_dict = doc.DOC_get_endpoint(method, uri)

		if self.is_initialized:
			for child in self.winfo_children():
				child.destroy()
		self._setup_gui()
		self._bind_shortcuts()

	def _setup_gui(self):

		self.is_initialized = True
		self.grid_rowconfigure(1, weight=1)
		self.bind_all("<Control-s>", self._send_request)

		# Top frame (GET http://....)
		self._make_top_frame()\
			.grid(row=0, column=0, sticky="nswe", columnspan=3)

		# Scrollframe
		self.scroll = ScrollFrame(self, background=_BG)
		self.scroll.grid(row=1, column=0, sticky='nswe')
		self.scroll.interior.grid_columnconfigure(1, weight=1)

		params_dict = self._order_params_by_source(self.ep_dict['params'])
		y = 0

		for source,v in params_dict.items():
			if not v: continue
			print("[" + source + "]")
			# Section header
			SmallTableHeader(self.scroll.interior, source, bg=_BG)\
				.grid(row=y, column=0, columnspan=2, sticky='we', padx=3, pady=(5,0))
			Separator(self.scroll.interior, color="#999")\
				.grid(row=y+1, column=0, columnspan=3, sticky='we', padx=3, pady=(0,6))
			y += 2

			for key, param in v.items():
				print(" -> " + key)
				w = _ParamWidget(self, key, param, y)
				#w.entry.bind("<FocusIn>", self._scroll_to_entry)
				self.entries.append(w)
				y += 1

		self.scroll.interior.grid_rowconfigure(y, weight=1)

		# Buttons
		btns = {" cancel " : self._close,
			" clear "  : self._clear_entries_text,
			" send "   : self._send_request}
		bf = ButtonFrame(self, btns, style='label', bg=_BG_BOT, border_fg='#bababa',
                                btn_fg='#eee', btn_fg_hover='#ddd', btn_font="Arial 10",
				align='right',
				#btn_font_hover="Arial 8",
                                btn_bg="#606060", btn_bg_hover="#808080",
                                btn_border_fg='#aaa', btn_border_hover_fg='#a0a0a0',
                                btn_pady=3, btn_padx=(0,5))
		bf.grid(row=4, column=0, sticky='nswe')
		bf.set_tooltip(2, "Send request [Ctrl+S]")

	def _bind_shortcuts(self, bind=True):
		if bind:
			self.bind1 = self.bind_all("<Control-s>", self._send_request)
		else:	self.unbind("<Control-s>", self.bind1)

	def _make_top_frame(self):
		# Make topframe with method and url
		f = tk.Frame(self, background=_BG_TOP,
                                highlightthickness=1,
                                highlightcolor="#5a5a5a")
		f.columnconfigure(3, weight=1)
		LeftLabel(f, text=self.method, font="monospace 10 bold",
				bg=_BG_TOP, fg='#eee')\
			.grid(row=0, column=0, sticky='nswe', padx=(3,0))
		self.lUri = LeftLabel(f, text=self.uri, font="monospace 10",
					fg='#eee', bg=_BG_TOP)
		self.lUri.grid(row=0, column=1, sticky='nswe', padx=(3, 10))
		return f

	def _order_params_by_source(self, params_dict):
		# Order endpoint parameters by their source.
		res = {
			'path'   : {},
			'query'  : {},
			'body'   : {},
			'form-data' : {},
			'header' : {}
		}
		for k, v in params_dict.items():
			res[v['source']][k] = v
		return res

	def _send_request(self, ev=None):
		# Gather all parameters and send request
		hdrs  = doc.DOC['headers']
		body  = ""
		query = ""
		uri   = self.uri

		for e in self.entries:
			val = e.get()

			if not val and e.required:
				# Required value is missing!
				e.scroll_to()
				e.entry.set_border(nseconds=5)
				print("Missing required value")
				return
			elif val and not e.validate():
				# Value has invalid type
				e.scroll_to()
				e.entry.set_border(color='red', nseconds=5)
				self.A.msg("Parameter '"+e.key+"' format!", 1)
				return
			elif val:
				if e.source == "path":
					uri = doc.set_url_path_item(uri, e.key, val)
					print("URI:", uri)
				elif e.source == "header":
					hdrs[e.key] = val
				elif e.source == "query":
					if query: query += "&"
					query += e.key + "=" + val
				elif e.source == "body":
					body = val
					if e.cont_type:
						hdrs['Content-Type'] = e.cont_type
				elif e.source == "form-data":
					if body: body += "&"
					body += e.key + "=" + val

		print("= Send request =")
		address = doc.DOC['address'] + uri
		print(self.method, address, end="")
		if query:
			address += "?" + query
			print("?"+query)
		else:	print()

		if body:
			print("Body:\n"+body+"\n")

		if hdrs:
			print("Header:", hdrs)

		self.respFrame.request(self.method, address,
				body if body else None,
				hdrs if hdrs else None,
				None) # TODO: auth

	def _clear_entries_text(self, ev=None):
		# Clear content of all entries
		for e in self.entries:
			e.entry.clear()

	def _close(self):
		self._bind_shortcuts(False)
		self.scroll.unbind_scroll_events()
		self.A.close_endpoint_request_frame()


class _ParamWidget:
	"""
	Frame for entering a single parameter.
	NOTE: All widgets are added to given parent frame!
	Grid: | userId | * | [<entry>] | type |
	        0        1   2           3
	"""
	STL_KEY = {"font" : "monospace 9 bold",
		   "fg" : "#333", "bg" : _BG}

	def __init__(self, parent, key, param, row):
		self.parent = parent
		self.key = key
		self.type = param['type']
		self.source = param['source']
		self.required = param['required']
		self.cont_type = param['content_type'] if 'content_type' in param else ''
		self.param_dict = param
		self.entry = None	# Entry widget
		self._setup_gui(row)

	def get(self):
		"""
		Returns key, type, required, source, value
		"""
		return self.entry.get()

	def validate(self):
		"""
		Validate datatype of entry content.
		"""
		typ = self.entry.get_type()
		if not typ: return False

		if typ == self.type:
			return True

		# If entry has string value and parameter content-type
		# is application/json, try to parse json...
		is_model = typ in doc.DOC['models']
		if typ == 'string' and self.cont_type == "application/json":
			try:
				json.loads(self.entry.get())
				return True
			except Exception as e:
				self.parent.A.msg(str(e))
				print(e)
				return False

		if self.type == "string":
			return True
		return False

	def _set_pathitem(self, ev):
		if self.validate():
			self.parent.lUri['text'] = doc.set_url_path_item(
					self.parent.uri,
					self.key, self.get())

	def scroll_to(self):
		"""
		Scroll to parameter
		"""
		canv = self.parent.scroll.canvas
		widget_top = self.entry.winfo_y()
		canvas_top = canv.canvasy(0)

		if widget_top != canvas_top:
			delta = int(widget_top-canvas_top) - 10
			canv.yview_scroll(delta, "units")
			self.entry.w.focus_set()

	def _setup_gui(self, row):
		scrl = self.parent.scroll.interior

		# Label (key/name)
		f = tk.Frame(scrl, background=_BG)
		f.grid(row=row, column=0, sticky='nswe', pady=(1,0))
		LeftLabel(f, text=self.key, **self.STL_KEY)\
			.grid(row=0, column=0, sticky='nw',
				padx=(3,0))
		if self.param_dict['required']:
			tk.Label(f, text="*", font="Arial 9 bold", fg='red', bg=_BG)\
				.grid(row=0, column=1, sticky='nw',
					padx=(0, 5))

		# Entry field
		if 'values' in self.param_dict and self.param_dict['values']:
			self.entry = MultiEntry(scrl, 'options',
					options=self.param_dict['values'])
		elif self.param_dict['type'] == 'object':
			self.entry = MultiEntry(scrl, 'text')
		elif self.param_dict['type'] in doc.DOC['models']:
			self.entry = MultiEntry(scrl, 'text', height=5, width=20)
		else:	self.entry = MultiEntry(scrl, 'entry')

		if self.source == 'path':
			if self.entry.style == 'entry':
				self.entry.w.bind("<FocusOut>", self._set_pathitem)
				self.entry.w.bind("<Return>", self._set_pathitem, add='+')
		if 'info' in self.param_dict and self.param_dict['info']:
			ToolTip(self.entry, self.param_dict['info'])

		# Add title to entry
		tf = tk.Frame(self.entry, pady=1) #, background=tf_bg)
		tf.configure(highlightthickness=1, highlightbackground="#999")
		tf.grid_columnconfigure(1, weight=1)
		LeftLabel(tf, text=self.param_dict['type'], #bg=tf_bg,
				font="monospace 7", fg='#004d00')\
			.grid(row=0, column=0, sticky='wne', padx=3, pady=(1,0))

		if 'content_type' in self.param_dict and self.param_dict['content_type']:
			LeftLabel(tf, text=self.param_dict['content_type'],
					#bg=tf_bg,
					font="monospace 7", fg='#00004d')\
				.grid(row=0, column=1, sticky='wne', padx=3)

		self.entry.set_title(tf)
		self.entry.grid(row=row, column=1, sticky='nswe', padx=(3,10), pady=(0,5))
