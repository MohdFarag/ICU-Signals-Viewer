# Python 3

import sys

# importing Qt widgets
from PyQt5.QtWidgets import *
from matplotlib.pyplot import pause, title

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
from time import perf_counter

# matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from scipy.io import loadmat


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.set_title('Spectrogram')
        super(MplCanvas, self).__init__(fig)


class Window(QMainWindow):
    """Main Window."""
    def __init__(self):
        
        """Initializer."""
        super().__init__()
        
        """Variables"""
        self.path = None # path of opened signal file

        self.time = [1,2,3,4,5,6,7,8,9,10] # Time Domain

        self.data_channel_1 = [0] * 10    # Default Value
        self.data_channel_2 = [10] * 10   # Default Value
        self.data_channel_3 = [-10] * 10  # Default Value
        
        
        """main properties"""
        # setting icon to the window
        self.setWindowIcon(QIcon('icon.png'))
        
        # setting title
        self.setWindowTitle("Multi-Channel Signal Viewer")

        #self.resize(600, 800) # set the size of the app

        # UI contents
        self._createMenuBar()
        self.initUI()

    def initUI(self):
        """Window GUI contents"""
        wid = QWidget(self)
        self.setCentralWidget(wid)
        
        outerLayout = QVBoxLayout()

        TopLayout = QHBoxLayout()

        # Create a layout for the plots
        plotsLayout = QVBoxLayout()
        
        # setting configuration options
        pg.setConfigOptions(antialias=True)

        # creating graphics layout widget
        self.GrLayout = pg.GraphicsLayoutWidget()

        self._addPlot(self.GrLayout, "Channels")

        # Create a layout for the main buttons
        mainButtonsLayout = QHBoxLayout()

        mainButtonsLayout.addSpacerItem(QSpacerItem(200, 10, QSizePolicy.Expanding))

        downSpeedBtn = QPushButton("-")
        PauseBtn = QPushButton("Pause")
        PlayBtn = QPushButton("Play")
        UpSpeedBtn = QPushButton("+")
    
        downSpeedBtn.setStyleSheet("font-size:14px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px;")
        PauseBtn.setStyleSheet("font-size:14px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px;")
        PlayBtn.setStyleSheet("font-size:14px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px;")
        UpSpeedBtn.setStyleSheet("font-size:14px; border-radius: 6px;border: 1px solid rgba(27, 31, 35, 0.15);padding: 5px 15px;")

        mainButtonsLayout.addWidget(downSpeedBtn,1)
        mainButtonsLayout.addWidget(PauseBtn,2)
        mainButtonsLayout.addWidget(PlayBtn,2)
        mainButtonsLayout.addWidget(UpSpeedBtn,1)
        
        mainButtonsLayout.addSpacerItem(QSpacerItem(200, 10, QSizePolicy.Expanding))

        plotsLayout.addWidget(self.GrLayout)
        plotsLayout.addLayout(mainButtonsLayout)
        plotsLayout.addSpacerItem(QSpacerItem(10, 25, QSizePolicy.Expanding))

        SpectrogramLayout = QVBoxLayout()
        plot = MplCanvas(self, width=5, height=6, dpi=100)
        SpectrogramLayout.addWidget(plot)
        SpectrogramLayout.addSpacerItem(QSpacerItem(10, 60, QSizePolicy.Expanding))

        TopLayout.addLayout(plotsLayout,2)
        TopLayout.addLayout(SpectrogramLayout,1)

        # Create a layout for the buttons for specific signal
        ChannelbuttonsLayout = QHBoxLayout()
        # Add some buttons to the layout
        tabs = QTabWidget()
        
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
        self.PlotGraph.setLimits(xMin=min(self.time), xMax=max(self.time),  
                yMin=min(all_data_channel), yMax=max(all_data_channel))
        self.legendItemName = self.PlotGraph.addLegend()

        # Plot and return the line of the signal to manipulate it. 
        self.data_line_ch1 = self.plotChannelSignal(self.PlotGraph, self.time, self.data_channel_1, "Channel 1")
        self.data_line_ch2 = self.plotChannelSignal(self.PlotGraph, self.time, self.data_channel_2, "Channel 2")
        self.data_line_ch3 = self.plotChannelSignal(self.PlotGraph, self.time, self.data_channel_3, "Channel 3")

        ### Commenting ##
        def timePlot():
            """Real Time Plot"""
            #     self.timer = QtCore.QTimer()
            #     self.timer.setInterval(50)
            #     self.timer.timeout.connect(self.update_plot_data)
            #     self.timer.start()

            # def update_plot_data(self):

            #     self.data_channel_1[:-1] = self.data_channel_1[1:]  # Remove the first
            #     self.data_channel_1[-1] = np.random.normal()  # Add a new random value.

            #     self.data_line_ch1.setData(self.time, self.data_channel_1)  # Update the data.
            pass
    
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
        buttonsLayout.addWidget(QPushButton("scTabUI3 Button1"))
        buttonsLayout.addWidget(QPushButton("scTabUI3 Button2"))
        buttonsLayout.addWidget(QPushButton("scTabUI3 Button3"))
        SpectrogramTab.setLayout(buttonsLayout)
        return SpectrogramTab

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
    
    # Change Color of Channel
    def changeColorBtn(self,data_line,colorbtn):
        def done(btn):
            data_line.setPen(pg.mkPen(btn.color()))

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