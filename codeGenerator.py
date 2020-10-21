"""
ESQUEMA A SEGUIR  
  Se trabaja con 3 archivos sobreescritos
  main.py :
    conecta el modulo lexico y sintacticos generados
    ademas recibe las cadenas de reconocimiento y se 
    comunica con el usuario.

  lexicon.py:
    realiza reconocimiento lexico, recibe cadena cruda y la transforma en
    elementos token reconocidos, que se devuelven al main

  syntactic.py
    recibe una cadena de tokens reconocidos por parte del main y 
    realiza el analisis sintactico.

Pasos para generacion de codigo:
    1. Obtencion de elementos de modulos lexico y sintactico
        a. de lexico se obtienen los tokens
        b. de sintactico se obtienen los simbolos y producciones y errores

    2. Creacion modulo lexico

    3. Creacion modulo sintactico

    4. configuracion de main
"""
from lexic import *
from syntactic import *
import os
from const import *
#------------------------------------------------------------------------------------------
# RUTAS A PLANTILLAS DE CÓDIGO
LEXICONTEMPLATEROUTE = 'templates/lexicontemplate.py'
SYNTACTICTEMPLATEROUTE = 'templates/syntactictemplate.py'
MAINTEMPLATEROUTE1 = 'templates/maintemplate_lex.py'
MAINTEMPLATEROUTE2 = 'templates/maintemplate_full.py'
WINDOWMAINTEMPLATEROUTE1 = 'templates/windowmaintemplate_lex.py'
WINDOWMAINTEMPLATEROUTE2 = 'templates/windowmaintemplate_full.py'

# IDENTIFICADORES DE PUNTOS DE INSERCIÓN DE CÓDIGO
LEXTOKENS = '#{(RECONOCIMIENTO-TOKENS)}\n'
SYNTAXINITIALNT = '#{(NTINICIAL-SINTÁCTICO)}\n'
SYNTAXRECO = '#{(RECONOCIMIENTO-SINTÁCTICO)}\n'
SYNTAXPROD = '#{(PRODUCCIONES-SINTÁCTICO)}\n'
SYNTAXERROR = '#{(ERRORES-SINTÁCTICO)}\n'

class CodeGenerator:
    """
        Documentación del generador de codigo.
    """

    def __init__(self, path, name, lexiconModule, syntacticModule):
        self.projectStatus = PSTATUS0
        self.mountLexicon(lexiconModule)
        self.mountSyntactic(syntacticModule)
        self.generateProjectCode()
        self.projectPath = f'{path}/{name}'
        
        
        #self.buildProject(projectPath)
        

    def buildProject(self, window = False):
        if self.projectStatus != PSTATUS0:
            self.writeProjectFile(self.projectPath, window)
        else: return (False, self.projectStatus)
        if self.projectStatus == PSTATUS1 or self.projectStatus == PSTATUS2:    
            self.writeLexiconFile(self.projectPath)
            if self.projectStatus == PSTATUS2:
                self.writeSyntacticFile(self.projectPath)
            return (True, self.projectStatus)
        else: return (False, self.projectStatus)


    def mountLexicon(self, lexiconModule = None):
        #DEFINICION TEMPORAL POR PRUEBAS
        self.lexiconCode = ''
        if len(lexiconModule.getTokenList()) > 0:
            tokenlist = []
            for token in lexiconModule.getTokenList():
                if token.getTypeExp() == 0:
                    tToken = Token(token.getName(),token.getTypeExp(), lexiconModule.convertInput(token.getRegularExp(),token.getTypeExp()))
                else:
                    tToken = token
                tokenlist.append(tToken)

            # GENERACION DE CODIGO(MOVER A OTRA FUNCION)
            self.generateLexiconCode(tokenlist)
            
            
    def mountSyntactic(self, syntacticModule = None):
        # CAMBIOS PARA SYNTAX
        # AGREGAR METODO GET CONTROL MATRIX, y linkear a self
        self.syntacticCodept1 = ''
        self.syntacticCodept2 = ''
        self.syntacticCodept3 = ''
        self.syntacticCodept4 = ''

        if (self.projectStatus != PSTATUS0 and len(syntacticModule.getNTSymbolList()) > 0 and
            len(syntacticModule.getProductionList()) > 1 ):

            syntacticModule.setInitialNt(syntacticModule.getNTSymbolList()[0])

            status, result = syntacticModule.validateGrammar()
            if status != GV_OK: return

            status = syntacticModule.generateSelectionSets()
            if status != GV_OK: return

            status, ambigusProductions = syntacticModule.validateAmbiguity()
            if status != GV_OK: return

        
            # AQUI PODRIA VALIDAR LA GRAMATICA OTRA VEZ PARA EVITAR CODIGO DE GRAMATICAS MAL
            initialNt = syntacticModule.getInitialNt()
            controlMatrix = syntacticModule.getControlMatrix()
            nIndexRow, nIndexCol = syntacticModule.getControlMatrixIndex()
            productionList = syntacticModule.getProductionList()
            # GENERACIÓN DE CÓDIGO
            self.generateSyntacticCode(initialNt, controlMatrix, nIndexRow, nIndexCol, productionList)

            nIndexRow, nIndexCol = syntacticModule.getControlMatrixIndex(True)
            self.generateErrorsCode(nIndexRow, nIndexCol, controlMatrix, syntacticModule)

        
    def generateLexiconCode(self, tokenlist):
        NL = '\n'

        condition = f'if (re.match("{tokenlist[0].getRegularExp()}",mainChar)):'
        matched = f'matched = re.match("{tokenlist[0].getRegularExp()}",mainChar).span(0)[1]'
        if tokenlist[0].getTypeExp() == 1: tokenName = f'tokenName = "{tokenlist[0].getName()}:"+mainChar[:matched]'
        else: tokenName = f'tokenName = "{tokenlist[0].getName()}"'
        self.lexiconCode += TAB2 + condition + NL
        self.lexiconCode += TAB3 + matched + NL
        self.lexiconCode += TAB3 + tokenName + NL + NL

        for token in tokenlist[1:]:
            condition = f'elif (re.match("{token.getRegularExp()}",mainChar)):'
            matched = f'matched = re.match("{token.getRegularExp()}",mainChar).span(0)[1]'
            if token.getTypeExp() == 1: tokenName = f'tokenName = "{token.getName()}:"+mainChar[:matched]'
            else: tokenName = f'tokenName = "{token.getName()}"'
            self.lexiconCode += TAB2 + condition + NL
            self.lexiconCode += TAB3 + matched + NL
            self.lexiconCode += TAB3 + tokenName + NL + NL
        
        self.projectStatus = PSTATUS1

    def generateSyntacticCode(self, initialNt, controlMatrix, nIndexRow, nIndexCol, productionList):
        # No terminal inicial
        self.syntacticCodept1 = f'{TAB2}stack.append("{initialNt.getTag()}")'

        # Reconocimiento
        # TRADUCCIÓN TABLA DE CONTROL
        self.syntacticCodept2 = ''
        # PRIMER MANUAL
        first = True
        # SIGUIENTES
        for row in nIndexRow.keys():
            conditionStack = f'if (stack[-1] == "{row}"):' if first  else f'elif (stack[-1] == "{row}"):'
            first = False
            conditionsMainChar = ''
            first = True
            for col in nIndexCol.keys():
                if (controlMatrix[nIndexRow[row]][nIndexCol[col]] != -1):
                    # FORMA SIN OPTIMIZAR
                    condition = TAB2 + TAB2 +'if' if first else TAB2 + TAB2 +'elif'
                    condition += f'(mainChar[head].token == "{col}"):'
                    if (controlMatrix[nIndexRow[row]][nIndexCol[col]] == -3):
                        production = TAB2 + TAB3 +f'head = self.productionPA(stack, head)'
                    else:
                        index = int(controlMatrix[nIndexRow[row]][nIndexCol[col]])
                        production = TAB2 + TAB3 + f'head = self.production{index}(stack, head)'
                    conditionsMainChar += condition + NL+ production + NL+ NL
                    first = False
            
            errorOption = TAB2 + TAB2 + 'else:' + NL
            errorOption += TAB2 + TAB3 + 'message = self.notifyError(stack[-1], mainChar[head].token, mainChar[head].position)' + NL
            errorOption += TAB2 + TAB3 + 'return (False, message, mainChar[head].position)' + NL
            conditionsMainChar += errorOption + NL+ NL
            self.syntacticCodept2 += TAB3 + conditionStack + NL+ conditionsMainChar
        
        # PRODUCCIONES
        self.syntacticCodept3 = ''
        i = 1
        for production in productionList:
            definition = f'def production{i}(self, stack, head):'
            pop = 'stack.pop()'
            replace = ''
            if production.getRightSide():
                first = production.getRightSide()[0]
                for symbol in reversed(production.getRightSide()[1:]):
                    append = f"stack.append('{symbol.getTag()}')"
                    replace += TAB2 +append + NL
                if first.getStype() == NT: replace += TAB2 + f"stack.append('{first.getTag()}')" + NL
                sreturn = 'return head + 1' if first.getStype() == TM else 'return head'
            else:
                sreturn = 'return head'

            i += 1
            self.syntacticCodept3 +=  TAB + definition + NL
            self.syntacticCodept3 +=  TAB2 + pop + NL
            if replace != '':  self.syntacticCodept3 +=  replace + NL
            self.syntacticCodept3 +=  TAB2 + sreturn + NL+ NL
        
        # AGREGAR PRODUCCION PA
        definition = 'def productionPA(self, stack, head):'
        pop = 'stack.pop()'
        sreturn = 'return head + 1'
        
        self.syntacticCodept3 +=  TAB + definition + NL
        self.syntacticCodept3 +=  TAB2 + pop + NL
        self.syntacticCodept3 +=  TAB2 + sreturn + NL + NL
        self.projectStatus = PSTATUS2

        
    def generateErrorsCode(self, nIndexRow, nIndexCol, controlMatrix, syntaxModule):
        self.syntacticCodept4 = ''
        errorDictionary = syntaxModule.getErrorDictionary()
        # MENSAJES DE ERROR
        first = True
        for row in nIndexRow.keys():
            conditionStackTop = f'if (stackTop == "{row}"):' if first  else f'elif (stackTop == "{row}"):'
            first = False
            conditionsHeadChar = ''
            first = True
            for col in nIndexCol.keys():
                if (controlMatrix[nIndexRow[row]][nIndexCol[col]] == -1):
                    # FORMA SIN OPTIMIZAR
                    condition = TAB3 + 'if' if first else TAB3 + 'elif'
                    condition += f'(headChar == "{col}"):'
                    if row in errorDictionary and col in errorDictionary[row]:
                        message = TAB2 + TAB2 + 'message = "'+ errorDictionary[row][col] +'"'
                    else:
                        message = TAB2 + TAB2 + 'message = "Se encontró "+ headChar + " y se esperaba "'
                        message += '"' + str(syntaxModule.getAwaitedSets(row)) +'"'
                    conditionsHeadChar += condition + NL + message + NL + NL
                    first = False

            self.syntacticCodept4 += TAB2 + conditionStackTop + NL + conditionsHeadChar
        

    def generateProjectCode(self):
        # AQUI DEBE VERIFICARSE SI EL CÓDIGO FINAL FUNCIONARA COMPLETO O SOLO CONSINTACTICO
        if self.projectStatus == PSTATUS0:
            self.mainFileConsole = ''
            self.mainFileWindow = ''
        elif self.projectStatus == PSTATUS1:
            self.mainFileConsole = MAINTEMPLATEROUTE1
            self.mainFileWindow = WINDOWMAINTEMPLATEROUTE1
        elif self.projectStatus == PSTATUS2:
            self.mainFileConsole = MAINTEMPLATEROUTE2
            self.mainFileWindow = WINDOWMAINTEMPLATEROUTE2


    def writeLexiconFile(self, path):
        # TAL VEZ AGREGAR LEXICON.py a path
        with open(LEXICONTEMPLATEROUTE, encoding="utf8") as lexicontemplate:
            filelines = lexicontemplate.readlines()
            with open(path+'/lexicon.py', 'w+', encoding="utf8") as outfile:
                for line in filelines:
                    if(line == LEXTOKENS):
                        # AQUI SE ESCRIBE EL CODIGO DE LOS TOKEN
                        outfile.write(self.lexiconCode)
                    else:    
                        outfile.write(line)
                outfile.close()
            lexicontemplate.close()

    def writeSyntacticFile(self, path):
        # TAL VEZ AGREGAR SYNTACTIC.py a path
        with open(SYNTACTICTEMPLATEROUTE, encoding="utf8") as syntactictemplate:
            filelines = syntactictemplate.readlines()
            with open(path+'/syntactic.py', 'w+', encoding="utf8") as outfile:
                for line in filelines:
                    if(line == SYNTAXINITIALNT):
                        # AQUI SE ESCRIBE EL CODIGO DE NT INICIAL
                        outfile.write(self.syntacticCodept1)
                    elif(line == SYNTAXRECO):
                        # AQUI SE ESCRIBE EL CODIGO DE RECONOCIMIENTO
                        outfile.write(self.syntacticCodept2)

                    elif(line == SYNTAXPROD):
                        # AQUI SE ESCRIBE EL CODIGO DE PRODUCCIONES
                        outfile.write(self.syntacticCodept3)

                    elif(line == SYNTAXERROR):
                        # AQUI SE ESCRIBE EL CODIGO DE PRODUCCIONES
                        outfile.write(self.syntacticCodept4)
                    
                    else:    
                        outfile.write(line)
                outfile.close()
            syntactictemplate.close()

    def writeProjectFile(self, path, window = False):
        try:
            # Create target Directory
            os.mkdir(path)
            # CREACION DE CÓDIGOS
            # AQUI DEBERIA VERSE SI EL PROYECTO TIENE SINTACTICO O SOLO LEXICO
            curtemplate =  self.mainFileWindow if window else self.mainFileConsole
            with open(curtemplate, encoding="utf8") as maintemplate:
                filelines = maintemplate.readlines()
                with open(path+'/main.py', 'w+', encoding="utf8") as outfile:
                    for line in filelines:
                            outfile.write(line)
                    outfile.close()
                maintemplate.close()

        except FileExistsError:
            self.projectStatus = PSTATUS5