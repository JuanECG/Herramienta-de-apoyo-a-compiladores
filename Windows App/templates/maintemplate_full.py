"""
Esta es la plantilla utilizada para la generación de código
para el archivo (main) principal de un proyecto de GADUN
"""

# IMPORTS de modulos lexico y sintactico
from lexicon import *
from syntactic import *

#CONSTANTS
LX_EXECUTION_ERROR = f'22 \nError en definición de Tokens'
SX_EXECUTION_ERROR = f'23 \nPosible error en definición de Producción'

class MainModule:
    def __init__(self):
        self.lexiconModule = Lexicon()
        self.syntacticModule = Syntactic()

    def lexiconAnalysis(self, userInput):
        status, result, lastPos = self.lexiconModule.lexiconAnalysis(userInput)

        if status:
            print("Cadena léxica valida")
        else:
            print(result)

        return status, result
    
    def syntacticAnalysis(self,inputChar):
        status, result, lastPosition = self.syntacticModule.syntacticAnalysis(inputChar)
        if status:
            print("Secuencia aceptada")
        else:
            print(result)
    
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

    def showMenu(self):

        while(True):
            print("Menún de Análizador Léxico-Sintáctico")
            print('1. Ingresar cadena para análisis léxico')
            print('2. Ingresar cadena para análisis sintáctico')
            print('3. Salir')
            opt = input("Ingrece su opción: ")
            if opt == '1':
                try:    status, result =  self.lexiconAnalysis(input("Ingrese la cadena a Análizar(Léxico): "))
                except:
                    print(LX_EXECUTION_ERROR)
                    break
                if status: print(self.parseResult(result))
            elif opt == '2':
                
                try:    status, result =  self.lexiconAnalysis(input("Ingrese la cadena a Análizar(Sintáctico): "))
                except:
                    print(LX_EXECUTION_ERROR)
                    break
                if status:
                    try:    self.syntacticAnalysis(result)
                    except:
                        print(SX_EXECUTION_ERROR)
                        break
            elif opt == '3':
                break
            else:
                print('Opción invalida...')
            print('\n\n')

if __name__ == "__main__":
    main = MainModule()
    main.showMenu()