#!/usr/bin/python3
#-*- encoding:utf-8 -*-
# -*- coding: utf-8 -*-
#coding=utf-8

import os
import tempfile

from src.globalvar import GetLogger, GetApp

#################################################
class AuidoArchive():

	def __init__(self, audioPath):
		global gLogger

		gLogger = GetLogger()

		self.__tempDir = tempfile.gettempdir()
		gLogger.info("tempDir: " + self.__tempDir)
		self.__audioPath = audioPath

	def query_audio(self, word):

		'''
		fileName = word + ".mp3"
		if(self.__audioZip.bFileIn(fileName)):
			audio = self.__audioZip.readFile(fileName)
		else:
			audioFile = os.path.join(self.__tempDir, word + ".mp3")
			audioURL = "https://ssl.gstatic.com/dictionary/static/sounds/oxford/" + word + "--_us_1.mp3"

			GetApp().download_file(audioURL, audioFile);
			if os.path.exists(audioFile):
				with open(audioFile, 'rb') as f:
					audio = f.read()
					self.__audioZip.addFile(fileName, audio)

				os.remove(audioFile)

		return dict, audio
		'''

		audioDir = os.path.join(self.__audioPath, word[0])

		audio = os.path.join(audioDir, word + ".mp3")
		# print(audio)

		try:
			if(not os.path.exists(audio)):
				audioURL = "https://ssl.gstatic.com/dictionary/static/sounds/oxford/" + word + "--_us_1.mp3"
				audioURL = audioURL.replace(" ", "%20")
				if (not os.path.exists(audioDir)):
					os.mkdir(audioDir)
				GetApp().download_file(audioURL, audio);
				if (not os.path.exists(audio)):
					audio = "Fail to download: " + word
					return False, audio

		except Exception as err:
			# print(CURR_FILENAME + ": Fail to query audio of " + word)
			audio = str(err)
			# print(str(err))
			return False, audio

		return True, audio

	def del_audio(self, word):

		audioFile = self.__audioPath + word + ".mp3"
		if os.path.isfile(audioFile): os.remove(audioFile)
		return not os.path.exists(audioFile)