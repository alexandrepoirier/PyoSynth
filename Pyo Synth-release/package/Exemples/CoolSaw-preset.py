#------------------------PATCH------------------------#
saw1 = SuperSaw(freq=pyosynth['pitch']*pyosynth['bend'],
                detune=pyosynth['c1'],
                bal=.7,
                mul=pyosynth['amp']*pyosynth['c2'])

saw2 = SuperSaw(freq=pyosynth['pitch']*pyosynth['bend']*.99,
                detune=pyosynth['c1'],
                bal=.7,
                mul=pyosynth['amp']*pyosynth['c2'])
                
sawFilter = Biquadx([saw1.mix(),saw2.mix()], freq=pyosynth['c9'], q=.74)
delay = SmoothDelay(sawFilter, pyosynth['c10'], pyosynth['c11'], mul=pyosynth['c12'])
                
noise = Noise(mul=pyosynth['c6']*2.92,add=1)
sine1 = Sine(freq=pyosynth['pitch']*pyosynth['bend']/2*noise, phase=pyosynth['c5'], mul=pyosynth['amp'])
sine2 = Sine(freq=pyosynth['pitch']*pyosynth['bend']/2*noise, mul=pyosynth['amp'])
subFilter = Biquad([sine1.mix(),sine2.mix()], freq=150, q=1, mul=.5)
subDrive = Disto(subFilter, drive=pyosynth['c6']*.67, slope=.9, mul=pyosynth['c7'])

lfo = LFO(freq=pyosynth['c3'], sharp=pyosynth['c4'], mul=pyosynth['mod'], add=1-pyosynth['mod'])
premix = Mix([sawFilter,delay,subDrive], voices=2)
mix = Freeverb(premix, size=pyosynth['c13'], damp=pyosynth['c14'], bal=pyosynth['c15'], mul=lfo).out()



#------------------------PRESET------------------------#
preset = {0: {'adsr': (0.01, 0.05, 0.7, 0.1),
     'adsr_ctlnums': (72, 74, 74, 72),
     'master': 0.8},
 1: {'attr': None,
     'ctlnum': 7,
     'exp': False,
     'max': 1,
     'min': 0,
     'name': 'Saw Detune',
     'port': False,
     'prec': 1,
     'floor':False,
     'val': 0.7318542003631592},
 2: {'attr': None,
     'ctlnum': 74,
     'exp': False,
     'max': 1,
     'min': 0,
     'name': 'Saw Vol',
     'port': False,
     'prec': 1,
     'floor':False,
     'val': 0.8268318772315979},
 3: {'attr': None,
     'ctlnum': 71,
     'exp': True,
     'max': 50,
     'min': 0.01,
     'name': 'LFO Freq',
     'port': True,
     'prec': 1,
     'floor':False,
     'val': None},
 4: {'attr': None,
     'ctlnum': 93,
     'exp': False,
     'max': 1,
     'min': 0,
     'name': 'LFO Sharpness',
     'port': False,
     'prec': 1,
     'floor':False,
     'val': None},
 5: {'attr': None,
     'ctlnum': 73,
     'exp': False,
     'max': 1,
     'min': 0,
     'name': 'Sub Phase',
     'port': True,
     'prec': 1,
     'floor':False,
     'val': None},
 6: {'attr': None,
     'ctlnum': 75,
     'exp': False,
     'max': 1,
     'min': 0,
     'name': 'Sub Violence',
     'port': False,
     'prec': 1,
     'floor':False,
     'val': None},
 7: {'attr': None,
     'ctlnum': 79,
     'exp': False,
     'max': 1,
     'min': 0,
     'name': 'Sub Vol',
     'port': True,
     'prec': 1,
     'floor':False,
     'val': 0.02356262505054474},
 9: {'attr': None,
     'ctlnum': 114,
     'exp': True,
     'max': 20000,
     'min': 20,
     'name': 'Saw Cutoff',
     'port': True,
     'prec': 1,
     'floor':False,
     'val': 1716.4449462890625},
 10: {'attr': None,
      'ctlnum': 76,
      'exp': True,
      'max': 1,
      'min': 0.0003,
      'name': 'Delay',
      'port': False,
      'prec': 4,
      'floor':False,
      'val': None},
 11: {'attr': None,
      'ctlnum': 77,
      'exp': False,
      'max': 1,
      'min': 0,
      'name': 'Feedback',
      'port': False,
      'prec': 1,
      'floor':False,
      'val': None},
 12: {'attr': None,
      'ctlnum': 91,
      'exp': False,
      'max': 1,
      'min': 0,
      'name': 'Delay Level',
      'port': False,
      'prec': 1,
      'floor':False,
      'val': None},
 13: {'attr': None,
      'ctlnum': 18,
      'exp': False,
      'max': 1,
      'min': 0,
      'name': 'R-Size',
      'port': False,
      'prec': 1,
      'floor':False,
      'val': None},
 14: {'attr': None,
      'ctlnum': 19,
      'exp': False,
      'max': 1,
      'min': 0,
      'name': 'R-Damp',
      'port': False,
      'prec': 1,
      'floor':False,
      'val': None},
 15: {'attr': None,
      'ctlnum': 16,
      'exp': False,
      'max': 1,
      'min': 0,
      'name': 'R-Bal',
      'port': False,
      'prec': 1,
      'floor':False,
      'val': None}}

pyosynth.setPreset(preset)