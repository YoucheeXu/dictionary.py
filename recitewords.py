#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import platform
import datetime
import time
import random
import json

try:	# python3
	import tkinter as tk
	import tkinter.messagebox as msgBox
except ImportError:
	import Tkinter as tk
	import tkMessageBox as msgBox

from src.usrprogress import UsrProgress
from src.sdictbase import SDictBase
from src.auidoarchive import AuidoArchive
from src.globalvar import *
from src.utils import *


def main():
	global gApp, gLogger, gCfg

	curPath = os.getcwd()
	cfgFile = os.path.join(curPath, "ReciteWords.json")
	# print("cfgFile : " + cfgFile)
	# print(cfgFile)
	with open(cfgFile, 'rb') as f:
		datum = f.read()
	gCfg = json.loads(datum, strict = False)

	version = gCfg["Common"]["ver"]

	bDebug = gCfg["Debug"]["Enable"]
	logFile = None
	
	if bDebug:
		logFile = gCfg["Debug"]["File"]

	lFile = os.path.join(curPath, logFile)

	gLogger = CreateLogger("ReciteWords", logFile)
	SetLogger(gLogger)

	gLogger.info(str(datetime.date.today()))
	# gLogger.info(platform.python_version())
	gLogger.info("Python {ver} {arch}".format(
			ver = platform.python_version(), arch = platform.architecture()[0]))
	gLogger.info("Tk {ver}".format(ver = tk.Tcl().eval('info patchlevel')))
	gLogger.info("ReciteWords {ver}".format(ver = version))

	try:
		root = tk.Tk()
		#root.geometry("800x600")
		gApp = MyApp(root)
		SetApp(gApp)
		root.mainloop()
	except Exception as ex:
		gLogger.error(Exception, ": ", ex)

class MainFrame(tk.Toplevel):
	""""""
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
		# global gLogger

		curPath = os.getcwd()
		gLogger.info("curPath: %s" %curPath)
		dict = "dict\\15000.dict"
		dictFile = os.path.join(curPath, dict)
		gLogger.info("dict: %s" %dictFile)
		audio = "audio\\Google-us.zip"
		audioFile = os.path.join(curPath, audio)
		gLogger.info("audio: %s" %audioFile)
		progress = "dict\\XYQ.progress"
		progressFile = os.path.join(curPath, progress)
		gLogger.info("progress: %s" %progressFile)

		try:
			self.__dictBase = SDictBase(dictFile)
			self.__audioBase = AuidoArchive(audioFile)
			self.__usrProgress = UsrProgress()
			self.__usrProgress.Open(progressFile)

		except Exception as error:
			gLogger.error(error)
			self.__Exit_App()

	def __GoStudyMode(self):
		# global gLogger

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

			# lastDate = self.__mySDict.GetItem(word, "LastDate")
			lastDate = self.__usrProgress.GetLastDate(word)

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
		# global gLogger

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
		# global gLogger

		# gLogger.info("TestPos: %d" %(self.__CurTestPos))
		word = self.__CurTestLst[self.__CurTestPos]
		gLogger.info("TestWord: %s, familiar: %.1f" %(word, self.__WordsDict[word]))

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
				gLogger.info("curCount: %d" %(self.__CurCount))
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
				gLogger.info("ErrCount: %d", self.__ErrCount)
				gLogger.info("Right word: %s, Wrong word: %s." %(word, input_word))
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
					# gLogger.info("LearnLst = " + "".join(list(str(self.__LearnLst))))
					self.__WordsDict[word] -= 1
					self.__LearnLst.append(word)
					gLogger.info(word + " has been added in learn list.")
					return
			else: 
				self.__Score.set("OK!")
				self.__ErrCount = 3

			if self.__CurTestPos < len(self.__CurTestLst):
				self.__wordInput.delete(0, tk.END)
				self.__Test_Next()
			else: 
				self.__CurCount += 1
				gLogger.info("curCount: %d" %(self.__CurCount))
				self.__GoTestMode()

	def __Chop(self, event = None):
		# global gLogger

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

			# gLogger.info(word + " is forgoten.")
			
			if self.__CurLearnPos < len(self.__CurLearnLst):
				self.__Study_Next()
			else: 
				self.__CurCount = 1
				gLogger.info("curCount: %d" %(self.__CurCount))
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

			# gLogger.info(word + " is forgoten.")

			# if self.__WordsDict[word] != None: del self.__WordsDict[word]
			# while word in self.__WordsDict: del self.__WordsDict[word]

			if self.__CurTestPos < len(self.__CurTestLst):
				self.__Test_Next()
			else: 
				self.__CurCount += 1
				gLogger.info("curCount: %d" %(self.__CurCount))
				self.__GoTestMode()

		self.__WordsDict[word] = 10

		gLogger.info("%s has been chopped!" %(word))

	def __Forgoten(self, event = None):
		# global gLogger

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

			gLogger.info(word + " is forgotten!")

			if self.__CurTestPos < len(self.__CurTestLst):
				self.__Test_Next()
			else: 
				self.__CurCount += 1
				gLogger.info("curCount: %d" %(self.__CurCount))
				self.__GoTestMode()

		#self.__WordsDict.pop(word)

		# gLogger.info("length of WordsDict: %d" %(len(self.__WordsDict)))
		# # gLogger.info("WordsDict: \r\n", self.__WordsDict)

		# gLogger.info("length of TestWordsList: %d" %(len(self.__TestLst)))
		# # gLogger.info("TestWordsList: \r\n", self.__TestLst)

		# gLogger.info("length of LearnWordsList: %d" %(len(self.__LearnLst)))
		# # gLogger.info("LearnWordsList: \r\n", self.__LearnLst)

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
		# global gLogger

		# mp3 = os.path.join(sys.path[0], "audio", "Google", word[0], word + ".mp3")
		bAudioOK, audio = self.__audioBase.query_audio(word)
		if (bAudioOK == False):
			gLogger.error(audio)
			return False

		if (IsWindows() == True):
			import mp3play
			try:
				clip = mp3play.load(audio)
				clip.play()
				time.sleep(min(30, clip.seconds() + 0.3))
				clip.stop()
			except:
				gLogger.error("Wrong mp3: " + audio)
				return False
		elif (IsLinux() == True):
			os.system("mplayer " + audio)

		return True

	def __Play_MP3_2(self, word):

		word += ".mp3"

		if word in self.__audioFile.namelist():
			mp3 = self.__audioFile.read(word)
		else:
			gLogger.error("Can't find %s." %(word))
			return False

		#2.创建合成器对象，解析出最初的几帧音频数据
		import pymedia.muxer as muxer
		dm = muxer.Demuxer('mp3')
		frames = dm.parse(mp3)
		gLogger.info(len(frames))

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
		gLogger.info("sample_rate:%s, channels:%s" %(r.sample_rate,r.channels))
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

		# txtLst = []

		# if self.__mySDict.GetAll(word, txtLst):
		bDictOK, txtLst = self.__dictBase.query_word(word)
		if bDictOK:

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
				#gLogger.info(item.strip())
				i += 1
				self.__Content.insert(tk.END, item.strip())
				self.__Content.insert(tk.END, "\r\n")
				if i == 2:
					self.__Content.insert(tk.END, "\r\n")
					i = 0

	def Go(self):
		# global gCfg, gLogger

		self.__today = datetime.date.strftime(datetime.date.today(), "%Y-%m-%d")

		# print(gCfg)
		gLogger.info("Go!")

		allLimit = gCfg["General"]["Limit"]
		newWdsLimit = gCfg["StudyMode"]["Limit"]
		self.__TestCount = gCfg["TestMode"]["Times"]

		nUser = gCfg["User"]["nUser"]
		level = gCfg["User"]["Info"][nUser - 1]["Target"]

		# update count

		# where = "level = '" + level + "'"
		allCount = self.__usrProgress.GetAllCount(level)

		# where = "level = '" + level + "' and familiar > 0"
		needCount = allCount - self.__usrProgress.GetNeedCount(level)

		# where = "level = '" + level + "' and LastDate is null "
		newCount = self.__usrProgress.GetNewCount(level)

		# where = "level = '" + level + "' and familiar = 10"
		finishCount = self.__usrProgress.GetFnshedCount(level)

		gApp.update_count(allCount, needCount, newCount, finishCount)

		self.__LearnLst = []
		self.__TestLst = []
		self.__WordsDict = {}

		wdsLst = []

		# get forgotten words
		familiar = -10.0
		words_len = 0

		# get new words list (familiar < 0)
		newWdsLst = []

		while(words_len < newWdsLimit and familiar <= 0):
			# where = "level = '" + level + "' and familiar = " + str(familiar) + " limit " + str(limit - words_len)
			# if self.__mySDict.GetWordsLst(wdsLst, where):
			if self.__usrProgress.GetWordsLst(wdsLst, level, familiar, newWdsLimit - words_len):
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
			#gLogger.info(familiar)
			familiar = round(familiar, 1)

		# random.shuffle(self.__LearnLst)

		forgottenWdsLst = []

		# gLogger.info("length of new words: %d." %(len(newWdsLst)))
		for wd in newWdsLst: 
			lastDate = self.__usrProgress.GetLastDate(wd)
			# print(lastDate, wd)
			if lastDate != None: 
				forgottenWdsLst.append(wd)
				# newWdsLst.remove(wd)
		for wd in forgottenWdsLst: newWdsLst.remove(wd)

		self.__LearnLst.extend(forgottenWdsLst)
		gLogger.info("length of forgotten words: %d." %(len(forgottenWdsLst)))
		gLogger.info("length of new words: %d." %(len(newWdsLst)))

		#get old words
		timeDayLst = []
		timeArray = gCfg["TimeInterval"]
		for timeGroup in timeArray:
			if(timeGroup["Unit"] == "d"):
				timeDayLst.append(timeGroup["Interval"])

		timeDayLst = timeDayLst[::-1]		# reverse list
		# gLogger.info("timeDayLst: ", timeDayLst)
		gLogger.info("timeDayLst = " + "".join(list(str(timeDayLst))))

		oldWordsLimit = allLimit - len(self.__LearnLst)

		familiar = 0.0
		words_len = 0

		due2test_num = 0

		lastlastdate = datetime.date.strftime(datetime.date.today(), "%Y-%m-%d") 

		for day in timeDayLst:
			selDate = datetime.date.today() - datetime.timedelta(day)
			# gLogger.info("selDate:", selDate)
			lastdate = datetime.date.strftime(selDate, "%Y-%m-%d")

			if day == timeDayLst[0]:
				lastlastdate = lastdate
				# where = "level = '" + level + "' and lastdate <= date('" + lastdate + "') and familiar < 10"
			else:
				# where = "level = '" + level + "' and lastdate <= date('" + lastdate + "') and lastdate > date('" + lastlastdate + "') and familiar < 10"
				pass

			# num = self.__mySDict.GetCount(where)

			# gLogger.info(lastdate + " day: " + str(day) + " "+ str(num) + " Words due to test.")

			# due2test_num += num

			if (words_len < oldWordsLimit):
				# lastdate = datetime.date.strftime(selDate, "%Y-%m-%d")
				# gLogger.info("lastdate: " + lastdate)
				# where = "level = '" + level + "' and lastdate <= date('" + lastdate + "') and familiar < 10 order by familiar limit " + str(oldWordsLimit - words_len)
				# where = "level = '" + level + "' and lastdate <= date('" + lastdate + "') and lastdate > date('" + lastlastdate + "') and familiar < 10 order by familiar limit " + str(oldWordsLimit - words_len)
				'''
				where += " order by familiar limit " + str(oldWordsLimit - words_len)
				if self.__mySDict.GetWordsLst(wdsLst, where):
				'''
				limit = oldWordsLimit - words_len
				if self.__usrProgress.GetWordsLst(wdsLst, level, lastdate, lastlastdate, 10, limit):
					# i = 0
					for item in wdsLst:
						for wd in item:
							# self.__WordsDict[wd] = self.__mySDict.GetItem(wd, "familiar")
							self.__WordsDict[wd] = self.__usrProgress.GetFamiliar(wd)
							# gLogger.info("word: %s, familiar: %f" %(wd, self.__WordsDict[wd]))
							# print(wd, type(self.__WordsDict[wd]))
							self.__TestLst.append(wd)
							# i += 1
					wdsLst = []
					words_len = len(self.__TestLst)
					# gLogger.info("lastdate: " + lastdate + ", len: " + str(i))
			# else: break
			lastlastdate = lastdate

		# gLogger.info("Words due to test: %d", due2test_num)

		# gLogger.info("TestLst = " + "".join(list(str(self.__TestLst))))
		self.__TestLst.extend(self.__LearnLst)

		words_len = allLimit - len(self.__TestLst)
		gLogger.info("left %d words for new" %words_len)

		if words_len > 0: 
			self.__TestLst.extend(newWdsLst[:words_len - 1])
			self.__LearnLst.extend(newWdsLst[:words_len - 1])

		for wd in newWdsLst[words_len:]:
			if wd in self.__WordsDict: del self.__WordsDict[wd]

		random.shuffle(self.__LearnLst)

		gLogger.info("len of all TestWordsList: %d." %(len(self.__TestLst)))
		self.__TestLst = list(set(self.__TestLst))	# remove duplicate item 
		gLogger.info("len of no repeat all TestWordsList: %d." %(len(self.__TestLst)))
		# gLogger.info("WordsDict = " + str(self.__WordsDict))
		# gLogger.info("len of WordsDict: %d: " %(len(self.__WordsDict)))
		# gLogger.info(self.__LearnLst)
		# gLogger.info("LearnLst = " + "".join(list(str(self.__LearnLst))))
		gLogger.info("len of LearnList: %d." %(len(self.__LearnLst)))
		#self.__wordInput['state'] = 'readonly'

		self.__numOfLearn.set("%d words to Learn!" %(len(self.__LearnLst)))
		self.__numOfTest.set("%d words to Test!" %(len(self.__TestLst)))
		self.__GoStudyMode()

	def __Save_Progress(self):
		# global gLogger

		#gLogger.info("WordsDict: ", self.__WordsDict)
		gLogger.info("len of self.__WordsDict: %d" %len(self.__WordsDict))
		gLogger.info("WordsDict = " + str(self.__WordsDict))

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

		gLogger.info("len of self.__WordsDict: %d" %len(self.__WordsDict))
		gLogger.info("WordsDict = " + str(self.__WordsDict))

		for word, familiar in self.__WordsDict.items():

			familiar += 1.0

			if familiar > 10: familiar = 10.0
			if familiar < -10: familiar = -10.0

			familiar = round(familiar, 1)

			self.__usrProgress.UpdateProgress(word, familiar, self.__today)

		# gLogger.info("TestWordsList: ")
		# gLogger.info(self.__TestLst)
		# gLogger.info("LearnWordsList: ")
		# gLogger.info(self.__LearnLst)

	def onCloseWindow(self):
		result = msgBox.askyesno(self.__Mode.get(), "Are you going to quit?")
		if result == True: 
			self.__Save_Progress()
			self.__Exit_App()
		else: return

	def __Exit_App(self, event = None):
		# self.__dictBase.Close() 
		# self.__audioBase.Close()
		# self.__usrProgress.Close()
		os._exit(0)


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

	def __hide(self):
		""""""
		self.root.withdraw()

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
 
	def __show(self):
		""""""
		self.root.update()
		self.root.deiconify()

	def __exit_app(self, event = None):
		self.__onCloseWindow()
		# os._exit(0)


if __name__ == "__main__":
	main()
