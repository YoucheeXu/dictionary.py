#!/usr/bin/python3
#-*- encoding:utf-8 -*-
# -*- coding: utf-8 -*-
#coding=utf-8
'''
To-Do:
* support create new dict and initialize it
'''
from src.sqlite import SQLite
from src.globalvar import GetLogger


class UsrProgress():
	"""
		# Words: word, symbol, meaning, sentences, level, familiar, lastdate
		# Words: word, level, familiar, lastdate
	"""
	def Open(self, dictSrc):
		global gLogger

		gLogger = GetLogger()

		self.__dictBase = SQLite()
		self.__dictBase.Open(dictSrc)
		# print("progress of " + dictSrc + "is OK to open!")

	def __del__(self):
		self.__dictBase.Close()

	def GetLastDate(self, word):
		return self.__dictBase.GetItem(word, "LastDate")

	def GetFamiliar(self, word):
		return self.__dictBase.GetItem(word, "familiar")

	def GetAllCount(self, level):
		where = "level = '" + level + "'"
		return self.__dictBase.GetCount(where)

	def GetNeedCount(self, level):
		where = "level = '" + level + "' and familiar > 0"
		return self.__dictBase.GetCount(where)

	def GetNewCount(self, level):
		where = "level = '" + level + "' and LastDate is null "
		return self.__dictBase.GetCount(where)

	def GetFnshedCount(self, level):
		where = "level = '" + level + "' and familiar = 10"
		return self.__dictBase.GetCount(where)

	def GetWordsLst(self, *args):
		wdsLst = args[0]
		level = args[1]
		familiar = args[-2]
		limit = args[-1]
		if len(args) == 4:
			# (wdsLst, level, familiar, limit)
			where = "level = '" + level + "' and familiar = " + str(familiar) + " limit " + str(limit)
			self.__dictBase.GetWordsLst(wdsLst, where)
		elif len(args) == 6:
			# (wdsLst, level, lastdate, lastlastdate, familiar, limit)
			lastdate = args[2]
			lastlastdate = args[3]
			where = "level = '" + level + "' and lastdate <= date('" + lastdate + "') and lastdate >= date('" + lastlastdate + "') and familiar < " + str(familiar)
			where += " order by familiar limit " + str(limit)

			self.__dictBase.GetWordsLst(wdsLst, where)

		if len(wdsLst) >= 1: 
			return True
		else:
			return False	

	def UpdateProgress(self, word, familiar, today):
		itmLst = ['familiar', 'lastdate']
		# valLst = []
		# valLst.append(str(familiar))
		# valLst.append("date('" + self.__today + "')")
		valLst = [str(familiar), "date('" + today + "')"]
		valueDict = dict(zip(itmLst, valLst))

		self.__dictBase.Update(word, valueDict)

	def DelWord(self, word):
		raise NotImplementedError("don't support to delete " + word)
		return False

	def Close(self):
		pass
