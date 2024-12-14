import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesno
from os.path import join as path_join
from os import listdir as os_listdir
from os import unlink as os_unlink
import json

import DOC as doc

from EndpointsFrame import EndpointsFrame
from EndpointRequest import EndpointRequestFrame
from ModelsFrame import ModelsFrame
from Frames import *
from widgets import ButtonLabel
from widgets import ButtonFrame
from widgets import LeftLabel
from widgets import Tablist
from widgets import ScrollFrame
from ResponseFrame import ResponseFrame
from ExportWindow import ExportWindow

from codegen import codegen

"""
Frame to create/view API documentations.
"""
class ApiDoc(tk.Frame):
	"""
	 0	    1
	|----------|----------------------------|
	|	   | Tabs			| 0
	|	   |----------------------------|
	| Endpoint | Mainframe or		| 1
	| Request  | EndpointResponseFrame	|
	|          |				|
	|          |				|
	|          |____________________________|
	|          | msgLabel/Progressbar	| 2
	|---------------------------------------|
	"""
	def __init__(self, parent, basedir):
		"""
		Create Apidoc instance.
		Args:
		  parent             Parent widget
		  basedir            Base config directory
		"""
		super().__init__(parent)
		self.basedir = basedir
		doc.DOC_new()
		self._setup_gui()


	def _setup_gui(self):
		self.ep_req_open = False	# Endpoint request open?

		self.grid_columnconfigure(1, weight=1)
		self.grid_rowconfigure(1, weight=1)

		# Tablist
		btns = {
			'info' : (' Info ', lambda:self.open_tab('info')),
			'models' : (' Models ', lambda:self.open_tab('models')),
			'endpoints' : (' Endpoints ', lambda:self.open_tab('endpoints')),
			'headers' : (' Header ', lambda:self.open_tab('headers')),
			'auth' : (' Authenticate ', lambda:self.open_tab('auth'))
		}
		self.tabs = Tablist(self, btns, bg_hover='#d8d8d8', bg='#bbb')

		# All mainframes
		self.frames = {
			'welcome'   : WelcomeFrame(self),
			'info'      : InfoEditFrame(self),
			'models'    : ModelsFrame(self),
			'endpoints' : EndpointsFrame(self),
			'headers'   : HeadersEditFrame(self),
			'auth'      : AuthEditFrame(self)
		}
		self.current_frame = 'welcome'
		for frame in self.frames.values():
			frame.grid(row=1, column=1, sticky='nswe')

		# Frame for sending endpoint request
		self.epRequestFrame = None
		self.responseFrame = None

		# Message label
		self.lblMsg = LeftLabel(self, font='monospace 9', bg='#555')

		self.open_tab('welcome')


	def reload_gui(self):
		for frame in self.frames.values():
			frame.load_from_DOC()

	def on_new_doc(self):
		"""
		Called when new api doc shall be created.
		"""
		if self.epRequestFrame:
			self.close_endpoint_request_frame()
		if doc.DOC_has_changed():
			if askyesno("File has changed",
				"Do you want to save before continue?"):
				self.on_save_doc()
		doc.DOC_new()
		self.reload_gui()
		self.tabs.block_all(False)
		self.open_tab('info')
		self.msg("Created new api documentation")

	def on_open_doc(self):
		"""
		Load documentation from file.
		"""
		if doc.DOC_has_changed():
			if askyesno("File has changed",
				"Do you want to save before continue?"):
				self.on_save_doc()
		ow = OpenApiDocWindow(self)

	def on_save_doc(self):
		"""
		Store apidoc at ~/.okapi/apidoc/<name>.json
		"""
		for frame in self.frames.values():
			frame.save_to_DOC()

		if not doc.DOC['name']:
			self.msg("Please set an API name!", 1)
			return
		elif not doc.DOC['version']:
			self.msg("Please set an API version!", 1)
			return
		try:
			p = doc.DOC_save_json(self.basedir)
			self.msg("Stored apidoc at " + p)
		except Exception as e:
			self.msg("Failed to save apidoc, "+str(e), 1)

	def on_delete_doc(self):
		if not doc.DOC['name']:
			return
		yes = askyesno("Delete Apidoc ?",
			"Do you really want to delete all documentation\n"\
			"for API '"+doc.DOC['name']+"'?\n"\
			"This cannot be undone!")
		if not yes: return
		os_unlink(doc.DOC_get_storage_path(self.basedir))
		doc.DOC_new()
		self.open_tab('welcome')

	def on_export(self, gentype:codegen.CodeGenType):
		"""
		Export apidoc as given type.
		"""
		self.msg("Exporting " + gentype.value + " ...")
		w = ExportWindow(self, doc.DOC, gentype)
		opts = w.show()

		if opts:
			if codegen.gen_code(doc.DOC, opts):
				self.msg("Created " + gentype.value \
					+ " at " + w.createpath, 0)
			else:	self.msg("Failed to export!", 1)
		else:	self.msg("Export cancelled", 1)


	def open_tab(self, title):
		"""
		Open frame with given title in mainframe.
		"""
		if title == 'welcome':
			self.tabs.grid_remove()
		elif self.current_frame == 'welcome':
			self.tabs.grid(row=0, column=1, sticky='nswe')

		self.frames[title].tkraise()
		if title != 'welcome':
			self.tabs.enable(title)

			if title in ('endpoints', 'models'):
				self.frames[title].scroll.bind_scroll_events()

		self.current_frame = title

	def open_endpoint_request_frame(self, method, uri):
		"""
		Open EndpointRequestFrame and let user enter parameter
		values and send a request.
		Grid: row=0, column=0
		"""
		if not doc.DOC['address']:
			self.msg("Please set an Api address first!", 1)
		elif not self.epRequestFrame:
			self.responseFrame = ResponseFrame(self, self.msg)
			self.epRequestFrame = EndpointRequestFrame(self, method, uri, self.responseFrame)
			self.epRequestFrame.grid(row=0, column=0, rowspan=2, sticky='nswe')
			self.responseFrame.grid(row=0, column=1, rowspan=2, sticky='nswe')
		else:	self.epRequestFrame.set_endpoint(method, uri)

	def close_endpoint_request_frame(self):
		"""
		Close EndpointRequestFrame.
		"""
		if self.epRequestFrame:
			self.epRequestFrame.grid_remove()
			self.responseFrame.grid_remove()
			self.epRequestFrame = None
			self.frames['endpoints'].scroll.bind_scroll_events()

			self.tabs.grid(row=0, column=1, sticky='nswe')
			self.open_tab(self.current_frame)
			#self.frames['models'].scroll.bind_scroll_events()

	def msg(self, text, typ=0, clear_after=5):
		"""
		Set dissappearing message.
		0=Info, 1=Error, 2=Warning.
		"""
		def clear_msg():
			if self.lblMsg != None:
				self.lblMsg.grid_remove()
		fgs = ["#eaeaea", "#e00", "#0ee"]

		self.lblMsg.configure(text=text, fg=fgs[typ%3])
		self.lblMsg.grid(row=2, column=0, sticky='nswe', ipadx=2,
				columnspan=2)

		if clear_after > 0:
			self.lblMsg.after(clear_after*1000, clear_msg)



class OpenApiDocWindow(tk.Toplevel):
	"""
	External window to select api to open.
	"""
	def __init__(self, parent):
		super().__init__()
		self.parent = parent
		self.api_names = self._get_api_names()

		if not self.api_names:
			self.parent.msg("No apidoc's found !", 1)
			self.destroy()
		else:	self._setup_gui()

	def _setup_gui(self):
		self.title("Open API documentation")
		self.geometry("300x100")
		self.grid_columnconfigure(1, weight=1)
		self.grid_rowconfigure(2, weight=1)
		self.bind("<Return>", self._open_api)

		LeftLabel(self, text='Api name', font='Arial 11')\
			.grid(row=0, column=0, sticky='nswe', padx=3, pady=5)

		self.vName = tk.StringVar(self)
		self.vName.set(self.api_names[0])
		self.cbNames = ttk.Combobox(self, values=self.api_names,
					state='readonly', textvariable=self.vName)
		self.cbNames.grid(row=0, column=1, sticky='we', pady=5, padx=4)

		btns = {
			'Cancel' : self.destroy,
			'Open' : self._open_api
		}
		ButtonFrame(self, btns, bg='#aaa')\
			.grid(row=3, column=0, sticky='nswe', columnspan=2)


	def _open_api(self, ev=None):
		# Open apidoc
		api_name = self.vName.get()
		if api_name:
			self.destroy()
			p = self._api_name_to_path(api_name)
			if not doc.DOC_load(p):
				self.parent.msg("Failed to load apidoc "+p+" !",1)
			else:
				if self.parent.epRequestFrame:
					self.parent.close_endpoint_request_frame()

				self.parent.msg("Loaded apidoc "+p)
				self.parent.tabs.block_all(False)
				self.parent.reload_gui()
				self.parent.open_tab('info')

	def _get_api_names(self):
		# Get list of all stored apidoc names.
		names = []
		p = path_join(self.parent.basedir, "apidoc")
		for file in os_listdir(p):
			filepath = path_join(p, file)
			try:
				f = open(filepath, "r")
				doc = json.load(f)
				names.append(doc['name'])
				f.close()
			except Exception as e:
				print("! Failed to read apiname from '"+filepath+"'")
				continue

		return sorted(names)


	def _api_name_to_path(self, api_name):
		# Get path to file where api with given name is stored
		name = api_name.lower().replace(' ', '_')
		return path_join(path_join(self.parent.basedir, 'apidoc'),
				name + '.json')
