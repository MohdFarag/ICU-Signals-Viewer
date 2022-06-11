# matplotlib
import matplotlib
import matplotlib.pyplot as plt
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
        self.axes.set_xlabel("Time")
        self.axes.set_ylabel("Frequency")
        
            
        self.data_channel = [0 for _ in range(500)]
        self.colorPalette = "binary"
        self.minContrast = 49
        self.maxContrast = 50
        
        # Color bar
        colormap = plt.cm.get_cmap(self.colorPalette)
        sm = plt.cm.ScalarMappable(cmap=colormap)
        self.colorBarSpectrogram = self.fig.colorbar(sm)
    
        super(MplCanvas, self).__init__(self.fig)
    
    def set_data_channel(self, data_channel):
        self.data_channel = data_channel

    def set_color(self, colorPalette):
        self.colorPalette = colorPalette

    def set_minContrast(self, minContrast):
        self.minContrast = minContrast - 100

    def set_maxContrast(self, maxContrast):
        self.maxContrast = maxContrast

    def plotSignal(self):
        fs = len(self.data_channel)   
        nfft = 10
        self.data_channel = np.array(self.data_channel)
        pxx,  freq, t, self.cax = self.axes.specgram(self.data_channel, nfft, fs, cmap=self.colorPalette, noverlap=nfft/3, mode="psd", vmin=self.minContrast,vmax=self.maxContrast)
        self.colorBarSpectrogram.update_normal(self.cax)
        self.draw()
        
    def clearSignal(self):
        self.axes.clear()