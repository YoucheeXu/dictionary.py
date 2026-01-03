#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ver 1.0.0.6

'''
To-Do:
* display log in console												wait to test
* word is added to learn list only once in test mode, and hint it		wait to test
* give up rember word to display word in "Next"							wait to test
'''


import sys, os, platform

import ctypes
try:	# python3
	import tkinter as tk
	import tkinter.messagebox as msgBox
except ImportError:
	import Tkinter as tk
	import tkMessageBox as msgBox

WINDOWS = (platform.system() == "Windows")
LINUX = (platform.system() == "Linux")
MAC = (platform.system() == "Darwin")

from src.sdictbase import SDictBase
import logging as _logging
import configparser
import string
import datetime
import time
import random

# Globals
global gLogger
gLogger = _logging.getLogger("ReciteWords6")
global app

def main():
	global app

	# lFile = sys.path[0] + "\\log\\recite_" + str(datetime.date.today()) + "_log.log"
	lFile = os.path.join(sys.path[0], "log", "reciteLog.log")
	_logging.basicConfig(level = _logging.DEBUG,
		format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s:\n%(message)s',
		datefmt = '%Y-%m-%d %H:%M:%S',
		filename = lFile,
		filemode = 'w')
	#定义一个StreamHandler，将DEBUG级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
	stream_handler = _logging.StreamHandler()
	# gLogger.setLevel(_logging.DEBUG)
	gLogger.setLevel(_logging.INFO)
	# formatter = _logging.Formatter('%(levelname)s - %(message)s')
	formatter = _logging.Formatter(fmt = "L%(lineno)03d %(levelname)s: %(message)s",
                                  datefmt = "%H:%M:%S")  # 创建一个格式化对象	
	stream_handler.setFormatter(formatter)
	gLogger.addHandler(stream_handler)

	gLogger.info(str(datetime.date.today()))
	gLogger.info(platform.python_version())
	try:
		root = tk.Tk()
		#root.geometry("800x600")
		app = MyApp(root)
		root.mainloop()
	except Exception as ex:
		print(Exception, ": ", ex)

class MainFrame(tk.Toplevel):
	""""""

	#----------------------------------------------------------------------
	def __init__(self, size):
		"""Constructor"""
		tk.Toplevel.__init__(self)

		self.__Mode = tk.StringVar()
		self.__Symbol = tk.StringVar()
		self.__Score = tk.StringVar()
		self.__CurCountStr = tk.StringVar()
		self.__numOfWords = tk.StringVar()
		self.__numOfLearn = tk.StringVar()
		self.__numOfTest = tk.StringVar()

		self.__initGUI()
		self.__initDict()

		self.bind("<F5>", self.__Play_Again)
		self.bind("<F6>", self.__Forgoten)
		self.bind("<F7>", self.__Chop)

		self.protocol('WM_DELETE_WINDOW', self.onCloseWindow)

		self.__Mode.set("Study Mode")
		self.__Symbol.set("")
		self.__Score.set("")
		self.__CurCountStr.set("")
		self.__numOfWords.set("")
		self.__numOfLearn.set("__numOfLearn")
		self.__numOfTest.set("__numOfTest")

		self.__WordsDict = {}

		self.__LearnLst = []
		self.__CurLearnLst = []
		self.__CurLearnPos = 0
		self.__TestLst = []
		self.__CurTestLst = []
		self.__CurTestPos = 0

		self.__TestCount = 0
		self.__ErrCount = 3
		self.__CurCount = 1

	def __initGUI(self):

		tk.Label(self, textvariable = self.__Mode).grid(row = 0, column = 1)

		self.__wordInput = tk.Entry(self)
		self.__wordInput.bind("<Return>", self.__Check_Input)
		self.__wordInput.focus_set()
		self.__wordInput.grid(row = 1, column = 1)

		tk.Label(self, textvariable = self.__Symbol).grid(row = 2, column = 1)

        # , state = tk.DISABLED
		self.__Content = tk.Text(self, height = 12, width = 65)
		self.__Content.grid(row = 3,  column = 0, columnspan = 3, sticky = tk.W + tk.E + tk.N + tk.S, padx = 5, pady = 5)

		tk.Button(self, text = "再读一遍(F5)", command = self.__Play_Again).grid(row = 4, column = 0)
		# self.__ForgotenButton = tk.Button(self, text = "忘记了！(F6)", command = self.__Forgoten, state = "disabled")
		self.__ForgotenButton = tk.Button(self, text = "忘记了！(F6)", command = self.__Forgoten)
		self.__ForgotenButton.grid(row = 4, column = 1)

		tk.Button(self, text = "斩！(F7)", command = self.__Chop).grid(row = 4, column = 2)

		tk.Label(self, textvariable = self.__CurCountStr).grid(row = 5, column = 1)
		tk.Label(self, textvariable = self.__Score).grid(row = 6, column = 1)
		tk.Label(self, textvariable = self.__numOfLearn).grid(row = 7, column = 0)
		tk.Label(self, textvariable = self.__numOfWords).grid(row = 7, column = 1)
		tk.Label(self, textvariable = self.__numOfTest).grid(row = 7, column = 2)

		self.update()

		width = self.winfo_reqwidth()
		height = self.winfo_reqheight()

		screenwidth = self.winfo_screenwidth()  
		screenheight = self.winfo_screenheight()  
		size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)

		self.geometry(size)

		#self.positionfrom((screenwidth - width)/2, (screenheight - height)/2)

		self.title("Study Mode")
		self.resizable(False, False)

		return "break"

	def __initDict(self):

		# sFile = sys.path[0] + "\\dict\\15000.dict"
		sFile = os.path.join(sys.path[0], "dict", "15000.dict")
		print("sFile = ", sFile)
		if os.path.isfile(sFile) == False:
			_logging.error("The is no dict: " + sFile)
			#self.__Exit_App()
			os._exit(-1)

		self.__mySDict = SDictBase()
		if self.__mySDict.open(sFile) == False:
			_logging.error("can't open: " + sFile)
			self.__Exit_App()

		# audio = sys.path[0] + "\\Audio\\Google.zip"
		# if os.path.isfile(audio) == False:
			# _logging.error("There is no audio: " + audio)
			# self.__Exit_App()

		# self.__audioFile = zipfile.ZipFile(audio, "r")
		# #_logging.info(__audioFile.namelist())

	def __GoStudyMode(self):
		self.__Mode.set("Study Mode")
		self.title("Study Mode")
		gLogger.info("Study Mode")
		self.__ForgotenButton.config(state = 'disabled')

		self.__CurCountStr.set("")

		self.__CurLearnPos = 0
		l = len(self.__LearnLst)
		if l > 10:
			self.__CurLearnLst = self.__LearnLst[0:10]
			del self.__LearnLst[0:10]
		elif l <= 0:
			self.__CurLearnLst = []
			self.__GoTestMode()
		else: 
			self.__CurLearnLst = self.__LearnLst[:]
			self.__LearnLst = []

		self.__numOfLearn.set("%d words to Learn!" %(len(self.__LearnLst)))
		self.__Study_Next()

	def __Study_Next(self):
		l = len(self.__CurLearnLst)
		if l > 0: 
			word = self.__CurLearnLst[self.__CurLearnPos]

			lastDate = self.__mySDict.get_item(word, "LastDate")

			if lastDate == None: self.__Score.set("New!")
			else: self.__Score.set("")

			# gLogger.info("LearnPos: %d" %(self.__CurLearnPos))
			# logstr = "LearnWord: %s, familiar: %.2f" %(word, self.__WordsDict[word])
			# print(type(self.__WordsDict[word]))
			gLogger.info("LearnWord: %s, familiar: %.1f" %(word, self.__WordsDict[word]))
			# gLogger.info(logstr)

			self.__Show_Content(word)
			self.__Play_MP3(word)

			self.__numOfWords.set(str(self.__CurLearnPos + 1) + " of " + str(l))

			self.__CurLearnPos += 1
		# else: 
			# self.__CurCount = 1
			# self.__CurTestLst = self.__CurLearnLst[:]
			# self.__GoTestMode()

	def __GoTestMode(self):
		self.__Mode.set("Test Mode")
		self.title("Test Mode")
		gLogger.info("Test Mode")
		self.__ForgotenButton.config(state = 'normal')

		if self.__CurCount <= self.__TestCount:
			#self.__CurCount += 1
			self.__CurCountStr.set("Count: %d of %d" %(self.__CurCount, self.__TestCount))
			self.__CurTestPos = 0
			self.__Clear_Content()
			# random.shuffle(self.__CurTestLst)

			self.__numOfTest.set("%d words to Test!" %(len(self.__TestLst)))
			self.__Test_Next()
		elif len(self.__CurLearnLst) > 0: 
			# random.shuffle(self.__LearnLst)
			self.__GoStudyMode()
		elif len(self.__TestLst) > 10:
			self.__CurTestLst = self.__TestLst[0:10]
			del self.__TestLst[0:10]
			self.__CurTestPos = 0
			self.__CurCount = 1
			self.__GoTestMode()
		elif len(self.__TestLst) > 0:
			self.__CurTestLst = self.__TestLst[:]
			del self.__TestLst[:]
			self.__TestLst = []
			self.__CurTestPos = 0
			self.__CurCount = 1
			self.__GoTestMode()
		elif len(self.__LearnLst) > 0:
			random.shuffle(self.__LearnLst)
			self.__GoStudyMode()
		else:
			self.__Save_Progress()
			self.__Exit_App()

	def __Test_Next(self):

		# _logging.info("TestPos: %d" %(self.__CurTestPos))
		word = self.__CurTestLst[self.__CurTestPos]
		_logging.info("TestWord: %s, familiar: %.1f" %(word, self.__WordsDict[word]))

		self.__Play_MP3(word)

		if self.__CurTestPos >= 1:
			lastWord = self.__CurTestLst[self.__CurTestPos - 1]
		else: lastWord = self.__CurTestLst[-1]

		if not(self.__CurTestPos == 0 and self.__CurCount == 1): self.__Show_Content(lastWord)
		self.__wordInput.delete(0, tk.END)

		self.__numOfWords.set(str(self.__CurTestPos + 1) + " of " + str(len(self.__CurTestLst)))

		self.__CurTestPos += 1

	def __Check_Input(self, event = None):

		#self.__numOfLearn.set("%d words to Learn!" %(len(self.__LearnLst)))
		#self.__numOfTest.set("%d words to Test!" %(len(self.__TestLst)))

		if self.__Mode.get() == "Study Mode":
			if self.__CurLearnPos < len(self.__CurLearnLst):
				self.__Study_Next()
			else:
				self.__CurCount = 1
				_logging.info("curCount: %d" %(self.__CurCount))
				self.__CurTestLst = self.__CurLearnLst[:]
				self.__GoTestMode()
				# self.__LearnLst = []
				# self.__CurTestPos = 0

				# self.__clear_content()
				# random.shuffle(self.__TestLst)
				# self.__Test_Next()
		else:
			input_word = self.__wordInput.get()
			word = self.__CurTestLst[self.__CurTestPos - 1]
			if input_word != word: 
				# self.__WordsDict[word] -= 1
				self.__Score.set("Wrong!")
				# self.__LearnLst.append(word)
				self.__numOfLearn.set("%d words to Learn!" %(len(self.__LearnLst)))
				_logging.info("ErrCount: %d", self.__ErrCount)
				_logging.info("Right word: %s, Wrong word: %s." %(word, input_word))
				if self.__ErrCount == 3:
					self.__CurTestPos -= 1
					self.__ErrCount -= 1
					self.__WordsDict[word] -= 0
					# self.__LearnLst.append(word)
				elif self.__ErrCount > 0:
					self.__CurTestPos -= 1
					self.__ErrCount -= 1
					self.__WordsDict[word] -= 1
					# self.__LearnLst.append(word)
				else:
					self.__ErrCount = 3
					#self.__CurTestPos -= 1
					self.__Play_MP3(word)
					self.__Show_Content(word)
					self.__wordInput.delete(0, tk.END)
					self.__wordInput.insert(tk.END, word)
					self.__Score.set("Go on!")
					# _logging.info("LearnLst = " + "".join(list(str(self.__LearnLst))))
					self.__WordsDict[word] -= 1
					self.__LearnLst.append(word)
					_logging.info(word + " has been added in learn list.")
					return
			else: 
				self.__Score.set("OK!")
				self.__ErrCount = 3

			if self.__CurTestPos < len(self.__CurTestLst):
				self.__wordInput.delete(0, tk.END)
				self.__Test_Next()
			else: 
				self.__CurCount += 1
				_logging.info("curCount: %d" %(self.__CurCount))
				self.__GoTestMode()

	def __Chop(self, event = None):

		word = ""
		if self.__Mode.get() == "Study Mode": 
			self.__CurLearnPos -= 1
			if self.__CurLearnPos <= 0: self.__CurLearnPos = 0
			word = self.__CurLearnLst[self.__CurLearnPos]

			# if self.__WordsDict[word] != None: del self.__WordsDict[word]
			# while word in self.__WordsDict: del self.__WordsDict[word]

			while word in self.__CurLearnLst:
				self.__CurLearnLst.remove(word)

			while word in self.__LearnLst:
				self.__LearnLst.remove(word)

			while word in self.__CurTestLst:
				self.__CurTestLst.remove(word)

			while word in self.__TestLst:
				self.__TestLst.remove(word)

			# _logging.info(word + " is forgoten.")
			
			if self.__CurLearnPos < len(self.__CurLearnLst):
				self.__Study_Next()
			else: 
				self.__CurCount = 1
				_logging.info("curCount: %d" %(self.__CurCount))
				self.__CurTestLst = self.__CurLearnLst[:]
				self.__GoTestMode()

		else:
			self.__CurTestPos -= 1
			if self.__CurTestPos <= 0: self.__CurTestPos = 0
			word = self.__CurTestLst[self.__CurTestPos]

			while word in self.__CurLearnLst:
				self.__CurLearnLst.remove(word)

			while word in self.__LearnLst:
				self.__LearnLst.remove(word)

			while word in self.__CurTestLst:
				self.__CurTestLst.remove(word)

			while word in self.__TestLst:
				self.__TestLst.remove(word)

			# _logging.info(word + " is forgoten.")

			# if self.__WordsDict[word] != None: del self.__WordsDict[word]
			# while word in self.__WordsDict: del self.__WordsDict[word]

			if self.__CurTestPos < len(self.__CurTestLst):
				self.__Test_Next()
			else: 
				self.__CurCount += 1
				_logging.info("curCount: %d" %(self.__CurCount))
				self.__GoTestMode()

		self.__WordsDict[word] = 10

		_logging.info("%s has been chopped!" %(word))

	def __Forgoten(self, event = None):
		word = ""

		if self.__Mode.get() == "Test Mode":
			self.__CurTestPos -= 1
			if self.__CurTestPos <= 0: self.__CurTestPos = 0
			word = self.__CurTestLst[self.__CurTestPos]

			while word in self.__CurTestLst:
				self.__CurTestLst.remove(word)

			while word in self.__TestLst:
				self.__TestLst.remove(word)

			self.__WordsDict[word] -= 5
			self.__LearnLst.append(word)

			_logging.info(word + " is forgoten.")

			if self.__CurTestPos < len(self.__CurTestLst):
				self.__Test_Next()
			else: 
				self.__CurCount += 1
				_logging.info("curCount: %d" %(self.__CurCount))
				self.__GoTestMode()

		#self.__WordsDict.pop(word)

		# _logging.info("length of WordsDict: %d" %(len(self.__WordsDict)))
		# # _logging.info("WordsDict: \r\n", self.__WordsDict)

		# _logging.info("length of TestWordsList: %d" %(len(self.__TestLst)))
		# # _logging.info("TestWordsList: \r\n", self.__TestLst)

		# _logging.info("length of LearnWordsList: %d" %(len(self.__LearnLst)))
		# # _logging.info("LearnWordsList: \r\n", self.__LearnLst)

		return word

	def __Clear_Content(self):
		self.__wordInput.delete(0, tk.END)
		self.__Symbol.set("")
		self.__Content.delete(1.0, tk.END)

	def __Play_Again(self, event = None):
		word = ""
		if self.__Mode.get() == "Study Mode": 
			word = self.__CurLearnLst[self.__CurLearnPos - 1]
		else: 
			word = self.__CurTestLst[self.__CurTestPos - 1]
		self.__Play_MP3(word)

	def __Play_MP3(self, word):
		# mp3 = sys.path[0] + "\\Audio\\Google\\" + word + ".mp3"
		# mp3 = os.path.join(sys.path[0], "audio", "Google", word + ".mp3")
		mp3 = os.path.join(sys.path[0], "audio", "Google", word[0], word + ".mp3")
		print("mp3 = ", mp3)
		if os.path.isfile(mp3) == False:
			_logging.error("There is no mp3: " + mp3)
			return "break"

		if (WINDOWS == True):
			import mp3play
			try:
				clip = mp3play.load(mp3)
				clip.play()
				time.sleep(min(30, clip.seconds() + 0.3))
				clip.stop()
			except:
				_logging.error("wrong mp3: " + mp3)
		elif (LINUX == True):
			os.system("mplayer " + mp3)

	def __Play_MP3_2(self, word):

		word += ".mp3"

		if word in self.__audioFile.namelist():
			mp3 = self.__audioFile.read(word)
		else:
			_logging.error("can't find %s." %(word))
			return False

		#2.创建合成器对象，解析出最初的几帧音频数据
		import pymedia.muxer as muxer
		dm = muxer.Demuxer('mp3')
		frames = dm.parse(mp3)
		_logging.info(len(frames))

		#3.根据解析出来的 Mp3 编码信息，创建解码器对象
		import pymedia.audio.acodec as acodec
		dec = acodec.Decoder(dm.streams[0])
		#像下面这样也行
		#params = {'id': acodec.getCodecID('mp3'), 'bitrate': 128000, 'sample_rate': 44100, 'ext': 'mp3', 'channels': 2}
		#dec= acodec.Decoder(params)

		#4.解码第一帧音频数据
		frame = frames[0]
		#音频数据在 frame 数组的第二个元素中
		#r = dec.decode(frame[1])
		r = dec.decode(mp3)
		_logging.info("sample_rate:%s, channels:%s" %(r.sample_rate,r.channels))
		#注意：这一步可以直接解码 r = dec.decode(data)，而不用读出第一帧音频数据
		#但是开始会有一下噪音，如果是网络流纯音频数据，不包含标签信息，则不会出现杂音

		#5.创建音频输出对象
		import pymedia.audio.sound as sound
		snd = sound.Output(r.sample_rate, r.channels, sound.AFMT_S16_LE)

		#6.播放
		if r: snd.play(r.data)

		# #7.继续读取、解码、播放
		# while True:
			# data = f.read(512)
			# if len(data)>0:
				# r = dec.decode(data)
				# if r: snd.play(r.data)
			# else:
				# break

		#8.延时，直到播放完毕
		import time
		while snd.isPlaying(): time.sleep(.5)

	def __Show_Content(self, word):

		self.__Clear_Content()
		self.__wordInput.insert(tk.END, word)

		txtLst = []

		if self.__mySDict.get_all(word, txtLst):

			symbol = txtLst[1]
			if symbol:
				# self.__Content.insert(END, symbol.strip())
				# self.__Content.insert(END, "\r\n")
				self.__Symbol.set("[" + symbol + "]")

			meaning = txtLst[2]

			self.__Content.insert(tk.END, meaning.strip())
			self.__Content.insert(tk.END, "\r\n\r\n")

			if txtLst[3] == None: return

			sentenses = txtLst[3].split("/r/n")
			i = 0
			for item in sentenses:
				#_logging.info(item.strip())
				i += 1
				self.__Content.insert(tk.END, item.strip())
				self.__Content.insert(tk.END, "\r\n")
				if i == 2:
					self.__Content.insert(tk.END, "\r\n")
					i = 0

	def Go(self):
		self.__today = datetime.date.strftime(datetime.date.today(), "%Y-%m-%d")

		# read configure file
		# cfgFile = sys.path[0] + "\\Data\\ReciteWords.ini"
		cfgFile = os.path.join(sys.path[0], "ReciteWords.ini")
		cfg = configparser.ConfigParser()  
		cfg.read(cfgFile)

		level = cfg.get("Words", "target")
		# limit = string.atoi(cfg.get("StudyMode", "limit"))
		limit = int(cfg.get("StudyMode", "limit"))
		# familiar = cfg.get("StudyMode", "familiar")
		# self.__TestCount = string.atoi(cfg.get("StudyMode", "count"))
		self.__TestCount = int(cfg.get("StudyMode", "count"))

		# update conunt

		where = "level = '" + level + "'"
		allCount = self.__mySDict.get_count(where)

		where = "level = '" + level + "' and familiar > 0"
		needCount = allCount - self.__mySDict.get_count(where)

		where = "level = '" + level + "' and LastDate is null "
		newCount = self.__mySDict.get_count(where)

		where = "level = '" + level + "' and familiar = 10"
		finishCount = self.__mySDict.get_count(where)

		global app
		app.update_count(allCount, needCount, newCount, finishCount)

		self.__LearnLst = []
		self.__TestLst = []
		self.__WordsDict = {}

		wdsLst = []

		# get forgot words
		familiar = -10.0
		words_len = 0

		newWdsLst = []

		while(words_len < limit and familiar <= 0):
			where = "level = '" + level + "' and familiar = " + str(familiar) + " limit " + str(limit - words_len)
			if self.__mySDict.get_wordslst(wdsLst, where):
				for item in wdsLst:
					for wd in item:
						# self.__WordsDict[wd] = string.atof(familiar)
						self.__WordsDict[wd] = familiar
						# print(wd, type(self.__WordsDict[wd]))
						# self.__LearnLst.append(wd)
						newWdsLst.append(wd)
				wdsLst = []
				# words_len = len(self.__LearnLst)
				words_len = len(newWdsLst)
			familiar += 0.5
			#_logging.info(familiar)
			familiar = round(familiar, 1)

		# random.shuffle(self.__LearnLst)

		forgotWdsLst = []

		_logging.info("len of raw new words: %d." %(len(newWdsLst)))
		for wd in newWdsLst: 
			lastDate = self.__mySDict.get_item(wd, "LastDate")
			# print(lastDate, wd)
			if lastDate != None: 
				forgotWdsLst.append(wd)
				# newWdsLst.remove(wd)
		for wd in forgotWdsLst: newWdsLst.remove(wd)

		self.__LearnLst.extend(forgotWdsLst)
		_logging.info("len of forgot words: %d." %(len(forgotWdsLst)))
		_logging.info("len of new words: %d." %(len(newWdsLst)))

		words_len = len(self.__LearnLst)

		#get old words
		timeLst = []
		for i in range(4, 9):
			tmp = cfg.get("Time", "Time" + str(i))
			# date = string.atoi(tmp[:-1])
			date = int(tmp[:-1])
			# _logging.info("date" + str(i) + ": " + tmp)
			timeLst.append(date)

		timeLst = timeLst[::-1]
		# _logging.info("timeLst: ")
		# _logging.info(timeLst)
		# _logging.info("timeLst: ", timeLst)
		_logging.info("timeLst = " + "".join(list(str(timeLst))))

		oldword_limit = limit*len(timeLst) - words_len

		familiar = 0.0
		words_len = 0

		due2test_num = 0

		lastlastdate = datetime.date.strftime(datetime.date.today(), "%Y-%m-%d") 

		for day in timeLst:
			selDate = datetime.date.today() - datetime.timedelta(day)
			# _logging.info("selDate:", selDate)
			lastdate = datetime.date.strftime(selDate, "%Y-%m-%d")

			if day == timeLst[0]:
				where = "level = '" + level + "' and lastdate <= date('" + lastdate + "') and familiar < 10"
			else:
				where = "level = '" + level + "' and lastdate <= date('" + lastdate + "') and lastdate > date('" + lastlastdate + "') and familiar < 10"

			num = self.__mySDict.get_count(where)

			_logging.info(lastdate + " day: " + str(day) + " "+ str(num) + " Words due to test.")

			due2test_num += num

			if (words_len < oldword_limit):
				# lastdate = datetime.date.strftime(selDate, "%Y-%m-%d")
				# _logging.info("lastdate: " + lastdate)
				# where = "level = '" + level + "' and lastdate <= date('" + lastdate + "') and familiar < 10 order by familiar limit " + str(oldword_limit - words_len)
				# where = "level = '" + level + "' and lastdate <= date('" + lastdate + "') and lastdate > date('" + lastlastdate + "') and familiar < 10 order by familiar limit " + str(oldword_limit - words_len)
				where += " order by familiar limit " + str(oldword_limit - words_len)
				if self.__mySDict.get_wordslst(wdsLst, where):
					i = 0
					for item in wdsLst:
						for wd in item:
							# self.__WordsDict[wd] = string.atof(self.__mySDict.get_item(wd, "familiar"))
							self.__WordsDict[wd] = self.__mySDict.get_item(wd, "familiar")
							# _logging.info("word: %s, familiar: %f" %(wd, self.__WordsDict[wd]))
							# print(wd, type(self.__WordsDict[wd]))
							self.__TestLst.append(wd)
							i += 1
					wdsLst = []
					words_len = len(self.__TestLst)
					_logging.info("lastdate: " + lastdate + ", len: " + str(i))
			# else: break
			lastlastdate = lastdate

		_logging.info("Words due to test: %d", due2test_num)

		# _logging.info("TestLst = " + "".join(list(str(self.__TestLst))))
		self.__TestLst.extend(self.__LearnLst)

		words_len = limit*len(timeLst) - len(self.__TestLst)
		print("left %d words for new" %words_len)
		if words_len > 0: 
			self.__TestLst.extend(newWdsLst[:words_len - 1])
			self.__LearnLst.extend(newWdsLst[:words_len - 1])

		for wd in newWdsLst[words_len:]:
			if wd in self.__WordsDict: del self.__WordsDict[wd]

		random.shuffle(self.__LearnLst)

		_logging.info("len of all TestWordsList: %d." %(len(self.__TestLst)))
		self.__TestLst = list(set(self.__TestLst))	# remove duplicate item 
		_logging.info("len of no repeat all TestWordsList: %d." %(len(self.__TestLst)))
		# _logging.info("WordsDict = " + str(self.__WordsDict))
		# _logging.info("len of WordsDict: %d: " %(len(self.__WordsDict)))
		# _logging.info(self.__LearnLst)
		# _logging.info("LearnLst = " + "".join(list(str(self.__LearnLst))))
		_logging.info("len of LearnList: %d." %(len(self.__LearnLst)))
		#self.__wordInput['state'] = 'readonly'

		self.__numOfLearn.set("%d words to Learn!" %(len(self.__LearnLst)))
		self.__numOfTest.set("%d words to Test!" %(len(self.__TestLst)))
		self.__GoStudyMode()

	def __Save_Progress(self):
		#_logging.info("WordsDict: ", self.__WordsDict)
		print("len of self.__WordsDict: %d" %len(self.__WordsDict))
		_logging.info("WordsDict = " + str(self.__WordsDict))

		# today = datetime.date.strftime(datetime.date.today(), "%Y-%m-%d")

		for word in self.__LearnLst:
			# if self.__WordsDict[word] != None: del self.__WordsDict[word]
			if word in self.__WordsDict: del self.__WordsDict[word]

		for word in self.__TestLst:
			# if self.__WordsDict[word] != None: del self.__WordsDict[word]
			if word in self.__WordsDict: del self.__WordsDict[word]
			
		if self.__Mode.get() == "Study Mode": 
			for word in self.__CurLearnLst:
				if word in self.__WordsDict: del self.__WordsDict[word]
		else:
			for word in self.__CurTestLst: 
				if word in self.__WordsDict: del self.__WordsDict[word]

		print("len of self.__WordsDict: %d" %len(self.__WordsDict))
		print("WordsDict = " + str(self.__WordsDict))

		itmLst = ['familiar', 'lastdate']

		for word, familiar in self.__WordsDict.items():

			familiar += 1.0

			if familiar > 10: familiar = 10.0
			if familiar < -10: familiar = -10.0

			familiar = round(familiar, 1)

			valLst = []
			valLst.append(str(familiar))
			valLst.append("date('" + self.__today + "')")
			valueDict = dict(zip(itmLst, valLst))

			_logging.info(word + ": " + str(valueDict))

			#self.__mySDict.update_item(word, "familiar", str(familiar))
			self.__mySDict.update(word, valueDict)

		# _logging.info("TestWordsList: ")
		# _logging.info(self.__TestLst)
		# _logging.info("LearnWordsList: ")
		# _logging.info(self.__LearnLst)

	def onCloseWindow(self):
		result = msgBox.askyesno(self.__Mode.get(), "Are you goning to quit?")
		if result == True: 
			self.__Save_Progress()
			self.__Exit_App()
		else: return

	def __Exit_App(self, event = None):
		self.__mySDict.close()
		# self.__logFile.close()
		os._exit(0)

########################################################################
class MyApp(object):

	def __init__(self, parent):
		"""Constructor"""
		self.root = parent
		self.root.title("Main frame")
		self.frame = tk.Frame(parent)
		self.frame.pack()

		self.state = False

		self.__allCount = tk.StringVar()
		self.__allCount.set("")
		self.__needCount = tk.StringVar()
		self.__needCount.set("")
		self.__newCount = tk.StringVar()
		self.__newCount.set("")
		self.__finishCount = tk.StringVar()
		self.__finishCount.set("")


		self.__btnStudy = tk.Button(self.frame, text = "开始学习(↲)", command = self.__openFrame)
		self.__btnStudy.pack()

		tk.Label(self.frame, textvariable = self.__allCount).pack()
		tk.Label(self.frame, textvariable = self.__needCount).pack()
		tk.Label(self.frame, textvariable = self.__newCount).pack()
		tk.Label(self.frame, textvariable = self.__finishCount).pack()

		self.root.protocol('WM_DELETE_WINDOW', self.__onCloseWindow)

		self.root.bind("<Escape>", self.__exit_app)
		self.root.bind("<Return>", self.__openFrame)

		self.toggle_fullscreen()

		#self.__openFrame()

	#----------------------------------------------------------------------
	def __hide(self):
		""""""
		self.root.withdraw()
 
	#----------------------------------------------------------------------
	def __openFrame(self, event = None):
		""""""
		#self.hide()
		# width = 600
		# height = 420

		# self.__btnStudy.state = tk.DISABLED

		self.__btnStudy['state'] = 'disabled'

		width = self.root.winfo_reqwidth()
		height = self.root.winfo_reqheight()

		screenwidth = self.root.winfo_screenwidth()  
		screenheight = self.root.winfo_screenheight()  
		size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)

		self.__mainFrame = MainFrame(size)
		self.__mainFrame.Go()

		# handler = lambda: self.onCloseFrame(mainFrame)
		# btn = tk.Button(mainFrame, text = "Close", command = handler)
		# btn.pack()

	def toggle_fullscreen(self, event = None):
		self.state = not self.state  # Just toggling the boolean
		self.root.attributes("-fullscreen", self.state)
		return "break"

	def update_count(self, allCount, needCount, newCount, finishCount):
		self.__allCount.set("All words: %d" %allCount)
		self.__needCount.set("Need to learn Word: %d" %needCount)
		self.__newCount.set("New words to learn: %d" %newCount)
		self.__finishCount.set("Words has recited: %d" %finishCount)
		return

	#----------------------------------------------------------------------
	def __onCloseFrame(self, frame):
		""""""
		frame.destroy()
		self.__show()

	def __onCloseWindow(self):
		# result = msgBox.askyesno(self.__Mode.get(), "Are you goning to quit?")
		# if result == True:
			# self.__mainFrame.onCloseWindow()
		# else: return

		self.__mainFrame.onCloseWindow()
		return
 
	#----------------------------------------------------------------------
	def __show(self):
		""""""
		self.root.update()
		self.root.deiconify()

	def __exit_app(self, event = None):
		self.__onCloseWindow()
		# os._exit(0)

#----------------------------------------------------------------------
if __name__ == "__main__":
	main()
