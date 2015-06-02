#------------------------PATCH------------------------#
mix = SfPlayer("/Users/alex/OneDrive/Pyo Synth/tests/nice-track.wav").out()


#------------------------PRESET------------------------#
preset = {0: {'adsr': (0.01, 0.05, 0.7, 0.1),
     'adsr_ctlnums': (74, 74, 74, 74),
     'master': 0.8},
 1: {'attr': 'mix.speed',
     'ctlnum': 7,
     'exp': False,
     'max': 1,
     'min': 0,
     'name': 'mix.speed',
     'port': True,
     'prec': 2,
     'val': 0.9999022483825684},
 2: {'attr': 'mix.mul',
     'ctlnum': 74,
     'exp': False,
     'max': 1,
     'min': 0,
     'name': 'mix.mul',
     'port': False,
     'prec': 2,
     'val': 0.9999679327011108}}

pyosynth.setPreset(preset)