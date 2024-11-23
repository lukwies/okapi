from tkinter import ttk
from widgets import LeftLabel

ENDPOINT_BG = "#eee"

# Message label colors
MSG_BG     = '#999'
MSG_COLORS = ['#222', '#e00', '#0ee']

"""
Label for entry widgets.
"""
ENTRY_LBL_STYLE = {'font':'Arial 8 bold', 'fg':'#222'}
#ENTRY_LBL_GRID = {'padx':3, 'sticky':'nswe'}
class EntryLabel(LeftLabel):
	def __init__(self, parent, text):
		super().__init__(parent, text=text, **ENTRY_LBL_STYLE)
	def do_grid(self, row, column, padx=3, sticky='nswe', *a, **kw):
		self.grid(row=row, column=column, padx=padx,
			sticky=sticky, *a, **kw)

# Infolabel
class InfoLabel(LeftLabel):
	def __init__(self, parent, text, font_size=9, bg="#eee"):
		super().__init__(parent, text=text, fg='#555', bg=bg,
				font="Arial {}".format(font_size))
	def do_grid(self, row, column, sticky='nswe', *a, **kw):
		self.grid(row=row, column=column, sticky=sticky, *a, **kw)

# Table header label
class TableHeader(LeftLabel):
	def __init__(self, parent, text, font="Arial 9",
			fg="#666", bg=ENDPOINT_BG, *a, **kw):
		super().__init__(parent, text=text, font=font,
				fg=fg, bg=bg, *a, **kw)
	def do_grid(self, row, column, sticky='nswe',
			 padx=(0,30), pady=(5,0), *a, **kw):
		self.grid(row=row, column=column, sticky=sticky,
			padx=padx, pady=pady, *a, **kw)

# Small table header label
class SmallTableHeader(LeftLabel):
	def __init__(self, parent, text, font="Arial 8",
			fg="#555", *a, **kw):
		super().__init__(parent, text=text, font=font,
				fg=fg, *a, **kw)
	def do_grid(self, row, column, sticky='nswe', padx=(0,20),
			pady=(4,0), *a, **kw):
		self.grid(row=row, column=column, sticky=sticky,
			padx=padx, pady=pady, *a, **kw)
