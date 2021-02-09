"""
    Esta es la plantilla utilizada para la generación de código
    para el archivo (lexicon) módulo léxico de TOOL
"""
# IMPORT BIBLIOTECA REGEX
import re

# CLASE NECESARIA PARA LA CREACIÓN DE CADENA LÉXICA
class Subtoken:
    def __init__(self, token, value, position ):
        self.token  = token
        self.value = value
        self.position  = position

    def __str__(self):
        return self.token

# ANALIZADOR LEXÍCO
class Lexicon:
    def __init__(self):
        self.separators = [' ','\n', '\t']

    def lexiconAnalysis(self, inputString):
        """
            Realiza el analisis sintactico sobre una cadena de entrada

            Retorna una tuplacon con los valores:
                0 -- Boolean: False si la cadena ingresada presenta un error Lexico
                0 -- Boolean: True si la cadena ingresada NO presenta error Lexico

                1 -- String: Mensaje de error lexico
                1 -- Subtoken[]: Lista de subtokens reconocidos

            Parámetros:
                inputString -- cadena de entrada para ser analizada
        """
        mainChar = ""+inputString
        # curPos: Controla la posicion de los elementos reconocidos en formato(fila,columna)
        curPos = [1,1]
        # result: Lista de subtokens reconocidos
        result = []
        while (True):
            #CONTROL DE CADENA, determina si la cadena ha terminado de ser analisada
            if(not len(mainChar)>0):
                return (True, result, None)

            # OMICION DE SEPARADORES (espacio en blanco, salto de linea, TAB)
            if(mainChar[0] in self.separators):
                if mainChar[0] == '\n':
                    curPos[0] += 1
                    curPos[1] = 1
                    
                mainChar = mainChar[1:]
                continue

            # RECONOCIMIENTO DE SUB-TOKEN
            isOK, mainChar, curPos = self.tokensMatch(mainChar, result, curPos)

            # CONTROL DE ANALISIS, determina si se reconocio un token o se encontro un error
            if(not isOK):
                message = f'Error Léxico en fila {str(curPos[0])} elemento {str(curPos[1])}:\n'
                message +=  f" El elemento '{mainChar[0]}' no pertenece a los tokens definidos"
                return (False, message, curPos)

    def tokensMatch(self, mainChar, result, position):
        """
            Reconoce el elemento subtoken al inicio de una cadena, y lo extrae de la misma

            Retorna un vector con los valores:

                0 -- Boolean: False, si la cadena no empieza con un subtoken definido
                0 -- Boolean: True, si se reconocio un subtoken al inicio de la cadena

                1 -- cadena resultante despues de analisis

                2 -- int[]: Posicion del ultimo elemento reconocido en la cadena,
                            si el primer valor es False, indica la posicion del error lexíco
            
            Parámetros:
                mainChar: cadena para someter a reconocimiento
                result: lista de Subtokens reconocidos
                position: Posicion actual del analisis lexíco
        """

       # DEFINICION DE RECONOCIMIENTO (TOKENS DE USUARIO)
#{(RECONOCIMIENTO-TOKENS)}
        else:
            return (False, mainChar, position)

        result.append(Subtoken(tokenName, mainChar[:matched], position.copy()))
        position[1] += 1
        return (True, mainChar[matched:], position)