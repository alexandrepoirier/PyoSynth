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

import wx, time, math
import PSConfig, PSButtons, PSUtils
from PSAudio import Click
from controlsPyImg import *
from threading import Timer

if PSConfig.USE_PYO64:
    from pyo64 import Midictl, Change, TrigFunc, CtlScan
else:
    from pyo import Midictl, Change, TrigFunc, CtlScan


class PSTextCtrl(wx.Control):
    def __init__(self, parent, pos, text):
        wx.Control.__init__(self, parent, -1, pos, (1,1), style=wx.NO_BORDER)

        #Fade in/out properties
        self.IS_SHOWN = True
        self._alpha = 255
        self._currentAlpha = 255
        self._delta = 17
        self._fadeTime = 10
        self._timer = wx.Timer(self, -1)
        
        #bitmaps
        self.left_bmp = txt_ctrl_left_side.GetBitmap()
        self.right_bmp = txt_ctrl_right_side.GetBitmap()
        self.middle_bmp = txt_ctrl_middle.GetBitmap()

        self._font = wx.Font(**PSConfig.FONTS['light']['norm'])
        
        #on coupe a 20 caracteres pour etre sure de na pas depasser
        self._maxChar = 20
        self._text = text[0:self._maxChar]
        self._textWidth = self.getTextWidth(self._text)
        self._lastTextWidth = -1
        
        self._margin = 4
        self._width = self._textWidth + self.left_bmp.GetSize()[0] + self.right_bmp.GetSize()[0] + (self._margin*2)
        self._height = self.middle_bmp.GetSize()[1]
        
        width = self._width + self._margin*2
        self.SetSize( (width, self._height) )

        if PSConfig.PLATFORM == 'darwin':
            self.Bind(wx.EVT_PAINT, self.OnPaintMac)
        elif PSConfig.PLATFORM == 'linux2':
            self.Bind(wx.EVT_PAINT, self.OnPaintLinux)

        self.Bind(wx.EVT_TIMER, self.changeAlpha)

    def OnPaintMac(self, evt):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.left_bmp, 0, 0)

        offset = self.left_bmp.GetSize()[0]
        loops = self._textWidth + self._margin * 2
        for i in range(loops):
            dc.DrawBitmap(self.middle_bmp, offset + i, 0)

        dc.DrawBitmap(self.right_bmp, offset + loops, 0)

        dc.SetFont(self._font)
        dc.SetTextForeground("#FFFFFF")
        dc.DrawText(self._text, offset + self._margin, self._height / 5)

    def OnPaintLinux(self, evt):
        dc = wx.PaintDC(self)
        posx, posy = self.GetPositionTuple()
        w, h = self.GetSizeTuple()
        bmp = self.Parent.GetRegion(posx, posy, w, h)
        dc.DrawBitmap(bmp, 0, 0)
        dc.DrawBitmap(self.left_bmp, 0, 0)
        
        offset = self.left_bmp.GetSize()[0]
        loops = self._textWidth+self._margin*2
        for i in range(loops):
            dc.DrawBitmap(self.middle_bmp, offset+i, 0)
            
        dc.DrawBitmap(self.right_bmp, offset+loops, 0)
        
        dc.SetFont(self._font)
        dc.SetTextForeground("#FFFFFF")
        dc.DrawText(self._text, offset+self._margin, self._height/5)
        
    def ShowWindow(self):
        self.IS_SHOWN = True
        self.Show(True)
        self._timer.Start(self._fadeTime)
        
    def HideWindow(self):
        self.IS_SHOWN = False
        self._timer.Start(self._fadeTime)
        
    def changeAlpha(self, evt):
        if self.IS_SHOWN:
            if self._currentAlpha < self._alpha:
                self._currentAlpha += self._delta
                wx.CallAfter(self.SetTransparent, self._currentAlpha)
            else:
                self._timer.Stop()
        else:
            if self._currentAlpha > 0:
                self._currentAlpha -= self._delta
                wx.CallAfter(self.SetTransparent, self._currentAlpha)
            else:
                wx.CallAfter(self.Show, False)
                self._timer.Stop()
        
    def getTextWidth(self, string):
        dc = wx.ClientDC(self)
        dc.SetFont(self._font)
        return dc.GetTextExtent(string)[0]
        
    def SetText(self, string):
        self.HideWindow()
        wx.CallLater(150, self.DoSetText, string)
        wx.CallLater(210, self.ShowWindow)
        
    def DoSetText(self, string):
        #mise a jour des variables
        self._lastTextWidth = self._textWidth
        self._text = string[0:self._maxChar]
        self._textWidth = self.getTextWidth(self._text)
        
        #mise a jour de la position
        x, y = self.GetPosition()
        x = x - (self._textWidth - self._lastTextWidth)
        self.SetPosition( (x, y) )
        
        #mise a jour de la taille
        self._width = self._textWidth + self.left_bmp.GetSize()[0] + self.right_bmp.GetSize()[0] + (self._margin*2)
        width = self._width + self._margin*2
        self.SetSize( (width, self._height) )
        
    def GetWidth(self):
        return self._width
        
    def GetHeight(self):
        return self._height
        
class PSScriptTextCtrl(wx.Control):
    def __init__(self, parent, pos, text):
        wx.Control.__init__(self, parent, -1, pos, (1,1), style=wx.NO_BORDER)
        
        #Fade in/out properties
        self.IS_SHOWN = True
        self._alpha = 255
        self._currentAlpha = 255
        self._delta = 17
        self._fadeTime = 10
        self._timer = wx.Timer(self, -1)
        
        #bitmaps
        self.left_bmp = txt_ctrl_left_side.GetBitmap()
        self.middle_bmp = txt_ctrl_middle.GetBitmap()

        self._font = wx.Font(**PSConfig.FONTS['light']['small'])
        
        #on coupe a 40 caracteres pour etre sure de na pas depasser
        self._maxChar = 40
        self._text = text[0:self._maxChar]
        self._textWidth = self.getTextWidth(self._text)
        self._margin = 4
        self._width = lambda: self._textWidth + self.left_bmp.GetSize()[0] + (self._margin*2)
        self._height = self.middle_bmp.GetSize()[1]
        self._adjustSize()
        
        if PSConfig.PLATFORM == 'darwin':
            self.Bind(wx.EVT_PAINT, self.OnPaintMac)
        elif PSConfig.PLATFORM == 'linux2':
            self.Bind(wx.EVT_PAINT, self.OnPaintLinux)

        self.Bind(wx.EVT_TIMER, self.changeAlpha)
        
    def OnPaintMac(self, evt):
        dc = wx.PaintDC(self)
        self.OnPaintGeneric(dc)

    def OnPaintLinux(self, evt):
        dc = wx.PaintDC(self)
        posx, posy = self.GetPositionTuple()
        w, h = self.GetSizeTuple()
        bmp = self.Parent.GetRegion(posx, posy, w, h)
        dc.DrawBitmap(bmp, 0, 0)

        self.OnPaintGeneric(dc)

    def OnPaintGeneric(self, dc):
        dc.DrawBitmap(self.left_bmp, 0, 0)

        offset = self.left_bmp.GetSize()[0]
        loops = self._textWidth + self._margin * 2
        for i in range(loops):
            dc.DrawBitmap(self.middle_bmp, offset + i, 0)

        dc.SetFont(self._font)
        dc.SetTextForeground("#FFFFFF")

        if PSConfig.PLATFORM == 'darwin':
            x = offset + self._margin + 2
            y = self._height / 5
        elif PSConfig.PLATFORM == 'linux2':
            x = offset + self._margin
            y = 4

        dc.DrawText(self._text, x, y)
        
    def ShowWindow(self):
        self.IS_SHOWN = True
        self.Show(True)
        self._timer.Start(self._fadeTime)
        
    def HideWindow(self):
        self.IS_SHOWN = False
        self._timer.Start(self._fadeTime)
        
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
        
    def getTextWidth(self, string):
        dc = wx.ClientDC(self)
        dc.SetFont(self._font)
        return dc.GetTextExtent(string)[0]
        
    def SetText(self, string):
        self.HideWindow()
        wx.CallLater(180, self.DoSetText, string)
        wx.CallLater(250, self.ShowWindow)
        
    def DoSetText(self, string):
        self._text = string[0:self._maxChar]
        self._textWidth = self.getTextWidth(self._text)
        self._adjustSize()

    def _adjustSize(self):
        self._width = self._textWidth + self.left_bmp.GetSize()[0] + (self._margin * 2)
        if PSConfig.PLATFORM == 'darwin':
            self.SetSize( (self._width + self._margin*2, self._height) )
        elif PSConfig.PLATFORM == 'linux2':
            self.SetSize( (self._width, self._height) )
        
    def GetWidth(self):
        return self.GetSize()[0]
        
    def GetHeight(self):
        return self.GetSize()[1]

class PSRecordTextCtrl(wx.Control):
    def __init__(self, parent, pos, text):
        wx.Control.__init__(self, parent, -1, pos, (130,26), style=wx.NO_BORDER)
        
        #bitmaps
        self.left_bmp = rec_txt_left_end.GetBitmap()
        self.middle_bmp = rec_txt_middle.GetBitmap()
        
        self._text = text
        self._time = "00:00"
        self._margin = 2
        self._RECORDING = False
        
        self._font = wx.Font(**PSConfig.FONTS['light']['norm'])

        if PSConfig.PLATFORM == 'darwin':
            self.Bind(wx.EVT_PAINT, self.OnPaintMac)
        elif PSConfig.PLATFORM == 'linux2':
            self.Bind(wx.EVT_PAINT, self.OnPaintLinux)
        
    def OnPaintMac(self, evt):
        dc = wx.PaintDC(self)
        dc.SetFont(self._font)

        dc.DrawBitmap(self.left_bmp, 0, 0)
        
        offset = self.left_bmp.GetSize()[0]
        loops = self.GetSize()[0]-offset
        for i in range(loops):
            dc.DrawBitmap(self.middle_bmp, offset+i, 0)
        
        if self._RECORDING:
            dc.SetTextForeground("#c30b0b")
        else:
            dc.SetTextForeground("#FFFFFF")
        dc.DrawText(self._text+" - "+self._time, offset+self._margin, 6)

    def OnPaintLinux(self, evt):
        dc = wx.PaintDC(self)
        dc.SetFont(self._font)

        posx, posy = self.GetPositionTuple()
        w, h = self.GetSizeTuple()
        region = self.Parent.GetRegion(posx, posy, w, h)
        dc.DrawBitmap(region, 0, 0)

        dc.DrawBitmap(self.left_bmp, 0, 0)

        offset = self.left_bmp.GetSize()[0]
        loops = self.GetSize()[0] - offset
        for i in range(loops):
            dc.DrawBitmap(self.middle_bmp, offset + i, 0)

        if self._RECORDING:
            dc.SetTextForeground("#c30b0b")
        else:
            dc.SetTextForeground("#FFFFFF")
        dc.DrawText(self._text + " - " + self._time, offset + self._margin, 6)
        
    def SetText(self, string):
        self._text = string
        self.Refresh()
        
    def SetTime(self, string):
        self._time = string
        self.Refresh()
        
    def SetRecState(self, state):
        self._RECORDING = state
        self.Refresh()

myEVT_KNOB_CLICKED = wx.NewEventType()
EVT_KNOB_CLICKED = wx.PyEventBinder(myEVT_KNOB_CLICKED, 1)

myEVT_KNOB_DRAG = wx.NewEventType()
EVT_KNOB_DRAG = wx.PyEventBinder(myEVT_KNOB_DRAG, 1)

myEVT_KNOB_UP = wx.NewEventType()
EVT_KNOB_UP = wx.PyEventBinder(myEVT_KNOB_UP, 1)

myEVT_KNOB_ENTER = wx.NewEventType()
EVT_KNOB_ENTER = wx.PyEventBinder(myEVT_KNOB_ENTER, 1)

myEVT_KNOB_LEAVE = wx.NewEventType()
EVT_KNOB_LEAVE = wx.PyEventBinder(myEVT_KNOB_LEAVE, 1)

myEVT_VOL_CHANGED = wx.NewEventType()
EVT_VOL_CHANGED = wx.PyEventBinder(myEVT_VOL_CHANGED, 1)

class VolumeSliderEvent(wx.PyCommandEvent):
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)
        self._clickPos = None
        
    def GetMousePosition(self):
        return self._clickPos

class VolumeSliderKnob(wx.Control):
    def __init__(self, parent):
        wx.Control.__init__(self, parent, -1, (0,0), (14,14), style=wx.NO_BORDER)
        
        #state variables
        self._clicked = False
        self._moving = False
        
        #bitmap
        self.knob_bmp = vol_slider_ctrl_knob.GetBitmap()
        
        if PSConfig.PLATFORM == 'darwin':
            self.Bind(wx.EVT_PAINT, self.OnPaintMac)
        elif PSConfig.PLATFORM == 'linux2':
            self.Bind(wx.EVT_PAINT, self.OnPaintLinux)

        self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        self.Bind(wx.EVT_LEFT_UP, self.OnClickUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)
        
    def OnPaintMac(self, evt):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.knob_bmp,0,0)

    def OnPaintLinux(self, evt):
        dc = wx.PaintDC(self)

        posx, posy = self.GetPositionTuple()
        w, h = self.GetSizeTuple()
        bmp = self.Parent.GetRegion(posx, posy, w, h)
        dc.DrawBitmap(bmp, 0, 0)

        dc.DrawBitmap(self.knob_bmp,0,0)
        
    def OnClick(self, evt):
        self._clicked = True
        self.CaptureMouse()
        #Custom event business
        event = VolumeSliderEvent(myEVT_KNOB_CLICKED, self.GetId())
        event._clickPos = evt.GetPosition()
        self.GetEventHandler().ProcessEvent(event)
        
    def OnClickUp(self, evt):
        self._clicked = False
        self.ReleaseMouse()
        #Custom event business
        event = VolumeSliderEvent(myEVT_KNOB_UP, self.GetId())
        event._clickPos = evt.GetPosition()
        self.GetEventHandler().ProcessEvent(event)
        
    def OnMotion(self, evt):
        if self._clicked:
            #Custom event business
            event = VolumeSliderEvent(myEVT_KNOB_DRAG, self.GetId())
            event._clickPos = evt.GetPosition()
            self.GetEventHandler().ProcessEvent(event)
            
    def OnEnter(self, evt):
        #Custom event business
        evt = VolumeSliderEvent(myEVT_KNOB_ENTER, self.GetId())
        self.GetEventHandler().ProcessEvent(evt)
        
    def OnLeave(self, evt):
        #Custom event business
        evt = VolumeSliderEvent(myEVT_KNOB_LEAVE, self.GetId())
        self.GetEventHandler().ProcessEvent(evt)

class VolumeSlider(wx.Control):
    """
    class VolumeSLider
    
    attributes:
        parent : parent window, a wx.Window
        pos    : position on the screen relative to the parent
        length : length of the track. An integer greater than 50.
        value  : value of the volume at initialisation as a float between 0 and 1.
    """
    def __init__(self, parent, pos, length, value=.8):
        wx.Control.__init__(self, parent, -1, pos, (length+12,14), style=wx.NO_BORDER)
        self._minLength = 50
        self._min = 0
        self._max = 1
        self._length = length if length > self._minLength else self._minLength
        self._value = value if value >= self._min and value <= self._max else 0.5
        
        self._clickPos = None
        
        self._knob = VolumeSliderKnob(self)
        self._maxPosX = self._length-(self._knob.GetSize()[0]/2)
        self.setValue(self._value)

        # bitmaps
        self.left_bmp = vol_slider_ctrl_track_left_end.GetBitmap()
        self.right_bmp = vol_slider_ctrl_track_right_end.GetBitmap()
        self.track_bmp = vol_slider_ctrl_track.GetBitmap()

        if PSConfig.PLATFORM == 'darwin':
            self.Bind(wx.EVT_PAINT, self.OnPaintMac)
        elif PSConfig.PLATFORM == 'linux2':
            self.Bind(wx.EVT_PAINT, self.OnPaintLinux)
            self._buffer = wx.EmptyBitmap(self.GetSize()[0], self.GetSize()[1])

        self.Bind(EVT_KNOB_CLICKED, self.OnClick)
        self.Bind(EVT_KNOB_UP, self.OnClickUp)
        self.Bind(EVT_KNOB_DRAG, self.OnMotion)
        self.Bind(EVT_KNOB_ENTER, self.OnEnter)
        self.Bind(EVT_KNOB_LEAVE, self.OnLeave)
        
    def OnPaintMac(self, evt):
        dc = wx.PaintDC(self)
        self._drawTrackBitmap(dc)

    def OnPaintLinux(self, evt):
        dc = wx.BufferedPaintDC(self, self._buffer)

        posx, posy = self.GetPositionTuple()
        w, h = self.GetSizeTuple()
        bmp = self.Parent.GetRegion(posx, posy, w, h)
        dc.DrawBitmap(bmp, 0, 0)

        self._drawTrackBitmap(dc)

    def GetRegion(self, x, y, w, h):
        bmp = wx.EmptyBitmap(w, h)
        dc = wx.MemoryDC(bmp)

        # get region underneath widget
        posx, posy = self.GetPositionTuple()
        parent_region = self.Parent.GetRegion(posx + x, posy + y, w, h)
        dc.DrawBitmap(parent_region, 0, 0)

        img = self._buffer.ConvertToImage()
        region = img.GetSubImage(wx.Rect(x, y, w, h))
        dc.DrawBitmap(wx.BitmapFromImage(region), 0, 0)

        dc.SelectObject(wx.NullBitmap)
        dc.Destroy()

        return bmp
        
    def OnClick(self, evt):
        self._clickPos = evt.GetMousePosition()
        
    def OnClickUp(self, evt):
        self._clickPos = None
        
    def OnMotion(self, evt):
        x = self._knob.GetPosition()[0] + (evt.GetMousePosition()[0]-self._clickPos[0])
        if x<0:x=0
        elif x>self._maxPosX:x=self._maxPosX
        self._knob.SetPosition((x,0))
        self._updateValue()
        
    def OnEnter(self, evt):
        evt.Skip()
        
    def OnLeave(self, evt):
        evt.Skip()
        
    def _drawTrackBitmap(self, dc):
        w,h = self.GetSize()
        
        dc.DrawBitmap(self.left_bmp,0,3)
        for i in range(6,self._length+1):
            dc.DrawBitmap(self.track_bmp,i,3)
        dc.DrawBitmap(self.right_bmp,self._length+1,3)
        
    def _updateValue(self):
        self._value = self._knob.GetPosition()[0]/float(self._maxPosX)
        #Custom event business
        evt = VolumeSliderEvent(myEVT_VOL_CHANGED, self.GetId())
        self.GetEventHandler().ProcessEvent(evt)
        
    def setValue(self, value):
        if value>self._max:value=self._max
        elif value<self._min:value=self._min
        self._value = value
        self._knob.SetPosition((self._value*self._maxPosX,0))
        #Custom event business
        evt = VolumeSliderEvent(myEVT_VOL_CHANGED, self.GetId())
        self.GetEventHandler().ProcessEvent(evt)
        
    def getValue(self):
        return self._value

class VuMeter(wx.Panel):
    def __init__(self, parent, pos, numSliders=2):
        wx.Panel.__init__(self, parent, -1, pos=pos, size=(242,30), style=wx.NO_BORDER)
        
        self._update_count = 0
        self._refresh_skip = 2
        self._count_reset = self._refresh_skip * 10000
        
        self.halfOnBitmaps = []
        self._createAlphaMeterBitmaps() #fills the halfOnBitmaps list
        self.fullOnBitmap = vu_meter_on.GetBitmap()
        self.vu_meter_off = vu_meter_off.GetBitmap()

        #sets the height of the panel and creates the buffer
        self.setNumSliders(numSliders)
        
        if PSConfig.PLATFORM == 'darwin':
            self.Bind(wx.EVT_PAINT, self.OnPaintMac)
        elif PSConfig.PLATFORM == 'linux2':
            self.Bind(wx.EVT_PAINT, self.OnPaintLinux)

        self.Bind(wx.EVT_CLOSE, self.OnClose)   

    def _createAlphaMeterBitmaps(self):
        img = vu_meter_on.GetImage()
        for i in range(1, 20):
            alpha = i/20.
            self.halfOnBitmaps.append(img.AdjustChannels(1,1,1,alpha).ConvertToBitmap())
    
    def setNumSliders(self, numSliders):
        self.numSliders = numSliders
        self.amplitude = [0] * self.numSliders
        self.lastValue = [0] * self.numSliders
        
        if numSliders > 2:
            self.overlap = 6
        else:
            self.overlap = 4
        height = (16*self.numSliders) - (self.overlap*(self.numSliders-1))
        
        self.SetSize((242, height))
        self.SetMinSize((242, height))

    def setRms(self, *args):
        if args[0] < 0: 
            return
        if not args:
            self.amplitude = [0 for i in range(self.numSliders)]
        else:
            self.amplitude = args
        self._update_count += 1
        if (self._update_count%self._refresh_skip) == 0:
            wx.CallAfter(self.Refresh)
        if self._update_count == self._count_reset:
            self._update_count = 0

    def reset(self):
        self.amplitude = [0 for i in range(self.numSliders)]
        wx.CallAfter(self.Refresh)

    def OnPaintMac(self, evt):
        dc = wx.PaintDC(self)
        self._drawMeters(dc)

    def OnPaintLinux(self, evt):
        dc = wx.PaintDC(self)

        posx, posy = self.GetPositionTuple()
        w, h = self.GetSizeTuple()
        bmp = self.Parent.GetRegion(posx, posy, w, h)
        dc.DrawBitmap(bmp, 0, 0)

        self._drawMeters(dc)

    def _drawMeters(self, dc):
        w,h = self.GetSize()

        for i in range(self.numSliders):
            db = PSUtils.clipper(math.log10(self.amplitude[i] + 0.000001) * 0.2 + 1., 0., 1.)
            self.lastValue[i] = db
            width = int(db*w)
            indexHalfOn = width%20
            widthFullOn = width - indexHalfOn
            y = (i*16) - (self.overlap*i)
            
            dc.DrawBitmap(self.vu_meter_off, 0, y)
            
            dc.SetClippingRegion(0, y, widthFullOn, 16)
            dc.DrawBitmap(self.fullOnBitmap, 0, y)
            dc.DestroyClippingRegion()
            
            if indexHalfOn > 0:
                dc.SetClippingRegion(widthFullOn, y, 20, 16)
                dc.DrawBitmap(self.halfOnBitmaps[indexHalfOn-1], 0, y)
                dc.DestroyClippingRegion()
    
    def OnClose(self, evt):
        self.Destroy()

    def setRefreshSkip(self, value):
        self._refresh_skip = value
        self._count_reset = value * 10000

class ClipLight(wx.Panel):
    """
    class ClipLight(wx.Panel)

    parametres:
                parent : fenetre parent, wx.Window
                pos : position relative a la fenetre parent
                timeout : temps en secondes avant que le voyant s'eteigne
    """
    def __init__(self, parent, pos, timeout):
        wx.Panel.__init__(self, parent, -1, pos, (19,19), style=wx.NO_BORDER)

        self._timeout = timeout
        self._IS_ON = False
        self.off_bmp = clip_light_off.GetBitmap()
        self.on_bmp = clip_light_on.GetBitmap()
        self._timer = None

        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, evt):
        dc = wx.PaintDC(self)

        if self._IS_ON:
            dc.DrawBitmap(self.on_bmp,0,0)
        else:
            dc.DrawBitmap(self.off_bmp,0,0)

    def turnOn(self):
        self._IS_ON = True

        if self._timer is None:
            self._timer = Timer(self._timeout, self._turnOff)
            self._timer.start()
        else:
            self._timer.cancel()
            self._timer = Timer(self._timeout, self._turnOff)
            self._timer.start()

        wx.CallAfter(self.Refresh)

    def _turnOff(self):
        self._IS_ON = False
        self._timer = None
        wx.CallAfter(self.Refresh)

class TrackProgressionBar(wx.Control):
    def __init__(self, parent, pos):
        wx.Control.__init__(self, parent, -1, pos, (100,5), style=wx.NO_BORDER)
        
        self._value = 0
        self._max = -1
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
    def OnPaint(self, evt):
        w,h = self.GetSize()
        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen("#c30b0b", 1, wx.SOLID))
        dc.SetBrush(wx.Brush("#c30b0b"))
        
        dc.DrawLine(0,h-1,w,h-1)
        if self._value > 0 and self._max > 0:
            width = (self._value/self._max)*w
            dc.DrawRectangle(0,0,width,h)
        
    def setValue(self, value):
        if self._max == -1:
            raise ValueError, "You have to set the maximum before setting the value."
        self._value = float(value) if value <= self._max else float(self._max)
        wx.CallAfter(self.Refresh)
        
    def setMax(self, value):
        if value == 0:
            raise ValueError, "The maximum must be greater than 0."
        self._max = value

myEVT_VALUE_CHANGED = wx.NewEventType()
EVT_VALUE_CHANGED = wx.PyEventBinder(myEVT_VALUE_CHANGED, 1)

myEVT_TOGGLE_CONTROL = wx.NewEventType()
EVT_TOGGLE_CONTROL = wx.PyEventBinder(myEVT_TOGGLE_CONTROL, 1)

class RotaryKnobEvent(wx.PyCommandEvent):
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)
        self._ctlNumber = None
        self._IS_CONTROLLED = None

    def GetCtlNumber(self):

        return self._ctlNumber

    def GetIsControlled(self):
        return self._IS_CONTROLLED

class PSSmallRotaryKnob(wx.Control):
    def __init__(self, parent, pos, min, max, text, ratio=80, shift_mul=20, valprec=2, init=None):
        wx.Control.__init__(self, parent, -1, pos, (31,31), style=wx.NO_BORDER)
        self._min = min
        self._max = max
        self._range = float(max)-min
        self._value = init if init != None else self._range/2
        self._lastValue = self._value
        self._val_prec = valprec
        self._bmp_margin = 0
        self._textMargin = 0
        self._mouse_y_org = None
        self._mouse_ratio = float(ratio) # pixels/unit -> +Xpx = +1u.
        self._ratio_multiplicator = float(shift_mul)
        self.ctl_num = 74 # arbitrary init value
        self._callback = None
        
        #objs audio
        self._midictl = Midictl(self.ctl_num, self._min, self._max)
        self._change = Change(self._midictl).stop()
        self._trigFunc = TrigFunc(self._change, self._setValueFromCtl).stop()
        
        #variables trigo pour le dessin de l'indicateur
        self._minRad = 5*math.pi/4
        self._maxRad = 7*math.pi/4
        self._rangeRad = 2*math.pi-(self._maxRad-self._minRad)
        self._rayon = 8
        self._calcTheta = lambda x:self._minRad-(self._rangeRad*x)
        self._calcX = lambda x:(self._rayon*2)+(math.cos(self._calcTheta(x))*self._rayon)+self._bmpMargin
        self._calcY = lambda x:(self._rayon*2)-(math.sin(self._calcTheta(x))*self._rayon)
        
        #state variable
        self.MIDI_LEARN = False
        self.IS_CONTROLLED = False
        self.SHOW_VALUE = False
        self._clicked = False
        self._shift_down = False
        
        #bitmap
        self.knob_bmp = rotary_knob.GetBitmap()
        self.bmp_w, self.bmp_h = self.knob_bmp.GetSize()
        
        self._font = wx.Font(**PSConfig.FONTS['light']['xsmall'])
        self.setText(text)
        
        self._hideValueTimer = wx.Timer(self, -1)

        if PSConfig.PLATFORM == 'darwin':
            self.Bind(wx.EVT_PAINT, self.OnPaintMac)
        elif PSConfig.PLATFORM == 'linux2':
            self.Bind(wx.EVT_PAINT, self.OnPaintLinux)

        self.Bind(wx.EVT_TIMER, self._hideValue)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        
    def reinit(self):
        self._midictl = Midictl(self.ctl_num, self._min, self._max)
        self._change = Change(self._midictl).stop()
        self._trigFunc = TrigFunc(self._change, self._setValueFromCtl).stop()

    def OnPaintMac(self, evt):
        dc = wx.PaintDC(self)
        self.OnPaintGeneric(dc)

    def OnPaintLinux(self, evt):
        dc = wx.PaintDC(self)
        posx, posy = self.GetPositionTuple()
        w, h = self.GetSizeTuple()
        bmp = self.Parent.GetRegion(posx, posy, w, h)
        dc.DrawBitmap(bmp, 0, 0)

        self.OnPaintGeneric(dc)

    def OnPaintGeneric(self, dc):
        dc.SetFont(self._font)
        if self.IS_CONTROLLED or self.MIDI_LEARN:
            dc.SetTextForeground("#d8ff00")
        else:
            dc.SetTextForeground("#c7c7c7")
        dc.SetPen(wx.Pen("#c7c7c7",1))
        
        #bg and txt
        dc.DrawBitmap(self.knob_bmp,self._bmpMargin,0)
        if self.SHOW_VALUE:
            prec = "%."+str(self._val_prec)+"f"
            val_txt = prec % self._value
            x = (self.GetSize()[0]-dc.GetTextExtent(val_txt)[0])/2
            dc.DrawText(val_txt, x, self.bmp_h)
        elif self.MIDI_LEARN:
            ctl_txt = str(self.ctl_num)
            x = (self.GetSize()[0]-dc.GetTextExtent(ctl_txt)[0])/2
            dc.DrawText(ctl_txt, x, self.bmp_h)
        else:
            dc.DrawText(self._text, self._txtMargin, self.bmp_h)
        
        #draw indicator
        index = (self._value-self._min)/self._range
        x = self._calcX(index)
        y = self._calcY(index)
        dc.DrawLine(x, y, self._knob_center, self.bmp_h/2.)
        
    def OnMouseDown(self, evt):
        cmd = evt.CmdDown()
        if cmd:
            self._toggleMidiLearn()
        else:
            self._mouse_y_org = wx.GetMousePosition()[1]
            self.CaptureMouse()
            self._clicked = True
            self.SHOW_VALUE = True
            wx.CallAfter(self.Refresh)
        
    def OnMouseUp(self, evt):
        self._clicked = False
        self._mouse_y_org = None
        self._lastValue = self._value
        
        self._startTimer()
        
        #evite d'Avoir une erreur au dclick
        try:
            self.ReleaseMouse()
        except:
            pass
        wx.CallAfter(self.Refresh)
        
    def OnDoubleClick(self, evt):
        if self.IS_CONTROLLED:
            # le __main__ traite cet event dans onToggleControl()
            event = RotaryKnobEvent(myEVT_TOGGLE_CONTROL, self.GetId())
            event._IS_CONTROLLED = False
            event._ctlNumber = self.ctl_num
            self.GetEventHandler().ProcessEvent(event)
            # fin custom event
            self._change.stop()
            self._trigFunc.stop()
            self.IS_CONTROLLED = False
        else:
            # le __main__ traite cet event dans onToggleControl()
            event = RotaryKnobEvent(myEVT_TOGGLE_CONTROL, self.GetId())
            event._IS_CONTROLLED = True
            event._ctlNumber = self.ctl_num
            self.GetEventHandler().ProcessEvent(event)
            # fin custom event
            self._change.play()
            self._trigFunc.play()
            self.IS_CONTROLLED = True
        wx.CallAfter(self.Refresh)
        
    def OnMotion(self, evt):
        if not self.IS_CONTROLLED and self._clicked:
            pos = wx.GetMousePosition()[1]
            if evt.ShiftDown():
                if not self._shift_down:
                    print "shift down"
                    self._shift_down = True
                    self._mouse_y_org = wx.GetMousePosition()[1]
                    self._lastValue = self._value
                div = self._mouse_ratio * self._ratio_multiplicator
            else:
                if self._shift_down:
                    print "shift up"
                    self._shift_down = False
                    self._mouse_y_org = wx.GetMousePosition()[1]
                    self._lastValue = self._value
                div = self._mouse_ratio
            delta = (self._mouse_y_org - pos) / div
            self.setValue(self._lastValue+delta, False)
            wx.CallAfter(self.Refresh)
            #Custom event business
            event = RotaryKnobEvent(myEVT_VALUE_CHANGED, self.GetId())
            self.GetEventHandler().ProcessEvent(event)

    def Enable(self, value):
        if value:
            self.SetTransparent(255)
        else:
            self.SetTransparent(100)
        wx.Control.Enable(self, value)
            
    def _hideValue(self, evt):
        self.SHOW_VALUE = False
        wx.CallAfter(self.Refresh)
            
    def _startTimer(self):
        if self._hideValueTimer.IsRunning():
            self._hideValueTimer.Stop()
        self._hideValueTimer.Start(1000, True)
    
    def _setValueFromCtl(self):
        self._lastValue = self._value
        value = self._midictl.get()
        if value > self._max:
            self._value = self._max
        elif value < self._min:
            self._value = self._min
        else:
            self._value = value
        if self._callback != None:
            self._callback(self._value)
        self.SHOW_VALUE = True
        wx.CallAfter(self.Refresh)
        wx.CallAfter(self._startTimer)
        #Custom event business
        event = RotaryKnobEvent(myEVT_VALUE_CHANGED, self.GetId())
        self.GetEventHandler().ProcessEvent(event)
    
    def _toggleMidiLearn(self):
        if self.MIDI_LEARN:
            self.MIDI_LEARN = False
            self.ctl_scan.stop()
            del self.ctl_scan
            self._midictl.setCtlNumber(self.ctl_num)
        else:
            self.MIDI_LEARN = True
            self.ctl_scan = CtlScan(self._setCtlNum, False)

    def _setCtlNum(self, num):
        self.ctl_num = num
        wx.CallAfter(self.Refresh)
    
    def setText(self, text):
        """
        Sets the text to show under the control and
        sets the size of the control accordingly.
        Creates self._bmpMargin and self._txtMargin (or updates them) so
        that the bitmap and the text are centered in the control.
        """
        self._text = text
        dc = wx.ClientDC(self)
        dc.SetFont(self._font)
        tw,th = dc.GetTextExtent(self._text)
        if tw > self.bmp_w:
            self._bmpMargin = (tw-self.bmp_w)/2
            self._txtMargin = 0
            w = tw
        else:
            self._bmpMargin = 0
            self._txtMargin = (self.bmp_w-tw)/2
            w = self.bmp_w
        if w%2 == 0:
            self._knob_center = w/2-1
        else:
            self._knob_center = w/2
        h = self._textMargin+th+self.bmp_h
        self.SetSize((w,h))
    
    def setValue(self, value, set_old=True):
        if not self.IsEnabled(): return

        if value > self._max:
            self._value = self._max
        elif value < self._min:
            self._value = self._min
        else:
            self._value = value
        if set_old:
            self._lastValue = self._value
        if self._callback != None:
            self._callback(self._value)
        #s'occupe de l'affichage de la valeur
        self.SHOW_VALUE = True
        self._startTimer()
        wx.CallAfter(self.Refresh)
        #Custom event business
        event = RotaryKnobEvent(myEVT_VALUE_CHANGED, self.GetId())
        self.GetEventHandler().ProcessEvent(event)
        
    def setCallback(self, callback):
        self._callback = callback
        
    def getValue(self):
        return self._value

    def getOldValue(self):
        return self._lastValue

class PSClick(wx.Control):
    def __init__(self, parent, pos, tempo, nchnls):
        wx.Control.__init__(self, parent, -1, pos, (143,30), style=wx.NO_BORDER)
        self._tempo = tempo
        #metronome is playing at creation time
        self._metronome = Click(tempo, nchnls)
        self._btn = PSButtons.PSClickButton(self, (95, 0))
        self._btn.disable()
        
        #variables d'etat
        self._outputting = False

        self._font = wx.Font(**PSConfig.FONTS['light']['large'])
        #bitmaps
        self.ctrl_bmp = click_bpm_ctrl.GetBitmap()
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(PSButtons.EVT_BTN_CLICKED, self.OnClick)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        
    def __getitem__(self, i):
        if i == 'click':
            return self._metronome[i]
    
    def reinit(self, nchnls):
        self._metronome.reinit(nchnls)
        
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        dc.SetFont(self._font)
        dc.SetTextForeground("#fefefe")
        
        dc.DrawBitmap(self.ctrl_bmp,0,0)
        tw,th = dc.GetTextExtent("%.2f bpm"%self._tempo)
        dc.DrawText("%.2f bpm" % self._tempo, (95-tw) / 2, 9 - PSConfig.Y_OFFSET)
        
    def OnClick(self, evt):
        if self._outputting:
            self._metronome.mute()
            self._outputting = False
            self._btn._state = False
        else:
            self._metronome.out()
            self._outputting = True
            self._btn._state = True
        wx.CallAfter(self.Refresh)
        
    def OnDoubleClick(self, evt):
        self.tempoCtrl = wx.TextCtrl(self, -1, str(self._tempo), (8,4), (80,-1), wx.TE_PROCESS_ENTER)
        self.Parent.Parent._addToWhiteList(self.tempoCtrl.GetId())
        self.tempoCtrl.Bind(wx.EVT_TEXT_ENTER, self.setTempoByEvent)
        self.tempoCtrl.SetBackgroundColour("#102D3D")
        self.tempoCtrl.SetForegroundColour("#fefefe")
        self.tempoCtrl.SetFont(self._font)
        
    def setTempoByEvent(self, evt):
        try:
            self._tempo = float(self.tempoCtrl.GetValue())
            self._metronome.setTempo(self._tempo)
        except:
            pass
        self.Parent.Parent._removeFromWhiteList(self.tempoCtrl.GetId())
        self.tempoCtrl.Show(False)
        self.tempoCtrl.Destroy()
        wx.CallAfter(self.Refresh)

    def setTempo(self, value):
        self._tempo = float(value)
        self._metronome.setTempo(self._tempo)
        wx.CallAfter(self.Refresh)

    def getTempo(self, sig=True):
        return self._metronome.getTempo(sig)

    def getTime(self, sig=True):
        return self._metronome.getTime(sig)

    def getFreq(self, sig=True):
        return self._metronome.getFreq(sig)
        
    def disable(self):
        self._btn.disable()
        
    def enable(self):
        self._btn.enable()
        
    def play(self):
        self._metronome.play()
        
    def stop(self):
        self._metronome.stop()
        self._metronome.mute()
        self._outputting = False
        self._btn._state = False
        wx.CallAfter(self.Refresh)
