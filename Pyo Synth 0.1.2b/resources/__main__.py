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

from PSInterface import *
import PSUtils
import PSAudio
import pprint
import pickle
import os
import time
import PSConfig
import re
import gc

if PSConfig.PLATFORM == 'linux2':
    from pyo64 import Metro, TrigFunc, class_args, CallAfter
else:
    from pyo import Metro, TrigFunc, class_args, CallAfter


class PyoSynth(wx.Frame):
    def __init__(self, server, namespace, chnl=0, numControls=PSConfig.PYOSYNTH_PREF['num_ctls']):
        size = self._getSize(numControls)
        fstyle = wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX)
        wx.Frame.__init__(self, parent=None, id=-1, title="Pyo Synth - v%s" % PSConfig.VERSIONS['Pyo Synth'], pos=(200, 200), size=size, style=fstyle)
        self._base_panel = wx.Panel(self, id=-1, pos=(0,0), size=size)

        # Variables generales
        self._server_ = server
        self.script_namespace = namespace
        self.USER_MATCH_MODE = True # set through the user interface, determines if math mode will be used
        self.AUTO_MATCH_MODE = True # set by the code, determines when match mode will be used
        self.MATCHING_VALUES = False # match mode is in progress?
        self.FIRST_EXEC = True
        self._FUNCTIONS_SET = False
        self._EXPORTING = False
        self._PRESET_CHANGED_KEYS_MODE = False
        self.FILE_DLG_OPEN = False
        # dernier ParamBox a avoir ete modifie
        self._last_changed = None
        self.LAST_EXC_SCRIPT = ""
        # petite fenetre qui affiche des messages d'avertissement
        self.warningWindow = None
        self.warningWindowPos = ((self.GetSize()[0]/2) - (WarningWindow.min_size[0]/2),
                                 PSConfig.SETUP_PANEL_HGT + PSConfig.UNIT_SIZE[1] - 5)
        # variable pour stocker le chemin d'acces au script
        self._script_path = ""
        # variable d'etat du script
        self.IS_RUNNING = False
        # contient tous les objets pyo presentement en execution
        self.pyo_objs = {}
        # contient toutes les variables declarees dans le script en execution
        self.script_vars = {}
        self._saveValCount = 0 # compte le nombre de fois que saveValuesInScript est appele
        # garde l'id des objets pouvant recevoir le focus pourle clavier
        self._kb_focus_white_list = []
        
        # midi
        self.midiKeys = PSAudio.MidiKeys(numControls, chnl)
        # Clipping monitor
        self.clip_monitor = PSAudio.ClipMonitor(.99, self.OnClip, 200)
        # clavier virtuel
        self.virtual_keys = VirtualKeyboard(PSConfig.DEFAULT_MAP_STYLE)
        
        # PatchWindow
        self.patchWindow = PatchWindow(self, namespace)
        # fenetre qui affiche le stdout
        self.terminal_win = PSTerminal(self, namespace)
        self._addToWhiteList(self.terminal_win.getWhiteListItems())
        # fenetre qui affiche les erreurs des scripts
        self.exc_win = PSExceptionWindow(self)
        self._addToWhiteList(self.exc_win.getWhiteListItems())
        
        # Menu panel
        self.menu_panel = MenuPanel(self, (0,0), (size[0], PSConfig.SETUP_PANEL_HGT))
        self.menu_panel.setAdsrCallbacks(self.midiKeys.getAdsrCallbacks())
        self.menu_panel.setAdsrValues(self.midiKeys.getAdsrValues())

        # Status bar
        y = PSConfig.UNIT_SIZE[1] * self.rows + PSConfig.SETUP_PANEL_HGT
        self.status_bar = StatusBarPanel(self, (0,y), (size[0], PSConfig.STATS_BAR_HGT), self._server_.getNchnls())
        server._server.setAmpCallable(self.status_bar.vu_meter)

        # ParamBoxes
        self._createBoxes(numControls)

        # server setup
        self.serverSetupPanel = ServerSetupPanel(self, server)
        self.menu_panel.setServerPanel(self.serverSetupPanel)
        
        # update the quick info zone
        self.menu_panel.snd_card_ctrl.DoSetText(self.serverSetupPanel.getOutputInterface())
        self.menu_panel.updateSampRateBufSizeTxt()
        
        # Rafraichissement ecran des valeurs
        self.rate = Metro(PSConfig.REFRESH_RATE)
        self.trig_func = TrigFunc(self.rate, self._mainRefreshLoop)

        
        # MENU ITEMS
        menubar = wx.MenuBar()
        
        filemenu = wx.Menu()
        filemenu.Append(100, "Save Script\tCtrl+S",
                        "Adds parameters and values at the end of the original script for easy callaback.",wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.savePresetByEvent, id=100)
        filemenu.Append(101, "Save Script As\tCtrl+Shift+S",
                        "Save script to a new location and add parameters and values at the end of the script for easy callaback.",wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.savePresetAsByEvent, id=101)
        filemenu.Append(106, "Save Log", "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self._saveTerminalLogByEvent, id=106)
        filemenu.Append(102, "Open Script\tCtrl+O",
                        "Open a pyo script for execution within PyoSynth.",wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self._openDialogByEvent, id=102)
        filemenu.Append(105, "Open Most Recent Script\tCtrl+Shift+O",
                        "Open most recent script from list.", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self._setMostRecentScriptByEvent, id=105)
        openrecent = wx.Menu()
        self._buildRecentScriptsMenu(openrecent, id_start=400)
        filemenu.AppendMenu(102, "Open Recent", openrecent)
        filemenu.AppendSeparator()
        self.exportitem = filemenu.Append(103, "Export as Samples\tCtrl+E",
                                          "Export this patch with current parameters as samples.",wx.ITEM_NORMAL)
        self.exportitem.Enable(False)
        self.Bind(wx.EVT_MENU, self._exportScriptByEvent, id=103)
        self.save_values_script = filemenu.Append(104, "Save values in script\tAlt+S",
                                                  "Saves the values of all used ParamBox directly in the script.", wx.ITEM_NORMAL)
        self.save_values_script.Enable(False)
        self.Bind(wx.EVT_MENU, self.saveValuesInScriptByEvent, id=104)
        #filemenu.Append(wx.ID_PREFERENCES, "Preferences\tCtrl+P", "", wx.ITEM_NORMAL)
        #self.Bind(wx.EVT_MENU, self.openPreferencesWinByEvent, id=wx.ID_PREFERENCES)
        menubar.Append(filemenu, "&File")
        
        mainmenu = wx.Menu()
        self.runitem = mainmenu.Append(200, "Run\tCtrl+R","",wx.ITEM_NORMAL)
        self.runitem.Enable(False)
        self.Bind(wx.EVT_MENU, self.menu_panel.btn_run.ToggleState, id=200)
        self.metroitem = mainmenu.Append(201, "Click\tCtrl+C","",wx.ITEM_NORMAL)
        self.metroitem.Enable(False)
        self.Bind(wx.EVT_MENU, self.menu_panel.metro.OnClick, id=201)
        mainmenu.Append(202, "Open Error Log\tCtrl+L", "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.exc_win.toggle, id=202)
        mainmenu.Append(206, "Open Python Interpreter\tCtrl+T", "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.terminal_win.toggle, id=206)
        self.reset_boxes_item = mainmenu.Append(205, "Reset all boxes\tCtrl+B")
        self.Bind(wx.EVT_MENU, self._resetAllBoxesByEvent, id=205)
        mainmenu.Append(207, "Performance Mode", "No background images will be drawn when enabled.", wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self._setPerformanceMode, id=207)
        mainmenu.AppendSeparator()
        self.virtual_keys_item = mainmenu.Append(203, "Use Computer keyboard as input\tCtrl+K", "", wx.ITEM_CHECK)
        self.virtual_keys_item.Enable(False)
        self.Bind(wx.EVT_MENU, self._toggleComputerKeyboardByEvent, id=203)
        self.match_mode_item = mainmenu.Append(204, "Match preset value\tCtrl+P", "", wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.toggleUserMatchModeByEvent, id=204)
        self.match_mode_item.Check(True)
        menubar.Append(mainmenu, "&Menu")

        midimenu = wx.Menu()
        keys_mode_text = midimenu.Append(300, "-- Keyboard Mode --", "", wx.ITEM_NORMAL)
        keys_mode_text.Enable(False)
        self.normal_keys_mode_item = midimenu.Append(301, "Normal\tCtrl+Shift+1", "", wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self._cycleKeyboardModesByEvent, id=301)
        self.sustain_keys_mode_item = midimenu.Append(302, "Normal + Sustain\tCtrl+Shift+2", "", wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self._cycleKeyboardModesByEvent, id=302)
        self.mono_keys_mode_item = midimenu.Append(303, "Mono\tCtrl+Shift+3", "", wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU, self._cycleKeyboardModesByEvent, id=303)

        # mono types menu
        mono_type_menu = wx.Menu()
        self._BASE_ID_MONO_TYPE = 304
        self._mono_type_items_list = []
        self._mono_type_items_list.append(mono_type_menu.Append(self._BASE_ID_MONO_TYPE, "Recent Note Proprity", "", wx.ITEM_RADIO))
        self._mono_type_items_list.append(mono_type_menu.Append(self._BASE_ID_MONO_TYPE+1, "Lowest Note Priority", "", wx.ITEM_RADIO))
        self._mono_type_items_list.append(mono_type_menu.Append(self._BASE_ID_MONO_TYPE+2, "Highest Note Priority", "", wx.ITEM_RADIO))
        self.Bind(wx.EVT_MENU, self._cycleMonoModesByEvent, id=self._BASE_ID_MONO_TYPE)
        self.Bind(wx.EVT_MENU, self._cycleMonoModesByEvent, id=self._BASE_ID_MONO_TYPE + 1)
        self.Bind(wx.EVT_MENU, self._cycleMonoModesByEvent, id=self._BASE_ID_MONO_TYPE + 2)
        midimenu.AppendMenu(-1, "Mono Mode", mono_type_menu)
        # end mono types menu

        midimenu.AppendSeparator()
        self._buildMidiProfileMenu(midimenu, id_start=600)
        self._updateMidiProfileMenu()
        self._setLastMidiProfile() # attemps to set to last profile used if any
        midimenu.AppendSeparator()
        self._buildPolyphonyMenu(midimenu, id_start=800)
        self._buildPitchBendMenu(midimenu, id_start=900)
        menubar.Append(midimenu, "&MIDI")

        funcmenu = wx.Menu()
        self._buildFunctionsMenu(funcmenu, id_start=700)
        menubar.Append(funcmenu, "&Functions")
        
        helpmenu = wx.Menu()
        helpmenu.Append(wx.ID_ABOUT, "About","",wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU,self._about, id=wx.ID_ABOUT)
        helpmenu.Append(500, "Help\tCtrl+?","",wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU,self._help, id=500)
        menubar.Append(helpmenu, "&Help")
        
        self.SetMenuBar(menubar)
        # FIN MENU ITEMS
        
        # section about
        self.aboutinfo = wx.AboutDialogInfo()
        self.aboutinfo.SetCopyright(u"\xa92015-2017 Alexandre Poirier")
        self.aboutinfo.SetDescription("Built: %s\n\nPyo Synth is an interface to help with live manipulation of synthesizer scripts written with pyo." % PSConfig.BUILD_DATE)
        self.aboutinfo.SetDevelopers(["Alexandre Poirier"])
        self.aboutinfo.SetName("Pyo Synth")
        self.aboutinfo.SetVersion(PSConfig.VERSIONS['Pyo Synth'])
        
        # binding events
        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        self.Bind(EVT_INTERFACE_CHANGED, self._updateInterfaceTextByEvent)
        self.Bind(EVT_SAMP_RATE_CHANGED, self._updateSampRateBfsTextByEvent)
        self.Bind(EVT_BUFSIZE_CHANGED, self._updateSampRateBfsTextByEvent)
        self.Bind(EVT_NCHNLS_CHANGED, self._updateNchnlsByEvent)
        self.Bind(EVT_VIRTUAL_KEYS_CHANGED, self._onVirtualKeysChangeByEvent)
        self.Bind(PSButtons.EVT_BTN_RUN, self._toggleRunStateByEvent)
        self.Bind(EVT_SAVE_TRACK, self._createSaveTrackDialogByEvent)
        self.menu_panel.btn_open.Bind(PSButtons.EVT_BTN_CLICKED, self._openDialogByEvent)
        self.menu_panel.btn_save.Bind(PSButtons.EVT_BTN_CLICKED, self.savePresetByEvent)
        self.menu_panel._attackKnob.Bind(PSControls.EVT_TOGGLE_CONTROL, self._onToggleADSRMidiControlByEvent)
        self.menu_panel._decayKnob.Bind(PSControls.EVT_TOGGLE_CONTROL, self._onToggleADSRMidiControlByEvent)
        self.menu_panel._sustainKnob.Bind(PSControls.EVT_TOGGLE_CONTROL, self._onToggleADSRMidiControlByEvent)
        self.menu_panel._releaseKnob.Bind(PSControls.EVT_TOGGLE_CONTROL, self._onToggleADSRMidiControlByEvent)

        self._setPreferences()
        # hack to get all widgets to refresh and draw their parents background
        wx.CallLater(100, self.Refresh)
        wx.CallLater(150, self.Refresh)
    #end __init__

##### --------------------
##### INTERFACE INTERFACE
##### --------------------
    def OnQuit(self, evt):
        evt.Skip()
        self._saveRecentScriptsList()
        self._savePyoSynthPref()
        if self._server_.getIsStarted():
            self._server_.stop()
            time.sleep(.2)
        self._server_.shutdown()
        time.sleep(.5)
        for box in self.boxes_list:
            box.OnQuit(evt)
        self.patchWindow.Destroy()
        self.exc_win.Destroy()
        self.Destroy()

    def OnMove(self, evt):
        evt.Skip()
        if hasattr(self, 'warningWindow'):
            if isinstance(self.warningWindow, wx.Frame):
                self.warningWindow.SetPosition(self.GetPosition()+self.warningWindowPos+(0,PSConfig.BANNER_OFFSET))
        if self.patchWindow.IsShown():
            self.patchWindow._setPosition()
        if self.status_bar.tracks_window.IsShown():
            self.status_bar.tracks_window._setPosition(self.GetPosition())
        for box in self.boxes_list:
            box.OnMove(evt)

    def OnClip(self):
        self.status_bar.clip_light.turnOn()

    def Show(self):
        self._printPyoVersion()
        PSUtils.printMessage("Ready", 0)
        return wx.Frame.Show(self)

    def _about(self, evt):
        wx.AboutBox(self.aboutinfo)
        
    def _help(self, evt):
        os.system('open ' + PSConfig.HELP_DOC.replace(' ', '\ '))

    def _updateInterfaceTextByEvent(self, evt):
        self.menu_panel.updateInterfaceTxt()

    def _updateSampRateBfsTextByEvent(self, evt):
        self.menu_panel.updateSampRateBufSizeTxt()

    def _updateNchnlsByEvent(self, evt):
        self.menu_panel.updateSampRateBufSizeTxt()
        self.status_bar.setNchnls(self._server_.getNchnls())

    def _onToggleADSRMidiControlByEvent(self, evt):
        """
        Mets les controles midi en pause pendant le controle des boutons ADSR.
        Appele par les boutons de l'enveloppe ADSR quand le mode midi est active par dbl-click.
        """
        index = self.midiKeys.getIndexFromCtlNumber(evt.GetCtlNumber())
        if index == -1:
            return
        if evt.GetIsControlled():
            self.midiKeys.ctl_list[index].pause(self.script_namespace)
        else:
            self.midiKeys.ctl_list[index].resume(self.script_namespace)

    def _onVirtualKeysChangeByEvent(self, evt):
        if self.serverSetupPanel.isUsingVirtualKeys():
            self.midiKeys.setVirtualKeyboardMode(self.virtual_keys)
            self.virtual_keys_item.Enable(True)
            self.boxes_list[0].setUnused(True)
            PSUtils.printMessage("Computer keyboard selected as MIDI input (Virtual Keyboard)", 1)
        else:
            self.midiKeys.disableVirtualKeyboardMode()
            self.boxes_list[0].setUnused(False)
            if self.virtual_keys_item.IsChecked():
                self._base_panel.Unbind(wx.EVT_KEY_DOWN)
                self._base_panel.Unbind(wx.EVT_KEY_UP)
                self.virtual_keys_item.Check(False)
            self.virtual_keys_item.Enable(False)
            PSUtils.printMessage("Virtual Keyboard disabled", 1)

    def _toggleComputerKeyboardByEvent(self, evt):
        if evt.IsChecked():
            self._base_panel.Bind(wx.EVT_KEY_DOWN, self.virtual_keys.OnKeyDown)
            self._base_panel.Bind(wx.EVT_KEY_UP, self.virtual_keys.OnKeyUp)
            PSUtils.printMessage("Virtual Keyboard engaged", 1)
        else:
            self._base_panel.Unbind(wx.EVT_KEY_DOWN)
            self._base_panel.Unbind(wx.EVT_KEY_UP)
            PSUtils.printMessage("Virtual Keyboard disengaged", 1)

    def _setPolyphonyByEvent(self, evt):
        index = evt.GetId()-self._BASE_ID_POLY_MENU
        PSConfig.PYOSYNTH_PREF['poly'] = PSConfig.POLYPHONY_VALUES[index]
        PSUtils.printMessage("Polyphony changed to: %d" % PSConfig.PYOSYNTH_PREF['poly'], 1)
        self.midiKeys.setPoly(PSConfig.PYOSYNTH_PREF['poly'])
        self.status_bar._doSafeUpdatePolyValue(0, False)

    def _setPitchBendRangeByEvent(self, evt):
        index = evt.GetId()-self._BASE_ID_PBEND_MENU
        PSConfig.PYOSYNTH_PREF['bend_range'] = PSConfig.PITCH_BEND_VALUES[index]
        PSUtils.printMessage("Pitch bend range changed to: %.1f" % PSConfig.PYOSYNTH_PREF['bend_range'], 1)
        self.midiKeys.setBendRange(PSConfig.PYOSYNTH_PREF['bend_range'])

    def openPreferencesWinByEvent(self, evt):
        PSUtils.printMessage("Preferences coming soon...", 0)

    def toggleUserMatchModeByEvent(self, evt):
        self.USER_MATCH_MODE = evt.IsChecked()
        if evt.IsChecked():
            PSUtils.printMessage("Match mode enabled", 1)
        else:
            PSUtils.printMessage("Match mode disabled", 1)

    def _cycleKeyboardModesByEvent(self, evt):
        id = evt.GetId()
        if id == 301:
            if self.midiKeys.getKeyboardMode() != 0:
                self.midiKeys.setKeyboardMode(0)
                PSUtils.printMessage("Keyboard mode: Normal", 1)
        elif id == 302:
            if self.midiKeys.getKeyboardMode() != 1:
                self.midiKeys.setKeyboardMode(1)
                PSUtils.printMessage("Keyboard mode: Normal + Sustain", 1)
        elif id == 303:
            if self.midiKeys.getKeyboardMode() != 2:
                self.midiKeys.setKeyboardMode(2)
                PSUtils.printMessage("Keyboard mode: Mono", 1)

    def _cycleMonoModesByEvent(self, evt):
        i = evt.GetId()-self._BASE_ID_MONO_TYPE
        PSUtils.printMessage("Mono type changed to: %s Note Priority" % (['Most Recent', 'Lowest', 'Highest'][i]), 1)
        PSConfig.PYOSYNTH_PREF['mono_type'] = i
        self.midiKeys.setMonoType(i)

    def _resetAllBoxesByEvent(self, evt):
        if self.IS_RUNNING:
            dlg = wx.MessageDialog(self, "You're about to reset all boxes, you will lose all unsaved progress.",
                                   "Reset all boxes?",
                                   wx.YES_NO|wx.NO_DEFAULT|wx.CENTRE|wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO:
                return

        for box in self.boxes_list:
            box.disable(self.script_namespace)

    def _saveRecentScriptsList(self):
        with open(PSConfig.RECENT_SCRIPTS_PATH, 'w') as f:
            pickle.dump(PSConfig.RECENT_SCRIPTS, f)

    def _savePyoSynthPref(self):
        with open(PSConfig.PYOSYNTH_PREF_PATH, 'w') as f:
            pickle.dump(PSConfig.PYOSYNTH_PREF, f)

    def _saveTerminalLogByEvent(self, evt):
        try:
            name = 'pyosynth_log_%s.txt' % time.strftime("%d-%m-%y_%H-%M-%S")
            self.terminal_win._stdout_ctrl.SaveFile(os.path.join(PSConfig.HOME_PATH, name), 0)
        except:
            PSUtils.printMessage("Failed to save the log")
        else:
            PSUtils.printMessage("Log saved in user's home directory")

    def _buildRecentScriptsMenu(self, menu, id_start):
        for path in PSConfig.RECENT_SCRIPTS:
            menu.Append(id_start, path, "", wx.ITEM_NORMAL)
            self.Bind(wx.EVT_MENU, self._setScriptFromRecentMenuByEvent, id=id_start)
            id_start += 1
        menu.Append(id_start, "Clear history", "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.clearRecentScriptsByEvent, id=id_start)

    def clearRecentScriptsByEvent(self, evt):
        PSConfig.RECENT_SCRIPTS = []
        menu = evt.GetEventObject()
        items = menu.GetMenuItems()
        for item in items:
            if item.GetText() != "Clear history":
                menu.DeleteItem(item)

    def _mainRefreshLoop(self):
        self._updatePolyDisplayValue()
        for box in self.boxes_list:
            box.SmartRefresh()
        if self._canSetFocus():
            self._base_panel.SetFocus()

    def _canSetFocus(self):
        if self.FILE_DLG_OPEN:
            return False
        try:
            focus_id = self.FindFocus().GetId()
        except AttributeError: # if FindFocus returns None
            return True
        else:
            if self._base_panel.GetId() != focus_id:
                if focus_id in self._kb_focus_white_list:
                    return False
        return True

    def _setPerformanceMode(self, evt):
        """
        This mode is functional, but not so optimized right now.
        Performance gain is about 3% of cpu usage at the moment.
        Maybe getting rid of the BufferedPaintDC will increase efficiency in this mode.
        """
        state = evt.IsChecked()
        for box in self.boxes_list:
            box.setPerformanceMode(state)
            box.ForceRefresh()
        if state:
            self.status_bar.vu_meter.setRefreshSkip(4)
        else:
            self.status_bar.vu_meter.setRefreshSkip(2)

    def setAutoMatchMode(self, state):
        self.AUTO_MATCH_MODE = state

    def _getMatchMode(self):
        return self.USER_MATCH_MODE and self.AUTO_MATCH_MODE

    def _updatePolyDisplayValue(self, value=None):
        if value is None: self.status_bar.updatePolyValue(self.midiKeys.getTotalVoicesPlaying())
        else: self.status_bar.updatePolyValue(value)

    def _addToWhiteList(self, *args):
        for arg in args:
            if isinstance(arg, list):
                for elem in arg:
                    if isinstance(elem, int):
                        self._kb_focus_white_list.append(elem)
                    else:
                        raise TypeError, "int expected, got %s" % type(elem)
            elif arg not in self._kb_focus_white_list:
                if isinstance(arg, int):
                    self._kb_focus_white_list.append(arg)
                else:
                    raise TypeError, "int expected, got %s" % type(arg)

    def _removeFromWhiteList(self, *args):
        for arg in args:
            if isinstance(arg, list):
                for elem in arg:
                    try: self._kb_focus_white_list.remove(elem)
                    except: pass # elem not in list
            else:
                try: self._kb_focus_white_list.remove(arg)
                except: pass # arg not in list

    def _createSaveTrackDialogByEvent(self, evt):
        dlg = wx.FileDialog(
            self, message=evt.GetMessage(),
            defaultDir=evt.GetDefaultDir(),
            defaultFile=evt.GetDefaultFile(),
            style=evt.GetStyle()
        )

        self.FILE_DLG_OPEN = True
        if dlg.ShowModal() == wx.ID_OK:
            self.FILE_DLG_OPEN = False
            path = dlg.GetPath()
            # make sure the user didn't change the fileformat
            try:
                path,ext = path.rsplit('.', 1)
            except ValueError: # no extension
                pass
            finally: # add correct fileformat
                path += PSConfig.REC_FORMAT_DICT[PSConfig.REC_FORMAT]
            shutil.move(evt.GetTrackPath(), path)
            evt.GetEventObject()._removeTrack()

##### --------------------
##### INIT INIT INIT INIT
##### --------------------
    def _getSize(self, num):
        self.rows = int(math.ceil((num) / float(PSConfig.NB_ELEM_ROW)))
        if self.rows>1:
            height = self.rows * PSConfig.UNIT_SIZE[1] + 22 + PSConfig.STATS_BAR_HGT + PSConfig.SETUP_PANEL_HGT
            width = PSConfig.UNIT_SIZE[0] * PSConfig.NB_ELEM_ROW + PSConfig.WHEELS_BOX_WIDTH
        else:
            height = PSConfig.UNIT_SIZE[1] + 22 + PSConfig.STATS_BAR_HGT + PSConfig.SETUP_PANEL_HGT
            width = (num) * PSConfig.UNIT_SIZE[0] + PSConfig.WHEELS_BOX_WIDTH
            
        return (width,height)
        
    def _createBoxes(self, num):
        self.boxes_list = []
        margin = PSConfig.WHEELS_BOX_WIDTH
        
        #creation boite de modulation et pitch bend
        self.boxes_list.append(WheelsBox(self, self.midiKeys['bend'], self.midiKeys['mod'], (0, PSConfig.SETUP_PANEL_HGT), PSConfig.UNIT_SIZE[1] * self.rows))
        
        for i in range(self.rows):
            for j in range(num):
                if j==PSConfig.NB_ELEM_ROW:
                    break
                if j+i*PSConfig.NB_ELEM_ROW < num:
                    ctl = j+ i * PSConfig.NB_ELEM_ROW + 1
                    self.boxes_list.append(ParamBox(self,
                                                    (PSConfig.UNIT_SIZE[0] * j + margin, PSConfig.UNIT_SIZE[1] * i + PSConfig.SETUP_PANEL_HGT),
                                                    "Unused", self.midiKeys.ctl_list[ctl])
                                           )


    def _setPreferences(self):
        PSUtils.printMessage("Loading PyoSynth preferences...", 1)

        # setting poly
        self.midiKeys.setPoly(PSConfig.PYOSYNTH_PREF['poly'])
        self.status_bar._doSafeUpdatePolyValue(0, PSConfig.PYOSYNTH_PREF['poly'])
        # check corresponding item in menu
        for item in self._poly_menu_items_list:
            if item.GetText() == str(PSConfig.PYOSYNTH_PREF['poly']):
                item.Check(True)
        PSUtils.printMessage("Polyphony set to: %d" % PSConfig.PYOSYNTH_PREF['poly'], 1)

        # setting bend range
        self.midiKeys.setBendRange(PSConfig.PYOSYNTH_PREF['bend_range'])
        # check corresponding item in menu
        for item in self._pbend_menu_items_list:
            if item.GetText() == str(PSConfig.PYOSYNTH_PREF['bend_range']):
                item.Check(True)
        PSUtils.printMessage("Pitch bend range set to: %.1f" % PSConfig.PYOSYNTH_PREF['bend_range'], 1)

        # setting mono type
        PSUtils.printMessage("Mono type changed to: %s Note Priority" %
                           (['Most Recent', 'Lowest', 'Highest'][PSConfig.PYOSYNTH_PREF['mono_type']]), 1)
        self.midiKeys.setMonoType(PSConfig.PYOSYNTH_PREF['mono_type'])
        self._mono_type_items_list[PSConfig.PYOSYNTH_PREF['mono_type']].Check(True)

    def enableMenuItems(self):
        """
        Appele quand un script est selectionne pour la premiere fois.
        """
        self.runitem.Enable(True)
        self.exportitem.Enable(True)

    def _printPyoVersion(self):
        import __builtin__
        if hasattr(__builtin__, 'pyo_use_double'):
            if PSConfig.PLATFORM == 'linux2':
                if __builtin__.__dict__['pyo_use_double'] is True:
                    prec = "double"
                else:
                    prec = "single"
            else:
                if __builtin__['pyo_use_double'] is True:
                    prec = "double"
                else:
                    prec = "single"
        else:
            prec = "single"
        PSUtils.printMessage("pyo version {1}.{2}.{3} (uses {0} precision)".format(prec, *PSConfig.VERSIONS['pyo']), 0)

    def _buildPolyphonyMenu(self, menu, id_start):
        self._BASE_ID_POLY_MENU = id_start
        poly_menu = wx.Menu()
        self._poly_menu_items_list = []

        for i, val in enumerate(PSConfig.POLYPHONY_VALUES):
            self._poly_menu_items_list.append(poly_menu.Append(self._BASE_ID_POLY_MENU + i,
                                                               "%s" % PSConfig.POLYPHONY_VALUES[i], "", wx.ITEM_RADIO))
            self.Bind(wx.EVT_MENU, self._setPolyphonyByEvent, id=self._BASE_ID_POLY_MENU+i)
        menu.AppendMenu(-1, "Max Polyphony", poly_menu)

    def _buildPitchBendMenu(self, menu, id_start):
        self._BASE_ID_PBEND_MENU = id_start
        pbend_menu = wx.Menu()
        self._pbend_menu_items_list = []

        for i, val in enumerate(PSConfig.PITCH_BEND_VALUES):
            self._pbend_menu_items_list.append(
                pbend_menu.Append(self._BASE_ID_PBEND_MENU + i, "%s" % val, "", wx.ITEM_RADIO))
            self.Bind(wx.EVT_MENU, self._setPitchBendRangeByEvent, id=self._BASE_ID_PBEND_MENU + i)
        menu.AppendMenu(-1, "Pitch Bend Range (semitones)", pbend_menu)


##### ---------------
##### FUNCTIONS MENU
##### ---------------
    def _buildFunctionsMenu(self, menu, id_start):
        self._funcmenu_items = []
        self._functions_dict = {} # to be used when functions are set by the user
        for i in range(10):
            id = id_start+i
            self._funcmenu_items.append( menu.Append(id, "f%d - Unassigned\tAlt+%d" % (i+1, (i+1)%10), "", wx.ITEM_NORMAL) )
            self._funcmenu_items[i].Enable(False)

    def _setFunctions(self, flist):
        for i, elem in enumerate(flist):
            if i>10: break
            if isinstance(elem, tuple):
                if not callable(elem[0]) or not isinstance(elem[1], str):
                    self.exc_win.printException(self._script_path.rsplit("/", 1)[1], "Error in setFunctions() : Tuple must be as follows (function, string)\n")
                    return
                id = self._funcmenu_items[i].GetId()
                self._functions_dict[id] = elem[0]
                self.Bind(wx.EVT_MENU, self._functionsCallback, id=id)
                self._funcmenu_items[i].Enable(True)
                self._funcmenu_items[i].SetText("f%d - %s\tAlt+%d" % ( (i + 1), elem[1], (i+1)%10))
                PSUtils.printMessage("Function %d - '%s' set" % (i+1, elem[1]), 1)
            else:
                if not callable(elem):
                    self.exc_win.printException(self._script_path.rsplit("/", 1)[1],
                                                "Error in setFunctions() : argument must be a function or a tuple as follows (function, string)\n")
                    return
                id = self._funcmenu_items[i].GetId()
                self._functions_dict[id] = elem
                self.Bind(wx.EVT_MENU, self._functionsCallback, id=id)
                self._funcmenu_items[i].Enable(True)
                self._funcmenu_items[i].SetText("f%d - No name\tAlt+%d" % ((i + 1), (i+1)%10))
                PSUtils.printMessage("Function %d - No name set" % (i + 1), 1)

        self._FUNCTIONS_SET = True

    def _removeFunctionsBindings(self):
        for i, elem in enumerate(self._funcmenu_items):
            if elem.IsEnabled():
                self.Unbind(wx.EVT_MENU, id=elem.GetId())
                elem.Enable(False)
                elem.SetText("f%d - Unassigned\tAlt+%d" % (i+1, (i+1)%10))
        self._functions_dict.clear()
        self._FUNCTIONS_SET = False

    def _functionsCallback(self, evt):
        id = evt.GetId()
        func_name = evt.GetEventObject().FindItemById(id).GetText().rsplit('\t', 1)[0]
        try:
            PSUtils.printMessage("Executing '%s'" % func_name, 1)
            func_return = self._functions_dict[id]()
        except Exception:
            exc_type, exc_name, exc_tb = sys.exc_info()
            string = "Error when trying to excute '%s'\n" % func_name
            string += traceback.format_exc(exc_tb)
            self.exc_win.newException(self._script_path.rsplit('/', 1)[1], string)
        else:
            try: # tries to print the output
                PSUtils.printMessage("'%s' returned: %s" % (func_name, str(func_return)))
            except:
                pass

##### --------------
##### MIDI PROFILES
##### --------------
    def _buildMidiProfileMenu(self, midimenu, id_start):
        midi_profiles_text = midimenu.Append(-1, "-- Midi Profiles --", "", wx.ITEM_NORMAL)
        midi_profiles_text.Enable(False)

        self._BASE_ID_SAVE_PROFILE = id_start
        self._BASE_ID_DEL_PROFILE = id_start + PSConfig.MAX_SAVE_PROFILES
        self._BASE_ID_LOAD_PROFILE = id_start + PSConfig.MAX_SAVE_PROFILES * 2
        self._save_profile_items = []
        self._del_profile_items = []
        self._load_profile_items = []
        save_profile_menu = wx.Menu()
        del_profile_menu = wx.Menu()

        # Build Save & Delete menus
        for i in range(PSConfig.MAX_SAVE_PROFILES):
            self._save_profile_items.append( save_profile_menu.Append(self._BASE_ID_SAVE_PROFILE + i, "Slot %d" % (i+1), "", wx.ITEM_NORMAL) )
            self.Bind(wx.EVT_MENU, self._saveMidiProfileByEvent, id=self._BASE_ID_SAVE_PROFILE + i)
            self._del_profile_items.append( del_profile_menu.Append(self._BASE_ID_DEL_PROFILE + i, "Profile %d" % (i+1), "", wx.ITEM_NORMAL) )
            self.Bind(wx.EVT_MENU, self._deleteMidiProfileByEvent, id=self._BASE_ID_DEL_PROFILE + i)
        midimenu.AppendMenu(-1, "Save In Slot", save_profile_menu)
        midimenu.AppendMenu(-1, "Delete Profile", del_profile_menu)

        # Build Load menu
        for i in range(PSConfig.MAX_SAVE_PROFILES):
            n = i+1
            self._load_profile_items.append( midimenu.Append(self._BASE_ID_LOAD_PROFILE + i, "Load Profile %d" % n, "", wx.ITEM_RADIO) )
            self.Bind(wx.EVT_MENU, self._setMidiProfileByEvent, id=self._BASE_ID_LOAD_PROFILE + i)

    def _updateMidiProfileMenu(self):
        n_midi_prof = len(PSConfig.midi_profiles)

        for i in range(PSConfig.MAX_SAVE_PROFILES):
            if i < n_midi_prof:
                self._save_profile_items[i].Enable(True)
                self._del_profile_items[i].Enable(True)
                self._load_profile_items[i].Enable(True)
            else:
                if i == n_midi_prof:
                    self._save_profile_items[i].Enable(True)
                else:
                    self._save_profile_items[i].Enable(False)
                self._del_profile_items[i].Enable(False)
                self._load_profile_items[i].Enable(False)

    def _setLastMidiProfile(self):
        if PSConfig.last_used_midi_profile == -1:
            return
        else:
            index = PSConfig.last_used_midi_profile
            # reflect the selected profile with interface
            self._load_profile_items[index].Check(True)
            self._doSetMidiProfile(index)

    def _setMidiProfileByEvent(self, evt):
        index = evt.GetId() - self._BASE_ID_LOAD_PROFILE
        PSConfig.last_used_midi_profile = index
        self._doSetMidiProfile(index)

    def _doSetMidiProfile(self, index):
        self.menu_panel.setAdsrCtlNums(PSConfig.midi_profiles[index][0])
        for i in range(1, len(PSConfig.midi_profiles[index])):
            self.midiKeys.ctl_list[i].setCtlNumber(PSConfig.midi_profiles[index][i])
        self._writeMidiProfilesToDisk()
        self.warningWindow = WarningWindow(self, self.GetPosition() + self.warningWindowPos+(0,PSConfig.BANNER_OFFSET),
                                           "Loaded MidiProfile %d" % (index+1))
        self.warningWindow.ShowWindow()
        wx.CallLater(2000, self.warningWindow.destroy)
        PSUtils.printMessage("Loaded MidiProfile %d: %s" % ((index + 1), PSConfig.midi_profiles[index]), 0)

    def _saveMidiProfileByEvent(self, evt):
        """
        Saves MidiProfile in selected slot.
        The config.midi_profiles list contains lists of the saved MidiProfiles.
        The MidiProfile itself is a list containing a tuple of the ADSR knobs' control numbers followed by the
        ParamBox's control numbers : [(A,D,S,R), ctl1, ctl2, ctl3,...]
        """
        index = evt.GetId() - self._BASE_ID_SAVE_PROFILE
        tmp_list = []
        tmp_list.append(self.menu_panel.getAdsrCtlNums())
        for i in range(1, len(self.midiKeys.ctl_list)):
            tmp_list.append(self.midiKeys.ctl_list[i].getCtlNumber())
        if len(PSConfig.midi_profiles) > index:
            PSConfig.midi_profiles[index] = tmp_list
        else:
            PSConfig.midi_profiles.append(tmp_list)
        self._updateMidiProfileMenu()
        # Check saved item to give visual feedback that the item has really been saved
        self._load_profile_items[index].Check(True)
        PSConfig.last_used_midi_profile = index
        self._writeMidiProfilesToDisk()
        self.warningWindow = WarningWindow(self, self.GetPosition() + self.warningWindowPos+(0,PSConfig.BANNER_OFFSET),
                                           "Saved MidiProfile %d" % (index+1))
        self.warningWindow.ShowWindow()
        wx.CallLater(2000, self.warningWindow.destroy)
        PSUtils.printMessage("Saved MidiProfile %d" % (index+1), 0)

    def _deleteMidiProfileByEvent(self, evt):
        index = evt.GetId() - self._BASE_ID_DEL_PROFILE
        PSConfig.midi_profiles.pop(index)
        self._updateMidiProfileMenu()
        self._writeMidiProfilesToDisk()
        self.warningWindow = WarningWindow(self, self.GetPosition() + self.warningWindowPos+(0,PSConfig.BANNER_OFFSET),
                                           "Deleted MidiProfile %d" % (index+1))
        self.warningWindow.ShowWindow()
        wx.CallLater(2000, self.warningWindow.destroy)
        PSUtils.printMessage("Deleted MidiProfile %d" % (index+1), 0)

    def _writeMidiProfilesToDisk(self):
        if len(PSConfig.midi_profiles) == 0:
            if os.path.exists(PSConfig.MIDI_PROFILES_PATH):
                os.remove(PSConfig.MIDI_PROFILES_PATH)
        else:
            with open(PSConfig.MIDI_PROFILES_PATH, 'w') as f:
                to_save = list(PSConfig.midi_profiles)
                to_save.append(PSConfig.last_used_midi_profile)
                pickle.dump(to_save, f)


##### ----------------------
##### SAVE VALUES IN SCRIPT
##### ----------------------
    def saveValuesInScriptByEvent(self, evt):
        float_prec = 4 # will be available as a preference
        if not self.IS_RUNNING:
            # Affichage du message d'avertissement
            self.warningWindow = WarningWindow(self, self.GetPosition()+self.warningWindowPos+(0,PSConfig.BANNER_OFFSET),
                                               "Start script before saving values to script")
            self.warningWindow.ShowWindow()
            wx.CallLater(2000,self.warningWindow.destroy)
            return

        dir, name = os.path.split(self._script_path)
        dlg = wx.FileDialog(
            self, message="Save values in script",
            defaultDir=dir,
            defaultFile=name,
            wildcard="Python source (*.py)|*.py",
            style=wx.SAVE | wx.CHANGE_DIR
        )

        self.FILE_DLG_OPEN = True
        if dlg.ShowModal() == wx.ID_OK:
            self.FILE_DLG_OPEN = False
            save_path = PSUtils.checkExtension(dlg.GetPath(), 'py')
        else:
            self.FILE_DLG_OPEN = False
            PSUtils.printMessage("Save Values in Script: Wrong extension for output file", 0)
            return

        self.warningWindow = WarningWindow(self, self.GetPosition() + self.warningWindowPos+(0,PSConfig.BANNER_OFFSET),
                                           "Saving values in the script...")
        self.warningWindow.ShowWindow()

        try:
            self._doSaveValuesInScript()
        except Warning, e:
            self.exc_win.printException(self._script_path.split('/')[-1], str(e))
            PSUtils.printMessage("An error occurred, see error log for more info.", 0)
            self.warningWindow.SetText("An error occurred.")
            wx.CallLater(2000, self.warningWindow.destroy)

    def _doSaveValuesInScript(self):
        PSUtils.printMessage("Saving values in script...", 1)
        links = self.patchWindow.getLinks()
        to_save = []
        for param in links:
            var_name, attr = param.split('.')
            value = links[param].pyo_obj.get()
            class_name = self.script_namespace[var_name].__class__.__name__
            init_line = class_args(self.script_namespace[var_name].__class__)
            to_save.append([var_name, attr, value, class_name, init_line])

        PSUtils.printMessage("Params to save: %d\n%s"% (len(to_save), to_save), 1)

        f = open(self._script_path, 'r')
        script = f.readlines()
        new_script = []
        for i, line in enumerate(script):
            PSUtils.printMessage("Evaluating line: %d" % (i+1), 1)
            new_line = ""
            if len(to_save) > 0:
                processed_elems = []
                for j, elem in enumerate(to_save):
                    text_inst = "%s *= *%s\(" % (elem[0], elem[3]) # text for instantiation of pyo object
                    res_inst = re.search(text_inst, line)
                    if res_inst is not None: # if this is the line we're looking for
                        PSUtils.printMessage("Found match for: %s" % elem[0], 1)

                        newl = "[a-zA-Z0-9_=,.\[\]'=+\(\) ]*\)\n"
                        if re.search(newl, line) is None: # make sure declaration is a one liner
                            raise Warning, "Multi-line declaration is not yet supported by this function"

                        text_attr = text_inst + "[a-zA-Z0-9_=,.\[\]'=+\(\) ]*%s *=" % elem[1]
                        res_attr = re.search(text_attr, line)
                        if res_attr is not None: # if the attribute keyword is in the line
                            PSUtils.printMessage("Found attribute '%s' in the line" % elem[1], 1)
                            new_line = line[0:res_attr.end()]
                            new_line += str(round(elem[2], float_prec))
                            offset = res_attr.end()
                            for i, char in enumerate(line[res_attr.end():]):
                                if char == ',' or char == ')':
                                    new_line += line[i+offset:]
                                    break
                            line = new_line
                            processed_elems.append(j)
                        else:
                            end = re.search("\)", line)
                            args = self._getArgs(line[res_inst.end():end.start()], elem[4])
                            if elem[1] in args[0]: # if the attribute is in the line (w/o keyword)
                                PSUtils.printMessage("Found value for attribute '%s' in the line" % elem[1], 1)
                                start, end = self._getAttrPos(line, res_inst.end(), args[1].index(elem[1]))
                                new_line = line[0:start]
                                new_line += ", %s" % str(round(elem[2], float_prec))
                                new_line += line[end:]
                                line = new_line
                                processed_elems.append(j)
                            else: # the attribute is not in the line at all, add it in the end
                                PSUtils.printMessage("Attribute '%s' not in the line, adding it at the end" % elem[1], 1)
                                new_line = line[0:-2]
                                new_line += ", %s=%s)\n" % (elem[1], str(round(elem[2], float_prec)))
                                line = new_line
                                processed_elems.append(j)
                    # end if this was the line of elem
                for n, index in enumerate(processed_elems):
                    to_save.pop(index-n)
                # end elem for loop
            new_script.append(line)
        # end main for loop

        f.close()

        # write modified script to path
        f = open(save_path, 'w')
        f.writelines(new_script)
        f.close()

        self._saveValCount += 1
        PSUtils.printMessage("Saved values in script", 0)
        self.warningWindow.SetText("Done!")
        wx.CallLater(2000, self.warningWindow.destroy)

    def _getArgs(self, line, init_line):
        """
        Gets the arguments in the code line and return a tuple :
        ([[parameter name, value], ... ], num of arguments)
        """
        line = self._stripChar(line, ' ')
        args = line.split(',')
        args_init = self._getInitLineArgs(init_line)
        dict = {}
        order = []
        for i, elem in enumerate(args):
            args[i] = elem.split('=')
            if len(args[i]) == 1: # if the param name is not specified, add it
                args[i].insert(0, args_init[i][0])
            order.append(args[i][0])
            dict[args[i][0]] = args[i][1]

        return (dict, order)

    def _getInitLineArgs(self, line):
        # dirty way of retrieving the args in the init line
        tmp_str = line.partition('(')[2].rpartition(')')[0]
        tmp_str = self._stripChar(tmp_str, ' ')
        args = tmp_str.split(',')
        for i, elem in enumerate(args):
            args[i] = elem.split('=')
        return args

    def _stripChar(self, string, char):
        """
        Removes specific character from the string. Mostly useful for removing spaces.
        """
        start = 0
        result = ""
        for i in range(len(string)):
            if string[i] == char:
                result += string[start:i]
                start = i+1
                i += 1
        if i > start: # grab the rest of the string
            result += string[start:]
        return result

    def _getAttrPos(self, line, attr_start, attr_pos):
        """
        Will return the start and end indexes of the argument in position attr_pos.
        :param line: The code line to analyse as as string.
        :param attr_start: Position of the opening parenthesis. Int
        :param attr_pos: The position of the argument in the code line. Int
        :return: (start, end)
        """
        count=0
        start=attr_start
        while count < attr_pos and start < len(line):
            start += 1
            if line[start] == ',':
                count+=1
        end=start
        while end < len(line):
            end += 1
            if line[end] == ',' or line[end] == ')':
                break
        return (start,end)


##### -----------------
##### SCRIPT EXECUTION
##### -----------------
    def _toggleRunStateByEvent(self, evt):
        """
        Demarre le metronome seulement si en mode running.
        S'assure que le midiKeys fonctionne si le serveur a change de parametres.
        """
        if self._EXPORTING:
            return
        # to do before running/stopping the script
        if evt.IsRunning():
            if not self._checkScriptPathIsValid():
                return
            if self._doPrepareToRunScript():
                self.menu_panel.btn_run.ToggleState()
                return
            # actually running/stopping the script
            if self._runScript(): # returns 1 if an error is raised
                self._stopScriptAfterError()
            else:
                if self._PRESET_CHANGED_KEYS_MODE:
                    #self._reinitMidiKeysWithConnections()
                    self._PRESET_CHANGED_KEYS_MODE = False
                self.startServer()
                if not self.FIRST_EXEC and self.LAST_EXC_SCRIPT == self._script_path:
                    self._relinkBoxes()
                if 'mix' in self.script_namespace:
                    self.clip_monitor.setInput(self.script_namespace['mix'])
                    self.clip_monitor.start()
                self.LAST_EXC_SCRIPT = self._script_path
        else:
            self._doPrepareToStopScript()
            self.stopServer()
            self.status_bar.vu_meter.reset()
            self._destroyWarningWindow()
            self._stopScript()
        
    def _doPrepareToRunScript(self):
        PSUtils.printMessage("Preparing to run the script", 0)
        if self.serverSetupPanel.hasChanged():
            if self._resetAudioObjsAfterServerShutdown():
                return 1
            self.serverSetupPanel.resetChangeFlag()
            self.setAutoMatchMode(True) # if values were changed, restore to last save
        if self.midiKeys.isDirty():
            self.midiKeys.reinit()
        self._enableMidiMenuItems(False)
        self._enableButtons()
        self.menu_panel.metro.play()
        self.menu_panel.metro.enable()
        self.rate.play()
        # if a new script is executed, reset all boxes and raise the FIRST_EXEC flag
        if self.LAST_EXC_SCRIPT != self._script_path:
            if self.LAST_EXC_SCRIPT != "":
                self.FIRST_EXEC = True
                self.setAutoMatchMode(True)
                self._saveValCount = 0
                self._resetAllBoxesByEvent(None)
        return 0
    
    def _doPrepareToStopScript(self, error=False):
        PSUtils.printMessage("Preparing to stop the script", 0)
        if self.MATCHING_VALUES:
            self.quitMatchMode()
        self.clip_monitor.stop()
        self._enableMidiMenuItems(True)
        self._disableButtons()
        if self._FUNCTIONS_SET:
            self._removeFunctionsBindings()
        self.menu_panel.metro.stop()
        self.menu_panel.metro.disable()
        self.rate.stop()
        #removing pyo objects from the PatchWindow
        self.patchWindow.clearObjects()
        #removing existing links between MidiControls and PyoObjs
        self._removeLinks()
        if not error:
            if self.FIRST_EXEC:
                self.setAutoMatchMode(False) # disable match mode after first exec
            self.FIRST_EXEC = False

    def _runScript(self):
        self.IS_RUNNING = True
        # actually running the script
        self._before_exec = self.script_namespace.copy()
        try:
            execfile(self._script_path, self.script_namespace)
        except Exception:
            exc_type, exc_name, exc_tb = sys.exc_info()
            string = traceback.format_exc(exc_tb)
            self.exc_win.newException(os.path.split(self._script_path)[1], string)
            self._getScriptVars()
            PSUtils.printMessage("An error occurred in the script", 0)
            return 1
        self._getScriptVars()
        # add pyo objects to the PatchWindow
        for obj in self.pyo_objs:
            self.patchWindow.addObject(obj)
        # updating basic stuff
        self.menu_panel.server_setup_btn.disable()
        self.menu_panel._updateStatus(self.IS_RUNNING)
        PSUtils.printMessage("Script running", 0)
        return 0

    def _stopScript(self):
        self.IS_RUNNING = False
        # stopping and deleting all objects from the script
        self._cleanScriptVars()
        # updating basic stuff
        self.menu_panel.server_setup_btn.enable()
        self.menu_panel._updateStatus(self.IS_RUNNING)
        PSUtils.printMessage("Script stopped", 0)

    def _stopScriptAfterError(self):
        self.menu_panel.btn_run.ToggleState()
        self._doPrepareToStopScript(error=True)
        self.stopServer()
        self.status_bar.vu_meter.reset()
        self._destroyWarningWindow()
        self._stopScript()

    def _runScriptForExport(self):
        try:
            self.serverSetupPanel.initServerForExport()
        except ServerNotBootedError, e:
            PSUtils.printMessage("Timeout expired: Server not booted", 1)
            self.exc_win.printException(self._script_path.split('/')[-1], str(e))
            return 1
        else:
            PSUtils.printMessage("Server booted", 1)

        self.midiKeys.prepareForExport(PSConfig.EXPORT_PREF['notedur'])
        for i in range(1, len(self.midiKeys.ctl_list)):
            self.midiKeys.ctl_list[i].reinit()
        self.menu_panel.reinit()
        self.menu_panel.metro.play()

        # if a new script is executed, reset all boxes and raise the FIRST_EXEC flag
        if self.LAST_EXC_SCRIPT != self._script_path:
            if self.LAST_EXC_SCRIPT != "":
                self.FIRST_EXEC = True
                self._saveValCount = 0
                self._resetAllBoxesByEvent(None)

        # only boxes that are already in use will be prepared for export
        # otherwise this is handled in the setPreset() method
        if not self.FIRST_EXEC and self.LAST_EXC_SCRIPT == self._script_path:
            for box in self.boxes_list:
                box.prepareForExport()

        if self._runScript(): # returns 1 if an error is raised
            return 1
        else:
            self.menu_panel.btn_run.ToggleState()
            if not self.FIRST_EXEC and self.LAST_EXC_SCRIPT == self._script_path:
                self._relinkBoxes()

            self.LAST_EXC_SCRIPT = self._script_path
            return 0

    def _stopScriptAfterExport(self):
        self._removeLinks()
        self._stopScript()
        self.menu_panel.btn_run.ToggleState()
        self.FIRST_EXEC = False
        self.menu_panel.metro.stop()
        self.serverSetupPanel.markDirty()  # will force server reinit and reinstate original settings when running next script
        self.midiKeys.cleanAfterExport()  # reset to original keyboard mode
        self._updatePolyDisplayValue(0)
        self.warningWindow.SetText("Done!")
        wx.CallLater(2000, self.warningWindow.destroy)

    def _stopCurrentScriptToRunNewScript(self):
        self.menu_panel.btn_run.ToggleState(0)
        time.sleep(.1)
        self.menu_panel.btn_run.ToggleState(0)

    def _getScriptVars(self):
        after_exec = self.script_namespace.copy()
        for key in after_exec:
            if key not in self._before_exec:
                if isinstance(after_exec[key], PyoObjectBase):
                    self.pyo_objs[key] = after_exec[key]
                else:
                    self.script_vars[key] = after_exec[key]

    def _cleanScriptVars(self):
        for obj in self.pyo_objs:
            try:
                self.pyo_objs[obj].stop()
            except AttributeError:
                # certains objets pyo n'ont pas de methode stop()
                pass
            string = "del %s" % obj
            exec string in self.script_namespace
        self.pyo_objs.clear()
        for var in self.script_vars:
            string = "del %s" % var
            exec string in self.script_namespace
        self.script_vars.clear()
        gc.collect()

    def _reinitMidiKeysWithConnections(self):
        d = self.midiKeys._getitem_dict
        self._streams_connections_dict = {}
        for key in d:
            self._streams_connections_dict[key] = []
        for obj in self.pyo_objs:
            self._getMidiKeysConnections(obj)
        self.midiKeys.reinit()
        self._reconnectMidiKeysInScript()

    def _getMidiKeysConnections(self, name):
        """
        Note: this method should be modified to use regex to analyse the file and retrieve the values as in the save
        values in script method. This will ensure that cases when arithmetic operations are performed on objects are
        also taken into account. Refactoring the code for save values in script could make it work for both cases.
        For example: pyosynth['pitch']*pyosynth['bend'] will be ignored by this method as it cannot detect the dummy
        object resulting of this operation.
        """
        try:
            # retourne une liste des parametres utilisables en format string
            param_list = PARAMS_TREE_DICT[self.script_namespace[name].__class__.__name__]
        except:
            # quitte la fonction si l'element ne fait pas parti des objets audio controlable
            return
        streams_dict = self.midiKeys._getitem_dict
        for param in param_list:
            current_value = eval('%s.%s'%(name, param), self.script_namespace)
            for key in streams_dict:
                if key in ['bend', 'mod'] and isinstance(streams_dict[key], int):
                    pass
                elif streams_dict[key] is current_value:
                    self._streams_connections_dict[key].append('%s.%s'%(name, param))

    def _reconnectMidiKeysInScript(self):
        print self._streams_connections_dict
        for key, param_list in self._streams_connections_dict.iteritems():
            for param in param_list:
                exec("%s=self.midiKeys['%s']"%(param,key), self.script_namespace, locals())

    def _resetAudioObjsAfterServerShutdown(self):
        try:
            self.serverSetupPanel.initServer()
        except ServerNotBootedError, e:
            PSUtils.printMessage("Timeout expired: Server not booted", 1)
            self.exc_win.printException(self._script_path.split('/')[-1], str(e))
            return 1
        else:
            PSUtils.printMessage("Server booted", 1)

        self.midiKeys.reinit()
        self.boxes_list[0].reinit(self.midiKeys['bend'], self.midiKeys['mod'])
        self.rate = Metro(PSConfig.REFRESH_RATE)
        self.trig_func = TrigFunc(self.rate, self._mainRefreshLoop)
        self.menu_panel.reinit()
        self.clip_monitor.reinit()
        return 0

    def _removeLinks(self):
        """
        Retire tous les liens avec les MidiControl avant de supprimer les objets audio du script.
        """
        for box in self.boxes_list:
            box.unlink(self.script_namespace)

    def _relinkBoxes(self):
        for box in self.boxes_list:
            try:
                box.relink(self.script_namespace)
            except NameError, e:
                self.exc_win.printException(self._script_path.split('/')[-1], str(e))

    def _enableButtons(self):
        self.status_bar.rec_btn.enable()
        self.metroitem.Enable(True)
        if self.serverSetupPanel.isUsingVirtualKeys():
            self.virtual_keys_item.Enable(True)
        self.save_values_script.Enable(True)

    def _disableButtons(self):
        self.status_bar.rec_btn.disable()
        self.metroitem.Enable(False)
        self.virtual_keys_item.Enable(False)
        self.save_values_script.Enable(False)

    def _enableMidiMenuItems(self, value):
        self.normal_keys_mode_item.Enable(value)
        self.sustain_keys_mode_item.Enable(value)
        self.mono_keys_mode_item.Enable(value)
        for elem in self._mono_type_items_list:
            elem.Enable(value)
        for elem in self._poly_menu_items_list:
            elem.Enable(value)
        for elem in self._pbend_menu_items_list:
            elem.Enable(value)

    def _destroyWarningWindow(self):
        if self.warningWindow != None:
            try:
                self.warningWindow.destroy()
            except:
                # if the window has already been destroyed but it hasn't been set to none
                pass

    def startServer(self):
        """
        Start the server (eventually with a fade in).
        """
        self._server_.start()
        PSUtils.printMessage("Pyo server started", 0)

    def stopServer(self):
        """
        Stop the server (eventually with a fade out).
        """
        time.sleep(.2)
        self._server_.stop()
        PSUtils.printMessage("Pyo server stopped", 0)
        time.sleep(.2)

    def _checkScriptPathIsValid(self):
        if not os.path.exists(self._script_path):
            self.menu_panel.btn_run.ToggleState()
            PSUtils.printMessage("Error: The script path does not exist.", 0)
            self.exc_win.printException(os.path.split(self._script_path)[1], "The script path does not exist.")
            return False
        return True

##### --------------------
##### EXPORT EXPORT EXPORT
##### --------------------
    def _showExportDialog(self):
        if len(PSConfig.EXPORT_PREF) > 0:
            dialog = ExportWindow(self, PSConfig.EXPORT_PREF)
        else:
            dialog = ExportWindow(self)
        dialog.CenterOnScreen()
        self._addToWhiteList(dialog.getWhiteListItems())
        if dialog.ShowModal() == wx.ID_OK:
            PSConfig.EXPORT_PREF = dialog.getValues()
            self._removeFromWhiteList(dialog.getWhiteListItems())
            dialog.Destroy()
        else:
            self._removeFromWhiteList(dialog.getWhiteListItems())
            dialog.Destroy()
            return 1

    def _createExportTree(self, velocityList):
        paths = []
        root = os.path.join(PSConfig.EXPORT_PREF['path'], 'PSExport')
        if not os.path.exists(root):
            os.mkdir(root)
        for i in range(PSConfig.EXPORT_PREF['velsteps']):
            path = os.path.join(root, "vel_%03d" % velocityList[i])
            paths.append(path)
            if not os.path.exists(path):
                os.mkdir(path)
        return paths

    def _exportScriptByEvent(self, evt):
        if self._showExportDialog() == 1:
            return
        else:
            with open(PSConfig.EXPORT_PREF_PATH, 'w') as f:
                pickle.dump(PSConfig.EXPORT_PREF, f)

        if self.IS_RUNNING:
            PSUtils.printMessage("Restarting server before export...", 0)
            self.menu_panel.btn_run.ToggleState(1)

        self._EXPORTING = True
        PSUtils.printMessage("Preparing to run script for export...", 0)
        self.menu_panel.btn_run.disable()
        self.runitem.Enable(False)
        if self._runScriptForExport():  # returns 1 if an error is raised
            PSUtils.printMessage("An error was raised while trying to run the script. See Script Error Log for more info.", 0)
            self.menu_panel.btn_run.enable()
            self.runitem.Enable(True)
        else:
            PSUtils.printMessage("Started exporting script to samples...", 0)
            self.warningWindow = WarningWindow(self, self.GetPosition() + self.warningWindowPos+(0,PSConfig.BANNER_OFFSET),
                                               "Exporting samples...")
            self.warningWindow.SetProgressBar()
            self.warningWindow.PulseProgressBar()
            self.warningWindow.ShowWindow(fade=False)
            wx.Yield()  # allows program to process events before continuing execution
            duration = self._doExportScript()
            self._stopScriptAfterExport()
            self.status_bar.vu_meter.reset()
            self.menu_panel.btn_run.enable()
            self.runitem.Enable(True)
            PSUtils.printMessage("Finished exporting script to samples in %02d:%02d:%02d"%PSUtils.getTimeFromSeconds(duration), 0)
            PSUtils.openSysFileBrowser(os.path.join(PSConfig.EXPORT_PREF['path'], 'PSExport'))
        self._EXPORTING = False

    def _doExportScript(self):
        freqsList = PSUtils.midiRangeToHz(PSConfig.EXPORT_PREF['midimin'], PSConfig.EXPORT_PREF['midimax'])
        velocityList = PSUtils.createVelocityList(PSConfig.EXPORT_PREF['velsteps'])
        totalSamples = len(freqsList) * len(velocityList)
        start_time = time.time()
        sample_proc_time_list = []
        self.warningWindow.SetProgressRange(totalSamples)
        self.warningWindow.SetProgressValue(0)
        self.warningWindow.SetBottomText("Elapsed: 00:00:00")
        paths = self._createExportTree(velocityList)
        midinote_count = PSConfig.EXPORT_PREF['midimin']

        for i in range(len(freqsList)):
            for j in range(len(velocityList)):
                path = os.path.join(paths[j], "note_%d%s" % (
                    midinote_count, PSConfig.REC_FORMAT_DICT[PSConfig.EXPORT_PREF['format']]))
                self.serverSetupPanel.recordOptions(PSConfig.EXPORT_PREF['filelength'],
                                                    path,
                                                    PSConfig.EXPORT_PREF['format'],
                                                    PSConfig.EXPORT_PREF['bitdepth'])
                self.midiKeys.setVelocityValue(velocityList[j] / 127.)
                self.midiKeys.notes.value = freqsList[i]
                self.midiKeys.playNote()
                PSUtils.printMessage(
                    "Offline Server rendering file %s dur=%.6f" % (path, PSConfig.EXPORT_PREF['filelength']), 0)
                self.serverSetupPanel._server.start()

                # display progress
                current_progress = i * PSConfig.EXPORT_PREF['velsteps'] + j + 1
                self.warningWindow.SetText(
                    "Exporting samples... %d/%d" % (current_progress, totalSamples))
                self.warningWindow.SetProgressValue(current_progress)

                if current_progress == 0:
                    sample_proc_time_list.append(time.time()-start_time)
                else:
                    sample_proc_time_list.append(time.time()-start_time-sum(sample_proc_time_list))
                estimate = sum(sample_proc_time_list)/len(sample_proc_time_list)*(totalSamples-current_progress)
                remaining_str = "Remaining: %02d:%02d:%02d" % PSUtils.getTimeFromSeconds(estimate)
                elapsed_str = "Elapsed: %02d:%02d:%02d" % PSUtils.getTimeFromSeconds(time.time()-start_time)
                self.warningWindow.SetBottomText(elapsed_str+"  |  "+remaining_str)
                # end display progress

                self._mainRefreshLoop()
                wx.Yield()  # allows program to process events before continuing execution
            midinote_count += 1
        return time.time()-start_time


##### --------------------
##### OPEN OPEN OPEN OPEN
##### --------------------
    def _openDialogByEvent(self, evt):
        if PSConfig.LAST_DIR is None:
            dir = r"%s" % PSConfig.HOME_PATH
        else:
            dir = r"%s" % PSConfig.LAST_DIR

        dlg = wx.FileDialog(
            self, message="Choose a script",
            defaultDir=dir,
            defaultFile="",
            wildcard="Python source (*.py)|*.py",
            style=wx.OPEN | wx.CHANGE_DIR
        )

        self.FILE_DLG_OPEN = True
        if dlg.ShowModal() == wx.ID_OK:
            self._script_path = dlg.GetPath()
            PSConfig.LAST_DIR = os.path.split(self._script_path)[0]
            self._addPathToRecent()
            self.menu_panel._setScriptName(os.path.split(self._script_path)[1])
            self.enableMenuItems()
            if self.IS_RUNNING:
                self._stopCurrentScriptToRunNewScript()
        self.FILE_DLG_OPEN = False

    def _addPathToRecent(self):
        """
        Ajoute un chemin d'acces a la liste de ceux ouvert recemment.
        Si le chemin est deja dans la liste, il ne fait que remonter
        en premiere position.
        """
        try:
            # verifie si le chemin est deja dans la liste et si oui, le retire
            index = PSConfig.RECENT_SCRIPTS.index(self._script_path)
            PSConfig.RECENT_SCRIPTS.pop(index)
        except ValueError:
            pass
        finally:
            PSConfig.RECENT_SCRIPTS.insert(0, self._script_path)
            if len(PSConfig.RECENT_SCRIPTS) > PSConfig.MAX_RECENT_SCRIPTS:
                PSConfig.RECENT_SCRIPTS.pop(-1)

    def _setScriptFromRecentMenuByEvent(self, evt):
        item = evt.GetEventObject().FindItemById(evt.GetId())
        self._script_path = item.GetText()
        PSConfig.LAST_DIR = os.path.split(self._script_path)[0]
        self._addPathToRecent()
        self.menu_panel._setScriptName(os.path.split(self._script_path)[1])
        self.enableMenuItems()
        if self.IS_RUNNING:
            self._stopCurrentScriptToRunNewScript()

    def _setMostRecentScriptByEvent(self, evt):
        if len(PSConfig.RECENT_SCRIPTS) > 0:
            self._script_path = PSConfig.RECENT_SCRIPTS[0]
            self.menu_panel._setScriptName(os.path.split(self._script_path)[1])
            self.enableMenuItems()
            if self.IS_RUNNING:
                self._stopCurrentScriptToRunNewScript()
        else:
            PSUtils.printMessage("No recent script to run yet.", 0)


##### -----------------------
##### PRESETS PRESETS PRESETS
##### -----------------------
    def savePresetByEvent(self, evt):
        preset = self.buildPreset()
        self.writePreset(self._script_path, preset)
        
    def savePresetAsByEvent(self, evt):
        dir, name = os.path.split(self._script_path)
        dlg = wx.FileDialog(
            self, message="Save script as",
            defaultDir=dir,
            defaultFile=name,
            wildcard="Python source (*.py)|*.py",
            style=wx.SAVE | wx.CHANGE_DIR
            )

        self.FILE_DLG_OPEN = True
        if dlg.ShowModal() == wx.ID_OK:
            save_path = PSUtils.checkExtension(dlg.GetPath(), 'py')
            PSConfig.LAST_DIR = os.path.split(save_path)[0]
            preset = self.buildPreset()
            if self.writePresetAs(self._script_path, save_path, preset):
                if self.LAST_EXC_SCRIPT == self._script_path:
                    self.LAST_EXC_SCRIPT = save_path
                self._script_path = save_path
                self._addPathToRecent()
                self.menu_panel._setScriptName(os.path.split(self._script_path)[1])
        self.FILE_DLG_OPEN = False
        
    def buildPreset(self):
        preset = {}
        preset[0] = {}
        preset[0]['master'] = self.status_bar.vol_slider.getValue()
        preset[0]['adsr'] = self.midiKeys.getAdsrValues()
        #preset[0]['keys_mode'] = self.midiKeys.getKeyboardMode()
        #if self.midiKeys.getKeyboardMode() == 2:
        #    preset[0]['mono_type'] = self.midiKeys.getMonoType()
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
                preset[i]['dB'] = self.boxes_list[i].DISPLAY_DB
                preset[i]['attr'] = self.midiKeys.getParamName(i)
                val = self.midiKeys.getValue(i)
                thresh = float("."+"0"*preset[i]['prec']+"1")
                if val <= preset[i]['min']+thresh:
                    preset[i]['val'] = None
                    preset[i]['norm_val'] = None
                elif val > preset[i]['max']:
                    preset[i]['val'] = preset[i]['max']
                    preset[i]['norm_val'] = 1.
                else:
                    preset[i]['val'] = val
                    preset[i]['norm_val'] = self.midiKeys.getNormValue(i)
        return preset
    
    def writePreset(self, path, dict):
        try:
            f = open(path, 'r')
        except IOError, e:
            # Affichage du message d'avertissement
            self.warningWindow = WarningWindow(self, self.GetPosition()+self.warningWindowPos+(0,PSConfig.BANNER_OFFSET),
                                               "Could not save the patch...")
            self.warningWindow.ShowWindow()
            wx.CallLater(2000,self.warningWindow.destroy)
        else:
            script = f.readlines()
            for i, line in enumerate(script):
                if line == PSConfig.PRESET_BANNER+ "\n":
                    script = script[0:i]
                    break
            while script[-1]=='\n':
                del script[-1]
            f.close()
            if PSConfig.PATCH_BANNER+ "\n" not in script:
                script.insert(0, PSConfig.PATCH_BANNER + "\n")
            f = open(path, 'w')
            f.writelines(script)
            f.write("\n\n\n" + PSConfig.PRESET_BANNER + "\n")
            f.write("preset = ")
            pprint.pprint(dict, f)
            f.write("\npyosynth.setPreset(preset)")
            f.close()
            # Affichage du message d'avertissement
            self.warningWindow = WarningWindow(self, self.GetPosition()+self.warningWindowPos+(0,PSConfig.BANNER_OFFSET),
                                               "Patch saved")
            self.warningWindow.ShowWindow()
            wx.CallLater(2000,self.warningWindow.destroy)
            
    def writePresetAs(self, source, dest, dict):
        try:
            f = open(source, 'r')
        except IOError, e:
            # Affichage du message d'avertissement
            self.warningWindow = WarningWindow(self, self.GetPosition()+self.warningWindowPos+(0,PSConfig.BANNER_OFFSET),
                                               "Could not save the patch...")
            self.warningWindow.ShowWindow()
            wx.CallLater(2000,self.warningWindow.destroy)
        else:
            script = f.readlines()
            for i, line in enumerate(script):
                if line == PSConfig.PRESET_BANNER+ "\n":
                    script = script[0:i]
                    break
            while script[-1]=='\n':
                del script[-1]
            f.close()
            if PSConfig.PATCH_BANNER+ "\n" not in script:
                script.insert(0, PSConfig.PATCH_BANNER + "\n")
            f = open(dest, 'w')
            f.writelines(script)
            f.write("\n\n\n" + PSConfig.PRESET_BANNER + "\n")
            f.write("preset = ")
            pprint.pprint(dict, f)
            f.write("\npyosynth.setPreset(preset)")
            f.close()
            # Affichage du message d'avertissement
            self.warningWindow = WarningWindow(self, self.GetPosition()+self.warningWindowPos+(0,PSConfig.BANNER_OFFSET),
                                               "Patch saved")
            self.warningWindow.ShowWindow()
            wx.CallLater(2000,self.warningWindow.destroy)
            return 1

    def crashSave(self):
        try:
            self._saveTerminalLogByEvent(None)
            path, name = os.path.split(self._script_path)
            name, ext = name.split('.')
            name += '_bk.'
            path = os.path.join(path,name+ext)
        except Exception:
            return 1

        preset = self.buildPreset()

        try:
            f = open(self._script_path, 'r')
        except IOError:
            return 1
        else:
            script = f.readlines()
            for i, line in enumerate(script):
                if line == PSConfig.PRESET_BANNER+ "\n":
                    script = script[0:i]
                    break
            while script[-1]=='\n':
                del script[-1]
            f.close()
            if PSConfig.PATCH_BANNER+ "\n" not in script:
                script.insert(0, PSConfig.PATCH_BANNER + "\n")
            f = open(path, 'w')
            f.writelines(script)
            f.write("\n\n\n" + PSConfig.PRESET_BANNER + "\n")
            f.write("preset = ")
            pprint.pprint(preset, f)
            f.write("\npyosynth.setPreset(preset)")
            f.close()
            return path
        
    def _setPreset(self, preset):
        if self._EXPORTING and not self.FIRST_EXEC:
            return
        elif self._EXPORTING and self.FIRST_EXEC:
            self._setPresetValuesForExport( self._doSetPreset(preset, True) )
        else:
            preset_values = self._doSetPreset(preset)
            if self._getMatchMode():
                self._setPresetValues(preset_values)

    def _doSetPreset(self, preset, export=False):
        if export:
            PSUtils.printMessage("Setting preset for export", 0)
        else:
            PSUtils.printMessage("Setting preset", 0)
        if 0 in preset:
            elem = preset.pop(0)
            self.menu_panel.setAdsrValues(elem['adsr'])
            master = elem['master']
            if master <= 1 and master >= 0:
                self._server_.amp = master
                self.status_bar._setMasterVolSlider(master)
            else:
                self._server_.amp = .8
                self.status_bar._setMasterVolSlider(.8)
            #if self.midiKeys.getKeyboardMode() != elem['keys_mode']:
            #    self._PRESET_CHANGED_KEYS_MODE = True
            #    self.midiKeys.setKeyboardMode(elem['keys_mode'])
            #    if elem['keys_mode'] == 0:
            #        self.normal_keys_mode_item.Check(True)
            #    elif elem['keys_mode'] == 1:
            #        self.sustain_keys_mode_item.Check(True)
            #    elif elem['keys_mode'] == 2:
            #        self.mono_keys_mode_item.Check(True)
            #        self.midiKeys.setMonoType(elem['mono_type'])
            #        self._mono_type_items_list[elem['mono_type']].Check(True)
        values_dict = {} #contains all the values for the MatchMode
        PSUtils.printMessage("Retrieving values for controls...", 1)
        for key in preset:
            try:
                if preset[key]['attr'] is not None:
                    self._makeConnection(key, preset[key]['attr'])
                self.boxes_list[key].enable(preset[key]['name'])
                self.boxes_list[key].setDisplayPrecision(preset[key]['prec'])
                self.boxes_list[key].DISPLAY_DB = preset[key]['dB']
                self.midiKeys.setScale(key, preset[key]['min'], preset[key]['max'])
                self.midiKeys.setExp(key, preset[key]['exp'])
                self.midiKeys.setPort(key, preset[key]['port'])
                self.midiKeys.setFloor(key, preset[key]['floor'])
            except (TypeError,NameError), e:
                self.exc_win.printException(self._script_path.split('/')[-1], "PresetError : "+str(e))
                self.boxes_list[key].enable("*"+preset[key]['name'])
            else:
                if export:
                    val = preset[key]['norm_val'] if preset[key]['norm_val'] is not None else 0.
                    values_dict[key] = val
                    PSUtils.printMessage("ctl: %d; norm val: %.3f" % (key, val), 1)
                else:
                    if preset[key]['val'] is not None:
                        values_dict[key] = preset[key]['val']
                        PSUtils.printMessage("ctl: %d; val: %.3f" % (key, preset[key]['val']), 1)

        return values_dict
                
    def _setPresetValues(self, values_dict):
        """
        Permet de sauvegarder un son en gardant les valeurs
        de tous les ParamBox en memoire.
        
        L'attribut preset doit etre un dictionnaire avec le format suivant:
            preset = {numero du controleur:valeur du controleur}
        """
        self.MATCHING_VALUES = True
        PSUtils.printMessage("Starting Match Mode...", 1)
        self.i = 0
        self.values_dict = values_dict

        self.reset_boxes_item.Enable(False)
        ##Affichage du message d'avertissement
        self.warningWindow = WarningWindow(self, self.GetPosition()+self.warningWindowPos+(0,PSConfig.BANNER_OFFSET),
                                           "Matching preset values...")
        self.warningWindow.ShowWindow()
        self.Raise() # little hack to give focus to the main frame after instantiating the WarningWindow
        self._nextPreset()

    def _setPresetValuesForExport(self, values_dict):
        PSUtils.printMessage("Setting preset values for export", 0)
        for key in values_dict:
            PSUtils.printMessage("Setting ctl %d to %.3f hijack value" % (key, values_dict[key]), 1)
            self.boxes_list[key].setHijackNormValueForExport(values_dict[key])

    def _nextPreset(self):
        if len(self.values_dict) > 0:
            self.enableBoxes(False)
            self.i += 1
            while True:
                if self.i in self.values_dict:
                    PSUtils.printMessage("Matching value for ctl.%d" % self.i, 1)
                    self.boxes_list[self.i].Enable(True)
                    self.boxes_list[self.i].matchValue(self.values_dict.pop(self.i))
                    break
                else:
                    self.i += 1
        else:
            self.MATCHING_VALUES = False
            PSUtils.printMessage("Match Mode completed", 1)
            self.reset_boxes_item.Enable(True)
            self.enableBoxes(True)
            self.warningWindow.SetText("Done!")
            self.warningWindow.destroy()
            del self.i
            del self.values_dict

    def quitMatchMode(self):
        self.MATCHING_VALUES = False
        self.enableBoxes(True)
        self.reset_boxes_item.Enable(True)
        self.boxes_list[self.i].stopMatchMode()
        self._destroyWarningWindow()
        del self.i
        del self.values_dict

    def enableBoxes(self, enable):
        for box in self.boxes_list:
            box.Enable(enable)
            
    def _makeConnection(self, ctl, attr):
        try:
            obj_name, obj_attr = attr.split('.')
        except:
            raise TypeError, "Object reference passed in preset for MidiControl no.%d should be a reference to an attribute of an object with the following format : obj.attr" % ctl

        if obj_name not in self.script_namespace:
            raise NameError, "The object named '%s' was not found in the script and the connection to MidiControl no.%d couldn't be made." % (obj_name, ctl)
        else:
            obj = self.script_namespace[obj_name]
            obj_audio_attrs = PARAMS_TREE_DICT[obj.__class__.__name__]  # parameters controllable at audio rate

        if obj_attr not in obj_audio_attrs:
            raise TypeError, "Object named '%s' of type '%s' has no attribute '%s'." % (obj_name, obj.__class__.__name__, obj_attr)
        else:
            self.patchWindow._makeConnection(attr, self.boxes_list[ctl])

##### -------------------
##### AVAILABLE FOR USER
##### -------------------
    def __getitem__(self, i):
        if i == 'click':
            return self.menu_panel[i]
        return self.midiKeys[i]
    
    def setScale(self, ctl, min, max):
        self.midiKeys.setScale(ctl, min, max)
            
    def setExp(self, ctl, value):
        self.midiKeys.setExp(ctl, value)
            
    def setPort(self, ctl, value):
        self.midiKeys.setPort(ctl, value)
        
    def setFloor(self, ctl, value):
        self.midiKeys.setFloor(ctl, value)

    def setDisplayDB(self, ctl, value):
        assert isinstance(value, bool), "setDisplayDB expects boolean value"
        self.boxes_list[ctl].setDisplayDB(value)

    def setTempo(self, value):
        assert isinstance(value, int) or isinstance(value, float), "setTempo() expecting integer or float type as value"
        self.menu_panel.metro.setTempo(value)

    def getTempo(self, sig=True):
        return self.menu_panel.metro.getTempo(sig)

    def getTempoTime(self, sig=True):
        return self.menu_panel.metro.getTime(sig)

    def getTempoFreq(self, sig=True):
        return self.menu_panel.metro.getFreq(sig)

    def getPoly(self):
        return self.midiKeys.getPolyphony()

    def setPreset(self, preset):
        self._setPreset(preset)

    def quickPreset(self, dict):
        if self._EXPORTING: return

        for key in dict:
            if isinstance(dict[key], list):
                self.boxes_list[key].enable(dict[key][0])
                self.boxes_list[key].val_prec = dict[key][1]
            else:
                self.boxes_list[key].enable(dict[key])

    def setFunctions(self, flist):
        """
        Sets the functions in the functions menu.
        Attribute flist has to be a list of callables, tuples or mix of both.
        Tuples have to be as follows (callable, string).
        """
        if self._EXPORTING: return

        PSUtils.printMessage("setFunctions() called", 1)
        if self._FUNCTIONS_SET:
            self.exc_win.printException(self._script_path.rsplit('/', 1)[1], "setFunctions() can only be called once\n")
            return
        if not isinstance(flist, list):
            self.exc_win.printException(self._script_path.rsplit("/", 1)[1], "Error : setFunctions() expects a list as an argument.\n")
            return
        if len(flist) > 10:
            self.exc_win.printException(self._script_path.rsplit("/", 1)[1],
                                        "Warning : max list size 10. Current size %d. Some functions won't be available.\n"%len(flist))
        self._setFunctions(flist)