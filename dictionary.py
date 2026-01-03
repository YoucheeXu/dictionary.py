#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os, shutil
sys.dont_write_bytecode = True
import time
import base64
import threading
import json

import urllib.request
import urllib.error

from tkinter import filedialog
import tkinter as tk
import tkinter.messagebox as msgBox

from cefpython3 import cefpython as cef

from AuidoArchive import AuidoArchive
from GDictBase import GDictBase
from SDictBase import SDictBase
from MDictBase import MDictBase
from globalVars import *
from utils import *
from DatumContainer import Queue, Stack


# Fix for PyCharm hints warnings
WindowUtils = cef.WindowUtils()

# Constants
# Tk 8.5 doesn't support png images
IMAGE_EXT = ".png" if tk.TkVersion > 8.5 else ".gif"

class MainFrame(tk.Frame):

	def __init__(self):

		self.__enableMove = False
		self.__winOK = False
		self.__bNormWindow = False

	def Create(self, width, height, showHiRatio, showWiRatio):

		# Root
		self.__root = tk.Tk()

		tk.Grid.rowconfigure(self.__root, 0, weight = 1)
		tk.Grid.columnconfigure(self.__root, 0, weight = 1)

		# MainFrame
		tk.Frame.__init__(self, self.__root)
		# self.__root.tk.call('tk', 'scaling', 1.25/75)

		# To-Do
		DPI_scaling = self.__getDPI()
		width *= DPI_scaling
		height *= DPI_scaling
		self.master.title("Dictionary")
		self.master.protocol("WM_DELETE_WINDOW", self.__on_close)
		# self.bind("<Destroy>", self.__destory)
		self.bind("<Configure>", self.__on_configure)
		self.master.bind("<Configure>", self.__on_root_configure)
		self.__root.bind("<Unmap>", self.__on_unmap)
		self.__root.bind("<Map>", self.__on_map)

		# BrowserFrame
		self.__browser_frame = BrowserFrame(self)
		self.__browser_frame.grid(row = 1, column = 0,
								 sticky = (tk.N + tk.S + tk.E + tk.W))
		tk.Grid.rowconfigure(self, 1, weight = 1)
		tk.Grid.columnconfigure(self, 0, weight = 1)

		# Pack MainFrame
		self.pack(fill = tk.BOTH, expand = tk.YES)

		screenwidth = self.__root.winfo_screenwidth()
		screenheight = self.__root.winfo_screenheight()
		size = '%dx%d+%d+%d' % (width, height, screenwidth * showWiRatio - width/2, screenheight * showHiRatio - height/2)

		gLogger.info("size: %s" %size)

		self.__root.geometry(size)
		self.__root.resizable(height = None, width = None)
		# self.__root.update_idletasks()

		self.__no_title()

		self.__setup_icon()
		self.__root.wm_attributes('-topmost', True)

		self.__winOK = True

	def __getDPI(self):
		if IsWindows():
			from ctypes import windll
			hDC = windll.user32.GetDC(0)
			LOGPIXELSX = 88
			dpi = windll.gdi32.GetDeviceCaps(hDC, LOGPIXELSX)/96
			gLogger.info("DPI is %f" %dpi)
			return dpi
		elif IsLinux():
			return 1.256

	def navigate(self, url):
		self.__browser_frame.navigate(url)

	def __no_title(self):

		if IsWindows():
			self.__root.overrideredirect(True)	#no title
			self.__root.after(10, lambda: self.__set_appwindow())
		elif IsLinux():
			self.__root.wm_attributes('-type', 'splash')

	def __set_appwindow(self):
		if IsWindows():

			from ctypes import windll

			GWL_EXSTYLE = -20
			WS_EX_APPWINDOW = 0x00040000
			WS_EX_TOOLWINDOW = 0x00000080

			hWnd = windll.user32.GetParent(self.__root.winfo_id())
			# gLogger.info("hWnd: %d" %hWnd)

			if Is32bit():
				exStyle = windll.user32.GetWindowLongW(hWnd, GWL_EXSTYLE)			# 32bit python
			else:
				exStyle = windll.user32.GetWindowLongPtrW(hWnd, GWL_EXSTYLE)		# 64bit python
			exStyle = exStyle & ~WS_EX_TOOLWINDOW
			exStyle = exStyle | WS_EX_APPWINDOW
			if Is32bit():
				res = windll.user32.SetWindowLongW(hWnd, GWL_EXSTYLE, exStyle)
			else:
				res = windll.user32.SetWindowLongPtrW(hWnd, GWL_EXSTYLE, exStyle)		# 64bit python

			# re-assert the new window style
			self.__root.wm_withdraw()
			self.__root.after(10, lambda: self.__root.wm_deiconify())

	def __on_root_configure(self, _):

		gLogger.debug("MainFrame.on_root_configure")
		if self.__browser_frame:
			self.__browser_frame.on_root_configure()

	def __on_configure(self, event):

		gLogger.debug("MainFrame.on_configure")
		if self.__browser_frame:
			width = event.width
			height = event.height

			self.__browser_frame.on_mainframe_configure(width, height)

	def __on_close(self):
		# global gLogger

		gLogger.info("MainFrame.on_close")
		if self.__browser_frame:
			self.__browser_frame.on_root_close()
		self.master.destroy()

	def __on_unmap(self, event):
		# gLogger.info("on_unmap!")
		pass

	def __on_map(self, event):
		if self.__root.wm_state() == "normal" and not self.__bNormWindow:
			self.__bNormWindow = True
			self.__no_title()
		pass

	def start_move(self, x, y):
		# gLogger.info("startMove!")
		self.__enableMove = True
		# self.x = event.x
		self.__x = x
		# self.y = event.y
		self.__y = y

		self.__root_x = self.__root.winfo_rootx()
		self.__root_y = self.__root.winfo_rooty()

		# gLogger.info("self.x: %d self.y: %d" %(self.__x, self.__y))
		# gLogger.info("self.root_x: %d self.root_y: %d" %(self.__root_x, self.__root_y))

	def moving(self, x, y):
		if(not self.__enableMove): return

		newX = self.__root_x + x - self.__x
		# newX = self.winfo_x() + x - self.x
		newY = self.__root_y + y - self.__y
		# newY = self.winfo_y() + y - self.y

        # deltax = event.x - self.x
        # deltay = event.y - self.y
        # x = self.winfo_x() + deltax
        # y = self.winfo_y() + deltay

		# gLogger.info("newX: %d newY: %d" %(newX, newY))

		# self.__root.geometry("+%s+%s" %(newX, newY))
		self.__root.geometry("+%s+%s" %(newX, newY))

	def stop_move(self, x, y):
		# gLogger.info("stopMove!")
		self.__enableMove = False
		self.__x = None
		self.__y = None

	def TopMostOrNot(self, bTop):
		self.__root.wm_attributes('-topmost', bTop)

	def get_browser(self):
		if self.__browser_frame:
			return self.__browser_frame.get_browser()
		return None

	def get_browser_frame(self):
		if self.__browser_frame:
			return self.__browser_frame
		return None

	def min(self):
		# self.master.wm_withdraw()
		# self.__root.state('withdrawn')
		# self.master.update_idletasks()
		# self.master.overrideredirect(False)
		# self.master.state('iconic')
		# self.master.wm_iconify()
		self.__root.overrideredirect(False)
		self.__root.iconify()
		self.__bNormWindow = False

	def restore(self):
		self.master.wm_deiconify()

	def __setup_icon(self):
		# icon_path = os.path.join(os.path.dirname(__file__), "main" + IMAGE_EXT)
		icon_path = os.path.join(os.getcwd(), "main" + IMAGE_EXT)
		if os.path.exists(icon_path):
			self.__icon = tk.PhotoImage(file = icon_path)
			# noinspection PyProtectedMember
			self.master.call("wm", "iconphoto", self.master._w, self.__icon)

class BrowserFrame(tk.Frame):

	def __init__(self, master):
		self.closing = False
		self.__browser = None
		tk.Frame.__init__(self, master)
		self.bind("<FocusIn>", self.__on_focus_in)
		self.bind("<FocusOut>", self.__on_focus_out)
		self.bind("<Configure>", self.__on_configure)
		# self.master.master.protocol("WM_DELETE_WINDOW", self.on_root_close)
		self.focus_set()
		# self.__fileURL = fileURL

	def __embed_browser(self):

		window_info = cef.WindowInfo()
		rect = [0, 0, self.winfo_width(), self.winfo_height()]
		window_info.SetAsChild(self.__get_window_handle(), rect)

		custom_settings = {
			"file_access_from_file_urls_allowed": True,\
			"universal_access_from_file_urls_allowed": True,\
			"web_security_disabled": True
		}

		# self.__fileURL = os.path.join(os.getcwd(), "gui/about_all.html")
		# gLogger.info("self.__fileURL = %s" %self.__fileURL)

		# self.__browser = cef.CreateBrowserSync(window_info, url="http://html5test.com/")
		# self.__browser = cef.CreateBrowserSync(window_info, url = "file:///" + self.__fileURL, settings = custom_settings)
		self.__browser = cef.CreateBrowserSync(window_info, url = "", settings = custom_settings)

		assert self.__browser

		# global dictBrowser
		# dictBrowser = self.__browser
		# globalVar.GetApp().set_browser(self.__browser)

		# js
		js = cef.JavascriptBindings()
		js.SetObject('external', GetApp())
		self.__browser.SetJavascriptBindings(js)

		self.__browser.SetClientHandler(LoadHandler())
		self.__browser.SetClientHandler(FocusHandler())
		self.__browser.SetClientHandler(RequestHandler())
		self.__message_loop_work()

	def navigate(self, url):
		self.__browser.LoadUrl(url)

	def __get_window_handle(self):
		if self.winfo_id() > 0:
			return self.winfo_id()
		elif MAC:
			# On Mac window id is an invalid negative value (Issue #308).
			# This is kind of a dirty hack to get window handle using
			# PyObjC package. If you change structure of windows then you
			# need to do modifications here as well.
			# noinspection PyUnresolvedReferences
			from AppKit import NSApp
			# noinspection PyUnresolvedReferences
			import objc
			# Sometimes there is more than one window, when application
			# didn't close cleanly last time Python displays an NSAlert
			# window asking whether to Reopen that window.
			# noinspection PyUnresolvedReferences
			return objc.pyobjc_id(NSApp.windows()[-1].contentView())
		else:
			raise Exception("Couldn't obtain window handle")

	def __message_loop_work(self):
		cef.MessageLoopWork()
		self.after(10, self.__message_loop_work)

	def __on_configure(self, _):
		if not self.__browser:
			self.__embed_browser()
			GetApp().navigate_home()

	def on_root_configure(self):
		# Root <Configure> event will be called when top window is moved
		if self.__browser:
			self.__browser.NotifyMoveOrResizeStarted()

	def on_mainframe_configure(self, width, height):
		# gLogger.info("on_mainframe_configure")
		if self.__browser:
			if IsWindows():
				WindowUtils.OnSize(self.get_window_handle(), 0, 0, 0)
			elif IsLinux():
				self.__browser.SetBounds(0, 0, width, height)
			self.__browser.NotifyMoveOrResizeStarted()

	def __on_focus_in(self, _):

		gLogger.debug("BrowserFrame.on_focus_in")
		if self.__browser:
			self.__browser.SetFocus(True)

	def __on_focus_out(self, _):

		gLogger.debug("BrowserFrame.on_focus_out")
		if self.__browser:
			self.__browser.SetFocus(False)

	def on_root_close(self):
		gLogger.info("BrowserFrame.on_root_close")
		if self.__browser:
			self.__browser.CloseBrowser(True)
			self.__clear_browser_references()
		self.destroy()

	def get_browser(self):
		if self.__browser:
			return self.__browser
		return None

	def __clear_browser_references(self):
		# Clear browser references that you keep anywhere in your
		# code. All references must be cleared for CEF to shutdown cleanly.
		self.__browser = None

class LoadHandler(object):

	# def __init__(self, browser_frame):
	def __init__(self):
		# self.__browser_frame = browser_frame
		pass

	# def OnLoadStart(self, browser, **_):
		# if self.__browser_frame.master.navigation_bar:
			# self.__browser_frame.master.navigation_bar.set_url(browser.GetUrl())
		# # gLogger.info("LoadHandler.OnLoadStart")

	def OnLoadEnd(self, browser, **_):
		# browser.ExecuteFunction("log", "info", "LoadHandler.OnLoadEnd", False)
		gLogger.info("LoadHandler.OnLoadEnd")
		GetApp().add_tabs()
		GetApp().fill_menus()
		browser.ExecuteFunction("bindToggleExample")

	'''
	browser	Browser
	frame	Frame
	error_code	NetworkError
	error_text_out	list[string]
	failed_url	string
	'''
	def OnLoadError(self, browser, frame, error_code, error_text_out, failed_url):
		gLogger.error(error_code)
		gLogger.error(error_text_out)
		gLogger.error(failed_url)

class FocusHandler(object):

	# def __init__(self, browser_frame):
	def __init__(self):
		# self.__browser_frame = browser_frame
		pass

	def OnTakeFocus(self, next_component, **_):
		gLogger.debug("FocusHandler.OnTakeFocus, next = {next}"
					 .format(next=next_component))

	def OnSetFocus(self, source, **_):
		gLogger.debug("FocusHandler.OnSetFocus, source = {source}"
					 .format(source = source))
		return False

	def OnGotFocus(self, **_):
		"""Fix CEF focus issues (#255). Call browser frame's focus_set
		   to get rid of type cursor in url entry widget."""
		gLogger.debug("FocusHandler.OnGotFocus")
		# self.__browser_frame.focus_set()

class RequestHandler(object):
	def __init__(self):
		pass

	'''
	Parameter	Type
	browser	Browser
	url	string
	allow_execution_out	list[bool]
	Return	void
	'''
	def OnProtocolExecution(self, browser, url, allow_execution_out):
		# gLogger.info(browser)
		gLogger.info("url: " + url)
		# gLogger.info(allow_execution_out)
		protocol = url[:url.find(":")]

		gLogger.info("protocol: " + protocol)
		if protocol == "entry":
			word = url[url.find("//") + 2:]
			GetApp().navigate_home()
			GetApp().query_word(word)

class dictApp():

	def __init__(self):
		self._cfgDictFile = ""
		self._cfgDict = None
		# self.__opener = None

		# self.__dictBaseLst = []
		self.__dictBaseDict = {}
		self.__dictAgent = {}
		self.__dictId = ""
		self.__curDictBase = None
		self.__word = None
		self.__dictParseFun = ""
		self.__bHomeRdy = False
		self.__bTop = True

		self.__lastWord = None
		self.__PrevStack = Stack()
		# self.__NextQueue = Queue()
		self.__NextStack = Stack()

		self.__dictSysMenu = {}

		self.__mutexDownloadFile = threading.Lock()

	def __del__(self):
		print("dict App del!")

	def StartAndRun(self):
		self._cfgDictFile = os.path.join(os.getcwd(), "Dictionary.json")
		self.__ReadConfigure()

	def __Start(self, width, height, fileURL, showHiRatio, showWiRatio):
		sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error

		# Tk must be initialized before CEF otherwise fatal error (Issue #306)
		settings = {
			"debug": True,
			"log_severity": cef.LOGSEVERITY_ERROR,
			"log_file": "log//debug.log"
		}
		cef.Initialize(settings = settings)

		# settings1 = {
			# "debug": True,
			# "log_file": "debug.log",
			# "log_severity": cef.LOGSEVERITY_INFO,
			# "product_version": "MyProduct/10.00",
			# "user_agent": "MyAgent/20.00 MyProduct/10.00",
		# }
		# cef.Initialize(settings = settings1)
		'''
		switches = {
			"enable-media-stream": "",
			"proxy-server": "socks5://127.0.0.1:8888",
			"disable-gpu": "",
		}
		cef.Initialize(switches=switches)
		'''
		# cef.Initialize()

		self.__fileURL = fileURL
		# self.__curDictBase = self.get_curDB()
		# self.__dictParseFun = self.__curDictBase.get_parseFun()

		self.__window = MainFrame()
		self.__window.Create(width, height, showHiRatio, showWiRatio)
		# self.__window.navigate(fileURL)
		self.__window.mainloop()

	def Close(self):
		for item in self.__dictBaseDict.values():
			gLogger.info("Close %s" %item["name"])
			item["dictBase"].close()

		self.__auidoArchive.close()

		self.__SaveConfigure()

	def navigate_home(self):
		self.__bHomeRdy = False
		self.__window.navigate(self.__fileURL)

	def __AddAgent(self, name, ip, program, bActived = False):
		self.__dictAgent.update({name: {"ip": ip, "program": program, "bActived": bActived}})

	def ActiveAgent(self, activeAgent):
		bIEAgent = False
		opener = None
		gLogger.info("activeAgent = %s" %activeAgent)
		self._cfgDict["Agents"]["activeAgent"] = activeAgent
		for name in self.__dictAgent.keys():
			if name == activeAgent:
				self.__dictAgent[name]["bActived"] = True
			else:
				self.__dictAgent[name]["bActived"] = False

		if activeAgent != "None":
			gLogger.info("active agent: %s" %activeAgent)
			ip = self.__dictAgent[activeAgent]["ip"]
			proxyHandler = urllib.request.ProxyHandler({
				'http': ip,
				'https': ip
			})
			opener = urllib.request.build_opener(proxyHandler)
		elif bIEAgent:
			gLogger.info("ie_agent")
			opener = urllib.request.build_opener()
		else:
			proxyHandler = urllib.request.ProxyHandler({})
			opener = urllib.request.build_opener(proxyHandler)

		opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		# install the openen on the module-level
		urllib.request.install_opener(opener)

		proxies = urllib.request.getproxies()

		if proxies:
			gLogger.info("proxies: " + str(proxies))

	def __AddAudio(self, name, audioPackage):
		self.__auidoArchive = audioPackage

	def __AddDictBase(self, name, dictSrc, format):

		typ = format["Type"]
		if(typ == "ZIP"):
			compression = format["Compression"]
			compresslevel = format["Compress Level"]
			dictBase = GDictBase(dictSrc, compression, compresslevel)
		elif(typ == "SQLite"):
			dictBase = SDictBase(dictSrc)
		elif(typ == "mdx"):
			dictBase = MDictBase(dictSrc)

		# self.__dictBaseLst.append(dictBase)

		dictId = "dict" + str(len(self.__dictBaseDict) + 1)
		self.__dictBaseDict.update({dictId: {"name": name, "dictBase": dictBase}})

	def add_tabs(self):
		html = '''\n							<div id = "toggle_example" align = "right">- Hide Examples</div>
							<p></p>'''
		for dictId, item in self.__dictBaseDict.items():
			gLogger.info("addTab: %s: %s" %(dictId, item["name"]))
			self.get_browser().ExecuteFunction("addTab", dictId, item["name"], html)
			self.__dictId = dictId

		self.get_browser().ExecuteFunction("bindSwitchTab");

		# switch to dict1
		self.__dictId = "dict1"
		self.__curDictBase = self.get_curDB()
		self.__dictParseFun = self.__curDictBase.get_parseFun()
		self.get_browser().ExecuteFunction("active_Tab", self.__dictId);

		self.__curDictBase = self.get_curDB()

		self.__bHomeRdy = True
		# if self.__word != None:
			# self.get_browser().ExecuteFunction("set_word", self.__word);
			# self.get_browser().ExecuteFunction("query_word");
			# self.query_word(self.__word)

	def __AddMenu(self, name, action, bActived = False):
		self.__dictSysMenu.update({name: action})
		# menuId = "dict" + str(len(self.__dictSysMenu) + 1)
		menuId = name
		self.get_browser().ExecuteFunction("fill_menu", menuId, name);
		if bActived:
			gLogger.info("Active Menu: %s" %menuId)
			self.get_browser().ExecuteFunction("active_menu", menuId);

	def fill_menus(self):
		for key in self.__dictAgent.keys():
			self.__AddMenu(key, "ActiveAgent", self.__dictAgent[key]["bActived"])
		# self.add_menu("None", "active_agent")
		self.get_browser().ExecuteFunction("bindMenus");

	def get_browser(self):
		return self.__window.get_browser()

	def switch_tab(self, tabId):
		# gLogger.info("switch to tab: " + tabId)
		self.__dictId = tabId
		self.__curDictBase = self.get_curDB()
		self.__dictParseFun = self.__curDictBase.get_parseFun()

	def get_curDB(self):
		return self.__dictBaseDict[self.__dictId]["dictBase"]

	def playMP3(self, audio):

		gLogger.info("going to play " + audio)
		self.get_browser().ExecuteFunction("playMP3", audio)
		return True

	def __dwf_callbackfunc(self, blocknum, blocksize, totalsize):
		# global gLogger

		'''回调函数
		@blocknum: 已经下载的数据块
		@blocksize: 数据块的大小
		@totalsize: 远程文件的大小
		'''
		percent = 100.0 * blocknum * blocksize / totalsize
		if percent > 100: percent = 100
		gLogger.info("%.2f%% download file." %percent)

	def download_file(self, dictPtr, url, local):
		if self.__mutexDownloadFile.acquire(1):
			dw = threading.Thread(target = self.__DownloadFileThread, args = (dictPtr, url, local, ))
			dw.start()

	def __DownloadFileThread(self, dictPtr, url, local):
		gLogger.info("Going to download %s" %url)

		errMsg = None
		try:
			urllib.request.urlretrieve(url, local, self.__dwf_callbackfunc)
		except urllib.error.HTTPError as err:
			gLogger.error(err.code)
			gLogger.error(err.reason)
			errMsg = err.reason
			# gLogger.error(err.headers)
		except urllib.error.URLError as err:
			errMsg = str(err).replace("<", "")
			errMsg = errMsg.replace(">", "")
			gLogger.error(errMsg)

		self.__mutexDownloadFile.release()

		dictPtr.NotifyDownload(errMsg)

	def download_file(self, url, local):
		gLogger.info("Going to download %s" %url)
		errMsg = None
		try:
			'''
			r = self.__opener.open(url)
			with open(local, 'wb') as f:
				f.write(r.read())
			'''
			urllib.request.urlretrieve(url, local, self.__dwf_callbackfunc)
		except urllib.error.HTTPError as err:
			gLogger.error(err.code)
			gLogger.error(err.reason)
			errMsg = err.reason
			# gLogger.error(err.headers)
		except urllib.error.URLError as err:
			errMsg = str(err).replace("<", "")
			errMsg = errMsg.replace(">", "")
			gLogger.error(errMsg)

		return errMsg

	def OnButtonClicked(self, id):
		# global gLogger

		if id == "btn_close":
			# self.__window.master.withdraw()
			self.__window.master.destroy()
		elif id == "btn_min": self.__window.min()
		elif id == "btn_prev": self.__QueryPrev()
		elif id == "btn_next": self.__QueryNext()
		else:
			gLogger.info(id)

	def OnMenuClicked(self, menuId):
		action = "self." + self.__dictSysMenu[menuId]
		gLogger.info("action = %s" %action)

		eval(action)(menuId)
		self.get_browser().ExecuteFunction("active_menu", menuId);

	def start_move(self, x, y):
		self.__window.start_move(x, y)

	def moving(self, x, y):
		self.__window.moving(x, y)

	def stop_move(self, x, y):
		self.__window.stop_move(x, y)

	def log(self, lvl, info):
		if(lvl == "info"):
			gLogger.info(info)
		elif(lvl == "error"):
			gLogger.error(info)

	def query_word(self, word, nDirect = 0):
		if self.__lastWord:
			if nDirect == -1:
				self.__NextStack.Push(self.__lastWord)
				# gLogger.info("__PrevQueue: %d", self.__PrevQueue.GetSize())
				if self.__NextStack.GetSize() >= 1:
					self.get_browser().ExecuteFunction("disableButton", "btn_next", False);					
			else:
				self.__PrevStack.Push(self.__lastWord)
				# gLogger.info("__PrevQueue: %d", self.__PrevQueue.GetSize())
				if self.__PrevStack.GetSize() >= 1:
					self.get_browser().ExecuteFunction("disableButton", "btn_prev", False);			

		self.__word = word

		if self.__bHomeRdy == False:
			return

		gLogger.info("word = %s;" %word)

		# curDictbase = self.get_curDB()

		bDictOK, dict = self.__curDictBase.query_word(word)
		bAudioOK, audio = self.__auidoArchive.query_audio(word)

		if(not bDictOK):
			gLogger.error("dict: " + dict)
			self.__RecordMissDict(word, dict)
			dict = '{\n' + \
					'	"query": "' + word +  '",\n' + \
					'	"sourceLanguage": "en",\n' + \
					'	"targetLanguage": "zh-Hans",\n' + \
					'	"primaries": [{\n' + \
					'		"type": "headword",\n' + \
					'		"terms": [{\n' + \
					'				"type": "text",\n' + \
					'				"text": "' + word + '",\n' + \
					'				"language": "en"\n' + \
					'			}, {\n' + \
					'				"type": "phonetic",\n' + \
					'				"text": "' + dict + '",\n' + \
					'				"language": "en",\n' + \
					'				"labels": [{\n' + \
					'					"text": "DJ",\n' + \
					'					"title": "Phonetic"\n' + \
					'				}]\n' + \
					'			}\n' + \
					'		]\n' + \
					'	}]\n' + \
					'}'

		if(not bAudioOK):
			gLogger.error("audio: " + audio)
			self.__RecordMissAudio(word, audio)
			audio = os.path.join(os.getcwd(), "audio", "WrongHint.mp3")

		# tabId = "dict" + str(self.__nTab + 1)
		# gLogger.info("tabId: " + tabId)
		# gLogger.info("dictParseFun: " + self.__dictParseFun)

		if bDictOK:
			# dict = 'Dictionary.py[L584] ERROR: <urlopen error [WinError 10060] 由于连接方在一段时后没有正确答复或连接的主机没有反应，连接尝试失败。>'
			self.get_browser().ExecuteFunction(self.__dictParseFun, word, self.__dictId, dict, audio)
			# gLogger.info("dict: " + dict)
			# gLogger.info("audio: " + audio)
		else:
			self.get_browser().ExecuteFunction("dictJson", word, self.__dictId, dict, audio)

		self.__lastWord = word

	def __QueryPrev(self):
		word = self.__PrevStack.Pop()
		if self.__PrevStack.GetSize() == 0:
			self.get_browser().ExecuteFunction("disableButton", "btn_prev", True);

		# self.__NextQueue.Enqueue(word)
		# if self.__NextQueue.GetSize() == 2:
				# self.get_browser().ExecuteFunction("disableButton", "btn_next", False);

		self.get_browser().ExecuteFunction("set_word", word);
		# self.get_browser().ExecuteFunction("query_word");
		self.query_word(word, -1)

	def __QueryNext(self):
		# word = self.__NextQueue.Dequeue()
		word = self.__NextStack.Pop()
		if self.__NextStack.GetSize() == 0:
			self.get_browser().ExecuteFunction("disableButton", "btn_next", True);

		# self.__PrevStack.Push(word)
		# if self.__PrevStack.GetSize() == 2:
				# self.get_browser().ExecuteFunction("disableButton", "btn_prev", False);

		self.get_browser().ExecuteFunction("set_word", word);
		# self.get_browser().ExecuteFunction("query_word");
		self.query_word(word, 1)

	def __SetMissRecordFile(self, miss_dict, miss_audio):
		self.__miss_dict = miss_dict
		self.__miss_audio = miss_audio

	def __RecordMissDict(self, word, why):
		with open(self.__miss_dict, mode = "a") as f:
			f.write(word + ": " + why + "\n")

	def __RecordMissAudio(self, word, why):
		# self.__miss_audio.write(word + ": " + why + "\r\n")
		with open(self.__miss_audio, mode = "a") as f:
			f.write(word + ": " + why + "\n\n")

	'''
	def speechWord(self, word, isUs):
		# gLogger.info("going to speech %s" %word)
		# mp3 = sys.path[0] + "\\Audio\\Google\\" + word + ".mp3"
		# mp3 = os.path.join(os.getcwd(), "audio/Google/" + word + ".mp3")
		audio = self.__auidoArchive.query_audio(word)
		gLogger.info("mp3 = %s" %audio)
		if os.path.isfile(audio) == False:
			gLogger.error("The is no mp3: " + audio)
			msgBox.showerror(word, "The is no mp3: " + audio)
			return "break"

		try:
			self.playMP3(audio)
		except Exception as ex:
			gLogger.error("wrong mp3: " + audio)
			msgBox.showerror(word, "wrong mp3: " + audio)
			gLogger.info(Exception + ": " + ex)
	'''

	def speechWord(self, audio):
		if os.path.isfile(audio) == False:
			gLogger.error("The is no mp3: " + audio)
			msgBox.showerror(word, "The is no mp3: " + audio)
		try:
			self.playMP3(audio)
		except Exception as ex:
			gLogger.error("wrong mp3: " + audio)
			msgBox.showerror(word, "wrong mp3: " + audio)
			gLogger.info(Exception + ": " + ex)

	def TopMostOrNot(self):
		self.__bTop = not self.__bTop
		self.__window.TopMostOrNot(self.__bTop)

	def OnTextChanged(self, word):
		# global gLogger

		wdsLst = []
		# gLogger.info("OnTextChanged: word = ", word)
		# ret = globalVar.GetApp().get_curDB().get_wordslst(wdsLst, word)
		# curDictbase = self.get_curDB()
		ret = self.__curDictBase.get_wordsLst(wdsLst, word)
		if (not ret):
			# gLogger.info("OnTextChanged: no similiar words!")
			return False

		self.__window.get_browser().ExecuteFunction("clear_words_list")

		for wd in wdsLst:
			# gLogger.info("Goint to append %s" %wd)
			self.__window.get_browser().ExecuteFunction("append_words_list", wd)
			# gLogger.info("found word: %s" %wd)
		# gLogger.info("Finished to append")

	# Deprecated
	def OnSaveHtml(self, html):
		outFile = filedialog.asksaveasfile(mode = 'w', defaultextension = ".html")
		# asksaveasfile return `None` if dialog closed with "cancel".
		if outFile:
			outFile.write(html)
			outFile.close()

	def __ReadConfigure(self):
		global gLogger
		with open(self._cfgDictFile, 'rb') as f:
			datum = f.read()
		self._cfgDict = json.loads(datum, strict = False)

		version = self._cfgDict["common"]["ver"]
		'''
		logging 用作记录日志，默认分为六种日志级别（括号为级别对应的数值），NOTSET（0）、DEBUG（10）、INFO（20）、WARNING（30）、ERROR（40）、CRITICAL（50）。logging执行时输出大于等于设置的日志级别的日志信息
		'''
		bDebug = self._cfgDict["Debug"]["bEnable"]
		if bDebug:
			level = logging.DEBUG
		else:
			level = logging.INFO
		
		curPath = os.getcwd()

		logFile = self._cfgDict["Debug"]["file"]
		lFile = os.path.join(curPath, logFile)

		gLogger = create_logger("Dictionary", lFile, level)
		SetLogger(gLogger)

		os_ver = ""
		if IsWindows():
			# platform.win32_ver(release='', version='', csd='', ptype='')
			# Get additional version information from the Windows Registry and return a tuple (release, version, csd, ptype) referring to OS release, version number, CSD level (service pack) and OS type (multi/single processor).
			os_ver = "Windoes " + platform.win32_ver()[0]
		elif IsLinux():
			gLogger.info("It's Linux!")
			platform.linux_distribution()

		gLogger.info(os_ver)
		gLogger.info("CEF Python v{ver}".format(ver = cef.__version__))
		gLogger.info("Python v{ver} {arch}".format(
				ver = platform.python_version(), arch = platform.architecture()[0]))
		gLogger.info("Tk v{ver}".format(ver = tk.Tcl().eval('info patchlevel')))
		gLogger.info("Dictionary v{ver}".format(ver = version))

		bIEAgent = self._cfgDict["Agents"]["bIEAgent"]
		activeAgent = self._cfgDict["Agents"]["activeAgent"]

		for agent in self._cfgDict["Agents"]["Info"]:
			name = agent["Name"]
			ip = agent["IP"]
			program = agent["Program"]
			self.__AddAgent(name, ip, program)
		self.__AddAgent("None", "", "")
		# self.__ActiveAgent(activeAgent)
		self.ActiveAgent(activeAgent)

		for tabGroup in self._cfgDict["Tabs"]:
			name = tabGroup["Name"]
			dict = tabGroup["Dict"]
			format = tabGroup["Format"]
			dictSrc = os.path.join(curPath, dict)
			self.__AddDictBase(name, dictSrc, format)

		audioGroup = self._cfgDict["Audio"][0]
		name = audioGroup["Name"]
		audio = audioGroup["Audio"]
		audioFile = os.path.join(curPath, audio)
		format = audioGroup["Format"]
		typ = format["Type"]

		if typ == "ZIP":
			compression = format["Compression"]
			compressLevel = format["Compress Level"]
			audioPackage = AuidoArchive(audioFile, compression, compressLevel)

		self.__AddAudio(name, audioPackage)
	 
		miss_dict = os.path.join(curPath, self._cfgDict["Miss"]["miss_dict"])
		miss_audio = os.path.join(curPath, self._cfgDict["Miss"]["miss_audio"])
		self.__SetMissRecordFile(miss_dict, miss_audio)

		width = int(self._cfgDict["GUI"]["Width"])
		height = int(self._cfgDict["GUI"]["Height"])
		fileURL = os.path.join(curPath, self._cfgDict["GUI"]["html"])

		showHiRatio = float(self._cfgDict["GUI"]["ShowHiRatio"])
		showWiRatio = float(self._cfgDict["GUI"]["ShowWiRatio"])

		self.__Start(width, height, fileURL, showHiRatio, showWiRatio)	

	def __SaveConfigure(self):
		gLogger.info("save configure")

		# jsonStr = json.dumps(self._cfgDict)
		with open(self._cfgDictFile, 'w') as f:
			# f.write(jsonStr)
			json.dump(self._cfgDict, f, indent=4)

def main():

	assert cef.__version__ >= "66.0", "CEF Python v66.0+ required to run this"

	global gLogger

	app = dictApp()
	SetApp(app)

	app.StartAndRun()

	# app.start()

	cef.Shutdown()

	app.Close()

	if os.path.exists("webrtc_event_logs"): shutil.rmtree("webrtc_event_logs")
	if os.path.exists("blob_storage"): shutil.rmtree("blob_storage")
	if os.path.exists("error.log"): os.remove("error.log")

	gLogger.info("All are done!")

if __name__ == '__main__':
	main()