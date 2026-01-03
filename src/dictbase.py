#!/usr/bin/python3
#-*- encoding:utf-8 -*-
# -*- coding: utf-8 -*-
#coding=utf-8
import abc

from src.globalvar import GetLogger


class DictBase(metaclass = abc.ABCMeta):

	# def __init__(self, dictSrc):
		# self.__dictSrc = dictSrc

	@abc.abstractmethod
	def get_parseFun(self):
		pass

	@abc.abstractmethod
	def query_word(self, word):
		pass

	@abc.abstractmethod
	def get_wordsLst(self, wdsLst, word):
		pass

	@abc.abstractmethod
	def getWritable(self):
		pass

	@abc.abstractmethod
	def del_word(self, word):
		pass

	@abc.abstractmethod
	def close(self):
		pass
