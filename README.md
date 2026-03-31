# To Do list

Done:
- OOP refactor
- Added neat functionality
- code rewritten so that creatures are written with json files (examples in creatures folder)
- update the installer script so it can modify the ._pth automatically (updated and now working)

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

- create a bat system executable to automatically set up the python environment rather than manually installing.

---

# **Installation and Running Guide - Cice **

**Working Systems :**

- WINDOWS 10/11 x86_64 64bit

...

# Installation Process

**Important**

the file named "projet ESP install folder.zip" contains a premade installation folder. you can just use it to install the program without setting up manually the environment. extract the file's content on your desktop and skip to step 5. 


1. **Create an empty working folder on the desktop or anywhere accessible**

( the name of the working folder doesn't matter, use something you will remember )

2. **Install the python virtual environment**

  - Download the embeddded python zip from the repository, (we took an online version)
  - Place the python zip inside the working folder
  - Unzip the compressed file and extract in a folder 

( on windows use "Extract All" after right clicking on the compressed file, it should uncompress/unzip the file then create a folder with the same name and place the content inside automatically)

3. **Download the installer scripts**

  - Download "change-dir.py" and "installer.py" and "get-pip.py" from the github repository.
  - Place "installer.py" and "get-pip.py" directly in the working folder.
  - Place "Change-dir.py" inside the embedded python folder ( "python-3.x.x-embed-amd64" )

4. **Download the Projects Files and Scripts.**

  - Download "requirements.txt", the files in the ESP-scripts github folder, the files in creatures folder from the github repository and place them in the working folder.
  - Make a folder named exactly "ESP-scripts" then place the files downloaded from the github folder with the same name inside the newly created folder.
  - Make a folder named exactly "creatures" then place the files downloaded from the github folder with the same name inside the newly created folder.

5. **Install the project**

**if you are on a school pc (restricted user permissions)**

  - run the Python shortcut. 
  - Run the following command, it will run the installation scripts :

--

import os
exec(open(os.getcwd() + "\\change-dir.py").read()), exec(open(os.getcwd() + "\\installer.py").read())

--

**if you are on your pc**

  - run the Python shortcut.
  - Run the following command, it will run the installation scripts :

--

import os
exec(open(os.getcwd() + "\\installer.py").read())

--

**if the shortcut python interpreter doesnt work properly, close the prompt and go in the embedded python folder ( "python-3.x.x-embed-amd64" ) then run the Python application named python.exe, then run the following command :**

--

import os
exec(open(os.getcwd() + "\\change-dir.py").read()), exec(open(os.getcwd() + "\\installer.py").read())

--

This important as it changes at first the working directory inside the python interpretor to the project default directory outside of the "python-3.x.x-embed-amd64" folder and reads the installation scripts.

This Installation process install pip which is the most used package downloader and installer for  python and link the required libraries so the virtual embedded python environment can use pip.

Now your project should be Installed

# Running The Project

To run the python scripts from the project you should use the embedded python application. you could use other means but this guide will not help you with those. 

**on School PCs (limited permissions)**

Only run AFTER the project is installed

2.  Click and Run the Python shortcut in the working folder.
3.  Run the following command to launch the project :

--

exec(open("change-dir.py").read()), exec(open("launcher.py").read())

--

**on your PC**

**Only run AFTER the project is installed (school pc) **

2.  Click and Run the Python shortcut in the working folder.
3.  Run the following command to launch the project :

--

exec(open("launcher.py").read())

--

**on your PC if shortcut doesnt work properly**

Only run AFTER the project is installed

1.  Open the the embedded python folder ( "python-3.x.x-embed-amd64" )
2.  Click and Run Python.exe
3.  Run the following command to launch the project :

--

exec(open("change-dir.py").read()), exec(open("launcher.py").read())

--

# Troubleshooting with the installation process

1. Pip does not install properly and is not usable

This issue stems from pip package module being successfully installed but the module is not recognized by the python intepreter. this is caused by a missing library and package site path link accessible to the python intepreter. without those paths, it cannot access and import the module.

to fix this issue you will need to modify manually the "._pth" file and append (add it at the end of the file) the required libraries paths so the python interpreter will recognize ad be able to import the pip module and use pip.

Insert the library paths after "#import site" inside the "python313._pth" file

insert the following string :

--

Lib
Lib\site-packages
Include\pygame

--

2. Scripts does not exists

you are not in the correct working directory, you need to change the working directory to the correct one. 

run this command to change working directory :

--

exec(open("change-dir.py").read())

--

after that it should have displayed : [DEBUG] current directory : ~[content]~
you should be in the working directory in the working folder outside of the python embedded virtual environment directory.

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
