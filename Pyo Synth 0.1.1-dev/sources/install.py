#!/usr/bin/env python
# encoding: utf-8

"""
Copyright 2015 Alexandre Poirier

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
import shutil
from resources import config.VERSION

def installationProcess():
    HOME_PATH = os.path.expanduser("~")
    PREF_PATH = os.path.join(HOME_PATH, "Library", "Pyo Synth")
    HELP_DOC = os.path.join(PREF_PATH, "manuel_dutilisation_pyosynth.pdf")
    REC_PATH = os.path.join(PREF_PATH, "recfiles")
    EXP_PATH = os.path.join(HOME_PATH, 'Documents', 'Exemples Pyo Synth')
    DMG = os.path.join("Volumes", "Pyo Synth "+config.VERSION)

    if not os.path.exists(PREF_PATH):
        os.mkdir(PREF_PATH)
    if not os.path.exists(REC_PATH):
        os.mkdir(REC_PATH)
    if not os.path.exists(EXP_PATH):
        os.mkdir(EXP_PATH)

    for root, dirs, files in os.walk(os.path.join(DMG, 'package', 'Exemples')):
        for file in files:
            shutil.copy(os.path.join(root, file), os.path.join(EXP_PATH, file))

    shutil.copy(os.path.join(DMG, 'package','Pyo Synth'), os.path.join('Applications'))
    shutil.copy(os.path.join(DMG, 'package','m8dn3820gn57fjf9'), os.path.join(PREF_PATH,'m8dn3820gn57fjf9'))
    shutil.copy(os.path.join(DMG, 'package','manuel_dutilisation_pyosynth.pdf'), HELP_DOC)

    execfile(os.path.join(DMG, 'package','objects_inspector.py'))
    shutil.move(os.path.join(DMG, 'audio_rate_params_dict.txt'), os.path.join(PREF_PATH,'audio_rate_params_dict.txt'))


try:
    installationProcess()
except Exception, e:
    print "** A problem occurred during installation **"
    print e
else:
    print "Installation completed."
