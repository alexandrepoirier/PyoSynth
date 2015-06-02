#l'element 0 est le master volume

preset = {0:{'master':0.6,
             'adsr':(.01,.02,.8,.2),
             'adsr_ctlnum':(73,72,71,75)
            },
          1:{'name':"Saw Detune",
             'min':0,
             'max':1,
             'port':False,
             'exp':False,
             'prec':1,
             'attr':'saw1.detune',
             'val':0.52,
             'ctlnum':74
            },
          2:{'name':"Saw Vol",
             'min':0,
             'max':1,
             'port':False,
             'exp':False,
             'prec':1,
             'attr':'saw1.mul',
             'val':0.8,
             'ctlnum':70
            }
         }