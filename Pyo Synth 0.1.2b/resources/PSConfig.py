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
import sys
import pickle
import time
import wx

#--------------------------------------------
#--------------- Constantes -----------------
#--------------------------------------------
VERSIONS = {'Pyo Synth':"0.1.2b", 'pyo':(0,8,4), 'python':(2,7,13)}
PLATFORM = sys.platform
crash_save_func = None
hide_main_win = None
UNIT_SIZE = (130,110)
WHEELS_BOX_WIDTH = 100
NB_ELEM_ROW = 8

if PLATFORM == 'linux2':
    Y_OFFSET = 3
    X_OFFSET = 1
    BANNER_OFFSET = 43
    USE_TRANSPARENCY = False
elif PLATFORM == 'win32':
    Y_OFFSET = 0
    X_OFFSET = 0
    BANNER_OFFSET = 0
    USE_TRANSPARENCY = False
elif PLATFORM == 'darwin':
    Y_OFFSET = 0
    X_OFFSET = 0
    BANNER_OFFSET = 0
    USE_TRANSPARENCY = True

REFRESH_RATE = 1./13
BG_COLOUR = "#333333"
STATS_BAR_HGT = 49
SETUP_PANEL_HGT = 61
TAB_WIN_HGT = 300
MAX_RECENT_SCRIPTS = 10
DEFAULT_POLYPHONY = 10
POLYPHONY_VALUES = [5,10,20,30,40]
DEFAULT_PBEND_RANGE = 2
PITCH_BEND_VALUES = [0.5,1,2,3,4,5,6,7,7.5,8,9,10,11,12,24]

REC_FORMAT_DICT = {0:".wav",1:".aif",2:".au",3:"",4:".sd2",5:".flac",6:".caf",7:".ogg"}
REC_FORMAT = 0
REC_BIT_DEPTH = 1
REC_MAX_TIME = 300 # in seconds

PATCH_BANNER = "#------------------------PATCH------------------------#"
PRESET_BANNER = "#------------------------PRESET------------------------#"

VERBOSE_LVL = 1
VERBOSE_KW_LVL = {0:"INFO", 1:"DEBUG"}

# defines different mapping solutions for the computer keyboard
# first number is the approximate span of the keyboard mapping in octaves (rounded up)
# note : in the future, the user should be able to define his own
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

# -------------------------------------------------------
# --------------- wx.Font pout le projet ----------------
# -------------------------------------------------------
if PLATFORM == 'darwin':
    x = 0
    monofont = 'Monaco'
elif PLATFORM == "linux2":
    x = 2
    monofont = 'Consolas'
elif PLATFORM == 'win32':
    x = 2
    monofont = 'Consolas'

FONTS = {'light':{'xsmall':{'pointSize':10-x, 'family':wx.FONTFAMILY_SWISS,
                            'style':wx.FONTSTYLE_NORMAL, 'weight':wx.FONTWEIGHT_LIGHT, 'face':"Helvetica"},
                  'small':{'pointSize':11-x, 'family':wx.FONTFAMILY_SWISS,
                            'style':wx.FONTSTYLE_NORMAL, 'weight':wx.FONTWEIGHT_LIGHT, 'face':"Helvetica"},
                  'norm':{'pointSize':12-x, 'family':wx.FONTFAMILY_SWISS,
                            'style':wx.FONTSTYLE_NORMAL, 'weight':wx.FONTWEIGHT_LIGHT, 'face':"Helvetica"},
                  'med':{'pointSize':13-x, 'family':wx.FONTFAMILY_SWISS,
                            'style':wx.FONTSTYLE_NORMAL, 'weight':wx.FONTWEIGHT_LIGHT, 'face':"Helvetica"},
                  'large':{'pointSize':14-x, 'family':wx.FONTFAMILY_SWISS,
                            'style':wx.FONTSTYLE_NORMAL, 'weight':wx.FONTWEIGHT_LIGHT, 'face':"Helvetica"},
                  'title1':{'pointSize':16-x, 'family':wx.FONTFAMILY_SWISS,
                            'style':wx.FONTSTYLE_NORMAL, 'weight':wx.FONTWEIGHT_LIGHT, 'face':"Helvetica"},
                  'title2':{'pointSize':17-x, 'family':wx.FONTFAMILY_SWISS,
                            'style':wx.FONTSTYLE_NORMAL, 'weight':wx.FONTWEIGHT_LIGHT, 'face':"Helvetica"}},
         'bold':{'xsmall':{'pointSize':10-x, 'family':wx.FONTFAMILY_MODERN,
                           'style':wx.FONTSTYLE_NORMAL, 'weight':wx.FONTWEIGHT_BOLD},
                  'norm':{'pointSize':12-x, 'family':wx.FONTFAMILY_MODERN,
                          'style':wx.FONTSTYLE_NORMAL, 'weight':wx.FONTWEIGHT_BOLD},
                  'large':{'pointSize':14-x, 'family':wx.FONTFAMILY_MODERN,
                           'style':wx.FONTSTYLE_NORMAL, 'weight':wx.FONTWEIGHT_BOLD},
                  'title1':{'pointSize':16-x, 'family':wx.FONTFAMILY_MODERN,
                            'style':wx.FONTSTYLE_NORMAL, 'weight':wx.FONTWEIGHT_BOLD},
                  'large_title':{'pointSize':23-x, 'family':wx.FONTFAMILY_MODERN,
                                 'style':wx.FONTSTYLE_NORMAL, 'weight':wx.FONTWEIGHT_BOLD},
                  'xl_title':{'pointSize':25-x, 'family':wx.FONTFAMILY_MODERN,
                              'style':wx.FONTSTYLE_NORMAL, 'weight':wx.FONTWEIGHT_BOLD}},
         'terminal':{'pointSize':11-x, 'family':wx.FONTFAMILY_MODERN, 'style':wx.FONTSTYLE_NORMAL,
                     'weight':wx.FONTWEIGHT_NORMAL, 'face':monofont}
         }

#-------------------------------------------------------
#----- Chemin vers dossiers/fichiers du programme ------
#-------------------------------------------------------
HOME_PATH = os.path.expanduser("~")

if PLATFORM == "darwin":
    PREF_PATH = os.path.join(HOME_PATH, "Library", "Pyo Synth")
elif PLATFORM == "linux2":
    PREF_PATH = os.path.join(HOME_PATH, ".PyoSynth")
else:
    print "PyoSynth doesn't run yet on Windows!"
    sys.exit()

REC_PATH = os.path.join(PREF_PATH, "recfiles")
HELP_DOC = os.path.join(PREF_PATH, "manuel_dutilisation_pyosynth.pdf")
EXP_PATH = os.path.join(HOME_PATH, 'Documents', 'Pyo Synth Examples')
LAST_DIR = None

if not os.path.exists(PREF_PATH):
    os.mkdir(PREF_PATH)
if not os.path.exists(REC_PATH):
    os.mkdir(REC_PATH)
if not os.path.exists(EXP_PATH):
    os.mkdir(EXP_PATH)
if not os.path.exists(os.path.join(EXP_PATH, 'Examples')):
    os.mkdir(os.path.join(EXP_PATH, 'Examples'))
if not os.path.exists(os.path.join(EXP_PATH, 'Tutorials')):
    os.mkdir(os.path.join(EXP_PATH, 'Tutorials'))

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
    if len(RECENT_SCRIPTS) > 0:
        LAST_DIR = os.path.split(RECENT_SCRIPTS[0])[0]
# verifie si les fichiers existes encore
to_del = []
for path in RECENT_SCRIPTS:
    if not os.path.exists(path):
        to_del.append(path)
for path in to_del:
    del RECENT_SCRIPTS[RECENT_SCRIPTS.index(path)]
del to_del

REP_FL_LOG = os.path.join(PREF_PATH, "err.log")
f_REP_N = "m8dn3820gn57fjf9"
f_REP_LOG_ = os.path.join(PREF_PATH, f_REP_N)

MAX_SAVE_PROFILES = 5
midi_profiles = []
last_used_midi_profile = -1
MIDI_PROFILES_PATH = os.path.join(PREF_PATH, "midi_profiles.pref")
if os.path.exists(MIDI_PROFILES_PATH):
    with open(MIDI_PROFILES_PATH, 'r') as f:
        midi_profiles = pickle.load(f)
    last_used_midi_profile = midi_profiles.pop(-1)

PYOSYNTH_PREF_PATH = os.path.join(PREF_PATH, "pyosynth.pref")
if os.path.exists(PYOSYNTH_PREF_PATH):
    with open(PYOSYNTH_PREF_PATH, 'r') as f:
        PYOSYNTH_PREF = pickle.load(f)
else:
    PYOSYNTH_PREF = {'poly': DEFAULT_POLYPHONY,
                     'bend_range': DEFAULT_PBEND_RANGE,
                     'mono_type': 0,
                     'num_ctls': 16}

BUILD_DATE = ""
if os.path.exists(os.path.join(PREF_PATH, 'app.info')):
    with open(os.path.join(PREF_PATH, 'app.info')) as f:
        app_info = pickle.load(f)
    BUILD_DATE = app_info['build_date']