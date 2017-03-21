**Avant d'installer Pyo Synth, assurez-vous d'avoir python 2.7 d'installé sur votre machine.**

Pour installer Pyo Synth suivez les étapes suivantes :
    1. Ouvrez le Terminal
    2. lancez le fichier 'install.py' (commande 'python install.py')
    3. si l'installation a fonctionnée, vous verrez l'inscription 'Installation completed.'
    4. maintenant glissez l'icône de Pyo Synth dans le dossier 'Applications'
    
Voilà, vous êtes maintenant prêt à vous servir de Pyo Synth. Pour toutes questions ou problèmes, vous pouvez me contacter à mon adresse courriel : alexpoirier05@gmail.com

N’oubliez pas de lire le fichier de licence pour connaître vos droits d’utilisateurs.

Les sources sont disponible sur le dépôt git : https://github.com/alexandrepoirier/PyoSynth

Note : en lançant Pyo Synth vous verrez deux icônes identiques dans le dock. Ceci est dû au fait que le module pyinstaller avec lequel l’application est construite lance un bootloader pour encadrer l’exécution de l’application. Vous pouvez prendre n’importe lequel des deux icônes si vous désirez en garder une dans le dock.

—————————————————————————————————————————————————————————————————————————————————————————————

**Before installing Pyo Synth, make sure you have python 2.7 installed on your machine.**

Follow these steps to install Pyo Synth :
    1. Open the Terminal
    2. Launch the install file (write ‘python install.py’ in the Terminal)
    3. If the installation succeeded, a message will be written saying ‘Installation completed’
    4. Drag and drop the Pyo Synth icon in the ‘Applications’ folder alias

You are now ready to use Pyo Synth. For any questions or for reporting problems with the software, please contact me at my email address : alexpoirier05@gmail.com

Don’t forget to read the licence to know your rights as a user of this open source software.

Sources are available on the git repository : https://github.com/alexandrepoirier/PyoSynth

Note : when launching Pyo Synth you might notice two icons in the dock instead of one. This is because the tool used to build Pyo Synth, pyinstaller, needs to launch a bootloader before launching the actual application. To learn more on this, you can go on the pyinstaller website and read the full explanation. If you want to keep Pyo Synth in the dock, you can use any of the two icons.

—————————————————————————————————————————————————————————————————————————————————————————————

Release history :

v0.1.2b - 20/03/2017

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
- wrapped a lot of wxPython method calls in wx.CallAfter() to be ahead safe
- when no midi keyboard was plugged, the server panel crashed the program
- Optimized the WheelsBox OnPaint method so it uses a BufferedPaintDC
- MathMode tweaked to facilitate its use. It accepts a wider range of values using the formula: val-(range/128) <= x >= val+(range/128)
- In the record options window, the midi range did not show correct values when loading preferences
- Optimized the virtual keyboard class. Voices are now managed better.
- When deleting a recording, the file is sent to trash instead of brutally erasing the file.

———— Implementation details ————
- Added a warning in the Script Errors Log when a link cannot be made upon restarting a script
- Midi input output choices added in the server window
- script execution methods moved in the __main__
- server is now marked dirty when making a change. Reinitialization happens when running a new script
- PYOSYTNH_PREF now saves polyphony, bend wheel range, mono type and the number of ParamBoxes (will eventually become a preference)
- when reinitializing a ParamBox, all its values are now reset
- Added debug info in the python interpreter

———————

v0.1.1 - 10/06/2015

- Lots of bug fixes
- Window priority problem fixed
- ‘Save As’ feature added
- Option to chose a midi device in the server setup panel added
- ’99 : All devices’ option added for midi input
- The computer keyboard can be used to play as a midi keyboard
- A peak light for the ‘mix’ object has been added on the interface

———————

v0.1.0b - 24/04/2015

First release. Beta version.