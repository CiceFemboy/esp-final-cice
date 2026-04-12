import os
DEFAULT_PATH = os.getcwd()

# installation de pip

print(f"[DEBUG] installing pip")

exec(open(DEFAULT_PATH + "\\get-pip.py").read())

# installation des requirements pour le bon fonctionnement du programme

print(f"[DEBUG] installing requirements")
import subprocess
import sys
import pip
subprocess.run([sys.executable, "-m", "pip", "install", "--no-warn-script-location", "-r", DEFAULT_PATH + "\\requirements.txt"])

# installation des variables d'environnement

print(f"[DEBUG] installing updated environmnent variables on PATH")
with open(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\python313._pth", "a") as file:
    file.write(r"\nLib\nLib\site-packages\nInclude\pygame")
    file.close()
os.environ["PATH"] += os.pathsep + "\\python-3.13.12-embed-amd64\\Lib"
os.environ["PATH"] += os.pathsep + "\\python-3.13.12-embed-amd64\\Lib\\site-packages"
os.environ["PATH"] += os.pathsep + "\\python-3.13.12-embed-amd64\\Include\\pygame"

# installation de demomunk et neatmunk comme un module pour le bon fonctionnement du programme sur l'environement virtuel local python

import shutil

def install_demomunk() :
	print(f"[DEBUG] installing demomunk")
	os.mkdir(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk")
	shutil.copyfile(DEFAULT_PATH + "\\ESP-scripts\\demomunk.py", DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk\\Game.py")
	with open(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk\\__init__.py", "w") as file:
		file.write('__all__ = ["main"]')

def install_neatmunk() :
	print(f"[DEBUG] installing neatmunk")
	os.mkdir(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\neat_munk")
	shutil.copyfile(DEFAULT_PATH + "\\ESP-scripts\\neat_munk.py", DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\neat_munk\\main.py")
	with open(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\neat_munk\\__init__.py", "w") as file:
		file.write('__all__ = ["main"]')


def install_completed() :
	input("Installation Completed ! Press enter to continue")
	exec(open(DEFAULT_PATH + "\\ESP-scripts\\launcher.py").read())

if os.path.isdir(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk"):
	print(f"[DEBUG] demomunk already installed")
	print(f"[DEBUG] uninstalling existing demomunk module from python")
	shutil.rmtree(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\neatmunk")
	shutil.rmtree(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk")
	print(f"[DEBUG] reinstalling and updating demomunk module from ESP-script folder")
	install_demomunk()
	install_neatmunk()
	install_completed()
else :
	install_demomunk()
	install_neatmunk()
	install_completed()

