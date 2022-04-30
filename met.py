## Team
# Athanasios Kalyviotis, 4607, cse84607
# Dimitrios Giannitsakis, 4338, cse84338

import numbers
import sys
import io


keyword = ['while','if','else']
addOperator = ['+','-']
mulOperator = ['*','/']
delimeter = [',','.',';']
groupSymbol= ['(',')','{','}','[',']']

# used in intermediate code generation - class Quad
label_number = 1 # a counter that keeps track of current quad label
temp_number = 1 # a counter that keeps track of current temporary variable number

class Token:
    def __init__(self, recognized_string, family, line_number):
        self.recognized_string = recognized_string
        self.family = family
        self.line_number = line_number

    def __str__(self):
        return f"{self.recognized_string}\t \
                family:{self.family},\t \
                line: {self.line_number}"


class Lex:
    def __init__(self, file_name, current_line, token):
        self.file_name = file_name # get filename from terminal argument
        self.current_line = current_line
        self.token = token
        self.last_position = 0 # initialize at the beggining of the file

    def __del__(self):
        source_file.close() # close the file (read-only)

    def error(self, type):
        if (type == 'CommentException'):
            print(f"There is an unclosed comment starting in line {token.line_number}")

        elif (type == 'IllegalCharacterException'):
            print(f"Found illegal character in line {token.line_number} after '{token.recognized_string}'")

        elif (type == 'AssignOperatorException'):
            print(f"Assignment operator ':=' expected in line {token.line_number} but instead got '{token.recognized_string}'")

        elif (type == 'IllegalNameException'):
            print(f"An ID/Keyword cannot begin with a digit. At line {token.line_number} ")

        else:      
            print('There has been an error')

        exit(-1)

    def next_token(self):
        global source_file
        source_file = open(self.file_name, 'r')
        recognized_string = ''
        family = ''
        openComment = False
        char = ' '

        # jump to where we left off
        source_file.seek(self.last_position)

        while char != '':

            # read by character
            char = source_file.read(1)
            # print (char)  

            if (char == '\n') : # changed line
                self.current_line+=1
                continue
            elif char == '#': 
                openComment = not openComment
                continue
            elif (char.isspace() or ('\t' in char)) or openComment:
                continue # skip white characters
            elif char == '': 
                if openComment : self.error('CommentException') # comment not closed
                else :
                    recognized_string = 'eof'
                    family = 'eof'
                    break
            else:
                    
                ## determine token family

                # number
                if (char >= '0' and char <= '9'):
                    recognized_string += char
                    save_cursor = source_file.tell() # save cursor
                    char = source_file.read(1) # peek  
                    while (char >= '0' and char <= '9') :
                        recognized_string += char
                        save_cursor = source_file.tell() # save cursor
                        char = source_file.read(1) # peek  
                    else:
                        if ((char >= 'A' and char <= 'Z') or (char >= 'a' and char <= 'z')):
                            # print('hit exception')
                            self.error('IllegalNameException')
                        source_file.seek(save_cursor) # revert cursor
                        family = 'number'
                    
                    break

                # id
                if ((char >= 'A' and char <= 'Z') or (char >= 'a' and char <= 'z')) :
                    while ((char >= '0' and char <= '9') or (char >= 'A' and char <= 'Z') or (char >= 'a' and char <= 'z')): 
                        recognized_string += char
                        save_cursor = source_file.tell() # save cursor
                        char = source_file.read(1) # peek  
                    else:
                        source_file.seek(save_cursor) # revert cursor
                        family = 'id'
                    break

                # addOperator
                if (char in addOperator) :
                    recognized_string += char
                    family = 'addOperator'
                    break

                # mulOperator
                elif (char in mulOperator) :
                    recognized_string += char
                    family = 'mulOperator'
                    break

                # groupSymbol
                elif (char in groupSymbol) :
                    recognized_string += char
                    family = 'groupSymbol'
                    break

                # delimeter
                elif (char in delimeter) :
                    recognized_string += char
                    family = 'delimeter'
                    break

                # assignment
                elif (char == ':') :
                    recognized_string += char
                    ### save_cursor = source_file.tell() # save cursor
                    char = source_file.read(1) # peek 
                    if (char == '=') :
                        recognized_string += char
                        family = 'assignment'
                    else :
                        ### source_file.seek(save_cursor) # revert cursor
                        self.error('AssignOperatorException')
                    break

                # relOperator
                elif (char == '<') :
                    recognized_string += char
                    family = 'relOperator'
                    save_cursor = source_file.tell() # save cursor
                    char = source_file.read(1) # peek 
                    if (char == '=' or char == '>') :
                        recognized_string += char
                    else :
                        source_file.seek(save_cursor) # revert cursor
                    break

                elif (char == '>') :
                    recognized_string += char
                    family = 'relOperator'
                    save_cursor = source_file.tell() # save cursor
                    char = source_file.read(1) # peek 
                    if (char == '=') :
                        recognized_string += char
                    else :
                        source_file.seek(save_cursor) # revert cursor
                    break

                elif (char == '=') :
                    recognized_string += char
                    family = 'relOperator'
                    break
                else:
                    self.error('IllegalCharacterException') # found illegal character

        if (openComment): self.error('CommentException')

        # save current position
        self.last_position = source_file.tell() 

        # generate the token and return it
        self.token = Token(recognized_string, family, self.current_line)
        return self.token;





class Parser:
    def __init__(self, lexical_analyzer):
        self.lexical_analyzer = lexical_analyzer

    def syntax_analyzer(self):
        global token
        token = self.get_token()
        self.program()
        print('compilation successfully completed')

    def get_token(self):
        next_token = self.lexical_analyzer.next_token()
        print (next_token)
        return next_token # get the next token

    def error(self, type):
        if (type == 'MissingCloseParen'):
            print(f"There is an unclosed parenthesis '(' in line {token.line_number}. Every '(' should close with ')' but instead got '{token.recognized_string}'")
        
        elif (type == 'MissingDefault'):
            print(f"'default' keyword expected in line {token.line_number}")

        elif (type == 'MissingOpenParen'):
            print(f"Open paren '(' expected in line {token.line_number} but instead got '{token.recognized_string}'")
                
        elif(type == 'MissingProgramId'):
            print("The name of the program expected after the keyword 'program' in line 1 but instead got '{token.recognized_string}'")

        elif (type == 'MissingCloseBracket'):
            print(f"There is an unclosed bracket '[' in line {token.line_number}. Every '[' should close with ']' but instead got '{token.recognized_string}'")

        elif (type == 'MissingOpenBracket'):
            print(f"Open bracket '[' expected in line {token.line_number} but instead got '{token.recognized_string}'")    

        elif (type == 'MissingCloseCurlyBracket'):
            print("Close curly bracket '}' expected in line %d. Every '{' should close with '}' but instead got '%s'"% (token.line_number, token.recognized_string))

        elif (type == 'MissingOpenCurlyBracket'):
            print("Open curly bracket '{' expected in line %d but instead got '%s'"% ((token.line_number), (token.recognized_string)))

        elif (type == 'MissingFullStop'):
            print("Every program should end with a fullstop, fullstop at the end is missing")

        elif (type == 'MissingRelOperator'):
            print(f"RelOperator Expected in line '{token.line_number}'")

        elif (type == 'MissingProgramm'):
            print(f"Keyword 'program' expected in line '{token.line_number}'. All programs should start with the keyword 'program'")

        elif (type == 'MissingInInout'):
            print(f"keyword in or inout expected in line '{token.line_number}'")

        elif (type == 'MissingInInoutdId'):
            print(f"Expected id after in/inout keyword in line '{token.line_number}' but instead got '{token.recognized_string}'")

        elif (type == 'MissingQuestionMark'):
            print(f"Questionmark expected in line '{token.line_number}' but instead got '{token.recognized_string}'") 

        elif (type == 'MissingAssignment'):
            print(f"Expected  ':='  for assigmnent of variable in line '{token.line_number}' but instead got '{token.recognized_string}'") 

        elif (type == 'MissingFunctionProcedure'):
            print(f"Keyword 'function' or 'procedure' expected in line '{token.line_number}' but instead got '{token.recognized_string}'. All subprograms should start with the keyword 'function' or 'procedure'")
        
        elif (type == 'MissingNoWord'):
            print("No characters are allowed after the fullstop indicating the end of the program")
        
        elif (type == 'MissingFactor'):
            print(f"Expected factor in line {token.line_number} but instead got '{token.recognized_string}'")
        exit(-1)   

    def ifStat(self):
        # print('ifStat')
        global token 
        if token.recognized_string == '(':
                token = self.get_token()
                self.condition()

                if token.recognized_string == ')':
                    token=self.get_token()
                    self.statements()
                    self.elsepart()
                else:
                    self.error('MissingCloseParen')      
        else:
            self.error('MissingOpenParen')

    def elsepart(self):
        # print('elsepart')
        global token 
        if token.recognized_string == 'else':
            token = self.get_token()
            self.statements()

    def whileStat(self):
        # print('whileStat')
        global token 
        if token.recognized_string == '(':
            token = self.get_token()
            self.condition()

            if token.recognized_string == ')':
                token=self.get_token()
                self.statements()        
    
            else:
                self.error('MissingCloseParen')
        else:
            self.error('MissingOpenParen')

    def switchcaseStat(self):
        # print('switchcaseStat')
        global token 
        while(token.recognized_string == 'case'):
            token = self.get_token()
            if token.recognized_string == '(':
                token = self.get_token()
                self.condition()
            
                if token.recognized_string == ')':
                        token = self.get_token()
                        self.statements()
                else:
                    self.error('MissingCloseParen')

            else:
                self.error('MissingOpenParen')

    def forcaseStat(self):
        # print('forcaseStat')
        global token 
        while(token.recognized_string == 'case'):
            token = self.get_token()
            if token.recognized_string == '(':
                token = self.get_token()
                self.condition()
           
                if token.recognized_string == ')':
                    token = self.get_token()
                    self.statements()
                else:
                     self.error('MissingCloseParen')
 
            else:
                self.error('MissingOpenParen')

        if(token.recognized_string == 'default'):
            token = self.get_token()
            self.statements()
        else:
            self.error('MissingDefault')


    def incaseStat(self):
        # print('incaseStat')
        global token 
        while(token.recognized_string == 'case'):
            token = self.get_token()
            if token.recognized_string == '(':
                token = self.get_token()
                self.condition()
           
                if token.recognized_string == ')':
                    token = self.get_token()
                    self.statements()
                else:
                     self.error('MissingCloseParen')
 
            else:
                self.error('MissingOpenParen')     

    def returnStat(self):
        # print('returnStat')
        global token 
        if token.recognized_string == '(':
            token = self.get_token()
            self.expression()
            if token.recognized_string != ')':
                self.error('MissingCloseParen')
            token = self.get_token()
        else:
            self.error('MissingOpenParen')


    def printStat(self):
        # print('printStat')
        global token 
        if token.recognized_string == '(':
            token = self.get_token()
            self.expression()
            if token.recognized_string != ')':
                self.error('MissingCloseParen')
            token = self.get_token()
        else:
            self.error('MissingOpenParen')


    def inputStat(self):
        # print('inputStat')
        global token 
        if token.recognized_string == '(':
            token = self.get_token()
            if token.family != 'id':
              self.error('MissingId')
            token = self.get_token()
            if token.recognized_string != ')':
                self.error('MissingCloseParen') 
            token = self.get_token()
            
        else: 
            self.error('MissingOpenParen') 

    def declarations(self):
        # print('declarations')
        global token 
        while (token.recognized_string == 'declare') :
            token = self.get_token()
            self.varlist()
            if(token.recognized_string != ';'):
                self.error('MissingQuestionMark')
            token = self.get_token()
            
             
    
    def block(self):
        # print('block')
        global token 
        if token.recognized_string == '{':
            token = self.get_token()
            self.declarations()
            self.subprograms()
            self.blockstatements()
            # print('back at block')
            if token.recognized_string != '}':
              self.error('MissingCloseCurlyBracket')
            token = self.get_token()

        else: 
            self.error('MissingOpenCurlyBracket')       
    
    def formalparlist(self):
        # print('formalparlist')
        global token 
        if token.recognized_string != ')': # if parenthesis don't close immediately
            self.formalparitem()
            while(token.recognized_string == ','):
                token = self.get_token()
                self.formalparitem()

    def formalparitem(self):
        # print('formalparitem')
        global token 
        if (token.recognized_string == 'in' or token.recognized_string == 'inout'):
            token = self.get_token()
            if token.family != 'id':
                self.error('MissingInInoutdId')
            token = self.get_token()        
        else:
            self.error('MissingInInout')        			    


    def statements(self):
        # print('statements')
        global token 
        if token.recognized_string == '{':
            token = self.get_token()
            self.statement()
            while(token.recognized_string == ';'):
                token = self.get_token()
                self.statement()
            if token.recognized_string != '}':
              self.error('MissingCloseCurlyBracket')
            token = self.get_token()
        else:
            self.statement()
            if (token.recognized_string != ';'):
                self.error('MissingQuestionMark')
            token = self.get_token()
           
    def blockstatements(self):
        # print('blockstatements')
        global token 
        self.statement()
        # print('back at blockstatements')
        while(token.recognized_string == ';'):
            token = self.get_token()
            self.statement()   

    def statement(self):
        # print('statement')
        global token 

        if token.recognized_string =='if':
             token = self.get_token()
             self.ifStat()

        elif token.recognized_string =='while':
            token = self.get_token()
            self.whileStat()

        elif token.recognized_string =='switchcase':
             token = self.get_token()
             self.switchcaseStat()

        elif token.recognized_string =='forcase':
             token = self.get_token()
             self.forcaseStat()

        elif token.recognized_string =='incase':
             token = self.get_token()
             self.incaseStat()

        elif token.recognized_string =='call':
             token = self.get_token()
             self.callStat()

        elif token.recognized_string =='return':
             token = self.get_token()
             self.returnStat()

        elif token.recognized_string =='input':
             token = self.get_token()
             self.inputStat()

        elif token.recognized_string =='print':
             token = self.get_token()
             self.printStat()

        elif token.family == 'id':
            token = self.get_token()
            self.assignStat()

        
                
    def assignStat(self):
        # print('assignStat')
        global token 
        if (token.family == 'assignment'):
            token = self.get_token()
            self.expression()
        else:
            self.error('MissingAssignment') 

    def condition(self):
        # print('condition')
        global token
        self.boolterm()
        while token.recognized_string == 'or':
            token = self.get_token()
            self.boolterm()

    def boolterm (self):
        # print('boolterm ')
        global token 
        self.boolfactor()
        while token.recognized_string == 'and':
            token = self.get_token()
            self.boolfactor()       
    
    def boolfactor(self):
        # print('boolfactor')
        global token
        if token.recognized_string == 'not':
            token = self.get_token()
            if token.recognized_string == '[':
                token = self.get_token()
                self.condition()
                if (token.recognized_string != ']'):
                    self.error('MissingCloseBracket')     
                token = self.get_token()
            else:
                self.error('MissingOpenBracket')           
    
        elif token.recognized_string == '[':
                token = self.get_token()
                self.condition()
                if (token.recognized_string != ']'):
                    self.error('MissingCloseBracket')   
                token = self.get_token()
        

        else:
            self.expression()
            
            if (token.family == 'relOperator'):
                token = self.get_token()
            else:
                self.error('MissingRelOperator')
            self.expression()      
        
    def expression(self):
        # print('expression')
        global token 
        self.optionalSign()
        self.term()
        while(token.family == 'addOperator'):
            token = self.get_token()
            self.term()      
            
    def term(self):
        # print('term')
        global token 
        self.factor()
        while(token.family == 'mulOperator'):
            token = self.get_token()
            self.factor()
        
    def program(self):
        # print('program')
        global token
        if token.recognized_string == 'program':
            token = self.get_token()
            if token.family == 'id':
                token = self.get_token()
                self.block()
                if token.recognized_string == '.':
                    token = self.get_token()
                    if token.recognized_string == 'eof':
                        token = self.get_token()
                    else:
                        self.error('MissingNoWord')
                else:	
                    self.error('MissingFullStop')
            else:
                self.error('MissingProgramId')
        else:
            self.error('MissingProgram')     

    def factor(self):
        # print('factor')
        global token
        if token.recognized_string == '(':
            token = self.get_token()
            self.expression()
            if token.recognized_string != ')':
                self.error('MissingCloseParen')
            token = self.get_token()

        elif token.family == 'id':
            token = self.get_token()
            self.idtail()   
        elif token.family == 'number': 
            token = self.get_token()

        else:
            self.error('MissingFactor')   
  
            
    def actualparlist(self):
        # print('actualparlist')
        global token
        if (token.recognized_string != ')'): # if parenthesis don't close immediately
            self.actualparitem()
            while(token.recognized_string == ','):
                token = self.get_token()
                self.actualparitem()

                   
    def subprogram(self):
        # print('subprogram')
        global token 
        if (token.recognized_string == 'function') or (token.recognized_string == 'procedure'):
            token = self.get_token()
            if token.family == 'id':
                token = self.get_token()
                if token.recognized_string == '(':
                    token = self.get_token()
                    self.formalparlist()
                    if token.recognized_string != ')':
                        self.error('MissingCloseParen')
                    token = self.get_token()
                    self.block()

                else:
                    self.error('MissingOpenParen')
            else:
                self.error('MissingId')
            
        else:
            self.error('MissingFunctionProcedure') 

    def subprograms(self):
        # print('subprograms')
        global token 
        while(token.recognized_string == 'function' or token.recognized_string =='procedure'):
            self.subprogram()
           

    def actualparitem(self):
        # print('actualparitem')
        global token
        if token.recognized_string == 'in':
            token = self.get_token()
            self.expression()
        elif token.recognized_string == 'inout':
            token = self.get_token()
            if token.family != 'id':
              self.error('MissingInInoutId')
            token = self.get_token()

        else:
          self.error('MissingInInout')
      
    def idtail(self):
        # print('idtail')
        global token
        if token.recognized_string == '(':
            token = self.get_token()
            self.actualparlist()
            if token.recognized_string != ')':
                self.error('MissingCloseParen')
            token = self.get_token()
            
    def optionalSign(self):
        # print('optionalSign')
        global token
        if token.family == 'addOperator':
          token = self.get_token()

            
    def varlist(self):
        # print('varlist')
        global token 
        if (token.recognized_string != ';'): # check for ';' if empty (see declarations grammar)

            if token.family == 'id':
                token = self.get_token()
                while(token.recognized_string == ','):
                    token = self.get_token()
                    if (token.family != 'id'):
                        self.error('MissingId')  
                    token = self.get_token()
                    
            else:
                self.error('MissingId')  

# intermediate code
class Quad :
    def __init__(self, label, operator, op1, op2, op3):
        self.label = label # so that we can identify different quads
        self.operator = operator
        self.op1 = op1
        self.op2 = op2
        self.op3 = op3

    def __str__(self):
        return f"{self.label}, \
                {self.operator}, \
                {self.op1}, {self.op2}, {self.op3}"
    
    def set_op3(self, op3):
        self.op3 = op3 

    def get_label(self):
        return self.label

class QuadPointer :
    def __init__(self, label, quad):
        self.label = label
        self.quad = quad
    
    def get_quad(self):
        return self.quad
    


# helper routines

quad_list = [] # global list that keeps all quad objects

# returns the quad object with the specified label
def searchQuad(label):
    for quad in quad_list:
        if quad.get_label() == label:
            return quad # return quad object


def genQuad(operator, op1, op2, op3):
    # create a new quad with the next label number
    newQuad = Quad(label_number, operator, op1, op2, op3)
    quad_list.add(newQuad) # add newly created quad to the list

def nextQuad():
    label_number += 1
    return label_number

def newTemp():
    temp = 'T_' + temp_number
    temp_number += 1
    return temp

def backpatch(list, label):
    for lbl in list:
        quad_to_complete = searchQuad(label) # search the quad object with a certain label number
        quad_to_complete.set_op3(label) # complete the quad's last operand with the updated label

def makeList(label):
    new_list = [label]
    return new_list

def mergeList(list1,list2):
    list = list1.extend(list2)    
    return list

def emptyList():
    new_list = []
    return new_list
        
name = sys.argv[1] # get command line argument
token = Token(None, None, 1)
lex = Lex(name, 1, token)
parser = Parser(lex)
parser.syntax_analyzer() # run syntax analyzer
