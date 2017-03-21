# Tutorial 3 - Functions Menu
#
# This menu is useful when you want to change values in your script that can't be done at audio rate.
# It can also be used to change the state of the program. Basically, anything more complicated than controlling a
# single parameter.
#
# We'll start by defining a simple script to fiddle with.
#
import random # import whatever you need, this is all regular python code

# harmonics table and oscillator
table = [1.0,0,0,0,0,0,0,0,0,0,0,0]
t = HarmTable(table)
osc = OscLoop(t, pyosynth['pitch'], mul=pyosynth['amp'])
oscmix = osc.mix()
oscmix.mul = .2 # the final output can be pretty loud so be careful

# EQ and final mix
eq_freqs = [250, 1000, 2500, 6000]
eq_qs = [1 for i in range(len(eq_freqs))]
eq_boosts = [0 for i in range(len(eq_freqs))]
eqs = EQ(oscmix, freq=eq_freqs[i], q=eq_qs[i], boost=eq_boosts[i])
mix = Mix(eqs.mix(), voices=2).out()

# define the function you want to use
def randHarms():
    # this lets us create random partials tables
    new_t = [random.random() for i in range(len(table))]
    t.replace(new_t)
    return new_t # the return value will be displayed in the terminal window, press Cmd+T to open it

def randEvenHarms():
    # randomize only even partials with fundamental
    new_t = []
    for i in range(len(table)):
        if i % 2 != 0 or i == 0:
            new_t.append(random.random())
        else:
            new_t.append(0.0)
    t.replace(new_t)
    return new_t

def randOddHarms():
    # randomize only odd partials with fundamental
    new_t = []
    for i in range(len(table)):
        if i % 2 == 0:
            new_t.append(random.random())
        else:
            new_t.append(0.0)
    t.replace(new_t)
    return new_t

def randEQ():
    # this function randomizes the EQ dips
    new_freqs = [eq_freqs[i]*random.uniform(0.9,1.1) for i in range(len(eq_freqs))]
    new_qs = [random.uniform(1,3) for i in range(len(eq_freqs))]
    new_boosts = [random.uniform(-12,0) for i in range(len(eq_freqs))]
    eqs.freq = new_freqs
    eqs.q = new_qs
    eqs.boost = new_boosts
    return "Frequencies: %s\nQs: %s\nLevels: %s"%(new_freqs,new_qs,new_boosts)

def randAll():
    # this randomizes both the harmonics and the EQ
    # since functions return their own results, we'll see the result of the function as a whole
    randHarms()
    randEQ()


# The setFunctions() method specifies the functions to be used in the menu
# It accept a list of either just callables, or tuples of a callable followed by a string.
pyosynth.setFunctions([(randHarms, "Randomize Harmonics"),
                       (randEvenHarms, "Rand. Even Harmonics"),
                       (randOddHarms, "Rand. Odd Harmonics"),
                       (randEQ, "Randomize EQ Params"),
                       (randAll, "Randomize Everything")])