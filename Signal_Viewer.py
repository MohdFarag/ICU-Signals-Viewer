# Python 3

from audioop import avg
import sys

# importing Qt widgets
from PyQt5.QtWidgets import *

# importing numpy as np
import numpy as np
import pandas as pd

# importing pyqtgraph as pg
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import os
from functools import partial

# importing time
from time import perf_counter, time

# matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# import scipy
from scipy.io import loadmat
from scipy import signal

# import random
import random


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.set_title('Spectrogram',fontweight ="bold")
        super(MplCanvas, self).__init__(self.fig)
    
    def plotSignal(self, data_channel, color, details=50):
        fs = 400
        nfft = 400
        data_channel = np.array(data_channel)
        self.axes.specgram(data_channel, nfft, fs, mode='magnitude',cmap=color, noverlap=nfft/2)
        self.draw()
        

class Window(QMainWindow):
    """Main Window."""
    def __init__(self):
        
        """Initializer."""
        super().__init__()
        
        """Variables"""
        self.path = None # path of opened signal file

        self.time = [i for i in range(0, 500)] # Time Domain

        self.data_channel_1 = [random.random()+10 for _ in range(0, 500)]
        self.data_channel_2 = [random.random() for _ in range(0, 500)]
        self.data_channel_3 = [random.random()-10 for _ in range(0, 500)]
        self.isPlotLive = True
        #self.data_channel = [-10] * 10  # Default Value

        self.time_live = list()
        self.data_channel_live_1 = list()
        self.data_channel_live_2 = list()
        self.data_channel_live_3 = list()

        self.speed = 50
        
        """main properties"""
        # setting icon to the window
        self.setWindowIcon(QIcon('icon.png'))
        
        # setting title
        self.setWindowTitle("Multi-Channel Signal Viewer")

        # UI contents
        self._createMenuBar()
        self.initUI()

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def initUI(self):
        """Window GUI contents"""
        wid = QWidget(self)
        self.setCentralWidget(wid)
        # setting configuration options
        pg.setConfigOptions(antialias=True)

        # big Layout
        outerLayout = QVBoxLayout()

        TopLayout = QHBoxLayout()

        # Create a layout for the plots
        plotsLayout = QVBoxLayout()

        # creating graphics layout widget
        self.GrLayout = pg.GraphicsLayoutWidget()
        self._addPlot(self.GrLayout, "Channels")

        # Create a layout for the main buttons
        mainButtonsLayout = QHBoxLayout()

        mainButtonsLayout.addSpacerItem(QSpacerItem(200, 10, QSizePolicy.Expanding))

        # Main buttons to manipulate the plot

        def signalSpeed(increaseDecrease):
                if increaseDecrease :
                    if self.speed < 100: 
                        self.speed += 25
                        self.statusBar.showMessage("Speed increased") 
                    else :
                        self.statusBar.showMessage("Speed can't increased!")    
                else :
                    if self.speed < 100 and self.speed > 0 : 
                        self.speed -= 25
                        self.statusBar.showMessage("Speed decreased") 
                    else :
                        self.statusBar.showMessage("Speed can't decreased!")
                self.SpeedSlider.setValue(int(self.speed))        
                self.timer.setInterval(int(100 - self.speed))

        def pausePlay(pauseOrPlay):
            self.isPlotLive = pauseOrPlay
            if pauseOrPlay:
                self.statusBar.showMessage("Plot is running...")
            else :
                self.statusBar.showMessage("Plot is stopped!!")

        # Down Button
        downSpeedBtn = QPushButton("-")
        downSpeedBtn.clicked.connect(partial(signalSpeed,False))
        # PauseAndPlay
        PauseBtn = QPushButton("Pause")
        PauseBtn.clicked.connect(partial(pausePlay,False))
        PlayBtn = QPushButton("Play")
        PlayBtn.clicked.connect(partial(pausePlay,True))
        # Up Button
        UpSpeedBtn = QPushButton("+")
        UpSpeedBtn.clicked.connect(partial(signalSpeed,True))

        # StyleSheet
        downSpeedBtn.setStyleSheet("font-size:14px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px;")
        PauseBtn.setStyleSheet("font-size:14px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px;")
        PlayBtn.setStyleSheet("font-size:14px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px;")
        UpSpeedBtn.setStyleSheet("font-size:14px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px;")

        mainButtonsLayout.addWidget(downSpeedBtn,1)
        mainButtonsLayout.addWidget(PauseBtn,2)
        mainButtonsLayout.addWidget(PlayBtn,2)
        mainButtonsLayout.addWidget(UpSpeedBtn,1)
        
        mainButtonsLayout.addSpacerItem(QSpacerItem(200, 10, QSizePolicy.Expanding))

        def SpeedSliderChange(value):
            self.speed = value
            self.timer.setInterval(int(100 - self.speed))

        self.SpeedSlider = QSlider(Qt.Horizontal, self)
        self.SpeedSlider.setValue(self.speed)
        self.SpeedSlider.valueChanged[int].connect(SpeedSliderChange)

        plotsLayout.addWidget(self.GrLayout)
        plotsLayout.addWidget(self.SpeedSlider)
        plotsLayout.addLayout(mainButtonsLayout)
        plotsLayout.addSpacerItem(QSpacerItem(10, 25, QSizePolicy.Expanding))

        SpectrogramLayout = QVBoxLayout()

        self.spectrogramGraph = MplCanvas(self, width=5, height=6, dpi=100)

        # Min Contrast changer
        def minSpectrogramSliderChange(value):
            self.plotSpectrogram(self.data_channel_1,"Reds",value)
            self.minvalueLabel.setText(str(value))
        minContrastSpectrogramLayout = QHBoxLayout()        
        minLabel = QLabel("Min:")
        minSpectrogramSlider = QSlider(Qt.Horizontal, self)
        minSpectrogramSlider.setValue(50)
        minSpectrogramSlider.valueChanged[int].connect(minSpectrogramSliderChange)  
        self.minvalueLabel = QLabel(str(minSpectrogramSlider.value()))  
        minContrastSpectrogramLayout.addWidget(minLabel)
        minContrastSpectrogramLayout.addWidget(minSpectrogramSlider)
        minContrastSpectrogramLayout.addWidget(self.minvalueLabel)

        # Max Contrast changer
        def maxSpectrogramSliderChange(value):
            self.plotSpectrogram(self.data_channel_2,"Reds",value)
            self.maxValueLabel.setText(str(value))
        maxContrastSpectrogramLayout = QHBoxLayout()        
        maxLabel = QLabel("Max:")
        maxSpectrogramSlider = QSlider(Qt.Horizontal, self)
        maxSpectrogramSlider.setValue(50)
        maxSpectrogramSlider.valueChanged[int].connect(maxSpectrogramSliderChange)
        self.maxValueLabel = QLabel(str(maxSpectrogramSlider.value()))    
        maxContrastSpectrogramLayout.addWidget(maxLabel)
        maxContrastSpectrogramLayout.addWidget(maxSpectrogramSlider)
        maxContrastSpectrogramLayout.addWidget(self.maxValueLabel)
        
        # Left part (Spectrogram)
        SpectrogramLayout.addWidget(self.spectrogramGraph)
        SpectrogramLayout.addLayout(minContrastSpectrogramLayout)
        SpectrogramLayout.addLayout(maxContrastSpectrogramLayout)                
        SpectrogramLayout.addSpacerItem(QSpacerItem(10, 35, QSizePolicy.Expanding))

        TopLayout.addLayout(plotsLayout,2)
        TopLayout.addLayout(SpectrogramLayout,1)

        # Create a layout for the buttons for specific signal
        ChannelbuttonsLayout = QHBoxLayout()
        # Add some buttons to the layout
        tabs = QTabWidget()
        tabs.setStyleSheet("font-size:15px;")
        tabs.addTab(self.channelTabUI1(), "Channel 1")
        tabs.addTab(self.channelTabUI2(), "Channel 2")
        tabs.addTab(self.channelTabUI3(), "Channel 3")
        
        tabs.addTab(self.SpectrogramTab(), "Spectrogram")
        ChannelbuttonsLayout.addWidget(tabs)

        # Nest the inner layouts into the outer layout
        outerLayout.addLayout(TopLayout,5)
        outerLayout.addLayout(ChannelbuttonsLayout,1)

        wid.setLayout(outerLayout)

    # Create a menu bar
    def _createMenuBar(self):
        """MenuBar"""
        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)

        menuBar = self.menuBar()
        
        # Creating menus using a QMenu object
        fileMenu = QMenu("&File", self)
        
        openF = QAction("Open...",self)
        openF.setShortcut("Ctrl+o")
        fileMenu.addAction(openF)
        openF.triggered.connect(self.browse_Signal)

        exportS = QAction("Export",self)
        exportS.setShortcut("Ctrl+E")
        fileMenu.addAction(exportS)
        exportS.triggered.connect(self.exportPDF)

        quit = QAction("Quit",self)
        quit.setShortcut("Ctrl+q")
        fileMenu.addAction(quit)
        quit.triggered.connect(self.exit)

        fileMenu.addAction(openF)
        fileMenu.addAction(quit)

        menuBar.addMenu(fileMenu)

    # Main Plot
    def _addPlot(self,GrLayout,title):
                    
        all_data_channel = self.data_channel_1.copy()
        all_data_channel.extend(self.data_channel_2)
        all_data_channel.extend(self.data_channel_3)

        self.PlotGraph = GrLayout.addPlot(colspan=2)
        self.PlotGraph.setTitle(title,color="w", size="17pt")
        self.PlotGraph.setLabel('bottom', 'Time', 's')
        self.PlotGraph.setLimits(xMin=min(self.time) - 10, xMax=max(self.time) + 10, 
                                yMin=min(all_data_channel) - len(self.time)/10, yMax=max(all_data_channel) + len(self.time)/10)
        # run to end
        self.legendItemName = self.PlotGraph.addLegend()

        # Plot and return the line of the signal to manipulate it. 
        self.data_line_ch1 = self.plotChannelSignal(self.PlotGraph, self.time, self.data_channel_1, "Channel 1")
        self.data_line_ch2 = self.plotChannelSignal(self.PlotGraph, self.time, self.data_channel_2, "Channel 2")
        self.data_line_ch3 = self.plotChannelSignal(self.PlotGraph, self.time, self.data_channel_3, "Channel 3")

        self.timer = QtCore.QTimer()
        self.timer.setInterval(int(self.speed))
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):

        if len(self.time_live) < len(self.time)-1 and self.isPlotLive:
            self.time_live.append(self.time[len(self.time_live)])
            
            self.data_channel_live_1.append(self.data_channel_1[len(self.time_live)])
            self.data_channel_live_2.append(self.data_channel_2[len(self.time_live)])
            self.data_channel_live_3.append(self.data_channel_3[len(self.time_live)])

            self.data_line_ch1.setData(self.time_live, self.data_channel_live_1)  # Update the data.
            self.data_line_ch2.setData(self.time_live, self.data_channel_live_2)  # Update the data.
            self.data_line_ch3.setData(self.time_live, self.data_channel_live_3)  # Update the data.
    
    # Plot channel of the signal.
    def plotChannelSignal(self, Channel, x, y, plotname, color="w"):
        pen = pg.mkPen(color=color) 
        data_line_channel = Channel.plot(x, y, name=plotname, pen=pen)
        return data_line_channel
        
    # Add Tabs
    def channelTabUI1(self):
        """Create the General page UI."""
        chTabUI1Tab = QWidget()
        buttonsLayout = QHBoxLayout()
        
        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))

        # Color Button Changer
        colorbtn = pg.ColorButton()
        self.changeColorBtn(self.data_line_ch1,colorbtn)
        ColorLabel = QLabel("Color:")
        ColorLabel.setStyleSheet("font-size:14px;")
        buttonsLayout.addWidget(ColorLabel,1)
        buttonsLayout.addWidget(colorbtn,1)

        buttonsLayout.addSpacerItem(QSpacerItem(200, 10, QSizePolicy.Expanding))
        
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

        buttonsLayout.addSpacerItem(QSpacerItem(200, 10, QSizePolicy.Expanding))
        
        # Hide/show the signal
        self.HideCheckBoxChannel1 = QCheckBox("Hide",self)
        self.HideCheckBoxChannel1.setStyleSheet("font-size:14px;")
        buttonsLayout.addWidget(self.HideCheckBoxChannel1,1)
        self.HideCheckBoxChannel1.stateChanged.connect(self.hideShowSignal)

        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))

        chTabUI1Tab.setLayout(buttonsLayout)
        return chTabUI1Tab
    
    def channelTabUI2(self):
        """Create the Network page UI."""
        chTabUI2Tab = QWidget()
        buttonsLayout = QHBoxLayout()
    
        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))

        colorbtn = pg.ColorButton()
        self.changeColorBtn(self.data_line_ch2, colorbtn)
        ColorLabel = QLabel("Color:")
        ColorLabel.setStyleSheet("font-size:14px;")
        buttonsLayout.addWidget(ColorLabel,1)
        buttonsLayout.addWidget(colorbtn,1)

        buttonsLayout.addSpacerItem(QSpacerItem(200, 10, QSizePolicy.Expanding))
        
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

        buttonsLayout.addSpacerItem(QSpacerItem(200, 10, QSizePolicy.Expanding))

        self.HideCheckBoxChannel2 = QCheckBox("Hide",self)
        self.HideCheckBoxChannel2.setStyleSheet("font-size:14px;")
        buttonsLayout.addWidget(self.HideCheckBoxChannel2,1)
        
        # connecting it to function
        self.HideCheckBoxChannel2.stateChanged.connect(self.hideShowSignal)

        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))
        
        chTabUI2Tab.setLayout(buttonsLayout)
        return chTabUI2Tab
    
    def channelTabUI3(self):
        """Create the Network page UI."""
        chTabUI3Tab = QWidget()
        buttonsLayout = QHBoxLayout()
    
        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))

        colorbtn = pg.ColorButton()
        self.changeColorBtn(self.data_line_ch3, colorbtn)
        ColorLabel = QLabel("Color:")
        ColorLabel.setStyleSheet("font-size:14px;")
        buttonsLayout.addWidget(ColorLabel,1)
        buttonsLayout.addWidget(colorbtn,1)

        buttonsLayout.addSpacerItem(QSpacerItem(200, 10, QSizePolicy.Expanding))
        
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

        buttonsLayout.addSpacerItem(QSpacerItem(200, 10, QSizePolicy.Expanding))

        self.HideCheckBoxChannel3 = QCheckBox("Hide",self)
        self.HideCheckBoxChannel3.setStyleSheet("font-size:14px;")
        buttonsLayout.addWidget(self.HideCheckBoxChannel3,1)
        
        # connecting it to function
        self.HideCheckBoxChannel3.stateChanged.connect(self.hideShowSignal)

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

        self.channelComboBox.currentTextChanged.connect(self.channelSpectrogram)
        
        buttonsLayout.addWidget(channelLabel,1)
        buttonsLayout.addWidget(self.channelComboBox,2)

        buttonsLayout.addSpacerItem(QSpacerItem(200, 10, QSizePolicy.Expanding))
        
        colorLabel = QLabel("Color:")
        colorLabel.setStyleSheet("font-size:14px;")
        colorComboBox = QComboBox()
        colorComboBox.setStyleSheet("font-size:12px; padding: 5px 10px;")
        colorComboBox.addItem("")
        colorComboBox.addItem("Red")
        colorComboBox.addItem("Green")
        colorComboBox.addItem("Blue")
        colorComboBox.addItem("Cyan")
        colorComboBox.addItem("Magenta")
        buttonsLayout.addWidget(colorLabel,1)
        buttonsLayout.addWidget(colorComboBox,2)

        buttonsLayout.addSpacerItem(QSpacerItem(100, 10, QSizePolicy.Expanding))
        
        SpectrogramTab.setLayout(buttonsLayout)
        return SpectrogramTab

    # Choose channel for the spectrogram
    def channelSpectrogram(self):
            value = self.channelComboBox.currentText()
            if value=="Channel 1":
                self.plotSpectrogram(self.data_channel_1,"Reds",500)
            elif value=="Channel 2":
                self.plotSpectrogram(self.data_channel_2,"Reds",500)
            elif value=="Channel 3":
                self.plotSpectrogram(self.data_channel_3,"Reds",500)

    # Browse and Open the signal.
    def browse_Signal(self):
        def open(self):
            self.path, self.fileExtension = QFileDialog.getOpenFileName(None, "Load Signal File", os.getenv('HOME') ,"csv(*.csv);; text(*.txt) ;; xls(*.xls)")
            
        def read(self):
            if self.fileExtension == "*.csv":
                self.data_channel_1 = pd.read_csv(self.path).iloc[:,1]
                #saves data length of the file
                self.time = self.data_channel_1.__len__()
                
                
            elif self.fileExtension == "*.txt":
                self.data_channel_2 = pd.read_csv(self.path).iloc[:,2]
                #saves data length of the file
                self.time = self.data_channel_2.__len__()
                
            elif self.fileExtension == "*.mat":
                mat = loadmat(self.fileExtension[0])
                self.data_channel_3 = pd.DataFrame(mat["F"]).iloc[:,1]
                #saves data length of the file
                self.time = self.data_channel_3.__len__()       

        def update(self):
            self.data_line_ch1.clear()
            self.data_line_ch1.setData(self.time, self.data_channel_1)   
        
        open(self)
        read(self)
        update(self)
    
    # Export information in PDF
    def exportPDF(self):
        pass

    # Change Color of Channel
    def changeColorBtn(self,data_line,colorbtn):
        def done(btn):
            data_line.setPen(btn.color())

        colorbtn.sigColorChanged.connect(done)

    # Show and Hide the signal
    def hideShowSignal(self) :
        if self.HideCheckBoxChannel1.isChecked():
            self.data_line_ch1.hide()
        else : 
            self.data_line_ch1.show()

        if self.HideCheckBoxChannel2.isChecked():
            self.data_line_ch2.hide()
        else : 
            self.data_line_ch2.show()
        
        if self.HideCheckBoxChannel3.isChecked():
            self.data_line_ch3.hide()
        else : 
            self.data_line_ch3.show()

    # Change title of the signal
    def changeTitle(self,data_line,TitleBox):
        self.legendItemName.removeItem(data_line)
        self.legendItemName.addItem(data_line, TitleBox.text())

    def plotSpectrogram(self, data_channel, color, details):
        self.spectrogramGraph.plotSignal(data_channel, color, details)
        
    # Quit the window    
    def exit(self):
        sys.exit()


if __name__ == "__main__":
    # Initialize Our Window App
    app = QApplication(sys.argv)
    win = Window()
    win.show()

    # Run the application
    sys.exit(app.exec_())