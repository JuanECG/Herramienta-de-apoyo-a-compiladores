import re
import copy
import grammar
from const import *

class Token ():
    """
    Creates a regular-expression or a set-of-expressions Token 
    
    Attributes:\n
        name: String that specifies the name of the Token
        typeExp: Boolean that specifies type of expression
            default:0
            regular expression: 0
            set-of-expressions: 1
        regularExp: A Python RegEx string that specifies the 
        regular expression that the Token will use.
            default=""
    """
    def __init__(self, name, typeExp=0, regularExp="", setExp = None):
        self.__name       = name
        self.__typeExp    = typeExp
        self.__regularExp = regularExp
        if setExp: self.__setExp = setExp
    
    def getName(self):
        return self.__name
    
    def getTypeExp(self):
        return self.__typeExp

    def getRegularExp(self):
        return self.__regularExp

    def getSetExp(self):
        return self.__setExp
    
    def setName(self, name):
        self.__name = name

    def setTypeExp(self, typeExp):
        self.__typeExp = typeExp
    
    def setRegularExp(self, regularExp):
        self.__regularExp = regularExp

    def setSetExp(self, setExp):
        self.__setExp = setExp

    def __str__(self):
        return self.__name
    
    def __eq__(self, o_t):
        if (self.__name == o_t.getName() and 
            self.__typeExp == o_t.getTypeExp() and
            self.__regularExp == o_t.getRegularExp()):
            return True
        return False

class Subset():
    """
    A class used to define a set of characters through a simplified expression(identifier)

    Attributes
    ----------
    identifier : string
        simplified expression used to refer to a characters subset instead a regular expression
    expression : string
        it's the regular expression that match the subset characters set
    description : string
        short description of the set of characters that will be matched by the subset
    
    Methods
    -------
    getIdentifier():
        returns the subset identifier
    getExpression():
        returns the regular expression asociated to the subset
    getDescription():
        returns the description given to the subset
    setIdentifier(identifier):
        defines the identifier for the subset
    setExpression(expression):
        defines the regular expression of the subset
    setDescription(description):
        defines a description about the subset
    """
    def __init__(self, identifier, expression, description):
        self.__identifier  = identifier
        self.__expression  = expression
        self.__description = description
    
    def getIdentifier(self):
        return self.__identifier
    
    def getExpression(self):
        return self.__expression

    def getDescription(self):
        return self.__description
    
    def setIdentifier(self, identifier):
        self.__identifier = identifier

    def setExpression(self, expression):
        self.__expression = expression
    
    def setDescription(self, description):
        self.__description = description

    def __eq__(self, o_e):
        if (o_e.getIdentifier() == self.__identifier and
            o_e.getExpression() == self.__expression and
            o_e.getDescription() == self.__description):
            return True
        return False

class SubToken():
    """
    A class that contains the resultant Token from an analysed sequence fragment

    Attributes
    ----------
    value : string
        contains the value of the recognized sequence fragment 
    token : string
        it refers to the name of the Token or patron that matched the sequence fragment
    position : tuple
        a tuple with the posicion defined as row and column of the recognized sequence fragment

    Methods
    -------
    getValue():
        returns the value of the recognized sequence fragment 
    getToken():
        returns the name of the defined token
    getPosition():
        returns the defined position
    setValue(value):
        defines the recognized secuence fragment value
    setToken(token):
        defines the name of matched token
    setPosition(position):
        defines the position of the matched secuence fragment 
    """
    def __init__(self, value, token, position):
        self.__value = value
        self.__token  = token
        self.__position  = position
    
    def getValue(self):
        return self.__value

    def getToken(self):
        return self.__token
    
    def getPosition(self):
        return self.__position

    def setValue(self, value):
        self.__value = value

    def setToken(self, token):
        self.__token = token

    def setPosition(self, position):
        self.__position = position
    
    def __str__(self):
        return str(self.__value)

class LexiconAnalyzer():
    """
    This module holds the tokens list and Subsets defined to run lexical analysis over a sequence
    """
    def __init__(self):
        self.__tokenList      = []
        self.__subTokenList   = []
        self.__subsetList     = []
        self.__separators     = []
        self.setDefaultValues()

    def addToken(self, nToken):
        """
            Adds a Token to Tokens list

            Parameters
            -----------
                nToken: Token to add
        """
        self.__tokenList.append(nToken)
    
    def setToken(self, sToken, id=-1,):
        """
           Replace the token in the given index

            Parameters
            -----------
                sToken: new Token
                id: int with positions of token to be replaced
        """
        self.__tokenList.pop(id)
        self.__tokenList.insert(id, sToken)

    def removeToken(self, index):
        """
            Removes Token in position index

            Parameters
            -----------
                index: int position of Token to be removed
        """
        oldtoken = self.__tokenList[index]
        self.__tokenList.pop(index)
        return oldtoken

    def getTokenList(self):
        """
            Get the tokens list

            returns:
                list: Tokens list
        """
        return self.__tokenList

    def addSubset(self, nSubset):
        """
            Adds a Sub-set to Sub-sets list

            Parameters
            -----------
                nSubset: Sub-set to add
        """
        self.__subsetList.append(nSubset)
    
    def setSubset(self, sSubset, id=-1):
        """
            Replaces Sub-set in position index

            Parameters
            -----------
                sSubset: new Sub-set
                id: int position of Sub-set to be replaced
        """
        oldSubset = self.__subsetList[id].getIdentifier()
        self.__subsetList.pop(id)
        self.updateTokens(oldSubset, sSubset.getIdentifier())
        self.__subsetList.insert(id,sSubset)

    def removeSubset(self, id):
        """
            Removes Sub-set in position index

            Parameters
            -----------
                id: int position of Sub-set to be removed
        """
        subIdentifier = self.__subsetList[id].getIdentifier()
        subExpression = self.__subsetList[id].getExpression()
        self.__subsetList.pop(id)
        for token in self.__tokenList:
            if subIdentifier in token.getRegularExp():
                token.setRegularExp(token.getRegularExp().replace(subIdentifier, subExpression))

    def getSubsetList(self):
        """
            Gets Sub-sets list

            returns:
                list: Sub-sets list
        """
        return self.__subsetList

    def getSeparators(self):
        """
            Gets defined separators list

            returns:
                list: Separators list
        """
        return self.__separators

    def setSeparators(self, sSeparators):
        """
            Defines separators list

            Parameters
            -----------
                sSeparators : Separators list
        """
        self.__separators = sSeparators
    
    def findSubset(self,id):
        """
            Verifies if exist a Sub-set in the given position

            Parameters
            -----------
                id : position of the Sub-set to be finded
            
            returns:
                True: if exist a Sub-set in the given position
                False: if there isn't match
        """
        for subset in self.__subsetList:
            if subset.getIdentifier() == id:
                return True
        return False
    
    def findToken(self, name):
        """
            Verifies if exist a Token with the given name

            Parameters
            -----------
                name : name of the Token to be finded
            
            returns:
                True: if exist a token with the given name
                False: if there isn't match
        """
        for token in self.__tokenList:
            if token.getName() == name:
                return True
        return False
    
    def findTokenbyExp(self,exp):
        """
            Verifies if exist a Token with the given Expression

            Parameters
            -----------
                exp : Expression of the Token to be finded
            
            returns:
                True: if exist a token with the given expression
                False: if there isn't match
        """
        for token in self.__tokenList:
            if token.getExpression() == exp:
                return True
        return False
    
    def getTokenbyName(self,name):
        """
            Returns Token with the given name

            Parameters
            -----------
                name : name of the Token to be finded
            
            returns:
                token with the given name
        """
        for token in self.__tokenList:
            if token.getName() == name:
                return token
        return False
    
    def getSubsetbyId(self,id):
        """
            Finds the Token with the given Expression

            Parameters
            -----------
                exp : Expression of the Token to be finded
        """
        for subset in self.__subsetList:
            if subset.getIdentifier() == id:
                return subset
        return False
    
    def charInSubsetList(self,char):
        """
            Verifies if exist Sub-set with the given identifier

            Parameters
            -----------
                char : character defined as identifier
            
            returns:
                subset: if exist a Sub-set with the given nidentifierame
                None: if there isn't match
        """
        for subset in self.__subsetList:
            if char == subset.getIdentifier():
                return subset
        return None
    
    def setDefaultValues(self):
        """
            Refresh Sub-sets list with default values
        """
        subsetL = Subset("l", "[a-z]", "Cualquier carácter alfabético entre a y z")
        subsetLL = Subset("L", "[A-Z]", "Cualquier carácter alfabético entre A y Z")
        subsetD = Subset("d", "[0-9]", "Cualquier dígito entre 0 y 9")
        subsetP = Subset(".", ".", "Cualquier carácter (Excepto, nueva línea)")
        subsetMu = Subset("*", "*", "Permite reconocer cero o más ocurrencias del caracter antes de este")
        subsetMa = Subset("+", "+", "Permite reconocer uno o más ocurrencias del caracter antes de este")
        
        self.__subsetList.append(subsetL)
        self.__subsetList.append(subsetLL)
        self.__subsetList.append(subsetD)
        self.__subsetList.append(subsetP)
        self.__subsetList.append(subsetMu)
        self.__subsetList.append(subsetMa)

        self.__separators.append(' ')
        self.__separators.append('\n')
        self.__separators.append('\t')

    def clearTokenList(self):
        """
            Clear the Tokens list
        """
        self.__tokenList = []

    def updateTokens(self,oldSubset, newSubset):
        """
            When a Sub-set is redefined, this function update Tokens expression to avoid
            mistakes on recognition

            Parameters
            -----------
                oldSubset: old Sub-set expression
                newSubset: new Sub-set expression
        """
        
        for token in self.__tokenList:
            if(token.getTypeExp()==0):
                bsFlag=False
                resultConvert = ""
                
                #expression = repr(token.getRegularExp())
                #expression = expression[1:-1]
                expression = token.getRegularExp()
                for char in expression:
                    if not bsFlag:
                        if char == '\\':
                            bsFlag = True
                        elif char == oldSubset: # REPLACE OLD EXP WITH NEW EXP
                            resultConvert += newSubset
                        elif char == newSubset: # AVOIDS NO SPECIAL CHARS TO BE INTERPRETED AS SPECIALS
                            resultConvert += f'\{newSubset}'
                        else: 
                            resultConvert += char
                    else:
                        if char == oldSubset and char not in CONVERTIONDIC:
                            resultConvert += char # TURNS OLD SPECIAL CHAR INTO NNORMAL CHAR
                        else:
                            resultConvert += f'\{char}'
                        bsFlag = False
                token.setRegularExp(resultConvert)

    def convertInput(self, expression, type=0):
        """
            Turns an expression defined with Sub-sets into a expression defined with regular expression
            sets for regex

            Parameters
            -----------
                expression :    String -- expression to be "translated"
                                List -- set of strings to be translated into one
                type :  0 -- if expression is a String
                        1 -- if expression is a set of Strings
            
            returns:
                string with final regular expression
        """
        resultConvert = ""
        if type == 0:
            #expression = repr(expression)
            #tExpression = list(expression[1:-1])
            tExpression = expression
            bsFlag = False
            
            for char in tExpression:
                if not bsFlag:
                    if char == '\\':
                        bsFlag = True
                    
                    elif self.charInSubsetList(char):
                        resultConvert +=self.charInSubsetList(char).getExpression()
                    else:
                        resultConvert += char
                else:
                    if self.charInSubsetList(char) and char not in CONVERTIONDIC:
                        resultConvert += char
                    else:
                        resultConvert += f'\{char}'
                    bsFlag = False
        elif type == 1:
            for char in expression:
                converted = ''
                for sc in char:
                    if sc in CONVERTIONDIC:
                        converted += CONVERTIONDIC[sc]
                    else: converted += sc
                
                resultConvert += converted + '|'

            resultConvert= resultConvert[:-1]
            resultConvert= "(" + resultConvert + ")"
        
        return resultConvert

    def runLexic(self, userInput):
        """
            Develops lexical analysis on the given string

            Parameters
            -----------
                userInput :    String with the input to be analyzed
            
            returns a tuple:
                boolean :   True -- if no lexical errors appeared on analysis
                            False -- if there was a lexical error on analysis

                if True: Returns the subtokens list result of the analysis
                else : Returns a String with the error message
        """
        # Connvert tokens to expressions with python
        tokenList = []
        self.__subTokenList = []
        result = self.__subTokenList
        for token in self.__tokenList:
            if token.getTypeExp() == 0:
                tToken = Token(token.getName(),token.getTypeExp(), self.convertInput(token.getRegularExp(),token.getTypeExp()))
            else:
                tToken = token
            tokenList.append(tToken)
        # Here starts the real algorithm
        #curPos x: row y: column
        curPos = [1,1]
        mainChar = ""+userInput
        activeTokenList = []
        while (True):
            activeTokenList = []
            if(not len(mainChar)>0):
                return (True,result)

            if(mainChar[0] in self.getSeparators()):
                if mainChar[0] == '\n':
                    curPos[0] += 1
                    curPos[1] = 1
                    
                mainChar = mainChar[1:]
                continue
                
            activeTokenList = self.analyzeChar(mainChar, tokenList)

            if len(activeTokenList) > 2:
                #Ambiguity error
                return self.notifyError("Error2",None,None,activeTokenList)

            elif len(activeTokenList) != 0 :
                #Validate and split mainChar
                newChar = self.validate(result, mainChar, curPos, activeTokenList)
                if(newChar != "Error2"):
                    mainChar = newChar
                    curPos[1] +=1
                else:
                    return self.notifyError("Error2",None,None,activeTokenList)
            elif len(activeTokenList) == 0:
                return self.notifyError("Error1",(mainChar[0],curPos),len(userInput)-len(mainChar))
                #No match character error
        
    def notifyError(self, error, errorChar=None, errorPos=None,activeTokenList=None):
        """
        Notifies a given error specified by the error atribute
        
        Attributes:\n
            error:     String that specifies the type of error
                    error1,error2, etc
            errorChar: Object that specifies the unknown element
                        default: None 
        """
        
        if error == "Error1":
            message= "Error léxico en fila "+str(errorChar[1][0])+ " elemento "+ str(errorChar[1][1])+":\n"    
            message += "El elemento '" + errorChar[0] + "' no pertenece a los tokens definidos."
            return (False,message, (errorChar[1][0], errorPos))
            
        elif error =="Error2":
            message="Existe un conflicto entre los token: "
            for token in activeTokenList:
                message= message + token.getName() + " "
            return (False,message)

    def analyzeChar(self, mainChar, tokenList):
        """
        Analyses a segment and checks whether its elements coincide
        with a TokenList
        """
        activeTokenList = []
        segment = mainChar
        for token in tokenList:
            x=re.match(token.getRegularExp(),segment)
            if (x is not None):
                activeTokenList.append(token)
        return activeTokenList

    def validate(self, result, mainChar, curPos, activeTokenList):
        """
        Checks and adds to the result array a given Token name
        """
        cut = 0
        activeTLlen = len(activeTokenList)
        if activeTLlen == 1:
            cut = re.match(activeTokenList[0].getRegularExp(),mainChar).span(0)
            if (activeTokenList[0].getTypeExp() == 1 ):
                subt = activeTokenList[0].getName()+":"+mainChar[0:cut[1]]
                result.append(SubToken(mainChar[0:cut[1]],subt,curPos.copy()))
            else:
                result.append(SubToken(mainChar[0:cut[1]],activeTokenList[0].getName(),curPos.copy()))
            return mainChar[cut[1]:]
            
        elif activeTLlen == 2:
            if (activeTokenList[0].getTypeExp() == 1 and activeTokenList[1].getTypeExp() == 0):
                cut = re.match(activeTokenList[0].getRegularExp(),mainChar).span(0)
                subt = activeTokenList[0].getName()+":"+mainChar[0:cut[1]]
                result.append(SubToken(mainChar[0:cut[1]],subt,curPos.copy()))
                return mainChar[cut[1]:]
                
            if(activeTokenList[1].getTypeExp() == 1 and activeTokenList[0].getTypeExp() == 0):
                cut = re.match(activeTokenList[1].getRegularExp(),mainChar).span(0)
                result.append(SubToken(mainChar[0:cut[1]],activeTokenList[1].getName(),curPos.copy()))
                return mainChar[cut[1]:]

        return "Error2"

    def validateRegExpression(self, regularExp):
        """
        Validates that the expressions structure is accurate with regular expressions standard
        """
        expression = repr(regularExp)
        expression = expression[1:-1]
        return grammar.grammar(expression)

    def cutStep(self, mainChar, result, curPos):
        """
        Sequence of functions in order to run as one step of Lexical Analysis
        """
        tokenList = []
        for token in self.__tokenList:
            if token.getTypeExp() == 0:
                tToken = Token(token.getName(),token.getTypeExp(), self.convertInput(token.getRegularExp(),token.getTypeExp()))
            else:
                tToken = token
            tokenList.append(tToken)

        activeTokenList  = []        
        activeTokenList = self.analyzeChar(mainChar, tokenList)

        if len(activeTokenList) > 2:
            return (-1, mainChar, curPos, result, activeTokenList)

        elif len(activeTokenList) != 0 :
            #Validate and split mainChar
            newChar = self.validate(result, mainChar, curPos, activeTokenList)
            if(newChar != "Error2"):
                return (1, newChar, curPos, result, activeTokenList)
            else:
                return (-1, mainChar, curPos, result, activeTokenList)

        elif len(activeTokenList) == 0:
            return (0, mainChar, curPos, result, activeTokenList)

    def generateSaveData(self):
        """
        Builsd a JSON structure of the current Token list and Sub-setd list in the project
        """
        tokens = []
        subsets = []

        for token in self.getTokenList():
            setExp = token.getSetExp() if token.getTypeExp() == 1  else None
            tokens.append({
                "name" : token.getName(),
                "typeExp": token.getTypeExp(),
                "regularExp": token.getRegularExp(),
                "setExp": setExp
            })

        for subset in self.getSubsetList():
            subsets.append({
                "identifier": subset.getIdentifier(),
                "expression": subset.getExpression(),
                "description": subset.getDescription()
            })

        lexicon = {
            "module":"lexicon",
            "tokens":tokens,
            "subsets": subsets
        }

        return lexicon

    def loadLexiconData(self, lexicon):
        """
        Mount a JSON structure into the Token List and the Sub-set list of the project

        Parameters
        ----------
        lexicon : Json structure
            Json structure to mount into the Lexic Module
        """
        tokens = lexicon.get("tokens")
        subsets = lexicon.get("subsets")
        self.__tokenList = []
        self.__subsetList = []
        for token in tokens:
            if token.get('typeExp') == 1: newToken = Token(token.get('name'),token.get('typeExp'),token.get('regularExp'), token.get('setExp'))
            else: newToken = Token(token.get('name'),token.get('typeExp'),token.get('regularExp'))
            self.addToken(newToken)
        
        # Hay que analizar que se hara con los subsets
        for subset in subsets:
            newSubset = Subset(subset.get('identifier'),subset.get('expression'),subset.get('description'))
            self.addSubset(newSubset)