#!/usr/bin/python3
#-*- encoding:utf-8 -*-
# -*- coding: utf-8 -*-
#coding=utf-8
'''
v1.0.1 given compression format
'''
import re
from zipfile import *

from src.globalvar import GetLogger


class ZipArchive:
	""" 将文件归档到zip文件，并从zip文件中读取数据
		压缩模式有ZIP_STORED和ZIP_DEFLATED，ZIP_STORED只是存储模式，不会对文件进行压缩，这个是默认值，如果你需要对文件进行压缩，必须使用ZIP_DEFLATED模式
	"""

	# To-Do
	def __init__(self, zip, compression, compresslevel):
		global gLogger

		gLogger = GetLogger()

		self.__zip = zip
		try:
			self.__archiveFile = ZipFile(self.__zip, 'a', compression, compresslevel)
		except (BadZipFile, LargeZipFile) as reason:
			gLogger.error(rason)
		except Exception as error:
			gLogger.error(error)
			# gLogger.error("Fail to open: %s." %self.__zip)

		self.__fileList = self.__archiveFile.namelist()
		# gLogger.info(self.__fileList)

	def __del__(self):
		print("kill myself.")
		self.__archiveFile.close()

	def addFile(self, fileName, datum):
		# global gLogger

		try:
			# self.__archiveFile.write(filePath)
			self.__archiveFile.writestr(fileName, datum)
		except (BadZipFile, LargeZipFile) as reason:
			gLogger.error(rason)
			return False
		except Exception as error:
			gLogger.error(error)
			# gLogger.error("Fail to add: %s into: %s" %(fileName, self.__zip))
			return False

		# fileName = os.path.basename(filePath)
		self.__fileList.append(fileName)
		return True

	def delFile(self, fileName):
		raise NotImplementedError("don't support to delete file: " + fileName)
		return False

	def readFile(self, fileName):
		# global gLogger

		if(not self.bFileIn(fileName)):
			return None
		try:
			file = self.__archiveFile.read(fileName)
		except (BadZipFile, LargeZipFile) as reason:
			gLogger.error(rason)
			return None
		except Exception as error:
			gLogger.error(error)
			# gLogger.error("Fail to add: %s into: %s" %(fileName, self.__zip))
			return None
		return file

	def bFileIn(self, fileName):
		# gLogger.info(self.__fileList)
		if fileName in self.__fileList:
			return True
		else:
			return False

	def searchFile(self, pattern, wdMatchLst):
		regex = re.compile(pattern)
		for word in self.__fileList:
			# gLogger.info(word)
			match = regex.search(word)
			if match:
				wdMatchLst.append(word)
		return len(wdMatchLst)