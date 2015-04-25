from pyo import NewTable, TableRec, TrigFunc, Spectrum, Sine
import wx, math, utils, buttons, controls

class PSSpectrum(wx.Panel):
    """
    Basic spectrum analyser showing the frequencies contained in a signal over time.
    
    attributes :    parent : The parent wx.Window object.
                    pos : Relative position of the spectrum within the parent.
                    size : Size of the spectrum window.
                    signal : Sound source used for the analysis.
                    sr : Sampling rate of the sound used in analysis.
    
    methods :       reinit(PyoObject signal, int sr {22050>=x=<192000})
                    setSize(int size {2**x, x>2})
                    setWinType(int type {0->8})
                    setGain(float gain {0>=x})
                    setSamplingRate(int sr {22050>=x=<192000})
                    int getSize()
                    int getWinType()
                    int getGain()
    """
    def __init__(self, parent, pos, size, signal, sr, nchnls=None):
        wx.Panel.__init__(self, parent, -1, pos, size)
        self.SetBackgroundColour("#000000")
        
        self._chnl_text_colours = ["#2696A2","#C47934","#B534C4","#6CFF00"]
        self._pen_colours = ["#132E31","#AA6F39","#AC46BB","#56BB46"]
        self._getBrushColours()
        if signal == None:
            self._sig = Sine([100*i for i in range(nchnls)])
        else:
            self._sig = signal
        self._chnls = len(self._sig)
        self._sr = sr
        self._initPoints()
        self._drawBackground()
        
        self._analysis = Spectrum(self._sig, 2048, wintype=2, function=self._getPoints).stop()
        self._analysis.setFscaling(True)
        self._analysis.setMscaling(True)
        w,h = size
        self._analysis.setWidth(w)
        self._analysis.setHeight(h)
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        
    def reinit(self, signal, sr, nchnls=None):
        if signal == None:
            self._sig = Sine([100*i for i in range(nchnls)])
        else:
            self._sig = signal
        self._sr = sr
        self._chnls = len(self._sig)
        self._drawBackground()
        self._analysis = Spectrum(self._sig, 2048, wintype=2, function=self._getPoints).stop()
        self._analysis.setFscaling(True)
        self._analysis.setMscaling(True)
        w,h = self.GetSize()
        self._analysis.setWidth(w)
        self._analysis.setHeight(h)
    
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self._bg,0,0)
        for i in range(self._chnls):
            dc.SetPen(wx.Pen(self._pen_colours[i], 1))
            dc.DrawLines(self._points[i])
            dc.SetBrush(wx.Brush(self._brush_colours[i]))
            dc.DrawPolygon(self._points[i])
        
    def OnQuit(self, evt):
        self.Destroy()
        
    def Show(self, show):
        wx.Panel.Show(self, show)
        if show:
            self.start()
        else:
            self.stop()
            
    def Destroy(self):
        self._analysis.stop()
        wx.Panel.Destroy(self)

    def _drawBackground(self):
        w,h = self.GetSize()
        self._bg = wx.EmptyBitmap(w,h)
        self._calcFreqIndicators()
        dc = wx.MemoryDC(self._bg)
        pen = wx.Pen("#3d3d3d", 1, wx.USER_DASH)
        pen.SetDashes([5,3])
        dc.SetPen(pen)
        dc.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, faceName="Helvetica"))
        dc.SetTextForeground("#c7c7c7")
        
        # -----------------------------------
        # dessin des indicateurs de frequence
        # -----------------------------------
        
        #calcul du range des exposants de 20Hz a sr/2.
        min_exp = math.log10(20)
        max_exp = math.log10(self._sr/2.)
        range_exp = max_exp-min_exp
        for i in range(len(self._freq_indicators)):
            exp = math.log10(self._freq_indicators[i])
            x = (exp-min_exp)/range_exp*w
            dc.DrawLine(x,1,x,h)
            if exp.is_integer():
                txt = str(int(self._freq_indicators[i]))
                dc.DrawText(txt,x+3,5)
        
        # -----------------------------------
        # dessin des indicateurs d'amplitude
        # -----------------------------------
        pen.SetDashes([1,4])
        dc.SetPen(pen)
        step = h/13.
        for i in range(1,13,2):
            dc.DrawLine(0,step*i,w,step*i)
            db = 20*math.log(1.3-i/10.)
            txt = "%.2f dB" % db
            x,y = dc.GetTextExtent(txt)
            dc.DrawText(txt,w-x-3,step*i)
            
        # ----------------------------
        # dessin des couleurs de canal
        # ----------------------------
        for i in range(self._chnls):
            dc.SetTextForeground(self._chnl_text_colours[i])
            txt = "chnl %d" % (i+1)
            dc.DrawText(txt,10,10*i+12)
        
    def _calcFreqIndicators(self):
        """
        Construit une liste de frequences entre 20Hz et sr/2.-5000 Hz
        """
        self._freq_indicators = []
        for i in range(1,5):
            for j in range(1,10):
                freq = math.pow(10, i)*j
                if freq > 20. and freq <= self._sr/2.-5000:
                    self._freq_indicators.append(freq)
        
    def _initPoints(self):
        """
        Initialise la liste de points pour OnPaint.
        """
        self._points = []
        for i in range(self._chnls):
            self._points.append([(0,400),(500,400)])
    
    def _getPoints(self, points):
        """
        Recoit les points de l'objet Spectrum et deplace les
        deux premiers points en dehors de la fenetre.
        """
        self._points = points
        for i in range(self._chnls):
            self._points[i][0] = (-1,self.GetSize()[1])
            self._points[i][1] = (-1,self._points[i][1][1])
        wx.CallAfter(self.Refresh)
        
    def _getBrushColours(self):
        """
        Utilise les couleurs des wx.Pen pour creer
        ceux des wx.Brush avec de la transparence.
        """
        self._brush_colours = []
        for i in range(len(self._pen_colours)):
            b = wx.Brush(self._pen_colours[i])
            r,g,b = b.GetColour().Get()
            self._brush_colours.append((r,g,b,50))
            
    def start(self):
        self._analysis.play()
        print 'start'
    
    def stop(self):
        self._analysis.stop()
        self._initPoints()
        wx.CallAfter(self.Refresh)
        print 'stop'
        
    def setInput(self, input):
        self._analysis.setInput(input)
        self._chnls = len(input)
        self._initPoints()
        self._drawBackground()
        wx.CallAfter(self.Refresh)
    
    def setSize(self, size):
        """
        Sets the size in samples of the analysis window.
        Number must be a power of 2 greater than 4.
        """
        self._analysis.setSize(size)
        
    def setWinType(self, type):
        """
        Sets the window type used during analysis.
        Choices are :
            0. rectangular (no windowing)
            1. Hamming
            2. Hanning
            3. Bartlett (triangular)
            4. Blackman 3-term
            5. Blackman-Harris 4-term
            6. Blackman-Harris 7-term
            7. Tuckey (alpha = 0.66)
            8. Sine (half-sine window)
        """
        self._analysis.setWinType(type)
        
    def setGain(self, gain):
        """
        Sets the gain for the analysis.
        """
        self._analysis.setGain(gain)
        
    def setSamplingRate(self, sr):
        """
        Sets the new sampling rate value.
        It's important to call this function if the sampling rate changes
        during runtime to ensure that the frequencies shown are correct.
        """
        self._sr = sr
        self._drawBackground()
        
    def getSize(self):
        return self._analysis._size
        
    def getWinType(self):
        return self._analysis._wintype
        
    def getGain(self):
        return self._analysis._gain

class PSSpectrumWrapper(wx.Panel):
    """
    Simple wrapper for the spectrum class that is used to draw the title bar
    and add controls to help configure the spectrum.
    """
    def __init__(self, parent, pos, size, signal, sr, nchnls=None):
        self._banner_height = 26
        self._controls_height = 21
        wx.Panel.__init__(self, parent, -1, pos, (size[0],size[1]+self._banner_height+self._controls_height), style=wx.NO_BORDER)
        
        self._spectrum = PSSpectrum(self, (0,self._banner_height), size, signal, sr, nchnls)
        
        self._colors = utils.getTransparentColour(50, "#C29024", "#F49500")
        
        #init buttons and win size
        self._createButtons([256,512,1024,2048,4096])
        self._activeButton = self._winSizeButtons[3]
        self._activeButton.SetState(1)
        self._spectrum.setSize(self._activeButton.GetValue())
        
        self._gain = 1.
        self._maxGain = 2.
        self._slider = controls.VolumeSlider(self, (85,size[1]+self._banner_height+5), 130, self._gain/self._maxGain)
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(buttons.EVT_BTN_CLICKED, self.OnWinSizeChange)
        self.Bind(controls.EVT_VOL_CHANGED, self.OnGainChange)
        
    def reinit(self, signal, sr, nchnls=None):
        self._spectrum.reinit(signal, sr, nchnls)
        self._spectrum.setSize(self._activeButton.GetValue())
        self._spectrum.setGain(self._gain)

    def OnPaint(self, evt):
        w,h = self.GetSize()
        dc = wx.PaintDC(self)
        dc.SetBrush(wx.Brush(self._colors[0]))
        dc.SetPen(wx.Pen(self._colors[1], 1))
        dc.SetClippingRegion(0,0,w,self._banner_height)
        dc.DrawRoundedRectangle(0,0,w,self._banner_height+3, 3)
        dc.DestroyClippingRegion()
        dc.DrawLine(0,self._banner_height-1,w,self._banner_height-1)
        dc.SetTextForeground("#CFCFCF")
        font = wx.Font(13, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, faceName="Helvetica")
        dc.SetFont(font)
        dc.DrawText("SPECTRUM DISPLAY",8,9)
        font.SetPointSize(10)
        dc.SetFont(font)
        txt = "Gain : %.2fdB" % (20*math.log10(self._gain+.000001))
        dc.DrawText(txt,0,h-self._controls_height+8)
        dc.DrawText("Window size",285,h-self._controls_height+8)
        
    def OnWinSizeChange(self, evt):
        btn = evt.GetEventObject()
        if btn != self._activeButton:
            self._activeButton.SetState(0)
            self._activeButton = btn
            self._spectrum.setSize(self._activeButton.GetValue())
            
    def OnGainChange(self, evt):
        self._gain = self._slider.getValue()*self._maxGain
        self._spectrum.setGain(self._gain)
        wx.CallAfter(self.Refresh)
        
    def Show(self, show):
        self._spectrum.Show(show)
        wx.Panel.Show(self, show)
        
    def _createButtons(self, values):
        w,h = self.GetSize()
        size = buttons.RectangleButton.size
        x = w-((size[0]+2)*len(values))
        y = h-self._controls_height+6
        self._winSizeButtons = []
        for i in range(len(values)):
            self._winSizeButtons.append(buttons.RectangleButton(self, (x,y), values[i]))
            x += size[0]+2

    def start(self):
        self._spectrum.start()
    
    def stop(self):
        self._spectrum.stop()
        
    def setInput(self, input):
        self._spectrum.setInput(input)
    
    def setSize(self, size):
        self._spectrum.setSize(size)
        
    def setWinType(self, type):
        self._spectrum.setWinType(type)
        
    def setGain(self, gain):
        self._spectrum.setGain(gain)
        
    def setSamplingRate(self, sr):
        self._spectrum.setSamplingRate(sr)
        
    def getSize(self):
        return self._spectrum.getSize()
        
    def getWinType(self):
        return self._spectrum.getWinType()
        
    def getGain(self):
        return self._spectrum.getGain()

class PSScope(wx.Panel):
    """
    Scope allows you to see the amplitude of a signal over time.
    
    attributes :    parent : The parent wx.Window object.
                    pos : Relative position of the spectrum within the parent.
                    size : Size of the spectrum window.
                    signal : Sound source used for the analysis.
                    rate : Duration of an analysis frame in seconds.
                    
    methods :       start()
                    stop()
                    setVZoom(float x {x>0})
                    setHZoom(float x {x>=1})
                    setRate(float s)
                    float getVZoom()
                    float getHZoom()
    """
    def __init__(self, parent, pos, size, signal, rate=1/25., nchnls=None):
        assert rate>0, "'rate' attribute must be greater than 0."
        wx.Panel.__init__(self, parent, -1, pos, size)
        self.SetMinSize((200,150))
        self.SetBackgroundColour("#000000")
        if signal == None:
            self._sig = Sig([0 for i in range(nchnls)])
        else:
            self._sig = signal
        self._chnls = len(self._sig)
        self._chnl_space = 4
        self._calcChnlHeight()
        self._hzoom = 1
        self._vzoom = 1
        self.RUNNING = False
        
        self._table = NewTable(rate, self._chnls)
        self._tablerec = TableRec(self._sig, self._table)
        self._trigDraw = TrigFunc(self._tablerec['trig'], self._processBuffer)
        
        self._initPoints()
        self._drawBackground()
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        
    def reinit(self, signal, rate=1/25.):
        self._tablerec.stop()
        self._sig = signal
        self._chnls = len(signal)
        self._calcChnlHeight()
        self._table = NewTable(rate, self._chnls)
        self._tablerec = TableRec(self._sig*self._vzoom, self._table)
        self._trigDraw = TrigFunc(self._tablerec['trig'], self._processBuffer)
        self._drawBackground()
        self.start()
    
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        self.Draw(dc)
        
    def Draw(self, dc):
        w, h = self.GetSize()
        dc.DrawBitmap(self._bg,0,0)
        dc.SetPen(wx.Pen("#248282", 1))
        
        for i in range(self._chnls):
            y_offset=self._chnl_space*i
            dc.DrawLines(self._points[i], yoffset=y_offset)
        
    def OnQuit(self, evt):
        self.Destroy()
        
    def Show(self, show):
        wx.Panel.Show(self, show)
        if show:
            self.start()
        else:
            self.stop()
            
    def Destroy(self):
        self.stop()
        wx.Panel.Destroy(self)
        
    def _drawBackground(self):
        w,h = self.GetSize()
        y_offset = self._chnl_height+self._chnl_space
        self._bg = wx.EmptyBitmap(w,h)
        dc = wx.MemoryDC(self._bg)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour().Get()))
        dc.Clear()
        
        #------------------------------
        # drawing the channel separators
        #------------------------------
        if self._chnls>1:
            dc.SetPen(wx.Pen("#242424", self._chnl_space))
            for i in range(1, self._chnls):
                y = self._chnl_height+self._chnl_space/2+(y_offset*(i-1))
                dc.DrawLine(0, y, w, y)
        
        #setting up the dc for the vertical lines
        dc.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, faceName="Helvetica"))
        dash_pen = wx.Pen("#242424", 1, wx.USER_DASH)
        dash_pen.SetDashes([5,3])
        norm_pen = wx.Pen("#242424",1)
        
        #duree de la fenetre en milisecondes
        ms = self._table.getLength()*1000/self._hzoom
        
        #------------------------------
        # draws the time indicators
        #------------------------------
        for i in range(self._chnls):
            offset = y_offset*i
            txt = "Chnl %d" % (i+1)
            dc.SetTextForeground("#248282")
            dc.DrawText(txt, 6, offset+self._chnl_height*.09)
            mid = self._chnl_height/2+offset
            dc.SetPen(norm_pen)
            dc.DrawLine(0,mid,w,mid)
            dc.SetPen(dash_pen)
            for i in range(1,6):
                if i!=1 or i!=5:
                    dc.DrawLine(w*i/5,offset,w*i/5,self._chnl_height+offset)
                txt = "%d ms" % int(ms*(i-1)/5+.5)
                dc.SetTextForeground("#c7c7c7")
                dc.DrawText(txt, w*(i-1)/5+3, self._chnl_height+offset-13)

    def _calcChnlHeight(self):
        #+.5 pour arrondir le resultat
        self._chnl_height = int(self.GetSize()[1]/self._chnls - self._chnl_space*(self._chnls-1)/self._chnls + .5)
    
    def _initPoints(self):
        """
        Initializes the points lists with straight lines.
        """
        self._points = []
        for i in range(self._chnls):
            x = self.GetSize()[0]
            mid = self._chnl_height/2 + self._chnl_height*i
            self._points.append([(0,mid),(x,mid)])
    
    def _processBuffer(self):
        """
        Gets the points list and adjusts them according to zoom values.
        """
        w = self.GetSize()[0]
        h = self._chnl_height*self._chnls
        self._points = self._table.getViewTable((w*self._hzoom,h))
        self._clipPoints()
        wx.CallAfter(self.Refresh)
        self._tablerec.play()
                
    def _clipPoints(self):
        """
        Clips the points so they are not drawn outside the window.
        """
        #deletes points that are outside the size of the window
        #so they are not drawn uselessly
        if self._hzoom > 1:
            for i in range(self._chnls):
                del self._points[i][self.GetSize()[0]+1:-1]
        #this loop makes sure no lines are drawn
        #outside the limits of the channel
        for i in range(self._chnls):
            for j in range(len(self._points[i])):
                x,y = self._points[i][j]
                if y < self._chnl_height*i: y=self._chnl_height*i
                if y > self._chnl_height*(i+1): y=self._chnl_height*(i+1)
                self._points[i][j] = (x,y)
                    
    def start(self):
        """
        Start the scope.
        """
        self._trigDraw.play()
        self._tablerec.play()
        self.RUNNING = True
        
    def stop(self):
        """
        Stops the scope. (Good to save on cpu usage)
        """
        self._trigDraw.stop()
        self._initPoints()
        self.RUNNING = False
        wx.CallAfter(self.Refresh)
        
    def setInput(self, input):
        self.__tablerec.setInput(input*self._vzoom)
        self._sig = input
        self._chnls = len(input)
        self._calcChnlHeight()
        self._initPoints()
        self._drawBackground()
        wx.CallAfter(self.Refresh)
        
    def setHZoom(self, x):
        """
        Sets the horizontal zoom.
        Value must be greater than 1.
        """
        if x<1: x=1
        self._hzoom = x
        self._drawBackground()
            
    def setVZoom(self, x):
        """
        Sets the vertical zoom or linear gain of the analysis.
        Value must be greater than 0.
        """
        if x<0: x=0
        self._vzoom = x
        self._tablerec.setInput(self._sig*self._vzoom)
        
    def setRate(self, rate):
        """
        Sets the rate at which the table is refreshed.
        This changes the size of the table.
        """
        self.reinit(self._sig, rate)
        
    def getHZoom(self):
        """
        Returns the value of the horizontal zoom.
        """
        return self._hzoom
        
    def getVZoom(self):
        """
        Return the value of the vertical zoom.
        You can convert this to dB using 20*log10(x).
        """
        return self._vzoom