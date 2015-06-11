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
import pickle
import time

#--------------------------------------------
#--------------- Constantes -----------------
#--------------------------------------------
VERSION = "0.1.1"
crash_save_func = None
hide_main_win = None
UNIT_SIZE = (130,110)
WHEELS_BOX_WIDTH = 100
NB_ELEM_ROW = 8
FONT_SIZE = {"unused":12,"title":14, "midilearn":16,"value":25,"adsr":10}
REFRESH_RATE = 1./13
BG_COLOUR = "#333333"
STATS_BAR_HGT = 49
SETUP_PANEL_HGT = 61
TAB_WIN_HGT = 300
MAX_RECENT_SCRIPTS = 10
POLYPHONY = 10

REC_FORMAT_DICT = {0:".wav",1:".aif",2:".au",3:"",4:".sd2",5:".flac",6:".caf",7:".ogg"}
REC_FORMAT = 0
REC_BIT_DEPTH = 1

PATCH_BANNER = "#------------------------PATCH------------------------#"
PRESET_BANNER = "#------------------------PRESET------------------------#"

# defines different mapping solutions for the computer keyboard
# first number is the approximate span of the keyboard mapping in octaves (rounded up)
# note : in the future, the user will be able to define his own
mapping_styles = {'keys':[2,90,83,88,68,67,86,71,66,72,78,74,77,81,50,87,51,69,82,53,84,54,89,55,85],
                  'typewriter':[4,308,306,90,88,67,86,66,65,83,68,70,71,81,87,69,82,84,49,50,51,52,53,
                                54,55,56,57,48,89,85,73,79,80,72,74,75,76,59,78,77,44,46,142]}
DEFAULT_MAP_STYLE = 'keys'

NOTE_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
MIDI_NOTES_NAMES = []
octave = -2
count, i = 0,0
while count<128:
    note = "%s%d"%(NOTE_NAMES[i],octave)
    MIDI_NOTES_NAMES.append(note)
    count += 1
    i+=1
    if i==12:
        octave += 1
        i=0

#-------------------------------------------------------
#----- Chemin vers dossiers/fichiers du programme ------
#-------------------------------------------------------
HOME_PATH = os.path.expanduser("~")
PREF_PATH = os.path.join(HOME_PATH, "Library", "Pyo Synth")
HELP_DOC = os.path.join(PREF_PATH, "manuel_dutilisation_pyosynth.pdf")

REC_PATH = os.path.join(PREF_PATH, "recfiles")
if os.path.exists(REC_PATH):
    for root, dirs, files in os.walk(REC_PATH):
        for file in files:
            path = os.path.join(root,file)
            ctime = os.path.getctime(path)
            delta = time.time()-ctime
            # suppression des fichiers vieux de plus d'une semaine
            if delta > 604800:
                os.remove(path)

EXPORT_PREF_PATH = os.path.join(PREF_PATH, "export_pref.pref")
EXPORT_PREF = {}
if os.path.exists(EXPORT_PREF_PATH):
    with open(EXPORT_PREF_PATH, 'r') as f:
        EXPORT_PREF = pickle.load(f)

RECENT_SCRIPTS_PATH = os.path.join(PREF_PATH, "recent_scripts.log")
RECENT_SCRIPTS = []
if os.path.exists(RECENT_SCRIPTS_PATH):
    with open(RECENT_SCRIPTS_PATH, 'r') as f:
        RECENT_SCRIPTS = pickle.load(f)
# verifie si les fichiers existes encore
to_del = []
for path in RECENT_SCRIPTS:
    if not os.path.exists(path):
        to_del.append(path)
for path in to_del:
    del RECENT_SCRIPTS[RECENT_SCRIPTS.index(path)]
del to_del
REP_FL_LOG = os.path.join(PREF_PATH, "err.log")
f_REP_LOG_ = os.path.join(PREF_PATH, "m8dn3820gn57fjf9")