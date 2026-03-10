import sys
import os
import subprocess
exec(open("change_dir.py").read())
path = os.getcwd()
PATH_TO_APPEND = "\\requirements.txt"
path = path + PATH_TO_APPEND
print(new_path)
print(f"[DEBUG] installing requirements")
subprocess.run([sys.executable, "-m", "pip", "install","-r", "requirements.txt"])
