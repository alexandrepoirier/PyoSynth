import sys
if sys.platform == 'linux2':
    from pyo64 import *
else:
    from pyo import *

class NoteinSustain:
    """
    Class similar to builtin Notein object but with sustain integrated.
    The sustain pedal is assumed to be controller number 64. See Notein's
    documentation for the argument descriptions.

    """
    def __init__(self, poly=10, scale=0, first=0, last=127, channel=0):
        self._sustain = False
        self._notelist = [0]*poly # notes that accumulate and play as sustain is engaged
        self._sus_notelist = [0]*poly # notes that are still pressed after sustain is released
        self._poly = poly
        self._notes = Notein(poly, scale, first, last, channel)
        self._noteon = TrigFunc(self._notes["trigon"], self._onNoteon, range(poly))
        self._noteoff = TrigFunc(self._notes["trigoff"], self._onNoteoff, range(poly))
        self._sus_ctl = Midictl(64, channel=channel)
        self._sus_ctl.setInterpolation(False)
        self._sus_callback = TrigFunc(Change(self._sus_ctl), self._onSustain)
        self._velocity = Sig([0]*poly)
        self._pitch = Sig([0]*poly)

    def __getitem__(self, str):
        if str == 'pitch':
            return self._pitch
        elif str == 'velocity':
            return self._velocity
        elif str == 'trigon':
            return self._notes['trigon']
        elif str == 'trigoff':
            return self._notes['trigoff']
        else:
            raise Exception, ("%s : invalid key in NoteinSustain.__getiem__"%str)

    def _onNoteon(self, which):
        try:
            index = self._notelist.index(0) # essai de trouver une voie de polyphonie
        except:
            pitch = self._notes.get("pitch", True)[which]
            try:
                index = self._notelist.index(pitch)
            except:
                # we have reached max polyphony and the new note is note in the list so exit func
                return
            else:
                # si le sustain est en fonction, on veut s'assurer que la note est aussi dans _sus_notelist
                if self._sus_notelist[index] == 0:
                    amp = self._notes.get("velocity", True)[which]
                    index = self._notelist.index(pitch)  # on veux toutefois ajuster son amplitude
                    self._sus_notelist[index] = pitch
                    self._velocity[index].value = amp
                else:
                    return
        else:
            pitch = self._notes.get("pitch", True)[which]
            amp = self._notes.get("velocity", True)[which]
            if pitch not in self._notelist: # on ajoute pas une note deja jouee
                self._notelist[index] = pitch
                self._pitch[index].value = pitch
                self._sus_notelist[index] = pitch
            else:
                index = self._notelist.index(pitch) # on veut toutefois ajuster son amplitude
                self._sus_notelist[index] = pitch
            self._velocity[index].value = amp

    def _onNoteoff(self, which):
        pitch = self._notes.get("pitch", True)[which]
        try:
            index = self._notelist.index(pitch)
        except:
            # max polyphony reached, new note was never played in the first place
            return
        else:
            self._sus_notelist[index] = 0
            if not self._sustain:
                self._velocity[index].value = 0

    def _onSustain(self):
        if self._sus_ctl.get() == 0:
            self._sustain = False
            self._releaseNotesSustain()
        else:
            self._sustain = True

    def _releaseNotesSustain(self):
        for i in range(self._poly):
            pitch = self._notelist[i]
            if pitch != 0 and pitch not in self._sus_notelist:
                self._velocity[i].value = 0

    def freeVoice(self, index):
        self._notelist[index] = 0