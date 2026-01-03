#!/usr/bin/python3
# -*- coding: utf-8 -*-

class Stack():
	""" 后进先出
	"""
	def __init__(self):
		self.__DatumLst = []
	def Push(self, x):
		self.__DatumLst.append(x)
	def Pop(self):
		if self.IsEmpty():
			raise IndexError("stack is empty")
		else:
			return self.__DatumLst.pop()
	def GetSize(self):
		return len(self.__DatumLst)
	def IsEmpty(self):
		return len(self.__DatumLst) == 0


class Queue():
	""" 先进先出
	"""
	def __init__(self):
		self.__DatumLst = []
	def Enqueue(self, x):	# 入队操作
		self.__DatumLst.append(x)
	def Dequeue(self):	# 出队操作
		if self.IsEmpty():
			raise IndexError("queue is empty")
		else:
			return self.__DatumLst.pop(0)
	def GetSize(self):
		return len(self.__DatumLst)
	def IsEmpty(self):
		return len(self.__DatumLst) == 0
