# Tutorial 2 - Quick Preset
#
# If you want to setup the controls in advance, and not through the interface, you can do it
# by using methods that are made available to you.
#
#
# Define a dictionary to setup the names of the controls you want to use
# The key is the number of the control box, the value, either a string or a list
info_dict = {1: "Saw Detune",
             2: "Saw Vol",
             3: "Saw Cutoff",
             4: "Master Vol",
             9: ["Delay", 4], # the list is used to define the name and the precision of the displayed value
             10: "Feedback",
             11: "Delay Level",
             }

# set it up using the quickPreset method
pyosynth.quickPreset(info_dict)

# define the scaling, the portamento and the exponential parameters if applicable
# First parameter is always the number of the ParamBox, from 1 to 16
pyosynth.setPort(1, True)
pyosynth.setPort(2, True)
pyosynth.setDisplayDB(2, True) # displays dB values, while controller values remain normalized
pyosynth.setScale(3, 20, 20000)
pyosynth.setPort(3, True)
pyosynth.setPort(4, True)
pyosynth.setDisplayDB(4, True)
pyosynth.setPort(9, True)
pyosynth.setScale(9, 0, .75)
pyosynth.setDisplayDB(11, True)

# create two slighlty detuned Saw oscillators
saw1 = SuperSaw(freq=pyosynth['pitch'] * pyosynth['bend'], # here we use the pitchbend control
                detune=pyosynth['c1'], # the first control 'c1' will be assigned to the detune parameter
                bal=.7,
                mul=pyosynth['amp'] * pyosynth['c2']) # here we call the second control directly in the script with 'c2'

saw2 = SuperSaw(freq=pyosynth['pitch'] * pyosynth['bend'] * .99,
                detune=pyosynth['c1'],
                bal=.7,
                mul=pyosynth['amp'] * pyosynth['c2'])

# Be sure to mix the oscillators when passing them to other objects as they contain as many streams as
# the number of polyphony voices. Without mixing the SuperSaw, we'd be creating 20 Biquadx objects and then
# 20 SmoothDelay objects. Not very efficient!
sawFilter = Biquadx([saw1.mix(), saw2.mix()], freq=pyosynth['c3'], q=.74)
delay = SmoothDelay(sawFilter, pyosynth['c9'], pyosynth['c10'], mul=pyosynth['c11'])
# finally, the mix object that sends the sound to the output
mix = Mix([sawFilter,delay], voices=2, mul=pyosynth['c4']).out()