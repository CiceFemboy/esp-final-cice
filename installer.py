import sys
import os
import subprocess
exec(open(os.getcwd() + "\\get-pip.py").read())
print(f"[DEBUG] installing requirements")
subprocess.run([sys.executable, "-m", "pip", "install","-r", "requirements.txt"])