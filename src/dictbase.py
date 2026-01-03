#!/usr/bin/python3
#-*- encoding:utf-8 -*-
# -*- coding: utf-8 -*-
#coding=utf-8

import abc

#################################################
class DictBase(metaclass = abc.ABCMeta):

	def __init__(self, dictPath, audioPath):
		self.__GDictPath = dictPath
		self.__GAudioPath = audioPath

	@abc.abstractmethod
	def query_word(self, word):
		pass

	@abc.abstractmethod
	def get_wordsLst(self, wdsLst, word):
		pass

	@abc.abstractmethod
	def del_word(self, word):
		pass

	@abc.abstractmethod
	def del_audio(self, word):
		pass