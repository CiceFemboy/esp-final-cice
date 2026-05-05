import os
DEFAULT_PATH = os.getcwd()

print("[Installation] - Installation de EVO SIM")

# installation des variables d'environnement

print(f"[Installation] - installation des variables d'environement sur PATH")
with open(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\python313._pth", "a") as file:
    file.write("\nLib\nLib\\site-packages\nInclude\\pygame\nScripts")
    file.close()

# installation de pip

import subprocess
import sys

print(f"[Installation] - installation de pip")

exec(open("get-pip.py").read())

# installation des requirements pour le bon fonctionnement du programme

print(f"[Installation] - installation des requirements")

import pip

subprocess.run([sys.executable, "-m", "pip", "install", "--no-warn-script-location", "-r", DEFAULT_PATH + "\\requirements.txt"])

# installation de tkinter

print(f"[Installation] - installation de tkinter")

import shutil

subprocess.run([sys.executable, "-m", "pip", "install", "--no-warn-script-location", "tkinter-embed"])

os.mkdir(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\lib")
shutil.copytree(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\tcl\\tcl8.6", DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\lib\\tcl8.6")
shutil.copytree(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\tcl\\tk8.6", DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\lib\\tk8.6")

# installation de demomunk et neatmunk comme un module pour le bon fonctionnement du programme sur l'environement virtuel local python

subprocess.run([sys.executable, "ESP-scripts\\script-installer.py"])

def install_completed() :
	input("Installation Completer ! Appuyer entrer pour continuer")

install_completed()

