from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import QFont, QFrame, QLabel, QListWidget, QMessageBox, pyqtSignal
from dialogs import *
from lexic import *
from syntactic import *
from codeGenerator import *
from datetime import datetime
import resourceFiles
import io
import json
from const import *
import webbrowser
from Styles import qss
import copy

class Snapshot:
    """
    A class used to represent a state or 'snapshot' in the main program

    Its purpose is to save information listed in tokens and productions so
    they can be checked for changes when the user decides to open, create
    or save a new file. 
    
    Attributes
    ----------
    tokenList : list
        contains the tokens created by the user
    subsetList : list
        contains the subsets that are either created by default when creating
        a new file or edited by the user
    ntSymbolList : list
        contains the non-terminals symbols created by the user
    productionList : list
        contains production objects that store the left side, right side and
        the selection set of a given production created by the user

    Methods
    -------
    verifyChanges(tokenList, subsetList, ntSymbolList = [], productionList = [])
        checks if another snapshot (composed and represented by the args) is
        different in any form to the current snapshot
        
    setLists(tokenList, subsetList, ntSymbolList = [], productionList = [])
        sets all the atributes for a given snapshot, ntSymbolList & productionList
        are empty by default but can be set
    """
    
    def __init__(self):
        """
            Class for project control and changes cheking. Saves copy of last token list,
            Sub-sets list, No-terminal symbols list and productions list. And error Dictionaries
        """

        self.tokenList = []
        self.subsetList = []
        self.ntSymbolList = []
        self.productionList = []
        self.errorsDictionary ={}

    def verifyChanges(self, tokenList, subsetList, ntSymbolList = [], productionList = [], errorsDictionary = {}):
        """
        Parameters
        ----------
        tokenList : list of tokens
            contains the tokens created by the user
        subsetList : list of subsets
            contains the subsets that are either created by default when creating
            a new file or edited by the user
        ntSymbolList : list, optional
            contains the non-terminals symbols created by the user
        productionList : int, optional
            contains production objects that store the left side, right side and
            the selection set of a given production created by the user
        """
        
        changesLex = changesSyn = changesDic = True
        if self.tokenList == tokenList and self.subsetList == subsetList:
            changesLex = False
        if (self.ntSymbolList == ntSymbolList and self.productionList == productionList):
            changesSyn = False
        if (self.errorsDictionary == errorsDictionary):
            changesDic = False
        return changesLex or changesSyn or changesDic
    
    def setLists(self, tokenList, subsetList, ntSymbolList = [], productionList = [], errorsDictionary = {}):
        """
        Parameters
        ----------
        tokenList : list of tokens
            contains the tokens created by the user
        subsetList : list of subsets
            contains the subsets that are either created by default when creating
            a new file or edited by the user
        ntSymbolList : list, optional
            contains the non-terminals symbols created by the user
        productionList : int, optional
            contains production objects that store the left side, right side and
            the selection set of a given production created by the user
        """
        
        self.tokenList = tokenList.copy()
        self.subsetList = subsetList.copy()
        self.ntSymbolList = ntSymbolList.copy()
        self.productionList = productionList.copy()
        self.errorsDictionary = copy.deepcopy(errorsDictionary)

class ProductionRow(): 
    """
    Defines the elements used in a row of the sintactic table
    
    Its purpose is to keep track of every part that composes a
    production to facilitate the manipulation of it when creating
    a grammar
    
    Attributes
    ----------
    left_list : List
        QListWidget item that stores the left-side elements of a production
    right_list : List
        QListWidget item that stores the right-side elements of a production
    index : int
        represents the place or 'index' in the production table for a given
        production. It also corresponds to its place in the grammar.
    production : Production, None by default
        contains a single object that stores the left side, right side and
        the selection set of a given production created by the user
    """
    
    def __init__(self, left_list, right_list, index):

        self.left_list = left_list
        self.right_list = right_list
        self.index = index
        self.production = None

class Ui_MainWindow(object):
    """
    Main window for sintactic and lexic modules
    
    Contains every method and declaration that responds to the graphic
    interface of the software as well as the instantiation of backend
    variables and I/O procedures.
    """
    
    def setupUi(self, MainWindow):
        
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setWindowState(QtCore.Qt.WindowMaximized)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/Variable_48px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setWindowTitle("Analizador")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        MainWindow.setCentralWidget(self.centralwidget)
        # stylesheet
        MainWindow.setStyleSheet(qss) 
        
        # menu bar declaration
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 600, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        # File Menu
        fileMenu = QtWidgets.QMenu("&Archivo", MainWindow)
        fileMenu.addAction("&Nuevo...", self.newProject, "Ctrl+N")
        fileMenu.addAction("&Abrir...", self.openProject, "Ctrl+O")
        fileMenu.addAction("&Guardar...", self.saveProject, "Ctrl+S")
        fileMenu.addAction("&Guardar como...", self.saveAsProject, "Ctrl+A")
        fileMenu.addAction("&Salir", QtWidgets.QApplication.instance().quit, "Ctrl+Q")

        # Code Menu
        codeMenu = QtWidgets.QMenu("&Código", MainWindow)
        codeMenu.addAction("&Generar Cód...", self.generateProjectCode, "Ctrl+G+C")

        # Help menu
        helpMenu = QtWidgets.QMenu("&Ayuda", MainWindow)
        helpMenu.addAction("&Abrir página...", self.openRepositorySite, "Ctrl+H")
        helpMenu.addAction("&Formulario de...", self.openFormSite, "Ctrl+F")
        helpMenu.addAction("&Obtener Ayuda",self.openHelp, "Ctrl+Y")
        
        self.menubar.addMenu(fileMenu)
        self.menubar.addMenu(codeMenu)
        self.menubar.addMenu(helpMenu)
        
        # control variables of analyzer window
        self.saveFlag = None
        self.snapshot = Snapshot()
        self.currentProjectName = ''
        self.MainWindow = MainWindow
        
        # main tab declaration
        self.tabMain = QtWidgets.QTabWidget(self.centralwidget)
        self.tabMain.setObjectName("tabMain")
        self.verticalLayout.addWidget(self.tabMain)
        
        #region: lexic tab declaration
        
        #region: lexic tab variables instantiation 
        self.tabLexic = QtWidgets.QWidget()
        self.tabLexic.setObjectName("tabLexic")
        self.tabLexicLayout = QtWidgets.QVBoxLayout(self.tabLexic)
        self.tabLexicLayout.setObjectName("tabLexicLayout")
        
        self.containerTop = QtWidgets.QHBoxLayout()
        self.containerTop.setSpacing(12)
        self.containerTop.setObjectName("containerTop")
        
        self.layoutTable = QtWidgets.QVBoxLayout()
        self.layoutTable.setSpacing(5)
        self.layoutTable.setObjectName("layoutTable")
        
        self.labelTitle = QtWidgets.QLabel(self.tabLexic)
        self.labelTitle.setIndent(5)
        self.labelTitle.setObjectName("labelTitle")
        self.labelTitle.setText("Lista de Tokens")
        self.layoutTable.addWidget(self.labelTitle)
        
        self.tableWidget = QtWidgets.QTableWidget(self.tabLexic)
        self.tableWidget.setMinimumSize(QtCore.QSize(200, 200))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Nombre")
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Expresión")
        self.tableWidget.setHorizontalHeaderItem(1, item)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(240)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.verticalHeader().setDefaultSectionSize(60)
        self.tableWidget.verticalHeader().setMinimumSectionSize(60)
        self.tableWidget.verticalHeader().setMaximumSectionSize(120)
        self.tableWidget.horizontalHeader().setMinimumSectionSize(120)
        self.tableWidget.horizontalHeader().setMaximumSectionSize(240)
        
        self.layoutTable.addWidget(self.tableWidget)
        
        self.layoutTableBtns = QtWidgets.QHBoxLayout()
        self.layoutTableBtns.setSpacing(0)
        self.layoutTableBtns.setObjectName("layoutTableBtns")
        
        self.playButton = QtWidgets.QPushButton(self.tabLexic)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.playButton.setIcon(icon1)
        self.playButton.setIconSize(QtCore.QSize(28, 28))
        self.playButton.setObjectName("playButton")
        self.playButton.setText("    Probar Tokens")
        self.layoutTableBtns.addWidget(self.playButton)
        
        spacerItem = QtWidgets.QSpacerItem(80, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layoutTableBtns.addItem(spacerItem)
        
        self.editButtonTable = QtWidgets.QPushButton(self.tabLexic)
        self.editButtonTable.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/Edit_48px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.editButtonTable.setIcon(icon2)
        self.editButtonTable.setIconSize(QtCore.QSize(28, 28))
        self.editButtonTable.setObjectName("editButtonTable")
        self.editButtonTable.setDisabled(True)
        self.layoutTableBtns.addWidget(self.editButtonTable)
        
        self.delButtonTable = QtWidgets.QPushButton(self.tabLexic)
        self.delButtonTable.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/Minus_48px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.delButtonTable.setIcon(icon3)
        self.delButtonTable.setIconSize(QtCore.QSize(28, 28))
        self.delButtonTable.setObjectName("delButtonTable")
        self.delButtonTable.setDisabled(True)
        self.layoutTableBtns.addWidget(self.delButtonTable)
        
        self.layoutTableBtns.setStretch(0, 8)
        self.layoutTableBtns.setStretch(1, 3)
        self.layoutTableBtns.setSpacing(3)
        self.layoutTable.addLayout(self.layoutTableBtns)
        self.containerTop.addLayout(self.layoutTable)
        
        self.layoutList = QtWidgets.QVBoxLayout()
        self.layoutList.setObjectName("layoutList")
        
        self.label_subconjunto = QtWidgets.QLabel(self.tabLexic)
        self.label_subconjunto.setAlignment(QtCore.Qt.AlignCenter)
        self.label_subconjunto.setObjectName("label_subconjunto")
        self.label_subconjunto.setText("Subconjunto")
        self.layoutList.addWidget(self.label_subconjunto)
        
        self.tableSubconjunto = QtWidgets.QTableWidget(self.tabLexic)
        self.tableSubconjunto.verticalHeader().setSectionResizeMode(1)
        self.tableSubconjunto.setObjectName("tableSubconjunto")
        self.tableSubconjunto.setColumnCount(2)
        self.tableSubconjunto.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Id")
        self.tableSubconjunto.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Descripción")
        self.tableSubconjunto.setHorizontalHeaderItem(1, item)
        self.tableSubconjunto.horizontalHeader().setDefaultSectionSize(50)
        self.tableSubconjunto.horizontalHeader().setStretchLastSection(True)
        self.tableSubconjunto.horizontalHeader().setMinimumSectionSize(40)
        self.tableSubconjunto.horizontalHeader().setMaximumSectionSize(80)
        self.tableSubconjunto.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.layoutList.addWidget(self.tableSubconjunto)
        
        self.layoutListBtns = QtWidgets.QHBoxLayout()
        self.layoutListBtns.setSpacing(0)
        self.layoutListBtns.setObjectName("layoutListBtns")
        
        self.modificarButton = QtWidgets.QPushButton(self.tabLexic)
        self.modificarButton.setMinimumSize(QtCore.QSize(0, 35))
        self.modificarButton.setObjectName("modificarButton")
        self.modificarButton.setText("Modificar")
        self.modificarButton.setDisabled(True)
        self.layoutListBtns.addWidget(self.modificarButton)
        
        self.undoButton = QtWidgets.QPushButton(self.tabLexic)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icons/undo_48px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.undoButton.setIcon(icon4)
        self.undoButton.setIconSize(QtCore.QSize(28, 28))
        self.undoButton.setObjectName("undoButton")
        self.undoButton.setToolTip("Restaura los elementos del subconjunto")
        self.layoutListBtns.addWidget(self.undoButton)
        
        self.addButton = QtWidgets.QPushButton(self.tabLexic)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icons/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addButton.setIcon(icon5)
        self.addButton.setIconSize(QtCore.QSize(28, 28))
        self.addButton.setObjectName("addButton")
        self.layoutListBtns.addWidget(self.addButton)
        
        self.delButton = QtWidgets.QPushButton(self.tabLexic)
        self.delButton.setIcon(icon3)
        self.delButton.setIconSize(QtCore.QSize(28, 28))
        self.delButton.setObjectName("delButton")
        self.delButton.setDisabled(True)
        self.layoutListBtns.addWidget(self.delButton)
        
        self.layoutListBtns.setSpacing(3)
        
        self.layoutList.addLayout(self.layoutListBtns)
        self.containerTop.addLayout(self.layoutList)
        self.containerTop.setStretch(0, 6)
        self.containerTop.setStretch(1, 3)
        self.tabLexicLayout.addLayout(self.containerTop,stretch=6)
        
        self.line = QtWidgets.QFrame(self.tabLexic)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.tabLexicLayout.addWidget(self.line,stretch=1)
        
        self.containerBottom = QtWidgets.QHBoxLayout()
        self.containerBottom.setObjectName("containerBottom")
        
        self.tabWidgetBottom = QtWidgets.QTabWidget(self.tabLexic)
        self.tabWidgetBottom.setObjectName("tabWidgetBottom")
        #endregion: lexic tab variables instantiation 
        
        #region: Tab #1: conjunto
        self.tabConjunto = QtWidgets.QWidget()
        self.tabConjunto.setMinimumSize(QtCore.QSize(500, 0))
        self.tabConjunto.setObjectName("tabConjunto")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.tabConjunto)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        spacerItem1 = QtWidgets.QSpacerItem(70, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem1)
        
        self.formConjunto = QtWidgets.QFormLayout()
        self.formConjunto.setFormAlignment(QtCore.Qt.AlignCenter)
        self.formConjunto.setObjectName("formConjunto")
        self.formConjunto.setSpacing(20)
        
        self.label_nombreConjunto = QtWidgets.QLabel(self.tabConjunto)
        self.label_nombreConjunto.setObjectName("label_nombreConjunto")
        self.label_nombreConjunto.setText("Nombre del Token:")
        self.formConjunto.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_nombreConjunto)
        
        self.conjuntoNameEdit = QtWidgets.QLineEdit(self.tabConjunto)
        self.conjuntoNameEdit.setClearButtonEnabled(True)
        self.conjuntoNameEdit.setObjectName("conjuntoNameEdit")
        self.conjuntoNameEdit.setMaximumHeight(27)
        self.formConjunto.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.conjuntoNameEdit)
        
        self.label_expConjunto = QtWidgets.QLabel(self.tabConjunto)
        self.label_expConjunto.setObjectName("label_expConjunto")
        self.label_expConjunto.setText("Expresión:")
        self.formConjunto.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_expConjunto)
        
        self.conjuntoExpEdit = QtWidgets.QLineEdit(self.tabConjunto)
        self.conjuntoExpEdit.setClearButtonEnabled(True)
        self.conjuntoExpEdit.setObjectName("conjuntoExpEdit")
        self.conjuntoExpEdit.setMaximumHeight(27)
        self.formConjunto.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.conjuntoExpEdit)
        
        self.layoutBtnsConjunto = QtWidgets.QHBoxLayout()
        self.layoutBtnsConjunto.setObjectName("layoutBtnsConjunto")
        
        self.conjuntoAddButton = QtWidgets.QPushButton(self.tabConjunto)
        self.conjuntoAddButton.setMinimumSize(QtCore.QSize(110, 25))
        self.conjuntoAddButton.setObjectName("conjuntoAddButton")
        self.conjuntoAddButton.setText("Agregar Expresión")
        self.layoutBtnsConjunto.addWidget(self.conjuntoAddButton)
        
        self.conjuntoCreateButton = QtWidgets.QPushButton(self.tabConjunto)
        self.conjuntoCreateButton.setMinimumSize(QtCore.QSize(100, 25))
        self.conjuntoCreateButton.setObjectName("conjuntoCreateButton")
        self.conjuntoCreateButton.setText("Crear Token")
        self.layoutBtnsConjunto.addWidget(self.conjuntoCreateButton)
        
        self.formConjunto.setLayout(2, QtWidgets.QFormLayout.FieldRole, self.layoutBtnsConjunto)
        self.horizontalLayout_9.addLayout(self.formConjunto)
        spacerItem2 = QtWidgets.QSpacerItem(70, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem2)
        self.horizontalLayout_9.setStretch(1, 1)
        self.tabWidgetBottom.addTab(self.tabConjunto, "Token de Conjunto")
        #endregion: Tab #1: conjunto
        
        #region: Tab #2: expresiones
        self.tabExp = QtWidgets.QWidget()
        self.tabExp.setObjectName("tabExp")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.tabExp)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        spacerItem3 = QtWidgets.QSpacerItem(70, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem3)
        
        self.formExp = QtWidgets.QFormLayout()
        self.formExp.setSpacing(20)
        self.formExp.setLabelAlignment(QtCore.Qt.AlignCenter)
        self.formExp.setFormAlignment(QtCore.Qt.AlignCenter)
        self.formExp.setObjectName("formExp")
        
        self.label_nombreExp = QtWidgets.QLabel(self.tabExp)
        self.label_nombreExp.setObjectName("label_nombreExp")
        self.label_nombreExp.setText("Nombre del Token:")
        self.formExp.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_nombreExp)
        
        self.tokenNameEdit = QtWidgets.QLineEdit(self.tabExp)
        self.tokenNameEdit.setClearButtonEnabled(True)
        self.tokenNameEdit.setObjectName("tokenNameEdit")
        self.tokenNameEdit.setMaximumHeight(27)
        self.formExp.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.tokenNameEdit)
        
        self.label_expReg = QtWidgets.QLabel(self.tabExp)
        self.label_expReg.setObjectName("label_expReg")
        self.label_expReg.setText("Expresión Regular:")
        self.formExp.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_expReg)
        
        self.tokenExpEdit = QtWidgets.QLineEdit(self.tabExp)
        self.tokenExpEdit.setClearButtonEnabled(True)
        self.tokenExpEdit.setObjectName("tokenExpEdit")
        self.tokenExpEdit.setMaximumHeight(27)
        self.formExp.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.tokenExpEdit)
        
        self.tokenCreateButton = QtWidgets.QPushButton(self.tabExp)
        self.tokenCreateButton.setMinimumSize(QtCore.QSize(100,25))
        self.tokenCreateButton.setObjectName("tokenCreateButton")
        self.tokenCreateButton.setText("Crear Token")
        self.formExp.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.tokenCreateButton)
        
        self.horizontalLayout_8.addLayout(self.formExp)
        spacerItem4 = QtWidgets.QSpacerItem(70, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem4)
        self.horizontalLayout_8.setStretch(1, 1)
        self.tabWidgetBottom.addTab(self.tabExp, "Token de Expresión Regular")
        self.containerBottom.addWidget(self.tabWidgetBottom)
        #endregion: Tab #2: expresiones
        
        self.layoutConjunto = QtWidgets.QVBoxLayout()
        self.layoutConjunto.setObjectName("layoutConjunto")
        self.layoutConjunto.setSpacing(0)
        
        self.conjuntoLabel = QtWidgets.QLabel(self.tabLexic)
        self.conjuntoLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.conjuntoLabel.setObjectName("conjuntoLabel")
        self.conjuntoLabel.setText("Elementos del Conjunto")
        self.layoutConjunto.addWidget(self.conjuntoLabel)
        
        self.conjuntoList = QtWidgets.QListWidget(self.tabLexic)
        self.conjuntoList.setMinimumSize(QtCore.QSize(150, 100))
        self.conjuntoList.setObjectName("conjuntoList")
        self.layoutConjunto.addWidget(self.conjuntoList)
        
        self.delButtonElementosConjunto = QtWidgets.QPushButton(self.tabLexic)
        self.delButtonElementosConjunto.setObjectName("delButtonEC")
        self.delButtonElementosConjunto.setIcon(icon3)
        self.delButtonElementosConjunto.setIconSize(QtCore.QSize(28, 28))
        self.delButtonElementosConjunto.setDisabled(True)
        self.layoutConjunto.addWidget(self.delButtonElementosConjunto)
        
        self.ErrorLogLabel = QtWidgets.QLabel(self.tabLexic)
        self.ErrorLogLabel.setMinimumSize(QtCore.QSize(250, 150))
        self.ErrorLogLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.ErrorLogLabel.setObjectName("ErrorLogLabel")
        self.layoutConjunto.addWidget(self.ErrorLogLabel)
        self.ErrorLogLabel.setWordWrap(True) 
        self.ErrorLogLabel.close()
        
        self.layoutConjunto.setStretch(1,3)
        self.layoutConjunto.setStretch(2,6)
        self.layoutConjunto.setStretch(3,1)
        self.containerBottom.addLayout(self.layoutConjunto)
        self.containerBottom.setStretch(0, 1)
        self.tabLexicLayout.addLayout(self.containerBottom,stretch=3)
        self.tabWidgetBottom.setCurrentIndex(0)
        #endregion: lexic tab declaration 
        
        #region: listeners and variables of the lexic module
        
        #listeners:
        self.tokenCreateButton.clicked.connect(lambda:self.addTokenExpRegular())
        self.tabWidgetBottom.currentChanged.connect(lambda:self.changeTabContent())
        self.editButtonTable.clicked.connect(lambda:self.dialogEditMain())
        self.delButtonTable.clicked.connect(lambda:self.deleteItemTable())
        self.conjuntoCreateButton.clicked.connect(lambda:self.addTokenConjunto())
        self.conjuntoAddButton.clicked.connect(lambda:self.addExpConjunto())
        self.modificarButton.clicked.connect(lambda:self.dialogEdit())
        self.tableWidget.itemClicked.connect(lambda:self.editButtonTable.setDisabled(False))
        self.tableWidget.itemClicked.connect(lambda:self.delButtonTable.setDisabled(False))
        self.tableWidget.itemDoubleClicked.connect(lambda:self.dialogEditMain())
        self.tableSubconjunto.itemClicked.connect(lambda:self.modificarButton.setDisabled(False))
        self.tableSubconjunto.itemClicked.connect(lambda:self.delButton.setDisabled(False))
        self.tableSubconjunto.itemDoubleClicked.connect(lambda:self.dialogEdit())
        self.playButton.clicked.connect(lambda:self.dialogCheck())
        self.addButton.clicked.connect(lambda:self.addItemSubconjunto())
        self.delButton.clicked.connect(lambda:self.delItemSubconjunto())
        self.undoButton.clicked.connect(lambda:self.setDefaultSubconjunto())
        self.conjuntoList.itemClicked.connect(lambda:self.delButtonElementosConjunto.setDisabled(False))        
        self.delButtonElementosConjunto.clicked.connect(lambda:self.deleteItemConjuntoList())
        self.tokenExpEdit.textEdited.connect(lambda:self.updateErrorLog())
        self.tableSubconjunto.itemClicked.connect(lambda:self.modificarButton.setDisabled(False))
        self.tableSubconjunto.itemClicked.connect(lambda:self.delButton.setDisabled(False))
        
        #variables:
        self.analyzer = LexiconAnalyzer()    
        self.tabWidgetBottom.setCurrentIndex(0)
        self.tabWidgetBottom.setTabOrder(self.tokenNameEdit,self.tokenExpEdit)
        self.tabWidgetBottom.setTabOrder(self.tokenExpEdit,self.tokenCreateButton)
        
        #populating table subconjunto
        for subset in self.analyzer.getSubsetList():
            nameItem=QtWidgets.QTableWidgetItem(subset.getIdentifier())
            nameItem.setFlags(  QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            descItem=QtWidgets.QTableWidgetItem(subset.getDescription())
            descItem.setFlags(  QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            rowPosition = self.tableSubconjunto.rowCount()
            self.tableSubconjunto.insertRow(rowPosition)
            self.tableSubconjunto.setItem(rowPosition, 0, nameItem)
            self.tableSubconjunto.setItem(rowPosition, 1, descItem)
            self.tableSubconjunto.item(rowPosition,1).setToolTip(subset.getDescription())
        
        #endregion: listeners and variables of the lexic module
    
        self.tabMain.addTab(self.tabLexic, "Analizador Léxico")
       
        #region: syntactic tab
        
        #region: syntactic tab variables instantiation 
        self.tabSyntactic = QtWidgets.QWidget()
        self.tabSyntactic.setObjectName("tabSyntactic")
        self.tabMain.addTab(self.tabSyntactic, "Analizador Sintáctico")
        
        self.tabSyntacticLayout = QtWidgets.QVBoxLayout(self.tabSyntactic)
        self.tabSyntacticLayout.setObjectName("tabSyntacticLayout")
        
        self.tabWidget = QtWidgets.QTabWidget(self.tabSyntactic)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.West)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Triangular)
        self.tabWidget.setObjectName("tabWidget")
        #endregion: syntactic tab variables instantiation 
        
        #region: first Tab
        self.tab_prod = QtWidgets.QWidget()
        self.tab_prod.setObjectName("tab_prod")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.tab_prod)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        
        self.layout_prod_1 = QtWidgets.QVBoxLayout()
        self.layout_prod_1.setObjectName("layout_prod_1")
        
        self.main_table_area = QtWidgets.QScrollArea(self.tab_prod)
        self.main_table_area.setWidgetResizable(True)
        self.main_table_area.setObjectName("main_table_area")
        
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 397, 309))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        
        self.layout_table_vertical = QtWidgets.QVBoxLayout()
        self.layout_table_vertical.setObjectName("layout_table_vertical")
        
        self.layout_titleLabels = QtWidgets.QHBoxLayout()
        self.layout_titleLabels.setObjectName("layout_titleLabels")
        
        self.LI_label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.LI_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.LI_label.setIndent(38)
        self.LI_label.setObjectName("LI_label")
        self.LI_label.setText("Lado Izquierdo")
        self.layout_titleLabels.addWidget(self.LI_label)
         
        self.LD_label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.LD_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.LD_label.setIndent(1)
        self.LD_label.setObjectName("LD_label")
        self.LD_label.setText("Lado Derecho")
        self.layout_titleLabels.addWidget(self.LD_label)
        
        self.layout_table_vertical.addLayout(self.layout_titleLabels)
        
        self.main_scroll_area = QtWidgets.QScrollArea(self.scrollAreaWidgetContents)
        self.main_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.main_scroll_area.setWidgetResizable(True)
        self.main_scroll_area.setObjectName("main_scroll_area")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 377, 269))
        self.scrollAreaWidgetContents_2.setMaximumHeight(70)
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        
        self.layout_table_horizontal = QtWidgets.QHBoxLayout()
        self.layout_table_horizontal.setObjectName("layout_table_horizontal")
          
        self.number_lists = QtWidgets.QVBoxLayout()
        self.number_lists.setObjectName("number_lists")
        
        self.label_4 = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label_4.setObjectName("label_4")
        self.label_4.setText("1")
        self.number_lists.addWidget(self.label_4)
        
        self.layout_table_horizontal.addLayout(self.number_lists)
        
        self.left_lists = QtWidgets.QVBoxLayout()
        self.left_lists.setObjectName("left_lists")
        self.first_list = List(self.scrollAreaWidgetContents_2)
        self.first_list.setObjectName("first_list")
        self.first_list.setStyleSheet("#first_list::item:!focus{background-color:white;color:black;}")
        self.first_list.setMaximumHeight(60)
        
        self.first_list.setAcceptDrops(True)
        self.first_list.setDragEnabled(True)
        self.first_list.setDragDropOverwriteMode(True)
        self.first_list.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.first_list.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.first_list.setFlow(QtWidgets.QListView.LeftToRight)
        self.first_list.itemMoved.connect(lambda:self.analyseLeft(self.first_list))
        self.first_list.itemDragged.connect(lambda:self.removeElement(self.first_list))
        self.first_list.itemDragged.connect(lambda:self.deleteArea.setDisabled(True))
        self.first_list.dragStarted.connect(lambda:self.setParentList(1,self.first_list))
        self.first_list.dragStarted.connect(lambda:self.deleteArea.setDisabled(False))
        
        
        self.left_lists.addWidget(self.first_list)
        self.layout_table_horizontal.addLayout(self.left_lists)
        
        self.right_lists = QtWidgets.QVBoxLayout()
        self.right_lists.setObjectName("right_lists")
        self.second_list = List(self.scrollAreaWidgetContents_2)
        self.second_list.setObjectName("second_list")
        self.second_list.setStyleSheet("#second_list::item:!focus{background-color:white;color:black;}")
        self.second_list.setMaximumHeight(60)
        
        self.second_list.setAcceptDrops(True)
        self.second_list.setDragEnabled(True)
        self.second_list.setDragDropOverwriteMode(True)
        self.second_list.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.second_list.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.second_list.setFlow(QtWidgets.QListView.LeftToRight)
        self.second_list.itemMoved.connect(lambda:self.analyseRight(self.second_list))
        self.second_list.itemDragged.connect(lambda:self.analyseRight(self.second_list))
        self.second_list.itemDragged.connect(lambda:self.deleteArea.setDisabled(True))
        self.second_list.dragStarted.connect(lambda:self.deleteArea.setDisabled(False))
        self.second_list.dragStarted.connect(lambda:self.setParentList(1,self.second_list))
        
        self.right_lists.addWidget(self.second_list)
        self.layout_table_horizontal.addLayout(self.right_lists)
        
        self.btn_lists = QtWidgets.QVBoxLayout()
        self.btn_lists.setObjectName("btn_lists")
        self.first_btn = QtWidgets.QPushButton(self.scrollAreaWidgetContents_2)
        self.first_btn.setObjectName("first_btn")
        self.first_btn.setMaximumHeight(60)
        self.first_btn.setMaximumWidth(40)
        icon_cls = QtGui.QIcon()
        icon_cls.addPixmap(QtGui.QPixmap(":/icons/Minus_48px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.first_btn.setIcon(icon_cls)
        self.first_btn.setIconSize(QtCore.QSize(30, 30))
        self.first_btn.clicked.connect(lambda:self.deleteRow(self.first_btn))
        self.btn_lists.addWidget(self.first_btn)
        self.layout_table_horizontal.addLayout(self.btn_lists)
        
        self.verticalLayout_6.addLayout(self.layout_table_horizontal)
        self.main_scroll_area.setWidget(self.scrollAreaWidgetContents_2)
        self.layout_table_vertical.addWidget(self.main_scroll_area)
        self.horizontalLayout_6.addLayout(self.layout_table_vertical)
        self.main_table_area.setWidget(self.scrollAreaWidgetContents)
        self.layout_prod_1.addWidget(self.main_table_area)
        
        self.layout_table_horizontal.setStretch(0, 0)
        self.layout_table_horizontal.setStretch(1, 2)
        self.layout_table_horizontal.setStretch(2, 5)
        self.layout_table_horizontal.setStretch(3, 1)
        
        self.deleteArea = Label(self.tab_prod)
        self.deleteArea.setPixmap(QtGui.QPixmap(":/icons/trash-40.png"))
        self.deleteArea.setAlignment(QtCore.Qt.AlignCenter)
        self.deleteArea.setMinimumHeight(60)
        self.deleteArea.setAcceptDrops(True)
        self.deleteArea.setDisabled(True)
        self.deleteArea.setStyleSheet("border :2px grey; border-style : dashed;")
        self.layout_prod_1.addWidget(self.deleteArea)
        
        self.btn_add = QtWidgets.QPushButton(self.tab_prod)
        self.btn_add.setToolTip("Añadir una producción vacía a la gramática")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_add.setIcon(icon1)
        self.btn_add.setIconSize(QtCore.QSize(30, 30))
        self.btn_add.setObjectName("btn_add")
        self.layout_prod_1.addWidget(self.btn_add)
        
        self.layout_prod_1_btns = QtWidgets.QHBoxLayout()
        self.layout_prod_1_btns.setSpacing(6)
        self.layout_prod_1_btns.setObjectName("layout_prod_1_btns")
        
        self.layout_prod_1_btnsLeft = QtWidgets.QHBoxLayout()
        self.layout_prod_1_btnsLeft.setObjectName("layout_prod_1_btnsLeft")
        
        self.btn_play = QtWidgets.QPushButton(self.tab_prod)
        self.btn_play.setText("    Validar Producciones")
        self.btn_play.setToolTip("Comprueba validez de la gramática y crea tabla de control")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_play.setIcon(icon2)
        self.btn_play.setIconSize(QtCore.QSize(80, 50))
        self.btn_play.setObjectName("btn_play")
        self.layout_prod_1_btnsLeft.addWidget(self.btn_play)
        self.layout_prod_1_btns.addLayout(self.layout_prod_1_btnsLeft)
        
        self.layout_prod_1.addLayout(self.layout_prod_1_btns)
        self.layout_prod_1.setStretch(0, 6)
        self.layout_prod_1.setStretch(2, 2)
        self.horizontalLayout_3.addLayout(self.layout_prod_1)
        
        self.layout_prod_2 = QtWidgets.QVBoxLayout()
        self.layout_prod_2.setObjectName("layout_prod_2")
        self.layout_prod_2_NT = QtWidgets.QVBoxLayout()
        self.layout_prod_2_NT.setObjectName("layout_prod_2_NT")
        
        self.NT_label = QtWidgets.QLabel(self.tab_prod)
        self.NT_label.setAlignment(QtCore.Qt.AlignCenter)
        self.NT_label.setObjectName("NT_label")
        self.layout_prod_2_NT.addWidget(self.NT_label)
        self.NT_label.setText("No Terminales")
        
        self.NT_items = List(self.tab_prod)
        self.NT_items.setObjectName("NT_items")
        self.NT_items.setDragEnabled(True)
        self.layout_prod_2_NT.addWidget(self.NT_items)
        
        self.layout_prod_2_NT_btns = QtWidgets.QHBoxLayout()
        self.layout_prod_2_NT_btns.setObjectName("layout_prod_2_NT_btns")
        self.layout_prod_2_NT_btns.setSpacing(10)
        
        
        self.btn_addNT = QtWidgets.QPushButton(self.tab_prod)
        self.btn_addNT.setObjectName("btn_addNT")
        self.layout_prod_2_NT_btns.addWidget(self.btn_addNT)
        self.btn_addNT.setText("Agregar")
        
        self.btn_delNT = QtWidgets.QPushButton(self.tab_prod)
        self.btn_delNT.setObjectName("btn_delNT")
        self.btn_delNT.setDisabled(True)
        self.layout_prod_2_NT_btns.addWidget(self.btn_delNT)
        self.btn_delNT.setText("Eliminar")
    
        self.layout_prod_2_NT.addLayout(self.layout_prod_2_NT_btns)
        self.layout_prod_2_NT.setStretch(1, 7)
        self.layout_prod_2.addLayout(self.layout_prod_2_NT)
        self.layout_prod_2_T = QtWidgets.QVBoxLayout()
        self.layout_prod_2_T.setObjectName("layout_prod_2_T")
        
        self.T_label = QtWidgets.QLabel(self.tab_prod)
        self.T_label.setAlignment(QtCore.Qt.AlignCenter)
        self.T_label.setObjectName("T_label")
        self.layout_prod_2_T.addWidget(self.T_label)
        self.T_label.setText("Terminales")
        
        self.tokens = List(self.tab_prod)
        self.tokens.setDragEnabled(True)
        self.tokens.setObjectName("tokens")
        self.layout_prod_2_T.addWidget(self.tokens)
        
        self.layout_prod_2.addLayout(self.layout_prod_2_T)
        self.layout_prod_2.setSpacing(0)
        self.layout_prod_2.setStretch(0, 1)
        self.layout_prod_2.setStretch(1, 1)
        self.horizontalLayout_3.addLayout(self.layout_prod_2)
        
        self.horizontalLayout_3.setStretch(0, 6)
        self.horizontalLayout_3.setStretch(1, 2)
        
        self.tabWidget.addTab(self.tab_prod, "Producciones")
        #endregion: first Tab
        
        #region: second Tab
        self.tab_table = QtWidgets.QWidget()
        self.tab_table.setObjectName("tab_table")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.tab_table)
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        self.layout_table_1 = QtWidgets.QVBoxLayout()
        self.layout_table_1.setSpacing(9)
        self.layout_table_1.setObjectName("layout_table_1")
        
        self.scrollArea = QtWidgets.QScrollArea(self.tab_table)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        
        self.scrollAreaWidgetContentsCT = QtWidgets.QWidget()
        self.scrollAreaWidgetContentsCT.setObjectName("scrollAreaWidgetContentsCT")
        self.horizontalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContentsCT)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        
        self.controlTableWidget = QtWidgets.QTableWidget(self.scrollAreaWidgetContentsCT)
        self.controlTableWidget.setObjectName("controlTableWidget")    
        self.controlTableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
        self.horizontalLayout_2.addWidget(self.controlTableWidget)
        self.scrollArea.setWidget(self.scrollAreaWidgetContentsCT)
        self.layout_table_1.addWidget(self.scrollArea)
        self.layout_explain = QtWidgets.QVBoxLayout()
        self.layout_explain.setObjectName("layout_explain")
        
        self.label_explain_title = QtWidgets.QLabel(self.tab_table)
        self.label_explain_title.setIndent(12)
        self.label_explain_title.setObjectName("label_explain_title")
        self.label_explain_title.setText("Seleccione un ítem de la tabla o de la lista para obtener información de este")
        self.layout_explain.addWidget(self.label_explain_title)
        
        #region: new error msg tabs
        
        self.tabErrores = QtWidgets.QTabWidget(self.tab_table)
        self.tabErrores.setObjectName("tabErrores")
        
        #region: first error msg tab
        self.tabErrorExp = QtWidgets.QWidget()
        self.VLTabError1 = QtWidgets.QVBoxLayout(self.tabErrorExp)
        self.frame_newMsg = QtWidgets.QFrame(self.tabErrorExp)
        self.frame_newMsg.setObjectName("frame_newMsg")
    
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_newMsg)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_msg = QtWidgets.QLabel(self.frame_newMsg)
        self.label_msg.setObjectName("label_msg")
        self.label_msg.setText("El caso de error seleccionado por defecto:  Se encontró ... y se esperaba ...")
        self.verticalLayout_2.addWidget(self.label_msg)
        self.textEditMsg = QtWidgets.QPlainTextEdit(self.frame_newMsg)
        self.textEditMsg.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.textEditMsg.setPlaceholderText("Ingrese el mensaje de error para el caso ...")
        self.textEditMsg.setObjectName("textEditMsg")
        self.verticalLayout_2.addWidget(self.textEditMsg)
        self.btnChangeMsg = QtWidgets.QPushButton(self.frame_newMsg)
        self.btnChangeMsg.setObjectName("btnChangeMsg")
        self.btnChangeMsg.setText("Cambiar Mensaje")
        self.verticalLayout_2.addWidget(self.btnChangeMsg)
        self.tabErrores.addTab(self.tabErrorExp, "Mensaje de Error")
        self.VLTabError1.addWidget(self.frame_newMsg)
        #endregion: first error msg tab

        #region: second error msg tab - cod
        self.tabErrorCod = QtWidgets.QWidget()
        self.tabErrorCod.setObjectName("tabErrorCod")
        self.VLTabError2 = QtWidgets.QVBoxLayout(self.tabErrorCod)
        
        self.labelCodErrorMsg = QtWidgets.QPlainTextEdit(self.tabErrorCod)
        self.labelCodErrorMsg.setReadOnly(True)
        self.VLTabError2.addWidget(self.labelCodErrorMsg)
            
        self.tabErrores.addTab(self.tabErrorCod, "Código")
        #endregion: second error msg tab
        
        self.tabErrores.close()
        self.layout_explain.addWidget(self.tabErrores)
        
        #endregion: new error msg tabs
        
        #region: explanation tabs
        
        self.tabProd = QtWidgets.QTabWidget(self.tab_table)
        self.tabProd.setObjectName("tabProd")
        
        #region: first explanation tab
        self.tabProdExp= QtWidgets.QWidget()
        self.VLTabProd1 = QtWidgets.QVBoxLayout(self.tabProdExp)
        self.VLTabProd1.setObjectName("VLTabProd1")
        self.VLTabProd1.setContentsMargins(0,0,0,0)
        self.frame_explain = QtWidgets.QFrame(self.tabProdExp)
        self.frame_explain.setObjectName("frame_explain")
        
        #vertical layout for first explanation tab
        self.Vcontainer_explain = QtWidgets.QVBoxLayout(self.frame_explain)
        self.Vcontainer_explain.setObjectName("Vcontainer_explain")
        
        # container for titles of first explanation tab
        self.container_titles = QtWidgets.QHBoxLayout()
        self.container_titles.setObjectName("container_titles")
        
        self.LLeftTitle = QtWidgets.QHBoxLayout()
        self.LLeftTitle.setObjectName("LLeftTitle")
        self.LLeftTitle.setSpacing(0)
        self.label_left_side = QtWidgets.QLabel(self.frame_explain)
        self.label_left_side.setText("Lado Izquierdo")
        self.label_left_side.setObjectName("label_left_side")
        self.label_left_side.setAlignment(QtCore.Qt.AlignCenter)
        self.label_right_side = QtWidgets.QLabel(self.frame_explain)
        self.label_right_side.setText("Lado Derecho")
        self.label_right_side.setObjectName("label_right_side")
        self.label_right_side.setAlignment(QtCore.Qt.AlignCenter)
        self.LLeftTitle.addWidget(self.label_left_side)
        self.LLeftTitle.addWidget(self.label_right_side)
        self.LRightTitle = QtWidgets.QHBoxLayout()
        self.LRightTitle.setObjectName("LRightTitle")
        self.label_title_app = QtWidgets.QLabel(self.frame_explain)
        self.label_title_app.setText("Aplicación")
        self.label_title_app.setObjectName("label_title_app")
        self.label_title_app.setAlignment(QtCore.Qt.AlignCenter)
        self.LRightTitle.addWidget(self.label_title_app)
        self.container_titles.addLayout(self.LLeftTitle)
        self.container_titles.addLayout(self.LRightTitle)
        self.Vcontainer_explain.addLayout(self.container_titles,stretch=3)
        
        self.container_explain = QtWidgets.QHBoxLayout()
        
        self.container_explain.setObjectName("container_explain")
        self.layout_explain_prod = QtWidgets.QVBoxLayout()
        self.layout_explain_prod.setObjectName("layout_explain_prod")
       
        self.frame_prod_items = QtWidgets.QFrame(self.frame_explain)
        self.frame_prod_items.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_prod_items.setObjectName("frame_prod_items")
        self.layout_frame_2 = QtWidgets.QHBoxLayout(self.frame_prod_items)
        self.layout_frame_2.setObjectName("layout_frame_2")
        
        self.label_item_left = QtWidgets.QLineEdit(self.frame_prod_items)
        self.label_item_left.setReadOnly(True)
        self.label_item_left.setObjectName("label_item_left")
        self.layout_frame_2.addWidget(self.label_item_left)
        self.line_2 = QtWidgets.QFrame(self.frame_prod_items)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.layout_frame_2.addWidget(self.line_2)
        self.label_item_right = QtWidgets.QLineEdit(self.frame_prod_items)
        self.label_item_right.setReadOnly(True)
        self.label_item_right.setObjectName("label_item_right")
        self.layout_frame_2.addWidget(self.label_item_right)
        
        self.layout_explain_prod.addWidget(self.frame_prod_items)
        
        self.frame_prod_detail = QtWidgets.QFrame(self.frame_explain)
        self.frame_prod_detail.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_prod_detail.setObjectName("frame_prod_detail")
        self.layout_frame_3 = QtWidgets.QHBoxLayout(self.frame_prod_detail)
        self.layout_frame_3.setObjectName("layout_frame_3")
        
        self.label_detail_1 = QtWidgets.QLabel(self.frame_prod_detail)
        self.label_detail_1.setText("")
        self.label_detail_1.setObjectName("label_detail_1")
        self.layout_frame_3.addWidget(self.label_detail_1)
        self.label_detail_2 = QtWidgets.QLabel(self.frame_prod_detail)
        self.label_detail_2.setText("")
        self.label_detail_2.setObjectName("label_detail_2")
        self.layout_frame_3.addWidget(self.label_detail_2)
        
        self.layout_explain_prod.addWidget(self.frame_prod_detail)
        self.container_explain.addLayout(self.layout_explain_prod)
        
        self.layout_explain_app = QtWidgets.QVBoxLayout()
        self.layout_explain_app.setObjectName("layout_explain_app")

        self.label_application = QtWidgets.QLineEdit(self.frame_explain)
        self.label_application.setReadOnly(True)
        self.label_application.setText("")
        self.label_application.setObjectName("label_application")
        self.layout_explain_app.addWidget(self.label_application)
        
        
        self.layout_explain_app.setStretch(0, 3)
        self.layout_explain_app.setStretch(1, 5)
        self.container_explain.addLayout(self.layout_explain_app)
        self.container_explain.setStretch(0, 1)
        self.container_explain.setStretch(1, 1)
        self.Vcontainer_explain.addLayout(self.container_explain,stretch=7)
        self.VLTabProd1.addWidget(self.frame_explain)
        self.tabProd.addTab(self.tabProdExp, "Explicación de Producción")
        
        #endregion: first explanation tab
        
        #region: second explanation tab - sig
        self.tabProdSig = QtWidgets.QWidget()
        self.tabProdSig.setObjectName("tabProdSig")
        self.VLTabProd2 = QtWidgets.QVBoxLayout(self.tabProdSig)
        self.VLTabProd2.setContentsMargins(0,0,0,0)
        
        self.frameFirst = QtWidgets.QFrame(self.tabProdSig)
        self.frameFirst.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameFirst.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameFirst.setObjectName("frameFirst")
        self.verticalLayoutFF = QtWidgets.QVBoxLayout(self.frameFirst)
        self.verticalLayoutFF.setObjectName("verticalLayoutFF")
        self.verticalLayoutFF.setSpacing(0)
        
        self.labelTitleFirst = QtWidgets.QLabel(self.frameFirst)
        self.labelTitleFirst.setObjectName("labelTitleFirst")
        self.labelTitleFirst.setText("Título")
        self.verticalLayoutFF.addWidget(self.labelTitleFirst)

        self.HLFirst1 = QtWidgets.QHBoxLayout()
        self.HLFirst1.setSpacing(0)
        self.HLFirst1.setObjectName("HLFirst1")
        self.labelPATitle = QtWidgets.QLabel(self.frameFirst)
        self.labelPATitle.setObjectName("labelPATitle")
        self.labelPATitle.setText("Producción")
        self.HLFirst1.addWidget(self.labelPATitle,stretch=3)
        self.labelPA = QtWidgets.QLabel(self.frameFirst)
        self.labelPA.setObjectName("labelPA")
        self.HLFirst1.addWidget(self.labelPA,stretch=7)
        self.verticalLayoutFF.addLayout(self.HLFirst1,stretch=1)
        
        self.HLFirst1_2 = QtWidgets.QHBoxLayout()
        self.HLFirst1_2.setSpacing(0)
        self.HLFirst1_2.setObjectName("HLFirst1_2")
        self.labelFCTitle = QtWidgets.QLabel(self.frameFirst)
        self.labelFCTitle.setObjectName("labelFCTitle")
        self.labelFCTitle.setText("Conjunto Primero")
        self.HLFirst1_2.addWidget(self.labelFCTitle,stretch=3)
        self.labelFC = QtWidgets.QLabel(self.frameFirst)
        self.labelFC.setObjectName("labelFC")
        self.HLFirst1_2.addWidget(self.labelFC,stretch=7)
        self.verticalLayoutFF.addLayout(self.HLFirst1_2,stretch=1)
        
        self.labelExpFirst = QtWidgets.QPlainTextEdit(self.frameFirst)
        self.labelExpFirst.setReadOnly(True)
        self.labelExpFirst.setFocusPolicy(QtCore.Qt.NoFocus)
        self.labelExpFirst.setObjectName("labelExpFirst")
        self.verticalLayoutFF.addWidget(self.labelExpFirst,stretch=3)
            # hidden tab sig buttons and layout
        """
        self.HLFirst1_3 = QtWidgets.QHBoxLayout()
        self.HLFirst1_3.setObjectName("HLFirst1_3")
        self.btn_CFirst = QtWidgets.QPushButton(self.frameFirst)
        self.btn_CFirst.setObjectName("btn_CFirst")
        self.btn_CFirst.setText("Conjunto Primero")
        self.HLFirst1_3.addWidget(self.btn_CFirst)
        self.btn_CSig = QtWidgets.QPushButton(self.frameFirst)
        self.btn_CSig.setObjectName("btn_CSig")
        self.btn_CSig.setText("Conjunto Siguiente")
        self.HLFirst1_3.addWidget(self.btn_CSig)
        self.btn_back = QtWidgets.QPushButton(self.frameFirst)
        self.btn_back.setObjectName("btn_back")
        self.btn_back.setText("<<")
        self.HLFirst1_3.addWidget(self.btn_back)
        self.btn_next = QtWidgets.QPushButton(self.frameFirst)
        self.btn_next.setObjectName("btn_next")
        self.btn_next.setText(">>")
        self.HLFirst1_3.addWidget(self.btn_next)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.HLFirst1_3.addItem(spacerItem)
        self.HLFirst1_3.setSpacing(4)
        
        self.verticalLayoutFF.addLayout(self.HLFirst1_3,stretch=1)
        """
        self.VLTabProd2.addWidget(self.frameFirst)
    
        
        
        self.tabProd.addTab(self.tabProdSig, "Selección")
        #endregion: second explanation tab - sigr
        
        #region: third explanation tab - cod
        self.tabProdCod = QtWidgets.QWidget()
        self.tabProdCod.setObjectName("tabProdCod")
        self.VLTabProd3 = QtWidgets.QVBoxLayout(self.tabProdCod)
        
        self.labelCodExplain = QtWidgets.QPlainTextEdit(self.tabProdCod)
        self.labelCodExplain.setReadOnly(True)
        self.VLTabProd3.addWidget(self.labelCodExplain)
        
        
        self.tabProd.addTab(self.tabProdCod, "Código")
        #endregion: third explanation tab
        
        self.layout_explain.addWidget(self.tabProd)
        #endregion: explanation tabs
           
        self.layout_table_1.addLayout(self.layout_explain)
        self.layout_table_1.setStretch(0, 7)
        self.layout_table_1.setStretch(1, 3)
        self.horizontalLayout.addLayout(self.layout_table_1)
        
        self.layout_table_2 = QtWidgets.QVBoxLayout()
        self.layout_table_2.setObjectName("layout_table_2")
        self.layout_table_2.setSpacing(0)
        
        self.label_prodList_title = QtWidgets.QLabel(self.tab_table)
        self.label_prodList_title.setAlignment(QtCore.Qt.AlignCenter)
        self.label_prodList_title.setObjectName("label_prodList_title")
        self.label_prodList_title.setText("Producciones")
        self.layout_table_2.addWidget(self.label_prodList_title)
        
        self.proudction_listWidget = QtWidgets.QListWidget(self.tab_table)
        self.proudction_listWidget.setObjectName("proudction_listWidget")
        self.layout_table_2.addWidget(self.proudction_listWidget)
        
        self.btn_search = QtWidgets.QPushButton(self.tab_table)
        self.btn_search.setObjectName("btn_search")
        self.btn_search.setText("Abrir Editor")
        self.btn_search.setMinimumHeight(110)
        self.btn_search.setEnabled(False)
        self.layout_table_2.addWidget(self.btn_search)
        
        self.horizontalLayout.addLayout(self.layout_table_2)
        self.horizontalLayout.setStretch(0, 3)
        self.horizontalLayout.setStretch(1, 1)
        self.tabWidget.addTab(self.tab_table, "Tabla de Control")
        
        #endregion: second Tab
        
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.setTabEnabled(1,0)
        self.tabSyntacticLayout.addWidget(self.tabWidget)
        #endregion: syntactic tab
        
        #region: listeners and variables of the sintactic module
        
        # Listeners
        self.btn_add.clicked.connect(lambda:self.addLists())
        self.btn_addNT.clicked.connect(lambda:self.addNT())
        self.NT_items.itemClicked.connect(lambda:self.btn_delNT.setEnabled(True))
        self.btn_delNT.clicked.connect(lambda:self.delNT())
        self.btn_play.clicked.connect(lambda:self.play())
        self.btn_search.clicked.connect(self.openEditor)
        self.NT_items.dragStarted.connect(lambda:self.setParentList(0))
        self.tokens.dragStarted.connect(lambda:self.setParentList(0))
        
        # variables
        self.sintactic_module = SyntacticAnalyzer()
        self.RowCount = 0
        self.errorRowList = []
        self.parentList = 0
        self.parentRightList = None
        self.parentRightListItems = []
        
        
        # create production and link the visual and logic values to a ProductionRow object
        production = Production()
        row = ProductionRow(self.first_list,self.second_list,0)
        row.production = production
        self.sintactic_module.addProduction(production)
        self.productionRowList = [row]
        
        self.confirmSignal = False

        self.getSymbols()
        
        #endregion: listeners and variables of the sintactic module
        
        #region: analyzer variables and listeners:
        
        #listeners:
        self.tabMain.tabBarClicked.connect(lambda:self.changeAnalyzerTab())
        self.tabWidget.tabBarClicked.connect(lambda:self.changeSyntacticTab())
        
            #listeners for hidden buttons in tab - sig
        """
        self.btn_CFirst.clicked.connect(lambda:self.reloadExpFirst())
        self.btn_CSig.clicked.connect(lambda:self.reloadExpSig())
        self.btn_back.clicked.connect(lambda:self.backwardsStepExp())
        self.btn_next.clicked.connect(lambda:self.fordwardsStepExp())
        """
        #endregion: analyzer variables and listeners:
        
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        self.snapshot.setLists(self.analyzer.getTokenList(),
                                    self.analyzer.getSubsetList(),
                                    self.sintactic_module.getNTSymbolList(),
                                    self.sintactic_module.getProductionList(),
                                    self.sintactic_module.errorsDictionary)
        
    #region: analyzer window specific methods
    
    def changeAnalyzerTab(self):
        #moves variables when the tabMain widget is clicked

        # only when index is 1
        if self.tabMain.currentIndex() == 0:
            #clean syntactic module
            self.clearContents(0)
            #reload syntactic module
            self.loadContents(0)
            # #moving new terminal symbols from the lexic tab
            # self.tokens.clear()
            # self.getSymbols()
         
    def changeSyntacticTab(self):
        # to avoid problems with pyqt layouts when switching views,
        # reload the view when the syntactic tab is clicked so that
        # it won't crash on itself forcing the user to resize the window.
        self.clearContents(0)
        self.loadContents(0)
    #endregion: analyzer window specific methods
    
    #region: lexic tab specific methods
      
    
    def setSuperClass(self,super):
        self.superclass = super
        
    def reloadMainTable(self):
        #deleting every row in the table main 
        for index in range(self.tableWidget.rowCount()):
            self.tableWidget.removeRow(0)
        
        #populating table main
        for token in self.analyzer.getTokenList():
            
            nameItem=QtWidgets.QTableWidgetItem(token.getName())
            nameItem.setFlags(  QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            descItem=QtWidgets.QTableWidgetItem(token.getRegularExp())
            descItem.setFlags(  QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)
            self.tableWidget.setItem(rowPosition, 0, nameItem)
            self.tableWidget.setItem(rowPosition, 1, descItem)
        
    
    def dialogEditMain(self):
        #opens up main table edit dialogs
        if self.tableWidget.rowCount() == 0:
            self.popup('No existe ningún elemento en la lista de Tokens')
            return
        # check if the item we selected is exp, token or conj. token
        exp = self.tableWidget.item(self.tableWidget.currentRow(),0).text()
        token = self.analyzer.getTokenbyName(exp)
        
        if token.getTypeExp() == 0:
            # regular exp
            edit = EditMainDlgExp(self)
            edit.exec_()
        else:
            #conj. token
            edit = EditMainDlg(self)
            edit.exec_()
    
    def updateErrorLog(self):
        if self.tokenExpEdit.text()=='':
            self.ErrorLogLabel.setText("")
            return
        if self.analyzer.validateRegExpression(self.analyzer.convertInput(self.tokenExpEdit.text())) == True:
            # the expression is correct
            result_string ="Expresión Correcta"
            # Setting the color of the message
            color = "0,163,25"
        else:
            # the expression has an error, print it in the error log label
            e1,e2 = self.analyzer.validateRegExpression(self.analyzer.convertInput(self.tokenExpEdit.text()))
            result_string = "Se esperaba: \n"+ e1 + "\ny llegó: \n" + e2
            # Setting the color of the message
            color = "255,0,0"
            
        
        # Applying the color change by appending it to the stylesheet
        self.ErrorLogLabel.setStyleSheet("background:rgb(255, 255, 255); border: 1px solid grey; color:rgb("+color+");;")
        # Setting the result in the error label
        self.ErrorLogLabel.setText(result_string)
        
    def dialogEdit(self):
        #opens up subconjunto edit dialogs
        
        if self.tableSubconjunto.rowCount() == 0:
            self.popup('No existe ningún elemento en la lista de subconjuntos')
            return
        edit = EditSubconjuntoDlg(self)
        edit.exec_()
        self.modificarButton.setDisabled(True)
        self.delButton.setDisabled(True)
               
    def dialogCheck(self):
        #opens up check dialog to run lexic function
        if len(self.analyzer.getTokenList()) == 0:
            self.popup("No existe ningún token para realizar análisis léxico")
            return
      
        self.other_window = QtWidgets.QMainWindow()
        self.checkEd = EditorWindow()
        self.checkEd.setupUi(self.other_window, self)
        self.other_window.show()
        
    def addItemSubconjunto(self):
        #adds item to subconjunto table
        add = AddSubconjuntoDlg(self)
        add.exec_()
        
    def deleteItemConjuntoList(self):
        #deletes an item from the conjunto List
        if self.conjuntoList.count() == 0:
            self.popup('No existe ningún elemento en la lista')
            return
        r = self.conjuntoList.currentRow()
        self.conjuntoList.takeItem(r)
        self.delButtonElementosConjunto.setDisabled(True)
           
    def setDefaultSubconjunto(self):
        #resets subconjunto to default values

        #deleting every row in the table
        for index in range(self.tableSubconjunto.rowCount()):
            self.tableSubconjunto.removeRow(0)
            self.analyzer.removeSubset(0)
        
        #setting default values for the analyzer
        self.analyzer.setDefaultValues()
        
        #populating table subconjunto
        for subset in self.analyzer.getSubsetList():
            
            nameItem=QtWidgets.QTableWidgetItem(subset.getIdentifier())
            nameItem.setFlags(  QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            descItem=QtWidgets.QTableWidgetItem(subset.getDescription())
            descItem.setFlags(  QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            rowPosition = self.tableSubconjunto.rowCount()
            self.tableSubconjunto.insertRow(rowPosition)
            self.tableSubconjunto.setItem(rowPosition, 0, nameItem)
            self.tableSubconjunto.setItem(rowPosition, 1, descItem)
            self.tableSubconjunto.item(rowPosition,1).setToolTip(subset.getDescription())
            
        # disabling buttons that shoudln't be enabled as no item is selected
        self.delButton.setDisabled(True)
        self.modificarButton.setDisabled(True)
 
    def delItemSubconjunto(self):
        #deletes item from subconjunto table
        if self.tableSubconjunto.rowCount() == 0:
            self.popup('No existe ningún elemento en la lista de subconjuntos')
            return
        r = self.tableSubconjunto.currentRow()
        self.tableSubconjunto.removeRow(r)
        self.analyzer.removeSubset(r)
        self.delButton.setDisabled(True)
        self.modificarButton.setDisabled(True)
        self.reloadMainTable()

    def deleteItemTable(self):
        #deletes an item from the main table
        r = self.tableWidget.currentRow()
        tokenName = self.tableWidget.item(r,0).text()
        token = self.analyzer.getTokenbyName(tokenName)
        
        if token.getTypeExp() == 0:
            if self.sintactic_module.isTMUsed(tokenName):
                self.popup("El token a eliminar está siendo utilizado en la gramática,\n ¿Está seguro de querer eliminarlo?",1)
                if self.confirmSignal == False: return
            self.sintactic_module.removeTMSymbol(tokenName)
        else:
            for item in token.getSetExp():
                if self.sintactic_module.isTMUsed(tokenName+":"+item):
                    self.popup("El token a eliminar está siendo utilizado en la gramática,\n ¿Está seguro de querer eliminarlo?",1)
                    if self.confirmSignal == False: return
                    break
            for item in token.getSetExp():
                self.sintactic_module.removeTMSymbol(tokenName+":"+item)
                
        self.analyzer.removeToken(self.tableWidget.currentRow())
        self.tableWidget.removeRow(r)
        self.delButtonTable.setDisabled(True)
        self.editButtonTable.setDisabled(True)
        # disable control table
        self.btn_search.setEnabled(False)
        
        # disable control table tab 
        self.tabWidget.setTabEnabled(1,0)  
          
    def changeTabContent(self):
        #changes lista de conjunto name depending on current tab
        if self.tabWidgetBottom.currentIndex() == 0:
            self.conjuntoLabel.setText("Elementos del Conjunto")
            self.ErrorLogLabel.close()
            self.conjuntoList.show()
            self.conjuntoList.clear()
            self.conjuntoExpEdit.setText("")
            self.conjuntoNameEdit.setText("")
            self.delButtonElementosConjunto.show()

        elif self.tabWidgetBottom.currentIndex() == 1:
            self.conjuntoLabel.setText("Validar Expresión")
            self.conjuntoList.close()
            self.delButtonElementosConjunto.close()
            self.ErrorLogLabel.show()
            self.tokenExpEdit.setText("")
            self.tokenNameEdit.setText("")
            
    def addTokenExpRegular(self):
     
        #check if any prompt is empty, create popup if it is
        if self.tokenNameEdit.text() == '' or self.tokenExpEdit.text() == '':
            self.popup("Se debe especificar ambos campos para crear un Token")
            return
        # no '<..>' character should appear in the name of the new token
        reg = re.findall("^<.*>$",self.tokenNameEdit.text())
        if reg:
            self.popup("Nombre inválido, porfavor elija otro")
            return

        if self.analyzer.findToken(self.tokenNameEdit.text()):
            self.popup("Ya existe un token con el nombre especificado")
            return
        
        if not self.analyzer.validateRegExpression(self.analyzer.convertInput(self.tokenExpEdit.text())):
            self.popup("La expresión especificada es inválida")
            #this message should appear in 'validar expresion' listwidget
            return
        
        #add token
        self.analyzer.addToken(Token(self.tokenNameEdit.text(),0,self.tokenExpEdit.text()))
        
        
        nameItem=QtWidgets.QTableWidgetItem(self.tokenNameEdit.text())
        nameItem.setFlags(  QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        expItem=QtWidgets.QTableWidgetItem(self.tokenExpEdit.text())
        expItem.setFlags(  QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        #add row
        rowPosition = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rowPosition)
        self.tableWidget.setItem(rowPosition, 0, nameItem)
        self.tableWidget.setItem(rowPosition, 1, expItem)
        #clear prompts
        self.tokenNameEdit.setText("")
        self.tokenExpEdit.setText("")
        self.ErrorLogLabel.setText("")
        
        # disable editor
        self.btn_search.setEnabled(False)
        
        # disable control table tab 
        self.tabWidget.setTabEnabled(1,0)  
           
    def addExpConjunto(self):
        
        #adds exp to exp list
                 
        text = self.conjuntoExpEdit.text()
        #check if text is empty and create a popup
        if text == '':
            self.popup('Se debe especificar la expresión')
            return
        #check if expression is already on the list. If it is, we don't add it.
        model = self.conjuntoList.model()
        for index in range(model.rowCount()):
            item = self.conjuntoList.item(index)
            if item.text() == text:
                self.popup('La expresión \''+ text +' \'ya existe dentro del conjunto a crear')
                return
        self.conjuntoList.addItem(text)
        self.conjuntoExpEdit.setText("")

    def addTokenConjunto(self):
        
        #adds conjunto token to token table
        
        expGrp = []
        expTable = ""
        flag = True # used as control variable when adding an exp without the list
        reg = re.findall("^<.*",self.conjuntoNameEdit.text())
        if reg:
            self.popup("Nombre inválido, porfavor elija otro")
            return
    
        #iterate over every item in the list
        model = self.conjuntoList.model()
        for index in range(model.rowCount()):
            item = self.conjuntoList.item(index)
            expGrp.append(item.text())
            expTable += item.text() + ','
            if item.text() == self.conjuntoExpEdit.text():
                self.popup('La expresión \''+ self.conjuntoExpEdit.text() +' \'ya existe dentro del conjunto a crear')
                return
        if model.rowCount() == 0:
            if self.conjuntoNameEdit.text() == '' or self.conjuntoExpEdit.text() == '':
                self.popup('Se debe especificar el nombre y al menos un elemento del conjunto')
                return
            expTable = self.conjuntoExpEdit.text() + ','
            expGrp.append(expTable[:-1])
            flag = False
        if self.conjuntoNameEdit.text() == '':
            self.popup('Se debe especificar el nombre del conjunto')
            return
        if self.conjuntoExpEdit.text() != '' and flag:
            expTable += self.conjuntoExpEdit.text() + ','
            expGrp.append(self.conjuntoExpEdit.text())
        #create new token
        if self.analyzer.findToken(self.conjuntoNameEdit.text()):
            self.popup("Ya existe un token con el nombre especificado")
            return
        self.analyzer.addToken(Token(self.conjuntoNameEdit.text(),1,self.analyzer.convertInput(expGrp,1), expGrp))
            
        #add token to list
        nameItem=QtWidgets.QTableWidgetItem(self.conjuntoNameEdit.text())
        nameItem.setFlags(  QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        expItem=QtWidgets.QTableWidgetItem(expTable[:-1])
        expItem.setFlags(  QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        rowPosition = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rowPosition)
        self.tableWidget.setItem(rowPosition, 0, nameItem)
        self.tableWidget.setItem(rowPosition, 1, expItem)
        
        #clear list and every prompt
        self.conjuntoNameEdit.setText("")
        self.conjuntoExpEdit.setText("")
        self.conjuntoList.clear()
        
        # disable editor
        self.btn_search.setEnabled(False)
        
        # disable control table tab 
        self.tabWidget.setTabEnabled(1,0)  
    
    #endregion: lexic tab specific methods
    
    #region: syntactic tab specific methods
    
    def setParentList(self,Listtype, RList=None):
        #changes the value of the global variable parentList
        #for parentList -> 0: NT and T lists, 1: production list
        self.parentList = Listtype     
        # if the parent list is type 1, store its reference
        # and the items that it had before the drag operation
        if self.parentList == 1 and RList != None:   
            self.parentRightList = RList
            self.parentRightListItems = []
            for i in range (self.parentRightList.count()):
                if self.parentRightList.item(i).text() != '':
                    self.parentRightListItems.append(self.parentRightList.item(i).text())
    
    def openEditor(self):
        self.other_window = QtWidgets.QMainWindow()
        self.checkEd = EditorWindow()
        self.checkEd.setupUi(self.other_window, self, True)
        self.other_window.show()

    def play(self):
        # disable, and clean tab_table
        self.tabWidget.setTabEnabled(1,0)
        self.clearControlTable()

        # !!ERROR on trying to clean error marks when a new file is being loaded

        # clear errors
        if len(self.errorRowList) > 0: 
            for row in self.productionRowList:
                row.left_list.setStyleSheet("background-color:white;")
                row.right_list.setStyleSheet("background-color:white;")
            
            # for row in self.errorRowList:
            #     # check if list exists
            #     if row.left_list and row.right_list:
            #         row.left_list.setStyleSheet("background-color:white;")
            #         row.right_list.setStyleSheet("background-color:white;")
            
            self.errorRowList.clear()
            
        for i in range (self.NT_items.count()):
            self.NT_items.item(i).setBackground(QtGui.QColor(255, 255, 255))

        if len(self.productionRowList) == 1: 
            self.popup("La gramática debe constar de al menos dos producciones")
            return
        
        leftSideNull = False
        for row in self.productionRowList:
            if row.left_list.item(0) is None or row.left_list.item(0).text() == '': 
                row.left_list.setStyleSheet("background-color:yellow;")
                self.errorRowList.append(row)
                leftSideNull = True
        if leftSideNull:
            self.popup("No deben existir producciones sin el lado izquierdo definido")
            return
    
        self.sintactic_module.setInitialNt(self.sintactic_module.getNTSymbolList()[0])
        status, result = self.sintactic_module.validateGrammar()
        
        if status == GV_DEATH_ERROR:
            self.popup("La gramática tiene producciones muertas")
            for production in result:
                row = self.findLinked(production=production)
                self.errorRowList.append(row)
                
                for row in self.errorRowList:
                    row.left_list.setStyleSheet("background-color:red;")
                    row.right_list.setStyleSheet("background-color:red;")

        elif status == GV_UNUSEDNT_ERROR:
            self.popup("La gramática tiene simbolos no terminales no utilizados")
            
            for i in range (self.NT_items.count()):
                if self.NT_items.item(i).text() in result:
                    self.NT_items.item(i).setBackground(QtGui.QColor(255, 128, 128))
                    
        elif status == GV_UNREACHABLE_ERROR:
            self.popup("La gramática tiene producciones inalcanzables")
            for production in result:
                row = self.findLinked(production=production)
                self.errorRowList.append(row)
                
                for row in self.errorRowList:
                    row.left_list.setStyleSheet("background-color:red;")
                    row.right_list.setStyleSheet("background-color:red;")
        elif status == GV_ALIVE_EXECUTION_ERROR or status == GV_REACH_EXECUTION_ERROR:
            self.popup(f"Execution error code: {status}")
            
        else:
            status = self.sintactic_module.generateSelectionSets()
            if status != GV_OK:
                self.popup(f"Execution error code: {status}")
                return
            
            # enable control table tab 
            self.tabWidget.setTabEnabled(1,1)   
            
            status, ambiguousProductions = self.sintactic_module.validateAmbiguity()
            if status == GV_AMBIGUOUS_ERROR:
                self.popup("La gramática es ambigua")
                
                for production in ambiguousProductions:
                    row = self.findLinked(production=production,listP=1)
                    for sub_row in row:
                        self.errorRowList.append(sub_row)
                    
                    for row in self.errorRowList:
                        row.left_list.setStyleSheet("background-color:red;")
                        row.right_list.setStyleSheet("background-color:red;")

            elif status == GV_OK:
                self.popup("La gramática es LL(1) valida",icon=1,title="Aviso")
                # enable the editor
                self.btn_search.setEnabled(True)
                

            else:
                self.popup(f"Execution error code: {status}")
                return
            
            self.loadControlTable()
                
    def findLinked(self,left_side=None,right_side=None,production=None,index=None,listP=0):
        
        if left_side: 
            for row in self.productionRowList:
                if row.left_list == left_side:
                    return row
        elif right_side:
            for row in self.productionRowList:
                if row.right_list == right_side:
                    return row
        elif production:
            rowList = []
            for row in self.productionRowList:
                if row.production == production:
                    if listP:
                        rowList.append(row)
                    else:
                        return row
            return rowList
        elif index:
            for row in self.productionRowList:
                if row.index == index:    
                    return row
                
        return None

    def addNT(self):
        # Opens up the Add Non Terminal Dialog
        addNt = AddNonTerminalDialog(self)
        addNt.exec_()
    
    def delNT(self):
        # Deletes an item from NT_items list
        
        # get the item that was selected
        items=self.NT_items.selectedItems()
        if not items: 
            self.btn_delNT.setDisabled(True)        
            return
        
        # check if the item we're about to delete is being used in any of the rows
        found = False
        #search in left lists
        for i in range (self.left_lists.count()):
            if self.left_lists.itemAt(i).widget().item(0) is None: continue
            if self.left_lists.itemAt(i).widget().item(0).text() == items[0].text():
                found = True
                break
        
        #search in right lists
        for i in range (self.right_lists.count()):
            for j in range (self.right_lists.itemAt(i).widget().count()):
                if self.right_lists.itemAt(i).widget().item(j).text() == items[0].text():
                    found = True
            else:
                continue  # only executed if the inner loop did NOT break
            break  # only executed if the inner loop DID break
                        
        if found:                        
            # if the item we're about to delete was found, create a popup
            msg = "El no terminal está siendo usado en algunas producciones, \n ¿Desea eliminarlo? (se eliminarán cada una de sus instancias)"
            self.popup(msg,confirmButton=True,icon=0)
            if self.confirmSignal == False:
                # user pressed No, abort the operation
                return
        
        # delete item's ocurrences from the main table since it wasn't found or user agreed to delete it
        
        # delete from left lists
        for i in range (self.left_lists.count()):
            items_list = self.left_lists.itemAt(i).widget().findItems(items[0].text(),QtCore.Qt.MatchExactly)
            for item in items_list:
                self.left_lists.itemAt(i).widget().takeItem(self.left_lists.itemAt(i).widget().row(item))
        
        # delete from right lists
        for i in range (self.right_lists.count()):
            items_list = self.right_lists.itemAt(i).widget().findItems(items[0].text(),QtCore.Qt.MatchExactly)
            for item in items_list:
                self.right_lists.itemAt(i).widget().takeItem(self.right_lists.itemAt(i).widget().row(item))
        
        # delete the item from the NT_items list
        for item in items:
            self.NT_items.takeItem(self.NT_items.row(item))
            # delete item from sintactic_module
            self.sintactic_module.removeNTbyExp(item.text())
            self.btn_delNT.setDisabled(True) 
        
        # disable editor
        self.btn_search.setEnabled(False)
        
        # disable control table tab 
        self.tabWidget.setTabEnabled(1,0)   
    
    def editNT(self):
        # Edits an item from NT_items list
        
        # get the item that was selected
        items=self.NT_items.selectedItems()
        if not items: 
            self.btn_delNT.setDisabled(True)        
            return
        #---
            
    def addLists(self,production=None):
        # Adds a row to the main table
        
        # increment number of rows
        self.RowCount += 1
        
        # create new left list
        left_list = List(self.scrollAreaWidgetContents)
        left_list.setObjectName("left_list")
        left_list.setStyleSheet("#left_list::item:!focus{background-color:white;color:black;}")
        left_list.setAcceptDrops(True)
        left_list.setDragEnabled(True)
        left_list.setDragDropOverwriteMode(True)
        left_list.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        left_list.setMaximumHeight(60)
        left_list.setDefaultDropAction(QtCore.Qt.MoveAction)
        left_list.setFlow(QtWidgets.QListView.LeftToRight)
        left_list.itemMoved.connect(lambda:self.analyseLeft(left_list))
        left_list.itemDragged.connect(lambda:self.removeElement(left_list))
        left_list.itemDragged.connect(lambda:self.deleteArea.setDisabled(True))
        left_list.dragStarted.connect(lambda:self.deleteArea.setDisabled(False))
        
        self.left_lists.addWidget(left_list)
        
        # create new right list
        right_list = List(self.scrollAreaWidgetContents)
        right_list.setObjectName("right_list")
        right_list.setStyleSheet("#right_list::item:!focus{background-color:white;color:black;}")
        right_list.setFlow(QtWidgets.QListView.LeftToRight)
        right_list.setAcceptDrops(True)
        right_list.setDragEnabled(True)
        right_list.setDragDropOverwriteMode(True)
        right_list.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        right_list.setMaximumHeight(60)
        right_list.setDefaultDropAction(QtCore.Qt.MoveAction)
        right_list.itemMoved.connect(lambda:self.analyseRight(right_list))
        right_list.itemDragged.connect(lambda:self.analyseRight(right_list))
        right_list.itemDragged.connect(lambda:self.deleteArea.setDisabled(True))
        right_list.dragStarted.connect(lambda:self.deleteArea.setDisabled(False))
        right_list.dragStarted.connect(lambda:self.setParentList(1,right_list))
        
        self.right_lists.addWidget(right_list)
        
        #create left label
        label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        label.setText(str(self.RowCount+1))
        self.number_lists.addWidget(label)
        
        # create new close btn
        btn_close = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        btn_close.setText("")
        icon_cls = QtGui.QIcon()
        icon_cls.addPixmap(QtGui.QPixmap(":/icons/Minus_48px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        btn_close.setIcon(icon_cls)
        # btn_close.setMinimumSize(QtCore.QSize(30, 60))
        btn_close.setIconSize(QtCore.QSize(30, 30))
        btn_close.setMaximumHeight(60)
        btn_close.setMaximumWidth(40)
        btn_close.setObjectName("btn_close")
        btn_close.clicked.connect(lambda:self.deleteRow(btn_close))
        self.btn_lists.addWidget(btn_close)

        # increment size of scroll area
        self.scrollAreaWidgetContents_2.setMaximumHeight(70*(self.RowCount + 1))
        
        # create production and link the visual and logic values to a ProductionRow object
        if not production: 
            production = Production()
            self.sintactic_module.addProduction(production)
        
        row = ProductionRow(left_list,right_list,self.RowCount)
        row.production = production
        self.productionRowList.append(row)
        
        if production.getLeftSide():
            left_list.addItem(production.getLeftSide().getTag())
        if production.getRightSide():
            for symbol in production.getRightSide():
                right_list.addItem(symbol.getTag())
        
    def removeElement(self, left_list):
        # when an items is dragged, remove all linked items

        # updating sintactic module left side production
        row = self.findLinked(left_list)
        if row: 
            row.production.setLeftSide(None)
            return
           
    def analyseRight(self,right_list):
        # Processes right a right list when an item enters in it
        
        # get the items list
        items = []
        for i in range (right_list.count()):
            if right_list.item(i).text() != '':
                items.append(right_list.item(i).text())
        
        row = self.findLinked(right_side=right_list)
        if row: 
            # update left side of production
            if row.left_list.count() > 0:
                left_tag = row.left_list.item(0).text()            
                row.production.setLeftSide(self.sintactic_module.findNTsymbol(left_tag))
            else:
                row.production.setLeftSide(None)
            # update right side of production                
            self.sintactic_module.updateRightSideProduction(items, row.production)

            # disable editor
            self.btn_search.setEnabled(False)
            
            # disable control table tab 
            self.tabWidget.setTabEnabled(1,0)   
                   
    def analyseLeft(self,left_list):
        # Decides wheter a new item enters a left list or not
        
        # check if we already have an item in the left list  
        if left_list.count()>1 : 
            #check if that item is a terminal or non terminal
            reg = re.findall("^<.*>$", left_list.item(1).text())
            if reg: 
                # it's a non-terminal, let's replace the old item 
                left_list.takeItem(0)
                
                # updating sintactic module left side production
                row = self.findLinked(left_list)
                if row: 
                    # update left side of production
                    symbol = self.sintactic_module.findNTsymbol(left_list.item(0).text())
                    row.production.setLeftSide(symbol)
                    
                    # update right side of production
                    items = []
                    for i in range (row.right_list.count()):
                        if row.right_list.item(i).text() != '':
                            items.append(row.right_list.item(i).text())
                    self.sintactic_module.updateRightSideProduction(items, row.production)
                    
                    # disable editor
                    self.btn_search.setEnabled(False)
                    
                    # disable control table tab 
                    self.tabWidget.setTabEnabled(1,0)   
                                
            else:
                # it's a terminal, let's delete it and keep the old item
                # first check if the item was dragged from a right list
                if self.parentList == 1:
                    self.parentRightList.clear()
                    for item in self.parentRightListItems:
                        self.parentRightList.addItem(item)
                    self.parentRightList = None
                    self.parentRightListItems.clear()
                    
                left_list.takeItem(1) 
                self.popup("Los elementos de tipo terminal no pueden ir en el lado izquierdo de una producción")
        else:
                 
            # there's no items in the left list, check if the one
            # that just arrived is a terminal or non-terminal
            
            reg = re.findall("^<.*>$", left_list.item(0).text())
            
            if reg:
                # it's a non-terminal, let's accept it (just return since it's 
                # already in the list)
                
                # updating sintactic module left side production
                row = self.findLinked(left_list)
                if row: 
                    # update left side of production
                    symbol = self.sintactic_module.findNTsymbol(left_list.item(0).text())
                    row.production.setLeftSide(symbol)
                    
                    # update right side of production
                    items = []
                    for i in range (row.right_list.count()):
                        if row.right_list.item(i).text() != '':
                            items.append(row.right_list.item(i).text())
                    self.sintactic_module.updateRightSideProduction(items, row.production)
                    
                    # disable editor
                    self.btn_search.setEnabled(False)
                    
                    # disable control table tab 
                    self.tabWidget.setTabEnabled(1,0)  
                
                return
            else:
                # it's a terminal, let's delete it
                
                # first check if the item was dragged from a right list
                
                if self.parentList == 1:
                    self.parentRightList.clear()
                    for item in self.parentRightListItems:
                        self.parentRightList.addItem(item)
                    self.parentRightList = None
                    self.parentRightListItems.clear()
                
                left_list.takeItem(0)
                self.popup("Los elementos de tipo terminal no pueden ir en el lado izquierdo de una producción")
    
    def getSymbols(self):
        # gets all the symbols defined in the previous module and places them in tokens list
        self.sintactic_module.loadTerminalSymbols(self.analyzer.getTokenList())
        symbols = self.sintactic_module.getTMSymbolList()
        for symbol in symbols:
            
            self.tokens.addItem(symbol.getTag())
    
    def deleteRow(self,button):
        # deletes a row from the main table
      
        # index will carry the number of the row we're about to delete
        index = None
        # find the row based on the button that was pressed
        for i in range(self.btn_lists.count()):
            if self.btn_lists.itemAt(i).widget() == button:
                index = i              

        row = self.findLinked(index=index)
        if row in self.errorRowList: self.errorRowList.remove(row)

        if index == 0:    
            self.left_lists.itemAt(0).widget().clear()
            self.right_lists.itemAt(0).widget().clear()
            self.productionRowList[0].production.setRightSide([])
            self.productionRowList[0].production.setLeftSide(None)
            return

        # delete the button and its reference from the layout
        button.deleteLater()
        self.btn_lists.removeWidget(self.btn_lists.itemAt(index).widget())
        
        # delete the left list and its reference from the layout
        self.left_lists.itemAt(index).widget().deleteLater()
        self.left_lists.removeWidget(self.left_lists.itemAt(index).widget())
        
        # delete the right list and its reference from the layout
        self.right_lists.itemAt(index).widget().deleteLater()
        self.right_lists.removeWidget(self.right_lists.itemAt(index).widget())
        
        # delete the number and its reference from the layout
        self.number_lists.itemAt(index).widget().deleteLater()
        self.number_lists.removeWidget(self.number_lists.itemAt(index).widget())
        
        # adjust the scroll area
        self.RowCount -= 1
        self.scrollAreaWidgetContents_2.setMaximumHeight(70*(self.RowCount+1))
        
        # delete from production list
        
        self.sintactic_module.removeProduction(index)
        self.productionRowList.pop(index)
        
        # re count rows
        for i in range(self.number_lists.count()):
            self.number_lists.itemAt(i).widget().setText(str(i+1))
            self.productionRowList[i].index=i
        
    def loadControlTable(self):
        #populating control table
        # get control matrix
        matrix = self.sintactic_module.getControlMatrix()
        # get indexes of matrix
        rows, cols = self.sintactic_module.getControlMatrixIndex(True)
        
        # set column and row count
        self.controlTableWidget.setColumnCount(len(cols))
        # set view for control table
        
        if len(cols) > 8:
            self.controlTableWidget.horizontalHeader().setSectionResizeMode(0)
            self.controlTableWidget.horizontalHeader().setDefaultSectionSize(80)
            self.controlTableWidget.horizontalHeader().setMinimumSectionSize(80)
            self.controlTableWidget.horizontalHeader().setMaximumSectionSize(80)
        else: self.controlTableWidget.horizontalHeader().setSectionResizeMode(1)
        
        if len(rows) > 7:
            self.controlTableWidget.verticalHeader().setSectionResizeMode(0)
            self.controlTableWidget.verticalHeader().setDefaultSectionSize(60)
            self.controlTableWidget.verticalHeader().setMinimumSectionSize(60)
            self.controlTableWidget.verticalHeader().setMaximumSectionSize(60)
        else: self.controlTableWidget.verticalHeader().setSectionResizeMode(1)
    
        #self.controlTableWidget.verticalHeader().setSectionResizeMode(1)
            
        #self.controlTableWidget.verticalHeader().setDefaultSectionSize(60)
        #self.controlTableWidget.verticalHeader().setStretchLastSection(True)
        
        for row in rows.keys():
            #create new row
            rowPosition = self.controlTableWidget.rowCount()
            self.controlTableWidget.insertRow(rowPosition)
            for col in cols.keys():
                #add n items to the new row
                
                #convert number to string based on its value
                value = matrix[rows[row]][cols[col]]
                if value >= 0:
                    # it's a production
                    item = QtWidgets.QTableWidgetItem("P:"+str(int(value)))

                elif value == CM_AMBIGUOUS:
                    # it's an ambiguos point
                    item = QtWidgets.QTableWidgetItem("Ambiguo")   
                
                elif value == CM_POP_ADVANCE:
                    # it's the default pop, advance production
                    item = QtWidgets.QTableWidgetItem("PA")
                    
                elif value == CM_ACCEPTED:
                    # it's an accepted production
                    item = QtWidgets.QTableWidgetItem("Aceptado")
                    
                else:  
                    # it's an error
                    item = QtWidgets.QTableWidgetItem("Error")
                
                    
                item.setFlags(  QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.controlTableWidget.setItem(rowPosition,cols[col],item)    
        id = None
        #print(rows)
        for row in rows.keys():
            if len(row) > 5: 
                row = row[:5]
                break
                
        
        
        # set vertical and horizontal headers
        self.controlTableWidget.setVerticalHeaderLabels(rows.keys())
        self.controlTableWidget.setHorizontalHeaderLabels(cols.keys())
        
        # populate proudctions listWidget
        pIndex = 1
        for production in self.sintactic_module.getProductionList():
            self.proudction_listWidget.addItem(f'{pIndex}. {str(production)}')
            pIndex += 1
            
        # add listener to list and the control table     
        self.proudction_listWidget.itemClicked.connect(lambda:self.showProductionInfo(0))
        self.controlTableWidget.itemClicked.connect(lambda:self.showProductionInfo(1))

    def showProductionInfo(self,fromTable=False):
        # when an item is clicked, show its info in the information panel
        # fromTable: the index comes from an item that's on the matrix rather than the list
        if fromTable: 
            itemText =self.controlTableWidget.currentItem().text()
            # get index of the clicked cell
            index = itemText.split(":")[-1]
            if index.isnumeric():
                index = int(index) -1
            
            elif itemText == 'Aceptado' or itemText == 'PA':
                self.tabProd.close()
                self.tabErrores.close()
                self.label_explain_title.setText("Pop, Avanza" if itemText=='PA' else "Aceptado")
                self.label_explain_title.show()
                return
            
            elif itemText == 'Ambiguo':
                self.tabProd.close()
                self.tabErrores.close()

                # Ambiguous Symbol
                hh = self.controlTableWidget.horizontalHeaderItem(self.controlTableWidget.currentColumn())
                # Production left side
                vh = self.controlTableWidget.verticalHeaderItem(self.controlTableWidget.currentRow())
                
                self.label_explain_title.setText(self.sintactic_module.getAmbiguityExplanation(hh.text(), vh.text()))

                self.label_explain_title.show()
                return


            elif itemText == 'Error':
                self.tabProd.close()
                self.tabErrores.show()

                y = self.controlTableWidget.currentColumn()
                x = self.controlTableWidget.currentRow()
                self.label_explain_title.close()
                
                self.btnChangeMsg.clicked.connect(lambda:self.saveErrorMsg())

                errormsg = self.sintactic_module.getErrorMessage(x, y)

                if errormsg is not None:
                    self.label_msg.setText(errormsg)
                    self.textEditMsg.setPlaceholderText("Nuevo mensaje de error ...")
                else:
                    self.label_msg.setText("El caso de error seleccionado por defecto:  Se encontró ... y se esperaba ...")
                    self.textEditMsg.setPlaceholderText("Ingrese el mensaje de error para el caso ...")
                    self.textEditMsg.setPlainText("")
                
                self.labelCodErrorMsg.setPlainText(self.sintactic_module.explainedCodeError(x,y))
                
                return
            else: return
        else: index = self.proudction_listWidget.currentRow()
        
        production_str, production_voidable, production_app = self.sintactic_module.explainProduction(index)
        if production_str == GV_2NDANALISYS_EXECUTION_ERROR:
            self.popup(f"Execution error code: {production_str}")
        else:
            # EXPLANATION SELECTION SET
            aProduction = self.sintactic_module.getProductionList()[index]
            self.labelTitleFirst.setText(EXPTITLE1)
            self.labelFCTitle.setText('Conjunto Selección')
            
            self.labelFC.setText(str(aProduction.getSelectionSet()))
            
            strProduction = str(aProduction)
            
            strProduction = strProduction.replace('<', '&lt;')
            strProduction = strProduction.replace('>', '&gt;')

            self.labelPA.setText(strProduction)
            
            self.labelExpFirst.clear()
            explanation = f'SELECCION({index+1}) = {FIRSTW}{self.sintactic_module.printFirstSymbols(aProduction.getRightSide(), True)}'
            if production_voidable:
                explanation += f' U {NEXTW}({aProduction.getLeftSide()})'
            explanation += f'\n{FIRSTW}{self.sintactic_module.printFirstSymbols(aProduction.getRightSide(), True)} = {self.sintactic_module.printFirstSymbols(aProduction.getFirst(), False)}'
            if production_voidable:
                explanation += f'\n{NEXTW}({aProduction.getLeftSide()}) = {self.sintactic_module.printFirstSymbols(aProduction.getNext(),False)}'
            explanation += f'\nSELECCION({index+1}) = {self.sintactic_module.printFirstSymbols(aProduction.getSelectionSet(),False)}'

            self.labelExpFirst.insertPlainText(explanation)


            # START EXPLANATION LOOP
            """
            self.explanationStepIndex = 0
            #self.explanationStage = EXPFIRSTSET
            self.labelTitleFirst.setText(EXPTITLE1)
            self.explanationStage = EXPINTRODUCTION
            self.labelFCTitle.setText('Conjunto Selección')
            self.introExplanation, self.firstExplanation, self.nextExplanation = self.sintactic_module.explainSelectionSet(index)
            self.mountExplanationStep(self.introExplanation[0])
            """
            # CODE EXPLANATION
            #self.labelCodErrorMsg.insertPlainText(self.sintactic_module.explainedCodeProduction(index))
            self.labelCodExplain.insertPlainText(self.sintactic_module.explainedCodeProduction(index))
            self.labelCodExplain.verticalScrollBar().setValue(0)
            self.label_item_left.setText(production_str[0])    
            self.label_item_right.setText(production_str[1])
            #self.labelCodExplain.textCursor().movePosition(QtGui.QTextCursor.Start)
            

            self.label_detail_1.setText("Anulable: ")
            self.label_detail_2.setText("Sí" if production_voidable else "No")    
            self.label_detail_2.setAlignment(QtCore.Qt.AlignCenter)
            self.label_application.setText(production_app)
            self.label_application.setAlignment(QtCore.Qt.AlignCenter)
            
            self.tabProd.show()
            self.tabErrores.close()
            #self.label_explain_title.setText("Explicación de Producción")
            self.label_explain_title.close()

    def mountExplanationStep(self, aStep):
        # IDEA intercambiar el elemento de la posicion por la fuente y texto
        strProduction = ''
        if aStep.aProduction is not None:
            if aStep.aProduction[0] != ' ':
                fSymbol = aStep.aProduction[0]+""
                fSymbol = fSymbol.replace('<', '&lt;')
                fSymbol = fSymbol.replace('>', '&gt;')
                strProduction += f'{fSymbol} &rarr; '
            i = 0
            for symbol in aStep.aProduction[1:]:
                fSymbol = symbol+""
                fSymbol = fSymbol.replace('<', '&lt;')
                fSymbol = fSymbol.replace('>', '&gt;')
                if i == aStep.selectedInProduction:
                    strProduction += f'<font color="blue">{fSymbol}</font> '    
                else: strProduction += fSymbol + ' '
                i += 1
            
    
                
        strFirst = ''
        if aStep.firstset is not None:
            if aStep.selectedInFirst is not None:
                j = 0
                for symbol in aStep.firstset:
                    fSymbol = symbol+""
                    fSymbol = fSymbol.replace('<', '&lt;')
                    fSymbol = fSymbol.replace('>', '&gt;')
                    if j in aStep.selectedInFirst:
                        strFirst += f'<font color="red">{fSymbol}</font> '
                    else: strFirst += fSymbol + ' '
                    j += 1
            else:
                for symbol in aStep.firstset:
                    fSymbol = symbol+""
                    fSymbol = fSymbol.replace('<', '&lt;')
                    fSymbol = fSymbol.replace('>', '&gt;')
                    strFirst += fSymbol + ' '
 

        #exp = aStep.explanation.replace('<', '&lt;')
        # exp = exp.replace('>', '&gt;')
        # exp = exp.replace('\n', '<br>')
        self.labelExpFirst.clear()
        #self.labelExpFirst.setHtml(exp)
        self.labelPA.setText(strProduction)
        self.labelFC.setText(strFirst)
        self.labelExpFirst.insertPlainText(aStep.explanation)
        
        #self.labelFC.setText("<font color=\"blue\">ALGO1</font> <font color=\"red\">ALGO2</font>")  
    
    def saveErrorMsg(self):
        y = self.controlTableWidget.currentColumn()
        x = self.controlTableWidget.currentRow()
        
        msg = self.textEditMsg.toPlainText()
        if msg == "":
            self.popup("El mensaje de error no debe estar vacío")
            return
        self.controlTableWidget.item(x,y).setToolTip(msg)
        self.label_msg.setText(msg)

        self.sintactic_module.setErrorMessage(x, y, msg)
        
        self.btnChangeMsg.disconnect()

    def clearControlTable(self):
        # clears contents of the control table tab
        for index in range(self.controlTableWidget.rowCount()):
            self.controlTableWidget.removeRow(0)
        self.proudction_listWidget.clear()
        self.label_item_left.clear()
        self.label_item_right.clear()
        self.label_detail_1.clear()
        self.label_detail_2.clear()
        self.label_application.clear()
        self.tabErrores.close()
        self.tabProd.close()
        self.label_explain_title.setText("Selecciona un ítem de la tabla o de la lista para obtener información de este")
        self.label_explain_title.show()
    """
    def reloadExpFirst(self):
        self.labelTitleFirst.setText(EXPTITLE2)
        self.explanationStage = EXPFIRSTSET
        self.explanationStepIndex = 0
        self.labelFCTitle.setText('Conjunto Primero')
        self.mountExplanationStep(self.firstExplanation[self.explanationStepIndex])

    def reloadExpSig(self):
        self.labelTitleFirst.setText(EXPTITLE3)
        self.explanationStage = EXPNEXTSET
        self.explanationStepIndex = 0
        self.labelFCTitle.setText('Conjunto Siguiente')
        self.mountExplanationStep(self.nextExplanation[self.explanationStepIndex])
    
    def backwardsStepExp(self):
        # CONTROL POR ETAPAS
        if self.explanationStage == EXPINTRODUCTION:
            current = self.introExplanation
        elif self.explanationStage == EXPFIRSTSET:
            current = self.firstExplanation
        elif self.explanationStage == EXPNEXTSET:
            current = self.nextExplanation

        if self.explanationStepIndex > 0:
            self.explanationStepIndex -= 1
            self.mountExplanationStep(current[self.explanationStepIndex])
        else:

            if self.explanationStage == EXPFIRSTSET:
                self.labelTitleFirst.setText(EXPTITLE1)
                self.explanationStage = EXPINTRODUCTION
                self.labelFCTitle.setText('Conjunto Selección')
                self.explanationStepIndex = len(self.introExplanation) -1
                self.mountExplanationStep(self.introExplanation[self.explanationStepIndex])

            elif self.explanationStage == EXPNEXTSET:
                self.labelTitleFirst.setText(EXPTITLE2)
                self.explanationStage = EXPFIRSTSET
                self.labelFCTitle.setText('Conjunto Primero')
                self.explanationStepIndex = len(self.firstExplanation) -1
                self.mountExplanationStep(self.firstExplanation[self.explanationStepIndex])
    
    def fordwardsStepExp(self):
        # CONTROL POR ETAPAS
        if self.explanationStage == EXPINTRODUCTION:
            current = self.introExplanation
        elif self.explanationStage == EXPFIRSTSET:
            current = self.firstExplanation
        elif self.explanationStage == EXPNEXTSET:
            current = self.nextExplanation
        
        if self.explanationStepIndex < len(current)-1:
            self.explanationStepIndex += 1
            self.mountExplanationStep(current[self.explanationStepIndex])
        else:
            if self.explanationStage == EXPINTRODUCTION:
                self.labelTitleFirst.setText(EXPTITLE2)
                self.explanationStage = EXPFIRSTSET
                self.labelFCTitle.setText('Conjunto Primero')
                self.explanationStepIndex = 0
                self.mountExplanationStep(self.firstExplanation[self.explanationStepIndex])

            elif self.explanationStage == EXPFIRSTSET:
                self.labelTitleFirst.setText(EXPTITLE3)
                self.explanationStage = EXPNEXTSET
                self.labelFCTitle.setText('Conjunto Siguiente')
                self.explanationStepIndex = 0
                self.mountExplanationStep(self.nextExplanation[self.explanationStepIndex])
    """                     
    #endregion: syntactic tab specific methods

    #region: window common used methods
    def checkChanges(self):
        # returns true, if there are changes and user wants to save them
        # false otherwise

        if self.snapshot.verifyChanges(self.analyzer.getTokenList(),self.analyzer.getSubsetList(),self.sintactic_module.getNTSymbolList(),self.sintactic_module.getProductionList(), self.sintactic_module.errorsDictionary):
            self.popup("Tiene cambios sin guardar. ¿Desea guardar antes de crear el nuevo proyecto?", True)
            if self.confirmSignal:
                self.saveProject()
        return False

    def saveProject(self):
        if not self.saveFlag:
            self.saveFlag, _ = QtWidgets.QFileDialog.getSaveFileName(self.MainWindow,"Guardar Proyecto",'',
                "Json Files (*.json);;All Files (*)")
        if self.saveFlag:
            with open(self.saveFlag, 'w', encoding='utf8') as outfile:
                data = []
                # CONSEGUIR SALVABLE DE LÉXICO
                lexicon = self.analyzer.generateSaveData()

                # CONSEGUIR SALVABLE DE SINTÁCTICO
                syntactic = self.sintactic_module.generateSaveData()

                # GENERAR INFORMACION DE CONTROL
                control = self.generateControlInfo()

                data.append(control)
                data.append(lexicon)
                data.append(syntactic)

                # GUARDAR ARCHIVO
                json.dump(data, outfile, indent=4, sort_keys=True, ensure_ascii=False)
                outfile.close()
            self.snapshot = Snapshot()
            #CAMBIO SNAPCHOT
            self.snapshot.setLists(self.analyzer.getTokenList(),
                                    self.analyzer.getSubsetList(),
                                    self.sintactic_module.getNTSymbolList(),
                                    self.sintactic_module.getProductionList(),
                                    self.sintactic_module.errorsDictionary)
            self.popup("Cambios guardados con éxtio", False,1)
    
    def saveAsProject(self):
        newFileName, _ = QtWidgets.QFileDialog.getSaveFileName(self.MainWindow,"Guardar como",'',
            "Json Files (*.json);;All Files (*)")

        if newFileName:
            with open(newFileName, 'w', encoding='utf8') as outfile:
                data = []
                # CONSEGUIR SALVABLE DE LÉXICO
                lexicon = self.analyzer.generateSaveData()

                # CONSEGUIR SALVABLE DE SINTÁCTICO
                syntactic = self.sintactic_module.generateSaveData()

                # GENERAR INFORMACION DE CONTROL
                self.saveFlag = newFileName
                control = self.generateControlInfo()

                data.append(control)
                data.append(lexicon)
                data.append(syntactic)

                # GUARDAR ARCHIVO
                json.dump(data, outfile, indent=4, sort_keys=True, ensure_ascii=False)
                outfile.close()
            self.snapshot = Snapshot()
            #CAMBIO SNAPCHOT
            self.snapshot.setLists(self.analyzer.getTokenList(),
                                    self.analyzer.getSubsetList(),
                                    self.sintactic_module.getNTSymbolList(),
                                    self.sintactic_module.getProductionList(),
                                    self.sintactic_module.errorsDictionary)
            self.popup("Cambios guardados con éxtio", False,1)

    def newProject(self):        
        if not self.checkChanges(): # there are no changes or user doesnt' want to save them
            self.tabMain.setCurrentIndex(0)
            self.tabWidget.setTabEnabled(1,0)
            self.currentProjectName = ''
            self.analyzer = LexiconAnalyzer()
            self.sintactic_module = SyntacticAnalyzer()
            initialProduction = Production()
            self.sintactic_module.addProduction(initialProduction)

            self.clearContents() # clear interface
            self.saveFlag = None
            #Solamente hay que refrescar la ventana
            self.snapshot = Snapshot()

            self.snapshot.setLists(self.analyzer.getTokenList(),
                                    self.analyzer.getSubsetList(),
                                    self.sintactic_module.getNTSymbolList(),
                                    self.sintactic_module.getProductionList(),
                                    self.sintactic_module.errorsDictionary)

    def openProject(self, path=None):
        
        if not self.checkChanges(): # there are no changes or user doesnt' want to save them
            if not path:
                path, _ = QtWidgets.QFileDialog.getOpenFileName(self.MainWindow, "Abrir Proyecto", '',
                        "Json Files (*.json);;All Files (*)")
                self.saveFlag = path
            if path:
                self.tabMain.setCurrentIndex(0)
                self.tabWidget.setTabEnabled(1,0)
                #self.tab_table.setDisabled(True)
                #
                #
                with open(path, encoding='utf8') as infile:
                    try:    
                        projectl = json.load(infile)
                    except:
                        self.popup("No se pudo abrir el archivo")
                        return
                    
                    # PRIMERO VERIFICAR INFO DE CONTROL
                    try:
                        control = projectl[0]
                        lexicon = projectl[1]
                        syntactic = projectl[2]
                    except:
                        self.popup("El archivo no contiene un proyecto valido")
                        return
                    
                    if control.get('status'):
                        self.analyzer = LexiconAnalyzer()
                        self.sintactic_module = SyntacticAnalyzer()
                        self.currentProjectName = control.get('projectName')

                        try:                    
                            # OBTENER MODULO LÉXICO
                            self.analyzer.loadLexiconData(lexicon)

                            if control.get('status') == SYNTACTIC: 
                                # OBTENER MODULO SINTACTICO
                                self.sintactic_module.loadTerminalSymbols(self.analyzer.getTokenList())                                
                                self.sintactic_module.loadSyntacticData(syntactic)

                            # ACTUALIZAR VISTA DE PROJECTO
                            self.loadContents()
                            self.snapshot = Snapshot()
                            self.snapshot.setLists(self.analyzer.getTokenList(),
                                        self.analyzer.getSubsetList(),
                                        self.sintactic_module.getNTSymbolList(),
                                        self.sintactic_module.getProductionList(),
                                        self.sintactic_module.errorsDictionary)
                        except:
                            self.popup("El proyecto esta corrupto")
                            return
                    else:
                        self.popup("El archivo no contiene un proyecto valido")

                    infile.close()
                # Metodo de carga de modulos
            
    def openHelp(self):
        #executes help windows  
        
        helpw = Help_Window()
        helpw.exec_()
             
        # self.help_window = QtWidgets.QMainWindow()
        # self.helpw = Help_Window()
        # self.helpw.setupUi(self.help_window)
        # self.help_window.show()
        
                             
    def generateProjectCode(self):
        
        if self.currentProjectName != '':
            self.popup("Seleccione el tipo de interfaz para el código generado",1,icon=2,
                   yesM="Consola",noM="Editor (ventana) ")
            dirpath = QtWidgets.QFileDialog.getExistingDirectory(self.MainWindow, 'Abrir directorio',
                                        options=QtWidgets.QFileDialog.ShowDirsOnly)
            if dirpath:
                codeGenerator = CodeGenerator(dirpath, self.currentProjectName, self.analyzer,self.sintactic_module)    
                if self.confirmSignal:    
                    # CONSOLE
                    status, project = codeGenerator.buildProject(False)
                elif self.confirmSignal is False:
                    # EDITOR(WINDOW)
                    status, project = codeGenerator.buildProject(True)
                    
                if project == PSTATUS0:
                    self.popup("No se pudo generar el código: El proyecto carece de definición para Analizador Léxico y Sintáctico")
                elif project == PSTATUS1:  
                    self.popup("Se ha generado el código del Analizador Léxico",icon=1)
                elif project == PSTATUS2:
                    self.popup("Se ha generado el código del Analizador Sintáctico",icon=1)
                elif project == PSTATUS5:
                    self.popup("Ya existe un directorio con el nombre"+self.currentProjectName)
                
        else:
            self.popup("Para generar el código de su proyecto primero debe guardarlo ¿Quiere guardar su proyecto?", True)
            if self.confirmSignal:
                self.saveProject()
                if self.currentProjectName != '':
                    self.generateProjectCode()
            
    
    def generateControlInfo(self):
        if self.saveFlag != '' or self.saveFlag is not None:
            project = self.saveFlag.split('/')[-1].split('.')[:-1]
            projectName = ""
            projectName = projectName.join(project)
            self.currentProjectName = projectName


            lastMod = str(datetime.now())
            status = LEXICON
            if(len(self.sintactic_module.getNTSymbolList())>0 or len(self.sintactic_module.getProductionList())):
                status = SYNTACTIC
            
            control = {
                "projectName": projectName,
                "lastMod": lastMod,
                "status": status
            }
            return control
        return None
    
    def openRepositorySite(self):
        webbrowser.open("https://github.com/JuanECG/Herramienta-de-apoyo-a-compiladores")
    
    def openFormSite(self):
        webbrowser.open("https://docs.google.com/forms/d/e/1FAIpQLSfDhviJA9dvnOwS87IjFpB8zueSKmuwzwJkVa6zLgqfC4xmhw/viewform?usp=sf_link")

    def clearContents(self,lex=True,synt=True): 
        
        if lex:
            # clearing lexic tab:
            
            # clearing ErrorLogLabel and text edits
            self.ErrorLogLabel.setText("")
            self.conjuntoExpEdit.setText("")
            self.conjuntoNameEdit.setText("")
            self.tokenNameEdit.setText("")
            self.tokenExpEdit.setText("")
            #setting default subconjunto contents
            self.setDefaultSubconjunto()
            #clear token list
            self.analyzer.clearTokenList() 
            #deleting every row in the table main 
            for index in range(self.tableWidget.rowCount()):
                self.tableWidget.removeRow(0)

        if synt:
            # clearing syntactic tab:
            
            # clears old content
            self.first_list.setStyleSheet("#first_list{background-color:white;}#first_list::item:!focus{background-color:white;color:black;}")
            self.second_list.setStyleSheet("#second_list{background-color:white;}#second_list::item:!focus{background-color:white;color:black;}")
            self.NT_items.clear()
            self.tokens.clear()
            
            # get len of all productions
            index = len(self.productionRowList)-1
            
            while index >0:
                #delete visual row
                
                # delete the button and its reference from the layout
                self.btn_lists.itemAt(index).widget().deleteLater()
                self.btn_lists.removeWidget(self.btn_lists.itemAt(index).widget())
                
                # delete the left list and its reference from the layout
                self.left_lists.itemAt(index).widget().deleteLater()
                self.left_lists.removeWidget(self.left_lists.itemAt(index).widget())
                
                # delete the right list and its reference from the layout
                self.right_lists.itemAt(index).widget().deleteLater()
                self.right_lists.removeWidget(self.right_lists.itemAt(index).widget())
                
                # delete the number and its reference from the layout
                self.number_lists.itemAt(index).widget().deleteLater()
                self.number_lists.removeWidget(self.number_lists.itemAt(index).widget())
                
                # adjust the scroll area
                self.RowCount -= 1
                self.scrollAreaWidgetContents_2.setMaximumHeight(70*(self.RowCount+1))
                #delete row from production list
                
                self.productionRowList.pop(index)
                #repeat until index == 0
                index -= 1
            #self.sintactic_module.removeProduction(0)
            #if not lex: self.productionRowList.pop(0)
            self.left_lists.itemAt(0).widget().clear()
            self.right_lists.itemAt(0).widget().clear()
        
    def loadContents(self,lex=True,synt=True):
    
        if lex:
            # loading lexic contents
            
            #deleting every row in the table subconjunto
            for index in range(self.tableSubconjunto.rowCount()):
                self.tableSubconjunto.removeRow(0)
                
            #populating table subconjunto
            for subset in self.analyzer.getSubsetList():
                
                nameItem=QtWidgets.QTableWidgetItem(subset.getIdentifier())
                nameItem.setFlags(  QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                descItem=QtWidgets.QTableWidgetItem(subset.getDescription())
                descItem.setFlags(  QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                rowPosition = self.tableSubconjunto.rowCount()
                self.tableSubconjunto.insertRow(rowPosition)
                self.tableSubconjunto.setItem(rowPosition, 0, nameItem)
                self.tableSubconjunto.setItem(rowPosition, 1, descItem)
            
            self.reloadMainTable()
        
        if synt:
            # loading syntactic contents
            
            # loads contents from saved file
            self.getSymbols()
            #load Non-Terminals
            for symbol in self.sintactic_module.getNTSymbolList():
                self.NT_items.addItem(symbol.getTag())
            #load Productions
            if len(self.sintactic_module.getProductionList()) > 0:
                production = self.sintactic_module.getProductionList()[0]
                if(production.getLeftSide()):
                    self.first_list.addItem(production.getLeftSide().getTag())
                if production.getRightSide():
                        for symbol in production.getRightSide():
                            self.second_list.addItem(symbol.getTag())
                    
                self.productionRowList[0].production = production
                    
                if len(self.sintactic_module.getProductionList()) > 1: 
                        for i in range(1,len(self.sintactic_module.getProductionList())):
                            self.addLists(self.sintactic_module.getProductionList()[i])
                        # for production in self.sintactic_module.getProductionList()[1:]:
                        #     self.addLists(production)
    
    def popup(self,msgText, confirmButton=False, icon=0,title="",yesM="Sí",noM="No"):
        #basic popup
        if confirmButton:
            msg = QMessageBox()
            msg.setWindowTitle("Advertencia")
            msg.setText(msgText)
            if icon == 0: msg.setIcon(QMessageBox.Warning)
            if icon == 1: msg.setIcon(QMessageBox.Information)
            if icon == 2: msg.setIcon(QMessageBox.Question)
            if icon == 3: msg.setIcon(QMessageBox.Critical)
            #msg.buttonClicked.connect(self.popup_clicked)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.button(QMessageBox.Yes).setText(yesM)
            msg.button(QMessageBox.No).setText(noM)
            msg.setWindowIcon(QtGui.QIcon(':/icons/Variable_48px.png'))
            msg.buttonClicked.connect(lambda:self.popup_c(msg))
            x = msg.exec_()  
            return
        msg = QMessageBox()
        msg.setWindowTitle("Advertencia")
        msg.setText(msgText)
        
        if icon == 0: msg.setIcon(QMessageBox.Warning)
        if icon == 1: msg.setIcon(QMessageBox.Information)
        if icon == 2: msg.setIcon(QMessageBox.Question)
        if icon == 3: msg.setIcon(QMessageBox.Critical)
        
        msg.setWindowIcon(QtGui.QIcon(':/icons/Variable_48px.png'))
        x = msg.exec_()
        return
        
    def popup_c(self,msg):
        if msg.clickedButton() == msg.button(QMessageBox.Yes):
            # YES pressed
            self.confirmSignal = True
        elif msg.clickedButton() == msg.button(QMessageBox.No):
            # NO pressed
            self.confirmSignal = False
            
    def popup_clicked(self, i):
        # establish procedures when a popup with yes or no buttons is created
        
        if i.text() == '&Yes':
            # yes procedure
            self.confirmSignal = True
        elif i.text() == '&No':
            # No procedure
            self.confirmSignal = False
    
    #endregion: window common used methods
    
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    
    splash_pix = QtGui.QPixmap(":/icons/gadun.jpg")
    splash = QtWidgets.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.show()
    
    def login():
        splash.close()
        MainWindow = QtWidgets.QMainWindow()
        ui = Ui_MainWindow()
        ui.setupUi(MainWindow)
        MainWindow.show()
        
    QtCore.QTimer.singleShot(2500, login)
    sys.exit(app.exec_())