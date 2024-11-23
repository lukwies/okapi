import tkinter as tk
from tkinter import ttk
from tkinter.constants import *

import pyperclip

class LeftLabel(tk.Label):
	'''
	Left justified label
	'''
	def __init__(self, parent, *args, **kwargs):
		super().__init__(parent, *args, **kwargs)
		self.configure(anchor='w', justify='left')

class Separator(tk.Frame):
	"""
	Small colored frame acting as a separator.
	Need this because ttk.Separator has always a 1px white border
	that cannot be removed (wtf?!).
	"""
	def __init__(self, parent, orient='horizontal',
			color='#444', size=1):
		super().__init__(parent, background=color)
		self.set(orient, size)

	def set(self, orient, size):
		if orient == 'horizontal':
			self.configure(height=size)
		elif orient == 'vertical':
			self.configure(width=size)
		else:	return

		self.orient = orient
		self.size = size

class ScrollTextFrame(tk.Frame):
	"""
	Frame with scrolltext area.
	"""
	def __init__(self, parent, disabled=False,
				scroll_vertical=True,
				scroll_horizontal=True,
				*args, **kwargs):
		super().__init__(parent)
		self.disabled = disabled
		self.text = tk.Text(self, wrap=tk.NONE,
				highlightthickness=0,
				*args, **kwargs)

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)
		self.text.grid(row=1, column=0, sticky='nswe')
		self.tags = {}

		if scroll_vertical:
			yScroll = tk.Scrollbar(self, orient='vertical')
			self.text.configure(yscrollcommand=yScroll.set)
			yScroll.grid(row=1, column=1, sticky='ns', rowspan=2)
			yScroll.configure(command=self.text.yview)

		if scroll_horizontal:
			xScroll = tk.Scrollbar(self, orient='horizontal')
			self.text.configure(xscrollcommand=xScroll.set)
			xScroll.grid(row=2, column=0, sticky='we')
			xScroll.configure(command=self.text.xview)

		if disabled:
			self.configure(state=tk.DISABLED)

	def block(self, block=True):
		self.text.configure(state="disabled" if block else "normal")

	def configure(self, *args, **kwargs):
		self.text.configure(*args, **kwargs)

	def bind(self, event, callback, add=None):
		self.text.bind(event, callback, add=add)

	def focus_set(self):
		self.text.focus_set()

	def nlines(self):
		return int(self.text.index('end-1c').split('.')[0])-1

	def adjust_height(self):
		self.configure(height=self.nlines())

	def clear_text(self):
		self.enable()
		self.text.delete("1.0", tk.END)
		self.disable()

	def get_text(self):
		return self.text.get("1.0", tk.END).strip()

	def set_text(self, text):
		self.clear_text()
		self.add_text(text)

	def set_json(self, dct, indent=2):
		self.set_text(json.dumps(dct, indent=indent))

	def set_dict(self, dct, prefix="", delim=": ", suffix="\n"):
		self.clear_text()
		for k,v in dct.items():
			self.add_text(prefix+k+delim+str(v)+suffix)

	def add_text(self, text, tag=None):
		self.enable()
		self.text.insert(tk.END, text, tag)
		self.disable()

	def add_clickable_text(self, text, tag,
			font='Arial 9', color='#333',
			command=None):
		self.add_text(text, tag)
		self.tag_bind(tag, '<Leave>',
			lambda e: self.text.config(cursor=''))
		self.tag_bind(tag, '<Enter>',
			lambda e: self.text.config(cursor='hand2'))
		self.tag_bind(tag, '<Button-1>', command)
		self.text.tag_configure(tag, foreground=color)
		self.text.tag_configure(tag, font=font)

	def add_colored(self, tag, text, font, color):
		self.add_text(text, tag)
		self.text.tag_configure(tag, foreground=color)
		self.text.tag_configure(tag, font=font)

	def tag_bind(self, tag_name, event, func):
		self.text.tag_bind(tag_name, event, func, add='+')

	def tag_config(self, *a, **kw):
		self.text.tag_config(*a, **kw)

	def enable(self):
		if self.disabled:
			self.text.configure(state=tk.NORMAL)
	def disable(self):
		if self.disabled:
			self.text.configure(state=tk.DISABLED)



class ButtonLabel(tk.Label):
	"""
	Clickable button label.
	"""
	def __init__(self, parent,
			on_click=None,
			hover_font = 'Arial 8 bold',
			hover_fg = '#f00',
			hover_bg = '#ddd',
			border_fg = None,
			hover_border_fg = None,
			*args, **kwargs):

		super().__init__(parent, cursor='hand2',
				anchor="w", justify="left",
				*args, **kwargs)
		self.on_click = on_click
		self.enabled  = False
		self.blocked  = False

		self.conf_leave = {
			"fg"   : self.cget('fg'),
			"bg"   : self.cget('bg'),
			"font" : self.cget('font')
		}
		self.conf_enter = {
			"fg"   : hover_fg,
			"bg"   : hover_bg,
			"font" : self.conf_leave['font'] if border_fg else hover_font
		}

		if border_fg:
			self.configure(highlightthickness=1)
			self.conf_enter['highlightbackground'] = hover_border_fg
			self.conf_leave['highlightbackground'] = border_fg

		self.configure(**self.conf_leave)

		self.bind('<Button-1>', self._on_click)
		self.bind('<Enter>', self._on_enter)
		self.bind('<Leave>', self._on_leave)

	def enable(self):
		if not self.blocked:
			self._on_enter()
			self.enabled = True

	def disable(self):
		if not self.blocked:
			self.enabled = False
			self._on_leave()

	def block(self, block=True):
		self.blocked = block
		self.configure(state="disabled" if block else "normal",
				cursor="left_ptr" if block else "hand2")

	def _on_click(self, ev):
		if self.on_click and not self.blocked:
			self.on_click()

	def _on_enter(self, ev=None):
		if not self.enabled and not self.blocked:
			self.configure(**self.conf_enter)
	def _on_leave(self, ev=None):
		if not self.enabled and not self.blocked:
			self.configure(**self.conf_leave)


class Tablist(tk.Frame):
	"""
	Frame with clickable tabs (ButtonLabel's).

	Example:
		btns = {
			'tab_1' : ('Start', lambda:self.open_tab('tab_1')),
			'tab_2' : ('Open', lambda:self.open_tab('tab_2')),
			'tab_3' : ('Exit', lambda:self.open_tab('tab_3'))
		}
		tabs = TabList(self, btns, ...)
		...
		tabs.enable('tab_1')
		...
	"""
	def __init__(self, parent, btns,
			font='Arial 10', font_hover='Arial 10 bold',
			fg='#222', fg_hover='#f00',
			bg='#ddd', bg_hover='#ddd',
			border_fg=None, hover_border_fg=None,
			*args, **kwargs):
		super().__init__(parent, background=bg, *args, **kwargs)
		self.tabs = {}
		self.enabled_tab = ""
		self.border_fg = border_fg
		x = 0
		for key,btn in btns.items():
			self.tabs[key] = ButtonLabel(self,
					on_click=btn[1], text=btn[0],
					fg=fg, hover_fg=fg_hover,
					bg=bg, hover_bg=bg_hover,
					font=font, hover_font=font_hover,
					border_fg=border_fg,
					hover_border_fg=hover_border_fg)
			self.tabs[key].grid(row=0, column=x, sticky='nswe')
			x += 1

		self.grid_columnconfigure(x, weight=1)

	def block(self, name, on=True):
		if name in self.tabs:
			self.tabs[name].block(on)

	def block_all(self, on=True):
		for btn in self.tabs.values():
			btn.block(on)

	def is_enabled(self, name):
		if name in self.tabs:
			return self.tabs[name].enabled
		return False

	def enable(self, name):
		for nam,tab in self.tabs.items():
			if name == nam:
				tab.enable()
				self.enabled_tab = name
			else:	tab.disable()
	def disable(self, name):
		if name in self.tabs:
			self.tabs[name].enabled = False
			if self.enabled_tab == name:
				self.enabled_tab = ""

'''
class ImageButton(tk.Label):
	"""\
	Button with an image, implemented using a tk.Label.
	"""
	def __init__(self, parent, img_path, background_hover='#0c0',
			width=30, height=30, command=None, *args, **kwargs):
		super().__init__(parent, cursor='hand1', *args, **kwargs)

		self.command = command
		self.background_normal = self.cget('bg')
		self.background_hover  = background_hover
		self.img = ImageTk.PhotoImage(Image.open(img_path).resize((width,height)))
		self.config(image=self.img, height=height, width=width)

		self.bind('<Button-1>', self.on_click)
		self.bind('<Enter>', self.on_enter)
		self.bind('<Leave>', self.on_leave)

	def on_enter(self, event=None):
		self.config(background=self.background_hover)

	def on_leave(self, event=None):
		self.config(background=self.background_normal)

	def on_click(self, event=None):
		if self.command:
			self.command()
'''


class ToolTip(object):
	"""\
	Gives a Tkinter widget a tooltip as the mouse is above the widget
	tested with Python27 and Python34  by  vegaseat  09sep2014
	www.daniweb.com/programming/software-development/code/484591/a-tooltip-class-for-tkinter

	Modified to include a delay time by Victor Zaccardo, 25mar16
	Modified that widget leave and enter events are handled by Lukas Wiese 5apr23

	IMPORTANT:
	  If widget is already bound to <Enter> or <Leave> it MUST
	  provide the methods .on_enter() and .on_leave(). Otherwise
	  it won't work since the according event only occures once.
	"""
	def __init__(self, widget, text='widget info'):
		self.waittime   = 400	#miliseconds
		self.wraplength = 180	#pixels
		self.widget     = widget
		self.text       = text
		self.widget.bind("<Enter>", self.enter)
		self.widget.bind("<Leave>", self.leave)
		self.widget.bind("<ButtonPress>", self.leave)
		self.id = None
		self.tw = None

	def enter(self, event=None):
		if callable(getattr(self.widget, 'on_enter', None)):
			self.widget.on_enter()
		self.schedule()

	def leave(self, event=None):
		if callable(getattr(self.widget, 'on_leave', None)):
			self.widget.on_leave()
		self.unschedule()
		self.hidetip()

	def schedule(self):
		self.unschedule()
		self.id = self.widget.after(self.waittime, self.showtip)

	def unschedule(self):
		id = self.id
		self.id = None
		if id:
			self.widget.after_cancel(id)

	def showtip(self, event=None):
		x = y = 0
		x, y, cx, cy = self.widget.bbox("insert")
		x += self.widget.winfo_rootx() + 25
		y += self.widget.winfo_rooty() + 20
		# creates a toplevel window
		self.tw = tk.Toplevel(self.widget)
		# Leaves only the label and removes the app window
		self.tw.wm_overrideredirect(True)
		self.tw.wm_geometry("+%d+%d" % (x, y))
		label = tk.Label(self.tw, text=self.text, justify='left',
				background="#ffffff", relief='solid', borderwidth=1)
#				wraplength = self.wraplength)
		label.pack(ipadx=1)

	def hidetip(self):
		tw = self.tw
		self.tw= None
		if tw: tw.destroy()



class ScrollFrame(tk.Frame):
	"""
	Frame that can be scrolled.
	"""
	def __init__(self, parent, *args, **kw):
		tk.Frame.__init__(self, parent, *args, **kw)

		# Create a canvas object and a vertical scrollbar for scrolling it.
		vscrollbar = ttk.Scrollbar(self, orient=VERTICAL)
		vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
		self.canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                                width = 200, height = 300,
                                yscrollcommand=vscrollbar.set,
				yscrollincrement=1)
		self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
		vscrollbar.config(command = self.canvas.yview)

		if 'background' in kw:
			self.canvas.configure(bg=kw['background'])

		# Reset the view
		self.canvas.xview_moveto(0)
		self.canvas.yview_moveto(0)

		# Create a frame inside the canvas which will be scrolled with it.
		self.interior = tk.Frame(self.canvas, *args, **kw)
		self.interior.bind('<Configure>', self._configure_interior)
		self.canvas.bind('<Configure>', self._configure_canvas)
		self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor=NW)
		self.bind_scroll_events()

	def bind_scroll_events(self):
		self.id_4 = self.interior.bind_all("<Button-4>", lambda e: self.scroll(True, 20))
		self.id_5 = self.interior.bind_all("<Button-5>", lambda e: self.scroll(False, 20))

	def unbind_scroll_events(self):
		self.interior.unbind("<Button-4>", self.id_4)
		self.interior.unbind("<Button-5>", self.id_5)

	def scroll(self, up=True, speed=10):
		if up: speed *= -1
		self.canvas.focus_set()
		self.canvas.yview_scroll(speed, "units")

	def _configure_interior(self, event):
		# Update the scrollbars to match the size of the inner frame.
		size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
		self.canvas.config(scrollregion=(0, 0, size[0], size[1]))
		if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
			# Update the canvas's width to fit the inner frame.
			self.canvas.config(width = self.interior.winfo_reqwidth())

	def _configure_canvas(self, event):
		if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
			# Update the inner frame's width to fill the canvas.
			self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())


class ButtonFrame(tk.Frame):
	"""
	A frame with buttons.
	The buttons can either be tk.Buttons or widgets.ButtonLabel's.
	"""
	def __init__(self, parent, btn_dict,
			style='button', font='Arial 8', bg='#ddd', border_fg=None,
			btn_fg='#333', btn_fg_hover='#555', btn_font='Arial 8',
			btn_bg='#ddd', btn_bg_hover='#e9e9e9', align='left',
			btn_border_fg=None, btn_border_hover_fg=None,
			btn_pady=2, btn_padx=2):
		"""
		Args:
		  parent:   Parent widget
		  btn_dict: A dictionary holding button infos (key=text, value=command)
		  font:     Button font
		  bg:       Frame background color
		"""
		super().__init__(parent, background=bg)

		if border_fg:
			self.configure(highlightthickness=1,
				highlightbackground=border_fg)
		col = 1
		self.btns = []

		for title, cmd in btn_dict.items():
			if style == 'button':
				btn = tk.Button(self, text=title, command=cmd, font=font,
						highlightthickness=0)
			elif style == 'label':
				btn = ButtonLabel(self, text=title, on_click=cmd,
						font=btn_font,
						fg=btn_fg, hover_fg=btn_fg_hover,
						bg=btn_bg, hover_bg=btn_bg_hover,
						border_fg=btn_border_fg,
						hover_border_fg=btn_border_hover_fg)
				self.btns.append(btn)
			else:	continue
			btn.grid(row=0, column=col, sticky='we',
				pady=btn_pady, padx=btn_padx)
			col += 1

		if align == 'right':
			self.grid_columnconfigure(0, weight=1)
		elif align == 'center':
			self.grid_columnconfigure((0, col), weight=1)

	def set_tooltip(self, index, tooltip):
		if index >= 0 and index < len(self.btns):
			ToolTip(self.btns[index], tooltip)

	def block(self, block=True):
		for btn in self.btns:
			btn.block(block)

class MultiEntry(tk.Frame):
	"""
	Frame with an entry widget.
	The entry widget can either be a text area, a single-line entry
	or a dropdownmenu. Parameters are 'text', 'entry' and 'options'.

	+-------------------------------+
	| Text/Entry/Combobox		|
	+-------------------------------+

	"""
	def __init__(self, parent, style, options=None,
				height=None, width=None):
		"""
		Args:
		  parent:	Parent widget
		  style:	Entry style ('text', 'entry', 'options')
		  options: 	If style is 'options' pass list with options here.
		"""
		super().__init__(parent, background='#dfdfdf')
		self.parent = parent
		self.style  = style
		self.opts   = options if options else []
		self.title  = None
		self.w      = None
		self._setup_gui(height, width)

	def set_title(self, titleframe):
		"""
		Set given widget as title.
		"""
		self.title = titleframe
		self.title.grid(row=0, column=0, sticky='nswe', padx=1)

	def set_border(self, color='#e00', nseconds=None):
		"""
		Set a 1px colored border around the MultiEntry frame.
		"""
		self.configure(highlightthickness=1,
				highlightbackground=color,
				highlightcolor=color)

		if nseconds:
			self.after(nseconds*1000,
				lambda:self.configure(highlightthickness=0))

	def get_type(self):
		"""
		Get type of entry content.
		Returns:
		  integer
		  decimal
		  boolean
		  string
		  UNKNOWN
		  None if no/invalid content
		"""
		s = self.get()
		if not s: return None

		if s.isnumeric():
			return "integer"
		elif s in ('true', 'false', 'True', 'False'):
			return "boolean"
		elif s[0].isalpha():
			return "string"
		else:
			try:
				x = float(s)
				return "decimal"
			except:	return "string"
		return "string"


	def _setup_gui(self, height, width):

		self.grid_columnconfigure(0, weight=1)

		# Entry widget (tk.Text, tk.Entry or tk.Listbox)
		self.vVal  = tk.StringVar(self)
		self.vVal.set("")

		if self.style == 'text':
			self.w = tk.Text(self, height=height, width=width,
					insertbackground='#222')
		elif self.style == 'options':
			self.w = ttk.Combobox(self, textvariable=self.vVal,
					values=self.opts)
		elif self.style == 'entry':
			self.w = tk.Entry(self, width=width,
					textvariable=self.vVal,
					insertbackground='#222')
		grid = {"sticky":'wnse'}
		if self.style != "entry":
			grid["padx"] = (1,0)
			grid["pady"] = (1,0)
		self.w.grid(row=1, column=0, **grid)

		# Popup menu
		self._setup_popup_menu()

	def get(self):
		if self.style == 'text':
			return self.w.get("1.0", tk.END).strip()
		elif self.style == 'entry':
			return self.vVal.get().strip()
		elif self.style == 'options':
			return self.vVal.get().strip()

	def set(self, value):
		if self.style == 'text':
			self.w.delete("1.0", tk.END)
			self.w.insert(tk.END, value)
		elif self.style == 'entry':
			self.vVal.set(value)
		elif self.style == 'options':
			self.vVal.set(value)

	def clear(self):
		if self.style == 'text':
			self.w.delete("1.0", tk.END)
		elif self.style == 'entry':
			self.vVal.set("")
		elif self.style == 'options':
			self.vVal.set("")

	def _setup_popup_menu(self):
		items = {}
		items['copy']  = lambda: pyperclip.copy(self.get())
		if self.style != 'options':
			items['paste'] = lambda: self.set(pyperclip.paste())
		items['clear'] = lambda: self.clear()
		PopupMenu(self.w, items)


class LabeledTextFrame(tk.Frame):
	"""
	+---------------+
	| Title		|
	+---------------+
	| Text		|
	|		|
	|		|
	+---------------+
	"""
	def __init__(self, parent, title,
			lbl_font='Arial 8 bold', lbl_fg='#333', lbl_bg='#dfdfdf',
			txt_font='Monospace 9', txt_fg='#eee', txt_bg='#292929',
			txt_height=None):
		super().__init__(parent, background=lbl_bg)
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)
		self.label = LeftLabel(self, text=" "+title, bg=lbl_bg,
				font=lbl_font, fg=lbl_fg)
		self.label.grid(row=0, column=0, sticky='nswe', ipadx=3)

		self.text = ScrollTextFrame(self, disabled=True,
				scroll_vertical=False, scroll_horizontal=False,
				height=txt_height, font=txt_font,
				bg=txt_bg, fg=txt_fg, relief='flat', padx=2)
		self.text_bg = self.text.text['bg']
		self.text_fg = self.text.text['fg']
		self.text.grid(row=1, column=0, sticky='nswe', ipadx=2)
		menu_items = {'copy': lambda:pyperclip.copy(self.text.get_text())}
		PopupMenu(self.text, menu_items)

	def block(self, block=True):
		bg = '#ccc' if block else self.text_bg
		fg = '#a0a0a0' if block else self.text_fg
		self.label.configure(state="disabled" if block else "normal")
		self.text.configure(bg=bg, fg=fg)




class TextStyler:
	"""
	This class is used to set highlighted JSON/XML
	in text area.
	Example:
		text = ScrollTextFrame(self, ...)
		TextStyler(text).set_json(json_dict)
	"""
	def __init__(self, text:ScrollTextFrame, adjust_text_height=False):
		self.text = text
		self.adjust_text_height = adjust_text_height
		self.text_fg = text.text['fg']
		self.text_bg = text.text['bg']
		self.colors = {}

		self.set_colors({
			'key'         : '#e65c00',
			'value'       : '#d580ff',
			'json_key'    : '#ebebe0',
			'json_string' : '#5cd65c',
			'json_int'    : '#ff3333',
			'json_bool'   : '#0099ff',
			'json_none'   : '#0066cc',
			'xml_tag'     : '#0099ff',
			'xml_values'  : '#e6ffff',
			'xml_header'  : '#d00'
		})

	# Set JSON
	def set_json(self, dct, is_array=False, clear_before=True):
		if clear_before: self.text.clear_text()
		if is_array:
			self.text.add_text("[\n")
			self._add_json_dict(dct, 4)
			self.add_text("]\n")
		else:	self._add_json_dict(dct, 2)
		self._auto_adjust_text_height()

	# Set XML
	def set_xml(self, name, dct,
			hdr='<?xml version="1.0" encoding="UTF-8"?>',
			clear_before=True):
		if clear_before: self.text.clear_text()
		self.text.add_text(hdr + "\n", 'xml_header')
		self._add_xml_dict(name, dct)
		self._auto_adjust_text_height()

	# Set colored dictionary as key-value pairs
	def set_dict(self, dct, clear_before=True):
		if clear_before: self.text.clear_text()
		for k,v in dct.items():
			self.text.add_text(k, 'key')
			self.text.add_text(': ')
			self.text.add_text(v, 'value')
			self.text.add_text('\n')

	# Set tag colors
	def set_colors(self, color_dict):
		for k,v in color_dict.items():
			self.text.tag_config(k, foreground=v)
		self.colors = color_dict

	def block(self, block=True):
		bg = '#ccc' if block else self.text_bg
		fg = '#a0a0a0' if block else self.text_fg
		self.text.configure(bg=bg, fg=fg)
		for k,v in self.colors.items():
			fg = '#a0a0a0' if block else v
			self.text.tag_config(k, foreground=fg)


	def _auto_adjust_text_height(self):
		if self.adjust_text_height:
			self.text.adjust_height()

	def _add_indented(self, s, indent, nl=False, tag=None):
		end = "\n" if nl else ""
		self.text.add_text(" "*indent + s + end, tag)

	def _add_lineend(self, comma=False):
		if comma: self.text.add_text(",")
		self.text.add_text("\n")

	#
	# JSON printing
	#
	def _add_json_value(self, val, indent=0, comma=False):
		self._add_indented("", indent)
		if type(val) == str:
			self.text.add_text('"{}"'.format(val), 'json_string')
		elif type(val) in (int,float):
			self.text.add_text("{}".format(val), 'json_int')
		elif type(val) == bool:
			self.text.add_text("{}".format('true' if val else 'false'), 'json_bool')
		elif val == None:
			self.text.add_text("null", 'json_none')

		self._add_lineend(comma)

	def _add_json_list(self, l, start_indent=0, indent=2,
				end_indent=0, comma=False):
		self._add_indented("[", start_indent, True)

		for i,item in enumerate(l):
			not_last = True if i < len(l)-1 else False
			if type(item) == dict:
				self._add_indented("", indent)
				self._add_json_dict(item, indent+2, not_last)
			elif type(item) == list:
				self._add_json_list(item, end_indent+2,
					indent+2, end_indent+2, not_last)
			else:	self._add_json_value(item, indent, not_last)

		self._add_indented("]", end_indent)
		self._add_lineend(comma)

	def _add_json_dict(self, d, indent=2, comma=False):
		self._add_indented("{\n", indent-2)

		for i,kv in enumerate(d.items()):
			k = kv[0]; v = kv[1]
			not_last = True if i<len(d)-1 else False
			self._add_indented("", indent)
			self.text.add_text('"{}"'.format(k), 'json_key')
			self.text.add_text(' : ')
			if type(v) == list:
				self._add_json_list(v, 0, indent+2, indent, not_last)
			elif type(v) == dict:
				self._add_json_dict(v, indent+2, not_last)
			else:	self._add_json_value(v, 0, not_last)

		self._add_indented("}", indent-2)
		self._add_lineend(comma)

	#
	# XML printing
	#
	def _add_xml_value(self, key, v, indent):
		self._add_indented("", indent)
		self.text.add_text("<" + key + ">", 'xml_tag')
		self.text.add_text(v, 'xml_value')
		self.text.add_text("</" + key + ">\n", 'xml_tag')

	def _add_xml_list(self, key, d, indent):
		self._add_indented("<"+key+">", indent, True, 'xml_tag')
		k = key+"It"
		for v in d:
			if type(v) in (str,int,float,bool):
				self._add_xml_value(k, v, indent+2)
			elif type(v) in (list,tuple):
				self._add_xml_list(k, v, indent+2)
			elif type(v) == dict:
				self._add_xml_dict(k, v, indent+2)
		self._add_indented("</"+key+">", indent, True, 'xml_tag')

	def _add_xml_dict(self, key, d, indent=0):
		self._add_indented("<"+key+">", indent, True, 'xml_tag')
		for k,v in d.items():
			if type(v) in (str,int,float,bool):
				self._add_xml_value(k, v, indent+2)
			elif type(v) in (list,tuple):
				self._add_xml_list(k, v, indent+2)
			elif type(v) == dict:
				self._add_xml_dict(k, v, indent+2)
		self._add_indented("</"+key+">", indent, True, 'xml_tag')



class PopupMenu(tk.Menu):
	def __init__(self, parent, items, bind_to=None):
		"""
		Args:
		  parent: Parent widget
		  items:  Dictionary with menu items where the
			  key is the label text and the value
			  is the function to execute on click.
			  Example:
				items = {
				  'new' : lambda: print("New"),
				  'copy' : lambda: print("Copy")
				}
				PopupMenu(self, items)
		  bind_to: List with widgets when the popupmenu shall
			   be bound to.
		"""
		super().__init__(parent, tearoff=0)
		self.parent = parent
		parent.bind("<Button-3>", self._open, add='+')

		for lbl,fnc in items.items():
			self.add_command(label=lbl, command=fnc)

		if bind_to != None:
			for w in bind_to:
				w.bind("<Button-3>", self._open, add='+')

	def _open(self, event):
		self.tk_popup(event.x_root, event.y_root)

