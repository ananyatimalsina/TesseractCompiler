import requests
from requests_html import HTML
import os
import shutil
import zipfile
import subprocess
import sys
from configparser import ConfigParser

config = ConfigParser()

try:
    config.read("config.ini")
    update = config["Settings"]["update"]
    mode = config["Settings"]["def_mode"]

except Exception as e:
    print("Config File Is Corrupted or does not Exist!" + e)

if update == "True":
    try:
        if os.path.isdir("Git"):
            shutil.rmtree("Git")

        if os.path.isdir("Sw"):
            shutil.rmtree("Sw")

        if os.path.isdir("vcpkg"):
            shutil.rmtree("vcpkg")

    except Exception as e:
        print("Could not remove Git, vcpkg and Sw directorys. Please delete them manually and try again!")
        pass

    git_r = requests.get("https://github.com/git-for-windows/git/releases/")
    git_r = HTML(html=str(git_r.content))
    git_url = git_r.links
    for i in git_url:
        if "MinGit" in i:
            git_url = i
            break

    git_url = "https://github.com" + git_url
    sw_url = "https://software-network.org/client/sw-master-windows-client.zip"

    r_git = requests.get(git_url)
    r_sw = requests.get(sw_url)

    os.mkdir("Git")

    open("Git.zip", "wb").write(r_git.content)
    open("Sw.zip", "wb").write(r_sw.content)

    with zipfile.ZipFile("Git.zip", "r") as zf:
        zf.extractall("Git")

    with zipfile.ZipFile("Sw.zip", "r") as zf:
        zf.extractall("Sw")

    os.remove("Sw.zip")
    os.remove("Git.zip")

    with open("Install.bat", "w") as f:
        f.write("SET PATH=%PATH%;" + os.getcwd() + "/Git/cmd" + "\n")
        f.write("git clone https://github.com/microsoft/vcpkg" + "\n")
        f.write("./vcpkg/bootstrap-vcpkg.bat" + "\n")
        f.write("cd Sw" + "\n")
        f.write("sw setup")

    subprocess.call(["Install.bat"])

    os.remove("Install.bat")

    config.set("Settings", "update", "False")

    with open("config.ini", "w") as configfile:
        config.write(configfile)

while 1:
    command = input("Please Enter a Command: ")
    command = str(command).lower()

    if command == "help":
        print("List of avilable commands:")
        print("help - Shows a List of all avilable commands")
        print("start - Starts the install/update process")
        print("exit - Exists the programm")
        print("mode sw/vs - Changes compilation modes")

    elif command == "exit":
        sys.exit()

    elif command == "mode sw":
        mode = "sw"
        config.set("Settings", "def_mode", "sw")

        with open("config.ini", "w") as configfile:
            config.write(configfile)

        print("Success! Changed mode to " + mode)

    elif command == "mode vs":
        mode = "vs"
        config.set("Settings", "def_mode", "vs")

        with open("config.ini", "w") as configfile:
            config.write(configfile)

        print("Success! Changed mode to " + mode)

    elif command == "start":
        if mode == "vs":
            with open("Install.bat", "w") as f:
                f.write("cd vcpkg" + "\n")
                f.write("vcpkg install tesseract:x64-windows-static")

        elif mode == "sw":
            with open("Install.bat", "w") as f:
                f.write("cd Sw" + "\n")
                f.write("sw build org.sw.demo.google.tesseract.tesseract-master")

        subprocess.call(["Install.bat"])

        os.remove("Install.bat")