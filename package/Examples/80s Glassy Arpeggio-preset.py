#------------------------PATCH------------------------#
scaleFactor = lambda x:2.**(x/12.)
scale_list = [1,1,1,1, scaleFactor(12), scaleFactor(24)]

rand_chaos = Randi(0, 1, [.5, 1, .2, .3])
rand_pitch = Randi(0, .08, [1, .8, .5, .2])
chen_mod = Sig(0)
chen = ChenLee(pitch=rand_pitch, chaos=rand_chaos, mul=chen_mod)

# OSC
rand_scale = Choice(scale_list, 1./pyosynth.getTempoTime()*4.)
fsine = FastSine(freq=pyosynth['pitch']*rand_scale, quality=0, mul=pyosynth['amp']*((1-chen_mod)+chen))
fsinemix = fsine.mix(1)
fsinedist = Disto(fsinemix, drive=.2)

lfo = LFO(freq=pyosynth['pitch'], mul=pyosynth['amp']*((1-chen_mod)+chen))
lfomix = lfo.mix(1)

oscmix = Mix([lfomix, fsinedist], voices=1)

# FX
delay1 = Delay(oscmix)
delay2 = Delay(oscmix)

pva = PVAnal(oscmix, size=2048)
pvg = PVGate(pva, thresh=-36, damp=0)
pvv = PVVerb(pvg, revtime=0.95, damp=0.95)
pvs = PVSynth(pvv)

lp_flt = MoogLP(Mix([delay1, delay2, pvs.mix(2), lfomix.mix(2)], voices=2))

mix = Mix([lp_flt], voices=2).out()



#------------------------PRESET------------------------#
preset = {0: {'adsr': (0.10000000000000003, 0.05, 0.7, 0.41999999999999993),
     'master': 0.8},
 1: {'attr': 'fsinedist.mul',
     'dB': True,
     'exp': False,
     'floor': False,
     'max': 1,
     'min': 0,
     'name': u'Sine vol',
     'norm_val': 0.5120000243186951,
     'port': False,
     'prec': 2,
     'val': 0.512000322341919},
 2: {'attr': 'fsinedist.drive',
     'dB': False,
     'exp': False,
     'floor': False,
     'max': 1,
     'min': 0,
     'name': u'Sine Dist',
     'norm_val': 0.7139999866485596,
     'port': False,
     'prec': 2,
     'val': 0.7139996290206909},
 3: {'attr': 'fsinedist.slope',
     'dB': False,
     'exp': False,
     'floor': False,
     'max': 1,
     'min': 0,
     'name': u'Dist Filter',
     'norm_val': 0.1979999989271164,
     'port': False,
     'prec': 2,
     'val': 0.19800007343292236},
 4: {'attr': 'delay1.delay',
     'dB': False,
     'exp': False,
     'floor': False,
     'max': 1,
     'min': 0,
     'name': u'Delay L',
     'norm_val': 0.16200000047683716,
     'port': False,
     'prec': 2,
     'val': 0.16199991106987},
 5: {'attr': 'delay2.delay',
     'dB': False,
     'exp': False,
     'floor': False,
     'max': 1,
     'min': 0,
     'name': u'Delay R',
     'norm_val': 0.2800000011920929,
     'port': False,
     'prec': 2,
     'val': 0.27999985218048096},
 6: {'attr': 'delay1.feedback',
     'dB': False,
     'exp': False,
     'floor': False,
     'max': 1,
     'min': 0,
     'name': u'Delay L FB',
     'norm_val': 0.47200000286102295,
     'port': False,
     'prec': 2,
     'val': 0.4719998240470886},
 7: {'attr': 'delay2.feedback',
     'dB': False,
     'exp': False,
     'floor': False,
     'max': 1,
     'min': 0,
     'name': u'Delay R FB',
     'norm_val': 0.3799999952316284,
     'port': False,
     'prec': 2,
     'val': 0.3799998164176941},
 8: {'attr': 'lfomix.mul',
     'dB': True,
     'exp': False,
     'floor': False,
     'max': 1,
     'min': 0,
     'name': u'Sawtooth vol',
     'norm_val': 0.406000018119812,
     'port': False,
     'prec': 2,
     'val': 0.4059998393058777},
 9: {'attr': 'chen_mod.value',
     'dB': False,
     'exp': False,
     'floor': False,
     'max': 1,
     'min': 0,
     'name': u'Chen Mod',
     'norm_val': 0.6859999895095825,
     'port': False,
     'prec': 2,
     'val': 0.6859996318817139},
 10: {'attr': 'pvv.revtime',
      'dB': False,
      'exp': False,
      'floor': False,
      'max': 1,
      'min': 0,
      'name': u'PVReverb Time',
      'norm_val': 0.40799999237060547,
      'port': False,
      'prec': 2,
      'val': 0.40799981355667114},
 11: {'attr': 'pvv.damp',
      'dB': False,
      'exp': False,
      'floor': False,
      'max': 1,
      'min': 0,
      'name': u'PVReverb Damp',
      'norm_val': 0.7839999794960022,
      'port': False,
      'prec': 2,
      'val': 0.7839996814727783},
 12: {'attr': 'delay1.mul',
      'dB': True,
      'exp': False,
      'floor': False,
      'max': 1,
      'min': 0,
      'name': u'Delay L vol',
      'norm_val': 0.5879999995231628,
      'port': False,
      'prec': 2,
      'val': 0.587999701499939},
 13: {'attr': 'delay2.mul',
      'dB': True,
      'exp': False,
      'floor': False,
      'max': 1,
      'min': 0,
      'name': u'Delay R vol',
      'norm_val': 0.5419999957084656,
      'port': False,
      'prec': 2,
      'val': 0.5419996976852417},
 14: {'attr': 'lp_flt.freq',
      'dB': False,
      'exp': True,
      'floor': False,
      'max': 20000.0,
      'min': 20.0,
      'name': u'LowPass Cutoff',
      'norm_val': 0.36800000071525574,
      'port': True,
      'prec': 1,
      'val': 2725.47705078125},
 15: {'attr': 'lp_flt.res',
      'dB': False,
      'exp': False,
      'floor': False,
      'max': 2.0,
      'min': 0,
      'name': u'LowPass Q',
      'norm_val': 0.6100000143051147,
      'port': False,
      'prec': 2,
      'val': 1.2199993133544922},
 16: {'attr': 'lfo.sharp',
      'dB': False,
      'exp': True,
      'floor': False,
      'max': 1,
      'min': 0,
      'name': u'Saw Sharpness',
      'norm_val': 0.8299999833106995,
      'port': True,
      'prec': 2,
      'val': 0.6888281106948853}}

pyosynth.setPreset(preset)