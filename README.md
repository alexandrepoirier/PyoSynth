# Pyo Synth
A GUI to help with pyo synthesizer scripts manipulation.</br>
License : GNU GPL v3

Pyo Synth is an open source application that makes the manipulation of pyo scripts easier by letting you control it with a midi keyboard. The interface allows you to setup every control on your keyboard and link them to parameters in your script during runtime. It is also possible to save your progress directly in the pyo script. See manual for more explanation on features.

It only works on Mac for the moment, but it should be adapted for Windows and Linux anytime in the future.

You can download the dmg on Source Forge : https://sourceforge.net/projects/pyosynth

<b>Version 0.1.2b</b></br>
———— New Features ————
- ParamBox click and drag added to modify values with the mouse
- Added Notein Sustain class; the sustain pedal is now supported with midi keyboards
- ParamBox refresh optimization (up to 30% cpu gain)
- Added mono mode for the computer keyboard and for midi keyboards
- Save As function added
- Save Values In Script function added
- New Functions menu implemented to facilitate calling methods during runtime. The result can be printed to the python interpreter using the return value.
- Added a basic python interpreter for deeper script manipulation
- New menu MidiProfiles allows to save different midi controls configurations
- Match Mode only called when executing a script for the first time
- Added option to disable the Match Mode
- ParamBox are now automatically relinked to their objects when restarting a script
- Added three methods to retrieve metronome streams: getTempoTime(), getTempoFreq() and getTempo()
- The polyphony can now be changed in the MIDI menu along with the pitch bend range
- Polyphony is displayed in real time in the status bar
- Added Reset All Boxes function
- Past recordings are now added to the recorded tracks list with additional information
- The ADSR enveloppe can now be tweaked precisely by holding the shift key while modifying the value

———— Bug Fixes ————
- fixed bug where playing on the computer keyboard created audio clicks
- stabilized the program. Less crashes occur when starting/stopping scripts multiple times.
- fixed a bug where the VuMeter crashed the program due to math.log returning infinite as a value
- clicks when recording tracks were due to the use of the Record object. Now replaced with a 5 minute long table. Uses more RAM, but no more clicks. Note: max duration will eventually become a preference.
- wrapped a lot of wxPython method calls in wx.CallAfter() to be thread safe
- when no midi keyboard was plugged, the server panel crashed the program
- Optimized the WheelsBox OnPaint method so it uses a BufferedPaintDC
- MatchMode tweaked to facilitate its use. It accepts a wider range of values using the formula: val-(range/128) <= x >= val+(range/128)
- In the record options window, the midi range did not show correct values when loading preferences
- Optimized the virtual keyboard class. Voices are now managed better.
- When deleting a recording, the file is sent to trash instead of brutally erasing the file.
- many more small bug fixes…

———— Implementation details ————
- Added a warning in the Script Errors Log when a link cannot be made upon restarting a script
- Midi input output choices added in the server window
- script execution methods moved in the __main__
- server is now marked dirty when making a change. Reinitialization happens when running a new script
- PYOSYNTH_PREF now saves polyphony, bend wheel range, mono type and the number of ParamBoxes (will eventually become a preference)
- when reinitializing a ParamBox, all its values are now reset
- Added debug info in the python interpreter

<b>Version 0.1.1</b></br>
- Lots of bug fixes
- Window priority problem fixed
- ‘Save As’ feature added
- Option to chose a midi device in the server setup panel added
- ’99 : All devices’ option added for midi input
- The computer keyboard can be used to play as a midi keyboard
- A peak light for the ‘mix’ object has been added on the interface

<b>Version 0.1.0b</b></br>
This is the first release and it is a beta version.
