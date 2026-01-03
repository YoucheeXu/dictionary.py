#!/usr/bin/python3
#-*- encoding:utf-8 -*-
# -*- coding: utf-8 -*-
#coding=utf-8
import os
import shutil
import time
from zipfile import ZIP_DEFLATED

from src.ziparchive import ZipArchive
from src.globalvar import get_logger, get_app


class AuidoArchive():
	def __init__(self, audioSrc, compression = ZIP_DEFLATED, compresslevel = 2):
		global gLogger

		gLogger = get_logger()

		self.__bWritable = True

		# self.__tempAudioDir = os.path.join(tempfile.gettempdir(), 'audio')
		filepath, self.__audioArchive = os.path.split(audioSrc)
		fileName, extension = os.path.splitext(self.__audioArchive)
		self.__tempAudioDir = os.path.join(filepath, fileName)
		if os.path.exists(self.__tempAudioDir) == False:
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
						return False, "{0} {1}{2}".format("Fail to read audio in", self.__audioArchive, "!")
			elif self.__bWritable:
				audioURL = "https://ssl.gstatic.com/dictionary/static/sounds/oxford/" + word + "--_us_1.mp3"

				err = get_app().download_file(audioURL, audioFile);
				if err:
					return False, str(err)

				if os.path.exists(audioFile):
					with open(audioFile, 'rb') as f:
						audio = f.read()
						self.__audioZip.addFile(fileName, audio)
					return True, audioFile
			else:
				return False, "{0} {1}{2}".format("no audio in", self.__audioArchive, "!")

		except Exception as err:
			return False, str(err)

		return False, "Unknown Error!"

	def getWritable(self):
		return self.__bWritable

	def del_audio(self, word):
		fileName = word[0] + "/" + word + ".mp3"
		return self.__dictZip.delFile(fileName)
