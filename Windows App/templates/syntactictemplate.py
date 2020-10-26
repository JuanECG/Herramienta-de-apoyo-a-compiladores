"""
Esta es la plantilla utilizada para la generacion de codigo
para el archivo (syntactic) modulo sintactico de TOOL
"""
# LOS IMPORTS SON TEMPORALES
# IMPORTS de modulos lexico y sintactico
from lexicon import Subtoken

# ANAIZADOR SINTÁCTICO
class Syntactic:

    def syntacticAnalysis(self, mainChar):
        
        # Agregar fin de cadena
        EOC = '¬'
        SB = '∇'
        if len(mainChar) > 0:
            steoc = Subtoken(EOC,EOC,(mainChar[-1].position[0], mainChar[-1].position[1]+1))
        else:
            steoc = Subtoken(EOC,EOC,(0,0))
        mainChar.append(steoc)

        stack = []
        head = 0
#{(NTINICIAL-SINTÁCTICO)}

        while(len(stack)!=0):
#{(RECONOCIMIENTO-SINTÁCTICO)}
        if mainChar[head].token == EOC:
            return (True, 'Secuencia aceptada', None)
        else:
            message = self.notifyError(SB, mainChar[head].token, mainChar[head].position)
            return (False, message, mainChar[head].position)

    
#{(PRODUCCIONES-SINTÁCTICO)}

    def notifyError(self, stackTop, headChar, errorPos):
        message = ''

#{(ERRORES-SINTÁCTICO)}

        if message == '':
            return 'Error sintáctico no definido'

        
        return f'Error sintáctico en fila {errorPos[0]} elemento {errorPos[1]}:\n{message}'
