from sly import Parser
from Lexer import CompLexer


class CompParser(Parser):
    
    tokens = CompLexer.tokens
    nextFreeIndex = 1
    tempIndexes = 0
    currContext = 0     #0 - main, następne dla kolejnych funkcji
    
    contexts = ["main"]
    variables = [[0, "acc"]]
    
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
        print("Assign", self.variables[0][0], "to", p[0])
        self.out += "STORE " + str(self.getVarCellIndex(p[0])) + "\n"
        
    @_("identifier")
    def value(self, p):
        return self.getVarCellIndex(p[0])

    @_("num")
    def value(self, p):
        self.out += "SET " + str(p[0]) + "\n"
        self.out += "STORE " + str(self.nextFreeIndex + self.tempIndexes) + "\n"
        self.tempIndexes += 1
        return self.nextFreeIndex + self.tempIndexes - 1
    
    @_("value")
    def expression(self, p):
        self.tempIndexes = 0

    @_("value PLUS value")
    def expression(self, p):
        self.out += "LOAD " + str(p[0]) + "\n"
        self.setAcc(str(p[0]))
        self.out += "ADD " + str(p[2]) + "\n"
        self.tempIndexes = 0
        pass

    def error(self, p):
        print("Error in line", p.lineno)
        
    #Ustaw akumulator
    def setAcc(self, x):
        self.variables[0][0] = x
    
    #Zwraca indeks zmiennej w pamięci
    def getVarCellIndex(self, x):
        for cellIndex in range(len(self.variables)):
            if self.currContext == self.variables[cellIndex][0] and x == self.variables[cellIndex][1]:
                return cellIndex
        print(self.variables, self.currContext, x, "not found")
  
   
if __name__ == '__main__':
    lexer = CompLexer()
    parser = CompParser()

    text = open("program.txt").read()
    result = parser.parse(lexer.tokenize(text))
    code = parser.out
    code += "HALT\n"
    print(" ")
    print(code)
    #print(parser.variables)
    