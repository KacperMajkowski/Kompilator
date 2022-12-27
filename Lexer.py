from sly import Lexer


class CompLexer(Lexer):
    tokens = {"identifier", "num", "semi",
              "PROGRAM_IS", "VAR", "BEGIN", "END",
              "READ", "WRITE", "ASSIGN",
              "PLUS", "MINUS", "MUL", "DIV", "MOD",
              "EQ", "NEQ", "GEQ", "LEQ", "GT", "LT",
              "IF", "THEN", "ENDIF", "ELSE",
              "WHILE", "DO", "ENDWHILE",
              "REPEAT", "UNTIL",
              "PROCEDURE", "IS", "LB", "RB"}
    
    ignore = ' \t'
    ignore_comma = ','
    ignore_comment = r'\[(.|\n)*\]'

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
    ASSIGN = r':='
    PLUS = r'\+'
    MINUS = r'\-'
    MUL = r'\*'
    DIV = r'\/'
    MOD = r'\%'
    GEQ = r'>='
    LEQ = r'<='
    GT = r'>'
    LT = r'<'
    NEQ = r'!='
    EQ = r'\='
    ENDIF = r'ENDIF'
    IF = r'IF'
    THEN = r'THEN'
    ELSE = r'ELSE'
    ENDWHILE = r'ENDWHILE'
    END = r'END'
    WHILE = r'WHILE'
    DO = r'DO'
    REPEAT = r'REPEAT'
    UNTIL = r'UNTIL'
    PROCEDURE = r'PROCEDURE'
    IS = r'IS'
    LB = r'\('
    RB = r'\)'
    
    identifier = r'[a-zA-Z_][a-zA-Z0-9_]*'
    
    
if __name__ == '__main__':
    data = open("program.txt").read()
    lexer = CompLexer()
    for tok in lexer.tokenize(data):
        print(tok)
        