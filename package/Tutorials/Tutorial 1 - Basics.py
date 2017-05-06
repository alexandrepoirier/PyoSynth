# Tutorial 1 - Basics
#
# Pyo Synth is basically a big wrapper around pyo's midi modules to provide a fast way of building synthesizer scripts
# and interacting with them. It gives you access to most of the midi streams and are available through the dictionary
# syntax. ex.: pyosynth['pitch']
#
# Current supported streams are: pitch, amp, vel, noteon, noteoff, bend, mod, freevoice and the midi controls 'c1'
# through 'c16'. I have yet to integrate the Aftertouch and Program changes.
#
# When running the script in pyosynth, every object is added to the PatchWindow so you can link their parameters
# to a knob on your midi device. Just click on a box, select an object in the list to see what parameters can be
# controlled at audio rate, then double click on the parameter you wish to control.
#
#------------------------PATCH------------------------#
# Here we use the pitch stream (in Hz) and the amp stream to control a Sine object
sine = Sine(freq=pyosynth['pitch'], mul=pyosynth['amp'])
sinemix = sine.mix()
delay1 = Delay(sinemix, delay=0.724, feedback=.4, mul=.8)
# The mix object mixes down the signal to whatever channels we need and outputs it to the speakers
# Note that this is the only .out() that we call
mix = Mix([sinemix,delay1], voices=2, mul=.4).out()


# Presets are created automatically when saving you setup in pyosynth
# As you can see, it saves the state of every control box, the ADSR enveloppe and the master volume.
#
# Then, using the Match Mode, you can recover a specific sound by matching the values of the preset with your midi
# keyboard knobs. This is enabled by default, but you can disable it with Cmd+P.
# The Match Mode will start automatically the first time you run a script. These values are also used in the case
# a script is exported without having being executed first.
#------------------------PRESET------------------------#
preset = {0: {'adsr': (0.01, 0.05, 0.7, 0.1), 'master': 0.8},
 1: {'attr': 'delay1.delay',
     'dB': False,
     'exp': False,
     'floor': False,
     'max': 1,
     'min': 0,
     'name': u'Delay',
     'norm_val': 0.33799999952316284,
     'port': False,
     'prec': 2,
     'val': 0.33800017833709717},
 2: {'attr': 'delay1.feedback',
     'dB': False,
     'exp': False,
     'floor': False,
     'max': 1,
     'min': 0,
     'name': u'Feedback',
     'norm_val': 0.49000000953674316,
     'port': False,
     'prec': 2,
     'val': 0.48999983072280884},
 3: {'attr': 'delay1.mul',
     'dB': True,
     'exp': True,
     'floor': False,
     'max': 1.5,
     'min': 0,
     'name': u'Delay Mix',
     'norm_val': 0.6940000057220459,
     'port': False,
     'prec': 2,
     'val': 0.7224537134170532}}

pyosynth.setPreset(preset)