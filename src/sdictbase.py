#!/usr/bin/python3
#-*- encoding:utf-8 -*-
# -*- coding: utf-8 -*-
#coding=utf-8
'''
'''
from src.dictbase import DictBase
from src.sqlite import SQLite
from src.globalvar import GetLogger


class SDictBase(DictBase):
	""" 
		# Words: word, symbol, meaning, sentences, level, familiar, lastdate
		# Words: word, symbol, meaning, sentences
	"""
	def __init__(self, dictSrc):
		global gLogger

		gLogger = GetLogger()

		self.__dictBase = SQLite()
		self.__dictBase.Open(dictSrc)

	def __del__(self):
		self.__dictBase.Close()

	def get_parseFun(self):
		return "dictHtml"

	# [symbol, meaning, sentences]
	def query_word(self, word):
		datum = []
		bDictOK = self.__dictBase.GetAll(word, datum)
		if bDictOK:
			return bDictOK, datum
		else:
			return bDictOK, datum[0]

	def get_wordsLst(self, wdsLst, word):
		# self.__dictBase.GetSimilarWordLst(word, wdsLst)
		where = "word like '" + word + "%'"
		self.__dictBase.GetWordsLst(wdsLst, where)
		if len(wdsLst) >= 1: return True
		else: return False

	def del_word(self, word):
		raise NotImplementedError("don't support to delete " + word)
		return False