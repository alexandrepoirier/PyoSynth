#------------------------PATCH------------------------#
sine1 = Sine(freq=pyosynth['pitch']*pyosynth['bend']*1.009, mul=.3*pyosynth['amp'])
sine2 = Sine(freq=pyosynth['pitch']*pyosynth['bend'], mul=.3*pyosynth['amp'])
sineOct1 = Sine(freq=pyosynth['pitch']*pyosynth['bend']*2.009, mul=.24*pyosynth['amp'])
sineOct2 = Sine(freq=pyosynth['pitch']*pyosynth['bend']*2, mul=.24*pyosynth['amp'])
osc_mix = Mix([sine1.mix(),sine2.mix(),sineOct1.mix(),sineOct2.mix()], voices=2)

hardEnv = LinTable(list=[(0,0.0000),(52,1.0000),(1076,0.6302),(8191,0.0000)])
ampPerc = TrigEnv(pyosynth['noteon'], hardEnv, dur=.1, mul=pyosynth['amp']).mix()
noise = PinkNoise(ampPerc).mix(2)
filter1 = ButBP(noise, freq=13787, q=3.16, mul=.2)
filter2 = Biquad(noise, freq=57.8, q=3.4, mul=.8)

mix1 = Mix([osc_mix, filter1, filter2], voices=2)
dist = Disto(mix1, drive=.86, slope=.2, mul=.3)

randFreq = Randi(1, 5, freq=.1)
randTime = Randi(.1, 1, freq=randFreq)
delay = Delay(dist, delay=randTime, mul=.38)

freqshift = FreqShift(dist, shift=553, mul=.4)

lfo = LFO(freq=.01, sharp=0, mul=pyosynth['mod'], add=1-pyosynth['mod'])
verb = Freeverb(Mix([dist, freqshift, delay], voices=2), size=.9, damp=.11, bal=.78, mul=lfo)

hpf = ButHP(verb, freq=120, mul=1)
mix = Compress(hpf).out()



#------------------------PRESET------------------------#
preset = {0: {'adsr': (0.01, 0.13750000000000004, 0.7000000000000001, 0.1),
     'adsr_ctlnums': (74, 74, 74, 74),
     'master': 0.8},
 1: {'attr': 'verb.size',
     'ctlnum': 7,
     'exp': False,
     'floor': False,
     'max': 1,
     'min': 0,
     'name': 'verb.size',
     'port': False,
     'prec': 2,
     'val': 0.6534831523895264},
 2: {'attr': 'verb.damp',
     'ctlnum': 74,
     'exp': False,
     'floor': False,
     'max': 1,
     'min': 0,
     'name': 'verb.damp',
     'port': False,
     'prec': 2,
     'val': 0.05505668371915817},
 3: {'attr': 'verb.bal',
     'ctlnum': 71,
     'exp': False,
     'floor': False,
     'max': 1,
     'min': 0,
     'name': 'verb.bal',
     'port': False,
     'prec': 2,
     'val': 0.9449419975280762},
 4: {'attr': 'dist.drive',
     'ctlnum': 93,
     'exp': False,
     'floor': False,
     'max': 1,
     'min': 0,
     'name': 'dist.drive',
     'port': False,
     'prec': 2,
     'val': 0.732223391532898},
 5: {'attr': 'mix.thresh',
     'ctlnum': 73,
     'exp': False,
     'floor': False,
     'max': 0.0,
     'min': -60.0,
     'name': u'Comp Thresh',
     'port': False,
     'prec': 1,
     'val': -24.0},
 6: {'attr': 'mix.ratio',
     'ctlnum': 75,
     'exp': False,
     'floor': False,
     'max': 20.0,
     'min': 1.0,
     'name': u'Comp Ratio',
     'port': False,
     'prec': 1,
     'val': 11.015462875366211},
 7: {'attr': 'mix.mul',
     'ctlnum': 79,
     'exp': False,
     'floor': False,
     'max': 3.0,
     'min': 0,
     'name': u'Comp MakeUp',
     'port': False,
     'prec': 2,
     'val': 2.1025524139404297},
 9: {'attr': 'freqshift.shift',
     'ctlnum': 114,
     'exp': True,
     'floor': False,
     'max': 2000.0,
     'min': 20.0,
     'name': u'FreqShift',
     'port': True,
     'prec': 1,
     'val': 279.81158447265625},
 10: {'attr': 'freqshift.mul',
      'ctlnum': 76,
      'exp': False,
      'floor': False,
      'max': 1,
      'min': 0,
      'name': u'FreqShift Vol',
      'port': False,
      'prec': 2,
      'val': None},
 11: {'attr': 'delay.mul',
      'ctlnum': 77,
      'exp': False,
      'floor': False,
      'max': 1,
      'min': 0,
      'name': u'Delay Vol',
      'port': False,
      'prec': 2,
      'val': None},
 12: {'attr': None,
      'ctlnum': 91,
      'exp': True,
      'floor': False,
      'max': 1.0,
      'min': 0.0,
      'name': u'Delay Fb',
      'port': True,
      'prec': 1,
      'val': 0.13116595149040222},
 13: {'attr': 'hpf.freq',
      'ctlnum': 18,
      'exp': True,
      'floor': False,
      'max': 20000.0,
      'min': 20.0,
      'name': u'HP Freq',
      'port': True,
      'prec': 1,
      'val': None},
 14: {'attr': 'lfo.freq',
      'ctlnum': 19,
      'exp': True,
      'floor': False,
      'max': 100.0,
      'min': 1.0,
      'name': u'LFO Freq',
      'port': False,
      'prec': 2,
      'val': 3.4571290016174316},
 15: {'attr': 'lfo.sharp',
      'ctlnum': 16,
      'exp': False,
      'floor': False,
      'max': 1,
      'min': 0,
      'name': u'LFO Sharp',
      'port': False,
      'prec': 2,
      'val': 0.25990331172943115}}

pyosynth.setPreset(preset)