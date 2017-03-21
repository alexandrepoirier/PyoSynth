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