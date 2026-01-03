#!/usr/bin/python3
#-*- encoding:utf-8 -*-
# -*- coding: utf-8 -*-
#coding=utf-8
'''
v1.1	every time open zip and close	
v1.0.1	given compression format
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
		self.__compression = compression
		self.__compresslevel = compresslevel
		'''
		self.__options = {
			'mode': 'a',
			'compression': ZIP_DEFLATED,
			'compresslevel': 2
		}
		'''
		# self.__options = ('a', ZIP_DEFLATED, True, 2)

		self.__fileList = []
	
		try:
			# self.__archiveFile = ZipFile(self.__zip, 'a', compression = ZIP_DEFLATED, compresslevel = 2);
			# with ZipFile(self.__zip, self.__options) as zipf:
			with ZipFile(self.__zip, 'a', ZIP_DEFLATED, compresslevel = 2) as zipf:
				self.__fileList = zipf.namelist()
		except (BadZipFile, LargeZipFile) as reason:
			gLogger.error(rason)
		except Exception as error:
			gLogger.error(error)
			# gLogger.error("Fail to open: %s." %self.__zip)

		# gLogger.info(self.__fileList)

	def addFile(self, fileName, datum):
		# global gLogger

		try:
			# self.__archiveFile.write(filePath)
			# self.__archiveFile.writestr(fileName, datum)
			# with ZipFile(self.__zip, self.__options) as zipf:
			with ZipFile(self.__zip, 'a', ZIP_DEFLATED, compresslevel = 2) as zipf:	
				zipf.writestr(fileName, datum)
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

	def readFile(self, fileName):

		if(not self.bFileIn(fileName)):
			return None
		file = None
		try:
			# file = self.__archiveFile.read(fileName)
			# with ZipFile(self.__zip, self.__options) as zipf:
			with ZipFile(self.__zip, 'a', ZIP_DEFLATED, compresslevel = 2) as zipf:
				file = zipf.read(fileName)
		except (BadZipFile, LargeZipFile) as reason:
			gLogger.error(reason)
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

	def delFile(self, fileName):
		raise NotImplementedError("don't support to delete file: " + fileName)
		return False
