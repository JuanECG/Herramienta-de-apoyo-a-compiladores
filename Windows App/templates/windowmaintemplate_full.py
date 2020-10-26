from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import sys
from contextlib import redirect_stdout
from PyQt5.QtGui import QFont
import re
from lexicon import *
from syntactic import *

#CONSTANTS
LX_EXECUTION_ERROR = f'22 \nError en definición de Tokens'
SX_EXECUTION_ERROR = f'23 \nPosible error en definición de Producción'

class EditorWindow(object):
    def setupUi(self, MainWindow, lexiconAnalyzer = None, allowSyntax = False, syntacticAnalizer = None):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(700, 570)
        #icon = QtGui.QIcon()
        #icon.addPixmap(QtGui.QPixmap(":/icons/Variable_48px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        #MainWindow.setWindowIcon(icon)

        # PERSONALIZACIÓN
        self.window = MainWindow

        self.textFormat = QtGui.QTextCharFormat()
        self.textFormat.setFontFamily("Arial")
        self.textFormat.setFontPointSize(12)

        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.runButton = QtWidgets.QPushButton(self.centralwidget)
        self.runButton.setGeometry(QtCore.QRect(10, 340, 50, 20))
        self.runButton.setObjectName("runButton")
        #iconPlay = QtGui.QIcon()
        #iconPlay.addPixmap(QtGui.QPixmap(":/icons/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        #self.runButton.setIcon(iconPlay)

        self.optionBox = QtWidgets.QComboBox(self.centralwidget)
        self.optionBox.setGeometry(QtCore.QRect(570, 340, 120, 20))
        self.optionBox.setObjectName("optionBox")
        self.optionBox.addItem("")
        self.optionBox.addItem("")


        self.numEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.numEdit.setGeometry(QtCore.QRect(10, 10, 30, 320))
        self.numEdit.setObjectName("numEdit")
        self.numEdit.setFont(font)
        self.numEdit.setTextInteractionFlags (QtCore.Qt.NoTextInteraction)
        self.numEdit.setFocusPolicy(QtCore.Qt.NoFocus)
        self.numEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.numEdit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.campEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.campEdit.setGeometry(QtCore.QRect(40, 10, 650, 320))
        self.campEdit.setFont(font)
        self.campEdit.setObjectName("campEdit")

    
        self.resultEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.resultEdit.setGeometry(QtCore.QRect(10, 370, 677, 157))
        self.resultEdit.setObjectName("resultEdit")
        self.resultEdit.setReadOnly(True)
        self.resultEdit.setFont(font)
        self.resultEdit.setFocusPolicy(QtCore.Qt.NoFocus)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 700, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # EDITOR CONFIGURATION
        self.setupFileMenu(MainWindow)
        self.errorSel = None
        self.errorLine = None
        self.toggled = False
        self.justLex = True
        self.lexFlag = True

        # OBTENCIÓN DE MÓDULOS
        
        self.lexA = lexiconAnalyzer
        if allowSyntax:
            self.synA = syntacticAnalizer

        # COMBOBOX
        if allowSyntax:
            self.optionBox.currentIndexChanged.connect(self.changeOption)
        else:
            self.optionBox.setEnabled(False)
        # BUTTONS CONF
        self.runButton.clicked.connect(self.runFull)
        #self.toggleButton.clicked.connect(self.toggleWindow)
        
        self.campEdit.cursorPositionChanged.connect(self.disselecterror)
        self.campEdit.textChanged.connect(self.numeration)
        #
        self.campEdit.verticalScrollBar().valueChanged.connect(
            self.numEdit.verticalScrollBar().setValue
        )
        self.numEdit.verticalScrollBar().valueChanged.connect(
            self.campEdit.verticalScrollBar().setValue)


        self.retranslateUi(MainWindow)
        
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Analizador Léxico-Sintáctico"))
        self.runButton.setText(_translate("MainWindow", "Run"))
        self.optionBox.setItemText(0, _translate("MainWindow", "Análisis Léxico"))
        self.optionBox.setItemText(1, _translate("MainWindow", "Análisis Sintáctico"))

    # SEGUNDA INSICION
        
    def newFile(self):
        self.campEdit.clear()

    def openFile(self, path=None):
        if not path:
            path, _ = QtWidgets.QFileDialog.getOpenFileName(self.window, "Open File", '',
                    "All Files (*);;C++ Files (*.cpp *.h*);;Python Files (*.py)")

        if path:
            inFile = QtCore.QFile(path)
            if inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
                text = inFile.readAll()

                try:
                    # Python v3.
                    text = str(text, encoding='ascii')
                except TypeError:
                    # Python v2.
                    text = str(text)

                self.campEdit.setPlainText(text)

    def setupFileMenu(self, MainWindow):
        fileMenu = QtWidgets.QMenu("&Opciones", MainWindow)
        self.menubar.addMenu(fileMenu)

        fileMenu.addAction("&Limpiar...", self.newFile, "Ctrl+N")
        fileMenu.addAction("&Abrir Archivo...", self.openFile, "Ctrl+O")

    def parseResult(self, result, acepted = True):
        curLine = 1
        if acepted: parsed = "Aceptado: \n"
        else: parsed = ''
        for i in result:
            if i.position[0] > curLine:
                parsed += "\n"
                curLine = i.position[0]
            parsed += " {"+str(i.token)+"} "
        return parsed

    # MODULO INICIO

    def runFull(self):
        self.disselecterror(True)
        self.clearError()
        userinput = self.campEdit.toPlainText()
        try:    status, result = self.runLexicAnalyzer(userinput)
        except:
            self.executionErrorStop(LX_EXECUTION_ERROR)
            return
        if status and not self.lexFlag:
            try:    self.runSyntacticAnalyzer(result)
            except:
                self.executionErrorStop(SX_EXECUTION_ERROR)
                return
            


    def changeOption(self, index):
        if index == 0:
            self.lexFlag = True
            #self.setLexiconLabels()
        else:
            self.lexFlag = False
            #self.setSyntacticLabels()


    def runLexicAnalyzer(self, userinput):
        status, result, lastPos = self.lexA.lexiconAnalysis(userinput)
        if(status):
            color = QtGui.QColor(0,163,25)
            cadena = self.parseResult(result)
        else:
            color = QtGui.QColor(255,0,0)
            cadena = result
            if lastPos:
                self.highlightError(lastPos)

        self.resultEdit.setTextColor(color)
        self.resultEdit.setText(cadena)
        return (status, result)
    
    def runSyntacticAnalyzer(self, userinput):
        result, message, lastPos = self.synA.syntacticAnalysis(userinput)
        if result:
            color = QtGui.QColor(0,163,25)
            
        else:
            color = QtGui.QColor(255,0,0)
            # SEÑALAR ERROR
            self.highlightError(lastPos)

        self.resultEdit.setTextColor(color)
        self.resultEdit.setText(message)

    # PRIMERA INSICION
    
    def disselecterror(self, manually = False):
        if self.errorSel is not None:
            cursor = self.campEdit.textCursor()
            if ((cursor.position() >= self.errorSel[0]
                and cursor.position() <= self.errorSel[1]) or manually):
                cursor.movePosition(QtGui.QTextCursor.Start)
                cursor.movePosition(QtGui.QTextCursor.End,QtGui.QTextCursor.KeepAnchor)
                cursor.setCharFormat(self.textFormat)
                self.errorSel = None

    def highlightError(self, pos):
        #posicion de fila y caracter
        format = QtGui.QTextCharFormat()
        format.setBackground(QtGui.QColor(255,0,0))
        cursor = self.campEdit.textCursor()
        
        cursor.movePosition(QtGui.QTextCursor.Start)
        cursor.movePosition(QtGui.QTextCursor.Down,QtGui.QTextCursor.KeepAnchor, pos[0]-1)
    

        cursor.select(QtGui.QTextCursor.BlockUnderCursor)
        self.errorSel = [cursor.selectionStart(),cursor.selectionEnd()]
        cursor.setCharFormat(format)

        cursor = self.numEdit.textCursor()
        numpos = (pos[0]- 1) * 2 if pos[0] > 0 else 0
        cursor.setPosition(numpos)
        cursor.select(QtGui.QTextCursor.BlockUnderCursor)
        cursor.setCharFormat(format)
        self.errorLine = pos[0]

    def clearError(self):
        if(self.errorLine is not None):
            cursor = self.numEdit.textCursor()
            cursor.movePosition(QtGui.QTextCursor.Start)
            cursor.movePosition(QtGui.QTextCursor.End,QtGui.QTextCursor.KeepAnchor)
            cursor.setCharFormat(self.textFormat)
            self.errorLine = None
            
    def executionErrorStop(self, errorCode):
        self.runButton.setEnabled(False)
        self.resultEdit.setText(f'Execution error code: {errorCode}')

    def numeration(self):
        curstring = self.campEdit.toPlainText()
        numstring = self.numEdit.toPlainText()
        linesCamp = len(re.findall('\n',curstring))
        linesNum  = len(re.findall('\n',numstring))

        cursor = self.numEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)

        while(not(linesCamp+1 == linesNum)):
            if linesCamp+1 > linesNum:
                linesNum +=1
                cursor.insertText(str(linesNum)+"\n")
            else:
                linesNum -=1
                cursor.movePosition(QtGui.QTextCursor.WordLeft)
                cursor.select(QtGui.QTextCursor.BlockUnderCursor)
                cursor.removeSelectedText()

if __name__ == "__main__":

    lexiconModule = Lexicon()
    syntacticModule = Syntactic()

    app = QtWidgets.QApplication(sys.argv)

    mainwindow = QtWidgets.QMainWindow()
    editor = EditorWindow()
    editor.setupUi(mainwindow,lexiconModule, True, syntacticModule)
    mainwindow.show()

    sys.exit(app.exec_())