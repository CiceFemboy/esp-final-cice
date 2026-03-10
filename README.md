# To Do list

Done:
- OOP refactor
- Added neat functionality
- code rewritten so that creatures are written with json files (examples in creatures folder)

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

- update the installer script so it can modify the ._pth automatically

---

# Installation and Running Guide - Cice

**Working Systems :**

- WINDOWS 10/11 x86_64 64bit

...

**-- Installation Process --**

1. Create an empty working folder on the desktop or anywhere accessible

( the name of the working folder doesn't matter, use something you will remember )

2. Install the python virtual environment

  - Download the embeddded python zip from the repository, (we took an online version)
  - Place the python zip inside the working folder
  - Unzip the compressed file and extract in a folder 

( on windows use "Extract All" after right clicking on the compressed file, it should uncompress/unzip the file then create a folder with the same name and place the content inside automatically)

3. Download Install the installer scripts

  - Download "change-dir.py" and "installer.py" and "get-pip.py" from the repository.
  - Place "installer.py" and "get-pip.py" directly in the working folder.
  - Place "Change-dir.py" inside the embedded python folder ( "python-3.x.x-embed-amd64" )

4. Download the Projects Files and Scripts.

  - Download "requirements.txt", "demomunk.py" and "neat_munk.py" and place the files in the working folder.

5. Install the project

  - Go in the embedded python folder ( "python-3.x.x-embed-amd64" ) then run the Python application named python.exe
  - Run the following command, it will run the installation scripts :

--

import os

exec(open(os.getcwd() + "\\change-dir.py").read()), exec(open(os.getcwd() + "\\installer.py").read())

--

This important as it changes at first the working directory inside the python interpretor to the project default directory outside of the "python-3.x.x-embed-amd64" folder and reads the installation scripts.

This Installation process install pip which is the most used package downloader and installer for  python and link the required libraries so the virtual embedded python environment can use pip.

Now your project should be Installed

**-- Running The Project --**

To run the python scripts from the project you should use the embedded python application. you could use other means but this guide will not help you with those. 

**Only run AFTER the project is installed**

1.  Open the Working Directory
2.  Open the the embedded python folder ( "python-3.x.x-embed-amd64" )
3.  Click and Run Python.exe
4.  Change Working Directory from the embedded python folder ( "python-3.x.x-embed-amd64" ) to the Working Folder
-  use this command :
--
exec(open("change-dir.py").read())
--
5. Run the project Scripts
- use this command and modify the command according to which script you need or want to run
 for example :
--
exec(open("demomunk.py").read())
--

---

# Troubleshooting with the installation process

1. Pip does not install properly and is not usable

This issue stems from pip package module being successfully installed but the module is not recognized by the python intepreter. this is caused by a missing library and package site path link accessible to the python intepreter. without those paths, it cannot access and import the module.

to fix this issue you will need to modify manually the "._pth" file and append (add it at the end of the file) the required libraries paths so the python interpreter will recognize ad be able to import the pip module and use pip.

Insert the library paths after "#import site" inside the "python313._pth" file

insert the following string :

--

Lib

Lib\site-packages

--

2. Scripts does not exists

you are not in the correct working directory, you need to change the working directory to the correct one. 

run this command >>
exec(open("change-dir.py").read())

only the change-dirpy script is located in the embedded python folder ( "python-3.x.x-embed-amd64" ), all other scripts will not be there, thus why you cannot run any of the scripts because they are not located there.

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
