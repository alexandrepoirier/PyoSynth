saw1 = SuperSaw(pyosynth['pitch']*pyosynth['bend']*1.01, mul=pyosynth['amp'])
saw2 = SuperSaw(pyosynth['pitch']*pyosynth['bend']*.99, mul=pyosynth['amp'])
oscMix = Mix([saw1.mix(),saw2.mix()], voices=2, mul=.5)

#fx
harmo = Harmonizer(oscMix)
harmoMix = Mix([oscMix,harmo], voices=2)
filter = Biquadx(harmoMix)
delay = SmoothDelay(filter)

mi = Mix([filter,delay], voices=2).out()