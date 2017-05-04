#!/usr/bin/env python
# encoding: utf-8

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

import math
import pickle
import shutil
import traceback
import os
import wx
import psutil
from send2trash import send2trash

# PyoSynth custom modules import
import PSAudio
import PSButtons
import PSControls
import PSConfig
import PSUtils
import interfacePyImg as imgs
from pyoParamTree import PARAMS_TREE_DICT

if PSConfig.USE_PYO64:
    from pyo64 import *
else:
    from pyo import *


myEVT_SAVE_TRACK = wx.NewEventType()
EVT_SAVE_TRACK = wx.PyEventBinder(myEVT_SAVE_TRACK, 1)

class RecordedTrackEvent(wx.PyCommandEvent):
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)
        self._track_path = ""
        self._default_dir = PSConfig.HOME_PATH
        self._default_file = ""
        self._style = wx.DEFAULT_DIALOG_STYLE
        self._message = ""

    def SetTrackPath(self, path):
        assert isinstance(path, str), "path attribute must be of string type"
        self._track_path = path

    def SetDefaultDir(self, path):
        assert isinstance(path, str), "path attribute must be of string type"
        self._default_dir = path

    def SetDefaultFile(self, filename):
        assert isinstance(filename, str), "file attribute must be of string type"
        self._default_file = filename

    def SetStyle(self, style):
        self._style = style

    def SetMessage(self, msg):
        assert isinstance(msg, str), "msg attribute must be of string type"
        self._message = msg

    def GetTrackPath(self):
        return self._track_path

    def GetDefaultDir(self):
        return self._default_dir

    def GetDefaultFile(self):
        return self._default_file

    def GetStyle(self):
        return self._style

    def GetMessage(self):
        return self._message


class RecordedTrackElement(wx.Panel):
    size = (164, 40)
    size_old = (164, 50)

    def __init__(self, parent, pos, path, id, old):
        if old:
            self._size = RecordedTrackElement.size_old
        else:
            self._size = RecordedTrackElement.size
        wx.Panel.__init__(self, parent, pos=pos, size=self._size)

        self._path = path
        self._text = "Track %d" % id
        self._durationText = self._getDurationText()
        self._old = old
        self._selected = False
        self._hover = False

        self._sndtable = None
        self._osc = None

        self._norm_font = wx.Font(**PSConfig.FONTS['light']['norm'])
        self._small_font = wx.Font(**PSConfig.FONTS['light']['xsmall'])

        if PSConfig.USE_TRANSPARENCY:
            self.SetTransparent(255)
            if old:
                self._select_clr = wx.Colour(32, 130, 150, 255)
                self._norm_clr = wx.Colour(32, 130, 150, 20)
                self._date_txt = self._getDateText()
            else:
                self._select_clr = wx.Colour(90, 90, 90, 255)
                self._norm_clr = wx.Colour(90, 90, 90, 20)
        else:
            if old:
                self._select_clr = wx.Colour(32, 130, 150)
                self._norm_clr = wx.Colour(22, 88, 101)
                self._date_txt = self._getDateText()
            else:
                self._select_clr = wx.Colour(90, 90, 90)
                self._norm_clr = wx.Colour(60, 60, 60)

        # buttons
        self.play_btn = PSButtons.PlayTrackButton(self, (5, 20))
        self.stop_btn = PSButtons.StopTrackButton(self, (19, 22))
        self.save_btn = PSButtons.SaveTrackButton(self, (100, 4))
        self.delete_btn = PSButtons.DeleteTrackButton(self, (118, 5))

        # marqueur de progression de lecture
        self.progression_bar = PSControls.TrackProgressionBar(self, (38, 25))
        self._progression_time = 0.

        # binding events
        if PSConfig.PLATFORM == 'linux2':
            self.Bind(wx.EVT_PAINT, self.OnPaintLinux)
        elif PSConfig.PLATFORM == 'darwin':
            self.Bind(wx.EVT_PAINT, self.OnPaintMac)

        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseIn)
        self.play_btn.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseIn)
        self.stop_btn.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseIn)
        self.save_btn.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseIn)
        self.delete_btn.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseIn)
        self.progression_bar.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseIn)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseOut)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseScroll)
        self.Bind(PSButtons.EVT_BTN_PLAY, self._playTrack)
        self.Bind(PSButtons.EVT_BTN_STOP, self._stopTrack)
        self.Bind(PSButtons.EVT_BTN_CLICKED, self._saveTrack, self.save_btn)
        self.Bind(PSButtons.EVT_BTN_CLICKED, self._deleteTrack, self.delete_btn)

    def OnPaintLinux(self, evt):
        if self._hover or self._selected:
            colour = self._select_clr
        else:
            colour = self._norm_clr

        self.play_btn.SetBackgroundColour(colour)
        self.stop_btn.SetBackgroundColour(colour)
        self.save_btn.SetBackgroundColour(colour)
        self.delete_btn.SetBackgroundColour(colour)
        self.progression_bar.SetBackgroundColour(colour)

        self.OnPaintGeneric(colour)

    def OnPaintMac(self, evt):
        if self._hover or self._selected:
            colour = self._select_clr
        else:
            colour = self._norm_clr

        self.OnPaintGeneric(colour)

    def OnPaintGeneric(self, colour):
        w, h = self.GetSize()
        dc = wx.PaintDC(self)

        dc.SetBrush(wx.Brush(colour))
        dc.SetPen(wx.Pen(colour, 1))
        dc.DrawRectangle(0, 0, w, h)

        dc.SetFont(self._norm_font)
        dc.SetTextForeground("#FFFFFF")
        dc.DrawText(self._text + " - " + self._durationText, 5, 6-PSConfig.Y_OFFSET)

        if self._old:
            dc.SetFont(self._small_font)
            dc.DrawText(self._date_txt,5, 38-PSConfig.Y_OFFSET)

    def OnMouseDown(self, evt):
        self._selected = True
        self.GetParent()._setSelection(self)

    def OnMouseIn(self, evt):
        evt.Skip()
        self._hover = True
        self.Refresh()

    def OnMouseOut(self, evt):
        evt.Skip()
        self._hover = False
        self.Refresh()

    def OnMouseScroll(self, evt):
        self.GetParent()._setScrollPosition(evt.GetWheelRotation())

    def _getDurationText(self):
        dur = sndinfo(self._path)[1]
        min = dur / 60
        sec = dur % 60
        if min >= 10:
            min = "%d" % min
        else:
            min = "0%d" % min
        if sec >= 10:
            sec = "%d" % sec
        else:
            sec = "0%d" % sec
        return min + ":" + sec

    def _getDateText(self):
        filename = self._path.rsplit('/', 1)[1].split('.')[0]
        d,t = filename.split('_')
        t = t.replace('-',':')
        return "Rec on: %s - %s" % (d,t)

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
            if self._sndtable is None:
                self._prog_bar_timer = wx.Timer(self)
                self.Bind(wx.EVT_TIMER, self._incrementPlayingTime)
                self._sndtable = SndTable(self._path)
                self._osc = Osc(self._sndtable, self._sndtable.getRate())
                self._duration = self._sndtable.getDur()
                self.progression_bar.setMax(self._duration)
                self._osc.setPhase(self._progression_time / self._duration)
            self._osc.out()
            self._prog_bar_timer.Start(100)
        else:
            self._pauseTrack()

    def _pauseTrack(self):
        if self._sndtable is not None:
            self._osc.stop()
            self._prog_bar_timer.Stop()

    def _stopTrack(self, evt):
        if self._sndtable is not None:
            self._osc.stop()
            self._osc.reset()
            self._prog_bar_timer.Stop()
            self._progression_time = 0
            self.progression_bar.setValue(0)
            self.play_btn.SetState(False)

    def _saveTrack(self, evt):
        # Custom event business
        event = RecordedTrackEvent(myEVT_SAVE_TRACK, self.GetId())
        event.SetTrackPath(self._path)
        event.SetDefaultDir(PSConfig.HOME_PATH)
        event.SetDefaultFile(".wav")
        event.SetStyle(wx.SAVE)
        event.SetMessage("Save Track")
        event.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(event)

    def _deleteTrack(self, evt):
        PSUtils.printMessage("Trashed file: %s" % self._path, 1)
        send2trash(self._path)
        self._removeTrack()

    def _removeTrack(self):
        self.deletePlaybackObjects()
        self.GetParent()._deleteTrack(self)

    def deletePlaybackObjects(self):
        if self._sndtable is not None:
            self.Unbind(wx.EVT_TIMER)
            self._prog_bar_timer.Destroy()
            self._osc.stop()
            self._sndtable = None
            self._osc = None
            del self._duration


class RecordedTracksList(wx.PyScrolledWindow):
    def __init__(self, parent, size, pos):
        wx.ScrolledWindow.__init__(self, parent, size=size, pos=pos)
        self.SetBackgroundColour("#323232")
        self.SetVirtualSize((self.GetSize()[0] - 15, 1000))
        self.scrollRate = 10
        self.SetScrollRate(1, self.scrollRate)

        # list containing all RecordedTrackElement instances
        self._tracks_list = []

        self._selected = None

        self.x_margin = 8
        self.y_margin = 10
        self._setVerticalScroll()

        # Binding events
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        self.PrepareDC(dc)
        self._drawFakeScrollbar(dc)

    def _drawFakeScrollbar(self, dc):
        dc.SetBrush(wx.Brush(wx.Colour(250, 250, 250)))
        dc.SetPen(wx.Pen(wx.Colour(250, 250, 250), 1))
        w, h = self.GetSize()
        if PSConfig.PLATFORM == 'linux2':
            scroll_w = 13
        elif PSConfig.PLATFORM == 'darwin':
            scroll_w = 15
        dc.DrawRectangle(w - scroll_w, 0, scroll_w, h)

    def _setVerticalScroll(self):
        self.SetVirtualSize((self.GetSize()[0] - 15, (self._getTotalListHeight() + self.y_margin)))

    def _setScrollPosition(self, delta):
        curr_scroll = abs(self.CalcScrolledPosition(0, 0)[1]) / self.scrollRate
        new_scroll = curr_scroll - delta
        self.Scroll(0, new_scroll)

    def _getTotalListHeight(self):
        h = 0
        for i, elem in enumerate(self._tracks_list):
            if elem._old:
                h += RecordedTrackElement.size_old[1]
            else:
                h += RecordedTrackElement.size[1]
            h += self.y_margin
        return h

    def _setSelection(self, elem):
        if self._selected is not None and self._selected != elem:
            self._selected._pauseTrack()
            self._selected.play_btn.SetState(False)
            self._selected._setSelection(False)
            self._selected.Refresh()
        self._selected = elem

    def _deleteTrack(self, track):
        if self._selected == track:
            self._selected = None
        track.Show(False)
        self._tracks_list.remove(track)
        wx.CallAfter(track.Destroy)
        self._repositionTrackElements()
        if len(self._tracks_list) == 0:
            self.GetGrandParent().noMoreTracks()

    def _repositionTrackElements(self):
        box_height = 0
        y = 0
        for i, elem in enumerate(self._tracks_list):
            if i > 0:
                if self._tracks_list[i-1]._old:
                    box_height = RecordedTrackElement.size_old[1]
                else:
                    box_height = RecordedTrackElement.size[1]
            y += (box_height + self.y_margin)
            elem.SetPosition(self.CalcScrolledPosition((self.x_margin, y)))
        self._setVerticalScroll()

    def addTrack(self, path, id, old=False):
        y = self._getTotalListHeight() + self.y_margin
        self._tracks_list.append(RecordedTrackElement(self, self.CalcScrolledPosition((self.x_margin, y)), path, id, old))
        self._setVerticalScroll()
        wx.CallAfter(self.Refresh)

    def deletePlaybackObjects(self):
        for track in self._tracks_list:
            track.deletePlaybackObjects()


class RecordedTracksWindow(wx.Frame):
    def __init__(self, parent, server, namespace):
        self.server = server
        self.script_namespace = namespace
        wx.Frame.__init__(self, parent, id=-1, size=(200, 216), style=wx.NO_BORDER | wx.FRAME_FLOAT_ON_PARENT)
        self.panel = wx.Panel(self, size=self.GetSize() + (1, 1))
        self.file_path = ""
        self.tracks_list = RecordedTracksList(self.panel, self.panel.GetSize() - (4, 26), (1, 23))
        self.__track_count__ = 0

        # position par rapport au frame principal
        self.pos_offset = wx.Point(295, 94+PSConfig.BANNER_OFFSET)

        # s'occupe de l'enregistrement
        self._trackRecorder = PSAudio.TrackRecorder()

        # Fade in/out properties
        self.IS_SHOWN = False
        if PSConfig.USE_TRANSPARENCY:
            self.SetTransparent(0)
            self._alpha = 255
            self._currentAlpha = 0
            self._delta = 22
            self._fadeTime = 27
            self._timer = wx.Timer(self, -1)
            self.Bind(wx.EVT_TIMER, self.changeAlpha)

        # bitmap
        self.background = imgs.recorded_tracks_bg.GetBitmap()

        # Binding events
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)

        self._checkRecFolderOnInit()

    def _checkRecFolderOnInit(self):
        PSUtils.printMessage("Scanning rec folder for files...", 1)
        if os.path.exists(PSConfig.REC_PATH):
            for root, dirs, files in os.walk(PSConfig.REC_PATH):
                for file in files:
                    if 'DS_Store' in file:
                        pass
                    else:
                        self.__track_count__ += 1
                        path = os.path.join(root, file)
                        PSUtils.printMessage("Found: %s" % path, 1)
                        self.tracks_list.addTrack(path, self.__track_count__, True)

    def OnPaint(self, evt):
        dc = wx.PaintDC(self.panel)
        dc.DrawBitmap(self.background, 0, 0)

    def ShowWindow(self, pos):
        if not self.IS_SHOWN:
            self.IS_SHOWN = True
            self.SetPosition(pos + self.pos_offset)
            self.Show(True)
            if PSConfig.USE_TRANSPARENCY:
                self._timer.Start(self._fadeTime)

    def HideWindow(self):
        self.IS_SHOWN = False
        if PSConfig.USE_TRANSPARENCY:
            self._timer.Start(self._fadeTime)
        else:
            self.Show(False)
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
        self.SetPosition(pos + self.pos_offset)

    def startRecording(self):
        if 'mix' not in self.script_namespace:
            # Cannot record because the script does not have a 'mix' object.
            return 0
        else:
            self.__track_count__ += 1
            self.file_path = self._trackRecorder.record(self.script_namespace['mix'], self.server.getNchnls())
            return self.__track_count__

    def stopRecording(self):
        self._trackRecorder.stop()
        self.tracks_list.addTrack(self.file_path, self.__track_count__)

    def noMoreTracks(self):
        self.GetParent().noMoreTracks()

##Custom events for the ServerSetupPanel
myEVT_INTERFACE_CHANGED = wx.NewEventType()
EVT_INTERFACE_CHANGED = wx.PyEventBinder(myEVT_INTERFACE_CHANGED, 1)

myEVT_SAMP_RATE_CHANGED = wx.NewEventType()
EVT_SAMP_RATE_CHANGED = wx.PyEventBinder(myEVT_SAMP_RATE_CHANGED, 1)

myEVT_BUFSIZE_CHANGED = wx.NewEventType()
EVT_BUFSIZE_CHANGED = wx.PyEventBinder(myEVT_BUFSIZE_CHANGED, 1)

myEVT_NCHNLS_CHANGED = wx.NewEventType()
EVT_NCHNLS_CHANGED = wx.PyEventBinder(myEVT_NCHNLS_CHANGED, 1)

myEVT_VIRTUAL_KEYS_CHANGED = wx.NewEventType()
EVT_VIRTUAL_KEYS_CHANGED = wx.PyEventBinder(myEVT_VIRTUAL_KEYS_CHANGED, 1)


class ServerSetupEvent(wx.PyCommandEvent):
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)


class ServerNotBootedError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, args, kwargs)


class ServerSetupPanel(wx.Panel):
    def __init__(self, parent, server):
        wx.Panel.__init__(self, parent, -1, (640, 61), (500, 260))
        self.SetBackgroundColour("#000000")
        self.Show(False)

        self._server = server

        # this flag is set to true when the server reinitializes itself
        # and that audio objects need to be reinstanciated
        # This has to be set to false after being handled by the program
        self.SERVER_CHANGED_FLAG = False
        # will change if the 'computer keyboard' option is selected
        self.USING_VIRTUAL_KEYS = False

        self.hasPreferences = False
        self.preferences = None
        self.getPreferences()

        # Fade in/out properties
        self.IS_SHOWN = False
        if PSConfig.USE_TRANSPARENCY:
            self.SetTransparent(0)
            self._alpha = 220
            self._currentAlpha = 0
            self._delta = 50
            self._fadeTime = 55
            self._timer = wx.Timer(self, -1)
            self.Bind(wx.EVT_TIMER, self.changeAlpha)

        # Setup lists
        self.samplingRates = ['22050 Hz', '32000 Hz', '44100 Hz', '48000 Hz', '88200 Hz', '96000 Hz']
        self.bufferSizes = ['32', '64', '128', '256', '512', '1024', '2048', '4096']
        self.audioDrivers = ['portaudio', 'jack', 'coreaudio', 'offline', 'offline_nb']
        self.numberChnls = ['1', '2', '3', '4']

        # Positions
        self.leftMargin = 8
        self.topMargin = 8
        self.interfaceCtrlPos = (self.leftMargin, 40)
        self.midiCtrlPos = (270, 40)
        self.lineSepPos = (20, 157)
        self.sampratePos = (self.leftMargin, 175)
        self.bufsizePos = (self.leftMargin, 205)
        self.audioDriverPos = (self.leftMargin, 235)
        self.duplexPos = (2 * self.GetSize()[0] / 3 - 20, 175)
        self.numChnlsPos = (2 * self.GetSize()[0] / 3 - 20, 205)

        # Controls
        x, y = self.interfaceCtrlPos
        self.inputChoice = wx.Choice(self, -1, (x + 6, y + 36), PSConfig.CHOICE_SIZE, choices=self.listDevices("input"))
        self.outputChoice = wx.Choice(self, -1, (x + 6, y + 80), PSConfig.CHOICE_SIZE, choices=self.listDevices("output"))

        x, y = self.midiCtrlPos
        self.midiInputChoice = wx.Choice(self, -1, (x + 6, y + 36), PSConfig.CHOICE_SIZE, choices=self.listMidiDevices("input"))
        self.midiOutputChoice = wx.Choice(self, -1, (x + 6, y + 80), PSConfig.CHOICE_SIZE, choices=self.listMidiDevices("output"))

        x, y = self.sampratePos
        self.samprateChoice = wx.Choice(self, -1, (x + 100, y - 6), PSConfig.CHOICE_SIZE, choices=self.samplingRates)

        x, y = self.bufsizePos
        self.bufsizeChoice = wx.Choice(self, -1, (x + 80, y - 6), PSConfig.CHOICE_SIZE, choices=self.bufferSizes)

        x, y = self.audioDriverPos
        self.audioDriverChoice = wx.Choice(self, -1, (x + 90, y - 6), PSConfig.CHOICE_SIZE, choices=self.audioDrivers)

        x, y = self.duplexPos
        self.duplexChoice = wx.Choice(self, -1, (x + 60, y - 6), PSConfig.CHOICE_SIZE, choices=['out', 'in/out'])

        x, y = self.numChnlsPos
        self.numChnlsChoice = wx.Choice(self, -1, (x + 80, y - 6), PSConfig.CHOICE_SIZE, choices=self.numberChnls)

        # Binding events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_CHOICE, self.changeInput, self.inputChoice)
        self.Bind(wx.EVT_CHOICE, self.changeOutput, self.outputChoice)
        self.Bind(wx.EVT_CHOICE, self.changeMidiInput, self.midiInputChoice)
        self.Bind(wx.EVT_CHOICE, self.changeMidiOutput, self.midiOutputChoice)
        self.Bind(wx.EVT_CHOICE, self.changeSampRate, self.samprateChoice)
        self.Bind(wx.EVT_CHOICE, self.changeBufSize, self.bufsizeChoice)
        self.Bind(wx.EVT_CHOICE, self.changeAudioDriver, self.audioDriverChoice)
        self.Bind(wx.EVT_CHOICE, self.changeDuplex, self.duplexChoice)
        self.Bind(wx.EVT_CHOICE, self.changeNumChnls, self.numChnlsChoice)

        #self.markDirty() # make sure the server is initialized with preferences when running a script for the first time

    def OnPaint(self, evt):
        w, h = self.GetSize()
        dc = wx.PaintDC(self)
        penWidth = 1
        dc.SetPen(wx.Pen("#444444", penWidth, wx.SOLID))

        # contour
        dc.DrawLine(0, 0, w - penWidth, 0)
        dc.DrawLine(0, 0, 0, h - penWidth)
        dc.DrawLine(0, h - penWidth, w - penWidth, h - penWidth)
        dc.DrawLine(w - penWidth, h - penWidth, w - penWidth, 0)

        # fonts
        titleFont = wx.Font(**PSConfig.FONTS['light']['title1'])
        regFont = wx.Font(**PSConfig.FONTS['light']['norm'])
        smallFont = wx.Font(**PSConfig.FONTS['light']['xsmall'])

        # Titre
        dc.SetTextForeground("#FFFFFF")
        dc.SetFont(titleFont)
        dc.DrawText("Server Setup", self.leftMargin, self.topMargin)

        dc.SetFont(regFont)
        x, y = self.interfaceCtrlPos
        dc.DrawText("Interface", x, y)

        dc.SetFont(smallFont)
        dc.DrawText("input", x + 6, y + 20)
        dc.DrawText("output", x + 6, y + 65)

        x, y = self.midiCtrlPos
        dc.DrawText("Midi input", x + 6, y + 20)
        dc.DrawText("Midi output", x + 6, y + 65)

        x, y = self.lineSepPos
        dc.DrawLine(x, y, w - x, y)

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
        if PSConfig.USE_TRANSPARENCY:
            self._timer.Start(self._fadeTime)

    def HideWindow(self):
        self.IS_SHOWN = False
        if PSConfig.USE_TRANSPARENCY:
            self._timer.Start(self._fadeTime)
        else:
            self.Show(False)
        self.savePreferences()

    def IsShown(self):
        return self.IS_SHOWN

    def changeAlpha(self, evt):
        if self.IS_SHOWN:
            if self._currentAlpha < self._alpha:
                self._currentAlpha += self._delta
                if self._currentAlpha > self._alpha: self._currentAlpha = self._alpha
                wx.CallAfter(self.SetTransparent, self._currentAlpha)
            else:
                self._timer.Stop()
        else:
            if self._currentAlpha > 0:
                self._currentAlpha -= self._delta
                if self._currentAlpha < 0: self._currentAlpha = 0
                wx.CallAfter(self.SetTransparent, self._currentAlpha)
            else:
                wx.CallAfter(self.Show, False)
                self._timer.Stop()

    def changeInput(self, evt):
        # set the flag to true so the main program
        # can respond accordingly and call initServer()
        self.SERVER_CHANGED_FLAG = True
        try:
            self.preferences['input'] = int(evt.GetString().split(':')[0][:-1])
        except ValueError:
            # consider the case when duplex mode is set so 0 and the Choice ctrl
            # displays only text, the int conversion will fail
            pass
        else:
            pass

    def changeOutput(self, evt):
        # set the flag to true so the main program
        # can respond accordingly and call initServer()
        self.SERVER_CHANGED_FLAG = True
        self.preferences['output'] = int(evt.GetString().split(':')[0][:-1])

        # Custom event business
        # Forces the update of the text control showing the name of the interface in use
        event = ServerSetupEvent(myEVT_INTERFACE_CHANGED, self.GetId())
        self.GetEventHandler().ProcessEvent(event)

    def changeMidiInput(self, evt):
        try:
            old_in = self.preferences['midi_input']
            self.preferences['midi_input'] = int(evt.GetString().split(':')[0][:-1])
        except ValueError:
            # this considers cases where duplex mode is set to 0 (and only text is selected)
            # or when the user selects the 'computer keyboard'
            if evt.GetString() == "Computer Keyboard":
                self.USING_VIRTUAL_KEYS = True
                # Forces update of the virtual keys parameters in the __main__
                event = ServerSetupEvent(myEVT_VIRTUAL_KEYS_CHANGED, self.GetId())
                self.GetEventHandler().ProcessEvent(event)
        else:
            if self.USING_VIRTUAL_KEYS:
                self.USING_VIRTUAL_KEYS = False
                # Forces update of the virtual keys parameters in the __main__
                event = ServerSetupEvent(myEVT_VIRTUAL_KEYS_CHANGED, self.GetId())
                self.GetEventHandler().ProcessEvent(event)

                self.SERVER_CHANGED_FLAG = True
            elif old_in != self.preferences['midi_input']:
                self.SERVER_CHANGED_FLAG = True

    def changeMidiOutput(self, evt):
        try:
            self.preferences['midi_output'] = int(evt.GetString().split(':')[0][:-1])
        except ValueError:
            # consider the case when duplex mode is set so 0 and the Choice ctrl
            # displays only text, the int conversion will fail
            pass
        else:
            # set the flag to true so the main program
            # can respond accordingly and call initServer()
            self.SERVER_CHANGED_FLAG = True

    def changeSampRate(self, evt):
        # set the flag to true so the main program
        # can respond accordingly and call initServer()
        self.SERVER_CHANGED_FLAG = True
        self.preferences['sr'] = int(evt.GetString()[0:-3])

        # Custom event business
        event = ServerSetupEvent(myEVT_SAMP_RATE_CHANGED, self.GetId())
        self.GetEventHandler().ProcessEvent(event)

    def changeBufSize(self, evt):
        # set the flag to true so the main program
        # can respond accordingly and call initServer()
        self.SERVER_CHANGED_FLAG = True
        self.preferences['bfs'] = int(evt.GetString())

        # Custom event business
        event = ServerSetupEvent(myEVT_BUFSIZE_CHANGED, self.GetId())
        self.GetEventHandler().ProcessEvent(event)

    def changeAudioDriver(self, evt):
        # set the flag to true so the main program
        # can respond accordingly and call initServer()
        self.SERVER_CHANGED_FLAG = True
        self.preferences['audio'] = evt.GetString()

    def changeDuplex(self, evt):
        # set the flag to true so the main program
        # can respond accordingly and call initServer()
        self.SERVER_CHANGED_FLAG = True
        self.preferences['duplex'] = evt.GetSelection()

        self.updateCtrls()

    def changeNumChnls(self, evt):
        # set the flag to true so the main program
        # can respond accordingly and call initServer()
        self.SERVER_CHANGED_FLAG = True
        self.preferences['nchnls'] = int(evt.GetString())

        # Custom event business
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
        Done once upon startup. If preferences values aren't valid anymore, the default settings are restored.
        """
        self.hasPreferences, self.preferences = PSUtils.getServerPreferences()
        if self.preferences['midi_input'] == -1:
            self.USING_VIRTUAL_KEYS = True
            event = ServerSetupEvent(myEVT_VIRTUAL_KEYS_CHANGED, self.GetId())
            wx.CallLater(200, self.GetEventHandler().ProcessEvent, event)

    def savePreferences(self):
        try:
            f = open(os.path.join(PSConfig.PREF_PATH, "server_setup.pref"), 'w')
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

    def markDirty(self):
        self.SERVER_CHANGED_FLAG = True

    def isUsingVirtualKeys(self):
        return self.USING_VIRTUAL_KEYS

    def initServer(self):
        """
        Initializes the server with the new preferences.
        """
        if self._server.getIsBooted():
            self._server.shutdown()
            time.sleep(.5)
        self._server.reinit(self.preferences['sr'],
                            self.preferences['nchnls'],
                            self.preferences['bfs'],
                            self.preferences['duplex'],
                            self.preferences['audio'],
                            jackname="Pyo Synth")
        self._server.setOutputDevice(self.preferences['output'])
        self._server.setMidiOutputDevice(self.preferences['midi_output'])
        if self.preferences['duplex']:
            self._server.setInputDevice(self.preferences['input'])
            self._server.setMidiInputDevice(self.preferences['midi_input'])
        self._server.boot()
        if self._waitForServerToBoot():
            raise ServerNotBootedError, "Timeout expired: Server wasn't able to boot."

    def initServerForExport(self):
        self.SERVER_CHANGED_FLAG = True
        self._server.stop()
        time.sleep(.2)
        self._server.shutdown()
        time.sleep(.5)

        self._server.reinit(self.preferences['sr'],
                            self.preferences['nchnls'],
                            self.preferences['bfs'],
                            self.preferences['duplex'],
                            audio="offline",
                            jackname="Pyo Synth")
        self._server.boot()
        if self._waitForServerToBoot():
            raise ServerNotBootedError, "Timeout expired: Server wasn't able to boot."

    def _waitForServerToBoot(self):
        timeout = 10
        time_count = 0
        time_delay = .1
        while time_count < timeout:
            if self._server.getIsBooted():
                return 0
            time.sleep(time_delay)
            time_count += time_delay
        return 1

    def startServer(self):
        self._server.start()

    def stopServer(self):
        self._server.stop()
        time.sleep(.2)

    def recordOptions(self, dur, name, fileformat, bitdepth):
        self._server.recordOptions(dur, name, fileformat, bitdepth)

    def listDevices(self, type):
        """
        Builds a list of available devices for the i/o interface choice.
        """
        devices = None
        maxChar = 27
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

    def listMidiDevices(self, type):
        """
        Builds a list of available midi devices for the i/o interface choice.
        """
        devices = None
        maxChar = 20
        list = []
        if type == "input":
            devices = pm_get_input_devices()
        elif type == "output":
            devices = pm_get_output_devices()
        for i in range(len(devices[0])):
            text = str(devices[1][i]) + " : "
            text += devices[0][i][0:maxChar]
            list.append(text)
        if type == "input":
            if len(list) > 1: list.append("99 : All Devices")
            list.append("Computer Keyboard")
        return list

    def updateCtrls(self):
        """
        Updates the values of the wx.Controls for the GUI.
        """
        self.duplexChoice.SetSelection(self.preferences['duplex'])

        if self.preferences['duplex']:
            # get the inputs
            list = self.listDevices("input")
            self.inputChoice.SetItems(list)
            list.extend(self.listDevices("output"))
            # set the size according to largest choice
            tw = self.getLongestText(list)
            self.inputChoice.SetSize((tw + 48 + PSConfig.CHOICE_X_DELTA, -1))
            self.outputChoice.SetSize((tw + 48 + PSConfig.CHOICE_X_DELTA, -1))
            names, indexes = pa_get_input_devices()
            self.inputChoice.SetSelection(indexes.index(self.preferences['input']))

            names, indexes = pa_get_output_devices()
            self.outputChoice.SetSelection(indexes.index(self.preferences['output']))

            # do the same for midi
            list = self.listMidiDevices("input")
            # handle the case where there is no midi devices connected
            # len(list) == 1 means only Computer keyboard is available
            if len(list) == 1:
                self.midiInputChoice.SetItems(list)
                self.midiOutputChoice.SetItems(["No midi devices"])
                self.midiInputChoice.SetSelection(0)
                self.midiOutputChoice.SetSelection(0)
                tw = self.getLongestText(list)
                self.midiInputChoice.SetSize((tw + 48 + PSConfig.CHOICE_X_DELTA, -1))
                self.midiOutputChoice.SetSize((tw + 48 + PSConfig.CHOICE_X_DELTA, -1))
            else:
                self.midiInputChoice.SetItems(list)
                list.extend(self.listMidiDevices("output"))
                tw = self.getLongestText(list)
                self.midiInputChoice.SetSize((tw + 48 + PSConfig.CHOICE_X_DELTA, -1))
                self.midiOutputChoice.SetSize((tw + 48 + PSConfig.CHOICE_X_DELTA, -1))

                if self.USING_VIRTUAL_KEYS:
                    self.midiInputChoice.SetSelection(self.midiInputChoice.GetCount()-1)
                else:
                    names, indexes = pm_get_input_devices()
                    indexes.append(99)
                    self.midiInputChoice.SetSelection(indexes.index(self.preferences['midi_input']))

                names, indexes = pm_get_output_devices()
                self.midiOutputChoice.SetSelection(indexes.index(self.preferences['midi_output']))
        else:
            self.inputChoice.SetItems(["Duplex mode is set to out."])
            self.midiInputChoice.SetItems(["Duplex mode is set to out."])
            self.inputChoice.SetSelection(0)
            self.midiInputChoice.SetSelection(0)
            tw, th = wx.WindowDC(self).GetTextExtent("Duplex mode is set to out.")
            self.inputChoice.SetSize((tw + 40, -1))
            self.midiInputChoice.SetSize((tw + 40, -1))

            names, indexes = pa_get_output_devices()
            self.outputChoice.SetSelection(indexes.index(self.preferences['output']))

            list = self.listMidiDevices("output")
            # handle the case where there is no midi devices connected
            if len(list) == 0:
                self.midiOutputChoice.SetItems(["No midi devices"])
                self.midiOutputChoice.SetSelection(0)
                tw = self.getLongestText(["No midi devices"])
                self.midiOutputChoice.SetSize((tw + 48, -1))
            else:
                names, indexes = pm_get_output_devices()
                self.midiOutputChoice.SetSelection(indexes.index(self.preferences['midi_output']))

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
    """
    Affiche une liste de tous les objets audio controlable present dans le script en cours d'execution.
    Accede au dictionnaire PARAMS_TREE_DICT pour determiner l'admissibilite d'un objet particulier.

    parametres:
                parent : fenetre parent, wx.Window
                namespace : reference au namespace le plus global (ou s'execute les scripts audio)
                            utilise pour realiser le lien entre les objets audio et le controleur
    """
    def __init__(self, parent, namespace):
        wx.Frame.__init__(self, parent, id=-1, size=(200, 216), style=wx.NO_BORDER | wx.FRAME_FLOAT_ON_PARENT)
        self.panel = wx.Panel(self, size=self.GetSize() + (1, 1))
        self.treeCtrl = wx.TreeCtrl(self.panel, size=self.panel.GetSize() - (4, 26), pos=(1, 23),
                                    style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT)
        self.treeCtrl.SetBackgroundColour(PSConfig.BG_COLOUR)
        self.treeCtrl.SetForegroundColour("#DDDDDD")

        self.script_namespace = namespace

        # Creation de l'arbre et du dictionnaire contenant
        # les references aux parametres des objets pyo
        self.param_dict = {}
        # id count sert a creer des liens entre les parametres
        # et leur references dans le param_dict
        self.__id__ = -1
        self.root = self.treeCtrl.AddRoot("Pyo Objects")
        self.treeCtrl.SetPyData(self.root, None)
        # le premier item de la liste est 'None', pour permettre d'enlever un parametre
        item = self.treeCtrl.AppendItem(self.root, 'None')
        self.treeCtrl.SetPyData(item, None)
        # stock l'id de la selection courrante
        self.selection = None

        # Fade in/out properties
        self.IS_SHOWN = False
        if PSConfig.USE_TRANSPARENCY:
            self.SetTransparent(0)
            self._alpha = 240
            self._currentAlpha = 0
            self._delta = 22
            self._fadeTime = 27
            self._timer = wx.Timer(self, -1)
            self.Bind(wx.EVT_TIMER, self.changeAlpha)

        # conserve une reference de l'objet ParamBox pour qui la fenetre s'est ouverte
        self._obj = None
        # conserve un dictionnaire des liens {param : obj}
        # ou 'obj' est une reference a l'objet ParamBox
        # et 'param' est un string representant le parametre de l'objet pyo associe
        self._links = {}

        # bitmap
        self.background = imgs.patch_window_bg.GetBitmap()

        # Binding events
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)
        self.treeCtrl.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelection, self.treeCtrl)

    def OnPaint(self, evt):
        dc = wx.PaintDC(self.panel)
        dc.DrawBitmap(self.background, 0, 0)

    def addObject(self, name):
        obj = self.script_namespace[name]
        try:
            # retourne une liste des parametres utilisables en format string
            param_list = PARAMS_TREE_DICT[obj.__class__.__name__]
        except:
            # quitte la fonction si l'element ne fait pas parti des objets audio controlable
            return
        item = self.treeCtrl.AppendItem(self.root, name + ' - ' + obj.__class__.__name__)
        self.treeCtrl.SetPyData(item, obj)

        for param in param_list:
            p = self.treeCtrl.AppendItem(item, param)

            # ici, on stock l'id de l'item pour pouvoir le recupere
            # plus tard et s'en servir comme cle dans le param_dict
            id = self.__getNewId__()
            self.treeCtrl.SetPyData(p, id)
            self.param_dict[id] = name + "." + param

    def clearObjects(self):
        # suppression de tous les elements
        self.treeCtrl.DeleteChildren(self.root)
        self.param_dict.clear()
        # ajout de l'entree None pour permettre de desactiver un ParamBox
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
        # verifie si la fenetre depasse du frame parent
        parent = self._obj.GetParent()
        end_of_frame = parent.GetSize()[0] + parent.GetScreenPosition()[0]
        pos = self._obj.GetScreenPosition() + (self._obj.GetSize()[0], 2)
        if (pos[0] + self.GetSize()[0]) > end_of_frame:
            pos = self._obj.GetScreenPosition() - (self.GetSize()[0], -2)

        self.SetPosition(pos)

    def ShowWindow(self, obj):
        self._obj = obj
        self._setPosition()

        # evite d'avoir l'erreur : cannot collapse hidden root
        # mais fonctionne quand meme
        try:
            self.treeCtrl.CollapseAllChildren(self.root)
        except:
            pass

        if not self.IS_SHOWN:
            self.IS_SHOWN = True
            self.Show(True)
            if PSConfig.USE_TRANSPARENCY:
                self._timer.Start(self._fadeTime)

    def HideWindow(self):
        self.selection = None
        self._obj = None
        self.IS_SHOWN = False
        if PSConfig.USE_TRANSPARENCY:
            self._timer.Start(self._fadeTime)
        else:
            self.Show(False)

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
        # si le parametre est deja associe a un ParamBox,
        # son ancien controle est dissocie
        if param in self._links:
            self._links[param].unlink(self.script_namespace)
        self._links[param] = obj
        obj.unlink(self.script_namespace)
        exec param + "= obj.getMidiControl()" in self.script_namespace, locals()
        obj.pyo_obj.setParamName(param)
        obj.enable(param)

    def getLinks(self):
        return self._links

    def __getNewId__(self):
        self.__id__ += 1
        return self.__id__


class WarningWindow(wx.Frame):
    min_size = wx.Size(200, 40)
    def __init__(self, parent, pos, text):
        wx.Frame.__init__(self, parent, -1, pos=pos, size=WarningWindow.min_size, style=wx.NO_BORDER | wx.FRAME_FLOAT_ON_PARENT)
        self.panel = wx.Panel(self, size=WarningWindow.min_size + (1, 1))
        self.panel.SetBackgroundColour("#888888")

        self._normal_font = wx.Font(**PSConfig.FONTS['light']['med'])
        self._small_font = wx.Font(**PSConfig.FONTS['light']['norm'])
        self._top_line = text
        self._bottom_line = None
        self._y_margin = 12
        self._x_margin = 15
        self._setSize() # size is set according to text width

        self.IS_SHOWN = False
        # Fade in/out properties
        if PSConfig.USE_TRANSPARENCY:
            self.SetTransparent(0)
            self._alpha = 220
            self._currentAlpha = 0
            self._delta = 22
            self._fadeTime = 27
            self._timer = wx.Timer(self, -1)
            self.Bind(wx.EVT_TIMER, self._changeAlpha)

        # Binding events
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, evt):
        w, h = self.GetSize()
        dc = wx.PaintDC(self.panel) # test this on mac: self vs. self.panel

        dc.SetTextForeground("#FFFFFF")
        dc.SetFont(self._normal_font)

        txt_w, txt_h = dc.GetTextExtent(self._top_line)
        dc.DrawText(self._top_line, (w / 2 - txt_w / 2), self._y_margin + 2 - PSConfig.Y_OFFSET)
        if self._bottom_line is not None:
            txt_w, txt_h = dc.GetTextExtent(self._bottom_line)
            dc.SetFont(self._small_font)
            dc.DrawText(self._bottom_line, (w / 2 - txt_w / 2 + 2), self.GetSize()[1] - self._y_margin - txt_h/2)

    def SetText(self, string):
        self._top_line = string
        self._setSize()
        self.Refresh()

    def SetBottomText(self, string):
        self._bottom_line = string
        self._setSize()
        self.Refresh()

    def SetProgressBar(self):
        self._gauge = wx.Gauge(self, -1, 100, (self._x_margin, self.GetSize()[1]/2-5),
                               (self.GetSize()[0] - 2*self._x_margin, -1 + PSConfig.GAUGE_Y_DELTA))
        self._setSize()

    def SetProgressRange(self, value):
        assert hasattr(self, "_gauge"), "You need to create the progress bar before setting its value."
        self._gauge.SetRange(value)

    def SetProgressValue(self, value):
        assert hasattr(self, "_gauge"), "You need to create the progress bar before setting its value."
        self._gauge.SetValue(value)

    def PulseProgressBar(self):
        assert hasattr(self, "_gauge"), "You need to create the progress bar before setting its value."
        self._gauge.Pulse()

    def ShowWindow(self, fade=True):
        self.IS_SHOWN = True
        self.Show(True)
        if PSConfig.USE_TRANSPARENCY:
            if fade:
                self._timer.Start(self._fadeTime)
            else:
                self.SetTransparent(255)
                self._currentAlpha = 255

    def destroy(self):
        self.IS_SHOWN = False
        if PSConfig.USE_TRANSPARENCY:
            self._timer.Start(self._fadeTime)
        else:
            self.Show(False)
            self.Destroy()

    def _changeAlpha(self, evt):
        if self.IS_SHOWN:
            if self._currentAlpha < self._alpha:
                self._currentAlpha += self._delta
                if self._currentAlpha > 255:
                    self._currentAlpha = 255
                wx.CallAfter(self.SetTransparent, self._currentAlpha)
            else:
                self._timer.Stop()
        else:
            if self._currentAlpha > 0:
                self._currentAlpha -= self._delta
                if self._currentAlpha < 0:
                    self._currentAlpha = 0
                wx.CallAfter(self.SetTransparent, self._currentAlpha)
            else:
                self.Show(False)
                self._timer.Stop()
                # Quand le fadeout est fini, la fenetre est detruite
                self.Destroy()

    def _setSize(self):
        w = self._getWidth()
        h = self._getHeight()
        wx.Frame.SetSize(self, (w,h))
        self.panel.SetSize((w+1,h+1))
        if hasattr(self, "_gauge"):
            gauge_w = w - 2*self._x_margin
            self._gauge.SetSize((gauge_w, -1))
            self._gauge.SetPosition(((w - gauge_w) / 2, h/2-5 + PSConfig.GAUGE_Y_DELTA))

    def _getWidth(self):
        """
        Returns the biggest value between _top_line width, _bottom_line width and min_size width.
        """
        dc = wx.ClientDC(self)
        dc.SetFont(self._normal_font)
        w = dc.GetTextExtent(self._top_line)[0]
        if self._bottom_line is not None:
            bw = dc.GetTextExtent(self._bottom_line)[0]
            w = bw if bw > w else w
        w = (w + 2 * self._x_margin) if w > (WarningWindow.min_size[0] - 2 * self._x_margin) else WarningWindow.min_size[0]
        return w

    def _getHeight(self):
        h = (WarningWindow.min_size[1] + 5 + PSConfig.GAUGE_Y_DELTA) if hasattr(self, "_gauge") else WarningWindow.min_size[1]
        dc = wx.ClientDC(self)
        dc.SetFont(self._normal_font)
        h = h if self._bottom_line is None else (h + dc.GetTextExtent(self._top_line)[1] + 5)
        return h


class ParamBoxSettingsWindow(wx.Frame):
    """
    class ParamBoxSettingWindow

    parametres:
                parent : fenetre parent, wx.Window
                pos : position de la fenetre sur l'ecran
                params : liste des parametre courant de l'objet pyo
                         [min, max, port, exp, text]
                func : fonction _setParams du PAramBox concerne
    """

    def __init__(self, parent, pos, params, func):
        self.parent = parent
        wx.Frame.__init__(self, None, -1, pos=pos, size=(120, 172), style=wx.NO_BORDER | wx.STAY_ON_TOP)
        self.SetTransparent(245)
        self.panel = wx.Panel(self, -1, size=self.GetSize() + (1, 1))

        self._min, self._max, self._port, self._exp, self._text, self._prec, self._int, self._dB = params
        self.callable = func

        # Positions
        self.leftMargin = 10
        self.topMargin = 8

        self.text_pos = (self.leftMargin, self.topMargin + 12)
        self.min_pos = (self.leftMargin, self.topMargin + 42)
        self.max_pos = (self.leftMargin, self.topMargin + 70)
        self.prec_pos = (self.leftMargin, self.topMargin + 95)
        self.port_pos = (self.leftMargin, self.topMargin + 120)
        self.exp_pos = (self.leftMargin + 55, self.topMargin + 120)
        self.int_pos = (self.leftMargin, self.topMargin + 140)
        self.dB_pos = (self.leftMargin + 55, self.topMargin + 140)

        # Controles
        x, y = self.text_pos
        self.textCtrl = wx.TextCtrl(self.panel, -1, pos=(x - 2, y), size=(100, -1), style=wx.TE_PROCESS_ENTER)
        self.textCtrl.SetBackgroundColour("#313131")
        self.textCtrl.SetForegroundColour("#d8ff00")
        self.textCtrl.SetValue(self._text)

        x, y = self.min_pos
        self.minCtrl = wx.TextCtrl(self.panel, -1, pos=(x + 37, y), size=(60, -1), style=wx.TE_PROCESS_ENTER)
        self.minCtrl.SetBackgroundColour("#313131")
        self.minCtrl.SetForegroundColour("#d8ff00")
        txt = "%.4f" % self._min
        self.minCtrl.SetValue(txt)

        x, y = self.max_pos
        self.maxCtrl = wx.TextCtrl(self.panel, -1, pos=(x + 37, y), size=(60, -1), style=wx.TE_PROCESS_ENTER)
        self.maxCtrl.SetBackgroundColour("#313131")
        self.maxCtrl.SetForegroundColour("#d8ff00")
        txt = "%.4f" % self._max
        self.maxCtrl.SetValue(txt)

        x, y = self.prec_pos
        self.precCtrl = wx.Choice(self.panel, -1, pos=(x + 37, y), choices=['1', '2', '3', '4'])
        self.precCtrl.SetSelection(self._prec - 1)

        x, y = self.port_pos
        self.portCheck = wx.CheckBox(self.panel, pos=(x, y))
        self.portCheck.SetValue(self._port)

        x, y = self.exp_pos
        self.expCheck = wx.CheckBox(self.panel, pos=(x, y))
        self.expCheck.SetValue(self._exp)

        x, y = self.int_pos
        self.intCheck = wx.CheckBox(self.panel, pos=(x, y))
        self.intCheck.SetValue(self._int)

        x, y = self.dB_pos
        self.dBCheck = wx.CheckBox(self.panel, pos=(x, y))
        self.dBCheck.SetValue(self._dB)

        # bitmap
        self.background = imgs.param_box_setup_bg.GetBitmap()

        # Binding events
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
        self.panel.Bind(wx.EVT_CHECKBOX, self.setdBDisplay, self.dBCheck)

    def OnPaint(self, evt):
        dc = wx.PaintDC(self.panel)

        # draw bg
        dc.DrawBitmap(self.background, 0, 0)

        font = wx.Font(**PSConfig.FONTS['light']['small'])

        # Texte
        dc.SetTextForeground("#FFFFFF")
        dc.SetFont(font)
        dc.DrawText("Name", self.leftMargin, self.topMargin)
        dc.DrawText("Min", self.leftMargin, self.min_pos[1] + 6)
        dc.DrawText("Max", self.leftMargin, self.max_pos[1] + 6)
        dc.DrawText("Prec.", self.leftMargin, self.prec_pos[1] + 6)
        dc.DrawText("Port", self.leftMargin + 23, self.port_pos[1] + 5)
        dc.DrawText("Exp", self.exp_pos[0] + 23, self.exp_pos[1] + 5)
        dc.DrawText("Int", self.int_pos[0] + 23, self.int_pos[1] + 5)
        dc.DrawText("dB", self.dB_pos[0] + 23, self.dB_pos[1] + 5)

    def OnEnter(self, evt):
        evt.Skip()
        self.callable()
        self.Hide()
        self.parent._destroySettingsWindow()

    def OnFocusCtrl(self, evt):
        evt.GetEventObject().SelectAll()

    def getFocus(self):
        self.SetFocus()

    def setText(self, evt):
        self._text = self.textCtrl.GetValue()

    def setMin(self, evt):
        try:
            self._min = float(self.minCtrl.GetValue().replace(',', '.'))
        except:
            # ne fait rien si le texte entre n'est pas un chiffre
            # -> l'ancienne valeur est conservee
            pass

    def setMax(self, evt):
        try:
            self._max = float(self.maxCtrl.GetValue().replace(',', '.'))
        except:
            # ne fait rien si le texte entre n'est pas un chiffre
            # -> l'ancienne valeur est conservee
            pass

    def setPort(self, evt):
        self._port = bool(self.portCheck.GetValue())

    def setExp(self, evt):
        self._exp = bool(self.expCheck.GetValue())

    def setPrec(self, evt):
        self._prec = self.precCtrl.GetSelection() + 1

    def setFloor(self, evt):
        self._int = bool(self.intCheck.GetValue())

    def setdBDisplay(self, evt):
        self._dB = bool(self.dBCheck.GetValue())

    def getWhiteListItems(self):
        return [self.textCtrl.GetId(), self.minCtrl.GetId(), self.maxCtrl.GetId()]


class WheelsBox(wx.Panel):
    def __init__(self, parent, bend_obj, mod_obj, pos, height):
        wx.Panel.__init__(self, parent, -1, pos=pos, size=(PSConfig.WHEELS_BOX_WIDTH, height))
        self._bg_colour = (45, 46, 38)
        self.SetBackgroundColour(self._bg_colour)
        self.parent = parent
        self.width, self.height = self.GetSize()
        self.active_fill_color = (31, 136, 175, 77)
        self.border_color = (31, 136, 175)

        self.bend_obj = bend_obj
        self.mod_obj = mod_obj

        # counter for idle state
        self._count = 0
        self._idle_rate = 10
        # stores last values for both objects
        self._last_values = [[0]*self._idle_rate,[0]*self._idle_rate]

        # bitmap
        self.background = imgs.bend_mod_bg.GetBitmap()
        # empty bitmap to store a snapshot of the parambox if idle
        self.buffer = wx.EmptyBitmap(self.width, self.height)
        self.titleFont = wx.Font(**PSConfig.FONTS['bold']['large'])

        self._initBoxCoords()

        # state variable
        self.UNUSED = False
        self.IDLE = False
        self.DRAW_BG = True

        # Binding events
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def reinit(self, bend_obj, mod_obj):
        self.bend_obj = bend_obj
        self.mod_obj = mod_obj

    def _scaleTranspo(self, value, range):
        try:
            semi = math.log(value, 2) * 12
        except ValueError:
            # considere le cas ou log(0) cause une erreur
            return 0

        if semi > range:
            return range / float(range)
        if semi < -range:
            return -range / float(range)
        return semi / float(range)

    def _initBoxCoords(self):
        self.y1 = 25
        self.y2 = self.height-10
        self.box_height = self.y2 - self.y1
        self.bbox_x1 = 8
        self.bbox_x2 = 41
        self.bbox_width = self.bbox_x2 - self.bbox_x1
        self.bbox_center = self.box_height/2+self.y1
        self.bbox_half_travel = self.bbox_center - self.y1
        self.mbox_x1 = 59
        self.mbox_x2 = 92
        self.mbox_width = self.mbox_x2 - self.mbox_x1

    def SmartRefresh(self):
        if self.UNUSED:
            return

        if self._count == self._idle_rate:
            if not self.IDLE:
                self.IDLE = self._checkIfIdle()
            self._count = 0

        bend_value = self.bend_obj.get()
        mod_value = self.mod_obj.get()
        if self._count > 0 and ( bend_value != self._last_values[0][self._count-1] or mod_value != self._last_values[1][self._count-1] ):
            self.IDLE = False
            self._count = 0

        if not self.IDLE:
            wx.CallAfter(self.Refresh)

        self._last_values[0][self._count] = bend_value
        self._last_values[1][self._count] = mod_value
        self._count += 1

    def ForceRefresh(self):
        self.IDLE = False
        self.Refresh()

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self, self.buffer)

        if self.UNUSED:
            bend_value = 1.
            mod_value = 0.
        else:
            try: # avoids rare crash when going from computer keyboard to midi keyboard
                bend_value = self.bend_obj.get()
                mod_value = self.mod_obj.get()
            except:
                bend_value = 1.
                mod_value = 0.

        if not self.IDLE:
            if self.DRAW_BG:
                dc.DrawBitmap(self.background, 0, 0)
            else:
                dc.SetBrush(wx.Brush(self._bg_colour))
                dc.DrawRectangle(0, 0, self.width, self.height)
                dc.SetPen(wx.Pen(self.border_color, 1))
                points = [(self.bbox_x1-2, self.y1-2),
                          (self.bbox_x2+2, self.y1-2),
                          (self.bbox_x2+2, self.y2+2),
                          (self.bbox_x1-2, self.y2+2),
                          (self.bbox_x1 - 2, self.y1 - 2)]
                dc.DrawLines(points)
                points = [(self.mbox_x1 - 2, self.y1 - 2),
                          (self.mbox_x2 + 1, self.y1 - 2),
                          (self.mbox_x2 + 1, self.y2 + 2),
                          (self.mbox_x1 - 2, self.y2 + 2),
                          (self.mbox_x1 - 2, self.y1 - 2)]
                dc.DrawLines(points)
                dc.SetTextForeground(self.border_color)
                dc.SetFont(self.titleFont)
                dc.DrawText("Bend", self.bbox_x1, 2)
                dc.DrawText("Mod", self.mbox_x1+4, 2)

            dc.SetPen(wx.Pen(self.active_fill_color, 1))
            dc.SetBrush(wx.Brush(self.active_fill_color))

            # Draw reference bars
            # Bend wheel
            if self.UNUSED:
                y = self.bbox_center
            else:
                y = math.ceil(
                    self.bbox_center - (self.bbox_half_travel * self._scaleTranspo(bend_value, self.bend_obj._brange)))
            points = [(self.bbox_x1, self.bbox_center),
                      (self.bbox_x1, y),
                      (self.bbox_x2, y),
                      (self.bbox_x2, self.bbox_center)]
            dc.DrawPolygon(points)
            # Mod wheel
            height = math.floor(self.box_height * mod_value)
            y = self.y2 - height + 1
            dc.DrawRectangle(self.mbox_x1, y, self.mbox_width, height)
            # Bend wheel middle line
            dc.GetPen().SetWidth(2)
            dc.DrawLine(self.bbox_x1, self.bbox_center - 1, self.bbox_x2, self.bbox_center - 1)
    # end OnPaint

    def OnMove(self, evt):
        evt.Skip()

    def OnQuit(self, evt):
        evt.Skip()

    def _checkIfIdle(self):
        # check if all last values are the same
        if self._last_values[0].count(self._last_values[0][0]) == self._idle_rate:
            return True
        elif self._last_values[1].count(self._last_values[1][0]) == self._idle_rate:
            return True
        else:
            return False

    def IsIdle(self):
        return self.IDLE

    def IsUnused(self):
        return self.UNUSED

    def unlink(self, namespace):
        pass

    def relink(self, namespace):
        pass

    def disable(self, namespace):
        pass

    def prepareForExport(self):
        pass

    def setDisplayDB(self, *args, **kwargs):
        pass

    def stopMatchMode(self):
        pass

    def setUnused(self, state):
        # disabled when VirtualKeyboard is in use
        if state:
            self.UNUSED = True
        else:
            self.UNUSED = False
            self.IDLE = False

    def setPerformanceMode(self, state):
        self.DRAW_BG = not state


class BoxBase(wx.Panel):
    """
    class BoxBase(wx.Panel)

    Definit les paramtres de base d'une ParamBox.

    parametres :
                parent : fenetre parent (fenetre principale), wx.Window
                pos : position relative au cadre principal en pixel
                size : grosseur, tuple (w,h)
    """
    def __init__(self, parent, pos, size):
        wx.Panel.__init__(self, parent, -1, pos=pos, size=size)
        self._bg_colour = (45,46,38)
        self.SetBackgroundColour(self._bg_colour)

        # bitmaps
        self.active_bg = imgs.param_box_active_bg.GetBitmap()
        self.inactive_bg = imgs.param_box_inactive_bg.GetBitmap()
        self.hijack_active_bg = imgs.param_box_hijack_active_bg.GetBitmap()
        self.hijack_inactive_bg = imgs.param_box_hijack_inactive_bg.GetBitmap()

        # colours
        if PSConfig.PLATFORM == 'darwin':
            self.active_color = "#d8ff00"
            self.inactive_color = "#f0f4d7"
            self.hijack_color = "#6cff00"
            self.hijack_inactive_color = "#70a34f"
            self.active_fill_color = (216, 255, 0, 51)
            self.inactive_fill_color = (240, 244, 215, 38)
            self.hijack_fill_color = (108, 255, 0, 51)
            self.hijack_inactive_fill_color = (112, 163, 79, 38)
        elif PSConfig.PLATFORM in ('win32', 'linux2'):
            self.active_color = "#d8ff00"
            self.inactive_color = "#e4ff81"
            self.hijack_color = "#7ce51e"
            self.hijack_inactive_color = "#a7ea6c"
            self.active_fill_color = (134,171,0)
            self.inactive_fill_color = (108,127,38)
            self.hijack_fill_color = (78,144,19)
            self.hijack_inactive_fill_color = (71,102,44)

        # Variables generales
        self.parent = parent
        self.width, self.height = size

        # Variables pour le MatchMode
        self.MATCH_MODE = False
        self.preset_value = None
        self.match_prec = 1.5 # a float between 1 and 2

        # Variables d'etat
        self.MIDI_LEARN = False
        self.DRAW_BG = True
        self.settingsWindow = None

        # Binding events
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, evt):
        evt.Skip()

    def ShowPatchWindow(self, evt):
        if not evt.ShiftDown() and not evt.ControlDown() and not evt.CmdDown():
            #verify that the ParamBox already requested the display of the PatchWindow
            if self.parent.patchWindow._obj is not None and self.parent.patchWindow._obj.GetId() == self.GetId():
                self.parent.patchWindow.HideWindow()
            else:
                if not self.MIDI_LEARN and not self.MATCH_MODE and self.settingsWindow is None:
                    self.parent._last_changed = self.GetId()
                    self.parent.patchWindow.ShowWindow(evt.GetEventObject())


class ParamBox(BoxBase):
    """
    class ParamBox(BoxBase)

    parametres :
                parent : fenetre parent, wx.Window
                pos : position relative au cadre principal, c-a-d le parent
                size : taille en pixel de la boite (w,h)
                list : [ text, MidiControl (, float_precision) ]
    """

    def __init__(self, parent, pos, title, obj):
        BoxBase.__init__(self, parent, pos=pos, size=PSConfig.UNIT_SIZE)

        # Variables generales
        self.text = title
        self.pyo_obj = obj
        self.ctl_num = self.pyo_obj.getCtlNumber()
        self.last_value = 0.
        self.last_norm_value = 0.
        self._box_px_range = 123
        self.val_prec = 2
        self._str_float_prec = "%."+str(self.val_prec)+"f"
        self._refresh_count = 0
        # variables pour le hijack mode
        self.mouse_y_org = 0
        self.value_ratio = 500.
        self.value_delta = 0. # value added to org_hijack_value to calculate the new value
        self.org_hijack_value = 0. # set on mouse down
        self.new_hijack_value = 0. # set during dragging
        self.last_midi_ctl_value = 0. # stores the value of the midi ctl before hijack begins

        # fonts
        self.valueFont = wx.Font(**PSConfig.FONTS['bold']['xl_title'])
        self.dBvalueFont = wx.Font(**PSConfig.FONTS['bold']['large_title'])
        self.titleFont = wx.Font(**PSConfig.FONTS['bold']['large'])
        self.unusedFont = wx.Font(**PSConfig.FONTS['bold']['norm'])
        self.midiLearnFont = wx.Font(**PSConfig.FONTS['bold']['title1'])

        # state variable
        self.IDLE = False # True quand le dessin est a jour et que la boite n'est pas en train d'etre modifiee
        self.UNUSED = True # False aussitot que 'parent.last_changed' est assignee a self
        self.HIJACKED = False # True quand l'usager change la valeur a la souris
        self.DRAGGED = False # sert a implementer le click and drag
        self.CLICKED = False # sert a implementer le click and drag
        self.DISPLAY_DB = False

        # empty bitmap to store a snapshot of the parambox if idle
        self.buffer = wx.EmptyBitmap(PSConfig.UNIT_SIZE[0], PSConfig.UNIT_SIZE[1])

        # Binding events
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.OnMouseCaptureLost)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)

    def Enable(self, state=True):
        if state:
            BoxBase.Enable(self)
        else:
            self.DRAGGED = False
            self.CLICKED = False
            if self.HasCapture():
                self.ReleaseMouse()
            BoxBase.Enable(self, False)

    def OnMove(self, evt):
        """
        Called by the main program OnMove method.
        """
        if self.settingsWindow is not None:
            if isinstance(self.settingsWindow, wx.Frame):
                pos = self.GetScreenPosition() + (self.GetSize()[0] - 5, -10)
                self.settingsWindow.SetPosition(pos)

    def SmartRefresh(self):
        if self.UNUSED:
            return
        if self.parent._last_changed == self.GetId() or self.last_value != self.pyo_obj.get() or self.MATCH_MODE or self.MIDI_LEARN:
            wx.CallAfter(self.Refresh)
        elif not self.IDLE:
            wx.CallAfter(self.Refresh)
        else:
            self._refresh_count += 1
            if self._refresh_count%13 == 0:
                wx.CallAfter(self.Refresh)
            if self._refresh_count == 13000:
                self._refresh_count = 0

    def ForceRefresh(self):
        self.IDLE = False
        self.Refresh()

    def OnPaint(self, evt):
        """
        Decide si la fenetre doit etre dessinee a nouveau.
        Autrement, utilise le buffer en memoire.
        """
        if self.HIJACKED:
            self._setHijackNormValue()
        dc = wx.BufferedPaintDC(self, self.buffer)
        # La boite de controle est inutilisee
        if self.UNUSED:
            self.OnPaintUnused(dc)
        # La boite de controle est utilisee
        else:
            if self.HIJACKED and self.pyo_obj.getNormValueMidi() != self.last_midi_ctl_value:
                self.HIJACKED = False
                self.pyo_obj.setHijack(False)
            value = self.pyo_obj.get()
            # Verifie si le carre doit etre dessine actif ou inactif
            if value != self.last_value or self.parent._last_changed == self.GetId() or self.MATCH_MODE or self.MIDI_LEARN:
                self.OnPaintActive(dc, value)
            else:
                self.OnPaintInactive(dc, value)

    def OnPaintUnused(self, dc):
        if not self.IDLE:
            self.IDLE = True
            if self.DRAW_BG:
                dc.DrawBitmap(self.inactive_bg, 0, 0)
            else:
                self._drawCheapBg(dc, self.inactive_color)
            # Unused text
            dc.SetFont(self.unusedFont)
            dc.SetTextForeground(self.inactive_color)
            w, h = dc.GetTextExtent(self.text)
            x = (self.width - w) / 2
            y = (self.height - h) / 2
            dc.DrawText(self.text, x, y)

    def OnPaintActive(self, dc, value):
        """
        Routine de dessin principal.
        Tient compte de tous les modes : MIDI_LEARN, MATCH_MODE et normal
        """
        self.parent._last_changed = self.GetId() # changed the type of this variable from object to ID
        self.IDLE = False
        if self.HIJACKED:
            # hijack style
            if self.DRAW_BG:
                dc.DrawBitmap(self.hijack_active_bg, 0, 0)
            else:
                self._drawCheapBg(dc, self.hijack_color)
            dc.SetTextForeground(self.hijack_color)
            dc.SetPen(wx.Pen(self.hijack_fill_color, 1))
            dc.SetBrush(wx.Brush(self.hijack_fill_color))
        else:
            # basic active style
            if self.DRAW_BG:
                dc.DrawBitmap(self.active_bg, 0, 0)
            else:
                self._drawCheapBg(dc, self.active_color)
            dc.SetTextForeground(self.active_color)
            dc.SetPen(wx.Pen(self.active_fill_color, 1))
            dc.SetBrush(wx.Brush(self.active_fill_color))

        if self.MIDI_LEARN:
            # MIDI LEARN text
            dc.SetFont(self.midiLearnFont)
            w, h = dc.GetTextExtent("MIDI")
            x = (self.width - w) / 2
            dc.DrawText("MIDI", x, 15)
            w, h = dc.GetTextExtent("LEARN")
            x = (self.width - w) / 2
            dc.DrawText("LEARN", x, 12 + h)

            # ctl number
            dc.SetFont(self.valueFont)
            ctl_txt = "%d" % self.ctl_num
            w, h = dc.GetTextExtent(ctl_txt)
            x = (self.width - w) / 2
            dc.DrawText(ctl_txt, x, 65)
        else:
            # draw level indicator
            width = (value - self.pyo_obj.getMin()) / self.pyo_obj.getRange() * self._box_px_range
            dc.DrawRectangle(4, 4, width, 102)

            # current value text and pos
            if self.DISPLAY_DB:
                dc.SetFont(self.dBvalueFont)
                text_value = self._getDBDisplayValue(value)
            else:
                dc.SetFont(self.valueFont)
                text_value = self._str_float_prec % value
            w, h = dc.GetTextExtent(text_value)
            x = (self.width - w) / 2

            if self.MATCH_MODE:
                # if relatively close to preset value, go to next control
                step = self.pyo_obj.getRange()/128.*self.match_prec
                if value >= (self.preset_value - step) and value <= (self.preset_value + step):
                    self.MATCH_MODE = False
                    self.parent._nextPreset() # remplacer cet appel par un event
                else:
                    # affichage de la valeur courante
                    dc.DrawText(text_value, x, 40)

                    # affichage de la valeur du preset
                    dc.SetFont(self.midiLearnFont)
                    cur_col = dc.GetTextForeground() # changes according to hijack vs. normal
                    dc.SetTextForeground("#d31ee5")
                    if self.DISPLAY_DB:
                        text_preset_value = self._getDBDisplayValue(self.preset_value)
                    else:
                        text_preset_value = "%.3f" % self.preset_value
                    w, h = dc.GetTextExtent(text_preset_value)
                    x = (self.width - w) / 2
                    dc.DrawText(text_preset_value, x, 53 + h)
                    dc.SetTextForeground(cur_col)
            else:
                dc.DrawText(text_value, x, 50)
            # important pour que self.parent.last_changed soit modifiee
            self.last_value = value
            self.last_norm_value = self.pyo_obj.getNormValue()

            # Draw title text
            dc.SetFont(self.titleFont)
            w, h = dc.GetTextExtent(self.text)
            x = (self.width - w) / 2
            dc.DrawText(self.text, x, 20)

    def OnPaintInactive(self, dc, value):
        if not self.IDLE:
            self.IDLE = True
            if self.HIJACKED:
                if self.DRAW_BG:
                    dc.DrawBitmap(self.hijack_inactive_bg, 0, 0)
                else:
                    self._drawCheapBg(dc, self.hijack_inactive_color)
                dc.SetTextForeground(self.hijack_inactive_color)
                dc.SetPen(wx.Pen(self.hijack_inactive_fill_color, 1))
                dc.SetBrush(wx.Brush(self.hijack_inactive_fill_color))
            else:
                if self.DRAW_BG:
                    dc.DrawBitmap(self.inactive_bg, 0, 0)
                else:
                    self._drawCheapBg(dc, self.inactive_color)
                dc.SetTextForeground(self.inactive_color)
                dc.SetPen(wx.Pen(self.inactive_fill_color, 1))
                dc.SetBrush(wx.Brush(self.inactive_fill_color))

            # draw level indicator
            width = (value - self.pyo_obj.getMin()) / self.pyo_obj.getRange() * self._box_px_range
            dc.DrawRectangle(4, 4, width, 102)

            # draw current value
            if self.DISPLAY_DB:
                dc.SetFont(self.dBvalueFont)
                text_value = self._getDBDisplayValue(value)
            else:
                dc.SetFont(self.valueFont)
                text_value = self._str_float_prec % value
            w, h = dc.GetTextExtent(text_value)
            x = (self.width - w) / 2
            dc.DrawText(text_value, x, 50)

            # Draw title text
            dc.SetFont(self.titleFont)
            w, h = dc.GetTextExtent(self.text)
            x = (self.width - w) / 2
            dc.DrawText(self.text, x, 20)

    def _drawCheapBg(self, dc , color):
        dc.SetBrush(wx.Brush(self._bg_colour))
        dc.DrawRectangle(0, 0, self.width, self.height)
        dc.SetPen(wx.Pen(color, 1))
        offset = 3
        points = [(offset, offset), (self.width - offset, offset),
                  (self.width - offset, self.height - offset), (offset, self.height - offset), (offset, offset)]
        dc.DrawLines(points)

    def OnMouseMove(self, evt):
        if self.CLICKED:
            if not self.DRAGGED:
                self.DRAGGED = True
                self.parent._last_changed = self.GetId()
            if not self.HIJACKED:
                self.HIJACKED = True
                self.pyo_obj.setHijack(True)
            self.value_delta = (self.mouse_y_org - wx.GetMousePosition()[1])/self.value_ratio
            self.new_hijack_value = self.value_delta + self.org_hijack_value

    def OnMouseDown(self, evt):
        self.CLICKED = True
        self.CaptureMouse()
        self.mouse_y_org = wx.GetMousePosition()[1]
        self.org_hijack_value = self.pyo_obj.getNormValue()
        if not self.HIJACKED:
            self.last_midi_ctl_value = self.pyo_obj.getNormValue()

    def OnMouseUp(self, evt):
        if not self.DRAGGED:
            if evt.ShiftDown() and not self.UNUSED:
                if self.settingsWindow is None:
                    self._showSettingsWindow()
                    self.Parent._addToWhiteList(self.settingsWindow.getWhiteListItems())
            elif evt.CmdDown() and not self.UNUSED:
                self._toggleMidiLearn()
            else:
                if self.settingsWindow is not None:
                    self._setParams()
                    wx.CallAfter(self.Refresh)
                    self.Parent._removeFromWhiteList(self.settingsWindow.getWhiteListItems())
                    # le timer permet d'eviter que la PatchWindow se rouvre
                    wx.CallLater(10, self._destroySettingsWindow)
                if self.MIDI_LEARN:
                    wx.CallLater(10, self._toggleMidiLearn)
            self.ShowPatchWindow(evt)
        else:
            self.DRAGGED = False
        self.ReleaseMouse()
        self.CLICKED = False

    def OnMouseCaptureLost(self, evt):
        self.DRAGGED = False
        self.CLICKED = False
        self.OnMouseUp(evt)

    def OnQuit(self, evt):
        """
        Called by the main program OnQuit method.
        """
        if self.settingsWindow is not None:
            self.settingsWindow.Destroy()

    def IsIdle(self):
        return self.IDLE

    def IsUnused(self):
        return self.UNUSED

    def disable(self, namespace):
        """
        Deconnecte le controle midi et place la ParamBox en mode Unused.
        Remet les valeurs par defaut.
        """
        if self.UNUSED:
            return
        self.pyo_obj.reset(namespace)
        self.text = "Unused"
        self.IDLE = False
        self.UNUSED = True
        self.DISPLAY_DB = False
        wx.CallAfter(self.Refresh)

    def enable(self, text):
        self.text = text
        self.IDLE = False
        self.UNUSED = False
        self.parent._last_changed = self.GetId()
        wx.CallAfter(self.Refresh)

    def unlink(self, namespace):
        """
        Defait le lien du controle midi avec le parametre courant en vue
        de faire un nouveau lien
        """
        if self.pyo_obj is not None:
            self.pyo_obj.unlink(namespace)

    def relink(self, namespace):
        if not self.UNUSED and self.pyo_obj is not None:
            self.pyo_obj.relink(namespace)

    def getMidiControl(self):
        return self.pyo_obj._obj

    def getText(self):
        return self.text

    def matchValue(self, value):
        self.MATCH_MODE = True
        self.preset_value = value

    def stopMatchMode(self):
        self.MATCH_MODE = False

    def _getDBDisplayValue(self, x):
        if x < 0.00000001:
            return u"-\u221EdB"
        else:
            return "%.1fdB" % PSUtils.ampTodB(x, 1)

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
        self.parent._last_changed = self.GetId()
        self.settingsWindow = ParamBoxSettingsWindow(self, (0, 0), self._getParams(), self._setParams)
        pos = self.GetScreenPosition() + (self.GetSize()[0] - 5, -10)
        self.settingsWindow.SetPosition(pos)
        self.settingsWindow.Show()

    def _destroySettingsWindow(self):
        self.settingsWindow.Show(False)
        self._destroyTimer = wx.CallLater(500, self.settingsWindow.Destroy)
        self.settingsWindow = None

    def _getParams(self):
        return [self.pyo_obj.getMin(), self.pyo_obj.getMax(), self.pyo_obj.hasPort(),
                self.pyo_obj.hasExp(), self.text, self.val_prec, self.pyo_obj.hasFloor(), self.DISPLAY_DB]

    def _setParams(self):
        self.pyo_obj.setScale(self.settingsWindow._min, self.settingsWindow._max)
        self.pyo_obj.setPort(self.settingsWindow._port)
        self.pyo_obj.setExp(self.settingsWindow._exp)
        self.text = self.settingsWindow._text
        self.setDisplayPrecision(self.settingsWindow._prec)
        self._str_float_prec = "%." + str(self.val_prec) + "f"
        self.DISPLAY_DB = self.settingsWindow._dB
        self.pyo_obj.setFloor(self.settingsWindow._int)

    def _setCtlNumLearn(self, num):
        self.ctl_num = num

    def _setHijackNormValue(self):
        self.pyo_obj.setHijackValue(self.new_hijack_value)

    def setHijackNormValueForExport(self, value):
        """
        Is only called once at the moment a preset is loaded during an export.
        Note : a preset (during an export) will be loaded only if it is the first time the script is executed.
        """
        self.HIJACKED = True
        self.pyo_obj.setHijack(True)
        self.last_value = -1 # trick it to paint it active once
        self.new_hijack_value = value
        self.Refresh()

    def prepareForExport(self):
        if self.UNUSED:
            return
        self.HIJACKED = True
        self.pyo_obj.setHijack(True)
        self.new_hijack_value = self.last_norm_value
        self.pyo_obj.setHijackValue(self.new_hijack_value)

    def setPerformanceMode(self, state):
        if state:
            self.Unbind(wx.EVT_LEFT_DOWN)
            self.Unbind(wx.EVT_LEFT_UP)
            self.Unbind(wx.EVT_MOTION)
            self.parent.Unbind(wx.EVT_MOVE, id=self.GetId())
        else:
            self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
            self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
            self.Bind(wx.EVT_MOTION, self.OnMouseMove)
            self.parent.Bind(wx.EVT_MOVE, self.OnMove, id=self.GetId())
        self.DRAW_BG = not state

    def setDisplayPrecision(self, value):
        self.val_prec = value
        self._str_float_prec = "%." + str(self.val_prec) + "f"

    def setDisplayDB(self, value):
        self.DISPLAY_DB = value


class StatusBarPanel(wx.Panel):
    def __init__(self, parent, pos, size, numChnls):
        wx.Panel.__init__(self, parent, -1, pos, size)

        # vu meter x pos
        self.vm_x = parent.GetSize()[0] - 265
        # master volume x pos
        self.mv_x = parent.GetSize()[0] / 2 - 80
        # rec section
        self.rec_x = 255
        self._upv_count = 0 # count for poly val refresh
        self._upv_last_val = -1 # last poly val

        # bouton d'enregistrement et txtCtrl
        self.recTxtCtrl = PSControls.PSRecordTextCtrl(self, (self.rec_x + 32, 12 - PSConfig.Y_OFFSET), "No tracks")
        x = self.recTxtCtrl.GetSize()[0] + self.recTxtCtrl.GetPosition()[0]
        self.open_rec_btn = PSButtons.OpenRecButton(self, (x, 12 - PSConfig.Y_OFFSET))

        self.rec_btn = PSButtons.RecButton(self, (self.rec_x, 6 - PSConfig.Y_OFFSET))
        self.rec_btn.disable()

        # fenetre des pistes enregistrees
        self.tracks_window = RecordedTracksWindow(self, self.GetParent()._server_, self.GetParent().script_namespace)

        # master volume slider
        self.vol_slider = PSControls.VolumeSlider(self, (self.mv_x + 100, 21 - PSConfig.Y_OFFSET), 150)
        self._changeMasterVol(None)

        # vu meter object
        self.vu_meter = PSControls.VuMeter(self, (self.vm_x, 13 - PSConfig.Y_OFFSET), numChnls)
        self.setVuMeterPosition(numChnls)
        # clip light object
        x = parent.GetSize()[0]-23
        self.clip_light = PSControls.ClipLight(self, (x, 17 - PSConfig.Y_OFFSET), .4)

        self._font_11 = wx.Font(**PSConfig.FONTS['light']['small'])
        self._font_13 = wx.Font(**PSConfig.FONTS['light']['med'])
        self._font_17 = wx.Font(**PSConfig.FONTS['light']['title2'])

        # CPU, RAM & poly usage infos
        self._proc_name = 'python'
        self.totalMem = psutil.virtual_memory()[0]
        self.python_id = self.getPythonID()
        self.python_proc = psutil.Process(self.python_id)


        self._proc_history_max = 4  # amount of data to store
        self._proc_counter = 0
        self._cpu_history_data = [0] * self._proc_history_max  # will keep track of cpu usage history
        self._mem_history_data = [0] * self._proc_history_max  # will keep track of memory usage history

        self.voicesText = wx.StaticText(self, -1, "", (15, 30 - PSConfig.Y_OFFSET))
        self.voicesText.SetFont(self._font_11)
        self.voicesText.SetForegroundColour("#FFFFFF")
        self.updatePolyValue(0)

        self.cpuText = wx.StaticText(self, -1, "", (15, 12 - PSConfig.Y_OFFSET))
        self.cpuText.SetFont(self._font_11)
        self.cpuText.SetForegroundColour("#FFFFFF")

        self.slashes = wx.StaticText(self, -1, "//", (93, 10 - PSConfig.Y_OFFSET))
        self.slashes.SetFont(self._font_17)
        self.slashes.SetForegroundColour("#FFFFFF")

        self.ramText = wx.StaticText(self, -1, "", (120, 12 - PSConfig.Y_OFFSET))
        self.ramText.SetFont(self._font_11)
        self.ramText.SetForegroundColour("#FFFFFF")
        self.updateUsage(-1)

        # empty bitmap to pass to the BufferedPaintDC
        self._buffer = wx.EmptyBitmap(self.GetSize()[0], self.GetSize()[1])
        # bitmap
        self.background = imgs.status_bar_background.GetBitmap()

        # timer to update cpu and ram usage
        self._cpu_timer = wx.Timer(self, -1)
        self._cpu_timer.Start(500)
        # timer to show record time
        self._rec_timer = wx.Timer(self, -1)
        # conserve le temps d'enregistrement en secondes
        self._rec_time = 0
        # keeps track of the number of tracks in the window
        self.__track_count__ = 0
        self._rec_autostop_timer = wx.Timer(self, -1)

        # Binding events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.updateUsage, self._cpu_timer)
        self.Bind(wx.EVT_TIMER, self.updateRecTime, self._rec_timer)
        self.Bind(wx.EVT_TIMER, self._automaticRecStop, self._rec_autostop_timer)
        self.Bind(PSButtons.EVT_BTN_REC, self._toggleRecording)
        self.Bind(PSButtons.EVT_BTN_OPEN, self._showRecordedTracks)
        self.vol_slider.Bind(PSControls.EVT_VOL_CHANGED, self._changeMasterVol)

    def _changeMasterVol(self, evt):
        self.GetParent()._server_.amp = self.vol_slider.getValue()

    def _setMasterVolSlider(self, value):
        self.vol_slider.setValue(value)

    def _toggleRecording(self, evt):
        if evt.GetState():
            id = self.tracks_window.startRecording() # returns 0 in case of error, otherwise returns the id
            if id:
                self._rec_time = 0
                self.recTxtCtrl.SetText("Track %d" % id)
                self.recTxtCtrl.SetTime("00:00")
                self._rec_timer.Start(1000)
                self._rec_autostop_timer.Start(PSConfig.REC_MAX_TIME * 1000)
                self.recTxtCtrl.SetRecState(evt.GetState())
            else:
                self.rec_btn._setState(False)
                script_name = os.path.split(self.GetParent()._script_path)[1]
                self.GetParent().exc_win.printException(script_name,
                                                        "Cannot record because the script does not have a 'mix' object.")
        else:
            self.tracks_window.stopRecording()
            self._rec_timer.Stop()
            self._rec_autostop_timer.Stop()
            self.recTxtCtrl.SetRecState(evt.GetState())

    def _automaticRecStop(self, evt):
        self._rec_autostop_timer.Stop()
        self.rec_btn.ToggleState(evt)

    def _showRecordedTracks(self, evt):
        if evt.GetState():
            self.tracks_window.ShowWindow(self.GetParent().GetPosition())
        else:
            self.tracks_window.HideWindow()

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self, self._buffer)

        dc.DrawBitmap(self.background, 0, 0)

        dc.SetTextForeground("#FFFFFF")
        dc.SetFont(self._font_13)
        dc.DrawText("Master volume", self.mv_x, 21 - PSConfig.Y_OFFSET * 2)
        dc.DrawText("Output level", self.vm_x - 80, 21 - PSConfig.Y_OFFSET * 2)

    def GetRegion(self, x, y, w, h):
        img = self._buffer.ConvertToImage()
        region = img.GetSubImage(wx.Rect(x, y, w, h))
        return wx.BitmapFromImage(region)

    def getPythonID(self):
        create_time = None
        id = None
        num = 0
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name'])
            except psutil.NoSuchProcess:
                pass
            else:
                if pinfo['name'] == self._proc_name:
                    num += 1
                    if create_time is None:
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
            self.vu_meter.SetPosition((self.vm_x, 19 - PSConfig.Y_OFFSET))
        elif chnls == 2:
            self.vu_meter.SetPosition((self.vm_x, 13 - PSConfig.Y_OFFSET))
        elif chnls == 3:
            self.vu_meter.SetPosition((self.vm_x, 8 - PSConfig.Y_OFFSET))
        elif chnls == 4:
            self.vu_meter.SetPosition((self.vm_x, 2 - PSConfig.Y_OFFSET))

    def updateUsage(self, evt):
        try:
            self._cpu_history_data[self._proc_counter] = self.python_proc.cpu_percent()
            self._mem_history_data[self._proc_counter] = self.python_proc.memory_percent() / 100. * self.totalMem / (1024 ** 2.)
        except psutil.NoSuchProcess:
            # this exception is raised once in a while
            # for some reason, the Python id becomes invalid
            # between the time the program initialises and this method is called
            self.python_id = self.getPythonID()
            self.python_proc = psutil.Process(self.python_id)
            return

        cpu = sum(self._cpu_history_data)/float(len(self._cpu_history_data))
        if cpu < 70.:
            self.cpuText.SetForegroundColour("#FFFFFF")
        elif cpu < 90.:
            self.cpuText.SetForegroundColour("#F69C55")
        else:
            self.cpuText.SetForegroundColour("#FF0000")
        self.cpuText.SetLabel("CPU : %.1f%%" % cpu)
        self.ramText.SetLabel("RAM : %.2f Mb" % ( sum(self._mem_history_data)/float(len(self._mem_history_data)) ) )
        self._proc_counter += 1
        if self._proc_counter == self._proc_history_max:
            self._proc_counter = 0

    def updateRecTime(self, evt):
        self._rec_time += 1
        min = self._rec_time / 60
        sec = self._rec_time % 60
        if min > 9:
            min = "%d" % min
        else:
            min = "0%d" % min
        if sec > 9:
            sec = "%d" % sec
        else:
            sec = "0%d" % sec
        self.recTxtCtrl.SetTime(min + ":" + sec)

    def noMoreTracks(self):
        self.recTxtCtrl.SetText("No tracks")
        self.recTxtCtrl.SetTime("00:00")

    def updatePolyValue(self, value):
        self._upv_count += 1
        if self._upv_last_val != value:
            if value == 0:
                wx.CallAfter(self._doSafeUpdatePolyValue, value, False)
            elif value == PSConfig.PYOSYNTH_PREF['poly']:
                wx.CallAfter(self._doSafeUpdatePolyValue, value, True)
            elif self._upv_count%7 == 0:
                wx.CallAfter(self._doSafeUpdatePolyValue, value, False)
                if self._upv_count == 70000:
                    self._upv_count = 0

    def _doSafeUpdatePolyValue(self, value, max):
        """
        This method has to be called through wx.CallAfter to avoid crashes.
        """
        self._upv_last_val = value
        if max is True:
            self.voicesText.SetForegroundColour("#FF0000")
        else:
            self.voicesText.SetForegroundColour("#FFFFFF")
        self.voicesText.SetLabel("Polyphony Voices : %d/%d" % (value, PSConfig.PYOSYNTH_PREF['poly']))


class MenuPanel(wx.Panel):
    def __init__(self, parent, pos, size):
        wx.Panel.__init__(self, parent, -1, pos, size)

        self.serverSetupPanel = None

        # positions des elements
        self.top_margin = 16
        self.btn_open_x = 154
        self.btn_save_x = self.btn_open_x + 77
        self.script_txt_x = self.btn_save_x + 93
        self.adsr_section = self.script_txt_x + 448

        self.font = wx.Font(**PSConfig.FONTS['light']['norm'])

        ##Declaration des boutons et labels de gauche a droite
        # boutons open et save
        self.btn_open = PSButtons.OpenButton(self, (self.btn_open_x, self.top_margin))
        self.btn_save = PSButtons.SaveButton(self, (self.btn_save_x, self.top_margin))

        # label du nom du script
        self.script_name = PSControls.PSScriptTextCtrl(self, (self.script_txt_x, 18), "No script selected")

        # bouton run
        x = self.script_name.GetWidth() + self.script_name.GetPosition()[0]
        self.btn_run = PSButtons.RunButton(self, (x, self.script_name.GetPosition()[1]))
        self.btn_run.disable()

        self.server_setup_btn = PSButtons.ServerSetupButton(self, (self.GetSize()[0] - 17, 0))

        # statut du script
        x += self.btn_run.GetSize()[0] + 10
        self.script_status = wx.StaticText(self, -1, "|  Stopped", (x, self.top_margin + 8 - PSConfig.Y_OFFSET))
        self.script_status.SetFont(self.font)
        self.script_status.SetForegroundColour("#FFFFFF")

        # metronome
        x += self.script_status.GetSize()[0] + 35
        self.metro = PSControls.PSClick(self, (x, self.top_margin - 2), 120, self.GetParent()._server_.getNchnls())

        # adsr envelope knobs
        self._attackKnob = PSControls.PSSmallRotaryKnob(self, pos=(self.adsr_section, 10), min=0, max=1, text='A',
                                                        ratio=100, shift_mul=100, valprec=3)

        x = self._attackKnob.GetPosition()[0] + self._attackKnob.GetSize()[0] + 10
        self._decayKnob = PSControls.PSSmallRotaryKnob(self, (x, 10), 0, 1, 'D', 80, 50, 2)

        x = self._decayKnob.GetPosition()[0] + self._decayKnob.GetSize()[0] + 10
        self._sustainKnob = PSControls.PSSmallRotaryKnob(self, (x, 10), 0, 1, 'S', 80, 50, 2)

        x = self._sustainKnob.GetPosition()[0] + self._sustainKnob.GetSize()[0] + 10
        self._releaseKnob = PSControls.PSSmallRotaryKnob(self, (x, 10), 0, 4, 'R', 50, 50, 2)

        # txt ctrl interface
        self.snd_card_ctrl = PSControls.PSTextCtrl(self, (0, 0), "Dummy text")
        posx = self.GetSize()[0] - self.snd_card_ctrl.GetWidth() - self.server_setup_btn.GetSize()[0] - 15
        self.snd_card_ctrl.SetPosition((posx, 12))

        fontSmall = wx.Font(**PSConfig.FONTS['light']['xsmall'])

        # quick info
        self.quick_info = wx.StaticText(self, -1, "sr : 44.1 | bfs : 256 | 2 chnls", (posx - 22, 40))
        self.quick_info.SetForegroundColour("#FFFFFF")
        self.quick_info.SetFont(fontSmall)

        # bitmaps
        # empty bitmap to pass to the BufferedPaintDC
        self._buffer = wx.EmptyBitmap(self.GetSize()[0], self.GetSize()[1])
        self.back = imgs.menu_background.GetBitmap()
        self.logo = imgs.logo.GetBitmap()
        self.separator = imgs.separator.GetBitmap()

        # Binding events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.server_setup_btn.Bind(PSButtons.EVT_BTN_CLICKED, self.ShowServerSetup)

    def __getitem__(self, i):
        if i == 'click':
            return self.metro[i]

    def reinit(self):
        self._attackKnob.reinit()
        self._decayKnob.reinit()
        self._sustainKnob.reinit()
        self._releaseKnob.reinit()
        self.metro.reinit(self.GetParent()._server_.getNchnls())

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self, self._buffer)
        dc.Clear()
        dc.DrawBitmap(self.back, 0, 0)
        dc.DrawBitmap(self.logo, 0, 0)
        dc.DrawBitmap(self.separator, 133, 7)

    def GetRegion(self, x, y, w, h):
        img = self._buffer.ConvertToImage()
        region = img.GetSubImage(wx.Rect(x, y, w, h))
        return wx.BitmapFromImage(region)

    def _setScriptName(self, name):
        self.script_name.SetText(PSUtils.shortenText(name, 20))
        self.btn_run.enable()
        wx.CallLater(180, self._moveScriptNameCtrl)

    def _moveScriptNameCtrl(self):
        # reposition du btn run
        x = self.script_name.GetWidth() + self.script_name.GetPosition()[0]
        self.btn_run.SetPosition((x, self.btn_run.GetPosition()[1]))
        # reposition le statut par rapport au nouveau nom de script
        x += self.btn_run.GetSize()[0] + 10
        self.script_status.SetPosition((x, self.script_status.GetPosition()[1]))

    def _updateStatus(self, is_running):
        # met a jour le statut du script
        if is_running:
            self.script_status.SetLabel("|  Running")
        else:
            self.script_status.SetLabel("|  Stopped")

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
        text = "sr : %.1f | bfs : %d | %d chnls" % (
            self.serverSetupPanel.getSamplingRate() / 1000., self.serverSetupPanel.getBufferSize(),
            self.serverSetupPanel.getNchnls())
        self.quick_info.SetLabel(text)


class ExportWindow(wx.Dialog):
    def __init__(self, parent, prefs=None):
        wx.Dialog.__init__(self, parent, -1, "Export Samples", size=PSConfig.EXPORT_WIN_SIZE)
        self.path = PSConfig.HOME_PATH
        self.bg = imgs.export_win_bg.GetBitmap()

        # Y positions
        if PSConfig.PLATFORM == 'linux2':
            self.section_x_offset = 5
        else:
            self.section_x_offset = 0
        outputFolder = 14
        exportRange = 85
        fileSpecs = 210 + self.section_x_offset
        margin_x = 14

        # Output folder
        label = wx.StaticText(self, -1, "Output Folder", (margin_x, outputFolder))
        label.SetForegroundColour("#d8ff00")
        btn = PSButtons.PSRectangleButton(self, (margin_x + 5, outputFolder + 23), (65, 23), "Choose...")
        self.Bind(PSButtons.EVT_BTN_CLICKED, self._dirDialog, btn)
        self.pathText = wx.StaticText(self, -1, PSUtils.shortenText(self.path, 40), (100, outputFolder + 25))
        self.pathText.SetForegroundColour("#f0f4d7")

        # Midi notes
        label = wx.StaticText(self, -1, "Export Range (Midi Notes)", (margin_x, exportRange))
        label.SetForegroundColour("#d8ff00")
        # min
        self.minText = wx.StaticText(self, -1, "From : %s(%d)" % (PSConfig.MIDI_NOTES_NAMES[21], 21),
                                     (margin_x + 5, exportRange + 25))
        self.minText.SetForegroundColour("#f0f4d7")
        self.midiMin = wx.Slider(self, -1, 21, 0, 127, pos=(margin_x + 5, exportRange + 50), size=(127, -1))
        # max
        self.maxText = wx.StaticText(self, -1, "To : %s(%d)" % (PSConfig.MIDI_NOTES_NAMES[106], 106),
                                     (margin_x + 160, exportRange + 25))
        self.maxText.SetForegroundColour("#f0f4d7")
        self.midiMax = wx.Slider(self, -1, 106, 0, 127, pos=(margin_x + 160, exportRange + 50), size=(127, -1))

        # Velocity steps
        label = wx.StaticText(self, -1, "Velocity Steps :", (margin_x + 5, exportRange + 80))
        label.SetForegroundColour("#f0f4d7")
        self.velSteps = wx.TextCtrl(self, pos=(margin_x + 103, exportRange + 80), size=(30, -1), style=wx.NO_BORDER)
        self.velSteps.SetValue('3')
        self.velSteps.SetBackgroundColour("#3d3d3d")
        self.velSteps.SetForegroundColour("#f0f4d7")

        # Note dur
        label = wx.StaticText(self, -1, "Note Duration :", (margin_x + 165, exportRange + 80))
        label.SetForegroundColour("#f0f4d7")
        self.noteDur = wx.TextCtrl(self, pos=(margin_x + 262, exportRange + 80), size=(30, -1), style=wx.NO_BORDER)
        self.noteDur.SetValue('5')
        self.noteDur.SetBackgroundColour("#3d3d3d")
        self.noteDur.SetForegroundColour("#f0f4d7")
        secs = wx.StaticText(self, -1, "secs.", (315, exportRange + 80))
        secs.SetForegroundColour("#f0f4d7")

        # File specs
        label = wx.StaticText(self, -1, "File Specifications", (margin_x, fileSpecs))
        label.SetForegroundColour("#d8ff00")
        # file format
        formats = ['.wav', '.aiff', '.au', '.raw', '.sd2', '.flac', '.caf', '.ogg']
        label = wx.StaticText(self, -1, "Format :", (margin_x + 5, fileSpecs + 29))
        label.SetForegroundColour("#f0f4d7")
        self.fileFormat = wx.Choice(self, -1, (margin_x + 60, fileSpecs + 27), PSConfig.CHOICE_SIZE, choices=formats)

        # bit depth
        bits = ['16 bits int', '24 bits int', '32 bits int', '32 bits float', '64 bits float',
                'U-Law encoded', 'A-Law encoded']
        label = wx.StaticText(self, -1, "Bit Depth :", (margin_x + 160, fileSpecs + 29))
        label.SetForegroundColour("#f0f4d7")
        self.bitDepth = wx.Choice(self, -1, (margin_x + 230, fileSpecs + 27), PSConfig.CHOICE_SIZE, choices=bits)

        # File length
        label = wx.StaticText(self, -1, "Length :", (margin_x + 5, fileSpecs + 59))
        label.SetForegroundColour("#f0f4d7")
        self.fileLength = wx.TextCtrl(self, pos=(margin_x + 60, fileSpecs + 60), size=(30, -1), style=wx.NO_BORDER)
        self.fileLength.SetBackgroundColour("#3d3d3d")
        self.fileLength.SetForegroundColour("#f0f4d7")
        self.fileLength.SetValue('5')
        secs = wx.StaticText(self, -1, "secs.", (margin_x + 100, fileSpecs + 59))
        secs.SetForegroundColour("#f0f4d7")

        sizex = 65
        sizey = 23
        x1 = PSConfig.EXPORT_WIN_SIZE[0] / 2 - sizex - margin_x / 2
        y = 310 + self.section_x_offset*2
        btn = PSButtons.PSRectangleButton(self, (x1, y), (sizex, sizey), "OK", id=wx.ID_OK)
        self.Bind(PSButtons.EVT_BTN_CLICKED, self._endModal, btn)
        btn = PSButtons.PSRectangleButton(self, (x1+sizex+margin_x/2, y), (sizex, sizey), "CANCEL", id=wx.ID_CANCEL)
        self.Bind(PSButtons.EVT_BTN_CLICKED, self._endModal, btn)

        if prefs is not None:
            self._updateFields(prefs)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SLIDER, self.OnChangeMin, self.midiMin)
        self.Bind(wx.EVT_SLIDER, self.OnChangeMax, self.midiMax)

    def OnPaint(self, evt):
        w, h = self.GetSize()
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bg, 0, 0)
        color = PSUtils.getTransparentColour(56, "#4f4f4f")[0]
        dc.SetBrush(wx.Brush(color))
        dc.SetPen(wx.Pen(color, 1))
        # gray backgrounds
        dc.DrawRectangle(7, 7, w - 14, 63)
        dc.DrawRectangle(7, 80, w - 14, 110+self.section_x_offset)
        dc.DrawRectangle(7, 200+self.section_x_offset, w - 14, 95+self.section_x_offset)

    def OnChangeMin(self, evt):
        i = self.midiMin.GetValue()
        text = "From : %s(%d)" % (PSConfig.MIDI_NOTES_NAMES[i], i)
        self.minText.SetLabel(text)

    def OnChangeMax(self, evt):
        i = self.midiMax.GetValue()
        text = "To : %s(%d)" % (PSConfig.MIDI_NOTES_NAMES[i], i)
        self.maxText.SetLabel(text)

    def _endModal(self, evt):
        self.EndModal(evt.GetId())

    def _dirDialog(self, evt):
        dlg = wx.DirDialog(self, "Choose a directory", defaultPath=self.path)
        if dlg.ShowModal() == wx.ID_OK:
            self.path = dlg.GetPath()
            self.pathText.SetLabel(PSUtils.shortenText(self.path, 44))
        dlg.Destroy()

    def _updateFields(self, prefs):
        self.path = prefs['path']
        self.pathText.SetLabel(self.path)

        # Display min midi note
        val = prefs['midimin']
        self.midiMin.SetValue(val)
        text = "From : %s(%d)" % (PSConfig.MIDI_NOTES_NAMES[val], val)
        self.minText.SetLabel(text)

        # Display max midi note
        val = prefs['midimax']
        self.midiMax.SetValue(val)
        text = "To : %s(%d)" % (PSConfig.MIDI_NOTES_NAMES[val], val)
        self.maxText.SetLabel(text)

        self.velSteps.SetValue(str(prefs['velsteps']))
        self.noteDur.SetValue(str(prefs['notedur']))
        self.fileFormat.SetSelection(prefs['format'])
        self.bitDepth.SetSelection(prefs['bitdepth'])
        self.fileLength.SetValue(str(prefs['filelength']))

    def getValues(self):
        return {'path': self.path,
                'midimin': self.midiMin.GetValue(),
                'midimax': self.midiMax.GetValue(),
                'velsteps': int(self.velSteps.GetValue()),
                'notedur': float(self.noteDur.GetValue()),
                'format': self.fileFormat.GetSelection(),
                'bitdepth': self.bitDepth.GetSelection(),
                'filelength': float(self.fileLength.GetValue())}

    def getWhiteListItems(self):
        return [self.velSteps.GetId(), self.noteDur.GetId(), self.fileLength.GetId()]


class PSExceptionWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Script Errors Log", (100, 100), (550, 300))
        x, y = self.GetSize()
        self.panel = wx.Panel(self, -1, (0, 0), (x,y))
        self.text = wx.TextCtrl(self.panel, -1, "", (0, 0), (x, y-6), style=wx.TE_MULTILINE | wx.TE_READONLY)

        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        self.Bind(wx.EVT_SIZE, self.OnSizeChange)

    def OnQuit(self, evt):
        self.Show(False)

    def OnSizeChange(self, evt):
        w, h = self.GetSize()
        self.panel.SetSize((w, h - 23))
        self.text.SetSize((w, h - 23))
        self.text.SetVirtualSize((w, h - 23))

    def toggle(self, evt):
        if self.IsShown():
            self.Show(False)
        else:
            self.Show(True)

    def printException(self, script_name, text):
        """
        Use this method to print custom text/error directly in the exception window.
        """
        self.text.AppendText(self._dateStamp(script_name))
        self.text.AppendText(text)
        self.Show(True)

    def newException(self, title, text):
        """
        Use this method to print a python exception in the exception window.
        All it does is remove the extra lines from the python traceback before adding it to the text control.
        """
        text = self._removeExtraLines(text)
        self.text.AppendText(self._dateStamp(title))
        self.text.AppendText(text)
        self.Show(True)

    def _dateStamp(self, name):
        return "\n---------- Error in '%s' - %s ----------\n" % (name, time.strftime("%H:%M:%S"))

    def _removeExtraLines(self, text):
        """
        Supprime la partie de l'exception qui refere au script de PyoSynth.
        """
        parts = text.split('\n', 3)
        return parts[0] + '\n' + parts[3]

    def getWhiteListItems(self):
        return [self.GetId(), self.panel.GetId(), self.text.GetId()]


class PSTerminal(wx.Frame):
    def __init__(self, parent, namespace):
        self._script_namespace = namespace
        wx.Frame.__init__(self, parent, -1, "Python Interpreter", (150, 150), (550, 300))
        self.SetSizeHints(minW=400, minH=100)
        x, y = self.GetSize()
        self._panel = wx.Panel(self, -1, (0,0), (x, y))

        # stdout text control
        self._stdout_ctrl = wx.TextCtrl(self._panel, -1, "", (-2, -2), (x+4, y+1), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self._stdout_ctrl.SetSizeHints(minW=400, minH=100)
        self._stdout_ctrl.SetBackgroundColour((45,46,38))
        self._stdout_ctrl.SetForegroundColour((249,249,243))

        # stdin text control
        self._stdin_ctrl = wx.TextCtrl(self._panel, -1, "", (-2, y-42), (x+4, -1), style=wx.TE_PROCESS_ENTER)

        self._stdout_ctrl.SetFont(wx.Font(**PSConfig.FONTS['terminal']))

        self._history = []
        self._histo_ind = -1
        self._max_history = 20
        self._current_line = ""

        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        self.Bind(wx.EVT_SIZE, self.OnSizeChange)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)
        self._stdin_ctrl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

    def OnQuit(self, evt):
        self.Show(False)

    def OnSizeChange(self, evt):
        w, h = self.GetSize()
        self._panel.SetSize((w, h))
        self._stdout_ctrl.SetSize((w + 4, h-37))
        self._stdin_ctrl.SetSize((w + 4, -1))
        self._stdin_ctrl.SetPosition((-2, h - 42))

    def OnEnter(self, evt):
        line = self._stdin_ctrl.GetValue()
        print ">>> %s" % line
        self._execLine(line)
        self._stdin_ctrl.Clear()
        self.Refresh()

    def OnKeyDown(self, evt):
        key = evt.GetKeyCode()
        if key == 317:
            self._browseHistory(1)
        elif key == 315:
            self._browseHistory(-1)
        else:
            evt.Skip()

    def _browseHistory(self, val):
        if val == -1:
            if self._histo_ind == -1:
                self._current_line = self._stdin_ctrl.GetValue()
                self._histo_ind = len(self._history)-1
            elif self._histo_ind == 0:
                pass
            else:
                self._histo_ind -= 1
        elif val == 1:
            if self._histo_ind == -1:
                pass
            elif self._histo_ind == len(self._history)-1:
                self._histo_ind = -1
                self._stdin_ctrl.SetValue(self._current_line)
            else:
                self._histo_ind += 1

        if self._histo_ind != -1:
            self._stdin_ctrl.SetValue(self._history[self._histo_ind])
        self._stdin_ctrl.SetInsertionPointEnd()

    def _addLineToHistory(self, line):
        self._history.append(line)
        if len(self._history) > self._max_history:
            self._history.pop(0)

    def _execLine(self, line):
        if "exit()" in line:
            dlg = wx.MessageDialog(self, "This will close PyoSynth, is this what you want?", "exit()", style=wx.YES_NO|wx.ICON_EXCLAMATION)
            dlg.Center()
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_NO:
                return
        try:
            if "=" in line:
                exec line in self._script_namespace
            else:
                print eval(line, self._script_namespace)
        except Exception, e:
            print e
        finally:
            self._addLineToHistory(line)
            self._histo_ind = -1

    def toggle(self, evt):
        if self.IsShown():
            self.Show(False)
        else:
            self.Show(True)
            self._stdin_ctrl.SetFocus()

    def write(self, text):
        """
        This method is called by stdout and needs to have this exact signature.
        """
        self._stdout_ctrl.AppendText(text)
        self.Refresh() # might be needed for windows

    def getWhiteListItems(self):
        return [self._stdin_ctrl.GetId(), self._stdout_ctrl.GetId()]


class CrashDialog(wx.Dialog):
    def __init__(self, message, caption):
        wx.Dialog.__init__(self, None, -1, '', size=(422, 300))

        bmp = imgs.icon_64x64.GetBitmap()
        icon = wx.StaticBitmap(self, -1, bmp, pos=(18, 23))

        caption_text = wx.StaticText(self, -1, caption, pos=(100, 20))
        font = wx.SystemSettings.GetFont(0)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        font.SetPointSize(13)
        caption_text.SetFont(font)

        y = caption_text.GetSize()[1] + caption_text.GetPosition()[1]
        message_text = wx.StaticText(self, -1, message, pos=(100, y + 10))
        message_text.Wrap(350)
        font.SetWeight(wx.FONTWEIGHT_NORMAL)
        font.SetPointSize(11)
        message_text.SetFont(font)

        y = message_text.GetSize()[1] + message_text.GetPosition()[1]
        comment_caption = wx.StaticText(self, -1, 'Commentaires :', pos=(100, y + 20))
        comment_caption.SetFont(font)

        y = comment_caption.GetSize()[1] + comment_caption.GetPosition()[1]
        self._comments = wx.TextCtrl(self, -1, '', pos=(100, y + 5), size=(300, 100), style=wx.TE_MULTILINE)

        w, h = self.GetSize()
        h = self._comments.GetSize()[1] + self._comments.GetPosition()[1] + 80
        self.SetSize((w, h))
        button = wx.Button(self, wx.ID_OK, pos=(w - 90, h - 60))

    def GetComments(self):
        return self._comments.GetValue().encode('utf_8')


class VirtualKeyboard:
    def __init__(self, style, mono=False, mono_type=0):
        self.map_style = style

        self.octave = 5
        self.min_octave = 0
        self.max_octave = 11 - PSConfig.mapping_styles[style][0]
        self.amp = .7  # value of the amplitude
        self.sustain = False
        self.setMonoMode(mono, mono_type)

        self.callback = None  # to be defined by setCallback
        self.poly = -1  # to be defined by setPoly with all the variables below
        self.keys = []  # stores which keys are playing
        self.notes = []  # stores what frequencies are played
        self.keys_pressed = []  # stores the keys that are currently pressed
        self.trigNoteOn = []  # streams for the note on event
        self.trigNoteOff = []  # streams for the note off event

        self.mapping = self.buildMapping()

    def __getitem__(self, i):
        if i == 'noteon':
            return self.trigNoteOn
        if i == 'noteoff':
            return self.trigNoteOff

    def OnKeyDown(self, evt):
        key = evt.GetKeyCode()

        # handle generic cases here
        if key > 313 and key < 318:
            self.OnSpecialKey(key)
            return
        if key == 32:
            if not self.mono_mode:
                self.setSustainOn()
            return
        if key in self.keys_pressed:
            return
        if key not in self.mapping:
            return

        # handle the note behavior here
        if self.mono_mode:
            self._onNoteOnMono(key)
        else:
            self._onNoteOn(key)

    def OnKeyUp(self, evt):
        key = evt.GetKeyCode()

        if key == 32:
            if not self.mono_mode:
                self.setSustainOff()
            return
        if key not in self.keys_pressed:
            return

        if self.mono_mode:
            self._onNoteOffMono(key)
        else:
            self._onNoteOff(key)

    def OnSpecialKey(self, key):
        if key == 314:
            self.lowerOctave()
        elif key == 316:
            self.raiseOctave()
        elif key == 315:
            self.raiseAmp()
        elif key == 317:
            self.lowerAmp()

    def _onNoteOn(self, key):
        try:
            # essai de trouver une voix de libre
            index = self.keys.index(0)
        except ValueError:
            # si aucune voix de libre, on quitte la fonction
            return
        else:
            self.keys_pressed[index] = key
            self.keys[index] = key
            self.notes[index] = self.mapping[key]
            self.callback(self.notes[index], self.amp, index)
            self.trigNoteOn[index].play()

    def _onNoteOff(self, key):
        index = self.keys_pressed.index(key)
        self.keys_pressed[index] = 0
        if not self.sustain:
            self.trigNoteOff[index].play()

    def _onNoteOnMono(self, key):
        if len(self.keys_pressed) < self.poly:
            self.keys_pressed.append(key)
            if self.mono_type == 0: # recent mode
                self.notes = self.mapping[key]
                self.callback(self.notes, self.amp)
            elif self.mono_type == 1: # low priority
                self._sortKeysWith()
                new_note = self.mapping[self.keys_pressed[0]]
                if self.notes != new_note:
                    self.notes = new_note
                    self.callback(self.notes, self.amp)
            elif self.mono_type == 2: # high priority
                self._sortKeysWith(True)
                new_note = self.mapping[self.keys_pressed[0]]
                if self.notes != new_note:
                    self.notes = new_note
                    self.callback(self.notes, self.amp)
        if len(self.keys_pressed) == 1:
            self.trigNoteOn.play()

    def _onNoteOffMono(self, key):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
            if len(self.keys_pressed) == 0:
                self.notes = 0
                self.trigNoteOff.play()
                self.callback(self.notes, self.amp) # remove this call to leave last note instead of resetting to 0Hz
                return
            if self.mono_type == 0: # recent mode
                new_note = self.mapping[self.keys_pressed[-1]]
            elif self.mono_type in (1,2): # low or high priority
                new_note = self.mapping[self.keys_pressed[0]]
            if self.notes != new_note:
                self.notes = new_note
                self.callback(self.notes, self.amp)

    def _sortKeysWith(self, reverse=False):
        """
        Sorts self.keys list according to the values in self.mapping dictionary.
        If reverse is True, values will be sorted from biggest to smallest.
        """
        len_keys = len(self.keys_pressed)
        if len_keys <= 1: # if only one note is pressed, nothing to sort
            return
        temp = 0
        if not reverse:
            for i in range(len_keys - 1):
                small_ind = i
                for j in range(i + 1, len_keys):
                    if self.mapping[self.keys_pressed[j]] < self.mapping[self.keys_pressed[small_ind]]:
                        small_ind = j
                if small_ind != i:
                    temp = self.keys_pressed[i]
                    self.keys_pressed[i] = self.keys_pressed[small_ind]
                    self.keys_pressed[small_ind] = temp
        else:
            for i in range(len_keys - 1):
                big_ind = i
                for j in range(i + 1, len_keys):
                    if self.mapping[self.keys_pressed[j]] > self.mapping[self.keys_pressed[big_ind]]:
                        big_ind = j
                if big_ind != i:
                    temp = self.keys_pressed[i]
                    self.keys_pressed[i] = self.keys_pressed[big_ind]
                    self.keys_pressed[big_ind] = temp

    def setPoly(self, value):
        """
        Sets how many polyphony voices will be available.
        Called when setting the virtual keyboard by the MidiKeys class.
        """
        self.poly = value
        if self.mono_mode:
            self.keys_pressed = [] # stores what keys are pressed. (by key code)
            self.notes = 0 # stores the note in hz that is playing
            self.trigNoteOn = Trig().stop()
            self.trigNoteOff = Trig().stop()
        else:
            self.keys = [0] * self.poly  # stores what keys are used. (by key code)
            self.notes = [0] * self.poly  # stores the notes in hz that are currently playing
            self.keys_pressed = [0] * self.poly # stores what keys are currently pressed, sustain or not
            self.trigNoteOn = [Trig().stop() for i in range(self.poly)]
            self.trigNoteOff = [Trig().stop() for i in range(self.poly)]

    def setCallback(self, func):
        self.callback = func

    def freeVoice(self, i=0):
        # called by MidiKeys object when the envelope has finished playing
        self.keys[i] = 0

    def setSustainOn(self):
        if not self.sustain: # prevents the function to spam because the key is held down
            self.sustain = True

    def setSustainOff(self):
        self.sustain = False

        for index, key in enumerate(self.keys_pressed):
            if key == 0 and self.keys[index] != 0:
                self.trigNoteOff[index].play()

    def setMonoMode(self, state=False, type=0):
        """
        Sets the mono mode to on or off. Allows to set the type of mono mode.

        state : True or False, is mono mode on or off.
        type : 0, 1 or 2, recent mode, low or high note priority, respectively.
        """
        self.mono_mode = state
        if state:
            assert type in (0, 1, 2), "VirtualKeyboard mono mode type can be either 0, 1 or 2."
            self.mono_type = type

    def setMonoType(self, type):
        assert type in (0, 1, 2), "VirtualKeyboard mono mode type can be either 0, 1 or 2."
        self.mono_type = type

    def buildMapping(self):
        dict = {}
        note = self.octave * 12
        for i in range(1, len(PSConfig.mapping_styles[self.map_style])):
            dict[PSConfig.mapping_styles[self.map_style][i]] = midiToHz(note)
            note += 1
        return dict

    def lowerOctave(self):
        if self.octave > self.min_octave:
            self.octave -= 1
        self.mapping = self.buildMapping()

    def raiseOctave(self):
        if self.octave < self.max_octave:
            self.octave += 1
        self.mapping = self.buildMapping()

    def lowerAmp(self):
        self.amp -= .1
        if self.amp <= 0.:
            self.amp = 0.

    def raiseAmp(self):
        self.amp += .1
        if self.amp >= 1.:
            self.amp = 1.

    def setMappingStyle(self, style):
        self.map_style = style
        self.max_octave = 11 - PSConfig.mapping_styles[self.map_style][0]
        self.mapping = self.buildMapping()
