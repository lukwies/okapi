import tkinter as tk
from tkinter import ttk
import re
#from widgets import *


import DOC as doc
from widgets import LeftLabel
from widgets import ScrollTextFrame
from widgets import ToolTip
from widgets import ButtonFrame
from style import EntryLabel
from utils import parse_key_value_text_to_dict

A8b="Arial 8 bold"
A10b="Arial 10 bold"

API_WELCOME_TEXT = \
"""To create a new documentation click File->new in the menu,
click File->open to load an existing api documentation.
"""


class WelcomeFrame(tk.Frame):
	def __init__(self, apidoc, *args, **kwargs):
		super().__init__(apidoc, *args, **kwargs)

		self.grid_columnconfigure(0, weight=1)
		LeftLabel(self, text="Welcome to okapi !",
				font='Arial 10 bold')\
			.grid(row=0, column=0, sticky='nswe',
				padx=5, pady=(5,0))
		LeftLabel(self, text=API_WELCOME_TEXT, font='Arial 10')\
			.grid(row=1, column=0, sticky='nswe',
				padx=5, pady=5)



	def load_from_DOC(self):
		pass
	def save_to_DOC(self):
		pass

class InfoEditFrame(tk.Frame):
	"""
	Frame for entering Api name and description.
	"""
	def __init__(self, apidoc, *args, **kwargs):
		super().__init__(apidoc, *args, **kwargs)
		self.A        = apidoc
		self.vName    = tk.StringVar(self)
		self.vVersion = tk.StringVar(self)
		self.vAddr    = tk.StringVar(self)
		self.txtInfo  = ScrollTextFrame(self)
		self._setup_gui()
		self.load_from_DOC()

	def load_from_DOC(self):
		self.vName.set(doc.DOC['name'])
		if 'info' in doc.DOC:
			self.txtInfo.set_text(doc.DOC['info'])
		if 'version' in doc.DOC:
			self.vVersion.set(doc.DOC['version'])
		if 'address' in doc.DOC:
			self.vAddr.set(doc.DOC['address'])

		state = 'readonly' if doc.DOC['name'] else 'normal'
		self.eName.configure(state=state)
		#self.eVers.configure(state=state)

	def save_to_DOC(self):
		doc.DOC['name'] = self.vName.get()
		doc.DOC['version'] = self.vVersion.get()
		doc.DOC['info'] = self.txtInfo.get_text()
		doc.DOC['address'] = self.vAddr.get()

	def _setup_gui(self):
		self.grid_columnconfigure(2, weight=1)
		self.grid_rowconfigure(4, weight=1)

		# Api Name (r=1)
		EntryLabel(self, "Api name").do_grid(1, 0, pady=(5,0))
		self.eName = tk.Entry(self, textvariable=self.vName, width=20)
		self.eName.grid(row=1, column=1, sticky='we', pady=(5,0), padx=2)
		self.eName.bind("<FocusOut>", lambda e:self.save_to_DOC())
		self.eName.bind("<Return>", lambda e:self.save_to_DOC, add='+')

		# Api version (r=2)
		EntryLabel(self, "Version").do_grid(2, 0, pady=(5,0))
		self.eVers = tk.Entry(self, textvariable=self.vVersion, width=20)
		self.eVers.grid(row=2, column=1, sticky='we', padx=2)
		self.eVers.bind("<FocusOut>", self._on_set_version)
#		self.eVers.bind("<Return>", self._on_set_version, add='+')

		# Api Address (r=3)
		EntryLabel(self, "Address").do_grid(3, 0)
		self.eAddr = tk.Entry(self, textvariable=self.vAddr)
		self.eAddr.grid(row=3, column=1, sticky='we',
				pady=(0,1), padx=2, columnspan=2)
		self.eAddr.bind("<FocusOut>", self._on_set_address)
		self.eAddr.bind("<Return>", self._on_set_address, add='+')

		# Description (r=4)
		EntryLabel(self, "Description").do_grid(4, 0, sticky='nwe', pady=(4,0))
		self.txtInfo.grid(row=4, column=1, sticky='nswe',
				columnspan=2, padx=3, pady=(0,3))

	def _on_set_address(self, ev=None):
		# Called if address changed
		a = self.vAddr.get()
		if not a: return
		if a[:7] not in ('http://', 'https:/'):
			a = 'http://' + a
		if a[-1] == '/':
			a = a.rstrip('/')
		self.vAddr.set(a)
		doc.DOC['address'] = self.vAddr.get()

	def _on_set_version(self, ev=None):
		# Called if version changed
		v = self.vVersion.get()
		if not v: return
		pat = r"(?:\d{1,4}\.?){1,3}[a-z]?"
		if not re.findall(pat, v):
			self.A.msg("Invalid version string", 1)
			self.vVersion.set("")
		else:	doc.DOC['version'] = v

class HeadersEditFrame(tk.Frame):
	"""
	—————————————————————————————————————————————
	Key   [______________]
	Value [______________]
	—————————————————————————————————————————————
	 Key : Value
	 Key : Value
	 Key : Value
	"""
	def __init__(self, apidoc):
		super().__init__(apidoc)
		self.A = apidoc
		self._setup_gui()

	def load_from_DOC(self):
		self.txt.clear_text()
		for k,v in doc.DOC['headers'].items():
			self.txt.add_text("{}: {}\n".format(k,v))

	def save_to_DOC(self):
		hdrs = parse_key_value_text_to_dict(self.txt.get_text())
		if not hdrs:
			self.A.msg("Header has invalid format !", 1)
			return
		doc.DOC['headers'] = hdrs

	def _setup_gui(self):
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)

		self.txt = ScrollTextFrame(self)
		self.txt.grid(row=0, column=0, sticky='nswe', pady=(3,0), padx=2)
		ToolTip(self.txt, "Add headers for this Api.\nSyntax: 'OPTION: VALUE\\n'")

		tk.Button(self, text="clear")\
			.grid(row=0, column=1, sticky='nwe', pady=2)


class AuthEditFrame(tk.Frame):
	def __init__(self, apidoc):
		super().__init__(apidoc)
		self._setup_gui()

	def load_from_DOC(self):
		pass
	def save_to_DOC(self):
		pass

	def _setup_gui(self):
		LeftLabel(self, text="Auth Type", font='Arial 9')\
			.grid(row=0, column=0, sticky='nswe', padx=5, pady=5)
		self.box = ttk.Combobox(self)\
			.grid(row=0, column=1, sticky='nswe', pady=5)
