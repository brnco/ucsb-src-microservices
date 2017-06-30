#!/usr/bin/env python
import os

def make(path):
	if path.startswith("/") or path.startswith("\\"):
		path = path[1:]
	path.replace("\\","/")	
	if not os.name == 'posix': #if windows
		if "microservices-logs" in path:
			drive = "S:/"
		else:
			drive = "R:/"
		realpath = os.path.join(drive,path)
	else: #if mac/ unix
		if "microservices-logs" in path:
			drive = "/special/DeptShare/special"
		else:
			drive = "/special"
		realpath = os.path.join(drive,path)
	return realpath