from sly import Parser
from Lexer import CompLexer
import re


class CompParser(Parser):
    
    tokens = CompLexer.tokens
    nextFreeIndex = 1
    tempIndexes = 0
    currContext = 0
    nextFreeContext = 0
    addedContext = False
    
    variables = [[0, "acc", "og"]]
    procedureDeclarations = []
    proceduresTable = []

    out = ""
    program = ""
    k_correction = 0

    @_("procedures main")
    def program_all(self, p):
        pass
    
    @_("procedures PROCEDURE proc_head IS VAR declarations BEGIN commands END")
    def procedures(self, p):
        self.variables = self.fixContexts(self.variables)
        self.k_correction = 0
        self.proceduresTable.append([p[2], p[7]])
        self.nextFreeContext += 2
        self.currContext += 2

    @_("procedures PROCEDURE proc_head IS BEGIN commands END")
    def procedures(self, p):
        self.variables = self.fixContexts(self.variables)
        self.k_correction = 0
        self.proceduresTable.append([p[2], p[5]])
        self.nextFreeContext += 2
        self.currContext += 2
        
    @_("")
    def procedures(self, p):
        self.k_correction = 0
    
    @_("identifier LB arguments RB")
    def proc_head(self, p):
        if self.getProcedureDeclaration(p[0]) is not None:
            p[0] = self.addToIndexesInIf(p[0], self.countLines(p[2]))
            p[2] = self.replacePointers(p[2], p[0])
            self.out += str(p[2])
        else:
            self.procedureDeclarations.append(p[0])
        return p[0]
    
    @_("arguments identifier")
    def arguments(self, p):
        self.variables.append([self.nextFreeContext, p[1], "ref"])
        self.nextFreeIndex += 1
        ret = ""
        print(self.variables)
        print(p[1])
        print(self.currContext)
        print(self.getVarCellIndex(p[1], self.currContext))
        if self.variables[self.getVarCellIndex(p[1], self.currContext)][2] == "og":
            ret += "SET " + str(self.getVarCellIndex(p[1], self.currContext)) + "\n"
        else:
            ret += "LOAD " + str(self.getVarCellIndex(p[1], self.currContext)) + "\n"
        ret += "STORE " + "?" + "\n"
        return p[0] + ret

    @_("identifier")
    def arguments(self, p):
        self.variables.append([self.nextFreeContext, p[0], "ref"])
        self.nextFreeIndex += 1
        ret = ""
        print(self.variables)
        print(p[0])
        print(self.currContext)
        print(self.getVarCellIndex(p[0], self.currContext))
        if self.variables[self.getVarCellIndex(p[0], self.currContext)][2] == "og":
            ret += "SET " + str(self.getVarCellIndex(p[0], self.currContext)) + "\n"
        else:
            ret += "LOAD " + str(self.getVarCellIndex(p[0], self.currContext)) + "\n"
        ret += "STORE " + "?" + "\n"
        return ret
        
    @_("PROGRAM_IS VAR declarations BEGIN commands END")
    def main(self, p):
        print(p[4])
        p[4] = self.replaceVariables(p[4])
        self.program = p[4]
        pass

    @_("PROGRAM_IS BEGIN commands END")
    def main(self, p):
        p[2] = self.replaceVariables(p[2])
        self.program = p[2]
        pass
    
    @_("declarations identifier")
    def declarations(self, p):
        self.variables.append([self.nextFreeContext, p[1], "og"])
        self.nextFreeIndex += 1
        
    @_("identifier")
    def declarations(self, p):
        self.nextFreeIndex = len(self.variables)
        self.variables.append([self.nextFreeContext, p[0], "og"])
        self.nextFreeIndex += 1
        self.variables[0][0] = self.nextFreeContext
        
    @_("commands command")  # Zwraca kod commands
    def commands(self, p):
        return p[0] + p[1]

    @_("command")           # Zwraca kod commands
    def commands(self, p):
        return p[0]

    # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND
    @_("proc_head semi")
    def command(self, p):
        self.out += "Procedure " + str(p[0]) #+ " "
        self.k_correction += self.getCurrK()
        tempK = self.getCurrK()
        self.out += self.addToIndexesInIf(self.proceduresTable[int(self.getProcedure(p[0])/2)][1], self.k_correction)
        self.out += "EndProcedure " + str(p[0]) #+ " "
        command = self.out
        self.k_correction += self.getCurrK() - tempK
        self.out = ""
        return command
    
    @_("READ identifier semi") # Zwraca swój kod
    def command(self, p):
        if self.getVarCellIndex(p[1], self.currContext) is None:
            print("Błąd w lini", p.lineno, ": Nie znaleziono zmiennej", p[1])
        self.out += "GET " + str(p[1]) + ">" + "\n"
        command = self.out
        self.k_correction += self.getCurrK()
        self.out = ""
        return command

    @_("WRITE value semi") # Zwraca swój kod
    def command(self, p):
        self.out += "PUT " + str(p[1]) + "\n"
        command = self.out
        self.k_correction += self.getCurrK()
        self.out = ""
        return command

    @_("identifier ASSIGN expression semi")  # Zwraca swój kod
    def command(self, p):
        self.out += "STORE " + str(p[0]) + ">" + "\n"
        command = self.out
        self.k_correction += self.getCurrK()
        self.out = ""
        return command
    
    @_("IF condition THEN commands ENDIF")
    def command(self, p):
        # Dodajemy 1 do indeksów p[3] bo dodajemy przed nim 1 nową liniję
        p[3] = self.addToIndexesInIf(p[3], 1)
        self.out = p[1] + "JPOS " + str(self.k_correction + 1) + "\n" + p[3]
        command = self.out
        self.k_correction += 1
        self.out = ""
        return command

    @_("IF condition THEN commands ELSE commands ENDIF")
    def command(self, p):
        # Dodajemy 1 do indeksów p[3] bo dodajemy przed nim 1 nową liniję
        p[3] = self.addToIndexesInIf(p[3], 1)
        # Dodajemy 2 do indeksów p[5] bo dodajemy przed nim 2 nowe liniji
        p[5] = self.addToIndexesInIf(p[5], 2)
                                                    # +2 za JPOS i JUMP
        self.out = p[1] + "JPOS " + str(self.k_correction - self.countLines(p[5]) + 2) + "\n" + p[3] +\
                            "JUMP " + str(self.k_correction + 2) + "\n" + p[5]  # +2 za JPOS i JUMP
        command = self.out
        self.k_correction += 2
        self.out = ""
        return command

    @_("WHILE condition DO commands ENDWHILE")
    def command(self, p):
        
        # Nie dodajemy indeksów do p[1] bo nie ma przed nim żadnych nowych komend
        # Dodajemy 1 do indeksów p[3] bo dodajemy przed nim 1 nowa linia
        p[3] = self.addToIndexesInIf(p[3], 1)
        
        self.out = p[1] + "JPOS " + str(self.k_correction + 2) + "\n" + p[3] \
                   + "JUMP " + str(self.k_correction - self.countLines(p[1]) - self.countLines(p[3])) + "\n"
        command = self.out
        self.k_correction += 2
        self.out = ""
        return command

    @_("REPEAT commands UNTIL condition semi")
    def command(self, p):
        # Nie dodajemy indeksów do p[1] ani p[3] bo nie ma przed nimi żadnych nowych komend
        self.out = p[1] + p[3] + "JPOS " + str(self.k_correction - self.countLines(p[3]) - self.countLines(p[1])) + "\n"
        command = self.out
        self.k_correction += 1
        self.out = ""
        return command
    # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND

    # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE
    @_("identifier")        #Value zwraca indeks w pamięci
    def value(self, p):
        return str(p[0]) + ">"
        #return self.getVarCellIndex(p[0], self.currContext)

    @_("num")
    def value(self, p):     #Value zwraca indeks w pamięci
        self.out += "SET " + str(p[0]) + "\n"
        index = self.nextFreeIndex + self.tempIndexes + 1000
        self.out += "STORE " + str(index) + "\n"
        self.tempIndexes += 1
        return index
    # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE
    
    # EXPRESSION  # EXPRESSION # EXPRESSION # EXPRESSION # EXPRESSION # EXPRESSION # EXPRESSION
    @_("value")             #Expresion ustawia akumulator na wynik, p - indeksy w pamięci
    def expression(self, p):
        self.out += "LOAD " + str(p[0]) + "\n"
        self.nextFreeIndex += self.tempIndexes
        self.tempIndexes = 0
        return p[0]

    @_("value PLUS value")  #Expresion ustawia akumulator na wynik, p - indeksy w pamięci
    def expression(self, p):
        self.out += "LOAD " + str(p[0]) + "\n"
        self.out += "ADD " + str(p[2]) + "\n"
        self.nextFreeIndex += self.tempIndexes
        self.tempIndexes = 0

    @_("value MINUS value")  # Expresion ustawia akumulator na wynik, p - indeksy w pamięci
    def expression(self, p):
        self.out += "LOAD " + str(p[0]) + "\n"
        self.out += "SUB " + str(p[2]) + "\n"
        self.nextFreeIndex += self.tempIndexes
        self.tempIndexes = 0

    @_("value MUL value")  # Expresion ustawia akumulator na wynik, p - indeksy w pamięci
    def expression(self, p):
        #Czy X lub Y jest zerem?
        self.out += "LOAD " + str(p[0]) + "\n"
        self.out += "JZERO " + str(self.getK() + 35) + "\n"
        self.out += "LOAD " + str(p[2]) + "\n"
        self.out += "JZERO " + str(self.getK() + 33) + "\n"
        
        # ty = Y
        # adr tY = nfi
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes + 1000) + "\n"
        self.tempIndexes += 1
        # Wynik = 0
        # adr Wynik = nfi + 1
        self.out += "SET 0" + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes + 1000) + "\n"
        self.tempIndexes += 1
        
        # Counter = 1
        # adr Counter = nfi + 2
        Ceq1 = self.getK() + 1
        self.out += "SET 1" + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes + 1000) + "\n"
        self.tempIndexes += 1
        # tX = X
        # adr Counter = nfi + 3
        self.out += "LOAD " + str(p[0]) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes + 1000) + "\n"
        self.tempIndexes += 1
        
        # Counter > tY?
        CgtTY = self.getK() + 1
        self.out += "SET 1" + "\n"
        self.out += "ADD " + str(self.nextFreeIndex + self.tempIndexes - 4 + 1000) + "\n"
        self.out += "SUB " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        self.out += "JZERO " + str(self.getK() + 9) + "\n"
        
        # Nie
        # Counter = Counter + Counter
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        self.out += "ADD " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        # tX = tX + tX
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 1 + 1000) + "\n"
        self.out += "ADD " + str(self.nextFreeIndex + self.tempIndexes - 1 + 1000) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 1 + 1000) + "\n"
        
        # Back to Counter > tY
        self.out += "JUMP " + str(CgtTY) + "\n"

        # Tak
        # HALF Counter
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        self.out += "HALF\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        # HALF tX
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 1 + 1000) + "\n"
        self.out += "HALF\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 1 + 1000) + "\n"
        # W = W + tX
        self.out += "ADD " + str(self.nextFreeIndex + self.tempIndexes - 3 + 1000) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 3 + 1000) + "\n"
        # tY = tY - Counter
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 4 + 1000) + "\n"
        self.out += "SUB " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 4 + 1000) + "\n"
        
        # tY = 0?
        self.out += "JPOS " + str(Ceq1) + "\n"
        
        # Wynik
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 3 + 1000) + "\n"

        self.nextFreeIndex += self.tempIndexes
        self.tempIndexes = 0
        
    @_("value DIV value")  # Expresion ustawia akumulator na wynik, p - indeksy w pamięci
    def expression(self, p):
        
        # tX = X; adr nfi + ti - 4
        self.out += "LOAD " + str(p[0]) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes + 1000) + "\n"
        self.tempIndexes += 1
        # tY = Y; adr nfi + ti - 3
        self.out += "LOAD " + str(p[2]) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes + 1000) + "\n"
        self.tempIndexes += 1
        # C = 1; adr nfi + ti - 2
        self.out += "SET 1\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes + 1000) + "\n"
        self.tempIndexes += 1
        # W = 0; adr nfi + ti - 1
        self.out += "SET 0\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes + 1000) + "\n"
        self.tempIndexes += 1

        # Y = 0?
        self.out += "LOAD " + str(p[2]) + "\n"
        self.out += "JZERO " + str(self.getK() + 34) + "\n"
        
        # tX < Y?
        tXY = self.getK() + 1
        self.out += "SET 1\n"
        self.out += "ADD " + str(self.nextFreeIndex + self.tempIndexes - 4 + 1000) + "\n"
        self.out += "SUB " + str(p[2]) + "\n"
        self.out += "JZERO " + str(self.getK() + 30) + "\n"
        
        
        # tY > tX?
        tYtX = self.getK() + 1
        self.out += "SET 1\n"
        self.out += "ADD " + str(self.nextFreeIndex + self.tempIndexes - 4 + 1000) + "\n"
        self.out += "SUB " + str(self.nextFreeIndex + self.tempIndexes - 3 + 1000) + "\n"
        self.out += "JZERO " + str(self.getK() + 9) + "\n"
        
        # tY = tY + tY
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 3 + 1000) + "\n"
        self.out += "ADD " + str(self.nextFreeIndex + self.tempIndexes - 3 + 1000) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 3 + 1000) + "\n"

        # C = C + C
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        self.out += "ADD " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        
        # JUMP to tX < tY
        self.out += "JUMP " + str(tYtX) + "\n"
        
        # HALF tY
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 3 + 1000) + "\n"
        self.out += "HALF\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 3 + 1000) + "\n"
        # HALF C
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        self.out += "HALF\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        # tX = tX - tY
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 4 + 1000) + "\n"
        self.out += "SUB " + str(self.nextFreeIndex + self.tempIndexes - 3 + 1000) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 4 + 1000) + "\n"
        # tY = Y
        self.out += "LOAD " + str(p[2]) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 3 + 1000) + "\n"
        # W = W + C
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 1 + 1000) + "\n"
        self.out += "ADD " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 1 + 1000) + "\n"
        # C = 1
        self.out += "SET 1\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        
        # JUMP to tX < Y
        self.out += "JUMP " + str(tXY) + "\n"
        
        # OUT W
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 1 + 1000) + "\n"

        self.nextFreeIndex += self.tempIndexes
        self.tempIndexes = 0

    @_("value MOD value")  # Expresion ustawia akumulator na wynik, p - indeksy w pamięci
    def expression(self, p):
    
        # tX = X; adr nfi + ti - 3
        self.out += "LOAD " + str(p[0]) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes + 1000) + "\n"
        self.tempIndexes += 1
        # tY = Y; adr nfi + ti - 2
        self.out += "LOAD " + str(p[2]) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes + 1000) + "\n"
        self.tempIndexes += 1
        # C = 1; adr nfi + ti - 1
        self.out += "SET 1\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes + 1000) + "\n"
        self.tempIndexes += 1
    
        # Y = 0?
        self.out += "LOAD " + str(p[2]) + "\n"
        self.out += "JZERO " + str(self.getK() + 31) + "\n"
    
        # tX < Y?
        tXY = self.getK() + 1
        self.out += "SET 1\n"
        self.out += "ADD " + str(self.nextFreeIndex + self.tempIndexes - 3 + 1000) + "\n"
        self.out += "SUB " + str(p[2]) + "\n"
        self.out += "JZERO " + str(self.getK() + 27) + "\n"
    
        # tY > tX?
        tYtX = self.getK() + 1
        self.out += "SET 1\n"
        self.out += "ADD " + str(self.nextFreeIndex + self.tempIndexes - 3 + 1000) + "\n"
        self.out += "SUB " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        self.out += "JZERO " + str(self.getK() + 9) + "\n"
    
        # tY = tY + tY
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        self.out += "ADD " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
    
        # C = C + C
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 1 + 1000) + "\n"
        self.out += "ADD " + str(self.nextFreeIndex + self.tempIndexes - 1 + 1000) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 1 + 1000) + "\n"
    
        # JUMP to tX < tY
        self.out += "JUMP " + str(tYtX) + "\n"
    
        # HALF tY
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        self.out += "HALF\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        # HALF C
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 1 + 1000) + "\n"
        self.out += "HALF\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 1 + 1000) + "\n"
        # tX = tX - tY
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 3 + 1000) + "\n"
        self.out += "SUB " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 3 + 1000) + "\n"
        # tY = Y
        self.out += "LOAD " + str(p[2]) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 2 + 1000) + "\n"
        # C = 1
        self.out += "SET 1\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 1 + 1000) + "\n"
    
        # JUMP to tX < Y
        self.out += "JUMP " + str(tXY) + "\n"
    
        # OUT tX
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 3 + 1000) + "\n"

        self.nextFreeIndex += self.tempIndexes
        self.tempIndexes = 0

    # EXPRESSION # EXPRESSION # EXPRESSION # EXPRESSION # EXPRESSION # EXPRESSION # EXPRESSION # EXPRESSION
    
    # CONDITION # CONDITION # CONDITION # CONDITION # CONDITION # CONDITION # CONDITION # CONDITION # CONDITION
    @_("value EQ value") # Condition ustawia acc na 0 jeśli prawda, inne jeśli fałsz, zwraca kod
    def condition(self, p):
        self.out += "LOAD " + str(p[0]) + "\n"
        self.out += "SUB " + str(p[2]) + "\n"
        self.out += "JPOS " + str(self.getK() + 4) + "\n"
        self.out += "LOAD " + str(p[2]) + "\n"
        self.out += "SUB " + str(p[0]) + "\n"

        command = self.out
        self.k_correction += self.getCurrK()
        self.out = ""
        return command

    @_("value NEQ value")  # Condition ustawia acc na 0 jeśli prawda, inne jeśli fałsz, zwraca kod
    def condition(self, p):
        self.out += "LOAD " + str(p[0]) + "\n"
        self.out += "SUB " + str(p[2]) + "\n"
        self.out += "JPOS " + str(self.getK() + 7) + "\n"
        self.out += "LOAD " + str(p[2]) + "\n"
        self.out += "SUB " + str(p[0]) + "\n"
        self.out += "JPOS " + str(self.getK() + 4) + "\n"
        self.out += "SET 1 " + "\n"
        self.out += "JUMP " + str(self.getK() + 3) + "\n"
        self.out += "SET 0 " + "\n"
    
        command = self.out
        self.k_correction += self.getCurrK()
        self.out = ""
        return command

    @_("value GEQ value")  # Condition ustawia acc na 0 jeśli prawda, inne jeśli fałsz, zwraca kod
    def condition(self, p):
        self.out += "LOAD " + str(p[2]) + "\n"
        self.out += "SUB " + str(p[0]) + "\n"
    
        command = self.out
        self.k_correction += self.getCurrK()
        self.out = ""
        return command

    @_("value LEQ value")  # Condition ustawia acc na 0 jeśli prawda, inne jeśli fałsz, zwraca kod
    def condition(self, p):
        self.out += "LOAD " + str(p[0]) + "\n"
        self.out += "SUB " + str(p[2]) + "\n"
    
        command = self.out
        self.k_correction += self.getCurrK()
        self.out = ""
        return command

    @_("value GT value")  # Condition ustawia acc na 0 jeśli prawda, inne jeśli fałsz, zwraca kod
    def condition(self, p):
        self.out += "SET 1" + "\n"
        self.out += "ADD " + str(p[2]) + "\n"
        self.out += "SUB " + str(p[0]) + "\n"
    
        command = self.out
        self.k_correction += self.getCurrK()
        self.out = ""
        return command

    @_("value LT value")  # Condition ustawia acc na 0 jeśli prawda, inne jeśli fałsz, zwraca kod
    def condition(self, p):
        self.out += "SET 1" + "\n"
        self.out += "ADD " + str(p[0]) + "\n"
        self.out += "SUB " + str(p[2]) + "\n"
    
        command = self.out
        self.k_correction += self.getCurrK()
        self.out = ""
        return command
    
    
    # CONDITION # CONDITION # CONDITION # CONDITION # CONDITION # CONDITION # CONDITION # CONDITION # CONDITION
    
    def error(self, p):
        print("Error in line", p.lineno)
    
    # Zwraca indeks zmiennej w pamięci
    def getVarCellIndex(self, x, context):
        for cellIndex in range(len(self.variables)):
            if context == self.variables[cellIndex][0] and x == self.variables[cellIndex][1]:
                return cellIndex
        # print(self.variables, context, x, "not found")
        
    def getProcedure(self, funcName):
        if funcName[-1] == " ":
            funcName = funcName[:-1]
        for procedureIndex in range(len(self.proceduresTable)):
            if self.proceduresTable[procedureIndex][0] == funcName:
                return procedureIndex*2
        #print("Procedure '" + funcName + "' not found in", self.proceduresTable)
        return None
    
    def getProcedureDeclaration(self, funcName):
        for procedureIndex in range(len(self.procedureDeclarations)):
            if self.procedureDeclarations[procedureIndex] == funcName:
                return procedureIndex
        #print("Procedure", funcName, "not found in", self.proceduresTable)
        return None

    def replacePointers(self, commands, funcName):
        curr = 0
        commands = commands.split()
        ret = ""
        contexts = list(map(lambda x: x[0], self.variables))
        firstIndex = contexts[1:].index(self.getProcedure(funcName)) + 1
        print("ProcedureName = ", funcName, "GetProcedure ", self.getProcedure(funcName), "index: ", firstIndex, "contexts: ", contexts)
        for commandIndex in range(len(commands)):
            if commands[commandIndex] == "?":
                commands[commandIndex] = str(firstIndex + curr)
                curr += 1
                
            if commands[commandIndex].isdigit() or commands[commandIndex] == "HALF":
                if commands[commandIndex] != "HALF":
                    ret += " "
                ret += commands[commandIndex] + "\n"
            else:
                ret += commands[commandIndex]
        return ret
                
    def replaceVariables(self, commandsStr):
        contextStack = [self.variables[0][0]]
        
        commands = re.split(r"\n| ", commandsStr)
        ret = ""
        for commandIndex in range(len(commands)):
            if len(str(commands[commandIndex])) > 1:
                if commands[commandIndex][-1] == ">":
                    print(self.variables)
                    print(commands[commandIndex])
                    print(contextStack)
                    if len(contextStack) > 1 and\
                            self.variables[self.getVarCellIndex(commands[commandIndex][:-1], contextStack[-1])][2] == "ref":
                        if commands[commandIndex - 1] != "PUT":
                            ret += "I"
                            commands[commandIndex] = self.getVarCellIndex(commands[commandIndex][:-1], contextStack[-1])
                        else:
                            ret = ret[:-3]
                            ret += "LOAD " + str(self.getVarCellIndex(commands[commandIndex][:-1], contextStack[-1])) + "\n"
                            commands[commandIndex] = str(commands[commandIndex - 1]) + " 0\n"
                            
                            commandsStr = self.addToIndexesInIf(commandsStr[commandIndex+1:], 1)
                            commands = commands[:commandIndex] + re.split(r"\n| ", commandsStr)
                    else:
                        commands[commandIndex] = self.getVarCellIndex(commands[commandIndex][:-1], contextStack[-1])
                
            if commands[commandIndex] == "Procedure":
                contextStack.append(self.getProcedure(commands[commandIndex + 1]))
                commands[commandIndex] = ""
                commands[commandIndex + 1] = ""
            elif commands[commandIndex] == "EndProcedure":
                contextStack.pop()
                commands[commandIndex] = ""
                commands[commandIndex + 1] = ""
            
            if str(commands[commandIndex]).isdigit() or commands[commandIndex] == "HALF":
                if commands[commandIndex] != "HALF":
                    ret += " "
                ret += str(commands[commandIndex]) + "\n"
            else:
                ret += str(commands[commandIndex])
        
        return ret

    # Zwraca linię w obecnej command
    def getCurrK(self):
        return self.out.count("\n")
        
    # Zwraca linię całego programu
    def getK(self):
        
        #       Długość programu           Długość command      Długość poprzednich command w commands
        return self.program.count("\n") + self.out.count("\n") + self.k_correction - 1
    
    def countLines(self, text):
        return text.count("\n")
    
    def addToIndexesInIf(self, commands, shift):
        commands = commands.split()
        ret = ""
        for commandIndex in range(len(commands)):
            if commands[commandIndex] == "JUMP" or commands[commandIndex] == "JZERO" or commands[commandIndex] == "JPOS":
                commands[commandIndex + 1] = str(int(commands[commandIndex + 1]) + shift)
            
            if commands[commandIndex].isdigit() or commands[commandIndex] == "HALF" or commands[commandIndex][-1] == ">":
                ret += commands[commandIndex] + "\n"
            else:
                ret += commands[commandIndex] + " "
        return ret
    
    def sub1fromVariablesDeclaredInProcedure(self, context):
        for varIndex in range(len(self.variables)):
            if self.variables[varIndex][0] == context:
                self.variables[varIndex][0] -= 1
                
        return self.variables
    
    def fixContexts(self, variables):
        for var in variables:
            if var[0] % 2 == 1:
                var[0] -= 1
        return variables
    
    def halfContexts(self, variables):
        
        done = False
        for var in variables:
            if var[0] % 2 == 1:
                done = True
        
        if not done:
            for var in variables:
                var[0] = int(var[0]/2)
        return variables
        
  
   
if __name__ == '__main__':
    lexer = CompLexer()
    parser = CompParser()

    text = open("program.txt").read()
    result = parser.parse(lexer.tokenize(text))
    parser.program += parser.out
    code = parser.program
    code += "HALT\n"
    print(" ")
    print(code)
    open("output.txt", 'w').write(code)
    # print(parser.variables)
    # print(parser.proceduresTable)
    