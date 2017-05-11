import wx
from wx.lib.embeddedimage import PyEmbeddedImage
import math
import PSConfig
import PSButtons
import PSUtils

myEVT_SCROLL_MOTION = wx.NewEventType()
EVT_SCROLL_MOTION = wx.PyEventBinder(myEVT_SCROLL_MOTION, 1)

class PSScrollBarEvent(wx.PyCommandEvent):
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)
        self._absolute_pixel_pos = 0.
        self._normal_value = 0.

    def GetNormalValue(self):
        return self._normal_value

    def GetAbsolutePixelPosition(self):
        return self._absolute_pixel_pos

class PSScrollBar(wx.Panel):
    _bar_margin = 3
    _bar_min_height = 24
    _base_ratio = 2
    _width = 11
    _bar_width = 5
    _click_y_inc = 50.

    def __init__(self, parent, id, pos, height, virtual_height, bg_colour="#FFFFFF", bar_colour="#7F7F7F"):
        wx.Panel.__init__(self, parent, id, pos, (PSScrollBar._width, height))
        self.SetBackgroundColour(bg_colour)
        self._scrollbar_colour = bar_colour
        self._virtual_height = 0.
        self._norm_value = 0.
        self._click_pos_y = 0
        self._CLICKED = False
        self.setVirtualHeight(virtual_height)

        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.OnMouseCaptureLost)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, evt):
        if self._content_ratio < 1:
            return
        else:
            dc = wx.PaintDC(self)
            dc.SetBrush(wx.Brush(self._scrollbar_colour))
            dc.SetPen(wx.Pen(self._scrollbar_colour, 1))
            dc.DrawRoundedRectangle(3, self._getScrollbarPos(), PSScrollBar._bar_width, self._getScrollbarHeight(), 2)

    def OnMouseDown(self, evt):
        if self._content_ratio > 1:
            mouse_relative_pos = self._getMouseRelativePosScrollbar()
            if mouse_relative_pos == 0:
                self._CLICKED = True
                self._click_pos_y = wx.GetMousePosition()[1]
                self.CaptureMouse()
            elif mouse_relative_pos > 0:
                self.setNormalValue(self._norm_value + PSScrollBar._click_y_inc / self._virtual_height)
                self._sendScrollbarEvent()
            elif mouse_relative_pos < 0:
                self.setNormalValue(self._norm_value - PSScrollBar._click_y_inc / self._virtual_height)
                self._sendScrollbarEvent()

    def OnMouseUp(self, evt):
        self._CLICKED = False
        self._click_pos_y = 0
        if self.HasCapture():
            self.ReleaseMouse()

    def OnMouseMotion(self, evt):
        if self._CLICKED:
            delta_y = wx.GetMousePosition()[1] - self._click_pos_y
            self.setNormalValue(self._norm_value + self._getNormStep() * delta_y)
            self._click_pos_y = wx.GetMousePosition()[1]
            self._sendScrollbarEvent()
            self.Refresh()

    def OnMouseCaptureLost(self, evt):
        self._CLICKED = False
        self._click_pos_y = 0

    def SetHeight(self, height):
        wx.Panel.SetSize(self, (PSScrollBar._width, height))
        self.setVirtualHeight(self._virtual_height)

    def SetSize(self, size):
        self.SetHeight(size[1])

    def _sendScrollbarEvent(self):
        event = PSScrollBarEvent(myEVT_SCROLL_MOTION, self.GetId())
        event._absolute_pixel_pos = self.getAbsolutePixelPosition()
        event._normal_value = self._norm_value
        self.GetEventHandler().ProcessEvent(event)

    def _getScrollbarHeight(self):
        h = self.GetSize()[1]
        min_h = h - PSScrollBar._bar_margin*2
        val = min_h - (self._virtual_height - h) / PSScrollBar._base_ratio
        if val < PSScrollBar._bar_min_height:
            return PSScrollBar._bar_min_height
        elif val > min_h - PSScrollBar._base_ratio:
            return min_h - PSScrollBar._base_ratio
        else:
            return val

    def _getScrollbarPos(self):
        return self._scrollbar_travel * self._norm_value + PSScrollBar._bar_margin

    def _getMouseRelativePosScrollbar(self):
        mouse_y = self.ScreenToClient(wx.GetMousePosition())[1]
        bar_y1 = self._getScrollbarPos()
        bar_y2 = bar_y1 + self._scrollbar_height
        if mouse_y < bar_y1:
            return mouse_y - bar_y1
        elif mouse_y > bar_y2:
            return mouse_y - bar_y2
        else:
            return 0

    def _getNormStep(self):
        return 1. / self._scrollbar_travel

    def _getPixelRatio(self):
        actual_ratio = (self._virtual_height - self.GetSize()[1]) / float(self._scrollbar_travel*PSScrollBar._base_ratio)
        if actual_ratio > 1:
            return math.floor(actual_ratio)
        else:
            return PSScrollBar._base_ratio

    def getAbsolutePixelPosition(self):
        return math.floor(self._norm_value * (self._virtual_height - self.GetSize()[1]))

    def setVirtualHeight(self, value):
        self._virtual_height = value
        self._content_ratio = value/float(self.GetSize()[1])
        if self._content_ratio > 1:
            self._scrollbar_height = self._getScrollbarHeight()
            self._scrollbar_travel = self.GetSize()[1] - self._scrollbar_height - PSScrollBar._bar_margin*2
        else:
            self._scrollbar_height = -1
            self._scrollbar_travel = -1
        self.Refresh()

    def setNormalValue(self, value):
        if value > 1:
            self._norm_value = 1.
        elif value < 0:
            self._norm_value = 0.
        else:
            self._norm_value = value
        self.Refresh()

    def setPrecent(self, percent):
        if percent > 100:
            self._norm_value = 1.
        elif percent < 0:
            self._norm_value = 0.
        else:
            self._norm_value = percent/100.
        self.Refresh()


class PSScrolledWindow(wx.Panel):
    def __init__(self, parent, id, pos, size):
        wx.Panel.__init__(self, parent, id, pos, size)
        self._scroll_bar = PSScrollBar(self, -1, (size[0]-PSScrollBar._width, 0), size[1], size[1])
        self._virtual_panel = wx.Panel(self, -1, (0,0), (self.GetSize()[0]-PSScrollBar._width, size[1]))
        self._virtual_height = size[1]

        self.Bind(EVT_SCROLL_MOTION, self.OnScrollMotion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self._virtual_panel.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)

    def OnScrollMotion(self, evt):
        self.SetVirtualPosition(-evt.GetAbsolutePixelPosition())
        wx.PostEvent(self, evt)

    def OnMouseWheel(self, evt):
        if self.GetSize()[1] - self._virtual_height < 0:
            self.SetVirtualPosition(self._virtual_panel.GetPosition()[1] + evt.GetWheelRotation())
            norm = self._virtual_panel.GetPosition()[1] / float(self.GetSize()[1] - self._virtual_height)
            self._scroll_bar.setNormalValue(norm)

    def SetSize(self, size):
        self._scroll_bar.SetHeight(size[1])
        self._scroll_bar.SetPosition((size[0]-PSScrollBar._width, 0))
        self._virtual_panel.SetSize((size[0]-PSScrollBar._width, self._virtual_height))
        wx.Panel.SetSize(self, size)

    def SetBackgroundColour(self, colour):
        wx.Panel.SetBackgroundColour(self, colour)
        self._virtual_panel.SetBackgroundColour(colour)

    def SetVirtualPosition(self, value):
        x = self._virtual_panel.GetPosition()[0]
        if value < self.GetSize()[1] - self._virtual_height:
            self._virtual_panel.SetPosition((x, self.GetSize()[1] - self._virtual_height))
        elif value > 0:
            self._virtual_panel.SetPosition((x, 0))
        else:
            self._virtual_panel.SetPosition((x, value))

    def setVirtualHeight(self, height):
        self._virtual_height = height
        self._virtual_panel.SetSize((self.GetSize()[0]-PSScrollBar._width, height))
        self._scroll_bar.setVirtualHeight(height)


class PatchesList(PSScrolledWindow):
    def __init__(self, parent, id, pos, size, margin_x=2, margin_y=2, bg_colour="#FFFFFF"):
        PSScrolledWindow.__init__(self, parent, id, pos, (size[0]+margin_x*2, size[1]))
        self.SetBackgroundColour(bg_colour)
        self._margin_x = margin_x
        self._margin_y = margin_y

        self._filters_text = ""
        self._filters_types = []

        self._elem_list = []
        self._text_filtered_elem_list = []
        self._type_filtered_elem_list = []
        self._displayed_elem_list = []
        self._selected_elem = None

    def applyFilters(self):
        del self._displayed_elem_list[:]
        if self._filters_text or self._filters_types:
            self._filterByType()
            self._filterByText()
            self._crossFilter()
            self._showFilteredElements()
        else:
            self._displayed_elem_list = list(self._elem_list)
            self._showAllElements()
        self.setVirtualHeight(self._getDisplayedListHeight())
        self._setElementsPositions()

    def _filterByType(self):
        del self._type_filtered_elem_list[:]
        if self._filters_types:
            for elem in self._elem_list:
                if elem.getType() in self._filters_types:
                    self._type_filtered_elem_list.append(elem)

    def _filterByText(self):
        del self._text_filtered_elem_list[:]
        if self._filters_text:
            for elem in self._elem_list:
                if self._filters_text in elem.getName().lower():
                    self._text_filtered_elem_list.append(elem)

    def _crossFilter(self):
        if self._type_filtered_elem_list:
            if self._text_filtered_elem_list:
                for elem in self._type_filtered_elem_list:
                    if self._filters_text in elem.getTitle():
                        self._displayed_elem_list.append(elem)
            else:
                self._displayed_elem_list = list(self._type_filtered_elem_list)
        elif self._text_filtered_elem_list:
            self._displayed_elem_list = list(self._text_filtered_elem_list)

    def _showFilteredElements(self):
        for elem in self._elem_list:
            if elem in self._displayed_elem_list:
                elem.Show(True)
            else:
                elem.Show(False)

    def _showAllElements(self):
        for elem in self._elem_list:
            elem.Show(True)

    def _setElementsPositions(self):
        for i, elem in enumerate(self._displayed_elem_list):
            y = (PatchElem._size[1] + self._margin_y) * i + self._margin_y
            elem.SetPosition((self._margin_x, y))

    def _getDisplayedListHeight(self):
        num_elems = len(self._displayed_elem_list)
        return (num_elems*self._margin_y+self._margin_y) + (num_elems * PatchElem._size[1])

    def setSelected(self, elem):
        if self._selected_elem == elem:
            return
        if self._selected_elem is not None:
            if self._selected_elem._settings_win is not None:
                self._selected_elem._settings_win.Destroy()
                self._selected_elem._settings_win = None
            self._selected_elem.deselect()
        self._selected_elem = elem

    def addElement(self, data):
        assert isinstance(data, dict), "PSPatchesList.addElement: data argument must be of type dict"
        elem = PatchElem(self._virtual_panel, data)
        elem.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self._elem_list.append(elem)
        self.applyFilters()

    def addElements(self, datas):
        assert isinstance(datas, list), "PSPatchesList.addElements: datas argument must be of type list"
        for data in datas:
            assert isinstance(data, dict), "PSPatchesList.addElement: data argument must be of type dict"
            elem = PatchElem(self._virtual_panel, data)
            elem.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
            self._elem_list.append(elem)
        self.applyFilters()

    def setTypeFilters(self, types):
        assert isinstance(types, list), "types argument must be a list"
        self._filters_types = types

    def setTextFilter(self, text):
        assert isinstance(text, str), "text argument must be a string"
        self._filters_text = text.lower()

# colours: gradient start, gradient end, border colour
PATCHES_TYPES_COLOURS = {'Analog':("#ffde00", "#ffa902", "#ffe744"),
                         'Digital':("#52d0ff","#1e6ba1", "#85deff"),
                         'Granular':("#12fc1d","#009904", "#43ff4c"),
                         'Percussive':("#ff4660","#b3112f", "#ff687d"),
                         'Sampling':("#2ff4c3","#087e61", "#50ffd3"),
                         'Real time processing':("#ffa751","#be3f00", "#ffab49"),
                         'Effects':("#c46cf7","#8c32ad", "#d287fd"),
                         'default':("#f4f4f4","#919191", "#f0f0f0")}

# STATE: 0 = Not downloaded, 1 = Downloaded and updated, 2 = Needs update
PATCH_ELEM_DATA_MODEL = {'TYPE':str,'NAME':str,'ID':int,'STATE':int,'VERSION':int,'PACKAGE':str,'MODIFIED':bool,
                         'USER_PATCH':bool}
PATCH_ELEM_STATE_MAP = {0:'Download',1:'Load',2:'Update'}

class PatchElem(wx.Panel):
    _size = (315, 108)
    _x_margin = 15

    def __init__(self, parent, data, id=-1):
        wx.Panel.__init__(self, parent, id, (0,0), PatchElem._size)
        self._data = self._validateData(data)
        self._HOVERED = False
        self._SELECTED = False

        if self._data['TYPE'] in PATCHES_TYPES_COLOURS:
            self._gradient_colours = PATCHES_TYPES_COLOURS[self._data['TYPE']][:2]
            self._border_colour = PATCHES_TYPES_COLOURS[self._data['TYPE']][2]
        else:
            self._gradient_colours = PATCHES_TYPES_COLOURS['default'][:2]
            self._border_colour = PATCHES_TYPES_COLOURS['default'][2]

        sizex = 80
        posx = PatchElem._size[0] - sizex - PatchElem._x_margin
        posy = 15
        btn_colours = ["#434343", "#848484"]
        text_colour = "#e9e9e9"
        self._action_btn = PSButtons.PSRectangleButton(self, (posx,posy), (sizex,26), PATCH_ELEM_STATE_MAP[self._data['STATE']])
        self._action_btn.setColours(btn_colours)
        self._action_btn.setTextColour(text_colour)
        self._action_btn.setFaceName('Helvetica')
        self._details_btn = PSButtons.PSRectangleButton(self, (posx,posy+31), (sizex,26), "Details")
        self._details_btn.setColours(btn_colours)
        self._details_btn.setTextColour(text_colour)
        self._details_btn.setFaceName('Helvetica')

        self._settings_win = None
        if self._data['STATE'] != 0:
            self._settings_btn = PSButtons.PSSettingsButton(self, (270,80))
            self.Bind(PSButtons.EVT_BTN_CLICK_UP, self.ShowSettingsWin, self._settings_btn)

        self._title_font = wx.Font(faceName="Helvetica", **PSConfig.FONTS['bold']['title2'])
        self._info_font = wx.Font(faceName="Helvetica", **PSConfig.FONTS['light']['small'])

        self.Bind(PSButtons.EVT_BTN_CLICKED, self.OnMouseDownActionButton, self._action_btn)
        self.Bind(PSButtons.EVT_BTN_CLICKED, self.OnMouseDownDetailsButton, self._details_btn)
        self.Bind(wx.EVT_LEFT_DOWN, self._setSelected)
        self.Bind(wx.EVT_LEFT_UP, self._setSelected)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)

    def OnPaint(self, evt):
        w,h = PatchElem._size
        dc = wx.PaintDC(self)
        start, end = self._gradient_colours
        dc.GradientFillLinear((0,0,w,h), start, end, wx.SOUTH)
        if self._HOVERED or self._SELECTED:
            dc.SetPen(wx.Pen(self._border_colour, 1))
            dc.DrawLines([(0,0),(w-1,0),(w-1,h-1),(0,h-1),(0,0)])
        dc.SetTextForeground("#494949")
        dc.SetFont(self._title_font)
        dc.DrawText(self._data['NAME'], PatchElem._x_margin, 20)
        dc.SetFont(self._info_font)
        dc.DrawText("Type: " + self._data['TYPE'], PatchElem._x_margin, 47)
        ver_str = ""
        if self._data['STATE'] == 2:
            ver_str = "Version: *%d" % self._data['VERSION']
        else:
            ver_str = "Version: %d" % self._data['VERSION']
        dc.DrawText(ver_str, PatchElem._x_margin + 1, 62)
        dc.DrawText('Package: ' + self._data['PACKAGE'], PatchElem._x_margin, 77)

    def OnMouseDownActionButton(self, evt):
        if self._data['STATE'] == 0:
            print 'Download'
        elif self._data['STATE'] == 1:
            print 'Load'
        elif self._data['STATE'] == 2:
            print 'Update'
        self._setSelected(evt)

    def OnMouseDownDetailsButton(self, evt):
        print "Show details for patch id #%d" % self._data['ID']

    def OnMouseEnter(self, evt):
        self._HOVERED = True
        self.Refresh()

    def OnMouseLeave(self, evt):
        self._HOVERED = False
        self.Refresh()

    def _setSelected(self, evt):
        if not self._SELECTED:
            self._SELECTED = True
            self.GetGrandParent().setSelected(self)
            self.Refresh()
        else:
            if self._settings_win is not None:
                self._settings_win.Destroy()
                self._settings_win = None

    def ShowSettingsWin(self, evt):
        if self._settings_win is None:
            self._settings_win = PSDropDownMenu(self, state=self._data['STATE'],
                                                modified=self._data['MODIFIED'],
                                                is_user_patch=self._data['USER_PATCH'])
            self._setSettingsWinPosition()
            self._settings_win.Show()
        else:
            self._settings_win.Show(False)
            self._settings_win = None
        if not self._SELECTED:
            self._setSelected(evt)

    def _setSettingsWinPosition(self):
        if self._settings_win is not None:
            offset_x = self.GetSize()[0] - self._settings_win.GetSize()[0] - 5
            offset_y = self.GetSize()[1] - 5
            x, y = self.GetScreenPositionTuple()
            self._settings_win.SetPosition((x+offset_x,y+offset_y))

    def _validateData(self, data):
        final_dict = {}
        for key in data:
            if key in PATCH_ELEM_DATA_MODEL:
                if type(data[key]) == PATCH_ELEM_DATA_MODEL[key]:
                    final_dict[key] = data[key]
                else:
                    raise TypeError, "PSPatchElem: wrong type in data"
        return final_dict

    def deselect(self):
        self._SELECTED = False
        self.Refresh()

    def getType(self):
        return self._data['TYPE']

    def getName(self):
        return self._data['NAME']


class PSDropDownMenuItem(wx.Panel):
    _x_margin = 10
    _y_margin = 10

    def __init__(self, parent, text, pos, align):
        wx.Panel.__init__(self, parent, -1, pos, (-1,-1))
        wx.Panel.SetSize(self, self._getMinSize(text))

        self._bg_colour_norm = "#FFFFFF"
        self._bg_colour_hover = "#FFFFFF"
        self._align = 'left'

        self._text = wx.StaticText(self, -1, text, self._getTextPos(text))
        self._text.Bind(wx.EVT_LEFT_UP, self.ChildRedirectEvent)
        self._text.Bind(wx.EVT_ENTER_WINDOW, self.ChildRedirectEvent)
        self._text.Bind(wx.EVT_LEAVE_WINDOW, self.ChildRedirectEvent)
        self.SetAlign(align)

        self.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)

    def OnMouseEnter(self, evt):
        self.SetBackgroundColour(self._bg_colour_hover)

    def OnMouseLeave(self, evt):
        self.SetBackgroundColour(self._bg_colour_norm)

    def ChildRedirectEvent(self, evt):
        wx.PostEvent(self, evt)

    def SetAlign(self, align):
        align = align.lower()
        assert align in ('left', 'center', 'right'), "PSDropDownMenuItem.SetAlgin: align attribute must be either\
                                                      'left', 'center' or 'right'"
        self._align = align
        self._text.SetPosition(self._getTextPos(self._text.GetLabel()))
        self.Refresh()

    def SetSize(self, size):
        wx.Panel.SetSize(self, size)
        self._text.SetPosition(self._getTextPos(self._text.GetLabel()))
        self.Refresh()

    def SetText(self, text):
        self._text.SetLabel(text)
        min_w,min_h = self._getMinSize(text)
        w,h = self.GetSize()
        if w<min_w or h<min_h:
            self.SetSize((min_w, min_h))
        else:
            self._text.SetPosition(self._getTextPos(text))

    def SetNormBackgroundColour(self, colour):
        self._bg_colour_norm = colour
        self.SetBackgroundColour(colour)

    def SetHoverBackgroundColour(self, colour):
        self._bg_colour_hover = colour

    def SetTextColour(self, colour):
        self._text.SetForegroundColour(colour)

    def _getMinSize(self, text):
        dc = wx.ClientDC(self)
        w, h = dc.GetTextExtent(text)
        w += PSDropDownMenuItem._x_margin*2
        h += PSDropDownMenuItem._y_margin*2
        return (w,h)

    def _getTextPos(self, text):
        w,h = self.GetSize()
        dc = wx.ClientDC(self)
        tw, th = dc.GetTextExtent(text)
        y = (h-th)/2

        if self._align == 'left':
            return (PSDropDownMenuItem._x_margin, y)
        elif self._align == 'center':
            return ((w-tw)/2, y)
        elif self._align == 'right':
            return (w-tw-PSDropDownMenuItem._x_margin, y)


class PSDropDownMenu(wx.Frame):
    _size = (250, 120)
    _entry_height = 25

    def __init__(self, parent, state=0, modified=False, is_user_patch=False):
        wx.Frame.__init__(self, parent, id=-1, size=PSDropDownMenu._size,
                          style=wx.NO_BORDER | wx.FRAME_FLOAT_ON_PARENT)
        self._panel = wx.Panel(self, -1, (0,0), self.GetSize())

        self._background_colour = "#434343"
        self._hover_element_colour = "#686868"
        self._border_colour = "#848484"
        self._font = wx.Font(**PSConfig.FONTS['light']['norm'])

        self._panel.SetBackgroundColour(self._background_colour)

        self._entries = []
        if is_user_patch:
            self._entries.append(PSDropDownMenuItem(self._panel, 'Edit', (0,0), 'right'))
            self._entries[-1].Bind(wx.EVT_LEFT_UP, self.OnEditScript)
            self._entries.append(PSDropDownMenuItem(self._panel, 'Edit Metadata', (0,0), 'right'))
            self._entries[-1].Bind(wx.EVT_LEFT_UP, self.OnEditMetadata)
            self._entries.append(PSDropDownMenuItem(self._panel, 'Submit', (0,0), 'right'))
            self._entries[-1].Bind(wx.EVT_LEFT_UP, self.OnSubmitScript)
        else:
            if state in [1,2]:
                self._entries.append(PSDropDownMenuItem(self._panel, 'Edit', (0,0), 'right'))
                self._entries[-1].Bind(wx.EVT_LEFT_UP, self.OnEditScript)
            if modified:
                self._entries.append(PSDropDownMenuItem(self._panel, 'Revert to original', (0,0), 'right'))
                self._entries[-1].Bind(wx.EVT_LEFT_UP, self.OnRevertToOriginal)
        self._entries.append(PSDropDownMenuItem(self._panel, 'Delete', (0,0), 'right'))
        self._entries[-1].Bind(wx.EVT_LEFT_UP, self.OnDeletePatch)

        self._buildList()

        self._panel.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, evt):
        w,h = self.GetSize()
        dc = wx.PaintDC(self._panel)
        dc.SetPen(wx.Pen(self._border_colour, 1))
        dc.DrawLines([(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1), (0, 0)])

    def OnEditScript(self, evt):
        print 'Edit script'

    def OnEditMetadata(self, evt):
        print 'Edit Metadata'

    def OnSubmitScript(self, evt):
        print 'Submit script'

    def OnRevertToOriginal(self, evt):
        print 'Revert to original'

    def OnDeletePatch(self, evt):
        print 'Delete patch'

    def SetBackgroundColour(self, colour):
        self._panel.SetBackgroundColour(colour)

    def SetBorderColour(self, colour):
        self._border_colour = colour
        self.Refresh()

    def OnHoverMenuElement(self, evt):
        print 'hover'
        evt.GetEvenObject().SetBackgroundColour(self._hover_element_colour)

    def OnLeaveMenuElement(self, evt):
        evt.GetEvenObject().SetBackgroundColour(self._background_colour)

    def _setSize(self):
        h = len(self._entries) * PSDropDownMenu._entry_height + 2
        w = self._entries[0].GetSize()[0] + 2
        self.SetSize((w,h))
        self._panel.SetSize((w,h))

    def _buildList(self):
        widest = 0
        for i, obj in enumerate(self._entries):
            y = PSDropDownMenu._entry_height*i+1
            obj.SetPosition((1,y))
            if i % 2:
                obj.SetNormBackgroundColour("#22272b")
                obj.SetHoverBackgroundColour("#37424b")
            else:
                obj.SetNormBackgroundColour("#121416")
                obj.SetHoverBackgroundColour("#37424b")
            obj.SetTextColour("#e9e9e9")
            if obj.GetSize()[0] > widest:
                widest = obj.GetSize()[0]
        for obj in self._entries:
            obj.SetSize((widest, PSDropDownMenu._entry_height))
        self._setSize()



if __name__ == "__main__":
    app = wx.App()

    # test numbers
    # 0 = scroll bar
    # 1 = scrolled window
    # 2 = patches list
    test = 2

    if test == 0:
        frame = wx.Frame(None, -1, "Scroll Bar Test", (50,50), (100, 322))
        basepanel = wx.Panel(frame, -1, (0,0), (100,300))
        basepanel.SetBackgroundColour("#FFFFFF")
        sb = PSScrollBar(basepanel, -1, (0,0), 300, 500, bg_colour="#000000")

        def printPosX(evt):
            print evt.GetAbsolutePixelPosition()
        basepanel.Bind(EVT_SCROLL_MOTION, printPosX)
    elif test == 1:
        frame = wx.Frame(None, -1, "Scrolled Window Test", (50, 50), (200, 422))
        scroll_win = PSScrolledWindow(frame, -1, (0,0), (200,400))

        def OnResize(evt):
            w,h = frame.GetSize()
            scroll_win.SetSize((w,h-22))
        frame.Bind(wx.EVT_SIZE, OnResize)
    elif test == 2:
        frame = wx.Frame(None, -1, "Patches List Test", (50, 50), (330, 522))
        win = PatchesList(frame, -1, (0, 0), (330, 500))
        win.SetBackgroundColour("#12181d")
        data1 = {'TYPE':'Analog','NAME':'Analogica','VERSION':1,'STATE':0,'PACKAGE':'Default library','ID':12,
                 'MODIFIED':False, 'USER_PATCH':True}
        data2 = {'TYPE':'Digital','NAME':'Digital Wonders','VERSION':2, 'STATE':1,'PACKAGE':'Community library','ID':14,
                 'MODIFIED': True, 'USER_PATCH': False}
        data3 = {'TYPE':'Granular','NAME':'Granusynth','VERSION':5, 'STATE':0,'PACKAGE':'Community library','ID':25,
                 'MODIFIED': True, 'USER_PATCH': True}
        data4 = {'TYPE': 'booboo','NAME':'Bonobo Style','VERSION':1, 'STATE':2,'PACKAGE':'Modern sound','ID':2,
                 'MODIFIED': False, 'USER_PATCH': False}
        data5 = {'TYPE':'Percussive','NAME':'Perky Synth','VERSION':10,'STATE':1,'PACKAGE':'Modern sound','ID':123,
                 'MODIFIED': False, 'USER_PATCH': False}
        data6 = {'TYPE':'Real time processing','NAME':'RTPower','VERSION':3,'STATE':2,'PACKAGE':'Default library',
                 'ID':85, 'MODIFIED':False, 'USER_PATCH':True}
        data7 = {'TYPE':'Effects','NAME':'Super Badass Effect','VERSION':2,'STATE':0,'PACKAGE':'Effects vol. 1','ID':90,
                 'MODIFIED': False, 'USER_PATCH': False}
        data8 = {'TYPE':'Sampling','NAME':'Samples for all','VERSION':4,'STATE':0,'PACKAGE':'Default library','ID':74,
                 'MODIFIED': True, 'USER_PATCH': False}
        datas = []
        for i in range(37):
            datas.append(data1)
            datas.append(data2)
            datas.append(data3)
            datas.append(data4)
            datas.append(data5)
            datas.append(data6)
            datas.append(data7)
            datas.append(data8)
        win.addElements(datas)
        #win.setTypeFilters(['Analog','Granular','Digital'])
        #win.setTextFilter('Synth')
        #win.applyFilters()

        def OnResize(evt):
            w,h = frame.GetSize()
            win.SetSize((w,h-22))
        frame.Bind(wx.EVT_SIZE, OnResize)

    frame.Show()
    app.MainLoop()