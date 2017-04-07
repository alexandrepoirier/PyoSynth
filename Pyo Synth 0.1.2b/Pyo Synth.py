#!/usr/bin/env python

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

import wx
import sys
import resources.extra as extra
from resources.PSUtils import getServerPreferences
from resources.PSConfig import USE_PYO64

if USE_PYO64:
    from pyo64 import *
else:
    from pyo import *

from resources import main


prefs = getServerPreferences()[1]
s = Server(sr=prefs['sr'], buffersize=prefs['bfs'], nchnls=prefs['nchnls'],
           duplex=prefs['duplex'], audio=prefs['audio'], jackname='Pyo Synth')
s.setInputDevice(prefs['input'])
s.setOutputDevice(prefs['output'])
s.setMidiInputDevice(prefs['midi_input'])
s.setMidiOutputDevice(prefs['midi_output'])
s.boot()
app = wx.App(False)
pyosynth = main.PyoSynth(s, locals())
sys.stdout = pyosynth.terminal_win
pyosynth.Show()
app.MainLoop()
