
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


---

run guide - install and run project's code

WINDOWS 10/11 x86_64 64 bit version

-- Installation --
create an empty working folder on the desktop or anywhere accessible

1. install python
 -place the python zip inside the working folder
 -unzip python zip and place the extracted python folder in the empty working folder
2. install change_dir.py script (moves the interpreter current directory to the working area)
 -put change_dir.py in the python folder
run python.exe
run on python >> exec(open("change_dir.py").read()) <<
this commandis important as it it enables you to read scripts in the working directory instead of inside the embeded python directory.
4. install pip
run on python >> exec(open("get-pip.py").read()) <<
there should be logs of the installation and new files inside the python folder. Pip is now installed
the command window should close, if not close it

*from the get-pip script online on github. credits to the contributors who made it.
https://github.com/pypa/get-pip

Now you should have pip installed on the embeded version of python

4. add packages path to the file named "python313._pth"

Insert library path  after '#import site'inside the file to ensure packages are recognized by python

Lib

Lib\site-packages

5. install requirements for the project's script 

run python.exe
run on python >> exec(open("requirements_pip_installer.py").re
