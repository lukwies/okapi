import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesno
import json

import DOC as doc
from ModelEditWindow import ModelEditWindow
from widgets import ScrollFrame
from widgets import ButtonLabel
from widgets import ButtonFrame
from widgets import LeftLabel
from widgets import ScrollTextFrame
from widgets import PopupMenu

# Used fonts
A8b = "Arial 8 bold"
A9b = "Arial 9 bold"

class ModelsFrame(tk.Frame):
	"""
	Frame with a scrollable list of data models.
	"""
	def __init__(self, apidoc):
		super().__init__(apidoc)
		self.A = apidoc
		self.scroll = None
		self._setup_gui()

	def load_from_DOC(self):
		if self.scroll:
			self.scroll.grid_remove()
		self.scroll = ScrollFrame(self)

		if not doc.DOC['models']:
			tk.Label(self, text="No models")\
				.grid(row=1, column=0, sticky='nswe')
		else:
			self.scroll.interior.grid_columnconfigure(0, weight=1)
			self.scroll.grid(row=1, column=0, sticky='nswe', pady=2, padx=2)

			y=0
			for m in doc.DOC['models'].keys():
				ModelListItem(self.scroll.interior, self, m)\
					.grid(row=y, column=0, sticky='nswe', pady=(4,1), padx=1)
				y += 1

	def save_to_DOC(self):
		pass

	def edit_model(self, model_name=''):
		win = ModelEditWindow(self, model_name)
		win.attributes('-topmost', 'true')

	def _setup_gui(self):
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)
		btns = {" Add ":self.edit_model}
		ButtonFrame(self, btns, style='label', bg='#ddd', border_fg='#bababa',
				btn_fg='#444', btn_fg_hover='#777', btn_font="Arial 8 bold",
				btn_bg='#e3e3e3', btn_bg_hover='#efefef',
				btn_border_fg='#aaa', btn_border_hover_fg='#a0a0a0',
				btn_pady=3, btn_padx=3)\
			.grid(row=0, column=0, sticky='senw')



class ModelListItem(tk.Frame):
	"""
	<MODEL>            (edit)[x][↓]
	...
	"""
	BG = '#eee'

	def __init__(self, scrlframe, parent, model_name):
		super().__init__(scrlframe, background=self.BG)
		self.scrlframe = scrlframe
		self.parent = parent
		self.model_name = model_name
		self.mod_dict = doc.DOC['models'][model_name]
		self._setup_gui()
		self._bind_events()

	def _setup_gui(self):
		self.grid_columnconfigure(0, weight=1)

		# Topframe with modelname and click-labels
		self.tf = tk.Frame(self, background=self.BG)
		self.tf.grid_columnconfigure(3, weight=1)
		self.tf.grid(row=0, column=0, sticky='nswe')

		# Model name
		self.lblName = LeftLabel(self.tf, text=self.model_name,
				font='monospace 11', bg=self.BG)
		self.lblName.grid(row=0, column=0, sticky='nswe', padx=(5,0))

		# Expand button
		self.btnExpand = ButtonLabel(self.tf, text="[↓]",
				on_click=self.expand, bg=self.BG,
				hover_bg=self.BG, font='Arial 8')
		self.btnExpand.grid(row=0, column=6, padx=2)

		# Expand frame
		self.expFrame = ExpandFrame(self, self.mod_dict, self.BG)

	def _delete_model(self):
		yes = askyesno(title='Delete model?',
				message='Do you really want to delete model ' \
						+ self.model_name + '?')
		if yes:
			del doc.DOC['models'][self.model_name]
			print(". deleted model: " + self.model_name)
			self.parent.A.msg("Deleted '"+self.model_name+"'")
			self.parent.load_from_DOC()

	def expand(self, ev=None):
		self.btnExpand['text'] = '[↑]'
		self.btnExpand.on_click = self.shrink
		self.lblName['text'] = self.model_name + " {"
		self.expFrame.grid(row=1, column=0, sticky='nswe')

	def shrink(self):
		self.btnExpand['text'] = '[↓]'
		self.btnExpand.on_click = self.expand
		self.lblName['text'] = self.model_name
		self.expFrame.grid_remove()

	def _bind_events(self):
		# Bind events
		self.bind("<Enter>", lambda e: self._set_border(True))
		self.bind("<Leave>", lambda e: self._set_border(False))
		menu_items = {
			"Edit" : lambda:self.parent.edit_model(self.model_name),
			"Delete" : self._delete_model
		}
		menu = PopupMenu(self, menu_items, (self.tf, self.lblName))
		menu.bind("<Enter>", lambda e: self._set_border(True))

	def _set_border(self, enable=True):
		# Set border around listitem
		if enable:
			self.configure(highlightthickness=1,
				highlightbackground="#888")
		else:	self.configure(highlightthickness=0)

class ExpandFrame(tk.Frame):
	"""
	Expanded model frame.
	"""
	def __init__(self, parent, mod_dict, bg):
		super().__init__(parent, background=bg)
		self.parent = parent
		self.mod_dict = mod_dict
		self.params = mod_dict['attributes']
		self.setup(bg)

	def setup(self, bg):
		"""
		"""
		self.grid_columnconfigure(3, weight=1)

		# Attributes
		y= 0
		for name,attr in self.mod_dict['attributes'].items():

			# Print red '*' if attribute is mandatory
			if attr['required']:
				tk.Label(self, text='*', font='Arial 9 bold',
					fg='#e00', bg=bg)\
				.grid(row=y, column=0, sticky='ne', padx=(20,0))

			# Attribute name
			LeftLabel(self, text=name, bg=bg, font='Arial 9 bold', fg='#333')\
				.grid(row=y, column=1, sticky='nwe', padx=(0,20))

			# datatype
			s = attr['type']
			if 'is_array' in attr and attr['is_array']:
				s = "array[" + s + "]"
			LeftLabel(self, text=s, bg=bg, font='Arial 9', fg='#333')\
				.grid(row=y, column=2, sticky='nwe', padx=3)

			if ('info' in attr and attr['info']) or \
					('values' in attr and attr['values']):
				ModelAttrInfoFrame(self, name, attr, bg)\
					.grid(row=y, column=3, padx=5, sticky='w')
			y += 1

		LeftLabel(self, text="}", font='monospace 11', bg=bg)\
			.grid(row=y, column=0, sticky='nswe', padx=5)
		y += 1

		# model Info
		if 'info' in self.mod_dict and self.mod_dict['info']:
			LeftLabel(self, text=self.mod_dict['info'],
				bg=bg, font='Arial 9')\
				.grid(row=y, column=0, sticky='nswe', columnspan=3,
					pady=5, padx=3)



class ModelAttrInfoFrame(tk.Frame):
	"""
	Frame holding model attribute informations.
	"""
	def __init__(self, parent, name, attr_dict, bg):
		super().__init__(parent, background=bg)
		self.expanded = False
		self._setup_gui(name, attr_dict, bg)

	def _setup_gui(self, name, attr, bg):
		self.grid_columnconfigure(0, weight=1)

		self.btnExp = ButtonLabel(self, text="[↓]",
				on_click=self._expand,
				font="Arial 8",	hover_font="Arial 8 bold",
				bg=bg, hover_bg=bg)
		self.btnExp.grid(row=0, column=0, sticky='nsw', pady=(0, 5))

		self.exFrame = tk.Frame(self, background=bg)
		self.exFrame.grid_columnconfigure(0, weight=1)

		if 'info' in attr and attr['info']:
			LeftLabel(self.exFrame, text=attr['info'],
				font='Arial 9', fg='#555', bg=bg)\
				.grid(row=0, column=0, sticky='nswe')
		if 'values' in attr and attr['values']:
			LeftLabel(self.exFrame, text="Allowed Values", font='Arial 9 bold',
					fg='#333', bg=bg)\
				.grid(row=1, column=0, sticky='nswe', pady=(5, 0))
			for i,v in enumerate(attr['values']):
				LeftLabel(self.exFrame, text="- "+v, font='Arial 8', fg='#222', bg=bg)\
					.grid(row=i+2, column=0, sticky='nswe',
						padx=5, ipadx=2)

	def _expand(self):
		self.expanded = not self.expanded
		if self.expanded:
			self.btnExp['text'] = '[↑]'
			self.exFrame.grid(row=1, column=0, sticky='nswe')
		else:
			self.btnExp['text'] = '[↓]'
			self.exFrame.grid_remove()
