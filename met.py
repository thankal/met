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
        # TODO: __del__ maybe add more to it?

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
            elif char == '': # EOF TODO: fix/not needed
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
                            print('hit exception')
                            self.error('IllegalNameException')
                        source_file.seek(save_cursor) # revert cursor
                        family = 'number'
                    
                    break

                # id
                if ((char >= 'A' and char <= 'Z') or (char >= 'a' and char <= 'z')) :
                    while ((char >= '0' and char <= '9') or (char >= 'A' and char <= 'Z') or (char >= 'a' and char <= 'z')): # TODO: improvements?
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
        tokenn = self.lexical_analyzer.next_token()
        print(tokenn)
        return tokenn # get the next token

    def error(self, type):
        if (type == 'MissingCloseParen'):
            print("Every program which contains '(' should end with ')' ")

        elif (type == 'MissingOpenParen'):
            print(f"Open paren '(' expected in line {token.line_number} but instead got {token.recognized_string}")
                
        elif(type == 'MissingProgramId'):
            print("The name of the program expected after the keyword program in line 1.The illegal name appeared.  ")

        elif (type == 'MissingCloseBracket'):
            print("Every program which contains '[' should end with ']' ")

        elif (type == 'MissingOpenBracket'):
            print(f"Open bracket '[' expected in line {token.line_number} but instead got {token.recognized_string}")    

        elif (type == 'MissingCloseCurlyBracket'):
            print("Every program which contains '{' should end with '}' ")

        elif (type == 'MissingOpenCurlyBracket'):
            print("Open curly bracket '{' expected in line %d " % (token.line_number))

        elif (type == 'MissingFullStop'):
            print("Every program should end with a fullstop,fullstop at the end is missing")

        elif (type == 'MissingRelOperator'):
            print("RelOperator Expected")

        elif (type == 'MissingProgramm'):
            print("keyword program expected in line 1.All programs should start with the keyword program ")

        elif (type == 'MissingInInout'):
            print("keyword in or inout expected in line 1.All programs should start with the keyword in or inout")

        elif (type == 'MissingInInoutdId'):
            print("Expected id after in/inout keyword")

        elif (type == 'MissingQuestionMark'):
            print("Questionmark expected") 

        elif (type == 'MissingAssignment'):
            print("Expected  ':='  for assigmnent of variable") 

        elif (type == 'MissingFunctionProcedure'):
            print("Keyword function or procedure expected.All subprograms should start with the keyword function or procedure")
        
        elif (type == 'MissingNoWord'):
            print("No characters are allowed after the fullstop indicating the end of the program")
        
        elif (type == 'MissingFactor'):
            print(f"Expected factor in line {token.line_number} but instead got {token.recognized_string}")
        exit(-1)   

    def ifStat(self):
        print('ifStat')
        global token 
        token = self.get_token()
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

    def elseStat(self):
        print('elseStat')
        global token 
        if token.recognized_string == 'else':
            token = self.get_token()
            self.statements()

    def whileStat(self):
        print('whileStat')
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
        print('switchcaseStat')
        global token 
        while(token.recognized_string == 'case'):
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
        print('forcaseStat')
        global token 
        while(token.recognized_string == 'case'):
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


    def incaseStat(self):
        print('incaseStat')
        global token 
        while(token.recognized_string == 'case'):
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
        print('returnStat')
        global token 
        if token.recognized_string == '(':
            token = self.get_token()
            self.exrpession()
            if token.recognized_string != ')':
                self.error('MissingCloseParen')
            token = self.get_token()
        else:
            self.error('MissingOpenParen')


    def printStat(self):
        print('printStat')
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
        print('inputStat')
        global token 
        if token.recognized_string == '(':
            token = self.get_token()
            if token.family != 'id':
              self.error('MissingId')
            token = self.get_token()
            if token.recognized_string != ')':
                self.error('MissingCloseParen') #TODO: change to MissingCloseParen
            token = self.get_token()
            
        else: 
            self.error('MissingOpenParen') #TODO: MissingOpenParen

    def declarations(self):
        print('declarations')
        global token 
        while (token.recognized_string == 'declare') :
            token = self.get_token()
            self.varlist()
            if(token.recognized_string != ';'):
                self.error('MissingQuestionMark')
            token = self.get_token()
            
             
    
    def block(self):
        print('block')
        global token 
        if token.recognized_string == '{':
            token = self.get_token()
            self.declarations()
            self.subprograms()
            self.blockstatements()
            print('back at block')
            if token.recognized_string != '}':
              self.error('MissingCloseCurlyBracket')
            token = self.get_token()

        else: 
            self.error('MissingOpenCurlyBracket')       
    
    def formalparlist(self):
        print('formalparlist')
        global token 
        if token.recognized_string != ')': # if parenthesis don't close immediately
            self.formalparitem()
            while(token.recognized_string == ','):
                token = self.get_token()
                self.formalparitem()

    def formalparitem(self):
        print('formalparitem')
        global token 
        if (token.recognized_string == 'in' or token.recognized_string == 'inout'):
            token = self.get_token()
            if self.token.family != 'id':
                self.error('MissingInInoutdId')
            token = self.get_token()        
        else:
            self.error('MissingInInout')        			    


    def statements(self):
        print('statements')
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
        print('blockstatements')
        global token 
        self.statement()
        print('back at blockstatements')
        while(token.recognized_string == ';'):
            print('found ;')

            token = self.get_token()
            self.statement()   

    def statement(self):
        print('statement')
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
             self.forCaseStat()

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
        print('assignStat')
        global token 
        if (token.family == 'assignment'):
            token = self.get_token()
            self.expression()
        else:
            self.error('MissingAssignment') 

    def condition(self):
        print('condition')
        global token
        self.boolterm()
        while token.recognized_string == 'or':
            token = self.get_token()
            self.boolterm()

    def boolterm (self):
        print('boolterm ')
        global token 
        self.boolfactor()
        while token.recognized_string == 'and':
            token = self.get_token()
            self.boolfactor()       
    
    def boolfactor(self):
        print('boolfactor')
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
        print('expression')
        global token 
        self.optionalSign()
        self.term()
        while(token.family == 'addOperator'):
            token = self.get_token()
            self.term()      
            
    def term(self):
        print('term')
        global token 
        self.factor()
        while(token.family == 'mulOperator'):
            token = self.get_token()
            self.factor()
        
    def program(self):
        print('program')
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
        print('factor')
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
        print('actualparlist')
        global token
        if (token.recognized_string != ')'): # if parenthesis don't close immediately
            self.actualparitem()
            while(token.recognized_string == ','):
                token = self.get_token()
                self.actualparitem()

                   
    def subprogram(self):
        print('subprogram')
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
        print('subprograms')
        global token 
        while(token.recognized_string == 'function' or token.recognized_string =='procedure'):
            token = self.get_token()
            self.subprogram()
           

    def actualparitem(self):
        print('actualparitem')
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
        print('idtail')
        global token
        if token.recognized_string == '(':
            token = self.get_token()
            self.actualparlist()
            if token.recognized_string != ')':
                self.error('MissingCloseParen')
            token = self.get_token()
            
    def optionalSign(self):
        print('optionalSign')
        global token
        if token.family == 'addOperator':
          token = self.get_token()

            
    def varlist(self):
        print('varlist')
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


## testing
# name = sys.argv[1]
# token = Token(None, None, None)
# lex = Lex(name, 1, token)


# for i in range(100):
#     print(lex.next_token())

name = sys.argv[1]
token = Token(None, None, 1)
lex = Lex(name, 1, token)
parser = Parser(lex)
parser.syntax_analyzer()
