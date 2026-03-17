import os
path = os.getcwd()
def change_path(path):
    temp_path = path
    value = len(temp_path) - 1
    while value != 0:
        if temp_path[value] != "\\" :
            temp_path = temp_path[:-1]
            value -= 1
        else:
            temp_path = temp_path[:-1]
            print(f"[DEBUG] Absolute Path = {temp_path}")
            return temp_path
new_path = change_path(path)
os.chdir(new_path)
print(f"[DEBUG] Current directory = {os.getcwd()}")
