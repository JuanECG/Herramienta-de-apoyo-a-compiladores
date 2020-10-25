import numpy as np
from lexic import *
from const import * 

class ExplanationStep:
    """
        Currently disable
    """
    def __init__(self):
        self.aProduction = None
        self.firstset = None
        self.explanation = None
        self.selectedInFirst = None
        self.selectedInProduction = -1

    def setAProduction(self, aProduction, noPro = False):
        production = []
        if noPro:
            production.append(' ')    
            for symbol in aProduction:
                production.append(symbol.getTag())
        else:
            production.append(aProduction.getLeftSide().getTag())
            if aProduction.getRightSide():
                for symbol in aProduction.getRightSide():
                    production.append(symbol.getTag())
        self.aProduction = production
    
    def setFirst(self, setFirst):
        first = []
        
        for symbol in setFirst:
            first.append(str(symbol))
        self.firstset = first
    
    def __str__(self):
        ret = f'Producción: {self.aProduction}'
        ret += f'\nSIP: {self.selectedInProduction}'
        ret += f'\n\nPrimero: {self.firstset}'
        ret += f'\nSIF: {self.selectedInFirst}'
        ret += f'\n\n {self.explanation}'
        return ret

class Symbol:
    """
    Class used to transfer information from the lexical module to the syntactic module

    Attributes
    ----------
    tag : string
        tag used to identify the symbol, if it's Terminal it is related with the name of a defined token
    stype : string
        string used to differentiate symbols, as terminals and NOnterminals
            TM = "Terminal"
            NT = "NonTerminal"
    
    Methods
    -------
    setTag(tag):
        defines the string as the symbol's tag it should be between '<>' if it is NO terminal, and doesn't
        use them if it is termminal
    setStype(stypea):
        defines the type of the symbol
    getTag():
        returns the symbol tag
    getStype():
        returns the symbol type
    """
    def __init__(self, tag, stype):
        self.__tag = tag
        self.__stype = stype

    def setTag(self, tag):
        self.__tag = tag

    def setStype(self, stype):
        self.__stype = stype
    
    def getTag(self):
        return self.__tag

    def getStype(self):
        return self.__stype

    def __str__(self):
        return self.__tag
    
    def __eq__(self, o_e):
        if type(o_e) is Symbol:
            if(self.getTag() == o_e.getTag() and
            self.getStype() == o_e.getStype()):
                return True
        return False

class Production:
    """
    This Class represents a production that has a left side and a right side used to define 
    a grammatical structure

    Attributes
    ----------
    leftSide : symbol
        An only one Nonterminal symbol that defines the production's left side
    rightSide : list
        A list of symbols Nonterminals and Terminals that define the production's right side
    selectionSet : list
        List with the set of symbols that represent the production's selection set
    next : list
        List with the set of symbols that represent the production's Next set
    first : list
        List with the set of symbols that represent the production's First set
    
    Methods
    -------
    setLeftSide(nSymbol):
        Sets the given symbol as the production's left side
    getLeftSide():
        Returns the left side symbol of the production
    addRightSideSymbol(nSymbol):
        Adds the given symbol to the end of the right side symbols list
    setRightSide(nSymbolist):
        Sets the given list as the production's right side
    getRightSide():
        Returns the production's right side
    setNext(nNext):
        Sets the given list as the production's Next set
    getNext():
        Returns the production's Next set
    setFirst(nFirst):
        Sets the given list as the production's First set
    getFirst():
        Returns the production's First set
    setSelectionSet(nSelectionSet):
        Sets the given list as the production's Selection set
    getSelectionSet():
        Returns the production's First set
    """
    def __init__(self, lefttSymbol=None):
        self.__leftSide = lefttSymbol
        self.__rightSide = []
        self.__selectionSet = None
        self.__next = None
        self.__first = None
        
    def __str__(self):
        string = self.__leftSide.getTag() + " →  "
        if self.__rightSide is not None and len(self.__rightSide) > 0:
            for symbol in self.__rightSide:
                string += symbol.getTag()+" "
        return string
    
    def setLeftSide(self, nSymbol):
        self.__leftSide = nSymbol

    def getLeftSide(self):
        return self.__leftSide

    def addRightSideSymbol(self, nSymbol):
        if self.__rightSide is None: self.__rightSide = []
        self.__rightSide.append(nSymbol)
    
    def setRightSide(self, nSymbolist):
        self.__rightSide = nSymbolist
    
    def getRightSide(self):
        return self.__rightSide

    def setNext(self, nNext):
        self.__next = nNext
        
    def getNext(self):
        return self.__next

    def setFirst(self, nFirst):
        self.__first = nFirst

    def getFirst(self):
        return self.__first

    def setSelectionSet(self, nSelectionSet):
        self.__selectionSet = nSelectionSet
    
    def getSelectionSet(self):
        return self.__selectionSet

    def __eq__(self, o_e):
        if (o_e.getLeftSide() == self.__leftSide and 
            o_e.getRightSide() == self.__rightSide):
            return True
        return False

class SyntacticAnalyzer:
    """
    This module holds the productions and symbols needed to define and execute a grammar in
    syntactic analysis. It requires a token list defined in lexical module to create Terminal symbols
    """
    def __init__(self, tokenList = None):
        self.__ntsymbolList = []
        self.__tmsymbolList = []
        self.__productionList = []
        self.__initialnt = None
        self.controlMatrix = None
        self.errorsDictionary = {}
        if(tokenList): self.loadTerminalSymbols(tokenList)
    
    def loadTerminalSymbols(self, tokenList):
        """
        Tooks the given Tokens list and turns it into a list of Nonterminal symbols

        Parameters
        -----------
        tokenList : list of Token
            list of tokens defined in lexical modulo
        """
        self.__tmsymbolList = []
        
        for token in tokenList:
            if(token.getTypeExp()== 1):
                for exp in token.getSetExp():
                    nSymbol = Symbol(token.getName()+":"+exp, TM)
                    self.__tmsymbolList.append(nSymbol)
            else:
                nSymbol = Symbol(token.getName(), TM)
                self.__tmsymbolList.append(nSymbol)
    
    def getNTSymbolList(self):
        """
        Returns the current Nonterminal symbols list
        """
        return self.__ntsymbolList

    def getTMSymbolList(self):
        """
        Returns the current Terminal symbols list
        """
        return self.__tmsymbolList

    # Metodo solo para debug
    def settmSymbolList(self, symbols):
        self.__tmsymbolList = symbols

    def setInitialNt(self, nSymbol):
        """
        Sets the given symbol as the INITIAL Nonterminal symbol of the grammar due to this, 
        it has to be a Nonterminal Symbol

        Parameters
        -----------
        nSymbol : Symbol
            Nonterminal symbol defined as the initial nonterminal
        """
        # SERIA CONVENIENTE VALIDAR QUE EL SIMBOLO EXISTA EN LA LISTA DE SIMBOLOS
        self.__initialnt = nSymbol
    
    def getInitialNt(self):
        """
        Returns the Initial Nonterminal symbol of the grammar
        """
        return self.__initialnt

    def addNoTerminalSymbol(self, symbolExp):
        """
        Creates a Nonterminal Symbol with the given string and appends it to the Nonterminal
        Symbols list

        Parameters
        -----------
        symbolExp : string
            String used to identify the new symbol, it should be between '<' and '>'
        """
        nSymbol = Symbol(symbolExp,NT)
        self.errorsDictionary[symbolExp] = {}
        self.__ntsymbolList.append(nSymbol)
    
    def removeNoTerminalSymbol(self, index):
        """
        Removes the Nonterminal Symbol in the index position

        Parameters
        -----------
        index : int
            Position of the symbol to be removed
        """
        ntTag = self.__ntsymbolList[index]
        if ntTag in self.errorsDictionary:
            del self.errorsDictionary[ntTag]
        self.__ntsymbolList.pop(index) 

    def getErrorDictionary(self):
        """
        Returns a dictionary that contains the errors defined by the user
        """
        return self.errorsDictionary

    def getErrorMessage(self, x, y):
        """
        Looks into the dictionaries for an error message in the given coordinates

        Parameters
        -----------
        x : int
            Position of the symbol in the control table related to the row
        y : int
            Position of the symbol in the control table related to the column
        
        Returns
        -------
        Returns a string with the error message defined for the given coordinates, if doesn't exist
        such message it returns None

        """

        nIndexRow, nIndexCol = self.getControlMatrixIndex(True)

        rowk = colk = None
        for row in nIndexRow.keys():
            if nIndexRow[row] == x:
                rowk = row
                break
        for col in nIndexCol.keys():
            if nIndexCol[col] == y:
                colk = col
                break
        
        if rowk and colk:
            errorDic = self.errorsDictionary
            if rowk not in errorDic: return None
            if colk in errorDic[rowk]:
                return errorDic[rowk][colk]
        return None
    
    def setErrorMessage(self, x, y, msg):
        """
        Creates into the dictionaries an error message in the given coordinates

        Parameters
        -----------
        x : int
            Position of the symbol in the control table related to the row
        y : int
            Position of the symbol in the control table related to the column
        msg : string
            Error message defined for the matching coordinates
        """
        nIndexRow, nIndexCol = self.getControlMatrixIndex(True)

        rowk = colk = None
        for row in nIndexRow.keys():
            if nIndexRow[row] == x:
                rowk = row
                break
        for col in nIndexCol.keys():
            if nIndexCol[col] == y:
                colk = col
                break
    
        if rowk and colk:
            errorDic = self.errorsDictionary
            if rowk not in errorDic:
                errorDic[rowk] = {}
            errorDic[rowk][colk] = msg
    
    def removeNTbyExp(self,exp):
        """
        Removes the Nonterminal Symbol identified with the given expression

        Parameters
        -----------
        exp : string
            Expression that identifies the nonterminal symbol to be removed
        """
        symbol = Symbol(exp,NT)
        if exp in self.errorsDictionary:
            del self.errorsDictionary[exp]

        for production in self.__productionList:
            if production.getLeftSide():
                if production.getLeftSide() == symbol:
                    production.setLeftSide(None)
                if production.getRightSide() is not None and symbol in production.getRightSide():
                    production.getRightSide().remove(symbol)
                    
        self.__ntsymbolList.remove(symbol) 
    
    def setNoTerminalSymbol(self, index, nSymbol):
        """
        Replace the Nonterminal symbol in the given position with the given symbol

        Parameters
        ----------
        index : int
            Position of the Nonterminal symbol to be replaced
        nSymbol : Symbol
            New symbol to be inserted into the old symbol position
        """
        self.removeNoTerminalSymbol(index)
        self.__ntsymbolList.insert(nSymbol)  

    def addProduction(self, nProduction):
        """
        Adds the given production to the productions list

        Parameters
        ----------
        """
        self.__productionList.append(nProduction)

    def removeProduction(self, index):
        """
        Remove the production in the given position from the productions list

        Parameters
        ----------
        index : int
            position of the production to be removed
        """
        self.__productionList.pop(index)

    def setProduction(self, index, nProduction):
        """
        Replace the production in the given position with the given production
        
        Parameters
        ----------
        index : int
            position of the production to be replaced
        nProduction : Production
            new production to be positioned instead the old production
        """
        self.removeProduction(index)
        self.__productionList.insert(index, nProduction)

    def getProductionList(self):
        """
        Returns the current production list
        """
        return self.__productionList
    
    def setProductionList(self, nProductionList):
        """
        Replace the current productions list with the given one
        
        Parameters
        ----------
        nProductionList : List of Productions
            new list of productions
        """
        self.__productionList = nProductionList

    def isTMUsed(self,token_tag):
        """
        Verifies if the given expression is owned by a symbol used in the grammar in any production
        
        Parameters
        ----------
        token_tag : string
            tag of the symbol to be verified

        Returns
        -------
            Returns True if the given symbol expression is used in some of the defined productions
            and False if it isn't
        """
        symbol = Symbol(token_tag,TM)
        for production in self.__productionList:
            if production.getRightSide() and symbol in production.getRightSide():
                return True
        return False  

    def setTMSymbol(self, newTMTag, oldTMTag):
        """
        NO defined
        
        Parameters
        ----------

        Returns
        -------
        """
        oldSymbol = Symbol(oldTMTag, TM)
        if oldSymbol in self.__tmsymbolList:
            index = self.__tmsymbolList.index(oldSymbol)
            self.__tmsymbolList[index].setTag(newTMTag)

            for production in self.__productionList:
                if production.getRightSide() is not None:
                    while (oldSymbol in production.getRightSide()):
                        index = production.getRightSide().index(oldSymbol)
                        production.getRightSide()[index].setTag(newTMTag)
    
    def removeTMSymbol(self, tokenTag):
        """
        Removes the given symbol from the Terminal symbols list and deletes its appearances
        in the defined productions
        
        Parameters
        ----------
        tokenTag : string
            Tag of the Terminal symbol to be removed

        Returns
        -------
            Returns the set of coordinates given as production and symbol position, of the places where
            was removed the given Terminal symbol
        """
        symbol = Symbol(tokenTag,TM)

        if symbol in self.__tmsymbolList:
            self.__tmsymbolList.remove(symbol)

        for production in self.__productionList:
            if production.getRightSide() is not None:
                i = 0
                while (symbol in production.getRightSide()):
                    production.getRightSide().remove(symbol)
                    i += 1    

    def findTMsymbol(self, tag):
        """
        Returns the Terminal symbol that contains the given tag
        
        Parameters
        ----------
        tag : string
            tag of the symbol to be found
        """
        for symbol in  self.__tmsymbolList:
            if symbol.getTag() == tag:
                return symbol
        return None

    def findNTsymbol(self, tag):
        """
        Returns the Nonterminal symbol that contains the given tag
        
        Parameters
        ----------
        tag : string
            tag of the symbol to be found
        """
        for symbol in  self.__ntsymbolList:
            if symbol.getTag() == tag:
                return symbol
        return None
    
    def updateRightSideProduction(self, RS, production):
        """
        Replace the list on the right side of the production with the list given
        
        Parameters
        ----------
        RS : string
            list of strings with the tags of the symbols to be replaced
        production : Production
            production to be updated
        """
        right_side = []
        if len(RS) > 0:
            for item in RS:
                symbol = self.findTMsymbol(item)
                if not symbol: symbol = self.findNTsymbol(item)
                right_side.append(symbol) 
            production.setRightSide(right_side)
        else: production.setRightSide(None)

    def validateGrammar(self):
        """
        Runs a serie of analysis over the defined grammar and validates if it is according to
        LL(1) grammars structure
        """
        if len(self.__ntsymbolList) == 0:
            return GV_0NT_SYMBOLS
        self.__initialnt = self.__ntsymbolList[0]

        # Utilizaremos el algoritmo de No terminales extraños
        aliveSymbols = self.__tmsymbolList.copy()
        
        nProductionList = self.__productionList.copy()
        try:
            self.analysisAliveProductions(aliveSymbols, nProductionList)    
        except:
            return (GV_ALIVE_EXECUTION_ERROR, None)
        
        # Verificacion de lista de producciones
        if(len(nProductionList) > 0): # Si nProductionList contiene producciones, estas son producciones muertas
            return (GV_DEATH_ERROR, nProductionList)

        # AQUI SE DEBE VERIFICAR LA EXISTENCIA DE SIMBOLOS NO UTILIZADOS
        if len(aliveSymbols) != (len(self.getNTSymbolList())+len(self.getTMSymbolList())):
            nUnusedSymbolList = []
            for symbol in self.getNTSymbolList():
                if symbol not in aliveSymbols:
                    nUnusedSymbolList.append(symbol.getTag())
            return (GV_UNUSEDNT_ERROR, nUnusedSymbolList)

        #Si es vacía, entonces no hay simbolos muertos, así que evaluamos si las producciones son alcanzables
        reachableSymbols = []
        reachableSymbols.append(self.getInitialNt())
        nProductionList = self.__productionList.copy()

        try:
            self.analysisReachableProductions(reachableSymbols, nProductionList)
        except:
            return (GV_REACH_EXECUTION_ERROR, None)

        # Verificacion de lista de producciones
        if(len(nProductionList) > 0): # Si nProductionList contiene producciones, estas son producciones inalcanzables
            return (GV_UNREACHABLE_ERROR, nProductionList)
        #Si es vacía, entonces no hay simbolos muertos, así que evaluamos si las producciones son alcanzables
    
        return (GV_OK, None)
        #Puede evaluarse la necesidad de indicar las producciones o symbolos problematicos
        
    def runSyntax(self, mainChar):
        """
        Executes a syntactic analysis over a secuence of subtokens given from lexical analysis using
        the rules defined by the typed grammar

        Parameters
        ----------
        mainChar : List of Tokens
            Resultant tokens secuence of the lexical analysis given for the Lexical Module

        Returns
        -------
        A tuple with the next positions:
            0: False -- If there was a syntactic error in the analysis
            0: True -- If the secuence was acepted

            1: A string with the message resultant of the analysis, error or accepted

            2: If the first position is False, it contains the position of the syntactic error
               else None

        """
        # Agregar subtoken, fin de cadema

        if len(mainChar) > 0:
            eocs = SubToken(EOC, EOC, (mainChar[-1].getPosition()[0], mainChar[-1].getPosition()[1]+1))
        else:
            eocs = SubToken(EOC, EOC, (0,0))
        mainChar.append(eocs)

        stack = []
        stack.append(self.getInitialNt())
        head = 0
        while(len(stack) != 0):
            if stack[-1].getStype() == TM:
                if mainChar[head].getToken() == stack[-1].getTag():
                    stack.pop()
                    head +=1
                else:
                    message = self.getDefinedError(stack[-1],mainChar[head])
                    return (False, message, mainChar[head].getPosition())
            else:
                production = self.findProduction(stack[-1].getTag(), mainChar[head].getToken())
                if production is not None:
                    head = self.applyProduction(production, stack, head)
                else:
                    message = self.getDefinedError(stack[-1],mainChar[head], True)
                    return (False, message, mainChar[head].getPosition())
        if (mainChar[head] != eocs):
            stackBot = Symbol(STACKBOTTOM, NT)
            message = self.getDefinedError(stackBot,mainChar[head], True)
            return (False, message, mainChar[head].getPosition())
        return (True, 'Secuencia aceptada', None)

    def getDefinedError(self, stackTop, headChar, awaited = False):
        """
        Returns the user defined error if it exist, else will return a default error

        Parameters
        ----------
        stackTop: Symbol
            Symbol on the top position of the stack
        headChar: Subtoken
            Subtoken on the header of the analyzed secuence
        awaited : boolean
            Flag to determinate if is needed an awaited symbols analysis (Just for Nonterminals)
        """
        
        message = f'Error sintáctico en fila {headChar.getPosition()[0]} elemento {headChar.getPosition()[1]}:\n'
        if stackTop.getTag() in self.errorsDictionary and headChar.getToken() in self.errorsDictionary[stackTop.getTag()]:
            message += self.errorsDictionary[stackTop.getTag()][headChar.getToken()]
        else:
            if awaited:
                message += f'Se encontró {headChar.getToken()} y se esperaba {str(self.getAwaitedSets(stackTop.getTag()))}'
            else:
                message += f'Se encontró {headChar.getToken()} y se esperaba {stackTop.getTag()}'

        return message

    def getAwaitedSets(self, symbol):
        """
        Analyzes the grammar and gets the awaited symbols for the given symbol
        
        Parameters
        ----------
        symbol : string
            Tag of the symbol to be analyzed
        """
        if symbol == STACKBOTTOM:
            return [f'Fin de Cadena({EOC})']
        else:
            awaited = []
            for production in self.__productionList:
                if production.getLeftSide().getTag() == symbol:
                    awaited.extend(production.getSelectionSet())
                    if EOC in awaited:
                        awaited.remove(EOC)
                        awaited.append(f'Fin de Cadena({EOC})')
            if len(awaited) == 0:
                awaited.append(symbol)
                
            return awaited

    def validateAmbiguity(self):
        """
        Compares the defined selection sets and verifies if exist ambiguity between two of them

        Returns
        -------
        None if there is no ambiguity in the grammar or the productions that have
        ambiguity
        """
        productionsets = {}
        try:
            for production in self.__productionList:
                if production.getLeftSide().getTag() not in productionsets:
                    productionsets[production.getLeftSide().getTag()] = []
                productionsets[production.getLeftSide().getTag()].append(production)
            
            for symbol in productionsets.keys():
                ambiguousProductions = []
                for production in productionsets[symbol]:
                    index = productionsets[symbol].index(production) + 1
                    for nProduction in productionsets[symbol][index:]:
                        inter = set(production.getSelectionSet()).intersection(set(nProduction.getSelectionSet()))
                        if len(inter) > 0:
                            ambiguousProductions.append(nProduction)
                    if len(ambiguousProductions) > 0:
                        ambiguousProductions.append(production)
                        return (GV_AMBIGUOUS_ERROR, ambiguousProductions)
            return (GV_OK, None)
            
        except:
            return (GV_AMBIGUOUS_EXECUTION_ERROR, None)        

    def getAmbiguityExplanation(self, amb_Symbol, ls_Symbol):
        explanation = 'Punto de ambigüedad, se puede aplicar las producciones:\n'
        pos = 1
        for production in self.__productionList:
            if (production.getLeftSide().getTag() == ls_Symbol and 
            amb_Symbol in production.getSelectionSet()):
                explanation += f'{pos}. {production}{NL}'
            pos += 1

        return explanation
    
    def findProduction(self, symbol, subtoken):
        """
        Finds the production to be applied with the symbol on stack top and that
        contains the given symbol in its selection set
        """
        for production in self.__productionList:
            if( production.getLeftSide().getTag() == symbol and 
               subtoken in production.getSelectionSet()):
                if production.getRightSide() is None:
                    return []
                return production.getRightSide()
        return None

    def applyProduction(self, production, stack, head):
        """
        Applies the given production to the stack and head variable
        """
        stack.pop()
        if production is not None and len(production)>0:
            if production[0].getStype()==TM:
                # Reconoce terminal, pop Avanza
                head +=1
                production = production[1:]
            # Remplaza...
            for symbol in reversed(production):
                stack.append(symbol)
        return head

    def analysisAliveProductions(self, aliveSymbols, nProductionList):
        """
        Analyzes the production list looking for death Symbols
        """
        newSymbol = True
        while (newSymbol):
            newSymbol = False
            for production in nProductionList:
                if (not production.getRightSide() or all(symbol in aliveSymbols for symbol in production.getRightSide())):
                    nProductionList.remove(production)
                    if(production.getLeftSide() not in aliveSymbols):
                        aliveSymbols.append(production.getLeftSide())
                    newSymbol = True
                    break                

    def analysisReachableProductions(self, reachableSymbols, nProductionList):
        """
        Analyzes the production list looking for no Reachable symbols
        """
        newSymbol = True
        while (newSymbol):
            newSymbol = False
            for production in nProductionList:
                
                if production.getLeftSide() in reachableSymbols:
                    nProductionList.remove(production)
                    if production.getRightSide():
                        for symbol in production.getRightSide():
                            if(symbol not in reachableSymbols):
                                reachableSymbols.append(symbol)
                    newSymbol = True
                    break                        

    def generateSelectionSets(self):
        """
        It runs a step sequence to get First, Next and Selection sets for each production
        """
        nProductionList = self.__productionList.copy()
        # nVoidableNtList Lista de producciones anulables
        # nFirstSetList Lista de Conjunto Primero por produccion
        
        #Paso 1
        # Primer análisis, elimincacion de producciones que contengan terminales en el LD
        try:    self.firstAnalysis(nProductionList)
        except:    return GV_1STANALISYS_EXECUTION_ERROR

        # Segundo análisis, Obtencion No terminales anulables
        try:    nVoidableNtList = self.secondAnalysis(nProductionList)
        except:    return GV_2NDANALISYS_EXECUTION_ERROR

        #Paso 2
        # Preparacion de Entorno
        nProductionList = self.__productionList.copy()
        size = len(self.__ntsymbolList) + len(self.__tmsymbolList)
        nMatrixIndex = self.generateMatrixIndex()
        nMatrixEDC = np.zeros((size, size))

        # Tercer análisis, generacion de relacion Empieza-Directamente-Con(nMatrixEDC)
        try:    self.thirdAnalysis(nProductionList,nVoidableNtList, nMatrixIndex, nMatrixEDC)
        except:    return GV_3RDANALISYS_EXECUTION_ERROR

        # Paso 3
        # Apicación de propiedad de Clausura Reflexiva(warshallAlgorithm) a nMatrixEDC,
        # para obtener relacion Empieza-Con(nMatrixEC)
        try:    nMatrixEC = self.warshallAlgorithm(nMatrixEDC)
        except:    return GV_WARSHALL_EXECUTION_ERROR

        # Paso 4
        # Cuarto análisis, Obtención de lista de "Conjuntos Primero" para cada símbolo
        try:    nSymbolFirstSetList = self.fourthAnalysis(nMatrixIndex,nMatrixEC)
        except:    return GV_4THANALISYS_EXECUTION_ERROR

        # Paso 5
        # Quinto análisis, Obtencion de lista de "Conjuntos Primero" para cada producción 
        try:    nFirstSetList = self.fifthAnalysis(nSymbolFirstSetList, nProductionList, nVoidableNtList)
        except:    return GV_5THANALISYS_EXECUTION_ERROR

        #Paso 6
        #Generación de relación es-seguido-directamente-por(nMatrixSDP)
        # Preparacion
        nMatrixSDP = np.zeros((size, size))
        # Sexto análisis
        try:    self.sixthAnalysis(nProductionList, nMatrixIndex, nMatrixSDP, nVoidableNtList)
        except:    return GV_6THANALISYS_EXECUTION_ERROR

        # Paso 7
        # Preparacion 
        nMatrixFDD = np.zeros((size, size))
        # Septimo análisis
        try:    self.seventhAnalysis(nProductionList, nMatrixIndex, nMatrixFDD, nVoidableNtList)
        except:    return GV_7THANALISYS_EXECUTION_ERROR

        # Paso 8
        #  Generación de relación es-fin-de
        try:    nMatrixFD = self.warshallAlgorithm(nMatrixFDD)
        except:    return GV_WARSHALL_EXECUTION_ERROR

        # Paso 9
        # Generación de relación es-seguido-de
        try:
            tmpMatrix1 = np.dot(nMatrixFD, nMatrixSDP)
            nMatrixSD = np.dot(tmpMatrix1, nMatrixEC)
        except:    return GV_DOTOPERATION_EXECUTION_ERROR
        # Paso 10
        # Agregar a la matriz SD el elemento fin de cadena
        try:    nMatrixSD = self.eighthAnalysis(nMatrixIndex, nMatrixSD, nMatrixFD)
        except:    return GV_8THANALISYS_EXECUTION_ERROR

        # Paso 11
        # Generación de conjunto siguiente para cada no terminal
        try:    nFollowSetList = self.ninethAnalysis(nMatrixIndex, nMatrixSD)
        except:    return GV_9THANALISYS_EXECUTION_ERROR

        # Paso 12 
        # Generación de conjunto seleccion
        try:    self.tenthAnalysis(nProductionList, nFollowSetList, nSymbolFirstSetList, nVoidableNtList)
        except:    return GV_10THANALISYS_EXECUTION_ERROR

        # Generación de tabla de control
        try: self.controlMatrix = self.generateControlMatrix(True)
        except:    return GV_SELECTIONMX_EXECUTION_ERROR

        return GV_OK

    def getControlMatrix(self):
        """
        Returns the current control Matrix
        """
        return self.controlMatrix
    
    def generateControlMatrix(self, stackBot = False):
        """
        Defines the Control Matrix based on the current grammar
        """

        nIndexRow, nIndexCol = self.getControlMatrixIndex(stackBot)
        controlMatrix = np.zeros((len(nIndexRow), len(nIndexCol)))
        row = col = 0
        for row in range(len(controlMatrix)):
            for col in range(len(controlMatrix[0])):
                controlMatrix[row][col] = CM_INITIAL_ERROR_VALUE
                col += 1
            row += 1
    
        productionIndex = 1
        for production in self.__productionList:
            leftSymbol = production.getLeftSide().getTag()
            for symbol in production.getSelectionSet():
                if controlMatrix[nIndexRow[leftSymbol]][nIndexCol[symbol]] == CM_INITIAL_ERROR_VALUE:
                    controlMatrix[nIndexRow[leftSymbol]][nIndexCol[symbol]] = productionIndex
                else:
                    controlMatrix[nIndexRow[leftSymbol]][nIndexCol[symbol]] = CM_AMBIGUOUS

            productionIndex += 1

        stackTerminals = []
        for production in self.__productionList:
            if production.getRightSide() is not None and len(production.getRightSide())>1:
                for symbol in production.getRightSide()[1:]:
                    if symbol.getStype() == TM:
                        stackTerminals.append(symbol.getTag())
        
        for symbol in stackTerminals:
            controlMatrix[nIndexRow[symbol]][nIndexCol[symbol]] = CM_POP_ADVANCE
        
        if stackBot:
            controlMatrix[nIndexRow[STACKBOTTOM]][nIndexCol[EOC]] = CM_ACCEPTED

        return controlMatrix

    def generateMatrixIndex(self):
        """
        Returns a dictionary that links Terminal and Nonterminal symbols with
        numerical positions of a Matrix
        """
        # Usamos un diccionario el cual guardara la posicion de fila y columna
        # a la que esta relacionada un symbolo
        nMatrixIndex = {}
        i = 0
        for symbol in self.__ntsymbolList:
            nMatrixIndex[symbol.getTag()] = i
            i+=1
        for symbol in self.__tmsymbolList:
            nMatrixIndex[symbol.getTag()] = i
            i+=1
        return nMatrixIndex

    def getControlMatrixIndex(self, stackBot = False):
        """
        Returns two dictionaries that links Terminal and Nonterminal symbols with
        numerical positions on the Control Matrix
        """
        nIndexCol = {}
        nIndexRow = {}
        i = j = 0
        for symbol in self.__ntsymbolList:
            nIndexRow[symbol.getTag()] = i
            i+=1

        # OBTENER TERMINALES DESPUES DEL PRIMER ELEMENTO
        for production in self.__productionList:
            if production.getRightSide() is not None and len(production.getRightSide())>1:
                for symbol in production.getRightSide()[1:]:
                    if symbol.getStype() == TM and symbol.getTag() not in nIndexRow:
                        nIndexRow[symbol.getTag()] = i
                        i+=1

        if stackBot:
            nIndexRow[STACKBOTTOM] = i

        for symbol in self.__tmsymbolList:
            nIndexCol[symbol.getTag()] = j
            j+=1
        nIndexCol[EOC] = j

        return nIndexRow, nIndexCol

    def firstAnalysis(self, nProductionList):
        """
        Analyzes the production list and removes every production with Terminal
        symbols on their right side
        """
        terminals = self.__tmsymbolList.copy()
        for production in nProductionList:
            if production.getRightSide():
                if any(symbol in terminals for symbol in production.getRightSide()):
                    nProductionList.remove(production)

    def secondAnalysis(self, nProductionList):
        """
        Applies the alive productions analysis over the production list to get
        the voidable symbols list
        """
        nVoidableNtList = []
        self.analysisAliveProductions(nVoidableNtList, nProductionList)
        return nVoidableNtList
    
    def thirdAnalysis(self, nProductionList, nVoidableNtList, nMatrixIndex, nMatrixEDC):
        """
        Iterates over the resultant productions list and defines the relation
        Begins-Directly-with(nMatrixEDC)
        """
        for production in nProductionList:
            if production.getRightSide() is not None:
                for symbol in production.getRightSide():
                    nMatrixEDC[nMatrixIndex[production.getLeftSide().getTag()]][nMatrixIndex[symbol.getTag()]] = 1
                    if symbol not in nVoidableNtList:
                        break
    
    def fourthAnalysis(self, nMatrixIndex, nMatrixEC):
        """
        Iterates over the Matrix Begins-With (nMatrixEC) and extract the First Set of each symbol
        """
        nFirstSetList = {}
        for tagRow, indexRow in nMatrixIndex.items():
            if self.findNTsymbol(tagRow):
                firstSet = []
                for tagCol, indexCol in nMatrixIndex.items():
                    if(nMatrixEC[indexRow][indexCol] == 1 and self.findTMsymbol(tagCol)):
                        firstSet.append(tagCol)
                nFirstSetList[tagRow] = firstSet
        return nFirstSetList

    def fifthAnalysis(self, nSymbolFirstSetList, nProductionList, nVoidableNtList):
        """
        Defines the First Set of each Production
        """
        nFirstSetList = []
        for production in nProductionList:
            firstSet = []
            if production.getRightSide() is not None:
                for symbol in production.getRightSide():
                    if(symbol.getStype()==TM):
                        firstSet.append(symbol.getTag())
                        break
                    else:
                        firstSet.extend(nSymbolFirstSetList[symbol.getTag()])
                        if symbol not in nVoidableNtList:
                            break
            nFirstSetList.append(firstSet)
        return nFirstSetList

    def sixthAnalysis(self, nProductionList, nMatrixIndex, nMatrixSDP, nVoidableNtList):
        """
        Defines relation Followed-Directly-By(nMatrixSDP)
        """
        for production in nProductionList:
            if production.getRightSide() is not None and len(production.getRightSide()) > 1:
                i = 0
                for symbol1 in production.getRightSide()[:-1]:
                    i += 1
                    for symbol2 in production.getRightSide()[i:]:
                        nMatrixSDP[nMatrixIndex[symbol1.getTag()]][nMatrixIndex[symbol2.getTag()]] = 1
                        if symbol2 not in nVoidableNtList:
                            break

    def seventhAnalysis(self, nProductionList, nMatrixIndex, nMatrixFDD, nVoidableNtList):
        """
        Defines relation Direct-End-Of(nMatrixFDD)
        """
        for production in nProductionList:
            if production.getRightSide() is not None:
                for symbol in reversed(production.getRightSide()):
                    nMatrixFDD[nMatrixIndex[symbol.getTag()]][nMatrixIndex[production.getLeftSide().getTag()]] = 1
                    if symbol not in nVoidableNtList:
                            break

    def eighthAnalysis(self, nMatrixIndex, nMatrixSD, nMatrixFD):
        """
        Adds to the relation Followed-by(nMatrixSD) the column of End of sequence
        """
        sizeR = len(nMatrixSD)
        tmpMatrix = np.zeros((sizeR, sizeR+1))
        for row in range(sizeR):
            for col in range(sizeR):
                if nMatrixSD[row][col] >= 1:
                    tmpMatrix[row][col] = 1
            if nMatrixFD[row][nMatrixIndex[self.getInitialNt().getTag()]] >= 1:
                tmpMatrix[row][sizeR] = 1
        return tmpMatrix

    def ninethAnalysis(self, nMatrixIndex, nMatrixSD):
        """
        Defines the Next Set for each Nonterminal
        """
        nFollowSetList = {}
        lastOnePos = len(nMatrixIndex)
        for tagRow, indexRow in nMatrixIndex.items():
            if self.findNTsymbol(tagRow):
                followSet = []
                for tagCol, indexCol in nMatrixIndex.items():
                    if(nMatrixSD[indexRow][indexCol] == 1 and self.findTMsymbol(tagCol)):
                        followSet.append(tagCol)
                if nMatrixSD[indexRow][lastOnePos] == 1:
                    followSet.append(EOC)
                nFollowSetList[tagRow] = followSet
        return nFollowSetList
    
    def tenthAnalysis(self, nProductionList, nFollowSetList, nFirstSetList, nVoidableNtList):
        """
        It links First, Next, and Selection Set for each production
        """
        for production in nProductionList:
            selectionSet = []
            firstSet = []
            nextSet = []
            if production.getRightSide() is not None:
                for symbol in production.getRightSide():
                    if symbol.getStype() == TM:
                        firstSet.append(symbol.getTag())
                        selectionSet.append(symbol.getTag())
                        break
                    else:
                        selectionSet.extend(nFirstSetList[symbol.getTag()])
                        firstSet.extend(nFirstSetList[symbol.getTag()])
                        if symbol not in nVoidableNtList:
                            break
                # ANULABLE
                if all(symbol in nVoidableNtList for symbol in production.getRightSide()):
                    nextSet.extend(nFollowSetList[production.getLeftSide().getTag()])
                    selectionSet.extend(nFollowSetList[production.getLeftSide().getTag()])

            else:
                nextSet.extend(nFollowSetList[production.getLeftSide().getTag()])
                selectionSet.extend(nFollowSetList[production.getLeftSide().getTag()])
            production.setSelectionSet(selectionSet)
            production.setFirst(firstSet)
            production.setNext(nextSet)

    def warshallAlgorithm(self, nMatrix):    
        """
        Applies reflexive transitive clausure property over the given Matrix
        """
        # Este algoritmo aplica la propiedad de clausura sobre una matriz
        assert (len(row) == len(nMatrix) for row in nMatrix)
        n = len(nMatrix)
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    nMatrix[i][j] = nMatrix[i][j] or (nMatrix[i][k] and nMatrix[k][j])
                    if i == j: nMatrix[i][j] = 1
        return nMatrix

    def explainProduction(self, pIndex):
        """
        Returns explanation items of the production in the index position in the production list
        
        Parameters
        ----------
        pIndex : int
            Position of the production to be explained
        
        Returns
        -------
        A tuple with the positions:
            0: String -- Representation of the production
            1: Boolean -- True if the given production is voidablo, else False
            2: String -- Sintetized explication of the production aplication
        """
        production = self.__productionList[pIndex]
        # LADO IZQ DER
        
        rs = ''
        ls = '' + production.getLeftSide().getTag()
        if production.getRightSide() is not None:
            for symbol in production.getRightSide():
                rs += symbol.getTag() + ' '
        lrs = [ls,rs]

        # ANULABLE
        voidable = True
        if production.getRightSide() is not None and len(production.getRightSide()) > 0:
            try:    nVoidableNtList = self.secondAnalysis(self.__productionList.copy())
            except:    return GV_2NDANALISYS_EXECUTION_ERROR, None, None
            if not all(symbol in nVoidableNtList for symbol in production.getRightSide()):
                voidable = False
        
        # APLICACION
        aplication = ''
        if production.getRightSide() is not None and len(production.getRightSide()) > 0:
            if len(production.getRightSide()) > 1:
                aplication +='re('
                rep = production.getRightSide()[1:] if production.getRightSide()[0].getStype() == TM else production.getRightSide()
                for symbol in reversed(rep):
                    aplication += f' {symbol.getTag()} '
                aplication +=') \n'
            else:
                aplication +='pop \n'

            if production.getRightSide()[0].getStype() == NT:
                aplication += 'retiene'
            else:
                aplication += 'avanza'
        else:
            aplication += 'pop \n'
            aplication += 'retiene'

        return lrs, voidable, aplication

    def explainSelectionSet(self, index):
        """
        NO defined
        
        Parameters
        ----------

        Returns
        -------
        """
        introExplanation = []
        firstExplanation = []
        nextExplanation = []

        aProduction = self.__productionList[index]

        introStep = ExplanationStep()
        # VALIDAR QUE SE ENCUENTRE LA PRODUCCION DE LO CONTRARIO DARA ERROR
        # CONJUNTO PRIMERO
        # AGREGAR ULTIMO PASO QUE INDIQUE QUE CONJUNTO SELECCION ES PRIMERO U SIGUIENTE O SOLO PRIMERO
        # AGREGAR SELECCION SET A INTRODUCCIÓN
    
        nProductionList = self.getProductionList().copy()
        nVoidableNtList = self.secondAnalysis(nProductionList)
        
        setFirst = []
        looked = []
        ntFlag = False
        setFirst, firstExplanation, ntFlag = self.explainedFirst(aProduction.getLeftSide(),setFirst, looked, nVoidableNtList, firstExplanation, ntFlag, aProduction)

        if ntFlag:
            
            while (ntFlag):
                aStep = ExplanationStep()
                aStep.explanation = "Terminado el análisis se revisa el conjunto PRIMERO resultante:"
                
                selectInFirst = []
                ntString = "( "
                ntCounter = 0
                for symbol in setFirst:
                    if  symbol.getStype() == NT:
                        ntString += f"{symbol}, "
                        ntCounter += 1
                        selectInFirst.append(setFirst.index(symbol))
                ntString = ntString[:-2]+" )"

                if ntCounter == 1: aStep.explanation += f"\nEn este caso existe un símbolo NO terminal {ntString}"
                else: aStep.explanation += f"\nEn este caso existen símbolos NO terminales {ntString}"
                
                aStep.explanation += f" dentro del conjunto, así que para obtener el conjunto PRIMERO de ({str(aProduction)}) es necesario obtener el conjunto PRIMERO de {ntString}, y reemplazarlo."
                aStep.selectedInFirst = selectInFirst
                aStep.setFirst(setFirst)
                
                firstExplanation.append(aStep)

                ntFlag = False

                newFirst = setFirst.copy()

                for symbol in setFirst:
                    #aStep = ExplanationStep()
                    if symbol not in looked:
                        looked.append(symbol)

                        if symbol.getStype() == TM:  continue

                        newFirst, firstExplanation, ntFlag = self.explainedFirst(symbol, newFirst, looked, nVoidableNtList, firstExplanation, ntFlag)
                        
                # Despues de cada for podria agregarse un Paso?

                setFirst = newFirst
            # AGREGAR PASOS DE FINALIZACION
        aStep = ExplanationStep()
        if len(setFirst) > 0:
            aStep.explanation = f"\nCon el conjunto {FIRSTW} libre de NO terminales, obtenemos:"
            aStep.explanation += f"\nConjunto {FIRSTW}{self.printFirstSymbols(aProduction.getRightSide(), True)} = {self.printFirstSymbols(setFirst)}"
            aStep.setFirst(setFirst)
        else: aStep.explanation = f"\nConjunto PRIMERO de ({aProduction}): VACÍO"
        
        firstExplanation.append(aStep)

        
        #CONJUNTO SIGUIENTE
        if not aProduction.getRightSide() or all(symbol in nVoidableNtList for symbol in aProduction.getRightSide()):
            introStep.explanation = f'Para obtener el conjunto SELECCION de ( {aProduction} ) se necesita obtener el conjunto PRIMERO de vacio '
            introStep.explanation += f'y el conjunto {NEXTW} de {aProduction.getLeftSide()}. '
            aStep = ExplanationStep()
            aStep.setAProduction(aProduction)
            aStep.explanation = f'Como el lado derecho de la producción es anulable se debe obtener el conjunto siguiente de {aProduction.getLeftSide()}, '
            aStep.explanation += f'para lo que se requiere analizar todas las producciones que contenga al símbolo {aProduction.getLeftSide()} del lado derecho, como:'

            #nextProductions= []
            index = 0
            postSteps = []
            fNextSet = []
            currentNextSet = []
            looked = [] # GLOBAl
            currentNextSymbol = aProduction.getLeftSide()
            newSteps = None
            for production in self.__productionList:

                if production.getRightSide() is not None and aProduction.getLeftSide() in production.getRightSide():
                    aStep.explanation += f'\n\nProducción {index}: {production}'
                    # AQUI DEBE PASAR ANALISIS
                    newSteps, looked, currentNextSet = self.explainedNext(aProduction.getLeftSide(), production, index, nVoidableNtList, fNextSet, looked, currentNextSet, currentNextSymbol)
                    postSteps.extend(newSteps)
                    #nextProductions.append(production)
                
                index += 1
            

            nextExplanation.append(aStep)
            nextExplanation.extend(postSteps)

            aStep = ExplanationStep()
            aStep.setFirst(currentNextSet)
            #aStep.explanation = f'CONCLUYE'
            #aStep.explanation = f'\nConcluye, conjunto SELECCION({self.__productionList.index(aProduction)}): {self.printFirstSymbols(currentNextSet)}.'
            aStep.explanation = f'Concluye, conjunto SELECCION({self.__productionList.index(aProduction)}) =  {FIRSTW}{self.printFirstSymbols(aProduction.getRightSide(), True)} U {NEXTW}({aProduction.getLeftSide()})'
            aStep.explanation += f'\n{FIRSTW}{self.printFirstSymbols(aProduction.getRightSide(), True)} =  {self.printFirstSymbols(setFirst)}'
            aStep.explanation += f'\n{NEXTW}({aProduction.getLeftSide()}) =  {self.printFirstSymbols(currentNextSet)}'

            if len(setFirst) > 0:
                currentNextSet.extend(setFirst)
                currentNextSet = list(set(currentNextSet))

            aStep.explanation += f'\nEntonces SELECCION({self.__productionList.index(aProduction)}) =  {self.printFirstSymbols(currentNextSet)}'
            nextExplanation.append(aStep)



        else:
            aStep = ExplanationStep()
            aStep.setAProduction(aProduction)
            aStep.setFirst(setFirst)
            aStep.explanation = f'Como el lado derecho de la producción NO es anulable no es necesario obtener el conjunto SIGUIENTE de {aProduction.getLeftSide()}.'
            aStep.explanation += f'\nConcluye, conjunto SELECCION({self.__productionList.index(aProduction)}) =  {FIRSTW}{self.printFirstSymbols(aProduction.getRightSide(), True)}'
            aStep.explanation += f'\n{FIRSTW}{self.printFirstSymbols(aProduction.getRightSide(), True)} =  {self.printFirstSymbols(setFirst)}'
            aStep.explanation += f'\nEntonces SELECCION({self.__productionList.index(aProduction)}) =  {self.printFirstSymbols(setFirst)}'
            nextExplanation.append(aStep)

            introStep.explanation = f'Para obtener el conjunto SELECCION de {aProduction}, se necesita obtener el conjunto PRIMERO de {self.printFirstSymbols(aProduction.getRightSide(),True)}.'
        
        introExplanation.append(introStep)

        return introExplanation, firstExplanation, nextExplanation
        
    def explainSymbol(self, symbol):
        if symbol.getStype() == TM:
            return f"el símbolo terminal ( {symbol.getTag()} )"
        return f"el símbolo NO terminal ( {symbol.getTag()} )"
    
    def printFirstSymbols(self, symbols, spaces = False):
        if symbols is not None and len(symbols) > 0:
            if spaces:
                result = '( '
                for symbol in symbols:
                    result += f"{symbol} "
                result =  result[:-1]+' )'
                return result
            else:
                result = '( '
                for symbol in symbols:
                    result += f"{symbol}, "
                result =  result[:-2]+' )'
        else: result = ''
        return result

    def explainedFirst(self, symbol, setFirst, looked, nVoidableNtList, explanation, ntFlag=False, aProduction = None):
        """
        NO defined
        """
        if aProduction:

            aStep = ExplanationStep()

            aStep.explanation = f"{FIRSTW}{self.printFirstSymbols(aProduction.getRightSide(), True)}"

            aStep.explanation += "\n\nSe analiza el lado derecho de la producción: "
            subSetFirst = []
            if aProduction.getRightSide():
                for aSymbol in aProduction.getRightSide():
                    if len(subSetFirst) == 0:
                        aStep.explanation += "\nEn este caso el primer elemento es "
                    else:
                        aStep.explanation = "El siguiente elemento es "
                    if aSymbol in setFirst or aSymbol in looked:
                        aStep.explanation += f"{self.explainSymbol(aSymbol)}, pero como este ya existe en el conjunto PRIMERO no se agrega, "
                    else:
                        if aSymbol.getStype() == NT: ntFlag = True
                        aStep.explanation += f"{self.explainSymbol(aSymbol)} el cual se agrega al conjunto PRIMERO."
                        subSetFirst.append(aSymbol)

                    aStep.setAProduction(aProduction)
                    aStep.setFirst(subSetFirst)
                    aStep.selectedInProduction = aProduction.getRightSide().index(aSymbol)
                    explanation.append(aStep)

                    if aSymbol not in nVoidableNtList:
                        aStep.explanation += f"\nComo {aSymbol.getTag()} NO es un símbolo anulable, el análisis termina aquí."
                        break
                    else:
                        aStep.explanation += f"\nComo {aSymbol.getTag()} es un símbolo anulable, se toma en cuenta el siguiente simbolo."
                        aStep = ExplanationStep()           

            else:
                aStep.setAProduction(aProduction)
                aStep.explanation += "\nComo el lado derecho de la producción es vacío(nulo), el conjunto PRIMERO de esta tambien es vacio"
                explanation.append(aStep)
            return (subSetFirst, explanation, ntFlag)
        else:
            
            
            index = 0
            postExplanation = []
            subSetFirst = setFirst.copy()
            prevStep = ExplanationStep()
            prevStep.explanation = f'Para {self.explainSymbol(symbol)} se busca las producciones en que este esté del lado izquierdo, como:'
            prevStep.setFirst(setFirst)
            prevStep.selectedInFirst = [setFirst.index(symbol)]
            for production in self.getProductionList():

                if production.getLeftSide() == symbol:

                    prevStep.explanation += f"\nProducción {index}: {production}"
                    
                    aStep = ExplanationStep()
                    aStep.explanation = f"En la producción {index} "
                    if production.getRightSide():
                        firstElement = True
                        for aSymbol in production.getRightSide():

                            if firstElement:
                                aStep.explanation += "el primer elemento es "
                                firstElement = False

                            else:
                                aStep.explanation = "El siguiente elemento es "

                            if aSymbol in setFirst or aSymbol in looked:
                                aStep.explanation += f"{self.explainSymbol(aSymbol)}, pero como este ya existe en el conjunto PRIMERO no se agrega, "
                            else:
                                if aSymbol.getStype() == NT: ntFlag = True
                                aStep.explanation += f"{self.explainSymbol(aSymbol)} el cual se agrega al conjunto PRIMERO."
                                subSetFirst.append(aSymbol)
                            
                            aStep.setAProduction(production)
                            aStep.setFirst(subSetFirst)
                            aStep.selectedInProduction = production.getRightSide().index(aSymbol)
                            aStep.selectedInFirst = [setFirst.index(symbol)]
                            postExplanation.append(aStep)

                            if aSymbol not in nVoidableNtList:
                                aStep.explanation += f"\nComo {aSymbol.getTag()} NO es un símbolo anulable, el análisis termina aquí."
                                break
                            else:
                                aStep.explanation += f"\nComo {aSymbol.getTag()} es un símbolo anulable, se toma en cuenta el siguiente simbolo."
                                aStep = ExplanationStep()           

                    else:

                        aStep.explanation += "el lado derecho de la producción es vacío(nulo) entonces el conjunto PRIMERO de esta tambien es vacio"
                        aStep.setAProduction(production)
                        aStep.setFirst(subSetFirst)
                        aStep.selectedInFirst = [setFirst.index(symbol)]
                        postExplanation.append(aStep)
                    index += 1
            # AGREGAR A ULTIMO ELEMENTO EN postExplanation... algo sobre eliminar el NO terminal recorrido
            # AGREGAR CONSIDERACION PARA CUANDO UN NT YA SE RECORRIO
            prevStep.explanation += f"\n\nCon lo que obtendremos el conjunto {symbol.getTag()}"
            explanation.append(prevStep)
            explanation.extend(postExplanation)
            subSetFirst.remove(symbol)
            return (subSetFirst, explanation, ntFlag)

    def explainedNext(self, symbol, production, index, nVoidableNtList, fNextSet, looked, currentNextSet, currentNextSymbol):
        """
        NO defined
        """
        # PONER ANTES EL INDICE DE LA PRODUCCION
        # VER COMO COMTROLAR SI YA SE RECORRIO O NO UN PRIMERO SIGUIENTE
        # VER COMO CAMBIAR EL NOMBRE DEL CONJUNTO
        # PUEDO AGREGAR ALGO QUE DIGA, QUE LOS SIGUIENTES Y PRIMEROS SE AGREGAN AL CONJUNTO SIGUIENTE

        nextSets = []
        firstSets = []

        #currentNextSet = [] #POSIBLE GLOBAl

        subExplanation = []
        nStep = ExplanationStep()
        nStep.setAProduction(production)
        if production.getRightSide() is not None:
            nStep.selectedInProduction = production.getRightSide().index(symbol)

        #if len(currentNextSet) > 0:
        #    nStep.setFirst(currentNextSet)
            #nStep.selectedInFirst = [currentNextSet.index(f'{NEXTW}({symbol})')]

        nStep.explanation = f'En la producción {index}:'

        if production.getRightSide() is not None and production.getRightSide().index(symbol) == len(production.getRightSide()) -1:
            
            
            nStep.explanation += f'Como {self.explainSymbol(symbol)} esta al final de la producción entonces:'
            nStep.explanation += f'\n{NEXTW}({symbol}) = {NEXTW}({production.getLeftSide()})'
            
            if f'{NEXTW}({production.getLeftSide()}' in looked:
                # YA FUE RECORRIDO EL SIGUIENTE
                nStep.explanation += f'\n\nPero como {NEXTW}({production.getLeftSide()}) ya fue obtenido, no se tiene en cuenta en este caso.'
            elif currentNextSymbol == production.getLeftSide():
                    nStep.explanation += f'\n\nComo {NEXTW}({production.getLeftSide()}) es el conjunto {NEXTW} que ya se esta obteniendo, no se toma en cuenta.'
            else:
                # NO HA SIDO RECORRIDO
                looked.append(f'{NEXTW}({production.getLeftSide()})')
                nextSets.append(production.getLeftSide())
                currentNextSet.append(f'{NEXTW}({production.getLeftSide()})')

            nStep.setFirst(currentNextSet)

        else:
            if production.getRightSide() is not None:
                nextSymbols = production.getRightSide()[production.getRightSide().index(symbol)+1:]
                if all(symbol in nVoidableNtList for symbol in nextSymbols):
                    # ANULABLE PRIMERO(b) U SIGUIENTE(A)
                    
                    #nStep.firstset = [f'{NEXTW}({production.getLeftSide()}) U {FIRSTW}{self.printFirstSymbols(nextSymbols, True)}']
                    nStep.explanation += f'Como los símbolos despues de {self.explainSymbol(symbol)} son TODOS anulables:'
                    nStep.explanation += f'\n{NEXTW}({symbol}) = {NEXTW}({production.getLeftSide()}) U {FIRSTW}{self.printFirstSymbols(nextSymbols, True)}'
            
                    
                    if f'{NEXTW}({production.getLeftSide()}' in looked:
                        # YA FUE RECORRIDO EL SIGUIENTE
                        nStep.explanation += f'\n\nComo {NEXTW}({production.getLeftSide()}) ya fue obtenido, no se tiene en cuenta en este caso.'
                    elif currentNextSymbol == production.getLeftSide():
                        nStep.explanation += f'\n\nComo {NEXTW}({production.getLeftSide()}) es el conjunto {NEXTW} que ya se esta obteniendo, no se toma en cuenta.'
                    else:
                        # NO HA SIDO RECORRIDO
                        looked.append(f'{NEXTW}({production.getLeftSide()})')
                        nextSets.append(production.getLeftSide())
                        currentNextSet.append(f'{NEXTW}({production.getLeftSide()})')

                    if f'{FIRSTW}{self.printFirstSymbols(nextSymbols, True)}' in looked:
                        # YA FUE RECORRIDO EL SIGUIENTE
                        nStep.explanation += f'\n\nComo {FIRSTW}{self.printFirstSymbols(nextSymbols, True)} ya fue obtenido, no se tiene en cuenta en este caso.'
                    else:
                        # NO HA SIDO RECORRIDO
                        looked.append(f'{FIRSTW}{self.printFirstSymbols(nextSymbols, True)}')
                        firstSets.append(nextSymbols)
                        currentNextSet.append(f'{FIRSTW}{self.printFirstSymbols(nextSymbols, True)}')

                    nStep.setFirst(currentNextSet)
                    

                else:
                    # SIGUIENTE(B) = PRIMERO(b)
                    
                    nStep.explanation += f'Como los símbolos despues de {self.explainSymbol(symbol)} NO son todos anulables:'
                    nStep.explanation += f'\n{NEXTW}({symbol}) = {FIRSTW}{self.printFirstSymbols(nextSymbols, True)}'

                    if f'{FIRSTW}{self.printFirstSymbols(nextSymbols, True)}' in looked:
                        # YA FUE RECORRIDO EL SIGUIENTE
                        nStep.explanation += f'\n\nComo {FIRSTW}{self.printFirstSymbols(nextSymbols, True)} ya fue obtenido, no se tiene en cuenta en este caso.'
                    else:
                        # NO HA SIDO RECORRIDO
                        looked.append(f'{FIRSTW}{self.printFirstSymbols(nextSymbols, True)}')
                        firstSets.append(nextSymbols)
                        currentNextSet.append(f'{FIRSTW}{self.printFirstSymbols(nextSymbols, True)}')

                    nStep.setFirst(currentNextSet)

        subExplanation.append(nStep)

        if len(firstSets) > 0:
            # CALCULAR PRIMEROS
            # AGREGAR TEXTO DE PARA CALCULAR PRIMERO DE...
            nStep = ExplanationStep()
            nStep.explanation = f"Para obtener {FIRSTW}{self.printFirstSymbols(nextSymbols, True)} se analiza los símbolos: "
            nStep.selectedInFirst = [currentNextSet.index(f'{FIRSTW}{self.printFirstSymbols(nextSymbols, True)}')]
            #subSetFirst = []
            subSetFirst = currentNextSet
            ntFlag = False
            firstElement = True

            for aSymbol in firstSets[-1]:

                if firstElement:
                    firstElement = False
                    nStep.explanation += "\nEl primer elemento es "
                else:
                    nStep.explanation = "El siguiente elemento es "
                if aSymbol in looked:                    
                    nStep.explanation += f"{self.explainSymbol(aSymbol)}, pero como este ya fue obtenido, no se agrega, "
                elif aSymbol in fNextSet:
                    nStep.explanation += f"{self.explainSymbol(aSymbol)}, pero como este ya existe en el conjunto SIGUIENTE no se agrega, "
                else:
                    if aSymbol.getStype() == NT: ntFlag = True
                    nStep.explanation += f"{self.explainSymbol(aSymbol)} el cual se agrega al conjunto SIGUIENTE."
                    subSetFirst.append(aSymbol)

                nStep.setAProduction(firstSets[-1], True)
                nStep.setFirst(subSetFirst)
                nStep.selectedInProduction = firstSets[-1].index(aSymbol)
                subExplanation.append(nStep)

                #if firstSets[-1].index(aSymbol) == len(firstSets[-1])-1:
                #    nStep.explanation += f"\nComo {aSymbol.getTag()} es el ultimo símbolo el análisis termina aquí."
                #    break

                if aSymbol not in nVoidableNtList:
                    nStep.explanation += f"\nComo {aSymbol.getTag()} NO es un símbolo anulable, el análisis termina aquí."
                    break
                else:    
                    nStep.explanation += f"\nComo {aSymbol.getTag()} es un símbolo anulable, se toma en cuenta el siguiente simbolo."
                    
                    if firstSets[-1].index(aSymbol) != len(firstSets[-1])-1:    nStep = ExplanationStep()
            
            # AQUI PODRIA PONER QUE SE QUITA EL SIMBOLO PRIMERO DEL CONJUNTO
            currentNextSet.remove(f'{FIRSTW}{self.printFirstSymbols(nextSymbols, True)}')
            nStep.explanation += f"\nCon los elementos iniciales de {FIRSTW}{self.printFirstSymbols(nextSymbols, True)} podemos eliminarlo de SIGUIENTE"

            
            while (ntFlag):
                nStep = ExplanationStep()
                nStep.explanation = "Terminado el análisis se revisa el conjunto resultante:"
                
                selectInFirst = []
                ntString = "( "
                ntCounter = 0
                for aSymbol in subSetFirst:
                    if type(aSymbol) is Symbol:
                        if  aSymbol.getStype() == NT:
                            ntString += f"{aSymbol}, "
                            ntCounter += 1
                            selectInFirst.append(subSetFirst.index(aSymbol))
                ntString = ntString[:-2]+" )"

                if ntCounter == 1: nStep.explanation += f"\nEn este caso existe un símbolo NO terminal {ntString}"
                else: nStep.explanation += f"\nEn este caso existen símbolos NO terminales {ntString}"
                
                nStep.explanation += f" dentro del conjunto, así que para obtener el conjunto SIGUIENTE es necesario obtener el conjunto PRIMERO de {ntString}, y reemplazarlo."
                nStep.selectedInFirst = selectInFirst
                nStep.setFirst(subSetFirst)
                
                subExplanation.append(nStep)

                ntFlag = False

                newFirst = subSetFirst.copy()

                for aSymbol in subSetFirst:
                    #aStep = ExplanationStep()
                    if aSymbol not in looked:
                        looked.append(aSymbol)

                        if aSymbol.getStype() == TM:  continue

                        newFirst, subExplanation, ntFlag = self.explainedFirst(aSymbol, newFirst, looked, nVoidableNtList, subExplanation, ntFlag)
                        
                # Despues de cada for podria agregarse un Paso?

                subSetFirst = newFirst
            # AGREGAR PASOS DE FINALIZACION
            currentNextSet = subSetFirst

        if len(nextSets) > 0:
            # CALCULAR SIGUIENTES DE...
            for aSymbol in nextSets:
                
                nStep = ExplanationStep()
                nStep.explanation = f"Para obtener {NEXTW}({aSymbol})"
                nStep.explanation += f' se requiere analizar todas las producciones que contenga al símbolo {aSymbol} del lado derecho, como:'
                nStep.setFirst(currentNextSet)
                nStep.selectedInFirst = [currentNextSet.index(f'{NEXTW}({aSymbol})')]

                nIndex = 0
                #nPostSteps = []
                nPostSteps = []
                newPS = None
                for nProduction in self.__productionList:

                    if nProduction.getRightSide() is not None and aSymbol in nProduction.getRightSide():
                        nStep.explanation += f'\n\nProducción {nIndex}: {nProduction}'
                        # AQUI DEBE PASAR ANALISIS
                        newPS, looked, currentNextSet = self.explainedNext(aSymbol, nProduction, nIndex, nVoidableNtList, fNextSet, looked, currentNextSet, currentNextSymbol)
                        #nextProductions.append(production)
                        nPostSteps.extend(newPS)
                    
                    nIndex += 1

                subExplanation.append(nStep)
                subExplanation.extend(nPostSteps)
                currentNextSet.remove(f'{NEXTW}({aSymbol})')
                if aSymbol == self.getInitialNt():
                    nStep.explanation += f'\n\nYa que {aSymbol} es el no terminal inicial, a su conjunto {NEXTW} se agrega el simbolo FIN de cadena.'
                    currentNextSet.append(EOC)

            # MENSAJE DE INTERCAMBIO
            nStep = ExplanationStep()
            nStep.explanation = f"Fin de {NEXTW}({aSymbol})"
            nStep.setFirst(currentNextSet)
            subExplanation.append(nStep)


        return subExplanation, looked, currentNextSet

    def explainedCodeProduction(self, index):
        """
        Explains how to codify the given production in the Syntactic Module
        
        Parameters
        ----------
        index : int
            Position of the production to be explained

        Returns
        -------
        A String with the explanation
        """
        tab = '    '
        aProduction = self.__productionList[index]
        explanation = ''
        
        # 1. Zona de análisis
        explanation = 'Para empezar se agrega en la zona de análisis sintáctico, un condicional(if o switch) para el "tope de pila"'
        explanation += ' e interno a este otro para la cabecera(puntero) en la cadena analizada, comparados con el lado izquierdo de '
        explanation += 'la producción analizada y su conjunto selección respectivamente. Asi:'

        explanation += f'\n\n#CONDICIONAL PILA CON LADO IZQ. DE PRODUCCIÓN'
        explanation += f'\nif (stack[-1] == "{aProduction.getLeftSide()}"):'
        explanation += f'\n{tab}#CONDICIONAL CABECERA CON CONJUNTO SELECCIÓN'
        explanation += f'\n{tab}if(mainChar[head].token in "{aProduction.getSelectionSet()}"):'
        explanation += f'\n{tab}{tab}head = self.production{index}(stack, head)'
        explanation += f'\n{tab}else:'
        explanation += f'\n{tab}{tab}#SECUENCIA DE ERROR POR DEFECTO'
        explanation += f'\n{tab}{tab}message = self.notifyError(stack[-1], mainChar[head].token)'
        explanation += f'\n{tab}{tab}return (False, message, mainChar[head].position)'

        explanation += f'\n\nDonde: \n\nstack : es la variable con la que se controla la pila, y la posición [-1], indica el elemento en tope.'
        explanation += f'\n\nmainChar : es la variable que contiene la cadena analizada.'
        explanation += f'\n\nhead : es la variable con la posición del elemento bajo analisis(cabecera o puntero).'

        explanation += f'\n\nEl código indica que si el tope de la pila es {aProduction.getLeftSide()} y en la cabecera'
        explanation += f' de la cadena analizada se encuentra un elemento del conjunto SELECCION de la producción el proceso a desempeñar será'
        explanation += f'el definido por el método "production{index}()", de lo contrario se ejecutara la secuencia de rechazo.'


        # 2. Produccion
        explanation += f'\n\nEn caso de continuar la secuencia correcta se agrega en la zona de Producciones la definición de la producción {index} así:'

        explanation += f'\n\ndef production{index}(self, stack, head):'
        explanation += f"\n{tab}#INSTRUCCIÓN POP"
        explanation += f'\n{tab}stack.pop()'

        prodExp = ''
        if aProduction.getRightSide() is not None and len(aProduction.getRightSide())>0:
            first = aProduction.getRightSide()[0]

            prodExp += f'\n\nComo el lado derecho de la producción empieza por {self.explainSymbol(first)}, '


            explanation += f"\n{tab}#INSTRUCCIONES DE REEMPLAZO"
            for symbol in reversed(aProduction.getRightSide()[1:]):
                explanation += f"\n{tab}stack.append('{symbol.getTag()}')"
                
            if first.getStype() == NT:
                if len(aProduction.getRightSide())>1:
                    prodExp += f'se toma todos los símbolos del lado derecho de la producción y se ingresan en orden inverso a la pila(append)'
                else:
                    prodExp += f'como es el único símbolo en el lado derecho de la producción se ingresa directamente a la pila(append).'
                explanation += f"\n{tab}stack.append('{first.getTag()}')"
                prodExp += f'\nComo el primer símbolo es NO terminal, la cabecera(head) se retorna sin cambio alguno, lo que emula el proceso de retiene.'
                explanation += f'\n{tab}#RETIENE'
                explanation += f'\n{tab}return head'

            else:
                prodExp += f'este NO se toma en cuenta'
                if len(aProduction.getRightSide())>1:
                    prodExp += f'y se toma los símbolos siguientes a {first}  y se ingresan en orden inverso a la pila(append).'
                else:
                    prodExp += f'como no hay mas simbolos, no se agrega nada a la pila.'
                prodExp += f'\nComo el primer símbolo es terminal, la cabecera(head) se retorna adicionando 1, lo que indica que la cabecera avanza en la cadena analizada.'
                
                explanation += f'\n{tab}#AVANZA'
                explanation += f'\n{tab}return head + 1'
            
        else:
            prodExp += f'\nComo el lado derecho de la producción es nulo, no se agrega símbolos a pila o modifica la variable cabecera(head).'
            explanation += f'\n{tab}return head'
        
        explanation += prodExp

        return explanation

    def explainedCodeError(self, x, y):
        """
        Explains how to codify the given error in the Syntactic Module
        
        Parameters
        ----------
        x : int
            Position of the error related to row
        y : int
            Position of the error related to column

        Returns
        -------
        A String with the explanation of the code
        """
        tab = '    '
        nIndexRow, nIndexCol = self.getControlMatrixIndex(True)

        rowk = colk = None
        for row in nIndexRow.keys():
            if nIndexRow[row] == x:
                rowk = row
                break
        for col in nIndexCol.keys():
            if nIndexCol[col] == y:
                colk = col
                break

        message = self.getErrorMessage(x, y)
        if message is None:
            message = f'Se econtro "+headChar+" y se esperaba {self.getAwaitedSets(rowk)}'
        
        if rowk and colk:
            explanation = 'Para obtener el mensaje de error dentro de la secuencia de rechazo, se agrega un condicional'
            explanation += ' que involucra el símbolo en el tope de la pila y otro para el elemento en la cabecera(puntero) de la cadena analizada'
            explanation += '.\nIndicando que el mensaje es específico para esa situación.'

            explanation += f'\n\n#CONDICIONAL TOPE DE PILA'
            explanation += f'\nif (stackTop == "{rowk}"):'
            explanation += f'\n#CONDICIONAL CABECERA EN CADENA'
            explanation += f'\n{tab}if(headChar == "{colk}"):'
            explanation += f'\n{tab}{tab}message = "{message}"'
            explanation += f'\n{tab}return message'

            explanation += '\n\nTome en cuenta que el metodo para obtener el mensaje de error dentro del código a generar'
            explanation += ' se denomina " notifyError(stackTop, headChar) ", donde:'
            explanation += '\n\nstackTop : Es la variable que controla el tope de la pila'
            explanation += '\n\nheadChar : Es la variable con el elemento en la cabecera de la cadena analizada'
            explanation += '\n\nSe define en la variable "message" el mensaje de error y se retorna.'

        return explanation

    def generateSaveData(self):
        """
        Builsd a JSON structure of the current Nonterminal symbols list, Productions Definition 
        and user errors definition
        """
        # POSIBLEMENTE TAMBIEN SE INDIQUE EL NT INICIAL
        ntSymbols = []
        productions = []
        errorsDictionary = []

        if len(self.__ntsymbolList) > 0:

            for symbol in self.__ntsymbolList:
                ntSymbols.append({
                    "tag": symbol.getTag()
                })

        if len(self.__productionList) > 0:
            for production in self.__productionList:
                rightSide = []
                if production.getRightSide() is not None:
                    for symbol in production.getRightSide():
                        rightSide.append(symbol.getTag())
                
                leftSide = production.getLeftSide().getTag() if production.getLeftSide() is not None else None
                productions.append({
                    "leftSide": leftSide,
                    "rightSide": rightSide
                })
        
        if len(self.errorsDictionary) > 0:
             
            for stackSymbol in self.errorsDictionary.keys():
                charSymbols = []
                for symbol in self.errorsDictionary[stackSymbol].keys():
                    charSymbols.append({
                        'symbol': symbol,
                        'message': self.errorsDictionary[stackSymbol][symbol]
                    })

                errorsDictionary.append({
                    "stackSymbol": stackSymbol,
                    "charSymbols": charSymbols

                })

        syntactic = {
            "module": "syntactic",
            "ntSymbols": ntSymbols,
            "productions": productions,
            "errorsDictionary": errorsDictionary
        }

        return syntactic

    def loadSyntacticData(self, syntactic):
        """
        Mount a JSON structure into the Symbols List and the productions of the project

        Parameters
        ----------
        syntactic : Json structure
            Json structure to mount into the Syntactic Module
        """
        # Ver como cargar nt inicial
        ntSymbols = syntactic.get("ntSymbols")
        productions = syntactic.get("productions")
        errorsDictionary = syntactic.get("errorsDictionary")

        self.__ntsymbolList = []
        self.__productionList = []
        self.__initialnt = None
        self.errorsDictionary = {}
        
        for symbol in ntSymbols:
            self.__ntsymbolList.append( Symbol(symbol.get('tag'), NT) )

        for production in productions:
            leftSide = production.get('leftSide')
            nSymbol = Symbol(leftSide, NT) if leftSide is not None else None
            newProduction = Production( nSymbol )
            newRightSide = []
            if production.get('rightSide'):
                for symbol in production.get('rightSide'):
                    newsymbol = self.findTMsymbol(symbol)
                    if not newsymbol: newsymbol = self.findNTsymbol(symbol)
                    newRightSide.append(newsymbol)
            newProduction.setRightSide(newRightSide)
            self.__productionList.append(newProduction)
        
        for stackSymbol in errorsDictionary:
            rowk = stackSymbol.get("stackSymbol")
            self.errorsDictionary[rowk] = {}
            for symbol in stackSymbol.get("charSymbols"):
                colk = symbol.get("symbol")
                self.errorsDictionary[rowk][colk] = symbol.get("message")         

