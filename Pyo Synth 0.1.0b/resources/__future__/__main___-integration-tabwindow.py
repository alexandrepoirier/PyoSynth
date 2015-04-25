from pyo import Metro, TrigFunc
from interface import *
import _core, tools, tabWindow
import pprint

class PyoSynth(wx.Frame):
    def __init__(self, server, namespace, chnl=0, poly=3, numControls=16):
        #calcul la grandeur du frame
        size = self._getSize(numControls)
        fstyle = wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX)
        wx.Frame.__init__(self, parent=None, id=-1, title="Pyo Synth - Untitled patch", pos=(100,100), size=size, style=fstyle)
        
        #Variables generales
        self.server = server
        self.script_namespace = namespace
        self._title = "Untitled patch"
        self._last_changed = None
        self.warningWindowPos = (self.GetSize()[0]/2-50,config.UNIT_SIZE[1]-5+config.SETUP_PANEL_HGT)
        
        #midi
        self.midiKeys = _core.MidiKeys(chnl, poly)
        
        #PatchWindow
        self.patchWindow = PatchWindow(self, namespace)
        
        #Menu panel
        self.menu_panel = MenuPanel(self, (0,0), (size[0],config.SETUP_PANEL_HGT), namespace)
        self.menu_panel.setAdsrCallbacks(self.midiKeys.getAdsrCallbacks())
        self.menu_panel.setAdsrValues(self.midiKeys.getAdsrValues())
        
        #Tab Window for editor and tools
        self._createTabWindow()
        
        #Status bar
        y = config.UNIT_SIZE[1]*self.rows+config.SETUP_PANEL_HGT+self.tab_win.GetSize()[1]
        self.status_bar = StatusBarPanel(self, (0,y), (size[0],config.STATS_BAR_HGT), self.server.getNchnls())
        server._server.setAmpCallable(self.status_bar.vu_meter)
        
        #ParamBoxes
        self.boxes_list = []
        self._createBoxes(numControls)

        #server setup
        self.serverSetupPanel = ServerSetupPanel(self, server)
        self.menu_panel.setServerPanel(self.serverSetupPanel)
        
        #update the quick info zone
        self.menu_panel.snd_card_ctrl.DoSetText(self.serverSetupPanel.getOutputInterface())
        self.menu_panel.updateSampRateBufSizeTxt()
        
        #Rafraichissement ecran des valeurs
        self.rate = Metro(config.REFRESH_RATE)
        self.trig_func = TrigFunc(self.rate, self._refresh)
        
        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        self.Bind(EVT_INTERFACE_CHANGED, self.updateInterfaceText)
        self.Bind(EVT_SAMP_RATE_CHANGED, self.updateSampRateBfsText)
        self.Bind(EVT_BUFSIZE_CHANGED, self.updateSampRateBfsText)
        self.Bind(EVT_NCHNLS_CHANGED, self.updateNchnls)
        self.Bind(buttons.EVT_BTN_RUN, self._prepareToRunScript)

    def __getitem__(self, i):
        return self.midiKeys[i]
    
    def OnQuit(self, evt):
        self.server.stop()
        time.sleep(.5)
        self.patchWindow.Destroy()
        self.Destroy()

    def OnMove(self, evt):
        if hasattr(self, 'warningWindow'):
            if isinstance(self.warningWindow, wx.Frame):
                self.warningWindow.SetPosition(self.GetPosition()+self.warningWindowPos)
        if self.patchWindow.IsShown():
            self.patchWindow._setPosition()
        
    def _refresh(self):
        for box in self.boxes_list:
            box.Refresh()
        
    def _getSize(self, num):
        self.rows = int(math.ceil((num)/float(config.NB_ELEM_ROW)))
        if self.rows>1:
            height = self.rows*config.UNIT_SIZE[1]+22+config.STATS_BAR_HGT+config.SETUP_PANEL_HGT+config.TAB_WIN_HGT
            width = config.UNIT_SIZE[0]*config.NB_ELEM_ROW+config.WHEELS_BOX_WIDTH
        else:
            height = config.UNIT_SIZE[1]+22+config.STATS_BAR_HGT+config.SETUP_PANEL_HGT+config.TAB_WIN_HGT
            width = (num)*config.UNIT_SIZE[0]+config.WHEELS_BOX_WIDTH
            
        return (width,height)
        
    def _prepareToRunScript(self, evt):
        """
        Demarre le metronome seulement si en mode running.
        S'assure que le midiKeys focntionne si le serveur a change de parametres.
        """
        #to do before running the script
        if evt.IsRunning():
            if self.serverSetupPanel.hasChanged():
                self.midiKeys.reinit()
                self.boxes_list[0].bend_obj = self.midiKeys['bend']
                self.boxes_list[0].mod_obj = self.midiKeys['mod']
                self.rate = Metro(config.REFRESH_RATE)
                self.trig_func = TrigFunc(self.rate, self._refresh)
                self.menu_panel.reinit()
                self.spectrum.reinit(None, self.server.getSamplingRate(), nchnls=self.server.getNchnls())
                self.serverSetupPanel.resetChangeFlag()
            self.status_bar.rec_btn.enable()
            self.rate.play()
        else:
            self.status_bar.rec_btn.disable()
            self.rate.stop()
            self.spectrum.stop()
            #removing pyo objects from the PatchWindow
            self.patchWindow.clearObjects()
            #removing existing links between MidiControls and PyoObjs
            self.removeLinks()
        #actually running the script
        self.menu_panel._runScript(evt)
        #to do after running the script
#        if evt.IsRunning():
#            if 'mix' in self.script_namespace:
#                self.spectrum.setInput(self.script_namespace['mix'])
#                self.spectrum.start()
        
    def _createTabWindow(self):
        y = config.UNIT_SIZE[1]*self.rows+config.SETUP_PANEL_HGT
        self.tab_win = tabWindow.PSTabWindow(self, (0,y), (self.GetSize()[0],config.TAB_WIN_HGT))
        self.editor = self.tab_win.addTab("Code editor")
        self.anal = self.tab_win.addTab("Analysis tools")
        #scope
        #self.scope = tools.PSScopeWrapper(self.tab_win,(110,18),(500,200), None, nchnls=self.server.getNchnls())
        #self.tab_win.addElementToTab(self.scope, self.anal)
        #spectrum
        self.spectrum = tools.PSSpectrumWrapper(self.tab_win,(620,18),(500,200), None, self.server.getSamplingRate(), nchnls=self.server.getNchnls())
        self.tab_win.addElementToTab(self.spectrum, self.anal)
        
        
    def _createBoxes(self, num):
        margin = config.WHEELS_BOX_WIDTH
        
        #creation boite de modulation et pitch bend
        self.boxes_list.append(WheelsBox(self, self.midiKeys['bend'], self.midiKeys['mod'], (0,config.SETUP_PANEL_HGT), config.UNIT_SIZE[1]*self.rows))
        
        for i in range(self.rows):
            for j in range(num):
                if j==config.NB_ELEM_ROW:
                    break
                if j+i*config.NB_ELEM_ROW < num:
                    ctl = j+i*config.NB_ELEM_ROW+1
                    self.boxes_list.append(ParamBox(self,
                                                    (config.UNIT_SIZE[0]*j+margin, config.UNIT_SIZE[1]*i+config.SETUP_PANEL_HGT),
                                                    config.UNIT_SIZE,
                                                    ["Unused", self.midiKeys.ctl_list[ctl]]))
            
    def _pauseMidiControl(self, ctlnum):
        index = self.midiKeys.getIndexFromCtlNumber(ctlnum)
        self.midiKeys.ctl_list[index].pause(self.script_namespace)
        
    def _resumeMidiControl(self, ctlnum):
        index = self.midiKeys.getIndexFromCtlNumber(ctlnum)
        self.midiKeys.ctl_list[index].resume(self.script_namespace)
        
    def addObject(self, name):
        self.patchWindow.addObject(name)
        
    def removeLinks(self):
        for box in self.boxes_list:
            box.unlink(self.script_namespace)
    
    def enableChildren(self, enable):
        list = self.GetChildren()
        for child in list:
            child.Enable(enable)
            
    def setScale(self, ctl, min, max):
        self.midiKeys.setScale(ctl, min, max)
            
    def setExp(self, ctl, value):
        self.midiKeys.setExp(ctl, value)
            
    def setPort(self, ctl, value):
        self.midiKeys.setPort(ctl, value)

    def savePreset(self, path):
        preset = {}
        preset[0] = {}
        preset[0]['master'] = self.status_bar.vol_slider.getValue()
        preset[0]['adsr'] = self.midiKeys.getAdsrValues()
        preset[0]['adsr_ctlnums'] = self.menu_panel.getAdsrCtlNums()
        for i in range(1, len(self.boxes_list)):
            if not self.boxes_list[i].IsUnused():
                preset[i] = {}
                preset[i]['name'] = self.boxes_list[i].getText()
                preset[i]['min'] = self.midiKeys.getMin(i)
                preset[i]['max'] = self.midiKeys.getMax(i)
                preset[i]['exp'] = self.midiKeys.getExp(i)
                preset[i]['port'] = self.midiKeys.getPort(i)
                preset[i]['prec'] = self.boxes_list[i].val_prec
                preset[i]['attr'] = self.midiKeys.getParamName(i)
                preset[i]['ctlnum'] = self.boxes_list[i].ctl_num
                val = self.midiKeys.getValue(i)
                thresh = float("."+"0"*preset[i]['prec']+"1")
                if val <= preset[i]['min']+thresh:
                    preset[i]['val'] = None
                elif val > preset[i]['max']:
                    preset[i]['val'] = preset[i]['max']
                else:
                    preset[i]['val'] = val
        self.writePreset(path, preset)
        
    def writePreset(self, path, dict):
        try:
            f = open(path, 'r+')
        except IOError, e:
            ##Affichage du message d'avertissement
            self.warningWindow = WarningWindow(self, self.GetPosition()+self.warningWindowPos, "Could not save the patch...")
            self.warningWindow.ShowWindow()
            wx.CallLater(2000,self.warningWindow.destroy)
        else:
            script = f.readlines()
            for i, line in enumerate(script):
                if line == config.PRESET_BANNER+"\n":
                    script = script[0:i]
                    break
        finally:
            while script[-1]=='\n':
                del script[-1]
            f.seek(0)
            if config.PATCH_BANNER+"\n" not in script:
                script.insert(0, config.PATCH_BANNER+"\n")
            f.writelines(script)
            f.write("\n\n\n"+config.PRESET_BANNER+"\n")
            f.write("preset = ")
            pprint.pprint(dict, f)
            f.write("\npyosynth.setPreset(preset)")
            f.close()
            ##Affichage du message d'avertissement
            self.warningWindow = WarningWindow(self, self.GetPosition()+self.warningWindowPos, "Patch saved")
            self.warningWindow.ShowWindow()
            wx.CallLater(2000,self.warningWindow.destroy)

    def setPreset(self, preset):
        if 0 in preset:
            elem = preset.pop(0)
            self.menu_panel.setAdsrValues(elem['adsr'])
            self.menu_panel.setAdsrCtlNums(elem['adsr_ctlnums'])
            master = elem['master']
            if master <= 1 and master >= 0:
                self.server.amp = master
                self.status_bar._setMasterVolSlider(master)
            else:
                self.server.amp = .8
                self.status_bar._setMasterVolSlider(.8)
        valuesDict = {} #contains all the values for the MatchMode
        for key in preset:
            self.boxes_list[key].enable(preset[key]['name'])
            self.boxes_list[key].val_prec = preset[key]['prec']
            self.midiKeys.setScale(key, preset[key]['min'], preset[key]['max'])
            self.midiKeys.setExp(key, preset[key]['exp'])
            self.midiKeys.setPort(key, preset[key]['port'])
            try:
                if preset[key]['attr'] != None: self._makeConnection(key, preset[key]['attr'])
            except (TypeError,NameError), e:
                print "PresetError : ", e
            else:
                val = preset[key]['val']
                if val != None:
                    valuesDict[key] = val
        self.setPresetValues(valuesDict)
            
    def _makeConnection(self, ctl, attr):
        obj_name = attr.split('.')[0]
        if len(obj_name) == 1:
            raise TypeError, "Object reference passed in preset for MidiControl no.%d. Should be a reference to an attribute of an object." % ctl
        elif obj_name not in self.script_namespace:
            raise NameError, "The object named %s was not found in the script and the connection to MidiControl no.%d couldn't be made." % (obj_name,ctl)
        else:
            exec attr+"= self.boxes_list[ctl].getMidiControl()" in self.script_namespace, locals()

    def quickPreset(self, dict):
        for key in dict:
            if isinstance(dict[key], list):
                self.boxes_list[key].enable(dict[key][0])
                self.boxes_list[key].val_prec = dict[key][1]
            else:
                self.boxes_list[key].enable(dict[key])
                
    def setPresetValues(self, preset):
        """
        Permet de sauvegarder un son en gardant les valeurs
        de tous les ParamBox en memoire.
        
        L'attribut preset doit etre un dictionnaire avec le format suivant:
            preset = {numero du controleur:valeur du controleur}
        """
        self.i = 0
        self.preset = preset
        
        ##Affichage du message d'avertissement
        self.warningWindow = WarningWindow(self, self.GetPosition()+self.warningWindowPos, "Matching preset values...")
        self.warningWindow.ShowWindow()
        
        self.nextPreset()
                
    def nextPreset(self):
        if len(self.preset) > 0:
            self.enableChildren(False)
            self.i += 1
            while True:
                if self.i in self.preset:
                    self.boxes_list[self.i].Enable(True)
                    self.boxes_list[self.i].matchValue(self.preset.pop(self.i))
                    break
                else:
                    self.i += 1
        else:
            self.enableChildren(True)
            self.warningWindow.SetText("Done!")
            self.warningWindow.destroy()
            del self.i
            del self.preset
            
    def updateInterfaceText(self, evt):
        self.menu_panel.updateInterfaceTxt()
        
    def updateSampRateBfsText(self, evt):
        self.menu_panel.updateSampRateBufSizeTxt()
        
    def updateNchnls(self, evt):
        self.menu_panel.updateSampRateBufSizeTxt()
        self.status_bar.setNchnls(self.server.getNchnls())