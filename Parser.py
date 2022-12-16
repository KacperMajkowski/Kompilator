from sly import Parser
from Lexer import CompLexer


class CompParser(Parser):
    
    tokens = CompLexer.tokens
    nextFreeIndex = 1
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
    
    @_("declarations identifier")
    def declarations(self, p):
        print("Declare variable", p[1])
        self.variables.append([self.currContext, p[1]])
        
    @_("identifier")
    def declarations(self, p):
        print("Declare variable", p[0])
        self.variables.append([self.currContext, p[0]])
        
    @_("commands command")
    def commands(self, p):
        pass

    @_("command")
    def commands(self, p):
        pass
        
    @_("READ identifier")
    def command(self, p):
        print("Read variable", p[1], "to cell", self.nextFreeIndex)
        self.nextFreeIndex += 1

    @_("WRITE value")
    def command(self, p):
        print("Put variable with index", p[1])
        self.out += "PUT " + str(p[1]) + "\n"
        
    @_("identifier")
    def value(self, p):
        return getVarCellIndex(self.variables, self.currContext, p[0])

    @_("num")
    def value(self, p):
        self.out += "SET " + str(p[0]) + "\n"
        return 0

    def error(self, t):
        print("Illegal character '%s'" % t)


def getFuncContext(f, functions):
    return functions.index(f)


def getVarCellIndex(variables, currContext, x):
    for cellIndex in range(len(variables)):
        if currContext == variables[cellIndex][0] and x == variables[cellIndex][1]:
            return cellIndex
    print(variables, currContext, x, "not found")
  
  
if __name__ == '__main__':
    lexer = CompLexer()
    parser = CompParser()

    text = open("program.txt").read()
    result = parser.parse(lexer.tokenize(text))
    print(" ")
    print(parser.out)
    #print(parser.variables)
    