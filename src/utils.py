#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import logging

# from globalVar import SetLogger


def create_logger(logger_name: str, logFile: str = "", level: int = logging.INFO):

	glogger = logging.getLogger(logger_name)
	glogger.setLevel(logging.DEBUG)

	if logFile:
		# print(logFile)
		fh = logging.FileHandler(logFile, mode='w')
		fh.setLevel(level)
		fh_formatter = logging.Formatter(fmt = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s:\n%(message)s\n',
										datefmt = "%H:%M:%S")
		fh.setFormatter(fh_formatter)					
		glogger.addHandler(fh)

	ch = logging.StreamHandler(stream = sys.stdout)
	ch.setLevel(level)
	ch_formatter = logging.Formatter(fmt = "%(filename)s[L%(lineno)03d] %(levelname)s: %(message)s",
									datefmt = "%H:%M:%S")
	ch.setFormatter(ch_formatter)
	glogger.addHandler(ch)

	return glogger
