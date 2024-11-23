import tkinter as tk
from tkinter import ttk
import json
#from tkinter.messagebox import askyesno

from widgets import ButtonLabel
from widgets import LeftLabel
from widgets import ScrollTextFrame
from widgets import ButtonFrame
from widgets import ScrollFrame
from widgets import ToolTip
from widgets import Tablist

from style import EntryLabel
from style import SmallTableHeader

import DOC as doc

"""
A toplevel window to create/edit a model.
"""

# Used fonts
A8b = "Arial 8 bold"
A9b = "Arial 9 bold"
A9  = "Arial 9"

###
### Standalone window to edit an api model and its attributes.
###

class ModelEditWindow(tk.Toplevel):
	"""
	A toplevel window, spawned on model adding / editing.
	"""
	def __init__(self, parent, model_name=''):
		super().__init__()
		self.parent = parent
		self.A = parent.A
		self.model_name = ''
		self.mod_dict = doc.new_model()
		self.edit_mode = False

		if model_name and model_name in doc.DOC['models']:
			self.model_name = model_name
			self.mod_dict = doc.DOC['models'][model_name]
			self.edit_mode = True
		self._setup_gui()

	def _setup_gui(self):
		self.geometry('480x300')
		self.title("Api Model")

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)


		# Main frames
		self.frames = {
			'info' : ModelEditFrame(self),
			'attr' : AttributeListFrame(self)
		}

		# Tablist
		tabs = {
			'info' : (' Info ', lambda:self._open_tab('info')),
			'attr' : (' Attributes', lambda:self._open_tab('attr'))
		}
		self.tablist = Tablist(self, tabs,
				bg_hover='#ddd', bg='#bbb',
				fg_hover='#222', fg='#111')
		self.tablist.grid(row=0, column=0, sticky='nswe')

		for f in self.frames.values():
			f.grid(row=1, column=0, sticky='nswe')

		# Message label
		self.lblMsg = tk.Label(self, font='monospace 9',
				anchor='w', justify='left', bg='#ddd')

		self._open_tab('info')

	def close(self, save_model=False):
		if save_model:
			if not self.model_name:
				self.msg("Missing name !", 1)
			elif not doc.is_valid_model_name(self.model_name):
				self.msg("Invalid model-name !", 1)
			elif not self.mod_dict['attributes']:
				self.msg("No attributes set !", 1)
			else:
				doc.DOC['models'][self.model_name] = self.mod_dict
				self.parent.load_from_DOC()
				self.destroy()
				print("\nStoring Model: " + self.model_name)
				print(json.dumps(doc.DOC, indent=4),
					end="\n===============\n")

		else:	self.destroy()


	def msg(self, text, typ=0, clear_after=5):
		def clear_msg():
			if self.lblMsg != None:
				self.lblMsg.grid_remove()
		fgs = ['#222', '#e00', '#0ee']
		self.lblMsg.configure(text=text, fg=fgs[typ%3])
		self.lblMsg.grid(row=3, column=0, sticky='nswe', padx=2)
		self.lblMsg.after(clear_after*1000, clear_msg)


	def _open_tab(self, title):
		if title in self.frames:
			self.frames[title].tkraise()
			self.tablist.enable(title)


class ModelEditFrame(tk.Frame):
	"""
	This frameis used if a new model is added or
	an existing model shall be edited.
	"""
	def __init__(self, parent):
		super().__init__(parent)
		self.mod_dict = parent.mod_dict
		self.msg = parent.msg
		self.parent = parent
		self.setup()

	def setup(self):
		self.grid_columnconfigure(1, weight=1)
#		self.grid_rowconfigure(1, minsize=2)
		self.grid_rowconfigure(2, weight=1)
#		self.configure(highlightbackground='#aaa', highlightthickness=1)

		# Model Name
		EntryLabel(self, "Name").do_grid(0, 0)
		self.vName = tk.StringVar(self)
		self.vName.set(self.parent.model_name)
		self.eName = tk.Entry(self, textvariable=self.vName)
		self.eName.grid(row=0, column=1, sticky='we', padx=2)

		# Model description
		EntryLabel(self, "Description").do_grid(1, 0, sticky='nwe')
		self.txtDescr = ScrollTextFrame(self, height=3)
		if 'info' in self.parent.mod_dict:
			self.txtDescr.set_text(self.parent.mod_dict['info'])
		self.txtDescr.grid(row=1, column=1, sticky='nswe', padx=2,
				rowspan=2)

		# Buttons (cancel, ok)
		btns = {
			'Cancel' : self.parent.destroy,
			'Save': self.save_model
		}
		ButtonFrame(self, btns, bg='#aaa')\
			.grid(row=4, column=0, sticky='nswe', columnspan=2)

		if self.parent.edit_mode:
			# If we're in edit mode, the model-name
			# can not be changed!
			self.eName.configure(state=tk.DISABLED)
		else:	self.eName.focus_set()

	def save_model(self):
		self.parent.model_name = self.vName.get()
		self.mod_dict['info'] = self.txtDescr.get_text()
		self.parent.close(True)


class AttributeListFrame(tk.Frame):
	"""
	Holding a list with all model attributes and a button
	to add a new attributes.
	"""
	def __init__(self, parent):
		"""
		Args:
		  parent: Parent widget (ModelEditWindow)
		"""
		super().__init__(parent)
		self.parent = parent
		self.mod_dict = parent.mod_dict
		self.msg = parent.msg
		self.attrs_dict = {}
		self.edit_mode = False

		if parent.mod_dict['attributes']:
			self.attrs_dict = parent.mod_dict['attributes']
			self.edit_mode = True
		self.setup()

	def setup(self):
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)

		# List with attributes
		self.scrollframe = None
		self._update_attribute_list()

		# Button to add parameter
		btns = {'Add' : lambda:self.open_subview('editattr')}
		self.btnFrame = ButtonFrame(self, btns, bg='#aaa')
		self.btnFrame.grid(row=1, column=0, sticky='nswe')

		# Attribute editing Frame
		self.attrEditFrame = None

	def open_subview(self, title, key='', attr_dict=None):
		if title == 'attrlist':
			if self.attrEditFrame:
				self.attrEditFrame.grid_remove()
				self.attrEditFrame.destroy()
			self.scrollframe.grid(row=0, column=0, sticky='nswe')
			self.btnFrame.grid(row=1, column=0, sticky='nswe')
		elif title == 'editattr':
			self.scrollframe.grid_remove()
			self.btnFrame.grid_remove()
			self.attrEditFrame = AttributeEditFrame(self,
						key, attr_dict)
			self.attrEditFrame.grid(row=0, column=0, sticky='nswe', padx=2)

	def add_attribute(self, name, attr_dict):
		self.attrs_dict[name] = attr_dict
		self.mod_dict['attributes'] = self.attrs_dict
		self._update_attribute_list()

	def _delete_attribute(self, name):
		if name in self.attrs_dict:
			del self.attrs_dict[name]
		self.parent.msg("Deleted attribute '"+name+"'")
		self._update_attribute_list()

	def _update_attribute_list(self):
		if self.scrollframe:
			self.scrollframe.grid_remove()
		self.scrollframe = ScrollFrame(self)
		self.scrollframe.interior.grid_columnconfigure(2, weight=1)
		self.scrollframe.grid(row=0, column=0, sticky='nswe', pady=2, padx=2)

		# Table headers
		f = self.scrollframe.interior
		SmallTableHeader(f, "Name").do_grid(0, 0)
		SmallTableHeader(f, "Type").do_grid(0, 1)
		SmallTableHeader(f, "Required").do_grid(0, 2)
		ttk.Separator(f, orient='horizontal')\
			.grid(row=1, column=0, sticky='nswe', columnspan=6, padx=2)
		y=2
		for name,attr_dict in self.attrs_dict.items():
			self._append_attribute_to_list(name, attr_dict, y)
			y += 1

	def _append_attribute_to_list(self, name, a, row):
		# Append a parameter to scrollable list.
		f = self.scrollframe.interior
		fnt = "Arial 9"
		fg  = '#222'

		# Name
		LeftLabel(f, text=name, font=fnt+' bold', fg=fg)\
			.grid(row=row, column=0, sticky='nswe', padx=(0,20))
		# Datatype
		s = a['type']
		if 'is_array' in a and a['is_array']:
			s = "array[" + s + "]"
		LeftLabel(f, text=s, font=fnt, fg=fg)\
			.grid(row=row, column=1, sticky='nswe', padx=(0,20))
		# Required ?
		s = 'yes' if a['required'] else 'no'
		LeftLabel(f, text=s, font=fnt, fg=fg)\
			.grid(row=row, column=2, sticky='nswe', padx=(0,20))
		# Buttons
		ButtonLabel(f, text="(edit)", on_click=lambda:self.open_subview('editattr',name,a),
				font='Arial 8', hover_font='Arial 8', hover_fg='#444')\
			.grid(row=row, column=3, sticky='swe')
		ButtonLabel(f, text="[x]", font='Arial 8', fg='red', hover_font='Arial 8',
				on_click=lambda:self._delete_attribute(name), hover_fg='#a00')\
			.grid(row=row, column=4, sticky='swe', padx=3)




class AttributeEditFrame(tk.Frame):
	"""
	Frame for creating/editing a model attribute.
	Name        [_______________] [*] Required?
	Datatype    [_____________|v] [*] Is Array?
        Values      [______________________________]
	Description [______________________________]
	"""
	def __init__(self, parent, name='', attr_dict=None):
		super().__init__(parent)
		self.parent = parent
		self.name = name
		self.attr_dict = doc.new_model_attribute()
		self.edit_mode = False

		if attr_dict:
			self.attr_dict = attr_dict
			self.edit_mode = True
		self._setup_gui()

	def _setup_gui(self):
		self.grid_rowconfigure(4, weight=1)
		self.grid_columnconfigure(1, weight=1)

		# Attribute name (key)
		EntryLabel(self, "Name").do_grid(0, 0)
		self.vName = tk.StringVar(self)
		self.vName.set(self.name)
		self.eName = tk.Entry(self, textvariable=self.vName)
		self.eName.grid(row=0, column=1, sticky='we')

		# Is required parameter ?
		self.vRequired = tk.IntVar(self)
		self.vRequired.set(int(self.attr_dict['required']))
		tk.Checkbutton(self, variable=self.vRequired,
				text="Required?", onvalue=1, offvalue=0)\
			.grid(row=0, column=2, sticky='w')

		# Datatype of single value
		EntryLabel(self, "Datatype").do_grid(2, 0)
		self.vDType = tk.StringVar(self)
		self.vDType.set(self.attr_dict['type'])
		self.cbDType = ttk.Combobox(self,
				values=doc.PARAMETER_DATATYPES+list(doc.DOC['models'].keys()),
		                textvariable=self.vDType) #, state='readonly')
		self.cbDType.grid(row=2, column=1, sticky='we', padx=1)

		# Datatype is array?
		self.vIsArray = tk.IntVar(self)
		if 'is_array' in self.attr_dict:
			self.vIsArray.set(int(self.attr_dict['is_array']))
		tk.Checkbutton(self, variable=self.vIsArray,
				text="Is array?", onvalue=1, offvalue=0)\
			.grid(row=2, column=2, sticky='w')

		# Predefined values
		EntryLabel(self, "Values").do_grid(3, 0)
		self.vValues = tk.StringVar(self)
		if 'values' in self.attr_dict:
			self.vValues.set(", ".join([str(x) for x in self.attr_dict['values']]))
		self.eValues = tk.Entry(self, textvariable=self.vValues)
		self.eValues.grid(row=3, column=1, sticky='we', pady=(2,0),columnspan=2)
		ToolTip(self.eValues, "Define allowed values, separated by comma (,)\n"\
					"Syntax: 'VALUE1(, VALUE2(, ...))'")

		# Description
		EntryLabel(self, "Description").do_grid(4, 0, sticky="nwe",
				pady=(2,0))
		self.txtInfo = ScrollTextFrame(self)
		if 'info' in self.attr_dict:
			self.txtInfo.set_text(self.attr_dict['info'])
		self.txtInfo.grid(row=4, column=1, columnspan=2,
				sticky='nswe', pady=(2,5))
		# Buttons
		btns = {}
		btns['Cancel'] = lambda:self.parent.open_subview('attrlist')
		btns['Save'] = lambda:self._save_attribute()

		ButtonFrame(self, btns, bg='#aaa')\
			.grid(row=5, column=0, sticky='nswe',
				columnspan=3)

		if self.edit_mode:
			# Name can't be changed on existing parameter
			self.eName.configure(state=tk.DISABLED)
		else:	self.eName.focus_set()


	def _delete_attribute(self):
		if not doc.is_valid_parameter_key(self.name):
			self.parent.msg("Invalid attribute name !", 1)
		else:
			self.parent.delete_attribute(self.name)
			self.parent.open_subview('attrlist')

	def _save_attribute(self):
		self.name = self.vName.get()
		if not self.edit_mode and self.name in self.parent.attrs_dict:
			self.parent.msg("Attribute '"+self.name+"' exists !", 1)
		elif not self.name:
			self.parent.msg("Missing attribute name !", 1)
		elif not self.vDType.get():
			self.parent.msg("No datatype set !", 1)
		else:
			self.attr_dict['type'] = self.vDType.get()
			self.attr_dict['required'] = self.vRequired.get()
			self.attr_dict['info'] = self.txtInfo.get_text()

			if self.vIsArray.get():
				self.attr_dict['is_array'] = True
			if self.vValues.get():
				self.attr_dict['values'] = \
					[v.strip() for v in self.vValues.get().split(',')]

			self.parent.add_attribute(self.name, self.attr_dict)
			self.parent.open_subview('attrlist')

