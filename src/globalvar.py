#-*- encoding:utf-8 -*-
# -*- coding: utf-8 -*-
#coding=utf-8

import platform

class globalVar:
	app = None

	# Platforms
	WINDOWS = (platform.system() == "Windows")
	LINUX = (platform.system() == "Linux")
	MAC = (platform.system() == "Darwin")

def GetApp(): return globalVar.app
def SetApp(app): globalVar.app = app

def IsWindows(): return globalVar.WINDOWS
def IsLinux(): return globalVar.LINUX