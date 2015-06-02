#!/usr/bin/env python
# encoding: utf-8

"""
Copyright 2015 Alexandre Poirier

This file is part of Pyo Synth, a python module to help digital signal
processing script creation.

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

from pyo import *
import wx, math, psutil, os, time, pickle, shutil, sys, traceback

#PyoSynth custom modules import
import audio, buttons, controls, config, utils
import interfacePyImg as imgs
from pyoParamTree import PARAMS_TREE_DICT

class RecordedTrackElement(wx.Panel):
    size = (164,40)
    def __init__(self, parent, pos, info):
        wx.Panel.__init__(self, parent, pos=pos, size=self.size)
        self.SetTransparent(255)
        
        self._selected = False
        self._hover = False
        
        self._sndtable = None
        
        #info => (path, track number)
        self._info = info
        self._text = "Track %d" % self._info[1]
        self._durationText = self._getDurationText()
        self.font = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, faceName="Helvetica")
        
        #buttons
        self.play_btn = buttons.PlayTrackButton(self, (5,20))
        self.stop_btn = buttons.StopTrackButton(self, (19,22))
        self.save_btn = buttons.SaveTrackButton(self, (100,4))
        self.delete_btn = buttons.DeleteTrackButton(self, (118,5))
        
        #marqueur de progression de lecture
        self.progression_bar = controls.TrackProgressionBar(self, (38,25))
        self._progression_time = 0

        #binding events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseIn)
        self.play_btn.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseIn)
        self.stop_btn.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseIn)
        self.save_btn.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseIn)
        self.delete_btn.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseIn)
        self.progression_bar.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseIn)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseOut)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseScroll)
        self.Bind(buttons.EVT_BTN_PLAY, self._playTrack)
        self.Bind(buttons.EVT_BTN_STOP, self._stopTrack)
        self.Bind(buttons.EVT_BTN_CLICKED, self._saveTrack, self.save_btn)
        self.Bind(buttons.EVT_BTN_CLICKED, self._deleteTrack, self.delete_btn)
        
    def OnPaint(self, evt):
        w,h = self.GetSize()
        dc = wx.PaintDC(self)
        
        #draw background
        colour = None
        if(self._hover or self._selected):
            colour = wx.Colour(90,90,90,255)
        else:
            colour = wx.Colour(90,90,90,20)
        dc.SetBrush(wx.Brush(colour))
        dc.SetPen(wx.Pen(colour,1))
        dc.DrawRectangle(0,0,w,h)
        
        dc.SetFont(self.font)
        dc.SetTextForeground("#FFFFFF")
        dc.DrawText(self._text+" - "+self._durationText,5,6)
        
    def OnMouseDown(self, evt):
        self._selected = True
        self.GetParent()._setSelection(self)
    
    def OnMouseIn(self, evt):
        self._hover = True
        self.Refresh()
        
    def OnMouseOut(self, evt):
        self._hover = False
        self.Refresh()
        
    def OnMouseScroll(self, evt):
        self.GetParent()._setScrollPosition(evt.GetWheelRotation())
        
    def _getDurationText(self):
        dur = sndinfo(self._info[0])[1]
        min = dur/60
        sec = dur%60
        if min >= 10: min = "%d" % min
        else: min = "0%d" % min
        if sec >= 10: sec = "%d" % sec
        else: sec = "0%d" % sec
        return min+":"+sec
        
    def _setSelection(self, state):
        self._selected = state
        
    def _incrementPlayingTime(self, evt):
        self._progression_time += .1
        self.progression_bar.setValue(self._progression_time)
        if self._progression_time >= self._duration:
            self._stopTrack(evt)
        
    def _playTrack(self, evt):
        self.OnMouseDown(evt)
        if evt.GetState():
            if self._sndtable == None:
                self._prog_bar_timer = wx.Timer(self)
                self.Bind(wx.EVT_TIMER, self._incrementPlayingTime)
                self._sndtable = SndTable(self._info[0])
                self._osc = Osc(self._sndtable, self._sndtable.getRate())
                self._duration = self._sndtable.getDur()
                self.progression_bar.setMax(self._duration)
                #si la fenete a ete fermee et rouverte, on doit s'assurer
                #que le playback recommence la ou il avait arrete la fois d'avant
                self._osc.setPhase(self._progression_time/self._duration)
            self._osc.out()
            self._prog_bar_timer.Start(100)
        else:
            self._pauseTrack()
            
    def _pauseTrack(self):
        if self._sndtable != None:
            self._osc.stop()
            self._prog_bar_timer.Stop()
            
    def _stopTrack(self, evt):
        if self._sndtable != None:
            self._osc.stop()
            self._osc.reset()
            self._prog_bar_timer.Stop()
            self._progression_time = 0
            self.progression_bar.setValue(0)
            self.play_btn.SetState(False)
            
    def _saveTrack(self, evt):
        dlg = wx.FileDialog(
            self, message="Save track",
            defaultDir=config.HOME_PATH,
            defaultFile=".wav",
            style=wx.SAVE
            )
        self.GetParent().GetParent().GetParent().Show(False)
        if dlg.ShowModal() == wx.ID_OK:
            # This returns the path of the selected file as a string
            path = dlg.GetPath()
            #this verifies that the user didn't try to change the fileformat
            ext = path.rsplit('.',1)
            if ext[1] != config.REC_FORMAT_DICT[config.REC_FORMAT][1:]:
                path = ext[0]+".wav"
            shutil.move(self._info[0],path)
            self._removeTrack()
        self.GetParent().GetParent().GetParent().Show(True)
            
    def _deleteTrack(self, evt):
        os.remove(self._info[0])
        self._removeTrack()
        
    def _removeTrack(self):
        self.deletePlaybackObjects()
        self.GetParent()._deleteTrack(self)
            
    def deletePlaybackObjects(self):
        if self._sndtable != None:
            self.Unbind(wx.EVT_TIMER)
            self._prog_bar_timer.Destroy()
            self._osc.stop()
            self._sndtable = None
            self._osc = None
            del self._duration
        
class RecordedTracksList(wx.PyScrolledWindow):
    def __init__(self, parent, size, pos):
        wx.ScrolledWindow.__init__(self, parent, size=size, pos=pos)
        self.SetVirtualSize((self.GetSize()[0]-15,1000))
        self.scrollRate = 10
        self.SetScrollRate(1,self.scrollRate)
        
        #list containing all RecordedTrackElement instances
        self._tracks_list = []
        
        self._selected = None
        
        self.box_height = RecordedTrackElement.size[1]
        self.x_margin = 8
        self.y_margin = 10
        self._setVerticalScroll()
        
        #Binding events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        self.PrepareDC(dc)
        self._drawFakeScrollbar(dc)
            
    def _drawFakeScrollbar(self, dc):
        dc.SetBrush(wx.Brush(wx.Colour(250,250,250)))
        dc.SetPen(wx.Pen(wx.Colour(250,250,250),1))
        w,h = self.GetSize()
        dc.DrawRectangle(w-15,0,15,h)
        
    def _setVerticalScroll(self):
        h = (self.box_height+self.y_margin)*len(self._tracks_list)+self.y_margin
        self.SetVirtualSize((self.GetSize()[0]-15,h))
        
    def _setScrollPosition(self, delta):
        curr_scroll = abs(self.CalcScrolledPosition(0,0)[1])/self.scrollRate
        new_scroll = curr_scroll-delta
        self.Scroll(0,new_scroll)
        
    def _setSelection(self, elem):
        if self._selected != None and self._selected != elem:
            self._selected._pauseTrack()
            self._selected.play_btn.SetState(False)
            self._selected._setSelection(False)
            self._selected.Refresh()
        self._selected = elem
        
    def _deleteTrack(self, track):
        if self._selected == track:
            self._selected = None
        track.Show(False)
        wx.CallAfter(track.Destroy)
        self._tracks_list.remove(track)
        self._repositionTrackElements()
        self._setVerticalScroll()
        
    def _repositionTrackElements(self):
        for i, elem in enumerate(self._tracks_list):
            y = i*(self.box_height+self.y_margin)+self.y_margin
            elem.SetPosition((self.x_margin,y))
        
    def addTrack(self, info):
        y = len(self._tracks_list)*(self.box_height+self.y_margin)+self.y_margin
        self._tracks_list.append(RecordedTrackElement(self, (self.x_margin,y), info))
        self._setVerticalScroll()
        
    def deletePlaybackObjects(self):
        for track in self._tracks_list:
            track.deletePlaybackObjects()

class RecordedTracksWindow(wx.Frame):
    def __init__(self, parent, server, namespace):
        self.server = server
        self.script_namespace = namespace
        wx.Frame.__init__(self, parent, id=-1, size=(200,216), style=wx.NO_BORDER|wx.STAY_ON_TOP)
        self.SetTransparent(0)
        self.panel = wx.Panel(self, size=self.GetSize()+(1,1))
        
        self.tracks_list = RecordedTracksList(self.panel, self.panel.GetSize()-(4,26), (1,23))

        #position par rapport au frame principal
        self.pos_offset = wx.Point(295,94)
        
        #s'occupe de l'enregistrement
        self._trackRecorder = audio.TrackRecorder()
        
        #Fade in/out properties
        self.IS_SHOWN = False
        self._alpha = 255
        self._currentAlpha = 0
        self._delta = 22
        self._fadeTime = 27
        self._timer = wx.Timer(self, -1)
        
        #bitmap
        self.background = imgs.recorded_tracks_bg.GetBitmap()
        
        #Binding events
        self.Bind(wx.EVT_TIMER, self.changeAlpha)
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)
        
    def OnPaint(self, evt):
        dc = wx.PaintDC(self.panel)
        dc.DrawBitmap(self.background,0,0)
    
    def ShowWindow(self, pos):
        if not self.IS_SHOWN:
            self.IS_SHOWN = True
            self.SetPosition(self.pos_offset+pos)
            self.Show(True)
            self._timer.Start(self._fadeTime)
        
    def HideWindow(self):
        self.IS_SHOWN = False
        self._timer.Start(self._fadeTime)
        self.tracks_list.deletePlaybackObjects()

    def changeAlpha(self, evt):
        if self.IS_SHOWN:
            if self._currentAlpha < self._alpha:
                self._currentAlpha += self._delta
                if self._currentAlpha > 255: self._currentAlpha = 255
                self.SetTransparent(self._currentAlpha)
            else:
                self._timer.Stop()
        else:
            if self._currentAlpha > 0:
                self._currentAlpha -= self._delta
                if self._currentAlpha < 0: self._currentAlpha = 0
                self.SetTransparent(self._currentAlpha)
            else:
                self.Show(False)
                self._timer.Stop()
        
    def _setPosition(self, pos):
        self.SetPosition(pos+self.pos_offset)
        
    def startRecording(self):
        if 'mix' not in self.script_namespace:
            #Cannot record because the script does not have a 'mix' object.
            return 0
        else:
            self.file_info = self._trackRecorder.record(self.script_namespace['mix'], self.server.getNchnls())
            return self.file_info
        
    def stopRecording(self):
        self._trackRecorder.stop()
        self.tracks_list.addTrack(self.file_info)

##Custom events for the ServerSetupPanel
myEVT_INTERFACE_CHANGED = wx.NewEventType()
EVT_INTERFACE_CHANGED = wx.PyEventBinder(myEVT_INTERFACE_CHANGED, 1)

myEVT_SAMP_RATE_CHANGED = wx.NewEventType()
EVT_SAMP_RATE_CHANGED = wx.PyEventBinder(myEVT_SAMP_RATE_CHANGED, 1)

myEVT_BUFSIZE_CHANGED = wx.NewEventType()
EVT_BUFSIZE_CHANGED = wx.PyEventBinder(myEVT_BUFSIZE_CHANGED, 1)

myEVT_NCHNLS_CHANGED = wx.NewEventType()
EVT_NCHNLS_CHANGED = wx.PyEventBinder(myEVT_NCHNLS_CHANGED, 1)

class ServerSetupEvent(wx.PyCommandEvent):
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)

class ServerSetupPanel(wx.Panel):
    def __init__(self, parent, server):
        wx.Panel.__init__(self, parent, -1, (690,61), (450,260))
        self.SetBackgroundColour("#000000")
        self.SetTransparent(0)
        self.Show(False)
        
        self._server = server
        
        #this flag is set to true when the server reinitializes itself
        #and that audio objects need to be reinstanciated
        #This has to be set to false after being handled by the program
        self.SERVER_CHANGED_FLAG = False
        
        self.hasPreferences = False
        self.preferences = self.getPreferences()
        
        #Fade in/out properties
        self.IS_SHOWN = False
        self._alpha = 220
        self._currentAlpha = 0
        self._delta = 50
        self._fadeTime = 55
        self._timer = wx.Timer(self, -1)
        
        #Setup lists
        self.samplingRates = ['22050 Hz', '32000 Hz', '44100 Hz', '48000 Hz', '88200 Hz', '96000 Hz']
        self.bufferSizes = ['32', '64', '128', '256', '512', '1024', '2048', '4096']
        self.audioDrivers = ['portaudio', 'jack', 'coreaudio', 'offline', 'offline_nb']
        self.numberChnls = ['1', '2', '3', '4']
        
        #Positions
        self.leftMargin = 8
        self.topMargin = 8
        self.interfaceCtrlPos = (self.leftMargin,40)
        self.lineSepPos = (20,157)
        self.sampratePos = (self.leftMargin, 175)
        self.bufsizePos = (self.leftMargin, 205)
        self.audioDriverPos = (self.leftMargin, 235)
        self.duplexPos = (2*self.GetSize()[0]/3-20, 175)
        self.numChnlsPos = (2*self.GetSize()[0]/3-20, 205)
        
        #Controls
        x, y = self.interfaceCtrlPos
        self.inputChoice = wx.Choice(self, -1, (x+6, y+36), choices=self.listDevices("input"))
        self.outputChoice = wx.Choice(self, -1, (x+6, y+80), choices=self.listDevices("output"))
        
        x, y = self.sampratePos
        self.samprateChoice = wx.Choice(self, -1, (x+100, y-6), choices=self.samplingRates)
        
        x, y = self.bufsizePos
        self.bufsizeChoice = wx.Choice(self, -1, (x+80, y-6), choices=self.bufferSizes)
        
        x, y = self.audioDriverPos
        self.audioDriverChoice = wx.Choice(self, -1, (x+90, y-6), choices=self.audioDrivers)
        
        x, y = self.duplexPos
        self.duplexChoice = wx.Choice(self, -1, (x+60, y-6), choices=['out', 'in/out'])
        
        x, y = self.numChnlsPos
        self.numChnlsChoice = wx.Choice(self, -1, (x+80, y-6), choices=self.numberChnls)
        
        #Binding events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.changeAlpha)
        self.Bind(wx.EVT_CHOICE, self.changeInput, self.inputChoice)
        self.Bind(wx.EVT_CHOICE, self.changeOutput, self.outputChoice)
        self.Bind(wx.EVT_CHOICE, self.changeSampRate, self.samprateChoice)
        self.Bind(wx.EVT_CHOICE, self.changeBufSize, self.bufsizeChoice)
        self.Bind(wx.EVT_CHOICE, self.changeAudioDriver, self.audioDriverChoice)
        self.Bind(wx.EVT_CHOICE, self.changeDuplex, self.duplexChoice)
        self.Bind(wx.EVT_CHOICE, self.changeNumChnls, self.numChnlsChoice)
    
        self.initServer()
        
    def OnPaint(self, evt):
        w, h = self.GetSize()
        dc = wx.PaintDC(self)
        penWidth = 1
        dc.SetPen(wx.Pen("#444444", penWidth, wx.SOLID))
        
        #contour
        dc.DrawLine(0, 0, w-penWidth, 0)
        dc.DrawLine(0, 0, 0, h-penWidth)
        dc.DrawLine(0, h-penWidth, w-penWidth, h-penWidth)
        dc.DrawLine(w-penWidth, h-penWidth, w-penWidth, 0)
        
        #fonts
        titleFont = wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, faceName="Helvetica")
        regFont = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, faceName="Helvetica")
        smallFont = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, faceName="Helvetica")
        
        #Titre
        dc.SetTextForeground("#FFFFFF")
        dc.SetFont(titleFont)
        dc.DrawText("Server Setup", self.leftMargin, self.topMargin)
        
        dc.SetFont(regFont)
        x, y = self.interfaceCtrlPos
        dc.DrawText("Interface", x, y)
        
        dc.SetFont(smallFont)
        dc.DrawText("input", x+6, y+20)
        dc.DrawText("output", x+6, y+65)
        
        x, y = self.lineSepPos
        dc.DrawLine(x, y, w-x, y)
        
        dc.SetFont(regFont)
        x, y = self.sampratePos
        dc.DrawText("Sampling Rate : ", x, y)
        x, y = self.bufsizePos
        dc.DrawText("Buffer Size : ", x, y)
        x, y = self.audioDriverPos
        dc.DrawText("Audio Driver : ", x, y)
        
        x, y = self.duplexPos
        dc.DrawText("Duplex : ", x, y)
        x, y = self.numChnlsPos
        dc.DrawText("Num Chnls : ", x, y)
    
    def ShowWindow(self):
        self.updateCtrls()
        self.IS_SHOWN = True
        self.Show(True)
        self._timer.Start(self._fadeTime)
        
    def HideWindow(self):
        self.IS_SHOWN = False
        self._timer.Start(self._fadeTime)
        self.savePreferences()
        
    def IsShown(self):
        return self.IS_SHOWN
        
    def changeAlpha(self, evt):
        if self.IS_SHOWN:
            if self._currentAlpha < self._alpha:
                self._currentAlpha += self._delta
                if self._currentAlpha > self._alpha: self._currentAlpha = self._alpha
                self.SetTransparent(self._currentAlpha)
            else:
                self._timer.Stop()
        else:
            if self._currentAlpha > 0:
                self._currentAlpha -= self._delta
                if self._currentAlpha < 0: self._currentAlpha = 0
                self.SetTransparent(self._currentAlpha)
            else:
                self.Show(False)
                self._timer.Stop()
        
    def changeInput(self, evt):
        self._server.stop()
        
        self.preferences['input'] = int(evt.GetString()[0])
        
        self.initServer()
        
    def changeOutput(self, evt):
        self._server.stop()
        
        self.preferences['output'] = int(evt.GetString()[0])
        
        self.initServer()
        
        #Custom event business
        event = ServerSetupEvent(myEVT_INTERFACE_CHANGED, self.GetId())
        self.GetEventHandler().ProcessEvent(event)
        
    def changeSampRate(self, evt):
        self._server.stop()
        
        self.preferences['sr'] = int(evt.GetString()[0:-3])
        
        self.initServer()
        
        #Custom event business
        event = ServerSetupEvent(myEVT_SAMP_RATE_CHANGED, self.GetId())
        self.GetEventHandler().ProcessEvent(event)
        
    def changeBufSize(self, evt):
        self._server.stop()
        
        self.preferences['bfs'] = int(evt.GetString())
        
        self.initServer()
        
        #Custom event business
        event = ServerSetupEvent(myEVT_BUFSIZE_CHANGED, self.GetId())
        self.GetEventHandler().ProcessEvent(event)
        
    def changeAudioDriver(self, evt):
        self._server.stop()
        
        self.preferences['audio'] = evt.GetString()
        
        self.initServer()
        
    def changeDuplex(self, evt):
        self._server.stop()
        
        self.preferences['duplex'] = evt.GetSelection()
        
        self.initServer()
        self.updateCtrls()
        
    def changeNumChnls(self, evt):
        self._server.stop()
        
        self.preferences['nchnls'] = int(evt.GetString())
        
        self.initServer()
        
        #Custom event business
        event = ServerSetupEvent(myEVT_NCHNLS_CHANGED, self.GetId())
        self.GetEventHandler().ProcessEvent(event)
    
    def getLongestText(self, list):
        longest = 0
        for i in range(len(list)):
            chars = len(list[i])
            if chars > longest:
                longest = i
            
        return wx.ClientDC(self).GetTextExtent(list[longest])[0]
    
    def getPreferences(self):
        """
        Tries to open pref file on HD, otherwise sets server to default settings.
        Done once upon startup.
        """
        try:
            f = open(os.path.join(config.PREF_PATH, "server_setup.pref"), 'r')
            self.hasPreferences = True
        except IOError, e:
            self.hasPreferences = False
            return {'sr':44100,'nchnls':2,'bfs':256,'duplex':1,'audio':'portaudio',
                    'output': pa_get_default_output(),
                    'input': pa_get_default_input()}
        else:
            pref = pickle.load(f)
            f.close()
            #verify if input/output interfaces are there
            if pref['output'] not in pa_get_output_devices()[1]:
                pref['output'] = pa_get_default_output()
            if pref['input'] not in pa_get_input_devices()[1]:
                pref['input'] = pa_get_default_input()
            return pref
            
    def savePreferences(self):
        try:
            f = open(os.path.join(config.PREF_PATH, "server_setup.pref"), 'w')
        except IOError, e:
            print "Could not write server preferences to disk.", e
        else:
            pickle.dump(self.preferences, f)
            f.close()
            
    def getOutputInterface(self):
        names, indexes = pa_get_output_devices()
        return names[indexes.index(self.preferences['output'])]
        
    def getSamplingRate(self):
        return self.preferences['sr']
        
    def getBufferSize(self):
        return self.preferences['bfs']
        
    def getNchnls(self):
        return self.preferences['nchnls']
        
    def hasChanged(self):
        return self.SERVER_CHANGED_FLAG
        
    def resetChangeFlag(self):
        self.SERVER_CHANGED_FLAG = False
    
    def initServer(self):
        """
        Initializes the server with the new preferences.
        """
        #set the flag to true so the main program
        #can respond accordingly
        self.SERVER_CHANGED_FLAG = True
        if self._server.getIsBooted():
            time.sleep(.2)
            self._server.shutdown()
            time.sleep(.2)
        
        self._server.reinit(self.preferences['sr'],
                            self.preferences['nchnls'],
                            self.preferences['bfs'],
                            self.preferences['duplex'],
                            self.preferences['audio'],
                            "pyo")
        self._server.setOutputDevice(self.preferences['output'])
        if self.preferences['duplex']:
            self._server.setInputDevice(self.preferences['input'])
        self._server.boot().start()
        
    def initServerForExport(self):
        self.SERVER_CHANGED_FLAG = True
        self._server.stop()
        time.sleep(.2)
        self._server.shutdown()
        time.sleep(.2)
        
        self._server.reinit(self.preferences['sr'],
                            self.preferences['nchnls'],
                            self.preferences['bfs'],
                            self.preferences['duplex'],
                            audio="offline",
                            jackname="pyo")
        self._server.boot()
        
    def recordOptions(self, dur, name, fileformat, bitdepth):
        self._server.recordOptions(dur, name, fileformat, bitdepth)
    
    def listDevices(self, type):
        """
        Builds a list of available devices for the i/o interface choice.
        """
        devices = None
        maxChar = 53
        list = []
        if type == "input":
            devices = pa_get_input_devices()
        elif type == "output":
            devices = pa_get_output_devices()
        for i in range(len(devices[0])):
            text = str(devices[1][i]) + " : "
            text += devices[0][i][0:maxChar]
            list.append(text)
        return list
    
    def updateCtrls(self):
        """
        Updates the values of the wx.Controls for the UI.
        """
        self.duplexChoice.SetSelection(self.preferences['duplex'])
        
        if self.preferences['duplex']:
            #get the inputs
            list = self.listDevices("input")
            #assign them to the choice
            self.inputChoice.SetItems(list)
            #set the size according to largest choice
            self.inputChoice.SetSize((self.getLongestText(list)+48,-1))
            
            names, indexes = pa_get_input_devices()
            self.inputChoice.SetSelection(indexes.index(self.preferences['input']))
            
            names, indexes = pa_get_output_devices()
            self.outputChoice.SetSelection(indexes.index(self.preferences['output']))
        else:
            self.inputChoice.SetItems(["Duplex mode is set to output only."])
            self.inputChoice.SetSelection(0)
            tw, th = wx.WindowDC(self).GetTextExtent("Duplex mode is set to output only.")
            self.inputChoice.SetSize((tw+40,-1))
            
            names, indexes = pa_get_output_devices()
            self.outputChoice.SetSelection(indexes.index(self.preferences['output']))
        
        sr = str(self.preferences['sr'])
        for i, elem in enumerate(self.samplingRates):
            if elem[0:-3] == sr:
                self.samprateChoice.SetSelection(i)
                break
        
        bfs = str(self._server.getBufferSize())
        for i, elem in enumerate(self.bufferSizes): 
            if elem == bfs:
                self.bufsizeChoice.SetSelection(i)
                break
        
        audio = self.preferences['audio']
        for i, elem in enumerate(self.audioDrivers): 
            if elem == audio:
                self.audioDriverChoice.SetSelection(i)
                break
        
        nchnls = str(self.preferences['nchnls'])
        for i, elem in enumerate(self.numberChnls): 
            if elem == nchnls:
                self.numChnlsChoice.SetSelection(i)
                break

class PatchWindow(wx.Frame):
    def __init__(self, parent, namespace):
        wx.Frame.__init__(self, parent, id=-1, size=(200,216), style=wx.NO_BORDER|wx.STAY_ON_TOP)
        self.SetTransparent(0)
        self.panel = wx.Panel(self, size=self.GetSize()+(1,1))
        self.treeCtrl = wx.TreeCtrl(self.panel, size=self.panel.GetSize()-(4,26), pos=(1,23), style=wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT)
        self.treeCtrl.SetBackgroundColour(config.BG_COLOUR)
        self.treeCtrl.SetForegroundColour("#DDDDDD")
        
        self.script_namespace = namespace
        
        #Creation de l'arbre et du dictionnaire contenant
        #les references aux parametres des objets pyo
        self.param_dict = {}
        #id count sert a creer des liens entre les paramtres
        #et leur references dans le param_dict
        self.__id__ = -1
        self.root = self.treeCtrl.AddRoot("Pyo Objects")
        self.treeCtrl.SetPyData(self.root, None)
        #le premier item de la liste est 'None', pour permettre d'enlever un parametre
        item = self.treeCtrl.AppendItem(self.root, 'None')
        self.treeCtrl.SetPyData(item, None)
        #stock l'id de la selection courrante
        self.selection = None
        
        #Fade in/out properties
        self.IS_SHOWN = False
        self._alpha = 240
        self._currentAlpha = 0
        self._delta = 22
        self._fadeTime = 27
        self._timer = wx.Timer(self, -1)
        
        #conserve l'objet ParamBox d'origine
        self._obj = None
        #conserve un dictionnaire des liens {param : obj}
        #ou 'obj' est une reference a l'objet ParamBox
        #et 'param' est un string represetant le parametre de l'objet pyo associe
        self._links = {}
        
        #bitmap
        self.background = imgs.patch_window_bg.GetBitmap()
        
        #Binding events
        self.Bind(wx.EVT_TIMER, self.changeAlpha)
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)
        self.treeCtrl.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelection, self.treeCtrl)

    def OnPaint(self, evt):
        dc = wx.PaintDC(self.panel)
        dc.DrawBitmap(self.background,0,0)
        
    def addObject(self, name):
        obj = self.script_namespace[name]
        try:
            PARAMS_TREE_DICT[obj.__class__.__name__]
        except Exception:
            return
        item = self.treeCtrl.AppendItem(self.root, name+' - '+obj.__class__.__name__)
        self.treeCtrl.SetPyData(item, obj)
        
        #retourne une liste des parametres utilisables en format string
        list = self._getParametersList(obj)
        
        for param in list:
            p = self.treeCtrl.AppendItem(item, param)

            #ici, on stock l'id de l'item pour pouvoir le recupere
            #plus tard et s'en servir comme cle dans le param_dict
            id = self.__getNewId__()
            self.treeCtrl.SetPyData(p, id)
            self.param_dict[id] = name+"."+param
        
    def clearObjects(self):
        #suppression de tous les elements
        self.treeCtrl.DeleteChildren(self.root)
        self.param_dict.clear()
        #ajout de l'entree None pour permettre de desactiver un ParamBox
        item = self.treeCtrl.AppendItem(self.root, 'None')
        self.treeCtrl.SetPyData(item, None)
    
    def OnSelection(self, evt):
        if not self.treeCtrl.ItemHasChildren(evt.GetItem()):
            self.selection = evt.GetItem()
    
    def OnLeftDClick(self, evt):
        evt.Skip()
        if self.selection:
            if self.treeCtrl.GetItemText(self.selection) == 'None':
                self._obj.disable(self.script_namespace)
                self.HideWindow()
            elif not self.treeCtrl.ItemHasChildren(self.selection):
                key = self.treeCtrl.GetItemData(self.selection).GetData()
                self._makeConnection(self.param_dict[key], self._obj)
                self.HideWindow()
        
    def _setPosition(self):
        #verifie si la fenetre depasse du frame parent
        parent = self._obj.GetParent()
        end_of_frame = parent.GetSize()[0]+parent.GetScreenPosition()[0]
        pos = self._obj.GetScreenPosition()+(self._obj.GetSize()[0],2)
        if (pos[0]+self.GetSize()[0]) > end_of_frame:
            pos = self._obj.GetScreenPosition()-(self.GetSize()[0],-2)
        
        self.SetPosition(pos)
        
    def ShowWindow(self, obj):
        self._obj = obj
        self._setPosition()
        
        #evite d'avoir l'erreur : cannot collapse hidden root
        #mais fonctionne quand meme
        try:
            self.treeCtrl.CollapseAllChildren(self.root)
        except:
            pass
        
        if not self.IS_SHOWN:
            self.IS_SHOWN = True
            self.Show(True)
            self._timer.Start(self._fadeTime)
        
    def HideWindow(self):
        self.selection = None
        self._obj = None
        self.IS_SHOWN = False
        self._timer.Start(self._fadeTime)
        
    def _hideWindow(self, evt):
        evt.Skip()
        self.HideWindow()
        
    def IsShown(self):
        return self.IS_SHOWN

    def changeAlpha(self, evt):
        if self.IS_SHOWN:
            if self._currentAlpha < self._alpha:
                self._currentAlpha += self._delta
                self.SetTransparent(self._currentAlpha)
            else:
                self._timer.Stop()
        else:
            if self._currentAlpha > 0:
                self._currentAlpha -= self._delta
                self.SetTransparent(self._currentAlpha)
            else:
                self.Show(False)
                self._timer.Stop()
                
    def _makeConnection(self, param, obj):
        #si le parametre est deja associe a un ParamBox,
        #son ancien controle est dissocie
        if param in self._links:
            self._links[param].unlink(self.script_namespace)
        self._links[param] = obj
        obj.unlink(self.script_namespace)
        exec param+"= obj.getMidiControl()" in self.script_namespace, locals()
        obj.pyo_obj.setParamName(param)
        obj.enable(param)

    def _getParametersList(self, obj):
        return PARAMS_TREE_DICT[obj.__class__.__name__]
        
    def __getNewId__(self):
        self.__id__ += 1
        return self.__id__

class WarningWindow(wx.Frame):
    def __init__(self, parent, pos, text):
        wx.Frame.__init__(self, parent, -1, pos=pos, size=(200,40), style=wx.NO_BORDER|wx.STAY_ON_TOP)
        self.SetTransparent(0)
        self.panel = wx.Panel(self, size=self.GetSize()+(1,1))
        self.panel.SetBackgroundColour("#888888")
        
        self.text = text
        self.setSize()
        
        #Fade in/out properties
        self.IS_SHOWN = False
        self._alpha = 220
        self._currentAlpha = 0
        self._delta = 22
        self._fadeTime = 27
        self._timer = wx.Timer(self, -1)
        
        #Binding events
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.changeAlpha)
        
    def OnPaint(self, evt):
        w, h = self.GetSize()
        dc = wx.PaintDC(self)
        
        font = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, faceName="Helvetica")
        dc.SetTextForeground("#FFFFFF")
        
        txt_w, txt_h = dc.GetTextExtent(self.text)
        dc.DrawText(self.text, (w/2-txt_w/2), 10)
        
    def SetText(self, string):
        self.text = string
        self.setSize()
        wx.CallAfter(self.Refresh)

    def ShowWindow(self, fade=True):
        self.IS_SHOWN = True
        self.Show(True)
        if fade:
            self._timer.Start(self._fadeTime)
        else:
            self.SetTransparent(255)
            self._currentAlpha = 255
        
    def destroy(self):
        self.IS_SHOWN = False
        self._timer.Start(self._fadeTime)
        
    def changeAlpha(self, evt):
        if self.IS_SHOWN:
            if self._currentAlpha < self._alpha:
                self._currentAlpha += self._delta
                if self._currentAlpha > 255:
                    self._currentAlpha = 255
                self.SetTransparent(self._currentAlpha)
            else:
                self._timer.Stop()
        else:
            if self._currentAlpha > 0:
                self._currentAlpha -= self._delta
                if self._currentAlpha < 0:
                    self._currentAlpha = 0
                self.SetTransparent(self._currentAlpha)
            else:
                self.Show(False)
                self._timer.Stop()
                #Quand le fadeout est fini, la fenetre est detruite
                self.Destroy()
                
    def setSize(self):
        dc = wx.ClientDC(self)
        font = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, faceName="Helvetica")
        w,h = dc.GetTextExtent(self.text)
        if w > self.GetSize()[0]-20:
            self.SetSize((w+20,40))
            self.panel.SetSize((w+20,40))

class ParamBoxSettingsWindow(wx.Frame):
    """
    class ParamBoxSettingWindow
    
    parametres
        pos : position de la fenetre sur l'ecran
        params : liste des parametre courant de l'objet pyo
                 [min, max, port, exp, text]
    """
    def __init__(self, parent, pos, params, callable):
        self.parent = parent
        wx.Frame.__init__(self, None, -1, pos=pos, size=(120,172), style=wx.NO_BORDER|wx.STAY_ON_TOP)
        self.SetTransparent(245)
        self.panel = wx.Panel(self, -1, size=self.GetSize()+(1,1))
        
        self._min, self._max, self._port, self._exp, self._text, self._prec, self._int = params
        self.callable = callable
        
        #Positions
        self.leftMargin = 10
        self.topMargin = 8
        
        self.text_pos = (self.leftMargin, self.topMargin+12)
        self.min_pos = (self.leftMargin, self.topMargin+42)
        self.max_pos = (self.leftMargin, self.topMargin+70)
        self.prec_pos = (self.leftMargin, self.topMargin+95)
        self.port_pos = (self.leftMargin, self.topMargin+120)
        self.exp_pos = (self.leftMargin+55, self.topMargin+120)
        self.int_pos = (self.leftMargin, self.topMargin+140)
        
        #Controles
        x, y = self.text_pos
        self.textCtrl = wx.TextCtrl(self.panel, -1, pos=(x-2,y), size=(100,-1), style=wx.TE_PROCESS_ENTER)
        self.textCtrl.SetBackgroundColour("#313131")
        self.textCtrl.SetForegroundColour("#d8ff00")
        self.textCtrl.SetValue(self._text)

        x, y = self.min_pos
        self.minCtrl = wx.TextCtrl(self.panel, -1, pos=(x+37,y), size=(60,-1), style=wx.TE_PROCESS_ENTER)
        self.minCtrl.SetBackgroundColour("#313131")
        self.minCtrl.SetForegroundColour("#d8ff00")
        txt = "%.4f" % self._min
        self.minCtrl.SetValue(txt)
        
        x, y = self.max_pos
        self.maxCtrl = wx.TextCtrl(self.panel, -1, pos=(x+37,y), size=(60,-1), style=wx.TE_PROCESS_ENTER)
        self.maxCtrl.SetBackgroundColour("#313131")
        self.maxCtrl.SetForegroundColour("#d8ff00")
        txt = "%.4f" % self._max
        self.maxCtrl.SetValue(txt)
        
        x, y = self.prec_pos
        self.precCtrl = wx.Choice(self.panel, -1, pos=(x+37, y), choices=['1','2','3','4'])
        self.precCtrl.SetSelection(self._prec-1)
        
        x, y = self.port_pos
        self.portCheck = wx.CheckBox(self.panel, pos=(x,y))
        self.portCheck.SetValue(self._port)
        
        x, y = self.exp_pos
        self.expCheck = wx.CheckBox(self.panel, pos=(x,y))
        self.expCheck.SetValue(self._exp)
        
        x, y = self.int_pos
        self.intCheck = wx.CheckBox(self.panel, pos=(x,y))
        self.intCheck.SetValue(self._int)
        
        #bitmap
        self.background = imgs.param_box_setup_bg.GetBitmap()
        
        #Binding events
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)
        self.panel.Bind(wx.EVT_TEXT, self.setText, self.textCtrl)
        self.panel.Bind(wx.EVT_TEXT, self.setMin, self.minCtrl)
        self.panel.Bind(wx.EVT_TEXT, self.setMax, self.maxCtrl)
        self.textCtrl.Bind(wx.EVT_SET_FOCUS, self.OnFocusCtrl, self.textCtrl)
        self.minCtrl.Bind(wx.EVT_SET_FOCUS, self.OnFocusCtrl, self.minCtrl)
        self.maxCtrl.Bind(wx.EVT_SET_FOCUS, self.OnFocusCtrl, self.maxCtrl)
        self.panel.Bind(wx.EVT_TEXT_ENTER, self.OnEnter, self.textCtrl)
        self.panel.Bind(wx.EVT_TEXT_ENTER, self.OnEnter, self.minCtrl)
        self.panel.Bind(wx.EVT_TEXT_ENTER, self.OnEnter, self.maxCtrl)
        self.panel.Bind(wx.EVT_CHOICE, self.setPrec, self.precCtrl)
        self.panel.Bind(wx.EVT_CHECKBOX, self.setPort, self.portCheck)
        self.panel.Bind(wx.EVT_CHECKBOX, self.setExp, self.expCheck)
        self.panel.Bind(wx.EVT_CHECKBOX, self.setFloor, self.intCheck)
        
    def OnPaint(self, evt):
        w, h = self.GetSize()
        dc = wx.PaintDC(self.panel)
        
        #draw bg
        dc.DrawBitmap(self.background,0,0)
        
        font = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, faceName="Helvetica")
        
        #Texte
        dc.SetTextForeground("#FFFFFF")
        dc.SetFont(font)
        dc.DrawText("Name", self.leftMargin, self.topMargin)
        dc.DrawText("Min", self.leftMargin, self.min_pos[1]+6)
        dc.DrawText("Max", self.leftMargin, self.max_pos[1]+6)
        dc.DrawText("Prec.", self.leftMargin, self.prec_pos[1]+6)
        dc.DrawText("Port", self.leftMargin+23, self.port_pos[1]+5)
        dc.DrawText("Exp", self.exp_pos[0]+23, self.exp_pos[1]+5)
        dc.DrawText("Int", self.int_pos[0]+23, self.int_pos[1]+5)
    
    def OnEnter(self, evt):
        evt.Skip()
        self.callable()
        self.Hide()
        self.parent._destroySettingsWindow()
        
    def OnFocusCtrl(self, evt):
        evt.Skip()
        evt.GetEventObject().SelectAll()

    def getFocus(self):
        self.SetFocus()
        
    def setText(self, evt):
        self._text = self.textCtrl.GetValue()

    def setMin(self, evt):
        try:
            self._min = float(self.minCtrl.GetValue().replace(',','.'))
        except:
            pass
        
    def setMax(self, evt):
        try:
            self._max = float(self.maxCtrl.GetValue().replace(',','.'))
        except:
            pass
        
    def setPort(self, evt):
        self._port = bool(self.portCheck.GetValue())
        
    def setExp(self, evt):
        self._exp = bool(self.expCheck.GetValue())
        
    def setPrec(self, evt):
        self._prec = self.precCtrl.GetSelection()+1
        
    def setFloor(self, evt):
        self._int = bool(self.intCheck.GetValue())

class WheelsBox(wx.Panel):
    def __init__(self, parent, bend_obj, mod_obj, pos, height):
        wx.Panel.__init__(self, parent, -1, pos=pos, size=(config.WHEELS_BOX_WIDTH,height))
        self.parent = parent
        self.width, self.height = self.GetSize()
        self.active_fill_color = (31,136,175,77)
        
        self.bend_obj = bend_obj
        self.mod_obj = mod_obj
        
        #bitmap
        self.background = imgs.bend_mod_bg.GetBitmap()
        
        self._initBoxCoords()
        
        #state varialbe
        self.UNUSED = False
        self.IDLE = False
        
        #Binding events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
    def _scaleTranspo(self, value, range):
        try:
            semi = math.log(value,2)*12
        except:
            return 0
        
        if semi > range:
            return range/float(range)
        if semi < -range:
            return -range/float(range)
        return semi/float(range)
        
    def _initBoxCoords(self):
        self.y1 = 25
        self.y2 = 212
        self.box_height = self.y2-self.y1
        self.bbox_x1 = 8
        self.bbox_x2 = 41
        self.bbox_width = self.bbox_x2-self.bbox_x1
        self.bbox_center = 118
        self.bbox_half_travel = self.bbox_center-self.y1
        self.mbox_x1 = 59
        self.mbox_x2 = 93
        self.mbox_width = self.mbox_x2-self.mbox_x1
        
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        dc.Clear()
        
        dc.DrawBitmap(self.background,0,0)
        
        dc.SetBrush(wx.Brush(self.active_fill_color))
        dc.SetPen(wx.Pen(self.active_fill_color, 1))
        
        ##Draw reference bars
        ##Bend wheel
        y = math.ceil(self.bbox_center-(self.bbox_half_travel*self._scaleTranspo(self.bend_obj.get(), self.bend_obj._brange)))
        points = [(self.bbox_x1,self.bbox_center),
                  (self.bbox_x1,y),
                  (self.bbox_x2,y),
                  (self.bbox_x2,self.bbox_center)]
        dc.DrawPolygon(points)
        ##Mod wheel
        height = math.ceil(self.box_height*self.mod_obj.get())
        y = self.y2-height
        dc.DrawRectangle(self.mbox_x1, y, self.mbox_width, height)
        ##Ben wheel middle line
        dc.GetPen().SetWidth(2)
        dc.DrawLine(self.bbox_x1,self.bbox_center-1,self.bbox_x2,self.bbox_center-1)
        
    def IsIdle(self):
        return self.IDLE
        
    def IsUnused(self):
        return self.UNUSED
    
    def unlink(self, namespace):
        pass
        
    def disable(self, namespace):
        pass

class BoxBase(wx.Panel):
    def __init__(self, parent, pos, size):
        wx.Panel.__init__(self, parent, -1, pos=pos, size=size)
        
        ##bitmaps
        self.active_bg = imgs.param_box_active_bg.GetBitmap()
        self.inactive_bg = imgs.param_box_inactive_bg.GetBitmap()
        
        ##colours
        self.active_color = "#d8ff00"
        self.inactive_color = "#f0f4d7"
        self.active_fill_color = (216,255,0,51)
        self.inactive_fill_color = (240,244,215,38)
        
        ##Variables generales
        self.parent = parent
        self.width, self.height = size
        
        ##Variables pour le MatchMode
        self.MATCH_MODE = False
        self.preset_value = None
        self.match_prec = .02
        
        ##Variables d'etat
        self.MIDI_LEARN = False
        self.settingsWindow = None
        
        #Binding events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
    def OnPaint(self, evt):
        evt.Skip()
        
    def ShowPatchWindow(self, evt):
        if not evt.ShiftDown() and not evt.ControlDown() and not evt.CmdDown():
            if self.parent.patchWindow._obj == self:
                self.parent.patchWindow.HideWindow()
            else:
                if not self.MIDI_LEARN and self.settingsWindow == None:
                    self.parent._last_changed = self
                    self.parent.patchWindow.ShowWindow(evt.GetEventObject())
        
class ParamBox(BoxBase):
    """
    class ParamBox
    
    parametres :
        - list : [ text, MidiControl (, float_precision) ]
    """
    def __init__(self, parent, pos, size, list):
        BoxBase.__init__(self, parent, pos=pos, size=size)
        
        #Variables generales
        self.text = list[0]
        self.pyo_obj = list[1]
        self.ctl_num = self.pyo_obj.getCtlNumber()
        self.last_value = None
        self._boxRange = 123
        if len(list) == 3:
            self.val_prec = list[2]
        else:
            self.val_prec = 2
        
        #fonts
        self.valueFont = wx.Font(config.FONT_SIZE['value'], wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.titleFont = wx.Font(config.FONT_SIZE['title'], wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.unusedFont = wx.Font(config.FONT_SIZE['unused'], wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.midiLearnFont = wx.Font(config.FONT_SIZE['midilearn'], wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        
        #state variable
        self.IDLE = False
        self.UNUSED = True
        
        #empty bitmap to store a snapshot of the parambox if idle
        self.buffer = wx.EmptyBitmap(size[0], size[1])
        
        #Binding events
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.parent.Bind(wx.EVT_MOVE, self.OnMove)
        self.parent.Bind(wx.EVT_CLOSE, self.OnQuit)

    def OnMove(self, evt):
        evt.Skip()
        if hasattr(self, 'settingsWindow'):
            if isinstance(self.settingsWindow, wx.Frame):
                pos = self.GetScreenPosition()+(self.GetSize()[0]-10, (self.GetSize()[1]-self.settingsWindow.GetSize()[1])/2)
                self.settingsWindow.SetPosition(pos)
        
    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self, self.buffer)
        ##La boite de controle est inutilisee
        if self.UNUSED:
            self.OnPaintUnused(dc)
        ##La boite de controle est utilisee
        else:
            value = self.pyo_obj.get()
            ##Verifie si le carre doit etre dessine actif ou inactif
            if value != self.last_value or self.parent._last_changed == self or self.MATCH_MODE or self.MIDI_LEARN:
                self.OnPaintActive(dc, value)
            else:
                self.OnPaintInactive(dc, value)
        
    def OnPaintUnused(self, dc):
        if not self.IDLE:
            self.IDLE = True
            #bg bitmap
            dc.DrawBitmap(self.inactive_bg,0,0)
            #Unused text
            dc.SetFont(self.unusedFont)
            dc.SetTextForeground(self.inactive_color)
            w,h = dc.GetTextExtent(self.text)
            x = (self.width - w)/2
            y = (self.height - h)/2
            dc.DrawText(self.text, x, y)
        
    def OnPaintActive(self, dc, value):
        self.parent._last_changed = self
        self.IDLE = False
        #basic active style
        dc.DrawBitmap(self.active_bg,0,0)
        dc.SetTextForeground(self.active_color)
        dc.SetPen(wx.Pen(self.active_fill_color,1))
        dc.SetBrush(wx.Brush(self.active_fill_color))
        
        if self.MIDI_LEARN:
            #MIDI LEARN text
            dc.SetFont(self.midiLearnFont)
            w,h = dc.GetTextExtent("MIDI")
            x = (self.width - w)/2
            dc.DrawText("MIDI", x, 15)
            w,h = dc.GetTextExtent("LEARN")
            x = (self.width - w)/2
            dc.DrawText("LEARN", x, 12+h)
            
            #ctl number
            dc.SetFont(self.valueFont)
            ctl_txt = "%d" % self.ctl_num
            w,h = dc.GetTextExtent(ctl_txt)
            x = (self.width - w)/2
            dc.DrawText(ctl_txt, x, 65)
        else:
            #draw level indicator
            width = (value-self.pyo_obj.getMin())/self.pyo_obj.getRange()*self._boxRange
            dc.DrawRectangle(4,4,width,102)
            
            #current value text and pos
            dc.SetFont(self.valueFont)
            precision = "%." + str(self.val_prec) + "f"
            text_value = precision % value
            w,h = dc.GetTextExtent(text_value)
            x = (self.width - w)/2
            
            if self.MATCH_MODE:
                #if relatively close to preset value, go to next control
                if value > self.preset_value*(1-self.match_prec) and value < self.preset_value*(1+self.match_prec):
                    self.MATCH_MODE = False
                    self.parent.nextPreset()
                else:
                    #affichage de la valeur courante
                    dc.DrawText(text_value, x, 40)
                    
                    #affichage de la valeur du preset
                    dc.SetFont(self.midiLearnFont)
                    dc.SetTextForeground("#EDAF42")
                    text_preset_value = "%.3f" % self.preset_value
                    w,h = dc.GetTextExtent(text_preset_value)
                    x = (self.width - w)/2
                    dc.DrawText(text_preset_value, x, 53+h)
                    dc.SetTextForeground(self.active_color)
            else:
                dc.DrawText(text_value, x, 50)
            #important pour que self.parent.last_changed soit modifiee
            self.last_value = value
            
            #Draw title text
            dc.SetFont(self.titleFont)
            w,h = dc.GetTextExtent(self.text)
            x = (self.width - w)/2
            dc.DrawText(self.text, x, 20)
        
    def OnPaintInactive(self, dc, value):
        if not self.IDLE:
            self.IDLE = True
            dc.DrawBitmap(self.inactive_bg,0,0)
            dc.SetTextForeground(self.inactive_color)
            dc.SetPen(wx.Pen(self.inactive_fill_color,1))
            dc.SetBrush(wx.Brush(self.inactive_fill_color))
            
            #draw level indicator
            width = (value-self.pyo_obj.getMin())/self.pyo_obj.getRange()*self._boxRange
            dc.DrawRectangle(4,4,width,102)
            
            #draw current value
            dc.SetFont(self.valueFont)
            precision = "%." + str(self.val_prec) + "f"
            text_value = precision % value
            w,h = dc.GetTextExtent(text_value)
            x = (self.width - w)/2
            dc.DrawText(text_value, x, 50)
            
            #Draw title text
            dc.SetFont(self.titleFont)
            w,h = dc.GetTextExtent(self.text)
            x = (self.width - w)/2
            dc.DrawText(self.text, x, 20)

    def OnMouseDown(self, evt):
        shift = evt.ShiftDown()
        cmd = evt.CmdDown()
        if shift and not self.UNUSED:
            if self.settingsWindow == None:
                self._showSettingsWindow()
        elif cmd and not self.UNUSED:
            self._toggleMidiLearn()
        else:
            if self.settingsWindow != None:
                self._setParams()
                #le timer permet d'eviter que la PatchWindow s'ouvre
                #chaque fois qu'on ferme la boite de settings
                #ou qu'on desactive le Midi Learn
                later = wx.CallLater(10, self._destroySettingsWindow)
            if self.MIDI_LEARN:
                later = wx.CallLater(10, self._toggleMidiLearn)
        self.ShowPatchWindow(evt)

    def OnQuit(self, evt):
        evt.Skip()
        if self.settingsWindow != None:
            self.settingsWindow.Destroy()
    
    def IsIdle(self):
        return self.IDLE
    
    def IsUnused(self):
        return self.UNUSED
    
    def disable(self, namespace):
        """
        Deconnecte le controle midi et place la ParamBox en mode Unused.
        """
        self.pyo_obj.unlink(namespace)
        self.text = "Unused"
        self.IDLE = False
        self.UNUSED = True
        self.Refresh()
    
    def enable(self, text):
        self.text = text
        self.UNUSED = False
        
    def unlink(self, namespace):
        """
        Defait le lien du controle midi avec le parametre courant en vue
        de faire un nouveau lien
        """
        if self.pyo_obj != None:
            self.pyo_obj.unlink(namespace)
    
    def getMidiControl(self):
        return self.pyo_obj._obj
        
    def getText(self):
        return self.text

    def matchValue(self, value):
        self.MATCH_MODE = True
        self.preset_value = value
        
    def _toggleMidiLearn(self):
        if self.MIDI_LEARN:
            self.MIDI_LEARN = False
            self.ctl_scan.stop()
            del self.ctl_scan
            self.pyo_obj.setCtlNumber(self.ctl_num)
        else:
            self.MIDI_LEARN = True
            self.ctl_scan = CtlScan(self._setCtlNumLearn, False)

    def _showSettingsWindow(self):
        self.parent._last_changed = self
        self.settingsWindow = ParamBoxSettingsWindow(self, (0,0), self._getParams(), self._setParams)
        pos = self.GetScreenPosition()+(self.GetSize()[0]-5, -10)
        self.settingsWindow.SetPosition(pos)
        self.settingsWindow.Show()
        
    def _destroySettingsWindow(self):
        self.settingsWindow.Show(False)
        self._destroyTimer = wx.CallLater(500, self.settingsWindow.Destroy)
        self.settingsWindow = None
                
    def _getParams(self):
        return [self.pyo_obj.getMin(), self.pyo_obj.getMax(), self.pyo_obj.hasPort(),
                self.pyo_obj.hasExp(), self.text, self.val_prec, self.pyo_obj.hasFloor()]
    
    def _setParams(self):
        self.pyo_obj.setScale(self.settingsWindow._min, self.settingsWindow._max)
        self.pyo_obj.setPort(self.settingsWindow._port)
        self.pyo_obj.setExp(self.settingsWindow._exp)
        self.text = self.settingsWindow._text
        self.val_prec = self.settingsWindow._prec
        self.pyo_obj.setFloor(self.settingsWindow._int)
    
    def _setCtlNumLearn(self, num):
        self.ctl_num = num

class StatusBarPanel(wx.Panel):
    def __init__(self, parent, pos, size, numChnls):
        wx.Panel.__init__(self, parent, -1, pos, size)
        
        #vu meter x pos
        self.vm_x = parent.GetSize()[0]-242-15
        #master volume x pos
        self.mv_x = parent.GetSize()[0]/2-80
        #rec section
        self.rec_x = 255

        #bouton d'enregistrement et txtCtrl
        self.rec_btn = buttons.RecButton(self, (self.rec_x,6))
        self.rec_btn.disable()
        
        self.recTxtCtrl = controls.PSRecordTextCtrl(self, (self.rec_x+32, 12), "No tracks")
        x = self.recTxtCtrl.GetSize()[0]+self.recTxtCtrl.GetPosition()[0]
        
        self.open_rec_btn = buttons.OpenRecButton(self, (x, 12))
        
        #fenetre des pistes enregistrees
        self.tracks_window = RecordedTracksWindow(self, self.GetParent().server, self.GetParent().script_namespace)
        
        #master volume slider
        self.vol_slider = controls.VolumeSlider(self, (self.mv_x+100,21), 150)
        self._changeMasterVol(None)
        
        #vu meter object
        self.vu_meter = controls.VuMeter(self, (self.vm_x,13), numChnls)
        self.setVuMeterPosition(numChnls)
        
        #CPU & RAM usage infos
        self.totalMem = psutil.virtual_memory()[0]
        self.python_id = self.getPythonID()
        self.python_proc = psutil.Process(self.python_id)
        
        font = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, faceName="Helvetica")
        slashFont = wx.Font(17, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, faceName="Helvetica")
        
        self.cpuText = wx.StaticText(self, -1, "", (15,21))
        self.cpuText.SetFont(font)
        self.cpuText.SetForegroundColour("#FFFFFF")
        
        self.slashes = wx.StaticText(self, -1, "//", (100,19))
        self.slashes.SetFont(slashFont)
        self.slashes.SetForegroundColour("#FFFFFF")
        
        self.ramText = wx.StaticText(self, -1, "", (130,21))
        self.ramText.SetFont(font)
        self.ramText.SetForegroundColour("#FFFFFF")
        self.updateUsage(-1)
        
        #bitmap
        self.background = imgs.status_bar_background.GetBitmap()
        #self.separator = imgs.separator.GetBitmap()
        
        #timer to update cpu and ram usage
        self._cpu_timer = wx.Timer(self, -1)
        self._cpu_timer.Start(1000)
        #timer to show record time
        self._rec_timer = wx.Timer(self, -1)
        #conserve le temps d'enregistrement en secondes
        self._rec_time = 0
        
        #Binding events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.updateUsage, self._cpu_timer)
        self.Bind(wx.EVT_TIMER, self.updateRecTime, self._rec_timer)
        self.Bind(buttons.EVT_BTN_REC, self._toggleRecording)
        self.Bind(buttons.EVT_BTN_OPEN, self._showRecordedTracks)
        self.vol_slider.Bind(controls.EVT_VOL_CHANGED, self._changeMasterVol)
        
    def _changeMasterVol(self, evt):
        self.GetParent().server.amp = self.vol_slider.getValue()
        
    def _setMasterVolSlider(self, value):
        self.vol_slider.setValue(value)
        
    def _toggleRecording(self, evt):
        if evt.GetState():
            info = self.tracks_window.startRecording()
            if info == 0:
                self.rec_btn._setState(False)
                script_name = os.path.split(self.GetParent().menu_panel._script_path)[1]
                self.GetParent().exc_win.printException(script_name, "Cannot record because the script does not have a 'mix' object.")
            else:
                self._rec_time = 0
                self.recTxtCtrl.SetText("Track %d"%info[1])
                self.recTxtCtrl.SetTime("00:00")
                self._rec_timer.Start(1000)
                self.recTxtCtrl.SetRecState(evt.GetState())
        else:
            self.tracks_window.stopRecording()
            self._rec_timer.Stop()
            self.recTxtCtrl.SetRecState(evt.GetState())
        
    def _showRecordedTracks(self, evt):
        if evt.GetState():
            self.tracks_window.ShowWindow(self.GetParent().GetPosition())
        else:
            self.tracks_window.HideWindow()
    
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        dc.Clear()
        
        dc.DrawBitmap(self.background,0,0)
        
        font = wx.Font(13, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, faceName="Helvetica")
        dc.SetFont(font)
        dc.SetTextForeground("#FFFFFF")
        dc.DrawText("Master volume", self.mv_x, 21)
        
        dc.DrawText("Output level", self.vm_x-80, 21)
        
    def getPythonID(self):
        create_time = None
        id = None
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name'])
            except psutil.NoSuchProcess:
                pass
            else:
                if pinfo['name'] == 'Python':
                    if create_time == None:
                        create_time = proc.create_time()
                        id = pinfo['pid']
                    elif proc.create_time() > create_time:
                        create_time = proc.create_time()
                        id = pinfo['pid']
        return id

    def setNchnls(self, num):
        self.vu_meter.setNumSliders(num)
        self.setVuMeterPosition(num)
            
    def setVuMeterPosition(self, chnls):
        if chnls == 1:
            self.vu_meter.SetPosition((self.vm_x,19))
        elif chnls == 2:
            self.vu_meter.SetPosition((self.vm_x,13))
        elif chnls == 3:
            self.vu_meter.SetPosition((self.vm_x,8))
        elif chnls == 4:
            self.vu_meter.SetPosition((self.vm_x,2))
        
    def updateUsage(self, evt):
        cpu = self.python_proc.cpu_percent()
        self.cpuText.SetLabel("CPU : %.1f%%" % cpu)
        mem = self.python_proc.memory_percent()/100. * self.totalMem / (1024**2.)
        self.ramText.SetLabel("RAM : %.2f Mb" % mem)
        
    def updateRecTime(self, evt):
        self._rec_time += 1
        min = self._rec_time/60
        sec = self._rec_time%60
        if min > 9: min = "%d" % min
        else: min = "0%d" % min
        if sec > 9: sec = "%d" % sec
        else: sec = "0%d" % sec
        self.recTxtCtrl.SetTime(min+":"+sec)
        
class MenuPanel(wx.Panel):
    def __init__(self, parent, pos, size, namespace):
        self.script_namespace = namespace
        wx.Panel.__init__(self, parent, -1, pos, size)
        
        #variable pour stocker le chemin d'acces au script
        self._script_path = ""
        #variable d'etat du script
        self.IS_RUNNING = False
        #contient tous les objets pyo présentement en execution
        self.pyo_objs = {}
        #contient toutes les variables declarees dans le script en execution
        self.script_vars = {}
        
        #positions des elements
        self.top_margin = 16
        self.btn_open_x = 154
        self.btn_save_x = self.btn_open_x+77
        self.script_txt_x = self.btn_save_x+93
        self.adsr_section = self.script_txt_x+448
        
        self.font = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, faceName="Helvetica")
        
        ##Declaration des boutons et labels de gauche a droite
        #boutons open et save
        self.btn_open = buttons.OpenButton(self, (self.btn_open_x,self.top_margin))
        self.btn_save = buttons.SaveButton(self, (self.btn_save_x,self.top_margin))
        
        #label du nom du script
        self.script_name = controls.PSScriptTextCtrl(self, (self.script_txt_x, 18), "No script selected")
        
        #bouton run
        x = self.script_name.GetWidth()+self.script_name.GetPosition()[0]
        self.btn_run = buttons.RunButton(self, (x,self.script_name.GetPosition()[1]))
        self.btn_run.disable()
        
        self.server_setup_btn = buttons.ServerSetupButton(self, (self.GetSize()[0]-17,0))
        
        #statut du script
        x += self.btn_run.GetSize()[0] + 10
        self.script_status = wx.StaticText(self, -1, "|  Stopped", (x,self.top_margin+8))
        self.script_status.SetFont(self.font)
        self.script_status.SetForegroundColour("#FFFFFF")
        
        #metronome
        x += self.script_status.GetSize()[0]+35
        self.metro = controls.PSClick(self, (x,self.top_margin-2), 120, self.GetParent().server.getNchnls())
        
        #adsr envelope knobs
        self._attackKnob = controls.PSSmallRotaryKnob(self, pos=(self.adsr_section,10), min=0, max=1, text='A', ratio=100, valprec=3)
        
        x = self._attackKnob.GetPosition()[0]+self._attackKnob.GetSize()[0]+10
        self._decayKnob = controls.PSSmallRotaryKnob(self, (x,10), 0, 1, 'D', 80, 2)
        
        x = self._decayKnob.GetPosition()[0]+self._decayKnob.GetSize()[0]+10
        self._sustainKnob = controls.PSSmallRotaryKnob(self, (x,10), 0, 1, 'S', 80, 2)
        
        x = self._sustainKnob.GetPosition()[0]+self._sustainKnob.GetSize()[0]+10
        self._releaseKnob = controls.PSSmallRotaryKnob(self, (x,10), 0, 4, 'R', 50, 2)
        
        #txt ctrl interface
        self.snd_card_ctrl = controls.PSTextCtrl(self, (0, 0), "Dummy text")
        posx = self.GetSize()[0] - self.snd_card_ctrl.GetWidth() - self.server_setup_btn.GetSize()[0] - 15
        self.snd_card_ctrl.SetPosition((posx,12))
        
        fontSmall = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, faceName="Helvetica")
        
        #quick info
        self.quick_info = wx.StaticText(self, -1, "sr : 44.1 | bfs : 256 | 2 chnls", (posx-22,40))
        self.quick_info.SetForegroundColour("#FFFFFF")
        self.quick_info.SetFont(fontSmall)
        
        #bitmaps
        self.back = imgs.menu_background.GetBitmap()
        self.logo = imgs.logo.GetBitmap()
        self.separator = imgs.separator.GetBitmap()
        
        #Binding events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.btn_open.Bind(buttons.EVT_BTN_CLICKED, self._openDialog)
        self.btn_save.Bind(buttons.EVT_BTN_CLICKED, self.GetParent().savePreset)
        self.server_setup_btn.Bind(buttons.EVT_BTN_CLICKED, self.ShowServerSetup)
        
    def __getitem__(self, i):
        if i == 'click':
            return self.metro[i]
    
    def reinit(self):
        self._attackKnob.reinit()
        self._decayKnob.reinit()
        self._sustainKnob.reinit()
        self._releaseKnob.reinit()
        self.metro.reinit(self.GetParent().server.getNchnls())
    
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        dc.Clear()
        dc.DrawBitmap(self.back, 0, 0)
        dc.DrawBitmap(self.logo, 0, 0)
        dc.DrawBitmap(self.separator, 133, 7)
    
    def _openDialog(self, evt):
        dlg = wx.FileDialog(
            self, message="Choose a script",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard="Python source (*.py)|*.py",
            style=wx.OPEN | wx.CHANGE_DIR
            )
            
        if dlg.ShowModal() == wx.ID_OK:
            self._script_path = dlg.GetPath()
            self._addPathToRecent()
            self._setScriptName()
            self.GetParent().enableMenuItems()
            
    def _addPathToRecent(self):
        try:
            index = config.RECENT_SCRIPTS.index(self._script_path)
            config.RECENT_SCRIPTS.pop(index)
        except:
            pass
        finally:
            config.RECENT_SCRIPTS.insert(0,self._script_path)
            if len(config.RECENT_SCRIPTS)>10:
                config.RECENT_SCRIPTS.pop(-1)
        
    def _runScript(self, evt):
        if self.IS_RUNNING:
            self.IS_RUNNING = False
            #stopping and deleting all objects from the script
            self._cleanScriptVars()
            #updating basic stuff
            self.btn_open.enable()
            self.server_setup_btn.enable()
            self._updateStatus()
            return 0
        else:
            self.IS_RUNNING = True
            #actually running the script
            self._before_exec = self.script_namespace.copy()
            try:
                execfile(self._script_path, self.script_namespace)
            except Exception:
                exc_type, exc_name, exc_tb = sys.exc_info()
                string = traceback.format_exc(exc_tb)
                self.GetParent().exc_win.newException(os.path.split(self._script_path)[1], string)
                self._getScriptVars()
                return -1
            self._getScriptVars()
            #add pyo objects to the PatchWindow
            for obj in self.pyo_objs:
                self.GetParent().patchWindow.addObject(obj)
            #updating basic stuff
            self.btn_open.disable()
            self.server_setup_btn.disable()
            self._updateStatus()
            return 1
    
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
            except:
                pass
            string = "del %s" % obj
            exec string in self.script_namespace
        self.pyo_objs.clear()
        for var in self.script_vars:
            string = "del %s" % var
            exec string in self.script_namespace
        self.script_vars.clear()
    
    def _setScriptName(self):
        name = os.path.split(self._script_path)[1]
        self.script_name.SetText(utils.shortenText(name,20))
        self.btn_run.enable()
        wx.CallLater(180, self._moveScriptNameCtrl)
        
    def _moveScriptNameCtrl(self):
        #reposition du btn run
        x = self.script_name.GetWidth()+self.script_name.GetPosition()[0]
        self.btn_run.SetPosition((x,self.btn_run.GetPosition()[1]))
        #reposition le statut par rapport au nouveau nom de script
        x += self.btn_run.GetSize()[0] + 10
        self.script_status.SetPosition((x,self.script_status.GetPosition()[1]))
        
    def _updateStatus(self):
        #met a jour le statut du script
        if self.IS_RUNNING:
            self.script_status.SetLabel("|  Running")
        else:
            self.script_status.SetLabel("|  Stopped")
            
    def _pauseMidiControl(self, ctlnum):
        self.GetParent()._pauseMidiControl(ctlnum)
        
    def _resumeMidiControl(self, ctlnum):
        self.GetParent()._resumeMidiControl(ctlnum)
    
    def setScriptFromRecentMenu(self, evt):
        item = evt.GetEventObject().FindItemById(evt.GetId())
        self._script_path = item.GetText()
        self._addPathToRecent()
        self._setScriptName()
        self.GetParent().enableMenuItems()
    
    def getAdsrCtlNums(self):
        return (self._attackKnob.ctl_num, self._decayKnob.ctl_num, 
                self._sustainKnob.ctl_num, self._releaseKnob.ctl_num)
    
    def setServerPanel(self, window):
        self.serverSetupPanel = window
        
    def setAdsrCallbacks(self, callbacks):
        self._attackKnob.setCallback(callbacks[0])
        self._decayKnob.setCallback(callbacks[1])
        self._sustainKnob.setCallback(callbacks[2])
        self._releaseKnob.setCallback(callbacks[3])
        
    def setAdsrValues(self, values):
        self._attackKnob.setValue(values[0])
        self._decayKnob.setValue(values[1])
        self._sustainKnob.setValue(values[2])
        self._releaseKnob.setValue(values[3])
        
    def setAdsrCtlNums(self, ctl_nums):
        self._attackKnob.ctl_num = ctl_nums[0]
        self._decayKnob.ctl_num = ctl_nums[1]
        self._sustainKnob.ctl_num = ctl_nums[2]
        self._releaseKnob.ctl_num = ctl_nums[3]
    
    def ShowServerSetup(self, evt):
        if self.serverSetupPanel.IsShown():
            self.serverSetupPanel.HideWindow()
        else:
            self.serverSetupPanel.ShowWindow()
    
    def updateInterfaceTxt(self):
        self.snd_card_ctrl.SetText(self.serverSetupPanel.getOutputInterface())
        
    def updateSampRateBufSizeTxt(self):
        text = "sr : %.1f | bfs : %d | %d chnls" % (self.serverSetupPanel.getSamplingRate()/1000., self.serverSetupPanel.getBufferSize(), self.serverSetupPanel.getNchnls())
        self.quick_info.SetLabel(text)

class ExportWindow(wx.Dialog):
    def __init__(self, parent, prefs=None):
        wx.Dialog.__init__(self, parent, -1, "Export Samples", size=(410,370))
        self.path = config.HOME_PATH
        self.bg = imgs.export_win_bg.GetBitmap()
        
        #Y positions
        outputFolder = 14
        exportRange = 85
        fileSpecs = 210
        margin_x = 14
        
        #Output folder
        label = wx.StaticText(self, -1, "Output Folder", (margin_x,outputFolder))
        label.SetForegroundColour("#d8ff00")
        btn = buttons.PSRectangleButton(self, (margin_x+5,outputFolder+23), (65,23), "Choose...")
        self.Bind(buttons.EVT_BTN_CLICKED, self._dirDialog, btn)
        self.pathText = wx.StaticText(self, -1, utils.shortenText(self.path, 40), (100, outputFolder+25))
        self.pathText.SetForegroundColour("#f0f4d7")
        
        #Midi notes
        label = wx.StaticText(self, -1, "Export Range (Midi Notes)", (margin_x,exportRange))
        label.SetForegroundColour("#d8ff00")
        #min
        self.minText = wx.StaticText(self, -1, "From : %s(%d)"%(config.MIDI_NOTES_NAMES[21],21), (margin_x+5,exportRange+25))
        self.minText.SetForegroundColour("#f0f4d7")
        self.midiMin = wx.Slider(self, -1, 21, 0, 127, pos=(margin_x+5, exportRange+50), size=(127,-1))
        #max
        self.maxText = wx.StaticText(self, -1, "To : %s(%d)"%(config.MIDI_NOTES_NAMES[106],106), (margin_x+160,exportRange+25))
        self.maxText.SetForegroundColour("#f0f4d7")
        self.midiMax = wx.Slider(self, -1, 106, 0, 127, pos=(margin_x+160, exportRange+50), size=(127,-1))
        
        #Velocity steps
        label = wx.StaticText(self, -1, "Velocity Steps :", (margin_x+5,exportRange+80))
        label.SetForegroundColour("#f0f4d7")
        self.velSteps = wx.TextCtrl(self, pos=(margin_x+103, exportRange+80), size=(30,-1), style=wx.NO_BORDER)
        self.velSteps.SetValue('3')
        self.velSteps.SetBackgroundColour("#3d3d3d")
        self.velSteps.SetForegroundColour("#f0f4d7")
        
        #Note dur
        label = wx.StaticText(self, -1, "Note Duration :", (margin_x+165,exportRange+80))
        label.SetForegroundColour("#f0f4d7")
        self.noteDur = wx.TextCtrl(self, pos=(margin_x+262, exportRange+80), size=(30,-1), style=wx.NO_BORDER)
        self.noteDur.SetValue('5')
        self.noteDur.SetBackgroundColour("#3d3d3d")
        self.noteDur.SetForegroundColour("#f0f4d7")
        secs = wx.StaticText(self, -1, "secs.", (315,exportRange+80))
        secs.SetForegroundColour("#f0f4d7")
        
        #File specs
        label = wx.StaticText(self, -1, "File Specifications", (margin_x,fileSpecs))
        label.SetForegroundColour("#d8ff00")
        #file format
        formats = ['.wav','.aiff','.au','.raw','.sd2','.flac','.caf','.ogg']
        label = wx.StaticText(self, -1, "Format :", (margin_x+5,fileSpecs+29))
        label.SetForegroundColour("#f0f4d7")
        self.fileFormat = wx.Choice(self, -1, (margin_x+60, fileSpecs+27), choices=formats)
        
        #bit depth
        bits = ['16 bits int', '24 bits int', '32 bits int', '32 bits float', '64 bits float',
                'U-Law encoded', 'A-Law encoded']
        label = wx.StaticText(self, -1, "Bit Depth :", (margin_x+160,fileSpecs+29))
        label.SetForegroundColour("#f0f4d7")
        self.bitDepth = wx.Choice(self, -1, (margin_x+230, fileSpecs+27), choices=bits)
        
        #File length
        label = wx.StaticText(self, -1, "Length :", (margin_x+5,fileSpecs+59))
        label.SetForegroundColour("#f0f4d7")
        self.fileLength = wx.TextCtrl(self, pos=(margin_x+60, fileSpecs+60), size=(30,-1), style=wx.NO_BORDER)
        self.fileLength.SetBackgroundColour("#3d3d3d")
        self.fileLength.SetForegroundColour("#f0f4d7")
        self.fileLength.SetValue('5')
        secs = wx.StaticText(self, -1, "secs.", (margin_x+100,fileSpecs+59))
        secs.SetForegroundColour("#f0f4d7")
        
        btn = buttons.PSRectangleButton(self, (120,310), (65,23), "OK", id=wx.ID_OK)
        self.Bind(buttons.EVT_BTN_CLICKED, self._endModal, btn)
        btn = buttons.PSRectangleButton(self, (193,310), (65,23), "CANCEL", id=wx.ID_CANCEL)
        self.Bind(buttons.EVT_BTN_CLICKED, self._endModal, btn)
        
        if prefs != None:
            self._updateFields(prefs)
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SLIDER, self.OnChangeMin, self.midiMin)
        self.Bind(wx.EVT_SLIDER, self.OnChangeMax, self.midiMax)
        
    def OnPaint(self, evt):
        w,h = self.GetSize()
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bg, 0, 0)
        color = utils.getTransparentColour(56,"#4f4f4f")[0]
        dc.SetBrush(wx.Brush(color))
        dc.SetPen(wx.Pen(color,1))
        dc.DrawRectangle(7,7,w-14,63)
        dc.DrawRectangle(7,80,w-14,110)
        dc.DrawRectangle(7,200,w-14,95)
        
    def OnChangeMin(self, evt):
        i = self.midiMin.GetValue()
        text = "From : %s(%d)"%(config.MIDI_NOTES_NAMES[i],i)
        self.minText.SetLabel(text)
        
    def OnChangeMax(self, evt):
        i = self.midiMax.GetValue()
        text = "To : %s(%d)"%(config.MIDI_NOTES_NAMES[i],i)
        self.maxText.SetLabel(text)
        
    def _endModal(self, evt):
        self.EndModal(evt.GetId())
    
    def _dirDialog(self, evt):
        dlg = wx.DirDialog(self, "Choose a directory", defaultPath=self.path)
        if dlg.ShowModal() == wx.ID_OK:
            self.path = dlg.GetPath()
            self.pathText.SetLabel(utils.shortenText(self.path, 44))
        dlg.Destroy()
        
    def _updateFields(self, prefs):
        self.path = prefs['path']
        self.pathText.SetLabel(self.path)
        self.midiMin.SetValue(prefs['midimin'])
        self.midiMax.SetValue(prefs['midimax'])
        self.velSteps.SetValue(str(prefs['velsteps']))
        self.noteDur.SetValue(str(prefs['notedur']))
        self.fileFormat.SetSelection(prefs['format'])
        self.bitDepth.SetSelection(prefs['bitdepth'])
        self.fileLength.SetValue(str(prefs['filelength']))
        
    def getValues(self):
        return {'path':self.path,
                'midimin':self.midiMin.GetValue(),
                'midimax':self.midiMax.GetValue(),
                'velsteps':int(self.velSteps.GetValue()),
                'notedur':float(self.noteDur.GetValue()),
                'format':self.fileFormat.GetSelection(),
                'bitdepth':self.bitDepth.GetSelection(),
                'filelength':float(self.fileLength.GetValue())}

class PSExceptionWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Script Errors Log", (100,100), (500,200))
        self.panel = wx.Panel(self, -1, (0,0), self.GetSize())
        self.text = wx.TextCtrl(self.panel, -1, "", (0,0), self.GetSize(), style=wx.TE_MULTILINE|wx.TE_READONLY)
        
        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        self.Bind(wx.EVT_SIZE, self.OnSizeChange)
        
    def OnQuit(self, evt):
        self.Show(False)
        
    def OnSizeChange(self, evt):
        w,h = self.GetSize()
        self.panel.SetSize((w,h-23))
        self.text.SetSize((w,h-23))
        self.text.SetVirtualSize((w,h-23))
        
    def toggle(self, evt):
        if self.IsShown():
            self.Show(False)
        else:
            self.Show(True)
    
    def printException(self, script_name, text):
        self.text.AppendText(self.dateStamp(script_name))
        self.text.AppendText(text)
        self.Show(True)
    
    def newException(self, script_name, text):
        text = self.removeExtraLines(text)
        self.text.AppendText(self.dateStamp(script_name))
        self.text.AppendText(text)
        self.Show(True)
    
    def dateStamp(self, name):
        return "\n---------- Error in '%s' - %s ----------\n"%(name,time.strftime("%H:%M:%S"))
        
    def removeExtraLines(self, text):
        """
        Supprime la partie de l'exception qui refere au script de PyoSynth.
        """
        parts = text.split('\n',3)
        return parts[0]+'\n'+parts[3]

class CrashDialog(wx.Dialog):
    def __init__(self, message, caption):
        wx.Dialog.__init__(self, None, -1, '', size=(422,300))
        
        bmp = imgs.icon_64x64.GetBitmap()
        icon = wx.StaticBitmap(self, -1, bmp, pos=(18,23))
        
        caption_text = wx.StaticText(self, -1, caption, pos=(100,20))
        font = wx.SystemSettings.GetFont(0)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        font.SetPointSize(13)
        caption_text.SetFont(font)
        
        y = caption_text.GetSize()[1]+caption_text.GetPosition()[1]
        message_text = wx.StaticText(self, -1, message, pos=(100,y+10))
        message_text.Wrap(350)
        font.SetWeight(wx.FONTWEIGHT_NORMAL)
        font.SetPointSize(11)
        message_text.SetFont(font)
        
        y = message_text.GetSize()[1]+message_text.GetPosition()[1]
        comment_caption = wx.StaticText(self, -1, 'Commentaires :', pos=(100,y+20))
        comment_caption.SetFont(font)
        
        y = comment_caption.GetSize()[1]+comment_caption.GetPosition()[1]
        self._comments = wx.TextCtrl(self, -1, '', pos=(100, y+5), size=(300,100), style=wx.TE_MULTILINE)
        
        w,h = self.GetSize()
        h = self._comments.GetSize()[1]+self._comments.GetPosition()[1]+80
        self.SetSize((w,h))
        button = wx.Button(self, wx.ID_OK, pos=(w-90,h-60))
        
    def GetComments(self):
        return self._comments.GetValue().encode('utf_8')