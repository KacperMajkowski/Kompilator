from sly import Lexer


class CompLexer(Lexer):
    tokens = {"identifier", "num", "READ", "WRITE", "PROGRAM_IS", "VAR", "BEGIN", "END"}
    
    ignore = ' \t'
    ignore_semicolon = ';'
    ignore_comma = ','
    ignore_comment = r'\[.*\]'
    ignore_newline = r'\n+'
    
    num = r'\d+'
    READ = r'READ'
    WRITE = r'WRITE'
    PROGRAM_IS = r'PROGRAM IS'
    VAR = r'VAR'
    BEGIN = r'BEGIN'
    END = r'END'
    
    identifier = r'[a-zA-Z_][a-zA-Z0-9_]*'
    
    
if __name__ == '__main__':
    data = open("program.txt").read()
    lexer = CompLexer()
    for tok in lexer.tokenize(data):
        print(tok)
        print('type=%r, value=%r' % (tok.type, tok.value))
        