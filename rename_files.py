import os
import string

def list_files(path):
    # returns a list of names (with extension, without full path) of all files 
    # in folder path
    files = []
    for name in os.listdir(path):
        if os.path.isfile(os.path.join(path, name)):
            files.append(name)
    return files 

files = list_files("./")

for file in files:
    if "#" in file:
        file = string.replace(file, "#", "\\#")
        new_file = string.replace(file, "\\#", "_")
        os.system("mv " + file + " " + new_file)
        print new_file 
