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

import wx
import PSConfig
import sys
import subprocess
import traceback
import pickle
import time
import PSInterface
import math
import os.path

if PSConfig.USE_PYO64:
    from pyo64 import midiToHz, pa_get_default_output, pa_get_default_input, pm_get_default_output, pm_get_default_input
    from pyo64 import pa_get_output_devices, pa_get_input_devices, pm_get_output_devices, pm_get_input_devices
else:
    from pyo import midiToHz, pa_get_default_output, pa_get_default_input, pm_get_default_output, pm_get_default_input
    from pyo import pa_get_output_devices, pa_get_input_devices, pm_get_output_devices, pm_get_input_devices


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
        
def checkExtension(path, ext):
    if path.rfind('.') == -1:
        return path+'.'+ext
    else:
        name, p_ext = path.rsplit('.',1)
        if p_ext != ext:
            return name+'.'+ext
        else:
            return path
            
def _repExcMkf(type, value, tb):
    PSConfig.hide_main_win()
    info = [time.strftime("%H:%M:%S, %d-%m-%Y"), PSConfig.VERSIONS['Pyo Synth']]
    info.append(''.join(traceback.format_exception(type,value,tb)))
    code = PSConfig.crash_save_func()
    if code == 1:
        msg = u"Ouppss! PyoSynth a planté sans crier gare...\nVous pouvez fournir des informations pour nous aider à régler le problème dans l'espace ci-dessous."
    else:
        msg = u"Ouppss! PyoSynth a planté sans crier gare, mais nous avons été capable de sauvegarder votre projet à l'emplacement suivant : %s\n\nVous pouvez fournir des informations pour nous aider à régler le problème dans l'espace ci-dessous."%code
    dlg = PSInterface.CrashDialog(msg, u'PyoSynth a généré une erreur.')
    dlg.Center()
    dlg.ShowModal()
    info.append(dlg.GetComments())
    dlg.Destroy()
    with open(PSConfig.REP_FL_LOG, 'w') as f:
        pickle.dump(info, f)
    openSysFileBrowser(PSConfig.REP_FL_LOG) # to remove before release
    sys.exit()

def ampTodB(x, prec):
    if x <= 0.000001:
        return -120.0
    return round(20 * math.log10(x), prec)

def dBToAmp(x, prec):
    return round(math.pow(10, x / 20.), prec)

def openSysFileBrowser(path):
    assert isinstance(path, str) or isinstance(path, unicode), "openSysFilBrowser(string): path expected as argument"
    if sys.platform == 'win32':
        subprocess.Popen(r'explorer /select,%s' % path)
    elif sys.platform == 'darwin':
        subprocess.call(["open", "-R", path])
    elif sys.platform == 'linux2':
        subprocess.call(['gnome-open', path])

def printMessage(text, level=0):
    if level <= PSConfig.VERBOSE_LVL:
        tclock = "%.2f" % (time.clock()%1)
        print "[%s.%s][%s] %s" % (time.strftime("%H:%M:%S"), tclock.split('.')[1], PSConfig.VERBOSE_KW_LVL[level], text)
    else:
        return

def clipper(value, min, max):
    if value>max:return max
    if value<min:return min
    return value

def getTimeFromSeconds(value):
    seconds = value % 60
    minutes = (value-seconds) / 60
    hours = minutes / 60
    minutes = minutes % 60
    return (hours, minutes, seconds)

def getServerPreferences():
    """
    Tries to open pref file on HD, otherwise sets server to default settings.
    Done once upon startup. If preferences values aren't valid anymore, the default settings are restored.
    """
    try:
        f = open(os.path.join(PSConfig.PREF_PATH, "server_setup.pref"), 'r')
        HAS_PREFS = True
    except IOError, e:
        HAS_PREFS = False
        return (HAS_PREFS,
                {'sr': 44100, 'nchnls': 2, 'bfs': 256, 'duplex': 1, 'audio': 'portaudio',
                'output': pa_get_default_output(),
                'input': pa_get_default_input(),
                'midi_output': pm_get_default_output(),
                'midi_input': pm_get_default_input()})
    else:
        pref = pickle.load(f)
        f.close()
        # verify if input/output interfaces are there
        if pref['output'] not in pa_get_output_devices()[1]:
            pref['output'] = pa_get_default_output()
        if pref['input'] not in pa_get_input_devices()[1]:
            pref['input'] = pa_get_default_input()
        if pref['midi_output'] not in pm_get_output_devices()[1]:
            pref['midi_output'] = pm_get_default_output()
        if pref['midi_input'] not in pm_get_input_devices()[1]:
            pref['midi_input'] = pm_get_default_input()
        return (HAS_PREFS, pref)