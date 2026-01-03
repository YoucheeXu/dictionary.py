#-*- encoding:utf-8 -*-
# -*- coding: utf-8 -*-
#coding=utf-8
import platform


class GlobalVar:
	app = None
	gLogger = None

	# Platforms
	WINDOWS: bool = (platform.system() == "Windows")
	LINUX: bool = (platform.system() == "Linux")
	MAC: bool = (platform.system() == "Darwin")

	b32bit: bool = (platform.architecture()[0] == "32bit")

def set_app(app): GlobalVar.app = app
def get_app(): return GlobalVar.app

def is_windows(): return GlobalVar.WINDOWS
def is_linux(): return GlobalVar.LINUX
def is_mac(): return GlobalVar.MAC
def is_32bit(): return GlobalVar.b32bit

def set_logger(logger): GlobalVar.gLogger = logger 
def get_logger(): return GlobalVar.gLogger
