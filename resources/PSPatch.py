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

import pickle
import os
import time
import re
import PSConfig

class PSPatch(object):
    _ext = '.pspatch'
    _usr_patch_mods_file = 'user.psmods'
    _data_model = {'NAME':"",'AUTHOR':"",'CREATION_DATE':"",'VERSION':-1,'TYPE':"",'ID':-1,'MODIFIED':False,'PACKAGE':""}

    def __init__(self, filepath, metadata=None):
        self._METADATA = dict(PSPatch._data_model)
        self._BASEDIR = u""
        self._SCRIPT = ""
        self._MOD_SCRIPT = ""
        self._PRESETS = {}
        self._USER_PRESETS = {}
        self._tmp_file_path = lambda: os.path.join(self._BASEDIR, "_tmp_"+self._METADATA['NAME']+'.py')
        self._usr_patch_mods_path = lambda: os.path.join(self._BASEDIR, PSPatch._usr_patch_mods_file)

        path, ext = os.path.splitext(filepath)
        if ext == PSPatch._ext:
            self._initPatch(filepath)
        elif ext == '.py':
            if metadata is not None:
                self._createPatch(filepath, metadata)
            else:
                raise AttributeError, "metadata attribute must be specified when creating a PSPatch object from a '.py' script"
        else:
            raise NameError, "Unsupported file type in PSPatch"

    def __del__(self):
        if os.path.exists(self._tmp_file_path()):
            os.remove(self._tmp_file_path())

    def _openUserMods(self):
        if os.path.exists(self._usr_patch_mods_path()):
            with open(self._usr_patch_mods_path(), 'rb') as f:
                data = pickle.load(f)
                if 'MOD_SCRIPT' in data:
                    self._MOD_SCRIPT = data['MOD_SCRIPT']
                if 'USER_PRESETS' in data:
                    self._USER_PRESETS = data['USER_PRESETS']

    def _writeUserMods(self):
        data = {}
        if self._USER_PRESETS:
            data['USER_PRESETS'] = self._USER_PRESETS
        if self._MOD_SCRIPT != "":
            data['MOD_SCRIPT'] = self._MOD_SCRIPT
        if data:
            with open(self._usr_patch_mods_path(), 'wb') as f:
                pickle.dump(data, f, 2)
        else:
            if os.path.exists(self._usr_patch_mods_path()):
                os.remove(self._usr_patch_mods_path())

    def _initPatch(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                patch = pickle.load(f)
            self._METADATA = patch['METADATA']
            self._SCRIPT = patch['SCRIPT']
            self._PRESETS = patch['PRESETS']
            self._BASEDIR = unicode(os.path.split(filepath)[0])
            self._openUserMods()
        else:
            raise IOError, "PSPatch._openPatch: path does not exist"

    def _createPatch(self, filepath, metadata):
        with open(filepath, 'r') as f:
            script = f.readlines()
            preset = None
            # parse and cleanup file
            for i, line in enumerate(script):
                if line == PSConfig.PATCH_BANNER + '\n':
                    pass
                elif line == PSConfig.PRESET_BANNER + '\n':
                    preset = script[i:-1]
                    break
                else:
                    self._SCRIPT += line
        # clean up extra new lines
        for i in range(len(self._SCRIPT)-1, 0, -1):
            if self._SCRIPT[i] != '\n':
                self._SCRIPT = self._SCRIPT[0:i+1]
                break

        # copy valid metadata
        for key in self._METADATA:
            if key in metadata:
                if type(metadata[key]) == type(self._METADATA[key]):
                    self._METADATA[key] = metadata[key]
                else:
                    raise TypeError, "Bad metadata type for '%s'" % key
        # making sure other metadata is valid at this point
        self._METADATA['VERSION'] = 0
        self._METADATA['CREATION_DATE'] = time.strftime("%d/%m/%Y")
        self._METADATA['ID'] = -1
        self._METADATA['MODIFIED'] = False

        if preset is not None:
            preset_string = ""
            for line in preset:
                if "pyosynth.setPreset" not in line:
                    preset_string += line
                else:
                    break
            exec(preset_string)
            self._PRESETS['Preset 1'] = preset

        self._BASEDIR = unicode(os.path.join(PSConfig.USR_LIB_PATH, self._removeSpecialChars(self._METADATA['NAME'])))
        if not os.path.exists(self._BASEDIR):
            os.mkdir(self._BASEDIR)
        else:
            raise IOError, "Folder already exists, cannot create patch with same name"
        self._writePatch()

    def _writePatch(self):
        patch_path = os.path.join(self._BASEDIR, self._METADATA['NAME']+PSPatch._ext)
        patch = {'METADATA':self._METADATA, 'SCRIPT':self._SCRIPT, 'PRESETS':self._PRESETS}
        with open(patch_path, 'wb') as f:
            pickle.dump(patch, f, 2)

    def _removeSpecialChars(self, text):
        text = re.sub('[^A-Za-z0-9 ]+', '', text)
        return text.replace(' ', '_')

    def createTempFile(self):
        with open(self._tmp_file_path(), 'w') as f:
            if self._METADATA['MODIFIED']:
                f.write(self._MOD_SCRIPT)
            else:
                f.write(self._SCRIPT)

    def deleteTempFile(self):
        if os.path.exists(self._tmp_file_path()):
            os.remove(self._tmp_file_path())

    def saveModifications(self):
        self._METADATA['MODIFIED'] = True
        self._MOD_SCRIPT = ""
        with open(self._tmp_file_path(), 'r') as f:
            script = f.readlines()
            # parse and cleanup file
            for i, line in enumerate(script):
                if line == PSConfig.PATCH_BANNER + '\n':
                    pass
                elif line == PSConfig.PRESET_BANNER + '\n':
                    break
                else:
                    self._MOD_SCRIPT += line
        # clean up extra new lines
        for i in range(len(self._MOD_SCRIPT) - 1, 0, -1):
            if self._MOD_SCRIPT[i] != '\n':
                self._MOD_SCRIPT = self._MOD_SCRIPT[0:i + 1]
                break

        self._writePatch()
        self._writeUserMods()

    def execScript(self, namespace):
        if self._METADATA['MODIFIED']:
            exec(self._MOD_SCRIPT, namespace)
        else:
            exec(self._SCRIPT, namespace)

    def revertToOriginalScript(self):
        self._MOD_SCRIPT = ""
        self._METADATA['MODIFIED'] = False
        self._writePatch()
        self._writeUserMods()

    def setID(self, id):
        assert type(id) == int, "PSPatch.setID : attribute id must be of type int"
        self._METADATA['ID'] = id

if __name__ == "__main__":
    test = 1
    if test==0:
        metadata = {'NAME': "Prime Sine", 'AUTHOR': "Alexandre Poirier", 'CREATION_DATE': "3/05/2017",
                    'TYPE': "Creative Synth", 'ID': 686}
        patch = PSPatch("/Users/alex/Desktop/PrimeSine.py", metadata)
        print "*********** Patch __dict__ ***********"
        print patch.__dict__
        print "*********** Patch Metadata ***********"
        for key in patch._METADATA:
            print "%s: %s" % (key, patch._METADATA[key])
        print "*********** Creating Temp File ***********"
        patch.createTempFile()
        print "*********** Saving Modifications ***********"
        patch.saveModifications()
        print "*********** Patch __dict__ ***********"
        print patch.__dict__
        print "*********** End of Test ***********"
    elif test==1:
        patch = PSPatch(os.path.join(PSConfig.USR_LIB_PATH,'Prime_Sine','Prime Sine.pspatch'))
        print "*********** Patch __dict__ ***********"
        print patch.__dict__
        print "*********** Patch Metadata ***********"
        for key in patch._METADATA:
            print "%s: %s" % (key, patch._METADATA[key])
        print "*********** Delete Temp File ***********"
        patch.deleteTempFile()
        print "*********** End of Test ***********"
