import sys
from lex import *
from emit import *


#Next Step = Emitting Statements
class Parser:
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter
        
        self.symbols = set()
        self.labelIsDeclared = set()
        self.labelIsGotoed = set()

        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken()

    def checkToken(self, kind):
        return kind == self.curToken.kind 

    def checkPeek(self, kind):
        return kind == self.peekToken.kind 

    def match(self, kind):
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + " got " + self.curToken.kind.name)
        self.nextToken()

    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()

    def abort(self, message):
        sys.exit("Error. " + message)
        
    #Production rules
    #program ::= {statement}
    def program(self):
        print("PROGRAM")
        self.emitter.headerLine("#include <stdio.h>")
        self.emitter.headerLine("int main(void){")
        
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
        
        while not self.checkToken(TokenType.EOF):
            self.statement()
            
        self.emitter.emitLine("return 0;")
        self.emitter.emitLine("}")
            
        for label in self.labelIsGotoed:
            if label not in self.labelIsDeclared:
                self.abort("Attempting to GOTO to undeclared label: " + label)
    
    # One of the following statements
    def statement(self):
        #Check the first token to see what kind fo statement this is'
        
        #"PRINT" (expression | string)
        if self.checkToken(TokenType.PRINT):
            print("STATEMENT-PRINT")
            self.nextToken()

            if self.checkToken(TokenType.STRING):
                #Simple string
                self.nextToken()
            else:
                #Expect an expressions
                self.expression()
        elif self.checkToken(TokenType.IF):
            print("STATEMENT-IF")
            self.nextToken()
            self.comparison()
            
            self.match(TokenType.THEN)
            self.nl()
            
            while not self.checkToken(TokenType.ENDIF):
                self.statement()
                
            self.match(TokenType.ENDIF)
            
        elif self.checkToken(TokenType.WHILE):
            print("STATEMENT-WHILE")
            self.nextToken()
            self.comparison()
            
            self.match(TokenType.REPEAT)
            self.nl()
            
            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()
                
            self.match(TokenType.ENDWHILE)
                
        elif self.checkToken(TokenType.LABEL):
            print("STATEMENT-LABEL")
            self.nextToken()
            
            if self.curToken.text in self.labelIsDeclared:
                self.abort("Label already exists: " + self.curToken.text)
            self.labelIsDeclared.add(self.curToken.text)
            
            self.match(TokenType.IDENT)
            
        elif self.checkToken(TokenType.GOTO):
            print("STATEMENT-GOTO")
            self.nextToken()
            self.labelIsGotoed.add(self.curToken.text)
            self.match(TokenType.IDENT)
            
        #"Let" ident "=" expressions
        elif self.checkToken(TokenType.LET):
            print("STATEMENT-LET")
            self.nextToken()
            
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
            
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.expression()
            
        elif self.checkToken(TokenType.INPUT):
            print("STATEMENT-INPUT")
            self.nextToken()
            
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
            
            self.match(TokenType.IDENT)
            
        else:
            self.abort("Invalid statement at " + self.curToken.text + " (" + self.curToken.kind.name + ")")
                
        #newline
        self.nl()
        
    def comparison(self):
        print("COMPARISON")
        
        self.expression()
        
        if self.isComparisonOperator():
            self.nextToken()
            self.expression()
        else:
            self.abort("Expected comparison operator at: " + self.curToken.text)
            
        while self.isComparisonOperator():
            self.nextToken()
            self.expression()
            
    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ)
        
    def expression(self):
        print("EXPRESSION")
        self.term()
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.nextToken()
            self.term()
            
    def term(self):
        print("TERM")
        
        self.unary()
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            self.nextToken()
            self.unary()
            
    def unary(self):
        print("UNARY")
        
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.nextToken()
        self.primary()
        
    def primary(self):
        print("PRIMARY (" + self.curToken.text + ")")
        
        if self.checkToken(TokenType.NUMBER):
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            
            if self.curToken.text not in self.symbols:
                self.abort("Referencing variable before assignment: " + self.curToken.text)
            self.nextToken()
        else:
            self.abort("Unexpected token at " + self.curToken.text)
            
    # nl ::= '\n'+
    def nl(self):
        print("NEWLINE")
        
        self.match(TokenType.NEWLINE)
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
