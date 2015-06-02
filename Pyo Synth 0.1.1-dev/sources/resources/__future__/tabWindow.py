import tabWindowPyImg as img
import wx

myEVT_TAB_CLICKED = wx.NewEventType()
EVT_TAB_CLICKED = wx.PyEventBinder(myEVT_TAB_CLICKED, 1)

myEVT_CLOSE_TAB = wx.NewEventType()
EVT_CLOSE_TAB = wx.PyEventBinder(myEVT_CLOSE_TAB, 1)

class TabWindowEvent(wx.PyCommandEvent):
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)
        self._id_ = -1
        
    def GetTabId(self):
        return self._id_

class PSTabWindowCloseButton(wx.Control):
    def __init__(self, parent):
        wx.Control.__init__(self, parent, -1, (0,0), (7,7), style=wx.NO_BORDER)
        
        self._colors = ["#c7c7c7","#c30b0b"]
        self._hover = 0
        
        self.Bind(wx.EVT_ENTER_WINDOW, self.MouseIn)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.MouseOut)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
    def OnPaint(self, evt):
        w,h = self.GetSize()
        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen(self._colors[self._hover],1))
        dc.DrawLine(0,0,w,h)
        dc.DrawLine(0,h,w,0)
        
    def MouseIn(self, evt):
        self._hover = 1
        wx.CallAfter(self.Refresh)
        
    def MouseOut(self, evt):
        self._hover = 0
        wx.CallAfter(self.Refresh)
        
class PSTabWindowTab(wx.Control):
    def __init__(self, parent, id, pos, text, closable=False):
        wx.Control.__init__(self, parent, -1, pos, (1,1), style=wx.NO_BORDER)
        
        self._id_ = id
        self._text = text
        self._closable = closable
        
        self.ACTIVE = False
        self._minTabWidth = 80
        self._font = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, faceName="Helvetica")
        
        if self._closable:
            self._createCloseButton()
        self._drawBitmaps()
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        
        if self.ACTIVE:
            dc.DrawBitmap(self._active_bmp,0,0)
        else:
            dc.DrawBitmap(self._inactive_bmp,0,0)
            
    def OnMouseDown(self, evt):
        self.ACTIVE = True
        #Custom event business
        event = TabWindowEvent(myEVT_TAB_CLICKED, self.GetId())
        event._id_ = self._id_
        self.GetEventHandler().ProcessEvent(event)
        wx.CallAfter(self.Refresh)
        
    def OnClose(self, evt):
        #Custom event business
        event = TabWindowEvent(myEVT_CLOSE_TAB, self.GetId())
        event._id_ = self._id_
        self.GetEventHandler().ProcessEvent(event)
        self.Destroy()
        
    def _createCloseButton(self):
        self._closeButton = PSTabWindowCloseButton(self)
        self._closeButton.Bind(wx.EVT_LEFT_DOWN, self.OnClose)
        
    def _destroyCloseButton(self):
        self._closeButton.Destroy()
        self._closeButton.Unbind(wx.EVT_LEFT_DOWN, self.OnClose)
        self._drawBitmaps()
        
    def _drawBitmaps(self):
        w,h = self._getButtonSize()
        self.SetSize((w,h))
        self._active_bmp = wx.EmptyBitmap(w,h)
        self._inactive_bmp = wx.EmptyBitmap(w,h)
        
        #source bmps
        a_left = img.tabwin_active_tab_left.GetBitmap()
        a_mid = img.tabwin_active_tab_middle.GetBitmap()
        a_right = img.tabwin_active_tab_right.GetBitmap()
        i_left = img.tabwin_inactive_tab_left.GetBitmap()
        i_mid = img.tabwin_inactive_tab_middle.GetBitmap()
        i_right = img.tabwin_inactive_tab_right.GetBitmap()
        
        #create DC and draw active bmp
        dc = wx.MemoryDC(self._active_bmp)
        dc.SetFont(self._font)
        dc.SetTextForeground("#c7c7c7")
        
        side_w = a_left.GetSize()[0]
        mid_w = a_mid.GetSize()[0]
        full = (w-side_w*2)/mid_w #mid bmps to draw completely
        rest = (w-side_w*2)%mid_w #mid bmp to draw partially
        
        dc.DrawBitmap(a_left,0,0)
        for i in range(full):
            offset = mid_w*i+side_w
            dc.DrawBitmap(a_mid,offset,0)
        x = mid_w*full+side_w
        dc.SetClippingRegion(x,0,rest,h)
        dc.DrawBitmap(a_mid,x,0)
        dc.DestroyClippingRegion()
        dc.DrawBitmap(a_right,x+rest,0)
        dc.DrawText(self._text,8,6)
        
        #now draw the inactive bmp
        dc.SelectObject(self._inactive_bmp)
        dc.DrawBitmap(i_left,0,0)
        for i in range(full):
            offset = mid_w*i+side_w
            dc.DrawBitmap(i_mid,offset,0)
        x = mid_w*full+side_w
        dc.SetClippingRegion(x,0,rest,h)
        dc.DrawBitmap(i_mid,x,0)
        dc.DestroyClippingRegion()
        dc.DrawBitmap(i_right,x+rest,0)
        dc.DrawText(self._text,8,6)
        
        #if closable, position close button and refresh tab
        if self._closable:
            cb_w = self._closeButton.GetSize()[0]
            self._closeButton.SetPosition((w-cb_w-7, 7))
        
        wx.CallAfter(self.Refresh)
        
    def _getButtonSize(self):
        dc = wx.ClientDC(self)
        dc.SetFont(self._font)
        w,h = dc.GetTextExtent(self._text)
        w += 20 #Add a margin of 10px on both sides
        if self._closable:
            w += self._closeButton.GetSize()[0]+5
        if w < self._minTabWidth:
            w = self._minTabWidth
        h = img.tabwin_active_tab_middle.GetBitmap().GetSize()[1]
        return (w,h)
        
    def SetText(self, text):
        self._text = text
        self._drawBitmaps()
        
    def SetClosable(self, closable):
        if self._closable == closable:
            return
        else:
            if closable:
                self._createCloseButton()
            else:
                self._destroyCloseButton()
            self._closable = closable
            self._drawBitmaps()
            
    def SetState(self, state):
        self.ACTIVE = state
        wx.CallAfter(self.Refresh)
        
    def GetId(self):
        return self._id_

class PSTabWindow(wx.Panel):
    def __init__(self, parent, pos, size):
        wx.Panel.__init__(self, parent, -1, pos, size, style=wx.NO_BORDER)
        
        self._id_ = -1
        self._tabs_elements_ = {}
        self._tabs_buttons = {}
        self._activeTab = -1
        self._tabHeight = img.tabwin_active_tab_middle.GetBitmap().GetSize()[1]
        
        self._drawBitmaps()
        
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        self.Bind(EVT_TAB_CLICKED, self.OnTabClicked)
        self.Bind(EVT_CLOSE_TAB, self.OnTabClose)
        
    def OnPaint(self, evt):
        w,h = self.GetSize()
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self._tabs_bg,0,0)
        dc.DrawBitmap(self._bg,1,self._tabHeight+1)
        dc.SetPen(wx.Pen("#c7c7c7",1))
        dc.DrawLine(0,self._tabHeight,w,self._tabHeight)
        dc.DrawLine(w,self._tabHeight,w,h)
        dc.DrawLine(w,h,0,h)
        dc.DrawLine(0,h,0,self._tabHeight)
        
    def OnResize(self, evt):
        self._drawBitmaps()
        
    def OnTabClicked(self, evt):
        if self._activeTab == evt.GetTabId():
            return
        if self._activeTab != -1:
            self._tabs_buttons[self._activeTab].SetState(False)
            self._showActiveTabElements(False)
        self._activeTab = evt.GetTabId()
        self._showActiveTabElements(True)
                
    def OnTabClose(self, evt):
        id = evt.GetTabId()
        if self._activeTab == id:
            if self._selectNextTab():
                if self._selectPreviousTab():
                    print 'oopss'
                    self._activeTab = -1
        self._destroyTabElements(id)
        del self._tabs_elements_[id]
        del self._tabs_buttons[id]
        self._updateTabsPositions()
        
    def OnQuit(self, evt):
        self._destroyAllTabs()
        self.Destroy()
        
    def _drawBitmaps(self):
        w,h = self.GetSize()
        self._bg = wx.EmptyBitmap(w-2, h-2-self._tabHeight)
        self._tabs_bg = wx.EmptyBitmap(w, self._tabHeight)
        
        #source bmps
        bg = img.tabwin_bg_tile.GetBitmap()
        tabs_bg = img.tabwin_tab_bg_tile.GetBitmap()

        #create DC and draw background
        dc = wx.MemoryDC(self._bg)
        
        bg_w, bg_h = bg.GetSize()
        rows = self._bg.GetSize()[1]/bg_h+1
        cols = self._bg.GetSize()[0]/bg_w+1
        for i in range(rows):
            y = bg_h*i
            for i in range(cols):
                x = bg_w*i
                dc.DrawBitmap(bg,x,y)

        #draw the tabs bg
        dc.SelectObject(self._tabs_bg)
        bg_w, bg_h = tabs_bg.GetSize()
        cols = self._tabs_bg.GetSize()[0]/bg_w+1
        for i in range(cols):
            dc.DrawBitmap(tabs_bg,bg_w*i,0)
        wx.CallAfter(self.Refresh)
        
    def _selectNextTab(self):
        for id in range(self._activeTab+1, self._id_+1):
            if id in self._tabs_buttons:
                self._activeTab = id
                self._tabs_buttons[id].SetState(True)
                self._showActiveTabElements(True)
                return 0
        return 1
        
    def _selectPreviousTab(self):
        for id in range(self._activeTab-1,-1,-1):
            if id in self._tabs_buttons:
                self._activeTab = id
                self._tabs_buttons[id].SetState(True)
                self._showActiveTabElements(True)
                return 0
        return 1
            
    def _showActiveTabElements(self, show):
        for win in self._tabs_elements_[self._activeTab]:
            win.Show(show)
            
    def _destroyTabElements(self, id):
        for win in self._tabs_elements_[id]:
            win.Destroy()
            
    def _destroyAllTabs(self):
        for tab in self._tabs_elements:
            self._destroyTabElements(tab)
            self._tabs_elements_[tab].Destroy()
            
    def _getNewId(self):
        self._id_ += 1
        return self._id_
        
    def _getNewTabPos(self):
        pos = 0
        for id in self._tabs_buttons:
            pos += self._tabs_buttons[id].GetSize()[0]+1
        return (pos,0)
        
    def _updateTabsPositions(self):
        pos = 0
        for id in range(self._id_+1):
            if id in self._tabs_buttons:
                self._tabs_buttons[id].SetPosition((pos,0))
                pos += self._tabs_buttons[id].GetSize()[0]+1
        
    def addTab(self, name, closable=False):
        """
        Add a tab to the tabbed window.
        This method returns the tab id which is needed to add elements to the tab.
        """
        id = self._getNewId()
        self._tabs_buttons[id] = PSTabWindowTab(self, id, self._getNewTabPos(), name, closable)
        self._tabs_elements_[id] = []
        if self._activeTab == -1:
            self._activeTab = id
            self._tabs_buttons[id].SetState(True)
        return id
        
    def addElementToTab(self, element, tab_id):
        """
        Adds an element to the tab specified with tab_id.
        Note : 'element' attribute must have Show and Destroy methods.
        """
        assert tab_id in self._tabs_buttons, "tab_id : %d, not valid." % tab_id
        x, y = element.GetPosition()
        element.SetPosition((x,y+self._tabHeight+1))
        self._tabs_elements_[tab_id].append(element)
        if tab_id != self._activeTab:
            element.Show(False)

if __name__ == "__main__":
    import tools
    from pyo import *
    app = wx.App(False)
    
    s = Server().boot().start()
    lfo = Sine([1,.2,200], mul=[100,50,100], add=[515,200,1500])
    sine = Sine(lfo, mul=.2).mix(2).out()
    
    fstyle = wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX)
    frame = wx.Frame(None, -1, "PSTabWindow Test", (100,100), (1140,300), style=fstyle)
    
    tab_win = PSTabWindow(frame, (0,0), frame.GetSize())
    editor = tab_win.addTab("Code editor")
    anal = tab_win.addTab("Analysis tools")
    
    scope = tools.PSScope(tab_win,(10,10),(500,200), sine)
    tab_win.addElementToTab(scope, anal)
    
    spectrum = tools.PSSpectrum(tab_win,(520,10),(500,200), sine, s.getSamplingRate())
    tab_win.addElementToTab(spectrum, anal)

    frame.Show()
    app.MainLoop()