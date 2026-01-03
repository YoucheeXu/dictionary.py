#-*- encoding:utf-8 -*-
# -*- coding: utf-8 -*-
#coding=utf-8

import platform

class globalVar:
	app = None
	gLogger = None

	# Platforms
	WINDOWS = (platform.system() == "Windows")
	LINUX = (platform.system() == "Linux")
	MAC = (platform.system() == "Darwin")

	b32bit = (platform.architecture()[0] == "32bit")

def SetApp(app): globalVar.app = app
def GetApp(): return globalVar.app

def IsWindows(): return globalVar.WINDOWS
def IsLinux(): return globalVar.LINUX
def IsMAC(): return globalVar.MAC
def Is32bit(): return globalVar.b32bit

def SetLogger(logger): globalVar.gLogger = logger 
def GetLogger(): return globalVar.gLogger
