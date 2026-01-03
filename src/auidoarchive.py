#!/usr/bin/python3
#-*- encoding:utf-8 -*-
# -*- coding: utf-8 -*-
#coding=utf-8
import os
import shutil
import time
from zipfile import ZIP_DEFLATED

from src.ziparchive import ZipArchive
from src.globalvar import GetLogger, GetApp


class AuidoArchive():
	def __init__(self, audioSrc, compression = ZIP_DEFLATED, compresslevel = 2):
		global gLogger

		gLogger = GetLogger()

		self.__bWritable = True

		# self.__tempAudioDir = os.path.join(tempfile.gettempdir(), 'audio')
		filepath, tempfilename = os.path.split(audioSrc)
		filename, extension = os.path.splitext(tempfilename)
		self.__tempAudioDir = os.path.join(filepath, filename)
		if not os.path.exists(self.__tempAudioDir):
			os.makedirs(self.__tempAudioDir)
		gLogger.info("tempAudioDir: " + self.__tempAudioDir)

		self.__audioZip = ZipArchive(audioSrc, compression, compresslevel)

	def close(self):
		if os.path.exists(self.__tempAudioDir):
			shutil.rmtree(self.__tempAudioDir)
		time.sleep(1)
		if os.path.isdir(self.__tempAudioDir) == False:
			print("OK to remove %s" %self.__tempAudioDir)

	def query_audio(self, word):

		# fileName = word + ".mp3"
		fileName = word[0] + "/" + word + ".mp3"

		audioFile = os.path.join(self.__tempAudioDir, word + ".mp3")

		try:		
			if(self.__audioZip.bFileIn(fileName)):
				if os.path.exists(audioFile) == True:
					return True, audioFile
				else:
					audio = self.__audioZip.readFile(fileName)
					if audio:
						with open(audioFile, 'wb') as f:
							f.write(audio)
						return True, audioFile
					else:
						return False, "Fail to read audio of " + word + " in file!"
			elif self.__bWritable:
				audioURL = "https://ssl.gstatic.com/dictionary/static/sounds/oxford/" + word + "--_us_1.mp3"

				err = GetApp().download_file(audioURL, audioFile);
				if err:
					return False, str(err)

				if os.path.exists(audioFile):
					with open(audioFile, 'rb') as f:
						audio = f.read()
						self.__audioZip.addFile(fileName, audio)
					return True, audioFile
			else:
				return False, "no audio: " + word + " in file!"

		except Exception as err:
			return False, str(err)

		return False, "Unknown Error!"

	def getWritable(self):
		return self.__bWritable

	def del_audio(self, word):
		fileName = word[0] + "/" + word + ".mp3"
		return self.__dictZip.delFile(fileName)
