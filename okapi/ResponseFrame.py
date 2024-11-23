import tkinter as tk
from tkinter.ttk import Progressbar
import threading
import requests
from urllib.parse import urlparse

from widgets import ScrollTextFrame
from widgets import LeftLabel
from widgets import TextStyler

import DOC as doc

"""
|---------------------------------------|	|---------------|
| Response (0.0034 sec)			| 0	| Headers	|
|---------------------------------------|	|		|
| 200 OK  (application/xml)  2351 byte	| 1	|		|
|---------------------------------------|	|		|
| <foo>					| 2	|		|
|   <bar>1</bar>			|	|---------------|
|   <baz>4</baz>			|	|		|
|					|	|		|
|   <bazi>				|	|		|
|     <fozi>hello wolrd</fozi>		|	|		|
|     <fazi>god bless you</fazi>	|	|		|
|---------------------------------------|	|---------------|
"""

class ResponseFrame(tk.Frame):

	def __init__(self, parent, msg_func):
		super().__init__(parent)
		self.parent = parent
		self.msg = msg_func
		self._setup_gui()


	def request(self, method, url, data=None, headers=None, auth=None):
		"""
		Called when 'send' button has been pressed.
		Collects all data needed for a request (from gui)
		and starts the request thread.
		"""
		self.clear()
		thread = _HTTPSendRecvThread(self, self.msg, method,
				url, data, headers, auth)
		thread.start()

	def set_response(self, resp, method, url):
		"""
		Display request header, response header and response body
		in according text fields.
		Args:
		  resp: The response (requests.Response)
		"""
		self.clear()
		self.fTitle.set_elapsed_time(resp)
		self.fStatus.set_status(resp)
		self.fStatus.set_method_and_url(method, url)
		self.fStatus.grid(row=1, column=0, sticky='nswe')
		self.fHeaders.set_headers(resp)
		self.fBody.set_body(resp)

	def clear(self, ev=None):
		self.fTitle.clear()
		self.fStatus.clear()
		self.fStatus.grid_remove()
		self.fBody.clear_text()
		self.fHeaders.clear()

	def _setup_gui(self):
		self.grid_rowconfigure(2, weight=1)
		self.grid_columnconfigure(0, weight=1) #, minsize=200)

		self.fTitle    = _TitleFrame(self)
		self.fStatus   = _StatusFrame(self)
		self.fBody     = _BodyFrame(self)
		self.fHeaders  = _HeaderFrame(self)

		self.fTitle.grid(row=0, column=0, sticky='nswe')
		self.fBody.grid(row=2, column=0, sticky='nswe')
		self.fHeaders.grid(row=0, column=1, rowspan=3, sticky='nswe')

	"""
	def save_response(self, ev=None):
		txt = self.txtRespBody.get_text()
		if not txt:
			self.okapi.set_msg("Nothing to save !", 4, "#e00")
		else:
			filename = asksaveasfile()
			print("TODO: Save as ", end="")
			print(filename)
	"""

							



class _TitleFrame(tk.Frame):
	"""
	Title frame ("Response  0.0012 sec)"
	"""
	def __init__(self, parent):
		super().__init__(parent, background="#666",
				highlightthickness=1,
				highlightcolor="#696969")
		self._setup_gui()

	def set_elapsed_time(self, resp:requests.Response):
		t = resp.elapsed.total_seconds()
		self.lTime['text'] = "(" + str(t) + " sec)"

	def clear(self):
		self.lTime['text'] = ""

	def _setup_gui(self):
		self.grid_columnconfigure(10, weight=1)
		# "Response"
		LeftLabel(self, text=" Response", font="monospace 10",
				fg="#ddd", bg="#666")\
			.grid(row=0, column=0, sticky='nswe')
#			fg="#f5f5f5", bg="#666")\
		# Elapsed time
		self.lTime = tk.Label(self, font="Verdana 8",
			fg="#f0f0f0", bg="#666")
		self.lTime.grid(row=0, column=1, sticky='nswe', padx=5)


class _StatusFrame(tk.Frame):
	"""
	Frame to show status code, content type and content length.

	 0      1    2                  3             4
	|-------------------------------------------------|
	| 200 | Ok | application/json | (3023 byte) | ... |
	|-------------------------------------------------|
	"""
	BG = "#d2d2d2"
	def __init__(self, parent):
		super().__init__(parent, background=self.BG)
		self._setup_gui()

	def set_method_and_url(self, method, url):
		self.lMethod['text'] = method
		self.lUri['text'] = url

	def set_status(self, resp:requests.Response):
		self.lCode['text'] = str(resp.status_code)
		self.lReason['text'] = resp.reason
		if 'content-type' in resp.headers:
			self.lType['text'] = resp.headers['content-type']

		if 'content-length' in resp.headers:
			self.lLength['text'] = "("+resp.headers['content-length']+")"

	def clear(self):
		self.lMethod['text'] = ""
		self.lUri['text']    = ""
		self.lCode['text']   = ""
		self.lReason['text'] = ""
		self.lLength['text'] = ""
		self.lType['text']   = ""

	def _setup_gui(self):
		# Request info (method + url)
		self.fReqInfo = tk.Frame(self, background="#aaa")
		self.fReqInfo.grid(row=0, column=0, sticky='nswe',
				columnspan=5, padx=1)
		self.lMethod = LeftLabel(self.fReqInfo, font="Verdana 9 bold",
					fg="#222", bg="#aaa")
		self.lMethod.grid(row=0, column=0, sticky='nswe', padx=(3,0))
		self.lUri = LeftLabel(self.fReqInfo, font="Verdana 9",
					fg="#222", bg="#aaa")
		self.lUri.grid(row=0, column=1, sticky='nswe', padx=(3,0))

		self.grid_columnconfigure(3, weight=1)
		# Status code
		self.lCode = LeftLabel(self, font="Verdana 9 bold",
			fg="#222", bg=self.BG)
		self.lCode.grid(row=1, column=0, sticky='nswe', padx=(3,0))
		# Status message
		self.lReason = LeftLabel(self, font="Verdana 9",
			fg="#444", bg=self.BG)
		self.lReason.grid(row=1, column=1, sticky='nswe', padx=(3,0))
		# Content-Length
		self.lLength = LeftLabel(self, font="monospace 8",
			fg="#666", bg=self.BG)
		self.lLength.grid(row=1, column=2, sticky='nswe', padx=3)
		# Content-Type
		self.lType = LeftLabel(self, font="monospace 8",
			fg="#004d00", bg=self.BG)
		self.lType.grid(row=1, column=4, sticky='nswe', padx=3)

class _BodyFrame(ScrollTextFrame):
	"""
	Frame where the response body is shown.
	"""
	def __init__(self, parent):
		super().__init__(parent, disabled=True, bg='#292929', fg='#eee')
		self.styler = TextStyler(self)

	def set_body(self, resp:requests.Response):
		if 'content-type' in resp.headers:
			ctype = resp.headers['content-type']

			if 'json' in ctype:
				self.styler.set_json(resp.json())
			elif 'xml' in ctype:
				self.styler.set_xml(resp.json())
			else:	self.text_text(resp.content)

	def clear(self):
		self.clear_text()


class _HeaderFrame(tk.Frame):
	BG = "#c0c0c0"
	TBG= "#292929"
	def __init__(self, parent):
		super().__init__(parent, background=self.BG)
		self._setup_gui()

	def set_headers(self, resp:requests.Response):
		"""
		Set headers from given response.
		"""
		# Set response header
		self.tResp.clear_text()
		self.tResp.add_colored('r0', str(resp.status_code)+" ","monospace 10", '#ccc')
		self.tResp.add_colored('r1', resp.reason+"\n","monospace 10", '#bbb')
		TextStyler(self.tResp).set_dict(resp.headers, False)

		# Set request header
		self.tReq.clear_text()
		parsed = urlparse(resp.request.url)

		self.tReq.add_colored('t0', resp.request.method+" ", "monospace 10", '#ccc')
		self.tReq.add_colored('t1', parsed.netloc+"\n", "monospace 10", '#bbb')
		TextStyler(self.tReq).set_dict(resp.request.headers, False)

		if resp.request.body:
			self.tReq.add_colored('t2', "\n" + resp.request.body,
				'Verdana 8', '#d0d0d0')
	def clear(self):
		self.tResp.clear_text()
		self.tReq.clear_text()

	def _setup_gui(self):
#		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(2, weight=2)
		self.grid_rowconfigure(2, minsize=100)
		self.grid_rowconfigure(4, weight=1)

		# Title ("Headers")
		LeftLabel(self, text=" Headers", font="monospace 10",
				fg="#ddd", bg="#666",
				highlightthickness=1,
				highlightcolor="#7a7a7a")\
			.grid(row=0, column=0, sticky='nswe')

		tconf = {"font":"monospace 9", "bg":self.TBG, "fg":"#444",
			"width":50}
		lconf = {"font":"Verdana 9", "bg":"#c9c9c9", "fg":"#333"}
		# Response
		LeftLabel(self, text=" Response", **lconf)\
			.grid(row=1, column=0, sticky='nswe')
		self.tResp = ScrollTextFrame(self, **tconf)
		self.tResp.grid(row=2, column=0, sticky='nswe')
		# Request
		LeftLabel(self, text=" Request", **lconf)\
			.grid(row=3, column=0, sticky='nswe')
		self.tReq = ScrollTextFrame(self, **tconf)
		self.tReq.grid(row=4, column=0, sticky='nswe')


class _HTTPSendRecvThread(threading.Thread):
	"""
	Thread for sending the request and
	receiving the response.
	"""
	def __init__(self, parent, msg_func, method, url,
			data, hdrs, auth):
		super().__init__()
		self.parent = parent
		self.msg    = msg_func
		self.method = method
		self.url    = url
		self.data   = data
		self.hdrs   = hdrs
		self.auth   = auth

		self.pbar = Progressbar(self.parent, orient='horizontal',
			mode='indeterminate', length=200)
		self.pbar.grid(row=3, column=0, sticky='we', columnspan=2)

	def run(self):
		print(". starting request ...")
		print(self.method, " ", self.url)

		self.pbar.start()
		try:
			resp = requests.request(
				self.method,
				self.url,
				data=self.data,
				headers=self.hdrs,
				auth=self.auth,
				timeout=5)
			self.parent.set_response(resp, self.method, self.url)

		except requests.exceptions.RequestException as e:
			self.msg(str(e), 1)
			print("Failed to request '" + self.url + "'", end="\n > ")
			print(e)

		self.pbar.grid_remove()








