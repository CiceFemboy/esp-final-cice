import shutil
import os

DEFAULT_PATH = os.getcwd()

def install_demomunk() :
	print(f"[DEBUG] installing demomunk")
	os.mkdir(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk")
	shutil.copyfile(DEFAULT_PATH + "\\ESP-scripts\\demomunk.py", DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk\\main.py")
	with open(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk\\__init__.py", "w") as file:
		file.write('__all__ = ["main"]')

def install_neatmunk() :
	print(f"[DEBUG] installing neatmunk")
	os.mkdir(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\neat_munk")
	shutil.copyfile(DEFAULT_PATH + "\\ESP-scripts\\neat_munk.py", DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\neat_munk\\main.py")
	with open(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\neat_munk\\__init__.py", "w") as file:
		file.write('__all__ = ["main"]')

def update_completed() :
	print(f"[DEBUG] Scripts and Modules Updated!")

# vérifie si les modules du projet on déja été installer et reinstalle les scripts
# sinon c'est un simple installation des scripts (comme durant l'installation initiale)

if os.path.isdir(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk"):
	print(f"[DEBUG] demomunk and neatmunk already installed")
	print(f"[DEBUG] uninstalling existing modules from python")
	shutil.rmtree(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\neat_munk")
	shutil.rmtree(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk")
	print(f"[DEBUG] reinstalling and updating scripts from ESP-scripts folder as python modules")
	install_demomunk()
	install_neatmunk()
	update_completed()
else:
	install_demomunk()
	install_neatmunk()