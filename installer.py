import os
DEFAULT_PATH = os.getcwd()

# installation de pip

print(f"[DEBUG] installing pip")
with open(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\python313._pth", "a") as file:
    file.write("\nLib\nLib\site-packages\nInclude\pygame")
    file.close()
exec(open(DEFAULT_PATH + "\\get-pip.py").read())

# installation des requirements pour le bon fonctionnement du programme

print(f"[DEBUG] installing requirements")
import subprocess
import sys
import pip
subprocess.run([sys.executable, "-m", "pip", "install","-r", DEFAULT_PATH + "\\requirements.txt"])

# installation de demomunk comme un module pour le bon fonctionnement du programme sur l'environement virtuel local python

import shutil

def install_demomunk() :
	print(f"[DEBUG] installing demomunk")
	os.mkdir(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk")
	shutil.copyfile(DEFAULT_PATH + "\\ESP-scripts\\demomunk.py", DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk\\Game.py")
	with open(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk\\__init__.py", "w") as file:
		file.write('__all__ = ["Game"]')

def install_completed() :
	sys.exit(input('Installation Completed ! Press enter to continue and close the prompt. To launch the program re-execute the python interpreter and run the following code : exec(open("change-dir.py").read()), exec(open("launcher.py").read())'))

if os.path.isdir(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk"):
	print(f"[DEBUG] demomunk already installed")
	print(f"[DEBUG] uninstalling existing demomunk module from python")
	shutil.rmtree(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk")
	print(f"[DEBUG] reinstalling and updating demomunk module from ESP-script folder")
	install_demomunk()
	install_completed()
else :
	print(f"[DEBUG] installing demomunk")
	install_demomunk()
	install_completed()

