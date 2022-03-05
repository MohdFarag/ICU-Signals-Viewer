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
        self.axes.set_title("Spectrogram",fontweight ="bold")
        super(MplCanvas, self).__init__(self.fig)
    
    data_channel = list()
    colorPalette = "Reds"
    minContrast = 50
    maxContrast = 100

    def set_data_channel(self, data_channel):
        self.data_channel = data_channel

    def set_color(self, colorPalette):
        self.colorPalette = colorPalette

    def set_minContrast(self, minContrast):
        self.minContrast = minContrast

    def set_minContrast(self, maxContrast):
        self.maxContrast = maxContrast

    def plotSignal(self):
        fs = 400
        nfft = 400
        self.data_channel = np.array(self.data_channel)
        self.axes.specgram(self.data_channel, nfft, fs, mode='magnitude',cmap=self.colorPalette, noverlap=nfft/2)
        self.draw()