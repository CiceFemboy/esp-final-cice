import os
DEFAULT_PATH = os.getcwd()
print(f"[DEBUG] installing pip")
with open(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\python313._pth", "a") as file:
    file.write("\nLib\nLib\site-packages\nInclude\pygame")
    file.close()
exec(open(DEFAULT_PATH + "\\get-pip.py").read())
print(f"[DEBUG] installing requirements")
import subprocess
import sys
import pip
subprocess.run([sys.executable, "-m", "pip", "install","-r", DEFAULT_PATH + "\\requirements.txt"])
import shutil
print(f"[DEBUG] installing demomunk")
os.mkdir(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk")
shutil.copyfile(DEFAULT_PATH + "\\ESP-scripts\\demomunk.py", DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk\\Game.py")
with open(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\Lib\\site-packages\\demomunk\\__init__.py", "w") as file:
	file.write('__all__ = ["Game"]')