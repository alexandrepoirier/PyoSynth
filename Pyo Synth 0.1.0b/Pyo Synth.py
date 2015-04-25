#!/usr/bin/env python
from pyo import *
import resources, wx, sys
from resources.utils import _repExcMkf

sys.excepthook = _repExcMkf

s = Server().boot()
app = wx.App(False)
pyosynth = resources.PyoSynth(s, locals(), poly=10)
pyosynth.Show()
app.MainLoop()