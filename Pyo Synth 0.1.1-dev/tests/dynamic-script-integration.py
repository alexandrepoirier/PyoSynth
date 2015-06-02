#!/usr/bin/env python
# encoding: utf-8
from pyo import *
import time

s = Server(sr=44100, nchnls=2, buffersize=512, duplex=1).boot()

pyo_objs = {}
dict_before = locals().copy()

execfile("/Volumes/DOCUMENTS/WORK/Pyo Projects/Pyo Synth/testScript.py")

dict_after = locals().copy()

##Compare le dictionnaire locals() avant et après
##l'exécution du script et les place dans
##un dictionnaire 'pyo_objs'
def getRunningPyoObjs():
    for key in dict_after:
        if key not in dict_before:
            if isinstance(dict_after[key], PyoObjectBase):
                pyo_objs[key] = dict_after[key]
    
##Arrête et nettoie tous les objets audio
##contenu dans le dictionnaire passé en paramètre
def cleanScriptObjs(dict):
    if len(dict)>0:
        for obj in dict:
            if isinstance(dict[obj], PyoObjectBase):
                Clean_objects(.1, dict[obj]).start()
        dict.clear()

getRunningPyoObjs()

s.gui(locals())