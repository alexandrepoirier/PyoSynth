#------------------------PATCH------------------------#
sine = Sine(freq=1, mul=10, add=1000)
sine2 = Sine(freq=sine, mul=.2).out()
a=5
b=2
c=5
#------------------------PRESET------------------------#
preset = {0: 1.0,
 1: {'attr': 'sine2.mul',
     'exp': False,
     'max': 1,
     'min': 0,
     'name': 'sine2.mul',
     'port': False,
     'prec': 1,
     'val': 0.7715933322906494},
 2: {'attr': 'sine.freq',
     'exp': False,
     'max': 50.0,
     'min': 1.0,
     'name': 'sine.freq',
     'port': False,
     'prec': 1,
     'val': 42.28053665161133},
 3: {'attr': 'sine.mul',
     'exp': False,
     'max': 200.0,
     'min': 1.0,
     'name': 'sine.mul',
     'port': False,
     'prec': 1,
     'val': 120.09868621826172}}

pyosynth.setPreset(preset)