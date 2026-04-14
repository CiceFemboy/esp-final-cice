import os
DEFAULT_PATH = os.getcwd()

# installation des variables d'environnement

print(f"[DEBUG] installing environmnent variables on PATH")
with open(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\python313._pth", "a") as file:
    file.write("\nLib\nLib\\site-packages\nInclude\\pygame\nScripts")
    file.close()

# installation de pip

import subprocess
import sys

print(f"[DEBUG] installing pip")

exec(open("get-pip.py").read())

# installation des requirements pour le bon fonctionnement du programme

print(f"[DEBUG] installing requirements")

import pip

subprocess.run([sys.executable, "-m", "pip", "install", "--no-warn-script-location", "-r", DEFAULT_PATH + "\\requirements.txt"])

# installation de demomunk et neatmunk comme un module pour le bon fonctionnement du programme sur l'environement virtuel local python

subprocess.run([sys.executable, "ESP-scripts\\script-installer.py"])

def install_completed() :
	input("Installation Completed ! Press enter to continue")

install_completed()

