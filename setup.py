import os
import sys
import shutil
from distutils.core import setup
import py2exe

# Import external modules required by logic_gates to ensure that they exist
import pygame

if len(sys.argv) < 2:
    sys.argv.append("py2exe")

# The following DLL hack is only useful if bundle_files = 1
# DLL Hack
old_determine_dll_type = py2exe.dllfinder.DllFinder.determine_dll_type
pack = ("smpeg.dll", "libfreetype-6.dll", "libogg-0.dll", "sdl_ttf.dll",)


# returning "EXT" packs the dll into the program
def determine_dll_type(self, imagename):
    if imagename.find("SDL") != -1:
        return "EXT"
    if imagename.find("sdl") != -1:
        return "EXT"
    if os.path.basename(imagename).lower() in pack:
        return "EXT"
    return old_determine_dll_type(self, imagename)
# Dissable the hack because tkinter requires .dlls in the folder anyway
# py2exe.dllfinder.DllFinder.determine_dll_type = determine_dll_type


# I have used a tkinter hack:
# Python34\lib\tkinter\_fix.py
# 57:    if "TCL_LIBRARY" not in os.environ or True:
# 67:    if "TK_LIBRARY" not in os.environ or True:
# 73:    if "TIX_LIBRARY" not in os.environ or True:
# (Added the "or True")
# This is because when py2exe.hooks tries to hook tkinter,
# it depends on "TCL_LIBRARY" not being in os.environ


if sys.maxsize > 2**32:
    platform = "64bit"
else:
    platform = "32bit"
# Full path of files is needed
icon_file = os.path.join(os.getcwd(), "images", "favicon.ico")
files = list(os.path.join(os.getcwd(), "images", i)
             for i in os.listdir("images")
             if i.endswith(".png"))
files.append(icon_file)
# These modules are not used by the program, there are probobally more
# that can be excluded but most of the remaining files are small or
# required
excludes = ["email",
            "_ctypes",
            "html",
            "http",
            "lib2to3",
            "logging",
            "multiprocessing",
            "pkg_resources",
            "pydoc_data",
            "unittest",
            "urllib",
            "xml",
            "xmlrpc",
            "_markerlib",
            "_ssl",
            "locale",
            "optparse",
            "calendar",
            "pydoc",
            "tarfile",
            "inspect",
            "datetime",
            "doctest",
            "zipfile",
            "difflib",
            "subprocess",
            "shutil",
            "platform",
            "unicodedata",
            "bz2"]
if os.path.isdir("dist"):
    print("Cleaning up "+os.path.join(os.getcwd(), "dist"))
    shutil.rmtree("dist")
setup(
    windows=[
        {
            "script": "logic_gates.py",
            "icon_resources": [(0, icon_file)]
            }
        ],
    version = "1.0.0",
    description = "A logic gates simulator and boolean expression simplifier written in python using pygame.",
    url = "",
    author = "Qi-rui Chen",
    author_email = "Qi-rui.Chen@hotmail.co.uk",
    name="Logic Gates",
    data_files=[("images", files)],
    zipfile=None,
    options={
        "py2exe":
        {"optimize": 2,
         "bundle_files": 2,
         "compressed": True,
         "includes": "pygame",
         "excludes": excludes
         }
        }
    )
if os.path.isdir("Logic Gates "+platform):
    print("Cleaning up "+os.path.join(os.getcwd(), "Logic Gates "+platform))
    shutil.rmtree("Logic Gates "+platform)
print("Moving dist to "+os.path.join(os.getcwd(), "Logic Gates "+platform))
shutil.move(os.path.join(os.getcwd(), "dist"),
            os.path.join(os.getcwd(), "Logic Gates "+platform))
