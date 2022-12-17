from sly import Lexer


class CompLexer(Lexer):
    tokens = {"identifier", "num", "semi",
              "PROGRAM_IS", "VAR", "BEGIN", "END",
              "READ", "WRITE", "ASSIGN",
              "PLUS", "MINUS"}
    
    ignore = ' \t'
    ignore_comma = ','
    ignore_comment = r'\[.*\]'

    @_(r'\n+')
    def newline(self, t):
        self.lineno += t.value.count('\n')
    
    num = r'\d+'
    semi = r';'
    READ = r'READ '
    WRITE = r'WRITE '
    PROGRAM_IS = r'PROGRAM IS'
    VAR = r'VAR '
    BEGIN = r'BEGIN'
    END = r'END'
    ASSIGN = r':='
    PLUS = r'\+'
    MINUS = r'\-'
    
    identifier = r'[a-zA-Z_][a-zA-Z0-9_]*'
    
    
if __name__ == '__main__':
    data = open("program.txt").read()
    lexer = CompLexer()
    for tok in lexer.tokenize(data):
        print(tok)
        