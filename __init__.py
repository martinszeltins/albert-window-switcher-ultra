# -*- coding: utf-8 -*-

"""Window Switcher Ultra.
Sysnopsis: <trigger> <query>"""

from subprocess import run
from albert import *

__title__ = "Window Switcher Ultra"
__version__ = "1.0.0"
__triggers__ = "win "
__authors__ = "Martins Zeltins"
__exec_deps__ = ["wmctrl"]

iconPath = os.path.dirname(__file__) + "/icon.svg"

def handleQuery(query):
    if query.isTriggered:
        return Item(id="Window Switcher Ultra",
                    icon=iconPath,
                    text="Window Switcher Ultra",
                    subtext="Search for %s" % (query.string),
                    actions=[ProcAction("Do something with %s" % (query.string),
                                        ["gnome-dictionary", "--look-up=%s" % query.string])])
