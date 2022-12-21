from sly import Parser
from Lexer import CompLexer


class CompParser(Parser):
    
    tokens = CompLexer.tokens
    nextFreeIndex = 1
    tempIndexes = 0
    currContext = 0     #0 - main, następne dla kolejnych funkcji
    
    contexts = ["main"]
    variables = [[0, "acc"]]
    
    k = 0
    out = ""
    program = ""
    k_correction = 0

    @_("main")
    def program_all(self, p):
        pass
    
    @_("PROGRAM_IS VAR declarations BEGIN commands END")
    def main(self, p):
        self.program = p[4]
        pass

    @_("PROGRAM_IS BEGIN commands END")
    def main(self, p):
        self.program = p[2]
        pass
    
    @_("declarations identifier")
    def declarations(self, p):
        self.variables.append([self.currContext, p[1]])
        self.nextFreeIndex += 1
        
    @_("identifier")
    def declarations(self, p):
        self.variables.append([self.currContext, p[0]])
        self.nextFreeIndex += 1
        
    @_("commands command")  # Zwraca kod commands
    def commands(self, p):
        return p[0] + p[1]

    @_("command")           # Zwraca kod commands
    def commands(self, p):
        return p[0]

    # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND
    @_("READ identifier semi") # Zwraca swój kod
    def command(self, p):
        if self.getVarCellIndex(p[1]) is None:
            print("Błąd w lini", p.lineno, ": Nie znaleziono zmiennej", p[1])
        self.out += "GET " + str(self.getVarCellIndex(p[1])) + "\n"
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

    @_("identifier ASSIGN expression semi") # Zwraca swój kod
    def command(self, p):
        self.out += "STORE " + str(self.getVarCellIndex(p[0])) + "\n"
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
                            "JUMP " + str(self.k_correction + 2) + "\n" + p[5] # +2 za JPOS i JUMP
        command = self.out
        self.k_correction += 2
        self.out = ""
        return command

    @_("WHILE condition DO commands ENDWHILE")
    def command(self, p):
        
        # Nie dodajemy indeksów do p[1] bo nie ma przed nim żadnych nowych komend
        # Dodajemy 1 do indeksów p[3] bo dodajemy przed nim 2 nowe liniji
        p[3] = self.addToIndexesInIf(p[3], 1)
        
        self.out = p[1] + "JPOS " + str(self.k_correction + 2) + "\n" + p[3] \
                   + "JUMP " + str(self.k_correction - self.countLines(p[1]) - self.countLines(p[3])) + "\n"
        command = self.out
        self.k_correction += 1
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
        return self.getVarCellIndex(p[0])

    @_("num")
    def value(self, p):     #Value zwraca indeks w pamięci
        self.out += "SET " + str(p[0]) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes) + "\n"
        self.tempIndexes += 1
        return self.nextFreeIndex + self.tempIndexes - 1
    # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE # VALUE
    
    # EXPRESSION  # EXPRESSION # EXPRESSION # EXPRESSION # EXPRESSION # EXPRESSION # EXPRESSION
    @_("value")             #Expresion ustawia akumulator na wynik, p - indeksy w pamięci
    def expression(self, p):
        self.out += "LOAD " + str(p[0]) + "\n"
        self.tempIndexes = 0
        return p[0]

    @_("value PLUS value")  #Expresion ustawia akumulator na wynik, p - indeksy w pamięci
    def expression(self, p):
        self.out += "LOAD " + str(p[0]) + "\n"
        self.out += "ADD " + str(p[2]) + "\n"
        self.tempIndexes = 0

    @_("value MINUS value")  # Expresion ustawia akumulator na wynik, p - indeksy w pamięci
    def expression(self, p):
        self.out += "LOAD " + str(p[0]) + "\n"
        self.out += "SUB " + str(p[2]) + "\n"
        self.tempIndexes = 0

    @_("value MUL value")  # Expresion ustawia akumulator na wynik, p - indeksy w pamięci
    def expression(self, p):
        #Czy X lub Y jest zerem?
        self.out += "LOAD " + str(p[0]) + "\n"
        self.out += "JZERO " + str(self.getK() + 36) + "\n"
        self.out += "LOAD " + str(p[2]) + "\n"
        self.out += "JZERO " + str(self.getK() + 34) + "\n"
        
        # ty = Y
        # adr tY = nfi
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes) + "\n"
        self.tempIndexes += 1
        # Wynik = 0
        # adr Wynik = nfi + 1
        self.out += "SET 0" + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes) + "\n"
        self.tempIndexes += 1
        
        # Counter = 1
        # adr Counter = nfi + 2
        Ceq1 = self.getK() + 1
        self.out += "SET 1" + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes) + "\n"
        self.tempIndexes += 1
        # tX = X
        # adr Counter = nfi + 3
        self.out += "LOAD " + str(p[0]) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes) + "\n"
        self.tempIndexes += 1
        
        # Counter > tY?
        CgtTY = self.getK() + 1
        self.out += "SET 1" + "\n"
        self.out += "ADD " + str(self.nextFreeIndex + self.tempIndexes - 4) + "\n"
        self.out += "SUB " + str(self.nextFreeIndex + self.tempIndexes - 2) + "\n"
        self.out += "JZERO " + str(self.getK() + 9) + "\n"
        
        # Nie
        # Counter = Counter + Counter
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 2) + "\n"
        self.out += "ADD " + str(self.nextFreeIndex + self.tempIndexes - 2) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 2) + "\n"
        # tX = tX + tX
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 1) + "\n"
        self.out += "ADD " + str(self.nextFreeIndex + self.tempIndexes - 1) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 1) + "\n"
        
        # Back to Counter > tY
        self.out += "JUMP " + str(CgtTY) + "\n"

        # Tak
        # HALF Counter
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 2) + "\n"
        self.out += "HALF\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 2) + "\n"
        # HALF tX
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 1) + "\n"
        self.out += "HALF\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 1) + "\n"
        # W = W + tX
        self.out += "ADD " + str(self.nextFreeIndex + self.tempIndexes - 3) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 3) + "\n"
        # tY = tY - Counter
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 4) + "\n"
        self.out += "SUB " + str(self.nextFreeIndex + self.tempIndexes - 2) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 4) + "\n"
        
        # tY = 0?
        self.out += "JPOS " + str(Ceq1) + "\n"
        
        # Wynik
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 3) + "\n"
        
        self.tempIndexes = 0
        
    @_("value DIV value")  # Expresion ustawia akumulator na wynik, p - indeksy w pamięci
    def expression(self, p):
        self.out += "LOAD " + str(p[0]) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes) + "\n"
        self.tempIndexes += 1
        self.out += "SET 0" + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes) + "\n"
        self.tempIndexes += 1
        
        # Czy Y == 0?
        self.out += "LOAD " + str(p[2]) + "\n"
        self.out += "JZERO " + str(self.getK() + 16) + "\n"
        
        # Dodaj 1 żeby dzielić całkowicie, potem odejmiemy 1 od wyniku
        self.out += "SET 1\n"
        self.out += "ADD " + str(self.nextFreeIndex + self.tempIndexes - 2) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 2) + "\n"
        
        # Odejmujemy aż nie otrzymamy zera
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 2) + "\n"
        start = self.getK()
        self.out += "JZERO " + str(start + 8) + "\n"
        self.out += "SUB " + str(p[2]) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 2) + "\n"
        self.out += "SET 1\n"
        self.out += "ADD " + str(self.nextFreeIndex + self.tempIndexes - 1) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 1) + "\n"
        self.out += "JUMP " + str(start) + "\n"
        
        #Odejmujemy 1
        self.out += "SET 1\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes) + "\n"
        self.tempIndexes += 1
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 2) + "\n"
        self.out += "SUB " + str(self.nextFreeIndex + self.tempIndexes - 1) + "\n"
        
        self.tempIndexes = 0

    @_("value MOD value")  # Expresion ustawia akumulator na wynik, p - indeksy w pamięci
    def expression(self, p):
        self.out += "LOAD " + str(p[0]) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes) + "\n"
        self.tempIndexes += 1
    
        # Czy Y == 0?
        self.out += "LOAD " + str(p[2]) + "\n"
        self.out += "JZERO " + str(self.getK() + 12) + "\n"
    
        # Odejmujemy aż nie otrzymamy zera
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 1) + "\n"
        start = self.getK()
        self.out += "JZERO " + str(start + 9) + "\n"    # Czy początkowe X == 0?
        self.out += "SUB " + str(p[2]) + "\n"
        self.out += "JZERO " + str(self.getK() + 4) + "\n"  # Czy po odjęciu X-Y == 0?
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 1) + "\n"
        self.out += "JUMP " + str(start + 1) + "\n"

        # Czy dzieli dokładnie?
        self.out += "LOAD " + str(p[2]) + "\n"
        self.out += "SUB " + str(self.nextFreeIndex + self.tempIndexes - 1) + "\n"
        self.out += "JZERO " + str(self.getK() + 3) + "\n"

        # Ładujemy ostatnie tX jako wynik
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 1) + "\n"
    
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
    def getVarCellIndex(self, x):
        for cellIndex in range(len(self.variables)):
            if self.currContext == self.variables[cellIndex][0] and x == self.variables[cellIndex][1]:
                return cellIndex
        print(self.variables, self.currContext, x, "not found")

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
            
            if commandIndex % 2 == 1:
                ret += " " + commands[commandIndex] + "\n"
            else:
                ret += commands[commandIndex]
        return ret
    
  
   
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
    #print(parser.variables)
    