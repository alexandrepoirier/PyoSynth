#!/usr/bin/env python
# encoding: utf-8

"""
Copyright 2015 Alexandre Poirier

This file is part of Pyo Synth, a python module to help digital signal
processing script creation.

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

import wx, config, sys, traceback, pickle, os, time, interface
from pyo import midiToHz

def getTransparentColour(alpha, *colours):
    """
    Takes colours in hexadecimal notation and converts them
    to r,v,b,a format.
    """
    list = []
    for i in range(len(colours)):
        b = wx.Brush(colours[i])
        r,g,b = b.GetColour().Get()
        list.append((r,g,b,alpha))
    return list
    
def midiRangeToHz(min, max):
    hz = []
    for i in range(min, max+1):
        hz.append(midiToHz(i))
    return hz
    
def createVelocityList(x):
    vel = []
    for i in range(1,x):
        vel.append(127/x*i)
    vel.append(127)
    return vel
    
def shortenText(text, length):
    if len(text) > length:
        newtext = text[:length/2-1]
        newtext += "..."
        newtext += text[-(length-3)/2:]
        return newtext
    else:
        return text
        
def _repExcMkf(type, value, tb):
    config.hide_main_win()
    info = [time.strftime("%H:%M:%S, %d-%m-%Y")]
    info.append(''.join(traceback.format_exception(type,value,tb)))
    code = config.crash_save_func()
    if code == 1:
        msg = u"Ouppss! PyoSynth a planté sans crier gare...\nVous pouvez fournir des informations pour nous aider à régler le problème dans l'espace ci-dessous."
    else:
        msg = u"Ouppss! PyoSynth a planté sans crier gare, mais nous avons été capable de sauvegarder votre projet à l'emplacement suivant : %s\n\nVous pouvez fournir des informations pour nous aider à régler le problème dans l'espace ci-dessous."%code
    dlg = interface.CrashDialog(msg, u'PyoSynth a généré une erreur.')
    dlg.Center()
    dlg.ShowModal()
    info.append(dlg.GetComments())
    dlg.Destroy()
    with open(config.REP_FL_LOG, 'w') as f:
        pickle.dump(info, f)
    sys.exit()