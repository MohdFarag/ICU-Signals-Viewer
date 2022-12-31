# !/usr/bin/python

import sys
# importing Qt widgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.Qt import QFileInfo

# import fitz
from fitz import fitz, Rect

# importing numpy and pandas
import numpy as np
import pandas as pd

# importing PyQtGraph
import pyqtgraph as pg
import pyqtgraph.exporters
from pyqtgraph.Qt import QtCore
from pyqtgraph.dockarea import *

import os
from functools import partial

#Import spectrogram.py class
import spectrogram


class Window(QMainWindow):
    """Main Window."""
    def __init__(self):
        
        """Initializer."""
        super().__init__()
        self.timer = QtCore.QTimer()
        """Variables"""
        self.path = None # path of opened signal file
        self.time = [i for i in range(0,500)]
        self.data_channel_1 = [0]
        self.data_channel_2 = [0]
        self.data_channel_3 = [0]
        self.existChannel = [0, 0, 0]
        self.plotStatus = True

        self.data_channel_live_1 = list()
        self.data_channel_live_2 = list()
        self.data_channel_live_3 = list()
        self.time_live = list()

        self.speed = 50
        
        """main properties"""
        # setting icon to the window
        self.setWindowIcon(QIcon('images/icon.png'))
        
        # setting title
        self.setWindowTitle("ICU Signal Viewer")

        # UI contents
        self._createMenuBar()
        self.initUI()
        
        # Status Bar
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet("font-size:13px; padding: 3px; color: black; font-weight:900")
        self.statusBar.showMessage("Welcome to our application...")
        self.setStatusBar(self.statusBar)

    def initUI(self):
        """Window GUI contents"""
        wid = QWidget(self)
        self.setCentralWidget(wid)
        # setting configuration options
        pg.setConfigOptions(antialias=True)

        # big Layout
        outerLayout = QVBoxLayout()

        ControlsLayout = QHBoxLayout()

        # Create a layout for the plots
        plotsLayout = QVBoxLayout()

        # creating graphics layout widget
        self.GrLayout = pg.GraphicsLayoutWidget()
        self.PlotGraph = self.GrLayout.addPlot()
        self.PlotGraph.setTitle("Channels",color="white", size="18pt")
        self.PlotGraph.setLabel('bottom', 'Time', 's')
        
        self.GrLayout.setBackground('#222831')
        self.PlotGraph.getAxis('left').setPen("#EEEEEE")
        self.PlotGraph.getAxis('bottom').setPen("#EEEEEE")
        
        # Add legend
        self.legendItemName = self.PlotGraph.addLegend()
        self.legendItemName.anchor(1,1)
        # Plot and return the line of the signal to manipulate it.
        self.data_line_ch1 = self.PlotGraph.plot(self.time_live, self.data_channel_live_1, name="Channel 1", pen="w")
        self.data_line_ch2 = self.PlotGraph.plot(self.time_live, self.data_channel_live_2, name="Channel 2", pen="w")
        self.data_line_ch3 = self.PlotGraph.plot(self.time_live, self.data_channel_live_3, name="Channel 3", pen="w")
        # Set shadow to the channels
        self.data_line_ch1.setShadowPen("pink")
        self.data_line_ch2.setShadowPen("red")
        self.data_line_ch3.setShadowPen("yellow")
        # Update The plot
        self._updatePlot()

        # Create a layout for the main buttons
        mainButtonsLayout = QHBoxLayout()

        mainButtonsLayout.addSpacerItem(QSpacerItem(250, 10, QSizePolicy.Expanding))

        # Main buttons to manipulate the plot
        def signalSpeed(increaseDecrease):
                if increaseDecrease :
                    if self.speed + 10 < 100: 
                        self.speed += 10
                        self.statusBar.showMessage("Speed increased") 
                    else :
                        self.speed = 100
                        self.statusBar.showMessage("Speed increased")
                else :
                    if self.speed - 10 > 0 : 
                        self.speed -= 10
                    else :
                        self.speed = 0
                    self.statusBar.showMessage("Speed decreased")
                self.speedValueLabel.setText(str(self.speed))
                self.SpeedSlider.setValue(int(self.speed))
                self.timer.setInterval(int((100-self.speed)))

        def pausePlay():
            if not self.plotStatus:
                self.timer.start()
                self.plotStatus = True
                self.PlayBtn.setIcon(QIcon("images/pause.ico"))
                self.statusBar.showMessage("Plot is running.. You can't add any signal while plot is running.")
            else :
                self.timer.stop()
                self.plotStatus = False
                self.PlayBtn.setIcon(QIcon("images/play.ico"))
                self.statusBar.showMessage("Plot is paused.")

        # Down Button
        downSpeedBtn = QPushButton()
        downSpeedBtn.setIcon(QIcon("images/decrease.svg"))
        downSpeedBtn.clicked.connect(partial(signalSpeed,False))
        # PauseAndPlay
        self.PlayBtn = QPushButton()
        self.PlayBtn.setIcon(QIcon("images/play.ico"))
        self.PlayBtn.clicked.connect(pausePlay)
        # Up Button
        UpSpeedBtn = QPushButton()
        UpSpeedBtn.setIcon(QIcon("images/increase.svg"))
        UpSpeedBtn.clicked.connect(partial(signalSpeed,True))

        # Grid Button
        self.gridShowBtn = QCheckBox("Show Grid", self)
        self.gridShowBtn.setStyleSheet("font-size:14px;")
        self.gridShowBtn.stateChanged.connect(self.showGrid)

        # StyleSheet
        downSpeedBtn.setStyleSheet("font-size:14px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px; background: black")
        self.PlayBtn.setStyleSheet("font-size:14px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px;")
        UpSpeedBtn.setStyleSheet("font-size:14px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px; background: black")

        mainButtonsLayout.addWidget(downSpeedBtn,2)
        mainButtonsLayout.addWidget(self.PlayBtn,2)
        mainButtonsLayout.addWidget(UpSpeedBtn,2)
        
        mainButtonsLayout.addSpacerItem(QSpacerItem(250, 10, QSizePolicy.Expanding))

        def SpeedSliderChange(value):
            self.speed = value
            self.speedValueLabel.setText(str(value))
            self.timer.setInterval(int(1*(100-self.speed)))
        
        speedSliderLayout = QHBoxLayout()
        sliderLabel=QLabel("Speed: ")
        sliderLabel.setStyleSheet("font-size: 13px;padding: 2px;font-weight: 800;")

        self.SpeedSlider = QSlider(Qt.Horizontal, self)
        self.SpeedSlider.setValue(self.speed)
        self.SpeedSlider.valueChanged[int].connect(SpeedSliderChange)

        self.speedValueLabel = QLabel("50")
        self.speedValueLabel.setStyleSheet("font-size: 13px;padding: 2px;font-weight: 800;")

        speedSliderLayout.addSpacerItem((QSpacerItem(30, 10, QSizePolicy.Expanding)))
        speedSliderLayout.addWidget(sliderLabel,1)
        speedSliderLayout.addWidget(self.SpeedSlider,10)
        speedSliderLayout.addWidget(self.speedValueLabel,1)
        speedSliderLayout.addSpacerItem((QSpacerItem(30, 10, QSizePolicy.Expanding)))

        plotsLayout.addLayout(speedSliderLayout)
        plotsLayout.addLayout(mainButtonsLayout)
        plotsLayout.addWidget(self.gridShowBtn)

        SpectrogramLayout = QVBoxLayout()
        
        self.spectrogramGraph = spectrogram.MplCanvas(self, width=5, height=6, dpi=100)
        self.spectrogramGraph.plotSignal()
        self.spectrogramGraph.clearSignal()
        self.spectrogramGraph.autoFillBackground()
        # self.spectrogramGraph.addColorBar()

        # Min Contrast changer
        def minSpectrogramSliderChange(value):
            if value > maxSpectrogramSlider.value():
                value = maxSpectrogramSlider.value()
                minSpectrogramSlider.setValue(value)

            self.minvalueLabel.setText(str(value))
            self.spectrogramGraph.set_minContrast(value)
            self.spectrogramGraph.plotSignal()

        # Min contrast spectrogram control
        minContrastSpectrogramLayout = QHBoxLayout()        
        minLabel = QLabel("Min:")
        minLabel.setStyleSheet("font-size: 13px;padding: 2px;font-weight: 800;")
        minSpectrogramSlider = QSlider(Qt.Horizontal, self)
        minSpectrogramSlider.setValue(0)
        minSpectrogramSlider.valueChanged[int].connect(minSpectrogramSliderChange)  
        self.minvalueLabel = QLabel(str(minSpectrogramSlider.value()))  
        minContrastSpectrogramLayout.addWidget(minLabel)
        minContrastSpectrogramLayout.addWidget(minSpectrogramSlider)
        minContrastSpectrogramLayout.addWidget(self.minvalueLabel)

        # Max Contrast changer
        def maxSpectrogramSliderChange(value):
            if value < minSpectrogramSlider.value():
                value = minSpectrogramSlider.value()
                maxSpectrogramSlider.setValue(value)
            self.maxValueLabel.setText(str(value))
            self.spectrogramGraph.set_maxContrast(value)
            self.spectrogramGraph.plotSignal()

        # Max contrast spectrogram control
        maxContrastSpectrogramLayout = QHBoxLayout()        
        maxLabel = QLabel("Max:")
        maxLabel.setStyleSheet("font-size: 13px;padding: 2px; font-weight: 800;")
        maxSpectrogramSlider = QSlider(Qt.Horizontal, self)
        maxSpectrogramSlider.setValue(100)
        maxSpectrogramSlider.valueChanged[int].connect(maxSpectrogramSliderChange)
        self.maxValueLabel = QLabel(str(maxSpectrogramSlider.value()))    
        maxContrastSpectrogramLayout.addWidget(maxLabel)
        maxContrastSpectrogramLayout.addWidget(maxSpectrogramSlider)
        maxContrastSpectrogramLayout.addWidget(self.maxValueLabel)
        
        # Left part (Spectrogram)
        
        SpectrogramLayout.addLayout(minContrastSpectrogramLayout)
        SpectrogramLayout.addLayout(maxContrastSpectrogramLayout)                
                
        # Top layout of the graph
        ControlsLayout.addLayout(plotsLayout,2)
        ControlsLayout.addLayout(SpectrogramLayout,1) 

        # Create a layout for the buttons for specific signal
        ChannelbuttonsLayout = QHBoxLayout()
        # Add some buttons to the layout
        self.tabs = QTabWidget()
        self.tabs.activateWindow()
        self.tabs.setStyleSheet("font-size:15px;")
        self.tabs.addTab(self.SpectrogramTab(), "Spectrogram")
        
        ChannelbuttonsLayout.addWidget(self.tabs)

        allDockArea = DockArea()
        
        plotArea = Dock("Plot", size=(2, 1))     ## give this dock the minimum possible size
        spectrogramArea = Dock("Spectrogram Area", size=(1,1), closable=True)
        
        plotArea.addWidget(self.GrLayout)
        plotArea.hideTitleBar()
        spectrogramArea.addWidget(self.spectrogramGraph)
        spectrogramArea.hideTitleBar()
        
        allDockArea.addDock(plotArea, 'left')      ## place d1 at left edge of dock area (it will fill the whole space since there are no other docks yet)
        allDockArea.addDock(spectrogramArea, 'right')     ## place d2 at right edge of dock area

        # Nest the inner layouts into the outer layout
        outerLayout.addWidget(allDockArea,5)
        outerLayout.addLayout(ControlsLayout,1)
        outerLayout.addLayout(ChannelbuttonsLayout,1)

        wid.setLayout(outerLayout)

    # Create a menu bar
    def _createMenuBar(self):
        """MenuBar"""
        toolbar = QToolBar("ICU Toolbar")
        self.addToolBar(toolbar)

        menuBar = self.menuBar()
        
        # Creating menus using a QMenu object
        fileMenu = QMenu("&File", self)
        
        openF = QAction("Open...",self)
        openF.setShortcut("Ctrl+o")
        fileMenu.addAction(openF)
        openF.triggered.connect(self.browse_Signal)

        exportS = QAction("Export",self)
        exportS.setShortcut("Ctrl+x")
        fileMenu.addAction(exportS)
        exportS.triggered.connect(self.exportPDF)

        quit = QAction("Quit",self)
        quit.setShortcut("Ctrl+q")
        fileMenu.addAction(quit)
        quit.triggered.connect(self.exit)

        menuBar.addMenu(fileMenu)

    # Main Plot
    def _updatePlot(self):
        self.incrementTimeAlongSignalRun = 1
        if self.existChannel[0] == 1 or self.existChannel[1] == 1 or self.existChannel[2] == 1 :
            self.timer.setInterval((int(5*(100-self.speed))))
            self.timer.timeout.connect(self.update_plot_data)
            self.timer.start()
            self.PlayBtn.setIcon(QIcon("images/pause.ico"))
            
    def update_plot_data(self):
        if len(self.time_live) < len(self.time) - 1:
            self.time_live.append(self.time[len(self.time_live)])
            if self.existChannel[0] != 0 :
                self.data_channel_live_1.append(self.data_channel_1[len(self.time_live)])
                self.data_line_ch1.setData(self.time_live, self.data_channel_live_1)  # Update the data.
            
            if self.existChannel[1] != 0 :
                self.data_channel_live_2.append(self.data_channel_2[len(self.time_live)])
                self.data_line_ch2.setData(self.time_live, self.data_channel_live_2)  # Update the data.
            
            if self.existChannel[2] != 0 :
                self.data_channel_live_3.append(self.data_channel_3[len(self.time_live)])
                self.data_line_ch3.setData(self.time_live, self.data_channel_live_3)  # Update the data.
            
            self.incrementTimeAlongSignalRun +=1
            self.setLimits()            

    # Show grid
    def showGrid(self):
        if self.gridShowBtn.isChecked():
            self.PlotGraph.showGrid(x=True, y=True)
        else:
            self.PlotGraph.showGrid(x=False, y=False)

    # Plot channel of the signal.
    def plotChannelSignal(self, Channel, x, y, plotname, color="w"):
        pen = pg.mkPen(color=color) 
        data_line_channel = Channel.plot(x, y, name=plotname, pen=pen)
        return data_line_channel
        
    # Add Tabs
    def channelTabUI1(self):
        """Create the General page UI."""
        chTabUI1Tab = QWidget()
        if self.existChannel[0] == 0:
            chTabUI1Tab.setDisabled(True)

        buttonsLayout = QHBoxLayout()
        
        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))

        # Color Button Changer
        colorbtn = pg.ColorButton()
        self.changeColorBtn(self.data_line_ch1,colorbtn)
        ColorLabel = QLabel("Color:")
        ColorLabel.setStyleSheet("font-size:14px;")
        buttonsLayout.addWidget(ColorLabel,1)
        buttonsLayout.addWidget(colorbtn,1)

        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))
        
        # Title Box Changer
        TitleLabel = QLabel("Label:")
        TitleLabel.setStyleSheet("font-size:14px;")
        buttonsLayout.addWidget(TitleLabel,1)
        
        TitleBox = QLineEdit(self)
        TitleBox.setStyleSheet("font-size:14px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px;")
        TitleBox.setText("Channel 1")
        buttonsLayout.addWidget(TitleBox,4)
        
        changeTitleBtn = QPushButton("Change Label")
        changeTitleBtn.setStyleSheet("font-size:14px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px;")
        changeTitleBtn.clicked.connect(partial(self.changeTitle,self.data_line_ch1,TitleBox))
        buttonsLayout.addWidget(changeTitleBtn,2)

        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))
        
        # Hide/show the signal
        self.HideCheckBoxChannel1 = QCheckBox("Hide",self)
        self.HideCheckBoxChannel1.setStyleSheet("font-size:14px;")
        buttonsLayout.addWidget(self.HideCheckBoxChannel1,1)
        self.HideCheckBoxChannel1.stateChanged.connect(self.hideShowSignal)

        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))

        self.clearChannel1 = QPushButton()
        self.clearChannel1.setIcon(QIcon("images/clear.svg"))
        self.clearChannel1.setStyleSheet("background: black; font-size:14px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px;")
        self.clearChannel1.clicked.connect(partial(self.signalClear,0))
        buttonsLayout.addWidget(self.clearChannel1,1)

        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))
        
        chTabUI1Tab.setLayout(buttonsLayout)
        return chTabUI1Tab
    
    def channelTabUI2(self):
        """Create the Network page UI."""
        chTabUI2Tab = QWidget()
        if self.existChannel[1] == 0:
            chTabUI2Tab.setDisabled(True)

        buttonsLayout = QHBoxLayout()
    
        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))

        colorbtn = pg.ColorButton()
        self.changeColorBtn(self.data_line_ch2, colorbtn)
        ColorLabel = QLabel("Color:")
        ColorLabel.setStyleSheet("font-size:14px;")
        buttonsLayout.addWidget(ColorLabel,1)
        buttonsLayout.addWidget(colorbtn,1)

        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))
        
        TitleLabel = QLabel("Label:")
        TitleLabel.setStyleSheet("font-size:14px;")
        buttonsLayout.addWidget(TitleLabel,1)
        
        TitleBox = QLineEdit(self)
        TitleBox.setStyleSheet("font-size:14px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px;")
        TitleBox.setText("Channel 2")
        buttonsLayout.addWidget(TitleBox,4)
        
        changeTitleBtn = QPushButton("Change Label")
        changeTitleBtn.setStyleSheet("font-size:14px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px;")
        changeTitleBtn.clicked.connect(partial(self.changeTitle,self.data_line_ch2,TitleBox))
        buttonsLayout.addWidget(changeTitleBtn,2)

        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))

        self.HideCheckBoxChannel2 = QCheckBox("Hide",self)
        self.HideCheckBoxChannel2.setStyleSheet("font-size:14px;")
        buttonsLayout.addWidget(self.HideCheckBoxChannel2,1)
        
        # connecting it to function
        self.HideCheckBoxChannel2.stateChanged.connect(self.hideShowSignal)

        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))

        self.clearChannel2 = QPushButton()
        self.clearChannel2.setIcon(QIcon("images/clear.svg"))
        self.clearChannel2.setStyleSheet("background: black; font-size:14px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px;")
        self.clearChannel2.clicked.connect(partial(self.signalClear,1))
        buttonsLayout.addWidget(self.clearChannel2,1)
        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))
        chTabUI2Tab.setLayout(buttonsLayout)
        return chTabUI2Tab
    
    def channelTabUI3(self):
        """Create the Network page UI."""
        chTabUI3Tab = QWidget()
        if self.existChannel[2] == 0:
            chTabUI3Tab.setDisabled(True)
        buttonsLayout = QHBoxLayout()
    
        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))

        colorbtn = pg.ColorButton()
        self.changeColorBtn(self.data_line_ch3, colorbtn)
        ColorLabel = QLabel("Color:")
        ColorLabel.setStyleSheet("font-size:14px;")
        buttonsLayout.addWidget(ColorLabel,1)
        buttonsLayout.addWidget(colorbtn,1)

        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))
        
        TitleLabel = QLabel("Label:")
        TitleLabel.setStyleSheet("font-size:14px;")
        buttonsLayout.addWidget(TitleLabel,1)
        
        TitleBox = QLineEdit(self)
        TitleBox.setStyleSheet("font-size:14px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px;")
        TitleBox.setText("Channel 3")
        buttonsLayout.addWidget(TitleBox,4)
        
        changeTitleBtn = QPushButton("Change Label")
        changeTitleBtn.setStyleSheet("font-size:14px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px;")
        changeTitleBtn.clicked.connect(partial(self.changeTitle,self.data_line_ch3,TitleBox))
        buttonsLayout.addWidget(changeTitleBtn,2)

        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))

        self.HideCheckBoxChannel3 = QCheckBox("Hide",self)
        self.HideCheckBoxChannel3.setStyleSheet("font-size:14px;")
        buttonsLayout.addWidget(self.HideCheckBoxChannel3,1)
        
        # connecting it to function
        self.HideCheckBoxChannel3.stateChanged.connect(self.hideShowSignal)

        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))
        
        self.clearChannel3 = QPushButton()
        self.clearChannel3.setIcon(QIcon("images/clear.svg"))
        self.clearChannel3.setStyleSheet("background: black; font-size:14px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px;")
        self.clearChannel3.clicked.connect(partial(self.signalClear,2))
        buttonsLayout.addWidget(self.clearChannel3,1)
        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))
        chTabUI3Tab.setLayout(buttonsLayout)
        return chTabUI3Tab
    
    def SpectrogramTab(self):
        """Create the Network page UI."""
        SpectrogramTab = QWidget()
        buttonsLayout = QHBoxLayout()

        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))

        channelLabel = QLabel("Channel:")
        channelLabel.setStyleSheet("font-size:14px;")
        self.channelComboBox = QComboBox()
        self.channelComboBox.setStyleSheet("font-size:12px; padding: 5px 10px;")
        self.channelComboBox.addItem("")
        self.channelComboBox.addItem("Channel 1")
        self.channelComboBox.addItem("Channel 2")
        self.channelComboBox.addItem("Channel 3")

        self.channelComboBox.activated.connect(partial(self.channelSpectrogram,self.spectrogramGraph))
        
        buttonsLayout.addWidget(channelLabel,1)
        buttonsLayout.addWidget(self.channelComboBox,2)

        buttonsLayout.addSpacerItem(QSpacerItem(200, 10, QSizePolicy.Expanding))
        
        colorLabel = QLabel("Color:")
        colorLabel.setStyleSheet("font-size:14px;")
        colorComboBox = QComboBox()
        colorComboBox.setStyleSheet("font-size:12px; padding: 5px 10px;")
        colorComboBox.addItem("binary")
        colorComboBox.addItem("viridis")
        colorComboBox.addItem("plasma")
        colorComboBox.addItem("inferno")
        colorComboBox.addItem("magma")
        colorComboBox.addItem("rainbow")

        colorComboBox.currentTextChanged.connect(partial(self.colorSpectrogram, self.spectrogramGraph))

        buttonsLayout.addWidget(colorLabel,1)
        buttonsLayout.addWidget(colorComboBox,2)

        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))

        SpectrogramTab.setLayout(buttonsLayout)
        return SpectrogramTab

    # Choose channel for the spectrogram
    def channelSpectrogram(self,spectrogramGraph):
            value = self.channelComboBox.currentText()
            spectrogramGraph.clearSignal()
            
            if value == "Channel 1":
                if self.existChannel[0] == 1 :
                    spectrogramGraph.set_data_channel(self.data_channel_live_1)
                else :
                    self.statusBar.showMessage("Choose Channel 1 first!")
            elif value == "Channel 2":
                if self.existChannel[0] == 1 :
                    spectrogramGraph.set_data_channel(self.data_channel_live_2)
                else :
                    self.statusBar.showMessage("Choose Channel 2 first!")
            elif value == "Channel 3":
                if self.existChannel[0] == 1 :
                    spectrogramGraph.set_data_channel(self.data_channel_live_3)
                else :
                    self.statusBar.showMessage("Choose Channel 3 first!")
            spectrogramGraph.plotSignal()

    # Browse and Open the signal.
    def browse_Signal(self):
        if self.existChannel != [1, 1, 1]:
            self.path, self.fileExtension = QFileDialog.getOpenFileName(None, "Load Signal File", os.getenv('HOME') ,"csv(*.csv);; text(*.txt)")
            if self.path == "":
                return

            downloadedDataChannel = [0]
            if self.fileExtension == "csv(*.csv)":
                downloadedDataChannel = pd.read_csv(self.path).iloc[:,1]
                downloadedDataChannel = downloadedDataChannel.values.tolist()
                downloadedDataChannel = downloadedDataChannel[::] # sample rate

            self._addNewChannel(downloadedDataChannel)
            self._updatePlot()
        else :
            self.statusBar.showMessage("You can't add more than 3 channels, clear one of them then add again!")

    def clearAllChannels(self):
        self.time_live = list()

        self.data_channel_live_1 = list()
        self.data_line_ch1.clear()
        self.data_channel_live_2 = list()
        self.data_line_ch2.clear()
        self.data_channel_live_3 = list()
        self.data_line_ch3.clear()

    def _addNewChannel(self, downloadedDataChannel):
        if self.existChannel[0] == 0 :
            self.clearAllChannels()
            self.data_channel_live_1 = []
            self.data_line_ch1.clear()

            self.data_channel_1 = downloadedDataChannel
            self.data_channel_live_1 = list()
            self.existChannel[0] = 1

            self.tabs.addTab(self.channelTabUI1(), "Channel 1")

            self.statusBar.showMessage("Channel 1 loaded successfully.")
        elif self.existChannel[1] == 0 :
            self.clearAllChannels()
            self.data_channel_live_2 = []
            self.data_line_ch2.clear()

            self.data_channel_2 = downloadedDataChannel
            self.data_channel_live_2 = list()
            self.existChannel[1] = 1

            self.tabs.addTab(self.channelTabUI2(), "Channel 2")

            self.statusBar.showMessage("Channel 2 loaded successfully.")
        elif self.existChannel[2] == 0 :
            self.clearAllChannels()
            self.data_channel_live_3 = []
            self.data_line_ch3.clear()

            self.data_channel_3 = downloadedDataChannel
            self.data_channel_live_3 = list()
            self.existChannel[2] = 1

            self.tabs.addTab(self.channelTabUI3(), "Channel 3")

            self.statusBar.showMessage("Channel 3 loaded successfully")
        else :
            self.statusBar.showMessage("You can't add more than 3 channels, clear one of them then add again!")
        self.addZerosChannel()

    def addZerosChannel(self):
        dataLengths = [len(self.data_channel_1), len(self.data_channel_2), len(self.data_channel_3)]
        maxLength = max(dataLengths)
        for _ in range(maxLength-dataLengths[0]):
            self.data_channel_1.append(np.random.randint(0,10))
        for _ in range(maxLength-dataLengths[1]):
            self.data_channel_2.append(np.random.randint(0,10))
        for _ in range(maxLength-dataLengths[2]):
            self.data_channel_3.append(np.random.randint(0,10))
        self.time = np.linspace(0,maxLength-1,maxLength)
        self.time_live = list()
        
    # Export information in PDF
    def exportPDF(self):
        exporter = pyqtgraph.exporters.ImageExporter(self.GrLayout.scene())
        exporter.export('images/image.png')

        output_file, _ = QFileDialog.getSaveFileName(self, 'Export PDF', None, 'PDF files (.pdf);;All Files()')
        if output_file != '':
            if QFileInfo(output_file).suffix() == "" : output_file += '.pdf'

            input_file = "others/blank.pdf"
            image_file = "images/image.png"
            
            # Adding Image
            img = open(image_file, "rb").read()
            rect = fitz.Rect(100, 0, 500, 500)
            doc = fitz.open(input_file)
            doc[0].insert_image(rect, stream=img)
            
            p = fitz.Point(100, 100)
            title = "Statistics Report about plot:"
            doc[0].insert_text(p, title, fontsize = 20)

            if self.existChannel[0] == 1 :
                # Channel 1 information
                p = fitz.Point(100, 400)
                titleChannel1 = "Channel 1:"
                doc[0].insert_text(p, titleChannel1, fontsize = 15)

                p = fitz.Point(100, 425)
                StatisticsChannel1 = self.channelStatisticsGet(self.data_channel_1)
                doc[0].insert_text(p, StatisticsChannel1, fontsize = 12)
            
            if self.existChannel[1] == 1 :
                # Channel 2 information
                p = fitz.Point(100, 525)
                titleChannel2 = "Channel 2:"
                doc[0].insert_text(p, titleChannel2, fontsize = 15)

                p = fitz.Point(100, 550)
                StatisticsChannel2 = self.channelStatisticsGet(self.data_channel_2)
                doc[0].insert_text(p, StatisticsChannel2, fontsize = 12)            
            
            if self.existChannel[2] == 1 :
                # Channel 3 information
                p = fitz.Point(100, 650)
                titleChannel3 = "Channel 3:"
                doc[0].insert_text(p, titleChannel3, fontsize = 15)

                p = fitz.Point(100, 675)
                StatisticsChannel3 = self.channelStatisticsGet(self.data_channel_3)
                doc[0].insert_text(p, StatisticsChannel3, fontsize = 12)    

            doc.save(output_file)
            self.statusBar.showMessage("Congratulation!! Exported to PDF successfully.")
    
    def channelStatisticsGet(self, data_channel):
        meanChannel = "mean: " + str(np.mean(data_channel)) + "\n"
        stdChannel = "Std: " + str(np.std(data_channel)) + "\n"
        minValueChannel = "MIN value: " + str(min(data_channel)) + "\n"
        maxValueChannel = "MAX value: " + str(max(data_channel)) + "\n"

        StatisticsChannel = meanChannel + stdChannel + minValueChannel + maxValueChannel

        return StatisticsChannel

    # Change Color of Channel
    def changeColorBtn(self,data_line,colorbtn):
        def done(btn):
            data_line.setPen(btn.color())

        colorbtn.sigColorChanged.connect(done)

    def colorSpectrogram(self, spectrogramGraph, color):
        self.statusBar.showMessage("Spectrogram platte color is changed to " + color + ".")
        spectrogramGraph.set_color(color)
        # spectrogramGraph.updateColorBar()
        spectrogramGraph.plotSignal()

    # Show and Hide the signal
    def hideShowSignal(self) :
        if self.HideCheckBoxChannel1.isChecked():
            self.statusBar.showMessage("Channel 1 is hided")
            self.data_line_ch1.hide()
        else :
            self.statusBar.showMessage("Channel 1 is showed")
            self.data_line_ch1.show()

        if self.HideCheckBoxChannel2.isChecked():
            self.statusBar.showMessage("Channel 2 is hided")
            self.data_line_ch2.hide()
        else :
            self.statusBar.showMessage("Channel 2 is showed")
            self.data_line_ch2.show()
        
        if self.HideCheckBoxChannel3.isChecked():
            self.statusBar.showMessage("Channel 3 is hided")
            self.data_line_ch3.hide()
        else : 
            self.statusBar.showMessage("Channel 3 is showed")
            self.data_line_ch3.show()

    # Change title of the signal
    def changeTitle(self,data_line,TitleBox):
        self.legendItemName.removeItem(data_line)
        self.legendItemName.addItem(data_line, TitleBox.text())

    # set Limits of signal
    def setLimits(self):
        pass
    
    def signalClear(self,channelNumber):
        if channelNumber == 0:
            self.data_line_ch1.clear()
            self.data_channel_1 = [0]
            self.data_channel_live_1 = [0]
            self.tabs.removeTab(1)
        elif channelNumber == 1:
            self.data_line_ch2.clear()
            self.data_channel_2 = [0]
            self.data_channel_live_2 = [0]
            self.tabs.removeTab(2)
        elif channelNumber == 2:
            self.data_line_ch3.clear()
            self.data_channel_3 = [0]
            self.data_channel_live_3 = [0]
            self.tabs.removeTab(3)
        
        self.PlayBtn.setIcon(QIcon("images/pause.ico"))
        self.existChannel[channelNumber] = 0
        self._updatePlot()
    
    # Quit the window    
    def exit(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Exit the application")
        dlg.setText("Are you sure you want to exit the application ?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Question)
        button = dlg.exec()

        if button == QMessageBox.Yes:
            sys.exit()
        

if __name__ == "__main__":
    # Initialize Our Window App
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    win = Window()
    win.show()

    # Run the application
    sys.exit(app.exec_())