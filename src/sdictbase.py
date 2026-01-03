#-*- encoding:utf-8 -*-
# -*- coding: utf-8 -*-
#coding=utf-8

import sqlite3
import os
import sys
import locale

#Words: word, symbol, meaning, sentences, level, familiar, lastdate

########################################################################
class SDictBase():

	def open(self, file):
		if os.path.isfile(file) == False:
			print("%s doesn't exit!" %(file))
			return False

		self.__conn = sqlite3.connect(file)
		self.__cur = self.__conn.cursor()
		return True;

	def get_all(self, word, txtLst):
		try:
			command = "select * from Words where word = '" + word + "'"
			self.__cur.execute(command)
			content = self.__cur.fetchone();
		except:
			print(command)
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
			print ("can't find %s" %(word))
			return False

	def get_item(self, word, item):
		try:
			command = "select " + item + " from Words where word = '" + word + "'"
			self.__cur.execute(command)
			content = self.__cur.fetchone();
			# if content:
				# return content[0]
			# else :
				# print("can't find %s" %(word))
				# return False
		except:
			print(command)
		return content[0]
	
	def get_count(self, where):
		command = "select count(*) from Words where " + where
		# print(command)
		self.__cur.execute(command)
		number = self.__cur.fetchone()[0];
		# print(number)
		return number

	def update_item(self, word, item, v):
		command = "update Words set " + item + " = " + v + " where word = '" + word + "'"
		# print(command)
		#os._exit(0)
		self.__cur.execute(command)
		self.__conn.commit()

	def update(self, word, contDict):
		#print(contDict)
		command = "update Words set "
		for keyword, value in contDict.items():
			#print ("%s => %r" % (keyword, value))
			command = command + keyword + " = " + value + ", "
		command = command + "where word = '" + word + "'"
		command = command.replace(", where", " where")
		# print(command)
		#os._exit(0)
		self.__cur.execute(command)
		self.__conn.commit()

	# def update_word(self, word, *content):
		# command = "update Words set "
		# for keyword, value in content.items():
			# #print ("%s => %r" % (keyword, value))
			# command = command + keyword + " = " + value + ", "
		# command = command + "where word = '" + word + "'"
		# command = command.replace(", where", " where")
		# print(command)
		# os._exit(0)
		# self.__cur.execute(command)
		# self.__conn.commit()
		
	# def get_wordslst(self, wdsLst, level, familiar, limit):
		# command = "select word from Words where level = '" + level + "' and familiar = " + str(familiar) + " order by familiar limit " + str(limit)
		# print (command)
		# self.__cur.execute(command)
		# content = self.__cur.fetchall();
		# if content:
			# wdsLst = wdsLst.extend(content)
			# return True
		# else :
			# print("can't get wordslst.")
			# return False

	def get_wordslst(self, wdsLst, where):
		command = "select word from Words where " + where
		print(command)
		self.__cur.execute(command)
		content = self.__cur.fetchall();
		if content:
			wdsLst = wdsLst.extend(content)
			print("Got wordslst: %d." %len(content))
			return True
		else:
			print("can't get wordslst.")
			return False

	def close(self):
		self.__cur.close()
		self.__conn.close()