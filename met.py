## Team
# Athanasios Kalyviotis, 4607, cse84607
# Dimitrios Giannitsakis, 4338, cse84338

from abc import abstractmethod
from asyncio import new_event_loop
from asyncore import write
from contextlib import redirect_stderr
from msilib.schema import File
import sys
from unittest import result
from abc import ABC, abstractmethod


keyword = ['while','if','else']
addOperator = ['+','-']
mulOperator = ['*','/']
delimeter = [',','.',';']
groupSymbol= ['(',')','{','}','[',']']

# used in intermediate code generation - class Quad
label_number = 0 # a counter that keeps track of current quad label
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
        # print (next_token) # TODO: only for debugging purposes
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

        elif (type == 'MissingId'):
            print(f"id expected before symbol '{token.recognized_string}' in line {token.line_number}")
        exit(-1)   

    def ifStat(self):
        # print('ifStat')
        global token 
        if token.recognized_string == '(':
                token = self.get_token()
                condition = self.condition()

                if token.recognized_string == ')':
                    backpatch(condition.true, nextQuad())
                    token = self.get_token()
                    self.statements()

                    ifList = makeList(nextQuad())
                    genQuad('jump', '_', '_', '_')
                    backpatch(condition.false, nextQuad())

                    self.elsepart()
                    backpatch(ifList, nextQuad())
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
        condQuad = nextQuad()
        global token 
        if token.recognized_string == '(':
            token = self.get_token()
            condition = self.condition()

            if token.recognized_string == ')':
                backpatch(condition.true, nextQuad())
                token = self.get_token()
                self.statements()
                genQuad('jump','_','_',condQuad)        
                backpatch(condition.false, nextQuad())

            else:
                self.error('MissingCloseParen')
        else:
            self.error('MissingOpenParen')

    def switchcaseStat(self):
        # print('switchcaseStat')
        exitList = emptyList()

        global token 
        while(token.recognized_string == 'case'):
            token = self.get_token()
            if token.recognized_string == '(':
                token = self.get_token()
                condition = self.condition()
            
                if token.recognized_string == ')':
                        backpatch(condition.true, nextQuad())
                        token = self.get_token()
                        self.statements()

                        t = makeList(nextQuad())
                        genQuad('jump', '_', '_', '_')
                        exitList = mergeList(exitList, t)
                        backpatch(condition.false, nextQuad())
                else:
                    self.error('MissingCloseParen')

            else:
                self.error('MissingOpenParen')

        if(token.recognized_string == 'default'):
            token = self.get_token()
            self.statements()
            backpatch(exitList, nextQuad())
        else:
            self.error('MissingDefault')


    def forcaseStat(self):
        # print('forcaseStat')
        firstCondQuad = nextQuad()
        global token 
        while(token.recognized_string == 'case'):
            token = self.get_token()
            if token.recognized_string == '(':
                token = self.get_token()
                condition = self.condition()
           
                if token.recognized_string == ')':
                    backpatch(condition.true, nextQuad())
                    token = self.get_token()
                    self.statements()

                    genQuad('jump','_','_', firstCondQuad) # TODO: maybe wrong
                    backpatch(condition.false, nextQuad())
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
        flag = newTemp()
        firstCondQuad = nextQuad()
        genQuad(':=',0,'_',flag)

        global token 
        while(token.recognized_string == 'case'):
            token = self.get_token()
            if token.recognized_string == '(':
                token = self.get_token()
                condition = self.condition()
           
                if token.recognized_string == ')':
                    backpatch(condition.true,nextQuad())

                    token = self.get_token()
                    self.statements()

                    genQuad(':=',1,'_',flag)
                    backpatch(condition.false,nextQuad())
                else:
                     self.error('MissingCloseParen')
 
            else:
                self.error('MissingOpenParen')     

        # added default statement 
        if(token.recognized_string == 'default'):
            genQuad('=', flag, 1, firstCondQuad)
            token = self.get_token()
            self.statements()
        else:
            self.error('MissingDefault')

    def returnStat(self):
        # print('returnStat')
        global token 
        if token.recognized_string == '(':
            token = self.get_token()
            e_place = self.expression()
            if token.recognized_string != ')':
                self.error('MissingCloseParen')
            token = self.get_token()
            genQuad('ret', e_place, '_', '_')
        else:
            self.error('MissingOpenParen')


    def callStat(self):
        # print('callstat')
        global token 
        if token.family != 'id':
            self.error('MissingId')
        callee_id = token.recognized_string

        token = self.get_token()
        if token.recognized_string == '(':
            token = self.get_token()
            self.actualparlist(id=callee_id)
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
            e_place = self.expression()
            if token.recognized_string != ')':
                self.error('MissingCloseParen')
            token = self.get_token()
            genQuad("out", e_place, "_", "_")
        else:
            self.error('MissingOpenParen')


    def inputStat(self):
        # print('inputStat')
        global token 
        if token.recognized_string == '(':
            token = self.get_token()
            if token.family != 'id':
              self.error('MissingId')

            global id
            id = token.recognized_string

            token = self.get_token()
            if token.recognized_string != ')':
                self.error('MissingCloseParen') 
            token = self.get_token()

            genQuad("in", id, "_", "_")
            
        else: 
            self.error('MissingOpenParen') 

    def declarations(self):
        # print('declarations')
        global token 
        global table # the symbol table

        while (token.recognized_string == 'declare' or token.recognized_string == 'const'):
            if (token.recognized_string == 'declare') :
                token = self.get_token()
                self.varlist()
                if(token.recognized_string != ';'):
                    self.error('MissingQuestionMark')
                token = self.get_token()

            # added feature; check for constant initialization
            if (token.recognized_string == 'const') :
                token = self.get_token()
                if token.family != 'id':
                    self.error('MissingId')
                id = token.recognized_string
                token = self.get_token()
                if (token.family != 'assignment'):
                    self.error('MissingAssignment') 
                token = self.get_token()
                if (token.family != 'number'):
                    print(f"Expected number but instead got{token.recognized_string} in line {token.line_number}")
                    exit(-1)
                value = token.recognized_string
                token = self.get_token()
                if(token.recognized_string != ';'):
                    self.error('MissingQuestionMark')
                token = self.get_token()

                # add a new entity to the symbol table
                const_entity = Constant(id, value)
                table.addEntity(const_entity, isConst=1)
            
             
    
    def program_block(self, name):
        # print('block')
        global token 
        if token.recognized_string == '{':
            token = self.get_token()
            self.declarations()
            self.subprograms()

            genQuad("begin_block", name, "_", "_")
            # TODO: blockstatements or block?
            self.blockstatements()
            genQuad("halt", "_", "_", "_") # the only differance to block()
            genQuad("end_block", name, "_", "_")
            # print('back at block')
            if token.recognized_string != '}':
              self.error('MissingCloseCurlyBracket')
            token = self.get_token()

        else: 
            self.error('MissingOpenCurlyBracket')       

    def block(self, name):
        # print('block')
        global token 
        if token.recognized_string == '{':
            token = self.get_token()
            self.declarations()
            self.subprograms()

            genQuad("begin_block", name, "_", "_")
            startingQuad_label = nextQuad() # give me the next quad; it will be the startingQuad used in the symbol table
            # TODO: blockstatements or block?
            self.blockstatements()
            genQuad("end_block", name, "_", "_")

            startingQuad = searchQuad(startingQuad_label) # give me the next quad; it will be the startingQuad used in the symbol table
            framelength = table.getCurrentOffset()
            table.addPrintPhase(f"{table}\n\n") # save symbol table state before we update the fields and remove the level
            table.updateFields(framelength, startingQuad) # update last entity's fields
            table.removeLevel()

            # print('back at block')
            if token.recognized_string != '}':
              self.error('MissingCloseCurlyBracket')
            token = self.get_token()

        else: 
            self.error('MissingOpenCurlyBracket')       
    
    def formalparlist(self, entity):
        # print('formalparlist')
        global token 
        if token.recognized_string != ')': # if parenthesis don't close immediately
            self.formalparitem(entity)
            while(token.recognized_string == ','):
                token = self.get_token()
                self.formalparitem(entity)

    def formalparitem(self, entity):
        # print('formalparitem')
        global token 
        if (token.recognized_string == 'in'):
            token = self.get_token()
            if token.family != 'id':
                self.error('MissingInInoutdId')
            id = token.recognized_string
            formal_parameter_entity = FormalParameter(id, 'cv') # create the new formal parameter entity

            curr_offset = table.getCurrentOffset() # get the current offset from the active scope
            parameter_entity = Parameter(id, 'cv', curr_offset) # create the new parameter entity with the correct offset
            table.addEntity(parameter_entity, 0) # add the newly created entity to the table (isConst=0)
            table.addFormalParameter(entity, formal_parameter_entity)


            token = self.get_token()        

        elif (token.recognized_string == 'inout'):
            token = self.get_token()
            if token.family != 'id':
                self.error('MissingInInoutdId')
            id = token.recognized_string
            formal_parameter_entity = FormalParameter(id, 'ref') # create the new formal parameter entity
            
            curr_offset = table.getCurrentOffset() # get the current offset from the active scope
            parameter_entity = Parameter(id, 'ref', curr_offset) # create the new parameter entity with the correct offset
            table.addEntity(parameter_entity, 0) # add the newly created entity to the table (isConst=0)
            table.addFormalParameter(entity, formal_parameter_entity)
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
            id = token.recognized_string
            token = self.get_token()
            self.assignStat(id)

        
                
    def assignStat(self, id):
        # print('assignStat')
        global token 
        if (token.family == 'assignment'):
            token = self.get_token()
            e_place = self.expression()
            genQuad(":=", e_place, "_", id)
        else:
            self.error('MissingAssignment') 

    def condition(self):
        # print('condition')
        global token
        boolterm1 = self.boolterm()
        # self.boolterm()
        condition = Bool_List()
        condition.true = boolterm1.true
        condition.false = boolterm1.false
        while token.recognized_string == 'or':
            backpatch(condition.false, nextQuad())
            token = self.get_token()
            boolterm2 = self.boolterm()
            condition.true = mergeList(condition.true, boolterm2.true)
            condition.false = boolterm2.false
        return condition

    def boolterm (self):
        # print('boolterm ')
        global token 
        boolfactor1 = self.boolfactor()
        boolterm = Bool_List()
        boolterm.true = boolfactor1.true
        boolterm.false = boolfactor1.false
        while token.recognized_string == 'and':
            backpatch(boolterm.true,nextQuad())
            token = self.get_token()
            boolfactor2 = self.boolfactor()
            boolterm.false = mergeList(boolterm.false, boolfactor2.false)       
            boolterm.true = boolfactor2.true

        return boolterm    
            
    def boolfactor(self):
        # print('boolfactor')
        global token
        boolfactor = Bool_List()
        if token.recognized_string == 'not':
            token = self.get_token()
            if token.recognized_string == '[':
                token = self.get_token()
                condition = self.condition()
                if (token.recognized_string != ']'):
                    self.error('MissingCloseBracket')
                boolfactor.true = condition.false
                boolfactor.false = condition.true         
                token = self.get_token()
            else:
                self.error('MissingOpenBracket')           
    
        elif token.recognized_string == '[':
                token = self.get_token()
                condition = self.condition()
                if (token.recognized_string != ']'):
                    self.error('MissingCloseBracket')
                boolfactor.true = condition.true
                boolfactor.false = condition.false       
                token = self.get_token()

        else:
            e1_place = self.expression()
            
            if (token.family == 'relOperator'):
                relOperator = token.recognized_string
                token = self.get_token()
            else:
                self.error('MissingRelOperator')
            e2_place = self.expression()
            boolfactor.true = makeList(nextQuad())
            genQuad(relOperator, e1_place, e2_place, '_')
            boolfactor.false = makeList(nextQuad())
            genQuad('jump','_','_','_')

        return boolfactor #TODO: was indented (inside else)
                 
        
    def expression(self):
        # print('expression')
        global token 
        self.optionalSign()
        t1_place = self.term()
        while(token.family == 'addOperator'):
            operator = token.recognized_string
            token = self.get_token()
            t2_place = self.term()      
            w = newTemp()
            genQuad(operator, t1_place, t2_place, w)
            t1_place = w
        e_place = t1_place
        return e_place
            
    def term(self):
        # print('term')
        global token 
        f1_place = self.factor()
        while(token.family == 'mulOperator'):
            token = self.get_token()
            f2_place = self.factor()
            w = newTemp()
            genQuad("*", f1_place, f2_place, w)
            f1_place = w
        t_place = f1_place
        return t_place


    def factor(self):
        # print('factor')
        global token
        if token.recognized_string == '(':
            token = self.get_token()
            e_place = self.expression()
            if token.recognized_string != ')':
                self.error('MissingCloseParen')
            token = self.get_token()
            f_place = e_place

        elif token.family == 'id':
            id = token.recognized_string
            token = self.get_token()
            id_place = self.idtail(id) # call idtail and pass the ID with it

            f_place = id_place 

        elif token.family == 'number': 
            f_place = token.recognized_string
            token = self.get_token()

        else:
            self.error('MissingFactor')   

        return f_place
  
        
    def program(self):
        # print('program')
        global token
        if token.recognized_string == 'program':
            token = self.get_token()
            if token.family == 'id':
                name = token.recognized_string # keep block name to generate quad later

                token = self.get_token()
                self.program_block(name)
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

            
    def actualparlist(self, id, needRet=0):
        # print('actualparlist')
        global token
        if (token.recognized_string != ')'): # if parenthesis don't close immediately
            self.actualparitem()
            while(token.recognized_string == ','):
                token = self.get_token()
                self.actualparitem()

            # done with function/procedure params, gen quads for call and maybe return value
            t = ''
            if (needRet):
                t = newTemp()
                genQuad('par', t, 'ret', '_') # extra quad; we need the return value (unlike callStat)
            genQuad('call', id, '_', '_')

            return t;

    def actualparitem(self):
        # print('actualparitem')
        global token
        if token.recognized_string == 'in':
            token = self.get_token()
            e_place = self.expression()
            genQuad("par", e_place, "cv", "_")

        elif token.recognized_string == 'inout':
            token = self.get_token()
            id = token.recognized_string
            genQuad("par", id, "ref", "_")

            if token.family != 'id':
              self.error('MissingInInoutId')
            token = self.get_token()

        else:
          self.error('MissingInInout')

                   
    def subprogram(self):
        # print('subprogram')
        global token 
        global table

        if (token.recognized_string == 'function'):
            token = self.get_token()
            name = token.recognized_string

            if token.family == 'id':
                id = token.recognized_string
                function_entity = Function(id) # create the new function entity 
                table.addEntity(function_entity, 0) # add the newly created entity to the table (isConst=0)
                table.addPrintPhase(f"{table}\n\n") # save symbol table state before we add a new level
                table.addLevel() # add a new level to the table

                token = self.get_token()
                if token.recognized_string == '(':
                    token = self.get_token()
                    self.formalparlist(function_entity) # ..also input function_entity; will need for formalparams completion
                    if token.recognized_string != ')':
                        self.error('MissingCloseParen')
                    token = self.get_token()
                    self.block(name)

                else:
                    self.error('MissingOpenParen')
            else:
                self.error('MissingId')
            

        elif (token.recognized_string == 'procedure'):
            token = self.get_token()
            name = token.recognized_string

            if token.family == 'id':
                id = token.recognized_string
                procedure_entity = Procedure(id) # create the new procedure entity 
                table.addEntity(procedure_entity, 0) # add the newly created entity to the table (isConst=0)
                table.addLevel() # add a new level to the table

                token = self.get_token()
                if token.recognized_string == '(':
                    token = self.get_token()
                    self.formalparlist(procedure_entity)
                    if token.recognized_string != ')':
                        self.error('MissingCloseParen')
                    token = self.get_token()
                    self.block(name)

                else:
                    self.error('MissingOpenParen')
            else:
                self.error('MissingId')
            
        else:
            self.error('MissingFunctionProcedure') 


    def subprograms(self):
        # print('subprograms')
        global token 
        while(token.recognized_string == 'function' or token.recognized_string == 'procedure'):
            self.subprogram()
           

    def idtail(self, id):
        # print('idtail')
        global token
        id_place = id # often the idtail is just called by a variable, so just return its name
        if token.recognized_string == '(':
            token = self.get_token()
            id_place = self.actualparlist(id, needRet=1) # executes only if it is a function or procedure
            if token.recognized_string != ')':
                self.error('MissingCloseParen')
            token = self.get_token()
        
        return id_place # return to factor rule
            
    def optionalSign(self):
        # print('optionalSign')
        global token
        if token.family == 'addOperator':
          token = self.get_token()

            
    def varlist(self):
        # print('varlist')
        global token 
        global table

        if (token.recognized_string != ';'): # check for ';' if empty (see declarations grammar)

            if token.family == 'id':
                id = token.recognized_string
                curr_offset = table.getCurrentOffset() # get the current offset from the active scope
                variable_entity = Variable(id, curr_offset) # create the new variable entity with the correct offset
                table.addEntity(variable_entity, 0) # add the newly created entity to the table (isConst=0)

                token = self.get_token()
                while(token.recognized_string == ','):
                    token = self.get_token()
                    if (token.family != 'id'):
                        self.error('MissingId')  
                    id = token.recognized_string
                    token = self.get_token()

                    curr_offset = table.getCurrentOffset() # get the current offset from the active scope
                    variable_entity = Variable(id, curr_offset) # create the new variable entity with the correct offset
                    table.addEntity(variable_entity, 0) # add the newly created entity to the table (isConst=0)
                    
            else:
                self.error('MissingId')  

# intermediate code classes
class Quad :
    def __init__(self, label, operator, op1, op2, target):
        self.label = label # so that we can identify different quads
        self.operator = operator
        self.op1 = op1
        self.op2 = op2
        self.target = target

    def __str__(self):
        return f"{self.label}, {self.operator}, {self.op1}, {self.op2}, {self.target}"
    
    def set_target(self, target):
        self.target = target 

    def get_label(self):
        return self.label


class Bool_List:
    def __init__(self):
        # two lists 
        self.true = []
        self.false = []

# helper routines

quad_list = [] # global list that keeps all quad objects

# returns the quad object with the specified label
def searchQuad(label):
    for quad in quad_list:
        if quad.get_label() == label:
            return quad # return quad object
    # should never get here!
    print("Fatal error")
    exit(-1)


def genQuad(operator, op1, op2, target):
    # create a new quad with the next label number
    global label_number
    label_number += 1;
    newQuad = Quad(label_number, operator, op1, op2, target)
    quad_list.append(newQuad) # add newly created quad to the list

def nextQuad():
    global label_number
    temp = label_number + 1
    return temp

def newTemp():
    global temp_number
    temp = 'T_' + str(temp_number)
    temp_number += 1

    # make an entry in the symbol table for the newly created temp
    curr_offset = table.getCurrentOffset()
    temp_entity = TemporaryVariable(temp, curr_offset)
    table.addEntity(temp_entity, 0)

    return temp

def backpatch(list, target):
    for label in list:
        quad_to_complete = searchQuad(label) # search the quad object with a certain label number
        quad_to_complete.set_target(target) # complete the quad's last operand with the updated target


def makeList(label):
    new_list = [label]
    return new_list

def mergeList(list1,list2):
    list = list1 + list2    
    return list


def emptyList():
    new_list = []
    return new_list

# print the quad list
def print_quads(quad_list):
    for quad in quad_list:
        print(quad)

# write all quads to a .int file
def export_quads(quad_list):
    intermediate_file = open('test.int', 'w')
    for quad in quad_list:
        intermediate_file.write(str(quad)+'\n')
    intermediate_file.close()

def create_c_code(quad_list):
    L = ['int main()\n','{\n','']
    parameters = []
    operands = set()
    for quad in quad_list:
        temp = f"\tL_{quad.label}: "

        if(quad.operator == "+"):
            temp += f"{quad.target} = {quad.op1} + {quad.op2};"
            operand = f"{quad.op1}"
            if (not operand.isnumeric()): operands.add(operand)
            operand = f"{quad.op2}"
            if (not operand.isnumeric()): operands.add(operand)
            operand = f"{quad.target}"
            if (not operand.isnumeric()): operands.add(operand)
            
            
        elif(quad.operator == '-'):
            temp += f"{quad.target} = {quad.op1} - {quad.op2};"            
            operand = f"{quad.op1}"
            if (not operand.isnumeric()): operands.add(operand)
            operand = f"{quad.op2}"
            if (not operand.isnumeric()): operands.add(operand)
            operand = f"{quad.target}"
            if (not operand.isnumeric()): operands.add(operand)
            

        elif(quad.operator == '*'):
            temp += f"{quad.target} = {quad.op1} * {quad.op2};"
            operand = f"{quad.op1}"
            if (not operand.isnumeric()): operands.add(operand)
            operand = f"{quad.op2}"
            if (not operand.isnumeric()): operands.add(operand)
            operand = f"{quad.target}"
            if (not operand.isnumeric()): operands.add(operand)
            

        elif(quad.operator == '/'):
            temp += f"{quad.target} = {quad.op1} / {quad.op2};"    
            operand = f"{quad.op1}"
            if (not operand.isnumeric()): operands.add(operand)
            operand = f"{quad.op2}"
            if (not operand.isnumeric()): operands.add(operand)
            operand = f"{quad.target}"
            if (not operand.isnumeric()): operands.add(operand)
            

        elif(quad.operator == ':='):
            temp += f"{quad.target} = {quad.op1};" 
            operand = f"{quad.op1}"
            if (not operand.isnumeric()): operands.add(operand)
            operand = f"{quad.target}"
            if (not operand.isnumeric()): operands.add(operand)
            

        elif(quad.operator == '='):
            temp += f"if ({quad.op1} = {quad.op2}) goto L_{quad.target};"
            operand = f"{quad.op1}"
            if (not operand.isnumeric()): operands.add(operand)
            operand = f"{quad.op2}"
            if (not operand.isnumeric()): operands.add(operand)
            

        elif(quad.operator == '>'):
            temp += f"if ({quad.op1} > {quad.op2}) goto L_{quad.target};"
            

        elif(quad.operator == '<'):
            temp += f"if ({quad.op1} < {quad.op2}) goto L_{quad.target};"
            

        elif(quad.operator == '<>'):
            temp += f"if ({quad.op1} != {quad.op2}) goto L_{quad.target};"
            

        elif(quad.operator == '>='):
            temp += f"if ({quad.op1} >= {quad.op2}) goto L_{quad.target};"
           

        elif(quad.operator == '<='):
            temp += f"if ({quad.op1} <= {quad.op2}) goto L_{quad.target};"
            

        elif(quad.operator == 'par'):
            parameters.append(str(quad.op1))
            operand = f"{quad.op1}"
            if (not operand.isnumeric()): operands.add(operand)
            

        elif(quad.operator == 'jump'):
            temp += f"goto L_{quad.target};"

        elif(quad.operator == 'in'):
            temp += f"scanf({quad.op1});"
            operand = f"{quad.op1}"
            if (not operand.isnumeric()): operands.add(operand)
            

        elif(quad.operator == 'out'):
            temp += f"printf({quad.op1});"
            operand = f"{quad.op1}"
            if (not operand.isnumeric()): operands.add(operand)
            

        elif(quad.operator == 'ret'):
            temp += f"return({quad.op1});"

        elif(quad.operator == 'halt'):
            temp += "{}"          

        elif(quad.operator == 'call'):
            temp += f"{quad.op1}("
            if (parameters):
                for par in parameters[:-1]: # read backwards
                    temp += (f"{par}, ")
                temp += f"{parameters[-1]});"
                parameters = []
            else:
                temp += ");"
      
        L.append(temp)
    
    declare = "\tint " 
    operands_list = list(operands)
    for op in operands_list[:-1]:
        declare += f"{op}, "
    declare += f"{operands_list[-1]};"
    L[2] += declare
    L.pop()
       
    file = open('test.c','w')
    for x in L:
        file.write(str(x)+'\n')
    file.close()    
    
# symbol table classes
class Table:
    def __init__(self):
        self.scope_list = [] # initialize a list of scopes
        self.addLevel()
        self.printPhases = []
    
    # add a new entity to the current scope
    def addEntity(self, new_entity, isConst):
        if (self.scope_list):
            self.scope_list[-1].addEntity(new_entity, isConst) # add a new entity on the uppermost scope 
    
    # add a new level(scope) to the table
    def addLevel(self):
        new_scope = Scope()
        self.scope_list.append(new_scope)

        global level_counter
        level_counter += 1 # created a new level, increment the counter

    # remove a level(scope) from the table
    def removeLevel(self):
        self.scope_list.pop(-1) # pop the last element of the scope_list

        global level_counter
        level_counter -= 1 # removed a new level, decrement the counter

    # update framelength and startingQuad fields in function or procedure entity
    def updateFields(self, framelength, startingQuad):
        self.scope_list[-2].updateFields(framelength, startingQuad)

    # add a new formal parameter to the function or procedure entity specified
    def addFormalParameter(self, entity, formal_parameter):
        entity.addFormalParameter(formal_parameter)

    # search for an entity based on name
    def searchEntity(self, name):
        for scope in self.scope_list[::-1]: # search in each level starting from the uppermost level to the lower ones
            scope.searchEntity(name)

        # if execution reaches this point it means entity was not found; throw an exception
        print(f"Entity with name {name} was not found.")
        exit(-1)
    
    # get the current relative offset of the uppermost scope
    def getCurrentOffset(self):
        if (self.scope_list):
            return self.scope_list[-1].getRelOffset()

    def __str__(self):
        temp = ''
        for scope in self.scope_list:
            temp += str(scope) # print scope
            temp += '\n'
        return temp
    
    # helper method
    def addPrintPhase(self, phase_string):
        self.printPhases.append(phase_string)

level_counter = 0 # keeps track of the current scope level

class Scope:
    def __init__(self):
        self.level = level_counter
        self.entity_list = [] # initialize a list of entities
        self.rel_offset = 12 # current relative offset of the scope
    
    def addEntity(self, new_entity, isConst):
        self.entity_list.append(new_entity) # add a new entity in the current scope

        # make sure constants don't occupy space in stack 
        if (isConst == 0):
            new_entity.offset = self.rel_offset
            self.rel_offset += 4 # if a new entity is added, the offset is incremented by 4 bytes

    def updateFields(self, framelength, startingQuad):
        self.entity_list[-1].updateFields(framelength, startingQuad) # TODO: maybe not the last entity?

    def addFormalParameter(self, entity, formal_parameter):
        entity.addFormalParameter(formal_parameter) 

    def searchEntity(self, name):
        for e in self.entity_list:
            if (e.name == name):
                return e

    def __str__(self):
        temp = ''
        for entity in self.entity_list[:-1:]:
            temp += '['
            temp += str(entity)
            temp += ']<-- '
        temp += '['
        temp += str(self.entity_list[-1]) # print also the last entity
        temp += ']'

        return f"({self.level})<-- {temp}" 

    def getRelOffset(self):
        return self.rel_offset

class Entity():
    def __init__(self, name):
        self.name = name    
    
    def updateFields(self, framelength, startingQuad):
        self.framelength = framelength
        self.startingQuad = startingQuad


    # when entity is a function or procedure
    def addFormalParameter(self, formal_parameter):
        self.formalParameters.append(formal_parameter) # add the new formal parameter to the list of parameters

    def __str__(self):
        return f"{self.name}"

class Variable(Entity):
    def __init__(self, name, offset):
       super().__init__(name)
       self.offset = offset

    def __str__(self):
        return f"{self.name}/{self.offset}"

class TemporaryVariable(Variable):
    def __init__(self, name, offset):
        super().__init__(name, offset)

class Constant(Entity):
    def __init__(self, name, value):
        super().__init__(name)
        self.value = value 

    def __str__(self):
        temp = super().__str__()
        temp += f"={self.value}"
        return temp

class Procedure(Entity):
    def __init__(self, name):
        super().__init__(name)
        self.startingQuad = None # not known initially
        self.framelength = 0 # not known initially
        self.formalParameters = [] # a list with all formal parameters
    
    def addFormalParameter(self, formal_parameter):
        self.formalParameters.append(formal_parameter) # add the new formal parameter to the list of parameters

    def __str__(self):
        temp = f"{self.name}/({self.startingQuad})/{self.framelength}"
        for param in self.formalParameters:
            temp += f"  <{str(param)}>"

        return temp
         
class Function(Procedure):
    def __init__(self, name):
        super().__init__(name)


class FormalParameter(Entity) :
    def __init__(self, name, mode):
        super().__init__(name)
        self.mode = mode

    def __str__(self):
        temp = super().__str__()
        temp += f"/{self.mode}"
        return temp

class Parameter(FormalParameter) :
    def __init__(self, name, mode, offset):
        super().__init__(name, mode)
        self.offset= offset

    def __str__(self):
        temp = f"{self.name}/{self.offset}/{self.mode}"
        return temp

                
# show all the symbol table phases in a readable format and export them to a .symb file
def export_symbols():
    symbol_file = open('test.symb', 'w')
    for state in table.printPhases:
        symbol_file.write(state)

        
# name = sys.argv[1] # get command line argument
name = sys.argv[1]
token = Token(None, None, 1)
lex = Lex(name, 1, token)
parser = Parser(lex)
table = Table()

parser.syntax_analyzer() # run syntax analyzer


# print_quads(quad_list) # TODO: delete useless
export_quads(quad_list)
create_c_code(quad_list)
export_symbols()
