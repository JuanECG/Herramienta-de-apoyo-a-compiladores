""" 
This module contains dialogs and re implementations of classes used in main analyzer.

The file is divided in two regions, subclasses and dialogs. Each contains
definitions for various classes that are used in the analyzer module for 
graphic purposes.

"""
from PyQt5.Qt import QLabel, QListWidget, QMessageBox, pyqtSignal
from PyQt5 import QtCore, QtGui, QtWidgets
import re
from lexic import SubToken, Subset, Token
from const import * 
from Styles import qss
import webbrowser

#region: subclasses
class Label(QLabel):
    """
    Implementation of the PyQt class Qlabel
    
    Its purpose is to enable signals when a label
    is dragged or dropped
    
    """
    itemEntered = pyqtSignal()
    def __init__(self, parent=None, **args):
        super(Label, self).__init__(parent, **args)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event):
        event.accept()
    
    def dropEvent(self, event):
        event.accept()
        self.itemEntered.emit()
        self.setDisabled(True)

class Clickable_Label(QLabel):
    """
    Implementation of the PyQt class Qlabel
    
    Its purpose is to enable signals when a label
    is clicked
    
    """
    clicked=pyqtSignal()
    def __init__(self, parent=None):
        QLabel.__init__(self, parent)

    def mousePressEvent(self, ev):
        self.clicked.emit()

class List(QListWidget):
    """
    Implementation of the PyQt class Qlistwidget
    
    Its purpose is to enable signals when an item 
    enters the list
    """
    # redefines Qlistwidget to create a signal when an item enters the list
    itemMoved = pyqtSignal()
    itemDragged =pyqtSignal()
    dragStarted = pyqtSignal()
    def __init__(self, parent=None, **args):
        super(List, self).__init__(parent, **args)
        #self.setDragDropMode(QAbstractItemView.InternalMove)
        self.acceptFlag = True
        self.setMouseTracking(True)

    def dropEvent(self, event):
        super(List, self).dropEvent(event)
        self.itemMoved.emit()
        for i in range (self.count()):
            self.item(i).setBackground(QtGui.QColor(255, 255, 255))
        
        
    def startDrag(self, event):
        self.dragStarted.emit()
        super(List,self).startDrag(event)
        self.itemDragged.emit()
        
        
    # def keyPressEvent(self, event):
    #     if event.key() == QtCore.Qt.Key_Delete:
    #         row = self.currentRow()
    #         self.takeItem(row)
    #     else:
    #         super().keyPressEvent(event)
#endregion: subclasses
            
#region: dialogs
class EditMainDlg(QtWidgets.QDialog):
    """
    Pyqt standard dialog 
    
    Its purpose is to enable the user to edit the
    main table of the lexic module
    """
    
    def __init__(self,main):
        super(EditMainDlg, self).__init__()
        self.setWindowFlags( QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.main = main
        self.exitOpt = False
        self.oldName = self.main.tableWidget.item(self.main.tableWidget.currentRow(),0).text()
        self.selectedRow = self.main.tableWidget.currentRow()
        self.setFixedSize(274,285)
        self.setWindowTitle("Editar Token")
        self.setStyleSheet(qss)
        iconEdit = QtGui.QIcon()
        iconEdit.addPixmap(QtGui.QPixmap(":/icons/Edit_48px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(iconEdit)
        
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.windowVLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.windowVLayout.setObjectName("windowVLayout")
        
        self.nameEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.nameEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.nameEdit.setObjectName("nameEdit")
        self.nameEdit.setPlaceholderText("Título")
        self.nameEdit.setMaximumHeight(27)
        self.nameEdit.setClearButtonEnabled(True)
        self.windowVLayout.addWidget(self.nameEdit)
        
        self.itemsListWidget = QtWidgets.QListWidget(self.centralwidget)
        self.itemsListWidget.setObjectName("itemsListWidget")
        self.windowVLayout.addWidget(self.itemsListWidget)
        
        self.layoutBtns = QtWidgets.QHBoxLayout()
        self.layoutBtns.setObjectName("layoutBtns")
        self.addBtn = QtWidgets.QPushButton(self.centralwidget)
        iconAdd = QtGui.QIcon()
        iconAdd.addPixmap(QtGui.QPixmap(":/icons/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addBtn.setIcon(iconAdd)
        self.addBtn.setIconSize(QtCore.QSize(30, 30))
        self.addBtn.setObjectName("addBtn")
        self.layoutBtns.addWidget(self.addBtn)
        
        self.delBtn = QtWidgets.QPushButton(self.centralwidget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/Minus_48px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.delBtn.setIcon(icon1)
        self.delBtn.setIconSize(QtCore.QSize(30, 30))
        self.delBtn.setObjectName("delBtn")
        self.delBtn.setDisabled(True)
        self.layoutBtns.addWidget(self.delBtn)
        self.windowVLayout.addLayout(self.layoutBtns)
        
        exp = self.main.tableWidget.item(self.main.tableWidget.currentRow(),0).text()
        self.currentToken = self.main.analyzer.getTokenbyName(exp)
        self.nameEdit.setText(exp)
        
        for item in self.currentToken.getSetExp():
            self.itemsListWidget.addItem(item)    
        #variables
        self.confirmChanges = False
        
        #listeners
        self.addBtn.clicked.connect(lambda:self.add())
        self.delBtn.clicked.connect(lambda:self.delete())
        self.nameEdit.textEdited.connect(lambda:self.changeTitle())
        self.itemsListWidget.itemClicked.connect(lambda:self.delBtn.setDisabled(False))
         
    def add(self):
        add = addItemDlg(self)
        add.exec_()
        
        if self.confirmChanges:
            # add new item to the token
            self.currentToken.getSetExp().append(self.itemsListWidget.item(self.itemsListWidget.count()-1).text())
            # update exp
            self.currentToken.setRegularExp(self.main.analyzer.convertInput(self.currentToken.getSetExp(),1))
            # update lexic main table
            itemText = ''
            for item in self.currentToken.getSetExp():
                itemText += item + ','
            self.main.tableWidget.item(self.main.tableWidget.currentRow(),1).setText(itemText[:-1])
            
            # disable editor
            self.main.btn_search.setEnabled(False)
            
            # disable control table tab 
            self.main.tabWidget.setTabEnabled(1,0)  
            
            self.confirmChanges = False
        
    def delete(self):
        
        item = self.itemsListWidget.item(self.itemsListWidget.currentRow()).text()
        # check if the item that's about to be deleted is not being used
        if self.main.sintactic_module.isTMUsed(self.currentToken.getName()+':'+item):
            self.main.popup("La expresión a eliminar está siendo utilizada en la gramática,\n ¿Está seguro de querer eliminarla?",1)
            if self.main.confirmSignal == False: return
        # delete item from token
        self.currentToken.getSetExp().remove(item)
        # update exp
        self.currentToken.setRegularExp(self.main.analyzer.convertInput(self.currentToken.getSetExp(),1))
        # update lexic main table
        itemText = ''
        for nItem in self.currentToken.getSetExp():
            itemText += nItem + ','
        self.main.tableWidget.item(self.main.tableWidget.currentRow(),1).setText(itemText[:-1])
        # delete from syntactic module
        self.main.sintactic_module.removeTMSymbol(self.currentToken.getName()+':'+item)
        # delete item from the list
        self.itemsListWidget.takeItem(self.itemsListWidget.currentRow())
        self.delBtn.setDisabled(True)
        
        # disable editor
        self.main.btn_search.setEnabled(False)
        
        # disable control table tab 
        self.main.tabWidget.setTabEnabled(1,0)  
        
        if self.itemsListWidget.count() == 0:
            # there's no items left, delete the row
            self.main.deleteItemTable()
            self.exitOpt = True
            self.close()
        
        
    def changeTitle(self):
        title = self.nameEdit.text()
        if self.main.analyzer.findToken(self.nameEdit.text()):
            return
    
        #if self.main.sintactic_module.isTMUsed(title):
        for item in self.currentToken.getSetExp():
            self.main.sintactic_module.setTMSymbol(title+':'+item,self.currentToken.getName()+':'+item)
        self.currentToken.setName(title)
        
        self.main.tableWidget.item(self.main.tableWidget.currentRow(),0).setText(title)
        
        self.oldName = self.nameEdit.text()
      
    def popup(self,msgText):
        msg = QMessageBox()
        msg.setWindowTitle("Advertencia")
        msg.setText(msgText)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowIcon(QtGui.QIcon(':/icons/Variable_48px.png'))
        x = msg.exec_()
        return
    
    def closeEvent(self, evnt):
        
        if self.exitOpt:
            super(EditMainDlg, self).closeEvent(evnt)
            return
        
        if self.nameEdit.text() == '':
            self.popup("Se debe especificar el nombre del token")
            evnt.ignore()
            return
        
        if self.oldName != self.nameEdit.text():
            if self.main.analyzer.findToken(self.nameEdit.text()):
                self.popup("Ya existe un token con el nombre especificado")
                evnt.ignore()
                return
        
        else: super(EditMainDlg, self).closeEvent(evnt)
        
      
        
class addItemDlg(QtWidgets.QDialog):
   
    def __init__(self,parent):
        super(addItemDlg, self).__init__()
        self.setWindowFlags( QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.parent = parent
        self.setFixedSize(193,70)
        self.setWindowTitle("Agregar Elemento")
        self.setStyleSheet(qss)
        iconAdd = QtGui.QIcon()
        iconAdd.addPixmap(QtGui.QPixmap(":/icons/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(iconAdd)
        
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.windowVLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.windowVLayout.setObjectName("windowVLayout")
        
        self.nameEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.nameEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.nameEdit.setObjectName("nameEdit")
        self.nameEdit.setMaximumHeight(27)
        self.nameEdit.setPlaceholderText("Expresión")
        self.nameEdit.setClearButtonEnabled(True)
        self.windowVLayout.addWidget(self.nameEdit)
        
        self.layoutBtns = QtWidgets.QHBoxLayout()
        self.layoutBtns.setObjectName("layoutBtns")
        self.addBtn = QtWidgets.QPushButton(self.centralwidget)
        self.addBtn.setText("Agregar Elemento")
        self.addBtn.setObjectName("addBtn")
        self.layoutBtns.addWidget(self.addBtn)
        
        self.cancelBtn = QtWidgets.QPushButton(self.centralwidget)
        self.cancelBtn.setText("Cancelar")
        self.cancelBtn.setObjectName("cancelBtn")
        self.layoutBtns.addWidget(self.cancelBtn)
        self.windowVLayout.addLayout(self.layoutBtns)
        
        self.addBtn.clicked.connect(lambda:self.add())
        self.cancelBtn.clicked.connect(lambda:self.close())
        
    def add(self):
        if self.nameEdit.text() == '':
            self.popup("El elemento debe tener una expresión")
            return
        
        for i in range (self.parent.itemsListWidget.count()):
            if self.parent.itemsListWidget.item(i).text() == self.nameEdit.text():    
                self.popup("Ya existe un elemento con esa expresión")
                return
        # add item to the list
        self.parent.itemsListWidget.addItem(self.nameEdit.text())
        self.parent.confirmChanges = True
        self.close()
    
    def popup(self,msgText):
        msg = QMessageBox()
        msg.setWindowTitle("Advertencia")
        msg.setText(msgText)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowIcon(QtGui.QIcon(':/icons/Variable_48px.png'))
        x = msg.exec_()
        return      

class EditMainDlgExp(QtWidgets.QDialog):
    """
    Pyqt standard dialog 
    
    Its purpose is to enable the user to edit the
    main table of the lexic module when a token
    with a regular expression is selected
    """
    
    def __init__(self,main):
        super(EditMainDlgExp, self).__init__()
        self.setWindowFlags( QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.main = main
        self.selectedRow = self.main.tableWidget.currentRow()
        self.resize(440,250)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/Edit_48px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.setStyleSheet(qss)
        self.setWindowTitle("Editar elemento")

        self.verticalLayoutWidget = QtWidgets.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(140, 10, 241, 151))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(18)
        self.verticalLayout.setObjectName("verticalLayout")
        self.name = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.name.setClearButtonEnabled(True)
        self.name.setObjectName("name")
        self.name.setText(main.tableWidget.item(self.selectedRow,0).text())
        self.idname = main.tableWidget.item(self.selectedRow,0).text()
        self.editToken = self.main.analyzer.getTokenbyName(self.idname)
        self.verticalLayout.addWidget(self.name)
        self.exp = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.exp.setObjectName("exp")
        self.exp.setClearButtonEnabled(True)
        self.exp.setText(main.tableWidget.item(self.selectedRow,1).text())
        self.idexp = main.tableWidget.item(self.selectedRow,1).text()
        self.verticalLayout.addWidget(self.exp)

        self.horizontalLayoutWidget = QtWidgets.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(160, 160, 191, 101))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.saveButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout.addWidget(self.saveButton)
        self.cancelButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.nameLabel = QtWidgets.QLabel(self)
        self.nameLabel.setGeometry(QtCore.QRect(30, 45, 51, 13))
        self.nameLabel.setObjectName("nameLabel")
        self.expLabel = QtWidgets.QLabel(self)
        self.expLabel.setGeometry(QtCore.QRect(30,116,100,13))
        self.expLabel.setObjectName("expLabel")
        self.setWindowTitle("Editar elemento")
        self.saveButton.setText("Guardar Cambios")
        self.cancelButton.setText("Cancelar")
        self.nameLabel.setText("Nombre:")
        self.expLabel.setText("Expresión:")
        self.setMinimumWidth(350)

        #listeners:
        self.saveButton.clicked.connect(lambda:self.saveChanges())
        self.cancelButton.clicked.connect(lambda:self.close())

    def saveChanges(self):
        #if no expression or description given, notify error
        
        newName = self.name.text()
        oldName = self.main.tableWidget.item(self.main.tableWidget.currentRow(),0).text()
        
        if newName == "" or self.exp.text()=="":
            self.popup("El nombre y la expresión deben ser especificados")
            return
        
        # if user changes name, check if it already exists
        if self.idname != newName:
            if self.main.analyzer.findToken(newName):
                self.popup("Ya existe un token con el nombre especificado")
                return
        
        #we should alert when a user can't enter a token with an expression that's already used
        #if so, then we can use a similar process to the name validation, using idexp. 
        
        #validate new expression
        if not self.main.analyzer.validateRegExpression(self.main.analyzer.convertInput(self.exp.text())):
            self.popup("La expresión especificada es inválida")
            return
        
        if newName != oldName:
            self.main.sintactic_module.setTMSymbol(newName,oldName)
            self.main.tableWidget.item(self.main.tableWidget.currentRow(),0).setText(newName)
            
        # update expression
        self.main.analyzer.setToken(Token(newName,0,self.exp.text()),self.selectedRow)
            
            
        nameItem=QtWidgets.QTableWidgetItem(newName)
        nameItem.setFlags(  QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        expItem=QtWidgets.QTableWidgetItem(self.exp.text())
        expItem.setFlags(  QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.main.tableWidget.setItem(self.selectedRow,0,nameItem)
        self.main.tableWidget.setItem(self.selectedRow,1,expItem)
        self.close()
        
        # disable editor
        self.main.btn_search.setEnabled(False)
        
        # disable control table tab 
        self.main.tabWidget.setTabEnabled(1,0)  

    def popup(self,msgText):
        msg = QMessageBox()
        msg.setWindowTitle("Advertencia")
        msg.setText(msgText)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowIcon(QtGui.QIcon(':/icons/Variable_48px.png'))
        x = msg.exec_()
        return
#---------------------------------------------------------------------------------------------
class AddSubconjuntoDlg(QtWidgets.QDialog):
    """
    Pyqt standard dialog 
    
    Its purpose is to enable the user to add an item
    in the 'subconjunto' table of the lexic module
    """
    
    def __init__(self, main):
        super(AddSubconjuntoDlg, self).__init__()
        self.setWindowFlags( QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.main = main
        self.setWindowTitle("Añadir elemento Subconjunto")
        self.row = self.main.tableSubconjunto.rowCount()
        self.setFixedSize(440,300)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.setStyleSheet(qss)

        self.verticalLayoutWidget = QtWidgets.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(140, 40, 241, 151))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(18)
        self.verticalLayout.setObjectName("verticalLayout")
        self.expEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.expEdit.setObjectName("expEdit")
        self.expEdit.setClearButtonEnabled(True)
        self.verticalLayout.addWidget(self.expEdit)
        self.expPythonEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.expPythonEdit.setObjectName("expPythonEdit")
        self.expPythonEdit.setClearButtonEnabled(True)
        self.verticalLayout.addWidget(self.expPythonEdit)
        self.descEdit = QtWidgets.QTextEdit(self.verticalLayoutWidget)
        self.descEdit.setObjectName("descEdit")
        self.verticalLayout.addWidget(self.descEdit)

        self.horizontalLayoutWidget = QtWidgets.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(170, 190, 200, 101))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.saveButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.saveButton.setObjectName("saveButton")
        #self.saveButton.setMinimumWidth(1)
        self.horizontalLayout.addWidget(self.saveButton)
        self.cancelButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.expLabel = QtWidgets.QLabel(self)
        self.expLabel.setGeometry(QtCore.QRect(30, 65, 51, 13))
        self.expLabel.setObjectName("expLabel")
        self.expPythonLabel = QtWidgets.QLabel(self)
        self.expPythonLabel.setGeometry(QtCore.QRect(30,120,105,13))
        self.expPythonLabel.setObjectName("expPythonLabel")
        self.descLabel = QtWidgets.QLabel(self)
        self.descLabel.setGeometry(QtCore.QRect(30, 175, 100, 13))
        self.descLabel.setObjectName("descLabel")
        self.setWindowTitle("Añadir elemento subconjunto")
        self.saveButton.setText("Guardar Expresión")
        self.cancelButton.setText("Cancelar")
        self.expLabel.setText("Id:")
        self.expPythonLabel.setText("Expresión Python:")
        self.descLabel.setText("Descripción:")
        self.control=True

        #listeners:
        self.saveButton.clicked.connect(lambda:self.saveChanges())
        self.cancelButton.clicked.connect(lambda:self.close())
        self.expPythonEdit.textEdited.connect(lambda:self.warning())
        
    def warning(self):
        if self.control:
            self.popup("ADVERTENCIA, las expresiones ingresadas como subconjuntos se tomarán literalmente en la construcción de tokens")
            self.control = False

    def saveChanges(self):
        #if no expression or description given, notify error
        if self.expEdit.text() == "" or self.descEdit.toPlainText() == "" or self.expPythonEdit.text()=="":
            self.popup("El id, la expresión y su descripción deben ser especificados")
            return
        
        nameItem=QtWidgets.QTableWidgetItem(self.expEdit.text())
        nameItem.setFlags(  QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        
        if self.main.analyzer.findSubset(self.expEdit.text()):
            self.popup("El identificiador especificado ya pertenece a otro subconjunto")
            return
        
        self.main.analyzer.addSubset(Subset(self.expEdit.text(),self.expPythonEdit.text(),self.descEdit.toPlainText()))
        
        expItem=QtWidgets.QTableWidgetItem(self.descEdit.toPlainText())
        expItem.setFlags(  QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.main.tableSubconjunto.insertRow(self.row)
        self.main.tableSubconjunto.setItem(self.row,0,nameItem)
        self.main.tableSubconjunto.setItem(self.row,1,expItem)
        self.close()

    def popup(self,msgText):
        msg = QMessageBox()
        msg.setWindowTitle("Advertencia")
        msg.setText(msgText)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowIcon(QtGui.QIcon(':/icons/Variable_48px.png'))
        x = msg.exec_()
        return
#---------------------------------------------------------------------------------------------
class EditSubconjuntoDlg(QtWidgets.QDialog):
    """
    Pyqt standard dialog 
    
    Its purpose is to enable the user to edit an item
    in the 'subconjunto' table of the lexic module
    """
    
    def __init__(self,main):
        super(EditSubconjuntoDlg, self).__init__()
        self.setWindowFlags( QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.main = main
        self.selectedRow = self.main.tableSubconjunto.currentRow()
        self.setWindowTitle("Editar elemento Subconjunto")
        self.setFixedSize(440,300)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/Edit_48px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.setStyleSheet(qss)

        self.verticalLayoutWidget = QtWidgets.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(140, 40, 241, 151))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(18)
        self.verticalLayout.setObjectName("verticalLayout")
        self.idName = main.tableSubconjunto.item(self.selectedRow,0).text()
        self.expEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.expEdit.setObjectName("expEdit")
        self.expEdit.setClearButtonEnabled(True)
        self.expEdit.setText(main.tableSubconjunto.item(self.selectedRow,0).text())
        self.verticalLayout.addWidget(self.expEdit)
        self.expPythonEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.expPythonEdit.setObjectName("expPythonEdit")
        self.expPythonEdit.setClearButtonEnabled(True)
        self.expPythonEdit.setText(self.main.analyzer.getSubsetbyId(self.idName).getExpression())
        self.verticalLayout.addWidget(self.expPythonEdit)
        self.descEdit = QtWidgets.QTextEdit(self.verticalLayoutWidget)
        self.descEdit.setObjectName("descEdit")
        self.descEdit.setText(main.tableSubconjunto.item(self.selectedRow,1).text())
        self.verticalLayout.addWidget(self.descEdit)

        self.horizontalLayoutWidget = QtWidgets.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(170, 190, 191, 101))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.saveButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout.addWidget(self.saveButton)
        self.cancelButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.expLabel = QtWidgets.QLabel(self)
        self.expLabel.setGeometry(QtCore.QRect(30, 65, 51, 13))
        self.expLabel.setObjectName("expLabel")
        self.expPythonLabel = QtWidgets.QLabel(self)
        self.expPythonLabel.setGeometry(QtCore.QRect(30,120,105,13))
        self.expPythonLabel.setObjectName("expPythonLabel")
        self.descLabel = QtWidgets.QLabel(self)
        self.descLabel.setGeometry(QtCore.QRect(30, 175, 100, 13))
        self.descLabel.setObjectName("descLabel")
        self.setWindowTitle("Editar elemento Subconjunto")
        self.saveButton.setText("Guardar Cambios")
        self.cancelButton.setText("Cancelar")
        self.expLabel.setText("Id:")
        self.expPythonLabel.setText("Expresión Python:")
        self.descLabel.setText("Descripción:")
        self.control=True

        #listeners:
        self.saveButton.clicked.connect(lambda:self.saveChanges())
        self.cancelButton.clicked.connect(lambda:self.close())
        self.expPythonEdit.textEdited.connect(lambda:self.warning())

    def saveChanges(self):
        #if no expression, if or description given, notify error
        if self.expEdit.text() == "" or self.descEdit.toPlainText() == "" or self.expPythonEdit.text()=="":
            self.popup("El id, la expresión y su descripción deben ser especificados")
            return
        
        
        if self.idName != self.expEdit.text():
            if self.main.analyzer.findSubset(self.expEdit.text()):
                self.popup("El identificiador especificado ya pertenece a otro subconjunto")
                return
        
        self.main.analyzer.setSubset(Subset(self.expEdit.text(),self.expPythonEdit.text(),self.descEdit.toPlainText()),self.selectedRow)
        
        nameItem=QtWidgets.QTableWidgetItem(self.expEdit.text())
        nameItem.setFlags(  QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        expItem=QtWidgets.QTableWidgetItem(self.descEdit.toPlainText())
        expItem.setFlags(  QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.main.tableSubconjunto.setItem(self.selectedRow,0,nameItem)
        self.main.tableSubconjunto.setItem(self.selectedRow,1,expItem)
        self.main.reloadMainTable()
        self.close()

    def warning(self):
        if self.control:
            self.popup("ADVERTENCIA, las expresiones ingresadas como subconjuntos se tomarán literalmente en la construcción de tokens")
            self.control = False
    
    def popup(self,msgText):
        msg = QMessageBox()
        msg.setWindowTitle("Advertencia")
        msg.setText(msgText)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowIcon(QtGui.QIcon(':/icons/Variable_48px.png'))
        x = msg.exec_()
        return
#---------------------------------------------------------------------------------------------
class EditorWindow(object):
    """
    Pyqt standard object 
    
    Its purpose is to create a window to allow the user
    to test the tokens that were created or loaded
    """
    
    def setupUi(self, MainWindow, main, allowSyntax = False):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(700, 570)
        icon = QtGui.QIcon()
        #MainWindow.setStyleSheet(qss)
        icon.addPixmap(QtGui.QPixmap(":/icons/Variable_48px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setWindowFlags( QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)

        # PERSONALIZACIÓN
        self.window = MainWindow
        self.main = main

        self.textFormat = QtGui.QTextCharFormat()
        self.textFormat.setFontFamily("Arial")
        self.textFormat.setFontPointSize(12)

        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)

        fontlittle = QtGui.QFont()
        fontlittle.setFamily("Arial")
        fontlittle.setPointSize(11)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.runButton = QtWidgets.QPushButton(self.centralwidget)
        self.runButton.setGeometry(QtCore.QRect(10, 340, 50, 20))
        self.runButton.setObjectName("runButton")
        iconPlay = QtGui.QIcon()
        iconPlay.addPixmap(QtGui.QPixmap(":/icons/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.runButton.setIcon(iconPlay)

        self.runStepButton = QtWidgets.QPushButton(self.centralwidget)
        self.runStepButton.setGeometry(QtCore.QRect(90, 340, 50, 20))
        self.runStepButton.setObjectName("runStepButton")
        iconFFordward = QtGui.QIcon()
        iconFFordward.addPixmap(QtGui.QPixmap(":/icons/fast-forward.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.runStepButton.setIcon(iconFFordward)

        self.stopStepButton = QtWidgets.QPushButton(self.centralwidget)
        self.stopStepButton.setGeometry(QtCore.QRect(150, 340, 50, 20))
        self.stopStepButton.setObjectName("stopStepButton")
        iconStop = QtGui.QIcon()
        iconStop.addPixmap(QtGui.QPixmap(":/icons/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.stopStepButton.setIcon(iconStop)

        self.nextStepButton = QtWidgets.QPushButton(self.centralwidget)
        self.nextStepButton.setGeometry(QtCore.QRect(210, 340, 50, 20))
        self.nextStepButton.setObjectName("nextStepButton")
        iconEnd = QtGui.QIcon()
        iconEnd.addPixmap(QtGui.QPixmap(":/icons/end.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.nextStepButton.setIcon(iconEnd)

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
        self.campEdit.setAcceptRichText(False)
        self.campEdit.setObjectName("campEdit")

        
        self.optionsTab = QtWidgets.QTabWidget(self.centralwidget)
        self.optionsTab.setGeometry(QtCore.QRect(10, 370, 681, 161))
        self.optionsTab.setObjectName("optionsTab")

        self.stepTab = QtWidgets.QWidget()
        self.stepTab.setObjectName("stepTab")

        self.stackLabel = QtWidgets.QLabel(self.stepTab)
        self.stackLabel.setGeometry(QtCore.QRect(360, 10, 281, 16))
        self.stackLabel.setObjectName("stackLabel")
        self.stackLabel.setFont(font)
        self.headerLabel = QtWidgets.QLabel(self.stepTab)
        self.headerLabel.setGeometry(QtCore.QRect(20, 10, 261, 16))
        self.headerLabel.setObjectName("headerLabel")
        self.headerLabel.setFont(font)
        self.aplicationLabel = QtWidgets.QLabel(self.stepTab)
        self.aplicationLabel.setGeometry(QtCore.QRect(20, 70, 271, 16))
        self.aplicationLabel.setObjectName("aplicationLabel")
        self.aplicationLabel.setFont(font)

        self.stackList = QtWidgets.QListWidget(self.stepTab)
        self.stackList.setGeometry(QtCore.QRect(360, 30, 291, 91))
        self.stackList.setObjectName("stackList")
        self.stackList.setFont(fontlittle)

        self.headerLine = QtWidgets.QLineEdit(self.stepTab)
        self.headerLine.setGeometry(QtCore.QRect(20, 30, 301, 20))
        self.headerLine.setObjectName("headerLine")
        self.headerLine.setReadOnly(True)
        self.headerLine.setFont(fontlittle)
        self.aplicationLine = QtWidgets.QLineEdit(self.stepTab)
        self.aplicationLine.setGeometry(QtCore.QRect(20, 90, 301, 20))
        self.aplicationLine.setObjectName("aplicationLine")
        self.aplicationLine.setReadOnly(True)
        self.aplicationLine.setFont(fontlittle)

        self.optionsTab.addTab(self.stepTab, "")
        self.resultTab = QtWidgets.QWidget()

        self.resultTab.setObjectName("resultTab")
        self.resultEdit = QtWidgets.QTextEdit(self.resultTab)
        self.resultEdit.setGeometry(QtCore.QRect(-1, -1, 677, 137))
        self.resultEdit.setObjectName("resultEdit")
        self.resultEdit.setReadOnly(True)
        self.resultEdit.setFont(font)
        self.resultEdit.setFocusPolicy(QtCore.Qt.NoFocus)
        self.optionsTab.addTab(self.resultTab, "")

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
        self.running = False

        # OBTENCIÓN DE MÓDULOS
        
        if allowSyntax:
            self.lexA = self.main.analyzer 
            self.synA = self.main.sintactic_module
        else:
            self.lexA = self.main.analyzer 
        # COMBOBOX
        if allowSyntax:
            self.optionBox.currentIndexChanged.connect(self.changeOption)
        else:
            self.optionBox.setEnabled(False)
        # BUTTONS CONF
        self.runButton.clicked.connect(self.runFull)
        self.runStepButton.clicked.connect(self.runStepbyStep)
        self.nextStepButton.clicked.connect(self.stepForward)
        self.nextStepButton.setEnabled(False)
        self.stopStepButton.clicked.connect(self.stopRunning)
        self.stopStepButton.setEnabled(False)
        
        self.campEdit.cursorPositionChanged.connect(self.disselecterror)
        self.campEdit.textChanged.connect(self.numeration)
        #
        self.campEdit.verticalScrollBar().valueChanged.connect(
            self.numEdit.verticalScrollBar().setValue
        )
        self.numEdit.verticalScrollBar().valueChanged.connect(
            self.campEdit.verticalScrollBar().setValue)


        self.retranslateUi(MainWindow)
        self.optionsTab.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Editor"))
        self.runButton.setText(_translate("MainWindow", ""))
        
        self.setLexiconLabels()
        self.optionsTab.setTabText(self.optionsTab.indexOf(self.stepTab), _translate("MainWindow", "Paso a paso"))
        self.optionsTab.setTabText(self.optionsTab.indexOf(self.resultTab), _translate("MainWindow", "Resultado"))
        self.optionBox.setItemText(0, _translate("MainWindow", "Análisis Léxico"))
        self.optionBox.setItemText(1, _translate("MainWindow", "Análisis Sintáctico"))

    def setLexiconLabels(self):
        _translate = QtCore.QCoreApplication.translate
        self.stackLabel.setText(_translate("MainWindow", "Cadena Resultado"))
        self.headerLabel.setText(_translate("MainWindow", "Elemento en Cabecera"))
        self.aplicationLabel.setText(_translate("MainWindow", "Token Reconocido"))

    def setSyntacticLabels(self):
        _translate = QtCore.QCoreApplication.translate
        self.stackLabel.setText(_translate("MainWindow", "Pila"))
        self.headerLabel.setText(_translate("MainWindow", "Elemento en Cabecera"))
        self.aplicationLabel.setText(_translate("MainWindow", "Producción en Aplicación"))
        
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

    def toggleWindow(self):
        if self.toggled:
            self.resultEdit.setGeometry(QtCore.QRect(10, 350, 680, 200))
            self.toggled = False
            self.window.resize(700, 600)
        else:
            self.resultEdit.setGeometry(QtCore.QRect(10, 350, 680, 0))
            self.toggled = True
            self.window.resize(700, 380)

    def parseResult(self, result, acepted = True):
        curLine = 1
        if acepted: parsed = "Aceptado: \n"
        else: parsed = ''
        for i in result:
            if i.getPosition()[0] > curLine:
                parsed += "\n"
                curLine = i.getPosition()[0]
            parsed += " { "+str(i.getToken())+" } "
        return parsed

    def runFull(self):        
        self.optionsTab.setCurrentWidget(self.optionsTab.widget(1))
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
            self.setLexiconLabels()
        else:
            self.lexFlag = False
            self.setSyntacticLabels()
        if self.running:
            self.stopRunning()
            self.stackList.clear()
            self.headerLine.setText('')
            self.aplicationLine.setText('')

    def runLexicAnalyzer(self, userinput):
        result = self.lexA.runLexic(userinput)
        if(result[0]):
            color = QtGui.QColor(0,163,25)
            cadena = self.parseResult(result[1])
        else:
            color = QtGui.QColor(255,0,0)
            cadena = result[1]
            if len(result)>2:
                self.highlightError(result[2])


        self.resultEdit.setTextColor(color)
        self.resultEdit.setText(cadena)
        return (result[0], result[1])
    
    def runSyntacticAnalyzer(self, userinput):
        result, message, lastPos = self.synA.runSyntax(userinput)
        if result:
            color = QtGui.QColor(0,163,25)

        else:
            color = QtGui.QColor(255,0,0)
            # SEÑALAR ERROR
            self.highlightError(lastPos, True)

        self.resultEdit.setTextColor(color)
        self.resultEdit.setText(message)

    def runStepbyStep(self):
        #CHANGES HERE.
        self.optionsTab.setCurrentWidget(self.optionsTab.widget(0))
        self.disselecterror(True)
        self.clearError()
        self.stackList.clear()
        self.selectedElement = None
       
        self.running = True
        userinput = self.campEdit.toPlainText()
        if len(userinput) > 0:
            if self.lexFlag:
                self.mainChar = userinput
                self.editPos = [0,0]
                self.curPos = [1,1]
                self.resultLex = []
                self.cleanedChars = []
                self.lexStep()
            else:
                status, self.resultLex = self.runLexicAnalyzer(userinput)
                if status:
                    eocs = SubToken(EOC, EOC, (0,0))
                    self.resultLex.append(eocs)
                    self.editPos = [0,0]
                    self.stack = []
                    self.stack.append(self.synA.getInitialNt())
                    self.oldHead = -1
                    self.head = 0
                # ---- INICIAL
                
                self.synStep()

            if self.running:
                self.selectElement(self.editPos)
                self.nextStepButton.setEnabled(True)
                self.stopStepButton.setEnabled(True)
        else:
            self.optionsTab.setCurrentWidget(self.optionsTab.widget(1))
            self.resultEdit.setText('Para esta función ingrece una cadena no vácia')

    def lexStep(self):

        self.editPos[0] = self.editPos[1]

        while(True):
            if(self.mainChar[0] == ' ' or self.mainChar[0] == '\n'):
                #cleanedChar += self.mainChar[0]
                if(self.mainChar[0] == '\n'):
                    self.curPos[0] += 1
                    self.curPos[1] = 1
                self.mainChar = self.mainChar[1:]
                self.editPos[0] += 1 
            else: 
                break
        #self.cleanedChars.append(cleanedChar)

        oldChar = self.mainChar + ""
        status ,self.mainChar, self.curPos, self.resultLex, activeTokens = self.lexA.cutStep(self.mainChar,self.resultLex, self.curPos)
        

        if status == -1:
            resultChar = "Existe un conflicto entre los token: "
            for token in activeTokens: resultChar += '\n' + token.getName()
            color = QtGui.QColor(255,0,0)
            self.stopRunning()
            originalChar = self.campEdit.toPlainText()
            errorPos = (self.curPos[0], originalChar-self.mainChar)
            self.highlightError(errorPos)
            
        elif status == 0:
            resultChar = f"Error léxico en fila {self.curPos[0]} elemento {self.curPos[1]}:\n"    
            resultChar += f"El elemento '{self.mainChar[0]}' no coincide con los tokens definidos"
            color = QtGui.QColor(255,0,0)
            self.stopRunning()
            originalChar = self.campEdit.toPlainText()
            errorPos = (self.curPos[0], len(originalChar)-len(self.mainChar))
            self.highlightError(errorPos)
        
        else:
            # ANÁLISIS CORRECTO
            dif = len(oldChar) - len(self.mainChar)
            self.editPos[1] =  self.editPos[0] + dif

            # RELLENAR LINEAS(lineEdit)
            for token in activeTokens:
                if token.getTypeExp() == 1 or len(activeTokens) == 1:
                    self.aplicationLine.setText(token.getName())
                    break
            color = QtGui.QColor(0,163,25)

            self.headerLine.setText(oldChar[0:dif])
            self.stackList.addItem(f'{self.resultLex[-1].getToken()}:{self.resultLex[-1].getValue()}')
            resultChar = self.parseResult(self.resultLex, False) if len(self.mainChar) > 0 else self.parseResult(self.resultLex)

        self.resultEdit.setTextColor(color)
        self.resultEdit.setText(resultChar)

    def synStep(self):

        if self.resultLex[self.head].getValue() == EOC:
                self.headerLine.setText('Fin de cadena')
                self.editPos = None
        elif self.oldHead != self.head:

            self.headerLine.setText(self.resultLex[self.head].getToken())
            self.oldHead = self.head
            originalChar = self.campEdit.toPlainText()
            #LIMPIEZA
            while(True):
                if(originalChar[self.editPos[1]] == ' ' or originalChar[self.editPos[0]] == '\n'):
                    self.editPos[1] += 1
                else: 
                    break
            # ACTUALIZACION DE SELECT
            self.editPos[0] = self.editPos[1]
            self.editPos[1] = self.editPos[0] + len(self.resultLex[self.head].getValue())

        # ACTUALIZAR STACK
        self.stackList.clear()
        for symbol in reversed(self.stack):
            self.stackList.addItem(f'{symbol.getTag()}')
        self.stackList.verticalScrollBar().setValue(0)

        # PRODUCCIÓN
        prostr = ''
        if len(self.stack) > 0:
        
            if self.stack[-1].getStype() == TM:
                if self.resultLex[self.head].getToken() == self.stack[-1].getTag():
                    self.stack.pop()
                    self.head +=1
                    prostr = 'PA'
                else:
                    message = self.synA.getDefinedError(self.stack[-1],self.resultLex[self.head], True)
                    self.resultEdit.setTextColor(QtGui.QColor(255,0,0))
                    self.resultEdit.setText(message)
                    self.stopRunning()
            else:
                production = self.synA.findProduction(self.stack[-1].getTag(), self.resultLex[self.head].getToken())
                if production is not None:
                    # CAMBIO INICIO
                    prostr = '' + self.stack[-1].getTag()+'→ ' 
                    for symbol in production:
                        prostr += symbol.getTag() + ' '
                    # CAMBIO FIN
                    self.head = self.synA.applyProduction(production, self.stack, self.head)
                    

                else:
                    message = self.synA.getDefinedError(self.stack[-1],self.resultLex[self.head], True)
                    self.resultEdit.setTextColor(QtGui.QColor(255,0,0))
                    self.resultEdit.setText(message)
                    self.stopRunning()
        else:
            if self.resultLex[self.head].getValue() == EOC:
                self.resultEdit.setTextColor(QtGui.QColor(0,163,25))
                self.resultEdit.setText('Secuencia aceptada')
            else:
                message = 'Error sintáctico se encontro '
                message += self.resultLex[self.head].getToken() +' y se esperaba fin de cadena'    
                
                self.resultEdit.setTextColor(QtGui.QColor(255,0,0))
                self.resultEdit.setText(message)
                
            self.stopRunning()
            
        self.aplicationLine.setText(prostr)
        
    def stopRunning(self):
        self.editPos = None
        self.diselectElement()
        self.running = False
        self.nextStepButton.setEnabled(False)
        self.stopStepButton.setEnabled(False)
        self.optionsTab.setCurrentWidget(self.optionsTab.widget(1))
        
    def stepForward(self):
        # VERIFICAR FIN DE LINEA Y SALTO
        self.diselectElement()
        #self.curpos =  (self.curpos[0],self.curpos[1]+1)
        #self.selectElement((self.curpos))
        if self.lexFlag:
            self.lexStep()
            if len(self.mainChar) == 0:
                self.stopRunning()
    
            else:
                self.selectElement(self.editPos)
        else:
            self.synStep()
            """ if len(self.stack) == 0:
                self.stopRunning()
            else:
                self.selectElement(self.editPos) """    
            self.selectElement(self.editPos)

    def stepBackward(self):
        # Guardar cadena original para proceso inverso
        pass
    
    def selectElement(self, pos = None):
        # MANEJAR VARIABLE SELECTED ELEMENT
        if pos:
            format = QtGui.QTextCharFormat()
            format.setBackground(QtGui.QColor(53,196,254))
            cursor = self.campEdit.textCursor()
            cursor.movePosition(QtGui.QTextCursor.Start)

            #cursor.select(QtGui.QTextCursor.BlockUnderCursor)

            # SELECCIONAR ELEMENTO EN POSICION
            cursor.setPosition(pos[0])
            cursor.setPosition(pos[1], QtGui.QTextCursor.KeepAnchor)
            #cursor.select(QtGui.QTextCursor.WordUnderCursor)

            # MODIFICAR VARIABLE SELECTEDELEMENT
            self.selectedElement = [cursor.selectionStart(),cursor.selectionEnd()]

            # CAMBIAR COLOR
            cursor.setCharFormat(format)

    def diselectElement(self):
        if self.selectedElement:
            cursor = self.campEdit.textCursor()
            cursor.setPosition(self.selectedElement[0])
            cursor.select(QtGui.QTextCursor.BlockUnderCursor)
            cursor.setCharFormat(self.textFormat)
            self.selectedElement = None
            
    def disselecterror(self, manually = False):
        if self.errorSel is not None:
            cursor = self.campEdit.textCursor()
            if ((cursor.position() >= self.errorSel[0]
                and cursor.position() <= self.errorSel[1]) or manually):
                cursor.movePosition(QtGui.QTextCursor.Start)
                cursor.movePosition(QtGui.QTextCursor.End,QtGui.QTextCursor.KeepAnchor)
                cursor.setCharFormat(self.textFormat)
                self.errorSel = None

    def highlightError(self, pos, justLine = False):
        #posicion de fila y caracter
        format = QtGui.QTextCharFormat()
        format.setBackground(QtGui.QColor(255,0,0))
        cursor = self.campEdit.textCursor()
        if justLine:
            cursor.movePosition(QtGui.QTextCursor.Start)
            cursor.movePosition(QtGui.QTextCursor.Down,QtGui.QTextCursor.KeepAnchor, pos[0]-1)
        else:
            cursor.setPosition(pos[1])

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
        self.runStepButton.setEnabled(False)
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
#---------------------------------------------------------------------------------------------
class AddNonTerminalDialog(QtWidgets.QDialog):
    """
    Pyqt standard dialog 
    
    Its purpose is to enable the user to add a non-terminal to the Non-terminal list 
    """
    
    def __init__(self, main):
        super(AddNonTerminalDialog, self).__init__()
        self.setWindowFlags( QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.setObjectName("AddNonTerminalDialog")
        self.main = main
        self.setFixedSize(401,163)
        self.setWindowTitle("Añadir No-Terminal")
        self.setStyleSheet(qss)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        
        self.layoutForm = QtWidgets.QHBoxLayout()
        self.layoutForm.setSpacing(6)
        self.layoutForm.setObjectName("layoutForm")
        
        self.nameLabel = QtWidgets.QLabel(self)
        self.nameLabel.setObjectName("nameLabel")
        self.layoutForm.addWidget(self.nameLabel)
        self.nameLabel.setText("Nombre:")
        
        self.expEdit = QtWidgets.QLineEdit(self)
        self.expEdit.setMaximumSize(QtCore.QSize(16777215, 30))
        self.expEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.expEdit.setClearButtonEnabled(True)
        self.expEdit.setObjectName("expEdit")
        self.expEdit.setText("<>")
        self.expEdit.setCursorPosition(1)
        self.layoutForm.addWidget(self.expEdit)
        
        self.verticalLayout.addLayout(self.layoutForm)
        
        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        
        self.buttonsLayout = QtWidgets.QHBoxLayout()
        self.buttonsLayout.setObjectName("buttonsLayout")
        
        self.createBtn = QtWidgets.QPushButton(self)
        self.createBtn.setMaximumSize(QtCore.QSize(16777215, 30))
        self.createBtn.setObjectName("createBtn")
        self.createBtn.setText("Crear")
        self.buttonsLayout.addWidget(self.createBtn)
        
        self.cancelBtn = QtWidgets.QPushButton(self)
        self.cancelBtn.setMaximumSize(QtCore.QSize(16777215, 30))
        self.cancelBtn.setObjectName("cancelBtn")
        self.cancelBtn.setText("Cancelar")
        self.buttonsLayout.addWidget(self.cancelBtn)
        
        self.verticalLayout.addLayout(self.buttonsLayout)
           
        
        #listeners
        self.expEdit.textEdited.connect(lambda:self.setDefault())
        self.expEdit.cursorPositionChanged.connect(lambda:self.cursorChanged())
        self.cancelBtn.clicked.connect(lambda:self.close())
        self.createBtn.clicked.connect(lambda:self.create())
        
        QtCore.QMetaObject.connectSlotsByName(self)

    def create(self):
        # adds item to the NT_items list
        
        if self.expEdit.text() == "<>":
            self.popup("El campo no puede estar vacío")
            return
        
        if len(self.expEdit.text()) > 17:
            self.popup("El nombre del no terminal no debería exceder los 15 caracteres")
            return

        for i in range (self.main.NT_items.count()):
            if self.main.NT_items.item(i).text() == self.expEdit.text():
                self.popup("Ya existe un no-terminal con ese nombre")
                return
        self.main.NT_items.addItem(self.expEdit.text())
        
        # add NT to sintactic_module
        self.main.sintactic_module.addNoTerminalSymbol(self.expEdit.text())
        
        # disable editor
        self.main.btn_search.setEnabled(False)
        
        # disable control table tab 
        self.main.tabWidget.setTabEnabled(1,0)  
        
        # close window
        self.close()

    def setDefault(self):
        # prevents the user form deleting the obligatory '<' and '>' characters
        text = self.expEdit.text()
        
        if self.expEdit.text() == "":
            self.expEdit.setText("<>")
            self.expEdit.setCursorPosition(1)
            return
        
        if text[0:1] != '<':
            self.expEdit.setText('<'+text)
            
        if text[len(text)-1] != '>':
            self.expEdit.setText(text+'>')
            
        reg = re.search("<|>", text[1:-1])
        
        if reg:
            self.popup("Los caracteres '<' & '>' no están permitidos para este campo")
            text =text.replace('<','')
            text =text.replace('>','')
            self.expEdit.setText('<'+text+'>')
    
    def cursorChanged(self):
        # prevents the user from positioning the cursos on the first and last pos
        if self.expEdit.cursorPosition() == 0:
            self.expEdit.setCursorPosition(1)
        elif self.expEdit.cursorPosition() == (len(self.expEdit.text())):
            self.expEdit.setCursorPosition(len(self.expEdit.text())-1)       
            
    def popup(self,msgText):
        msg = QMessageBox()
        msg.setWindowTitle("Advertencia")
        msg.setText(msgText)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowIcon(QtGui.QIcon(':/icons/Variable_48px.png'))
        x = msg.exec_()
        return       
#---------------------------------------------------------------------------------------------
class Help_Window(QtWidgets.QDialog):
    """
    Pyqt standard dialog 
    
    Its purpose is to create a window to allow the user
    to find useful information to report a bug and give
    suggestions
    """
    def __init__(self):
        super(Help_Window, self).__init__()
        self.setWindowFlags( QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.setObjectName("Help_Window")
        self.setFixedSize(610,400)
        self.setWindowTitle("Ayuda")
        
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/Variable_48px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget_dialog")
        # stylesheet
        self.setStyleSheet(qss)    
        
        
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.HL_bugs = QtWidgets.QHBoxLayout()
        self.HL_bugs.setObjectName("HL_bugs")
        self.VL_mail = QtWidgets.QVBoxLayout()
        self.VL_mail.setObjectName("VL_mail")
        self.suggestion_title_label = QtWidgets.QLabel(self.centralwidget)
        self.suggestion_title_label.setObjectName("suggestion_title_label")
        self.suggestion_title_label.setText("¿Tienes sugerencias?, ¿Encontraste un Bug?")
        self.VL_mail.addWidget(self.suggestion_title_label)
        self.steps_label = QtWidgets.QLabel(self.centralwidget)
        self.steps_label.setObjectName("steps_label")
        self.steps_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.steps_label.setText("Escribe un correo a la dirección gadunsoporte@gmail.com \ncon el" +
                                 " asunto “soporte compilador”, detallando:\n\n    \u2022    "  +
                                 "Sugerencia o Bug (error dentro del programa)\n    \u2022    "+
                                 "Información de contacto (opcional)\n    \u2022    "          +
                                 "Screenshot del Bug (opcional)\n")
                                 
        self.VL_mail.addWidget(self.steps_label)
        self.HL_bugs.addLayout(self.VL_mail)
        self.ico_IdeaBug = QtWidgets.QLabel(self.centralwidget)
        self.ico_IdeaBug.setAlignment(QtCore.Qt.AlignCenter)
        self.ico_IdeaBug.setObjectName("ico_IdeaBug")
        self.ico_IdeaBug.setPixmap(QtGui.QPixmap(":/icons/idea-bug.png"))
        self.ico_IdeaBug.setToolTip("¡Tu opinión vale muchísimo!")
        #self.ico_IdeaBug.setText("ico imagen bug e idea")
        self.HL_bugs.addWidget(self.ico_IdeaBug)
        self.verticalLayout_3.addLayout(self.HL_bugs)
        
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_3.addWidget(self.line)
        self.VL_info = QtWidgets.QVBoxLayout()
        self.VL_info.setObjectName("VL_info")
       
        self.ico_github = Clickable_Label(self.centralwidget)
        self.ico_github.setAlignment(QtCore.Qt.AlignCenter)
        self.ico_github.setObjectName("ico_github")
        self.ico_github.setPixmap(QtGui.QPixmap(":/icons/github.png"))
        self.ico_github.setToolTip("Link al repositorio")
        #self.ico_github.setText("ico github, link repo ")
        self.VL_info.addWidget(self.ico_github)
        
        self.info_title_label = QtWidgets.QLabel(self.centralwidget)
        self.info_title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.info_title_label.setObjectName("info_title_label")
        self.info_title_label.setText("<a> Encuentra más información sobre el programa \n y su código fuente en el <a href=\"https://gitlab.com/JuanesCG/trabajo-de-grado\">repositorio oficial</a></a>")
        #+"<a href=\"https://github.com/JuanECG/Herramienta-de-apoyo-a-compiladores">github</a>")
        self.VL_info.addWidget(self.info_title_label)
        
        self.verticalLayout_3.addLayout(self.VL_info)
        
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout_3.addWidget(self.line_2)
        self.HL_autors = QtWidgets.QHBoxLayout()
        self.HL_autors.setObjectName("HL_autors")
        
        self.ico_u = QtWidgets.QLabel(self.centralwidget)
        self.ico_u.setAlignment(QtCore.Qt.AlignCenter)
        self.ico_u.setObjectName("ico_u")
        self.ico_u.setPixmap(QtGui.QPixmap(":/icons/logo-udenar.png"))
        self.HL_autors.addWidget(self.ico_u)
        #self.ico_u.setText("ico udenar, ing sistemas")
        
        self.autors_label = QtWidgets.QLabel(self.centralwidget)
        self.autors_label.setObjectName("autors_label")
        self.autors_label.setText("Autores:\n\n""Juan Esteban Castro Guerrero \n""Peter D\'loise Chicaiza Cortez")
        self.HL_autors.addWidget(self.autors_label)
        
        self.verticalLayout_3.addLayout(self.HL_autors)
        
        self.centralwidget.setGeometry(0,0,610,400)
        
        self.ico_github.clicked.connect(lambda:self.openGit())
        self.info_title_label.linkActivated.connect(lambda:self.openGit())
        
    def openGit(self):
        webbrowser.open("https://github.com/JuanECG/Herramienta-de-apoyo-a-compiladores")
      
#---------------------------------------------------------------------------------------------
#endregion: dialogs