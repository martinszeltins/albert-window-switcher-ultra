# -*- coding: utf-8 -*-

"""Window Switcher Ultra.
X11 window switcher that actually works.
Synopsis: <trigger> <filter>"""

import os
import time
import threading
import subprocess
from albert import *

__title__ = "Window Switcher Ultra"
__version__ = "0.1.0"
__triggers__ = "win "
__authors__ = "Martins Zeltins"
__exec_deps__ = ["wmctrl"]

defaultIconPath = os.path.dirname(__file__) + "/icon.png"
isCacheTimerActive = False
cachedResults = []

def clearCachedResultsAfterThirtySeconds():
    global cachedResults
    global isCacheTimerActive
    time.sleep(30)
    cachedResults = []
    isCacheTimerActive = False

def getOpenWindows(query):
    global cachedResults
    global isCacheTimerActive
    opened_windows = []
    query_clean = query.string.strip().lower()

    # Do we have cached results? Use those, it will be faster!
    if len(cachedResults) > 0:
        for result in cachedResults:
            # If there is a search query, show only those results that match
            if query_clean:
                if not query_clean in result.text.lower() and not query_clean in result.subtext.lower():
                    continue

            opened_windows.append(result)

        return opened_windows


    # Else we will populate the cached results
    wmctrl_output = subprocess.check_output(["wmctrl", "-lpx"])
    window_lines = wmctrl_output.decode().split("\n")

    for window_line in window_lines:
        columns = window_line.split()

        if len(columns) > 1:
            window_id = columns[0]
            pid = columns[2]
            window_title = " ".join(columns[5:])
            wm_class = columns[3]

            # Get window title and description from wmctrl and ps
            # And add some exceptions in those cases where it is needed.
            if wm_class == "Steam.Steam":
                ps_output = "steam"
                window_title = "Steam"
            elif wm_class == "jetbrains-phpstorm.jetbrains-phpstorm":
                ps_output = "phpstorm"
                window_title = window_title + " - " + "PHPStorm"
            else:
                ps_output = subprocess.check_output(f"ps -eo pid,comm | grep {pid}", shell=True)
                ps_output = ps_output.decode()
                ps_output = ps_output.split()

                if len(ps_output) > 0:
                    ps_output = ps_output[1]
                else:
                    ps_output = ""

            if ps_output == "eog":
                window_title = window_title + " - " + "Image Viewer"

            if ps_output == "nautilus":
                window_title = window_title + " - " + "Nautilus File Manager"

            if ps_output == "gedit":
                window_title = window_title + " - " + "Text Editor"

            # We don't want to see these appear in search results
            if ps_output == "albert" or ps_output == "guake":
                continue
            
            # If there is a search query, show only those results that match
            if query_clean:
                if not query_clean in window_title.lower() and not query_clean in ps_output.lower():
                    continue

            # Find the icon by executable name or if we cannot find it
            # We will provide default icons ourselves.
            iconPath = iconLookup(ps_output.lower())

            if not iconPath:
                if ps_output == "code": iconPath = os.path.dirname(__file__) + "/vscode.png"
                if "gimp" in ps_output: iconPath = os.path.dirname(__file__) + "/gimp.png"
                if ps_output == "phpstorm": iconPath = os.path.dirname(__file__) + "/phpstorm.png"
                if ps_output == "chrome": iconPath = os.path.dirname(__file__) + "/google-chrome.png"
                if ps_output == "sublime_text": iconPath = os.path.dirname(__file__) + "/sublime_text.png"
                if "gnome-terminal" in ps_output: iconPath = os.path.dirname(__file__) + "/gnome-terminal.png"
                if "system-mo" in ps_output: iconPath = os.path.dirname(__file__) + "/gnome-system-monitor.png"

            item = Item(id=window_title,
                icon=iconPath or defaultIconPath,
                text=window_title,
                subtext=ps_output,
                actions=[
                    ProcAction(text="Switch Window", commandline=["wmctrl", '-i', '-a', window_id] ),
                ]
            )

            opened_windows.append(item)
            if not query_clean: cachedResults.append(item)

    # Start a timer that will clear the cached results after 30 seconds
    # It also makes sure the timer is not running already.
    if "thread" not in globals() or not thread.is_alive():
        if not isCacheTimerActive:
            thread = threading.Thread(target=clearCachedResultsAfterThirtySeconds)
            thread.start()
            isCacheTimerActive = True

    return opened_windows

def handleQuery(query):
    if query.isTriggered:
        results = getOpenWindows(query)
        return results
