info_dict = {  1:"Saw Detune",
               2:"Saw Vol",
               3:"LFO Freq",
               4:"LFO Sharpness",
               5:"Sub Phase",
               6:"Sub Violence",
               7:"Sub Vol",
               9:"Saw Cutoff",
               10:["Delay", 4],
               11:"Feedback",
               12:"Delay Level",
               13:"R-Size",
               14:"R-Damp",
               15:"R-Bal"
            }
            
pyosynth.quickPreset(info_dict)

#############################
# Modification des controles
#############################
pyosynth.setScale(9,20,20000) ##cutoff
pyosynth.setExp(9,True)
pyosynth.setPort(9,True)
pyosynth.setScale(10,.0003,1) ##delay
pyosynth.setExp(10,True)
pyosynth.setScale(3,.01,50) ##lfo freq
pyosynth.setExp(3,True)
pyosynth.setPort(3,True)
pyosynth.setPort(5,True)
pyosynth.setPort(7,True)

def setFreqFactor():
    freqFactor.value = scaledVel.get()

##################
## Debut du patch
##################
saw1 = SuperSaw(freq=pyosynth['pitch']*pyosynth['bend'],
                detune=pyosynth['c1'],
                bal=.7, 
                mul=pyosynth['amp']*pyosynth['c2'])

saw2 = SuperSaw(freq=pyosynth['pitch']*pyosynth['bend']*.99,
                detune=pyosynth['c1'],
                bal=.7, 
                mul=pyosynth['amp']*pyosynth['c2'])
                
scaledVel = Scale(pyosynth['vel'], outmin=.1).mix()
noteon = TrigFunc(pyosynth['noteon'], setFreqFactor)
freqFactor = Sig(1)
sawFilter = Biquadx([saw1.mix(),saw2.mix()], freq=pyosynth['c9']*freqFactor, q=.74)
delay = SmoothDelay(sawFilter, pyosynth['c10'], pyosynth['c11'], mul=pyosynth['c12'])
                
noise = Noise(mul=pyosynth['c6']*2.92,add=1)
sine1 = Sine(freq=pyosynth['pitch']*pyosynth['bend']/2*noise, phase=pyosynth['c5'], mul=pyosynth['amp'])
sine2 = Sine(freq=pyosynth['pitch']*pyosynth['bend']/2*noise, mul=pyosynth['amp'])
subFilter = Biquad([sine1.mix(),sine2.mix()], freq=150, q=1, mul=.5)
subDrive = Disto(subFilter, drive=pyosynth['c6']*.67, slope=.9, mul=pyosynth['c7'])

lfo = LFO(freq=pyosynth['c3'], sharp=pyosynth['c4'], mul=pyosynth['mod'], add=1-pyosynth['mod'])
premix = Mix([sawFilter,delay,subDrive], voices=2)
mix = Freeverb(premix, size=pyosynth['c13'], damp=pyosynth['c14'], bal=pyosynth['c15'], mul=lfo).out()