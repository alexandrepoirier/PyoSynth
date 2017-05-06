import sys
if sys.platform == 'linux2':
    from pyo64 import *
else:
    from pyo import *
import math

class NuttallTable(PyoTableObject):
    def __init__(self, size):
        PyoTableObject.__init__(self, size)
        self._table = DataTable(size)
        self._table.replace(self._createNuttallWindow(size))
        self._base_objs = self._table.getBaseObjects()
        
    def _createNuttallWindow(self, size):
        list = []
        for i in range(size):
            list.append(self._nuttallFunction(i, size))
        return list
        
    def _nuttallFunction(self, x, N):
        a0, a1, a2, a3 = (0.355768, 0.487396, 0.144232, 0.012604)
        y = a0 - a1*math.cos( (2*math.pi*x) / (N-1) ) + a2*math.cos( (4*math.pi*x) / (N-1) ) - a3*math.cos( (6*math.pi*x) / (N-1) )
        return y
