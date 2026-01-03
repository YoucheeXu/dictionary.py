#!/usr/bin/python3
#-*- encoding:utf-8 -*-
# -*- coding: utf-8 -*-
#coding=utf-8

from DictBase import *

#################################################
class MDictBase(DictBase):

	def __init__(self, dictArchive, audioArchive = None):
		self.__dictArchive = dictArchive

	def query_word(self, word):
		pass

	def get_wordsLst(self, wdsLst, word):
		pass

	def del_word(self, word):
		pass

	def del_audio(self, word):
		pass