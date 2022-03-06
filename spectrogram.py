# matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from random import randint

class MplCanvas(FigureCanvasQTAgg):
    
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.set_title("Spectrogram", fontweight ="bold")
        self.axes.set_xlabel("time (in seconds)")
        self.axes.set_ylabel("frequency")
        #self.fig.colorbar(cax).set_label('Intensity [dB]')
        super(MplCanvas, self).__init__(self.fig)
    
    data_channel = [0 for i in range(500)]
    colorPalette = "gray"
    minContrast = -50
    maxContrast = 50

    def set_data_channel(self, data_channel):
        self.data_channel = data_channel

    def set_color(self, colorPalette):
        self.colorPalette = colorPalette

    def set_minContrast(self, minContrast):
        self.minContrast = minContrast - 100

    def set_maxContrast(self, maxContrast):
        self.maxContrast = maxContrast

    def plotSignal(self):
        fs = 400
        nfft = 400
        self.data_channel = np.array(self.data_channel)
        pxx,  freq, t, cax = self.axes.specgram(self.data_channel, nfft, fs, cmap=self.colorPalette, noverlap=nfft/2, mode="psd", vmin=self.minContrast,vmax=self.maxContrast)
        self.draw()
        