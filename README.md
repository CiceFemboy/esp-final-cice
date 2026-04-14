# To Do list

Done:
- OOP refactor
- Added neat functionality
- code rewritten so that creatures are written with json files (examples in creatures folder)
- installer script
- launcher script
- bat system executable to automatically set up the python environment and launch the program. (coupled with a install script and launcher script)
-----------------------------------

to do :  
- visualization
  - marqueurs derriere disant genre 1m, 2m, etc...
  - nodes
  - fitness graph
  - comme dans evolution voir generation par generation
  - species chart

- creature editor


--


---

# **Installation Guide - Cice**

**Working Systems**

- WINDOWS 10/11 x86_64 64bit

...

# Installation Process

1. **Download File named "projet ESP install folder.zip"

on windows use "Extract All" after right clicking on the compressed file, it should uncompress/unzip the zip file with its content as a folder automatically.

2. **Place the Project's Folder on your Desktop.

3. **Open the Folder named "working folder"

4. **Double Click and Execute 'run.bat' to Launch the project

**Important
on the first run, it will install the project's code, its requirements and install the python environment.
refer to the installation process later on the README to understand what exactly happens

5. **How the Installation Works**

What does the Launch and Installation process do?
(how installer.py, launcher.py and script-installer.py works)

**Launch Process (launcher.py)

1. **run.bat executes and opens launcher.py script using the python application embedded in the project.

2. **launcher.py verifies if lib folder exists (if it exists itmeans requirements are downloaded)

if the 'Lib' folder do not exist ; launcher.py executes installer.py and the installation process begins.

if the 'Lib' folder exists ; launcher.py do not proceed with the installation process and calls the script-installer.py script to refresh the project's code as python modules.

**installation Process (installer.py)

1. Install the Environment Variables on the python313._pth file to enable python to recognize pip as a python module.

2. Install pip (python module tha download and install python modules from the PyPi online package library) via the "get-pip.py" script (free online script that download and install the pip module and package from the internet)

3. Install requirements via pip

4. Install the project's code located in ESP-scripts as python modules (calls script-installer.py)

Now the project should be Installed

**Script Refresh Process (script-installer.py)

1. detects if the scripts are installed as Python modules

if demomunk exists as a pythonmodule ; it deletes the existing modules then reinstall the scripts' code on ES-scripts as python modules.

if demomunk does not exist as a python module ; install the scripts' code on ES-scripts as python modules.

# Running The Project

To run the project just execute the file named "run.bat", the project should launch normally.

**Manual Running**

If run.bat doesnt work properly

2.  Click and Run the Python application named Python.exe located in the embedded python application on the project.
3.  Run the following command to launch the project :

--

exec(open("change-dir.py").read()), exec(open("ESP-scripts\\launcher.py").read())

--

# Troubleshooting with the installation process

1. **Pip does not install properly and is not usable**

This issue stems from pip package module being successfully installed but the module is not recognized by the python intepreter. this is caused by a missing library and package site path link accessible to the python intepreter. without those paths, it cannot access and import the module.

to fix this issue you will need to modify manually the "._pth" file and append (add it at the end of the file) the required libraries paths so the python interpreter will recognize ad be able to import the pip module and use pip.

Insert the library paths after "#import site" inside the "python313._pth" file

insert the following string :

--

Lib

Lib\site-packages

Include\pygame

Scripts

--

2. **'Script.py' does not exists**

you are not in the correct working directory, you need to change the working directory to the correct one. 

run this command to change working directory :

--

exec(open("change-dir.py").read())

--

after that it should have displayed : [DEBUG] current directory : ~[content]~
you should be in the working directory in the working folder outside of the python embedded virtual environment directory.

3. **'Module' does not exists**

close the interpreter's prompt then re-execute the python interpreter

---

# Credits

- **Python Project**
Using the embedded python application from the official python website ( python-embed 3.13.12 for amd64 (x86_64) )

Credits to the Python Project contributors and to Python.org

link : https://www.python.org/

download link for the exact version we used : https://www.python.org/ftp/python/3.13.12/python-3.13.12-embed-amd64.zip

- **Get-pip.py Script**

Using the get-pip.py script on github. 

Credits to the contributors and those who made it and continued the project.

link : https://github.com/pypa/get-pip
