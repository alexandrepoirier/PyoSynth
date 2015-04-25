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

import wx
import buttonsPyImg as BPY

myEVT_BTN_CLICKED = wx.NewEventType()
EVT_BTN_CLICKED = wx.PyEventBinder(myEVT_BTN_CLICKED, 1)

myEVT_BTN_RUN = wx.NewEventType()
EVT_BTN_RUN = wx.PyEventBinder(myEVT_BTN_RUN, 1)

myEVT_BTN_REC = wx.NewEventType()
EVT_BTN_REC = wx.PyEventBinder(myEVT_BTN_REC, 1)

myEVT_BTN_OPEN = wx.NewEventType()
EVT_BTN_OPEN = wx.PyEventBinder(myEVT_BTN_OPEN, 1)

myEVT_BTN_PLAY = wx.NewEventType()
EVT_BTN_PLAY = wx.PyEventBinder(myEVT_BTN_PLAY, 1)

myEVT_BTN_STOP = wx.NewEventType()
EVT_BTN_STOP = wx.PyEventBinder(myEVT_BTN_STOP, 1)

class PSButtonEvent(wx.PyCommandEvent):
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)
        self._state = False
        self._evt_obj = None
        
    def IsRunning(self):
        return self._state
        
    def GetState(self):
        return self._state
        
    def GetEventObject(self):
        return self._evt_obj

class PSButtonBase(wx.Control):
    def __init__(self, parent, pos, size):
        wx.Control.__init__(self, parent, -1, pos, size, style=wx.NO_BORDER)
        
        self.normal = None
        self.hover = None
        self.clicked = None
        self.disabled = None
        
        self._hovered = False
        self._clicked = False
        self._enabled = True
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ENTER_WINDOW, self.MouseIn)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.MouseOut)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        self.Bind(wx.EVT_LEFT_UP, self.OnClickUp)
        
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        
        if self._clicked:
            dc.DrawBitmap(self.clicked, 0, 0)
        elif self._hovered:
            dc.DrawBitmap(self.hover, 0, 0)
        elif not self._enabled:
            dc.DrawBitmap(self.disabled, 0, 0)
        else:
            dc.DrawBitmap(self.normal, 0, 0)
        
    def MouseIn(self, evt):
        self._hovered = True
        wx.CallAfter(self.Refresh)
        
    def MouseOut(self, evt):
        self._hovered = False
        self._clicked = False
        wx.CallAfter(self.Refresh)
        
    def OnClick(self, evt):
        self._clicked = True
        wx.CallAfter(self.Refresh)
        
        #Custom event business
        evt = PSButtonEvent(myEVT_BTN_CLICKED, self.GetId())
        self.GetEventHandler().ProcessEvent(evt)
        
    def OnClickUp(self, evt):
        self._clicked = False
        wx.CallAfter(self.Refresh)
        
    def disable(self):
        self._enabled = False
        self.SetTransparent(200)
        #for the run button only
        if hasattr(self, "textCtrl"):
            self.textCtrl.SetForegroundColour("#999999")
        self.Disable()
        
    def enable(self):
        self._enabled = True
        self.SetTransparent(255)
        #for the run button only
        if hasattr(self, "textCtrl"):
            self.textCtrl.SetForegroundColour("#6cff00")
        self.Enable()
        
class ServerSetupButton(PSButtonBase):
    def __init__(self, parent, pos):
        PSButtonBase.__init__(self, parent, pos, (17,59))
        
        self.SetName("server button")
        
        self.normal = BPY.server_btn_normal.GetBitmap()
        self.disabled = BPY.server_btn_normal.GetImage().ConvertToGreyscale().ConvertToBitmap()
        self.hover = BPY.server_btn_hover.GetBitmap()
        self.clicked = BPY.server_btn_clicked.GetBitmap()
        
class OpenButton(PSButtonBase):
    def __init__(self, parent, pos):
        PSButtonBase.__init__(self, parent, pos, (77,28))
        
        self.normal = BPY.open_btn_normal.GetBitmap()
        self.disabled = BPY.open_btn_normal.GetImage().ConvertToGreyscale().ConvertToBitmap()
        self.hover = BPY.open_btn_hover.GetBitmap()
        self.clicked = BPY.open_btn_clicked.GetBitmap()
        
class SaveButton(PSButtonBase):
    def __init__(self, parent, pos):
        PSButtonBase.__init__(self, parent, pos, (80,28))
        
        self.normal = BPY.save_btn_normal.GetBitmap()
        self.disabled = BPY.save_btn_normal.GetImage().ConvertToGreyscale().ConvertToBitmap()
        self.hover = BPY.save_btn_hover.GetBitmap()
        self.clicked = BPY.save_btn_clicked.GetBitmap()
        
class RunButton(PSButtonBase):
    def __init__(self, parent, pos):
        PSButtonBase.__init__(self, parent, pos, (47,22))
        
        self.normal = BPY.run_btn_normal.GetBitmap()
        self.disabled = BPY.run_btn_normal.GetImage().ConvertToGreyscale().ConvertToBitmap()
        self.hover = BPY.run_btn_hover.GetBitmap()
        self.clicked = BPY.run_btn_clicked.GetBitmap()
        
        self.font = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, faceName="Helvetica")
        self.textCtrl = wx.StaticText(self, -1, "RUN", (8,6))
        self.textCtrl.SetFont(self.font)
        self.textCtrl.SetForegroundColour("#6cff00")
        
        self._running = False
        
        self.Bind(EVT_BTN_CLICKED, self.ToggleState)
        self.textCtrl.Bind(wx.EVT_ENTER_WINDOW, self.MouseIn)
        self.textCtrl.Bind(wx.EVT_LEAVE_WINDOW, self.MouseOut)
        self.textCtrl.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        self.textCtrl.Bind(wx.EVT_LEFT_UP, self.OnClickUp)
        
    def ToggleState(self, event):
        if self._running:
            self._running = False
            self.textCtrl.SetLabel("RUN")
            self.textCtrl.SetPosition((8,6))
            self.textCtrl.SetForegroundColour("#6cff00")
        else:
            self._running = True
            self.textCtrl.SetLabel("STOP")
            self.textCtrl.SetPosition((6,6))
            self.textCtrl.SetForegroundColour("#ff7f00")
        #Custom event business
        evt = PSButtonEvent(myEVT_BTN_RUN, self.GetId())
        evt._state = self._running
        self.GetEventHandler().ProcessEvent(evt)

class RecButton(PSButtonBase):
    def __init__(self, parent, pos):
        PSButtonBase.__init__(self, parent, pos, (37,37))
        
        self.normal = BPY.rec_btn_normal.GetBitmap()
        self.disabled = BPY.rec_btn_normal.GetImage().ConvertToGreyscale().ConvertToBitmap()
        self.hover = self.normal
        self.clicked = BPY.rec_btn_clicked.GetBitmap()
        
        self._running = False
        
        self.Bind(EVT_BTN_CLICKED, self.ToggleState)
        
    def ToggleState(self, event):
        event.Skip()
        self._running = not self._running
        #Custom event business
        evt = PSButtonEvent(myEVT_BTN_REC, self.GetId())
        evt._state = self._running
        self.GetEventHandler().ProcessEvent(evt)
        
class OpenRecButton(PSButtonBase):
    def __init__(self, parent, pos):
        PSButtonBase.__init__(self, parent, pos, (37,37))
        
        self.normal = BPY.rec_txt_btn_normal.GetBitmap()
        self.disabled = self.normal
        self.clicked = BPY.rec_txt_btn_up.GetBitmap()
        
        self._open = False
        
        self.Bind(EVT_BTN_CLICKED, self.ToggleState)
        
    #override the OnPaint function to reflect the state
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        
        if self._open:
            dc.DrawBitmap(self.clicked, 0, 0)
        elif not self._enabled:
            dc.DrawBitmap(self.disabled, 0, 0)
        else:
            dc.DrawBitmap(self.normal, 0, 0)
    
    def ToggleState(self, event):
        self._open = not self._open
        #Custom event business
        evt = PSButtonEvent(myEVT_BTN_OPEN, self.GetId())
        evt._state = self._open
        self.GetEventHandler().ProcessEvent(evt)
        
class PlayTrackButton(wx.Control):
    def __init__(self, parent, pos):
        wx.Control.__init__(self, parent, -1, pos, (9,11))
        
        self.play = BPY.play_btn.GetBitmap()
        self.clicked_play = BPY.play_btn.GetImage().AdjustChannels(.6,.6,.6).ConvertToBitmap()
        self.pause = BPY.pause_btn.GetBitmap()
        self.clicked_pause = BPY.pause_btn.GetImage().AdjustChannels(.6,.6,.6).ConvertToBitmap()
        
        self._playing = False
        self._clicked = False
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_UP, self.OnClickUp)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        
        if self._playing:
            if self._clicked:
                dc.DrawBitmap(self.clicked_pause, 1, 2)
            else:
                dc.DrawBitmap(self.pause, 1, 2)
        else:
            if self._clicked:
                dc.DrawBitmap(self.clicked_play, 0, 0)
            else:
                dc.DrawBitmap(self.play, 0, 0)
        
    def OnClick(self, evt):
        self._clicked = True
        wx.CallAfter(self.Refresh)

    def OnClickUp(self, evt):
        self._clicked = False
        self._playing = not self._playing
        wx.CallAfter(self.Refresh)
        
        #Custom event business
        evt = PSButtonEvent(myEVT_BTN_PLAY, self.GetId())
        evt._state = self._playing
        self.GetEventHandler().ProcessEvent(evt)
        
    def SetState(self, state):
        self._playing = state
        wx.CallAfter(self.Refresh)
        
class StopTrackButton(wx.Control):
    def __init__(self, parent, pos):
        wx.Control.__init__(self, parent, -1, pos, (7,7))
        
        self.normal = BPY.stop_btn.GetBitmap()
        self.clicked = BPY.stop_btn.GetImage().AdjustChannels(.6,.6,.6).ConvertToBitmap()
        
        self._clicked = False
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        self.Bind(wx.EVT_LEFT_UP, self.OnClickUp)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)
        
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        if self._clicked:
            dc.DrawBitmap(self.clicked,0,0)
        else:
            dc.DrawBitmap(self.normal,0,0)
        
    def OnClick(self, evt):
        self._clicked = True
        wx.CallAfter(self.Refresh)
        
    def OnClickUp(self, evt):
        self._clicked = False
        wx.CallAfter(self.Refresh)
        #Custom event business
        evt = PSButtonEvent(myEVT_BTN_STOP, self.GetId())
        self.GetEventHandler().ProcessEvent(evt)
        
    def OnLeave(self, evt):
        self._clicked = False
        wx.CallAfter(self.Refresh)
        
class SaveTrackButton(PSButtonBase):
    def __init__(self, parent, pos):
        PSButtonBase.__init__(self, parent, pos, (13,13))
        
        self.normal = BPY.save_track_btn_normal.GetBitmap()
        self.hover = BPY.save_track_btn_hover.GetBitmap()
        self.clicked = self.hover
        
    def disable(self):
        pass
        
    def enable(self):
        pass
        
class DeleteTrackButton(PSButtonBase):
    def __init__(self, parent, pos):
        PSButtonBase.__init__(self, parent, pos, (12,12))
        
        self.normal = BPY.delete_track_btn_normal.GetBitmap()
        self.hover = BPY.delete_track_btn_hover.GetBitmap()
        self.clicked = self.hover
        
    def disable(self):
        pass
        
    def enable(self):
        pass
        
class RectangleStateButton(wx.Control):
    size = (28,15)
    def __init__(self, parent, pos, value):
        wx.Control.__init__(self, parent, -1, pos, RectangleButton.size, style=wx.NO_BORDER)
        
        self._value = value
        self._brush_colours = ["#3d3d3d","#202020"]
        self._pen_colours = ["#3d3d3d","#CFCFCF"]
        self._selected = 0
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.MouseDown)
        
    def OnPaint(self, evt):
        w,h = self.GetSize()
        dc = wx.PaintDC(self)
        
        dc.SetPen(wx.Pen(self._pen_colours[self._selected],1))
        dc.SetBrush(wx.Brush(self._brush_colours[self._selected]))
        dc.DrawRectangle(0,0,w,h)
        
        dc.SetTextForeground("#CFCFCF")
        dc.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, faceName="Helvetica"))
        text = "%d"%self._value
        tw,th = dc.GetTextExtent(text)
        dc.DrawText(text, (w-tw)/2, (h-th)/2+1)
        
    def MouseDown(self, evt):
        self._selected = 1
        #Custom event business
        event = PSButtonEvent(myEVT_BTN_CLICKED, self.GetId())
        event._evt_obj = self
        self.GetEventHandler().ProcessEvent(event)
        wx.CallAfter(self.Refresh)
        
    def GetValue(self):
        return self._value
        
    def SetState(self, state):
        if state:
            self._selected = 1
        else:
            self._selected = 0
        wx.CallAfter(self.Refresh)
        
class PSRectangleButton(wx.Control):
    def __init__(self, parent, pos, size, text, id=-1):
        wx.Control.__init__(self, parent, id, pos, size, style=wx.NO_BORDER)
        
        self._font = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, faceName="Helvetica")
        self._brush_colours = ["#3d3d3d","#202020"]
        self._pen_colours = ["#3d3d3d","#f0f4d7"]
        self._clicked = 0
        self._hover = 0
        self.setText(text)
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.MouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.MouseUp)
        self.Bind(wx.EVT_ENTER_WINDOW, self.MouseIn)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.MouseOut)
        
    def OnPaint(self, evt):
        w,h = self.GetSize()
        dc = wx.PaintDC(self)
        
        dc.SetPen(wx.Pen(self._pen_colours[self._hover],1))
        dc.SetBrush(wx.Brush(self._brush_colours[self._clicked]))
        dc.DrawRectangle(0,0,w,h)
        
        dc.SetTextForeground("#f0f4d7")
        dc.SetFont(self._font)
        tw,th = dc.GetTextExtent(self._text)
        dc.DrawText(self._text, (w-tw)/2-1, (h-th)/2+2)
        
    def MouseDown(self, evt):
        self._clicked = 1
        #Custom event business
        event = PSButtonEvent(myEVT_BTN_CLICKED, self.GetId())
        self.GetEventHandler().ProcessEvent(event)
        wx.CallAfter(self.Refresh)
        
    def MouseUp(self, evt):
        self._clicked = 0
        wx.CallAfter(self.Refresh)
        
    def MouseIn(self, evt):
        self._hover = 1
        wx.CallAfter(self.Refresh)

    def MouseOut(self, evt):
        self._clicked = 0
        self._hover = 0
        wx.CallAfter(self.Refresh)
        
    def setSize(self, size):
        w,h = size
        if w < self._minWidth: w = self._minWidth
        if h < self._minHeight: h = self._minHeight
        self.SetSize((w,h))
        
    def setText(self, text):
        self._text = text
        dc = wx.ClientDC(self)
        dc.SetFont(self._font)
        tw,th = dc.GetTextExtent(text)
        self._minWidth = tw+4
        self._minHeight = th+4
        w,h = self.GetSize()
        if w < self._minWidth: w = self._minWidth
        if h < self._minHeight: h = self._minHeight
        self.SetSize((w,h))
        wx.CallAfter(self.Refresh)
        
class PSClickButton(PSButtonBase):
    def __init__(self, parent, pos):
        PSButtonBase.__init__(self, parent, pos, (48,30))
        
        self.normal = BPY.click_btn_normal.GetBitmap()
        self.hover = BPY.click_btn_hover.GetBitmap()
        self.clicked = BPY.click_btn_clicked.GetBitmap()
        self.disabled = BPY.click_btn_normal.GetImage().ConvertToGreyscale().ConvertToBitmap()

        self._state = False
        
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        
        if self._clicked:
            dc.DrawBitmap(self.clicked, 0, 0)
        elif self._hovered:
            dc.DrawBitmap(self.hover, 0, 0)
        elif not self._enabled:
            dc.DrawBitmap(self.disabled, 0, 0)
        else:
            dc.DrawBitmap(self.normal, 0, 0)
            
        font = wx.Font(14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, faceName="Helvetica")
        dc.SetFont(font)
        dc.SetTextForeground("#fefefe")
        if self._state:
            dc.DrawText("On",14,9)
        else:
            dc.DrawText("Off",14,9)
