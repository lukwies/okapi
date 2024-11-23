import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

import DOC as doc
from widgets import ButtonLabel
from widgets import ButtonFrame
from widgets import LeftLabel
from widgets import ScrollFrame

from codegen import codegen


class ExportWindow(tk.Toplevel):
	"""
	Window to let user select all the endpoints used to
	export client/server code.
	"""
	def __init__(self, parent, doc, gentype:codegen.CodeGenType):
		super().__init__(parent)

		self.parent  = parent
		self.doc     = doc
		self.opts    = codegen.CodeGenOptions(gentype)
		self.createpath = ""
		self._cancel = True

	def show(self):
		self._setup_gui()
		self.parent.wait_window(self)
		return None if self._cancel else self.opts

	def _setup_gui(self):
		self.geometry('340x300')
		self.title("Export {}".format(self.opts.type.value))
		self.grid_rowconfigure(7, weight=1)
		self.grid_columnconfigure(0, weight=1)
		self.cbs = []

		# Select export path
		self.vPath = tk.StringVar(self)
		LeftLabel(self, text="Directory path", bg='#c5c5c5', fg='#444')\
			.grid(row=0, column=0, sticky='nswe')
		f = tk.Frame(self)
		f.grid_columnconfigure(1, weight=1)
		f.grid(row=1, column=0, sticky='nswe')
		self.ePath = tk.Entry(f, highlightthickness=0, textvariable=self.vPath)
		self.ePath.grid(row=0, column=1, sticky='we', padx=(10,0), pady=4)
		ButtonLabel(f, text=" Browse ", font='Arial 11',
				hover_font='Arial 11', #border_fg='#444',
				relief="raised", on_click=self._browse)\
			.grid(row=0, column=2, sticky='we', padx=(2,3), pady=(4,3))

		# Export options
		self.vComments = tk.IntVar()
		self.vComments.set(1)
		LeftLabel(self, text="Options", bg='#c5c5c5', fg='#444')\
			.grid(row=2, column=0, sticky='nswe', pady=(3,0))
		cb = tk.Checkbutton(self, variable=self.vComments,
			text="Create comments", onvalue=1,
			justify='left', anchor='w', fg='#333',
			offvalue=0)
		cb.grid(row=3, column=0, sticky='nswe')

		# Scrollframe with checkbuttons to select which endpoints
		# to export.
		LeftLabel(self, text="Endpoints", bg='#c5c5c5', fg='#444')\
			.grid(row=6, column=0, sticky='nswe', pady=(3,0))
		scroll = ScrollFrame(self)
		scroll.interior.grid_columnconfigure(0, weight=1)
		scroll.grid(row=7, column=0, sticky='nswe')
		y = 1
		for method,x in self.doc['endpoints'].items():
			for uri in x.keys():
				v = tk.IntVar()
				v.set(1)
				cb = tk.Checkbutton(scroll.interior, variable=v,
					text=method+" "+uri, onvalue=1,
					justify='left', anchor='w', fg='#333',
					offvalue=0)
				cb.grid(row=y, column=0, sticky='nswe')
				self.cbs.append((v, method, uri))
				y += 1

		# Buttons (cancel, export)
		btns = {
			"Cancel" : self.destroy,
			"Export" : self._on_export
		}
		ButtonFrame(self, btns, bg='#999')\
			.grid(row=10, column=0, sticky='nswe')

	def _on_export(self):
		# Called after "Export" button clicked
		p = self.vPath.get()
		if not p:
			messagebox.showwarning("Warning", "Missing Path!",
				parent=self)
			return
		elif not os.path.isdir(p):
			messagebox.showwarning("Warning",
				"No such directory '"+p+"'!",
				parent=self)
			return

		filename = codegen.get_filename(doc.DOC, self.opts.type)
		self.createpath = os.path.join(p, filename)
		if os.path.exists(self.createpath):
			if not messagebox.askyesno("Warning",\
				"Path already exists, want to overwrite it?",\
				parent=self):
				return

		self.opts.comments = self.vComments.get()
		self.opts.path     = self.vPath.get()
		self.opts.filename = filename

		for v,method,uri in self.cbs:
			if v.get():
				self.opts.add_endpoint(method, uri)
		self._cancel = False
		self.destroy()

	def _browse(self):
		# Open file or dirbrowser
		path = filedialog.askdirectory(parent=self)
		if path: self.vPath.set(path)
		print("Path:", self.vPath.get())
