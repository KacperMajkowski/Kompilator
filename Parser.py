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

    @_("main")
    def program_all(self, p):
        pass
    
    @_("PROGRAM_IS VAR declarations BEGIN commands END")
    def main(self, p):
        pass

    @_("PROGRAM_IS BEGIN commands END")
    def main(self, p):
        pass
    
    @_("declarations identifier")
    def declarations(self, p):
        print("Declare variable", p[1])
        self.variables.append([self.currContext, p[1]])
        self.nextFreeIndex += 1
        
    @_("identifier")
    def declarations(self, p):
        print("Declare variable", p[0])
        self.variables.append([self.currContext, p[0]])
        self.nextFreeIndex += 1
        
    @_("commands command")
    def commands(self, p):
        pass

    @_("command")
    def commands(self, p):
        pass

    # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND # COMMAND
    @_("READ identifier semi")
    def command(self, p):
        print("Read input to variable", p[1], "on index", self.getVarCellIndex(p[1]))
        if self.getVarCellIndex(p[1]) is None:
            print("Błąd w lini", p.lineno, ": Nie znaleziono zmiennej", p[1])
        self.out += "GET " + str(self.getVarCellIndex(p[1])) + "\n"

    @_("WRITE value semi")
    def command(self, p):
        print("Put variable with index", p[1])
        self.out += "PUT " + str(p[1]) + "\n"

    @_("identifier ASSIGN expression semi")
    def command(self, p):
        print("Assign acc to", p[0])
        self.out += "STORE " + str(self.getVarCellIndex(p[0])) + "\n"
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
        pass

    @_("value MINUS value")  # Expresion ustawia akumulator na wynik, p - indeksy w pamięci
    def expression(self, p):
        self.out += "LOAD " + str(p[0]) + "\n"
        self.out += "SUB " + str(p[2]) + "\n"
        self.tempIndexes = 0
        pass

    @_("value MUL value")  # Expresion ustawia akumulator na wynik, p - indeksy w pamięci
    def expression(self, p):
        self.out += "SET 0\n"                       #Początkowy wynik
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes) + "\n"
        self.tempIndexes += 1
        self.out += "LOAD " + str(p[2]) + "\n"      #Mnożnik
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes) + "\n"
        self.tempIndexes += 1
        self.out += "SET 1\n"                       #Jedynka
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes) + "\n"
        self.tempIndexes += 1

        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 2) + "\n"         # Załaduj tY
        start = self.getK()                                                                 # Zapisz początek pętli
        self.out += "JZERO " + str(start + 8) + "\n"                                        # Czy Y == 0?
        self.out += "SUB " + str(self.nextFreeIndex + self.tempIndexes - 1) + "\n"          # Y = Y - 1
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 2) + "\n"        # Zapisz nowe Y
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 3) + "\n"         # Załaduj tX
        self.out += "ADD " + str(p[0]) + "\n"                                               # Dodaj oryginalne X
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes - 3) + "\n"        # Zapisz nowe tX
        self.out += "JUMP " + str(start) + "\n"                                             # Wróć na początek
        self.out += "LOAD " + str(self.nextFreeIndex + self.tempIndexes - 3) + "\n"         # Załaduj tX jako wynik
        
        self.tempIndexes = 0
        pass

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
        pass

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
        pass
    # EXPRESION #EXPRESION #EXPRESION #EXPRESION #EXPRESION #EXPRESION #EXPRESION #EXPRESION #EXPRESION
    
    def error(self, p):
        print("Error in line", p.lineno)
    
    # Zwraca indeks zmiennej w pamięci
    def getVarCellIndex(self, x):
        for cellIndex in range(len(self.variables)):
            if self.currContext == self.variables[cellIndex][0] and x == self.variables[cellIndex][1]:
                return cellIndex
        print(self.variables, self.currContext, x, "not found")
        
    # Zwraca indeks zmiennej w pamięci
    def getK(self):
        return self.out.count("\n") - 1
  
   
if __name__ == '__main__':
    lexer = CompLexer()
    parser = CompParser()

    text = open("program.txt").read()
    result = parser.parse(lexer.tokenize(text))
    code = parser.out
    code += "HALT\n"
    print(" ")
    print(code)
    print(parser.getK())
    #print(parser.variables)
    