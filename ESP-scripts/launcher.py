import os
import subprocess
import sys

DEFAULT_PATH = os.getcwd()

def start() :
	subprocess.run([sys.executable, "ESP-scripts\\menu.py"])

# vérifie si le programe à été installer

if os.path.isdir(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib"):
	subprocess.run([sys.executable, "ESP-scripts\\script-installer.py"])
	start()
else :
	subprocess.run([sys.executable, "ESP-scripts\\installer.py", "--no-warn-script-location"])
	start()