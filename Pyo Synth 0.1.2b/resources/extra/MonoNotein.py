from pyo import *

class MonoNotein:
    """
    Creates ane emulatino of a mono Notein object that onl plays one note, like a mono synth.

    mode : The mono mode. Can be 0:recent, 1:low priority, 2:high priority
    portamento : time to glide between notes
    maxHoldNotes : maximum number of notes that can be held in memory.
    channel : Midi channel to listen to.
    """
    def __init__(self, mode=0, portamento=0.05, maxHoldNotes=10, channel=0):
        # pitch (in Hz) and amplitude (normalized) audio streams
        self.hz = SigTo(0, portamento, 0)
        self.amp = Sig(0)
        self._port = portamento

        # pitch and amplitude lists
        self.plist = []
        self.alist = []
        # only for low and high prority
        self.current = 0

        self.setMonoType(mode)

        # get midi notes
        self.note = Notein(poly=maxHoldNotes, channel=channel)
        # listen to 'note on' and 'note off' triggers and call onNote
        self.notetrig = TrigFunc(self.note['trigon']+self.note['trigoff'], self.onNote, range(maxHoldNotes))

    def __getitem__(self, x):
        if x == "pitch":
            return self.hz
        elif x == "velocity":
            return self.amp

    def onNote(self, which):
        pit = self.note["pitch"].get(True)[which]
        vel = self.note["velocity"].get(True)[which]
        if vel:
            self.plist.append(pit)
            self.alist.append(vel)
            if self.mode == 0:
                self.hz.value = midiToHz(pit)
                self.amp.value = vel
                self.current = pit
            else:
                self.onNoteOnLowHigh(pit, vel)
        else:
            self.mode_callback(pit)

    def onNoteOnLowHigh(self, pit, vel):
        if self.mode == 1:
            if pit < self.current or self.current == 0:
                self.hz.value = midiToHz(pit)
                self.amp.value = vel
                self.current = pit
        else:
            if pit > self.current:
                self.hz.value = midiToHz(pit)
                self.amp.value = vel
                self.current = pit

    def onNoteOffRecent(self, pit):
        pos = self.plist.index(pit)
        if pos == (len(self.plist) - 1):
            del self.plist[-1]
            del self.alist[-1]
            if len(self.plist) == 0:
                self.hz.value = 0
                self.amp.value = 0
            else:
                self.hz.value = midiToHz(self.plist[-1])
                self.amp.value = self.alist[-1]
        else:
            del self.plist[pos]
            del self.alist[pos]

    def onNoteOffLowHigh(self, pit):
        pos = self.plist.index(pit)
        del self.plist[pos]
        del self.alist[pos]
        if pit == self.current:
            if len(self.plist) == 0:
                self.hz.value = 0
                self.amp.value = 0
                self.current = 0
            else:
                if self.mode == 1:
                    val = min(self.plist)
                else:
                    val = max(self.plist)
                pos = self.plist.index(val)
                self.hz.value = midiToHz(val)
                self.amp.value = self.alist[pos]
                self.current = val

    def setMonoType(self, type):
        # which mode to use
        assert type in (0, 1, 2), "MonoNotein 'type' attribute must be either 0, 1 or 2 (recent, low priority, high priority)."
        if type == 0:
            self.mode_callback = self.onNoteOffRecent
        else:
            self.mode_callback = self.onNoteOffLowHigh
        self.mode = type

    def setPort(self, value):
        self._port = value
        self.hz.setTime(value)