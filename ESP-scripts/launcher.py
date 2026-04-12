import os

DEFAULT_PATH = os.getcwd()

def start() :
	exec(open("ESP-scripts\\menu.py").read())

# verifie si le programe à été installer 

if os.path.isdir(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib"):
	start()
else :
	exec(open("ESP-scripts\\installer.py").read())
	start()


# exec(open(DEFAULT_PATH + "\\ESP-scripts\\neat_munk.py").read())