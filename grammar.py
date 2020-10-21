EXP = "exp"
ALT = "alt"
ANY = "any"
SE  = "se"
SEC  = "sec"
SER  = "ser"
CHAR = "char"
AGR = "agr"
MUT = "mut"
RAN = "ran"
D = "d"
OP  = "op"
CMP = "cmp"

specialCharsIn = [ '[', ']', '{', '}', '-']
specialCharsOut = ['(', ')', '[', ']', '{', '}', '*', '$', '?','+']
band = []
stack = []

def grammar(inputString):
    global band
    global stack
    stack = []
    band = list(inputString+"$")
    stack.append(EXP)
    head = 0
    #---------------------------------------------------------
    while(True):

        if(len(band)<=head): 
            e1,e2 =notifyError(stack[-1], 'Fin de cadena')
            return e1,e2

        if(len(stack) == 0):
            if(len(stack) == 0 and len(band)==head+1):
                return True
            else:
                return False

        elif(stack[-1]==EXP):
            if(band[head]=='\\' or band[head]=='(' or isChar(band[head]) or band[head]=='['):
                production_one()
            else:
                e1,e2 =notifyError(stack[-1], band[head])
                return e1,e2

        elif(stack[-1]==ALT):
            if(band[head]=='\\'):
                head = production_two(head)
            elif(isChar(band[head]) or band[head]=='['):
                production_four()
            elif(band[head]=='('):
                production_three()
            else:
                e1,e2 =notifyError(stack[-1], band[head])
                return e1,e2

        elif(stack[-1]==ANY):
            if(head == len(band) and band[head]=='$'):
                e1,e2 =notifyError(ANY, band[head])
                return e1,e2
            head = production_five(head)

        elif(stack[-1]==SE):
            if(isChar(band[head])):
                head = production_five(head)
            elif(band[head]=='['):
                head = production_six(head)
            else:
                e1,e2 =notifyError(stack[-1], band[head])
                return e1,e2

        elif(stack[-1]==SEC):
            if(isChar(band[head])):
                head = production_seven(head)
            elif(band[head]=='\\' or isChar(band[head], 1)):
                head = production_eight(head)
            
            else:
                e1,e2 =notifyError(stack[-1], band[head])
                return e1,e2

        elif(stack[-1]==SER):
            if(band[head]=='-'):
                head = production_nine(head)
            elif(band[head]=='\\' or isChar(band[head],1) or band[head]==']'):
                production_ten()
            
            else:
                e1,e2 =notifyError(stack[-1], band[head])
                return e1,e2

        elif(stack[-1]==CHAR):
            if(band[head]=='\\'):
                head = production_eight(head)
            elif(isChar(band[head],1)):
                head = production_eleven(head)
            elif(band[head]==']'):
                head = production_five(head)
            else:
                e1,e2 =notifyError(stack[-1], band[head])
                return e1,e2

        elif(stack[-1]==AGR):
            if(band[head]=='('):
                head = production_twelve(head)
            else:
                e1,e2 =notifyError(stack[-1], band[head])
                return e1,e2
        
        elif(stack[-1]==MUT):
            if(band[head]=='\\' or isChar(band[head]) or band[head]=='[' or band[head]=='(' 
            or band[head]==')' or band[head]=='|'or (head == len(band)-1 and band[head]=='$')):
                production_fourteen()
            elif(band[head]=='+' or band[head]=='*'):
                head = production_five(head)
            elif(band[head]=='{'):
                head = production_thirteen(head)
            else:
                e1,e2 =notifyError(stack[-1], band[head])
                return e1,e2

        elif(stack[-1]==RAN):
            if(band[head]=='}'):
                head = production_five(head)
            elif(band[head]==','):
                head = production_fifteen(head)
            else:
                e1,e2 =notifyError(stack[-1], band[head])
                return e1,e2

        elif(stack[-1]==D):
            if(isDigit(band[head])):
                head = production_sixteen(head)
            elif(band[head]=='}' or band[head]==','):
                production_fourteen()
            else:
                e1,e2 =notifyError(stack[-1], band[head])
                return e1,e2

        elif(stack[-1]==OP):
            if(band[head]=='\\' or isChar(band[head]) or band[head]=='[' or band[head]=='(' 
            or band[head]==')' or (head == len(band)-1 and band[head]=='$')):
                production_fourteen()
            elif(band[head]=='|'):
                head = production_seventeen(head)
            else:
                e1,e2 =notifyError(stack[-1], band[head])
                return e1,e2

        elif(stack[-1]==CMP):
            if(band[head]=='\\' or isChar(band[head]) or band[head]=='[' or band[head]=='(' ):
                production_eightteen()
            elif(band[head]==')' or (head == len(band)-1 and band[head]=='$')):
                production_fourteen()
            else:
                e1,e2 =notifyError(stack[-1], band[head])
                return e1,e2

        elif(stack[-1]== ')' or stack[-1]== ']' or stack[-1]== '}'):
            if(stack[-1]== band[head]):
                head = production_five(head)
            else:
                e1,e2 =notifyError(stack[-1], band[head])
                return e1,e2

        elif(stack[-1]== 'l'):
            if(isChar(band[head])):
                head = production_five(head)
            else:
                e1,e2 = notifyError(stack[-1], band[head])
                return e1,e2
                
                

    
def isChar(char, type = 0):
    if ((type == 0 and char in specialCharsOut)
    or (type == 1 and char in specialCharsIn)):
        return False    
    return True

def isDigit(dig):
    digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    if dig in digits:
        return True
    return False

def production_one():
    stack.pop()
    stack.append(CMP)
    stack.append(OP)
    stack.append(ALT)

def production_two(head):
    stack.pop()
    stack.append(MUT)
    stack.append(ANY)
    head = head + 1
    return head

def production_three():
    stack.pop()
    stack.append(MUT)
    stack.append(AGR)

def production_four():
    stack.pop()
    stack.append(MUT)
    stack.append(SE)

def production_five(head):
    stack.pop()
    head += 1
    return head
    
def production_six(head):
    stack.pop()
    stack.append(SEC)
    head += 1
    return head

def production_seven(head):
    stack.pop()
    stack.append(SER)
    head += 1
    return head

def production_eight(head):
    stack.pop()
    stack.append(CHAR)
    stack.append(ANY)
    head += 1
    return head

def production_nine(head):
    stack.pop()
    stack.append(']')
    stack.append('l')
    head += 1
    return head

def production_ten():
    stack.pop()
    stack.append(CHAR)

def production_eleven(head):
    stack.pop()
    stack.append(CHAR)
    head += 1
    return head

def production_twelve(head):
    stack.pop()
    stack.append(')')
    stack.append(EXP)
    head += 1
    return head

def production_thirteen(head):
    stack.pop()
    stack.append(RAN)
    stack.append(D)
    head += 1
    return head

def production_fourteen():
    stack.pop()

def production_fifteen(head):
    stack.pop()
    stack.append('}')
    stack.append(D)
    head += 1
    return head

def production_sixteen(head):
    stack.pop()
    stack.append(D)
    head += 1
    return head

def production_seventeen(head):
    stack.pop()
    stack.append(OP)
    stack.append(ALT)
    head += 1
    return head

def production_eightteen():
    stack.pop()
    stack.append(CMP)
    stack.append(ALT)


def notifyError(error, Charpos):
    charWaited = ""
    if(error == EXP):
        charWaited = charWaited + "\\, [, char, ( "
    elif(error == ALT):
        charWaited = charWaited + "\\, [, char, ( "
    elif(error == ANY):
        charWaited = charWaited + "un Caracter"
    elif(error == SE):
        charWaited = charWaited + "[, char "
    elif(error == SEC):
        charWaited = charWaited + "char, \\ "
    elif(error == SER):
        charWaited = charWaited + "-, ], char, \\ "
    elif(error == CHAR):
        charWaited = charWaited + "] char, \\ "
    elif(error == AGR):
        charWaited = charWaited + "("
    elif(error == MUT):
        charWaited = charWaited + "+, *, [, char, {, |, \\, (, ) "
    elif(error == RAN):
        charWaited = charWaited + "',' , } "
    elif(error == D):
        charWaited = charWaited + "',' , }, Digito "
    elif(error == OP):
        charWaited = charWaited + "|, \\, [, char, (, )"
    elif(error == CMP):
        charWaited = charWaited + "\\, [, char, (, ) "
    else:
        charWaited = charWaited + error + " "
    
    return charWaited, Charpos