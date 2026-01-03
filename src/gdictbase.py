#!/usr/bin/python3
#-*- encoding:utf-8 -*-
# -*- coding: utf-8 -*-
#coding=utf-8

import os
# import globalVar
from globalVar import *
from ZipArchive import *
import tempfile
import json
from DictBase import *

'''
v2.1
a/able.json

v2.0 support zip dict
'''

#################################################
class GDictBase(DictBase):

	def __init__(self, dictZip, audioPath):

		self.__dictZip = ZipArchive(dictZip)
		# self.__audioZip = ZipArchive(audioZip)
		self.__tempDir = tempfile.gettempdir()
		print(self.__tempDir)
		self.__audioPath = audioPath

	def query_word(self, word):
		# dict = None
		datum = None
		audio = None

		fileName = word[0] + "/" + word + ".json"
		
		if(self.__dictZip.bFileIn(fileName)):
			dict = self.__dictZip.readFile(fileName)
		else:
			wordFile = os.path.join(self.__tempDir, word + ".json")
			jsonURL = "http://dictionary.so8848.com/ajax_search?q=" + word
			GetApp().download_file(jsonURL, wordFile);

			dict = None
			if os.path.exists(wordFile):
				with open(wordFile, 'rb') as f:
					dict = f.read()
					if(self.__VerifyJson(wordFile, word, dict)):
						# self.__dictZip.addFile(wordFile)
						# addFile(self, fileName, datum)
						print("%s's json is OK!" %word)
						self.__dictZip.addFile(fileName, dict)
					else:
						dict = None

				os.remove(wordFile)

		# print("%s = %s" %(word, dict))

		if(dict):
			# print(dict)
			datum = json.loads(dict, strict = False)

			if(datum["ok"]):
				info = datum["info"]
				# print(info)

				# regex = re.compile(r'\\(?![/u"])')
				# info_fixed = regex.sub(r"\\\\", info)
				# dict = json.loads(info_fixed, strict = False)
				# dict = info_fixed
				dict = info
				# print("%s = %s" %(word, dict))

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

		audioFile = os.path.join(self.__audioPath, word[0], word + ".mp3")

		if(not os.path.exists(audioFile)):
			audioURL = "https://ssl.gstatic.com/dictionary/static/sounds/oxford/" + word + "--_us_1.mp3"

			GetApp().download_file(audioURL, audioFile);
			if (not os.path.exists(audioFile)):
				audioFile = None

		return dict, audioFile

	def __VerifyJson(self, jsonFile, word, dict):
		try:
			# with open(jsonFile, 'rb') as f:
				# dict = f.read()
				# print(dict)

			datum = json.loads(dict, strict = False)

			if(datum["ok"]):
				info = datum["info"]

				regex = re.compile(r'\\(?![/u"])')
				info_fixed = regex.sub(r"\\\\", info)
				datum = json.loads(info_fixed, strict = False)
				# datum = json.loads(info, strict = False)
				if(datum["query"] == word):
					return True

		except Exception as err:
			print(err)

		return False

	def get_wordsLst(self, wdMatchLst, word):

		fileName = word[0] + "/" + word + ".*\.json"
		# print("Going to find: " + fileName)
		self.__dictZip.searchFile(fileName, wdMatchLst)

		for i in range(len(wdMatchLst)):
			wdMatchLst[i] = wdMatchLst[i][2: -5]

		if len(wdMatchLst) >= 1: return True
		else: return False

	def del_word(self, word):
		raise NotImplementedError("don't suppor to del dict of  " + word)
		return False

	def del_audio(self, word):
		'''
		raise NotImplementedError("don't suppor to del audio of  " + word)
		return False
		'''

		audioFile = self.__audioPath + word + ".mp3"
		if os.path.isfile(audioFile): os.remove(audioFile)
		return not os.path.exists(audioFile)