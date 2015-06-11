#!/usr/bin/env python

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

from pyo import *
import resources
import wx
import sys
from resources.utils import _repExcMkf
from resources.config import POLYPHONY

sys.excepthook = _repExcMkf

s = Server().boot()
app = wx.App(False)
pyosynth = resources.PyoSynth(s, locals(), poly=POLYPHONY)
pyosynth.Show()
app.MainLoop()