#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import sys

# from globalVar import SetLogger

def CreateLogger(loggerName, logFile = None, level = logging.INFO):

	gLogger = logging.getLogger(loggerName)
	gLogger.setLevel(logging.DEBUG)

	if not logFile is None:
		# print(logFile)
		fh = logging.FileHandler(logFile, mode='w')
		fh.setLevel(level)
		fh_formatter = logging.Formatter(fmt = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s:\n%(message)s\n',
										datefmt = "%H:%M:%S")
		fh.setFormatter(fh_formatter)					
		gLogger.addHandler(fh)

	ch = logging.StreamHandler(stream = sys.stdout)
	ch.setLevel(level)
	ch_formatter = logging.Formatter(fmt = "%(filename)s[L%(lineno)03d] %(levelname)s: %(message)s",
									datefmt = "%H:%M:%S")
	ch.setFormatter(ch_formatter)
	gLogger.addHandler(ch)

	return gLogger