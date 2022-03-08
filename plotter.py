from PyQt5.QtCore import *
import pyqtgraph as pg
import pyqtgraph.exporters
from pyqtgraph.Qt import QtCore
from pyqtgraph.dockarea import *
import numpy as np
import pandas as pd

class signalPlotter(pg.GraphicsLayoutWidget()):

    def __init__(self, sampleinterval=0.1, timewindow=10., size=(600,350)):
        # Data stuff
        self._interval = int(sampleinterval*1000)
        
        self.time = list()
        self.data_channel_1 = [0]
        self.data_channel_2 = [0]
        self.data_channel_3 = [0]
        self.existChannel = [0, 0, 0]

        self.data_channel_live_1 = list()
        self.data_channel_live_2 = list()
        self.data_channel_live_3 = list()
        self.time_live = list()

        # PyQtGraph stuff
        self.PlotGraph = self.GrLayout.addPlot()
        self.PlotGraph.setTitle("Channels",color="w", size="18pt")
        self.PlotGraph.setLabel('bottom', 'Time', 's')
        self.PlotGraph.enableAutoRange(0.75, x=True, y=True)
        self.PlotGraph.setAutoVisible(x=True, y=True)
        self.PlotGraph.showGrid(x=True, y=True)
        self.legendItemName = self.PlotGraph.addLegend()

        data_line_channel1 = self.PlotGraph.plot(self.time_live, self.data_channel_live_1, name="Channel 1")
        data_line_channel2 = self.PlotGraph.plot(self.time_live, self.data_channel_live_2, name="Channel 2")
        data_line_channel3 = self.PlotGraph.plot(self.time_live, self.data_channel_live_3, name="Channel 3")
        
        # QTimer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updatePlot)
        self.timer.start(self._interval)


    # Main Plot
    def _updatePlot(self):
        self.incrementTimeAlongSignalRun = 0
        if self.existChannel[0] == 1 or self.existChannel[1] == 1 or self.existChannel[2] == 1 :
            self.timer = QtCore.QTimer()
            self.timer.setInterval((int(5*(100-self.speed))))
            self.timer.start()
            self.timer.timeout.connect(self.update_plot_data)

    def update_plot_data(self):
        if len(self.time_live) < len(self.time)-1:
            self.time_live.append(self.time[len(self.time_live)])
            self.incrementTimeAlongSignalRun += 1
            if self.existChannel[0] != 0 :
                self.data_channel_live_1.append(self.data_channel_1[len(self.time_live)])
                self.data_line_ch1.setData(self.time_live, self.data_channel_live_1)  # Update the data.
            elif self.existChannel[1] != 0 :
                self.data_channel_live_2.append(self.data_channel_2[len(self.time_live)])
                self.data_line_ch2.setData(self.time_live, self.data_channel_live_2)  # Update the data.
            elif self.existChannel[2] != 0 :
                self.data_channel_live_3.append(self.data_channel_3[len(self.time_live)])
                self.data_line_ch3.setData(self.time_live, self.data_channel_live_3)  # Update the data.
            
            self.setLimits()            
