"""
Esta es la plantilla utilizada para la generación de código
para el archivo (syntactic) módulo sintáctico de TOOL
"""

# IMPORTS de modulos lexico y sintactico
from lexicon import Subtoken

# ANAIZADOR SINTÁCTICO
class Syntactic:

    def syntacticAnalysis(self, mainChar):
        """
            Realiza el análisis sintáctico sobre le secuencia entrante

            Retorna una tupla con los valores:
                0 -- Boolean: False, sí la cadena ingresada presenta un error Sintáctico
                0 -- Boolean: True, sí la cadena ingresada es aceptada

                1 -- String: Mensaje de error o aceptación

                2 -- Tupla: Posición en fila y columna del error sintáctico o None

            Parámetros:
                inputString -- cadena de entrada para ser analizada
        """
        
        EOC = '¬'   # Símbolo fin de cadena
        SB = '∇'    # Símbolo fondo de pila
        if len(mainChar) > 0:
            steoc = Subtoken(EOC,EOC,(mainChar[-1].position[0], mainChar[-1].position[1]+1))
        else:
            steoc = Subtoken(EOC,EOC,(0,0))
        mainChar.append(steoc)

        stack = []  # Pila para análisis
        head = 0    # Variable para control de cabecera en secuencia analizada 
#{(NTINICIAL-SINTÁCTICO)}

        # Ciclo para recorrido de secuencia
        while(len(stack)!=0):
#{(RECONOCIMIENTO-SINTÁCTICO)}
        if mainChar[head].token == EOC:
            return (True, 'Secuencia aceptada', None)
        else:
            message = self.notifyError(SB, mainChar[head].token, mainChar[head].position)
            return (False, message, mainChar[head].position)


    # LISTA DE PRODUCCIONES DEFINIDAS POR EL USUARIO    
#{(PRODUCCIONES-SINTÁCTICO)}

    # LISTA DE MENSAJES DE ERROR
    def notifyError(self, stackTop, headChar, errorPos):
        """
            Retorna el mensaje de error de acuerdo a los parámetros tope de pila y cabecera

            Retorna:
                String: Mensaje de error definido

            Parámetros:
                stackTop -- tope de la pila
                headChar -- elemento de secuencia en cabecera     
        """
        message = ''

#{(ERRORES-SINTÁCTICO)}

        if message == '':
            return 'Error sintáctico no definido'

        
        return f'Error sintáctico en fila {errorPos[0]} elemento {errorPos[1]}:\n{message}'
