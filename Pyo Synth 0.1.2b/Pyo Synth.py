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

if sys.platform == 'linux2':
    print 'pyo64'
    from pyo64 import *
else:
    from pyo import *


from resources import __main__

s = Server().boot()
app = wx.App(False)
pyosynth = __main__.PyoSynth(s, locals())
sys.stdout = pyosynth.terminal_win
pyosynth.Show()
app.MainLoop()
