import os
DEFAULT_PATH = os.getcwd()
print(f"[DEBUG] installing pip")
with open(DEFAULT_PATH + "\\python-3.13.12-embed-amd64\\python313._pth", "a") as file:
    file.write("\nLib\nLib\site-packages")
    file.close()
exec(open(DEFAULT_PATH + "\\get-pip.py").read())
print(f"[DEBUG] installing requirements")
import subprocess
import sys
import pip
subprocess.run([sys.executable, "-m", "pip", "install","-r", DEFAULT_PATH + "\\requirements.txt"])
