#!/usr/bin/env python
# encoding: utf-8

"""
Copyright 2017 Alexandre Poirier

This file is part of Pyo Synth, a GUI written in python that helps
with live manipulation of synthesizer scripts written with the pyo library.

Pyo Synth is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

Pyo Synth is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Pyo Synth.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import time
import pickle
import shutil
from sources.resources.config import *

MSG_KEYW = {0:'INFO',1:'WARNING',2:'ERROR'}
def printMessage(text, level=0):
    tclock = "%.2f" % (time.clock()%1)
    print "[%s.%s][%s] %s" % (time.strftime("%H:%M:%S"), tclock.split('.')[1], MSG_KEYW[level], text)

def validateVersions():
    import sys
    from pyo import getVersion
    import wxversion
    if sys.version_info[:3] != VERSIONS['python']:
        printMessage("python {}.{}.{} must be used to run Pyo Synth from sources".format(*VERSIONS['python']), 2)
        exit()
    if getVersion() != VERSIONS['pyo']:
        printMessage("pyo version installed: {}.{}.{} ; pyo version required {}.{}.{}".format(*getVersion()+VERSIONS['pyo']), 1)
        printMessage("Installed pyo version doesn't match what Pyo Synth uses. Some objects might not be available.", 1)
    if not wxversion.checkInstalled('2.8'):
        printMessage("wxPython version required {}.{}.{}".format(*VERSIONS['wx']), 1)

def installationProcess():
    CWD = os.getcwd()

    # copying examples
    ex_path = os.path.join(CWD, 'package', 'Examples')
    if os.path.exists(ex_path):
        printMessage("Copying examples files", 0)
        for root, dirs, files in os.walk(ex_path):
            for file in files:
                if '.DS_Store' not in file:
                    shutil.copy(os.path.join(root, file), os.path.join(EXP_PATH, "Examples", file))
    else:
        printMessage("Couldn't find examples folder", 2)

    # copying tutorials
    tuto_path = os.path.join(CWD, 'package', 'Tutorials')
    if os.path.exists(tuto_path):
        printMessage("Copying tutorials files", 0)
        for root, dirs, files in os.walk(tuto_path):
            for file in files:
                if '.DS_Store' not in file:
                    shutil.copy(os.path.join(root, file), os.path.join(EXP_PATH, "Tutorials", file))
    else:
        printMessage("Couldn't find tutorials folder", 2)


    printMessage("Copying manual", 0)
    shutil.copy(os.path.join(CWD, package, 'manuel_dutilisation_pyosynth.pdf'), os.path.join(PREF_PATH, 'manuel_dutilisation_pyosynth.pdf'))
    printMessage("Building pyo objects dictionary...", 0)
    execfile(os.path.join(CWD, 'package', 'scripts','objects_inspector.py'), globals())
    printMessage("Moving dictionary", 0)
    shutil.move(os.path.join(CWD, 'audio_rate_params_dict.txt'), os.path.join(PREF_PATH,'audio_rate_params_dict.txt'))


validateVersions()
try:
    installationProcess()
except Exception, e:
    printMessage("A problem occurred during installation", 2)
    printMessage(e, 2)
else:
    printMessage("Installation completed.", 0)
