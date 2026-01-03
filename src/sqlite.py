#!/usr/bin/python3
#-*- encoding:utf-8 -*-
# -*- coding: utf-8 -*-
#coding=utf-8
import sqlite3
import os

from src.globalvar import get_logger


class SQLite():

	def Open(self, file):
		global gLogger

		gLogger = get_logger()

		if os.path.isfile(file) == False:
			raise Exception("%s doesn't exit!" %(file))
			# gLogger.info("%s doesn't exit!" %(file))
			return False

		self.__conn = sqlite3.connect(file)
		self.__cur = self.__conn.cursor()
		gLogger.info(file + "is OK to open!")
		return True

	def GetAll(self, word, txtLst):
		# global gLogger

		try:
			command = "select * from Words where word = '" + word + "'"
			self.__cur.execute(command)
			content = self.__cur.fetchone()
		except:
			gLogger.error(command)

		if content:
			# symbol = content[1]
			# meaning = content[2]
			# sentences = content[3]
			# level = content[4]
			# familiar = content[5]
			# lastdate = content[6]
			txtLst = txtLst.extend(content)
			return True
		else:
			error = "can't find %s" %(word)
			gLogger.info(error)
			txtLst = txtLst.append(error)
			return False

	def GetItem(self, word, item):
		try:
			command = "select " + item + " from Words where word = '" + word + "'"
			self.__cur.execute(command)
			content = self.__cur.fetchone()
			# if content:
				# return content[0]
			# else :
				# gLogger.info("can't find %s" %(word))
				# return False
		except:
			gLogger.error(command)
		return content[0]
	
	def GetCount(self, where):
		command = "select count(*) from Words where " + where
		# gLogger.info(command)
		self.__cur.execute(command)
		number = self.__cur.fetchone()[0]
		# gLogger.info(number)
		return number

	def UpdateItem(self, word, item, v):
		command = "update Words set " + item + " = " + v + " where word = '" + word + "'"
		# gLogger.info(command)
		#os._exit(0)
		self.__cur.execute(command)
		self.__conn.commit()

	def Update(self, word, contDict):
		#gLogger.info(contDict)
		command = "update Words set "
		for keyword, value in contDict.items():
			#gLogger.info ("%s => %r" % (keyword, value))
			command = command + keyword + " = " + value + ", "
		command = command + "where word = '" + word + "'"
		command = command.replace(", where", " where")
		# gLogger.info(command)
		#os._exit(0)
		self.__cur.execute(command)
		self.__conn.commit()

	# def update_word(self, word, *content):
		# command = "update Words set "
		# for keyword, value in content.items():
			# #gLogger.info ("%s => %r" % (keyword, value))
			# command = command + keyword + " = " + value + ", "
		# command = command + "where word = '" + word + "'"
		# command = command.replace(", where", " where")
		# gLogger.info(command)
		# os._exit(0)
		# self.__cur.execute(command)
		# self.__conn.commit()
		
	# def get_wordslst(self, wdsLst, level, familiar, limit):
		# command = "select word from Words where level = '" + level + "' and familiar = " + str(familiar) + " order by familiar limit " + str(limit)
		# gLogger.info (command)
		# self.__cur.execute(command)
		# content = self.__cur.fetchall();
		# if content:
			# wdsLst = wdsLst.extend(content)
			# return True
		# else :
			# gLogger.info("can't get wordslst.")
			# return False

	def GetWordsLst(self, wdsLst, where):
		command = "select word from Words where " + where
		gLogger.info(command)
		self.__cur.execute(command)
		content = self.__cur.fetchall()
		if content:
			wdsLst = wdsLst.extend(content)
			gLogger.info("Got wordslst: %d." %len(content))
			return True
		else:
			gLogger.info("can't get wordslst.")
			return False

	def Close(self):
		self.__cur.close()
		self.__conn.close()
