#################################################################
#################################################################

# Author: martinja
# Contact: javier.martinez.samblas@cern.ch

# CODE OBTAINED FROM: https://github.com/pyqtgraph/pyqtgraph/pull/1574

#################################################################
#################################################################

# IMPORTS

from davit.__imports__ import *

#################################################################
#################################################################

class BigDataPlot(pg.PlotCurveItem):

    def __init__(self, *args, **kwds):
        self._plotData = None
        pg.PlotCurveItem.__init__(self, *args, **kwds)

    def setPlotData(self, plotData):
        self._plotData = plotData
        self.replot()

    def viewRangeChanged(self):
        self.replot(lazy=True)

    def replot(self, lazy=False):

        if self._plotData is None:
            self.setData([])
            return

        vb = self.getViewBox()
        if vb is None:
            return

        if not isinstance(vb, pg.ViewBox):
            return

        x1, x2 = vb.viewRange()[0]
        data = self._plotData.sample(x1, x2, lazy=lazy)

        if data is not None:
            self.setData(*data)

#################################################################
#################################################################

class PlotDataClass:

    def __init__(self, x, y, cache=None, chunk_size=100_000, app = None, name = ""):

        if x is None:
            x = len(y)
        elif len(x) != len(y):
            raise ValueError

        if not chunk_size:
            chunk_size = 100_000

        self._chunk_size = chunk_size
        self._app = app
        self._name = name

        if cache == "auto":
            cache = self.computeDownsampleCache(y)

        self._x = x
        self._y = y
        self._cache = cache
        self._lastRange = None

        return

    def sample(self, x1, x2, lazy=True, padding=0.3, **kwargs):

        i1, i2, ds = self.plotDataRange(self._x, x1, x2, padding=padding, **kwargs)

        if lazy and self._lastRange is not None:
            i11, i21, ds1 = self._lastRange
            i12, i22, _ = self.plotDataRange(self._x, x1, x2, padding=0, **kwargs)
            if (i11 <= i12 <= i22 <= i21) and (ds1 == ds):
                return

        i, y = self.downsample(data=self._y, start=i1, stop=i2, ds=ds, cache=self._cache)

        if isinstance(self._x, int):
            x = np.arange(i.start, i.stop, i.step)
        else:
            x = self._x[i]

        self._lastRange = (i1, i2, ds)

        return x, y

    def plotDataRange(self, x, x1, x2, padding=0.3, sampleLimit=2500, regularize=True):

        pad = (x2 - x1) * padding
        x1, x2 = x1 - pad, x2 + pad

        if isinstance(x, int):
            n = x
            i1 = max(0, min(n, int(x1)))
            i2 = max(0, min(n, int(x2)))
        else:
            n = len(x)
            i1, i2 = np.searchsorted(x, [x1, x2]).tolist()

        ds = max(1, (i2 - i1) // sampleLimit)

        if regularize:
            lv = ds.bit_length()
            ds = 2 ** lv
            i1 = (i1 // ds - 1) * ds
            i2 = (i2 // ds + 1) * ds
            i1 = max(0, min(n, i1))
            i2 = max(0, min(n, i2))

        return i1, i2, ds

    def downsample(self, data, start, stop, ds, cache=None, **kwargs):

        if not (0 <= start < stop <= len(data)):
            raise ValueError
        if ds <= 2:
            dat = data[start:stop]
            idx = slice(start, stop)
        else:
            if cache is not None and ds in cache:
                dat = cache[ds][2 * start // ds: 2 * stop // ds + 1]
            else:
                dat = self._downsample(data=data, start=start, stop=stop, ds=ds, **kwargs)
            idx = slice(start, start + len(dat) * ds // 2, ds // 2)

        return idx, dat

    def _downsample(self, data, start, stop, ds):

        # CHAT-GPT FIXED
        # The issue seems to be that the 'visible' array can be partially unfilled with zeros at the end.
        # This can happen when the last chunk of data is not fully filled. To fix this, you should create
        # a 'visible' array that only contains the final size needed. You can calculate the final size of the
        # 'visible' array by using the 'targetPtr' value after the loop. The updated version of the code creates
        # a 'temp_visible' array that has the same initial size as before but then slices it to only include
        # the filled portion before returning it as 'visible'. This should prevent the zeros from appearing at
        # the end of the output.

        samples = 1 + ((stop - start) // ds)
        temp_visible = np.zeros(samples * 2, dtype=data.dtype)
        sourcePtr = start
        targetPtr = 0
        chunk_size = (self._chunk_size // ds) * ds

        while sourcePtr < stop:
            chunk = data[sourcePtr: min(stop, sourcePtr + chunk_size)]
            sourcePtr += len(chunk)

            if len(chunk) % ds != 0:
                tail = np.full(ds - len(chunk) % ds, chunk[-1])
                chunk = np.append(chunk, tail)

            chunk = chunk.reshape(len(chunk) // ds, ds)

            chunkMax = chunk.max(axis=1)
            chunkMin = chunk.min(axis=1)

            temp_visible[targetPtr: targetPtr + chunk.shape[0] * 2: 2] = chunkMin
            temp_visible[1 + targetPtr: 1 + targetPtr + chunk.shape[0] * 2: 2] = chunkMax
            targetPtr += chunk.shape[0] * 2

        visible = temp_visible[:targetPtr]

        return visible

    # def _downsample(self, data, start, stop, ds):
    #
    #     samples = 1 + ((stop - start) // ds)
    #     visible = np.zeros(samples * 2, dtype=data.dtype)
    #     sourcePtr = start
    #     targetPtr = 0
    #     chunk_size = (self._chunk_size // ds) * ds
    #
    #     while sourcePtr < stop:
    #         chunk = data[sourcePtr: min(stop, sourcePtr + chunk_size)]
    #         sourcePtr += len(chunk)
    #
    #         if len(chunk) % ds != 0:
    #             tail = np.full(ds - len(chunk) % ds, chunk[-1])
    #             chunk = np.append(chunk, tail)
    #
    #         chunk = chunk.reshape(len(chunk) // ds, ds)
    #
    #         chunkMax = chunk.max(axis=1)
    #         chunkMin = chunk.min(axis=1)
    #
    #         visible[targetPtr: targetPtr + chunk.shape[0] * 2: 2] = chunkMin
    #         visible[1 + targetPtr: 1 + targetPtr + chunk.shape[0] * 2: 2] = chunkMax
    #         targetPtr += chunk.shape[0] * 2
    #
    #     return visible

    def computeDownsampleCache(self, data, minLevelSize=2500, maxLevelSize=10_000_000, use_progress_bar = True):

        minLevel = max(2, (len(data) // maxLevelSize).bit_length())
        maxLevel = (len(data) // minLevelSize).bit_length()

        if use_progress_bar:
            self.progress_dialog = QProgressDialog("Precomputing downsample cache for curve {}...".format(self._name), None, 0, len(range(minLevel, maxLevel + 1)))
            self.progress_dialog.setMaximumHeight(300)
            self.progress_dialog.setMaximumWidth(1000)
            self.progress_dialog.setMinimumHeight(75)
            self.progress_dialog.setMinimumWidth(600)
            self.progress_dialog.setAutoClose(False)
            self.progress_dialog.setWindowModality(Qt.ApplicationModal)
            self.progress_dialog.closeEvent = closeEventIgnore
            self.progress_dialog.setWindowTitle("Progress")
            self.progress_dialog.setWindowIcon(qta.icon("mdi6.timer-sand"))
            self.progress_dialog.show()
            self.progress_dialog.repaint()
            self._app.processEvents(QEventLoop.ExcludeUserInputEvents)
            self.progress_dialog.setValue(0)
            self.progress_dialog.repaint()
            self._app.processEvents(QEventLoop.ExcludeUserInputEvents)

        out = {}
        dat = None
        for c_lv, lv in enumerate(range(minLevel, maxLevel + 1)):

            ds = 2 ** lv
            if dat is None:
                dat = self._downsample(data=data, start=0, stop=len(data), ds=ds)
            else:
                dat = self._downsample(data=dat, start=0, stop=len(dat), ds=4)
            out[ds] = dat

            if use_progress_bar:
                self.progress_dialog.setValue(c_lv)
                self.progress_dialog.repaint()
                self._app.processEvents(QEventLoop.ExcludeUserInputEvents)

        if use_progress_bar:
            self.progress_dialog.close()
            del self.progress_dialog

        return out

#################################################################
#################################################################