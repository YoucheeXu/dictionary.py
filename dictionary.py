#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Example of embedding CEF Python browser using Tkinter toolkit.
# This example has two widgets: a navigation bar and a browser.
#
# NOTE: This example often crashes on Mac (Python 2.7, Tk 8.5/8.6)
#	   during initial app loading with such message:
#	   "Segmentation fault: 11". Reported as Issue #309.
#
# Tested configurations:
# - Tk 8.5 on Windows/Mac
# - Tk 8.6 on Linux
# - CEF Python v55.3+
#
# Known issue on Linux: When typing url, mouse must be over url
# entry widget otherwise keyboard focus is lost (Issue #255
# and Issue #284).

# pip3 install cefpython3==66.0
# pip3 uninstall cefpython3==56.1

# ver: 1.0.0.7

from cefpython3 import cefpython as cef

import sys, os
import logging as _logging
import time
import base64
import threading
import configparser

# python3
import urllib.request
import urllib.error

# import urllib3
# from urllib3.exceptions import NewConnectionError, ConnectTimeoutError, MaxRetryError,HTTPError,RequestError,ReadTimeoutError,ResponseError

# python2
# import urllib2

# python3
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

from GDictBase import *
from globalVar import *

# Fix for PyCharm hints warnings
WindowUtils = cef.WindowUtils()

# Globals
gLogger = _logging.getLogger("Dictionary")

# Constants
# Tk 8.5 doesn't support png images
IMAGE_EXT = ".png" if tk.TkVersion > 8.5 else ".gif"

def main():

	assert cef.__version__ >= "55.3", "CEF Python v55.3+ required to run this"

	if IsWindows(): print("It's Windows!")
	elif IsLinux(): print("It's Linux!")

	curPath = os.getcwd()
	cfgFile = os.path.join(curPath, "Dictionary.ini")
	cfg = configparser.ConfigParser()  
	cfg.read(cfgFile)

	version = cfg.get("common", "ver")

	bDebug = cfg.getboolean("Debug", "bEnable")
	logFile = cfg.get("Debug", "file")

	# lFile = sys.path[0] + '/log/Dictionary5_log.log'
	lFile = os.path.join(curPath, logFile)

	_logging.basicConfig(level = _logging.DEBUG,
		format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s:\n%(message)s',
		datefmt = '%Y-%m-%d %H:%M:%S',
		filename = lFile,
		filemode = 'a')
	gLogger.setLevel(_logging.INFO)
	# gLogger.setLevel(_logging.NOTSET)
	stream_handler = _logging.StreamHandler()
	# formatter = _logging.Formatter("[%(filename)s] %(message)s")
	formatter = _logging.Formatter(fmt = "L%(lineno)03d %(levelname)s: %(message)s",
                                  datefmt = "%H:%M:%S")  # 创建一个格式化对象
	stream_handler.setFormatter(formatter)
	gLogger.addHandler(stream_handler)

	gLogger.info("CEF Python {ver}".format(ver = cef.__version__))
	gLogger.info("Python {ver} {arch}".format(
			ver = platform.python_version(), arch = platform.architecture()[0]))
	gLogger.info("Tk {ver}".format(ver = tk.Tcl().eval('info patchlevel')))
	gLogger.info("Dictionary {ver}".format(ver = version))

	# global app
	app = dictApp()
	# globalVar.SetApp(app)
	SetApp(app)

	bAgent = cfg.getboolean("Agent", "bAgent")
	Proxy = cfg.get("Agent", "ip")
	app.SetAgent(bAgent, Proxy)

	dictZip = os.path.join(curPath, "dict", "Google.zip")
	# audioZip = os.path.join(curPath, "audio", "Google.zip")
	# app.AddDictBase(dictZip, audioZip)

	# dictPath = os.path.join(curPath, "dict", "Google")
	audioPath = os.path.join(curPath, "audio", "Google")
	# app.AddDictBase(dictPath, audioPath)

	app.AddDictBase(dictZip, audioPath)

	miss_dict = os.path.join(curPath, cfg.get("Miss", "miss_dict"))
	miss_audio = os.path.join(curPath, cfg.get("Miss", "miss_audio"))

	app.SetMissRecordFile(miss_dict, miss_audio)

	width = int(cfg.get("GUI", "Width"))
	height = int(cfg.get("GUI", "Height"))
	fileURL = os.path.join(curPath, cfg.get("GUI", "html"))
	app.Start(width, height, fileURL)

	# cfg.close()

	sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error

	# root = tk.Tk()
	# # root.attributes("-alpha",0.0)
	# global window
	# window = MainFrame(root)

	# Tk must be initialized before CEF otherwise fatal error (Issue #306)
	# settings = {
		# "debug": True,
		# "log_severity": cef.LOGSEVERITY_INFO,
		# "log_file": "log//debug.log"
	# }
	# cef.Initialize(settings = settings)

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
	cef.Initialize()
	app.mainloop()
	cef.Shutdown()

	gLogger.info("All are done!")

# def GetApp(): return globalVar.app

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

	def __init__(self, root, width, height, fileURL):
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
		self.browser_frame = BrowserFrame(self, fileURL, self.navigation_bar)
		self.browser_frame.grid(row = 1, column = 0,
								 sticky = (tk.N + tk.S + tk.E + tk.W))
		tk.Grid.rowconfigure(self, 1, weight = 1)
		tk.Grid.columnconfigure(self, 0, weight = 1)

		# Pack MainFrame
		self.pack(fill = tk.BOTH, expand = tk.YES)

		# self.bind("<Map>", self.frame_mapped)

	def geometry(self, size):
		gLogger.info(size)
		self.__window.geometry(size);

	def on_root_configure(self, _):
		gLogger.debug("MainFrame.on_root_configure")
		if self.browser_frame:
			self.browser_frame.on_root_configure()

	def on_configure(self, event):
		gLogger.debug("MainFrame.on_configure")
		if self.browser_frame:
			width = event.width
			height = event.height
			if self.navigation_bar:
				height = height - self.navigation_bar.winfo_height()
			self.browser_frame.on_mainframe_configure(width, height)

	def on_focus_in(self, _):
		gLogger.debug("MainFrame.on_focus_in")

	def on_focus_out(self, _):
		gLogger.debug("MainFrame.on_focus_out")

	def on_close(self):
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
		# resources = os.path.join(os.path.dirname(__file__), "data")
		icon_path = os.path.join(os.path.dirname(__file__), "main" + IMAGE_EXT)
		if os.path.exists(icon_path):
			self.icon = tk.PhotoImage(file = icon_path)
			# noinspection PyProtectedMember
			self.master.call("wm", "iconphoto", self.master._w, self.icon)

class BrowserFrame(tk.Frame):

	def __init__(self, master, fileURL, navigation_bar = None):
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
		gLogger.debug("BrowserFrame.on_focus_in")
		if self.browser:
			self.browser.SetFocus(True)

	def on_focus_out(self, _):
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
		# self.browser_frame.focus_set()

class dictApp():

	def __init__(self):

		# self.__dictbase = GDictBase()
		# dictPath = os.path.join(curPath, "dict", "Google")
		# audioPath = os.path.join(curPath, "audio", "Google")
		# self.__dictbase.set_path(dictPath, audioPath)

		self.enableMove = False

		# root.attributes("-alpha",0.0)

	def __del__(self):
		self.__miss_dict.close()
		self.__miss_audio.close()

	def Start(self, width, height, fileURL):
		self.__root = tk.Tk()
		self.__window = MainFrame(self.__root, width, height, fileURL)

	def SetAgent(self, bAgent, Proxy):
		self.__bAgent = bAgent
		self.__Proxy = Proxy

	def AddDictBase(self, dictSrc, audioSrc):
		self.__dictbase = GDictBase(dictSrc, audioSrc)

	def get_browser(self):
		return self.__window.get_browser()

	def get_curDB(self):
		return self.__dictbase

	def mainloop(self):
		self.__window.mainloop()

	def playMP3(self, audio):
		gLogger.info("going to play " + audio)
		self.__window.get_browser().ExecuteFunction("playMP3", audio)
		return True

	def dwf_callbackfunc(self, blocknum, blocksize, totalsize):
		'''回调函数
		@blocknum: 已经下载的数据块
		@blocksize: 数据块的大小
		@totalsize: 远程文件的大小
		'''
		percent = 100.0 * blocknum * blocksize / totalsize
		if percent > 100: percent = 100
		gLogger.info("%.2download_filef%%" %percent)

	# To-Do:
	def download_file(self, url, local):
		# headers = {
			# 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
		# }
			# proxy_handler = urllib.request.ProxyHandler({
				# 'http': 'web-proxy.oa.com:8080',
				# 'https': 'web-proxy.oa.com:8080'
			# })
			# opener = urllib.request.build_opener(proxy_handler)
			# urllib.request.install_opener(opener)

			# request = urllib.request.Request(url=url, headers=headers)
			# response = urllib.request.urlopen(request)
			# gLogger.info(response.read().decode('utf-8'))		
		try:
			gLogger.info("Going to download %s" %url)
			if(self.__bAgent == True):
				# proxy = 'http://127.0.0.1:8087'
				# proxy = 'http://10.0.4.225:3128'
				# proxy = 'http://10.0.4.206:8118'

				# python2
				# proxy_handler = urllib2.ProxyHandler({'http': proxy})
				## opener = urllib2.build_opener(proxy_handler, urllib2.ProxyHandler)
				# opener = urllib2.build_opener(proxy_handler)
				# python3
				proxy_handler = urllib.request.ProxyHandler({
					'http': self.__Proxy,
					'https': self.__Proxy
				})
				opener = urllib.request.build_opener(proxy_handler)

			else:
				# python3
				opener = urllib.request.build_opener()

			# urllib2.install_opener(opener)
			# urllib.urlretrieve(url, local, self.dwf_callbackfunc)

			# proxies = {'http': 'http://127.0.0.1:8087'}
			# opener = urllib.FancyURLopener(proxies)
			# opener.retrieve(url, local, self.dwf_callbackfunc)

			r = opener.open(url)
			file = open(local, 'wb')
			file.write(r.read())
			file.close()

		except Exception as ex:
			gLogger.error("fail to download %s" %url)
			gLogger.info("Exception: " + str(ex))
			return False
		return True

	def OnButtonClicked(self, id):
		if id == "btn_close": tk.Tk().quit()
		elif id == "btn_min": self.__window.min()
		else: 
			gLogger.info(id)

	def startMove(self, x, y):
		gLogger.info("startMove!")
		self.enableMove = True
		# self.x = event.x
		self.x = x
		# self.y = event.y
		self.y = y

		self.root_x = self.__root.winfo_rootx()
		self.root_y = self.__root.winfo_rooty()

		gLogger.info("self.x: %d self.y: %d" %(self.x, self.y))
		gLogger.info("self.root_x: %d self.root_y: %d" %(self.root_x, self.root_y))

	def moving(self, x, y):
		if(not self.enableMove): return

		newX = self.root_x + x - self.x 
		# newX = self.winfo_x() + x - self.x 
		newY = self.root_y + y - self.y
		# newY = self.winfo_y() + y - self.y

        # deltax = event.x - self.x
        # deltay = event.y - self.y
        # x = self.winfo_x() + deltax
        # y = self.winfo_y() + deltay

		gLogger.info("newX: %d newY: %d" %(newX, newY))

		# self.__root.geometry("+%s+%s" %(newX, newY))
		self.__window.geometry("+%s+%s" %(newX, newY))

	def stopMove(self, x, y):
		gLogger.info("stopMove!")
		self.enableMove = False
		self.x = None
		self.y = None

	def log(self, info):
		gLogger.info(info)

	def QueryWord(self, word):
		gLogger.info("word = %s" %word)
		# globalVar.GetApp().get_curDB().query_word(word)
		dict, audio = self.get_curDB().query_word(word)
		# gLogger.info("word = %s" %dict)
		# Execute Javascript function
		# self.__window.get_browser().ExecuteFunction("google_search")
		# gLogger.info("dict = " + str(dict))
		# gLogger.info("audio = " + str(audio))
		# if(dict and audio):
		if(dict):
			self.__window.get_browser().ExecuteFunction("google_dict", word, dict, audio)
		else:
			gLogger.info("miss dict of %s" %word)
			self.RecordMissDict(word)

		if(audio):
			# self.speechWord(word, True);
			self.speechWord(audio)
		else:
			gLogger.info("miss audio of %s" %word)
			self.RecordMissAudio(word)

	def SetMissRecordFile(self, miss_dict, miss_audio):
		self.__miss_dict = open(miss_dict, mode = "a")
		self.__miss_audio = open(miss_audio, mode = "a")

	def RecordMissDict(self, word):
		self.__miss_dict.write(" " + word)

	def RecordMissAudio(self, word):
		self.__miss_audio.write(" " + word)

	def speechWord(self, word, isUs):
		# gLogger.info("going to speech %s" %word)
		# mp3 = sys.path[0] + "\\Audio\\Google\\" + word + ".mp3"
		mp3 = os.path.join(os.getcwd(), "audio/Google/" + word + ".mp3")
		gLogger.info("mp3 = %s" %mp3)
		if os.path.isfile(mp3) == False:
			gLogger.error("The is no mp3: " + mp3)
			msgBox.showerror(word, "The is no mp3: " + mp3)
			return "break"

		try:
			self.playMP3(mp3)
		except Exception as ex:
			gLogger.error("wrong mp3: " + mp3)
			msgBox.showerror(word, "wrong mp3: " + mp3)
			gLogger.info(Exception + ": " + ex)

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
		wdsLst = []
		# gLogger.info("OnTextChanged: word = ", word)
		# ret = globalVar.GetApp().get_curDB().get_wordslst(wdsLst, word)
		ret = self.get_curDB().get_wordsLst(wdsLst, word)
		if (not ret): 
			# gLogger.info("OnTextChanged: no similiar words!")
			return False

		for wd in wdsLst:
			self.__window.get_browser().ExecuteFunction("append_words_list", wd)
			# gLogger.info("found word: %s" %wd)

	def wrongJson(self, word): 
		ret = self.__dictbase.del_word(word)
		if ret == True: 
			# msgBox.showinfo("Info", "Success to delete " + word)
			gLogger.info("Success to delete: " + word)

	def OnSaveHtml(self, html):
		outFile = filedialog.asksaveasfile(mode = 'w', defaultextension = ".html")
		# asksaveasfile return `None` if dialog closed with "cancel".
		if outFile:
			outFile.write(html)
			outFile.close()

if __name__ == '__main__':
	main()