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

# Fix for PyCharm hints warnings
WindowUtils = cef.WindowUtils()

# Constants
# Tk 8.5 doesn't support png images
IMAGE_EXT = ".png" if tk.TkVersion > 8.5 else ".gif"

class MainFrame(tk.Frame):

	def __init__(self):

		self.__enableMove = False
		self.__winOK = False

	def Create(self, width, height):

		# Root
		self.__root = tk.Tk()

		tk.Grid.rowconfigure(self.__root, 0, weight = 1)
		tk.Grid.columnconfigure(self.__root, 0, weight = 1)

		# MainFrame
		tk.Frame.__init__(self, self.__root)
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
		size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)

		gLogger.info("size: %s" %size)

		self.__root.geometry(size)
		self.__root.resizable(height = None, width = None)

		self.__no_title()

		self.__setup_icon()
		self.__root.wm_attributes('-topmost', True)

		self.__winOK = True

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
		# gLogger.info("on_map!")
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

	def get_browser(self):
		if self.__browser_frame:
			return self.__browser_frame.get_browser()
		return None

	def get_browser_frame(self):
		if self.__browser_frame:
			return self.__browser_frame
		return None

	def min(self):
		# return
		# self.master.wm_withdraw()
		# self.__root.state('withdrawn')
		# self.master.update_idletasks()
		self.master.overrideredirect(False)
		self.master.state('iconic')
		# self.master.wm_iconify()
		pass

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

		self.__bAgent = False

		# self.__dictBaseLst = []
		self.__dictBaseDict = {}
		self.__nTab = 0
		self.__curDictBase = None
		self.__word = None
		self.__homeRdy = False

	def __del__(self):
		print("dict App del!")

	def start(self, width, height, fileURL):

		self.__fileURL = fileURL
		self.__curDictBase = self.get_curDB()
		self.__DictParseFun = self.__curDictBase.get_parseFun()

		self.__window = MainFrame()
		self.__window.Create(width, height)
		# self.__window.navigate(fileURL)
		self.__window.mainloop()

	def close(self):
		for dictBase in self.__dictBaseDict.values():
			gLogger.info("Close %s" %dictBase["name"])
			dictBase["dictBase"].close()

		self.__auidoArchive.close()

	def navigate_home(self):
		self.__homeRdy = False
		self.__window.navigate(self.__fileURL)

	def set_agent(self, ip, name, program):
		self.__bAgent = True
		self.__Proxy = ip
		self.__Name = name
		self.__Program = program

	def add_audio(self, name, audioPackage):
		self.__auidoArchive = audioPackage

	def add_dictBase(self, name, dictSrc, format):

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

		id = "dict" + str(len(self.__dictBaseDict) + 1)
		self.__dictBaseDict.update({id: {"name": name, "dictBase": dictBase}})

	def add_tabs(self):
		html = '''							<div id = "toggle_example" align = "right">- Hide Examples</div>
							<p></p>'''

		for key, item in self.__dictBaseDict.items():
			self.get_browser().ExecuteFunction("addTab", key, item["name"], html);

		self.get_browser().ExecuteFunction("bindSwitchTab");
		# tabId = "dict1"
		tabId = "dict" + str(self.__nTab + 1)
		self.get_browser().ExecuteFunction("activeTab", tabId);

		self.__homeRdy = True
		if self.__word != None:
			self.get_browser().ExecuteFunction("set_word", self.__word);
			self.get_browser().ExecuteFunction("query_word");
			# self.query_word(self.__word)

	def get_browser(self):
		return self.__window.get_browser()

	def switch_tab(self, n):
		gLogger.info("switch to tab: " + str(n))
		self.__nTab = n - 1
		self.__curDictBase = self.get_curDB()
		self.__DictParseFun = self.__curDictBase.get_parseFun()

	def get_curDB(self):
		# return self.__dictBaseLst[self.__nTab]
		id = "dict" + str(self.__nTab + 1)
		# print(self.__dictBaseDict)
		return self.__dictBaseDict[id]["dictBase"]

	def playMP3(self, audio):

		gLogger.info("going to play " + audio)
		self.get_browser().ExecuteFunction("playMP3", audio)
		return True

	def dwf_callbackfunc(self, blocknum, blocksize, totalsize):
		# global gLogger

		'''回调函数
		@blocknum: 已经下载的数据块
		@blocksize: 数据块的大小
		@totalsize: 远程文件的大小
		'''
		percent = 100.0 * blocknum * blocksize / totalsize
		if percent > 100: percent = 100
		gLogger.info("%.2download_filef%%" %percent)

	# To-Do:
	# add progress hint
	# detect proxy program before download
	def download_file(self, url, local):
		# global gLogger

		# try:
		gLogger.info("Going to download %s" %url)
		if(self.__bAgent == True):
			proxyHandler = urllib.request.ProxyHandler({
				'http': self.__Proxy,
				'https': self.__Proxy
			})
			opener = urllib.request.build_opener(proxyHandler)

		else:
			opener = urllib.request.build_opener()

		opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		r = opener.open(url)

		with open(local, 'wb') as f:
			f.write(r.read())

		# except Exception as ex:
			# gLogger.error("fail to download %s" %urls)
			# gLogger.info("Exception: " + str(ex))
			# return False
		# return True

	def OnButtonClicked(self, id):
		# global gLogger

		if id == "btn_close":
			# self.__window.master.withdraw()
			self.__window.master.destroy()

		elif id == "btn_min": self.__window.min()
		else: 
			gLogger.info(id)

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

	def query_word(self, word):
		self.__word = word

		if self.__homeRdy == False:
			return

		gLogger.info("word = %s;" %word)

		# curDictbase = self.get_curDB()

		bDictOK, dict = self.__curDictBase.query_word(word)
		bAudioOK, audio = self.__auidoArchive.query_audio(word)

		if(not bDictOK):
			gLogger.error("dict: " + dict)
			self.__record_miss_dict(word, dict)
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
			self.__record_miss_audio(word, audio)
			audio = os.path.join(os.getcwd(), "audio", "WrongHint.mp3")

		tabId = "dict" + str(self.__nTab + 1)
		# gLogger.info("tabId: " + tabId)

		# gLogger.info("dictParseFun: " + self.__DictParseFun)

		if bDictOK:
			self.get_browser().ExecuteFunction(self.__DictParseFun, word, tabId, dict, audio)
			# gLogger.info("dict: " + dict)
			# gLogger.info("audio: " + audio)
		else:
			self.get_browser().ExecuteFunction("dictJson", word, tabId, dict, audio)

	def set_miss_record_file(self, miss_dict, miss_audio):
		self.__miss_dict = miss_dict
		self.__miss_audio = miss_audio

	def __record_miss_dict(self, word, why):
		with open(self.__miss_dict, mode = "a") as f:
			f.write(word + ": " + why + "\r\n")

	def __record_miss_audio(self, word, why):
		# self.__miss_audio.write(word + ": " + why + "\r\n")
		with open(self.__miss_audio, mode = "a") as f:
			f.write(word + ": " + why + "\r\n")

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
			return "break"

		try:
			self.playMP3(audio)
		except Exception as ex:
			gLogger.error("wrong mp3: " + audio)
			msgBox.showerror(word, "wrong mp3: " + audio)
			gLogger.info(Exception + ": " + ex)

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

		for wd in wdsLst:
			self.__window.get_browser().ExecuteFunction("append_words_list", wd)
			# gLogger.info("found word: %s" %wd)

	# Deprecated
	def OnSaveHtml(self, html):
		outFile = filedialog.asksaveasfile(mode = 'w', defaultextension = ".html")
		# asksaveasfile return `None` if dialog closed with "cancel".
		if outFile:
			outFile.write(html)
			outFile.close()

def main():

	assert cef.__version__ >= "66.0", "CEF Python v66.0+ required to run this"

	global gLogger

	if IsWindows(): print("It's Windows!")
	elif IsLinux(): print("It's Linux!")

	curPath = os.getcwd()
	cfgFile = os.path.join(curPath, "Dictionary.json")
	# print(cfgFile)
	with open(cfgFile, 'rb') as f:
		datum = f.read()
	cfg = json.loads(datum, strict = False)

	version = cfg["common"]["ver"]

	bDebug = cfg["Debug"]["bEnable"]
	logFile = None
	if bDebug:
		logFile = cfg["Debug"]["file"]

	lFile = os.path.join(curPath, logFile)

	gLogger = create_logger("Dictionary", logFile)
	SetLogger(gLogger)

	gLogger.info("CEF Python v{ver}".format(ver = cef.__version__))
	gLogger.info("Python v{ver} {arch}".format(
			ver = platform.python_version(), arch = platform.architecture()[0]))
	gLogger.info("Tk v{ver}".format(ver = tk.Tcl().eval('info patchlevel')))
	gLogger.info("Dictionary v{ver}".format(ver = version))

	app = dictApp()
	SetApp(app)

	bAgent = cfg["Agent"]["bAgent"]
	if bAgent == True:
		nProxy = cfg["Agent"]["nAgent"]

		agentGroup = cfg["Agent"]["Info"][nProxy - 1]
		gLogger.info(agentGroup)
		ip = agentGroup["IP"]
		name = agentGroup["Name"]
		program = agentGroup["Program"]
		gLogger.info(ip, name, program)
		app.set_agent(ip, name, program)

	tabArray = cfg["Tab"]
	for tabGroup in tabArray:
		name = tabGroup["Name"]
		dict = tabGroup["Dict"]
		format = tabGroup["Format"]
		dictSrc = os.path.join(curPath, dict)
		app.add_dictBase(name, dictSrc, format)

	audioGroup = cfg["Audio"][0]
	name = audioGroup["Name"]
	audio = audioGroup["Audio"]
	audioFile = os.path.join(curPath, audio)
	format = audioGroup["Format"]
	typ = format["Type"]
	
	if typ == "ZIP":
		compression = format["Compression"]
		compressLevel = format["Compress Level"]
		audioPackage = AuidoArchive(audioFile, compression, compressLevel)

	app.add_audio(name, audioPackage)

	miss_dict = os.path.join(curPath, cfg["Miss"]["miss_dict"])
	miss_audio = os.path.join(curPath, cfg["Miss"]["miss_audio"])
	app.set_miss_record_file(miss_dict, miss_audio)

	width = int(cfg["GUI"]["Width"])
	height = int(cfg["GUI"]["Height"])
	fileURL = os.path.join(curPath, cfg["GUI"]["html"])

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

	app.start(width, height, fileURL)

	cef.Shutdown()

	app.close()

	if os.path.exists("webrtc_event_logs"): shutil.rmtree("webrtc_event_logs")
	if os.path.exists("blob_storage"): shutil.rmtree("blob_storage")
	if os.path.exists("error.log"): os.remove("error.log")

	gLogger.info("All are done!")

if __name__ == '__main__':
	main()