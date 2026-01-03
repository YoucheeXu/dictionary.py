#!/usr/bin/python3
#-*- encoding:utf-8 -*-
# -*- coding: utf-8 -*-
#coding=utf-8
'''
v2.2 delete audio part

v2.1
a/able.json in zip

v2.0 support zip dict
'''
import os
import tempfile
import json

from src.dictbase import DictBase
from src.ziparchive import ZipArchive
from src.globalvar import GetLogger, GetApp


class GDictBase(DictBase):

	def __init__(self, dictSrc, compression, compresslevel):
		global gLogger

		gLogger = GetLogger()

		self.__bWritable = True
		self.__dictZip = ZipArchive(dictSrc, compression, compresslevel)
		self.__tempDir = tempfile.gettempdir()
		gLogger.info("tempDir: " + self.__tempDir)

	def close(self):
		pass

	def get_parseFun(self):
		return "dictJson"

	def query_word(self, word):

		# fileName = os.path.join(word[0], word + ".json")
		fileName = word[0] + "/" + word + ".json"

		wordFile = None
		try:
			if self.__dictZip.bFileIn(fileName):
				dict = self.__dictZip.readFile(fileName)
			elif self.__bWritable:
				wordFile = os.path.join(self.__tempDir, word + ".json")
				jsonURL = "http://dictionary.so8848.com/ajax_search?q=" + word
				jsonURL = jsonURL.replace(" ", "%20")
				err = GetApp().download_file(jsonURL, wordFile)
				if err:
					return False, str(err)

				if os.path.exists(wordFile):
					with open(wordFile, 'rb') as f:
						dict = f.read()
						inWord = self.__GetInWord(dict)
					os.remove(wordFile)

					if(inWord):
						# self.__dictZip.addFile(wordFile)
						# addFile(self, fileName, datum)
						if inWord == word:
							# print("%s's json is OK!" %word)
							# GetApp().log("info", "%s's json is OK!" %word)
							self.__dictZip.addFile(fileName, dict)
						else:
							datum = "Wrong word: " + inWord + ";"
							# GetApp().log("error", "%s isn't what we want!" %word)
							return False, datum
					else:
						datum = "No word in dictionary."
						return False, datum

				else:
					datum = "Fail to download: " + word
					return False, datum
			else:
				datum = "no word: " + word + " in dict."
				return False, datum

			# print("%s = %s" %(word, dict))

			if(dict):
				dictDatum = json.loads(dict, strict = False)

				if(dictDatum["ok"]):
					info = dictDatum["info"]

					# regex = re.compile(r'\\(?![/u"])')
					# info_fixed = regex.sub(r"\\\\", info)
					# dict = info_fixed
					datum = info
					# print("%s = %s" %(word, dict))
					return True, datum
			else:
				datum = "Fail to read: " + word
				return False, datum

		except Exception as err:
			# print("fail to query dict of " + word)
			GetApp().log("error", "fail to query dict of " + word)
			datum = str(err).replace("<", "")
			datum = datum.replace(">", "")
			if os.path.exists(wordFile):
				os.remove(wordFile)
			return False, datum

		datum = "Unknown error!"
		return False, datum

	def __GetInWord(self, dict):

		datum = json.loads(dict, strict = False)

		if(datum["ok"]):
			info = datum["info"]
			# print(info)
			# GetApp().log("info", info)
			# regex = re.compile(r'\\(?![/u"])')
			# info_fixed = regex.sub(r"\\\\", info)
			# GetApp().log("info", info_fixed)
			# datum = json.loads(info_fixed, strict = False)
			# info = info.replace('\\"', '"')
			# info = info.replace('/', '')
			info = info.replace('\\', '\\\\')
			# GetApp().log("info", info)
			datum = json.loads(info, strict = True)
			return datum["primaries"][0]["terms"][0]["text"]

		return None

	def get_wordsLst(self, wdMatchLst, word):

		fileName = word[0] + "/" + word + ".*\.json"
		# print("Going to find: " + fileName)
		self.__dictZip.searchFile(fileName, wdMatchLst)

		for i in range(len(wdMatchLst)):
			wdMatchLst[i] = wdMatchLst[i][2: -5]

		if len(wdMatchLst) >= 1: return True
		else: return False

	def getWritable(self):
		return self.__bWritable

	def del_word(self, word):
		fileName = word[0] + "/" + word + ".json"
		return self.__dictZip.delFile(fileName)
