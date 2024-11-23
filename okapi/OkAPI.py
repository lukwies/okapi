import os
import sys
import requests
import threading
import time
from os import path

import tkinter as tk
from tkinter import ttk

from okapi.RequestFrame import RequestFrame
from okapi.ApiDoc import ApiDoc
from okapi.DOC import DOC as doc
from okapi.widgets import Tablist
from okapi.codegen import codegen

"""
|-------------------------------|
| Menu				|
|-------------------------------|
| ApiDoc or			| 0
| RequestFrame			|
|				|
|				|
|-------------------------------|
| Message label / Progressbar	| 1
|-------------------------------|
| Footer			| 2
|-------------------------------|
"""
OKAPI_VERSION = "0.1"
OKAPI_RELEASE = "okapi v" + OKAPI_VERSION + " (2024)"

class OkAPI:
	"""
	FILES:
		~/.okapi/uris.txt
		~/.okapi/user_agents.txt
		~/.okapi/apidoc/<api-name>.json
	"""

	def __init__(self, basedir=None):
		if not basedir:
			self.basedir = os.path.join(path.expanduser('~'), '.okapi')
		else:	self.basedir = basedir

		if not path.isdir(self.basedir):
			os.mkdir(self.basedir)
			os.mkdir(os.path.join(self.basedir, "apidoc"))

		self.user_agents_file = path.join(self.basedir, "user_agents.txt")
		self.user_agents = []

		self.uris_file = path.join(self.basedir, "uris.txt")
		self.uris = []

	def run(self):
		"""
		Start okapi
		"""
		self._load_files()
		self._setup_gui()
		self.root.mainloop()


	def _load_files(self):
		"""
		load resource files.
		"""
		def load_file(p):
			try:
				f = open(p, "r")
				a = [l.strip() for l in f.readlines()]
				return [l for l in a if l != ""]
			except Exception as e:
				print(e)
				return []

		self.user_agents = load_file(self.user_agents_file)
		self.uris = load_file(self.uris_file)

	def _setup_gui(self):
		self.root = tk.Tk()
		self.root.geometry('640x400')
		self.root.title(OKAPI_RELEASE)
		self.root.grid_columnconfigure(0, weight=1)
		self.root.grid_rowconfigure(0, weight=1)

		# URL bar (optional)
		self.fRequest = RequestFrame(self)
		self.fRequest.grid(row=0, column=0, sticky='nswe')

		# Mainframe (apidoc or request/response)
		self.fApiDoc = ApiDoc(self.root, self.basedir)
		self.fApiDoc.grid(row=0, column=0, sticky='nswe')

		# Label for messages, warnings and errors
		self.lblMsg = tk.Label(self.root, font='monospace 9',
				justify='left', anchor='w', bg='#ddd')
		# Footer
		self.footer = tk.Frame(self.root, background='#333', height=30)
		self.footer.grid(row=2, column=0, sticky='nsew')
		self.footer.grid_columnconfigure(0, weight=1)
		lbl = tk.Label(self.footer, text="Path: "+self.basedir,
				justify='left', anchor='w',
				font="'monospace 8", bg='#333', fg='#bbb')
		lbl.grid(row=0, column=0, sticky='nswe', padx=2)
		lbl = tk.Label(self.footer, text=OKAPI_RELEASE, font="monospace 8",
				bg='#333', fg='#bbb')
		lbl.grid(row=0, column=1, sticky='nswe', padx=5)

		# Create menu
		menu = self._make_menu()
		self.root.configure(menu=menu)

		#self.root.bind('<Control-s>', self.on_send)
		#self.root.bind('<Control-Tab>', lambda e: self._open_view(open_other=True))

		# TODO
		self.fApiDoc.on_open_doc()


	def msg(self, text, typ=0, clear_after=5):
		"""
		Add a message.
		"""
		def clear_msg():
			if self.lblMsg != None:
				self.lblMsg.grid_remove()
		fgs = ["#eaeaea", "#e00", "#0ee"]
		self.lblMsg.configure(text=text, fg=fgs[typ%3])
		self.lblMsg.grid(row=1, column=0, sticky='nswe', padx=2)
		if clear_after > 0:
			self.lblMsg.after(clear_after*1000, clear_msg)

	def _exec_apidoc_command(self, cmd="new"):
		if cmd == "new":
			self.fApiDoc.on_new_doc()
		elif cmd == "open":
			self.fApiDoc.on_open_doc()
		elif cmd == "delete":
			self.fApiDoc.on_delete_doc()
		elif cmd == "save":
			self.fApiDoc.on_save_doc()
		self.vMenuReqOpen.set(0)
		self._open_request_view()

	def _open_request_view(self):
		# Show/Hide request frame
		if self.vMenuReqOpen.get() == 1:
			self.fRequest.clear()
			self.fRequest.tkraise()
		else:	self.fApiDoc.tkraise()


	def _make_menu(self):
		menu = tk.Menu(self.root, font='Verdana 10')
		menu.configure(background='#303030', foreground='#fefefe')

		# File Menu
		mFile = tk.Menu(menu, tearoff=False)
		mFile.add_command(label='New', command=lambda:self._exec_apidoc_command("new"))
		mFile.add_command(label='Open', command=lambda:self._exec_apidoc_command("open"))
		mFile.add_command(label='Save', command=lambda:self._exec_apidoc_command("save"))
		mFile.add_command(label='Delete', command=lambda:self._exec_apidoc_command("delete"))
		mFile.add_separator()
		mFile.add_command(label='Exit',	command=self.root.destroy)
		mFile.entryconfig("Delete", foreground='#e00')
		menu.add_cascade(label='File', menu=mFile)
		self.mFile = mFile

		# Export Menu
		mExp = tk.Menu(menu, tearoff=False)
		menu.add_cascade(label='Export', menu=mExp)
		# Export doc (submenu)
		mExportDoc = tk.Menu(menu, tearoff=False)
		mExportDoc.add_command(label='Html')
		mExportDoc.add_command(label='Textfile',
			command=lambda:self.fApiDoc.on_export(codegen.CodeGenType.TEXT))
		mExportDoc.add_command(label='Markdown')
		mExp.add_cascade(label='Documentation', menu=mExportDoc)
		# Export server code (submenu)
		mExpServer = tk.Menu(menu, tearoff=False)
		mExpServer.add_command(label='ESP server',
			command=lambda:self.fApiDoc.on_export(codegen.CodeGenType.ESP32_SERVER))
		mExpServer.add_command(label='Flask')
		mExp.add_cascade(label='Server Code', menu=mExpServer)
		# Export client code (submenu)
		mExpClient = tk.Menu(menu, tearoff=False)
		mExpClient.add_command(label='Curl script')
		mExpClient.add_command(label='Python client')
		mExpClient.add_command(label='ESP client',
			command=lambda:self.fApiDoc.on_export(codegen.CodeGenType.ESP32_CLIENT))
		mExp.add_cascade(label='Client Code', menu=mExpClient)

#		mExp.entryconfig("Documentation", state=tk.DISABLED)
#		mExp.entryconfig("Server Code", state=tk.DISABLED)
#		mExp.entryconfig("Client Code", state=tk.DISABLED)
#		mFile.entryconfig("Export Doc", state="disabled")
#		mFile.entryconfig("Export Code", state="disabled")

		# View
		mView = tk.Menu(menu, tearoff=False)
		self.vMenuReqOpen = tk.IntVar(self.root)
		self.vMenuReqOpen.set(0)
		mView.add_checkbutton(label="Request", onvalue=1,
				offvalue=0, variable=self.vMenuReqOpen,
				command=self._open_request_view)
		menu.add_cascade(label='View', menu=mView)
		return menu
