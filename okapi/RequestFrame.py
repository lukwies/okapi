import tkinter as tk
from tkinter import ttk

from widgets import ToolTip
from ResponseFrame import ResponseFrame
from RequestOptionsFrame import RequestOptionsFrame

"""
|---------------------------------------|
| [ GET [v]][                   ][send] |
|---------------------------------------|
| RequestOptionsFrame			|
|---------------------------------------|
| ResponseFrame				|
|					|
|					|
|					|
|					|
|---------------------------------------|

"""

class RequestFrame(tk.Frame):
	"""
	This frame holds the basic request settings like HTTP-type, URI, port
	and a button to send the request.
	"""
	METHODS = ['GET', 'POST', 'HEAD', 'PUT', 'DELETE']

	def __init__(self, okapi):
		super().__init__(okapi.root,
			highlightthickness=1,
			highlightbackground='#999') #, background='#a0a0a0')
		self.O = okapi
		self.uris = okapi.uris
		self._setup_gui()

	def clear(self):
		self.vMethod.set("GET")
		self.vURI.set("")
		self.fResp.clear()

	def _setup_gui(self):
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(2, weight=1)

		self.fUrlbar = self._make_url_bar()
		self.fUrlbar.grid(row=0, column=0, sticky='nwse')

		self.fOpts = RequestOptionsFrame(self, self.O)
		self.fOpts.grid(row=1, column=0, sticky='nwse')

		self.fResp = ResponseFrame(self, self.O.msg)
		self.fResp.grid(row=2, column=0, sticky='nwse')

	def _make_url_bar(self):
		f = tk.Frame(self)
		f.configure(pady=3, padx=3)
		f.grid_columnconfigure(1, weight=1)
		# Method
		self.vMethod = tk.StringVar(self)
		self.vMethod.set("GET")
		self.cbGET = ttk.Combobox(f, values=self.METHODS,
				state='readonly',
				textvariable=self.vMethod, width=7)
		#self.cbGET.bind("<<ComboboxSelected>>", self._cbGET_on_select)
		self.cbGET.grid(row=0, column=0, sticky='nswe')
		ToolTip(self.cbGET, "Choose HTTP method")
		# Url
		self.vURI = tk.StringVar(self)
		self.cbURI = ttk.Combobox(f, values=self.uris,
				textvariable=self.vURI)
		self.cbURI.bind('<Return>', self._cbURI_on_return)
		#self.cbURI.bind("<<ComboboxSelected>>", self._cbURI_on_select)
		self.cbURI.grid(row=0, column=1, sticky='nswe')
		ToolTip(self.cbURI, "Choose or enter URI")
		# Send button
		self.btnSend = tk.Button(f, text='SEND',
				background='#80cc80',
				command=self._on_send)
		self.btnSend.grid(row=0, column=3, sticky='we', ipady=0, pady=0)
		ToolTip(self.btnSend, "Send request\n[CTRL+S]")

		return f

	def _cbURI_on_return(self, event):
		value = self.vURI.get()

		if value and value not in self.uris:
			self.uris.insert(0, value)
			self.cbURI.configure(values=self.uris)

	def _on_send(self, ev=None):
		uri = self.vURI.get().strip()
		if not uri:
			self.O.msg("Missing url !", 1)
			return

		if not uri.startswith("http://") and \
		   not uri.startswith("https://"):
			uri = "http://" + uri

		body,hdrs,auth = self.fOpts.get()

		# TODO: body, header, auth
		self.fResp.request(self.vMethod.get(), uri, body,
					hdrs, auth)





