"""
Copyright 2017 Alexandre Poirier

This file is part of Pyo Synth, a GUI written in python that helps
with live manipulation of synthesizer scripts written with the pyo library.

Pyo Synth is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

Pyo Synth is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Pyo Synth.  If not, see <http://www.gnu.org/licenses/>.
"""

import pickle, PSConfig, os

PARAMS_TREE_DICT = {}

try:
    with open(os.path.join(PSConfig.PREF_PATH, "audio_rate_params_dict.txt")) as f:
        PARAMS_TREE_DICT = pickle.load(f)
except IOError, e:
    raise IOError, "Can't open pyo objects parameters dictionary."