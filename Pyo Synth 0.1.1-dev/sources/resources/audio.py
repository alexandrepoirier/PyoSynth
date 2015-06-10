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
import config
import time
import os.path


class MidiControl:
    """
    class MidiControl
    
    parametres
        - ctlnumber : numero d'identification du controle midi
        - chnl : canal midi sur lequel le signal doit etre recu
        
    Note : La variable _obj contient un objet imbrique de la maniere suivante : Port( Scale( Midictl() ) )
           
           La variable self._param_name doit absolument contenir le nom du parametre auquel est associe
           self._obj avec le nom de la variable concernee en prefixe. Par exemple : sineLFO.mul
    """

    def __init__(self, ctlnumber, chnl):
        self._ctlnumber = ctlnumber
        self._chnl = chnl
        self._minscale = 0
        self._maxscale = 1
        self._exp = False
        self._port = False
        self._int = False
        self._midi_obj = Midictl(ctlnumber, channel=chnl)
        self._scale_obj = Scale(self._midi_obj)
        self._obj = Port(self._scale_obj, risetime=0, falltime=0)
        self._param_name = None

    def reinit(self):
        self._midi_obj = Midictl(self._ctlnumber, channel=self._chnl)
        self._scale_obj = Scale(self._midi_obj)
        self._obj = Port(self._scale_obj, risetime=0, falltime=0)
        self.setExp(self._exp)
        self.setPort(self._port)
        self.setScale(self._minscale, self._maxscale)
        self.setFloor(self._int)

    def get(self, all=False):
        return self._obj.get(all)

    def getCtlNumber(self):
        return self._ctlnumber

    def getMin(self):
        return self._minscale

    def getMax(self):
        return self._maxscale

    def getRange(self):
        return self._maxscale - self._minscale

    def getParamName(self):
        return self._param_name

    def hasExp(self):
        return self._exp

    def hasPort(self):
        return self._port

    def hasFloor(self):
        return self._int

    def setParamName(self, name):
        self._param_name = name

    def setCtlNumber(self, num):
        self._ctlnumber = num
        self._midi_obj.setCtlNumber(num)

    def setScale(self, min, max):
        self._minscale = min
        self._maxscale = max
        self._scale_obj.setOutMin(min)
        self._scale_obj.setOutMax(max)

    def setExp(self, value):
        self._exp = value
        if value:
            self._scale_obj.setExp(2)
        else:
            self._scale_obj.setExp(1)

    def setPort(self, value):
        self._port = value
        if value:
            self._obj.setRiseTime(.05)
            self._obj.setFallTime(.05)
        else:
            self._obj.setRiseTime(0)
            self._obj.setFallTime(0)

    def setFloor(self, value):
        if value != self._int:
            self._int = value
            if value:
                self._obj.setInput(Floor(self._scale_obj))
            else:
                self._obj.setInput(self._scale_obj)

    def unlink(self, namespace):
        if self._param_name is not None:
            string = self._param_name + "= %f" % self._obj.get()
            exec string in namespace
            self._param_name = None

    def pause(self, namespace):
        if self._param_name is not None:
            string = self._param_name + "= %f" % self._obj.get()
            exec string in namespace
        self._obj.stop()

    def resume(self, namespace):
        self._obj.play()
        if self._param_name is not None:
            string = self._param_name + "= self._obj"
            exec string in namespace, locals()


class MidiKeys:
    """
    class MidiKeys
    
    parametres
        env : - en mode 'ctl', les quatres premiers boutons sont assignes aux parametres
                de l'enveloppe. (Attack, Decay, Sustain, Release)
              - en mode 'list', l'enveloppe est determinee au moment de la declaration
                avec une liste.
                
        chnl : canal midi sur lequel le clavier est branche. 0 veut dire tous les canaux.
        
        poly : nombre de notes pouvant etre jouees simultanement.
    """

    def __init__(self, chnl=0, poly=10):
        self.mode = 'normal'
        self.attack = 0.01
        self.decay = 0.05
        self.sustain = 0.7
        self.release = 0.10
        self.velocity_curve = 2
        self._chnl = chnl
        self._poly = poly
        self.notes = Notein(poly=poly, scale=1, channel=chnl)
        self.velocity = Scale(self.notes['velocity'], exp=self.velocity_curve)
        self.bend = Bendin(scale=1, channel=chnl)
        self.amp = MidiAdsr(self.velocity, self.attack, self.decay, self.sustain, self.release)

        # liste contenant tous les controles
        ##le premier est la roulette de modulation
        ##les autres numeros sont arbitraires
        self.ctl_list = [Midictl(1), MidiControl(7, chnl), MidiControl(74, chnl), MidiControl(71, chnl),
                         MidiControl(93, chnl),
                         MidiControl(73, chnl), MidiControl(75, chnl), MidiControl(79, chnl), MidiControl(72, chnl),
                         MidiControl(114, chnl), MidiControl(76, chnl), MidiControl(77, chnl), MidiControl(91, chnl),
                         MidiControl(18, chnl), MidiControl(19, chnl), MidiControl(16, chnl), MidiControl(17, chnl)]

    def reinit(self):
        """
        Reinitializes the midiKeys audio objects in case the server has rebooted (and cleared the audio callback loop).
        """
        if self.mode == 'export':
            del self.noteon
            del self.noteoff

        self.mode = 'normal'
        self.notes = Notein(poly=self._poly, scale=1, channel=self._chnl)
        self.velocity = Scale(self.notes['velocity'], exp=self.velocity_curve)
        self.bend = Bendin(scale=1, channel=self._chnl)
        self.ctl_list[0] = Midictl(1)
        for i in range(1, 17):
            self.ctl_list[i].reinit()

        self.amp = MidiAdsr(self.velocity, self.attack, self.decay, self.sustain, self.release)

    def __getitem__(self, i):
        if i == 'pitch':
            if self.mode == 'normal':
                return self.notes['pitch']
            if self.mode == 'export':
                return self.notes
            if self.mode == 'virtual':
                return self.notes
        if i == 'amp':
            return self.amp
        if i == 'vel':
            if self.mode == 'normal':
                return self.velocity
            if self.mode == 'export':
                return self.velocity
            if self.mode == 'virtual':
                return 0
        if i == 'bend':
            if self.mode == 'normal':
                return self.bend
            else:
                return 1
        if i == 'mod':
            if self.mode == 'normal':
                return self.ctl_list[0]
            else:
                return 0
        if i == 'noteon':
            if self.mode == 'normal':
                return self.notes['trigon']
            if self.mode == 'export':
                return self.noteon
        if i == 'noteoff':
            if self.mode == 'normal':
                return self.notes['trigoff']
            if self.mode == 'export':
                return self.noteoff
        if i == 'c1':
            return self.ctl_list[1]._obj
        if i == 'c2':
            return self.ctl_list[2]._obj
        if i == 'c3':
            return self.ctl_list[3]._obj
        if i == 'c4':
            return self.ctl_list[4]._obj
        if i == 'c5':
            return self.ctl_list[5]._obj
        if i == 'c6':
            return self.ctl_list[6]._obj
        if i == 'c7':
            return self.ctl_list[7]._obj
        if i == 'c8':
            return self.ctl_list[8]._obj
        if i == 'c9':
            return self.ctl_list[9]._obj
        if i == 'c10':
            return self.ctl_list[10]._obj
        if i == 'c11':
            return self.ctl_list[11]._obj
        if i == 'c12':
            return self.ctl_list[12]._obj
        if i == 'c13':
            return self.ctl_list[13]._obj
        if i == 'c14':
            return self.ctl_list[14]._obj
        if i == 'c15':
            return self.ctl_list[15]._obj
        if i == 'c16':
            return self.ctl_list[16]._obj

    def onVirtualKeysNewNote(self, notes, amp):
        self.notes.value = notes
        self.amp.mul = amp

    def onVirtualNoteOn(self, i):
        self.amp[i].play()

    def onVirtualNoteOff(self, i):
        self.amp[i].stop()

    def setEnv(self, list):
        self.attack, self.decay, self.sustain, self.release = list
        self.amp.setAttack(self.attack)
        self.amp.setDecay(self.decay)
        self.amp.setSustain(self.sustain)
        self.amp.setRelease(self.release)

    def setScale(self, ctl, min, max):
        self.ctl_list[ctl].setScale(min, max)

    def setExp(self, ctl, value):
        self.ctl_list[ctl].setExp(value)

    def setPort(self, ctl, value):
        self.ctl_list[ctl].setPort(value)

    def setFloor(self, ctl, value):
        self.ctl_list[ctl].setFloor(value)

    def setAttack(self, value):
        self.attack = value
        self.amp.setAttack(value)

    def setDecay(self, value):
        self.decay = value
        self.amp.setDecay(value)

    def setSustain(self, value):
        self.sustain = value
        self.amp.setSustain(value)

    def setRelease(self, value):
        self.release = value
        self.amp.setRelease(value)

    def setVelocityCurve(self, value):
        self.velocity_curve = value
        self.velocity.setExp(value)

    def setVelocityValue(self, value):
        if self.mode == "export":
            self.velocity._input.value = value

    def setVirtualKeyboard(self, keys_obj):
        self.mode = 'virtual'
        keys_obj.setPoly(self._poly)
        keys_obj.setCallback(self.onVirtualKeysNewNote)
        self.notes = Sig([0 for i in range(self._poly)])
        self.amp = Adsr(self.attack, self.decay, self.sustain, self.release, 0, [i for i in range(self._poly)])
        self.trigFuncOn = TrigFunc(keys_obj['noteon'], self.onVirtualNoteOn, [i for i in range(self._poly)])
        self.trigFuncOff = TrigFunc(keys_obj['noteoff'], self.onVirtualNoteOff, [i for i in range(self._poly)])

    def prepareForExport(self, dur):
        self.mode = 'export'
        self.velocity = Scale(Sig(1), exp=self.velocity_curve)
        self.notes = Sig(1)
        self.noteon = Trig().stop()
        self.amp = Adsr(self.attack, self.decay, self.sustain, self.release, dur, mul=self.velocity)
        self.noteoff = Thresh(self.amp, 0.001, 1)

    def playNote(self):
        self.noteon.play()
        self.amp.play()

    def getAdsrCallbacks(self):
        return self.setAttack, self.setDecay, self.setSustain, self.setRelease

    def getPolyphony(self):
        return self._poly

    def getNotes(self):
        return self.notes['pitch'].get(True)

    def getMin(self, ctl):
        return self.ctl_list[ctl].getMin()

    def getMax(self, ctl):
        return self.ctl_list[ctl].getMax()

    def getExp(self, ctl):
        return self.ctl_list[ctl].hasExp()

    def getPort(self, ctl):
        return self.ctl_list[ctl].hasPort()

    def getFloor(self, ctl):
        return self.ctl_list[ctl].hasFloor()

    def getAdsrValues(self):
        return self.attack, self.decay, self.sustain, self.release

    def getAttack(self):
        return self.attack

    def getDecay(self):
        return self.decay

    def getSustain(self):
        return self.sustain

    def getRelease(self):
        return self.release

    def getValue(self, ctl):
        return self.ctl_list[ctl].get()

    def getParamName(self, ctl):
        return self.ctl_list[ctl].getParamName()

    def getIndexFromCtlNumber(self, num):
        for i in range(1, len(self.ctl_list)):
            if self.ctl_list[i].getCtlNumber() == num:
                return i


class TrackRecorder:
    def __init__(self):
        # sera cree a chaque enregistrement
        self._recObj = None
        # contiendra le chemin vers le dernier fichier enregistre
        self._path = None
        # garde en memoire le nombre de piste enregitree
        self.__trackCount__ = 0

    def record(self, obj, chnls):
        self.__trackCount__ += 1
        self._path = self._makeNewPath()
        self._recObj = Record(obj, self._path, chnls, sampletype=config.REC_BIT_DEPTH)
        return self._path, self.__trackCount__

    def stop(self):
        self._recObj.stop()

    def _makeNewPath(self):
        date = time.strftime("%d-%m-%y")
        name = date + "_%d%s" % (self.__trackCount__, config.REC_FORMAT_DICT[config.REC_FORMAT])
        return os.path.join(config.REC_PATH, name)


class Click:
    def __init__(self, tempo, nchnls, mul=1):
        self.freq = 900
        self.mul = mul
        self.time = 60. / tempo
        self.metro = Metro(self.time).play()
        self.adsr = LinTable([(0, 0), (100, 1), (1000, .25), (8191, 0)])
        self.env = TrigEnv(self.metro, table=self.adsr, dur=.125, mul=self.mul)
        if nchnls == 1:
            self.sine = Sine(freq=self.freq, mul=self.env)
        else:
            self.sine = Sine(freq=[self.freq, self.freq], mul=self.env)

    def __getitem__(self, i):
        if i == 'click':
            return self.metro

    def reinit(self, nchnls):
        self.metro = Metro(self.time).stop()
        self.adsr = LinTable([(0, 0), (100, 1), (1000, .25), (8191, 0)])
        self.env = TrigEnv(self.metro, table=self.adsr, dur=.125, mul=self.mul)
        if nchnls == 1:
            self.sine = Sine(freq=self.freq, mul=self.env)
        else:
            self.sine = Sine(freq=[self.freq, self.freq], mul=self.env)

    def out(self):
        self.play()
        self.sine.out()
        return self

    def mute(self):
        self.env.stop()
        self.sine.stop()

    def play(self):
        self.metro.play()
        self.env.play()
        self.sine.play()
        return self

    def stop(self):
        self.mute()
        self.metro.stop()
        return self

    def setTempo(self, tempo):
        self.time = 60. / tempo
        self.metro.time = self.time

    def setMul(self, mul):
        self.mul = mul
        self.env.mul = mul


class ClipMonitor:
    """
    :type: clipval: float between 0 and 1
           callback: python function
           reset_time: integer, time in milliseconds
    """
    def __init__(self, clipval, callback, reset_time):
        self.callback = callback
        self.clip_val = clipval
        self.reset_time = reset_time / 1000.
        self.timer = None
        self.thresh = Thresh(Sig(0), threshold=self.clip_val).stop()
        self.trigCallback = TrigFunc(self.thresh, self.onClip).stop()

    def reinit(self):
        self.thresh = Thresh(Sig(0), threshold=self.clip_val).stop()
        self.trigCallback = TrigFunc(self.thresh, self.onClip).stop()

    def start(self):
        self.thresh.play()
        self.trigCallback.play()
        return self

    def stop(self):
        self.trigCallback.stop()
        self.thresh.stop()

    def onClip(self):
        self.stop()
        self.callback()
        self.timer = CallAfter(self.start, self.reset_time)

    def setInput(self, input):
        if len(input) > 1:
            self.thresh.input = input.mix(1)
        else:
            self.thresh.input = input
