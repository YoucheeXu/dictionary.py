#!/usr/bin/python3
#-*- encoding:utf-8 -*-
# -*- coding: utf-8 -*-
#coding=utf-8

'''
ZipArchive.py
将文件归档到zip文件，并从zip文件中读取数据
'''

import os
from zipfile import *
import re

'''
压缩模式有ZIP_STORED和ZIP_DEFLATED，ZIP_STORED只是存储模式，不会对文件进行压缩，这个是默认值，如果你需要对文件进行压缩，必须使用ZIP_DEFLATED模式
'''

class ZipArchive:

	def __init__(self, zip):
		self.__zip = zip
		try:
			self.__archiveFile = ZipFile(self.__zip, 'a', compression = ZIP_DEFLATED, compresslevel = 2);
		except (BadZipFile, LargeZipFile) as reason:
			print(rason)
		except Exception as error:
			print(error)
			print("Fail to open: %s." %self.__zip)

		self.__fileList = self.__archiveFile.namelist()
		# print(self.__fileList)

	def __del__(self):
		print("kill myself.")
		self.__archiveFile.close()

	def addFile(self, fileName, datum):
		try:
			# self.__archiveFile.write(filePath)
			self.__archiveFile.writestr(fileName, datum)
		except (BadZipFile, LargeZipFile) as reason:
			print(rason)
			return False
		except Exception as error:
			print(error)
			print("Fail to add: %s into: %s" %(fileName, self.__zip))
			return False

		# fileName = os.path.basename(filePath)
		self.__fileList.append(fileName)
		return True

	def delFile(self, fileName):
		pass

	def readFile(self, fileName):
		if(not self.bFileIn(fileName)):
			return None
		try:
			file = self.__archiveFile.read(fileName)
		except (BadZipFile, LargeZipFile) as reason:
			print(rason)
			return None
		except Exception as error:
			print(error)
			print("Fail to add: %s into: %s" %(fileName, self.__zip))
			return None
		return file

	def bFileIn(self, fileName):
		if fileName in self.__fileList:
			return True
		else:
			return False

	def searchFile(self, pattern, wdMatchLst):
		regex = re.compile(pattern)
		for word in self.__fileList:
			# print(word)
			match = regex.search(word)
			if match:
				wdMatchLst.append(word)
		return len(wdMatchLst)