noise = Noise(mul=.01)

sinefb = Sig(0)
sine1 = SineLoop(freq=pyosynth['pitch']*.99+noise, feedback=sinefb, mul=pyosynth['amp'])
sine2 = SineLoop(freq=pyosynth['pitch']*1.01+noise, feedback=sinefb, mul=pyosynth['amp'])

wgDryWet = Sig(0)
sinemix = Mix([sine1.mix(),sine2.mix()], voices=2, mul=1-wgDryWet)
wg = AllpassWG(sinemix, mul=wgDryWet)
wgMix = Mix([sinemix,wg], voices=2)

delay = SmoothDelay(wgMix)
rev = WGVerb(delay)
dist = Disto(rev, mul=.7)

mix = Mix([wgMix,dist], voices=2).out()