import wx
import math
import PSUtils

class AnimationBase(wx.Panel):
    def __init__(self, parent, id, pos, size, rate):
        wx.Panel.__init__(self, parent, id, pos, size)
        self._getTimeFromRate = lambda x: 1./float(x)*1000
        self._getRateFromTime = lambda x: 1./(x/1000.)
        self._time = self._getTimeFromRate(rate)
        self._timer = wx.Timer(self)
        self._RUN = False
        self._WAIT_FOR_FRAME_COUNT = False
        self._frame = 0

        self.Bind(wx.EVT_TIMER, self._onTimerEvent)

    def OnFrame(self, frameId):
        """To be overridden by children class"""
        pass

    def _onTimerEvent(self, evt):
        if self._RUN:
            self.OnFrame(self._frame)
            wx.CallAfter(self.Refresh)
            self._frame += 1
        else:
            self._timer.Stop()

        if self._WAIT_FOR_FRAME_COUNT:
            if self._frame % self._getRateFromTime(self._time) == 1:
                self._RUN = False

    def start(self, *args, **kwargs):
        self._RUN = True
        self._timer.Start(self._time)

    def stop(self, *args, **kwargs):
        self._RUN = False

    def stopAfter(self, *args, **kwargs):
        self._WAIT_FOR_FRAME_COUNT = True

    def setRate(self, rate):
        self._time = self._getTimeFromRate(rate)

    def getRate(self):
        return self._getRateFromTime(self._time)


class RotateAnimation(AnimationBase):
    _margin = 2
    """
    class RotateAnimation
    
    Rotates a bitmap by a predefined step at a predefined rate.

    :Parent: :py:class:'AnimationBase'

    :Args:

        parent: wx.Window
            Parent window containing the animation.
        pos: int
            Relative position to the parent window.
        bmp: wx.Bitmap
            Bitmap image subject to rotation.
        rate: int or float
            Refresh rate in frame/sec.
        step: int or float
            The angle of rotation in degrees that will be added to the image at every frame.
    """
    def __init__(self, parent, pos, bmp, rate, step):
        assert bmp.GetSize()[0]&1 == 1 and bmp.GetSize()[1]&1 == 1,\
            "Bitmap must have odd width and height sizes to perform accurate rotation around the center"
        w,h = bmp.GetSize()
        AnimationBase.__init__(self, parent, -1, pos, (w + RotateAnimation._margin, h + RotateAnimation._margin), rate)
        self._bmp = bmp
        self._bmp_size = bmp.GetSize()
        self._img = bmp.ConvertToImage()
        self._center_point = wx.Point(bmp.GetSize()[0]/2+1,bmp.GetSize()[1]/2+1)
        self._rotation_delta = step*math.pi/180
        self._current_radian = 0

        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, evt):
        print self._getBitmapPosition()
        dc = wx.PaintDC(self)
        margin = RotateAnimation._margin/2
        dc.DrawBitmap(self._bmp, 0+margin, 0+margin)

    def OnFrame(self, frameId):
        self._current_radian += self._rotation_delta
        if self._current_radian > 2. * math.pi:
            self._current_radian = self._rotation_delta
        self._bmp = self._img.Rotate(self._current_radian, self._center_point).ConvertToBitmap()

    def SetBackgroundColour(self, colour):
        self._img.SetMaskColour(*PSUtils.convertHexToRGB(colour))
        AnimationBase.SetBackgroundColour(self, colour)

    def _getBitmapPosition(self):
        """Return the bitmap's position according to current angle of rotation"""
        if self._current_radian < (math.pi / 2.):
            return self._getPosFirstAndThirdQuadrant()
        elif self._current_radian < math.pi:
            return self._getPosSecondAndFourthQuadrant()
        elif self._current_radian < (3. * math.pi / 2.):
            return self._getPosFirstAndThirdQuadrant()
        elif self._current_radian < (2. * math.pi):
            return self._getPosSecondAndFourthQuadrant()

    def _getPosFirstAndThirdQuadrant(self):
        bw, bh = self._bmp_size
        org_rad = math.atan((bh/2.) / (bh/2.))
        hypothenuse = (bw / 2.) / math.cos(self._current_radian)


    def _getPosSecondAndFourthQuadrant(self):
        pass


if __name__ == '__main__':
    app = wx.App(False)
    frame = wx.Frame(None, -1, "Animation Test", (50,50), (100,122))
    basepanel = wx.Panel(frame, -1, (0,0), (100,100))
    bitmap = wx.Bitmap('/Users/alex/OneDrive/Pyo Synth - old dev/img/controls/update-btn/update-btn.gif')
    animtest = RotateAnimation(basepanel, (0,0), bitmap, 30, 10)
    animtest.SetBackgroundColour('#12181d')
    frame.Show()
    animtest.start()
    app.MainLoop()