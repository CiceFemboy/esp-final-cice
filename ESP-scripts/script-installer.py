import shutil
import os

DEFAULT_PATH = os.getcwd()

def install_demomunk() :
	print(f"[Script] - installation de demomunk")
	os.mkdir(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk")
	shutil.copyfile(DEFAULT_PATH + "\\ESP-scripts\\demomunk.py", DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk\\main.py")
	with open(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk\\__init__.py", "w") as file:
		file.write('__all__ = ["main"]')

def install_neatmunk() :
	print(f"[Script] - installation de neatmunk")
	os.mkdir(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\neat_munk")
	shutil.copyfile(DEFAULT_PATH + "\\ESP-scripts\\neat_munk.py", DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\neat_munk\\main.py")
	with open(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\neat_munk\\__init__.py", "w") as file:
		file.write('__all__ = ["main"]')

def update_completed() :
	print(f"[Script] - Scripts and Modules Updated!")

# vérifie si les modules du projet on déja été installer et reinstalle les scripts
# sinon c'est un simple installation des scripts (comme durant l'installation initiale)

if os.path.isdir(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk"):
	print(f"[Script] - demomunk et neatmunk déja installer !")
	print(f"[Script] - dé-installation des scripts existant sur python")
	shutil.rmtree(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\neat_munk")
	shutil.rmtree(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk")
	print(f"[Script] - ré-installation et mise à jour des scripts depuis le dossier ESP-scripts comme modules python")
	install_demomunk()
	install_neatmunk()
	update_completed()
else:
	install_demomunk()
	install_neatmunk()