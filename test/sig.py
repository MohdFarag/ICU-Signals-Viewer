# Python 3

import sys

# PyQt5

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

# matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(311)
        self.axes = fig.add_subplot(312)
        self.axes = fig.add_subplot(313)
        super(MplCanvas, self).__init__(fig)


class Window(QMainWindow):
    """Main Window."""
    def __init__(self, parent=None):
        
        """Initializer."""
        super().__init__(parent)

        # main properties
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.setWindowTitle("Multi-Channel Signal Viewer") # set title of the app
        #self.resize(400, 400) # set the size of the app
        self._createMenuBar()
        self.initUI()


    def initUI(self):
        """Window GUI contents"""
        wid = QWidget(self)
        self.setCentralWidget(wid)
        
        outerLayout = QVBoxLayout()

        # Create a layout for the checkboxes
        plotsLayout = QVBoxLayout()
        
        # Add plots to the layout
        plot = MplCanvas(self, width=5, height=6, dpi=100)
        
        plotsLayout.addWidget(plot)
        
        # Create a layout for the buttons
        buttonsLayout = QHBoxLayout()
        # Add some buttons to the layout
        tabs = QTabWidget()
        tabs.addTab(self.chTabUI1(), "Channel 1")
        tabs.addTab(self.chTabUI2(), "Channel 2")
        tabs.addTab(self.chTabUI3(), "Channel 3")
        buttonsLayout.addWidget(tabs)

        # Nest the inner layouts into the outer layout
        outerLayout.addLayout(plotsLayout)
        outerLayout.addLayout(buttonsLayout)

        wid.setLayout(outerLayout)
        
    # Create a menu bar
    def _createMenuBar(self):
        """MenuBar"""
        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)

        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        
        fileMenu.addAction("Open...")

        save = QAction("Screenshot",self)
        fileMenu.addAction(save)
        
        quit = QAction("Quit",self) 
        quit.setShortcut("Ctrl+q")
        fileMenu.addAction(quit)

    def chTabUI1(self):
            """Create the General page UI."""
            chTabUI1Tab = QWidget()
            buttonsLayout = QHBoxLayout()
            buttonsLayout.addWidget(QPushButton("scTabUI1 Button1"))
            buttonsLayout.addWidget(QPushButton("scTabUI1 Button2"))
            buttonsLayout.addWidget(QPushButton("scTabUI1 Button3"))
            chTabUI1Tab.setLayout(buttonsLayout)
            return chTabUI1Tab

    def chTabUI2(self):
        """Create the Network page UI."""
        chTabUI2Tab = QWidget()
        buttonsLayout = QHBoxLayout()
        buttonsLayout.addWidget(QPushButton("scTabUI2 Button1"))
        buttonsLayout.addWidget(QPushButton("scTabUI2 Button2"))
        buttonsLayout.addWidget(QPushButton("scTabUI2 Button3"))
        chTabUI2Tab.setLayout(buttonsLayout)
        return chTabUI2Tab
    
    def chTabUI3(self):
        """Create the Network page UI."""
        chTabUI3Tab = QWidget()
        buttonsLayout = QHBoxLayout()
        buttonsLayout.addWidget(QPushButton("scTabUI3 Button1"))
        buttonsLayout.addWidget(QPushButton("scTabUI3 Button2"))
        buttonsLayout.addWidget(QPushButton("scTabUI3 Button3"))
        chTabUI3Tab.setLayout(buttonsLayout)
        return chTabUI3Tab

if __name__ == "__main__":
    # Initialize Our Window App
    app = QApplication(sys.argv)
    win = Window()
    win.show()

    # Run the application
    sys.exit(app.exec_())