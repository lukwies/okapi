import tkinter as tk
import re
from tkinter import ttk

from widgets import LeftLabel
from widgets import ToolTip
from widgets import ScrollTextFrame
from widgets import Tablist

TAB_FONT="Arial 10"
BTN_FONT="Monospace 7 bold"
TAB_COLOR='#ddd'

class RequestOptionsFrame(tk.Frame):

	def __init__(self, parent, okapi):

		super().__init__(parent)
		self.okapi = okapi
		self._setup_gui()


	def get(self):
		"""
		Get request parameters, headers and auth
		options.

		return:
		  params,headers,auth
		"""
		body    = self.frames['body'].get()
		headers = self.frames['hdrs'].get()
		uagent  = self.frames['uagent'].get()
#		auth    = self.frames['auth'].get()

		if uagent:
			# Add useragent to headers
			headers["User-Agent"] = uagent

		# TODO auth
		return body,headers,None


	def _setup_gui(self):
		self.grid_columnconfigure(0, weight=1)

		tab_btns = {
			'body' : (' Body ', lambda:self._open_frame('body')),
			'hdrs' : (' Header ', lambda:self._open_frame('hdrs')),
			'uagent' : (' Useragent ', lambda:self._open_frame('uagent')),
			'auth' : (' Authenticate ', lambda:self._open_frame('auth'))
		}
		self.tabs = Tablist(self, tab_btns, bg_hover='#ccc', bg='#bbb')
		self.frames = {
			'body' : RequestBodyFrame(self, self.okapi),
			'hdrs' : RequestHeadersFrame(self, self.okapi),
			'uagent' : RequestUseragentFrame(self, self.okapi),
			'auth' : RequestAuthFrame(self, self.okapi)
		}
		self.frames['hdrs'].set({"DNT":"1"})
		self.current_frame = None

		self.tabs.grid(row=0, column=0, sticky='nswe')

	def _open_frame(self, title):
		if self.tabs.is_enabled(title):
			self.tabs.disable(title)
			self.frames[title].grid_remove()
		else:
			if self.current_frame:
				self.frames[self.current_frame].grid_remove()
			self.tabs.enable(title)
			self.frames[title].grid(row=1, column=0, sticky='nswe')
			self.current_frame = title


class RequestBodyFrame(tk.Frame):
	"""
	Tab where query parameters can be added.
	"""
	def __init__(self, parent, okapi):
		super().__init__(parent)
		self.okapi = okapi
		self.configure(pady=3, background=TAB_COLOR)

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(2, weight=1)
		self.txtBody = ScrollTextFrame(self, height=4, font='monospace 9')
		self.txtBody.grid(row=0, column=0,
				sticky='nswe', rowspan=3, padx=2, pady=2)

		self.btnLoad = tk.Button(self, text="load",
				font=BTN_FONT, command=self._on_load,
				highlightthickness=0)
		self.btnLoad.grid(row=0, column=1, sticky='nwe', padx=2, pady=(2,2))

		self.btnClear = tk.Button(self, text="clear",
				font=BTN_FONT, command=self._on_clear,
				highlightthickness=0)
		self.btnClear.grid(row=1, column=1, sticky='nwe', padx=2)


	def set(self, text):
		self.txtBody.set_text(text)

	def get(self):
		return self.txtBody.get_text()

	def _on_load(self):
		self.okapi.msg("NOT IMPLEMENTED !!", 1)

	def _on_clear(self):
		self.txtBody.clear_text()




class RequestHeadersFrame(tk.Frame):
	"""
	Tab with a textarea where header values can be added.
	"""
	def __init__(self, parent, okapi):
		super().__init__(parent)
		self.okapi = okapi
		self._setup_gui()

	def get(self):
		"""
		Get headers as dictionary.
		Returns None on misformatted header value(s).
		"""
		hdr = {}
		for line in self.txt.get_text().split('\n'):
			try:
				i = line.index(':')
				key = line[:i].strip()
				val = line[i+1:].strip()
				if not key or not val:
					self.okapi.msg("Invalid header '"+line+"' !", 1)
					return None
				hdr[key] = val
			except:
				self.okapi.msg("Invalid header '"+line+"' !", 1)
				return None
		return hdr

	def set(self, hdrs:dict):
		self.txt.clear_text()
		self.add(hdrs)

	def add(self, hdrs:dict):
		for k,v in hdrs.items():
			self.txt.add_text(k + ": " + v + "\n")

	def _on_clear(self):
		self.headers = {}
		self.txt.clear_text()

	def _setup_gui(self):
		self.configure(pady=3, background=TAB_COLOR)
		self.grid_columnconfigure(0, weight=1)
		self.txt = ScrollTextFrame(self, height=5, bg="#333", fg='#eee',
				insertbackground='#e9e9e9')
		self.txt.grid(row=0, column=0, sticky='nswe')
		ToolTip(self.txt, 'SYNTAX: "OPTION: VALUE\\n"')
		self.btnClear = tk.Button(self, text="clear", font=BTN_FONT,
				command=self._on_clear,
				highlightthickness=0)
		self.btnClear.grid(row=0, column=2, sticky='nwe', padx=1)


class RequestUseragentFrame(tk.Frame):
	"""
	Tab where authentication information can be added
	to the request header.
	"""
	def __init__(self, parent, okapi):
		super().__init__(parent)
		self.okapi = okapi
		self.uagents = okapi.user_agents

		self.varUAgent = tk.StringVar(self)
		self.varUAgent.set('Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0')
		self.cbUAgent = ttk.Combobox(self, textvariable=self.varUAgent,
					values=self.uagents, width=40)
		self.cbUAgent.bind("<<ComboboxSelected>>", self.cbUAgent_on_select)
		self.btnReset = tk.Button(self, text="reset", font=BTN_FONT)

		self.setup()

	def setup(self):
		self.configure(pady=3)
		self.grid_columnconfigure(1, weight=1)

		lbl = tk.Label(self, text='User-Agent', font='monospace 8 bold')
		lbl.grid(row=0, column=0)
		self.cbUAgent.grid(row=0, column=1, sticky='we', padx=2)
		self.btnReset.grid(row=0, column=2)


	def set(self, uagent):
		self.varUAgent.set(uagent)

	def get(self) -> str:
		"""
		Returns the useragent string.
		"""
		return self.varUAgent.get()

	def cbUAgent_on_select(self, event):
		pass

class RequestAuthFrame(tk.Frame):
	"""
	Tab where authentication information can be added
	to the request header.

	AuthTypes:
	  Basic
	  Digest
	  Bearer	Creates header "Authentication: Bearer <KEY>"
	  Api-Key	Creates header "X-Api-Key: <KEY>"
	  OAuth 1
	"""
	def __init__(self, parent, okapi):
		super().__init__(parent)
		self.okapi = okapi

		self.grid_columnconfigure(2, weight=1)
		self.varAuthType = tk.StringVar(self)
		self.varAuthType.set("None")

		LeftLabel(self, text="Auth Type", font="Arial 9 bold")\
			.grid(row=0, column=0, sticky='nswe', padx=3)
		self.cbAuthType = ttk.Combobox(self, textvariable=self.varAuthType,
					values=['None', 'Basic', 'Digest', 'Bearer', 'OAuth 1'],
					state='readonly')
		self.cbAuthType.bind("<<ComboboxSelected>>", self.on_select_authtype)
		self.cbAuthType.grid(row=0, column=1, sticky='we', padx=3, pady=10)

		self.frames = {
			'basic' : UserPassFrame(self, okapi),
			'digest' : UserPassFrame(self, okapi)
		}
		self.frame = None

	def set_authentication(self, auth_type, user=None, password=None, token=None):
		# TODO
		pass

	def on_select_authtype(self, e=None):
		if self.frame:
			self.frame.grid_remove()
#			self.sep.grid_remove()

		authType = self.varAuthType.get()

		if authType == "Basic":
			self.frame = self.frames['basic']
			self.frame.eUser.focus_set()
			self.frame.grid(row=2, column=0, sticky='nswe', columnspan=3, pady=4)
		elif authType == "Digest":
			self.frame = self.frames['digest']
			self.frame.grid(row=2, column=0, sticky='nswe', columnspan=3)
		elif authType == "Bearer":
			pass
		elif authType == "OAuth 1":
			pass



class UserPassFrame(tk.Frame):
	def __init__(self, parent, okapi):
		super().__init__(parent)
		self.okapi = okapi
		self.varUser = tk.StringVar(self)
		self.varPass = tk.StringVar(self)
		self.setup()

	def setup(self):
		self.configure(pady=3, padx=3)
		self.grid_columnconfigure(1, weight=1)

		LeftLabel(self, text='User', font='monospace 9')\
			.grid(row=0, column=0, sticky='nswe', padx=3)
		self.eUser = tk.Entry(self, textvariable=self.varUser)
		self.eUser.grid(row=0, column=1, sticky='w', padx=5)

		LeftLabel(self, text='Pass', font='monospace 9')\
			.grid(row=1, column=0, sticky='nswe', padx=3)
		self.ePass = tk.Entry(self, textvariable=self.varPass, show='*')
		self.ePass.grid(row=1, column=1, sticky='w', padx=5)

	def get(self):
		return self.varUser.get(), self.varPass.get()

