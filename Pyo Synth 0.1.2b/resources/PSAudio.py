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

import PSConfig
import time
import os.path
import extra

if PSConfig.PLATFORM == 'linux2':
    from pyo64 import *
else:
    from pyo import *


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
        self._hijack = False
        self._hijack_obj = Sig(0)
        self._midi_obj = Midictl(ctlnumber, channel=chnl)
        self._scale_obj = Scale(self._midi_obj)
        self._obj = Port(self._scale_obj, risetime=0, falltime=0)
        self._param_name = None
        self._last_param_name = None

    def reinit(self):
        self._hijack_obj = Sig(0)
        self._midi_obj = Midictl(self._ctlnumber, channel=self._chnl)
        self._scale_obj = Scale(self._midi_obj)
        self._obj = Port(self._scale_obj, risetime=0, falltime=0)
        self.setExp(self._exp)
        self.setPort(self._port)
        self.setScale(self._minscale, self._maxscale)
        self.setFloor(self._int)
        self.setHijack(self._hijack)

    def reset(self, namespace):
        """
        Resets all parameters to default values.
        """
        self.unlink(namespace)
        self.setScale(0, 1)
        self.setExp(False)
        self.setPort(False)
        self.setFloor(False)
        self._param_name = None
        self._last_param_name = None

    def dump(self):
        """
        Prints all info on the object.
        """
        dict = {'ctl number':self._ctlnumber, 'channel':self._chnl,
                'min':self._minscale, 'max':self._maxscale,
                'exponential curve':self._exp, 'portamento':self._port,
                'integers only':self._int, 'hijacked':self._hijack,
                'param name':self._param_name, 'previous param':self._last_param_name}
        print dict

    def get(self):
        return self._obj.get()

    def getNormValueMidi(self):
        return self._midi_obj.get()

    def getNormValueHijack(self):
        return self._hijack_obj.get()

    def getNormValue(self):
        """
        Get current normalized value (0 >= value <= 1).
        """
        if self._hijack:
            return self._hijack_obj.get()
        else:
            return self._midi_obj.get()

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
        self._last_param_name = self._param_name

    def setCtlNumber(self, num):
        self._ctlnumber = num
        self._midi_obj.setCtlNumber(num)

    def setScale(self, min, max):
        self._minscale = min
        self._scale_obj.setOutMin(min)
        self._maxscale = max
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
        self._int = value
        if value:
            self._obj.setInput(Floor(self._scale_obj))
        else:
            self._obj.setInput(self._scale_obj)

    def setHijack(self, state):
        if state:
            self._scale_obj.input = self._hijack_obj
        else:
            self._scale_obj.input = self._midi_obj
        self._hijack = state

    def setHijackValue(self, value):
        if value > 1:
            self._hijack_obj.setValue(1)
        elif value < 0:
            self._hijack_obj.setValue(0)
        else:
            self._hijack_obj.setValue(value)

    def unlink(self, namespace):
        if self._param_name is not None:
            self._last_param_name = self._param_name
            string = self._param_name + "= %f" % self._obj.get()
            exec string in namespace
            self._param_name = None

    def relink(self, namespace):
        """
        Will attempt to relink the control to its last parameter.
        Returns 1 in case the parameter does not exist anymore, otherwise returns 0.
        """
        if self._last_param_name is not None:
            try:
                string = self._last_param_name + "= self._obj"
                exec string in namespace, locals()
            except Exception:
                raise NameError, "Warning : Couldn't link ParamBox to parameter %s."%self._last_param_name
            else:
                self._param_name = self._last_param_name

    def pause(self, namespace):
        if self._param_name is not None:
            string = self._param_name + "= %f" % self._obj.get()
            exec string in namespace
        self._obj.stop()

    def resume(self, namespace):
        self._obj.play()
        if self._param_name is not None:
            string = self._param_name + "= self._obj"
            exec string in namespace, globals()


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

        keyboard_mode : mode du clavier midi. 0 = Normal, 1 = Normal + Sustain, 2 = Mono
    """

    def __init__(self, num_ctls=16, chnl=0, poly=10, keyboard_mode=0, portamento=0.05, mono_mode=0):
        self._IS_DIRTY = False
        # mode: 0=normal, 1=virtual, 2=export
        self.mode = 0
        self.attack = 0.01
        self.decay = 0.05
        self.sustain = 0.7
        self.release = 0.10
        self.velocity_curve = 2
        self.num_ctls = num_ctls
        self._get_item_ctl = ['c%d'%i for i in range(1,num_ctls+1)]
        self._chnl = chnl
        self._poly = poly
        self._mono_port = portamento
        self._bend_range = 2.
        self.keyboard_mode = keyboard_mode
        self.mono_mode = mono_mode
        self._virtual_keys_obj = None

        if self.keyboard_mode == 0:
            self.notes = Notein(poly=self._poly, scale=1, channel=self._chnl)
        elif self.keyboard_mode == 1:
            self.notes = extra.NoteinSustain(poly=self._poly, scale=1, channel=self._chnl)
        elif self.keyboard_mode == 2:
            self.release = self._mono_port
            self.notes = extra.MonoNotein(mode=self.mono_mode, portamento=self._mono_port,  maxHoldNotes=self._poly, channel=self._chnl)

        self.velocity = Scale(self.notes['velocity'], exp=self.velocity_curve)
        self.bend = Bendin(brange=self._bend_range, scale=1, channel=chnl)
        self.amp = MidiAdsr(self.velocity, self.attack, self.decay, self.sustain, self.release)

        if self.keyboard_mode == 1:
            self.detectRelease = Thresh(self.amp, threshold=0.001, dir=1)
            self.trigFreeVoice = TrigFunc(self.detectRelease, self.notes.freeVoice, [i for i in range(self._poly)])

        # liste contenant tous les controles
        # le premier est la roulette de modulation
        self.ctl_list = [Midictl(1)]
        for i in range(num_ctls):
            self.ctl_list.append(MidiControl(7, chnl=chnl))

    def reinit(self):
        """
        Reinitializes the midiKeys audio objects in case the server has rebooted (and cleared the audio callback loop).
        """
        if self.mode == 0:
            self._doReinitNormal()
        elif self.mode == 1:
            self._doReinitVirtual()
        # reinit the dirty flag
        self._IS_DIRTY = False

    def _doReinitNormal(self):
        if self.keyboard_mode == 0: # normal
            self.notes = Notein(poly=self._poly, scale=1, channel=self._chnl)
        elif self.keyboard_mode == 1: # normal with sustain
            self.notes = extra.NoteinSustain(poly=self._poly, scale=1, channel=self._chnl)
        elif self.keyboard_mode == 2: # mono
            self.notes = extra.MonoNotein(mode=self.mono_mode, portamento=self._mono_port,  maxHoldNotes=self._poly, channel=self._chnl)
        self.velocity = Scale(self.notes['velocity'], exp=self.velocity_curve)
        self.bend = Bendin(brange=self._bend_range, scale=1, channel=self._chnl)
        self.amp = MidiAdsr(self.velocity, self.attack, self.decay, self.sustain, self.release)
        if self.keyboard_mode == 1:
            self.detectRelease = Thresh(self.amp, threshold=0.001, dir=1)
            self.trigFreeVoice = TrigFunc(self.detectRelease, self.notes.freeVoice, [i for i in range(self._poly)])
        self._doReinitControls()

    def _doReinitVirtual(self):
        if self.keyboard_mode == 2:
            voices = 1
            self._virtual_keys_obj.setMonoMode(True, self.mono_mode)
            self.notes = SigTo(0, self._mono_port)
        else:
            voices = self._poly
            self._virtual_keys_obj.setMonoMode(False)
            self.notes = Sig([0 for i in range(voices)])
        self._virtual_keys_obj.setPoly(self._poly)
        self._virtual_keys_obj.setCallback(self.onVirtualKeysNewNote)
        self.amp = Adsr(self.attack, self.decay, self.sustain, self.release, 0, [i for i in range(voices)])
        if self.keyboard_mode != 2:
            self.detectRelease = Thresh(self.amp, threshold=0.001, dir=1)
            self.trigFreeVoice = TrigFunc(self.detectRelease, self._virtual_keys_obj.freeVoice, [i for i in range(voices)])
        self.trigFuncOn = TrigFunc(self._virtual_keys_obj['noteon'], self.onVirtualNoteOn, [i for i in range(voices)])
        self.trigFuncOff = TrigFunc(self._virtual_keys_obj['noteoff'], self.onVirtualNoteOff, [i for i in range(voices)])
        self._doReinitControls()

    def _doReinitControls(self):
        self.ctl_list[0] = Midictl(1)
        for i in range(1, self.num_ctls+1):
            self.ctl_list[i].reinit()

    def __getitem__(self, i):
        if i == 'pitch':
            if self.mode == 0:
                return self.notes['pitch']
            if self.mode == 2:
                return self.notes
            if self.mode == 1:
                return self.notes
        if i == 'amp':
            return self.amp
        if i == 'vel':
            if self.mode == 0:
                return self.velocity
            if self.mode == 2:
                return self.velocity
            if self.mode == 1:
                raise Exception('Cannot use velocity stream with virtual keyboard.')
        if i == 'bend':
            if self.mode == 0:
                return self.bend
            else:
                return 1
        if i == 'mod':
            if self.mode == 0:
                return self.ctl_list[0]
            else:
                return 0
        if i == 'noteon':
            if self.mode == 0:
                return self.notes['trigon']
            if self.mode == 2:
                return self.noteon
            if self.mode == 1:
                return self._virtual_keys_obj['noteon']
        if i == 'noteoff':
            if self.mode == 0:
                return self.notes['trigoff']
            if self.mode == 2:
                return self.noteoff
            if self.mode == 1:
                return self._virtual_keys_obj['noteoff']
        if i == 'freevoice':
            if self.mode == 0:
                if self.keyboard_mode == 1:
                    return self.trigFreeVoice
                else:
                    return self.notes['trigoff']
            if self.mode == 1:
                if self.keyboard_mode < 2:
                    return self.trigFreeVoice
                else:
                    return self._virtual_keys_obj['noteoff']
            if self.mode == 2:
                raise Exception('Cannot use freevoice stream during export.')
        if i in self._get_item_ctl:
            return self.ctl_list[int(i[1:])]._obj
        raise KeyError, "MidiKeys Error: '%s' is not a valid stream"%i

    def _getitem_dict(self):
        """
        Builds a dictionary of all the elements that can be retrieved using the __getitem__ method and returns it.
        """
        dict = {}
        for elem in self._get_item_ctl:
            dict[elem] = self[elem]
        dict.update({'pitch': self['pitch'],
                     'amp': self['amp'],
                     'bend': self['bend'],
                     'mod': self['mod'],
                     'noteon': self['noteon'],
                     'noteoff': self['noteoff'],
                     'freevoice': self['freevoice']})
        if self.mode == 0:
            dict.update({'vel': self['vel']})
        return dict

    # -------------------------
    # Setters
    # -------------------------
    def setPoly(self, poly):
        self._IS_DIRTY = True
        self._poly = poly

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
        self._mono_port = value
        self.release = value
        self.amp.setRelease(value)
        if self.keyboard_mode == 2:
            if self._virtual_keys_obj is None:
                self.notes.setPort(value)
            else:
                self.notes.setTime(value)

    def setBendRange(self, value):
        self._bend_range = value
        self.bend.setBrange(value)

    def setVelocityCurve(self, value):
        self.velocity_curve = value
        self.velocity.setExp(value)

    def setKeyboardMode(self, mode):
        assert mode in (0, 1, 2), "Mode argument must be 0, 1 or 2. (Normal, Normal + Sustain or Mono)"
        self.keyboard_mode = mode
        self._IS_DIRTY = True

    def setMonoType(self, type):
        assert type in (0, 1, 2), "Mono 'type' attribute should be either 0, 1 or 2. (Recent, Low or High priority)"
        self.mono_mode = type
        if self.keyboard_mode == 2:
            if self._virtual_keys_obj is not None:
                self._virtual_keys_obj.setMonoType(type)
            else:
                self.notes.setMonoType(type)

    # -------------------------
    # Getters
    # -------------------------
    def getAdsrCallbacks(self):
        return self.setAttack, self.setDecay, self.setSustain, self.setRelease

    def getPolyphony(self):
        if self.mode == 2:
            return 1
        elif self.keyboard_mode == 2:  # mono mode
            return 1
        return self._poly

    def getTotalVoicesPlaying(self):
        if self.mode == 2:
            return 1
        if self.keyboard_mode < 2:
            return self._poly - self.amp.get(True).count(0.)
        else:
            return 1 - self.amp.get(True).count(0.)

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

    def getBendRange(self):
        return self._bend_range

    def getValue(self, ctl):
        return self.ctl_list[ctl].get()

    def getNormValue(self, ctl):
        return self.ctl_list[ctl].getNormValue()

    def getParamName(self, ctl):
        return self.ctl_list[ctl].getParamName()

    def getIndexFromCtlNumber(self, num):
        try:
            return [self.ctl_list[i].getCtlNumber() for i in self.num_ctls].index(num)
        except:
            return -1

    def getKeyboardMode(self):
        return self.keyboard_mode

    def getMonoType(self):
        return self.mono_mode

    def isDirty(self):
        return self._IS_DIRTY

    # -------------------------
    # Methods for script export
    # -------------------------
    def prepareForExport(self, dur):
        self._mode_bf_export = self.mode
        self.mode = 2
        self.velocity = Scale(Sig(1), exp=self.velocity_curve)
        self.notes = Sig(1)
        self.noteon = Trig().stop()
        self.amp = Adsr(self.attack, self.decay, self.sustain, self.release, dur, mul=self.velocity)
        self.noteoff = Thresh(self.amp, 0.001, 1)

    def cleanAfterExport(self):
        self._IS_DIRTY = True
        self.mode = self._mode_bf_export
        del self.noteon
        del self.noteoff
        del self._mode_bf_export

    def playNote(self):
        self.noteon.play()
        self.amp.play()

    def setVelocityValue(self, value):
        if self.mode == 2:
            self.velocity._input.value = value

    # ----------------------------
    # Methods for virtual keyboard
    # ----------------------------
    def onVirtualKeysNewNote(self, note, amp, i=0):
        # Called at every key press (this is the callback for VirtualKeyboard class)
        self.notes[i].value = note
        self.amp[i].mul = amp

    def onVirtualNoteOn(self, i=0):
        # Called by trigfunc when VirtualKeyboard sends a trigger
        self.amp[i].play()

    def onVirtualNoteOff(self, i=0):
        # Called by trigfunc when VirtualKeyboard sends a trigger
        self.amp[i].stop()

    def setVirtualKeyboardMode(self, keys_obj):
        self.mode = 1
        self._virtual_keys_obj = keys_obj
        self._IS_DIRTY = True

    def disableVirtualKeyboardMode(self):
        self.mode = 0
        self._virtual_keys_obj = None
        del self.trigFuncOff
        del self.trigFuncOn
        self._IS_DIRTY = True


class SoundRecorder2:
    def __init__(self, obj, path, chnls):
        # instance variables
        self._chnls = chnls
        self._path = path
        self._table_dur = 10.0 # min 5 sec.
        self._getSampleLimit = lambda x: x*self._table_dur-x
        self._table_count_index = -1
        self._table_list = []
        self._IS_SAVING = False

        # pyo objects
        self._prepareNextTable()
        self._rec_obj = TableRec(obj, self._table_list[self._table_count_index])
        self._sample_clock = Thresh(self._rec_obj['time'], self._getSampleLimit(self._rec_obj.getSamplingRate()))
        self._prep_trigf = TrigFunc(self._sample_clock, self._prepareNextTable)
        self._tswitch_trig = TrigFunc(self._rec_obj['trig'], self._switchNextTable)

    def __del__(self):
        if self._rec_obj.isPlaying():
            self.stop()
        if self._IS_SAVING:
            Clean_objects(5, self)
        self._sample_clock.stop()
        self._prep_trigf.stop()
        self._tswitch_trig.stop()

    def record(self):
        self._rec_obj.play()
        return self

    def stop(self):
        cur_pos = self._rec_obj['time'].get()
        print cur_pos
        self._rec_obj.stop()
        self._table_list[0].view()
        self._saveRecording(cur_pos)

    def _prepareNextTable(self):
        print "prepare next table"
        self._table_count_index += 1
        self._table_list.append(NewTable(self._table_dur, self._chnls))

    def _switchNextTable(self):
        self._rec_obj.setTable(self._table_list[self._table_count_index])
        self._rec_obj.play()

    def _saveRecording(self, pos):
        self._IS_SAVING = True
        sr = self._rec_obj.getSamplingRate()
        total_dur = int(sr*self._table_count_index*self._table_dur+pos)
        final_table = DataTable(total_dur, self._chnls)
        for i in range(self._table_count_index+1):
            length = int(sr*self._table_dur)
            if i == self._table_count_index:
                length = int(pos)
            final_table.copyData(self._table_list[i], srcpos=0, destpos=int(sr*i*self._table_dur), length=length)
        final_table.fadein()
        final_table.fadeout()
        final_table.save(self._path, PSConfig.REC_FORMAT, PSConfig.REC_BIT_DEPTH)
        self._IS_SAVING = False


class SoundRecorder:
    def __init__(self, obj, path, chnls):
        # instance variables
        self._chnls = chnls
        self._path = path
        self._counter = 0
        self._IS_SAVING = False

        # pyo objects
        self._table = NewTable(PSConfig.REC_MAX_TIME + 1, self._chnls)
        self._rec_obj = TableFill(obj, self._table)

    def __del__(self):
        if self._rec_obj.isPlaying():
            self.stop()
        if self._IS_SAVING:
            Clean_objects(5, self)

    def stop(self):
        cur_pos = int(self._rec_obj.getCurrentPos(False))
        self._rec_obj.stop()
        self._saveRecording(cur_pos)

    def _saveRecording(self, pos):
        self._IS_SAVING = True
        final_table = DataTable(pos, self._chnls)
        final_table.copyData(self._table, srcpos=0, destpos=0, length=pos)
        final_table.fadein()
        final_table.fadeout()
        final_table.save(self._path, PSConfig.REC_FORMAT, PSConfig.REC_BIT_DEPTH)
        self._IS_SAVING = False


class TrackRecorder:
    def __init__(self):
        """
        Used to record live audio in Pyo Synth.
        Max length in seconds in set in the config file.
        It will eventually be available as an option in the preferences.
        """
        self._recObj = None

    def record(self, obj, chnls):
        path = self._makeNewRecFilePath()
        # creates a 10sec long record object
        self._recObj = SoundRecorder(obj, path, chnls)
        return path

    def stop(self):
        self._recObj.stop()

    def _makeNewRecFilePath(self):
        name = "%s%s" % (time.strftime("%d-%m-%y_%H-%M-%S"), PSConfig.REC_FORMAT_DICT[PSConfig.REC_FORMAT])
        return os.path.join(PSConfig.REC_PATH, name)


class Click:
    def __init__(self, tempo, nchnls, mul=1):
        self._sine_freq = 900
        self._tempo_val_ = tempo
        self._tempo = Sig(tempo)
        self._mul = mul
        self._time = 60. / self._tempo
        self._freq = 1. / self._time
        self._metro = Metro(self._time).play()
        self._adsr = LinTable([(0, 0), (100, 1), (1000, .25), (8191, 0)])
        self._env = TrigEnv(self._metro, table=self._adsr, dur=.125, mul=self._mul)
        if nchnls == 1:
            self._sine = FastSine(freq=self._sine_freq, quality=0, mul=self._env)
        else:
            self._sine = FastSine(freq=[self._sine_freq, self._sine_freq], quality=0, mul=self._env)

    def __getitem__(self, i):
        if i == 'click':
            return self._metro

    def reinit(self, nchnls):
        self._tempo = Sig(self._tempo_val_)
        self._time = 60. / self._tempo
        self._freq = 1. / self._time
        self._metro = Metro(self._time).stop()
        self._adsr = LinTable([(0, 0), (100, 1), (1000, .25), (8191, 0)])
        self._env = TrigEnv(self._metro, table=self._adsr, dur=.125, mul=self._mul)
        if nchnls == 1:
            self._sine = FastSine(freq=self._sine_freq, quality=0, mul=self._env)
        else:
            self._sine = FastSine(freq=[self._sine_freq, self._sine_freq], quality=0, mul=self._env)

    def out(self):
        self.play()
        self._sine.out()
        return self

    def mute(self):
        self._env.stop()
        self._sine.stop()

    def play(self):
        self._metro.play()
        self._env.play()
        self._sine.play()
        return self

    def stop(self):
        self.mute()
        self._metro.stop()
        return self

    def setTempo(self, tempo):
        self._tempo.value = tempo
        self._tempo_val_ = tempo

    def setMul(self, mul):
        self._mul = mul
        self._env.mul = mul

    def getTempo(self, sig=True):
        if sig:
            return self._tempo
        else:
            return self._tempo_val_

    def getTime(self, sig=True):
        if sig:
            return self._time
        else:
            return 60. / self._tempo_val_

    def getFreq(self, sig=True):
        if sig:
            return self._freq
        else:
            return 1. / (60. / self._tempo_val_)


class ClipMonitor:
    """
    :type: clipval: float between 0 and 1
           callback: python function
           reset_time: integer, time in milliseconds
    """
    def __init__(self, clipval, callback, reset_time):
        self._input = Sig(0)
        self.callback = callback
        self.clip_val = clipval
        self.reset_time = reset_time / 1000.
        self.timer = None
        self.thresh = Thresh(Sig(0), threshold=self.clip_val).stop()
        self.trigCallback = TrigFunc(self.thresh, self.onClip).stop()

    def reinit(self):
        self._input = Sig(0)
        self.thresh = Thresh(self._input, threshold=self.clip_val).stop()
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
            self._input = input.mix(1)
            self.thresh.input = self._input
        else:
            self._input = input
            self.thresh.input = input
