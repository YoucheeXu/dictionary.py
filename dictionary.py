#!/usr/bin/python3
# -*- coding: utf-8 -*-

# pip3 install cefpython3==66.0
# pip3 uninstall cefpython3==66.0

from cefpython3 import cefpython as cef

import sys, os
import time
import base64
import threading
import json

import urllib.request
import urllib.error

from tkinter import filedialog
import tkinter as tk
import tkinter.messagebox as msgBox

try:
	from ctypes import windll
	GWL_STYLE = -16
	GWL_EXSTYLE = -20
	WS_EX_APPWINDOW = 0x00040000
	WS_EX_TOOLWINDOW = 0x00000080
	WS_CAPTION = 0x00C00000

except ImportError:
	pass

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

# global gLogger

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

	gLogger = CreateLogger("Dictionary", logFile)
	SetLogger(gLogger)

	gLogger.info("CEF Python {ver}".format(ver = cef.__version__))
	gLogger.info("Python {ver} {arch}".format(
			ver = platform.python_version(), arch = platform.architecture()[0]))
	gLogger.info("Tk {ver}".format(ver = tk.Tcl().eval('info patchlevel')))
	gLogger.info("Dictionary {ver}".format(ver = version))

	# gLogger.info(cfg);
	# global app
	app = dictApp()
	# globalVar.SetApp(app)
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
		app.SetAgent(ip, name, program)

	tabArray = cfg["Tab"]
	for tabGroup in tabArray:
		name = tabGroup["Name"]
		dict = tabGroup["Dict"]
		format = tabGroup["Format"]
		dictSrc = os.path.join(curPath, dict)
		app.AddDictBase(name, dictSrc, format)

	audioGroup = cfg["Audio"][0]
	name = audioGroup["Name"]
	audio = audioGroup["Audio"]
	audioPath = os.path.join(curPath, audio)
	app.AddAudio(name, audioPath)

	miss_dict = os.path.join(curPath, cfg["Miss"]["miss_dict"])
	miss_audio = os.path.join(curPath, cfg["Miss"]["miss_audio"])
	app.SetMissRecordFile(miss_dict, miss_audio)

	width = int(cfg["GUI"]["Width"])
	height = int(cfg["GUI"]["Height"])
	fileURL = os.path.join(curPath, cfg["GUI"]["html"])
	app.Start(width, height, fileURL)

	sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error

	# root = tk.Tk()
	# # root.attributes("-alpha",0.0)
	# global window
	# window = MainFrame(root)

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
	app.mainloop()
	cef.Shutdown()

	gLogger.info("All are done!")

def set_appwindow(root):
	if IsWindows():
		hwnd = windll.user32.GetParent(root.winfo_id())
		# exStyle = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
		# exStyle &= ~WS_EX_TOOLWINDOW
		# exStyle |= WS_EX_APPWINDOW
		# res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, exStyle)
		
		style = windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
		style &= ~WS_CAPTION
		res = windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)
		# re-assert the new window style

		# root.wm_withdraw()
		# root.after(10, lambda: root.wm_deiconify())
	pass

class MainFrame(tk.Frame):

	def Start(self, root, width, height, fileURL):
		# global gLogger

		self.browser_frame = None
		self.navigation_bar = None

		# width = 701
		# height = 551

		screenwidth = root.winfo_screenwidth()
		screenheight = root.winfo_screenheight()  
		size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)

		gLogger.info("size: %s" %size)

		# Root
		root.geometry(size)
		# root.overrideredirect(True)		#no title

		# if IsWindows():
			# root.aftesr_idle(root.lower)
			# root.after(10, lambda: set_appwindow(root))
		self.__window = root

		# root.attributes('-alpha', 0.0) #For icon
		# root.iconify()
		# self.__window = tk.Toplevel(root)
		# self.__window.geometry(size)
		# self.__window.overrideredirect(True)	#no title

		tk.Grid.rowconfigure(self.__window, 0, weight = 1)
		tk.Grid.columnconfigure(self.__window, 0, weight = 1)

		# MainFrame
		tk.Frame.__init__(self, self.__window)
		self.master.title("Dictionary")
		self.master.protocol("WM_DELETE_WINDOW", self.on_close)
		self.master.bind("<Configure>", self.on_root_configure)
		self.setup_icon()
		self.bind("<Configure>", self.on_configure)
		self.bind("<FocusIn>", self.on_focus_in)
		self.bind("<FocusOut>", self.on_focus_out)

		# # NavigationBar
		# self.navigation_bar = NavigationBar(self)
		# self.navigation_bar.grid(row=0, column=0,
		#						  sticky=(tk.N + tk.S + tk.E + tk.W))
		# tk.Grid.rowconfigure(self, 0, weight=0)
		# tk.Grid.columnconfigure(self, 0, weight=0)

		# BrowserFrame
		# self.browser_frame = BrowserFrame(self, fileURL, self.navigation_bar)
		self.browser_frame = BrowserFrame()
		self.browser_frame.init(self, fileURL, self.navigation_bar)
		self.browser_frame.grid(row = 1, column = 0,
								 sticky = (tk.N + tk.S + tk.E + tk.W))
		tk.Grid.rowconfigure(self, 1, weight = 1)
		tk.Grid.columnconfigure(self, 0, weight = 1)

		# Pack MainFrame
		self.pack(fill = tk.BOTH, expand = tk.YES)

	def geometry(self, size):
		# global gLogger

		gLogger.info(size)
		self.__window.geometry(size);

	def on_root_configure(self, _):
		# global gLogger

		gLogger.debug("MainFrame.on_root_configure")
		if self.browser_frame:
			self.browser_frame.on_root_configure()

	def on_configure(self, event):
		# global gLogger

		gLogger.debug("MainFrame.on_configure")
		if self.browser_frame:
			width = event.width
			height = event.height
			if self.navigation_bar:
				height = height - self.navigation_bar.winfo_height()
			self.browser_frame.on_mainframe_configure(width, height)

	def on_focus_in(self, _):
		# global gLogger

		gLogger.debug("MainFrame.on_focus_in")

	def on_focus_out(self, _):
		# global gLogger

		gLogger.debug("MainFrame.on_focus_out")

	def on_close(self):
		# global gLogger

		gLogger.info("on_close")
		if self.browser_frame:
			self.browser_frame.on_root_close()
		self.master.destroy()

	def get_browser(self):
		if self.browser_frame:
			return self.browser_frame.browser
		return None

	def get_browser_frame(self):
		if self.browser_frame:
			return self.browser_frame
		return None

	def min(self):
		return
		# self.master.wm_withdraw()
		# self.master.wm_iconify()
		self.master.update_idletasks()
		self.master.overrideredirect(False)
		#root.state('withdrawn')
		self.master.state('iconic')

	def restore(self):
		self.master.wm_deiconify()

	def frame_mapped(self, e):
		self.master.update_idletasks()
		# self.master.overrideredirect(True)
		self.master.after(1, lambda: set_appwindow(self.master))
		self.master.state('normal')

	def setup_icon(self):
		# resources = os.path.join(os.path.dirname(__file__), "resources")
        # icon_path = os.path.join(resources, "tkinter"+IMAGE_EXT)
		icon_path = os.path.join(os.path.dirname(__file__), "main" + IMAGE_EXT)
		if os.path.exists(icon_path):
			self.icon = tk.PhotoImage(file = icon_path)
			# noinspection PyProtectedMember
			self.master.call("wm", "iconphoto", self.master._w, self.icon)

class BrowserFrame(tk.Frame):

	def init(self, master, fileURL, navigation_bar = None):
		self.navigation_bar = navigation_bar
		self.closing = False
		self.browser = None
		tk.Frame.__init__(self, master)
		self.bind("<FocusIn>", self.on_focus_in)
		self.bind("<FocusOut>", self.on_focus_out)
		self.bind("<Configure>", self.on_configure)
		self.focus_set()
		self.__fileURL = fileURL

	def embed_browser(self):

		window_info = cef.WindowInfo()
		rect = [0, 0, self.winfo_width(), self.winfo_height()]
		window_info.SetAsChild(self.get_window_handle(), rect)

		# options.add_argument('--log-level=3')
		# options = webdriver.ChromeOptions()
		# options.add_experimental_option('excludeSwitches', ['enable-logging'])
		# driver = webdriver.Chrome(executable_path='<path-to-chrome>', options=options)		
		settings2 = {
			"file_access_from_file_urls_allowed": True,\
			"universal_access_from_file_urls_allowed": True,\
			"web_security_disabled": True
		}
		# file://Data/GUI_3.html
		# "~/Green/Dictionary/Data/GUI_3.html"
		# self.__fileURL = os.path.join(os.getcwd(), "gui/GUI.html")
		# urlStr = os.path.join(os.getcwd(), "gui/about_all.html")
		# urlStr = os.path.join(os.getcwd(), "PronounceWord/PronounceWord.mini.html")
		# gLogger.info("urlStr = %s" %urlStr)
		self.browser = cef.CreateBrowserSync(window_info, url = "file:///" + self.__fileURL, settings = settings2)
		# self.browser = cef.CreateBrowserSync(window_info, url="http://html5test.com/")
		# self.browser = cef.CreateBrowserSync(window_info, url="http://jplayer.org/audio/mp3/Miaow-07-Bubble.mp3")
		assert self.browser

		# global dictBrowser
		# dictBrowser = self.browser
		# globalVar.GetApp().set_browser(self.browser)

		# js
		js = cef.JavascriptBindings()
		# external = External()
		# js.SetObject('external', external)
		# js.SetObject('external', globalVar.GetApp())
		js.SetObject('external', GetApp())
		self.browser.SetJavascriptBindings(js)

		self.browser.SetClientHandler(LoadHandler(self))
		self.browser.SetClientHandler(FocusHandler(self))
		self.message_loop_work()

	def get_window_handle(self):
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

	def message_loop_work(self):
		cef.MessageLoopWork()
		self.after(10, self.message_loop_work)

	def on_configure(self, _):
		if not self.browser:
			self.embed_browser()

	def on_root_configure(self):
		# Root <Configure> event will be called when top window is moved
		if self.browser:
			self.browser.NotifyMoveOrResizeStarted()

	def on_mainframe_configure(self, width, height):
		if self.browser:
			if IsWindows():
				WindowUtils.OnSize(self.get_window_handle(), 0, 0, 0)
			elif IsLinux():
				self.browser.SetBounds(0, 0, width, height)
			self.browser.NotifyMoveOrResizeStarted()

	def on_focus_in(self, _):
		# global gLogger

		gLogger.debug("BrowserFrame.on_focus_in")
		if self.browser:
			self.browser.SetFocus(True)

	def on_focus_out(self, _):
		# global gLogger

		gLogger.debug("BrowserFrame.on_focus_out")
		if self.browser:
			self.browser.SetFocus(False)

	def on_root_close(self):
		if self.browser:
			self.browser.CloseBrowser(True)
			self.clear_browser_references()
		self.destroy()

	def clear_browser_references(self):
		# Clear browser references that you keep anywhere in your
		# code. All references must be cleared for CEF to shutdown cleanly.
		self.browser = None

class LoadHandler(object):

	def __init__(self, browser_frame):
		self.browser_frame = browser_frame

	def OnLoadStart(self, browser, **_):
		if self.browser_frame.master.navigation_bar:
			self.browser_frame.master.navigation_bar.set_url(browser.GetUrl())

class FocusHandler(object):

	def __init__(self, browser_frame):
		self.browser_frame = browser_frame

	def OnTakeFocus(self, next_component, **_):
		# global gLogger

		gLogger.debug("FocusHandler.OnTakeFocus, next = {next}"
					 .format(next=next_component))

	def OnSetFocus(self, source, **_):
		# global gLogger

		gLogger.debug("FocusHandler.OnSetFocus, source = {source}"
					 .format(source = source))
		return False

	def OnGotFocus(self, **_):
		"""Fix CEF focus issues (#255). Call browser frame's focus_set
		   to get rid of type cursor in url entry widget."""
		# global gLogger

		gLogger.debug("FocusHandler.OnGotFocus")
		# self.browser_frame.focus_set()

class dictApp():

	def __init__(self):

		self.__enableMove = False
		self.__bAgent = False

		self.__dictBaseLst = []
		self.__nTab = 0
		self.__curDictBase = None

		# root.attributes("-alpha",0.0)

	def __del__(self):
		self.__miss_dict.close()
		self.__miss_audio.close()

	def Start(self, width, height, fileURL):
		self.__nTab = 0
		self.__curDictBase = self.get_curDB()
		self.__DictParseFun = self.__curDictBase.get_parseFun()

		self.__root = tk.Tk()
		self.__window = MainFrame()
		self.__window.Start(self.__root, width, height, fileURL)

	def SetAgent(self, ip, name, program):
		self.__bAgent = True
		self.__Proxy = ip
		self.__Name = name
		self.__Program = program

	def AddAudio(self, name, audioPath):
		self.__auidoArchive = AuidoArchive(audioPath)

	def AddDictBase(self, name, dictSrc, format):
		# global gLogger

		typ = format["Type"]
		if(typ == "ZIP"):
			compression = format["Compression"]
			compresslevel = format["Compress Level"]
			dictBase = GDictBase(dictSrc, compression, compresslevel)
		elif(typ == "SQLite"):
			dictBase = SDictBase(dictSrc)
		elif(typ == "mdx"):
			dictBase = MDictBase(dictSrc)

		self.__dictBaseLst.append(dictBase)

	def get_browser(self):
		return self.__window.get_browser()

	def SwitchTab(self, n):
		self.__nTab = n - 1
		self.__curDictBase = self.get_curDB()
		self.__DictParseFun = self.__curDictBase.get_parseFun()
		# print(self.__nTab)

	def get_curDB(self):
		return self.__dictBaseLst[self.__nTab]

	def mainloop(self):
		self.__window.mainloop()

	def playMP3(self, audio):
		# global gLogger

		gLogger.info("going to play " + audio)
		self.__window.get_browser().ExecuteFunction("playMP3", audio)
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
	# error return
	def download_file(self, url, local):
		# global gLogger

		# try:
		gLogger.info("Going to download %s" %url)
		if(self.__bAgent == True):
			proxy_handler = urllib.request.ProxyHandler({
				'http': self.__Proxy,
				'https': self.__Proxy
			})
			opener = urllib.request.build_opener(proxy_handler)

		else:
			opener = urllib.request.build_opener()

		r = opener.open(url)
		file = open(local, 'wb')
		file.write(r.read())
		file.close()

		# except Exception as ex:
			# gLogger.error("fail to download %s" %url)
			# gLogger.info("Exception: " + str(ex))
			# return False
		# return True

	def OnButtonClicked(self, id):
		# global gLogger

		if id == "btn_close": tk.Tk().quit()
		elif id == "btn_min": self.__window.min()
		else: 
			gLogger.info(id)

	def startMove(self, x, y):
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
		self.__window.geometry("+%s+%s" %(newX, newY))

	def stopMove(self, x, y):
		# gLogger.info("stopMove!")
		self.__enableMove = False
		self.__x = None
		self.__y = None

	def log(self, lvl, info):
		if(lvl == "info"):
			gLogger.info(info)
		elif(lvl == "error"):
			gLogger.error(info)

	def QueryWord(self, word):
		# global gLogger

		gLogger.info("word = %s;" %word)

		# curDictbase = self.get_curDB()

		bDictOK, dict = self.__curDictBase.query_word(word)
		bAudioOK, audio = self.__auidoArchive.query_audio(word)

		if(not bDictOK):
			gLogger.error("dict: " + dict)
			self.RecordMissDict(word)
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
			self.RecordMissAudio(word)
			audio = os.path.join(os.getcwd(), "audio", "WrongHint.mp3")

		tabId = "panel" + str(self.__nTab + 1)

		# gLogger.info(dict)
		if bDictOK:
			self.__window.get_browser().ExecuteFunction(self.__DictParseFun, word, tabId, dict, audio)
		else:
			self.__window.get_browser().ExecuteFunction("dictJson", word, tabId, dict, audio)

	def SetMissRecordFile(self, miss_dict, miss_audio):
		self.__miss_dict = open(miss_dict, mode = "a")
		self.__miss_audio = open(miss_audio, mode = "a")

	def RecordMissDict(self, word):
		self.__miss_dict.write(" " + word)

	def RecordMissAudio(self, word):
		self.__miss_audio.write(" " + word)

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

	def OnSaveHtml(self, html):
		outFile = filedialog.asksaveasfile(mode = 'w', defaultextension = ".html")
		# asksaveasfile return `None` if dialog closed with "cancel".
		if outFile:
			outFile.write(html)
			outFile.close()

if __name__ == '__main__':
	main()