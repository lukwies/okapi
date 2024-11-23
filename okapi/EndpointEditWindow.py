import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesno
#from tkinter.messagebox import askyesno
import json

import DOC as doc
from widgets import ScrollFrame
from widgets import ButtonLabel
from widgets import LeftLabel
from widgets import ScrollTextFrame
from widgets import ButtonFrame
from widgets import Tablist
from widgets import ToolTip
from utils import parse_key_value_text_to_dict

from style import EntryLabel
from style import SmallTableHeader

"""
A toplevel window to create/edit an endpoint.
"""

# Used fonts
A8b = "Arial 8 bold"
A9b = "Arial 9 bold"
A9  = "Arial 9"

###
### Standalone window to edit an api endpoint and its parameters.
###

class EndpointEditWindow(tk.Toplevel):
	"""
	A toplevel window, spawned on endpoint adding / editing.
	"""
	def __init__(self, parent, method=None, uri=None):
		super().__init__(parent)
		self.parent = parent
		self.A      = parent.A
		self.method = 'GET'
		self.uri    = ''
		self.edit_mode = False
		self.ep_dict = doc.new_endpoint()

		if doc.DOC_is_endpoint(method, uri):
			self.method = method
			self.uri = uri
			self.ep_dict = doc.DOC_get_endpoint(method, uri, True)
			self.edit_mode = True
		self._setup_gui()

	def _setup_gui(self):
		self.geometry('340x300')
		self.title("Api Endpoint")

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)

		# Tablist
		tab_btns = {
			'endpoint' : (' Endpoint ',
					lambda:self.open_view('endpoint')),
			'parameters' : (' Parameters ',
					lambda:self.open_view('parameters')),
			'response' : (' Response ',
					lambda:self.open_view('response'))
		}
		self.tabs = Tablist(self, tab_btns,
				bg_hover='#ddd', bg='#bbb',
				fg_hover='#222', fg='#111')
		self.tabs.grid(row=0, column=0, sticky='nswe')

		# Mainframes
		self.frames = {
			'endpoint' : EndPointEditFrame(self),
			'parameters' : ParameterListFrame(self),
			'response' : ResponseListFrame(self)
		}
		for frame in self.frames.values():
			frame.grid(row=1, column=0, sticky='nswe')
		self.open_view('endpoint')

		# Message label
		self.lblMsg = tk.Label(self, font='monospace 9',
				anchor='w', justify='left', bg='#ddd')

	def close_window(self, save_endpoint=False):
		if save_endpoint:
			if not self.uri:
				self.A.msg("Missing URI !", 1)
			elif self.uri[0] != "/":
				self.A.msg("URI must have a leading '/'", 1)
			elif not doc.is_valid_URI(self.uri,
					allow_placeholders=True):
				self.A.msg("URI has invalid format !", 1)
			elif 'summary' not in self.ep_dict or not self.ep_dict['summary']:
				self.A.msg("Please set a summary !", 1)
			else:
				doc.DOC_add_endpoint(self.method,
					self.uri, self.ep_dict)
				self.parent.load_from_DOC()
				self.destroy()
				self.A.msg("Created endpoint " + self.uri)
		else:	self.destroy()


	def set_msg(self, text, clear_after=5, fg='#222'):
		def clear_msg():
			if self.lblMsg != None:
				self.lblMsg.grid_remove()
		self.lblMsg.configure(text=text, fg=fg)
		self.lblMsg.grid(row=3, column=0, sticky='nswe', padx=2)
		self.lblMsg.after(clear_after*1000, clear_msg)

	def open_view(self, title):
		self.frames[title].tkraise()
		self.tabs.enable(title)

	def get_method_and_uri(self):
		self.frames['endpoint'].save_all_values()
		return self.method, self.uri


class EndPointEditFrame(tk.Frame):
	"""
	This frameis used if a new endpoint is added or
	an existing endpoint shall be edited.
	"""
	def __init__(self, parent):
		super().__init__(parent)
		self.ep_dict = parent.ep_dict
		self.set_msg = parent.set_msg
		self.parent = parent
		self._setup_gui()

	def save_all_values(self):
		"""
		Gather all values from gui items and store them.
		"""
		self.parent.method = self.vMethod.get()
		uri = self.vURI.get().strip()
		if uri and uri != "/":
			if uri[-1] == "/": uri = uri.rstrip("/")
			if uri[0]  != "/": uri = "/" + uri
		self.parent.uri = uri
		self.parent.ep_dict['summary'] = self.vSummary.get()
		self.parent.ep_dict['info'] = self.txtInfo.get_text()

	def _setup_gui(self):
		self.grid_columnconfigure(1, weight=1)
		self.grid_rowconfigure(3, weight=1)

		# Endpoint HTTP method
		EntryLabel(self, "Method").do_grid(0, 0)
		self.vMethod = tk.StringVar(self)
		self.vMethod.set(self.parent.method)
		self.cbMethod = ttk.Combobox(self,values=['GET', 'POST', 'PUT', 'HEAD', 'DELETE'],
		                textvariable=self.vMethod, state='readonly', width=7)
		self.cbMethod.grid(row=0, column=1, sticky='w', padx=2, pady=4)

		# Endpoint URI
		EntryLabel(self, 'URI').do_grid(1, 0)
		self.vURI = tk.StringVar(self)
		self.vURI.set(self.parent.uri)
		self.eURI = tk.Entry(self, textvariable=self.vURI)
		self.eURI.grid(row=1, column=1, sticky='we', padx=1)

		# Summary
		self.vSummary = tk.StringVar(self)
		if 'summary' in self.parent.ep_dict:
			self.vSummary.set(self.parent.ep_dict['summary'])

		EntryLabel(self, 'Summary').do_grid(2, 0)
		self.eSummary = tk.Entry(self, textvariable=self.vSummary)
		self.eSummary.grid(row=2, column=1, sticky='we', padx=1)
		ToolTip(self.eSummary, "Enter short description")

		# Endpoint description
		EntryLabel(self, 'Description').do_grid(3, 0, sticky='nwe', pady=(4,0))
		self.txtInfo = ScrollTextFrame(self, height=3)
		if 'info' in self.parent.ep_dict:
			self.txtInfo.set_text(self.parent.ep_dict['info'])
		self.txtInfo.grid(row=3, column=1, sticky='nswe', padx=2)

		# Buttons (cancel, ok)
		btns = {
			'Cancel' : self.parent.destroy,
			'Save': self._save_endpoint
		}
		ButtonFrame(self, btns, bg='#aaa')\
			.grid(row=6, column=0, sticky='nswe', columnspan=2)

		if self.parent.edit_mode:
			# If we're in edit mode, HTTP method and URI
			# can not be changed!
			self.cbMethod.configure(state=tk.DISABLED)
			self.eURI.configure(state=tk.DISABLED)
		else:	self.eURI.focus_set()

	def _save_endpoint(self):
		self.save_all_values()
		self.parent.close_window(True)


class ParameterListFrame(tk.Frame):
	"""
	Holding a list with all endpoint parameters and a button
	to add a new parameter.
	"""
	def __init__(self, parent):
		"""
		Args:
		  parent: Parent widget (EndPointEditWindow)
		  params_dict: Dict with all parameters (see apidoc.py)
		"""
		super().__init__(parent)
		self.parent = parent
		self.ep_dict = parent.ep_dict
		self.set_msg = parent.set_msg
		self.params_dict = {}
		self.edit_mode = False

		if parent.ep_dict['params']:
			self.params_dict = parent.ep_dict['params']
			self.edit_mode = True
		self._setup_gui()

	def _setup_gui(self):
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)

		# Scrollable list with parameters
		self.scrollframe = None
		self._update_parameter_list()

		# Button to add parameter
		btns = {'Add' : lambda:self.open_subview('editparam')}
		self.btnFrame = ButtonFrame(self, btns, bg='#aaa')
		self.btnFrame.grid(row=1, column=0, sticky='nswe')

		self.paramEditFrame = None

	def open_subview(self, title, key='', param_dict=None):
		if title == 'paramlist':
			if self.paramEditFrame:
				self.paramEditFrame.grid_remove()
				self.paramEditFrame.destroy()
			self.scrollframe.grid(row=0, column=0, sticky='nswe')
			self.btnFrame.grid(row=1, column=0, sticky='nswe')
		elif title == 'editparam':
			self.scrollframe.grid_remove()
			self.btnFrame.grid_remove()
			self.paramEditFrame = ParameterEditFrame(self,
						key, param_dict)
			self.paramEditFrame.grid(row=0, column=0, sticky='nswe')

	def add_parameter(self, key, param_dict):
		# Add parameter
		self.params_dict[key] = param_dict
		self.ep_dict['params'] = self.params_dict
		self._update_parameter_list()

	def _delete_parameter(self, key):
		# Delete parameter
		if key not in self.params_dict:
			return False

		#yes = askyesno("Delete parameter",
		#		"Do you really want to delete parameter '"+key+"' ?")
		#if not yes: return False
		del self.params_dict[key]
		self.parent.set_msg("Deleted parameter '"+key+"'", 5)
		self._update_parameter_list()
		return True

	def _update_parameter_list(self):
		if self.scrollframe:
			self.scrollframe.grid_remove()
		self.scrollframe = ScrollFrame(self)
		self.scrollframe.interior.grid_columnconfigure(3, weight=1)
		self.scrollframe.grid(row=0, column=0, sticky='nswe', pady=2, padx=2)

		# Table headers
		f = self.scrollframe.interior
		SmallTableHeader(f, "Name").do_grid(0, 0)
		SmallTableHeader(f, "Type").do_grid(0, 1)
		SmallTableHeader(f, "Source").do_grid(0, 2)
		SmallTableHeader(f, "Required").do_grid(0, 3)
		ttk.Separator(f, orient='horizontal')\
			.grid(row=1, column=0, sticky='nswe', columnspan=6, padx=2)

		y = 2
		for key,p in self.params_dict.items():
			self._append_parameter_to_list(key, p, y)
			y += 1

	def _append_parameter_to_list(self, key, p, row):
		# Append a parameter to scrollable list.
		f = self.scrollframe.interior
		fnt = "Arial 9"
		fg  = '#222'

		# Name
		LeftLabel(f, text=key, font=fnt+' bold', fg=fg)\
			.grid(row=row, column=0, sticky='nswe', padx=(0,20))
		# Datatype
		s = p['type']
		if 'is_array' in p and p['is_array']:
			s = "array[" + s + "]"
		LeftLabel(f, text=s, font=fnt, fg=fg)\
			.grid(row=row, column=1, sticky='nswe', padx=(0,20))
		# Source
		LeftLabel(f, text=p['source'], font=fnt, fg=fg)\
			.grid(row=row, column=2, sticky='nswe', padx=(0,20))

		# Required ?
		s = 'yes' if p['required'] else 'no'
		LeftLabel(f, text=s, font=fnt, fg=fg)\
			.grid(row=row, column=3, sticky='nswe', padx=(0,20))

		# Buttons
		ButtonLabel(f, text="(edit)", on_click=lambda:self.open_subview('editparam',key,p),
				font='Arial 8', hover_font='Arial 8', hover_fg='#444')\
			.grid(row=row, column=4, sticky='swe')
		ButtonLabel(f, text="[x]", font='Arial 8', fg='red', hover_font='Arial 8',
				on_click=lambda:self._delete_parameter(key), hover_fg='#a00')\
			.grid(row=row, column=5, sticky='swe', padx=3)


class ParameterEditFrame(tk.Frame):
	"""
	Frame for editing an endpoint parameter.
	"""
	def __init__(self, parent, key='', param_dict=None):
		super().__init__(parent)
		self.parent = parent
		self.key = key
		self.param_dict = doc.new_endpoint_parameter()
		self.edit_mode = False

		if param_dict:
			self.param_dict = param_dict
			self.edit_mode = True

		self.vKey = tk.StringVar(self)
		self.vSource = tk.StringVar(self)

		self.method,self.uri = parent.parent.get_method_and_uri()

		# Get pathitems and remove the ones already declared.
		self.path_items = doc.get_url_path_items(self.uri)
		for pit in self.path_items:
			if pit in parent.params_dict:
				self.path_items.remove(pit)

		self.dtypeValues = ['string', 'integer', 'boolean',
					 'decimal', 'object']
		self.sourceValues = []

		if self.path_items:
			print("PATHITEMS:", self.path_items)
			self.sourceValues.append('path')
		if self.method == 'GET':
			self.sourceValues += ['query', 'header']
			self.dtypeValues = self.dtypeValues[:-1]
		else:
			self.sourceValues += ['form-data', 'body', 'header']
			self.dtypeValues += list(doc.DOC['models'].keys())
		if key:
			self.vKey.set(key)
		self.vSource.set(self.sourceValues[0])
		self._setup_gui()

	def _setup_gui(self):
		self.grid_rowconfigure(6, weight=1)
		self.grid_columnconfigure(1, weight=1)

		# Parameter name (key)
		EntryLabel(self, "Name").do_grid(1, 0)
		self.eKey = tk.Entry(self, textvariable=self.vKey)
		self.eKey.grid(row=1, column=1, sticky='we')

		# Is required parameter ?
		self.vRequired = tk.IntVar(self)
		self.vRequired.set(int(self.param_dict['required']))
		self.cRequired = tk.Checkbutton(self, variable=self.vRequired,
				font='Arial 8 bold', fg='#222',
				text=" Required?", onvalue=1, offvalue=0)
		self.cRequired.grid(row=1, column=2, sticky='nsew', padx=(2,5))

		# Datatype
		EntryLabel(self, "Datatype").do_grid(2, 0)
		self.vDType = tk.StringVar(self)
		self.cbDType = ttk.Combobox(self,
				values=self.dtypeValues,
		                textvariable=self.vDType) #, state='readonly')
		self.cbDType.grid(row=2, column=1, sticky='we', padx=1)
		self.cbDType.bind("<<ComboboxSelected>>", self._on_select_dtype)
		if self.edit_mode:
			self.vDType.set(self.param_dict['type'])
			self.cbDType.configure(state=tk.DISABLED)

		# Datatype is list/array?
		self.vIsArray = tk.IntVar(self)
		if 'is_array' in self.param_dict:
			self.vIsArray.set(self.param_dict['is_array'])
		self.cIsArray = tk.Checkbutton(self, variable=self.vIsArray,
				font='Arial 8 bold', fg='#222',
				text=" Is array?", onvalue=1, offvalue=0)
		self.cIsArray.grid(row=2, column=2, sticky='w', padx=(2,5))

		# Content-Type
		self.vCType = tk.StringVar(self)
		self.lblCType = EntryLabel(self, "Content-Type")
		self.cbCType = ttk.Combobox(self, textvariable=self.vCType,
				values=["application/json","application/xml"],
				state='readonly')

		# Parameter source
		EntryLabel(self, "Source").do_grid(3, 0)
		self.cbSource = ttk.Combobox(self, width=10,
				values=self.sourceValues,
		                textvariable=self.vSource, state='readonly')
		self.cbSource.grid(row=3, column=1, sticky='w', padx=1, pady=2)
		self.cbSource.bind("<<ComboboxSelected>>", self._on_select_source)

		# Predefined values
		self.vValues = tk.StringVar(self)
		if 'values' in self.param_dict:
			self.vValues.set(", ".join([str(x) \
				for x in self.param_dict['values']]))
		self.lblValues = EntryLabel(self, 'Values')
		self.eValues = tk.Entry(self, textvariable=self.vValues)

		# Description
		EntryLabel(self, "Description").do_grid(6, 0, sticky='new', pady=(4,0))
		self.txtInfo = ScrollTextFrame(self)
		self.txtInfo.grid(row=6, column=1, sticky='nswe', padx=1,
				columnspan=2)
		if 'info' in self.param_dict:
			self.txtInfo.set_text(self.param_dict['info'])

		# Buttons
		btns = {}
		btns['Cancel'] = lambda:self.parent.open_subview('paramlist')
		btns['Save'] = lambda:self._save_parameter()

		ButtonFrame(self, btns, bg='#aaa')\
			.grid(row=9, column=0, sticky='nswe',
				columnspan=3)

		if self.edit_mode:
			# Key can't be changed on existing parameter
			self.eKey.configure(state=tk.DISABLED)
			self.cIsArray.configure(state=tk.DISABLED)
			self.cbSource.configure(state=tk.DISABLED)
			self.cbDType.configure(state=tk.DISABLED)
		else:
			self.eKey.focus_set()
			self._on_select_source()


	def _save_parameter(self):
		# Save parameter
		self.key = self.vKey.get()
		if not self.edit_mode and self.key in self.parent.params_dict:
			self.parent.set_msg("Parameter '"+self.key+"' exists !", 5, '#e00')
			return
		if not self.vDType.get():
			self.parent.set_msg("Missing datatype !", 5, '#e00')
			return

		self.param_dict['required'] = self.vRequired.get()
		self.param_dict['type']     = self.vDType.get()
		self.param_dict['source']   = self.vSource.get()

		if self.vIsArray.get():
			self.param_dict['is_array'] = self.vIsArray.get()
		if self.vCType.get():
			self.param_dict['content_type'] = self.vCType.get()
		if self.txtInfo.get_text():
			self.param_dict['info'] = self.txtInfo.get_text()

		if not self.key:
			if self.param_dict['source'] == 'body':
				# If no key is given and source is 'body',
				# the key name is set to 'body' as well.
				self.key = 'body'
			else:
				self.parent.set_msg("Missing parameter name !", 4, '#e00')
				return

		if self.vValues.get():
			self.param_dict['values'] = \
				[v.strip() for v in self.vValues.get().split(',')]

		self.parent.add_parameter(self.key, self.param_dict)
		self.parent.open_subview('paramlist')

	def _on_select_source(self, ev=None):
		# Called if combobox 'Source' selected
		self.cRequired.configure(state=tk.NORMAL)
		self._show_hide_content_type(False)
		self._show_hide_values(False)
		if not self.edit_mode:
			self.eKey.configure(state=tk.NORMAL)

		src = self.vSource.get()
		if src == 'path':
			# A path item parameter must be set.
			# If there's just one path item, set it as
			# parameter name/key. Allowed datatype: string,
			# integer
			self.vDType.set("")
			self.cbDType.configure(values=['string','integer'])
			self.vRequired.set(1)
			self.cRequired.configure(state=tk.DISABLED)

			# Set pathitem as key/name if not already defined.
			for pi in self.path_items:
				if pi not in self.parent.params_dict:
					self.vKey.set(pi)
					return
			# All pathitems are defined, remove 'path' from
			# combobox.
			self.sourceValues.remove('path')
			self.cbSource.configure(values=self.sourceValues)
			self.cRequired.configure(state=tk.NORMAL)
			self.vSource.set(self.sourceValues[0])
			self.vRequired.set(0)

		elif src == 'body':
			# body allowes all datatypes
			self.vDType.set("")
			self.cbDType.configure(values=self.dtypeValues)
			self.vRequired.set(0)

		elif src in ('query', 'header'):
			# Allowed Types: string,int,decimal,bool
			self.vDType.set("")
			self.cbDType.configure(values=self.dtypeValues[:4])
			self.vRequired.set(0)


	def _on_select_dtype(self, ev=None):
		# Called if combobox 'Datatype' selected
		dt  = self.vDType.get()
		src = self.vSource.get()
		if dt == 'object' or dt in doc.DOC['models']:
			if dt == 'object':
				self.parent.set_msg("You should rather create a model!", 5)
			if src == 'body':
				self.vKey.set("body")
				self.eKey.configure(state=tk.DISABLED)
			self.vCType.set("application/json")
			self._show_hide_content_type(True)
			self._show_hide_values(False)
		else:
			self._show_hide_content_type(False)
			self._show_hide_values(True)
			if self.eKey['state'] == tk.DISABLED:
				self.eKey.configure(state=tk.NORMAL)
				self.vKey.set("")

	def _show_hide_values(self, show=True):
		if show:
			self.lblValues.grid(row=4, column=0, sticky='nswe', padx=(3,0))
			self.eValues.grid(row=4, column=1, columnspan=2, sticky='we')
		else:
			self.vValues.set("")
			self.lblValues.grid_remove()
			self.eValues.grid_remove()

	def _show_hide_content_type(self, show=True):
		if show:
			self.lblCType.grid(row=5, column=0, sticky='nswe', padx=3)
			self.cbCType.grid(row=5, column=1, sticky='we', padx=1, columnspan=2)
		else:
			self.vCType.set("")
			self.lblCType.grid_remove()
			self.cbCType.grid_remove()


class ResponseListFrame(tk.Frame):
	"""
	Holding a list with all responses.
	"""
	def __init__(self, parent):
		"""
		Args:
		  parent: Parent widget (EndPointEditWindow)
		"""
		super().__init__(parent)
		self.parent = parent
		self.ep_dict = parent.ep_dict
		self.set_msg = parent.set_msg
		self.resps_dict = {}
		self.edit_mode = False

		if parent.ep_dict['response']:
			self.resps_dict = parent.ep_dict['response']
			self.edit_mode = True
		self._setup_gui()

	def _setup_gui(self):
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)

		# List with responses
		self.scrollframe = None
		self._update_responses_list()

		# Reponse editing Frame
		self.respEditFrame = None

		# Button to add parameter
		btns = {'Add' : lambda:self.open_subview('editresponse')}
		self.btnFrame = ButtonFrame(self, btns, bg='#aaa')
		self.btnFrame.grid(row=1, column=0, sticky='nswe')

	def open_subview(self, title, status_code='', resp_dict=None):
		if title == 'responseslist':
			if self.respEditFrame:
				self.respEditFrame.grid_remove()
				self.respEditFrame.destroy()
			self.scrollframe.grid(row=0, column=0, sticky='nswe')
			self.btnFrame.grid(row=1, column=0, sticky='nswe')
		elif title == 'editresponse':
			self.scrollframe.grid_remove()
			self.btnFrame.grid_remove()
			self.respEditFrame = ResponseEditFrame(self,
						status_code, resp_dict)
			self.respEditFrame.grid(row=0, column=0, sticky='nswe')

	def add_response(self, status_code, resp_dict):
		# Add response
		self.resps_dict[status_code] = resp_dict
		self.ep_dict['response'] = self.resps_dict
		self._update_responses_list()

	def _delete_response(self, status_code):
		# Delete response
		if status_code in self.resps_dict:
			del self.resps_dict[status_code]
			self.parent.set_msg("Deleted response '"+str(status_code)+"'", 5)
			self._update_responses_list()

	def _update_responses_list(self):
		if self.scrollframe:
			self.scrollframe.grid_remove()
		self.scrollframe = ScrollFrame(self)
		self.scrollframe.interior.grid_columnconfigure(1, weight=1)
		self.scrollframe.grid(row=0, column=0, sticky='nswe', pady=2, padx=2)

		# Table headers
		f = self.scrollframe.interior
		SmallTableHeader(f, "Code").do_grid(0, 0)
		SmallTableHeader(f, "Description").do_grid(0, 1)
		ttk.Separator(f, orient='horizontal')\
			.grid(row=1, column=0, sticky='nswe', columnspan=4, padx=2)
		y = 2
		for code,resp_dict in self.resps_dict.items():
			self._append_response_to_list(code, resp_dict, y)
			y += 1

	def _append_response_to_list(self, code, r, row):
		# Append a response to scrollable list.
		f = self.scrollframe.interior
		fnt = "Arial 9"
		fg  = '#222'
		# Name
		LeftLabel(f, text=code, font=fnt+' bold', fg=fg)\
			.grid(row=row, column=0, sticky='nswe', padx=(1,20))
		# Description
		LeftLabel(f, text=r['summary'], font=fnt, fg=fg)\
			.grid(row=row, column=1, sticky='nswe', padx=(0,20))
		# Buttons
		ButtonLabel(f, text="(edit)", on_click=lambda:self.open_subview('editresponse',code,r),
				font='Arial 8', hover_font='Arial 8', hover_fg='#444')\
			.grid(row=row, column=2, sticky='swe')
		ButtonLabel(f, text="[x]", font='Arial 8', fg='red', hover_font='Arial 8',
				on_click=lambda:self._delete_response(code), hover_fg='#a00')\
			.grid(row=row, column=3, sticky='swe', padx=3)


class ResponseEditFrame(tk.Frame):
	"""
	Frame to create/edit a response.
	"""
	def __init__(self, parent, status_code='', resp_dict=None):
		super().__init__(parent)
		self.parent = parent
		self.status_code = status_code
		self.resp_dict = doc.new_endpoint_response()
		self.edit_mode = False

		if resp_dict:
			self.resp_dict = resp_dict
			self.edit_mode = True

		self._setup_gui()


	def _setup_gui(self):
		self.grid_rowconfigure(3, weight=1)
		self.grid_columnconfigure(1, weight=1)

		self.lPAD = {"padx" : (3,5), "pady" : (2,0)}
		self.rPAD = {"padx" : (1,1), "pady" : (2,0)}
		self.r2PAD = {"padx" : (0,1), "pady" : (1,0)}

		# HTTP status code
		EntryLabel(self, "Status-Code*").do_grid(0, 0)
		self.vCode = tk.StringVar(self)
		self.vCode.set(self.status_code)
		self.eCode = tk.Entry(self, textvariable=self.vCode, width=4)
		self.eCode.grid(row=0, column=1, sticky='w', padx=1, pady=(5,0))
		self.eCode.bind("<FocusOut>", self._on_status_code_select)
		self.eCode.bind("<Return>", self._on_status_code_select, add='+')
		ToolTip(self.eCode, "Enter HTTP status code (200, 404, ...)")

		if self.edit_mode:
			# Code can't be changed on existing response
			self.eCode.configure(state=tk.DISABLED)
		else:	self.eCode.focus_set()

		# Summary
		EntryLabel(self, "Summary").do_grid(1, 0)
		self.vSummary = tk.StringVar(self)
		self.vSummary.set(self.resp_dict['summary'])
		self.eSummary = tk.Entry(self, textvariable=self.vSummary)
		self.eSummary.grid(row=1, column=1, sticky='we', padx=(0,1), pady=1)
		ToolTip(self.eSummary, "Enter a short description")

		# Tablist
		tabs = {
			'header' : (' Header ', lambda:self._open_tab('header')),
			'body'   : (' Body ',   lambda:self._open_tab('body'))
		}
		self.tablist = Tablist(self, tabs,
				bg_hover='#ccc', bg='#bbb',
				fg_hover='#222', fg='#111')
		self.tablist.grid(row=2, column=0, columnspan=2, sticky='nswe', pady=(10,0))

		# Tabs
		self.tabframes = {
			'header' : ResponseEditHeadersFrame(self, self.resp_dict),
			'body' : ResponseEditBodyFrame(self, self.resp_dict)
		}
		for frame in self.tabframes.values():
			frame.grid(row=3, column=0, columnspan=2, sticky='nswe')
		self._open_tab('header')

		# Buttons
		btns = {
			'Cancel' : lambda:self.parent.open_subview('responseslist'),
			'Save' : lambda:self._save_response()
		}
		ButtonFrame(self, btns, bg='#aaa')\
			.grid(row=8, column=0, sticky='nswe', pady=(2,0),
				columnspan=2)

		self._on_status_code_select(None)

	def _on_status_code_select(self, ev=None):
		# If status code is 20X, user can define a model as
		# response body
		c = self.vCode.get()
		if c and not doc.is_valid_http_code(c):
			self.parent.set_msg("Invalid status-code !", 5, '#e00')
			self.vCode.set("")

	def _open_tab(self, title):
		# Open 'header' or 'body' settings tab
		if title in self.tabframes:
			self.tabframes[title].tkraise()
			self.tablist.enable(title)


	def _save_response(self):
		# For saving a response, status-code and summary are
		# required to be set.
		self.status_code=code = self.vCode.get()
		if not code:
			self.parent.set_msg("Please set a status-code !", 5, '#e00')
		elif not doc.is_valid_http_code(code):
			self.parent.set_msg("Invalid http status-code !", 5, '#e00')
		elif not self.edit_mode and code in self.parent.resps_dict:
			self.parent.set_msg("Status code '"+code+"' exists !", 5, '#e00')
		elif not self.vSummary.get():
			self.parent.set_msg("Please set a summary !", 5, '#e00')
		else:
			self.resp_dict['summary'] = self.vSummary.get()
			vtype    = self.tabframes['body'].get_type()
			#if vtype: 
			self.resp_dict['content_type'] = vtype
			vModel   = self.tabframes['body'].get_model()
			if vModel: self.resp_dict['model'] = vModel
			vExample = self.tabframes['body'].get_example()
			if vExample: self.resp_dict['example'] = vExample
			vHeaders = self.tabframes['header'].get_headers()
			if vHeaders: self.resp_dict['headers'] = vHeaders.copy()

			self.parent.add_response(code, self.resp_dict)
			self.parent.open_subview('responseslist')

class ResponseEditHeadersFrame(tk.Frame):
	def __init__(self, parent, resp_dict=None):
		super().__init__(parent)
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)
		self.txt = ScrollTextFrame(self, scroll_horizontal=False)
		self.txt.grid(row=0, column=0, sticky='nswe', pady=5, padx=2)

		if resp_dict and 'headers' in resp_dict:
			for k,v in resp_dict['headers'].items():
				self.txt.add_text(str(k) + ": " + str(v) + "\n")

	def get_headers(self) -> dict:
		"""
		Get headers as dictionary.
		Returns None on error.
		"""
		return parse_key_value_text_to_dict(self.txt.get_text())


class ResponseEditBodyFrame(tk.Frame):
	def __init__(self, parent, resp_dict):
		super().__init__(parent)
		self.resp_dict = resp_dict
		self._setup_gui()

	def get_type(self):
		return self.vType.get()
	def get_model(self):
		return self.vModel.get()
	def get_example(self):
		return self.txtEx.get_text()

	def _setup_gui(self):
		self.grid_rowconfigure(2, weight=1)
		self.grid_columnconfigure(1, weight=1)

		self.lPAD = {"padx" : (3,5), "pady" : (2,0)}
		self.rPAD = {"padx" : (1,1), "pady" : (2,0)}
		self.r2PAD = {"padx" : (0,1), "pady" : (1,0)}

		# Respond with Model ?
		self.vModel = tk.StringVar(self)
		if 'model' in self.resp_dict:
			self.vModel.set(self.resp_dict['model'])
		self.lblModel = EntryLabel(self, "Model")
		self.lblModel.grid(row=0, column=0, sticky='nswe', padx=3, pady=(10,0))
		self.cbModel = ttk.Combobox(self, textvariable=self.vModel,
				values=['']+list(doc.DOC['models'].keys()),
				state='readonly')
		self.cbModel.bind("<<ComboboxSelected>>", self._on_model_select)
		self.cbModel.grid(row=0, column=1, sticky='we', padx=1, pady=(10,0))

		# Content-Type  (onyl if code=2XX)
		self.vType = tk.StringVar(self)
		if 'content_type' in self.resp_dict:
			self.vType.set(self.resp_dict['content_type'])
		self.lblType = EntryLabel(self, 'Content-Type')
		self.lblType.grid(row=1, column=0, sticky='nswe', **self.lPAD)
		self.cbType = ttk.Combobox(self, textvariable=self.vType,
				values=doc.RESPONSE_CONTENT_TYPES)
		self.cbType.bind("<<ComboboxSelected>>", self._on_type_select)
		self.cbType.grid(row=1, column=1, sticky='we', **self.rPAD)

		# Example
		self.lblEx = EntryLabel(self, 'Example\nbody')
		self.txtEx = ScrollTextFrame(self, scroll_horizontal=False)
		if 'example' in self.resp_dict:
			self.txtEx.set_text(self.resp_dict['example'])

		self._on_type_select()

	def _on_type_select(self, ev=None):
		# If type is "text/..." or "application/..." and no model
		# is selected, user can define an example response body
		typ = self.vType.get()
		if typ and (typ.startswith("text/") or (typ.startswith("application/")) \
				and not self.vModel.get()):
			self.lblEx.grid(row=2, column=0, sticky='nw', **self.lPAD)
			self.txtEx.grid(row=2, column=1, sticky='nswe', **self.rPAD)
		else:
			self.txtEx.set_text("")
			self.lblEx.grid_remove()
			self.txtEx.grid_remove()

	def _on_model_select(self, ev=None):
		# If a model was selected, set content-type to json/xml
		# and remove example frame
		name = self.vModel.get()
		if name:
			self.vType.set("application/json")
			self.cbType.configure(values=["application/json","application/xml"])
			self.lblEx.grid_remove()
			self.txtEx.grid_remove()
			self.txtEx.set_text("")
		else:
			self.vType.set("")
			self.cbType.configure(values=doc.RESPONSE_CONTENT_TYPES)
